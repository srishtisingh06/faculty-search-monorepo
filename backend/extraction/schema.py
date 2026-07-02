"""
Standard Faculty Record Schema
───────────────────────────────
Every extraction method (rule-based OR LLM) must produce a dict
matching this schema before it goes into the database.

This is the contract between extraction/* and database/db_writer.py.
"""
from pydantic import BaseModel, field_validator
import re

EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.-]+$')


class FacultyRecord(BaseModel):
    name: str
    designation: str = ""
    department: str = ""
    email: str = ""
    phone: str = ""
    research_areas: list[str] = []
    profile_url: str = ""
    scholar_url: str = ""
    linkedin_url: str = ""
    orcid_url: str = ""

    # Metadata about how this record was extracted — useful for monitoring
    extraction_method: str = "rule"   # "rule" | "llm"
    extraction_confidence: float = 0.0

    @field_validator("name")
    @classmethod
    def name_must_be_plausible(cls, v: str) -> str:
        v = (v or "").strip()
        if not v or len(v) < 3 or len(v.split()) > 8:
            raise ValueError("implausible name")
        return v

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str) -> str:
        v = (v or "").strip()
        if v and not EMAIL_RE.fullmatch(v):
            return ""  # drop bad email rather than reject whole record
        return v

    @field_validator("research_areas", mode="before")
    @classmethod
    def clean_research_areas(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            v = [v]
        return [r.strip() for r in v if r and r.strip()]
