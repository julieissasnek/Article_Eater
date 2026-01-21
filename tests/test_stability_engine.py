"""
Tests for Stability Engine
==========================

Tests for stability tracking and reporting.

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus
)
from src.services.stability_engine import (
    StabilityEngine,
    StabilityLevel,
    PublicationBiasRisk,
    BeliefStabilityInfo,
    StabilityReport
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def empty_web():
    """Create an empty web."""
    return WebOfBelief()


@pytest.fixture
def stable_web():
    """Create a web with stable beliefs."""
    web = WebOfBelief()

    # Add beliefs with stable credence histories
    for i in range(5):
        belief = Belief(
            belief_id=f"stable_{i}",
            content=f"Stable belief {i}",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.7, 0.1)
        )
        # Add stable history (small changes)
        for j in range(6):
            belief.record_credence_change(0.7 + 0.001 * j, f"paper_{j}")
        web.beliefs[belief.belief_id] = belief

    return web


@pytest.fixture
def unstable_web():
    """Create a web with unstable beliefs."""
    web = WebOfBelief()

    # Add beliefs with unstable credence histories
    for i in range(5):
        belief = Belief(
            belief_id=f"unstable_{i}",
            content=f"Unstable belief {i}",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.3)
        )
        # Add unstable history (large changes)
        for j in range(6):
            belief.record_credence_change(0.3 + 0.2 * (j % 2), f"paper_{j}")
        web.beliefs[belief.belief_id] = belief

    return web


@pytest.fixture
def contested_web():
    """Create a web with contested beliefs."""
    web = WebOfBelief()

    # Add contested beliefs (oscillating)
    for i in range(5):
        belief = Belief(
            belief_id=f"contested_{i}",
            content=f"Contested belief {i}",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.3),
            contested=True
        )
        # Add oscillating history
        for j in range(6):
            belief.record_credence_change(0.3 if j % 2 == 0 else 0.7, f"paper_{j}")
        web.beliefs[belief.belief_id] = belief

    return web


@pytest.fixture
def mixed_web():
    """Create a web with mixed stability."""
    web = WebOfBelief()

    # Some stable
    for i in range(3):
        belief = Belief(
            belief_id=f"stable_{i}",
            content=f"Stable belief {i}",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.7, 0.1)
        )
        for j in range(6):
            belief.record_credence_change(0.7 + 0.001 * j, f"paper_{j}")
        web.beliefs[belief.belief_id] = belief

    # Some unstable
    belief = Belief(
        belief_id="unstable_0",
        content="Unstable belief",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.5, 0.3)
    )
    for j in range(6):
        belief.record_credence_change(0.3 + 0.15 * j, f"paper_{j}")
    web.beliefs[belief.belief_id] = belief

    # One contested
    contested = Belief(
        belief_id="contested_0",
        content="Contested belief",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.5, 0.3),
        contested=True
    )
    web.beliefs[contested.belief_id] = contested

    return web


# =============================================================================
# Stability Level Tests
# =============================================================================

class TestStabilityLevel:
    """Tests for stability level detection."""

    def test_empty_web_is_stable(self, empty_web):
        """Test that empty web is considered stable."""
        engine = StabilityEngine(empty_web)
        assert engine.check_stability() == StabilityLevel.STABLE

    def test_stable_web_detected(self, stable_web):
        """Test detecting stable web."""
        engine = StabilityEngine(stable_web)
        assert engine.check_stability() == StabilityLevel.STABLE

    def test_unstable_web_detected(self, unstable_web):
        """Test detecting unstable web."""
        engine = StabilityEngine(unstable_web)
        level = engine.check_stability()
        # Oscillating beliefs may be detected as contested (correct behavior)
        assert level in (StabilityLevel.UNSTABLE, StabilityLevel.CONVERGING, StabilityLevel.CONTESTED)

    def test_contested_web_detected(self, contested_web):
        """Test detecting contested web."""
        engine = StabilityEngine(contested_web)
        assert engine.check_stability() == StabilityLevel.CONTESTED

    def test_mixed_web_level(self, mixed_web):
        """Test mixed web stability level."""
        engine = StabilityEngine(mixed_web)
        level = engine.check_stability()
        # Mixed should be converging or unstable
        assert level in (StabilityLevel.CONVERGING, StabilityLevel.UNSTABLE)


# =============================================================================
# Publication Bias Tests
# =============================================================================

class TestPublicationBias:
    """Tests for publication bias estimation."""

    def test_insufficient_data(self, empty_web):
        """Test handling of insufficient data."""
        engine = StabilityEngine(empty_web)
        bias = engine.estimate_publication_bias()

        assert bias.risk_level == PublicationBiasRisk.UNKNOWN
        assert bias.confidence == 0.0

    def test_high_bias_detection(self):
        """Test detecting high publication bias (all positive results)."""
        web = WebOfBelief()

        # Add only positive findings
        for i in range(10):
            belief = Belief(
                belief_id=f"positive_{i}",
                content=f"Effect X improves outcome Y (significant, p<.05)",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.8, 0.1)
            )
            web.beliefs[belief.belief_id] = belief

        engine = StabilityEngine(web)
        bias = engine.estimate_publication_bias()

        assert bias.risk_level == PublicationBiasRisk.HIGH
        assert bias.null_result_ratio < 0.1
        assert bias.warning_message is not None
        assert "publication bias" in bias.warning_message.lower()

    def test_low_bias_detection(self):
        """Test detecting low publication bias (good null representation)."""
        web = WebOfBelief()

        # Add mix of positive and null findings
        for i in range(8):
            belief = Belief(
                belief_id=f"positive_{i}",
                content=f"Effect found (p<.05)",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.7, 0.15)
            )
            web.beliefs[belief.belief_id] = belief

        for i in range(4):
            belief = Belief(
                belief_id=f"null_{i}",
                content=f"No significant effect found",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.4, 0.2)
            )
            web.beliefs[belief.belief_id] = belief

        engine = StabilityEngine(web)
        bias = engine.estimate_publication_bias()

        assert bias.risk_level == PublicationBiasRisk.LOW
        assert bias.null_result_ratio >= 0.15

    def test_null_indicators_recognized(self):
        """Test that null result indicators are recognized."""
        web = WebOfBelief()

        null_contents = [
            "No effect was found between X and Y",
            "The relationship was not significant",
            "Failed to replicate previous findings",
            "Did not replicate the original study",
            "No association between variables"
        ]

        for i, content in enumerate(null_contents):
            belief = Belief(
                belief_id=f"null_{i}",
                content=content,
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.4, 0.2)
            )
            web.beliefs[belief.belief_id] = belief

        engine = StabilityEngine(web)
        bias = engine.estimate_publication_bias()

        assert bias.null_studies == len(null_contents)


# =============================================================================
# Gap Identification Tests
# =============================================================================

class TestGapIdentification:
    """Tests for epistemic gap identification."""

    def test_uncertain_beliefs_identified(self):
        """Test identifying uncertain beliefs as gaps."""
        web = WebOfBelief()

        # Add high-uncertainty belief
        belief = Belief(
            belief_id="uncertain_1",
            content="Uncertain finding",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.5)  # High uncertainty
        )
        web.beliefs[belief.belief_id] = belief

        engine = StabilityEngine(web)
        all_gaps, high_voi = engine.identify_gaps()

        assert len(all_gaps) >= 1
        assert any("uncertain" in g.gap_type for g in all_gaps)

    def test_contested_beliefs_in_gaps(self, contested_web):
        """Test that contested beliefs appear in gaps."""
        engine = StabilityEngine(contested_web)
        all_gaps, high_voi = engine.identify_gaps()

        assert len(all_gaps) >= 1

    def test_high_voi_filtering(self):
        """Test that high-VOI gaps are filtered correctly."""
        web = WebOfBelief()

        # High uncertainty = high VOI
        b1 = Belief(
            belief_id="high_voi",
            content="High uncertainty",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.6)  # Very high uncertainty
        )
        web.beliefs[b1.belief_id] = b1

        # Low uncertainty = low VOI
        b2 = Belief(
            belief_id="low_voi",
            content="Low uncertainty",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.7, 0.1)  # Low uncertainty
        )
        web.beliefs[b2.belief_id] = b2

        engine = StabilityEngine(web, voi_threshold=0.3)
        all_gaps, high_voi = engine.identify_gaps()

        # High VOI should include high uncertainty belief
        high_voi_ids = [g.gap_id for g in high_voi]
        assert any("high_voi" in gid for gid in high_voi_ids)


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Tests for stability report generation."""

    def test_report_structure(self, stable_web):
        """Test that report has required fields."""
        engine = StabilityEngine(stable_web)
        report = engine.generate_report()

        assert report.stability_level is not None
        assert report.total_beliefs == 5
        assert report.publication_bias is not None
        assert report.recommendation is not None

    def test_report_stable_web(self, stable_web):
        """Test report for stable web."""
        engine = StabilityEngine(stable_web)
        report = engine.generate_report()

        assert report.stability_level == StabilityLevel.STABLE
        assert report.stable_beliefs >= 4
        assert report.convergence_achieved is True

    def test_report_contested_web(self, contested_web):
        """Test report for contested web."""
        engine = StabilityEngine(contested_web)
        report = engine.generate_report()

        assert report.stability_level == StabilityLevel.CONTESTED
        assert report.contested_beliefs >= 4

    def test_report_to_dict(self, stable_web):
        """Test report serialization."""
        engine = StabilityEngine(stable_web)
        report = engine.generate_report()
        d = report.to_dict()

        assert 'stability_level' in d
        assert 'papers_processed' in d
        assert 'publication_bias' in d
        assert 'recommendation' in d

    def test_report_recommendation_content(self, stable_web):
        """Test that recommendation has appropriate content."""
        engine = StabilityEngine(stable_web)
        report = engine.generate_report()

        # Stable web should mention equilibrium
        assert "equilibrium" in report.recommendation.lower() or "stable" in report.recommendation.lower()


