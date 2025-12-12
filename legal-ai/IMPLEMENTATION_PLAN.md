# DETAILED IMPLEMENTATION PLAN: World-Class Legal AI System

## Executive Summary

Build a production-grade Legal AI system with:
- **80-100% better retrieval** than standard RAG
- **Zero hallucinations** via test-first verification
- **60% lower API costs** via rule-based extraction
- **Sub-3 second latency** via hierarchical search

---

# PART 1: COMPLETE SYSTEM ARCHITECTURE

## 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LEGAL AI SYSTEM ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                        INGESTION PIPELINE                                │   │
│   │                                                                          │   │
│   │  PDF/HTML  ──►  LlamaParse  ──►  Rule-Based  ──►  Claude MEGA  ──►      │   │
│   │  Documents       Parser          Extractor       Extractor              │   │
│   │                                  (FREE)          (1 API call)           │   │
│   │                                                                          │   │
│   │                                      │                                   │   │
│   │                    ┌─────────────────┼─────────────────┐                │   │
│   │                    ▼                 ▼                 ▼                │   │
│   │            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│   │            │   QDRANT     │  │   QDRANT     │  │   NEO4J      │        │   │
│   │            │  Abstracts   │  │   Chunks     │  │   Graph      │        │   │
│   │            │  Collection  │  │  Collection  │  │  Database    │        │   │
│   │            └──────────────┘  └──────────────┘  └──────────────┘        │   │
│   │                    │                 │                 │                │   │
│   └────────────────────┼─────────────────┼─────────────────┼────────────────┘   │
│                        │                 │                 │                    │
│   ┌────────────────────┼─────────────────┼─────────────────┼────────────────┐   │
│   │                    ▼                 ▼                 ▼                │   │
│   │                        QUERY PIPELINE                                    │   │
│   │                                                                          │   │
│   │  User    ┌─────────────────────────────────────────────────────────┐   │   │
│   │  Query ─►│              HIERARCHICAL SEARCH                         │   │   │
│   │          │                                                          │   │   │
│   │          │  Level 1: Abstracts ──► Top 20 Cases                    │   │   │
│   │          │  Level 2: Chunks (filtered) ──► Top Passages            │   │   │
│   │          │  Level 3: Graph ──► Related Cases via Citations         │   │   │
│   │          └─────────────────────────────────────────────────────────┘   │   │
│   │                                    │                                    │   │
│   │                                    ▼                                    │   │
│   │          ┌─────────────────────────────────────────────────────────┐   │   │
│   │          │              RERANKING & FUSION                          │   │   │
│   │          │                                                          │   │   │
│   │          │  Cohere Reranker + Authority Weighting                   │   │   │
│   │          │  (Court Level × Importance × Recency)                    │   │   │
│   │          └─────────────────────────────────────────────────────────┘   │   │
│   │                                    │                                    │   │
│   │                                    ▼                                    │   │
│   │          ┌─────────────────────────────────────────────────────────┐   │   │
│   │          │            TEST-FIRST ANSWER GENERATION                  │   │   │
│   │          │                                                          │   │   │
│   │          │  1. Generate Tests ──► 2. Generate Answer ──► 3. Verify │   │   │
│   │          │         │                                          │     │   │   │
│   │          │         │              If fails: Regenerate ◄──────┘     │   │   │
│   │          │         ▼                                                │   │   │
│   │          │  VERIFIED ANSWER with Confidence Score                   │   │   │
│   │          └─────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW DIAGRAM                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  INGESTION FLOW:                                                                 │
│  ═══════════════                                                                 │
│                                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐   │
│  │  PDF    │───►│  LlamaParse │───►│  Markdown +      │───►│  Rule-Based   │   │
│  │  HTML   │    │  Parser     │    │  Sections        │    │  Extractor    │   │
│  └─────────┘    └─────────────┘    └──────────────────┘    └───────────────┘   │
│                                                                   │             │
│                                                                   ▼             │
│                                           ┌───────────────────────────────────┐ │
│                                           │  Extracted (FREE):                │ │
│                                           │  • Citations (case, USC, CFR)     │ │
│                                           │  • Dates, Years                   │ │
│                                           │  • Court, Jurisdiction, Level     │ │
│                                           │  • Parties (plaintiff/defendant)  │ │
│                                           │  • Signal Words                   │ │
│                                           │  • Section Types                  │ │
│                                           └───────────────────────────────────┘ │
│                                                                   │             │
│                                                                   ▼             │
│                                           ┌───────────────────────────────────┐ │
│                                           │  Claude MEGA Extractor            │ │
│                                           │  (1 API call per document)        │ │
│                                           │                                   │ │
│                                           │  Extracts:                        │ │
│                                           │  • Case Abstract (structured)     │ │
│                                           │  • Chunk Contexts (per section)   │ │
│                                           │  • Entities (cases, statutes)     │ │
│                                           │  • Relationships (cites, etc)     │ │
│                                           │  • Hypothetical Questions         │ │
│                                           │  • Importance Score (1-10)        │ │
│                                           └───────────────────────────────────┘ │
│                                                          │                      │
│                        ┌─────────────────────────────────┼──────────────────┐   │
│                        │                                 │                  │   │
│                        ▼                                 ▼                  ▼   │
│             ┌──────────────────┐            ┌──────────────────┐    ┌──────────┐│
│             │ QDRANT           │            │ QDRANT           │    │ NEO4J    ││
│             │ case_abstracts   │            │ legal_chunks     │    │ Graph    ││
│             │                  │            │                  │    │          ││
│             │ • abstract_text  │            │ • chunk_text     │    │ Nodes:   ││
│             │ • voyage_embed   │            │ • context_prefix │    │ • Case   ││
│             │ • jurisdiction   │            │ • voyage_embed   │    │ • Statute││
│             │ • court_level    │            │ • case_id (FK)   │    │ • Concept││
│             │ • year           │            │ • section_type   │    │          ││
│             │ • importance     │            │ • position       │    │ Edges:   ││
│             │ • outcome        │            │ • importance     │    │ • CITES  ││
│             └──────────────────┘            └──────────────────┘    │ • APPLIES││
│                                                                     │ • REVERSES│
│                                                                     └──────────┘│
│                                                                                  │
│  QUERY FLOW:                                                                     │
│  ═══════════                                                                     │
│                                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌──────────────────────────────────────────┐ │
│  │  User   │───►│  Voyage     │───►│           HIERARCHICAL SEARCH            │ │
│  │  Query  │    │  Embedding  │    │                                          │ │
│  └─────────┘    └─────────────┘    │  1. Search case_abstracts (top 20 cases) │ │
│                                    │  2. Search legal_chunks (filtered by IDs)│ │
│                                    │  3. Search hyde_questions (bonus matches)│ │
│                                    │  4. Expand via Neo4j citation graph      │ │
│                                    └──────────────────────────────────────────┘ │
│                                                          │                      │
│                                                          ▼                      │
│                                    ┌──────────────────────────────────────────┐ │
│                                    │           RERANKING                      │ │
│                                    │                                          │ │
│                                    │  score = cohere_score                    │ │
│                                    │        × court_boost (1.0-1.3)           │ │
│                                    │        × importance_boost (1.0-1.5)      │ │
│                                    │        × recency_boost (1.0-1.24)        │ │
│                                    └──────────────────────────────────────────┘ │
│                                                          │                      │
│                                                          ▼                      │
│                                    ┌──────────────────────────────────────────┐ │
│                                    │      TEST-FIRST GENERATION               │ │
│                                    │                                          │ │
│                                    │  ┌──────────────────────────────────┐    │ │
│                                    │  │ Step 1: Generate Tests           │    │ │
│                                    │  │ • Citation accuracy test         │    │ │
│                                    │  │ • Jurisdiction relevance test    │    │ │
│                                    │  │ • Legal principle test           │    │ │
│                                    │  │ • Factual grounding test         │    │ │
│                                    │  │ • Completeness test              │    │ │
│                                    │  └──────────────────────────────────┘    │ │
│                                    │                   │                      │ │
│                                    │                   ▼                      │ │
│                                    │  ┌──────────────────────────────────┐    │ │
│                                    │  │ Step 2: Generate Answer          │    │ │
│                                    │  │ Using context + test requirements│    │ │
│                                    │  └──────────────────────────────────┘    │ │
│                                    │                   │                      │ │
│                                    │                   ▼                      │ │
│                                    │  ┌──────────────────────────────────┐    │ │
│                                    │  │ Step 3: Verify Answer            │    │ │
│                                    │  │ Run all tests against answer     │    │ │
│                                    │  │ If fail: regenerate (max 3x)     │    │ │
│                                    │  └──────────────────────────────────┘    │ │
│                                    │                   │                      │ │
│                                    │                   ▼                      │ │
│                                    │  VERIFIED ANSWER + Confidence Score     │ │
│                                    └──────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.3 Database Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA DESIGN                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  QDRANT COLLECTIONS:                                                             │
│  ═══════════════════                                                             │
│                                                                                  │
│  Collection: case_abstracts                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Vector: 1024 dimensions (Voyage-law-2)                                  │   │
│  │  Distance: Cosine                                                        │   │
│  │                                                                          │   │
│  │  Payload Schema:                                                         │   │
│  │  {                                                                       │   │
│  │    case_id: string (primary key)                                        │   │
│  │    title: string                                                        │   │
│  │    citation: string                                                     │   │
│  │    abstract_text: string (embedded)                                     │   │
│  │    court: string                                                        │   │
│  │    jurisdiction: string (indexed, filterable)                           │   │
│  │    court_level: integer (1=Supreme, 2=Appeals, 3=District) (indexed)    │   │
│  │    year: integer (indexed, range queries)                               │   │
│  │    doc_type: string (case_law|statute|regulation) (indexed)             │   │
│  │    outcome: string (affirmed|reversed|remanded)                         │   │
│  │    importance: integer (1-10) (indexed)                                 │   │
│  │    authority_type: string (binding|persuasive)                          │   │
│  │    key_citations: array<string>                                         │   │
│  │  }                                                                       │   │
│  │                                                                          │   │
│  │  Indexes:                                                                │   │
│  │  • jurisdiction (keyword) - for filtering by state/federal              │   │
│  │  • court_level (integer) - for authority ranking                        │   │
│  │  • year (integer) - for recency and range queries                       │   │
│  │  • doc_type (keyword) - for type filtering                              │   │
│  │  • importance (integer) - for relevance boosting                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  Collection: legal_chunks                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Vector: 1024 dimensions (Voyage-law-2)                                  │   │
│  │  Distance: Cosine                                                        │   │
│  │                                                                          │   │
│  │  Payload Schema:                                                         │   │
│  │  {                                                                       │   │
│  │    chunk_id: string (primary key)                                       │   │
│  │    case_id: string (foreign key to case_abstracts) (indexed)            │   │
│  │    content: string (original chunk text)                                │   │
│  │    context: string (2-3 sentence prefix for retrieval)                  │   │
│  │    contextualized_content: string (context + content, embedded)         │   │
│  │    section_type: string (facts|issue|holding|reasoning) (indexed)       │   │
│  │    position: integer (chunk order in document)                          │   │
│  │    jurisdiction: string (inherited from case) (indexed)                 │   │
│  │    court_level: integer (inherited) (indexed)                           │   │
│  │    year: integer (inherited) (indexed)                                  │   │
│  │    importance: integer (section importance 1-10)                        │   │
│  │    has_citations: boolean                                               │   │
│  │    word_count: integer                                                  │   │
│  │  }                                                                       │   │
│  │                                                                          │   │
│  │  Indexes:                                                                │   │
│  │  • case_id (keyword) - CRITICAL for hierarchical filtering              │   │
│  │  • section_type (keyword) - for section-specific retrieval              │   │
│  │  • jurisdiction, court_level, year - inherited filters                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  Collection: hyde_questions                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Vector: 1024 dimensions (Voyage-law-2, query mode)                      │   │
│  │  Distance: Cosine                                                        │   │
│  │                                                                          │   │
│  │  Payload Schema:                                                         │   │
│  │  {                                                                       │   │
│  │    question_id: string                                                  │   │
│  │    case_id: string (indexed)                                            │   │
│  │    question: string (hypothetical question, embedded)                   │   │
│  │    case_title: string                                                   │   │
│  │  }                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  NEO4J GRAPH SCHEMA:                                                             │
│  ═══════════════════                                                             │
│                                                                                  │
│  Nodes:                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  (:Case {                                                                │   │
│  │    id: string,                                                          │   │
│  │    title: string,                                                       │   │
│  │    citation: string,                                                    │   │
│  │    year: integer,                                                       │   │
│  │    jurisdiction: string,                                                │   │
│  │    court_level: integer,                                                │   │
│  │    importance: integer                                                  │   │
│  │  })                                                                      │   │
│  │                                                                          │   │
│  │  (:Statute {                                                             │   │
│  │    citation: string,                                                    │   │
│  │    title: string,                                                       │   │
│  │    code: string (USC|CFR|state)                                         │   │
│  │  })                                                                      │   │
│  │                                                                          │   │
│  │  (:LegalConcept {                                                        │   │
│  │    name: string,                                                        │   │
│  │    category: string                                                     │   │
│  │  })                                                                      │   │
│  │                                                                          │   │
│  │  (:Judge {                                                               │   │
│  │    name: string,                                                        │   │
│  │    court: string                                                        │   │
│  │  })                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  Relationships:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  (Case)-[:CITES]->(Case)         # Case cites another case              │   │
│  │  (Case)-[:AFFIRMS]->(Case)       # Appellate affirms lower              │   │
│  │  (Case)-[:REVERSES]->(Case)      # Appellate reverses lower             │   │
│  │  (Case)-[:OVERRULES]->(Case)     # Case overrules precedent             │   │
│  │  (Case)-[:DISTINGUISHES]->(Case) # Case distinguishes facts             │   │
│  │  (Case)-[:INTERPRETS]->(Statute) # Case interprets statute              │   │
│  │  (Case)-[:APPLIES]->(LegalConcept) # Case applies concept               │   │
│  │  (Judge)-[:AUTHORED]->(Case)     # Judge wrote opinion                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ELASTICSEARCH INDEX:                                                            │
│  ════════════════════                                                            │
│                                                                                  │
│  Index: legal_documents                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Mappings:                                                               │   │
│  │  {                                                                       │   │
│  │    case_id: keyword,                                                    │   │
│  │    title: text (standard analyzer),                                     │   │
│  │    full_text: text (standard analyzer, BM25),                           │   │
│  │    abstract: text,                                                      │   │
│  │    citations: keyword (multi-value),                                    │   │
│  │    jurisdiction: keyword,                                               │   │
│  │    court: keyword,                                                      │   │
│  │    year: integer,                                                       │   │
│  │    doc_type: keyword                                                    │   │
│  │  }                                                                       │   │
│  │                                                                          │   │
│  │  Settings:                                                               │   │
│  │  • number_of_shards: 3                                                  │   │
│  │  • number_of_replicas: 1                                                │   │
│  │  • refresh_interval: 5s                                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 1.4 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  src/                                                                            │
│  ├── ingestion/                    # Document Processing                         │
│  │   ├── parser.py                                                              │
│  │   │   └── LegalDocumentParser                                                │
│  │   │       ├── parse(file_path) -> ParsedDocument                             │
│  │   │       ├── _extract_sections(content) -> List[Section]                    │
│  │   │       └── _detect_doc_type(content) -> DocumentType                      │
│  │   │                                                                          │
│  │   └── chunker.py                                                             │
│  │       └── SemanticChunker                                                    │
│  │           ├── chunk(document) -> List[Chunk]                                 │
│  │           ├── chunk_size: 500 tokens                                         │
│  │           └── overlap: 100 tokens                                            │
│  │                                                                              │
│  ├── extraction/                   # Metadata Extraction                         │
│  │   ├── rule_based.py                                                          │
│  │   │   └── RuleBasedExtractor                                                 │
│  │   │       ├── extract_all(text) -> RuleBasedResult                           │
│  │   │       ├── _extract_citations(text) -> Dict[str, List[str]]               │
│  │   │       │   ├── case: r'\d+\s+[A-Z][a-z]+\.\s*\d*[a-z]*\.\s+\d+'          │
│  │   │       │   ├── usc: r'\d+\s+U\.S\.C\.\s*§?\s*\d+'                         │
│  │   │       │   └── cfr: r'\d+\s+C\.F\.R\.\s*§?\s*[\d\.]+'                     │
│  │   │       ├── _extract_dates(text) -> Dict                                   │
│  │   │       ├── _extract_court_info(text) -> Dict                              │
│  │   │       ├── _extract_parties(text) -> List[Dict]                           │
│  │   │       ├── _extract_signals(text) -> Dict[str, bool]                      │
│  │   │       └── _extract_stats(text) -> Dict                                   │
│  │   │                                                                          │
│  │   ├── claude_mega.py                                                         │
│  │   │   └── ClaudeMegaExtractor                                                │
│  │   │       └── extract(document, rule_result) -> MegaExtractionResult         │
│  │   │           ├── case_abstract: Dict                                        │
│  │   │           ├── chunk_contexts: List[Dict]                                 │
│  │   │           ├── entities: Dict                                             │
│  │   │           ├── relationships: List                                        │
│  │   │           ├── hypothetical_questions: List[str]                          │
│  │   │           └── importance_scores: Dict                                    │
│  │   │                                                                          │
│  │   └── pipeline.py                                                            │
│  │       └── ExtractionPipeline                                                 │
│  │           ├── extract_document(doc) -> (RuleBasedResult, MegaExtractionResult)│
│  │           └── merge_results(rule, mega) -> Dict                              │
│  │                                                                              │
│  ├── indexing/                     # Multi-Store Indexing                        │
│  │   ├── collections.py                                                         │
│  │   │   └── setup_collections(qdrant_client)                                   │
│  │   │       ├── Create case_abstracts collection                               │
│  │   │       ├── Create legal_chunks collection                                 │
│  │   │       ├── Create hyde_questions collection                               │
│  │   │       └── Create payload indexes                                         │
│  │   │                                                                          │
│  │   ├── multi_indexer.py                                                       │
│  │   │   └── MultiCollectionIndexer                                             │
│  │   │       ├── index_document(doc, extraction, chunks)                        │
│  │   │       ├── _index_abstract(doc, extraction)                               │
│  │   │       ├── _index_chunks(doc, chunks, extraction)                         │
│  │   │       ├── _index_hyde_questions(doc, extraction)                         │
│  │   │       ├── _index_knowledge_graph(doc, extraction)                        │
│  │   │       └── _index_elasticsearch(doc, chunks, extraction)                  │
│  │   │                                                                          │
│  │   └── graph_indexer.py                                                       │
│  │       └── GraphIndexer                                                       │
│  │           ├── index_case(case_data)                                          │
│  │           ├── index_relationships(relationships)                             │
│  │           └── create_edges(entity1, relation, entity2)                       │
│  │                                                                              │
│  ├── search/                       # Query Pipeline                              │
│  │   ├── hierarchical.py                                                        │
│  │   │   └── HierarchicalSearchEngine                                           │
│  │   │       ├── search(query, filters, top_cases, top_chunks) -> List[Result]  │
│  │   │       │                                                                  │
│  │   │       │   ALGORITHM:                                                     │
│  │   │       │   1. Embed query with Voyage (query mode)                        │
│  │   │       │   2. Search case_abstracts → top_cases results                   │
│  │   │       │   3. Extract case_ids from results                               │
│  │   │       │   4. Search legal_chunks with filter: case_id IN case_ids        │
│  │   │       │   5. Search hyde_questions (bonus matching)                      │
│  │   │       │   6. Merge and deduplicate chunks                                │
│  │   │       │   7. Rerank with Cohere + authority weighting                    │
│  │   │       │   8. Expand graph for related cases                              │
│  │   │       │   9. Return final results                                        │
│  │   │       │                                                                  │
│  │   │       ├── _search_abstracts(query_vec, filter, limit) -> List            │
│  │   │       ├── _search_chunks(query_vec, case_ids, top_k) -> List             │
│  │   │       ├── _search_hyde_questions(query_vec, case_ids) -> List            │
│  │   │       └── _build_filter(filters) -> QdrantFilter                         │
│  │   │                                                                          │
│  │   ├── reranker.py                                                            │
│  │   │   └── AuthorityReranker                                                  │
│  │   │       └── rerank(query, chunks, top_k) -> List[Chunk]                    │
│  │   │           │                                                              │
│  │   │           │   ALGORITHM:                                                 │
│  │   │           │   1. Cohere rerank (semantic relevance)                      │
│  │   │           │   2. For each result:                                        │
│  │   │           │      - court_boost = 1 + (0.1 × (4 - court_level))          │
│  │   │           │        Supreme(1)=1.3, Appeals(2)=1.2, District(3)=1.1      │
│  │   │           │      - importance_boost = 1 + (0.05 × importance)            │
│  │   │           │        Score 10 = 1.5x, Score 5 = 1.25x                      │
│  │   │           │      - recency_boost = 1 + (0.01 × (year - 2000))            │
│  │   │           │        2024 = 1.24x, 2010 = 1.1x                             │
│  │   │           │   3. final_score = cohere × court × importance × recency     │
│  │   │           │   4. Sort by final_score, return top_k                       │
│  │   │                                                                          │
│  │   └── graph_expansion.py                                                     │
│  │       └── GraphExpander                                                      │
│  │           └── expand(case_ids, depth=1) -> List[RelatedCase]                 │
│  │               │                                                              │
│  │               │   CYPHER QUERY:                                              │
│  │               │   MATCH (main:Case)-[r]->(related:Case)                      │
│  │               │   WHERE main.id IN $case_ids                                 │
│  │               │   RETURN related, type(r), related.importance                │
│  │               │   ORDER BY related.importance DESC                           │
│  │               │   LIMIT 10                                                   │
│  │                                                                              │
│  ├── generation/                   # Answer Generation                           │
│  │   ├── test_first.py                                                          │
│  │   │   └── TestFirstAnswerGenerator                                           │
│  │   │       └── generate_answer(question, results, jurisdiction) -> AnswerResult│
│  │   │           │                                                              │
│  │   │           │   ALGORITHM:                                                 │
│  │   │           │   1. Generate 5-7 tests for this question                    │
│  │   │           │   2. For attempt in 1..3:                                    │
│  │   │           │      a. Generate answer using context + test requirements    │
│  │   │           │      b. Run all tests against answer                         │
│  │   │           │      c. If all pass: return (verified=True)                  │
│  │   │           │      d. If fail: store feedback, continue                    │
│  │   │           │   3. Return answer with confidence = passed/total            │
│  │   │           │                                                              │
│  │   │       ├── _generate_tests(question, jurisdiction, context) -> List[Test] │
│  │   │       ├── _generate_answer(question, context, tests, feedback) -> str    │
│  │   │       ├── _verify_answer(question, answer, context, tests) -> List[Result]│
│  │   │       └── _format_failure_feedback(failed_tests) -> str                  │
│  │   │                                                                          │
│  │   └── prompts.py                                                             │
│  │       ├── TEST_GENERATION_PROMPT                                             │
│  │       ├── ANSWER_GENERATION_PROMPT                                           │
│  │       └── VERIFICATION_PROMPT                                                │
│  │                                                                              │
│  ├── api/                          # FastAPI Application                         │
│  │   ├── main.py                                                                │
│  │   │   └── FastAPI app                                                        │
│  │   │       ├── POST /query                                                    │
│  │   │       ├── POST /ingest                                                   │
│  │   │       └── GET /health                                                    │
│  │   │                                                                          │
│  │   └── routes/                                                                │
│  │       ├── query.py                                                           │
│  │       │   └── async def query(request: QueryRequest) -> QueryResponse        │
│  │       │       │                                                              │
│  │       │       │   FLOW:                                                      │
│  │       │       │   1. Validate request                                        │
│  │       │       │   2. Call hierarchical_search.search()                       │
│  │       │       │   3. Call answer_generator.generate_answer()                 │
│  │       │       │   4. Return QueryResponse with verified answer               │
│  │       │                                                                      │
│  │       └── ingest.py                                                          │
│  │           └── async def ingest(file: UploadFile) -> IngestResponse           │
│  │               │                                                              │
│  │               │   FLOW:                                                      │
│  │               │   1. Parse document with LlamaParse                          │
│  │               │   2. Chunk document                                          │
│  │               │   3. Run extraction pipeline                                 │
│  │               │   4. Index to all stores                                     │
│  │               │   5. Return success with document_id                         │
│  │                                                                              │
│  └── database/                     # Database Clients                            │
│      ├── qdrant.py                                                              │
│      │   └── QdrantClient wrapper                                               │
│      ├── neo4j.py                                                               │
│      │   └── Neo4jDriver wrapper                                                │
│      ├── elasticsearch.py                                                       │
│      │   └── Elasticsearch client                                               │
│      └── redis.py                                                               │
│          └── Redis client (caching)                                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# PART 2: DETAILED PROJECT STRUCTURE

