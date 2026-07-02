"""
LLM Extraction Layer — Ollama (local, free)
──────────────────────────────────────────────
Used ONLY as a fallback when rule_extractor.py + confidence.py decide
the rules failed. Never sees raw HTML — only the already-cleaned,
already-isolated card text from html_cleaner.py.

Runs locally via Ollama (llama3.2:3b) — zero API cost, but slower than
a cloud API and somewhat less accurate. The rule-based layer doing
60-70% of the work is what makes this acceptable: the LLM only handles
records the regex/CSS approach couldn't.

Prereqs:
    ollama pull llama3.2:3b
    pip install ollama --break-system-packages
"""
import json
import logging
import re

import ollama

logger = logging.getLogger(__name__)

MODEL_NAME = "llama3.2:3b"
MAX_INPUT_CHARS = 1500   # defensive truncation — a single faculty card never needs more

SCHEMA_HINT = """{"name": "", "designation": "", "department": "", "email": "", "phone": "", "research_areas": [], "scholar_url": "", "linkedin_url": "", "orcid_url": ""}"""

PROMPT_TEMPLATE = """Extract faculty information from this text. Return ONLY valid JSON matching this exact schema. Use "" for missing string fields and [] for missing arrays. Do not invent data that isn't present in the text.

Schema:
{schema}

Text:
{text}

JSON:"""


def _safe_json_parse(raw_response: str) -> dict | None:
    """LLMs sometimes wrap JSON in markdown fences or add commentary — strip that."""
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # If there's text before/after the JSON object, extract just the {...}
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("LLM returned unparseable JSON: %s", raw_response[:200])
        return None


def llm_extract(card_text: str, schema_hint: str = SCHEMA_HINT) -> dict | None:
    """
    Single-record LLM extraction. card_text should already be cleaned
    plain text (from html_cleaner.to_plain_text), not raw HTML.
    """
    truncated = card_text[:MAX_INPUT_CHARS]
    prompt = PROMPT_TEMPLATE.format(schema=schema_hint, text=truncated)

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        raw = response["message"]["content"]
        return _safe_json_parse(raw)
    except Exception as exc:
        logger.error("Ollama extraction failed: %s", exc)
        return None


def llm_extract_batch(card_texts: list[str], schema_hint: str = SCHEMA_HINT) -> list[dict | None]:
    """
    Batch multiple cards into ONE prompt to cut per-call overhead.
    Returns a list of dicts (or None for entries that failed to parse),
    same order as input.
    """
    if not card_texts:
        return []

    numbered = "\n\n".join(
        f"[{i}]\n{t[:MAX_INPUT_CHARS]}" for i, t in enumerate(card_texts)
    )
    prompt = f"""Extract faculty info from each numbered text block below. Return a JSON array, one object per block, in the same order. Each object must match this schema exactly:
{schema_hint}

Use "" for missing string fields and [] for missing arrays. Do not invent data.

{numbered}

JSON array:"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )
        raw = response["message"]["content"]
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group()
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            raise ValueError("Expected JSON array")
        # Pad/truncate to match input length defensively
        while len(parsed) < len(card_texts):
            parsed.append(None)
        return parsed[: len(card_texts)]
    except Exception as exc:
        logger.error("Batch LLM extraction failed, falling back to per-record: %s", exc)
        # Fallback: process one at a time if batch parsing fails
        return [llm_extract(t, schema_hint) for t in card_texts]
