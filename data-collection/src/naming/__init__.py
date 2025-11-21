"""
Universal Naming System for Legal Documents
World-Class Legal RAG System

Components:
- EnhancedNamer: Main filename generator
- FilenameParser: Parse filenames to metadata
- CitationEncoder: Encode/decode legal citations
- PartyAbbreviator: Abbreviate party names
- DocnumGenerator: Generate document numbers
- HashGenerator: Generate content hashes
"""

# Legacy imports (for backward compatibility)
from .universal_namer import UniversalNamer
from .id_generator import IDGenerator

# Enhanced naming system
from .constants import (
    COUNTRY_CODES, DOC_TYPE_NAMES, COURT_CODES, SUBJECT_NAMES, STATUS_NAMES,
    LANGUAGE_CODES, SUBJECT_KEYWORDS, REPORTER_CODES, PARTY_ABBREVIATIONS,
    MAX_FILENAME_LENGTH, MAX_IDENTIFIER_LENGTH, MAX_DOCNUM_LENGTH, HASH_LENGTH,
    DocType, SubjectCode, LegalStatus
)
from .hash_generator import HashGenerator
from .citation_encoder import CitationEncoder, CitationComponents
from .party_abbreviator import PartyAbbreviator
from .docnum_generator import DocnumGenerator
from .enhanced_namer import (
    EnhancedNamer, DocumentMetadata, FilenameComponents,
    generate_filename, validate_filename, generate_global_id
)
from .filename_parser import FilenameParser, parse_filename, extract_metadata

__all__ = [
    # Legacy
    'UniversalNamer',
    'IDGenerator',

    # Enhanced naming
    'EnhancedNamer',
    'DocumentMetadata',
    'FilenameComponents',
    'FilenameParser',
    'CitationEncoder',
    'CitationComponents',
    'PartyAbbreviator',
    'DocnumGenerator',
    'HashGenerator',

    # Convenience functions
    'generate_filename',
    'validate_filename',
    'generate_global_id',
    'parse_filename',
    'extract_metadata',

    # Constants
    'COUNTRY_CODES',
    'DOC_TYPE_NAMES',
    'COURT_CODES',
    'SUBJECT_NAMES',
    'STATUS_NAMES',
    'LANGUAGE_CODES',
    'REPORTER_CODES',

    # Enums
    'DocType',
    'SubjectCode',
    'LegalStatus',
]

__version__ = '2.0.0'
