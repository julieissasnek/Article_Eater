#!/usr/bin/env python3
"""Restore confidence values that were destructively clamped to ceiling maximums.

This script compares template files against commit 90a53c6 (pre-clamping) and
restores original confidence values where the current value equals the ceiling.
It also flags restored steps with ceiling_status: "exceeds" for panel review.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
BASELINE_COMMIT = "90a53c6"

CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORY_DERIVED": 0.40,
}


@dataclass
class Restoration:
    """Record of a restored confidence value."""
    template_id: str
    template_file: str
    field_path: str  # e.g., "mechanism_chain[5].confidence"
    warrant: str
    original_value: float
    clamped_value: float
    ceiling: float


def get_template_from_git(filename: str, commit: str) -> Optional[dict[str, Any]]:
    """Fetch template from git at a specific commit."""
    result = subprocess.run(
        ["git", "show", f"{commit}:data/templates/{filename}"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"  Warning: Failed to parse {filename} from git: {e}")
            return None
    return None


def normalize_warrant(value: str | None) -> str | None:
    """Normalize warrant string."""
    if not value:
        return None
    return value.strip().upper()


def check_restoration_needed(
    current_conf: float, original_conf: float, warrant: str | None
) -> bool:
    """Check if restoration is needed.
    
    Restoration is needed if:
    - original_conf > ceiling AND
    - current_conf == ceiling (exactly)
    """
    if warrant is None or original_conf is None:
        return False
    
    warrant = normalize_warrant(warrant)
    ceiling = CEILINGS.get(warrant)
    if ceiling is None:
        return False
    
    # Round to avoid floating point errors
    current_rounded = round(current_conf, 10)
    ceiling_rounded = round(ceiling, 10)
    
    return (
        original_conf > ceiling and
        abs(current_rounded - ceiling_rounded) < 1e-9
    )


def restore_mechanism_chain(
    current_template: dict[str, Any],
    original_template: dict[str, Any],
    restorations: list[Restoration],
    template_id: str,
    template_file: str,
) -> bool:
    """Restore mechanism_chain steps. Return True if any changes made."""
    current_chain = current_template.get("mechanism_chain", [])
    original_chain = original_template.get("mechanism_chain", [])
    
    if not current_chain or not original_chain:
        return False
    
    changed = False
    for idx in range(min(len(current_chain), len(original_chain))):
        cur_step = current_chain[idx]
        orig_step = original_chain[idx]
        
        cur_conf = cur_step.get("confidence")
        orig_conf = orig_step.get("confidence")
        cur_warrant = cur_step.get("warrant")
        
        if cur_conf is None or orig_conf is None or cur_warrant is None:
            continue
        
        if check_restoration_needed(cur_conf, orig_conf, cur_warrant):
            warrant_norm = normalize_warrant(cur_warrant)
            ceiling = CEILINGS.get(warrant_norm)
            
            # Restore the original value
            current_chain[idx]["confidence"] = orig_conf
            
            # Flag for panel review
            current_chain[idx]["ceiling_status"] = "exceeds"
            
            restorations.append(
                Restoration(
                    template_id=template_id,
                    template_file=template_file,
                    field_path=f"mechanism_chain[{idx + 1}].confidence",
                    warrant=warrant_norm,
                    original_value=orig_conf,
                    clamped_value=cur_conf,
                    ceiling=ceiling,
                )
            )
            changed = True
    
    return changed


def restore_root_confidence(
    current_template: dict[str, Any],
) -> bool:
    """Recalculate root-level confidence as mean of step confidences.
    
    Return True if the value changed.
    """
    mechanism_chain = current_template.get("mechanism_chain", [])
    if not mechanism_chain:
        return False
    
    step_confidences = []
    for step in mechanism_chain:
        conf = step.get("confidence")
        if isinstance(conf, (int, float)):
            step_confidences.append(conf)
    
    if not step_confidences:
        return False
    
    new_root_confidence = sum(step_confidences) / len(step_confidences)
    old_root_confidence = current_template.get("confidence")
    
    if old_root_confidence != new_root_confidence:
        current_template["confidence"] = new_root_confidence
        return True
    
    return False


def restore_all_templates() -> list[Restoration]:
    """Iterate through templates, restore values, and return list of restorations."""
    restorations: list[Restoration] = []
    files_processed = 0
    files_changed = 0
    
    template_paths = sorted(TEMPLATES_DIR.glob("*.json"))
    
    for template_path in template_paths:
        files_processed += 1
        
        # Load current version
        try:
            with open(template_path) as f:
                current = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  Error reading {template_path.name}: {e}")
            continue
        
        # Skip if no mechanism_chain
        if "mechanism_chain" not in current:
            continue
        
        template_id = current.get("template_id", template_path.stem)
        
        # Load original from git
        original = get_template_from_git(template_path.name, BASELINE_COMMIT)
        if original is None:
            continue
        
        # Track changes
        any_change = False
        
        # Restore mechanism_chain confidences
        if restore_mechanism_chain(current, original, restorations, template_id, template_path.name):
            any_change = True
        
        # Recalculate root confidence if any step changed
        if any_change:
            restore_root_confidence(current)
            
            # Write back to file
            with open(template_path, "w") as f:
                json.dump(current, f, indent=2)
            
            files_changed += 1
            print(f"  Updated: {template_path.name}")
    
    print(f"\nProcessed {files_processed} templates")
    print(f"Modified {files_changed} templates")
    print(f"Restored {len(restorations)} confidence values")
    
    return restorations


def print_restoration_report(restorations: list[Restoration]) -> None:
    """Print summary report of all restorations."""
    if not restorations:
        print("\nNo restorations were needed.")
        return
    
    print("\n" + "=" * 80)
    print("RESTORATION REPORT")
    print("=" * 80)
    
    # Group by template
    by_template = {}
    for r in restorations:
        if r.template_id not in by_template:
            by_template[r.template_id] = []
        by_template[r.template_id].append(r)
    
    # Group by warrant
    by_warrant = {}
    for r in restorations:
        if r.warrant not in by_warrant:
            by_warrant[r.warrant] = []
        by_warrant[r.warrant].append(r)
    
    print(f"\nTotal restorations: {len(restorations)}")
    print(f"Templates affected: {len(by_template)}")
    print(f"Warrant types: {sorted(by_warrant.keys())}")
    
    print("\n" + "-" * 80)
    print("BY WARRANT TYPE:")
    print("-" * 80)
    for warrant in sorted(by_warrant.keys()):
        items = by_warrant[warrant]
        ceiling = CEILINGS.get(warrant)
        print(f"\n{warrant} (ceiling={ceiling}): {len(items)} restorations")
        
        # Show value ranges
        original_vals = [r.original_value for r in items]
        deltas = [r.original_value - r.clamped_value for r in items]
        
        print(f"  Original values: {min(original_vals):.3f} - {max(original_vals):.3f}")
        print(f"  Loss from clamping: {min(deltas):.3f} - {max(deltas):.3f}")
    
    print("\n" + "-" * 80)
    print("BY TEMPLATE:")
    print("-" * 80)
    for template_id in sorted(by_template.keys()):
        items = by_template[template_id]
        print(f"\n{template_id}: {len(items)} steps")
        for r in items:
            print(f"  {r.field_path}: {r.clamped_value} -> {r.original_value} "
                  f"({r.warrant} ceiling={r.ceiling})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print(f"Restoring confidence values from commit {BASELINE_COMMIT}...\n")
    restorations = restore_all_templates()
    print_restoration_report(restorations)
    
    # Save restorations to JSON for reference
    report_path = PROJECT_ROOT / "data" / "restorations.json"
    with open(report_path, "w") as f:
        json.dump(
            {
                "baseline_commit": BASELINE_COMMIT,
                "total_restorations": len(restorations),
                "ceilings": CEILINGS,
                "restorations": [
                    {
                        "template_id": r.template_id,
                        "template_file": r.template_file,
                        "field_path": r.field_path,
                        "warrant": r.warrant,
                        "original_value": r.original_value,
                        "clamped_value": r.clamped_value,
                        "ceiling": r.ceiling,
                    }
                    for r in restorations
                ],
            },
            f,
            indent=2,
        )
    
    print(f"\nRestoration log saved to: {report_path}")
