"""
Unit tests for error handling utilities
"""
import pytest
from unittest.mock import Mock, patch
from neo4j.exceptions import ServiceUnavailable, TransientError, Neo4jError

from utils.error_handling import (
    neo4j_retry,
    safe_neo4j_operation,
    Neo4jTransactionContext,
    validate_json_structure,
    sanitize_neo4j_string,
    batch_operation
)


@pytest.mark.unit
class TestNeo4jRetry:
    """Test neo4j_retry decorator"""

    def test_retry_on_transient_error(self):
        """Test retry logic on transient errors"""
        mock_func = Mock(side_effect=[
            TransientError("Temporary failure"),
            TransientError("Temporary failure"),
            "success"
        ])

        decorated_func = neo4j_retry(max_attempts=3)(mock_func)
        result = decorated_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_on_service_unavailable(self):
        """Test retry on ServiceUnavailable"""
        mock_func = Mock(side_effect=[
            ServiceUnavailable("Connection lost"),
            "success"
        ])

        decorated_func = neo4j_retry(max_attempts=3)(mock_func)
        result = decorated_func()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_max_attempts_exceeded(self):
        """Test failure after max attempts"""
        mock_func = Mock(side_effect=TransientError("Persistent failure"))

        decorated_func = neo4j_retry(max_attempts=2)(mock_func)

        with pytest.raises(TransientError):
            decorated_func()

        assert mock_func.call_count == 2

    def test_no_retry_on_permanent_error(self):
        """Test no retry on non-transient errors"""
        mock_func = Mock(side_effect=ValueError("Permanent error"))

        decorated_func = neo4j_retry(max_attempts=3)(mock_func)

        with pytest.raises(ValueError):
            decorated_func()

        # Should fail immediately without retry
        assert mock_func.call_count == 1


@pytest.mark.unit
class TestSafeNeo4jOperation:
    """Test safe_neo4j_operation function"""

    def test_successful_operation(self):
        """Test successful operation returns result"""
        mock_operation = Mock(return_value="success")

        result = safe_neo4j_operation(mock_operation, "arg1", "arg2")

        assert result == "success"
        mock_operation.assert_called_once_with("arg1", "arg2")

    def test_neo4j_error_returns_fallback(self):
        """Test Neo4jError returns fallback value"""
        mock_operation = Mock(side_effect=Neo4jError("Database error"))

        result = safe_neo4j_operation(
            mock_operation,
            fallback_value="fallback",
            error_message="Test operation failed"
        )

        assert result == "fallback"

    def test_generic_exception_returns_fallback(self):
        """Test generic exception returns fallback"""
        mock_operation = Mock(side_effect=RuntimeError("Unexpected error"))

        result = safe_neo4j_operation(
            mock_operation,
            fallback_value=None,
            error_message="Operation failed"
        )

        assert result is None

    def test_operation_with_kwargs(self):
        """Test operation with keyword arguments"""
        mock_operation = Mock(return_value="result")

        result = safe_neo4j_operation(
            mock_operation,
            key1="value1",
            key2="value2"
        )

        assert result == "result"
        mock_operation.assert_called_once_with(key1="value1", key2="value2")


@pytest.mark.unit
class TestNeo4jTransactionContext:
    """Test Neo4jTransactionContext manager"""

    def test_transaction_commit_on_success(self):
        """Test transaction commits on successful execution"""
        mock_session = Mock()
        mock_tx = Mock()
        mock_session.begin_transaction.return_value = mock_tx

        with Neo4jTransactionContext(mock_session, "Test operation") as tx:
            tx.run("CREATE (n:Node)")

        mock_session.begin_transaction.assert_called_once()
        mock_tx.commit.assert_called_once()
        mock_tx.rollback.assert_not_called()

    def test_transaction_rollback_on_error(self):
        """Test transaction rolls back on error"""
        mock_session = Mock()
        mock_tx = Mock()
        mock_session.begin_transaction.return_value = mock_tx

        with pytest.raises(ValueError):
            with Neo4jTransactionContext(mock_session, "Test operation") as tx:
                raise ValueError("Test error")

        mock_session.begin_transaction.assert_called_once()
        mock_tx.rollback.assert_called_once()
        mock_tx.commit.assert_not_called()

    def test_transaction_rollback_on_commit_failure(self):
        """Test rollback if commit fails"""
        mock_session = Mock()
        mock_tx = Mock()
        mock_tx.commit.side_effect = RuntimeError("Commit failed")
        mock_session.begin_transaction.return_value = mock_tx

        with pytest.raises(RuntimeError):
            with Neo4jTransactionContext(mock_session, "Test operation") as tx:
                pass  # Successful execution but commit will fail

        mock_tx.commit.assert_called_once()
        mock_tx.rollback.assert_called_once()


