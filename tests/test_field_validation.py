"""Tests for field validation protocol generator (Task 13.10)."""

import json
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from src.cmr.field_validation import (
    StudyDesignType,
    MeasurementTier,
    DVMeasure,
    Control,
    FieldStudyProtocol,
    generate_protocol,
    get_available_protocols,
    generate_all_protocols,
    format_protocol_report,
    export_protocols_json,
)


# ============================================================================
# Test Enums
# ============================================================================

class TestStudyDesignType:
    """Tests for StudyDesignType enum."""

    def test_all_design_types_exist(self):
        """Verify all expected design types are defined."""
        expected = [
            "within_subjects",
            "between_subjects",
            "mixed_design",
            "quasi_experimental",
            "longitudinal",
            "cross_sectional",
        ]
        actual = [d.value for d in StudyDesignType]
        assert set(expected) == set(actual)

    def test_enum_string_serialization(self):
        """Design types serialize to strings."""
        assert StudyDesignType.WITHIN_SUBJECTS.value == "within_subjects"
        assert str(StudyDesignType.QUASI_EXPERIMENTAL) == "StudyDesignType.QUASI_EXPERIMENTAL"


class TestMeasurementTier:
    """Tests for MeasurementTier enum."""

    def test_tiers_are_ordered(self):
        """Verify tier progression from A (easy) to D (expert)."""
        tiers = ["A", "B", "C", "D"]
        actual = [t.value for t in MeasurementTier]
        assert actual == tiers

    def test_tier_descriptions_match_values(self):
        """Tier values match accessibility levels."""
        assert MeasurementTier.A.value == "A"  # Easy
        assert MeasurementTier.D.value == "D"  # Expert


# ============================================================================
# Test Dataclasses
# ============================================================================

class TestDVMeasure:
    """Tests for DVMeasure dataclass."""

    def test_dv_measure_creation(self):
        """Can create a DV measure with all fields."""
        dv = DVMeasure(
            name="Cortisol",
            instrument="ELISA",
            tier=MeasurementTier.D,
            frequency="pre_post",
            estimated_cost_usd=1500,
            notes="Requires saliva collection",
        )
        assert dv.name == "Cortisol"
        assert dv.tier == MeasurementTier.D
        assert dv.estimated_cost_usd == 1500

    def test_dv_measure_default_notes(self):
        """Notes field has empty string default."""
        dv = DVMeasure(
            name="PSQI",
            instrument="Questionnaire",
            tier=MeasurementTier.A,
            frequency="single",
            estimated_cost_usd=0,
        )
        assert dv.notes == ""


class TestControl:
    """Tests for Control dataclass."""

    def test_control_creation(self):
        """Can create a control specification."""
        ctrl = Control(name="Temperature", method="match", critical=True)
        assert ctrl.name == "Temperature"
        assert ctrl.method == "match"
        assert ctrl.critical is True

    def test_control_default_critical(self):
        """Critical defaults to True."""
        ctrl = Control(name="Time of day", method="counterbalance")
        assert ctrl.critical is True


class TestFieldStudyProtocol:
    """Tests for FieldStudyProtocol dataclass."""

    @pytest.fixture
    def sample_protocol(self):
        """Create a minimal sample protocol for testing."""
        return FieldStudyProtocol(
            template_id="TEST1",
            template_name="Test Template",
            prediction="Higher X leads to better Y",
            study_design=StudyDesignType.WITHIN_SUBJECTS,
            sample_n=40,
            sample_justification="Power analysis for d=0.5",
            iv_manipulation="Vary X across conditions",
            dv_measures=[
                DVMeasure(
                    name="Outcome Y",
                    instrument="Y-Scale",
                    tier=MeasurementTier.A,
                    frequency="pre_post",
                    estimated_cost_usd=0,
                )
            ],
            controls=[Control(name="Age", method="match")],
            duration_weeks=2,
            success_criteria=["Y increases with X"],
            estimated_total_cost_usd=1000,
            cost_breakdown={"participant_compensation": 1000},
            ethical_considerations=["Minimal risk"],
            practical_notes=["Recruit from local population"],
        )

    def test_protocol_to_dict(self, sample_protocol):
        """Protocol can be converted to dictionary."""
        d = sample_protocol.to_dict()
        assert d["template_id"] == "TEST1"
        assert d["study_design"] == "within_subjects"
        assert len(d["dv_measures"]) == 1
        assert d["dv_measures"][0]["tier"] == "A"

    def test_protocol_generated_at_timestamp(self, sample_protocol):
        """Protocol has generated_at timestamp."""
        d = sample_protocol.to_dict()
        assert "generated_at" in d
        # Should be valid ISO format
        datetime.fromisoformat(d["generated_at"])


