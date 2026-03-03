"""
Tests for Credence Confidence Intervals via Delta Method Uncertainty Propagation

Comprehensive test suite for credence_intervals.py module, covering:
1. Utility functions (logit, sigmoid, derivatives)
2. Delta method variance computation
3. Single credence estimation with confidence intervals
4. Batch processing
5. Uncertainty decomposition and sensitivity analysis
6. Edge cases and boundary conditions

Reference:
    Cooke, R. M. (1991). Experts in Uncertainty. Oxford University Press.
    Casella & Berger (2002). Statistical Inference (2nd ed.). §5.5: Delta method.

Author: Claude Code
Date: 2026-03-02
"""

import math
import pytest

from src.services.credence_intervals import (
    logit,
    sigmoid,
    sigmoid_derivative,
    logit_derivative,
    compute_logit_variance,
    compute_credence_se,
    compute_credence_with_ci,
    batch_credence_intervals,
    uncertainty_decomposition,
    sensitivity_analysis,
    CredenceEstimate,
    BatchCredenceResult,
    Z_CRITICAL_95,
    Z_CRITICAL_90,
    Z_CRITICAL_99,
    DEFAULT_D_SE,
    DEFAULT_OMEGA_SE,
    DEFAULT_DELTA_SE,
    DEFAULT_P_LAB_SE,
)


# =============================================================================
# UTILITY FUNCTION TESTS
# =============================================================================

class TestLogitSigmoid:
    """Test logit and sigmoid transformations."""

    def test_logit_neutral(self):
        """logit(0.5) should be 0."""
        assert abs(logit(0.5)) < 1e-10

    def test_logit_positive(self):
        """logit(p) > 0 for p > 0.5."""
        assert logit(0.75) > 0
        assert logit(0.99) > 0

    def test_logit_negative(self):
        """logit(p) < 0 for p < 0.5."""
        assert logit(0.25) < 0
        assert logit(0.01) < 0

    def test_sigmoid_neutral(self):
        """sigmoid(0) should be 0.5."""
        assert abs(sigmoid(0.0) - 0.5) < 1e-10

    def test_sigmoid_positive(self):
        """sigmoid(x) > 0.5 for x > 0."""
        assert sigmoid(1.0) > 0.5
        assert sigmoid(2.0) > 0.5

    def test_sigmoid_negative(self):
        """sigmoid(x) < 0.5 for x < 0."""
        assert sigmoid(-1.0) < 0.5
        assert sigmoid(-2.0) < 0.5

    def test_sigmoid_saturates(self):
        """sigmoid saturates to [0, 1] at extremes."""
        assert sigmoid(100) == 1.0
        assert sigmoid(-100) < 1e-40  # Saturates to ~0

    def test_logit_sigmoid_roundtrip(self):
        """sigmoid(logit(p)) should recover p."""
        for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert abs(sigmoid(logit(p)) - p) < 1e-8

    def test_sigmoid_logit_roundtrip(self):
        """logit(sigmoid(x)) should recover x."""
        for x in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            assert abs(logit(sigmoid(x)) - x) < 1e-8


class TestDerivatives:
    """Test derivative functions."""

    def test_sigmoid_derivative_neutral(self):
        """σ'(0) = 0.25."""
        assert abs(sigmoid_derivative(0.0) - 0.25) < 1e-10

    def test_sigmoid_derivative_monotone(self):
        """σ'(x) > 0 everywhere (sigmoid is monotone increasing)."""
        for x in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            assert sigmoid_derivative(x) > 0

    def test_sigmoid_derivative_symmetric(self):
        """σ'(-x) = σ'(x) (sigmoid derivative is symmetric)."""
        for x in [0.5, 1.0, 1.5, 2.0]:
            assert abs(sigmoid_derivative(x) - sigmoid_derivative(-x)) < 1e-10

    def test_logit_derivative_neutral(self):
        """logit'(0.5) = 4."""
        assert abs(logit_derivative(0.5) - 4.0) < 1e-10

    def test_logit_derivative_positive(self):
        """logit'(p) > 0 for all p ∈ (0, 1)."""
        for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert logit_derivative(p) > 0

    def test_logit_derivative_symmetric(self):
        """logit'(p) = logit'(1-p) (symmetric around 0.5)."""
        for p in [0.2, 0.3, 0.4]:
            assert abs(logit_derivative(p) - logit_derivative(1.0 - p)) < 1e-10


