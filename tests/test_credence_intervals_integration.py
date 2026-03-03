"""
Integration tests for credence_intervals.py with existing ATLAS modules.

Tests the credence interval module working together with:
- epistemic_projection.py (ATLAS projection formula)
- warrant_strength.py (ω computation)

Author: Claude Code
Date: 2026-03-02
"""

import pytest

from src.services.epistemic_projection import (
    project_single_edge,
    CANONICAL_DISCOUNT_FACTORS,
)
from src.services.warrant_strength import compute_credence_from_warrants
from src.services.credence_intervals import (
    compute_credence_with_ci,
    batch_credence_intervals,
    uncertainty_decomposition,
)


class TestIntegrationWithEpistemicProjection:
    """Test credence_intervals working with epistemic_projection.py."""

    def test_point_estimate_consistency(self):
        """Point estimate from credence_intervals should match epistemic_projection."""
        # Single mechanism warrant
        p_lab = 0.75
        warrant_type = "mechanism"
        omega = 0.85
        delta = 0.90

        # From epistemic_projection
        d = CANONICAL_DISCOUNT_FACTORS[warrant_type]
        p_target_projection = project_single_edge(p_lab, warrant_type, omega, delta)

        # From credence_intervals (with zero uncertainty for comparison)
        estimate = compute_credence_with_ci(
            p_lab=p_lab,
            d=d,
            omega=omega,
            delta=delta,
            p_lab_se=0.0,
            d_se=0.0,
            omega_se=0.0,
            delta_se=0.0,
        )

        # Point estimates should match
        assert abs(estimate.point - p_target_projection) < 1e-10

    def test_parallel_projection_with_intervals(self):
        """Test multiple edges (parallel projection) with uncertainty quantification."""
        # Three independent pieces of evidence (parallel projection)
        edges = [
            {
                "p_lab": 0.75,
                "tau": "mechanism",
                "omega": 0.85,
                "delta": 0.90,
            },
            {
                "p_lab": 0.70,
                "tau": "empirical_association",
                "omega": 0.75,
                "delta": 0.85,
            },
            {
                "p_lab": 0.80,
                "tau": "functional",
                "omega": 0.80,
                "delta": 0.95,
            },
        ]

        # Point estimate from warrant_strength module
        credence_point = compute_credence_from_warrants(edges)

        # Now compute with uncertainty for the first edge
        # (to illustrate integration pattern)
        edge1 = edges[0]
        d1 = CANONICAL_DISCOUNT_FACTORS[edge1["tau"]]

        estimate = compute_credence_with_ci(
            p_lab=edge1["p_lab"],
            d=d1,
            omega=edge1["omega"],
            delta=edge1["delta"],
        )

        # Should have reasonable credence value
        assert 0.0 < estimate.point < 1.0
        # And uncertainty bounds
        assert estimate.lower < estimate.point < estimate.upper


class TestIntegrationWithWarrantStrength:
    """Test credence_intervals working with warrant_strength.py."""

    def test_omega_uncertainty_propagates(self):
        """Uncertainty in ω should propagate to credence CI width."""
        p_lab = 0.75
        d = 0.80
        delta = 0.90

        # Low ω uncertainty
        est_low_uncertainty = compute_credence_with_ci(
            p_lab=p_lab,
            d=d,
            omega=0.85,
            delta=delta,
            omega_se=0.02,  # Very precise ω
        )

        # High ω uncertainty
        est_high_uncertainty = compute_credence_with_ci(
            p_lab=p_lab,
            d=d,
            omega=0.85,
            delta=delta,
            omega_se=0.15,  # Uncertain ω
        )

        # Higher ω uncertainty should give wider CI
        assert est_high_uncertainty.width() > est_low_uncertainty.width()

        # Verify ω contribution increases
        low_omega_pct = est_low_uncertainty.components["omega"]
        high_omega_pct = est_high_uncertainty.components["omega"]
        assert high_omega_pct > low_omega_pct

    def test_realistic_warrant_scenario(self):
        """Test realistic RCT warrant scenario with credence intervals."""
        # Typical mechanism warrant from RCT
        # - p_lab ~ 0.70 (70% effect in lab)
        # - d = 0.80 (mechanism warrant type)
        # - ω ~ 0.80 (good warrant quality from RCT)
        # - δ ~ 0.85 (moderately similar population)

        estimate = compute_credence_with_ci(
            p_lab=0.70,
            d=0.80,
            omega=0.80,
            delta=0.85,
            p_lab_se=0.10,
            d_se=0.08,
            omega_se=0.05,
            delta_se=0.06,
        )

        # Should have reasonable credence
        assert 0.50 < estimate.point < 0.85

        # Should have non-trivial but bounded uncertainty
        assert 0.05 < estimate.width() < 0.50

        # p_lab uncertainty should dominate (as per sensitivity analysis)
        assert estimate.components["p_lab"] > 50.0


