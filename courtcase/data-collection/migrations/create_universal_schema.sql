-- ============================================================================
-- UNIVERSAL LEGAL DOCUMENT MANAGEMENT SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Version: 2.0
-- Created: 2025-10-22
-- Description: Universal schema for multi-country legal document management
--              with standardized naming conventions and folder structures
-- ============================================================================

-- ============================================================================
-- MAIN TABLE: Universal Legal Documents
-- ============================================================================

CREATE TABLE IF NOT EXISTS universal_legal_documents (
    -- ========================================================================
    -- PRIMARY IDENTIFICATION
    -- ========================================================================
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    global_id TEXT UNIQUE NOT NULL,              -- Sequential global ID: ULEGAL-0000000001
    uuid TEXT UNIQUE NOT NULL,                   -- UUID v4 for distributed systems

    -- ========================================================================
    -- COUNTRY & JURISDICTION
    -- ========================================================================
    country_code TEXT NOT NULL,                  -- ISO 3166-1 Alpha-2: IN, BD, PK, etc.
    country_name TEXT NOT NULL,                  -- Full name: India, Bangladesh, etc.
    jurisdiction_level TEXT,                     -- CENTRAL, STATE, PROVINCIAL, etc.
    jurisdiction_name TEXT,                      -- Specific state/province if applicable

    -- ========================================================================
    -- DOCUMENT CLASSIFICATION
    -- ========================================================================
    doc_category TEXT NOT NULL,                  -- CASE, ACT, RULE, ORDER, etc.
    doc_type TEXT,                               -- Specific type: Civil, Criminal, etc.
    doc_subcategory TEXT,                        -- Further classification

    -- ========================================================================
    -- STANDARDIZED IDENTIFICATION
    -- ========================================================================
    doc_number TEXT,                             -- Official number: XLV, 045, etc.
    doc_year INTEGER,                            -- Year: 1860, 2023, etc.
    yearly_sequence INTEGER,                     -- Sequential number within year
    country_doc_id TEXT,                         -- Country-specific ID

    -- ========================================================================
    -- TITLE & NAMING
    -- ========================================================================
    title_full TEXT NOT NULL,                    -- Complete official title
    title_short TEXT,                            -- Short/popular title
    title_alternate TEXT,                        -- Alternate names/translations

    -- ========================================================================
    -- SUBJECT CLASSIFICATION (Multi-level Taxonomy)
    -- ========================================================================
    subject_primary TEXT,                        -- Primary: CRIMINAL, CIVIL, CONSTITUTIONAL
    subject_secondary TEXT,                      -- Secondary: PROPERTY, CONTRACT, TORT
    subject_code TEXT,                           -- 3-letter code: CRM, CIV, CON
    subject_tags TEXT,                           -- JSON array of tags

    -- ========================================================================
    -- COURT/AUTHORITY INFORMATION (for CASE docs)
    -- ========================================================================
    court_level TEXT,                            -- SUPREME, HIGH, DISTRICT, etc.
    court_name TEXT,                             -- Full court name
    court_code TEXT,                             -- Abbreviation: SC, HC, etc.
    bench_type TEXT,                             -- CONSTITUTIONAL, DIVISION, etc.
    bench_size INTEGER,                          -- Number of judges
    judges TEXT,                                 -- JSON array of judge names

    -- ========================================================================
    -- MINISTRY/AUTHORITY (for ACT/RULE docs)
    -- ========================================================================
    issuing_authority TEXT,                      -- Ministry, Department, etc.
    authority_code TEXT,                         -- Abbreviation

    -- ========================================================================
    -- CITATIONS & REFERENCES
    -- ========================================================================
    citation_primary TEXT,                       -- Main citation
    citation_alternate TEXT,                     -- Alternative citations (JSON array)
    citation_neutral TEXT,                       -- Neutral citation if available

    -- ========================================================================
    -- LEGAL STATUS & DATES
    -- ========================================================================
    legal_status TEXT DEFAULT 'ACTIVE',          -- ACTIVE, REPEALED, AMENDED, SUPERSEDED
    date_enacted DATE,                           -- When passed/decided
    date_effective DATE,                         -- When came into force
    date_published DATE,                         -- Official publication date
    date_last_amended DATE,                      -- Last amendment
    date_repealed DATE,                          -- If repealed

    -- ========================================================================
    -- CONTENT
    -- ========================================================================
    html_content TEXT,                           -- Full HTML
    plain_text TEXT,                             -- Extracted text
    summary TEXT,                                -- Brief summary
    headnotes TEXT,                              -- Case headnotes
    preamble TEXT,                               -- Act preamble
    key_provisions TEXT,                         -- Important sections (JSON)

    -- ========================================================================
    -- FILE MANAGEMENT (Universal Naming Convention)
    -- ========================================================================
    filename_universal TEXT UNIQUE,              -- Standardized filename
    file_path_relative TEXT,                     -- Relative path from Legal_Database/
    file_path_absolute TEXT,                     -- Absolute path
    folder_category TEXT,                        -- CASE, ACT, RULE, etc.
    folder_subcategory TEXT,                     -- Subfolder classification

    -- ========================================================================
    -- PDF INFORMATION
    -- ========================================================================
    pdf_url TEXT,                                -- Source PDF URL
    pdf_filename TEXT,                           -- PDF filename (same as universal)
    pdf_path TEXT,                               -- PDF file path
    pdf_downloaded BOOLEAN DEFAULT 0,
    pdf_size_bytes INTEGER,
    pdf_pages INTEGER,
    pdf_hash_sha256 TEXT,                        -- For deduplication
    pdf_ocr_done BOOLEAN DEFAULT 0,

    -- ========================================================================
    -- SOURCE INFORMATION
    -- ========================================================================
    source_url TEXT NOT NULL,                    -- Original URL
    source_domain TEXT NOT NULL,                 -- Domain name
    source_database TEXT,                        -- Source DB name
    source_index TEXT,                           -- Which index/category
    source_last_checked DATE,                    -- Last verification

    -- ========================================================================
    -- RELATIONSHIPS
    -- ========================================================================
    parent_doc_id INTEGER,                       -- Parent document (amendments)
    supersedes_doc_id INTEGER,                   -- Doc this supersedes
    amended_by TEXT,                             -- JSON array of amending docs
    cited_by_count INTEGER DEFAULT 0,            -- Number of citations
    cites_count INTEGER DEFAULT 0,               -- Number of docs this cites

    -- ========================================================================
    -- METADATA & VERSIONING
    -- ========================================================================
    version INTEGER DEFAULT 1,                   -- Document version
    checksum TEXT,                               -- Content checksum
    language TEXT DEFAULT 'en',                  -- ISO 639-1 code
    encoding TEXT DEFAULT 'UTF-8',

    -- ========================================================================
    -- SCRAPING METADATA
    -- ========================================================================
    scraper_name TEXT,                           -- Which scraper
    scraper_version TEXT,                        -- Scraper version
    scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scrape_status TEXT DEFAULT 'COMPLETE',       -- PENDING, COMPLETE, ERROR, PARTIAL
    scrape_error TEXT,                           -- Error message if any
    scrape_duration_ms INTEGER,                  -- Time taken

    -- ========================================================================
    -- QUALITY & VALIDATION
    -- ========================================================================
    data_quality_score REAL,                     -- 0-100 quality score
    validation_status TEXT,                      -- VALIDATED, PENDING, FAILED
    validation_errors TEXT,                      -- JSON array of issues
    manual_review_needed BOOLEAN DEFAULT 0,

    -- ========================================================================
    -- TIMESTAMPS
    -- ========================================================================
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,

    -- ========================================================================
    -- CONSTRAINTS
    -- ========================================================================
    UNIQUE(country_code, source_url),
    FOREIGN KEY (parent_doc_id) REFERENCES universal_legal_documents(id) ON DELETE SET NULL,
    FOREIGN KEY (supersedes_doc_id) REFERENCES universal_legal_documents(id) ON DELETE SET NULL
);

