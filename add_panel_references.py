#!/usr/bin/env python3
"""
Add panel_debate_reference fields to all Toulmin justification objects
in MUSIC-I (13 templates) and THERMAL-I (3 templates).
"""

import json
import os
from pathlib import Path

# Template to panel mapping
MUSIC_I_TEMPLATES = [
    "ACOUSTIC_EMOTION_MAPPING_001",
    "AUDITORY_FRACTAL_SCALING_001",
    "AUD_REVERBERATION_SPACE_003",
    "AUD_SCENE_ANALYSIS_001",
    "BRECVEMA_BRAINSTEM_001",
    "BRECVEMA_CONTAGION_003",
    "BRECVEMA_EXPECTANCY_004",
    "BRECVEMA_MEMORY_005",
    "BRECVEMA_MULTI_MECHANISM_001",
    "BRECVEMA_RHYTHMIC_ENTRAINMENT_002",
    "MS_ACOUSTIC_ECOLOGY_001",
    "NEURAL_MUSIC_EMOTION_ARCH_001",
    "PLEASURABLE_SADNESS_001",
]

THERMAL_I_TEMPLATES = [
    "IC_THERMAL_COMFORT_001",
    "THERMAL_ADAPTIVE_PE_001",
    "THERMAL_COMFORT_ADAPTIVE_PE_001",
]

# Section mappings based on OUTPUT BLOCK 1 structure
MUSIC_I_SECTIONS = {
    "BRECVEMA_BRAINSTEM_001": "Template 1: BRECVEMA_BRAINSTEM_001",
    "BRECVEMA_RHYTHMIC_ENTRAINMENT_002": "Template 2: BRECVEMA_RHYTHMIC_ENTRAINMENT_002",
    "BRECVEMA_CONTAGION_003": "Template 3: BRECVEMA_CONTAGION_003",
    "BRECVEMA_EXPECTANCY_004": "Template 4: BRECVEMA_EXPECTANCY_004",
    "BRECVEMA_MEMORY_005": "Template 5: BRECVEMA_MEMORY_005",
    "NEURAL_MUSIC_EMOTION_ARCH_001": "Template 6: NEURAL_MUSIC_EMOTION_ARCH_001",
    "PLEASURABLE_SADNESS_001": "Template 7: PLEASURABLE_SADNESS_001",
    "ACOUSTIC_EMOTION_MAPPING_001": "Template 8: ACOUSTIC_EMOTION_MAPPING_001",
    "MS_ACOUSTIC_ECOLOGY_001": "Template 9: MS_ACOUSTIC_ECOLOGY_001",
    "AUD_SCENE_ANALYSIS_001": "Template 10: AUD_SCENE_ANALYSIS_001",
    "AUD_REVERBERATION_SPACE_003": "Template 11: AUD_REVERBERATION_SPACE_003",
    "AUDITORY_FRACTAL_SCALING_001": "Template 12: AUDITORY_FRACTAL_SCALING_001",
    "BRECVEMA_MULTI_MECHANISM_001": "Template 13: BRECVEMA_MULTI_MECHANISM_001",
}

THERMAL_I_SECTIONS = {
    "IC_THERMAL_COMFORT_001": "Template 1: IC_THERMAL_COMFORT_001 (Tier A — calibrated first per C-04)",
    "THERMAL_ADAPTIVE_PE_001": "Template 2: THERMAL_ADAPTIVE_PE_001 (Tier A — calibrated second per C-04)",
    "THERMAL_COMFORT_ADAPTIVE_PE_001": "Template 3: THERMAL_COMFORT_ADAPTIVE_PE_001 (Tier C — calibrated last per C-04)",
}

def add_panel_reference_to_justification(justification, panel, document, section):
    """
    Add panel_debate_reference to a justification object if not already present.
    Returns True if added, False if already present.
    """
    if not justification:
        return False

    if "panel_debate_reference" in justification:
        print(f"  → Skipping: panel_debate_reference already exists")
        return False

    justification["panel_debate_reference"] = {
        "panel": panel,
        "document": document,
        "relevant_section": section
    }
    return True

def process_template(template_path, template_id, panel, panel_document, panel_section):
    """
    Process a single template file.
    Returns the number of justification objects updated.
    """
    print(f"\nProcessing: {template_id}")

    with open(template_path, 'r') as f:
        template = json.load(f)

    count = 0

    # Process mechanism_chain if it exists
    if "mechanism_chain" in template:
        for step_idx, step in enumerate(template["mechanism_chain"]):
            if "justification" in step:
                step_num = step.get('step', f"[{step_idx}]")
                step_from = step.get('from', 'unknown')
                step_to = step.get('to', 'unknown')
                print(f"  Step {step_num}: {step_from} → {step_to}")
                if add_panel_reference_to_justification(
                    step["justification"],
                    panel,
                    panel_document,
                    panel_section
                ):
                    count += 1
                    print(f"    ✓ Added panel reference")
    else:
        # If no mechanism_chain, note it
        print(f"  Note: No mechanism_chain found in this template")

    # Write back to file
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    if count > 0:
        print(f"  Total references added to mechanism justifications: {count}")
    else:
        print(f"  Total references added: {count}")
    return count

def main():
    base_path = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1")
    templates_dir = base_path / "data" / "templates"

    total_count = 0

    # Process MUSIC-I templates
    print("=" * 70)
    print("PROCESSING MUSIC-I TEMPLATES")
    print("=" * 70)

    for template_id in MUSIC_I_TEMPLATES:
        template_path = templates_dir / f"{template_id}.json"
        if template_path.exists():
            section = MUSIC_I_SECTIONS[template_id]
            count = process_template(
                template_path,
                template_id,
                "MUSIC-I",
                "docs/MUSIC_I_Panel_Output.md",
                section
            )
            total_count += count
        else:
            print(f"WARNING: {template_id}.json not found")

    # Process THERMAL-I templates
    print("\n" + "=" * 70)
    print("PROCESSING THERMAL-I TEMPLATES")
    print("=" * 70)

    for template_id in THERMAL_I_TEMPLATES:
        template_path = templates_dir / f"{template_id}.json"
        if template_path.exists():
            section = THERMAL_I_SECTIONS[template_id]
            count = process_template(
                template_path,
                template_id,
                "THERMAL-I",
                "docs/THERMAL_I_Panel_Output.md",
                section
            )
            total_count += count
        else:
            print(f"WARNING: {template_id}.json not found")

    print("\n" + "=" * 70)
    print(f"COMPLETION SUMMARY")
    print("=" * 70)
    print(f"Total justification objects updated: {total_count}")
    print(f"Templates processed: {len(MUSIC_I_TEMPLATES) + len(THERMAL_I_TEMPLATES)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
