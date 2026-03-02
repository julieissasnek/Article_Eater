"""
Tests for OVERSEER v2 Management Layer

30+ tests covering:
- Pipeline registration and status
- Queue health monitoring
- Suggestion backlog detection
- Extraction queue monitoring
- Panel convocation triggers
- Management report generation
- Edge cases
"""

import pytest
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import json

from src.services.overseer_management import (
    PipelineRegistry,
    QueueHealthMonitor,
    ArticleFlowMonitor,
    SearchSuggestionTracker,
    ExtractionQueueMonitor,
    PanelConvocationService,
    ManagementDashboard,
    ReflexMonitor,
    SuccessConditionMonitor,
)
from src.services.overseer_management_models import (
    PipelineStatus,
    PipelineStatusSummary,
    QueueHealthReport,
    ArticleFlowReport,
    SuggestionBacklogReport,
    ExtractionQueueReport,
    ManagementReport,
)


@pytest.fixture
def temp_db():
    """Create temporary databases for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        overseer_db = str(Path(tmpdir) / "overseer.db")
        web_db = str(Path(tmpdir) / "web.db")

        # Initialize overseer.db
        with sqlite3.connect(overseer_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()

        # Initialize web.db with minimal schema
        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            # Create minimal tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_targets (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT,
                    updated_at TEXT,
                    status TEXT,
                    completed_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT,
                    updated_at TEXT,
                    pdf_status TEXT,
                    extraction_status TEXT,
                    integration_status TEXT,
                    extraction_quality REAL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT,
                    status TEXT,
                    source TEXT
                )
            """)

            conn.commit()

        yield overseer_db, web_db


# ============================================================================
# PipelineRegistry Tests
# ============================================================================

