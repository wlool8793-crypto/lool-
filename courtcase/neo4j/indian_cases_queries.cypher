// ============================================================
// INDIAN CASES - EXPLORATION QUERIES FOR NEO4J BROWSER
// ============================================================
// 30 Indian Supreme Court cases integrated with CPC structure
// ============================================================

// === INDIAN CASES OVERVIEW ===

// 1. VIEW ALL INDIAN CASES
MATCH (c:Case {source: 'IndianKanoon'})
RETURN c.name as CaseName,
       c.citation as Citation,
       c.date as Date,
       c.case_type as Type
ORDER BY c.date DESC
LIMIT 30;

// 2. INDIAN CASES BY TYPE
MATCH (c:Case {source: 'IndianKanoon'})
RETURN c.case_type as CaseType,
       count(*) as Count
ORDER BY Count DESC;

// 3. VISUALIZE ALL INDIAN CASES WITH THEIR CONNECTIONS
MATCH path = (c:Case {source: 'IndianKanoon'})-[r]-(n)
WHERE type(r) IN ['APPLIES_SECTION', 'DECIDED_BY', 'BEFORE_COURT', 'PETITIONER', 'RESPONDENT']
RETURN path
LIMIT 150;

// === INDIAN CASES AND CPC SECTIONS ===

