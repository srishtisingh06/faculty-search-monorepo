"""
FastAPI REST API — Faculty Search System
Exposes:
  GET  /search?q=...&top_k=10        – semantic search
  GET  /faculty/{faculty_id}         – profile detail
  GET  /institutes                   – list all institutes
  GET  /health                       – liveness check
"""
import logging
from functools import lru_cache
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embeddings.embed_pipeline import _get_model
from configs.settings import FAISS_INDEX_PATH, FAISS_META_PATH
from database.db_writer import get_connection
from vector_store.faiss_index import load_index, search_by_text
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Faculty Search API",
    description="Semantic search over IIT/NIT/BITS faculty profiles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def preload_model():
    print("Loading embedding model...")
    _get_model()
    print("Embedding model loaded.")

# ── Pydantic models ───────────────────────────────────────────────────────────
class SearchResult(BaseModel):
    faculty_id: str
    faculty_name: str
    designation: Optional[str]
    department: Optional[str]
    institute: Optional[str]
    profile_url: str
    score: float


class FacultyDetail(BaseModel):
    id: str
    faculty_name: str
    designation: Optional[str]
    department: Optional[str]
    institute_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    office: Optional[str]
    google_scholar: Optional[str]
    linkedin: Optional[str]
    personal_website: Optional[str]
    profile_image: Optional[str]
    profile_url: str
    research_interests: list[str]
    research_areas: list[str]
    publications: list[str]
    education: list[str]

class InstituteSummary(BaseModel):
    id: str
    name: str
    type: str
    city: Optional[str]
    state: Optional[str]
    website_url: Optional[str]
    faculty_count: int
    department_count: int
    publication_count: int

# ── FAISS (lazy-loaded, cached) ────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _faiss():
    try:
        return load_index(FAISS_INDEX_PATH, FAISS_META_PATH)
    except FileNotFoundError:
        logger.warning("FAISS index not found — semantic search unavailable")
        return None, []


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/search", response_model=list[SearchResult])
def semantic_search(
    q: str = Query(..., min_length=2, description="Search query"),
    top_k: int = Query(10, ge=1, le=50),
    institute_type: Optional[str] = Query(None, description="IIT | NIT | BITS"),
    department: Optional[str] = Query(None),
):
    index, metadata = _faiss()
    if index is None:
        raise HTTPException(503, "Vector index not available. Run embed + faiss pipeline first.")

    hits = search_by_text(q, index, metadata, top_k=top_k * 3)

    # Enrich with DB data and apply optional filters
    conn = get_connection()
    cur = conn.cursor()
    results = []
    for hit in hits:
        fid = hit.get("faculty_id")
        if not fid:
            continue
        cur.execute("""
            SELECT f.id, f.faculty_name, f.designation, f.profile_url,
                   d.canonical_name AS department,
                   i.name AS institute_name, i.type AS institute_type
            FROM   faculty f
            LEFT   JOIN departments d ON d.id = f.department_id
            LEFT   JOIN institutes  i ON i.id = f.institute_id
            WHERE  f.id = %s
        """, (fid,))
        row = cur.fetchone()
        if not row:
            continue
        if institute_type and row["institute_type"] != institute_type.upper():
            continue
        if department and department.lower() not in (row["department"] or "").lower():
            continue
        results.append(SearchResult(
            faculty_id=str(row["id"]),
            faculty_name=row["faculty_name"],
            designation=row.get("designation"),
            department=row.get("department"),
            institute=row.get("institute_name"),
            profile_url=row["profile_url"],
            score=hit["score"],
        ))
        if len(results) >= top_k:
            break

    cur.close()
    conn.close()
    return results