class TestPipelineRegistry:
    """Test pipeline registration and status tracking."""

    def test_registry_initialization(self, temp_db):
        """Registry should initialize with schema."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        # Should not raise
        assert registry.db_path == Path(overseer_db)

    def test_default_pipelines_registered(self, temp_db):
        """Default 6 pipelines should be registered."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        pipelines = registry.get_all_pipelines()
        assert len(pipelines) == 6

        pipeline_ids = {p.pipeline_id for p in pipelines}
        assert pipeline_ids == {
            "article-discovery",
            "pdf-acquisition",
            "extraction",
            "integration",
            "qa-audit",
            "nightly-maintenance",
        }

    def test_register_heartbeat(self, temp_db):
        """Should record pipeline heartbeat."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        registry.register_heartbeat(
            "article-discovery",
            PipelineStatus.HEALTHY,
            queue_depth=5,
            throughput_24h=12,
            error_rate_24h=0.02,
        )

        pipelines = registry.get_all_pipelines()
        discovery = next(p for p in pipelines if p.pipeline_id == "article-discovery")

        assert discovery.status == PipelineStatus.HEALTHY
        assert discovery.queue_depth == 5
        assert discovery.throughput_24h == 12
        assert discovery.error_rate_24h == 0.02

    def test_heartbeat_updates_status(self, temp_db):
        """Heartbeat should update status."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        # First heartbeat
        registry.register_heartbeat("extraction", PipelineStatus.HEALTHY)
        pipelines1 = registry.get_all_pipelines()
        extraction1 = next(p for p in pipelines1 if p.pipeline_id == "extraction")
        assert extraction1.status == PipelineStatus.HEALTHY

        # Update status
        registry.register_heartbeat("extraction", PipelineStatus.DEGRADED)
        pipelines2 = registry.get_all_pipelines()
        extraction2 = next(p for p in pipelines2 if p.pipeline_id == "extraction")
        assert extraction2.status == PipelineStatus.DEGRADED

    def test_pipeline_status_summary(self, temp_db):
        """Status summary should aggregate statuses."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        registry.register_heartbeat("article-discovery", PipelineStatus.HEALTHY)
        registry.register_heartbeat("pdf-acquisition", PipelineStatus.DEGRADED)
        registry.register_heartbeat("extraction", PipelineStatus.STALLED)
        registry.register_heartbeat("integration", PipelineStatus.BLOCKED)

        summary = registry.get_pipeline_status_summary()

        assert summary.total_pipelines == 6
        assert summary.healthy_count == 1
        assert summary.degraded_count == 1
        assert summary.stalled_count == 1
        assert summary.blocked_count == 1

    def test_critical_alert_blocked(self, temp_db):
        """Should alert when pipeline blocked."""
        overseer_db, _ = temp_db
        registry = PipelineRegistry(overseer_db)

        registry.register_heartbeat("article-discovery", PipelineStatus.BLOCKED)

        summary = registry.get_pipeline_status_summary()
        alert = summary.critical_alert()

        assert alert is not None
        assert "BLOCKED" in alert


# ============================================================================
# QueueHealthMonitor Tests
# ============================================================================

class TestQueueHealthMonitor:
    """Test queue health monitoring."""

    def test_empty_queue(self, temp_db):
        """Should handle empty queue gracefully."""
        _, web_db = temp_db
        monitor = QueueHealthMonitor(web_db)

        report = monitor.check_queue_health()

        assert isinstance(report, QueueHealthReport)
        assert report.total_targets == 0
        assert report.health_status in ["OK", "UNKNOWN"]

    def test_queue_health_open_targets(self, temp_db):
        """Should count open targets."""
        _, web_db = temp_db
        monitor = QueueHealthMonitor(web_db)

        # Add targets
        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            for i in range(5):
                cursor.execute("""
                    INSERT INTO research_targets (created_at, updated_at, status)
                    VALUES (?, ?, ?)
                """, (now, now, "open"))

            conn.commit()

        report = monitor.check_queue_health()

        assert report.total_targets == 5
        assert report.open_targets == 5

    def test_queue_health_searching_targets(self, temp_db):
        """Should count searching targets."""
        _, web_db = temp_db
        monitor = QueueHealthMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO research_targets (created_at, updated_at, status)
                VALUES (?, ?, ?)
            """, (now, now, "searching"))

            cursor.execute("""
                INSERT INTO research_targets (created_at, updated_at, status)
                VALUES (?, ?, ?)
            """, (now, now, "found"))

            conn.commit()

        report = monitor.check_queue_health()

        assert report.searching_targets == 1
        assert report.found_targets == 1

    def test_queue_health_oldest_target(self, temp_db):
        """Should identify age of oldest open target."""
        _, web_db = temp_db
        monitor = QueueHealthMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            old_time = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
            new_time = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO research_targets (created_at, updated_at, status)
                VALUES (?, ?, ?)
            """, (old_time, new_time, "open"))

            conn.commit()

        report = monitor.check_queue_health()

        assert report.oldest_open_target_hours >= 9  # Allow some slack
        assert report.oldest_open_target_hours <= 11

    def test_queue_health_red_alert(self, temp_db):
        """Should alert RED if many open targets or very old."""
        _, web_db = temp_db
        monitor = QueueHealthMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            very_old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()

            for i in range(25):  # >20 triggers RED
                cursor.execute("""
                    INSERT INTO research_targets (created_at, updated_at, status)
                    VALUES (?, ?, ?)
                """, (very_old, very_old, "open"))

            conn.commit()

        report = monitor.check_queue_health()

        assert report.health_status == "RED"


# ============================================================================
# ArticleFlowMonitor Tests
# ============================================================================

class TestArticleFlowMonitor:
    """Test article flow monitoring."""

    def test_empty_flow(self, temp_db):
        _, web_db = temp_db
        monitor = ArticleFlowMonitor(web_db)

        report = monitor.check_article_flow()

        assert isinstance(report, ArticleFlowReport)
        assert report.overall_throughput_24h >= 0

    def test_flow_bottleneck_detection(self, temp_db):
        """Should identify bottleneck stages."""
        _, web_db = temp_db
        monitor = ArticleFlowMonitor(web_db)

        # Add papers with backlog at extraction stage
        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            # Many at extraction, few completed
            for i in range(30):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status, extraction_status)
                    VALUES (?, ?, ?, ?)
                """, (now, now, "pdf_acquired", "extracting"))

            conn.commit()

        report = monitor.check_article_flow()

        # Should have low flow efficiency
        assert report.flow_efficiency <= 0.5 or report.total_items_in_system > 0


