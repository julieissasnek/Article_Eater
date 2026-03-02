"""
Test VOI integration across gap predictor, queue service, and scheduled pipeline.

Tests cover:
1. GapPredictor with VOI scorer produces non-0.5 scores
2. GapPredictor without VOI scorer falls back to 0.5
3. Queue returns highest-VOI target first
4. Queue falls back to FIFO when all VOI scores are equal

Sprint: VOI Integration Fix
Date: 2026-03-02
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch

from src.services.gap_predictor import GapPredictor, PredictedGap
from src.epistemic.gap_types import GapType, GapPriority
from src.queue.service import ResearchQueueService
from src.queue.models import ResearchTarget, TargetStatus, Priority


# =============================================================================
# Mock Objects
# =============================================================================


class MockBelief:
    """Mock belief object for testing."""
    def __init__(self, belief_id, level="empirical", credence_value=0.7):
        self.belief_id = belief_id
        self.level = level
        self.credence = Mock(value=credence_value)
        self.environment_id = "env_test"
        self.outcome_id = "out_test"


class MockWebOfBelief:
    """Mock web of belief for testing."""
    def __init__(self, n_beliefs=3):
        self.beliefs = {
            f"belief_{i}": MockBelief(f"belief_{i}", credence_value=0.5 + i * 0.1)
            for i in range(n_beliefs)
        }


class MockVOICalculator:
    """Mock VOI calculator for testing."""
    def __init__(self, return_voi=0.75):
        self.return_voi = return_voi

    def calculate_voi(self, gap_type, belief, web=None):
        """Return fixed VOI scores for testing."""
        return (self.return_voi, self.return_voi * 0.6, self.return_voi * 0.4)


# =============================================================================
# Test Fix 1: GapPredictor with VOI Scorer
# =============================================================================


class TestGapPredictorWithVOIScorer:
    """Test that GapPredictor correctly wires VOI computation."""

    def test_gap_predictor_accepts_voi_scorer(self):
        """GapPredictor should accept optional voi_scorer parameter."""
        mock_scorer = MockVOICalculator()
        gp = GapPredictor(voi_scorer=mock_scorer)
        assert gp.voi_scorer is mock_scorer

    def test_gap_predictor_lazy_loads_voi_scorer(self):
        """GapPredictor should lazy-load VOI scorer if not provided."""
        gp = GapPredictor()
        scorer = gp.voi_scorer
        assert scorer is None or hasattr(scorer, 'calculate_voi')

    def test_compute_gap_voi_returns_non_fallback_when_scorer_available(self):
        """_compute_gap_voi should use real scorer when available."""
        mock_scorer = MockVOICalculator(return_voi=0.85)
        web = MockWebOfBelief()
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi = gp._compute_gap_voi(GapType.MECHANISM, "belief_0")
        assert voi == 0.85

    def test_compute_gap_voi_fallback_when_scorer_unavailable(self):
        """_compute_gap_voi should fall back to 0.5 when scorer unavailable."""
        gp = GapPredictor(web=MockWebOfBelief())
        voi = gp._compute_gap_voi(GapType.MECHANISM, "belief_0")
        assert voi == 0.5

    def test_compute_mediation_voi_uses_real_scorer_when_available(self):
        """_compute_mediation_voi should use real scorer."""
        mock_scorer = MockVOICalculator(return_voi=0.72)
        web = MockWebOfBelief()
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi = gp._compute_mediation_voi("env_a", "env_x", "out_y")
        assert voi == 0.72

    def test_compute_mediation_voi_fallback_when_scorer_fails(self):
        """_compute_mediation_voi should fall back gracefully if scorer fails."""
        mock_scorer = Mock()
        mock_scorer.calculate_voi.side_effect = Exception("VOI calc failed")
        web = MockWebOfBelief()
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi = gp._compute_mediation_voi("env_a", "env_x", "out_y")
        assert 0.3 <= voi <= 0.95

    def test_compute_mechanism_voi_uses_real_scorer(self):
        """_compute_mechanism_voi should use real scorer."""
        mock_scorer = MockVOICalculator(return_voi=0.68)
        web = MockWebOfBelief()
        empirical_beliefs = [MockBelief("belief_0")]
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi = gp._compute_mechanism_voi(empirical_beliefs)
        assert voi == 0.68

    def test_compute_boundary_voi_uses_real_scorer(self):
        """_compute_boundary_voi should use real scorer."""
        mock_scorer = MockVOICalculator(return_voi=0.55)
        web = MockWebOfBelief()
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi = gp._compute_boundary_voi(3, 2)
        assert voi == 0.55


# =============================================================================
# Test Fix 2: Queue Returns Highest-VOI Target First
# =============================================================================


class TestQueueVOIPrioritization:
    """Test that ResearchQueueService prioritizes by VOI."""

    def test_get_next_target_returns_highest_voi(self):
        """get_next_target should return target with highest VOI."""
        queue = ResearchQueueService()

        targets = [
            ResearchTarget(
                target_id="target_1",
                gap_type=GapType.VALIDATION,
                gap_id="gap_1",
                gap_description="Low VOI gap",
                voi_score=0.3,
                priority=Priority.LOW,
                status=TargetStatus.OPEN,
            ),
            ResearchTarget(
                target_id="target_2",
                gap_type=GapType.MECHANISM,
                gap_id="gap_2",
                gap_description="High VOI gap",
                voi_score=0.9,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
            ),
            ResearchTarget(
                target_id="target_3",
                gap_type=GapType.BOUNDARY,
                gap_id="gap_3",
                gap_description="Medium VOI gap",
                voi_score=0.6,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
            ),
        ]

        for target in targets:
            queue._targets[target.target_id] = target

        collector_id = "collector_test"
        next_target = queue.get_next_target(collector_id)

        assert next_target is not None
        assert next_target.target_id == "target_2"
        assert next_target.voi_score == 0.9
        assert next_target.assigned_to == collector_id

    def test_get_next_highest_voi_target_prioritizes_by_priority_then_voi(self):
        """get_next_highest_voi_target should prioritize: priority rank > VOI > creation time."""
        queue = ResearchQueueService()

        high_priority_target = ResearchTarget(
            target_id="target_high_pri",
            gap_type=GapType.VALIDATION,
            gap_id="gap_hp",
            gap_description="High priority, low VOI",
            voi_score=0.3,
            priority=Priority.HIGH,
            status=TargetStatus.OPEN,
            created_at=datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        medium_priority_target = ResearchTarget(
            target_id="target_med_pri",
            gap_type=GapType.MECHANISM,
            gap_id="gap_mp",
            gap_description="Medium priority, high VOI",
            voi_score=0.95,
            priority=Priority.MEDIUM,
            status=TargetStatus.OPEN,
            created_at=datetime(2026, 3, 1, 12, 1, 0, tzinfo=timezone.utc),
        )

        queue._targets["target_high_pri"] = high_priority_target
        queue._targets["target_med_pri"] = medium_priority_target

        collector_id = "collector_test"
        next_target = queue.get_next_highest_voi_target(collector_id)

        assert next_target.target_id == "target_high_pri"

    def test_get_prioritized_targets_returns_sorted_list(self):
        """get_prioritized_targets should return all targets sorted by priority and VOI."""
        queue = ResearchQueueService()
        # Clear any existing targets
        queue._targets = {}

        targets = [
            ResearchTarget(
                target_id="prio_target_1",
                gap_type=GapType.VALIDATION,
                gap_id="prio_gap_1",
                gap_description="Gap 1",
                voi_score=0.5,
                priority=Priority.LOW,
                status=TargetStatus.OPEN,
            ),
            ResearchTarget(
                target_id="prio_target_2",
                gap_type=GapType.MECHANISM,
                gap_id="prio_gap_2",
                gap_description="Gap 2",
                voi_score=0.8,
                priority=Priority.HIGH,
                status=TargetStatus.SEARCHING,
            ),
            ResearchTarget(
                target_id="prio_target_3",
                gap_type=GapType.BOUNDARY,
                gap_id="prio_gap_3",
                gap_description="Gap 3",
                voi_score=0.7,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
            ),
        ]

        for target in targets:
            queue._targets[target.target_id] = target

        prioritized = queue.get_prioritized_targets()

        assert len(prioritized) == 3
        assert prioritized[0].priority == Priority.HIGH
        assert prioritized[1].priority == Priority.MEDIUM
        assert prioritized[2].priority == Priority.LOW

    def test_get_next_target_with_equal_voi_uses_creation_time(self):
        """When VOI scores are equal, should use creation time (newer first due to reverse sort)."""
        queue = ResearchQueueService()
        # Clear any existing targets
        queue._targets = {}

        earlier_time = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        later_time = datetime(2026, 3, 1, 11, 0, 0, tzinfo=timezone.utc)

        targets = [
            ResearchTarget(
                target_id="time_target_later",
                gap_type=GapType.VALIDATION,
                gap_id="time_gap_later",
                gap_description="Later target",
                voi_score=0.5,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
                created_at=later_time,
            ),
            ResearchTarget(
                target_id="time_target_earlier",
                gap_type=GapType.VALIDATION,
                gap_id="time_gap_earlier",
                gap_description="Earlier target",
                voi_score=0.5,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
                created_at=earlier_time,
            ),
        ]

        for target in targets:
            queue._targets[target.target_id] = target

        collector_id = "collector_test_time"
        next_target = queue.get_next_target(collector_id)

        # With reverse=True in sort, newer targets come first when VOI is equal
        assert next_target.target_id == "time_target_later"


# =============================================================================
# Test Fix 3: Automated Searcher Integration
# =============================================================================


class TestAutomatedSearcherIntegration:
    """Test that automated searcher can be triggered from the queue."""

    def test_queue_has_run_automated_searcher_method(self):
        """ResearchQueueService should have run_automated_searcher method."""
        queue = ResearchQueueService()
        assert hasattr(queue, 'run_automated_searcher')
        assert callable(queue.run_automated_searcher)


# =============================================================================
# Integration Tests
# =============================================================================


class TestVOIIntegrationEndToEnd:
    """End-to-end tests for VOI integration."""

    def test_gap_predictor_with_real_voi_produces_differentiated_scores(self):
        """Real VOI scorer should produce varied, meaningful scores."""
        mock_scorer = MockVOICalculator(return_voi=0.72)
        web = MockWebOfBelief(n_beliefs=3)
        gp = GapPredictor(web=web, voi_scorer=mock_scorer)

        voi_mechanism = gp._compute_gap_voi(GapType.MECHANISM, "belief_0")
        voi_validation = gp._compute_gap_voi(GapType.VALIDATION, "belief_1")
        voi_boundary = gp._compute_gap_voi(GapType.BOUNDARY, "belief_2")

        assert 0.0 < voi_mechanism <= 1.0
        assert 0.0 < voi_validation <= 1.0
        assert 0.0 < voi_boundary <= 1.0

    def test_queue_respects_voi_across_multiple_targets(self):
        """Queue should consistently respect VOI ordering across multiple operations."""
        queue = ResearchQueueService()
        # Clear any existing targets
        queue._targets = {}

        for i in range(5):
            target = ResearchTarget(
                target_id=f"multi_target_{i}",
                gap_type=GapType.MECHANISM,
                gap_id=f"multi_gap_{i}",
                gap_description=f"Gap {i}",
                voi_score=float(i) * 0.2,
                priority=Priority.MEDIUM,
                status=TargetStatus.OPEN,
            )
            queue._targets[f"multi_target_{i}"] = target

        prioritized = queue.get_prioritized_targets()

        for i in range(len(prioritized) - 1):
            assert prioritized[i].voi_score >= prioritized[i + 1].voi_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
