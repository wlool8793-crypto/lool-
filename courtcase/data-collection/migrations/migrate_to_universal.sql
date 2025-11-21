-- ============================================================================
-- MIGRATION SCRIPT: Legacy to Universal Schema
-- ============================================================================
-- Description: Migrate existing legal_documents table to universal schema
-- Version: 1.0
-- Created: 2025-10-22
-- ============================================================================

-- This script migrates data from the legacy legal_documents table to the
-- new universal_legal_documents table with proper mapping and defaults.

-- ============================================================================
-- STEP 1: Backup existing data
-- ============================================================================

-- Create backup table
CREATE TABLE IF NOT EXISTS legal_documents_backup AS
SELECT * FROM legal_documents;

-- ============================================================================
-- STEP 2: Migrate data to universal schema
-- ============================================================================

INSERT OR IGNORE INTO universal_legal_documents (
    -- Country & Jurisdiction
    country_code,
    country_name,
    jurisdiction_level,

    -- Document Classification
    doc_category,
    doc_type,
    country_doc_id,
    doc_year,

    -- Titles
    title_full,
    title_short,

    -- Subject (basic mapping)
    subject_primary,

    -- Court/Authority Information
    court_name,
    judges,

    -- Ministry (for Bangladesh docs)
    issuing_authority,

    -- Citations
    citation_primary,

    -- Legal Status & Dates
    legal_status,
    date_effective,
    date_last_amended,

    -- Content
    html_content,
    plain_text,
    summary,

    -- PDF Information
    pdf_url,
    pdf_path,
    pdf_downloaded,
    pdf_size_bytes,
    pdf_hash_sha256,

    -- Source Information
    source_url,
    source_domain,
    source_index,

    -- Scraping Metadata
    scraper_name,
    scraper_version,
    scrape_timestamp,
    scrape_status,
    scrape_error,

    -- Global IDs (will be generated)
    global_id,
    uuid,

    -- Timestamps
    created_at,
    updated_at
)
SELECT
    -- Country & Jurisdiction mapping
    CASE
        WHEN country = 'india' THEN 'IN'
        WHEN country = 'bangladesh' THEN 'BD'
        WHEN country = 'pakistan' THEN 'PK'
        ELSE UPPER(SUBSTR(country, 1, 2))
    END as country_code,

    CASE
        WHEN country = 'india' THEN 'India'
        WHEN country = 'bangladesh' THEN 'Bangladesh'
        WHEN country = 'pakistan' THEN 'Pakistan'
        ELSE country
    END as country_name,

    'CENTRAL' as jurisdiction_level,

    -- Document Classification
    CASE
        WHEN doc_type IN ('case', 'Case') THEN 'CASE'
        WHEN doc_type IN ('act', 'Act') THEN 'ACT'
        WHEN doc_type IN ('ordinance', 'Ordinance') THEN 'ACT'
        WHEN doc_type IN ('rule', 'Rule', 'Regulation') THEN 'RULE'
        WHEN doc_type IN ('order', 'Order', 'Presidential Order') THEN 'ORDER'
        ELSE 'MISC'
    END as doc_category,

    doc_type as doc_type,
    country_doc_id,
    year as doc_year,

    -- Titles
    title as title_full,
    short_title,

    -- Subject (basic classification from category field)
    CASE
        WHEN LOWER(category) LIKE '%criminal%' THEN 'CRIMINAL'
        WHEN LOWER(category) LIKE '%civil%' THEN 'CIVIL'
        WHEN LOWER(category) LIKE '%constitution%' THEN 'CONSTITUTIONAL'
        WHEN LOWER(category) LIKE '%tax%' OR LOWER(category) LIKE '%revenue%' THEN 'TAX'
        WHEN LOWER(category) LIKE '%labor%' OR LOWER(category) LIKE '%labour%' THEN 'LABOR'
        WHEN LOWER(category) LIKE '%property%' THEN 'PROPERTY'
        WHEN LOWER(category) LIKE '%contract%' THEN 'CONTRACT'
        WHEN LOWER(category) LIKE '%environment%' THEN 'ENVIRONMENTAL'
        ELSE 'GENERAL'
    END as subject_primary,

    -- Court/Authority
    court_or_ministry as court_name,
    bench as judges,

    -- Ministry (for non-court docs)
    CASE
        WHEN doc_type NOT IN ('case', 'Case') THEN court_or_ministry
        ELSE NULL
    END as issuing_authority,

    -- Citations
    citation as citation_primary,

    -- Status & Dates
    COALESCE(UPPER(status), 'ACTIVE') as legal_status,
    effective_date as date_effective,
    last_amended_date as date_last_amended,

    -- Content
    html_content,
    plain_text,
    summary,

    -- PDF
    pdf_url,
    pdf_path,
    pdf_downloaded,
    pdf_size_kb * 1024 as pdf_size_bytes,  -- Convert KB to bytes
    pdf_hash as pdf_hash_sha256,

    -- Source
    source_url,
    source_site as source_domain,
    source_index,

    -- Scraping
    'legacy_scraper' as scraper_name,
    scraper_version,
    scraped_at as scrape_timestamp,
    scrape_status,
    error_message as scrape_error,

    -- Generate IDs (these will be updated by a Python script)
    'ULEGAL-' || printf('%010d', id) as global_id,
    lower(hex(randomblob(16))) as uuid,

    -- Timestamps
    scraped_at as created_at,
    updated_at

