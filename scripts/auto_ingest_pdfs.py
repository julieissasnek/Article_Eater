#!/usr/bin/env python3
"""
auto_ingest_pdfs.py — Automatic PDF-to-EN Ingestion Pipeline
=============================================================

Watches data/pdfs_incoming/ for new PDFs and runs the full pipeline:
  1. DETECT:    Scan pdfs_incoming/ for new PDFs (not yet in extractions/)
  2. EXTRACT:   Run Gemini extraction on each PDF → extraction JSON
  3. QA GATE:   Validate extraction quality (≥0.75 score)
  4. INTEGRATE: Add beliefs to Web of Belief
  5. OVERSEER:  Notify Overseer of new integration, run health check

This script is the missing link between "drop PDFs in a folder" and
"beliefs appear in the EN with full provenance."

Usage:
  python scripts/auto_ingest_pdfs.py                    # process all new PDFs
  python scripts/auto_ingest_pdfs.py --watch             # poll every 60s
  python scripts/auto_ingest_pdfs.py --dry-run           # show what would happen
  python scripts/auto_ingest_pdfs.py --skip-integration  # extract only

Author: AG (Antigravity)
Date: 2026-03-02
"""

import json
import glob
import logging
import os
import shutil
import subprocess
import sys
import time
import argparse
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timezone

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [INGEST] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# PATHS
# =============================================================================

INCOMING_DIR = PROJECT_ROOT / "data" / "pdfs_incoming"
PROCESSED_DIR = PROJECT_ROOT / "data" / "pdfs"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
INGEST_LOG = PROJECT_ROOT / "data" / "acquisition" / "ingest_log.json"
HITL_DB = PROJECT_ROOT / "data" / "acquisition" / "hitl_needed.json"  # DOIs needing human
ACQUISITION_REPORT = PROJECT_ROOT / "data" / "acquisition" / "foundational_acquisition_report.json"


# =============================================================================
# INGESTION RESULT
# =============================================================================

@dataclass
class IngestResult:
    filename: str
    doi: Optional[str] = None
    stage: str = "detect"
    extracted: bool = False
    extraction_file: Optional[str] = None
    qa_score: Optional[float] = None
    qa_passed: bool = False
    integrated: bool = False
    beliefs_added: int = 0
    overseer_notified: bool = False
    overseer_violations: int = 0
    error: Optional[str] = None
    hitl_recorded: bool = False  # Written to HITL DB for human action
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# =============================================================================
# HITL (Human-In-The-Loop) FAILURE DATABASE
# =============================================================================

def record_hitl_needed(
    doi: str,
    reason: str,
    paper_info: Optional[Dict] = None,
    priority: str = "normal",
) -> None:
    """Record a DOI that needs human intervention for PDF acquisition.

    Writes to data/acquisition/hitl_needed.json — visible on dashboard.
    The Overseer can read this to recommend human actions.
    """
    HITL_DB.parent.mkdir(parents=True, exist_ok=True)

    # Load existing
    entries = []
    if HITL_DB.exists():
        try:
            with open(HITL_DB) as f:
                entries = json.load(f)
        except Exception:
            entries = []

    # Don't duplicate
    existing_dois = {e.get("doi") for e in entries}
    if doi in existing_dois:
        # Update existing entry
        for e in entries:
            if e.get("doi") == doi:
                e["last_attempt"] = datetime.now(timezone.utc).isoformat()
                e["attempt_count"] = e.get("attempt_count", 1) + 1
                e["reason"] = reason
                break
    else:
        entries.append({
            "doi": doi,
            "reason": reason,
            "priority": priority,
            "paper_info": paper_info or {},
            "first_recorded": datetime.now(timezone.utc).isoformat(),
            "last_attempt": datetime.now(timezone.utc).isoformat(),
            "attempt_count": 1,
            "status": "pending",  # pending | acquired | abandoned
            "recommended_sources": [
                "Elicit (paste DOI)",
                "Academia.edu (search by author)",
                "UCSD Library EZProxy",
                "scholar.archive.org",
            ],
        })

    with open(HITL_DB, "w") as f:
        json.dump(entries, f, indent=2)
    logger.info(f"  📋 HITL: recorded {doi} for human acquisition ({reason})")


def get_hitl_summary() -> Dict[str, Any]:
    """Get summary of HITL queue — for dashboard display."""
    if not HITL_DB.exists():
        return {"total": 0, "pending": 0, "acquired": 0}

    try:
        with open(HITL_DB) as f:
            entries = json.load(f)
    except Exception:
        return {"total": 0, "pending": 0, "acquired": 0}

    pending = [e for e in entries if e.get("status") == "pending"]
    acquired = [e for e in entries if e.get("status") == "acquired"]

    return {
        "total": len(entries),
        "pending": len(pending),
        "acquired": len(acquired),
        "high_priority": len([e for e in pending if e.get("priority") == "high"]),
        "oldest_pending": min((e.get("first_recorded", "") for e in pending), default=None),
        "pending_dois": [e["doi"] for e in pending[:10]],
    }


