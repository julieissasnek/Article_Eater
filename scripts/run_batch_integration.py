#!/usr/bin/env python3
"""
Batch Paper Integration Script
================================

Created: 2026-02-27
Sprint: INTEGRATION-1

Drives the PaperIntegrationOrchestrator for a batch of papers from the
batch manifest. Designed for parallel execution across multiple AG instances.

Usage:
    python scripts/run_batch_integration.py --batch 1
    python scripts/run_batch_integration.py --batch 1 --dry-run
    python scripts/run_batch_integration.py --batch 1 --paper-limit 5

Safety:
    - SQLite WAL mode for concurrent access
    - Idempotent: re-running skips already-integrated papers
    - Per-paper error isolation: one failure doesn't stop the batch
"""

from __future__ import annotations

import argparse
import json
import math
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
EXTRACTIONS_DIR = DATA_DIR / "extractions"
RESULTS_DIR = DATA_DIR / "integration_results"
MANIFEST_PATH = EXTRACTIONS_DIR / "batch_manifest.json"
DB_PATH = DATA_DIR / "web_persistence_v2.db"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BATCH] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ===========================================================================
# QUALITY ASSESSMENT
# ===========================================================================

class QualityVerdict:
    """Result of evaluating a paper extraction's quality."""

    def __init__(
        self,
        accept: bool,
        skip_reason: Optional[str] = None,
        quality_tier: str = "unknown",
        notes: List[str] = None,
    ):
        self.accept = accept
        self.skip_reason = skip_reason
        self.quality_tier = quality_tier  # high, medium, low
        self.notes = notes or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accept": self.accept,
            "skip_reason": self.skip_reason,
            "quality_tier": self.quality_tier,
            "notes": self.notes,
        }


def assess_quality(extraction: Dict[str, Any]) -> QualityVerdict:
    """
    Evaluate whether a paper extraction is worth integrating.

    Criteria:
    - quality_action must be "accept"
    - Must have >= 3 findings
    - quality_score must be >= 0.4
    - Papers with no effect sizes are flagged (not skipped) but get lower tier
    """
    notes: List[str] = []

    # Check quality_action
    quality_action = extraction.get("quality_action", "unknown")
    if quality_action != "accept":
        return QualityVerdict(
            accept=False,
            skip_reason=f"rejected_by_extraction (quality_action={quality_action})",
            quality_tier="rejected",
        )

    # Check number of findings
    findings = extraction.get("findings", [])
    n_findings = len(findings)
    if n_findings < 3:
        return QualityVerdict(
            accept=False,
            skip_reason=f"too_few_findings (n={n_findings})",
            quality_tier="low",
        )

    # Check quality score
    quality_score = extraction.get("quality_score", 0.0)
    if quality_score < 0.4:
        return QualityVerdict(
            accept=False,
            skip_reason=f"low_quality_score ({quality_score:.2f})",
            quality_tier="low",
        )

    # Classify quality tier
    detected_family = extraction.get("detected_family", "unknown")
    has_effect_sizes = any(
        f.get("effect_size") is not None for f in findings if isinstance(f, dict)
    )
    has_p_values = any(f.get("p_value") is not None for f in findings if isinstance(f, dict))

    if has_effect_sizes and has_p_values and quality_score >= 0.7:
        tier = "high"
    elif (has_effect_sizes or has_p_values) and quality_score >= 0.5:
        tier = "medium"
    else:
        tier = "low"

    # Build notes
    article_type = extraction.get("detected_article_type", "unknown")
    notes.append(f"article_type={article_type}")
    notes.append(f"family={detected_family}")

    if not has_effect_sizes:
        notes.append("no_effect_sizes (theoretical contribution)")
    if not has_p_values:
        notes.append("no_p_values")

    # Count claim types
    claim_types: Dict[str, int] = {}
    for f in findings:
        if not isinstance(f, dict):
            continue
        ct = f.get("claim_type", "unknown")
        claim_types[ct] = claim_types.get(ct, 0) + 1
    dominant_claim_type = max(claim_types, key=claim_types.get) if claim_types else "unknown"
    notes.append(f"dominant_claim_type={dominant_claim_type}")

    return QualityVerdict(
        accept=True,
        quality_tier=tier,
        notes=notes,
    )


# ===========================================================================
# CONFIDENCE HELPERS
# ===========================================================================

