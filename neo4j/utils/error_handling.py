"""
Error handling utilities for Neo4j operations
Provides retry logic, transaction management, and graceful degradation
"""
import functools
import time
from typing import Callable, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
from neo4j.exceptions import (
    ServiceUnavailable,
    TransientError,
    SessionExpired,
    Neo4jError
)
import logging

logger = logging.getLogger(__name__)


# Retry decorator for Neo4j transient errors
def neo4j_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    multiplier: int = 2
):
    """
    Retry decorator for Neo4j operations that may fail transiently

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        multiplier: Exponential backoff multiplier

    Example:
        @neo4j_retry(max_attempts=5)
        def create_node(session, properties):
            session.run("CREATE (n:Node $props)", props=properties)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            ServiceUnavailable,
            TransientError,
            SessionExpired
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )


def safe_neo4j_operation(
    operation: Callable,
    *args,
    fallback_value: Any = None,
    error_message: str = "Neo4j operation failed",
    **kwargs
) -> Optional[Any]:
    """
    Execute Neo4j operation with error handling and fallback

    Args:
        operation: Function to execute
        *args: Positional arguments for operation
        fallback_value: Value to return on error (default: None)
        error_message: Custom error message
        **kwargs: Keyword arguments for operation

    Returns:
        Result of operation or fallback_value on error

    Example:
        result = safe_neo4j_operation(
            session.run,
            "MATCH (n) RETURN count(n)",
            fallback_value=0,
            error_message="Failed to count nodes"
        )
    """
    try:
        return operation(*args, **kwargs)
    except Neo4jError as e:
        logger.error(f"{error_message}: {str(e)}")
        logger.debug(f"Args: {args}, Kwargs: {kwargs}", exc_info=True)
        return fallback_value
    except Exception as e:
        logger.error(f"Unexpected error in {error_message}: {str(e)}")
        logger.debug(f"Args: {args}, Kwargs: {kwargs}", exc_info=True)
        return fallback_value


class Neo4jTransactionContext:
    """
    Context manager for Neo4j transactions with rollback support

    Example:
        with Neo4jTransactionContext(session, "Create nodes") as tx:
            tx.run("CREATE (n:Node {id: $id})", id=1)
            tx.run("CREATE (n:Node {id: $id})", id=2)
        # Auto-commits on success, rolls back on error
    """

    def __init__(self, session, operation_name: str = "Transaction"):
        self.session = session
        self.operation_name = operation_name
        self.tx = None

    def __enter__(self):
        logger.info(f"Starting transaction: {self.operation_name}")
        self.tx = self.session.begin_transaction()
        return self.tx

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - commit
            try:
                self.tx.commit()
                logger.info(f"Transaction committed: {self.operation_name}")
            except Exception as e:
                logger.error(f"Failed to commit transaction: {str(e)}")
                self.tx.rollback()
                logger.info(f"Transaction rolled back: {self.operation_name}")
                raise
        else:
            # Error - rollback
            self.tx.rollback()
            logger.warning(
                f"Transaction rolled back due to error: {self.operation_name}\n"
                f"Error: {exc_type.__name__}: {exc_val}"
            )

        return False  # Re-raise exception


def validate_json_structure(data: dict, required_keys: list, data_name: str = "Data"):
    """
    Validate JSON data structure

    Args:
        data: Dictionary to validate
        required_keys: List of required keys
        data_name: Name of data for error messages

    Raises:
        ValueError: If validation fails

    Example:
        validate_json_structure(
            case_data,
            ["id", "name", "citation"],
            "Case data"
        )
    """
    if not isinstance(data, dict):
        raise ValueError(f"{data_name} must be a dictionary, got {type(data)}")

    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValueError(
            f"{data_name} missing required keys: {', '.join(missing_keys)}"
        )

    logger.debug(f"{data_name} validation passed")


def sanitize_neo4j_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string for Neo4j storage

    Args:
        value: String to sanitize
        max_length: Maximum length (truncate if longer)

    Returns:
        Sanitized string

    Example:
        safe_name = sanitize_neo4j_string(party_name, max_length=200)
    """
    if not isinstance(value, str):
        value = str(value)

    # Remove null bytes
    value = value.replace('\x00', '')

    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length-3] + "..."
        logger.debug(f"Truncated string to {max_length} characters")

    return value.strip()


def batch_operation(
    items: list,
    operation: Callable,
    batch_size: int = 100,
    operation_name: str = "Batch operation"
) -> dict:
    """
    Execute operation in batches with progress tracking

    Args:
        items: List of items to process
        operation: Function to call for each batch
        batch_size: Number of items per batch
        operation_name: Name for logging

    Returns:
        Dictionary with success/failure counts

    Example:
        results = batch_operation(
            cases,
            lambda batch: load_cases_to_neo4j(batch),
            batch_size=50,
            operation_name="Load cases"
        )
    """
    total = len(items)
    success_count = 0
    failure_count = 0

    logger.info(f"Starting {operation_name}: {total} items in batches of {batch_size}")

    for i in range(0, total, batch_size):
        batch = items[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

        try:
            operation(batch)
            success_count += len(batch)
        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {str(e)}")
            failure_count += len(batch)

    logger.info(
        f"{operation_name} complete: {success_count} succeeded, "
        f"{failure_count} failed out of {total} total"
    )

    return {
        "total": total,
        "success": success_count,
        "failure": failure_count,
        "success_rate": success_count / total if total > 0 else 0
    }
