-- Migration 002: Content Tables
-- Creates: content, citations, judges
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: content (Full Text Storage with FTS)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,

    -- Text Content
    full_text TEXT,                          -- Complete document text
    headnote TEXT,                           -- Case headnote/summary
    summary TEXT,                            -- Executive summary
    judgment TEXT,                           -- Judgment text
    ratio_decidendi TEXT,                    -- Reasoning
    obiter_dicta TEXT,                       -- Incidental remarks

    -- Structured Sections (for Acts/Rules)
    preamble TEXT,
    sections JSONB DEFAULT '[]'::jsonb,      -- [{"number": "1", "title": "...", "text": "..."}]
    schedules JSONB DEFAULT '[]'::jsonb,
    appendices JSONB DEFAULT '[]'::jsonb,

    -- Full-Text Search (PostgreSQL TSVector)
    search_vector TSVECTOR,                  -- For full-text search
    search_vector_headnote TSVECTOR,

    -- Content Statistics
    word_count INTEGER,
    character_count INTEGER,
    paragraph_count INTEGER,
    section_count INTEGER DEFAULT 0,

    -- Language & Processing
    language_code CHAR(2) DEFAULT 'en',      -- en, bn, hi, ur
    ocr_applied BOOLEAN DEFAULT FALSE,
    ocr_confidence DECIMAL(3,2),
    text_quality VARCHAR(20),                -- high, medium, low, poor

    -- Content Extraction Metadata
    extraction_method VARCHAR(20),           -- pdf_text, ocr, manual, api
    extraction_tool VARCHAR(50),             -- pypdf2, tesseract, etc.
    extraction_timestamp TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_language CHECK (language_code ~ '^[a-z]{2}$'),
    CONSTRAINT chk_text_quality CHECK (text_quality IN ('high', 'medium', 'low', 'poor'))
);

-- Indexes for content
CREATE INDEX idx_content_document ON content(document_id);
CREATE INDEX idx_content_language ON content(language_code);
CREATE INDEX idx_content_quality ON content(text_quality) WHERE text_quality IS NOT NULL;

-- GIN indexes for full-text search
CREATE INDEX idx_content_fts ON content USING GIN(search_vector);
CREATE INDEX idx_content_headnote_fts ON content USING GIN(search_vector_headnote);

-- GIN indexes for JSON fields
CREATE INDEX idx_content_sections ON content USING GIN(sections);

-- Trigger to auto-update search vectors
CREATE OR REPLACE FUNCTION update_content_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        COALESCE(NEW.full_text, '') || ' ' ||
        COALESCE(NEW.judgment, '') || ' ' ||
        COALESCE(NEW.summary, '')
    );

    NEW.search_vector_headnote := to_tsvector('english', COALESCE(NEW.headnote, ''));

    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_content_search_vector
    BEFORE INSERT OR UPDATE OF full_text, judgment, summary, headnote ON content
    FOR EACH ROW
    EXECUTE FUNCTION update_content_search_vector();

CREATE TRIGGER trigger_content_updated_at
    BEFORE UPDATE ON content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: citations (Citation Details with Phase 1 Integration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Citation Type
    citation_type VARCHAR(20) NOT NULL,      -- primary, alternate, neutral, parallel

    -- Parsed Citation Components
    volume INTEGER,
    year INTEGER,
    reporter VARCHAR(20),                    -- DLR, BLD, AIR, SCC, PLD, SCMR
    court_code VARCHAR(10),                  -- HCD, AD, SC, etc.
    page INTEGER,
    series VARCHAR(10),                      -- Old Series, New Series

    -- Encoded Citation (Phase 1 Integration)
    citation_encoded VARCHAR(50),            -- 22DLR98H205 (from Phase 1 CitationEncoder)
    citation_display TEXT,                   -- 22 (1998) DLR (HCD) 205

    -- Additional Citation Info
    citation_full TEXT,                      -- Complete citation as it appears
    neutral_citation VARCHAR(100),           -- [2020] EWHC 123 (Admin)

    -- Flags
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_citation_type_encoded UNIQUE(document_id, citation_type, citation_encoded),
    CONSTRAINT chk_citation_type CHECK (citation_type IN ('primary', 'alternate', 'neutral', 'parallel')),
    CONSTRAINT chk_year_range CHECK (year >= 1800 AND year <= 2100),
    CONSTRAINT chk_volume CHECK (volume > 0),
    CONSTRAINT chk_page CHECK (page > 0)
);

-- Indexes for citations
CREATE INDEX idx_citation_document ON citations(document_id);
CREATE INDEX idx_citation_type ON citations(citation_type);
CREATE INDEX idx_citation_reporter ON citations(reporter) WHERE reporter IS NOT NULL;
CREATE INDEX idx_citation_year ON citations(year) WHERE year IS NOT NULL;
CREATE INDEX idx_citation_encoded ON citations(citation_encoded) WHERE citation_encoded IS NOT NULL;
CREATE INDEX idx_citation_primary ON citations(is_primary) WHERE is_primary = TRUE;

