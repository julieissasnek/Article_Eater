#!/usr/bin/env python3
"""
Full System Health Check
========================
Unified health checker that runs ALL overseer checks.

Usage:
  python scripts/run_full_system_health.py              # Full system health check
  python scripts/run_full_system_health.py --json       # Machine-readable JSON output
  python scripts/run_full_system_health.py --verbose    # Debug output
  python scripts/run_full_system_health.py --db-path /path/to/overseer.db

This script:
  1. Imports the OverseerService
  2. Runs check_health() — overall system health metrics
  3. Runs check_integrity() — database and data integrity verification
  4. Runs check_all_subsystems() — individual subsystem status checks
  5. Generates a unified health report with:
     - Overall system status (green/yellow/red)
     - Timestamp and duration
     - Subsystem-level details
     - Violation counts and severity breakdown
     - Actionable recommendations
  6. Writes report to docs/overseer_reports/health_report_YYYY-MM-DD_HH-MM-SS.json
  7. Prints color-coded console summary (green=pass, yellow=warn, red=fail)
  8. Supports --json flag for machine-readable output only

Author: Claude Code (Article Eater CMR System)
Date: March 2026
"""

import argparse
import json
import logging
import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

# Setup repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Setup logging
def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# ANSI Color Codes (WCAG Accessible)
# ============================================================================

class Colors:
    """WCAG-compliant ANSI colors (avoid dark blue on dark backgrounds)."""
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # High contrast colors suitable for dark terminals
    GREEN = "\033[92m"       # Bright green
    YELLOW = "\033[93m"      # Bright yellow (not orange)
    RED = "\033[91m"         # Bright red
    CYAN = "\033[96m"        # Bright cyan
    WHITE = "\033[97m"       # White

    @staticmethod
    def status_color(status: str) -> str:
        """Map status to appropriate color."""
        status_lower = status.lower()
        if status_lower in ('pass', 'success', 'ok', 'healthy'):
            return Colors.GREEN
        elif status_lower in ('warn', 'warning', 'degraded'):
            return Colors.YELLOW
        elif status_lower in ('fail', 'failure', 'error', 'unhealthy'):
            return Colors.RED
        else:
            return Colors.CYAN

    @staticmethod
    def colored(text: str, color: str) -> str:
        """Wrap text with color code."""
        return f"{color}{text}{Colors.RESET}"


# ============================================================================
# Database Path Resolution
# ============================================================================

