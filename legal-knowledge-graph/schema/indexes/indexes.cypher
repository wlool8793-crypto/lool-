// =============================================================================
// LEGAL KNOWLEDGE GRAPH - INDEXES
// =============================================================================
// This file contains all indexes for the legal knowledge graph schema
// optimized for hybrid search (vector + keyword + graph traversal)
// =============================================================================

// -----------------------------------------------------------------------------
// CASE NODE INDEXES
// -----------------------------------------------------------------------------

// Property indexes for filtering and lookup
CREATE INDEX case_decision_date IF NOT EXISTS
FOR (c:Case) ON (c.decision_date);

CREATE INDEX case_jurisdiction IF NOT EXISTS
FOR (c:Case) ON (c.jurisdiction);

CREATE INDEX case_type IF NOT EXISTS
FOR (c:Case) ON (c.case_type);

CREATE INDEX case_status IF NOT EXISTS
FOR (c:Case) ON (c.status);

CREATE INDEX case_precedent_value IF NOT EXISTS
FOR (c:Case) ON (c.precedent_value);

CREATE INDEX case_court IF NOT EXISTS
FOR (c:Case) ON (c.court);

CREATE INDEX case_primary_domain IF NOT EXISTS
FOR (c:Case) ON (c.primary_domain);

// Common metadata indexes for Case
CREATE INDEX case_source IF NOT EXISTS
FOR (c:Case) ON (c.source);

CREATE INDEX case_extracted_at IF NOT EXISTS
FOR (c:Case) ON (c.extracted_at);

CREATE INDEX case_extracted_by IF NOT EXISTS
FOR (c:Case) ON (c.extracted_by);

CREATE INDEX case_confidence_score IF NOT EXISTS
FOR (c:Case) ON (c.confidence_score);

CREATE INDEX case_trust_score IF NOT EXISTS
FOR (c:Case) ON (c.trust_score);

CREATE INDEX case_verification_status IF NOT EXISTS
FOR (c:Case) ON (c.verification_status);

CREATE INDEX case_version IF NOT EXISTS
FOR (c:Case) ON (c.version);

// Composite indexes for common query patterns
CREATE INDEX case_jurisdiction_type IF NOT EXISTS
FOR (c:Case) ON (c.jurisdiction, c.case_type);

CREATE INDEX case_jurisdiction_date IF NOT EXISTS
FOR (c:Case) ON (c.jurisdiction, c.decision_date);

CREATE INDEX case_court_date IF NOT EXISTS
FOR (c:Case) ON (c.court, c.decision_date);

// Full-text indexes for keyword search
CREATE FULLTEXT INDEX case_fulltext IF NOT EXISTS
FOR (c:Case) ON EACH [c.title, c.summary, c.headnotes, c.full_text]
OPTIONS {
  analyzer: 'english'
};

CREATE TEXT INDEX case_title_text IF NOT EXISTS
FOR (c:Case) ON (c.title);

CREATE TEXT INDEX case_citation_text IF NOT EXISTS
FOR (c:Case) ON (c.citation);

// Vector index for semantic search (RAG)
CREATE VECTOR INDEX case_embedding IF NOT EXISTS
FOR (c:Case) ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// STATUTE NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX statute_jurisdiction IF NOT EXISTS
FOR (s:Statute) ON (s.jurisdiction);

CREATE INDEX statute_status IF NOT EXISTS
FOR (s:Statute) ON (s.status);

CREATE INDEX statute_type IF NOT EXISTS
FOR (s:Statute) ON (s.statute_type);

CREATE INDEX statute_version IF NOT EXISTS
FOR (s:Statute) ON (s.version);

CREATE INDEX statute_current IF NOT EXISTS
FOR (s:Statute) ON (s.is_current_version);

CREATE INDEX statute_enactment_date IF NOT EXISTS
FOR (s:Statute) ON (s.enactment_date);

CREATE INDEX statute_effective_date IF NOT EXISTS
FOR (s:Statute) ON (s.effective_date);

// Common metadata indexes for Statute
CREATE INDEX statute_source IF NOT EXISTS
FOR (s:Statute) ON (s.source);

CREATE INDEX statute_extracted_at IF NOT EXISTS
FOR (s:Statute) ON (s.extracted_at);

