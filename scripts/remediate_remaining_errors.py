#!/usr/bin/env python3
"""
Comprehensive CMR Template Remediation Script

Fixes all 5 error classes in calibrated templates:
  - Fix A: Compute root-level tier from mechanism_chain
  - Fix B: Compute root-level bridge_warrant from mechanism_chain
  - Fix C: Compute root-level confidence from mechanism_chain
  - Fix D: T1 framework remediation (MUSIC-I, CROSSCUT-I, missing codes)
  - Fix E: Normalize legacy field names

Usage:
    python3 scripts/remediate_remaining_errors.py

Output:
    - Modified templates written back to data/templates/*.json
    - Detailed change report to stdout
    - Summary statistics

Author: Claude Code (Feb 23, 2026)
Sprint: CC_REPAIR_SPRINT, Task E-02
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Tuple
from collections import defaultdict

from resolve_fields import (
    resolve_field, get_mechanism_chain, get_confidence,
    get_bridge_warrant, get_calibration_status, normalize_template
)

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# Bridge warrant hierarchy (strongest to weakest)
WARRANT_HIERARCHY = {
    "CONSTITUTIVE": 0,
    "MECHANISM": 1,
    "EMPIRICAL_ASSOCIATION": 2,
    "FUNCTIONAL": 3,
    "CAPACITY": 4,
    "ANALOGICAL": 5,
    "THEORY_DERIVED": 6,
}

# Tier hierarchy (lowest to highest: C < B < A)
TIER_HIERARCHY = {
    "C": 2,
    "B": 1,
    "A": 0,
}

# Bridge warrant ceiling priors
BRIDGE_CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORY_DERIVED": 0.40,
}

# T1 Framework codes
T1_FRAMEWORKS = {"PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI"}

# Fix D1: MUSIC-I non-canonical codes mapping
MUSIC_T1_MAP = {
    'AEP': ['IC'],
    'MEP': ['IC', 'PP'],
    'MM': ['MS'],
    'EM': ['MS'],
    'CS': ['PP'],
    'SE': ['MSI'],
    'AR': ['MSI', 'SN'],
    'SA': ['PP', 'MSI'],
    'PS': ['PP']
}

# Fix D2: CROSSCUT-I AX templates with citations-as-T1
CROSSCUT_AX_MAPPING = {
    'AX_DOSE_RESPONSE_007': ['PP', 'NM'],
    'AX_HABITUATION_002': ['PP', 'NM'],
    'AX_CONTROL_STRESS_004': ['NM', 'IC'],
    'AX_CHRONIC_ACUTE_011': ['NM', 'IC'],
}

# Fix D3: Templates missing t1_frameworks entirely
MISSING_T1_MAP = {
    'AX_ATTENTION_MEDIATION_010': ['PP', 'DT'],
    'AX_CULTURAL_MODULATION_009': ['EC', 'DP'],
    'AX_INDIVIDUAL_DIFFERENCES_008': ['NM', 'DP'],
    'AX_VR_LIMITATION_012': ['PP', 'MSI'],
    'AX3_AWE_MECHANISM_001': ['PP', 'NM', 'IC'],
    'AX3_SMALL_SELF_001': ['IC', 'EC'],
    'ER_ECOLOGICAL_RATIONALITY_001': ['PP', 'DP'],
    'TEMPORAL_HIERARCHY_ARCH_PE_001': ['PP'],
    'CROSS_HIERARCHICAL_CONTROL_001': ['PP', 'DT'],
    'CROSS_PROACTIVE_REACTIVE_CONTROL_001': ['DP', 'DT'],
    'CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001': ['PP', 'NM'],
    'CROSS_WM_GAMMA_BETA_DYNAMICS_001': ['PP', 'MS'],
    'SALIENCE_NETWORK_SWITCH_001': ['DT', 'NM'],
}


@dataclass
class RemediationLog:
    """Track changes for a single template."""
    template_id: str
    file_path: str
    changes: List[str] = field(default_factory=list)

    def add_change(self, fix_label: str, detail: str):
        """Record a change."""
        self.changes.append(f"{fix_label}: {detail}")


def normalize_tier(tier_str: Optional[str]) -> Optional[str]:
    """Normalize tier string to canonical form (A, B, or C)."""
    if not tier_str:
        return None

    tier_str = str(tier_str).strip().upper()

    # Handle "Tier A", "Tier B", etc.
    match = re.search(r'(A|B|C)', tier_str)
    if match:
        return match.group(1)

    return None


def extract_warrant_keyword(text: str) -> Optional[str]:
    """Extract first warrant keyword from text using regex."""
    if not isinstance(text, str):
        return None

    pattern = r'(CONSTITUTIVE|MECHANISM|EMPIRICAL_ASSOCIATION|FUNCTIONAL|CAPACITY|ANALOGICAL|THEORY_DERIVED)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)

    return None


def get_weakest_warrant(warrants: List[str]) -> Optional[str]:
    """Return the weakest (lowest priority) warrant from a list."""
    if not warrants:
        return None

    # Filter out None and normalize
    valid = [w.upper() for w in warrants if w]
    if not valid:
        return None

    # Find weakest (highest number in hierarchy)
    weakest = max(valid, key=lambda w: WARRANT_HIERARCHY.get(w, 999))
    return weakest


def get_lowest_tier(tiers: List[str]) -> Optional[str]:
    """Return the lowest (weakest) tier from a list (C < B < A)."""
    if not tiers:
        return None

    # Normalize and filter
    valid = [normalize_tier(t) for t in tiers if normalize_tier(t)]
    if not valid:
        return None

    # Find lowest (highest number: C=2, B=1, A=0)
    lowest = max(valid, key=lambda t: TIER_HIERARCHY.get(t, -1))
    return lowest


def derive_tier_from_warrant(warrant: str) -> str:
    """Derive tier from bridge warrant type."""
    warrant = warrant.upper() if warrant else None
    if warrant in ("CONSTITUTIVE", "MECHANISM", "EMPIRICAL_ASSOCIATION", "FUNCTIONAL"):
        return "B"
    elif warrant in ("CAPACITY", "ANALOGICAL", "THEORY_DERIVED"):
        return "C"
    else:
        return "B"  # default


def collect_step_warrants(chain: List[Dict]) -> List[str]:
    """Collect all warrant types from mechanism_chain steps."""
    warrants = []

    for step in chain:
        if not isinstance(step, dict):
            continue

        # Check multiple field names for warrant
        for field_name in ["warrant", "bridge_warrant", "warrant_type"]:
            w = step.get(field_name)
            if w:
                # Handle verbose strings
                if isinstance(w, str) and len(w) > 25:
                    extracted = extract_warrant_keyword(w)
                    if extracted:
                        warrants.append(extracted)
                        break
                elif isinstance(w, str):
                    warrants.append(w)
                    break

    return warrants


def collect_step_tiers(chain: List[Dict]) -> List[str]:
    """Collect all depth_tier values from mechanism_chain steps."""
    tiers = []

    for step in chain:
        if not isinstance(step, dict):
            continue

        # Check multiple field names for tier
        for field_name in ["depth_tier", "justification.depth_tier", "toulmin_justification.depth_tier"]:
            t = step.get(field_name)
            if t:
                normalized = normalize_tier(t)
                if normalized:
                    tiers.append(normalized)
                    break

        # Check nested justification object
        if not tiers or len(tiers) == len([x for x in tiers if x]):
            justification = step.get("justification") or step.get("toulmin_justification")
            if isinstance(justification, dict):
                t = justification.get("depth_tier")
                if t:
                    normalized = normalize_tier(t)
                    if normalized:
                        tiers.append(normalized)

    return tiers


def collect_step_confidences(chain: List[Dict]) -> List[float]:
    """Collect all confidence values from mechanism_chain steps."""
    confidences = []

    for step in chain:
        if not isinstance(step, dict):
            continue

        for field_name in ["confidence", "prior_confidence", "bridge_prior"]:
            c = step.get(field_name)
            if c is not None:
                try:
                    confidences.append(float(c))
                    break
                except (ValueError, TypeError):
                    pass

    return confidences


def fix_a_compute_tier(template: Dict, log: RemediationLog) -> bool:
    """Fix A: Compute root-level tier from mechanism_chain."""
    # Only set if template doesn't already have a valid tier
    existing_tier = template.get("tier")
    if existing_tier and normalize_tier(existing_tier):
        return False  # Already has valid tier

    chain = get_mechanism_chain(template)

    # Collect tiers from steps
    tiers = collect_step_tiers(chain)

    if tiers:
        lowest_tier = get_lowest_tier(tiers)
        if lowest_tier:
            template["tier"] = lowest_tier
            log.add_change("Fix-A", f"Computed tier '{lowest_tier}' from {len(tiers)} mechanism steps")
            return True

    # Fallback: derive from bridge_warrant
    warrant = get_bridge_warrant(template)
    if warrant:
        derived_tier = derive_tier_from_warrant(warrant)
        template["tier"] = derived_tier
        log.add_change("Fix-A", f"Derived tier '{derived_tier}' from bridge_warrant '{warrant}'")
        return True

    return False


def fix_b_compute_bridge_warrant(template: Dict, log: RemediationLog) -> bool:
    """Fix B: Compute root-level bridge_warrant from mechanism_chain."""
    existing_warrant = get_bridge_warrant(template)

    # If missing, compute from mechanism_chain
    if not existing_warrant:
        chain = get_mechanism_chain(template)
        warrants = collect_step_warrants(chain)

        if warrants:
            weakest = get_weakest_warrant(warrants)
            if weakest:
                template["bridge_warrant"] = weakest
                log.add_change("Fix-B", f"Computed bridge_warrant '{weakest}' from {len(warrants)} mechanism steps")
                return True
        return False

    # If verbose string (length > 25), extract warrant keyword
    if isinstance(existing_warrant, str) and len(existing_warrant) > 25:
        extracted = extract_warrant_keyword(existing_warrant)
        if extracted and extracted != existing_warrant:
            template["bridge_warrant"] = extracted
            log.add_change("Fix-B", f"Normalized verbose bridge_warrant '{existing_warrant[:30]}...' to '{extracted}'")
            return True

    return False


def fix_c_compute_confidence(template: Dict, log: RemediationLog) -> bool:
    """Fix C: Compute root-level confidence from mechanism_chain."""
    existing_confidence = get_confidence(template)

    # Only compute if missing
    if existing_confidence is not None:
        return False

    chain = get_mechanism_chain(template)
    confidences = collect_step_confidences(chain)

    if confidences:
        mean_confidence = sum(confidences) / len(confidences)
        # Round to 2 decimals
        rounded_confidence = round(mean_confidence, 2)
        template["confidence"] = rounded_confidence
        log.add_change("Fix-C", f"Computed confidence {rounded_confidence} from {len(confidences)} mechanism steps")
        return True

    # Fallback: use bridge warrant ceiling prior
    warrant = get_bridge_warrant(template)
    if warrant:
        warrant_upper = warrant.upper()
        if warrant_upper in BRIDGE_CEILINGS:
            ceiling_prior = BRIDGE_CEILINGS[warrant_upper]
            template["confidence"] = ceiling_prior
            log.add_change("Fix-C", f"Applied ceiling prior {ceiling_prior} for bridge_warrant '{warrant}'")
            return True

    return False


def fix_d1_music_i_mapping(template: Dict, log: RemediationLog) -> bool:
    """Fix D1: Map MUSIC-I non-canonical codes to canonical."""
    t1_frameworks = template.get("t1_frameworks", [])
    if not isinstance(t1_frameworks, list):
        return False

    changed = False
    new_frameworks = set()

    # First, add all existing canonical codes
    for code in t1_frameworks:
        if isinstance(code, str):
            code_str = code.strip()
            if code_str in T1_FRAMEWORKS:
                new_frameworks.add(code_str)

    # Then, map non-canonical codes
    for code in t1_frameworks:
        if isinstance(code, str):
            code_str = code.strip()
            if code_str in MUSIC_T1_MAP:
                # Add mapped canonical codes
                for mapped in MUSIC_T1_MAP[code_str]:
                    if mapped not in new_frameworks:
                        new_frameworks.add(mapped)
                        changed = True

    if changed:
        template["t1_frameworks"] = sorted(list(new_frameworks))
        log.add_change("Fix-D1", f"Mapped MUSIC-I non-canonical codes, result: {sorted(list(new_frameworks))}")
        return True

    return False


def fix_d2_crosscut_ax_citations(template: Dict, log: RemediationLog) -> bool:
    """Fix D2: CROSSCUT-I AX templates with citations-as-T1."""
    template_id = template.get("template_id")
    if not template_id or template_id not in CROSSCUT_AX_MAPPING:
        return False

    t1_frameworks = template.get("t1_frameworks", [])
    if not isinstance(t1_frameworks, list):
        t1_frameworks = []

    # Check if any entry is a long string (citation)
    has_citations = any(isinstance(f, str) and len(f) > 5 for f in t1_frameworks)

    if has_citations:
        # Move citations to key_references
        citations = [f for f in t1_frameworks if isinstance(f, str) and len(f) > 5]
        for citation in citations:
            if "key_references" not in template:
                template["key_references"] = []
            if citation not in template["key_references"]:
                template["key_references"].append(citation)

        # Replace with canonical codes
        canonical_codes = CROSSCUT_AX_MAPPING[template_id]
        template["t1_frameworks"] = canonical_codes
        log.add_change("Fix-D2", f"Moved {len(citations)} citations to key_references, set t1_frameworks to {canonical_codes}")
        return True

    return False


def fix_d3_missing_t1_frameworks(template: Dict, log: RemediationLog) -> bool:
    """Fix D3: Templates missing t1_frameworks entirely."""
    template_id = template.get("template_id")
    if not template_id or template_id not in MISSING_T1_MAP:
        return False

    # Only set if missing or empty
    t1_frameworks = template.get("t1_frameworks")
    if t1_frameworks and (isinstance(t1_frameworks, list) and t1_frameworks):
        return False

    canonical_codes = MISSING_T1_MAP[template_id]
    template["t1_frameworks"] = canonical_codes
    log.add_change("Fix-D3", f"Set missing t1_frameworks to {canonical_codes}")
    return True


def fix_e_normalize_legacy_fields(template: Dict, log: RemediationLog) -> bool:
    """Fix E: Normalize legacy field names."""
    changed = False

    # status -> calibration_status
    if "status" in template and "calibration_status" not in template:
        template["calibration_status"] = template.pop("status")
        log.add_change("Fix-E", "Renamed 'status' to 'calibration_status'")
        changed = True

    # template_name -> name
    if "template_name" in template and "name" not in template:
        template["name"] = template.pop("template_name")
        log.add_change("Fix-E", "Renamed 'template_name' to 'name'")
        changed = True

    # panel_id or panel -> panel_source
    if "panel_id" in template and "panel_source" not in template:
        template["panel_source"] = template.pop("panel_id")
        log.add_change("Fix-E", "Renamed 'panel_id' to 'panel_source'")
        changed = True
    elif "panel" in template and "panel_source" not in template:
        template["panel_source"] = template.pop("panel")
        log.add_change("Fix-E", "Renamed 'panel' to 'panel_source'")
        changed = True

    return changed


def apply_all_fixes(template: Dict, file_path: Path) -> RemediationLog:
    """Apply all applicable fixes to a calibrated template."""
    template_id = template.get("template_id", file_path.stem)
    log = RemediationLog(
        template_id=template_id,
        file_path=str(file_path.relative_to(PROJECT_ROOT))
    )

    # Check if calibrated
    status = get_calibration_status(template)
    if status != "calibrated":
        return log  # Skip non-calibrated templates

    # Apply fixes in order
    fix_a_compute_tier(template, log)
    fix_b_compute_bridge_warrant(template, log)
    fix_c_compute_confidence(template, log)
    fix_d1_music_i_mapping(template, log)
    fix_d2_crosscut_ax_citations(template, log)
    fix_d3_missing_t1_frameworks(template, log)
    fix_e_normalize_legacy_fields(template, log)

    return log


def remediate_all_templates() -> Tuple[int, List[RemediationLog], Dict[str, int]]:
    """
    Load all templates, apply fixes to calibrated ones, write back.

    Returns:
        (templates_modified, logs, fix_counts)
    """
    json_files = sorted(TEMPLATES_DIR.glob("*.json"))
    logs = []
    fix_counts = defaultdict(int)
    templates_modified = 0

    print(f"Processing {len(json_files)} template files...")
    print()

    for file_path in json_files:
        try:
            with open(file_path) as f:
                template = json.load(f)
        except json.JSONDecodeError as e:
            print(f"SKIP (JSON error): {file_path.name} — {e}", file=sys.stderr)
            continue

        log = apply_all_fixes(template, file_path)

        if log.changes:
            # Write modified template back
            try:
                with open(file_path, 'w') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                    f.write('\n')  # Add trailing newline
                templates_modified += 1
                logs.append(log)

                # Count fixes
                for change in log.changes:
                    fix_label = change.split(":")[0]
                    fix_counts[fix_label] += 1
            except Exception as e:
                print(f"WRITE ERROR: {file_path.name} — {e}", file=sys.stderr)
        else:
            logs.append(log)  # Keep zero-change logs for reporting

    return templates_modified, logs, fix_counts


def print_change_report(templates_modified: int, logs: List[RemediationLog], fix_counts: Dict[str, int]):
    """Print detailed change report."""
    print("=" * 70)
    print("REMEDIATION REPORT")
    print("=" * 70)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    print("SUMMARY")
    print("-" * 70)
    print(f"Templates modified: {templates_modified}")
    print()

    if fix_counts:
        print("FIXES APPLIED BY TYPE")
        print("-" * 70)
        for fix_label in sorted(fix_counts.keys()):
            count = fix_counts[fix_label]
            print(f"  {fix_label:10s}: {count:3d} applications")
        print()

    print("PER-TEMPLATE CHANGE LOG")
    print("-" * 70)

    modified_logs = [log for log in logs if log.changes]

    if modified_logs:
        for log in sorted(modified_logs, key=lambda x: x.template_id):
            print(f"\n{log.template_id}")
            for change in log.changes:
                print(f"  • {change}")
    else:
        print("No changes made (all templates already compliant or non-calibrated)")

    print()
    print("=" * 70)


def main():
    print("Comprehensive CMR Template Remediation")
    print("=" * 70)
    print(f"Starting at: {datetime.now(timezone.utc).isoformat()}")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print()

    templates_modified, logs, fix_counts = remediate_all_templates()

    print_change_report(templates_modified, logs, fix_counts)

    print(f"Completed at: {datetime.now(timezone.utc).isoformat()}")

    return 0 if templates_modified >= 0 else 1


if __name__ == "__main__":
    exit(main())
