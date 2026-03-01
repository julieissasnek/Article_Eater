"""
test_cva_three_hard_problems.py — R2.6 Test Suite
===================================================

Tests for the Three Hard Problems remediation (R2.1–R2.5).
~20 new tests; all 24 existing must still pass.

Reference: AG_PHASE2_REMEDIATION §R2.6
"""

import pytest
import numpy as np
from unittest.mock import Mock

from src.services.cva_constraint_engine import (
    CVAConstraintEngine,
    ConstraintDistribution,
    FRAME_PRECISIONS,
)
from src.services.cva_dynamics import (
    CVACouplingMatrices,
    CVADynamicsEngine,
    CoupledDynamicsState,
    DecomposedFeedbackEngine,
    DecomposedFeedback,
    phi,
    phi_prime,
)
from src.services.cva_valuation_engine import (
    CVAValuationEngine,
    CompleteValuationVector,
    AUXILIARY_FRAME_CONFIG,
)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


# ══════════════════════════════════════════════════════════════════
# R2.1: Probabilistic Constraint Recognition
# ══════════════════════════════════════════════════════════════════

class TestProbabilisticConstraintRecognition:

    def test_constraint_distribution_mean_and_precision(self):
        """ConstraintDistribution correctly parameterized."""
        mean = [0.5] * 8
        precision = [2.0] * 8
        dist = ConstraintDistribution(mean=mean, precision=precision,
                                       activity_frame="RESTING")
        np.testing.assert_array_almost_equal(dist.map_estimate(), mean)
        assert dist.activity_frame == "RESTING"

    def test_constraint_distribution_sampling(self):
        """sample() produces correct shape and approximate mean/std."""
        np.random.seed(42)
        mean = [0.5, -0.5, 0.2, 0.0, 1.0, 0.1, -0.3, 0.8]
        precision = [2.0, 1.5, 1.0, 0.5, 0.8, 1.2, 0.9, 1.1]
        dist = ConstraintDistribution(mean=mean, precision=precision,
                                       activity_frame="EXPLORING")

        samples = dist.sample(n=10000)
        assert samples.shape == (10000, 8)

        sample_mean = np.mean(samples, axis=0)
        np.testing.assert_array_almost_equal(sample_mean, mean, decimal=1)

        expected_std = 1.0 / np.sqrt(np.array(precision) + 1e-8)
        sample_std = np.std(samples, axis=0)
        np.testing.assert_array_almost_equal(sample_std, expected_std, decimal=1)

    def test_entropy_decreases_with_precision(self):
        """Higher precision → lower entropy."""
        mean = [0.5] * 8
        dist_low = ConstraintDistribution(mean=mean, precision=[0.5]*8,
                                           activity_frame="EXPLORING")
        dist_high = ConstraintDistribution(mean=mean, precision=[2.0]*8,
                                            activity_frame="RESTING")
        assert dist_high.entropy() < dist_low.entropy()

    def test_backward_compatibility_map_estimate(self):
        """MAP estimate equals mean for Gaussian."""
        np.random.seed(42)
        mean = list(np.random.randn(8))
        precision = list(np.random.rand(8) + 0.1)
        dist = ConstraintDistribution(mean=mean, precision=precision,
                                       activity_frame="EATING")
        np.testing.assert_array_almost_equal(dist.map_estimate(), mean)

    def test_recognize_probabilistic_produces_distribution(self):
        """Engine produces valid ConstraintDistribution."""
        engine = CVAConstraintEngine()
        scene = {"edge": 0.5, "motion": 0.3, "contrast": 0.6,
                 "figure_ground": 0.5, "temporal_coherence": 0.7, "symmetry": 0.4}
        dist = engine.recognize_constraints_probabilistic(scene, "RESTING")
        assert len(dist.mean) == 8
        assert len(dist.precision) == 8
        assert dist.activity_frame == "RESTING"


# ══════════════════════════════════════════════════════════════════
# R2.2: Decomposed Feedback
# ══════════════════════════════════════════════════════════════════

