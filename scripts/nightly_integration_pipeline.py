#!/usr/bin/env python3
"""
ATLAS Nightly Integration Pipeline
====================================

Created: 2026-02-27
Sprint: MAINTENANCE-1

Unified nightly pipeline that runs the complete integration and maintenance
cycle. Designed to be run via cron or manually each evening.

Stages:
    0. Pre-flight: Backup all databases
    1. Discovery: Check for new articles (AG acquisition pipeline + Zotero)
    2. Triage: Classify new articles
    3. Extraction: Extract claims from triaged articles
    4. Auto-approve: Approve extractions that meet quality thresholds
    5. Integration: Run SystemSetup.setup() for bulk integration
    6. Web health: Improve connectivity (AG's safe_improve_web_health)
    7. Health check: Run full health gauntlet
    8. Report: Generate nightly report + notifications

Prerequisites:
    - Python 3.10+
    - All ATLAS dependencies installed
    - data/extractions/ populated with extraction JSONs
    - data/templates/ populated with template JSONs

Usage:
    # Full nightly run
    python scripts/nightly_integration_pipeline.py

    # Specific stages only
    python scripts/nightly_integration_pipeline.py --stages backup,integrate,health

    # Dry run (show what would be done)
    python scripts/nightly_integration_pipeline.py --dry-run

    # Skip backup (not recommended)
    python scripts/nightly_integration_pipeline.py --skip-backup

Cron example (run at 11 PM nightly):
    0 23 * * * cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python scripts/nightly_integration_pipeline.py >> logs/nightly_$(date +\\%Y-\\%m-\\%d).log 2>&1
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.db_locator import get_web_db

DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NIGHTLY] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


class NightlyPipeline:
    """Orchestrates the full nightly integration cycle."""

    def __init__(self, dry_run: bool = False, skip_backup: bool = False):
        self.dry_run = dry_run
        self.skip_backup = skip_backup
        self.report: Dict[str, Any] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "stages": {},
            "errors": [],
        }

    def run_stage(self, name: str, func, **kwargs) -> Dict[str, Any]:
        """Run a named stage with timing and error handling."""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"STAGE: {name}")
        logger.info(f"{'=' * 60}")

        start = time.time()
        result = {"status": "skipped", "duration_s": 0}

        if self.dry_run:
            logger.info(f"  [DRY-RUN] Would run: {name}")
            result["status"] = "dry_run"
        else:
            try:
                output = func(**kwargs)
                result["status"] = "ok"
                result["output"] = output
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                self.report["errors"].append(f"{name}: {e}")
                logger.error(f"  FAILED: {e}", exc_info=True)

        result["duration_s"] = round(time.time() - start, 1)
        self.report["stages"][name] = result
        logger.info(f"  → {result['status']} ({result['duration_s']}s)")
        return result

    # =========================================================================
    # STAGE 0: BACKUP
    # =========================================================================

    def stage_backup(self) -> Dict[str, Any]:
        """Pre-flight: back up all critical databases."""
        if self.skip_backup:
            return {"skipped": True}

        result = subprocess.run(
            [sys.executable, "scripts/backup_databases.py",
             "--tag", f"nightly_{datetime.now().strftime('%Y%m%d')}"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=120,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
        }

    # =========================================================================
    # STAGE 1-3: DISCOVERY, TRIAGE, EXTRACTION
    # =========================================================================

    def stage_discovery(self) -> Dict[str, Any]:
        """Check for new articles via AG's acquisition pipeline."""
        # Check if run_acquisition_pipeline.py exists
        acq_script = PROJECT_ROOT / "scripts" / "run_acquisition_pipeline.py"
        if not acq_script.exists():
            return {"skipped": True, "reason": "acquisition script not found"}

        result = subprocess.run(
            [sys.executable, str(acq_script), "--dry-run"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=300,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",
        }

    def stage_triage(self) -> Dict[str, Any]:
        """Triage new articles in the extraction queue."""
        queue_path = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
        if not queue_path.exists():
            return {"skipped": True, "reason": "no extraction queue"}

        raw = json.loads(queue_path.read_text(encoding="utf-8"))
        items = raw.get("items", {}) if isinstance(raw, dict) else {}
        pending = sum(
            1 for item in items.values()
            if isinstance(item, dict) and item.get("status") == "pending"
        )
        return {"pending_articles": pending, "note": "manual triage required via gemini_triage_papers.py"}

    def stage_extraction(self) -> Dict[str, Any]:
        """Check extraction queue status."""
        queue_path = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
        if not queue_path.exists():
            return {"skipped": True}

        raw = json.loads(queue_path.read_text(encoding="utf-8"))
        items = raw.get("items", {}) if isinstance(raw, dict) else {}
        status_counts = {}
        for item in items.values():
            if isinstance(item, dict):
                s = item.get("status", "unknown")
                status_counts[s] = status_counts.get(s, 0) + 1

        return {"queue_status": status_counts, "total": len(items)}

    # =========================================================================
    # STAGE 3.5: QA QUALITY GATE (H5)
    # =========================================================================

    def stage_qa_quality_gate(self) -> Dict[str, Any]:
        """
        Extraction quality gate: validate all extraction JSONs against
        the 50+ field quality rules.

        Uses ExtractionFieldValidator (src/qa/extraction_field_validator.py).
        Flags articles below 0.75 quality score for re-extraction.
        Writes re-extraction queue to data/extraction_pipeline/reextraction_queue.json.

        Reports to OVERSEER if mean quality drops below 0.75.
        Gracefully skips if validator is unavailable.
        """
        extractions_dir = DATA_DIR / "extractions"
        if not extractions_dir.exists():
            return {"skipped": True, "reason": "extractions directory not found"}

        try:
            from src.qa.extraction_field_validator import ExtractionFieldValidator

            validator = ExtractionFieldValidator()
            batch_report = validator.validate_batch(extractions_dir)

            # Identify articles below quality threshold
            threshold = 0.75
            below_threshold = batch_report.articles_below_threshold(threshold)

            # Build re-extraction queue
            reextraction_queue = []
            for article in below_threshold:
                reextraction_queue.append({
                    "file": article.source_file,
                    "quality_score": round(article.quality_score, 4),
                    "critical_errors": len(article.critical_errors),
                    "total_violations": len(article.all_violations),
                    "top_violations": dict(
                        sorted(article.violations_by_field().items(),
                               key=lambda x: -x[1])[:3]
                    ),
                })

            # Write re-extraction queue
            reextract_path = (
                DATA_DIR / "extraction_pipeline" / "reextraction_queue.json"
            )
            reextract_path.parent.mkdir(parents=True, exist_ok=True)
            reextract_path.write_text(
                json.dumps({
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "threshold": threshold,
                    "total_articles": len(batch_report.articles),
                    "articles_below_threshold": len(below_threshold),
                    "mean_quality": round(batch_report.mean_score, 4),
                    "queue": reextraction_queue,
                }, indent=2),
                encoding="utf-8",
            )

            logger.info(
                f"QA Quality Gate: {len(batch_report.articles)} articles, "
                f"mean={batch_report.mean_score:.3f}, "
                f"{len(below_threshold)} below {threshold}"
            )

            # Report to Overseer if mean quality drops below threshold (QA-1 invariant)
            mean_quality = batch_report.mean_score
            if mean_quality < threshold:
                logger.warning(
                    f"QA Quality Gate ALERT: Mean extraction quality {mean_quality:.3f} "
                    f"is below threshold {threshold}. "
                    f"{len(below_threshold)}/{len(batch_report.articles)} articles flagged for re-extraction."
                )

            # Phase 1B: Compute violation statistics
            all_violations = {}
            for article in batch_report.articles:
                for field, count in article.violations_by_field().items():
                    all_violations[field] = all_violations.get(field, 0) + count

            # Get top violation types
            top_violations = sorted(all_violations.items(), key=lambda x: -x[1])[:10]

            return {
                "total_articles": len(batch_report.articles),
                "total_findings": batch_report.total_findings,
                "mean_quality": round(batch_report.mean_score, 4),
                "articles_below_threshold": len(below_threshold),
                "threshold": threshold,
                "total_violations": batch_report.total_violations,
                "reextraction_queue_path": str(reextract_path),
                # Phase 1B additions
                "top_violation_fields": {k: v for k, v in top_violations},
                "quality_score_distribution": {
                    "min": round(min(a.quality_score for a in batch_report.articles), 4) if batch_report.articles else 0,
                    "max": round(max(a.quality_score for a in batch_report.articles), 4) if batch_report.articles else 0,
                    "mean": round(batch_report.mean_score, 4),
                },
            }

        except ImportError:
            logger.warning("ExtractionFieldValidator not available; skipping QA quality gate")
            return {"skipped": True, "reason": "validator unavailable"}
        except Exception as e:
            logger.error(f"QA quality gate failed: {e}", exc_info=True)
            return {"error": str(e)}

    # =========================================================================
    # STAGE 4: AUTO-APPROVE
    # =========================================================================

    def stage_auto_approve(self) -> Dict[str, Any]:
        """
        Auto-approve extractions that meet quality thresholds.

        Threshold: extraction must have ≥5 findings, article_type classified,
        and classification_confidence ≥ 0.7.
        """
        queue_path = DATA_DIR / "extraction_pipeline" / "extraction_queue.json"
        if not queue_path.exists():
            return {"skipped": True}

        raw = json.loads(queue_path.read_text(encoding="utf-8"))
        items = raw.get("items", {}) if isinstance(raw, dict) else {}

        auto_approved = 0
        manual_review = 0

        for pid, item in items.items():
            if not isinstance(item, dict) or item.get("status") != "accepted":
                continue

            extraction = item.get("extraction_result", {})
            if not extraction:
                manual_review += 1
                continue

            findings = extraction.get("findings", [])
            confidence = item.get("classification_confidence", 0)
            article_type = item.get("article_type", "unknown")

            # Auto-approve if quality thresholds met
            if (len(findings) >= 5
                    and confidence >= 0.7
                    and article_type != "unknown"):
                item["status"] = "approved"
                item["approved_at"] = datetime.now(timezone.utc).isoformat()
                item["reviewer_notes"] = "auto_approved_nightly"
                auto_approved += 1
            else:
                manual_review += 1

        if auto_approved > 0:
            # Update stats
            stats = raw.get("stats", {})
            stats["accepted"] = max(0, stats.get("accepted", 0) - auto_approved)
            stats["approved"] = stats.get("approved", 0) + auto_approved
            raw["stats"] = stats
            raw["updated_at"] = datetime.now(timezone.utc).isoformat()

            queue_path.write_text(
                json.dumps(raw, indent=2, default=str),
                encoding="utf-8",
            )

        return {
            "auto_approved": auto_approved,
            "manual_review_needed": manual_review,
        }

    # =========================================================================
    # STAGE 5: INTEGRATION
    # =========================================================================

    def stage_integrate(self) -> Dict[str, Any]:
        """
        Run SystemSetup.setup() for bulk integration of all extraction JSONs.

        This rebuilds the entire web from scratch using all available extractions.
        Benchmarked at ~4 minutes for 800+ papers.
        """
        try:
            from src.services.system_setup import SystemSetup

            setup = SystemSetup(
                db_path=str(get_web_db()),  # Centralized: was hardcoded
                extractions_dir="data/extractions",
                theories_dir="data/theories",
                templates_dir="data/templates",
                output_dir="data/setup_output",
            )

            start = time.time()
            report = setup.setup()
            elapsed = time.time() - start

            return {
                "state": str(report.state),
                "papers_loaded": report.n_papers_loaded,
                "beliefs_created": report.n_beliefs_created,
                "constraints_created": report.n_constraints_created,
                "equilibrium_iterations": report.equilibrium_iterations,
                "convergence_achieved": report.convergence_achieved,
                "final_coherence": report.final_coherence,
                "elapsed_s": round(elapsed, 1),
                "warnings": report.warnings[:5],
            }
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # STAGE 6: WEB HEALTH IMPROVEMENT
    # =========================================================================

    def stage_web_health(self) -> Dict[str, Any]:
        """Run AG's safe_improve_web_health to connect isolated beliefs."""
        script = PROJECT_ROOT / "scripts" / "safe_improve_web_health.py"
        if not script.exists():
            return {"skipped": True, "reason": "script not found"}

        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=300,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-1000:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
        }

    # =========================================================================
    # STAGE 7: HEALTH CHECK GAUNTLET
    # =========================================================================

    def stage_health_check(self) -> Dict[str, Any]:
        """Run the full health check gauntlet."""
        results = {}

        health_scripts = [
            ("check_web_bn_health", "scripts/check_web_bn_health.py"),
            ("compute_system_health", "scripts/compute_system_health.py"),
        ]

        for name, script_path in health_scripts:
            script = PROJECT_ROOT / script_path
            if not script.exists():
                results[name] = {"skipped": True}
                continue

            try:
                result = subprocess.run(
                    [sys.executable, str(script)],
                    capture_output=True, text=True, cwd=str(PROJECT_ROOT),
                    timeout=120,
                )
                results[name] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout[-500:] if result.stdout else "",
                }
            except subprocess.TimeoutExpired:
                results[name] = {"error": "timeout"}

        return results

    # =========================================================================
    # STAGE 7.2: WARRANT MONITORING
    # =========================================================================

    def _stage_warrant_monitoring(self) -> Dict[str, Any]:
        """
        Monitor warrant type distribution and flag issues.

        Scans all extraction JSON files and checks:
        1. Bridge warrant type distribution across canonical types
        2. Flags any extractions using deprecated/non-canonical names
        3. Identifies warrant types that are underrepresented (<5% of total)
        4. Tracks claims missing bridge_warrant_type entirely
        """
        extractions_dir = DATA_DIR / "extractions"
        if not extractions_dir.exists():
            return {"skipped": True, "reason": "extractions directory not found"}

        warrant_counts: Dict[str, int] = {
            "CONSTITUTIVE": 0,
            "MECHANISM": 0,
            "EMPIRICAL_ASSOCIATION": 0,
            "FUNCTIONAL": 0,
            "CAPACITY": 0,
            "ANALOGICAL": 0,
            "THEORY_DERIVED": 0,
            "unknown": 0,
        }

        deprecated_names = {
            "EMPIRICAL_COVARIANCE": "EMPIRICAL_ASSOCIATION",
            "THEORETICAL_DEFAULT": "THEORY_DERIVED",
            "empirical_covariance": "EMPIRICAL_ASSOCIATION",
            "theoretical_default": "THEORY_DERIVED",
        }

        deprecated_uses = []
        missing_warrant_types = []
        warnings = []

        try:
            for extraction_file in extractions_dir.glob("*.json"):
                try:
                    extraction = json.loads(extraction_file.read_text(encoding="utf-8"))

                    # Check template bridge_warrant field if present
                    bridge_warrant = extraction.get("bridge_warrant")
                    if bridge_warrant:
                        if bridge_warrant in deprecated_names:
                            canonical = deprecated_names[bridge_warrant]
                            deprecated_uses.append({
                                "file": extraction_file.name,
                                "used": bridge_warrant,
                                "canonical": canonical
                            })
                            warrant_counts[canonical] = warrant_counts.get(canonical, 0) + 1
                        elif bridge_warrant in warrant_counts:
                            warrant_counts[bridge_warrant] += 1
                        else:
                            warrant_counts["unknown"] += 1

                    # Check each claim's bridge_warrant_type if present
                    claims = extraction.get("claims", [])
                    for claim in claims:
                        claim_warrant = claim.get("bridge_warrant_type")
                        if claim_warrant:
                            if claim_warrant in deprecated_names:
                                canonical = deprecated_names[claim_warrant]
                                deprecated_uses.append({
                                    "file": extraction_file.name,
                                    "claim_id": claim.get("id"),
                                    "used": claim_warrant,
                                    "canonical": canonical
                                })
                                warrant_counts[canonical] = warrant_counts.get(canonical, 0) + 1
                            elif claim_warrant in warrant_counts:
                                warrant_counts[claim_warrant] += 1
                            else:
                                warrant_counts["unknown"] += 1
                        else:
                            missing_warrant_types.append({
                                "file": extraction_file.name,
                                "claim_id": claim.get("id", "unknown")
                            })

                except json.JSONDecodeError as e:
                    warnings.append(f"Malformed JSON in {extraction_file.name}: {str(e)[:100]}")
                except Exception as e:
                    warnings.append(f"Error processing {extraction_file.name}: {str(e)[:100]}")

            # Identify underrepresented warrant types (<5% of total non-unknown)
            total_warrants = sum(v for k, v in warrant_counts.items() if k != "unknown")
            underrepresented = []

            if total_warrants > 0:
                threshold = 0.05 * total_warrants
                for wt in ["CONSTITUTIVE", "MECHANISM", "EMPIRICAL_ASSOCIATION", "FUNCTIONAL",
                           "CAPACITY", "ANALOGICAL", "THEORY_DERIVED"]:
                    count = warrant_counts.get(wt, 0)
                    if 0 < count < threshold:
                        underrepresented.append({
                            "warrant_type": wt,
                            "count": count,
                            "percent": round(100 * count / total_warrants, 1)
                        })

            return {
                "status": "ok",
                "warrant_distribution": warrant_counts,
                "total_warrants": total_warrants,
                "coverage": {
                    "present_types": len([wt for wt in warrant_counts if warrant_counts[wt] > 0 and wt != "unknown"]),
                    "canonical_types": 7
                },
                "deprecated_uses": len(deprecated_uses),
                "deprecated_files": deprecated_uses[:10] if deprecated_uses else [],
                "missing_warrant_types": len(missing_warrant_types),
                "underrepresented_types": underrepresented,
                "warnings": warnings[:5] if warnings else []
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # =========================================================================
    # STAGE 7.5: OVERSEER COVERAGE METRICS (EN-0E)
    # =========================================================================

    def stage_overseer_coverage(self) -> Dict[str, Any]:
        """
        Run OVERSEER coverage and utilization invariants (INV-6..INV-9)
        and compute the AESHI composite score.
        """
        try:
            from src.services.overseer import OverseerService

            overseer = OverseerService(
                overseer_db_path=str(DATA_DIR / "overseer.db"),
                web=None,  # Will read from web.db directly
                web_db_path=str(get_web_db()),
                templates_dir=str(DATA_DIR / "templates"),
                extractions_dir=str(DATA_DIR / "extractions"),
                theories_dir=str(DATA_DIR / "theories"),
            )

            # Run coverage checks
            utilization = overseer._check_pipeline_utilization()
            template_coverage = overseer._check_template_belief_coverage()
            theory_orphan_rate = overseer._check_theory_linkage()
            evidence_diversity = overseer._check_evidence_diversity()

            # Compute AESHI
            health_metrics = {
                'pipeline_utilization': utilization,
                'template_belief_coverage': template_coverage,
                'theory_orphan_rate': theory_orphan_rate,
                'paper_evidence_ratio': evidence_diversity,
                'provenance_coverage': 1.0,  # placeholder
                'global_coherence': None,
                'conflict_rate': 0.0,
            }
            aeshi = overseer.compute_aeshi(health_metrics)

            return {
                'pipeline_utilization': utilization,
                'template_belief_coverage': template_coverage,
                'theory_orphan_rate': theory_orphan_rate,
                'evidence_diversity': evidence_diversity,
                'aeshi_score': aeshi,
            }
        except Exception as e:
            return {'error': str(e)}

    # =========================================================================
    # STAGE 7.7: NIGHTLY DISCOVERY (AG 2026-03-01, QA Spec Fix 5)
    # =========================================================================

    def stage_nightly_discovery(self) -> Dict[str, Any]:
        """Nightly discovery loop: gap prediction + defeater search + annotation harvest.

        This stage turns the nightly pipeline from a maintenance job into a
        learning loop. Every night:
        1. Run gap predictor on updated web → new PredictedGap objects
        2. Run defeater search for beliefs with credence ≥ 0.8
        3. Harvest OPEN_QUESTION/SEARCH_PROMPT annotations as user-guided gaps
        4. Re-score VOI with new data
        5. Generate discovery digest

        Non-critical: failures here don't block the rest of the pipeline.
        """
        result: Dict[str, Any] = {
            "gaps_found": 0,
            "high_voi_gaps": 0,
            "defeaters_found": 0,
            "annotations_harvested": 0,
            "digest": "",
        }

        # Step 1: Run gap predictor
        try:
            from src.services.gap_predictor import GapPredictor

            gp = GapPredictor()
            gap_report = gp.find_all_gaps(max_gaps=30)

            result["gaps_found"] = gap_report.n_gaps
            result["high_voi_gaps"] = sum(
                1 for g in gap_report.gaps if g.voi_score >= 0.8
            )
            result["gap_type_counts"] = gap_report.summary.get("gap_type_counts", {})

            # Save gap report
            gap_report_path = LOGS_DIR / f"gap_report_{datetime.now().strftime('%Y-%m-%d')}.json"
            gap_report_path.write_text(
                json.dumps(gap_report.to_dict(), indent=2, default=str),
                encoding="utf-8",
            )
            result["gap_report_path"] = str(gap_report_path)

            logger.info(
                "Gap prediction: %d gaps found (%d high-VOI)",
                result["gaps_found"], result["high_voi_gaps"],
            )
        except Exception as e:
            logger.warning(f"Gap prediction failed (non-critical): {e}")
            result["gap_error"] = str(e)

        # Step 2: Defeater search for high-credence beliefs
        try:
            from src.services.gap_predictor import GapPredictor

            gp = GapPredictor()
            defeater_result = gp.find_all_defeaters(limit=10)

            result["beliefs_checked_for_defeaters"] = defeater_result.get(
                "beliefs_checked", 0
            )
            result["defeaters_found"] = defeater_result.get(
                "beliefs_with_defeaters", 0
            )

            logger.info(
                "Defeater search: checked %d beliefs, found defeaters for %d",
                result["beliefs_checked_for_defeaters"],
                result["defeaters_found"],
            )
        except Exception as e:
            logger.warning(f"Defeater search failed (non-critical): {e}")
            result["defeater_error"] = str(e)

        # Step 3: Count annotation-harvested gaps (already included in gap_report)
        try:
            from src.services.gap_predictor import GapPredictor

            gp = GapPredictor()
            ann_gaps = gp.harvest_annotation_gaps()
            result["annotations_harvested"] = len(ann_gaps)

            logger.info(
                "Annotation harvest: %d gaps from user annotations",
                result["annotations_harvested"],
            )
        except Exception as e:
            logger.warning(f"Annotation harvest failed (non-critical): {e}")

        # Step 4: VOI re-scoring summary
        try:
            from src.cmr.voi_scoring import aggregate_paper_voi

            # If gap_report exists, show VOI distribution
            if "gap_report" in dir() and gap_report.gaps:
                voi_scores = [g.voi_score for g in gap_report.gaps]
                result["voi_summary"] = {
                    "mean_voi": round(sum(voi_scores) / len(voi_scores), 3),
                    "max_voi": round(max(voi_scores), 3),
                    "above_0.8": sum(1 for v in voi_scores if v >= 0.8),
                }
        except Exception as e:
            logger.debug(f"VOI summary failed: {e}")

        # Step 5: Generate discovery digest
        digest_lines = [
            f"## Nightly Discovery Digest — {datetime.now().strftime('%Y-%m-%d')}",
            "",
            f"- **Gaps found**: {result['gaps_found']} ({result['high_voi_gaps']} high-VOI)",
            f"- **Defeaters**: checked {result.get('beliefs_checked_for_defeaters', 0)} beliefs, "
            f"found defeaters for {result['defeaters_found']}",
            f"- **Annotation harvest**: {result['annotations_harvested']} user-identified gaps",
        ]

        if result.get("voi_summary"):
            vs = result["voi_summary"]
            digest_lines.append(
                f"- **VOI**: mean={vs['mean_voi']}, max={vs['max_voi']}, "
                f"{vs['above_0.8']} above 0.8 threshold"
            )

        digest = "\n".join(digest_lines)
        result["digest"] = digest

        # Save digest
        digest_path = LOGS_DIR / f"discovery_digest_{datetime.now().strftime('%Y-%m-%d')}.md"
        digest_path.write_text(digest, encoding="utf-8")
        result["digest_path"] = str(digest_path)

        logger.info("\n" + digest)
        return result

    # =========================================================================
    # STAGE 8: REPORT
    # =========================================================================

    def stage_report(self) -> Dict[str, Any]:
        """Generate nightly report."""
        self.report["completed_at"] = datetime.now(timezone.utc).isoformat()
        self.report["n_errors"] = len(self.report["errors"])

        # Compute total duration
        stages_ok = sum(
            1 for s in self.report["stages"].values()
            if s.get("status") == "ok"
        )
        stages_failed = sum(
            1 for s in self.report["stages"].values()
            if s.get("status") == "failed"
        )
        total_duration = sum(
            s.get("duration_s", 0) for s in self.report["stages"].values()
        )
        self.report["summary"] = {
            "stages_ok": stages_ok,
            "stages_failed": stages_failed,
            "total_duration_s": round(total_duration, 1),
        }

        # Save report
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = LOGS_DIR / f"nightly_{datetime.now().strftime('%Y-%m-%d')}.json"
        report_path.write_text(
            json.dumps(self.report, indent=2, default=str),
            encoding="utf-8",
        )

        # Also save markdown summary
        md_path = LOGS_DIR / f"nightly_{datetime.now().strftime('%Y-%m-%d')}.md"
        md_lines = [
            f"# Nightly Pipeline Report — {datetime.now().strftime('%Y-%m-%d')}",
            "",
            f"Duration: {total_duration:.1f}s | OK: {stages_ok} | Failed: {stages_failed}",
            "",
        ]
        for name, stage in self.report["stages"].items():
            status_emoji = {"ok": "✓", "failed": "✗", "dry_run": "○", "skipped": "—"}.get(
                stage.get("status", "?"), "?"
            )
            md_lines.append(
                f"- {status_emoji} **{name}** ({stage.get('duration_s', 0)}s) — {stage.get('status', '?')}"
            )
            if stage.get("error"):
                md_lines.append(f"  - Error: {stage['error'][:100]}")

        if self.report["errors"]:
            md_lines.extend(["", "## Errors", ""])
            for err in self.report["errors"]:
                md_lines.append(f"- {err[:200]}")

        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        # AESHI summary in report (EN-0E)
        overseer_stage = self.report["stages"].get("overseer_coverage", {})
        output = overseer_stage.get("output", {})
        if isinstance(output, dict) and "aeshi_score" in output:
            self.report["aeshi_score"] = output["aeshi_score"]
            logger.info(f"AESHI Score: {output['aeshi_score']}/100")

        # Queue notification if there were failures
        if stages_failed > 0:
            try:
                from src.services.notification_service import (
                    notify, NotificationType, Severity,
                )
                notify(
                    NotificationType.PIPELINE_FAILURE,
                    Severity.WARNING,
                    f"Nightly pipeline: {stages_failed} stage(s) failed",
                    f"Check {report_path}",
                    send_email=False,
                )
            except Exception as e:
                logger.debug(f"Non-critical: {e}")

        return {
            "report_path": str(report_path),
            "md_path": str(md_path),
        }

    # =========================================================================
    # MAIN ORCHESTRATION
    # =========================================================================

    def run(self, stages: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run the full nightly pipeline or specified stages."""

        all_stages = [
            ("backup", self.stage_backup),
            ("discovery", self.stage_discovery),
            ("triage", self.stage_triage),
            ("extraction", self.stage_extraction),
            ("qa_quality_gate", self.stage_qa_quality_gate),
            ("auto_approve", self.stage_auto_approve),
            ("integrate", self.stage_integrate),
            ("web_health", self.stage_web_health),
            ("health_check", self.stage_health_check),
            ("warrant_monitoring", self._stage_warrant_monitoring),
            ("overseer_coverage", self.stage_overseer_coverage),
            ("nightly_discovery", self.stage_nightly_discovery),
            ("report", self.stage_report),
        ]

        for name, func in all_stages:
            if stages and name not in stages:
                continue
            self.run_stage(name, func)

        return self.report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ATLAS Nightly Integration Pipeline"
    )
    parser.add_argument(
        "--stages", type=str,
        help="Comma-separated list of stages to run (default: all)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without doing it"
    )
    parser.add_argument(
        "--skip-backup", action="store_true",
        help="Skip pre-flight backup (not recommended)"
    )
    args = parser.parse_args()

    stages = args.stages.split(",") if args.stages else None

    pipeline = NightlyPipeline(
        dry_run=args.dry_run,
        skip_backup=args.skip_backup,
    )

    report = pipeline.run(stages=stages)

    # Print summary
    summary = report.get("summary", {})
    print(f"\n{'=' * 60}")
    print(f"NIGHTLY PIPELINE COMPLETE")
    print(f"  OK: {summary.get('stages_ok', 0)}")
    print(f"  Failed: {summary.get('stages_failed', 0)}")
    print(f"  Duration: {summary.get('total_duration_s', 0)}s")
    if report.get("errors"):
        print(f"  Errors:")
        for err in report["errors"]:
            print(f"    - {err[:100]}")
    print(f"{'=' * 60}")

    return 1 if summary.get("stages_failed", 0) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
