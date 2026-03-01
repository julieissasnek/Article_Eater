"""
test_cva_models.py — Tests for CVA Core Data Structures (Phase 1)
=================================================================

Tests constraint vectors, valuation vectors, subject characteristics,
and activity frames.
"""

import json
import math
import pytest

from src.models.cva_constraint import (
    Tier1ConstraintVector,
    Tier2ConstraintVector,
    CVAConstraintVector,
    ConstraintTheta,
    DEFAULT_TIER2_THETA,
    ConstraintTier,
    ConstraintName,
    Tier1Primitive,
)
from src.models.cva_valuation import (
    CVAValuationVector,
    CulturalVariant,
    NeurotypeValuationModifier,
    NEUROTYPE_MODIFIERS,
    ValuationName,
)
from src.models.subject_characteristics import (
    SubjectCharacteristics,
    NeurotypeProfile,
    NeurotypeName,
    CulturalContext,
    SelfConstrual,
    DevelopmentalStage,
    AcuteState,
    TraitProfile,
    NEUROTYPE_PROFILES,
    CULTURAL_PRESETS,
)
from src.models.activity_frame import (
    ActivityFrame,
    ActivityFrameType,
    PrecisionProfile,
    FRAME_PRECISION_PROFILES,
)


# ──────────────────────────────────────────────────────────────────
# Tier 1 Constraints
# ──────────────────────────────────────────────────────────────────

class TestTier1ConstraintVector:
    def test_default_values(self):
        t1 = Tier1ConstraintVector()
        assert all(v == 0.0 for v in t1.as_vector())

    def test_bounds_enforced(self):
        with pytest.raises(ValueError):
            Tier1ConstraintVector(edge=1.5)
        with pytest.raises(ValueError):
            Tier1ConstraintVector(contrast=-0.1)

    def test_as_vector_length(self):
        t1 = Tier1ConstraintVector(edge=0.5, motion=0.3)
        assert len(t1.as_vector()) == 6

    def test_aging_decline_no_effect_young(self):
        t1 = Tier1ConstraintVector(contrast=0.8, temporal_coherence=0.7)
        aged = t1.apply_aging_decline(25)
        assert aged.contrast == 0.8
        assert aged.temporal_coherence == 0.7

    def test_aging_decline_reduces_contrast(self):
        t1 = Tier1ConstraintVector(contrast=0.8, temporal_coherence=0.7)
        aged = t1.apply_aging_decline(70)
        assert aged.contrast < 0.8
        assert aged.temporal_coherence < 0.7


# ──────────────────────────────────────────────────────────────────
# Tier 2 Constraints
# ──────────────────────────────────────────────────────────────────

class TestTier2ConstraintVector:
    def test_default_values(self):
        t2 = Tier2ConstraintVector()
        assert all(v == 0.5 for v in t2.as_vector())

    def test_clamping(self):
        t2 = Tier2ConstraintVector(processing_cost=1.5, load_rate=-0.3)
        assert t2.processing_cost == 1.0
        assert t2.load_rate == 0.0

    def test_as_vector_length(self):
        assert len(Tier2ConstraintVector().as_vector()) == 8

    def test_distance(self):
        a = Tier2ConstraintVector(processing_cost=0.0)
        b = Tier2ConstraintVector(processing_cost=1.0)
        assert a.distance(b) > 0

    def test_getitem(self):
        t2 = Tier2ConstraintVector(narrative_coherence=0.8)
        assert t2["narrative_coherence"] == 0.8


# ──────────────────────────────────────────────────────────────────
# Combined Constraint Vector
# ──────────────────────────────────────────────────────────────────

class TestCVAConstraintVector:
    def test_full_vector_length(self):
        c = CVAConstraintVector()
        assert len(c.as_full_vector()) == 14  # 6 + 8

    def test_json_round_trip(self):
        c = CVAConstraintVector(
            tier1=Tier1ConstraintVector(edge=0.7, motion=0.3),
            tier2=Tier2ConstraintVector(processing_cost=0.8),
            scene_id="scene_001",
        )
        j = c.to_json()
        c2 = CVAConstraintVector.from_json(j)
        assert c2.tier1.edge == 0.7
        assert c2.tier2.processing_cost == 0.8
        assert c2.scene_id == "scene_001"


# ──────────────────────────────────────────────────────────────────
# Constraint Theta
# ──────────────────────────────────────────────────────────────────

class TestConstraintTheta:
    def test_apply_computes_weighted_sum(self):
        theta = ConstraintTheta(
            gain=2.0, bias=0.1,
            source_weights={"edge": 0.5, "motion": 0.5},
        )
        result = theta.apply({"edge": 0.4, "motion": 0.6})
        # 2.0 * (0.5*0.4 + 0.5*0.6) + 0.1 = 2.0*0.5 + 0.1 = 1.1 → clamped to 1.0
        assert result == 1.0  # clamped

    def test_default_theta_all_constraints(self):
        assert len(DEFAULT_TIER2_THETA) == 8


# ──────────────────────────────────────────────────────────────────
# Valuations
# ──────────────────────────────────────────────────────────────────

