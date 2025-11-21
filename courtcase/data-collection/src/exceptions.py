"""
Custom Exception Hierarchy for IndianKanoon Data Collection System

This module provides a comprehensive set of custom exceptions for error handling
across the application. Each exception includes contextual information, logging,
and structured error reporting.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ScraperException(Exception):
    """
    Base exception for all scraper-related errors.

    All custom exceptions in this application inherit from this base class.
    Provides common functionality for error tracking, logging, and context.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
        log_level: int = logging.ERROR
    ):
        """
        Initialize the exception with message and context.

        Args:
            message: Human-readable error message
            context: Additional context about the error (e.g., URL, file path, etc.)
            original_exception: Original exception if this is wrapping another exception
            log_level: Logging level for this exception (default: ERROR)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        self.exception_type = self.__class__.__name__

        # Log the exception with context
        self._log_exception(log_level)

    def _log_exception(self, log_level: int):
        """Log the exception with full context."""
        log_message = f"{self.exception_type}: {self.message}"

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            log_message += f" | Context: {context_str}"

        if self.original_exception:
            log_message += f" | Original: {type(self.original_exception).__name__}: {str(self.original_exception)}"

        logger.log(log_level, log_message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for structured logging/reporting.

        Returns:
            Dictionary with exception details
        """
        return {
            'exception_type': self.exception_type,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'original_exception': str(self.original_exception) if self.original_exception else None
        }

    def __str__(self) -> str:
        """String representation of the exception."""
        parts = [self.message]
        if self.context:
            parts.append(f"Context: {self.context}")
        if self.original_exception:
            parts.append(f"Caused by: {type(self.original_exception).__name__}")
        return " | ".join(parts)


class NetworkException(ScraperException):
    """
    Exception for network-related errors.

    Raised when network operations fail (HTTP requests, timeouts, connection errors).
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        retry_count: int = 0,
        **kwargs
    ):
        """
        Initialize network exception.

        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code if applicable
            retry_count: Number of retries attempted
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if url:
            context['url'] = url
        if status_code:
            context['status_code'] = status_code
        if retry_count:
            context['retry_count'] = retry_count

        super().__init__(message, context=context, **kwargs)


class PDFDownloadException(ScraperException):
    """
    Exception for PDF download errors.

    Raised when PDF download operations fail (invalid PDF, empty file, corrupted data).
    """

    def __init__(
        self,
        message: str,
        pdf_url: Optional[str] = None,
        output_path: Optional[str] = None,
        file_size: Optional[int] = None,
        is_valid_pdf: Optional[bool] = None,
        **kwargs
    ):
        """
        Initialize PDF download exception.

        Args:
            message: Error message
            pdf_url: URL of the PDF being downloaded
            output_path: Local path where PDF should be saved
            file_size: Size of downloaded file in bytes
            is_valid_pdf: Whether the file is a valid PDF
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if pdf_url:
            context['pdf_url'] = pdf_url
        if output_path:
            context['output_path'] = output_path
        if file_size is not None:
            context['file_size'] = file_size
        if is_valid_pdf is not None:
            context['is_valid_pdf'] = is_valid_pdf

        super().__init__(message, context=context, **kwargs)


class DatabaseException(ScraperException):
    """
    Exception for database-related errors.

    Raised when database operations fail (connection errors, query failures, constraint violations).
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        record_id: Optional[int] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize database exception.

        Args:
            message: Error message
            operation: Database operation that failed (e.g., 'INSERT', 'UPDATE', 'SELECT')
            table: Database table involved
            record_id: ID of the record if applicable
            query: SQL query that failed (truncated for safety)
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if operation:
            context['operation'] = operation
        if table:
            context['table'] = table
        if record_id:
            context['record_id'] = record_id
        if query:
            # Truncate query for logging safety
            context['query'] = query[:200] + '...' if len(query) > 200 else query

        super().__init__(message, context=context, **kwargs)


