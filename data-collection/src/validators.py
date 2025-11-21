"""
Validators Module
Centralized validation functions for PDFs, URLs, and data.
Provides consistent validation logic across the application.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class PDFValidator:
    """Validator for PDF files."""

    # PDF file signature (magic number)
    PDF_SIGNATURE = b'%PDF'

    # Common PDF version signatures
    PDF_VERSIONS = [b'%PDF-1.0', b'%PDF-1.1', b'%PDF-1.2', b'%PDF-1.3',
                    b'%PDF-1.4', b'%PDF-1.5', b'%PDF-1.6', b'%PDF-1.7', b'%PDF-2.0']

    # Minimum valid PDF size (1KB)
    MIN_SIZE = 1024

    @classmethod
    def validate_header(cls, file_path: str) -> bool:
        """
        Validate PDF file header.

        Args:
            file_path: Path to the PDF file

        Returns:
            True if valid PDF header, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != cls.PDF_SIGNATURE:
                    logger.warning(f"Invalid PDF signature: {header} (expected {cls.PDF_SIGNATURE})")
                    return False
            return True

        except Exception as e:
            logger.error(f"Error validating PDF header for {file_path}: {e}")
            return False

    @classmethod
    def validate_size(cls, file_path: str, min_size: Optional[int] = None) -> bool:
        """
        Validate PDF file size.

        Args:
            file_path: Path to the PDF file
            min_size: Minimum file size in bytes (uses default if None)

        Returns:
            True if size is valid, False otherwise
        """
        min_size = min_size or cls.MIN_SIZE

        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            file_size = os.path.getsize(file_path)

            if file_size < min_size:
                logger.warning(f"PDF too small: {file_size} bytes < {min_size} bytes")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating PDF size for {file_path}: {e}")
            return False

    @classmethod
    def validate_file(
        cls,
        file_path: str,
        check_header: bool = True,
        check_size: bool = True,
        min_size: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive PDF file validation.

        Args:
            file_path: Path to the PDF file
            check_header: Whether to check PDF header
            check_size: Whether to check file size
            min_size: Minimum file size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Check file size
        if check_size:
            if not cls.validate_size(file_path, min_size):
                file_size = os.path.getsize(file_path)
                min_size = min_size or cls.MIN_SIZE
                return False, f"File too small: {file_size} bytes < {min_size} bytes"

        # Check PDF header
        if check_header:
            if not cls.validate_header(file_path):
                return False, "Invalid PDF header"

        return True, None

    @classmethod
    def is_valid_pdf(cls, file_path: str, min_size: Optional[int] = None) -> bool:
        """
        Quick check if file is a valid PDF.

        Args:
            file_path: Path to the PDF file
            min_size: Minimum file size in bytes

        Returns:
            True if valid PDF, False otherwise
        """
        is_valid, _ = cls.validate_file(file_path, min_size=min_size)
        return is_valid


class URLValidator:
    """Validator for URLs."""

    # IndianKanoon URL patterns
    INDIANKANOON_DOC_PATTERN = re.compile(r'/doc/\d+/?')
    INDIANKANOON_DOCFRAGMENT_PATTERN = re.compile(r'/docfragment/\d+/?')

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        Validate if string is a valid URL.

        Args:
            url: URL string

        Returns:
            True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @classmethod
    def is_indiankanoon_url(cls, url: str) -> bool:
        """
        Check if URL is from IndianKanoon.org.

        Args:
            url: URL string

        Returns:
            True if IndianKanoon URL, False otherwise
        """
        try:
            result = urlparse(url)
            return 'indiankanoon' in result.netloc.lower()
        except Exception:
            return False

    @classmethod
    def is_doc_url(cls, url: str) -> bool:
        """
        Check if URL is an IndianKanoon document URL.

        Args:
            url: URL string

        Returns:
            True if document URL, False otherwise
        """
        return bool(cls.INDIANKANOON_DOC_PATTERN.search(url) or
                   cls.INDIANKANOON_DOCFRAGMENT_PATTERN.search(url))

    @classmethod
    def extract_doc_id(cls, url: str) -> Optional[str]:
        """
        Extract document ID from IndianKanoon URL.

        Args:
            url: IndianKanoon URL

        Returns:
            Document ID or None if not found
        """
        try:
            # Try /doc/ pattern
            match = cls.INDIANKANOON_DOC_PATTERN.search(url)
            if match:
                doc_id = match.group().split('/doc/')[1].strip('/').split('?')[0]
                return doc_id

            # Try /docfragment/ pattern
            match = cls.INDIANKANOON_DOCFRAGMENT_PATTERN.search(url)
            if match:
                doc_id = match.group().split('/docfragment/')[1].strip('/').split('?')[0]
                return doc_id

            return None

        except Exception as e:
            logger.error(f"Error extracting doc ID from URL {url}: {e}")
            return None

    @classmethod
    def validate_url(
        cls,
        url: str,
        must_be_indiankanoon: bool = False,
        must_be_doc: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive URL validation.

        Args:
            url: URL to validate
            must_be_indiankanoon: URL must be from IndianKanoon
            must_be_doc: URL must be a document URL

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if valid URL
        if not cls.is_valid_url(url):
            return False, "Invalid URL format"

        # Check if IndianKanoon URL
        if must_be_indiankanoon and not cls.is_indiankanoon_url(url):
            return False, "Not an IndianKanoon URL"

        # Check if document URL
        if must_be_doc and not cls.is_doc_url(url):
            return False, "Not a valid document URL"

        return True, None


class DataValidator:
    """Validator for data and inputs."""

    @staticmethod
    def validate_year(year: int, min_year: int = 1900, max_year: int = 2100) -> bool:
        """
        Validate year value.

        Args:
            year: Year to validate
            min_year: Minimum valid year
            max_year: Maximum valid year

        Returns:
            True if valid year, False otherwise
        """
        return min_year <= year <= max_year

    @staticmethod
    def validate_year_range(start_year: int, end_year: int) -> Tuple[bool, Optional[str]]:
        """
        Validate year range.

        Args:
            start_year: Start year
            end_year: End year

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not DataValidator.validate_year(start_year):
            return False, f"Invalid start year: {start_year}"

        if not DataValidator.validate_year(end_year):
            return False, f"Invalid end year: {end_year}"

        if start_year > end_year:
            return False, f"Start year ({start_year}) must be <= end year ({end_year})"

        return True, None

    @staticmethod
    def validate_positive_int(value: int, name: str = "value") -> Tuple[bool, Optional[str]]:
        """
        Validate that value is a positive integer.

        Args:
            value: Value to validate
            name: Name of the value (for error message)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, int):
            return False, f"{name} must be an integer"

        if value <= 0:
            return False, f"{name} must be positive (got {value})"

        return True, None

    @staticmethod
    def validate_non_negative_number(
        value: float,
        name: str = "value"
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that value is a non-negative number.

        Args:
            value: Value to validate
            name: Name of the value (for error message)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, f"{name} must be a number"

        if value < 0:
            return False, f"{name} must be non-negative (got {value})"

        return True, None

    @staticmethod
    def validate_directory(path: str, create: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate directory path.

        Args:
            path: Directory path
            create: Create directory if it doesn't exist

        Returns:
            Tuple of (is_valid, error_message)
        """
        dir_path = Path(path)

        if dir_path.exists():
            if not dir_path.is_dir():
                return False, f"Path exists but is not a directory: {path}"
            return True, None

        if create:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                return True, None
            except Exception as e:
                return False, f"Failed to create directory {path}: {e}"

        return False, f"Directory does not exist: {path}"


def validate_pdf_file(
    file_path: str,
    check_header: bool = True,
    check_size: bool = True,
    min_size: int = 1024
) -> bool:
    """
    Convenience function to validate PDF file.

    Args:
        file_path: Path to PDF file
        check_header: Check PDF header
        check_size: Check file size
        min_size: Minimum file size in bytes

    Returns:
        True if valid, False otherwise
    """
    return PDFValidator.is_valid_pdf(file_path, min_size=min_size)


def validate_url(
    url: str,
    must_be_indiankanoon: bool = False,
    must_be_doc: bool = False
) -> bool:
    """
    Convenience function to validate URL.

    Args:
        url: URL to validate
        must_be_indiankanoon: Must be IndianKanoon URL
        must_be_doc: Must be document URL

    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = URLValidator.validate_url(url, must_be_indiankanoon, must_be_doc)
    return is_valid
