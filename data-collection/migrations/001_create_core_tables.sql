-- Migration 001: Core Tables
-- Creates: documents, file_storage, parties
-- World-Class Legal RAG System - Phase 2

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ============================================================================
-- TABLE: documents (Main Document Metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    -- Primary Keys
    id SERIAL PRIMARY KEY,
    global_id VARCHAR(10) NOT NULL,          -- BD00000001 (Phase 1 naming)
    uuid UUID DEFAULT gen_random_uuid() NOT NULL,

    -- Naming Convention (Phase 1 Integration)
    filename_universal VARCHAR(150) NOT NULL, -- Complete Phase 1 filename
    content_hash CHAR(16) NOT NULL,          -- 16-char SHA-256 hash

    -- Document Classification
    country_code CHAR(2) NOT NULL,           -- BD, IN, PK, US, UK
    doc_type VARCHAR(3) NOT NULL,            -- CAS, ACT, RUL, ORD, ORN, TRE, CON
    doc_subtype VARCHAR(4),                  -- HCD, AD, SC, CTR, STA, FED

    -- Title & Identification
    title_full TEXT NOT NULL,
    title_short VARCHAR(500),
    title_alternate TEXT,
    doc_year INTEGER NOT NULL,
    doc_number VARCHAR(50),                  -- Act number, Rule number, etc.

    -- Subject Classification (Phase 1 Integration)
    subject_primary VARCHAR(3),              -- CRM, CIV, CON, PRO, etc.
    subject_secondary VARCHAR(3),
    subject_tags JSONB DEFAULT '[]'::jsonb,  -- ["keyword1", "keyword2"]

    -- Legal Status & Dates
    legal_status VARCHAR(3),                 -- ACT, REP, AMD, SUP, OVR, PND
    date_judgment DATE,
    date_enacted DATE,
    date_effective DATE,
    date_published DATE,
    date_last_amended DATE,
    date_repealed DATE,

    -- Source Information
    source_url TEXT NOT NULL,
    source_domain VARCHAR(100) NOT NULL,
    source_id VARCHAR(100),                  -- ID in source system
    source_database VARCHAR(100),

    -- Relationships
    parent_doc_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    supersedes_doc_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,

    -- RAG Metadata
    chunk_count INTEGER DEFAULT 0,
    chunk_strategy VARCHAR(20) DEFAULT 'semantic',  -- sentence, paragraph, semantic, hybrid
    embedding_model VARCHAR(50),             -- all-MiniLM-L6-v2, etc.
    embedding_status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    last_embedded_at TIMESTAMP,

    -- Statistics
    cited_by_count INTEGER DEFAULT 0,
    cites_count INTEGER DEFAULT 0,

    -- Data Quality
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score >= 0 AND data_quality_score <= 1),
    validation_status VARCHAR(20) DEFAULT 'pending',  -- pending, valid, invalid, needs_review
    validation_errors TEXT,
    manual_review_needed BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,      -- Flexible additional metadata

    -- Scraping Metadata
    scraper_name VARCHAR(100),
    scraper_version VARCHAR(20),
    scrape_timestamp TIMESTAMP,
    scrape_duration_ms INTEGER,

    -- Timestamps
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_global_id UNIQUE(global_id),
    CONSTRAINT uk_filename UNIQUE(filename_universal),
    CONSTRAINT uk_uuid UNIQUE(uuid),
    CONSTRAINT chk_doc_year CHECK (doc_year >= 1800 AND doc_year <= 2100),
    CONSTRAINT chk_country_code CHECK (country_code ~ '^[A-Z]{2}$'),
    CONSTRAINT chk_doc_type CHECK (doc_type IN ('CAS', 'ACT', 'RUL', 'ORD', 'ORN', 'TRE', 'CON', 'REG')),
    CONSTRAINT chk_embedding_status CHECK (embedding_status IN ('pending', 'processing', 'completed', 'failed', 'skipped'))
);

-- Indexes for documents table
CREATE INDEX idx_doc_global_id ON documents(global_id);
CREATE INDEX idx_doc_country_type ON documents(country_code, doc_type);
CREATE INDEX idx_doc_country_type_year ON documents(country_code, doc_type, doc_year);
CREATE INDEX idx_doc_year ON documents(doc_year);
CREATE INDEX idx_doc_subject ON documents(subject_primary) WHERE subject_primary IS NOT NULL;
CREATE INDEX idx_doc_source ON documents(source_domain);
CREATE INDEX idx_doc_status ON documents(legal_status) WHERE legal_status IS NOT NULL;
CREATE INDEX idx_doc_embedding_pending ON documents(embedding_status) WHERE embedding_status != 'completed';
CREATE INDEX idx_doc_quality ON documents(data_quality_score) WHERE data_quality_score IS NOT NULL;
CREATE INDEX idx_doc_created ON documents(created_at DESC);
CREATE INDEX idx_doc_metadata ON documents USING GIN(metadata);
CREATE INDEX idx_doc_subject_tags ON documents USING GIN(subject_tags);

