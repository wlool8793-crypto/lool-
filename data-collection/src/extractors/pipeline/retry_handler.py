"""
Retry handler for Legal RAG Extraction System (Phase 3)
Advanced retry logic with exponential backoff and circuit breaker
"""

from typing import Dict, Any, Callable, Optional, List
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

from ..exceptions import is_transient_error
from ..config import config
from ..logging_config import get_logger

logger = get_logger(__name__)


class RetryHandler:
    """
    Advanced retry handler with multiple strategies.

    Features:
    - Exponential backoff with jitter
    - Circuit breaker pattern
    - Per-operation retry budgets
    - Retry statistics tracking
    - Configurable retry conditions
    """

    def __init__(
        self,
        max_retries: int = None,
        base_delay: float = None,
        backoff_factor: float = None,
        max_delay: float = 60.0,
        jitter: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum retry attempts (default from config)
            base_delay: Base delay in seconds (default from config)
            backoff_factor: Exponential backoff factor (default from config)
            max_delay: Maximum delay between retries
            jitter: Add random jitter to delays
            circuit_breaker_threshold: Failures before circuit opens
            circuit_breaker_timeout: Seconds before circuit reset attempt
        """
        self.max_retries = max_retries or config.max_retries
        self.base_delay = base_delay or config.retry_delay
        self.backoff_factor = backoff_factor or config.retry_backoff
        self.max_delay = max_delay
        self.jitter = jitter

        # Circuit breaker
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.circuit_state = {}  # operation_name -> state
        self.failure_counts = defaultdict(int)
        self.last_failure_time = {}

        # Statistics
        self.retry_stats = defaultdict(lambda: {
            'total_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'total_delay': 0.0
        })

    def retry(
        self,
        operation: Callable,
        *args,
        operation_name: str = None,
        should_retry: Optional[Callable[[Exception], bool]] = None,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Function to execute
            *args: Positional arguments for operation
            operation_name: Name for logging and circuit breaker
            should_retry: Custom retry condition function
            max_retries: Override max retries
            **kwargs: Keyword arguments for operation

        Returns:
            Operation result

        Raises:
            Exception if all retries exhausted
        """
        operation_name = operation_name or operation.__name__
        max_retries = max_retries if max_retries is not None else self.max_retries

        # Check circuit breaker
        if self._is_circuit_open(operation_name):
            raise CircuitBreakerOpenError(
                f"Circuit breaker open for {operation_name}"
            )

        # Default retry condition
        if should_retry is None:
            should_retry = is_transient_error

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # Execute operation
                result = operation(*args, **kwargs)

                # Success - update stats and reset circuit breaker
                if attempt > 0:
                    self.retry_stats[operation_name]['successful_retries'] += 1
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt + 1}"
                    )

                self._reset_circuit_breaker(operation_name)

                return result

            except Exception as e:
                last_exception = e

                # Update stats
                self.retry_stats[operation_name]['total_attempts'] += 1

                # Check if should retry
                if not should_retry(e):
                    logger.warning(
                        f"{operation_name} failed with non-retryable error: {e}"
                    )
                    self._record_failure(operation_name)
                    raise

                # Check if retries exhausted
                if attempt >= max_retries:
                    logger.error(
                        f"{operation_name} failed after {attempt + 1} attempts: {e}"
                    )
                    self._record_failure(operation_name)
                    self.retry_stats[operation_name]['failed_retries'] += 1
                    raise

                # Calculate delay
                delay = self._calculate_delay(attempt)

                logger.warning(
                    f"{operation_name} failed (attempt {attempt + 1}/{max_retries + 1}), "
                    f"retrying in {delay:.2f}s: {e}"
                )

                # Update delay stats
                self.retry_stats[operation_name]['total_delay'] += delay

                # Wait before retry
                time.sleep(delay)

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt.

        Uses exponential backoff: delay = base_delay * (backoff_factor ^ attempt)

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.base_delay * (self.backoff_factor ** attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            jitter_range = delay * 0.1  # ±10%
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter

        return max(0.0, delay)

    # ==================== Circuit Breaker ====================

    def _is_circuit_open(self, operation_name: str) -> bool:
        """
        Check if circuit breaker is open for operation.

        Args:
            operation_name: Operation name

        Returns:
            True if circuit is open (should not retry)
        """
        state = self.circuit_state.get(operation_name, 'closed')

        if state == 'closed':
            return False

        if state == 'open':
            # Check if timeout elapsed
            last_failure = self.last_failure_time.get(operation_name)

            if last_failure:
                elapsed = (datetime.utcnow() - last_failure).total_seconds()

                if elapsed >= self.circuit_breaker_timeout:
                    # Attempt reset
                    self.circuit_state[operation_name] = 'half-open'
                    logger.info(f"Circuit breaker for {operation_name} half-open")
                    return False

            return True

        if state == 'half-open':
            # Allow one attempt
            return False

        return False

    def _record_failure(self, operation_name: str):
        """
        Record failure for circuit breaker.

        Args:
            operation_name: Operation name
        """
        self.failure_counts[operation_name] += 1
        self.last_failure_time[operation_name] = datetime.utcnow()

        # Check if threshold exceeded
        if self.failure_counts[operation_name] >= self.circuit_breaker_threshold:
            self.circuit_state[operation_name] = 'open'
            logger.warning(
                f"Circuit breaker opened for {operation_name} "
                f"after {self.failure_counts[operation_name]} failures"
            )

    def _reset_circuit_breaker(self, operation_name: str):
        """
        Reset circuit breaker after success.

        Args:
            operation_name: Operation name
        """
        if operation_name in self.circuit_state:
            self.circuit_state[operation_name] = 'closed'
            self.failure_counts[operation_name] = 0
            logger.info(f"Circuit breaker for {operation_name} closed")

    # ==================== Batch Operations ====================

    def retry_batch(
        self,
        operations: List[Callable],
        operation_names: Optional[List[str]] = None,
        fail_fast: bool = False
    ) -> List[Any]:
        """
        Execute multiple operations with retry.

        Args:
            operations: List of functions to execute
            operation_names: Optional list of operation names
            fail_fast: Stop on first failure

        Returns:
            List of results (None for failed operations)
        """
        if operation_names is None:
            operation_names = [f"operation_{i}" for i in range(len(operations))]

        results = []

        for operation, name in zip(operations, operation_names):
            try:
                result = self.retry(operation, operation_name=name)
                results.append(result)

            except Exception as e:
                logger.error(f"Batch operation {name} failed: {e}")

                if fail_fast:
                    raise

                results.append(None)

        return results

    # ==================== Statistics ====================

    def get_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get retry statistics.

        Args:
            operation_name: Specific operation (None for all)

        Returns:
            Statistics dictionary
        """
        if operation_name:
            return dict(self.retry_stats.get(operation_name, {}))

        return {
            name: dict(stats)
            for name, stats in self.retry_stats.items()
        }

    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """
        Get circuit breaker status for all operations.

        Returns:
            Status dictionary
        """
        return {
            'circuit_states': dict(self.circuit_state),
            'failure_counts': dict(self.failure_counts),
            'last_failures': {
                name: time.isoformat() + 'Z'
                for name, time in self.last_failure_time.items()
            }
        }

    def reset_stats(self):
        """Reset all statistics."""
        self.retry_stats.clear()
        self.circuit_state.clear()
        self.failure_counts.clear()
        self.last_failure_time.clear()


# ==================== Decorator ====================

def retry_on_error(
    max_retries: int = None,
    base_delay: float = None,
    backoff_factor: float = None,
    should_retry: Optional[Callable[[Exception], bool]] = None
):
    """
    Decorator for automatic retry on errors.

    Args:
        max_retries: Maximum retry attempts
        base_delay: Base delay in seconds
        backoff_factor: Exponential backoff factor
        should_retry: Custom retry condition

    Usage:
        @retry_on_error(max_retries=3)
        def my_function():
            ...
    """
    def decorator(func):
        handler = RetryHandler(
            max_retries=max_retries,
            base_delay=base_delay,
            backoff_factor=backoff_factor
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.retry(
                func,
                *args,
                operation_name=func.__name__,
                should_retry=should_retry,
                **kwargs
            )

        return wrapper

    return decorator


# ==================== Exceptions ====================

class CircuitBreakerOpenError(Exception):
    """Circuit breaker is open, operation not allowed."""
    pass


class RetryExhaustedError(Exception):
    """All retry attempts have been exhausted."""
    pass


# ==================== Convenience Functions ====================

def retry_operation(
    operation: Callable,
    *args,
    max_retries: int = 3,
    **kwargs
) -> Any:
    """
    Quick retry of operation (convenience function).

    Args:
        operation: Function to execute
        *args: Positional arguments
        max_retries: Maximum retries
        **kwargs: Keyword arguments

    Returns:
        Operation result
    """
    handler = RetryHandler(max_retries=max_retries)
    return handler.retry(operation, *args, **kwargs)


def retry_with_backoff(
    operation: Callable,
    *args,
    max_retries: int = 5,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    """
    Retry with aggressive backoff.

    Args:
        operation: Function to execute
        *args: Positional arguments
        max_retries: Maximum retries
        base_delay: Base delay
        backoff_factor: Backoff factor
        **kwargs: Keyword arguments

    Returns:
        Operation result
    """
    handler = RetryHandler(
        max_retries=max_retries,
        base_delay=base_delay,
        backoff_factor=backoff_factor
    )
    return handler.retry(operation, *args, **kwargs)
