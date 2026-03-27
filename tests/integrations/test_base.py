"""Tests for BaseIntegration and exception hierarchy."""

from unittest.mock import MagicMock, patch

import pytest

from src.integrations.base import (
    AuthenticationError,
    BaseIntegration,
    IntegrationConfig,
    IntegrationConnectionError,
    RateLimitError,
)


class _ConcreteIntegration(BaseIntegration):
    """Minimal concrete implementation for testing."""

    @property
    def service_name(self) -> str:
        return "test-service"

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False


class TestExceptionHierarchy:
    def test_rate_limit_error_stores_retry_after(self) -> None:
        err = RateLimitError("too many requests", retry_after=30)
        assert err.retry_after == 30
        assert "too many requests" in str(err)

    def test_authentication_error_is_integration_error(self) -> None:
        from src.integrations.base import IntegrationError

        assert issubclass(AuthenticationError, IntegrationError)

    def test_connection_error_is_integration_error(self) -> None:
        from src.integrations.base import IntegrationError

        assert issubclass(IntegrationConnectionError, IntegrationError)


class TestBaseIntegration:
    @pytest.fixture
    def integration(self) -> _ConcreteIntegration:
        return _ConcreteIntegration()

    def test_context_manager(self, integration: _ConcreteIntegration) -> None:
        with integration:
            assert integration.is_connected is True
        assert integration.is_connected is False

    def test_validate_config_valid(self, integration: _ConcreteIntegration) -> None:
        integration._validate_config()  # should not raise

    def test_validate_config_bad_retries(self) -> None:
        cfg = IntegrationConfig(max_retries=0)
        integ = _ConcreteIntegration(cfg)
        with pytest.raises(ValueError, match="max_retries"):
            integ._validate_config()

    def test_validate_config_bad_timeout(self) -> None:
        cfg = IntegrationConfig(timeout=-1.0)
        integ = _ConcreteIntegration(cfg)
        with pytest.raises(ValueError, match="timeout"):
            integ._validate_config()

    def test_validate_config_bad_rate_limit_delay(self) -> None:
        cfg = IntegrationConfig(rate_limit_delay=-0.1)
        integ = _ConcreteIntegration(cfg)
        with pytest.raises(ValueError, match="rate_limit_delay"):
            integ._validate_config()

    def test_handle_rate_limit_non_429(self, integration: _ConcreteIntegration) -> None:
        response = MagicMock()
        response.status_code = 200
        integration._handle_rate_limit(response)  # should not raise

    def test_handle_rate_limit_no_status_code(self, integration: _ConcreteIntegration) -> None:
        integration._handle_rate_limit("not a response")  # should not raise

    @patch("src.integrations.base.time.sleep")
    def test_handle_rate_limit_429_with_retry_after(
        self, mock_sleep: MagicMock, integration: _ConcreteIntegration
    ) -> None:
        response = MagicMock()
        response.status_code = 429
        response.headers = {"Retry-After": "5"}
        with pytest.raises(RateLimitError) as exc_info:
            integration._handle_rate_limit(response)
        assert exc_info.value.retry_after == 5
        mock_sleep.assert_called_once_with(5)

    @patch("src.integrations.base.time.sleep")
    def test_handle_rate_limit_429_no_retry_after(
        self, mock_sleep: MagicMock, integration: _ConcreteIntegration
    ) -> None:
        response = MagicMock()
        response.status_code = 429
        response.headers = {}
        with pytest.raises(RateLimitError):
            integration._handle_rate_limit(response)
        mock_sleep.assert_called_once_with(integration._config.rate_limit_delay)

    def test_retry_with_backoff_succeeds(self, integration: _ConcreteIntegration) -> None:
        call_count = 0

        @integration.retry_with_backoff(max_attempts=3, initial_wait=0.01)
        def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("transient")
            return "ok"

        result = flaky()
        assert result == "ok"
        assert call_count == 2

    def test_retry_with_backoff_exhausted(self, integration: _ConcreteIntegration) -> None:
        @integration.retry_with_backoff(max_attempts=2, initial_wait=0.01)
        def always_fail() -> None:
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            always_fail()
