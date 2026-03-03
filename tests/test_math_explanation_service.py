"""
Tests for Math Explanation Service.

Created: 2026-03-02
Author: Claude Code
"""

import pytest
from src.services.math_explanation_service import (
    MathExplanationService,
    MathExplanation,
    UserDepth,
    Provenance,
    ConstantExplanation,
)


class TestMathExplanationServiceInitialization:
    """Test service initialization."""

    def test_service_initializes(self):
        """Service should initialize without error."""
        service = MathExplanationService()
        assert service is not None

    def test_service_ready_to_explain(self):
        """Service should be ready to explain formulas."""
        service = MathExplanationService()
        # Should not raise error
        explanation = service.explain('credence_projection')
        assert explanation is not None


class TestExplainCredenceProjection:
    """Test credence projection formula explanation."""

    def test_explain_credence_projection(self):
        """Should explain credence projection formula."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert explanation is not None
        assert explanation.formula_name == 'Credence Projection'

    def test_credence_projection_has_four_layers(self):
        """Should have all four explanation layers."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.plain_english) > 0
        assert len(explanation.intuition) > 0
        assert len(explanation.formal_notation) > 0
        assert len(explanation.worked_examples) > 0

    def test_credence_projection_has_variables_defined(self):
        """Should define all variables."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert 'p_target' in explanation.variable_definitions
        assert 'p_lab' in explanation.variable_definitions
        assert 'd(τ)' in explanation.variable_definitions or 'd' in explanation.variable_definitions

    def test_credence_projection_has_three_worked_examples(self):
        """Should have three worked examples."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.worked_examples) == 3

    def test_credence_projection_examples_span_diversity(self):
        """Worked examples should span best/worst/typical cases."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        scenarios = [ex.get('scenario', '').lower() for ex in explanation.worked_examples]
        # Should have distinct scenarios
        assert len(set(scenarios)) >= 2

    def test_credence_projection_has_justified_constants(self):
        """Should justify all constants."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.constants) > 0
        for constant in explanation.constants:
            assert constant.provenance is not None
            assert len(constant.justification) > 0

    def test_credence_projection_has_assumptions(self):
        """Should state assumptions explicitly."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.assumptions) > 0

    def test_credence_projection_has_failure_modes(self):
        """Should identify failure modes."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.failure_modes) > 0

    def test_credence_projection_has_figure_references(self):
        """Should reference relevant figures."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.related_figure_ids) > 0
        # Should reference M-25, M-27, M-30
        assert 'M-25' in explanation.related_figure_ids or 'M-27' in explanation.related_figure_ids


class TestExplainCoherence:
    """Test coherence formula explanation."""

    def test_explain_coherence(self):
        """Should explain coherence formula."""
        service = MathExplanationService()
        explanation = service.explain('coherence_c_star')
        assert explanation is not None
        assert 'Coherence' in explanation.formula_name

    def test_coherence_has_plain_english(self):
        """Should have plain English explanation."""
        service = MathExplanationService()
        explanation = service.explain('coherence')
        assert len(explanation.plain_english) > 0
        assert 'coherent' in explanation.plain_english.lower()

    def test_coherence_has_intuition(self):
        """Should have intuitive explanation."""
        service = MathExplanationService()
        explanation = service.explain('c_star')
        assert len(explanation.intuition) > 0
        # Should mention conflicts and agreements
        intuition_lower = explanation.intuition.lower()
        assert 'conflict' in intuition_lower or 'agreement' in intuition_lower

    def test_coherence_formal_notation(self):
        """Should show formal notation."""
        service = MathExplanationService()
        explanation = service.explain('coherence_c_star')
        assert 'C*' in explanation.formal_notation or 'C' in explanation.formal_notation

    def test_coherence_worked_examples(self):
        """Should have worked examples."""
        service = MathExplanationService()
        explanation = service.explain('coherence')
        assert len(explanation.worked_examples) >= 1

    def test_coherence_provenance(self):
        """Should state provenance."""
        service = MathExplanationService()
        explanation = service.explain('coherence')
        assert explanation.provenance is not None


class TestExplainVOI:
    """Test value of information explanation."""

    def test_explain_voi(self):
        """Should explain VOI formula."""
        service = MathExplanationService()
        explanation = service.explain('voi')
        assert explanation is not None
        assert 'Value' in explanation.formula_name or 'VOI' in explanation.formula_name

    def test_voi_plain_english(self):
        """Should explain VOI in plain English."""
        service = MathExplanationService()
        explanation = service.explain('value_of_information')
        assert len(explanation.plain_english) > 0

    def test_voi_distinguishes_structural_epistemic(self):
        """Should distinguish structural vs epistemic value."""
        service = MathExplanationService()
        explanation = service.explain('voi')
        intuition_lower = explanation.intuition.lower()
        assert 'structural' in intuition_lower
        assert 'epistemic' in intuition_lower


class TestExplainUnknownFormula:
    """Test behavior for unknown formulas."""

    def test_explain_unknown_formula(self):
        """Should handle unknown formula gracefully."""
        service = MathExplanationService()
        explanation = service.explain('unknown_formula_xyz')
        assert explanation is not None
        assert isinstance(explanation, MathExplanation)

    def test_unknown_formula_is_labeled(self):
        """Unknown formula should be noted."""
        service = MathExplanationService()
        explanation = service.explain('bogus')
        assert 'not yet' in explanation.plain_english.lower() or 'unknown' in explanation.plain_english.lower()


class TestExplainConstant:
    """Test constant explanation."""

    def test_explain_lambda(self):
        """Should explain lambda constant."""
        service = MathExplanationService()
        explanation = service.explain_constant('lambda')
        assert explanation is not None
        assert 'λ' in explanation.symbol or 'lambda' in explanation.name.lower()

    def test_lambda_has_value_and_units(self):
        """Lambda explanation should have value and units."""
        service = MathExplanationService()
        explanation = service.explain_constant('lambda')
        assert explanation.value > 0
        assert len(explanation.units) > 0

    def test_explain_omega_floor(self):
        """Should explain omega floor constant."""
        service = MathExplanationService()
        explanation = service.explain_constant('omega_floor')
        assert explanation is not None
        assert explanation.value == 0.05

    def test_explain_omega_ceiling(self):
        """Should explain omega ceiling constant."""
        service = MathExplanationService()
        explanation = service.explain_constant('omega_ceiling')
        assert explanation is not None
        assert explanation.value == 0.98

    def test_explain_delta_default(self):
        """Should explain delta default constant."""
        service = MathExplanationService()
        explanation = service.explain_constant('delta_default')
        assert explanation is not None
        assert explanation.value == 0.90

    def test_explain_alpha_voi(self):
        """Should explain alpha VOI constant."""
        service = MathExplanationService()
        explanation = service.explain_constant('alpha_voi')
        assert explanation is not None
        assert explanation.value == 0.6

    def test_constant_has_provenance(self):
        """Constants should have provenance."""
        service = MathExplanationService()
        explanation = service.explain_constant('lambda')
        assert explanation.provenance is not None
        assert explanation.provenance in [
            Provenance.EMPIRICAL, Provenance.THEORETICAL,
            Provenance.CALIBRATED, Provenance.STIPULATED
        ]

    def test_constant_has_justification(self):
        """Constants should be justified."""
        service = MathExplanationService()
        explanation = service.explain_constant('lambda')
        assert len(explanation.justification) > 0

    def test_constant_has_sensitivity(self):
        """Constants should have sensitivity analysis."""
        service = MathExplanationService()
        explanation = service.explain_constant('lambda')
        assert len(explanation.sensitivity) > 0


class TestGetIntuition:
    """Test intuition retrieval."""

    def test_get_intuition_credence_projection(self):
        """Should return intuition for credence projection."""
        service = MathExplanationService()
        intuition = service.get_intuition('credence_projection')
        assert len(intuition) > 0
        assert 'logit' in intuition.lower() or 'transform' in intuition.lower()

    def test_get_intuition_coherence(self):
        """Should return intuition for coherence."""
        service = MathExplanationService()
        intuition = service.get_intuition('coherence')
        assert len(intuition) > 0

    def test_get_intuition_voi(self):
        """Should return intuition for VOI."""
        service = MathExplanationService()
        intuition = service.get_intuition('voi')
        assert len(intuition) > 0


class TestGetWorkedExample:
    """Test worked example retrieval."""

    def test_get_worked_example_credence(self):
        """Should return worked example for credence projection."""
        service = MathExplanationService()
        example = service.get_worked_example('credence_projection')
        assert len(example) > 0
        assert 'EXAMPLE' in example or 'example' in example

    def test_worked_example_has_computation(self):
        """Worked example should show computation steps."""
        service = MathExplanationService()
        example = service.get_worked_example('credence_projection')
        assert 'Computation' in example or 'computation' in example.lower()

    def test_worked_example_has_result(self):
        """Worked example should show result."""
        service = MathExplanationService()
        example = service.get_worked_example('credence_projection')
        assert 'Result' in example or 'result' in example.lower()

    def test_worked_example_has_interpretation(self):
        """Worked example should interpret result."""
        service = MathExplanationService()
        example = service.get_worked_example('credence_projection')
        assert 'Interpretation' in example or 'interpretation' in example.lower()

    def test_get_example_for_specific_context(self):
        """Should return example for specific context if available."""
        service = MathExplanationService()
        # Request high-quality study example
        example = service.get_worked_example('credence_projection', context='high')
        assert len(example) > 0


class TestMathExplanationStructure:
    """Test the four-layer explanation structure."""

    def test_layer1_plain_english(self):
        """Layer 1 should have plain English statement."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        # Should be understandable without math notation
        assert len(explanation.plain_english) > 50
        # Should not have too much notation
        notation_chars = sum(1 for c in explanation.plain_english if c in 'αβγδλωμσ')
        assert notation_chars < len(explanation.plain_english) * 0.1

    def test_layer2_intuition(self):
        """Layer 2 should explain why the formula has this form."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.intuition) > 50
        # Should explain design choices
        assert any(word in explanation.intuition.lower() for word in ['why', 'because', 'motivation'])

    def test_layer3_formal_notation(self):
        """Layer 3 should show formal statement with definitions."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.formal_notation) > 0
        assert len(explanation.variable_definitions) > 0
        # Each variable should be defined
        for var in explanation.variable_definitions:
            assert len(explanation.variable_definitions[var]) > 0

    def test_layer4_examples(self):
        """Layer 4 should have worked examples."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.worked_examples) > 0
        # Each example should be complete
        for example in explanation.worked_examples:
            assert 'scenario' in example or 'context' in example
            assert 'result' in example or 'computation' in example


class TestNormCompliance:
    """Test compliance with MATH_EXPLANATION_NORMS."""

    def test_norm1_four_layers(self):
        """Norm 1: Every formula should have four layers."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.plain_english) > 0  # Layer 1
        assert len(explanation.intuition) > 0  # Layer 2
        assert len(explanation.formal_notation) > 0  # Layer 3
        assert len(explanation.worked_examples) > 0  # Layer 4

    def test_norm2_provenance_tracking(self):
        """Norm 2: Every formula should have provenance."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert explanation.provenance in [
            Provenance.ESTABLISHED, Provenance.ADAPTED, Provenance.NOVEL
        ]
        assert len(explanation.provenance_detail) > 0

    def test_norm3_justified_constants(self):
        """Norm 3: Every constant should be justified."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        for constant in explanation.constants:
            assert constant.provenance in [
                Provenance.EMPIRICAL, Provenance.THEORETICAL,
                Provenance.CALIBRATED, Provenance.STIPULATED
            ]
            assert len(constant.justification) > 0

    def test_norm4_assumptions_and_scope(self):
        """Norm 4: Should state assumptions and domain of validity."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.assumptions) > 0
        assert len(explanation.domain_of_validity) > 0
        assert len(explanation.failure_modes) > 0

    def test_norm5_common_sense_labels(self):
        """Norm 5: Should use common-sense labels."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        assert len(explanation.common_sense_terms) > 0
        # Each symbol should have a plain-English name
        for symbol, plain_name in explanation.common_sense_terms.items():
            assert len(plain_name) > 0

    def test_norm6_figures(self):
        """Norm 6: Multi-variable formulas should reference figures."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        # Credence projection has >2 variables, should have figures
        num_vars = len(explanation.variable_definitions)
        if num_vars > 2:
            assert len(explanation.related_figure_ids) > 0

    def test_norm7_diversity_of_examples(self):
        """Norm 7: Examples should span diversity of cases."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection')
        # Should have at least best/worst/typical
        assert len(explanation.example_contexts) >= 2


class TestUserDepthHandling:
    """Test that user depth is handled (even if not fully implemented)."""

    def test_explain_with_minimal_depth(self):
        """Should accept minimal depth parameter."""
        service = MathExplanationService()
        # Should not raise error
        explanation = service.explain('credence_projection', depth=UserDepth.MINIMAL)
        assert explanation is not None

    def test_explain_with_standard_depth(self):
        """Should accept standard depth parameter."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection', depth=UserDepth.STANDARD)
        assert explanation is not None

    def test_explain_with_comprehensive_depth(self):
        """Should accept comprehensive depth parameter."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection', depth=UserDepth.COMPREHENSIVE)
        assert explanation is not None


class TestUserTypeRouting:
    """Test routing to user type explanations."""

    def test_explain_for_architect(self):
        """Should explain for architect."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection', user_type='architect')
        assert explanation is not None

    def test_explain_for_researcher(self):
        """Should explain for researcher."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection', user_type='researcher')
        assert explanation is not None

    def test_explain_for_student(self):
        """Should explain for student."""
        service = MathExplanationService()
        explanation = service.explain('credence_projection', user_type='student')
        assert explanation is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
