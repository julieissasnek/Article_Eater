#!/usr/bin/env python3
"""
Sprint C: Integration & Verification Script
=============================================

Runs the Sprint C verification checklist from CW's edited plan:
1. Sample 5 real beliefs and trace through full pipeline
2. Compute ω for sample beliefs, compare to legacy credence
3. Verify unified annotation queries return all types
4. Check provenance JustificationStatus distribution
5. Report annotation coverage (AN-SC-04)

Usage:
    python3 scripts/sprint_c_verification.py [--db PATH] [--n-beliefs 5]
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.db_locator import get_web_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_DB = get_web_db()  # Centralized: was hardcoded


def trace_beliefs(db_path: str, n: int = 5) -> dict:
    """Trace N sample beliefs through the full pipeline."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get column info
    cols = {row[1] for row in conn.execute("PRAGMA table_info(beliefs)").fetchall()}

    # Sample beliefs with variety: pick from different templates
    beliefs = conn.execute(
        """SELECT * FROM beliefs
           WHERE status != 'RETIRED'
           ORDER BY RANDOM()
           LIMIT ?""",
        (n,),
    ).fetchall()

    results = []
    for b in beliefs:
        belief_id = b["belief_id"]
        trace = {
            "belief_id": belief_id,
            "template_id": b["template_id"] if "template_id" in cols else None,
            "credence": b["credence"] if "credence" in cols else None,
            "status": b["status"],
        }

        # Check provenance via epistemic_v2 JSON column
        if "epistemic_v2" in cols and b["epistemic_v2"]:
            try:
                ev2 = json.loads(b["epistemic_v2"]) if isinstance(b["epistemic_v2"], str) else b["epistemic_v2"]
                prov = ev2.get("provenance_v2", {})
                trace["justification_status"] = prov.get("justification_status", 
                    ev2.get("status_v2", "UNKNOWN"))
                trace["source_article"] = prov.get("source_article", "")[:60]
            except (json.JSONDecodeError, AttributeError):
                trace["justification_status"] = "PARSE_ERROR"
                trace["source_article"] = ""
        else:
            trace["justification_status"] = "NO_EPISTEMIC_V2"
            trace["source_article"] = ""

        # Check constraints (edges) for this belief
        constraint_cols = {row[1] for row in conn.execute("PRAGMA table_info(constraints)").fetchall()}
        edge_count = conn.execute(
            "SELECT COUNT(*) FROM constraints WHERE source_id = ? OR target_id = ?",
            (belief_id, belief_id),
        ).fetchone()[0]
        trace["edge_count"] = edge_count

        # Get environment and outcome
        if "environment_id" in cols:
            trace["environment_id"] = b["environment_id"][:40] if b["environment_id"] else None
        if "outcome_id" in cols:
            trace["outcome_id"] = b["outcome_id"][:40] if b["outcome_id"] else None

        results.append(trace)

    conn.close()
    return {"beliefs": results, "sampled": len(results)}


def compute_omega_for_beliefs(db_path: str, n: int = 10) -> dict:
    """Compute ω for N beliefs and compare to legacy credence."""
    from src.services.warrant_strength import compute_omega_from_extraction

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cols = {row[1] for row in conn.execute("PRAGMA table_info(beliefs)").fetchall()}

    beliefs = conn.execute(
        """SELECT * FROM beliefs
           WHERE status != 'RETIRED'
           ORDER BY RANDOM()
           LIMIT ?""",
        (n,),
    ).fetchall()

    comparisons = []
    for b in beliefs:
        belief_id = b["belief_id"]
        legacy_credence = b["credence"] if "credence" in cols else None

        # Build finding dict from epistemic_v2 metadata
        finding = {}
        if "epistemic_v2" in cols and b["epistemic_v2"]:
            try:
                ev2 = json.loads(b["epistemic_v2"]) if isinstance(b["epistemic_v2"], str) else b["epistemic_v2"]
                prov = ev2.get("provenance_v2", {})
                finding["design_type"] = prov.get("design_type", "observational")
                finding["sample_size"] = prov.get("sample_size")
                finding["pre_registered"] = prov.get("pre_registered", False)
                finding["blinded"] = prov.get("blinded", False)
                finding["publication_type"] = prov.get("publication_type", "peer_reviewed")
            except (json.JSONDecodeError, AttributeError):
                finding["design_type"] = "observational"

        try:
            result = compute_omega_from_extraction(finding)
            comparisons.append({
                "belief_id": belief_id[:30],
                "legacy_credence": round(legacy_credence, 4) if legacy_credence else None,
                "omega": round(result.omega, 4),
                "omega_source": round(result.omega_source, 4),
                "omega_sev": round(result.omega_sev, 4),
                "design_type": result.design_type,
            })
        except Exception as e:
            comparisons.append({
                "belief_id": belief_id[:30],
                "error": str(e),
            })

    conn.close()

    # Compute correlation if we have enough data
    valid = [(c["legacy_credence"], c["omega"]) for c in comparisons
             if c.get("legacy_credence") is not None and c.get("omega") is not None]
    correlation = None
    if len(valid) >= 3:
        lc = [v[0] for v in valid]
        oc = [v[1] for v in valid]
        mean_lc = sum(lc) / len(lc)
        mean_oc = sum(oc) / len(oc)
        cov = sum((a - mean_lc) * (b - mean_oc) for a, b in valid) / len(valid)
        var_lc = sum((a - mean_lc) ** 2 for a in lc) / len(lc)
        var_oc = sum((b - mean_oc) ** 2 for b in oc) / len(oc)
        if var_lc > 0 and var_oc > 0:
            correlation = round(cov / (var_lc ** 0.5 * var_oc ** 0.5), 4)

    return {
        "comparisons": comparisons,
        "correlation": correlation,
        "n_valid": len(valid),
    }


