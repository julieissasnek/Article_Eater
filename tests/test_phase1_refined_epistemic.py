"""
Article Eater - Comprehensive Test Plan
========================================

Tests for the refined epistemic architecture based on Expert Panel recommendations.

Test Categories:
1. Unit Tests - Individual components work correctly
2. Integration Tests - Components work together
3. Philosophical Tests - Architecture captures intended epistemology
4. Calibration Tests - System makes accurate predictions
5. Temporal Tests - Temporal parameters are extracted and aggregated correctly

Based on Glymour's criteria:
- Coherence predicts stability
- Grounded credences predict replication
- VOI predicts informativeness
"""

import pytest
import math
from typing import Dict, Any, List

# Import modules under test
from src.services.refined_epistemic import (
    RefinedEpistemicState,
    SemanticBelief,
    SemanticStatus,
    RefinedDependency,
    DependencyType,
    BovensHartmannCoherence,
    create_refined_neuroarchitecture
)

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    EpistemicLevel,
    BeliefStatus,
    Credence,
    UncertainQuantity,
    create_neuroarchitecture_web
)

from src.services.abstraction_levels import (
    AbstractionController,
    AbstractionLevel,
    NestedTheory,
    TheoryDependency,
    CriterialRule,
    create_grounded_neuroarchitecture
)


# =============================================================================
# 1. UNIT TESTS
# =============================================================================

class TestSemanticStatus:
    """Test semantic status and revisability."""
    
    def test_revisability_ordering(self):
        """Analytic < Criterial < Framework < Synthetic < Peripheral."""
        beliefs = [
            SemanticBelief("a", "test", SemanticStatus.ANALYTIC),
            SemanticBelief("c", "test", SemanticStatus.CRITERIAL),
            SemanticBelief("f", "test", SemanticStatus.FRAMEWORK),
            SemanticBelief("s", "test", SemanticStatus.SYNTHETIC),
            SemanticBelief("p", "test", SemanticStatus.PERIPHERAL),
        ]
        
        revisabilities = [b.revisability() for b in beliefs]
        assert revisabilities == sorted(revisabilities), "Revisability should increase"
    
    def test_criterial_very_low_revisability(self):
        """Criterial beliefs should be very hard to revise."""
        criterial = SemanticBelief("c", "test", SemanticStatus.CRITERIAL)
        assert criterial.revisability() < 0.1
    
    def test_revision_type_classification(self):
        """Different semantic statuses have different revision types."""
        criterial = SemanticBelief("c", "test", SemanticStatus.CRITERIAL)
        synthetic = SemanticBelief("s", "test", SemanticStatus.SYNTHETIC)
        
        assert criterial.revision_type() == "meaning_change"
        assert synthetic.revision_type() == "belief_change"


class TestDependencyTypes:
    """Test dependency types and propagation."""
    
    def test_propagation_ordering(self):
        """Presuppositional > Constitutive > Explanatory > Evidential > Analogical."""
        deps = [
            RefinedDependency("p", "a", "b", DependencyType.PRESUPPOSITIONAL, 1.0),
            RefinedDependency("c", "a", "b", DependencyType.CONSTITUTIVE, 1.0),
            RefinedDependency("x", "a", "b", DependencyType.EXPLANATORY, 1.0),
            RefinedDependency("e", "a", "b", DependencyType.EVIDENTIAL, 1.0),
            RefinedDependency("a", "a", "b", DependencyType.ANALOGICAL, 1.0),
        ]
        
        factors = [d.propagation_factor() for d in deps]
        assert factors == sorted(factors, reverse=True), "Propagation should be ordered"
    
    def test_strength_scales_propagation(self):
        """Stronger dependencies propagate more."""
        weak = RefinedDependency("w", "a", "b", DependencyType.EVIDENTIAL, 0.3)
        strong = RefinedDependency("s", "a", "b", DependencyType.EVIDENTIAL, 0.9)
        
        assert strong.propagation_factor() > weak.propagation_factor()