@pytest.mark.unit
class TestValidateJsonStructure:
    """Test validate_json_structure function"""

    def test_valid_structure_passes(self):
        """Test validation passes with valid structure"""
        data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        required_keys = ["key1", "key2"]

        # Should not raise
        validate_json_structure(data, required_keys, "Test data")

    def test_missing_keys_raises_error(self):
        """Test missing keys raises ValueError"""
        data = {"key1": "value1"}
        required_keys = ["key1", "key2", "key3"]

        with pytest.raises(ValueError) as exc_info:
            validate_json_structure(data, required_keys, "Test data")

        assert "missing required keys" in str(exc_info.value)
        assert "key2" in str(exc_info.value)

    def test_non_dict_raises_error(self):
        """Test non-dict input raises ValueError"""
        data = ["not", "a", "dict"]
        required_keys = ["key1"]

        with pytest.raises(ValueError) as exc_info:
            validate_json_structure(data, required_keys, "Test data")

        assert "must be a dictionary" in str(exc_info.value)

    def test_empty_required_keys(self):
        """Test validation with no required keys"""
        data = {"key1": "value1"}
        required_keys = []

        # Should not raise
        validate_json_structure(data, required_keys, "Test data")


@pytest.mark.unit
class TestSanitizeNeo4jString:
    """Test sanitize_neo4j_string function"""

    def test_sanitize_removes_null_bytes(self):
        """Test null byte removal"""
        dirty_string = "Hello\x00World"
        clean_string = sanitize_neo4j_string(dirty_string)

        assert "\x00" not in clean_string
        assert clean_string == "HelloWorld"

    def test_sanitize_strips_whitespace(self):
        """Test whitespace stripping"""
        dirty_string = "  Hello World  "
        clean_string = sanitize_neo4j_string(dirty_string)

        assert clean_string == "Hello World"

    def test_sanitize_truncates_long_strings(self):
        """Test long string truncation"""
        long_string = "A" * 500
        clean_string = sanitize_neo4j_string(long_string, max_length=100)

        assert len(clean_string) == 100
        assert clean_string.endswith("...")

    def test_sanitize_non_string_input(self):
        """Test conversion of non-string input"""
        number = 12345
        result = sanitize_neo4j_string(number)

        assert isinstance(result, str)
        assert result == "12345"

    def test_sanitize_no_max_length(self):
        """Test no truncation when max_length not specified"""
        long_string = "A" * 500
        clean_string = sanitize_neo4j_string(long_string)

        assert len(clean_string) == 500


@pytest.mark.unit
class TestBatchOperation:
    """Test batch_operation function"""

    def test_batch_operation_success(self):
        """Test successful batch processing"""
        items = list(range(10))
        mock_operation = Mock()

        results = batch_operation(
            items,
            mock_operation,
            batch_size=3,
            operation_name="Test batch"
        )

        # Should be called 4 times (10 items / 3 per batch = 3.33 -> 4 batches)
        assert mock_operation.call_count == 4
        assert results['total'] == 10
        assert results['success'] == 10
        assert results['failure'] == 0
        assert results['success_rate'] == 1.0

    def test_batch_operation_with_failures(self):
        """Test batch processing with some failures"""
        items = list(range(10))
        mock_operation = Mock(side_effect=[
            None,  # Success
            RuntimeError("Batch failed"),  # Failure
            None,  # Success
            None   # Success
        ])

        results = batch_operation(
            items,
            mock_operation,
            batch_size=3,
            operation_name="Test batch"
        )

        assert results['total'] == 10
        assert results['success'] == 7  # 3 successful batches
        assert results['failure'] == 3  # 1 failed batch
        assert results['success_rate'] == 0.7

    def test_batch_operation_empty_list(self):
        """Test batch operation with empty list"""
        items = []
        mock_operation = Mock()

        results = batch_operation(
            items,
            mock_operation,
            batch_size=5,
            operation_name="Empty batch"
        )

        assert results['total'] == 0
        assert results['success'] == 0
        assert results['failure'] == 0
        assert results['success_rate'] == 0

    def test_batch_operation_single_batch(self):
        """Test batch operation with single batch"""
        items = [1, 2, 3]
        mock_operation = Mock()

        results = batch_operation(
            items,
            mock_operation,
            batch_size=10,
            operation_name="Single batch"
        )

        assert mock_operation.call_count == 1
        assert results['success'] == 3

    def test_batch_operation_exact_batches(self):
        """Test batch operation with exact number of batches"""
        items = list(range(15))
        mock_operation = Mock()

        results = batch_operation(
            items,
            mock_operation,
            batch_size=5,
            operation_name="Exact batches"
        )

        assert mock_operation.call_count == 3  # Exactly 3 batches
        assert results['success'] == 15
