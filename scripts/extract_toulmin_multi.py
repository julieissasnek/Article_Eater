import sys
import json
import os

from apply_toulmin_justification import (
    make_data_entry,
    make_justification,
    apply_justification_to_template,
    report_panel_status,
    load_template,
    save_template
)

TEMPLATES = [
    "MATERIAL_IDENTITY_INTEGRATION_001",
    "CT_AFFECTIVE_TOUCH_001",
    "NATURAL_MATERIAL_CONVERGENCE_001",
    "HAP_SURFACE_MATERIAL_001",
    "MSI_INVERSE_EFFECTIVENESS_002",
    "MSI_CONGRUENCY_PRINCIPLE_001",
    "CROSSMODAL_CONGRUENCE_001",
    "MATERIAL_CULTURAL_CONDITIONING_001",
    "MATERIAL_AGING_TEMPORAL_DEPTH_001"
]

def run_multi_extraction():
    print("MULTI-I Toulmin Retrofit Outline")
    print("--------------------------------")
    print("CC: Please populate the 'justifications' dictionary below by reading docs/MULTI_I_Panel_Output.md")
    
    justifications = {}
    
    updated_count = 0
    steps_updated = 0
    
    for tid in TEMPLATES:
        path, data = load_template(tid)
        if not path:
            print(f"Template {tid} not found!")
            continue
            
        if tid in justifications:
            count = apply_justification_to_template(data, justifications[tid])
            if count > 0:
                save_template(path, data)
                updated_count += 1
                steps_updated += count
                print(f"Updated {tid} ({count} steps)")
        else:
            print(f"TODO: {tid} needs justification data")
            
    print(f"\nApplied justifications to {steps_updated} steps across {updated_count} templates.")
    
if __name__ == "__main__":
    run_multi_extraction()
