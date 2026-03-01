"""
test_cva_post_remediation.py — Tests for Post-Remediation Tasks
================================================================

Comprehensive tests for:
  1. Migration 023 (overseer tables)
  2. Migration 024 (CVA persistence tables)
  3. CVA pipeline stage integration
  4. Template ↔ CVA linking
  5. Dashboard data generation
"""

import pytest
import sqlite3
import json
import os
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════════════════
# 1. Migration Tests
# ══════════════════════════════════════════════════════════════════

class TestMigrations:
    """Test migration 023 (overseer) and 024 (CVA persistence)."""

    def _make_db(self):
        """Create in-memory DB with baseline schema and run all migrations."""
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        # Create baseline tables that early migrations expect
        cur.execute("""
            CREATE TABLE IF NOT EXISTS web_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS beliefs (
                id TEXT PRIMARY KEY,
                web_id TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS constraints (
                id TEXT PRIMARY KEY,
                web_id TEXT
            )
        """)
        conn.commit()
        from src.services.db_migrations import MigrationManager
        mgr = MigrationManager(conn)
        mgr.run_pending_migrations()
        return conn

    def test_all_migrations_run(self):
        """All migrations run without error."""
        conn = self._make_db()
        from src.services.db_migrations import MigrationManager
        mgr = MigrationManager(conn)
        assert mgr.get_current_version() >= 10
        conn.close()

    def test_overseer_health_metrics_table_exists(self):
        """Migration 023 creates overseer_health_metrics table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='overseer_health_metrics'")
        assert cur.fetchone() is not None
        conn.close()

    def test_overseer_violations_table_exists(self):
        """Migration 023 creates overseer_invariant_violations table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='overseer_invariant_violations'")
        assert cur.fetchone() is not None
        conn.close()

    def test_overseer_quarantine_table_exists(self):
        """Migration 023 creates overseer_quarantine table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='overseer_quarantine'")
        assert cur.fetchone() is not None
        conn.close()

    def test_overseer_snapshots_table_exists(self):
        """Migration 023 creates overseer_snapshots table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='overseer_snapshots'")
        assert cur.fetchone() is not None
        conn.close()

    def test_cva_constraint_states_table(self):
        """Migration 024 creates cva_constraint_states table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cva_constraint_states'")
        assert cur.fetchone() is not None
        conn.close()

    def test_cva_valuation_states_table(self):
        """Migration 024 creates cva_valuation_states table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cva_valuation_states'")
        assert cur.fetchone() is not None
        conn.close()

    def test_cva_attractor_states_table(self):
        """Migration 024 creates cva_attractor_states table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cva_attractor_states'")
        assert cur.fetchone() is not None
        conn.close()

    def test_cva_annotations_table(self):
        """Migration 024 creates cva_annotations table."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cva_annotations'")
        assert cur.fetchone() is not None
        conn.close()

    def test_insert_into_overseer_health_metrics(self):
        """Can insert a health metric row."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO overseer_health_metrics (mode, global_coherence, total_beliefs)
            VALUES ('PERIODIC', 0.82, 500)
        """)
        conn.commit()
        cur.execute("SELECT global_coherence, total_beliefs FROM overseer_health_metrics")
        row = cur.fetchone()
        assert row == (0.82, 500)
        conn.close()

    def test_insert_into_cva_constraint_states(self):
        """Can insert a CVA constraint state row."""
        conn = self._make_db()
        cur = conn.cursor()
        mean_json = json.dumps([0.5] * 8)
        cur.execute("""
            INSERT INTO cva_constraint_states (subject_id, activity_frame, mean_json, entropy)
            VALUES ('subj_001', 'RESTING', ?, 3.14)
        """, (mean_json,))
        conn.commit()
        cur.execute("SELECT subject_id, entropy FROM cva_constraint_states")
        row = cur.fetchone()
        assert row == ('subj_001', 3.14)
        conn.close()

    def test_insert_into_cva_valuation_states(self):
        """Can insert a CVA valuation state row."""
        conn = self._make_db()
        cur = conn.cursor()
        core_json = json.dumps([0.5] * 9)
        cur.execute("""
            INSERT INTO cva_valuation_states (subject_id, cultural_variant, core_json, beauty_score)
            VALUES ('subj_001', 'WESTERN', ?, 0.75)
        """, (core_json,))
        conn.commit()
        cur.execute("SELECT beauty_score FROM cva_valuation_states")
        assert cur.fetchone()[0] == 0.75
        conn.close()

    def test_insert_into_cva_attractor_states(self):
        """Can insert a CVA attractor state row."""
        conn = self._make_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cva_attractor_states (subject_id, attractor_name, is_stable, kappa_loop)
            VALUES ('subj_001', 'sringara', 1, 0.038)
        """)
        conn.commit()
        cur.execute("SELECT attractor_name, kappa_loop FROM cva_attractor_states")
        row = cur.fetchone()
        assert row == ('sringara', 0.038)
        conn.close()

    def test_migration_idempotency(self):
        """Running migrations twice doesn't error."""
        conn = self._make_db()
        from src.services.db_migrations import MigrationManager
        mgr = MigrationManager(conn)
        # Should be 0 pending
        assert mgr.run_pending_migrations() == 0
        conn.close()


