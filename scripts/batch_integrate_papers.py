#!/usr/bin/env python3
"""
Batch Paper Integration Script
===============================

Processes paper extractions from data/extractions/ through the
PaperIntegrationOrchestrator, adapting the findings format to claims/rules.

Usage:
    python3 scripts/batch_integrate_papers.py --batch 1
    python3 scripts/batch_integrate_papers.py --batch 1 --dry-run --limit 3
    python3 scripts/batch_integrate_papers.py --batch 1 --db data/web_persistence_v2.db

Created: 2026-02-27
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("batch_integrate")


# =============================================================================
# CONSTANTS
# =============================================================================

MANIFEST_PATH = PROJECT_ROOT / "data" / "extractions" / "batch_manifest.json"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
RESULTS_DIR = PROJECT_ROOT / "data" / "integration_results"
DEFAULT_DB = PROJECT_ROOT / "data" / "web_persistence_v2.db"

# Quality gates
MIN_QUALITY_SCORE = 0.4
MIN_FINDINGS = 1

# Claim types considered empirically substantive
EMPIRICAL_CLAIM_TYPES = {
    "empirical", "causal", "correlational", "experimental",
    "quasi_experimental", "observational", "meta_analytic",
}

# Evidence type weights for ae_confidence derivation
EVIDENCE_TYPE_WEIGHTS = {
    "cited": 0.85,
    "observed": 0.80,
    "experimental": 0.90,
    "statistical": 0.90,
    "claimed": 0.55,
    "theoretical": 0.40,
    "inferred": 0.45,
}

# Claim type → epistemic level
CLAIM_TYPE_TO_LEVEL = {
    "empirical": "EMPIRICAL",
    "causal": "INTERMEDIATE",
    "correlational": "EMPIRICAL",
    "experimental": "EMPIRICAL",
    "quasi_experimental": "EMPIRICAL",
    "observational": "EMPIRICAL",
    "meta_analytic": "EMPIRICAL",
    "theoretical_proposition": "THEORETICAL",
    "review_synthesis": "INTERMEDIATE",
    "mechanistic": "INTERMEDIATE",
}

# Claim type → warrant type
CLAIM_TYPE_TO_WARRANT = {
    "empirical": "EMPIRICAL_ASSOCIATION",
    "causal": "MECHANISM",
    "correlational": "EMPIRICAL_ASSOCIATION",
    "experimental": "MECHANISM",
    "quasi_experimental": "EMPIRICAL_ASSOCIATION",
    "observational": "EMPIRICAL_ASSOCIATION",
    "meta_analytic": "EMPIRICAL_ASSOCIATION",
    "theoretical_proposition": "CONSTITUTIVE",
    "review_synthesis": "EMPIRICAL_ASSOCIATION",
    "mechanistic": "MECHANISM",
}


# =============================================================================
# FINDINGS → CLAIMS ADAPTER
# =============================================================================

def _build_statement(finding: Dict[str, Any]) -> str:
    """Build a human-readable statement from a finding's antecedent/consequent."""
    ant = finding.get("antecedent", "Unknown factor")
    con = finding.get("consequent", "Unknown outcome")
    direction = finding.get("direction", "unclear")

    direction_verb = {
        "increase": "increases",
        "decrease": "decreases",
        "unclear": "is associated with",
        "no_effect": "has no significant effect on",
        "mixed": "has mixed effects on",
        "modulates": "modulates",
    }.get(direction, "is associated with")

    return f"{ant} {direction_verb} {con}"


def _derive_confidence(
    finding: Dict[str, Any], paper_quality: float
) -> float:
    """
    Derive an ae_confidence score for a finding.

    Combines:
    - Paper-level quality_score (0–1)
    - Evidence type weight
    - Presence of effect size / p-value (bonus)
    """
    evidence_type = finding.get("evidence_type", "claimed")
    ev_weight = EVIDENCE_TYPE_WEIGHTS.get(evidence_type, 0.50)

    base = paper_quality * 0.4 + ev_weight * 0.4

    # Bonus for statistical evidence
    if finding.get("effect_size") is not None:
        base += 0.10
    if finding.get("p_value") is not None:
        base += 0.05
    if finding.get("sample_size") and finding["sample_size"] > 0:
        base += 0.05

    return min(0.95, max(0.10, base))


