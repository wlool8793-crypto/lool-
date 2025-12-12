-- Migration 004: Metadata Tables
-- Creates: translations, document_metadata
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: translations (Multi-Language Support)
-- ============================================================================
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Language Information
    language_code CHAR(2) NOT NULL,          -- bn, hi, ur, ta, pa, etc.
    language_name VARCHAR(50),               -- Bengali, Hindi, Urdu

    -- Translated Content
    title_translated TEXT,
    summary_translated TEXT,
    headnote_translated TEXT,
    full_text_translated TEXT,

    -- Translation Metadata
    translation_method VARCHAR(20),          -- official, auto, manual, human_reviewed
    translation_tool VARCHAR(50),            -- Google Translate, DeepL, manual, etc.
    translation_quality DECIMAL(3,2),        -- 0.00 to 1.00
    translation_confidence DECIMAL(3,2),

    -- Translator Information
    translator_name VARCHAR(200),
    translator_organization VARCHAR(200),
    translation_date DATE,

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(200),
    verified_at TIMESTAMP,

    -- Search Support
    search_vector_translated TSVECTOR,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_language UNIQUE(document_id, language_code),
    CONSTRAINT chk_language_code CHECK (language_code ~ '^[a-z]{2}$'),
    CONSTRAINT chk_translation_method CHECK (translation_method IN (
        'official', 'auto', 'manual', 'human_reviewed', 'certified', 'machine'
    )),
    CONSTRAINT chk_translation_quality CHECK (translation_quality >= 0 AND translation_quality <= 1)
);

-- Indexes for translations
CREATE INDEX idx_translation_document ON translations(document_id);
CREATE INDEX idx_translation_language ON translations(language_code);
CREATE INDEX idx_translation_method ON translations(translation_method);
CREATE INDEX idx_translation_quality ON translations(translation_quality DESC) WHERE translation_quality IS NOT NULL;
CREATE INDEX idx_translation_verified ON translations(is_verified) WHERE is_verified = TRUE;

-- Full-text search on translated content
CREATE INDEX idx_translation_fts ON translations USING GIN(search_vector_translated);

