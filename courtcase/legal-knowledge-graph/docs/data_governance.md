# Data Governance in Legal Knowledge Graph

## Overview

Data governance is critical for the Legal Knowledge Graph to ensure accuracy, reliability, and traceability of legal information. This document covers the comprehensive data governance framework implemented in Iteration 2.

## Core Principles

1. **Provenance**: Every piece of data must be traceable to its source
2. **Versioning**: All changes must be tracked with complete audit trails
3. **Trust Scoring**: Data quality must be quantifiable and filterable
4. **Verification**: Manual verification status must be maintained
5. **Transparency**: Data lineage must be clear and accessible

## Provenance Tracking

### Required Fields

All nodes in the graph must include the following provenance fields:

```cypher
{
  source: 'IndianKanoon',              // Data source identifier
  extracted_at: datetime(),             // Extraction timestamp
  extracted_by: 'GPT-4',               // Extraction method/model
  confidence_score: 0.95,               // Extraction confidence (0.0-1.0)
  source_url: 'https://...'            // Original source URL (optional)
}
```

### Data Sources

**Primary Sources** (High Reliability):
- IndianKanoon: 0.9 base trust
- Court websites: 0.95 base trust
- Official law repositories: 1.0 base trust
- Manual Entry by legal experts: 1.0 base trust

**Secondary Sources** (Medium Reliability):
- Automated extraction: 0.7 base trust
- Third-party aggregators: 0.8 base trust
- Academic databases: 0.85 base trust

**Tertiary Sources** (Lower Reliability):
- Web scraping: 0.6 base trust
- Unverified submissions: 0.5 base trust

### Extraction Methods

Track which extraction method was used:

```cypher
// Examples
extracted_by: 'GPT-4'                    // LLM extraction
extracted_by: 'Gemini-2.5-Pro'           // Alternative LLM
extracted_by: 'Manual'                   // Human expert
extracted_by: 'Regex-Parser-v2'          // Rule-based extraction
extracted_by: 'GPT-4-Chunking-v2'        // Chunking algorithm
```

### Query by Provenance

```cypher
// Find all cases from specific source
MATCH (c:Case)
WHERE c.source = 'IndianKanoon'
  AND c.extracted_at >= datetime('2024-01-01')
RETURN c.case_id, c.title, c.extracted_at
ORDER BY c.extracted_at DESC

// Find cases with high extraction confidence
MATCH (c:Case)
WHERE c.confidence_score > 0.9
  AND c.source IN ['IndianKanoon', 'Court Registry']
RETURN c
```

## Versioning System

### Version Tracking

Every node maintains version information:

```cypher
{
  version: 3,                          // Current version number
  created_at: datetime(),              // Initial creation timestamp
  updated_at: datetime(),              // Last update timestamp
  changelog: [                         // Array of change records
    {
      version: 1,
      date: '2025-01-15',
      changes: 'Initial creation',
      updated_by: 'GPT-4'
    },
    {
      version: 2,
      date: '2025-03-20',
      changes: 'Added full text',
      updated_by: 'Manual'
    },
    {
      version: 3,
      date: '2025-11-11',
      changes: 'Corrected citation format',
      updated_by: 'Manual'
    }
  ]
}
```

### Version Increment Rules

1. **Minor Updates**: Increment version for:
   - Typo corrections
   - Formatting changes
   - Adding optional fields
   - Metadata updates

2. **Major Updates**: Increment version for:
   - Changing core facts
   - Correcting legal citations
   - Updating case outcomes
   - Modifying legal interpretations

### Changelog Best Practices

```cypher
// Add new changelog entry
MATCH (c:Case {case_id: $case_id})
SET c.version = c.version + 1,
    c.updated_at = datetime(),
    c.changelog = c.changelog + [{
      version: c.version + 1,
      date: toString(date()),
      changes: $changes_description,
      updated_by: $updated_by,
      previous_value: $old_value,
      new_value: $new_value
    }]
```

### Query Version History

```cypher
// Get complete version history for a case
MATCH (c:Case {case_id: $case_id})
UNWIND c.changelog as change
RETURN
  change.version,
  change.date,
  change.changes,
  change.updated_by
ORDER BY change.version ASC

// Find recently updated cases
MATCH (c:Case)
WHERE c.updated_at >= datetime() - duration('P7D')  // Last 7 days
RETURN c.case_id, c.title, c.version, c.updated_at
ORDER BY c.updated_at DESC
```

## Trust Scoring

### Trust Score Components

The trust_score (0.0-1.0) is a composite metric based on:

