"""Tests for extraction field validator blocking gate.

Tests the Phase 1B quality gate functionality:
- validate_and_gate: determines if extraction passes threshold
- gate_extraction: moves failing extractions to repair queue
- Repair queue management and violation logging
"""

import json
import pytest
import tempfile
from pathlib import Path

from src.qa.extraction_field_validator import (
    ExtractionFieldValidator,
    gate_extraction,
)


@pytest.fixture
def temp_extractions_dir():
    """Temporary directory for extraction files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def validator():
    return ExtractionFieldValidator()


def create_good_finding():
    """Create a finding that passes all validations."""
    return {
        "antecedent": "Ceiling height (3.0m vs 2.4m)",
        "consequent": "cognitive performance",
        "direction": "increase",
        "claim_type": "empirical_finding",
        "measure_type": "cognitive",
        "outcome_domain": "cognition",
        "p_value": 0.03,
        "effect_size": 0.45,
        "effect_size_type": "Cohen's d",
        "sample_size": 60,
        "confidence_interval": [0.1, 0.8],
        "test_statistic": 2.15,
        # Phase 1A principle-compliance fields (required for Phase 1B validator)
        "causal_tier": "EXPERIMENTAL",
        "justification_status": "GROUNDED",
        "defeater_search_status": "none_reported",
        "scope_conditions": {
            "setting": "lab",
            "population": "university students",
            "climate": "temperate",
            "duration": "acute",
            "measurement_type": "cognitive_task"
        },
        "source_quality_indicators": {
            "pre_registered": False,
            "blinding": "none",
            "independence_flag": True,
            "replication_status": "original"
        },
        "defeat_relationships": [],
        "conflict_type": None,
        "epistemic_level": "EMPIRICAL",
    }


def create_bad_finding():
    """Create a finding with critical violations."""
    return {
        "antecedent": "",  # NULL_ANTECEDENT
        "consequent": "",  # NULL_CONSEQUENT
        "direction": None,
        "claim_type": "empirical_finding",
        "p_value": None,
        "effect_size": None,
    }


def create_extraction_with_n_findings(n_good: int, n_bad: int):
    """Create an extraction JSON with specified number of good and bad findings."""
    findings = []
    for _ in range(n_good):
        findings.append(create_good_finding())
    for _ in range(n_bad):
        findings.append(create_bad_finding())

    return {
        "article_type": "empirical",
        "findings": findings,
        "_meta": {"source": "test"},
    }


class TestValidateAndGate:
    """Test the validate_and_gate function."""

    def test_passing_extraction_returns_passed_true(self, validator, temp_extractions_dir):
        """Test that a high-quality extraction returns passed=True."""
        extraction_file = temp_extractions_dir / "good_article.json"
        extraction_data = create_extraction_with_n_findings(5, 0)  # All good
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        passed, score, violations = validator.validate_and_gate(
            extraction_file, threshold=0.75
        )

        assert passed is True
        assert score >= 0.75
        # Some violations may exist (warnings) but score should be high
        assert isinstance(violations, list)

    def test_failing_extraction_returns_passed_false(self, validator, temp_extractions_dir):
        """Test that a low-quality extraction returns passed=False."""
        extraction_file = temp_extractions_dir / "bad_article.json"
        extraction_data = create_extraction_with_n_findings(0, 5)  # All bad
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        passed, score, violations = validator.validate_and_gate(
            extraction_file, threshold=0.75
        )

        assert passed is False
        assert score < 0.75
        assert len(violations) > 0

    def test_violations_are_serializable_dicts(self, validator, temp_extractions_dir):
        """Test that returned violations are serializable dicts."""
        extraction_file = temp_extractions_dir / "violations_test.json"
        extraction_data = create_extraction_with_n_findings(0, 1)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        passed, score, violations = validator.validate_and_gate(extraction_file)

        assert len(violations) > 0
        for violation in violations:
            assert isinstance(violation, dict)
            # Should be serializable
            serialized = json.dumps(violation)
            assert isinstance(serialized, str)

    def test_custom_threshold(self, validator, temp_extractions_dir):
        """Test that custom thresholds are respected."""
        extraction_file = temp_extractions_dir / "threshold_test.json"
        extraction_data = create_extraction_with_n_findings(3, 1)  # Mixed
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        # With strict threshold, should fail
        passed_strict, score, _ = validator.validate_and_gate(
            extraction_file, threshold=0.95
        )

        # With lenient threshold, should pass
        passed_lenient, _, _ = validator.validate_and_gate(
            extraction_file, threshold=0.50
        )

        # Score should be the same
        _, score_check, _ = validator.validate_and_gate(extraction_file, threshold=0.75)
        assert abs(score - score_check) < 0.001

        # At least one of the two should differ
        assert passed_strict != passed_lenient


class TestGateExtraction:
    """Test the gate_extraction function that moves failing files."""

    def test_passing_extraction_not_moved(self, temp_extractions_dir):
        """Test that passing extractions are NOT moved to repair queue."""
        extraction_file = temp_extractions_dir / "passing.json"
        extraction_data = create_extraction_with_n_findings(10, 0)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        result = gate_extraction(extraction_file, threshold=0.75)

        # Check result structure
        assert result["passed"] is True
        assert result["score"] >= 0.75
        assert result["original_path"] == str(extraction_file)
        assert result["new_path"] is None
        assert result["n_violations"] >= 0

        # File should still exist in original location
        assert extraction_file.exists()
        # Repair queue should not exist or be empty
        repair_dir = temp_extractions_dir / "needs_repair"
        if repair_dir.exists():
            repair_files = list(repair_dir.glob("*.json"))
            assert len(repair_files) == 0

    def test_failing_extraction_moved_to_repair(self, temp_extractions_dir):
        """Test that failing extractions are moved to repair queue."""
        extraction_file = temp_extractions_dir / "failing.json"
        extraction_data = create_extraction_with_n_findings(0, 10)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        result = gate_extraction(extraction_file, threshold=0.75)

        # Check result structure
        assert result["passed"] is False
        assert result["score"] < 0.75
        assert result["original_path"] == str(extraction_file)
        assert result["new_path"] is not None
        assert result["n_violations"] > 0

        # Original file should NOT exist
        assert not extraction_file.exists()

        # File should exist in repair queue
        repair_path = Path(result["new_path"])
        assert repair_path.exists()
        assert repair_path.parent.name == "needs_repair"

    def test_violations_json_created(self, temp_extractions_dir):
        """Test that a .violations.json file is created for failed extractions."""
        extraction_file = temp_extractions_dir / "violations_manifest_test.json"
        extraction_data = create_extraction_with_n_findings(1, 5)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        result = gate_extraction(extraction_file, threshold=0.75)

        if not result["passed"]:  # If it failed
            # Find violations file
            repair_dir = temp_extractions_dir / "needs_repair"
            violations_files = list(repair_dir.glob("*.violations.json"))

            assert len(violations_files) > 0
            violations_file = violations_files[0]

            # Verify content
            manifest = json.loads(violations_file.read_text(encoding="utf-8"))
            assert "original_path" in manifest
            assert "repair_queue_path" in manifest
            assert "quality_score" in manifest
            assert "threshold" in manifest
            assert "timestamp" in manifest
            assert "violation_count" in manifest
            assert "violations" in manifest
            assert isinstance(manifest["violations"], list)

    def test_custom_threshold_gates_correctly(self, temp_extractions_dir):
        """Test that custom thresholds control gating decisions."""
        extraction_file = temp_extractions_dir / "threshold_gate_test.json"
        extraction_data = create_extraction_with_n_findings(3, 1)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        # First, gate with strict threshold
        result_strict = gate_extraction(extraction_file, threshold=0.95)

        # After gating, restore the file from repair queue for second test
        repair_dir = temp_extractions_dir / "needs_repair"
        extraction_file = temp_extractions_dir / "threshold_gate_test2.json"
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        # Then gate with lenient threshold
        result_lenient = gate_extraction(extraction_file, threshold=0.50)

        # At least one should differ
        assert result_strict["passed"] != result_lenient["passed"]

    def test_missing_file_handled_gracefully(self, temp_extractions_dir):
        """Test that missing files are handled gracefully."""
        missing_file = temp_extractions_dir / "nonexistent.json"

        # Missing file should fail gracefully (return failed result or raise)
        try:
            result = gate_extraction(missing_file)
            # If it returns, it should indicate failure
            # The function tries to move the file but fails, which is expected
            # Just check that it didn't crash
            assert "message" in result or "error" in result or not result.get("passed")
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            # Exceptions are also acceptable
            pass

    def test_repair_queue_dir_created_if_needed(self, temp_extractions_dir):
        """Test that repair queue directory is created automatically."""
        extraction_file = temp_extractions_dir / "create_repair_dir_test.json"
        extraction_data = create_extraction_with_n_findings(0, 5)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        repair_dir = temp_extractions_dir / "needs_repair"
        assert not repair_dir.exists()

        result = gate_extraction(extraction_file, threshold=0.75)

        # After gating, repair dir should exist
        assert repair_dir.exists()
        assert result["passed"] is False

    def test_gating_multiple_files(self, temp_extractions_dir):
        """Test gating multiple extraction files in sequence."""
        files_to_gate = []
        for i in range(3):
            extraction_file = temp_extractions_dir / f"batch_test_{i}.json"
            if i < 2:
                # First 2 are good
                extraction_data = create_extraction_with_n_findings(5, 0)
            else:
                # Last one is bad
                extraction_data = create_extraction_with_n_findings(0, 5)
            extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")
            files_to_gate.append(extraction_file)

        # Gate them all
        results = []
        for filepath in files_to_gate:
            result = gate_extraction(filepath, threshold=0.75)
            results.append(result)

        # Check results
        assert len(results) == 3
        assert results[0]["passed"] is True
        assert results[1]["passed"] is True
        assert results[2]["passed"] is False

        # Verify repair queue has 1 file
        repair_dir = temp_extractions_dir / "needs_repair"
        repair_files = [f for f in repair_dir.glob("*.json") if not f.name.endswith(".violations.json")]
        assert len(repair_files) == 1

    def test_result_message_is_informative(self, temp_extractions_dir):
        """Test that result messages provide useful information."""
        extraction_file = temp_extractions_dir / "message_test.json"
        extraction_data = create_extraction_with_n_findings(0, 3)
        extraction_file.write_text(json.dumps(extraction_data), encoding="utf-8")

        result = gate_extraction(extraction_file, threshold=0.75)

        assert "message" in result
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0
        # Message should mention pass/fail status
        assert "PASS" in result["message"] or "FAIL" in result["message"]
        # Should mention score
        assert str(round(result["score"], 2)) in result["message"] or "score" in result["message"].lower()