# ============================================================================
# Test Protocol Generators
# ============================================================================

class TestGenerateProtocol:
    """Tests for generate_protocol function."""

    def test_generate_l2_protocol(self):
        """L2 protocol generator works."""
        protocol = generate_protocol("L2")
        assert protocol is not None
        assert protocol.template_id == "L2"
        assert "circadian" in protocol.template_name.lower()

    def test_generate_vf3_protocol(self):
        """VF3 protocol generator works."""
        protocol = generate_protocol("VF3")
        assert protocol is not None
        assert protocol.template_id == "VF3"
        assert "ceiling" in protocol.prediction.lower()

    def test_generate_view1_protocol(self):
        """VIEW1 protocol generator works."""
        protocol = generate_protocol("VIEW1")
        assert protocol is not None
        assert protocol.template_id == "VIEW1"
        assert "nature" in protocol.prediction.lower() or "view" in protocol.prediction.lower()

    def test_generate_soc2_protocol(self):
        """SOC2 protocol generator works."""
        protocol = generate_protocol("SOC2")
        assert protocol is not None
        assert protocol.template_id == "SOC2"
        assert "privacy" in protocol.prediction.lower()

    def test_generate_mat1_protocol(self):
        """MAT1 protocol generator works."""
        protocol = generate_protocol("MAT1")
        assert protocol is not None
        assert protocol.template_id == "MAT1"
        assert "material" in protocol.prediction.lower() or "touch" in protocol.prediction.lower()

    def test_case_insensitive_lookup(self):
        """Protocol lookup is case-insensitive."""
        assert generate_protocol("l2") is not None
        assert generate_protocol("L2") is not None
        assert generate_protocol("vf3") is not None
        assert generate_protocol("VF3") is not None

    def test_unknown_template_returns_none(self):
        """Unknown template ID returns None."""
        assert generate_protocol("UNKNOWN99") is None
        assert generate_protocol("") is None


class TestGetAvailableProtocols:
    """Tests for get_available_protocols function."""

    def test_returns_list(self):
        """Returns a list of template IDs."""
        protocols = get_available_protocols()
        assert isinstance(protocols, list)
        assert len(protocols) >= 5  # L2, VF3, VIEW1, SOC2, MAT1

    def test_list_is_sorted(self):
        """List is alphabetically sorted."""
        protocols = get_available_protocols()
        assert protocols == sorted(protocols)

    def test_expected_templates_present(self):
        """Expected templates are available."""
        protocols = get_available_protocols()
        assert "L2" in protocols
        assert "VF3" in protocols
        assert "VIEW1" in protocols
        assert "SOC2" in protocols
        assert "MAT1" in protocols


class TestGenerateAllProtocols:
    """Tests for generate_all_protocols function."""

    def test_returns_list_of_protocols(self):
        """Returns list of FieldStudyProtocol objects."""
        protocols = generate_all_protocols()
        assert isinstance(protocols, list)
        assert all(isinstance(p, FieldStudyProtocol) for p in protocols)

    def test_generates_correct_count(self):
        """Generates one protocol per registered generator."""
        protocols = generate_all_protocols()
        available = get_available_protocols()
        assert len(protocols) == len(available)


# ============================================================================
# Test Protocol Quality
# ============================================================================