-- Full-text search on title
CREATE INDEX idx_doc_title_fts ON documents USING GIN(to_tsvector('english', title_full));

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: file_storage (Multi-Tier PDF Storage Tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_storage (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL DEFAULT 1,

    -- Storage Locations
    storage_tier VARCHAR(20) NOT NULL,       -- 'drive', 'cache', 'both', 'none'

    -- Google Drive Storage
    drive_file_id VARCHAR(100),              -- Google Drive file ID
    drive_folder_path TEXT,                  -- /BD/CAS/1998/
    drive_web_link TEXT,                     -- Shareable link
    drive_md5_checksum VARCHAR(32),          -- Google Drive MD5

    -- Local Cache Storage
    local_cache_path VARCHAR(500),           -- /data/cache/BD00000001_...pdf
    cache_tier VARCHAR(20) DEFAULT 'cold',   -- 'hot', 'warm', 'cold'

    -- File Properties
    pdf_filename VARCHAR(150) NOT NULL,      -- Phase 1 generated filename
    pdf_hash_sha256 CHAR(64) NOT NULL,       -- Full 64-character SHA-256
    pdf_size_bytes BIGINT NOT NULL,
    pdf_pages INTEGER,

    -- Versioning
    is_current_version BOOLEAN DEFAULT TRUE,
    version_notes TEXT,
    replaced_by_version INTEGER,             -- Points to newer version
    supersedes_version INTEGER,              -- Points to older version

    -- Upload/Download Status
    upload_status VARCHAR(20) DEFAULT 'pending',  -- pending, uploading, completed, failed
    download_status VARCHAR(20),             -- pending, downloading, completed, failed
    uploaded_at TIMESTAMP,
    downloaded_at TIMESTAMP,

    -- Access Tracking
    download_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    cache_priority INTEGER DEFAULT 0,        -- Higher = keep in cache longer
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,

    -- Integrity Verification
    checksum_verified_at TIMESTAMP,
    checksum_match BOOLEAN,
    integrity_check_count INTEGER DEFAULT 0,

    -- Error Tracking
    upload_error TEXT,
    download_error TEXT,
    upload_attempts INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_version UNIQUE(document_id, version_number),
    CONSTRAINT chk_version_number CHECK (version_number > 0),
    CONSTRAINT chk_storage_tier CHECK (storage_tier IN ('drive', 'cache', 'both', 'none')),
    CONSTRAINT chk_upload_status CHECK (upload_status IN ('pending', 'uploading', 'completed', 'failed', 'skipped')),
    CONSTRAINT chk_cache_tier CHECK (cache_tier IN ('hot', 'warm', 'cold'))
);

-- Indexes for file_storage
CREATE INDEX idx_storage_document ON file_storage(document_id);
CREATE INDEX idx_storage_tier ON file_storage(storage_tier);
CREATE INDEX idx_storage_current ON file_storage(is_current_version) WHERE is_current_version = TRUE;
CREATE INDEX idx_storage_cache_priority ON file_storage(cache_priority DESC, last_accessed_at DESC);
CREATE INDEX idx_storage_drive_file ON file_storage(drive_file_id) WHERE drive_file_id IS NOT NULL;
CREATE INDEX idx_storage_upload_status ON file_storage(upload_status) WHERE upload_status != 'completed';
CREATE INDEX idx_storage_cache_path ON file_storage(local_cache_path) WHERE local_cache_path IS NOT NULL;
CREATE INDEX idx_storage_hash ON file_storage(pdf_hash_sha256);

-- Trigger for file_storage updated_at
CREATE TRIGGER trigger_file_storage_updated_at
    BEFORE UPDATE ON file_storage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: parties (Case Parties)
-- ============================================================================
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    -- Party Information
    party_type VARCHAR(20) NOT NULL,         -- petitioner, respondent, appellant, intervener, amicus
    party_name TEXT NOT NULL,
    party_name_abbr VARCHAR(50),             -- From Phase 1 PartyAbbreviator
    party_order INTEGER NOT NULL DEFAULT 1,  -- 1st petitioner, 2nd petitioner, etc.

    -- Legal Representation
    representation TEXT,                     -- Lawyer/law firm name
    lawyer_name VARCHAR(200),
    law_firm VARCHAR(200),

    -- Party Classification
    party_category VARCHAR(50),              -- individual, corporation, government, ngo
    party_identifier VARCHAR(100),           -- Tax ID, registration number, etc.

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_doc_party_type_order UNIQUE(document_id, party_type, party_order),
    CONSTRAINT chk_party_type CHECK (party_type IN ('petitioner', 'respondent', 'appellant', 'defendant', 'plaintiff', 'intervener', 'amicus_curiae', 'witness')),
    CONSTRAINT chk_party_order CHECK (party_order > 0)
);

-- Indexes for parties
CREATE INDEX idx_party_document ON parties(document_id);
CREATE INDEX idx_party_type ON parties(party_type);
CREATE INDEX idx_party_name ON parties USING GIN(to_tsvector('english', party_name));
CREATE INDEX idx_party_lawyer ON parties(lawyer_name) WHERE lawyer_name IS NOT NULL;

-- Comments for documentation
COMMENT ON TABLE documents IS 'Main document metadata table with Phase 1 naming integration';
COMMENT ON COLUMN documents.global_id IS 'Unique global identifier from Phase 1 naming (e.g., BD00000001)';
COMMENT ON COLUMN documents.filename_universal IS 'Complete Phase 1 generated filename';
COMMENT ON COLUMN documents.content_hash IS '16-character SHA-256 hash from Phase 1';

COMMENT ON TABLE file_storage IS 'Multi-tier PDF storage tracking (Google Drive + Local Cache)';
COMMENT ON COLUMN file_storage.storage_tier IS 'Current storage location: drive, cache, both, or none';
COMMENT ON COLUMN file_storage.cache_priority IS 'LRU cache priority (higher = keep longer)';

COMMENT ON TABLE parties IS 'Case parties with Phase 1 party name abbreviation integration';

-- Initial statistics
SELECT 'Migration 001 completed: Core tables created' AS status;
