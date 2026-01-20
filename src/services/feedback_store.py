"""
Unified Feedback Store for Article Eater Post-Quinean.

Phase E: Implementation (Sprint B)
Per Lampson critique: Single feedback store instead of three.

This module provides centralized storage for feedback from all system
components (credibility testing, explanations, search), enabling:
1. Cross-component analysis
2. Single schema to maintain
3. Unified migration path

Date: January 20, 2026
"""

import sqlite3
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Literal
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SystemFeedback:
    """
    Unified feedback record for all system operations.

    Per Lampson: Keep it simple. One structure for all feedback types.
    Component-specific details go in the 'details' field.
    """
    feedback_id: str
    timestamp: datetime
    component: Literal["credibility", "explanation", "search"]
    operation_id: str  # Links to specific check/explanation/search

    # Core outcome
    outcome: Literal["positive", "negative", "neutral", "deferred"]

    # Component-specific details (flexible JSON)
    details: Dict[str, Any] = field(default_factory=dict)

    # For reviewer
    reviewer_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'feedback_id': self.feedback_id,
            'timestamp': self.timestamp.isoformat(),
            'component': self.component,
            'operation_id': self.operation_id,
            'outcome': self.outcome,
            'details': self.details,
            'reviewer_notes': self.reviewer_notes
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'SystemFeedback':
        """Create from dictionary."""
        return cls(
            feedback_id=d['feedback_id'],
            timestamp=datetime.fromisoformat(d['timestamp']),
            component=d['component'],
            operation_id=d['operation_id'],
            outcome=d['outcome'],
            details=d.get('details', {}),
            reviewer_notes=d.get('reviewer_notes')
        )


# =============================================================================
# FEEDBACK STORE
# =============================================================================