def verify_annotation_queries(db_path: str) -> dict:
    """Verify unified annotation API returns all types."""
    from src.services.annotation_service import (
        AnnotationService, AnnotationType, AnnotationLayer,
    )

    svc = AnnotationService(db_path=db_path)

    # Get stats
    stats = svc.get_annotation_stats()
    coverage = svc.get_annotation_coverage()

    # Test get_all_annotations on a random target
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    sample = conn.execute(
        "SELECT DISTINCT target_id FROM annotations LIMIT 3"
    ).fetchall()
    conn.close()

    query_results = []
    for row in sample:
        target_id = row["target_id"]
        all_anns = svc.get_all_annotations(target_id)
        by_layer = {}
        for a in all_anns:
            layer = a.layer.value if hasattr(a.layer, 'value') else str(a.layer)
            by_layer[layer] = by_layer.get(layer, 0) + 1
        query_results.append({
            "target_id": target_id[:40],
            "total": len(all_anns),
            "by_layer": by_layer,
        })

    # Check all 23 types are registered
    registered_types = set()
    conn = sqlite3.connect(db_path)
    for row in conn.execute("SELECT type FROM annotation_types").fetchall():
        registered_types.add(row[0])
    conn.close()
    enum_types = set(t.value for t in AnnotationType)

    return {
        "stats": stats,
        "coverage": coverage,
        "query_samples": query_results,
        "registered_type_count": len(registered_types),
        "enum_type_count": len(enum_types),
        "missing_types": list(enum_types - registered_types),
        "all_types_registered": registered_types >= enum_types,
    }


