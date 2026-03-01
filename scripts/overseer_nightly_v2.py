#!/usr/bin/env python3
"""
Unified Nightly Health Orchestrator — ATLAS v2
===============================================

Created: 2026-02-27
Sprint: COMPLETENESS-1

Replaces overseer_nightly.py by running ALL health checks in a single
orchestrated sequence, aggregating results into a unified report with
trend comparison and prioritised action items.

Stages:
  1. compute_system_health.py  → AESHI score + gate results
  2. check_web_bn_health.py    → web/BN alignment metrics
  3. lint_bridge_ceilings.py   → ceiling violations
  4. corpus_health_report.py   → coverage snapshot
  5. overseer.periodic_audit() → INV-0..INV-5 (including fixed INV-4)
  6. Pipeline registry health
  7. Aggregate into unified report
  8. Trend comparison against previous run
  9. Generate prioritised action items
  10. Notify if AESHI drops or critical violations appear

Usage:
    python scripts/overseer_nightly_v2.py              # Full run
    python scripts/overseer_nightly_v2.py --dry-run    # Preview only
    python scripts/overseer_nightly_v2.py --skip-scripts  # Skip subprocess calls
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.services.notification_service import (
    notify_health_alert,
    notify_pipeline_failure,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("overseer_nightly_v2")

DATA_DIR = REPO_ROOT / "data"
DOCS_DIR = REPO_ROOT / "docs" / "overseer_reports"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Stage Runners
# =============================================================================

def run_script(name: str, script_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """Run a health script and capture its exit code."""
    result = {"stage": name, "status": "skipped", "output": "", "error": None}

    full_path = REPO_ROOT / script_path
    if not full_path.exists():
        result["status"] = "missing"
        result["error"] = f"Script not found: {script_path}"
        log.warning(f"[{name}] Script not found: {full_path}")
        return result

    if dry_run:
        result["status"] = "dry_run"
        log.info(f"[{name}] Would run: python {script_path}")
        return result

    try:
        log.info(f"[{name}] Running: python {script_path}")
        proc = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(REPO_ROOT),
        )
        result["output"] = proc.stdout[-2000:] if proc.stdout else ""
        result["error"] = proc.stderr[-1000:] if proc.stderr else None
        result["exit_code"] = proc.returncode
        result["status"] = "pass" if proc.returncode == 0 else "fail"
        log.info(f"[{name}] Exit code: {proc.returncode}")
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Script timed out after 300s"
        log.error(f"[{name}] Timed out")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        log.error(f"[{name}] Error: {e}")

    return result


def load_json_report(path: Path) -> Optional[Dict]:
    """Load a JSON report file if it exists."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"Failed to load {path}: {e}")
    return None


def run_overseer_audit(dry_run: bool = False) -> Dict[str, Any]:
    """Run the overseer periodic_audit() directly (no subprocess)."""
    result = {"stage": "overseer_audit", "status": "skipped"}

    if dry_run:
        result["status"] = "dry_run"
        return result

    try:
        from src.services.overseer import OverseerService

        # Find database paths
        overseer_db = None
        web_db = None
        for candidate in [DATA_DIR, DATA_DIR / "production", REPO_ROOT / ".data"]:
            if (candidate / "overseer.db").exists():
                overseer_db = candidate / "overseer.db"
            if (candidate / "web.db").exists():
                web_db = candidate / "web.db"

        if not overseer_db or not web_db:
            result["status"] = "missing_db"
            result["error"] = f"overseer.db: {overseer_db}, web.db: {web_db}"
            return result

        overseer = OverseerService(
            overseer_db_path=str(overseer_db),
            web=None,  # Graceful degradation — no live web instance in batch mode
            web_db_path=str(web_db),
        )
        violations = overseer.check_integrity()
        health = overseer.check_health()
        pipeline_health = overseer.get_pipeline_health()

        result["status"] = "pass" if not violations else "violations"
        result["violations"] = [
            {"code": v.code, "severity": v.severity, "description": v.description}
            for v in violations
        ]
        result["health_summary"] = {
            k: v for k, v in health.items()
            if isinstance(v, (int, float, str, bool, type(None)))
        }
        result["pipeline_health"] = pipeline_health

        log.info(
            f"[overseer_audit] {len(violations)} violations, "
            f"{len(pipeline_health)} pipelines tracked"
        )
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        log.error(f"[overseer_audit] Error: {e}")

    return result


# =============================================================================
# Trend Comparison
# =============================================================================

def load_previous_report() -> Optional[Dict]:
    """Load the most recent previous unified report."""
    reports = sorted(DOCS_DIR.glob("unified_health_*.json"))
    if reports:
        return load_json_report(reports[-1])
    return None


