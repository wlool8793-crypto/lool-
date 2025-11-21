# Legal Knowledge Graph - Quickstart Guide

## Overview

This guide will help you set up and start using the Legal Knowledge Graph schema in under 30 minutes.

## Prerequisites

- Neo4j 5.11+ (for vector search support)
- 8GB+ RAM recommended
- Python 3.8+ (for data ingestion)
- OpenAI API key (for embeddings) or alternative embedding service

## Step 1: Install Neo4j

### Option A: Neo4j Desktop
1. Download from https://neo4j.com/download/
2. Create new project
3. Create database (name: `legal-knowledge-graph`)
4. Set initial password
5. Start database

### Option B: Docker
```bash
docker run \
  --name neo4j-legal \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.13-enterprise
```

### Option C: Neo4j AuraDB
1. Go to https://console.neo4j.io
2. Create new instance
3. Save connection credentials

## Step 2: Create Schema

### Run Constraints and Indexes

```bash
# Connect to Neo4j
cypher-shell -u neo4j -p your-password

# Run schema creation script
:source schema/cypher/create_schema.cypher
```

Or use Python:
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "your-password")
)

with driver.session() as session:
    # Read and execute constraints
    with open('schema/constraints/constraints.cypher', 'r') as f:
        constraints = f.read()
        for constraint in constraints.split(';'):
            if constraint.strip():
                session.run(constraint)

    # Read and execute indexes
    with open('schema/indexes/indexes.cypher', 'r') as f:
        indexes = f.read()
        for index in indexes.split(';'):
            if index.strip():
                session.run(index)
```

### Verify Schema

```cypher
// Check constraints
SHOW CONSTRAINTS;

// Check indexes
SHOW INDEXES;

// Should see:
// - 18 unique constraints
// - 50+ indexes (property, composite, fulltext, vector)
```

## Step 3: Load Sample Data

```bash
# Load sample data
cypher-shell -u neo4j -p your-password \
  < schema/cypher/sample_data.cypher
```

This creates:
- 3 jurisdictions (BD, IN, PK)
- 4 legal domains
- 2 courts
- 3 statutes
- 3 sections
- 2 judges
- 2 legal principles
- 2 parties
- 2 cases with full relationships

### Verify Data Load

```cypher
// Count nodes by type
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC;

// Should show:
// Jurisdiction: 3
// LegalDomain: 4
// Court: 2
// Statute: 3
// Section: 3
// Judge: 2
// Case: 2
// etc.
```

## Step 4: Run Sample Queries

### Query 1: Find All Cases

```cypher
MATCH (c:Case)
RETURN c.title, c.citation, c.decision_date, c.jurisdiction
ORDER BY c.decision_date DESC;
```

### Query 2: Explore Precedent Chain

```cypher
MATCH (c1:Case {case_id: 'CASE-BD-SC-2023-001'})
MATCH path = (c1)-[:CITES*1..2]->(c2:Case)
RETURN path;
```

### Query 3: Find Statutes in Jurisdiction

```cypher
MATCH (s:Statute {jurisdiction: 'BD'})
MATCH (s)-[:CONTAINS]->(sec:Section)
RETURN s.name, collect(sec.section_number) as sections
ORDER BY s.name;
```

### Query 4: Cases by Legal Domain

```cypher
MATCH (c:Case)-[:BELONGS_TO_DOMAIN]->(d:LegalDomain {name: 'Criminal Law'})
RETURN c.title, c.citation, c.decision_date
ORDER BY c.decision_date DESC;
```

## Step 5: Generate Embeddings

### Install Dependencies

```bash
pip install openai neo4j tiktoken
```

### Create Embeddings Script

```python
import openai
from neo4j import GraphDatabase

openai.api_key = "your-api-key"

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "your-password")
)

def generate_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def embed_cases():
    with driver.session() as session:
        # Get all cases without embeddings
        result = session.run("""
            MATCH (c:Case)
            WHERE c.embedding IS NULL
            RETURN c.case_id as id, c.summary as text
        """)

        for record in result:
            case_id = record['id']
            text = record['text'] or ''

            if text:
                embedding = generate_embedding(text)

                # Update case with embedding
                session.run("""
                    MATCH (c:Case {case_id: $case_id})
                    SET c.embedding = $embedding
                """, case_id=case_id, embedding=embedding)

                print(f"Embedded: {case_id}")

embed_cases()
```

## Step 6: Perform Hybrid Search

### Vector Search

```cypher
// Find semantically similar cases
MATCH (c:Case)
WHERE c.embedding IS NOT NULL
CALL db.index.vector.queryNodes('case_embedding', 5, $query_embedding)
YIELD node, score
RETURN node.title, node.citation, score
ORDER BY score DESC;
```

### Keyword Search

```cypher
// Full-text search
CALL db.index.fulltext.queryNodes('case_fulltext', 'murder death penalty')
YIELD node, score
RETURN node.title, node.citation, score
ORDER BY score DESC;
```

### Combined Hybrid Search

```cypher
// Vector + keyword + filters
CALL db.index.vector.queryNodes('case_embedding', 10, $query_embedding)
YIELD node as case, score as vector_score
WHERE case.jurisdiction = 'BD'
AND case.case_type = 'Criminal'
CALL db.index.fulltext.queryNodes('case_fulltext', $query_text)
YIELD node as case2, score as text_score
WHERE case = case2
RETURN case.title,
       case.citation,
       (0.6 * vector_score + 0.4 * text_score) as combined_score