class TestCVAValuationVector:
    def test_western_has_9_dimensions(self):
        v = CVAValuationVector(variant=CulturalVariant.WESTERN)
        assert v.dimensionality == 9

    def test_japanese_has_10_dimensions(self):
        v = CVAValuationVector(variant=CulturalVariant.JAPANESE)
        assert v.dimensionality == 10
        assert "AmaeValue" in v.values
        assert "MaValue" in v.values

    def test_west_african_has_6_dimensions(self):
        v = CVAValuationVector(variant=CulturalVariant.WEST_AFRICAN)
        assert v.dimensionality == 6
        assert "ÀṣàValue" in v.values

    def test_indian_has_4_dimensions(self):
        v = CVAValuationVector(variant=CulturalVariant.INDIAN)
        assert v.dimensionality == 4
        assert "RasaValue" in v.values
        assert "DharmaValue" in v.values

    def test_clamping(self):
        v = CVAValuationVector(values={"SafetyValue": 1.5, "InterestValue": -0.3})
        assert v.values["SafetyValue"] == 1.0
        assert v.values["InterestValue"] == 0.0

    def test_json_round_trip(self):
        v = CVAValuationVector(
            variant=CulturalVariant.JAPANESE,
            subject_id="subj_001",
        )
        v["AmaeValue"] = 0.8
        j = v.to_json()
        v2 = CVAValuationVector.from_json(j)
        assert v2.variant == CulturalVariant.JAPANESE
        assert v2["AmaeValue"] == 0.8

    def test_dominant_valuation(self):
        v = CVAValuationVector(values={
            "SafetyValue": 0.9,
            "InterestValue": 0.3,
        })
        assert v.dominant_valuation() == "SafetyValue"


class TestNeurotypeModifiers:
    def test_ptsd_amplifies_safety(self):
        v = CVAValuationVector(variant=CulturalVariant.WESTERN)
        mod = NEUROTYPE_MODIFIERS["ptsd"]
        v_mod = mod.apply(v)
        assert v_mod["SafetyValue"] > v["SafetyValue"]

    def test_adhd_amplifies_interest(self):
        v = CVAValuationVector(variant=CulturalVariant.WESTERN)
        mod = NEUROTYPE_MODIFIERS["adhd"]
        v_mod = mod.apply(v)
        # Interest is capped at 1.0, but should be higher than original
        assert v_mod["InterestValue"] >= v["InterestValue"]

    def test_all_10_neurotypes_present(self):
        assert len(NEUROTYPE_MODIFIERS) == 10


# ──────────────────────────────────────────────────────────────────
# Subject Characteristics
# ──────────────────────────────────────────────────────────────────

class TestSubjectCharacteristics:
    def test_default_typical(self):
        s = SubjectCharacteristics()
        assert s.neurotype.name == NeurotypeName.TYPICAL

    def test_precision_computation(self):
        s = SubjectCharacteristics()
        p = s.compute_precision()
        # β₀(1.5) × state(1.0) × neuro(1.0) × trait(1.5) = 2.25
        assert p == pytest.approx(2.25, abs=0.01)

    def test_precision_reduced_by_fatigue(self):
        s = SubjectCharacteristics()
        s.state.fatigue = 0.5
        p_fatigued = s.compute_precision()
        s.state.fatigue = 0.0
        p_rested = s.compute_precision()
        assert p_fatigued < p_rested

    def test_precision_reduced_by_adhd(self):
        typical = SubjectCharacteristics()
        adhd = SubjectCharacteristics()
        adhd.neurotype = NEUROTYPE_PROFILES["adhd"]
        assert adhd.compute_precision() < typical.compute_precision()

    def test_json_round_trip(self):
        s = SubjectCharacteristics(
            subject_id="test_001",
            culture=CULTURAL_PRESETS["japanese"],
            neurotype=NEUROTYPE_PROFILES["asd"],
        )
        j = s.to_json()
        s2 = SubjectCharacteristics.from_json(j)
        assert s2.subject_id == "test_001"
        assert s2.culture.kappa_self == SelfConstrual.INTERDEPENDENT
        assert s2.neurotype.name == NeurotypeName.ASD

    def test_all_13_neurotype_profiles(self):
        assert len(NEUROTYPE_PROFILES) == 13

    def test_all_4_cultural_presets(self):
        assert len(CULTURAL_PRESETS) == 4


# ──────────────────────────────────────────────────────────────────
# Activity Frame
# ──────────────────────────────────────────────────────────────────

class TestActivityFrame:
    def test_default_frame(self):
        f = ActivityFrame()
        assert f.frame_type == ActivityFrameType.EXPLORATORY

    def test_10_frame_types(self):
        assert len(ActivityFrameType) == 10

    def test_each_frame_has_precision_profile(self):
        for ft in ActivityFrameType:
            assert ft in FRAME_PRECISION_PROFILES

    def test_emergency_has_max_safety_precision(self):
        p = FRAME_PRECISION_PROFILES[ActivityFrameType.EMERGENCY]
        assert p.safety == 1.0
        assert p.global_precision >= 2.0

    def test_effective_precision(self):
        f = ActivityFrame(frame_type=ActivityFrameType.GOAL_DIRECTED)
        # Frame precision = 1.8, subject precision = 2.0
        eff = f.get_effective_precision(2.0)
        assert eff == pytest.approx(3.6, abs=0.01)

    def test_json_round_trip(self):
        f = ActivityFrame(
            frame_type=ActivityFrameType.CREATIVE,
            duration_minutes=45.0,
            description="Design session",
        )
        j = f.to_json()
        f2 = ActivityFrame.from_json(j)
        assert f2.frame_type == ActivityFrameType.CREATIVE
        assert f2.duration_minutes == 45.0