CREATE INDEX statute_extracted_by IF NOT EXISTS
FOR (s:Statute) ON (s.extracted_by);

CREATE INDEX statute_confidence_score IF NOT EXISTS
FOR (s:Statute) ON (s.confidence_score);

CREATE INDEX statute_trust_score IF NOT EXISTS
FOR (s:Statute) ON (s.trust_score);

CREATE INDEX statute_verification_status IF NOT EXISTS
FOR (s:Statute) ON (s.verification_status);

// Composite indexes
CREATE INDEX statute_jurisdiction_status IF NOT EXISTS
FOR (s:Statute) ON (s.jurisdiction, s.status);

// Full-text indexes
CREATE FULLTEXT INDEX statute_fulltext IF NOT EXISTS
FOR (s:Statute) ON EACH [s.name, s.short_name, s.summary, s.preamble, s.full_text]
OPTIONS {
  analyzer: 'english'
};

CREATE TEXT INDEX statute_name_text IF NOT EXISTS
FOR (s:Statute) ON (s.name);

// Vector index
CREATE VECTOR INDEX statute_embedding IF NOT EXISTS
FOR (s:Statute) ON (s.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// SECTION NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX section_number IF NOT EXISTS
FOR (s:Section) ON (s.section_number);

CREATE INDEX section_version IF NOT EXISTS
FOR (s:Section) ON (s.version);

CREATE INDEX section_current IF NOT EXISTS
FOR (s:Section) ON (s.is_current_version);

CREATE INDEX section_status IF NOT EXISTS
FOR (s:Section) ON (s.status);

CREATE INDEX section_effective_from IF NOT EXISTS
FOR (s:Section) ON (s.effective_from);

CREATE INDEX section_effective_to IF NOT EXISTS
FOR (s:Section) ON (s.effective_to);

CREATE INDEX section_type IF NOT EXISTS
FOR (s:Section) ON (s.section_type);

// Common metadata indexes for Section
CREATE INDEX section_source IF NOT EXISTS
FOR (s:Section) ON (s.source);

CREATE INDEX section_extracted_at IF NOT EXISTS
FOR (s:Section) ON (s.extracted_at);

CREATE INDEX section_extracted_by IF NOT EXISTS
FOR (s:Section) ON (s.extracted_by);

CREATE INDEX section_confidence_score IF NOT EXISTS
FOR (s:Section) ON (s.confidence_score);

CREATE INDEX section_trust_score IF NOT EXISTS
FOR (s:Section) ON (s.trust_score);

CREATE INDEX section_verification_status IF NOT EXISTS
FOR (s:Section) ON (s.verification_status);

// Composite indexes for temporal queries
CREATE INDEX section_temporal IF NOT EXISTS
FOR (s:Section) ON (s.effective_from, s.effective_to, s.is_current_version);

// Full-text indexes
CREATE FULLTEXT INDEX section_fulltext IF NOT EXISTS
FOR (s:Section) ON EACH [s.section_number, s.title, s.text, s.summary]
OPTIONS {
  analyzer: 'english'
};

CREATE TEXT INDEX section_text IF NOT EXISTS
FOR (s:Section) ON (s.text);

// Vector index
CREATE VECTOR INDEX section_embedding IF NOT EXISTS
FOR (s:Section) ON (s.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// AMENDMENT NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX amendment_date IF NOT EXISTS
FOR (a:Amendment) ON (a.amendment_date);

CREATE INDEX amendment_type IF NOT EXISTS
FOR (a:Amendment) ON (a.amendment_type);

CREATE INDEX amendment_effective_date IF NOT EXISTS
FOR (a:Amendment) ON (a.effective_date);

// Common metadata indexes for Amendment
CREATE INDEX amendment_source IF NOT EXISTS
FOR (a:Amendment) ON (a.source);

CREATE INDEX amendment_extracted_at IF NOT EXISTS
FOR (a:Amendment) ON (a.extracted_at);

CREATE INDEX amendment_extracted_by IF NOT EXISTS
FOR (a:Amendment) ON (a.extracted_by);

CREATE INDEX amendment_confidence_score IF NOT EXISTS
FOR (a:Amendment) ON (a.confidence_score);

CREATE INDEX amendment_trust_score IF NOT EXISTS
FOR (a:Amendment) ON (a.trust_score);

CREATE INDEX amendment_verification_status IF NOT EXISTS
FOR (a:Amendment) ON (a.verification_status);

CREATE INDEX amendment_version IF NOT EXISTS
FOR (a:Amendment) ON (a.version);

// -----------------------------------------------------------------------------
// JUDGE NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX judge_name IF NOT EXISTS
FOR (j:Judge) ON (j.name);

CREATE INDEX judge_jurisdiction IF NOT EXISTS
FOR (j:Judge) ON (j.jurisdiction);

CREATE INDEX judge_court IF NOT EXISTS
FOR (j:Judge) ON (j.court);

CREATE INDEX judge_status IF NOT EXISTS
FOR (j:Judge) ON (j.status);

CREATE INDEX judge_designation IF NOT EXISTS
FOR (j:Judge) ON (j.designation);

// Common metadata indexes for Judge
CREATE INDEX judge_source IF NOT EXISTS
FOR (j:Judge) ON (j.source);

CREATE INDEX judge_extracted_at IF NOT EXISTS
FOR (j:Judge) ON (j.extracted_at);

CREATE INDEX judge_extracted_by IF NOT EXISTS
FOR (j:Judge) ON (j.extracted_by);

CREATE INDEX judge_confidence_score IF NOT EXISTS
FOR (j:Judge) ON (j.confidence_score);

CREATE INDEX judge_trust_score IF NOT EXISTS
FOR (j:Judge) ON (j.trust_score);

CREATE INDEX judge_verification_status IF NOT EXISTS
FOR (j:Judge) ON (j.verification_status);

CREATE INDEX judge_version IF NOT EXISTS
FOR (j:Judge) ON (j.version);

// Full-text index
CREATE FULLTEXT INDEX judge_fulltext IF NOT EXISTS
FOR (j:Judge) ON EACH [j.name, j.biography]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// COURT NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX court_name IF NOT EXISTS
FOR (c:Court) ON (c.name);

CREATE INDEX court_jurisdiction IF NOT EXISTS
FOR (c:Court) ON (c.jurisdiction);

CREATE INDEX court_level IF NOT EXISTS
FOR (c:Court) ON (c.court_level);

CREATE INDEX court_type IF NOT EXISTS
FOR (c:Court) ON (c.court_type);

// Composite index for hierarchy queries
CREATE INDEX court_hierarchy IF NOT EXISTS
FOR (c:Court) ON (c.jurisdiction, c.court_level);

// Common metadata indexes for Court
CREATE INDEX court_source IF NOT EXISTS
FOR (c:Court) ON (c.source);

CREATE INDEX court_extracted_at IF NOT EXISTS
FOR (c:Court) ON (c.extracted_at);

CREATE INDEX court_extracted_by IF NOT EXISTS
FOR (c:Court) ON (c.extracted_by);

CREATE INDEX court_confidence_score IF NOT EXISTS
FOR (c:Court) ON (c.confidence_score);

CREATE INDEX court_trust_score IF NOT EXISTS
FOR (c:Court) ON (c.trust_score);

CREATE INDEX court_verification_status IF NOT EXISTS
FOR (c:Court) ON (c.verification_status);

CREATE INDEX court_version IF NOT EXISTS
FOR (c:Court) ON (c.version);

// -----------------------------------------------------------------------------
// PARTY NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX party_name IF NOT EXISTS
FOR (p:Party) ON (p.name);

CREATE INDEX party_type IF NOT EXISTS
FOR (p:Party) ON (p.party_type);

CREATE INDEX party_jurisdiction IF NOT EXISTS
FOR (p:Party) ON (p.jurisdiction);

// Common metadata indexes for Party
CREATE INDEX party_source IF NOT EXISTS
FOR (p:Party) ON (p.source);

CREATE INDEX party_extracted_at IF NOT EXISTS
FOR (p:Party) ON (p.extracted_at);

CREATE INDEX party_extracted_by IF NOT EXISTS
FOR (p:Party) ON (p.extracted_by);

CREATE INDEX party_confidence_score IF NOT EXISTS
FOR (p:Party) ON (p.confidence_score);

CREATE INDEX party_trust_score IF NOT EXISTS
FOR (p:Party) ON (p.trust_score);

CREATE INDEX party_verification_status IF NOT EXISTS
FOR (p:Party) ON (p.verification_status);

CREATE INDEX party_version IF NOT EXISTS
FOR (p:Party) ON (p.version);

// Full-text index
CREATE FULLTEXT INDEX party_fulltext IF NOT EXISTS
FOR (p:Party) ON EACH [p.name]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// LAWYER NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX lawyer_name IF NOT EXISTS
FOR (l:Lawyer) ON (l.name);

CREATE INDEX lawyer_jurisdiction IF NOT EXISTS
FOR (l:Lawyer) ON (l.jurisdiction);

CREATE INDEX lawyer_designation IF NOT EXISTS
FOR (l:Lawyer) ON (l.designation);

CREATE INDEX lawyer_status IF NOT EXISTS
FOR (l:Lawyer) ON (l.status);

// Common metadata indexes for Lawyer
CREATE INDEX lawyer_source IF NOT EXISTS
FOR (l:Lawyer) ON (l.source);

CREATE INDEX lawyer_extracted_at IF NOT EXISTS
FOR (l:Lawyer) ON (l.extracted_at);

CREATE INDEX lawyer_extracted_by IF NOT EXISTS
FOR (l:Lawyer) ON (l.extracted_by);

CREATE INDEX lawyer_confidence_score IF NOT EXISTS
FOR (l:Lawyer) ON (l.confidence_score);

CREATE INDEX lawyer_trust_score IF NOT EXISTS
FOR (l:Lawyer) ON (l.trust_score);

CREATE INDEX lawyer_verification_status IF NOT EXISTS
FOR (l:Lawyer) ON (l.verification_status);

CREATE INDEX lawyer_version IF NOT EXISTS
FOR (l:Lawyer) ON (l.version);

// Full-text index
CREATE FULLTEXT INDEX lawyer_fulltext IF NOT EXISTS
FOR (l:Lawyer) ON EACH [l.name]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// LEGAL_PRINCIPLE NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX principle_name IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.name);

CREATE INDEX principle_type IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.principle_type);

// Common metadata indexes for LegalPrinciple
CREATE INDEX principle_source IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.source);

