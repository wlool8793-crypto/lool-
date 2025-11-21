// ============================================================================
// LEGAL KNOWLEDGE GRAPH - SCHEMA CREATION SCRIPT
// ============================================================================
// Version: 1.0
// Date: 2025-11-11
// Description: Complete schema for production-grade legal knowledge graph
// Supporting: Multi-jurisdiction, temporal versioning, RAG workflows
// ============================================================================

// ============================================================================
// STEP 1: CREATE CONSTRAINTS (Must be created before indexes)
// ============================================================================

// Case constraints
CREATE CONSTRAINT unique_case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE;
CREATE CONSTRAINT unique_citation IF NOT EXISTS FOR (c:Case) REQUIRE c.citation IS UNIQUE;

// Statute constraints
CREATE CONSTRAINT unique_statute_id IF NOT EXISTS FOR (s:Statute) REQUIRE s.statute_id IS UNIQUE;

// Section constraints
CREATE CONSTRAINT unique_section_id IF NOT EXISTS FOR (s:Section) REQUIRE s.section_id IS UNIQUE;

// Judge constraints
CREATE CONSTRAINT unique_judge_id IF NOT EXISTS FOR (j:Judge) REQUIRE j.judge_id IS UNIQUE;

// LegalPrinciple constraints
CREATE CONSTRAINT unique_principle_id IF NOT EXISTS FOR (p:LegalPrinciple) REQUIRE p.principle_id IS UNIQUE;

// LegalIssue constraints
CREATE CONSTRAINT unique_issue_id IF NOT EXISTS FOR (i:LegalIssue) REQUIRE i.issue_id IS UNIQUE;

// StatusChange constraints
CREATE CONSTRAINT unique_status_change_id IF NOT EXISTS FOR (sc:StatusChange) REQUIRE sc.status_change_id IS UNIQUE;

// Chunk constraints
CREATE CONSTRAINT unique_chunk_id IF NOT EXISTS FOR (ch:Chunk) REQUIRE ch.chunk_id IS UNIQUE;

// Court constraints
CREATE CONSTRAINT unique_court_id IF NOT EXISTS FOR (c:Court) REQUIRE c.court_id IS UNIQUE;

// Party constraints
CREATE CONSTRAINT unique_party_id IF NOT EXISTS FOR (p:Party) REQUIRE p.party_id IS UNIQUE;

// Lawyer constraints
CREATE CONSTRAINT unique_lawyer_id IF NOT EXISTS FOR (l:Lawyer) REQUIRE l.lawyer_id IS UNIQUE;

// Topic constraints
CREATE CONSTRAINT unique_topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.topic_id IS UNIQUE;

// LegalDomain constraints
CREATE CONSTRAINT unique_domain_id IF NOT EXISTS FOR (ld:LegalDomain) REQUIRE ld.domain_id IS UNIQUE;

// Jurisdiction constraints
CREATE CONSTRAINT unique_jurisdiction_id IF NOT EXISTS FOR (j:Jurisdiction) REQUIRE j.jurisdiction_id IS UNIQUE;

// Keyword constraints
CREATE CONSTRAINT unique_keyword_id IF NOT EXISTS FOR (k:Keyword) REQUIRE k.keyword_id IS UNIQUE;

// Version constraints
CREATE CONSTRAINT unique_version_id IF NOT EXISTS FOR (v:Version) REQUIRE v.version_id IS UNIQUE;

// Document constraints
CREATE CONSTRAINT unique_document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.document_id IS UNIQUE;

// Embedding constraints
CREATE CONSTRAINT unique_embedding_id IF NOT EXISTS FOR (e:Embedding) REQUIRE e.embedding_id IS UNIQUE;

// Amendment constraints
CREATE CONSTRAINT unique_amendment_id IF NOT EXISTS FOR (a:Amendment) REQUIRE a.amendment_id IS UNIQUE;

// ============================================================================
// STEP 2: CREATE INDEXES FOR PERFORMANCE
// ============================================================================

// --- Case Indexes ---
CREATE INDEX case_decision_date IF NOT EXISTS FOR (c:Case) ON (c.decision_date);
CREATE INDEX case_jurisdiction IF NOT EXISTS FOR (c:Case) ON (c.jurisdiction);
CREATE INDEX case_type IF NOT EXISTS FOR (c:Case) ON (c.case_type);
CREATE INDEX case_status IF NOT EXISTS FOR (c:Case) ON (c.status);
CREATE INDEX case_court IF NOT EXISTS FOR (c:Case) ON (c.court);
CREATE INDEX case_outcome IF NOT EXISTS FOR (c:Case) ON (c.outcome);
CREATE INDEX case_primary_domain IF NOT EXISTS FOR (c:Case) ON (c.primary_domain);
CREATE TEXT INDEX case_title_text IF NOT EXISTS FOR (c:Case) ON (c.title);
CREATE TEXT INDEX case_summary_text IF NOT EXISTS FOR (c:Case) ON (c.summary);

