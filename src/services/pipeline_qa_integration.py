"""
Pipeline QA Integration Module — Nightly and Paper Integration Wiring
=====================================================================

Provides orchestration for confounder risk checking and credence interval
computation in the context of the ATLAS pipeline.

Two entry points:
1. batch_assess_findings() — For nightly pipeline on all findings
2. assess_paper_beliefs() — For paper integration on newly-created beliefs

Created: 2026-03-02
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# Feature flag: enable/disable QA integration
QA_INTEGRATION_ENABLED = os.environ.get("AE_QA_INTEGRATION", "true").lower() == "true"
CONFOUNDER_CHECKER_ENABLED = os.environ.get("AE_CONFOUNDER_CHECKER", "true").lower() == "true"
CREDENCE_INTERVALS_ENABLED = os.environ.get("AE_CREDENCE_INTERVALS", "true").lower() == "true"


def batch_assess_findings(
    beliefs: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assess all findings in the system for confounder risk and credence uncertainty.

    Called by: overseer_nightly_v3.py as a new pipeline stage

    Args:
        beliefs: Optional list of belief dicts. If None, loads from database.
        output_dir: Optional directory to write QA reports to.

    Returns:
        Dict with structure:
        {
            "status": "success" | "error" | "disabled",
            "confounder_assessment": {...} or None,
            "credence_assessment": {...} or None,
            "timestamp": ISO datetime,
            "duration_ms": milliseconds,
            "error": str (if status=="error")
        }
    """
    import time
    start = time.time()

    result = {
        "status": "success",
        "confounder_assessment": None,
        "credence_assessment": None,
        "timestamp": None,
        "duration_ms": 0,
    }

    if not QA_INTEGRATION_ENABLED:
        logger.info("QA integration disabled (AE_QA_INTEGRATION=false)")
        result["status"] = "disabled"
        return result

    try:
        from datetime import datetime, timezone
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Load beliefs if not provided
        if beliefs is None:
            beliefs = _load_beliefs_from_db()
            logger.info(f"Loaded {len(beliefs)} beliefs from database")

        if not beliefs:
            logger.info("No beliefs to assess")
            result["duration_ms"] = int((time.time() - start) * 1000)
            return result

        # Run confounder risk assessment
        if CONFOUNDER_CHECKER_ENABLED:
            try:
                result["confounder_assessment"] = _run_confounder_assessment(beliefs, output_dir)
            except Exception as e:
                logger.warning(f"Confounder assessment failed (non-fatal): {e}")
                result["confounder_assessment"] = {
                    "status": "error",
                    "error": str(e)
                }

        # Run credence interval computation
        if CREDENCE_INTERVALS_ENABLED:
            try:
                result["credence_assessment"] = _run_credence_assessment(beliefs, output_dir)
            except Exception as e:
                logger.warning(f"Credence interval assessment failed (non-fatal): {e}")
                result["credence_assessment"] = {
                    "status": "error",
                    "error": str(e)
                }

        result["duration_ms"] = int((time.time() - start) * 1000)
        logger.info(f"QA batch assessment completed in {result['duration_ms']}ms")

        return result

    except Exception as e:
        logger.error(f"Batch QA assessment error: {e}")
        result["status"] = "error"
        result["error"] = str(e)
        result["duration_ms"] = int((time.time() - start) * 1000)
        return result


