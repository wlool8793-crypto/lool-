-- Migration 005: RAG Tables
-- Creates: document_chunks
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: document_chunks (RAG Text Chunks for Vector Retrieval)
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Chunk Identification
    chunk_index INTEGER NOT NULL,            -- 0, 1, 2, 3... (order in document)
    chunk_id VARCHAR(50),                    -- Optional external ID (for Qdrant, etc.)

    -- Chunk Content
    chunk_text TEXT NOT NULL,
    chunk_hash CHAR(16),                     -- Hash of chunk text (for deduplication)
    chunk_level VARCHAR(20),                 -- sentence, paragraph, section, semantic, hybrid

    -- Position Tracking
    start_char INTEGER,                      -- Start character position in full_text
    end_char INTEGER,                        -- End character position
    start_page INTEGER,                      -- Start page number in PDF
    end_page INTEGER,                        -- End page number

    -- Size Metrics
    chunk_tokens INTEGER,                    -- Token count (for LLM context)
    chunk_words INTEGER,
    chunk_chars INTEGER,

    -- Hierarchical Chunking
    parent_chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE SET NULL,
    child_chunk_count INTEGER DEFAULT 0,
    chunk_depth INTEGER DEFAULT 0,           -- 0 = top level, 1 = child, 2 = grandchild

    -- RAG/Embedding Metadata
    embedding_id VARCHAR(50),                -- Qdrant point ID or vector DB ID
    embedding_model VARCHAR(50),             -- all-MiniLM-L6-v2, text-embedding-ada-002
    embedding_dimension INTEGER,             -- 384, 768, 1536, etc.
    embedding_status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    embedded_at TIMESTAMP,

    -- Context Preservation
    context_before TEXT,                     -- Previous N characters for context
    context_after TEXT,                      -- Next N characters for context
    section_title VARCHAR(500),              -- Section/heading this chunk belongs to
    section_number VARCHAR(50),

    -- Semantic Properties
    is_heading BOOLEAN DEFAULT FALSE,
    is_citation BOOLEAN DEFAULT FALSE,
    is_footnote BOOLEAN DEFAULT FALSE,
    is_table BOOLEAN DEFAULT FALSE,
    is_list_item BOOLEAN DEFAULT FALSE,

    -- Quality Metrics
    chunk_quality_score DECIMAL(3,2),        -- 0.00 to 1.00
    has_meaningful_content BOOLEAN DEFAULT TRUE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,      -- Additional chunk-specific metadata

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_chunk_index UNIQUE(document_id, chunk_index),
    CONSTRAINT chk_chunk_level CHECK (chunk_level IN (
        'sentence', 'paragraph', 'section', 'page', 'semantic', 'hybrid', 'sliding_window'
    )),
    CONSTRAINT chk_embedding_status CHECK (embedding_status IN (
        'pending', 'processing', 'completed', 'failed', 'skipped'
    )),
    CONSTRAINT chk_position CHECK (start_char IS NULL OR end_char IS NULL OR end_char >= start_char),
    CONSTRAINT chk_pages CHECK (start_page IS NULL OR end_page IS NULL OR end_page >= start_page),
    CONSTRAINT chk_chunk_quality CHECK (chunk_quality_score >= 0 AND chunk_quality_score <= 1)
);

-- Indexes for document_chunks
CREATE INDEX idx_chunk_document ON document_chunks(document_id);
CREATE INDEX idx_chunk_doc_index ON document_chunks(document_id, chunk_index);
CREATE INDEX idx_chunk_embedding_id ON document_chunks(embedding_id) WHERE embedding_id IS NOT NULL;
CREATE INDEX idx_chunk_embedding_status ON document_chunks(embedding_status) WHERE embedding_status != 'completed';
CREATE INDEX idx_chunk_level ON document_chunks(chunk_level);
CREATE INDEX idx_chunk_parent ON document_chunks(parent_chunk_id) WHERE parent_chunk_id IS NOT NULL;
CREATE INDEX idx_chunk_depth ON document_chunks(chunk_depth);
CREATE INDEX idx_chunk_tokens ON document_chunks(chunk_tokens) WHERE chunk_tokens IS NOT NULL;
CREATE INDEX idx_chunk_quality ON document_chunks(chunk_quality_score DESC) WHERE chunk_quality_score IS NOT NULL;
CREATE INDEX idx_chunk_hash ON document_chunks(chunk_hash) WHERE chunk_hash IS NOT NULL;

