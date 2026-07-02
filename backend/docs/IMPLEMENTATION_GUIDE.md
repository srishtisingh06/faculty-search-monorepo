# Faculty Discovery & Semantic Search System
## Complete Implementation Guide — Technical Mentor Review

---

## PART 1 — PROJECT STATUS REVIEW

### Progress Table

| Module | File | Status | Completion % | Remarks |
|---|---|---|---|---|
| Config & Settings | `configs/settings.py` | ✅ Complete | 100% | All paths, DB, FAISS, embedding params |
| Excel Seed Reader | `data/seed_reader.py` | ✅ Complete | 100% | Reads IIT/NIT/BITS xlsx, normalises URLs |
| Scrapy Crawler | `crawler/scrapy_spiders/faculty_spider.py` | ✅ Complete | 90% | Needs `scrapy.cfg` and `__init__.py` to run |
| Scrapy Batch Runner | `crawler/scrapy_spiders/run_all_crawls.py` | ✅ Complete | 95% | Checkpoint logic, subprocess runner |
| Playwright Crawler | `crawler/playwright_crawler/pw_crawler.py` | ⚠️ Partial | 75% | Missing batch runner equivalent for Playwright |
| Faculty Parser | `parser/faculty_parser.py` | ✅ Complete | 90% | Solid extraction; edge cases need real-site testing |
| PostgreSQL Schema | `database/schema.sql` | ✅ Complete | 100% | Production-grade, triggers, indexes, FK |
| DB Writer | `database/db_writer.py` | ✅ Complete | 95% | Full UPSERT pipeline; needs connection pool for scale |
| Embedding Pipeline | `embeddings/embed_pipeline.py` | ✅ Complete | 90% | Chunking + mean-pool + DB writeback |
| FAISS Index | `vector_store/faiss_index.py` | ✅ Complete | 90% | Flat/IVF/HNSW with metadata; HNSW recommended |
| FastAPI | `api/main.py` | ✅ Complete | 85% | Search + detail + institutes endpoints |
| Master Pipeline | `pipeline.py` | ✅ Complete | 90% | Orchestrates all phases end to end |
| `requirements.txt` | ❌ Missing | 0% | Must create before anything runs |
| `scrapy.cfg` | ❌ Missing | 0% | Scrapy won't run without it |
| `.env` file | ❌ Missing | 0% | DB credentials must be externalised |
| `__init__.py` files | ❌ Missing | 0% | Python package imports will fail |
| Playwright batch runner | ❌ Missing | 0% | No equivalent of `run_all_crawls.py` for PW |
| Tests | ❌ Missing | 0% | No test files exist yet |
| Logging setup module | ⚠️ Partial | 40% | Defined in settings but no central logger module |
| Docker / docker-compose | ❌ Missing | 0% | Optional but strongly recommended |

---

### What Is Already MVP-Ready

The following pieces are fully written and will work once the missing files below are added:

- Reading institutes from Excel and extracting URLs
- Scrapy spider that discovers department + faculty pages on a static site
- Playwright crawler for JS-rendered sites
- HTML parser that extracts name, email, designation, research interests, publications
- PostgreSQL schema with all tables, indexes, and UPSERT logic
- Embedding pipeline using `sentence-transformers`
- FAISS HNSW index builder and semantic search
- REST API with `/search`, `/faculty/{id}`, `/institutes`

### What Is Still Missing (Must Create Before Running)

1. `requirements.txt` — without this you cannot install any dependency
2. `scrapy.cfg` — Scrapy refuses to run without a project config file
3. `__init__.py` in every folder — without these, `from crawler.xxx import yyy` fails
4. `.env` file — DB password must not be hardcoded
5. Playwright batch runner — there is no script to run Playwright across all institutes
6. Tests — no verification that individual modules work

### MVP vs Advanced Features

**MVP (get this working first):**
- Excel reader → Scrapy crawler → Parser → PostgreSQL → Basic keyword search via SQL

