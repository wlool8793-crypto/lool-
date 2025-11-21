// ============================================================================
// LEGAL KNOWLEDGE GRAPH - TEST QUERIES
// ============================================================================
// Version: 1.0
// Date: 2025-11-11
// Description: Comprehensive test queries for schema validation
// Categories: 8 (Basic Retrieval, Precedent Chains, Temporal Queries,
//             Multi-Jurisdiction, RAG-Optimized, Legal Reasoning,
//             Domain-Specific, Performance Testing)
// Total Queries: 60+
// ============================================================================

// ============================================================================
// A. BASIC RETRIEVAL (10 queries)
// ============================================================================

// A1. Find case by citation
MATCH (c:Case {citation: "AIR 1973 SC 1461"})
RETURN c;

// A2. Find case by neutral citation
MATCH (c:Case {neutral_citation: "[1989] BDSC 001"})
RETURN c;

// A3. Find statute by name
MATCH (s:Statute)
WHERE s.name CONTAINS "Penal Code"
RETURN s;

// A4. Find all cases decided by a specific judge
MATCH (c:Case)-[r:DECIDED_BY]->(j:Judge {name: "Justice Syed Mahmud Hossain"})
RETURN c.title, c.citation, c.decision_date, r.role
ORDER BY c.decision_date DESC;

// A5. Find all cases in Bangladesh jurisdiction
MATCH (c:Case {jurisdiction: "BD"})
RETURN c.title, c.citation, c.decision_date
ORDER BY c.decision_date DESC;

// A6. Find all cases by court
MATCH (c:Case {court: "Supreme Court of Bangladesh"})
RETURN c.title, c.citation, c.decision_date
ORDER BY c.decision_date DESC;

// A7. Find all constitutional cases
MATCH (c:Case {case_type: "Constitutional"})
RETURN c.title, c.citation, c.jurisdiction, c.decision_date
ORDER BY c.decision_date;

// A8. Find all active statutes in Bangladesh
MATCH (s:Statute {jurisdiction: "BD", status: "Active"})
RETURN s.name, s.version, s.is_current_version, s.effective_date;

// A9. Find current version of a specific statute
MATCH (s:Statute {is_current_version: true})
WHERE s.name CONTAINS "Penal Code"
RETURN s;

// A10. Find all sections of a statute
MATCH (st:Statute)-[r:CONTAINS]->(sec:Section)
WHERE st.name CONTAINS "Penal Code" AND st.is_current_version = true
RETURN sec.section_number, sec.title, sec.version, sec.is_current_version
ORDER BY toInteger(sec.section_number);

// ============================================================================
// B. PRECEDENT CHAINS (12 queries)
// ============================================================================

// B1. Find all cases directly cited by a specific case
MATCH (citing:Case {case_id: "CASE-BD-SC-2023-001"})-[r:CITES]->(cited:Case)
RETURN citing.title AS from_case,
       cited.title AS to_case,
       cited.citation,
       r.citation_type,
       r.treatment,
       r.weight
ORDER BY r.weight DESC;

// B2. Find all cases that cite a specific case
MATCH (citing:Case)-[r:CITES]->(cited:Case {case_id: "CASE-IN-SC-1973-027"})
RETURN citing.title, citing.citation, citing.jurisdiction, r.citation_type, r.treatment
ORDER BY citing.decision_date;

// B3. Find precedent chain (2-hop) from Case A
MATCH path = (c1:Case {case_id: "CASE-BD-SC-2023-001"})-[:CITES*1..2]->(c2:Case)
RETURN c1.title AS starting_case,
       [node IN nodes(path) | node.title] AS precedent_chain,
       length(path) AS chain_length
ORDER BY chain_length;

// B4. Find precedent chain (4-hop) - Kesavananda to recent cases
MATCH path = (c1:Case {case_id: "CASE-IN-SC-1973-027"})<-[:CITES*1..4]-(c2:Case)
WHERE c1 <> c2
RETURN c2.title AS recent_case,
       c2.citation,
       c2.decision_date,
       [node IN nodes(path) | node.short_title] AS precedent_chain,
       length(path) AS chain_depth
ORDER BY chain_depth DESC, c2.decision_date DESC
LIMIT 10;

// B5. Find cases that overrule a specific case
MATCH (overruling:Case)-[r:CITES {citation_type: "Overruled"}]->(overruled:Case)
RETURN overruling.title, overruling.citation, overruling.decision_date,
       overruled.title, overruled.citation, overruled.decision_date
