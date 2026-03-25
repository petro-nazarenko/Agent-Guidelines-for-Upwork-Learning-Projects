"""Tests for retry utilities."""

import pytest

from src.utils.retry import with_retry


class TestWithRetry:
    """Tests for retry decorator."""

    def test_success_on_first_attempt(self) -> None:
        """Test successful function without retry."""
        call_count = 0

        @with_retry(max_attempts=3)
        def successful_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure(self) -> None:
        """Test retry on transient failure."""
        call_count = 0

        @with_retry(max_attempts=3, initial_wait=0.01)
        def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    def test_raises_after_max_attempts(self) -> None:
        """Test that exception is raised after max attempts."""
        call_count = 0

        @with_retry(max_attempts=3, initial_wait=0.01)
        def always_fail() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fail()

        assert call_count == 3

    def test_retry_specific_exceptions(self) -> None:
        """Test retry only on specific exceptions."""
        call_count = 0

        @with_retry(max_attempts=3, exceptions=(ConnectionError,))
        def mixed_failures() -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Not retryable")
            if call_count == 2:
                raise ConnectionError("Retryable")
            return "success"

        with pytest.raises(ValueError, match="Not retryable"):
            mixed_failures()

        assert call_count == 1
