"""
Master Pipeline Runner
──────────────────────
Orchestrates all phases:
  Phase 1: Read seed data from Excel
  Phase 2: Crawl (Scrapy for static, Playwright for dynamic)
  Phase 3: Parse raw HTML → structured faculty records
  Phase 4: Store in PostgreSQL
  Phase 5: Generate embeddings
  Phase 6: Build FAISS index

Usage:
    python pipeline.py --phase all
    python pipeline.py --phase crawl
    python pipeline.py --phase parse
    python pipeline.py --phase embed
    python pipeline.py --phase faiss
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from configs.settings import EXCEL_FILES, LOG_DIR, PROCESSED_DIR, RAW_DIR
from data.seed_reader import load_all_institutes
from database.db_writer import run_schema, save_faculty_profile
from embeddings.embed_pipeline import run_embedding_pipeline
from parser.faculty_parser import parse_from_file
from vector_store.faiss_index import build_and_save_index

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "pipeline.log"),
    ],
)
logger = logging.getLogger("pipeline")


# ── Phase helpers ─────────────────────────────────────────────────────────────
def phase_crawl_scrapy(institutes: list[dict]):
    """Launch Scrapy batch runner (spawns subprocesses per institute)."""
    from crawler.scrapy_spiders.run_all_crawls import main as scrapy_main
    scrapy_main()


async def phase_crawl_playwright(institutes: list[dict]):
    """
    Playwright crawler for institutes flagged as dynamic
    (or run after Scrapy to fill gaps).
    """
    from crawler.playwright_crawler.pw_crawler import crawl_institute
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for inst in institutes:
        out = PROCESSED_DIR / f"{inst['name'].replace(' ', '_')}_pw.jsonl"
        results = await crawl_institute(inst["url"], inst["name"], inst["type"])
        with out.open("w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
        logger.info("Playwright done: %s → %d profiles", inst["name"], len(results))


def phase_parse_and_store(institutes: list[dict]):
    """Scan all raw JSONL files, parse HTML, save to PostgreSQL."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    inst_map = {i["name"]: i for i in institutes}

    # Collect all JSONL crawl manifests
    jsonl_files = list(RAW_DIR.rglob("*.jsonl")) + list(PROCESSED_DIR.glob("*.jsonl"))
    logger.info("Found %d crawl manifest files", len(jsonl_files))

    total_parsed = 0
    total_saved = 0

    for jf in jsonl_files:
        with jf.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    meta = json.loads(line)
                except json.JSONDecodeError:
                    continue

                profile = parse_from_file(meta)
                if not profile:
                    continue
                total_parsed += 1

                inst_info = inst_map.get(meta.get("institute_name", ""), {})
                ok = save_faculty_profile(
                    profile,
                    institute_url=inst_info.get("url", ""),
                    institute_type=inst_info.get("type", "Other"),
                    city=inst_info.get("city", ""),
                    state=inst_info.get("state", ""),
                )
                if ok:
                    total_saved += 1

    logger.info("Parse+store done: %d parsed, %d saved to DB", total_parsed, total_saved)


def phase_embed():
    logger.info("Starting embedding pipeline")
    matrix, meta = run_embedding_pipeline()
    logger.info("Embeddings done: %s, %d metadata records", matrix.shape, len(meta))


def phase_faiss():
    logger.info("Building FAISS index")
    index, meta = build_and_save_index()
    logger.info("FAISS index built: %d vectors", index.ntotal)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Faculty Search Pipeline")
    parser.add_argument(
        "--phase",
        choices=["all", "schema", "crawl", "parse", "embed", "faiss"],
        default="all",
    )
    parser.add_argument(
        "--crawler",
        choices=["scrapy", "playwright", "both"],
        default="scrapy",
        help="Which crawler to use in the crawl phase",
    )
    args = parser.parse_args()

    # Load seed data
    institutes = load_all_institutes(
        EXCEL_FILES["iit"],
        EXCEL_FILES["nit_bits"],
        EXCEL_FILES["bits"],
    )
    logger.info("Loaded %d institutes from seed files", len(institutes))

    if args.phase in ("all", "schema"):
        logger.info("── Phase 0: Schema ──")
        run_schema()

    if args.phase in ("all", "crawl"):
        logger.info("── Phase 2: Crawl ──")
        if args.crawler in ("scrapy", "both"):
            phase_crawl_scrapy(institutes)
        if args.crawler in ("playwright", "both"):
            asyncio.run(phase_crawl_playwright(institutes))

    if args.phase in ("all", "parse"):
        logger.info("── Phase 3: Parse & Store ──")
        phase_parse_and_store(institutes)

    if args.phase in ("all", "embed"):
        logger.info("── Phase 5: Embed ──")
        phase_embed()

    if args.phase in ("all", "faiss"):
        logger.info("── Phase 6: FAISS ──")
        phase_faiss()

    logger.info("Pipeline complete.")


if __name__ == "__main__":
    main()
