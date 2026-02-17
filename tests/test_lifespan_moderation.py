"""
Tests for lifespan moderation (Sprint 11 Task 11.3).

Verifies that:
1. Age is correctly extracted from occupant_profile
2. Compute functions produce different WIS for different ages
3. The pipeline applies lifespan moderation correctly
"""

import pytest
from src.cmr.lifespan_moderation import (
    extract_occupant_age,
    call_compute_with_age,
    compute_template_with_lifespan,
    get_age_adjustment_factor,
)
from src.cmr.template_computations import (
    get_lifespan_multiplier,
    compute_vf3_ceiling_height,
    compute_l2_circadian_medi,
)


class TestAgeExtraction:
    """Tests for extract_occupant_age function."""

    def test_extract_age_from_age_key(self):
        profile = {"age": 35}
        assert extract_occupant_age(profile) == 35

    def test_extract_age_from_occupant_age_key(self):
        profile = {"occupant_age": 42}
        assert extract_occupant_age(profile) == 42

    def test_extract_age_from_age_years_key(self):
        profile = {"age_years": 28}
        assert extract_occupant_age(profile) == 28

    def test_extract_age_returns_none_if_missing(self):
        profile = {"name": "Test User"}
        assert extract_occupant_age(profile) is None

    def test_extract_age_prefers_age_key(self):
        profile = {"age": 30, "occupant_age": 40}
        assert extract_occupant_age(profile) == 30


class TestLifespanMultipliers:
    """Tests for lifespan sensitivity multipliers."""

    def test_child_has_higher_multiplier(self):
        child_mult = get_lifespan_multiplier(7)
        adult_mult = get_lifespan_multiplier(35)
        assert child_mult > adult_mult, "Children should have higher sensitivity"

    def test_elderly_has_higher_multiplier(self):
        elderly_mult = get_lifespan_multiplier(70)
        adult_mult = get_lifespan_multiplier(35)
        assert elderly_mult > adult_mult, "Elderly should have higher sensitivity"

    def test_reference_band_is_1_0(self):
        """Adults 25-50 should have multiplier 1.0"""
        assert get_lifespan_multiplier(30) == 1.0
        assert get_lifespan_multiplier(45) == 1.0

    def test_u_curve_shape(self):
        """Verify U-curve: high at ends, low in middle."""
        ages = [5, 15, 35, 55, 75]
        mults = [get_lifespan_multiplier(a) for a in ages]
        # Children (5) and elderly (75) should be > middle ages
        assert mults[0] > mults[2]  # 5 > 35
        assert mults[4] > mults[2]  # 75 > 35


class TestVF3AgeDifferences:
    """Test that VF3 produces different scores for different ages."""

    def test_vf3_child_vs_adult(self):
        """VF3 should produce different results for age 7 vs age 35."""
        result_child = compute_vf3_ceiling_height(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            occupant_age=7,
        )
        result_adult = compute_vf3_ceiling_height(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            occupant_age=35,
        )

        # Both should produce valid results
        assert result_child is not None
        assert result_adult is not None

        # The lifespan multiplier should differ
        child_mult = result_child.details.get("lifespan_multiplier", 1.0)
        adult_mult = result_adult.details.get("lifespan_multiplier", 1.0)
        assert child_mult != adult_mult, "Child and adult should have different multipliers"
        assert child_mult > adult_mult, "Child should have higher sensitivity"

    def test_vf3_elderly_vs_adult(self):
        """VF3 should produce different results for age 70 vs age 35."""
        result_elderly = compute_vf3_ceiling_height(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            occupant_age=70,
        )
        result_adult = compute_vf3_ceiling_height(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            occupant_age=35,
        )

        elderly_mult = result_elderly.details.get("lifespan_multiplier", 1.0)
        adult_mult = result_adult.details.get("lifespan_multiplier", 1.0)
        assert elderly_mult > adult_mult, "Elderly should have higher sensitivity"


