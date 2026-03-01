#!/usr/bin/env python3
"""
T1.5 Audit Script
================

Audits all calibrated templates to:
1. Identify FORMAL (reduced) T1.5 theories
2. Separate PLAUSIBLE_CANDIDATES (real but unreduced theories)
3. Flag and discard FABRICATED theories

Handles both simple string lists and rich dict structures.

Runs in two passes:
  - DRY RUN: Shows what would happen
  - APPLY: Actually modifies templates

Date: 2026-02-23
"""

import json
import glob
import collections
from pathlib import Path
from typing import Dict, List, Tuple, Set, Union, Any
import sys

# =============================================================================
# CANONICAL REGISTRIES
# =============================================================================

FORMAL_T1_5 = {
    # Original 4 (pre-Feb 2026)
    "ART": ["Attention_Restoration_Theory", "ART", "Attention_Restoration"],
    "SRT": ["Stress_Reduction_Theory", "SRT", "Stress_Recovery_Theory", "Stress_Reduction"],
    "Biophilia": ["Biophilia", "biophilia"],
    "Prospect_Refuge": ["Prospect_Refuge", "Prospect-Refuge", "prospect_refuge"],
    
    # Feb 20 reductions
    "Privacy_Regulation": ["Privacy_Regulation", "Privacy_Regulation_Theory"],
    "Kaplan_Preference_Matrix": ["Kaplan_Preference_Matrix", "Kaplan_Matrix"],
    "Adaptive_Thermal_Comfort": ["Adaptive_Thermal_Comfort"],
    
    # Feb 21 reductions  
    "Space_Syntax": ["Space_Syntax"],
    "Soundscape_Theory": ["Soundscape_Theory", "Soundscape", "Soundscape_Ecology", "ISO_12913_Soundscape"],
    "Place_Attachment": ["Place_Attachment"],
    
    # Also mentioned as reduced in TRANSFER_Feb23_Session9.md
    "Fractal_Fluency": ["Fractal_Fluency"],
    "Awe_Kama_Muta": ["Awe_Kama_Muta", "Awe_Theory", "Awe/Kama_Muta", "Kama_Muta"],
}

