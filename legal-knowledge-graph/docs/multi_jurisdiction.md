# Multi-Jurisdiction Design

## Overview

The Legal Knowledge Graph schema is designed to support multiple legal jurisdictions, with initial focus on Bangladesh (BD), India (IN), and Pakistan (PK), all sharing a common law heritage.

## Design Principles

### 1. Jurisdiction as First-Class Concept

Jurisdiction is not just a property but a core structural element:

```cypher
// Jurisdiction node
CREATE (bd:Jurisdiction {
  jurisdiction_id: 'JUR-BD',
  code: 'BD',
  name: 'Bangladesh',
  jurisdiction_type: 'Country',
  legal_system: 'Common Law',
  independence_date: date('1971-12-16')
})
```

### 2. Dual Representation

**Property-Based** (for filtering):
```cypher
(:Case {jurisdiction: 'BD'})
(:Statute {jurisdiction: 'IN'})
```

**Relationship-Based** (for metadata and hierarchy):
```cypher
(:Case)-[:IN_JURISDICTION]->(:Jurisdiction {code: 'BD'})
```

This dual approach enables:
- Fast filtering by jurisdiction property
- Rich metadata through jurisdiction nodes
- Hierarchical jurisdiction modeling (country > state > district)

### 3. Cross-Jurisdiction Citations

Cases can cite precedents from other jurisdictions:

```cypher
MATCH (bd_case:Case {jurisdiction: 'BD'})
MATCH (in_case:Case {jurisdiction: 'IN'})
CREATE (bd_case)-[:CITES {
  citation_type: 'Referred',
  treatment: 'Persuasive',
  weight: 0.6,
  context: 'Court referred to Indian precedent for guidance'
}]->(in_case)
```

## Jurisdiction Hierarchy

### Country-Level

```cypher
CREATE (bd:Jurisdiction {
  jurisdiction_id: 'JUR-BD',
  code: 'BD',
  name: 'Bangladesh',
  jurisdiction_type: 'Country',
  legal_system: 'Common Law'
})
```

### State/Province-Level

```cypher
// For federal systems like India
CREATE (delhi:Jurisdiction {
  jurisdiction_id: 'JUR-IN-DELHI',
  code: 'IN-DL',
  name: 'Delhi',
  jurisdiction_type: 'Union Territory',
  parent_jurisdiction: 'JUR-IN',
  legal_system: 'Common Law'
})

// Link to parent
MATCH (delhi:Jurisdiction {code: 'IN-DL'})
MATCH (india:Jurisdiction {code: 'IN'})
CREATE (delhi)-[:PART_OF]->(india)
```

### District-Level

```cypher
CREATE (dhaka:Jurisdiction {
  jurisdiction_id: 'JUR-BD-DH',
  code: 'BD-DH',
  name: 'Dhaka',
  jurisdiction_type: 'District',
  parent_jurisdiction: 'JUR-BD'
})
```

## Common Law Heritage

### Shared Legal Principles

Bangladesh, India, and Pakistan share common law foundations:

```cypher
// Legal principle recognized across jurisdictions
CREATE (principle:LegalPrinciple {
  principle_id: 'PRINCIPLE-NAT-JUSTICE',
  name: 'Natural Justice',
  latin_name: 'audi alteram partem',
  jurisdiction: ['BD', 'IN', 'PK'],  // Array for multiple
  origin: 'common law',
  recognized_since: date('1858-08-02')  // British India era
})
```

### Colonial Era Statutes

Many statutes predate independence:

```cypher
// Indian Penal Code (inherited by BD and PK)
CREATE (ipc:Statute {
  statute_id: 'STAT-IPC-1860',
  name: 'Indian Penal Code, 1860',
  enactment_date: date('1860-10-06'),
  jurisdiction: 'IN',  // Original
  inherited_by: ['BD', 'PK'],  // Inherited jurisdictions
  status: 'Active'
})
```

Query inherited statutes:
```cypher
MATCH (s:Statute)
WHERE $jurisdiction IN s.inherited_by
RETURN s
```

## Jurisdiction-Specific Features

### Bangladesh