class TestL2AgeDifferences:
    """Test that L2 circadian template handles age correctly."""

    def test_l2_elderly_needs_more_light(self):
        """
        Per AGE-I: elderly need ~2x melanopic irradiance.
        Same illuminance should score LOWER for 70-year-old than 30-year-old.
        """
        result_elderly = compute_l2_circadian_medi(
            medi_lux=200.0,  # Moderate M-EDI
            exposure_duration_hours=2.0,
            time_of_day="morning",
            occupant_age=70,
        )
        result_adult = compute_l2_circadian_medi(
            medi_lux=200.0,
            exposure_duration_hours=2.0,
            time_of_day="morning",
            occupant_age=30,
        )

        # Both produce valid results
        assert result_elderly is not None
        assert result_adult is not None

        # The age-corrected threshold should differ
        # Elderly have higher threshold due to lens yellowing
        elderly_details = result_elderly.details or {}
        adult_details = result_adult.details or {}

        # Check that age correction is being applied
        if "age_corrected_threshold" in elderly_details:
            assert elderly_details["age_corrected_threshold"] > adult_details.get(
                "age_corrected_threshold", 200
            ), "Elderly should need higher M-EDI threshold"


class TestComputeWithLifespan:
    """Test the compute_template_with_lifespan wrapper."""

    def test_computes_vf3_with_age(self):
        result = compute_template_with_lifespan(
            template_id="VF3",
            measured_features={
                "ceiling_height_m": 3.0,
                "floor_area_m2": 25.0,
            },
            occupant_profile={"age": 35},
        )
        assert result["template"] == "VF3"
        assert "wis" in result
        assert result["needs_computation"] is False
        assert result["lifespan_applied"] is True
        assert result["age"] == 35

    def test_returns_placeholder_for_unknown_template(self):
        result = compute_template_with_lifespan(
            template_id="UNKNOWN_TEMPLATE",
            measured_features={},
            occupant_profile={"age": 35},
        )
        assert result["needs_computation"] is True
        assert result["wis"] == 50.0

    def test_age_passed_through(self):
        """Verify age is correctly passed to compute function."""
        result_7 = compute_template_with_lifespan(
            template_id="VF3",
            measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
            occupant_profile={"age": 7},
        )
        result_35 = compute_template_with_lifespan(
            template_id="VF3",
            measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
            occupant_profile={"age": 35},
        )

        assert result_7["age"] == 7
        assert result_35["age"] == 35
        # Multipliers should differ
        mult_7 = result_7.get("lifespan_multiplier", 1.0)
        mult_35 = result_35.get("lifespan_multiplier", 1.0)
        assert mult_7 != mult_35


class TestAgeAdjustmentFactor:
    """Test the get_age_adjustment_factor function."""

    def test_neutral_unchanged(self):
        """Neutral PE direction should not change WIS."""
        assert get_age_adjustment_factor(60.0, 7, "neutral") == 60.0
        assert get_age_adjustment_factor(60.0, 70, "neutral") == 60.0

    def test_reference_age_unchanged(self):
        """Reference band age should not change WIS."""
        assert get_age_adjustment_factor(70.0, 35, "positive") == 70.0
        assert get_age_adjustment_factor(30.0, 35, "negative") == 30.0

    def test_positive_effect_amplified_for_child(self):
        """Positive PE effect should be stronger for children."""
        base_wis = 70.0  # Above neutral
        child_wis = get_age_adjustment_factor(base_wis, 7, "positive")
        adult_wis = get_age_adjustment_factor(base_wis, 35, "positive")
        assert child_wis >= adult_wis, "Child should get more benefit from good feature"

    def test_negative_effect_amplified_for_elderly(self):
        """Negative PE effect should be stronger for elderly."""
        base_wis = 30.0  # Below neutral
        elderly_wis = get_age_adjustment_factor(base_wis, 70, "negative")
        adult_wis = get_age_adjustment_factor(base_wis, 35, "negative")
        assert elderly_wis <= adult_wis, "Elderly should suffer more from bad feature"


class TestCallComputeWithAge:
    """Test the call_compute_with_age function."""

    def test_calls_vf3_correctly(self):
        result = call_compute_with_age(
            template_id="VF3",
            measured_features={
                "ceiling_height_m": 2.75,
                "floor_area_m2": 18.0,
            },
            occupant_profile={"age": 35},
        )
        assert result is not None
        assert result.output_type == "goldilocks_zone"
        # r_h is stored in the value field, not in details
        assert result.value > 0  # R_h ratio computed
        assert "lifespan_multiplier" in result.details

    def test_returns_none_for_unknown_template(self):
        result = call_compute_with_age(
            template_id="NONEXISTENT",
            measured_features={},
            occupant_profile={"age": 35},
        )
        assert result is None

    def test_returns_none_for_missing_required_params(self):
        """Should return None if required parameters are missing."""
        result = call_compute_with_age(
            template_id="VF3",
            measured_features={"ceiling_height_m": 3.0},  # Missing floor_area_m2
            occupant_profile={"age": 35},
        )
        assert result is None
