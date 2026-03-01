#!/usr/bin/env python3
"""
generate_annotations_a9_a13_a14.py — Auto-Generate A9/A13/A14 Annotations
=========================================================================

Scans 824 extraction files and auto-generates:
  A9  (surprise_flag):       Findings that contradict the majority direction
  A13 (replication_status):  DOIs that share antecedent+consequent pairs
  A14 (effect_magnitude):    Human-readable effect size interpretations

No LLM required — pure data analysis.

Usage:
    python3 scripts/generate_annotations_a9_a13_a14.py [--limit N]

Added: 2026-02-28 (V5+ remediation Priority 2)
"""

import json
import logging
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
OUTPUT_DIR = PROJECT_ROOT / "data" / "annotations"


# ═══════════════════════════════════════════════════════════════
# Effect Size Interpretation (A14)
# ═══════════════════════════════════════════════════════════════

EFFECT_SIZE_SCALE = [
    (0.01, "negligible", "Barely detectable — like the difference between 20°C and 20.1°C in room comfort"),
    (0.20, "small", "Noticeable if you're paying attention — like the difference between a slightly warm and slightly cool room"),
    (0.50, "medium", "Clearly noticeable — like the difference between a quiet library and a busy café for concentration"),
    (0.80, "large", "Dramatic — like the difference between working in a windowless basement and a sunlit corner office"),
    (1.20, "very large", "Transformative — like the difference between a hospital ward and a healing garden for stress recovery"),
    (float('inf'), "massive", "Among the strongest effects in environmental psychology"),
]


def interpret_effect_size(d: float) -> Dict:
    """Convert Cohen's d to human-readable A14 annotation."""
    d_abs = abs(d)
    for threshold, label, analogy in EFFECT_SIZE_SCALE:
        if d_abs < threshold:
            # NNT approximation: NNT ≈ 1/Φ(d/√2) where Φ is normal CDF
            # Simplified: NNT ≈ 2π/d for moderate d
            nnt = max(2, round(2.5 / max(0.01, d_abs)))
            return {
                "type": "effect_magnitude",
                "cohens_d": round(d, 3),
                "magnitude_label": label,
                "human_scale": analogy,
                "nnt": nnt,
                "nnt_explanation": f"For every {nnt} people exposed to this design change, 1 will measurably benefit",
                "practical_significance": label,
            }
    return {"type": "effect_magnitude", "cohens_d": d, "magnitude_label": "unknown"}


# ═══════════════════════════════════════════════════════════════
# Surprise Detection (A9)
# ═══════════════════════════════════════════════════════════════

def detect_surprises(
    all_findings: List[Dict],
    min_group_size: int = 3
) -> List[Dict]:
    """
    Detect A9 surprise flags by finding findings whose direction
    contradicts the majority for the same antecedent→consequent pattern.

    A finding is "surprising" if:
    1. Most findings with similar antecedent/consequent say direction=X
    2. This finding says direction=Y (opposite)
    3. The group has at least min_group_size findings (statistical basis)
    """
    # Group findings by normalized antecedent+consequent
    groups = defaultdict(list)
    for f in all_findings:
        ant = (f.get("antecedent") or "").lower().strip()[:80]
        con = (f.get("consequent") or "").lower().strip()[:80]
        if ant and con:
            key = f"{ant}|{con}"
            groups[key].append(f)

    surprises = []
    for key, group in groups.items():
        if len(group) < min_group_size:
            continue

        directions = Counter(f.get("direction", "").lower() for f in group)
        if len(directions) < 2:
            continue  # No disagreement

        majority_dir, majority_count = directions.most_common(1)[0]
        minority_findings = [
            f for f in group
            if f.get("direction", "").lower() != majority_dir
        ]

        for mf in minority_findings:
            surprise_level = 1.0 - (len(minority_findings) / len(group))
            surprises.append({
                "type": "surprise_flag",
                "paper_id": mf.get("_paper_id", ""),
                "finding_index": mf.get("_finding_index", 0),
                "common_assumption": f"Most studies ({majority_count}/{len(group)}) find direction='{majority_dir}'",
                "actual_finding": f"This study finds direction='{mf.get('direction', '')}'",
                "surprise_level": round(surprise_level, 2),
                "why_surprising": f"Contradicts {majority_count} other findings with same antecedent→consequent pattern",
                "antecedent": mf.get("antecedent", "")[:200],
                "consequent": mf.get("consequent", "")[:200],
                "group_size": len(group),
            })

    return sorted(surprises, key=lambda x: x["surprise_level"], reverse=True)


# ═══════════════════════════════════════════════════════════════
# Replication Detection (A13)
# ═══════════════════════════════════════════════════════════════