CREATE INDEX principle_extracted_at IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.extracted_at);

CREATE INDEX principle_extracted_by IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.extracted_by);

CREATE INDEX principle_confidence_score IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.confidence_score);

CREATE INDEX principle_trust_score IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.trust_score);

CREATE INDEX principle_verification_status IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.verification_status);

CREATE INDEX principle_version IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.version);

// Full-text indexes
CREATE FULLTEXT INDEX principle_fulltext IF NOT EXISTS
FOR (lp:LegalPrinciple) ON EACH [lp.name, lp.latin_name, lp.description]
OPTIONS {
  analyzer: 'english'
};

// Vector index
CREATE VECTOR INDEX principle_embedding IF NOT EXISTS
FOR (lp:LegalPrinciple) ON (lp.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// TOPIC NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX topic_name IF NOT EXISTS
FOR (t:Topic) ON (t.name);

CREATE INDEX topic_domain IF NOT EXISTS
FOR (t:Topic) ON (t.legal_domain);

CREATE INDEX topic_hierarchy IF NOT EXISTS
FOR (t:Topic) ON (t.hierarchy_level);

// Common metadata indexes for Topic
CREATE INDEX topic_source IF NOT EXISTS
FOR (t:Topic) ON (t.source);

CREATE INDEX topic_extracted_at IF NOT EXISTS
FOR (t:Topic) ON (t.extracted_at);

CREATE INDEX topic_extracted_by IF NOT EXISTS
FOR (t:Topic) ON (t.extracted_by);

CREATE INDEX topic_confidence_score IF NOT EXISTS
FOR (t:Topic) ON (t.confidence_score);

CREATE INDEX topic_trust_score IF NOT EXISTS
FOR (t:Topic) ON (t.trust_score);

CREATE INDEX topic_verification_status IF NOT EXISTS
FOR (t:Topic) ON (t.verification_status);

CREATE INDEX topic_version IF NOT EXISTS
FOR (t:Topic) ON (t.version);

// Full-text index
CREATE FULLTEXT INDEX topic_fulltext IF NOT EXISTS
FOR (t:Topic) ON EACH [t.name, t.description]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// LEGAL_ISSUE NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX issue_type IF NOT EXISTS
FOR (li:LegalIssue) ON (li.issue_type);

CREATE INDEX issue_complexity IF NOT EXISTS
FOR (li:LegalIssue) ON (li.complexity);

// Common metadata indexes for LegalIssue
CREATE INDEX issue_source IF NOT EXISTS
FOR (li:LegalIssue) ON (li.source);

CREATE INDEX issue_extracted_at IF NOT EXISTS
FOR (li:LegalIssue) ON (li.extracted_at);

CREATE INDEX issue_extracted_by IF NOT EXISTS
FOR (li:LegalIssue) ON (li.extracted_by);

CREATE INDEX issue_confidence_score IF NOT EXISTS
FOR (li:LegalIssue) ON (li.confidence_score);

CREATE INDEX issue_trust_score IF NOT EXISTS
FOR (li:LegalIssue) ON (li.trust_score);

CREATE INDEX issue_verification_status IF NOT EXISTS
FOR (li:LegalIssue) ON (li.verification_status);

CREATE INDEX issue_version IF NOT EXISTS
FOR (li:LegalIssue) ON (li.version);

// Full-text index
CREATE FULLTEXT INDEX issue_fulltext IF NOT EXISTS
FOR (li:LegalIssue) ON EACH [li.description]
OPTIONS {
  analyzer: 'english'
};

// Vector index
CREATE VECTOR INDEX issue_embedding IF NOT EXISTS
FOR (li:LegalIssue) ON (li.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// STATUS_CHANGE NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX status_change_date IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.change_date);

CREATE INDEX status_change_new_status IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.new_status);

CREATE INDEX status_change_previous_status IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.previous_status);

