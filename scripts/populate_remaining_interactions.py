#!/usr/bin/env python3
"""
Populate cross_template_interactions for 20 templates.

This script assigns mechanistic interactions based on template content.
Target templates are organized in three groups:
  - MEMORY-I (10 templates)
  - MULTI-I (9 templates)
  - T6 (Tier 1 Framework template)

Each template gets a list of interaction dictionaries with the structure:
  {"template_id": "OTHER_TEMPLATE_ID", "interaction_type": "TYPE", "description": "..."}
"""

import json
import glob
from pathlib import Path
from typing import List, Dict, Any

# Define the interactions for each template
INTERACTIONS_MAP = {
    "ED_HIPPOCAMPAL_ENCODING_001": [
        {"template_id": "ED_PATTERN_SEP_COMP_001", "interaction_type": "feeds_into", 
         "description": "Hippocampal encoding provides input patterns for separation and completion"},
        {"template_id": "SN_CONTEXT_MEMORY_002", "interaction_type": "complementary", 
         "description": "Encoding binds spatial context to episodic content"},
        {"template_id": "ED_SCHEMA_ENCODING_001", "interaction_type": "feeds_into", 
         "description": "Novel encoding feeds schema updating processes"},
    ],
    "ED_PATTERN_SEP_COMP_001": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "receives_from", 
         "description": "Receives encoded patterns for separation/completion"},
        {"template_id": "ED_RECONSOLIDATION_001", "interaction_type": "feeds_into", 
         "description": "Pattern completion during retrieval triggers reconsolidation"},
    ],
    "ED_PE_ENCODING_PRINCIPLE_001": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "moderates", 
         "description": "Prediction error strength modulates encoding depth"},
        {"template_id": "THRESHOLD_EPISODIC_BOUNDARY_001", "interaction_type": "complementary", 
         "description": "PE at transitions enhances boundary encoding"},
    ],
    "ED_RECONSOLIDATION_001": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "receives_from", 
         "description": "Reconsolidation requires prior hippocampal encoding"},
        {"template_id": "ED_SYSTEMS_CONSOLIDATION_001", "interaction_type": "sequential", 
         "description": "Reconsolidation updates memories during consolidation window"},
    ],
    "ED_SCHEMA_ENCODING_001": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "receives_from", 
         "description": "Schema integration depends on initial hippocampal encoding"},
        {"template_id": "ED_SYSTEMS_CONSOLIDATION_001", "interaction_type": "feeds_into", 
         "description": "Schema-consistent memories consolidate faster"},
    ],
    "ED_SYSTEMS_CONSOLIDATION_001": [
        {"template_id": "MS_CONSOLIDATION_RESTORATION_001", "interaction_type": "complementary", 
         "description": "Systems consolidation and sleep consolidation work in concert"},
        {"template_id": "MS_RIPPLE_REPLAY_002", "interaction_type": "receives_from", 
         "description": "Sharp-wave ripple replay drives systems consolidation"},
    ],
    "MS_CONSOLIDATION_RESTORATION_001": [
        {"template_id": "MS_RIPPLE_REPLAY_002", "interaction_type": "sequential", 
         "description": "Sleep consolidation involves ripple-mediated replay"},
        {"template_id": "ED_SYSTEMS_CONSOLIDATION_001", "interaction_type": "complementary", 
         "description": "Sleep provides temporal window for systems consolidation"},
    ],
    "MS_RIPPLE_REPLAY_002": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "receives_from", 
         "description": "Replay requires prior hippocampal encoding of experience"},
        {"template_id": "MS_CONSOLIDATION_RESTORATION_001", "interaction_type": "feeds_into", 
         "description": "Ripple replay drives sleep-dependent consolidation"},
    ],
    "SN_CONTEXT_MEMORY_002": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "complementary", 
         "description": "Spatial context provides binding scaffold for episodic encoding"},
        {"template_id": "THRESHOLD_EPISODIC_BOUNDARY_001", "interaction_type": "moderates", 
         "description": "Spatial transitions modulate boundary detection"},
    ],
    "THRESHOLD_EPISODIC_BOUNDARY_001": [
        {"template_id": "ED_PE_ENCODING_PRINCIPLE_001", "interaction_type": "complementary", 
         "description": "Boundary transitions generate prediction errors enhancing encoding"},
        {"template_id": "SN_CONTEXT_MEMORY_002", "interaction_type": "receives_from", 
         "description": "Spatial context changes trigger episodic boundaries"},
    ],
    # MULTI-I (9 templates)
    "CROSSMODAL_CONGRUENCE_001": [
        {"template_id": "MSI_CONGRUENCY_PRINCIPLE_001", "interaction_type": "complementary", 
         "description": "Crossmodal congruence instantiates multisensory congruency principle"},
        {"template_id": "NATURAL_MATERIAL_CONVERGENCE_001", "interaction_type": "feeds_into", 
         "description": "Crossmodal congruence enhances natural material perception"},
    ],
    "CT_AFFECTIVE_TOUCH_001": [
        {"template_id": "HAP_SURFACE_MATERIAL_001", "interaction_type": "complementary", 
         "description": "Affective touch provides hedonic evaluation of surface haptics"},
        {"template_id": "MATERIAL_IDENTITY_INTEGRATION_001", "interaction_type": "feeds_into", 
         "description": "Touch-based affect contributes to material identity formation"},
    ],
    "HAP_SURFACE_MATERIAL_001": [
        {"template_id": "CT_AFFECTIVE_TOUCH_001", "interaction_type": "receives_from", 
         "description": "Surface material properties activate affective touch pathways"},
        {"template_id": "NATURAL_MATERIAL_CONVERGENCE_001", "interaction_type": "feeds_into", 
         "description": "Haptic surface properties contribute to natural material evaluation"},
    ],
    "MATERIAL_AGING_TEMPORAL_DEPTH_001": [
        {"template_id": "MATERIAL_CULTURAL_CONDITIONING_001", "interaction_type": "complementary", 
         "description": "Material aging acquires cultural significance through conditioning"},
        {"template_id": "MATERIAL_IDENTITY_INTEGRATION_001", "interaction_type": "feeds_into", 
         "description": "Patina and aging contribute to place-material identity"},
    ],
    "MATERIAL_CULTURAL_CONDITIONING_001": [
        {"template_id": "MATERIAL_AGING_TEMPORAL_DEPTH_001", "interaction_type": "complementary", 
         "description": "Cultural conditioning shapes interpretation of material aging"},
        {"template_id": "NATURAL_MATERIAL_CONVERGENCE_001", "interaction_type": "moderates", 
         "description": "Cultural conditioning modulates natural material preferences"},
    ],
    "MATERIAL_IDENTITY_INTEGRATION_001": [
        {"template_id": "MATERIAL_AGING_TEMPORAL_DEPTH_001", "interaction_type": "receives_from", 
         "description": "Material identity incorporates temporal/aging properties"},
        {"template_id": "MATERIAL_CULTURAL_CONDITIONING_001", "interaction_type": "receives_from", 
         "description": "Cultural conditioning shapes material identity associations"},
    ],
    "MSI_CONGRUENCY_PRINCIPLE_001": [
        {"template_id": "MSI_INVERSE_EFFECTIVENESS_002", "interaction_type": "complementary", 
         "description": "Congruency and inverse effectiveness are complementary integration principles"},
        {"template_id": "CROSSMODAL_CONGRUENCE_001", "interaction_type": "scope_partition", 
         "description": "General MSI principle; crossmodal congruence is specific application"},
    ],
    "MSI_INVERSE_EFFECTIVENESS_002": [
        {"template_id": "MSI_CONGRUENCY_PRINCIPLE_001", "interaction_type": "complementary", 
         "description": "Inverse effectiveness and congruency jointly determine integration strength"},
        {"template_id": "NATURAL_MATERIAL_CONVERGENCE_001", "interaction_type": "feeds_into", 
         "description": "Weak unimodal signals boost multisensory integration of natural materials"},
    ],
    "NATURAL_MATERIAL_CONVERGENCE_001": [
        {"template_id": "HAP_SURFACE_MATERIAL_001", "interaction_type": "receives_from", 
         "description": "Convergent evaluation integrates haptic surface properties"},
        {"template_id": "CROSSMODAL_CONGRUENCE_001", "interaction_type": "receives_from", 
         "description": "Natural material evaluation benefits from crossmodal congruence"},
    ],
    # T6 (Tier 1 Framework)
    "T6": [
        {"template_id": "ED_HIPPOCAMPAL_ENCODING_001", "interaction_type": "feeds_into", 
         "description": "Framework-level predictions constrain hippocampal encoding processes"},
        {"template_id": "BRECVEMA_EXPECTANCY_004", "interaction_type": "feeds_into", 
         "description": "Predictive processing framework grounds musical expectancy mechanisms"},
    ],
}