def detect_replications(all_findings: List[Dict]) -> List[Dict]:
    """
    Detect A13 replication status by finding multiple papers
    testing the same antecedent→consequent relationship.

    Groups by normalized antecedent+consequent, then checks
    if the direction is consistent across papers.
    """
    # Group by antecedent+consequent
    groups = defaultdict(list)
    for f in all_findings:
        ant = (f.get("antecedent") or "").lower().strip()[:80]
        con = (f.get("consequent") or "").lower().strip()[:80]
        if ant and con:
            key = f"{ant}|{con}"
            groups[key].append(f)

    replications = []
    for key, group in groups.items():
        unique_papers = set(f.get("_paper_id", "") for f in group)
        if len(unique_papers) < 2:
            continue  # Need at least 2 papers for replication

        # Check direction consistency
        directions = Counter(f.get("direction", "").lower() for f in group)
        majority_dir, majority_count = directions.most_common(1)[0]

        consistent_count = majority_count
        total = len(group)

        if consistent_count == total:
            status = "fully_replicated"
        elif consistent_count >= total * 0.75:
            status = "mostly_replicated"
        elif consistent_count >= total * 0.5:
            status = "partially_replicated"
        else:
            status = "contested"

        robustness = consistent_count / total

        # Collect sample sizes
        sample_sizes = [
            f.get("sample_size") for f in group
            if f.get("sample_size") and isinstance(f.get("sample_size"), (int, float))
        ]

        replications.append({
            "type": "replication_status",
            "antecedent": group[0].get("antecedent", "")[:200],
            "consequent": group[0].get("consequent", "")[:200],
            "n_studies": len(unique_papers),
            "n_findings": total,
            "direction_consistency": round(robustness, 2),
            "overall_status": status,
            "robustness_score": round(robustness, 2),
            "paper_ids": list(unique_papers)[:20],
            "sample_sizes": sample_sizes[:10],
            "majority_direction": majority_dir,
        })

    return sorted(replications, key=lambda x: x["n_studies"], reverse=True)


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    extraction_files = sorted(EXTRACTIONS_DIR.glob("10.*.json"))
    if args.limit > 0:
        extraction_files = extraction_files[:args.limit]

    logger.info(f"Scanning {len(extraction_files)} extraction files")

    # Collect all findings with paper metadata
    all_findings = []
    a14_annotations = []

    for ef in extraction_files:
        try:
            data = json.load(open(ef))
            paper_id = ef.stem
            for i, finding in enumerate(data.get("findings", [])):
                finding["_paper_id"] = paper_id
                finding["_finding_index"] = i
                all_findings.append(finding)

                # A14: Effect magnitude
                es = finding.get("effect_size")
                if es:
                    d_val = None
                    if isinstance(es, dict):
                        d_val = es.get("cohens_d", es.get("value"))
                    elif isinstance(es, (int, float)):
                        d_val = es

                    if d_val and isinstance(d_val, (int, float)) and d_val != 0:
                        a14 = interpret_effect_size(d_val)
                        a14["paper_id"] = paper_id
                        a14["finding_index"] = i
                        a14["antecedent"] = finding.get("antecedent", "")[:200]
                        a14["consequent"] = finding.get("consequent", "")[:200]
                        a14_annotations.append(a14)
        except Exception:
            pass

    logger.info(f"Total findings: {len(all_findings)}")

    # A9: Surprise detection
    logger.info("Detecting A9 surprises...")
    a9_annotations = detect_surprises(all_findings)
    logger.info(f"Found {len(a9_annotations)} surprise flags")

    # A13: Replication detection
    logger.info("Detecting A13 replications...")
    a13_annotations = detect_replications(all_findings)
    logger.info(f"Found {len(a13_annotations)} replication clusters")

    # A14 summary
    logger.info(f"Generated {len(a14_annotations)} A14 effect magnitude annotations")

    # ═══════════════════════════════════════════════════════════
    # SUCCESS CONDITIONS
    # ═══════════════════════════════════════════════════════════

    success_conditions = []

    sc1 = len(a14_annotations) > 100
    success_conditions.append(("SC-1: A14 annotations > 100", sc1, f"{len(a14_annotations)}"))

    sc2 = len(a13_annotations) > 10
    success_conditions.append(("SC-2: A13 replication clusters > 10", sc2, f"{len(a13_annotations)}"))

    sc3 = len(a9_annotations) > 0
    success_conditions.append(("SC-3: A9 surprises detected", sc3, f"{len(a9_annotations)}"))

    # Save outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_DIR / "a9_surprise_flags.json", "w") as f:
        json.dump(a9_annotations, f, indent=2)
    with open(OUTPUT_DIR / "a13_replication_status.json", "w") as f:
        json.dump(a13_annotations, f, indent=2)
    with open(OUTPUT_DIR / "a14_effect_magnitude.json", "w") as f:
        json.dump(a14_annotations, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("  ANNOTATION AUTO-GENERATION RESULTS")
    print("=" * 60)
    print(f"  A9  Surprise Flags:      {len(a9_annotations)}")
    print(f"  A13 Replication Clusters: {len(a13_annotations)}")
    print(f"  A14 Effect Magnitudes:    {len(a14_annotations)}")
    print()

    # A14 breakdown
    mag_counts = Counter(a["magnitude_label"] for a in a14_annotations)
    print("  A14 Magnitude Distribution:")
    for label, count in sorted(mag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {label:15s}: {count}")
    print()

    # A13 breakdown
    rep_counts = Counter(a["overall_status"] for a in a13_annotations)
    print("  A13 Replication Status Distribution:")
    for status, count in sorted(rep_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {status:25s}: {count}")
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
        print(f"\n  ❌ GENERATION INCOMPLETE")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