// Common metadata indexes for StatusChange
CREATE INDEX status_change_source IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.source);

CREATE INDEX status_change_extracted_at IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.extracted_at);

CREATE INDEX status_change_extracted_by IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.extracted_by);

CREATE INDEX status_change_confidence_score IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.confidence_score);

CREATE INDEX status_change_trust_score IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.trust_score);

CREATE INDEX status_change_verification_status IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.verification_status);

CREATE INDEX status_change_version IF NOT EXISTS
FOR (sc:StatusChange) ON (sc.version);

// -----------------------------------------------------------------------------
// CHUNK NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX chunk_type IF NOT EXISTS
FOR (ch:Chunk) ON (ch.chunk_type);

CREATE INDEX chunk_trust_score IF NOT EXISTS
FOR (ch:Chunk) ON (ch.trust_score);

CREATE INDEX chunk_confidence_score IF NOT EXISTS
FOR (ch:Chunk) ON (ch.confidence_score);

CREATE INDEX chunk_verification_status IF NOT EXISTS
FOR (ch:Chunk) ON (ch.verification_status);

// Common metadata indexes for Chunk
CREATE INDEX chunk_source IF NOT EXISTS
FOR (ch:Chunk) ON (ch.source);

CREATE INDEX chunk_extracted_at IF NOT EXISTS
FOR (ch:Chunk) ON (ch.extracted_at);

