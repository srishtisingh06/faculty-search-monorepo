"""Central configuration for Faculty Search System."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Database ──────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "database": os.getenv("PGDATABASE", "faculty_search"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
}
DATABASE_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ── Input Files ───────────────────────────────────────────────────────────────
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

EXCEL_FILES = {
    "iit": DATA_DIR / "IIT_Colleges_List(1).xlsx",
    "nit_bits": DATA_DIR / "NIT_BITS_Colleges_List.xlsx",
    "bits": DATA_DIR / "BITS_Colleges_List(1).xlsx",
    "tracker": DATA_DIR / "College_Department_Tracker(3).xlsx",
}

# ── Target Departments ────────────────────────────────────────────────────────
TARGET_DEPARTMENTS = [
    "Computer Science",
    "CSE",
    "Computer Engineering",
    "Electronics",
    "ECE",
    "Electrical",
    "EEE",
    "Mechanical",
    "Mathematics",
    "Maths",
]

DEPARTMENT_CANONICAL = {
    "CSE": "Computer Science & Engineering",
    "Computer Science": "Computer Science & Engineering",
    "Computer Engineering": "Computer Science & Engineering",
    "ECE": "Electronics & Communication Engineering",
    "Electronics": "Electronics & Communication Engineering",
    "EEE": "Electrical & Electronics Engineering",
    "Electrical": "Electrical Engineering",
    "Mechanical": "Mechanical Engineering",
    "Mathematics": "Mathematics",
    "Maths": "Mathematics",
}

# ── Crawler ───────────────────────────────────────────────────────────────────
SCRAPY_SETTINGS = {
    "CONCURRENT_REQUESTS": 8,
    "DOWNLOAD_DELAY": 1.5,
    "RANDOMIZE_DOWNLOAD_DELAY": True,
    "RETRY_TIMES": 3,
    "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],
    "ROBOTSTXT_OBEY": True,
    "USER_AGENT": (
        "Mozilla/5.0 (compatible; AcademiaBot/1.0; "
        "+https://github.com/yourorg/faculty-search)"
    ),
    "HTTPCACHE_ENABLED": True,
    "HTTPCACHE_DIR": str(RAW_DIR / "scrapy_cache"),
    "FEEDS": {str(RAW_DIR / "scraped_%(name)s.jsonl"): {"format": "jsonlines"}},
    "LOG_LEVEL": "INFO",
    "LOG_FILE": str(BASE_DIR / "logs" / "scrapy.log"),
}

PLAYWRIGHT_TIMEOUT = 30_000   # ms
PLAYWRIGHT_HEADLESS = True

# ── Embedding ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
CHUNK_SIZE = 512          # tokens
CHUNK_OVERLAP = 64

# ── FAISS ─────────────────────────────────────────────────────────────────────
FAISS_INDEX_TYPE = "HNSW"   # "Flat", "IVF", "HNSW"
FAISS_HNSW_M = 32
FAISS_IVF_NLIST = 64
FAISS_INDEX_PATH = str(BASE_DIR / "vector_store" / "faculty.index")
FAISS_META_PATH = str(BASE_DIR / "vector_store" / "faculty_meta.json")

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = BASE_DIR / "logs"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