ORDER BY overruling.decision_date;

// B6. Find cases overruled by a specific case
MATCH (c:Case {case_id: "CASE-IN-SC-1978-012"})-[r:CITES {citation_type: "Overruled"}]->(overruled:Case)
RETURN c.title AS overruling_case,
       overruled.title AS overruled_case,
       overruled.citation,
       r.context;

// B7. Find conflicting precedents on a specific issue
MATCH (c1:Case)-[r1:ADDRESSES]->(i:LegalIssue {issue_id: "ISSUE-CRIM-002"})<-[r2:ADDRESSES]-(c2:Case)
WHERE c1.case_id < c2.case_id AND r1.holding <> r2.holding
RETURN i.description AS issue,
       c1.title AS case1, c1.citation AS citation1, r1.holding AS holding1,
       c2.title AS case2, c2.citation AS citation2, r2.holding AS holding2;

// B8. Find most cited case (citation count)
MATCH (cited:Case)<-[r:CITES]-(citing:Case)
WITH cited, count(r) AS citation_count
RETURN cited.title, cited.citation, cited.jurisdiction, citation_count
ORDER BY citation_count DESC
LIMIT 10;

// B9. Find citation influence score (weighted by treatment)
MATCH (cited:Case)<-[r:CITES]-(citing:Case)
WITH cited,
     sum(CASE r.treatment
         WHEN 'Positive' THEN 1.0
         WHEN 'Neutral' THEN 0.5
         WHEN 'Negative' THEN 0.0
         ELSE 0.5 END) AS influence_score,
     count(r) AS citation_count
RETURN cited.title, cited.citation, citation_count, influence_score
ORDER BY influence_score DESC
LIMIT 10;

// B10. Find cross-jurisdiction citation flow (BD citing IN)
MATCH (bd:Case {jurisdiction: "BD"})-[r:CITES]->(in:Case {jurisdiction: "IN"})
RETURN bd.title AS bd_case, bd.citation AS bd_citation,
       in.title AS in_case, in.citation AS in_citation,
       r.citation_type, r.treatment
ORDER BY bd.decision_date;

// B11. Find case reinstatement chain (overruled then approved)
MATCH (c1:Case {case_id: "CASE-BD-SC-2019-007"})<-[r1:CITES]-(c2:Case)
MATCH (c1)<-[r2:CITES]-(c3:Case)
WHERE r1.citation_type = "Overruled" AND r2.citation_type = "Approved"
RETURN c1.title AS original_case,
       c2.title AS overruling_case, c2.decision_date AS overruled_date,
       c3.title AS reinstating_case, c3.decision_date AS reinstated_date,
       r2.context
ORDER BY c3.decision_date;

// B12. Find precedent evolution for a legal principle
MATCH (c:Case)-[r:APPLIES]->(p:LegalPrinciple {principle_id: "PRIN-BASIC-STRUCTURE"})
RETURN c.title, c.citation, c.jurisdiction, c.decision_date, r.application_type
ORDER BY c.decision_date;

// ============================================================================
// C. TEMPORAL QUERIES (10 queries)
// ============================================================================

// C1. Find statute version active on a specific date (2010-01-01)
MATCH (s:Statute)
WHERE s.name CONTAINS "Penal Code"
  AND s.jurisdiction = "BD"
  AND s.effective_date <= date("2010-01-01")
  AND (s.expiry_date IS NULL OR s.expiry_date > date("2010-01-01"))
RETURN s.name, s.version, s.effective_date, s.expiry_date, s.status
ORDER BY s.version DESC
LIMIT 1;

// C2. Find all amendments to a statute
MATCH (newer:Statute)-[r:AMENDS]->(older:Statute)
WHERE older.name CONTAINS "Penal Code" OR newer.name CONTAINS "Penal Code"
RETURN newer.version AS new_version,
       older.version AS old_version,
       r.amendment_type,
       r.amendment_date,
       r.description
ORDER BY r.amendment_date;

// C3. Find section version active on specific date (2015-06-01)
MATCH (sec:Section {section_number: "376"})
WHERE sec.effective_from <= date("2015-06-01")
  AND (sec.effective_to IS NULL OR sec.effective_to > date("2015-06-01"))
RETURN sec.section_id, sec.version, sec.text, sec.effective_from, sec.effective_to;

