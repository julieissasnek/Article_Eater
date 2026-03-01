#!/usr/bin/env python3
"""
assign_formal_t1_5.py

Apply panel results (Feb 23) to move BRECVEMA and Flow_Theory to formal T1.5
and clean up rejected theories from candidates.

Formal T1.5 Roster (14 theories):
  ART, SRT, Biophilia, Prospect_Refuge,
  Privacy_Regulation, Kaplan_Preference_Matrix, Adaptive_Thermal_Comfort,
  Space_Syntax, Soundscape_Theory, Place_Attachment,
  Fractal_Fluency, Awe_Kama_Muta, BRECVEMA, Flow_Theory
"""

import json
import glob
from pathlib import Path
from collections import defaultdict

FORMAL_ROSTER = {
    # Original 4
    "ART", "SRT", "Biophilia", "Prospect_Refuge",
    # Feb 20 reductions
    "Privacy_Regulation", "Kaplan_Preference_Matrix", "Adaptive_Thermal_Comfort",
    # Feb 21 reductions
    "Space_Syntax", "Soundscape_Theory", "Place_Attachment",
    # Earlier reductions
    "Fractal_Fluency", "Awe_Kama_Muta",
    # NEW from panel (Feb 23)
    "BRECVEMA", "Flow_Theory"
}

REJECTED = {
    "Free_Energy_Minimization", "Cognitive_Map_Theory", "Proxemics", "Proxemics_Theory",
    "Chronobiology", "Defensible_Space", "CPTED", "Allesthesia", "Mehrabian_Russell",
    "Circadian_Architecture"
}

DEFERRED = {
    "Episodic_Memory_Theory", "Berlyne_Arousal", "Predictive_Coding_Music", "Auditory_Scene_Analysis"
}

# Templates that should have BRECVEMA assigned
BRECVEMA_TEMPLATES = {
    "BRECVEMA_BRAINSTEM_001",
    "BRECVEMA_RHYTHMIC_ENTRAINMENT_002",
    "BRECVEMA_CONTAGION_003",
    "BRECVEMA_EXPECTANCY_004",
    "BRECVEMA_MEMORY_005",
    "BRECVEMA_MULTI_MECHANISM_001",
    "NEURAL_MUSIC_EMOTION_ARCH_001",
    "PLEASURABLE_SADNESS_001",
    "ACOUSTIC_EMOTION_MAPPING_001"
}

# Templates that should have Flow_Theory assigned
FLOW_TEMPLATES = {
    "INCUBATION_ARCHITECTURE_001",
    "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001",
    "CREATIVE_NETWORK_DYNAMICS_001",
    "CROSS_CREATIVE_NETWORK_DYNAMICS_001",
    "PROCESSING_STYLE_MODULATION_001"
}

def process_templates():
    """Process all calibrated templates."""
    template_dir = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/templates")
    templates = sorted(glob.glob(str(template_dir / "*.json")))
    
    stats = {
        "processed": 0,
        "brecvema_assigned": 0,
        "flow_assigned": 0,
        "rejected_removed": 0,
        "deferred_kept": 0,
        "errors": []
    }
    
    for template_path in templates:
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            # Only process calibrated templates
            is_calibrated = (
                template.get('calibration_status') == 'calibrated' or
                template.get('calibrated', False)
            )
            if not is_calibrated:
                continue
            
            stats["processed"] += 1
            template_id = template.get('template_id')
            
            # Initialize fields if missing
            if 't1_5_parent_theories' not in template:
                template['t1_5_parent_theories'] = []
            if 't1_5_candidates' not in template:
                template['t1_5_candidates'] = []
            
            parent_theories = template['t1_5_parent_theories']
            candidates = template['t1_5_candidates']
            
            # Assign BRECVEMA if in BRECVEMA_TEMPLATES
            if template_id in BRECVEMA_TEMPLATES:
                if "BRECVEMA" not in parent_theories:
                    parent_theories.append("BRECVEMA")
                    stats["brecvema_assigned"] += 1
                # Remove from candidates if present
                if "BRECVEMA" in candidates:
                    candidates.remove("BRECVEMA")
            
            # Assign Flow_Theory if in FLOW_TEMPLATES
            if template_id in FLOW_TEMPLATES:
                if "Flow_Theory" not in parent_theories:
                    parent_theories.append("Flow_Theory")
                    stats["flow_assigned"] += 1
                # Remove from candidates if present
                if "Flow_Theory" in candidates:
                    candidates.remove("Flow_Theory")
            
            # Move BRECVEMA/Flow_Theory from candidates to parent if present
            for theory in ["BRECVEMA", "Flow_Theory"]:
                if theory in candidates and theory not in parent_theories:
                    parent_theories.append(theory)
                    candidates.remove(theory)
            
            # Clean up candidates: remove REJECTED theories
            new_candidates = []
            for c in candidates:
                if c in REJECTED:
                    stats["rejected_removed"] += 1
                elif c in DEFERRED:
                    new_candidates.append(c)
                    stats["deferred_kept"] += 1
                else:
                    new_candidates.append(c)
            
            template['t1_5_candidates'] = new_candidates
            template['t1_5_parent_theories'] = parent_theories
            
            # Write back
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
                f.write('\n')
        
        except Exception as e:
            stats["errors"].append(f"{template_path}: {str(e)}")
    
    return stats

def update_field_aliases():
    """Update field_aliases.json with formal T1.5 enum."""
    aliases_path = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/schemas/field_aliases.json")
    
    with open(aliases_path, 'r') as f:
        aliases = json.load(f)
    
    # Add formal T1.5 enum
    aliases['t1_5_formal_enum'] = sorted(list(FORMAL_ROSTER))
    aliases['_updated'] = '2026-02-23T17:00:00Z (panel results applied)'
    
    with open(aliases_path, 'w') as f:
        json.dump(aliases, f, indent=2)
        f.write('\n')
    
    print(f"\nUpdated field_aliases.json with formal T1.5 enum ({len(FORMAL_ROSTER)} theories)")

if __name__ == '__main__':
    print("=" * 70)
    print("ASSIGN FORMAL T1.5 - Panel Results Application")
    print("=" * 70)
    print(f"\nFormal T1.5 Roster: {len(FORMAL_ROSTER)} theories")
    print(f"  {', '.join(sorted(FORMAL_ROSTER))}")
    print(f"\nRejected theories to remove: {len(REJECTED)}")
    print(f"Deferred theories to keep: {len(DEFERRED)}")
    print(f"\nBRECVEMA templates: {len(BRECVEMA_TEMPLATES)}")
    print(f"Flow_Theory templates: {len(FLOW_TEMPLATES)}")
    print("\n" + "-" * 70)
    
    stats = process_templates()
    
    print(f"\nProcessing Results:")
    print(f"  Calibrated templates processed: {stats['processed']}")
    print(f"  BRECVEMA assigned: {stats['brecvema_assigned']}")
    print(f"  Flow_Theory assigned: {stats['flow_assigned']}")
    print(f"  Rejected theories removed: {stats['rejected_removed']}")
    print(f"  Deferred theories kept: {stats['deferred_kept']}")
    
    if stats['errors']:
        print(f"\nErrors encountered ({len(stats['errors'])}):")
        for error in stats['errors']:
            print(f"  {error}")
    
    update_field_aliases()
    
    print("\n" + "=" * 70)
    print("Panel results applied successfully!")
    print("=" * 70)
