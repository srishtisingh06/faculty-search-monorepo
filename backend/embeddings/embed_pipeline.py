"""
Embedding Pipeline
──────────────────
Generates sentence-transformer embeddings for faculty profiles
and prepares them for FAISS ingestion.

Design decisions:
  - Embed: research_interests, research_areas, biography, projects, publications
  - Skip:  faculty_name, email, phone  (non-semantic PII)
  - Chunk: 512-token window, 64-token overlap for long texts
  - Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim, fast, accurate)
  - Output: numpy array + JSON metadata sidecar
"""
import json
import logging
from pathlib import Path
from typing import Optional
import threading
import numpy as np
import psycopg2.extras

from configs.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DB_CONFIG,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    PROCESSED_DIR,
)
from database.db_writer import get_connection

logger = logging.getLogger(__name__)

# Lazy-load the model on first use
_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model once: %s", EMBEDDING_MODEL)
            _model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")

        return _model


# ── Text preparation ──────────────────────────────────────────────────────────
def build_embed_text(row: dict) -> str:
    """
    Concatenate embeddable fields into one document string.
    Never include name/email/phone.
    """
    parts = []

    for ri in row.get("research_interests") or []:
        parts.append(ri)
    for ra in row.get("research_areas") or []:
        parts.append(ra)

    designation = row.get("designation") or ""
    if designation.strip():
        parts.append(designation.strip())

    bio = row.get("biography") or ""
    if bio.strip():
        parts.append(bio.strip())

    for proj in row.get("projects") or []:
        parts.append(proj)

    for pub in row.get("publications") or []:
        parts.append(pub)

    return " | ".join(p.strip() for p in parts if p.strip())

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Simple word-level chunking.
    For academic text, word-level chunks are more stable than character-level.
    """
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
        if start >= len(words):
            break
    return chunks


# ── Embedding generation ──────────────────────────────────────────────────────
def embed_text(text: str) -> np.ndarray:
    """Embed a single text string. Returns (dim,) float32 array."""
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return vec.astype(np.float32)


def embed_faculty_row(row: dict) -> Optional[np.ndarray]:
    """
    Embed one faculty record.
    If the document is long, chunk it and return the mean-pooled embedding.
    """
    text = build_embed_text(row)
    if not text.strip():
        return None

    chunks = chunk_text(text)
    if not chunks:
        return None

    model = _get_model()
    vecs = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
    # Mean pool across chunks → single vector per faculty
    return np.mean(vecs, axis=0).astype(np.float32)


# ── Batch pipeline ────────────────────────────────────────────────────────────
def fetch_faculty_for_embedding(limit: int = 10_000) -> list[dict]:
    """
    Pull faculty rows from PostgreSQL that don't yet have an embedding.
    Joins research_interests, publications, projects via Python
    (simpler than a wide SQL join).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.faculty_name, f.designation, f.department_id,
               d.canonical_name AS department,
               i.name           AS institute_name,
               f.profile_url
        FROM   faculty f
        LEFT   JOIN departments d ON d.id = f.department_id
        LEFT   JOIN institutes  i ON i.id = f.institute_id
        WHERE  f.embedding_vector IS NULL
        LIMIT  %s
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]

    # Fetch child tables per faculty
    for row in rows:
        fid = row["id"]
        cur.execute(
            "SELECT interest_text, source FROM research_interests WHERE faculty_id = %s", (fid,)
        )
        items = cur.fetchall()
        row["research_interests"] = [r["interest_text"] for r in items if r["source"] == "research_interests"]
        row["research_areas"]     = [r["interest_text"] for r in items if r["source"] == "research_areas"]

        cur.execute("SELECT title FROM publications WHERE faculty_id = %s LIMIT 20", (fid,))
        row["publications"] = [r["title"] for r in cur.fetchall()]

        cur.execute("SELECT title FROM projects WHERE faculty_id = %s LIMIT 10", (fid,))
        row["projects"] = [r["title"] for r in cur.fetchall()]

        row["biography"] = ""   # extend if you add biography column later

    cur.close()
    conn.close()
    return rows


def run_embedding_pipeline(batch_size: int = 64) -> tuple[np.ndarray, list[dict]]:
    """
    Main pipeline:
    1. Fetch unembedded faculty from DB
    2. Generate embeddings in batches
    3. Save vectors to disk (numpy) + metadata JSON
    4. Persist embedding_vector (as JSON string) back to DB

    Returns: (matrix of shape [N, dim], list of metadata dicts)
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    rows = fetch_faculty_for_embedding()
    logger.info("Embedding %d faculty records", len(rows))

    all_vectors: list[np.ndarray] = []
    metadata: list[dict] = []

    conn = get_connection()
    cur = conn.cursor()

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        logger.info("Batch %d–%d / %d", i, i + len(batch), len(rows))

        for row in batch:
            vec = embed_faculty_row(row)
            if vec is None:
                logger.debug("No embeddable text for faculty %s", row["id"])
                continue

            all_vectors.append(vec)
            meta = {
                "faculty_id":  row["id"],
                "faculty_name": row.get("faculty_name", ""),
                "department":   row.get("department", ""),
                "institute":    row.get("institute_name", ""),
                "profile_url":  row.get("profile_url", ""),
            }
            metadata.append(meta)

            # Persist embedding back to DB (as JSON string for portability)
            cur.execute(
                "UPDATE faculty SET embedding_vector = %s WHERE id = %s",
                (json.dumps(vec.tolist()), row["id"]),
            )

        conn.commit()

    cur.close()
    conn.close()

    if not all_vectors:
        logger.warning("No embeddings generated.")
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32), []

    matrix = np.stack(all_vectors).astype(np.float32)

    # Save artefacts
    np_path = PROCESSED_DIR / "faculty_embeddings.npy"
    meta_path = PROCESSED_DIR / "faculty_metadata.json"
    np.save(str(np_path), matrix)
    meta_path.write_text(json.dumps(metadata, indent=2))
    logger.info("Saved %d embeddings → %s", len(all_vectors), np_path)

    return matrix, metadata


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    matrix, meta = run_embedding_pipeline()
    print(f"Embedding matrix: {matrix.shape}")
    print(f"Sample metadata: {meta[:2]}")
