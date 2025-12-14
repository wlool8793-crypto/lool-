# LEGAL AI SYSTEM - COMPLETE BLUEPRINT FOR AGENTIC IDE

## INSTRUCTIONS FOR AGENTIC IDE

This is a detailed specification. Write production-grade code for each file.
Follow the exact structure, logic, and interfaces specified.

---

## SYSTEM OVERVIEW

```
Goal: Legal AI with 80-100% better retrieval, zero hallucinations
Tech: LangChain ecosystem (MVP) → Convert to custom code later
```

---

## INFRASTRUCTURE

### File: docker-compose.yml

**Services to create:**

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| qdrant | qdrant/qdrant:v1.12.1 | 6333, 6334 | Vector DB (3 collections) |
| neo4j | neo4j:5.26.0 | 7474, 7687 | Knowledge graph |
| elasticsearch | elasticsearch:8.16.0 | 9200 | BM25 search |
| redis | redis:7.4-alpine | 6379 | Caching |

**Requirements:**
- Health checks for all services
- Volume persistence
- Memory limits (qdrant: 8G, neo4j: 4G, es: 4G, redis: 1G)
- Single network: legal-ai-network

---

### File: requirements.txt

**Dependencies:**
```
# LangChain
langchain==0.3.7
langchain-core==0.3.21
langchain-community==0.3.7
langchain-anthropic==0.3.0
langchain-voyageai==0.1.2
langchain-qdrant==0.2.0
langchain-cohere==0.3.2
langgraph==0.2.53

# Databases
qdrant-client==1.12.1
neo4j==5.26.0
elasticsearch==8.16.0
redis==5.2.1

# Document Processing
llama-parse==0.5.17
pypdf==5.1.0
beautifulsoup4==4.12.3
tiktoken==0.8.0

# API
fastapi==0.115.6
uvicorn[standard]==0.32.1
sse-starlette==2.1.3

# Utils
python-dotenv==1.0.1
pydantic==2.10.3
pydantic-settings==2.6.1
tenacity==9.0.0
structlog==24.4.0
```

---

### File: .env.example

**Variables needed:**
```
ANTHROPIC_API_KEY=
VOYAGE_API_KEY=
COHERE_API_KEY=
LLAMA_CLOUD_API_KEY=

QDRANT_HOST=localhost
QDRANT_PORT=6333

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=legal_ai_2024

ELASTICSEARCH_URL=http://localhost:9200
REDIS_URL=redis://localhost:6379/0

EMBEDDING_MODEL=voyage-law-2
EMBEDDING_DIMENSION=1024
LLM_MODEL=claude-3-5-sonnet-20241022
RERANK_MODEL=rerank-v3.5

TOP_CASES=20
TOP_CHUNKS=10
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MAX_VERIFICATION_ATTEMPTS=3
```

---

## SOURCE FILES

### File: src/config.py

**Purpose:** Centralized configuration

**Implementation:**
- Use pydantic-settings BaseSettings
- Load from .env file
- All settings as class attributes
- Cached with @lru_cache

**Settings to include:**
- All API keys
- All database connection strings
- Model names
- Search parameters (TOP_CASES, TOP_CHUNKS, etc.)
- Feature flags

---

### File: src/extraction/rule_based.py

**Purpose:** FREE metadata extraction using regex (no API calls)

**Class: RuleBasedExtractor**

**Methods:**
```python
def extract(text: str) -> RuleBasedResult
def _extract_citations(text: str) -> Dict[str, List[str]]
def _extract_dates(text: str) -> List[str]
def _extract_year(text: str) -> Optional[int]
def _extract_court(text: str) -> Dict  # {court, level}
def _extract_jurisdiction(text: str) -> str
def _extract_parties(text: str) -> Dict[str, str]
def _extract_signals(text: str) -> Dict[str, bool]
def _extract_sections(text: str) -> List[str]
```

**Regex patterns to implement:**

| Type | Pattern |
|------|---------|
| Case citation | `\d+\s+[A-Z][a-z]+\.(?:\s*\d*[a-z]*\.)*\s+\d+` |
| USC | `\d+\s+U\.S\.C\.?\s*§?\s*\d+` |
| CFR | `\d+\s+C\.F\.R\.?\s*§?\s*[\d\.]+` |
| Supreme Court | `\d+\s+U\.S\.\s+\d+` |
| Federal Reporter | `\d+\s+F\.(?:2d\|3d\|4th)?\s+\d+` |

**Court levels:**
- Supreme Court = 1
- Court of Appeals = 2
- District Court = 3

