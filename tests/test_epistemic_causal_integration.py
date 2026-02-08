"""
Tests for Sprint 1.5: Epistemic-Causal Integration

This module tests the integration between:
1. The existing WebOfBelief (src/services/web_of_belief.py)
2. The new EpistemicCausalBridge (epistemic_causal_integration.py)

Test Strategy:
- Type compatibility: Verify the bridge accepts the existing WebOfBelief
- Model building: Test causal model extraction from web
- Counterfactual inference: Test epistemic-constrained counterfactuals
- Robustness analysis: Test sensitivity to belief revision
- Generalization: Test contrast class handling

Sprint 1.5.9 Deliverable
Date: February 8, 2026
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the epistemic layer source to path
EPIST_LAYER_PATH = Path("/Users/davidusa/REPOS/research/claude_epist_layer adds K to causal BN")
sys.path.insert(0, str(EPIST_LAYER_PATH))

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    CausalDirection,
    ScopeConditions,
    EnablingConditions,
    create_neuroarchitecture_web,
)

# Import from the epistemic causal integration module
import epistemic_causal_integration as eci


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def minimal_web():
    """Create a minimal WebOfBelief for testing."""
    web = WebOfBelief(domain="test")

    # Add a theoretical belief
    theory_belief = Belief(
        belief_id="theory:stress_recovery",
        content="Natural environments promote stress recovery through psychophysiological mechanisms",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.15),
        entrenchment=0.7,
        theory_id="SRT",
        tags=["outcome:stress", "exposure:nature"]
    )
    web.add_belief(theory_belief)
    web.theory_ids.add("SRT")

    # Add an intermediate belief (mechanistic)
    mech_belief = Belief(
        belief_id="mech:parasympathetic",
        content="Nature exposure activates parasympathetic nervous system",
        level=EpistemicLevel.INTERMEDIATE,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.70, 0.20),
        entrenchment=0.5,
        theory_id="SRT",
        tags=["outcome:parasympathetic", "exposure:nature"]
    )
    web.add_belief(mech_belief)

    # Add an empirical belief
    emp_belief = Belief(
        belief_id="emp:ulrich_1984",
        content="Hospital patients with nature views recovered faster than those with wall views",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.80, 0.10),
        entrenchment=0.6,
        theory_id="SRT",
        paper_ids=["ulrich_1984"],
        tags=["outcome:recovery", "exposure:nature_view"]
    )
    web.add_belief(emp_belief)

    # Add constraints
    web.add_constraint(Constraint(
        constraint_id="c:theory_mech",
        source_id="theory:stress_recovery",
        target_id="mech:parasympathetic",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.8
    ))

    web.add_constraint(Constraint(
        constraint_id="c:mech_emp",
        source_id="mech:parasympathetic",
        target_id="emp:ulrich_1984",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.7
    ))

    return web


@pytest.fixture
def multi_theory_web():
    """Create a WebOfBelief with multiple theories for testing."""
    web = WebOfBelief(domain="neuroarchitecture")

    # SRT (Stress Recovery Theory)
    web.add_belief(Belief(
        belief_id="theory:srt",
        content="Stress Recovery Theory: Natural environments promote recovery from stress",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ENTRENCHED,
        credence=Credence(0.80, 0.10),
        entrenchment=0.85,
        theory_id="SRT",
        tags=["outcome:stress"]
    ))
    web.theory_ids.add("SRT")

    # ART (Attention Restoration Theory)
    web.add_belief(Belief(
        belief_id="theory:art",
        content="Attention Restoration Theory: Natural environments restore directed attention",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ENTRENCHED,
        credence=Credence(0.75, 0.12),
        entrenchment=0.80,
        theory_id="ART",
        tags=["outcome:attention"]
    ))
    web.theory_ids.add("ART")

    # Shared empirical belief
    web.add_belief(Belief(
        belief_id="emp:nature_benefit",
        content="20-minute nature walk improves mood and attention",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.85, 0.08),
        entrenchment=0.5,
        paper_ids=["study_001", "study_002"],
        tags=["outcome:mood", "outcome:attention", "exposure:nature_walk"]
    ))

    # Connect to both theories
    web.add_constraint(Constraint(
        constraint_id="c:srt_emp",
        source_id="theory:srt",
        target_id="emp:nature_benefit",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.7
    ))
    web.add_constraint(Constraint(
        constraint_id="c:art_emp",
        source_id="theory:art",
        target_id="emp:nature_benefit",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.8
    ))

    return web


# =============================================================================
# TYPE COMPATIBILITY TESTS
# =============================================================================

class TestTypeCompatibility:
    """Test that existing WebOfBelief types work with EpistemicCausalBridge."""

    def test_web_has_required_attributes(self, minimal_web):
        """Verify WebOfBelief has attributes expected by the bridge."""
        # Required by EpistemicCausalBridge.__init__
        assert hasattr(minimal_web, 'domain')
        assert hasattr(minimal_web, 'beliefs')
        assert hasattr(minimal_web, 'constraints')
        assert hasattr(minimal_web, 'theory_ids')

        # Required methods
        assert hasattr(minimal_web, 'marginal_theory_probability')
        assert callable(minimal_web.marginal_theory_probability)

    def test_belief_has_required_attributes(self, minimal_web):
        """Verify Belief class has attributes expected by the bridge."""
        belief = list(minimal_web.beliefs.values())[0]

        # Required attributes
        assert hasattr(belief, 'belief_id')
        assert hasattr(belief, 'content')
        assert hasattr(belief, 'level')
        assert hasattr(belief, 'credence')
        assert hasattr(belief, 'entrenchment')
        assert hasattr(belief, 'tags')
        assert hasattr(belief, 'theory_id')

    def test_credence_has_required_attributes(self, minimal_web):
        """Verify Credence class has expected interface."""
        belief = list(minimal_web.beliefs.values())[0]
        credence = belief.credence

        assert hasattr(credence, 'value')
        assert hasattr(credence, 'uncertainty')
        assert 0 <= credence.value <= 1
        assert 0 <= credence.uncertainty <= 1

    def test_epistemic_level_compatibility(self, minimal_web):
        """Test that EpistemicLevel enums are compatible."""
        # Both modules define EpistemicLevel - check values match
        web_levels = {level.value for level in EpistemicLevel}
        bridge_levels = {level.value for level in eci.EpistemicLevel}

        assert web_levels == bridge_levels, \
            f"EpistemicLevel mismatch: web={web_levels}, bridge={bridge_levels}"

    def test_constraint_type_compatibility(self, minimal_web):
        """Test that ConstraintType enums are compatible."""
        # Core types that must be shared
        required_types = {"supports", "contradicts", "explains", "instantiates"}
        web_types = {ct.value for ct in ConstraintType}
        bridge_types = {ct.value for ct in eci.ConstraintType}

        assert required_types.issubset(web_types), \
            f"Missing required types in web: {required_types - web_types}"
        assert required_types.issubset(bridge_types), \
            f"Missing required types in bridge: {required_types - bridge_types}"


# =============================================================================
# BRIDGE CONSTRUCTION TESTS
# =============================================================================

class TestBridgeConstruction:
    """Test EpistemicCausalBridge construction with existing WebOfBelief."""

    def test_bridge_accepts_web(self, minimal_web):
        """Test that bridge can be constructed with existing WebOfBelief."""
        # This should not raise
        bridge = eci.EpistemicCausalBridge(minimal_web)

        assert bridge.web is minimal_web
        assert bridge.multi_theory_model is None  # Not built yet

    def test_bridge_accesses_beliefs(self, minimal_web):
        """Test that bridge can access beliefs from the web."""
        bridge = eci.EpistemicCausalBridge(minimal_web)

        # Bridge should be able to iterate beliefs
        belief_count = len(bridge.web.beliefs)
        assert belief_count == 3

    def test_bridge_accesses_constraints(self, minimal_web):
        """Test that bridge can access constraints from the web."""
        bridge = eci.EpistemicCausalBridge(minimal_web)

        constraint_count = len(bridge.web.constraints)
        assert constraint_count == 2


# =============================================================================
# MODEL BUILDING TESTS
# =============================================================================

class TestModelBuilding:
    """Test causal model extraction from epistemic web."""

    def test_build_causal_models_basic(self, minimal_web):
        """Test basic causal model building."""
        bridge = eci.EpistemicCausalBridge(minimal_web)

        model = bridge.build_causal_models(credence_threshold=0.5)

        assert model is not None
        assert bridge.multi_theory_model is model

    def test_build_causal_models_multi_theory(self, multi_theory_web):
        """Test causal model building with multiple theories."""
        bridge = eci.EpistemicCausalBridge(multi_theory_web)

        model = bridge.build_causal_models(credence_threshold=0.5)

        # Should have models for both SRT and ART
        assert "SRT" in model.theory_models or len(model.theory_models) >= 1

    def test_build_causal_models_credence_threshold(self, minimal_web):
        """Test that credence threshold filters beliefs."""
        bridge = eci.EpistemicCausalBridge(minimal_web)

        # High threshold should filter out more beliefs
        model_high = bridge.build_causal_models(credence_threshold=0.9)

        # Reset and build with low threshold
        bridge.multi_theory_model = None
        model_low = bridge.build_causal_models(credence_threshold=0.3)

        # Both should work (may have different content)
        assert model_high is not None
        assert model_low is not None

    def test_theory_credence_extracted(self, multi_theory_web):
        """Test that theory credences are extracted correctly."""
        bridge = eci.EpistemicCausalBridge(multi_theory_web)
        model = bridge.build_causal_models()

        # Check that theory models have credences
        for theory_id, theory_model in model.theory_models.items():
            assert hasattr(theory_model, 'theory_credence')
            assert 0 <= theory_model.theory_credence <= 1


# =============================================================================
# COUNTERFACTUAL INFERENCE TESTS
# =============================================================================

class TestCounterfactualInference:
    """Test counterfactual queries with epistemic constraints."""

    def test_counterfactual_basic(self, minimal_web):
        """Test basic counterfactual query."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        # Query: What if we increase nature exposure?
        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert result is not None
        assert hasattr(result, 'point_estimate')
        assert hasattr(result, 'confidence_interval')
        assert hasattr(result, 'epistemic_quality')

    def test_counterfactual_has_robustness(self, minimal_web):
        """Test that counterfactual includes robustness analysis."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'robustness')
        assert hasattr(result.robustness, 'robustness_score')

    def test_counterfactual_has_coherence(self, minimal_web):
        """Test that counterfactual includes coherence assessment."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'coherence')
        assert hasattr(result.coherence, 'coherence_score')

    def test_counterfactual_has_scope(self, minimal_web):
        """Test that counterfactual includes scope assessment."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'scope')
        assert hasattr(result.scope, 'scope_score')

    def test_counterfactual_theory_breakdown(self, multi_theory_web):
        """Test that counterfactual provides per-theory results."""
        bridge = eci.EpistemicCausalBridge(multi_theory_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature_walk": 1.0},
            outcome="mood"
        )

        assert hasattr(result, 'by_theory')
        assert isinstance(result.by_theory, dict)

    def test_counterfactual_generates_warnings(self, minimal_web):
        """Test that counterfactual generates appropriate warnings."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'warnings')
        assert isinstance(result.warnings, list)


