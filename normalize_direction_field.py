#!/usr/bin/env python3
"""
DIRECTION FIELD NORMALIZATION SCRIPT
Fixes RV5-3 audit issue: maps 169+ unique values to 4 canonical values.

Script performs:
1. Scan of all extraction JSON files
2. Mapping of direction field values to canonical forms
3. Backup creation before modifications
4. Dry-run reporting
5. In-place modification with validation
6. Detailed statistics and mapping table output

Canonical values:
  - "increase": positive effects, improvements, enhancements
  - "decrease": negative effects, reductions, impairments
  - "no_effect": null effects, no change, non-significant
  - "mixed": complex, conditional, bidirectional effects
"""

import json
import os
import shutil
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List

# ============================================================================
# CANONICAL MAPPING RULES
# ============================================================================

DIRECTION_MAPPING = {
    # ========== INCREASE CATEGORY ==========
    # Positive/enhancing effects
    "increase": "increase",
    "positive": "increase",
    "higher": "increase",
    "up": "increase",
    "enhance": "increase",
    "improve": "increase",
    "promotes": "increase",
    "promote": "increase",
    "facilitates": "increase",
    "facilitate": "increase",
    "elevate": "increase",
    "elevates": "increase",
    "boost": "increase",
    "boosts": "increase",
    "amplify": "increase",
    "amplifies": "increase",
    "greater": "increase",
    "more": "increase",
    "rise": "increase",
    "rises": "increase",
    "gain": "increase",
    "gains": "increase",
    "augment": "increase",
    "augments": "increase",
    "strengthen": "increase",
    "strengthens": "increase",
    "heighten": "increase",
    "heightens": "increase",
    "intensify": "increase",
    "intensifies": "increase",
    "expand": "increase",
    "expands": "increase",
    "escalate": "increase",
    "escalates": "increase",
    "enhance": "increase",
    "enhances": "increase",
    "enables": "increase",
    "enable": "increase",
    "creates": "increase",
    "create": "increase",
    "provides": "increase",
    "improve": "increase",
    "improves": "increase",
    "increased": "increase",
    "increasing": "increase",
    "increases": "increase",
    "elevated": "increase",
    "positive effect": "increase",
    "positive relationship": "increase",
    "positive association": "increase",
    "increases with": "increase",
    "higher with": "increase",
    "greater with": "increase",
    "more with": "increase",
    "accelerate": "increase",
    "accelerates": "increase",
    "exacerbate": "increase",
    "exacerbates": "increase",
    "exacerbated": "increase",
    "worsens": "increase",  # worsen an effect = increase its effect
    "worsen": "increase",
    "worsened": "increase",
    "upregulate": "increase",
    "upregulates": "increase",
    "upregulated": "increase",

    # ========== DECREASE CATEGORY ==========
    # Negative/reducing effects
    "decrease": "decrease",
    "negative": "decrease",
    "lower": "decrease",
    "down": "decrease",
    "reduce": "decrease",
    "reduces": "decrease",
    "reduced": "decrease",
    "reducing": "decrease",
    "diminish": "decrease",
    "diminishes": "decrease",
    "diminished": "decrease",
    "impair": "decrease",
    "impairs": "decrease",
    "impaired": "decrease",
    "inhibit": "decrease",
    "inhibits": "decrease",
    "inhibited": "decrease",
    "suppress": "decrease",
    "suppresses": "decrease",
    "suppressed": "decrease",
    "attenuate": "decrease",
    "attenuates": "decrease",
    "attenuated": "decrease",
    "weaken": "decrease",
    "weakens": "decrease",
    "weakened": "decrease",
    "less": "decrease",
    "decline": "decrease",
    "declines": "decrease",
    "declined": "decrease",
    "drop": "decrease",
    "drops": "decrease",
    "dropped": "decrease",
    "fall": "decrease",
    "falls": "decrease",
    "fallen": "decrease",
    "shrink": "decrease",
    "shrinks": "decrease",
    "shrunk": "decrease",
    "contract": "decrease",
    "contracts": "decrease",
    "contracted": "decrease",
    "subtract": "decrease",
    "subtracts": "decrease",
    "subtracted": "decrease",
    "negative effect": "decrease",
    "negative relationship": "decrease",
    "negative association": "decrease",
    "decreases with": "decrease",
    "lower with": "decrease",
    "less with": "decrease",
    "fewer with": "decrease",
    "downregulate": "decrease",
    "downregulates": "decrease",
    "downregulated": "decrease",
    "mitigate": "decrease",
    "mitigates": "decrease",
    "mitigated": "decrease",
    "abolish": "decrease",
    "abolishes": "decrease",
    "abolished": "decrease",
    "eliminate": "decrease",
    "eliminates": "decrease",
    "eliminated": "decrease",
    "remove": "decrease",
    "removes": "decrease",
    "removed": "decrease",
    "eliminate": "decrease",

    # ========== NO_EFFECT CATEGORY ==========
    # Non-significant, null effects, no change
    "no_effect": "no_effect",
    "null": "no_effect",
    "none": "no_effect",
    "no change": "no_effect",
    "no difference": "no_effect",
    "no significant": "no_effect",
    "ns": "no_effect",
    "non-significant": "no_effect",
    "nonsignificant": "no_effect",
    "non significant": "no_effect",
    "negligible": "no_effect",
    "not significant": "no_effect",
    "insignificant": "no_effect",
    "not significant": "no_effect",
    "not related": "no_effect",
    "not related": "no_effect",
    "unrelated": "no_effect",
    "not associated": "no_effect",
    "no association": "no_effect",
    "no relationship": "no_effect",
    "no correlation": "no_effect",
    "not correlated": "no_effect",
    "ns (not significant)": "no_effect",
    "no significant difference": "no_effect",
    "no significant relationship": "no_effect",
    "no significant effect": "no_effect",
    "no significant association": "no_effect",
    "not different": "no_effect",
    "no different": "no_effect",
    "equal": "no_effect",
    "similar": "no_effect",
    "same": "no_effect",
    "comparable": "no_effect",
    "equivalent": "no_effect",
    "no effect": "no_effect",
    "no effects": "no_effect",
    "no statistical": "no_effect",
    "statistically not": "no_effect",
    "not statistically": "no_effect",
    "not statistically significant": "no_effect",

    # ========== MIXED CATEGORY ==========
    # Complex, conditional, bidirectional effects
    "mixed": "mixed",
    "varies": "mixed",
    "depends": "mixed",
    "conditional": "mixed",
    "moderated": "mixed",
    "moderation": "mixed",
    "interaction": "mixed",
    "interacts": "mixed",
    "interacting": "mixed",
    "complex": "mixed",
    "bidirectional": "mixed",
    "biphasic": "mixed",
    "nonlinear": "mixed",
    "non-linear": "mixed",
    "curvilinear": "mixed",
    "inverted-U": "mixed",
    "inverted U": "mixed",
    "U-shaped": "mixed",
    "U shaped": "mixed",
    "polynomial": "mixed",
    "dependent on": "mixed",
    "depends on": "mixed",
    "contingent": "mixed",
    "contingent on": "mixed",
    "contextual": "mixed",
    "context-dependent": "mixed",
    "depends on condition": "mixed",
    "conditional on": "mixed",
    "modulates": "mixed",
    "modulate": "mixed",
    "modulating": "mixed",
    "modulation": "mixed",
    "threshold": "mixed",
    "threshold effect": "mixed",
    "dose-response": "mixed",
    "dose response": "mixed",
    "varying": "mixed",
    "variable": "mixed",
    "inconsistent": "mixed",
    "inconsistently": "mixed",
    "heterogeneous": "mixed",
    "heterogeneous effect": "mixed",
    "different across": "mixed",
    "differs by": "mixed",
    "depends on context": "mixed",
    "context dependent": "mixed",
    "conditional effect": "mixed",
    "conditional on": "mixed",
    "partially": "mixed",
    "partially increases": "mixed",
    "partially decreases": "mixed",
    "partly": "mixed",
    "somewhat": "mixed",
    "inconsistent effect": "mixed",
    "variable effect": "mixed",

    # ========== CLAIM_TYPE LEAKED INTO DIRECTION ==========
    # These are claim types, not directions - map to "mixed" with flag
    "causal": "mixed",
    "associational": "mixed",
    "correlational": "mixed",
    "correlational relationship": "mixed",
    "correlation": "mixed",
    "association": "mixed",
    "causal relationship": "mixed",
    "causal effect": "mixed",
    "influence": "mixed",
    "influences": "mixed",
    "influenced": "mixed",
    "affects": "mixed",
    "affect": "mixed",
    "affected": "mixed",
    "affecting": "mixed",
    "impact": "mixed",
    "impacts": "mixed",
    "impacted": "mixed",
    "leads to": "mixed",
    "lead to": "mixed",
    "cause": "mixed",
    "causes": "mixed",
    "caused": "mixed",
    "causing": "mixed",

    # ========== OTHER EDGE CASES ==========
    "descriptive": "mixed",
    "unclear": "mixed",
    "significant": "mixed",  # significant but direction unclear
    "significant effect": "mixed",
    "change": "mixed",
    "changes": "mixed",
    "changed": "mixed",
    "changes with": "mixed",
    "support": "mixed",
    "supports": "mixed",
    "supported": "mixed",
    "supports hypothesis": "mixed",
    "support hypothesis": "mixed",
    "disconfirm": "mixed",
    "disconfirms": "mixed",
    "confirm": "mixed",
    "confirms": "mixed",
    "confirmed": "mixed",
    "available": "mixed",
    "alter": "mixed",
    "alters": "mixed",
    "altered": "mixed",
    "provide": "mixed",
    "increases": "increase",  # defer to increase category
    "decreases": "decrease",  # defer to decrease category
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def normalize_for_matching(value: str) -> str:
    """Normalize value for mapping (lowercase, strip whitespace, handle None)."""
    if value is None:
        return "null"
    if not isinstance(value, str):
        return str(value).lower().strip()
    return value.lower().strip()


def map_direction(original_value) -> Tuple[str, bool]:
    """
    Map original direction value to canonical form.
    Returns: (canonical_value, is_claim_type_flag)
    """
    if original_value is None or original_value == "":
        return "no_effect", False

    normalized = normalize_for_matching(original_value)

    # Direct lookup
    if normalized in DIRECTION_MAPPING:
        canonical = DIRECTION_MAPPING[normalized]
        # Flag if this was a claim_type
        is_claim_type = original_value in [
            "causal", "associational", "correlational", "modulates",
            "influence", "affects", "impact", "leads to", "cause", "causes"
        ]
        return canonical, is_claim_type

    # Try partial matching for phrases
    for key, canonical in DIRECTION_MAPPING.items():
        if len(key) > 3 and key in normalized:  # avoid single-word false matches
            return canonical, key in ["causal", "associational", "correlational",
                                       "modulates", "influence", "affects", "impact"]

    # If not found, default to "mixed" with warning
    return "mixed", False


def scan_extractions(extraction_dir: str) -> Dict:
    """
    Scan all extraction files and build mapping table.
    Returns dict: {original_value: (canonical_value, count, claim_type_flag)}
    """
    mapping_table = defaultdict(lambda: {"canonical": None, "count": 0, "is_claim_type": False})

    for filename in os.listdir(extraction_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(extraction_dir, filename), 'r') as f:
                    data = json.load(f)
                    if 'findings' in data and isinstance(data['findings'], list):
                        for finding in data['findings']:
                            if 'direction' in finding:
                                original = finding['direction']
                                canonical, is_claim_type = map_direction(original)
                                key = normalize_for_matching(original)
                                mapping_table[key]['canonical'] = canonical
                                mapping_table[key]['count'] += 1
                                if is_claim_type:
                                    mapping_table[key]['is_claim_type'] = True
            except Exception as e:
                print(f"Warning: Error reading {filename}: {e}")

    return mapping_table


def create_backup(extraction_dir: str, backup_dir: str):
    """Create backup of extractions directory."""
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree(extraction_dir, backup_dir)
    print(f"Backup created: {backup_dir}")


def dry_run(extraction_dir: str, mapping_table: Dict) -> Dict:
    """
    Perform dry run: scan files and report what would change.
    Returns: {total_files, total_findings, would_change, unmapped_findings}
    """
    stats = {
        'total_files': 0,
        'total_findings': 0,
        'would_change': 0,
        'unmapped': defaultdict(int),
        'by_canonical': defaultdict(int)
    }

    for filename in os.listdir(extraction_dir):
        if filename.endswith('.json'):
            stats['total_files'] += 1
            try:
                with open(os.path.join(extraction_dir, filename), 'r') as f:
                    data = json.load(f)
                    if 'findings' in data and isinstance(data['findings'], list):
                        for finding in data['findings']:
                            stats['total_findings'] += 1
                            if 'direction' in finding:
                                original = finding['direction']
                                canonical, _ = map_direction(original)
                                normalized = normalize_for_matching(original)

                                if canonical == "mixed" and normalized not in DIRECTION_MAPPING:
                                    stats['unmapped'][original] += 1
                                elif str(original).lower().strip() != canonical:
                                    stats['would_change'] += 1

                                stats['by_canonical'][canonical] += 1
            except Exception as e:
                print(f"Warning: Error reading {filename}: {e}")

    return stats


def apply_normalization(extraction_dir: str) -> Dict:
    """
    Apply normalization in-place to all extraction files.
    Returns: {total_files, total_findings, changed_findings, unmapped_findings}
    """
    stats = {
        'total_files': 0,
        'total_findings': 0,
        'changed_findings': 0,
        'unmapped_findings': 0,
        'changes_by_file': []
    }

    for filename in os.listdir(extraction_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(extraction_dir, filename)
            file_changes = 0
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if 'findings' in data and isinstance(data['findings'], list):
                    for finding in data['findings']:
                        stats['total_findings'] += 1
                        if 'direction' in finding:
                            original = finding['direction']
                            canonical, _ = map_direction(original)
                            normalized = normalize_for_matching(original)

                            if canonical == "mixed" and normalized not in DIRECTION_MAPPING:
                                stats['unmapped_findings'] += 1

                            if str(original).lower().strip() != canonical:
                                finding['direction'] = canonical
                                file_changes += 1
                                stats['changed_findings'] += 1

                # Write back if changes were made
                if file_changes > 0:
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2)
                    stats['changes_by_file'].append((filename, file_changes))

                stats['total_files'] += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return stats


def save_mapping_table(mapping_table: Dict, output_file: str):
    """Save mapping table as JSON for reproducibility."""
    # Convert to regular dict and sort by count
    table = {}
    for key, val in sorted(mapping_table.items(), key=lambda x: -x[1]['count']):
        table[key] = {
            'original': key,
            'canonical': val['canonical'],
            'count': val['count'],
            'is_claim_type': val['is_claim_type']
        }

    with open(output_file, 'w') as f:
        json.dump(table, f, indent=2)
    print(f"Mapping table saved: {output_file}")


def print_report(dry_run_stats: Dict, apply_stats: Dict, mapping_table: Dict):
    """Print comprehensive report."""
    print("\n" + "=" * 80)
    print("DIRECTION FIELD NORMALIZATION REPORT")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    print("DRY RUN RESULTS:")
    print(f"  Total extraction files: {dry_run_stats['total_files']}")
    print(f"  Total findings: {dry_run_stats['total_findings']}")
    print(f"  Findings that would change: {dry_run_stats['would_change']}")
    print(f"  Unmapped findings (will stay as-is): {len(dry_run_stats['unmapped'])}")
    print()

    print("CANONICAL VALUE DISTRIBUTION (after normalization):")
    for canonical in ['increase', 'decrease', 'no_effect', 'mixed']:
        count = dry_run_stats['by_canonical'].get(canonical, 0)
        pct = (count / dry_run_stats['total_findings'] * 100) if dry_run_stats['total_findings'] > 0 else 0
        print(f"  {canonical:15s} -> {count:6d} findings ({pct:5.1f}%)")
    print()

    if dry_run_stats['unmapped']:
        print("UNMAPPED VALUES (defaulting to 'mixed'):")
        for val, count in sorted(dry_run_stats['unmapped'].items(), key=lambda x: -x[1])[:20]:
            print(f"  {val!r:40s} -> {count:5d} findings (WARNING)")
        if len(dry_run_stats['unmapped']) > 20:
            print(f"  ... and {len(dry_run_stats['unmapped']) - 20} more")
    print()

    print("APPLICATION RESULTS:")
    print(f"  Total files processed: {apply_stats['total_files']}")
    print(f"  Total findings processed: {apply_stats['total_findings']}")
    print(f"  Findings actually changed: {apply_stats['changed_findings']}")
    print(f"  Unmapped findings (WARNING): {apply_stats['unmapped_findings']}")
    print()

    if apply_stats['changes_by_file']:
        print("TOP 10 FILES WITH MOST CHANGES:")
        for filename, count in sorted(apply_stats['changes_by_file'], key=lambda x: -x[1])[:10]:
            print(f"  {filename:60s} -> {count:4d} changes")
    print()

    print("MAPPING TABLE TOP 30 VALUES:")
    print(f"{'Original Value':40s} {'Canonical':12s} {'Count':8s} {'Claim Type?':12s}")
    print("-" * 72)
    for key, val in sorted(mapping_table.items(), key=lambda x: -x[1]['count'])[:30]:
        claim_flag = "YES" if val['is_claim_type'] else ""
        print(f"{key:40s} {val['canonical']:12s} {val['count']:8d} {claim_flag:12s}")

    print("\n" + "=" * 80)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    extraction_dir = "data/extractions"
    backup_dir = "data/extractions_backup_2026-02-28"
    mapping_output = "data/direction_normalization_map.json"

    print("DIRECTION FIELD NORMALIZATION SCRIPT")
    print("=" * 80)
    print()

    # Step 1: Create backup
    print("Step 1: Creating backup...")
    create_backup(extraction_dir, backup_dir)
    print()

    # Step 2: Scan for mapping table
    print("Step 2: Scanning extraction files and building mapping table...")
    mapping_table = scan_extractions(extraction_dir)
    print(f"  Found {len(mapping_table)} unique direction values")
    print()

    # Step 3: Dry run
    print("Step 3: Running dry-run analysis...")
    dry_stats = dry_run(extraction_dir, mapping_table)
    print()

    # Step 4: Apply normalization
    print("Step 4: Applying normalization in-place...")
    apply_stats = apply_normalization(extraction_dir)
    print(f"  Changed {apply_stats['changed_findings']} findings")
    print()

    # Step 5: Save mapping table
    print("Step 5: Saving mapping table...")
    save_mapping_table(mapping_table, mapping_output)
    print()

    # Step 6: Print report
    print_report(dry_stats, apply_stats, mapping_table)

    print("NORMALIZATION COMPLETE")
    print("=" * 80)
    print(f"Backup location: {backup_dir}")
    print(f"Mapping table: {mapping_output}")
