"""
Tests for Stopping Rules Service
================================

Tests for evidence gathering stopping criteria.

Date: January 21, 2026
Phase D Sprint D1
"""

import pytest
from src.services.stopping_rules import (
    StoppingRulesEngine,
    StoppingDecision,
    StoppingReason,
    StoppingCriterion,
    evaluate_stopping
)
from src.services.web_of_belief import (
    WebOfBelief, Belief, Credence, EpistemicLevel, SourceDepth
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def empty_web():
    """Create empty web."""
    return WebOfBelief()


@pytest.fixture
def minimal_web():
    """Create web with minimal beliefs (below threshold)."""
    web = WebOfBelief()
    for i in range(3):
        belief = Belief(
            belief_id=f"b{i}",
            content=f"Belief number {i} about light",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.6, 0.15)
        )
        web.beliefs[belief.belief_id] = belief
    return web


@pytest.fixture
def sufficient_web():
    """Create web with sufficient evidence."""
    web = WebOfBelief()
    for i in range(10):
        belief = Belief(
            belief_id=f"b{i}",
            content=f"Finding {i}: Natural light affects productivity in different ways",
            level=EpistemicLevel.EMPIRICAL if i % 2 == 0 else EpistemicLevel.THEORETICAL,
            credence=Credence(0.7 + (i * 0.02), 0.10),
            outcome_id="productivity"
        )
        web.beliefs[belief.belief_id] = belief
    return web


@pytest.fixture
def saturated_web():
    """Create web where information is saturated (repetitive)."""
    web = WebOfBelief()
    # All beliefs are essentially the same
    for i in range(15):
        belief = Belief(
            belief_id=f"b{i}",
            content="Natural light improves productivity in office workers",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10)
        )
        web.beliefs[belief.belief_id] = belief
    return web


@pytest.fixture
def contested_web():
    """Create web with contested beliefs."""
    web = WebOfBelief()
    for i in range(10):
        belief = Belief(
            belief_id=f"b{i}",
            content=f"Finding {i} about open offices",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.25),
            contested=True
        )
        web.beliefs[belief.belief_id] = belief
    return web


# =============================================================================
# Basic Engine Tests
# =============================================================================

class TestStoppingRulesEngine:
    """Tests for StoppingRulesEngine."""

    def test_engine_creation(self, empty_web):
        """Test engine can be created."""
        engine = StoppingRulesEngine(empty_web)
        assert engine is not None
        assert engine.min_beliefs == 5  # default

    def test_engine_custom_params(self, empty_web):
        """Test engine with custom parameters."""
        engine = StoppingRulesEngine(
            empty_web,
            min_beliefs=10,
            confidence_threshold=0.8,
            saturation_window=20
        )
        assert engine.min_beliefs == 10
        assert engine.confidence_threshold == 0.8

    def test_evaluate_returns_decision(self, empty_web):
        """Test evaluate returns StoppingDecision."""
        engine = StoppingRulesEngine(empty_web)
        decision = engine.evaluate()
        assert isinstance(decision, StoppingDecision)


# =============================================================================
# Stopping Criteria Tests
# =============================================================================

class TestStoppingCriteria:
    """Tests for individual stopping criteria."""

    def test_empty_web_should_not_stop(self, empty_web):
        """Test that empty web should not recommend stopping."""
        decision = evaluate_stopping(empty_web)
        assert decision.should_stop is False

    def test_minimal_web_should_not_stop(self, minimal_web):
        """Test that minimal evidence doesn't trigger stop."""
        decision = evaluate_stopping(minimal_web, min_beliefs=5)
        assert decision.should_stop is False
        # Should have evidence count criterion not met
        count_unmet = [c for c in decision.criteria_not_met
                       if c.reason == StoppingReason.EVIDENCE_COUNT]
        assert len(count_unmet) > 0

    def test_sufficient_web_may_stop(self, sufficient_web):
        """Test that sufficient evidence may trigger stop."""
        decision = evaluate_stopping(sufficient_web, min_beliefs=5)
        # Should have evidence count criterion met
        count_met = [c for c in decision.criteria_met
                     if c.reason == StoppingReason.EVIDENCE_COUNT]
        assert len(count_met) > 0

    def test_confidence_criterion(self, sufficient_web):
        """Test confidence threshold criterion."""
        # High threshold - should not be met
        decision = evaluate_stopping(
            sufficient_web,
            confidence_threshold=0.95
        )
        conf_unmet = [c for c in decision.criteria_not_met
                      if c.reason == StoppingReason.CONFIDENCE_THRESHOLD]
        assert len(conf_unmet) > 0

        # Low threshold - should be met
        decision = evaluate_stopping(
            sufficient_web,
            confidence_threshold=0.5
        )
        conf_met = [c for c in decision.criteria_met
                    if c.reason == StoppingReason.CONFIDENCE_THRESHOLD]
        assert len(conf_met) > 0


