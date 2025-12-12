"""
Core extraction modules for Legal RAG Extraction System (Phase 3)
PDF, HTML, and text processing
"""

from .pdf_extractor import PDFExtractor
from .html_extractor import HTMLExtractor
from .text_normalizer import TextNormalizer

__all__ = [
    'PDFExtractor',
    'HTMLExtractor',
    'TextNormalizer',
]