CREATE INDEX chunk_extracted_by IF NOT EXISTS
FOR (ch:Chunk) ON (ch.extracted_by);

CREATE INDEX chunk_version IF NOT EXISTS
FOR (ch:Chunk) ON (ch.version);

// Vector index for semantic search
CREATE VECTOR INDEX chunk_embedding IF NOT EXISTS
FOR (ch:Chunk) ON (ch.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Full-text index for chunk text
CREATE FULLTEXT INDEX chunk_fulltext IF NOT EXISTS
FOR (ch:Chunk) ON EACH [ch.text, ch.content]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// VERSION NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX version_number IF NOT EXISTS
FOR (v:Version) ON (v.version_number);

CREATE INDEX version_current IF NOT EXISTS
FOR (v:Version) ON (v.current);

CREATE INDEX version_valid_from IF NOT EXISTS
FOR (v:Version) ON (v.valid_from);

CREATE INDEX version_valid_to IF NOT EXISTS
FOR (v:Version) ON (v.valid_to);

// Composite index for temporal queries
CREATE INDEX version_temporal IF NOT EXISTS
FOR (v:Version) ON (v.valid_from, v.valid_to, v.current);

// Common metadata indexes for Version
CREATE INDEX version_source IF NOT EXISTS
FOR (v:Version) ON (v.source);

CREATE INDEX version_extracted_at IF NOT EXISTS
FOR (v:Version) ON (v.extracted_at);

CREATE INDEX version_extracted_by IF NOT EXISTS
FOR (v:Version) ON (v.extracted_by);

CREATE INDEX version_confidence_score IF NOT EXISTS
FOR (v:Version) ON (v.confidence_score);

CREATE INDEX version_trust_score IF NOT EXISTS
FOR (v:Version) ON (v.trust_score);

CREATE INDEX version_verification_status IF NOT EXISTS
FOR (v:Version) ON (v.verification_status);

// -----------------------------------------------------------------------------
// DOCUMENT NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX document_type IF NOT EXISTS
FOR (d:Document) ON (d.document_type);

CREATE INDEX document_jurisdiction IF NOT EXISTS
FOR (d:Document) ON (d.jurisdiction);

CREATE INDEX document_source IF NOT EXISTS
FOR (d:Document) ON (d.source);

CREATE INDEX document_publication_date IF NOT EXISTS
FOR (d:Document) ON (d.publication_date);

CREATE INDEX document_format IF NOT EXISTS
FOR (d:Document) ON (d.file_format);

// Composite index
CREATE INDEX document_source_jurisdiction IF NOT EXISTS
FOR (d:Document) ON (d.source, d.jurisdiction);

// Common metadata indexes for Document
CREATE INDEX document_extracted_at IF NOT EXISTS
FOR (d:Document) ON (d.extracted_at);

CREATE INDEX document_extracted_by IF NOT EXISTS
FOR (d:Document) ON (d.extracted_by);

CREATE INDEX document_confidence_score IF NOT EXISTS
FOR (d:Document) ON (d.confidence_score);

CREATE INDEX document_trust_score IF NOT EXISTS
FOR (d:Document) ON (d.trust_score);

CREATE INDEX document_verification_status IF NOT EXISTS
FOR (d:Document) ON (d.verification_status);

CREATE INDEX document_version IF NOT EXISTS
FOR (d:Document) ON (d.version);

// -----------------------------------------------------------------------------
// EMBEDDING NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX embedding_model IF NOT EXISTS
FOR (e:Embedding) ON (e.embedding_model);

CREATE INDEX embedding_chunk_index IF NOT EXISTS
FOR (e:Embedding) ON (e.chunk_index);

// Common metadata indexes for Embedding
CREATE INDEX embedding_source IF NOT EXISTS
FOR (e:Embedding) ON (e.source);

CREATE INDEX embedding_extracted_at IF NOT EXISTS
FOR (e:Embedding) ON (e.extracted_at);

CREATE INDEX embedding_extracted_by IF NOT EXISTS
FOR (e:Embedding) ON (e.extracted_by);

CREATE INDEX embedding_confidence_score IF NOT EXISTS
FOR (e:Embedding) ON (e.confidence_score);

CREATE INDEX embedding_trust_score IF NOT EXISTS
FOR (e:Embedding) ON (e.trust_score);

CREATE INDEX embedding_verification_status IF NOT EXISTS
FOR (e:Embedding) ON (e.verification_status);

CREATE INDEX embedding_version IF NOT EXISTS
FOR (e:Embedding) ON (e.version);

// Vector index (primary index for RAG retrieval)
CREATE VECTOR INDEX embedding_vector IF NOT EXISTS
FOR (e:Embedding) ON (e.vector)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// Full-text index for text chunks
CREATE FULLTEXT INDEX embedding_text IF NOT EXISTS
FOR (e:Embedding) ON EACH [e.text]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// LEGAL_DOMAIN NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX domain_name IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.name);

CREATE INDEX domain_parent IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.parent_domain);

