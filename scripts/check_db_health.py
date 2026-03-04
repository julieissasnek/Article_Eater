#!/usr/bin/env python3
"""
Database Health Check with Success Conditions
==============================================

Proactive health checks for ATLAS database infrastructure.
Run this script to verify DB integrity before other operations.

Usage:
    python3 scripts/check_db_health.py           # Run all checks
    python3 scripts/check_db_health.py --quick   # Essential checks only
    python3 scripts/check_db_health.py --json    # Output as JSON for overseer

Success Conditions (SC-DB-*):
    SC-DB-1: db_locator returns existing file
    SC-DB-2: beliefs table exists in canonical DB
    SC-DB-3: beliefs table has >0 rows
    SC-DB-4: Required columns exist in beliefs table
    SC-DB-5: No shadowing DBs (root ae.db vs data/)
    SC-DB-6: Overseer uses same DB as db_locator
    SC-DB-7: template_ids coverage >= threshold
    SC-DB-8: Migration 023 applied to overseer.db
    SC-DB-9: Foreign key integrity (beliefs.web_id)
    SC-DB-10: Theory orphan rate below threshold

Created: 2026-03-04
Author: Claude (fixing DB path confusion issues)
Integration: Wire into overseer nightly pipeline
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    sc_id: str
    name: str
    passed: bool
    message: str
    details: dict = field(default_factory=dict)
    severity: str = "ERROR"  # ERROR, WARNING, INFO


@dataclass
class DBHealthReport:
    """Complete health report."""
    timestamp: str
    canonical_db: Optional[str]
    total_checks: int
    passed: int
    failed: int
    warnings: int
    results: list[HealthCheckResult] = field(default_factory=list)
    overall_healthy: bool = False

    def add(self, result: HealthCheckResult):
        self.results.append(result)
        self.total_checks += 1
        if result.passed:
            self.passed += 1
        elif result.severity == "WARNING":
            self.warnings += 1
        else:
            self.failed += 1

    def finalize(self):
        self.overall_healthy = self.failed == 0


def get_canonical_db() -> tuple[Optional[Path], Optional[str]]:
    """Get canonical DB path via db_locator."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from src.services.db_locator import get_web_db
        path = Path(get_web_db())
        return path, None
    except Exception as e:
        return None, str(e)


def check_sc_db_1(report: DBHealthReport) -> Optional[Path]:
    """SC-DB-1: db_locator returns existing file."""
    db_path, error = get_canonical_db()

    if error:
        report.add(HealthCheckResult(
            sc_id="SC-DB-1",
            name="db_locator returns existing file",
            passed=False,
            message=f"db_locator failed: {error}",
            severity="ERROR"
        ))
        return None

    if not db_path or not db_path.exists():
        report.add(HealthCheckResult(
            sc_id="SC-DB-1",
            name="db_locator returns existing file",
            passed=False,
            message=f"DB path does not exist: {db_path}",
            severity="ERROR"
        ))
        return None

    report.add(HealthCheckResult(
        sc_id="SC-DB-1",
        name="db_locator returns existing file",
        passed=True,
        message=f"Canonical DB: {db_path}",
        details={"path": str(db_path), "size_mb": db_path.stat().st_size / (1024*1024)}
    ))
    return db_path


def check_sc_db_2(report: DBHealthReport, db_path: Path):
    """SC-DB-2: beliefs table exists in canonical DB."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}

            if 'beliefs' in tables:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-2",
                    name="beliefs table exists",
                    passed=True,
                    message="beliefs table found",
                    details={"all_belief_tables": [t for t in tables if 'belief' in t.lower()]}
                ))
            elif 'belief_versions' in tables:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-2",
                    name="beliefs table exists",
                    passed=False,
                    message="beliefs table missing, only belief_versions exists",
                    details={"available": "belief_versions"},
                    severity="ERROR"
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-2",
                    name="beliefs table exists",
                    passed=False,
                    message="No belief tables found",
                    details={"all_tables": sorted(tables)},
                    severity="ERROR"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-2",
            name="beliefs table exists",
            passed=False,
            message=f"DB query failed: {e}",
            severity="ERROR"
        ))


def check_sc_db_3(report: DBHealthReport, db_path: Path):
    """SC-DB-3: beliefs table has >0 rows."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]

            if count > 0:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-3",
                    name="beliefs table has data",
                    passed=True,
                    message=f"{count:,} beliefs found",
                    details={"count": count}
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-3",
                    name="beliefs table has data",
                    passed=False,
                    message="beliefs table is EMPTY (0 rows)",
                    details={"count": 0},
                    severity="ERROR"
                ))
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            report.add(HealthCheckResult(
                sc_id="SC-DB-3",
                name="beliefs table has data",
                passed=False,
                message="beliefs table does not exist",
                severity="ERROR"
            ))
        else:
            raise