**Signal words to detect:**
- affirmed, reversed, overruled, distinguished, cited, followed

**Section types to detect:**
- facts, issue, holding, reasoning, conclusion

**Output dataclass: RuleBasedResult**
```python
@dataclass
class RuleBasedResult:
    citations: Dict[str, List[str]]
    dates: List[str]
    year: Optional[int]
    court: Optional[str]
    court_level: int  # 1-3
    jurisdiction: Optional[str]
    parties: Dict[str, str]
    signals: Dict[str, bool]
    section_types: List[str]
    word_count: int
    has_citations: bool
```

---

### File: src/extraction/claude_mega.py

**Purpose:** Extract everything in ONE API call per document

**Class: ClaudeMegaExtractor**

**Method:**
```python
def extract(
    document: str,
    chunks: List[str],
    rule_metadata: dict
) -> MegaExtractionResult
```

**Uses:** LangChain ChatAnthropic with claude-3-haiku (cheap, fast)

**Single prompt extracts:**
1. Case abstract (title, citation, court, year, outcome, summary, holdings, principles)
2. Chunk contexts (2-3 sentence prefix for EACH chunk for contextual retrieval)
3. Entities (cases, statutes, concepts, judges)
4. Relationships (cites, affirms, reverses, interprets, applies)
5. Hypothetical questions (3-5 questions this case answers - for HyDE)
6. Importance score (1-10)

**Output models (Pydantic):**
```python
class CaseAbstract(BaseModel):
    title: str
    citation: str
    court: str
    year: int
    outcome: str  # affirmed/reversed/remanded
    summary: str  # 2-3 sentences
    key_holdings: List[str]
    legal_principles: List[str]

class ChunkContext(BaseModel):
    chunk_index: int
    context: str  # 2-3 sentence prefix
    section_type: str
    importance: int  # 1-10

class Entity(BaseModel):
    name: str
    type: str  # case/statute/concept/judge
    citation: Optional[str]

class Relationship(BaseModel):
    source: str
    target: str
    relation: str  # cites/affirms/reverses/interprets/applies

class MegaExtractionResult(BaseModel):
    case_abstract: CaseAbstract
    chunk_contexts: List[ChunkContext]
    entities: List[Entity]
    relationships: List[Relationship]
    hypothetical_questions: List[str]
    importance_score: int
```

**CRITICAL - Chunk Context Format:**
```
"This [section_type] from [case_name] discusses [topic].
The court [key action/finding]. This is relevant to [legal principle]."
```

---

### File: src/extraction/pipeline.py

**Purpose:** Combined extraction pipeline

**Class: ExtractionPipeline**

**Method:**
```python
def extract_document(
    document: str,
    chunks: List[str]
) -> Tuple[RuleBasedResult, MegaExtractionResult]
```

**Logic:**
1. Run rule_based.extract() first (FREE)
2. Pass results to claude_mega.extract()
3. Return both results

---

### File: src/ingestion/parser.py

**Purpose:** Parse PDF/HTML documents

**Class: LegalDocumentParser**

**Method:**
```python
def parse(file_path: str) -> List[Document]
```

**Implementation:**
- Use LangChain LlamaParse loader for PDFs (if API key available)
- Fallback to PyPDFLoader
- Use BSHTMLLoader for HTML
- Add source metadata to documents

---

### File: src/ingestion/chunker.py

**Purpose:** Contextual chunking with 2-3 sentence prefixes

**Class: ContextualChunker**

**CRITICAL FEATURE - Contextual Retrieval:**
Each chunk gets a context prefix that improves retrieval by 35-49%

**Method:**
```python
def chunk(
    documents: List[Document],
    chunk_contexts: List[ChunkContext]  # From MEGA extraction
) -> List[Document]
```

**Logic:**
1. Use LangChain RecursiveCharacterTextSplitter
2. Split with legal separators: `["\n## ", "\nFACTS", "\nHOLDING", "\n\n", ". "]`
3. Chunk size: 500 tokens, overlap: 100 tokens
4. For each chunk, prepend the context from MegaExtractionResult
5. Final content = context + "\n\n" + original_chunk

**Output metadata per chunk:**
- chunk_id
- case_id
- position
- section_type
- token_count
- has_context: bool

---

### File: src/ingestion/pipeline.py

**Purpose:** Full ingestion pipeline

**Class: IngestionPipeline**

**Method:**
```python
def ingest(file_path: str) -> IngestionResult
```

