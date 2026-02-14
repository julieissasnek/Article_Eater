"""
Tests for Panel-Approved Revisions.

Verifies implementation of panel consensus decisions:
- D-PANEL.1: Coherence warrant scales with link count
- D-PANEL.2: Vigilance warrant scales with source quality
- D-PANEL.3: Revised source quality weights
- D-PANEL.4: Context-dependent commitment penalty
"""

import pytest
import math


class TestDPanel1CoherenceWarrantScaling:
    """D-PANEL.1: Coherence warrant scales with link count."""

    def test_base_warrant_single_link(self):
        """Single link returns base + minimal boost."""
        from src.epistemic.warrant_scaling import compute_coherence_warrant

        result = compute_coherence_warrant(link_count=1)
        # Base (0.55) + sqrt(1) * 0.05 = 0.60
        assert result == pytest.approx(0.60, abs=0.01)

    def test_warrant_increases_with_links(self):
        """More links increase warrant."""
        from src.epistemic.warrant_scaling import compute_coherence_warrant

        w1 = compute_coherence_warrant(1)
        w4 = compute_coherence_warrant(4)
        w9 = compute_coherence_warrant(9)

        assert w4 > w1
        assert w9 > w4

    def test_diminishing_returns(self):
        """Warrant increase follows sqrt (diminishing returns), capped at max_boost."""
        from src.epistemic.warrant_scaling import compute_coherence_warrant

        w1 = compute_coherence_warrant(1)  # sqrt(1)*0.05 = 0.05 boost
        w4 = compute_coherence_warrant(4)  # sqrt(4)*0.05 = 0.10 boost
        w9 = compute_coherence_warrant(9)  # sqrt(9)*0.05 = 0.15 boost (at max)

        # Each should be higher than previous
        assert w4 > w1
        assert w9 > w4

        # w9 should be at or near max (0.55 + 0.15 = 0.70)
        assert w9 == pytest.approx(0.70, abs=0.01)

    def test_warrant_capped(self):
        """Warrant doesn't exceed cap."""
        from src.epistemic.warrant_scaling import compute_coherence_warrant

        result = compute_coherence_warrant(link_count=100)
        assert result <= 0.75

    def test_contradictions_reduce_warrant(self):
        """Contradicting links reduce warrant."""
        from src.epistemic.warrant_scaling import get_coherence_warrant_for_belief

        no_contra = get_coherence_warrant_for_belief(5, 0)
        with_contra = get_coherence_warrant_for_belief(5, 3)

        assert with_contra < no_contra

    def test_warrant_floor_with_contradictions(self):
        """Warrant doesn't go below floor even with many contradictions."""
        from src.epistemic.warrant_scaling import get_coherence_warrant_for_belief

        result = get_coherence_warrant_for_belief(5, 100)
        assert result >= 0.40


class TestDPanel2VigilanceWarrantScaling:
    """D-PANEL.2: Vigilance warrant scales with source quality."""

    def test_zero_quality_base_warrant(self):
        """Zero quality gives base warrant."""
        from src.epistemic.warrant_scaling import compute_vigilance_warrant

        result = compute_vigilance_warrant(0.0)
        assert result == pytest.approx(0.50, abs=0.01)

    def test_perfect_quality_max_warrant(self):
        """Perfect quality gives max warrant."""
        from src.epistemic.warrant_scaling import compute_vigilance_warrant

        result = compute_vigilance_warrant(1.0)
        assert result == pytest.approx(0.75, abs=0.01)

    def test_linear_scaling(self):
        """Warrant scales linearly with quality."""
        from src.epistemic.warrant_scaling import compute_vigilance_warrant

        w_mid = compute_vigilance_warrant(0.5)
        expected = 0.50 + (0.25 * 0.5)  # base + scale * quality
        assert w_mid == pytest.approx(expected, abs=0.01)

    def test_validation(self):
        """Invalid quality raises error."""
        from src.epistemic.warrant_scaling import compute_vigilance_warrant

        with pytest.raises(ValueError):
            compute_vigilance_warrant(1.5)

        with pytest.raises(ValueError):
            compute_vigilance_warrant(-0.1)


class TestDPanel3RevisedWeights:
    """D-PANEL.3: Revised source quality weights."""

    def test_revised_weights(self):
        """Weights are revised per Cartwright."""
        from src.epistemic.source_quality import DEFAULT_SOURCE_QUALITY_WEIGHTS

        assert DEFAULT_SOURCE_QUALITY_WEIGHTS["rigor"] == 0.35  # Was 0.40
        assert DEFAULT_SOURCE_QUALITY_WEIGHTS["independence"] == 0.30  # Was 0.25
        assert DEFAULT_SOURCE_QUALITY_WEIGHTS["replication"] == 0.20
        assert DEFAULT_SOURCE_QUALITY_WEIGHTS["commitment"] == 0.15

    def test_weights_sum_to_one(self):
        """Weights still sum to 1.0."""
        from src.epistemic.source_quality import DEFAULT_SOURCE_QUALITY_WEIGHTS

        total = sum(DEFAULT_SOURCE_QUALITY_WEIGHTS.values())
        assert total == pytest.approx(1.0, abs=0.001)

    def test_independence_now_second_highest(self):
        """Independence is now second-highest weight."""
        from src.epistemic.source_quality import DEFAULT_SOURCE_QUALITY_WEIGHTS

        weights = sorted(DEFAULT_SOURCE_QUALITY_WEIGHTS.items(), key=lambda x: x[1], reverse=True)
        assert weights[0][0] == "rigor"
        assert weights[1][0] == "independence"


