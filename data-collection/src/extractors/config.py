"""
Configuration for Legal RAG Extraction System (Phase 3)
Production-grade configuration with Pydantic validation
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pathlib import Path


class ExtractionConfig(BaseSettings):
    """
    Production extraction configuration.

    All settings can be overridden via environment variables with EXTRACT_ prefix.
    Example: EXTRACT_MIN_QUALITY_SCORE=0.8
    """

    # ==================== Quality Thresholds ====================
    min_quality_score: float = Field(
        default=0.70,
        description="Minimum overall quality score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    citation_confidence_threshold: float = Field(
        default=0.90,
        description="Minimum citation confidence for 'valid' status",
        ge=0.0,
        le=1.0
    )

    party_confidence_threshold: float = Field(
        default=0.85,
        description="Minimum party extraction confidence",
        ge=0.0,
        le=1.0
    )

    # ==================== Retry Configuration ====================
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed extractions",
        ge=0,
        le=10
    )

    retry_delay: float = Field(
        default=1.0,
        description="Initial delay between retries (seconds)",
        ge=0.0
    )

    retry_backoff: float = Field(
        default=2.0,
        description="Exponential backoff multiplier",
        ge=1.0
    )

    # ==================== PDF Extraction ====================
    pdf_max_pages: int = Field(
        default=1000,
        description="Maximum PDF pages to process",
        ge=1
    )

    pdf_max_file_size_mb: int = Field(
        default=100,
        description="Maximum PDF file size in MB",
        ge=1
    )

    pdf_fallback_engines: List[str] = Field(
        default=['pdfplumber', 'PyPDF2', 'pdfminer'],
        description="PDF extraction engines in fallback order"
    )

    enable_ocr: bool = Field(
        default=True,
        description="Enable OCR for scanned PDFs"
    )

    ocr_confidence_threshold: float = Field(
        default=0.60,
        description="Minimum OCR confidence to use OCR text",
        ge=0.0,
        le=1.0
    )

    # ==================== HTML Extraction ====================
    html_max_size_mb: int = Field(
        default=10,
        description="Maximum HTML content size in MB",
        ge=1
    )

    html_timeout_seconds: int = Field(
        default=30,
        description="Timeout for HTML parsing",
        ge=1
    )

    # ==================== Text Normalization ====================
    normalize_unicode: bool = Field(
        default=True,
        description="Apply Unicode normalization (NFKC)"
    )

    expand_ligatures: bool = Field(
        default=True,
        description="Expand ligatures (ﬁ → fi)"
    )

    normalize_quotes: bool = Field(
        default=True,
        description="Convert smart quotes to ASCII"
    )

    # ==================== Extraction Behavior ====================
    skip_on_error: bool = Field(
        default=True,
        description="Skip document on error instead of raising exception"
    )

    save_partial_results: bool = Field(
        default=True,
        description="Save partial results even if extraction is incomplete"
    )

    enable_progress_tracking: bool = Field(
        default=True,
        description="Enable progress callbacks for batch processing"
    )

    # ==================== Performance ====================
    enable_caching: bool = Field(
        default=True,
        description="Enable pattern file caching"
    )

    cache_size: int = Field(
        default=128,
        description="LRU cache size for patterns",
        ge=0
    )

    parallel_extraction: bool = Field(
        default=True,
        description="Enable parallel extraction where possible"
    )

    max_workers: int = Field(
        default=4,
        description="Maximum parallel workers",
        ge=1,
        le=16
    )

    # ==================== Paths ====================
    pattern_dir: str = Field(
        default='src/extractors/patterns',
        description="Directory containing pattern YAML files"
    )

    log_dir: str = Field(
        default='logs',
        description="Directory for log files"
    )

    cache_dir: str = Field(
        default='data/cache',
        description="Directory for caching"
    )

    # ==================== Keyword Extraction ====================
    keyword_max_features: int = Field(
        default=20,
        description="Maximum keywords to extract per document",
        ge=1,
        le=100
    )

    keyword_min_frequency: int = Field(
        default=2,
        description="Minimum keyword frequency",
        ge=1
    )

    # ==================== Subject Classification ====================
    subject_min_confidence: float = Field(
        default=0.70,
        description="Minimum confidence for subject classification",
        ge=0.0,
        le=1.0
    )

    enable_ml_classifier: bool = Field(
        default=True,
        description="Enable ML-based subject classifier"
    )

    use_ensemble: bool = Field(
        default=True,
        description="Use ensemble (rule-based + ML) for subject classification"
    )

    # ==================== Validators ====================
    @field_validator('pattern_dir', 'log_dir', 'cache_dir')
    @classmethod
    def validate_directory(cls, v):
        """Ensure directory exists or can be created"""
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @field_validator('pdf_fallback_engines')
    @classmethod
    def validate_pdf_engines(cls, v):
        """Ensure at least one PDF engine specified"""
        if not v:
            raise ValueError("At least one PDF extraction engine must be specified")
        valid_engines = {'pdfplumber', 'PyPDF2', 'pdfminer', 'tesseract'}
        for engine in v:
            if engine not in valid_engines:
                raise ValueError(f"Invalid PDF engine: {engine}. Must be one of {valid_engines}")
        return v

    model_config = {
        "env_prefix": "EXTRACT_",
        "case_sensitive": False
    }


# Global config instance
config = ExtractionConfig()