class TestProtocolQuality:
    """Tests for protocol content quality."""

    @pytest.fixture
    def all_protocols(self):
        """Generate all protocols for quality checks."""
        return generate_all_protocols()

    def test_all_have_predictions(self, all_protocols):
        """All protocols have non-empty predictions."""
        for p in all_protocols:
            assert p.prediction, f"{p.template_id} missing prediction"
            assert len(p.prediction) > 50, f"{p.template_id} prediction too short"

    def test_all_have_dv_measures(self, all_protocols):
        """All protocols have at least 3 DV measures."""
        for p in all_protocols:
            assert len(p.dv_measures) >= 3, f"{p.template_id} needs more DV measures"

    def test_all_have_controls(self, all_protocols):
        """All protocols have at least 3 control variables."""
        for p in all_protocols:
            assert len(p.controls) >= 3, f"{p.template_id} needs more controls"

    def test_all_have_success_criteria(self, all_protocols):
        """All protocols have at least 2 success criteria."""
        for p in all_protocols:
            assert len(p.success_criteria) >= 2, f"{p.template_id} needs more success criteria"

    def test_sample_sizes_reasonable(self, all_protocols):
        """All protocols have reasonable sample sizes."""
        for p in all_protocols:
            assert 30 <= p.sample_n <= 150, f"{p.template_id} sample size {p.sample_n} unusual"

    def test_costs_are_positive(self, all_protocols):
        """All protocols have positive cost estimates."""
        for p in all_protocols:
            assert p.estimated_total_cost_usd > 0, f"{p.template_id} missing cost estimate"

    def test_cost_breakdown_sums_correctly(self, all_protocols):
        """Cost breakdown approximately sums to total."""
        for p in all_protocols:
            breakdown_sum = sum(p.cost_breakdown.values())
            # Allow 10% tolerance for rounding
            assert abs(breakdown_sum - p.estimated_total_cost_usd) / p.estimated_total_cost_usd < 0.1, \
                f"{p.template_id} cost breakdown doesn't sum to total"

    def test_ethical_considerations_present(self, all_protocols):
        """All protocols have ethical considerations."""
        for p in all_protocols:
            assert len(p.ethical_considerations) >= 2, f"{p.template_id} needs more ethical considerations"


# ============================================================================
# Test Report Formatting
# ============================================================================

class TestFormatProtocolReport:
    """Tests for format_protocol_report function."""

    def test_report_contains_template_id(self):
        """Report contains template ID."""
        protocol = generate_protocol("L2")
        report = format_protocol_report(protocol)
        assert "L2" in report

    def test_report_contains_all_sections(self):
        """Report contains all expected sections."""
        protocol = generate_protocol("VF3")
        report = format_protocol_report(protocol)
        sections = [
            "PREDICTION",
            "STUDY DESIGN",
            "DEPENDENT VARIABLES",
            "CONTROLS",
            "SUCCESS CRITERIA",
            "COST ESTIMATE",
            "ETHICAL CONSIDERATIONS",
            "PRACTICAL NOTES",
        ]
        for section in sections:
            assert section in report, f"Missing section: {section}"

    def test_report_has_readable_format(self):
        """Report has readable formatting."""
        protocol = generate_protocol("VIEW1")
        report = format_protocol_report(protocol)
        # Has separators
        assert "=" * 50 in report or "=" * 70 in report
        assert "-" * 50 in report
        # Has line breaks
        assert "\n\n" in report


# ============================================================================
# Test JSON Export
# ============================================================================