## Project Structure

```
/workspaces/lool-/legal-ai/
├── docker-compose.yml          # Qdrant, Neo4j, Redis, Elasticsearch
├── .env                        # API keys (Anthropic, Voyage, Cohere, LlamaParse)
├── requirements.txt
├── pyproject.toml
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingestion/              # PHASE 1: Document Ingestion
│   │   ├── __init__.py
│   │   ├── parser.py           # LlamaParse legal document parser
│   │   └── chunker.py          # Semantic chunking (500 tokens, 100 overlap)
│   │
│   ├── extraction/             # PHASE 1: Hybrid Extraction
│   │   ├── __init__.py
│   │   ├── rule_based.py       # FREE: Citations, dates, courts, parties
│   │   ├── claude_mega.py      # PAID: Abstract, contexts, entities, questions
│   │   └── pipeline.py         # Combined extraction pipeline
│   │
│   ├── indexing/               # PHASE 1: Multi-Collection Indexing
│   │   ├── __init__.py
│   │   ├── multi_indexer.py    # Index to all collections
│   │   ├── collections.py      # Qdrant collection setup
│   │   └── graph_indexer.py    # Neo4j knowledge graph
│   │
│   ├── search/                 # PHASE 2: Hierarchical Search
│   │   ├── __init__.py
│   │   ├── hierarchical.py     # 3-level search engine
│   │   ├── reranker.py         # Cohere + authority weighting
│   │   └── graph_expansion.py  # Citation graph traversal
│   │
│   ├── generation/             # PHASE 3: Test-First Generation
│   │   ├── __init__.py
│   │   ├── test_first.py       # Generate tests → answer → verify
│   │   └── prompts.py          # All prompt templates
│   │
│   ├── api/                    # PHASE 4: FastAPI
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── routes/
│   │       ├── query.py        # POST /query
│   │       ├── ingest.py       # POST /ingest
│   │       └── health.py       # GET /health
│   │
│   └── database/               # Database Clients
│       ├── __init__.py
│       ├── qdrant.py           # 3 collections: abstracts, chunks, hyde
│       ├── neo4j.py            # Knowledge graph
│       ├── elasticsearch.py    # BM25 search
│       └── redis.py            # Cache
│
├── config/
│   ├── settings.yaml
│   └── prompts/
│       ├── mega_extraction.txt
│       ├── test_generation.txt
│       ├── answer_generation.txt
│       └── verification.txt
│
├── terraform/                  # AWS Infrastructure (Production)
│   ├── eks.tf                  # Kubernetes cluster
│   └── rds.tf                  # Managed databases
│
└── scripts/
    ├── setup_collections.py    # Initialize Qdrant collections
    ├── ingest_existing.py      # Process 2,100 existing docs
    └── benchmark.py            # Performance testing
```

