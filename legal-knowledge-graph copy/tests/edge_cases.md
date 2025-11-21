# Legal Knowledge Graph - Edge Cases Analysis

## Version 1.0 - Iteration 1

This document catalogs edge cases discovered during schema testing that may break, confuse, or stress the knowledge graph design.

---

## 1. TEMPORAL EDGE CASES

### 1.1 Case Overruled Then Reinstated
**Description**: Case A is initially active, then overruled by Case B, then reinstated by Case C.

**Example**:
- CASE-BD-SC-2019-007 (Hossain) - Active
- CASE-BD-SC-2024-003 (Alam) - Overrules Hossain
- CASE-BD-SC-2025-001 (Khan) - Overrules Alam, Reinstates Hossain

**Issues**:
- Schema supports this through `CITES` relationship with citation_type "Overruled" and "Approved"
- Status tracking is challenging - should Hossain status change from "Active" → "Overruled" → "Active"?
- Current schema uses static `status` field which requires manual updates
- **Query complexity**: Finding current precedent status requires traversing entire citation chain
- **Temporal integrity**: No automated status update when new case overrules/reinstates

**Potential Problems**:
- Manual status updates may lag behind citations
- Conflicting status indicators (status field vs. citation relationships)
- Historical queries need to know status *at a point in time*

**Recommendations**:
- Add `status_effective_date` to track when status changed
- Create computed property or function to determine "current effective status"
- Add `StatusChange` event node to track status history
- Consider materialized view for current precedent status

---

### 1.2 Temporal Gaps in Section Versions
**Description**: Section version 2 expires on 2013-04-14, but version 3 doesn't take effect until 2013-04-16 (2-day gap).

**Issues**:
- What is the law during the gap period?
- Schema allows this but doesn't enforce continuity
- Queries for "law at date X" may return null during gaps

**Potential Problems**:
- Legal uncertainty
- Cases decided during gap period reference which version?
- No constraint preventing gaps

**Recommendations**:
- Add constraint: `effective_from` of new version = `effective_to` + 1 day of old version
- Or allow transition periods with both versions "Active" status
- Add validation layer to detect/flag gaps

---

### 1.3 Overlapping Section Versions (Transition Period)
**Description**: Two versions of same section both active during transition period (e.g., new law passed but old law still applies to pending cases).

**Example**: Section 376 V3 active until 2020-10-12, V4 active from 2020-10-13. But cases filed before Oct 13 may still use V3.

**Issues**:
- Current schema uses `is_current_version` boolean (only one can be true)
- Real legal systems often have transition provisions
- Schema doesn't model "applicable_to" relationship between case and section version

**Potential Problems**:
- Binary current/non-current doesn't reflect legal reality
- No way to represent "Section X V3 applies to cases filed before date Y"

**Recommendations**:
- Replace `is_current_version` with `applicability_rule` text field
- Add `APPLICABLE_TO` relationship from Section to Case with conditions
- Consider adding `TransitionPeriod` node

---

### 1.4 Retroactive Statute Amendments
**Description**: Amendment passed in 2020 but declared effective from 2018 (retroactive).

**Issues**:
- Cases decided in 2019 cited version that was later retroactively changed
- Schema doesn't distinguish between enactment date and retroactive effective date

**Potential Problems**:
- Historical queries may be incorrect
- Cases may cite "wrong" version (that was current at time but retroactively changed)

**Recommendations**:
- Add `enacted_date` vs `effective_date` vs `retroactive_from_date`
- Add `is_retroactive` boolean flag
- Track which cases were affected by retroactive changes

---

## 2. PRECEDENT/CITATION EDGE CASES

### 2.1 Circular Citations
**Description**: Case A cites Case B, Case B cites Case C, Case C cites Case A (citation cycle).

**Issues**:
- Schema allows this (no constraint preventing cycles)
- Graph traversal queries may infinite loop without depth limits
- Logically unusual but may occur with obiter dicta or distinguishing

**Potential Problems**:
- Precedent chain queries can fail without `*1..10` depth limit
- Cycle detection needed for validation

