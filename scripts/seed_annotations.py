#!/usr/bin/env python3
"""
Seed Initial Annotations — Populate CALIBRATION_NOTE and SENSITIVITY_FLAG
=========================================================================

Created: 2026-02-27
Sprint: EN-0D

Seeds annotations from existing template data:
1. CALIBRATION_NOTE: For each calibrated template, record bridge_warrant + panel_source
2. SENSITIVITY_FLAG: For parameters that vary >2× across studies (check range fields)

Usage:
    python scripts/seed_annotations.py --dry-run      # Preview
    python scripts/seed_annotations.py                 # Apply
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.annotation_service import (
    AnnotationService,
    AnnotationType,
)

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path("data/templates")


def find_sensitive_parameters(template: Dict) -> List[Dict]:
    """
    Find parameters that vary >2× across their range.
    Returns list of {param_name, min, max, ratio, unit}.
    """
    params = template.get("calibrated_parameters", {})
    if not isinstance(params, dict):
        return []

    sensitive = []
    for name, spec in params.items():
        if not isinstance(spec, dict):
            continue

        # Check range field
        param_range = spec.get("range", [])
        if isinstance(param_range, list) and len(param_range) == 2:
            low, high = param_range
            if isinstance(low, (int, float)) and isinstance(high, (int, float)):
                if low > 0 and high / low > 2.0:
                    sensitive.append({
                        "param_name": name,
                        "min": low,
                        "max": high,
                        "ratio": round(high / low, 1),
                        "value": spec.get("value"),
                        "unit": spec.get("unit", ""),
                    })

        # Check CI field
        ci = spec.get("ci_95", [])
        if isinstance(ci, list) and len(ci) == 2:
            ci_low, ci_high = ci
            if isinstance(ci_low, (int, float)) and isinstance(ci_high, (int, float)):
                if ci_low > 0 and ci_high / ci_low > 3.0:
                    # Wide CI — also flag
                    if name not in [s["param_name"] for s in sensitive]:
                        sensitive.append({
                            "param_name": name,
                            "min": ci_low,
                            "max": ci_high,
                            "ratio": round(ci_high / ci_low, 1),
                            "value": spec.get("value"),
                            "unit": spec.get("unit", ""),
                            "source": "ci_95",
                        })

    return sensitive


def collect_seed_annotations(templates_dir: Path) -> List[Dict]:
    """Collect all annotations to seed."""
    annotations = []

    for json_file in sorted(templates_dir.glob("*.json")):
        try:
            template = json.load(open(json_file))
        except Exception:
            continue

        tid = template.get("display_id", json_file.stem)
        is_calibrated = template.get("calibration_status") == "calibrated"

        # CALIBRATION_NOTE for calibrated templates
        if is_calibrated:
            warrant = template.get("bridge_warrant", "unknown")
            panel = template.get("panel_source", "unknown")
            panel_docs = template.get("panel_docs", [])
            name = template.get("name", "")

            content = (
                f"Calibrated template '{name}'. "
                f"Bridge warrant: {warrant}. "
                f"Panel: {panel}."
            )
            if panel_docs:
                docs_str = ", ".join(str(d)[:60] for d in panel_docs[:3])
                content += f" Source docs: {docs_str}"

            annotations.append({
                "type": AnnotationType.CALIBRATION_NOTE.value,
                "target_type": "template",
                "target_id": tid,
                "content": content,
                "author": "system (seed_annotations v1)",
                "confidence": 0.95,
                "provenance": {
                    "method": "seed_annotations.py",
                    "version": "v1_2026-02-27",
                    "source_field": "bridge_warrant + panel_source",
                },
                "metadata": {
                    "bridge_warrant": warrant,
                    "panel_source": panel,
                    "calibration_status": "calibrated",
                },
            })

        # SENSITIVITY_FLAG for sensitive parameters
        sensitive = find_sensitive_parameters(template)
        for sp in sensitive:
            content = (
                f"Parameter '{sp['param_name']}' varies {sp['ratio']}× "
                f"across studies (range: {sp['min']}–{sp['max']} {sp.get('unit', '')[:40]})"
            )
            annotations.append({
                "type": AnnotationType.SENSITIVITY_FLAG.value,
                "target_type": "parameter",
                "target_id": f"{tid}:{sp['param_name']}",
                "content": content,
                "author": "system (seed_annotations v1)",
                "confidence": 0.8,
                "provenance": {
                    "method": "seed_annotations.py",
                    "version": "v1_2026-02-27",
                    "source_field": "calibrated_parameters.range",
                },
                "metadata": {
                    "param_name": sp["param_name"],
                    "min": sp["min"],
                    "max": sp["max"],
                    "ratio": sp["ratio"],
                    "value": sp["value"],
                },
            })

    return annotations


def main():
    parser = argparse.ArgumentParser(description="Seed initial annotations")
    parser.add_argument("--templates-dir", type=Path, default=TEMPLATES_DIR)
    parser.add_argument("--db-path", default="/tmp/annotations_seed.db",
                        help="Database path (default: /tmp for safety)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    annotations = collect_seed_annotations(args.templates_dir)

    # Summary
    by_type = {}
    for a in annotations:
        by_type[a["type"]] = by_type.get(a["type"], 0) + 1

    print(f"=== SEED ANNOTATIONS ===")
    print(f"Total: {len(annotations)}")
    for t, n in sorted(by_type.items()):
        print(f"  {t}: {n}")

    if args.dry_run:
        print(f"\n🔍 Dry run — no annotations written.")
        if args.verbose:
            for a in annotations[:10]:
                print(f"  [{a['type']}] {a['target_type']}:{a['target_id']}")
                print(f"    {a['content'][:80]}...")
        return 0

    # Create and seed
    svc = AnnotationService(db_path=args.db_path)
    results = svc.create_annotations_batch(annotations)
    print(f"\n✅ Seeded {len(results)} annotations to {args.db_path}")

    stats = svc.get_annotation_stats()
    print(f"Stats: {json.dumps(stats, indent=2)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
