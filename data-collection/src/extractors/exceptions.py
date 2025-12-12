"""
Custom exceptions for Legal RAG Extraction System (Phase 3)
Comprehensive error hierarchy for production-grade error handling
"""

from typing import Optional, Dict, Any


class ExtractionError(Exception):
    """Base exception for all extraction errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ==================== Input Validation Errors ====================

class ValidationError(ExtractionError):
    """Base validation error"""
    pass


class InvalidInputError(ValidationError):
    """Input data is invalid"""
    pass


class InvalidFileFormatError(ValidationError):
    """File format is not supported"""
    pass


class FileSizeExceededError(ValidationError):
    """File size exceeds maximum allowed"""

    def __init__(self, actual_size: int, max_size: int):
        super().__init__(
            f"File size {actual_size}MB exceeds maximum {max_size}MB",
            {"actual_size_mb": actual_size, "max_size_mb": max_size}
        )


class FileCorruptedError(ValidationError):
    """File is corrupted or unreadable"""
    pass


# ==================== PDF Extraction Errors ====================

class PDFExtractionError(ExtractionError):
    """PDF extraction failed"""
    pass


class PDFNotReadableError(PDFExtractionError):
    """PDF file cannot be read"""
    pass


class PDFEncryptedError(PDFExtractionError):
    """PDF is encrypted"""
    pass


class PDFPageLimitExceededError(PDFExtractionError):
    """PDF has too many pages"""

    def __init__(self, actual_pages: int, max_pages: int):
        super().__init__(
            f"PDF has {actual_pages} pages, exceeds maximum {max_pages}",
            {"actual_pages": actual_pages, "max_pages": max_pages}
        )


class OCRError(PDFExtractionError):
    """OCR processing failed"""
    pass


# ==================== Legal Extraction Errors ====================

class CitationExtractionError(ExtractionError):
    """Citation extraction failed"""
    pass


class NoCitationFoundError(CitationExtractionError):
    """No citations found in document"""
    pass


class InvalidCitationFormatError(CitationExtractionError):
    """Citation format is invalid"""
    pass


class PartyExtractionError(ExtractionError):
    """Party extraction failed"""
    pass


class NoPartiesFoundError(PartyExtractionError):
    """No parties found in document"""
    pass


class JudgeExtractionError(ExtractionError):
    """Judge extraction failed"""
    pass


class DateExtractionError(ExtractionError):
    """Date extraction failed"""
    pass


class InvalidDateFormatError(DateExtractionError):
    """Date format is invalid"""
    pass


class SectionExtractionError(ExtractionError):
    """Section/statute extraction failed"""
    pass


# ==================== Analysis Errors ====================

class AnalysisError(ExtractionError):
    """Base analysis error"""
    pass


class KeywordExtractionError(AnalysisError):
    """Keyword extraction failed"""
    pass


class SubjectClassificationError(AnalysisError):
    """Subject classification failed"""
    pass


class QualityAnalysisError(AnalysisError):
    """Quality analysis failed"""
    pass


class QualityThresholdError(QualityAnalysisError):
    """Quality score below threshold"""

    def __init__(self, score: float, threshold: float):
        super().__init__(
            f"Quality score {score:.2f} below threshold {threshold:.2f}",
            {"score": score, "threshold": threshold}
        )
        self.score = score
        self.threshold = threshold


# ==================== Pipeline Errors ====================

class PipelineError(ExtractionError):
    """Pipeline execution error"""
    pass


class StageFailedError(PipelineError):
    """Extraction stage failed"""

    def __init__(self, stage_name: str, original_error: Exception):
        super().__init__(
            f"Stage '{stage_name}' failed: {str(original_error)}",
            {"stage": stage_name, "error_type": type(original_error).__name__}
        )
        self.stage_name = stage_name
        self.original_error = original_error


class RetryExhaustedError(PipelineError):
    """Maximum retries exceeded"""

    def __init__(self, attempts: int, last_error: Exception):
        super().__init__(
            f"Retry exhausted after {attempts} attempts: {str(last_error)}",
            {"attempts": attempts, "last_error_type": type(last_error).__name__}
        )
        self.attempts = attempts
        self.last_error = last_error


class CircuitBreakerOpenError(PipelineError):
    """Circuit breaker is open, blocking requests"""

    def __init__(self, error_rate: float, threshold: float):
        super().__init__(
            f"Circuit breaker open: error rate {error_rate:.2%} exceeds {threshold:.2%}",
            {"error_rate": error_rate, "threshold": threshold}
        )


# ==================== Configuration Errors ====================

class ConfigurationError(ExtractionError):
    """Configuration error"""
    pass


class PatternFileNotFoundError(ConfigurationError):
    """Pattern file not found"""

    def __init__(self, pattern_file: str):
        super().__init__(
            f"Pattern file not found: {pattern_file}",
            {"pattern_file": pattern_file}
        )


class InvalidPatternError(ConfigurationError):
    """Pattern format is invalid"""
    pass


# ==================== Integration Errors ====================

class IntegrationError(ExtractionError):
    """Integration with Phase 1/2 failed"""
    pass


class Phase1IntegrationError(IntegrationError):
    """Phase 1 (naming) integration failed"""
    pass


class Phase2IntegrationError(IntegrationError):
    """Phase 2 (database) integration failed"""
    pass


# ==================== Utility Functions ====================

def is_transient_error(error: Exception) -> bool:
    """
    Determine if error is transient (should retry) or permanent.

    Transient errors:
    - Network timeouts
    - Temporary file locks
    - OCR failures

    Permanent errors:
    - File not found
    - Invalid format
    - Corrupted files
    """
    transient_types = (
        OCRError,
        RetryExhaustedError,
    )

    permanent_types = (
        InvalidInputError,
        InvalidFileFormatError,
        FileCorruptedError,
        PDFEncryptedError,
        PatternFileNotFoundError,
        InvalidPatternError,
    )

    if isinstance(error, permanent_types):
        return False

    if isinstance(error, transient_types):
        return True

    # Default: transient (allow retry)
    return True


def categorize_error(error: Exception) -> str:
    """
    Categorize error for logging and metrics.

    Returns:
        Category string: 'validation', 'extraction', 'analysis', 'pipeline', 'config', 'integration', 'unknown'
    """
    if isinstance(error, ValidationError):
        return 'validation'
    elif isinstance(error, (PDFExtractionError, CitationExtractionError, PartyExtractionError,
                            JudgeExtractionError, DateExtractionError, SectionExtractionError)):
        return 'extraction'
    elif isinstance(error, AnalysisError):
        return 'analysis'
    elif isinstance(error, PipelineError):
        return 'pipeline'
    elif isinstance(error, ConfigurationError):
        return 'config'
    elif isinstance(error, IntegrationError):
        return 'integration'
    else:
        return 'unknown'