**Recommendations**:
- Add application-level cycle detection
- Flag suspicious circular citations for review
- Use depth limits on all traversal queries

---

### 2.2 Self-Citation
**Description**: Case A cites itself (in a later portion of the judgment or in a review/modification).

**Issues**:
- Schema allows `(c:Case)-[:CITES]->(c)` (self-loop)
- Logically possible in rehearings, modifications, clarifications

**Potential Problems**:
- Precedent chain queries include self-loops
- Statistical analysis (citation counts) inflated

**Recommendations**:
- Add constraint or application validation to flag self-citations
- Filter self-citations in analysis queries: `WHERE citing <> cited`

---

### 2.3 Conflicting Precedents (Active)
**Description**: Two binding precedents with contradictory holdings on same issue, both status "Active".

**Example**:
- Case X: "Section 376 requires corroboration" (Active)
- Case Y: "Section 376 does not require corroboration" (Active)

**Issues**:
- Schema allows this (no constraint enforcing consistency)
- Users querying for "the law" get conflicting answers
- Real-world scenario: conflicting High Court precedents before Supreme Court resolves

**Potential Problems**:
- RAG system may return conflicting legal advice
- Query results ambiguous
- No automatic conflict detection

**Recommendations**:
- Add `CONFLICTS_WITH` relationship between cases
- Create conflict detection query to flag contradictions
- Add `conflict_status` field: "Resolved", "Unresolved", "Pending Appeal"
- Prioritize by court hierarchy and date in RAG retrieval

---

### 2.4 Precedent from Lower Court Cited by Higher Court
**Description**: Supreme Court cites High Court decision as persuasive precedent.

**Issues**:
- Schema doesn't model court hierarchy
- Citation weight/precedent value unclear
- May need different treatment than Supreme Court citing Supreme Court

**Potential Problems**:
- All citations treated equally regardless of court hierarchy
- Binding vs persuasive authority not algorithmically determinable

**Recommendations**:
- Add `court_level` field to Case (Supreme, High, District, etc.)
- Add `court_hierarchy` table/graph
- Compute `is_binding` property based on court hierarchy
- Add citation weight based on court relationship

---

## 3. STATUTE/SECTION EDGE CASES

### 3.1 Section Renumbered
**Description**: Section 302A becomes Section 302B in amendment (renumbering, not just content change).

**Issues**:
- Current schema identifies sections by `section_number` and `version`
- Renumbering creates new section_number but is conceptually same provision
- Older cases cite "Section 302A" which no longer exists

**Potential Problems**:
- Cases citing old section number can't find current equivalent
- Query for "all cases citing Section 302A" misses cases citing 302B
- No `RENAMED_TO` relationship

**Recommendations**:
- Add `RENAMED_TO` relationship between sections
- Add `historical_section_numbers` array field
- Create alias resolution in query layer

---

### 3.2 Section Partially Repealed
**Description**: Section 376(1)(a) repealed but Section 376(1)(b) and 376(2) remain active.

**Issues**:
- Schema models section as atomic unit
- No support for sub-section granularity
- Status would be ambiguous: "Partially Repealed" but no detail on which parts

**Potential Problems**:
- Cannot model sub-section level amendments
- Queries can't distinguish between fully and partially repealed sections

**Recommendations**:
- Add `SubSection` node type
- Model hierarchy: Statute → Section → SubSection → Clause
- Add `repealed_provisions` text array listing specific sub-sections
- Status field: "Partially Repealed" with details in `status_details`

---

### 3.3 Statute Superseded by New Statute (Not Amendment)
**Description**: Value Added Tax Act 1991 completely replaced by Value Added Tax and Supplementary Duty Act 2012 (different statute_id).

**Issues**:
- Current `SUPERSEDES` relationship only between versions of same statute
- New statute has different statute_id and name
- Cases may still cite old statute for historical context

**Potential Problems**:
- No relationship linking old statute to new statute
- Users searching for "VAT law" may not find old statute
- Historical queries need to know what law was in effect

