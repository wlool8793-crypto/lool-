"""
Legal RAG Extraction System - Phase 3
Complete metadata extraction for legal documents
"""

__version__ = '3.0.0'

# Core extractors
from .core import PDFExtractor, HTMLExtractor, TextNormalizer

# Legal extractors
from .legal import (
    CitationExtractor,
    PartyExtractor,
    JudgeExtractor,
    DateExtractor,
    SectionExtractor
)

# Analysis extractors
from .analysis import (
    KeywordExtractor,
    SubjectClassifier,
    QualityAnalyzer
)

# Pipeline
from .pipeline import (
    ExtractionPipeline,
    extract_document,
    RetryHandler,
    MetricsCollector
)

# Integration
from .integration import (
    Phase1Integrator,
    Phase2Integrator,
    apply_naming_conventions,
    save_to_database
)

# Configuration and utilities
from .config import config, ExtractionConfig
from .exceptions import ExtractionError
from .logging_config import get_logger

__all__ = [
    # Version
    '__version__',

    # Core
    'PDFExtractor',
    'HTMLExtractor',
    'TextNormalizer',

    # Legal
    'CitationExtractor',
    'PartyExtractor',
    'JudgeExtractor',
    'DateExtractor',
    'SectionExtractor',

    # Analysis
    'KeywordExtractor',
    'SubjectClassifier',
    'QualityAnalyzer',

    # Pipeline
    'ExtractionPipeline',
    'extract_document',
    'RetryHandler',
    'MetricsCollector',

    # Integration
    'Phase1Integrator',
    'Phase2Integrator',
    'apply_naming_conventions',
    'save_to_database',

    # Config/Utils
    'config',
    'ExtractionConfig',
    'ExtractionError',
    'get_logger',
]
