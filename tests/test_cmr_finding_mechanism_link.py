"""
Tests for FindingMechanismLink and CMR specification integration.

Sprint 8 Task: Implement FindingMechanismLink data structure per CMR_SPECIFICATION_2026-03-02.md

Tests cover:
1. FindingMechanismLink instantiation and validation
2. MechanismStep construction with maturity/confidence levels
3. Serialization to/from dict
4. Edge type compatibility
5. Multi-framework convergence tracking
6. Integration with edge_types registry
"""

import pytest
from dataclasses import asdict
from datetime import datetime, timezone

from src.epistemic.edge_types import (
    FindingMechanismLink,
    MechanismStep,
    MechanismExplanationType,
    MechanismStepEvidence,
    MechanismStepMaturity,
    EdgeType,
    get_valid_source_types,
    get_valid_target_types,
    validate_edge_connection,
)


class TestMechanismStep:
    """Tests for MechanismStep dataclass."""

    def test_create_basic_mechanism_step(self):
        """Create a basic mechanism step with required fields."""
        step = MechanismStep(
            step_number=0,
            from_entity="visual_cortex_V1",
            activity="efficient_coding_of_1/f_spectrum",
            to_entity="prediction_error_signal",
            change_produced="reduced_prediction_error_magnitude",
            level="circuit",
            maturity="how-actually",
            evidence_type="direct_test",
        )
        assert step.step_number == 0
        assert step.from_entity == "visual_cortex_V1"
        assert step.confidence == 0.5  # Default
        assert step.bridging_quality == "MEDIUM"  # Default

    def test_mechanism_step_with_evidence_citation(self):
        """Create step with full evidence details."""
        step = MechanismStep(
            step_number=1,
            from_entity="anterior_cingulate",
            activity="compute_precision_weighting",
            to_entity="thalamic_reticular_nucleus",
            change_produced="reduced_precision_weighting_demand",
            level="circuit",
            maturity="how-plausibly",
            evidence_type="indirect_support",
            evidence_citation="Friston et al. (2012)",
            confidence=0.70,
            bridging_quality="MEDIUM",
        )
        assert step.evidence_citation == "Friston et al. (2012)"
        assert step.confidence == 0.70
        assert step.maturity == "how-plausibly"

    def test_mechanism_step_maturity_levels(self):
        """Test all maturity levels."""
        for maturity in ["how-actually", "how-plausibly", "how-possibly"]:
            step = MechanismStep(
                step_number=0,
                from_entity="A",
                activity="process",
                to_entity="B",
                change_produced="change",
                level="circuit",
                maturity=maturity,
                evidence_type="direct_test",
            )
            assert step.maturity == maturity

    def test_mechanism_step_to_dict(self):
        """Convert MechanismStep to dictionary."""
        step = MechanismStep(
            step_number=2,
            from_entity="locus_coeruleus",
            activity="adjust_neuromodulation",
            to_entity="cortical_arousal",
            change_produced="reduced_noradrenergic_arousal",
            level="cellular",
            maturity="how-actually",
            evidence_type="indirect_support",
            evidence_citation="Aston-Jones & Cohen (2005)",
            confidence=0.80,
        )
        step_dict = step.to_dict()
        assert isinstance(step_dict, dict)
        assert step_dict["step_number"] == 2
        assert step_dict["from_entity"] == "locus_coeruleus"
        assert step_dict["confidence"] == 0.80