**Recommendations**:
- Allow `SUPERSEDES` between different statutes (not just versions)
- Add `REPLACES` relationship distinct from version supersession
- Add `predecessor_statute` and `successor_statute` fields

---

## 4. JUDGE/DECISION EDGE CASES

### 4.1 Judge Decides Case in Lower Court, Then Same Case in Higher Court (After Elevation)
**Description**: Judge X decides case at High Court. Elevated to Supreme Court. Same case appealed to Supreme Court. Judge X on Supreme Court bench hearing appeal of own decision.

**Issues**:
- Schema allows judge to decide same case twice
- Violates natural justice (judge reviewing own decision)
- Should be flagged as conflict of interest

**Potential Problems**:
- No constraint preventing this
- Conflict of interest detection not built-in

**Recommendations**:
- Add application-level validation to detect judge deciding same case at multiple levels
- Add `RECUSED_FROM` relationship
- Flag for manual review

---

### 4.2 Concurring vs Dissenting Opinions
**Description**: 5-judge bench, 3-2 decision. Majority opinion is binding, but dissenting opinion may be persuasive in future.

**Issues**:
- Schema tracks `opinion_type` in `DECIDED_BY` relationship
- But case summary/holding reflects only majority
- Dissenting opinions not separately modeled

**Potential Problems**:
- RAG context may miss important dissenting reasoning
- Future cases may cite dissenting opinion as persuasive
- No separate node for individual opinions

**Recommendations**:
- Create `Opinion` node (separate from Case)
- Relationship: `(Judge)-[:AUTHORED]->(Opinion)<-[:HAS_OPINION]-(Case)`
- Opinion properties: `type` (Majority, Concurring, Dissenting), `text`, `reasoning`
- Case cites Opinion, not just Case

---

## 5. CROSS-DOMAIN EDGE CASES

### 5.1 Case Addresses Multiple Domains
**Description**: Criminal case (murder) that also raises constitutional issue (Article 32 fair trial).

**Issues**:
- `case_type` is single value: "Criminal" or "Constitutional"?
- Test data uses "Criminal" but case also addresses constitutional issue
- Domain field on LegalIssue helps but case classification is ambiguous

**Potential Problems**:
- Domain-specific queries may miss cross-domain cases
- Classification is not mutually exclusive

**Recommendations**:
- Change `case_type` from string to string array: `["Criminal", "Constitutional"]`
- Add `primary_domain` and `secondary_domains` fields
- Add `INVOLVES_DOMAIN` relationship to Domain node

---

## 6. DATA QUALITY EDGE CASES

### 6.1 Missing Required Fields
**Description**: Case created without `decision_date` (marked required in schema).

**Issues**:
- Schema defines required fields but Neo4j doesn't enforce
- Constraints only cover uniqueness, not presence

**Potential Problems**:
- Queries filtering by date will miss records with null dates
- Temporal queries fail

**Recommendations**:
- Add node property existence constraints (Neo4j Enterprise)
- Add application-level validation before insert
- Regular data quality audits

---

### 6.2 Inconsistent Date Formats
**Description**: Some dates stored as "2023-01-15", others as "15/01/2023", others as datetime objects.

**Issues**:
- Schema specifies "date" type but doesn't enforce format
- Comparison and sorting fail with mixed formats

**Potential Problems**:
- Date range queries incorrect
- Cannot reliably sort by date

**Recommendations**:
- Enforce ISO 8601 format (YYYY-MM-DD) at application layer
- Use Neo4j `date()` type, not string
- Add data validation/migration scripts

---

## 7. VECTOR/RAG EDGE CASES

### 7.1 Missing Embeddings
**Description**: Vector similarity search requires embeddings, but some cases don't have them.

**Issues**:
- `embedding` field is optional
- Vector similarity queries exclude cases without embeddings
- Hybrid search may be incomplete

**Potential Problems**:
- RAG retrieval biased toward cases with embeddings
- Older cases may lack embeddings (added retroactively)

**Recommendations**:
- Batch process to generate embeddings for all cases
- Flag cases missing embeddings
- Fallback to keyword search if embedding missing

---