def compute_trends(current: Dict, previous: Optional[Dict]) -> Dict[str, Any]:
    """Compare current report to previous, compute deltas."""
    trends = {"has_previous": previous is not None}

    if not previous:
        return trends

    # AESHI delta
    curr_aeshi = current.get("aeshi_score", 0)
    prev_aeshi = previous.get("aeshi_score", 0)
    trends["aeshi_delta"] = curr_aeshi - prev_aeshi
    trends["aeshi_direction"] = (
        "improving" if trends["aeshi_delta"] > 0
        else "declining" if trends["aeshi_delta"] < 0
        else "stable"
    )

    # Violation delta
    curr_violations = current.get("total_violations", 0)
    prev_violations = previous.get("total_violations", 0)
    trends["violation_delta"] = curr_violations - prev_violations

    # Ceiling violation delta
    curr_ceiling = current.get("ceiling_violations", 0)
    prev_ceiling = previous.get("ceiling_violations", 0)
    trends["ceiling_delta"] = curr_ceiling - prev_ceiling

    return trends


# =============================================================================
# Action Item Generation
# =============================================================================

def generate_action_items(report: Dict) -> List[Dict[str, str]]:
    """Generate prioritised action items from report data."""
    items = []

    aeshi = report.get("aeshi_score", 0)
    if aeshi < 50:
        items.append({
            "priority": "P0",
            "action": "Fix pipeline smoke tests (AESHI bottleneck)",
            "impact": f"AESHI {aeshi:.0f} → estimated +15-20 points",
        })

    violations = report.get("overseer_audit", {}).get("violations", [])
    inv4 = [v for v in violations if v.get("code") == "INV-4"]
    if inv4:
        items.append({
            "priority": "P0",
            "action": "Investigate coherence decline (INV-4 violation)",
            "impact": "System stability at risk",
        })

    ceiling_count = report.get("ceiling_violations", 0)
    if ceiling_count > 50:
        items.append({
            "priority": "P1",
            "action": f"Audit {ceiling_count} ceiling violations (calibration review)",
            "impact": "Epistemic confidence accuracy",
        })

    # Pipeline staleness
    pipeline_health = report.get("overseer_audit", {}).get("pipeline_health", {})
    stale = [pid for pid, ph in pipeline_health.items() if ph.get("stale")]
    if stale:
        items.append({
            "priority": "P1",
            "action": f"Restart stale pipelines: {', '.join(stale)}",
            "impact": "Pipeline continuity",
        })

    # Trend-based actions
    trends = report.get("trends", {})
    if trends.get("aeshi_delta", 0) < -5:
        items.append({
            "priority": "P0",
            "action": f"AESHI dropped {abs(trends['aeshi_delta']):.0f} points since last run",
            "impact": "Rapid degradation — investigate immediately",
        })

    # Sort by priority
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return items[:5]  # Top 5


# =============================================================================
# Report Generation
# =============================================================================

def generate_markdown_report(report: Dict) -> str:
    """Generate human-readable markdown from the unified report."""
    lines = [
        f"# ATLAS Unified Health Report",
        f"*Generated: {report['timestamp']}*",
        "",
    ]

    # AESHI headline
    aeshi = report.get("aeshi_score", "?")
    band = report.get("aeshi_band", "?")
    lines.append(f"## System Health: AESHI {aeshi} ({band})")
    lines.append("")

    # Trends
    trends = report.get("trends", {})
    if trends.get("has_previous"):
        delta = trends.get("aeshi_delta", 0)
        direction = trends.get("aeshi_direction", "stable")
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        lines.append(f"**Trend**: {arrow} {direction} (Δ {delta:+.1f})")
        lines.append("")

    # Stage results
    lines.append("## Health Check Results")
    lines.append("")
    lines.append("| Stage | Status |")
    lines.append("|-------|--------|")
    for stage in report.get("stages", []):
        status_icon = {
            "pass": "PASS", "fail": "FAIL", "dry_run": "DRY-RUN",
            "missing": "MISSING", "timeout": "TIMEOUT", "error": "ERROR",
            "violations": "VIOLATIONS", "skipped": "SKIPPED",
        }.get(stage.get("status", "?"), stage.get("status", "?"))
        lines.append(f"| {stage['stage']} | {status_icon} |")
    lines.append("")

    # Overseer violations
    violations = report.get("overseer_audit", {}).get("violations", [])
    if violations:
        lines.append(f"## Invariant Violations ({len(violations)})")
        lines.append("")
        for v in violations:
            lines.append(f"- **{v['code']}** [{v['severity']}]: {v['description']}")
        lines.append("")

    # Pipeline health
    pipeline_health = report.get("overseer_audit", {}).get("pipeline_health", {})
    if pipeline_health:
        lines.append("## Pipeline Registry")
        lines.append("")
        lines.append("| Pipeline | Status | Last Run | Stale? |")
        lines.append("|----------|--------|----------|--------|")
        for pid, ph in pipeline_health.items():
            stale_str = "YES" if ph.get("stale") else "no"
            last = ph.get("last_run", "never")
            if last and len(last) > 19:
                last = last[:19]
            lines.append(
                f"| {pid} | {ph.get('last_status', 'unknown')} | {last} | {stale_str} |"
            )
        lines.append("")

    # Action items
    actions = report.get("action_items", [])
    if actions:
        lines.append("## Priority Actions")
        lines.append("")
        for a in actions:
            lines.append(f"- **[{a['priority']}]** {a['action']}")
            lines.append(f"  Impact: {a['impact']}")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Main Orchestrator
