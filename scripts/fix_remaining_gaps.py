#!/usr/bin/env python3
"""
Fix remaining data quality gaps in calibrated templates.

GAP 1: 15 calibrated templates with empty t1_frameworks
- Assign based on mechanistic content

GAP 2: 23 calibrated templates with no root-level confidence
- Compute as mean of step-level confidences
- Use defaults by bridge_warrant type if steps lack confidence
"""

import json
import glob
import os
from pathlib import Path
from statistics import mean

# Default confidences by bridge_warrant type
BRIDGE_DEFAULTS = {
    'CONSTITUTIVE': 0.70,
    'MECHANISM': 0.55,
    'EMPIRICAL_ASSOCIATION': 0.50,
    'FUNCTIONAL': 0.45,
    'CAPACITY': 0.40,
    'ANALOGICAL': 0.30,
    'THEORY_DERIVED': 0.35,
}

# Mapping of template IDs/filenames to t1_frameworks
T1_MAPPING = {
    # MEMORY-I templates (hippocampal/memory systems)
    'ED_HIPPOCAMPAL_ENCODING_001': ['MS', 'SN'],
    'ED_PATTERN_SEP_COMP_001': ['MS', 'PP'],
    'ED_PE_ENCODING_PRINCIPLE_001': ['MS', 'PP'],
    'ED_RECONSOLIDATION_001': ['MS'],
    'ED_SCHEMA_ENCODING_001': ['MS', 'PP'],
    'ED_SYSTEMS_CONSOLIDATION_001': ['MS'],
    'THRESHOLD_EPISODIC_BOUNDARY_001': ['MS', 'SN'],
    
    # VISUAL-I templates (predictive processing in visual cortex)
    'LUM_CONTRAST_PE_001': ['PP'],
    'PP_SPECTRAL_MATCH_001': ['PP'],
    'PP_COMPLEXITY_GOLDILOCKS_002': ['PP'],
    'PP_RAPID_GIST_004': ['PP'],
    'VF1_CONTOUR_PE_001': ['PP'],
    'VF2_VISUAL_RHYTHM_001': ['PP'],
    'VF3_SPATIAL_PROPORTIONS_001': ['PP'],
    
    # Alternative naming patterns for visual templates
    'L1_luminance_contrast_pe': ['PP'],
    'VF1_contour_pe_curvature': ['PP'],
    'VF2_visual_rhythm_scaling': ['PP'],
    'VF3': ['PP'],
    
    # Architecture/thermal templates (predictive processing + neuromodulation)
    'T1': ['PP', 'NM'],
    'T2': ['PP', 'NM'],
    'T22': ['PP', 'NM'],
    
    # SOCIAL-I - nature view
    'VIEW1': ['PP', 'NM', 'IC'],
    'NATURE_VIEW_CONVERGENCE_001': ['PP', 'NM', 'IC'],
}

def get_template_id(template_obj, filepath):
    """Extract template ID from object or filepath."""
    tid = template_obj.get('id')
    if tid:
        return tid
    # Try to extract from filename
    filename = os.path.basename(filepath)
    # Remove .json extension
    return filename.replace('.json', '')

def compute_confidence_from_chain(template_obj):
    """
    Compute confidence as mean of step-level confidences.
    Use defaults if steps lack confidence.
    """
    mechanism_chain = template_obj.get('mechanism_chain', [])
    if not mechanism_chain:
        # No chain means we can't compute - return None
        return None
    
    confidences = []
    for step in mechanism_chain:
        step_conf = step.get('confidence')
        if step_conf is not None:
            confidences.append(step_conf)
        else:
            # Use default based on bridge_warrant
            bridge_warrant = step.get('bridge_warrant')
            if bridge_warrant and bridge_warrant in BRIDGE_DEFAULTS:
                confidences.append(BRIDGE_DEFAULTS[bridge_warrant])
            else:
                # Ultimate fallback
                confidences.append(0.50)
    
    if confidences:
        return round(mean(confidences), 2)
    return None

def fix_templates():
    """Fix both GAP 1 (t1_frameworks) and GAP 2 (confidence)."""
    
    template_dir = Path('/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates')
    template_files = list(template_dir.glob('*.json'))
    
    gap1_fixed = 0
    gap2_fixed = 0
    errors = []
    
    for tpath in template_files:
        try:
            with open(tpath, 'r') as f:
                template = json.load(f)
        except Exception as e:
            errors.append(f"Failed to load {tpath}: {e}")
            continue
        
        # Check if calibrated
        is_calibrated = (
            template.get('calibration_status') == 'calibrated' or
            template.get('status') == 'calibrated' or
            template.get('calibrated', False)
        )
        
        if not is_calibrated:
            continue
        
        # Get template ID/filename
        tid = get_template_id(template, str(tpath))
        
        # GAP 1: Fix empty t1_frameworks
        if not template.get('t1_frameworks'):
            # Try exact match first, then try without extension
            mapping_key = None
            if tid in T1_MAPPING:
                mapping_key = tid
            else:
                # Try without .json
                base_tid = tid.replace('.json', '')
                if base_tid in T1_MAPPING:
                    mapping_key = base_tid
            
            if mapping_key:
                template['t1_frameworks'] = T1_MAPPING[mapping_key]
                gap1_fixed += 1
                print(f"GAP 1: {tid} -> {T1_MAPPING[mapping_key]}")
        
        # GAP 2: Fix missing confidence
        if template.get('confidence') is None:
            new_conf = compute_confidence_from_chain(template)
            if new_conf is not None:
                template['confidence'] = new_conf
                gap2_fixed += 1
                print(f"GAP 2: {tid} -> confidence={new_conf}")
        
        # Write back
        try:
            with open(tpath, 'w') as f:
                json.dump(template, f, indent=2)
        except Exception as e:
            errors.append(f"Failed to write {tpath}: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"GAP 1 (t1_frameworks): {gap1_fixed} fixed")
    print(f"GAP 2 (confidence): {gap2_fixed} fixed")
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors[:5]:
            print(f"  - {err}")

if __name__ == '__main__':
    fix_templates()
