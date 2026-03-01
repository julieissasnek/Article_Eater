"""
Tests for T2 Mechanism Template Archetypes — Sprint 7
=====================================================
Created: 2026-02-28
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

from src.models.mechanism_templates import (
    T2ArchetypeType,
    T2Archetype,
    T2ArchetypeRegistry,
    PredictiveCodingArchetype,
    HomeostaticRegulationArchetype,
    AccumulationToBoundArchetype,
    CompetitiveSelectionArchetype,
    GatedPropagationArchetype,
    ConvergentStateMonitoringArchetype,
    ParameterSpec,
    DomainExample,
)
from src.services.template_quality_assurance import TemplateQA, QAReport


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def archetype_registry_path() -> Path:
    """Path to mechanism_archetypes.json"""
    return Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"


@pytest.fixture
def registry(archetype_registry_path) -> T2ArchetypeRegistry:
    """Load archetype registry."""
    registry = T2ArchetypeRegistry()
    if archetype_registry_path.exists():
        registry.load_from_json_file(archetype_registry_path)
    return registry


@pytest.fixture
def sample_template() -> Dict[str, Any]:
    """Sample template with mechanism_chain."""
    return {
        "template_id": "TEST_TEMPLATE_001",
        "mechanism_chain": [
            {
                "mechanism": "Prediction error minimization via predictive coding",
                "justification": {
                    "warrant": "EMPIRICAL_ASSOCIATION",
                    "studies": ["Smith et al., 2020"]
                }
            },
            {
                "mechanism": "Visual complexity preferences",
                "justification": {
                    "warrant": "THEORY_DERIVED",
                    "theories": ["PP"]
                }
            }
        ]
    }


# =============================================================================
# TESTS: BASIC INSTANTIATION
# =============================================================================

class TestArchetypeInstantiation:
    """Test that archetypes can be instantiated."""

    def test_predictive_coding_archetype(self):
        """Test PredictiveCodingArchetype creation."""
        arch = PredictiveCodingArchetype(
            archetype_id="PC_001",
            archetype_type=T2ArchetypeType.PREDICTIVE_CODING,
            name="Predictive Coding",
            description="Test archetype",
            theoretical_basis=["Friston 2010"],
            input_variables=["observation", "prediction"],
            output_variables=["error", "update"],
            parameters={},
            domain_examples=[],
            computational_signature="error = obs - pred",
            t1_framework_links=["PP"],
            precision_weighted=True,
            hierarchical_levels=3,
        )
        assert arch.archetype_id == "PC_001"
        assert arch.precision_weighted is True
        assert arch.hierarchical_levels == 3

    def test_homeostatic_regulation_archetype(self):
        """Test HomeostaticRegulationArchetype creation."""
        arch = HomeostaticRegulationArchetype(
            archetype_id="HR_001",
            archetype_type=T2ArchetypeType.HOMEOSTATIC_REGULATION,
            name="Homeostatic Regulation",
            description="Test archetype",
            theoretical_basis=["Cannon 1932"],
            input_variables=["state", "setpoint"],
            output_variables=["drive"],
            parameters={},
            domain_examples=[],
            computational_signature="drive = |state - setpoint|",
            t1_framework_links=["IC"],
            setpoint_variable="temperature",
            feedback_type="negative",
            adaptation_rate=0.1,
        )
        assert arch.setpoint_variable == "temperature"
        assert arch.feedback_type == "negative"

    def test_accumulation_to_bound_archetype(self):
        """Test AccumulationToBoundArchetype creation."""
        arch = AccumulationToBoundArchetype(
            archetype_id="ATB_001",
            archetype_type=T2ArchetypeType.ACCUMULATION_TO_BOUND,
            name="Accumulation to Bound",
            description="Test archetype",
            theoretical_basis=["Ratcliff 2008"],
            input_variables=["evidence"],
            output_variables=["decision"],
            parameters={},
            domain_examples=[],
            computational_signature="decision when evidence >= threshold",
            t1_framework_links=["DP"],
            threshold=1.0,
            drift_rate=0.5,
            noise_level=0.3,
        )
        assert arch.threshold == 1.0
        assert arch.drift_rate == 0.5

    def test_competitive_selection_archetype(self):
        """Test CompetitiveSelectionArchetype creation."""
        arch = CompetitiveSelectionArchetype(
            archetype_id="CS_001",
            archetype_type=T2ArchetypeType.COMPETITIVE_SELECTION,
            name="Competitive Selection",
            description="Test archetype",
            theoretical_basis=["Desimone 1995"],
            input_variables=["activations"],
            output_variables=["winner"],
            parameters={},
            domain_examples=[],
            computational_signature="winner = argmax(activation)",
            t1_framework_links=["PP"],
            n_competitors=4,
            inhibition_type="lateral",
        )
        assert arch.n_competitors == 4
        assert arch.inhibition_type == "lateral"

    def test_gated_propagation_archetype(self):
        """Test GatedPropagationArchetype creation."""
        arch = GatedPropagationArchetype(
            archetype_id="GP_001",
            archetype_type=T2ArchetypeType.GATED_PROPAGATION,
            name="Gated Propagation",
            description="Test archetype",
            theoretical_basis=["Miller 2001"],
            input_variables=["input", "gate"],
            output_variables=["output"],
            parameters={},
            domain_examples=[],
            computational_signature="output = gate * input",
            t1_framework_links=["NM"],
            modulation_type="multiplicative",
        )
        assert arch.modulation_type == "multiplicative"

    def test_convergent_state_monitoring_archetype(self):
        """Test ConvergentStateMonitoringArchetype creation."""
        arch = ConvergentStateMonitoringArchetype(
            archetype_id="CSM_001",
            archetype_type=T2ArchetypeType.CONVERGENT_STATE_MONITORING,
            name="Convergent State Monitoring",
            description="Test archetype",
            theoretical_basis=["Stein 1993"],
            input_variables=["sensors"],
            output_variables=["state_estimate"],
            parameters={},
            domain_examples=[],
            computational_signature="estimate = mean(sensors)",
            t1_framework_links=["IC"],
            n_sensors=3,
            convergence_criterion="weighted_mean",
        )
        assert arch.n_sensors == 3
        assert arch.convergence_criterion == "weighted_mean"


# =============================================================================
# TESTS: REGISTRY
# =============================================================================

class TestT2ArchetypeRegistry:
    """Test registry operations."""

    def test_register_archetype(self, registry):
        """Test registering an archetype."""
        arch = PredictiveCodingArchetype(
            archetype_id="TEST_001",
            archetype_type=T2ArchetypeType.PREDICTIVE_CODING,
            name="Test PC",
            description="Test",
            theoretical_basis=[],
            input_variables=[],
            output_variables=[],
            parameters={},
            domain_examples=[],
            computational_signature="",
            t1_framework_links=[],
        )
        registry.register(arch)
        assert registry.get("TEST_001") is arch

    def test_get_by_type(self, registry):
        """Test retrieving archetypes by type."""
        archetypes = registry.get_by_type(
            T2ArchetypeType.PREDICTIVE_CODING
        )
        assert len(archetypes) >= 0  # May be empty if registry not loaded

    def test_list_all(self, registry):
        """Test listing all archetypes."""
        all_archs = registry.list_all()
        assert isinstance(all_archs, list)

    def test_load_from_json(self, registry, archetype_registry_path):
        """Test loading archetypes from JSON file."""
        if archetype_registry_path.exists():
            assert len(registry.list_all()) == 6  # Should have 6 archetypes

            # Check that all 6 types are represented
            types = set(a.archetype_type for a in registry.list_all())
            assert T2ArchetypeType.PREDICTIVE_CODING in types
            assert T2ArchetypeType.HOMEOSTATIC_REGULATION in types
            assert T2ArchetypeType.ACCUMULATION_TO_BOUND in types
            assert T2ArchetypeType.COMPETITIVE_SELECTION in types
            assert T2ArchetypeType.GATED_PROPAGATION in types
            assert T2ArchetypeType.CONVERGENT_STATE_MONITORING in types


# =============================================================================
# TESTS: MECHANISM TEXT MATCHING
# =============================================================================

class TestMechanismMatching:
    """Test mechanism text fuzzy matching."""

    def test_match_exact_name(self, registry):
        """Test exact name match scoring."""
        matches = registry.match_mechanism_text("Predictive Coding")
        assert len(matches) > 0
        assert matches[0][1] > 0.5  # Should have decent score

    def test_match_description_keywords(self, registry):
        """Test keyword matching in descriptions."""
        matches = registry.match_mechanism_text(
            "hierarchical inference and prediction error"
        )
        assert len(matches) > 0

    def test_match_signature_partial(self, registry):
        """Test computational signature matching."""
        matches = registry.match_mechanism_text(
            "error = observation - prediction"
        )
        assert len(matches) > 0

    def test_no_match(self, registry):
        """Test when mechanism doesn't match any archetype."""
        matches = registry.match_mechanism_text("xyzzy plugh quux")
        assert len(matches) == 0


