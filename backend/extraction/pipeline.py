"""
Extraction Pipeline — Orchestrator
─────────────────────────────────────
This is the single entry point that ties everything together:

  raw HTML
     │
     ▼
  clean_html()              (extraction/html_cleaner.py)
     │
     ▼
  detect_repeating_blocks() (extraction/pattern_detector.py)  → list of card Tags
     │
     ▼  for each card:
  rule_extract()            (extraction/rule_extractor.py)
     │
     ▼
  score_confidence()        (extraction/confidence.py)
     │
     ├── confident enough?  ──► use rule result
     │
     └── not confident?     ──► llm_extract() via Ollama (extraction/llm_extractor.py)
                                  (checked against cache/llm_cache.py first)
     │
     ▼
  validate_record()         (validation/validators.py)
     │
     ▼
  dedupe_batch()             (validation/dedup.py)
     │
     ▼
  list[dict] ready for database/db_writer.py

Usage:
    from extraction.pipeline import process_page

    records = process_page(raw_html, source_url="https://example.edu/faculty")
    for r in records:
        save_faculty_profile(r, institute_url=..., institute_type=...)
"""
import logging

from extraction.html_cleaner import clean_html, to_plain_text
from extraction.pattern_detector import detect_repeating_blocks
from extraction.rule_extractor import rule_extract
from extraction.confidence import score_confidence, needs_llm_fallback
from extraction.llm_extractor import llm_extract_batch
from validation.validators import validate_record
from validation.dedup import dedupe_batch
from cache.llm_cache import LLMCache

logger = logging.getLogger(__name__)

_cache = LLMCache()


def process_page(raw_html: str, source_url: str = "", use_llm_fallback: bool = True) -> list[dict]:
    """
    Full pipeline for a single crawled page.
    Returns a list of clean, validated, deduplicated faculty dicts.
    """
    soup = clean_html(raw_html)
    cards = detect_repeating_blocks(soup)

    if not cards:
        logger.info("No repeating card blocks detected on %s", source_url)
        return []

    logger.info("Detected %d candidate cards on %s", len(cards), source_url)

    rule_results: list[dict | None] = []
    needs_llm_idx: list[int] = []
    card_texts: list[str] = []

    # Pass 1 — rule-based extraction on every card
    for i, card in enumerate(cards):
        card_html = str(card)
        extracted = rule_extract(card_html)
        confidence = score_confidence(extracted)

        if extracted and not needs_llm_fallback(extracted):
            extracted["extraction_method"] = "rule"
            extracted["extraction_confidence"] = confidence
            rule_results.append(extracted)
        else:
            rule_results.append(None)
            needs_llm_idx.append(i)
            card_texts.append(to_plain_text(card))

    logger.info(
        "Rules succeeded on %d/%d cards. %d cards need LLM fallback.",
        len(cards) - len(needs_llm_idx), len(cards), len(needs_llm_idx)
    )

    # Pass 2 — LLM fallback, only for what rules couldn't handle
    if use_llm_fallback and needs_llm_idx:
        llm_inputs = []
        cache_hits = {}
        for local_i, text in enumerate(card_texts):
            cached = _cache.get(text)
            if cached is not None:
                cache_hits[local_i] = cached
            else:
                llm_inputs.append((local_i, text))

        if llm_inputs:
            texts_to_send = [t for _, t in llm_inputs]
            llm_results = llm_extract_batch(texts_to_send)
            for (local_i, text), result in zip(llm_inputs, llm_results):
                if result:
                    _cache.set(text, result)
                cache_hits[local_i] = result
            _cache.save()

        for local_i, page_i in enumerate(needs_llm_idx):
            result = cache_hits.get(local_i)
            if result:
                result["extraction_method"] = "llm"
                result["extraction_confidence"] = score_confidence(result)
                rule_results[page_i] = result

    # Pass 3 — validate everything
    validated = []
    for extracted in rule_results:
        if extracted is None:
            continue
        clean = validate_record(
            extracted,
            extraction_method=extracted.get("extraction_method", "rule"),
            confidence=extracted.get("extraction_confidence", 0.0),
        )
        if clean:
            if source_url and not clean.get("profile_url"):
                clean["profile_url"] = source_url
            validated.append(clean)

    logger.info("%d/%d cards passed validation", len(validated), len(cards))

    # Pass 4 — dedupe within this page's results
    deduped = dedupe_batch(validated)
    if len(deduped) != len(validated):
        logger.info("Dropped %d duplicates", len(validated) - len(deduped))

    return deduped