class TestBovensHartmannCoherence:
    """Test coherence calculations."""
    
    def test_independent_beliefs_zero_coherence(self):
        """Independent beliefs should have ~0 coherence."""
        calc = BovensHartmannCoherence()
        
        # P(A) = 0.5, P(B) = 0.5, P(A,B) = 0.25 (independent)
        coherence = calc.pairwise_coherence(0.5, 0.5, 0.25)
        assert abs(coherence) < 0.1, "Independent beliefs should have near-zero coherence"
    
    def test_perfectly_correlated_positive_coherence(self):
        """Perfectly correlated beliefs should have positive coherence."""
        calc = BovensHartmannCoherence()
        
        # P(A) = 0.5, P(B) = 0.5, P(A,B) = 0.5 (perfect positive correlation)
        coherence = calc.pairwise_coherence(0.5, 0.5, 0.5)
        assert coherence > 0.5, "Correlated beliefs should have positive coherence"
    
    def test_contradictory_negative_coherence(self):
        """Contradictory beliefs should have negative coherence."""
        calc = BovensHartmannCoherence()
        
        # P(A) = 0.8, P(B) = 0.8, P(A,B) = 0.2 (below independence)
        coherence = calc.pairwise_coherence(0.8, 0.8, 0.2)
        assert coherence < 0, "Contradictory beliefs should have negative coherence"


class TestUncertainQuantity:
    """Test uncertain quantity updates."""
    
    def test_update_reduces_uncertainty(self):
        """Adding observations should reduce uncertainty."""
        uq = UncertainQuantity(estimate=100, standard_error=20, n_observations=1)
        updated = uq.update(105, 15, weight=1.0)
        
        assert updated.standard_error < uq.standard_error
        assert updated.n_observations == 2
    
    def test_update_shifts_estimate(self):
        """Estimate should shift toward observations."""
        uq = UncertainQuantity(estimate=100, standard_error=20, n_observations=1)
        updated = uq.update(150, 20, weight=1.0)
        
        assert 100 < updated.estimate < 150
    
    def test_moderator_tracking(self):
        """Updates with moderators should track by moderator."""
        uq = UncertainQuantity(estimate=100, standard_error=20, n_observations=0)
        
        uq = uq.update(80, 10, moderator_key="indoor")
        uq = uq.update(120, 10, moderator_key="outdoor")
        
        assert "indoor" in uq.by_moderator
        assert "outdoor" in uq.by_moderator
        assert uq.by_moderator["indoor"].estimate < uq.by_moderator["outdoor"].estimate
    
    def test_heterogeneity_detection(self):
        """Heterogeneity should be detected when moderator values differ."""
        uq = UncertainQuantity(estimate=100, standard_error=20, n_observations=0)
        
        # Add very different values for different moderators
        uq = uq.update(50, 10, moderator_key="condition_a")
        uq = uq.update(150, 10, moderator_key="condition_b")
        
        assert uq.heterogeneity() > 0.3, "Should detect heterogeneity"


# =============================================================================
# 2. INTEGRATION TESTS
# =============================================================================

class TestRefinedEpistemicState:
    """Test refined epistemic state integration."""
    
    def test_create_neuroarchitecture(self):
        """Should create valid neuroarchitecture state."""
        state = create_refined_neuroarchitecture()
        
        assert len(state.beliefs) >= 6
        assert len(state.dependencies) >= 4
        assert state.global_coherence() > 0
    
    def test_evidence_propagates(self):
        """Evidence should propagate through dependencies."""
        state = create_refined_neuroarchitecture()
        
        old_srt = state.beliefs["SRT_core"].credence
        
        state.add_evidence(
            "new_evidence",
            "New study supports cortisol reduction",
            supports={"nature_cortisol": 0.7}
        )
        
        # Should propagate to SRT_core via evidential dependency
        # (nature_cortisol -> SRT_core)
        new_srt = state.beliefs["SRT_core"].credence
        assert new_srt >= old_srt, "Evidence should propagate"
    
    def test_constitutive_propagates_strongly(self):
        """Constitutive dependencies should propagate more than evidential."""
        state = create_refined_neuroarchitecture()
        
        # Force update to criterial rule
        crit = state.beliefs["crit_cortisol"]
        old_nature = state.beliefs["nature_cortisol"].credence
        
        state.update_belief("crit_cortisol", crit.credence - 0.1)
        
        new_nature = state.beliefs["nature_cortisol"].credence
        delta = old_nature - new_nature
        
        # Constitutive should cause significant propagation
        assert delta > 0.05, "Constitutive should propagate strongly"


