"""Tests for Tier A Quick Assessment. Sprint 12 Task 12.6."""

import pytest
from src.cmr.quick_assess import quick_assess, format_quick_report, QuickAssessResult


class TestQuickAssessBasics:
    def test_returns_result(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        assert isinstance(result, QuickAssessResult)

    def test_rating_in_valid_range(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        assert result.overall_rating in ["Good", "Fair", "Needs Attention", "Poor"]

    def test_wis_in_range(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        assert 0 <= result.overall_wis <= 100


class TestTierATemplates:
    def test_vf3_assessed_with_dimensions(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        assert "VF3" in result.template_scores

    def test_view1_assessed_with_view(self):
        result = quick_assess(has_nature_view=True, view_content="nature")
        assert "VIEW1" in result.template_scores

    def test_sc4_assessed_with_wayfinding(self):
        result = quick_assess(wayfinding_clear=True)
        assert "SC4" in result.template_scores

    def test_mat4_assessed_with_material(self):
        result = quick_assess(primary_material="wood")
        assert "MAT4" in result.template_scores


class TestQualityRatings:
    def test_good_conditions_rate_well(self):
        result = quick_assess(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            has_nature_view=True,
            view_content="nature",
            wayfinding_clear=True,
            primary_material="wood",
            thermal_system="operable_windows",
        )
        assert result.overall_wis >= 60

    def test_poor_conditions_rate_badly(self):
        result = quick_assess(
            ceiling_height_m=2.4,
            floor_area_m2=100.0,
            has_nature_view=False,
            view_content=None,
            wayfinding_clear=False,
            primary_material="concrete",
            thermal_system=None,
        )
        assert result.overall_wis < 60


class TestRecommendations:
    def test_has_recommendations(self):
        result = quick_assess(ceiling_height_m=2.5, floor_area_m2=20.0)
        assert len(result.recommendations) >= 1

    def test_recommends_nature_for_poor_view(self):
        result = quick_assess(has_nature_view=False, view_content=None)
        has_nature_rec = any("nature" in r.lower() for r in result.recommendations)
        assert has_nature_rec or result.overall_wis >= 50


class TestTierBSuggestions:
    def test_has_tier_b_suggestions(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        assert len(result.tier_b_suggestions) >= 1

    def test_suggests_light_measurement(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        has_light = any("light" in s.lower() or "lux" in s.lower() for s in result.tier_b_suggestions)
        assert has_light


class TestTierBExtendedAssessment:
    def test_tier_b_inputs_enable_ab_mode(self):
        result = quick_assess(
            ceiling_height_m=3.0,
            floor_area_m2=25.0,
            has_nature_view=True,
            view_content="nature",
            wayfinding_clear=True,
            wall_colors=["green", "beige"],
            color_sequence_varied=True,
            floor_surface="level",
            thermal_system="operable_windows",
            primary_material="wood",
            max_group_size=8,
            illuminance_lux=420,
            ambient_noise_dba=42,
            rt60_seconds=0.5,
        )
        assert result.tier_mode == "A+B"
        assert result.templates_assessed >= 20
        assert len(result.tier_b_reveals) >= 1
        assert "L1" in result.template_scores
        assert "SOC2" in result.template_scores


class TestSkippedTemplates:
    def test_skips_without_inputs(self):
        result = quick_assess()  # No inputs
        assert len(result.templates_skipped) > 0

    def test_tracks_skipped(self):
        result = quick_assess(ceiling_height_m=3.0)  # Only ceiling
        assert "VIEW1" in result.templates_skipped


class TestReportFormatting:
    def test_format_report_returns_string(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        report = format_quick_report(result)
        assert isinstance(report, str)
        assert "Overall Rating" in report

    def test_report_includes_score(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0)
        report = format_quick_report(result)
        assert "Wellness Score" in report


class TestAgeModeration:
    def test_age_parameter_accepted(self):
        result = quick_assess(ceiling_height_m=3.0, floor_area_m2=25.0, occupant_age=70)
        assert isinstance(result, QuickAssessResult)
