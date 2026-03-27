"""Logging configuration and utilities."""

import logging
import os
import sys
from typing import cast

import structlog

DEFAULT_LOG_LEVEL = logging.INFO

_logging_configured = False


def configure_logging(log_level: int | None = None) -> None:
    """Configure structured logging. Idempotent — safe to call multiple times.

    The first call wins. Subsequent calls are no-ops so that the CLI entry
    point can set the level from config before any module-level logger fires.

    Args:
        log_level: Logging level (e.g. logging.DEBUG). When None, reads the
                   LOG_LEVEL environment variable (default: INFO).
    """
    global _logging_configured
    if _logging_configured:
        return
    _logging_configured = True

    if log_level is None:
        env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, env_level, DEFAULT_LOG_LEVEL)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(
    name: str | None = None,
) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    if not _logging_configured:
        configure_logging()

    logger = structlog.get_logger(name)
    return cast(structlog.stdlib.BoundLogger, logger)


def add_log_context(**kwargs: str) -> None:
    """Add context to all subsequent log messages.

    Args:
        **kwargs: Context key-value pairs
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**kwargs)