// Common metadata indexes for LegalDomain
CREATE INDEX domain_source IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.source);

CREATE INDEX domain_extracted_at IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.extracted_at);

CREATE INDEX domain_extracted_by IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.extracted_by);

CREATE INDEX domain_confidence_score IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.confidence_score);

CREATE INDEX domain_trust_score IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.trust_score);

CREATE INDEX domain_verification_status IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.verification_status);

CREATE INDEX domain_version IF NOT EXISTS
FOR (ld:LegalDomain) ON (ld.version);

// Full-text index
CREATE FULLTEXT INDEX domain_fulltext IF NOT EXISTS
FOR (ld:LegalDomain) ON EACH [ld.name, ld.description]
OPTIONS {
  analyzer: 'english'
};

// -----------------------------------------------------------------------------
// JURISDICTION NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX jurisdiction_code IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.code);

CREATE INDEX jurisdiction_type IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.jurisdiction_type);

CREATE INDEX jurisdiction_parent IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.parent_jurisdiction);

CREATE INDEX jurisdiction_legal_system IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.legal_system);

// Common metadata indexes for Jurisdiction
CREATE INDEX jurisdiction_source IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.source);

CREATE INDEX jurisdiction_extracted_at IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.extracted_at);

CREATE INDEX jurisdiction_extracted_by IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.extracted_by);

