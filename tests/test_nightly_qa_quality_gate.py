"""
Test: Nightly QA Quality Gate Stage
===================================

Tests for the QA Quality Gate stage in nightly_integration_pipeline.py.

The QA Quality Gate stage:
1. Runs ExtractionFieldValidator on all extraction JSONs
2. Identifies articles below 0.75 quality threshold
3. Writes re-extraction queue to data/extraction_pipeline/reextraction_queue.json
4. Logs warnings if mean quality drops below threshold
5. Gracefully handles missing validator

Test Coverage:
- stage_qa_quality_gate with valid extractions
- Quality scoring and threshold detection
- Re-extraction queue generation
- Error handling (missing validator, missing directory)
- Low quality alert logging
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# =============================================================================
# Mock Classes
# =============================================================================

@dataclass
class MockViolation:
    """Mock violation for testing."""
    rule_id: str
    field: str
    severity: str
    message: str
    finding_index: int = 0
    details: Dict = field(default_factory=dict)


@dataclass
class MockArticleReport:
    """Mock article validation report."""
    source_file: str
    quality_score: float
    critical_errors: List[MockViolation] = field(default_factory=list)
    all_violations: List[MockViolation] = field(default_factory=list)

    def violations_by_field(self) -> Dict[str, int]:
        """Return violation counts by field."""
        counts = {}
        for v in self.all_violations:
            counts[v.field] = counts.get(v.field, 0) + 1
        return counts


@dataclass
class MockBatchReport:
    """Mock batch validation report."""
    articles: List[MockArticleReport] = field(default_factory=list)
    total_findings: int = 0
    total_violations: int = 0
    mean_score: float = 0.85

    def articles_below_threshold(self, threshold: float) -> List[MockArticleReport]:
        """Return articles below threshold."""
        return [a for a in self.articles if a.quality_score < threshold]


class MockExtractionFieldValidator:
    """Mock validator for testing."""

    def __init__(self, articles_data: Optional[Dict[str, float]] = None):
        """
        Initialize validator.

        Args:
            articles_data: Dict mapping filenames to quality scores
        """
        self.articles_data = articles_data or {}

    def validate_batch(self, extractions_dir: Path) -> MockBatchReport:
        """Validate a batch of extraction files."""
        articles = []
        total_violations = 0

        for filename, score in self.articles_data.items():
            # Generate violations based on score
            violations = []
            critical_errors = []

            if score < 0.75:
                # Low quality gets critical errors
                for i in range(max(2, int((1 - score) * 10))):
                    v = MockViolation(
                        rule_id=f"R{i+1}",
                        field=f"field_{i % 5}",
                        severity="error" if i < 2 else "warning",
                        message=f"Violation {i+1} for {filename}",
                    )
                    violations.append(v)
                    if v.severity == "critical":
                        critical_errors.append(v)

            articles.append(MockArticleReport(
                source_file=filename,
                quality_score=score,
                critical_errors=critical_errors,
                all_violations=violations,
            ))
            total_violations += len(violations)

        # Compute mean score
        mean_score = sum(a.quality_score for a in articles) / len(articles) if articles else 0.0

        return MockBatchReport(
            articles=articles,
            total_violations=total_violations,
            total_findings=len(articles),
            mean_score=mean_score,
        )


# =============================================================================
# Tests
# =============================================================================

class TestQAQualityGateStage:
    """Test the QA Quality Gate stage."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary data directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            extractions_dir = root / "extractions"
            extractions_dir.mkdir()
            pipeline_dir = root / "extraction_pipeline"
            pipeline_dir.mkdir()

            yield {
                "root": root,
                "extractions": extractions_dir,
                "pipeline": pipeline_dir,
            }

    @pytest.fixture
    def nightly_pipeline(self, temp_dirs, monkeypatch):
        """Create NightlyPipeline instance with temp directories."""
        # Import here to avoid issues if nightly_integration_pipeline not available
        try:
            from scripts.nightly_integration_pipeline import NightlyPipeline
        except ImportError:
            pytest.skip("nightly_integration_pipeline not available")

        # Patch DATA_DIR
        monkeypatch.setattr(
            "scripts.nightly_integration_pipeline.DATA_DIR",
            temp_dirs["root"],
        )

        return NightlyPipeline(dry_run=False)

    def test_stage_qa_quality_gate_high_quality(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test stage with high-quality extractions."""
        # Mock the validator with high quality scores
        articles_data = {
            "10.1234_paper1.json": 0.95,
            "10.1234_paper2.json": 0.87,
            "10.1234_paper3.json": 0.92,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert "error" not in result
        assert result["total_articles"] == 3
        assert result["articles_below_threshold"] == 0
        assert result["mean_quality"] == pytest.approx(0.913, abs=0.01)
        assert result["threshold"] == 0.75
        assert "reextraction_queue_path" in result

    def test_stage_qa_quality_gate_mixed_quality(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test stage with mixed quality extractions."""
        articles_data = {
            "10.1234_paper1.json": 0.95,
            "10.1234_paper2.json": 0.55,  # Below threshold
            "10.1234_paper3.json": 0.70,  # Below threshold
            "10.1234_paper4.json": 0.82,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert result["total_articles"] == 4
        assert result["articles_below_threshold"] == 2
        assert result["mean_quality"] == pytest.approx(0.755, abs=0.01)
        assert result["threshold"] == 0.75
        assert result["total_violations"] > 0

        # Verify re-extraction queue file exists
        queue_path = Path(result["reextraction_queue_path"])
        assert queue_path.exists()

        # Verify queue contents
        queue_data = json.loads(queue_path.read_text())
        assert queue_data["total_articles"] == 4
        assert queue_data["articles_below_threshold"] == 2
        assert len(queue_data["queue"]) == 2
        assert queue_data["queue"][0]["file"] in [
            "10.1234_paper2.json",
            "10.1234_paper3.json",
        ]

    def test_stage_qa_quality_gate_all_low_quality(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test stage when all articles are below threshold."""
        articles_data = {
            "10.1234_paper1.json": 0.50,
            "10.1234_paper2.json": 0.60,
            "10.1234_paper3.json": 0.70,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert result["total_articles"] == 3
        assert result["articles_below_threshold"] == 3
        assert result["mean_quality"] == pytest.approx(0.60, abs=0.01)

    def test_stage_qa_quality_gate_empty_directory(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test stage when extractions directory exists but is empty."""
        mock_validator = MockExtractionFieldValidator({})

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert result["total_articles"] == 0
        assert result["articles_below_threshold"] == 0

    def test_stage_qa_quality_gate_missing_directory(self, nightly_pipeline, monkeypatch):
        """Test stage when extractions directory doesn't exist."""
        # Ensure directory doesn't exist
        monkeypatch.setattr(
            "scripts.nightly_integration_pipeline.DATA_DIR",
            Path("/nonexistent/path"),
        )

        result = nightly_pipeline.stage_qa_quality_gate()

        assert result["skipped"] is True
        assert "reason" in result

    def test_stage_qa_quality_gate_validator_unavailable(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test graceful degradation when validator is unavailable."""
        monkeypatch.setattr(
            "scripts.nightly_integration_pipeline.DATA_DIR",
            temp_dirs["root"],
        )

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            side_effect=ImportError("Validator not available"),
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert result["skipped"] is True
        assert "validator unavailable" in result.get("reason", "").lower()

    def test_stage_qa_quality_gate_validation_error(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test error handling during validation."""
        mock_validator = Mock()
        mock_validator.validate_batch.side_effect = RuntimeError("Validation failed")

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        assert "error" in result

    def test_reextraction_queue_structure(self, nightly_pipeline, temp_dirs, monkeypatch):
        """Test that re-extraction queue has correct structure."""
        articles_data = {
            "10.1234_paper1.json": 0.70,
            "10.1234_paper2.json": 0.60,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        queue_path = Path(result["reextraction_queue_path"])
        queue_data = json.loads(queue_path.read_text())

        # Verify required fields
        assert "generated_at" in queue_data
        assert "threshold" in queue_data
        assert "total_articles" in queue_data
        assert "articles_below_threshold" in queue_data
        assert "mean_quality" in queue_data
        assert "queue" in queue_data
        assert isinstance(queue_data["queue"], list)

        # Verify each queue item
        for item in queue_data["queue"]:
            assert "file" in item
            assert "quality_score" in item
            assert "critical_errors" in item
            assert "total_violations" in item
            assert "top_violations" in item

    def test_stage_quality_gate_alert_threshold(self, nightly_pipeline, temp_dirs, monkeypatch, caplog):
        """Test that warning is logged when mean quality drops below threshold."""
        import logging
        caplog.set_level(logging.WARNING)

        articles_data = {
            "10.1234_paper1.json": 0.70,
            "10.1234_paper2.json": 0.72,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        # Mean quality is below 0.75, should trigger alert
        assert result["mean_quality"] < 0.75
        assert any("ALERT" in record.message for record in caplog.records)

    def test_stage_quality_gate_no_alert_above_threshold(self, nightly_pipeline, temp_dirs, monkeypatch, caplog):
        """Test that no alert is logged when mean quality is above threshold."""
        import logging
        caplog.set_level(logging.WARNING)

        articles_data = {
            "10.1234_paper1.json": 0.90,
            "10.1234_paper2.json": 0.85,
        }

        mock_validator = MockExtractionFieldValidator(articles_data)

        with patch(
            "src.qa.extraction_field_validator.ExtractionFieldValidator",
            return_value=mock_validator,
        ):
            result = nightly_pipeline.stage_qa_quality_gate()

        # Mean quality is above 0.75, should not trigger alert
        assert result["mean_quality"] > 0.75
        assert not any("ALERT" in record.message for record in caplog.records)


class TestQAQualityGateIntegration:
    """Integration tests for QA quality gate in the full pipeline."""

    def test_qa_stage_in_pipeline_stages_list(self):
        """Verify that QA quality gate stage is in the pipeline's stages list."""
        try:
            from scripts.nightly_integration_pipeline import NightlyPipeline
        except ImportError:
            pytest.skip("nightly_integration_pipeline not available")

        pipeline = NightlyPipeline(dry_run=True)

        # Mock run to get the stages list
        with patch.object(pipeline, 'run_stage'):
            # Check that qa_quality_gate is in the run method's all_stages
            import inspect
            source = inspect.getsource(pipeline.run)
            assert "qa_quality_gate" in source

    def test_qa_stage_position_after_extraction(self):
        """Verify QA quality gate stage runs after extraction stages."""
        try:
            from scripts.nightly_integration_pipeline import NightlyPipeline
        except ImportError:
            pytest.skip("nightly_integration_pipeline not available")

        pipeline = NightlyPipeline(dry_run=True)

        import inspect
        source = inspect.getsource(pipeline.run)

        # Find positions of extraction and qa_quality_gate
        extraction_pos = source.find("extraction")
        qa_pos = source.find("qa_quality_gate")

        # QA should come after extraction
        assert extraction_pos < qa_pos
        assert qa_pos > 0

    def test_qa_stage_position_before_auto_approve(self):
        """Verify QA quality gate stage runs before auto-approve."""
        try:
            from scripts.nightly_integration_pipeline import NightlyPipeline
        except ImportError:
            pytest.skip("nightly_integration_pipeline not available")

        pipeline = NightlyPipeline(dry_run=True)

        import inspect
        source = inspect.getsource(pipeline.run)

        # Find positions of qa_quality_gate and auto_approve
        qa_pos = source.find("qa_quality_gate")
        approve_pos = source.find("auto_approve")

        # QA should come before auto-approve
        assert qa_pos < approve_pos
        assert qa_pos > 0