class TestFindingMechanismLink:
    """Tests for FindingMechanismLink dataclass."""

    @pytest.fixture
    def sample_mechanism_steps(self):
        """Create a sample mechanism chain for testing."""
        return [
            MechanismStep(
                step_number=0,
                from_entity="visual_cortex",
                activity="process_1/f_spectrum",
                to_entity="prediction_error",
                change_produced="low_error",
                level="circuit",
                maturity="how-actually",
                evidence_type="direct_test",
                confidence=0.95,
            ),
            MechanismStep(
                step_number=1,
                from_entity="anterior_cingulate",
                activity="compute_precision",
                to_entity="thalamus",
                change_produced="reduced_precision_demand",
                level="circuit",
                maturity="how-plausibly",
                evidence_type="indirect_support",
                confidence=0.70,
            ),
            MechanismStep(
                step_number=2,
                from_entity="HPA_axis",
                activity="reduce_cortisol",
                to_entity="systemic_circulation",
                change_produced="low_cortisol",
                level="molecular",
                maturity="how-actually",
                evidence_type="logical_inference",
                confidence=0.85,
            ),
        ]

    def test_create_finding_mechanism_link(self, sample_mechanism_steps):
        """Create a complete FindingMechanismLink."""
        link = FindingMechanismLink(
            link_id="FML-F-ulrich-1984-T-predictive-processing",
            finding_id="F-ulrich-1984",
            finding_description="Nature exposure reduces hospital recovery time by 3.7 days",
            template_id="T-predictive-processing-visual-stats",
            template_name="predictive-processing-visual-statistics",
            framework_id="TIER1-predictive-processing",
            framework_name="predictive-processing",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.78,
            confidence_justification="Multi-step chain with strong spectral statistics evidence",
            finding_measure_type="Recovery time (days), analgesic use",
            mechanism_prediction="Reduced cortisol via HPA axis pathway",
            measure_alignment="adequate",
        )

        assert link.link_id == "FML-F-ulrich-1984-T-predictive-processing"
        assert link.finding_id == "F-ulrich-1984"
        assert link.overall_confidence == 0.78
        assert len(link.mechanism_steps) == 3
        assert link.explanation_type == "directly_explains"

    def test_finding_mechanism_link_defaults(self, sample_mechanism_steps):
        """Test default field values."""
        link = FindingMechanismLink(
            link_id="FML-test",
            finding_id="F-test",
            finding_description="Test finding",
            template_id="T-test",
            template_name="test-template",
            framework_id="TIER1-test",
            framework_name="test-framework",
            explanation_type="partially_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.50,
            confidence_justification="Test",
            finding_measure_type="test measure",
            mechanism_prediction="test prediction",
            measure_alignment="loose",
        )

        assert link.derived_predictions == []
        assert link.prediction_grammar_operations == []
        assert link.converges_with_frameworks == []
        assert link.convergence_independence == "medium"
        assert link.maturity_status == "proposal"

    def test_finding_mechanism_link_with_predictions(self, sample_mechanism_steps):
        """Create link with derived predictions."""
        link = FindingMechanismLink(
            link_id="FML-test-predictions",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-test",
            template_name="test",
            framework_id="TIER1-test",
            framework_name="test",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.75,
            confidence_justification="Test",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="adequate",
            derived_predictions=[
                "Artificial fractals should produce similar benefit",
                "High-anxiety patients should show larger benefit",
            ],
            prediction_grammar_operations=["SUBSTITUTE_CAUSE", "VARY_MODERATOR"],
        )

        assert len(link.derived_predictions) == 2
        assert len(link.prediction_grammar_operations) == 2
        assert "SUBSTITUTE_CAUSE" in link.prediction_grammar_operations

    def test_finding_mechanism_link_convergence(self, sample_mechanism_steps):
        """Test multi-framework convergence tracking."""
        link = FindingMechanismLink(
            link_id="FML-convergence-test",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-test",
            template_name="test",
            framework_id="TIER1-predictive-processing",
            framework_name="predictive-processing",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.82,
            confidence_justification="Multi-framework convergence",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="perfect",
            converges_with_frameworks=[
                "DMN/TPN-dynamics",
                "interoceptive-inference",
                "embodied-cognition",
            ],
            convergence_independence="high",
        )

        assert len(link.converges_with_frameworks) == 3
        assert link.convergence_independence == "high"
        assert link.overall_confidence == 0.82

    def test_finding_mechanism_link_scope_conditions(self, sample_mechanism_steps):
        """Test scope conditions specification."""
        scope = {
            "population": ["post-operative patients", "adult humans"],
            "context": ["hospital setting", "window available"],
            "conditions": ["acute post-operative stress"],
        }

        link = FindingMechanismLink(
            link_id="FML-scope-test",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-test",
            template_name="test",
            framework_id="TIER1-test",
            framework_name="test",
            explanation_type="conditional_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.70,
            confidence_justification="Test",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="adequate",
            scope_conditions=scope,
        )

        assert link.scope_conditions["population"] == ["post-operative patients", "adult humans"]
        assert "hospital setting" in link.scope_conditions["context"]

    def test_finding_mechanism_link_to_dict(self, sample_mechanism_steps):
        """Convert FindingMechanismLink to dictionary."""
        link = FindingMechanismLink(
            link_id="FML-dict-test",
            finding_id="F-test",
            finding_description="Test finding",
            template_id="T-test",
            template_name="test-template",
            framework_id="TIER1-test",
            framework_name="test-framework",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.75,
            confidence_justification="Test confidence",
            finding_measure_type="test-measure",
            mechanism_prediction="test-prediction",
            measure_alignment="adequate",
        )

        link_dict = link.to_dict()
        assert isinstance(link_dict, dict)
        assert link_dict["link_id"] == "FML-dict-test"
        assert link_dict["overall_confidence"] == 0.75
        assert isinstance(link_dict["mechanism_steps"], list)
        assert len(link_dict["mechanism_steps"]) == 3
        # Check that mechanism_steps are converted to dicts
        assert isinstance(link_dict["mechanism_steps"][0], dict)
        assert "step_number" in link_dict["mechanism_steps"][0]

    def test_finding_mechanism_link_hashable(self, sample_mechanism_steps):
        """Test that FindingMechanismLink is hashable."""
        link1 = FindingMechanismLink(
            link_id="FML-hash-test",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-test",
            template_name="test",
            framework_id="TIER1-test",
            framework_name="test",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.75,
            confidence_justification="Test",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="adequate",
        )

        link_set = {link1}
        assert link1 in link_set

    def test_finding_mechanism_link_equality(self, sample_mechanism_steps):
        """Test equality based on link_id."""
        link1 = FindingMechanismLink(
            link_id="FML-eq-test",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-test",
            template_name="test",
            framework_id="TIER1-test",
            framework_name="test",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.75,
            confidence_justification="Test",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="adequate",
        )

        link2 = FindingMechanismLink(
            link_id="FML-eq-test",  # Same ID
            finding_id="F-different",
            finding_description="Different",
            template_id="T-different",
            template_name="different",
            framework_id="TIER1-different",
            framework_name="different",
            explanation_type="partially_explains",
            mechanism_steps=[],
            overall_confidence=0.50,
            confidence_justification="Different",
            finding_measure_type="other",
            mechanism_prediction="other",
            measure_alignment="loose",
        )

        assert link1 == link2  # Same link_id means equal

    def test_finding_mechanism_link_alternatives(self, sample_mechanism_steps):
        """Test tracking of alternative explanations."""
        alternatives = [
            "embodied-cognition-postural-pathway",
            "spatial-navigation-cognitive-mapping",
            "placebo-expectancy",
        ]

        link = FindingMechanismLink(
            link_id="FML-alt-test",
            finding_id="F-test",
            finding_description="Test",
            template_id="T-best",
            template_name="best-explanation",
            framework_id="TIER1-test",
            framework_name="test",
            explanation_type="directly_explains",
            mechanism_steps=sample_mechanism_steps,
            overall_confidence=0.78,
            confidence_justification="Multi-framework convergence",
            finding_measure_type="measure",
            mechanism_prediction="prediction",
            measure_alignment="adequate",
            alternatives_considered=alternatives,
            why_best_explanation="Strongest mechanistic chain with highest convergence",
        )

        assert len(link.alternatives_considered) == 3
        assert "embodied-cognition-postural-pathway" in link.alternatives_considered
        assert link.why_best_explanation.startswith("Strongest")