**Advanced (add after MVP works):**
- Playwright crawler (for dynamic sites)
- Sentence-transformer embeddings
- FAISS semantic search
- FastAPI REST endpoints
- Docker deployment

---

## PART 2 — MISSING FILES TO CREATE RIGHT NOW

### 2.1 `requirements.txt`

```
# Core
scrapy==2.11.2
playwright==1.44.0
beautifulsoup4==4.12.3
lxml==5.2.2
requests==2.32.3

# Database
psycopg2-binary==2.9.9

# Data
pandas==2.2.2
openpyxl==3.1.2
numpy==1.26.4

# Embeddings
sentence-transformers==3.0.1
faiss-cpu==1.8.0

# API
fastapi==0.111.0
uvicorn==0.30.1

# Utilities
python-dotenv==1.0.1
tqdm==4.66.4
```

### 2.2 `.env`

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=faculty_search
PGUSER=postgres
PGPASSWORD=your_password_here
```

### 2.3 `scrapy.cfg`

```ini
[settings]
default = crawler.scrapy_spiders.settings_scrapy

[deploy]
project = faculty_search
```

### 2.4 `__init__.py` files needed

Create an empty file at each of these paths:
```
configs/__init__.py
data/__init__.py
crawler/__init__.py
crawler/scrapy_spiders/__init__.py
crawler/playwright_crawler/__init__.py
parser/__init__.py
database/__init__.py
embeddings/__init__.py
vector_store/__init__.py
api/__init__.py
```

---

## PART 3 — FILE-BY-FILE EXPLANATION

### `configs/settings.py`

**Purpose:** Central configuration file. All paths, DB credentials, crawler settings, embedding model name, FAISS parameters live here. Every other file imports from this.

**When it runs:** At import time — it runs whenever any other module loads it.

**Input:** Environment variables (DB password, host etc.)

**Output:** Python constants imported by other modules

**Dependencies:** `python-dotenv`, `pathlib`, `os`

**Common errors:**
- `ModuleNotFoundError: No module named 'configs'` → You forgot `__init__.py` in `configs/`
- DB connection fails → Check `.env` values match your PostgreSQL setup

---

### `data/seed_reader.py`

**Purpose:** Reads the four Excel files you uploaded. Returns a unified Python list of dicts like `{"name": "IIT Bombay", "url": "https://www.iitb.ac.in", "type": "IIT", "city": "Mumbai", "state": "Maharashtra"}`. This list becomes the input to the crawlers.

**When it runs:** At the very start of the pipeline, before any crawling.

**Input:** 
- `IIT_Colleges_List.xlsx` (24 IITs)
- `NIT_BITS_Colleges_List.xlsx` (31 NITs + 5 BITS)
- `BITS_Colleges_List.xlsx` (6 BITS campuses)

**Output:** Python list of ~60 institute dicts

**Dependencies:** `pandas`, `openpyxl`

**Common errors:**
- `FileNotFoundError` → Excel files must be placed in `data/` folder
- Sheet name mismatch → The code expects `"IIT Colleges"` as sheet name; verify with `pd.read_excel(..., sheet_name=None).keys()`

**Test it:**
```python
python data/seed_reader.py
```
You should see 5 institute dicts printed. If you see 0, the Excel path is wrong.

---

### `crawler/scrapy_spiders/faculty_spider.py`

**Purpose:** The main Scrapy spider. Starts at a college homepage, finds department links (by matching keywords like "CSE", "Mechanical"), then finds faculty listing pages, then finds individual profile URLs, then downloads and saves the raw HTML of each profile page. Also outputs a JSONL manifest file with the path to each saved HTML file.

**When it runs:** Phase 2 of the pipeline, once per institute.

**Input:** `INSTITUTE_URL`, `INSTITUTE_NAME`, `INSTITUTE_TYPE` (passed as Scrapy settings)

**Output:**
- Raw HTML files saved to `data/raw/<TYPE>/<InstituteName>/`
- JSONL manifest at `data/raw/scraped_faculty_spider.jsonl`

**Dependencies:** `scrapy`, `configs.settings`

**Common errors:**
- `scrapy: command not found` → Activate virtualenv first
- `Spider not found: faculty_spider` → Missing `scrapy.cfg` or `__init__.py`
- `ROBOTSTXT_OBEY=True` blocks crawl → Some colleges block bots; set to `False` carefully
- Empty output → Department keyword didn't match any link text on that site; inspect the homepage HTML manually

---

### `crawler/scrapy_spiders/run_all_crawls.py`

**Purpose:** Runs the Scrapy spider for all 60+ institutes one by one. Saves a checkpoint file so if it crashes at institute #30, next run it skips the first 29.

**When it runs:** After seed reader, to batch-crawl everything.

**Input:** Institute list from `seed_reader.py`

**Output:** Checkpoint file at `logs/scrapy_checkpoint.json`, plus all the raw HTML from the spider.

**Common errors:**
- `subprocess.TimeoutExpired` → Some college sites are slow; increase timeout from 600 to 1200
- Spider fails for 1 institute → Normal; it's logged and skipped; rest continue

---

### `crawler/playwright_crawler/pw_crawler.py`

**Purpose:** Uses a real browser (Chromium) to crawl sites where faculty pages are loaded by JavaScript. Many newer IIT/NIT portals use React or Angular — Scrapy can't see their content because it only downloads HTML, not runs JavaScript. Playwright actually opens a browser, waits for JS to render, then extracts the content.

**When it runs:** After Scrapy, for sites where Scrapy got 0 results.

**Input:** `--url`, `--institute`, `--type` command-line arguments

**Output:** Raw HTML files in `data/raw/`, JSONL file in `data/processed/`

**Dependencies:** `playwright` (and you must run `playwright install chromium` once)

**Common errors:**
- `playwright._impl._errors.TimeoutError` → Page took too long; site may be down
- `Error: browserType.launch: Executable doesn't exist` → Run `python -m playwright install chromium`

