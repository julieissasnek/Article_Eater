"""
Tests for Tier 1 Data Model Extensions
======================================

Tests for the new data model fields added per expert panel feedback:
- SourceDepth enum
- EnablingConditions dataclass
- CredenceHistoryEntry dataclass
- Belief extensions (source_depth, enabling_conditions, contested, credence_history)

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone

from src.services.web_of_belief import (
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    SourceDepth,
    EnablingConditions,
    CredenceHistoryEntry,
    ScopeConditions
)


# =============================================================================
# SourceDepth Tests
# =============================================================================

class TestSourceDepth:
    """Tests for SourceDepth enum."""

    def test_source_depth_values(self):
        """Test that all expected values exist."""
        assert SourceDepth.FULL_TEXT.value == "full_text"
        assert SourceDepth.ABSTRACT.value == "abstract"
        assert SourceDepth.METADATA.value == "metadata"

    def test_source_depth_from_string(self):
        """Test creating SourceDepth from string."""
        assert SourceDepth("full_text") == SourceDepth.FULL_TEXT
        assert SourceDepth("abstract") == SourceDepth.ABSTRACT
        assert SourceDepth("metadata") == SourceDepth.METADATA


# =============================================================================
# EnablingConditions Tests
# =============================================================================

class TestEnablingConditions:
    """Tests for EnablingConditions dataclass."""

    def test_empty_enabling_conditions(self):
        """Test creating empty enabling conditions."""
        ec = EnablingConditions()
        assert ec.is_empty()
        assert ec.minimum_exposure is None
        assert ec.baseline_state is None
        assert len(ec.concurrent_factors) == 0
        assert len(ec.blocking_factors) == 0

    def test_enabling_conditions_with_values(self):
        """Test creating enabling conditions with values."""
        ec = EnablingConditions(
            minimum_exposure=">30 minutes",
            baseline_state="non-depressed",
            concurrent_factors=["quiet environment"],
            blocking_factors=["artificial light present"],
            threshold=">300 lux",
            dosage="daily exposure"
        )
        assert not ec.is_empty()
        assert ec.minimum_exposure == ">30 minutes"
        assert ec.threshold == ">300 lux"
        assert "quiet environment" in ec.concurrent_factors

    def test_enabling_conditions_to_dict(self):
        """Test serialization to dictionary."""
        ec = EnablingConditions(
            minimum_exposure=">30 minutes",
            threshold=">300 lux"
        )
        d = ec.to_dict()
        assert d['minimum_exposure'] == ">30 minutes"
        assert d['threshold'] == ">300 lux"
        assert d['baseline_state'] is None

    def test_enabling_conditions_from_dict(self):
        """Test deserialization from dictionary."""
        d = {
            'minimum_exposure': ">30 minutes",
            'threshold': ">300 lux",
            'concurrent_factors': ["quiet"],
            'blocking_factors': []
        }
        ec = EnablingConditions.from_dict(d)
        assert ec.minimum_exposure == ">30 minutes"
        assert ec.threshold == ">300 lux"
        assert "quiet" in ec.concurrent_factors

    def test_enabling_conditions_roundtrip(self):
        """Test that to_dict/from_dict preserves data."""
        ec = EnablingConditions(
            minimum_exposure=">30 minutes",
            baseline_state="healthy",
            concurrent_factors=["a", "b"],
            blocking_factors=["c"],
            threshold=">300 lux",
            dosage="daily"
        )
        d = ec.to_dict()
        ec2 = EnablingConditions.from_dict(d)
        assert ec2.minimum_exposure == ec.minimum_exposure
        assert ec2.baseline_state == ec.baseline_state
        assert ec2.concurrent_factors == ec.concurrent_factors
        assert ec2.blocking_factors == ec.blocking_factors
        assert ec2.threshold == ec.threshold
        assert ec2.dosage == ec.dosage


# =============================================================================
# CredenceHistoryEntry Tests
# =============================================================================

class TestCredenceHistoryEntry:
    """Tests for CredenceHistoryEntry dataclass."""

    def test_create_entry(self):
        """Test creating a history entry."""
        entry = CredenceHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            credence_value=0.75,
            delta=0.05,
            triggered_by="paper_123",
            update_reason="New supporting evidence"
        )
        assert entry.credence_value == 0.75
        assert entry.delta == 0.05
        assert entry.triggered_by == "paper_123"

    def test_entry_to_dict(self):
        """Test serialization to dictionary."""
        ts = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        entry = CredenceHistoryEntry(
            timestamp=ts,
            credence_value=0.75,
            delta=0.05,
            triggered_by="paper_123",
            update_reason="test"
        )
        d = entry.to_dict()
        assert d['credence_value'] == 0.75
        assert d['delta'] == 0.05
        assert d['triggered_by'] == "paper_123"
        assert '2026-01-20' in d['timestamp']

    def test_entry_from_dict(self):
        """Test deserialization from dictionary."""
        d = {
            'timestamp': '2026-01-20T12:00:00+00:00',
            'credence_value': 0.75,
            'delta': 0.05,
            'triggered_by': 'paper_123',
            'update_reason': 'test'
        }
        entry = CredenceHistoryEntry.from_dict(d)
        assert entry.credence_value == 0.75
        assert entry.delta == 0.05
        assert entry.triggered_by == 'paper_123'


# =============================================================================
# Belief Extensions Tests
# =============================================================================

class TestBeliefExtensions:
    """Tests for Belief dataclass with Tier 1 extensions."""

    @pytest.fixture
    def basic_belief(self):
        """Create a basic belief for testing."""
        return Belief(
            belief_id="test_001",
            content="Natural light improves mood",
            level=EpistemicLevel.EMPIRICAL
        )

    def test_default_source_depth(self, basic_belief):
        """Test that default source depth is FULL_TEXT."""
        assert basic_belief.source_depth == SourceDepth.FULL_TEXT

    def test_set_source_depth(self):
        """Test setting source depth to ABSTRACT."""
        belief = Belief(
            belief_id="test_002",
            content="Test belief from abstract",
            level=EpistemicLevel.EMPIRICAL,
            source_depth=SourceDepth.ABSTRACT
        )
        assert belief.source_depth == SourceDepth.ABSTRACT

    def test_default_not_contested(self, basic_belief):
        """Test that beliefs are not contested by default."""
        assert basic_belief.contested is False

    def test_empty_credence_history(self, basic_belief):
        """Test that credence history starts empty."""
        assert len(basic_belief.credence_history) == 0

    def test_enabling_conditions_attachment(self):
        """Test attaching enabling conditions to belief."""
        ec = EnablingConditions(
            minimum_exposure=">30 minutes",
            threshold=">300 lux"
        )
        belief = Belief(
            belief_id="test_003",
            content="Natural light improves mood",
            level=EpistemicLevel.EMPIRICAL,
            enabling_conditions=ec
        )
        assert belief.enabling_conditions is not None
        assert belief.enabling_conditions.minimum_exposure == ">30 minutes"

    def test_record_credence_change(self, basic_belief):
        """Test recording credence changes."""
        basic_belief.record_credence_change(0.6, "paper_001", "Initial evidence")
        basic_belief.record_credence_change(0.7, "paper_002", "More evidence")

        assert len(basic_belief.credence_history) == 2
        assert basic_belief.credence_history[0].credence_value == 0.6
        assert basic_belief.credence_history[1].credence_value == 0.7
        # Use approximate comparison for floating point
        assert abs(basic_belief.credence_history[1].delta - 0.1) < 0.001

    def test_credence_stability(self, basic_belief):
        """Test credence stability calculation."""
        # Set initial credence close to where we'll stabilize
        basic_belief.credence = Credence(0.7, 0.3)

        # Record some stable changes (small deltas)
        for i in range(5):
            basic_belief.record_credence_change(0.7 + 0.005 * i, f"paper_{i}")

        stability = basic_belief.credence_stability(window=5)
        assert stability < 0.01  # Should be stable

    def test_credence_instability(self, basic_belief):
        """Test detecting instability."""
        # Record some unstable changes
        basic_belief.record_credence_change(0.5, "paper_1")
        basic_belief.record_credence_change(0.8, "paper_2")
        basic_belief.record_credence_change(0.4, "paper_3")
        basic_belief.record_credence_change(0.9, "paper_4")
        basic_belief.record_credence_change(0.3, "paper_5")

        stability = basic_belief.credence_stability(window=5)
        assert stability > 0.1  # Should be unstable

    def test_is_stable(self, basic_belief):
        """Test is_stable method."""
        # Set initial credence close to where we'll stabilize
        basic_belief.credence = Credence(0.7, 0.3)

        # Record stable changes (small deltas from 0.7)
        for i in range(5):
            basic_belief.record_credence_change(0.7 + 0.001 * i, f"paper_{i}")

        assert basic_belief.is_stable(threshold=0.01, window=5)

    def test_oscillation_detection(self, basic_belief):
        """Test detection of oscillating credences."""
        # Create oscillation across 0.5 threshold
        basic_belief.record_credence_change(0.3, "paper_1")
        basic_belief.record_credence_change(0.7, "paper_2")  # Cross
        basic_belief.record_credence_change(0.3, "paper_3")  # Cross
        basic_belief.record_credence_change(0.7, "paper_4")  # Cross
        basic_belief.record_credence_change(0.3, "paper_5")  # Cross

        assert basic_belief.contested is True

    def test_credence_range(self, basic_belief):
        """Test credence range calculation."""
        basic_belief.record_credence_change(0.3, "paper_1")
        basic_belief.record_credence_change(0.8, "paper_2")
        basic_belief.record_credence_change(0.5, "paper_3")

        low, high = basic_belief.credence_range()
        assert low == 0.3
        assert high == 0.8

    def test_belief_to_dict_with_extensions(self):
        """Test that to_dict includes new fields."""
        ec = EnablingConditions(minimum_exposure=">30 minutes")
        belief = Belief(
            belief_id="test_004",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            source_depth=SourceDepth.ABSTRACT,
            enabling_conditions=ec,
            contested=True
        )
        belief.record_credence_change(0.7, "paper_1", "test")

        d = belief.to_dict()
        assert d['source_depth'] == 'abstract'
        assert d['contested'] is True
        assert 'enabling_conditions' in d
        assert d['enabling_conditions']['minimum_exposure'] == ">30 minutes"
        assert 'credence_history' in d
        assert len(d['credence_history']) == 1

    def test_belief_from_dict_with_extensions(self):
        """Test that from_dict parses new fields."""
        d = {
            'belief_id': 'test_005',
            'content': 'Test belief',
            'level': 'empirical',
            'status': 'established',
            'source_depth': 'abstract',
            'contested': True,
            'enabling_conditions': {
                'minimum_exposure': '>30 minutes',
                'threshold': '>300 lux'
            },
            'credence_history': [
                {
                    'timestamp': '2026-01-20T12:00:00+00:00',
                    'credence_value': 0.7,
                    'delta': 0.0,
                    'triggered_by': 'paper_1',
                    'update_reason': 'test'
                }
            ]
        }

        belief = Belief.from_dict(d)
        assert belief.source_depth == SourceDepth.ABSTRACT
        assert belief.contested is True
        assert belief.enabling_conditions is not None
        assert belief.enabling_conditions.minimum_exposure == ">30 minutes"
        assert len(belief.credence_history) == 1
        assert belief.credence_history[0].credence_value == 0.7

    def test_belief_roundtrip_with_extensions(self):
        """Test full roundtrip serialization with new fields."""
        ec = EnablingConditions(
            minimum_exposure=">30 minutes",
            threshold=">300 lux",
            concurrent_factors=["quiet"],
            blocking_factors=["artificial"]
        )
        scope = ScopeConditions(
            population="adults",
            setting="office",
            scope_specified=True
        )
        belief = Belief(
            belief_id="test_006",
            content="Natural light improves mood",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            source_depth=SourceDepth.ABSTRACT,
            enabling_conditions=ec,
            scope=scope,
            contested=False
        )
        belief.record_credence_change(0.7, "paper_1", "Initial")
        belief.record_credence_change(0.75, "paper_2", "More evidence")

        # Roundtrip
        d = belief.to_dict()
        belief2 = Belief.from_dict(d)

        assert belief2.belief_id == belief.belief_id
        assert belief2.source_depth == belief.source_depth
        assert belief2.contested == belief.contested
        assert belief2.enabling_conditions.minimum_exposure == ec.minimum_exposure
        assert belief2.enabling_conditions.threshold == ec.threshold
        assert len(belief2.credence_history) == 2
        assert belief2.scope.population == "adults"


# =============================================================================
# Integration Tests
# =============================================================================

class TestDataModelIntegration:
    """Integration tests for data model extensions."""

    def test_abstract_only_causal_claim_workflow(self):
        """
        Test the workflow for abstract-only causal claims.

        Per expert panel (Cartwright): Causal claims from abstracts
        should have lower default credence and warning badges.
        """
        belief = Belief(
            belief_id="causal_001",
            content="Natural light causes improved mood",
            level=EpistemicLevel.EMPIRICAL,
            source_depth=SourceDepth.ABSTRACT,
            credence=Credence(0.5, 0.5)  # Lower starting credence
        )

        # Verify lower credence for abstract-only
        assert belief.source_depth == SourceDepth.ABSTRACT
        assert belief.credence.value == 0.5

        # Could upgrade to full-text later
        belief.source_depth = SourceDepth.FULL_TEXT
        assert belief.source_depth == SourceDepth.FULL_TEXT

    def test_contested_belief_workflow(self):
        """
        Test the workflow for contested beliefs.

        Per expert panel (Epistemologist): When evidence genuinely
        conflicts, the web should reflect that, not average it away.
        """
        belief = Belief(
            belief_id="contested_001",
            content="Background music improves productivity",
            level=EpistemicLevel.EMPIRICAL
        )

        # Simulate conflicting evidence
        belief.record_credence_change(0.3, "study_1", "No effect found")
        belief.record_credence_change(0.7, "study_2", "Positive effect")
        belief.record_credence_change(0.3, "study_3", "No effect")
        belief.record_credence_change(0.7, "study_4", "Positive effect")
        belief.record_credence_change(0.3, "study_5", "No effect")

        # Should be marked as contested
        assert belief.contested is True

        # Should report a range, not a point
        low, high = belief.credence_range()
        assert low < 0.5
        assert high > 0.5

    def test_stability_based_stopping(self):
        """
        Test stability-based stopping rule.

        Per expert panel (Simon): Stop searching when credence
        stabilizes, not after arbitrary paper count.
        """
        belief = Belief(
            belief_id="stable_001",
            content="Natural light improves mood",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.5, 0.4)  # Start at 0.5
        )

        # Initial instability - large swings
        belief.record_credence_change(0.4, "paper_1")
        belief.record_credence_change(0.6, "paper_2")
        belief.record_credence_change(0.5, "paper_3")

        # Not stable yet (large deltas in history)
        assert not belief.is_stable(threshold=0.02, window=3)

        # Transition to convergence zone
        belief.record_credence_change(0.72, "paper_4")

        # Converging evidence - all close to each other
        belief.record_credence_change(0.73, "paper_5")
        belief.record_credence_change(0.735, "paper_6")
        belief.record_credence_change(0.74, "paper_7")
        belief.record_credence_change(0.745, "paper_8")
        belief.record_credence_change(0.748, "paper_9")

        # Now check stability for last 5 entries (papers 5-9)
        # These all have small deltas: 0.01, 0.005, 0.005, 0.005, 0.003
        assert belief.is_stable(threshold=0.02, window=5)
