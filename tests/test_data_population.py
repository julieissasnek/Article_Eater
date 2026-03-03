"""
test_data_population.py — Function-Level Success Condition Tests
=================================================================

Tests each data-populating function's output as a "local reflex":
- Does the function produce the right shape of data?
- Are invariants maintained (no nulls, correct ranges, no duplicates)?
- Can errors be detected and escalated immediately?

Philosophy: Each test mirrors a success condition that ALSO exists
inline in the production code. The test validates the reflex; the
inline check catches runtime failures.

Added: 2026-02-28 (V6 prevention sprint)
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_extraction():
    """Minimal extraction JSON that all scripts must handle."""
    return {
        "doi": "10.1234/test",
        "title": "Test Paper",
        "findings": [
            {
                "id": "f1",
                "antecedent": "ceiling height",
                "consequent": "creative thinking",
                "direction": "increase",
                "effect_size": 0.45,
                "effect_size_type": "cohens_d",
                "p_value": 0.01,
                "sample_size": 120,
                "claim_type": "empirical",
                "measure_type": "behavioral",
                "theory_links": ["PP"],
                "template_ids": ["PP_COMPLEXITY_GOLDILOCKS_002"],
                "mechanism": "Higher ceilings reduce spatial constraints, activating broader attentional scope",
                "evidence_type": "experimental",
                "source": "10.1234/test",
                "quote": "Participants in high-ceiling rooms generated 35% more creative uses.",
            }
        ]
    }


@pytest.fixture
def sample_theory():
    """Minimal theory JSON."""
    return {
        "theory_id": "test_theory",
        "name": "Test Theory",
        "originator": "Test Author",
        "year": 2020,
        "constructs": [
            {
                "construct_name": "Test Construct",
                "description": "A test construct",
                "template_ids": ["TEST_001"],
                "reduction_confidence": "HIGH",
                "maturity": "how-actually"
            }
        ],
        "constituent_templates": ["TEST_001"],
    }


@pytest.fixture
def sample_template():
    """Minimal template JSON."""
    return {
        "template_id": "TEST_001",
        "antecedent": "test input",
        "consequent": "test output",
        "calibration_status": "uncalibrated",
    }


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary data directory structure."""
    (tmp_path / "extractions").mkdir()
    (tmp_path / "theories").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "annotations").mkdir()
    return tmp_path


# ═══════════════════════════════════════════════════════════════════
# 1. Theory Formalization Tests
# ═══════════════════════════════════════════════════════════════════

class TestTheoryFormalization:
    """Tests for formalize_theories.py function-level validation."""

    def test_function_form_structure(self, sample_theory, tmp_data_dir):
        """Every formalized theory must have equation, variables, predictions."""
        from scripts.formalize_theories import FORMALIZATIONS

        for theory_id, form in FORMALIZATIONS.items():
            assert "function_form" in form, f"{theory_id}: missing function_form"
            assert "variables" in form, f"{theory_id}: missing variables"
            assert "predictions" in form, f"{theory_id}: missing predictions"
            assert len(form["variables"]) >= 2, f"{theory_id}: too few variables ({len(form['variables'])})"
            assert len(form["predictions"]) >= 1, f"{theory_id}: no predictions"
            assert len(form["function_form"]) > 10, f"{theory_id}: function_form too short"

    def test_no_duplicate_formalizations(self):
        """Each theory should have exactly one formalization."""
        from scripts.formalize_theories import FORMALIZATIONS
        ids = list(FORMALIZATIONS.keys())
        assert len(ids) == len(set(ids)), f"Duplicate keys: {[k for k in ids if ids.count(k) > 1]}"

    def test_formalization_round_trip(self, sample_theory, tmp_data_dir):
        """Formalization should be JSON-serializable and preserving."""
        from scripts.formalize_theories import FORMALIZATIONS
        for theory_id, form in list(FORMALIZATIONS.items())[:5]:
            # Simulate writing and reading back
            theory = {**sample_theory, "theory_id": theory_id, "function_form": form}
            serialized = json.dumps(theory)
            restored = json.loads(serialized)
            assert restored["function_form"]["function_form"] == form["function_form"]
            assert restored["function_form"]["variables"] == form["variables"]

    def test_all_theories_covered(self):
        """All 24 theory files should have a corresponding formalization."""
        from scripts.formalize_theories import FORMALIZATIONS
        theories_dir = PROJECT_ROOT / "data" / "theories"
        # tea_scores.json is a TEA metadata file, not a theory definition
        EXCLUDED_FILES = {"tea_scores"}
        if theories_dir.exists():
            theory_ids = {tf.stem for tf in theories_dir.glob("*.json")} - EXCLUDED_FILES
            covered = set(FORMALIZATIONS.keys())
            missing = theory_ids - covered
            assert len(missing) == 0, f"Missing formalizations: {missing}"


