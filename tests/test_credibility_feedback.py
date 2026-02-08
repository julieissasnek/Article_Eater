"""
Tests for Credibility Feedback Tracking.

TODO 1: Credibility Testing Method - Feedback Loop Component
Date: February 8, 2026
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

from src.services.credibility_feedback import (
    FeedbackTracker,
    FlagResolution,
    Resolution,
    ErrorCategory,
    FalsePositiveReason,
    PerformanceMetrics,
    ThresholdAdjustment,
    create_resolution_from_report,
    batch_resolve_flags,
    create_tracker,
)
from src.services.credibility_testing import (
    CredibilityReport,
    CredibilityFlag,
    Decision,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def tracker(temp_db):
    """Create a FeedbackTracker with temporary database."""
    return FeedbackTracker(temp_db)


@pytest.fixture
def sample_resolution():
    """Create a sample FlagResolution."""
    return FlagResolution(
        resolution_id="test_article_0_20260208120000",
        article_id="test_article",
        flag_index=0,
        flag_reason="Credence at boundary",
        flag_confidence=0.9,
        flag_decision="block",
        resolution=Resolution.TRUE_POSITIVE,
        resolved_at=datetime.now(timezone.utc),
        reviewer_id="reviewer_1",
        reviewer_notes="Extraction error in LLM parsing",
        error_category=ErrorCategory.EXTRACTION_ERROR,
    )


@pytest.fixture
def sample_report():
    """Create a sample CredibilityReport with flags."""
    report = CredibilityReport(
        article_id="test_article_123",
        timestamp=datetime.now(timezone.utc),
    )
    report.add_flag(CredibilityFlag(
        decision=Decision.BLOCK,
        reason="Sample size is non-positive",
        confidence=1.0,
        field_name="sample_size",
    ))
    report.add_flag(CredibilityFlag(
        decision=Decision.REVIEW,
        reason="Scope may extend beyond sample",
        confidence=0.7,
        field_name="scope",
    ))
    return report


# =============================================================================
# TEST: Resolution Enum
# =============================================================================

class TestResolutionEnum:
    def test_resolution_values(self):
        assert Resolution.TRUE_POSITIVE.value == "true_positive"
        assert Resolution.FALSE_POSITIVE.value == "false_positive"
        assert Resolution.DEFERRED.value == "deferred"
        assert Resolution.INCONCLUSIVE.value == "inconclusive"


# =============================================================================
# TEST: FlagResolution
# =============================================================================

class TestFlagResolution:
    def test_creation(self, sample_resolution):
        assert sample_resolution.article_id == "test_article"
        assert sample_resolution.resolution == Resolution.TRUE_POSITIVE
        assert sample_resolution.error_category == ErrorCategory.EXTRACTION_ERROR

    def test_to_dict(self, sample_resolution):
        d = sample_resolution.to_dict()
        assert d['resolution'] == 'true_positive'
        assert d['error_category'] == 'extraction_error'
        assert 'resolved_at' in d

    def test_from_dict(self, sample_resolution):
        d = sample_resolution.to_dict()
        restored = FlagResolution.from_dict(d)
        assert restored.resolution == Resolution.TRUE_POSITIVE
        assert restored.error_category == ErrorCategory.EXTRACTION_ERROR

    def test_false_positive_resolution(self):
        res = FlagResolution(
            resolution_id="fp_test",
            article_id="article_fp",
            flag_index=0,
            flag_reason="Unusual pattern",
            flag_confidence=0.6,
            flag_decision="review",
            resolution=Resolution.FALSE_POSITIVE,
            resolved_at=datetime.now(timezone.utc),
            false_positive_reason=FalsePositiveReason.UNUSUAL_BUT_VALID,
        )
        assert res.resolution == Resolution.FALSE_POSITIVE
        assert res.false_positive_reason == FalsePositiveReason.UNUSUAL_BUT_VALID


# =============================================================================
# TEST: PerformanceMetrics
# =============================================================================

class TestPerformanceMetrics:
    def test_rates(self):
        metrics = PerformanceMetrics(
            flag_type="test",
            total_flags=100,
            resolved_count=80,
            true_positive_count=60,
            false_positive_count=20,
            deferred_count=15,
            inconclusive_count=5,
        )
        assert metrics.true_positive_rate == 60 / 80
        assert metrics.false_positive_rate == 20 / 80
        assert metrics.precision == 60 / 80

    def test_zero_resolved(self):
        metrics = PerformanceMetrics(
            flag_type="test",
            total_flags=10,
            resolved_count=0,
            true_positive_count=0,
            false_positive_count=0,
            deferred_count=10,
            inconclusive_count=0,
        )
        assert metrics.true_positive_rate == 0.0
        assert metrics.false_positive_rate == 0.0
        assert metrics.precision == 0.0

    def test_to_dict(self):
        metrics = PerformanceMetrics(
            flag_type="scope",
            total_flags=50,
            resolved_count=40,
            true_positive_count=30,
            false_positive_count=10,
            deferred_count=5,
            inconclusive_count=5,
        )
        d = metrics.to_dict()
        assert d['flag_type'] == 'scope'
        assert d['precision'] == 0.75
        assert 'true_positive_rate' in d


# =============================================================================
# TEST: FeedbackTracker
# =============================================================================

class TestFeedbackTracker:
    def test_initialization(self, tracker):
        assert tracker.db_path.exists()

    def test_record_resolution(self, tracker, sample_resolution):
        tracker.record_resolution(sample_resolution)
        retrieved = tracker.get_resolution(sample_resolution.resolution_id)
        assert retrieved is not None
        assert retrieved.article_id == sample_resolution.article_id
        assert retrieved.resolution == Resolution.TRUE_POSITIVE

    def test_get_resolutions_for_article(self, tracker, sample_resolution):
        tracker.record_resolution(sample_resolution)
        resolutions = tracker.get_resolutions_for_article("test_article")
        assert len(resolutions) == 1
        assert resolutions[0].resolution_id == sample_resolution.resolution_id

    def test_get_all_resolutions(self, tracker, sample_resolution):
        tracker.record_resolution(sample_resolution)

        # Add another
        res2 = FlagResolution(
            resolution_id="test_2",
            article_id="other_article",
            flag_index=0,
            flag_reason="Other issue",
            flag_confidence=0.5,
            flag_decision="review",
            resolution=Resolution.FALSE_POSITIVE,
            resolved_at=datetime.now(timezone.utc),
        )
        tracker.record_resolution(res2)

        all_res = tracker.get_all_resolutions()
        assert len(all_res) == 2

    def test_update_resolution(self, tracker, sample_resolution):
        # Record initial
        tracker.record_resolution(sample_resolution)

        # Update with same ID
        updated = FlagResolution(
            resolution_id=sample_resolution.resolution_id,
            article_id=sample_resolution.article_id,
            flag_index=sample_resolution.flag_index,
            flag_reason=sample_resolution.flag_reason,
            flag_confidence=sample_resolution.flag_confidence,
            flag_decision=sample_resolution.flag_decision,
            resolution=Resolution.FALSE_POSITIVE,  # Changed
            resolved_at=datetime.now(timezone.utc),
            reviewer_notes="Changed my mind",
        )
        tracker.record_resolution(updated)

        retrieved = tracker.get_resolution(sample_resolution.resolution_id)
        assert retrieved.resolution == Resolution.FALSE_POSITIVE


class TestPerformanceMetricsCalculation:
    def test_overall_metrics(self, tracker):
        # Add mix of resolutions
        for i in range(10):
            res = FlagResolution(
                resolution_id=f"res_{i}",
                article_id=f"article_{i}",
                flag_index=0,
                flag_reason="Test reason",
                flag_confidence=0.8,
                flag_decision="review",
                resolution=Resolution.TRUE_POSITIVE if i < 7 else Resolution.FALSE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
            )
            tracker.record_resolution(res)

        metrics = tracker.get_performance_metrics()
        assert metrics.total_flags == 10
        assert metrics.true_positive_count == 7
        assert metrics.false_positive_count == 3
        assert metrics.precision == 0.7

    def test_metrics_by_flag_type(self, tracker):
        # Add resolutions with different flag reasons
        for i in range(5):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"scope_{i}",
                article_id=f"article_scope_{i}",
                flag_index=0,
                flag_reason="Scope overreach",
                flag_confidence=0.7,
                flag_decision="review",
                resolution=Resolution.TRUE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
            ))

        for i in range(5):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"causal_{i}",
                article_id=f"article_causal_{i}",
                flag_index=0,
                flag_reason="Causal claim mismatch",
                flag_confidence=0.6,
                flag_decision="review",
                resolution=Resolution.FALSE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
            ))

        by_type = tracker.get_metrics_by_flag_type()
        assert len(by_type) == 2


class TestThresholdAdjustments:
    def test_suggest_raise_threshold(self, tracker):
        # Add many false positives for one flag type
        for i in range(15):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"fp_{i}",
                article_id=f"article_{i}",
                flag_index=0,
                flag_reason="Effect size implausible",
                flag_confidence=0.6,
                flag_decision="review",
                resolution=Resolution.FALSE_POSITIVE if i < 12 else Resolution.TRUE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
            ))

        adjustments = tracker.suggest_threshold_adjustments(target_precision=0.7, min_samples=10)
        assert len(adjustments) > 0
        assert adjustments[0].direction == "raise"

    def test_no_adjustment_for_small_samples(self, tracker):
        # Add only 5 resolutions (below min_samples)
        for i in range(5):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"small_{i}",
                article_id=f"article_{i}",
                flag_index=0,
                flag_reason="Some issue",
                flag_confidence=0.5,
                flag_decision="review",
                resolution=Resolution.FALSE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
            ))

        adjustments = tracker.suggest_threshold_adjustments(min_samples=10)
        assert len(adjustments) == 0


class TestDistributions:
    def test_error_distribution(self, tracker):
        # Add true positives with different error categories
        for i, cat in enumerate([
            ErrorCategory.EXTRACTION_ERROR,
            ErrorCategory.EXTRACTION_ERROR,
            ErrorCategory.SCOPE_ERROR,
            ErrorCategory.CAUSAL_ERROR,
        ]):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"tp_{i}",
                article_id=f"article_{i}",
                flag_index=0,
                flag_reason="Some issue",
                flag_confidence=0.8,
                flag_decision="block",
                resolution=Resolution.TRUE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
                error_category=cat,
            ))

        dist = tracker.get_error_distribution()
        assert dist['extraction_error'] == 2
        assert dist['scope_error'] == 1
        assert dist['causal_error'] == 1

    def test_false_positive_distribution(self, tracker):
        for i, reason in enumerate([
            FalsePositiveReason.THRESHOLD_TOO_STRICT,
            FalsePositiveReason.THRESHOLD_TOO_STRICT,
            FalsePositiveReason.UNUSUAL_BUT_VALID,
        ]):
            tracker.record_resolution(FlagResolution(
                resolution_id=f"fp_{i}",
                article_id=f"article_{i}",
                flag_index=0,
                flag_reason="Some issue",
                flag_confidence=0.5,
                flag_decision="review",
                resolution=Resolution.FALSE_POSITIVE,
                resolved_at=datetime.now(timezone.utc),
                false_positive_reason=reason,
            ))

        dist = tracker.get_false_positive_distribution()
        assert dist['threshold_too_strict'] == 2
        assert dist['unusual_but_valid'] == 1


class TestReportGeneration:
    def test_generate_report(self, tracker, sample_resolution):
        tracker.record_resolution(sample_resolution)

        report = tracker.generate_report()
        assert 'generated_at' in report
        assert 'overall' in report
        assert 'by_flag_type' in report
        assert 'suggested_adjustments' in report
        assert report['overall']['total_flags'] == 1


# =============================================================================
# TEST: Helper Functions
# =============================================================================

class TestHelperFunctions:
    def test_create_resolution_from_report(self, sample_report):
        resolution = create_resolution_from_report(
            report=sample_report,
            flag_index=0,
            resolution=Resolution.TRUE_POSITIVE,
            reviewer_id="test_reviewer",
            error_category=ErrorCategory.EXTRACTION_ERROR,
        )
        assert resolution.article_id == "test_article_123"
        assert resolution.flag_reason == "Sample size is non-positive"
        assert resolution.resolution == Resolution.TRUE_POSITIVE

    def test_batch_resolve_flags(self, tracker, sample_report):
        resolutions = batch_resolve_flags(
            tracker=tracker,
            report=sample_report,
            resolution=Resolution.TRUE_POSITIVE,
            reviewer_id="bulk_reviewer",
        )
        assert len(resolutions) == 2

        # Verify all were recorded
        all_res = tracker.get_all_resolutions()
        assert len(all_res) == 2


class TestFactoryFunctions:
    def test_create_tracker(self, temp_db):
        tracker = create_tracker(temp_db)
        assert tracker.db_path == Path(temp_db)


# =============================================================================
# TEST: Edge Cases
# =============================================================================

class TestEdgeCases:
    def test_empty_tracker(self, tracker):
        metrics = tracker.get_performance_metrics()
        assert metrics.total_flags == 0
        assert metrics.precision == 0.0

    def test_get_nonexistent_resolution(self, tracker):
        result = tracker.get_resolution("nonexistent_id")
        assert result is None

    def test_get_resolutions_for_nonexistent_article(self, tracker):
        result = tracker.get_resolutions_for_article("nonexistent_article")
        assert result == []

    def test_resolution_without_optional_fields(self, tracker):
        res = FlagResolution(
            resolution_id="minimal",
            article_id="article",
            flag_index=0,
            flag_reason="Issue",
            flag_confidence=0.5,
            flag_decision="review",
            resolution=Resolution.DEFERRED,
            resolved_at=datetime.now(timezone.utc),
        )
        tracker.record_resolution(res)
        retrieved = tracker.get_resolution("minimal")
        assert retrieved is not None
        assert retrieved.error_category is None
        assert retrieved.false_positive_reason is None