1. **Source Reliability** (40% weight):
   - Official sources: 1.0
   - IndianKanoon: 0.9
   - Automated extraction: 0.7

2. **Verification Status** (30% weight):
   - Verified: +0.2
   - Unverified: 0.0
   - Disputed: -0.3
   - Deprecated: 0.0

3. **Authority Level** (15% weight):
   - Supreme Court: +0.1
   - High Court: +0.05
   - District Court: 0.0

4. **Confidence Score** (15% weight):
   - Direct contribution from extraction confidence

### Trust Score Calculation

```python
def calculate_trust_score(node):
    # Base score from source
    source_scores = {
        'Court Registry': 1.0,
        'Manual Entry': 1.0,
        'IndianKanoon': 0.9,
        'BDLaws': 0.85,
        'Automated': 0.7,
        'Web Scraping': 0.6
    }
    source_score = source_scores.get(node['source'], 0.5)

    # Verification bonus/penalty
    verification_adjustment = {
        'Verified': 0.2,
        'Unverified': 0.0,
        'Disputed': -0.3,
        'Deprecated': -0.5
    }
    verification = verification_adjustment.get(node['verification_status'], 0.0)

    # Authority bonus (for Case nodes)
    authority_bonus = 0.0
    if 'authority_level' in node:
        authority_bonus = (node['authority_level'] - 3) * 0.05

    # Confidence score contribution
    confidence = node.get('confidence_score', 0.8)

    # Weighted combination
    trust_score = (
        0.40 * source_score +
        0.30 * (source_score + verification) +
        0.15 * (1.0 + authority_bonus) +
        0.15 * confidence
    )

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, trust_score))
```

### Trust Score Example

```cypher
// Case with high trust score
CREATE (c:Case {
  case_id: 'bd_2023_sc_001',
  title: 'Rahman v. State',
  source: 'Court Registry',              // 1.0 base
  verification_status: 'Verified',       // +0.2
  authority_level: 5,                    // Supreme Court +0.1
  confidence_score: 0.98,                // High confidence
  trust_score: 0.96,                     // Composite result
  extracted_by: 'Manual',
  extracted_at: datetime()
})

// Case with lower trust score
CREATE (c:Case {
  case_id: 'bd_2023_dc_045',
  title: 'Local Case',
  source: 'Web Scraping',                // 0.6 base
  verification_status: 'Unverified',     // 0.0
  authority_level: 3,                    // District Court 0.0
  confidence_score: 0.75,                // Medium confidence
  trust_score: 0.62,                     // Composite result
  extracted_by: 'Automated',
  extracted_at: datetime()
})
```

### Verification Status

Four verification states:

1. **Verified**: Manually verified by legal expert
   - Highest trust
   - Can be used in production applications
   - Requires human review

2. **Unverified**: Not yet verified
   - Default state for automated extraction
   - Medium trust
   - Acceptable for research, not for legal advice

3. **Disputed**: Accuracy is questioned
   - Low trust
   - Requires investigation
   - Should not be used until resolved

4. **Deprecated**: Outdated or superseded
   - Very low trust
   - Kept for historical reference
   - Should be filtered out in most queries

### Trust-Based Filtering

```cypher
// Production-grade query (high trust only)
MATCH (c:Case)
WHERE c.trust_score > 0.8
  AND c.verification_status = 'Verified'
  AND c.jurisdiction = 'BD'
RETURN c

// Research query (medium trust acceptable)
MATCH (c:Case)
WHERE c.trust_score > 0.6
  AND c.verification_status IN ['Verified', 'Unverified']
  AND c.jurisdiction = 'BD'
RETURN c

// Exclude disputed/deprecated data
MATCH (c:Case)
WHERE c.verification_status NOT IN ['Disputed', 'Deprecated']
RETURN c
```

## Best Practices for Data Quality

### 1. Always Track Provenance

```cypher
// GOOD: Include provenance
CREATE (c:Case {
  case_id: 'bd_2023_001',
  title: 'Rahman v. State',
  source: 'IndianKanoon',
  extracted_at: datetime(),
  extracted_by: 'GPT-4',
  confidence_score: 0.95,
  trust_score: 0.88,
  verification_status: 'Unverified',
  version: 1,
  created_at: datetime(),
  updated_at: datetime()
})

// BAD: Missing provenance
CREATE (c:Case {
  case_id: 'bd_2023_001',
  title: 'Rahman v. State'
})
```

### 2. Use Appropriate Trust Thresholds