// 4. INDIAN CASES CITING CPC SECTIONS
MATCH (c:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
RETURN c.name as Case,
       c.date as Date,
       collect(s.section_id) as SectionsCited
ORDER BY c.date DESC;

// 5. MOST CITED CPC SECTIONS BY INDIAN CASES
MATCH (c:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
RETURN s.section_id as Section,
       s.title as SectionTitle,
       count(c) as IndianCasesCount
ORDER BY IndianCasesCount DESC
LIMIT 20;

// 6. VISUALIZE INDIAN CASES → SECTIONS → PARTS
MATCH path = (c:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)-[:BELONGS_TO_PART]->(p:Part)
RETURN path
LIMIT 100;

// 7. COMPARE: SECTIONS CITED BY INDIAN vs BANGLADESH CASES
// Indian cases
MATCH (ic:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
WITH collect(DISTINCT s.section_id) as IndianSections
// Bangladesh cases
MATCH (bc:Case)
WHERE bc.source IS NULL OR bc.source <> 'IndianKanoon'
MATCH (bc)-[:APPLIES_SECTION]->(s2:Section)
WITH IndianSections, collect(DISTINCT s2.section_id) as BangladeshSections
RETURN IndianSections, BangladeshSections;

// === JUDGES IN INDIAN CASES ===

// 8. JUDGES IN INDIAN CASES
MATCH (c:Case {source: 'IndianKanoon'})-[:DECIDED_BY]->(j:Judge)
RETURN j.name as Judge,
       count(c) as CasesDecided
ORDER BY CasesDecided DESC;

// 9. VISUALIZE JUDGE NETWORK
MATCH path = (j:Judge)<-[:DECIDED_BY]-(c:Case {source: 'IndianKanoon'})-[:BEFORE_COURT]->(court:Court)
RETURN path
LIMIT 50;

// 10. FIND JUDGES WHO REFERENCED SPECIFIC CPC SECTION
MATCH (j:Judge)<-[:DECIDED_BY]-(c:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
WHERE s.section_id CONTAINS '115'
RETURN j.name as Judge,
       collect(c.name) as Cases
ORDER BY j.name;

// === COURTS ===

// 11. COURTS HEARING INDIAN CASES
MATCH (c:Case {source: 'IndianKanoon'})-[:BEFORE_COURT]->(court:Court)
RETURN court.name as Court,
       count(c) as CasesCount
ORDER BY CasesCount DESC;

// 12. SUPREME COURT OF INDIA CASES
MATCH (court:Court {name: 'Supreme Court of India'})<-[:BEFORE_COURT]-(c:Case)
RETURN c.name as Case,
       c.date as Date,
       c.case_type as Type
ORDER BY c.date DESC
LIMIT 20;

// === PARTIES IN INDIAN CASES ===

// 13. MOST FREQUENT LITIGANTS (PETITIONERS)
MATCH (c:Case {source: 'IndianKanoon'})-[:PETITIONER]->(p:Party)
RETURN p.name as Petitioner,
       count(c) as CasesCount
ORDER BY CasesCount DESC
LIMIT 10;

// 14. MOST FREQUENT RESPONDENTS
MATCH (c:Case {source: 'IndianKanoon'})-[:RESPONDENT]->(p:Party)
RETURN p.name as Respondent,
       count(c) as CasesCount
ORDER BY CasesCount DESC
LIMIT 10;

// 15. VISUALIZE PARTIES AND THEIR CASES
MATCH path = (p:Party)<-[:PETITIONER|RESPONDENT]-(c:Case {source: 'IndianKanoon'})
RETURN path
LIMIT 100;

// === CASE TYPES AND TOPICS ===

// 16. CRIMINAL vs CIVIL CASES
MATCH (c:Case {source: 'IndianKanoon'})-[:BELONGS_TO_TOPIC]->(t:Topic)
RETURN t.name as Topic,
       count(c) as Count
ORDER BY Count DESC;

// 17. VISUALIZE CASES BY TOPIC
MATCH path = (c:Case {source: 'IndianKanoon'})-[:BELONGS_TO_TOPIC]->(t:Topic)
RETURN path;

// === CROSS-JURISDICTION ANALYSIS ===

// 18. COMPARE INDIAN AND BANGLADESH LEGAL SYSTEMS
MATCH (ic:Case {source: 'IndianKanoon'})-[:FROM_COUNTRY]->(india:Country {name: 'India'})
WITH count(ic) as IndianCount
MATCH (bc:Case)
WHERE bc.source IS NULL OR bc.source <> 'IndianKanoon'
MATCH (bc)-[:FROM_COUNTRY|DECIDED_BY*1..2]-(n)
WITH IndianCount, count(DISTINCT bc) as BangladeshCount
RETURN IndianCount, BangladeshCount;

// 19. SECTIONS USED IN BOTH JURISDICTIONS
MATCH (s:Section)<-[:APPLIES_SECTION]-(c:Case)
WITH s,
     sum(CASE WHEN c.source = 'IndianKanoon' THEN 1 ELSE 0 END) as IndianUse,
     sum(CASE WHEN c.source IS NULL OR c.source <> 'IndianKanoon' THEN 1 ELSE 0 END) as BangladeshUse
WHERE IndianUse > 0 AND BangladeshUse > 0
RETURN s.section_id as Section,
       s.title as Title,
       IndianUse,
       BangladeshUse
ORDER BY (IndianUse + BangladeshUse) DESC;

// 20. VISUALIZE COMPLETE CROSS-JURISDICTION GRAPH
MATCH path = (c:Case)-[:APPLIES_SECTION]->(s:Section)
WHERE s.section_id IN ['Section 2', 'Section 10', 'Section 11', 'Section 115']
RETURN path;

// === TEMPORAL ANALYSIS ===

// 21. CASES BY YEAR
MATCH (c:Case {source: 'IndianKanoon'})
WHERE c.year IS NOT NULL
RETURN c.year as Year,
       count(*) as CasesCount
ORDER BY Year DESC;

// 22. RECENT CASES (2023-2024)
MATCH (c:Case {source: 'IndianKanoon'})
WHERE c.year >= 2023
RETURN c.name as Case,
       c.date as Date,
       c.case_type as Type
ORDER BY c.date DESC;

// === ADVANCED QUERIES ===

// 23. FIND CASES WITH MOST SECTIONS CITED
MATCH (c:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
WITH c, count(s) as SectionsCount
WHERE SectionsCount > 0
RETURN c.name as Case,
       c.date as Date,
       SectionsCount
ORDER BY SectionsCount DESC
LIMIT 10;

// 24. FIND JUDGES WHO CITE SAME SECTIONS
MATCH (j1:Judge)<-[:DECIDED_BY]-(c1:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
MATCH (j2:Judge)<-[:DECIDED_BY]-(c2:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s)
WHERE j1.name < j2.name
RETURN j1.name as Judge1,
       j2.name as Judge2,
       collect(DISTINCT s.section_id) as CommonSections,
       count(DISTINCT s) as Count
ORDER BY Count DESC
LIMIT 10;

// 25. COMPLETE ECOSYSTEM VIEW (ALL DATA)
MATCH path = (c:Case)-[r]-(n)
WHERE c.source = 'IndianKanoon'
RETURN path
LIMIT 200;

// 26. SEARCH CASES BY KEYWORD
MATCH (c:Case {source: 'IndianKanoon'})
WHERE toLower(c.name) CONTAINS 'income tax'
   OR toLower(c.name) CONTAINS 'taxation'
RETURN c.name as Case,
       c.date as Date
LIMIT 10;

// 27. FIND LANDMARK SUPREME COURT CASES WITH CPC CITATIONS
MATCH (court:Court {name: 'Supreme Court of India'})<-[:BEFORE_COURT]-(c:Case)-[:APPLIES_SECTION]->(s:Section)
RETURN c.name as Case,
       c.date as Date,
       collect(s.section_id) as CPCSections
ORDER BY c.date DESC
LIMIT 15;

// === STATISTICS ===

// 28. INDIAN CASES STATISTICS SUMMARY
MATCH (c:Case {source: 'IndianKanoon'})
WITH count(c) as TotalCases
MATCH (c2:Case {source: 'IndianKanoon'})-[:APPLIES_SECTION]->(s:Section)
WITH TotalCases, count(DISTINCT c2) as CasesWithSections, count(DISTINCT s) as UniqueSections
MATCH (c3:Case {source: 'IndianKanoon'})-[:DECIDED_BY]->(j:Judge)
WITH TotalCases, CasesWithSections, UniqueSections, count(DISTINCT j) as UniqueJudges
MATCH (c4:Case {source: 'IndianKanoon'})-[:PETITIONER|RESPONDENT]->(p:Party)
WITH TotalCases, CasesWithSections, UniqueSections, UniqueJudges, count(DISTINCT p) as UniqueParties
RETURN TotalCases,
       CasesWithSections,
       UniqueSections,
       UniqueJudges,
       UniqueParties;

// 29. GRAPH DENSITY ANALYSIS
MATCH (c:Case {source: 'IndianKanoon'})-[r]->()
RETURN c.name as Case,
       count(r) as OutgoingRelationships
ORDER BY OutgoingRelationships DESC
LIMIT 10;

// 30. FIND ISOLATED CASES (NO SECTION CITATIONS)
MATCH (c:Case {source: 'IndianKanoon'})
WHERE NOT (c)-[:APPLIES_SECTION]->()
RETURN c.name as Case,
       c.date as Date
LIMIT 10;

// ============================================================
// RECOMMENDED STARTING POINTS:
//
// For Overview: Run Queries 1, 2, 3
// For CPC Analysis: Run Queries 4, 5, 6
// For Judges: Run Query 8
// For Cross-Jurisdiction: Run Queries 18, 19, 20
// For Visualization: Run Query 3, 25
// ============================================================
