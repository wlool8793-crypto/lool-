"""
Input/output validators for Legal RAG Extraction System (Phase 3)
Production-grade validation for all data entering and leaving the system
"""

import os
import magic
from pathlib import Path
from typing import Optional, Tuple
import chardet

from .exceptions import (
    InvalidInputError,
    InvalidFileFormatError,
    FileSizeExceededError,
    FileCorruptedError,
    PDFNotReadableError,
    PDFEncryptedError,
    ValidationError
)
from .config import config
from .logging_config import get_logger

logger = get_logger(__name__)


# ==================== File Validation ====================

def validate_pdf_file(pdf_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate PDF file before extraction.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (is_valid, error_message)

    Raises:
        ValidationError: If validation fails
    """
    try:
        path = Path(pdf_path)

        # Check file exists
        if not path.exists():
            raise InvalidInputError(f"PDF file not found: {pdf_path}")

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > config.pdf_max_file_size_mb:
            raise FileSizeExceededError(
                int(file_size_mb),
                config.pdf_max_file_size_mb
            )

        # Check file type using magic bytes
        try:
            file_type = magic.from_file(str(path), mime=True)
            if file_type not in ['application/pdf', 'application/x-pdf']:
                raise InvalidFileFormatError(
                    f"File is not a PDF: {file_type}",
                    {"detected_type": file_type, "expected_type": "application/pdf"}
                )
        except Exception as e:
            # If magic fails, try to read PDF header
            with open(path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    raise InvalidFileFormatError(
                        "File does not have PDF header",
                        {"header": header.decode('latin-1', errors='ignore')}
                    )

        # Try to open with PyPDF2 for quick validation
        try:
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                # Check if encrypted
                if reader.is_encrypted:
                    raise PDFEncryptedError(f"PDF is encrypted: {pdf_path}")

                # Check page count
                page_count = len(reader.pages)
                if page_count == 0:
                    raise FileCorruptedError("PDF has no pages")

                if page_count > config.pdf_max_pages:
                    logger.warning(
                        f"PDF has {page_count} pages, exceeds recommended {config.pdf_max_pages}"
                    )

        except PyPDF2.errors.PdfReadError as e:
            raise PDFNotReadableError(f"Cannot read PDF: {str(e)}")

        return True, None

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"PDF validation error: {e}", exc_info=True)
        raise ValidationError(f"PDF validation failed: {str(e)}")


def validate_html_content(html_content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate HTML content before extraction.

    Args:
        html_content: HTML string

    Returns:
        Tuple of (is_valid, error_message)

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Check not empty
        if not html_content or not html_content.strip():
            raise InvalidInputError("HTML content is empty")

        # Check size
        size_mb = len(html_content.encode('utf-8')) / (1024 * 1024)
        if size_mb > config.html_max_size_mb:
            raise FileSizeExceededError(
                int(size_mb),
                config.html_max_size_mb
            )

        # Check encoding
        try:
            html_content.encode('utf-8')
        except UnicodeEncodeError as e:
            # Try to detect encoding
            detected = chardet.detect(html_content.encode('latin-1', errors='ignore'))
            logger.warning(
                f"HTML encoding issue. Detected: {detected.get('encoding')}",
                extra={"detected_encoding": detected}
            )

        # Basic HTML validation (check for some HTML tags)
        html_lower = html_content.lower()
        if '<html' not in html_lower and '<body' not in html_lower and '<div' not in html_lower:
            logger.warning("HTML content may not be valid HTML (no standard tags found)")

        return True, None

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"HTML validation error: {e}", exc_info=True)
        raise ValidationError(f"HTML validation failed: {str(e)}")


# ==================== Input Validation ====================

def validate_extraction_input(
    html_content: Optional[str] = None,
    pdf_path: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate extraction input.

    Args:
        html_content: HTML content
        pdf_path: PDF file path

    Returns:
        Tuple of (is_valid, error_message)

    Raises:
        InvalidInputError: If both inputs are None
    """
    if not html_content and not pdf_path:
        raise InvalidInputError("At least one of html_content or pdf_path must be provided")

    if html_content:
        validate_html_content(html_content)

    if pdf_path:
        validate_pdf_file(pdf_path)

    return True, None


# ==================== Output Validation ====================

def validate_citation(citation_data: dict) -> bool:
    """
    Validate citation data.

    Args:
        citation_data: Citation dictionary

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    required_fields = ['citation_text', 'citation_encoded', 'year', 'reporter', 'page']

    for field in required_fields:
        if field not in citation_data:
            raise ValidationError(f"Citation missing required field: {field}")

    # Validate year
    year = citation_data.get('year')
    if not isinstance(year, int) or year < 1800 or year > 2100:
        raise ValidationError(f"Invalid citation year: {year}")

    # Validate page
    page = citation_data.get('page')
    if not isinstance(page, int) or page < 1:
        raise ValidationError(f"Invalid citation page: {page}")

    # Validate confidence if present
    if 'confidence' in citation_data:
        conf = citation_data['confidence']
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            raise ValidationError(f"Invalid citation confidence: {conf}")

    return True


def validate_party(party_data: dict) -> bool:
    """
    Validate party data.

    Args:
        party_data: Party dictionary

    Returns:
        True if valid
    """
    required_fields = ['party_type', 'party_name', 'party_name_abbr', 'party_order']

    for field in required_fields:
        if field not in party_data:
            raise ValidationError(f"Party missing required field: {field}")

    # Validate party_order
    order = party_data.get('party_order')
    if not isinstance(order, int) or order < 1:
        raise ValidationError(f"Invalid party order: {order}")

    return True


def validate_quality_score(quality_score: float) -> bool:
    """
    Validate quality score.

    Args:
        quality_score: Quality score (0.0-1.0)

    Returns:
        True if valid
    """
    if not isinstance(quality_score, (int, float)):
        raise ValidationError(f"Quality score must be numeric: {type(quality_score)}")

    if quality_score < 0.0 or quality_score > 1.0:
        raise ValidationError(f"Quality score must be 0.0-1.0: {quality_score}")

    return True


def validate_extraction_output(result: dict) -> bool:
    """
    Validate complete extraction output.

    Args:
        result: Complete extraction result dictionary

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Check status
    if 'status' not in result:
        raise ValidationError("Extraction result missing 'status' field")

    valid_statuses = ['success', 'partial', 'failed']
    if result['status'] not in valid_statuses:
        raise ValidationError(f"Invalid status: {result['status']}")

    # If citations present, validate each
    if 'citations' in result and result['citations']:
        for citation in result['citations']:
            validate_citation(citation)

    # If parties present, validate each
    if 'parties' in result and result['parties']:
        for party in result['parties']:
            validate_party(party)

    # If quality score present, validate
    if 'data_quality_score' in result:
        validate_quality_score(result['data_quality_score'])

    return True


# ==================== Security Validation ====================

def check_for_malicious_content(file_path: str) -> bool:
    """
    Basic security check for malicious content.

    Args:
        file_path: Path to file

    Returns:
        True if safe, False if suspicious
    """
    try:
        path = Path(file_path)

        # Check for suspicious extensions
        suspicious_extensions = ['.exe', '.dll', '.bat', '.sh', '.cmd', '.com', '.scr']
        if path.suffix.lower() in suspicious_extensions:
            logger.warning(f"Suspicious file extension: {path.suffix}")
            return False

        # Check for null bytes (potential path traversal)
        if '\x00' in str(path):
            logger.warning("Null byte detected in file path")
            return False

        # Check for path traversal
        if '..' in str(path):
            logger.warning("Path traversal attempt detected")
            return False

        return True

    except Exception as e:
        logger.error(f"Security check error: {e}", exc_info=True)
        return False