# =============================================================================
# DELTA METHOD VARIANCE COMPUTATION TESTS
# =============================================================================

class TestLogitVariance:
    """Test variance computation for logit transform via Delta method."""

    def test_zero_uncertainty(self):
        """With zero parameter uncertainty, total variance should be ~0."""
        total_var, _ = compute_logit_variance(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.0,
            d_se=0.0,
            omega_se=0.0,
            delta_se=0.0,
        )
        assert abs(total_var) < 1e-10

    def test_variance_decomposition_sums(self):
        """Component variances should sum to total variance."""
        total_var, components = compute_logit_variance(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )
        component_sum = sum(components.values())
        assert abs(total_var - component_sum) < 1e-10

    def test_variance_positive(self):
        """Variance should always be non-negative."""
        total_var, components = compute_logit_variance(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )
        assert total_var >= 0
        for v in components.values():
            assert v >= 0

    def test_variance_increases_with_uncertainty(self):
        """Variance should increase as input uncertainty increases."""
        total_var_low, _ = compute_logit_variance(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.05,
            d_se=0.05,
            omega_se=0.02,
            delta_se=0.02,
        )
        total_var_high, _ = compute_logit_variance(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.20,
            d_se=0.15,
            omega_se=0.10,
            delta_se=0.10,
        )
        assert total_var_high > total_var_low

    def test_p_lab_uncertainty_dominates_for_extreme_p(self):
        """For extreme p_lab values, p_lab uncertainty should dominate."""
        _, components_low = compute_logit_variance(
            p_lab=0.05,  # Very low probability
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )
        total = sum(components_low.values())
        p_lab_pct = (components_low["p_lab"] / total) * 100
        # p_lab should contribute >50% at extreme values
        assert p_lab_pct > 50


class TestCredenceSE:
    """Test transformation of standard error from log-odds to probability scale."""

    def test_zero_logit_se(self):
        """With zero logit_se, p_target_se should be zero."""
        se = compute_credence_se(p_target=0.75, logit_se=0.0)
        assert abs(se) < 1e-10

    def test_neutral_point(self):
        """At p_target=0.5, SE transformation should be maximal."""
        se_neutral = compute_credence_se(p_target=0.5, logit_se=1.0)
        se_extreme = compute_credence_se(p_target=0.9, logit_se=1.0)
        # At p=0.5, derivative is 0.25; at p=0.9, derivative is 0.09
        assert se_neutral > se_extreme

    def test_symmetric_around_neutral(self):
        """SE should be symmetric around p=0.5."""
        se_low = compute_credence_se(p_target=0.3, logit_se=1.0)
        se_high = compute_credence_se(p_target=0.7, logit_se=1.0)
        assert abs(se_low - se_high) < 1e-10

    def test_se_increases_with_logit_se(self):
        """p_target_se should increase with logit_se."""
        se1 = compute_credence_se(p_target=0.75, logit_se=0.5)
        se2 = compute_credence_se(p_target=0.75, logit_se=1.0)
        assert se2 > se1


# =============================================================================
# MAIN CREDENCE ESTIMATION WITH CI TESTS
# =============================================================================

