-- Migration: Add Bangladesh Laws Table
-- Created: 2025-10-21
-- Description: Table for storing Bangladesh legal documents from bdlaws.minlaw.gov.bd

CREATE TABLE IF NOT EXISTS bangladesh_laws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core Identifiers
    act_number TEXT,                    -- e.g., "Act No. 123"
    act_id TEXT,                        -- e.g., "act-367" from URL
    title TEXT NOT NULL,                -- Full title of the law
    short_title TEXT,                   -- Short title if available

    -- Classification
    type TEXT,                          -- Act, Ordinance, President's Order
    category TEXT,                      -- Subject category
    year INTEGER,                       -- Year enacted
    ministry TEXT,                      -- Responsible ministry

    -- URLs and Paths
    url TEXT UNIQUE NOT NULL,           -- Main URL
    source_index TEXT,                  -- chronological or alphabetical

    -- Content
    html_content TEXT,                  -- Full HTML content
    plain_text TEXT,                    -- Extracted plain text
    summary TEXT,                       -- Summary if available

    -- PDF Information
    pdf_url TEXT,                       -- PDF download link
    pdf_path TEXT,                      -- Local path to downloaded PDF
    pdf_downloaded BOOLEAN DEFAULT 0,   -- Whether PDF was downloaded
    pdf_size_kb INTEGER,                -- PDF file size in KB

    -- Status Information
    status TEXT DEFAULT 'in_force',     -- in_force, repealed, amended
    last_amended_date TEXT,             -- Date of last amendment

    -- Scraping Metadata
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scrape_status TEXT DEFAULT 'pending',  -- pending, complete, error
    error_message TEXT,                 -- Error details if any

    -- Indexes for fast queries
    UNIQUE(url)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_bangladesh_year ON bangladesh_laws(year);
CREATE INDEX IF NOT EXISTS idx_bangladesh_type ON bangladesh_laws(type);
CREATE INDEX IF NOT EXISTS idx_bangladesh_category ON bangladesh_laws(category);
CREATE INDEX IF NOT EXISTS idx_bangladesh_status ON bangladesh_laws(status);
CREATE INDEX IF NOT EXISTS idx_bangladesh_pdf_downloaded ON bangladesh_laws(pdf_downloaded);
CREATE INDEX IF NOT EXISTS idx_bangladesh_act_id ON bangladesh_laws(act_id);

-- Statistics view
CREATE VIEW IF NOT EXISTS bangladesh_stats AS
SELECT
    COUNT(*) as total_laws,
    COUNT(CASE WHEN pdf_downloaded = 1 THEN 1 END) as pdfs_downloaded,
    COUNT(CASE WHEN html_content IS NOT NULL THEN 1 END) as html_scraped,
    COUNT(CASE WHEN status = 'in_force' THEN 1 END) as laws_in_force,
    MIN(year) as earliest_year,
    MAX(year) as latest_year,
    COUNT(DISTINCT type) as law_types,
    COUNT(DISTINCT category) as categories
FROM bangladesh_laws;