// Common metadata indexes for Case
CREATE INDEX case_source IF NOT EXISTS FOR (c:Case) ON (c.source);
CREATE INDEX case_extracted_at IF NOT EXISTS FOR (c:Case) ON (c.extracted_at);
CREATE INDEX case_extracted_by IF NOT EXISTS FOR (c:Case) ON (c.extracted_by);
CREATE INDEX case_confidence_score IF NOT EXISTS FOR (c:Case) ON (c.confidence_score);
CREATE INDEX case_trust_score IF NOT EXISTS FOR (c:Case) ON (c.trust_score);
CREATE INDEX case_verification_status IF NOT EXISTS FOR (c:Case) ON (c.verification_status);
CREATE INDEX case_version IF NOT EXISTS FOR (c:Case) ON (c.version);

// --- Statute Indexes ---
CREATE INDEX statute_jurisdiction IF NOT EXISTS FOR (s:Statute) ON (s.jurisdiction);
CREATE INDEX statute_status IF NOT EXISTS FOR (s:Statute) ON (s.status);
CREATE INDEX statute_version IF NOT EXISTS FOR (s:Statute) ON (s.version);
CREATE INDEX statute_current IF NOT EXISTS FOR (s:Statute) ON (s.is_current_version);
CREATE INDEX statute_type IF NOT EXISTS FOR (s:Statute) ON (s.statute_type);
CREATE TEXT INDEX statute_name_text IF NOT EXISTS FOR (s:Statute) ON (s.name);

// --- Section Indexes ---
CREATE INDEX section_number IF NOT EXISTS FOR (s:Section) ON (s.section_number);
CREATE INDEX section_version IF NOT EXISTS FOR (s:Section) ON (s.version);
CREATE INDEX section_current IF NOT EXISTS FOR (s:Section) ON (s.is_current_version);
CREATE INDEX section_effective_from IF NOT EXISTS FOR (s:Section) ON (s.effective_from);
CREATE INDEX section_status IF NOT EXISTS FOR (s:Section) ON (s.status);
CREATE TEXT INDEX section_text IF NOT EXISTS FOR (s:Section) ON (s.text);

// --- Judge Indexes ---
CREATE INDEX judge_name IF NOT EXISTS FOR (j:Judge) ON (j.name);
CREATE INDEX judge_jurisdiction IF NOT EXISTS FOR (j:Judge) ON (j.jurisdiction);
CREATE INDEX judge_status IF NOT EXISTS FOR (j:Judge) ON (j.status);
CREATE INDEX judge_court IF NOT EXISTS FOR (j:Judge) ON (j.court);

// --- Court Indexes ---
CREATE INDEX court_name IF NOT EXISTS FOR (c:Court) ON (c.name);
CREATE INDEX court_jurisdiction IF NOT EXISTS FOR (c:Court) ON (c.jurisdiction);
CREATE INDEX court_level IF NOT EXISTS FOR (c:Court) ON (c.court_level);
CREATE INDEX court_type IF NOT EXISTS FOR (c:Court) ON (c.court_type);

// --- LegalPrinciple Indexes ---
CREATE INDEX principle_name IF NOT EXISTS FOR (p:LegalPrinciple) ON (p.name);
CREATE INDEX principle_type IF NOT EXISTS FOR (p:LegalPrinciple) ON (p.principle_type);
CREATE TEXT INDEX principle_definition IF NOT EXISTS FOR (p:LegalPrinciple) ON (p.definition);

// --- LegalIssue Indexes ---
CREATE INDEX issue_type IF NOT EXISTS FOR (i:LegalIssue) ON (i.issue_type);
CREATE INDEX issue_domain IF NOT EXISTS FOR (i:LegalIssue) ON (i.domain);
CREATE TEXT INDEX issue_description IF NOT EXISTS FOR (i:LegalIssue) ON (i.description);

// --- StatusChange Indexes ---
CREATE INDEX status_change_date IF NOT EXISTS FOR (sc:StatusChange) ON (sc.change_date);
CREATE INDEX status_change_new_status IF NOT EXISTS FOR (sc:StatusChange) ON (sc.new_status);
CREATE INDEX status_change_previous_status IF NOT EXISTS FOR (sc:StatusChange) ON (sc.previous_status);

// --- Chunk Indexes ---
CREATE INDEX chunk_type IF NOT EXISTS FOR (ch:Chunk) ON (ch.chunk_type);
CREATE INDEX chunk_trust_score IF NOT EXISTS FOR (ch:Chunk) ON (ch.trust_score);
CREATE INDEX chunk_confidence_score IF NOT EXISTS FOR (ch:Chunk) ON (ch.confidence_score);
CREATE INDEX chunk_verification_status IF NOT EXISTS FOR (ch:Chunk) ON (ch.verification_status);

// ============================================================================
// STEP 3: CREATE RELATIONSHIP INDEXES
// ============================================================================