**Logic:**
1. Parse document → List[Document]
2. Get full text
3. Initial chunking (for MEGA extraction)
4. Run extraction pipeline → RuleBasedResult, MegaExtractionResult
5. Final chunking with contexts
6. Index to all stores (multi_indexer)
7. Return stats

---

### File: src/indexing/collections.py

**Purpose:** Setup 3 Qdrant collections

**Collections:**

**1. case_abstracts (Level 1 search)**
```
Vector: 1024 dims (voyage-law-2)
Payload indexes:
- case_id (keyword)
- jurisdiction (keyword)
- court_level (integer)
- year (integer)
- importance (integer)
- doc_type (keyword)
```

**2. legal_chunks (Level 2 search)**
```
Vector: 1024 dims
Payload indexes:
- chunk_id (keyword)
- case_id (keyword) ← CRITICAL for hierarchical filtering
- section_type (keyword)
- jurisdiction (keyword)
- court_level (integer)
- year (integer)
```

**3. hyde_questions (HyDE matching)**
```
Vector: 1024 dims
Payload indexes:
- case_id (keyword)
```

**Class: QdrantCollectionManager**

**Methods:**
```python
def setup_all(recreate: bool = False) -> Dict[str, str]
def get_vectorstore(collection_name: str) -> Qdrant
def get_stats() -> Dict[str, Dict]
```

---

### File: src/indexing/graph.py

**Purpose:** Neo4j knowledge graph

**Schema:**

**Nodes:**
```
(:Case {id, title, citation, year, jurisdiction, court_level, importance})
(:Statute {citation, title, code})
(:LegalConcept {name, category})
(:Judge {name, court})
```

**Relationships:**
```
(Case)-[:CITES]->(Case)
(Case)-[:AFFIRMS]->(Case)
(Case)-[:REVERSES]->(Case)
(Case)-[:OVERRULES]->(Case)
(Case)-[:DISTINGUISHES]->(Case)
(Case)-[:INTERPRETS]->(Statute)
(Case)-[:APPLIES]->(LegalConcept)
(Judge)-[:AUTHORED]->(Case)
```

**Class: KnowledgeGraph**

**Methods:**
```python
def setup_schema() -> Dict[str, str]
def add_case(case_data: Dict) -> None
def add_relationship(source_id, target_id, relation_type) -> None
def add_statute_interpretation(case_id, statute_citation) -> None
def get_related_cases(case_ids: List[str], depth: int, limit: int) -> List[Dict]
def get_citing_cases(case_id: str, limit: int) -> List[Dict]
def get_stats() -> Dict
```

---

### File: src/indexing/elasticsearch_index.py

**Purpose:** BM25 full-text search index

**Index: legal_documents**

**Mappings:**
```json
{
  "case_id": "keyword",
  "title": "text",
  "full_text": "text",
  "abstract": "text",
  "citations": "keyword",
  "jurisdiction": "keyword",
  "court": "keyword",
  "year": "integer"
}
```

**Class: ElasticsearchManager**

**Methods:**
```python
def setup_index(recreate: bool = False) -> Dict
def index_document(doc: Dict) -> None
def search(query: str, filters: Dict, limit: int) -> List[Dict]
def get_stats() -> Dict
```

---

### File: src/indexing/multi_indexer.py

**Purpose:** Index to ALL stores in one call

**Class: MultiIndexer**

**Method:**
```python
def index_document(
    doc: Document,
    extraction: MegaExtractionResult,
    chunks: List[Document],
    rule_metadata: RuleBasedResult
) -> IndexingResult
```

**Logic:**
1. Generate embeddings for abstract → Voyage
2. Index to case_abstracts collection
3. Generate embeddings for all chunks → Voyage batch
4. Index to legal_chunks collection
5. Generate embeddings for HyDE questions → Voyage
6. Index to hyde_questions collection
7. Add case node to Neo4j
8. Add all relationships to Neo4j
9. Index full text to Elasticsearch
10. Return stats

---

### File: src/search/hierarchical.py

**Purpose:** 3-Level hierarchical search

**ALGORITHM:**
```
Level 1: Search case_abstracts → top 20 cases
         ↓ Extract case_ids
Level 2: Search legal_chunks WITH FILTER case_id IN [case_ids]
         ↓ Get relevant passages
Level 3: Expand via Neo4j → get related cases through citations
         ↓ Search their chunks too
Merge: Combine all results, deduplicate
Rerank: Cohere + authority weighting
```

**Class: HierarchicalSearchEngine**

**Method:**
```python
def search(
    query: str,
    top_cases: int = 20,
    top_chunks: int = 10,
    filters: Optional[Dict] = None
) -> List[SearchResult]
```