-- ============================================================================
-- SEQUENCE TRACKER - For generating sequential IDs
-- ============================================================================

CREATE TABLE IF NOT EXISTS sequence_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequence_type TEXT NOT NULL,                 -- GLOBAL, YEARLY, COUNTRY
    country_code TEXT,                           -- NULL for global
    doc_category TEXT,                           -- CASE, ACT, RULE, etc.
    year INTEGER,                                -- NULL for global
    last_value INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sequence_type, country_code, doc_category, year)
);

-- Initialize global sequence
INSERT OR IGNORE INTO sequence_tracker (sequence_type, last_value)
VALUES ('GLOBAL', 0);

-- ============================================================================
-- CITATIONS TABLE - Track document citations
-- ============================================================================

CREATE TABLE IF NOT EXISTS citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citing_doc_id INTEGER NOT NULL,             -- Document making the citation
    cited_doc_id INTEGER,                        -- Document being cited (NULL if external)
    citation_text TEXT NOT NULL,                 -- How it's cited
    citation_context TEXT,                       -- Surrounding text
    citation_type TEXT,                          -- PRECEDENT, REFERENCE, SUPERSEDED
    citation_strength TEXT,                      -- FOLLOWED, DISTINGUISHED, OVERRULED
    page_number INTEGER,                         -- Where citation appears
    section_number TEXT,                         -- Section reference

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (citing_doc_id) REFERENCES universal_legal_documents(id) ON DELETE CASCADE,
    FOREIGN KEY (cited_doc_id) REFERENCES universal_legal_documents(id) ON DELETE SET NULL
);