def check_sc_db_4(report: DBHealthReport, db_path: Path):
    """SC-DB-4: Required columns exist in beliefs table."""
    required_columns = {
        'belief_id', 'content', 'web_id', 'level', 'status',
        'credence_value', 'theory_id', 'created_at', 'updated_at'
    }
    recommended_columns = {'template_ids', 'environment_id', 'outcome_id', 'epistemic_v2'}

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("PRAGMA table_info(beliefs)")
            actual_columns = {row[1] for row in cursor.fetchall()}

            missing_required = required_columns - actual_columns
            missing_recommended = recommended_columns - actual_columns

            if missing_required:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-4",
                    name="Required columns exist",
                    passed=False,
                    message=f"Missing required columns: {missing_required}",
                    details={"missing": list(missing_required), "actual": sorted(actual_columns)},
                    severity="ERROR"
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-4",
                    name="Required columns exist",
                    passed=True,
                    message=f"All {len(required_columns)} required columns present",
                    details={
                        "required": sorted(required_columns),
                        "missing_recommended": list(missing_recommended) if missing_recommended else []
                    }
                ))

            if missing_recommended:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-4b",
                    name="Recommended columns exist",
                    passed=False,
                    message=f"Missing recommended columns: {missing_recommended}",
                    details={"missing": list(missing_recommended)},
                    severity="WARNING"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-4",
            name="Required columns exist",
            passed=False,
            message=f"Schema check failed: {e}",
            severity="ERROR"
        ))


def check_sc_db_5(report: DBHealthReport, canonical_path: Path):
    """SC-DB-5: No shadowing DBs (root ae.db with data vs canonical)."""
    shadow_candidates = [
        PROJECT_ROOT / "ae.db",
        PROJECT_ROOT / "web_persistence.db",
        PROJECT_ROOT / "web_persistence_v2.db",
    ]

    shadows_found = []
    for candidate in shadow_candidates:
        if candidate.exists() and candidate != canonical_path:
            try:
                with sqlite3.connect(str(candidate)) as conn:
                    tables = {row[0] for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()}
                    if 'beliefs' in tables:
                        count = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
                        if count > 0:
                            shadows_found.append({
                                "path": str(candidate),
                                "beliefs_count": count
                            })
            except Exception:
                pass

    if shadows_found:
        report.add(HealthCheckResult(
            sc_id="SC-DB-5",
            name="No shadowing DBs in root",
            passed=False,
            message=f"Found {len(shadows_found)} DB(s) in root that could shadow canonical DB",
            details={"shadows": shadows_found, "canonical": str(canonical_path)},
            severity="WARNING"
        ))
    else:
        report.add(HealthCheckResult(
            sc_id="SC-DB-5",
            name="No shadowing DBs in root",
            passed=True,
            message="No shadowing DBs found",
            details={"canonical": str(canonical_path)}
        ))


def check_sc_db_6(report: DBHealthReport, canonical_path: Path):
    """SC-DB-6: Overseer uses same DB as db_locator."""
    # Check if overseer.py imports db_locator
    overseer_path = PROJECT_ROOT / "src" / "services" / "overseer.py"

    if not overseer_path.exists():
        report.add(HealthCheckResult(
            sc_id="SC-DB-6",
            name="Overseer uses db_locator",
            passed=False,
            message="overseer.py not found",
            severity="WARNING"
        ))
        return

    content = overseer_path.read_text()
    uses_locator = "from src.services.db_locator import" in content or \
                   "db_locator" in content

    if uses_locator:
        report.add(HealthCheckResult(
            sc_id="SC-DB-6",
            name="Overseer uses db_locator",
            passed=True,
            message="Overseer imports db_locator"
        ))
    else:
        report.add(HealthCheckResult(
            sc_id="SC-DB-6",
            name="Overseer uses db_locator",
            passed=False,
            message="Overseer does NOT import db_locator (MT-16 issue)",
            details={"recommendation": "Overseer.__init__ should default to get_web_db()"},
            severity="WARNING"
        ))


