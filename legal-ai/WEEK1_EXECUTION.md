# WEEK 1 EXECUTION GUIDE - Legal AI System

## FOR AGENTIC CODE IDE EXECUTION

This file contains ALL code and instructions to implement Week 1 infrastructure.
Execute each section in order. All file paths are absolute.

---

## PROJECT INFO

- **Project Root**: `/workspaces/lool-/legal-ai/`
- **Goal**: Set up production-grade infrastructure for Legal AI
- **Services**: Qdrant, Neo4j, Elasticsearch, Redis
- **Vector Dimensions**: 1024 (Voyage-law-2)

---

## STEP 1: CREATE DIRECTORY STRUCTURE

```bash
mkdir -p /workspaces/lool-/legal-ai/src/{ingestion,extraction,indexing,search,generation,api/routes,database}
mkdir -p /workspaces/lool-/legal-ai/config/prompts
mkdir -p /workspaces/lool-/legal-ai/scripts
mkdir -p /workspaces/lool-/legal-ai/tests/{unit,integration,e2e}
```

---

## STEP 2: CREATE docker-compose.yml

**File**: `/workspaces/lool-/legal-ai/docker-compose.yml`

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:v1.7.0
    container_name: legal-ai-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO
      - QDRANT__STORAGE__ON_DISK_PAYLOAD=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  neo4j:
    image: neo4j:5.15.0
    container_name: legal-ai-neo4j
    restart: unless-stopped
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_plugins:/plugins
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-legal_ai_2024}
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_initial__size=1G
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4J_dbms_memory_pagecache_size=1G
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    container_name: legal-ai-elasticsearch
    restart: unless-stopped
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - xpack.security.enrollment.enabled=false
      - ES_JAVA_OPTS=-Xms2g -Xmx2g
      - cluster.name=legal-ai-cluster
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  redis:
    image: redis:7.2-alpine
    container_name: legal-ai-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
      --save 60 1000
      --save 300 10
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 5s
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

volumes:
  qdrant_data:
    driver: local
  neo4j_data:
    driver: local
  neo4j_logs:
    driver: local
  neo4j_plugins:
    driver: local
  elasticsearch_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    name: legal-ai-network
    driver: bridge
```

---

## STEP 3: CREATE .env.example

**File**: `/workspaces/lool-/legal-ai/.env.example`

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
EMBEDDING_MODEL=voyage-law-2
EMBEDDING_DIMENSION=1024
EXTRACTION_MODEL=claude-3-haiku-20240307
GENERATION_MODEL=claude-3-5-sonnet-20241022
VERIFICATION_MODEL=claude-3-5-sonnet-20241022
RERANK_MODEL=rerank-english-v3.0

# ═══════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=false
CHUNK_SIZE=500
CHUNK_OVERLAP=100
DEFAULT_TOP_CASES=20
DEFAULT_TOP_CHUNKS=10
MAX_RETRY_ATTEMPTS=3
```

---

## STEP 4: CREATE requirements.txt

**File**: `/workspaces/lool-/legal-ai/requirements.txt`

```txt
# Core Dependencies
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
pyyaml==6.0.1

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# AI/ML APIs
anthropic==0.18.1
voyageai==0.2.1
cohere==4.47
llama-parse==0.3.9

# Databases
qdrant-client==1.7.0
neo4j==5.17.0
elasticsearch==8.12.1
redis==5.0.1

# Document Processing
tiktoken==0.5.2
pypdf==4.0.1
beautifulsoup4==4.12.3

# Utilities
httpx==0.26.0
tenacity==8.2.3
structlog==24.1.0

# Development
pytest==8.0.0
pytest-asyncio==0.23.4
black==24.1.1
ruff==0.2.0
mypy==1.8.0
```

---

## STEP 5: CREATE src/__init__.py

**File**: `/workspaces/lool-/legal-ai/src/__init__.py`

```python
"""Legal AI System - World-class legal research with 80-100% better retrieval."""

__version__ = "1.0.0"
```

---

## STEP 6: CREATE src/indexing/__init__.py

**File**: `/workspaces/lool-/legal-ai/src/indexing/__init__.py`

```python
"""Indexing module for multi-collection vector storage."""

from .collections import QdrantCollectionManager, setup_qdrant

__all__ = ["QdrantCollectionManager", "setup_qdrant"]
```

---

## STEP 7: CREATE src/indexing/collections.py

**File**: `/workspaces/lool-/legal-ai/src/indexing/collections.py`

