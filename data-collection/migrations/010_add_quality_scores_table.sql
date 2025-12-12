-- ============================================================================
-- Phase 4 Migration: Add quality_scores table
-- Tracks quality gate results for each document
-- ============================================================================

-- Drop table if exists (for clean re-runs)
DROP TABLE IF EXISTS quality_scores CASCADE;

-- Create quality_scores table
CREATE TABLE quality_scores (
    id SERIAL PRIMARY KEY,

    -- Foreign key to documents table
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,

    -- Overall quality score (0.0 - 1.0)
    overall_score FLOAT NOT NULL,

    -- Phase 3 Quality Analyzer dimensions (5 dimensions)
    completeness_score FLOAT,
    citation_quality_score FLOAT,
    text_quality_score FLOAT,
    metadata_quality_score FLOAT,
    consistency_score FLOAT,

    -- Quality gate pass/fail tracking (8 gates)
    gate_1_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- HTTP response validation
    gate_2_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- PDF validation
    gate_3_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Text extraction quality
    gate_4_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Metadata confidence
    gate_5_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Overall quality score
    gate_6_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Schema validation
    gate_7_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Database transaction
    gate_8_passed BOOLEAN NOT NULL DEFAULT FALSE,  -- Drive upload verification

    -- Quality gate failure reasons (JSON for detailed diagnostics)
    gate_failures JSONB,

    -- Extraction metadata
    extraction_method VARCHAR(50),  -- 'pdfplumber', 'pypdf2', 'pdfminer', 'ocr'
    extraction_time_seconds FLOAT,
    ocr_used BOOLEAN DEFAULT FALSE,
    ocr_confidence FLOAT,

    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    initial_quality_score FLOAT,  -- Score before retries
    quality_improved BOOLEAN DEFAULT FALSE,  -- Did retry improve quality?

    -- Routing information
    quality_queue VARCHAR(20),  -- 'PRIORITY', 'NORMAL', 'LOW_PRIORITY', 'MANUAL_REVIEW'
    priority_level INTEGER,
    flagged_for_review BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX idx_quality_document ON quality_scores(document_id);
CREATE INDEX idx_quality_overall_score ON quality_scores(overall_score);
CREATE INDEX idx_quality_queue ON quality_scores(quality_queue);
CREATE INDEX idx_quality_flagged ON quality_scores(flagged_for_review);
CREATE INDEX idx_quality_created ON quality_scores(created_at);

-- Create partial indexes for specific quality ranges
CREATE INDEX idx_quality_excellent ON quality_scores(overall_score) WHERE overall_score >= 0.85;
CREATE INDEX idx_quality_good ON quality_scores(overall_score) WHERE overall_score >= 0.70 AND overall_score < 0.85;
CREATE INDEX idx_quality_poor ON quality_scores(overall_score) WHERE overall_score < 0.50;

-- Create index for failed gates
CREATE INDEX idx_quality_gates_failed ON quality_scores(gate_1_passed, gate_2_passed, gate_3_passed, gate_4_passed, gate_5_passed, gate_6_passed, gate_7_passed, gate_8_passed);

-- Create GIN index for JSONB gate_failures
CREATE INDEX idx_quality_failures_jsonb ON quality_scores USING GIN (gate_failures);

-- Add comment
COMMENT ON TABLE quality_scores IS 'Phase 4: Quality scores and quality gate tracking for each document';

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE quality_scores TO indiankanoon_user;
GRANT USAGE, SELECT ON SEQUENCE quality_scores_id_seq TO indiankanoon_user;

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_quality_scores_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER quality_scores_updated_at_trigger
BEFORE UPDATE ON quality_scores
FOR EACH ROW
EXECUTE FUNCTION update_quality_scores_updated_at();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Quality scores table created successfully';
END $$;
