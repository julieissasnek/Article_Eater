"""
OVERSEER v2 Management Layer

Expands OVERSEER from health monitoring into full pipeline management.
Monitors article discovery, PDF acquisition, extraction, integration, and QA flows.
Tracks suggestion backlogs and recommends panel convocation.

David Kirsh: "OVERSEER is not just a health monitor — it's a MANAGER.
It needs to know about all the pipelines, track whether work is flowing,
detect bottlenecks, and recommend actions (including convening panels)."

Core Responsibilities:
1. PipelineRegistry: Track all 6 major pipelines
2. QueueHealthMonitor: Detect research queue problems
3. ArticleFlowMonitor: Measure flow through suggestion→search→PDF→extraction→integration
4. SearchSuggestionTracker: Alert if suggestions are piling up
5. ExtractionQueueMonitor: Alert if PDFs awaiting encoding
6. PanelConvocationService: Determine when panel review is needed
7. ManagementDashboard: Aggregate into single-page view
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sqlite3
import json

from src.services.overseer_management_models import (
    PipelineStatus,
    PipelineRecord,
    QueueHealthReport,
    ArticleFlowStageMetrics,
    ArticleFlowReport,
    SuggestionAge,
    SuggestionBacklogReport,
    GapSourceType,
    ExtractionStage,
    ExtractionQueueMetrics,
    ExtractionQueueReport,
    PanelRecommendation,
    ManagementReport,
    PipelineStatusSummary,
    MetricTrend,
    SystemHealthTrend,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Registry
# ============================================================================

class PipelineRegistry:
    """
    Registry and status tracker for all system pipelines.

    Pipelines:
    1. article-discovery: GapPredictor → ResearchQueue → AutomatedSearcher/ZoteroWatcher
    2. pdf-acquisition: SearchResult → PDFRetrieval → local storage
    3. extraction: PDF → Gemini extraction → validation → template encoding
    4. integration: Extracted findings → web_of_belief → BN update → OVERSEER check
    5. qa-audit: QA handler → theory guides → interpretation space
    6. nightly-maintenance: snapshot → cache refresh → health report
    """

    def __init__(self, overseer_db_path: str):
        self.db_path = Path(overseer_db_path)
        self._init_registry()

    def _init_registry(self) -> None:
        """Initialize pipeline registry tables."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS management_pipelines (
                        pipeline_id TEXT PRIMARY KEY,
                        display_name TEXT NOT NULL,
                        components TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_heartbeat TEXT,
                        status TEXT DEFAULT 'unknown',
                        queue_depth INTEGER DEFAULT 0,
                        throughput_24h INTEGER DEFAULT 0,
                        error_rate_24h REAL DEFAULT 0.0,
                        bottleneck TEXT,
                        last_error TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS management_pipeline_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pipeline_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        status_before TEXT,
                        status_after TEXT,
                        details TEXT,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (pipeline_id) REFERENCES management_pipelines(pipeline_id)
                    )
                """)
                conn.commit()

            # Register default pipelines if not present
            self._register_default_pipelines()
        except Exception as e:
            logger.error(f"Failed to initialize pipeline registry: {e}")

    def _register_default_pipelines(self) -> None:
        """Register the 6 standard pipelines if not already present."""
        pipelines = [
            ("article-discovery", "Article Discovery",
             ["gap-predictor", "research-queue", "automated-searcher", "zotero-watcher"]),
            ("pdf-acquisition", "PDF Acquisition",
             ["search-result-processor", "pdf-retriever", "local-storage"]),
            ("extraction", "Extraction",
             ["pdf-loader", "gemini-extraction", "extraction-validator", "template-encoder"]),
            ("integration", "Integration",
             ["extraction-to-web", "web-of-belief", "bn-update", "overseer-check"]),
            ("qa-audit", "QA & Audit",
             ["qa-handler", "theory-guides", "interpretation-space"]),
            ("nightly-maintenance", "Nightly Maintenance",
             ["snapshot", "cache-refresh", "health-report", "archive"]),
        ]

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            for pipeline_id, display_name, components in pipelines:
                cursor.execute(
                    "SELECT pipeline_id FROM management_pipelines WHERE pipeline_id = ?",
                    (pipeline_id,)
                )
                if not cursor.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    cursor.execute("""
                        INSERT INTO management_pipelines
                        (pipeline_id, display_name, components, created_at, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (pipeline_id, display_name, json.dumps(components), now, "unknown"))
            conn.commit()

    def register_heartbeat(self, pipeline_id: str, status: PipelineStatus,
                          queue_depth: int = 0, throughput_24h: int = 0,
                          error_rate_24h: float = 0.0, bottleneck: Optional[str] = None,
                          last_error: Optional[str] = None) -> None:
        """Register a pipeline heartbeat."""
        now = datetime.now(timezone.utc).isoformat()
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE management_pipelines
                    SET last_heartbeat = ?, status = ?, queue_depth = ?,
                        throughput_24h = ?, error_rate_24h = ?, bottleneck = ?,
                        last_error = ?
                    WHERE pipeline_id = ?
                """, (now, status.value, queue_depth, throughput_24h, error_rate_24h,
                      bottleneck, last_error, pipeline_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to register heartbeat for {pipeline_id}: {e}")

    def get_all_pipelines(self) -> List[PipelineRecord]:
        """Get all pipeline records."""
        pipelines = []
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM management_pipelines")
                rows = cursor.fetchall()

                for row in rows:
                    (pipeline_id, display_name, components_json, created_at,
                     last_heartbeat, status, queue_depth, throughput_24h,
                     error_rate_24h, bottleneck, last_error) = row

                    last_hb = (datetime.fromisoformat(last_heartbeat)
                              if last_heartbeat else datetime.now(timezone.utc))
                    pipelines.append(PipelineRecord(
                        pipeline_id=pipeline_id,
                        display_name=display_name,
                        components=json.loads(components_json),
                        last_heartbeat=last_hb,
                        status=PipelineStatus(status or "unknown"),
                        queue_depth=queue_depth or 0,
                        throughput_24h=throughput_24h or 0,
                        error_rate_24h=error_rate_24h or 0.0,
                        bottleneck=bottleneck,
                        last_error=last_error,
                    ))
        except Exception as e:
            logger.error(f"Failed to fetch pipelines: {e}")

        return pipelines

    def get_pipeline_status_summary(self) -> PipelineStatusSummary:
        """Get quick summary of all pipeline statuses."""
        pipelines = self.get_all_pipelines()
        now = datetime.now(timezone.utc)

        status_by_pipeline = {p.pipeline_id: p.status.value for p in pipelines}

        return PipelineStatusSummary(
            timestamp=now,
            total_pipelines=len(pipelines),
            healthy_count=sum(1 for p in pipelines if p.status == PipelineStatus.HEALTHY),
            degraded_count=sum(1 for p in pipelines if p.status == PipelineStatus.DEGRADED),
            stalled_count=sum(1 for p in pipelines if p.status == PipelineStatus.STALLED),
            blocked_count=sum(1 for p in pipelines if p.status == PipelineStatus.BLOCKED),
            unknown_count=sum(1 for p in pipelines if p.status == PipelineStatus.UNKNOWN),
            status_by_pipeline=status_by_pipeline,
        )


# ============================================================================
# Queue Health Monitor
# ============================================================================

class QueueHealthMonitor:
    """Monitor the research queue for health and backlog problems."""

    def __init__(self, web_db_path: str):
        self.web_db_path = Path(web_db_path)

    def check_queue_health(self) -> QueueHealthReport:
        """
        Assess research queue health.

        Returns:
            QueueHealthReport with:
            - How many targets are OPEN (unassigned)?
            - How many are SEARCHING (in progress) for how long?
            - What's the search→found conversion rate?
            - Are suggestions piling up?
            - What's avg time from OPEN → FOUND → CLOSED?
        """
        now = datetime.now(timezone.utc)

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Query ResearchTarget table from queue/models.py
                # Assumes table: research_targets
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count,
                        SUM(CASE WHEN status = 'searching' THEN 1 ELSE 0 END) as searching_count,
                        SUM(CASE WHEN status = 'found' THEN 1 ELSE 0 END) as found_count,
                        SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_count,
                        SUM(CASE WHEN status = 'stale' THEN 1 ELSE 0 END) as stale_count
                    FROM research_targets
                """)
                row = cursor.fetchone()

                if not row or row[0] is None:
                    # Table doesn't exist or empty
                    return self._empty_queue_report(now)

                (total, open_c, searching_c, found_c, closed_c, stale_c) = row
                open_c = open_c or 0
                searching_c = searching_c or 0
                found_c = found_c or 0
                closed_c = closed_c or 0
                stale_c = stale_c or 0

                # Compute conversion rate
                if total > 0:
                    search_to_found_rate = found_c / (open_c + searching_c + found_c) if (open_c + searching_c + found_c) > 0 else 0.0
                else:
                    search_to_found_rate = 0.0

                # Query oldest targets
                cursor.execute("""
                    SELECT created_at, status FROM research_targets
                    WHERE status IN ('open', 'searching')
                    ORDER BY created_at ASC
                    LIMIT 1
                """)
                oldest_row = cursor.fetchone()
                if oldest_row and oldest_row[0]:
                    oldest_created = datetime.fromisoformat(oldest_row[0])
                    oldest_open_hours = (now - oldest_created).total_seconds() / 3600
                else:
                    oldest_open_hours = 0.0

                # Query avg time metrics (simplified)
                cursor.execute("""
                    SELECT
                        AVG(JULIANDAY(completed_at) - JULIANDAY(created_at)) * 24 as avg_hours_to_found
                    FROM research_targets
                    WHERE status IN ('found', 'closed') AND completed_at IS NOT NULL
                """)
                avg_row = cursor.fetchone()
                avg_time_to_found = (avg_row[0] or 0.0) if avg_row else 0.0

                # Determine health status
                if open_c > 20 or oldest_open_hours > 168:  # >20 open or >1 week old
                    health_status = "RED"
                elif open_c > 10 or oldest_open_hours > 72:
                    health_status = "YELLOW"
                else:
                    health_status = "OK"

                recommendations = []
                if open_c > 10:
                    recommendations.append(f"High number of open targets ({open_c}); "
                                          "consider increasing searcher capacity")
                if oldest_open_hours > 72:
                    recommendations.append(f"Oldest target age: {oldest_open_hours:.1f} hours; "
                                          "may indicate stalled search")

                return QueueHealthReport(
                    timestamp=now,
                    total_targets=total,
                    open_targets=open_c,
                    searching_targets=searching_c,
                    found_targets=found_c,
                    closed_targets=closed_c,
                    stale_targets=stale_c,
                    search_to_found_rate=search_to_found_rate,
                    avg_time_open_to_found_hours=avg_time_to_found,
                    avg_time_open_to_closed_hours=avg_time_to_found,  # simplified
                    oldest_open_target_hours=oldest_open_hours,
                    oldest_searching_target_hours=oldest_open_hours,  # simplified
                    health_status=health_status,
                    recommendations=recommendations,
                )

        except Exception as e:
            logger.error(f"Failed to check queue health: {e}")
            return self._empty_queue_report(now)

    def _empty_queue_report(self, now: datetime) -> QueueHealthReport:
        """Return default empty queue report."""
        return QueueHealthReport(
            timestamp=now,
            total_targets=0,
            open_targets=0,
            searching_targets=0,
            found_targets=0,
            closed_targets=0,
            stale_targets=0,
            search_to_found_rate=0.0,
            avg_time_open_to_found_hours=0.0,
            avg_time_open_to_closed_hours=0.0,
            oldest_open_target_hours=0.0,
            oldest_searching_target_hours=0.0,
            health_status="UNKNOWN",
            recommendations=["Research queue table not found or empty"],
        )