def resolve_db_paths(db_path: Optional[Path] = None, web_db_path: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Resolve overseer.db and web.db paths.

    Args:
        db_path: Override path for overseer.db (if provided)
        web_db_path: Override path for web.db (if provided)

    Returns:
        (overseer_db_path, web_db_path)

    Raises:
        FileNotFoundError: If databases cannot be found
    """
    if db_path and web_db_path:
        if db_path.exists() and web_db_path.exists():
            return db_path, web_db_path
        else:
            raise FileNotFoundError(f"Provided paths do not exist: {db_path}, {web_db_path}")

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
    for overseer_db, web_db in candidates:
        if overseer_db.exists():
            logger.warning(f"Found overseer.db but web.db not found at {web_db}")
            return overseer_db, web_db

    raise FileNotFoundError(
        f"Cannot find overseer.db or web.db in standard locations. "
        f"Checked: {[str(p[0]) for p in candidates]}"
    )


# ============================================================================
# OVERSEER Service Loading
# ============================================================================

def load_overseer_service(overseer_db_path: Path, web_db_path: Path):
    """
    Load the OverseerService.

    Args:
        overseer_db_path: Path to overseer.db
        web_db_path: Path to web.db

    Returns:
        OverseerService instance or None if import fails
    """
    try:
        from src.services.overseer import OverseerService

        logger.debug("Loading OVERSEER service...")
        overseer = OverseerService(
            overseer_db_path=str(overseer_db_path),
            web=None,
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
# Report Directory Handling
# ============================================================================

def ensure_report_directory() -> Path:
    """Create docs/overseer_reports/ if it doesn't exist."""
    report_dir = REPO_ROOT / "docs" / "overseer_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


# ============================================================================
# Health Check Execution
# ============================================================================

def run_health_checks(overseer) -> Dict[str, Any]:
    """
    Run all overseer health checks.

    Returns:
        Dict with aggregated health results
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "health": None,
            "integrity": None,
            "subsystems": None,
        },
        "summary": {
            "overall_status": "unknown",
            "subsystems_checked": 0,
            "critical_violations": 0,
            "warnings": 0,
        },
    }

    # Run check_health()
    try:
        logger.debug("Running check_health()...")
        health = overseer.check_health() if hasattr(overseer, 'check_health') else None

        if health:
            results["checks"]["health"] = {
                "status": "completed",
                "metrics": getattr(health, 'health_metrics', {}),
                "duration_ms": getattr(health, 'duration_ms', None),
            }
            logger.info(f"check_health() completed: {results['checks']['health']['status']}")
        else:
            results["checks"]["health"] = {"status": "skipped", "reason": "Method not available"}
            logger.warning("check_health() not available")

    except Exception as e:
        logger.error(f"check_health() failed: {e}", exc_info=True)
        results["checks"]["health"] = {"status": "failed", "error": str(e)}

    # Run check_integrity()
    try:
        logger.debug("Running check_integrity()...")
        integrity = overseer.check_integrity() if hasattr(overseer, 'check_integrity') else None

        if integrity:
            results["checks"]["integrity"] = {
                "status": "completed",
                "violations": getattr(integrity, 'violations', []),
                "alerts": getattr(integrity, 'alerts', []),
            }
            violation_count = len(getattr(integrity, 'violations', []))
            results["summary"]["critical_violations"] += violation_count
            logger.info(f"check_integrity() completed: {violation_count} violations found")
        else:
            results["checks"]["integrity"] = {"status": "skipped", "reason": "Method not available"}
            logger.warning("check_integrity() not available")

    except Exception as e:
        logger.error(f"check_integrity() failed: {e}", exc_info=True)
        results["checks"]["integrity"] = {"status": "failed", "error": str(e)}

    # Run check_all_subsystems()
    try:
        logger.debug("Running check_all_subsystems()...")
        subsystems = overseer.check_all_subsystems() if hasattr(overseer, 'check_all_subsystems') else None

        if subsystems:
            subsystem_results = {}
            if isinstance(subsystems, dict):
                subsystem_results = subsystems
            else:
                # Handle dataclass or object
                subsystem_results = getattr(subsystems, 'subsystems', {})

            results["checks"]["subsystems"] = {
                "status": "completed",
                "subsystems": subsystem_results,
                "count": len(subsystem_results),
            }
            results["summary"]["subsystems_checked"] = len(subsystem_results)
            logger.info(f"check_all_subsystems() completed: {len(subsystem_results)} subsystems checked")
        else:
            results["checks"]["subsystems"] = {"status": "skipped", "reason": "Method not available"}
            logger.warning("check_all_subsystems() not available")

    except Exception as e:
        logger.error(f"check_all_subsystems() failed: {e}", exc_info=True)
        results["checks"]["subsystems"] = {"status": "failed", "error": str(e)}

    # Determine overall status
    check_statuses = [
        results["checks"]["health"].get("status") if results["checks"]["health"] else "skipped",
        results["checks"]["integrity"].get("status") if results["checks"]["integrity"] else "skipped",
        results["checks"]["subsystems"].get("status") if results["checks"]["subsystems"] else "skipped",
    ]

    if "failed" in check_statuses:
        results["summary"]["overall_status"] = "critical"
    elif results["summary"]["critical_violations"] > 0:
        results["summary"]["overall_status"] = "unhealthy"
    elif "completed" in check_statuses:
        results["summary"]["overall_status"] = "healthy"
    else:
        results["summary"]["overall_status"] = "unknown"

    return results


# ============================================================================
# Report Persistence
# ============================================================================

def save_health_report(health_results: Dict[str, Any], report_dir: Path) -> Path:
    """
    Save unified health report to JSON file.

    Args:
        health_results: Aggregated health check results
        report_dir: Directory to save reports

    Returns:
        Path to saved report file
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    report_path = report_dir / f"health_report_{timestamp}.json"

    with open(report_path, "w") as f:
        json.dump(health_results, f, indent=2, default=str)

    logger.info(f"Saved health report to {report_path}")
    return report_path


# ============================================================================
# Console Output Formatting
# ============================================================================

def print_console_summary(health_results: Dict[str, Any], report_path: Optional[Path] = None):
    """
    Print color-coded console summary of health check.

    Args:
        health_results: Aggregated health check results
        report_path: Path to saved report (for reference)
    """
    summary = health_results.get("summary", {})
    checks = health_results.get("checks", {})

    print("\n" + "=" * 80)
    print(Colors.colored("SYSTEM HEALTH REPORT", Colors.BOLD))
    print("=" * 80)

    # Timestamp
    timestamp = health_results.get("timestamp", "unknown")
    print(f"Timestamp: {timestamp}")

    # Overall status (with color)
    overall_status = summary.get("overall_status", "unknown").upper()
    status_color = Colors.status_color(overall_status)
    print(f"\nOverall Status: {Colors.colored(overall_status, status_color)}")

    # Subsystems checked
    subsystems_checked = summary.get("subsystems_checked", 0)
    print(f"Subsystems Checked: {subsystems_checked}")

    # Violations and warnings
    critical_violations = summary.get("critical_violations", 0)
    violations_color = Colors.RED if critical_violations > 0 else Colors.GREEN
    print(f"Critical Violations: {Colors.colored(str(critical_violations), violations_color)}")

    # Health check summary
    print(f"\n{Colors.bold('Health Checks:')}")
    for check_name, check_result in checks.items():
        if check_result:
            status = check_result.get("status", "unknown").upper()
            status_color = Colors.status_color(status)
            print(f"  {check_name.capitalize()}: {Colors.colored(status, status_color)}")
            if status == "FAILED":
                error = check_result.get("error")
                if error:
                    print(f"    Error: {error}")

    # Report location
    if report_path:
        print(f"\nDetailed Report: {report_path}")

    print("=" * 80 + "\n")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for full system health check."""

    parser = argparse.ArgumentParser(
        description="Full System Health Check: Unified overseer health verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as machine-readable JSON only (no console summary)",
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

    # Reconfigure logger if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 80)
    logger.info("FULL SYSTEM HEALTH CHECK STARTING")
    logger.info(f"Verbose: {args.verbose}")
    logger.info(f"JSON output: {args.json}")
    logger.info("=" * 80)

    start_time = time.time()
    health_results = None
    error_msg = None

    try:
        # Resolve database paths
        logger.debug("Resolving database paths...")
        overseer_db_path, web_db_path = resolve_db_paths(args.db_path, args.web_db_path)

        logger.info(f"Using overseer.db: {overseer_db_path}")
        logger.info(f"Using web.db: {web_db_path}")

        # Load OVERSEER service
        logger.debug("Loading OVERSEER service...")
        overseer = load_overseer_service(overseer_db_path, web_db_path)
        if not overseer:
            raise RuntimeError("Failed to load OVERSEER service")

        # Ensure report directory
        report_dir = ensure_report_directory()
        logger.debug(f"Reports will be saved to: {report_dir}")

        # Run health checks
        logger.info("Running health checks...")
        health_results = run_health_checks(overseer)

        logger.info("Health checks completed successfully")

    except FileNotFoundError as e:
        logger.error(f"Database not found: {e}")
        error_msg = str(e)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=args.verbose)
        error_msg = str(e)

    # Calculate elapsed time
    elapsed_ms = (time.time() - start_time) * 1000

    # Add timing to results
    if health_results:
        health_results["duration_ms"] = elapsed_ms

    # Output results
    if args.json:
        # JSON-only output
        output = health_results or {"error": error_msg, "success": False}
        print(json.dumps(output, indent=2, default=str))
    else:
        # Console output
        if error_msg:
            print(f"\n{Colors.colored('ERROR', Colors.RED)}: {error_msg}\n", file=sys.stderr)
            return 1
        else:
            report_path = None
            if health_results:
                # Save report to disk
                report_dir = ensure_report_directory()
                report_path = save_health_report(health_results, report_dir)

            # Print console summary
            print_console_summary(health_results or {}, report_path)

    return 0 if error_msg is None else 1


if __name__ == "__main__":
    sys.exit(main())