```cypher
// Critical legal advice: trust_score > 0.85, Verified
// Legal research: trust_score > 0.7, Verified or Unverified
// Exploratory analysis: trust_score > 0.5, any status
// Historical analysis: include all, note trust scores
```

### 3. Maintain Changelog

```cypher
// GOOD: Document all changes
MATCH (c:Case {case_id: $case_id})
SET c.citation = $new_citation,
    c.version = c.version + 1,
    c.updated_at = datetime(),
    c.changelog = c.changelog + [{
      version: c.version + 1,
      date: toString(date()),
      changes: 'Corrected citation format from "2023 BLD 1" to "2023 BLD (HCD) 1"',
      updated_by: 'Manual Review',
      previous_value: $old_citation,
      new_value: $new_citation
    }]

// BAD: Update without changelog
MATCH (c:Case {case_id: $case_id})
SET c.citation = $new_citation
```

### 4. Verify High-Impact Data

Priority verification order:
1. Supreme Court decisions
2. Constitutional interpretations
3. Frequently cited cases
4. Recent precedents (last 5 years)
5. Cross-jurisdiction references

### 5. Handle Conflicts Transparently

```cypher
// Mark conflicting data
MATCH (c1:Case {case_id: 'bd_2023_001'})
MATCH (c2:Case {case_id: 'bd_2023_002'})
WHERE c1.outcome <> c2.outcome
  AND exists((c1)-[:RAISES_ISSUE]->()<-[:RAISES_ISSUE]-(c2))
CREATE (c1)-[:CONFLICTS_WITH {
  issue: 'Interpretation of Section 302',
  resolution_status: 'Unresolved',
  conflict_severity: 'High',
  same_jurisdiction: true
}]->(c2)
```

## Query Examples

### Example 1: High-Quality Case Retrieval

```cypher
// Get only high-trust, verified cases for legal research
MATCH (c:Case)
WHERE c.trust_score > 0.8
  AND c.verification_status = 'Verified'
  AND c.status = 'Active'
  AND c.jurisdiction = 'BD'
  AND c.decision_date >= date('2020-01-01')
RETURN
  c.case_id,
  c.citation,
  c.title,
  c.trust_score,
  c.source,
  c.verification_status,
  c.decision_date
ORDER BY c.trust_score DESC, c.decision_date DESC
```

### Example 2: Data Quality Audit

```cypher
// Analyze data quality by source
MATCH (c:Case)
RETURN
  c.source,
  count(*) as total_cases,
  avg(c.trust_score) as avg_trust,
  avg(c.confidence_score) as avg_confidence,
  sum(CASE WHEN c.verification_status = 'Verified' THEN 1 ELSE 0 END) as verified_count,
  sum(CASE WHEN c.verification_status = 'Disputed' THEN 1 ELSE 0 END) as disputed_count
ORDER BY avg_trust DESC
```

### Example 3: Version History Analysis

```cypher
// Find cases with multiple revisions
MATCH (c:Case)
WHERE c.version > 1
RETURN
  c.case_id,
  c.title,
  c.version,
  c.created_at,
  c.updated_at,
  size(c.changelog) as revision_count,
  [change IN c.changelog | change.updated_by] as updated_by_list
ORDER BY c.version DESC
LIMIT 20
```

### Example 4: Trust Score Distribution

```cypher
// Analyze trust score distribution
MATCH (c:Case)
WHERE c.jurisdiction = 'BD'
RETURN
  CASE
    WHEN c.trust_score >= 0.9 THEN 'Excellent (0.9-1.0)'
    WHEN c.trust_score >= 0.8 THEN 'Good (0.8-0.9)'
    WHEN c.trust_score >= 0.7 THEN 'Fair (0.7-0.8)'
    WHEN c.trust_score >= 0.6 THEN 'Poor (0.6-0.7)'
    ELSE 'Very Poor (<0.6)'
  END as trust_category,
  count(*) as case_count,
  avg(c.trust_score) as avg_trust
ORDER BY avg_trust DESC
```

### Example 5: Verification Status Report

```cypher
// Generate verification status report
MATCH (c:Case)
WHERE c.jurisdiction = 'BD'
  AND c.decision_date >= date('2023-01-01')
RETURN
  c.verification_status,
  count(*) as count,
  avg(c.trust_score) as avg_trust,
  min(c.trust_score) as min_trust,
  max(c.trust_score) as max_trust
ORDER BY count DESC
```

### Example 6: Unverified High-Authority Cases