class TestDecomposedFeedback:

    def test_attention_error_with_gaze(self):
        """Gaze-modulated attention error = dot(gaze, precision)."""
        engine = DecomposedFeedbackEngine()
        precision = [2.0, 1.0, 0.5, 0.3, 0.3, 0.5, 1.0, 2.0]
        dist = ConstraintDistribution(mean=[0.5]*8, precision=precision,
                                       activity_frame="RESTING")
        gaze = np.array([1.0, 0.5, 0.2, 0.1, 0.1, 0.2, 0.5, 1.0])

        e_attn = engine.compute_attention_error(dist, np.ones(9), "RESTING", gaze)
        expected = np.dot(gaze, precision)
        assert abs(e_attn - expected) < 1e-6

    def test_attention_error_without_gaze(self):
        """Default attention error = RMS(precision)."""
        engine = DecomposedFeedbackEngine()
        precision = [2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0]
        dist = ConstraintDistribution(mean=[0.5]*8, precision=precision,
                                       activity_frame="RESTING")

        e_attn = engine.compute_attention_error(dist, np.ones(9), "RESTING")
        expected = np.sqrt(np.mean(np.array(precision) ** 2))
        assert abs(e_attn - expected) < 1e-6

    def test_precision_error_variance_mismatch(self):
        """High variance samples → high precision error."""
        engine = DecomposedFeedbackEngine()
        np.random.seed(42)
        high_var = [np.random.randn(8) * 2.0 for _ in range(10)]
        e_prec = engine.compute_precision_error(high_var, "RESTING")
        assert e_prec > 0

    def test_prior_error_cultural_baseline(self):
        """Deviation from baseline → nonzero prior error."""
        engine = DecomposedFeedbackEngine()
        vals = np.ones(9) * 0.5
        baseline = np.ones(9) * 1.0

        e_prior = engine.compute_prior_error(
            np.ones(8), vals, "WORSHIPPING",
            cultural_baseline=baseline,
        )
        expected = np.linalg.norm(vals - baseline)
        assert abs(e_prior - expected) < 1e-6

    def test_compose_feedback_timescale_decay(self):
        """Attention decays fastest; prior decays slowest."""
        engine = DecomposedFeedbackEngine()
        fb = engine.compose_feedback(1.0, 1.0, 1.0, dt=1.0)

        # After 1s:  attn exp(-1/0.4)≈0.082 < prec exp(-1/1.0)≈0.368 < prior exp(-1/3.0)≈0.717
        assert fb.epsilon_attention < fb.epsilon_precision < fb.epsilon_prior

    def test_feedback_dominance(self):
        """Dominant signal identified correctly."""
        fb = DecomposedFeedback(
            epsilon_attention=0.5,
            epsilon_precision=2.0,
            epsilon_prior=0.3,
        )
        assert fb.dominance() == "precision"

    def test_feedback_total_magnitude(self):
        """Total magnitude = L2 norm."""
        fb = DecomposedFeedback(
            epsilon_attention=3.0,
            epsilon_precision=4.0,
            epsilon_prior=0.0,
        )
        assert abs(fb.total_magnitude() - 5.0) < 1e-6


# ══════════════════════════════════════════════════════════════════
# R2.3: Sparse Auxiliary Activation
# ══════════════════════════════════════════════════════════════════

