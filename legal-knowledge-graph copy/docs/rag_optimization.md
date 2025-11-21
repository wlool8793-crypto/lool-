# RAG Optimization Features

## Overview

This document details the Retrieval-Augmented Generation (RAG) optimization features built into the Legal Knowledge Graph schema.

## RAG Architecture

### Three-Pillar Approach

The schema implements a hybrid retrieval system combining:

1. **Vector Search** (Semantic)
2. **Keyword Search** (Lexical)
3. **Graph Traversal** (Relational)

This multi-modal approach ensures comprehensive and accurate retrieval across different query types.

## Vector Search Implementation

### Embedding Nodes

Dedicated `Embedding` nodes enable sophisticated vector search:

```cypher
CREATE (e:Embedding {
  embedding_id: 'emb_001',
  vector: [0.012, -0.034, ...],  // 1536 dimensions
  text: 'The Supreme Court held that...',
  embedding_model: 'text-embedding-ada-002',
  dimensions: 1536,
  chunk_index: 1,
  chunk_size: 512,
  overlap: 50
})
```

### Vector Indexes

```cypher
CREATE VECTOR INDEX embedding_vector IF NOT EXISTS
FOR (e:Embedding) ON (e.vector)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
```

### Multi-Level Embedding Strategy

**Document-Level Embeddings**:
- Entire case summary
- Full statute preamble
- Legal principle definition

**Chunk-Level Embeddings**:
- 512-token chunks with 50-token overlap
- Indexed separately for granular retrieval
- Linked to parent document

**Hybrid Approach**:
```cypher
// Document-level search (broad context)
(:Case)-[:HAS_EMBEDDING]->(:Embedding {chunk_index: 0})

// Chunk-level search (specific passages)
(:Case)-[:HAS_EMBEDDING]->(:Embedding {chunk_index: 1..N})
```

### Similarity Search Query

```cypher
// Find semantically similar cases
MATCH (e:Embedding)
WHERE e.vector IS NOT NULL
CALL db.index.vector.queryNodes('embedding_vector', 10, $query_embedding)
YIELD node, score
MATCH (node)<-[:HAS_EMBEDDING]-(case:Case)
RETURN case, score
ORDER BY score DESC
LIMIT 5
```

## Keyword Search Implementation

### Full-Text Indexes

Strategic full-text indexes on key fields:

```cypher
// Case full-text search
CREATE FULLTEXT INDEX case_fulltext IF NOT EXISTS
FOR (c:Case) ON EACH [c.title, c.summary, c.headnotes, c.full_text]
OPTIONS {analyzer: 'english'};

// Statute full-text search
CREATE FULLTEXT INDEX statute_fulltext IF NOT EXISTS
FOR (s:Statute) ON EACH [s.name, s.short_name, s.summary, s.preamble, s.full_text]
OPTIONS {analyzer: 'english'};

// Section full-text search
CREATE FULLTEXT INDEX section_fulltext IF NOT EXISTS
FOR (s:Section) ON EACH [s.section_number, s.title, s.text, s.summary]
OPTIONS {analyzer: 'english'};
```

### Keyword Extraction

Dedicated `Keyword` nodes with embeddings:

```cypher
CREATE (k:Keyword {
  keyword_id: 'KW-MURDER',
  term: 'murder',
  normalized_term: 'murder',
  category: 'Crime',
  frequency: 1000,
  embedding: [...]  // Keyword embedding
})

// Link to documents with relevance
(case)-[:HAS_KEYWORD {
  relevance_score: 0.95,
  frequency: 8,
  extraction_method: 'TF-IDF'
}]->(keyword)
```

### Keyword Search Query

```cypher
// Full-text search with ranking
CALL db.index.fulltext.queryNodes('case_fulltext', 'murder AND death penalty')
YIELD node, score
MATCH (node:Case)
WHERE node.jurisdiction = 'BD'
RETURN node, score
ORDER BY score DESC
LIMIT 10
```

## Graph Traversal for Context Enrichment

### Precedent Chain Retrieval

