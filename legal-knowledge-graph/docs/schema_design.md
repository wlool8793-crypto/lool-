# Legal Knowledge Graph - Schema Design

## Overview

This document describes the architecture and design decisions for the Legal Knowledge Graph schema, optimized for production-grade RAG (Retrieval-Augmented Generation) applications across multiple jurisdictions.

## Design Goals

1. **Hybrid Search Capability**: Support vector search, keyword search, and graph traversal simultaneously
2. **Multi-Jurisdiction Support**: Handle legal systems from Bangladesh, India, and Pakistan (extensible to others)
3. **Temporal Correctness**: Track amendments, versions, and point-in-time validity of legal provisions
4. **All Legal Domains**: Comprehensive coverage of civil, criminal, constitutional, property, family, commercial, tax, and administrative law
5. **Precedent Analysis**: Enable precedent chain discovery and citation network analysis
6. **RAG Optimization**: Structured for efficient retrieval and context generation

## Core Architecture

### Node Types (22 Total)

The schema consists of 22 node types organized into several categories:

#### Primary Legal Entities
- **Case**: Legal judgments and decisions
- **Statute**: Legislative acts and laws
- **Section**: Individual provisions within statutes
- **Amendment**: Changes to statutes/sections

#### Judicial Entities
- **Judge**: Judicial officers
- **Court**: Courts in the judicial hierarchy
- **Party**: Parties to legal cases
- **Lawyer**: Legal practitioners

#### Knowledge Organization
- **LegalPrinciple**: Legal doctrines and maxims
- **Topic**: Subject matter classification
- **LegalIssue**: Specific legal questions
- **LegalDomain**: Areas of law (civil, criminal, etc.)
- **Jurisdiction**: Geographic/legal jurisdictions
- **Keyword**: Search and classification terms

#### Temporal & Version Control
- **Version**: Version snapshots of statutes/sections
- **Citation**: Citation references and context
- **StatusChange**: Tracks status changes of cases over time

#### RAG Infrastructure
- **Document**: Source documents
- **Embedding**: Vector embeddings for semantic search
- **Chunk**: Document chunks for granular retrieval

### Relationship Types (33 Total)

Relationships connect nodes to form a rich knowledge graph:

#### Case-to-Case Relationships
- **CITES**: Citation with treatment (followed, distinguished, overruled)
- **OVERRULES**: One case overrules another
- **FOLLOWS**: Precedent following
- **DISTINGUISHES**: Factual/legal distinction
- **RELATED_TO**: Generic relationship
- **HARMONIZED_WITH**: Aligned interpretations across jurisdictions
- **DIVERGES_FROM**: Differing interpretations across jurisdictions
- **CONFLICTS_WITH**: Direct conflicts requiring resolution

#### Case-to-Statute Relationships
- **APPLIES_SECTION**: Application of specific section
- **INTERPRETS**: Interpretation of statute/section
- **APPLIES**: General application of statute

#### Temporal Relationships
- **AMENDS**: Amendment tracking
- **VERSION_OF**: Version linkage
- **SUPERSEDES**: Version supersession
- **HAS_STATUS_CHANGE**: Tracks status changes

#### Structural Relationships
- **CONTAINS**: Statute contains sections
- **BEFORE_COURT**: Case heard in court
- **HEARD_IN**: Case heard in specific court
- **DECIDED_BY**: Judge authorship
- **PETITIONER/RESPONDENT**: Party roles
- **REPRESENTED_BY**: Lawyer representation
- **SUPERIOR_TO**: Court hierarchy

#### Classification Relationships
- **BELONGS_TO_DOMAIN**: Legal domain membership
- **IN_JURISDICTION**: Jurisdiction membership
- **RAISES_ISSUE**: Issue identification
- **ESTABLISHES_PRINCIPLE**: Principle establishment
- **APPLIES_PRINCIPLE**: Application of principle in chunk
- **HAS_KEYWORD**: Keyword tagging
- **ADDRESSES**: Topic addressed by case

#### RAG Relationships
- **HAS_EMBEDDING**: Embedding linkage
- **SOURCE_DOCUMENT**: Document provenance
- **CHUNK_OF**: Chunk belongs to document

## Key Design Decisions

### 1. Data Governance

**Decision**: Implement comprehensive provenance tracking, versioning, and trust scoring across all nodes

**Rationale**:
- Legal data requires high accuracy and traceability
- Multiple data sources have varying reliability
- Data quality directly impacts RAG application accuracy
- Enables filtering by trust level for production applications
- Supports audit trails and compliance requirements

