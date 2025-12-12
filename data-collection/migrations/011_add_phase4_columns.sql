-- ============================================================================
-- Phase 4 Migration: Add Phase 4 columns to existing tables
-- Adds Google Drive URLs, quality tracking, and performance fields
-- ============================================================================

-- Add columns to documents table if they don't exist
DO $$
BEGIN
    -- Google Drive fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='drive_file_id') THEN
        ALTER TABLE documents ADD COLUMN drive_file_id VARCHAR(255);
        CREATE INDEX idx_documents_drive_file_id ON documents(drive_file_id);
        RAISE NOTICE 'Added drive_file_id column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='drive_url') THEN
        ALTER TABLE documents ADD COLUMN drive_url TEXT;
        RAISE NOTICE 'Added drive_url column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='drive_tier') THEN
        ALTER TABLE documents ADD COLUMN drive_tier VARCHAR(10) DEFAULT 'HOT';
        CREATE INDEX idx_documents_drive_tier ON documents(drive_tier);
        RAISE NOTICE 'Added drive_tier column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='upload_verified') THEN
        ALTER TABLE documents ADD COLUMN upload_verified BOOLEAN DEFAULT FALSE;
        CREATE INDEX idx_documents_upload_verified ON documents(upload_verified);
        RAISE NOTICE 'Added upload_verified column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='uploaded_at') THEN
        ALTER TABLE documents ADD COLUMN uploaded_at TIMESTAMP;
        RAISE NOTICE 'Added uploaded_at column';
    END IF;

    -- Content hash for deduplication
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='content_hash') THEN
        ALTER TABLE documents ADD COLUMN content_hash VARCHAR(64);  -- SHA-256
        CREATE UNIQUE INDEX idx_documents_content_hash ON documents(content_hash) WHERE content_hash IS NOT NULL;
        RAISE NOTICE 'Added content_hash column with unique index';
    END IF;

    -- PDF metadata
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='pdf_size_bytes') THEN
        ALTER TABLE documents ADD COLUMN pdf_size_bytes BIGINT;
        RAISE NOTICE 'Added pdf_size_bytes column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='pdf_pages') THEN
        ALTER TABLE documents ADD COLUMN pdf_pages INTEGER;
        RAISE NOTICE 'Added pdf_pages column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='pdf_version') THEN
        ALTER TABLE documents ADD COLUMN pdf_version VARCHAR(10);
        RAISE NOTICE 'Added pdf_version column';
    END IF;

    -- Performance tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='download_time_ms') THEN
        ALTER TABLE documents ADD COLUMN download_time_ms INTEGER;
        RAISE NOTICE 'Added download_time_ms column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='extraction_time_ms') THEN
        ALTER TABLE documents ADD COLUMN extraction_time_ms INTEGER;
        RAISE NOTICE 'Added extraction_time_ms column';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='total_processing_time_ms') THEN
        ALTER TABLE documents ADD COLUMN total_processing_time_ms INTEGER;
        RAISE NOTICE 'Added total_processing_time_ms column';
    END IF;

    -- Proxy tracking (which proxy was used)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='proxy_id') THEN
        ALTER TABLE documents ADD COLUMN proxy_id VARCHAR(50);
        CREATE INDEX idx_documents_proxy_id ON documents(proxy_id);
        RAISE NOTICE 'Added proxy_id column';
    END IF;

    -- Quality score (denormalized for fast filtering)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='quality_score') THEN
        ALTER TABLE documents ADD COLUMN quality_score FLOAT;
        CREATE INDEX idx_documents_quality_score ON documents(quality_score);
        RAISE NOTICE 'Added quality_score column';
    END IF;

    -- Worker/thread that processed this document
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='worker_id') THEN
        ALTER TABLE documents ADD COLUMN worker_id INTEGER;
        RAISE NOTICE 'Added worker_id column';
    END IF;

END $$;

-- Add comments
COMMENT ON COLUMN documents.drive_file_id IS 'Google Drive file ID';
COMMENT ON COLUMN documents.drive_url IS 'Public Google Drive URL';
COMMENT ON COLUMN documents.drive_tier IS 'Storage tier: HOT, WARM, or COLD';
COMMENT ON COLUMN documents.upload_verified IS 'Whether Drive upload was verified';
COMMENT ON COLUMN documents.content_hash IS 'SHA-256 hash of PDF content for deduplication';
COMMENT ON COLUMN documents.pdf_size_bytes IS 'PDF file size in bytes';
COMMENT ON COLUMN documents.pdf_pages IS 'Number of pages in PDF';
COMMENT ON COLUMN documents.quality_score IS 'Overall quality score (0.0-1.0) from quality_scores table';
COMMENT ON COLUMN documents.proxy_id IS 'Proxy server ID used for download';
COMMENT ON COLUMN documents.worker_id IS 'Worker thread/process ID that processed this document';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Phase 4 columns added successfully to documents table';
END $$;