```cypher
// Find precedent chain
MATCH path = (start:Case {case_id: $case_id})-[:CITES*1..3]->(precedent:Case)
WHERE ALL(r IN relationships(path) WHERE r.treatment = 'Positive')
RETURN precedent, length(path) as depth
ORDER BY depth
```

### Related Section Discovery

```cypher
// Find related sections through case applications
MATCH (case:Case)-[:APPLIES_SECTION]->(section:Section)
WHERE case.case_id = $case_id
MATCH (statute:Statute)-[:CONTAINS]->(section)
MATCH (statute)-[:CONTAINS]->(related:Section)
WHERE related <> section
RETURN related, statute
```

### Cross-Jurisdiction Precedent

```cypher
// Find persuasive precedents from other jurisdictions
MATCH (case:Case {jurisdiction: 'BD'})-[:CITES]->(cited:Case)
WHERE cited.jurisdiction IN ['IN', 'PK']
AND cited.precedent_value = 'Binding'
RETURN cited
```

## Hybrid Retrieval Pipeline

### Stage 1: Multi-Modal Retrieval

**Vector Search**:
```cypher
CALL db.index.vector.queryNodes('case_embedding', 20, $query_embedding)
YIELD node as case, score as vector_score
```

**Keyword Search**:
```cypher
CALL db.index.fulltext.queryNodes('case_fulltext', $query_text)
YIELD node as case, score as text_score
```

**Metadata Filter**:
```cypher
MATCH (case:Case)
WHERE case.jurisdiction = $jurisdiction
AND case.case_type = $case_type
AND case.decision_date >= $start_date
```

### Stage 2: Score Fusion

**Weighted Combination**:
```cypher
WITH case,
     0.5 * vector_score as vs,
     0.3 * text_score as ts,
     0.2 * graph_score as gs
RETURN case, (vs + ts + gs) as final_score
ORDER BY final_score DESC
```

**Reciprocal Rank Fusion**:
```python
def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            scores[doc] = scores.get(doc, 0) + 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Stage 3: Context Assembly

```cypher
// Get comprehensive context for top results
MATCH (case:Case {case_id: $case_id})
OPTIONAL MATCH (case)-[:APPLIES_SECTION]->(section:Section)
OPTIONAL MATCH (case)-[:CITES]->(cited:Case)
OPTIONAL MATCH (case)-[:RAISES_ISSUE]->(issue:LegalIssue)
OPTIONAL MATCH (case)-[:ESTABLISHES_PRINCIPLE]->(principle:LegalPrinciple)
OPTIONAL MATCH (case)-[:DECIDED_BY]->(judge:Judge)
RETURN case,
       collect(DISTINCT section) as sections,
       collect(DISTINCT cited) as citations,
       collect(DISTINCT issue) as issues,
       collect(DISTINCT principle) as principles,
       judge
```

## Chunk Node and Granular Retrieval

### Overview

Iteration 2 introduces dedicated `Chunk` nodes for semantically meaningful document segments, enabling more precise retrieval than traditional fixed-size chunking.

### Chunk Node Architecture

**Semantic Chunking**:
```cypher
// Create chunk with semantic type
CREATE (chunk:Chunk {
  chunk_id: 'bd_2023_sc_001_chunk_003',
  chunk_text: 'The Supreme Court held that Article 32 of the Constitution...',
  chunk_type: 'holding',  // facts, holding, reasoning, dissent, etc.
  start_char: 1250,
  end_char: 1450,
  token_count: 42,
  source: 'IndianKanoon',
  extracted_at: datetime('2024-01-15T10:30:00Z'),
  extracted_by: 'GPT-4-Chunking-v2',
  confidence_score: 0.95,
  trust_score: 0.92,
  verification_status: 'Verified',
  version: 1,
  created_at: datetime('2024-01-15T10:30:00Z'),
  updated_at: datetime('2024-01-15T10:30:00Z'),
  summary: 'Supreme Court ruling on Article 32 constitutional remedies',
  keywords: ['Article 32', 'constitutional remedies', 'fundamental rights'],
  embedding: [0.012, -0.034, ...]  // 1536-dimensional vector
})