class TestComputeCredenceWithCI:
    """Test the main entry point for credence estimation with confidence intervals."""

    def test_point_estimate_basic(self):
        """Test point estimate computation."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.0,
            d_se=0.0,
            omega_se=0.0,
            delta_se=0.0,
        )
        # With zero uncertainty, CI should be very narrow
        assert estimate.width() < 0.01

    def test_ci_bounds_valid(self):
        """CI bounds should satisfy: 0.01 <= lower <= point <= upper <= 0.99."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert 0.01 <= estimate.lower <= estimate.point <= estimate.upper <= 0.99

    def test_ci_width_positive(self):
        """CI width should be non-negative."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert estimate.width() >= 0

    def test_ci_width_increases_with_uncertainty(self):
        """CI width should increase as input uncertainty increases."""
        est_low = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.05,
            d_se=0.05,
            omega_se=0.02,
            delta_se=0.02,
        )
        est_high = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.25,
            d_se=0.20,
            omega_se=0.10,
            delta_se=0.10,
        )
        assert est_high.width() > est_low.width()

    def test_confidence_level_affects_width(self):
        """Wider CI should correspond to higher confidence level."""
        est_90 = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            confidence_level=0.90,
        )
        est_95 = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            confidence_level=0.95,
        )
        est_99 = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            confidence_level=0.99,
        )
        assert est_90.width() < est_95.width() < est_99.width()

    def test_symmetric_ci(self):
        """CI should be approximately symmetric around point estimate."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        lower_dist = estimate.point - estimate.lower
        upper_dist = estimate.upper - estimate.point
        assert abs(lower_dist - upper_dist) < 0.01

    def test_input_validation_p_lab(self):
        """p_lab must be in (0, 1)."""
        with pytest.raises(ValueError):
            compute_credence_with_ci(p_lab=0.0, d=0.80, omega=0.85)
        with pytest.raises(ValueError):
            compute_credence_with_ci(p_lab=1.0, d=0.80, omega=0.85)

    def test_input_validation_confidence(self):
        """confidence_level must be in (0, 1)."""
        with pytest.raises(ValueError):
            compute_credence_with_ci(
                p_lab=0.75,
                d=0.80,
                omega=0.85,
                confidence_level=0.0,
            )
        with pytest.raises(ValueError):
            compute_credence_with_ci(
                p_lab=0.75,
                d=0.80,
                omega=0.85,
                confidence_level=1.0,
            )

    def test_credence_data_structure(self):
        """CredenceEstimate should have all required fields."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert hasattr(estimate, "point")
        assert hasattr(estimate, "lower")
        assert hasattr(estimate, "upper")
        assert hasattr(estimate, "se")
        assert hasattr(estimate, "confidence_level")
        assert hasattr(estimate, "components")
        assert hasattr(estimate, "logit_se")
        assert hasattr(estimate, "notes")

    def test_components_sum_to_100(self):
        """Variance components should sum to ~100%."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        component_sum = sum(estimate.components.values())
        assert abs(component_sum - 100.0) < 0.1

    def test_serialization(self):
        """CredenceEstimate should serialize to dict."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        d = estimate.to_dict()
        assert "point" in d
        assert "lower" in d
        assert "upper" in d
        assert "se" in d
        assert "components" in d


class TestCredenceEstimate:
    """Test CredenceEstimate dataclass."""

    def test_post_init_validation(self):
        """Post-init should clip invalid bounds."""
        # This should not raise, but should clip
        estimate = CredenceEstimate(
            point=0.5,
            lower=-0.1,
            upper=1.1,
            se=0.05,
        )
        assert 0.01 <= estimate.lower
        assert estimate.upper <= 0.99

    def test_width_method(self):
        """width() should return upper - lower."""
        estimate = CredenceEstimate(
            point=0.5,
            lower=0.4,
            upper=0.6,
            se=0.05,
        )
        assert abs(estimate.width() - 0.2) < 1e-10


# =============================================================================
# BATCH PROCESSING TESTS
# =============================================================================

class TestBatchCredenceIntervals:
    """Test batch processing of multiple beliefs."""

    def test_batch_empty(self):
        """Batch with no beliefs should return empty list."""
        result = batch_credence_intervals([])
        assert len(result.estimates) == 0

    def test_batch_single(self):
        """Batch with one belief should return one estimate."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85, "delta": 0.90}
        ]
        result = batch_credence_intervals(beliefs)
        assert len(result.estimates) == 1
        assert isinstance(result.estimates[0], CredenceEstimate)

    def test_batch_multiple(self):
        """Batch with multiple beliefs should return multiple estimates."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85, "delta": 0.90},
            {"p_lab": 0.65, "d": 0.80, "omega": 0.70, "delta": 0.85},
            {"p_lab": 0.55, "d": 0.95, "omega": 0.90, "delta": 1.0},
        ]
        result = batch_credence_intervals(beliefs)
        assert len(result.estimates) == 3

    def test_batch_summary_stats(self):
        """Batch should compute summary statistics."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85},
            {"p_lab": 0.65, "d": 0.80, "omega": 0.70},
        ]
        result = batch_credence_intervals(beliefs)
        assert "mean_point" in result.summary_stats
        assert "mean_ci_width" in result.summary_stats
        assert "median_ci_width" in result.summary_stats
        assert result.summary_stats["n_beliefs"] == 2

    def test_batch_with_belief_ids(self):
        """Batch should preserve belief identifiers."""
        beliefs = [
            {"belief_id": "B1", "p_lab": 0.75, "d": 0.80, "omega": 0.85},
            {"belief_id": "B2", "p_lab": 0.65, "d": 0.80, "omega": 0.70},
        ]
        result = batch_credence_intervals(beliefs)
        for est in result.estimates:
            assert "belief_id" in est.notes

    def test_batch_missing_required_fields(self):
        """Batch should skip beliefs missing required fields."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85},
            {"p_lab": 0.65, "d": 0.80},  # Missing omega
            {"p_lab": 0.55, "d": 0.95, "omega": 0.90},
        ]
        result = batch_credence_intervals(beliefs)
        assert len(result.estimates) == 2

    def test_batch_defaults(self):
        """Batch should use default uncertainty values when not provided."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85}
        ]
        result = batch_credence_intervals(beliefs)
        assert len(result.estimates) == 1
        # Point estimate should be computed with defaults
        assert result.estimates[0].se > 0

    def test_batch_serialization(self):
        """Batch result should serialize to dict."""
        beliefs = [
            {"p_lab": 0.75, "d": 0.80, "omega": 0.85},
            {"p_lab": 0.65, "d": 0.80, "omega": 0.70},
        ]
        result = batch_credence_intervals(beliefs)
        d = result.to_dict()
        assert "estimates" in d
        assert "summary_stats" in d
        assert len(d["estimates"]) == 2


