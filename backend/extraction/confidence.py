"""
Confidence Scoring
───────────────────
Decides per-record whether rule-based extraction succeeded well enough,
or whether this record should escalate to the LLM fallback.

This is the routing logic that keeps LLM usage low — only records that
score below threshold ever reach Ollama.
"""
import re

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")

CONFIDENCE_THRESHOLD = 0.5


def score_confidence(extracted: dict | None) -> float:
    """Returns 0.0 - 1.0. Higher = more trustworthy rule-based extraction."""
    if not extracted:
        return 0.0

    score = 0.0
    name = extracted.get("name", "")
    if name and 2 <= len(name.split()) <= 5:
        score += 0.5

    email = extracted.get("email", "")
    if email and EMAIL_RE.fullmatch(email):
        score += 0.3

    if extracted.get("designation"):
        score += 0.2

    return min(score, 1.0)


def needs_llm_fallback(extracted: dict | None, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
    return score_confidence(extracted) < threshold
