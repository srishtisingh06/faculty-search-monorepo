"""
Deduplication Layer
─────────────────────
At scale, the same professor can appear from a department listing page
AND a lab page AND a college directory. This catches near-duplicates
that don't share an identical profile_url (your existing PostgreSQL
UPSERT in db_writer.py already handles EXACT profile_url duplicates —
this layer is for fuzzy, cross-page duplicates).

Requires: pip install rapidfuzz --break-system-packages
"""
import logging

from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

NAME_SIMILARITY_THRESHOLD = 90  # 0-100 scale


def is_duplicate(new_record: dict, existing_records: list[dict]) -> str | None:
    """
    Checks new_record against a list of already-seen records
    (e.g. faculty already inserted for this institute in the current run).
    Returns the matching record's identifier if a duplicate is found, else None.

    existing_records entries are expected to have at least: name, email, id
    """
    new_name = (new_record.get("name") or "").lower().strip()
    new_email = (new_record.get("email") or "").lower().strip()

    for existing in existing_records:
        existing_email = (existing.get("email") or "").lower().strip()
        if new_email and existing_email and new_email == existing_email:
            return existing.get("id")

        existing_name = (existing.get("name") or "").lower().strip()
        if new_name and existing_name:
            similarity = fuzz.ratio(new_name, existing_name)
            if similarity >= NAME_SIMILARITY_THRESHOLD:
                return existing.get("id")

    return None


def dedupe_batch(records: list[dict]) -> list[dict]:
    """
    Dedupes a list of freshly-extracted records against each other
    (e.g. before writing a crawl batch to the database).
    Keeps the first occurrence of each apparent duplicate.
    """
    kept: list[dict] = []
    seen_as_existing = []

    for record in records:
        dup_id = is_duplicate(record, seen_as_existing)
        if dup_id is None:
            kept.append(record)
            seen_as_existing.append({
                "id": record.get("profile_url") or record.get("name"),
                "name": record.get("name"),
                "email": record.get("email"),
            })
        else:
            logger.debug("Dropped duplicate: %s", record.get("name"))

    return kept
