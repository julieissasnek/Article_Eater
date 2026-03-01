"""Database Migration Tracker for Article Eater.

A lightweight migration system for SQLite databases.

Usage:
    from src.services.db_migrations import MigrationManager

    mgr = MigrationManager(conn)
    mgr.run_pending_migrations()

Adding new migrations:
    1. Add a function to MIGRATIONS dict with version number as key
    2. Function receives cursor, returns nothing (raises on error)
    3. Migrations run in version order
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Callable, Dict, Optional

LOGGER = logging.getLogger(__name__)

# Migration functions: version -> callable(cursor)
# Each migration should be idempotent where possible
MIGRATIONS: Dict[int, Callable[[sqlite3.Cursor], None]] = {}


def migration(version: int):
    """Decorator to register a migration function."""
    def decorator(func: Callable[[sqlite3.Cursor], None]):
        MIGRATIONS[version] = func
        return func
    return decorator


# =============================================================================
# MIGRATION DEFINITIONS
# =============================================================================

@migration(1)
def _m001_create_migration_table(cursor: sqlite3.Cursor) -> None:
    """Bootstrap: create the migrations tracking table itself."""
    # This is handled specially in MigrationManager.ensure_migration_table()
    pass


@migration(2)
def _m002_add_schema_version_to_metadata(cursor: sqlite3.Cursor) -> None:
    """Add schema_version column to web_metadata if missing."""
    cursor.execute("PRAGMA table_info(web_metadata)")
    columns = {row[1] for row in cursor.fetchall()}
    if "schema_version" not in columns:
        cursor.execute("ALTER TABLE web_metadata ADD COLUMN schema_version INTEGER DEFAULT 1")
        LOGGER.info("Added schema_version column to web_metadata")


@migration(3)
def _m003_add_index_beliefs_web_id(cursor: sqlite3.Cursor) -> None:
    """Add index on beliefs.web_id for faster queries."""
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_beliefs_web_id
        ON beliefs(web_id)
    """)
    LOGGER.info("Created index idx_beliefs_web_id")


