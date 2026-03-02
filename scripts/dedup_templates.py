#!/usr/bin/env python3
"""
dedup_templates.py — Remove duplicate template IDs across template files
=========================================================================

Found by validation_reflexes tests: 42 template IDs exist in multiple files
(e.g., NM_SAFETY_SIGNALING_001 in both T66.json and NM_SAFETY_SIGNALING_001.json).

Strategy: Keep the richer file (more fields filled). Delete the sparser duplicate.

Success conditions:
  SC-1: 0 duplicate template IDs after dedup
  SC-2: No templates lost (all unique IDs preserved)
  SC-3: No errors during dedup

Added: 2026-02-28 (V6 prevention — caught by test_no_duplicate_template_ids)
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.utils.validation_reflexes import validate_template, warn
    HAS_REFLEXES = True
except ImportError:
    HAS_REFLEXES = False


def richness_score(template: dict) -> int:
    """Score how "rich" a template is (more filled fields = richer)."""
    score = 0
    for key, val in template.items():
        if val is not None and val != "" and val != [] and val != {}:
            score += 1
        # Bonus for calibrated templates
        if key == "calibration_status" and val == "calibrated":
            score += 5
        # Bonus for evidence
        if key == "evidence_paper_ids" and isinstance(val, list) and len(val) > 0:
            score += 3
        if key == "effect_size_range" and val:
            score += 2
    return score


def main():
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    
    # Build map: template_id → list of (path, template_data, richness)
    id_map = {}
    for tf in template_files:
        try:
            t = json.load(open(tf))
            tid = t.get("template_id", tf.stem)
            richness = richness_score(t)
            if tid not in id_map:
                id_map[tid] = []
            id_map[tid].append((tf, t, richness))
        except Exception as e:
            print(f"  ✗ Error reading {tf.name}: {e}")
    
    # Find duplicates
    duplicates = {tid: entries for tid, entries in id_map.items() if len(entries) > 1}
    print(f"Found {len(duplicates)} duplicate template IDs across {sum(len(e) for e in duplicates.values())} files")
    
    removed = 0
    kept = 0
    errors = 0
    unique_ids_before = len(id_map)
    
    for tid, entries in duplicates.items():
        # Sort by richness: keep the richest
        entries.sort(key=lambda x: x[2], reverse=True)
        keeper = entries[0]
        
        # Validate the keeper
        if HAS_REFLEXES:
            ok, msg = validate_template(keeper[1])
            warn(ok, msg, context=f"dedup_templates({tid})")
        
        # Remove the rest
        for path, data, richness in entries[1:]:
            print(f"  ✓ {tid}: keep {keeper[0].name} (richness={keeper[2]}), remove {path.name} (richness={richness})")
            try:
                os.remove(path)
                removed += 1
            except Exception as e:
                print(f"  ✗ Error removing {path.name}: {e}")
                errors += 1
        kept += 1
    
    # Verify: recount
    remaining = list(TEMPLATES_DIR.glob("*.json"))
    remaining_ids = set()
    dup_check = []
    for tf in remaining:
        try:
            t = json.load(open(tf))
            tid = t.get("template_id", tf.stem)
            if tid in remaining_ids:
                dup_check.append(tid)
            remaining_ids.add(tid)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    
    # ── Success Conditions ──
    print(f"\n{'='*60}")
    print(f"  TEMPLATE DEDUP RESULTS")
    print(f"{'='*60}")
    print(f"  Files before:  {len(template_files)}")
    print(f"  Files after:   {len(remaining)}")
    print(f"  Removed:       {removed}")
    print(f"  Unique IDs:    {len(remaining_ids)}")
    
    sc1 = len(dup_check) == 0
    sc2 = len(remaining_ids) == unique_ids_before  # No IDs lost
    sc3 = errors == 0
    
    print(f"\n  ── SUCCESS CONDITIONS ──")
    print(f"  {'✓' if sc1 else '✗'}  SC-1: 0 remaining duplicates: {len(dup_check)}")
    print(f"  {'✓' if sc2 else '✗'}  SC-2: All IDs preserved: {len(remaining_ids)}/{unique_ids_before}")
    print(f"  {'✓' if sc3 else '✗'}  SC-3: No errors: {errors}")
    all_pass = sc1 and sc2 and sc3
    print(f"\n  {'✅ ALL PASS' if all_pass else '⚠️ SOME FAILED'}")
    print(f"{'='*60}")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