# =============================================================================
# UNCERTAINTY DECOMPOSITION TESTS
# =============================================================================

class TestUncertaintyDecomposition:
    """Test variance contribution analysis."""

    def test_decomposition_sums_to_100(self):
        """Percentage decomposition should sum to 100%."""
        decomp = uncertainty_decomposition(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )
        component_sum = sum(v for k, v in decomp.items() if k != "total_var")
        assert abs(component_sum - 100.0) < 0.1

    def test_decomposition_all_parameters(self):
        """Decomposition should include all parameters."""
        decomp = uncertainty_decomposition(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert "p_lab" in decomp
        assert "d" in decomp
        assert "omega" in decomp
        assert "delta" in decomp
        assert "total_var" in decomp

    def test_decomposition_with_zero_uncertainty(self):
        """With zero uncertainty, all components should be zero."""
        decomp = uncertainty_decomposition(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.0,
            d_se=0.0,
            omega_se=0.0,
            delta_se=0.0,
        )
        assert decomp["total_var"] == 0.0


# =============================================================================
# SENSITIVITY ANALYSIS TESTS
# =============================================================================

class TestSensitivityAnalysis:
    """Test sensitivity analysis functionality."""

    def test_sensitivity_returns_dict(self):
        """Sensitivity analysis should return dict with all parameters."""
        sens = sensitivity_analysis(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
        )
        assert "p_lab_se" in sens
        assert "d_se" in sens
        assert "omega_se" in sens
        assert "delta_se" in sens

    def test_sensitivity_results_are_lists(self):
        """Each parameter should have a list of (se, width) tuples."""
        sens = sensitivity_analysis(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            n_points=5,
        )
        for param, results in sens.items():
            assert isinstance(results, list)
            assert len(results) == 5
            for se, width in results:
                assert isinstance(se, float)
                assert isinstance(width, float)

    def test_sensitivity_ci_width_increases(self):
        """CI width should increase monotonically with parameter uncertainty."""
        sens = sensitivity_analysis(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            n_points=5,
        )
        for param, results in sens.items():
            widths = [w for _, w in results]
            # Widths should be non-decreasing (allowing for small numerical variation)
            for i in range(len(widths) - 1):
                assert widths[i] <= widths[i + 1] + 1e-6


# =============================================================================
# REALISTIC INTEGRATION TESTS
# =============================================================================

class TestRealisticScenarios:
    """Test realistic belief assessment scenarios."""

    def test_strong_evidence(self):
        """Strong evidence should have narrow CI and high credence."""
        estimate = compute_credence_with_ci(
            p_lab=0.80,      # High effect in lab
            d=0.95,           # Constitutive warrant (near-perfect transfer)
            omega=0.95,       # Excellent warrant strength
            delta=0.95,       # Similar population
            p_lab_se=0.05,    # Low uncertainty
            d_se=0.05,
            omega_se=0.03,
            delta_se=0.03,
        )
        assert estimate.point > 0.70
        assert estimate.width() < 0.25

    def test_weak_evidence(self):
        """Weak evidence should have wider CI and moderate credence."""
        estimate = compute_credence_with_ci(
            p_lab=0.55,       # Marginal effect in lab
            d=0.40,           # Analogical warrant (fragile transfer)
            omega=0.50,       # Moderate warrant strength
            delta=0.70,       # Different population
            p_lab_se=0.20,    # High uncertainty
            d_se=0.15,
            omega_se=0.10,
            delta_se=0.10,
        )
        assert 0.40 < estimate.point < 0.65
        assert estimate.width() > 0.10

    def test_moderate_evidence(self):
        """Moderate evidence should have moderate CI and credence."""
        estimate = compute_credence_with_ci(
            p_lab=0.70,       # Moderate effect in lab
            d=0.80,           # Mechanism warrant
            omega=0.75,       # Good warrant strength
            delta=0.85,       # Fairly similar population
            p_lab_se=0.12,    # Moderate uncertainty
            d_se=0.08,
            omega_se=0.05,
            delta_se=0.05,
        )
        assert 0.55 < estimate.point < 0.80
        assert 0.10 < estimate.width() < 0.30

    def test_high_uncertainty_scenario(self):
        """High uncertainty in all parameters should give very wide CI."""
        estimate = compute_credence_with_ci(
            p_lab=0.60,
            d=0.70,
            omega=0.70,
            delta=0.75,
            p_lab_se=0.25,    # High uncertainty everywhere
            d_se=0.20,
            omega_se=0.15,
            delta_se=0.15,
            confidence_level=0.99,
        )
        # CI should be quite wide
        assert estimate.width() > 0.30

    def test_extreme_p_lab(self):
        """Very high or very low p_lab should produce near-extreme credences."""
        est_low = compute_credence_with_ci(
            p_lab=0.05,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        est_high = compute_credence_with_ci(
            p_lab=0.95,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert est_low.point < 0.3
        assert est_high.point > 0.7


# =============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_p_lab_near_zero(self):
        """p_lab near 0 should not cause numerical issues."""
        estimate = compute_credence_with_ci(
            p_lab=0.01,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert 0.0 < estimate.point < 1.0

    def test_p_lab_near_one(self):
        """p_lab near 1 should not cause numerical issues."""
        estimate = compute_credence_with_ci(
            p_lab=0.99,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert 0.0 < estimate.point < 1.0

    def test_all_parameters_zero(self):
        """Very small parameters should not crash."""
        estimate = compute_credence_with_ci(
            p_lab=0.50,
            d=0.01,
            omega=0.01,
            delta=0.01,
        )
        assert 0.0 < estimate.point < 1.0

    def test_all_parameters_one(self):
        """All parameters at maximum should work."""
        estimate = compute_credence_with_ci(
            p_lab=0.99,
            d=0.95,
            omega=1.0,
            delta=1.0,
        )
        assert estimate.point > 0.95

    def test_zero_se_parameters(self):
        """Zero SE for all parameters should give narrow CI."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.0,
            d_se=0.0,
            omega_se=0.0,
            delta_se=0.0,
        )
        assert estimate.width() < 0.01

    def test_very_large_se(self):
        """Very large SEs should not cause overflow."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.50,
            d_se=0.50,
            omega_se=0.50,
            delta_se=0.50,
        )
        assert 0.01 <= estimate.lower
        assert estimate.upper <= 0.99


# =============================================================================
# NUMERICAL PRECISION TESTS
# =============================================================================

class TestNumericalPrecision:
    """Test numerical stability and precision."""

    def test_consistency_across_calls(self):
        """Same inputs should give identical outputs."""
        est1 = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        est2 = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
        )
        assert est1.point == est2.point
        assert est1.lower == est2.lower
        assert est1.upper == est2.upper

    def test_se_always_positive(self):
        """Standard error should always be non-negative."""
        for p_lab in [0.1, 0.3, 0.5, 0.7, 0.9]:
            for d in [0.3, 0.6, 0.9]:
                for omega in [0.5, 0.8]:
                    estimate = compute_credence_with_ci(p_lab, d, omega)
                    assert estimate.se >= 0

    def test_logit_se_nonzero_with_uncertainty(self):
        """With non-zero input uncertainty, logit_se should be positive."""
        estimate = compute_credence_with_ci(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )
        assert estimate.logit_se > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