// Link chunk to source case
MATCH (case:Case {case_id: 'bd_2023_sc_001'})
MATCH (chunk:Chunk {chunk_id: 'bd_2023_sc_001_chunk_003'})
CREATE (chunk)-[:CHUNK_OF]->(case)
```

**Chunk Types for Legal Documents**:
- **facts**: Factual background and case history
- **holding**: Court's decision/ruling
- **reasoning**: Legal reasoning and analysis
- **dissent**: Dissenting opinions
- **procedural_history**: Procedural timeline
- **legal_analysis**: Legal doctrine discussion
- **precedent_discussion**: Discussion of prior cases
- **statute_interpretation**: Interpretation of statutes

### Advantages of Chunk Nodes

1. **Semantic Precision**: Retrieve exact legal concepts (e.g., only holdings)
2. **Reduced Noise**: Filter out irrelevant procedural text
3. **Context Preservation**: Maintain position within document
4. **Metadata Enrichment**: Store keywords, entities, summaries per chunk
5. **Trust Filtering**: Each chunk has trust_score for quality control

### Granular Retrieval Queries

**Query by Chunk Type**:
```cypher
// Find only holdings from relevant cases
CALL db.index.vector.queryNodes('chunk_embedding_index', 10, $query_embedding)
YIELD node as chunk, score
WHERE chunk:Chunk
  AND chunk.chunk_type = 'holding'
  AND chunk.trust_score > 0.8
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.jurisdiction = 'BD'
RETURN chunk.chunk_text, case.title, score
ORDER BY score DESC
```

**Query with Trust Filtering**:
```cypher
// High-quality chunks only
MATCH (chunk:Chunk)
WHERE chunk.trust_score > 0.8
  AND chunk.verification_status = 'Verified'
  AND chunk.chunk_type IN ['holding', 'reasoning']
CALL db.index.vector.queryNodes('chunk_embedding_index', 5, $query_embedding)
YIELD node, score
WHERE node = chunk
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
RETURN chunk, case, score
```

**Multi-Type Retrieval**:
```cypher
// Get both holdings and reasoning
MATCH (chunk:Chunk)
WHERE chunk.chunk_type IN ['holding', 'reasoning']
  AND chunk.trust_score > 0.75
CALL db.index.vector.queryNodes('chunk_embedding_index', 20, $query_embedding)
YIELD node, score
WHERE node = chunk
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
RETURN chunk.chunk_type, chunk.chunk_text, case.citation, score
ORDER BY score DESC
```

## Principle-Based RAG with APPLIES_PRINCIPLE

### Overview

The `APPLIES_PRINCIPLE` relationship links chunks to legal principles, enabling principle-based legal reasoning in RAG applications.

### Relationship Structure

```cypher
// Link chunk to applied principle
MATCH (chunk:Chunk {chunk_id: 'bd_2023_sc_001_chunk_003'})
MATCH (principle:LegalPrinciple {principle_id: 'PRIN-BASIC-STRUCTURE'})
CREATE (chunk)-[:APPLIES_PRINCIPLE {
  context: 'Applied to determine that Parliament cannot amend Constitution to abolish fundamental rights',
  confidence: 0.95,
  principle_text: 'The Basic Structure Doctrine prevents amendments that alter essential features...',
  application_type: 'Applied',  // Applied, Distinguished, Explained, Criticized, etc.
  relevance_score: 0.98,
  extracted_by: 'GPT-4-Principle-Extraction-v2',
  created_at: datetime('2024-01-15T10:30:00Z')
}]->(principle)
```

### Principle-Based Query Patterns

**Pattern 1: Find Applications of Specific Principle**:
```cypher
// Find all chunks applying "Natural Justice"
MATCH (principle:LegalPrinciple {name: 'Natural Justice'})
MATCH (chunk:Chunk)-[r:APPLIES_PRINCIPLE]->(principle)
WHERE r.confidence > 0.8
  AND chunk.trust_score > 0.8
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.jurisdiction = 'BD'
RETURN chunk.chunk_text, r.application_type, r.context, case.citation
ORDER BY case.decision_date DESC
```

**Pattern 2: Principle Discovery from Query**:
```cypher
// Find relevant chunks and their principles
CALL db.index.vector.queryNodes('chunk_embedding_index', 10, $query_embedding)
YIELD node as chunk, score
WHERE chunk:Chunk AND chunk.trust_score > 0.8
MATCH (chunk)-[r:APPLIES_PRINCIPLE]->(principle:LegalPrinciple)
WHERE r.confidence > 0.85
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
RETURN
  chunk.chunk_text,
  principle.name,
  principle.definition,
  r.application_type,
  case.citation,
  score