@app.get("/faculty/{faculty_id}", response_model=FacultyDetail)
def get_faculty(faculty_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT f.id, f.faculty_name, f.designation, f.email, f.phone,
               f.office, f.google_scholar, f.linkedin, f.personal_website,
               f.profile_image, f.profile_url,
               d.canonical_name AS department,
               i.name AS institute_name
        FROM   faculty f
        LEFT   JOIN departments d ON d.id = f.department_id
        LEFT   JOIN institutes  i ON i.id = f.institute_id
        WHERE  f.id = %s
    """, (faculty_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Faculty not found")

    cur.execute(
        "SELECT interest_text, source FROM research_interests WHERE faculty_id = %s", (faculty_id,)
    )
    interests = cur.fetchall()
    cur.execute("SELECT title FROM publications WHERE faculty_id = %s", (faculty_id,))
    pubs = [r["title"] for r in cur.fetchall()]
    cur.execute("SELECT raw_text FROM education WHERE faculty_id = %s", (faculty_id,))
    edu = [r["raw_text"] for r in cur.fetchall()]

    cur.close()
    conn.close()

    return FacultyDetail(
        id=str(row["id"]),
        faculty_name=row["faculty_name"],
        designation=row.get("designation"),
        department=row.get("department"),
        institute_name=row.get("institute_name"),
        email=row.get("email"),
        phone=row.get("phone"),
        office=row.get("office"),
        google_scholar=row.get("google_scholar"),
        linkedin=row.get("linkedin"),
        personal_website=row.get("personal_website"),
        profile_image=row.get("profile_image"),
        profile_url=row["profile_url"],
        research_interests=[r["interest_text"] for r in interests if r["source"] == "research_interests"],
        research_areas=[r["interest_text"] for r in interests if r["source"] == "research_areas"],
        publications=pubs,
        education=edu,
    )


@app.get("/institutes", response_model=list[InstituteSummary])
def list_institutes(type: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            i.id,
            i.name,
            i.type,
            i.city,
            i.state,
            i.website_url,

            COUNT(DISTINCT f.id) AS faculty_count,
            COUNT(DISTINCT d.id) AS department_count,
            COUNT(DISTINCT p.id) AS publication_count

        FROM institutes i

        LEFT JOIN faculty f
            ON f.institute_id = i.id

        LEFT JOIN departments d
            ON d.institute_id = i.id

        LEFT JOIN publications p
            ON p.faculty_id = f.id
    """

    params = []

    if type:
        sql += " WHERE i.type = %s "
        params.append(type.upper())

    sql += """
        GROUP BY
            i.id,
            i.name,
            i.type,
            i.city,
            i.state,
            i.website_url

        ORDER BY i.name
    """

    cur.execute(sql, tuple(params))

    rows = []

    for r in cur.fetchall():
        rows.append(
            InstituteSummary(
                id=str(r["id"]),
                name=r["name"],
                type=r["type"],
                city=r["city"],
                state=r["state"],
                website_url=r["website_url"],
                faculty_count=r["faculty_count"],
                department_count=r["department_count"],
                publication_count=r["publication_count"],
            )
        )

    cur.close()
    conn.close()

    return rows
@app.get("/institutes/{institute_id}")
def get_institute(institute_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            i.id,
            i.name,
            i.short_name,
            i.type,
            i.city,
            i.state,
            i.website_url,

            COUNT(DISTINCT f.id) AS faculty_count,
            COUNT(DISTINCT d.id) AS department_count,
            COUNT(DISTINCT p.id) AS publication_count

        FROM institutes i

        LEFT JOIN faculty f
            ON f.institute_id = i.id

        LEFT JOIN departments d
            ON d.institute_id = i.id

        LEFT JOIN publications p
            ON p.faculty_id = f.id

        WHERE i.id = %s

        GROUP BY
            i.id,
            i.name,
            i.short_name,
            i.type,
            i.city,
            i.state,
            i.website_url
        """,
        (institute_id,),
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Institute not found",
        )

    return dict(row)


@app.get("/institutes/{institute_id}/faculty")
def institute_faculty(institute_id: str, limit: int = 10):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            f.id,
            f.faculty_name,
            f.designation,
            d.canonical_name AS department,
            f.profile_image,
            f.profile_url

        FROM faculty f

        LEFT JOIN departments d
            ON d.id = f.department_id

        WHERE f.institute_id = %s

        ORDER BY f.faculty_name
        LIMIT %s
        """,
        (institute_id, limit),
    )

    rows = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return rows
@app.get("/institutes/{institute_id}/departments")
def institute_departments(institute_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            d.id,
            d.name,
            d.canonical_name,

            COUNT(DISTINCT f.id) AS faculty_count,
            COUNT(DISTINCT p.id) AS publication_count

        FROM departments d

        LEFT JOIN faculty f
            ON f.department_id = d.id

        LEFT JOIN publications p
            ON p.faculty_id = f.id

        WHERE d.institute_id = %s

        GROUP BY
            d.id,
            d.name,
            d.canonical_name

        ORDER BY faculty_count DESC
        """,
        (institute_id,),
    )

    rows = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return rows
@app.get("/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM institutes")
    institutes = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM faculty")
    faculty = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM departments")
    departments = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM publications")
    publications = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return {
        "institutes": institutes,
        "faculty": faculty,
        "departments": departments,
        "publications": publications,
    }
@app.get("/institutes/{institute_id}/research-areas")
def institute_research_areas(institute_id: str, limit: int = 8):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            ri.interest_text AS name,
            COUNT(DISTINCT ri.faculty_id) AS faculty_count
        FROM research_interests ri
        JOIN faculty f
            ON f.id = ri.faculty_id
        WHERE f.institute_id = %s
        GROUP BY ri.interest_text
        ORDER BY faculty_count DESC
        LIMIT %s
        """,
        (institute_id, limit),
    )

    rows = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return rows

class DepartmentSummary(BaseModel):
    id: str
    name: str
    faculty_count: int
    publication_count: int


@app.get("/departments")
def list_departments():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.canonical_name AS department,
            COUNT(DISTINCT f.id) AS faculty,
            COUNT(DISTINCT p.id) AS publications
        FROM departments d
        LEFT JOIN faculty f
            ON f.department_id = d.id
        LEFT JOIN publications p
            ON p.faculty_id = f.id
        GROUP BY d.canonical_name
        ORDER BY faculty DESC
    """)

    departments = [dict(r) for r in cur.fetchall()]

    for dept in departments:
        dept_name = dept["department"]

        cur.execute("""
            SELECT
                i.name AS institute,
                COUNT(DISTINCT f.id) AS faculty_count
            FROM faculty f
            JOIN departments d
                ON d.id = f.department_id
            JOIN institutes i
                ON i.id = f.institute_id
            WHERE d.canonical_name = %s
            GROUP BY i.name
            ORDER BY faculty_count DESC
            LIMIT 3
        """, (dept_name,))

        dept["top_institutes"] = [
            r["institute"] for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT
                ri.interest_text AS name,
                COUNT(DISTINCT ri.faculty_id) AS count
            FROM research_interests ri
            JOIN faculty f
                ON f.id = ri.faculty_id
            JOIN departments d
                ON d.id = f.department_id
            WHERE
                d.canonical_name = %s
                AND ri.interest_text IS NOT NULL
                AND TRIM(ri.interest_text) <> ''
            GROUP BY ri.interest_text
            ORDER BY count DESC
            LIMIT 8
        """, (dept_name,))

        dept["research_areas"] = [
            dict(r) for r in cur.fetchall()
        ]

    cur.close()
    conn.close()

    return departments