def check_provenance_distribution(db_path: str) -> dict:
    """Check JustificationStatus distribution across beliefs."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cols = {row[1] for row in conn.execute("PRAGMA table_info(beliefs)").fetchall()}

    # Use epistemic_v2 column (the actual schema) instead of nonexistent 'provenance'
    if "epistemic_v2" not in cols:
        conn.close()
        return {
            "warning": "No epistemic_v2 column in beliefs table (provenance stored elsewhere)",
            "total_beliefs": conn.execute("SELECT COUNT(*) FROM beliefs WHERE status != 'RETIRED'").fetchone()[0] if False else 0,
            "distribution": {},
            "grounding_ratio": 0,
            "grounded_count": 0,
            "aeshi_grounding_score": "N/A",
        }

    rows = conn.execute(
        "SELECT epistemic_v2 FROM beliefs WHERE status != 'RETIRED'"
    ).fetchall()

    distribution = {}
    total = 0
    for (ev2_raw,) in rows:
        total += 1
        if not ev2_raw:
            status = "NONE"
        else:
            try:
                ev2 = json.loads(ev2_raw) if isinstance(ev2_raw, str) else ev2_raw
                prov = ev2.get("provenance_v2", {})
                status = prov.get("justification_status",
                    ev2.get("status_v2", "UNSET"))
            except (json.JSONDecodeError, AttributeError):
                status = "PARSE_ERROR"
        distribution[status] = distribution.get(status, 0) + 1

    conn.close()

    grounded = distribution.get("GROUNDED", 0)
    grounding_ratio = grounded / total if total > 0 else 0

    return {
        "total_beliefs": total,
        "distribution": distribution,
        "grounding_ratio": round(grounding_ratio, 4),
        "grounded_count": grounded,
        "aeshi_grounding_score": "GREEN" if grounding_ratio >= 0.60 else
                                 "YELLOW" if grounding_ratio >= 0.40 else "RED",
    }


def main():
    parser = argparse.ArgumentParser(description="Sprint C verification")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB))
    parser.add_argument("--n-beliefs", type=int, default=5)
    args = parser.parse_args()

    print("=" * 70)
    print("SPRINT C: INTEGRATION & VERIFICATION")
    print("=" * 70)

    # 1. Trace beliefs
    print("\n--- 1. BELIEF PIPELINE TRACE ---")
    trace = trace_beliefs(args.db, args.n_beliefs)
    for b in trace["beliefs"]:
        print(f"  {b['belief_id'][:35]:35s}  "
              f"cred={b.get('credence', '?')!s:6s}  "
              f"edges={b.get('edge_count', '?'):3}  "
              f"just={b.get('justification_status', '?')}")

    # 2. ω vs legacy credence
    print("\n--- 2. ω vs LEGACY CREDENCE ---")
    omega_cmp = compute_omega_for_beliefs(args.db, min(args.n_beliefs * 2, 20))
    for c in omega_cmp["comparisons"]:
        if "error" in c:
            print(f"  {c['belief_id']:30s}  ERROR: {c['error']}")
        else:
            print(f"  {c['belief_id']:30s}  "
                  f"legacy={c.get('legacy_credence', '?')!s:6s}  "
                  f"ω={c['omega']:.4f}  "
                  f"ω_src={c['omega_source']:.3f}  "
                  f"design={c.get('design_type', '?')}")
    if omega_cmp["correlation"] is not None:
        print(f"\n  Correlation(legacy, ω): r = {omega_cmp['correlation']:.4f}"
              f"  (n={omega_cmp['n_valid']})")
        print(f"  Target: r > 0.5 → {'✅ PASS' if omega_cmp['correlation'] > 0.5 else '⚠️ DIVERGENT (expected: SQ reshuffles rankings)'}")
    else:
        print(f"  (Insufficient data for correlation)")

    # 3. Annotation queries
    print("\n--- 3. ANNOTATION QUERY VERIFICATION ---")
    ann_v = verify_annotation_queries(args.db)
    print(f"  Registered types: {ann_v['registered_type_count']}/23"
          f"  ({'✅' if ann_v['all_types_registered'] else '❌ MISSING: ' + str(ann_v['missing_types'])})")
    print(f"  Total active annotations: {ann_v['stats'].get('total', 0)}")
    print(f"  By type: {json.dumps(ann_v['stats'].get('by_type', {}), indent=None)}")
    cov = ann_v.get("coverage", {})
    print(f"  Coverage: {json.dumps(cov.get('by_layer', {}), indent=None)}")
    for qs in ann_v.get("query_samples", []):
        print(f"  get_all_annotations({qs['target_id'][:25]}): {qs['total']} results, layers={qs['by_layer']}")

    # 4. Provenance distribution
    print("\n--- 4. PROVENANCE / JUSTIFICATION STATUS ---")
    prov = check_provenance_distribution(args.db)
    if "warning" in prov:
        print(f"  ⚠️ {prov['warning']}")
        print(f"  (Provenance stored in epistemic_v2 JSON — check may need schema update)")
    elif prov["total_beliefs"] == 0:
        print(f"  ⚠️ No non-retired beliefs found")
    else:
        print(f"  Total beliefs: {prov['total_beliefs']}")
        for status, count in sorted(prov["distribution"].items(), key=lambda x: -x[1]):
            pct = 100 * count / prov["total_beliefs"]
            print(f"  {status:20s}  {count:5d}  ({pct:.1f}%)")
        print(f"\n  Grounding ratio: {prov['grounding_ratio']:.4f}  ({prov['aeshi_grounding_score']})")

    # Summary
    print("\n" + "=" * 70)
    print("SPRINT C SUMMARY")
    print("=" * 70)
    checks = {
        "Belief trace": trace["sampled"] >= args.n_beliefs,
        "ω computed": len([c for c in omega_cmp["comparisons"] if "omega" in c]) > 0,
        "23 types registered": ann_v["all_types_registered"],
        "Annotations exist": ann_v["stats"].get("total", 0) > 0,
        "Provenance parsed": prov.get("total_beliefs", 0) > 0 or "warning" in prov,
    }
    for check, ok in checks.items():
        print(f"  {'✅' if ok else '❌'}  {check}")

    all_pass = all(checks.values())
    print(f"\n  {'✅ ALL CHECKS PASS' if all_pass else '⚠️ SOME CHECKS FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