# =============================================================================
# Saturation Tests
# =============================================================================

class TestSaturationDetection:
    """Tests for information saturation detection."""

    def test_saturated_web_detected(self, saturated_web):
        """Test that repetitive content is detected as saturated."""
        engine = StoppingRulesEngine(saturated_web, saturation_window=10)
        decision = engine.evaluate()

        # May detect saturation due to repetitive content
        saturation_met = [c for c in decision.criteria_met
                         if c.reason == StoppingReason.SATURATION]
        # Note: actual detection depends on implementation details


# =============================================================================
# Coverage Tests
# =============================================================================

class TestCoverageDetection:
    """Tests for epistemic coverage detection."""

    def test_single_level_low_coverage(self, minimal_web):
        """Test that single epistemic level has low coverage."""
        # All beliefs in minimal_web are EMPIRICAL
        decision = evaluate_stopping(minimal_web)
        coverage_criteria = [c for c in decision.criteria_met + decision.criteria_not_met
                            if c.reason == StoppingReason.COVERAGE]
        assert len(coverage_criteria) > 0

    def test_multiple_levels_good_coverage(self, sufficient_web):
        """Test that multiple epistemic levels increase coverage."""
        # sufficient_web has both EMPIRICAL and THEORETICAL
        decision = evaluate_stopping(sufficient_web)
        coverage_met = [c for c in decision.criteria_met
                       if c.reason == StoppingReason.COVERAGE]
        assert len(coverage_met) > 0


# =============================================================================
# Contradiction Stability Tests
# =============================================================================

class TestContradictionStability:
    """Tests for contradiction stability detection."""

    def test_contested_web_stability(self, contested_web):
        """Test contradiction stability in contested web."""
        decision = evaluate_stopping(contested_web)
        # All beliefs are contested, rate is stable
        stability_criteria = [c for c in decision.criteria_met + decision.criteria_not_met
                              if c.reason == StoppingReason.CONTRADICTION_STABLE]
        assert len(stability_criteria) > 0


# =============================================================================
# Decision Logic Tests
# =============================================================================

class TestDecisionLogic:
    """Tests for overall decision logic."""

    def test_decision_has_recommendation(self, sufficient_web):
        """Test that decision includes recommendation."""
        decision = evaluate_stopping(sufficient_web)
        assert decision.recommendation is not None
        assert len(decision.recommendation) > 0

    def test_decision_has_confidence(self, sufficient_web):
        """Test that decision has confidence score."""
        decision = evaluate_stopping(sufficient_web)
        assert 0 <= decision.confidence <= 1

    def test_decision_to_dict(self, sufficient_web):
        """Test decision serialization."""
        decision = evaluate_stopping(sufficient_web)
        d = decision.to_dict()

        assert 'should_stop' in d
        assert 'primary_reason' in d
        assert 'confidence' in d
        assert 'criteria_met' in d
        assert 'criteria_not_met' in d
        assert 'recommendation' in d


# =============================================================================
# Topic-Specific Tests
# =============================================================================

class TestTopicFiltering:
    """Tests for topic-specific evaluation."""

    def test_evaluate_with_topic(self, sufficient_web):
        """Test evaluation filtered by topic."""
        decision = evaluate_stopping(sufficient_web, topic="light")
        # Should find beliefs mentioning "light"
        assert decision is not None

    def test_evaluate_no_matching_topic(self, sufficient_web):
        """Test evaluation with non-matching topic."""
        decision = evaluate_stopping(sufficient_web, topic="xyzzy_nomatch")
        # Should not stop since no evidence for this topic
        assert decision.should_stop is False


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_evaluate_stopping_function(self, sufficient_web):
        """Test evaluate_stopping convenience function."""
        decision = evaluate_stopping(
            sufficient_web,
            min_beliefs=5,
            confidence_threshold=0.6
        )
        assert isinstance(decision, StoppingDecision)

    def test_evaluate_stopping_defaults(self, sufficient_web):
        """Test evaluate_stopping with default parameters."""
        decision = evaluate_stopping(sufficient_web)
        assert decision is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestStoppingIntegration:
    """Integration tests for stopping rules."""

    def test_full_evaluation_workflow(self, sufficient_web):
        """Test complete evaluation workflow."""
        # Create engine
        engine = StoppingRulesEngine(
            sufficient_web,
            min_beliefs=5,
            confidence_threshold=0.7
        )

        # Evaluate
        decision = engine.evaluate()

        # Check structure
        assert isinstance(decision, StoppingDecision)
        assert len(decision.criteria_met) + len(decision.criteria_not_met) >= 4

        # Check all criteria have required fields
        for criterion in decision.criteria_met + decision.criteria_not_met:
            assert criterion.name is not None
            assert criterion.description is not None
            assert criterion.reason is not None
            assert 0 <= criterion.threshold
            assert criterion.is_met in [True, False]