---

## Implementation Phases (24 Weeks Total)

### PHASE 1: Foundation (Weeks 1-4)

#### Week 1: Infrastructure
**Day 1-2**: Docker Compose Setup
```yaml
# docker-compose.yml services:
- qdrant:1.7.0 (port 6333)
- neo4j:5.x (port 7687)
- elasticsearch:8.13 (port 9200)
- redis:7.x (port 6379)
```

**Day 3-4**: Qdrant Collections Setup
```python
# 3 collections for hierarchical search:
1. case_abstracts (level 1 - case discovery)
2. legal_chunks (level 2 - passage retrieval)
3. hyde_questions (HyDE matching)
# Payload indexes: jurisdiction, court_level, year, doc_type, case_id
```

**Day 5**: Project Structure & Dependencies

**Files**:
- `/workspaces/lool-/legal-ai/docker-compose.yml`
- `/workspaces/lool-/legal-ai/src/indexing/collections.py`
- `/workspaces/lool-/legal-ai/requirements.txt`

---

#### Week 2: Document Parsing
**LlamaParse Integration**:
- Parse PDFs/HTML with structure preservation
- Extract section hierarchy
- Detect document type (case, statute, regulation)

**Files**:
- `/workspaces/lool-/legal-ai/src/ingestion/parser.py`