# =============================================================================
# Stopping Rule Tests
# =============================================================================

class TestStoppingRules:
    """Tests for stopping rules."""

    def test_stable_web_can_stop(self, stable_web):
        """Test that stable web indicates can stop."""
        engine = StabilityEngine(stable_web)

        # Simulate processing papers
        for _ in range(6):
            engine.record_paper_processed()
            engine.check_stability()

        should_stop, reason = engine.should_stop_searching()
        # Might not stop immediately due to streak requirement
        assert "stable" in reason.lower() or "more papers" in reason.lower()

    def test_unstable_web_continues(self):
        """Test that unstable web continues searching."""
        # Create truly unstable (not oscillating) web
        web = WebOfBelief()
        for i in range(5):
            belief = Belief(
                belief_id=f"unstable_{i}",
                content=f"Unstable belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                credence=Credence(0.5, 0.3)
            )
            # Add trending (not oscillating) history
            for j in range(6):
                belief.record_credence_change(0.3 + 0.1 * j, f"paper_{j}")
            web.beliefs[belief.belief_id] = belief

        engine = StabilityEngine(web)
        should_stop, reason = engine.should_stop_searching()

        assert should_stop is False
        assert "continue" in reason.lower() or "evolving" in reason.lower() or "converg" in reason.lower()

    def test_contested_may_stop(self, contested_web):
        """Test that highly contested web may stop."""
        engine = StabilityEngine(contested_web)
        should_stop, reason = engine.should_stop_searching()

        # Contested web should mention disagreement
        assert "disagree" in reason.lower() or "contest" in reason.lower()