# =============================================================================

def run_unified_health(dry_run: bool = False, skip_scripts: bool = False) -> Dict:
    """Run the complete unified health check and return the report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log.info(f"=== ATLAS Unified Health Check: {timestamp} ===")

    report = {
        "timestamp": timestamp,
        "mode": "dry_run" if dry_run else "full",
        "stages": [],
    }

    # Stage 1-4: Run health scripts
    scripts = [
        ("system_health", "scripts/compute_system_health.py"),
        ("web_bn_health", "scripts/check_web_bn_health.py"),
        ("ceiling_lint", "scripts/lint_bridge_ceilings.py"),
        ("corpus_health", "scripts/corpus_health_report.py"),
    ]

    for name, path in scripts:
        if skip_scripts:
            report["stages"].append({"stage": name, "status": "skipped"})
        else:
            result = run_script(name, path, dry_run=dry_run)
            report["stages"].append(result)

    # Stage 5: Overseer audit (direct Python call)
    audit_result = run_overseer_audit(dry_run=dry_run)
    report["stages"].append(audit_result)
    report["overseer_audit"] = audit_result

    # Load computed reports for aggregation
    health_report = load_json_report(
        DATA_DIR / "production" / "system_health_report.json"
    )
    if health_report:
        score_data = health_report.get("score", health_report)
        if isinstance(score_data, dict):
            report["aeshi_score"] = score_data.get("overall_score", 0)
            report["aeshi_band"] = score_data.get("band", "?")
        else:
            report["aeshi_score"] = score_data
            report["aeshi_band"] = "?"

    ceiling_report = load_json_report(
        DATA_DIR / "ceiling_violation_report.json"
    )
    if ceiling_report:
        if isinstance(ceiling_report, list):
            report["ceiling_violations"] = len(ceiling_report)
        elif isinstance(ceiling_report, dict):
            report["ceiling_violations"] = ceiling_report.get(
                "total_violations", len(ceiling_report.get("violations", []))
            )

    # Total violations from overseer
    report["total_violations"] = len(
        audit_result.get("violations", [])
    )

    # Stage 8: Trend comparison
    previous = load_previous_report()
    report["trends"] = compute_trends(report, previous)

    # Stage 9: Action items
    report["action_items"] = generate_action_items(report)

    # Save JSON report
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = DOCS_DIR / f"unified_health_{today}.json"
    json_path.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    log.info(f"JSON report saved: {json_path}")

    # Save markdown report
    md_path = DOCS_DIR / f"unified_health_{today}.md"
    md_path.write_text(generate_markdown_report(report), encoding="utf-8")
    log.info(f"Markdown report saved: {md_path}")

    # Stage 10: Notifications
    aeshi = report.get("aeshi_score", 100)
    if aeshi < 60:
        notify_health_alert(
            aeshi,
            report.get("aeshi_band", "?"),
            f"Unified nightly check: {len(report.get('action_items', []))} action items",
        )

    trends = report.get("trends", {})
    if trends.get("aeshi_delta", 0) < -5:
        notify_health_alert(
            aeshi,
            report.get("aeshi_band", "?"),
            f"AESHI dropped {abs(trends['aeshi_delta']):.0f} points since last run!",
        )

    # Summary
    log.info(
        f"=== Unified Health Complete: AESHI {aeshi} "
        f"({report.get('aeshi_band', '?')}) | "
        f"{report.get('total_violations', 0)} violations | "
        f"{len(report.get('action_items', []))} actions ==="
    )

    return report


def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Unified Nightly Health Orchestrator"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview without running scripts or modifying DB",
    )
    parser.add_argument(
        "--skip-scripts", action="store_true",
        help="Skip subprocess health scripts (only run overseer audit)",
    )
    args = parser.parse_args()

    report = run_unified_health(
        dry_run=args.dry_run,
        skip_scripts=args.skip_scripts,
    )

    # Print summary
    aeshi = report.get("aeshi_score", "?")
    band = report.get("aeshi_band", "?")
    actions = report.get("action_items", [])
    print(f"\nATLAS Health: AESHI {aeshi} ({band})")
    if actions:
        print(f"Top action: [{actions[0]['priority']}] {actions[0]['action']}")

    sys.exit(0 if report.get("aeshi_score", 0) >= 60 else 1)


if __name__ == "__main__":
    main()