# ══════════════════════════════════════════════════════════════════
# 2. Template ↔ CVA Linking Tests
# ══════════════════════════════════════════════════════════════════

class TestTemplateCVALinker:
    """Test CVATemplateLinker service."""

    def test_link_template_basic(self):
        """Link returns correct constraint/valuation tags."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        link = linker.link_template("T4_prospect_refuge")
        assert "control_efficacy" in link.constraint_tags
        assert "SafetyValue" in link.valuation_tags
        assert "M_CCT_PREFERENCE" in link.molecule_links

    def test_link_all_templates(self):
        """All templates linked successfully."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        links = linker.link_all_templates()
        assert len(links) >= 12

    def test_unknown_template(self):
        """Unknown template returns empty tags."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        link = linker.link_template("T999_nonexistent")
        assert link.constraint_tags == []
        assert link.valuation_tags == []
        assert link.molecule_links == []

    def test_get_templates_for_constraint(self):
        """Find templates predicting about a specific constraint."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        templates = linker.get_templates_for_constraint("prediction_error")
        assert len(templates) >= 3  # Multiple templates involve prediction error

    def test_get_templates_for_valuation(self):
        """Find templates relating to a specific valuation."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        templates = linker.get_templates_for_valuation("SafetyValue")
        assert len(templates) >= 2

    def test_coverage_report(self):
        """Coverage report has correct structure."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        report = linker.coverage_report()
        assert "constraint_coverage" in report
        assert "valuation_coverage" in report
        assert "uncovered_constraints" in report
        assert len(report["constraint_coverage"]) == 8

    def test_export_links_to_json(self):
        """Export produces valid JSON file."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            count = linker.export_links(path)
            assert count >= 12
            data = json.loads(Path(path).read_text())
            assert "template_cva_links" in data
            assert data["total_templates"] >= 12
        finally:
            os.unlink(path)

    def test_to_dict_roundtrip(self):
        """TemplateCVALink.to_dict() produces serializable dict."""
        from src.services.cva_template_linker import CVATemplateLinker
        linker = CVATemplateLinker()
        link = linker.link_template("T8_cultural_meaning")
        d = link.to_dict()
        assert d["template_id"] == "T8_cultural_meaning"
        assert "M_RASA" in d["molecule_links"]
        # Verify JSON-serializable
        json.dumps(d)


# ══════════════════════════════════════════════════════════════════
# 3. Dashboard Generation Tests
# ══════════════════════════════════════════════════════════════════

class TestDashboard:
    """Test CVA dashboard data generators."""

    def test_neurotype_sensitivity(self):
        """Neurotype sensitivity generator produces valid JSON."""
        from src.services.cva_dashboard import generate_neurotype_sensitivity
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_neurotype_sensitivity(tmpdir)
            data = json.loads(Path(path).read_text())
            assert "neurotypes" in data
            assert "ptsd" in data["neurotypes"]
            assert data["neurotypes"]["ptsd"]["prediction_error"] == 2.0

    def test_frame_precision_heatmap(self):
        """Frame precision heatmap covers all 10 frames."""
        from src.services.cva_dashboard import generate_frame_precision_heatmap
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_frame_precision_heatmap(tmpdir)
            data = json.loads(Path(path).read_text())
            assert len(data["frames"]) == 10
            assert "RESTING" in data["frames"]
            assert "EXERCISING" in data["frames"]

    def test_template_coverage(self):
        """Template coverage matrix generated."""
        from src.services.cva_dashboard import generate_template_coverage
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_template_coverage(tmpdir)
            data = json.loads(Path(path).read_text())
            assert data["total_templates"] >= 12
            assert "constraint_coverage" in data


# ══════════════════════════════════════════════════════════════════
# 4. Pipeline Stage Tests
# ══════════════════════════════════════════════════════════════════

class TestPipelineStage:
    """Test CVA enrichment pipeline stage."""

    def test_cva_stage_registered(self):
        """CVA stage is in pipeline STAGES dict."""
        import importlib
        # Patch the FileHandler to avoid sandbox log file issues
        with patch("logging.FileHandler", MagicMock()):
            import scripts.scheduled_pipeline as sp
            importlib.reload(sp)
            assert "cva" in sp.STAGES

    def test_cva_enrichment_runs(self):
        """run_cva_enrichment() completes without error."""
        with patch("logging.FileHandler", MagicMock()):
            import scripts.scheduled_pipeline as sp
            result = sp.run_cva_enrichment()
            assert result is True


# ══════════════════════════════════════════════════════════════════
# 5. Cross-Component Integration Tests
# ══════════════════════════════════════════════════════════════════

class TestCrossComponentIntegration:
    """Test integration across migrations, persistence, and pipeline."""

    def _make_db(self):
        """Helper: create in-memory DB with baseline schema and run migrations."""
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS web_metadata (key TEXT PRIMARY KEY, value TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS beliefs (id TEXT PRIMARY KEY, web_id TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS constraints (id TEXT PRIMARY KEY, web_id TEXT)")
        conn.commit()
        from src.services.db_migrations import MigrationManager
        mgr = MigrationManager(conn)
        mgr.run_pending_migrations()
        return conn

    def test_full_persistence_roundtrip(self):
        """Compute CVA → persist to DB → read back."""
        from src.services.cva_constraint_engine import CVAConstraintEngine
        from src.services.cva_valuation_engine import CVAValuationEngine

        # Setup DB
        conn = self._make_db()

        # Compute CVA
        c_engine = CVAConstraintEngine()
        v_engine = CVAValuationEngine()
        scene = {"edge": 0.7, "motion": 0.5, "contrast": 0.6,
                 "figure_ground": 0.8, "temporal_coherence": 0.5, "symmetry": 0.4}
        constraints = c_engine.compute(scene)
        dist = c_engine.recognize_constraints_probabilistic(scene, "STUDYING")
        valuations = v_engine.compute(constraints)

        # Persist constraint state
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cva_constraint_states (subject_id, activity_frame, mean_json, entropy)
            VALUES ('test_subj', 'STUDYING', ?, ?)
        """, (json.dumps(list(dist.mean)), dist.entropy()))
        constraint_state_id = cur.lastrowid

        # Persist valuation state
        cur.execute("""
            INSERT INTO cva_valuation_states (constraint_state_id, subject_id, cultural_variant, core_json)
            VALUES (?, 'test_subj', ?, ?)
        """, (constraint_state_id, str(valuations.variant), json.dumps(valuations.values)))
        conn.commit()

        # Read back
        cur.execute("SELECT mean_json, entropy FROM cva_constraint_states WHERE subject_id='test_subj'")
        row = cur.fetchone()
        read_mean = json.loads(row[0])
        assert len(read_mean) == 8
        assert row[1] == pytest.approx(dist.entropy(), abs=1e-6)

        cur.execute("SELECT core_json FROM cva_valuation_states WHERE subject_id='test_subj'")
        row = cur.fetchone()
        read_vals = json.loads(row[0])
        assert len(read_vals) >= 5

        conn.close()

    def test_template_linker_with_constraint_engine(self):
        """Template linker tags match constraint engine dimensions."""
        from src.services.cva_template_linker import CVATemplateLinker
        from src.models.cva_constraint import Tier2ConstraintVector

        linker = CVATemplateLinker()
        link = linker.link_template("T3_restoration_attention")

        # All constraint tags should be valid Tier 2 constraint names
        valid_constraints = set(Tier2ConstraintVector.__dataclass_fields__.keys())
        for tag in link.constraint_tags:
            assert tag in valid_constraints, f"{tag} not a valid Tier 2 constraint"

    def test_dynamics_with_persistence(self):
        """Dynamics engine output can be persisted to attractor_states."""
        from src.services.cva_dynamics import CVADynamicsEngine, CVACouplingMatrices
        from src.services.db_migrations import MigrationManager

        conn = self._make_db()

        engine = CVADynamicsEngine()
        coupling = CVACouplingMatrices.default()
        fp = np.zeros(17)
        stab = engine.check_attractor_stability(fp, coupling)

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cva_attractor_states
                (subject_id, attractor_name, fixed_point_json, is_stable, kappa_loop, max_real_eigenvalue)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'test_subj', 'origin', json.dumps(fp.tolist()),
            1 if stab["is_stable"] else 0,
            stab["kappa_loop"],
            stab["max_real_eigenvalue"],
        ))
        conn.commit()

        cur.execute("SELECT kappa_loop FROM cva_attractor_states WHERE attractor_name='origin'")
        row = cur.fetchone()
        assert row[0] == pytest.approx(stab["kappa_loop"], abs=1e-6)
        conn.close()
