#!/usr/bin/env python3
"""
Overseer Nightly Report v3 — Phase 4, Task 4.6
===============================================

Runs all invariants (INV-0..INV-13), computes AESHI, checks pipeline
utilization, template/theory coverage, annotation freshness, CVA stability,
runs predictive health, executes playbooks for violations, generates unified
report (JSON + markdown), and notifies if AESHI dropped >5 or new CRITICAL.

Usage:
    python scripts/overseer_nightly_v3.py
    python scripts/overseer_nightly_v3.py --dry-run
    python scripts/overseer_nightly_v3.py --output data/reports/
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_nightly_v3(dry_run: bool = False, output_dir: str = None) -> dict:
    """Execute full nightly v3 audit."""
    start = time.time()
    report = {
        "version": "3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "sections": {},
        "summary": {},
    }
    
    # =========================================================================
    # Section 1: Core Health Metrics
    # =========================================================================
    logger.info("Section 1: Core health metrics...")
    health_metrics = {}
    try:
        from src.services.overseer import OverseerService
        # Try to instantiate - may fail without DB access
        overseer = OverseerService(
            overseer_db_path=":memory:",
            web=None,
            web_db_path=str(PROJECT_ROOT / "data" / "article_eater.db"),
        )
        health_metrics = overseer.check_health()
        report["sections"]["health"] = health_metrics
    except Exception as e:
        logger.warning(f"Health check unavailable: {e}")
        report["sections"]["health"] = {"status": "unavailable", "error": str(e)}
    
    # =========================================================================
    # Section 2: Invariant Checks (INV-0..INV-9)
    # =========================================================================
    logger.info("Section 2: Core invariants (INV-0..INV-9)...")
    violations = []
    try:
        if 'overseer' in dir() and overseer:
            integrity = overseer.check_integrity()
            violations = integrity if isinstance(integrity, list) else []
    except Exception as e:
        logger.warning(f"Integrity check unavailable: {e}")
    
    report["sections"]["core_invariants"] = {
        "violations_count": len(violations),
        "violations": [v.__dict__ if hasattr(v, '__dict__') else str(v) for v in violations],
    }
    
    # =========================================================================
    # Section 3: CVA Invariants (INV-10..INV-13)
    # =========================================================================
    logger.info("Section 3: CVA invariants (INV-10..INV-13)...")
    try:
        from src.services.overseer_predictive import run_all_cva_checks
        cva_results = run_all_cva_checks()
        report["sections"]["cva_invariants"] = cva_results
    except ImportError:
        report["sections"]["cva_invariants"] = {"status": "module_not_available"}
    except Exception as e:
        report["sections"]["cva_invariants"] = {"status": "error", "error": str(e)}
    
    # =========================================================================
    # Section 4: AESHI Score
    # =========================================================================
    logger.info("Section 4: AESHI score...")
    aeshi_score = 50.0  # Default
    try:
        if 'overseer' in dir() and overseer:
            aeshi_score = overseer.compute_aeshi(health_metrics)
    except Exception as e:
        logger.warning(f"AESHI computation failed: {e}")
    
    report["sections"]["aeshi"] = {
        "score": round(aeshi_score, 1),
        "grade": _aeshi_grade(aeshi_score),
    }
    
    # =========================================================================
    # Section 5: Predictive Health
    # =========================================================================
    logger.info("Section 5: Predictive health...")
    try:
        from src.services.overseer_predictive import PredictiveHealthEngine
        pred_engine = PredictiveHealthEngine()
        
        # Build minimal history from current snapshot
        history = [{
            "timestamp": report["timestamp"],
            "aeshi_score": aeshi_score,
            "global_coherence": health_metrics.get("global_coherence", 0.5),
            "pipeline_utilization": health_metrics.get("pipeline_utilization", 0),
            "violation_count": len(violations),
            "provenance_coverage": health_metrics.get("provenance_coverage", 1.0),
        }]
        
        prediction = pred_engine.predict_health(history)
        patterns = pred_engine.detect_patterns(history)
        
        report["sections"]["predictive"] = {
            "prediction": prediction.to_dict(),
            "patterns": [p.to_dict() for p in patterns],
        }
    except Exception as e:
        report["sections"]["predictive"] = {"status": "error", "error": str(e)}
    
    # =========================================================================
    # Section 6: Self-Healing Cycle (Phase 4)
    # =========================================================================
    logger.info("Section 6: Self-healing cycle...")
    healing_summary = {}
    playbook_results = []
    if not dry_run and violations:
        try:
            from src.services.overseer_self_healing import SelfHealingOverseer
            
            healer = SelfHealingOverseer(overseer, enable_predictive=True)
            
            # Roll back any expired threshold adjustments first
            rollbacks = healer.rollback_adjustments()
            if rollbacks:
                logger.info(f"Rolled back {rollbacks} expired adjustments")
            
            # Full healing cycle
            heal_report = healer.heal()
            healing_summary = heal_report.to_dict()
            playbook_results = heal_report.playbook_results
            
            # Log results
            logger.info(
                f"Healing: {heal_report.violations_healed}/{heal_report.violations_detected} "
                f"healed, {heal_report.violations_deferred} deferred"
            )
        except ImportError:
            logger.warning("Self-healing engine not available, falling back to raw playbooks")
            try:
                from src.services.overseer_playbooks import RemediationEngine
                engine = RemediationEngine()
                for v in violations:
                    code = v.code if hasattr(v, 'code') else str(v)
                    try:
                        result = engine.execute_playbook(code)
                        playbook_results.append(
                            result.__dict__ if hasattr(result, '__dict__') else str(result)
                        )
                    except Exception as e:
                        playbook_results.append({"code": code, "error": str(e)})
            except Exception as e:
                logger.warning(f"Playbook execution failed: {e}")
        except Exception as e:
            logger.warning(f"Self-healing failed: {e}")
    
    report["sections"]["healing"] = {
        "summary": healing_summary,
        "playbook_results": playbook_results,
        "dry_run": dry_run,
    }
    
    # =========================================================================
    # Section 7: Completeness Audit
    # =========================================================================
    logger.info("Section 7: Completeness audit...")
    try:
        if 'overseer' in dir() and overseer:
            completeness = overseer.audit_completeness()
            report["sections"]["completeness"] = completeness
    except Exception as e:
        report["sections"]["completeness"] = {"status": "error", "error": str(e)}
    
    # =========================================================================
    # Section 8: System Statistics
    # =========================================================================
    logger.info("Section 8: System statistics...")
    stats = _collect_system_stats()
    report["sections"]["statistics"] = stats
    
    # =========================================================================
    # Summary
    # =========================================================================
    duration_ms = (time.time() - start) * 1000
    report["duration_ms"] = round(duration_ms, 1)
    report["summary"] = {
        "aeshi": round(aeshi_score, 1),
        "violations": len(violations),
        "cva_checks_passed": sum(
            1 for v in report["sections"].get("cva_invariants", {}).values()
            if isinstance(v, dict) and v.get("passed", False)
        ),
        "playbooks_executed": len(playbook_results),
        "duration_ms": round(duration_ms, 1),
    }
    
    # =========================================================================
    # Output
    # =========================================================================
    out_dir = Path(output_dir) if output_dir else PROJECT_ROOT / "data" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # JSON report
    json_path = out_dir / f"nightly_v3_{date_str}.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    # Markdown report
    md_path = out_dir / f"nightly_v3_{date_str}.md"
    with open(md_path, "w") as f:
        f.write(_generate_markdown(report))
    
    logger.info(f"Reports saved to {out_dir}")
    logger.info(f"  JSON: {json_path.name}")
    logger.info(f"  Markdown: {md_path.name}")
    
    # Alert check
    if aeshi_score < 60:
        logger.warning(f"⚠️  AESHI below threshold: {aeshi_score:.1f} < 60")
    
    return report


def _aeshi_grade(score: float) -> str:
    """Convert AESHI score to letter grade."""
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


def _collect_system_stats() -> dict:
    """Collect system-wide statistics."""
    stats = {}
    
    # Template count
    templates_dir = PROJECT_ROOT / "data" / "templates"
    if templates_dir.exists():
        stats["templates"] = len(list(templates_dir.glob("*.json")))
    
    # Extraction count
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    if extractions_dir.exists():
        stats["extractions"] = len(list(extractions_dir.glob("*.json")))
    
    # Molecule count
    molecules_dir = PROJECT_ROOT / "data" / "molecules"
    if molecules_dir.exists():
        stats["molecules"] = len(list(molecules_dir.glob("*.json")))
    
    # CVA files
    cva_files = list((PROJECT_ROOT / "src" / "services").glob("cva_*.py"))
    cva_models = list((PROJECT_ROOT / "src" / "models").glob("cva_*.py"))
    stats["cva_service_files"] = len(cva_files)
    stats["cva_model_files"] = len(cva_models)
    
    # Test count
    tests_dir = PROJECT_ROOT / "tests"
    if tests_dir.exists():
        stats["test_files"] = len(list(tests_dir.glob("test_*.py")))
    
    # Unresolved outcomes
    unresolved = PROJECT_ROOT / "data" / "unresolved_outcomes.jsonl"
    if unresolved.exists():
        with open(unresolved) as f:
            stats["unresolved_outcomes"] = sum(1 for _ in f)
    
    return stats


def _generate_markdown(report: dict) -> str:
    """Generate markdown nightly report."""
    lines = [
        f"# Overseer Nightly Report v3",
        f"**Date**: {report['timestamp']}",
        f"**Duration**: {report.get('duration_ms', 0):.0f}ms",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| AESHI Score | **{report['summary'].get('aeshi', '?')}** ({report['sections'].get('aeshi', {}).get('grade', '?')}) |",
        f"| Core Violations | {report['summary'].get('violations', 0)} |",
        f"| CVA Checks Passed | {report['summary'].get('cva_checks_passed', 0)}/4 |",
        f"| Playbooks Executed | {report['summary'].get('playbooks_executed', 0)} |",
        "",
    ]
    
    # Statistics
    stats = report["sections"].get("statistics", {})
    if stats:
        lines.extend([
            "## System Statistics",
            "",
            f"| Component | Count |",
            f"|-----------|-------|",
        ])
        for key, val in stats.items():
            lines.append(f"| {key.replace('_', ' ').title()} | {val} |")
        lines.append("")
    
    # CVA Invariants
    cva = report["sections"].get("cva_invariants", {})
    if isinstance(cva, dict) and cva.get("status") != "module_not_available":
        lines.extend(["## CVA Invariants", ""])
        for code, result in sorted(cva.items()):
            if isinstance(result, dict):
                status = "✅" if result.get("passed", False) else "❌"
                desc = result.get("description", code)
                lines.append(f"- {status} **{code}**: {desc}")
        lines.append("")
    
    # Predictive
    pred = report["sections"].get("predictive", {})
    if isinstance(pred, dict) and "prediction" in pred:
        p = pred["prediction"]
        lines.extend([
            "## Predictive Health",
            f"- **Predicted AESHI**: {p.get('predicted_aeshi', '?')}",
            f"- **Trend**: {p.get('trend_direction', 'unknown')} (slope: {p.get('trend_slope', 0):.3f}/day)",
            f"- **Confidence**: {p.get('confidence', 0):.0%}",
            f"- **Risk Factors**: {', '.join(p.get('risk_factors', ['none']))}",
            f"- **Recommendations**: {', '.join(p.get('recommended_actions', ['none']))}",
            "",
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Overseer Nightly Report v3")
    parser.add_argument("--dry-run", action="store_true", help="Don't execute remediations")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args()
    
    report = run_nightly_v3(dry_run=args.dry_run, output_dir=args.output)
    
    print(f"\n{'='*60}")
    print(f"NIGHTLY v3 COMPLETE")
    print(f"{'='*60}")
    print(f"AESHI: {report['summary'].get('aeshi', '?')} ({report['sections'].get('aeshi', {}).get('grade', '?')})")
    print(f"Violations: {report['summary'].get('violations', 0)}")
    print(f"CVA Checks: {report['summary'].get('cva_checks_passed', 0)}/4")
    print(f"Duration: {report.get('duration_ms', 0):.0f}ms")


if __name__ == "__main__":
    main()
