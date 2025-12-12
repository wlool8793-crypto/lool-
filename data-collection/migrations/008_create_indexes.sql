-- Migration 008: Additional Indexes & Performance Optimization
-- Creates composite indexes, partial indexes, and performance tuning
-- World-Class Legal RAG System - Phase 2

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- ============================================================================

-- Document search by country, type, year, subject
CREATE INDEX IF NOT EXISTS idx_doc_search_combo
ON documents(country_code, doc_type, doc_year, subject_primary)
WHERE legal_status = 'ACT';

-- Document search by status and dates
CREATE INDEX IF NOT EXISTS idx_doc_status_dates
ON documents(legal_status, date_judgment, date_enacted);

-- Citation lookup (reporter + year + page)
CREATE INDEX IF NOT EXISTS idx_citation_lookup
ON citations(reporter, year, page)
WHERE is_primary = TRUE;

-- Legal references network analysis
CREATE INDEX IF NOT EXISTS idx_ref_network
ON legal_references(citing_doc_id, cited_doc_id, reference_type)
WHERE is_resolved = TRUE;

-- Chunk retrieval for RAG
CREATE INDEX IF NOT EXISTS idx_chunk_rag_retrieval
ON document_chunks(document_id, embedding_status, chunk_quality_score)
WHERE embedding_status = 'completed' AND has_meaningful_content = TRUE;

-- File storage multi-tier lookup
CREATE INDEX IF NOT EXISTS idx_storage_multi_tier
ON file_storage(document_id, version_number, is_current_version, storage_tier);

-- ============================================================================
-- PARTIAL INDEXES FOR FILTERED QUERIES
-- ============================================================================

-- Documents pending embedding
CREATE INDEX IF NOT EXISTS idx_doc_pending_embedding
ON documents(id, chunk_count)
WHERE embedding_status IN ('pending', 'failed');

-- High-quality documents for RAG
CREATE INDEX IF NOT EXISTS idx_doc_high_quality
ON documents(id, global_id, doc_type)
WHERE data_quality_score >= 0.8 AND validation_status = 'valid';

-- Recently updated documents
CREATE INDEX IF NOT EXISTS idx_doc_recent_updates
ON documents(updated_at DESC)
WHERE updated_at >= NOW() - INTERVAL '30 days';

-- Unresolved legal references (for citation matching)
CREATE INDEX IF NOT EXISTS idx_ref_unresolved
ON legal_references(citation_text, external_citation)
WHERE is_resolved = FALSE;

-- Pending file uploads to Google Drive
CREATE INDEX IF NOT EXISTS idx_storage_pending_upload
ON file_storage(id, document_id, pdf_filename)
WHERE upload_status IN ('pending', 'failed') AND storage_tier IN ('none', 'cache');

-- Failed chunks (for retry)
CREATE INDEX IF NOT EXISTS idx_chunk_failed
ON document_chunks(document_id, chunk_index)
WHERE embedding_status = 'failed';

-- Documents needing manual review
CREATE INDEX IF NOT EXISTS idx_doc_manual_review
ON documents(id, global_id, title_full)
WHERE manual_review_needed = TRUE;

-- ============================================================================
-- COVERING INDEXES (Include columns for index-only scans)
-- ============================================================================

-- Document list with basic info (avoid table lookups)
CREATE INDEX IF NOT EXISTS idx_doc_list_covering
ON documents(country_code, doc_type, doc_year)
INCLUDE (global_id, title_short, subject_primary, legal_status);

-- Citation display (avoid content table lookup)
CREATE INDEX IF NOT EXISTS idx_citation_display_covering
ON citations(document_id)
INCLUDE (citation_display, citation_encoded, reporter, year)
WHERE is_primary = TRUE;

-- File storage current version (avoid multiple lookups)
CREATE INDEX IF NOT EXISTS idx_storage_current_covering
ON file_storage(document_id)
INCLUDE (pdf_filename, drive_file_id, local_cache_path, pdf_size_bytes)
WHERE is_current_version = TRUE;

-- ============================================================================
-- EXPRESSION INDEXES
-- ============================================================================

-- Lowercase title search
CREATE INDEX IF NOT EXISTS idx_doc_title_lower
ON documents(LOWER(title_full));

-- Year extraction from dates
CREATE INDEX IF NOT EXISTS idx_doc_judgment_year
ON documents(EXTRACT(YEAR FROM date_judgment))
WHERE date_judgment IS NOT NULL;

-- Document age (for prioritization)
CREATE INDEX IF NOT EXISTS idx_doc_age
ON documents((NOW() - scraped_at))
WHERE scraped_at IS NOT NULL;

-- ============================================================================
-- TEXT SEARCH INDEXES (Additional FTS)
-- ============================================================================

