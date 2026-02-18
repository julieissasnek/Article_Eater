"""Tests for Evidence Accumulation Engine. Sprint 13 Task 13.3."""

import pytest
import math

from src.cmr.learning.evidence_accumulation import (
    EffectEstimate,
    EvidencePool,
    AccumulatedEvidence,
    accumulate_evidence,
    accumulate_and_propose,
    generate_proposals_from_accumulated,
    compute_fixed_effects_meta,
    compute_heterogeneity,
    format_accumulation_report,
)
from src.cmr.learning.update_proposals import ProposalType


class TestEffectEstimate:
    def test_creates_estimate(self):
        e = EffectEstimate(
            paper_citation="Smith 2024",
            effect_size=0.5,
            sample_n=100,
        )
        assert e.paper_citation == "Smith 2024"
        assert e.effect_size == 0.5
        assert e.sample_n == 100

    def test_get_se_from_provided(self):
        e = EffectEstimate(
            paper_citation="Test",
            effect_size=0.5,
            sample_n=100,
            standard_error=0.1,
        )
        assert e.get_se() == 0.1

    def test_get_se_estimated(self):
        e = EffectEstimate(
            paper_citation="Test",
            effect_size=0.5,
            sample_n=100,
        )
        se = e.get_se()
        # SE should be reasonable for n=100
        assert 0.1 < se < 0.3

    def test_get_weight(self):
        e = EffectEstimate(
            paper_citation="Test",
            effect_size=0.5,
            sample_n=100,
            standard_error=0.2,
        )
        # Weight = 1 / SE^2 = 1 / 0.04 = 25
        assert e.get_weight() == pytest.approx(25.0)

    def test_larger_n_larger_weight(self):
        e_small = EffectEstimate(paper_citation="Small", effect_size=0.5, sample_n=20)
        e_large = EffectEstimate(paper_citation="Large", effect_size=0.5, sample_n=200)
        assert e_large.get_weight() > e_small.get_weight()