def _citation_bonus(citation_count) -> float:
    """
    Log-scaled confidence bonus from citation count.

    10 cites → +0.05,  100 → +0.10,  1000+ → +0.15 (capped).
    Aligns with Quinean entrenchment: highly-cited beliefs are harder to dislodge.
    """
    if not citation_count or citation_count <= 0:
        return 0.0
    return min(0.15, 0.05 * math.log10(max(1, citation_count)))


# ===========================================================================
# FINDINGS → CLAIMS CONVERSION
# ===========================================================================

def convert_findings_to_claims(
    extraction: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Convert extraction findings to the ae.claim.v1 + ae.rule.v1 format
    expected by the PaperIntegrationOrchestrator.

    Mirrors the transformation in system_setup.py _phase_4_web_insertion.
    """
    doi = extraction.get("doi", "unknown")
    findings = extraction.get("findings", [])
    pm = extraction.get("paper_metadata", {})

    claims: List[Dict[str, Any]] = []
    rules: List[Dict[str, Any]] = []

    for i, f in enumerate(findings):
        finding_id = f.get("id", i)

        # Build the claim statement from antecedent → consequent
        antecedent = f.get("antecedent", "")
        consequent = f.get("consequent", "")
        direction = f.get("direction", "unspecified")
        statement = f"{antecedent} → {consequent} ({direction})"

        # Compute confidence: base + p-value bonus + citation bonus
        cite_count = extraction.get("crossref_citation_count", 0)
        base_confidence = 0.6 if f.get("p_value") else 0.4
        ae_confidence = min(0.85, base_confidence + _citation_bonus(cite_count))

        claim = {
            "claim_id": f"{doi}__f{finding_id}",
            "node_id": f"{doi}__f{finding_id}",
            "paper_id": doi,
            "claim_type": _map_claim_type(f.get("claim_type", "")),
            "statement": statement,
            "claim_text": statement,
            "ae_confidence": ae_confidence,
            "confidence_se": 0.2,
            "constructs": {
                "environment_factors": [{"id": antecedent, "role": "independent"}],
                "outcomes": [{"id": consequent, "role": "dependent"}],
                "mediators": [],
                "moderators": [
                    {"id": m, "value": None}
                    for m in (f.get("moderators_reported") or [])
                ],
            },
            "construct_id": (f.get("template_ids") or [None])[0] if f.get("template_ids") else None,
            "dependent_variable": consequent,
            "independent_variable": antecedent,
            "effect_size_d": f.get("effect_size"),
            "theory_names": f.get("theory_links") or [],
            "evidence_level": _map_evidence_level(f),
            "study": {
                "design": f.get("measure_type") or "unknown",
                "sample": {
                    "n": f.get("sample_size"),
                    "population": None,
                    "age_mean": None,
                    "country": None,
                },
                "task": {
                    "description": f.get("source", ""),
                    "type": "unknown",
                },
                "setting": {},
            },
            "statistics": {
                "effect_size": {
                    "type": f.get("effect_size_type"),
                    "value": f.get("effect_size"),
                },
                "p_value": f.get("p_value"),
                "ci95": None,
            },
            "evidence": [{
                "kind": "span",
                "source": f.get("source"),
                "note": f.get("quote", "")[:200] if f.get("quote") else None,
            }],
            "constraints": [],
            # Bibliographic metadata
            "publication_year": pm.get("year"),
            "publication_authors": pm.get("authors", []),
            "publication_journal": pm.get("journal", ""),
            "citation_count": pm.get("citation_count"),
        }
        claims.append(claim)

        # Create rules from theory_links → constraints
        for theory in (f.get("theory_links") or []):
            rules.append({
                "rule_id": f"{doi}__r{finding_id}_{theory}",
                "edge_id": f"{doi}__r{finding_id}_{theory}",
                "paper_id": doi,
                "source_node": f"{doi}__f{finding_id}",
                "source_claim_id": f"{doi}__f{finding_id}",
                "target_node": theory,
                "target_theory": theory,
                "constraint_type": (
                    "SUPPORTS" if direction in ("increase", "positive")
                    else "INFORMS"
                ),
                "relationship": (
                    "supports" if direction in ("increase", "positive")
                    else "informs"
                ),
                "strength": 0.5,
            })

    return claims, rules


def _map_claim_type(raw: str) -> str:
    """Map extraction claim_type to the pipeline's canonical types."""
    mapping = {
        "empirical": "EMPIRICAL",
        "causal": "CAUSAL",
        "correlational": "CORRELATIONAL",
        "theoretical_proposition": "THEORETICAL",
        "meta_analytic": "META_ANALYTIC",
        "descriptive": "DESCRIPTIVE",
    }
    return mapping.get(raw.lower(), "UNSPECIFIED") if raw else "UNSPECIFIED"


def _map_evidence_level(finding: Dict[str, Any]) -> str:
    """Map finding characteristics to epistemic level."""
    evidence_type = finding.get("evidence_type", "")
    claim_type = finding.get("claim_type", "")

    if claim_type == "meta_analytic":
        return "META_ANALYTIC"
    elif evidence_type in ("empirical", "measured") or finding.get("p_value"):
        return "EMPIRICAL"
    elif evidence_type == "cited":
        return "OBSERVATIONAL"
    elif evidence_type in ("theoretical", "claimed"):
        return "THEORETICAL"
    else:
        return "OBSERVATIONAL"


# ===========================================================================
# BATCH PROCESSOR
# ===========================================================================

class BatchProcessor:
    """Process a batch of papers through the integration pipeline."""

    def __init__(
        self,
        batch_id: int,
        db_path: Path = DB_PATH,
        dry_run: bool = False,
        paper_limit: Optional[int] = None,
    ):
        self.batch_id = batch_id
        self.db_path = db_path
        self.dry_run = dry_run
        self.paper_limit = paper_limit

        # Load manifest
        with open(MANIFEST_PATH) as f:
            self.manifest = json.load(f)

        # Find our batch
        self.batch_info = None
        for batch in self.manifest["batches"]:
            if batch["batch_id"] == batch_id:
                self.batch_info = batch
                break

        if self.batch_info is None:
            raise ValueError(
                f"Batch {batch_id} not found in manifest. "
                f"Available: {[b['batch_id'] for b in self.manifest['batches']]}"
            )

        self.files = self.batch_info["files"]
        if self.paper_limit:
            self.files = self.files[:self.paper_limit]

        # Results tracking
        self.results: Dict[str, Dict[str, Any]] = {}
        self.summary = {
            "total_papers": len(self.files),
            "integrated": 0,
            "skipped": 0,
            "failed": 0,
            "already_integrated": 0,
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
        }

    def run(self) -> Dict[str, Any]:
        """Execute the batch integration."""
        logger.info("=" * 70)
        logger.info(
            "BATCH %d: Processing %d papers (files %d–%d)",
            self.batch_id,
            len(self.files),
            self.batch_info["start"],
            self.batch_info["end"],
        )
        if self.dry_run:
            logger.info("  ** DRY RUN — no database writes **")
        logger.info("=" * 70)

        start_time = time.time()

        # Open database connection
        db_conn = None
        orchestrator = None

        if not self.dry_run:
            db_conn = sqlite3.connect(str(self.db_path))
            db_conn.execute("PRAGMA journal_mode=WAL")
            db_conn.execute("PRAGMA busy_timeout=30000")

            # Ensure required tables exist
            self._ensure_tables(db_conn)

            # Initialize orchestrator
            try:
                from src.services.paper_integration.orchestrator import (
                    PaperIntegrationOrchestrator,
                )
                orchestrator = PaperIntegrationOrchestrator(
                    db_conn=db_conn,
                    template_dir=str(DATA_DIR / "templates"),
                    molecule_dir=str(DATA_DIR / "molecules"),
                    theory_dir=str(DATA_DIR / "theories"),
                )
                logger.info("Orchestrator initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize orchestrator: %s", e)
                if db_conn:
                    db_conn.close()
                raise

        # Process each paper
        for i, filename in enumerate(self.files):
            paper_num = i + 1
            doi = filename.replace(".json", "").replace("_", "/")

            logger.info(
                "\n--- Paper %d/%d: %s ---",
                paper_num, len(self.files), doi,
            )

            try:
                result = self._process_paper(
                    filename, doi, orchestrator, db_conn,
                )
                self.results[doi] = result

                # Update summary
                status = result["status"]
                if status == "integrated":
                    self.summary["integrated"] += 1
                elif status == "skipped":
                    self.summary["skipped"] += 1
                elif status == "already_integrated":
                    self.summary["already_integrated"] += 1
                elif status == "failed":
                    self.summary["failed"] += 1

                tier = result.get("quality_tier", "low")
                if tier in self.summary["quality_distribution"]:
                    self.summary["quality_distribution"][tier] += 1

            except Exception as e:
                logger.error("  UNHANDLED ERROR for %s: %s", doi, e)
                self.results[doi] = {
                    "status": "failed",
                    "error": str(e),
                    "n_findings": 0,
                    "n_integrated": 0,
                    "n_skipped": 0,
                }
                self.summary["failed"] += 1

        # Close database
        if db_conn:
            db_conn.close()

        elapsed = time.time() - start_time

        # Write results
        output = {
            "batch_id": self.batch_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "dry_run": self.dry_run,
            "summary": self.summary,
            "papers": self.results,
        }

        self._write_results(output)
        self._print_summary(elapsed)

        return output

    def _process_paper(
        self,
        filename: str,
        doi: str,
        orchestrator,
        db_conn,
    ) -> Dict[str, Any]:
        """Process a single paper extraction."""
        extraction_path = EXTRACTIONS_DIR / filename

        # Load extraction
        if not extraction_path.exists():
            logger.warning("  File not found: %s", extraction_path)
            return {
                "status": "failed",
                "error": f"file_not_found: {filename}",
                "n_findings": 0,
                "n_integrated": 0,
                "n_skipped": 0,
            }

        with open(extraction_path) as f:
            extraction = json.load(f)

        n_findings = extraction.get("n_findings", len(extraction.get("findings", [])))
        quality_score = extraction.get("quality_score", 0.0)

        # Assess quality
        verdict = assess_quality(extraction)
        logger.info(
            "  Quality: %s (tier=%s, score=%.2f, findings=%d)",
            "ACCEPT" if verdict.accept else "SKIP",
            verdict.quality_tier,
            quality_score,
            n_findings,
        )

        if not verdict.accept:
            logger.info("  Skip reason: %s", verdict.skip_reason)
            return {
                "status": "skipped",
                "n_findings": n_findings,
                "n_integrated": 0,
                "n_skipped": n_findings,
                "skip_reason": verdict.skip_reason,
                "quality_score": quality_score,
                "quality_tier": verdict.quality_tier,
                "template_matches": [],
                "notes": verdict.notes,
            }

        # Convert findings to claims/rules format
        claims, rules = convert_findings_to_claims(extraction)
        logger.info("  Converted: %d claims, %d rules", len(claims), len(rules))

        # Collect template matches from findings
        template_matches = set()
        for f in extraction.get("findings", []):
            if isinstance(f, dict):
                template_matches.update(f.get("template_ids") or [])
        template_matches = sorted(template_matches)

        if self.dry_run:
            logger.info("  [DRY RUN] Would integrate %d claims, %d rules", len(claims), len(rules))
            return {
                "status": "would_integrate",
                "n_findings": n_findings,
                "n_integrated": len(claims),
                "n_skipped": 0,
                "skip_reason": None,
                "quality_score": quality_score,
                "quality_tier": verdict.quality_tier,
                "template_matches": template_matches,
                "notes": verdict.notes,
            }

        # Run the orchestrator
        try:
            extraction_data = {
                "claims": claims,
                "rules": rules,
                "doi": doi,
                "title": extraction.get("title", ""),
                "authors": extraction.get("authors", ""),
            }

            event = orchestrator.integrate_paper(
                paper_id=doi,
                extraction_data=extraction_data,
                paper_metadata=extraction.get("paper_metadata", {}),
            )

            status_value = event.status.value if hasattr(event.status, "value") else str(event.status)

            if status_value == "COMPLETED":
                logger.info(
                    "  ✓ Integrated: %d beliefs, %d constraints",
                    len(event.beliefs_added),
                    len(event.constraints_added),
                )
                return {
                    "status": "integrated",
                    "n_findings": n_findings,
                    "n_integrated": len(event.beliefs_added),
                    "n_skipped": max(0, n_findings - len(event.beliefs_added)),
                    "skip_reason": None,
                    "quality_score": quality_score,
                    "quality_tier": verdict.quality_tier,
                    "template_matches": template_matches,
                    "beliefs_added": len(event.beliefs_added),
                    "constraints_added": len(event.constraints_added),
                    "molecules_affected": list(event.molecules_affected),
                    "notes": verdict.notes,
                }
            else:
                logger.warning(
                    "  ⚠ Integration status: %s — %s",
                    status_value,
                    event.error_log or "no error details",
                )
                return {
                    "status": "failed",
                    "n_findings": n_findings,
                    "n_integrated": len(event.beliefs_added),
                    "n_skipped": 0,
                    "skip_reason": None,
                    "quality_score": quality_score,
                    "quality_tier": verdict.quality_tier,
                    "template_matches": template_matches,
                    "error": event.error_log,
                    "notes": verdict.notes,
                }

        except Exception as e:
            logger.error("  ✗ Integration failed: %s", e)
            return {
                "status": "failed",
                "n_findings": n_findings,
                "n_integrated": 0,
                "n_skipped": 0,
                "error": str(e),
                "quality_score": quality_score,
                "quality_tier": verdict.quality_tier,
                "template_matches": template_matches,
                "notes": verdict.notes,
            }

    def _ensure_tables(self, db_conn: sqlite3.Connection) -> None:
        """Ensure all required tables exist in the database."""
        cursor = db_conn.cursor()

        # Core tables needed by the orchestrator
        # Schema matches production web_persistence.py
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS beliefs (
                belief_id TEXT PRIMARY KEY,
                web_id TEXT DEFAULT 'master',
                content TEXT,
                credence_value REAL DEFAULT 0.5,
                credence_uncertainty REAL DEFAULT 0.2,
                level TEXT DEFAULT 'EMPIRICAL',
                status TEXT DEFAULT 'ACCEPTED',
                paper_ids TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS constraints (
                constraint_id TEXT PRIMARY KEY,
                web_id TEXT DEFAULT 'master',
                source_id TEXT,
                target_id TEXT,
                constraint_type TEXT DEFAULT 'SUPPORTS',
                strength REAL DEFAULT 0.5,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS paper_integration_events (
                event_id TEXT PRIMARY KEY,
                paper_id TEXT,
                timestamp TEXT,
                action TEXT,
                status TEXT,
                pre_snapshot_id TEXT,
                post_snapshot_id TEXT,
                beliefs_added TEXT,
                beliefs_retired TEXT,
                constraints_added TEXT,
                constraints_retired TEXT,
                bn_edges_updated TEXT,
                molecules_affected TEXT,
                tags_assigned TEXT,
                cascade_log TEXT,
                supersedes_paper_id TEXT,
                supersession_records TEXT,
                error_log TEXT,
                rollback_of_event_id TEXT
            );

            CREATE TABLE IF NOT EXISTS belief_versions (
                version_id TEXT PRIMARY KEY,
                belief_id TEXT,
                paper_id TEXT,
                timestamp TEXT,
                credence_mean REAL,
                credence_se REAL,
                status TEXT,
                scope_json TEXT,
                is_current INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS web_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS tag_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                belief_id TEXT,
                tag_dimension TEXT,
                tag_value TEXT,
                paper_id TEXT,
                confidence REAL DEFAULT 0.0,
                timestamp TEXT
            );
        """)
        db_conn.commit()

    def _write_results(self, output: Dict[str, Any]) -> None:
        """Write results to the integration_results directory."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result_path = RESULTS_DIR / f"batch_{self.batch_id}_results.json"
        with open(result_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        logger.info("\nResults written to: %s", result_path)

    def _print_summary(self, elapsed: float) -> None:
        """Print a summary of the batch processing."""
        s = self.summary
        logger.info("\n" + "=" * 70)
        logger.info("BATCH %d SUMMARY", self.batch_id)
        logger.info("=" * 70)
        logger.info("  Total papers:        %d", s["total_papers"])
        logger.info("  Integrated:          %d", s["integrated"])
        logger.info("  Skipped:             %d", s["skipped"])
        logger.info("  Already integrated:  %d", s["already_integrated"])
        logger.info("  Failed:              %d", s["failed"])
        logger.info("  Quality distribution:")
        for tier, count in s["quality_distribution"].items():
            logger.info("    %-8s %d", tier, count)
        logger.info("  Elapsed:             %.1f seconds", elapsed)
        logger.info("=" * 70)


# ===========================================================================
# CLI
# ===========================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run batch paper integration for the ATLAS Web of Belief.",
    )
    parser.add_argument(
        "--batch", type=int, required=True,
        help="Batch number (1-11) from the manifest",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Evaluate quality and convert findings without writing to DB",
    )
    parser.add_argument(
        "--paper-limit", type=int, default=None,
        help="Limit processing to first N papers in the batch (for testing)",
    )
    parser.add_argument(
        "--db-path", type=str, default=str(DB_PATH),
        help=f"Path to the SQLite database (default: {DB_PATH})",
    )

    args = parser.parse_args()

    try:
        processor = BatchProcessor(
            batch_id=args.batch,
            db_path=Path(args.db_path),
            dry_run=args.dry_run,
            paper_limit=args.paper_limit,
        )
        processor.run()
        return 0
    except Exception as e:
        logger.error("Batch processing failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