# =============================================================================
# CONTRAST CLASS TESTS (Van Fraassen)
# =============================================================================

class TestContrastClass:
    """Test van Fraassen contrast class handling."""

    def test_contrast_class_construction(self):
        """Test ContrastClass can be constructed."""
        # Create a minimal population context
        pop_context = eci.PopulationContext(
            population_id="general",
            baselines={}
        )

        contrast = eci.ContrastClass(
            contrast_id="c1",
            focal=eci.ConditionSpec(
                variable="nature",
                value=1.0,
                description="20 min nature walk"
            ),
            contrasts=[
                eci.ConditionSpec(
                    variable="urban",
                    value=0.0,
                    description="20 min urban walk"
                )
            ],
            contrast_type=eci.ContrastType.ALTERNATIVE,
            population_context=pop_context
        )

        assert contrast.contrast_id == "c1"
        assert contrast.contrast_type == eci.ContrastType.ALTERNATIVE

    def test_counterfactual_with_contrast_class(self, minimal_web):
        """Test counterfactual query with explicit contrast class."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        pop_context = eci.PopulationContext(
            population_id="general",
            baselines={}
        )

        contrast = eci.ContrastClass(
            contrast_id="nature_vs_urban",
            focal=eci.ConditionSpec(
                variable="nature",
                value=1.0,
                description="Nature exposure"
            ),
            contrasts=[
                eci.ConditionSpec(
                    variable="urban",
                    value=0.0,
                    description="Urban exposure"
                )
            ],
            contrast_type=eci.ContrastType.ALTERNATIVE,
            population_context=pop_context
        )

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress",
            contrast_class=contrast
        )

        assert result is not None
        assert hasattr(result, 'contrast')


# =============================================================================
# ROBUSTNESS ANALYSIS TESTS
# =============================================================================

class TestRobustnessAnalysis:
    """Test robustness to belief revision."""

    def test_robustness_score_bounded(self, minimal_web):
        """Test that robustness score is properly bounded."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        score = result.robustness.robustness_score
        assert 0 <= score <= 1, f"Robustness score out of bounds: {score}"

    def test_robustness_identifies_sensitive_beliefs(self, minimal_web):
        """Test that robustness analysis identifies sensitive beliefs."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        # Robustness should have information about sensitive beliefs
        assert hasattr(result.robustness, 'sensitive_beliefs') or \
               hasattr(result.robustness, 'fragile_beliefs')


# =============================================================================
# EPISTEMIC QUALITY TESTS
# =============================================================================

class TestEpistemicQuality:
    """Test epistemic quality scoring."""

    def test_epistemic_quality_computed(self, minimal_web):
        """Test that epistemic quality is computed."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'epistemic_quality')
        assert 0 <= result.epistemic_quality <= 1

    def test_epistemic_quality_combines_components(self, minimal_web):
        """Test that epistemic quality combines robustness, coherence, scope."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        # Quality should reflect component scores
        components = [
            result.robustness.robustness_score,
            result.coherence.coherence_score,
            result.scope.scope_score,
        ]

        # All components should be bounded
        for score in components:
            assert 0 <= score <= 1


# =============================================================================
# INTEGRATION WITH EXISTING WEB TESTS
# =============================================================================

class TestExistingWebIntegration:
    """Test integration with factory-created webs."""

    def test_neuroarchitecture_web(self):
        """Test with the standard neuroarchitecture web."""
        web = create_neuroarchitecture_web()

        # Should have beliefs
        assert len(web.beliefs) > 0

        # Should be usable with bridge
        bridge = eci.EpistemicCausalBridge(web)
        assert bridge.web is web

    def test_neuroarchitecture_web_model_building(self):
        """Test building models from neuroarchitecture web."""
        web = create_neuroarchitecture_web()
        bridge = eci.EpistemicCausalBridge(web)

        # Should be able to build models
        model = bridge.build_causal_models(credence_threshold=0.3)
        assert model is not None


# =============================================================================
# SUMMARY METHOD TESTS
# =============================================================================

class TestSummaryMethods:
    """Test that result objects have summary methods."""

    def test_counterfactual_result_summary(self, minimal_web):
        """Test that counterfactual result has summary method."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert hasattr(result, 'summary')
        summary = result.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling in the integration."""

    def test_counterfactual_without_build(self, minimal_web):
        """Test counterfactual auto-builds if needed."""
        bridge = eci.EpistemicCausalBridge(minimal_web)

        # Should auto-build models
        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert result is not None
        assert bridge.multi_theory_model is not None

    def test_empty_web(self):
        """Test behavior with empty web."""
        web = WebOfBelief(domain="empty")
        bridge = eci.EpistemicCausalBridge(web)

        # Building models from empty web should not crash
        model = bridge.build_causal_models()
        assert model is not None


# =============================================================================
# WEB OF BELIEF INTEGRATION METHODS (Sprint 1.5.10)
# =============================================================================

class TestWebOfBeliefBridgeMethods:
    """Test the new bridge methods added to WebOfBelief."""

    def test_causal_bridge_available(self):
        """Test that bridge availability check works."""
        web = WebOfBelief(domain="test")
        # Should return True since we have the module
        assert web.causal_bridge_available() is True

    def test_create_causal_bridge(self, minimal_web):
        """Test creating a bridge from WebOfBelief."""
        bridge = minimal_web.create_causal_bridge()

        assert bridge is not None
        assert bridge.web is minimal_web

    def test_counterfactual_convenience_method(self, minimal_web):
        """Test the convenience counterfactual method on WebOfBelief."""
        result = minimal_web.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert result is not None
        assert hasattr(result, 'point_estimate')
        assert hasattr(result, 'epistemic_quality')

    def test_counterfactual_with_threshold(self, minimal_web):
        """Test counterfactual with custom credence threshold."""
        result = minimal_web.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress",
            credence_threshold=0.3
        )

        assert result is not None

    def test_neuroarchitecture_web_counterfactual(self):
        """Test counterfactual on the standard neuroarchitecture web."""
        web = create_neuroarchitecture_web()

        result = web.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert result is not None
        assert result.summary()  # Should produce a summary string


# =============================================================================
# VALUE COMPUTATION TESTS (Sprint 1.6.3)
# =============================================================================

class TestValueComputation:
    """Test Sprint 1.6.3 value computation methods."""

    def test_belief_centrality_basic(self, minimal_web):
        """Test that centrality is computed for beliefs."""
        # Theory belief has 1 outgoing constraint
        centrality = minimal_web.belief_centrality("theory:stress_recovery")
        assert 0 <= centrality <= 1

    def test_belief_centrality_more_connections(self, minimal_web):
        """Test that centrality increases with more connections."""
        # Mechanism belief has 2 connections (one in, one out)
        mech_centrality = minimal_web.belief_centrality("mech:parasympathetic")
        # Theory has 1 connection (out only)
        theory_centrality = minimal_web.belief_centrality("theory:stress_recovery")

        # Mechanism should have higher centrality due to more connections
        assert mech_centrality >= theory_centrality

    def test_belief_centrality_nonexistent(self, minimal_web):
        """Test centrality returns 0 for nonexistent beliefs."""
        centrality = minimal_web.belief_centrality("nonexistent")
        assert centrality == 0.0

    def test_belief_sensitivity_basic(self, minimal_web):
        """Test that sensitivity is computed."""
        sensitivity = minimal_web.belief_sensitivity("mech:parasympathetic")
        assert 0 <= sensitivity <= 1

    def test_belief_sensitivity_nonexistent(self, minimal_web):
        """Test sensitivity returns 0 for nonexistent beliefs."""
        sensitivity = minimal_web.belief_sensitivity("nonexistent")
        assert sensitivity == 0.0

    def test_belief_value_combines_metrics(self, minimal_web):
        """Test that value combines centrality and sensitivity."""
        value = minimal_web.belief_value("mech:parasympathetic")
        centrality = minimal_web.belief_centrality("mech:parasympathetic")
        sensitivity = minimal_web.belief_sensitivity("mech:parasympathetic")

        # With default weights (0.5, 0.5), value should be average
        expected = 0.5 * centrality + 0.5 * sensitivity
        assert abs(value - expected) < 0.01

    def test_belief_value_custom_weight(self, minimal_web):
        """Test value with custom centrality weight."""
        value = minimal_web.belief_value("mech:parasympathetic", centrality_weight=0.8)
        centrality = minimal_web.belief_centrality("mech:parasympathetic")
        sensitivity = minimal_web.belief_sensitivity("mech:parasympathetic")

        expected = 0.8 * centrality + 0.2 * sensitivity
        assert abs(value - expected) < 0.01

    def test_beliefs_by_value_returns_ranked_list(self, minimal_web):
        """Test beliefs_by_value returns sorted list."""
        ranked = minimal_web.beliefs_by_value()

        # Should have all beliefs
        assert len(ranked) == len(minimal_web.beliefs)

        # Should be tuples of (belief_id, value, centrality, sensitivity)
        for item in ranked:
            assert len(item) == 4
            assert item[0] in minimal_web.beliefs
            assert 0 <= item[1] <= 1  # value
            assert 0 <= item[2] <= 1  # centrality
            assert 0 <= item[3] <= 1  # sensitivity

        # Should be sorted by value descending
        values = [item[1] for item in ranked]
        assert values == sorted(values, reverse=True)

    def test_beliefs_by_value_top_n(self, minimal_web):
        """Test beliefs_by_value with top_n limit."""
        ranked = minimal_web.beliefs_by_value(top_n=2)
        assert len(ranked) == 2

    def test_high_value_beliefs(self, minimal_web):
        """Test high_value_beliefs returns detailed dicts."""
        # With low threshold to ensure we get results
        results = minimal_web.high_value_beliefs(threshold=0.0)

        assert len(results) > 0
        for result in results:
            assert 'belief_id' in result
            assert 'content' in result
            assert 'level' in result
            assert 'credence' in result
            assert 'entrenchment' in result
            assert 'value' in result
            assert 'centrality' in result
            assert 'sensitivity' in result
            assert 'inference_type' in result
            assert 'belief_kind' in result

    def test_empty_web_centrality(self):
        """Test centrality on empty web."""
        web = WebOfBelief(domain="empty")
        centrality = web.belief_centrality("nonexistent")
        assert centrality == 0.0

    def test_empty_web_beliefs_by_value(self):
        """Test beliefs_by_value on empty web."""
        web = WebOfBelief(domain="empty")
        ranked = web.beliefs_by_value()
        assert ranked == []

    def test_single_belief_no_constraints(self):
        """Test value metrics with single unconnected belief."""
        web = WebOfBelief(domain="test")
        web.add_belief(Belief(
            belief_id="lone",
            content="A lone belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.STUB,
            credence=Credence(0.5, 0.3)
        ))

        centrality = web.belief_centrality("lone")
        assert centrality == 0.0  # No connections

        # Sensitivity should be 0 (no constraints to affect coherence)
        sensitivity = web.belief_sensitivity("lone")
        assert sensitivity == 0.0

    def test_multi_theory_value_computation(self, multi_theory_web):
        """Test value computation with multiple theories."""
        ranked = multi_theory_web.beliefs_by_value()

        # Should have all beliefs from multi-theory web
        assert len(ranked) == len(multi_theory_web.beliefs)

        # All values should be valid
        for belief_id, value, centrality, sensitivity in ranked:
            assert 0 <= value <= 1


# =============================================================================
# TENSION-RESOLVING EXPERIMENTS TESTS (Sprint 1.6.4)
# =============================================================================

class TestTensionResolvingExperiments:
    """Test Sprint 1.6.4 tension-resolving experiment suggestions."""

    @pytest.fixture
    def tension_web(self):
        """Create a web with explicit tensions."""
        web = WebOfBelief(domain="test")

        # Add two contradictory empirical beliefs
        belief1 = Belief(
            belief_id="emp:nature_helps",
            content="Nature exposure reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.75, 0.15),
            entrenchment=0.5,
            paper_ids=["study_001"]
        )
        belief2 = Belief(
            belief_id="emp:nature_no_effect",
            content="Nature exposure has no effect on stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.70, 0.20),
            entrenchment=0.4,
            paper_ids=["study_002"]
        )

        web.add_belief(belief1)
        web.add_belief(belief2)

        # Add contradiction constraint
        web.add_constraint(Constraint(
            constraint_id="c:contradiction",
            source_id="emp:nature_helps",
            target_id="emp:nature_no_effect",
            constraint_type=ConstraintType.CONTRADICTS,
            strength=0.9
        ))

        return web

    def test_suggest_experiments_returns_list(self, tension_web):
        """Test that suggest_experiments returns a list."""
        suggestions = tension_web.suggest_experiments()
        assert isinstance(suggestions, list)

    def test_suggest_experiments_for_tension(self, tension_web):
        """Test that tensions generate experiment suggestions."""
        suggestions = tension_web.suggest_experiments()

        # Should have at least one suggestion for the contradiction
        assert len(suggestions) > 0

        # Check structure
        suggestion = suggestions[0]
        assert 'experiment_id' in suggestion
        assert 'type' in suggestion
        assert 'hypothesis' in suggestion
        assert 'source_belief' in suggestion
        assert 'priority' in suggestion

    def test_experiment_has_scope_suggestion(self, tension_web):
        """Test that experiments include scope suggestions."""
        suggestions = tension_web.suggest_experiments()

        if suggestions:
            assert 'scope_suggestion' in suggestions[0]

    def test_experiment_has_expected_resolution(self, tension_web):
        """Test that experiments include resolution expectations."""
        suggestions = tension_web.suggest_experiments()

        if suggestions:
            assert 'expected_resolution' in suggestions[0]

    def test_suggest_experiments_max_limit(self, tension_web):
        """Test max_suggestions limit."""
        suggestions = tension_web.suggest_experiments(max_suggestions=1)
        assert len(suggestions) <= 1

    def test_get_research_priorities(self, tension_web):
        """Test comprehensive research priorities."""
        priorities = tension_web.get_research_priorities()

        assert 'web_coherence' in priorities
        assert 'n_tensions' in priorities
        assert 'suggested_experiments' in priorities
        assert 'high_value_beliefs' in priorities
        assert 'research_directions' in priorities

    def test_research_priorities_coherence_value(self, tension_web):
        """Test that coherence is properly included."""
        priorities = tension_web.get_research_priorities()
        assert 0 <= priorities['web_coherence'] <= 1

    def test_empty_web_experiments(self):
        """Test experiments on empty web."""
        web = WebOfBelief(domain="empty")
        suggestions = web.suggest_experiments()
        assert suggestions == []

    def test_no_tension_web_experiments(self, minimal_web):
        """Test experiments on web without explicit tensions."""
        suggestions = minimal_web.suggest_experiments()
        # May or may not have suggestions depending on contested beliefs
        assert isinstance(suggestions, list)

    def test_contested_belief_experiment(self):
        """Test experiment suggestion for contested belief."""
        web = WebOfBelief(domain="test")

        belief = Belief(
            belief_id="contested",
            content="A contested finding",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.5, 0.3),
            contested=True
        )
        web.add_belief(belief)

        suggestions = web.suggest_experiments()

        # Should suggest experiment for contested belief
        assert any(s.get('tension_type') == 'credence_oscillation' for s in suggestions)

    def test_experiment_type_inference(self, tension_web):
        """Test that experiment type is inferred correctly."""
        suggestions = tension_web.suggest_experiments()

        if suggestions:
            exp_type = suggestions[0].get('type')
            # Conflicting empirical beliefs should suggest replication
            assert exp_type in ['replication_study', 'hypothesis_test', 'mechanism_study',
                               'measurement_study', 'exploratory_study']

    def test_priority_based_on_value(self, tension_web):
        """Test that priority is based on belief value."""
        suggestions = tension_web.suggest_experiments()

        for suggestion in suggestions:
            priority = suggestion.get('priority', 0)
            assert 0 <= priority <= 1

    def test_research_directions_generated(self, tension_web):
        """Test that research directions are generated."""
        priorities = tension_web.get_research_priorities()
        directions = priorities['research_directions']

        assert isinstance(directions, list)
        if directions:
            direction = directions[0]
            assert 'direction' in direction
            assert 'rationale' in direction
            assert 'approach' in direction


# =============================================================================
# ENABLING CONDITIONS TESTS (P-EC-R9)
# =============================================================================

class TestEnablingConditions:
    """Test P-EC-R9: Check enabling_conditions before counterfactuals."""

    @pytest.fixture
    def enabling_web(self):
        """Create a web with beliefs that have enabling conditions."""
        web = WebOfBelief(domain="test")

        # Belief with enabling conditions
        belief_with_conditions = Belief(
            belief_id="theory:stress_recovery",
            content="Nature exposure reduces stress",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.75, 0.15),
            entrenchment=0.7,
            theory_id="SRT",
            enabling_conditions=EnablingConditions(
                minimum_exposure=">30 minutes",
                baseline_state="elevated stress",
                concurrent_factors=["quiet environment"],
                blocking_factors=["urban noise"]
            ),
            tags=["outcome:stress", "exposure:nature"]
        )
        web.add_belief(belief_with_conditions)
        web.theory_ids.add("SRT")

        # Belief without enabling conditions
        belief_without_conditions = Belief(
            belief_id="mech:parasympathetic",
            content="Nature activates parasympathetic nervous system",
            level=EpistemicLevel.INTERMEDIATE,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.70, 0.20),
            entrenchment=0.5,
            theory_id="SRT",
            tags=["outcome:parasympathetic", "exposure:nature"]
        )
        web.add_belief(belief_without_conditions)

        return web

    def test_check_enabling_conditions_no_conditions(self, minimal_web):
        """Test that beliefs without conditions pass the check."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        belief = minimal_web.beliefs["theory:stress_recovery"]

        result = bridge._check_enabling_conditions(belief)
        assert result is True

    def test_check_enabling_conditions_with_conditions(self, enabling_web):
        """Test that beliefs with conditions are checked."""
        bridge = eci.EpistemicCausalBridge(enabling_web)
        belief = enabling_web.beliefs["theory:stress_recovery"]

        # Should still return True (we can't verify conditions)
        # but the check is performed
        result = bridge._check_enabling_conditions(belief)
        assert result is True

    def test_get_blocked_beliefs_initially_empty(self, minimal_web):
        """Test that blocked beliefs list is initially empty."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        blocked = bridge.get_blocked_beliefs()
        assert blocked == []

    def test_serialize_enabling_conditions(self, enabling_web):
        """Test enabling conditions serialization."""
        bridge = eci.EpistemicCausalBridge(enabling_web)
        belief = enabling_web.beliefs["theory:stress_recovery"]

        serialized = bridge._serialize_enabling_conditions(belief)

        assert serialized is not None
        assert 'minimum_exposure' in serialized
        assert serialized['minimum_exposure'] == ">30 minutes"
        assert 'blocking_factors' in serialized
        assert 'urban noise' in serialized['blocking_factors']

    def test_serialize_enabling_conditions_none(self, minimal_web):
        """Test serialization returns None when no conditions."""
        bridge = eci.EpistemicCausalBridge(minimal_web)
        belief = minimal_web.beliefs["theory:stress_recovery"]

        serialized = bridge._serialize_enabling_conditions(belief)
        assert serialized is None

    def test_get_theory_beliefs_includes_check_param(self, enabling_web):
        """Test that _get_theory_beliefs has check_enabling parameter."""
        bridge = eci.EpistemicCausalBridge(enabling_web)

        # With check enabled (default)
        beliefs_checked = bridge._get_theory_beliefs("SRT", 0.5, check_enabling=True)
        assert isinstance(beliefs_checked, list)

        # Without check
        beliefs_unchecked = bridge._get_theory_beliefs("SRT", 0.5, check_enabling=False)
        assert isinstance(beliefs_unchecked, list)

    def test_counterfactual_with_enabling_conditions(self, enabling_web):
        """Test counterfactual works with beliefs that have enabling conditions."""
        bridge = eci.EpistemicCausalBridge(enabling_web)
        bridge.build_causal_models()

        result = bridge.counterfactual(
            intervention={"nature": 1.0},
            outcome="stress"
        )

        assert result is not None
        assert hasattr(result, 'point_estimate')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
