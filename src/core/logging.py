"""Structured Logging Configuration for Article Eater.

This module provides structured logging with JSON output for production
and human-readable console output for development.

Usage:
    from src.core.logging import get_logger, configure_logging

    # Configure once at startup
    configure_logging(json_logs=False, log_level="INFO")

    # Get a logger for your module
    logger = get_logger(__name__)

    # Log with context
    logger.info("processing_paper", paper_id="p123", page_count=42)
    logger.warning("low_coherence", belief_id="b456", score=0.3)
    logger.error("extraction_failed", paper_id="p789", error="timeout")

Output (console mode):
    2026-02-23 09:45:12 [info     ] processing_paper  paper_id=p123 page_count=42

Output (JSON mode):
    {"event": "processing_paper", "paper_id": "p123", "page_count": 42, "timestamp": "2026-02-23T09:45:12Z", "level": "info"}
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Optional

import structlog
from structlog.typing import Processor


def _add_log_level(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add log level to event dict."""
    event_dict["level"] = method_name
    return event_dict


def _add_module_info(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add module/function info from stack."""
    # structlog already handles this via CallsiteParameterAdder
    return event_dict


def configure_logging(
    json_logs: bool = False,
    log_level: str = "INFO",
    include_timestamps: bool = True,
) -> None:
    """Configure structured logging for the application.

    Args:
        json_logs: If True, output JSON logs (for production). If False, console output.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_timestamps: Include timestamp in logs
    """
    # Common processors for both modes
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if include_timestamps:
        shared_processors.insert(0, structlog.processors.TimeStamper(fmt="iso"))

    if json_logs:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        A bound structlog logger
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """Bind context variables that will be included in all subsequent logs.

    Useful for adding request IDs, user IDs, etc. that should appear in all
    log messages within a context.

    Example:
        bind_context(request_id="req-123", user_id="u456")
        logger.info("processing")  # Will include request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables."""
    structlog.contextvars.clear_contextvars()


# Convenience: configure with defaults on import if not already configured
# This allows simple usage: from src.core.logging import get_logger
# More sophisticated apps should call configure_logging() explicitly
_configured = False


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        configure_logging(json_logs=False, log_level="INFO")
        _configured = True


# Auto-configure with defaults
_ensure_configured()