---

### `parser/faculty_parser.py`

**Purpose:** Takes a raw HTML file (saved by the crawler) and extracts structured data from it. Uses BeautifulSoup to parse the HTML, then applies regex patterns and section-heading detection to find: name, designation, email, phone, research interests, publications, education, Google Scholar link, etc.

**When it runs:** Phase 3, after crawling is complete.

**Input:** A dict with `raw_html_path`, `profile_url`, `institute_name`, etc. (from the JSONL manifest)

**Output:** A `FacultyProfile` dataclass / dict like:
```json
{
  "faculty_name": "Dr. Ravi Kumar",
  "designation": "Associate Professor",
  "department": "Computer Science & Engineering",
  "email": "ravi@iitb.ac.in",
  "research_interests": ["Machine Learning", "NLP"],
  "publications": ["Deep Learning for...", "Attention is All..."],
  ...
}
```

**Dependencies:** `beautifulsoup4`, `lxml`

**Common errors:**
- `faculty_name` is empty for many profiles → The HTML structure of that college is unusual; you may need to add a site-specific selector
- Email not extracted → Some colleges obfuscate emails with JavaScript; Playwright would be needed
- Publications list is empty → The section heading on that site doesn't match any expected keyword; add it to the list in `_extract_publications`

---

### `database/schema.sql`

**Purpose:** Creates all 7 PostgreSQL tables: `institutes`, `departments`, `faculty`, `research_interests`, `publications`, `education`, `projects`, plus a `crawl_log` table. Also creates indexes for fast search and a trigger to auto-update `updated_at`.

**When it runs:** Once, at project setup.

**Input:** Your PostgreSQL database (must already exist)

**Output:** All tables created in the database

**Run it:**
```bash
psql -U postgres -d faculty_search -f database/schema.sql
```