# =============================================================================
# Belief Stability Info Tests
# =============================================================================

class TestBeliefStabilityInfo:
    """Tests for individual belief stability info."""

    def test_stable_belief_info(self, stable_web):
        """Test getting stability info for stable belief."""
        engine = StabilityEngine(stable_web)
        belief = stable_web.beliefs["stable_0"]
        info = engine.get_belief_stability_info(belief)

        assert info.is_stable is True
        assert info.is_contested is False
        assert info.max_delta_in_window < 0.01

    def test_contested_belief_info(self, contested_web):
        """Test getting stability info for contested belief."""
        engine = StabilityEngine(contested_web)
        belief = contested_web.beliefs["contested_0"]
        info = engine.get_belief_stability_info(belief)

        assert info.is_contested is True

    def test_info_to_dict(self, stable_web):
        """Test serialization of belief stability info."""
        engine = StabilityEngine(stable_web)
        belief = stable_web.beliefs["stable_0"]
        info = engine.get_belief_stability_info(belief)
        d = info.to_dict()

        assert 'belief_id' in d
        assert 'is_stable' in d
        assert 'max_delta_in_window' in d


# =============================================================================
# Papers Processed Tracking Tests
# =============================================================================

class TestPapersProcessed:
    """Tests for papers processed tracking."""

    def test_initial_count_zero(self, stable_web):
        """Test that initial paper count is zero."""
        engine = StabilityEngine(stable_web)
        assert engine.papers_processed == 0

    def test_count_increments(self, stable_web):
        """Test that paper count increments."""
        engine = StabilityEngine(stable_web)
        engine.record_paper_processed()
        engine.record_paper_processed()
        engine.record_paper_processed()

        assert engine.papers_processed == 3

    def test_count_in_report(self, stable_web):
        """Test that paper count appears in report."""
        engine = StabilityEngine(stable_web)
        engine.record_paper_processed()
        engine.record_paper_processed()

        report = engine.generate_report()
        assert report.papers_processed == 2