### 7.2 Embedding Dimension Mismatch
**Description**: Some embeddings are 1536-dim (OpenAI), others are 768-dim (Sentence-BERT).

**Issues**:
- Schema specifies 1536 dimensions
- Mixed embedding models not supported in single vector index

**Potential Problems**:
- Cannot compare embeddings from different models
- Index creation fails with wrong dimensions

**Recommendations**:
- Standardize on single embedding model
- Create separate indexes for different dimensions
- Add `embedding_model` and `embedding_dimension` fields

---

## 8. MULTI-JURISDICTION EDGE CASES

### 8.1 Jurisdiction Code Ambiguity
**Description**: "IN" could mean India or Indonesia.

**Issues**:
- Two-letter codes may overlap
- Schema doesn't enforce jurisdiction code standard

**Potential Problems**:
- Incorrect jurisdiction assignment
- Cross-jurisdiction queries return wrong results

**Recommendations**:
- Use ISO 3166-1 alpha-3 codes (IND, BGD, PAK)
- Or use full names with code as secondary
- Add `Jurisdiction` node with standardized codes

---

### 8.2 Cross-Jurisdiction Statutory References
**Description**: Bangladesh Penal Code 1860 is same as Indian Penal Code 1860 (both inherited from British India).

**Issues**:
- Two separate statute nodes with different statute_ids
- Same section numbers but different jurisdictions
- Historical relationship not modeled

**Potential Problems**:
- Cannot query "all jurisdictions using Section 302"
- Comparative analysis difficult

**Recommendations**:
- Add `DERIVED_FROM` relationship between statutes
- Add `common_law_origin` field
- Create `StatuteFamily` node for related statutes across jurisdictions

---

## 9. PERFORMANCE EDGE CASES

### 9.1 Dense Citation Networks (Highly Cited Cases)
**Description**: Kesavananda Bharati cited by 500+ cases.

**Issues**:
- Node has 500+ incoming CITES relationships
- Queries expanding from this node are expensive
- Graph visualization cluttered

**Potential Problems**:
- Query performance degrades for landmark cases
- Memory issues in full context retrieval

**Recommendations**:
- Paginate citation results
- Add citation count as cached property
- Sample citations rather than returning all
- Create summary nodes for highly cited cases

---

### 9.2 Deep Precedent Chains (10+ Hops)
**Description**: Precedent chain from 2025 case back to 1950 case (10+ hops).

**Issues**:
- `[:CITES*1..10]` may timeout
- Cartesian product explosion

**Potential Problems**:
- Query timeout
- Excessive memory usage

**Recommendations**:
- Limit depth in production queries
- Use shortest path algorithms
- Pre-compute precedent lineages for important cases
- Add `precedent_depth` cached property

---

## 10. SCHEMA AMBIGUITY EDGE CASES

### 10.1 Citation Node vs CITES Relationship
**Description**: Schema has both `Citation` node and `CITES` relationship with same properties.

**Issues**:
- Redundant/overlapping models
- Test data only uses `CITES` relationship
- Unclear when to use node vs relationship

**Potential Problems**:
- Inconsistent data modeling
- Wasted storage
- Query confusion

**Recommendations**:
- Choose one: either Citation as node or as relationship properties
- If Citation is complex (has its own relationships), use node
- If Citation is just metadata on CITES, use relationship properties only
- **Decision**: Remove `Citation` node, keep only `CITES` relationship with properties

---

## SUMMARY

**Total Edge Cases Documented**: 25

**Categories**:
- Temporal: 4
- Precedent/Citation: 4
- Statute/Section: 3
- Judge/Decision: 2
- Cross-Domain: 1
- Data Quality: 2
- Vector/RAG: 2
- Multi-Jurisdiction: 2
- Performance: 2
- Schema Ambiguity: 1

**Severity Levels**:
- Critical (Schema Breaking): 3
- High (Data Integrity): 8
- Medium (Query/Performance): 10
- Low (Usability): 4

**Next Steps**:
- Prioritize Critical and High severity issues for Iteration 2
- Implement recommended constraints and validations
- Add data quality checks
- Refine schema based on findings
