#!/usr/bin/env python3
"""
Populate t1_5_parent_theories field for calibrated templates.

This script:
1. Loads all template JSONs from data/templates/
2. For calibrated templates with empty/missing t1_5_parent_theories
3. Looks up the template_id in the comprehensive T1.5 mapping table
4. Sets t1_5_parent_theories to the mapped list
5. Writes back to JSON file
6. Reports changes

Does NOT overwrite existing t1_5_parent_theories values.
Special: Preserves existing "biophilia (Tier 2)" in NATURE_VIEW_CONVERGENCE_001
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Template base directory
TEMPLATES_DIR = Path("data/templates")

# Comprehensive T1.5 mapping table (template_id -> list of T1.5 theories)
T1_5_MAPPING = {
    # CREATIVE-I (7 templates)
    "INCUBATION_ARCHITECTURE_001": ["ART", "Embodied_Cognition", "Biophilia"],
    "HC_CREATIVE_DIVERGENCE_001": ["ART", "Biophilia"],
    "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001": ["Flow_Theory", "Space_Syntax"],
    "PROCESSING_STYLE_MODULATION_001": ["Flow_Theory", "Berlyne_Arousal"],
    "CREATIVE_NETWORK_DYNAMICS_001": ["Flow_Theory"],
    "CROSS_CREATIVE_NETWORK_DYNAMICS_001": ["Flow_Theory"],
    "CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001": ["Berlyne_Arousal"],

    # MUSIC-I (13 templates)
    "BRECVEMA_BRAINSTEM_001": ["BRECVEMA"],
    "BRECVEMA_RHYTHMIC_ENTRAINMENT_002": ["BRECVEMA"],
    "BRECVEMA_CONTAGION_003": ["BRECVEMA"],
    "BRECVEMA_EXPECTANCY_004": ["BRECVEMA", "Predictive_Coding_Music"],
    "BRECVEMA_MEMORY_005": ["BRECVEMA"],
    "BRECVEMA_MULTI_MECHANISM_001": ["BRECVEMA"],
    "NEURAL_MUSIC_EMOTION_ARCH_001": ["BRECVEMA", "Predictive_Coding_Music"],
    "PLEASURABLE_SADNESS_001": ["BRECVEMA"],
    "ACOUSTIC_EMOTION_MAPPING_001": ["ISO_12913_Soundscape"],
    "MS_ACOUSTIC_ECOLOGY_001": ["ISO_12913_Soundscape"],
    "AUD_SCENE_ANALYSIS_001": ["Auditory_Scene_Analysis", "ISO_12913_Soundscape"],
    "AUD_REVERBERATION_SPACE_003": ["Auditory_Scene_Analysis"],
    "AUDITORY_FRACTAL_SCALING_001": ["Fractal_Fluency"],

    # THERMAL-I (3 templates)
    "IC_THERMAL_COMFORT_001": ["Interoceptive_Prediction"],
    "THERMAL_ADAPTIVE_PE_001": ["Free_Energy_Minimization", "Adaptive_Thermal_Comfort"],
    "THERMAL_COMFORT_ADAPTIVE_PE_001": ["Allesthesia", "Adaptive_Thermal_Comfort"],

    # NEUROMOD-I (14 templates)
    "NM_REWARD_PREDICTION_ERROR_001": ["Free_Energy_Minimization"],
    "NM_WANTING_LIKING_DISSOCIATION_001": ["Incentive_Salience"],
    "NM_DOPAMINE_NOVELTY_002": ["Free_Energy_Minimization"],
    "NM_DOPAMINERGIC_NOVELTY_REWARD_001": ["Incentive_Salience"],
    "NM_NORADRENERGIC_EXPLORE_006": ["Free_Energy_Minimization"],
    "NM_CHOLINERGIC_GATING_007": ["Free_Energy_Minimization"],
    "NM_SEROTONERGIC_MOOD_001": ["Interoceptive_Prediction"],
    "NM_THREAT_HPA_001": ["SRT", "Allostasis"],
    "NM_SAFETY_SIGNALING_001": ["SRT"],
    "MULTIMODAL_PE_INTEGRATION_001": ["Free_Energy_Minimization", "Inverse_Effectiveness"],
    "ALLOSTATIC_MASTER_001": ["Allostasis"],
    "NM_OXYTOCIN_SOCIAL_003": ["Oxytocin_Social_Bonding"],
    "NM_SOCIAL_ISOLATION_ALLOSTATIC_001": ["Allostasis"],
    "NM_VAGAL_REGULATION_001": ["Vagal_Regulation"],

    # CROSSCUT-I (17 templates) — AX axioms
    "AX_DOSE_RESPONSE_007": ["Berlyne_Arousal", "Adaptive_Thermal_Comfort", "ART"],
    "AX_HABITUATION_002": ["ART", "Berlyne_Arousal"],
    "AX_CONTROL_STRESS_004": ["SRT", "Adaptive_Thermal_Comfort"],
    "AX_CHRONIC_ACUTE_011": ["Allostasis", "ART"],
    "AX_INDIVIDUAL_DIFFERENCES_008": ["Sensory_Processing_Sensitivity"],
    "AX_CULTURAL_MODULATION_009": ["Cultural_Neuroscience"],
    "AX_ATTENTION_MEDIATION_010": ["ART", "Biased_Competition"],
    "AX_VR_LIMITATION_012": ["Virtual_Reality_Presence"],
    "SALIENCE_NETWORK_SWITCH_001": ["Free_Energy_Minimization"],
    "CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001": ["Free_Energy_Minimization"],
    "CROSS_WM_GAMMA_BETA_DYNAMICS_001": ["Free_Energy_Minimization"],
    "CROSS_PROACTIVE_REACTIVE_CONTROL_001": ["Dual_Mechanisms_Control"],
    "CROSS_HIERARCHICAL_CONTROL_001": ["Free_Energy_Minimization"],
    "TEMPORAL_HIERARCHY_ARCH_PE_001": ["Free_Energy_Minimization"],
    "ER_ECOLOGICAL_RATIONALITY_001": ["Ecological_Rationality"],
    "AX3_AWE_MECHANISM_001": ["Awe_Theory"],
    "AX3_SMALL_SELF_001": ["Awe_Theory"],

    # MEMORY-I (10 templates)
    "ED_HIPPOCAMPAL_ENCODING_001": ["Pattern_Separation_Completion"],
    "ED_PATTERN_SEP_COMP_001": ["Pattern_Separation_Completion"],
    "ED_PE_ENCODING_PRINCIPLE_001": ["Free_Energy_Minimization"],
    "ED_RECONSOLIDATION_001": ["Reconsolidation"],
    "ED_SCHEMA_ENCODING_001": ["Schema_Theory"],
    "ED_SYSTEMS_CONSOLIDATION_001": ["Systems_Consolidation"],
    "MS_CONSOLIDATION_RESTORATION_001": ["Systems_Consolidation", "ART"],
    "MS_RIPPLE_REPLAY_002": ["Systems_Consolidation"],
    "SN_CONTEXT_MEMORY_002": ["Cognitive_Map_Theory"],
    "THRESHOLD_EPISODIC_BOUNDARY_001": ["Event_Segmentation"],

    # MULTI-I (9 templates)
    "CROSSMODAL_CONGRUENCE_001": ["Inverse_Effectiveness"],
    "CT_AFFECTIVE_TOUCH_001": ["Interoceptive_Prediction"],
    "HAP_SURFACE_MATERIAL_001": ["Embodied_Cognition"],
    "MATERIAL_AGING_TEMPORAL_DEPTH_001": ["Embodied_Cognition"],
    "MATERIAL_CULTURAL_CONDITIONING_001": ["Embodied_Cognition", "Cultural_Neuroscience"],
    "MATERIAL_IDENTITY_INTEGRATION_001": ["Embodied_Cognition"],
    "MSI_CONGRUENCY_PRINCIPLE_001": ["Bayesian_Causal_Inference"],
    "MSI_INVERSE_EFFECTIVENESS_002": ["Inverse_Effectiveness"],
    "NATURAL_MATERIAL_CONVERGENCE_001": ["Biophilia", "Embodied_Cognition"],

    # VISUAL-I templates
    "PP_SPECTRAL_MATCH_001": ["Free_Energy_Minimization", "Fractal_Fluency"],
    "PP_COMPLEXITY_GOLDILOCKS_002": ["Berlyne_Arousal", "Free_Energy_Minimization"],
    "PP_RAPID_GIST_004": ["Free_Energy_Minimization"],
    "CONTOUR_PE_CURVATURE_001": ["Free_Energy_Minimization"],  # VF1
    "VISUAL_RHYTHM_SCALING_001": ["Fractal_Fluency"],  # VF2
    "VF3_SPATIAL_PROPORTIONS_001": ["Free_Energy_Minimization"],
    "LUM_CONTRAST_PE_001": ["Free_Energy_Minimization"],  # L1
    # NATURE_VIEW_CONVERGENCE_001: Special case - already has ["biophilia (Tier 2)"], do NOT overwrite

    # LIGHT-I templates
    "CIRCADIAN_ARCH_REGULATION_001": ["Circadian_Entrainment"],  # L2
    "CB_SLEEP_ARCHITECTURE_002": ["Circadian_Entrainment"],
    "CHRONO_LIGHT_ENTRAINMENT_001": ["Circadian_Entrainment"],  # T30
    "NM_CIRCADIAN_ENTRAINMENT_001": ["Circadian_Entrainment"],
    # DAYLIGHT_MULTICHANNEL_001 (L3): Already has ["ART", "SRT"], do NOT overwrite
    "DYNAMIC_LIGHT_TEMPORAL_001": ["Circadian_Entrainment", "Free_Energy_Minimization"],  # L5
    # CIRCADIAN_ARCH_REG_001 (L2): Already has ["Adaptive_Thermal_Comfort"], do NOT overwrite
    "CCT_TEMPORAL_ECOLOGICAL_001": ["Embodied_Cognition"],  # L4

    # SPATIAL-I templates
    "ISOVIST_VISUAL_PREDICTION_001": ["Space_Syntax", "Prospect_Refuge"],  # SC2
    "SPATIAL_INTEGRATION_NAV_PE_001": ["Space_Syntax"],  # SC1
    "ARCH_PROMENADE_PE_ORCHESTRATION_001": ["Free_Energy_Minimization"],  # SC3
    "SPATIAL_SOCIAL_ENCOUNTER_001": ["Space_Syntax"],  # SC4

    # SOCIAL-I templates
    "PROXEMIC_PE_ARCH_001": ["Proxemics", "Space_Syntax"],  # SOC1
    "PRIVACY_GRADIENT_REGULATION_001": ["Privacy_Regulation"],  # SOC2
    "TERRITORIAL_AFFORDANCE_SOCIAL_001": ["Territorial_Psychology"],  # SOC3
    "CROSS_SOCIAL_AFFORDANCE_READING_001": ["Social_Brain"],  # T48
    "CROSS_SOCIAL_MIRROR_PRESENCE_001": ["Mirror_Neuron_System"],  # T49
    "NM_SOCIAL_ISOLATION_ALLOSTATIC_001": ["Allostasis", "Social_Deprivation"],  # T50
    "CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001": ["Mentalizing"],  # T51
    "NM_SOCIAL_ENRICHMENT_MODULATION_001": ["Social_Motivation"],  # T52

    # COLOR/CHROMATIC-I templates
    "CHROMATIC_PE_ARCH_001": ["Color_Psychology", "Free_Energy_Minimization"],  # COL1
    "COLOR_AROUSAL_MODULATION_001": ["Berlyne_Arousal", "Color_Psychology"],  # COL2

    # CREATIVE-I additional
    "INCUBATION_ARCHITECTURE_001": ["ART", "Embodied_Cognition", "Biophilia"],  # CREA3

    # MUSIC-I additional (from panel mappings)
    "OSCILLATORY_ENTRAINMENT_METRIC_001": ["BRECVEMA"],  # M8
    "GROOVE_MOTOR_PREDICTION_001": ["BRECVEMA", "Motor_Prediction"],  # M9
    "ASAP_MOTOR_AUDITORY_PREDICTION_001": ["BRECVEMA", "Motor_Auditory_Integration"],  # M10
    "AUDITORY_MOTOR_PLASTICITY_001": ["BRECVEMA", "Motor_Learning"],  # M11
    "AESTHETIC_VS_UTILITARIAN_EMOTIONS_001": ["BRECVEMA"],  # M14
    "MUSICAL_CHILLS_CONVERGENCE_001": ["BRECVEMA"],  # M16

    # OLFACTORY-I templates
    "OLFACTORY_PE_TRANSITION_001": ["Olfactory_Prediction", "Free_Energy_Minimization"],

    # LIGHT-I special cases with panel-assigned T1.5 (previously skipped but should be added)
    "DAYLIGHT_MULTICHANNEL_001": ["ART", "SRT"],  # L3 - from LIGHT-I panel output
    "CIRCADIAN_ARCH_REG_001": ["Adaptive_Thermal_Comfort"],  # L2 - from LIGHT-I panel output
}

def load_template(template_path: Path) -> dict:
    """Load template JSON from file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {template_path}: {e}")
        return None