-- ============================================================================
-- DOCUMENT AMENDMENTS - Track amendment history
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_amendments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_doc_id INTEGER NOT NULL,               -- Original document
    amending_doc_id INTEGER NOT NULL,            -- Amendment document
    amendment_type TEXT,                         -- SECTION_INSERT, SECTION_DELETE, MODIFY
    amendment_date DATE,
    sections_affected TEXT,                      -- JSON array
    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (base_doc_id) REFERENCES universal_legal_documents(id) ON DELETE CASCADE,
    FOREIGN KEY (amending_doc_id) REFERENCES universal_legal_documents(id) ON DELETE CASCADE
);

-- ============================================================================
-- FLEXIBLE METADATA - Country-specific fields
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    metadata_type TEXT DEFAULT 'text',          -- text, number, date, json, boolean

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (document_id) REFERENCES universal_legal_documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, metadata_key)
);

-- ============================================================================
-- INDEXES - Optimized for common queries
-- ============================================================================

-- Primary lookups
CREATE INDEX IF NOT EXISTS idx_global_id ON universal_legal_documents(global_id);
CREATE INDEX IF NOT EXISTS idx_uuid ON universal_legal_documents(uuid);
CREATE INDEX IF NOT EXISTS idx_filename ON universal_legal_documents(filename_universal);

-- Country & jurisdiction
CREATE INDEX IF NOT EXISTS idx_country ON universal_legal_documents(country_code);
CREATE INDEX IF NOT EXISTS idx_country_category ON universal_legal_documents(country_code, doc_category);
CREATE INDEX IF NOT EXISTS idx_country_year ON universal_legal_documents(country_code, doc_year);

-- Classification
CREATE INDEX IF NOT EXISTS idx_category ON universal_legal_documents(doc_category);
CREATE INDEX IF NOT EXISTS idx_doc_type ON universal_legal_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_subject ON universal_legal_documents(subject_primary);

-- Status & dates
CREATE INDEX IF NOT EXISTS idx_status ON universal_legal_documents(legal_status);
CREATE INDEX IF NOT EXISTS idx_year ON universal_legal_documents(doc_year);
CREATE INDEX IF NOT EXISTS idx_date_enacted ON universal_legal_documents(date_enacted);

-- Court/Authority
CREATE INDEX IF NOT EXISTS idx_court ON universal_legal_documents(court_name);
CREATE INDEX IF NOT EXISTS idx_authority ON universal_legal_documents(issuing_authority);

-- File management
CREATE INDEX IF NOT EXISTS idx_pdf_downloaded ON universal_legal_documents(pdf_downloaded);
CREATE INDEX IF NOT EXISTS idx_folder_category ON universal_legal_documents(folder_category);

-- Source
CREATE INDEX IF NOT EXISTS idx_source_domain ON universal_legal_documents(source_domain);
CREATE INDEX IF NOT EXISTS idx_scrape_status ON universal_legal_documents(scrape_status);

-- Timestamps
CREATE INDEX IF NOT EXISTS idx_created_at ON universal_legal_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_updated_at ON universal_legal_documents(updated_at);

-- Citations
CREATE INDEX IF NOT EXISTS idx_cit_citing ON citations(citing_doc_id);
CREATE INDEX IF NOT EXISTS idx_cit_cited ON citations(cited_doc_id);
CREATE INDEX IF NOT EXISTS idx_cit_type ON citations(citation_type);

-- Amendments
CREATE INDEX IF NOT EXISTS idx_amend_base ON document_amendments(base_doc_id);
CREATE INDEX IF NOT EXISTS idx_amend_amending ON document_amendments(amending_doc_id);

-- ============================================================================
-- VIEWS - Reporting and Statistics
-- ============================================================================