class TestWebOfBelief:
    """Test web of belief integration."""
    
    def test_create_web(self):
        """Should create valid web."""
        web = create_neuroarchitecture_web()
        
        assert len(web.beliefs) >= 5
        assert len(web.theory_ids) >= 2
        assert len(web.theory_worlds) == 2 ** len(web.theory_ids)
    
    def test_joint_probability_updates(self):
        """Theory worlds should update with evidence."""
        web = create_neuroarchitecture_web()
        
        old_p_art = web.marginal_theory_probability("ART")
        
        web.add_evidence(
            "ev_test",
            "Test evidence",
            "paper:test",
            theory_relevance={"ART": 0.8}
        )
        
        new_p_art = web.marginal_theory_probability("ART")
        assert new_p_art > old_p_art
    
    def test_stubs_exist(self):
        """Stubs should be unintegrated."""
        web = create_neuroarchitecture_web()
        stubs = web.get_stubs()
        
        assert len(stubs) >= 1
        for stub in stubs:
            assert stub.status == BeliefStatus.STUB
    
    def test_equilibrium_reduces_tensions(self):
        """Seeking equilibrium should reduce tensions."""
        web = create_neuroarchitecture_web()
        
        # Create a tension
        from src.services.web_of_belief import ConstraintType
        anomaly = Belief(
            belief_id="anomaly",
            content="Contradicts nature_restores_attention",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.3),
            entrenchment=0.2
        )
        web.add_belief(anomaly, connect_to=[
            ("nature_restores_attention", ConstraintType.CONTRADICTS, 0.7)
        ])
        
        initial_tensions = len(web.tensions())
        result = web.seek_equilibrium()
        final_tensions = result["remaining_tensions"]
        
        assert final_tensions <= initial_tensions


class TestAbstractionController:
    """Test abstraction level control."""
    
    def test_grounded_credences(self):
        """Grounded credences should account for dependencies."""
        controller = create_grounded_neuroarchitecture()
        
        srt = controller.nested_theories["SRT"]
        
        # SRT depends on stress_physiology (essential)
        # Grounded should be less than local (dependencies reduce)
        assert srt.grounded_credence <= srt.local_credence
    
    def test_dependency_weakening_propagates(self):
        """Weakening a deep theory should affect dependent theories."""
        controller = create_grounded_neuroarchitecture()
        
        old_biophilia = controller.nested_theories["BIOPHILIA"].grounded_credence
        
        # Weaken evolutionary psychology
        controller.nested_theories["evolutionary_psychology"].local_credence = 0.3
        
        # Recompute grounded credences
        for theory in controller.nested_theories.values():
            if theory.dependencies:
                supporting_creds = {
                    dep.supporting_theory: controller.nested_theories[dep.supporting_theory].local_credence
                    for dep in theory.dependencies
                    if dep.supporting_theory in controller.nested_theories
                }
                theory.compute_grounded_credence(supporting_creds)
        
        new_biophilia = controller.nested_theories["BIOPHILIA"].grounded_credence
        
        # Biophilia depends essentially on evopsych, should drop significantly
        assert new_biophilia < old_biophilia * 0.8


# =============================================================================
# 3. PHILOSOPHICAL TESTS
# =============================================================================

class TestQuineanProperties:
    """Test that the architecture captures Quinean epistemology."""
    
    def test_no_unrevisable_beliefs(self):
        """All beliefs should have some revisability > 0."""
        state = create_refined_neuroarchitecture()
        
        for belief in state.beliefs.values():
            assert belief.revisability() > 0, f"{belief.belief_id} should be revisable"
    
    def test_entrenchment_is_emergent(self):
        """Entrenchment should emerge from dependency structure."""
        state = create_refined_neuroarchitecture()
        
        # Criterial beliefs should be more entrenched (many depend on them)
        criterial = [b for b in state.beliefs.values() 
                    if b.semantic_status == SemanticStatus.CRITERIAL]
        synthetic = [b for b in state.beliefs.values() 
                    if b.semantic_status == SemanticStatus.SYNTHETIC]
        
        avg_crit_entrench = sum(b.entrenchment for b in criterial) / len(criterial)
        avg_synth_entrench = sum(b.entrenchment for b in synthetic) / len(synthetic)
        
        assert avg_crit_entrench > avg_synth_entrench
    
    def test_mutual_constraint(self):
        """Changes at any level should potentially affect other levels."""
        web = create_neuroarchitecture_web()
        
        # Get beliefs at different levels
        theoretical = web.get_beliefs_by_level(EpistemicLevel.THEORETICAL)
        empirical = web.get_beliefs_by_level(EpistemicLevel.INTERMEDIATE)
        
        # Change at empirical level should affect theoretical
        if empirical:
            web.add_evidence(
                "ev_mutual",
                "New evidence",
                "paper:test",
                supports_beliefs={empirical[0].belief_id: 0.7},
                theory_relevance={"ART": 0.7}
            )
            
            # Theory probability should have changed
            assert web.marginal_theory_probability("ART") != 0.5


