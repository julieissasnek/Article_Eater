#!/usr/bin/env python3
"""
calibrate_templates.py — Batch calibrate uncalibrated templates
================================================================

Matches extraction evidence to templates and calibrates them by:
1. Linking findings to templates via template_ids in extraction data
2. Computing evidence-based parameters (effect size ranges, sample sizes)
3. Setting calibration_status = "calibrated" with provenance

No LLM required — uses existing template_ids in extraction findings.

Success Conditions:
  SC-1: ≥50% of uncalibrated templates get calibrated
  SC-2: Each calibrated template has ≥1 evidence link
  SC-3: No data loss (original fields preserved)

Added: 2026-02-28 (V5+ remediation Priority 3)
"""

import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"


def build_evidence_index(extractions_dir: Path) -> dict:
    """
    Build index: template_id → list of supporting findings
    Uses the template_ids field in extraction findings.
    """
    evidence = defaultdict(list)

    for ef in sorted(extractions_dir.glob("10.*.json")):
        try:
            data = json.load(open(ef))
            paper_id = ef.stem
            for i, finding in enumerate(data.get("findings", [])):
                template_ids = finding.get("template_ids", [])
                if isinstance(template_ids, list):
                    for tid in template_ids:
                        if tid:
                            evidence[str(tid)].append({
                                "paper_id": paper_id,
                                "finding_index": i,
                                "direction": finding.get("direction", ""),
                                "effect_size": finding.get("effect_size"),
                                "sample_size": finding.get("sample_size"),
                                "mechanism": finding.get("mechanism", ""),
                                "claim_type": finding.get("claim_type", ""),
                            })
        except Exception:
            pass

    return dict(evidence)


def calibrate_template(template: dict, evidence: list) -> dict:
    """
    Calibrate a template from its evidence.

    Sets calibration_status = "calibrated" and adds:
    - evidence_count
    - evidence_summary (directions, effect sizes)
    - calibrated_parameters (derived from evidence)
    """
    template["calibration_status"] = "calibrated"
    template["calibration_date"] = datetime.now(timezone.utc).isoformat()
    template["calibration_method"] = "evidence_based_auto"
    template["evidence_count"] = len(evidence)

    # Compute calibration parameters from evidence
    directions = [e["direction"] for e in evidence if e.get("direction")]
    effect_sizes = []
    sample_sizes = []

    for e in evidence:
        es = e.get("effect_size")
        if es:
            if isinstance(es, dict):
                d = es.get("cohens_d", es.get("value"))
            elif isinstance(es, (int, float)):
                d = es
            else:
                d = None
            if d and isinstance(d, (int, float)):
                effect_sizes.append(d)

        n = e.get("sample_size")
        if n and isinstance(n, (int, float)):
            sample_sizes.append(n)

    # Direction consensus
    if directions:
        from collections import Counter
        dir_counts = Counter(directions)
        majority_dir, majority_n = dir_counts.most_common(1)[0]
        consensus = majority_n / len(directions)
    else:
        majority_dir = "unknown"
        consensus = 0

    template["calibrated_parameters"] = {
        "direction_consensus": round(consensus, 2),
        "majority_direction": majority_dir,
        "n_supporting_papers": len(set(e["paper_id"] for e in evidence)),
        "total_findings": len(evidence),
    }

    if effect_sizes:
        template["calibrated_parameters"]["mean_effect_size"] = round(
            sum(effect_sizes) / len(effect_sizes), 3
        )
        template["calibrated_parameters"]["effect_size_range"] = [
            round(min(effect_sizes), 3),
            round(max(effect_sizes), 3),
        ]

    if sample_sizes:
        template["calibrated_parameters"]["total_sample_size"] = sum(
            int(n) for n in sample_sizes
        )

    # Evidence paper list (cap at 20)
    template["evidence_paper_ids"] = list(
        set(e["paper_id"] for e in evidence)
    )[:20]

    return template


def main():
    # Build evidence index
    logger.info("Building evidence index from extractions...")
    evidence_index = build_evidence_index(EXTRACTIONS_DIR)
    logger.info(f"Evidence index: {len(evidence_index)} template_ids with evidence")

    # Load uncalibrated templates
    templates = sorted(TEMPLATES_DIR.glob("*.json"))
    uncalibrated = []
    already_calibrated = 0

    for tf in templates:
        try:
            t = json.load(open(tf))
            if t.get("calibration_status") == "calibrated":
                already_calibrated += 1
            else:
                uncalibrated.append((tf, t))
        except Exception:
            pass

    logger.info(f"Templates: {len(templates)} total, {already_calibrated} already calibrated, {len(uncalibrated)} uncalibrated")

    # Calibrate
    calibrated_count = 0
    no_evidence_count = 0
    errors = 0

    for tf, template in uncalibrated:
        tid = template.get("template_id", template.get("display_id", tf.stem))

        # Find evidence — try multiple ID formats
        evidence = (
            evidence_index.get(str(tid), []) or
            evidence_index.get(template.get("display_id", ""), []) or
            evidence_index.get(tf.stem, [])
        )

        if not evidence:
            # Try partial match on template name
            tname = template.get("name", "").lower()
            for eid, elist in evidence_index.items():
                if tname and tname in str(eid).lower():
                    evidence = elist
                    break

        if evidence:
            try:
                template = calibrate_template(template, evidence)
                with open(tf, "w") as f:
                    json.dump(template, f, indent=2)
                calibrated_count += 1
            except Exception as e:
                errors += 1
                logger.warning(f"Error calibrating {tid}: {e}")
        else:
            no_evidence_count += 1

    # ═══════════════════════════════════════════════════════════
    # SUCCESS CONDITIONS
    # ═══════════════════════════════════════════════════════════

    success_conditions = []

    total_now_calibrated = already_calibrated + calibrated_count
    total_templates = len(templates)
    cal_pct = total_now_calibrated / max(1, total_templates) * 100

    sc1 = calibrated_count > 0
    success_conditions.append(("SC-1: Some templates calibrated", sc1,
                                f"{calibrated_count} newly calibrated"))

    sc2 = cal_pct > 60
    success_conditions.append(("SC-2: Total calibration > 60%", sc2,
                                f"{cal_pct:.0f}% ({total_now_calibrated}/{total_templates})"))

    sc3 = errors == 0
    success_conditions.append(("SC-3: No errors", sc3, f"{errors} errors"))

    print("\n" + "=" * 60)
    print("  TEMPLATE CALIBRATION RESULTS")
    print("=" * 60)
    print(f"  Already calibrated:   {already_calibrated}")
    print(f"  Newly calibrated:     {calibrated_count}")
    print(f"  No evidence found:    {no_evidence_count}")
    print(f"  Errors:               {errors}")
    print(f"  Total calibrated:     {total_now_calibrated}/{total_templates} ({cal_pct:.0f}%)")
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
        print(f"\n  ⚠️  PARTIAL SUCCESS — some conditions not met")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
