"""Tests for Uncertainty-Aware WIS. Sprint 13 Task 13.6."""

import pytest
import random

from src.cmr.wis import (
    UncertainWIS,
    compute_uncertain_wis,
    aggregate_domain_wis_uncertain,
    aggregate_overall_wis_uncertain,
    get_uncertainty_breakdown,
    CALIBRATION_UNCERTAINTY,
    TIER_UNCERTAINTY,
    PE_CONTRIBUTION_UNCERTAINTY,
    _get_uncertainty_sd,
)


class TestUncertaintyConstants:
    def test_calibration_uncertainty_values(self):
        # More calibrated = less uncertainty
        assert CALIBRATION_UNCERTAINTY["established"] < CALIBRATION_UNCERTAINTY["partial"]
        assert CALIBRATION_UNCERTAINTY["partial"] < CALIBRATION_UNCERTAINTY["uncalibrated"]

    def test_tier_uncertainty_values(self):
        # Higher tier (more precise) = less uncertainty
        assert TIER_UNCERTAINTY["D"] < TIER_UNCERTAINTY["C"]
        assert TIER_UNCERTAINTY["C"] < TIER_UNCERTAINTY["B"]
        assert TIER_UNCERTAINTY["B"] < TIER_UNCERTAINTY["A"]

    def test_pe_contribution_values(self):
        # Predictive is most certain
        assert PE_CONTRIBUTION_UNCERTAINTY["predictive"] < PE_CONTRIBUTION_UNCERTAINTY["explanatory"]
        assert PE_CONTRIBUTION_UNCERTAINTY["explanatory"] < PE_CONTRIBUTION_UNCERTAINTY["organizational"]


class TestGetUncertaintySD:
    def test_established_calibration_low_sd(self):
        sd = _get_uncertainty_sd(60.0, "established", "C", "predictive")
        # Should be relatively low (well-calibrated, precise, predictive)
        assert sd < 15.0

    def test_uncalibrated_high_sd(self):
        sd = _get_uncertainty_sd(60.0, "uncalibrated", "A", "unknown")
        # Should be high (uncalibrated, visual observation, unknown PE)
        assert sd > 20.0

    def test_higher_base_wis_higher_sd(self):
        sd_low = _get_uncertainty_sd(30.0, "partial", "B", "explanatory")
        sd_high = _get_uncertainty_sd(80.0, "partial", "B", "explanatory")
        # SD scales with base WIS
        assert sd_high > sd_low

    def test_minimum_sd(self):
        # Even with perfect calibration, there should be minimum uncertainty
        sd = _get_uncertainty_sd(10.0, "established", "D", "predictive")
        assert sd >= 1.0


class TestUncertainWIS:
    def test_creates_dataclass(self):
        u = UncertainWIS(
            wis=60.0,
            wis_lower=55.0,
            wis_upper=65.0,
            confidence_width=10.0,
        )
        assert u.wis == 60.0
        assert u.wis_lower == 55.0
        assert u.wis_upper == 65.0
        assert u.confidence_width == 10.0

    def test_to_dict(self):
        u = UncertainWIS(wis=60.0, wis_lower=55.0, wis_upper=65.0, confidence_width=10.0)
        d = u.to_dict()
        assert d["wis"] == 60.0
        assert d["wis_lower"] == 55.0
        assert d["wis_upper"] == 65.0