FROM legal_documents
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='legal_documents');

-- ============================================================================
-- STEP 3: Migrate document metadata
-- ============================================================================

INSERT OR IGNORE INTO document_metadata (
    document_id,
    metadata_key,
    metadata_value,
    metadata_type
)
SELECT
    (SELECT id FROM universal_legal_documents WHERE source_url = ld.source_url LIMIT 1) as document_id,
    dm.metadata_key,
    dm.metadata_value,
    dm.metadata_type
FROM legal_documents ld
JOIN document_metadata dm ON ld.id = dm.document_id
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='legal_documents');

-- ============================================================================
-- STEP 4: Update sequence tracker for migrated data
-- ============================================================================

-- Update global sequence
UPDATE sequence_tracker
SET last_value = (SELECT MAX(id) FROM universal_legal_documents)
WHERE sequence_type = 'GLOBAL';

-- Initialize yearly sequences for existing data
INSERT OR IGNORE INTO sequence_tracker (
    sequence_type,
    country_code,
    doc_category,
    year,
    last_value
)
SELECT DISTINCT
    'YEARLY' as sequence_type,
    country_code,
    doc_category,
    doc_year,
    COUNT(*) OVER (PARTITION BY country_code, doc_category, doc_year) as last_value
FROM universal_legal_documents
WHERE doc_year IS NOT NULL;

-- ============================================================================
-- STEP 5: Data quality checks
-- ============================================================================

-- Check for documents without global_id
SELECT COUNT(*) as missing_global_id
FROM universal_legal_documents
WHERE global_id IS NULL OR global_id = '';

-- Check for documents without uuid
SELECT COUNT(*) as missing_uuid
FROM universal_legal_documents
WHERE uuid IS NULL OR uuid = '';

-- Check for documents without country_code
SELECT COUNT(*) as missing_country_code
FROM universal_legal_documents
WHERE country_code IS NULL OR country_code = '';

-- ============================================================================
-- STEP 6: Summary report
-- ============================================================================

-- Migration summary
SELECT
    'MIGRATION SUMMARY' as report_type,
    (SELECT COUNT(*) FROM legal_documents_backup) as legacy_count,
    (SELECT COUNT(*) FROM universal_legal_documents) as universal_count,
    (SELECT COUNT(*) FROM universal_legal_documents) -
    (SELECT COUNT(*) FROM legal_documents_backup) as new_count;

-- By country
SELECT
    country_code,
    country_name,
    COUNT(*) as migrated_docs
FROM universal_legal_documents
GROUP BY country_code, country_name
ORDER BY migrated_docs DESC;

-- By category
SELECT
    doc_category,
    COUNT(*) as migrated_docs
FROM universal_legal_documents
GROUP BY doc_category
ORDER BY migrated_docs DESC;

-- ============================================================================
-- NOTES FOR MANUAL STEPS
-- ============================================================================

/*
IMPORTANT: After running this SQL migration, you MUST run the Python migration
utility to:

1. Generate proper global_id values (sequential ULEGAL-0000000001, etc.)
2. Generate proper UUID v4 values
3. Generate universal filenames
4. Calculate yearly sequences
5. Infer subjects from content
6. Generate subject codes
7. Calculate file paths
8. Update quality scores

Run: python -m src.utils.migrator

This will complete the migration and ensure all fields are properly populated.
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
