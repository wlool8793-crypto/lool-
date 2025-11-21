// =============================================================================
// LEGAL KNOWLEDGE GRAPH - CONSTRAINTS
// =============================================================================
// This file contains all constraints for the legal knowledge graph schema
// ensuring data integrity and uniqueness across the graph database.
// =============================================================================

// -----------------------------------------------------------------------------
// CASE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_case_id IF NOT EXISTS
FOR (c:Case) REQUIRE c.case_id IS UNIQUE;

CREATE CONSTRAINT unique_case_citation IF NOT EXISTS
FOR (c:Case) REQUIRE c.citation IS UNIQUE;

CREATE CONSTRAINT case_id_not_null IF NOT EXISTS
FOR (c:Case) REQUIRE c.case_id IS NOT NULL;

CREATE CONSTRAINT case_title_not_null IF NOT EXISTS
FOR (c:Case) REQUIRE c.title IS NOT NULL;

CREATE CONSTRAINT case_jurisdiction_not_null IF NOT EXISTS
FOR (c:Case) REQUIRE c.jurisdiction IS NOT NULL;

// -----------------------------------------------------------------------------
// STATUTE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_statute_id IF NOT EXISTS
FOR (s:Statute) REQUIRE s.statute_id IS UNIQUE;

CREATE CONSTRAINT statute_id_not_null IF NOT EXISTS
FOR (s:Statute) REQUIRE s.statute_id IS NOT NULL;

CREATE CONSTRAINT statute_name_not_null IF NOT EXISTS
FOR (s:Statute) REQUIRE s.name IS NOT NULL;

CREATE CONSTRAINT statute_jurisdiction_not_null IF NOT EXISTS
FOR (s:Statute) REQUIRE s.jurisdiction IS NOT NULL;

// -----------------------------------------------------------------------------
// SECTION NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_section_id IF NOT EXISTS
FOR (s:Section) REQUIRE s.section_id IS UNIQUE;

CREATE CONSTRAINT section_id_not_null IF NOT EXISTS
FOR (s:Section) REQUIRE s.section_id IS NOT NULL;

CREATE CONSTRAINT section_text_not_null IF NOT EXISTS
FOR (s:Section) REQUIRE s.text IS NOT NULL;

// -----------------------------------------------------------------------------
// AMENDMENT NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_amendment_id IF NOT EXISTS
FOR (a:Amendment) REQUIRE a.amendment_id IS UNIQUE;

CREATE CONSTRAINT amendment_id_not_null IF NOT EXISTS
FOR (a:Amendment) REQUIRE a.amendment_id IS NOT NULL;

// -----------------------------------------------------------------------------
// JUDGE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_judge_id IF NOT EXISTS
FOR (j:Judge) REQUIRE j.judge_id IS UNIQUE;

CREATE CONSTRAINT judge_id_not_null IF NOT EXISTS
FOR (j:Judge) REQUIRE j.judge_id IS NOT NULL;

CREATE CONSTRAINT judge_name_not_null IF NOT EXISTS
FOR (j:Judge) REQUIRE j.name IS NOT NULL;

// -----------------------------------------------------------------------------
// COURT NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_court_id IF NOT EXISTS
FOR (c:Court) REQUIRE c.court_id IS UNIQUE;

CREATE CONSTRAINT court_id_not_null IF NOT EXISTS
FOR (c:Court) REQUIRE c.court_id IS NOT NULL;

CREATE CONSTRAINT court_name_not_null IF NOT EXISTS
FOR (c:Court) REQUIRE c.name IS NOT NULL;

// -----------------------------------------------------------------------------
// PARTY NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_party_id IF NOT EXISTS
FOR (p:Party) REQUIRE p.party_id IS UNIQUE;

CREATE CONSTRAINT party_id_not_null IF NOT EXISTS
FOR (p:Party) REQUIRE p.party_id IS NOT NULL;

CREATE CONSTRAINT party_name_not_null IF NOT EXISTS
FOR (p:Party) REQUIRE p.name IS NOT NULL;

// -----------------------------------------------------------------------------
// LAWYER NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_lawyer_id IF NOT EXISTS
FOR (l:Lawyer) REQUIRE l.lawyer_id IS UNIQUE;

CREATE CONSTRAINT lawyer_id_not_null IF NOT EXISTS
FOR (l:Lawyer) REQUIRE l.lawyer_id IS NOT NULL;

CREATE CONSTRAINT lawyer_name_not_null IF NOT EXISTS
FOR (l:Lawyer) REQUIRE l.name IS NOT NULL;

// -----------------------------------------------------------------------------
// LEGAL_PRINCIPLE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_principle_id IF NOT EXISTS
FOR (lp:LegalPrinciple) REQUIRE lp.principle_id IS UNIQUE;