-- Trigger to update search vector
CREATE OR REPLACE FUNCTION update_translation_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector_translated := to_tsvector('simple',  -- Use 'simple' for non-English
        COALESCE(NEW.title_translated, '') || ' ' ||
        COALESCE(NEW.summary_translated, '') || ' ' ||
        COALESCE(NEW.headnote_translated, '')
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_translation_search_vector
    BEFORE INSERT OR UPDATE OF title_translated, summary_translated, headnote_translated ON translations
    FOR EACH ROW
    EXECUTE FUNCTION update_translation_search_vector();

CREATE TRIGGER trigger_translations_updated_at
    BEFORE UPDATE ON translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: document_metadata (Flexible Key-Value Store)
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_metadata (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Metadata Key-Value
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT,
    metadata_type VARCHAR(20) DEFAULT 'text',  -- text, number, date, json, boolean, url

    -- Categorization
    metadata_category VARCHAR(50),             -- court_info, technical, administrative, custom
    metadata_source VARCHAR(50),               -- scraper, extractor, manual, api

    -- Display Properties
    is_public BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    display_label VARCHAR(100),

    -- Validation
    is_verified BOOLEAN DEFAULT FALSE,
    validation_status VARCHAR(20),

    -- Metadata about metadata
    metadata_metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_metadata_key UNIQUE(document_id, metadata_key),
    CONSTRAINT chk_metadata_type CHECK (metadata_type IN (
        'text', 'number', 'date', 'datetime', 'json', 'boolean', 'url', 'email', 'array'
    ))
);

-- Indexes for document_metadata
CREATE INDEX idx_metadata_document ON document_metadata(document_id);
CREATE INDEX idx_metadata_key ON document_metadata(metadata_key);
CREATE INDEX idx_metadata_category ON document_metadata(metadata_category) WHERE metadata_category IS NOT NULL;
CREATE INDEX idx_metadata_type ON document_metadata(metadata_type);
CREATE INDEX idx_metadata_public ON document_metadata(is_public) WHERE is_public = TRUE;

-- GIN index for JSON metadata
CREATE INDEX idx_metadata_jsonb ON document_metadata USING GIN(metadata_metadata);

-- Index for key-value lookups
CREATE INDEX idx_metadata_key_value ON document_metadata(metadata_key, metadata_value);

CREATE TRIGGER trigger_document_metadata_updated_at
    BEFORE UPDATE ON document_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get metadata value
CREATE OR REPLACE FUNCTION get_document_metadata(
    p_document_id INTEGER,
    p_metadata_key VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_value TEXT;
BEGIN
    SELECT metadata_value INTO v_value
    FROM document_metadata
    WHERE document_id = p_document_id
      AND metadata_key = p_metadata_key
    LIMIT 1;

    RETURN v_value;
END;
$$ LANGUAGE plpgsql;

-- Function to set metadata value
CREATE OR REPLACE FUNCTION set_document_metadata(
    p_document_id INTEGER,
    p_metadata_key VARCHAR,
    p_metadata_value TEXT,
    p_metadata_type VARCHAR DEFAULT 'text'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO document_metadata (document_id, metadata_key, metadata_value, metadata_type)
    VALUES (p_document_id, p_metadata_key, p_metadata_value, p_metadata_type)
    ON CONFLICT (document_id, metadata_key)
    DO UPDATE SET
        metadata_value = EXCLUDED.metadata_value,
        metadata_type = EXCLUDED.metadata_type,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Documents with translation availability
CREATE OR REPLACE VIEW v_documents_with_translations AS
SELECT
    d.id,
    d.global_id,
    d.title_full,
    d.country_code,
    COUNT(t.id) AS translation_count,
    STRING_AGG(t.language_code, ', ' ORDER BY t.language_code) AS available_languages,
    BOOL_OR(t.is_verified) AS has_verified_translation
FROM documents d
LEFT JOIN translations t ON d.id = t.document_id
GROUP BY d.id, d.global_id, d.title_full, d.country_code;

-- View: Metadata summary per document
CREATE OR REPLACE VIEW v_document_metadata_summary AS
SELECT
    document_id,
    COUNT(*) AS total_metadata_fields,
    COUNT(CASE WHEN metadata_type = 'text' THEN 1 END) AS text_fields,
    COUNT(CASE WHEN metadata_type = 'number' THEN 1 END) AS number_fields,
    COUNT(CASE WHEN metadata_type = 'date' THEN 1 END) AS date_fields,
    COUNT(CASE WHEN metadata_type = 'json' THEN 1 END) AS json_fields,
    COUNT(CASE WHEN is_verified THEN 1 END) AS verified_fields
FROM document_metadata
GROUP BY document_id;

-- View: Translation quality report
CREATE OR REPLACE VIEW v_translation_quality_report AS
SELECT
    language_code,
    language_name,
    COUNT(*) AS total_translations,
    AVG(translation_quality) AS avg_quality,
    COUNT(CASE WHEN is_verified THEN 1 END) AS verified_count,
    COUNT(CASE WHEN translation_method = 'official' THEN 1 END) AS official_count,
    COUNT(CASE WHEN translation_method = 'auto' THEN 1 END) AS auto_count,
    COUNT(CASE WHEN translation_method = 'manual' THEN 1 END) AS manual_count
FROM translations
GROUP BY language_code, language_name
ORDER BY total_translations DESC;

-- Comments for documentation
COMMENT ON TABLE translations IS 'Multi-language translations for documents (Bengali, Hindi, Urdu, etc.)';
COMMENT ON COLUMN translations.search_vector_translated IS 'Auto-generated TSVector for full-text search in translated language';

COMMENT ON TABLE document_metadata IS 'Flexible key-value store for additional document metadata';
COMMENT ON FUNCTION get_document_metadata IS 'Retrieve metadata value for a document by key';
COMMENT ON FUNCTION set_document_metadata IS 'Set or update metadata value for a document';

COMMENT ON VIEW v_documents_with_translations IS 'Documents with translation availability summary';
COMMENT ON VIEW v_document_metadata_summary IS 'Metadata field count and type summary per document';
COMMENT ON VIEW v_translation_quality_report IS 'Translation quality metrics by language';

SELECT 'Migration 004 completed: Metadata tables and functions created' AS status;