-- Full-text search on citation display
CREATE INDEX idx_citation_display_fts ON citations USING GIN(to_tsvector('english', citation_display));

-- ============================================================================
-- TABLE: judges (Bench Composition)
-- ============================================================================
CREATE TABLE IF NOT EXISTS judges (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Judge Information
    judge_name VARCHAR(200) NOT NULL,
    judge_title VARCHAR(50),                 -- Hon'ble, Justice, Chief Justice
    judge_designation VARCHAR(50),           -- CJ, J, AJ

    -- Role in Case
    is_author BOOLEAN DEFAULT FALSE,         -- Author of main judgment
    is_presiding BOOLEAN DEFAULT FALSE,      -- Presiding judge
    opinion_type VARCHAR(20),                -- majority, concurring, dissenting, separate

    -- Judge Order
    judge_order INTEGER NOT NULL DEFAULT 1,  -- Position in bench

    -- Opinion Details
    opinion_summary TEXT,
    opinion_pages JSONB,                     -- Page numbers where opinion appears

    -- Judge Metadata
    judge_identifier VARCHAR(100),           -- Unique judge ID (if available)
    judge_court VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_judge_name_opinion UNIQUE(document_id, judge_name, opinion_type),
    CONSTRAINT chk_opinion_type CHECK (opinion_type IN ('majority', 'concurring', 'dissenting', 'separate', 'unanimous')),
    CONSTRAINT chk_judge_order CHECK (judge_order > 0)
);

-- Indexes for judges
CREATE INDEX idx_judge_document ON judges(document_id);
CREATE INDEX idx_judge_name ON judges(judge_name);
CREATE INDEX idx_judge_author ON judges(is_author) WHERE is_author = TRUE;
CREATE INDEX idx_judge_presiding ON judges(is_presiding) WHERE is_presiding = TRUE;
CREATE INDEX idx_judge_opinion ON judges(opinion_type) WHERE opinion_type IS NOT NULL;

-- Full-text search on judge names
CREATE INDEX idx_judge_name_fts ON judges USING GIN(to_tsvector('english', judge_name));

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Documents with primary citations
CREATE OR REPLACE VIEW v_documents_with_citations AS
SELECT
    d.id,
    d.global_id,
    d.title_full,
    d.doc_year,
    d.country_code,
    d.doc_type,
    c.citation_display,
    c.citation_encoded,
    c.reporter,
    c.year AS citation_year
FROM documents d
LEFT JOIN citations c ON d.id = c.document_id AND c.is_primary = TRUE;

-- View: Documents with content stats
CREATE OR REPLACE VIEW v_documents_with_content AS
SELECT
    d.id,
    d.global_id,
    d.title_full,
    d.doc_type,
    c.word_count,
    c.paragraph_count,
    c.section_count,
    c.language_code,
    c.text_quality,
    CASE
        WHEN c.full_text IS NOT NULL THEN 'full'
        WHEN c.summary IS NOT NULL THEN 'summary'
        ELSE 'none'
    END AS content_availability
FROM documents d
LEFT JOIN content c ON d.id = c.document_id;

-- View: Case bench composition
CREATE OR REPLACE VIEW v_case_benches AS
SELECT
    d.id AS document_id,
    d.global_id,
    d.title_full,
    COUNT(j.id) AS bench_size,
    STRING_AGG(j.judge_name, ', ' ORDER BY j.judge_order) AS judges,
    MAX(CASE WHEN j.is_author THEN j.judge_name END) AS author_judge
FROM documents d
LEFT JOIN judges j ON d.id = j.document_id
WHERE d.doc_type = 'CAS'
GROUP BY d.id, d.global_id, d.title_full;

-- Comments for documentation
COMMENT ON TABLE content IS 'Full text storage with PostgreSQL full-text search integration';
COMMENT ON COLUMN content.search_vector IS 'Auto-generated TSVector for full-text search on full_text + judgment + summary';

COMMENT ON TABLE citations IS 'Citation details with Phase 1 CitationEncoder integration';
COMMENT ON COLUMN citations.citation_encoded IS 'Encoded citation from Phase 1 (e.g., 22DLR98H205)';

COMMENT ON TABLE judges IS 'Bench composition and judge opinions';

COMMENT ON VIEW v_documents_with_citations IS 'Documents with their primary citations';
COMMENT ON VIEW v_documents_with_content IS 'Documents with content availability statistics';
COMMENT ON VIEW v_case_benches IS 'Case documents with bench composition';

-- Grant permissions (adjust as needed)
-- GRANT SELECT ON v_documents_with_citations TO legal_rag_readonly;
-- GRANT SELECT ON v_documents_with_content TO legal_rag_readonly;
-- GRANT SELECT ON v_case_benches TO legal_rag_readonly;

SELECT 'Migration 002 completed: Content tables and views created' AS status;