**Common errors:**
- `role "postgres" does not exist` → Create the role: `createuser -s postgres`
- `database "faculty_search" does not exist` → `createdb faculty_search`
- `extension "pg_trgm" does not exist` → `CREATE EXTENSION pg_trgm;` manually

---

### `database/db_writer.py`

**Purpose:** Python code that connects to PostgreSQL and saves parsed faculty data. Uses UPSERT (`ON CONFLICT DO UPDATE`) so running the pipeline twice doesn't create duplicates. Handles: institutes, departments, faculty, research interests, publications, education, projects.

**When it runs:** Phase 4, after parsing.

**Input:** A parsed `FacultyProfile` dict + institute metadata

**Output:** Rows inserted/updated in PostgreSQL

**Dependencies:** `psycopg2-binary`, `configs.settings`

**Common errors:**
- `psycopg2.OperationalError: could not connect to server` → PostgreSQL is not running; `sudo service postgresql start`
- `UniqueViolation` → Should not happen because we use UPSERT; if it does, a constraint is missing
- `faculty_name` is null → Parser returned empty name; that profile is skipped (correct behaviour)

---

### `embeddings/embed_pipeline.py`

**Purpose:** Reads faculty records from PostgreSQL that don't have embeddings yet, generates a 384-dimensional embedding vector for each using `sentence-transformers/all-MiniLM-L6-v2`, saves the embedding matrix to disk as a `.npy` file, and also writes each vector back to the `faculty.embedding_vector` column in PostgreSQL.

**Important:** Only these fields are embedded: research interests, research areas, biography, projects, publications. Name, email, phone are deliberately excluded (they are not semantic).

**When it runs:** Phase 5, after all faculty data is in PostgreSQL.

**Input:** PostgreSQL `faculty` table rows with no embedding

**Output:**
- `data/processed/faculty_embeddings.npy` — numpy matrix of shape `(N, 384)`
- `data/processed/faculty_metadata.json` — list of `{faculty_id, faculty_name, department, institute, profile_url}`

**Dependencies:** `sentence-transformers`, `numpy`, `psycopg2`

**First run:** The model (~90 MB) downloads automatically from HuggingFace. Needs internet.

**Common errors:**
- `No module named 'sentence_transformers'` → `pip install sentence-transformers`
- Very slow → Normal on CPU; 7,000 profiles take ~20–40 minutes on CPU, ~3 minutes on GPU
- `faculty_embeddings.npy not found` after running → Check logs for DB connection errors

---

### `vector_store/faiss_index.py`

**Purpose:** Loads the `.npy` embedding matrix from disk, builds a FAISS HNSW index, saves it to `vector_store/faculty.index`, and provides a `search_by_text()` function that takes a plain-English query, embeds it, and returns the top-K most semantically similar faculty profiles.

**When it runs:** Phase 6, after embeddings are generated.

**Input:** `data/processed/faculty_embeddings.npy` + metadata JSON

**Output:** `vector_store/faculty.index` (FAISS binary file)

**Why HNSW for this project:**
- You have 3,000–7,000 profiles
- HNSW needs no training step (unlike IVF)
- Query time is < 5ms even on CPU
- Recall@10 is typically > 95%

**Dependencies:** `faiss-cpu`, `numpy`

**Common errors:**
- `import faiss` fails → `pip install faiss-cpu` (not `faiss`)
- Index file is very large → HNSW stores the graph; for 7,000 × 384-dim it is ~40 MB, normal
- Search returns wrong results → Verify embeddings were L2-normalised (sentence-transformers does this by default with `normalize_embeddings=True`)

---

### `api/main.py`

**Purpose:** FastAPI REST server with 3 endpoints:
- `GET /search?q=machine+learning&top_k=10` — semantic search
- `GET /faculty/{id}` — full profile detail
- `GET /institutes?type=IIT` — list institutes

**When it runs:** Last phase, after FAISS index is ready.