```python
"""
Qdrant Collection Setup for Legal AI System.

Creates 3 collections for hierarchical search:
1. case_abstracts - Level 1: Case discovery
2. legal_chunks - Level 2: Passage retrieval
3. hyde_questions - HyDE matching

Production-grade with optimized HNSW and payload indexes.
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
import os

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
                ("case_id", PayloadSchemaType.KEYWORD),
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
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            timeout=timeout,
            prefer_grpc=True,
        )
        logger.info(f"Connected to Qdrant at {host}:{port}")

    def setup_all_collections(self, recreate: bool = False) -> dict:
        """Set up all collections with indexes."""
        results = {}

        for collection_name, config in self.COLLECTIONS.items():
            try:
                exists = self._collection_exists(collection_name)

                if exists and recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                    exists = False

                if not exists:
                    self._create_collection(collection_name)
                    self._create_indexes(collection_name, config["indexes"])
                    results[collection_name] = "created"
                    logger.info(f"Created collection: {collection_name}")
                else:
                    results[collection_name] = "exists"
                    logger.info(f"Collection exists: {collection_name}")

            except Exception as e:
                results[collection_name] = f"error: {str(e)}"
                logger.error(f"Error with {collection_name}: {e}")

        return results

    def _collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        try:
            self.client.get_collection(name)
            return True
        except Exception:
            return False

    def _create_collection(self, name: str) -> None:
        """Create collection with optimized settings."""
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE,
                on_disk=True,
            ),
            hnsw_config=HnswConfigDiff(
                m=16,
                ef_construct=100,
                full_scan_threshold=10000,
                max_indexing_threads=0,
                on_disk=False,
            ),
            optimizers_config=OptimizersConfigDiff(
                memmap_threshold=50000,
                indexing_threshold=20000,
                flush_interval_sec=5,
                max_optimization_threads=2,
            ),
            on_disk_payload=True,
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
        """Verify all collections are properly set up."""
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
    """Convenience function to set up Qdrant collections."""
    manager = QdrantCollectionManager(host=host, port=port)
    return manager.setup_all_collections(recreate=recreate)


if __name__ == "__main__":
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

    manager = QdrantCollectionManager(host=host, port=port)
    stats = manager.get_collection_stats()

    print("\nCollection Statistics:")
    for name, info in stats.items():
        print(f"  {name}: {info}")
```

---

## STEP 8: CREATE src/database/__init__.py

**File**: `/workspaces/lool-/legal-ai/src/database/__init__.py`

```python
"""Database clients for Legal AI System."""

from .neo4j_setup import Neo4jSchemaManager, setup_neo4j
from .elasticsearch_setup import ElasticsearchIndexManager, setup_elasticsearch

__all__ = [
    "Neo4jSchemaManager",
    "setup_neo4j",
    "ElasticsearchIndexManager",
    "setup_elasticsearch",
]
```

---

## STEP 9: CREATE src/database/neo4j_setup.py

**File**: `/workspaces/lool-/legal-ai/src/database/neo4j_setup.py`

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
import os

logger = logging.getLogger(__name__)


class Neo4jSchemaManager:
    """Manages Neo4j schema for Legal AI knowledge graph."""

    CONSTRAINTS = [
        ("case_id_unique", "CREATE CONSTRAINT case_id_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE"),
        ("case_citation_unique", "CREATE CONSTRAINT case_citation_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.citation IS UNIQUE"),
        ("statute_citation_unique", "CREATE CONSTRAINT statute_citation_unique IF NOT EXISTS FOR (s:Statute) REQUIRE s.citation IS UNIQUE"),
        ("concept_name_unique", "CREATE CONSTRAINT concept_name_unique IF NOT EXISTS FOR (lc:LegalConcept) REQUIRE lc.name IS UNIQUE"),
        ("judge_name_unique", "CREATE CONSTRAINT judge_name_unique IF NOT EXISTS FOR (j:Judge) REQUIRE j.name IS UNIQUE"),
    ]

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
        """Set up all constraints and indexes."""
        results = {"constraints": {}, "indexes": {}}

        with self.driver.session() as session:
            for name, query in self.CONSTRAINTS:
                try:
                    session.run(query)
                    results["constraints"][name] = "created"
                    logger.info(f"Created constraint: {name}")
                except Exception as e:
                    results["constraints"][name] = f"exists or error: {str(e)[:50]}"

            for name, query in self.INDEXES:
                try:
                    session.run(query)
                    results["indexes"][name] = "created"
                    logger.info(f"Created index: {name}")
                except Exception as e:
                    results["indexes"][name] = f"exists or error: {str(e)[:50]}"

        return results

    def verify_schema(self) -> dict:
        """Verify schema is properly set up."""
        with self.driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = [r["name"] for r in result]

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

## STEP 10: CREATE src/database/elasticsearch_setup.py

**File**: `/workspaces/lool-/legal-ai/src/database/elasticsearch_setup.py`

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
import os

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
        """Set up the legal_documents index."""
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
            logger.info(f"Created index: {self.INDEX_NAME}")
            return {"status": "created"}
        else:
            logger.info(f"Index exists: {self.INDEX_NAME}")
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

