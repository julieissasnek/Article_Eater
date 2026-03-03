#!/usr/bin/env python3
"""
bulk_integrate_extractions.py — Fast Bulk Paper Integration
============================================================

Converts 824 extraction JSONs directly into Web of Belief entries
WITHOUT requiring LLM API calls. Uses existing extraction data
(findings, effect sizes, theory links, mechanisms) to create
beliefs and constraints directly.

This bypasses the slow batch integration pipeline (which requires
Gemini API calls per paper) and instead does direct conversion:

    extraction.finding → belief (with credence from effect size + sample size)
    extraction.theory_link → constraint (linking belief to theory node)
    extraction.mechanism → bridge_warrant (if mechanism pathway specified)

Usage:
    python3 scripts/bulk_integrate_extractions.py [--dry-run] [--limit N] [--db-path PATH]

Added: 2026-02-28 (V5+ remediation Priority 1)
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
RESULTS_DIR = PROJECT_ROOT / "data" / "integration_results"


# ═══════════════════════════════════════════════════════════════
# Credence Computation
# ═══════════════════════════════════════════════════════════════

def compute_credence(finding: dict) -> float:
    """
    Compute initial credence for a belief from extraction data.

    Uses a weighted combination of:
    - Effect size magnitude (larger = higher credence)
    - Sample size (larger = higher credence)
    - Direction clarity (clear direction = higher credence)
    - Theory linkage (linked to known theory = modest boost)

    Returns a value in [0.1, 0.9] — never extreme without human review.
    """
    credence = 0.5  # Base prior (maximum ignorance)

    # Effect size contribution
    es = finding.get("effect_size")
    if es:
        if isinstance(es, dict):
            d = abs(es.get("cohens_d", es.get("value", 0)) or 0)
        elif isinstance(es, (int, float)):
            d = abs(es)
        else:
            d = 0

        if d > 0:
            # Sigmoid mapping: d=0.2 → +0.05, d=0.5 → +0.10, d=0.8 → +0.15
            es_boost = min(0.2, d * 0.2)
            credence += es_boost

    # Sample size contribution
    n = finding.get("sample_size") or finding.get("n")
    if n and isinstance(n, (int, float)) and n > 0:
        # Log scaling: n=30 → +0.02, n=100 → +0.05, n=1000 → +0.08
        import math
        n_boost = min(0.1, math.log10(max(1, n)) * 0.03)
        credence += n_boost

    # Theory linkage boost
    if finding.get("theory_links") or finding.get("theory"):
        credence += 0.05

    # Mechanism evidence boost
    if finding.get("mechanism") or finding.get("mechanism_pathway"):
        credence += 0.05

    # Clamp to [0.1, 0.9]
    return max(0.1, min(0.9, credence))


def classify_finding_domain(finding: dict) -> str:
    """Classify finding into a domain based on content."""
    text = json.dumps(finding).lower()

    domain_keywords = {
        "neuroarchitecture": ["amygdala", "cortex", "fmri", "neural", "brain"],
        "environmental_psychology": ["nature", "green", "outdoor", "restoration", "biophil"],
        "architectural_perception": ["room", "ceiling", "building", "interior", "facade"],
        "affect": ["emotion", "stress", "anxiety", "mood", "arousal"],
        "cognition": ["attention", "memory", "cognitive", "processing"],
        "lighting": ["light", "illumina", "lux", "cct", "color temperature"],
        "acoustics": ["noise", "sound", "acoustic", "decibel"],
        "thermal": ["temperature", "thermal", "hvac", "comfort"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in text for kw in keywords):
            return domain

    return "general"


# ═══════════════════════════════════════════════════════════════
# Database Operations
# ═══════════════════════════════════════════════════════════════

def ensure_schema(conn: sqlite3.Connection):
    """Ensure integration_log table exists (other tables already present)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS integration_log (
            log_id TEXT PRIMARY KEY,
            paper_id TEXT,
            n_beliefs INTEGER,
            n_constraints INTEGER,
            integrated_at TEXT
        )
    """)
    conn.commit()


def is_paper_integrated(conn: sqlite3.Connection, paper_id: str) -> bool:
    """Check if paper already integrated."""
    cur = conn.execute(
        "SELECT COUNT(*) FROM integration_log WHERE paper_id = ?",
        (paper_id,)
    )
    return cur.fetchone()[0] > 0


# Default web_id for bulk-integrated beliefs
BULK_WEB_ID = "web:atlas_v1"


def integrate_paper(
    conn: sqlite3.Connection,
    paper_id: str,
    findings: List[dict],
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Integrate a single paper's findings into the database.

    Uses existing schema:
      beliefs: belief_id, web_id, content, credence_value, credence_uncertainty,
               level, status, paper_ids, created_at, updated_at
      constraints: constraint_id, web_id, source_id, target_id,
                   constraint_type, strength, created_at

    Returns (n_beliefs, n_constraints) created.
    """
    beliefs_created = 0
    constraints_created = 0
    now = datetime.now(timezone.utc).isoformat()

    for i, finding in enumerate(findings):
        # Create belief from finding — extraction schema uses antecedent/consequent
        belief_id = f"belief:{paper_id}:f{i}:{uuid.uuid4().hex[:6]}"

        # Build content from antecedent → consequent (primary extraction fields)
        antecedent = finding.get("antecedent", "")
        consequent = finding.get("consequent", "")
        if antecedent and consequent:
            content = f"{antecedent} → {consequent}"
        elif antecedent:
            content = antecedent
        elif consequent:
            content = consequent
        else:
            # Fallback to other content fields
            content = finding.get("finding", finding.get("claim",
                      finding.get("description", finding.get("quote", ""))))

        if not content or len(content) < 10:
            continue

        credence = compute_credence(finding)
        domain = classify_finding_domain(finding)
        paper_ids_json = json.dumps([paper_id])

        if not dry_run:
            try:
                # Serialize scope conditions if available (Sprint 6: Scope Persistence)
                scope_json = None
                if isinstance(finding, dict):
                    try:
                        from src.services.extraction_to_web import _extract_scope
                        scope_obj = _extract_scope({"study": finding.get("study", {})})
                        scope_json = json.dumps(scope_obj.to_dict())
                    except Exception:
                        pass  # Graceful degradation if scope extraction fails

                conn.execute(
                    """INSERT OR IGNORE INTO beliefs
                       (belief_id, web_id, content, credence_value, credence_uncertainty,
                        level, status, paper_ids, scope, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (belief_id, BULK_WEB_ID, content[:2000], credence, 0.3,
                     domain, "active", paper_ids_json, scope_json, now, now)
                )
                beliefs_created += 1
            except sqlite3.IntegrityError:
                continue
        else:
            beliefs_created += 1

        # Create constraints from theory links
        tl = finding.get("theory_links", [])
        if isinstance(tl, list):
            for tlink in tl:
                if isinstance(tlink, dict):
                    theory_name = tlink.get("theory", tlink.get("name", ""))
                elif isinstance(tlink, str):
                    theory_name = tlink
                else:
                    continue

                if not theory_name:
                    continue

                constraint_id = f"constr:{paper_id}:f{i}:{uuid.uuid4().hex[:6]}"
                if not dry_run:
                    try:
                        conn.execute(
                            """INSERT OR IGNORE INTO constraints
                               (constraint_id, web_id, source_id, target_id,
                                constraint_type, strength, created_at)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (constraint_id, BULK_WEB_ID, belief_id,
                             f"theory:{theory_name}",
                             "theory_support", credence * 0.8, now)
                        )
                        constraints_created += 1
                    except sqlite3.IntegrityError:
                        continue
                else:
                    constraints_created += 1

    # Log integration
    if not dry_run and beliefs_created > 0:
        conn.execute(
            "INSERT OR REPLACE INTO integration_log (log_id, paper_id, n_beliefs, n_constraints, integrated_at) VALUES (?, ?, ?, ?, ?)",
            (f"log:{paper_id}", paper_id, beliefs_created, constraints_created, now)
        )

    return beliefs_created, constraints_created


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Bulk integrate extraction data")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    parser.add_argument("--limit", type=int, default=0, help="Max papers (0=all)")
    parser.add_argument("--db-path", type=str, default="/tmp/web_persistence_v2.db",
                        help="Database path")
    args = parser.parse_args()

    extraction_files = sorted(EXTRACTIONS_DIR.glob("10.*.json"))
    if args.limit > 0:
        extraction_files = extraction_files[:args.limit]

    logger.info(f"Found {len(extraction_files)} extraction files")
    logger.info(f"DB path: {args.db_path}")
    logger.info(f"Dry run: {args.dry_run}")

    conn = None
    if not args.dry_run:
        conn = sqlite3.connect(args.db_path)
        ensure_schema(conn)

    total_beliefs = 0
    total_constraints = 0
    papers_integrated = 0
    papers_skipped = 0
    papers_empty = 0
    papers_errors = 0

    for i, ef in enumerate(extraction_files):
        paper_id = ef.stem  # DOI-based filename

        # Check if already integrated
        if conn and is_paper_integrated(conn, paper_id):
            papers_skipped += 1
            continue

        try:
            data = json.load(open(ef))
            findings = data.get("findings", [])

            if not findings:
                papers_empty += 1
                continue

            n_beliefs, n_constraints = integrate_paper(
                conn, paper_id, findings, dry_run=args.dry_run
            )

            total_beliefs += n_beliefs
            total_constraints += n_constraints
            papers_integrated += 1

            if (i + 1) % 50 == 0:
                logger.info(
                    f"Progress: {i+1}/{len(extraction_files)} papers, "
                    f"{total_beliefs} beliefs, {total_constraints} constraints"
                )
                if conn:
                    conn.commit()

        except Exception as e:
            papers_errors += 1
            if papers_errors <= 5:
                logger.warning(f"Error processing {paper_id}: {e}")

    if conn:
        conn.commit()

    # ═══════════════════════════════════════════════════════════════
    # SUCCESS CONDITIONS — These MUST pass or the integration FAILED
    # ═══════════════════════════════════════════════════════════════

    n_input = len(extraction_files)
    n_processed = papers_integrated + papers_skipped + papers_empty
    error_rate = papers_errors / max(1, n_input)

    success_conditions = []

    # SC-1: At least 80% of input files must be processed (not errored)
    sc1_pass = error_rate < 0.20
    success_conditions.append(("SC-1: Error rate < 20%",
                                sc1_pass,
                                f"{error_rate*100:.1f}% errors ({papers_errors}/{n_input})"))

    # SC-2: If non-dry-run, at least 1 belief must be created per non-empty paper
    if not args.dry_run and papers_integrated > 0:
        beliefs_per_paper = total_beliefs / max(1, papers_integrated)
        sc2_pass = beliefs_per_paper >= 1.0
        success_conditions.append(("SC-2: ≥1 belief per paper",
                                    sc2_pass,
                                    f"{beliefs_per_paper:.1f} beliefs/paper"))
    else:
        sc2_pass = True
        success_conditions.append(("SC-2: ≥1 belief per paper", True, "N/A (dry run)"))

    # SC-3: DB row count must have increased
    if conn and not args.dry_run:
        conn2 = sqlite3.connect(args.db_path)
        cur = conn2.execute("SELECT COUNT(*) FROM beliefs")
        db_beliefs = cur.fetchone()[0]
        cur = conn2.execute("SELECT COUNT(*) FROM integration_log")
        db_logs = cur.fetchone()[0]
        cur = conn2.execute("SELECT COUNT(DISTINCT paper_id) FROM integration_log")
        db_papers = cur.fetchone()[0]
        conn2.close()

        sc3_pass = db_papers > 0 if papers_integrated > 0 else True
        success_conditions.append(("SC-3: DB papers integrated > 0",
                                    sc3_pass,
                                    f"{db_papers} papers in integration_log, {db_beliefs} total beliefs"))
    else:
        success_conditions.append(("SC-3: DB verification", True, "N/A (dry run)"))

    # SC-4: No more than 10% empty extraction files
    empty_rate = papers_empty / max(1, n_input)
    sc4_pass = empty_rate < 0.10
    success_conditions.append(("SC-4: Empty extractions < 10%",
                                sc4_pass,
                                f"{empty_rate*100:.1f}% ({papers_empty}/{n_input})"))

    # SC-5: At least some constraints created (evidence of theory linkage)
    if papers_integrated > 0:
        sc5_pass = total_constraints > 0
        success_conditions.append(("SC-5: Constraints created > 0",
                                    sc5_pass,
                                    f"{total_constraints} constraints"))
    else:
        success_conditions.append(("SC-5: Constraints > 0", True, "N/A (no papers)"))

    # ─── Print Results ───
    print("\n" + "=" * 60)
    print("  BULK INTEGRATION RESULTS")
    print("=" * 60)
    print(f"  Papers processed:    {papers_integrated}")
    print(f"  Papers skipped:      {papers_skipped} (already integrated)")
    print(f"  Papers empty:        {papers_empty}")
    print(f"  Papers with errors:  {papers_errors}")
    print(f"  Beliefs created:     {total_beliefs}")
    print(f"  Constraints created: {total_constraints}")
    print(f"  DB path:             {args.db_path}")
    print(f"  Dry run:             {args.dry_run}")
    print()
    print("  ── SUCCESS CONDITIONS ──")
    all_pass = True
    for name, passed, detail in success_conditions:
        icon = "✓" if passed else "✗ FAIL"
        print(f"  {icon}  {name}: {detail}")
        if not passed:
            all_pass = False

    if all_pass:
        print(f"\n  ✅ ALL SUCCESS CONDITIONS MET")
    else:
        print(f"\n  ❌ INTEGRATION FAILED — success conditions not met")
        print(f"     This failure is INTENTIONAL — it prevents silent 0% integration.")

    print("=" * 60)

    if conn:
        conn.close()

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "papers_integrated": papers_integrated,
        "papers_skipped": papers_skipped,
        "papers_empty": papers_empty,
        "papers_errors": papers_errors,
        "total_beliefs": total_beliefs,
        "total_constraints": total_constraints,
        "dry_run": args.dry_run,
        "db_path": args.db_path,
        "success_conditions": {name: {"passed": passed, "detail": detail}
                                for name, passed, detail in success_conditions},
        "all_conditions_met": all_pass,
    }
    results_file = RESULTS_DIR / "bulk_integration_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_file}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
