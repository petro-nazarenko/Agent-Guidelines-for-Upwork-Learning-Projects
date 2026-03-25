"""Base integration classes and common patterns."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

import tenacity
from tenacity import (
    RetryCallState,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class IntegrationError(Exception):
    """Base exception for integration errors."""


class RateLimitError(IntegrationError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(IntegrationError):
    """Raised when authentication fails."""


class ConnectionError(IntegrationError):
    """Raised when connection fails."""


@dataclass
class IntegrationConfig:
    """Base configuration for integrations."""

    max_retries: int = 3
    timeout: float = 30.0
    rate_limit_delay: float = 1.0


class BaseIntegration(ABC):
    """Abstract base class for integrations.

    Provides common patterns:
    - Exponential backoff retry logic
    - Rate limiting awareness
    - Connection management
    - Standardized logging
    """

    def __init__(self, config: IntegrationConfig | None = None) -> None:
        self._config = config or IntegrationConfig()
        self._connected = False
        self._logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the name of the service."""
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the service."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the service."""
        raise NotImplementedError

    def __enter__(self) -> "BaseIntegration":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()

    def retry_with_backoff(
        self,
        max_attempts: int | None = None,
        initial_wait: float = 1.0,
        max_wait: float = 60.0,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for retry with exponential backoff.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_wait: Initial wait time in seconds
            max_wait: Maximum wait time in seconds

        Returns:
            Decorated function with retry logic
        """
        if max_attempts is None:
            max_attempts = self._config.max_retries

        stop_strategy = stop_after_attempt(max_attempts)
        wait_strategy = tenacity.wait_exponential(
            multiplier=initial_wait,
            max=max_wait,
        )

        def before_callback(retry_state: RetryCallState) -> None:
            """Log retry attempts."""
            attempt = retry_state.attempt_number
            exception = retry_state.outcome.exception() if retry_state.outcome else None
            self._logger.warning(
                f"Retry attempt {attempt}/{max_attempts} for {self.service_name}",
                extra={"exception": str(exception) if exception else None},
            )

        return tenacity.retry(
            stop=stop_strategy,
            wait=wait_strategy,
            before_sleep=before_callback,
            reraise=True,
        )

    def _handle_rate_limit(self, response: Any) -> None:
        """Handle rate limit response.

        Args:
            response: API response object

        Raises:
            RateLimitError: When rate limit is exceeded
        """
        if hasattr(response, "status_code") and response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

    def _validate_config(self) -> None:
        """Validate integration configuration."""
        if self._config.max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if self._config.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self._config.rate_limit_delay < 0:
            raise ValueError("rate_limit_delay cannot be negative")

    @property
    def is_connected(self) -> bool:
        """Check if integration is connected."""
        return self._connected