**Implementation**:

**Provenance Tracking**:
```cypher
// Every node tracks its data source
(:Case {
  source: 'IndianKanoon',
  extracted_at: datetime('2025-11-11T10:30:00Z'),
  extracted_by: 'GPT-4',
  confidence_score: 0.95,
  source_url: 'https://indiankanoon.org/doc/123456/'
})
```

**Versioning System**:
```cypher
// Version tracking with changelog
(:Case {
  version: 3,
  created_at: datetime('2025-01-15T10:00:00Z'),
  updated_at: datetime('2025-11-11T14:30:00Z'),
  changelog: [
    {version: 1, date: '2025-01-15', changes: 'Initial creation', updated_by: 'GPT-4'},
    {version: 2, date: '2025-03-20', changes: 'Added full text', updated_by: 'Manual'},
    {version: 3, date: '2025-11-11', changes: 'Corrected citation', updated_by: 'Manual'}
  ]
})
```

**Trust Scoring**:
```cypher
// Composite trust score based on multiple factors
(:Case {
  trust_score: 0.92,  // 0.0-1.0 composite score
  verification_status: 'Verified',  // Verified, Unverified, Disputed, Deprecated
  authority_level: 5,  // 5=Supreme Court, 4=High Court, etc.
  confidence_score: 0.95  // Extraction confidence
})

// Query with trust filtering for production use
MATCH (c:Case)
WHERE c.trust_score > 0.8
  AND c.verification_status = 'Verified'
  AND c.jurisdiction = 'BD'
RETURN c
```

**Trust Score Calculation**:
- Source reliability: IndianKanoon (0.9), Manual Entry (1.0), Automated (0.7)
- Verification status: Verified (+0.2), Unverified (0.0), Disputed (-0.3)
- Authority level: Supreme Court (+0.1), High Court (+0.05)
- Confidence score: Direct contribution (0.0-1.0)
- Age penalty: Recent data more trusted

### 2. Status Management

**Decision**: Track case status changes through dedicated StatusChange nodes

**Rationale**:
- Legal precedents change status over time (Active → Overruled)
- Need to track when and why status changed
- Important for understanding evolution of legal doctrine
- Enables temporal queries on precedent validity
- Supports automated alerts when precedents are overruled

**Implementation**:
```cypher
// StatusChange node tracks all status transitions
CREATE (sc:StatusChange {
  status_change_id: 'SC-BD-2023-001-001',
  previous_status: 'Active',
  new_status: 'Overruled',
  change_date: date('2023-06-15'),
  reason: 'Overruled by Supreme Court in Rahman v. State',
  triggered_by_case_id: 'CASE-BD-SC-2023-067',
  updated_by: 'Manual',
  source: 'Court Registry',
  confidence_score: 1.0,
  verified: true,
  trust_score: 0.98,
  verification_status: 'Verified',
  created_at: datetime('2023-06-15T16:00:00Z'),
  updated_at: datetime('2023-06-15T16:00:00Z')
})

// Link to case
MATCH (c:Case {case_id: 'CASE-BD-SC-2020-045'})
MATCH (sc:StatusChange {status_change_id: 'SC-BD-2023-001-001'})
CREATE (c)-[:HAS_STATUS_CHANGE]->(sc)

// Query status history
MATCH (c:Case {case_id: $case_id})-[:HAS_STATUS_CHANGE]->(sc:StatusChange)
RETURN sc
ORDER BY sc.change_date DESC
```

**Status Values**:
- Active: Currently valid precedent
- Overruled: Explicitly overruled by higher court
- Superseded: Replaced by new legislation
- Distinguished: Limited in scope
- Deprecated: No longer followed
- Upheld: Affirmed on appeal

### 3. Court Hierarchy

**Decision**: Model court hierarchy explicitly through SUPERIOR_TO relationships

**Rationale**:
- Court hierarchy determines binding precedent
- Essential for understanding precedent weight
- Enables automatic precedent authority calculation
- Supports jurisdiction-specific hierarchy modeling
- Critical for RAG applications to understand precedent binding nature