-- Full-text search on chunk text
CREATE INDEX idx_chunk_text_fts ON document_chunks USING GIN(to_tsvector('english', chunk_text));

-- GIN index for metadata
CREATE INDEX idx_chunk_metadata ON document_chunks USING GIN(metadata);

-- Composite index for RAG queries (document + embedding status)
CREATE INDEX idx_chunk_doc_embedding ON document_chunks(document_id, embedding_status);

-- Trigger for updated_at
CREATE TRIGGER trigger_document_chunks_updated_at
    BEFORE UPDATE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update chunk count on documents table
CREATE OR REPLACE FUNCTION update_document_chunk_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE documents
        SET chunk_count = chunk_count + 1
        WHERE id = NEW.document_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE documents
        SET chunk_count = GREATEST(chunk_count - 1, 0)
        WHERE id = OLD.document_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_chunk_count
    AFTER INSERT OR DELETE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_chunk_count();

-- Function to auto-calculate chunk metrics
CREATE OR REPLACE FUNCTION calculate_chunk_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate character count
    NEW.chunk_chars := LENGTH(NEW.chunk_text);

    -- Calculate word count (approximate)
    NEW.chunk_words := array_length(regexp_split_to_array(NEW.chunk_text, '\s+'), 1);

    -- Calculate token count (rough estimate: words * 1.3)
    IF NEW.chunk_tokens IS NULL THEN
        NEW.chunk_tokens := ROUND(NEW.chunk_words * 1.3)::INTEGER;
    END IF;

    -- Set end_char if not provided
    IF NEW.start_char IS NOT NULL AND NEW.end_char IS NULL THEN
        NEW.end_char := NEW.start_char + NEW.chunk_chars;
    END IF;

    -- Generate hash if not provided
    IF NEW.chunk_hash IS NULL THEN
        NEW.chunk_hash := LEFT(MD5(NEW.chunk_text), 16);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_chunk_metrics
    BEFORE INSERT OR UPDATE OF chunk_text ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION calculate_chunk_metrics();

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Chunk statistics per document
CREATE OR REPLACE VIEW v_document_chunk_stats AS
SELECT
    d.id AS document_id,
    d.global_id,
    d.title_full,
    COUNT(c.id) AS total_chunks,
    AVG(c.chunk_tokens) AS avg_chunk_tokens,
    MIN(c.chunk_tokens) AS min_chunk_tokens,
    MAX(c.chunk_tokens) AS max_chunk_tokens,
    SUM(c.chunk_tokens) AS total_tokens,
    COUNT(CASE WHEN c.embedding_status = 'completed' THEN 1 END) AS embedded_chunks,
    COUNT(CASE WHEN c.embedding_status = 'pending' THEN 1 END) AS pending_chunks,
    COUNT(CASE WHEN c.embedding_status = 'failed' THEN 1 END) AS failed_chunks,
    AVG(c.chunk_quality_score) AS avg_quality_score
FROM documents d
LEFT JOIN document_chunks c ON d.id = c.document_id
GROUP BY d.id, d.global_id, d.title_full;

-- View: Embedding progress
CREATE OR REPLACE VIEW v_embedding_progress AS
SELECT
    embedding_model,
    embedding_status,
    COUNT(*) AS chunk_count,
    SUM(chunk_tokens) AS total_tokens,
    AVG(chunk_tokens) AS avg_tokens,
    MIN(embedded_at) AS first_embedded,
    MAX(embedded_at) AS last_embedded
FROM document_chunks
WHERE embedding_model IS NOT NULL
GROUP BY embedding_model, embedding_status
ORDER BY embedding_model, embedding_status;

