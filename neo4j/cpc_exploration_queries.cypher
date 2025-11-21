// ============================================================
// CPC FULL TEXT - EXPLORATION QUERIES FOR NEO4J BROWSER
// ============================================================
// Now includes: 150 Sections, 50 Orders, 11 Parts, 14 Definitions
// ============================================================

// === OVERVIEW QUERIES ===

// 1. VIEW CPC STRUCTURE - All Parts
MATCH (p:Part)-[:PART_OF]->(stat:Statute {id: 'cpc_1908'})
RETURN p.part_number as Part, p.title as Title
ORDER BY p.part_number;

// 2. VIEW ALL ORDERS
MATCH (o:Order)-[:PART_OF]->(stat:Statute)
RETURN o.order_id as Order, o.title as Title
ORDER BY o.order_id
LIMIT 50;

// 3. SECTIONS BY PART
MATCH (s:Section)-[:BELONGS_TO_PART]->(p:Part)
RETURN p.part_number as Part,
       p.title as PartTitle,
       count(s) as SectionCount
ORDER BY p.part_number;

// === VISUALIZE CPC HIERARCHY ===

// 4. VISUALIZE PART I - SUITS IN GENERAL (with sections)
MATCH path = (p:Part {part_number: 'Part I'})<-[:BELONGS_TO_PART]-(s:Section)
RETURN path
LIMIT 50;

// 5. VISUALIZE SPECIFIC ORDER - ORDER VI (PLEADINGS)
MATCH path = (o:Order {order_id: 'ORDER VI'})-[*1..2]-(n)
RETURN path;

// 6. SHOW HIERARCHY: Statute → Parts → Sections
MATCH path = (stat:Statute {id: 'cpc_1908'})<-[:PART_OF]-(p:Part)<-[:BELONGS_TO_PART]-(s:Section)
RETURN path
LIMIT 100;

// === CASE-CENTRIC QUERIES ===

// 7. CASES WITH THEIR APPLIED SECTIONS (Enhanced View)
MATCH path = (c:Case)-[:APPLIES_SECTION]->(s:Section)-[:PART_OF|BELONGS_TO_PART*0..2]-(p)
WHERE p:Part OR p:Statute
RETURN path;

// 8. FIND WHICH PART A CASE RELATES TO
MATCH (c:Case)-[:APPLIES_SECTION]->(s:Section)-[:BELONGS_TO_PART]->(p:Part)
RETURN c.citation as Case,
       c.name as CaseName,
       collect(DISTINCT p.title) as RelatedParts;

// 9. SECTIONS MOST FREQUENTLY CITED IN CASES
MATCH (s:Section)<-[:APPLIES_SECTION]-(c:Case)
RETURN s.section_id as Section,
       s.title as Title,
       count(c) as CaseCount
ORDER BY CaseCount DESC;

// === SECTION-SPECIFIC QUERIES ===

// 10. FIND SECTION 115 (Revision) - Complete Info
MATCH (s:Section)
WHERE s.section_id CONTAINS '115'
OPTIONAL MATCH (s)-[:BELONGS_TO_PART]->(p:Part)
OPTIONAL MATCH (c:Case)-[:APPLIES_SECTION]->(s)
RETURN s.section_id as Section,
       s.title as Title,
       p.title as Part,
       collect(c.citation) as CitedInCases;

// 11. EXPLORE ORDER VI (Pleadings & Amendments)
MATCH (o:Order {order_id: 'ORDER VI'})
RETURN o.order_id as Order,
       o.title as Title;

// 12. FIND ALL SECTIONS IN PART VII (APPEALS)
MATCH (s:Section)-[:BELONGS_TO_PART]->(p:Part {part_number: 'Part VII'})
RETURN s.section_id as Section,
       s.title as Title
ORDER BY s.section_number;

// === DEFINITION QUERIES ===

// 13. VIEW ALL LEGAL DEFINITIONS
MATCH (d:Definition)-[:DEFINED_IN]->(s:Section)
RETURN d.term as Term,
       s.section_id as DefinedIn