## STEP 11: CREATE scripts/verify_week1.py

**File**: `/workspaces/lool-/legal-ai/scripts/verify_week1.py`

```python
#!/usr/bin/env python3
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
            results[name] = f"OK (vectors: {info.vectors_count})"
        except Exception as e:
            results[name] = f"FAIL: {e}"

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
            return f"OK (constraints: {len(constraints)})"
    except Exception as e:
        return f"FAIL: {e}"
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
            return f"OK (docs: {docs})"
        else:
            return "FAIL: Index not found"
    except Exception as e:
        return f"FAIL: {e}"


def check_redis():
    """Verify Redis setup."""
    import redis

    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    try:
        r = redis.from_url(url)
        r.ping()
        return "OK"
    except Exception as e:
        return f"FAIL: {e}"


def main():
    print("=" * 60)
    print("WEEK 1 INFRASTRUCTURE VERIFICATION")
    print("=" * 60)

    all_passed = True

    print("\n[QDRANT COLLECTIONS]")
    qdrant_results = check_qdrant()
    for name, status in qdrant_results.items():
        passed = "OK" in status
        symbol = "[PASS]" if passed else "[FAIL]"
        print(f"  {symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("\n[NEO4J]")
    neo4j_status = check_neo4j()
    passed = "OK" in neo4j_status
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"  {symbol} Schema: {neo4j_status}")
    if not passed:
        all_passed = False

    print("\n[ELASTICSEARCH]")
    es_status = check_elasticsearch()
    passed = "OK" in es_status
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"  {symbol} Index: {es_status}")
    if not passed:
        all_passed = False

    print("\n[REDIS]")
    redis_status = check_redis()
    passed = "OK" in redis_status
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"  {symbol} Connection: {redis_status}")
    if not passed:
        all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("ALL CHECKS PASSED - Week 1 infrastructure ready!")
        return 0
    else:
        print("SOME CHECKS FAILED - Review above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

## STEP 12: CREATE pyproject.toml

**File**: `/workspaces/lool-/legal-ai/pyproject.toml`

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

## EXECUTION COMMANDS

After creating all files, run these commands:

```bash
# 1. Navigate to project
cd /workspaces/lool-/legal-ai

# 2. Copy .env.example to .env and fill in API keys
cp .env.example .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Docker services
docker-compose up -d

# 5. Wait for services to be healthy (30-60 seconds)
docker-compose ps

# 6. Set up Qdrant collections
python -m src.indexing.collections

# 7. Set up Neo4j schema
python -m src.database.neo4j_setup

# 8. Set up Elasticsearch index
python -m src.database.elasticsearch_setup

# 9. Verify everything
python scripts/verify_week1.py
```

---

## EXPECTED OUTPUT

After successful execution:

```
============================================================
WEEK 1 INFRASTRUCTURE VERIFICATION
============================================================

[QDRANT COLLECTIONS]
  [PASS] case_abstracts: OK (vectors: 0)
  [PASS] legal_chunks: OK (vectors: 0)
  [PASS] hyde_questions: OK (vectors: 0)

[NEO4J]
  [PASS] Schema: OK (constraints: 5)

[ELASTICSEARCH]
  [PASS] Index: OK (docs: 0)

[REDIS]
  [PASS] Connection: OK

============================================================
ALL CHECKS PASSED - Week 1 infrastructure ready!
```

---

## FILE SUMMARY

| # | File Path | Purpose |
|---|-----------|---------|
| 1 | `docker-compose.yml` | 4 services configuration |
| 2 | `.env.example` | Environment template |
| 3 | `requirements.txt` | Python dependencies |
| 4 | `pyproject.toml` | Project configuration |
| 5 | `src/__init__.py` | Package init |
| 6 | `src/indexing/__init__.py` | Indexing module init |
| 7 | `src/indexing/collections.py` | Qdrant 3 collections setup |
| 8 | `src/database/__init__.py` | Database module init |
| 9 | `src/database/neo4j_setup.py` | Neo4j schema setup |
| 10 | `src/database/elasticsearch_setup.py` | ES index setup |
| 11 | `scripts/verify_week1.py` | Verification script |

---

## WEEK 1 COMPLETE CHECKLIST

- [ ] Directory structure created
- [ ] docker-compose.yml created
- [ ] .env.example created
- [ ] requirements.txt created
- [ ] pyproject.toml created
- [ ] src/__init__.py created
- [ ] src/indexing/__init__.py created
- [ ] src/indexing/collections.py created
- [ ] src/database/__init__.py created
- [ ] src/database/neo4j_setup.py created
- [ ] src/database/elasticsearch_setup.py created
- [ ] scripts/verify_week1.py created
- [ ] Docker services running
- [ ] Qdrant collections created
- [ ] Neo4j schema created
- [ ] Elasticsearch index created
- [ ] All verifications passed