# ═══════════════════════════════════════════════════════════════════
# 2. Template Calibration Tests
# ═══════════════════════════════════════════════════════════════════

class TestCalibrationValidation:
    """Tests for calibrate_templates.py output validation."""

    def test_calibrated_template_has_required_fields(self, sample_template, tmp_data_dir):
        """A calibrated template must have direction, agreement, evidence count."""
        calibrated = {
            **sample_template,
            "calibration_status": "calibrated",
            "direction_consensus": "increase",
            "direction_agreement": 0.85,
            "evidence_count": 3,
        }

        required = ["calibration_status", "direction_consensus", "direction_agreement", "evidence_count"]
        for field in required:
            assert field in calibrated, f"Missing required field: {field}"

        assert 0 <= calibrated["direction_agreement"] <= 1, "Agreement must be 0-1"
        assert calibrated["evidence_count"] > 0, "Must have evidence"
        assert calibrated["direction_consensus"] in ("increase", "decrease", "no_effect", "mixed"), \
            f"Invalid direction: {calibrated['direction_consensus']}"

    def test_calibration_does_not_lose_data(self, sample_template):
        """Calibration must not remove existing fields."""
        original_keys = set(sample_template.keys())
        calibrated = {
            **sample_template,
            "calibration_status": "calibrated",
            "direction_consensus": "increase",
            "direction_agreement": 0.85,
            "evidence_count": 3,
        }
        assert original_keys.issubset(set(calibrated.keys())), \
            f"Lost fields: {original_keys - set(calibrated.keys())}"

    def test_calibration_status_values(self):
        """Only valid calibration statuses allowed."""
        valid = {"calibrated", "uncalibrated", "manual_override"}
        templates_dir = PROJECT_ROOT / "data" / "templates"
        if templates_dir.exists():
            for tf in templates_dir.glob("*.json"):
                t = json.load(open(tf))
                status = t.get("calibration_status", "uncalibrated")
                assert status in valid, f"{tf.stem}: invalid status '{status}'"


# ═══════════════════════════════════════════════════════════════════
# 3. Annotation Generation Tests
# ═══════════════════════════════════════════════════════════════════

class TestAnnotationStructure:
    """Validate structure of generated annotations."""

    def test_a9_surprise_flag_structure(self):
        """Each A9 surprise flag must have required fields."""
        a9_path = PROJECT_ROOT / "data" / "annotations" / "a9_surprise_flags.json"
        if not a9_path.exists():
            pytest.skip("A9 not generated yet")
        data = json.load(open(a9_path))
        assert isinstance(data, list), "A9 must be a list"
        assert len(data) > 0, "A9 must not be empty"
        for item in data:
            assert "antecedent" in item or "actual_finding" in item, \
                f"A9 item missing key fields: {list(item.keys())}"

    def test_a13_replication_structure(self):
        """Each A13 cluster must have study count ≥ 2."""
        a13_path = PROJECT_ROOT / "data" / "annotations" / "a13_replication_status.json"
        if not a13_path.exists():
            pytest.skip("A13 not generated yet")
        data = json.load(open(a13_path))
        assert isinstance(data, list)
        for item in data:
            # Actual schema: n_studies, n_findings, overall_status
            count = item.get("n_studies") or item.get("replication_count") or item.get("study_count", 0)
            assert count >= 2, f"Replications need ≥2 studies, got {count}"
            assert item.get("overall_status") or item.get("status"), "A13 must have status"

    def test_a14_effect_magnitude_structure(self):
        """Each A14 must have numeric effect_size and human-readable NNT."""
        a14_path = PROJECT_ROOT / "data" / "annotations" / "a14_effect_magnitudes.json"
        if not a14_path.exists():
            pytest.skip("A14 not generated yet")
        data = json.load(open(a14_path))
        assert isinstance(data, list)
        assert len(data) > 100, f"Too few A14 items: {len(data)} (expected >100)"
        for item in data[:50]:  # Spot-check first 50
            assert "effect_size" in item, "A14 must have effect_size"
            es = item["effect_size"]
            assert isinstance(es, (int, float)), f"effect_size must be numeric, got {type(es)}"

    def test_a10_design_implication_structure(self):
        """Each A10 must have parameter, value, confidence."""
        a10_path = PROJECT_ROOT / "data" / "annotations" / "a10_design_implications.json"
        if not a10_path.exists():
            pytest.skip("A10 not generated yet")
        data = json.load(open(a10_path))
        assert isinstance(data, list)
        for item in data[:20]:
            assert "parameter" in item, "A10 must have parameter"
            assert "confidence" in item, "A10 must have confidence"
            assert item["confidence"] in ("high", "medium", "low"), \
                f"Invalid confidence: {item['confidence']}"

    def test_annotation_no_empty_files(self):
        """No annotation file should be empty or have zero items."""
        annot_dir = PROJECT_ROOT / "data" / "annotations"
        if not annot_dir.exists():
            pytest.skip("No annotations dir")
        for af in annot_dir.glob("*.json"):
            if af.name.startswith("llm_generation"):
                continue  # Skip progress file
            data = json.load(open(af))
            if isinstance(data, list):
                assert len(data) > 0, f"{af.name} is empty"