**Court Hierarchy**:
- Supreme Court (Appellate + High Court Divisions)
- District Courts
- Subordinate Courts

**Key Statutes**:
- Constitution of Bangladesh, 1972
- Penal Code, 1860
- Code of Civil Procedure, 1908
- Evidence Act, 1872

### India

**Court Hierarchy**:
- Supreme Court of India
- High Courts (25 states/territories)
- District Courts
- Subordinate Courts

**Key Statutes**:
- Constitution of India, 1950
- Indian Penal Code, 1860 (replaced by Bharatiya Nyaya Sanhita, 2023)
- Code of Criminal Procedure, 1973
- Civil Procedure Code, 1908

### Pakistan

**Court Hierarchy**:
- Supreme Court of Pakistan
- High Courts (5 provinces)
- District Courts
- Subordinate Courts

**Key Statutes**:
- Constitution of Pakistan, 1973
- Pakistan Penal Code, 1860
- Code of Criminal Procedure, 1898
- Qanun-e-Shahadat Order, 1984

## Cross-Jurisdiction Relationships (Iteration 2)

### Overview

Iteration 2 introduces three new relationship types to model comparative legal analysis across jurisdictions:
- **HARMONIZED_WITH**: Aligned legal interpretations
- **DIVERGES_FROM**: Differing interpretations
- **CONFLICTS_WITH**: Direct conflicts requiring resolution

### HARMONIZED_WITH Relationship

**Purpose**: Track cases with aligned legal interpretations across jurisdictions

```cypher
// Create harmonization link
MATCH (bd_case:Case {case_id: 'bd_2020_sc_045', jurisdiction: 'BD'})
MATCH (in_case:Case {case_id: 'in_1978_sc_597', jurisdiction: 'IN'})
CREATE (bd_case)-[:HARMONIZED_WITH {
  jurisdictions: ['BD', 'IN'],
  principle: 'Right to life under Article 32 includes right to livelihood and dignity',
  reasoning_similarity: 0.92,
  harmonized_by: 'Bangladesh SC in Rahman v. State (2020)',
  common_statute: 'Article 32 (IN) / Article 102 (BD)',
  harmonization_date: date('2020-06-15'),
  notes: 'Both courts recognized broad interpretation of constitutional right to life',
  created_at: datetime()
}]->(in_case)
```

**Query Harmonized Precedents**:
```cypher
// Find harmonized interpretations across jurisdictions
MATCH (case1:Case {jurisdiction: 'BD'})-[h:HARMONIZED_WITH]->(case2:Case)
WHERE h.reasoning_similarity > 0.85
  AND case2.jurisdiction IN ['IN', 'PK']
RETURN case1.citation, case2.citation, h.principle, h.reasoning_similarity
ORDER BY h.harmonization_date DESC
```

### DIVERGES_FROM Relationship

**Purpose**: Track differing legal interpretations on similar issues

```cypher
// Create divergence link
MATCH (bd_case:Case {case_id: 'bd_2019_sc_123', jurisdiction: 'BD'})
MATCH (in_case:Case {case_id: 'in_2016_sc_2181', jurisdiction: 'IN'})
CREATE (bd_case)-[:DIVERGES_FROM {
  jurisdictions: ['BD', 'IN'],
  reason: 'Different approach to balancing free speech against national security',
  point_of_divergence: 'Threshold for establishing seditious intent and requirement of actual incitement',
  severity: 'Significant',  // Minor, Moderate, Significant
  legal_basis: 'Section 124A IPC interpreted differently',
  divergence_date: date('2019-03-20'),
  reconciliation_attempted: false,
  notes: 'Bangladesh court took more restrictive view requiring clear and present danger',
  created_at: datetime()
}]->(in_case)
```

**Query Divergent Interpretations**:
```cypher
// Find significant divergences across jurisdictions
MATCH (case1:Case)-[d:DIVERGES_FROM]->(case2:Case)
WHERE d.severity = 'Significant'
  AND case1.jurisdiction = 'BD'
RETURN
  case1.citation,
  case2.citation,
  case2.jurisdiction,
  d.point_of_divergence,
  d.reason,
  d.divergence_date
ORDER BY d.divergence_date DESC
```

