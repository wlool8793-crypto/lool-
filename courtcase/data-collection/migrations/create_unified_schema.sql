-- Migration: Create Unified Multi-Country Legal Documents Schema
-- Created: 2025-10-21
-- Description: Unified table supporting multiple countries' legal databases

-- Main unified legal documents table
CREATE TABLE IF NOT EXISTS legal_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Country Identification
    country TEXT NOT NULL,                      -- 'india', 'bangladesh', 'pakistan', etc.
    country_doc_id TEXT,                        -- Country-specific document ID (e.g., act number)

    -- Document Metadata
    title TEXT NOT NULL,
    short_title TEXT,
    doc_type TEXT,                              -- Case, Act, Ordinance, Presidential Order, etc.
    year INTEGER,
    category TEXT,                              -- Subject category
    court_or_ministry TEXT,                     -- Court name (India) or Ministry (Bangladesh)

    -- Citations and References
    citation TEXT,                              -- Legal citation
    bench TEXT,                                 -- Judge names (for cases)

    -- URLs and Source
    source_url TEXT NOT NULL,                   -- Original URL
    source_site TEXT NOT NULL,                  -- Domain name
    source_index TEXT,                          -- Which index it came from

    -- Content
    html_content TEXT,                          -- Full HTML content
    plain_text TEXT,                            -- Extracted plain text
    summary TEXT,                               -- Summary/snippet

    -- PDF Information
    pdf_url TEXT,                               -- PDF download URL
    pdf_path TEXT,                              -- Local filesystem path
    pdf_downloaded BOOLEAN DEFAULT 0,           -- Whether PDF was successfully downloaded
    pdf_size_kb INTEGER,                        -- PDF file size in kilobytes
    pdf_hash TEXT,                              -- SHA256 hash for deduplication

    -- Status and Lifecycle
    status TEXT DEFAULT 'active',               -- active, repealed, amended
    effective_date TEXT,                        -- When it came into force
    last_amended_date TEXT,                     -- Last amendment date

    -- Scraping Metadata
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scrape_status TEXT DEFAULT 'complete',      -- pending, complete, error, partial
    error_message TEXT,                         -- Error details if any
    scraper_version TEXT,                       -- Version of scraper used

    -- Constraints
    UNIQUE(country, source_url)
);

-- Flexible metadata table for country-specific fields
CREATE TABLE IF NOT EXISTS document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    metadata_type TEXT DEFAULT 'text',          -- text, number, date, json

    FOREIGN KEY (document_id) REFERENCES legal_documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, metadata_key)
);

-- Citations and references between documents
CREATE TABLE IF NOT EXISTS document_citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citing_doc_id INTEGER NOT NULL,
    cited_doc_id INTEGER,
    citation_text TEXT,
    citation_context TEXT,

    FOREIGN KEY (citing_doc_id) REFERENCES legal_documents(id) ON DELETE CASCADE,
    FOREIGN KEY (cited_doc_id) REFERENCES legal_documents(id) ON DELETE SET NULL
);

-- Scraping queue for managing large scraping jobs
CREATE TABLE IF NOT EXISTS scraping_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    url TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',              -- pending, processing, complete, failed
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,

    UNIQUE(country, url)
);

-- ============================================================================
-- INDEXES for fast queries
-- ============================================================================

-- Country and document type
CREATE INDEX IF NOT EXISTS idx_docs_country ON legal_documents(country);
CREATE INDEX IF NOT EXISTS idx_docs_country_type ON legal_documents(country, doc_type);
CREATE INDEX IF NOT EXISTS idx_docs_type ON legal_documents(doc_type);

-- Time-based queries
CREATE INDEX IF NOT EXISTS idx_docs_year ON legal_documents(year);
CREATE INDEX IF NOT EXISTS idx_docs_scraped_at ON legal_documents(scraped_at);

-- Status queries
CREATE INDEX IF NOT EXISTS idx_docs_status ON legal_documents(status);
CREATE INDEX IF NOT EXISTS idx_docs_scrape_status ON legal_documents(scrape_status);
CREATE INDEX IF NOT EXISTS idx_docs_pdf_downloaded ON legal_documents(pdf_downloaded);

-- Court/Ministry
CREATE INDEX IF NOT EXISTS idx_docs_court_ministry ON legal_documents(court_or_ministry);

-- Full-text search (if SQLite compiled with FTS support)
-- CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
--     title, plain_text, summary,
--     content='legal_documents'
-- );

-- ============================================================================
-- VIEWS for statistics and reporting
-- ============================================================================

-- Overall statistics
CREATE VIEW IF NOT EXISTS overall_stats AS
SELECT
    COUNT(*) as total_documents,
    COUNT(DISTINCT country) as total_countries,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    COUNT(CASE WHEN html_content IS NOT NULL THEN 1 END) as html_scraped,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_documents,
    MIN(year) as earliest_year,
    MAX(year) as latest_year
FROM legal_documents;

-- Per-country statistics
CREATE VIEW IF NOT EXISTS country_stats AS
SELECT
    country,
    COUNT(*) as total_docs,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    COUNT(DISTINCT doc_type) as doc_types,
    COUNT(DISTINCT year) as years_covered,
    MIN(year) as earliest_year,
    MAX(year) as latest_year,
    MAX(scraped_at) as last_scraped
FROM legal_documents
GROUP BY country;

-- Documents scraped today
CREATE VIEW IF NOT EXISTS today_scraping_progress AS
SELECT
    country,
    COUNT(*) as scraped_today,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_today
FROM legal_documents
WHERE DATE(scraped_at) = DATE('now')
GROUP BY country;

-- ============================================================================
-- MIGRATION: Copy existing data from legal_cases table (if exists)
-- ============================================================================

-- Insert existing Indian Kanoon data into unified table
INSERT OR IGNORE INTO legal_documents (
    country,
    country_doc_id,
    title,
    doc_type,
    year,
    citation,
    court_or_ministry,
    source_url,
    source_site,
    html_content,
    plain_text,
    summary,
    pdf_url,
    pdf_path,
    pdf_downloaded,
    scraped_at
)
SELECT
    'india' as country,
    id as country_doc_id,
    title,
    'case' as doc_type,
    CAST(substr(case_date, 1, 4) AS INTEGER) as year,
    citation,
    court as court_or_ministry,
    case_url as source_url,
    'indiankanoon.org' as source_site,
    NULL as html_content,
    full_text as plain_text,
    snippet as summary,
    pdf_link as pdf_url,
    pdf_path,
    CASE WHEN pdf_downloaded = 1 THEN 1 ELSE 0 END as pdf_downloaded,
    scraped_at
FROM legal_cases
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='legal_cases');

-- ============================================================================
-- TRIGGERS for automatic timestamp updates
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_legal_documents_timestamp
AFTER UPDATE ON legal_documents
BEGIN
    UPDATE legal_documents
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