CREATE INDEX jurisdiction_confidence_score IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.confidence_score);

CREATE INDEX jurisdiction_trust_score IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.trust_score);

CREATE INDEX jurisdiction_verification_status IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.verification_status);

CREATE INDEX jurisdiction_version IF NOT EXISTS
FOR (j:Jurisdiction) ON (j.version);

// -----------------------------------------------------------------------------
// KEYWORD NODE INDEXES
// -----------------------------------------------------------------------------

CREATE INDEX keyword_term IF NOT EXISTS
FOR (k:Keyword) ON (k.term);

CREATE INDEX keyword_normalized IF NOT EXISTS
FOR (k:Keyword) ON (k.normalized_term);

CREATE INDEX keyword_category IF NOT EXISTS
FOR (k:Keyword) ON (k.category);

CREATE INDEX keyword_frequency IF NOT EXISTS
FOR (k:Keyword) ON (k.frequency);

// Common metadata indexes for Keyword
CREATE INDEX keyword_source IF NOT EXISTS
FOR (k:Keyword) ON (k.source);

CREATE INDEX keyword_extracted_at IF NOT EXISTS
FOR (k:Keyword) ON (k.extracted_at);

CREATE INDEX keyword_extracted_by IF NOT EXISTS
FOR (k:Keyword) ON (k.extracted_by);

CREATE INDEX keyword_confidence_score IF NOT EXISTS
FOR (k:Keyword) ON (k.confidence_score);

CREATE INDEX keyword_trust_score IF NOT EXISTS
FOR (k:Keyword) ON (k.trust_score);

CREATE INDEX keyword_verification_status IF NOT EXISTS
FOR (k:Keyword) ON (k.verification_status);

CREATE INDEX keyword_version IF NOT EXISTS
FOR (k:Keyword) ON (k.version);

// Full-text index
CREATE FULLTEXT INDEX keyword_fulltext IF NOT EXISTS
FOR (k:Keyword) ON EACH [k.term, k.normalized_term]
OPTIONS {
  analyzer: 'english'
};

// Vector index
CREATE VECTOR INDEX keyword_embedding IF NOT EXISTS
FOR (k:Keyword) ON (k.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};

// -----------------------------------------------------------------------------
// RELATIONSHIP INDEXES
// -----------------------------------------------------------------------------

// CITES relationship
CREATE INDEX cites_type IF NOT EXISTS
FOR ()-[r:CITES]-() ON (r.citation_type);

CREATE INDEX cites_treatment IF NOT EXISTS
FOR ()-[r:CITES]-() ON (r.treatment);

CREATE INDEX cites_weight IF NOT EXISTS
FOR ()-[r:CITES]-() ON (r.weight);

// AMENDS relationship
CREATE INDEX amends_type IF NOT EXISTS
FOR ()-[r:AMENDS]-() ON (r.amendment_type);