ORDER BY combined_score DESC
LIMIT 5;
```

## Step 7: Temporal Queries

### Point-in-Time Query

```cypher
// What did Section 302 say on 2020-01-01?
MATCH (v:Version)-[:VERSION_OF]->(s:Section {section_number: '302'})
WHERE v.valid_from <= date('2020-01-01')
AND (v.valid_to IS NULL OR v.valid_to > date('2020-01-01'))
RETURN v.content as text_on_date;
```

### Amendment History

```cypher
// Get amendment history
MATCH (s:Section {section_number: '302'})
MATCH (v:Version)-[:VERSION_OF]->(s)
RETURN v.version_number,
       v.valid_from,
       v.valid_to,
       v.change_summary
ORDER BY v.version_number;
```

## Step 8: RAG Integration

### Python RAG Pipeline

```python
from neo4j import GraphDatabase
import openai

class LegalRAG:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def search(self, query, jurisdiction='BD', top_k=5):
        # Generate query embedding
        embedding = self.generate_embedding(query)

        # Hybrid search
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('case_embedding', $top_k, $embedding)
                YIELD node as case, score as vector_score
                WHERE case.jurisdiction = $jurisdiction

                // Get full context
                OPTIONAL MATCH (case)-[:APPLIES_SECTION]->(sec:Section)
                OPTIONAL MATCH (case)-[:CITES]->(cited:Case)

                RETURN case.title,
                       case.summary,
                       case.citation,
                       collect(DISTINCT sec.text) as sections,
                       collect(DISTINCT cited.title) as citations,
                       vector_score
                ORDER BY vector_score DESC
                LIMIT $top_k
            """, top_k=top_k, embedding=embedding, jurisdiction=jurisdiction)

            return [dict(record) for record in result]

    def generate_embedding(self, text):
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

    def generate_answer(self, query, context):
        prompt = f"""Based on the following legal context, answer the query.

Context:
{context}

Query: {query}

Answer:"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

# Usage
rag = LegalRAG("bolt://localhost:7687", "neo4j", "password")

# Search
results = rag.search("What is the punishment for murder in Bangladesh?")

# Format context
context = "\n\n".join([
    f"{r['case.title']}: {r['case.summary']}"
    for r in results
])

# Generate answer
answer = rag.generate_answer(
    "What is the punishment for murder in Bangladesh?",
    context
)

print(answer)
```

## Common Use Cases

### Use Case 1: Find Similar Cases

```cypher
MATCH (target:Case {case_id: $case_id})
MATCH (similar:Case)
WHERE similar <> target
  AND similar.jurisdiction = target.jurisdiction
  AND similar.case_type = target.case_type
CALL db.index.vector.queryNodes('case_embedding', 10, target.embedding)
YIELD node, score
WHERE node = similar
RETURN similar.title, similar.citation, score
ORDER BY score DESC
LIMIT 5;
```

### Use Case 2: Trace Precedent Chain

```cypher
MATCH path = (start:Case {case_id: $case_id})-[:CITES*1..5]->(end:Case)
WHERE ALL(r IN relationships(path) WHERE r.treatment = 'Positive')
RETURN path
ORDER BY length(path) DESC
LIMIT 10;
```

### Use Case 3: Find Applicable Statutes

```cypher
MATCH (issue:LegalIssue {description: $issue_description})
MATCH (case:Case)-[:RAISES_ISSUE]->(issue)
MATCH (case)-[:APPLIES_SECTION]->(sec:Section)
MATCH (statute:Statute)-[:CONTAINS]->(sec)
RETURN DISTINCT statute.name,
       collect(DISTINCT sec.section_number) as sections,
       count(DISTINCT case) as case_count
ORDER BY case_count DESC;
```

## Next Steps

1. **Load Your Data**: Import your own cases, statutes, and judgments
2. **Customize Schema**: Add jurisdiction-specific node types
3. **Optimize Queries**: Create custom indexes for your query patterns
4. **Build API**: Create GraphQL or REST API on top
5. **Deploy**: Production deployment with clustering and backups

## Troubleshooting

### Vector Search Not Working

```cypher
// Check if vector index exists
SHOW INDEXES WHERE type = 'VECTOR';

// If missing, create it
CREATE VECTOR INDEX case_embedding IF NOT EXISTS
FOR (c:Case) ON (c.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
```

### Slow Queries

```cypher
// Add missing indexes
CREATE INDEX case_jurisdiction_type IF NOT EXISTS
FOR (c:Case) ON (c.jurisdiction, c.case_type);

// Use EXPLAIN to analyze
EXPLAIN MATCH (c:Case {jurisdiction: 'BD'})
WHERE c.case_type = 'Criminal'
RETURN c;
```

### Out of Memory

```conf
# neo4j.conf
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=8g
dbms.memory.pagecache.size=4g
```

## Resources

- **Schema Documentation**: See `docs/schema_design.md`
- **RAG Guide**: See `docs/rag_optimization.md`
- **Temporal Queries**: See `docs/temporal_design.md`
- **Multi-Jurisdiction**: See `docs/multi_jurisdiction.md`
- **Neo4j Documentation**: https://neo4j.com/docs/

---

**Need Help?**
- Check the documentation in `/docs`
- Review sample queries in `/schema/cypher`
- Examine test cases in `/tests`

**Version**: 1.0.0
**Last Updated**: 2025-11-11