CREATE CONSTRAINT principle_id_not_null IF NOT EXISTS
FOR (lp:LegalPrinciple) REQUIRE lp.principle_id IS NOT NULL;

CREATE CONSTRAINT principle_name_not_null IF NOT EXISTS
FOR (lp:LegalPrinciple) REQUIRE lp.name IS NOT NULL;

// -----------------------------------------------------------------------------
// TOPIC NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_topic_id IF NOT EXISTS
FOR (t:Topic) REQUIRE t.topic_id IS UNIQUE;

CREATE CONSTRAINT topic_id_not_null IF NOT EXISTS
FOR (t:Topic) REQUIRE t.topic_id IS NOT NULL;

CREATE CONSTRAINT topic_name_not_null IF NOT EXISTS
FOR (t:Topic) REQUIRE t.name IS NOT NULL;

// -----------------------------------------------------------------------------
// LEGAL_ISSUE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_issue_id IF NOT EXISTS
FOR (li:LegalIssue) REQUIRE li.issue_id IS UNIQUE;

CREATE CONSTRAINT issue_id_not_null IF NOT EXISTS
FOR (li:LegalIssue) REQUIRE li.issue_id IS NOT NULL;

CREATE CONSTRAINT issue_description_not_null IF NOT EXISTS
FOR (li:LegalIssue) REQUIRE li.description IS NOT NULL;

// -----------------------------------------------------------------------------
// STATUS_CHANGE NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_status_change_id IF NOT EXISTS
FOR (sc:StatusChange) REQUIRE sc.status_change_id IS UNIQUE;

CREATE CONSTRAINT status_change_id_not_null IF NOT EXISTS
FOR (sc:StatusChange) REQUIRE sc.status_change_id IS NOT NULL;

// -----------------------------------------------------------------------------
// CHUNK NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_chunk_id IF NOT EXISTS
FOR (ch:Chunk) REQUIRE ch.chunk_id IS UNIQUE;

CREATE CONSTRAINT chunk_id_not_null IF NOT EXISTS
FOR (ch:Chunk) REQUIRE ch.chunk_id IS NOT NULL;

// -----------------------------------------------------------------------------
// VERSION NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_version_id IF NOT EXISTS
FOR (v:Version) REQUIRE v.version_id IS UNIQUE;

CREATE CONSTRAINT version_id_not_null IF NOT EXISTS
FOR (v:Version) REQUIRE v.version_id IS NOT NULL;

// -----------------------------------------------------------------------------
// DOCUMENT NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_document_id IF NOT EXISTS
FOR (d:Document) REQUIRE d.document_id IS UNIQUE;

CREATE CONSTRAINT document_id_not_null IF NOT EXISTS
FOR (d:Document) REQUIRE d.document_id IS NOT NULL;

// -----------------------------------------------------------------------------
// EMBEDDING NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_embedding_id IF NOT EXISTS
FOR (e:Embedding) REQUIRE e.embedding_id IS UNIQUE;

CREATE CONSTRAINT embedding_id_not_null IF NOT EXISTS
FOR (e:Embedding) REQUIRE e.embedding_id IS NOT NULL;

// -----------------------------------------------------------------------------
// LEGAL_DOMAIN NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_domain_id IF NOT EXISTS
FOR (ld:LegalDomain) REQUIRE ld.domain_id IS UNIQUE;

CREATE CONSTRAINT unique_domain_name IF NOT EXISTS
FOR (ld:LegalDomain) REQUIRE ld.name IS UNIQUE;

CREATE CONSTRAINT domain_id_not_null IF NOT EXISTS
FOR (ld:LegalDomain) REQUIRE ld.domain_id IS NOT NULL;

// -----------------------------------------------------------------------------
// JURISDICTION NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_jurisdiction_id IF NOT EXISTS
FOR (j:Jurisdiction) REQUIRE j.jurisdiction_id IS UNIQUE;

CREATE CONSTRAINT unique_jurisdiction_code IF NOT EXISTS
FOR (j:Jurisdiction) REQUIRE j.code IS UNIQUE;

CREATE CONSTRAINT jurisdiction_id_not_null IF NOT EXISTS
FOR (j:Jurisdiction) REQUIRE j.jurisdiction_id IS NOT NULL;

// -----------------------------------------------------------------------------
// KEYWORD NODE CONSTRAINTS
// -----------------------------------------------------------------------------
CREATE CONSTRAINT unique_keyword_id IF NOT EXISTS
FOR (k:Keyword) REQUIRE k.keyword_id IS UNIQUE;

CREATE CONSTRAINT unique_keyword_term IF NOT EXISTS
FOR (k:Keyword) REQUIRE k.term IS UNIQUE;

CREATE CONSTRAINT keyword_id_not_null IF NOT EXISTS
FOR (k:Keyword) REQUIRE k.keyword_id IS NOT NULL;

// =============================================================================
// END OF CONSTRAINTS
// =============================================================================