class TestExportProtocolsJson:
    """Tests for export_protocols_json function."""

    def test_export_without_path_returns_dict(self):
        """Export without path returns dictionary."""
        result = export_protocols_json()
        assert isinstance(result, dict)
        assert "protocols" in result
        assert "n_protocols" in result
        assert "generated_at" in result

    def test_export_to_file(self):
        """Export can write to file."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            export_protocols_json(path)
            assert path.exists()

            with open(path, "r") as f:
                data = json.load(f)

            assert "protocols" in data
            assert len(data["protocols"]) >= 5
        finally:
            path.unlink()

    def test_exported_json_valid(self):
        """Exported JSON is valid and complete."""
        data = export_protocols_json()

        # Check structure
        assert data["n_protocols"] == len(data["protocols"])

        # Check each protocol has required fields
        required_fields = [
            "template_id",
            "prediction",
            "study_design",
            "sample_n",
            "dv_measures",
            "controls",
            "success_criteria",
            "estimated_total_cost_usd",
        ]
        for protocol in data["protocols"]:
            for field in required_fields:
                assert field in protocol, f"Missing field {field} in protocol"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_generate_format_export_workflow(self):
        """Complete workflow: generate → format → export."""
        # Generate single protocol
        protocol = generate_protocol("L2")
        assert protocol is not None

        # Format as report
        report = format_protocol_report(protocol)
        assert len(report) > 500  # Substantial report

        # Export all to JSON
        data = export_protocols_json()
        l2_data = next(p for p in data["protocols"] if p["template_id"] == "L2")
        assert l2_data["prediction"] == protocol.prediction

    def test_all_templates_round_trip(self):
        """All templates can generate, format, and serialize."""
        for template_id in get_available_protocols():
            # Generate
            protocol = generate_protocol(template_id)
            assert protocol is not None, f"Failed to generate {template_id}"

            # Format
            report = format_protocol_report(protocol)
            assert template_id in report, f"Template ID not in report for {template_id}"

            # Serialize
            d = protocol.to_dict()
            json_str = json.dumps(d)
            assert len(json_str) > 100, f"JSON too short for {template_id}"


# ============================================================================
# Specific Template Tests
# ============================================================================

class TestL2Protocol:
    """Specific tests for L2 (Circadian) protocol."""

    @pytest.fixture
    def protocol(self):
        return generate_protocol("L2")

    def test_includes_melatonin_measure(self, protocol):
        """L2 protocol includes DLMO measurement."""
        dv_names = [dv.name.lower() for dv in protocol.dv_measures]
        assert any("dlmo" in n or "melatonin" in n for n in dv_names)

    def test_includes_light_exposure_measure(self, protocol):
        """L2 protocol includes light exposure measurement."""
        dv_names = [dv.name.lower() for dv in protocol.dv_measures]
        assert any("light" in n for n in dv_names)

    def test_controls_for_chronotype(self, protocol):
        """L2 protocol controls for chronotype."""
        control_names = [c.name.lower() for c in protocol.controls]
        assert any("chronotype" in n for n in control_names)


class TestVF3Protocol:
    """Specific tests for VF3 (Ceiling Height) protocol."""

    @pytest.fixture
    def protocol(self):
        return generate_protocol("VF3")

    def test_includes_creative_task(self, protocol):
        """VF3 protocol includes creative/abstract task."""
        dv_names = [dv.name.lower() for dv in protocol.dv_measures]
        assert any("abstract" in n or "creative" in n or "rat" in dv.instrument.lower()
                   for dv, n in zip(protocol.dv_measures, dv_names))

    def test_uses_within_subjects(self, protocol):
        """VF3 protocol uses within-subjects design."""
        assert protocol.study_design == StudyDesignType.WITHIN_SUBJECTS


class TestVIEW1Protocol:
    """Specific tests for VIEW1 (Nature View) protocol."""

    @pytest.fixture
    def protocol(self):
        return generate_protocol("VIEW1")

    def test_includes_stress_measure(self, protocol):
        """VIEW1 protocol includes stress measurement."""
        dv_names = [dv.name.lower() for dv in protocol.dv_measures]
        assert any("stress" in n or "cortisol" in n for n in dv_names)

    def test_includes_attention_measure(self, protocol):
        """VIEW1 protocol includes attention restoration measure."""
        dv_names = [dv.name.lower() for dv in protocol.dv_measures]
        dv_instruments = [dv.instrument.lower() for dv in protocol.dv_measures]
        assert any("attention" in n or "digit span" in i
                   for n, i in zip(dv_names, dv_instruments))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