def finding_to_claim(
    finding: Dict[str, Any],
    paper_doi: str,
    paper_quality: float,
) -> Dict[str, Any]:
    """
    Adapt an extraction finding to the claims format expected by
    PaperIntegrationOrchestrator._step_map_extraction().
    """
    finding_id = finding.get("id", uuid.uuid4().hex[:8])
    claim_type = finding.get("claim_type") or "theoretical_proposition"

    statement = _build_statement(finding)
    claim_text = finding.get("quote", statement)
    confidence = _derive_confidence(finding, paper_quality)

    return {
        "node_id": f"b_{paper_doi}_{finding_id}",
        "statement": statement,
        "claim_text": claim_text,
        "ae_confidence": confidence,
        "confidence_se": 0.15,  # Default uncertainty
        "evidence_level": CLAIM_TYPE_TO_LEVEL.get(claim_type, "EMPIRICAL"),
        "construct_id": None,  # Could be extracted from finding fields
        "dependent_variable": finding.get("consequent"),
        "independent_variable": finding.get("antecedent"),
        "effect_size_d": finding.get("effect_size"),
        "theory_names": finding.get("theory_links", []),
        # Preserve original finding data for provenance
        "_finding": finding,
        "_warrant_type": CLAIM_TYPE_TO_WARRANT.get(claim_type, "EMPIRICAL_ASSOCIATION"),
    }


def findings_to_rules(
    findings: List[Dict[str, Any]],
    paper_doi: str,
) -> List[Dict[str, Any]]:
    """
    Build constraint/rule edges from findings that reference templates
    or have causal relationships between findings.
    """
    rules = []

    for finding in findings:
        template_ids = finding.get("template_ids", [])
        finding_id = finding.get("id", uuid.uuid4().hex[:8])
        source_node = f"b_{paper_doi}_{finding_id}"

        for tid in template_ids:
            # Create a SUPPORTS constraint between the finding and the template
            rules.append({
                "edge_id": f"c_{paper_doi}_{finding_id}_to_{tid}",
                "source_node": source_node,
                "target_node": f"template_{tid}",
                "constraint_type": "SUPPORTS",
                "strength": 0.6,
                "paper_id": paper_doi,
            })

    return rules


# =============================================================================
# QUALITY EVALUATION
# =============================================================================

def evaluate_paper_quality(
    extraction: Dict[str, Any],
) -> Tuple[str, Optional[str], Dict[str, Any]]:
    """
    Evaluate whether a paper extraction should be integrated or skipped.

    Returns:
        (status, skip_reason, quality_details)
        where status is 'integrate' or 'skip'
    """
    quality_score = extraction.get("quality_score", 0.0)
    n_findings = extraction.get("n_findings", 0)
    findings = extraction.get("findings", [])
    quality_action = extraction.get("quality_action", "accept")
    article_type = extraction.get("detected_article_type", "unknown")
    family = extraction.get("detected_family", "unknown")

    details = {
        "quality_score": quality_score,
        "n_findings": n_findings,
        "quality_action": quality_action,
        "article_type": article_type,
        "family": family,
    }

    # Gate 1: quality_action rejection
    if quality_action == "reject":
        return "skip", "quality_rejected", details

    # Gate 2: minimum quality score
    if quality_score < MIN_QUALITY_SCORE:
        return "skip", "low_quality_score", details

    # Gate 3: must have at least 1 finding
    if n_findings < MIN_FINDINGS or len(findings) < MIN_FINDINGS:
        return "skip", "too_few_findings", details

    # Gate 4: Check for substantive findings
    empirical_count = 0
    theoretical_with_template = 0

    for f in findings:
        ct = (f.get("claim_type") or "").lower()
        if ct in EMPIRICAL_CLAIM_TYPES:
            empirical_count += 1
        elif ct == "theoretical_proposition" and f.get("template_ids"):
            theoretical_with_template += 1

    substantive = empirical_count + theoretical_with_template
    details["empirical_findings"] = empirical_count
    details["theoretical_with_templates"] = theoretical_with_template
    details["substantive_findings"] = substantive

    # Allow papers with at least some grounded content
    # Theoretical papers are fine if they reference templates
    if substantive == 0 and n_findings > 0:
        # Still accept if there are enough theoretical propositions
        # (some foundational theoretical papers are pure theory but valuable)
        theoretical_count = sum(
            1 for f in findings
            if (f.get("claim_type") or "").lower() == "theoretical_proposition"
        )
        if theoretical_count >= 3:
            details["note"] = "accepted_as_theoretical_foundation"
            return "integrate", None, details
        return "skip", "no_substantive_findings", details

    return "integrate", None, details