class TestComputeUncertainWIS:
    def test_returns_uncertain_wis(self):
        random.seed(42)
        result = compute_uncertain_wis(60.0)
        assert isinstance(result, UncertainWIS)
        assert result.wis == 60.0

    def test_bounds_contain_point_estimate(self):
        random.seed(42)
        result = compute_uncertain_wis(60.0, n_samples=1000)
        # Point estimate should typically be within bounds
        # (though not guaranteed for all seeds)
        assert result.wis_lower <= result.wis <= result.wis_upper

    def test_confidence_width_positive(self):
        random.seed(42)
        result = compute_uncertain_wis(60.0)
        assert result.confidence_width > 0

    def test_lower_uncertainty_narrower_ci(self):
        random.seed(42)
        # Well-calibrated should have narrower CI
        established = compute_uncertain_wis(60.0, "established", "C", "predictive")
        random.seed(42)
        uncalibrated = compute_uncertain_wis(60.0, "uncalibrated", "A", "unknown")
        assert established.confidence_width < uncalibrated.confidence_width

    def test_clamps_to_valid_range(self):
        random.seed(42)
        result = compute_uncertain_wis(95.0, "uncalibrated")  # High uncertainty
        # Should clamp to 0-100
        assert 0 <= result.wis_lower <= 100
        assert 0 <= result.wis_upper <= 100

    def test_custom_n_samples(self):
        random.seed(42)
        result = compute_uncertain_wis(60.0, n_samples=500)
        assert result.n_samples == 500


class TestAggregateDomainWISUncertain:
    def test_empty_scores(self):
        result = aggregate_domain_wis_uncertain([])
        assert result["domain_wis"] == 0.0
        assert result["template_count"] == 0

    def test_single_template(self):
        random.seed(42)
        scores = [{"wis": 60.0, "calibration_status": "partial"}]
        result = aggregate_domain_wis_uncertain(scores, n_samples=500)
        assert result["domain_wis"] == pytest.approx(60.0, rel=0.1)
        assert result["template_count"] == 1

    def test_multiple_templates(self):
        random.seed(42)
        scores = [
            {"wis": 60.0, "calibration_status": "partial"},
            {"wis": 70.0, "calibration_status": "substantial"},
            {"wis": 50.0, "calibration_status": "preliminary"},
        ]
        result = aggregate_domain_wis_uncertain(scores, n_samples=500)
        # Should be weighted average of 60, 70, 50
        assert 50 < result["domain_wis"] < 70
        assert result["template_count"] == 3

    def test_has_uncertainty_bounds(self):
        random.seed(42)
        scores = [{"wis": 60.0, "calibration_status": "partial"}]
        result = aggregate_domain_wis_uncertain(scores, n_samples=500)
        assert "domain_wis_lower" in result
        assert "domain_wis_upper" in result
        assert "confidence_width" in result
        assert result["confidence_width"] > 0

    def test_method_is_uncertain(self):
        result = aggregate_domain_wis_uncertain([{"wis": 50.0}])
        assert result["method"] == "uncertain_weighted_average"


class TestAggregateOverallWISUncertain:
    def test_empty_domains(self):
        result = aggregate_overall_wis_uncertain([])
        assert result["overall_wis"] == 0.0
        assert result["domain_count"] == 0

    def test_single_domain(self):
        random.seed(42)
        domains = [{"domain_wis": 60.0, "domain": "L"}]
        result = aggregate_overall_wis_uncertain(domains, n_samples=500)
        assert result["overall_wis"] == pytest.approx(60.0, rel=0.1)

    def test_multiple_domains_geometric_mean(self):
        random.seed(42)
        domains = [
            {"domain_wis": 64.0, "domain": "L"},
            {"domain_wis": 64.0, "domain": "VF"},
        ]
        # Geometric mean of equal values should equal that value
        result = aggregate_overall_wis_uncertain(domains, n_samples=500)
        assert result["overall_wis"] == pytest.approx(64.0, rel=0.1)

    def test_has_uncertainty_bounds(self):
        random.seed(42)
        domains = [
            {"domain_wis": 60.0, "domain_wis_lower": 55.0, "domain_wis_upper": 65.0},
        ]
        result = aggregate_overall_wis_uncertain(domains, n_samples=500)
        assert "overall_wis_lower" in result
        assert "overall_wis_upper" in result
        assert "confidence_width" in result

    def test_identifies_severe_deficits(self):
        domains = [
            {"domain_wis": 60.0, "domain": "Good"},
            {"domain_wis": 25.0, "domain": "Bad"},
        ]
        result = aggregate_overall_wis_uncertain(domains, n_samples=500)
        assert "Bad" in result["severe_deficits"]

    def test_method_is_uncertain(self):
        result = aggregate_overall_wis_uncertain([{"domain_wis": 50.0}])
        assert result["method"] == "uncertain_geometric_mean"