@app.get("/coverage")
def coverage():
    conn = get_connection()
    cur = conn.cursor()

    # Overall counts
    cur.execute("SELECT COUNT(*) AS count FROM institutes")
    institutes = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM faculty")
    faculty = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM departments")
    departments = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM publications")
    publications = cur.fetchone()["count"]

    # Institute type coverage
    cur.execute("SELECT COUNT(*) AS count FROM institutes WHERE type = 'IIT'")
    iit = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM institutes WHERE type = 'NIT'")
    nit = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM institutes WHERE type = 'BITS'")
    bits = cur.fetchone()["count"]

    overall = iit + nit + bits

    cur.close()
    conn.close()

    return {
        "institutes": institutes,
        "faculty": faculty,
        "departments": departments,
        "publications": publications,

        "iit": {
            "covered": iit,
            "total": 23,
            "percentage": round((iit / 23) * 100, 1)
        },

        "nit": {
            "covered": nit,
            "total": 31,
            "percentage": round((nit / 31) * 100, 1)
        },

        "bits": {
            "covered": bits,
            "total": 5,
            "percentage": round((bits / 5) * 100, 1)
        },

        "overall": {
            "covered": overall,
            "total": 59,
            "percentage": round((overall / 59) * 100, 1)
        }
    }
@app.get("/institute-type-coverage")
def institute_type_coverage():

    conn = get_connection()
    cur = conn.cursor()

    result = {}

    for institute_type in ["IIT", "NIT", "BITS"]:

        cur.execute("""
            SELECT
                i.name,
                COUNT(f.id) AS faculty
            FROM institutes i
            LEFT JOIN faculty f
                ON f.institute_id = i.id
            WHERE i.type = %s
            GROUP BY i.name
            ORDER BY faculty DESC;
        """, (institute_type,))

        institutes = []

        for row in cur.fetchall():

            faculty = row["faculty"]
            coverage = min(100, round((faculty / 300) * 100))

            institutes.append({
                "name": row["name"],
                "faculty": faculty,
                "coverage": coverage,
            })

        result[institute_type.lower()] = institutes

    cur.close()
    conn.close()

    return result