-- Party name fuzzy search
CREATE INDEX IF NOT EXISTS idx_party_name_trgm
ON parties USING GIN(party_name gin_trgm_ops);

-- Judge name fuzzy search
CREATE INDEX IF NOT EXISTS idx_judge_name_trgm
ON judges USING GIN(judge_name gin_trgm_ops);

-- Act name fuzzy search
CREATE INDEX IF NOT EXISTS idx_section_act_trgm
ON sections_cited USING GIN(act_name gin_trgm_ops);

-- Source domain fuzzy search
CREATE INDEX IF NOT EXISTS idx_source_domain_trgm
ON scrape_sources USING GIN(source_domain gin_trgm_ops);

-- ============================================================================
-- BTREE INDEXES FOR SORTING
-- ============================================================================

-- Most cited documents (by citation count)
CREATE INDEX IF NOT EXISTS idx_doc_cited_count
ON documents(cited_by_count DESC NULLS LAST)
WHERE cited_by_count > 0;

-- Document quality score
CREATE INDEX IF NOT EXISTS idx_doc_quality_desc
ON documents(data_quality_score DESC NULLS LAST)
WHERE data_quality_score IS NOT NULL;

-- Scrape job completion time
CREATE INDEX IF NOT EXISTS idx_job_duration
ON scrape_jobs(duration_seconds DESC NULLS LAST)
WHERE status = 'completed';

-- ============================================================================
-- FOREIGN KEY INDEXES (If not already created)
-- ============================================================================

