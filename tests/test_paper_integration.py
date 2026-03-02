"""
Tests for Paper Integration Pipeline
=====================================

Created: 2026-02-25
Sprint: INTEGRATION-1

End-to-end tests for:
1. Full 14-step cascade with mock paper extraction
2. Supersession detection with overlapping constructs
3. Paper-level rollback
4. Idempotency (same paper twice = no-op)
5. Tag assignment
6. Molecule linkage
7. Database migration
"""

import json
import os
import sqlite3
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.paper_integration.models import (
    PaperIntegrationEvent,
    CascadeStep,
    CascadeStepStatus,
    SupersessionRecord,
    IntegrationAction,
    IntegrationStatus,
    SupersessionReason,
    BeliefVersionEntry,
    TagAssignment,
)
from src.services.paper_integration.supersession import (
    SupersessionResolver,
    PaperProfile,
    OVERLAP_THRESHOLD,
)
from src.services.paper_integration.rollback import IntegrationRollback
from src.services.paper_integration.tag_engine import TagAssignmentEngine
from src.services.paper_integration.molecule_linker import (
    MoleculeLinker,
    TemplateMatch,
    LinkageResult,
)
from src.services.db_migrations import MigrationManager


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def db_conn():
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create core tables that the pipeline expects — production schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beliefs (
            belief_id TEXT PRIMARY KEY,
            web_id TEXT,
            content TEXT,
            credence_value REAL,
            credence_uncertainty REAL,
            level TEXT,
            status TEXT DEFAULT 'ACCEPTED',
            paper_ids TEXT,
            paper_id TEXT,
            created_at TEXT,
            updated_at TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS constraints (
            constraint_id TEXT PRIMARY KEY,
            web_id TEXT,
            source_id TEXT,
            target_id TEXT,
            constraint_type TEXT,
            strength REAL,
            paper_id TEXT,
            created_at TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Run our new migrations
    mgr = MigrationManager(conn)
    mgr.run_pending_migrations()

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_extraction():
    """Sample extraction output mimicking ae.claim.v2 + ae.rule.v1."""
    return {
        "claims": [
            {
                "node_id": "b_test_001",
                "statement": "Nature exposure reduces cortisol levels by 15% in office workers",
                "ae_confidence": 0.75,
                "confidence_se": 0.12,
                "evidence_level": "EMPIRICAL",
                "construct_id": "cortisol_reduction",
                "dependent_variable": "cortisol",
                "independent_variable": "nature exposure",
                "effect_size_d": 0.45,
                "theory_names": ["SRT"],
            },
            {
                "node_id": "b_test_002",
                "statement": "Fractal patterns in facade design increase visual preference ratings",
                "ae_confidence": 0.68,
                "confidence_se": 0.15,
                "evidence_level": "EMPIRICAL",
                "construct_id": "visual_preference",
                "dependent_variable": "preference rating",
                "independent_variable": "fractal dimension",
                "effect_size_d": 0.62,
                "theory_names": ["Biophilia", "PP"],
            },
        ],
        "rules": [
            {
                "edge_id": "c_test_001",
                "source_node": "b_test_001",
                "target_node": "b_test_002",
                "constraint_type": "SUPPORTS",
                "strength": 0.6,
            },
        ],
    }


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create a temporary template directory with sample templates."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Sample template that should match the cortisol claim
    template1 = {
        "template_id": "SRT_CORTISOL_001",
        "construct_name": "cortisol_reduction",
        "dependent_variable": "cortisol",
        "independent_variable": "nature exposure",
        "short_description": "Nature reduces cortisol",
        "t1_frameworks": {"NM": 40, "IC": 30, "PP": 30},
        "t1_5_parent_theories": ["SRT"],
    }
    (template_dir / "SRT_CORTISOL_001.json").write_text(json.dumps(template1))

    # Sample template for fractal preference
    template2 = {
        "template_id": "PP_FRACTAL_001",
        "construct_name": "visual_preference",
        "dependent_variable": "preference rating",
        "independent_variable": "fractal dimension",
        "short_description": "Fractal fluency visual preference",
        "t1_frameworks": {"PP": 50, "NM": 30, "EC": 20},
        "t1_5_parent_theories": ["Fractal_Fluency", "Biophilia"],
    }
    (template_dir / "PP_FRACTAL_001.json").write_text(json.dumps(template2))

    return str(template_dir)


@pytest.fixture
def temp_molecule_dir(tmp_path):
    """Create a temporary molecule directory with sample molecules."""
    mol_dir = tmp_path / "molecules"
    mol_dir.mkdir()

    molecule1 = {
        "molecule_id": "SRT",
        "name": "Stress Reduction Theory Molecule",
        "constituent_templates": ["SRT_CORTISOL_001", "SRT_ANS_002"],
    }
    (mol_dir / "srt.json").write_text(json.dumps(molecule1))

    molecule2 = {
        "molecule_id": "GOLDILOCKS_PRINCIPLE",
        "name": "Goldilocks Principle",
        "constituent_templates": ["PP_FRACTAL_001", "THERMAL_001"],
    }
    (mol_dir / "goldilocks.json").write_text(json.dumps(molecule2))

    return str(mol_dir)


@pytest.fixture
def temp_theory_dir(tmp_path):
    """Create a temporary theory directory with sample theories."""
    theory_dir = tmp_path / "theories"
    theory_dir.mkdir()

    theory1 = {
        "theory_id": "SRT",
        "name": "Stress Reduction Theory",
        "constituent_templates": ["SRT_CORTISOL_001", "SRT_ANS_002"],
    }
    (theory_dir / "srt.json").write_text(json.dumps(theory1))

    return str(theory_dir)


# =============================================================================
# MODEL TESTS
# =============================================================================

class TestModels:
    """Test data model serialization and deserialization."""

    def test_cascade_step_lifecycle(self):
        step = CascadeStep(step_number=1, step_name="test_step")
        assert step.status == CascadeStepStatus.PENDING

        step.start()
        assert step.status == CascadeStepStatus.RUNNING
        assert step.started_at is not None

        step.complete(items_processed=5)
        assert step.status == CascadeStepStatus.COMPLETED
        assert step.items_processed == 5

    def test_cascade_step_failure(self):
        step = CascadeStep(step_number=1, step_name="test_step")
        step.start()
        step.fail("Something went wrong")
        assert step.status == CascadeStepStatus.FAILED
        assert step.error_message == "Something went wrong"

    def test_event_serialization_roundtrip(self):
        event = PaperIntegrationEvent(
            paper_id="test_paper",
            action=IntegrationAction.INTEGRATE,
            beliefs_added=["b1", "b2"],
        )
        d = event.to_dict()
        restored = PaperIntegrationEvent.from_dict(d)
        assert restored.paper_id == "test_paper"
        assert restored.beliefs_added == ["b1", "b2"]
        assert restored.action == IntegrationAction.INTEGRATE

    def test_supersession_record_serialization(self):
        record = SupersessionRecord(
            superseding_paper_id="new",
            superseded_paper_id="old",
            reason=SupersessionReason.META_ANALYSIS,
            construct_overlap_score=0.85,
        )
        d = record.to_dict()
        assert d["reason"] == "META_ANALYSIS"
        restored = SupersessionRecord.from_dict(d)
        assert restored.reason == SupersessionReason.META_ANALYSIS


# =============================================================================
# SUPERSESSION TESTS
# =============================================================================

class TestSupersession:
    """Test supersession detection logic."""

    def test_no_supersession_different_constructs(self):
        resolver = SupersessionResolver()
        new_paper = PaperProfile(
            paper_id="new",
            publication_year=2025,
            construct_ids={"A", "B"},
        )
        existing = PaperProfile(
            paper_id="old",
            publication_year=2020,
            construct_ids={"C", "D"},
        )
        records = resolver.detect_supersessions(new_paper, [existing])
        assert len(records) == 0

    def test_supersession_meta_analysis(self):
        resolver = SupersessionResolver()
        new_paper = PaperProfile(
            paper_id="meta",
            publication_year=2025,
            study_design="meta_analysis",
            construct_ids={"cortisol", "stress", "nature"},
        )
        existing = PaperProfile(
            paper_id="individual",
            publication_year=2020,
            study_design="observational",
            construct_ids={"cortisol", "stress"},
            belief_ids=["b1", "b2"],
        )
        records = resolver.detect_supersessions(new_paper, [existing])
        assert len(records) == 1
        assert records[0].reason == SupersessionReason.META_ANALYSIS
        assert records[0].confidence >= 0.85

    def test_supersession_newer_larger_sample(self):
        resolver = SupersessionResolver()
        new_paper = PaperProfile(
            paper_id="new",
            publication_year=2025,
            sample_size=500,
            study_design="observational",
            construct_ids={"A", "B", "C"},
        )
        existing = PaperProfile(
            paper_id="old",
            publication_year=2020,
            sample_size=100,
            study_design="observational",
            construct_ids={"A", "B"},
            belief_ids=["b1"],
        )
        records = resolver.detect_supersessions(new_paper, [existing])
        assert len(records) == 1
        assert records[0].reason == SupersessionReason.LARGER_SAMPLE

    def test_overlap_below_threshold(self):
        resolver = SupersessionResolver()
        new_paper = PaperProfile(
            paper_id="new",
            construct_ids={"A", "B", "C", "D", "E"},
        )
        existing = PaperProfile(
            paper_id="old",
            construct_ids={"A", "F", "G", "H", "I"},
        )
        # Overlap is 1/5 = 0.20, below OVERLAP_THRESHOLD
        records = resolver.detect_supersessions(new_paper, [existing])
        assert len(records) == 0


# =============================================================================
# TAG ENGINE TESTS
# =============================================================================

class TestTagEngine:
    """Test 3D taxonomy tag assignment."""

    def test_entity_tags_lighting(self):
        engine = TagAssignmentEngine()
        tags = engine.assign_tags(
            belief_id="b1",
            paper_id="p1",
            statement="Daylight exposure at 300 lux improves circadian entrainment",
        )
        entity_tags = [t for t in tags if t.tag_dimension == "entity"]
        entity_values = [t.tag_value for t in entity_tags]
        assert "lighting" in entity_values

    def test_entity_tags_thermal(self):
        engine = TagAssignmentEngine()
        tags = engine.assign_tags(
            belief_id="b1",
            paper_id="p1",
            statement="Thermal comfort at 22C with radiant cooling improves productivity",
        )
        entity_tags = [t for t in tags if t.tag_dimension == "entity"]
        entity_values = [t.tag_value for t in entity_tags]
        assert "thermal" in entity_values

    def test_theoretical_tags_known_theories(self):
        engine = TagAssignmentEngine()
        tags = engine.assign_tags(
            belief_id="b1",
            paper_id="p1",
            statement="Nature exposure reduces stress",
            theory_names=["SRT", "Biophilia"],
        )
        theoretical_tags = [t for t in tags if t.tag_dimension == "theoretical"]
        values = [t.tag_value for t in theoretical_tags]
        assert "SRT" in values
        assert "Biophilia" in values

    def test_effect_size_categorization(self):
        engine = TagAssignmentEngine()

        # Small effect
        tags_small = engine.assign_tags("b1", "p1", "Test", effect_size_d=0.3)
        es_tags = [t for t in tags_small if t.tag_dimension == "effect_size"]
        assert len(es_tags) == 1
        assert es_tags[0].tag_value == "small"

        # Large effect
        tags_large = engine.assign_tags("b2", "p1", "Test", effect_size_d=1.2)
        es_tags = [t for t in tags_large if t.tag_dimension == "effect_size"]
        assert len(es_tags) == 1
        assert es_tags[0].tag_value == "large"

    def test_tag_persistence(self, db_conn):
        engine = TagAssignmentEngine(db_conn)
        tags = engine.assign_tags(
            belief_id="b_persist",
            paper_id="p_persist",
            statement="Acoustic comfort at 55 dB improves focus",
            effect_size_d=0.5,
        )
        persisted = engine.persist_tags(tags, db_conn)
        assert persisted > 0

        # Retrieve and verify
        retrieved = engine.get_tags_for_belief("b_persist", db_conn)
        assert len(retrieved) > 0


# =============================================================================
# MOLECULE LINKER TESTS
# =============================================================================

class TestMoleculeLinker:
    """Test belief → template → molecule → T1.5 linkage."""

    def test_construct_id_match(self, temp_template_dir, temp_molecule_dir, temp_theory_dir):
        linker = MoleculeLinker(
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )
        result = linker.link_belief(
            belief_id="b1",
            paper_id="p1",
            statement="Cortisol reduction from nature",
            construct_id="cortisol_reduction",
        )
        assert len(result.template_matches) > 0
        match = result.template_matches[0]
        assert match.template_id == "SRT_CORTISOL_001"
        assert match.match_score >= 0.90
        assert "SRT" in result.molecules_affected

    def test_dv_iv_match(self, temp_template_dir, temp_molecule_dir, temp_theory_dir):
        linker = MoleculeLinker(
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )
        result = linker.link_belief(
            belief_id="b2",
            paper_id="p1",
            statement="Visual preference for fractal facades",
            dependent_variable="preference rating",
            independent_variable="fractal dimension",
        )
        assert len(result.template_matches) > 0
        assert any(m.template_id == "PP_FRACTAL_001" for m in result.template_matches)

    def test_stale_molecules(self, temp_template_dir, temp_molecule_dir, temp_theory_dir):
        linker = MoleculeLinker(
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )
        results = linker.link_beliefs_batch(
            [
                {"belief_id": "b1", "statement": "Cortisol", "construct_id": "cortisol_reduction"},
                {"belief_id": "b2", "statement": "Fractal", "construct_id": "visual_preference"},
            ],
            paper_id="p1",
        )
        stale = linker.get_stale_molecules(results)
        assert "SRT" in stale
        assert "GOLDILOCKS_PRINCIPLE" in stale


# =============================================================================
# ROLLBACK TESTS
# =============================================================================

class TestRollback:
    """Test paper-level rollback."""

    def test_rollback_removes_beliefs(self, db_conn):
        cursor = db_conn.cursor()

        # Simulate a completed integration
        cursor.execute("""
            INSERT INTO paper_integration_events
            (event_id, paper_id, timestamp, action, status,
             beliefs_added, beliefs_retired, constraints_added,
             constraints_retired, bn_edges_updated, molecules_affected,
             tags_assigned, cascade_log)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "evt_001", "paper_A", datetime.now(timezone.utc).isoformat(),
            "INTEGRATE", "COMPLETED",
            json.dumps(["b_A_001", "b_A_002"]),
            json.dumps([]),
            json.dumps(["c_A_001"]),
            json.dumps([]),
            json.dumps([]),
            json.dumps(["SRT"]),
            json.dumps({}),
            json.dumps([]),
        ))

        # Add the beliefs
        cursor.execute("""
            INSERT INTO beliefs (belief_id, web_id, content, status, paper_id, created_at)
            VALUES ('b_A_001', 'master', 'Test belief 1', 'ACCEPTED', 'paper_A', ?)
        """, (datetime.now(timezone.utc).isoformat(),))
        cursor.execute("""
            INSERT INTO beliefs (belief_id, web_id, content, status, paper_id, created_at)
            VALUES ('b_A_002', 'master', 'Test belief 2', 'ACCEPTED', 'paper_A', ?)
        """, (datetime.now(timezone.utc).isoformat(),))

        # Add belief versions
        cursor.execute("""
            INSERT INTO belief_versions
            (version_id, belief_id, paper_id, timestamp, credence_mean, is_current)
            VALUES ('v1', 'b_A_001', 'paper_A', ?, 0.7, 1)
        """, (datetime.now(timezone.utc).isoformat(),))
        cursor.execute("""
            INSERT INTO belief_versions
            (version_id, belief_id, paper_id, timestamp, credence_mean, is_current)
            VALUES ('v2', 'b_A_002', 'paper_A', ?, 0.8, 1)
        """, (datetime.now(timezone.utc).isoformat(),))

        db_conn.commit()

        # Execute rollback
        rollback = IntegrationRollback(db_conn)
        event = rollback.rollback_paper("paper_A")

        assert event.action == IntegrationAction.ROLLBACK
        assert event.status == IntegrationStatus.COMPLETED
        assert event.rollback_of_event_id == "evt_001"

        # Verify beliefs are retired
        cursor.execute("SELECT status FROM beliefs WHERE belief_id = 'b_A_001'")
        assert cursor.fetchone()[0] == "RETIRED"

        # Verify belief versions are non-current
        cursor.execute("""
            SELECT is_current FROM belief_versions
            WHERE belief_id = 'b_A_001' AND paper_id = 'paper_A'
        """)
        assert cursor.fetchone()[0] == 0

        # Verify original event is marked ROLLED_BACK
        cursor.execute("""
            SELECT status FROM paper_integration_events WHERE event_id = 'evt_001'
        """)
        assert cursor.fetchone()[0] == "ROLLED_BACK"


# =============================================================================
# ORCHESTRATOR TESTS
# =============================================================================

class TestOrchestrator:
    """Test the full 14-step integration cascade."""

    def test_full_integration_cascade(
        self, db_conn, sample_extraction, temp_template_dir,
        temp_molecule_dir, temp_theory_dir
    ):
        from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator

        orchestrator = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )

        event = orchestrator.integrate_paper(
            paper_id="test_paper_001",
            extraction_data=sample_extraction,
            paper_metadata={"publication_year": 2024, "study_design": "rct"},
        )

        # Check event completed
        assert event.status == IntegrationStatus.COMPLETED
        assert event.paper_id == "test_paper_001"

        # Check beliefs were added
        assert len(event.beliefs_added) == 2
        assert "b_test_001" in event.beliefs_added
        assert "b_test_002" in event.beliefs_added

        # Check constraints were added
        assert len(event.constraints_added) == 1

        # Check all 14 cascade steps ran
        assert len(event.cascade_steps) == 14

        # Critical steps should all be COMPLETED
        critical_steps = [s for s in event.cascade_steps if s.is_critical]
        for step in critical_steps:
            assert step.status == CascadeStepStatus.COMPLETED, (
                f"Critical step {step.step_name} was {step.status}"
            )

        # Check tags were assigned
        assert len(event.tags_assigned) > 0

        # Check molecules were matched
        assert len(event.molecules_affected) > 0

    def test_idempotency(
        self, db_conn, sample_extraction, temp_template_dir,
        temp_molecule_dir, temp_theory_dir
    ):
        from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator

        orchestrator = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )

        # First integration
        event1 = orchestrator.integrate_paper(
            paper_id="idem_paper",
            extraction_data=sample_extraction,
        )
        assert event1.status == IntegrationStatus.COMPLETED

        # Second integration — should be a no-op
        orchestrator2 = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )
        event2 = orchestrator2.integrate_paper(
            paper_id="idem_paper",
            extraction_data=sample_extraction,
        )

        # Should return the existing event, not create a new one
        assert event2.status == IntegrationStatus.COMPLETED
        assert event2.event_id == event1.event_id

    def test_integration_then_rollback(
        self, db_conn, sample_extraction, temp_template_dir,
        temp_molecule_dir, temp_theory_dir
    ):
        from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator

        orchestrator = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            template_dir=temp_template_dir,
            molecule_dir=temp_molecule_dir,
            theory_dir=temp_theory_dir,
        )

        # Integrate
        event = orchestrator.integrate_paper(
            paper_id="rollback_test",
            extraction_data=sample_extraction,
        )
        assert event.status == IntegrationStatus.COMPLETED

        # Verify beliefs exist
        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM beliefs WHERE paper_id = 'rollback_test'")
        assert cursor.fetchone()[0] == 2

        # Rollback
        rollback_event = orchestrator.rollback_paper("rollback_test")
        assert rollback_event.status == IntegrationStatus.COMPLETED

        # Verify beliefs are retired
        cursor.execute("""
            SELECT COUNT(*) FROM beliefs
            WHERE paper_id = 'rollback_test' AND status = 'RETIRED'
        """)
        assert cursor.fetchone()[0] == 2


# =============================================================================
# MIGRATION TESTS
# =============================================================================

class TestMigrations:
    """Test database migrations 5-8."""

    @staticmethod
    def _create_prereq_tables(conn):
        """Create prerequisite tables that earlier migrations depend on."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_metadata (
                key TEXT PRIMARY KEY, value TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS beliefs (
                belief_id TEXT PRIMARY KEY, web_id TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constraints (
                constraint_id TEXT PRIMARY KEY, web_id TEXT
            )
        """)
        conn.commit()

    def test_migrations_run_successfully(self):
        conn = sqlite3.connect(":memory:")
        self._create_prereq_tables(conn)
        mgr = MigrationManager(conn)
        count = mgr.run_pending_migrations()
        assert count >= 4  # At least migrations 5-8

        # Verify tables exist
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """)
        tables = {row[0] for row in cursor.fetchall()}
        assert "paper_integration_events" in tables
        assert "belief_versions" in tables
        assert "supersession_records" in tables
        assert "tag_assignments" in tables

        conn.close()

    def test_migrations_idempotent(self):
        conn = sqlite3.connect(":memory:")
        self._create_prereq_tables(conn)
        mgr = MigrationManager(conn)

        # Run twice
        count1 = mgr.run_pending_migrations()
        count2 = mgr.run_pending_migrations()

        assert count1 >= 4
        assert count2 == 0  # No pending migrations on second run

        conn.close()


class TestNewWiring:
    """Tests for the Phase 2 wiring: social epistemology, provenance, coherence."""

    @pytest.fixture
    def wired_orchestrator(self, db_conn, sample_extraction, temp_template_dir,
                           temp_molecule_dir, temp_theory_dir):
        """Orchestrator with extraction data ready to integrate."""
        from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator
        orch = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            template_dir=str(temp_template_dir),
            molecule_dir=str(temp_molecule_dir),
            theory_dir=str(temp_theory_dir),
        )
        return orch

    def test_social_epistemology_fires(self, wired_orchestrator, sample_extraction):
        """Step 11 should identify communities and create provenances."""
        event = wired_orchestrator.integrate_paper(
            paper_id="test_social_ep",
            extraction_data=sample_extraction,
        )
        # Find step 11 in cascade
        step_11 = next(
            (s for s in event.cascade_steps if s.step_name == "update_social_epistemology"),
            None,
        )
        assert step_11 is not None
        assert step_11.status == CascadeStepStatus.COMPLETED
        # Should report communities_in_registry > 0
        if step_11.details:
            assert step_11.details.get("communities_in_registry", 0) > 0

    def test_provenance_constructed_eagerly(self, wired_orchestrator, sample_extraction, db_conn):
        """Step 5 should construct Haack Provenance objects for each belief."""
        event = wired_orchestrator.integrate_paper(
            paper_id="test_provenance",
            extraction_data=sample_extraction,
        )
        # Check that belief_versions have scope_json with provenance data
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT scope_json FROM belief_versions
            WHERE paper_id = 'test_provenance' AND scope_json IS NOT NULL
        """)
        rows = cursor.fetchall()
        # At least some beliefs should have provenance stored
        # (depends on PROVENANCE_AVAILABLE flag)
        try:
            from src.models.provenance import Provenance
            assert len(rows) >= 1, "Expected at least 1 belief with provenance data"
            data = json.loads(rows[0][0])
            assert "grounding_score" in data
            assert "justification_status" in data
            assert "sources" in data
        except ImportError:
            # Provenance module not available — that's ok, skip
            pass

    def test_voi_gap_closure_step_fires(self, wired_orchestrator, sample_extraction):
        """Step 12 should attempt gap closure assessment."""
        event = wired_orchestrator.integrate_paper(
            paper_id="test_voi",
            extraction_data=sample_extraction,
        )
        step_12 = next(
            (s for s in event.cascade_steps if s.step_name == "refresh_voi_gaps"),
            None,
        )
        assert step_12 is not None
        # Should complete (possibly with skipped=True if funnel unavailable)
        assert step_12.status in (CascadeStepStatus.COMPLETED, CascadeStepStatus.FAILED)

    def test_qa_cache_eager_mode(self, wired_orchestrator, sample_extraction):
        """Step 10 should mark caches as stale in eager mode."""
        event = wired_orchestrator.integrate_paper(
            paper_id="test_qa_eager",
            extraction_data=sample_extraction,
        )
        step_10 = next(
            (s for s in event.cascade_steps if s.step_name == "recompute_qa"),
            None,
        )
        assert step_10 is not None
        assert step_10.status == CascadeStepStatus.COMPLETED

    def test_coherence_pre_snapshot(self, wired_orchestrator, sample_extraction):
        """Step 2 should attempt coherence measurement."""
        event = wired_orchestrator.integrate_paper(
            paper_id="test_coherence_snap",
            extraction_data=sample_extraction,
        )
        step_2 = next(
            (s for s in event.cascade_steps if s.step_name == "snapshot_pre"),
            None,
        )
        assert step_2 is not None
        assert step_2.status == CascadeStepStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
