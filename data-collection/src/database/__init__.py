"""
Database package for Legal RAG System
Exports models, connection, and utilities
"""

from .connection import (
    DatabaseConnection,
    DatabaseConfig,
    get_db_connection,
    init_db,
    close_db
)

from .models import (
    Base,
    Document,
    FileStorage,
    Party,
    Judge,
    Citation,
    Content,
    DocumentChunk,
    # Enums
    DocType,
    SubjectCode,
    LegalStatus,
    EmbeddingStatus,
    StorageTier,
)

__all__ = [
    # Connection
    'DatabaseConnection',
    'DatabaseConfig',
    'get_db_connection',
    'init_db',
    'close_db',

    # Models
    'Base',
    'Document',
    'FileStorage',
    'Party',
    'Judge',
    'Citation',
    'Content',
    'DocumentChunk',

    # Enums
    'DocType',
    'SubjectCode',
    'LegalStatus',
    'EmbeddingStatus',
    'StorageTier',
]

__version__ = '2.0.0'
