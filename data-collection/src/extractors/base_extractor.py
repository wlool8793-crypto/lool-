"""
Base extractor for Legal RAG Extraction System (Phase 3)
Abstract base class with retry logic and error handling
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time

from .config import config
from .exceptions import (
    ExtractionError,
    RetryExhaustedError,
    is_transient_error,
    categorize_error
)
from .logging_config import get_logger

logger = get_logger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.

    Provides:
    - Standardized extract() interface with error handling
    - Automatic retry logic with exponential backoff
    - Input/output validation hooks
    - Logging integration
    - Performance tracking
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize base extractor.

        Args:
            name: Extractor name (defaults to class name)
        """
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f"extractors.{self.name}")

    # ==================== Abstract Methods ====================

    @abstractmethod
    def _extract_impl(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Core extraction implementation (subclasses must override).

        Args:
            input_data: Input data to extract from
            **kwargs: Additional extraction parameters

        Returns:
            Dictionary with extraction results

        Raises:
            ExtractionError: If extraction fails
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before extraction.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate extraction output.

        Args:
            output: Extraction output to validate

        Returns:
            True if valid, False if partial/incomplete
        """
        pass

    # ==================== Main Extract Method ====================

    def extract(
        self,
        input_data: Any,
        *,
        document_id: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main extraction method with error handling and retry logic.

        Args:
            input_data: Input data to extract from
            document_id: Optional document identifier for logging
            max_retries: Max retry attempts (overrides config)
            retry_delay: Initial retry delay (overrides config)
            **kwargs: Additional extraction parameters

        Returns:
            Dictionary with extraction results including:
            - status: 'success', 'partial', or 'failed'
            - data: Extracted data (if successful)
            - error: Error message (if failed)
            - execution_time_ms: Execution time in milliseconds
        """
        start_time = time.time()
        doc_id = document_id or "unknown"

        # Use config defaults if not specified
        max_retries = max_retries if max_retries is not None else config.max_retries
        retry_delay = retry_delay if retry_delay is not None else config.retry_delay

        self.logger.info(
            f"Starting extraction: {self.name}",
            extra={"document_id": doc_id, "extraction_stage": self.name}
        )

        # Try extraction with retries
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                # Validate input
                if not self.validate_input(input_data):
                    return self._build_error_result(
                        "Input validation failed",
                        start_time,
                        error_type="validation"
                    )

                # Execute extraction
                result = self._extract_impl(input_data, **kwargs)

                # Validate output
                is_valid = self.validate_output(result)

                # Set status based on validation
                if is_valid:
                    result['status'] = 'success'
                else:
                    result['status'] = 'partial'
                    self.logger.warning(
                        f"Extraction incomplete: {self.name}",
                        extra={"document_id": doc_id}
                    )

                # Add execution time
                execution_ms = int((time.time() - start_time) * 1000)
                result['execution_time_ms'] = execution_ms

                self.logger.info(
                    f"Extraction complete: {self.name} ({result['status']})",
                    extra={
                        "document_id": doc_id,
                        "status": result['status'],
                        "duration_ms": execution_ms
                    }
                )

                return result

            except Exception as e:
                last_error = e
                error_category = categorize_error(e)

                self.logger.error(
                    f"Extraction error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}",
                    extra={
                        "document_id": doc_id,
                        "error_category": error_category,
                        "attempt": attempt + 1
                    },
                    exc_info=True
                )

                # Check if should retry
                if attempt < max_retries and is_transient_error(e):
                    # Calculate backoff delay
                    delay = retry_delay * (config.retry_backoff ** attempt)
                    self.logger.info(
                        f"Retrying in {delay:.1f}s...",
                        extra={"document_id": doc_id, "retry_delay": delay}
                    )
                    time.sleep(delay)
                else:
                    # No more retries or permanent error
                    break

        # All retries exhausted
        if last_error:
            return self._build_error_result(
                str(last_error),
                start_time,
                error_type=type(last_error).__name__,
                error_category=categorize_error(last_error)
            )
        else:
            return self._build_error_result(
                "Unknown error",
                start_time,
                error_type="unknown"
            )

    # ==================== Helper Methods ====================

    def _build_error_result(
        self,
        error_msg: str,
        start_time: float,
        error_type: str = "unknown",
        error_category: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Build standardized error result.

        Args:
            error_msg: Error message
            start_time: Start time for execution calculation
            error_type: Type of error
            error_category: Error category

        Returns:
            Error result dictionary
        """
        execution_ms = int((time.time() - start_time) * 1000)

        return {
            'status': 'failed',
            'error': error_msg,
            'error_type': error_type,
            'error_category': error_category,
            'execution_time_ms': execution_ms,
            'data': None
        }

    def extract_safe(
        self,
        input_data: Any,
        default: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Safe extraction that never raises exceptions.

        Args:
            input_data: Input data to extract from
            default: Default value if extraction fails
            **kwargs: Additional extraction parameters

        Returns:
            Extraction result or default
        """
        try:
            return self.extract(input_data, **kwargs)
        except Exception as e:
            self.logger.error(f"Safe extraction failed: {e}", exc_info=True)
            return default or {'status': 'failed', 'error': str(e), 'data': None}


class SimpleExtractor(BaseExtractor):
    """
    Simplified extractor for basic use cases.

    Provides default implementations of validation methods.
    Subclasses only need to implement _extract_impl().
    """

    def validate_input(self, input_data: Any) -> bool:
        """Default input validation (checks not None/empty)"""
        if input_data is None:
            return False
        if isinstance(input_data, str) and not input_data.strip():
            return False
        return True

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Default output validation (checks has data)"""
        if not output:
            return False

        # Check if has meaningful data
        data = output.get('data')
        if data is None:
            return False

        # Check if data is not empty
        if isinstance(data, (list, dict, str)) and not data:
            return False

        return True


# ==================== Retry Utilities ====================

def retry_on_failure(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retry logic on any function.

    Args:
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries
        backoff: Exponential backoff multiplier
        exceptions: Tuple of exceptions to catch

    Example:
        @retry_on_failure(max_retries=3, retry_delay=1.0)
        def extract_something():
            # ... extraction logic
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e

                    if attempt < max_retries and is_transient_error(e):
                        delay = retry_delay * (backoff ** attempt)
                        logger.debug(f"Retrying {func.__name__} in {delay:.1f}s...")
                        time.sleep(delay)
                    else:
                        break

            # Raise last error
            if last_error:
                raise RetryExhaustedError(max_retries + 1, last_error)
            else:
                raise ExtractionError(f"Function {func.__name__} failed after {max_retries + 1} attempts")

        return wrapper
    return decorator


def extract_with_fallback(extractors: list, input_data: Any, **kwargs) -> Dict[str, Any]:
    """
    Try multiple extractors in order until one succeeds.

    Args:
        extractors: List of extractor instances
        input_data: Input data
        **kwargs: Additional arguments

    Returns:
        First successful extraction result

    Raises:
        ExtractionError: If all extractors fail
    """
    errors = []

    for extractor in extractors:
        try:
            result = extractor.extract(input_data, **kwargs)
            if result.get('status') in ['success', 'partial']:
                return result
            else:
                errors.append(f"{extractor.name}: {result.get('error', 'unknown error')}")
        except Exception as e:
            errors.append(f"{extractor.name}: {str(e)}")

    # All extractors failed
    raise ExtractionError(
        f"All extractors failed: {'; '.join(errors)}",
        {"extractor_count": len(extractors), "errors": errors}
    )