PLAUSIBLE_CANDIDATES = {
    "BRECVEMA",
    "Flow_Theory",
    "Episodic_Memory_Theory",
    "Cognitive_Map_Theory",
    "Berlyne_Arousal",
    "Proxemics",
    "Proxemics_Theory",
    "Mehrabian_Russell",
    "Chronobiology",
    "Allesthesia",
    "Defensible_Space",
    "CPTED",
    "Auditory_Scene_Analysis",
    "Predictive_Coding_Music",
    "Predictive_Coding_Vision",
    "Embodied_Cognition",
    "Gestalt_Theory",
    "Dynamic_Attending_Theory",
    "Mirror_Neuron_Theory",
    "Aesthetic_Emotion_Theory",
    "Sleep_Memory_Consolidation",
    "Systems_Consolidation_Theory",
    "Relational_Memory_Theory",
    "Event_Segmentation_Theory",
    "Schema_Theory",
    "Memory_Reconsolidation_Theory",
    "Reward_Prediction_Theory",
    "Free_Energy_Minimization",
    "Body_Budget_Model",
    "Affective_Neuroscience",
    "DMN_TPN_Theory",
    "Bayesian_Cue_Integration",
    "Multisensory_Integration_Theory",
    "Crossmodal_Correspondence",
    "Golden_Ratio_Theory",
    "Scene_Perception_Theory",
    "Ecological_Optics",
    "Contrast_Adaptation",
    "Attention_Theory",
    "Adaptive_Gain_Theory",
    "Safety_Signal_Theory",
    "Salience_Network_Theory",
    "Neural_Oscillation_Theory",
    "Working_Memory_Theory",
    "Temporal_Hierarchy_Theory",
    "Ecological_Rationality",
    "Bounded_Rationality",
    "Dual_Mechanisms_Control",
    "Thalamic_Gating_Theory",
    "Haptic_Perception_Theory",
    "Affective_Touch_Theory",
    "Material_Culture_Theory",
    "Wabi_Sabi",
    "Cultural_Neuroscience",
    "Identity_Theory",
    "Circadian_Architecture",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_theory_name(theory: Union[str, Dict]) -> str:
    """Extract theory name from either string or dict."""
    if isinstance(theory, str):
        return theory
    elif isinstance(theory, dict):
        return theory.get('name', '')
    return ''

def build_alias_map() -> Dict[str, str]:
    """Build case-insensitive alias → canonical name map."""
    alias_map = {}
    for canonical, aliases in FORMAL_T1_5.items():
        for alias in aliases:
            alias_map[alias.lower()] = canonical
    return alias_map

def classify_theory(theory_name: str, alias_map: Dict[str, str]) -> Tuple[str, str]:
    """
    Classify a theory name.
    
    Returns: (category, canonical_name_or_input)
      - ("FORMAL", "CanonicalName") if it matches a formal theory
      - ("CANDIDATE", theory_name) if it matches a plausible candidate
      - ("FABRICATED", theory_name) if it doesn't match either
    """
    if not theory_name:
        return ("FABRICATED", "(empty name)")
    
    # Try exact match to formal (with case-insensitive alias lookup)
    if theory_name.lower() in alias_map:
        canonical = alias_map[theory_name.lower()]
        return ("FORMAL", canonical)
    
    # Try exact match to plausible candidates
    if theory_name in PLAUSIBLE_CANDIDATES:
        return ("CANDIDATE", theory_name)
    
    # Try case-insensitive match to plausible candidates
    for candidate in PLAUSIBLE_CANDIDATES:
        if theory_name.lower() == candidate.lower():
            return ("CANDIDATE", candidate)
    
    # Fabricated
    return ("FABRICATED", theory_name)

def audit_template_dry_run(template_path: str, alias_map: Dict[str, str]) -> Dict:
    """
    Dry-run audit on a single template.
    
    Returns dict with:
      - is_calibrated: bool
      - formal_theories: list of canonical names (or [] if none)
      - candidates_moved: list of theory names to move
      - fabricated_discarded: list of theory names to discard
      - actions: list of action strings (for reporting)
    """
    try:
        with open(template_path) as f:
            data = json.load(f)
    except Exception as e:
        return {
            "is_calibrated": False,
            "error": str(e),
            "formal_theories": [],
            "candidates_moved": [],
            "fabricated_discarded": [],
            "actions": [],
        }
    
    is_calibrated = data.get('calibration_status') == 'calibrated' or data.get('calibrated', False)
    
    if not is_calibrated:
        return {
            "is_calibrated": False,
            "formal_theories": [],
            "candidates_moved": [],
            "fabricated_discarded": [],
            "actions": [],
        }
    
    # Get current t1_5_parent_theories
    current_theories = data.get('t1_5_parent_theories', [])
    
    formal_theories = []
    candidates_moved = []
    fabricated_discarded = []
    actions = []
    
    for theory in current_theories:
        theory_name = extract_theory_name(theory)
        category, canonical = classify_theory(theory_name, alias_map)
        
        if category == "FORMAL":
            if canonical not in formal_theories:
                formal_theories.append(canonical)
                if canonical != theory_name:
                    actions.append(f"  NORMALIZE: {theory_name} → {canonical}")
                else:
                    actions.append(f"  KEEP: {theory_name}")
        
        elif category == "CANDIDATE":
            candidates_moved.append(canonical)
            actions.append(f"  MOVE→CANDIDATE: {theory_name}")
        
        else:  # FABRICATED
            fabricated_discarded.append(theory_name)
            actions.append(f"  DISCARD: {theory_name} (fabricated)")
    
    return {
        "is_calibrated": True,
        "formal_theories": formal_theories,
        "candidates_moved": candidates_moved,
        "fabricated_discarded": fabricated_discarded,
        "actions": actions,
    }

def apply_audit_to_template(template_path: str, alias_map: Dict[str, str]) -> bool:
    """
    Actually apply the audit to a template.
    
    Returns: True if modified, False otherwise
    """
    try:
        with open(template_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR reading {template_path}: {e}")
        return False
    
    is_calibrated = data.get('calibration_status') == 'calibrated' or data.get('calibrated', False)
    
    if not is_calibrated:
        return False
    
    current_theories = data.get('t1_5_parent_theories', [])
    formal_theories = []
    candidates_moved = []
    
    for theory in current_theories:
        theory_name = extract_theory_name(theory)
        category, canonical = classify_theory(theory_name, alias_map)
        
        if category == "FORMAL":
            if canonical not in formal_theories:
                formal_theories.append(canonical)
        
        elif category == "CANDIDATE":
            if canonical not in candidates_moved:
                candidates_moved.append(canonical)
    
    # Update the template
    modified = False
    
    # Set formal theories (normalized to strings only)
    if data.get('t1_5_parent_theories') != formal_theories:
        data['t1_5_parent_theories'] = formal_theories
        modified = True
    
    # Create/update candidates field
    if candidates_moved:
        if data.get('t1_5_candidates') != candidates_moved:
            data['t1_5_candidates'] = candidates_moved
            modified = True
    else:
        # Remove candidates field if empty
        if 't1_5_candidates' in data:
            del data['t1_5_candidates']
            modified = True
    
    if modified:
        try:
            with open(template_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"ERROR writing {template_path}: {e}")
            return False
    
    return False

# =============================================================================
# MAIN
# =============================================================================

def main():
    repo_root = Path('/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1')
    template_dir = repo_root / 'data' / 'templates'
    
    if not template_dir.exists():
        print(f"ERROR: Template directory not found: {template_dir}")
        sys.exit(1)
    
    print("=" * 80)
    print("T1.5 AUDIT SCRIPT")
    print("=" * 80)
    print()
    
    # Build alias map
    alias_map = build_alias_map()
    print(f"Loaded {len(FORMAL_T1_5)} formal T1.5 theories")
    print(f"Loaded {len(PLAUSIBLE_CANDIDATES)} plausible candidates")
    print()
    
    # Find all templates
    template_files = sorted(glob.glob(str(template_dir / '*.json')))
    print(f"Found {len(template_files)} template files")
    print()
    
    # =============================================================================
    # PHASE 1: DRY RUN
    # =============================================================================
    print("=" * 80)
    print("PHASE 1: DRY RUN (no modifications)")
    print("=" * 80)
    print()
    
    dry_run_results = []
    for template_path in template_files:
        result = audit_template_dry_run(template_path, alias_map)
        if result['is_calibrated']:
            dry_run_results.append({
                'path': template_path,
                'filename': Path(template_path).name,
                'result': result,
            })
    
    # Summary statistics
    total_calibrated = len(dry_run_results)
    with_formal = sum(1 for r in dry_run_results if r['result']['formal_theories'])
    with_candidates = sum(1 for r in dry_run_results if r['result']['candidates_moved'])
    with_fabricated = sum(1 for r in dry_run_results if r['result']['fabricated_discarded'])
    
    print(f"DRY RUN SUMMARY:")
    print(f"  Calibrated templates: {total_calibrated}")
    print(f"  With formal T1.5: {with_formal}")
    print(f"  With candidates to move: {with_candidates}")
    print(f"  With fabricated labels to discard: {with_fabricated}")
    print()
    
    # Aggregate statistics
    all_formal = collections.Counter()
    all_candidates = collections.Counter()
    all_fabricated = collections.Counter()
    
    for r in dry_run_results:
        result = r['result']
        all_formal.update(result['formal_theories'])
        all_candidates.update(result['candidates_moved'])
        all_fabricated.update(result['fabricated_discarded'])
    
    print("FORMAL T1.5 THEORIES (retained):")
    if all_formal:
        for theory, count in all_formal.most_common():
            print(f"  {theory}: {count} templates")
    else:
        print("  (none)")
    print()
    
    print("PLAUSIBLE CANDIDATES (to be moved to t1_5_candidates):")
    if all_candidates:
        for theory, count in all_candidates.most_common(15):
            print(f"  {theory}: {count} templates")
        if len(all_candidates) > 15:
            print(f"  ... and {len(all_candidates) - 15} more")
    else:
        print("  (none)")
    print()
    
    print("FABRICATED LABELS (to be discarded):")
    if all_fabricated:
        for theory, count in all_fabricated.most_common():
            print(f"  {theory}: {count} occurrences")
    else:
        print("  (none - all theories are either formal or candidates)")
    print()
    
    # Offer to proceed
    print("=" * 80)
    print("Do you want to APPLY these changes? (y/n)")
    response = input("> ").strip().lower()
    
    if response != 'y':
        print("\nDry run complete. No changes applied.")
        return
    
    # =============================================================================
    # PHASE 2: APPLY
    # =============================================================================
    print()
    print("=" * 80)
    print("PHASE 2: APPLYING CHANGES")
    print("=" * 80)
    print()
    
    modified_count = 0
    for template_path in template_files:
        if apply_audit_to_template(template_path, alias_map):
            modified_count += 1
            print(f"✓ {Path(template_path).name}")
    
    print()
    print(f"Modified {modified_count} templates")
    print()
    
    # =============================================================================
    # VERIFICATION
    # =============================================================================
    print("=" * 80)
    print("VERIFICATION: Post-audit state")
    print("=" * 80)
    print()
    
    formal_count_after = collections.Counter()
    candidates_count_after = collections.Counter()
    empty_t1_5_count = 0
    
    for template_path in template_files:
        try:
            with open(template_path) as f:
                data = json.load(f)
            
            is_calibrated = data.get('calibration_status') == 'calibrated' or data.get('calibrated', False)
            if not is_calibrated:
                continue
            
            formal = data.get('t1_5_parent_theories', [])
            candidates = data.get('t1_5_candidates', [])
            
            if not formal:
                empty_t1_5_count += 1
            else:
                formal_count_after.update(formal)
            
            candidates_count_after.update(candidates)
        
        except Exception as e:
            print(f"ERROR reading {template_path}: {e}")
    
    print(f"Calibrated templates with formal T1.5: {total_calibrated - empty_t1_5_count}/{total_calibrated}")
    print(f"Calibrated templates with empty T1.5: {empty_t1_5_count}/{total_calibrated}")
    print()
    
    print("Formal theories in use (post-audit):")
    for k, v in formal_count_after.most_common():
        print(f"  {k}: {v}")
    print()
    
    print("Candidate theories in use (post-audit):")
    for k, v in candidates_count_after.most_common(15):
        print(f"  {k}: {v}")
    if len(candidates_count_after) > 15:
        print(f"  ... and {len(candidates_count_after) - 15} more")
    print()
    
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
