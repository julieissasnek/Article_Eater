"""
logging_config.py — Centralized Structured JSON Logging for ATLAS
=================================================================

Provides a JSONFormatter and setup_logging() function that wires
structured JSON output into all ATLAS services (overseer, orchestrator,
extraction pipeline, notification service).

Every log entry includes:
  - timestamp (ISO 8601)
  - level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
  - module (source module name)
  - message (log text)
  - context (optional dict with extra data)

Console output uses WCAG 2.1 AA compliant colors:
  - cyan for INFO
  - yellow for WARNING
  - green for DEBUG
  - white for ERROR/CRITICAL
  (no dark blue on dark backgrounds per CLAUDE.md)

Created: 2026-02-28  Phase 0, Task 0.5
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    Formats log records as structured JSON.

    Output format (one JSON object per line):
    {
        "timestamp": "2026-02-28T01:23:45.678Z",
        "level": "INFO",
        "module": "overseer",
        "message": "INV-4 check passed",
        "context": {"coherence_delta": -0.02}
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }

        # Include context if attached to the record
        context = getattr(record, "context", None)
        if context and isinstance(context, dict):
            entry["context"] = context

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)

        # Include function name and line for DEBUG/ERROR level
        if record.levelno >= logging.ERROR or record.levelno <= logging.DEBUG:
            entry["function"] = record.funcName
            entry["lineno"] = record.lineno

        return json.dumps(entry, default=str)


class ColorConsoleFormatter(logging.Formatter):
    """
    WCAG 2.1 AA compliant console formatter.

    Colors chosen for readability on dark backgrounds:
      DEBUG    → green
      INFO     → cyan
      WARNING  → yellow
      ERROR    → white (bold)
      CRITICAL → white (bold, underline)

    Never uses dark blue on dark backgrounds (per CLAUDE.md).
    """

    COLORS = {
        logging.DEBUG: "\033[32m",       # green
        logging.INFO: "\033[36m",        # cyan
        logging.WARNING: "\033[33m",     # yellow
        logging.ERROR: "\033[1;37m",     # bold white
        logging.CRITICAL: "\033[1;4;37m",  # bold underline white
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        timestamp = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).strftime("%H:%M:%S")
        level = record.levelname[:4].ljust(4)
        module = record.module[:20].ljust(20)
        message = record.getMessage()

        formatted = f"{color}{timestamp} [{level}] {module} {message}{self.RESET}"

        # Append context if present
        context = getattr(record, "context", None)
        if context and isinstance(context, dict):
            ctx_str = " ".join(f"{k}={v}" for k, v in context.items())
            formatted += f" {color}| {ctx_str}{self.RESET}"

        if record.exc_info and record.exc_info[0] is not None:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class ContextAdapter(logging.LoggerAdapter):
    """
    Logger adapter that merges context dict into log records.

    Usage:
        logger = get_logger("overseer", context={"paper_id": "10.1234/abc"})
        logger.info("Processing paper", extra={"context": {"step": 5}})
        # Output includes both paper_id and step in context
    """

    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        # Merge adapter context with per-call context
        record_ctx = extra.get("context", {})
        merged = {**self.extra, **record_ctx}
        extra["context"] = merged
        return msg, kwargs


def setup_logging(
    level: int = logging.INFO,
    json_file: Optional[str] = None,
    console: bool = True,
    json_to_stdout: bool = False,
) -> None:
    """
    Configure structured logging for all ATLAS services.

    Args:
        level: Minimum log level (default: INFO)
        json_file: Path to JSON log file (optional)
        console: Whether to output colored console logs (default: True)
        json_to_stdout: If True, stdout gets JSON instead of colored text

    Usage:
        from src.utils.logging_config import setup_logging
        setup_logging(level=logging.DEBUG, json_file="logs/atlas.jsonl")
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplication
    root.handlers.clear()

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        if json_to_stdout:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(ColorConsoleFormatter())
        console_handler.setLevel(level)
        root.addHandler(console_handler)

    if json_file:
        file_handler = logging.FileHandler(json_file, mode="a")
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(level)
        root.addHandler(file_handler)


def get_logger(
    name: str, context: Optional[Dict[str, Any]] = None
) -> logging.LoggerAdapter:
    """
    Get a structured logger with optional persistent context.

    Args:
        name: Logger name (usually module name)
        context: Dict of key-value pairs included with every log entry

    Returns:
        ContextAdapter wrapping a standard logger

    Usage:
        logger = get_logger("orchestrator", {"paper_id": "10.1234/abc"})
        logger.info("Step 5 complete", extra={"context": {"beliefs": 42}})
    """
    base_logger = logging.getLogger(name)
    return ContextAdapter(base_logger, context or {})
