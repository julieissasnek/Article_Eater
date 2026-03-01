"""
test_cva_engines.py — Tests for CVA Computation Engines (Phase 2)
==================================================================

Tests constraint engine, valuation engine, beauty readout,
and dynamics system.
"""

import math
import pytest

from src.models.cva_constraint import (
    Tier1ConstraintVector,
    Tier2ConstraintVector,
    CVAConstraintVector,
)
from src.models.cva_valuation import CVAValuationVector, CulturalVariant
from src.models.subject_characteristics import (
    SubjectCharacteristics,
    NeurotypeProfile,
    NeurotypeName,
    NEUROTYPE_PROFILES,
    CULTURAL_PRESETS,
)
from src.models.activity_frame import ActivityFrame, ActivityFrameType
from src.services.cva_constraint_engine import CVAConstraintEngine
from src.services.cva_valuation_engine import CVAValuationEngine
from src.services.cva_beauty import (
    LinearBeautyReadout,
    QuadraticBeautyReadout,
    NeuralBeautyReadout,
    RasaBeautyReadout,
    create_beauty_readout,
    BeautyModelType,
)
from src.services.cva_dynamics import (
    CVADynamics,
    DynamicsState,
    FeedbackSignal,
)


# ──────────────────────────────────────────────────────────────────
# Constraint Engine
# ──────────────────────────────────────────────────────────────────

class TestCVAConstraintEngine:
    SCENE = {
        "edge": 0.7, "motion": 0.4, "contrast": 0.6,
        "figure_ground": 0.5, "temporal_coherence": 0.8, "symmetry": 0.6,
    }

    def test_compute_typical_subject(self):
        engine = CVAConstraintEngine()
        result = engine.compute(self.SCENE)
        assert isinstance(result, CVAConstraintVector)
        assert len(result.as_full_vector()) == 14

    def test_tier2_values_in_range(self):
        engine = CVAConstraintEngine()
        result = engine.compute(self.SCENE)
        for v in result.tier2.as_vector():
            assert 0.0 <= v <= 1.0

    def test_ptsd_amplifies_prediction_error(self):
        engine = CVAConstraintEngine()
        typical = engine.compute(self.SCENE)

        ptsd_subject = SubjectCharacteristics(
            neurotype=NEUROTYPE_PROFILES["ptsd"],
        )
        ptsd_result = engine.compute(self.SCENE, ptsd_subject)

        assert ptsd_result.tier2.prediction_error >= typical.tier2.prediction_error

    def test_expert_reduces_processing_cost(self):
        engine = CVAConstraintEngine()

        novice = SubjectCharacteristics()
        novice.experience.mastery = 0.0
        c_novice = engine.compute(self.SCENE, novice)

        expert = SubjectCharacteristics()
        expert.experience.mastery = 1.0
        c_expert = engine.compute(self.SCENE, expert)

        assert c_expert.tier2.processing_cost <= c_novice.tier2.processing_cost

    def test_aging_reduces_tier1_contrast(self):
        engine = CVAConstraintEngine()

        young = SubjectCharacteristics()
        young.development.age = 25
        c_young = engine.compute(self.SCENE, young)

        older = SubjectCharacteristics()
        older.development.age = 75
        c_older = engine.compute(self.SCENE, older)

        assert c_older.tier1.contrast <= c_young.tier1.contrast


# ──────────────────────────────────────────────────────────────────
# Valuation Engine
# ──────────────────────────────────────────────────────────────────