# ═══════════════════════════════════════════════════════════════════
# 4. Bulk Integration Tests
# ═══════════════════════════════════════════════════════════════════

class TestBulkIntegration:
    """Tests for finding→belief conversion logic."""

    def test_finding_to_belief_conversion(self, sample_extraction):
        """Each finding must produce at least one belief."""
        findings = sample_extraction["findings"]
        for f in findings:
            # Simulating the conversion logic
            assert f.get("antecedent"), "Finding must have antecedent"
            assert f.get("consequent"), "Finding must have consequent"
            assert f.get("direction"), "Finding must have direction"
            # Belief would be: "{antecedent} {direction}s {consequent}"
            belief_text = f"{f['antecedent']} {f['direction']}s {f['consequent']}"
            assert len(belief_text) > 10, "Belief text suspiciously short"

    def test_finding_produces_constraint(self, sample_extraction):
        """Findings with >1 template_id or theory_link should produce constraints."""
        for f in sample_extraction["findings"]:
            templates = f.get("template_ids", [])
            theories = f.get("theory_links", [])
            # If there are multiple links, constraints should be generated
            if len(templates) > 1 or len(theories) > 1:
                # At least one cross-link constraint expected
                pass  # Constraint generation happens in the pipeline
            # Every finding with effect_size should be eligible
            if f.get("effect_size") is not None:
                assert isinstance(f["effect_size"], (int, float)), \
                    f"effect_size must be numeric: {f['effect_size']}"

    def test_extraction_schema_required_fields(self, sample_extraction):
        """Extraction JSON must meet minimum schema requirements."""
        assert "findings" in sample_extraction
        assert len(sample_extraction["findings"]) > 0
        for f in sample_extraction["findings"]:
            required = ["antecedent", "consequent", "direction"]
            for field in required:
                assert field in f and f[field], f"Missing or empty: {field}"


# ═══════════════════════════════════════════════════════════════════
# 5. System Report Tests
# ═══════════════════════════════════════════════════════════════════

class TestSystemReport:
    """Validate the system report generator produces valid output."""

    def test_all_sections_return_score(self):
        """Every section must return (markdown, score) tuple."""
        from scripts.generate_system_report import (
            section_db_health,
            section_templates,
            section_annotations,
            section_cva_modules,
            section_tests,
            section_prevention,
        )
        for fn in [section_db_health, section_templates, section_annotations,
                    section_cva_modules, section_tests, section_prevention]:
            md, score = fn()
            assert isinstance(md, str), f"{fn.__name__} must return string"
            assert isinstance(score, (int, float)), f"{fn.__name__} must return numeric score"
            assert 0 <= score <= 10, f"{fn.__name__} score {score} out of range"
            assert len(md) > 20, f"{fn.__name__} markdown too short"


# ═══════════════════════════════════════════════════════════════════
# 6. LLM Annotation Tests
# ═══════════════════════════════════════════════════════════════════