// C4. Find all versions of a section with timeline
MATCH (sec:Section {section_number: "376"})
RETURN sec.section_id, sec.version, sec.effective_from, sec.effective_to,
       sec.is_current_version, sec.status
ORDER BY sec.version;

// C5. Find cases citing a specific version of a section
MATCH (c:Case)-[r:INTERPRETS]->(sec:Section {section_id: "SEC-BD-PC-376-V3"})
RETURN c.title, c.citation, c.decision_date, r.interpretation_type, r.holding
ORDER BY c.decision_date;

// C6. Point-in-time reconstruction: statute snapshot at date (2012-01-01)
MATCH (st:Statute {statute_id: "STAT-BD-PC-1860-V3"})
MATCH (st)-[r:CONTAINS]->(sec:Section)
WHERE sec.effective_from <= date("2012-01-01")
  AND (sec.effective_to IS NULL OR sec.effective_to > date("2012-01-01"))
RETURN st.name, st.version, st.effective_date,
       collect({section: sec.section_number, title: sec.title, version: sec.version}) AS sections;

// C7. Find amendment chain for a section
MATCH path = (newer:Section)-[:AMENDS*1..]->(older:Section)
WHERE newer.section_number = "376" AND older.section_number = "376"
RETURN [node IN nodes(path) | {
  version: node.version,
  effective_from: node.effective_from,
  text: substring(node.text, 0, 100)
}] AS amendment_chain,
length(path) AS amendments_count
ORDER BY amendments_count DESC
LIMIT 1;

// C8. Find cases decided between two dates
MATCH (c:Case)
WHERE c.decision_date >= date("2020-01-01") AND c.decision_date <= date("2024-12-31")
RETURN c.title, c.citation, c.decision_date, c.case_type
ORDER BY c.decision_date;

// C9. Find statutes enacted in a specific year
MATCH (s:Statute)
WHERE s.enactment_date >= date("2017-01-01") AND s.enactment_date <= date("2017-12-31")
RETURN s.name, s.jurisdiction, s.enactment_date, s.effective_date;

// C10. Find temporal gap in section versions (sections with gaps between effective_to and next effective_from)
MATCH (sec1:Section)-[:SUPERSEDES]->(sec2:Section)
WHERE sec1.section_number = sec2.section_number
  AND sec2.effective_to IS NOT NULL
  AND sec1.effective_from > sec2.effective_to
RETURN sec2.section_number,
       sec2.version AS old_version, sec2.effective_to AS old_end,
       sec1.version AS new_version, sec1.effective_from AS new_start,
       duration.between(sec2.effective_to, sec1.effective_from).days AS gap_days;

// ============================================================================
// D. MULTI-JURISDICTION QUERIES (8 queries)
// ============================================================================

// D1. Find BD cases citing IN precedents
MATCH (bd:Case {jurisdiction: "BD"})-[r:CITES]->(in:Case {jurisdiction: "IN"})
RETURN bd.title AS bangladesh_case, bd.citation AS bd_citation,
       in.title AS indian_case, in.citation AS in_citation,
       r.citation_type, r.treatment
ORDER BY bd.decision_date;

// D2. Find common law precedents shared across BD/IN/PK
MATCH (c:Case)<-[:CITES]-(citing:Case)
WHERE c.jurisdiction = "IN"
WITH c, collect(DISTINCT citing.jurisdiction) AS citing_jurisdictions
WHERE size(citing_jurisdictions) >= 2
  AND 'BD' IN citing_jurisdictions
  AND 'PK' IN citing_jurisdictions
RETURN c.title, c.citation, c.jurisdiction, citing_jurisdictions;

// D3. Find jurisdiction-specific interpretations of same legal principle
MATCH (c:Case)-[r:APPLIES]->(p:LegalPrinciple {principle_id: "PRIN-BASIC-STRUCTURE"})
RETURN p.name AS principle,
       c.jurisdiction,
       c.title AS case_title,
       c.citation,
       c.decision_date,
       r.application_type
ORDER BY c.jurisdiction, c.decision_date;

// D4. Count cases by jurisdiction
MATCH (c:Case)
RETURN c.jurisdiction, count(c) AS case_count
ORDER BY case_count DESC;

// D5. Find cross-border precedent influence (IN → BD → others)
MATCH path = (in:Case {jurisdiction: "IN"})<-[:CITES]-(bd:Case {jurisdiction: "BD"})<-[:CITES]-(other:Case)
WHERE other.jurisdiction NOT IN ["IN", "BD"]
RETURN in.title AS indian_precedent,
       bd.title AS bangladesh_case,
       other.title AS third_jurisdiction_case,
       other.jurisdiction
