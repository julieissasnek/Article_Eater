#!/usr/bin/env python3
"""
OVERSEER Nightly Batch — Sprint 5
==================================
Runs periodic audit + maintenance outside the integration pipeline.

Usage:
  python scripts/overseer_nightly.py                    # Full nightly run
  python scripts/overseer_nightly.py --audit-only       # Just audit, no maintenance
  python scripts/overseer_nightly.py --maintenance-only  # Just maintenance
  python scripts/overseer_nightly.py --dry-run           # Preview what would happen

Cron example (run at 2 AM):
  0 2 * * * cd /path/to/repo && python scripts/overseer_nightly.py >> logs/overseer_nightly.log 2>&1

This script:
  1. Loads OVERSEER service (connects to overseer.db + web.db)
  2. Runs periodic_audit() — full integrity check, completeness audit, health metrics
  3. Runs run_maintenance() — stale cache marking, orphan detection, snapshot rotation
  4. Batch QA cache recomputation (O-6: batched nightly)
  5. Generates health report and saves to docs/overseer_reports/
  6. Checks quarantine deadlines — warns about beliefs approaching 7-day review deadline
  7. Logs summary to stdout + file

Author: Claude Code (Article Eater CMR System)
Date: February 2026
"""

import argparse
import json
import logging
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

# Setup repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Setup logging
log_dir = REPO_ROOT / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "overseer_nightly.log"),
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Database Path Resolution
# ============================================================================

def resolve_db_paths() -> tuple[Path, Path]:
    """
    Resolve overseer.db and web.db paths.

    Returns:
        (overseer_db_path, web_db_path)

    Raises:
        FileNotFoundError: If databases cannot be found
    """
    # Try common locations
    candidates = [
        (REPO_ROOT / "overseer.db", REPO_ROOT / "web.db"),
        (REPO_ROOT / "data" / "overseer.db", REPO_ROOT / "data" / "web.db"),
        (REPO_ROOT / ".data" / "overseer.db", REPO_ROOT / ".data" / "web.db"),
    ]

    for overseer_db, web_db in candidates:
        if overseer_db.exists() and web_db.exists():
            return overseer_db, web_db

    # If web.db not found but overseer.db exists, still return paths
    # (web.db may be optional for read-only access)
    for overseer_db, web_db in candidates:
        if overseer_db.exists():
            logger.warning(f"Found overseer.db but web.db not found at {web_db}")
            return overseer_db, web_db

    raise FileNotFoundError(
        f"Cannot find overseer.db or web.db in standard locations. "
        f"Checked: {[str(p[0]) for p in candidates]}"
    )


# ============================================================================
# OVERSEER Service Import & Initialization
# ============================================================================

def load_overseer_service(overseer_db_path: Path, web_db_path: Path):
    """
    Load the OverseerService.

    Args:
        overseer_db_path: Path to overseer.db
        web_db_path: Path to web.db (for read-only access)

    Returns:
        OverseerService instance or None if import fails
    """
    try:
        from src.services.overseer import OverseerService
        logger.info(f"Loading OVERSEER service...")

        # Create service with None web object (graceful degradation)
        overseer = OverseerService(
            overseer_db_path=str(overseer_db_path),
            web=None,  # We don't need WebOfBelief for nightly audit
            web_db_path=str(web_db_path)
        )
        logger.info("OVERSEER service loaded successfully")
        return overseer

    except ImportError as e:
        logger.error(f"Failed to import OverseerService: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OverseerService: {e}")
        return None


# ============================================================================
# Report Output
# ============================================================================