class TestCVAValuationEngine:
    def _make_constraints(self):
        return CVAConstraintVector(
            tier2=Tier2ConstraintVector(
                processing_cost=0.3,
                prediction_error=0.5,
                control_efficacy=0.7,
                affordance_density=0.5,
                social_cue_density=0.4,
                multisensory_coherence=0.6,
                narrative_coherence=0.5,
            )
        )

    def test_western_produces_9d(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        v = engine.compute(c)
        assert v.variant == CulturalVariant.WESTERN
        assert v.dimensionality == 9

    def test_japanese_produces_amae(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        subject = SubjectCharacteristics(culture=CULTURAL_PRESETS["japanese"])
        v = engine.compute(c, subject)
        assert v.variant == CulturalVariant.JAPANESE
        assert "AmaeValue" in v.values

    def test_indian_produces_rasa_dharma(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        subject = SubjectCharacteristics(culture=CULTURAL_PRESETS["indian"])
        v = engine.compute(c, subject)
        assert v.variant == CulturalVariant.INDIAN
        assert "RasaValue" in v.values
        assert "DharmaValue" in v.values

    def test_values_in_range(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        v = engine.compute(c)
        for val in v.values.values():
            assert 0.0 <= val <= 1.0

    def test_neurotype_modulation(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        v_typical = engine.compute(c)

        ptsd = SubjectCharacteristics(neurotype=NEUROTYPE_PROFILES["ptsd"])
        v_ptsd = engine.compute(c, ptsd)

        # PTSD should amplify safety
        assert v_ptsd["SafetyValue"] >= v_typical["SafetyValue"]

    def test_frame_modulates_valuations(self):
        engine = CVAValuationEngine()
        c = self._make_constraints()
        frame_explore = ActivityFrame(frame_type=ActivityFrameType.EXPLORATORY)
        frame_emergency = ActivityFrame(frame_type=ActivityFrameType.EMERGENCY)

        v_explore = engine.compute(c, frame=frame_explore)
        v_emergency = engine.compute(c, frame=frame_emergency)

        # Emergency should weight safety more
        assert isinstance(v_emergency, CVAValuationVector)
        assert isinstance(v_explore, CVAValuationVector)


# ──────────────────────────────────────────────────────────────────
# Beauty Readout
# ──────────────────────────────────────────────────────────────────

class TestBeautyReadout:
    def _make_valuation(self):
        return CVAValuationVector(variant=CulturalVariant.WESTERN)

    def test_linear_returns_0_1(self):
        model = LinearBeautyReadout()
        v = self._make_valuation()
        b = model.compute(v)
        assert 0.0 <= b <= 1.0

    def test_quadratic_returns_0_1(self):
        model = QuadraticBeautyReadout()
        v = self._make_valuation()
        b = model.compute(v)
        assert 0.0 <= b <= 1.0

    def test_neural_returns_0_1(self):
        model = NeuralBeautyReadout()
        v = self._make_valuation()
        b = model.compute(v)
        assert 0.0 <= b <= 1.0

    def test_rasa_returns_0_1(self):
        model = RasaBeautyReadout()
        v = self._make_valuation()
        b = model.compute(v)
        assert 0.0 <= b <= 1.0

    def test_rasa_dominant(self):
        model = RasaBeautyReadout()
        v = self._make_valuation()
        dom = model.dominant_rasa(v)
        assert dom in model.rasa_configs

    def test_factory_all_models(self):
        for mtype in BeautyModelType:
            model = create_beauty_readout(mtype)
            v = self._make_valuation()
            b = model.compute(v)
            assert 0.0 <= b <= 1.0

    def test_high_interest_increases_beauty(self):
        model = LinearBeautyReadout()
        low = CVAValuationVector(values={"InterestValue": 0.1, "SafetyValue": 0.5})
        high = CVAValuationVector(values={"InterestValue": 0.9, "SafetyValue": 0.5})
        assert model.compute(high) > model.compute(low)


# ──────────────────────────────────────────────────────────────────
# Dynamics
# ──────────────────────────────────────────────────────────────────

class TestCVADynamics:
    def test_step_moves_toward_target(self):
        dyn = CVADynamics(alpha=2.0, beta=1.5, dt=0.01)
        state = DynamicsState(constraints=[0.3] * 8, valuations=[0.3] * 9)
        target_c = [0.7] * 8
        target_v = [0.7] * 9

        new_state = dyn.step(state, target_c, target_v)
        # Should move toward target
        assert new_state.constraints[0] > 0.3
        assert new_state.valuations[0] > 0.3

    def test_converges_after_simulation(self):
        dyn = CVADynamics(alpha=5.0, beta=3.0, dt=0.01)
        state = DynamicsState(constraints=[0.2] * 8, valuations=[0.2] * 9)
        target_c = [0.8] * 8
        target_v = [0.8] * 9

        trajectory = dyn.simulate(state, target_c, target_v, duration=2.0)
        final = trajectory[-1]

        assert dyn.has_converged(final, target_c, target_v, tolerance=0.05)

    def test_stability_check(self):
        dyn = CVADynamics(alpha=2.0, beta=1.5, dt=0.01)
        state = DynamicsState()
        target_c = [0.5] * 8
        target_v = [0.5] * 9

        is_stable, kappa = dyn.check_stability(state, target_c, target_v)
        assert is_stable
        assert kappa < 0.5

    def test_unstable_with_high_alpha(self):
        dyn = CVADynamics(alpha=100.0, beta=100.0, dt=0.1)
        state = DynamicsState()
        target_c = [0.5] * 8
        target_v = [0.5] * 9

        is_stable, kappa = dyn.check_stability(state, target_c, target_v)
        assert not is_stable  # κ = 100 × 0.1 = 10 > 0.5

    def test_feedback_signal(self):
        fb = FeedbackSignal(epsilon_attn=0.5, epsilon_prec=0.3, epsilon_prior=0.2)
        assert fb.total == pytest.approx(0.36, abs=0.01)

    def test_trajectory_length(self):
        dyn = CVADynamics(dt=0.01)
        state = DynamicsState()
        traj = dyn.simulate(state, [0.5]*8, [0.5]*9, duration=0.5)
        assert len(traj) == 51  # 50 steps + initial