# =============================================================================
# TEMPLATE MATCHING & ANNOTATIONS
# =============================================================================

def load_template_ids() -> set:
    """Load all template IDs from data/templates/."""
    ids = set()
    if TEMPLATES_DIR.exists():
        for f in TEMPLATES_DIR.glob("*.json"):
            # Template ID is the filename stem
            ids.add(f.stem)
    return ids


def assess_template_matches(
    findings: List[Dict[str, Any]],
    known_templates: set,
) -> Dict[str, List[str]]:
    """
    For each finding, check which templates it connects to.
    Returns {finding_id: [matched_template_ids]}.
    """
    matches = {}
    for finding in findings:
        fid = str(finding.get("id", "?"))
        tids = finding.get("template_ids", [])
        matched = [t for t in tids if t in known_templates]
        if matched:
            matches[fid] = matched
    return matches


def generate_annotations(
    findings: List[Dict[str, Any]],
    paper_doi: str,
) -> List[Dict[str, Any]]:
    """
    Generate annotations for notable findings:
    - SENSITIVITY_FLAG for variable parameters
    - OPEN_QUESTION for gaps
    - CONTRADICTION for direction conflicts
    """
    annotations = []

    for finding in findings:
        fid = finding.get("id", "?")

        # Sensitivity: findings with moderators or mixed direction
        if finding.get("moderators_reported"):
            annotations.append({
                "type": "SENSITIVITY_FLAG",
                "finding_id": fid,
                "paper_doi": paper_doi,
                "reason": f"Moderators reported: {finding['moderators_reported']}",
            })

        if finding.get("direction") == "mixed":
            annotations.append({
                "type": "SENSITIVITY_FLAG",
                "finding_id": fid,
                "paper_doi": paper_doi,
                "reason": "Mixed direction — result depends on conditions",
            })

        # Open question: findings with unclear mechanism
        if finding.get("mechanism") is None and finding.get("claim_type") == "causal":
            annotations.append({
                "type": "OPEN_QUESTION",
                "finding_id": fid,
                "paper_doi": paper_doi,
                "reason": "Causal claim with no mechanism specified",
            })

    return annotations


# =============================================================================
# BATCH ORCHESTRATION
# =============================================================================