**Steps:**
1. Embed query with Voyage (input_type="query")
2. Search case_abstracts → get top_cases results
3. Extract case_ids from results
4. Search legal_chunks with filter: case_id IN case_ids
5. Search hyde_questions for bonus matches
6. If ENABLE_GRAPH_EXPANSION: get related cases from Neo4j, search their chunks
7. Merge all chunk results
8. Rerank with authority weighting
9. Return top_chunks

**Output:**
```python
@dataclass
class SearchResult:
    id: str
    case_id: str
    content: str
    score: float
    authority_score: float
    metadata: Dict[str, Any]
```

---

### File: src/search/hybrid.py

**Purpose:** Combine vector search + BM25

**Class: HybridSearchEngine**

**Method:**
```python
def search(
    query: str,
    top_k: int = 10,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3
) -> List[SearchResult]
```

**Logic:**
1. Get vector results from hierarchical search
2. Get BM25 results from Elasticsearch
3. Normalize scores (0-1)
4. Combine: final_score = vector_weight * vector_score + bm25_weight * bm25_score
5. Merge and deduplicate by case_id
6. Return combined results

---

### File: src/search/reranker.py

**Purpose:** Authority-weighted reranking

**Class: AuthorityReranker**

**Method:**
```python
def rerank(
    query: str,
    results: List[SearchResult],
    top_k: int
) -> List[SearchResult]
```

**AUTHORITY FORMULA:**
```python
# Cohere rerank first
cohere_score = cohere.rerank(query, documents)

# Authority boosts
court_boost = 1 + (0.1 * (4 - court_level))
# Supreme (1) = 1.3, Appeals (2) = 1.2, District (3) = 1.1

importance_boost = 1 + (0.05 * importance)
# Score 10 = 1.5x, Score 5 = 1.25x

recency_boost = 1 + (0.01 * (year - 2000))
# 2024 = 1.24x, 2010 = 1.1x

# Final score
authority_score = cohere_score * court_boost * importance_boost * recency_boost
```

---

### File: src/generation/prompts.py

**Purpose:** All prompts in one place

**Prompts to define:**

**1. TEST_GENERATION_PROMPT**
```
Generate 5 verification tests for legal answer:
- Citation accuracy
- Jurisdiction correctness
- Legal principle accuracy
- Factual grounding
- Completeness
```

**2. ANSWER_GENERATION_PROMPT**
```
Answer using ONLY context provided.
Must pass all tests.
Include feedback from previous attempts if retry.
```

**3. VERIFICATION_PROMPT**
```
Verify answer against each test.
Output PASS/FAIL for each with reason.
Final line: OVERALL: X/Y passed
```

**4. CONTEXT_GENERATION_PROMPT** (for chunk contexts)
```
Generate 2-3 sentence context for this chunk.
Format: "This [section] from [case] discusses [topic]..."
```

---

### File: src/generation/test_first.py

**Purpose:** Test-first answer generation with zero hallucinations

**ALGORITHM:**
```
1. Generate 5 verification tests
2. Generate answer (considering tests)
3. Verify answer against tests
4. If any test fails AND attempts < 3:
   - Add failure feedback
   - Go to step 2
5. Return answer with confidence score
```

**Class: TestFirstGenerator**

**Uses:** LangGraph for workflow

**State:**
```python
class GenerationState(TypedDict):
    question: str
    context: str
    jurisdiction: str
    tests: List[VerificationTest]
    answer: str
    attempt: int
    max_attempts: int
    all_passed: bool
    confidence: float  # passed_tests / total_tests
    feedback: List[str]
```

**Workflow nodes:**
1. generate_tests → creates 5 tests
2. generate_answer → creates answer considering tests + feedback
3. verify_answer → checks each test, sets pass/fail

**Conditional edge:**
- If all_passed OR attempt >= max_attempts → END
- Else → generate_answer (retry)

**Method:**
```python
def generate(
    question: str,
    context: Optional[str] = None,
    jurisdiction: str = "Federal"
) -> GenerationResult
```

**Output:**
```python
class GenerationResult:
    question: str
    answer: str
    confidence: float
    verified: bool
    attempts: int
    tests: List[VerificationTest]
```

---

### File: src/api/main.py

**Purpose:** FastAPI application

**Endpoints:**

**GET /health**
```python
Response: {
    "status": "ok" | "degraded",
    "version": "1.0.0",
    "services": {
        "qdrant": "ok" | "error",
        "neo4j": "ok" | "error",
        "elasticsearch": "ok" | "error",
        "redis": "ok" | "error"
    }
}
```

