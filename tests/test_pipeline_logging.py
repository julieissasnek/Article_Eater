"""
Tests for Sprint 2.0.5: Pipeline logging and error handling.

Created: 2026-02-08
"""

import json
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.pipeline_logging import (
    PipelineError,
    ExtractionError,
    LLMError,
    ConfigurationError,
    WebIntegrationError,
    SerializationError,
    DatabaseError,
    ValidationError,
    RetryableError,
    ErrorSeverity,
    ErrorCollector,
    ErrorRecord,
    configure_logging,
    get_logger,
    with_retry,
    pipeline_stage,
)


# =============================================================================
# EXCEPTION HIERARCHY TESTS
# =============================================================================


class TestPipelineError:
    """Tests for the PipelineError base class."""

    def test_basic_creation(self):
        """Test basic error creation."""
        err = PipelineError("Something went wrong")
        assert err.message == "Something went wrong"
        assert err.stage is None
        assert err.paper_id is None
        assert err.recoverable is False
        assert err.context == {}
        assert err.timestamp is not None

    def test_with_metadata(self):
        """Test error with full metadata."""
        err = PipelineError(
            "Extraction failed",
            stage="extraction",
            paper_id="paper123",
            recoverable=True,
            context={"file": "test.pdf"},
        )
        assert err.stage == "extraction"
        assert err.paper_id == "paper123"
        assert err.recoverable is True
        assert err.context == {"file": "test.pdf"}

    def test_to_dict(self):
        """Test serialization to dictionary."""
        err = PipelineError("Test error", stage="test", paper_id="p1")
        d = err.to_dict()

        assert d["error_type"] == "PipelineError"
        assert d["message"] == "Test error"
        assert d["stage"] == "test"
        assert d["paper_id"] == "p1"
        assert d["recoverable"] is False
        assert "timestamp" in d


class TestSpecializedErrors:
    """Tests for specialized error types."""

    def test_extraction_error(self):
        """Test ExtractionError has correct stage."""
        err = ExtractionError("PDF parsing failed")
        assert err.stage == "extraction"

    def test_llm_error(self):
        """Test LLMError has correct stage."""
        err = LLMError("API timeout")
        assert err.stage == "llm_extraction"

    def test_configuration_error(self):
        """Test ConfigurationError has correct stage."""
        err = ConfigurationError("Missing API key")
        assert err.stage == "configuration"

    def test_web_integration_error(self):
        """Test WebIntegrationError has correct stage."""
        err = WebIntegrationError("Coherence computation failed")
        assert err.stage == "web_integration"

    def test_serialization_error(self):
        """Test SerializationError has correct stage."""
        err = SerializationError("JSON encoding failed")
        assert err.stage == "serialization"

    def test_database_error(self):
        """Test DatabaseError has correct stage."""
        err = DatabaseError("Connection refused")
        assert err.stage == "database"

    def test_validation_error(self):
        """Test ValidationError has correct stage."""
        err = ValidationError("Invalid input format")
        assert err.stage == "validation"

    def test_retryable_error(self):
        """Test RetryableError is marked recoverable."""
        err = RetryableError("Transient failure", max_retries=5)
        assert err.recoverable is True
        assert err.max_retries == 5


# =============================================================================
# ERROR COLLECTOR TESTS
# =============================================================================