ORDER BY other.decision_date;

// D6. Find most influential cross-jurisdiction precedent
MATCH (c:Case)-[r:CITES]->(cited:Case)
WHERE c.jurisdiction <> cited.jurisdiction
WITH cited, count(r) AS cross_jurisdiction_citations, collect(DISTINCT c.jurisdiction) AS citing_jurisdictions
RETURN cited.title, cited.citation, cited.jurisdiction,
       cross_jurisdiction_citations,
       citing_jurisdictions
ORDER BY cross_jurisdiction_citations DESC
LIMIT 5;

// D7. Find judges who cited foreign precedents
MATCH (c:Case)-[:DECIDED_BY]->(j:Judge)
MATCH (c)-[r:CITES]->(foreign:Case)
WHERE c.jurisdiction <> foreign.jurisdiction
RETURN j.name, j.court, j.jurisdiction,
       count(DISTINCT foreign) AS foreign_citations,
       collect(DISTINCT foreign.jurisdiction) AS foreign_jurisdictions
ORDER BY foreign_citations DESC;

// D8. Compare statutory versions across jurisdictions
MATCH (s:Statute)
WHERE s.name CONTAINS "Penal Code" OR s.name CONTAINS "IPC"
RETURN s.jurisdiction, s.name, s.version, s.effective_date, s.is_current_version
ORDER BY s.jurisdiction, s.version;

// ============================================================================
// E. RAG-OPTIMIZED QUERIES (10 queries)
// ============================================================================
// Note: Vector similarity queries commented out (require Neo4j 5.11+ with vector support)
// These demonstrate the intended RAG query patterns

// E1. Vector similarity search (requires embeddings)
// MATCH (c:Case)
// WHERE c.embedding IS NOT NULL
// WITH c, vector.similarity.cosine(c.embedding, $query_embedding) AS similarity
// WHERE similarity > 0.7
// RETURN c.title, c.citation, c.summary, similarity
// ORDER BY similarity DESC
// LIMIT 10;

// E2. Hybrid search: keyword + semantic (simulated without vectors)
MATCH (c:Case)
WHERE c.summary CONTAINS "murder" OR c.catchwords CONTAINS "Murder"
RETURN c.title, c.citation, c.summary, c.catchwords
LIMIT 10;

// E3. Context retrieval for RAG: Case + precedents + sections + principles
MATCH (c:Case {case_id: "CASE-BD-SC-2023-001"})
OPTIONAL MATCH (c)-[r_cites:CITES]->(precedent:Case)
OPTIONAL MATCH (c)-[r_interprets:INTERPRETS]->(sec:Section)
OPTIONAL MATCH (c)-[r_applies:APPLIES]->(prin:LegalPrinciple)
OPTIONAL MATCH (c)-[r_addresses:ADDRESSES]->(issue:LegalIssue)
RETURN c AS case,
       collect(DISTINCT {case: precedent, relationship: r_cites}) AS precedents,
       collect(DISTINCT {section: sec, relationship: r_interprets}) AS sections,
       collect(DISTINCT {principle: prin, relationship: r_applies}) AS principles,
       collect(DISTINCT {issue: issue, relationship: r_addresses}) AS issues;

// E4. Find similar cases by catchwords overlap
MATCH (c1:Case {case_id: "CASE-BD-SC-2023-001"})
MATCH (c2:Case)
WHERE c1 <> c2
  AND any(word IN c1.catchwords WHERE word IN c2.catchwords)
WITH c1, c2,
     [word IN c1.catchwords WHERE word IN c2.catchwords] AS common_catchwords,
     size([word IN c1.catchwords WHERE word IN c2.catchwords]) AS overlap_count
RETURN c2.title, c2.citation, common_catchwords, overlap_count
ORDER BY overlap_count DESC
LIMIT 10;

// E5. Find related cases through shared legal issues
MATCH (c1:Case {case_id: "CASE-BD-SC-2023-001"})-[:ADDRESSES]->(issue:LegalIssue)<-[:ADDRESSES]-(c2:Case)
WHERE c1 <> c2
RETURN c2.title, c2.citation, issue.description, c2.decision_date
ORDER BY c2.decision_date DESC;