**POST /search**
```python
Request: {
    "query": str,
    "top_k": int = 10,
    "filters": Optional[Dict]
}
Response: {
    "results": List[SearchResult],
    "total": int
}
```

**POST /query**
```python
Request: {
    "question": str,
    "jurisdiction": str = "Federal",
    "top_chunks": int = 10,
    "stream": bool = False
}
Response: {
    "question": str,
    "answer": str,
    "confidence": float,
    "verified": bool,
    "sources": List[Dict]
}
```

**POST /query (stream=True)**
- Use SSE (Server-Sent Events)
- Event: "sources" → search results
- Event: "answer" → answer chunks
- Event: "done" → final metadata

**POST /ingest**
```python
Request: {
    "file_path": str
}
Response: {
    "chunks_ingested": int,
    "case_id": str
}
```

---

### File: src/api/middleware.py

**Purpose:** Caching and rate limiting

**Implement:**
1. Redis cache for search results (TTL: 1 hour)
2. Redis cache for embeddings (TTL: 24 hours)
3. Rate limiting (optional)

**Cache key format:**
- Search: `search:{hash(query + filters)}`
- Embedding: `embed:{hash(text)}`

---

### File: scripts/setup_all.py

**Purpose:** One-click setup

**Steps:**
1. Setup Qdrant collections (3)
2. Setup Neo4j schema
3. Setup Elasticsearch index
4. Verify all services
5. Print status

---

### File: scripts/verify_all.py

**Purpose:** Full system verification

**Checks:**
1. Environment variables set
2. LangChain imports work
3. Qdrant connected + 3 collections exist
4. Neo4j connected + schema exists
5. Elasticsearch connected + index exists
6. Redis connected

**Output:** PASS/FAIL for each with details

---

### File: scripts/demo.py

**Purpose:** Demo the full system

**Steps:**
1. Ingest a sample PDF
2. Run a test query
3. Show hierarchical search results
4. Show verified answer
5. Print confidence score

---

## TESTS

### File: tests/test_extraction.py

**Test cases:**
1. Rule-based extracts citations correctly
2. Rule-based extracts court level correctly
3. MEGA extraction returns valid structure
4. MEGA generates chunk contexts

---

### File: tests/test_search.py

**Test cases:**
1. Hierarchical search returns results
2. Level 2 filters by case_id correctly
3. Authority reranking applies formula correctly
4. Hybrid search combines scores correctly

---

### File: tests/test_generation.py

**Test cases:**
1. Test generation creates 5 tests
2. Verification detects failing answers
3. Retry loop improves answer
4. Confidence score calculated correctly

---

## EXECUTION ORDER

```
1. Create docker-compose.yml
2. Create requirements.txt
3. Create .env.example
4. Create src/config.py
5. Create src/extraction/rule_based.py
6. Create src/extraction/claude_mega.py
7. Create src/extraction/pipeline.py
8. Create src/ingestion/parser.py
9. Create src/ingestion/chunker.py
10. Create src/ingestion/pipeline.py
11. Create src/indexing/collections.py
12. Create src/indexing/graph.py
13. Create src/indexing/elasticsearch_index.py
14. Create src/indexing/multi_indexer.py
15. Create src/search/hierarchical.py
16. Create src/search/hybrid.py
17. Create src/search/reranker.py
18. Create src/generation/prompts.py
19. Create src/generation/test_first.py
20. Create src/api/main.py
21. Create src/api/middleware.py
22. Create scripts/setup_all.py
23. Create scripts/verify_all.py
24. Create scripts/demo.py
25. Create tests/test_*.py
```

---

## VERIFICATION CHECKLIST

After implementation, verify:

- [ ] docker-compose up starts all 4 services
- [ ] pip install -r requirements.txt succeeds
- [ ] scripts/setup_all.py creates all collections/indexes
- [ ] scripts/verify_all.py shows all PASS
- [ ] Ingesting a PDF creates entries in all stores
- [ ] Search returns hierarchical results
- [ ] Answer generation includes confidence score
- [ ] API endpoints all work
- [ ] Streaming works for /query

---

## KEY METRICS TO ACHIEVE

| Metric | Target | How |
|--------|--------|-----|
| Retrieval improvement | +35-49% | Contextual chunk prefixes |
| Hallucination rate | 0% | Test-first verification |
| API cost savings | 60% | Rule-based extraction |
| Query latency | <3 seconds | Hierarchical search |
| Search precision | +20-30% | Case abstracts collection |
