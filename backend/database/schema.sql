-- ============================================================
-- Faculty Search System — PostgreSQL Schema
-- Production-grade with UPSERT, indexing, and FK constraints
-- ============================================================

-- ── Extensions ────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- trigram similarity for text search

-- ── 1. Institutes ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS institutes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    short_name      TEXT,
    type            TEXT NOT NULL CHECK (type IN ('IIT', 'NIT', 'BITS', 'Other')),
    city            TEXT,
    state           TEXT,
    website_url     TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_institutes_website UNIQUE (website_url)
);

CREATE INDEX IF NOT EXISTS idx_institutes_type   ON institutes (type);
CREATE INDEX IF NOT EXISTS idx_institutes_name   ON institutes USING gin (name gin_trgm_ops);

-- ── 2. Departments ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institute_id    UUID NOT NULL REFERENCES institutes (id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    canonical_name  TEXT NOT NULL,           -- normalised e.g. "Computer Science & Engineering"
    dept_url        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_departments_inst_name UNIQUE (institute_id, canonical_name)
);

CREATE INDEX IF NOT EXISTS idx_departments_institute ON departments (institute_id);
CREATE INDEX IF NOT EXISTS idx_departments_canonical ON departments (canonical_name);

-- ── 3. Faculty ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faculty (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institute_id        UUID NOT NULL REFERENCES institutes (id) ON DELETE CASCADE,
    department_id       UUID REFERENCES departments (id) ON DELETE SET NULL,
    faculty_name        TEXT NOT NULL,
    designation         TEXT,
    email               TEXT,
    phone               TEXT,
    office              TEXT,
    biography           TEXT,
    google_scholar      TEXT,
    linkedin            TEXT,
    personal_website    TEXT,
    profile_image       TEXT,
    profile_url         TEXT NOT NULL,
    raw_html_path       TEXT,
    embedding_vector    TEXT,               -- JSON array stored as text; replace with pgvector if available
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_faculty_profile_url UNIQUE (profile_url)
);

CREATE INDEX IF NOT EXISTS idx_faculty_institute    ON faculty (institute_id);
CREATE INDEX IF NOT EXISTS idx_faculty_department   ON faculty (department_id);
CREATE INDEX IF NOT EXISTS idx_faculty_name         ON faculty USING gin (faculty_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_faculty_designation  ON faculty (designation);
CREATE INDEX IF NOT EXISTS idx_faculty_email        ON faculty (email);

-- ── 4. Research Interests ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS research_interests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id      UUID NOT NULL REFERENCES faculty (id) ON DELETE CASCADE,
    interest_text   TEXT NOT NULL,
    source          TEXT CHECK (source IN ('research_interests', 'research_areas')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_research_faculty_text UNIQUE (faculty_id, interest_text)
);

CREATE INDEX IF NOT EXISTS idx_research_faculty      ON research_interests (faculty_id);
CREATE INDEX IF NOT EXISTS idx_research_text_trgm    ON research_interests USING gin (interest_text gin_trgm_ops);

-- ── 5. Publications ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS publications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id      UUID NOT NULL REFERENCES faculty (id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    authors         TEXT,
    venue           TEXT,
    year            SMALLINT,
    doi             TEXT,
    url             TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_publications_faculty_title UNIQUE (faculty_id, title)
);

CREATE INDEX IF NOT EXISTS idx_publications_faculty ON publications (faculty_id);
CREATE INDEX IF NOT EXISTS idx_publications_year    ON publications (year);
CREATE INDEX IF NOT EXISTS idx_publications_title   ON publications USING gin (title gin_trgm_ops);

-- ── 6. Education ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS education (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id      UUID NOT NULL REFERENCES faculty (id) ON DELETE CASCADE,
    degree          TEXT,
    institution     TEXT,
    year            SMALLINT,
    raw_text        TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_education_faculty ON education (faculty_id);

-- ── 7. Projects ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id      UUID NOT NULL REFERENCES faculty (id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    description     TEXT,
    funding_agency  TEXT,
    year            SMALLINT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_faculty ON projects (faculty_id);

-- ── 8. Crawl Log ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS crawl_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institute_id    UUID REFERENCES institutes (id) ON DELETE SET NULL,
    url             TEXT NOT NULL,
    crawl_source    TEXT CHECK (crawl_source IN ('scrapy', 'playwright')),
    status          TEXT CHECK (status IN ('success', 'failed', 'skipped')),
    error_message   TEXT,
    crawled_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawl_log_institute ON crawl_log (institute_id);
CREATE INDEX IF NOT EXISTS idx_crawl_log_status    ON crawl_log (status);

-- ── Trigger: auto-update updated_at ──────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['institutes','departments','faculty'] LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at BEFORE UPDATE ON %s '
            'FOR EACH ROW EXECUTE FUNCTION update_updated_at()', t, t
        );
    END LOOP;
END$$;
