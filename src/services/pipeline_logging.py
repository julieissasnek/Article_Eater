"""
Sprint 2.0.5: Structured logging and error handling for Article Eater pipeline.

This module provides:
1. Centralized logging configuration with structured output
2. Custom exception hierarchy for pipeline errors
3. Error recovery mechanisms for transient failures
4. Context managers for pipeline stages

Created: 2026-02-08
"""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
import time

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Default log level from environment
LOG_LEVEL = os.environ.get("AE_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get("AE_LOG_FORMAT", "structured")  # "structured" or "simple"
LOG_FILE = os.environ.get("AE_LOG_FILE", None)  # Optional file path

# Structured log format
STRUCTURED_FORMAT = (
    '{"ts": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
    '"message": "%(message)s", "module": "%(module)s", "func": "%(funcName)s", "line": %(lineno)d}'
)

# Simple log format
SIMPLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        # Add extra context if available
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add custom fields from extra
        if hasattr(record, "paper_id"):
            log_entry["paper_id"] = record.paper_id
        if hasattr(record, "run_id"):
            log_entry["run_id"] = record.run_id
        if hasattr(record, "stage"):
            log_entry["stage"] = record.stage
        if hasattr(record, "context"):
            log_entry["context"] = record.context

        return json.dumps(log_entry, default=str)


def configure_logging(
    level: Optional[str] = None,
    format_type: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the Article Eater pipeline.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: "structured" for JSON, "simple" for human-readable
        log_file: Optional path to write logs to a file
    """
    level = level or LOG_LEVEL
    format_type = format_type or LOG_FORMAT
    log_file = log_file or LOG_FILE

    # Get root logger for AE
    root_logger = logging.getLogger("ae")
    root_logger.setLevel(getattr(logging, level, logging.INFO))

    # Clear existing handlers
    root_logger.handlers = []

    # Create formatter
    if format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(SIMPLE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(file_path))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the AE namespace."""
    return logging.getLogger(f"ae.{name}")


# =============================================================================
# EXCEPTION HIERARCHY
# =============================================================================


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    def __init__(
        self,
        message: str,
        stage: Optional[str] = None,
        paper_id: Optional[str] = None,
        recoverable: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.stage = stage
        self.paper_id = paper_id
        self.recoverable = recoverable
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "stage": self.stage,
            "paper_id": self.paper_id,
            "recoverable": self.recoverable,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class ExtractionError(PipelineError):
    """Error during text extraction from PDF/documents."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="extraction", **kwargs)


class LLMError(PipelineError):
    """Error during LLM-based extraction."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="llm_extraction", **kwargs)


class ConfigurationError(PipelineError):
    """Error in pipeline configuration (missing keys, invalid settings)."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="configuration", **kwargs)


class WebIntegrationError(PipelineError):
    """Error during Web of Belief integration."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="web_integration", **kwargs)


class SerializationError(PipelineError):
    """Error during output serialization."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="serialization", **kwargs)


class DatabaseError(PipelineError):
    """Error during database operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="database", **kwargs)


class ValidationError(PipelineError):
    """Error during input/output validation."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, stage="validation", **kwargs)


class RetryableError(PipelineError):
    """Error that can be retried (transient failures)."""

    def __init__(self, message: str, max_retries: int = 3, **kwargs):
        super().__init__(message, recoverable=True, **kwargs)
        self.max_retries = max_retries


# =============================================================================
# ERROR SEVERITY
# =============================================================================


class ErrorSeverity(Enum):
    """Error severity levels for classification."""

    FATAL = auto()  # Pipeline must abort
    BLOCKING = auto()  # Current paper cannot proceed
    DEGRADED = auto()  # Reduced functionality but can continue
    WARNING = auto()  # Non-fatal issue, logged for review
    INFO = auto()  # Informational (not an error)


@dataclass
class ErrorRecord:
    """Structured error record for tracking."""

    error_id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    stage: str
    paper_id: Optional[str]
    recoverable: bool
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity.name,
            "stage": self.stage,
            "paper_id": self.paper_id,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "stack_trace": self.stack_trace,
            "retry_count": self.retry_count,
        }


# =============================================================================
# ERROR COLLECTOR
# =============================================================================


class ErrorCollector:
    """Collects and manages errors during pipeline execution."""

    def __init__(self, run_id: str, paper_id: Optional[str] = None):
        self.run_id = run_id
        self.paper_id = paper_id
        self.errors: List[ErrorRecord] = []
        self._error_count = 0
        self._logger = get_logger("error_collector")

    def record(
        self,
        error: Union[Exception, str],
        severity: ErrorSeverity,
        stage: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorRecord:
        """Record an error."""
        self._error_count += 1
        error_id = f"{self.run_id}.err.{self._error_count}"

        if isinstance(error, PipelineError):
            message = error.message
            error_type = type(error).__name__
            recoverable = error.recoverable
            ctx = {**error.context, **(context or {})}
        elif isinstance(error, Exception):
            message = str(error)
            error_type = type(error).__name__
            recoverable = False
            ctx = context or {}
        else:
            message = str(error)
            error_type = "Error"
            recoverable = False
            ctx = context or {}

        record = ErrorRecord(
            error_id=error_id,
            error_type=error_type,
            message=message,
            severity=severity,
            stage=stage,
            paper_id=self.paper_id,
            recoverable=recoverable,
            timestamp=datetime.now(timezone.utc),
            context=ctx,
            stack_trace=traceback.format_exc() if isinstance(error, Exception) else None,
        )

        self.errors.append(record)

        # Log based on severity
        log_level = {
            ErrorSeverity.FATAL: logging.CRITICAL,
            ErrorSeverity.BLOCKING: logging.ERROR,
            ErrorSeverity.DEGRADED: logging.WARNING,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.INFO: logging.INFO,
        }.get(severity, logging.ERROR)

        self._logger.log(
            log_level,
            f"[{stage}] {error_type}: {message}",
            extra={
                "paper_id": self.paper_id,
                "run_id": self.run_id,
                "stage": stage,
                "context": ctx,
            },
        )

        return record

    def has_fatal_errors(self) -> bool:
        """Check if any fatal errors were recorded."""
        return any(e.severity == ErrorSeverity.FATAL for e in self.errors)

    def has_blocking_errors(self) -> bool:
        """Check if any blocking errors were recorded."""
        return any(e.severity in (ErrorSeverity.FATAL, ErrorSeverity.BLOCKING) for e in self.errors)

    def get_errors_by_stage(self, stage: str) -> List[ErrorRecord]:
        """Get all errors for a specific stage."""
        return [e for e in self.errors if e.stage == stage]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of collected errors."""
        by_severity = {}
        for sev in ErrorSeverity:
            count = sum(1 for e in self.errors if e.severity == sev)
            if count > 0:
                by_severity[sev.name] = count

        by_stage = {}
        for e in self.errors:
            by_stage[e.stage] = by_stage.get(e.stage, 0) + 1

        return {
            "total_errors": len(self.errors),
            "has_fatal": self.has_fatal_errors(),
            "has_blocking": self.has_blocking_errors(),
            "by_severity": by_severity,
            "by_stage": by_stage,
            "recoverable_count": sum(1 for e in self.errors if e.recoverable),
        }

    def to_jsonl(self, path: Path) -> int:
        """Write errors to JSONL file."""
        with path.open("w", encoding="utf-8") as f:
            for e in self.errors:
                f.write(json.dumps(e.to_dict(), default=str) + "\n")
        return len(self.errors)


# =============================================================================
# RETRY MECHANISM
# =============================================================================

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator for retrying functions on transient failures.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger for retry messages
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            log = logger or get_logger("retry")
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        log.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        log.error(f"All {max_retries + 1} attempts failed: {e}")
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            return None  # type: ignore

        return wrapper

    return decorator


# =============================================================================
# STAGE CONTEXT MANAGER
# =============================================================================


@contextmanager
def pipeline_stage(
    stage_name: str,
    error_collector: ErrorCollector,
    paper_id: Optional[str] = None,
    fatal_on_error: bool = False,
):
    """
    Context manager for pipeline stages with automatic error handling.

    Usage:
        with pipeline_stage("extraction", collector, paper_id) as stage:
            # do extraction work
            stage.log_info("Extracted 5 findings")

    Args:
        stage_name: Name of the pipeline stage
        error_collector: ErrorCollector instance
        paper_id: Paper ID being processed
        fatal_on_error: If True, errors are marked as FATAL
    """
    logger = get_logger(stage_name)
    start_time = time.time()

    class StageContext:
        def __init__(self):
            self.name = stage_name
            self.success = True
            self.result = None

        def log_debug(self, msg: str, **kwargs):
            logger.debug(f"[{paper_id}] {msg}", extra={"paper_id": paper_id, **kwargs})

        def log_info(self, msg: str, **kwargs):
            logger.info(f"[{paper_id}] {msg}", extra={"paper_id": paper_id, **kwargs})

        def log_warning(self, msg: str, **kwargs):
            logger.warning(f"[{paper_id}] {msg}", extra={"paper_id": paper_id, **kwargs})

        def log_error(self, msg: str, error: Optional[Exception] = None, **kwargs):
            logger.error(f"[{paper_id}] {msg}", exc_info=error, extra={"paper_id": paper_id, **kwargs})

        def record_error(
            self,
            error: Union[Exception, str],
            severity: Optional[ErrorSeverity] = None,
            context: Optional[Dict[str, Any]] = None,
        ) -> ErrorRecord:
            self.success = False
            if severity is None:
                severity = ErrorSeverity.FATAL if fatal_on_error else ErrorSeverity.BLOCKING
            return error_collector.record(error, severity, stage_name, context)

    ctx = StageContext()

    logger.debug(f"[{paper_id}] Starting stage: {stage_name}")

    try:
        yield ctx
    except PipelineError as e:
        ctx.success = False
        severity = ErrorSeverity.FATAL if fatal_on_error else ErrorSeverity.BLOCKING
        error_collector.record(e, severity, stage_name)
        raise
    except Exception as e:
        ctx.success = False
        severity = ErrorSeverity.FATAL if fatal_on_error else ErrorSeverity.BLOCKING
        error_collector.record(e, severity, stage_name)
        raise
    finally:
        elapsed = time.time() - start_time
        status = "completed" if ctx.success else "failed"
        logger.debug(f"[{paper_id}] Stage {stage_name} {status} in {elapsed:.2f}s")


# =============================================================================
# INITIALIZATION
# =============================================================================

# Configure logging on module import (can be reconfigured later)
configure_logging()
