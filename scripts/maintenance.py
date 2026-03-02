#!/usr/bin/env python3
"""Periodic Maintenance Script for Article Eater.

This script performs routine maintenance tasks:
- Database migrations
- Database integrity checks
- Cache cleanup
- Temporary file cleanup
- Log rotation hints

Usage:
    python scripts/maintenance.py              # Run all maintenance tasks
    python scripts/maintenance.py --check      # Check status only, no changes
    python scripts/maintenance.py --task db    # Run specific task

Tasks:
    db          - Run pending database migrations
    integrity   - Check database integrity
    cache       - Clean old cache files
    temp        - Clean temporary files
    all         - Run all tasks (default)
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_migrations import MigrationManager, check_migration_status

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)

# Configuration
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
TEMP_PATTERNS = ["*.tmp", "*.bak", "*.swp", "*~"]
CACHE_MAX_AGE_DAYS = 7

# Use centralized DB resolver
try:
    from src.services.db_locator import get_web_db
    _canonical = get_web_db()
    DB_FILES = [_canonical]
    # Also check v1 if different
    _v1 = DATA_DIR / "web_persistence.db"
    if _v1 != _canonical and _v1.exists():
        DB_FILES.append(_v1)
except Exception:
    DB_FILES = [
        DATA_DIR / "web_persistence.db",
    ]


def task_migrations(check_only: bool = False) -> dict:
    """Run or check database migrations."""
    results = {"status": "ok", "databases": []}

    for db_path in DB_FILES:
        if not db_path.exists():
            LOGGER.debug("Database not found: %s", db_path)
            continue

        status = check_migration_status(str(db_path))
        db_info = {
            "path": str(db_path.name),
            "current_version": status["current_version"],
            "pending_count": status["pending_count"],
        }

        if status["pending_count"] > 0:
            if check_only:
                LOGGER.info(
                    "%s: %d pending migrations (versions: %s)",
                    db_path.name,
                    status["pending_count"],
                    status["pending_versions"],
                )
                db_info["action"] = "pending"
            else:
                LOGGER.info("Running migrations on %s...", db_path.name)
                conn = sqlite3.connect(str(db_path))
                try:
                    mgr = MigrationManager(conn)
                    count = mgr.run_pending_migrations()
                    LOGGER.info("Applied %d migrations to %s", count, db_path.name)
                    db_info["action"] = f"applied_{count}"
                finally:
                    conn.close()
        else:
            LOGGER.debug("%s: up to date (version %d)", db_path.name, status["current_version"])
            db_info["action"] = "up_to_date"

        results["databases"].append(db_info)

    return results


def task_integrity(check_only: bool = False) -> dict:
    """Check database integrity."""
    results = {"status": "ok", "databases": []}

    for db_path in DB_FILES:
        if not db_path.exists():
            continue

        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]

            db_info = {
                "path": str(db_path.name),
                "integrity": result,
            }

            if result != "ok":
                LOGGER.warning("Integrity check failed for %s: %s", db_path.name, result)
                results["status"] = "warning"
            else:
                LOGGER.debug("%s: integrity OK", db_path.name)

            results["databases"].append(db_info)
        finally:
            conn.close()

    return results


def task_cache_cleanup(check_only: bool = False) -> dict:
    """Clean old cache files."""
    results = {"status": "ok", "files_found": 0, "files_removed": 0, "bytes_freed": 0}

    if not CACHE_DIR.exists():
        LOGGER.debug("Cache directory not found: %s", CACHE_DIR)
        return results

    cutoff = datetime.now(timezone.utc) - timedelta(days=CACHE_MAX_AGE_DAYS)

    for cache_file in CACHE_DIR.rglob("*"):
        if not cache_file.is_file():
            continue

        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            results["files_found"] += 1
            size = cache_file.stat().st_size

            if check_only:
                LOGGER.debug("Would remove: %s (age: %s)", cache_file.name, datetime.now(timezone.utc) - mtime)
            else:
                try:
                    cache_file.unlink()
                    results["files_removed"] += 1
                    results["bytes_freed"] += size
                    LOGGER.debug("Removed: %s", cache_file.name)
                except OSError as e:
                    LOGGER.warning("Failed to remove %s: %s", cache_file, e)

    if results["files_found"] > 0:
        LOGGER.info(
            "Cache cleanup: %d files found, %d removed, %.2f MB freed",
            results["files_found"],
            results["files_removed"],
            results["bytes_freed"] / (1024 * 1024),
        )

    return results


def task_temp_cleanup(check_only: bool = False) -> dict:
    """Clean temporary files."""
    results = {"status": "ok", "files_found": 0, "files_removed": 0}

    for pattern in TEMP_PATTERNS:
        for temp_file in PROJECT_ROOT.rglob(pattern):
            # Skip venv and other excluded directories
            if any(part in temp_file.parts for part in ["venv", ".venv", "node_modules", ".git"]):
                continue

            results["files_found"] += 1

            if check_only:
                LOGGER.debug("Would remove: %s", temp_file)
            else:
                try:
                    temp_file.unlink()
                    results["files_removed"] += 1
                    LOGGER.debug("Removed: %s", temp_file)
                except OSError as e:
                    LOGGER.warning("Failed to remove %s: %s", temp_file, e)

    if results["files_found"] > 0:
        LOGGER.info(
            "Temp cleanup: %d files found, %d removed",
            results["files_found"],
            results["files_removed"],
        )

    return results


def run_all_tasks(check_only: bool = False) -> dict:
    """Run all maintenance tasks."""
    results = {}

    LOGGER.info("=" * 60)
    LOGGER.info("Article Eater Maintenance %s", "CHECK" if check_only else "RUN")
    LOGGER.info("=" * 60)

    LOGGER.info("\n--- Database Migrations ---")
    results["migrations"] = task_migrations(check_only)

    LOGGER.info("\n--- Database Integrity ---")
    results["integrity"] = task_integrity(check_only)

    LOGGER.info("\n--- Cache Cleanup ---")
    results["cache"] = task_cache_cleanup(check_only)

    LOGGER.info("\n--- Temp File Cleanup ---")
    results["temp"] = task_temp_cleanup(check_only)

    LOGGER.info("\n" + "=" * 60)
    LOGGER.info("Maintenance complete")
    LOGGER.info("=" * 60)

    return results


TASKS = {
    "db": task_migrations,
    "integrity": task_integrity,
    "cache": task_cache_cleanup,
    "temp": task_temp_cleanup,
    "all": run_all_tasks,
}


def main():
    parser = argparse.ArgumentParser(
        description="Article Eater maintenance script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check status only, don't make changes",
    )
    parser.add_argument(
        "--task",
        choices=list(TASKS.keys()),
        default="all",
        help="Specific task to run (default: all)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    task_func = TASKS[args.task]
    results = task_func(check_only=args.check)

    # Exit with error if any task reported issues
    if isinstance(results, dict) and results.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