ORDER BY score DESC
```

**Pattern 3: Cross-Principle Analysis**:
```cypher
// Find cases applying multiple related principles
MATCH (chunk1:Chunk)-[:APPLIES_PRINCIPLE]->(p1:LegalPrinciple {name: 'Natural Justice'})
MATCH (chunk2:Chunk)-[:APPLIES_PRINCIPLE]->(p2:LegalPrinciple {name: 'Fair Hearing'})
MATCH (chunk1)-[:CHUNK_OF]->(case:Case)<-[:CHUNK_OF]-(chunk2)
WHERE case.jurisdiction = 'BD'
  AND chunk1.trust_score > 0.8
  AND chunk2.trust_score > 0.8
RETURN case.title, case.citation,
       collect(DISTINCT p1.name) + collect(DISTINCT p2.name) as principles
```

**Pattern 4: Principle Evolution Tracking**:
```cypher
// Track how a principle is applied over time
MATCH (principle:LegalPrinciple {name: 'Basic Structure Doctrine'})
MATCH (chunk:Chunk)-[r:APPLIES_PRINCIPLE]->(principle)
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.jurisdiction IN ['BD', 'IN']
  AND r.confidence > 0.85
RETURN
  case.decision_date,
  case.citation,
  r.application_type,
  chunk.chunk_text,
  case.jurisdiction
ORDER BY case.decision_date ASC
```

### Trust-Based Filtering for Production

**High-Trust Query Pattern**:
```cypher
// Production-grade query with strict trust requirements
MATCH (chunk:Chunk)
WHERE chunk.trust_score > 0.8
  AND chunk.verification_status = 'Verified'
  AND chunk.confidence_score > 0.9
CALL db.index.vector.queryNodes('chunk_embedding_index', 5, $query_embedding)
YIELD node, score
WHERE node = chunk
MATCH (chunk)-[:CHUNK_OF]->(case:Case)
WHERE case.trust_score > 0.85
  AND case.verification_status = 'Verified'
  AND case.status = 'Active'
OPTIONAL MATCH (chunk)-[r:APPLIES_PRINCIPLE]->(principle:LegalPrinciple)
WHERE r.confidence > 0.85
RETURN
  chunk.chunk_text as text,
  chunk.chunk_type as type,
  case.citation,
  case.decision_date,
  collect(principle.name) as principles,
  score
ORDER BY score DESC
LIMIT 5
```

**Quality Metrics**:
```cypher
// Analyze chunk quality across corpus
MATCH (chunk:Chunk)
RETURN
  chunk.chunk_type,
  count(*) as total_chunks,
  avg(chunk.trust_score) as avg_trust,
  avg(chunk.confidence_score) as avg_confidence,
  sum(CASE WHEN chunk.verification_status = 'Verified' THEN 1 ELSE 0 END) as verified_count
ORDER BY avg_trust DESC
```

## Chunk Strategy for Large Documents

### Chunking Parameters

```python
CHUNK_SIZE = 512  # tokens
OVERLAP = 50      # tokens
MAX_CHUNKS = 100  # per document