// E6. Graph traversal + retrieval: Find interpretation lineage
MATCH path = (c:Case)-[:INTERPRETS]->(sec:Section)<-[:CONTAINS]-(st:Statute)
WHERE c.case_id = "CASE-BD-SC-2023-001"
MATCH (sec)<-[:INTERPRETS]-(other_cases:Case)
WHERE other_cases <> c
RETURN c.title AS focus_case,
       sec.section_number,
       sec.title AS section_title,
       st.name AS statute,
       collect({case: other_cases.title, citation: other_cases.citation}) AS other_interpretations;

// E7. Retrieve case with full statutory context
MATCH (c:Case {case_id: "CASE-BD-SC-2023-001"})-[:INTERPRETS]->(sec:Section)<-[:CONTAINS]-(st:Statute)
RETURN c.title AS case_title,
       c.citation,
       c.summary,
       collect({
         section_number: sec.section_number,
         section_title: sec.title,
         section_text: sec.text,
         statute_name: st.name,
         version: sec.version
       }) AS statutory_context;

// E8. Find cases with similar fact patterns (using case_type + catchwords)
MATCH (c1:Case {case_id: "CASE-BD-SC-2023-001"})
MATCH (c2:Case)
WHERE c1 <> c2
  AND c1.case_type = c2.case_type
  AND any(word IN c1.catchwords WHERE word IN c2.catchwords)
RETURN c2.title, c2.citation, c2.case_type, c2.catchwords
LIMIT 10;

// E9. Retrieve precedent network for RAG context window
MATCH (c:Case {case_id: "CASE-BD-SC-2023-001"})
OPTIONAL MATCH path = (c)-[:CITES*1..2]->(precedent:Case)
WITH c, collect(DISTINCT precedent) AS precedent_network
UNWIND precedent_network AS prec
OPTIONAL MATCH (prec)-[:INTERPRETS]->(sec:Section)
RETURN c.title AS focus_case,
       collect({
         case: prec.title,
         citation: prec.citation,
         summary: prec.summary,
         sections: collect(DISTINCT sec.section_number)
       }) AS precedent_context;

// E10. Full RAG context: Case with all connected entities
MATCH (c:Case {case_id: "CASE-BD-SC-2023-001"})
OPTIONAL MATCH (c)-[:CITES]->(cited:Case)
OPTIONAL MATCH (c)-[:INTERPRETS]->(sec:Section)
OPTIONAL MATCH (c)-[:APPLIES]->(prin:LegalPrinciple)
OPTIONAL MATCH (c)-[:ADDRESSES]->(issue:LegalIssue)
OPTIONAL MATCH (c)-[:DECIDED_BY]->(judge:Judge)
RETURN {
  case: c,
  cited_cases: collect(DISTINCT cited),
  sections: collect(DISTINCT sec),
  principles: collect(DISTINCT prin),
  issues: collect(DISTINCT issue),
  judges: collect(DISTINCT judge)
} AS full_context;

// ============================================================================
// F. LEGAL REASONING QUERIES (10 queries)
// ============================================================================

// F1. Find interpretation lineage for a section
MATCH (sec:Section {section_number: "302", is_current_version: true})
MATCH (c:Case)-[r:INTERPRETS]->(sec)
RETURN c.title, c.citation, c.decision_date,
       r.interpretation_type, r.holding
ORDER BY c.decision_date;

// F2. Detect conflicts between cases addressing same issue
MATCH (c1:Case)-[r1:ADDRESSES]->(issue:LegalIssue)<-[r2:ADDRESSES]-(c2:Case)
WHERE c1.case_id < c2.case_id
  AND r1.holding <> r2.holding
  AND c1.status = "Active" AND c2.status = "Active"
RETURN issue.description AS conflicting_issue,
       c1.title AS case1, c1.citation AS cite1, r1.holding AS holding1,
       c2.title AS case2, c2.citation AS cite2, r2.holding AS holding2;

// F3. Find principle evolution over time
MATCH (c:Case)-[r:APPLIES]->(p:LegalPrinciple {name: "Basic Structure Doctrine"})
RETURN c.decision_date, c.jurisdiction, c.title, c.citation, r.application_type
ORDER BY c.decision_date;

// F4. Multi-hop reasoning: A cites B, B interprets C, C amends D
MATCH (a:Case {case_id: "CASE-BD-SC-2023-001"})-[:CITES]->(b:Case)
MATCH (b)-[:INTERPRETS]->(c:Section)
MATCH (c)-[:AMENDS]->(d:Section)
RETURN a.title AS starting_case,
       b.title AS cited_case,
       c.section_number AS interpreted_section,
       c.version AS current_version,
       d.version AS previous_version;