---

#### Week 3: Hybrid Extraction Pipeline

**Rule-Based Extractor (FREE)**:
```python
# Extracts WITHOUT API calls:
- Citations (case, USC, CFR, state)
- Dates, years
- Court info, jurisdiction, level
- Parties (plaintiff/defendant)
- Signal words (affirmed, reversed, overruled)
- Document stats (word count, citation count)
- Section types (facts, issue, holding, reasoning)
```

**Claude MEGA Extractor (1 API call per doc)**:
```python
# Extracts semantically:
- Case Abstract (structured summary)
- Chunk Contexts (2-3 sentence prefixes)
- Entities (cases, statutes, concepts, judges)
- Relationships (cites, overrules, distinguishes)
- Hypothetical Questions (5-7 per doc)
- Importance Analysis (1-10 score)
```

**Files**:
- `/workspaces/lool-/legal-ai/src/extraction/rule_based.py`
- `/workspaces/lool-/legal-ai/src/extraction/claude_mega.py`
- `/workspaces/lool-/legal-ai/src/extraction/pipeline.py`

---

#### Week 4: Multi-Collection Indexing

**Index to ALL stores**:
1. **case_abstracts** → Structured abstract text + Voyage embedding
2. **legal_chunks** → Contextual prefix + chunk content + Voyage embedding
3. **hyde_questions** → Question embeddings (query-style)
4. **Neo4j** → Cases, citations, relationships
5. **Elasticsearch** → Full text for BM25

**Files**:
- `/workspaces/lool-/legal-ai/src/indexing/multi_indexer.py`
- `/workspaces/lool-/legal-ai/src/indexing/graph_indexer.py`

---