**Implementation**:
```cypher
// Create court hierarchy
CREATE (supreme:Court {
  court_id: 'CRT-BD-SC',
  name: 'Supreme Court of Bangladesh',
  court_level: 5,
  court_type: 'Apex',
  jurisdiction: 'BD',
  established_date: date('1972-12-16')
})

CREATE (high:Court {
  court_id: 'CRT-BD-HC',
  name: 'High Court Division',
  court_level: 4,
  court_type: 'Constitutional',
  jurisdiction: 'BD'
})

CREATE (district:Court {
  court_id: 'CRT-BD-DH-DC',
  name: 'Dhaka District Court',
  court_level: 3,
  court_type: 'District',
  jurisdiction: 'BD'
})

// Establish hierarchy
MATCH (supreme:Court {court_id: 'CRT-BD-SC'})
MATCH (high:Court {court_id: 'CRT-BD-HC'})
MATCH (district:Court {court_id: 'CRT-BD-DH-DC'})
CREATE (supreme)-[:SUPERIOR_TO {binding: true}]->(high)
CREATE (high)-[:SUPERIOR_TO {binding: true}]->(district)

// Query to find binding precedents based on hierarchy
MATCH (case_court:Court {court_id: $case_court_id})
MATCH (precedent_court:Court)-[:SUPERIOR_TO*0..]->(case_court)
MATCH (precedent:Case)-[:BEFORE_COURT]->(precedent_court)
WHERE precedent.status = 'Active'
RETURN precedent, precedent_court.court_level as authority
ORDER BY authority DESC
```

**Court Levels**:
- Level 5: Supreme Court/Apex Court
- Level 4: High Court/Constitutional Court
- Level 3: District Court
- Level 2: Subordinate Courts
- Level 1: Special Tribunals

### 4. Multi-Jurisdiction Support

**Decision**: Store jurisdiction as a property on nodes + dedicated Jurisdiction nodes

**Rationale**:
- Allows filtering by jurisdiction (BD, IN, PK)
- Supports jurisdiction hierarchy (country > state > district)
- Enables cross-jurisdiction precedent analysis
- Maintains legal system differences

**Implementation**:
```cypher
// Jurisdiction as property for quick filtering
(:Case {jurisdiction: 'BD'})

// Jurisdiction node for hierarchy and metadata
(:Case)-[:IN_JURISDICTION]->(:Jurisdiction {code: 'BD'})
```

### 2. Temporal Versioning

**Decision**: Use Version nodes linked to statutes/sections with valid_from/valid_to dates

**Rationale**:
- Statutes and sections change over time through amendments
- Need to track historical versions for point-in-time queries
- Important for legal research to know what law applied when
- Supports retrospective application analysis

**Implementation**:
- Each amendment creates a new Version node
- Versions linked via VERSION_OF relationship
- valid_from and valid_to dates enable temporal queries
- is_current flag for quick access to current version

### 3. Citation as Both Node and Relationship

**Decision**: Citation information stored in both Citation nodes and CITES relationships

**Rationale**:
- Citation context (how a case cites another) is rich data
- Need to track treatment (positive/negative/neutral)
- Citation networks are first-class analytical targets
- Supports citation weight calculation for precedent strength

### 4. Separate Embedding Nodes

**Decision**: Create dedicated Embedding nodes rather than just properties

**Rationale**:
- Large documents need chunking (one document → many embeddings)
- Enables chunk-level retrieval and ranking
- Supports multiple embedding models
- Allows embedding updates without touching source nodes
- Better for RAG workflows

### 5. Legal Domain Taxonomy

**Decision**: Use dedicated LegalDomain nodes with hierarchical structure

**Rationale**:
- Enables domain-specific search and filtering
- Supports multi-domain classification (a case can belong to multiple domains)
- Allows confidence scoring for domain membership
- Extensible taxonomy as new domains emerge

### 6. Hybrid Search Architecture

**Decision**: Combine three search strategies in one schema

**Strategies**:
1. **Vector Search**: Semantic similarity via embeddings (cosine similarity)
2. **Keyword Search**: Full-text indexes on text properties
3. **Graph Traversal**: Relationship-based discovery (precedent chains, citations)

**Implementation**:
- Vector indexes on embedding properties (1536 dimensions)
- Full-text indexes on title, summary, text fields
- Relationship indexes for efficient traversal
- Combined in RAG pipeline for optimal results

### 7. Precedent Chain Modeling

**Decision**: Use typed CITES relationships with treatment metadata

**Rationale**:
- Legal reasoning depends on how cases cite each other
- "Followed" vs "Overruled" vs "Distinguished" are fundamentally different
- Weight property enables precedent strength calculation
- Supports judicial trend analysis

### 8. Property Design Patterns