// F5. Find overruling cascade (A overrules B, C overrules A)
MATCH (c:Case)-[:CITES {citation_type: "Overruled"}]->(a:Case)
MATCH (a)-[:CITES {citation_type: "Overruled"}]->(b:Case)
RETURN c.title AS latest_case, c.decision_date AS latest_date,
       a.title AS middle_case, a.decision_date AS middle_date,
       b.title AS original_case, b.decision_date AS original_date
ORDER BY c.decision_date DESC;

// F6. Find inconsistent interpretations of same section
MATCH (c1:Case)-[r1:INTERPRETS]->(sec:Section)<-[r2:INTERPRETS]-(c2:Case)
WHERE c1.case_id < c2.case_id
  AND r1.interpretation_type <> r2.interpretation_type
RETURN sec.section_number, sec.title,
       c1.title AS case1, r1.interpretation_type AS type1, r1.holding AS holding1,
       c2.title AS case2, r2.interpretation_type AS type2, r2.holding AS holding2;

// F7. Find ratio decidendi for all cases on an issue
MATCH (c:Case)-[r:ADDRESSES]->(issue:LegalIssue {issue_id: "ISSUE-CONST-001"})
RETURN c.title, c.citation, c.decision_date,
       r.holding, r.ratio_decidendi, r.is_main_issue
ORDER BY c.decision_date;

// F8. Trace constitutional interpretation evolution
MATCH path = (recent:Case)-[:CITES*1..3]->(historic:Case)
WHERE recent.case_type = "Constitutional"
  AND historic.case_type = "Constitutional"
  AND recent.decision_date > date("2010-01-01")
WITH recent, historic, path
MATCH (recent)-[:INTERPRETS]->(sec:Section)
WHERE sec.section_type = "Article"
RETURN recent.title AS recent_case,
       historic.title AS historic_precedent,
       sec.section_number AS article,
       length(path) AS precedent_distance
ORDER BY sec.section_number, length(path);

// F9. Find cases with conflicting treatments of same precedent
MATCH (p:Case)<-[r1:CITES]-(c1:Case)
MATCH (p)<-[r2:CITES]-(c2:Case)
WHERE c1.case_id < c2.case_id
  AND r1.treatment = "Positive" AND r2.treatment = "Negative"
RETURN p.title AS precedent, p.citation,
       c1.title AS positive_treatment, c1.decision_date AS pos_date,
       c2.title AS negative_treatment, c2.decision_date AS neg_date;

// F10. Find legislative response to judicial interpretation
MATCH (c:Case)-[r_interp:INTERPRETS]->(sec_old:Section)
MATCH (sec_new:Section)-[r_amend:AMENDS]->(sec_old)
WHERE sec_old.section_number = sec_new.section_number
  AND r_amend.amendment_date > c.decision_date
RETURN c.title AS case,
       c.decision_date AS interpretation_date,
       r_interp.holding AS judicial_interpretation,
       sec_new.section_number AS section,
       r_amend.amendment_date AS amendment_date,
       r_amend.description AS legislative_response;

// ============================================================================
// G. DOMAIN-SPECIFIC QUERIES (8 queries)
// ============================================================================

// G1. Find criminal law precedents for murder cases
MATCH (c:Case {case_type: "Criminal"})
WHERE any(word IN c.catchwords WHERE word IN ["Murder", "Section 302"])
RETURN c.title, c.citation, c.decision_date, c.outcome
ORDER BY c.decision_date DESC;

// G2. Constitutional interpretation of Article 32/21
MATCH (c:Case)-[r:INTERPRETS]->(sec:Section)
WHERE sec.section_number IN ["32", "21"] AND sec.section_type = "Article"
RETURN c.title, c.citation, c.decision_date,
       sec.section_number AS article,
       r.interpretation_type,
       r.holding
ORDER BY c.decision_date;

// G3. Property law cases involving title disputes
MATCH (c:Case {case_type: "Civil"})
WHERE any(word IN c.catchwords WHERE word IN ["Property", "Title"])
RETURN c.title, c.citation, c.decision_date
ORDER BY c.decision_date DESC;

