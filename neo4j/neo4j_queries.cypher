// ============================================================
// CPC Knowledge Graph - Neo4j Browser Queries
// ============================================================

// 1. VIEW ALL NODES (Overview)
MATCH (n)
RETURN n
LIMIT 100;

// 2. VIEW COMPLETE GRAPH STRUCTURE
MATCH path = (n)-[r]->(m)
RETURN path
LIMIT 200;

// 3. VIEW ONLY LEGAL CASES AND THEIR CONNECTIONS
MATCH path = (c:Case)-[r]-(n)
RETURN path;

// 4. FOCUS ON ONE CASE - "Siddique Mia vs Md Idris Miah"
MATCH path = (c:Case {citation: "60 DLR 20"})-[r*1..2]-(n)
RETURN path;

// 5. SHOW CASES BY TOPIC
MATCH (c:Case)-[:BELONGS_TO_TOPIC]->(t:Topic)
RETURN t.name as Topic, collect(c.citation) as Cases;

// 6. LEGAL PRINCIPLES AND THEIR CASES
MATCH (p:Principle)<-[:ESTABLISHES]-(c:Case)
RETURN p.name as Principle,
       p.description as Description,
       collect(c.name) as Cases;

// 7. SECTIONS AND CASES THAT USE THEM
MATCH (s:Section)<-[:APPLIES_SECTION]-(c:Case)
RETURN s.section_id as Section,
       s.title as Title,
       collect(c.citation) as Citations;

// 8. COURT HIERARCHY WITH CASES
MATCH (c:Case)-[:BEFORE_COURT]->(court:Court)
RETURN court.name as Court,
       count(c) as CaseCount,
       collect(c.citation) as Cases
ORDER BY CaseCount DESC;

// 9. JUDGES AND THEIR CASES
MATCH (j:Judge)<-[:DECIDED_BY]-(c:Case)
RETURN j.name as Judge,
       collect(c.citation + " (" + c.year + ")") as Cases;

// 10. PRECEDENT CITATION NETWORK
MATCH path = (c1:Case)-[:CITES_PRECEDENT]->(c2:Case)
RETURN path;

// 11. CASES WITH SECTION 115 (Revision)
MATCH (c:Case)-[:APPLIES_SECTION]->(s:Section)
WHERE s.section_id CONTAINS "115"
RETURN c.name as Case,
       c.citation as Citation,
       c.topic as Topic,
       s.section_id as Section;

// 12. CASES WITH INHERENT POWER
MATCH (c:Case)-[:APPLIES_SECTION]->(s:Section {section_id: "Section 151"})
RETURN c.name as Case,
       c.citation as Citation,
       c.abstract as Abstract;

// 13. ALL STATUTES AND THEIR SECTIONS
MATCH (sec:Section)-[:PART_OF]->(stat:Statute)
RETURN stat.name as Statute,
       collect(sec.section_id) as Sections;

// 14. PARTY INVOLVEMENT IN CASES
MATCH (p:Party)<-[:PETITIONER]-(c:Case)
RETURN p.name as Petitioner,
       collect(c.citation) as CasesAsPetitioner
UNION
MATCH (p:Party)<-[:RESPONDENT]-(c:Case)
RETURN p.name as Respondent,
       collect(c.citation) as CasesAsRespondent;

// 15. COMPLETE CASE DETAILS (Pick one case)
MATCH (c:Case {citation: "74 DLR 101"})
OPTIONAL MATCH (c)-[:DECIDED_BY]->(j:Judge)
OPTIONAL MATCH (c)-[:BEFORE_COURT]->(court:Court)
OPTIONAL MATCH (c)-[:APPLIES_SECTION]->(s:Section)
OPTIONAL MATCH (c)-[:ESTABLISHES]->(p:Principle)
RETURN c.name as Case,
       c.citation as Citation,
       c.year as Year,
       c.abstract as Abstract,
       collect(DISTINCT j.name) as Judges,
       court.name as Court,
       collect(DISTINCT s.section_id) as Sections,
       collect(DISTINCT p.name) as Principles;

// 16. GRAPH STATISTICS
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (:`'+label+'`) RETURN count(*) as count',{})
YIELD value
RETURN label, value.count as count
ORDER BY count DESC;

// NOTE: Query 16 requires APOC plugin. Use this alternative:
MATCH (n)
RETURN labels(n)[0] as NodeType, count(*) as Count
ORDER BY Count DESC;

// 17. RELATIONSHIP STATISTICS
MATCH ()-[r]->()
RETURN type(r) as RelationshipType, count(*) as Count
ORDER BY Count DESC;

// 18. FIND MOST CITED SECTIONS
MATCH (s:Section)<-[:APPLIES_SECTION]-(c:Case)
RETURN s.section_id as Section,
       s.title as Title,
       count(c) as UsedInCases
ORDER BY UsedInCases DESC;

// 19. CASES FROM 2007-2008 (Older cases)
MATCH (c:Case)
WHERE c.year >= 2007 AND c.year <= 2008
RETURN c.year as Year,
       c.name as Case,
       c.citation as Citation,
       c.topic as Topic
ORDER BY c.year;

// 20. VISUALIZE BY TOPIC (Run separately for each)
// For Revision cases:
MATCH path = (c:Case)-[*1..2]-(n)
WHERE c.topic = "Revision"
RETURN path;

// For Appeal cases:
MATCH path = (c:Case)-[*1..2]-(n)
WHERE c.topic = "Appeal"
RETURN path;

// For Inherent Power cases:
MATCH path = (c:Case)-[*1..2]-(n)
WHERE c.topic = "Inherent Power"
RETURN path;