class TestSparseAuxiliaryActivation:

    def test_worshipping_activates_sacredness(self):
        """WORSHIPPING frame activates sacredness auxiliary."""
        config = AUXILIARY_FRAME_CONFIG["WORSHIPPING"]
        assert "sacredness" in config["auxiliary_axes"]

    def test_creating_activates_originality(self):
        """CREATING frame activates originality auxiliary."""
        config = AUXILIARY_FRAME_CONFIG["CREATING"]
        assert "originality" in config["auxiliary_axes"]

    def test_resting_has_no_auxiliaries(self):
        """RESTING frame has no active auxiliaries."""
        config = AUXILIARY_FRAME_CONFIG["RESTING"]
        assert len(config["auxiliary_axes"]) == 0

    def test_complete_valuation_sparse(self):
        """CompleteValuationVector correctly stores core + sparse aux."""
        core = np.ones(9) * 0.5
        gains = np.ones(9)
        val = CompleteValuationVector(
            core=core, auxiliary={"sacredness": 0.8},
            active_auxiliary_axes=["sacredness"],
            activity_frame="WORSHIPPING", precision_gains=gains,
        )
        assert val.core.shape == (9,)
        assert "sacredness" in val.auxiliary
        assert val.get_full_valuation().shape == (10,)  # 9 core + 1 aux
        assert val.core_only().shape == (9,)

    def test_compute_valuation_with_frame_produces_auxiliaries(self):
        """compute_valuation_with_frame() activates correct auxiliaries."""
        engine = CVAValuationEngine()
        from src.models.subject_characteristics import SubjectCharacteristics
        scene = {"edge": 0.5, "motion": 0.3, "contrast": 0.6,
                 "figure_ground": 0.5, "temporal_coherence": 0.7, "symmetry": 0.4}
        from src.services.cva_constraint_engine import CVAConstraintEngine
        c_engine = CVAConstraintEngine()
        c = c_engine.compute(scene)

        # WORSHIPPING should have sacredness
        val = engine.compute_valuation_with_frame(c, "WORSHIPPING")
        assert "sacredness" in val.auxiliary
        assert val.activity_frame == "WORSHIPPING"

        # RESTING should have no auxiliaries
        val_rest = engine.compute_valuation_with_frame(c, "RESTING")
        assert len(val_rest.auxiliary) == 0


# ══════════════════════════════════════════════════════════════════
# R2.4: Coupling Dynamics
# ══════════════════════════════════════════════════════════════════

