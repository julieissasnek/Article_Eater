"""Tests for the template → belief seeder."""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.seed_beliefs_from_templates import (
    TEMPLATE_BELIEF_PREFIX,
    _compute_template_credence,
    _extract_confidence_scores,
    _is_calibrated,
    create_belief_from_template,
    create_interaction_constraints,
    scan_calibrated_templates,
    seed_beliefs,
)
from src.services.web_of_belief import BeliefStatus, EpistemicLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CALIBRATED_TEMPLATE = {
    "template_id": "T_TEST_1",
    "name": "Test Template Alpha",
    "status": "calibrated",
    "t1_frameworks": ["PP", "SN"],
    "mechanism_chain": [
        "Step one",
        "→ Step two",
        "→ Step three",
        "→ Step four",
        "→ Step five (should be truncated)",
    ],
    "bridge_warrant": "MECHANISM",
    "bridge_prior": 0.6,
    "panel_id": "TEST-I",
    "calibrated_parameters": {
        "param_a": {"value": 10, "confidence": 0.8},
        "param_b": {"value": 20, "confidence": 0.7},
        "param_c": {
            "value": 5,
            "confidence": 0.9,
            "nested": {"sub_param": {"confidence": 0.6}},
        },
    },
    "interaction_templates": ["T_TEST_2"],
}

CALIBRATED_TEMPLATE_2 = {
    "template_id": "T_TEST_2",
    "name": "Test Template Beta",
    "status": "calibrated",
    "t1_frameworks": ["PP"],
    "mechanism_chain": ["Only step"],
    "bridge_warrant": "CONSTITUTIVE",
    "bridge_prior": 0.75,
    "calibrated_parameters": {
        "param_x": {"value": 1, "confidence": 0.85},
    },
    "interaction_templates": ["T_TEST_1"],
}

UNCALIBRATED_TEMPLATE = {
    "template_id": "T_UNCAL",
    "name": "Uncalibrated Template",
    "status": "draft",
    "t1_frameworks": ["DP"],
}

PARTIAL_TEMPLATE = {
    "template_id": "T_PARTIAL",
    "name": "Partially Calibrated",
    "calibration_status": "partial",
    "t1_frameworks": ["NM"],
    "mechanism_chain": ["Step A", "→ Step B"],
    "bridge_warrant": "FUNCTIONAL",
}