# ============================================================================
# Article Flow Monitor
# ============================================================================

class ArticleFlowMonitor:
    """Track article flow through suggestion→search→PDF→extraction→integration."""

    def __init__(self, web_db_path: str):
        self.web_db_path = Path(web_db_path)

    def check_article_flow(self) -> ArticleFlowReport:
        """
        Measure flow through each pipeline stage.

        Returns:
            ArticleFlowReport with metrics for:
            - Suggestion→search stage
            - Search→PDF stage
            - PDF→extraction stage
            - Extraction→integration stage
        """
        now = datetime.now(timezone.utc)

        stages = [
            self._measure_stage("suggestion-search", "research_targets", "status",
                               "open", "found"),
            self._measure_stage("pdf-extraction", "papers", "extraction_status",
                               "pdf_acquired", "extracted"),
            self._measure_stage("extraction-integration", "papers", "integration_status",
                               "extracted", "integrated"),
        ]

        total_in_system = sum(s.items_waiting + s.items_in_progress for s in stages)
        bottleneck_stage = max(stages, key=lambda s: s.bottleneck_score, default=None)

        total_completed_24h = sum(s.items_completed_24h for s in stages)
        total_completed_7d = sum(s.items_completed_7d for s in stages)

        flow_efficiency = sum(s.items_completed_24h for s in stages) / max(total_in_system, 1)

        health_status = "OK"
        if bottleneck_stage and bottleneck_stage.bottleneck_score > 0.7:
            health_status = "RED"
        elif bottleneck_stage and bottleneck_stage.bottleneck_score > 0.4:
            health_status = "YELLOW"

        recommendations = []
        if bottleneck_stage:
            recommendations.append(f"Bottleneck detected in {bottleneck_stage.stage_name}: "
                                  f"investigate {bottleneck_stage.bottleneck_component}")

        return ArticleFlowReport(
            timestamp=now,
            stages=stages,
            overall_throughput_24h=total_completed_24h,
            overall_throughput_7d=total_completed_7d,
            total_items_in_system=total_in_system,
            critical_bottleneck=bottleneck_stage.bottleneck_component if bottleneck_stage else None,
            flow_efficiency=flow_efficiency,
            health_status=health_status,
            recommendations=recommendations,
        )

    def _measure_stage(self, stage_name: str, table: str, status_column: str,
                       waiting_status: str, completed_status: str) -> ArticleFlowStageMetrics:
        """Measure metrics for one flow stage."""
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Items waiting (status = waiting_status)
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} = ?
                """, (waiting_status,))
                waiting = cursor.fetchone()[0] or 0

                # Items in progress
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} NOT IN (?, ?)
                """, (waiting_status, completed_status))
                in_progress = cursor.fetchone()[0] or 0

                # Items completed in various time windows
                # (assumes updated_at column exists)
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} = ? AND updated_at > ?
                """, (completed_status, day_ago.isoformat()))
                completed_24h = cursor.fetchone()[0] or 0

                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} = ? AND updated_at > ?
                """, (completed_status, week_ago.isoformat()))
                completed_7d = cursor.fetchone()[0] or 0

                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} = ? AND updated_at > ?
                """, (completed_status, month_ago.isoformat()))
                completed_30d = cursor.fetchone()[0] or 0

                # Failure rate (simplified: assume failures are marked with error status)
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table}
                    WHERE {status_column} LIKE '%error%' OR {status_column} = 'failed'
                """)
                failures_24h = cursor.fetchone()[0] or 0
                failure_rate = failures_24h / max(waiting + in_progress, 1)

                # Avg processing time (simplified)
                cursor.execute(f"""
                    SELECT AVG(JULIANDAY(updated_at) - JULIANDAY(created_at)) * 24
                    FROM {table}
                    WHERE {status_column} = ?
                """, (completed_status,))
                avg_time = cursor.fetchone()[0] or 0.0

                # Bottleneck score: ratio of waiting to completed
                bottleneck_score = waiting / max(completed_24h + 1, 1)

                return ArticleFlowStageMetrics(
                    stage_name=stage_name,
                    items_waiting=waiting,
                    items_in_progress=in_progress,
                    items_completed_24h=completed_24h,
                    items_completed_7d=completed_7d,
                    items_completed_30d=completed_30d,
                    failure_rate_24h=min(failure_rate, 1.0),
                    avg_processing_time_hours=avg_time,
                    bottleneck_score=min(bottleneck_score, 1.0),
                    bottleneck_component=None,  # TODO: identify slow service
                )

        except Exception as e:
            logger.error(f"Failed to measure stage {stage_name}: {e}")
            return ArticleFlowStageMetrics(
                stage_name=stage_name,
                items_waiting=0,
                items_in_progress=0,
                items_completed_24h=0,
                items_completed_7d=0,
                items_completed_30d=0,
                failure_rate_24h=0.0,
                avg_processing_time_hours=0.0,
                bottleneck_score=0.0,
                bottleneck_component=None,
            )