class TestErrorCollector:
    """Tests for ErrorCollector."""

    def test_basic_collection(self):
        """Test basic error collection."""
        collector = ErrorCollector("run123", "paper456")
        assert collector.run_id == "run123"
        assert collector.paper_id == "paper456"
        assert len(collector.errors) == 0

    def test_record_exception(self):
        """Test recording an exception."""
        collector = ErrorCollector("run1", "paper1")
        try:
            raise ValueError("Test error")
        except ValueError as e:
            record = collector.record(e, ErrorSeverity.WARNING, "test")

        assert len(collector.errors) == 1
        assert record.error_type == "ValueError"
        assert record.message == "Test error"
        assert record.severity == ErrorSeverity.WARNING
        assert record.stage == "test"

    def test_record_pipeline_error(self):
        """Test recording a PipelineError."""
        collector = ErrorCollector("run1")
        err = ExtractionError("PDF failed", paper_id="p1", context={"file": "x.pdf"})
        record = collector.record(err, ErrorSeverity.BLOCKING, "extraction")

        assert record.error_type == "ExtractionError"
        assert record.recoverable is False
        assert record.context == {"file": "x.pdf"}

    def test_record_string(self):
        """Test recording a string error."""
        collector = ErrorCollector("run1")
        record = collector.record("Something went wrong", ErrorSeverity.INFO, "info")

        assert record.message == "Something went wrong"
        assert record.error_type == "Error"

    def test_has_fatal_errors(self):
        """Test fatal error detection."""
        collector = ErrorCollector("run1")
        assert not collector.has_fatal_errors()

        collector.record("Warning", ErrorSeverity.WARNING, "test")
        assert not collector.has_fatal_errors()

        collector.record("Fatal", ErrorSeverity.FATAL, "test")
        assert collector.has_fatal_errors()

    def test_has_blocking_errors(self):
        """Test blocking error detection."""
        collector = ErrorCollector("run1")
        assert not collector.has_blocking_errors()

        collector.record("Warning", ErrorSeverity.WARNING, "test")
        assert not collector.has_blocking_errors()

        collector.record("Blocking", ErrorSeverity.BLOCKING, "test")
        assert collector.has_blocking_errors()

    def test_get_errors_by_stage(self):
        """Test filtering errors by stage."""
        collector = ErrorCollector("run1")
        collector.record("Error 1", ErrorSeverity.WARNING, "stage_a")
        collector.record("Error 2", ErrorSeverity.WARNING, "stage_b")
        collector.record("Error 3", ErrorSeverity.WARNING, "stage_a")

        stage_a_errors = collector.get_errors_by_stage("stage_a")
        assert len(stage_a_errors) == 2

    def test_get_summary(self):
        """Test error summary generation."""
        collector = ErrorCollector("run1")
        collector.record("Fatal error", ErrorSeverity.FATAL, "init")
        collector.record("Warning 1", ErrorSeverity.WARNING, "extract")
        collector.record("Warning 2", ErrorSeverity.WARNING, "extract")
        collector.record(RetryableError("Retry me"), ErrorSeverity.DEGRADED, "web")

        summary = collector.get_summary()
        assert summary["total_errors"] == 4
        assert summary["has_fatal"] is True
        assert summary["has_blocking"] is True
        assert summary["by_severity"]["FATAL"] == 1
        assert summary["by_severity"]["WARNING"] == 2
        assert summary["by_stage"]["extract"] == 2
        assert summary["recoverable_count"] == 1

    def test_to_jsonl(self):
        """Test writing errors to JSONL file."""
        collector = ErrorCollector("run1", "paper1")
        collector.record("Error 1", ErrorSeverity.WARNING, "test")
        collector.record("Error 2", ErrorSeverity.FATAL, "test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "errors.jsonl"
            count = collector.to_jsonl(path)

            assert count == 2
            assert path.exists()

            lines = path.read_text().strip().split("\n")
            assert len(lines) == 2

            record1 = json.loads(lines[0])
            assert record1["message"] == "Error 1"
            assert record1["severity"] == "WARNING"


# =============================================================================
# RETRY MECHANISM TESTS
# =============================================================================


class TestRetryMechanism:
    """Tests for the retry decorator."""

    def test_successful_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @with_retry(max_retries=3)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "success"

        result = succeed()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_failure(self):
        """Test function retries on failure then succeeds."""
        call_count = 0

        @with_retry(max_retries=3, delay=0.01)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient failure")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """Test raises after max retries."""
        call_count = 0

        @with_retry(max_retries=2, delay=0.01)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent failure")

        with pytest.raises(ValueError, match="Permanent failure"):
            always_fail()

        assert call_count == 3  # 1 initial + 2 retries

    def test_specific_exception_types(self):
        """Test only specified exceptions are retried."""
        call_count = 0

        @with_retry(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def fail_with_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            fail_with_type_error()

        assert call_count == 1  # No retries for TypeError


# =============================================================================
# LOGGING CONFIGURATION TESTS
# =============================================================================


class TestLoggingConfiguration:
    """Tests for logging configuration."""

    def test_get_logger(self):
        """Test logger name prefixing."""
        logger = get_logger("pipeline")
        assert logger.name == "ae.pipeline"

    def test_configure_logging(self):
        """Test logging configuration."""
        configure_logging(level="DEBUG", format_type="simple")
        logger = get_logger("test")
        assert logger.level == logging.NOTSET  # Inherits from parent
        # Root ae logger should be DEBUG
        assert logging.getLogger("ae").level == logging.DEBUG


# =============================================================================
# PIPELINE STAGE CONTEXT MANAGER TESTS
# =============================================================================


class TestPipelineStage:
    """Tests for pipeline_stage context manager."""

    def test_successful_stage(self):
        """Test successful stage execution."""
        collector = ErrorCollector("run1")

        with pipeline_stage("extraction", collector, "paper1") as stage:
            stage.log_info("Processing...")
            stage.result = {"findings": 5}

        assert stage.success is True
        assert len(collector.errors) == 0

    def test_failed_stage_with_exception(self):
        """Test stage that raises exception."""
        collector = ErrorCollector("run1")

        with pytest.raises(ValueError):
            with pipeline_stage("extraction", collector, "paper1") as stage:
                raise ValueError("Extraction failed")

        assert stage.success is False
        assert len(collector.errors) == 1
        assert collector.errors[0].error_type == "ValueError"

    def test_failed_stage_with_pipeline_error(self):
        """Test stage that raises PipelineError."""
        collector = ErrorCollector("run1")

        with pytest.raises(ExtractionError):
            with pipeline_stage("extraction", collector, "paper1") as stage:
                raise ExtractionError("PDF corrupted")

        assert len(collector.errors) == 1
        assert collector.errors[0].error_type == "ExtractionError"

    def test_record_error_manually(self):
        """Test manually recording errors in stage."""
        collector = ErrorCollector("run1")

        with pipeline_stage("extraction", collector, "paper1") as stage:
            stage.record_error("Non-fatal issue", ErrorSeverity.WARNING)
            # Stage continues despite error

        assert len(collector.errors) == 1
        assert collector.errors[0].severity == ErrorSeverity.WARNING


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for error handling system."""

    def test_full_error_workflow(self):
        """Test complete error handling workflow."""
        # Create collector
        collector = ErrorCollector("ae.run.20260208", "paper_test_001")

        # Simulate pipeline stages
        with pipeline_stage("validation", collector, "paper_test_001") as stage:
            stage.log_info("Validating input bundle")
            # Validation passes

        with pipeline_stage("extraction", collector, "paper_test_001") as stage:
            stage.log_info("Extracting text")
            stage.record_error("PDF quality warning", ErrorSeverity.WARNING)
            # Continue despite warning

        # Check final state
        assert len(collector.errors) == 1
        assert not collector.has_blocking_errors()

        summary = collector.get_summary()
        assert summary["total_errors"] == 1
        assert summary["by_severity"]["WARNING"] == 1

    def test_error_serialization_roundtrip(self):
        """Test errors can be serialized and read back."""
        collector = ErrorCollector("run1", "paper1")

        # Add various error types
        collector.record(ExtractionError("PDF failed", context={"page": 5}), ErrorSeverity.BLOCKING, "extraction")
        collector.record(LLMError("Timeout"), ErrorSeverity.DEGRADED, "llm")
        collector.record("Generic warning", ErrorSeverity.WARNING, "misc")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "errors.jsonl"
            collector.to_jsonl(path)

            # Read back
            lines = path.read_text().strip().split("\n")
            records = [json.loads(line) for line in lines]

            assert len(records) == 3
            assert records[0]["error_type"] == "ExtractionError"
            assert records[0]["context"]["page"] == 5
            assert records[1]["error_type"] == "LLMError"
            assert records[2]["error_type"] == "Error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
