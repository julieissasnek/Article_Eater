#!/usr/bin/env python3
"""
Validator for mechanism integration norms as specified in PANEL_INTEGRATION_PROMPT-reusable.md.
Checks:
1. Mechanism chain step fields: step, from, to, description, warrant, confidence, justification
   (Also allows legacy aliases: process, substrate, bridge_warrant).
2. The three-factor credence formula:
   P(CNFA effect) = P(parent theory) x P(bridge) x P(CNFA-specific)
"""

import json
import sys
import argparse

def check_mechanism_step(step, idx):
    errors = []
    
    # Required fields per integration prompt
    # "each with `step`, `from`, `to`, `description`, `warrant`, `confidence`, `justification`"
    # We allow fallbacks for legacy templates being migrated.
    if 'step' not in step:
        errors.append(f"Step {idx}: Missing 'step'")
    
    if 'from' not in step and 'substrate' not in step:
        errors.append(f"Step {idx}: Missing 'from' (or 'substrate')")
    
    if 'to' not in step and 'process' not in step:
        errors.append(f"Step {idx}: Missing 'to' (or 'process')")
    
    if 'description' not in step and 'process' not in step:
        errors.append(f"Step {idx}: Missing 'description'")
        
    if 'warrant' not in step and 'bridge_warrant' not in step:
        errors.append(f"Step {idx}: Missing 'warrant' (or 'bridge_warrant')")
        
    if 'confidence' not in step:
        errors.append(f"Step {idx}: Missing 'confidence'")
        
    # The integration prompt requires 'justification'
    if 'justification' not in step:
        # Check if toulmin validator is meant to handle this exclusively, but prompt says it should be in the object
        errors.append(f"Step {idx}: Missing 'justification' object")
    elif isinstance(step.get('justification'), dict):
        j = step['justification']
        if 'data' not in j: errors.append(f"Step {idx}: justification missing 'data'")
        if 'backing' not in j: errors.append(f"Step {idx}: justification missing 'backing'")
        if 'qualifier' not in j: errors.append(f"Step {idx}: justification missing 'qualifier'")
        if 'rebuttal' not in j: errors.append(f"Step {idx}: justification missing 'rebuttal'")
        if 'competing_accounts' not in j: errors.append(f"Step {idx}: justification missing 'competing_accounts'")
        if 'depth_tier' not in j: errors.append(f"Step {idx}: justification missing 'depth_tier'")
        
    return errors

def check_three_factor_credence(template_data):
    errors = []
    # Check if the three-factor credence formula is present
    conf_obj = template_data.get('confidence_factors') or template_data.get('credence')
    
    # If not explicitly defined, check if we can infer from template root
    if not conf_obj:
        if 'parent_theory_confidence' in template_data and 'bridge_confidence' in template_data:
            conf_obj = template_data
        else:
            return [] # Not present
            
    p_parent = conf_obj.get('parent_theory', conf_obj.get('parent_theory_confidence', 1.0))
    p_bridge = conf_obj.get('bridge', conf_obj.get('bridge_confidence', 1.0))
    p_specific = conf_obj.get('cnfa_specific', conf_obj.get('cnfa_specific_confidence', 1.0))
    
    expected_composite = p_parent * p_bridge * p_specific
    
    # Check if the template top-level confidence matches the 3-factor calculation
    actual_confidence = template_data.get('confidence')
    
    if actual_confidence is not None:
        if abs(expected_composite - actual_confidence) > 0.05:
            errors.append(f"Three-factor credence formula violation: {p_parent} * {p_bridge} * {p_specific} = {expected_composite:.3f}, but template confidence is {actual_confidence}")
            
    return errors

def validate_template_integration_norms(file_path):
    print(f"Validating integration norms for {file_path}...")
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  Fail: Could not parse JSON: {e}")
        return False
        
    mechanisms = data.get('mechanism_chain', [])
    if not mechanisms:
        errors.append("No mechanism_chain found or it is empty.")
    else:
        for idx, step in enumerate(mechanisms):
            step_errors = check_mechanism_step(step, idx)
            errors.extend(step_errors)
            
    credence_errors = check_three_factor_credence(data)
    errors.extend(credence_errors)
    
    if not data.get('bridge_warrant'):
        # Check if any mechanism step has a bridge warrant since we need an overall one
        warrants = [s.get('bridge_warrant', s.get('warrant')) for s in mechanisms]
        if not any(warrants):
            errors.append("Template missing overall 'bridge_warrant' and no steps provide one.")
            
    if errors:
        print(f"  FAIL: {len(errors)} integration norm violations found:")
        for err in errors:
            print(f"    - {err}")
        return False
    else:
        print("  PASS: Mechanism integration norms satisfied.")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate mechanism integration norms")
    parser.add_argument("files", nargs="+", help="Template JSON files to validate")
    args = parser.parse_args()
    
    all_passed = True
    for fp in args.files:
        if not validate_template_integration_norms(fp):
            all_passed = False
            
    sys.exit(0 if all_passed else 1)