# ============================================================================
# Search Suggestion Tracker
# ============================================================================

class SearchSuggestionTracker:
    """Monitor whether gap-driven and VOI-driven search suggestions are being acted on."""

    def __init__(self, web_db_path: str, staleness_threshold_days: int = 7):
        self.web_db_path = Path(web_db_path)
        self.staleness_threshold_days = staleness_threshold_days

    def check_suggestion_backlog(self) -> SuggestionBacklogReport:
        """
        David's concern: "if suggestions for searches are piling up it should
        be tracking that the search, citation and PDF hunter is doing its job"

        Returns:
            SuggestionBacklogReport with:
            - Total unacted suggestions
            - Age distribution
            - By source type
            - Staleness alerts
        """
        now = datetime.now(timezone.utc)
        staleness_cutoff = now - timedelta(days=self.staleness_threshold_days)

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Query unacted suggestions
                # Assumes: interpretation_space_suggestions or similar table
                cursor.execute("""
                    SELECT COUNT(*) FROM interpretation_space_suggestions
                    WHERE status = 'proposed' OR status = 'identified'
                """)
                total_unacted = cursor.fetchone()[0] or 0

                # Age distribution
                cutoff_0_1d = (now - timedelta(days=1)).isoformat()
                cutoff_1_3d = (now - timedelta(days=3)).isoformat()
                cutoff_3_7d = (now - timedelta(days=7)).isoformat()
                cutoff_7_30d = (now - timedelta(days=30)).isoformat()

                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN created_at > ? THEN 1 ELSE 0 END) as count_0_1d,
                        SUM(CASE WHEN created_at > ? AND created_at <= ? THEN 1 ELSE 0 END) as count_1_3d,
                        SUM(CASE WHEN created_at > ? AND created_at <= ? THEN 1 ELSE 0 END) as count_3_7d,
                        SUM(CASE WHEN created_at > ? AND created_at <= ? THEN 1 ELSE 0 END) as count_7_30d,
                        SUM(CASE WHEN created_at <= ? THEN 1 ELSE 0 END) as count_30plus_d,
                        MIN(created_at) as oldest_created
                    FROM interpretation_space_suggestions
                    WHERE status IN ('proposed', 'identified')
                """, (
                    cutoff_0_1d,
                    cutoff_1_3d, cutoff_0_1d,
                    cutoff_3_7d, cutoff_1_3d,
                    cutoff_7_30d, cutoff_3_7d,
                    cutoff_7_30d,
                ))
                age_row = cursor.fetchone()
                if age_row:
                    (c0, c1, c3, c7, c30, oldest) = age_row
                    oldest_days = int((now - datetime.fromisoformat(oldest)).days) if oldest else 0
                else:
                    c0 = c1 = c3 = c7 = c30 = 0
                    oldest_days = 0

                age_dist = SuggestionAge(
                    count_0_1d=c0 or 0,
                    count_1_3d=c1 or 0,
                    count_3_7d=c3 or 0,
                    count_7_30d=c7 or 0,
                    count_30plus_d=c30 or 0,
                    oldest_suggestion_days=oldest_days,
                )

                # By source
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN source = 'argumentation' THEN 1 ELSE 0 END) as arg,
                        SUM(CASE WHEN source = 'voi' THEN 1 ELSE 0 END) as voi,
                        SUM(CASE WHEN source = 'qa' THEN 1 ELSE 0 END) as qa,
                        SUM(CASE WHEN source = 'interpretation_space' THEN 1 ELSE 0 END) as interp,
                        SUM(CASE WHEN source NOT IN ('argumentation', 'voi', 'qa', 'interpretation_space') THEN 1 ELSE 0 END) as other
                    FROM interpretation_space_suggestions
                    WHERE status IN ('proposed', 'identified')
                """)
                source_row = cursor.fetchone()
                by_arg = (source_row[0] or 0) if source_row else 0
                by_voi = (source_row[1] or 0) if source_row else 0
                by_qa = (source_row[2] or 0) if source_row else 0
                by_interp = (source_row[3] or 0) if source_row else 0
                by_other = (source_row[4] or 0) if source_row else 0

                # Staleness check
                # Flag if oldest exceeds staleness threshold
                exceeded_staleness = age_dist.count_7_30d + age_dist.count_30plus_d
                staleness_alert = (exceeded_staleness > 0) or (oldest_days > self.staleness_threshold_days)
                max_age_to_threshold = oldest_days / max(self.staleness_threshold_days, 1)

                health_status = "OK"
                if staleness_alert:
                    health_status = "RED"
                elif total_unacted > 20:
                    health_status = "YELLOW"

                recommendations = []
                if exceeded_staleness > 0:
                    recommendations.append(
                        f"{exceeded_staleness} suggestions older than {self.staleness_threshold_days} days; "
                        "suggest prioritizing search efforts"
                    )
                if total_unacted > 30:
                    recommendations.append(
                        f"Large backlog ({total_unacted} unacted); may need searcher capacity increase"
                    )

                return SuggestionBacklogReport(
                    timestamp=now,
                    total_unacted_suggestions=total_unacted,
                    age_distribution=age_dist,
                    by_argumentation_gaps=by_arg,
                    by_voi_gaps=by_voi,
                    by_qa_gaps=by_qa,
                    by_interpretation_space_gaps=by_interp,
                    by_other=by_other,
                    staleness_threshold_days=self.staleness_threshold_days,
                    suggestions_exceeding_staleness=exceeded_staleness,
                    max_age_to_stale_ratio=max_age_to_threshold,
                    staleness_alert=staleness_alert,
                    health_status=health_status,
                    recommendations=recommendations,
                )

        except Exception as e:
            logger.error(f"Failed to check suggestion backlog: {e}")
            return SuggestionBacklogReport(
                timestamp=now,
                total_unacted_suggestions=0,
                age_distribution=SuggestionAge(0, 0, 0, 0, 0, 0),
                by_argumentation_gaps=0,
                by_voi_gaps=0,
                by_qa_gaps=0,
                by_interpretation_space_gaps=0,
                by_other=0,
                staleness_threshold_days=self.staleness_threshold_days,
                suggestions_exceeding_staleness=0,
                max_age_to_stale_ratio=0.0,
                staleness_alert=False,
                health_status="UNKNOWN",
                recommendations=["Suggestion table not found"],
            )


