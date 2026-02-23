#!/usr/bin/env python3
"""
Apply Toulmin justification layers to template mechanism steps.

Usage:
    python3 scripts/apply_toulmin_justification.py --panel STRESS-I --dry-run
    python3 scripts/apply_toulmin_justification.py --panel LIGHT-I

This script:
1. Reads all templates for a given panel from data/templates/
2. For each mechanism step, adds a 'justification' block containing:
   - data: array of empirical findings (source, paradigm, effect, n, design)
   - backing: narrative connecting the data to the warrant
   - qualifier: scope conditions and confidence rationale
   - rebuttal: conditions under which the claim would fail
   - competing_accounts: alternative explanations from panel debate
   - depth_tier: A (full), B (moderate), C (placeholder)
3. Writes the updated template back to disk

The justification content must be manually authored by reading the panel output
documents. This script provides the STRUCTURE and HELPERS for applying them.

Toulmin Schema Reference:
    docs/OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md

Panel Output Documents:
    docs/VISUAL_I_Panel_Output_Feb21.md     → TJ-03 (AG completed)
    docs/SPATIAL_I_Panel_Output_Feb21.md    → TJ-04 (AG completed)
    docs/LIGHT_I_Panel_Output_Feb21.md      → TJ-05 (CC assigned)
    docs/STRESS_I_Panel_Output_Feb21.md     → TJ-06 (CC assigned)
"""

import json
import glob
import argparse
import sys
import os

TEMPLATES_DIR = 'data/templates'


def find_templates_for_panel(panel_name: str) -> dict:
    """Find all templates belonging to a panel."""
    templates = {}
    panel_lower = panel_name.lower().replace('-', '').replace('_', '')
    
    for f in sorted(glob.glob(f'{TEMPLATES_DIR}/*.json')):
        with open(f) as fh:
            d = json.load(fh)
        
        # Check multiple panel identifier fields
        for field in ['source_panel', 'panel_source', 'panel']:
            val = str(d.get(field, '')).lower().replace('-', '').replace('_', '')
            if panel_lower in val:
                tid = d.get('template_id', os.path.basename(f))
                templates[tid] = {'path': f, 'data': d}
                break
    
    return templates


def classify_depth_tier(step_data: dict, competing_accounts: list) -> str:
    """Classify justification depth tier based on confidence and warrant."""
    conf = step_data.get('confidence', 0) or 0
    warrant = str(step_data.get('warrant', step_data.get('bridge_warrant', '')))
    
    if conf > 0.55 or 'MECHANISM' in warrant or len(competing_accounts) > 0:
        return 'A'  # Full depth — rich debate content
    elif conf >= 0.40:
        return 'B'  # Moderate depth
    return 'C'  # Placeholder or minimal


def make_data_entry(finding: str, source: str, paradigm: str = '',
                    effect: str = '', n=None, design: str = '') -> dict:
    """Create a standardized data entry for the Toulmin data array."""
    entry = {
        'finding': finding,
        'source': source,
        'paradigm': paradigm,
        'effect': effect,
        'n': n,
        'design': design
    }
    return entry


def make_justification(data: list, backing: str, qualifier: str,
                       rebuttal: str, competing_accounts: list = None) -> dict:
    """Create a complete Toulmin justification block."""
    return {
        'data': data,
        'backing': backing,
        'qualifier': qualifier,
        'rebuttal': rebuttal,
        'competing_accounts': competing_accounts or []
    }


def apply_justification_to_template(template_data: dict, 
                                     step_justifications: dict) -> int:
    """Apply justification blocks to mechanism chain steps.
    
    Args:
        template_data: The full template JSON dict
        step_justifications: Dict mapping step number → justification dict
        
    Returns:
        Number of steps updated
    """
    count = 0
    for step in template_data.get('mechanism_chain', []):
        sn = step.get('step')
        if sn in step_justifications:
            j = step_justifications[sn]
            j['depth_tier'] = classify_depth_tier(
                step, j.get('competing_accounts', [])
            )
            step['justification'] = j
            count += 1
    return count


def save_template(path: str, data: dict):
    """Write template JSON back to disk."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def report_panel_status(templates: dict):
    """Print summary of justification status for all templates."""
    total_steps = 0
    justified_steps = 0
    tier_counts = {'A': 0, 'B': 0, 'C': 0, 'none': 0}
    
    for tid, info in templates.items():
        chain = info['data'].get('mechanism_chain', [])
        total_steps += len(chain)
        for step in chain:
            j = step.get('justification')
            if j:
                justified_steps += 1
                tier = j.get('depth_tier', 'C')
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            else:
                tier_counts['none'] += 1
        
        print(f'  {tid}: {len(chain)} steps', end='')
        has_j = sum(1 for s in chain if 'justification' in s)
        if has_j:
            print(f' ({has_j} justified)', end='')
        print()
    
    print(f'\nTotal: {justified_steps}/{total_steps} steps justified')
    print(f'  Tier A (full): {tier_counts["A"]}')
    print(f'  Tier B (moderate): {tier_counts["B"]}')
    print(f'  Tier C (placeholder): {tier_counts["C"]}')
    print(f'  No justification: {tier_counts["none"]}')


def main():
    parser = argparse.ArgumentParser(
        description='Apply Toulmin justification to template mechanism steps'
    )
    parser.add_argument('--panel', required=True,
                       help='Panel name (e.g., STRESS-I, LIGHT-I)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Report status without modifying files')
    args = parser.parse_args()
    
    templates = find_templates_for_panel(args.panel)
    
    if not templates:
        print(f'No templates found for panel: {args.panel}')
        print(f'Available panels in {TEMPLATES_DIR}:')
        panels = set()
        for f in glob.glob(f'{TEMPLATES_DIR}/*.json'):
            with open(f) as fh:
                d = json.load(fh)
            for field in ['source_panel', 'panel_source', 'panel']:
                val = d.get(field, '')
                if val:
                    panels.add(str(val)[:50])
        for p in sorted(panels):
            print(f'  {p}')
        sys.exit(1)
    
    print(f'Panel: {args.panel}')
    print(f'Templates found: {len(templates)}')
    report_panel_status(templates)
    
    if args.dry_run:
        print('\n[DRY RUN] No files modified.')
        print('\nTo apply justifications, import this module and use:')
        print('  from scripts.apply_toulmin_justification import *')
        print('  templates = find_templates_for_panel("STRESS-I")')
        print('  j = make_justification(')
        print('      data=[make_data_entry("finding", "source", ...)],')
        print('      backing="...", qualifier="...", rebuttal="...",')
        print('      competing_accounts=[]')
        print('  )')
        print('  apply_justification_to_template(template_data, {1: j, 2: j2})')
        print('  save_template(path, template_data)')


if __name__ == '__main__':
    main()