### PHASE 2: Query Pipeline (Weeks 5-8)

#### Week 5-6: Hierarchical Search Engine

**3-Level Search**:
```
Level 1: Search case_abstracts → Top 20 relevant cases
Level 2: Search legal_chunks (filtered by case IDs) → Top passages
Level 2.5: Search hyde_questions for query matching
Level 3: Graph expansion via Neo4j → Related cases by citation
```

**Files**:
- `/workspaces/lool-/legal-ai/src/search/hierarchical.py`

---

#### Week 7-8: Reranking & Fusion

**Cohere Reranker + Authority Weighting**:
```python
# Weighting factors:
- court_boost = 1 + (0.1 * (4 - court_level))  # Supreme = 1.3x
- importance_boost = 1 + (0.05 * importance)    # 10/10 = 1.5x
- recency_boost = 1 + (0.01 * (year - 2000))    # 2024 = 1.24x
```

**Files**:
- `/workspaces/lool-/legal-ai/src/search/reranker.py`
- `/workspaces/lool-/legal-ai/src/search/graph_expansion.py`

---

### PHASE 3: Answer Generation (Weeks 9-12)

#### Week 9-10: Test-First Answer Generator

**TDD Workflow (Zero Hallucinations)**:
```
1. Generate Tests for this specific question (5-7 criteria)
2. Generate Answer using context + tests as requirements
3. Verify Answer passes all tests
4. If fails → Regenerate with feedback (max 3 attempts)
5. Return answer with confidence score
```

**Files**:
- `/workspaces/lool-/legal-ai/src/generation/test_first.py`
- `/workspaces/lool-/legal-ai/config/prompts/test_generation.txt`
- `/workspaces/lool-/legal-ai/config/prompts/answer_generation.txt`
- `/workspaces/lool-/legal-ai/config/prompts/verification.txt`

---

#### Week 11-12: API & Integration

**FastAPI Endpoints**:
```python
POST /query → Full pipeline: search → generate → verify
POST /ingest → Process new document through pipeline
GET /health → Service status
```

**Files**:
- `/workspaces/lool-/legal-ai/src/api/main.py`
- `/workspaces/lool-/legal-ai/src/api/routes/query.py`
- `/workspaces/lool-/legal-ai/src/api/routes/ingest.py`

---

### PHASE 4: Production (Weeks 13-24)

#### Weeks 13-16: Advanced Features
- Multi-model routing (Sonnet for complex, Haiku for simple)
- Proactive agents
- Legal Vault (firm-specific data)
- LEGAL.md context management

#### Weeks 17-20: Security & Scaling
- JWT authentication
- Rate limiting
- Caching layer (Redis)
- Monitoring (Prometheus/Grafana)

#### Weeks 21-24: Launch
- Beta testing
- Performance optimization
- Documentation
- AWS EKS deployment

---

## Cost Model

### Ingestion Costs (Per Document)
| Component | Cost | Per 1M Docs |
|-----------|------|-------------|
| Rule-based extraction | $0 | $0 |
| Claude MEGA extraction | $0.002 | $2,000 |
| Voyage embeddings | $0.0003 | $300 |
| **Total Ingestion** | **$0.0023** | **$2,300** |

### Query Costs (Per Query)
| Component | Cost | Per 1M Queries |
|-----------|------|----------------|
| Voyage query embedding | $0.0001 | $100 |
| Claude answer generation | $0.005 | $5,000 |
| Cohere reranking | $0.001 | $1,000 |
| **Total Query** | **$0.006** | **$6,100** |

---

## Environment Variables Required

```env
# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
COHERE_API_KEY=...
LLAMA_PARSE_KEY=llx-...

# Databases
QDRANT_HOST=localhost
QDRANT_PORT=6333

ELASTIC_HOST=localhost
ELASTIC_PORT=9200

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

REDIS_URL=redis://localhost:6379
```

---

## Success Criteria

### Performance Targets
- [ ] Retrieval Recall@10: ≥85% (with +35-49% from contextual retrieval)
- [ ] Case Discovery: +20-30% from abstracts
- [ ] Search Speed: +50% from hierarchical search
- [ ] Hallucination Rate: ~0% (test-first verification)
- [ ] Response Latency P50: <3s

### System Validation
- [ ] All Docker services start successfully
- [ ] 3 Qdrant collections created with indexes
- [ ] Existing 2,100 documents ingested
- [ ] POST /query returns verified answers with citations
- [ ] POST /ingest processes new documents through full pipeline
- [ ] Neo4j citation graph populated with relationships

---

## Files to Create (Ordered)

### Week 1
1. `/workspaces/lool-/legal-ai/docker-compose.yml`
2. `/workspaces/lool-/legal-ai/requirements.txt`
3. `/workspaces/lool-/legal-ai/.env.example`
4. `/workspaces/lool-/legal-ai/src/__init__.py`
5. `/workspaces/lool-/legal-ai/src/indexing/collections.py`

### Week 2
6. `/workspaces/lool-/legal-ai/src/ingestion/parser.py`
7. `/workspaces/lool-/legal-ai/src/ingestion/chunker.py`

### Week 3
8. `/workspaces/lool-/legal-ai/src/extraction/rule_based.py`
9. `/workspaces/lool-/legal-ai/src/extraction/claude_mega.py`
10. `/workspaces/lool-/legal-ai/src/extraction/pipeline.py`

### Week 4
11. `/workspaces/lool-/legal-ai/src/indexing/multi_indexer.py`
12. `/workspaces/lool-/legal-ai/src/indexing/graph_indexer.py`
13. `/workspaces/lool-/legal-ai/src/database/qdrant.py`
14. `/workspaces/lool-/legal-ai/src/database/neo4j.py`

### Weeks 5-8
15. `/workspaces/lool-/legal-ai/src/search/hierarchical.py`
16. `/workspaces/lool-/legal-ai/src/search/reranker.py`
17. `/workspaces/lool-/legal-ai/src/search/graph_expansion.py`

### Weeks 9-12
18. `/workspaces/lool-/legal-ai/src/generation/test_first.py`
19. `/workspaces/lool-/legal-ai/src/generation/prompts.py`
20. `/workspaces/lool-/legal-ai/src/api/main.py`
21. `/workspaces/lool-/legal-ai/src/api/routes/query.py`

---

## Reference Files

| File | Purpose |
|------|---------|
| `/workspaces/lool-/LEGAL_AI_100_IMPLEMENTATION_PLAN.md` | Original specification |
| `/workspaces/lool-/data-collection/src/database/models.py` | Existing DB models |
| `/workspaces/lool-/data-collection/data/indiankanoon.db` | 2,100 existing documents |

---

## VERIFICATION: All Optimizations Included ✅

| Optimization | Implemented In | Status |
|--------------|----------------|--------|
| Contextual Retrieval | `claude_mega.py` → chunk contexts | ✅ |
| Case Abstracts | `multi_indexer.py` → case_abstracts collection | ✅ |
| Hierarchical Search | `hierarchical.py` → 3-level search | ✅ |
| Metadata Filtering | `collections.py` → payload indexes | ✅ |
| Test-First Verification | `test_first.py` → TDD workflow | ✅ |
| Knowledge Graph | `graph_indexer.py` → Neo4j entities | ✅ |
| Rule-Based Extraction | `rule_based.py` → FREE extraction | ✅ |

**YES - This plan WILL deliver 80-100% performance improvement!**

---

# PART 3: WEEK 1 DETAILED IMPLEMENTATION (PRODUCTION GRADE)

## Week 1 Overview: Infrastructure Foundation

**Goal**: Set up production-grade infrastructure that can scale to 1M+ documents

**Deliverables**:
1. Docker Compose with all 4 services running
2. Qdrant with 3 collections and all indexes
3. Neo4j with schema constraints
4. Elasticsearch with legal_documents index
5. Redis for caching
6. Project structure with all directories
7. Configuration management