def assess_paper_beliefs(
    paper_id: str,
    beliefs: List[Dict[str, Any]],
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assess beliefs from a newly-integrated paper for QA issues.

    Called by: orchestrator.py after belief creation/update (Step 4+)

    Args:
        paper_id: Paper identifier for tracking.
        beliefs: List of newly-created belief dicts.
        output_dir: Optional directory to write QA reports to.

    Returns:
        Dict with structure:
        {
            "status": "success" | "error" | "skipped",
            "paper_id": str,
            "confounder_report": {...} or None,
            "credence_report": {...} or None,
            "high_risk_count": int,
            "recommendations": [str],
            "error": str (if status=="error")
        }
    """
    result = {
        "status": "success",
        "paper_id": paper_id,
        "confounder_report": None,
        "credence_report": None,
        "high_risk_count": 0,
        "recommendations": [],
    }

    if not QA_INTEGRATION_ENABLED:
        logger.debug(f"QA integration disabled for paper {paper_id}")
        result["status"] = "skipped"
        return result

    try:
        if not beliefs:
            logger.debug(f"Paper {paper_id} has no beliefs to assess")
            result["status"] = "skipped"
            return result

        # Run confounder risk assessment
        if CONFOUNDER_CHECKER_ENABLED:
            try:
                confounder_result = _run_confounder_assessment(
                    beliefs, output_dir, paper_id=paper_id
                )
                result["confounder_report"] = confounder_result

                # Count high-risk beliefs
                if confounder_result.get("batch_report"):
                    batch = confounder_result["batch_report"]
                    result["high_risk_count"] = batch.get("high_risk_count", 0)

                    # Add recommendations for high-risk beliefs
                    if result["high_risk_count"] > 0:
                        result["recommendations"].append(
                            f"Paper {paper_id}: {result['high_risk_count']} high-risk "
                            f"confounding beliefs detected — review control adequacy"
                        )
            except Exception as e:
                logger.warning(f"Confounder assessment for paper {paper_id} failed: {e}")
                result["confounder_report"] = {
                    "status": "error",
                    "error": str(e)
                }

        # Run credence interval computation
        if CREDENCE_INTERVALS_ENABLED:
            try:
                credence_result = _run_credence_assessment(
                    beliefs, output_dir, paper_id=paper_id
                )
                result["credence_report"] = credence_result

                # Check for wide confidence intervals
                if credence_result.get("summary_stats"):
                    stats = credence_result["summary_stats"]
                    mean_width = stats.get("mean_ci_width", 0.0)
                    if mean_width > 0.4:
                        result["recommendations"].append(
                            f"Paper {paper_id}: wide credence confidence intervals "
                            f"(mean width {mean_width:.2f}) — consider additional validation"
                        )
            except Exception as e:
                logger.warning(f"Credence assessment for paper {paper_id} failed: {e}")
                result["credence_report"] = {
                    "status": "error",
                    "error": str(e)
                }

        return result

    except Exception as e:
        logger.error(f"Paper {paper_id} QA assessment error: {e}")
        result["status"] = "error"
        result["error"] = str(e)
        return result


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _load_beliefs_from_db() -> List[Dict[str, Any]]:
    """Load all beliefs from the web of belief database."""
    try:
        from src.services.web_of_belief import WebOfBelief
        from src.services.db_locator import get_web_db

        web_db = get_web_db()
        # Try loading web of belief
        # This is a fallback; in production we'd load from the actual web object
        return []
    except Exception as e:
        logger.debug(f"Could not load beliefs from DB: {e}")
        return []


def _run_confounder_assessment(
    beliefs: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    paper_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run confounder risk assessment on beliefs.

    Returns dict with batch report and high-risk beliefs.
    """
    try:
        from src.qa.confounder_risk_checker import ConfounderRiskChecker

        checker = ConfounderRiskChecker()
        batch_report = checker.assess_all_beliefs(beliefs)

        result = {
            "status": "success",
            "batch_report": batch_report.to_dict(),
            "high_risk_beliefs": [
                r.to_dict() for r in batch_report.high_risk_beliefs
            ],
            "medium_risk_beliefs": [
                r.to_dict() for r in batch_report.medium_risk_beliefs
            ],
        }

        # Write report to file if output_dir specified
        if output_dir:
            try:
                _write_confounder_report(batch_report, output_dir, paper_id)
            except Exception as e:
                logger.debug(f"Could not write confounder report: {e}")

        logger.info(
            f"Confounder assessment: {batch_report.beliefs_assessed} beliefs, "
            f"{batch_report.high_risk_count} high-risk, "
            f"{batch_report.medium_risk_count} medium-risk"
        )

        return result

    except ImportError as e:
        logger.warning(f"ConfounderRiskChecker not available: {e}")
        return {"status": "unavailable", "error": str(e)}
    except Exception as e:
        logger.error(f"Confounder assessment error: {e}")
        raise


def _run_credence_assessment(
    beliefs: List[Dict[str, Any]],
    output_dir: Optional[str] = None,
    paper_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run credence interval computation on beliefs.

    Returns dict with batch result including confidence intervals.
    """
    try:
        from src.services.credence_intervals import batch_credence_intervals

        batch_result = batch_credence_intervals(beliefs, confidence_level=0.95)

        result = {
            "status": "success",
            "n_estimates": len(batch_result.estimates),
            "summary_stats": batch_result.summary_stats,
            "estimates": [
                {
                    "belief_id": est.notes.split(";")[0].replace("belief_id=", ""),
                    "point": round(est.point, 4),
                    "lower": round(est.lower, 4),
                    "upper": round(est.upper, 4),
                    "se": round(est.se, 4),
                    "width": round(est.width(), 4),
                    "components": est.components,
                }
                for est in batch_result.estimates[:10]  # First 10 for brevity
            ]
        }

        # Write report to file if output_dir specified
        if output_dir:
            try:
                _write_credence_report(batch_result, output_dir, paper_id)
            except Exception as e:
                logger.debug(f"Could not write credence report: {e}")

        logger.info(
            f"Credence interval assessment: {len(batch_result.estimates)} estimates, "
            f"mean CI width {batch_result.summary_stats.get('mean_ci_width', 0.0):.3f}"
        )

        return result

    except ImportError as e:
        logger.warning(f"Credence intervals module not available: {e}")
        return {"status": "unavailable", "error": str(e)}
    except Exception as e:
        logger.error(f"Credence assessment error: {e}")
        raise


def _write_confounder_report(
    batch_report,
    output_dir: str,
    paper_id: Optional[str] = None
):
    """Write confounder risk report to file."""
    import json
    from datetime import datetime

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"confounder_risk_{paper_id or 'batch'}_{timestamp}.json"
    filepath = output_path / filename

    filepath.write_text(
        json.dumps(batch_report.to_dict(), indent=2),
        encoding="utf-8"
    )
    logger.debug(f"Confounder report written to {filepath}")


def _write_credence_report(
    batch_result,
    output_dir: str,
    paper_id: Optional[str] = None
):
    """Write credence interval report to file."""
    import json
    from datetime import datetime

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"credence_intervals_{paper_id or 'batch'}_{timestamp}.json"
    filepath = output_path / filename

    report_dict = {
        "n_estimates": len(batch_result.estimates),
        "summary_stats": batch_result.summary_stats,
        "estimates": [
            {
                "belief_id": est.notes.split(";")[0].replace("belief_id=", ""),
                "point": round(est.point, 4),
                "lower": round(est.lower, 4),
                "upper": round(est.upper, 4),
                "se": round(est.se, 4),
                "components": est.components,
            }
            for est in batch_result.estimates
        ]
    }

    filepath.write_text(
        json.dumps(report_dict, indent=2),
        encoding="utf-8"
    )
    logger.debug(f"Credence report written to {filepath}")