**How to start:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open `http://localhost:8000/docs` for interactive Swagger UI.

**Dependencies:** `fastapi`, `uvicorn`, FAISS index must exist

---

### `pipeline.py`

**Purpose:** Master orchestrator. Runs all phases in order with one command.

**Common usage:**
```bash
python pipeline.py --phase all --crawler scrapy
python pipeline.py --phase embed        # re-run just embeddings
python pipeline.py --phase faiss        # re-build just FAISS index
```

---

## PART 4 — STEP-BY-STEP IMPLEMENTATION FROM SCRATCH

### Step 0 — Prerequisites (do this first, once)

Make sure these are installed on your machine:
```bash
# Check Python version (need 3.10 or higher)
python3 --version

# Check PostgreSQL
psql --version

# If PostgreSQL not installed (Ubuntu/Debian):
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

---

### Step 1 — Project Setup

**1a. Clone or create the project folder**
```bash
mkdir faculty-search-system
cd faculty-search-system
```

**1b. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

You should see `(venv)` at the start of your terminal prompt. This means you are inside the virtual environment.

**1c. Create requirements.txt** (copy from Part 2.1 above) then install:
```bash
pip install -r requirements.txt
```
This takes 5–10 minutes. You'll see packages downloading.

**1d. Install Playwright browsers**
```bash
python -m playwright install chromium
```

**1e. Create the folder structure**
```bash
mkdir -p data/{raw,processed} crawler/{scrapy_spiders,playwright_crawler} \
         parser database embeddings vector_store api logs configs tests docs
```

**1f. Create all `__init__.py` files**
```bash
touch configs/__init__.py data/__init__.py crawler/__init__.py \
      crawler/scrapy_spiders/__init__.py crawler/playwright_crawler/__init__.py \
      parser/__init__.py database/__init__.py embeddings/__init__.py \
      vector_store/__init__.py api/__init__.py
```

**1g. Create `.env` file**
```bash
cat > .env << 'EOF'
PGHOST=localhost
PGPORT=5432
PGDATABASE=faculty_search
PGUSER=postgres
PGPASSWORD=your_password_here
EOF
```

**1h. Add dotenv loading to the top of `configs/settings.py`**
Add this at the very top of `settings.py`, before any other code:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

### Step 2 — Database Setup

**2a. Create the PostgreSQL database**
```bash
sudo -u postgres psql -c "CREATE DATABASE faculty_search;"
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE faculty_search TO myuser;"
```

Update your `.env` with `myuser` and `mypassword`.

**2b. Install the PostgreSQL extensions**
```bash
sudo -u postgres psql -d faculty_search -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
sudo -u postgres psql -d faculty_search -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

**2c. Apply the schema**
```bash
psql -U myuser -d faculty_search -f database/schema.sql
```

**Expected output:**
```
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE FUNCTION
DO
```

**Verify tables were created:**
```bash
psql -U myuser -d faculty_search -c "\dt"
```
You should see 8 tables listed.

---

### Step 3 — Copy Your Excel Files

Copy your four Excel files into the `data/` folder:
```bash
cp /path/to/IIT_Colleges_List.xlsx       data/
cp /path/to/NIT_BITS_Colleges_List.xlsx  data/
cp /path/to/BITS_Colleges_List.xlsx      data/
cp /path/to/College_Department_Tracker.xlsx data/
```

**Test the seed reader:**
```bash
python data/seed_reader.py
```

**Expected output:**
```
INFO - Loaded 24 IITs from IIT_Colleges_List.xlsx
INFO - Loaded 36 institutes from NIT_BITS_Colleges_List.xlsx
INFO - Loaded 6 BITS campuses from BITS_Colleges_List.xlsx
INFO - Total unique institutes: 60
{'name': 'IIT Kharagpur', 'url': 'https://www.iitkgp.ac.in', 'type': 'IIT', ...}
...
```

If you see 0 institutes, the Excel file path or sheet name is wrong.

