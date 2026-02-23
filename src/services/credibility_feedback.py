"""
Credibility Feedback Tracking for Article Eater Post-Quinean.

TODO 1: Credibility Testing Method - Feedback Loop Component

This module tracks how credibility flags are resolved by human reviewers,
enabling threshold calibration and performance monitoring.

Per Simon: Adjust thresholds based on actual false positive rates.
Per Mayo: Severe testing requires tracking what tests were passed.

Date: February 8, 2026
"""

import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.services.credibility_testing import (
    CredibilityReport,
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class Resolution(Enum):
    """How a flag was resolved by human review."""
    TRUE_POSITIVE = "true_positive"      # Flag correctly identified a problem
    FALSE_POSITIVE = "false_positive"    # Flag was raised incorrectly
    DEFERRED = "deferred"                # Decision postponed
    INCONCLUSIVE = "inconclusive"        # Couldn't determine correctness


class ErrorCategory(Enum):
    """Category of error when flag was true positive."""
    EXTRACTION_ERROR = "extraction_error"      # LLM/parser extracted wrongly
    PAPER_ERROR = "paper_error"                # Paper itself has issues
    SYSTEM_ERROR = "system_error"              # Bug in our code
    SCOPE_ERROR = "scope_error"                # Scope conditions wrong
    CAUSAL_ERROR = "causal_error"              # Causal claims overreached
    STATISTICAL_ERROR = "statistical_error"    # Stats misinterpreted
    OTHER = "other"


class FalsePositiveReason(Enum):
    """Why a flag was a false positive."""
    THRESHOLD_TOO_STRICT = "threshold_too_strict"
    UNUSUAL_BUT_VALID = "unusual_but_valid"
    CONTEXT_NOT_CAPTURED = "context_not_captured"
    DOMAIN_SPECIFIC = "domain_specific"
    MISSING_METADATA = "missing_metadata"
    OTHER = "other"


@dataclass
class FlagResolution:
    """Record of how a credibility flag was resolved."""
    # Identification
    resolution_id: str
    article_id: str
    flag_index: int          # Index in the original report's flags list

    # Original flag info (denormalized for query convenience)
    flag_reason: str
    flag_confidence: float
    flag_decision: str       # "block" or "review"

    # Resolution
    resolution: Resolution
    resolved_at: datetime
    reviewer_id: Optional[str] = None
    reviewer_notes: Optional[str] = None

    # If true positive
    error_category: Optional[ErrorCategory] = None
    error_details: Optional[str] = None

    # If false positive
    false_positive_reason: Optional[FalsePositiveReason] = None
    suggested_threshold_change: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        d = asdict(self)
        d['resolution'] = self.resolution.value
        d['resolved_at'] = self.resolved_at.isoformat()
        if self.error_category:
            d['error_category'] = self.error_category.value
        if self.false_positive_reason:
            d['false_positive_reason'] = self.false_positive_reason.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'FlagResolution':
        """Create from dictionary."""
        d = d.copy()
        d['resolution'] = Resolution(d['resolution'])
        d['resolved_at'] = datetime.fromisoformat(d['resolved_at'])
        if d.get('error_category'):
            d['error_category'] = ErrorCategory(d['error_category'])
        if d.get('false_positive_reason'):
            d['false_positive_reason'] = FalsePositiveReason(d['false_positive_reason'])
        return cls(**d)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific flag type or overall."""
    flag_type: str
    total_flags: int
    resolved_count: int
    true_positive_count: int
    false_positive_count: int
    deferred_count: int
    inconclusive_count: int

    @property
    def true_positive_rate(self) -> float:
        """Proportion of flags that were true problems."""
        if self.resolved_count == 0:
            return 0.0
        return self.true_positive_count / self.resolved_count

    @property
    def false_positive_rate(self) -> float:
        """Proportion of flags that were false alarms."""
        if self.resolved_count == 0:
            return 0.0
        return self.false_positive_count / self.resolved_count

    @property
    def precision(self) -> float:
        """Precision = TP / (TP + FP)."""
        tp_fp = self.true_positive_count + self.false_positive_count
        if tp_fp == 0:
            return 0.0
        return self.true_positive_count / tp_fp

    def to_dict(self) -> Dict[str, Any]:
        return {
            'flag_type': self.flag_type,
            'total_flags': self.total_flags,
            'resolved_count': self.resolved_count,
            'true_positive_count': self.true_positive_count,
            'false_positive_count': self.false_positive_count,
            'deferred_count': self.deferred_count,
            'inconclusive_count': self.inconclusive_count,
            'true_positive_rate': self.true_positive_rate,
            'false_positive_rate': self.false_positive_rate,
            'precision': self.precision,
        }


@dataclass
class ThresholdAdjustment:
    """Suggested adjustment to a threshold based on performance."""
    flag_type: str
    current_threshold: float
    suggested_threshold: float
    direction: str              # "raise" or "lower"
    reason: str
    confidence: float           # How confident are we in this suggestion
    based_on_n: int             # Number of resolutions this is based on

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# FEEDBACK TRACKER
# =============================================================================

class FeedbackTracker:
    """
    Tracks flag resolutions to improve credibility testing thresholds.

    Uses SQLite for persistent storage. Thread-safe for single-writer scenarios.
    """

    def __init__(self, db_path: str = "credibility_feedback.db"):
        """
        Initialize feedback tracker.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flag_resolutions (
                    resolution_id TEXT PRIMARY KEY,
                    article_id TEXT NOT NULL,
                    flag_index INTEGER NOT NULL,
                    flag_reason TEXT NOT NULL,
                    flag_confidence REAL NOT NULL,
                    flag_decision TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    resolved_at TEXT NOT NULL,
                    reviewer_id TEXT,
                    reviewer_notes TEXT,
                    error_category TEXT,
                    error_details TEXT,
                    false_positive_reason TEXT,
                    suggested_threshold_change REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_article_id
                ON flag_resolutions(article_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_flag_reason
                ON flag_resolutions(flag_reason)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_resolution
                ON flag_resolutions(resolution)
            """)
            conn.commit()

    def record_resolution(self, resolution: FlagResolution) -> None:
        """
        Record how a flag was resolved.

        Args:
            resolution: The resolution record
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO flag_resolutions (
                    resolution_id, article_id, flag_index,
                    flag_reason, flag_confidence, flag_decision,
                    resolution, resolved_at, reviewer_id, reviewer_notes,
                    error_category, error_details,
                    false_positive_reason, suggested_threshold_change
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resolution.resolution_id,
                resolution.article_id,
                resolution.flag_index,
                resolution.flag_reason,
                resolution.flag_confidence,
                resolution.flag_decision,
                resolution.resolution.value,
                resolution.resolved_at.isoformat(),
                resolution.reviewer_id,
                resolution.reviewer_notes,
                resolution.error_category.value if resolution.error_category else None,
                resolution.error_details,
                resolution.false_positive_reason.value if resolution.false_positive_reason else None,
                resolution.suggested_threshold_change,
            ))
            conn.commit()

        logger.info(f"Recorded resolution {resolution.resolution_id}: {resolution.resolution.value}")

    def get_resolution(self, resolution_id: str) -> Optional[FlagResolution]:
        """Get a specific resolution by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM flag_resolutions WHERE resolution_id = ?",
                (resolution_id,)
            )
            row = cur.fetchone()
            if row:
                return self._row_to_resolution(row)
        return None

    def get_resolutions_for_article(self, article_id: str) -> List[FlagResolution]:
        """Get all resolutions for an article."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM flag_resolutions WHERE article_id = ? ORDER BY flag_index",
                (article_id,)
            )
            return [self._row_to_resolution(row) for row in cur.fetchall()]

    def get_all_resolutions(self) -> List[FlagResolution]:
        """Get all resolutions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT * FROM flag_resolutions ORDER BY resolved_at DESC"
            )
            return [self._row_to_resolution(row) for row in cur.fetchall()]

    def _row_to_resolution(self, row: sqlite3.Row) -> FlagResolution:
        """Convert database row to FlagResolution."""
        return FlagResolution(
            resolution_id=row['resolution_id'],
            article_id=row['article_id'],
            flag_index=row['flag_index'],
            flag_reason=row['flag_reason'],
            flag_confidence=row['flag_confidence'],
            flag_decision=row['flag_decision'],
            resolution=Resolution(row['resolution']),
            resolved_at=datetime.fromisoformat(row['resolved_at']),
            reviewer_id=row['reviewer_id'],
            reviewer_notes=row['reviewer_notes'],
            error_category=ErrorCategory(row['error_category']) if row['error_category'] else None,
            error_details=row['error_details'],
            false_positive_reason=FalsePositiveReason(row['false_positive_reason']) if row['false_positive_reason'] else None,
            suggested_threshold_change=row['suggested_threshold_change'],
        )

    def get_performance_metrics(self, flag_type: Optional[str] = None) -> PerformanceMetrics:
        """
        Compute performance metrics from resolution history.

        Args:
            flag_type: If provided, compute metrics for this flag type only.
                       If None, compute overall metrics.

        Returns:
            PerformanceMetrics object
        """
        with sqlite3.connect(self.db_path) as conn:
            if flag_type:
                cur = conn.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN resolution != 'deferred' AND resolution != 'inconclusive' THEN 1 ELSE 0 END) as resolved,
                        SUM(CASE WHEN resolution = 'true_positive' THEN 1 ELSE 0 END) as tp,
                        SUM(CASE WHEN resolution = 'false_positive' THEN 1 ELSE 0 END) as fp,
                        SUM(CASE WHEN resolution = 'deferred' THEN 1 ELSE 0 END) as deferred,
                        SUM(CASE WHEN resolution = 'inconclusive' THEN 1 ELSE 0 END) as inconclusive
                    FROM flag_resolutions
                    WHERE flag_reason LIKE ?
                """, (f"%{flag_type}%",))
            else:
                cur = conn.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN resolution != 'deferred' AND resolution != 'inconclusive' THEN 1 ELSE 0 END) as resolved,
                        SUM(CASE WHEN resolution = 'true_positive' THEN 1 ELSE 0 END) as tp,
                        SUM(CASE WHEN resolution = 'false_positive' THEN 1 ELSE 0 END) as fp,
                        SUM(CASE WHEN resolution = 'deferred' THEN 1 ELSE 0 END) as deferred,
                        SUM(CASE WHEN resolution = 'inconclusive' THEN 1 ELSE 0 END) as inconclusive
                    FROM flag_resolutions
                """)

            row = cur.fetchone()
            return PerformanceMetrics(
                flag_type=flag_type or "all",
                total_flags=row[0] or 0,
                resolved_count=row[1] or 0,
                true_positive_count=row[2] or 0,
                false_positive_count=row[3] or 0,
                deferred_count=row[4] or 0,
                inconclusive_count=row[5] or 0,
            )

    def get_metrics_by_flag_type(self) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics broken down by flag type."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT DISTINCT flag_reason FROM flag_resolutions"
            )
            flag_types = [row[0] for row in cur.fetchall()]

        return {
            ft: self.get_performance_metrics(ft)
            for ft in flag_types
        }

    def suggest_threshold_adjustments(
        self,
        target_precision: float = 0.7,
        min_samples: int = 10
    ) -> List[ThresholdAdjustment]:
        """
        Suggest threshold adjustments based on performance.

        Per Simon: Adjust based on actual false positive rates.

        Args:
            target_precision: Target precision (TP / (TP + FP))
            min_samples: Minimum resolved samples to make a suggestion

        Returns:
            List of suggested threshold adjustments
        """
        adjustments = []
        metrics_by_type = self.get_metrics_by_flag_type()

        for flag_type, metrics in metrics_by_type.items():
            if metrics.resolved_count < min_samples:
                continue

            current_precision = metrics.precision

            if current_precision < target_precision - 0.1:
                # Too many false positives - raise threshold
                adjustments.append(ThresholdAdjustment(
                    flag_type=flag_type,
                    current_threshold=0.5,  # Default, would need actual threshold tracking
                    suggested_threshold=0.6,
                    direction="raise",
                    reason=f"Precision {current_precision:.0%} below target {target_precision:.0%}. "
                           f"FP rate: {metrics.false_positive_rate:.0%}",
                    confidence=min(0.9, metrics.resolved_count / 50),
                    based_on_n=metrics.resolved_count,
                ))
            elif current_precision > target_precision + 0.2:
                # Very few false positives - might be missing issues
                adjustments.append(ThresholdAdjustment(
                    flag_type=flag_type,
                    current_threshold=0.5,
                    suggested_threshold=0.4,
                    direction="lower",
                    reason=f"Precision {current_precision:.0%} well above target. "
                           f"May be missing issues. Consider lowering threshold.",
                    confidence=min(0.7, metrics.resolved_count / 50),
                    based_on_n=metrics.resolved_count,
                ))

        return adjustments

    def get_error_distribution(self) -> Dict[str, int]:
        """Get distribution of error categories for true positives."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT error_category, COUNT(*)
                FROM flag_resolutions
                WHERE resolution = 'true_positive' AND error_category IS NOT NULL
                GROUP BY error_category
            """)
            return {row[0]: row[1] for row in cur.fetchall()}

    def get_false_positive_distribution(self) -> Dict[str, int]:
        """Get distribution of false positive reasons."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                SELECT false_positive_reason, COUNT(*)
                FROM flag_resolutions
                WHERE resolution = 'false_positive' AND false_positive_reason IS NOT NULL
                GROUP BY false_positive_reason
            """)
            return {row[0]: row[1] for row in cur.fetchall()}

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Returns:
            Dictionary with overall metrics, per-type metrics,
            distributions, and threshold suggestions.
        """
        overall = self.get_performance_metrics()
        by_type = self.get_metrics_by_flag_type()
        adjustments = self.suggest_threshold_adjustments()

        return {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'overall': overall.to_dict(),
            'by_flag_type': {k: v.to_dict() for k, v in by_type.items()},
            'error_distribution': self.get_error_distribution(),
            'false_positive_distribution': self.get_false_positive_distribution(),
            'suggested_adjustments': [a.to_dict() for a in adjustments],
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_resolution_from_report(
    report: CredibilityReport,
    flag_index: int,
    resolution: Resolution,
    reviewer_id: Optional[str] = None,
    reviewer_notes: Optional[str] = None,
    error_category: Optional[ErrorCategory] = None,
    false_positive_reason: Optional[FalsePositiveReason] = None,
) -> FlagResolution:
    """
    Create a FlagResolution from a CredibilityReport and flag index.

    Convenience function for reviewers.
    """
    flag = report.flags[flag_index]

    return FlagResolution(
        resolution_id=f"{report.article_id}_{flag_index}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        article_id=report.article_id,
        flag_index=flag_index,
        flag_reason=flag.reason,
        flag_confidence=flag.confidence,
        flag_decision=flag.decision.value,
        resolution=resolution,
        resolved_at=datetime.now(timezone.utc),
        reviewer_id=reviewer_id,
        reviewer_notes=reviewer_notes,
        error_category=error_category,
        false_positive_reason=false_positive_reason,
    )


def batch_resolve_flags(
    tracker: FeedbackTracker,
    report: CredibilityReport,
    resolution: Resolution,
    reviewer_id: Optional[str] = None,
    reviewer_notes: Optional[str] = None,
) -> List[FlagResolution]:
    """
    Resolve all flags in a report with the same resolution.

    Useful for bulk accept/reject.
    """
    resolutions = []
    for i in range(len(report.flags)):
        res = create_resolution_from_report(
            report=report,
            flag_index=i,
            resolution=resolution,
            reviewer_id=reviewer_id,
            reviewer_notes=reviewer_notes,
        )
        tracker.record_resolution(res)
        resolutions.append(res)
    return resolutions


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_tracker(db_path: str = "credibility_feedback.db") -> FeedbackTracker:
    """Create a feedback tracker instance."""
    return FeedbackTracker(db_path)


def get_default_tracker() -> FeedbackTracker:
    """Get tracker using default database path."""
    import os
    db_path = os.environ.get("AE_FEEDBACK_DB", "credibility_feedback.db")
    return FeedbackTracker(db_path)
