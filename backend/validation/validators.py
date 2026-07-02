"""
Validation Layer
──────────────────
Final gate before a record reaches the database. Catches:
  - Hallucinated/malformed LLM output (rule-based rarely hallucinates,
    it either matches or returns None)
  - Implausible names, bad email formats

Uses extraction/schema.py (FacultyRecord) for the actual validation.
"""
import logging

from pydantic import ValidationError

from extraction.schema import FacultyRecord

logger = logging.getLogger(__name__)


def validate_record(raw_dict: dict | None, extraction_method: str, confidence: float) -> dict | None:
    """
    Validates a raw extracted dict against FacultyRecord schema.
    Returns a clean dict ready for db_writer, or None if invalid.
    """
    if not raw_dict or not raw_dict.get("name"):
        return None

    raw_dict = dict(raw_dict)  # don't mutate caller's dict
    raw_dict["extraction_method"] = extraction_method
    raw_dict["extraction_confidence"] = confidence

    try:
        record = FacultyRecord(**raw_dict)
        return record.model_dump()
    except ValidationError as exc:
        logger.debug("Record failed validation (%s): %s", raw_dict.get("name", "?"), exc)
        return None