def check_sc_db_7(report: DBHealthReport, db_path: Path, threshold: float = 0.10):
    """SC-DB-7: template_ids coverage >= threshold."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            # Check if column exists
            columns = {row[1] for row in conn.execute("PRAGMA table_info(beliefs)").fetchall()}
            if 'template_ids' not in columns:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-7",
                    name="template_ids coverage",
                    passed=False,
                    message="template_ids column does not exist",
                    severity="WARNING"
                ))
                return

            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            with_templates = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE template_ids IS NOT NULL AND template_ids != '' AND template_ids != '[]'"
            ).fetchone()[0]

            coverage = with_templates / total if total > 0 else 0

            if coverage >= threshold:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-7",
                    name="template_ids coverage",
                    passed=True,
                    message=f"Coverage: {coverage*100:.1f}% ({with_templates:,}/{total:,})",
                    details={"coverage": coverage, "with_templates": with_templates, "total": total}
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-7",
                    name="template_ids coverage",
                    passed=False,
                    message=f"Coverage {coverage*100:.1f}% below threshold {threshold*100:.0f}%",
                    details={"coverage": coverage, "threshold": threshold, "with_templates": with_templates, "total": total},
                    severity="WARNING"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-7",
            name="template_ids coverage",
            passed=False,
            message=f"Check failed: {e}",
            severity="WARNING"
        ))


def check_sc_db_8(report: DBHealthReport, canonical_path: Path):
    """SC-DB-8: Migration 023 applied to overseer.db."""
    overseer_db = canonical_path.parent / "overseer.db"

    if not overseer_db.exists():
        report.add(HealthCheckResult(
            sc_id="SC-DB-8",
            name="Migration 023 applied",
            passed=False,
            message=f"overseer.db not found at {overseer_db}",
            severity="WARNING"
        ))
        return

    try:
        with sqlite3.connect(str(overseer_db)) as conn:
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}

            # Migration 023 creates overseer_health_metrics
            if 'overseer_health_metrics' in tables:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-8",
                    name="Migration 023 applied",
                    passed=True,
                    message="overseer_health_metrics table exists"
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-8",
                    name="Migration 023 applied",
                    passed=False,
                    message="overseer_health_metrics table missing - run migration 023",
                    details={"existing_tables": sorted(tables)},
                    severity="WARNING"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-8",
            name="Migration 023 applied",
            passed=False,
            message=f"Check failed: {e}",
            severity="WARNING"
        ))


def check_sc_db_9(report: DBHealthReport, db_path: Path):
    """SC-DB-9: Foreign key integrity (beliefs.web_id)."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            # Check if web_metadata table exists
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}

            if 'web_metadata' not in tables:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-9",
                    name="Foreign key integrity",
                    passed=True,
                    message="web_metadata table not present (FK check skipped)",
                    severity="INFO"
                ))
                return

            # Count orphaned beliefs (web_id not in web_metadata)
            orphaned = conn.execute("""
                SELECT COUNT(*) FROM beliefs b
                WHERE NOT EXISTS (SELECT 1 FROM web_metadata w WHERE w.web_id = b.web_id)
            """).fetchone()[0]

            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]

            if orphaned == 0:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-9",
                    name="Foreign key integrity",
                    passed=True,
                    message="All beliefs have valid web_id references"
                ))
            else:
                rate = orphaned / total if total > 0 else 0
                report.add(HealthCheckResult(
                    sc_id="SC-DB-9",
                    name="Foreign key integrity",
                    passed=rate < 0.05,  # Allow up to 5% orphans
                    message=f"{orphaned:,} beliefs ({rate*100:.1f}%) have invalid web_id",
                    details={"orphaned": orphaned, "total": total, "rate": rate},
                    severity="WARNING" if rate < 0.05 else "ERROR"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-9",
            name="Foreign key integrity",
            passed=False,
            message=f"Check failed: {e}",
            severity="WARNING"
        ))