---

### Step 4 — Create `scrapy.cfg`

Create this file in the **root of your project** (same level as `pipeline.py`):
```ini
[settings]
default = crawler.scrapy_spiders.settings_scrapy

[deploy]
project = faculty_search
```

Also create `crawler/scrapy_spiders/settings_scrapy.py`:
```python
# Scrapy project settings
BOT_NAME = "faculty_search"
SPIDER_MODULES = ["crawler.scrapy_spiders"]
NEWSPIDER_MODULE = "crawler.scrapy_spiders"
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.5
HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = "data/raw/scrapy_cache"
LOG_LEVEL = "INFO"
```

---

### Step 5 — Run Scrapy on a Single Institute First (Test Run)

Never run on all 60 institutes without testing one first.

```bash
cd faculty-search-system
scrapy crawl faculty_spider \
  -s INSTITUTE_URL=https://www.iitb.ac.in \
  -s INSTITUTE_NAME="IIT Bombay" \
  -s INSTITUTE_TYPE=IIT \
  -s LOG_LEVEL=INFO
```

**What you should see:**
- Scrapy logs showing URLs being visited
- Files appearing in `data/raw/IIT/IIT_Bombay/` (HTML files)
- A JSONL file at `data/raw/scraped_faculty_spider.jsonl`

**If you see 0 items scraped:**
1. Open the college homepage manually in a browser
2. Look at the menu — what does the "Academics" or "Faculty" link say?
3. The spider uses keyword matching; if the link says "People" or "Our Team" it won't catch it
4. Add those keywords to `FACULTY_PAGE_PATTERNS` in `faculty_spider.py`

---

### Step 6 — Run the Parser on Collected HTML

```bash
python -c "
import json
from parser.faculty_parser import parse_from_file

with open('data/raw/scraped_faculty_spider.jsonl') as f:
    for line in f:
        meta = json.loads(line.strip())
        result = parse_from_file(meta)
        if result:
            print(json.dumps(result, indent=2))
            break  # just show first result
"
```

**Expected output:**
```json
{
  "faculty_name": "Prof. Abhay Karandikar",
  "designation": "Professor",
  "department": "Computer Science & Engineering",
  "email": "ak@ee.iitb.ac.in",
  "research_interests": ["Wireless Communication", "5G Networks"],
  "publications": ["Capacity Analysis of...", "MIMO Systems..."],
  ...
}
```

If `faculty_name` is empty for many profiles, that site uses a non-standard HTML structure. You will need to add a site-specific selector to the parser.

---

### Step 7 — Store in PostgreSQL

```bash
python -c "
import json
from parser.faculty_parser import parse_from_file
from database.db_writer import save_faculty_profile

with open('data/raw/scraped_faculty_spider.jsonl') as f:
    for line in f:
        meta = json.loads(line.strip())
        profile = parse_from_file(meta)
        if profile:
            save_faculty_profile(
                profile,
                institute_url='https://www.iitb.ac.in',
                institute_type='IIT',
                city='Mumbai',
                state='Maharashtra'
            )
print('Done inserting')
"
```

**Verify in PostgreSQL:**
```bash
psql -U myuser -d faculty_search -c "SELECT faculty_name, designation, email FROM faculty LIMIT 10;"
```

---

### Step 8 — Run All Institutes with Scrapy Batch Runner

Once the single-institute test works:
```bash
python -m crawler.scrapy_spiders.run_all_crawls
```

This runs Scrapy for all 60+ institutes. It will take several hours. The checkpoint file means you can stop and resume.

---

### Step 9 — Generate Embeddings

After enough faculty data is in PostgreSQL (at least 100 records for a meaningful test):
```bash
python -m embeddings.embed_pipeline
```

**Expected output:**
```
INFO - Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
INFO - Embedding 1250 faculty records
INFO - Batch 0–64 / 1250
...
INFO - Saved 1180 embeddings → data/processed/faculty_embeddings.npy
Embedding matrix: (1180, 384)
```

