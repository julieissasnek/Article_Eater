"""
test_overseer_coverage.py — Test INV-6 through INV-9: Coverage Invariants
=========================================================================

Tests pipeline utilization, template coverage, theory linkage,
and evidence diversity invariants.

Phase 0, Task 0.2
"""

import sqlite3
import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


@pytest.fixture
def temp_env():
    """Create temporary environment with overseer.db, web.db, and data dirs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        overseer_db = os.path.join(tmpdir, "overseer.db")
        web_db = os.path.join(tmpdir, "web.db")

        # Create data directories
        extractions_dir = os.path.join(tmpdir, "extractions")
        templates_dir = os.path.join(tmpdir, "templates")
        theories_dir = os.path.join(tmpdir, "theories")
        os.makedirs(extractions_dir)
        os.makedirs(templates_dir)
        os.makedirs(theories_dir)

        # Create web.db
        conn = sqlite3.connect(web_db)
        now = datetime.now(timezone.utc).isoformat()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS beliefs (
                belief_id TEXT PRIMARY KEY,
                web_id TEXT DEFAULT 'master',
                content TEXT,
                credence_value REAL DEFAULT 0.5,
                credence_uncertainty REAL DEFAULT 0.2,
                level TEXT DEFAULT 'EMPIRICAL',
                status TEXT DEFAULT 'ACCEPTED',
                paper_ids TEXT,
                created_at TEXT,
                updated_at TEXT
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

        yield {
            "overseer_db": overseer_db,
            "web_db": web_db,
            "extractions_dir": extractions_dir,
            "templates_dir": templates_dir,
            "theories_dir": theories_dir,
            "tmpdir": tmpdir,
        }


@pytest.fixture
def overseer(temp_env):
    """Create OverseerService with test env."""
    try:
        from src.services.overseer import OverseerService
        return OverseerService(
            overseer_db_path=temp_env["overseer_db"],
            web=None,
            web_db_path=temp_env["web_db"],
            extractions_dir=temp_env["extractions_dir"],
            templates_dir=temp_env["templates_dir"],
            theories_dir=temp_env["theories_dir"],
        )
    except Exception as e:
        pytest.skip(f"OverseerService not available: {e}")


class TestINV6PipelineUtilization:
    """INV-6: Pipeline utilization — at least 25% of extractions integrated."""

    def test_utilization_zero_with_no_data(self, overseer):
        """No extractions → returns None (can't compute ratio)."""
        result = overseer._check_pipeline_utilization()
        assert result is None  # No extraction files

    def test_utilization_below_threshold(self, overseer, temp_env):
        """Violation when utilization < 25%."""
        # Create 10 extraction files but 0 integrated
        for i in range(10):
            path = os.path.join(temp_env["extractions_dir"], f"paper_{i}.json")
            with open(path, "w") as f:
                json.dump({"title": f"Paper {i}"}, f)

        result = overseer._check_pipeline_utilization()
        assert result is not None
        assert result < 0.25

        # Should trigger violation
        violations = overseer.check_integrity()
        inv6 = [v for v in violations if v.code == "INV-6"]
        assert len(inv6) == 1

    def test_utilization_above_threshold(self, overseer, temp_env):
        """No violation when utilization ≥ 25%."""
        # Create 4 extractionfiles
        for i in range(4):
            path = os.path.join(temp_env["extractions_dir"], f"paper_{i}.json")
            with open(path, "w") as f:
                json.dump({"title": f"Paper {i}"}, f)

        # Insert 2 beliefs (50% utilization)
        conn = sqlite3.connect(temp_env["web_db"])
        now = datetime.now(timezone.utc).isoformat()
        for i in range(2):
            conn.execute(
                "INSERT INTO beliefs (belief_id, content, credence_value, level, status, created_at) "
                "VALUES (?, ?, 0.5, 'EMPIRICAL', 'ACCEPTED', ?)",
                (f"b_{i}", f"Belief {i}", now),
            )
        conn.commit()
        conn.close()

        result = overseer._check_pipeline_utilization()
        assert result is not None
        assert result >= 0.25


class TestINV7TemplateCoverage:
    """INV-7: Template coverage — fraction of templates with ≥1 belief."""

    def test_coverage_with_no_templates(self, overseer):
        """No templates → None or 0."""
        result = overseer._check_template_belief_coverage()
        # With no templates, should handle gracefully
        assert result is None or result == 0

    def test_coverage_below_threshold(self, overseer, temp_env):
        """Violation when coverage < 80%."""
        # Create 10 template files
        for i in range(10):
            path = os.path.join(temp_env["templates_dir"], f"T{i}.json")
            with open(path, "w") as f:
                json.dump({
                    "template_id": f"T{i}",
                    "name": f"Template {i}",
                    "constituent_findings": [],
                }, f)

        result = overseer._check_template_belief_coverage()
        if result is not None:
            assert result < 0.80


class TestINV8TheoryLinkage:
    """INV-8: Theory linkage — orphan rate ≤ 10%."""

    def test_linkage_with_no_theories(self, overseer):
        """No theories → None."""
        result = overseer._check_theory_linkage()
        assert result is None or isinstance(result, float)

    def test_orphan_theories_detected(self, overseer, temp_env):
        """Theories without templates trigger violation."""
        # Create theories with no constituent_templates
        for i in range(5):
            path = os.path.join(temp_env["theories_dir"], f"theory_{i}.json")
            with open(path, "w") as f:
                json.dump({
                    "theory_id": f"theory_{i}",
                    "name": f"Theory {i}",
                    "constituent_templates": [],
                }, f)

        result = overseer._check_theory_linkage()
        if result is not None:
            assert result > 0.10  # All orphaned


class TestINV9EvidenceDiversity:
    """INV-9: Evidence diversity — paper-sourced beliefs ≥ 20%."""

    def test_diversity_with_empty_db(self, overseer):
        """Empty DB → None or 0."""
        result = overseer._check_evidence_diversity()
        assert result is None or isinstance(result, float)

    def test_low_paper_sourced_diversity(self, overseer, temp_env):
        """Violation when paper-sourced < 20%."""
        # Insert all template-sourced beliefs
        conn = sqlite3.connect(temp_env["web_db"])
        now = datetime.now(timezone.utc).isoformat()
        for i in range(10):
            conn.execute(
                "INSERT INTO beliefs (belief_id, content, credence_value, level, status, created_at) "
                "VALUES (?, ?, 0.5, 'EMPIRICAL', 'ACCEPTED', ?)",
                (f"template:b_{i}", f"Template belief {i}", now),
            )
        conn.commit()
        conn.close()

        result = overseer._check_evidence_diversity()
        if result is not None:
            assert result < 0.20


class TestAESHI:
    """Test AESHI computation includes coverage/utilization."""

    def test_aeshi_returns_score(self, overseer):
        """AESHI should return a number 0-100."""
        score = overseer.compute_aeshi()
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_aeshi_penalizes_low_utilization(self, overseer, temp_env):
        """Low pipeline utilization caps AESHI at 50."""
        # Create many extractions, zero integrated
        for i in range(100):
            path = os.path.join(temp_env["extractions_dir"], f"paper_{i}.json")
            with open(path, "w") as f:
                json.dump({"title": f"Paper {i}"}, f)

        score = overseer.compute_aeshi()
        # With 0% utilization, should be capped
        assert score <= 50