# ============================================================================
# Extraction Queue Monitor
# ============================================================================

class ExtractionQueueMonitor:
    """Track PDFs waiting to be encoded into article templates."""

    def __init__(self, web_db_path: str):
        self.web_db_path = Path(web_db_path)

    def check_extraction_queue(self) -> ExtractionQueueReport:
        """
        David's concern: "as PDFs pile up they have to be encoded in article templates"

        Returns:
            ExtractionQueueReport with:
            - PDFs downloaded but not yet extracted
            - PDFs extracted but not validated
            - PDFs validated but not integrated
            - Quality score distribution
            - Estimated time to clear at current throughput
        """
        now = datetime.now(timezone.utc)

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Count PDFs at each stage
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN pdf_status = 'downloaded' THEN 1 ELSE 0 END) as pdf_dl,
                        SUM(CASE WHEN pdf_status = 'extracted' THEN 1 ELSE 0 END) as pdf_extracted,
                        SUM(CASE WHEN pdf_status = 'validated' THEN 1 ELSE 0 END) as pdf_validated
                    FROM papers
                """)
                stage_row = cursor.fetchone()
                pdf_dl = (stage_row[0] or 0) if stage_row else 0
                pdf_extracted = (stage_row[1] or 0) if stage_row else 0
                pdf_validated = (stage_row[2] or 0) if stage_row else 0

                # Quality distribution (if extraction_quality column exists)
                try:
                    cursor.execute("""
                        SELECT
                            SUM(CASE WHEN extraction_quality >= 0.85 THEN 1 ELSE 0 END) as excellent,
                            SUM(CASE WHEN extraction_quality >= 0.70 AND extraction_quality < 0.85 THEN 1 ELSE 0 END) as good,
                            SUM(CASE WHEN extraction_quality >= 0.50 AND extraction_quality < 0.70 THEN 1 ELSE 0 END) as fair,
                            SUM(CASE WHEN extraction_quality < 0.50 THEN 1 ELSE 0 END) as poor,
                            AVG(extraction_quality) as avg_quality
                        FROM papers
                        WHERE pdf_status IN ('extracted', 'validated')
                    """)
                    quality_row = cursor.fetchone()
                    quality_dist = {
                        "excellent": quality_row[0] or 0,
                        "good": quality_row[1] or 0,
                        "fair": quality_row[2] or 0,
                        "poor": quality_row[3] or 0,
                    }
                    avg_quality = quality_row[4] or 0.0
                except Exception:  
                    quality_dist = {}
                    avg_quality = 0.0

                # Throughput
                day_ago = now - timedelta(days=1)
                week_ago = now - timedelta(days=7)

                cursor.execute("""
                    SELECT COUNT(*) FROM papers
                    WHERE pdf_status = 'validated' AND updated_at > ?
                """, (day_ago.isoformat(),))
                throughput_24h = cursor.fetchone()[0] or 0

                cursor.execute("""
                    SELECT COUNT(*) FROM papers
                    WHERE pdf_status = 'validated' AND updated_at > ?
                """, (week_ago.isoformat(),))
                throughput_7d = cursor.fetchone()[0] or 0

                # Estimate time to clear
                if throughput_24h > 0:
                    total_waiting = pdf_dl + pdf_extracted
                    est_hours = (total_waiting / throughput_24h) * 24
                else:
                    est_hours = float('inf')

                # Health assessment
                critical_backlog = pdf_dl > 100 or (pdf_dl + pdf_extracted) > 200
                health_status = "RED" if critical_backlog else ("YELLOW" if pdf_dl > 30 else "OK")

                recommendations = []
                if pdf_dl > 50:
                    recommendations.append(f"{pdf_dl} PDFs awaiting extraction; increase extraction capacity")
                if avg_quality < 0.75:
                    recommendations.append(f"Average extraction quality {avg_quality:.2f} is below target 0.75; "
                                          "review extraction model")

                return ExtractionQueueReport(
                    timestamp=now,
                    pdfs_downloaded_not_extracted=pdf_dl,
                    pdfs_extracted_not_validated=pdf_extracted,
                    pdfs_validated_not_integrated=pdf_validated,
                    quality_distribution=quality_dist,
                    extraction_quality_mean=avg_quality,
                    throughput_24h=throughput_24h,
                    throughput_7d=throughput_7d,
                    estimated_hours_to_clear=est_hours if est_hours != float('inf') else 0.0,
                    critical_backlog=critical_backlog,
                    health_status=health_status,
                    recommendations=recommendations,
                )

        except Exception as e:
            logger.error(f"Failed to check extraction queue: {e}")
            return ExtractionQueueReport(
                timestamp=now,
                pdfs_downloaded_not_extracted=0,
                pdfs_extracted_not_validated=0,
                pdfs_validated_not_integrated=0,
                quality_distribution={},
                extraction_quality_mean=0.0,
                throughput_24h=0,
                throughput_7d=0,
                estimated_hours_to_clear=0.0,
                critical_backlog=False,
                health_status="UNKNOWN",
                recommendations=["Extraction queue metrics unavailable"],
            )


# ============================================================================
# Panel Convocation Service
# ============================================================================

class PanelConvocationService:
    """Determine when automated panel review is needed."""

    def check_panel_needs(self, web: Optional[Any] = None,
                         overseer_db_path: Optional[str] = None) -> List[PanelRecommendation]:
        """
        David says: "sometimes this might require convening a panel"

        Trigger conditions:
        - High-risk decision accumulated (3+ unresolved)
        - Coherence threshold violation persisting >3 days
        - New theory or framework proposed
        - Conflicting evidence pattern detected
        - Quarterly scheduled review due
        - Quality score declining trend (3+ consecutive drops)

        Returns:
            List of PanelRecommendation objects
        """
        recommendations = []

        # Placeholder implementation
        # Real implementation would check:
        # 1. Decision log for unresolved decisions
        # 2. Coherence metrics from web_of_belief
        # 3. Theory registry for new frameworks
        # 4. Conflict detector for evidence patterns
        # 5. Panel schedule for quarterly reviews
        # 6. Quality metrics for trend analysis

        # For now, return example structure
        if web:
            # Check for coherence issues
            try:
                # Get coherence metrics if available
                if hasattr(web, 'compute_coherence'):
                    coherence = web.compute_coherence()
                    if coherence < 0.5:
                        recommendations.append(PanelRecommendation(
                            panel_type="coherence-recovery",
                            urgency="high",
                            reason="System coherence below 0.5; expert review needed",
                            context={"coherence": coherence},
                            data_required=["web_snapshot", "belief_versions", "recent_integrations"],
                        ))
            except Exception:  
                pass

        # Check for high-risk decisions (would read from DECISIONS_LOG)
        # TODO: Implement decision log parsing

        # Check for declining quality trend
        # TODO: Implement quality trend analysis

        return recommendations


# ============================================================================
# Reflex System Monitor
# ============================================================================

class ReflexMonitor:
    """Monitor the reflex system's activity and health.

    Tracks: reflex firing rates, auto-fix success rates,
    unresolved violations, and reflex coverage gaps.
    """

    def __init__(self, overseer_db_path: str):
        self.overseer_db_path = overseer_db_path

    def check_reflex_health(self) -> Dict[str, Any]:
        """
        Analyze reflex system health from the overseer database.

        Returns:
            Dict with:
            - total_reflexes: Number of registered reflexes
            - fired_24h: Count of firings in last 24 hours
            - auto_fixed_24h: Count of successful auto-fixes
            - unresolved_24h: Count of detected but not fixed
            - auto_fix_success_rate: Percentage of detected issues that were auto-fixed
            - reflexes_by_severity: Distribution of firing severities
            - reflexes_by_component: Which components are firing most
            - unresolved_violations: Details of issues needing attention
            - health_status: "HEALTHY", "WARNING", or "CRITICAL"
        """
        try:
            conn = sqlite3.connect(str(self.overseer_db_path))
            cursor = conn.cursor()

            # Total reflexes (count distinct reflex_ids in the events table)
            cursor.execute("SELECT COUNT(DISTINCT reflex_id) FROM reflex_events")
            total_reflexes = cursor.fetchone()[0] or 0

            # Events in last 24 hours
            cursor.execute("""
                SELECT COUNT(*),
                       SUM(detected),
                       SUM(auto_fixed),
                       SUM(CASE WHEN detected=1 AND auto_fixed=0 THEN 1 ELSE 0 END)
                FROM reflex_events
                WHERE timestamp > datetime('now', '-1 day')
            """)
            row = cursor.fetchone()
            fired_24h = row[0] or 0
            detected_24h = row[1] or 0
            auto_fixed_24h = row[2] or 0
            unresolved_24h = row[3] or 0

            # Auto-fix success rate
            auto_fix_rate = 0.0
            if detected_24h > 0:
                auto_fix_rate = (auto_fixed_24h / detected_24h) * 100

            # Distribution by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM reflex_events
                WHERE timestamp > datetime('now', '-1 day')
                GROUP BY severity
                ORDER BY count DESC
            """)
            severity_dist = {row[0]: row[1] for row in cursor.fetchall()}

            # Distribution by component
            cursor.execute("""
                SELECT component, COUNT(*) as count
                FROM reflex_events
                WHERE timestamp > datetime('now', '-1 day')
                GROUP BY component
                ORDER BY count DESC
            """)
            component_dist = {row[0]: row[1] for row in cursor.fetchall()}

            # Unresolved violations (detected but not auto-fixed)
            cursor.execute("""
                SELECT reflex_id, description, severity, COUNT(*) as count
                FROM reflex_events
                WHERE detected=1 AND auto_fixed=0
                AND timestamp > datetime('now', '-7 days')
                GROUP BY reflex_id, description, severity
                ORDER BY count DESC
                LIMIT 20
            """)
            unresolved = [
                {
                    "reflex_id": row[0],
                    "description": row[1],
                    "severity": row[2],
                    "count": row[3]
                }
                for row in cursor.fetchall()
            ]

            conn.close()

            # Determine health status
            health_status = "HEALTHY"
            if unresolved_24h > 5 or severity_dist.get("critical", 0) > 0:
                health_status = "CRITICAL"
            elif unresolved_24h > 2 or severity_dist.get("error", 0) > 3:
                health_status = "WARNING"

            return {
                "total_reflexes": total_reflexes,
                "fired_24h": fired_24h,
                "detected_24h": detected_24h,
                "auto_fixed_24h": auto_fixed_24h,
                "unresolved_24h": unresolved_24h,
                "auto_fix_success_rate": round(auto_fix_rate, 1),
                "severity_distribution": severity_dist,
                "component_distribution": component_dist,
                "unresolved_violations": unresolved,
                "health_status": health_status,
            }
        except Exception as e:
            logger.warning(f"Reflex health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "health_status": "UNKNOWN",
            }


