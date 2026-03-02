"""
Interpretation Space Suggestions Manager

Manages the interpretation_space_suggestions table that tracks search suggestions
from multiple sources (QA, gap predictor, argumentation, etc.) and monitors
whether they are being acted upon.

This supports SearchSuggestionTracker's oversight role in detecting bottlenecks
in the article-discovery pipeline.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict

LOGGER = logging.getLogger(__name__)


@dataclass
class SuggestionRecord:
    """A single search suggestion record."""
    source: str  # 'qa', 'gap_predictor', 'argumentation', 'voi', 'interpretation_space', 'other'
    status: str  # 'proposed', 'identified', 'searching', 'resolved', 'stale'
    description: str  # Human-readable description
    suggested_search: str  # The actual search query
    priority_score: float  # VOI or other priority metric
    article_id: Optional[str] = None  # Linked article if found
    created_at: Optional[str] = None  # ISO timestamp, auto-set if None
    updated_at: Optional[str] = None  # ISO timestamp, auto-set if None
    resolved_at: Optional[str] = None  # ISO timestamp when resolved
    id: Optional[int] = None  # Database ID, set by insert

    def to_tuple(self) -> tuple:
        """Convert to tuple for SQL INSERT (excluding id)."""
        now = datetime.now(timezone.utc).isoformat()
        created = self.created_at or now
        updated = self.updated_at or now
        return (
            self.source,
            self.status,
            self.description,
            self.suggested_search,
            self.priority_score,
            created,
            updated,
            self.resolved_at,
            self.article_id,
        )


class InterpretationSpaceSuggestionsManager:
    """Manages interpretation_space_suggestions table operations."""

    def __init__(self, db_path: str):
        """Initialize manager with database path."""
        self.db_path = Path(db_path)

    def insert_suggestion(self, record: SuggestionRecord) -> int:
        """
        Insert a new suggestion.

        Args:
            record: SuggestionRecord with source, status, description, etc.

        Returns:
            Inserted row ID
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                cursor.execute("""
                    INSERT INTO interpretation_space_suggestions
                    (source, status, description, suggested_search, priority_score,
                     created_at, updated_at, resolved_at, article_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.source,
                    record.status,
                    record.description,
                    record.suggested_search,
                    record.priority_score,
                    record.created_at or now,
                    record.updated_at or now,
                    record.resolved_at,
                    record.article_id,
                ))
                conn.commit()
                return cursor.lastrowid

        except Exception as e:
            LOGGER.error(f"Failed to insert interpretation space suggestion: {e}")
            raise

    def insert_qa_followups(self, followups: List[str], priority_score: float = 0.6) -> int:
        """
        Insert follow-up suggestions from QA handler.

        Args:
            followups: List of follow-up question strings
            priority_score: VOI or priority score (0-1)

        Returns:
            Count of inserted suggestions
        """
        count = 0
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                for followup in followups:
                    if not followup or not followup.strip():
                        continue

                    cursor.execute("""
                        INSERT INTO interpretation_space_suggestions
                        (source, status, description, suggested_search, priority_score,
                         created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        'qa',
                        'proposed',
                        f"QA follow-up suggestion",
                        followup.strip(),
                        priority_score,
                        now,
                        now,
                    ))
                    count += 1

                conn.commit()
                LOGGER.debug(f"Inserted {count} QA follow-up suggestions")

        except Exception as e:
            LOGGER.error(f"Failed to insert QA follow-ups: {e}")
            raise

        return count

    def insert_gap_predictor_suggestions(
        self,
        gaps: List[dict],
        priority_score: Optional[float] = None
    ) -> int:
        """
        Insert gap predictor suggestions.

        Args:
            gaps: List of gap dicts with 'gap_id', 'description', 'suggested_search', 'voi_score'
            priority_score: Override VOI score if provided

        Returns:
            Count of inserted suggestions
        """
        count = 0
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                for gap in gaps:
                    gap_id = gap.get('gap_id', '')
                    description = gap.get('description', '')
                    search = gap.get('suggested_search', '')
                    voi = priority_score if priority_score is not None else gap.get('voi_score', 0.5)

                    if not search or not description:
                        continue

                    cursor.execute("""
                        INSERT INTO interpretation_space_suggestions
                        (source, status, description, suggested_search, priority_score,
                         created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        'gap_predictor',
                        'identified',
                        f"Gap {gap_id}: {description}",
                        search,
                        voi,
                        now,
                        now,
                    ))
                    count += 1

                conn.commit()
                LOGGER.debug(f"Inserted {count} gap predictor suggestions")

        except Exception as e:
            LOGGER.error(f"Failed to insert gap predictor suggestions: {e}")
            raise

        return count

    def insert_argumentation_suggestions(
        self,
        suggestions: List[dict],
        priority_score: float = 0.65
    ) -> int:
        """
        Insert argumentation layer suggestions.

        Args:
            suggestions: List of dicts with 'description', 'search_query'
            priority_score: Default priority for argumentation

        Returns:
            Count of inserted suggestions
        """
        count = 0
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                for suggestion in suggestions:
                    description = suggestion.get('description', '')
                    search_query = suggestion.get('search_query', suggestion.get('suggested_search', ''))

                    if not search_query or not description:
                        continue

                    cursor.execute("""
                        INSERT INTO interpretation_space_suggestions
                        (source, status, description, suggested_search, priority_score,
                         created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        'argumentation',
                        'proposed',
                        description,
                        search_query,
                        priority_score,
                        now,
                        now,
                    ))
                    count += 1

                conn.commit()
                LOGGER.debug(f"Inserted {count} argumentation suggestions")

        except Exception as e:
            LOGGER.error(f"Failed to insert argumentation suggestions: {e}")
            raise

        return count

    def update_suggestion_status(
        self,
        suggestion_id: int,
        new_status: str,
        article_id: Optional[str] = None
    ) -> bool:
        """
        Update status of a suggestion (e.g., from 'proposed' to 'searching' or 'resolved').

        Args:
            suggestion_id: Row ID
            new_status: New status value
            article_id: Optional article ID if resolved

        Returns:
            True if updated, False if not found
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                resolved_at = now if new_status == 'resolved' else None

                cursor.execute("""
                    UPDATE interpretation_space_suggestions
                    SET status = ?, updated_at = ?, resolved_at = ?,
                        article_id = COALESCE(?, article_id)
                    WHERE id = ?
                """, (new_status, now, resolved_at, article_id, suggestion_id))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            LOGGER.error(f"Failed to update suggestion status: {e}")
            raise

    def get_unacted_suggestions_count(self) -> int:
        """Get count of unacted (proposed/identified) suggestions."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM interpretation_space_suggestions
                    WHERE status IN ('proposed', 'identified')
                """)
                return cursor.fetchone()[0] or 0
        except Exception as e:
            LOGGER.error(f"Failed to get unacted count: {e}")
            return 0

    def get_suggestions_by_source(self, source: str, status: Optional[str] = None) -> List[dict]:
        """
        Get suggestions by source, optionally filtered by status.

        Args:
            source: One of: 'qa', 'gap_predictor', 'argumentation', etc.
            status: Optional status filter

        Returns:
            List of suggestion dicts
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if status:
                    cursor.execute("""
                        SELECT * FROM interpretation_space_suggestions
                        WHERE source = ? AND status = ?
                        ORDER BY priority_score DESC, created_at DESC
                    """, (source, status))
                else:
                    cursor.execute("""
                        SELECT * FROM interpretation_space_suggestions
                        WHERE source = ?
                        ORDER BY priority_score DESC, created_at DESC
                    """, (source,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            LOGGER.error(f"Failed to get suggestions by source: {e}")
            return []

    def get_stale_suggestions(self, days: int = 7) -> List[dict]:
        """
        Get suggestions older than N days that haven't been resolved.

        Args:
            days: Age threshold in days

        Returns:
            List of stale suggestion dicts
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cutoff = datetime.fromtimestamp(
                    datetime.now(timezone.utc).timestamp() - (days * 86400),
                    tz=timezone.utc
                ).isoformat()

                cursor.execute("""
                    SELECT * FROM interpretation_space_suggestions
                    WHERE status NOT IN ('resolved', 'stale')
                    AND created_at < ?
                    ORDER BY created_at ASC
                """, (cutoff,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            LOGGER.error(f"Failed to get stale suggestions: {e}")
            return []

    def mark_stale_suggestions(self, days: int = 7) -> int:
        """
        Mark suggestions older than N days as stale if not resolved.

        Args:
            days: Age threshold in days

        Returns:
            Count of marked suggestions
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()

                cutoff = datetime.fromtimestamp(
                    datetime.now(timezone.utc).timestamp() - (days * 86400),
                    tz=timezone.utc
                ).isoformat()

                cursor.execute("""
                    UPDATE interpretation_space_suggestions
                    SET status = 'stale', updated_at = ?
                    WHERE status NOT IN ('resolved', 'stale')
                    AND created_at < ?
                """, (now, cutoff))

                conn.commit()
                return cursor.rowcount

        except Exception as e:
            LOGGER.error(f"Failed to mark stale suggestions: {e}")
            raise

    def clear_suggestions_for_source(self, source: str, status: Optional[str] = None) -> int:
        """
        Clear suggestions from a specific source, optionally filtered by status.

        Useful for refresh operations (e.g., gap predictor regenerates all gaps).

        Args:
            source: Source type
            status: Optional status filter (if None, clears all for source)

        Returns:
            Count of deleted suggestions
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                if status:
                    cursor.execute("""
                        DELETE FROM interpretation_space_suggestions
                        WHERE source = ? AND status = ?
                    """, (source, status))
                else:
                    cursor.execute("""
                        DELETE FROM interpretation_space_suggestions
                        WHERE source = ?
                    """, (source,))

                conn.commit()
                return cursor.rowcount

        except Exception as e:
            LOGGER.error(f"Failed to clear suggestions: {e}")
            raise
