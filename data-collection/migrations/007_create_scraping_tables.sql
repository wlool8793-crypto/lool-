-- Migration 007: Scraping Tables
-- Creates: scrape_sources, scrape_jobs
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- TABLE: scrape_sources (Source Website Configurations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS scrape_sources (
    id SERIAL PRIMARY KEY,

    -- Source Identification
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_domain VARCHAR(100) NOT NULL,
    source_short_name VARCHAR(20),

    -- Geographic/Jurisdiction
    country_code CHAR(2) NOT NULL,
    jurisdiction_level VARCHAR(20),          -- national, state, district, international

    -- URLs
    base_url TEXT NOT NULL,
    search_url TEXT,
    api_endpoint TEXT,

    -- Scraper Configuration
    scraper_class VARCHAR(100),              -- Python class name
    scraper_version VARCHAR(20),
    scraper_type VARCHAR(20),                -- html, api, pdf_direct, selenium

    -- Status & Priority
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,              -- Higher = scrape first
    scraping_frequency VARCHAR(20),          -- daily, weekly, monthly, manual

    -- Capabilities
    has_search BOOLEAN DEFAULT FALSE,
    has_pagination BOOLEAN DEFAULT FALSE,
    has_api BOOLEAN DEFAULT FALSE,
    has_pdf_download BOOLEAN DEFAULT FALSE,
    has_bulk_download BOOLEAN DEFAULT FALSE,

    -- Rate Limiting
    rate_limit_requests_per_minute INTEGER DEFAULT 60,
    rate_limit_delay_seconds DECIMAL(5,2) DEFAULT 1.0,
    concurrent_connections INTEGER DEFAULT 1,

    -- Authentication
    requires_auth BOOLEAN DEFAULT FALSE,
    auth_type VARCHAR(20),                   -- none, api_key, oauth, session, cookies
    auth_config JSONB,                       -- Encrypted credentials

    -- Statistics
    last_scraped_at TIMESTAMP,
    last_successful_scrape TIMESTAMP,
    last_failed_scrape TIMESTAMP,
    total_documents INTEGER DEFAULT 0,
    total_successful_scrapes INTEGER DEFAULT 0,
    total_failed_scrapes INTEGER DEFAULT 0,

    -- Health Monitoring
    health_status VARCHAR(20) DEFAULT 'unknown',  -- healthy, degraded, down, unknown
    health_check_url TEXT,
    last_health_check TIMESTAMP,
    consecutive_failures INTEGER DEFAULT 0,

    -- Document Type Support
    supported_doc_types JSONB DEFAULT '[]'::jsonb,  -- ["CAS", "ACT", "RUL"]

    -- Scraper Configuration (JSON)
    config JSONB DEFAULT '{}'::jsonb,        -- Scraper-specific settings
    selectors JSONB DEFAULT '{}'::jsonb,     -- CSS/XPath selectors
    pagination_config JSONB DEFAULT '{}'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    description TEXT,
    notes TEXT,

    -- Contact & Support
    website_contact_email VARCHAR(200),
    robots_txt_url TEXT,
    terms_of_service_url TEXT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_priority CHECK (priority >= 0 AND priority <= 100),
    CONSTRAINT chk_scraper_type CHECK (scraper_type IN (
        'html', 'api', 'pdf_direct', 'selenium', 'playwright', 'requests', 'scrapy'
    )),
    CONSTRAINT chk_health_status CHECK (health_status IN (
        'healthy', 'degraded', 'down', 'unknown', 'maintenance'
    )),
    CONSTRAINT chk_scraping_frequency CHECK (scraping_frequency IN (
        'realtime', 'hourly', 'daily', 'weekly', 'monthly', 'manual', 'on_demand'
    ))
);

-- Indexes for scrape_sources
CREATE INDEX idx_source_domain ON scrape_sources(source_domain);
CREATE INDEX idx_source_country ON scrape_sources(country_code);
CREATE INDEX idx_source_active ON scrape_sources(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_source_priority ON scrape_sources(priority DESC) WHERE is_active = TRUE;
CREATE INDEX idx_source_health ON scrape_sources(health_status);
CREATE INDEX idx_source_frequency ON scrape_sources(scraping_frequency);

-- GIN indexes for JSON fields
CREATE INDEX idx_source_config ON scrape_sources USING GIN(config);
CREATE INDEX idx_source_doc_types ON scrape_sources USING GIN(supported_doc_types);

CREATE TRIGGER trigger_scrape_sources_updated_at
    BEFORE UPDATE ON scrape_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TABLE: scrape_jobs (Scraping Job Tracking & History)
-- ============================================================================
CREATE TABLE IF NOT EXISTS scrape_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,

    -- Source Reference
    source_id INTEGER REFERENCES scrape_sources(id) ON DELETE SET NULL,
    source_name VARCHAR(100),                -- Denormalized for history

    -- Job Configuration
    job_type VARCHAR(20) NOT NULL,           -- full, incremental, retry, test, manual
    job_mode VARCHAR(20) DEFAULT 'normal',   -- normal, fast, thorough, test

    -- Scope
    start_page INTEGER DEFAULT 1,
    end_page INTEGER,
    max_documents INTEGER,
    start_date DATE,
    end_date DATE,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed, cancelled, paused
    status_message TEXT,

    -- Progress Tracking
    total_urls INTEGER DEFAULT 0,
    urls_processed INTEGER DEFAULT 0,
    urls_pending INTEGER DEFAULT 0,
    urls_skipped INTEGER DEFAULT 0,

    -- Results
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    downloaded_pdfs INTEGER DEFAULT 0,

    -- Document IDs Created
    document_ids_created JSONB DEFAULT '[]'::jsonb,  -- Array of document IDs

    -- Performance Metrics
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    paused_at TIMESTAMP,
    resumed_at TIMESTAMP,
    duration_seconds INTEGER,
    avg_time_per_document DECIMAL(10,2),

    -- Resource Usage
    requests_made INTEGER DEFAULT 0,
    bytes_downloaded BIGINT DEFAULT 0,
    pdfs_downloaded INTEGER DEFAULT 0,

    -- Error Tracking
    error_message TEXT,
    error_traceback TEXT,
    error_count_by_type JSONB DEFAULT '{}'::jsonb,  -- {"404": 5, "timeout": 3}
    failed_urls JSONB DEFAULT '[]'::jsonb,

    -- Retry Information
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    parent_job_id UUID REFERENCES scrape_jobs(job_id),

    -- Checkpoint/Resume
    checkpoint_data JSONB,                   -- State for resuming
    last_checkpoint_at TIMESTAMP,
    is_resumable BOOLEAN DEFAULT TRUE,

    -- Configuration Snapshot
    config_snapshot JSONB,                   -- Scraper config at run time

    -- Execution Context
    executed_by VARCHAR(100),                -- user ID, system, cron
    execution_node VARCHAR(100),             -- Which server/pod ran this
    execution_environment VARCHAR(20),       -- dev, staging, production

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_job_type CHECK (job_type IN (
        'full', 'incremental', 'retry', 'test', 'manual', 'scheduled', 'emergency'
    )),
    CONSTRAINT chk_job_status CHECK (status IN (
        'pending', 'queued', 'running', 'completed', 'failed', 'cancelled', 'paused', 'timeout'
    )),
    CONSTRAINT chk_progress CHECK (
        urls_processed >= 0 AND
        success_count >= 0 AND
        error_count >= 0 AND
        urls_processed = success_count + error_count + urls_skipped + duplicate_count
    )
);

-- Indexes for scrape_jobs
CREATE INDEX idx_job_id ON scrape_jobs(job_id);
CREATE INDEX idx_job_source ON scrape_jobs(source_id) WHERE source_id IS NOT NULL;
CREATE INDEX idx_job_status ON scrape_jobs(status);
CREATE INDEX idx_job_type ON scrape_jobs(job_type);
CREATE INDEX idx_job_created ON scrape_jobs(created_at DESC);
CREATE INDEX idx_job_running ON scrape_jobs(status, started_at) WHERE status = 'running';
CREATE INDEX idx_job_parent ON scrape_jobs(parent_job_id) WHERE parent_job_id IS NOT NULL;
CREATE INDEX idx_job_completion ON scrape_jobs(completed_at DESC) WHERE completed_at IS NOT NULL;

-- GIN indexes for JSON fields
CREATE INDEX idx_job_checkpoint ON scrape_jobs USING GIN(checkpoint_data);
CREATE INDEX idx_job_doc_ids ON scrape_jobs USING GIN(document_ids_created);

-- Composite index for active job queries
CREATE INDEX idx_job_active ON scrape_jobs(source_id, status, created_at) WHERE status IN ('pending', 'running', 'paused');

CREATE TRIGGER trigger_scrape_jobs_updated_at
    BEFORE UPDATE ON scrape_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to start a scraping job
CREATE OR REPLACE FUNCTION start_scrape_job(
    p_source_id INTEGER,
    p_job_type VARCHAR DEFAULT 'incremental'
)
RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
BEGIN
    INSERT INTO scrape_jobs (
        source_id,
        source_name,
        job_type,
        status,
        started_at
    )
    SELECT
        id,
        source_name,
        p_job_type,
        'running',
        NOW()
    FROM scrape_sources
    WHERE id = p_source_id
    RETURNING job_id INTO v_job_id;

    -- Update source last_scraped_at
    UPDATE scrape_sources
    SET last_scraped_at = NOW()
    WHERE id = p_source_id;

    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

-- Function to complete a scraping job
CREATE OR REPLACE FUNCTION complete_scrape_job(
    p_job_id UUID,
    p_status VARCHAR DEFAULT 'completed',
    p_success_count INTEGER DEFAULT 0,
    p_error_count INTEGER DEFAULT 0
)
RETURNS VOID AS $$
DECLARE
    v_source_id INTEGER;
    v_started_at TIMESTAMP;
BEGIN
    -- Get source_id and started_at
    SELECT source_id, started_at
    INTO v_source_id, v_started_at
    FROM scrape_jobs
    WHERE job_id = p_job_id;

    -- Update job
    UPDATE scrape_jobs
    SET
        status = p_status,
        completed_at = NOW(),
        duration_seconds = EXTRACT(EPOCH FROM (NOW() - v_started_at))::INTEGER,
        success_count = p_success_count,
        error_count = p_error_count,
        urls_processed = p_success_count + p_error_count
    WHERE job_id = p_job_id;

    -- Update source statistics
    IF v_source_id IS NOT NULL THEN
        UPDATE scrape_sources
        SET
            last_successful_scrape = CASE WHEN p_status = 'completed' THEN NOW() ELSE last_successful_scrape END,
            last_failed_scrape = CASE WHEN p_status = 'failed' THEN NOW() ELSE last_failed_scrape END,
            total_successful_scrapes = total_successful_scrapes + CASE WHEN p_status = 'completed' THEN 1 ELSE 0 END,
            total_failed_scrapes = total_failed_scrapes + CASE WHEN p_status = 'failed' THEN 1 ELSE 0 END,
            consecutive_failures = CASE
                WHEN p_status = 'completed' THEN 0
                WHEN p_status = 'failed' THEN consecutive_failures + 1
                ELSE consecutive_failures
            END,
            health_status = CASE
                WHEN p_status = 'completed' THEN 'healthy'
                WHEN consecutive_failures + 1 >= 3 THEN 'down'
                WHEN consecutive_failures + 1 = 2 THEN 'degraded'
                ELSE health_status
            END
        WHERE id = v_source_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Active scraping sources
CREATE OR REPLACE VIEW v_active_scrape_sources AS
SELECT
    s.*,
    COUNT(j.id) AS total_jobs,
    MAX(j.completed_at) AS last_job_completed,
    CASE
        WHEN s.consecutive_failures >= 3 THEN 'Critical'
        WHEN s.consecutive_failures = 2 THEN 'Warning'
        WHEN s.last_scraped_at < NOW() - INTERVAL '7 days' THEN 'Stale'
        ELSE 'OK'
    END AS status_flag
FROM scrape_sources s
LEFT JOIN scrape_jobs j ON s.id = j.source_id
WHERE s.is_active = TRUE
GROUP BY s.id
ORDER BY s.priority DESC, s.source_name;

-- View: Recent scraping jobs
CREATE OR REPLACE VIEW v_recent_scrape_jobs AS
SELECT
    j.job_id,
    j.source_name,
    j.job_type,
    j.status,
    j.urls_processed,
    j.success_count,
    j.error_count,
    j.started_at,
    j.completed_at,
    j.duration_seconds,
    CASE
        WHEN j.duration_seconds > 0 AND j.urls_processed > 0 THEN
            ROUND(j.urls_processed::DECIMAL / j.duration_seconds, 2)
        ELSE 0
    END AS docs_per_second
FROM scrape_jobs j
WHERE j.created_at >= NOW() - INTERVAL '7 days'
ORDER BY j.created_at DESC
LIMIT 100;

-- View: Scraping job statistics
CREATE OR REPLACE VIEW v_scrape_job_stats AS
SELECT
    s.source_name,
    s.country_code,
    COUNT(j.id) AS total_jobs,
    COUNT(CASE WHEN j.status = 'completed' THEN 1 END) AS completed_jobs,
    COUNT(CASE WHEN j.status = 'failed' THEN 1 END) AS failed_jobs,
    SUM(j.success_count) AS total_documents,
    AVG(j.duration_seconds) AS avg_duration_seconds,
    MAX(j.completed_at) AS last_completed
FROM scrape_sources s
LEFT JOIN scrape_jobs j ON s.id = j.source_id
GROUP BY s.id, s.source_name, s.country_code
ORDER BY total_documents DESC;

-- View: Currently running jobs
CREATE OR REPLACE VIEW v_running_scrape_jobs AS
SELECT
    j.job_id,
    j.source_name,
    j.job_type,
    j.started_at,
    EXTRACT(EPOCH FROM (NOW() - j.started_at))::INTEGER AS running_seconds,
    j.urls_processed,
    j.success_count,
    j.error_count,
    CASE
        WHEN EXTRACT(EPOCH FROM (NOW() - j.started_at)) > 3600 THEN 'Long Running'
        WHEN j.last_checkpoint_at < NOW() - INTERVAL '5 minutes' THEN 'Stalled'
        ELSE 'Normal'
    END AS job_health
FROM scrape_jobs j
WHERE j.status = 'running'
ORDER BY j.started_at;

-- Comments for documentation
COMMENT ON TABLE scrape_sources IS 'Configuration and metadata for legal document sources (62 Bangladesh sources + future countries)';
COMMENT ON COLUMN scrape_sources.config IS 'Scraper-specific configuration (selectors, pagination, etc.)';
COMMENT ON COLUMN scrape_sources.auth_config IS 'Authentication credentials (should be encrypted at application layer)';

COMMENT ON TABLE scrape_jobs IS 'Scraping job execution tracking with progress, errors, and performance metrics';
COMMENT ON COLUMN scrape_jobs.checkpoint_data IS 'Resume state for interrupted jobs';
COMMENT ON FUNCTION start_scrape_job IS 'Create and start a new scraping job';
COMMENT ON FUNCTION complete_scrape_job IS 'Mark job as completed and update source statistics';

COMMENT ON VIEW v_active_scrape_sources IS 'Active sources with health status';
COMMENT ON VIEW v_recent_scrape_jobs IS 'Recent scraping jobs with performance metrics';
COMMENT ON VIEW v_scrape_job_stats IS 'Aggregated statistics per source';
COMMENT ON VIEW v_running_scrape_jobs IS 'Currently executing jobs with health check';

SELECT 'Migration 007 completed: Scraping tables and functions created' AS status;
