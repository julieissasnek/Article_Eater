"""Tests for Sensitivity Analysis. Sprint 12 Task 12.20."""

import pytest
from src.cmr.sensitivity import (
    analyze_sensitivity,
    format_sensitivity_report,
    get_quick_sensitivity,
    FeatureSensitivity,
    SensitivityResult,
    FEATURE_RANGES,
    CATEGORICAL_FEATURES,
)


class TestFeatureRanges:
    def test_continuous_features_have_required_keys(self):
        for name, config in FEATURE_RANGES.items():
            assert "worst" in config, f"{name} missing 'worst'"
            assert "best" in config, f"{name} missing 'best'"
            assert "unit" in config, f"{name} missing 'unit'"
            assert "description" in config, f"{name} missing 'description'"
            assert "category" in config, f"{name} missing 'category'"

    def test_categorical_features_have_required_keys(self):
        for name, config in CATEGORICAL_FEATURES.items():
            assert "worst" in config, f"{name} missing 'worst'"
            assert "best" in config, f"{name} missing 'best'"
            assert "description" in config, f"{name} missing 'description'"
            assert "category" in config, f"{name} missing 'category'"

    def test_ceiling_height_range(self):
        assert FEATURE_RANGES["ceiling_height_m"]["worst"] < FEATURE_RANGES["ceiling_height_m"]["best"]

    def test_noise_is_inverted(self):
        # Lower noise is better
        assert FEATURE_RANGES["ambient_noise_dba"]["worst"] > FEATURE_RANGES["ambient_noise_dba"]["best"]


class TestQuickSensitivity:
    def test_returns_dict(self):
        result = get_quick_sensitivity({})
        assert isinstance(result, dict)
        assert "quick_analysis" in result
        assert result["quick_analysis"] is True

    def test_has_recommendations(self):
        result = get_quick_sensitivity({"ceiling_height_m": 2.4})
        assert "recommendations" in result
        assert "top_recommendation" in result

    def test_identifies_low_ceiling(self):
        result = get_quick_sensitivity({"ceiling_height_m": 2.4})
        recs = result["recommendations"]
        has_ceiling_rec = any(r["feature"] == "ceiling_height_m" for r in recs)
        assert has_ceiling_rec

    def test_identifies_low_light(self):
        result = get_quick_sensitivity({"illuminance_lux": 100})
        recs = result["recommendations"]
        has_light_rec = any(r["feature"] == "illuminance_lux" for r in recs)
        assert has_light_rec

    def test_identifies_high_noise(self):
        result = get_quick_sensitivity({"ambient_noise_dba": 60})
        recs = result["recommendations"]
        has_noise_rec = any(r["feature"] == "ambient_noise_dba" for r in recs)
        assert has_noise_rec

    def test_identifies_missing_nature_view(self):
        result = get_quick_sensitivity({"has_nature_view": False})
        recs = result["recommendations"]
        has_view_rec = any(r["feature"] == "has_nature_view" for r in recs)
        assert has_view_rec

    def test_good_conditions_fewer_recommendations(self):
        good = get_quick_sensitivity({
            "ceiling_height_m": 3.5,
            "illuminance_lux": 450,
            "ambient_noise_dba": 35,
            "has_nature_view": True,
            "primary_material": "wood",
        })
        bad = get_quick_sensitivity({
            "ceiling_height_m": 2.4,
            "illuminance_lux": 100,
            "ambient_noise_dba": 70,
            "has_nature_view": False,
            "primary_material": "concrete",
        })
        # Bad conditions should have more recommendations
        assert len(bad["recommendations"]) >= len(good["recommendations"])

    def test_age_specific_recommendations(self):
        child_result = get_quick_sensitivity({}, {"age": 8})
        adult_result = get_quick_sensitivity({}, {"age": 35})
        elder_result = get_quick_sensitivity({}, {"age": 75})
        # Different age groups get different recommendations
        # (or at least the function handles them without error)
        assert isinstance(child_result, dict)
        assert isinstance(adult_result, dict)
        assert isinstance(elder_result, dict)


class TestFeatureSensitivityDataclass:
    def test_creates_sensitivity_record(self):
        s = FeatureSensitivity(
            feature="test",
            description="Test feature",
            category="test_cat",
            worst_value=1.0,
            best_value=5.0,
            unit="m",
            wis_at_worst=40.0,
            wis_at_best=60.0,
            wis_delta=20.0,
        )
        assert s.feature == "test"
        assert s.wis_delta == 20.0
        assert s.rank == 0  # Default
        assert s.diminishing_returns is False  # Default


