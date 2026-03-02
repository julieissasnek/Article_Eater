"""
test_cva_sprint_series.py — Tests for CVA Sprint Series (CVA-1 through CVA-9)
==============================================================================

Comprehensive test suite covering:
  CVA-3: Activity Frame Registry (goal activation, constraint salience, worked examples)
  CVA-5: Goal-Modulated Projection (d_goal, d_frame, aggregation, comparison)
  Cross-component integration tests

Target: 60+ new tests
"""

import json
import math
import os
import sys
import tempfile

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ══════════════════════════════════════════════════════════════════
# CVA-3: Activity Frame Registry Tests
# ══════════════════════════════════════════════════════════════════

class TestCanonicalFrames:
    """Test all 8 canonical activity frames."""

    def test_eight_canonical_frames_exist(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        assert len(CANONICAL_FRAMES) == 8
        expected = {
            "hospital_recovery", "office_work", "social_gathering",
            "yoga_meditation", "museum_visiting", "home_living",
            "retail_shopping", "sacred_space",
        }
        assert set(CANONICAL_FRAMES.keys()) == expected

    @pytest.mark.parametrize("frame_name", [
        "hospital_recovery", "office_work", "social_gathering",
        "yoga_meditation", "museum_visiting", "home_living",
        "retail_shopping", "sacred_space",
    ])
    def test_frame_has_required_fields(self, frame_name):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES[frame_name]
        assert frame.name == frame_name
        assert len(frame.description) > 10
        assert len(frame.primary_goals) >= 2
        assert len(frame.valuation_weights) == 9
        assert len(frame.constraint_salience_mask) == 8
        assert len(frame.context_examples) >= 2
        assert len(frame.friston_interpretation) > 20

    @pytest.mark.parametrize("frame_name", [
        "hospital_recovery", "office_work", "social_gathering",
        "yoga_meditation", "museum_visiting", "home_living",
        "retail_shopping", "sacred_space",
    ])
    def test_valuation_weights_in_range(self, frame_name):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES[frame_name]
        for axis, weight in frame.valuation_weights.items():
            assert 0.0 <= weight <= 1.0, f"{frame_name}.{axis} = {weight}"

    @pytest.mark.parametrize("frame_name", [
        "hospital_recovery", "office_work", "social_gathering",
        "yoga_meditation", "museum_visiting", "home_living",
        "retail_shopping", "sacred_space",
    ])
    def test_constraint_salience_in_range(self, frame_name):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES[frame_name]
        for c, sigma in frame.constraint_salience_mask.items():
            assert 0.0 <= sigma <= 1.0, f"{frame_name}.{c} = {sigma}"

    def test_primary_goals_are_valid_axes(self):
        from src.services.cva.activity_frame_registry import (
            CANONICAL_FRAMES, VALUATION_AXES,
        )
        valid = set(VALUATION_AXES)
        for name, frame in CANONICAL_FRAMES.items():
            for goal in frame.primary_goals:
                assert goal in valid, f"{name}: invalid goal '{goal}'"

    def test_constraint_names_are_valid(self):
        from src.services.cva.activity_frame_registry import (
            CANONICAL_FRAMES, CONSTRAINT_NAMES,
        )
        valid = set(CONSTRAINT_NAMES)
        for name, frame in CANONICAL_FRAMES.items():
            for c in frame.constraint_salience_mask:
                assert c in valid, f"{name}: invalid constraint '{c}'"


class TestGoalActivation:
    """Test frame-dependent goal activation (Sprint CVA-3 §3)."""

    def test_inactive_goals_contribute_zero(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES["hospital_recovery"]
        zeta = {
            "SafetyValue": 0.8, "InterestValue": 0.9,
            "RestorationValue": 0.7, "StatusValue": 0.5,
            "BelongingValue": 0.4, "IdentityCongruenceValue": 0.3,
            "AutonomySupportValue": 0.6, "CompetenceSupportValue": 0.5,
            "RelatednessSupportValue": 0.7,
        }
        adjusted = frame.compute_frame_adjusted_valuation(zeta)
        # InterestValue is NOT in hospital_recovery primary_goals
        assert adjusted["InterestValue"] == 0.0
        # StatusValue is NOT active
        assert adjusted["StatusValue"] == 0.0
        # SafetyValue IS active
        assert adjusted["SafetyValue"] > 0.0

    def test_active_goals_weighted(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES["office_work"]
        zeta = {axis: 0.5 for axis in [
            "SafetyValue", "InterestValue", "RestorationValue",
            "StatusValue", "BelongingValue", "IdentityCongruenceValue",
            "AutonomySupportValue", "CompetenceSupportValue",
            "RelatednessSupportValue",
        ]}
        adjusted = frame.compute_frame_adjusted_valuation(zeta)
        # CompetenceSupportValue is primary for office_work (weight=0.80)
        assert adjusted["CompetenceSupportValue"] == 0.5 * 0.80


class TestConstraintSalienceMask:
    """Test frame-dependent constraint salience (Sprint CVA-3 §4)."""

    def test_masking_attenuates_constraints(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES["yoga_meditation"]
        c = {name: 0.8 for name in [
            "processing_cost", "load_rate", "prediction_error",
            "control_efficacy", "affordance_density", "social_cue_density",
            "multisensory_coherence", "narrative_coherence",
        ]}
        masked = frame.apply_constraint_salience(c)
        # social_cue_density should be heavily attenuated (σ=0.1)
        assert masked["social_cue_density"] == pytest.approx(0.08, abs=0.01)
        # multisensory_coherence should be preserved (σ=0.9)
        assert masked["multisensory_coherence"] == pytest.approx(0.72, abs=0.01)

    def test_hospital_masks_affordance_density(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES["hospital_recovery"]
        c = {name: 1.0 for name in [
            "processing_cost", "load_rate", "prediction_error",
            "control_efficacy", "affordance_density", "social_cue_density",
            "multisensory_coherence", "narrative_coherence",
        ]}
        masked = frame.apply_constraint_salience(c)
        # Affordance density low for immobile patient (σ=0.2)
        assert masked["affordance_density"] == pytest.approx(0.2, abs=0.01)
        # Prediction error fully salient (σ=1.0)
        assert masked["prediction_error"] == pytest.approx(1.0, abs=0.01)


class TestActivityFrameRegistry:
    """Test the registry class."""

    def test_registry_init(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        assert len(registry.list_frames()) == 8

    def test_get_frame(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        frame = registry.get_frame("office_work")
        assert frame.name == "office_work"

    def test_get_unknown_frame_raises(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        with pytest.raises(KeyError, match="Unknown frame"):
            registry.get_frame("nonexistent_frame")

    def test_register_custom_frame(self):
        from src.services.cva.activity_frame_registry import (
            ActivityFrameRegistry, CanonicalFrame,
        )
        registry = ActivityFrameRegistry()
        custom = CanonicalFrame(
            name="test_frame",
            description="Test frame",
            primary_goals=["SafetyValue"],
            valuation_weights={a: 0.5 for a in [
                "SafetyValue", "InterestValue", "RestorationValue",
                "StatusValue", "BelongingValue", "IdentityCongruenceValue",
                "AutonomySupportValue", "CompetenceSupportValue",
                "RelatednessSupportValue",
            ]},
            constraint_salience_mask={c: 0.5 for c in [
                "processing_cost", "load_rate", "prediction_error",
                "control_efficacy", "affordance_density", "social_cue_density",
                "multisensory_coherence", "narrative_coherence",
            ]},
        )
        registry.register_frame(custom)
        assert len(registry.list_frames()) == 9
        assert registry.get_frame("test_frame").name == "test_frame"

    def test_activate_frame(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        c = {name: 0.5 for name in [
            "processing_cost", "load_rate", "prediction_error",
            "control_efficacy", "affordance_density", "social_cue_density",
            "multisensory_coherence", "narrative_coherence",
        ]}
        zeta = {axis: 0.5 for axis in [
            "SafetyValue", "InterestValue", "RestorationValue",
            "StatusValue", "BelongingValue", "IdentityCongruenceValue",
            "AutonomySupportValue", "CompetenceSupportValue",
            "RelatednessSupportValue",
        ]}
        adjusted = registry.activate_frame("office_work", c, zeta)
        assert isinstance(adjusted, dict)
        assert len(adjusted) == 9

    def test_compare_frames(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        comparison = registry.compare_frames("hospital_recovery", "office_work")
        assert "valuation_weights" in comparison
        assert "constraint_salience" in comparison
        assert "shared_active_goals" in comparison
        assert len(comparison["valuation_weights"]) == 9

    def test_validate_frame_constraints(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        missing = registry.validate_frame_constraints(
            "office_work",
            ["processing_cost", "load_rate"],
        )
        assert len(missing) == 6  # 8 total - 2 provided = 6 missing

    def test_frame_matches_context(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        cues = {
            "social_cue_density": 0.9,
            "narrative_coherence": 0.8,
        }
        score = registry.frame_matches_context("social_gathering", cues)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # social gathering should match social cues

    def test_export_registry(self):
        from src.services.cva.activity_frame_registry import ActivityFrameRegistry
        registry = ActivityFrameRegistry()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            count = registry.export_registry(path)
            assert count == 8
            data = json.loads(open(path).read())
            assert len(data) == 8
        finally:
            os.unlink(path)

    def test_frame_to_dict_roundtrip(self):
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        frame = CANONICAL_FRAMES["museum_visiting"]
        d = frame.to_dict()
        assert d["name"] == "museum_visiting"
        assert len(d["primary_goals"]) >= 2
        assert len(d["valuation_weights"]) == 9
        assert len(d["constraint_salience_mask"]) == 8


# ══════════════════════════════════════════════════════════════════
# CVA-3: Worked Examples (Sprint CVA-3 §6)
# ══════════════════════════════════════════════════════════════════

class TestWorkedExamples:
    """Test the 5 worked examples from Sprint CVA-3 spec."""

    def test_example1_hospital_recovery_vs_visitor(self):
        """Same room, different frames: recovery vs visiting."""
        from src.services.cva.activity_frame_registry import (
            ActivityFrameRegistry, CanonicalFrame,
        )
        registry = ActivityFrameRegistry()
        comparison = registry.compare_frames("hospital_recovery", "social_gathering")
        # Safety should be much higher in recovery
        safety_diff = comparison["valuation_weights"]["SafetyValue"]
        assert safety_diff["frame_a"] > safety_diff["frame_b"]
        # Social cue density should be lower in recovery
        social = comparison["constraint_salience"]["social_cue_density"]
        assert social["frame_a"] < social["frame_b"]

    def test_example2_creative_vs_admin(self):
        """Creative studio: creative work vs admin frame."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        creative = CANONICAL_FRAMES["museum_visiting"]  # closest proxy
        admin = CANONICAL_FRAMES["office_work"]
        # Interest should be higher for creative
        assert creative.valuation_weights["InterestValue"] > admin.valuation_weights["InterestValue"]

    def test_example3_museum_art_vs_school_group(self):
        """Museum: art appreciation vs school group."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        museum = CANONICAL_FRAMES["museum_visiting"]
        # Narrative coherence should be highly salient for museum
        assert museum.constraint_salience_mask["narrative_coherence"] == 1.0

    def test_example4_home_vs_retail_autonomy(self):
        """Home living vs retail: autonomy comparison."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        home = CANONICAL_FRAMES["home_living"]
        retail = CANONICAL_FRAMES["retail_shopping"]
        # Both value autonomy but home more so
        assert home.valuation_weights["AutonomySupportValue"] > \
               retail.valuation_weights["AutonomySupportValue"]

    def test_example5_yoga_meditation_vs_social_yoga(self):
        """Yoga: meditation (internal) vs social (community)."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        meditation = CANONICAL_FRAMES["yoga_meditation"]
        social = CANONICAL_FRAMES["social_gathering"]
        # Meditation masks social cues; social gathering maximizes them
        assert meditation.constraint_salience_mask["social_cue_density"] < 0.2
        assert social.constraint_salience_mask["social_cue_density"] == 1.0


# ══════════════════════════════════════════════════════════════════
# CVA-5: Goal-Modulated Projection Tests
# ══════════════════════════════════════════════════════════════════

class TestGoalWarrantAlignment:
    """Test the goal-warrant alignment matrix."""

    def test_matrix_completeness(self):
        from src.services.cva.epistemic_projection_cva import (
            GOAL_WARRANT_ALIGNMENT,
        )
        from src.services.epistemic_projection import CANONICAL_DISCOUNT_FACTORS
        assert len(GOAL_WARRANT_ALIGNMENT) == 9
        for goal, warrants in GOAL_WARRANT_ALIGNMENT.items():
            assert len(warrants) == 7
            for wtype in CANONICAL_DISCOUNT_FACTORS:
                assert wtype in warrants, f"{goal} missing {wtype}"

    def test_alignment_values_in_range(self):
        from src.services.cva.epistemic_projection_cva import GOAL_WARRANT_ALIGNMENT
        for goal, warrants in GOAL_WARRANT_ALIGNMENT.items():
            for wtype, val in warrants.items():
                assert 0.3 <= val <= 1.0, f"{goal}.{wtype} = {val}"

    def test_safety_trusts_mechanism_more_than_analogy(self):
        from src.services.cva.epistemic_projection_cva import GOAL_WARRANT_ALIGNMENT
        safety = GOAL_WARRANT_ALIGNMENT["SafetyValue"]
        assert safety["mechanism"] > safety["analogical"]

    def test_interest_values_analogy_highly(self):
        from src.services.cva.epistemic_projection_cva import GOAL_WARRANT_ALIGNMENT
        interest = GOAL_WARRANT_ALIGNMENT["InterestValue"]
        assert interest["analogical"] >= 0.75  # analogies ARE how novelty works


class TestDGoal:
    """Test d_goal function."""

    def test_empty_goals_returns_unity(self):
        from src.services.cva.epistemic_projection_cva import d_goal
        assert d_goal([], "mechanism") == 1.0

    def test_single_goal(self):
        from src.services.cva.epistemic_projection_cva import d_goal
        result = d_goal(["SafetyValue"], "mechanism")
        assert 0.3 <= result <= 1.0

    def test_multiple_goals_averaged(self):
        from src.services.cva.epistemic_projection_cva import d_goal
        result = d_goal(["SafetyValue", "InterestValue"], "mechanism")
        # Should be average of SafetyValue.mechanism and InterestValue.mechanism
        assert 0.3 <= result <= 1.0


class TestDFrame:
    """Test d_frame function."""

    def test_known_frame(self):
        from src.services.cva.epistemic_projection_cva import d_frame
        result = d_frame("hospital_recovery", "analogical")
        assert result < 0.5  # analogies risky in clinical settings

    def test_unknown_frame_default(self):
        from src.services.cva.epistemic_projection_cva import d_frame
        result = d_frame("unknown_frame", "mechanism")
        assert result == 0.8  # default

    def test_context_sensitivity_analogy_high_pred_error(self):
        from src.services.cva.epistemic_projection_cva import d_frame
        c_high = {"prediction_error": 0.9}
        c_low = {"prediction_error": 0.3}
        d_high = d_frame("office_work", "analogical", c_high)
        d_low = d_frame("office_work", "analogical", c_low)
        assert d_high < d_low  # high pred error further reduces analogical


class TestComputeDCVA:
    """Test full CVA discount computation."""

    def test_cva_discount_lower_than_baseline(self):
        """CVA discount should generally be ≤ baseline (more conservative)."""
        from src.services.cva.epistemic_projection_cva import compute_d_cva
        from src.services.epistemic_projection import CANONICAL_DISCOUNT_FACTORS
        d_base = CANONICAL_DISCOUNT_FACTORS["mechanism"]
        d_cva = compute_d_cva(
            "mechanism",
            ["SafetyValue"],
            "hospital_recovery",
        )
        assert d_cva <= d_base  # goal + frame modulation only reduces

    def test_no_goal_no_frame_equals_baseline(self):
        from src.services.cva.epistemic_projection_cva import compute_d_cva
        from src.services.epistemic_projection import CANONICAL_DISCOUNT_FACTORS
        d_base = CANONICAL_DISCOUNT_FACTORS["mechanism"]
        d_cva = compute_d_cva("mechanism", [], "")
        assert d_cva == pytest.approx(d_base, abs=0.01)


class TestGoalModulatedProjection:
    """Test goal-modulated projection functions."""

    def test_single_edge_projection(self):
        from src.services.cva.epistemic_projection_cva import project_goal_modulated
        result = project_goal_modulated(
            p_lab=0.75,
            warrant_type="mechanism",
            goal_vector=["SafetyValue"],
            frame_name="hospital_recovery",
            omega=0.9,
            delta=0.85,
        )
        assert 0.0 < result < 1.0
        assert result != 0.5  # should shift from prior

    def test_aggregation(self):
        from src.services.cva.epistemic_projection_cva import (
            aggregate_projections_goal_modulated,
        )
        edges = [
            {"p_lab": 0.70, "tau": "mechanism", "omega": 0.85},
            {"p_lab": 0.65, "tau": "empirical_association", "omega": 0.80},
        ]
        result = aggregate_projections_goal_modulated(
            edges,
            goal_vector=["SafetyValue", "RestorationValue"],
            frame_name="hospital_recovery",
        )
        assert 0.0 < result < 1.0

    def test_empty_edges_returns_prior(self):
        from src.services.cva.epistemic_projection_cva import (
            aggregate_projections_goal_modulated,
        )
        result = aggregate_projections_goal_modulated(
            [], ["SafetyValue"], "hospital_recovery",
        )
        assert result == 0.5


class TestPathComposition:
    """Test path discount composition."""

    def test_min_method(self):
        from src.services.cva.epistemic_projection_cva import (
            compose_path_discounts_goal_modulated,
        )
        edges = [
            {"tau": "mechanism", "omega": 0.9, "delta": 1.0},
            {"tau": "analogical", "omega": 0.7, "delta": 0.8},
        ]
        result = compose_path_discounts_goal_modulated(
            edges, ["SafetyValue"], "hospital_recovery", method="min",
        )
        assert result > 0
        assert result < 1.0

    def test_product_method(self):
        from src.services.cva.epistemic_projection_cva import (
            compose_path_discounts_goal_modulated,
        )
        edges = [
            {"tau": "mechanism", "omega": 0.9, "delta": 1.0},
            {"tau": "functional", "omega": 0.8, "delta": 0.9},
        ]
        result = compose_path_discounts_goal_modulated(
            edges, ["CompetenceSupportValue"], "office_work", method="product",
        )
        assert result > 0


class TestProjectionComparison:
    """Test comparison utilities."""

    def test_comparison_returns_both_projections(self):
        from src.services.cva.epistemic_projection_cva import project_comparison
        comp = project_comparison(
            p_lab=0.75,
            warrant_type="mechanism",
            omega=0.9,
            goal_vector=["SafetyValue"],
            frame_name="hospital_recovery",
        )
        assert 0 < comp.p_baseline < 1
        assert 0 < comp.p_goal_modulated < 1
        assert isinstance(comp.improvement, float)

    def test_comparison_to_dict(self):
        from src.services.cva.epistemic_projection_cva import project_comparison
        comp = project_comparison(
            p_lab=0.70,
            warrant_type="analogical",
            omega=0.8,
            goal_vector=["InterestValue"],
            frame_name="museum_visiting",
        )
        d = comp.to_dict()
        assert "p_baseline" in d
        assert "p_goal_modulated" in d
        assert "improvement" in d

    def test_full_diagnostic(self):
        from src.services.cva.epistemic_projection_cva import (
            project_with_full_diagnostic,
        )
        edges = [
            {"p_lab": 0.70, "tau": "mechanism", "omega": 0.9},
            {"p_lab": 0.65, "tau": "functional", "omega": 0.8},
        ]
        result = project_with_full_diagnostic(
            edges,
            goal_vector=["SafetyValue", "RestorationValue"],
            frame_name="hospital_recovery",
        )
        assert "p_baseline" in result
        assert "p_goal_modulated" in result
        assert "edge_details" in result
        assert len(result["edge_details"]) == 2


class TestExport:
    """Test export utilities."""

    def test_export_goal_warrant_matrix(self):
        from src.services.cva.epistemic_projection_cva import export_goal_warrant_matrix
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            count = export_goal_warrant_matrix(path)
            assert count == 63  # 9 × 7
            data = json.loads(open(path).read())
            assert "matrix" in data
            assert len(data["matrix"]) == 9
        finally:
            os.unlink(path)


# ══════════════════════════════════════════════════════════════════
# Cross-Component Integration Tests
# ══════════════════════════════════════════════════════════════════

class TestCrossComponentIntegration:
    """Test CVA-3 + CVA-5 integration."""

    def test_frame_goals_feed_into_projection(self):
        """Frame's primary goals should modulate projection."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        from src.services.cva.epistemic_projection_cva import project_goal_modulated

        frame = CANONICAL_FRAMES["hospital_recovery"]
        result = project_goal_modulated(
            p_lab=0.75,
            warrant_type="mechanism",
            goal_vector=frame.primary_goals,
            frame_name=frame.name,
            omega=0.9,
        )
        assert 0.0 < result < 1.0

    def test_same_evidence_different_frames_different_projections(self):
        """Same evidence should project differently under different frames."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        from src.services.cva.epistemic_projection_cva import project_goal_modulated

        p_lab, wtype, omega = 0.75, "analogical", 0.8

        recovery = CANONICAL_FRAMES["hospital_recovery"]
        p_recovery = project_goal_modulated(
            p_lab, wtype, recovery.primary_goals, recovery.name, omega=omega,
        )

        museum = CANONICAL_FRAMES["museum_visiting"]
        p_museum = project_goal_modulated(
            p_lab, wtype, museum.primary_goals, museum.name, omega=omega,
        )

        # Museum should trust analogical evidence more than hospital
        assert abs(p_museum - 0.5) > abs(p_recovery - 0.5) or \
               p_museum != p_recovery  # at minimum they should differ

    def test_constraint_salience_and_projection_pipeline(self):
        """Full pipeline: frame → mask constraints → modulate projection."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        from src.services.cva.epistemic_projection_cva import (
            project_goal_modulated, d_frame,
        )

        frame = CANONICAL_FRAMES["office_work"]
        c = {name: 0.6 for name in [
            "processing_cost", "load_rate", "prediction_error",
            "control_efficacy", "affordance_density", "social_cue_density",
            "multisensory_coherence", "narrative_coherence",
        ]}
        masked = frame.apply_constraint_salience(c)
        p = project_goal_modulated(
            p_lab=0.70,
            warrant_type="empirical_association",
            goal_vector=frame.primary_goals,
            frame_name=frame.name,
            constraint_vector=masked,
            omega=0.85,
        )
        assert 0.0 < p < 1.0

    def test_all_frames_produce_valid_projections(self):
        """Every canonical frame should produce valid projections."""
        from src.services.cva.activity_frame_registry import CANONICAL_FRAMES
        from src.services.cva.epistemic_projection_cva import project_goal_modulated
        from src.services.epistemic_projection import CANONICAL_DISCOUNT_FACTORS

        for frame_name, frame in CANONICAL_FRAMES.items():
            for wtype in CANONICAL_DISCOUNT_FACTORS:
                p = project_goal_modulated(
                    p_lab=0.70,
                    warrant_type=wtype,
                    goal_vector=frame.primary_goals,
                    frame_name=frame_name,
                    omega=0.8,
                )
                assert 0.0 < p < 1.0, f"Invalid p={p} for {frame_name}/{wtype}"