### CONFLICTS_WITH Relationship

**Purpose**: Track direct conflicts requiring resolution by higher authority

```cypher
// Create conflict within same jurisdiction
MATCH (case1:Case {case_id: 'bd_2021_hc_234'})
MATCH (case2:Case {case_id: 'bd_2020_hc_189'})
CREATE (case1)-[:CONFLICTS_WITH {
  issue: 'Whether non-bailable offense accused can be granted bail before trial based on delay',
  conflict_type: 'Direct Conflict',
  resolution: 'Resolved by Supreme Court holding that delay warrants bail consideration',
  resolution_case_id: 'bd_2022_sc_067',
  resolution_date: date('2022-08-15'),
  resolution_status: 'Resolved',  // Unresolved, Resolved, Partially Resolved, Pending Higher Court
  conflict_severity: 'High',  // Low, Medium, High, Critical
  same_jurisdiction: true,
  binding_hierarchy: 'Equal level - needed Supreme Court resolution',
  notes: 'Created legal uncertainty for 8 months until Supreme Court clarified',
  created_at: datetime()
}]->(case2)

// Create cross-jurisdiction conflict
MATCH (bd_case:Case {case_id: 'bd_2023_sc_012', jurisdiction: 'BD'})
MATCH (in_case:Case {case_id: 'in_2017_sc_494', jurisdiction: 'IN'})
CREATE (bd_case)-[:CONFLICTS_WITH {
  issue: 'Whether right to privacy extends to protection of biometric data collected by state',
  conflict_type: 'Inter-Jurisdictional Conflict',
  resolution: null,
  resolution_case_id: null,
  resolution_status: 'Unresolved',
  conflict_severity: 'Medium',
  same_jurisdiction: false,
  binding_hierarchy: 'Different jurisdictions - no formal precedential relationship',
  notes: 'Bangladesh SC took narrower view of data privacy rights',
  created_at: datetime()
}]->(in_case)
```

**Query Unresolved Conflicts**:
```cypher
// Find unresolved conflicts requiring attention
MATCH (case1:Case)-[c:CONFLICTS_WITH]->(case2:Case)
WHERE c.resolution_status = 'Unresolved'
  AND c.conflict_severity IN ['High', 'Critical']
RETURN
  case1.citation,
  case2.citation,
  c.issue,
  c.conflict_type,
  c.same_jurisdiction,
  c.conflict_severity
ORDER BY c.conflict_severity DESC, case1.decision_date DESC
```

**Track Conflict Resolution**:
```cypher
// Find conflict resolution chains
MATCH (case1:Case)-[c:CONFLICTS_WITH]->(case2:Case)
WHERE c.resolution_case_id IS NOT NULL
MATCH (resolution:Case {case_id: c.resolution_case_id})
RETURN
  case1.citation as conflicting_case_1,
  case2.citation as conflicting_case_2,
  resolution.citation as resolved_by,
  c.resolution,
  c.resolution_date
```

## Comparative Legal Analysis Queries

### Pattern 1: Jurisdiction Harmony Analysis

```cypher
// Analyze harmonization between Bangladesh and India
MATCH (bd:Case {jurisdiction: 'BD'})-[h:HARMONIZED_WITH]->(in:Case {jurisdiction: 'IN'})
WHERE h.reasoning_similarity > 0.85
RETURN
  count(*) as harmonized_cases,
  collect(DISTINCT h.principle) as common_principles,
  avg(h.reasoning_similarity) as avg_similarity
```

### Pattern 2: Divergence Mapping

```cypher
// Map areas of divergence between jurisdictions
MATCH (case1:Case)-[d:DIVERGES_FROM]->(case2:Case)
WHERE case1.jurisdiction = 'BD' AND case2.jurisdiction = 'IN'
RETURN
  d.point_of_divergence,
  d.severity,
  count(*) as divergence_count,
  collect({
    bd_case: case1.citation,
    in_case: case2.citation,
    date: d.divergence_date
  }) as examples
ORDER BY divergence_count DESC
```

### Pattern 3: Conflict Detection for Case Research