def process_single_paper(
    extraction_path: Path,
    db_conn: sqlite3.Connection,
    known_templates: set,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Process a single paper extraction through the pipeline.

    Returns a result dict suitable for the batch results file.
    """
    with open(extraction_path, "r") as f:
        extraction = json.load(f)

    paper_doi = extraction.get("doi", extraction_path.stem)
    title = extraction.get("title", extraction.get("crossref_title", "Unknown"))
    findings = extraction.get("findings", [])

    result = {
        "doi": paper_doi,
        "title": title,
        "extraction_file": extraction_path.name,
        "n_findings_total": len(findings),
    }

    # Step 1: Quality evaluation
    status, skip_reason, quality_details = evaluate_paper_quality(extraction)
    result["quality"] = quality_details

    if status == "skip":
        result["status"] = "skipped"
        result["skip_reason"] = skip_reason
        result["n_integrated"] = 0
        result["n_skipped"] = len(findings)
        result["template_matches"] = {}
        result["notes"] = f"Skipped: {skip_reason}"
        return result

    # Step 2: Template matching assessment
    template_matches = assess_template_matches(findings, known_templates)
    result["template_matches"] = template_matches

    # Step 3: Generate annotations
    annotations = generate_annotations(findings, paper_doi)
    result["annotations"] = annotations

    # Step 4: Adapt findings → claims
    paper_quality = extraction.get("quality_score", 0.5)
    claims = [
        finding_to_claim(f, paper_doi, paper_quality)
        for f in findings
    ]
    rules = findings_to_rules(findings, paper_doi)

    result["n_claims_generated"] = len(claims)
    result["n_rules_generated"] = len(rules)

    # Step 5: Warrant type distribution
    warrant_dist = {}
    for c in claims:
        wt = c.get("_warrant_type", "UNKNOWN")
        warrant_dist[wt] = warrant_dist.get(wt, 0) + 1
    result["warrant_distribution"] = warrant_dist

    if dry_run:
        result["status"] = "dry_run"
        result["n_integrated"] = 0
        result["n_skipped"] = 0
        result["notes"] = "Dry run — no database writes"
        # Show a sample claim for inspection
        if claims:
            result["sample_claim"] = {
                k: v for k, v in claims[0].items()
                if k != "_finding"
            }
        return result

    # Step 6: Run through the orchestrator
    try:
        from src.services.paper_integration.orchestrator import (
            PaperIntegrationOrchestrator,
        )

        orchestrator = PaperIntegrationOrchestrator(
            db_conn=db_conn,
            web=None,  # Direct mapping mode for bulk import
            template_dir=str(TEMPLATES_DIR),
            molecule_dir=str(PROJECT_ROOT / "data" / "molecules"),
            theory_dir=str(PROJECT_ROOT / "data" / "theories"),
        )

        event = orchestrator.integrate_paper(
            paper_id=paper_doi,
            extraction_data={"claims": claims, "rules": rules},
            paper_metadata={
                "title": title,
                "doi": paper_doi,
                "year": extraction.get("crossref_year"),
                "journal": extraction.get("crossref_journal", extraction.get("journal")),
                "citation_count": extraction.get("crossref_citation_count"),
                "article_type": extraction.get("detected_article_type"),
            },
        )

        result["status"] = event.status.value if hasattr(event.status, 'value') else str(event.status)
        result["n_integrated"] = len(event.beliefs_added)
        result["n_skipped"] = len(findings) - len(event.beliefs_added)
        result["beliefs_added"] = event.beliefs_added[:5]  # First 5 for reference
        result["constraints_added"] = len(event.constraints_added)
        result["molecules_affected"] = event.molecules_affected
        result["notes"] = "Integrated via PaperIntegrationOrchestrator"

        # Check for already-integrated (idempotency)
        if result["status"] == "completed" and result["n_integrated"] == 0:
            result["notes"] = "Already integrated (idempotent skip)"

    except Exception as e:
        logger.error("Orchestrator failed for %s: %s", paper_doi, e, exc_info=True)
        result["status"] = "error"
        result["error"] = str(e)
        result["n_integrated"] = 0
        result["n_skipped"] = len(findings)
        result["notes"] = f"Orchestrator error: {e}"

    return result


def run_batch(
    batch_num: int,
    db_path: str = str(DEFAULT_DB),
    dry_run: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run paper integration for an entire batch.

    Returns the full results dict.
    """
    # Load manifest
    if not MANIFEST_PATH.exists():
        logger.error("Batch manifest not found at %s", MANIFEST_PATH)
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    # Find the batch
    batch = None
    for b in manifest["batches"]:
        if b["batch_id"] == batch_num:
            batch = b
            break

    if batch is None:
        logger.error("Batch %d not found in manifest", batch_num)
        sys.exit(1)

    files = batch["files"]
    if limit:
        files = files[:limit]

    logger.info(
        "=== BATCH %d: Processing %d papers (of %d in batch) ===",
        batch_num, len(files), batch["count"],
    )

    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Create DB backup before processing (skip for dry run)
    db_file = Path(db_path)
    if not dry_run and db_file.exists():
        backup_name = f"{db_file.stem}.backup_before_batch{batch_num}_{datetime.now().strftime('%Y%m%d_%H%M')}{db_file.suffix}"
        backup_path = db_file.parent / backup_name
        if not backup_path.exists():
            shutil.copy2(db_file, backup_path)
            logger.info("DB backup created: %s", backup_path.name)

    # Connect to database
    if dry_run:
        # For dry run, use in-memory DB (no actual writes needed)
        db_conn = sqlite3.connect(":memory:")
        logger.info("Dry-run mode: using in-memory database")
    else:
        if not db_file.exists():
            logger.error("Database not found at %s", db_path)
            sys.exit(1)
        db_conn = sqlite3.connect(db_path)
        db_conn.execute("PRAGMA journal_mode=WAL")
        db_conn.execute("PRAGMA busy_timeout=5000")

    # Load template IDs for matching
    known_templates = load_template_ids()
    logger.info("Loaded %d template IDs from %s", len(known_templates), TEMPLATES_DIR)

    # Process each paper
    results = {}
    stats = {"integrated": 0, "skipped": 0, "errors": 0, "dry_run": 0}
    total_findings = 0
    total_integrated_findings = 0

    for i, filename in enumerate(files, 1):
        extraction_path = EXTRACTIONS_DIR / filename
        if not extraction_path.exists():
            logger.warning("[%d/%d] File not found: %s", i, len(files), filename)
            results[filename] = {
                "status": "error",
                "error": "extraction file not found",
                "n_findings": 0,
                "n_integrated": 0,
                "n_skipped": 0,
            }
            stats["errors"] += 1
            continue

        logger.info("[%d/%d] Processing: %s", i, len(files), filename)

        try:
            result = process_single_paper(
                extraction_path, db_conn, known_templates, dry_run
            )
            paper_key = result.get("doi", filename)
            results[paper_key] = result

            status = result.get("status", "unknown")
            if status == "skipped":
                stats["skipped"] += 1
            elif status == "dry_run":
                stats["dry_run"] += 1
            elif status in ("completed", "integrated"):
                stats["integrated"] += 1
                total_integrated_findings += result.get("n_integrated", 0)
            else:
                stats["errors"] += 1

            total_findings += result.get("n_findings_total", 0)

        except Exception as e:
            logger.error("[%d/%d] Unexpected error processing %s: %s",
                         i, len(files), filename, e, exc_info=True)
            results[filename] = {
                "status": "error",
                "error": str(e),
                "n_findings": 0,
                "n_integrated": 0,
                "n_skipped": 0,
            }
            stats["errors"] += 1

    db_conn.close()

    # Write results
    results_file = RESULTS_DIR / f"batch_{batch_num}_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info("Results written to: %s", results_file)

    # Summary
    print("\n" + "=" * 60)
    print(f"BATCH {batch_num} SUMMARY")
    print("=" * 60)
    print(f"  Total papers processed:  {len(results)}")
    print(f"  Integrated:              {stats['integrated']}")
    print(f"  Skipped:                 {stats['skipped']}")
    print(f"  Errors:                  {stats['errors']}")
    if dry_run:
        print(f"  Dry run:                 {stats['dry_run']}")
    print(f"  Total findings seen:     {total_findings}")
    print(f"  Total findings integrated: {total_integrated_findings}")
    print(f"  Results file:            {results_file}")
    print("=" * 60)

    # Quality distribution of skipped papers
    skip_reasons = {}
    for r in results.values():
        if r.get("status") == "skipped":
            reason = r.get("skip_reason", "unknown")
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1

    if skip_reasons:
        print("\nSkip reason distribution:")
        for reason, count in sorted(skip_reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Batch integrate paper extractions into Web of Belief"
    )
    parser.add_argument(
        "--batch", type=int, required=True,
        help="Batch number (1-11) from the manifest"
    )
    parser.add_argument(
        "--db", type=str, default=str(DEFAULT_DB),
        help=f"Path to SQLite database (default: {DEFAULT_DB})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Evaluate papers but don't write to database"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit processing to first N papers in the batch"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    run_batch(
        batch_num=args.batch,
        db_path=args.db,
        dry_run=args.dry_run,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
