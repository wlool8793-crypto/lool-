"""
Utility modules for Neo4j Legal Knowledge Graph
"""
from .error_handling import (
    neo4j_retry,
    safe_neo4j_operation,
    Neo4jTransactionContext,
    validate_json_structure,
    sanitize_neo4j_string,
    batch_operation
)

from .monitoring import (
    setup_logging,
    init_monitoring,
    PerformanceMonitor,
    Neo4jQueryProfiler,
    monitor_function,
    global_monitor
)

from .pdf_extractor import (
    PDFCaseExtractor,
    LegalCase,
    extract_pdf_to_json
)

from .embeddings_generator import (
    EmbeddingsGenerator,
    Neo4jEmbeddingsLoader,
    TextChunk,
    generate_embeddings_for_cases,
    create_chunks_with_embeddings
)

__all__ = [
    # Error handling
    'neo4j_retry',
    'safe_neo4j_operation',
    'Neo4jTransactionContext',
    'validate_json_structure',
    'sanitize_neo4j_string',
    'batch_operation',

    # Monitoring
    'setup_logging',
    'init_monitoring',
    'PerformanceMonitor',
    'Neo4jQueryProfiler',
    'monitor_function',
    'global_monitor',

    # PDF extraction
    'PDFCaseExtractor',
    'LegalCase',
    'extract_pdf_to_json',

    # Embeddings & RAG
    'EmbeddingsGenerator',
    'Neo4jEmbeddingsLoader',
    'TextChunk',
    'generate_embeddings_for_cases',
    'create_chunks_with_embeddings'
]