**Consistent Patterns Across Nodes**:
- `*_id`: Unique identifier (required, unique constraint)
- `created_at`, `updated_at`: Audit timestamps
- `status`: Current state (Active, Repealed, etc.)
- `version`: Version number where applicable
- `jurisdiction`: Geographic scope
- `embedding`: Vector representation (where applicable)
- `keywords`: Array of search terms

### 9. Index Strategy

**Three-Tier Indexing**:

1. **Unique Constraints**: On all ID fields
2. **Property Indexes**: On frequently filtered fields (jurisdiction, date, status)
3. **Composite Indexes**: On common query combinations
4. **Full-Text Indexes**: On searchable text fields
5. **Vector Indexes**: On embedding properties

**Rationale**: Balance query performance with write overhead

### 10. Relationship Property Design

**Decision**: Store contextual metadata on relationships

**Examples**:
- CITES: citation_type, treatment, weight, context
- AMENDS: amendment_type, amendment_date
- VERSION_OF: valid_from, valid_to, is_current

**Rationale**: Relationships are not just connections but carry semantic meaning

## Schema Extensibility

### Adding New Jurisdictions
1. Create new Jurisdiction node
2. Add jurisdiction code to existing nodes
3. Update jurisdiction property on relevant nodes

### Adding New Legal Domains
1. Create new LegalDomain node
2. Link to cases/statutes via BELONGS_TO_DOMAIN
3. Update domain classification logic

### Adding New Node Types
1. Define JSON schema in schema/nodes/
2. Add constraints and indexes
3. Define relationships to existing nodes
4. Update documentation

### Adding New Relationships
1. Define JSON schema in schema/relationships/
2. Add relationship indexes if needed
3. Update traversal queries
4. Document use cases

## Performance Considerations

### Query Optimization
- Use jurisdiction and date filters early in queries
- Leverage composite indexes for common patterns
- Limit graph traversal depth for citation chains
- Use vector search for initial candidate retrieval

### Write Optimization
- Batch inserts for large data loads
- Create indexes after bulk data load
- Use MERGE for idempotent operations
- Periodic constraint validation

### Scaling Strategies
- Partition by jurisdiction for very large datasets
- Separate read and write workloads
- Archive old versions to reduce active dataset
- Use APOC procedures for complex operations

## Integration with RAG Pipeline

### Retrieval Flow
1. **Query Analysis**: Identify jurisdiction, domain, keywords
2. **Vector Search**: Find semantically similar embeddings
3. **Keyword Search**: Full-text match on legal terms
4. **Graph Expansion**: Traverse to related cases, statutes
5. **Ranking**: Combine scores from all three methods
6. **Context Assembly**: Gather full context for LLM

### Embedding Strategy
- Chunk large documents (512-1024 tokens)
- Overlap chunks (50-100 tokens)
- Store both chunk and full document
- Index at both chunk and document level

## Validation & Quality

### Data Integrity
- Unique constraints prevent duplicates
- NOT NULL constraints enforce required fields
- Relationship constraints ensure valid connections
- Temporal constraints validate date ranges

### Quality Metrics
- Citation resolution rate
- Embedding coverage
- Cross-jurisdiction links
- Temporal completeness
- Domain classification accuracy

## Future Enhancements

### Planned Features
1. Multi-language support (Bengali, Hindi, Urdu)
2. Image/diagram embeddings
3. Audio hearing transcripts
4. Automated citation extraction
5. ML-based domain classification
6. Precedent strength scoring
7. Contradiction detection
8. Legal reasoning graphs

### Research Directions
1. Graph neural networks for case outcome prediction
2. Temporal knowledge graph embeddings
3. Cross-lingual legal concept alignment
4. Automated legal summarization
5. Citation recommendation systems

## References

- Neo4j Graph Data Modeling Best Practices
- Common Law Citation Systems
- Legal Information Retrieval Standards
- RAG Architecture Patterns
- Temporal Graph Database Design

---

**Version**: 2.0.0 (Iteration 2)
**Last Updated**: 2025-11-11
**Maintainer**: Legal Knowledge Graph Team

**Iteration 2 Highlights**:
- Added Data Governance (provenance, versioning, trust scoring)
- Added Status Management (StatusChange node)
- Added Court Hierarchy (SUPERIOR_TO relationships)
- Added Chunk node for granular retrieval
- Added cross-jurisdiction relationships (HARMONIZED_WITH, DIVERGES_FROM, CONFLICTS_WITH)
- Expanded from 18 to 22 node types
- Expanded from 25 to 33 relationship types