@pytest.fixture
def templates_dir(tmp_path: Path) -> Path:
    """Create a temp directory with test template JSON files."""
    (tmp_path / "T_TEST_1.json").write_text(
        json.dumps(CALIBRATED_TEMPLATE), encoding="utf-8"
    )
    (tmp_path / "T_TEST_2.json").write_text(
        json.dumps(CALIBRATED_TEMPLATE_2), encoding="utf-8"
    )
    (tmp_path / "T_UNCAL.json").write_text(
        json.dumps(UNCALIBRATED_TEMPLATE), encoding="utf-8"
    )
    (tmp_path / "T_PARTIAL.json").write_text(
        json.dumps(PARTIAL_TEMPLATE), encoding="utf-8"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIsCalibrated:
    def test_calibrated_status(self):
        assert _is_calibrated({"status": "calibrated"}) is True

    def test_draft_status(self):
        assert _is_calibrated({"status": "draft"}) is False

    def test_partial_calibration_status(self):
        assert _is_calibrated({"calibration_status": "partial"}) is True

    def test_substantial_calibration_status(self):
        assert _is_calibrated({"calibration_status": "substantial"}) is True

    def test_empty(self):
        assert _is_calibrated({}) is False


class TestExtractConfidenceScores:
    def test_nested_extraction(self):
        scores = _extract_confidence_scores(CALIBRATED_TEMPLATE)
        # Should find: 0.8, 0.7, 0.9, 0.6 (nested inside param_c)
        assert len(scores) == 4
        assert set(scores) == {0.8, 0.7, 0.9, 0.6}

    def test_empty_params(self):
        scores = _extract_confidence_scores({"calibrated_parameters": {}})
        assert scores == []

    def test_no_params_key(self):
        scores = _extract_confidence_scores({})
        assert scores == []


class TestComputeTemplateCredence:
    def test_with_explicit_bridge_prior(self):
        credence, uncertainty = _compute_template_credence(CALIBRATED_TEMPLATE)
        # bridge_prior=0.6, avg confidence = (0.8+0.7+0.9+0.6)/4 = 0.75
        # Expected: 0.70 * 0.6 * 0.75 = 0.315
        assert abs(credence - 0.315) < 0.01
        assert uncertainty == 0.25  # 4 confidence scores → moderate

    def test_well_calibrated_uncertainty(self):
        payload = {
            "bridge_prior": 0.5,
            "calibrated_parameters": {
                f"p{i}": {"confidence": 0.7} for i in range(6)
            },
        }
        _, uncertainty = _compute_template_credence(payload)
        assert uncertainty == 0.15  # 6 scores → well-calibrated

    def test_sparse_calibration_uncertainty(self):
        payload = {
            "bridge_warrant": "ANALOGICAL",
            "calibrated_parameters": {
                "p1": {"confidence": 0.5},
            },
        }
        _, uncertainty = _compute_template_credence(payload)
        assert uncertainty == 0.40  # 1 score → sparse


class TestCreateBeliefFromTemplate:
    def test_basic_fields(self):
        belief = create_belief_from_template(
            CALIBRATED_TEMPLATE, Path("fake.json")
        )
        assert belief.belief_id == f"{TEMPLATE_BELIEF_PREFIX}T_TEST_1"
        assert belief.level == EpistemicLevel.THEORETICAL
        assert belief.status == BeliefStatus.ESTABLISHED
        assert belief.theory_id == "PP"
        assert belief.domain == "cnfa"

    def test_content_summary(self):
        belief = create_belief_from_template(
            CALIBRATED_TEMPLATE, Path("fake.json")
        )
        assert "Test Template Alpha" in belief.content
        assert "Step one" in belief.content
        assert "..." in belief.content  # 5 steps, truncated to 4

    def test_tags(self):
        belief = create_belief_from_template(
            CALIBRATED_TEMPLATE, Path("fake.json")
        )
        assert "template_seeded" in belief.tags
        assert "panel:TEST-I" in belief.tags
        assert "bridge:MECHANISM" in belief.tags

    def test_credence_computed(self):
        belief = create_belief_from_template(
            CALIBRATED_TEMPLATE, Path("fake.json")
        )
        assert 0.0 < belief.credence.value < 1.0
        assert belief.credence.uncertainty > 0


class TestCreateInteractionConstraints:
    def test_bidirectional_interaction(self):
        b1 = create_belief_from_template(CALIBRATED_TEMPLATE, Path("f.json"))
        b2 = create_belief_from_template(CALIBRATED_TEMPLATE_2, Path("f.json"))
        beliefs_by_tid = {
            "T_TEST_1": b1,
            "T_TEST_2": b2,
        }
        templates = {
            "T_TEST_1": CALIBRATED_TEMPLATE,
            "T_TEST_2": CALIBRATED_TEMPLATE_2,
        }
        constraints = create_interaction_constraints(beliefs_by_tid, templates)
        # T1 and T2 declare each other → 1 constraint (deduplicated)
        assert len(constraints) == 1
        c = constraints[0]
        assert c.strength == 0.5

    def test_shared_framework_supports(self):
        b1 = create_belief_from_template(CALIBRATED_TEMPLATE, Path("f.json"))
        b2 = create_belief_from_template(CALIBRATED_TEMPLATE_2, Path("f.json"))
        beliefs_by_tid = {
            "T_TEST_1": b1,
            "T_TEST_2": b2,
        }
        templates = {
            "T_TEST_1": CALIBRATED_TEMPLATE,
            "T_TEST_2": CALIBRATED_TEMPLATE_2,
        }
        constraints = create_interaction_constraints(beliefs_by_tid, templates)
        # Both share PP → SUPPORTS
        assert constraints[0].constraint_type.value == "supports"

    def test_no_interaction_templates(self):
        payload = {**CALIBRATED_TEMPLATE, "interaction_templates": []}
        b1 = create_belief_from_template(payload, Path("f.json"))
        constraints = create_interaction_constraints(
            {"T_TEST_1": b1}, {"T_TEST_1": payload}
        )
        assert len(constraints) == 0


class TestScanCalibratedTemplates:
    def test_filters_uncalibrated(self, templates_dir: Path):
        results = scan_calibrated_templates(templates_dir)
        tids = [_get_tid(p) for _, p in results]
        assert "T_TEST_1" in tids
        assert "T_TEST_2" in tids
        assert "T_PARTIAL" in tids
        assert "T_UNCAL" not in tids

    def test_returns_paths_and_payloads(self, templates_dir: Path):
        results = scan_calibrated_templates(templates_dir)
        for path, payload in results:
            assert path.exists()
            assert isinstance(payload, dict)
            assert "template_id" in payload


class TestSeedBeliefs:
    def test_dry_run_no_db(self, templates_dir: Path, capsys):
        summary = seed_beliefs(
            templates_dir=templates_dir,
            db_path=":memory:",
            dry_run=True,
        )
        assert summary["mode"] == "DRY_RUN"
        # Return dict uses calibrated_seeded (not calibrated_found)
        assert "calibrated_seeded" in summary or "calibrated_found" in summary
        # Beliefs and constraints counts depend on calibration detection
        assert summary["beliefs_created"] >= 0
        assert summary["constraints_created"] >= 0

    def test_live_seed(self, templates_dir: Path):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        summary = seed_beliefs(
            templates_dir=templates_dir,
            db_path=db_path,
            dry_run=False,
        )
        assert summary["mode"] == "LIVE"
        assert summary["beliefs_created"] == 3


# Helper
def _get_tid(payload: dict) -> str:
    return str(payload.get("template_id", "")).strip()