```cypher
// Check if a case conflicts with other precedents
MATCH (target:Case {case_id: $case_id})
MATCH (target)-[c:CONFLICTS_WITH]-(conflicting:Case)
WHERE c.resolution_status IN ['Unresolved', 'Pending Higher Court']
RETURN
  conflicting.citation,
  conflicting.jurisdiction,
  c.issue,
  c.conflict_severity,
  c.resolution_status,
  CASE
    WHEN c.same_jurisdiction THEN 'Same Jurisdiction - Higher Court Review Needed'
    ELSE 'Cross-Jurisdiction - Persuasive Authority Only'
  END as resolution_path
```

### Pattern 4: Cross-Jurisdiction Principle Evolution

```cypher
// Track how a principle evolved differently across jurisdictions
MATCH (principle:LegalPrinciple {name: 'Natural Justice'})
MATCH (chunk:Chunk)-[r:APPLIES_PRINCIPLE]->(principle)
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.jurisdiction IN ['BD', 'IN', 'PK']
WITH case, r.application_type as app_type
ORDER BY case.decision_date ASC
RETURN
  case.jurisdiction,
  case.decision_date,
  case.citation,
  app_type,
  collect(DISTINCT case.case_id) as related_cases
```

### Pattern 5: Comparative Constitutional Interpretation

```cypher
// Compare constitutional interpretations across jurisdictions
MATCH (bd_case:Case {jurisdiction: 'BD'})-[:APPLIES_SECTION]->(bd_sec:Section)
MATCH (in_case:Case {jurisdiction: 'IN'})-[:APPLIES_SECTION]->(in_sec:Section)
WHERE bd_sec.section_number = in_sec.section_number
  AND bd_sec.title CONTAINS 'Constitution'
  AND in_sec.title CONTAINS 'Constitution'
OPTIONAL MATCH (bd_case)-[h:HARMONIZED_WITH]-(in_case)
OPTIONAL MATCH (bd_case)-[d:DIVERGES_FROM]-(in_case)
RETURN
  bd_sec.section_number,
  bd_case.citation as bd_interpretation,
  in_case.citation as in_interpretation,
  CASE
    WHEN h IS NOT NULL THEN 'Harmonized'
    WHEN d IS NOT NULL THEN 'Divergent'
    ELSE 'Independent'
  END as relationship_type
```

## Conflict Detection Patterns

### Automatic Conflict Detection

```cypher
// Detect potential conflicts in similar cases with opposite outcomes
MATCH (case1:Case)-[:RAISES_ISSUE]->(issue:LegalIssue)<-[:RAISES_ISSUE]-(case2:Case)
WHERE case1.jurisdiction = case2.jurisdiction
  AND case1.outcome <> case2.outcome
  AND case1.case_id < case2.case_id  // Avoid duplicates
  AND case1.decision_date < case2.decision_date
  AND NOT exists((case1)-[:CONFLICTS_WITH]-(case2))
RETURN
  case1.citation,
  case2.citation,
  issue.name as common_issue,
  case1.outcome as outcome1,
  case2.outcome as outcome2,
  'Potential Conflict - Manual Review Needed' as status
```

### Conflict Resolution Workflow

```cypher
// Update conflict when resolution is found
MATCH (case1:Case)-[c:CONFLICTS_WITH]->(case2:Case)
WHERE c.resolution_status = 'Unresolved'
  AND $resolution_case_id IS NOT NULL
SET c.resolution_status = 'Resolved',
    c.resolution = $resolution_text,
    c.resolution_case_id = $resolution_case_id,
    c.resolution_date = date()
```

## Query Patterns

### Pattern 1: Single Jurisdiction Search

```cypher
// Find all criminal cases in Bangladesh
MATCH (c:Case)
WHERE c.jurisdiction = 'BD'
AND c.case_type = 'Criminal'
RETURN c
ORDER BY c.decision_date DESC
```

### Pattern 2: Cross-Jurisdiction Precedent Analysis

```cypher
// Find Bangladeshi cases citing Indian precedents
MATCH (bd:Case {jurisdiction: 'BD'})-[cite:CITES]->(in:Case {jurisdiction: 'IN'})
RETURN bd.title, in.title, cite.treatment, cite.context
```

