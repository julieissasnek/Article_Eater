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
    "EPISODIC_WAYFINDING_001",
    "SEMANTIC_SPATIAL_MEMORY_001",
    "WORKING_MEMORY_LOAD_ARCH_001",
    "ENVIRONMENTAL_ENRICHMENT_HGC_001",
    "SPATIAL_ANCHORING_001",
    "ALLOSTATIC_MEMORY_IMPAIRMENT_001",
    "COLLECTIVE_ARCH_MEMORY_001",
    "NM_SLEEP_ARCH_CONSOLIDATION_001",
    "MEMORY_PALACE_AFFORDANCE_001",
    "AGING_COGNITIVE_MAP_DECLINE_001"
]

def run_memory_extraction():
    print("MEMORY-I Toulmin Retrofit Outline")
    print("---------------------------------")
    print("CC: Please populate the 'justifications' dictionary below by reading docs/MEMORY_I_Panel_Output.md")
    
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
    run_memory_extraction()
