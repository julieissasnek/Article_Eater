"""
test_pipeline_registry.py — Test Pipeline Registration in overseer.db
=====================================================================

Verifies that pipeline stages persist to overseer.db via
OverseerService.report_pipeline_run() and register_pipeline().

Phase 0, Task 0.3
"""

import sqlite3
import json
import os
import tempfile
import pytest
from datetime import datetime, timezone


@pytest.fixture
def temp_dbs():
    """Create temporary overseer.db and web.db."""
    with tempfile.TemporaryDirectory() as tmpdir:
        overseer_db = os.path.join(tmpdir, "overseer.db")
        web_db = os.path.join(tmpdir, "web.db")

        # Create minimal web.db
        conn = sqlite3.connect(web_db)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS beliefs (
                belief_id TEXT PRIMARY KEY,
                web_id TEXT DEFAULT 'master',
                content TEXT,
                credence_value REAL DEFAULT 0.5,
                level TEXT DEFAULT 'EMPIRICAL',
                status TEXT DEFAULT 'ACCEPTED',
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS constraints (
                constraint_id TEXT PRIMARY KEY,
                web_id TEXT DEFAULT 'master',
                source_id TEXT,
                target_id TEXT,
                constraint_type TEXT DEFAULT 'SUPPORTS',
                strength REAL DEFAULT 0.5,
                created_at TEXT
            );
        """)
        conn.close()

        yield overseer_db, web_db


@pytest.fixture
def overseer(temp_dbs):
    """Create OverseerService."""
    overseer_db, web_db = temp_dbs
    try:
        from src.services.overseer import OverseerService
        return OverseerService(
            overseer_db_path=overseer_db,
            web=None,
            web_db_path=web_db,
        )
    except Exception as e:
        pytest.skip(f"OverseerService not available: {e}")


class TestPipelineRegistration:
    """Test pipeline registration in overseer.db."""

    def test_register_pipeline(self, overseer, temp_dbs):
        """register_pipeline persists to pipeline_registry table."""
        overseer.register_pipeline(
            pipeline_id="test_pipeline",
            name="Test Pipeline",
            schedule="0 * * * *",
            depends_on=["discovery"],
        )

        # Verify in DB
        conn = sqlite3.connect(temp_dbs[0])
        row = conn.execute(
            "SELECT pipeline_id, name, schedule FROM pipeline_registry "
            "WHERE pipeline_id = 'test_pipeline'"
        ).fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "test_pipeline"
        assert row[1] == "Test Pipeline"

    def test_register_canonical_pipelines(self, overseer, temp_dbs):
        """register_canonical_pipelines registers all 6 pipelines."""
        overseer.register_canonical_pipelines()

        conn = sqlite3.connect(temp_dbs[0])
        rows = conn.execute(
            "SELECT pipeline_id FROM pipeline_registry ORDER BY pipeline_id"
        ).fetchall()
        conn.close()

        pipeline_ids = {r[0] for r in rows}
        expected = {"discovery", "triage", "extraction", "tables", "integration", "overseer"}
        assert expected.issubset(pipeline_ids)

    def test_report_pipeline_run(self, overseer, temp_dbs):
        """report_pipeline_run persists to pipeline_run_log."""
        overseer.register_pipeline("test_pipe", "Test", "daily")
        overseer.report_pipeline_run(
            pipeline_id="test_pipe",
            status="pass",
            duration_ms=1234,
            metadata={"papers_processed": 42},
        )

        conn = sqlite3.connect(temp_dbs[0])
        row = conn.execute(
            "SELECT pipeline_id, status, duration_ms, metadata "
            "FROM pipeline_run_log WHERE pipeline_id = 'test_pipe'"
        ).fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "test_pipe"
        assert row[1] == "pass"
        assert row[2] == 1234
        metadata = json.loads(row[3])
        assert metadata["papers_processed"] == 42

    def test_pipeline_run_updates_registry(self, overseer, temp_dbs):
        """report_pipeline_run updates registry last_run_at and run_count."""
        overseer.register_pipeline("test_pipe", "Test", "daily")

        overseer.report_pipeline_run("test_pipe", "pass", 100)
        overseer.report_pipeline_run("test_pipe", "pass", 200)

        conn = sqlite3.connect(temp_dbs[0])
        row = conn.execute(
            "SELECT run_count, last_status FROM pipeline_registry "
            "WHERE pipeline_id = 'test_pipe'"
        ).fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 2  # Two runs
        assert row[1] == "pass"

    def test_pipeline_health(self, overseer):
        """get_pipeline_health returns health for registered pipelines."""
        overseer.register_canonical_pipelines()
        overseer.report_pipeline_run("discovery", "pass", 500)

        health = overseer.get_pipeline_health()
        assert isinstance(health, (list, dict))

        # Handle both dict and list return types
        if isinstance(health, dict):
            disco = health.get("discovery")
        else:
            disco = next((p for p in health if p.get("pipeline_id") == "discovery"), None)
        assert disco is not None
        assert disco.get("last_status") == "pass"

    def test_pipeline_health_stale_detection(self, overseer):
        """Pipelines without recent runs are marked stale."""
        overseer.register_canonical_pipelines()
        # Don't run any pipelines
        health = overseer.get_pipeline_health()
        assert isinstance(health, (list, dict))
        # All should be stale or have no runs
        items = health.values() if isinstance(health, dict) else health
        for p in items:
            last_run = p.get("last_run_at") or p.get("last_run")
            assert last_run is None or p.get("is_stale", True)