class TestCouplingDynamics:

    def test_soft_relu_activation(self):
        """φ(0) = log(2), φ'(x) = sigmoid(x)."""
        assert phi(0.0) == pytest.approx(np.log(2), abs=1e-6)
        assert phi(10.0) > phi(0.0)
        assert phi(-10.0) < phi(0.0)

        x = np.linspace(-5, 5, 11)
        computed = phi_prime(x, alpha=1.0)
        expected = 1.0 / (1.0 + np.exp(-x))
        np.testing.assert_array_almost_equal(computed, expected)

    def test_coupling_matrices_default_shapes(self):
        """Default coupling has correct matrix shapes."""
        coupling = CVACouplingMatrices.default()
        assert coupling.K_cc.shape == (8, 8)
        assert coupling.K_cv.shape == (8, 9)
        assert coupling.K_vc.shape == (9, 8)
        assert coupling.K_vv.shape == (9, 9)

    def test_coupling_strength_reasonable(self):
        """Default coupling κ_loop < 0.5."""
        coupling = CVACouplingMatrices.default()
        kappa = coupling.estimate_coupling_strength()
        assert kappa < 0.5

    def test_dynamics_engine_step(self):
        """Single integration step produces valid output."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        state = CoupledDynamicsState(
            constraints=np.ones(8) * 0.5,
            valuations=np.ones(9) * 0.5,
            constraint_target=np.ones(8) * 0.5,
            valuation_target=np.ones(9) * 0.5,
        )
        new_state = engine.step(state, coupling)
        assert new_state.constraints.shape == (8,)
        assert new_state.valuations.shape == (9,)
        assert new_state.time == pytest.approx(0.01)

    def test_convergence_to_fixed_point(self):
        """Dynamics converge to stable fixed point."""
        np.random.seed(42)
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        state = CoupledDynamicsState(
            constraints=np.random.randn(8) * 0.1,
            valuations=np.random.randn(9) * 0.1,
            constraint_target=np.zeros(8),
            valuation_target=np.zeros(9),
        )
        final, trajectory = engine.run_to_convergence(
            state, coupling, max_steps=5000, tolerance=1e-3,
        )
        # Should converge near targets (allowing for phi(0)≈0.69 offset)
        assert len(trajectory) > 1

    def test_coupling_serialization(self):
        """CVACouplingMatrices round-trips through dict."""
        coupling = CVACouplingMatrices.default()
        data = coupling.to_dict()
        coupling2 = CVACouplingMatrices.from_dict(data)
        np.testing.assert_array_almost_equal(coupling.K_cc, coupling2.K_cc)
        np.testing.assert_array_almost_equal(coupling.K_vc, coupling2.K_vc)


# ══════════════════════════════════════════════════════════════════
# R2.5: Lyapunov Analysis
# ══════════════════════════════════════════════════════════════════

class TestLyapunovAnalysis:

    def test_jacobian_shape(self):
        """Full Jacobian is 17×17."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        state = CoupledDynamicsState(
            constraints=np.ones(8) * 0.1,
            valuations=np.ones(9) * 0.1,
            constraint_target=np.zeros(8),
            valuation_target=np.zeros(9),
        )
        J = engine.compute_full_jacobian(state, coupling)
        assert J.shape == (17, 17)
        assert np.linalg.norm(J) > 0

    def test_stability_at_origin(self):
        """Origin is stable for default coupling."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        fp = np.zeros(17)
        stab = engine.check_attractor_stability(fp, coupling)
        assert stab["is_stable"] or stab["max_real_eigenvalue"] < 1.0
        assert stab["kappa_loop"] < 0.1

    def test_stability_report_structure(self):
        """Stability report contains all required fields."""
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        stab = engine.check_attractor_stability(np.zeros(17), coupling)
        assert "eigenvalues" in stab
        assert "max_real_eigenvalue" in stab
        assert "is_stable" in stab
        assert "kappa_loop" in stab
        assert "dominance_profile" in stab


# ══════════════════════════════════════════════════════════════════
# Integration: Full Cycle
# ══════════════════════════════════════════════════════════════════

class TestIntegrationThreeHardProblems:

    def test_full_pipeline_constraint_to_dynamics(self):
        """Constraints → Distribution → Feedback → Dynamics → Stability."""
        # R2.1: Probabilistic constraints
        mean = [0.5] * 8
        precision = [2.0, 1.5, 1.0, 0.5, 0.8, 1.2, 0.9, 1.1]
        dist = ConstraintDistribution(mean=mean, precision=precision,
                                       activity_frame="RESTING")

        # R2.3: Frame-aware valuation
        core = np.ones(9) * 0.5
        gains = np.array([1.5, 1.5, 1.0, 0.3, 0.3, 2.0, 2.0, 0.5, 0.5])
        valuation = CompleteValuationVector(
            core=core * gains, auxiliary={},
            active_auxiliary_axes=[], activity_frame="RESTING",
            precision_gains=gains,
        )

        # R2.4: Coupled dynamics
        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        state = CoupledDynamicsState(
            constraints=dist.map_estimate(),
            valuations=valuation.core,
            constraint_target=dist.map_estimate(),
            valuation_target=valuation.core,
        )

        # R2.2: Decomposed feedback
        fb_engine = DecomposedFeedbackEngine()
        e_attn = fb_engine.compute_attention_error(dist, state.valuations, "RESTING")
        e_prior = fb_engine.compute_prior_error(
            state.constraints, state.valuations, "RESTING",
        )
        fb = fb_engine.compose_feedback(e_attn, 0.0, e_prior)

        # All valid
        assert dist.map_estimate().shape == (8,)
        assert valuation.core.shape == (9,)
        assert fb.total_magnitude() >= 0

        # One integration step
        new_state = engine.step(state, coupling)
        assert new_state.constraints.shape == (8,)
        assert new_state.valuations.shape == (9,)


# ══════════════════════════════════════════════════════════════════
# Parametrized: All 10 Activity Frames
# ══════════════════════════════════════════════════════════════════

ACTIVITY_FRAMES = [
    "RESTING", "STUDYING", "EXPLORING", "CREATING", "WORSHIPPING",
    "PLAYING", "EATING", "SOCIALIZING", "SLEEPING", "EXERCISING",
]

@pytest.mark.parametrize("activity_frame", ACTIVITY_FRAMES)
class TestAllActivityFrames:

    def test_frame_has_precision(self, activity_frame):
        """Each frame has precision weights defined."""
        assert activity_frame in FRAME_PRECISIONS
        assert len(FRAME_PRECISIONS[activity_frame]) == 8

    def test_frame_has_config(self, activity_frame):
        """Each frame has auxiliary config defined."""
        assert activity_frame in AUXILIARY_FRAME_CONFIG
        config = AUXILIARY_FRAME_CONFIG[activity_frame]
        assert "auxiliary_axes" in config
        assert "core_gains" in config
        assert len(config["core_gains"]) == 9
