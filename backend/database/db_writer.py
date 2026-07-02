"""
Database writer: inserts / upserts parsed faculty data into PostgreSQL.
Uses psycopg2 with explicit transaction management and UPSERT logic.
"""
import logging
import uuid
from contextlib import contextmanager
from typing import Optional

import psycopg2
import psycopg2.extras

from configs.settings import DB_CONFIG

logger = logging.getLogger(__name__)


# ── Connection ────────────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.RealDictCursor)


@contextmanager
def transaction():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def run_schema(schema_path: str = "database/schema.sql"):
    """One-time schema initialisation."""
    with open(schema_path) as f:
        sql = f.read()
    with transaction() as cur:
        cur.execute(sql)
    logger.info("Schema applied.")


# ── Upsert helpers ────────────────────────────────────────────────────────────
def upsert_institute(cur, name: str, inst_type: str, url: str,
                     city: str = "", state: str = "") -> str:

    cur.execute("""
        SELECT id
        FROM institutes
        WHERE LOWER(name)=LOWER(%s)
        LIMIT 1
    """, (name,))

    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE institutes
            SET
                website_url = COALESCE(website_url,%s),
                city = COALESCE(city,%s),
                state = COALESCE(state,%s),
                updated_at = NOW()
            WHERE id=%s
        """, (
            url,
            city,
            state,
            row["id"]
        ))

        return str(row["id"])

    institute_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO institutes
        (
            id,
            name,
            type,
            city,
            state,
            website_url
        )
        VALUES
        (%s,%s,%s,%s,%s,%s)
    """, (
        institute_id,
        name,
        inst_type,
        city,
        state,
        url
    ))

    return institute_id


def upsert_department(cur, institute_id: str, name: str, canonical: str,
                      dept_url: str = "") -> str:
    """Insert or update department; returns its UUID."""
    cur.execute("""
        INSERT INTO departments (id, institute_id, name, canonical_name, dept_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (institute_id, canonical_name) DO UPDATE
            SET name = EXCLUDED.name,
                dept_url = EXCLUDED.dept_url,
                updated_at = NOW()
        RETURNING id
    """, (str(uuid.uuid4()), institute_id, name, canonical, dept_url))
    return str(cur.fetchone()["id"])


def upsert_faculty(cur, profile: dict, institute_id: str,
                   department_id: Optional[str] = None) -> Optional[str]:
    """
    Upsert a faculty record keyed on profile_url.
    Returns faculty UUID or None if insert skipped.
    """
    if not profile.get("faculty_name") or not profile.get("profile_url"):
        return None
    cur.execute("""
        INSERT INTO faculty (
            id, institute_id, department_id, faculty_name, designation,
            email, phone, office, google_scholar, linkedin,
            personal_website, profile_image, profile_url, raw_html_path
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (profile_url) DO UPDATE SET
            faculty_name     = EXCLUDED.faculty_name,
            designation      = EXCLUDED.designation,
            email            = COALESCE(EXCLUDED.email, faculty.email),
            phone            = COALESCE(EXCLUDED.phone, faculty.phone),
            office           = COALESCE(EXCLUDED.office, faculty.office),
            google_scholar   = COALESCE(EXCLUDED.google_scholar, faculty.google_scholar),
            linkedin         = COALESCE(EXCLUDED.linkedin, faculty.linkedin),
            profile_image    = COALESCE(EXCLUDED.profile_image, faculty.profile_image),
            department_id    = COALESCE(EXCLUDED.department_id, faculty.department_id),
            updated_at       = NOW()
        RETURNING id
    """, (
        str(uuid.uuid4()), institute_id, department_id,
        profile.get("faculty_name", ""),
        profile.get("designation", ""),
        profile.get("email", "") or None,
        profile.get("phone", "") or None,
        profile.get("office", "") or None,
        profile.get("google_scholar", "") or None,
        profile.get("linkedin", "") or None,
        profile.get("personal_website", "") or None,
        profile.get("profile_image", "") or None,
        profile["profile_url"],
        profile.get("raw_html_path", "") or None,
    ))
    row = cur.fetchone()
    return str(row["id"]) if row else None


def insert_research_interests(cur, faculty_id: str, interests: list[str],
                               source: str = "research_interests"):
    for text in interests:
        text = text.strip()
        if not text:
            continue
        cur.execute("""
            INSERT INTO research_interests (id, faculty_id, interest_text, source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (faculty_id, interest_text) DO NOTHING
        """, (str(uuid.uuid4()), faculty_id, text, source))


def insert_publications(cur, faculty_id: str, pubs: list[str]):
    for title in pubs:
        title = title.strip()
        if not title:
            continue
        cur.execute("""
            INSERT INTO publications (id, faculty_id, title)
            VALUES (%s, %s, %s)
            ON CONFLICT (faculty_id, title) DO NOTHING
        """, (str(uuid.uuid4()), faculty_id, title))


def insert_education(cur, faculty_id: str, edu_list: list[str]):
    for raw in edu_list:
        raw = raw.strip()
        if not raw:
            continue
        cur.execute("""
            INSERT INTO education (id, faculty_id, raw_text)
            VALUES (%s, %s, %s)
        """, (str(uuid.uuid4()), faculty_id, raw))


def insert_projects(cur, faculty_id: str, projects: list[str]):
    for title in projects:
        title = title.strip()
        if not title:
            continue
        cur.execute("""
            INSERT INTO projects (id, faculty_id, title)
            VALUES (%s, %s, %s)
        """, (str(uuid.uuid4()), faculty_id, title))


# ── Top-level save function ───────────────────────────────────────────────────
def save_faculty_profile(
    profile: dict,
    institute_url: str,
    institute_type: str = "IIT",
    city: str = "",
    state: str = "",
) -> bool:
    """
    Full save pipeline for one parsed FacultyProfile dict.
    Returns True on success.
    """
    try:
        with transaction() as cur:
            # Institutes
            inst_id = upsert_institute(
                cur,
                name=profile.get("institute_name", ""),
                inst_type=institute_type,
                url=institute_url,
                city=city,
                state=state,
            )

            # Department
            dept_id = None
            dept_name = profile.get("department", "").strip()
            if dept_name:
                from configs.settings import DEPARTMENT_CANONICAL
                canonical = DEPARTMENT_CANONICAL.get(dept_name, dept_name)
                dept_id = upsert_department(cur, inst_id, dept_name, canonical)

            # Faculty
            faculty_id = upsert_faculty(cur, profile, inst_id, dept_id)
            if not faculty_id:
                return False

            # Child records
            insert_research_interests(cur, faculty_id, profile.get("research_interests", []))
            insert_research_interests(cur, faculty_id, profile.get("research_areas", []),
                                       source="research_areas")
            insert_publications(cur, faculty_id, profile.get("publications", []))
            insert_education(cur, faculty_id, profile.get("education", []))
            insert_projects(cur, faculty_id, profile.get("projects", []))

        logger.info("Saved: %s @ %s", profile.get("faculty_name"), profile.get("institute_name"))
        return True

    except Exception as exc:
        logger.error("DB save failed for %s: %s", profile.get("profile_url"), exc)
        return False