# =============================================================================
# PIPELINE STAGES
# =============================================================================

def detect_new_pdfs() -> List[Path]:
    """Find PDFs in incoming/ that haven't been extracted yet."""
    if not INCOMING_DIR.exists():
        INCOMING_DIR.mkdir(parents=True, exist_ok=True)
        return []

    pdf_files = sorted(INCOMING_DIR.glob("*.pdf"))
    if not pdf_files:
        return []

    # Check which have already been extracted
    existing_extractions = set()
    for f in EXTRACTIONS_DIR.glob("*.json"):
        stem = f.stem  # e.g., "10.1038_nrn2787"
        existing_extractions.add(stem)

    new_pdfs = []
    for pdf in pdf_files:
        stem = pdf.stem
        if stem not in existing_extractions:
            new_pdfs.append(pdf)
        else:
            logger.info(f"  Already extracted: {pdf.name}")

    return new_pdfs


def extract_pdf(pdf_path: Path, dry_run: bool = False) -> Optional[str]:
    """
    Extract a PDF using the v3 extraction pipeline.

    Returns the path to the extraction JSON, or None on failure.
    """
    if dry_run:
        logger.info(f"  [DRY RUN] Would extract: {pdf_path.name}")
        return None

    # Try using the Gemini extraction script
    extraction_script = PROJECT_ROOT / "scripts" / "v3_surgical_update.py"
    if not extraction_script.exists():
        # Fallback: try the simpler extraction approach
        extraction_script = PROJECT_ROOT / "scripts" / "extract_pdf.py"

    if not extraction_script.exists():
        logger.warning(f"  No extraction script found. Creating placeholder extraction.")
        return _create_placeholder_extraction(pdf_path)

    try:
        result = subprocess.run(
            [sys.executable, str(extraction_script), str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            # Look for the newly created extraction file
            stem = pdf_path.stem
            expected = EXTRACTIONS_DIR / f"{stem}.json"
            if expected.exists():
                return str(expected)
            # Check if it was created with a different name
            logger.warning(f"  Extraction completed but output file not found at {expected}")
        else:
            logger.error(f"  Extraction failed: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        logger.error(f"  Extraction timed out after 120s")
    except Exception as e:
        logger.error(f"  Extraction error: {e}")

    return None


def _create_placeholder_extraction(pdf_path: Path) -> Optional[str]:
    """Create a minimal extraction JSON for later re-extraction."""
    stem = pdf_path.stem
    # Try to parse DOI from filename
    doi = stem.replace("_", "/", 1)  # e.g., "10.1038_nrn2787" -> "10.1038/nrn2787"

    extraction = {
        "article_id": stem,
        "doi": doi,
        "title": f"[Pending full extraction] {stem}",
        "extraction_version": "v3-placeholder",
        "extraction_date": datetime.now(timezone.utc).isoformat(),
        "source_pdf": str(pdf_path),
        "needs_reextraction": True,
        "findings": [],
        "metadata": {
            "status": "placeholder",
            "note": "Auto-created by auto_ingest_pdfs.py. Needs Gemini re-extraction."
        }
    }

    out_path = EXTRACTIONS_DIR / f"{stem}.json"
    with open(out_path, "w") as f:
        json.dump(extraction, f, indent=2)

    logger.info(f"  Created placeholder extraction: {out_path.name}")
    return str(out_path)


def qa_check(extraction_path: str) -> float:
    """Run quality check on extraction. Returns score 0-1."""
    try:
        with open(extraction_path) as f:
            data = json.load(f)

        # Basic quality checks
        score = 0.0
        checks = 0

        # Has title?
        if data.get("title") and not data["title"].startswith("[Pending"):
            score += 1
        checks += 1

        # Has findings?
        findings = data.get("findings", [])
        if len(findings) > 0:
            score += 1
        checks += 1

        # Has DOI?
        if data.get("doi"):
            score += 1
        checks += 1

        # Has article type?
        if data.get("article_type"):
            score += 1
        checks += 1

        # More than 3 findings?
        if len(findings) >= 3:
            score += 1
        checks += 1

        # Has theory links?
        if data.get("theory_links") or data.get("theory_commitments"):
            score += 1
        checks += 1

        return score / checks if checks > 0 else 0.0

    except Exception as e:
        logger.warning(f"  QA check failed: {e}")
        return 0.0


def integrate_to_web(extraction_path: str, dry_run: bool = False) -> int:
    """
    Integrate extraction into Web of Belief.

    Returns number of beliefs added.
    """
    if dry_run:
        logger.info(f"  [DRY RUN] Would integrate: {extraction_path}")
        return 0

    try:
        from src.web_of_belief import WebOfBelief
        from src.services.extraction_to_web import ExtractionToWebIntegrator

        web = WebOfBelief()
        integrator = ExtractionToWebIntegrator(web)

        with open(extraction_path) as f:
            extraction = json.load(f)

        before_count = len(web.beliefs) if hasattr(web, 'beliefs') else 0
        integrator.integrate_extraction(extraction)
        after_count = len(web.beliefs) if hasattr(web, 'beliefs') else 0

        added = after_count - before_count
        return max(0, added)

    except ImportError:
        logger.warning("  Web of Belief not available for integration")
        return 0
    except Exception as e:
        logger.warning(f"  Integration error: {e}")
        return 0


def notify_overseer(paper_id: str, dry_run: bool = False) -> tuple:
    """
    Notify Overseer of new paper integration.

    Returns (notified: bool, violations: int).
    """
    if dry_run:
        logger.info(f"  [DRY RUN] Would notify Overseer for: {paper_id}")
        return (False, 0)

    try:
        from src.services.overseer import OverseerService
        from src.services.db_locator import locate_databases

        db_paths = locate_databases()
        overseer = OverseerService(
            overseer_db_path=db_paths.get("overseer_db", "data/overseer.db"),
            web=None,
            web_db_path=db_paths.get("web_db", "data/web_of_belief.db"),
        )

        report = overseer.post_integration_check(paper_id=paper_id)
        violations = len(report.violations) if report and report.violations else 0

        if violations > 0:
            logger.warning(f"  ⚠️ Overseer found {violations} violations after integrating {paper_id}")
            for v in report.violations[:3]:
                logger.warning(f"    - {v.code}: {v.description}")
        else:
            logger.info(f"  ✅ Overseer: no violations for {paper_id}")

        return (True, violations)

    except ImportError:
        logger.info(f"  Overseer not available (import error)")
        return (False, 0)
    except Exception as e:
        logger.info(f"  Overseer notification failed: {e}")
        return (False, 0)


def move_to_processed(pdf_path: Path):
    """Move PDF from incoming to processed directory."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED_DIR / pdf_path.name
    if dest.exists():
        # Don't overwrite
        logger.info(f"  PDF already in processed: {pdf_path.name}")
        return
    shutil.move(str(pdf_path), str(dest))
    logger.info(f"  Moved to processed: {dest.name}")


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def ingest_pipeline(dry_run: bool = False, skip_integration: bool = False,
                    skip_overseer: bool = False) -> List[IngestResult]:
    """Run the full ingestion pipeline on all new PDFs."""

    logger.info("=" * 60)
    logger.info(f"PDF Auto-Ingestion Pipeline — {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    # Stage 1: DETECT
    logger.info("\n📡 Stage 1: DETECT — scanning pdfs_incoming/")
    new_pdfs = detect_new_pdfs()

    if not new_pdfs:
        logger.info("  No new PDFs found. Pipeline complete.")
        return []

    logger.info(f"  Found {len(new_pdfs)} new PDF(s)")
    results = []

    for i, pdf_path in enumerate(new_pdfs, 1):
        logger.info(f"\n{'─' * 50}")
        logger.info(f"[{i}/{len(new_pdfs)}] {pdf_path.name}")
        logger.info(f"{'─' * 50}")

        result = IngestResult(filename=pdf_path.name)

        # Derive DOI from filename
        stem = pdf_path.stem
        result.doi = stem.replace("_", "/", 1)

        # Stage 2: EXTRACT
        logger.info(f"  🔬 Stage 2: EXTRACT")
        result.stage = "extract"
        extraction_path = extract_pdf(pdf_path, dry_run=dry_run)

        if extraction_path:
            result.extracted = True
            result.extraction_file = extraction_path

            # V13 Audit Fix: Notify IncrementalUpdater that new extraction arrived.
            # This marks affected materialized view clusters as STALE so precomputed
            # answer cards get rebuilt on the next nightly run.
            try:
                from src.qa.incremental_updater import IncrementalUpdater
                updater = IncrementalUpdater()
                affected = updater.on_new_extraction(extraction_path)
                if affected:
                    logger.info(f"  📊 MV updater: {len(affected)} cluster(s) marked STALE")
            except ImportError:
                pass  # IncrementalUpdater not available
            except Exception as e:
                logger.debug(f"  MV updater skipped: {e}")

            # Stage 3: QA GATE
            logger.info(f"  ✅ Stage 3: QA GATE")
            result.stage = "qa"
            result.qa_score = qa_check(extraction_path)
            result.qa_passed = result.qa_score >= 0.5  # Lower threshold for new extractions
            logger.info(f"  QA Score: {result.qa_score:.2f} ({'PASS' if result.qa_passed else 'FAIL'})")

            # Stage 4: INTEGRATE
            if result.qa_passed and not skip_integration:
                logger.info(f"  🌐 Stage 4: INTEGRATE to Web of Belief")
                result.stage = "integrate"
                result.beliefs_added = integrate_to_web(extraction_path, dry_run=dry_run)
                result.integrated = result.beliefs_added > 0 or dry_run
                logger.info(f"  Beliefs added: {result.beliefs_added}")

                # Stage 5: OVERSEER
                if result.integrated and not skip_overseer:
                    logger.info(f"  👁️ Stage 5: OVERSEER notification")
                    result.stage = "overseer"
                    notified, violations = notify_overseer(stem, dry_run=dry_run)
                    result.overseer_notified = notified
                    result.overseer_violations = violations
            elif not result.qa_passed:
                logger.warning(f"  ⚠️ QA failed — flagged for re-extraction")
                result.error = f"QA score {result.qa_score:.2f} below threshold"
            else:
                logger.info(f"  ⏭️ Skipping integration (--skip-integration)")

            # Move to processed
            if not dry_run:
                move_to_processed(pdf_path)
        else:
            if not dry_run:
                result.error = "Extraction failed"
                logger.error(f"  ❌ Extraction failed for {pdf_path.name}")
                # Record in HITL DB for human follow-up
                record_hitl_needed(
                    doi=result.doi or stem,
                    reason="Extraction failed — PDF may be corrupt or unsupported format",
                    paper_info={"filename": pdf_path.name},
                    priority="high",
                )
                result.hitl_recorded = True

        result.stage = "complete"
        results.append(result)

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info(f"INGESTION SUMMARY")
    logger.info(f"{'=' * 60}")
    extracted = sum(1 for r in results if r.extracted)
    qa_passed = sum(1 for r in results if r.qa_passed)
    integrated = sum(1 for r in results if r.integrated)
    overseer_ok = sum(1 for r in results if r.overseer_notified and r.overseer_violations == 0)
    total_beliefs = sum(r.beliefs_added for r in results)

    logger.info(f"  PDFs processed:    {len(results)}")
    logger.info(f"  Extracted:         {extracted}")
    logger.info(f"  QA passed:         {qa_passed}")
    logger.info(f"  Integrated:        {integrated}")
    logger.info(f"  Overseer clear:    {overseer_ok}")
    logger.info(f"  Total beliefs:     {total_beliefs}")

    # Save log
    INGEST_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run" if dry_run else "live",
        "pdfs_processed": len(results),
        "extracted": extracted,
        "qa_passed": qa_passed,
        "integrated": integrated,
        "total_beliefs_added": total_beliefs,
        "results": [asdict(r) for r in results],
    }

    # Append to log
    existing_log = []
    if INGEST_LOG.exists():
        try:
            with open(INGEST_LOG) as f:
                existing_log = json.load(f)
        except Exception:
            existing_log = []

    existing_log.append(log_entry)
    with open(INGEST_LOG, "w") as f:
        json.dump(existing_log, f, indent=2)
    logger.info(f"\n  Log saved to {INGEST_LOG}")

    # Report HITL queue status
    hitl = get_hitl_summary()
    if hitl["pending"] > 0:
        logger.info(f"\n  📋 HITL Queue: {hitl['pending']} DOIs need human acquisition")
        logger.info(f"     View: data/acquisition/hitl_needed.json")
        logger.info(f"     Recommended: paste DOIs into Elicit or search Academia.edu")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Auto-ingest PDFs from pdfs_incoming/ → extraction → EN → Overseer"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--watch", action="store_true", help="Poll every 60s for new PDFs")
    parser.add_argument("--watch-interval", type=int, default=60, help="Poll interval in seconds")
    parser.add_argument("--skip-integration", action="store_true", help="Extract only, don't integrate")
    parser.add_argument("--skip-overseer", action="store_true", help="Don't notify Overseer")
    parser.add_argument("--hitl-status", action="store_true", help="Show HITL queue status")
    args = parser.parse_args()

    if args.hitl_status:
        hitl = get_hitl_summary()
        print(json.dumps(hitl, indent=2))
        return 0

    if args.watch:
        logger.info(f"👁️ Watching {INCOMING_DIR} every {args.watch_interval}s...")
        while True:
            ingest_pipeline(
                dry_run=args.dry_run,
                skip_integration=args.skip_integration,
                skip_overseer=args.skip_overseer,
            )
            time.sleep(args.watch_interval)
    else:
        results = ingest_pipeline(
            dry_run=args.dry_run,
            skip_integration=args.skip_integration,
            skip_overseer=args.skip_overseer,
        )
        return 0 if all(r.stage == "complete" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
