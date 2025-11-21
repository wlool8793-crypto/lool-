# Temporal Design - Versioning and Amendments

## Overview

Legal systems are inherently temporal - statutes get amended, sections are repealed, and case law evolves. This document explains how the schema handles temporal aspects of legal knowledge.

## Core Temporal Concepts

### 1. Statutory Versioning

Statutes change over time through amendments. We need to:
- Track all versions of a statute
- Know what was valid at any point in time
- Query historical versions
- Understand amendment chains

### 2. Point-in-Time Queries

**Use Case**: "What did Section 302 say on January 1, 2010?"

The schema must support queries for the state of law at any historical date.

### 3. Amendment Tracking

Every change to a statute or section must be:
- Recorded with date and reason
- Linked to the amending act
- Traceable through version history
- Queryable for impact analysis

## Schema Design for Temporal Data

### Version Nodes

`Version` nodes represent specific versions of statutes or sections:

```cypher
CREATE (v:Version {
  version_id: 'VERSION-BD-PC-302-V3',
  version_number: 3,
  valid_from: date('2023-07-01'),
  valid_to: null,  // Still current
  content: 'Whoever commits murder shall be punished...',
  change_summary: 'Added alternative sentencing and fine provision',
  change_type: 'amended',
  amending_act: 'Penal Code (Amendment) Act, 2023',
  current: true
})
```

### Temporal Properties

**On Statute and Section nodes**:
- `version`: Current version number
- `is_current_version`: Boolean flag
- `enactment_date`: When originally enacted
- `effective_date`: When it came into force
- `expiry_date`: When repealed (if applicable)
- `status`: Active, Repealed, Superseded, Suspended

**On Version nodes**:
- `valid_from`: Start of validity period
- `valid_to`: End of validity period (null if current)
- `version_number`: Sequential version identifier
- `current`: Boolean flag for current version

### Amendment Nodes

`Amendment` nodes capture the details of changes:

```cypher
CREATE (a:Amendment {
  amendment_id: 'AMEND-BD-PC-302-2023',
  amendment_type: 'modification',
  effective_date: date('2023-07-01'),
  amendment_act: 'Penal Code (Amendment) Act, 2023',
  original_text: 'Whoever commits murder shall be punished with death.',
  amended_text: 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.',
  reason: 'To provide alternative sentencing options and deterrent fine',
  retrospective: false
})
```

### Temporal Relationships

**VERSION_OF**: Links version to source
```cypher
(version:Version)-[:VERSION_OF {
  version_number: 3,
  is_current: true,
  valid_from: date('2023-07-01'),
  valid_to: null
}]->(section:Section)
```

**SUPERSEDES**: Links versions in sequence
```cypher
(v3:Version)-[:SUPERSEDES {
  supersede_date: date('2023-07-01')
}]->(v2:Version)
```

**AMENDS**: Links amendment to target
```cypher
(amendment:Amendment)-[:AMENDS {
  amendment_type: 'modification',
  amendment_date: date('2023-07-01')
}]->(section:Section)
```

## Temporal Query Patterns

### Pattern 1: Get Current Version

```cypher
// Get current version of a section
MATCH (s:Section {section_number: '302'})
WHERE s.is_current_version = true
RETURN s
```

Or via version node:
```cypher
MATCH (v:Version)-[:VERSION_OF]->(s:Section {section_id: 'SEC-BD-PC-302'})
WHERE v.current = true
RETURN v.content as current_text
```

### Pattern 2: Point-in-Time Query

```cypher
// What did Section 302 say on 2020-01-01?
MATCH (v:Version)-[:VERSION_OF]->(s:Section {section_number: '302'})
WHERE v.valid_from <= date('2020-01-01')
AND (v.valid_to IS NULL OR v.valid_to > date('2020-01-01'))
RETURN v.content as text_on_date
```

### Pattern 3: Amendment History

```cypher
// Get full amendment history for a section
MATCH (s:Section {section_number: '302'})
MATCH (v:Version)-[:VERSION_OF]->(s)
OPTIONAL MATCH (a:Amendment)-[:AMENDS]->(s)
RETURN s.section_number,
       v.version_number,
       v.valid_from,
       v.valid_to,
       v.change_summary,
       collect(a) as amendments
ORDER BY v.version_number DESC
```

### Pattern 4: Version Timeline

```cypher
// Get chronological version timeline
MATCH path = (latest:Version)-[:SUPERSEDES*]->(earliest:Version)
WHERE (latest)-[:VERSION_OF]->(:Section {section_number: '302'})
AND latest.current = true
RETURN [v IN nodes(path) | {
  version: v.version_number,
  valid_from: v.valid_from,
  valid_to: v.valid_to,
  changes: v.change_summary
}] as timeline
```

### Pattern 5: Cases Applying Historical Version

```cypher
// Find cases that applied a specific version
MATCH (case:Case)-[:APPLIES_SECTION]->(s:Section {section_number: '302'})
MATCH (v:Version)-[:VERSION_OF]->(s)
WHERE v.valid_from <= case.decision_date
AND (v.valid_to IS NULL OR v.valid_to > case.decision_date)
RETURN case, v.version_number, v.content
```

## Amendment Types

### 1. Addition (Insertion)
New section added to statute
```cypher
{amendment_type: 'addition', change_type: 'inserted'}
```

### 2. Deletion (Repeal)
Section removed from statute
```cypher
{amendment_type: 'deletion', change_type: 'repealed', valid_to: repeal_date}
```

### 3. Substitution
Entire section replaced
```cypher
{amendment_type: 'substitution', change_type: 'substituted'}
```