-- View: Hierarchical chunk tree
CREATE OR REPLACE VIEW v_chunk_hierarchy AS
WITH RECURSIVE chunk_tree AS (
    -- Base case: root chunks (no parent)
    SELECT
        id,
        document_id,
        chunk_index,
        parent_chunk_id,
        chunk_level,
        chunk_depth,
        ARRAY[chunk_index] AS path,
        1 AS level
    FROM document_chunks
    WHERE parent_chunk_id IS NULL

    UNION ALL

    -- Recursive case: child chunks
    SELECT
        c.id,
        c.document_id,
        c.chunk_index,
        c.parent_chunk_id,
        c.chunk_level,
        c.chunk_depth,
        ct.path || c.chunk_index,
        ct.level + 1
    FROM document_chunks c
    INNER JOIN chunk_tree ct ON c.parent_chunk_id = ct.id
)
SELECT * FROM chunk_tree;

-- View: Chunks ready for RAG
CREATE OR REPLACE VIEW v_chunks_ready_for_rag AS
SELECT
    c.id,
    c.document_id,
    c.chunk_index,
    c.chunk_text,
    c.chunk_tokens,
    c.embedding_id,
    c.chunk_level,
    c.section_title,
    d.global_id,
    d.title_full,
    d.doc_type,
    d.doc_year,
    d.country_code,
    d.subject_primary
FROM document_chunks c
INNER JOIN documents d ON c.id = d.id
WHERE c.embedding_status = 'completed'
  AND c.has_meaningful_content = TRUE
  AND c.chunk_quality_score >= 0.5;

-- View: Chunk quality issues
CREATE OR REPLACE VIEW v_chunk_quality_issues AS
SELECT
    c.id,
    c.document_id,
    d.global_id,
    c.chunk_index,
    c.chunk_level,
    c.chunk_quality_score,
    c.chunk_tokens,
    c.has_meaningful_content,
    CASE
        WHEN c.chunk_tokens < 10 THEN 'Too short'
        WHEN c.chunk_tokens > 1000 THEN 'Too long'
        WHEN c.chunk_quality_score < 0.3 THEN 'Low quality'
        WHEN NOT c.has_meaningful_content THEN 'No meaningful content'
        ELSE 'Unknown issue'
    END AS issue_type
FROM document_chunks c
INNER JOIN documents d ON c.document_id = d.id
WHERE c.chunk_quality_score < 0.5
   OR c.chunk_tokens < 10
   OR c.chunk_tokens > 1000
   OR NOT c.has_meaningful_content;

-- Comments for documentation
COMMENT ON TABLE document_chunks IS 'Text chunks for RAG (Retrieval-Augmented Generation) with vector embeddings';
COMMENT ON COLUMN document_chunks.chunk_id IS 'External ID for vector database (Qdrant, Pinecone, etc.)';
COMMENT ON COLUMN document_chunks.embedding_id IS 'Vector database point ID';
COMMENT ON COLUMN document_chunks.chunk_level IS 'Chunking strategy: sentence, paragraph, section, semantic';
COMMENT ON COLUMN document_chunks.parent_chunk_id IS 'For hierarchical chunking (parent-child relationships)';

COMMENT ON FUNCTION update_document_chunk_count IS 'Auto-update chunk_count on documents table';
COMMENT ON FUNCTION calculate_chunk_metrics IS 'Auto-calculate chunk metrics (words, tokens, hash)';

COMMENT ON VIEW v_document_chunk_stats IS 'Chunk statistics aggregated per document';
COMMENT ON VIEW v_embedding_progress IS 'Embedding progress by model and status';
COMMENT ON VIEW v_chunk_hierarchy IS 'Recursive hierarchical chunk tree';
COMMENT ON VIEW v_chunks_ready_for_rag IS 'High-quality chunks ready for RAG retrieval';
COMMENT ON VIEW v_chunk_quality_issues IS 'Chunks with quality issues requiring attention';

SELECT 'Migration 005 completed: RAG tables and functions created' AS status;
