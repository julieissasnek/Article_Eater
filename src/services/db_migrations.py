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