def check_sc_db_10(report: DBHealthReport, db_path: Path, threshold: float = 0.60):
    """SC-DB-10: Theory orphan rate below threshold."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            orphans = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE theory_id IS NULL OR theory_id = ''"
            ).fetchone()[0]

            orphan_rate = orphans / total if total > 0 else 0

            if orphan_rate <= threshold:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-10",
                    name="Theory orphan rate",
                    passed=True,
                    message=f"Orphan rate: {orphan_rate*100:.1f}% (threshold: {threshold*100:.0f}%)",
                    details={"orphan_rate": orphan_rate, "orphans": orphans, "total": total}
                ))
            else:
                report.add(HealthCheckResult(
                    sc_id="SC-DB-10",
                    name="Theory orphan rate",
                    passed=False,
                    message=f"Orphan rate {orphan_rate*100:.1f}% exceeds threshold {threshold*100:.0f}%",
                    details={"orphan_rate": orphan_rate, "orphans": orphans, "total": total, "threshold": threshold},
                    severity="WARNING"
                ))
    except Exception as e:
        report.add(HealthCheckResult(
            sc_id="SC-DB-10",
            name="Theory orphan rate",
            passed=False,
            message=f"Check failed: {e}",
            severity="WARNING"
        ))


def run_all_checks(quick: bool = False) -> DBHealthReport:
    """Run all DB health checks."""
    report = DBHealthReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        canonical_db=None,
        total_checks=0,
        passed=0,
        failed=0,
        warnings=0
    )

    # SC-DB-1: Get canonical DB (required for other checks)
    db_path = check_sc_db_1(report)
    if not db_path:
        report.finalize()
        return report

    report.canonical_db = str(db_path)

    # Essential checks (always run)
    check_sc_db_2(report, db_path)
    check_sc_db_3(report, db_path)
    check_sc_db_4(report, db_path)

    if not quick:
        # Extended checks
        check_sc_db_5(report, db_path)
        check_sc_db_6(report, db_path)
        check_sc_db_7(report, db_path)
        check_sc_db_8(report, db_path)
        check_sc_db_9(report, db_path)
        check_sc_db_10(report, db_path)

    report.finalize()
    return report


def print_report(report: DBHealthReport):
    """Print human-readable report."""
    print("\n" + "=" * 60)
    print("  DATABASE HEALTH CHECK REPORT")
    print("=" * 60)
    print(f"  Timestamp: {report.timestamp}")
    print(f"  Canonical DB: {report.canonical_db or 'NOT FOUND'}")
    print()

    # Summary
    status = "HEALTHY" if report.overall_healthy else "UNHEALTHY"
    status_icon = "\u2705" if report.overall_healthy else "\u274c"
    print(f"  {status_icon} Overall: {status}")
    print(f"  Checks: {report.total_checks} total, {report.passed} passed, {report.failed} failed, {report.warnings} warnings")
    print()

    # Details
    for result in report.results:
        if result.passed:
            icon = "\u2705"
        elif result.severity == "WARNING":
            icon = "\u26a0\ufe0f"
        else:
            icon = "\u274c"

        print(f"  {icon} [{result.sc_id}] {result.name}")
        print(f"      {result.message}")
        if result.details and not result.passed:
            for key, val in result.details.items():
                if isinstance(val, list) and len(val) > 5:
                    print(f"      {key}: [{len(val)} items]")
                else:
                    print(f"      {key}: {val}")

    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Check ATLAS database health")
    parser.add_argument("--quick", action="store_true", help="Run essential checks only")
    parser.add_argument("--json", action="store_true", help="Output as JSON for overseer")
    args = parser.parse_args()

    report = run_all_checks(quick=args.quick)

    if args.json:
        # Convert to JSON-serializable format
        output = {
            "timestamp": report.timestamp,
            "canonical_db": report.canonical_db,
            "total_checks": report.total_checks,
            "passed": report.passed,
            "failed": report.failed,
            "warnings": report.warnings,
            "overall_healthy": report.overall_healthy,
            "results": [asdict(r) for r in report.results]
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(report)

    # Exit code: 0 if healthy, 1 if unhealthy
    sys.exit(0 if report.overall_healthy else 1)


if __name__ == "__main__":
    main()
