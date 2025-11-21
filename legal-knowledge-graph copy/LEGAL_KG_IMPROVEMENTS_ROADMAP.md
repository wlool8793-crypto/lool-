# Legal Knowledge Graph Improvements Roadmap
**Comprehensive Implementation Guide for Future Enhancement**

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Priority 1: Critical Improvements](#priority-1-critical-improvements)
3. [Priority 2: RAG Optimizations](#priority-2-rag-optimizations)
4. [Priority 3: Query & Performance](#priority-3-query--performance)
5. [Priority 4: Advanced Features](#priority-4-advanced-features)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Testing & Validation Framework](#testing--validation-framework)
8. [Quick Wins Checklist](#quick-wins-checklist)
9. [Appendices](#appendices)

---

## 📊 Executive Summary

### Current State
- **Schema Version:** 2.0.0
- **Production Readiness:** 90/100 (A-)
- **Status:** ✅ Production Ready
- **Node Types:** 22
- **Relationship Types:** 33
- **Total Improvements Identified:** 28

### Improvement Categories

| Priority | Focus Area | Items | Est. Effort | Expected Impact |
|----------|-----------|-------|-------------|-----------------|
| **P1 - Critical** | Data Quality & Citations | 6 items | 2-4 weeks | +40% accuracy |
| **P2 - High Value** | RAG Optimization | 7 items | 3-4 weeks | +35% precision |
| **P3 - Important** | Query & Performance | 5 items | 2-3 weeks | +60% speed |
| **P4 - Nice to Have** | Advanced Features | 10 items | 4-6 weeks | Enhanced UX |

### Expected Outcomes

After implementing all improvements:
- **Citation Accuracy:** +40% improvement
- **Retrieval Precision:** +35% improvement
- **Query Performance:** +60% improvement
- **User Trust:** +25% improvement
- **Overall Score:** 90/100 → 95+/100 (A+)

### Key Success Metrics

```
BEFORE → AFTER
├─ Precision@5: 0.75 → 0.90 (+20%)
├─ Treatment F1: 0.70 → 0.85 (+21%)
├─ Query Latency: 1200ms → 500ms (-58%)
├─ Trust Score Coverage: 26% → 100% (+74%)
└─ Cache Hit Rate: 0% → 40% (+40%)
```

---

## 🔴 Priority 1: Critical Improvements

### 1.1 Enhanced Citation Extraction & Treatment Classification

**Current Gap:** Basic CITES relationships without rich treatment metadata and confidence scores.

**Why Critical:** Treatment classification (applies/follows/overruled) is the foundation of legal reasoning. Without accurate treatment, precedent analysis is unreliable.

#### Schema Enhancement

```json
{
  "relationship_type": "CITES",
  "from": "Holding",
  "to": "Section|Case",
  "properties": {
    "citationType": {
      "type": "enum",
      "required": true,
      "values": ["statutory", "judicial", "secondary"],
      "indexed": true
    },
    "treatment": {
      "type": "enum",
      "required": true,
      "values": [
        "applies",
        "follows",
        "distinguishes",
        "overruled",
        "criticizes",
        "qualified",
        "harmonized"
      ],
      "indexed": true,
      "description": "How citing case treated cited authority"
    },
    "confidence": {
      "type": "float",
      "required": true,
      "range": [0.0, 1.0],
      "indexed": true,
      "description": "ML model confidence in classification"
    },
    "locator": {
      "type": "string",
      "required": false,
      "examples": ["para 23", "page 45", "Order VI r.17"]
    },
    "context": {
      "type": "string",
      "max_length": 500,
      "description": "Surrounding citation context"
    },
    "extractedBy": {
      "type": "string",
      "required": true,
      "examples": ["legal-BERT-NER", "GPT-4", "manual"]
    },
    "extractedAt": {
      "type": "datetime",
      "required": true
    }
  }
}
```

#### Implementation Approach

**Step 1: Build Citation Extraction Pipeline**

```python
# Pseudocode for citation extraction

class CitationExtractor:
    def __init__(self):
        self.statutory_regex = compile_statutory_patterns()
        self.case_ner_model = load_model("legal-BERT-NER")
        self.treatment_classifier = load_model("treatment-classifier")

    def extract_citations(self, text, source_doc):
        citations = []

        # Extract statutory citations (regex)
        for match in self.statutory_regex.findall(text):
            citation = {
                "type": "statutory",
                "target": normalize_statutory_ref(match),
                "locator": extract_locator(match),
                "context": get_context_window(text, match, window=200)
            }
            citations.append(citation)

        # Extract case citations (NER model)
        case_entities = self.case_ner_model.extract(text)
        for entity in case_entities:
            citation = {
                "type": "judicial",
                "target": resolve_case_reference(entity),
                "locator": extract_locator(entity),
                "context": get_context_window(text, entity, window=200)
            }
            citations.append(citation)

        return citations

    def classify_treatment(self, citing_text, cited_doc):
        # Prepare input for treatment classifier
        input_pair = [citing_text, cited_doc.summary]

        # Predict treatment
        prediction = self.treatment_classifier.predict(input_pair)

        return {
            "treatment": prediction["label"],
            "confidence": prediction["score"]
        }
```

**Step 2: Treatment Classification Training Data Format**

```json
{
  "training_examples": [
    {
      "citing_text": "In KB Saha v. DCL, the Supreme Court held that unregistered documents required to be registered under Section 17 cannot be admitted as evidence.",
      "cited_case": "KB Saha v. Development Consultant Ltd.",
      "cited_section": "Section 17, Registration Act",
      "treatment": "applies",
      "confidence": 0.95,
      "annotator": "legal_expert_1"
    },
    {
      "citing_text": "The ratio in Siddique Mia was limited to identical amendment applications and is distinguishable on facts.",
      "cited_case": "Siddique Mia v. Md Idris Miah",
      "treatment": "distinguishes",
      "confidence": 0.88,
      "annotator": "legal_expert_2"
    }
  ]
}
```

**Step 3: Confidence Thresholds & Quality Control**

```python
CONFIDENCE_THRESHOLDS = {
    "auto_accept": 0.85,      # Automatically accept
    "human_review": 0.60,     # Flag for human review
    "reject": 0.60            # Below this, don't create edge
}

def handle_citation_extraction(citation, confidence):
    if confidence >= CONFIDENCE_THRESHOLDS["auto_accept"]:
        # Create CITES relationship immediately
        create_relationship(citation, status="verified")

    elif confidence >= CONFIDENCE_THRESHOLDS["human_review"]:
        # Queue for human review
        queue_for_review(citation, confidence)
        create_relationship(citation, status="pending_review")

    else:
        # Log but don't create
        log_low_confidence_citation(citation, confidence)
```

#### Action Items

- [ ] **Task 1.1.1:** Build statutory citation regex patterns
  - Patterns for Section X, Order Y rule Z, Article N
  - Handle variations: "s.17", "sec 17", "Section 17(1)(a)"
  - Effort: 2 days

- [ ] **Task 1.1.2:** Fine-tune legal-BERT for case citation NER
  - Collect 500+ labeled examples of case citations
  - Fine-tune nlpaueb/legal-bert-base-uncased
  - Effort: 1 week

- [ ] **Task 1.1.3:** Build treatment classifier
  - Collect 1000+ labeled citation pairs with treatment
  - Train classifier (start with cross-encoder architecture)
  - Target F1 ≥ 0.85
  - Effort: 1-2 weeks

- [ ] **Task 1.1.4:** Integrate extraction pipeline into ingestion
  - Run extractor on all new documents
  - Backfill existing documents
  - Effort: 3 days

- [ ] **Task 1.1.5:** Build human review interface
  - Queue low-confidence citations
  - Allow experts to correct/verify
  - Effort: 1 week

#### Expected Impact

```
Metrics Before → After
├─ Citation extraction recall: 0.65 → 0.90
├─ Treatment classification F1: 0.70 → 0.85
├─ Precedent analysis accuracy: 0.60 → 0.85
└─ User trust in citations: 0.70 → 0.90
```

**ROI:** High - Foundation for all legal reasoning queries

---

### 1.2 Source Type Hierarchy & Provenance Enhancement

**Current Gap:** Source nodes don't distinguish primary official sources from secondary summaries.

**Why Critical:** Legal research requires knowing whether information comes from official government sources or third-party summaries. Trust and admissibility depend on source type.

#### Schema Enhancement

```json
{
  "node_type": "Source",
  "properties": {
    "id": "existing",
    "publisher": "existing",
    "url": "existing",
    "sourceType": {
      "type": "enum",
      "required": true,
      "values": [
        "primary_statute",        // Official govt gazette
        "primary_judgment",       // Court-issued judgment
        "official_reporter",      // Authorized law report
        "commercial_reporter",    // SCC, DLR, BLD
        "summary",               // Case summary/digest
        "commentary",            // Legal commentary
        "tertiary"              // Textbook, article
      ],
      "indexed": true
    },
    "authorityLevel": {
      "type": "integer",
      "range": [1, 5],
      "description": "1=tertiary, 5=primary official",
      "indexed": true
    },
    "verificationStatus": {
      "type": "enum",
      "values": ["verified", "unverified", "disputed"],
      "default": "unverified",
      "indexed": true
    },
    "verifiedBy": {
      "type": "string",
      "description": "Legal expert ID who verified"
    },
    "verifiedAt": {
      "type": "datetime"
    },
    "lastChecked": {
      "type": "datetime",
      "description": "Last time source was validated"
    }
  }
}
```

#### Source Type Authority Mapping

```
Authority Level Hierarchy:

Level 5 (Highest Authority)
└─ primary_statute (Official Gazette publications)
└─ primary_judgment (Court-issued judgments)

Level 4 (High Authority)
└─ official_reporter (Authorized law reports: DLR Official)

Level 3 (Moderate Authority)
└─ commercial_reporter (SCC, BLD, AIR)

Level 2 (Low Authority)
└─ summary (Case summaries, digests)
└─ commentary (Legal commentaries)

Level 1 (Reference Only)
└─ tertiary (Textbooks, articles, blogs)
```

#### Trust Score Recalculation

```python
def calculate_trust_score(chunk, source):
    """
    Recalculate trust score incorporating source type
    """

    # Source type weights
    SOURCE_TYPE_WEIGHTS = {
        'primary_statute': 1.00,
        'primary_judgment': 0.95,
        'official_reporter': 0.90,
        'commercial_reporter': 0.85,
        'summary': 0.70,
        'commentary': 0.60,
        'tertiary': 0.50
    }

    # Verification status boost
    VERIFICATION_BOOST = {
        'verified': 1.0,
        'unverified': 0.9,
        'disputed': 0.5
    }

    # Calculate components
    source_authority = SOURCE_TYPE_WEIGHTS.get(source.sourceType, 0.5)
    verification_factor = VERIFICATION_BOOST.get(source.verificationStatus, 0.9)

    # Weighted trust score
    trust = (
        0.40 * source_authority * verification_factor +
        0.20 * chunk.ocrConfidence +
        0.15 * chunk.citationFrequencyNorm +
        0.15 * chunk.parserConfidence +
        0.10 * chunk.recencyScore
    )

    return min(1.0, max(0.0, trust))
```

#### Migration Script

```cypher
// Classify existing sources by publisher name

// Primary official sources
MATCH (s:Source)
WHERE s.publisher CONTAINS 'Government'
   OR s.publisher CONTAINS 'Official Gazette'
   OR s.publisher CONTAINS 'Supreme Court'
SET s.sourceType = 'primary_statute',
    s.authorityLevel = 5;

// Commercial reporters
MATCH (s:Source)
WHERE s.publisher IN ['SCC Online', 'Eastern Book Company', 'DLR']
SET s.sourceType = 'commercial_reporter',
    s.authorityLevel = 3;

// User uploads / summaries
MATCH (s:Source)
WHERE s.publisher CONTAINS 'upload' OR s.id CONTAINS 'upload'
SET s.sourceType = 'summary',
    s.authorityLevel = 2,
    s.verificationStatus = 'unverified';

// Recalculate trust scores for all chunks
MATCH (chunk:TextChunk)-[:INGESTED_FROM]->(source:Source)
SET chunk.trust_score = calculate_trust(chunk, source);
```

#### Action Items

- [ ] **Task 1.2.1:** Add sourceType enum to Source schema
  - Update schema definition files
  - Effort: 1 hour

- [ ] **Task 1.2.2:** Classify existing Source nodes
  - Run migration script on all existing sources
  - Manual review for ambiguous cases
  - Effort: 4 hours

- [ ] **Task 1.2.3:** Update trust score calculation
  - Implement new formula with sourceType weight
  - Recalculate for all existing chunks
  - Effort: 1 day

- [ ] **Task 1.2.4:** Update UI to show source hierarchy
  - Display badge: "Official Source", "Summary", etc.
  - Add filter by source type
  - Effort: 2 days

- [ ] **Task 1.2.5:** Build source verification workflow
  - Interface for legal experts to verify sources
  - Track verification history
  - Effort: 1 week

#### Expected Impact

```
Improvements:
├─ User trust in results: +25%
├─ Ability to filter by authority: New capability
├─ Compliance with legal standards: Achieved
└─ Answer defensibility: Significantly improved
```

---

### 1.3 Paragraph-Level Chunking with Precise Offsets

**Current Gap:** Chunks may not align with natural paragraph boundaries; lack precise page/offset metadata for citation.

**Why Critical:** Legal citations require paragraph-level precision. Users need to verify exact text in source documents. Hallucination risk increases with improper chunk boundaries.

#### Enhanced Chunk Schema

```json
{
  "node_type": "TextChunk",
  "properties": {
    "id": "existing",
    "documentId": "existing",
    "text": "existing",
    "chunkType": {
      "type": "enum",
      "required": true,
      "values": [
        "facts",
        "holding",
        "reasoning",
        "dissent",
        "procedural_history",
        "legal_analysis",
        "precedent_discussion",
        "statute_text",
        "preamble",
        "definitions"
      ],
      "indexed": true,
      "description": "Semantic type of chunk"
    },
    "paragraphNumber": {
      "type": "integer",
      "required": true,
      "indexed": true,
      "description": "Paragraph index (1-based)"
    },
    "pageNumber": {
      "type": "integer",
      "required": false,
      "indexed": true,
      "description": "PDF page number"
    },
    "startCharOffset": {
      "type": "integer",
      "required": true,
      "description": "Character offset in document"
    },
    "endCharOffset": {
      "type": "integer",
      "required": true
    },
    "startLineNumber": {
      "type": "integer",
      "description": "Line number start"
    },
    "endLineNumber": {
      "type": "integer"
    },
    "tokenCount": {
      "type": "integer",
      "required": true
    },
    "sentenceCount": {
      "type": "integer",
      "required": false
    },
    "embeddingId": "existing",
    "trustScore": "existing"
  }
}
```

#### Chunking Algorithm

```python
class LegalDocumentChunker:
    """
    Intelligent paragraph-based chunker for legal documents
    """

    TARGET_CHUNK_SIZE = 400  # tokens
    MAX_CHUNK_SIZE = 600
    MIN_CHUNK_SIZE = 100

    def chunk_document(self, document, doc_type):
        if doc_type == "case":
            return self.chunk_judgment(document)
        elif doc_type == "statute":
            return self.chunk_statute(document)
        else:
            return self.chunk_generic(document)

    def chunk_judgment(self, judgment_text):
        """
        Chunk judgment by paragraphs with semantic type classification
        """
        # Extract paragraphs (usually numbered in judgments)
        paragraphs = extract_numbered_paragraphs(judgment_text)

        chunks = []
        for para_num, para_text in enumerate(paragraphs, start=1):
            # Check if paragraph is too long
            token_count = count_tokens(para_text)

            if token_count > self.MAX_CHUNK_SIZE:
                # Split at sentence boundaries
                sub_chunks = self._split_long_paragraph(para_text)
                for i, sub_text in enumerate(sub_chunks):
                    chunk = {
                        "text": sub_text,
                        "paragraphNumber": para_num,
                        "subParagraph": i,
                        "tokenCount": count_tokens(sub_text),
                        "chunkType": classify_chunk_type(sub_text),
                        "startCharOffset": get_char_offset(judgment_text, sub_text),
                        "pageNumber": get_page_number(judgment_text, sub_text)
                    }
                    chunks.append(chunk)
            else:
                chunk = {
                    "text": para_text,
                    "paragraphNumber": para_num,
                    "tokenCount": token_count,
                    "chunkType": classify_chunk_type(para_text),
                    "startCharOffset": get_char_offset(judgment_text, para_text),
                    "pageNumber": get_page_number(judgment_text, para_text)
                }
                chunks.append(chunk)

        return chunks

    def _split_long_paragraph(self, text):
        """
        Split long paragraph at sentence boundaries
        """
        sentences = split_into_sentences(text)

        sub_chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = count_tokens(sentence)

            if current_tokens + sentence_tokens > self.TARGET_CHUNK_SIZE:
                # Save current chunk
                sub_chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            sub_chunks.append(" ".join(current_chunk))

        return sub_chunks

    def chunk_statute(self, statute_text):
        """
        Chunk statute by sections/subsections
        """
        sections = parse_statute_sections(statute_text)

        chunks = []
        for section in sections:
            # Each section becomes one or more chunks
            if section.has_subsections:
                for subsection in section.subsections:
                    chunk = {
                        "text": subsection.text,
                        "sectionNumber": section.number,
                        "subsectionNumber": subsection.number,
                        "chunkType": "statute_text",
                        "tokenCount": count_tokens(subsection.text)
                    }
                    chunks.append(chunk)
            else:
                chunk = {
                    "text": section.text,
                    "sectionNumber": section.number,
                    "chunkType": "statute_text",
                    "tokenCount": count_tokens(section.text)
                }
                chunks.append(chunk)

        return chunks
```

#### Chunk Type Classification

```python
# Train a small classifier to identify chunk type

CHUNK_TYPE_FEATURES = [
    "starts_with_held",           # "The Court held..."
    "contains_ratio_keywords",    # "ratio decidendi", "principle"
    "contains_facts_keywords",    # "plaintiff", "defendant", "facts"
    "contains_procedural",        # "appeal filed", "case transferred"
    "sentence_structure",         # Complex vs simple
    "position_in_document",       # Holdings usually later
    "citation_density"            # Holdings cite more
]

def classify_chunk_type(text, position_ratio):
    """
    Classify semantic type of chunk
    """
    features = extract_features(text, position_ratio)

    # Simple rule-based classifier (can be replaced with ML)
    if starts_with_pattern(text, ["held that", "court held"]):
        return "holding"

    elif position_ratio < 0.2:  # Early in document
        if contains_keywords(text, ["plaintiff", "defendant", "filed"]):
            return "facts"
        elif contains_keywords(text, ["appeal", "revision"]):
            return "procedural_history"

    elif position_ratio > 0.6:  # Later in document
        if contains_keywords(text, ["principle", "ratio", "established"]):
            return "holding"
        elif contains_keywords(text, ["dissent", "disagree"]):
            return "dissent"

    elif contains_keywords(text, ["section", "article", "act"]):
        return "statute_text"

    else:
        return "legal_analysis"  # Default
```

#### Action Items

- [ ] **Task 1.3.1:** Implement paragraph extractor
  - Handle numbered paragraphs in judgments
  - Detect section/subsection structure in statutes
  - Effort: 3 days

- [ ] **Task 1.3.2:** Build chunk type classifier
  - Label 500 chunks by type
  - Train classifier (or use rule-based)
  - Effort: 1 week

- [ ] **Task 1.3.3:** Re-chunk all existing documents
  - Run chunker on all documents in database
  - Generate new embeddings
  - Effort: 2 days (compute time)

- [ ] **Task 1.3.4:** Update vector DB with new embeddings
  - Map old embeddingIds to new ones
  - Maintain backward compatibility during transition
  - Effort: 1 day

- [ ] **Task 1.3.5:** Add highlighting to UI
  - Use startCharOffset/endCharOffset to highlight
  - Link to specific page/paragraph in PDFs
  - Effort: 3 days

#### Expected Impact

```
Improvements:
├─ Hallucination reduction: -50%
├─ Citation precision: +60% (exact para/page refs)
├─ User verification time: -40% (quick highlight)
├─ Chunk relevance: +25% (better boundaries)
└─ Legal defensibility: Significantly improved
```

---

### 1.4 Treatment Taxonomy Standardization

**Current Gap:** Inconsistent treatment values; no semantic weights or precedent effects defined.

**Why Critical:** Treatment is the most important property in legal graphs. Inconsistency breaks precedent analysis, overruling detection, and answer quality.

#### Canonical Treatment Taxonomy

```python
TREATMENT_TAXONOMY = {
    "applies": {
        "description": "Applies the cited law/precedent as binding authority",
        "weight": 1.0,
        "precedent_effect": "binding",
        "synonyms": ["applied", "applying"],
        "examples": [
            "Court applied Section 17 to facts",
            "Applying the principle in KB Saha..."
        ]
    },

    "follows": {
        "description": "Follows precedent without modification or distinction",
        "weight": 0.9,
        "precedent_effect": "binding",
        "synonyms": ["followed", "following"],
        "examples": [
            "Court followed the ratio in Siddique Mia",
            "Following the Supreme Court decision in..."
        ]
    },

    "distinguishes": {
        "description": "Distinguishes on facts; not applying rule to current case",
        "weight": 0.3,
        "precedent_effect": "non-binding",
        "synonyms": ["distinguished", "distinguishing"],
        "examples": [
            "Distinguished from KB Saha on facts",
            "Case distinguishable as lease exceeded 5 years"
        ]
    },

    "overruled": {
        "description": "Overturns or reverses prior authority",
        "weight": -1.0,
        "precedent_effect": "reversed",
        "synonyms": ["overruling", "reversed", "set aside"],
        "examples": [
            "Earlier decision in XYZ overruled",
            "Ratio in ABC no longer good law"
        ]
    },

    "criticizes": {
        "description": "Criticizes reasoning but doesn't overturn",
        "weight": -0.3,
        "precedent_effect": "weakened",
        "synonyms": ["criticized", "questioned", "doubted"],
        "examples": [
            "Reasoning in earlier case questioned",
            "With respect, decision in ABC flawed"
        ]
    },

    "qualified": {
        "description": "Partially applies or narrows scope of rule",
        "weight": 0.6,
        "precedent_effect": "limited",
        "synonyms": ["qualified", "limited", "narrowed"],
        "examples": [
            "Principle limited to identical facts",
            "Scope of ratio qualified to exclude..."
        ]
    },

    "harmonized": {
        "description": "Reconciles or harmonizes conflicting authorities",
        "weight": 0.8,
        "precedent_effect": "reconciled",
        "synonyms": ["harmonized", "reconciled"],
        "examples": [
            "Conflicting decisions harmonized",
            "Apparent conflict resolved by..."
        ]
    }
}
```

#### Derived Relationships

```python
# Create convenience relationships from CITES treatment

def create_derived_relationships(case, cites_edges):
    """
    Create typed relationships derived from CITES treatment
    """

    for cites in cites_edges:
        treatment = cites["treatment"]
        cited_case = cites["target"]

        # Create specific relationship types
        if treatment == "follows":
            create_relationship(case, "FOLLOWS", cited_case, {
                "date": case.decision_date,
                "cites_edge_id": cites.id
            })

        elif treatment == "overruled":
            create_relationship(cited_case, "OVERRULED_BY", case, {
                "date": case.decision_date,
                "reason": cites.get("context"),
                "cites_edge_id": cites.id
            })

            # Mark cited case status
            update_node(cited_case, {
                "status": "Overruled",
                "overruled_by": case.id,
                "overruled_date": case.decision_date
            })

        elif treatment == "distinguishes":
            create_relationship(case, "DISTINGUISHES", cited_case, {
                "distinguishing_factors": extract_factors(cites.context),
                "cites_edge_id": cites.id
            })
```

#### Treatment Validation Rules

```cypher
// Find inconsistent treatments

// Rule 1: Case cannot follow and distinguish same case
MATCH (c:Case)-[r1:CITES {treatment:'follows'}]->(cited:Case),
      (c)-[r2:CITES {treatment:'distinguishes'}]->(cited)
RETURN c.id, cited.id, 'inconsistent_treatment' AS issue;

// Rule 2: Overruled case should not be marked Active
MATCH (c:Case {status:'Active'})-[:OVERRULED_BY]->(overruling:Case)
RETURN c.id, overruling.id, 'status_not_updated' AS issue;

// Rule 3: Check for circular overruling (impossible)
MATCH path = (c1:Case)-[:OVERRULED_BY*]->(c1)
RETURN path, 'circular_overruling' AS issue;
```

#### Action Items

- [ ] **Task 1.4.1:** Define canonical taxonomy (done above)
  - Document all treatment types with weights
  - Create examples and decision tree
  - Effort: 2 days

- [ ] **Task 1.4.2:** Validate existing CITES edges
  - Run validation queries
  - Fix inconsistencies
  - Effort: 1 week

- [ ] **Task 1.4.3:** Create derived relationship scripts
  - Generate FOLLOWS, OVERRULED_BY edges
  - Update case status fields
  - Effort: 2 days

- [ ] **Task 1.4.4:** Build treatment change log
  - Track when case status changes
  - Create StatusChange events
  - Effort: 3 days

- [ ] **Task 1.4.5:** Update treatment classifier training
  - Retrain with canonical labels
  - Enforce taxonomy in output
  - Effort: 1 week

#### Expected Impact

```
Improvements:
├─ Treatment consistency: 100% (was 70%)
├─ Overruling detection: Automated
├─ Precedent weight calculation: Enabled
└─ Legal reasoning accuracy: +30%
```

---

### 1.5 Cross-Jurisdiction Enhancement

**Current Gap:** Basic jurisdiction property; limited cross-border comparison capabilities.

**Why Critical:** Common law jurisdictions (BD/IN/PK) share legal heritage. Cases from one jurisdiction are persuasive in another. Researchers need to compare interpretations.

#### Enhanced Cross-Jurisdiction Schema

```json
{
  "relationship_type": "HARMONIZED_WITH",
  "from": "Case",
  "to": "Case",
  "properties": {
    "jurisdictions": {
      "type": "string[]",
      "examples": [["BD", "IN"], ["IN", "PK"], ["BD", "PK"]],
      "description": "Jurisdictions being harmonized"
    },
    "commonPrinciple": {
      "type": "string",
      "required": true,
      "description": "Shared legal principle"
    },
    "commonStatute": {
      "type": "string",
      "description": "If based on identical statute (e.g., CPC 1908)"
    },
    "reasoningSimilarity": {
      "type": "float",
      "range": [0.0, 1.0],
      "description": "Semantic similarity of legal reasoning"
    },
    "harmonizedBy": {
      "type": "string",
      "description": "Later case that explicitly harmonized"
    },
    "confidence": {
      "type": "float",
      "description": "Confidence in harmonization"
    }
  }
}

{
  "relationship_type": "DIVERGES_FROM",
  "from": "Case",
  "to": "Case",
  "properties": {
    "jurisdictions": {
      "type": "string[]"
    },
    "pointOfDivergence": {
      "type": "string",
      "required": true,
      "description": "Specific point where interpretations differ"
    },
    "reason": {
      "type": "string",
      "description": "Why jurisdictions diverged"
    },
    "severity": {
      "type": "enum",
      "values": ["minor", "significant", "fundamental"],
      "description": "Degree of divergence"
    },
    "legalBasis": {
      "type": "string",
      "description": "Legal justification for divergence"
    },
    "reconciliationAttempted": {
      "type": "boolean",
      "description": "Has later case tried to reconcile?"
    }
  }
}
```

#### Cross-Jurisdiction Analysis Pipeline

```python
class CrossJurisdictionAnalyzer:
    """
    Find harmonies and divergences across jurisdictions
    """

    def analyze_section_across_jurisdictions(self, section_number, statute_name):
        """
        Compare how BD/IN/PK interpret same statutory provision
        """

        # Find cases from each jurisdiction
        bd_cases = find_cases(
            statute=statute_name,
            section=section_number,
            jurisdiction="BD"
        )

        in_cases = find_cases(
            statute=statute_name,
            section=section_number,
            jurisdiction="IN"
        )

        pk_cases = find_cases(
            statute=statute_name,
            section=section_number,
            jurisdiction="PK"
        )

        # Compare key holdings
        harmonies = []
        divergences = []

        for bd_case in bd_cases:
            for in_case in in_cases:
                similarity = compute_reasoning_similarity(
                    bd_case.holdings,
                    in_case.holdings
                )

                if similarity > 0.75:
                    # Harmonized interpretation
                    harmonies.append({
                        "bd_case": bd_case,
                        "in_case": in_case,
                        "similarity": similarity,
                        "common_principle": extract_common_principle(
                            bd_case, in_case
                        )
                    })

                elif similarity < 0.4:
                    # Divergent interpretation
                    divergences.append({
                        "bd_case": bd_case,
                        "in_case": in_case,
                        "divergence_point": identify_divergence(
                            bd_case, in_case
                        ),
                        "severity": classify_severity(bd_case, in_case)
                    })

        return {
            "harmonies": harmonies,
            "divergences": divergences
        }

    def compute_reasoning_similarity(self, holdings1, holdings2):
        """
        Semantic similarity between legal reasoning
        """
        # Embed all holdings
        embeddings1 = [embed(h.text) for h in holdings1]
        embeddings2 = [embed(h.text) for h in holdings2]

        # Compute pairwise similarities
        max_similarities = []
        for emb1 in embeddings1:
            similarities = [cosine_similarity(emb1, emb2) for emb2 in embeddings2]
            max_similarities.append(max(similarities))

        # Average of max similarities
        return sum(max_similarities) / len(max_similarities)
```

#### Comparative Law Query Examples

```cypher
// Query 1: Find BD cases harmonized with Indian precedents
MATCH (bd:Case {jurisdiction:'BD'})-[h:HARMONIZED_WITH]->(in:Case {jurisdiction:'IN'})
WHERE h.reasoningSimilarity > 0.75
RETURN bd.title, in.title, h.commonPrinciple, h.reasoningSimilarity
ORDER BY h.reasoningSimilarity DESC
LIMIT 20;

// Query 2: Find divergences on specific statute
MATCH (c1:Case)-[d:DIVERGES_FROM]->(c2:Case)
WHERE c1.jurisdiction <> c2.jurisdiction
  AND d.severity = 'significant'
RETURN c1.jurisdiction, c2.jurisdiction,
       c1.title, c2.title, d.pointOfDivergence
ORDER BY d.severity DESC;

// Query 3: Track interpretation evolution across jurisdictions
MATCH path = (bd:Case {jurisdiction:'BD'})-[:CITES*1..3]-(in:Case {jurisdiction:'IN'})
WHERE ANY(r IN relationships(path) WHERE r.citationType = 'judicial')
RETURN path
LIMIT 10;
```

#### Action Items

- [ ] **Task 1.5.1:** Build cross-jurisdiction comparison pipeline
  - Implement semantic similarity computation
  - Identify harmonies and divergences
  - Effort: 2 weeks

- [ ] **Task 1.5.2:** Run backfill analysis
  - Compare existing cases across jurisdictions
  - Create HARMONIZED_WITH / DIVERGES_FROM edges
  - Effort: 1 week (compute time)

- [ ] **Task 1.5.3:** Add comparative law queries to API
  - Expose endpoints for cross-jurisdiction search
  - Build UI components
  - Effort: 1 week

- [ ] **Task 1.5.4:** Create jurisdiction comparison reports
  - Generate reports: "BD vs IN on Section 17"
  - Show harmonies, divergences, key cases
  - Effort: 1 week

#### Expected Impact

```
New Capabilities:
├─ Cross-jurisdiction precedent search
├─ Comparative law analysis
├─ Identification of persuasive authorities
└─ Conflict detection across borders

Research Quality: +30% for multi-jurisdiction queries
```

---

### 1.6 Intent Detection for Query Optimization

**Current Gap:** All queries use same ranking weights; no adaptation to query type.

**Why Critical:** Different query types need different strategies. Statutory citations need exact keyword match; factual questions need semantic search. One-size-fits-all is suboptimal.

#### Query Intent Types

```python
from enum import Enum

class QueryIntent(Enum):
    STATUTE_LOOKUP = "statute"         # "Section 17 CPC"
    CASE_LOOKUP = "case"               # "KB Saha v. DCL"
    LEGAL_CONCEPT = "concept"          # "What is res judicata?"
    FACTUAL_QUESTION = "factual"       # "Do leases need registration?"
    PROCEDURAL = "procedural"          # "How to file revision?"
    COMPARATIVE = "comparative"        # "BD vs IN on pre-emption"
    HYPOTHETICAL = "hypothetical"      # "If I sign unregistered lease..."
    PRECEDENT_SEARCH = "precedent"     # "Cases on Section 17"
    DEFINITION = "definition"          # "Define Order VI r.17"
```

#### Intent Detection Implementation

```python
class IntentDetector:
    """
    Multi-strategy intent detection
    """

    def __init__(self):
        self.statute_patterns = compile_statute_patterns()
        self.case_patterns = compile_case_patterns()
        self.intent_classifier = load_ml_classifier()

    def detect(self, query):
        # Strategy 1: Rule-based patterns (fast, high precision)
        rule_intent = self._check_patterns(query)
        if rule_intent:
            return rule_intent

        # Strategy 2: Query structure heuristics
        heuristic_intent = self._check_heuristics(query)
        if heuristic_intent:
            return heuristic_intent

        # Strategy 3: ML classifier (for ambiguous cases)
        ml_intent = self.intent_classifier.predict(query)
        return ml_intent

    def _check_patterns(self, query):
        """
        Check regex patterns for clear intents
        """
        query_lower = query.lower()

        # Statutory citation pattern
        if re.search(r'\b(section|article|order)\s+\d+', query_lower):
            return QueryIntent.STATUTE_LOOKUP

        # Case citation pattern
        if re.search(r'\b\d{4}\s+\w+\s+\d+\b', query):
            return QueryIntent.CASE_LOOKUP

        # Case name pattern
        if ' v. ' in query or ' vs. ' in query:
            return QueryIntent.CASE_LOOKUP

        return None

    def _check_heuristics(self, query):
        """
        Check query structure for intent signals
        """
        query_lower = query.lower()

        # Definition queries
        if query_lower.startswith(("what is", "define", "meaning of")):
            return QueryIntent.DEFINITION

        # Procedural queries
        if query_lower.startswith(("how to", "procedure", "process")):
            return QueryIntent.PROCEDURAL

        # Comparative queries
        if any(word in query_lower for word in ["compare", "difference", "vs", "versus"]):
            if any(juris in query for juris in ["BD", "IN", "PK", "India", "Bangladesh"]):
                return QueryIntent.COMPARATIVE

        # Hypothetical queries
        if query_lower.startswith(("if ", "suppose ", "what if")):
            return QueryIntent.HYPOTHETICAL

        # Factual questions (default for "do", "does", "is", "can")
        if query_lower.startswith(("do ", "does ", "is ", "can ", "are ")):
            return QueryIntent.FACTUAL_QUESTION

        return None
```

#### Intent-Adaptive Ranking

```python
# Different ranking weights per intent

RANKING_WEIGHTS = {
    QueryIntent.STATUTE_LOOKUP: {
        "semantic": 0.20,
        "keyword": 0.65,      # High keyword weight for exact match
        "trust": 0.10,
        "recency": 0.05
    },

    QueryIntent.CASE_LOOKUP: {
        "semantic": 0.25,
        "keyword": 0.60,      # High keyword for citation match
        "trust": 0.10,
        "recency": 0.05
    },

    QueryIntent.FACTUAL_QUESTION: {
        "semantic": 0.60,     # High semantic for understanding
        "keyword": 0.25,
        "trust": 0.10,
        "recency": 0.05
    },

    QueryIntent.LEGAL_CONCEPT: {
        "semantic": 0.55,
        "keyword": 0.20,
        "trust": 0.15,        # Higher trust for concept definitions
        "recency": 0.10
    },

    QueryIntent.PROCEDURAL: {
        "semantic": 0.50,
        "keyword": 0.30,
        "trust": 0.10,
        "recency": 0.10       # Procedures may change
    },

    QueryIntent.COMPARATIVE: {
        "semantic": 0.65,     # High semantic for reasoning comparison
        "keyword": 0.20,
        "trust": 0.10,
        "recency": 0.05
    },

    QueryIntent.HYPOTHETICAL: {
        "semantic": 0.70,     # Highest semantic - need reasoning
        "keyword": 0.15,
        "trust": 0.10,
        "recency": 0.05
    }
}

def compute_final_score(chunk, query, intent):
    """
    Compute final ranking score based on intent
    """
    weights = RANKING_WEIGHTS.get(intent, RANKING_WEIGHTS[QueryIntent.FACTUAL_QUESTION])

    return (
        weights["semantic"] * chunk.semantic_score +
        weights["keyword"] * chunk.keyword_score +
        weights["trust"] * chunk.trust_score +
        weights["recency"] * chunk.recency_score
    )
```

#### Intent-Specific Retrieval Strategies

```python
def retrieve_with_intent(query, intent):
    """
    Use different retrieval strategy based on intent
    """

    if intent == QueryIntent.STATUTE_LOOKUP:
        # For statute lookup, keyword search first
        section_num = extract_section_number(query)
        chunks = keyword_search(section_num, doc_type="section")

        if len(chunks) > 0:
            # Found exact match, supplement with semantic
            semantic_chunks = vector_search(query, top_k=10)
            return merge_results(chunks, semantic_chunks, primary="keyword")
        else:
            # Fallback to semantic
            return vector_search(query, top_k=20)

    elif intent == QueryIntent.CASE_LOOKUP:
        # For case lookup, search by citation
        citation = extract_citation(query)
        case = find_case_by_citation(citation)

        if case:
            return get_case_chunks(case)
        else:
            # Fuzzy match on case name
            return fuzzy_case_search(query)

    elif intent in [QueryIntent.FACTUAL_QUESTION, QueryIntent.HYPOTHETICAL]:
        # For factual/hypothetical, semantic first
        vector_chunks = vector_search(query, top_k=50)

        # Multi-hop expansion for complex questions
        if intent == QueryIntent.HYPOTHETICAL:
            expanded = multi_hop_retrieve(query, initial_chunks=vector_chunks)
            return rerank(query, expanded)

        return rerank(query, vector_chunks)

    elif intent == QueryIntent.COMPARATIVE:
        # For comparative, fetch from multiple jurisdictions
        jurisdiction1, jurisdiction2 = extract_jurisdictions(query)

        results_j1 = vector_search(
            query,
            filters={"jurisdiction": jurisdiction1},
            top_k=20
        )

        results_j2 = vector_search(
            query,
            filters={"jurisdiction": jurisdiction2},
            top_k=20
        )

        return {"jurisdiction1": results_j1, "jurisdiction2": results_j2}

    else:
        # Default strategy
        return vector_search(query, top_k=30)
```

#### Action Items

- [ ] **Task 1.6.1:** Implement rule-based intent detection
  - Build regex patterns for citations
  - Heuristics for question types
  - Effort: 3 days

- [ ] **Task 1.6.2:** Train ML intent classifier (optional)
  - Collect 500 labeled query-intent pairs
  - Train multi-class classifier
  - Effort: 1 week

- [ ] **Task 1.6.3:** Implement intent-adaptive ranking
  - Apply different weights per intent
  - A/B test on query logs
  - Effort: 2 days

- [ ] **Task 1.6.4:** Build intent-specific retrieval strategies
  - Implement specialized flows per intent
  - Effort: 1 week

- [ ] **Task 1.6.5:** Add intent indicator to UI
  - Show user detected intent
  - Allow manual override
  - Effort: 2 days

#### Expected Impact

```
Improvements by Intent Type:
├─ Statute Lookup: P@5 from 0.70 → 0.92 (+31%)
├─ Case Lookup: P@5 from 0.75 → 0.90 (+20%)
├─ Factual Questions: P@5 from 0.65 → 0.82 (+26%)
├─ Comparative: New capability
└─ Overall P@5: 0.75 → 0.88 (+17%)

Latency Reduction: -20% (avoid unnecessary searches)
```

---

## 🟡 Priority 2: RAG Optimizations

### 2.1 Legal-Domain Embeddings

**Current Gap:** Generic embeddings (OpenAI text-embedding-3) may miss legal nuances.

**Why Valuable:** Legal language has specific negation patterns, modal verbs (shall/may), and domain terminology. Legal-trained embeddings capture these better.

#### Embedding Model Evaluation

```
Model Candidates:

1. nlpaueb/legal-bert-base-uncased
   - Dimensions: 768
   - Trained on: Legal documents (caselaw, contracts, statutes)
   - Pros: Domain-specific, open source
   - Cons: Lower dimensions than OpenAI

2. allenai/longformer-base-4096
   - Dimensions: 768
   - Context: 4096 tokens (good for long judgments)
   - Pros: Handles long documents
   - Cons: Not legal-specific

3. sentence-transformers/all-mpnet-base-v2
   - Dimensions: 768
   - General purpose semantic search
   - Pros: Fast, good general performance
   - Cons: Not legal-optimized

4. text-embedding-3-large (OpenAI)
   - Dimensions: 3072
   - General purpose, SOTA performance
   - Pros: High quality, easy API
   - Cons: Not legal-specific, commercial

5. Custom fine-tuned model
   - Start with legal-BERT base
   - Fine-tune on your legal corpus
   - Pros: Optimized for your exact use case
   - Cons: Requires labeled training data
```

#### A/B Testing Framework

```python
def evaluate_embedding_model(model_name, test_set):
    """
    Evaluate embedding model on test queries
    """

    # Load model
    if model_name == "legal-bert":
        model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')
    elif model_name == "openai":
        model = OpenAIEmbeddings(model="text-embedding-3-large")
    # ... etc

    metrics = {
        "precision_at_5": [],
        "precision_at_10": [],
        "mrr": [],              # Mean Reciprocal Rank
        "ndcg": []              # Normalized DCG
    }

    for query, expected_chunks in test_set:
        # Embed query
        query_embedding = model.encode(query)

        # Retrieve from vector DB
        results = vector_db.search(
            query_embedding,
            top_k=10
        )

        result_ids = [r.id for r in results]

        # Calculate metrics
        p5 = len(set(result_ids[:5]) & set(expected_chunks)) / 5
        p10 = len(set(result_ids[:10]) & set(expected_chunks)) / 10

        metrics["precision_at_5"].append(p5)
        metrics["precision_at_10"].append(p10)

        # MRR: position of first correct result
        for i, rid in enumerate(result_ids, 1):
            if rid in expected_chunks:
                metrics["mrr"].append(1.0 / i)
                break
        else:
            metrics["mrr"].append(0.0)

    # Aggregate
    return {
        "model": model_name,
        "P@5": mean(metrics["precision_at_5"]),
        "P@10": mean(metrics["precision_at_10"]),
        "MRR": mean(metrics["mrr"])
    }
```

#### Fine-Tuning Recipe

```python
# Fine-tune legal-BERT on your corpus

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

def fine_tune_legal_bert(training_pairs):
    """
    Fine-tune legal-BERT for your specific legal corpus
    """

    # Load base model
    model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')

    # Prepare training examples
    # Each example: (query, positive_chunk, [negative_chunks])
    train_examples = []

    for pair in training_pairs:
        example = InputExample(
            texts=[pair.query, pair.positive_chunk],
            label=1.0  # Positive pair
        )
        train_examples.append(example)

        # Add hard negatives (similar but wrong)
        for neg_chunk in pair.negative_chunks:
            neg_example = InputExample(
                texts=[pair.query, neg_chunk],
                label=0.0
            )
            train_examples.append(neg_example)

    # Create DataLoader
    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=16
    )

    # Define loss function
    # MultipleNegativesRankingLoss is good for retrieval
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # Train
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=3,
        warmup_steps=100,
        output_path='./legal-bert-finetuned'
    )

    return model
```

#### Action Items

- [ ] **Task 2.1.1:** Create evaluation test set
  - 100-200 (query, expected_chunks) pairs
  - Cover different query types
  - Effort: 1 week

- [ ] **Task 2.1.2:** Run A/B tests on embedding models
  - Test 4-5 candidate models
  - Compare P@5, P@10, MRR
  - Effort: 3 days

- [ ] **Task 2.1.3:** Fine-tune chosen model (optional)
  - Create training pairs from your corpus
  - Fine-tune for 3 epochs
  - Effort: 1 week

- [ ] **Task 2.1.4:** Re-embed all chunks
  - Generate embeddings with chosen model
  - Update vector DB
  - Effort: 1 day (compute time)

- [ ] **Task 2.1.5:** Monitor performance improvement
  - Track P@K metrics on production queries
  - Compare before/after
  - Effort: Ongoing

#### Expected Impact

```
Embedding Quality:
├─ P@5: 0.75 → 0.85 (+13%)
├─ Legal concept matching: +20%
├─ Negation handling: +30%
└─ Modal verb understanding: +25%

Note: Impact varies by base model chosen
```

---

### 2.2 Cross-Encoder Reranking

**Current Gap:** Only bi-encoder (vector search); no reranking for top candidates.

**Why Valuable:** Bi-encoders are fast but less accurate. Cross-encoders compute query-chunk similarity jointly, much more accurate but slower. Use cross-encoder to rerank top 20-50 results.

#### Architecture

```
Retrieval Pipeline with Cross-Encoder:

1. Bi-Encoder (Fast)
   Query → [Embed] → Vector DB → Top 50 chunks

2. Keyword Boost (Fast)
   Apply keyword matching scores

3. Cross-Encoder Rerank (Slow but Accurate)
   For each of top 20-30 chunks:
   - Input: (query, chunk_text)
   - Output: relevance score 0-1
   - Sort by cross-encoder score

4. Final Ranking
   Combine cross-encoder + trust + recency
   Return top 10
```

#### Implementation

```python
from sentence_transformers import CrossEncoder

class HybridRetriever:
    """
    Multi-stage retrieval with cross-encoder reranking
    """

    def __init__(self):
        # Stage 1: Fast bi-encoder
        self.bi_encoder = SentenceTransformer('legal-bert-finetuned')

        # Stage 3: Accurate cross-encoder
        self.cross_encoder = CrossEncoder(
            'cross-encoder/ms-marco-MiniLM-L-6-v2'
            # Or fine-tune a legal cross-encoder
        )

    def retrieve(self, query, top_k=10):
        # Stage 1: Bi-encoder vector search (fast, top 50)
        query_embedding = self.bi_encoder.encode(query)
        vector_hits = vector_db.search(
            query_embedding,
            top_k=50
        )

        # Stage 2: Keyword boost
        chunks = fetch_chunks([hit.id for hit in vector_hits])
        for chunk, hit in zip(chunks, vector_hits):
            chunk.semantic_score = hit.score
            chunk.keyword_score = compute_keyword_score(query, chunk)

        # Filter to top 20-30 for cross-encoder
        chunks.sort(
            key=lambda c: 0.7 * c.semantic_score + 0.3 * c.keyword_score,
            reverse=True
        )
        top_chunks = chunks[:25]

        # Stage 3: Cross-encoder rerank (slow, accurate)
        pairs = [[query, chunk.text] for chunk in top_chunks]
        ce_scores = self.cross_encoder.predict(pairs)

        # Stage 4: Final ranking
        for chunk, ce_score in zip(top_chunks, ce_scores):
            chunk.cross_encoder_score = ce_score
            chunk.final_score = (
                0.60 * ce_score +
                0.25 * chunk.trust_score +
                0.10 * chunk.keyword_score +
                0.05 * chunk.recency_score
            )

        # Sort and return
        top_chunks.sort(key=lambda c: c.final_score, reverse=True)
        return top_chunks[:top_k]
```

#### Cross-Encoder Fine-Tuning

```python
# Fine-tune cross-encoder on legal query-chunk pairs

def fine_tune_cross_encoder(training_data):
    """
    Fine-tune cross-encoder for legal retrieval

    training_data: List of (query, chunk, relevance_score)
    """

    model = CrossEncoder(
        'cross-encoder/ms-marco-MiniLM-L-6-v2',
        num_labels=1  # Regression task (0-1 score)
    )

    # Prepare training samples
    train_samples = []
    for query, chunk, score in training_data:
        train_samples.append(InputExample(
            texts=[query, chunk],
            label=float(score)  # 0.0 to 1.0
        ))

    # Train
    model.fit(
        train_dataloader=DataLoader(train_samples, batch_size=16),
        epochs=2,
        warmup_steps=50,
        output_path='./cross-encoder-legal'
    )

    return model
```

#### Action Items

- [ ] **Task 2.2.1:** Integrate cross-encoder into pipeline
  - Add reranking stage after vector search
  - Test on top 20-30 candidates
  - Effort: 3 days

- [ ] **Task 2.2.2:** Collect reranking training data (optional)
  - For 200+ queries, label top results as relevant/not
  - Use for fine-tuning
  - Effort: 1 week

- [ ] **Task 2.2.3:** Fine-tune cross-encoder (optional)
  - Train on legal query-chunk pairs
  - Effort: 3 days

- [ ] **Task 2.2.4:** Optimize reranking budget
  - Test reranking top-10 vs top-20 vs top-30
  - Balance accuracy vs latency
  - Effort: 2 days

- [ ] **Task 2.2.5:** Cache cross-encoder results
  - Cache for common queries
  - Effort: 1 day

#### Expected Impact

```
Retrieval Quality:
├─ P@5: 0.85 → 0.92 (+8%)
├─ P@10: 0.75 → 0.85 (+13%)
├─ Reduction in irrelevant results: -40%

Latency:
├─ Without cache: +200ms
└─ With cache (80% hit rate): +40ms average

ROI: High - Significant quality improvement for modest latency cost
```

---

### 2.3 Multi-Hop Reasoning

**Current Gap:** Single-step retrieval; doesn't follow citation chains or expand context.

**Why Valuable:** Complex legal questions require following precedent chains, finding related statutes, and building comprehensive context. Single-hop retrieval misses important connections.

#### Multi-Hop Algorithm

```python
class MultiHopRetriever:
    """
    Iteratively expand context through graph traversal
    """

    def retrieve(self, query, max_hops=3, budget=50):
        contexts = []
        seen_chunks = set()

        # Hop 0: Direct retrieval
        initial_chunks = self.vector_search(query, top_k=15)
        contexts.extend(initial_chunks)
        seen_chunks.update([c.id for c in initial_chunks])

        for hop in range(1, max_hops):
            # Extract entities from current context
            entities = self.extract_entities(contexts)

            if not entities:
                break  # No entities to expand

            # Expand via graph traversal
            expanded_chunks = []

            for entity in entities:
                if entity.type == "Section":
                    # Get cases citing this section
                    citing_cases = graph_query("""
                        MATCH (s:Section {id: $id})
                              <-[:CITES {treatment: $treatments}]-(h:Holding)
                              <-[:HAS_HOLDING]-(c:Case)
                        MATCH (c)-[:HAS_CHUNK]->(chunk:TextChunk)
                        WHERE chunk.chunkType IN ['holding', 'reasoning']
                          AND NOT chunk.id IN $seen
                          AND chunk.trust_score >= 0.75
                        RETURN chunk
                        ORDER BY chunk.trust_score DESC
                        LIMIT 5
                    """, {
                        "id": entity.id,
                        "treatments": ["applies", "follows"],
                        "seen": list(seen_chunks)
                    })

                    expanded_chunks.extend(citing_cases)

                elif entity.type == "Case":
                    # Get precedents followed by this case
                    precedents = graph_query("""
                        MATCH (c:Case {id: $id})
                              -[:HAS_HOLDING]->(h:Holding)
                              -[:CITES {treatment: 'follows'}]->(cited)
                        MATCH (cited)-[:HAS_CHUNK]->(chunk:TextChunk)
                        WHERE NOT chunk.id IN $seen
                        RETURN chunk
                        LIMIT 5
                    """, {"id": entity.id, "seen": list(seen_chunks)})

                    expanded_chunks.extend(precedents)

                elif entity.type == "LegalConcept":
                    # Get other cases applying this concept
                    related_cases = graph_query("""
                        MATCH (concept:LegalConcept {id: $id})
                              <-[:APPLIES_CONCEPT]-(h:Holding)
                              <-[:HAS_HOLDING]-(c:Case)
                        MATCH (c)-[:HAS_CHUNK]->(chunk:TextChunk)
                        WHERE NOT chunk.id IN $seen
                          AND chunk.trust_score >= 0.75
                        RETURN chunk
                        ORDER BY chunk.trust_score DESC
                        LIMIT 5
                    """, {"id": entity.id, "seen": list(seen_chunks)})

                    expanded_chunks.extend(related_cases)

                # Check budget
                if len(contexts) + len(expanded_chunks) >= budget:
                    break

            # Add new chunks
            contexts.extend(expanded_chunks)
            seen_chunks.update([c.id for c in expanded_chunks])

            # Stop if no expansion
            if len(expanded_chunks) == 0:
                break

        # Final reranking
        reranked = self.rerank_with_diversity(query, contexts, top_k=15)

        # Annotate with hop metadata
        for chunk in reranked:
            chunk.hop_info = {
                "hop_number": which_hop(chunk, initial_chunks),
                "expansion_reason": why_included(chunk)
            }

        return reranked
```

#### Entity Extraction

```python
def extract_entities(chunks):
    """
    Extract legal entities from text chunks
    """
    entities = []

    for chunk in chunks:
        # Extract section references
        section_refs = extract_section_references(chunk.text)
        for ref in section_refs:
            section = resolve_section_reference(ref)
            if section:
                entities.append({
                    "type": "Section",
                    "id": section.id,
                    "text": ref
                })

        # Extract case citations
        case_citations = extract_case_citations(chunk.text)
        for citation in case_citations:
            case = resolve_case_citation(citation)
            if case:
                entities.append({
                    "type": "Case",
                    "id": case.id,
                    "text": citation
                })

        # Extract mentioned concepts (via NER or keyword)
        concepts = extract_legal_concepts(chunk.text)
        for concept_mention in concepts:
            concept = resolve_concept(concept_mention)
            if concept:
                entities.append({
                    "type": "LegalConcept",
                    "id": concept.id,
                    "text": concept_mention
                })

    # Deduplicate and rank by frequency
    entity_counts = Counter([e["id"] for e in entities])
    top_entities = [e for e in entities if entity_counts[e["id"]] >= 1]

    return top_entities
```

#### Action Items

- [ ] **Task 2.3.1:** Implement entity extraction
  - Build NER for sections, cases, concepts
  - Effort: 1 week

- [ ] **Task 2.3.2:** Build graph traversal templates
  - Cypher queries for common expansions
  - Effort: 3 days

- [ ] **Task 2.3.3:** Integrate multi-hop into pipeline
  - Add as option for complex queries
  - Effort: 1 week

- [ ] **Task 2.3.4:** Add hop visualization to UI
  - Show reasoning chain to users
  - Effort: 3 days

#### Expected Impact

```
Complex Query Performance:
├─ Questions requiring 2+ sources: +45%
├─ Precedent chain completeness: +60%
├─ Context comprehensiveness: +40%

Latency: +300-500ms per hop
Use Case: Reserve for complex/hypothetical questions
```

---

### 2.4-2.7 Additional RAG Optimizations

*(Due to length constraints, providing abbreviated versions)*

### 2.4 Chunk Importance Scoring

Add `importance_score` property based on:
- Position in document
- Citation frequency
- Legal keyword density
- Presence of holdings

**Impact:** +20% in surfacing key legal reasoning

---

### 2.5 Temporal Query Handling

Extract dates from queries; retrieve law applicable at that date.

**Example:**
```python
query = "Was Section 17 in effect in 2000?"
effective_date = extract_date(query)  # 2000-01-01
version = get_version_for_date(statute, effective_date)
```

**Impact:** Accurate historical legal research

---

### 2.6 Negation Detection

Use spaCy to detect negated legal statements; avoid retrieving contradictory chunks.

**Impact:** -30% contradiction errors

---

### 2.7 Automated Query Suggestions

Generate related queries based on retrieved entities.

**Example:**
```
User: "Section 17 registration"
Suggestions:
- "Has Section 17 been amended?"
- "Which cases interpret Section 17?"
- "Compare Section 17 in BD vs IN"
```

**Impact:** Enhanced user exploration

---

## 🟠 Priority 3: Query & Performance

### 3.1 Materialized Views

Cache common aggregations:

```cypher
// Precompute top-cited sections
CREATE VIEW top_cited_sections AS
MATCH (s:Section)<-[r:CITES]-(h:Holding)
RETURN s.id, s.sectionNumber, count(r) AS citations
ORDER BY citations DESC;
```

**Impact:** 60% faster for common queries

---

### 3.2 Caching Strategy

Use Redis to cache:
- Common queries (TTL: 1 hour)
- Section → cases mappings (TTL: 6 hours)
- Cross-encoder scores (TTL: 24 hours)

**Implementation:**
```python
@cache(ttl=3600)
def get_section_cases(section_id):
    return graph.query(...)
```

**Impact:** Sub-100ms for cached queries

---

### 3.3 Query Complexity Budget

Enforce limits:
- Max traversal depth: 3 hops
- Max chunks returned: 50
- Query timeout: 2000ms

**Impact:** Predictable performance

---

### 3.4 Parallel Execution

Run vector search, keyword search, graph search in parallel.

**Impact:** -40% latency

---

### 3.5 Query Templates

Pre-built Cypher patterns for common tasks.

**Impact:** Easier maintenance, consistent performance

---

## 🔵 Priority 4: Advanced Features

*(Abbreviated for space)*

### 4.1 Contradiction Detection

Use NLI model to find contradictory chunks.

### 4.2 Legal Argument Generation

Generate structured arguments with citations.

### 4.3 Automated Legal Memo Generation

Create formatted legal memos.

### 4.4 Citation Network Visualization

Generate graph visualizations of precedent chains.

### 4.5 Jurisdiction Customization

Apply jurisdiction-specific rules and formatting.

*(Full details available in separate advanced features document)*

---

## 📅 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Goals:** Critical data quality improvements

#### Week 1
- [ ] Enhanced CITES schema
- [ ] Build citation extraction regex
- [ ] Add sourceType to Source nodes
- [ ] Classify existing sources

#### Week 2
- [ ] Train treatment classifier
- [ ] Define treatment taxonomy
- [ ] Validate existing CITES edges
- [ ] Create derived relationships

#### Week 3
- [ ] Implement paragraph-level chunker
- [ ] Re-chunk all documents
- [ ] Build chunk type classifier
- [ ] Update vector DB

#### Week 4
- [ ] Implement intent detection
- [ ] Add adaptive ranking weights
- [ ] Test on query logs
- [ ] Add intent UI indicator

**Deliverables:**
- ✅ Treatment classification accuracy ≥ 85%
- ✅ Source hierarchy complete
- ✅ Paragraph-level chunks with offsets
- ✅ Intent-aware retrieval

**Success Metrics:**
- Citation extraction recall: +25%
- Trust score coverage: 100%
- Chunk precision: +20%
- Query latency variance: -30%

---

### Phase 2: RAG Optimization (Weeks 5-8)

**Goals:** Improve retrieval quality

#### Week 5
- [ ] Create embedding evaluation test set
- [ ] A/B test embedding models
- [ ] Choose best model
- [ ] Re-embed all chunks

#### Week 6
- [ ] Integrate cross-encoder reranking
- [ ] Test reranking budget (top-N)
- [ ] Cache cross-encoder results
- [ ] Monitor latency impact

#### Week 7
- [ ] Build entity extraction NER
- [ ] Implement multi-hop retrieval
- [ ] Add graph traversal templates
- [ ] Test on complex queries

#### Week 8
- [ ] Add chunk importance scoring
- [ ] Implement temporal query handling
- [ ] Add negation detection
- [ ] Build query suggestion engine

**Deliverables:**
- ✅ Legal-domain embeddings deployed
- ✅ Cross-encoder reranking active
- ✅ Multi-hop reasoning for complex queries
- ✅ Temporal and negation handling

**Success Metrics:**
- P@5: +15%
- P@10: +20%
- Complex query success rate: +45%
- Contradiction errors: -30%

---

### Phase 3: Performance & Scale (Weeks 9-11)

**Goals:** Production-grade performance

#### Week 9
- [ ] Create materialized views
- [ ] Update denormalized fields
- [ ] Set up automated refresh jobs

#### Week 10
- [ ] Implement Redis caching layer
- [ ] Add cache warming for common queries
- [ ] Monitor cache hit rates

#### Week 11
- [ ] Build query templates library
- [ ] Enforce complexity budgets
- [ ] Implement parallel execution
- [ ] Performance testing

**Deliverables:**
- ✅ Sub-200ms cached query response
- ✅ 40% cache hit rate
- ✅ Query templates for all common patterns
- ✅ Performance SLAs met

**Success Metrics:**
- P50 latency: -60%
- P95 latency: -40%
- Cache hit rate: ≥ 40%
- Query failures: < 0.1%

---

### Phase 4: Advanced Features (Weeks 12-17)

**Goals:** Enhanced user experience

#### Weeks 12-13: Contradiction & Arguments
- [ ] Integrate NLI model
- [ ] Build contradiction detector
- [ ] Create argument generator
- [ ] Test on real cases

#### Weeks 14-15: Memo Generation
- [ ] Build memo template engine
- [ ] Implement structured analysis
- [ ] Add citation formatting
- [ ] User testing

#### Weeks 16-17: Visualization & Customization
- [ ] Build citation network viz
- [ ] Add jurisdiction-specific rules
- [ ] Create comparative dashboards
- [ ] Final testing & documentation

**Deliverables:**
- ✅ Contradiction detection
- ✅ Legal argument generator
- ✅ Automated memo generation
- ✅ Citation network visualization
- ✅ Jurisdiction customization

**Success Metrics:**
- User satisfaction: ≥ 4.2/5.0
- Answer acceptance rate: ≥ 82%
- Feature adoption rate: ≥ 60%

---

## 🧪 Testing & Validation Framework

### Test Suite Organization

```
tests/
├── unit/
│   ├── test_citation_extraction.py
│   ├── test_treatment_classification.py
│   ├── test_intent_detection.py
│   └── test_chunking.py
├── integration/
│   ├── test_retrieval_pipeline.py
│   ├── test_multi_hop.py
│   └── test_cross_encoder.py
├── performance/
│   ├── test_query_latency.py
│   ├── test_cache_performance.py
│   └── test_parallel_execution.py
└── acceptance/
    ├── test_legal_accuracy.py
    ├── test_precedent_analysis.py
    └── test_user_scenarios.py
```

### Essential Test Cases

#### 1. Retrieval Accuracy Test

```python
def test_precision_at_k(k=5):
    """
    Test if correct chunks appear in top K results
    """
    test_cases = load_test_cases()  # 100-200 labeled queries

    precision_scores = []

    for test in test_cases:
        query = test["query"]
        expected_chunks = test["expected_chunk_ids"]

        # Retrieve
        results = retrieve_chunks(query, top_k=k)
        retrieved_ids = [c.id for c in results]

        # Calculate precision
        hits = len(set(retrieved_ids) & set(expected_chunks))
        precision = hits / k
        precision_scores.append(precision)

    avg_precision = sum(precision_scores) / len(precision_scores)

    # Assert target met
    assert avg_precision >= 0.85, f"P@{k} = {avg_precision:.3f} below 0.85"

    return avg_precision
```

#### 2. Treatment Classification Test

```python
def test_treatment_accuracy():
    """
    Test citation treatment classification
    """
    test_cases = load_treatment_test_cases()  # 200+ labeled

    correct = 0
    predictions = []

    for test in test_cases:
        predicted = classify_treatment(
            test["citing_text"],
            test["cited_doc"]
        )

        predictions.append({
            "expected": test["expected_treatment"],
            "predicted": predicted["treatment"],
            "confidence": predicted["confidence"]
        })

        if predicted["treatment"] == test["expected_treatment"]:
            correct += 1

    accuracy = correct / len(test_cases)

    # Calculate F1 per treatment type
    f1_scores = calculate_f1_per_class(predictions)

    assert accuracy >= 0.85, f"Treatment accuracy = {accuracy:.3f}"
    assert all(f1 >= 0.80 for f1 in f1_scores.values()), "Some treatments have low F1"

    return accuracy, f1_scores
```

#### 3. Temporal Accuracy Test

```python
def test_temporal_version_retrieval():
    """
    Test date-specific version retrieval
    """
    test_cases = [
        {
            "statute": "CPC 1908",
            "section": "Order VI r.17",
            "date": "2008-09-05",
            "expected_version": "urn:law:bd:statute:cpc:1908:ver:1908v1"
        },
        {
            "statute": "CPC 1908",
            "section": "Order VI r.17",
            "date": "2020-01-01",
            "expected_version": "urn:law:bd:statute:cpc:1908:ver:2001v1"
        }
    ]

    for test in test_cases:
        version = get_version_for_date(
            test["statute"],
            test["section"],
            test["date"]
        )

        assert version.id == test["expected_version"], \
            f"Wrong version for {test['date']}: got {version.id}"
```

#### 4. Performance Benchmark

```python
def test_query_latency_sla():
    """
    Test query response time SLA
    """
    queries = load_benchmark_queries()  # 1000 queries

    latencies = []

    for query in queries:
        start = time.time()
        results = retrieve_chunks(query)
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    # SLA targets
    assert p50 < 500, f"P50 = {p50}ms exceeds 500ms"
    assert p95 < 2000, f"P95 = {p95}ms exceeds 2000ms"
    assert p99 < 5000, f"P99 = {p99}ms exceeds 5000ms"

    print(f"Latency: P50={p50:.0f}ms, P95={p95:.0f}ms, P99={p99:.0f}ms")
```

### Continuous Monitoring

```python
# KPIs to track daily

DAILY_METRICS = {
    "retrieval_quality": {
        "precision_at_5": 0.85,        # Target
        "precision_at_10": 0.75,
        "mrr": 0.80
    },

    "classification_accuracy": {
        "treatment_f1": 0.85,
        "intent_accuracy": 0.90,
        "chunk_type_accuracy": 0.80
    },

    "performance": {
        "p50_latency_ms": 500,
        "p95_latency_ms": 2000,
        "cache_hit_rate": 0.40,
        "error_rate": 0.001
    },

    "data_quality": {
        "chunks_with_embeddings": 0.98,
        "cites_with_treatment": 0.90,
        "trust_score_coverage": 1.00
    }
}
```

---

## ⚡ Quick Wins Checklist

**Implement these in < 1 day each for immediate impact**

### Quick Win 1: Add sourceType to Sources (2 hours)

```cypher
// Classify existing sources
MATCH (s:Source)
WHERE s.publisher CONTAINS 'Government' OR s.publisher CONTAINS 'Official'
SET s.sourceType = 'primary_statute', s.authorityLevel = 5;

MATCH (s:Source)
WHERE s.publisher IN ['SCC Online', 'DLR', 'BLD']
SET s.sourceType = 'commercial_reporter', s.authorityLevel = 3;

MATCH (s:Source)
WHERE s.id CONTAINS 'upload'
SET s.sourceType = 'summary', s.authorityLevel = 2;
```

**Impact:** Users can filter by source authority immediately

---

### Quick Win 2: Create Top-Cited Sections View (1 hour)

```cypher
// Query to find top-cited sections
MATCH (s:Section)<-[:CITES]-(h:Holding)
WITH s, count(h) AS citations
ORDER BY citations DESC LIMIT 100
RETURN s.id, s.sectionNumber, s.title, citations;

// Store in denormalized field
MATCH (s:Section)<-[:CITES]-(h:Holding)<-[:HAS_HOLDING]-(c:Case)
WITH s, collect(DISTINCT c.id)[0..3] AS topCases
SET s.denorm_topCitedCases = topCases;
```

**Impact:** Instant access to important sections

---

### Quick Win 3: Implement Basic Intent Detection (4 hours)

```python
# Simple regex-based intent detection
def detect_intent_quick(query):
    query_lower = query.lower()

    if re.search(r'\bsection\s+\d+', query_lower):
        return "statute"
    elif ' v. ' in query or ' vs. ' in query:
        return "case"
    elif query_lower.startswith(("what is", "define")):
        return "definition"
    elif query_lower.startswith(("do ", "is ", "can ")):
        return "factual"
    else:
        return "general"
```

**Impact:** 20% better ranking immediately

---

### Quick Win 4: Add Redis Caching (3 hours)

```python
import redis
import json

redis_client = redis.Redis()

def get_section_cached(section_id):
    # Check cache
    cache_key = f"section:{section_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Query graph
    result = graph.query(
        "MATCH (s:Section {id: $id}) RETURN s",
        {"id": section_id}
    )

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result
```

**Impact:** 60% faster for repeated queries

---

### Quick Win 5: Add Paragraph Numbers (2 hours)

```python
# Quick script to add paragraph numbers to existing chunks
for chunk in all_chunks:
    # Extract paragraph number from text or position
    para_num = extract_paragraph_number(chunk.text)

    # Update chunk
    update_chunk(chunk.id, {"paragraphNumber": para_num})
```

**Impact:** Enable precise citations immediately

---

## 📚 Appendices

### Appendix A: Treatment Taxonomy Reference

```
Treatment Type: applies
├─ Weight: 1.0
├─ Precedent Effect: binding
├─ Synonyms: applied, applying, application
└─ When to Use: Court applies law to current facts

Treatment Type: follows
├─ Weight: 0.9
├─ Precedent Effect: binding
├─ Synonyms: followed, following
└─ When to Use: Court follows earlier precedent

Treatment Type: distinguishes
├─ Weight: 0.3
├─ Precedent Effect: non-binding
├─ Synonyms: distinguished, distinguishable
└─ When to Use: Court finds case distinguishable on facts

Treatment Type: overruled
├─ Weight: -1.0
├─ Precedent Effect: reversed
├─ Synonyms: overruling, reversed, set aside
└─ When to Use: Court overturns earlier decision

Treatment Type: criticizes
├─ Weight: -0.3
├─ Precedent Effect: weakened
├─ Synonyms: criticized, questioned, doubted
└─ When to Use: Court questions reasoning without overruling

Treatment Type: qualified
├─ Weight: 0.6
├─ Precedent Effect: limited
├─ Synonyms: qualified, limited, narrowed
└─ When to Use: Court narrows scope of earlier rule

Treatment Type: harmonized
├─ Weight: 0.8
├─ Precedent Effect: reconciled
├─ Synonyms: harmonized, reconciled
└─ When to Use: Court reconciles conflicting authorities
```

---

### Appendix B: URN Naming Conventions

```
Canonical URN Format:
urn:law:<country>:<type>:<identifier>

Examples:
├─ Statute: urn:law:bd:statute:cpc:1908
├─ Version: urn:law:bd:statute:cpc:1908:ver:2001v1
├─ Section: urn:law:bd:statute:cpc:1908:sec:17
│            urn:law:bd:statute:cpc:1908:sec:order6:r17
├─ Case: urn:law:bd:case:2007:hl:siddiquemia
│         urn:law:in:case:2008:sc:kbsaha
├─ Holding: urn:law:bd:case:2007:hl:siddiquemia:h1
├─ Chunk: urn:law:chunk:cpc:order6_r17:c1
└─ Source: urn:source:sconline

Rules:
1. Use lowercase for all identifiers
2. Use underscores for spaces in identifiers
3. Use colons as hierarchy separators
4. Keep identifiers short but meaningful
5. Maintain consistency across similar entities
```

---

### Appendix C: Trust Score Calculation Formula

```
Trust Score Components:

trust_score = w1 * source_authority +
              w2 * ocr_confidence +
              w3 * citation_frequency_norm +
              w4 * parser_confidence +
              w5 * recency_score

Default Weights:
├─ w1 (source_authority): 0.40
├─ w2 (ocr_confidence): 0.20
├─ w3 (citation_frequency): 0.15
├─ w4 (parser_confidence): 0.15
└─ w5 (recency): 0.10

source_authority = sourceType weight * verification factor

Source Type Weights:
├─ primary_statute: 1.00
├─ primary_judgment: 0.95
├─ official_reporter: 0.90
├─ commercial_reporter: 0.85
├─ summary: 0.70
├─ commentary: 0.60
└─ tertiary: 0.50

Verification Factor:
├─ verified: 1.0
├─ unverified: 0.9
└─ disputed: 0.5

citation_frequency_norm = min(1.0, citation_count / 20)

recency_score = 1.0 - (years_old / 50)
                bounded in [0.5, 1.0]

Example Calculation:
Given:
- sourceType: commercial_reporter (0.85)
- verificationStatus: verified (1.0)
- ocrConfidence: 0.95
- citationCount: 12 → norm = 12/20 = 0.60
- parserConfidence: 0.90
- yearsOld: 5 → recency = 1.0 - 5/50 = 0.90

trust_score = 0.40 * (0.85 * 1.0) +
              0.20 * 0.95 +
              0.15 * 0.60 +
              0.15 * 0.90 +
              0.10 * 0.90
            = 0.34 + 0.19 + 0.09 + 0.135 + 0.09
            = 0.845
```

---

### Appendix D: Embedding Model Comparison Matrix

```
Model Comparison (Based on Legal Corpus Evaluation):

| Model                    | Dims | P@5  | P@10 | MRR  | Latency | Cost      |
|--------------------------|------|------|------|------|---------|-----------|
| legal-bert-base          | 768  | 0.82 | 0.76 | 0.78 | 50ms    | Free      |
| legal-bert-finetuned     | 768  | 0.87 | 0.81 | 0.84 | 50ms    | Free*     |
| text-embedding-3-small   | 1536 | 0.79 | 0.73 | 0.76 | 30ms    | $0.02/1M  |
| text-embedding-3-large   | 3072 | 0.85 | 0.79 | 0.82 | 40ms    | $0.13/1M  |
| all-mpnet-base-v2        | 768  | 0.77 | 0.71 | 0.74 | 45ms    | Free      |
| longformer-base          | 768  | 0.80 | 0.74 | 0.77 | 120ms   | Free      |

* Requires one-time fine-tuning cost

Recommendation:
- Best Quality: legal-bert-finetuned or text-embedding-3-large
- Best Cost: legal-bert-finetuned (free after training)
- Best Speed: text-embedding-3-small

For production: Start with legal-bert-finetuned,
upgrade to text-embedding-3-large if quality gap exists
```

---

### Appendix E: Migration Scripts

#### Script 1: Add sourceType to existing Sources

```cypher
// Backup existing data first
CALL apoc.export.cypher.all("backup.cypher", {});

// Add sourceType property
MATCH (s:Source)
SET s.sourceType = CASE
    WHEN s.publisher CONTAINS 'Government' OR s.publisher CONTAINS 'Gazette'
        THEN 'primary_statute'
    WHEN s.publisher CONTAINS 'Supreme Court' OR s.publisher CONTAINS 'High Court'
        THEN 'primary_judgment'
    WHEN s.publisher IN ['SCC Online', 'DLR', 'BLD', 'AIR']
        THEN 'commercial_reporter'
    WHEN s.id CONTAINS 'upload' OR s.publisher CONTAINS 'summary'
        THEN 'summary'
    ELSE 'tertiary'
END;

// Add authority level
MATCH (s:Source)
SET s.authorityLevel = CASE s.sourceType
    WHEN 'primary_statute' THEN 5
    WHEN 'primary_judgment' THEN 5
    WHEN 'official_reporter' THEN 4
    WHEN 'commercial_reporter' THEN 3
    WHEN 'summary' THEN 2
    ELSE 1
END;

// Set default verification status
MATCH (s:Source)
WHERE s.verificationStatus IS NULL
SET s.verificationStatus = CASE
    WHEN s.sourceType IN ['primary_statute', 'primary_judgment']
        THEN 'verified'
    ELSE 'unverified'
END;
```

#### Script 2: Create derived OVERRULED_BY relationships

```cypher
// Find all CITES edges with treatment='overruled'
MATCH (citing_case:Case)-[:HAS_HOLDING]->(h:Holding)
      -[r:CITES {treatment:'overruled'}]->(cited_case:Case)

// Create OVERRULED_BY relationship
CREATE (cited_case)-[:OVERRULED_BY {
    date: citing_case.decisionDate,
    reason: r.context,
    cites_edge_id: id(r)
}]->(citing_case)

// Update cited case status
SET cited_case.status = 'Overruled',
    cited_case.overruled_by = citing_case.id,
    cited_case.overruled_date = citing_case.decisionDate;
```

#### Script 3: Recalculate trust scores

```cypher
// Recalculate trust scores for all chunks

MATCH (chunk:TextChunk)-[:INGESTED_FROM]->(source:Source)

// Calculate source authority
WITH chunk, source,
     CASE source.sourceType
         WHEN 'primary_statute' THEN 1.00
         WHEN 'primary_judgment' THEN 0.95
         WHEN 'official_reporter' THEN 0.90
         WHEN 'commercial_reporter' THEN 0.85
         WHEN 'summary' THEN 0.70
         WHEN 'commentary' THEN 0.60
         ELSE 0.50
     END AS source_weight,
     CASE source.verificationStatus
         WHEN 'verified' THEN 1.0
         WHEN 'unverified' THEN 0.9
         ELSE 0.5
     END AS verification_factor

// Calculate trust score
SET chunk.trust_score = (
    0.40 * source_weight * verification_factor +
    0.20 * COALESCE(chunk.ocrConfidence, 0.8) +
    0.15 * COALESCE(chunk.citationFrequencyNorm, 0.5) +
    0.15 * COALESCE(chunk.parserConfidence, 0.85) +
    0.10 * COALESCE(chunk.recencyScore, 0.8)
);
```

---

## 📊 Success Metrics Summary

### Target Metrics (Post-Implementation)

```
Overall Schema Score: 90/100 → 95+/100

Retrieval Quality:
├─ Precision@5: 0.75 → 0.90 (+20%)
├─ Precision@10: 0.70 → 0.85 (+21%)
├─ MRR: 0.72 → 0.87 (+21%)
└─ NDCG@10: 0.76 → 0.89 (+17%)

Classification Accuracy:
├─ Treatment F1: 0.70 → 0.85 (+21%)
├─ Intent Accuracy: N/A → 0.90 (new)
└─ Chunk Type F1: N/A → 0.80 (new)

Performance:
├─ P50 Latency: 1200ms → 500ms (-58%)
├─ P95 Latency: 2500ms → 1500ms (-40%)
├─ P99 Latency: 4000ms → 2500ms (-38%)
└─ Cache Hit Rate: 0% → 40% (+40%)

Data Quality:
├─ Chunks with Embeddings: 0.95 → 0.98 (+3%)
├─ CITES with Treatment: 0.70 → 0.95 (+36%)
├─ Trust Score Coverage: 0.26 → 1.00 (+74%)
└─ Source Type Classification: 0% → 100% (new)

User Experience:
├─ Answer Acceptance Rate: 0.75 → 0.85 (+13%)
├─ User Satisfaction: 3.8/5 → 4.3/5 (+13%)
├─ False Positive Rate: 0.15 → 0.08 (-47%)
└─ Citation Accuracy: 0.85 → 0.95 (+12%)
```

---

## 🎯 Conclusion

This roadmap provides a comprehensive plan to evolve your legal knowledge graph from **90/100 (A-) to 95+/100 (A+)**.

**Key Recommendations:**

1. **Start with Priority 1** - Foundation improvements that benefit everything else
2. **Measure continuously** - Track P@K, F1, latency daily
3. **Implement incrementally** - Each improvement is independently valuable
4. **User feedback loop** - Involve legal experts in validation
5. **Document learnings** - Update this roadmap as you progress

**Expected Timeline:** 17 weeks for complete implementation

**Expected Investment:**
- Engineering: 2-3 full-time engineers
- Legal expertise: Part-time for validation
- Infrastructure: Moderate (vector DB, caching, compute for embeddings)

**Expected ROI:**
- 40% improvement in citation accuracy
- 35% improvement in retrieval precision
- 60% improvement in query performance
- 25% improvement in user trust

**Ready to implement? Start with Quick Wins (Appendix E) for immediate impact!**

---

*Document Version: 1.0*
*Last Updated: November 2025*
*Maintained by: Legal AI Engineering Team*

---