---

### Step 10 — Build FAISS Index

```bash
python -m vector_store.faiss_index
```

**Expected output:**
```
INFO - Built IndexHNSWFlat (M=32) with 1180 vectors
INFO - FAISS index saved → vector_store/faculty.index (1180 vectors)
Index ready: 1180 vectors, type=HNSW
```

---

### Step 11 — Test Semantic Search

```bash
python -c "
from vector_store.faiss_index import load_index, search_by_text

index, metadata = load_index()
results = search_by_text('deep learning for natural language processing', index, metadata, top_k=5)
for r in results:
    print(r)
"
```

**Expected output:**
```
{'faculty_id': 'abc...', 'faculty_name': 'Dr. Preethi Jyothi', 'department': 'Computer Science & Engineering', 'institute': 'IIT Bombay', 'profile_url': '...', 'score': 0.89}
...
```

---

### Step 12 — Start the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open in browser: `http://localhost:8000/docs`

Test search: `http://localhost:8000/search?q=computer+vision&top_k=5`

---

## PART 5 — COMPLETE EXECUTION FLOW

```
Excel Files (IIT/NIT/BITS .xlsx)
           │
           ▼
   data/seed_reader.py
   → list of 60 institutes with URLs
           │
           ▼
   ┌───────────────────────────────┐
   │        PHASE 2: CRAWL        │
   │                               │
   │  Scrapy Spider                │
   │  (static sites, fast)         │
   │            +                  │
   │  Playwright Crawler           │
   │  (JS-rendered sites)          │
   └───────────┬───────────────────┘
               │
               ▼
   data/raw/<TYPE>/<College>/*.html    ← raw HTML files
   data/raw/scraped_faculty_spider.jsonl  ← manifest
           │
           ▼
   parser/faculty_parser.py
   parse_from_file(meta) → FacultyProfile dict
           │
           ▼
   database/db_writer.py
   save_faculty_profile() → PostgreSQL
   ┌──────────────────────────────────────┐
   │  institutes  departments  faculty    │
   │  research_interests  publications   │
   │  education  projects                │
   └──────────────────────────────────────┘
           │
           ▼
   embeddings/embed_pipeline.py
   → data/processed/faculty_embeddings.npy  (N × 384)
   → data/processed/faculty_metadata.json
           │
           ▼
   vector_store/faiss_index.py
   → vector_store/faculty.index  (HNSW graph)
           │
           ▼
   api/main.py  (FastAPI)
   GET /search?q=...
           │
           ▼
   Semantic Search Results
   (faculty profiles ranked by relevance)
```

---

## PART 6 — TESTING PLAN

### Module 1: Seed Reader

```bash
python data/seed_reader.py
```
✅ Pass: Prints 50+ institute dicts with valid URLs  
❌ Fail: 0 results → Check Excel file path and sheet name

---

### Module 2: Database

```bash
psql -U myuser -d faculty_search -c "\dt"
```
✅ Pass: Shows 8 tables  
❌ Fail: `ERROR: extension not found` → Run `CREATE EXTENSION pgcrypto;` manually

---

### Module 3: Scrapy Spider

```bash
scrapy crawl faculty_spider \
  -s INSTITUTE_URL=https://www.iitkgp.ac.in \
  -s INSTITUTE_NAME="IIT Kharagpur" \
  -s INSTITUTE_TYPE=IIT
```
✅ Pass: HTML files appear in `data/raw/IIT/IIT_Kharagpur/`  
❌ Fail (0 files): `ROBOTSTXT_OBEY` blocked it, or department link keywords don't match

**Debug:** Add `-s LOG_LEVEL=DEBUG` to see every URL being visited

---

### Module 4: Parser

