-- ============================================================================
-- Phase 4 Migration: Create views and functions for quality monitoring
-- Provides easy-to-query views for quality statistics and reporting
-- ============================================================================

-- Drop existing views if they exist
DROP VIEW IF EXISTS quality_summary CASCADE;
DROP VIEW IF EXISTS quality_distribution CASCADE;
DROP VIEW IF EXISTS quality_gates_summary CASCADE;
DROP VIEW IF EXISTS low_quality_documents CASCADE;
DROP VIEW IF EXISTS recent_quality_trends CASCADE;

-- ============================================================================
-- VIEW: quality_summary
-- Overall quality statistics
-- ============================================================================
CREATE VIEW quality_summary AS
SELECT
    COUNT(*) as total_documents,
    ROUND(AVG(overall_score)::numeric, 3) as avg_quality_score,
    ROUND(MIN(overall_score)::numeric, 3) as min_quality_score,
    ROUND(MAX(overall_score)::numeric, 3) as max_quality_score,
    ROUND(STDDEV(overall_score)::numeric, 3) as stddev_quality_score,
    COUNT(*) FILTER (WHERE overall_score >= 0.85) as excellent_count,
    COUNT(*) FILTER (WHERE overall_score >= 0.70 AND overall_score < 0.85) as good_count,
    COUNT(*) FILTER (WHERE overall_score >= 0.50 AND overall_score < 0.70) as acceptable_count,
    COUNT(*) FILTER (WHERE overall_score < 0.50) as poor_count,
    COUNT(*) FILTER (WHERE flagged_for_review) as flagged_count,
    ROUND((COUNT(*) FILTER (WHERE overall_score < 0.50)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as rejection_rate_percent
FROM quality_scores;

COMMENT ON VIEW quality_summary IS 'Overall quality statistics for all documents';

-- ============================================================================
-- VIEW: quality_distribution
-- Quality score distribution in buckets
-- ============================================================================
CREATE VIEW quality_distribution AS
SELECT
    CASE
        WHEN overall_score >= 0.90 THEN '0.90-1.00 (Excellent)'
        WHEN overall_score >= 0.85 THEN '0.85-0.90 (Very Good)'
        WHEN overall_score >= 0.80 THEN '0.80-0.85 (Good)'
        WHEN overall_score >= 0.70 THEN '0.70-0.80 (Acceptable)'
        WHEN overall_score >= 0.60 THEN '0.60-0.70 (Fair)'
        WHEN overall_score >= 0.50 THEN '0.50-0.60 (Poor)'
        ELSE '< 0.50 (Very Poor / Rejected)'
    END as quality_bucket,
    COUNT(*) as document_count,
    ROUND((COUNT(*)::float / SUM(COUNT(*)) OVER () * 100)::numeric, 2) as percentage
FROM quality_scores
GROUP BY quality_bucket
ORDER BY quality_bucket DESC;

COMMENT ON VIEW quality_distribution IS 'Distribution of quality scores across buckets';

-- ============================================================================
-- VIEW: quality_gates_summary
-- Pass rate for each quality gate
-- ============================================================================
CREATE VIEW quality_gates_summary AS
SELECT
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE gate_1_passed) as gate_1_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_1_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_1_pass_rate,
    COUNT(*) FILTER (WHERE gate_2_passed) as gate_2_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_2_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_2_pass_rate,
    COUNT(*) FILTER (WHERE gate_3_passed) as gate_3_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_3_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_3_pass_rate,
    COUNT(*) FILTER (WHERE gate_4_passed) as gate_4_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_4_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_4_pass_rate,
    COUNT(*) FILTER (WHERE gate_5_passed) as gate_5_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_5_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_5_pass_rate,
    COUNT(*) FILTER (WHERE gate_6_passed) as gate_6_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_6_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_6_pass_rate,
    COUNT(*) FILTER (WHERE gate_7_passed) as gate_7_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_7_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_7_pass_rate,
    COUNT(*) FILTER (WHERE gate_8_passed) as gate_8_passed_count,
    ROUND((COUNT(*) FILTER (WHERE gate_8_passed)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as gate_8_pass_rate
FROM quality_scores;

COMMENT ON VIEW quality_gates_summary IS 'Pass rates for all 8 quality gates';

-- ============================================================================
-- VIEW: low_quality_documents
-- Documents with quality issues that need review
-- ============================================================================
CREATE VIEW low_quality_documents AS
SELECT
    d.id,
    d.global_id,
    d.filename_universal,
    d.court_code,
    d.subject_code,
    q.overall_score,
    q.quality_queue,
    q.flagged_for_review,
    q.gate_failures,
    q.retry_count,
    q.extraction_method,
    q.created_at
FROM documents d
JOIN quality_scores q ON d.id = q.document_id
WHERE q.overall_score < 0.70 OR q.flagged_for_review = TRUE
ORDER BY q.overall_score ASC, q.created_at DESC;

COMMENT ON VIEW low_quality_documents IS 'Documents with quality score < 0.70 or flagged for review';

-- ============================================================================
-- VIEW: recent_quality_trends
-- Quality trends over the last 24 hours (hourly buckets)
-- ============================================================================
CREATE VIEW recent_quality_trends AS
SELECT
    DATE_TRUNC('hour', created_at) as hour_bucket,
    COUNT(*) as documents_processed,
    ROUND(AVG(overall_score)::numeric, 3) as avg_quality_score,
    COUNT(*) FILTER (WHERE overall_score >= 0.85) as excellent_count,
    COUNT(*) FILTER (WHERE overall_score < 0.50) as poor_count,
    ROUND((COUNT(*) FILTER (WHERE overall_score < 0.50)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2) as rejection_rate
FROM quality_scores
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour_bucket
ORDER BY hour_bucket DESC;

COMMENT ON VIEW recent_quality_trends IS 'Quality trends over the last 24 hours (hourly)';

-- ============================================================================
-- FUNCTION: get_quality_report
-- Generate a comprehensive quality report
-- ============================================================================
CREATE OR REPLACE FUNCTION get_quality_report()
RETURNS TABLE (
    metric VARCHAR,
    value TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Total Documents'::VARCHAR, COUNT(*)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Average Quality Score', ROUND(AVG(overall_score)::numeric, 3)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Rejection Rate (%)', ROUND((COUNT(*) FILTER (WHERE overall_score < 0.50)::float / NULLIF(COUNT(*), 0) * 100)::numeric, 2)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Excellent (≥0.85)', COUNT(*) FILTER (WHERE overall_score >= 0.85)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Good (0.70-0.85)', COUNT(*) FILTER (WHERE overall_score >= 0.70 AND overall_score < 0.85)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Acceptable (0.50-0.70)', COUNT(*) FILTER (WHERE overall_score >= 0.50 AND overall_score < 0.70)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Poor (<0.50)', COUNT(*) FILTER (WHERE overall_score < 0.50)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Flagged for Review', COUNT(*) FILTER (WHERE flagged_for_review)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'OCR Used', COUNT(*) FILTER (WHERE ocr_used)::TEXT FROM quality_scores
    UNION ALL
    SELECT 'Average Extraction Time (s)', ROUND(AVG(extraction_time_seconds)::numeric, 2)::TEXT FROM quality_scores WHERE extraction_time_seconds IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_quality_report IS 'Generate a comprehensive quality report';

-- ============================================================================
-- FUNCTION: get_quality_gate_failures
-- Get detailed information about quality gate failures
-- ============================================================================
CREATE OR REPLACE FUNCTION get_quality_gate_failures(min_failures INTEGER DEFAULT 1)
RETURNS TABLE (
    document_id INTEGER,
    global_id VARCHAR,
    total_failed_gates INTEGER,
    failed_gates TEXT,
    failure_details JSONB,
    overall_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        q.document_id,
        d.global_id,
        (CASE WHEN NOT gate_1_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_2_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_3_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_4_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_5_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_6_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_7_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_8_passed THEN 1 ELSE 0 END)::INTEGER as total_failed,
        STRING_AGG(
            CASE
                WHEN NOT gate_1_passed THEN 'Gate1:HTTP'
                WHEN NOT gate_2_passed THEN 'Gate2:PDF'
                WHEN NOT gate_3_passed THEN 'Gate3:Text'
                WHEN NOT gate_4_passed THEN 'Gate4:Metadata'
                WHEN NOT gate_5_passed THEN 'Gate5:Overall'
                WHEN NOT gate_6_passed THEN 'Gate6:Validation'
                WHEN NOT gate_7_passed THEN 'Gate7:Database'
                WHEN NOT gate_8_passed THEN 'Gate8:Upload'
            END, ', ') as failed_gates_list,
        q.gate_failures,
        q.overall_score
    FROM quality_scores q
    JOIN documents d ON q.document_id = d.id
    WHERE (
        (CASE WHEN NOT gate_1_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_2_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_3_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_4_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_5_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_6_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_7_passed THEN 1 ELSE 0 END +
         CASE WHEN NOT gate_8_passed THEN 1 ELSE 0 END) >= min_failures
    )
    GROUP BY q.document_id, d.global_id, q.gate_failures, q.overall_score,
             q.gate_1_passed, q.gate_2_passed, q.gate_3_passed, q.gate_4_passed,
             q.gate_5_passed, q.gate_6_passed, q.gate_7_passed, q.gate_8_passed
    ORDER BY total_failed DESC, q.overall_score ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_quality_gate_failures IS 'Get documents with quality gate failures';

-- Grant permissions on views
GRANT SELECT ON quality_summary TO indiankanoon_user;
GRANT SELECT ON quality_distribution TO indiankanoon_user;
GRANT SELECT ON quality_gates_summary TO indiankanoon_user;
GRANT SELECT ON low_quality_documents TO indiankanoon_user;
GRANT SELECT ON recent_quality_trends TO indiankanoon_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Quality monitoring views and functions created successfully';
    RAISE NOTICE 'Available views:';
    RAISE NOTICE '  - quality_summary';
    RAISE NOTICE '  - quality_distribution';
    RAISE NOTICE '  - quality_gates_summary';
    RAISE NOTICE '  - low_quality_documents';
    RAISE NOTICE '  - recent_quality_trends';
    RAISE NOTICE 'Available functions:';
    RAISE NOTICE '  - get_quality_report()';
    RAISE NOTICE '  - get_quality_gate_failures(min_failures)';
END $$;