```cypher
// Find high-authority cases that need verification
MATCH (c:Case)
WHERE c.verification_status = 'Unverified'
  AND c.authority_level >= 4  // High Court or above
  AND c.decision_date >= date('2023-01-01')
  AND c.confidence_score > 0.85
RETURN
  c.case_id,
  c.citation,
  c.title,
  c.authority_level,
  c.trust_score,
  c.source,
  c.extracted_at
ORDER BY c.authority_level DESC, c.decision_date DESC
LIMIT 50
```

### Example 7: Cross-Node Trust Filtering

```cypher
// RAG query with trust filtering across multiple node types
MATCH (chunk:Chunk)
WHERE chunk.trust_score > 0.8
  AND chunk.verification_status = 'Verified'
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.trust_score > 0.85
  AND case.verification_status = 'Verified'
  AND case.status = 'Active'
OPTIONAL MATCH (chunk)-[r:APPLIES_PRINCIPLE]->(principle:LegalPrinciple)
WHERE r.confidence > 0.85
RETURN
  chunk.chunk_text,
  case.citation,
  case.trust_score,
  collect(principle.name) as principles
ORDER BY case.trust_score DESC, chunk.trust_score DESC
```

## Data Quality Metrics

### Key Performance Indicators (KPIs)

1. **Coverage Metrics**:
   - Total nodes with provenance data: Target 100%
   - Nodes with changelog: Target 100%
   - Nodes with trust_score: Target 100%

2. **Quality Metrics**:
   - Average trust_score: Target > 0.8
   - Verified nodes percentage: Target > 60%
   - Disputed nodes percentage: Target < 5%

3. **Freshness Metrics**:
   - Nodes updated in last 30 days: Track trend
   - Average age of unverified high-authority cases: Target < 60 days

4. **Confidence Metrics**:
   - Average confidence_score: Target > 0.85
   - Low confidence nodes (<0.7): Target < 10%

### Monitoring Queries

```cypher
// Overall data quality dashboard
MATCH (n)
WHERE n:Case OR n:Statute OR n:Section OR n:Chunk
RETURN
  labels(n)[0] as node_type,
  count(*) as total,
  avg(n.trust_score) as avg_trust,
  avg(n.confidence_score) as avg_confidence,
  sum(CASE WHEN n.verification_status = 'Verified' THEN 1 ELSE 0 END) * 100.0 / count(*) as verified_pct,
  sum(CASE WHEN n.trust_score > 0.8 THEN 1 ELSE 0 END) * 100.0 / count(*) as high_trust_pct
ORDER BY node_type
```

## Governance Workflow

### Data Ingestion Workflow

1. **Extract**: Automated extraction with provenance
2. **Compute Trust**: Calculate initial trust_score
3. **Flag for Review**: High-authority or low-confidence items
4. **Verify**: Manual verification by experts
5. **Update Trust**: Recalculate trust_score after verification
6. **Publish**: Make available for queries

### Verification Workflow

```cypher
// Mark case as verified
MATCH (c:Case {case_id: $case_id})
SET c.verification_status = 'Verified',
    c.trust_score = $recalculated_trust_score,
    c.version = c.version + 1,
    c.updated_at = datetime(),
    c.changelog = c.changelog + [{
      version: c.version + 1,
      date: toString(date()),
      changes: 'Manually verified by legal expert',
      updated_by: $verifier_name,
      verification_notes: $notes
    }]
```

### Dispute Resolution Workflow

```cypher
// Mark case as disputed
MATCH (c:Case {case_id: $case_id})
SET c.verification_status = 'Disputed',
    c.trust_score = c.trust_score - 0.3,  // Penalty
    c.version = c.version + 1,
    c.updated_at = datetime(),
    c.changelog = c.changelog + [{
      version: c.version + 1,
      date: toString(date()),
      changes: 'Marked as disputed',
      updated_by: $reporter_name,
      dispute_reason: $reason,
      dispute_details: $details
    }]
```

## Data Retention Policy

### Active Data
- trust_score > 0.6
- verification_status: Verified, Unverified
- Kept in primary database

### Archived Data
- trust_score <= 0.6
- verification_status: Deprecated
- Moved to archive after 1 year

### Deletion Policy
- Disputed data: Investigate within 30 days
- Deprecated data: Archive after 1 year
- Very low trust (<0.3): Flag for deletion review

---

**Version**: 2.0.0 (Iteration 2)
**Last Updated**: 2025-11-11
**Maintainer**: Legal Knowledge Graph Team

**Document Status**: Comprehensive data governance framework for legal knowledge graph data quality assurance.
