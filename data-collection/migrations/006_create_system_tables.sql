-- Migration 006: System Tables
-- Creates: document_versions, sequence_tracker
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: document_versions (Version History & Audit Trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,         -- 1, 2, 3...

    -- Version Type
    change_type VARCHAR(20) NOT NULL,        -- content, metadata, pdf, citation, full

    -- What Changed
    change_description TEXT,
    changed_fields JSONB DEFAULT '[]'::jsonb,  -- ["title", "subject_primary", "legal_status"]
    change_summary TEXT,

    -- Version Validity Period
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,                      -- NULL = current version
    is_current BOOLEAN DEFAULT TRUE,

    -- Snapshot of Changed Data
    snapshot_data JSONB,                     -- Full or partial document snapshot

    -- Change Author/Source
    created_by VARCHAR(100),                 -- User ID, system, scraper name
    created_by_type VARCHAR(20),             -- user, system, scraper, api, import
    change_reason VARCHAR(200),              -- Why was this changed?

    -- Approval/Review
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    approval_status VARCHAR(20),             -- pending, approved, rejected

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_version UNIQUE(document_id, version_number),
    CONSTRAINT chk_version_number CHECK (version_number > 0),
    CONSTRAINT chk_change_type CHECK (change_type IN (
        'content', 'metadata', 'pdf', 'citation', 'status', 'full', 'translation', 'correction'
    )),
    CONSTRAINT chk_created_by_type CHECK (created_by_type IN (
        'user', 'system', 'scraper', 'api', 'import', 'migration', 'automated'
    )),
    CONSTRAINT chk_approval_status CHECK (approval_status IN (
        'pending', 'approved', 'rejected', 'auto_approved'
    )),
    CONSTRAINT chk_validity_period CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

-- Indexes for document_versions
CREATE INDEX idx_version_document ON document_versions(document_id);
CREATE INDEX idx_version_doc_num ON document_versions(document_id, version_number);
CREATE INDEX idx_version_current ON document_versions(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_version_type ON document_versions(change_type);
CREATE INDEX idx_version_created ON document_versions(created_at DESC);
CREATE INDEX idx_version_validity ON document_versions(valid_from, valid_to);
CREATE INDEX idx_version_approval ON document_versions(approval_status) WHERE requires_approval = TRUE;

-- GIN indexes for JSON fields
CREATE INDEX idx_version_fields ON document_versions USING GIN(changed_fields);
CREATE INDEX idx_version_snapshot ON document_versions USING GIN(snapshot_data);

-- Function to create new version
CREATE OR REPLACE FUNCTION create_document_version(
    p_document_id INTEGER,
    p_change_type VARCHAR,
    p_change_description TEXT,
    p_changed_fields JSONB DEFAULT '[]'::jsonb,
    p_created_by VARCHAR DEFAULT 'system'
)
RETURNS INTEGER AS $$
DECLARE
    v_version_number INTEGER;
    v_version_id INTEGER;
BEGIN
    -- Get next version number
    SELECT COALESCE(MAX(version_number), 0) + 1
    INTO v_version_number
    FROM document_versions
    WHERE document_id = p_document_id;

    -- Mark previous versions as not current
    UPDATE document_versions
    SET is_current = FALSE,
        valid_to = NOW()
    WHERE document_id = p_document_id
      AND is_current = TRUE;

    -- Insert new version
    INSERT INTO document_versions (
        document_id,
        version_number,
        change_type,
        change_description,
        changed_fields,
        created_by,
        created_by_type,
        is_current,
        valid_from
    ) VALUES (
        p_document_id,
        v_version_number,
        p_change_type,
        p_change_description,
        p_changed_fields,
        p_created_by,
        'system',
        TRUE,
        NOW()
    ) RETURNING id INTO v_version_id;

    RETURN v_version_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TABLE: sequence_tracker (ID Generation & Sequences)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sequence_tracker (
    id SERIAL PRIMARY KEY,

    -- Sequence Identification
    sequence_type VARCHAR(50) NOT NULL,      -- global_id, chunk_id, custom_seq
    country_code CHAR(2),                    -- BD, IN, PK (for country-specific sequences)
    doc_type VARCHAR(3),                     -- CAS, ACT, RUL (for type-specific sequences)
    year INTEGER,                            -- For yearly sequences

    -- Sequence Value
    last_value BIGINT NOT NULL DEFAULT 0,
    current_value BIGINT NOT NULL DEFAULT 0,
    increment_by INTEGER DEFAULT 1,
    min_value BIGINT DEFAULT 1,
    max_value BIGINT DEFAULT 9999999999,

    -- Sequence Properties
    is_active BOOLEAN DEFAULT TRUE,
    is_cyclic BOOLEAN DEFAULT FALSE,         -- Reset when max reached?
    cache_size INTEGER DEFAULT 1,            -- How many to cache in memory

    -- Usage Statistics
    total_generated BIGINT DEFAULT 0,
    last_generated_at TIMESTAMP,
    generation_count_today INTEGER DEFAULT 0,
    last_reset_at TIMESTAMP,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    description TEXT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_sequence UNIQUE(sequence_type, country_code, doc_type, year),
    CONSTRAINT chk_increment CHECK (increment_by > 0),
    CONSTRAINT chk_values CHECK (current_value >= min_value AND current_value <= max_value)
);

-- Indexes for sequence_tracker
CREATE INDEX idx_seq_type ON sequence_tracker(sequence_type);
CREATE INDEX idx_seq_country ON sequence_tracker(country_code) WHERE country_code IS NOT NULL;
CREATE INDEX idx_seq_doctype ON sequence_tracker(doc_type) WHERE doc_type IS NOT NULL;
CREATE INDEX idx_seq_year ON sequence_tracker(year) WHERE year IS NOT NULL;
CREATE INDEX idx_seq_active ON sequence_tracker(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_seq_composite ON sequence_tracker(sequence_type, country_code, doc_type, year);

CREATE TRIGGER trigger_sequence_tracker_updated_at
    BEFORE UPDATE ON sequence_tracker
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to get next sequence value
CREATE OR REPLACE FUNCTION get_next_sequence(
    p_sequence_type VARCHAR,
    p_country_code CHAR(2) DEFAULT NULL,
    p_doc_type VARCHAR DEFAULT NULL,
    p_year INTEGER DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_next_value BIGINT;
BEGIN
    -- Get and increment sequence
    UPDATE sequence_tracker
    SET
        current_value = current_value + increment_by,
        last_value = current_value,
        total_generated = total_generated + 1,
        last_generated_at = NOW(),
        generation_count_today = generation_count_today + 1
    WHERE sequence_type = p_sequence_type
      AND (country_code = p_country_code OR (country_code IS NULL AND p_country_code IS NULL))
      AND (doc_type = p_doc_type OR (doc_type IS NULL AND p_doc_type IS NULL))
      AND (year = p_year OR (year IS NULL AND p_year IS NULL))
      AND is_active = TRUE
    RETURNING current_value INTO v_next_value;

    -- If sequence doesn't exist, create it
    IF v_next_value IS NULL THEN
        INSERT INTO sequence_tracker (
            sequence_type,
            country_code,
            doc_type,
            year,
            current_value,
            last_value,
            total_generated,
            last_generated_at
        ) VALUES (
            p_sequence_type,
            p_country_code,
            p_doc_type,
            p_year,
            1,
            1,
            1,
            NOW()
        ) RETURNING current_value INTO v_next_value;
    END IF;

    RETURN v_next_value;
END;
$$ LANGUAGE plpgsql;

-- Function to generate global_id (Phase 1 integration)
CREATE OR REPLACE FUNCTION generate_global_id(
    p_country_code CHAR(2) DEFAULT 'BD'
)
RETURNS VARCHAR(10) AS $$
DECLARE
    v_sequence BIGINT;
    v_global_id VARCHAR(10);
BEGIN
    -- Get next sequence for this country
    v_sequence := get_next_sequence('global_id', p_country_code);

    -- Format as: CC + 8-digit sequence (e.g., BD00000001)
    v_global_id := p_country_code || LPAD(v_sequence::TEXT, 8, '0');

    RETURN v_global_id;
END;
$$ LANGUAGE plpgsql;

-- Function to reset daily counters (call from cron/scheduler)
CREATE OR REPLACE FUNCTION reset_daily_sequence_counters()
RETURNS INTEGER AS $$
DECLARE
    v_reset_count INTEGER;
BEGIN
    UPDATE sequence_tracker
    SET generation_count_today = 0
    WHERE generation_count_today > 0;

    GET DIAGNOSTICS v_reset_count = ROW_COUNT;

    RETURN v_reset_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Document version history
CREATE OR REPLACE VIEW v_document_version_history AS
SELECT
    d.id AS document_id,
    d.global_id,
    d.title_full,
    v.version_number,
    v.change_type,
    v.change_description,
    v.created_by,
    v.created_at,
    v.is_current,
    v.valid_from,
    v.valid_to,
    CASE
        WHEN v.is_current THEN 'Current'
        WHEN v.valid_to IS NOT NULL THEN 'Historical'
        ELSE 'Draft'
    END AS version_status
FROM documents d
INNER JOIN document_versions v ON d.id = v.document_id
ORDER BY d.id, v.version_number DESC;

-- View: Version change frequency
CREATE OR REPLACE VIEW v_version_change_frequency AS
SELECT
    document_id,
    COUNT(*) AS total_versions,
    MIN(created_at) AS first_version_date,
    MAX(created_at) AS last_version_date,
    COUNT(CASE WHEN change_type = 'content' THEN 1 END) AS content_changes,
    COUNT(CASE WHEN change_type = 'metadata' THEN 1 END) AS metadata_changes,
    COUNT(CASE WHEN change_type = 'pdf' THEN 1 END) AS pdf_changes,
    COUNT(DISTINCT created_by) AS unique_editors
FROM document_versions
GROUP BY document_id
HAVING COUNT(*) > 1;

-- View: Sequence usage statistics
CREATE OR REPLACE VIEW v_sequence_stats AS
SELECT
    sequence_type,
    country_code,
    doc_type,
    year,
    current_value,
    total_generated,
    generation_count_today,
    last_generated_at,
    ROUND((current_value::DECIMAL / max_value) * 100, 2) AS percent_used,
    max_value - current_value AS remaining_capacity
FROM sequence_tracker
WHERE is_active = TRUE
ORDER BY sequence_type, country_code, doc_type, year;

-- View: Recent version changes
CREATE OR REPLACE VIEW v_recent_version_changes AS
SELECT
    d.global_id,
    d.title_full,
    v.version_number,
    v.change_type,
    v.change_description,
    v.created_by,
    v.created_at
FROM document_versions v
INNER JOIN documents d ON v.document_id = d.id
WHERE v.created_at >= NOW() - INTERVAL '7 days'
ORDER BY v.created_at DESC
LIMIT 100;

-- Comments for documentation
COMMENT ON TABLE document_versions IS 'Version history and audit trail for document changes';
COMMENT ON COLUMN document_versions.snapshot_data IS 'JSONB snapshot of document state at this version';
COMMENT ON FUNCTION create_document_version IS 'Create new version and mark previous as not current';

COMMENT ON TABLE sequence_tracker IS 'Sequence generator for global_id and other auto-incrementing IDs';
COMMENT ON FUNCTION get_next_sequence IS 'Get next value from a sequence (thread-safe)';
COMMENT ON FUNCTION generate_global_id IS 'Generate Phase 1 global_id (e.g., BD00000001)';

COMMENT ON VIEW v_document_version_history IS 'Complete version history per document';
COMMENT ON VIEW v_version_change_frequency IS 'Documents with frequent changes';
COMMENT ON VIEW v_sequence_stats IS 'Sequence usage and capacity statistics';

SELECT 'Migration 006 completed: System tables and functions created' AS status;