class TestMechanismExplanationTypes:
    """Tests for MechanismExplanationType enum."""

    def test_explanation_types_defined(self):
        """Verify all explanation types from spec are defined."""
        expected = {
            "DIRECTLY_EXPLAINS",
            "PARTIALLY_EXPLAINS",
            "MODULATES",
            "MEDIATES",
            "CONTRADICTS",
            "CONDITIONAL_EXPLAINS",
        }
        actual = {e.name for e in MechanismExplanationType}
        assert expected == actual

    def test_explanation_type_values(self):
        """Check explanation type values."""
        assert MechanismExplanationType.DIRECTLY_EXPLAINS.value == "directly_explains"
        assert MechanismExplanationType.PARTIALLY_EXPLAINS.value == "partially_explains"
        assert MechanismExplanationType.CONTRADICTS.value == "contradicts"


class TestEdgeTypeIntegration:
    """Tests for CMR edge types in the EdgeType enum."""

    def test_finding_mechanism_edge_types_exist(self):
        """Verify new edge types exist in EdgeType enum."""
        assert hasattr(EdgeType, "FINDING_MECHANISM_EXPLAINS")
        assert hasattr(EdgeType, "FINDING_MECHANISM_CONTRADICTS")

    def test_finding_mechanism_explains_edge_type(self):
        """Test FINDING_MECHANISM_EXPLAINS edge type."""
        edge_type = EdgeType.FINDING_MECHANISM_EXPLAINS
        assert edge_type.value == "finding_mechanism_explains"

    def test_finding_mechanism_contradicts_edge_type(self):
        """Test FINDING_MECHANISM_CONTRADICTS edge type."""
        edge_type = EdgeType.FINDING_MECHANISM_CONTRADICTS
        assert edge_type.value == "finding_mechanism_contradicts"

    def test_finding_mechanism_edge_compatibility(self):
        """Test edge type compatibility for finding-mechanism edges."""
        # FINDING_MECHANISM_EXPLAINS
        is_valid, msg = validate_edge_connection(
            EdgeType.FINDING_MECHANISM_EXPLAINS,
            source_node_type="mechanistic_template",
            target_node_type="empirical_finding",
        )
        assert is_valid, f"Should be valid: {msg}"

        # FINDING_MECHANISM_CONTRADICTS
        is_valid, msg = validate_edge_connection(
            EdgeType.FINDING_MECHANISM_CONTRADICTS,
            source_node_type="template_chain",
            target_node_type="synthesis_conclusion",
        )
        assert is_valid, f"Should be valid: {msg}"

    def test_finding_mechanism_edge_invalid_source(self):
        """Test invalid source type for finding-mechanism edge."""
        is_valid, msg = validate_edge_connection(
            EdgeType.FINDING_MECHANISM_EXPLAINS,
            source_node_type="empirical_finding",  # Invalid source
            target_node_type="empirical_finding",
        )
        assert not is_valid, "Should reject invalid source type"

    def test_finding_mechanism_edge_invalid_target(self):
        """Test invalid target type for finding-mechanism edge."""
        is_valid, msg = validate_edge_connection(
            EdgeType.FINDING_MECHANISM_EXPLAINS,
            source_node_type="mechanistic_template",
            target_node_type="theoretical_proposition",  # Invalid target
        )
        assert not is_valid, "Should reject invalid target type"

    def test_valid_source_types_for_finding_mechanism_explains(self):
        """Test get_valid_source_types for FINDING_MECHANISM_EXPLAINS."""
        valid_sources = get_valid_source_types(EdgeType.FINDING_MECHANISM_EXPLAINS)
        assert "template_chain" in valid_sources
        assert "mechanistic_template" in valid_sources

    def test_valid_target_types_for_finding_mechanism_explains(self):
        """Test get_valid_target_types for FINDING_MECHANISM_EXPLAINS."""
        valid_targets = get_valid_target_types(EdgeType.FINDING_MECHANISM_EXPLAINS)
        assert "empirical_finding" in valid_targets
        assert "synthesis_conclusion" in valid_targets