def save_template(template_path: Path, template_data: dict) -> bool:
    """Save template JSON to file."""
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {template_path}: {e}")
        return False

def is_calibrated(template_data: dict) -> bool:
    """Check if template is calibrated (has source_panel from expert panel)."""
    # Check for source_panel field - indicates panel-calibrated template
    source_panel = template_data.get("source_panel", "")
    return bool(source_panel and source_panel.strip())

def needs_t1_5_population(template_data: dict) -> bool:
    """Check if template needs t1_5_parent_theories populated."""
    # Don't overwrite if already has a non-empty value
    theories = template_data.get("t1_5_parent_theories")
    if theories and isinstance(theories, list) and len(theories) > 0:
        return False
    return True

def populate_templates():
    """Main function: populate t1_5_parent_theories for calibrated templates."""
    if not TEMPLATES_DIR.exists():
        print(f"ERROR: Templates directory not found: {TEMPLATES_DIR}")
        return

    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    print(f"Found {len(template_files)} template files")
    print()

    stats = {
        "total": 0,
        "calibrated": 0,
        "needs_population": 0,
        "updated": 0,
        "already_populated": 0,
        "special_cases_skipped": 0,
    }

    updated_templates = []

    for template_path in template_files:
        template_data = load_template(template_path)
        if not template_data:
            continue

        stats["total"] += 1
        template_id = template_data.get("template_id", "UNKNOWN")
        display_id = template_data.get("display_id", "")

        # Check if calibrated
        if not is_calibrated(template_data):
            continue

        stats["calibrated"] += 1

        # Check if needs population
        if not needs_t1_5_population(template_data):
            stats["already_populated"] += 1
            continue

        stats["needs_population"] += 1

        # Special cases: NATURE_VIEW_CONVERGENCE_001 already has explicit panel value to preserve
        if template_id == "NATURE_VIEW_CONVERGENCE_001":
            # This already has ["biophilia (Tier 2)"], don't overwrite per user instruction
            stats["special_cases_skipped"] += 1
            continue

        # Look up T1.5 theories from mapping
        if template_id not in T1_5_MAPPING:
            print(f"WARNING: {display_id} ({template_id}) not in T1.5 mapping table")
            continue

        theories = T1_5_MAPPING[template_id]

        # Update template
        template_data["t1_5_parent_theories"] = theories

        # Save to file
        if save_template(template_path, template_data):
            stats["updated"] += 1
            updated_templates.append({
                "display_id": display_id,
                "template_id": template_id,
                "theories": theories,
                "filename": template_path.name
            })

    # Report results
    print("\n" + "="*80)
    print("POPULATION RESULTS")
    print("="*80)
    print(f"Total template files:           {stats['total']}")
    print(f"Calibrated templates:          {stats['calibrated']}")
    print(f"Needed population:             {stats['needs_population']}")
    print(f"Updated with T1.5 theories:    {stats['updated']}")
    print(f"Already had T1.5 theories:     {stats['already_populated']}")
    print(f"Special cases (skipped):       {stats['special_cases_skipped']}")
    print()

    if updated_templates:
        print(f"\nDetailed list of {len(updated_templates)} updated templates:")
        print("-" * 80)
        for template in sorted(updated_templates, key=lambda x: x['display_id'] or x['template_id']):
            display = template['display_id'] if template['display_id'] else template['template_id']
            theories_str = ", ".join(template['theories'])
            print(f"{display:20} → {theories_str}")
        print("-" * 80)

    print("\nDone!")

if __name__ == "__main__":
    populate_templates()