def chunk_document(text, chunk_size=512, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({
            'text': chunk,
            'start': start,
            'end': end,
            'index': len(chunks)
        })
        start = end - overlap
    return chunks
```

### Chunk Storage

```cypher
// Create Chunk nodes (not just Embedding nodes)
UNWIND $chunks as chunk
CREATE (c:Chunk {
  chunk_id: $case_id + '_chunk_' + chunk.index,
  chunk_text: chunk.text,
  chunk_type: chunk.semantic_type,
  start_char: chunk.start,
  end_char: chunk.end,
  token_count: chunk.token_count,
  embedding: chunk.embedding,
  source: $source,
  extracted_at: datetime(),
  extracted_by: 'GPT-4-Chunking-v2',
  confidence_score: chunk.confidence,
  trust_score: $trust_score,
  verification_status: 'Unverified',
  version: 1,
  created_at: datetime(),
  updated_at: datetime(),
  summary: chunk.summary,
  keywords: chunk.keywords
})

// Link to source case
MATCH (case:Case {case_id: $case_id})
MATCH (c:Chunk {chunk_id: $case_id + '_chunk_' + chunk.index})
CREATE (c)-[:CHUNK_OF]->(case)
```

## RAG Query Patterns

### Pattern 1: Semantic Case Search

```cypher
// Find cases semantically similar to query
CALL db.index.vector.queryNodes('case_embedding', 10, $query_embedding)
YIELD node, score
MATCH (node)<-[:HAS_EMBEDDING]-(case:Case)
WHERE case.jurisdiction = $jurisdiction
RETURN case.title, case.citation, case.summary, score
ORDER BY score DESC
```

### Pattern 2: Statute + Application Search

```cypher
// Find statute and cases applying it
MATCH (s:Section {section_number: $section_num})
MATCH (stat:Statute)-[:CONTAINS]->(s)
OPTIONAL MATCH (case:Case)-[:APPLIES_SECTION]->(s)
RETURN stat, s, collect(case) as applications
```

### Pattern 3: Issue-Based Retrieval

```cypher
// Find cases addressing similar issues
CALL db.index.vector.queryNodes('issue_embedding', 5, $issue_embedding)
YIELD node as issue, score
MATCH (case:Case)-[:RAISES_ISSUE]->(issue)
RETURN case, issue, score
ORDER BY score DESC
```

### Pattern 4: Principle-Based Search

```cypher
// Find cases establishing a legal principle
MATCH (principle:LegalPrinciple {name: $principle_name})
MATCH (case:Case)-[:ESTABLISHES_PRINCIPLE]->(principle)
RETURN case
ORDER BY case.decision_date DESC
```

## Performance Optimization

### Index Warmup

```cypher
// Warm up vector index
CALL db.index.vector.queryNodes('embedding_vector', 1, $dummy_vector)
YIELD node
RETURN count(node)
```

### Query Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_case_context(case_id):
    # Expensive graph traversal
    return driver.execute_query(context_query, case_id=case_id)
```

### Batch Embedding Generation

```python
def batch_embed(texts, batch_size=100):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = openai.Embedding.create(
            input=batch,
            model="text-embedding-ada-002"
        )
        embeddings.extend(batch_embeddings)
    return embeddings
```

## Evaluation Metrics

### Retrieval Quality

**Precision@K**: Relevant results in top K
```python
precision_at_k = relevant_in_top_k / k
```

**Recall@K**: Coverage of relevant results
```python
recall_at_k = relevant_in_top_k / total_relevant
```

**MRR (Mean Reciprocal Rank)**:
```python
mrr = mean(1 / rank_of_first_relevant)
```

**NDCG (Normalized Discounted Cumulative Gain)**:
```python
ndcg = dcg / idcg
```

### Graph Coverage

- Embedding coverage: % of nodes with embeddings
- Citation resolution: % of citations successfully linked
- Cross-jurisdiction links: Count of inter-jurisdiction citations

## Best Practices

### Embedding Generation

1. **Use domain-specific models** when available
2. **Normalize text** before embedding
3. **Batch process** for efficiency
4. **Version embeddings** with model identifier
5. **Update periodically** as models improve

### Query Optimization

1. **Apply filters early** (jurisdiction, date)
2. **Limit graph depth** in traversals
3. **Use composite indexes** for common patterns
4. **Cache frequent queries**
5. **Monitor slow queries**

### Context Selection

1. **Balance breadth and depth**
2. **Prioritize recent precedents**
3. **Include cross-references**
4. **Add metadata** (dates, courts, outcomes)
5. **Summarize long contexts**

---

**Version**: 2.0.0 (Iteration 2)
**Last Updated**: 2025-11-11

**Iteration 2 Additions**:
- Chunk nodes for granular retrieval
- APPLIES_PRINCIPLE relationship for principle-based RAG
- Trust-based filtering for production queries
- Semantic chunking by legal document structure