CREATE INDEX amends_date IF NOT EXISTS
FOR ()-[r:AMENDS]-() ON (r.amendment_date);

// OVERRULES relationship
CREATE INDEX overrules_date IF NOT EXISTS
FOR ()-[r:OVERRULES]-() ON (r.overrule_date);

CREATE INDEX overrules_type IF NOT EXISTS
FOR ()-[r:OVERRULES]-() ON (r.overrule_type);

// FOLLOWS relationship
CREATE INDEX follows_strength IF NOT EXISTS
FOR ()-[r:FOLLOWS]-() ON (r.precedent_strength);

// DISTINGUISHES relationship
CREATE INDEX distinguishes_basis IF NOT EXISTS
FOR ()-[r:DISTINGUISHES]-() ON (r.distinction_basis);

// APPLIES_SECTION relationship
CREATE INDEX applies_section_type IF NOT EXISTS
FOR ()-[r:APPLIES_SECTION]-() ON (r.application_type);

// BEFORE_COURT relationship
CREATE INDEX before_court_date IF NOT EXISTS
FOR ()-[r:BEFORE_COURT]-() ON (r.decision_date);

// PETITIONER relationship
CREATE INDEX petitioner_role IF NOT EXISTS
FOR ()-[r:PETITIONER]-() ON (r.party_role);

// RESPONDENT relationship
CREATE INDEX respondent_role IF NOT EXISTS
FOR ()-[r:RESPONDENT]-() ON (r.party_role);

// REPRESENTED_BY relationship
CREATE INDEX represented_by_case IF NOT EXISTS
FOR ()-[r:REPRESENTED_BY]-() ON (r.case_id);

// BELONGS_TO_DOMAIN relationship
CREATE INDEX belongs_to_domain_relevance IF NOT EXISTS
FOR ()-[r:BELONGS_TO_DOMAIN]-() ON (r.relevance);

// IN_JURISDICTION relationship
CREATE INDEX in_jurisdiction_dates IF NOT EXISTS
FOR ()-[r:IN_JURISDICTION]-() ON (r.from_date, r.to_date);

// VERSION_OF relationship
CREATE INDEX version_of_dates IF NOT EXISTS
FOR ()-[r:VERSION_OF]-() ON (r.valid_from, r.valid_to);

CREATE INDEX version_of_current IF NOT EXISTS
FOR ()-[r:VERSION_OF]-() ON (r.is_current);

// HAS_EMBEDDING relationship
CREATE INDEX has_embedding_chunk IF NOT EXISTS
FOR ()-[r:HAS_EMBEDDING]-() ON (r.chunk_index);

CREATE INDEX has_embedding_model IF NOT EXISTS
FOR ()-[r:HAS_EMBEDDING]-() ON (r.embedding_model);

// ESTABLISHES_PRINCIPLE relationship
CREATE INDEX establishes_principle_role IF NOT EXISTS
FOR ()-[r:ESTABLISHES_PRINCIPLE]-() ON (r.principle_role);

// RAISES_ISSUE relationship
CREATE INDEX raises_issue_main IF NOT EXISTS
FOR ()-[r:RAISES_ISSUE]-() ON (r.is_main_issue);

// HAS_KEYWORD relationship
CREATE INDEX has_keyword_relevance IF NOT EXISTS
FOR ()-[r:HAS_KEYWORD]-() ON (r.relevance_score);

// RELATED_TO relationship
CREATE INDEX related_to_nature IF NOT EXISTS
FOR ()-[r:RELATED_TO]-() ON (r.relationship_nature);

// SIMILAR_TO relationship (Iteration 4: RAG Lateral Expansion)
CREATE INDEX similar_to_score IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.similarity_score);

CREATE INDEX similar_to_type IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.similarity_type);

CREATE INDEX similar_to_rank IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.similarity_rank);

CREATE INDEX similar_to_computed IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.computed_at);

CREATE INDEX similar_to_rag_weight IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.rag_weight);

// Composite index for RAG retrieval optimization
CREATE INDEX similar_to_score_type IF NOT EXISTS
FOR ()-[r:SIMILAR_TO]-() ON (r.similarity_score, r.similarity_type);

// =============================================================================
// END OF INDEXES
// =============================================================================