def load_template(template_path: str) -> Dict[str, Any]:
    """Load a template JSON file."""
    with open(template_path, 'r') as f:
        return json.load(f)


def save_template(template_path: str, data: Dict[str, Any]) -> None:
    """Save a template JSON file with pretty formatting."""
    with open(template_path, 'w') as f:
        json.dump(data, f, indent=2)


def find_template_path(template_id: str, templates_dir: str) -> str:
    """Find the path to a template file by ID."""
    pattern = f"{templates_dir}/{template_id}.json"
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    return None


def main():
    """Populate cross_template_interactions for the 20 templates."""
    repo_root = Path(__file__).parent.parent
    templates_dir = repo_root / "data" / "templates"
    
    if not templates_dir.exists():
        print(f"ERROR: Templates directory not found: {templates_dir}")
        return
    
    templates_dir_str = str(templates_dir)
    
    total_processed = 0
    total_updated = 0
    errors = []
    
    for template_id, interactions in INTERACTIONS_MAP.items():
        template_path = find_template_path(template_id, templates_dir_str)
        
        if not template_path:
            msg = f"SKIP: {template_id} - template file not found"
            print(msg)
            errors.append(msg)
            continue
        
        try:
            template_data = load_template(template_path)
            old_count = len(template_data.get('cross_template_interactions', []))
            
            # Set the interactions
            template_data['cross_template_interactions'] = interactions
            
            # Save back
            save_template(template_path, template_data)
            
            new_count = len(interactions)
            print(f"OK: {template_id:40s} ({old_count} -> {new_count} interactions)")
            total_updated += 1
            
        except Exception as e:
            msg = f"ERROR: {template_id} - {str(e)}"
            print(msg)
            errors.append(msg)
        
        total_processed += 1
    
    print("\n" + "=" * 80)
    print(f"Summary: {total_updated}/{total_processed} templates updated")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