class FeedbackStore:
    """
    Unified storage for all system feedback.

    Supports:
    - Recording feedback from credibility, explanation, search components
    - Querying by component, outcome, time range
    - Cross-component analysis
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "system_feedback.db"):
        """
        Initialize feedback store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    details TEXT,  -- JSON
                    reviewer_notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Indices for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_component
                ON feedback(component)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_outcome
                ON feedback(outcome)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
                ON feedback(timestamp)
            """)

            # Schema version tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_info (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute("""
                INSERT OR REPLACE INTO schema_info (key, value)
                VALUES ('version', ?)
            """, (str(self.SCHEMA_VERSION),))

            conn.commit()

    @contextmanager
    def _connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def record(self, feedback: SystemFeedback) -> None:
        """
        Record a feedback entry.

        Args:
            feedback: The feedback to record
        """
        with self._connection() as conn:
            conn.execute("""
                INSERT INTO feedback
                (feedback_id, timestamp, component, operation_id, outcome, details, reviewer_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.feedback_id,
                feedback.timestamp.isoformat(),
                feedback.component,
                feedback.operation_id,
                feedback.outcome,
                json.dumps(feedback.details),
                feedback.reviewer_notes
            ))
            conn.commit()

        logger.debug(f"Recorded feedback {feedback.feedback_id} for {feedback.component}")

    def get_by_id(self, feedback_id: str) -> Optional[SystemFeedback]:
        """Get feedback by ID."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM feedback WHERE feedback_id = ?",
                (feedback_id,)
            ).fetchone()

            if row:
                return self._row_to_feedback(row)
            return None

    def get_by_component(
        self,
        component: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[SystemFeedback]:
        """Get all feedback for a component."""
        with self._connection() as conn:
            rows = conn.execute("""
                SELECT * FROM feedback
                WHERE component = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (component, limit, offset)).fetchall()

            return [self._row_to_feedback(row) for row in rows]

    def get_by_outcome(
        self,
        outcome: str,
        component: Optional[str] = None,
        limit: int = 100
    ) -> List[SystemFeedback]:
        """Get feedback by outcome, optionally filtered by component."""
        with self._connection() as conn:
            if component:
                rows = conn.execute("""
                    SELECT * FROM feedback
                    WHERE outcome = ? AND component = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (outcome, component, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM feedback
                    WHERE outcome = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (outcome, limit)).fetchall()

            return [self._row_to_feedback(row) for row in rows]

    def get_recent(
        self,
        since: datetime,
        component: Optional[str] = None
    ) -> List[SystemFeedback]:
        """Get feedback since a timestamp."""
        with self._connection() as conn:
            if component:
                rows = conn.execute("""
                    SELECT * FROM feedback
                    WHERE timestamp >= ? AND component = ?
                    ORDER BY timestamp DESC
                """, (since.isoformat(), component)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM feedback
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (since.isoformat(),)).fetchall()

            return [self._row_to_feedback(row) for row in rows]

    def _row_to_feedback(self, row: sqlite3.Row) -> SystemFeedback:
        """Convert database row to SystemFeedback."""
        return SystemFeedback(
            feedback_id=row['feedback_id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            component=row['component'],
            operation_id=row['operation_id'],
            outcome=row['outcome'],
            details=json.loads(row['details']) if row['details'] else {},
            reviewer_notes=row['reviewer_notes']
        )

    # =========================================================================
    # ANALYTICS
    # =========================================================================

    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """
        Get statistics for a component.

        Returns counts by outcome and other metrics.
        """
        with self._connection() as conn:
            # Outcome distribution
            rows = conn.execute("""
                SELECT outcome, COUNT(*) as count
                FROM feedback
                WHERE component = ?
                GROUP BY outcome
            """, (component,)).fetchall()

            outcome_counts = {row['outcome']: row['count'] for row in rows}
            total = sum(outcome_counts.values())

            return {
                'component': component,
                'total_feedback': total,
                'outcome_counts': outcome_counts,
                'positive_rate': outcome_counts.get('positive', 0) / total if total > 0 else 0,
                'negative_rate': outcome_counts.get('negative', 0) / total if total > 0 else 0,
            }

    def cross_component_analysis(self) -> Dict[str, Any]:
        """
        Analyze patterns across components.

        Per Lampson: This is the payoff of unified storage.
        """
        with self._connection() as conn:
            # Overall stats by component
            rows = conn.execute("""
                SELECT component, outcome, COUNT(*) as count
                FROM feedback
                GROUP BY component, outcome
            """).fetchall()

            component_outcomes: Dict[str, Dict[str, int]] = {}
            for row in rows:
                comp = row['component']
                if comp not in component_outcomes:
                    component_outcomes[comp] = {}
                component_outcomes[comp][row['outcome']] = row['count']

            # Correlation: Do credibility flags correlate with search utility?
            # (This would require matching operation_ids across components)

            return {
                'component_outcomes': component_outcomes,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }

    def get_all_feedback(self, limit: int = 1000) -> List[SystemFeedback]:
        """Get all feedback (for testing/export)."""
        with self._connection() as conn:
            rows = conn.execute("""
                SELECT * FROM feedback
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()

            return [self._row_to_feedback(row) for row in rows]

    def clear_all(self) -> int:
        """
        Clear all feedback (for testing).

        Returns number of records deleted.
        """
        with self._connection() as conn:
            result = conn.execute("DELETE FROM feedback")
            count = result.rowcount
            conn.commit()
            return count


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_feedback_id(component: str, operation_id: str) -> str:
    """Create a unique feedback ID."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"fb_{component}_{timestamp}_{operation_id[:8]}"


def create_credibility_feedback(
    operation_id: str,
    outcome: Literal["positive", "negative", "neutral", "deferred"],
    flag_type: Optional[str] = None,
    was_correct: Optional[bool] = None,
    reviewer_notes: Optional[str] = None
) -> SystemFeedback:
    """
    Create feedback for a credibility check.

    Args:
        operation_id: The credibility report ID
        outcome: Whether the flag was correct (positive=true positive, negative=false positive)
        flag_type: The type of flag that was raised
        was_correct: Was the system's decision correct?
        reviewer_notes: Optional notes from reviewer
    """
    return SystemFeedback(
        feedback_id=create_feedback_id("credibility", operation_id),
        timestamp=datetime.now(timezone.utc),
        component="credibility",
        operation_id=operation_id,
        outcome=outcome,
        details={
            'flag_type': flag_type,
            'was_correct': was_correct,
        },
        reviewer_notes=reviewer_notes
    )


def create_explanation_feedback(
    operation_id: str,
    outcome: Literal["positive", "negative", "neutral", "deferred"],
    pattern_used: Optional[str] = None,
    comprehension_score: Optional[float] = None,
    reviewer_notes: Optional[str] = None
) -> SystemFeedback:
    """
    Create feedback for an explanation.

    Args:
        operation_id: The explanation request ID
        outcome: Whether the explanation was helpful
        pattern_used: Which explanation pattern was used
        comprehension_score: User-reported comprehension (0-1)
        reviewer_notes: Optional notes
    """
    return SystemFeedback(
        feedback_id=create_feedback_id("explanation", operation_id),
        timestamp=datetime.now(timezone.utc),
        component="explanation",
        operation_id=operation_id,
        outcome=outcome,
        details={
            'pattern_used': pattern_used,
            'comprehension_score': comprehension_score,
        },
        reviewer_notes=reviewer_notes
    )


def create_search_feedback(
    operation_id: str,
    outcome: Literal["positive", "negative", "neutral", "deferred"],
    gap_type: Optional[str] = None,
    strategy_used: Optional[str] = None,
    papers_found: int = 0,
    papers_useful: int = 0,
    reviewer_notes: Optional[str] = None
) -> SystemFeedback:
    """
    Create feedback for a search operation.

    Args:
        operation_id: The search operation ID
        outcome: Whether the search was useful
        gap_type: Type of gap being filled
        strategy_used: Search strategy employed
        papers_found: Number of papers returned
        papers_useful: Number of papers that were actually useful
        reviewer_notes: Optional notes
    """
    return SystemFeedback(
        feedback_id=create_feedback_id("search", operation_id),
        timestamp=datetime.now(timezone.utc),
        component="search",
        operation_id=operation_id,
        outcome=outcome,
        details={
            'gap_type': gap_type,
            'strategy_used': strategy_used,
            'papers_found': papers_found,
            'papers_useful': papers_useful,
            'precision': papers_useful / papers_found if papers_found > 0 else 0,
        },
        reviewer_notes=reviewer_notes
    )