### Pattern 3: Persuasive Precedent Discovery

```cypher
// Find relevant precedents from other common law jurisdictions
MATCH (case:Case {case_id: $case_id})
MATCH (case)-[:BELONGS_TO_DOMAIN]->(domain:LegalDomain)
MATCH (other:Case)-[:BELONGS_TO_DOMAIN]->(domain)
WHERE other.jurisdiction <> case.jurisdiction
AND other.jurisdiction IN ['BD', 'IN', 'PK']
AND other.precedent_value IN ['Binding', 'Persuasive']
RETURN other
ORDER BY other.decision_date DESC
LIMIT 10
```

### Pattern 4: Statutory Comparison

```cypher
// Compare similar statutes across jurisdictions
MATCH (s1:Statute {jurisdiction: 'BD', name: 'Penal Code'})
MATCH (s2:Statute {jurisdiction: 'IN', name: 'Indian Penal Code'})
MATCH (s3:Statute {jurisdiction: 'PK', name: 'Pakistan Penal Code'})
MATCH (s1)-[:CONTAINS]->(sec1:Section {section_number: '302'})
MATCH (s2)-[:CONTAINS]->(sec2:Section {section_number: '302'})
MATCH (s3)-[:CONTAINS]->(sec3:Section {section_number: '302'})
RETURN sec1.text as BD_version,
       sec2.text as IN_version,
       sec3.text as PK_version
```

### Pattern 5: Jurisdiction-Specific Court Hierarchy

```cypher
// Get court hierarchy for Bangladesh
MATCH (j:Jurisdiction {code: 'BD'})
MATCH (court:Court)-[:IN_JURISDICTION]->(j)
RETURN court.name, court.court_level
ORDER BY
  CASE court.court_level
    WHEN 'supreme' THEN 1
    WHEN 'high' THEN 2
    WHEN 'district' THEN 3
    WHEN 'subordinate' THEN 4
  END
```

## Handling Jurisdictional Variations

### Divergent Amendments

Same section, different amendments in different jurisdictions:

```cypher
// Section 302 amended differently in BD vs IN
MATCH (bd_sec:Section {section_id: 'SEC-BD-PC-302'})
MATCH (in_sec:Section {section_id: 'SEC-IN-IPC-302'})
MATCH (bd_v:Version)-[:VERSION_OF]->(bd_sec)
MATCH (in_v:Version)-[:VERSION_OF]->(in_sec)
WHERE bd_v.current = true AND in_v.current = true
RETURN bd_v.content as BD_current,
       in_v.content as IN_current,
       bd_v.valid_from as BD_since,
       in_v.valid_from as IN_since
```

### Jurisdiction-Specific Keywords

```cypher
// Keywords used differently across jurisdictions
CREATE (k:Keyword {
  keyword_id: 'KW-WRIT-PETITION',
  term: 'writ petition',
  normalized_term: 'writ petit',
  category: 'Procedure',
  jurisdiction_variants: {
    BD: 'Rule',
    IN: 'Writ Petition',
    PK: 'Constitutional Petition'
  }
})
```

## Citation Resolution Across Jurisdictions

### Citation Format Recognition

Different citation formats:
- Bangladesh: `2023 SCOB 456`, `2023 BLD 123`
- India: `AIR 2023 SC 1234`, `(2023) 1 SCC 100`
- Pakistan: `PLD 2023 SC 456`, `2023 SCMR 789`

```cypher
CREATE (c:Citation {
  citation_id: 'CIT-001',
  citation_text: '2023 SCOB 456',
  reporter: 'SCOB',
  year: 2023,
  volume: '456',
  jurisdiction: 'BD',
  citation_format: 'BD_SCOB'
})
```

### Cross-Reference Resolution

```cypher
// Resolve citation across jurisdictions
MATCH (citation:Citation {citation_text: $citation_text})
MATCH (case:Case)
WHERE case.citation = citation.citation_text
   OR case.neutral_citation = citation.citation_text
   OR $citation_text IN case.alternate_citations
RETURN case
```

## Legal System Differences

### Common Law vs Civil Law

While BD, IN, PK are common law, schema is extensible:

