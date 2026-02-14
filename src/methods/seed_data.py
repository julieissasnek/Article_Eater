"""
Method Registry Seed Data (Sprint 4b / Task 4b.2).

Initial entries for 15+ common CNFA instruments and presentation modalities.
Based on Methodological_Validity_Framework_Tier2b_V1.0.docx.

References:
- Cortisol: Kirschbaum & Hellhammer (1994)
- HRV: Task Force (1996)
- EEG: Luck (2014)
- Critical instrument facts from CNFA literature review
"""

from src.methods.registry import (
    MethodEntry,
    MethodType,
    MovementCompatibility,
    ProfileStatus,
)


SEED_ENTRIES = [
    # =========================================================================
    # PHYSIOLOGICAL BIOMARKERS
    # =========================================================================

    MethodEntry(
        method_id="salivary_cortisol",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="HPA axis stress response",
        temporal_onset="15-20 min",
        temporal_peak="20-40 min",
        temporal_recovery="40-60 min",
        minimum_sampling_window="20 min post-stressor",
        confounds=[
            "diurnal_curve", "caffeine", "oral_contraceptives",
            "menstrual_phase", "exercise_within_2hr", "food_intake_30min",
            "seasonal_variation", "medications_corticosteroids_SSRIs"
        ],
        vr_specific_confounds=["headset_novelty_stress", "cybersickness"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "hpa_stress_reactivity": 0.95,
            "subjective_stress": 0.40,
            "autonomic_arousal": 0.20,
            "mood": 0.15
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="hrv_frequency_domain",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Autonomic nervous system balance",
        temporal_onset="seconds",
        temporal_peak="seconds",
        temporal_recovery="minutes",
        minimum_sampling_window="5 min for frequency domain",
        confounds=[
            "physical_activity", "respiratory_rate", "age",
            "fitness_level", "body_position", "medication"
        ],
        vr_specific_confounds=["cybersickness_elevates_sympathetic"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "parasympathetic_activity": 0.85,
            "sympathovagal_balance": 0.50,
            "relaxation": 0.70,
            "stress": 0.60
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="hrv_time_domain",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Heart rate variability (RMSSD, SDNN)",
        temporal_onset="immediate",
        minimum_sampling_window="2 min for time domain",
        confounds=[
            "physical_activity", "respiratory_rate", "age",
            "fitness_level", "body_position"
        ],
        vr_specific_confounds=["cybersickness_elevates_sympathetic"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "parasympathetic_activity": 0.80,
            "relaxation": 0.65,
            "stress": 0.55
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="eda_scr",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Skin conductance response (phasic)",
        temporal_onset="1-3 sec",
        temporal_peak="2-4 sec",
        temporal_recovery="4-6 sec",
        confounds=[
            "temperature", "humidity", "movement",
            "electrode_placement", "skin_hydration"
        ],
        vr_specific_confounds=["thermal_stress_from_headset"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "arousal": 0.85,
            "sympathetic_activation": 0.80,
            "emotional_intensity": 0.70,
            "valence": 0.20
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="eda_scl",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Skin conductance level (tonic)",
        temporal_onset="seconds",
        minimum_sampling_window="30 sec",
        confounds=[
            "temperature", "humidity", "baseline_drift",
            "electrode_placement", "skin_hydration"
        ],
        vr_specific_confounds=["thermal_stress_from_headset"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "tonic_arousal": 0.75,
            "sympathetic_tone": 0.70,
            "stress": 0.50
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="blood_pressure",
        method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
        construct_measured="Cardiovascular stress response",
        temporal_onset="seconds",
        confounds=[
            "physical_activity", "posture", "caffeine",
            "time_of_day", "medication"
        ],
        vr_specific_confounds=["postural_stress_standing_vr"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "cardiovascular_stress": 0.85,
            "sympathetic_activation": 0.75,
            "relaxation": 0.60
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    # =========================================================================
    # NEURAL IMAGING
    # =========================================================================

    MethodEntry(
        method_id="eeg_frequency_bands",
        method_type=MethodType.NEURAL_IMAGING,
        construct_measured="Cortical oscillatory activity",
        temporal_onset="immediate",
        minimum_sampling_window="2 sec for spectral analysis",
        spatial_resolution="centimeters (volume conduction)",
        confounds=[
            "movement_artifacts", "eye_blinks", "electrical_noise",
            "scalp_thickness", "hair_density"
        ],
        vr_specific_confounds=[
            "hmd_pressure_artifacts", "hmd_electromagnetic_interference",
            "electrode_coverage_blocked_by_hmd"
        ],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.NO,
        construct_validity_map={
            "cortical_arousal": 0.80,
            "relaxation_alpha": 0.75,
            "cognitive_engagement_beta": 0.70,
            "approach_withdrawal_motivation": 0.65,
            "specific_brain_region_activation": 0.30
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="fmri_bold",
        method_type=MethodType.NEURAL_IMAGING,
        construct_measured="Regional brain activation (hemodynamic)",
        temporal_onset="4-6 sec (hemodynamic lag)",
        temporal_peak="6-8 sec",
        spatial_resolution="millimeters",
        minimum_sampling_window="block design 15+ sec",
        confounds=[
            "head_motion", "physiological_noise", "scanner_drift",
            "task_difficulty_confound"
        ],
        vr_specific_confounds=["incompatible_with_standard_vr"],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.NO,
        construct_validity_map={
            "regional_brain_activation": 0.90,
            "cognitive_processing": 0.80,
            "emotional_processing": 0.75,
            "real_world_neural_activity": 0.40
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="fnirs",
        method_type=MethodType.NEURAL_IMAGING,
        construct_measured="Prefrontal cortical oxygenation",
        temporal_onset="2-4 sec",
        spatial_resolution="centimeters",
        confounds=[
            "scalp_blood_flow", "skin_tone", "hair",
            "motion_artifacts"
        ],
        vr_specific_confounds=["hmd_interference_with_prefrontal_sensors"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.CONFOUNDED,
        construct_validity_map={
            "prefrontal_activity": 0.75,
            "cognitive_load": 0.70,
            "attention": 0.60,
            "whole_brain_activation": 0.20
        },
        profile_status=ProfileStatus.PARTIALLY_CHARACTERIZED,
    ),

    # =========================================================================
    # BEHAVIORAL MEASURES
    # =========================================================================

    MethodEntry(
        method_id="eye_tracking",
        method_type=MethodType.BEHAVIORAL_MEASURE,
        construct_measured="Visual attention allocation",
        temporal_onset="immediate",
        confounds=[
            "calibration_drift", "glasses", "eye_makeup",
            "lighting_conditions"
        ],
        vr_specific_confounds=["hmd_integrated_tracker_accuracy"],
        valence_sensitivity=False,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_attention": 0.90,
            "interest": 0.70,
            "cognitive_load": 0.60,
            "preference": 0.40
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    # =========================================================================
    # SELF-REPORT MEASURES
    # =========================================================================

    MethodEntry(
        method_id="self_report_preference",
        method_type=MethodType.SELF_REPORT,
        construct_measured="Conscious evaluative judgment",
        temporal_onset="retrospective",
        confounds=[
            "demand_characteristics", "social_desirability", "scale_anchoring",
            "question_order", "mood_state", "fatigue"
        ],
        vr_specific_confounds=["technology_novelty_bias"],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "explicit_preference": 0.90,
            "actual_behavior": 0.50,
            "implicit_affect": 0.30,
            "physiological_response": 0.25
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="self_report_stai",
        method_type=MethodType.SELF_REPORT,
        construct_measured="State-Trait Anxiety Inventory",
        temporal_onset="retrospective",
        confounds=[
            "demand_characteristics", "alexithymia", "response_style"
        ],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "state_anxiety": 0.85,
            "trait_anxiety": 0.90,
            "physiological_anxiety": 0.50,
            "behavioral_avoidance": 0.45
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="self_report_panas",
        method_type=MethodType.SELF_REPORT,
        construct_measured="Positive and Negative Affect Schedule",
        temporal_onset="retrospective",
        confounds=[
            "demand_characteristics", "response_style", "time_frame_ambiguity"
        ],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "positive_affect": 0.85,
            "negative_affect": 0.85,
            "arousal": 0.60,
            "physiological_state": 0.35
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="self_report_prs",
        method_type=MethodType.SELF_REPORT,
        construct_measured="Perceived Restorativeness Scale",
        temporal_onset="retrospective",
        confounds=[
            "demand_characteristics", "environmental_familiarity",
            "baseline_fatigue_level"
        ],
        valence_sensitivity=True,
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "perceived_restoration": 0.90,
            "attention_restoration": 0.75,
            "actual_cognitive_recovery": 0.50,
            "physiological_recovery": 0.30
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    # =========================================================================
    # PRESENTATION MODALITIES
    # =========================================================================

    MethodEntry(
        method_id="photographs_2d",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="2D visual representation of environment",
        confounds=[
            "viewing_angle_fixed", "lighting_conditions_photo",
            "resolution", "display_calibration"
        ],
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_preference": 0.86,  # Stamps (1990) r=0.86 with in-situ
            "aesthetic_judgment": 0.80,
            "wayfinding": 0.20,
            "stress_response": 0.30,
            "spatial_cognition": 0.25,
            "attention_restoration": 0.40,
            "material_preference": 0.75
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="vr_hmd_stationary",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="Immersive visual environment (stationary)",
        confounds=[
            "fov_restriction_110deg", "resolution_20ppd",
            "haptic_absence", "thermal_absence", "olfactory_absence"
        ],
        vr_specific_confounds=[
            "cybersickness", "vergence_accommodation_conflict",
            "weight_discomfort"
        ],
        movement_compatible=MovementCompatibility.NO,
        construct_validity_map={
            "visual_preference": 0.80,
            "presence": 0.75,
            "stress_response": 0.60,
            "spatial_cognition": 0.50,
            "wayfinding": 0.40,
            "attention_restoration": 0.50
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="vr_hmd_room_scale",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="Immersive visual environment with locomotion",
        confounds=[
            "fov_restriction_110deg", "resolution_20ppd",
            "haptic_absence", "thermal_absence", "olfactory_absence"
        ],
        vr_specific_confounds=[
            "vestibular_visual_conflict_reduced",
            "tracking_boundary_artifacts"
        ],
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_preference": 0.85,
            "wayfinding": 0.70,
            "stress_response": 0.65,
            "spatial_cognition": 0.70,
            "attention_restoration": 0.55,
            "material_preference": 0.20,
            "social_behavior": 0.35,
            "temporal_comprehension": 0.50
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="vr_cave",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="CAVE automatic virtual environment",
        confounds=[
            "limited_tracking_volume", "projection_resolution",
            "haptic_absence", "olfactory_absence"
        ],
        vr_specific_confounds=[
            "reduced_cybersickness_vs_hmd",
            "peripheral_vision_preserved"
        ],
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_preference": 0.85,
            "stress_response": 0.75,  # Fich et al. (2014) used CAVE
            "spatial_cognition": 0.70,
            "wayfinding": 0.65,
            "presence": 0.80
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),

    MethodEntry(
        method_id="real_building_controlled",
        method_type=MethodType.PRESENTATION_MODALITY,
        construct_measured="Real physical environment (controlled study)",
        confounds=[
            "uncontrolled_variables", "temporal_variation",
            "other_occupants", "researcher_presence"
        ],
        movement_compatible=MovementCompatibility.YES,
        construct_validity_map={
            "visual_preference": 0.95,
            "stress_response": 0.90,
            "spatial_cognition": 0.95,
            "wayfinding": 0.95,
            "attention_restoration": 0.90,
            "social_behavior": 0.90,
            "thermal_comfort": 0.95,
            "acoustic_experience": 0.95
        },
        profile_status=ProfileStatus.WELL_CHARACTERIZED,
    ),
]


def load_seed_entries(registry) -> int:
    """
    Load all seed entries into a registry.

    Returns:
        Number of entries loaded
    """
    for entry in SEED_ENTRIES:
        registry.add(entry)
    return len(SEED_ENTRIES)