class TestGetUncertaintyBreakdown:
    def test_returns_breakdown(self):
        breakdown = get_uncertainty_breakdown(60.0, "partial", "B", "explanatory")
        assert "parameter_uncertainty" in breakdown
        assert "measurement_uncertainty" in breakdown
        assert "model_uncertainty" in breakdown
        assert "combined_uncertainty_fraction" in breakdown

    def test_parameter_uncertainty_source(self):
        breakdown = get_uncertainty_breakdown(60.0, "established")
        assert breakdown["parameter_uncertainty"]["source"] == "calibration_status"
        assert breakdown["parameter_uncertainty"]["value"] == "established"

    def test_measurement_uncertainty_source(self):
        breakdown = get_uncertainty_breakdown(60.0, None, "C")
        assert breakdown["measurement_uncertainty"]["source"] == "accessibility_tier"
        assert breakdown["measurement_uncertainty"]["value"] == "C"

    def test_model_uncertainty_source(self):
        breakdown = get_uncertainty_breakdown(60.0, None, None, "predictive")
        assert breakdown["model_uncertainty"]["source"] == "pe_contribution"
        assert breakdown["model_uncertainty"]["value"] == "predictive"

    def test_wis_sd_values(self):
        breakdown = get_uncertainty_breakdown(100.0, "partial", "B", "explanatory")
        # WIS SD should be positive
        assert breakdown["parameter_uncertainty"]["wis_sd"] > 0
        assert breakdown["measurement_uncertainty"]["wis_sd"] > 0
        assert breakdown["model_uncertainty"]["wis_sd"] > 0

    def test_combined_uncertainty(self):
        breakdown = get_uncertainty_breakdown(60.0, "uncalibrated", "A", "unknown")
        # Combined should be higher than any individual
        param = breakdown["parameter_uncertainty"]["uncertainty_fraction"]
        meas = breakdown["measurement_uncertainty"]["uncertainty_fraction"]
        model = breakdown["model_uncertainty"]["uncertainty_fraction"]
        combined = breakdown["combined_uncertainty_fraction"]
        assert combined >= max(param, meas, model)


class TestReproducibility:
    def test_seed_reproducibility(self):
        random.seed(123)
        result1 = compute_uncertain_wis(60.0, "partial", "B", "explanatory", n_samples=100)
        random.seed(123)
        result2 = compute_uncertain_wis(60.0, "partial", "B", "explanatory", n_samples=100)
        assert result1.wis_lower == result2.wis_lower
        assert result1.wis_upper == result2.wis_upper


class TestEdgeCases:
    def test_zero_wis(self):
        random.seed(42)
        result = compute_uncertain_wis(0.0)
        assert result.wis == 0.0
        # Lower bound should be clamped to 0
        assert result.wis_lower >= 0

    def test_hundred_wis(self):
        random.seed(42)
        result = compute_uncertain_wis(100.0, "established", "D", "predictive")
        assert result.wis == 100.0
        # Upper bound should be clamped to 100
        assert result.wis_upper <= 100

    def test_unknown_calibration_status(self):
        # Should use default uncertainty
        result = compute_uncertain_wis(60.0, "nonexistent_status")
        assert isinstance(result, UncertainWIS)

    def test_unknown_tier(self):
        result = compute_uncertain_wis(60.0, accessibility_tier="X")
        assert isinstance(result, UncertainWIS)

    def test_unknown_pe_contribution(self):
        result = compute_uncertain_wis(60.0, pe_contribution="novel_type")
        assert isinstance(result, UncertainWIS)