### 4. Modification
Partial change to section text
```cypher
{amendment_type: 'modification', change_type: 'amended'}
```

## Versioning Strategy

### Create New Version

When a section is amended:

```cypher
// 1. Mark current version as no longer current
MATCH (current:Version)-[:VERSION_OF]->(s:Section {section_id: $section_id})
WHERE current.current = true
SET current.current = false,
    current.valid_to = $amendment_date

// 2. Create new version
CREATE (new:Version {
  version_id: $new_version_id,
  version_number: current.version_number + 1,
  valid_from: $amendment_date,
  valid_to: null,
  content: $new_content,
  change_summary: $change_summary,
  change_type: 'amended',
  amending_act: $amending_act,
  current: true
})

// 3. Link to section
CREATE (new)-[:VERSION_OF {
  version_number: current.version_number + 1,
  is_current: true,
  valid_from: $amendment_date
}]->(s)

// 4. Link to previous version
CREATE (new)-[:SUPERSEDES {
  supersede_date: $amendment_date
}]->(current)

// 5. Update section's current version
SET s.version = current.version_number + 1,
    s.updated_at = datetime()
```

### Handle Retrospective Amendments

Some amendments apply retroactively:

```cypher
CREATE (a:Amendment {
  amendment_id: $amendment_id,
  effective_date: date('2023-07-01'),
  retrospective: true,
  retrospective_date: date('2022-01-01'),
  reason: 'Clarification of legislative intent'
})
```

Query with retrospective consideration:
```cypher
MATCH (v:Version)-[:VERSION_OF]->(s:Section)
MATCH (a:Amendment)-[:AMENDS]->(s)
WHERE a.retrospective = true
AND a.retrospective_date <= $query_date
AND a.effective_date > $query_date
RETURN v, a
```

## Temporal Constraints

### Validation Rules

1. **No Overlapping Versions**:
   - A section can't have two versions valid at the same time

2. **Continuous Timeline**:
   - No gaps in version coverage (valid_to of v1 = valid_from of v2)

3. **Single Current Version**:
   - Only one version can have current = true

4. **Date Ordering**:
   - valid_from < valid_to
   - version_number increases over time

### Enforcement

```cypher
// Check for overlapping versions (should return 0)
MATCH (v1:Version)-[:VERSION_OF]->(s:Section)
MATCH (v2:Version)-[:VERSION_OF]->(s)
WHERE v1 <> v2
AND v1.valid_from <= v2.valid_to
AND v2.valid_from <= v1.valid_to
RETURN count(*) as overlaps

// Check for multiple current versions (should return 0)
MATCH (v:Version)-[:VERSION_OF]->(s:Section)
WHERE v.current = true
WITH s, count(v) as current_count
WHERE current_count > 1
RETURN count(*) as violations
```

## Use Cases

### 1. Legal Research

**Scenario**: Lawyer needs to know what law applied when a contract was signed in 2015.

```cypher
MATCH (v:Version)-[:VERSION_OF]->(s:Section {section_number: '10'})
MATCH (statute:Statute)-[:CONTAINS]->(s)
WHERE v.valid_from <= date('2015-06-15')
AND (v.valid_to IS NULL OR v.valid_to > date('2015-06-15'))
RETURN statute.name, s.section_number, v.content
```

### 2. Legislative Impact Analysis

**Scenario**: Analyze how many cases were affected by a 2023 amendment.

```cypher
MATCH (a:Amendment {effective_date: date('2023-07-01')})
MATCH (a)-[:AMENDS]->(s:Section)
MATCH (case:Case)-[:APPLIES_SECTION]->(s)
WHERE case.decision_date < a.effective_date
RETURN count(case) as cases_affected
```

### 3. Amendment Tracking Dashboard

```cypher
// Get all amendments in last 5 years
MATCH (a:Amendment)
WHERE a.effective_date >= date() - duration('P5Y')
MATCH (a)-[:AMENDS]->(target)
RETURN a.amendment_act,
       a.effective_date,
       a.amendment_type,
       labels(target)[0] as target_type,
       target.section_number as section
ORDER BY a.effective_date DESC
```

### 4. Statute Evolution Visualization

```cypher
// Get complete evolution of a statute
MATCH (statute:Statute {statute_id: 'STAT-BD-PC-1860'})
MATCH (statute)-[:CONTAINS]->(s:Section)
MATCH (v:Version)-[:VERSION_OF]->(s)
RETURN s.section_number,
       collect({
         version: v.version_number,
         from: v.valid_from,
         to: v.valid_to,
         changes: v.change_summary
       }) as history
ORDER BY s.section_number
```

## Best Practices

### 1. Always Use Temporal Queries
Never assume the current version is what you need - always filter by date.

### 2. Maintain Continuous Timeline
Ensure no gaps in version coverage for critical provisions.

### 3. Document Amendment Reasons
Always include reason and amending act for auditability.

### 4. Index Temporal Properties
Critical for performance:
```cypher
CREATE INDEX section_temporal IF NOT EXISTS
FOR (s:Section) ON (s.effective_from, s.effective_to, s.is_current_version);
```

### 5. Version Everything Important
Statutes and sections are obvious, but consider versioning:
- Court rules
- Legal forms
- Procedural requirements
- Fee schedules

## Future Enhancements

### Planned Features

1. **Draft Versions**: Track proposed amendments before enactment
2. **Conditional Amendments**: Amendments that depend on other events
3. **Automatic Version Migration**: Auto-create versions from amendment data
4. **Temporal Visualizations**: Timeline graphs of statutory evolution
5. **Change Notifications**: Alert when provisions are amended

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
