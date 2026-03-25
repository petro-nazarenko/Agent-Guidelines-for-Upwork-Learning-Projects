"""Logging configuration and utilities."""

import logging
import sys
from typing import Optional

import structlog

DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(
    name: Optional[str] = None,
    log_level: int = DEFAULT_LOG_LEVEL,
) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level

    Returns:
        Configured structlog logger
    """
    configure_logging(log_level)

    logger = structlog.get_logger(name)
    return logger


def configure_logging(log_level: int = DEFAULT_LOG_LEVEL) -> None:
    """Configure structured logging.

    Args:
        log_level: Global logging level
    """
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


def add_log_context(**kwargs: str) -> None:
    """Add context to all subsequent log messages.

    Args:
        **kwargs: Context key-value pairs
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**kwargs)