class TestMeasureAlignment:
    """Tests for measure alignment scoring."""

    def test_measure_alignment_options(self):
        """Test valid measure alignment options."""
        valid_alignments = ["perfect", "adequate", "loose", "misaligned"]
        for alignment in valid_alignments:
            link = FindingMechanismLink(
                link_id=f"FML-align-{alignment}",
                finding_id="F-test",
                finding_description="Test",
                template_id="T-test",
                template_name="test",
                framework_id="TIER1-test",
                framework_name="test",
                explanation_type="directly_explains",
                mechanism_steps=[],
                overall_confidence=0.75,
                confidence_justification="Test",
                finding_measure_type="measure",
                mechanism_prediction="prediction",
                measure_alignment=alignment,
            )
            assert link.measure_alignment == alignment


class TestMaturityLevels:
    """Tests for mechanism step maturity levels."""

    def test_maturity_levels_defined(self):
        """Verify maturity levels are properly defined."""
        expected_maturities = ["how-actually", "how-plausibly", "how-possibly"]
        for maturity in expected_maturities:
            step = MechanismStep(
                step_number=0,
                from_entity="A",
                activity="process",
                to_entity="B",
                change_produced="change",
                level="circuit",
                maturity=maturity,
                evidence_type="direct_test",
            )
            assert step.maturity == maturity

    def test_confidence_penalty_structure(self):
        """Test confidence penalties for maturity levels."""
        # According to spec: how-actually has highest confidence,
        # how-plausibly reduced, how-possibly lowest
        steps_by_maturity = {
            "how-actually": MechanismStep(
                step_number=0,
                from_entity="A",
                activity="process",
                to_entity="B",
                change_produced="change",
                level="circuit",
                maturity="how-actually",
                evidence_type="direct_test",
                confidence=0.95,
            ),
            "how-plausibly": MechanismStep(
                step_number=1,
                from_entity="A",
                activity="process",
                to_entity="B",
                change_produced="change",
                level="circuit",
                maturity="how-plausibly",
                evidence_type="indirect_support",
                confidence=0.70,
            ),
            "how-possibly": MechanismStep(
                step_number=2,
                from_entity="A",
                activity="process",
                to_entity="B",
                change_produced="change",
                level="circuit",
                maturity="how-possibly",
                evidence_type="analogy",
                confidence=0.45,
            ),
        }

        # Verify confidence ordering
        actually_conf = steps_by_maturity["how-actually"].confidence
        plausibly_conf = steps_by_maturity["how-plausibly"].confidence
        possibly_conf = steps_by_maturity["how-possibly"].confidence

        assert actually_conf > plausibly_conf > possibly_conf


class TestMechanismStepEvidence:
    """Tests for mechanism step evidence types."""

    def test_evidence_types_defined(self):
        """Verify all evidence types from spec are defined."""
        expected = {
            "DIRECT_TEST",
            "INDIRECT_SUPPORT",
            "LOGICAL_INFERENCE",
            "ANALOGY",
        }
        actual = {e.name for e in MechanismStepEvidence}
        assert expected == actual

    def test_evidence_type_values(self):
        """Check evidence type values."""
        assert MechanismStepEvidence.DIRECT_TEST.value == "direct_test"
        assert MechanismStepEvidence.INDIRECT_SUPPORT.value == "indirect_support"
        assert MechanismStepEvidence.LOGICAL_INFERENCE.value == "logical_inference"
        assert MechanismStepEvidence.ANALOGY.value == "analogy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