-- Overall statistics
CREATE VIEW IF NOT EXISTS v_overall_stats AS
SELECT
    COUNT(*) as total_documents,
    COUNT(DISTINCT country_code) as total_countries,
    COUNT(DISTINCT doc_category) as total_categories,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    COUNT(CASE WHEN legal_status = 'ACTIVE' THEN 1 END) as active_documents,
    MIN(doc_year) as earliest_year,
    MAX(doc_year) as latest_year,
    AVG(data_quality_score) as avg_quality_score
FROM universal_legal_documents;

-- Country statistics
CREATE VIEW IF NOT EXISTS v_country_stats AS
SELECT
    country_code,
    country_name,
    COUNT(*) as total_docs,
    COUNT(DISTINCT doc_category) as categories,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    COUNT(CASE WHEN legal_status = 'ACTIVE' THEN 1 END) as active_docs,
    MIN(doc_year) as earliest_year,
    MAX(doc_year) as latest_year,
    MAX(scrape_timestamp) as last_scraped,
    AVG(data_quality_score) as avg_quality
FROM universal_legal_documents
GROUP BY country_code, country_name;

-- Category statistics
CREATE VIEW IF NOT EXISTS v_category_stats AS
SELECT
    doc_category,
    COUNT(*) as total_docs,
    COUNT(DISTINCT country_code) as countries,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    MIN(doc_year) as earliest_year,
    MAX(doc_year) as latest_year
FROM universal_legal_documents
GROUP BY doc_category;

-- Recent activity
CREATE VIEW IF NOT EXISTS v_recent_scrapes AS
SELECT
    country_code,
    doc_category,
    COUNT(*) as docs_scraped,
    MAX(scrape_timestamp) as last_scrape
FROM universal_legal_documents
WHERE DATE(scrape_timestamp) = DATE('now')
GROUP BY country_code, doc_category;

-- Quality monitoring
CREATE VIEW IF NOT EXISTS v_quality_issues AS
SELECT
    country_code,
    doc_category,
    COUNT(*) as total_docs,
    COUNT(CASE WHEN manual_review_needed = 1 THEN 1 END) as needs_review,
    COUNT(CASE WHEN validation_status = 'FAILED' THEN 1 END) as validation_failed,
    AVG(data_quality_score) as avg_quality
FROM universal_legal_documents
GROUP BY country_code, doc_category;

-- ============================================================================
-- TRIGGERS - Automatic updates
-- ============================================================================

-- Update timestamp trigger
CREATE TRIGGER IF NOT EXISTS trg_update_timestamp
AFTER UPDATE ON universal_legal_documents
BEGIN
    UPDATE universal_legal_documents
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Update citation counts
CREATE TRIGGER IF NOT EXISTS trg_update_citation_counts_insert
AFTER INSERT ON citations
BEGIN
    UPDATE universal_legal_documents
    SET cites_count = cites_count + 1
    WHERE id = NEW.citing_doc_id;

    UPDATE universal_legal_documents
    SET cited_by_count = cited_by_count + 1
    WHERE id = NEW.cited_doc_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_update_citation_counts_delete
AFTER DELETE ON citations
BEGIN
    UPDATE universal_legal_documents
    SET cites_count = cites_count - 1
    WHERE id = OLD.citing_doc_id;

    UPDATE universal_legal_documents
    SET cited_by_count = cited_by_count - 1
    WHERE id = OLD.cited_doc_id;
END;

-- ============================================================================
-- FULL-TEXT SEARCH (Optional - requires FTS5)
-- ============================================================================

-- Uncomment if SQLite compiled with FTS5 support
/*
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title_full,
    title_short,
    plain_text,
    summary,
    content='universal_legal_documents',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS trg_fts_insert
AFTER INSERT ON universal_legal_documents
BEGIN
    INSERT INTO documents_fts(rowid, title_full, title_short, plain_text, summary)
    VALUES (NEW.id, NEW.title_full, NEW.title_short, NEW.plain_text, NEW.summary);
END;

CREATE TRIGGER IF NOT EXISTS trg_fts_update
AFTER UPDATE ON universal_legal_documents
BEGIN
    UPDATE documents_fts
    SET title_full = NEW.title_full,
        title_short = NEW.title_short,
        plain_text = NEW.plain_text,
        summary = NEW.summary
    WHERE rowid = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_fts_delete
AFTER DELETE ON universal_legal_documents
BEGIN
    DELETE FROM documents_fts WHERE rowid = OLD.id;
END;
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
