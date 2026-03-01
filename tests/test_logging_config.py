"""
test_logging_config.py — Test Structured JSON Logging
=====================================================

Verifies JSONFormatter output, required fields, color formatter,
and setup_logging integration.

Phase 0, Task 0.5
"""

import json
import logging
import tempfile
import os
import pytest

from src.utils.logging_config import (
    JSONFormatter,
    ColorConsoleFormatter,
    ContextAdapter,
    setup_logging,
    get_logger,
)


class TestJSONFormatter:
    """Test structured JSON log output."""

    def test_produces_valid_json(self):
        """Each log entry is valid JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=42, msg="Test message", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_required_fields_present(self):
        """Every entry has timestamp, level, module, message."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py",
            lineno=10, msg="Warning message", args=(), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "timestamp" in parsed
        assert parsed["level"] == "WARNING"
        assert "module" in parsed
        assert parsed["message"] == "Warning message"

    def test_context_included(self):
        """Context dict is included when attached to record."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="With context", args=(), exc_info=None,
        )
        record.context = {"paper_id": "10.1234/abc", "step": 5}
        parsed = json.loads(formatter.format(record))
        assert parsed["context"]["paper_id"] == "10.1234/abc"
        assert parsed["context"]["step"] == 5

    def test_exception_included(self):
        """Exception info is captured in output."""
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test", level=logging.ERROR, pathname="test.py",
                lineno=1, msg="Error occurred", args=(),
                exc_info=sys.exc_info(),
            )
        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]

    def test_timestamp_is_iso8601(self):
        """Timestamp follows ISO 8601 format."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Time test", args=(), exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        # Should parse as ISO format (contains T and timezone)
        assert "T" in parsed["timestamp"]


class TestColorConsoleFormatter:
    """Test WCAG 2.1 AA compliant console output."""

    def test_color_codes_present(self):
        """Output contains ANSI color codes."""
        formatter = ColorConsoleFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Colored output", args=(), exc_info=None,
        )
        output = formatter.format(record)
        assert "\033[" in output  # ANSI escape present

    def test_no_dark_blue(self):
        """No dark blue color codes per WCAG/CLAUDE.md requirement."""
        formatter = ColorConsoleFormatter()
        for level in [logging.DEBUG, logging.INFO, logging.WARNING,
                      logging.ERROR, logging.CRITICAL]:
            record = logging.LogRecord(
                name="test", level=level, pathname="test.py",
                lineno=1, msg="Check", args=(), exc_info=None,
            )
            output = formatter.format(record)
            # Dark blue ANSI: \033[34m or \033[0;34m
            assert "\033[34m" not in output
            assert "\033[0;34m" not in output


class TestContextAdapter:
    """Test logger with persistent context."""

    def test_context_merged(self):
        """Persistent and per-call context are merged."""
        base = logging.getLogger("test_adapter")
        adapter = ContextAdapter(base, {"session": "abc123"})

        # Create a handler to capture output
        handler = logging.Handler()
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(record)

        base.addHandler(Capture())
        base.setLevel(logging.DEBUG)

        adapter.info("Test", extra={"context": {"step": 3}})

        assert len(records) == 1
        ctx = records[0].context
        assert ctx["session"] == "abc123"
        assert ctx["step"] == 3

        # Cleanup
        base.handlers.clear()


class TestSetupLogging:
    """Test setup_logging integration."""

    def test_setup_with_json_file(self):
        """JSON file handler created when path specified."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = f.name

        try:
            setup_logging(json_file=path, console=False)
            logger = logging.getLogger("test_setup")
            logger.info("JSON file test")

            # Read and parse log file
            with open(path) as fh:
                lines = fh.readlines()
            # At least one JSON line
            assert len(lines) >= 1
            parsed = json.loads(lines[-1])
            assert parsed["message"] == "JSON file test"
        finally:
            os.unlink(path)
            # Reset logging
            logging.getLogger().handlers.clear()

    def test_get_logger_returns_adapter(self):
        """get_logger returns a ContextAdapter."""
        logger = get_logger("test_module", {"key": "val"})
        assert isinstance(logger, ContextAdapter)