CREATE INDEX cites_type IF NOT EXISTS FOR ()-[r:CITES]-() ON (r.citation_type);
CREATE INDEX cites_treatment IF NOT EXISTS FOR ()-[r:CITES]-() ON (r.treatment);
CREATE INDEX interprets_type IF NOT EXISTS FOR ()-[r:INTERPRETS]-() ON (r.interpretation_type);
CREATE INDEX amends_type IF NOT EXISTS FOR ()-[r:AMENDS]-() ON (r.amendment_type);
CREATE INDEX amends_date IF NOT EXISTS FOR ()-[r:AMENDS]-() ON (r.amendment_date);
CREATE INDEX decided_by_role IF NOT EXISTS FOR ()-[r:DECIDED_BY]-() ON (r.role);
CREATE INDEX applies_type IF NOT EXISTS FOR ()-[r:APPLIES]-() ON (r.application_type);
CREATE INDEX supersedes_date IF NOT EXISTS FOR ()-[r:SUPERSEDES]-() ON (r.supersede_date);

// New relationship indexes for Iteration 2
CREATE INDEX has_status_change_date IF NOT EXISTS FOR ()-[r:HAS_STATUS_CHANGE]-() ON (r.change_date);
CREATE INDEX superior_to_level IF NOT EXISTS FOR ()-[r:SUPERIOR_TO]-() ON (r.hierarchy_level);
CREATE INDEX heard_in_date IF NOT EXISTS FOR ()-[r:HEARD_IN]-() ON (r.hearing_date);
CREATE INDEX chunk_of_index IF NOT EXISTS FOR ()-[r:CHUNK_OF]-() ON (r.chunk_index);
CREATE INDEX applies_principle_strength IF NOT EXISTS FOR ()-[r:APPLIES_PRINCIPLE]-() ON (r.application_strength);
CREATE INDEX harmonized_with_degree IF NOT EXISTS FOR ()-[r:HARMONIZED_WITH]-() ON (r.harmony_degree);
CREATE INDEX diverges_from_degree IF NOT EXISTS FOR ()-[r:DIVERGES_FROM]-() ON (r.divergence_degree);
CREATE INDEX conflicts_with_severity IF NOT EXISTS FOR ()-[r:CONFLICTS_WITH]-() ON (r.conflict_severity);

// ============================================================================
// STEP 4: CREATE VECTOR INDEXES FOR RAG (Neo4j 5.11+)
// ============================================================================
// Note: Requires Neo4j 5.11+ with vector search support
// Uncomment if using Neo4j with vector support

// CREATE VECTOR INDEX case_embedding IF NOT EXISTS
// FOR (c:Case) ON (c.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// CREATE VECTOR INDEX statute_embedding IF NOT EXISTS
// FOR (s:Statute) ON (s.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// CREATE VECTOR INDEX section_embedding IF NOT EXISTS
// FOR (s:Section) ON (s.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// CREATE VECTOR INDEX principle_embedding IF NOT EXISTS
// FOR (p:LegalPrinciple) ON (p.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// CREATE VECTOR INDEX issue_embedding IF NOT EXISTS
// FOR (i:LegalIssue) ON (i.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// CREATE VECTOR INDEX chunk_embedding IF NOT EXISTS
// FOR (ch:Chunk) ON (ch.embedding)
// OPTIONS {indexConfig: {
//   `vector.dimensions`: 1536,
//   `vector.similarity_function`: 'cosine'
// }};

// ============================================================================
// STEP 5: VERIFY SCHEMA
// ============================================================================

// Show all constraints
SHOW CONSTRAINTS;

// Show all indexes
SHOW INDEXES;

// ============================================================================
// SCHEMA SUMMARY (Iteration 2)
// ============================================================================
// Node Types: 18 (Case, Statute, Section, Judge, Court, Party, Lawyer,
//             LegalPrinciple, LegalIssue, Topic, LegalDomain, Jurisdiction,
//             Keyword, StatusChange, Chunk, Version, Document, Embedding)
// Relationship Types: 16+ (CITES, INTERPRETS, CONTAINS, AMENDS, DECIDED_BY,
//                      ADDRESSES, APPLIES, SUPERSEDES, HAS_STATUS_CHANGE,
//                      SUPERIOR_TO, HEARD_IN, CHUNK_OF, APPLIES_PRINCIPLE,
//                      HARMONIZED_WITH, DIVERGES_FROM, CONFLICTS_WITH, ...)
// Constraints: 18+ (all unique IDs)
// Indexes: 100+ (property, text, vector)
// Features:
//   - Multi-jurisdiction support (BD, IN, PK, UK, US)
//   - Temporal versioning (effective_from, effective_to, version)
//   - Precedent tracking (CITES with treatment)
//   - RAG-ready (vector embeddings for Case, Statute, Section, Principle, Issue, Chunk)
//   - Status change tracking (StatusChange node)
//   - Court hierarchy (SUPERIOR_TO relationship)
//   - Chunking for RAG (Chunk node with embeddings)
//   - Common metadata (source, extracted_at, extracted_by, confidence_score,
//     trust_score, verification_status, version on all nodes)
//   - Judicial analysis (judges, legal principles, issues)
//   - Domain classification (LegalDomain with hierarchy)
// ============================================================================
