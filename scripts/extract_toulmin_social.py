import sys
import json
import os

# We will let CC fill in the specific Toulmin justifications from the SOCIAL-I transcript.
# This script sets up the framework for CC to apply the data quickly.

from apply_toulmin_justification import (
    make_data_entry,
    make_justification,
    apply_justification_to_template,
    report_panel_status,
    load_template,
    save_template
)

TEMPLATES = [
    "PROXEMIC_PE_ARCH_001",
    "NM_SOCIAL_ISOLATION_ALLOSTATIC_001", 
    "SPATIAL_SOCIAL_ENCOUNTER_001",
    "NM_VAGAL_REGULATION_001",
    "NM_OXYTOCIN_SOCIAL_003",
    "PRIVACY_GRADIENT_REGULATION_001",
    "TERRITORIAL_AFFORDANCE_SOCIAL_001",
    "CROSS_SOCIAL_MIRROR_PRESENCE_001",
    "XF_SOCIAL_AFFORDANCE_DENSITY_001",
    "CROSS_SOCIAL_AFFORDANCE_READING_001",
    "CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001"
]

def run_social_extraction():
    print("SOCIAL-I Toulmin Retrofit Outline")
    print("---------------------------------")
    print("CC: Please populate the 'justifications' dictionary below by reading docs/SOCIAL_I_Panel_Output.md")
    print("Use the Debate sections to populate the competing_accounts, backing, and rebuttal.")
    
    justifications = {
        # Example structure for CC:
        # "PROXEMIC_PE_ARCH_001": {
        #     1: make_justification(
        #         data=[make_data_entry(finding="...", source="...", paradigm="...")],
        #         backing="...",
        #         qualifier="...",
        #         rebuttal="...",
        #         competing_accounts=["..."]
        #     ),
        #     # ... steps 2, 3, 4
        # },
    }
    
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
    run_social_extraction()
