#!/usr/bin/env python3
"""
Bridge Template Worlds — Cross-populate fields between calibrated and uncalibrated templates
============================================================================================

Created: 2026-02-27
Phase: 1 (Web Maturity Deepening)

Problem: 208 templates split into two nearly disjoint schemas.
  - Calibrated (103): mechanism_chain, calibrated_parameters, bridge_warrant
  - Uncalibrated (105): causal_links, higher_order_principle, moderators, structural_pattern

Solution: Non-destructively bridge the gap by synthesizing missing fields from available data.
All synthesized fields carry `bridge_inferred: true` provenance.

Usage:
    python scripts/bridge_template_worlds.py --dry-run      # Preview changes
    python scripts/bridge_template_worlds.py                 # Apply changes
    python scripts/bridge_template_worlds.py --report-only   # Just show gap report
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path("data/templates")
BRIDGE_VERSION = "bridge_v1_2026-02-27"


# =============================================================================
# GAP ANALYSIS
# =============================================================================

def analyze_gaps(templates: List[Dict]) -> Dict[str, Any]:
    """Compute field coverage and identify bridgeable gaps."""
    cal = [t for t in templates if t.get("calibration_status") == "calibrated"]
    uncal = [t for t in templates if t.get("calibration_status") != "calibrated"]

    fields = [
        "mechanism_chain", "calibrated_parameters", "causal_links",
        "bridge_warrant", "higher_order_principle", "moderators",
        "structural_pattern", "building_types", "framework_ids",
    ]

    report = {
        "n_calibrated": len(cal),
        "n_uncalibrated": len(uncal),
        "n_total": len(templates),
        "field_coverage": {},
        "bridgeable": {},
    }

    for field in fields:
        cal_pct = sum(1 for t in cal if t.get(field)) / max(len(cal), 1) * 100
        uncal_pct = sum(1 for t in uncal if t.get(field)) / max(len(uncal), 1) * 100
        report["field_coverage"][field] = {
            "calibrated": round(cal_pct, 1),
            "uncalibrated": round(uncal_pct, 1),
            "gap": round(abs(cal_pct - uncal_pct), 1),
        }

    # Count bridgeable templates
    report["bridgeable"] = {
        "uncal_can_gain_mechanism_chain": sum(
            1 for t in uncal if t.get("causal_links") and not t.get("mechanism_chain")
        ),
        "uncal_can_gain_bridge_warrant": sum(
            1 for t in uncal if t.get("causal_links") and not t.get("bridge_warrant")
        ),
        "cal_can_gain_higher_order_principle": sum(
            1 for t in cal if not t.get("higher_order_principle") and t.get("name")
        ),
        "uncal_can_gain_building_types": sum(
            1 for t in uncal if not t.get("building_types") and t.get("moderators")
        ),
    }

    return report


# =============================================================================
# BRIDGE OPERATIONS
# =============================================================================

def synthesize_mechanism_chain_from_causal_links(
    causal_links: List[Dict],
) -> List[Dict]:
    """
    Convert causal_links (uncalibrated format) into mechanism_chain (calibrated format).

    Input format:
        {link_id, from_level, to_level, activity, direction, mechanism_summary, edge_confidence}

    Output format:
        {step, from, to, description, warrant, confidence}
    """
    chain = []
    confidence_map = {
        "strong": 0.75,
        "moderate": 0.55,
        "weak": 0.35,
        "speculative": 0.20,
        "unknown": 0.40,
    }

    for i, link in enumerate(causal_links):
        from_entity = link.get("from_level", link.get("from", "unknown"))
        to_entity = link.get("to_level", link.get("to", "unknown"))
        summary = link.get("mechanism_summary", link.get("description", ""))
        conf_label = str(link.get("edge_confidence", "unknown")).lower()

        chain.append({
            "step": i + 1,
            "from": from_entity,
            "to": to_entity,
            "description": summary,
            "warrant": "ANALOGICAL",  # Conservative — we don't know the original warrant
            "confidence": confidence_map.get(conf_label, 0.40),
            "bridge_inferred": True,
            "source_link_id": link.get("link_id", ""),
        })

    return chain


def infer_bridge_warrant_from_maturity(causal_links: List[Dict]) -> str:
    """
    Infer a bridge_warrant from the most common edge_confidence in causal_links.
    Conservative: we default to ANALOGICAL unless strong evidence suggests otherwise.
    """
    if not causal_links:
        return "ANALOGICAL"

    confidences = [
        str(cl.get("edge_confidence", "unknown")).lower() for cl in causal_links
    ]
    strong = sum(1 for c in confidences if c == "strong")
    moderate = sum(1 for c in confidences if c == "moderate")

    if strong > len(causal_links) / 2:
        return "EMPIRICAL_ASSOCIATION"
    elif moderate > len(causal_links) / 2:
        return "MECHANISM"
    return "ANALOGICAL"


def infer_building_types_from_moderators(moderators: List) -> List[str]:
    """
    Extract building types from moderator descriptions.
    Looks for building-type keywords in moderator text.
    """
    building_keywords = {
        "office": "offices",
        "school": "schools",
        "classroom": "schools",
        "hospital": "hospitals",
        "healthcare": "hospitals",
        "residential": "residential",
        "home": "residential",
        "retail": "retail",
        "museum": "museums",
        "library": "libraries",
        "eldercare": "eldercare",
        "care facility": "eldercare",
    }

    found = set()
    for mod in moderators:
        mod_text = str(mod).lower()
        for kw, btype in building_keywords.items():
            if kw in mod_text:
                found.add(btype)

    return sorted(found) if found else ["all"]


def synthesize_higher_order_principle(template: Dict) -> str:
    """
    Generate a higher_order_principle from available fields.
    Uses mechanism_chain entities and name to construct a principle statement.
    """
    name = template.get("name", "")
    chain = template.get("mechanism_chain", [])

    if chain and len(chain) >= 2:
        first = chain[0].get("from", "").replace("_", " ")
        last = chain[-1].get("to", "").replace("_", " ")
        return (
            f"{first.capitalize()} → {last} pathway: "
            f"The mechanism by which {name.lower()} operates"
        )

    return f"The principle underlying {name.lower()}" if name else ""


# =============================================================================
# BRIDGE EXECUTION
# =============================================================================

def bridge_template(
    template: Dict,
    dry_run: bool = False,
) -> Tuple[Dict, List[str]]:
    """
    Bridge a single template by filling in missing fields.
    Returns (modified_template, list_of_changes_made).
    """
    changes = []
    t = template  # Modify in-place if not dry_run, or just report

    is_calibrated = t.get("calibration_status") == "calibrated"

    # --- Uncalibrated → gain mechanism_chain from causal_links ---
    if not is_calibrated and t.get("causal_links") and not t.get("mechanism_chain"):
        chain = synthesize_mechanism_chain_from_causal_links(t["causal_links"])
        if chain:
            if not dry_run:
                t["mechanism_chain"] = chain
            changes.append(
                f"  + mechanism_chain ({len(chain)} steps from {len(t['causal_links'])} causal_links)"
            )

    # --- Uncalibrated → gain bridge_warrant ---
    if not is_calibrated and t.get("causal_links") and not t.get("bridge_warrant"):
        warrant = infer_bridge_warrant_from_maturity(t["causal_links"])
        if not dry_run:
            t["bridge_warrant"] = warrant
            t["bridge_warrant_inferred"] = True
        changes.append(f"  + bridge_warrant = {warrant} (inferred from edge_confidence)")

    # --- Uncalibrated → gain building_types from moderators ---
    if not is_calibrated and t.get("moderators") and not t.get("building_types"):
        btypes = infer_building_types_from_moderators(t["moderators"])
        if not dry_run:
            t["building_types"] = btypes
            t["building_types_inferred"] = True
        changes.append(f"  + building_types = {btypes}")

    # --- Calibrated → gain higher_order_principle ---
    if is_calibrated and not t.get("higher_order_principle") and t.get("name"):
        principle = synthesize_higher_order_principle(t)
        if principle:
            if not dry_run:
                t["higher_order_principle"] = principle
                t["higher_order_principle_inferred"] = True
            changes.append(f"  + higher_order_principle (from mechanism chain)")

    # --- Add bridge provenance if any changes were made ---
    if changes and not dry_run:
        if "bridge_provenance" not in t:
            t["bridge_provenance"] = {
                "bridge_version": BRIDGE_VERSION,
                "bridged_at": datetime.now(timezone.utc).isoformat(),
                "fields_inferred": [c.split("=")[0].strip().lstrip("+").strip() for c in changes],
            }

    return t, changes


def bridge_all_templates(
    templates_dir: Path,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Bridge all templates in the directory.
    Returns summary of changes.
    """
    results = {
        "total": 0,
        "modified": 0,
        "changes_by_field": {},
        "details": [],
    }

    for json_file in sorted(templates_dir.glob("*.json")):
        try:
            with open(json_file) as f:
                template = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Skipping {json_file}: {e}")
            continue

        results["total"] += 1
        display_id = template.get("display_id", json_file.stem)

        modified_template, changes = bridge_template(template, dry_run=dry_run)

        if changes:
            results["modified"] += 1
            results["details"].append({
                "display_id": display_id,
                "file": str(json_file.name),
                "changes": changes,
            })

            for change in changes:
                field = change.split("=")[0].strip().lstrip("+").strip()
                results["changes_by_field"][field] = (
                    results["changes_by_field"].get(field, 0) + 1
                )

            # Write back if not dry run
            if not dry_run:
                with open(json_file, "w") as f:
                    json.dump(modified_template, f, indent=2, ensure_ascii=False)
                    f.write("\n")

    return results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Bridge Template Worlds — cross-populate fields between calibrated and uncalibrated templates"
    )
    parser.add_argument(
        "--templates-dir", type=Path, default=TEMPLATES_DIR,
        help="Path to templates directory",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--report-only", action="store_true",
        help="Show gap analysis report only (no changes)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show per-template details",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    # Load templates for analysis
    templates = []
    for f in sorted(args.templates_dir.glob("*.json")):
        try:
            templates.append(json.load(open(f)))
        except Exception:
            continue

    # Gap report
    report = analyze_gaps(templates)
    print("=" * 70)
    print("WEB OF BELIEF — TEMPLATE GAP ANALYSIS")
    print("=" * 70)
    print(f"  Total templates:   {report['n_total']}")
    print(f"  Calibrated:        {report['n_calibrated']}")
    print(f"  Uncalibrated:      {report['n_uncalibrated']}")
    print()
    print(f"{'Field':35s} {'Cal%':>6s} {'Uncal%':>8s} {'Gap':>6s}")
    print("-" * 60)
    for field, cov in report["field_coverage"].items():
        marker = " ← BRIDGE" if cov["gap"] > 30 else ""
        print(f"  {field:33s} {cov['calibrated']:5.0f}% {cov['uncalibrated']:7.0f}% {cov['gap']:5.0f}%{marker}")
    print()
    print("Bridgeable:")
    for key, count in report["bridgeable"].items():
        print(f"  {key}: {count}")

    if args.report_only:
        return 0

    # Bridge
    print()
    action = "DRY RUN" if args.dry_run else "APPLYING CHANGES"
    print(f"{'=' * 70}")
    print(f"BRIDGE EXECUTION ({action})")
    print(f"{'=' * 70}")

    results = bridge_all_templates(args.templates_dir, dry_run=args.dry_run)

    print(f"  Templates scanned: {results['total']}")
    print(f"  Templates modified: {results['modified']}")
    print()

    if results["changes_by_field"]:
        print("Changes by field:")
        for field, count in sorted(results["changes_by_field"].items()):
            print(f"  {field}: {count} templates")
        print()

    if args.verbose and results["details"]:
        print("Details:")
        for d in results["details"]:
            print(f"  {d['display_id']} ({d['file']}):")
            for c in d["changes"]:
                print(f"    {c}")
        print()

    if not args.dry_run:
        print(f"✅ Bridge complete. {results['modified']} templates enriched.")
        print(f"   Provenance tag: {BRIDGE_VERSION}")
    else:
        print(f"🔍 Dry run complete. {results['modified']} templates WOULD be enriched.")
        print(f"   Run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