class ValidationException(ScraperException):
    """
    Exception for data validation errors.

    Raised when data fails validation checks (missing required fields, invalid formats).
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize validation exception.

        Args:
            message: Error message
            field: Field name that failed validation
            value: Value that failed validation
            expected_type: Expected data type or format
            validation_rule: Validation rule that was violated
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if field:
            context['field'] = field
        if value is not None:
            # Truncate long values
            value_str = str(value)
            context['value'] = value_str[:100] + '...' if len(value_str) > 100 else value_str
        if expected_type:
            context['expected_type'] = expected_type
        if validation_rule:
            context['validation_rule'] = validation_rule

        # Validation errors are typically warnings, not critical errors
        kwargs.setdefault('log_level', logging.WARNING)

        super().__init__(message, context=context, **kwargs)


class WebDriverException(ScraperException):
    """
    Exception for Selenium WebDriver errors.

    Raised when WebDriver operations fail (initialization errors, element not found, timeouts).
    """

    def __init__(
        self,
        message: str,
        driver_type: str = "Chrome",
        page_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize WebDriver exception.

        Args:
            message: Error message
            driver_type: Type of WebDriver (Chrome, Firefox, etc.)
            page_url: URL of the page being accessed
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        context['driver_type'] = driver_type
        if page_url:
            context['page_url'] = page_url

        super().__init__(message, context=context, **kwargs)


class ParsingException(ScraperException):
    """
    Exception for HTML/XML parsing errors.

    Raised when parsing operations fail (malformed HTML, missing elements, extraction errors).
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        parser_type: str = "BeautifulSoup",
        selector: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize parsing exception.

        Args:
            message: Error message
            url: URL of the page being parsed
            parser_type: Type of parser being used
            selector: CSS/XPath selector that failed
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if url:
            context['url'] = url
        context['parser_type'] = parser_type
        if selector:
            context['selector'] = selector

        super().__init__(message, context=context, **kwargs)


class FileOperationException(ScraperException):
    """
    Exception for file system operation errors.

    Raised when file operations fail (file not found, permission denied, disk full).
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize file operation exception.

        Args:
            message: Error message
            file_path: Path to the file
            operation: Operation that failed (read, write, delete, etc.)
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if file_path:
            context['file_path'] = file_path
        if operation:
            context['operation'] = operation

        super().__init__(message, context=context, **kwargs)


class ConfigurationException(ScraperException):
    """
    Exception for configuration errors.

    Raised when configuration is invalid or missing (missing env vars, invalid settings).
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration exception.

        Args:
            message: Error message
            config_key: Configuration key that is invalid/missing
            config_file: Configuration file path
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_file:
            context['config_file'] = config_file

        super().__init__(message, context=context, **kwargs)


class DriveUploadException(ScraperException):
    """
    Exception for Google Drive upload errors.

    Raised when Drive operations fail (authentication errors, upload failures, quota exceeded).
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        drive_file_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Drive upload exception.

        Args:
            message: Error message
            file_path: Local file path being uploaded
            drive_file_id: Google Drive file ID if applicable
            folder_id: Target folder ID
            **kwargs: Additional arguments passed to ScraperException
        """
        context = kwargs.pop('context', {})
        if file_path:
            context['file_path'] = file_path
        if drive_file_id:
            context['drive_file_id'] = drive_file_id
        if folder_id:
            context['folder_id'] = folder_id

        super().__init__(message, context=context, **kwargs)


# Exception counter for monitoring
class ExceptionCounter:
    """
    Global exception counter for monitoring and metrics.

    Tracks the number of each type of exception raised during execution.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._counters = {}
        return cls._instance

    def increment(self, exception_type: str):
        """Increment counter for a specific exception type."""
        if exception_type not in self._counters:
            self._counters[exception_type] = 0
        self._counters[exception_type] += 1

    def get_counts(self) -> Dict[str, int]:
        """Get all exception counts."""
        return self._counters.copy()

    def get_count(self, exception_type: str) -> int:
        """Get count for a specific exception type."""
        return self._counters.get(exception_type, 0)

    def reset(self):
        """Reset all counters."""
        self._counters.clear()

    def report(self) -> str:
        """Generate a report of all exception counts."""
        if not self._counters:
            return "No exceptions recorded."

        lines = ["Exception Statistics:"]
        total = sum(self._counters.values())
        lines.append(f"Total Exceptions: {total}")
        lines.append("-" * 50)

        # Sort by count (descending)
        sorted_counts = sorted(self._counters.items(), key=lambda x: x[1], reverse=True)
        for exc_type, count in sorted_counts:
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"{exc_type}: {count} ({percentage:.1f}%)")

        return "\n".join(lines)


# Global exception counter instance
exception_counter = ExceptionCounter()


def track_exception(exception: ScraperException):
    """
    Track an exception in the global counter.

    Args:
        exception: Exception to track
    """
    exception_counter.increment(exception.exception_type)


# Hook into ScraperException to auto-track all exceptions
original_init = ScraperException.__init__

def tracked_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    track_exception(self)

ScraperException.__init__ = tracked_init