# ============================================================================
# Success Condition Monitor
# ============================================================================

class SuccessConditionMonitor:
    """Monitor the success conditions registry.

    Tracks: SC pass/fail rates from test runs, SCs without recent validation,
    SCs with degrading metrics, and coverage gaps.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
        self.success_conditions_path = self.repo_root / "contracts" / "success_conditions.json"

    def check_success_conditions(self) -> Dict[str, Any]:
        """
        Analyze success conditions registry.

        Returns:
            Dict with:
            - total_conditions: Total SCs across all modules
            - modules: Count of modules
            - conditions_by_module: SC count per module
            - conditions_without_tests: SCs that reference missing test files
            - condition_details: List of all SCs with validation status
            - coverage_status: Whether all critical modules are covered
            - health_status: "HEALTHY", "WARNING", or "CRITICAL"
        """
        try:
            if not self.success_conditions_path.exists():
                return {
                    "status": "error",
                    "error": f"success_conditions.json not found at {self.success_conditions_path}",
                    "health_status": "CRITICAL",
                }

            with open(self.success_conditions_path) as f:
                registry = json.load(f)

            conditions = registry.get("conditions", {})
            total_conditions = 0
            conditions_by_module = {}
            all_conditions_detail = []
            missing_tests = []

            for module_path, module_data in conditions.items():
                module_conds = module_data.get("conditions", [])
                sc_count = len(module_conds)
                total_conditions += sc_count
                conditions_by_module[module_path] = sc_count

                # Check each SC for test file existence
                for sc in module_conds:
                    sc_id = sc.get("id", "unknown")
                    test_name = sc.get("test_name", "")

                    all_conditions_detail.append({
                        "id": sc_id,
                        "name": sc.get("name", ""),
                        "module": module_path,
                        "test_name": test_name,
                        "threshold": sc.get("threshold", ""),
                    })

                    # Attempt to verify test exists
                    # This is a simple heuristic: look for test file in tests/ directory
                    test_dir = self.repo_root / "tests"
                    if test_dir.exists():
                        test_files = list(test_dir.glob("test_*.py"))
                        test_found = any(test_name in str(f) for f in test_files)
                        if not test_found and test_name:
                            missing_tests.append({
                                "condition_id": sc_id,
                                "test_name": test_name,
                                "module": module_path,
                            })

            # Determine health status
            health_status = "HEALTHY"
            if len(missing_tests) > total_conditions * 0.2:  # >20% of tests missing
                health_status = "CRITICAL"
            elif len(missing_tests) > 0:
                health_status = "WARNING"

            return {
                "total_conditions": total_conditions,
                "modules_count": len(conditions_by_module),
                "conditions_by_module": conditions_by_module,
                "conditions_without_tests": missing_tests,
                "conditions_without_tests_count": len(missing_tests),
                "condition_details": all_conditions_detail,
                "coverage_status": "complete" if len(missing_tests) == 0 else "incomplete",
                "health_status": health_status,
            }
        except Exception as e:
            logger.warning(f"Success condition check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "health_status": "UNKNOWN",
            }


# ============================================================================
# Management Dashboard
# ============================================================================

class ManagementDashboard:
    """Aggregate all monitoring into a single status view."""

    def __init__(self, overseer_db_path: str, web_db_path: str, web: Optional[Any] = None):
        self.overseer_db_path = overseer_db_path
        self.web_db_path = web_db_path
        self.web = web

        self.registry = PipelineRegistry(overseer_db_path)
        self.queue_monitor = QueueHealthMonitor(web_db_path)
        self.flow_monitor = ArticleFlowMonitor(web_db_path)
        self.suggestion_tracker = SearchSuggestionTracker(web_db_path)
        self.extraction_monitor = ExtractionQueueMonitor(web_db_path)
        self.panel_service = PanelConvocationService()
        self.reflex_monitor = ReflexMonitor(overseer_db_path)
        self.success_condition_monitor = SuccessConditionMonitor()

    def generate_management_report(self) -> ManagementReport:
        """
        Generate complete single-page management view.

        Returns:
            ManagementReport with:
            1. Pipeline statuses (all 6)
            2. Queue health (backlog, throughput, bottlenecks)
            3. Article flow
            4. Suggestion backlog
            5. Extraction queue
            6. Panel needs
            7. Error/failure trends
            8. Recommendations
        """
        now = datetime.now(timezone.utc)

        # Collect all monitoring reports
        pipeline_records = self.registry.get_all_pipelines()
        pipeline_dict = {p.pipeline_id: p for p in pipeline_records}

        queue_health = self.queue_monitor.check_queue_health()
        article_flow = self.flow_monitor.check_article_flow()
        suggestion_backlog = self.suggestion_tracker.check_suggestion_backlog()
        extraction_queue = self.extraction_monitor.check_extraction_queue()
        panel_recommendations = self.panel_service.check_panel_needs(self.web, self.overseer_db_path)

        # QA system monitoring
        reflex_health = self.reflex_monitor.check_reflex_health()
        success_conditions = self.success_condition_monitor.check_success_conditions()

        # Aggregate error trends
        error_count_24h = sum(
            1 for p in pipeline_records
            if p.last_error and p.error_rate_24h > 0.05
        )
        error_rate_trend = "stable"  # TODO: compute trend
        most_common_error = None  # TODO: extract from logs

        # Determine overall health
        pipeline_statuses = [p.status for p in pipeline_records]
        blocked_count = sum(1 for s in pipeline_statuses if s == PipelineStatus.BLOCKED)
        stalled_count = sum(1 for s in pipeline_statuses if s == PipelineStatus.STALLED)

        if blocked_count > 0:
            overall_health = "RED"
        elif stalled_count > 1 or queue_health.health_status == "RED":
            overall_health = "YELLOW"
        else:
            overall_health = "HEALTHY"

        # Compile recommendations
        critical_alerts = []
        immediate_actions = []

        if blocked_count > 0:
            critical_alerts.append(f"{blocked_count} pipeline(s) BLOCKED")
            immediate_actions.append("Investigate blocked pipelines immediately")

        if suggestion_backlog.staleness_alert:
            critical_alerts.append("Suggestion backlog exceeds staleness threshold")
            immediate_actions.append("Prioritize search for old suggestions")

        if extraction_queue.critical_backlog:
            critical_alerts.append("PDF extraction queue critical")
            immediate_actions.append("Increase extraction capacity or prioritize oldest PDFs")

        # Check reflex health
        if reflex_health.get("health_status") == "CRITICAL":
            critical_alerts.append("Reflex system has unresolved violations")
            immediate_actions.append("Review and address unresolved reflex violations")

        # Check success conditions coverage
        sc_missing = success_conditions.get("conditions_without_tests_count", 0)
        if sc_missing > 0:
            critical_alerts.append(f"{sc_missing} success conditions lack test coverage")
            immediate_actions.append("Add tests for missing success conditions")

        # Combine all recommendations
        all_recommendations = (
            queue_health.recommendations +
            article_flow.recommendations +
            suggestion_backlog.recommendations +
            extraction_queue.recommendations
        )

        return ManagementReport(
            timestamp=now,
            pipeline_statuses=pipeline_dict,
            queue_health=queue_health,
            article_flow=article_flow,
            suggestion_backlog=suggestion_backlog,
            extraction_queue=extraction_queue,
            panel_needs=panel_recommendations,
            reflex_health=reflex_health,
            success_conditions=success_conditions,
            error_count_24h=error_count_24h,
            error_rate_trend=error_rate_trend,
            most_common_error=most_common_error,
            overall_health=overall_health,
            critical_alerts=critical_alerts,
            immediate_actions_recommended=immediate_actions,
            previous_report_timestamp=None,  # TODO: track previous report
            changes_since_previous={},  # TODO: compute deltas
        )

    def management_check(self) -> str:
        """
        Run full management check and return readable report.

        Called by nightly pipeline alongside health/integrity/completeness checks.
        """
        report = self.generate_management_report()
        return self._format_report(report)

    def _format_report(self, report: ManagementReport) -> str:
        """Format management report as readable text."""
        lines = [
            "=" * 80,
            "OVERSEER v2 MANAGEMENT REPORT",
            f"Timestamp: {report.timestamp.isoformat()}",
            "=" * 80,
            "",
        ]

        # Overall status
        lines.extend([
            "OVERALL HEALTH: " + report.overall_health,
            "",
        ])

        # Critical alerts
        if report.critical_alerts:
            lines.extend([
                "CRITICAL ALERTS:",
            ])
            for alert in report.critical_alerts:
                lines.append(f"  ⚠ {alert}")
            lines.append("")

        # Pipeline statuses
        lines.extend([
            "PIPELINE STATUSES:",
        ])
        for pipeline_id, record in report.pipeline_statuses.items():
            status_symbol = {
                "healthy": "✓",
                "degraded": "⚠",
                "stalled": "⚠",
                "blocked": "✗",
                "unknown": "?",
            }.get(record.status.value, "?")
            lines.append(
                f"  {status_symbol} {record.display_name:30s} | "
                f"Depth: {record.queue_depth:3d} | "
                f"24h: {record.throughput_24h:3d} | "
                f"Error: {record.error_rate_24h*100:5.1f}%"
            )
        lines.append("")

        # Queue health
        lines.extend([
            "QUEUE HEALTH:",
            f"  Total targets: {report.queue_health.total_targets}",
            f"  Open: {report.queue_health.open_targets} | "
            f"Searching: {report.queue_health.searching_targets} | "
            f"Found: {report.queue_health.found_targets} | "
            f"Closed: {report.queue_health.closed_targets}",
            f"  Search→Found rate: {report.queue_health.search_to_found_rate*100:.1f}%",
            f"  Oldest open: {report.queue_health.oldest_open_target_hours:.1f}h",
            f"  Status: {report.queue_health.health_status}",
            "",
        ])

        # Article flow
        lines.extend([
            "ARTICLE FLOW:",
        ])
        for stage in report.article_flow.stages:
            lines.append(
                f"  {stage.stage_name:30s} | "
                f"Waiting: {stage.items_waiting:3d} | "
                f"24h: {stage.items_completed_24h:3d} | "
                f"Bottleneck: {stage.bottleneck_score*100:.0f}%"
            )
        lines.extend([
            f"  Overall efficiency: {report.article_flow.flow_efficiency*100:.1f}%",
            "",
        ])

        # Suggestion backlog
        lines.extend([
            "SUGGESTION BACKLOG:",
            f"  Total unacted: {report.suggestion_backlog.total_unacted_suggestions}",
            f"  Age: 0-1d: {report.suggestion_backlog.age_distribution.count_0_1d} | "
            f"1-3d: {report.suggestion_backlog.age_distribution.count_1_3d} | "
            f"3-7d: {report.suggestion_backlog.age_distribution.count_3_7d} | "
            f"7-30d: {report.suggestion_backlog.age_distribution.count_7_30d} | "
            f">30d: {report.suggestion_backlog.age_distribution.count_30plus_d}",
            f"  Oldest: {report.suggestion_backlog.age_distribution.oldest_suggestion_days} days",
            f"  Status: {report.suggestion_backlog.health_status}",
            "",
        ])

        # Extraction queue
        lines.extend([
            "EXTRACTION QUEUE:",
            f"  Downloaded: {report.extraction_queue.pdfs_downloaded_not_extracted}",
            f"  Extracted: {report.extraction_queue.pdfs_extracted_not_validated}",
            f"  Validated: {report.extraction_queue.pdfs_validated_not_integrated}",
            f"  Quality: {report.extraction_queue.extraction_quality_mean:.2f}",
            f"  Throughput 24h: {report.extraction_queue.throughput_24h}",
            f"  Est. clear time: {report.extraction_queue.estimated_hours_to_clear:.1f}h",
            f"  Status: {report.extraction_queue.health_status}",
            "",
        ])

        # Reflex health
        if report.reflex_health:
            lines.extend([
                "REFLEX SYSTEM HEALTH:",
                f"  Total reflexes: {report.reflex_health.get('total_reflexes', 0)}",
                f"  Fired (24h): {report.reflex_health.get('fired_24h', 0)}",
                f"  Auto-fixed (24h): {report.reflex_health.get('auto_fixed_24h', 0)}",
                f"  Unresolved (24h): {report.reflex_health.get('unresolved_24h', 0)}",
                f"  Auto-fix success rate: {report.reflex_health.get('auto_fix_success_rate', 0):.1f}%",
                f"  Health: {report.reflex_health.get('health_status', 'UNKNOWN')}",
                "",
            ])

        # Success conditions
        if report.success_conditions:
            lines.extend([
                "SUCCESS CONDITIONS REGISTRY:",
                f"  Total conditions: {report.success_conditions.get('total_conditions', 0)}",
                f"  Modules covered: {report.success_conditions.get('modules_count', 0)}",
                f"  Without tests: {report.success_conditions.get('conditions_without_tests_count', 0)}",
                f"  Coverage: {report.success_conditions.get('coverage_status', 'unknown')}",
                f"  Health: {report.success_conditions.get('health_status', 'UNKNOWN')}",
                "",
            ])

        # Panel recommendations
        if report.panel_needs:
            lines.extend([
                "PANEL CONVOCATION RECOMMENDATIONS:",
            ])
            for rec in report.panel_needs:
                lines.append(f"  [{rec.urgency.upper()}] {rec.panel_type}: {rec.reason}")
            lines.append("")

        # Immediate actions
        if report.immediate_actions_recommended:
            lines.extend([
                "IMMEDIATE ACTIONS RECOMMENDED:",
            ])
            for action in report.immediate_actions_recommended:
                lines.append(f"  • {action}")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)