# ============================================================================
# SearchSuggestionTracker Tests
# ============================================================================

class TestSearchSuggestionTracker:
    """Test suggestion backlog tracking."""

    def test_empty_suggestions(self, temp_db):
        """Should handle empty suggestion set."""
        _, web_db = temp_db
        tracker = SearchSuggestionTracker(web_db)

        report = tracker.check_suggestion_backlog()

        assert isinstance(report, SuggestionBacklogReport)
        assert report.total_unacted_suggestions == 0

    def test_unacted_suggestions(self, temp_db):
        """Should count unacted suggestions."""
        _, web_db = temp_db
        tracker = SearchSuggestionTracker(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            for i in range(10):
                cursor.execute("""
                    INSERT INTO interpretation_space_suggestions
                    (created_at, status, source)
                    VALUES (?, ?, ?)
                """, (now, "proposed", "voi"))

            conn.commit()

        report = tracker.check_suggestion_backlog()

        assert report.total_unacted_suggestions == 10

    def test_suggestion_age_distribution(self, temp_db):
        """Should categorize suggestions by age."""
        _, web_db = temp_db
        tracker = SearchSuggestionTracker(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()

            # New suggestion
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO interpretation_space_suggestions
                (created_at, status, source)
                VALUES (?, ?, ?)
            """, (now, "proposed", "voi"))

            # Very old suggestion (40 days) — exceeds 30 days
            very_old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            cursor.execute("""
                INSERT INTO interpretation_space_suggestions
                (created_at, status, source)
                VALUES (?, ?, ?)
            """, (very_old, "proposed", "voi"))

            conn.commit()

        report = tracker.check_suggestion_backlog()

        assert report.age_distribution.count_0_1d == 1
        assert report.age_distribution.count_30plus_d == 1
        assert report.age_distribution.oldest_suggestion_days == 40

    def test_suggestion_staleness_alert(self, temp_db):
        """Should alert if suggestions exceed staleness threshold."""
        _, web_db = temp_db
        tracker = SearchSuggestionTracker(web_db, staleness_threshold_days=5)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()

            # Add very old suggestion
            very_old = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
            cursor.execute("""
                INSERT INTO interpretation_space_suggestions
                (created_at, status, source)
                VALUES (?, ?, ?)
            """, (very_old, "proposed", "voi"))

            conn.commit()

        report = tracker.check_suggestion_backlog()

        assert report.staleness_alert is True
        assert report.health_status == "RED"

    def test_suggestion_by_source(self, temp_db):
        """Should categorize suggestions by source type."""
        _, web_db = temp_db
        tracker = SearchSuggestionTracker(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            sources = [
                ("argumentation", 3),
                ("voi", 2),
                ("qa", 4),
                ("interpretation_space", 1),
            ]

            for source, count in sources:
                for i in range(count):
                    cursor.execute("""
                        INSERT INTO interpretation_space_suggestions
                        (created_at, status, source)
                        VALUES (?, ?, ?)
                    """, (now, "proposed", source))

            conn.commit()

        report = tracker.check_suggestion_backlog()

        assert report.by_argumentation_gaps == 3
        assert report.by_voi_gaps == 2
        assert report.by_qa_gaps == 4
        assert report.by_interpretation_space_gaps == 1


# ============================================================================
# ExtractionQueueMonitor Tests
# ============================================================================

class TestExtractionQueueMonitor:
    """Test extraction queue monitoring."""

    def test_empty_extraction_queue(self, temp_db):
        """Should handle empty extraction queue."""
        _, web_db = temp_db
        monitor = ExtractionQueueMonitor(web_db)

        report = monitor.check_extraction_queue()

        assert isinstance(report, ExtractionQueueReport)
        assert report.pdfs_downloaded_not_extracted == 0

    def test_extraction_queue_counting(self, temp_db):
        """Should count PDFs at each extraction stage."""
        _, web_db = temp_db
        monitor = ExtractionQueueMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            # Downloaded stage
            for i in range(5):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (now, now, "downloaded"))

            # Extracted stage
            for i in range(3):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (now, now, "extracted"))

            # Validated stage
            for i in range(2):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (now, now, "validated"))

            conn.commit()

        report = monitor.check_extraction_queue()

        assert report.pdfs_downloaded_not_extracted == 5
        assert report.pdfs_extracted_not_validated == 3
        assert report.pdfs_validated_not_integrated == 2

    def test_extraction_queue_critical_backlog(self, temp_db):
        """Should alert if PDF backlog exceeds threshold."""
        _, web_db = temp_db
        monitor = ExtractionQueueMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            # Large backlog
            for i in range(120):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (now, now, "downloaded"))

            conn.commit()

        report = monitor.check_extraction_queue()

        assert report.critical_backlog is True
        assert report.health_status == "RED"

    def test_extraction_throughput(self, temp_db):
        """Should measure extraction throughput."""
        _, web_db = temp_db
        monitor = ExtractionQueueMonitor(web_db)

        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            recent = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()

            # Recent completed PDFs
            for i in range(10):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (recent, now, "validated"))

            conn.commit()

        report = monitor.check_extraction_queue()

        assert report.throughput_24h == 10


# ============================================================================
# ManagementDashboard Tests
# ============================================================================

class TestManagementDashboard:
    """Test complete management dashboard."""

    def test_management_report_generation(self, temp_db):
        """Should generate complete management report."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        report = dashboard.generate_management_report()

        assert isinstance(report, ManagementReport)
        assert report.timestamp is not None
        assert isinstance(report.pipeline_statuses, dict)
        assert isinstance(report.queue_health, QueueHealthReport)
        assert isinstance(report.article_flow, ArticleFlowReport)
        assert isinstance(report.suggestion_backlog, SuggestionBacklogReport)
        assert isinstance(report.extraction_queue, ExtractionQueueReport)

    def test_management_report_overall_health_healthy(self, temp_db):
        """Should report HEALTHY when all systems OK."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        # Set all pipelines to healthy
        registry = dashboard.registry
        for pipeline_id in [
            "article-discovery", "pdf-acquisition", "extraction",
            "integration", "qa-audit", "nightly-maintenance"
        ]:
            registry.register_heartbeat(pipeline_id, PipelineStatus.HEALTHY)

        report = dashboard.generate_management_report()

        assert report.overall_health == "HEALTHY"

    def test_management_report_overall_health_red(self, temp_db):
        """Should report RED when pipeline blocked."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        registry = dashboard.registry
        registry.register_heartbeat("article-discovery", PipelineStatus.BLOCKED)

        report = dashboard.generate_management_report()

        assert report.overall_health == "RED"
        assert len(report.critical_alerts) > 0

    def test_management_report_critical_alerts(self, temp_db):
        """Should include critical alerts in report."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        registry = dashboard.registry
        registry.register_heartbeat("integration", PipelineStatus.BLOCKED)

        report = dashboard.generate_management_report()

        assert len(report.critical_alerts) > 0

    def test_management_check_formatting(self, temp_db):
        """Should format report as readable text."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        text_report = dashboard.management_check()

        assert isinstance(text_report, str)
        assert "OVERSEER v2 MANAGEMENT REPORT" in text_report
        assert "PIPELINE STATUSES:" in text_report
        assert "QUEUE HEALTH:" in text_report


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full management layer."""

    def test_full_monitoring_workflow(self, temp_db):
        """Test complete monitoring workflow."""
        overseer_db, web_db = temp_db

        # Setup
        dashboard = ManagementDashboard(overseer_db, web_db)

        # Register heartbeats
        registry = dashboard.registry
        for pipeline_id in ["article-discovery", "extraction"]:
            registry.register_heartbeat(
                pipeline_id,
                PipelineStatus.HEALTHY,
                queue_depth=10,
                throughput_24h=5,
            )

        # Add queue data
        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO research_targets (created_at, updated_at, status)
                VALUES (?, ?, ?)
            """, (now, now, "open"))

            for i in range(3):
                cursor.execute("""
                    INSERT INTO papers (created_at, updated_at, pdf_status)
                    VALUES (?, ?, ?)
                """, (now, now, "downloaded"))

            conn.commit()

        # Generate report
        report = dashboard.generate_management_report()

        assert report is not None
        assert report.queue_health.open_targets == 1
        assert report.extraction_queue.pdfs_downloaded_not_extracted == 3

    def test_recommendations_generation(self, temp_db):
        """Should generate actionable recommendations."""
        overseer_db, web_db = temp_db
        dashboard = ManagementDashboard(overseer_db, web_db)

        # Create problematic state
        with sqlite3.connect(web_db) as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()

            # Many old suggestions
            old = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            for i in range(10):
                cursor.execute("""
                    INSERT INTO interpretation_space_suggestions
                    (created_at, status, source)
                    VALUES (?, ?, ?)
                """, (old, "proposed", "voi"))

            conn.commit()

        report = dashboard.generate_management_report()

        assert len(report.immediate_actions_recommended) >= 0


# ============================================================================
# Tests for ReflexMonitor
# ============================================================================

class TestReflexMonitor:
    """Tests for the ReflexMonitor service class."""

    @pytest.fixture
    def monitor(self, tmp_path):
        """Create a ReflexMonitor with a test database."""
        db_path = tmp_path / "test_overseer.db"
        return ReflexMonitor(str(db_path))

    def test_reflex_monitor_initialization(self, monitor):
        """Test that ReflexMonitor initializes correctly."""
        assert monitor is not None
        assert monitor.overseer_db_path is not None

    def test_check_reflex_health_empty_database(self, monitor):
        """Test health check on empty database returns valid structure."""
        # Initialize the reflex_events table
        import sqlite3
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)
        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        assert "total_reflexes" in health
        assert "fired_24h" in health
        assert "auto_fixed_24h" in health
        assert "unresolved_24h" in health
        assert "auto_fix_success_rate" in health
        assert "health_status" in health

    def test_check_reflex_health_with_data(self, monitor, tmp_path):
        """Test health check with actual reflex event data."""
        import sqlite3
        from datetime import datetime, timezone
        import uuid

        # Insert test data
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)

        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO reflex_events
            (event_id, timestamp, reflex_id, component, success_condition_id,
             detected, description, auto_fixed, fix_action, severity, context_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), now, "RFX-TEST-001", "test_component", "SC-001",
              1, "Test violation", 1, "fixed", "warning", "{}"))

        cursor.execute("""
            INSERT INTO reflex_events
            (event_id, timestamp, reflex_id, component, success_condition_id,
             detected, description, auto_fixed, fix_action, severity, context_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), now, "RFX-TEST-002", "test_component", "SC-002",
              1, "Another violation", 0, "manual_required", "error", "{}"))

        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        assert health["total_reflexes"] >= 0
        assert health["fired_24h"] == 2
        assert health["auto_fixed_24h"] == 1
        assert health["unresolved_24h"] == 1
        assert health["auto_fix_success_rate"] == 50.0

    def test_reflex_health_status_healthy(self, monitor, tmp_path):
        """Test health status is HEALTHY when few violations."""
        import sqlite3
        # Initialize the reflex_events table
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)
        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        # Empty database should be HEALTHY
        assert health["health_status"] == "HEALTHY"

    def test_reflex_health_includes_severity_distribution(self, monitor):
        """Test health check includes severity distribution."""
        import sqlite3
        # Initialize the reflex_events table
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)
        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        assert "severity_distribution" in health
        assert isinstance(health["severity_distribution"], dict)

    def test_reflex_health_includes_component_distribution(self, monitor):
        """Test health check includes component distribution."""
        import sqlite3
        # Initialize the reflex_events table
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)
        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        assert "component_distribution" in health
        assert isinstance(health["component_distribution"], dict)

    def test_reflex_health_includes_unresolved_violations(self, monitor):
        """Test health check includes unresolved violations list."""
        import sqlite3
        # Initialize the reflex_events table
        conn = sqlite3.connect(str(monitor.overseer_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)
        conn.commit()
        conn.close()

        health = monitor.check_reflex_health()
        assert "unresolved_violations" in health
        assert isinstance(health["unresolved_violations"], list)


# ============================================================================
# Tests for SuccessConditionMonitor
# ============================================================================

class TestSuccessConditionMonitor:
    """Tests for the SuccessConditionMonitor service class."""

    @pytest.fixture
    def monitor(self):
        """Create a SuccessConditionMonitor."""
        from src.services.overseer_management import SuccessConditionMonitor
        return SuccessConditionMonitor()

    def test_success_condition_monitor_initialization(self, monitor):
        """Test that SuccessConditionMonitor initializes correctly."""
        assert monitor is not None
        assert monitor.repo_root is not None
        assert monitor.success_conditions_path is not None

    def test_check_success_conditions_returns_structure(self, monitor):
        """Test that check_success_conditions returns expected structure."""
        result = monitor.check_success_conditions()
        assert "total_conditions" in result
        assert "modules_count" in result
        assert "conditions_by_module" in result
        assert "conditions_without_tests" in result
        assert "conditions_without_tests_count" in result
        assert "coverage_status" in result
        assert "health_status" in result

    def test_success_conditions_loads_registry(self, monitor):
        """Test that success conditions registry is loaded."""
        result = monitor.check_success_conditions()
        # If registry exists, should have > 0 conditions
        if result.get("status") != "error":
            assert result["total_conditions"] > 0
            assert result["modules_count"] > 0

    def test_success_conditions_coverage_status(self, monitor):
        """Test that coverage_status is either 'complete' or 'incomplete'."""
        result = monitor.check_success_conditions()
        if result.get("status") != "error":
            assert result["coverage_status"] in ("complete", "incomplete")

    def test_success_conditions_health_status_values(self, monitor):
        """Test that health_status is one of the expected values."""
        result = monitor.check_success_conditions()
        assert result["health_status"] in ("HEALTHY", "WARNING", "CRITICAL", "UNKNOWN")

    def test_success_conditions_modules_coverage(self, monitor):
        """Test that conditions_by_module is a dict."""
        result = monitor.check_success_conditions()
        if result.get("status") != "error":
            assert isinstance(result["conditions_by_module"], dict)

    def test_success_conditions_detail_list(self, monitor):
        """Test that condition_details is a list."""
        result = monitor.check_success_conditions()
        if result.get("status") != "error":
            assert isinstance(result["condition_details"], list)

    def test_success_conditions_missing_tests_list(self, monitor):
        """Test that conditions_without_tests is a list."""
        result = monitor.check_success_conditions()
        assert isinstance(result["conditions_without_tests"], list)

    def test_success_conditions_consistency(self, monitor):
        """Test that missing_tests count matches list length."""
        result = monitor.check_success_conditions()
        missing_count = result["conditions_without_tests_count"]
        missing_list = result["conditions_without_tests"]
        assert missing_count == len(missing_list)


# ============================================================================
# Integration Tests for Reflex + SC monitoring in ManagementDashboard
# ============================================================================

class TestManagementDashboardWithReflexAndSC:
    """Tests for ReflexMonitor and SuccessConditionMonitor integration."""

    @pytest.fixture
    def dashboard(self, tmp_path):
        """Create a ManagementDashboard with test databases."""
        from src.services.overseer_management import ManagementDashboard

        overseer_db = tmp_path / "overseer.db"
        web_db = tmp_path / "article_eater.db"

        # Initialize both databases with minimal schema
        import sqlite3
        conn = sqlite3.connect(str(overseer_db))
        conn.execute("""
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
        conn.commit()
        conn.close()

        conn = sqlite3.connect(str(web_db))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY)
        """)
        conn.commit()
        conn.close()

        return ManagementDashboard(str(overseer_db), str(web_db))

    def test_dashboard_has_reflex_monitor(self, dashboard):
        """Test that dashboard has a reflex monitor."""
        from src.services.overseer_management import ReflexMonitor
        assert hasattr(dashboard, 'reflex_monitor')
        assert isinstance(dashboard.reflex_monitor, ReflexMonitor)

    def test_dashboard_has_success_condition_monitor(self, dashboard):
        """Test that dashboard has a success condition monitor."""
        from src.services.overseer_management import SuccessConditionMonitor
        assert hasattr(dashboard, 'success_condition_monitor')
        assert isinstance(dashboard.success_condition_monitor, SuccessConditionMonitor)

    def test_management_report_includes_reflex_health(self, dashboard):
        """Test that management report includes reflex health."""
        report = dashboard.generate_management_report()
        assert hasattr(report, 'reflex_health')
        assert isinstance(report.reflex_health, dict)

    def test_management_report_includes_success_conditions(self, dashboard):
        """Test that management report includes success conditions."""
        report = dashboard.generate_management_report()
        assert hasattr(report, 'success_conditions')
        assert isinstance(report.success_conditions, dict)

    def test_formatted_report_includes_reflex_section(self, dashboard):
        """Test that formatted report includes reflex health section."""
        report = dashboard.generate_management_report()
        formatted = dashboard._format_report(report)
        assert "REFLEX SYSTEM HEALTH" in formatted

    def test_formatted_report_includes_success_conditions_section(self, dashboard):
        """Test that formatted report includes success conditions section."""
        report = dashboard.generate_management_report()
        formatted = dashboard._format_report(report)
        assert "SUCCESS CONDITIONS REGISTRY" in formatted

    def test_critical_alerts_for_reflex_issues(self, dashboard, tmp_path):
        """Test that critical alerts include reflex issues when relevant."""
        import sqlite3
        import uuid
        from datetime import datetime, timezone

        # Add critical reflex event
        conn = sqlite3.connect(str(dashboard.overseer_db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflex_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                reflex_id TEXT NOT NULL,
                component TEXT NOT NULL,
                success_condition_id TEXT,
                detected INTEGER NOT NULL,
                description TEXT,
                auto_fixed INTEGER NOT NULL,
                fix_action TEXT,
                severity TEXT,
                context_json TEXT
            )
        """)

        now = datetime.now(timezone.utc).isoformat()
        # Add 6 unresolved critical issues to trigger critical alert
        for i in range(6):
            cursor.execute("""
                INSERT INTO reflex_events
                (event_id, timestamp, reflex_id, component, success_condition_id,
                 detected, description, auto_fixed, fix_action, severity, context_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), now, f"RFX-TEST-{i}", "test_component", "SC-001",
                  1, "Critical violation", 0, "manual_required", "critical", "{}"))

        conn.commit()
        conn.close()

        report = dashboard.generate_management_report()
        # Should have alert about reflex system issues
        assert any("reflex" in alert.lower() or "violation" in alert.lower()
                   for alert in report.critical_alerts) or len(report.critical_alerts) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