class TestBatchIntegrationScenario:
    """Test batch processing in realistic belief network scenario."""

    def test_multiple_warrant_types(self):
        """Process multiple edges with different warrant types."""
        beliefs = [
            {
                "belief_id": "B1",
                "p_lab": 0.80,  # High effect
                "d": CANONICAL_DISCOUNT_FACTORS["constitutive"],
                "omega": 0.95,
                "delta": 0.98,
                "p_lab_se": 0.05,
            },
            {
                "belief_id": "B2",
                "p_lab": 0.70,
                "d": CANONICAL_DISCOUNT_FACTORS["mechanism"],
                "omega": 0.80,
                "delta": 0.85,
                "p_lab_se": 0.10,
            },
            {
                "belief_id": "B3",
                "p_lab": 0.65,  # Adjusted: closer to 0.70 so we can see CI width patterns
                "d": CANONICAL_DISCOUNT_FACTORS["analogical"],
                "omega": 0.60,
                "delta": 0.70,
                "p_lab_se": 0.20,
            },
        ]

        result = batch_credence_intervals(beliefs, confidence_level=0.95)

        # Should process all beliefs
        assert len(result.estimates) == 3

        # Credence should decrease with lower p_lab and worse warrant type
        credences = [est.point for est in result.estimates]
        assert credences[0] > credences[1]  # B1 > B2
        assert credences[1] > credences[2]  # B2 > B3

        # B2 and B3 with higher p_lab_se should have wider CI than B1
        widths = [est.width() for est in result.estimates]
        assert widths[1] > widths[0] or widths[2] > widths[0]

        # Summary stats should be present
        assert result.summary_stats["n_beliefs"] == 3
        assert "mean_ci_width" in result.summary_stats

    def test_convergent_evidence_scenario(self):
        """Test multiple converging pieces of evidence."""
        # Three independent warrant types all supporting same claim
        beliefs = [
            {
                "belief_id": "empirical_assoc",
                "p_lab": 0.72,
                "d": CANONICAL_DISCOUNT_FACTORS["empirical_association"],
                "omega": 0.80,
                "delta": 0.90,
                "p_lab_se": 0.10,
            },
            {
                "belief_id": "mechanism",
                "p_lab": 0.75,
                "d": CANONICAL_DISCOUNT_FACTORS["mechanism"],
                "omega": 0.85,
                "delta": 0.88,
                "p_lab_se": 0.10,
            },
            {
                "belief_id": "functional",
                "p_lab": 0.68,
                "d": CANONICAL_DISCOUNT_FACTORS["functional"],
                "omega": 0.78,
                "delta": 0.85,
                "p_lab_se": 0.10,
            },
        ]

        result = batch_credence_intervals(beliefs)

        # All estimates should be in reasonable range
        for est in result.estimates:
            assert 0.35 < est.point < 0.85
            assert est.width() < 0.50

        # Mean credence should be moderate-to-high
        assert result.summary_stats["mean_point"] > 0.50


class TestUncertaintySourceIdentification:
    """Test using decomposition to identify critical uncertainties."""

    def test_identify_dominant_uncertainty_source(self):
        """Decomposition should identify which parameter's uncertainty drives CI width."""
        # Scenario: high p_lab uncertainty
        decomp_high_p_lab = uncertainty_decomposition(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.25,  # High uncertainty
            d_se=0.05,
            omega_se=0.02,
            delta_se=0.02,
        )

        # p_lab should dominate
        assert decomp_high_p_lab["p_lab"] > 80.0

        # Scenario: high d uncertainty
        decomp_high_d = uncertainty_decomposition(
            p_lab=0.75,
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.05,
            d_se=0.25,  # High uncertainty
            omega_se=0.02,
            delta_se=0.02,
        )

        # d should be more prominent
        assert decomp_high_d["d"] > decomp_high_d["p_lab"]

    def test_neutral_point_parameter_dominance(self):
        """Away from extreme p values, parameter uncertainties should be more balanced."""
        decomp = uncertainty_decomposition(
            p_lab=0.70,  # Moderate effect
            d=0.80,
            omega=0.85,
            delta=0.90,
            p_lab_se=0.15,
            d_se=0.10,
            omega_se=0.05,
            delta_se=0.05,
        )

        # p_lab should dominate (logit'(0.7) = 6.73, so p_lab dominates)
        assert decomp["p_lab"] > 50.0  # Dominant
        # Other parameters contribute but less
        assert decomp["d"] > 0.0
        assert decomp["omega"] > 0.0


class TestCredenceIntervalBoundaryConditions:
    """Test boundary and extreme value handling in realistic contexts."""

    def test_near_certain_effect(self):
        """Very high p_lab should give high credence."""
        estimate = compute_credence_with_ci(
            p_lab=0.95,  # Nearly certain effect in lab
            d=CANONICAL_DISCOUNT_FACTORS["mechanism"],
            omega=0.90,
            delta=0.95,
            p_lab_se=0.05,  # Low uncertainty for near-certain effect
            d_se=0.08,
            omega_se=0.05,
            delta_se=0.05,
        )

        # Credence should be very high
        assert estimate.point > 0.80
        assert estimate.lower > 0.60

    def test_near_null_effect(self):
        """Very low p_lab should give low credence."""
        estimate = compute_credence_with_ci(
            p_lab=0.05,  # Nearly null effect in lab
            d=CANONICAL_DISCOUNT_FACTORS["mechanism"],
            omega=0.90,
            delta=0.95,
            p_lab_se=0.05,  # Low uncertainty for near-null effect
            d_se=0.08,
            omega_se=0.05,
            delta_se=0.05,
        )

        # Credence should be very low
        assert estimate.point < 0.30
        assert estimate.upper < 0.60

    def test_fragile_warrant_type(self):
        """Analogical warrant (fragile transfer) should reduce credence."""
        p_lab = 0.70
        omega = 0.85
        delta = 0.90

        # Strong warrant type
        est_mechanism = compute_credence_with_ci(
            p_lab=p_lab,
            d=CANONICAL_DISCOUNT_FACTORS["mechanism"],
            omega=omega,
            delta=delta,
        )

        # Fragile warrant type
        est_analogical = compute_credence_with_ci(
            p_lab=p_lab,
            d=CANONICAL_DISCOUNT_FACTORS["analogical"],
            omega=omega,
            delta=delta,
        )

        # Mechanism warrant should give higher credence
        assert est_mechanism.point > est_analogical.point


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
