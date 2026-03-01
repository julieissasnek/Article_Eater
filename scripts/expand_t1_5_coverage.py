#!/usr/bin/env python3
"""
expand_t1_5_coverage.py
Expand T1.5 (domain-level bridge theory) coverage for all 83 calibrated templates.

T1.5 theories are domain-level bridge theories between T1 neurally-grounded
frameworks and specific architectural phenomena.

Author: Claude Code
Date: 2026-02-23
Version: 1.0
"""

import json
import glob
from pathlib import Path
from typing import Dict, List, Optional

# Comprehensive T1.5 mapping by template_id
T1_5_MAPPING: Dict[str, List[str]] = {
    # MEMORY-I templates
    "ED_HIPPOCAMPAL_ENCODING_001": ["Relational_Memory_Theory", "Episodic_Memory_Theory"],
    "ED_PATTERN_SEP_COMP_001": ["Relational_Memory_Theory", "Computational_Neuroscience"],
    "ED_PE_ENCODING_PRINCIPLE_001": ["Relational_Memory_Theory", "Free_Energy_Minimization"],
    "ED_RECONSOLIDATION_001": ["Episodic_Memory_Theory", "Memory_Reconsolidation_Theory"],
    "ED_SCHEMA_ENCODING_001": ["Schema_Theory", "Episodic_Memory_Theory"],
    "ED_SYSTEMS_CONSOLIDATION_001": ["Systems_Consolidation_Theory", "Episodic_Memory_Theory"],
    "MS_CONSOLIDATION_RESTORATION_001": ["Sleep_Memory_Consolidation", "Systems_Consolidation_Theory"],
    "MS_RIPPLE_REPLAY_002": ["Sleep_Memory_Consolidation", "Systems_Consolidation_Theory"],
    "SN_CONTEXT_MEMORY_002": ["Cognitive_Map_Theory", "Episodic_Memory_Theory"],
    "THRESHOLD_EPISODIC_BOUNDARY_001": ["Event_Segmentation_Theory", "Episodic_Memory_Theory"],

    # NEUROMOD-I templates
    "ALLOSTATIC_MASTER_001": ["Allostasis_Theory", "Body_Budget_Model"],
    "MULTIMODAL_PE_INTEGRATION_001": ["Free_Energy_Minimization", "Neuromodulatory_Architecture"],
    "NM_CHOLINERGIC_GATING_007": ["Neuromodulatory_Architecture", "Attention_Theory"],
    "NM_DOPAMINERGIC_NOVELTY_REWARD_001": ["Reward_Prediction_Theory", "Neuromodulatory_Architecture"],
    "NM_DOPAMINE_NOVELTY_002": ["Reward_Prediction_Theory", "Neuromodulatory_Architecture"],
    "NM_NORADRENERGIC_EXPLORE_006": ["Neuromodulatory_Architecture", "Adaptive_Gain_Theory"],
    "NM_REWARD_PREDICTION_ERROR_001": ["Reward_Prediction_Theory", "Free_Energy_Minimization"],
    "NM_SAFETY_SIGNALING_001": ["Neuromodulatory_Architecture", "Safety_Signal_Theory"],
    "NM_SEROTONERGIC_MOOD_001": ["Neuromodulatory_Architecture", "Affective_Neuroscience"],
    "NM_THREAT_HPA_001": ["Allostasis_Theory", "Neuromodulatory_Architecture"],
    "NM_WANTING_LIKING_DISSOCIATION_001": ["Reward_Prediction_Theory", "Affective_Neuroscience"],

    # MUSIC-I templates
    "ACOUSTIC_EMOTION_MAPPING_001": ["ISO_12913_Soundscape", "Affective_Neuroscience"],
    "AUDITORY_FRACTAL_SCALING_001": ["Fractal_Fluency", "Auditory_Scene_Analysis"],
    "AUD_REVERBERATION_SPACE_003": ["Auditory_Scene_Analysis", "Spatial_Acoustics"],
    "AUD_SCENE_ANALYSIS_001": ["Auditory_Scene_Analysis", "ISO_12913_Soundscape"],
    "BRECVEMA_BRAINSTEM_001": ["BRECVEMA"],
    "BRECVEMA_CONTAGION_003": ["BRECVEMA", "Mirror_Neuron_Theory"],
    "BRECVEMA_EXPECTANCY_004": ["BRECVEMA", "Predictive_Coding_Music"],
    "BRECVEMA_MEMORY_005": ["BRECVEMA", "Episodic_Memory_Theory"],
    "BRECVEMA_MULTI_MECHANISM_001": ["BRECVEMA"],
    "BRECVEMA_RHYTHMIC_ENTRAINMENT_002": ["BRECVEMA", "Dynamic_Attending_Theory"],
    "MS_ACOUSTIC_ECOLOGY_001": ["ISO_12913_Soundscape", "Acoustic_Ecology"],
    "NEURAL_MUSIC_EMOTION_ARCH_001": ["BRECVEMA", "Predictive_Coding_Music"],
    "PLEASURABLE_SADNESS_001": ["BRECVEMA", "Aesthetic_Emotion_Theory"],

    # VISUAL-I templates
    "LUM_CONTRAST_PE_001": ["Predictive_Coding_Vision", "Contrast_Adaptation"],
    "PP_SPECTRAL_MATCH_001": ["Predictive_Coding_Vision", "Ecological_Optics"],
    "PP_COMPLEXITY_GOLDILOCKS_002": ["Berlyne_Arousal", "Predictive_Coding_Vision"],
    "PP_RAPID_GIST_004": ["Scene_Perception_Theory", "Predictive_Coding_Vision"],
    "VF1_CONTOUR_PE_001": ["Predictive_Coding_Vision", "Gestalt_Theory"],
    "VF2_VISUAL_RHYTHM_001": ["Predictive_Coding_Vision", "Gestalt_Theory"],
    "VF3_SPATIAL_PROPORTIONS_001": ["Predictive_Coding_Vision", "Golden_Ratio_Theory"],

    # CREATIVE-I templates
    "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001": ["Flow_Theory", "Space_Syntax"],
    "CREATIVE_NETWORK_DYNAMICS_001": ["Flow_Theory", "DMN_TPN_Theory"],
    "CROSS_CREATIVE_NETWORK_DYNAMICS_001": ["Flow_Theory", "DMN_TPN_Theory"],
    "CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001": ["Berlyne_Arousal", "DMN_TPN_Theory"],
    "HC_CREATIVE_DIVERGENCE_001": ["ART", "Biophilia"],
    "INCUBATION_ARCHITECTURE_001": ["ART", "Embodied_Cognition"],
    "PROCESSING_STYLE_MODULATION_001": ["Flow_Theory", "Berlyne_Arousal"],

    # CROSSCUT-I templates
    "AX3_AWE_MECHANISM_001": ["Awe_Theory", "Self_Transcendence"],
    "AX3_SMALL_SELF_001": ["Awe_Theory", "Self_Transcendence"],
    "AX_ATTENTION_MEDIATION_010": ["Attention_Theory", "Free_Energy_Minimization"],
    "AX_CHRONIC_ACUTE_011": ["Allostasis_Theory", "Stress_Theory"],
    "AX_CONTROL_STRESS_004": ["Perceived_Control_Theory", "Stress_Theory"],
    "AX_CULTURAL_MODULATION_009": ["Cultural_Neuroscience", "Embodied_Cognition"],
    "AX_DOSE_RESPONSE_007": ["Dose_Response_Theory", "Free_Energy_Minimization"],
    "AX_HABITUATION_002": ["Habituation_Theory", "Free_Energy_Minimization"],
    "AX_INDIVIDUAL_DIFFERENCES_008": ["Individual_Differences", "Personality_Neuroscience"],
    "AX_VR_LIMITATION_012": ["Virtual_Reality_Theory", "Presence_Theory"],
    "CROSS_HIERARCHICAL_CONTROL_001": ["Hierarchical_Control_Theory", "Free_Energy_Minimization"],
    "CROSS_PROACTIVE_REACTIVE_CONTROL_001": ["Dual_Mechanisms_Control", "DMN_TPN_Theory"],
    "CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001": ["Thalamic_Gating_Theory", "Neuromodulatory_Architecture"],
    "CROSS_WM_GAMMA_BETA_DYNAMICS_001": ["Working_Memory_Theory", "Neural_Oscillation_Theory"],
    "ER_ECOLOGICAL_RATIONALITY_001": ["Ecological_Rationality", "Bounded_Rationality"],
    "SALIENCE_NETWORK_SWITCH_001": ["Salience_Network_Theory", "DMN_TPN_Theory"],
    "TEMPORAL_HIERARCHY_ARCH_PE_001": ["Temporal_Hierarchy_Theory", "Free_Energy_Minimization"],

    # MULTI-I templates
    "CROSSMODAL_CONGRUENCE_001": ["Multisensory_Integration_Theory", "Crossmodal_Correspondence"],
    "CT_AFFECTIVE_TOUCH_001": ["Affective_Touch_Theory", "Embodied_Cognition"],
    "HAP_SURFACE_MATERIAL_001": ["Haptic_Perception_Theory", "Embodied_Cognition"],
    "MATERIAL_AGING_TEMPORAL_DEPTH_001": ["Material_Culture_Theory", "Wabi_Sabi"],
    "MATERIAL_CULTURAL_CONDITIONING_001": ["Material_Culture_Theory", "Cultural_Neuroscience"],
    "MATERIAL_IDENTITY_INTEGRATION_001": ["Material_Culture_Theory", "Identity_Theory"],
    "MSI_CONGRUENCY_PRINCIPLE_001": ["Multisensory_Integration_Theory", "Bayesian_Cue_Integration"],
    "MSI_INVERSE_EFFECTIVENESS_002": ["Multisensory_Integration_Theory", "Bayesian_Cue_Integration"],
    "NATURAL_MATERIAL_CONVERGENCE_001": ["Biophilia", "Material_Culture_Theory"],

    # THERMAL-I templates
    "IC_THERMAL_COMFORT_001": ["Adaptive_Thermal_Comfort", "Allesthesia"],
    "THERMAL_ADAPTIVE_PE_001": ["Adaptive_Thermal_Comfort", "Free_Energy_Minimization"],
    "THERMAL_COMFORT_ADAPTIVE_PE_001": ["Adaptive_Thermal_Comfort", "Allesthesia"],

    # LIGHT-I templates
    "CB_SLEEP_ARCHITECTURE_002": ["Chronobiology", "Sleep_Architecture_Theory"],
    "CIRCADIAN_ARCH_REGULATION_001": ["Chronobiology", "Circadian_Architecture"],

    # Panel V / Tier 1 / MAT-I templates
    "DYNAMIC_LIGHT_TEMPORAL_001": ["Chronobiology", "Temporal_Dynamics"],
    "CHRONO_LIGHT_ENTRAINMENT_001": ["Chronobiology", "Circadian_Architecture"],
    "NM_CIRCADIAN_ENTRAINMENT_001": ["Chronobiology", "Neuromodulatory_Architecture"],
    "CCT_TEMPORAL_ECOLOGICAL_001": ["Chronobiology", "Ecological_Optics"],
}