@migration(4)
def _m004_add_index_constraints_web_id(cursor: sqlite3.Cursor) -> None:
    """Add index on constraints.web_id for faster queries."""
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_constraints_web_id
        ON constraints(web_id)
    """)
    LOGGER.info("Created index idx_constraints_web_id")


# =============================================================================
# SPRINT INTEGRATION-1: Paper Integration Pipeline (2026-02-25)
# =============================================================================

@migration(5)
def _m005_create_paper_integration_events(cursor: sqlite3.Cursor) -> None:
    """Create paper_integration_events table for audit trail."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_integration_events (
            event_id TEXT PRIMARY KEY,
            paper_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            pre_snapshot_id TEXT,
            post_snapshot_id TEXT,
            supersedes_paper_id TEXT,
            beliefs_added TEXT,
            beliefs_retired TEXT,
            constraints_added TEXT,
            constraints_retired TEXT,
            bn_edges_updated TEXT,
            molecules_affected TEXT,
            tags_assigned TEXT,
            cascade_log TEXT,
            supersession_records TEXT,
            error_log TEXT,
            rollback_of_event_id TEXT
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pie_paper_id
        ON paper_integration_events(paper_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pie_status
        ON paper_integration_events(status)
    """)
    LOGGER.info("Created paper_integration_events table with indices")


@migration(6)
def _m006_create_belief_versions(cursor: sqlite3.Cursor) -> None:
    """Create belief_versions table for per-belief version tracking."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS belief_versions (
            version_id TEXT PRIMARY KEY,
            belief_id TEXT NOT NULL,
            paper_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            credence_mean REAL,
            credence_se REAL,
            status TEXT,
            scope_json TEXT,
            is_current INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bv_belief_id
        ON belief_versions(belief_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bv_paper_id
        ON belief_versions(paper_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bv_is_current
        ON belief_versions(is_current)
    """)
    LOGGER.info("Created belief_versions table with indices")


@migration(7)
def _m007_create_supersession_records(cursor: sqlite3.Cursor) -> None:
    """Create supersession_records table for paper replacement tracking."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supersession_records (
            record_id TEXT PRIMARY KEY,
            superseding_paper_id TEXT NOT NULL,
            superseded_paper_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            construct_overlap REAL,
            confidence REAL,
            beliefs_superseded TEXT,
            beliefs_retained TEXT,
            timestamp TEXT NOT NULL,
            rolled_back INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sr_superseding
        ON supersession_records(superseding_paper_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sr_superseded
        ON supersession_records(superseded_paper_id)
    """)
    LOGGER.info("Created supersession_records table with indices")


@migration(8)
def _m008_create_tag_assignments(cursor: sqlite3.Cursor) -> None:
    """Create tag_assignments table for 3D taxonomy."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag_assignments (
            belief_id TEXT NOT NULL,
            tag_dimension TEXT NOT NULL,
            tag_value TEXT NOT NULL,
            paper_id TEXT NOT NULL,
            confidence REAL,
            timestamp TEXT NOT NULL,
            PRIMARY KEY (belief_id, tag_dimension, tag_value)
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ta_dimension
        ON tag_assignments(tag_dimension)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ta_paper_id
        ON tag_assignments(paper_id)
    """)
    LOGGER.info("Created tag_assignments table with indices")


# =============================================================================
# Migration 023: OVERSEER schema (from 023_paper_metadata_and_overseer.sql)
# =============================================================================

@migration(9)
def _m009_overseer_health_metrics(cursor: sqlite3.Cursor) -> None:
    """Create overseer_health_metrics, violations, quarantine, snapshots tables."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overseer_health_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            mode TEXT NOT NULL,
            trigger_paper_id TEXT,
            global_coherence REAL,
            per_theory_coherence_json TEXT,
            coherence_delta REAL,
            conflict_count INTEGER,
            conflict_rate REAL,
            new_conflicts_json TEXT,
            total_beliefs INTEGER,
            orphan_belief_count INTEGER,
            total_templates INTEGER,
            templates_with_evidence INTEGER,
            coverage_ratio REAL,
            total_qa_caches INTEGER,
            stale_qa_caches INTEGER,
            cache_freshness REAL,
            bn_edge_count INTEGER,
            bn_web_sync_violations INTEGER,
            beliefs_with_provenance INTEGER,
            beliefs_without_provenance INTEGER,
            provenance_coverage REAL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_overseer_health_ts ON overseer_health_metrics(timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_overseer_health_mode ON overseer_health_metrics(mode)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overseer_invariant_violations (
            violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            invariant_code TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            affected_belief_ids_json TEXT,
            trigger_paper_id TEXT,
            resolved BOOLEAN DEFAULT 0,
            resolved_at TEXT,
            resolution_notes TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_overseer_violations_inv ON overseer_invariant_violations(invariant_code)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overseer_quarantine (
            quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            belief_id TEXT NOT NULL,
            quarantined_at TEXT NOT NULL DEFAULT (datetime('now')),
            reason TEXT NOT NULL,
            violation_id INTEGER,
            review_deadline TEXT,
            status TEXT DEFAULT 'QUARANTINED',
            reviewed_at TEXT,
            reviewer_notes TEXT,
            original_credence REAL,
            original_status TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_overseer_quarantine_status ON overseer_quarantine(status)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS overseer_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            snapshot_type TEXT NOT NULL,
            global_coherence REAL,
            total_beliefs INTEGER,
            total_constraints INTEGER,
            total_theories INTEGER,
            metadata_json TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_overseer_snapshots_ts ON overseer_snapshots(timestamp DESC)")
    LOGGER.info("Created overseer tables: health_metrics, violations, quarantine, snapshots")


# =============================================================================
# Migration 024: CVA Persistence Tables
# =============================================================================

@migration(10)
def _m010_cva_persistence_tables(cursor: sqlite3.Cursor) -> None:
    """Create CVA persistence tables for storing computed states."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cva_constraint_states (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            subject_id TEXT,
            scene_id TEXT,
            activity_frame TEXT,
            tier1_json TEXT,
            tier2_json TEXT,
            mean_json TEXT,
            precision_json TEXT,
            entropy REAL,
            neurotype TEXT,
            culture TEXT,
            age INTEGER
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_cs_subject ON cva_constraint_states(subject_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_cs_frame ON cva_constraint_states(activity_frame)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_cs_ts ON cva_constraint_states(timestamp DESC)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cva_valuation_states (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            constraint_state_id INTEGER REFERENCES cva_constraint_states(state_id),
            subject_id TEXT,
            activity_frame TEXT,
            cultural_variant TEXT,
            core_json TEXT,
            auxiliary_json TEXT,
            precision_gains_json TEXT,
            beauty_score REAL,
            beauty_model TEXT,
            dominant_rasa TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_vs_subject ON cva_valuation_states(subject_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_vs_culture ON cva_valuation_states(cultural_variant)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cva_attractor_states (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            subject_id TEXT,
            attractor_name TEXT,
            fixed_point_json TEXT,
            is_stable INTEGER,
            kappa_loop REAL,
            max_real_eigenvalue REAL,
            basin_volume REAL,
            coupling_matrices_json TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_as_subject ON cva_attractor_states(subject_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_as_attractor ON cva_attractor_states(attractor_name)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cva_annotations (
            annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            belief_id TEXT,
            paper_id TEXT,
            measurement_modality TEXT,
            stimulus_type TEXT,
            molecule_link TEXT,
            constraint_tags_json TEXT,
            valuation_tags_json TEXT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_ann_belief ON cva_annotations(belief_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cva_ann_modality ON cva_annotations(measurement_modality)")

    LOGGER.info("Created CVA persistence tables: constraint_states, valuation_states, attractor_states, annotations")


# =============================================================================
# MIGRATION MANAGER
# =============================================================================

class MigrationManager:
    """Manages database schema migrations."""

    MIGRATION_TABLE = "_schema_migrations"

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cursor = conn.cursor()

    def ensure_migration_table(self) -> None:
        """Create the migrations tracking table if it doesn't exist."""
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.MIGRATION_TABLE} (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                checksum TEXT
            )
        """)
        self.conn.commit()

    def get_applied_versions(self) -> set[int]:
        """Get set of already-applied migration versions."""
        self.ensure_migration_table()
        self.cursor.execute(f"SELECT version FROM {self.MIGRATION_TABLE}")
        return {row[0] for row in self.cursor.fetchall()}

    def get_current_version(self) -> int:
        """Get the highest applied migration version."""
        applied = self.get_applied_versions()
        return max(applied) if applied else 0

    def get_pending_migrations(self) -> list[int]:
        """Get list of migrations that haven't been applied yet."""
        applied = self.get_applied_versions()
        all_versions = set(MIGRATIONS.keys())
        pending = sorted(all_versions - applied)
        return pending

    def run_migration(self, version: int) -> None:
        """Run a single migration."""
        if version not in MIGRATIONS:
            raise ValueError(f"Unknown migration version: {version}")

        func = MIGRATIONS[version]
        name = func.__name__

        LOGGER.info("Running migration %d: %s", version, name)

        try:
            func(self.cursor)

            # Record the migration
            self.cursor.execute(f"""
                INSERT INTO {self.MIGRATION_TABLE} (version, name, applied_at)
                VALUES (?, ?, ?)
            """, (version, name, datetime.now(timezone.utc).isoformat()))

            self.conn.commit()
            LOGGER.info("Migration %d completed successfully", version)

        except Exception as exc:
            self.conn.rollback()
            LOGGER.error("Migration %d failed: %s", version, exc)
            raise

    def run_pending_migrations(self) -> int:
        """Run all pending migrations in order. Returns count of migrations run."""
        self.ensure_migration_table()
        pending = self.get_pending_migrations()

        if not pending:
            LOGGER.debug("No pending migrations")
            return 0

        LOGGER.info("Running %d pending migrations", len(pending))

        for version in pending:
            self.run_migration(version)

        return len(pending)

    def get_migration_history(self) -> list[dict]:
        """Get history of applied migrations."""
        self.ensure_migration_table()
        self.cursor.execute(f"""
            SELECT version, name, applied_at
            FROM {self.MIGRATION_TABLE}
            ORDER BY version
        """)
        return [
            {"version": row[0], "name": row[1], "applied_at": row[2]}
            for row in self.cursor.fetchall()
        ]

    def status(self) -> dict:
        """Get migration status summary."""
        return {
            "current_version": self.get_current_version(),
            "pending_count": len(self.get_pending_migrations()),
            "pending_versions": self.get_pending_migrations(),
            "total_migrations": len(MIGRATIONS),
        }


def run_migrations_on_db(db_path: str) -> int:
    """Convenience function to run migrations on a database file."""
    conn = sqlite3.connect(db_path)
    try:
        mgr = MigrationManager(conn)
        return mgr.run_pending_migrations()
    finally:
        conn.close()


def check_migration_status(db_path: str) -> dict:
    """Check migration status without running anything."""
    conn = sqlite3.connect(db_path)
    try:
        mgr = MigrationManager(conn)
        return mgr.status()
    finally:
        conn.close()
