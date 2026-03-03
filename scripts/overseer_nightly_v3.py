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
    # Section 9: Management Layer (Pipeline Monitoring & Queue Health)
    # =========================================================================
    logger.info("Section 9: Management layer (pipeline monitoring, queue health)...")
    management_report = {}
    try:
        from src.services.overseer_management import ManagementDashboard
        dashboard = ManagementDashboard(
            overseer_db_path=str(PROJECT_ROOT / "data" / "overseer.db"),
            web_db_path=str(PROJECT_ROOT / "data" / "article_eater.db"),
        )
        mgmt_result = dashboard.management_check()
        management_report = mgmt_result if isinstance(mgmt_result, dict) else {
            "pipeline_statuses": getattr(mgmt_result, "pipeline_statuses", {}),
            "queue_health": getattr(mgmt_result, "queue_health", {}),
            "article_flow": getattr(mgmt_result, "article_flow", {}),
            "suggestion_backlog": getattr(mgmt_result, "suggestion_backlog", {}),
            "extraction_queue": getattr(mgmt_result, "extraction_queue", {}),
            "panel_needs": getattr(mgmt_result, "panel_needs", []),
            "recommendations": getattr(mgmt_result, "recommendations", []),
        }
        report["sections"]["management"] = management_report
        logger.info(f"  Pipeline count: {len(management_report.get('pipeline_statuses', {}))}")
        logger.info(f"  Recommendations: {len(management_report.get('recommendations', []))}")
    except ImportError:
        logger.warning("Management layer not available (overseer_management.py missing)")
        report["sections"]["management"] = {"status": "unavailable", "reason": "module_not_found"}
    except Exception as e:
        logger.warning(f"Management layer check failed: {e}")
        report["sections"]["management"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # Section 10: Reflex System Execution
    # =========================================================================
    logger.info("Section 10: Reflex system execution...")
    reflex_results = {}
    try:
        from src.qa.reflex_system import ReflexRegistry
        registry = ReflexRegistry(
            repo_root=PROJECT_ROOT,
            overseer_db_path=PROJECT_ROOT / "data" / "overseer.db"
        )
        results = registry.run_all()

        total = len(results)
        fired = sum(1 for r in results if r.detected_issue)
        fixed = sum(1 for r in results if r.auto_fixed)
        unfixed = sum(1 for r in results if r.detected_issue and not r.auto_fixed)

        reflex_results = {
            "total_reflexes": total,
            "fired": fired,
            "fixed": fixed,
            "unfixed": unfixed,
            "success_rate": round((fixed / fired * 100) if fired > 0 else 0.0, 1),
            "details": [
                {
                    "reflex_id": r.reflex_id,
                    "detected": r.detected_issue,
                    "fixed": r.auto_fixed,
                    "needs_attention": r.needs_attention,
                }
                for r in results[:50]  # Limit detail to first 50 for brevity
            ]
        }
        report["sections"]["reflexes"] = reflex_results
        logger.info(f"  Total reflexes: {total}")
        logger.info(f"  Fired: {fired}, Fixed: {fixed}, Unfixed: {unfixed}")
    except ImportError:
        logger.warning("Reflex system not available (reflex_system.py missing)")
        report["sections"]["reflexes"] = {"status": "unavailable", "reason": "module_not_found"}
    except Exception as e:
        logger.warning(f"Reflex system execution failed: {e}")
        report["sections"]["reflexes"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # Section 11: Recommendation Loop Health
    # =========================================================================
    logger.info("Section 11: Recommendation loop health...")
    recommendation_loop_report = {}
    try:
        from src.services.recommendation_loop import RecommendationLoopService

        service = RecommendationLoopService(
            db_path=str(PROJECT_ROOT / "web_persistence_v2.db"),
            web_db_path=str(PROJECT_ROOT / "data" / "article_eater.db"),
        )

        # Run single pass and capture health metrics
        loop_result = service.run_single_pass(top_n=3)

        # Extract key metrics
        harvest_gaps = loop_result.get("steps", {}).get("harvest_gaps", {})
        harvest_qa = loop_result.get("steps", {}).get("harvest_qa", {})
        prioritize = loop_result.get("steps", {}).get("prioritize", {})
        insert = loop_result.get("steps", {}).get("insert", {})
        dispatch = loop_result.get("steps", {}).get("dispatch", {})
        health = loop_result.get("steps", {}).get("health", {})

        recommendation_loop_report = {
            "status": "operational",
            "cycle_duration_seconds": loop_result.get("duration_seconds", 0),
            "interpretation_space_gaps": harvest_gaps.get("count", 0),
            "qa_suggestions": harvest_qa.get("count", 0),
            "total_suggestions": prioritize.get("total_suggestions", 0),
            "high_voi_suggestions": prioritize.get("high_voi", 0),
            "medium_voi_suggestions": prioritize.get("medium_voi", 0),
            "low_voi_suggestions": prioritize.get("low_voi", 0),
            "inserted_into_queue": insert.get("inserted_count", 0),
            "searches_dispatched": dispatch.get("dispatched_count", 0),
            "total_targets_in_queue": dispatch.get("total_targets", 0),
            "high_priority_targets": dispatch.get("high_priority_targets", 0),
            "queue_health": health,
        }

        report["sections"]["recommendation_loop"] = recommendation_loop_report
        logger.info(f"  Harvested {harvest_gaps.get('count', 0)} gaps, {harvest_qa.get('count', 0)} QA items")
        logger.info(f"  Dispatched {dispatch.get('dispatched_count', 0)} searches from {dispatch.get('total_targets', 0)} targets")
        logger.info(f"  Queue health: {health.get('status', 'unknown')}")

    except ImportError:
        logger.warning("Recommendation loop service not available (recommendation_loop.py missing)")
        report["sections"]["recommendation_loop"] = {"status": "unavailable", "reason": "module_not_found"}
    except Exception as e:
        logger.warning(f"Recommendation loop health check failed: {e}")
        report["sections"]["recommendation_loop"] = {"status": "error", "error": str(e)}

    # =========================================================================
    # Section 12: QA Assessment (Confounder Risk & Credence Intervals)
    # =========================================================================
    logger.info("Section 12: QA assessment (confounder risk & credence intervals)...")
    qa_assessment_report = {}
    try:
        from src.services.pipeline_qa_integration import batch_assess_findings

        output_dir = PROJECT_ROOT / "data" / "qa_reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        qa_result = batch_assess_findings(output_dir=str(output_dir))

        qa_assessment_report = {
            "status": qa_result.get("status"),
            "timestamp": qa_result.get("timestamp"),
            "duration_ms": qa_result.get("duration_ms"),
        }

        # Add confounder assessment if available
        if qa_result.get("confounder_assessment"):
            conf = qa_result["confounder_assessment"]
            if conf.get("status") == "success" and conf.get("batch_report"):
                batch = conf["batch_report"]
                qa_assessment_report["confounder_risk"] = {
                    "beliefs_assessed": batch.get("beliefs_assessed", 0),
                    "high_risk_count": batch.get("high_risk_count", 0),
                    "medium_risk_count": batch.get("medium_risk_count", 0),
                    "low_risk_count": batch.get("low_risk_count", 0),
                    "mean_design_risk": batch.get("mean_design_risk", 0.0),
                    "mean_control_adequacy": batch.get("mean_control_adequacy", 0.0),
                }
                logger.info(
                    f"  Confounder risk: {batch.get('beliefs_assessed', 0)} beliefs, "
                    f"{batch.get('high_risk_count', 0)} high-risk, "
                    f"{batch.get('medium_risk_count', 0)} medium-risk"
                )
            elif conf.get("status") == "error":
                qa_assessment_report["confounder_risk"] = {
                    "status": "error",
                    "error": conf.get("error")
                }

        # Add credence assessment if available
        if qa_result.get("credence_assessment"):
            cred = qa_result["credence_assessment"]
            if cred.get("status") == "success" and cred.get("summary_stats"):
                stats = cred["summary_stats"]
                qa_assessment_report["credence_intervals"] = {
                    "n_estimates": stats.get("n_beliefs", 0),
                    "mean_ci_width": round(stats.get("mean_ci_width", 0.0), 3),
                    "median_ci_width": round(stats.get("median_ci_width", 0.0), 3),
                    "max_ci_width": round(stats.get("max_ci_width", 0.0), 3),
                }
                logger.info(
                    f"  Credence intervals: {stats.get('n_beliefs', 0)} estimates, "
                    f"mean width {stats.get('mean_ci_width', 0.0):.3f}"
                )
            elif cred.get("status") == "error":
                qa_assessment_report["credence_intervals"] = {
                    "status": "error",
                    "error": cred.get("error")
                }

        report["sections"]["qa_assessment"] = qa_assessment_report

    except ImportError:
        logger.warning("QA integration module not available (pipeline_qa_integration.py missing)")
        report["sections"]["qa_assessment"] = {"status": "unavailable", "reason": "module_not_found"}
    except Exception as e:
        logger.warning(f"QA assessment failed (non-fatal): {e}")
        report["sections"]["qa_assessment"] = {"status": "error", "error": str(e)}

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

    # ── ETL Data Quality Metrics (Wave 8, V10 #4 Data Engineer) ──────
    if extractions_dir and extractions_dir.exists():
        try:
            import json as _json
            total_findings = 0
            with_sample_size = 0
            with_effect_size = 0
            with_theory_commitments = 0
            with_mechanism_chain = 0
            with_instruments = 0
            v3_count = 0
            files_with_findings = 0

            for ext_file in extractions_dir.glob("*.json"):
                try:
                    data = _json.loads(ext_file.read_text(errors='replace'))
                    if not isinstance(data, dict):
                        continue
                    if data.get("extraction_version") == "v3.0":
                        v3_count += 1
                    findings = data.get("findings", [])
                    if findings:
                        files_with_findings += 1
                    for f in findings:
                        total_findings += 1
                        if f.get("sample_size"):
                            with_sample_size += 1
                        if f.get("effect_size"):
                            with_effect_size += 1
                    if data.get("theory_commitments"):
                        with_theory_commitments += 1
                    if data.get("mechanism_chain"):
                        with_mechanism_chain += 1
                    if data.get("instruments_used"):
                        with_instruments += 1
                except Exception:
                    pass

            n = max(total_findings, 1)
            stats["data_quality"] = {
                "total_findings": total_findings,
                "files_with_findings": files_with_findings,
                "v3_count": v3_count,
                "sample_size_pct": round(100 * with_sample_size / n, 1),
                "effect_size_pct": round(100 * with_effect_size / n, 1),
                "theory_commitments_pct": round(100 * with_theory_commitments / max(files_with_findings, 1), 1),
                "mechanism_chain_pct": round(100 * with_mechanism_chain / max(files_with_findings, 1), 1),
                "instruments_pct": round(100 * with_instruments / max(files_with_findings, 1), 1),
            }
            logger.info(
                f"  Data quality: {with_sample_size}/{total_findings} "
                f"({stats['data_quality']['sample_size_pct']}%) sample_size, "
                f"{with_effect_size}/{total_findings} "
                f"({stats['data_quality']['effect_size_pct']}%) effect_size"
            )
        except Exception as e:
            logger.warning(f"ETL metrics scan failed: {e}")
    
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
            if isinstance(val, dict):
                continue  # Handle nested dicts separately
            lines.append(f"| {key.replace('_', ' ').title()} | {val} |")
        lines.append("")

        # Data Quality sub-table (Wave 8, V10 #4 Data Engineer)
        dq = stats.get("data_quality", {})
        if dq:
            lines.extend([
                "## ETL Data Quality",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Total Findings | {dq.get('total_findings', '?')} |",
                f"| Files with Findings | {dq.get('files_with_findings', '?')} |",
                f"| At v3.0 | {dq.get('v3_count', '?')} |",
                f"| **sample_size** | **{dq.get('sample_size_pct', '?')}%** |",
                f"| **effect_size** | **{dq.get('effect_size_pct', '?')}%** |",
                f"| theory_commitments | {dq.get('theory_commitments_pct', '?')}% |",
                f"| mechanism_chain | {dq.get('mechanism_chain_pct', '?')}% |",
                f"| instruments | {dq.get('instruments_pct', '?')}% |",
                "",
            ])
    
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
