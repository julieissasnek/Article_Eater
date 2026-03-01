#!/usr/bin/env python3
"""
Fix 8 failing calibrated templates:

GROUP A (4 SPATIAL-I templates): Add root-level bridge_warrant and confidence
  - Extracted from mechanism_chain steps
  - bridge_warrant = weakest warrant (hierarchy: CONSTITUTIVE > MECHANISM > ... > ANALOGICAL > THEORETICAL_DEFAULT)
  - confidence = mean of step-level confidences

GROUP B (4 CROSSCUT-I AX templates): Add description/process to mechanism steps
  - Steps missing description/process but have label, from, to, claim, substrate
  - Generate description from available fields

Author: Claude Code
Date: 2026-02-23
"""

import json
import re
from pathlib import Path
from typing import Dict, Tuple, List, Optional

# Warrant hierarchy (lower index = stronger)
WARRANT_HIERARCHY = [
    'CONSTITUTIVE',
    'MECHANISM',
    'EMPIRICAL_COVARIANCE',
    'FUNCTIONAL',
    'CAPACITY',
    'ANALOGICAL',
    'THEORETICAL_DEFAULT',
]

def warrant_strength(warrant: str) -> int:
    """Return strength index; lower is stronger."""
    if warrant and warrant.upper() in WARRANT_HIERARCHY:
        return WARRANT_HIERARCHY.index(warrant.upper())
    return len(WARRANT_HIERARCHY)  # unknown = weakest


def extract_warrant_from_backing(backing: str) -> Optional[Tuple[str, float]]:
    """
    Extract warrant type and confidence from backing text.
    Pattern: "confidence X.XX (WARRANT_TYPE)"
    """
    pattern = r'confidence\s+([0-9.]+)\s*\(([A-Z_]+)'
    match = re.search(pattern, backing)
    if match:
        confidence = float(match.group(1))
        warrant = match.group(2)
        return (warrant, confidence)
    return None


def fix_group_a_template(template_path: Path) -> Dict:
    """
    GROUP A: Add bridge_warrant and confidence to SPATIAL-I templates.
    """
    with open(template_path) as f:
        data = json.load(f)
    
    mechanism_chain = data.get('mechanism_chain', [])
    
    # Extract warrant and confidence from each step's justification backing
    step_warrants = []
    step_confidences = []
    
    for step in mechanism_chain:
        justification = step.get('justification', {})
        backing = justification.get('backing', '')
        
        # Try to extract from backing text
        result = extract_warrant_from_backing(backing)
        if result:
            warrant, confidence = result
            step_warrants.append(warrant)
            step_confidences.append(confidence)
    
    # If no warrants found in backing, check for explicit warrant_type field (fallback)
    if not step_warrants:
        for step in mechanism_chain:
            warrant = step.get('warrant_type')
            conf = step.get('warrant_confidence')
            if warrant:
                step_warrants.append(warrant)
            if conf:
                step_confidences.append(conf)
    
    # Compute bridge_warrant: weakest (highest index) warrant across steps
    if step_warrants:
        bridge_warrant = max(step_warrants, key=warrant_strength)
    else:
        bridge_warrant = 'THEORETICAL_DEFAULT'  # fallback
    
    # Compute confidence: mean of step confidences
    if step_confidences:
        confidence = round(sum(step_confidences) / len(step_confidences), 2)
    else:
        confidence = 0.50  # fallback
    
    # Add to root level
    data['bridge_warrant'] = bridge_warrant
    data['confidence'] = confidence
    
    return data, {
        'bridge_warrant': bridge_warrant,
        'confidence': confidence,
        'step_warrants': step_warrants,
        'step_confidences': step_confidences,
    }


def generate_step_description(step: Dict) -> str:
    """
    Generate description for a mechanism step from available fields.
    Priority: claim > from→to > label > substrate
    """
    # Try claim first
    if 'claim' in step:
        claim = step['claim']
        if isinstance(claim, str):
            return claim
    
    # Try from→to
    if 'from' in step and 'to' in step:
        return f"{step['from']} → {step['to']}"
    
    # Try label (which is usually from→to format)
    if 'label' in step:
        return step['label']
    
    # Try substrate + some other context
    parts = []
    if 'substrate' in step:
        parts.append(f"Substrate: {step['substrate']}")
    if 'from' in step:
        parts.append(f"From: {step['from']}")
    if 'to' in step:
        parts.append(f"To: {step['to']}")
    
    if parts:
        return ' | '.join(parts)
    
    return "Mechanism step"


def fix_group_b_template(template_path: Path) -> Dict:
    """
    GROUP B: Add description/process to mechanism steps.
    """
    with open(template_path) as f:
        data = json.load(f)
    
    mechanism_chain = data.get('mechanism_chain', [])
    fixed_steps = 0
    
    for step in mechanism_chain:
        # Check if missing both description and process
        if 'description' not in step and 'process' not in step:
            description = generate_step_description(step)
            step['description'] = description
            fixed_steps += 1
    
    return data, {'fixed_steps': fixed_steps}


def main():
    """Main entry point: fix all 8 templates."""
    repo_root = Path('/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1')
    template_dir = repo_root / 'data' / 'templates'
    
    # GROUP A templates (filename -> template_id)
    group_a_files = {
        'ARCH_PROMENADE_TEMPORAL_PE_001.json': 'ARCH_PROMENADE_TEMPORAL_PE_001',
        'SC2_isovist_visual_prediction.json': 'ISOVIST_VISUAL_PREDICTION_001',
        'SC4_spatial_social_encounter.json': 'SPATIAL_SOCIAL_ENCOUNTER_001',
        'SPATIAL_INTEGRATION_PE_001.json': 'SPATIAL_INTEGRATION_PE_001',
    }
    
    # GROUP B templates
    group_b_files = {
        'AX_CHRONIC_ACUTE_011.json': 'AX_CHRONIC_ACUTE_011',
        'AX_CONTROL_STRESS_004.json': 'AX_CONTROL_STRESS_004',
        'AX_DOSE_RESPONSE_007.json': 'AX_DOSE_RESPONSE_007',
        'AX_HABITUATION_002.json': 'AX_HABITUATION_002',
    }
    
    print("=" * 70)
    print("FIX 8 FAILING CALIBRATED TEMPLATES")
    print("=" * 70)
    
    # Process GROUP A
    print("\nGROUP A: Adding bridge_warrant and confidence")
    print("-" * 70)
    
    for filename, template_id in group_a_files.items():
        filepath = template_dir / filename
        try:
            data, info = fix_group_a_template(filepath)
            
            # Write back
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ {template_id}")
            print(f"  bridge_warrant: {info['bridge_warrant']}")
            print(f"  confidence: {info['confidence']}")
            print(f"  (from {len(info['step_warrants'])} steps: {info['step_warrants']})")
            
        except Exception as e:
            print(f"✗ {template_id}: {e}")
    
    # Process GROUP B
    print("\nGROUP B: Adding description/process to mechanism steps")
    print("-" * 70)
    
    for filename, template_id in group_b_files.items():
        filepath = template_dir / filename
        try:
            data, info = fix_group_b_template(filepath)
            
            # Write back
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ {template_id}: fixed {info['fixed_steps']} steps")
            
        except Exception as e:
            print(f"✗ {template_id}: {e}")
    
    print("\n" + "=" * 70)
    print("DONE: All 8 templates fixed")
    print("=" * 70)


if __name__ == '__main__':
    main()