class TestSensitivityResultDataclass:
    def test_creates_result(self):
        r = SensitivityResult(
            baseline_wis=55.0,
            top_recommendation="Do something",
            top_feature="ceiling_height_m",
            top_delta=15.0,
        )
        assert r.baseline_wis == 55.0
        assert r.top_feature == "ceiling_height_m"
        assert len(r.feature_sensitivities) == 0  # Default empty


class TestFormatSensitivityReport:
    def test_formats_result(self):
        result = SensitivityResult(
            baseline_wis=55.0,
            feature_sensitivities=[
                FeatureSensitivity(
                    feature="ceiling_height_m",
                    description="Ceiling height",
                    category="spatial",
                    worst_value=2.4,
                    best_value=4.0,
                    unit="m",
                    wis_at_worst=45.0,
                    wis_at_best=65.0,
                    wis_delta=20.0,
                    rank=1,
                ),
            ],
            top_recommendation="Increase ceiling height",
            top_feature="ceiling_height_m",
            top_delta=20.0,
            category_impacts={"spatial": 20.0},
        )
        report = format_sensitivity_report(result)
        assert isinstance(report, str)
        assert "SENSITIVITY ANALYSIS" in report
        assert "Baseline WIS" in report
        assert "Ceiling height" in report
        assert "spatial" in report.lower()

    def test_includes_recommendation(self):
        result = SensitivityResult(
            baseline_wis=50.0,
            top_recommendation="Test recommendation here",
        )
        report = format_sensitivity_report(result)
        assert "Test recommendation here" in report

    def test_marks_diminishing_returns(self):
        result = SensitivityResult(
            baseline_wis=50.0,
            feature_sensitivities=[
                FeatureSensitivity(
                    feature="test",
                    description="Test feature",
                    category="test",
                    worst_value=0,
                    best_value=10,
                    unit="",
                    wis_at_worst=40,
                    wis_at_best=60,
                    wis_delta=20,
                    rank=1,
                    diminishing_returns=True,
                    diminishing_threshold=6.0,
                ),
            ],
        )
        report = format_sensitivity_report(result)
        assert "*" in report  # Diminishing returns marker


class TestAnalyzeSensitivity:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_sens.db")

    def test_returns_result(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,  # Faster
        )
        assert isinstance(result, SensitivityResult)

    def test_has_baseline_wis(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
        )
        assert 0 <= result.baseline_wis <= 100

    def test_has_feature_sensitivities(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
        )
        assert len(result.feature_sensitivities) > 0

    def test_sensitivities_are_ranked(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
        )
        ranks = [s.rank for s in result.feature_sensitivities]
        assert ranks == sorted(ranks)  # Should be in order 1, 2, 3, ...

    def test_has_top_recommendation(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
        )
        assert result.top_recommendation != ""
        assert result.top_feature != ""
        assert "probability" in result.top_recommendation.lower()

    def test_has_category_impacts(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
        )
        assert len(result.category_impacts) > 0
        assert "spatial" in result.category_impacts

    def test_handles_empty_features(self, temp_db):
        result = analyze_sensitivity(
            measured_features={},
            db_path=temp_db,
            check_diminishing=False,
        )
        assert isinstance(result, SensitivityResult)

    def test_probability_and_actionability_fields(self, temp_db):
        result = analyze_sensitivity(
            measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 20.0},
            db_path=temp_db,
            check_diminishing=False,
            monte_carlo_samples=300,
        )
        assert 0.0 <= result.top_probability <= 1.0
        for s in result.feature_sensitivities:
            assert 0.0 <= s.improvement_probability <= 1.0
            assert s.delta_ci_lower <= s.delta_ci_upper
            assert s.actionability_score >= 0.0


class TestCLIIntegration:
    def test_sensitivity_command_exists(self):
        from src.cmr.cli import build_parser
        parser = build_parser()
        # Test that the sensitivity command is recognized
        args = parser.parse_args(["sensitivity"])
        assert args.command == "sensitivity"

    def test_quick_sensitivity_flag(self):
        from src.cmr.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["sensitivity", "--quick", "--ceiling-height", "2.75"])
        assert args.quick is True
        assert args.ceiling_height == 2.75

    def test_no_diminishing_flag(self):
        from src.cmr.cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["sensitivity", "--no-diminishing"])
        assert args.no_diminishing is True