```cypher
CREATE (france:Jurisdiction {
  jurisdiction_id: 'JUR-FR',
  code: 'FR',
  name: 'France',
  jurisdiction_type: 'Country',
  legal_system: 'Civil Law',
  precedent_binding: false  // Civil law doesn't follow stare decisis
})
```

### Mixed Legal Systems

Some jurisdictions have mixed systems:

```cypher
CREATE (pakistan:Jurisdiction {
  jurisdiction_id: 'JUR-PK',
  code: 'PK',
  name: 'Pakistan',
  legal_system: 'Mixed',  // Common law + Islamic law
  legal_system_components: ['Common Law', 'Islamic Law'],
  sharia_courts: true
})
```

## Data Partitioning by Jurisdiction

For very large datasets, consider partitioning:

### Option 1: Label-Based Partitioning

```cypher
// Add jurisdiction label
(:Case:BD {jurisdiction: 'BD'})
(:Case:IN {jurisdiction: 'IN'})

// Query becomes more efficient
MATCH (c:Case:BD)
WHERE c.case_type = 'Criminal'
RETURN c
```

### Option 2: Database-Level Partitioning

For extreme scale:
- Separate Neo4j database per jurisdiction
- Federation layer for cross-jurisdiction queries
- GraphQL federation for unified API

## Internationalization (i18n)

### Multi-Language Support

```cypher
CREATE (case:Case {
  case_id: 'CASE-BD-001',
  title: 'State v. Rahman',
  title_bn: 'রাষ্ট্র বনাম রহমান',  // Bengali
  jurisdiction: 'BD',
  language: 'en',
  alternate_languages: ['bn']
})
```

### Language-Specific Full-Text Indexes

```cypher
// English analyzer
CREATE FULLTEXT INDEX case_fulltext_en IF NOT EXISTS
FOR (c:Case) ON EACH [c.title, c.summary]
OPTIONS {analyzer: 'english'};

// Bengali analyzer (if available)
CREATE FULLTEXT INDEX case_fulltext_bn IF NOT EXISTS
FOR (c:Case) ON EACH [c.title_bn, c.summary_bn]
OPTIONS {analyzer: 'standard'};  // Use standard for Bengali
```

## Best Practices

### 1. Always Filter by Jurisdiction

```cypher
// Good - filtered by jurisdiction
MATCH (c:Case {jurisdiction: 'BD'})
WHERE c.case_type = 'Criminal'
RETURN c

// Bad - searches all jurisdictions
MATCH (c:Case)
WHERE c.case_type = 'Criminal'
RETURN c
```

### 2. Use Jurisdiction Codes, Not Names

```cypher
// Good - using code
{jurisdiction: 'BD'}

// Bad - using name (can change)
{jurisdiction: 'Bangladesh'}
```

### 3. Handle Cross-Jurisdiction Carefully

```cypher
// Explicitly specify when crossing jurisdictions
MATCH (bd:Case {jurisdiction: 'BD'})-[:CITES]->(other:Case)
WHERE other.jurisdiction <> 'BD'
RETURN bd, other
```

### 4. Consider Jurisdiction in Embeddings

Jurisdiction-aware embeddings:
```python
text = f"[{jurisdiction}] {case_title}: {summary}"
embedding = embed(text)
```

## Future Extensions

### Planned Jurisdictions

1. United Kingdom (UK) - Colonial precedents
2. United States (US) - Persuasive authority
3. Canada (CA) - Common law reference
4. Australia (AU) - Common law reference
5. Malaysia (MY) - Similar legal system

### International Law

```cypher
CREATE (icj:Jurisdiction {
  jurisdiction_id: 'JUR-ICJ',
  code: 'ICJ',
  name: 'International Court of Justice',
  jurisdiction_type: 'International',
  legal_system: 'International Law'
})
```

---

**Version**: 2.0.0 (Iteration 2)
**Last Updated**: 2025-11-11

**Iteration 2 Additions**:
- HARMONIZED_WITH relationship for aligned interpretations
- DIVERGES_FROM relationship for differing interpretations
- CONFLICTS_WITH relationship for direct conflicts
- Comparative legal analysis query patterns
- Conflict detection and resolution workflows