@app.get("/department-coverage")
def department_coverage():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.canonical_name AS department,
            COUNT(DISTINCT f.id) AS faculty,
            COUNT(DISTINCT p.id) AS publications
        FROM departments d
        LEFT JOIN faculty f
            ON f.department_id = d.id
        LEFT JOIN publications p
            ON p.faculty_id = f.id
        GROUP BY d.canonical_name
        ORDER BY faculty DESC;
    """)

    rows = []

    for row in cur.fetchall():

        faculty = row["faculty"]

        percentage = min(100, round((faculty / 412) * 100))

        rows.append({
            "department": row["department"],
            "faculty": faculty,
            "publications": row["publications"],
            "percentage": percentage,
        })

    cur.close()
    conn.close()

    return rows

@app.get("/state-coverage")
def state_coverage():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            state,
            COUNT(*) AS institutes,
            (
                SELECT COUNT(*)
                FROM faculty f
                WHERE f.institute_id IN (
                    SELECT id
                    FROM institutes i2
                    WHERE i2.state = institutes.state
                )
            ) AS faculty

        FROM institutes
        GROUP BY state
        ORDER BY institutes DESC;
    """)

    result = []

    for row in cur.fetchall():

        result.append({
            "state": row["state"],
            "institutes": row["institutes"],
            "faculty": row["faculty"],
        })

    cur.close()
    conn.close()

    return result

@app.get("/coverage-map")
def coverage_map():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS count FROM institutes")
    institutes = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM faculty")
    faculty = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM departments")
    departments = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM publications")
    publications = cur.fetchone()["count"]

    cur.execute("""
        SELECT COUNT(DISTINCT state) AS count
        FROM institutes
    """)

    states = cur.fetchone()["count"]

    cur.close()
    conn.close()

    return {
        "states": states,
        "institutes": institutes,
        "faculty": faculty,
        "departments": departments,
        "publications": publications,
    }
@app.get("/analytics/summary")
def analytics_summary():
    conn = get_connection()
    cur = conn.cursor()

    # Total Institutes
    cur.execute("SELECT COUNT(*) AS count FROM institutes")
    institutes = cur.fetchone()["count"]

    # Total Faculty
    cur.execute("SELECT COUNT(*) AS count FROM faculty")
    faculty = cur.fetchone()["count"]

    # Total Departments
    cur.execute("""
        SELECT COUNT(DISTINCT canonical_name) AS count
        FROM departments
    """)
    departments = cur.fetchone()["count"]

    # Total Publications
    cur.execute("SELECT COUNT(*) AS count FROM publications")
    publications = cur.fetchone()["count"]

    cur.close()
    conn.close()

    return {
        "institutes": institutes,
        "faculty": faculty,
        "departments": departments,
        "publications": publications
    }
@app.get("/analytics/institute-types")
def analytics_institute_types():
    conn = get_connection()
    cur = conn.cursor()

    result = []

    for t in ["IIT", "NIT", "BITS"]:

        cur.execute("""
            SELECT COUNT(f.id) AS faculty
            FROM institutes i
            LEFT JOIN faculty f
            ON i.id=f.institute_id
            WHERE i.type=%s
        """,(t,))

        faculty = cur.fetchone()["faculty"] or 0

        result.append({
            "name":t,
            "faculty":faculty
        })

    cur.close()
    conn.close()

    return result
@app.get("/analytics/departments")
def analytics_departments():

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT
            canonical_name,
            COUNT(*) AS departments
        FROM departments
        GROUP BY canonical_name
        ORDER BY departments DESC
    """)

    rows=cur.fetchall()

    data=[]

    for row in rows:

        cur.execute("""
            SELECT COUNT(*)
            FROM faculty f
            JOIN departments d
            ON f.department_id=d.id
            WHERE d.canonical_name=%s
        """,(row["canonical_name"],))

        faculty=cur.fetchone()["count"]

        data.append({
            "department":row["canonical_name"],
            "faculty":faculty
        })

    cur.close()
    conn.close()

    return data
@app.get("/analytics/states")
def analytics_states():

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT
            state,
            COUNT(DISTINCT id) AS institutes
        FROM institutes
        GROUP BY state
    """)

    rows=cur.fetchall()

    result=[]

    for row in rows:

        cur.execute("""
            SELECT COUNT(f.id) AS faculty
            FROM faculty f
            JOIN institutes i
            ON f.institute_id=i.id
            WHERE i.state=%s
        """,(row["state"],))

        faculty=cur.fetchone()["faculty"]

        result.append({
            "state":row["state"],
            "institutes":row["institutes"],
            "faculty":faculty
        })

    cur.close()
    conn.close()

    return result
@app.get("/analytics/states")
def analytics_states():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            state,
            COUNT(DISTINCT id) AS institutes,
            (
                SELECT COUNT(*)
                FROM faculty f
                JOIN institutes i2
                ON f.institute_id=i2.id
                WHERE i2.state=i.state
            ) AS faculty
        FROM institutes i
        GROUP BY state
        ORDER BY faculty DESC;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows