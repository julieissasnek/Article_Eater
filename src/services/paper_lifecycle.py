"""
Paper Lifecycle Tracking Service.

Provides unified tracking for each paper's journey through the processing pipeline:
    Discovery → Search → Retrieval → Storage → Typing → Extraction → Synthesis

Created: 2026-02-09
Version: 23.0.1
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# LIFECYCLE STAGES AND STATUSES
# =============================================================================


class LifecycleStage(str, Enum):
    """Paper processing lifecycle stages."""

    DISCOVERED = "discovered"      # Paper need identified
    SEARCHED = "searched"          # Located via search API
    RETRIEVED = "retrieved"        # PDF/metadata acquired
    STORED = "stored"              # In database with metadata
    TYPED = "typed"                # Article type classified
    EXTRACTING = "extracting"      # LLM extraction in progress
    EXTRACTED = "extracted"        # Claims/rules generated
    SYNTHESIZING = "synthesizing"  # Web integration in progress
    SYNTHESIZED = "synthesized"    # Final web state generated
    ARCHIVED = "archived"          # Processing complete, archived
    FAILED = "failed"              # Terminal failure state


class StageStatus(str, Enum):
    """Status within a lifecycle stage."""

    STARTED = "started"        # Stage just began
    IN_PROGRESS = "in_progress"  # Processing ongoing
    SUCCESS = "success"        # Stage completed successfully
    FAILED = "failed"          # Stage failed (may retry)
    BLOCKED = "blocked"        # Blocked, needs intervention
    SKIPPED = "skipped"        # Stage skipped (e.g., no PDF)


# Valid stage transitions
VALID_TRANSITIONS = {
    LifecycleStage.DISCOVERED: [LifecycleStage.SEARCHED, LifecycleStage.RETRIEVED, LifecycleStage.STORED],
    LifecycleStage.SEARCHED: [LifecycleStage.RETRIEVED, LifecycleStage.FAILED],
    LifecycleStage.RETRIEVED: [LifecycleStage.STORED, LifecycleStage.FAILED],
    LifecycleStage.STORED: [LifecycleStage.TYPED, LifecycleStage.EXTRACTING, LifecycleStage.FAILED],
    LifecycleStage.TYPED: [LifecycleStage.EXTRACTING, LifecycleStage.FAILED],
    LifecycleStage.EXTRACTING: [LifecycleStage.EXTRACTED, LifecycleStage.FAILED],
    LifecycleStage.EXTRACTED: [LifecycleStage.SYNTHESIZING, LifecycleStage.ARCHIVED, LifecycleStage.FAILED],
    LifecycleStage.SYNTHESIZING: [LifecycleStage.SYNTHESIZED, LifecycleStage.FAILED],
    LifecycleStage.SYNTHESIZED: [LifecycleStage.ARCHIVED],
    LifecycleStage.ARCHIVED: [],
    LifecycleStage.FAILED: [LifecycleStage.DISCOVERED],  # Can retry from beginning
}


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class LifecycleEvent:
    """A single lifecycle event/transition."""

    paper_id: str
    stage: LifecycleStage
    status: StageStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    run_id: Optional[str] = None
    job_id: Optional[str] = None
    triggered_by: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    blocking_reason: Optional[str] = None
    n_claims: Optional[int] = None
    n_rules: Optional[int] = None
    n_findings: Optional[int] = None
    text_source: Optional[str] = None
    text_length: Optional[int] = None
    coherence_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value if isinstance(self.stage, LifecycleStage) else self.stage
        d["status"] = self.status.value if isinstance(self.status, StageStatus) else self.status
        return d


@dataclass
class PaperStatus:
    """Current status of a paper in the pipeline."""

    paper_id: str
    title: Optional[str]
    current_stage: LifecycleStage
    stage_since: str
    blocked_reason: Optional[str] = None
    total_transitions: int = 0
    last_activity: Optional[str] = None
    n_claims: int = 0
    n_rules: int = 0
    processing_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["current_stage"] = self.current_stage.value if isinstance(self.current_stage, LifecycleStage) else self.current_stage
        return d


@dataclass
class PipelineHealth:
    """Overall pipeline health summary."""

    total_papers: int = 0
    papers_by_stage: Dict[str, int] = field(default_factory=dict)
    papers_blocked: int = 0
    papers_failed: int = 0
    avg_processing_time_seconds: float = 0.0
    last_7_days_processed: int = 0
    stage_success_rates: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# PAPER LIFECYCLE SERVICE
# =============================================================================


class PaperLifecycleService:
    """
    Service for tracking paper lifecycle through the processing pipeline.

    Usage:
        service = PaperLifecycleService()

        # Start tracking a paper
        service.transition(paper_id, LifecycleStage.DISCOVERED)

        # Update stage with context
        with service.stage_context(paper_id, LifecycleStage.EXTRACTING, run_id="run_123") as ctx:
            # ... do extraction work ...
            ctx.set_metrics(n_claims=5, n_rules=3)

        # Get paper status
        status = service.get_paper_status(paper_id)

        # Get pipeline health
        health = service.get_pipeline_health()
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the lifecycle service."""
        self.db_path = db_path or self._resolve_db_path()
        self._ensure_schema()

    def _resolve_db_path(self) -> Path:
        """Resolve database path from environment."""
        db = os.environ.get("AE_DB_PATH") or os.environ.get("AE_DB") or os.environ.get("DB_PATH")
        if not db:
            db_url = os.environ.get("DB_URL")
            if db_url and db_url.startswith("sqlite:///"):
                db = db_url.replace("sqlite:///", "", 1)
        return Path(db or "ae.db").expanduser().resolve()

    def _ensure_schema(self) -> None:
        """Ensure lifecycle tables exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if paper_lifecycle table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='paper_lifecycle'
            """)
            if not cursor.fetchone():
                # Create tables
                self._create_schema(conn)

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create lifecycle schema tables."""
        cursor = conn.cursor()

        # Try to add columns to articles (may already exist)
        for col, default in [
            ("lifecycle_stage", "'discovered'"),
            ("lifecycle_updated_at", "NULL"),
            ("lifecycle_blocked_reason", "NULL"),
        ]:
            try:
                cursor.execute(f"ALTER TABLE articles ADD COLUMN {col} TEXT DEFAULT {default}")
            except sqlite3.OperationalError:
                pass  # Column already exists

        # Create paper_lifecycle table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_lifecycle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'started',
                started_at TEXT DEFAULT (datetime('now')),
                completed_at TEXT,
                duration_seconds REAL,
                run_id TEXT,
                job_id TEXT,
                triggered_by TEXT,
                details TEXT,
                error_message TEXT,
                blocking_reason TEXT,
                n_claims INTEGER,
                n_rules INTEGER,
                n_findings INTEGER,
                text_source TEXT,
                text_length INTEGER,
                coherence_score REAL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_paper ON paper_lifecycle(paper_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_stage ON paper_lifecycle(stage)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_status ON paper_lifecycle(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paper_lifecycle_started ON paper_lifecycle(started_at DESC)")

        # Create paper_metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_metrics (
                paper_id TEXT PRIMARY KEY,
                first_seen_at TEXT,
                last_processed_at TEXT,
                total_processing_time_seconds REAL,
                n_processing_attempts INTEGER DEFAULT 0,
                n_failures INTEGER DEFAULT 0,
                text_source TEXT,
                text_length INTEGER,
                n_claims INTEGER DEFAULT 0,
                n_rules INTEGER DEFAULT 0,
                n_findings INTEGER DEFAULT 0,
                n_tables_extracted INTEGER DEFAULT 0,
                n_table_claims INTEGER DEFAULT 0,
                extraction_confidence REAL,
                coherence_score REAL,
                has_blocking_issues INTEGER DEFAULT 0,
                n_beliefs_added INTEGER DEFAULT 0,
                n_stubs_created INTEGER DEFAULT 0,
                n_tensions_detected INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)

        conn.commit()
        logger.info("Paper lifecycle schema created")

    @contextmanager
    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # TRANSITION METHODS
    # -------------------------------------------------------------------------

    def transition(
        self,
        paper_id: str,
        stage: LifecycleStage,
        status: StageStatus = StageStatus.STARTED,
        run_id: Optional[str] = None,
        job_id: Optional[str] = None,
        triggered_by: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        blocking_reason: Optional[str] = None,
        **metrics,
    ) -> int:
        """
        Record a lifecycle stage transition.

        Args:
            paper_id: The paper identifier
            stage: Target lifecycle stage
            status: Status within the stage
            run_id: Pipeline run ID
            job_id: Processing queue job ID
            triggered_by: What triggered this transition
            details: Additional context as dict
            error_message: Error message if failed
            blocking_reason: Reason if blocked
            **metrics: Stage-specific metrics (n_claims, n_rules, etc.)

        Returns:
            ID of the lifecycle event record
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert lifecycle event
            cursor.execute("""
                INSERT INTO paper_lifecycle (
                    paper_id, stage, status, started_at, run_id, job_id,
                    triggered_by, details, error_message, blocking_reason,
                    n_claims, n_rules, n_findings, text_source, text_length, coherence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_id,
                stage.value if isinstance(stage, LifecycleStage) else stage,
                status.value if isinstance(status, StageStatus) else status,
                now,
                run_id,
                job_id,
                triggered_by,
                json.dumps(details) if details else None,
                error_message,
                blocking_reason,
                metrics.get("n_claims"),
                metrics.get("n_rules"),
                metrics.get("n_findings"),
                metrics.get("text_source"),
                metrics.get("text_length"),
                metrics.get("coherence_score"),
            ))

            event_id = cursor.lastrowid

            # Update articles table
            cursor.execute("""
                UPDATE articles
                SET lifecycle_stage = ?,
                    lifecycle_updated_at = ?,
                    lifecycle_blocked_reason = ?
                WHERE article_id = ?
            """, (
                stage.value if isinstance(stage, LifecycleStage) else stage,
                now,
                blocking_reason,
                paper_id,
            ))

            conn.commit()
            logger.debug(f"Lifecycle transition: {paper_id} -> {stage.value}:{status.value}")

            return event_id

    def complete_stage(
        self,
        paper_id: str,
        stage: LifecycleStage,
        status: StageStatus = StageStatus.SUCCESS,
        duration_seconds: Optional[float] = None,
        error_message: Optional[str] = None,
        **metrics,
    ) -> None:
        """
        Mark a stage as completed.

        Updates the most recent event for this paper+stage with completion info.
        """
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Find the most recent event for this paper+stage
            cursor.execute("""
                SELECT id FROM paper_lifecycle
                WHERE paper_id = ? AND stage = ? AND completed_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1
            """, (paper_id, stage.value if isinstance(stage, LifecycleStage) else stage))

            row = cursor.fetchone()
            if row:
                event_id = row["id"]

                # Build update query
                updates = ["completed_at = ?", "status = ?"]
                params = [now, status.value if isinstance(status, StageStatus) else status]

                if duration_seconds is not None:
                    updates.append("duration_seconds = ?")
                    params.append(duration_seconds)

                if error_message:
                    updates.append("error_message = ?")
                    params.append(error_message)

                for key in ["n_claims", "n_rules", "n_findings", "text_source", "text_length", "coherence_score"]:
                    if key in metrics:
                        updates.append(f"{key} = ?")
                        params.append(metrics[key])

                params.append(event_id)
                cursor.execute(f"UPDATE paper_lifecycle SET {', '.join(updates)} WHERE id = ?", params)

                # Update articles table status
                if status in [StageStatus.BLOCKED, StageStatus.FAILED]:
                    cursor.execute("""
                        UPDATE articles
                        SET lifecycle_blocked_reason = ?
                        WHERE article_id = ?
                    """, (error_message or "Processing failed", paper_id))

                conn.commit()

    @contextmanager
    def stage_context(
        self,
        paper_id: str,
        stage: LifecycleStage,
        run_id: Optional[str] = None,
        job_id: Optional[str] = None,
        triggered_by: str = "pipeline",
    ):
        """
        Context manager for tracking a stage execution.

        Usage:
            with service.stage_context(paper_id, LifecycleStage.EXTRACTING, run_id="123") as ctx:
                # ... do work ...
                ctx.set_metrics(n_claims=5, n_rules=3)

        The stage is automatically marked as SUCCESS on clean exit, FAILED on exception.
        """
        start_time = time.time()
        metrics = {}

        class StageContext:
            def set_metrics(self, **kwargs):
                metrics.update(kwargs)

        ctx = StageContext()

        # Record stage start
        self.transition(
            paper_id=paper_id,
            stage=stage,
            status=StageStatus.IN_PROGRESS,
            run_id=run_id,
            job_id=job_id,
            triggered_by=triggered_by,
        )

        try:
            yield ctx

            # Success
            duration = time.time() - start_time
            self.complete_stage(
                paper_id=paper_id,
                stage=stage,
                status=StageStatus.SUCCESS,
                duration_seconds=duration,
                **metrics,
            )

        except Exception as e:
            # Failure
            duration = time.time() - start_time
            self.complete_stage(
                paper_id=paper_id,
                stage=stage,
                status=StageStatus.FAILED,
                duration_seconds=duration,
                error_message=str(e),
                **metrics,
            )
            raise

    # -------------------------------------------------------------------------
    # QUERY METHODS
    # -------------------------------------------------------------------------

    def get_paper_status(self, paper_id: str) -> Optional[PaperStatus]:
        """Get current status of a paper."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    a.article_id,
                    a.title,
                    a.lifecycle_stage,
                    a.lifecycle_updated_at,
                    a.lifecycle_blocked_reason,
                    (SELECT COUNT(*) FROM paper_lifecycle WHERE paper_id = a.article_id) as total_transitions,
                    (SELECT MAX(started_at) FROM paper_lifecycle WHERE paper_id = a.article_id) as last_activity,
                    COALESCE(m.n_claims, 0) as n_claims,
                    COALESCE(m.n_rules, 0) as n_rules,
                    COALESCE(m.total_processing_time_seconds, 0) as processing_time
                FROM articles a
                LEFT JOIN paper_metrics m ON m.paper_id = a.article_id
                WHERE a.article_id = ?
            """, (paper_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return PaperStatus(
                paper_id=row["article_id"],
                title=row["title"],
                current_stage=LifecycleStage(row["lifecycle_stage"]) if row["lifecycle_stage"] else LifecycleStage.DISCOVERED,
                stage_since=row["lifecycle_updated_at"] or "",
                blocked_reason=row["lifecycle_blocked_reason"],
                total_transitions=row["total_transitions"] or 0,
                last_activity=row["last_activity"],
                n_claims=row["n_claims"],
                n_rules=row["n_rules"],
                processing_time_seconds=row["processing_time"],
            )

    def get_paper_history(self, paper_id: str) -> List[LifecycleEvent]:
        """Get full lifecycle history for a paper."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM paper_lifecycle
                WHERE paper_id = ?
                ORDER BY started_at ASC
            """, (paper_id,))

            events = []
            for row in cursor.fetchall():
                events.append(LifecycleEvent(
                    paper_id=row["paper_id"],
                    stage=LifecycleStage(row["stage"]),
                    status=StageStatus(row["status"]),
                    started_at=row["started_at"],
                    completed_at=row["completed_at"],
                    duration_seconds=row["duration_seconds"],
                    run_id=row["run_id"],
                    job_id=row["job_id"],
                    triggered_by=row["triggered_by"],
                    details=json.loads(row["details"]) if row["details"] else None,
                    error_message=row["error_message"],
                    blocking_reason=row["blocking_reason"],
                    n_claims=row["n_claims"],
                    n_rules=row["n_rules"],
                    n_findings=row["n_findings"],
                    text_source=row["text_source"],
                    text_length=row["text_length"],
                    coherence_score=row["coherence_score"],
                ))

            return events

    def get_papers_by_stage(
        self,
        stage: Optional[LifecycleStage] = None,
        status: Optional[StageStatus] = None,
        limit: int = 100,
    ) -> List[PaperStatus]:
        """Get papers filtered by stage and/or status."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    a.article_id,
                    a.title,
                    a.lifecycle_stage,
                    a.lifecycle_updated_at,
                    a.lifecycle_blocked_reason,
                    (SELECT COUNT(*) FROM paper_lifecycle WHERE paper_id = a.article_id) as total_transitions,
                    (SELECT MAX(started_at) FROM paper_lifecycle WHERE paper_id = a.article_id) as last_activity
                FROM articles a
                WHERE 1=1
            """
            params = []

            if stage:
                query += " AND a.lifecycle_stage = ?"
                params.append(stage.value if isinstance(stage, LifecycleStage) else stage)

            if status == StageStatus.BLOCKED:
                query += " AND a.lifecycle_blocked_reason IS NOT NULL"

            query += " ORDER BY a.lifecycle_updated_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            papers = []
            for row in cursor.fetchall():
                papers.append(PaperStatus(
                    paper_id=row["article_id"],
                    title=row["title"],
                    current_stage=LifecycleStage(row["lifecycle_stage"]) if row["lifecycle_stage"] else LifecycleStage.DISCOVERED,
                    stage_since=row["lifecycle_updated_at"] or "",
                    blocked_reason=row["lifecycle_blocked_reason"],
                    total_transitions=row["total_transitions"] or 0,
                    last_activity=row["last_activity"],
                ))

            return papers

    def get_blocked_papers(self, limit: int = 50) -> List[PaperStatus]:
        """Get papers that are blocked and need attention."""
        return self.get_papers_by_stage(status=StageStatus.BLOCKED, limit=limit)

    def get_pipeline_health(self) -> PipelineHealth:
        """Get overall pipeline health summary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            health = PipelineHealth()

            # Total papers
            cursor.execute("SELECT COUNT(*) FROM articles")
            health.total_papers = cursor.fetchone()[0]

            # Papers by stage
            cursor.execute("""
                SELECT lifecycle_stage, COUNT(*) as count
                FROM articles
                WHERE lifecycle_stage IS NOT NULL
                GROUP BY lifecycle_stage
            """)
            for row in cursor.fetchall():
                health.papers_by_stage[row["lifecycle_stage"]] = row["count"]

            # Blocked papers
            cursor.execute("SELECT COUNT(*) FROM articles WHERE lifecycle_blocked_reason IS NOT NULL")
            health.papers_blocked = cursor.fetchone()[0]

            # Failed in last 7 days
            cursor.execute("""
                SELECT COUNT(DISTINCT paper_id) FROM paper_lifecycle
                WHERE status = 'failed'
                AND started_at >= datetime('now', '-7 days')
            """)
            health.papers_failed = cursor.fetchone()[0]

            # Average processing time
            cursor.execute("""
                SELECT AVG(total_processing_time_seconds)
                FROM paper_metrics
                WHERE total_processing_time_seconds > 0
            """)
            row = cursor.fetchone()
            health.avg_processing_time_seconds = row[0] or 0.0

            # Last 7 days processed
            cursor.execute("""
                SELECT COUNT(DISTINCT paper_id) FROM paper_lifecycle
                WHERE status = 'success'
                AND started_at >= datetime('now', '-7 days')
            """)
            health.last_7_days_processed = cursor.fetchone()[0]

            # Success rates by stage
            cursor.execute("""
                SELECT stage,
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes,
                       COUNT(*) as total
                FROM paper_lifecycle
                WHERE started_at >= datetime('now', '-30 days')
                GROUP BY stage
            """)
            for row in cursor.fetchall():
                if row["total"] > 0:
                    health.stage_success_rates[row["stage"]] = row["successes"] / row["total"]

            return health

    # -------------------------------------------------------------------------
    # METRICS METHODS
    # -------------------------------------------------------------------------

    def update_paper_metrics(
        self,
        paper_id: str,
        **metrics,
    ) -> None:
        """Update aggregate metrics for a paper."""
        now = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if metrics record exists
            cursor.execute("SELECT paper_id FROM paper_metrics WHERE paper_id = ?", (paper_id,))
            exists = cursor.fetchone() is not None

            if exists:
                # Build update query
                updates = ["updated_at = ?", "last_processed_at = ?"]
                params = [now, now]

                for key, value in metrics.items():
                    if value is not None:
                        updates.append(f"{key} = ?")
                        params.append(value)

                params.append(paper_id)
                cursor.execute(f"UPDATE paper_metrics SET {', '.join(updates)} WHERE paper_id = ?", params)
            else:
                # Insert new record
                columns = ["paper_id", "first_seen_at", "last_processed_at", "updated_at"]
                values = [paper_id, now, now, now]

                for key, value in metrics.items():
                    if value is not None:
                        columns.append(key)
                        values.append(value)

                placeholders = ", ".join(["?"] * len(values))
                cursor.execute(
                    f"INSERT INTO paper_metrics ({', '.join(columns)}) VALUES ({placeholders})",
                    values
                )

            conn.commit()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


_service_instance: Optional[PaperLifecycleService] = None


def get_lifecycle_service() -> PaperLifecycleService:
    """Get the singleton lifecycle service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = PaperLifecycleService()
    return _service_instance


def track_paper_stage(
    paper_id: str,
    stage: LifecycleStage,
    run_id: Optional[str] = None,
    **kwargs,
) -> int:
    """Convenience function to track a paper stage transition."""
    return get_lifecycle_service().transition(paper_id, stage, run_id=run_id, **kwargs)


def get_paper_lifecycle_status(paper_id: str) -> Optional[PaperStatus]:
    """Convenience function to get paper status."""
    return get_lifecycle_service().get_paper_status(paper_id)