class TestReflectiveEquilibrium:
    """Test reflective equilibrium properties."""
    
    def test_less_entrenched_adjusts(self):
        """In tension, less entrenched belief should adjust more."""
        web = create_neuroarchitecture_web()
        
        # Add anomaly with low entrenchment
        from src.services.web_of_belief import ConstraintType
        anomaly = Belief(
            belief_id="anomaly_re",
            content="Contradicts established belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.3),
            entrenchment=0.1  # Very low
        )
        web.add_belief(anomaly, connect_to=[
            ("nature_restores_attention", ConstraintType.CONTRADICTS, 0.7)
        ])
        
        old_anomaly = web.beliefs["anomaly_re"].credence.value
        old_established = web.beliefs["nature_restores_attention"].credence.value
        
        web.seek_equilibrium()
        
        new_anomaly = web.beliefs["anomaly_re"].credence.value
        new_established = web.beliefs["nature_restores_attention"].credence.value
        
        # Anomaly should have adjusted more
        anomaly_change = abs(new_anomaly - old_anomaly)
        established_change = abs(new_established - old_established)
        
        assert anomaly_change >= established_change


# =============================================================================
# 4. CALIBRATION TESTS (require real data)
# =============================================================================

class TestCalibrationPlaceholders:
    """Placeholder tests for calibration (require real PDFs)."""
    
    def test_credence_calibration_structure(self):
        """Test that we can track calibration."""
        # This test structure will be filled when PDFs are available
        state = create_refined_neuroarchitecture()
        
        # We should be able to extract beliefs with credences
        beliefs_with_credence = [
            (b.belief_id, b.credence)
            for b in state.beliefs.values()
            if b.semantic_status in [SemanticStatus.SYNTHETIC, SemanticStatus.PERIPHERAL]
        ]
        
        assert len(beliefs_with_credence) >= 2
        # TODO: With real data, check if 0.7 credence beliefs are true ~70% of time
    
    def test_temporal_extraction_structure(self):
        """Test that temporal extraction structure exists."""
        # This will be filled when PDFs are available
        uq = UncertainQuantity(estimate=1200, standard_error=300, n_observations=0)
        
        # Structure should support extraction and aggregation
        uq = uq.update(1100, 200)
        uq = uq.update(1350, 250)
        
        assert uq.n_observations == 2
        assert 1100 < uq.estimate < 1350


# =============================================================================
# 5. TEMPORAL TESTS
# =============================================================================

class TestTemporalParameters:
    """Test temporal parameter handling."""
    
    def test_temporal_aggregation(self):
        """Temporal parameters should aggregate across observations."""
        uq = UncertainQuantity(estimate=1200, standard_error=300, n_observations=0,
                               lower_bound=0)
        
        # Add multiple observations
        observations = [1100, 1300, 1150, 1250, 1200]
        for obs in observations:
            uq = uq.update(obs, 150)
        
        assert uq.n_observations == 5
        # Should converge toward mean
        assert 1100 < uq.estimate < 1300
        # SE should decrease with more observations
        assert uq.standard_error < 300
    
    def test_moderator_heterogeneity_detection(self):
        """Should detect heterogeneity across moderators."""
        uq = UncertainQuantity(estimate=1200, standard_error=300, n_observations=0)
        
        # Add very different values for different conditions
        for _ in range(3):
            uq = uq.update(800, 100, moderator_key="short_exposure")
        for _ in range(3):
            uq = uq.update(1600, 100, moderator_key="long_exposure")
        
        heterogeneity = uq.heterogeneity()
        assert heterogeneity > 0.3, "Should detect substantial heterogeneity"


# =============================================================================
# RUN TESTS
# =============================================================================

def run_all_tests():
    """Run all tests and report results."""
    import traceback
    
    test_classes = [
        TestSemanticStatus,
        TestDependencyTypes,
        TestBovensHartmannCoherence,
        TestUncertainQuantity,
        TestRefinedEpistemicState,
        TestWebOfBelief,
        TestAbstractionController,
        TestQuineanProperties,
        TestReflectiveEquilibrium,
        TestCalibrationPlaceholders,
        TestTemporalParameters,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__name__}")
        print('='*60)
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    print('='*60)
    
    if failed_tests:
        print("\nFailed tests:")
        for cls, method, error in failed_tests:
            print(f"  - {cls}.{method}: {error}")
    
    return passed_tests, total_tests, failed_tests


if __name__ == "__main__":
    run_all_tests()