class TestEvidencePool:
    def test_creates_pool(self):
        pool = EvidencePool(template_id="VF3", parameter_name="optimal_Rh")
        assert pool.template_id == "VF3"
        assert pool.parameter_name == "optimal_Rh"
        assert len(pool.estimates) == 0

    def test_add_estimate(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        pool.add_estimate(
            paper_citation="Study 1",
            effect_size=0.4,
            sample_n=50,
        )
        assert len(pool.estimates) == 1
        assert pool.estimates[0].paper_citation == "Study 1"

    def test_get_total_n(self):
        pool = EvidencePool(template_id="L1", parameter_name="test")
        pool.add_estimate("Study 1", 0.3, 50)
        pool.add_estimate("Study 2", 0.4, 80)
        pool.add_estimate("Study 3", 0.5, 70)
        assert pool.get_total_n() == 200


class TestComputeFixedEffectsMeta:
    def test_single_study(self):
        estimates = [
            EffectEstimate("Single", 0.5, 100, 0.2)
        ]
        mean, ci_lo, ci_hi, _ = compute_fixed_effects_meta(estimates)
        assert mean == pytest.approx(0.5)
        # CI should be roughly mean ± 1.96 * 0.2
        assert ci_lo == pytest.approx(0.5 - 1.96 * 0.2, rel=0.1)
        assert ci_hi == pytest.approx(0.5 + 1.96 * 0.2, rel=0.1)

    def test_multiple_studies(self):
        estimates = [
            EffectEstimate("Study 1", 0.4, 100, 0.2),
            EffectEstimate("Study 2", 0.6, 100, 0.2),
        ]
        mean, ci_lo, ci_hi, _ = compute_fixed_effects_meta(estimates)
        # Weighted mean should be 0.5 (equal weights)
        assert mean == pytest.approx(0.5, rel=0.01)
        # CI should be narrower with 2 studies
        assert ci_hi - ci_lo < 2 * 1.96 * 0.2

    def test_empty_estimates(self):
        mean, ci_lo, ci_hi, weights = compute_fixed_effects_meta([])
        assert mean == 0.0
        assert ci_lo == 0.0
        assert ci_hi == 0.0
        assert weights == 0.0

    def test_unequal_weights(self):
        # Large study with 0.6, small study with 0.3
        estimates = [
            EffectEstimate("Large", 0.6, 200, 0.1),  # Higher weight
            EffectEstimate("Small", 0.3, 50, 0.3),   # Lower weight
        ]
        mean, _, _, _ = compute_fixed_effects_meta(estimates)
        # Mean should be closer to 0.6 (larger weight)
        assert mean > 0.45


class TestComputeHeterogeneity:
    def test_homogeneous_studies(self):
        estimates = [
            EffectEstimate("Study 1", 0.5, 100, 0.2),
            EffectEstimate("Study 2", 0.5, 100, 0.2),
            EffectEstimate("Study 3", 0.5, 100, 0.2),
        ]
        mean, _, _, _ = compute_fixed_effects_meta(estimates)
        q, i_sq = compute_heterogeneity(estimates, mean)
        # All effects are equal, so Q and I² should be 0
        assert q == pytest.approx(0.0)
        assert i_sq == pytest.approx(0.0)

    def test_heterogeneous_studies(self):
        estimates = [
            EffectEstimate("Study 1", 0.2, 100, 0.2),
            EffectEstimate("Study 2", 0.5, 100, 0.2),
            EffectEstimate("Study 3", 0.8, 100, 0.2),
        ]
        mean, _, _, _ = compute_fixed_effects_meta(estimates)
        q, i_sq = compute_heterogeneity(estimates, mean)
        # Different effects should give high Q and I²
        assert q > 0
        assert i_sq > 0

    def test_single_study(self):
        estimates = [EffectEstimate("Single", 0.5, 100, 0.2)]
        q, i_sq = compute_heterogeneity(estimates, 0.5)
        assert q == 0.0
        assert i_sq == 0.0


class TestAccumulateEvidence:
    def test_empty_pool(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        result = accumulate_evidence(pool, current_value=0.5)
        assert result.n_studies == 0
        assert result.needs_update is False
        assert result.weighted_mean == 0.5

    def test_value_within_ci(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        pool.add_estimate("Study 1", 0.5, 100, 0.1)
        pool.add_estimate("Study 2", 0.5, 100, 0.1)
        result = accumulate_evidence(pool, current_value=0.5)
        assert result.needs_update is False
        assert result.contradiction_detected is False

    def test_value_outside_ci(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        pool.add_estimate("Study 1", 0.8, 100, 0.05)
        pool.add_estimate("Study 2", 0.8, 100, 0.05)
        # Current value far from evidence
        result = accumulate_evidence(pool, current_value=0.3)
        assert result.needs_update is True

    def test_contradiction_detected(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        # Very tight CI around 0.8
        pool.add_estimate("Study 1", 0.8, 500, 0.03)
        pool.add_estimate("Study 2", 0.8, 500, 0.03)
        # Current value very different
        result = accumulate_evidence(pool, current_value=0.2)
        assert result.contradiction_detected is True

    def test_accumulates_individual_estimates(self):
        pool = EvidencePool(template_id="VF3", parameter_name="test")
        pool.add_estimate("Study 1", 0.4, 50)
        pool.add_estimate("Study 2", 0.5, 60)
        pool.add_estimate("Study 3", 0.6, 70)
        result = accumulate_evidence(pool, current_value=0.5)
        assert len(result.individual_estimates) == 3


class TestAccumulatedEvidence:
    def test_to_dict(self):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="optimal_Rh",
            current_value=0.5,
            n_studies=3,
            total_n=200,
            weighted_mean=0.55,
            ci_lower=0.45,
            ci_upper=0.65,
            heterogeneity_q=2.5,
            i_squared=20.0,
            needs_update=False,
            contradiction_detected=False,
        )
        d = acc.to_dict()
        assert d["template_id"] == "VF3"
        assert d["parameter_name"] == "optimal_Rh"
        assert d["weighted_mean"] == 0.55
        assert d["n_studies"] == 3


class TestGenerateProposalsFromAccumulated:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_proposals.db")

    def test_no_proposal_when_not_needed(self, temp_db):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="test",
            current_value=0.5,
            n_studies=2,
            total_n=100,
            weighted_mean=0.5,
            ci_lower=0.4,
            ci_upper=0.6,
            heterogeneity_q=0.0,
            i_squared=0.0,
            needs_update=False,
            contradiction_detected=False,
        )
        proposals = generate_proposals_from_accumulated(acc, temp_db)
        assert len(proposals) == 0

    def test_generates_revision_proposal(self, temp_db):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="test",
            current_value=0.3,
            n_studies=2,
            total_n=100,
            weighted_mean=0.6,
            ci_lower=0.5,
            ci_upper=0.7,
            heterogeneity_q=1.0,
            i_squared=10.0,
            needs_update=True,
            contradiction_detected=False,
            individual_estimates=[
                EffectEstimate("Study 1", 0.55, 50),
                EffectEstimate("Study 2", 0.65, 50),
            ],
        )
        proposals = generate_proposals_from_accumulated(acc, temp_db)
        assert len(proposals) == 1
        assert proposals[0].proposal_type == ProposalType.BOUNDARY_REVISION

    def test_generates_contradiction_proposal(self, temp_db):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="test",
            current_value=0.2,
            n_studies=2,
            total_n=200,
            weighted_mean=0.8,
            ci_lower=0.75,
            ci_upper=0.85,
            heterogeneity_q=1.0,
            i_squared=10.0,
            needs_update=True,
            contradiction_detected=True,
            individual_estimates=[
                EffectEstimate("Contradicting Study", 0.8, 100),
            ],
        )
        proposals = generate_proposals_from_accumulated(acc, temp_db)
        assert len(proposals) == 1
        assert proposals[0].proposal_type == ProposalType.CONTRADICTION_FLAG


class TestAccumulateAndPropose:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_full.db")

    def test_convenience_function(self, temp_db):
        studies = [
            {"paper_citation": "Smith 2024", "effect_size": 0.5, "sample_n": 100},
            {"paper_citation": "Jones 2024", "effect_size": 0.6, "sample_n": 80},
        ]
        acc, proposals = accumulate_and_propose(
            template_id="VF3",
            parameter_name="optimal_Rh",
            current_value=0.55,
            studies=studies,
            db_path=temp_db,
        )
        assert isinstance(acc, AccumulatedEvidence)
        assert acc.n_studies == 2
        assert acc.total_n == 180

    def test_generates_proposal_when_needed(self, temp_db):
        studies = [
            {"paper_citation": "Study 1", "effect_size": 0.8, "sample_n": 100, "se": 0.05},
            {"paper_citation": "Study 2", "effect_size": 0.8, "sample_n": 100, "se": 0.05},
        ]
        acc, proposals = accumulate_and_propose(
            template_id="VF3",
            parameter_name="test",
            current_value=0.3,  # Far from evidence
            studies=studies,
            db_path=temp_db,
        )
        assert acc.needs_update is True
        assert len(proposals) >= 1


class TestFormatAccumulationReport:
    def test_formats_report(self):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="optimal_Rh",
            current_value=0.5,
            n_studies=3,
            total_n=250,
            weighted_mean=0.55,
            ci_lower=0.48,
            ci_upper=0.62,
            heterogeneity_q=3.2,
            i_squared=25.0,
            needs_update=False,
            contradiction_detected=False,
            individual_estimates=[
                EffectEstimate("Smith 2024", 0.52, 80),
                EffectEstimate("Jones 2024", 0.58, 90),
                EffectEstimate("Brown 2024", 0.55, 80),
            ],
        )
        report = format_accumulation_report(acc)
        assert "VF3" in report
        assert "optimal_Rh" in report
        assert "Studies: 3" in report
        assert "Total N: 250" in report
        assert "Smith 2024" in report
        assert "WITHIN 95% CI" in report

    def test_shows_outside_ci(self):
        acc = AccumulatedEvidence(
            template_id="L1",
            parameter_name="test",
            current_value=0.2,
            n_studies=2,
            total_n=100,
            weighted_mean=0.6,
            ci_lower=0.5,
            ci_upper=0.7,
            heterogeneity_q=1.0,
            i_squared=10.0,
            needs_update=True,
            contradiction_detected=False,
        )
        report = format_accumulation_report(acc)
        assert "OUTSIDE 95% CI" in report
        assert "UPDATE RECOMMENDED" in report

    def test_shows_contradiction(self):
        acc = AccumulatedEvidence(
            template_id="VIEW1",
            parameter_name="test",
            current_value=0.1,
            n_studies=2,
            total_n=100,
            weighted_mean=0.9,
            ci_lower=0.85,
            ci_upper=0.95,
            heterogeneity_q=0.5,
            i_squared=5.0,
            needs_update=True,
            contradiction_detected=True,
        )
        report = format_accumulation_report(acc)
        assert "CONTRADICTION DETECTED" in report

    def test_shows_high_heterogeneity(self):
        acc = AccumulatedEvidence(
            template_id="VF3",
            parameter_name="test",
            current_value=0.5,
            n_studies=3,
            total_n=150,
            weighted_mean=0.5,
            ci_lower=0.3,
            ci_upper=0.7,
            heterogeneity_q=15.0,
            i_squared=80.0,
            needs_update=False,
            contradiction_detected=False,
        )
        report = format_accumulation_report(acc)
        assert "High heterogeneity" in report