-- Ensure all foreign keys have indexes for join performance
CREATE INDEX IF NOT EXISTS idx_content_doc_fk ON content(document_id);
CREATE INDEX IF NOT EXISTS idx_parties_doc_fk ON parties(document_id);
CREATE INDEX IF NOT EXISTS idx_judges_doc_fk ON judges(document_id);
CREATE INDEX IF NOT EXISTS idx_citations_doc_fk ON citations(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_fk ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_refs_citing_fk ON legal_references(citing_doc_id);
CREATE INDEX IF NOT EXISTS idx_refs_cited_fk ON legal_references(cited_doc_id);
CREATE INDEX IF NOT EXISTS idx_sections_doc_fk ON sections_cited(document_id);
CREATE INDEX IF NOT EXISTS idx_keywords_doc_fk ON keywords(document_id);
CREATE INDEX IF NOT EXISTS idx_amendments_base_fk ON amendments(base_doc_id);
CREATE INDEX IF NOT EXISTS idx_translations_doc_fk ON translations(document_id);
CREATE INDEX IF NOT EXISTS idx_metadata_doc_fk ON document_metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_versions_doc_fk ON document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_storage_doc_fk ON file_storage(document_id);
CREATE INDEX IF NOT EXISTS idx_jobs_source_fk ON scrape_jobs(source_id);

-- ============================================================================
-- STATISTICS UPDATES
-- ============================================================================

-- Increase statistics target for frequently queried columns
ALTER TABLE documents ALTER COLUMN country_code SET STATISTICS 1000;
ALTER TABLE documents ALTER COLUMN doc_type SET STATISTICS 1000;
ALTER TABLE documents ALTER COLUMN doc_year SET STATISTICS 1000;
ALTER TABLE documents ALTER COLUMN subject_primary SET STATISTICS 500;
ALTER TABLE citations ALTER COLUMN reporter SET STATISTICS 500;
ALTER TABLE document_chunks ALTER COLUMN embedding_status SET STATISTICS 500;

-- ============================================================================
-- VACUUM AND ANALYZE
-- ============================================================================

-- Ensure statistics are up to date
ANALYZE documents;
ANALYZE file_storage;
ANALYZE content;
ANALYZE citations;
ANALYZE document_chunks;
ANALYZE legal_references;
ANALYZE parties;
ANALYZE judges;

-- ============================================================================
-- MATERIALIZED VIEWS FOR EXPENSIVE QUERIES
-- ============================================================================

-- Materialized view: Document statistics (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_document_statistics AS
SELECT
    country_code,
    doc_type,
    doc_year,
    COUNT(*) AS document_count,
    COUNT(CASE WHEN embedding_status = 'completed' THEN 1 END) AS embedded_count,
    AVG(data_quality_score) AS avg_quality_score,
    AVG(chunk_count) AS avg_chunk_count,
    AVG(cited_by_count) AS avg_cited_by_count
FROM documents
GROUP BY country_code, doc_type, doc_year;

CREATE UNIQUE INDEX idx_mv_doc_stats ON mv_document_statistics(country_code, doc_type, doc_year);

-- Materialized view: Citation network metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_citation_network AS
SELECT
    d.id AS document_id,
    d.global_id,
    d.title_full,
    c.citation_display,
    COUNT(DISTINCT lr_out.cited_doc_id) AS outgoing_citations,
    COUNT(DISTINCT lr_in.citing_doc_id) AS incoming_citations,
    COUNT(DISTINCT lr_out.cited_doc_id) + COUNT(DISTINCT lr_in.citing_doc_id) AS total_connections
FROM documents d
LEFT JOIN citations c ON d.id = c.document_id AND c.is_primary = TRUE
LEFT JOIN legal_references lr_out ON d.id = lr_out.citing_doc_id
LEFT JOIN legal_references lr_in ON d.id = lr_in.cited_doc_id
GROUP BY d.id, d.global_id, d.title_full, c.citation_display;

CREATE UNIQUE INDEX idx_mv_citation_net ON mv_citation_network(document_id);
CREATE INDEX idx_mv_citation_net_connections ON mv_citation_network(total_connections DESC);

-- Materialized view: RAG readiness
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_rag_readiness AS
SELECT
    d.id,
    d.global_id,
    d.country_code,
    d.doc_type,
    d.chunk_count,
    COUNT(dc.id) AS total_chunks,
    COUNT(CASE WHEN dc.embedding_status = 'completed' THEN 1 END) AS embedded_chunks,
    CASE
        WHEN COUNT(dc.id) = 0 THEN 'no_chunks'
        WHEN COUNT(CASE WHEN dc.embedding_status = 'completed' THEN 1 END) = 0 THEN 'not_embedded'
        WHEN COUNT(CASE WHEN dc.embedding_status = 'completed' THEN 1 END) < COUNT(dc.id) THEN 'partially_embedded'
        ELSE 'ready'
    END AS rag_status
FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
GROUP BY d.id, d.global_id, d.country_code, d.doc_type, d.chunk_count;

CREATE UNIQUE INDEX idx_mv_rag_readiness ON mv_rag_readiness(id);
CREATE INDEX idx_mv_rag_status ON mv_rag_readiness(rag_status);

-- ============================================================================
-- REFRESH FUNCTIONS FOR MATERIALIZED VIEWS
-- ============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS TEXT AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_end_time TIMESTAMP;
    v_duration INTERVAL;
BEGIN
    v_start_time := clock_timestamp();

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_document_statistics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_citation_network;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rag_readiness;

    v_end_time := clock_timestamp();
    v_duration := v_end_time - v_start_time;

    RETURN 'All materialized views refreshed in ' || v_duration;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEX MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to reindex all tables (run during low traffic)
CREATE OR REPLACE FUNCTION reindex_all_tables()
RETURNS TEXT AS $$
DECLARE
    v_table RECORD;
    v_count INTEGER := 0;
BEGIN
    FOR v_table IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    LOOP
        EXECUTE 'REINDEX TABLE ' || quote_ident(v_table.tablename);
        v_count := v_count + 1;
    END LOOP;

    RETURN 'Reindexed ' || v_count || ' tables';
END;
$$ LANGUAGE plpgsql;

-- Function to show index usage statistics
CREATE OR REPLACE FUNCTION show_index_usage()
RETURNS TABLE (
    schemaname TEXT,
    tablename TEXT,
    indexname TEXT,
    idx_scan BIGINT,
    idx_tup_read BIGINT,
    idx_tup_fetch BIGINT,
    size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.schemaname::TEXT,
        s.tablename::TEXT,
        s.indexrelname::TEXT,
        s.idx_scan,
        s.idx_tup_read,
        s.idx_tup_fetch,
        ROUND(pg_relation_size(s.indexrelid) / 1024.0 / 1024.0, 2) AS size_mb
    FROM pg_stat_user_indexes s
    JOIN pg_indexes i ON s.indexrelname = i.indexname
    WHERE s.schemaname = 'public'
    ORDER BY s.idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON MATERIALIZED VIEW mv_document_statistics IS 'Document counts and metrics by country/type/year (refresh daily)';
COMMENT ON MATERIALIZED VIEW mv_citation_network IS 'Citation network metrics for each document (refresh weekly)';
COMMENT ON MATERIALIZED VIEW mv_rag_readiness IS 'RAG embedding readiness status per document (refresh hourly)';

COMMENT ON FUNCTION refresh_all_materialized_views IS 'Refresh all materialized views (run via cron)';
COMMENT ON FUNCTION reindex_all_tables IS 'Reindex all tables for maintenance (run weekly during low traffic)';
COMMENT ON FUNCTION show_index_usage IS 'Show index usage statistics for optimization';

-- ============================================================================
-- FINAL OPTIMIZATION
-- ============================================================================

-- Update table statistics
ANALYZE;

SELECT 'Migration 008 completed: Indexes, materialized views, and optimization functions created' AS status;