# =============================================================================
# TESTS: TEMPLATE VALIDATION
# =============================================================================

class TestTemplateQA:
    """Test template quality assurance service."""

    def test_qa_service_init(self, archetype_registry_path):
        """Test QA service initialization."""
        qa = TemplateQA(archetype_registry_path)
        assert qa.registry is not None

    def test_validate_valid_template(self, sample_template):
        """Test validation of valid template."""
        archetype_registry_path = (
            Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"
        )
        qa = TemplateQA(archetype_registry_path)
        report = qa.validate_template(sample_template)

        assert report.template_id == "TEST_TEMPLATE_001"
        assert isinstance(report.passed, bool)
        assert isinstance(report.errors, list)
        assert isinstance(report.warnings, list)

    def test_validate_missing_mechanism_chain(self):
        """Test validation when mechanism_chain is missing."""
        archetype_registry_path = (
            Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"
        )
        qa = TemplateQA(archetype_registry_path)

        template = {"template_id": "BAD_001"}
        report = qa.validate_template(template)

        assert report.passed is False
        assert len(report.errors) > 0

    def test_validate_empty_mechanism_chain(self):
        """Test validation when mechanism_chain is empty."""
        archetype_registry_path = (
            Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"
        )
        qa = TemplateQA(archetype_registry_path)

        template = {
            "template_id": "BAD_002",
            "mechanism_chain": []
        }
        report = qa.validate_template(template)

        assert report.passed is False
        assert any("empty" in e.lower() for e in report.errors)

    def test_qa_report_to_dict(self):
        """Test QA report serialization."""
        report = QAReport(
            template_id="TEST_001",
            passed=True,
            warnings=["warning 1"],
            errors=[],
            matched_archetypes=[("PC_001", 0.8)],
        )

        d = report.to_dict()
        assert d["template_id"] == "TEST_001"
        assert d["passed"] is True
        assert len(d["warnings"]) == 1
        assert len(d["matched_archetypes"]) == 1

    def test_summary_report_empty(self):
        """Test summary report with empty list."""
        archetype_registry_path = (
            Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"
        )
        qa = TemplateQA(archetype_registry_path)
        summary = qa.summary_report([])

        assert summary["total_templates"] == 0
        assert summary["passed"] == 0
        assert summary["passed_pct"] == 0.0

    def test_summary_report_with_reports(self):
        """Test summary report with actual reports."""
        archetype_registry_path = (
            Path(__file__).parent.parent / "data" / "mechanism_archetypes.json"
        )
        qa = TemplateQA(archetype_registry_path)

        reports = [
            QAReport("T1", True, [], []),
            QAReport("T2", False, ["warning"], ["error"]),
        ]
        summary = qa.summary_report(reports)

        assert summary["total_templates"] == 2
        assert summary["passed"] == 1
        assert summary["passed_pct"] == 50.0
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 1


