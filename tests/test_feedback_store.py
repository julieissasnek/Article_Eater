"""
Tests for Unified Feedback Store.

Phase E: Implementation (Sprint B)
Per Lampson: Single feedback store instead of three.

Date: January 20, 2026
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta

from src.services.feedback_store import (
    SystemFeedback,
    FeedbackStore,
    create_feedback_id,
    create_credibility_feedback,
    create_explanation_feedback,
    create_search_feedback,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def store(temp_db):
    """Create a FeedbackStore instance with temporary database."""
    return FeedbackStore(temp_db)


@pytest.fixture
def sample_feedback():
    """Create a sample feedback record."""
    return SystemFeedback(
        feedback_id="fb_test_001",
        timestamp=datetime.now(timezone.utc),
        component="credibility",
        operation_id="op_test_001",
        outcome="positive",
        details={"flag_type": "scope_overreach", "was_correct": True},
        reviewer_notes="Test note",
    )


# =============================================================================
# UNIT TESTS: SystemFeedback
# =============================================================================

class TestSystemFeedback:
    """Tests for SystemFeedback dataclass."""

    def test_creation(self, sample_feedback):
        """Test basic feedback creation."""
        assert sample_feedback.feedback_id == "fb_test_001"
        assert sample_feedback.component == "credibility"
        assert sample_feedback.outcome == "positive"

    def test_to_dict(self, sample_feedback):
        """Test serialization."""
        d = sample_feedback.to_dict()
        assert d['feedback_id'] == "fb_test_001"
        assert d['component'] == "credibility"
        assert 'timestamp' in d

    def test_from_dict(self, sample_feedback):
        """Test deserialization."""
        d = sample_feedback.to_dict()
        restored = SystemFeedback.from_dict(d)
        assert restored.feedback_id == sample_feedback.feedback_id
        assert restored.component == sample_feedback.component


# =============================================================================
# UNIT TESTS: Factory Functions
# =============================================================================

class TestFactoryFunctions:
    """Tests for feedback factory functions."""

    def test_create_feedback_id(self):
        """Test ID generation."""
        id1 = create_feedback_id("credibility", "op_001")
        id2 = create_feedback_id("credibility", "op_002")
        assert id1.startswith("fb_credibility_")
        assert id1 != id2

    def test_create_credibility_feedback(self):
        """Test credibility feedback creation."""
        fb = create_credibility_feedback(
            operation_id="cred_001",
            outcome="positive",
            flag_type="scope_overreach",
            was_correct=True,
            reviewer_notes="Good catch",
        )
        assert fb.component == "credibility"
        assert fb.outcome == "positive"
        assert fb.details['flag_type'] == "scope_overreach"

    def test_create_explanation_feedback(self):
        """Test explanation feedback creation."""
        fb = create_explanation_feedback(
            operation_id="exp_001",
            outcome="positive",
            pattern_used="evidence_trace",
            comprehension_score=0.8,
        )
        assert fb.component == "explanation"
        assert fb.details['pattern_used'] == "evidence_trace"

    def test_create_search_feedback(self):
        """Test search feedback creation."""
        fb = create_search_feedback(
            operation_id="search_001",
            outcome="positive",
            gap_type="uncertain",
            strategy_used="keyword",
            papers_found=20,
            papers_useful=5,
        )
        assert fb.component == "search"
        assert fb.details['precision'] == 0.25  # 5/20


# =============================================================================
# INTEGRATION TESTS: FeedbackStore
# =============================================================================

class TestFeedbackStore:
    """Integration tests for FeedbackStore."""

    def test_record_and_retrieve(self, store, sample_feedback):
        """Test basic record and retrieve."""
        store.record(sample_feedback)
        retrieved = store.get_by_id(sample_feedback.feedback_id)

        assert retrieved is not None
        assert retrieved.feedback_id == sample_feedback.feedback_id
        assert retrieved.component == sample_feedback.component

    def test_get_by_component(self, store):
        """Test filtering by component."""
        # Add feedback for different components
        store.record(create_credibility_feedback("op1", "positive"))
        store.record(create_credibility_feedback("op2", "negative"))
        store.record(create_explanation_feedback("op3", "positive"))

        cred_feedback = store.get_by_component("credibility")
        exp_feedback = store.get_by_component("explanation")

        assert len(cred_feedback) == 2
        assert len(exp_feedback) == 1
        assert all(f.component == "credibility" for f in cred_feedback)

    def test_get_by_outcome(self, store):
        """Test filtering by outcome."""
        store.record(create_credibility_feedback("op1", "positive"))
        store.record(create_credibility_feedback("op2", "negative"))
        store.record(create_credibility_feedback("op3", "positive"))

        positive = store.get_by_outcome("positive")
        negative = store.get_by_outcome("negative")

        assert len(positive) == 2
        assert len(negative) == 1

    def test_get_recent(self, store):
        """Test filtering by timestamp."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        recent_time = datetime.now(timezone.utc) - timedelta(minutes=30)

        # Create old feedback
        old_fb = SystemFeedback(
            feedback_id="fb_old",
            timestamp=old_time,
            component="credibility",
            operation_id="old_op",
            outcome="positive",
        )
        store.record(old_fb)

        # Create recent feedback
        store.record(create_credibility_feedback("recent_op", "positive"))

        # Query for last hour
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        recent = store.get_recent(since)

        assert len(recent) == 1
        assert recent[0].operation_id == "recent_op"

    def test_component_stats(self, store):
        """Test statistics computation."""
        store.record(create_credibility_feedback("op1", "positive"))
        store.record(create_credibility_feedback("op2", "positive"))
        store.record(create_credibility_feedback("op3", "negative"))

        stats = store.get_component_stats("credibility")

        assert stats['total_feedback'] == 3
        assert stats['outcome_counts']['positive'] == 2
        assert stats['outcome_counts']['negative'] == 1
        assert abs(stats['positive_rate'] - 2/3) < 0.01

    def test_cross_component_analysis(self, store):
        """Test cross-component analysis."""
        store.record(create_credibility_feedback("op1", "positive"))
        store.record(create_explanation_feedback("op2", "positive"))
        store.record(create_search_feedback("op3", "negative"))

        analysis = store.cross_component_analysis()

        assert 'credibility' in analysis['component_outcomes']
        assert 'explanation' in analysis['component_outcomes']
        assert 'search' in analysis['component_outcomes']

    def test_clear_all(self, store):
        """Test clearing all records."""
        store.record(create_credibility_feedback("op1", "positive"))
        store.record(create_credibility_feedback("op2", "negative"))

        count = store.clear_all()
        assert count == 2

        all_feedback = store.get_all_feedback()
        assert len(all_feedback) == 0