// G4. Tax law cases and interpretations since 2020
MATCH (c:Case {case_type: "Tax"})
WHERE c.decision_date >= date("2020-01-01")
OPTIONAL MATCH (c)-[r:INTERPRETS]->(sec:Section)
RETURN c.title, c.citation, c.decision_date,
       collect({section: sec.section_number, interpretation: r.interpretation_type}) AS interpretations
ORDER BY c.decision_date DESC;

// G5. Rape cases with evidence standard analysis
MATCH (c:Case)-[r:INTERPRETS]->(sec:Section {section_number: "376"})
RETURN c.title, c.citation, c.decision_date, c.status,
       r.interpretation_type, r.holding
ORDER BY c.decision_date;

// G6. Constitutional bench decisions by year
MATCH (c:Case {bench_type: "Constitution Bench"})
WITH c.decision_date.year AS year, count(c) AS decisions
RETURN year, decisions
ORDER BY year DESC;

// G7. Criminal appeals outcome analysis
MATCH (c:Case {case_type: "Criminal"})
WHERE c.case_number CONTAINS "Criminal Appeal"
RETURN c.outcome, count(c) AS count
ORDER BY count DESC;

// G8. Judge specialization analysis (most cases per domain)
MATCH (c:Case)-[:DECIDED_BY]->(j:Judge)
WITH j, c.case_type AS domain, count(c) AS case_count
RETURN j.name, j.court,
       collect({domain: domain, cases: case_count}) AS specializations
ORDER BY j.name;

// ============================================================================
// H. PERFORMANCE TESTING QUERIES (6 queries)
// ============================================================================

// H1. Large result set retrieval (all cases with relationships)
MATCH (c:Case)
OPTIONAL MATCH (c)-[r]-(related)
RETURN c, collect({type: type(r), node: related}) AS relationships
LIMIT 1000;

// H2. Deep traversal (10-hop precedent chain)
MATCH path = (c1:Case)-[:CITES*1..10]->(c2:Case)
WHERE c1.decision_date > date("2020-01-01")
RETURN c1.title AS recent_case,
       [node IN nodes(path) | node.short_title] AS precedent_chain,
       length(path) AS depth
ORDER BY depth DESC
LIMIT 100;

// H3. Complex multi-pattern match
MATCH (c:Case {jurisdiction: "BD", case_type: "Constitutional"})
MATCH (c)-[:CITES]->(precedent:Case {jurisdiction: "IN"})
MATCH (c)-[:INTERPRETS]->(sec:Section)
MATCH (c)-[:APPLIES]->(prin:LegalPrinciple)
MATCH (c)-[:DECIDED_BY]->(judge:Judge)
RETURN c.title,
       collect(DISTINCT precedent.citation) AS indian_precedents,
       collect(DISTINCT sec.section_number) AS sections,
       collect(DISTINCT prin.name) AS principles,
       collect(DISTINCT judge.name) AS judges;

// H4. Aggregations: Count cases per year per jurisdiction
MATCH (c:Case)
WITH c.jurisdiction AS jurisdiction,
     c.decision_date.year AS year,
     count(c) AS case_count
RETURN jurisdiction, year, case_count
ORDER BY jurisdiction, year;

// H5. Graph statistics
MATCH (c:Case)
WITH count(c) AS total_cases
MATCH (s:Statute)
WITH total_cases, count(s) AS total_statutes
MATCH (sec:Section)
WITH total_cases, total_statutes, count(sec) AS total_sections
MATCH ()-[r:CITES]->()
WITH total_cases, total_statutes, total_sections, count(r) AS total_citations
MATCH ()-[r2:INTERPRETS]->()
WITH total_cases, total_statutes, total_sections, total_citations, count(r2) AS total_interpretations
RETURN total_cases, total_statutes, total_sections, total_citations, total_interpretations;

// H6. Find most connected nodes (high degree centrality)
MATCH (c:Case)
OPTIONAL MATCH (c)-[r]-()
WITH c, count(r) AS degree
RETURN c.title, c.citation, degree
ORDER BY degree DESC
LIMIT 20;

// ============================================================================
// TEST QUERY SUMMARY
// ============================================================================
// Total Queries: 64
// A. Basic Retrieval: 10
// B. Precedent Chains: 12
// C. Temporal Queries: 10
// D. Multi-Jurisdiction: 8
// E. RAG-Optimized: 10
// F. Legal Reasoning: 10
// G. Domain-Specific: 8
// H. Performance Testing: 6
// ============================================================================