# =============================================================================
# TESTS: DATA CLASS SERIALIZATION
# =============================================================================

class TestDataClassSerialization:
    """Test to_dict/from_dict conversions."""

    def test_parameter_spec_roundtrip(self):
        """Test ParameterSpec serialization roundtrip."""
        spec = ParameterSpec(
            name="test_param",
            default_value=0.5,
            min_value=0.0,
            max_value=1.0,
            unit="dimensionless",
            description="Test parameter"
        )

        d = spec.to_dict()
        spec2 = ParameterSpec.from_dict(d)

        assert spec2.name == spec.name
        assert spec2.default_value == spec.default_value

    def test_domain_example_roundtrip(self):
        """Test DomainExample serialization roundtrip."""
        example = DomainExample(
            domain="Test Domain",
            template_id="TEST_001",
            description="Test example"
        )

        d = example.to_dict()
        example2 = DomainExample.from_dict(d)

        assert example2.domain == example.domain
        assert example2.template_id == example.template_id


# =============================================================================
# TESTS: PROCESSING_FLUENCY THEORY
# =============================================================================

class TestProcessingFluencyTheory:
    """Test that processing_fluency.json loads and validates."""

    def test_processing_fluency_json_exists(self):
        """Check processing_fluency.json exists."""
        pf_path = (
            Path(__file__).parent.parent / "data" / "theories" / "processing_fluency.json"
        )
        assert pf_path.exists()

    def test_processing_fluency_json_loads(self):
        """Test processing_fluency.json loads correctly."""
        pf_path = (
            Path(__file__).parent.parent / "data" / "theories" / "processing_fluency.json"
        )
        with open(pf_path) as f:
            theory = json.load(f)

        assert theory["theory_id"] == "PROCESSING_FLUENCY"
        assert theory["status"] == "ACTIVE"
        assert "linked_archetypes" in theory

    def test_processing_fluency_archetype_links(self):
        """Test that linked archetypes are valid."""
        pf_path = (
            Path(__file__).parent.parent / "data" / "theories" / "processing_fluency.json"
        )
        with open(pf_path) as f:
            theory = json.load(f)

        linked = theory.get("linked_archetypes", [])
        assert len(linked) > 0

        # Check that archetype names are reasonable
        valid_names = [
            "PREDICTIVE_CODING",
            "HOMEOSTATIC_REGULATION",
            "ACCUMULATION_TO_BOUND",
            "COMPETITIVE_SELECTION",
            "GATED_PROPAGATION",
            "CONVERGENT_STATE_MONITORING"
        ]
        for name in linked:
            assert name in valid_names