class TestFeedbackStorePersistence:
    """Tests for database persistence."""

    def test_persistence_across_instances(self, temp_db):
        """Test that data persists across store instances."""
        # Write with first instance
        store1 = FeedbackStore(temp_db)
        store1.record(create_credibility_feedback("persist_op", "positive"))

        # Read with second instance
        store2 = FeedbackStore(temp_db)
        feedback = store2.get_all_feedback()

        assert len(feedback) == 1
        assert feedback[0].operation_id == "persist_op"


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_details(self, store):
        """Test feedback with empty details."""
        fb = SystemFeedback(
            feedback_id="fb_empty",
            timestamp=datetime.now(timezone.utc),
            component="credibility",
            operation_id="empty_op",
            outcome="neutral",
            details={},
        )
        store.record(fb)
        retrieved = store.get_by_id("fb_empty")
        assert retrieved.details == {}

    def test_large_details(self, store):
        """Test feedback with large details dict."""
        large_details = {f"key_{i}": f"value_{i}" for i in range(100)}
        fb = SystemFeedback(
            feedback_id="fb_large",
            timestamp=datetime.now(timezone.utc),
            component="credibility",
            operation_id="large_op",
            outcome="positive",
            details=large_details,
        )
        store.record(fb)
        retrieved = store.get_by_id("fb_large")
        assert len(retrieved.details) == 100

    def test_special_characters_in_notes(self, store):
        """Test handling of special characters."""
        fb = SystemFeedback(
            feedback_id="fb_special",
            timestamp=datetime.now(timezone.utc),
            component="credibility",
            operation_id="special_op",
            outcome="positive",
            reviewer_notes="Notes with 'quotes' and \"double quotes\" and\nnewlines",
        )
        store.record(fb)
        retrieved = store.get_by_id("fb_special")
        assert "quotes" in retrieved.reviewer_notes
        assert "\n" in retrieved.reviewer_notes

    def test_get_nonexistent(self, store):
        """Test retrieving nonexistent record."""
        result = store.get_by_id("nonexistent_id")
        assert result is None