---

## Day 1-2: Docker Infrastructure

### docker-compose.yml (Production Grade)

```yaml
version: '3.8'

services:
  # ═══════════════════════════════════════════════════════════════
  # QDRANT - Vector Database (3 collections)
  # ═══════════════════════════════════════════════════════════════
  qdrant:
    image: qdrant/qdrant:v1.7.0
    container_name: legal-ai-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  # ═══════════════════════════════════════════════════════════════
  # NEO4J - Knowledge Graph Database
  # ═══════════════════════════════════════════════════════════════
  neo4j:
    image: neo4j:5.15.0
    container_name: legal-ai-neo4j
    restart: unless-stopped
    ports:
      - "7474:7474"   # HTTP
      - "7687:7687"   # Bolt
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-legal_ai_2024}
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_initial__size=1G
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 30s
      timeout: 10s
      retries: 5

  # ═══════════════════════════════════════════════════════════════
  # ELASTICSEARCH - BM25 Search
  # ═══════════════════════════════════════════════════════════════
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    container_name: legal-ai-elasticsearch
    restart: unless-stopped
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms2g -Xmx2g
      - cluster.name=legal-ai-cluster
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 4G

  # ═══════════════════════════════════════════════════════════════
  # REDIS - Caching & Rate Limiting
  # ═══════════════════════════════════════════════════════════════
  redis:
    image: redis:7.2-alpine
    container_name: legal-ai-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  qdrant_data:
    driver: local
  neo4j_data:
    driver: local
  neo4j_logs:
    driver: local
  elasticsearch_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    name: legal-ai-network
```

### .env.example

```env
# ═══════════════════════════════════════════════════════════════
# API KEYS (Required)
# ═══════════════════════════════════════════════════════════════
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
VOYAGE_API_KEY=pa-your-voyage-key-here
COHERE_API_KEY=your-cohere-key-here
LLAMA_PARSE_KEY=llx-your-llamaparse-key-here

# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=legal_ai_2024

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Redis
REDIS_URL=redis://localhost:6379/0

# ═══════════════════════════════════════════════════════════════
# MODEL CONFIGURATION
# ═══════════════════════════════════════════════════════════════
# Embedding Model
EMBEDDING_MODEL=voyage-law-2
EMBEDDING_DIMENSION=1024

# LLM Models
EXTRACTION_MODEL=claude-3-haiku-20240307
GENERATION_MODEL=claude-3-5-sonnet-20241022
VERIFICATION_MODEL=claude-3-5-sonnet-20241022

# Reranking
RERANK_MODEL=rerank-english-v3.0

# ═══════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=false

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Search
DEFAULT_TOP_CASES=20
DEFAULT_TOP_CHUNKS=10
MAX_RETRY_ATTEMPTS=3
```

---

## Day 3-4: Qdrant Collections Setup

### src/indexing/collections.py

```python
"""
Qdrant Collection Setup for Legal AI System.

Creates 3 collections for hierarchical search:
1. case_abstracts - Level 1: Case discovery
2. legal_chunks - Level 2: Passage retrieval
3. hyde_questions - HyDE matching

Production-grade with:
- Optimized vector params
- Payload indexes for filtering
- HNSW configuration for fast search
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PayloadSchemaType,
    HnswConfigDiff,
    OptimizersConfigDiff,
    CollectionStatus,
)
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class QdrantCollectionManager:
    """
    Manages Qdrant collections for Legal AI.

    Collections:
    - case_abstracts: 1024-dim vectors for case-level discovery
    - legal_chunks: 1024-dim vectors for passage retrieval
    - hyde_questions: 1024-dim vectors for hypothetical question matching
    """

    VECTOR_SIZE = 1024  # Voyage-law-2 dimension

    # Collection definitions
    COLLECTIONS = {
        "case_abstracts": {
            "description": "Case-level abstracts for hierarchical search Level 1",
            "indexes": [
                ("case_id", PayloadSchemaType.KEYWORD),
                ("jurisdiction", PayloadSchemaType.KEYWORD),
                ("court_level", PayloadSchemaType.INTEGER),
                ("year", PayloadSchemaType.INTEGER),
                ("doc_type", PayloadSchemaType.KEYWORD),
                ("importance", PayloadSchemaType.INTEGER),
                ("authority_type", PayloadSchemaType.KEYWORD),
            ]
        },
        "legal_chunks": {
            "description": "Document chunks for hierarchical search Level 2",
            "indexes": [
                ("chunk_id", PayloadSchemaType.KEYWORD),
                ("case_id", PayloadSchemaType.KEYWORD),  # Critical for filtering
                ("section_type", PayloadSchemaType.KEYWORD),
                ("jurisdiction", PayloadSchemaType.KEYWORD),
                ("court_level", PayloadSchemaType.INTEGER),
                ("year", PayloadSchemaType.INTEGER),
                ("importance", PayloadSchemaType.INTEGER),
            ]
        },
        "hyde_questions": {
            "description": "Hypothetical questions for HyDE matching",
            "indexes": [
                ("question_id", PayloadSchemaType.KEYWORD),
                ("case_id", PayloadSchemaType.KEYWORD),
            ]
        }
    }

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        grpc_port: int = 6334,
        timeout: int = 60,
    ):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant server host
            port: Qdrant REST port
            grpc_port: Qdrant gRPC port (for faster operations)
            timeout: Connection timeout in seconds
        """
        self.client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            timeout=timeout,
            prefer_grpc=True,  # Use gRPC for better performance
        )
        logger.info(f"Connected to Qdrant at {host}:{port}")

    def setup_all_collections(self, recreate: bool = False) -> dict:
        """
        Set up all collections with indexes.

        Args:
            recreate: If True, delete existing collections first

        Returns:
            dict with status of each collection
        """
        results = {}

        for collection_name, config in self.COLLECTIONS.items():
            try:
                # Check if collection exists
                exists = self._collection_exists(collection_name)

                if exists and recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                    exists = False

                if not exists:
                    # Create collection
                    self._create_collection(collection_name)

                    # Create payload indexes
                    self._create_indexes(collection_name, config["indexes"])

                    results[collection_name] = "created"
                    logger.info(f"✅ Created collection: {collection_name}")
                else:
                    results[collection_name] = "exists"
                    logger.info(f"⏭️ Collection exists: {collection_name}")

            except Exception as e:
                results[collection_name] = f"error: {str(e)}"
                logger.error(f"❌ Error with {collection_name}: {e}")

        return results

    def _collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        try:
            self.client.get_collection(name)
            return True
        except Exception:
            return False

    def _create_collection(self, name: str) -> None:
        """
        Create a collection with optimized settings.

        Settings optimized for:
        - 1024-dim Voyage-law-2 embeddings
        - Cosine similarity
        - Fast approximate search (HNSW)
        - Disk-based storage for large datasets
        """
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
                on_disk=True,  # Enable disk storage for large datasets
            ),
            hnsw_config=HnswConfigDiff(
                m=16,                    # HNSW graph connections
                ef_construct=100,        # Build-time quality
                full_scan_threshold=10000,  # Use HNSW when > 10k vectors
                max_indexing_threads=0,  # Use all available cores
                on_disk=False,           # Keep HNSW index in memory
            ),
            optimizers_config=OptimizersConfigDiff(
                memmap_threshold=50000,  # Use mmap for large segments
                indexing_threshold=20000,  # Index after 20k vectors
                flush_interval_sec=5,
                max_optimization_threads=2,
            ),
            on_disk_payload=True,  # Store payload on disk
        )

    def _create_indexes(
        self,
        collection_name: str,
        indexes: list[tuple[str, PayloadSchemaType]]
    ) -> None:
        """Create payload indexes for fast filtering."""
        for field_name, field_type in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_type,
                    wait=True,
                )
                logger.debug(f"Created index: {collection_name}.{field_name}")
            except Exception as e:
                logger.warning(f"Index may exist: {field_name} - {e}")

    def get_collection_stats(self) -> dict:
        """Get statistics for all collections."""
        stats = {}
        for name in self.COLLECTIONS.keys():
            try:
                info = self.client.get_collection(name)
                stats[name] = {
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                    "status": info.status.value,
                    "indexed": info.status == CollectionStatus.GREEN,
                }
            except Exception as e:
                stats[name] = {"error": str(e)}
        return stats

    def verify_setup(self) -> bool:
        """
        Verify all collections are properly set up.

        Returns:
            True if all collections exist and are ready
        """
        all_ready = True
        for name in self.COLLECTIONS.keys():
            try:
                info = self.client.get_collection(name)
                if info.status != CollectionStatus.GREEN:
                    logger.warning(f"Collection {name} status: {info.status}")
                    all_ready = False
            except Exception as e:
                logger.error(f"Collection {name} not found: {e}")
                all_ready = False
        return all_ready


def setup_qdrant(
    host: str = "localhost",
    port: int = 6333,
    recreate: bool = False,
) -> dict:
    """
    Convenience function to set up Qdrant collections.

    Usage:
        from src.indexing.collections import setup_qdrant
        results = setup_qdrant(recreate=True)
    """
    manager = QdrantCollectionManager(host=host, port=port)
    return manager.setup_all_collections(recreate=recreate)


if __name__ == "__main__":
    # Run standalone setup
    import os
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))

    print("=" * 60)
    print("QDRANT COLLECTION SETUP")
    print("=" * 60)

    results = setup_qdrant(host=host, port=port, recreate=False)

    print("\nResults:")
    for name, status in results.items():
        print(f"  {name}: {status}")

    # Verify
    manager = QdrantCollectionManager(host=host, port=port)
    stats = manager.get_collection_stats()

    print("\nCollection Statistics:")
    for name, info in stats.items():
        print(f"  {name}: {info}")
```