# Default T1.5 for SPATIAL-I templates without explicit mapping
SPATIAL_I_DEFAULT = ["Space_Syntax", "Cognitive_Map_Theory"]


def is_calibrated(template_data: Dict) -> bool:
    """Check if template is marked as calibrated."""
    return (
        template_data.get("calibration_status") == "calibrated"
        or template_data.get("calibrated") is True
    )


def has_t1_5(template_data: Dict) -> bool:
    """Check if template has non-empty t1_5_parent_theories."""
    t1_5 = template_data.get("t1_5_parent_theories")
    return t1_5 is not None and isinstance(t1_5, list) and len(t1_5) > 0


def get_t1_5_theories(template_id: str, t1_frameworks: Optional[List[str]]) -> Optional[List[str]]:
    """
    Determine T1.5 theories for a template based on ID and T1 frameworks.
    
    Returns None if no mapping found (template should keep existing value).
    """
    # Check explicit mapping first
    if template_id in T1_5_MAPPING:
        return T1_5_MAPPING[template_id]
    
    # Check for SPATIAL-I pattern
    if "SPATIAL" in template_id.upper():
        return SPATIAL_I_DEFAULT
    
    # No mapping found
    return None


def process_templates(templates_dir: str) -> Dict[str, int]:
    """
    Process all template files and add T1.5 parent theories where needed.
    
    Returns: Dictionary with statistics
    """
    results = {
        "total": 0,
        "calibrated": 0,
        "already_have_t1_5": 0,
        "updated": 0,
        "skipped_no_mapping": 0,
        "errors": 0,
    }
    
    template_files = sorted(glob.glob(f"{templates_dir}/*.json"))
    
    for template_file in template_files:
        results["total"] += 1
        
        try:
            with open(template_file, "r") as f:
                template_data = json.load(f)
            
            # Check if calibrated
            if not is_calibrated(template_data):
                continue
            
            results["calibrated"] += 1
            template_id = template_data.get("template_id")
            t1_frameworks = template_data.get("t1_frameworks", [])
            
            # Check if already has T1.5
            if has_t1_5(template_data):
                results["already_have_t1_5"] += 1
                continue
            
            # Try to get T1.5 mapping
            t1_5_theories = get_t1_5_theories(template_id, t1_frameworks)
            
            if t1_5_theories is None:
                results["skipped_no_mapping"] += 1
                print(f"  SKIP (no mapping): {template_id}")
                continue
            
            # Update template
            template_data["t1_5_parent_theories"] = t1_5_theories
            
            # Write back
            with open(template_file, "w") as f:
                json.dump(template_data, f, indent=2)
            
            results["updated"] += 1
            print(f"  UPDATED: {template_id} <- {t1_5_theories}")
        
        except Exception as e:
            results["errors"] += 1
            print(f"  ERROR in {template_file}: {str(e)}")
    
    return results


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    templates_dir = repo_root / "data" / "templates"
    
    print("\n" + "="*80)
    print("T1.5 PARENT THEORIES EXPANSION")
    print("="*80)
    print(f"\nProcessing templates from: {templates_dir}")
    print("-" * 80)
    
    results = process_templates(str(templates_dir))
    
    print("\n" + "-" * 80)
    print("SUMMARY")
    print("-" * 80)
    print(f"Total templates:              {results['total']}")
    print(f"Calibrated:                   {results['calibrated']}")
    print(f"Already have T1.5:            {results['already_have_t1_5']}")
    print(f"Updated with T1.5:            {results['updated']}")
    print(f"Skipped (no mapping):         {results['skipped_no_mapping']}")
    print(f"Errors:                       {results['errors']}")
    print("="*80 + "\n")
    
    if results["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