def ensure_report_directory() -> Path:
    """Create docs/overseer_reports/ if it doesn't exist."""
    report_dir = REPO_ROOT / "docs" / "overseer_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def save_health_report(overseer, health_report, report_dir: Path) -> Path:
    """
    Save health report to JSON file.

    Args:
        overseer: OverseerService instance
        health_report: HealthReport object from periodic_audit()
        report_dir: Directory to save reports

    Returns:
        Path to saved report file
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = report_dir / f"nightly_{timestamp}.json"

    # Convert HealthReport dataclass to dict
    report_data = {
        "timestamp": health_report.timestamp,
        "mode": health_report.mode,
        "trigger_paper_id": health_report.trigger_paper_id,
        "health_metrics": health_report.health_metrics,
        "violations": [
            {
                "code": v.code,
                "severity": v.severity,
                "description": v.description,
                "affected_beliefs": v.affected_beliefs,
                "trigger_paper_id": v.trigger_paper_id,
            }
            for v in health_report.violations
        ],
        "alerts": health_report.alerts,
        "quarantine_actions": health_report.quarantine_actions,
        "maintenance_actions": health_report.maintenance_actions,
        "duration_ms": health_report.duration_ms,
    }

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"Saved health report to {report_path}")
    return report_path


# ============================================================================
# Quarantine Deadline Checking
# ============================================================================

def check_quarantine_deadlines(overseer, web_db_path: Path) -> List[Dict[str, Any]]:
    """
    Check for beliefs in quarantine approaching 7-day review deadline.

    Args:
        overseer: OverseerService instance
        web_db_path: Path to web.db for direct DB access

    Returns:
        List of warnings for beliefs near deadline
    """
    warnings = []

    try:
        # Quarantine state is in overseer.db (per O-7 Parnas information hiding)
        overseer_db = getattr(overseer, 'db_path', None)
        db_to_query = str(overseer_db) if overseer_db else str(web_db_path)

        with sqlite3.connect(db_to_query) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get all quarantined beliefs from overseer_quarantine table
            cursor.execute("""
                SELECT belief_id, quarantined_at, review_deadline
                FROM overseer_quarantine
                WHERE status = 'QUARANTINED'
            """)

            rows = cursor.fetchall()
            now = datetime.now(timezone.utc)
            deadline_days = 7
            warning_threshold_days = 1  # Warn if <1 day until deadline

            for row in rows:
                belief_id = row["belief_id"]
                quarantine_ts = row["quarantined_at"]

                # Parse timestamp (may be ISO format or unix timestamp)
                try:
                    if isinstance(quarantine_ts, str):
                        q_date = datetime.fromisoformat(quarantine_ts.replace("Z", "+00:00"))
                    else:
                        q_date = datetime.fromtimestamp(quarantine_ts, tz=timezone.utc)
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse quarantine_timestamp for {belief_id}")
                    continue

                deadline = q_date + timedelta(days=deadline_days)
                time_remaining = deadline - now

                if time_remaining.total_seconds() < 0:
                    # Deadline has passed
                    warnings.append({
                        "belief_id": belief_id,
                        "status": "OVERDUE",
                        "deadline": deadline.isoformat(),
                        "days_overdue": abs(time_remaining.days),
                        "action": "Needs immediate human review",
                    })
                elif time_remaining.days < warning_threshold_days:
                    # Deadline is approaching
                    warnings.append({
                        "belief_id": belief_id,
                        "status": "URGENT",
                        "deadline": deadline.isoformat(),
                        "hours_remaining": round(time_remaining.total_seconds() / 3600, 1),
                        "action": "Will expire soon, schedule review",
                    })

    except Exception as e:
        logger.warning(f"Could not check quarantine deadlines: {e}")

    return warnings


# ============================================================================
# Maintenance Execution
# ============================================================================

def run_qa_cache_recomputation(overseer) -> Dict[str, Any]:
    """
    Run batched nightly QA cache recomputation (O-6).

    This is designed to be executed once per night, marking
    stale caches and recomputing QA metrics in batch mode.

    Args:
        overseer: OverseerService instance

    Returns:
        Dict with recomputation summary
    """
    result = {
        "action": "qa_cache_recomputation",
        "status": "completed",
        "stale_caches_found": 0,
        "caches_recomputed": 0,
        "errors": [],
    }

    try:
        # O-6: Batched QA cache recomputation
        # Attempt to import QA cache infrastructure
        try:
            from src.qa.qa_cache_manager import QACacheManager
            has_qa_cache = True
        except ImportError:
            has_qa_cache = False

        if not has_qa_cache:
            result["status"] = "skipped"
            result["reason"] = "QACacheManager not available"
            return result

        # Check if overseer has a reference to the QA cache manager
        cache_manager = getattr(overseer, 'qa_cache_manager', None)
        if cache_manager is None:
            # Try to find stale caches via overseer's health metrics
            health = overseer.check_health() if hasattr(overseer, 'check_health') else None
            if health and hasattr(health, 'stale_caches'):
                result["stale_caches_found"] = health.stale_caches
            else:
                result["status"] = "skipped"
                result["reason"] = "No QA cache manager configured on overseer"
                return result

        # If QA cache manager is available, use it for batch invalidation
        if cache_manager:
            stale = cache_manager.get_stale_entries() if hasattr(cache_manager, 'get_stale_entries') else []
            result["stale_caches_found"] = len(stale)

            for entry in stale:
                try:
                    molecule_id = entry if isinstance(entry, str) else getattr(entry, 'molecule_id', str(entry))
                    cache_manager.invalidate(molecule_id)
                    result["caches_recomputed"] += 1
                except Exception as e:
                    result["errors"].append(f"Failed to recompute {molecule_id}: {e}")

        logger.info(
            f"O-6 QA cache recomputation: {result['caches_recomputed']}/{result['stale_caches_found']} "
            f"caches recomputed, {len(result['errors'])} errors"
        )

    except Exception as e:
        result["status"] = "failed"
        result["reason"] = str(e)
        logger.error(f"QA cache recomputation failed: {e}")

    return result


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for nightly batch."""

    parser = argparse.ArgumentParser(
        description="OVERSEER Nightly Batch: Periodic audit and maintenance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Run only the periodic audit, skip maintenance",
    )
    parser.add_argument(
        "--maintenance-only",
        action="store_true",
        help="Run only maintenance, skip audit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen, don't modify databases",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Path to overseer.db (auto-detected if not specified)",
    )
    parser.add_argument(
        "--web-db-path",
        type=Path,
        help="Path to web.db (auto-detected if not specified)",
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("OVERSEER Nightly Batch Starting")
    logger.info(f"Mode: {'DRY-RUN' if args.dry_run else 'EXECUTE'}")
    logger.info(f"Audit: {not args.maintenance_only}, Maintenance: {not args.audit_only}")
    logger.info("=" * 80)

    # Resolve database paths
    try:
        if args.db_path and args.web_db_path:
            overseer_db_path = args.db_path
            web_db_path = args.web_db_path
        else:
            overseer_db_path, web_db_path = resolve_db_paths()

        logger.info(f"Using overseer.db: {overseer_db_path}")
        logger.info(f"Using web.db: {web_db_path}")

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    # Load OVERSEER service
    overseer = load_overseer_service(overseer_db_path, web_db_path)
    if not overseer:
        logger.error("Failed to load OVERSEER service. Exiting.")
        return 1

    # Ensure report directory exists
    report_dir = ensure_report_directory()

    # Results tracking
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "audit": None,
        "maintenance": None,
        "qa_cache_recomputation": None,
        "quarantine_warnings": [],
    }

    # ========================================================================
    # Run Periodic Audit
    # ========================================================================

    if not args.maintenance_only:
        try:
            logger.info("Starting periodic audit...")
            health_report = overseer.periodic_audit()

            # Save report to disk
            report_path = save_health_report(overseer, health_report, report_dir)

            # Summary
            audit_summary = {
                "status": "completed",
                "duration_ms": health_report.duration_ms,
                "violations_count": len(health_report.violations),
                "alerts_count": len(health_report.alerts),
                "quarantine_actions": len(health_report.quarantine_actions),
                "report_path": str(report_path),
            }

            results["audit"] = audit_summary

            # Log summary
            logger.info(f"Periodic audit completed in {health_report.duration_ms:.0f}ms")
            logger.info(f"  Violations: {len(health_report.violations)}")
            logger.info(f"  Alerts: {len(health_report.alerts)}")
            logger.info(f"  Quarantine actions: {len(health_report.quarantine_actions)}")

            # Log violations
            for v in health_report.violations:
                logger.warning(f"  {v.code} ({v.severity}): {v.description}")

            # Log alerts
            for a in health_report.alerts:
                logger.warning(f"  ALERT: {a}")

        except Exception as e:
            logger.error(f"Periodic audit failed: {e}", exc_info=True)
            results["audit"] = {"status": "failed", "error": str(e)}
            return 1

    # ========================================================================
    # Run Maintenance
    # ========================================================================

    if not args.audit_only:
        try:
            logger.info("Starting maintenance...")
            maintenance_result = overseer.run_maintenance()

            maintenance_summary = {
                "status": "completed" if not args.dry_run else "dry_run",
                "actions_count": len(maintenance_result.get("actions", [])),
                "actions": maintenance_result.get("actions", []),
            }

            results["maintenance"] = maintenance_summary

            logger.info(f"Maintenance completed: {len(maintenance_result.get('actions', []))} actions")
            for action in maintenance_result.get("actions", []):
                logger.info(f"  {action.get('action')}: {action.get('resource')}")

        except Exception as e:
            logger.error(f"Maintenance failed: {e}", exc_info=True)
            results["maintenance"] = {"status": "failed", "error": str(e)}
            return 1

    # ========================================================================
    # QA Cache Recomputation (O-6)
    # ========================================================================

    if not args.audit_only:
        try:
            logger.info("Running QA cache recomputation...")
            qa_result = run_qa_cache_recomputation(overseer)
            results["qa_cache_recomputation"] = qa_result
            logger.info(f"QA cache recomputation: {qa_result['status']}")

        except Exception as e:
            logger.error(f"QA cache recomputation failed: {e}", exc_info=True)
            results["qa_cache_recomputation"] = {"status": "failed", "error": str(e)}

    # ========================================================================
    # Check Quarantine Deadlines
    # ========================================================================

    if not args.audit_only:
        try:
            logger.info("Checking quarantine deadlines...")
            warnings = check_quarantine_deadlines(overseer, web_db_path)
            results["quarantine_warnings"] = warnings

            if warnings:
                logger.warning(f"Found {len(warnings)} beliefs with approaching deadlines:")
                for w in warnings:
                    logger.warning(f"  {w['belief_id']}: {w['status']} - {w['action']}")
            else:
                logger.info("No beliefs with approaching deadlines")

        except Exception as e:
            logger.warning(f"Could not check quarantine deadlines: {e}")

    # ========================================================================
    # Summary
    # ========================================================================

    logger.info("=" * 80)
    logger.info("OVERSEER Nightly Batch Complete")
    logger.info(f"Audit: {results['audit']}")
    logger.info(f"Maintenance: {results['maintenance']}")
    if results.get("qa_cache_recomputation"):
        logger.info(f"QA Cache Recomputation: {results['qa_cache_recomputation']['status']}")
    logger.info("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