```python
from parser.faculty_parser import parse_profile

html = open("data/raw/IIT/IIT_Bombay/<some_hash>.html").read()
result = parse_profile(html, "https://www.iitb.ac.in/faculty/xyz")
print(result.faculty_name)     # Should print a name
print(result.email)            # Should print an email or ""
print(result.research_interests)  # Should print a list
```
✅ Pass: `faculty_name` is a real person's name  
❌ Fail: Name is empty → That page's HTML uses an unusual structure; inspect it and add a CSS selector

---

### Module 5: DB Writer

```bash
psql -U myuser -d faculty_search -c "SELECT COUNT(*) FROM faculty;"
```
✅ Pass: Count increases after running the parse+store phase  
❌ Fail: Count stays 0 → Check logs for psycopg2 errors

---

### Module 6: Embeddings

```python
import numpy as np
m = np.load("data/processed/faculty_embeddings.npy")
print(m.shape)   # Should be (N, 384) where N > 0
print(m[0])      # Should be a float32 array of 384 numbers
```
✅ Pass: Shape is `(N, 384)` with N > 0  
❌ Fail: File doesn't exist → Run `python -m embeddings.embed_pipeline`

---

### Module 7: FAISS

```python
from vector_store.faiss_index import load_index, search_by_text
index, meta = load_index()
results = search_by_text("machine learning", index, meta, top_k=3)
print(results)
```
✅ Pass: Returns 3 dicts with `faculty_name`, `institute`, `score`  
❌ Fail: `FileNotFoundError` → Run `python -m vector_store.faiss_index` first

---

### Module 8: API

```bash
uvicorn api.main:app --port 8000 &
curl "http://localhost:8000/health"
curl "http://localhost:8000/search?q=robotics&top_k=3"
```
✅ Pass: `/health` returns `{"status": "ok"}`, `/search` returns a list  
❌ Fail: 503 on /search → FAISS index not loaded; run embed + faiss phases first

---

## PART 7 — COMMON BEGINNER MISTAKES

### Mistake 1: Running Python files from the wrong directory

Always run from the **project root**:
```bash
cd /path/to/faculty-search-system    # ← must be here
python data/seed_reader.py           # ✅
```
Not from inside a subfolder, or imports will fail.

### Mistake 2: Not activating virtual environment

Every time you open a new terminal:
```bash
source venv/bin/activate    # Linux/Mac
```
If you don't do this, you'll get `ModuleNotFoundError` even for installed packages.

### Mistake 3: Crawling too aggressively

`DOWNLOAD_DELAY = 1.5` means wait 1.5 seconds between requests. Don't lower this. IIT/NIT servers are government infrastructure; sending too many requests can get your IP blocked.

### Mistake 4: Expecting 100% parser accuracy

No HTML parser gets every field correct on every site. Target: get name + email + research interests for 70%+ of profiles. That's a good result. Some profiles will have empty fields — that's acceptable.

### Mistake 5: Running embeddings before sufficient data

Embeddings on 5 profiles look identical to embeddings on 50 profiles in terms of the code working, but semantic search won't be meaningful with fewer than ~200 profiles. Crawl at least 5–10 colleges before embedding.

---

## PART 8 — RECOMMENDED IMPLEMENTATION ORDER

Week 1 (MVP):
1. Setup + virtualenv + dependencies
2. PostgreSQL + schema
3. Seed reader test
4. Scrapy on 2–3 colleges (IIT Bombay, IIT Madras, NIT Trichy)
5. Parser test on collected HTML
6. Store in PostgreSQL
7. Verify with `SELECT * FROM faculty LIMIT 10;`

Week 2 (Scale):
8. Run Scrapy batch on all 60 institutes
9. Add Playwright for sites where Scrapy got 0 results
10. Improve parser for sites with unusual structure

Week 3 (Semantic Search):
11. Generate embeddings
12. Build FAISS index
13. Test semantic search
14. Start FastAPI

Week 4 (Polish):
15. Add tests
16. Add Docker
17. Build a simple frontend (React or Streamlit)