---

## Day 5: Neo4j Schema Setup

### src/database/neo4j_setup.py

```python
"""
Neo4j Knowledge Graph Schema for Legal AI.

Nodes:
- Case: Legal cases with citations
- Statute: Laws and regulations
- LegalConcept: Legal principles
- Judge: Judges who authored opinions

Relationships:
- CITES, AFFIRMS, REVERSES, OVERRULES, DISTINGUISHES
- INTERPRETS (Case -> Statute)
- APPLIES (Case -> LegalConcept)
- AUTHORED (Judge -> Case)
"""

from neo4j import GraphDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Neo4jSchemaManager:
    """
    Manages Neo4j schema for Legal AI knowledge graph.
    """

    # Constraints for data integrity
    CONSTRAINTS = [
        ("case_id_unique", "CREATE CONSTRAINT case_id_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE"),
        ("case_citation_unique", "CREATE CONSTRAINT case_citation_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.citation IS UNIQUE"),
        ("statute_citation_unique", "CREATE CONSTRAINT statute_citation_unique IF NOT EXISTS FOR (s:Statute) REQUIRE s.citation IS UNIQUE"),
        ("concept_name_unique", "CREATE CONSTRAINT concept_name_unique IF NOT EXISTS FOR (lc:LegalConcept) REQUIRE lc.name IS UNIQUE"),
        ("judge_name_unique", "CREATE CONSTRAINT judge_name_unique IF NOT EXISTS FOR (j:Judge) REQUIRE j.name IS UNIQUE"),
    ]

    # Indexes for fast lookups
    INDEXES = [
        ("case_jurisdiction_idx", "CREATE INDEX case_jurisdiction_idx IF NOT EXISTS FOR (c:Case) ON (c.jurisdiction)"),
        ("case_year_idx", "CREATE INDEX case_year_idx IF NOT EXISTS FOR (c:Case) ON (c.year)"),
        ("case_court_level_idx", "CREATE INDEX case_court_level_idx IF NOT EXISTS FOR (c:Case) ON (c.court_level)"),
        ("case_importance_idx", "CREATE INDEX case_importance_idx IF NOT EXISTS FOR (c:Case) ON (c.importance)"),
        ("statute_code_idx", "CREATE INDEX statute_code_idx IF NOT EXISTS FOR (s:Statute) ON (s.code)"),
    ]

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")

    def close(self):
        """Close connection."""
        self.driver.close()

    def setup_schema(self) -> dict:
        """
        Set up all constraints and indexes.

        Returns:
            dict with status of each constraint/index
        """
        results = {"constraints": {}, "indexes": {}}

        with self.driver.session() as session:
            # Create constraints
            for name, query in self.CONSTRAINTS:
                try:
                    session.run(query)
                    results["constraints"][name] = "created"
                    logger.info(f"✅ Created constraint: {name}")
                except Exception as e:
                    results["constraints"][name] = f"exists or error: {str(e)[:50]}"

            # Create indexes
            for name, query in self.INDEXES:
                try:
                    session.run(query)
                    results["indexes"][name] = "created"
                    logger.info(f"✅ Created index: {name}")
                except Exception as e:
                    results["indexes"][name] = f"exists or error: {str(e)[:50]}"

        return results

    def verify_schema(self) -> dict:
        """Verify schema is properly set up."""
        with self.driver.session() as session:
            # Count constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = [r["name"] for r in result]

            # Count indexes
            result = session.run("SHOW INDEXES")
            indexes = [r["name"] for r in result]

            return {
                "constraints_count": len(constraints),
                "indexes_count": len(indexes),
                "constraints": constraints,
                "indexes": indexes,
            }

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WITH labels(n) AS labels, count(*) AS count
                RETURN labels, count
            """)

            node_counts = {}
            for record in result:
                label = record["labels"][0] if record["labels"] else "Unknown"
                node_counts[label] = record["count"]

            result = session.run("""
                MATCH ()-[r]->()
                WITH type(r) AS type, count(*) AS count
                RETURN type, count
            """)

            rel_counts = {}
            for record in result:
                rel_counts[record["type"]] = record["count"]

            return {
                "nodes": node_counts,
                "relationships": rel_counts,
            }


def setup_neo4j(uri: str, user: str, password: str) -> dict:
    """Convenience function to set up Neo4j schema."""
    manager = Neo4jSchemaManager(uri, user, password)
    try:
        results = manager.setup_schema()
        return results
    finally:
        manager.close()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "legal_ai_2024")

    print("=" * 60)
    print("NEO4J SCHEMA SETUP")
    print("=" * 60)

    results = setup_neo4j(uri, user, password)

    print("\nConstraints:")
    for name, status in results["constraints"].items():
        print(f"  {name}: {status}")

    print("\nIndexes:")
    for name, status in results["indexes"].items():
        print(f"  {name}: {status}")
```

---

## Day 5: Elasticsearch Index Setup

### src/database/elasticsearch_setup.py

