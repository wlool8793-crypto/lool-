-- Migration 003: Reference Tables
-- Creates: legal_references, sections_cited, keywords, amendments
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: legal_references (Citation Graph for Neo4j Preparation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS legal_references (
    id SERIAL PRIMARY KEY,

    -- Document Relationships
    citing_doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    cited_doc_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,  -- NULL if external

    -- Reference Details
    citation_text TEXT,                      -- How the citation appears in text
    reference_type VARCHAR(20),              -- followed, distinguished, overruled, referred, approved, disapproved
    citation_strength VARCHAR(20),           -- strong, medium, weak, mentioned

    -- Context
    context_text TEXT,                       -- Surrounding text
    context_snippet TEXT,                    -- Brief snippet (200 chars)

    -- Position in Document
    page_number INTEGER,
    paragraph_number INTEGER,
    section_reference VARCHAR(50),           -- If in specific section

    -- Resolution Status
    is_resolved BOOLEAN DEFAULT FALSE,       -- Found in our database
    external_citation TEXT,                  -- If citation is to external document
    external_jurisdiction VARCHAR(50),

    -- Graph Properties (for Neo4j export)
    graph_weight DECIMAL(3,2) DEFAULT 0.5,   -- Edge weight for graph analysis
    is_precedent BOOLEAN DEFAULT FALSE,      -- Is this a precedential citation?

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_reference_type CHECK (reference_type IN (
        'followed', 'distinguished', 'overruled', 'referred', 'approved',
        'disapproved', 'considered', 'applied', 'explained', 'doubted', 'not_followed'
    )),
    CONSTRAINT chk_citation_strength CHECK (citation_strength IN ('strong', 'medium', 'weak', 'mentioned', 'cited')),
    CONSTRAINT chk_graph_weight CHECK (graph_weight >= 0 AND graph_weight <= 1)
);

-- Indexes for legal_references
CREATE INDEX idx_ref_citing ON legal_references(citing_doc_id);
CREATE INDEX idx_ref_cited ON legal_references(cited_doc_id) WHERE cited_doc_id IS NOT NULL;
CREATE INDEX idx_ref_type ON legal_references(reference_type);
CREATE INDEX idx_ref_strength ON legal_references(citation_strength);
CREATE INDEX idx_ref_resolved ON legal_references(is_resolved);
CREATE INDEX idx_ref_precedent ON legal_references(is_precedent) WHERE is_precedent = TRUE;
CREATE INDEX idx_ref_external ON legal_references(external_jurisdiction) WHERE external_jurisdiction IS NOT NULL;

-- Composite index for citation graph queries
CREATE INDEX idx_ref_citing_cited ON legal_references(citing_doc_id, cited_doc_id) WHERE cited_doc_id IS NOT NULL;

-- Full-text search on citation text
CREATE INDEX idx_ref_citation_fts ON legal_references USING GIN(to_tsvector('english', citation_text));

CREATE TRIGGER trigger_legal_references_updated_at
    BEFORE UPDATE ON legal_references
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: sections_cited (Statutory References)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sections_cited (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Act/Statute Information
    act_global_id VARCHAR(10),               -- References documents.global_id if in our DB
    act_name TEXT NOT NULL,                  -- Full act name
    act_short_name VARCHAR(200),
    act_year INTEGER,

    -- Section/Article Reference
    section_number VARCHAR(50),
    article_number VARCHAR(50),
    rule_number VARCHAR(50),
    clause_number VARCHAR(50),
    sub_section VARCHAR(50),

    -- Context
    context_text TEXT,
    mention_count INTEGER DEFAULT 1,         -- How many times cited in document

    -- Resolution
    is_resolved BOOLEAN DEFAULT FALSE,       -- Found in our database
    resolved_doc_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_at_least_one_reference CHECK (
        section_number IS NOT NULL OR
        article_number IS NOT NULL OR
        rule_number IS NOT NULL OR
        clause_number IS NOT NULL
    )
);

-- Indexes for sections_cited
CREATE INDEX idx_section_document ON sections_cited(document_id);
CREATE INDEX idx_section_act_name ON sections_cited(act_name);
CREATE INDEX idx_section_act_id ON sections_cited(act_global_id) WHERE act_global_id IS NOT NULL;
CREATE INDEX idx_section_resolved ON sections_cited(resolved_doc_id) WHERE resolved_doc_id IS NOT NULL;
CREATE INDEX idx_section_year ON sections_cited(act_year) WHERE act_year IS NOT NULL;

-- Full-text search on act names
CREATE INDEX idx_section_act_fts ON sections_cited USING GIN(to_tsvector('english', act_name));

-- ============================================================================
-- TABLE: keywords (Extracted Keywords & Tags)
-- ============================================================================
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Keyword Details
    keyword VARCHAR(100) NOT NULL,
    keyword_normalized VARCHAR(100),         -- Lowercased, stemmed version
    keyword_type VARCHAR(20),                -- subject, entity, concept, person, place, organization

    -- Weighting & Confidence
    weight DECIMAL(3,2),                     -- 0.00 to 1.00 (importance/relevance)
    frequency INTEGER DEFAULT 1,             -- Occurrence count in document
    tf_idf_score DECIMAL(10,6),             -- TF-IDF score

    -- Extraction Method
    extraction_method VARCHAR(20),           -- auto, manual, ml, regex, ner
    extraction_model VARCHAR(50),            -- Model name if ML-based
    confidence DECIMAL(3,2),                 -- Confidence score (0-1)

    -- Position
    first_mention_position INTEGER,          -- Character position of first occurrence

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_keyword_type UNIQUE(document_id, keyword_normalized, keyword_type),
    CONSTRAINT chk_keyword_type CHECK (keyword_type IN (
        'subject', 'entity', 'concept', 'person', 'place', 'organization',
        'event', 'law', 'statute', 'legal_term', 'other'
    )),
    CONSTRAINT chk_weight CHECK (weight >= 0 AND weight <= 1),
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

-- Indexes for keywords
CREATE INDEX idx_keyword_document ON keywords(document_id);
CREATE INDEX idx_keyword_lookup ON keywords(keyword_normalized);
CREATE INDEX idx_keyword_type ON keywords(keyword_type);
CREATE INDEX idx_keyword_weight ON keywords(weight DESC) WHERE weight IS NOT NULL;
CREATE INDEX idx_keyword_method ON keywords(extraction_method);

-- GIN index for faster keyword searches
CREATE INDEX idx_keyword_trgm ON keywords USING GIN(keyword_normalized gin_trgm_ops);

-- ============================================================================
-- TABLE: amendments (Act Amendment History)
-- ============================================================================
CREATE TABLE IF NOT EXISTS amendments (
    id SERIAL PRIMARY KEY,

    -- Document Relationships
    base_doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    amending_doc_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,

    -- Amendment Details
    amendment_number INTEGER,                -- 1st Amendment, 2nd Amendment, etc.
    amendment_name VARCHAR(200),             -- Constitutional Amendment Act, 2020
    amendment_date DATE,
    effective_date DATE,

    -- Amendment Type
    amendment_type VARCHAR(20),              -- substitution, insertion, deletion, addition, repeal

    -- Affected Sections
    sections_affected JSONB DEFAULT '[]'::jsonb,  -- ["Section 5", "Section 12A", "Schedule III"]
    articles_affected JSONB DEFAULT '[]'::jsonb,
    schedules_affected JSONB DEFAULT '[]'::jsonb,

    -- Description
    description TEXT,
    summary TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_reversed BOOLEAN DEFAULT FALSE,       -- Was this amendment later reversed?
    reversed_by_doc_id INTEGER REFERENCES documents(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_amendment_type CHECK (amendment_type IN (
        'substitution', 'insertion', 'deletion', 'addition', 'repeal',
        'modification', 'omission', 'renumbering', 'redesignation'
    ))
);

-- Indexes for amendments
CREATE INDEX idx_amendment_base ON amendments(base_doc_id);
CREATE INDEX idx_amendment_amending ON amendments(amending_doc_id) WHERE amending_doc_id IS NOT NULL;
CREATE INDEX idx_amendment_number ON amendments(base_doc_id, amendment_number);
CREATE INDEX idx_amendment_date ON amendments(amendment_date) WHERE amendment_date IS NOT NULL;
CREATE INDEX idx_amendment_type ON amendments(amendment_type);
CREATE INDEX idx_amendment_active ON amendments(is_active) WHERE is_active = TRUE;

-- GIN index for sections search
CREATE INDEX idx_amendment_sections ON amendments USING GIN(sections_affected);

CREATE TRIGGER trigger_amendments_updated_at
    BEFORE UPDATE ON amendments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Citation network statistics
CREATE OR REPLACE VIEW v_citation_network_stats AS
SELECT
    citing_doc_id,
    COUNT(*) AS total_citations,
    COUNT(DISTINCT cited_doc_id) AS unique_citations,
    COUNT(CASE WHEN reference_type = 'followed' THEN 1 END) AS citations_followed,
    COUNT(CASE WHEN reference_type = 'distinguished' THEN 1 END) AS citations_distinguished,
    COUNT(CASE WHEN reference_type = 'overruled' THEN 1 END) AS citations_overruled,
    COUNT(CASE WHEN is_resolved THEN 1 END) AS internal_citations,
    COUNT(CASE WHEN NOT is_resolved THEN 1 END) AS external_citations
FROM legal_references
GROUP BY citing_doc_id;

-- View: Most cited documents
CREATE OR REPLACE VIEW v_most_cited_documents AS
SELECT
    d.id,
    d.global_id,
    d.title_full,
    d.doc_year,
    c.citation_display,
    COUNT(lr.id) AS times_cited,
    COUNT(CASE WHEN lr.reference_type = 'followed' THEN 1 END) AS times_followed,
    COUNT(CASE WHEN lr.is_precedent THEN 1 END) AS precedential_citations
FROM documents d
LEFT JOIN citations c ON d.id = c.document_id AND c.is_primary = TRUE
LEFT JOIN legal_references lr ON d.id = lr.cited_doc_id
GROUP BY d.id, d.global_id, d.title_full, d.doc_year, c.citation_display
HAVING COUNT(lr.id) > 0
ORDER BY times_cited DESC;

-- View: Act amendment timeline
CREATE OR REPLACE VIEW v_act_amendment_timeline AS
SELECT
    d.id AS act_id,
    d.global_id,
    d.title_full AS act_name,
    d.date_enacted AS original_date,
    a.amendment_number,
    a.amendment_date,
    a.amendment_type,
    a.description,
    a.is_active
FROM documents d
LEFT JOIN amendments a ON d.id = a.base_doc_id
WHERE d.doc_type = 'ACT'
ORDER BY d.id, a.amendment_date;

-- View: Keyword frequency across corpus
CREATE OR REPLACE VIEW v_keyword_frequency AS
SELECT
    keyword_normalized,
    keyword_type,
    COUNT(DISTINCT document_id) AS document_count,
    SUM(frequency) AS total_frequency,
    AVG(weight) AS avg_weight,
    MIN(first_mention_position) AS earliest_position
FROM keywords
GROUP BY keyword_normalized, keyword_type
HAVING COUNT(DISTINCT document_id) > 1
ORDER BY document_count DESC, total_frequency DESC;

-- Comments for documentation
COMMENT ON TABLE legal_references IS 'Citation graph for document relationships (prepared for Neo4j export)';
COMMENT ON COLUMN legal_references.graph_weight IS 'Edge weight for graph algorithms (0-1)';

COMMENT ON TABLE sections_cited IS 'Statutory references within documents';
COMMENT ON TABLE keywords IS 'Extracted keywords with TF-IDF weighting';
COMMENT ON TABLE amendments IS 'Act amendment history and tracking';

COMMENT ON VIEW v_citation_network_stats IS 'Citation statistics per document';
COMMENT ON VIEW v_most_cited_documents IS 'Documents ranked by citation count';
COMMENT ON VIEW v_act_amendment_timeline IS 'Timeline of act amendments';
COMMENT ON VIEW v_keyword_frequency IS 'Keyword frequency across all documents';

SELECT 'Migration 003 completed: Reference tables and views created' AS status;