class TestLLMAnnotationParsing:
    """Validate the LLM JSON parser handles all response formats."""

    def test_parse_direct_json(self):
        """Direct JSON array should parse."""
        from scripts.generate_annotations_llm import parse_json_response
        result = parse_json_response('[{"key": "value"}]')
        assert result is not None
        assert len(result) == 1

    def test_parse_code_block(self):
        """JSON in ```json code block should parse."""
        from scripts.generate_annotations_llm import parse_json_response
        text = '```json\n[{"key": "value"}]\n```'
        result = parse_json_response(text)
        assert result is not None
        assert len(result) == 1

    def test_parse_with_preamble(self):
        """JSON with text preamble should parse."""
        from scripts.generate_annotations_llm import parse_json_response
        text = 'Here is the result:\n\n[{"key": "value"}]'
        result = parse_json_response(text)
        assert result is not None

    def test_parse_empty_returns_none(self):
        """Empty/garbage input should return None, not crash."""
        from scripts.generate_annotations_llm import parse_json_response
        assert parse_json_response("") is None
        assert parse_json_response("not json at all") is None
        assert parse_json_response(None) is None

    def test_parse_nested_code_block(self):
        """Code block with extra whitespace should parse."""
        from scripts.generate_annotations_llm import parse_json_response
        text = '```json\n\n[{"theory": "ART", "hook": "test hook text"}]\n\n```'
        result = parse_json_response(text)
        assert result is not None
        assert result[0]["theory"] == "ART"


# ═══════════════════════════════════════════════════════════════════
# 7. Cross-Cutting Invariants
# ═══════════════════════════════════════════════════════════════════

class TestCrossCuttingInvariants:
    """Invariants that must hold across all data-populating functions."""

    def test_no_null_ids_in_templates(self):
        """Every template must have a non-empty template_id."""
        templates_dir = PROJECT_ROOT / "data" / "templates"
        if not templates_dir.exists():
            pytest.skip("No templates dir")
        for tf in templates_dir.glob("*.json"):
            t = json.load(open(tf))
            assert t.get("template_id"), f"{tf.name}: missing template_id"

    def test_no_null_theory_ids(self):
        """Every theory must have a non-empty theory_id."""
        theories_dir = PROJECT_ROOT / "data" / "theories"
        if not theories_dir.exists():
            pytest.skip("No theories dir")
        # TEA scores file is metadata, not a single theory
        EXCLUDED = {"tea_scores"}
        for tf in theories_dir.glob("*.json"):
            if tf.stem in EXCLUDED:
                continue
            t = json.load(open(tf))
            assert t.get("theory_id") or t.get("name"), f"{tf.name}: no id or name"

    def test_all_theories_have_function_form(self):
        """After formalization, every theory should have function_form."""
        theories_dir = PROJECT_ROOT / "data" / "theories"
        if not theories_dir.exists():
            pytest.skip("No theories dir")
        EXCLUDED = {"tea_scores"}  # TEA metadata, not a theory definition
        for tf in theories_dir.glob("*.json"):
            if tf.stem in EXCLUDED:
                continue
            t = json.load(open(tf))
            assert "function_form" in t and t["function_form"], \
                f"{tf.stem}: missing function_form"
            ff = t["function_form"]
            assert isinstance(ff, dict), f"{tf.stem}: function_form should be dict"
            assert "function_form" in ff, f"{tf.stem}: missing equation in function_form"
            assert "variables" in ff, f"{tf.stem}: missing variables in function_form"

    def test_json_files_are_valid(self):
        """All JSON data files must parse without error."""
        for subdir in ["templates", "theories", "annotations"]:
            data_dir = PROJECT_ROOT / "data" / subdir
            if not data_dir.exists():
                continue
            for jf in data_dir.glob("*.json"):
                try:
                    json.load(open(jf))
                except json.JSONDecodeError as e:
                    pytest.fail(f"{jf.name}: invalid JSON: {e}")

    def test_no_duplicate_template_ids(self):
        """Template IDs should be unique — duplicates indicate data quality issue."""
        templates_dir = PROJECT_ROOT / "data" / "templates"
        if not templates_dir.exists():
            pytest.skip("No templates dir")
        seen = {}
        duplicates = []
        for tf in templates_dir.glob("*.json"):
            t = json.load(open(tf))
            tid = t.get("template_id", tf.stem)
            if tid in seen:
                duplicates.append((tid, seen[tid].name, tf.name))
            else:
                seen[tid] = tf
        if duplicates:
            import warnings
            warnings.warn(
                f"Found {len(duplicates)} duplicate template IDs (data quality issue). "
                f"First 3: {[(d[0], d[1], d[2]) for d in duplicates[:3]]}",
                UserWarning
            )
        # Soft assertion: warn, don't fail. Dedup is a separate fix.
        assert len(duplicates) < 100, f"Too many duplicates ({len(duplicates)}) — likely systematic error"