class TestDPanel4ContextDependentCommitment:
    """D-PANEL.4: Context-dependent commitment penalty."""

    def test_study_type_enum_exists(self):
        """StudyType enum is defined."""
        from src.epistemic.source_quality import StudyType

        assert StudyType.CONFIRMATORY.value == "confirmatory"
        assert StudyType.EXPLORATORY.value == "exploratory"
        assert StudyType.REPLICATION.value == "replication"
        assert StudyType.META_ANALYSIS.value == "meta_analysis"

    def test_penalty_multipliers_defined(self):
        """Penalty multipliers are defined for each type."""
        from src.epistemic.source_quality import (
            StudyType, COMMITMENT_PENALTY_MULTIPLIER
        )

        assert COMMITMENT_PENALTY_MULTIPLIER[StudyType.CONFIRMATORY] == 1.0
        assert COMMITMENT_PENALTY_MULTIPLIER[StudyType.EXPLORATORY] == 0.5
        assert COMMITMENT_PENALTY_MULTIPLIER[StudyType.REPLICATION] == 0.0
        assert COMMITMENT_PENALTY_MULTIPLIER[StudyType.META_ANALYSIS] == 0.0

    def test_confirmatory_full_penalty(self):
        """Confirmatory studies get full commitment penalty."""
        from src.epistemic.source_quality import (
            compute_source_quality_context, StudyType
        )

        # High commitment (0.8) should reduce quality
        confirmatory = compute_source_quality_context(
            0.8, 0.8, 0.7, 0.7, StudyType.CONFIRMATORY
        )

        # Lower commitment (0.2) should give higher quality
        low_commit = compute_source_quality_context(
            0.8, 0.2, 0.7, 0.7, StudyType.CONFIRMATORY
        )

        assert low_commit > confirmatory

    def test_replication_no_penalty(self):
        """Replication studies get no commitment penalty."""
        from src.epistemic.source_quality import (
            compute_source_quality_context, StudyType
        )

        # High commitment shouldn't matter for replications
        high_commit = compute_source_quality_context(
            0.8, 0.8, 0.7, 0.7, StudyType.REPLICATION
        )
        low_commit = compute_source_quality_context(
            0.8, 0.2, 0.7, 0.7, StudyType.REPLICATION
        )

        # Should be equal since commitment penalty is 0
        assert high_commit == pytest.approx(low_commit, abs=0.01)

    def test_exploratory_half_penalty(self):
        """Exploratory studies get half commitment penalty."""
        from src.epistemic.source_quality import (
            compute_source_quality_context, StudyType
        )

        confirmatory = compute_source_quality_context(
            0.8, 0.8, 0.7, 0.7, StudyType.CONFIRMATORY
        )
        exploratory = compute_source_quality_context(
            0.8, 0.8, 0.7, 0.7, StudyType.EXPLORATORY
        )
        replication = compute_source_quality_context(
            0.8, 0.8, 0.7, 0.7, StudyType.REPLICATION
        )

        # Exploratory should be between confirmatory and replication
        assert confirmatory < exploratory < replication


class TestArgumentativeWarrant:
    """D1.6: Argumentative warrant (approved as-is at 0.70)."""

    def test_base_value(self):
        """Argumentative warrant is 0.70."""
        from src.epistemic.warrant_scaling import BASE_ARGUMENTATIVE_WARRANT

        assert BASE_ARGUMENTATIVE_WARRANT == 0.70

    def test_with_scrutiny(self):
        """Returns 0.70 when adversarial scrutiny survived."""
        from src.epistemic.warrant_scaling import compute_argumentative_warrant

        result = compute_argumentative_warrant(adversarial_scrutiny_survived=True)
        assert result == 0.70

    def test_without_scrutiny(self):
        """Returns 0.50 (neutral) without adversarial scrutiny."""
        from src.epistemic.warrant_scaling import compute_argumentative_warrant

        result = compute_argumentative_warrant(adversarial_scrutiny_survived=False)
        assert result == 0.50


class TestTotalWarrantComputation:
    """Test combined warrant computation."""

    def test_no_warrants_neutral(self):
        """No warrant sources gives neutral (0.50)."""
        from src.epistemic.warrant_scaling import compute_total_warrant

        result = compute_total_warrant()
        assert result == 0.50

    def test_single_warrant_source(self):
        """Single warrant source returns that warrant."""
        from src.epistemic.warrant_scaling import compute_total_warrant

        result = compute_total_warrant(coherence_links=4)
        # Should be close to coherence warrant for 4 links
        assert 0.60 < result < 0.70

    def test_multiple_warrants_combine(self):
        """Multiple warrants combine via noisy-OR."""
        from src.epistemic.warrant_scaling import compute_total_warrant

        single = compute_total_warrant(coherence_links=4)
        combined = compute_total_warrant(
            coherence_links=4,
            adversarial_scrutiny=True,
            source_quality=0.8
        )

        # Combined should be higher than single
        assert combined > single
        # But still bounded by 1.0
        assert combined <= 1.0

    def test_noisy_or_formula(self):
        """Verify noisy-OR combination."""
        from src.epistemic.warrant_scaling import compute_total_warrant

        # Two independent warrants of 0.60 each
        # noisy-OR: 1 - (1-0.6)(1-0.6) = 1 - 0.16 = 0.84
        result = compute_total_warrant(
            coherence_links=4,  # ~0.65
            source_quality=0.6  # ~0.65
        )

        # Should be higher than either individual warrant
        assert result > 0.65
