#!/usr/bin/env python3
"""
Apply ceiling panel decisions to template files.

Decision Types:
- A: Upgrade warrant (change bridge_warrant to new_warrant)
- B: Accept override (add ceiling_override_rationale field)
- C: Reduce confidence (adjust confidence value; should be 0 of these)

After applying changes, recalculates root-level bridge_warrant as the weakest
across all steps in the mechanism_chain.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / 'data'
TEMPLATES_DIR = DATA_DIR / 'templates'
DECISIONS_FILE = DATA_DIR / 'ceiling_decisions.json'
REPORT_FILE = REPO_ROOT / 'CEILING_DECISIONS_APPLICATION_REPORT.txt'

# Warrant hierarchy (for recalculating root bridge_warrant)
WARRANT_HIERARCHY = {
    'EMPIRICAL_ASSOCIATION': 1,
    'MECHANISM': 2,
    'CONSTITUTIVE': 3,
}

def load_decisions() -> Dict:
    """Load ceiling decisions from JSON."""
    with open(DECISIONS_FILE) as f:
        return json.load(f)

def load_template(template_id: str) -> Tuple[Dict, str]:
    """Load a template by ID. Returns (template_data, filepath)."""
    template_path = TEMPLATES_DIR / f'{template_id}.json'
    if not template_path.exists():
        return None, None
    
    with open(template_path) as f:
        return json.load(f), str(template_path)

def apply_decision(template: Dict, step_num: int, decision_type: str, 
                   new_warrant: str = None, rationale: str = None) -> Tuple[bool, str]:
    """
    Apply a single ceiling decision to a template's mechanism_chain step.
    
    Returns (success, message)
    """
    if 'mechanism_chain' not in template:
        return False, f"No mechanism_chain found"
    
    chain = template['mechanism_chain']
    
    # Find the step by step number
    step = None
    step_idx = None
    for i, s in enumerate(chain):
        if s.get('step') == step_num:
            step = s
            step_idx = i
            break
    
    if step is None:
        return False, f"Step {step_num} not found in mechanism_chain"
    
    if decision_type == 'A':
        # Decision A: Upgrade warrant
        if new_warrant is None:
            return False, f"Decision A requires new_warrant"
        old_warrant = step.get('warrant')
        step['warrant'] = new_warrant
        return True, f"Step {step_num}: warrant upgraded {old_warrant} -> {new_warrant}"
    
    elif decision_type == 'B':
        # Decision B: Accept override (add ceiling_override_rationale)
        if rationale is None:
            return False, f"Decision B requires rationale"
        step['ceiling_override_rationale'] = rationale
        return True, f"Step {step_num}: override rationale added"
    
    elif decision_type == 'C':
        # Decision C: Reduce confidence
        if new_warrant is None:
            return False, f"Decision C requires confidence value in new_warrant field"
        old_conf = step.get('confidence')
        step['confidence'] = new_warrant  # new_warrant contains the confidence value
        return True, f"Step {step_num}: confidence reduced {old_conf} -> {new_warrant}"
    
    return False, f"Unknown decision type: {decision_type}"

def recalculate_bridge_warrant(template: Dict) -> str:
    """
    Recalculate root-level bridge_warrant as the weakest warrant in mechanism_chain.
    Returns the weakest warrant.
    """
    if 'mechanism_chain' not in template or not template['mechanism_chain']:
        return template.get('bridge_warrant', 'EMPIRICAL_ASSOCIATION')
    
    warrants = [step.get('warrant', 'EMPIRICAL_ASSOCIATION') 
                for step in template['mechanism_chain']]
    
    # Find the weakest (lowest hierarchy value)
    weakest = min(warrants, key=lambda w: WARRANT_HIERARCHY.get(w, 0))
    
    template['bridge_warrant'] = weakest
    return weakest

def main():
    """Main execution."""
    print("Loading ceiling decisions...")
    decisions_data = load_decisions()
    decisions = decisions_data['decisions']
    
    # Group by template_id
    by_template: Dict[str, List] = defaultdict(list)
    for dec in decisions:
        by_template[dec['template_id']].append(dec)
    
    # Apply decisions
    changes_by_template = defaultdict(lambda: {'decisions': [], 'bridge_recalc': None})
    template_files_modified = set()
    
    for template_id, template_decisions in by_template.items():
        template_data, filepath = load_template(template_id)
        
        if template_data is None:
            print(f"[SKIP] {template_id}: File not found")
            continue
        
        print(f"\nProcessing {template_id}...")
        
        for dec in template_decisions:
            step = dec['step']
            decision_type = dec['decision']
            new_warrant = dec.get('new_warrant')
            rationale = dec.get('rationale')
            
            success, msg = apply_decision(
                template_data, step, decision_type, new_warrant, rationale
            )
            
            if success:
                print(f"  [OK] {msg}")
                changes_by_template[template_id]['decisions'].append({
                    'step': step,
                    'type': decision_type,
                    'message': msg
                })
            else:
                print(f"  [FAIL] Step {step}: {msg}")
        
        # Recalculate bridge_warrant if any decisions were applied
        if changes_by_template[template_id]['decisions']:
            old_warrant = template_data.get('bridge_warrant')
            new_warrant = recalculate_bridge_warrant(template_data)
            
            if old_warrant != new_warrant:
                print(f"  [RECALC] bridge_warrant: {old_warrant} -> {new_warrant}")
                changes_by_template[template_id]['bridge_recalc'] = {
                    'old': old_warrant,
                    'new': new_warrant
                }
            
            # Write template back to file
            with open(filepath, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            template_files_modified.add(template_id)
            print(f"  [SAVED] {filepath}")
    
    # Generate report
    print("\n" + "="*80)
    print("GENERATING REPORT")
    print("="*80)
    
    with open(REPORT_FILE, 'w') as f:
        f.write("CEILING DECISIONS APPLICATION REPORT\n")
        f.write(f"Date: 2026-02-23\n")
        f.write(f"Total decision records: {len(decisions)}\n")
        f.write(f"Unique templates affected: {len(by_template)}\n")
        f.write(f"Templates successfully modified: {len(template_files_modified)}\n")
        f.write("\n" + "="*80 + "\n\n")
        
        # Summary by decision type
        type_counts = defaultdict(int)
        for dec in decisions:
            type_counts[dec['decision']] += 1
        
        f.write("DECISION TYPE SUMMARY\n")
        f.write("-" * 40 + "\n")
        for dtype in ['A', 'B', 'C']:
            count = type_counts.get(dtype, 0)
            if dtype == 'A':
                f.write(f"  A (warrant upgrade):      {count}\n")
            elif dtype == 'B':
                f.write(f"  B (accept override):      {count}\n")
            elif dtype == 'C':
                f.write(f"  C (confidence reduced):   {count}\n")
        f.write("\n")
        
        # Details by template
        f.write("TEMPLATE MODIFICATION DETAILS\n")
        f.write("-" * 40 + "\n\n")
        
        for template_id in sorted(changes_by_template.keys()):
            changes = changes_by_template[template_id]
            f.write(f"{template_id}:\n")
            
            if changes['decisions']:
                f.write(f"  Decisions Applied: {len(changes['decisions'])}\n")
                for dec in changes['decisions']:
                    f.write(f"    - Step {dec['step']} ({dec['type']}): {dec['message']}\n")
            
            if changes['bridge_recalc']:
                rc = changes['bridge_recalc']
                f.write(f"  Bridge Warrant Recalculated: {rc['old']} -> {rc['new']}\n")
            
            f.write("\n")
        
        # Summary
        f.write("\n" + "="*80 + "\n")
        f.write("SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Templates modified: {len(template_files_modified)}\n")
        f.write(f"Total decision records processed: {len(decisions)}\n")
        
        # Count changes by type
        type_applied = defaultdict(int)
        for changes in changes_by_template.values():
            for dec in changes['decisions']:
                type_applied[dec['type']] += 1
        
        f.write("\nChanges applied by type:\n")
        for dtype in ['A', 'B', 'C']:
            count = type_applied.get(dtype, 0)
            if dtype == 'A':
                f.write(f"  A (warrant upgrade):      {count}\n")
            elif dtype == 'B':
                f.write(f"  B (accept override):      {count}\n")
            elif dtype == 'C':
                f.write(f"  C (confidence reduced):   {count}\n")
    
    print(f"\nReport written to: {REPORT_FILE}")
    
    with open(REPORT_FILE) as f:
        print("\n" + f.read())

if __name__ == '__main__':
    main()