```python
"""
Elasticsearch Index Setup for Legal AI BM25 Search.

Index: legal_documents
- Full-text search with BM25
- Keyword fields for filtering
- Optimized analyzers for legal text
"""

from elasticsearch import Elasticsearch
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ElasticsearchIndexManager:
    """Manages Elasticsearch index for legal documents."""

    INDEX_NAME = "legal_documents"

    INDEX_SETTINGS = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "5s",
            "analysis": {
                "analyzer": {
                    "legal_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",
                            "porter_stem"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "case_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "legal_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "full_text": {
                    "type": "text",
                    "analyzer": "legal_analyzer"
                },
                "abstract": {
                    "type": "text",
                    "analyzer": "legal_analyzer"
                },
                "citations": {"type": "keyword"},
                "jurisdiction": {"type": "keyword"},
                "court": {"type": "keyword"},
                "court_level": {"type": "integer"},
                "year": {"type": "integer"},
                "doc_type": {"type": "keyword"},
                "importance": {"type": "integer"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        }
    }

    def __init__(self, host: str = "localhost", port: int = 9200):
        """Initialize Elasticsearch client."""
        self.es = Elasticsearch([f"http://{host}:{port}"])
        logger.info(f"Connected to Elasticsearch at {host}:{port}")

    def setup_index(self, recreate: bool = False) -> dict:
        """
        Set up the legal_documents index.

        Args:
            recreate: If True, delete existing index first
        """
        exists = self.es.indices.exists(index=self.INDEX_NAME)

        if exists and recreate:
            logger.info(f"Deleting existing index: {self.INDEX_NAME}")
            self.es.indices.delete(index=self.INDEX_NAME)
            exists = False

        if not exists:
            self.es.indices.create(
                index=self.INDEX_NAME,
                body=self.INDEX_SETTINGS
            )
            logger.info(f"✅ Created index: {self.INDEX_NAME}")
            return {"status": "created"}
        else:
            logger.info(f"⏭️ Index exists: {self.INDEX_NAME}")
            return {"status": "exists"}

    def get_stats(self) -> dict:
        """Get index statistics."""
        try:
            stats = self.es.indices.stats(index=self.INDEX_NAME)
            return {
                "docs_count": stats["indices"][self.INDEX_NAME]["primaries"]["docs"]["count"],
                "size_bytes": stats["indices"][self.INDEX_NAME]["primaries"]["store"]["size_in_bytes"],
            }
        except Exception as e:
            return {"error": str(e)}


def setup_elasticsearch(host: str = "localhost", port: int = 9200, recreate: bool = False) -> dict:
    """Convenience function to set up Elasticsearch index."""
    manager = ElasticsearchIndexManager(host=host, port=port)
    return manager.setup_index(recreate=recreate)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    port = int(os.getenv("ELASTICSEARCH_PORT", 9200))

    print("=" * 60)
    print("ELASTICSEARCH INDEX SETUP")
    print("=" * 60)

    result = setup_elasticsearch(host=host, port=port, recreate=False)
    print(f"\nResult: {result}")
```

---

## Day 5: Requirements & Project Configuration

### requirements.txt

```txt
# ═══════════════════════════════════════════════════════════════
# Core Dependencies
# ═══════════════════════════════════════════════════════════════
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
pyyaml==6.0.1

# ═══════════════════════════════════════════════════════════════
# Web Framework
# ═══════════════════════════════════════════════════════════════
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# ═══════════════════════════════════════════════════════════════
# AI/ML APIs
# ═══════════════════════════════════════════════════════════════
anthropic==0.18.1
voyageai==0.2.1
cohere==4.47
llama-parse==0.3.9

# ═══════════════════════════════════════════════════════════════
# Databases
# ═══════════════════════════════════════════════════════════════
qdrant-client==1.7.0
neo4j==5.17.0
elasticsearch==8.12.1
redis==5.0.1

# ═══════════════════════════════════════════════════════════════
# Document Processing
# ═══════════════════════════════════════════════════════════════
tiktoken==0.5.2
pypdf==4.0.1
beautifulsoup4==4.12.3

# ═══════════════════════════════════════════════════════════════
# Utilities
# ═══════════════════════════════════════════════════════════════
httpx==0.26.0
tenacity==8.2.3
structlog==24.1.0

# ═══════════════════════════════════════════════════════════════
# Development
# ═══════════════════════════════════════════════════════════════
pytest==8.0.0
pytest-asyncio==0.23.4
black==24.1.1
ruff==0.2.0
mypy==1.8.0
```

### pyproject.toml

```toml
[project]
name = "legal-ai"
version = "1.0.0"
description = "World-class Legal AI System with 80-100% better retrieval"
requires-python = ">=3.11"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## Week 1 Verification Script

### scripts/verify_week1.py

```python
"""
Week 1 Verification Script.

Verifies all infrastructure is properly set up:
1. Docker services running
2. Qdrant collections created with indexes
3. Neo4j schema created
4. Elasticsearch index created
5. Redis available
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_qdrant():
    """Verify Qdrant setup."""
    from qdrant_client import QdrantClient

    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )

    collections = ["case_abstracts", "legal_chunks", "hyde_questions"]
    results = {}

    for name in collections:
        try:
            info = client.get_collection(name)
            results[name] = f"✅ OK (vectors: {info.vectors_count})"
        except Exception as e:
            results[name] = f"❌ FAIL: {e}"

    return results

def check_neo4j():
    """Verify Neo4j setup."""
    from neo4j import GraphDatabase

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "legal_ai_2024")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = list(result)
            return f"✅ OK (constraints: {len(constraints)})"
    except Exception as e:
        return f"❌ FAIL: {e}"
    finally:
        driver.close()

def check_elasticsearch():
    """Verify Elasticsearch setup."""
    from elasticsearch import Elasticsearch

    host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    port = int(os.getenv("ELASTICSEARCH_PORT", 9200))

    es = Elasticsearch([f"http://{host}:{port}"])

    try:
        if es.indices.exists(index="legal_documents"):
            stats = es.indices.stats(index="legal_documents")
            docs = stats["indices"]["legal_documents"]["primaries"]["docs"]["count"]
            return f"✅ OK (docs: {docs})"
        else:
            return "❌ Index not found"
    except Exception as e:
        return f"❌ FAIL: {e}"

def check_redis():
    """Verify Redis setup."""
    import redis

    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        r = redis.from_url(url)
        r.ping()
        return "✅ OK"
    except Exception as e:
        return f"❌ FAIL: {e}"

def main():
    print("=" * 60)
    print("WEEK 1 INFRASTRUCTURE VERIFICATION")
    print("=" * 60)

    print("\n📦 QDRANT COLLECTIONS:")
    qdrant_results = check_qdrant()
    for name, status in qdrant_results.items():
        print(f"   {name}: {status}")

    print("\n🔗 NEO4J:")
    print(f"   Schema: {check_neo4j()}")

    print("\n🔍 ELASTICSEARCH:")
    print(f"   Index: {check_elasticsearch()}")

    print("\n💾 REDIS:")
    print(f"   Connection: {check_redis()}")

    print("\n" + "=" * 60)

    # Summary
    all_ok = all("✅" in str(v) for v in qdrant_results.values())
    all_ok = all_ok and "✅" in check_neo4j()
    all_ok = all_ok and "✅" in check_elasticsearch()
    all_ok = all_ok and "✅" in check_redis()

    if all_ok:
        print("🎉 ALL CHECKS PASSED - Week 1 infrastructure ready!")
        return 0
    else:
        print("⚠️ SOME CHECKS FAILED - Review above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Week 1 Completion Checklist

| Task | Status | File |
|------|--------|------|
| Docker Compose | ⬜ | `docker-compose.yml` |
| Environment Config | ⬜ | `.env.example` |
| Qdrant Collections | ⬜ | `src/indexing/collections.py` |
| Neo4j Schema | ⬜ | `src/database/neo4j_setup.py` |
| Elasticsearch Index | ⬜ | `src/database/elasticsearch_setup.py` |
| Requirements | ⬜ | `requirements.txt` |
| Verification Script | ⬜ | `scripts/verify_week1.py` |

---

## Week 1 Commands

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy
docker-compose ps

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set up Qdrant collections
python -m src.indexing.collections

# 5. Set up Neo4j schema
python -m src.database.neo4j_setup

# 6. Set up Elasticsearch index
python -m src.database.elasticsearch_setup

# 7. Verify everything
python scripts/verify_week1.py
```

---

**WEEK 1 DELIVERS: Production-grade infrastructure foundation for the Legal AI system.**