ORDER BY d.term;

// 14. FIND DEFINITION OF "DECREE"
MATCH (d:Definition {term: "decree"})-[:DEFINED_IN]->(s:Section)
RETURN d.term as Term,
       s.section_id as Section,
       d.defined_in as Source;

// 15. VISUALIZE DEFINITIONS AND THEIR SECTION
MATCH path = (d:Definition)-[:DEFINED_IN]->(s:Section)
RETURN path;

// === COMPLEX ANALYTICAL QUERIES ===

// 16. COMPARE REVISION vs APPEAL SECTIONS
// Find sections related to Revision
MATCH (c1:Case {topic: "Revision"})-[:APPLIES_SECTION]->(s1:Section)
WITH collect(DISTINCT s1.section_id) as RevisionSections
// Find sections related to Appeal
MATCH (c2:Case {topic: "Appeal"})-[:APPLIES_SECTION]->(s2:Section)
RETURN "Revision" as Topic, RevisionSections as Sections
UNION
MATCH (c2:Case {topic: "Appeal"})-[:APPLIES_SECTION]->(s2:Section)
WITH collect(DISTINCT s2.section_id) as AppealSections
RETURN "Appeal" as Topic, AppealSections as Sections;

// 17. PARTS MOST REFERENCED BY CASES
MATCH (c:Case)-[:APPLIES_SECTION]->(s:Section)-[:BELONGS_TO_PART]->(p:Part)
RETURN p.part_number as Part,
       p.title as Title,
       count(DISTINCT c) as CaseCount,
       collect(DISTINCT c.citation) as Cases
ORDER BY CaseCount DESC;

// 18. FIND SECTIONS WITH NO CASE REFERENCES (Unused in Case Law)
MATCH (s:Section)
WHERE NOT (s)<-[:APPLIES_SECTION]-(:Case)
RETURN s.section_id as Section,
       s.title as Title
LIMIT 20;

// === FULL GRAPH VISUALIZATIONS ===

// 19. COMPLETE CASE ECOSYSTEM (Cases + Sections + Parts)
MATCH path = (c:Case)-[*1..3]-(n)
WHERE n:Section OR n:Part OR n:Judge OR n:Court OR n:Principle
RETURN path
LIMIT 200;

// 20. CPC STRUCTURE OVERVIEW (Statute → Parts → Sections → Cases)
MATCH path = (stat:Statute {id: 'cpc_1908'})<-[:PART_OF*1..3]-(n)
RETURN path
LIMIT 300;

// === SEARCH QUERIES ===

// 21. SEARCH SECTIONS BY KEYWORD IN TITLE
MATCH (s:Section)
WHERE toLower(s.title) CONTAINS 'appeal'
   OR toLower(s.title) CONTAINS 'revision'
RETURN s.section_id as Section,
       s.title as Title
LIMIT 20;

// 22. FIND ORDERS RELATED TO EXECUTION
MATCH (o:Order)
WHERE toLower(o.title) CONTAINS 'execution'
RETURN o.order_id as Order,
       o.title as Title;

// 23. SECTIONS IN PART II (EXECUTION)
MATCH (s:Section)-[:BELONGS_TO_PART]->(p:Part {part_number: 'Part II'})
RETURN s.section_id as Section,
       s.title as Title,
       s.section_number as Number
ORDER BY s.section_number
LIMIT 20;

// === STATISTICS ===

// 24. COUNT NODES BY TYPE
MATCH (n)
RETURN labels(n)[0] as NodeType,
       count(*) as Count
ORDER BY Count DESC;

// 25. COUNT RELATIONSHIPS BY TYPE
MATCH ()-[r]->()
RETURN type(r) as RelationshipType,
       count(*) as Count
ORDER BY Count DESC;

// ============================================================
// RECOMMENDED STARTING POINTS:
//
// For Structure: Run Queries 1, 2, 6
// For Cases: Run Queries 7, 8, 9
// For Definitions: Run Query 13
// For Visualization: Run Query 19
// ============================================================
