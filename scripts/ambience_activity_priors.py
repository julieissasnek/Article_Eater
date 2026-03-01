#!/usr/bin/env python3
"""
Ambience-Activity Prior Model for CMR Prediction Engine
========================================================

Encodes the conditional probability structure of real interior environments:
  - P(lighting | activity_type, time_of_day)
  - P(noise_level | activity_type, space_type)
  - P(material_palette | space_type)
  - P(co-occurring_features | anchor_feature)

Grounded in three frameworks:
  1. Mehrabian & Russell (1974) PAD dimensions for emotional response
  2. Bitner (1992) Servicescape dimensions (ambient, spatial, signs/symbols)
  3. Kruithof (1941) lighting preference (CCT × illuminance × task)

The model classifies environments by activity-type and computes which
template compositions are REALISTIC (occur in actual built environments)
vs. ANOMALOUS (rare combinations that would be more informative to test).

Author: David Kirsh & Claude Opus 4.6
Date:   2026-02-24
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import defaultdict

# ─── Activity-Space Types ────────────────────────────────────────

# Based on Bitner (1992) servicescape + Places365 indoor categories
# Each activity type has characteristic ambient profiles

@dataclass
class AmbientProfile:
    """Characteristic ambient conditions for a space-activity type."""
    # Lighting
    illuminance_lux_range: tuple = (0, 0)      # (min, max) typical lux
    cct_kelvin_range: tuple = (0, 0)            # color temperature range
    daylight_fraction: float = 0.0              # 0-1, proportion of light from daylight
    # Acoustic
    background_noise_dB: tuple = (0, 0)         # (min, max) typical dB(A)
    speech_intelligibility: float = 0.0         # 0-1, fraction of speech that is intelligible
    natural_sound_fraction: float = 0.0         # 0-1, fraction of soundscape that is natural
    # Olfactory
    olfactory_valence: float = 0.0              # -1 to +1 (unpleasant to pleasant)
    scent_complexity: int = 0                   # number of distinct odorant sources
    # Thermal
    temperature_C_range: tuple = (0, 0)         # (min, max) air temp
    thermal_variability: float = 0.0            # 0-1, how much temperature fluctuates
    # Social
    social_density: float = 0.0                 # people per 10m²
    social_modes: int = 0                       # number of social modes supported
    # PAD emotional target (Mehrabian & Russell)
    pleasure_target: float = 0.0                # -1 to +1
    arousal_target: float = 0.0                 # -1 to +1 (low = calm, high = stimulating)
    dominance_target: float = 0.0               # -1 to +1 (low = submissive, high = in control)


# ─── Canonical Activity-Space Profiles ───────────────────────────

ACTIVITY_PROFILES = {
    # ─── Focus/Cognitive Work ────────────────────────
    "deep_reading": AmbientProfile(
        illuminance_lux_range=(300, 500),
        cct_kelvin_range=(3000, 4000),
        daylight_fraction=0.5,
        background_noise_dB=(25, 35),
        speech_intelligibility=0.0,
        natural_sound_fraction=0.0,
        olfactory_valence=0.2,
        scent_complexity=1,
        temperature_C_range=(21, 23),
        thermal_variability=0.1,
        social_density=0.5,
        social_modes=1,
        pleasure_target=0.4,
        arousal_target=-0.3,
        dominance_target=0.5,
    ),
    "focused_computer_work": AmbientProfile(
        illuminance_lux_range=(300, 500),
        cct_kelvin_range=(4000, 5000),
        daylight_fraction=0.3,
        background_noise_dB=(30, 45),
        speech_intelligibility=0.2,
        natural_sound_fraction=0.0,
        olfactory_valence=0.0,
        scent_complexity=0,
        temperature_C_range=(21, 24),
        thermal_variability=0.05,
        social_density=2.0,
        social_modes=2,
        pleasure_target=0.2,
        arousal_target=0.1,
        dominance_target=0.4,
    ),

    # ─── Creative Work ────────────────────────────────
    "creative_brainstorming": AmbientProfile(
        illuminance_lux_range=(100, 300),
        cct_kelvin_range=(2700, 3500),
        daylight_fraction=0.4,
        background_noise_dB=(50, 70),
        speech_intelligibility=0.3,
        natural_sound_fraction=0.1,
        olfactory_valence=0.3,
        scent_complexity=2,
        temperature_C_range=(22, 25),
        thermal_variability=0.1,
        social_density=3.0,
        social_modes=3,
        pleasure_target=0.5,
        arousal_target=0.3,
        dominance_target=0.3,
    ),
    "painting_drawing": AmbientProfile(
        illuminance_lux_range=(400, 800),
        cct_kelvin_range=(5000, 6500),
        daylight_fraction=0.8,
        background_noise_dB=(25, 40),
        speech_intelligibility=0.0,
        natural_sound_fraction=0.2,
        olfactory_valence=0.1,
        scent_complexity=2,
        temperature_C_range=(20, 23),
        thermal_variability=0.15,
        social_density=0.3,
        social_modes=1,
        pleasure_target=0.5,
        arousal_target=0.0,
        dominance_target=0.6,
    ),

    # ─── Social ───────────────────────────────────────
    "intimate_conversation": AmbientProfile(
        illuminance_lux_range=(50, 150),
        cct_kelvin_range=(2200, 3000),
        daylight_fraction=0.2,
        background_noise_dB=(35, 50),
        speech_intelligibility=0.1,
        natural_sound_fraction=0.05,
        olfactory_valence=0.5,
        scent_complexity=3,
        temperature_C_range=(22, 24),
        thermal_variability=0.05,
        social_density=1.0,
        social_modes=2,
        pleasure_target=0.7,
        arousal_target=-0.1,
        dominance_target=0.5,
    ),
    "group_socializing": AmbientProfile(
        illuminance_lux_range=(100, 300),
        cct_kelvin_range=(2700, 4000),
        daylight_fraction=0.3,
        background_noise_dB=(55, 70),
        speech_intelligibility=0.4,
        natural_sound_fraction=0.0,
        olfactory_valence=0.3,
        scent_complexity=3,
        temperature_C_range=(22, 25),
        thermal_variability=0.1,
        social_density=5.0,
        social_modes=4,
        pleasure_target=0.6,
        arousal_target=0.4,
        dominance_target=0.2,
    ),
    "formal_dining": AmbientProfile(
        illuminance_lux_range=(50, 200),
        cct_kelvin_range=(2200, 3000),
        daylight_fraction=0.1,
        background_noise_dB=(45, 60),
        speech_intelligibility=0.2,
        natural_sound_fraction=0.0,
        olfactory_valence=0.7,
        scent_complexity=5,
        temperature_C_range=(21, 23),
        thermal_variability=0.05,
        social_density=3.0,
        social_modes=2,
        pleasure_target=0.8,
        arousal_target=0.1,
        dominance_target=0.3,
    ),

    # ─── Restoration ──────────────────────────────────
    "meditation_quiet_rest": AmbientProfile(
        illuminance_lux_range=(20, 100),
        cct_kelvin_range=(2200, 2700),
        daylight_fraction=0.3,
        background_noise_dB=(20, 30),
        speech_intelligibility=0.0,
        natural_sound_fraction=0.5,
        olfactory_valence=0.6,
        scent_complexity=1,
        temperature_C_range=(22, 24),
        thermal_variability=0.05,
        social_density=0.2,
        social_modes=1,
        pleasure_target=0.6,
        arousal_target=-0.6,
        dominance_target=0.7,
    ),
    "nature_walk_garden": AmbientProfile(
        illuminance_lux_range=(5000, 100000),
        cct_kelvin_range=(5500, 6500),
        daylight_fraction=1.0,
        background_noise_dB=(35, 50),
        speech_intelligibility=0.0,
        natural_sound_fraction=0.8,
        olfactory_valence=0.7,
        scent_complexity=4,
        temperature_C_range=(18, 28),
        thermal_variability=0.4,
        social_density=0.5,
        social_modes=3,
        pleasure_target=0.7,
        arousal_target=-0.2,
        dominance_target=0.6,
    ),

    # ─── Clinical/Healthcare ──────────────────────────
    "hospital_patient_recovery": AmbientProfile(
        illuminance_lux_range=(100, 300),
        cct_kelvin_range=(3500, 4500),
        daylight_fraction=0.5,
        background_noise_dB=(35, 55),
        speech_intelligibility=0.3,
        natural_sound_fraction=0.1,
        olfactory_valence=-0.3,
        scent_complexity=2,
        temperature_C_range=(22, 24),
        thermal_variability=0.05,
        social_density=0.5,
        social_modes=2,
        pleasure_target=0.3,
        arousal_target=-0.3,
        dominance_target=-0.2,
    ),

    # ─── Retail/Commercial ────────────────────────────
    "retail_browsing": AmbientProfile(
        illuminance_lux_range=(300, 750),
        cct_kelvin_range=(3000, 4500),
        daylight_fraction=0.2,
        background_noise_dB=(50, 65),
        speech_intelligibility=0.2,
        natural_sound_fraction=0.0,
        olfactory_valence=0.4,
        scent_complexity=3,
        temperature_C_range=(21, 24),
        thermal_variability=0.05,
        social_density=4.0,
        social_modes=3,
        pleasure_target=0.5,
        arousal_target=0.3,
        dominance_target=0.2,
    ),

    # ─── Educational ──────────────────────────────────
    "classroom_lecture": AmbientProfile(
        illuminance_lux_range=(300, 500),
        cct_kelvin_range=(4000, 5000),
        daylight_fraction=0.4,
        background_noise_dB=(35, 50),
        speech_intelligibility=0.9,
        natural_sound_fraction=0.0,
        olfactory_valence=0.0,
        scent_complexity=0,
        temperature_C_range=(21, 24),
        thermal_variability=0.05,
        social_density=5.0,
        social_modes=2,
        pleasure_target=0.2,
        arousal_target=0.2,
        dominance_target=-0.2,
    ),
}

# ─── Time-of-Day Modifiers ──────────────────────────────────────

TIME_OF_DAY_MODIFIERS = {
    "early_morning_0600_0800": {
        "illuminance_multiplier": 0.6,
        "cct_shift_K": -500,           # warmer at dawn
        "daylight_fraction_override": 0.3,
        "arousal_shift": -0.2,
        "cortisol_phase": "rising",
        "melatonin_phase": "falling",
        "circadian_alerting_need": "HIGH",
        "optimal_task": ["gentle_wake", "light_exercise", "planning"],
    },
    "morning_0800_1200": {
        "illuminance_multiplier": 1.0,
        "cct_shift_K": 0,
        "daylight_fraction_override": None,
        "arousal_shift": 0.0,
        "cortisol_phase": "peak",
        "melatonin_phase": "suppressed",
        "circadian_alerting_need": "LOW",
        "optimal_task": ["focused_work", "complex_problem_solving", "critical_thinking"],
    },
    "afternoon_1200_1700": {
        "illuminance_multiplier": 1.0,
        "cct_shift_K": 0,
        "daylight_fraction_override": None,
        "arousal_shift": -0.1,         # post-lunch dip
        "cortisol_phase": "declining",
        "melatonin_phase": "suppressed",
        "circadian_alerting_need": "MODERATE",
        "optimal_task": ["creative_work", "collaboration", "routine_tasks"],
    },
    "late_afternoon_1700_1900": {
        "illuminance_multiplier": 0.7,
        "cct_shift_K": -300,
        "daylight_fraction_override": 0.5,
        "arousal_shift": -0.1,
        "cortisol_phase": "low",
        "melatonin_phase": "pre-onset",
        "circadian_alerting_need": "MODERATE",
        "optimal_task": ["social_interaction", "light_creative_work", "exercise"],
    },
    "evening_1900_2200": {
        "illuminance_multiplier": 0.4,
        "cct_shift_K": -1000,          # should be warm, low blue
        "daylight_fraction_override": 0.0,
        "arousal_shift": -0.3,
        "cortisol_phase": "nadir",
        "melatonin_phase": "onset",
        "circadian_alerting_need": "AVOID",
        "optimal_task": ["relaxation", "social", "light_reading", "entertainment"],
    },
    "night_2200_0600": {
        "illuminance_multiplier": 0.1,
        "cct_shift_K": -1500,
        "daylight_fraction_override": 0.0,
        "arousal_shift": -0.6,
        "cortisol_phase": "nadir",
        "melatonin_phase": "peak",
        "circadian_alerting_need": "CONTRAINDICATED",
        "optimal_task": ["sleep", "rest"],
    },
}


# ─── Feature Co-occurrence Priors ────────────────────────────────

# P(feature_B | feature_A) — empirical co-occurrence in real interiors
# Based on architectural conventions, design pattern co-occurrence,
# and Bitner (1992) servicescape dimension correlations
#
# Format: {anchor_feature: {co_feature: probability}}

FEATURE_COOCCURRENCE = {
    # Material co-occurrences
    "teak_wall_paneling": {
        "tropical_plants": 0.65,
        "polished_concrete_floor": 0.40,
        "warm_lighting_3000K": 0.75,
        "natural_stone_accents": 0.35,
        "diffuse_indirect_light": 0.60,
        "leather_furniture": 0.45,
        "cedar_scent": 0.15,
        "water_feature": 0.20,
    },
    "exposed_concrete_walls": {
        "steel_fixtures": 0.55,
        "pendant_industrial_lights": 0.50,
        "polished_concrete_floor": 0.60,
        "open_ductwork": 0.45,
        "large_windows": 0.40,
        "minimal_plants": 0.30,
        "cool_lighting_5000K": 0.35,
    },
    "floor_to_ceiling_windows": {
        "daylight_dominant": 0.85,
        "nature_view": 0.50,
        "glare_risk": 0.40,
        "warm_floor_material": 0.30,
        "circadian_benefit": 0.75,
        "thermal_asymmetry": 0.45,
    },
    "biophilic_green_wall": {
        "natural_daylight": 0.60,
        "wood_accents": 0.55,
        "water_feature": 0.30,
        "earth_tones": 0.50,
        "natural_soundscape": 0.20,
        "plant_scent": 0.40,
        "warm_lighting_3000K": 0.45,
    },
    "open_plan_office": {
        "speech_noise_55dB": 0.80,
        "mechanical_HVAC_hum": 0.75,
        "fluorescent_4000K": 0.50,
        "low_ceiling_2_4m": 0.45,
        "carpet_floor": 0.60,
        "acoustic_panels": 0.35,
        "minimal_daylight": 0.40,
        "high_social_density": 0.70,
    },

    # Lighting co-occurrences
    "warm_dim_lighting_2700K_100lux": {
        "evening_activity": 0.70,
        "intimate_social": 0.60,
        "candles_present": 0.30,
        "dark_wood_materials": 0.45,
        "soft_textiles": 0.50,
        "low_noise_level": 0.40,
        "pleasant_scent": 0.35,
    },
    "bright_daylight_6500K_500lux": {
        "morning_activity": 0.55,
        "productive_task": 0.65,
        "large_windows": 0.70,
        "white_neutral_materials": 0.45,
        "minimal_scent": 0.60,
        "moderate_noise": 0.40,
    },

    # Activity-space co-occurrences
    "cafe_setting": {
        "warm_lighting_3000K": 0.65,
        "background_music": 0.80,
        "coffee_aroma": 0.90,
        "wood_furniture": 0.55,
        "speech_babble_55dB": 0.75,
        "moderate_social_density": 0.70,
        "plants_present": 0.40,
    },
    "library_reading_room": {
        "quiet_25dB": 0.85,
        "neutral_lighting_4000K": 0.60,
        "daylight_supplemented": 0.50,
        "wood_paneling": 0.40,
        "book_paper_scent": 0.70,
        "low_social_density": 0.75,
        "high_ceiling": 0.35,
    },
    "spa_treatment_room": {
        "dim_warm_lighting_2700K": 0.85,
        "nature_soundscape": 0.70,
        "essential_oil_scent": 0.90,
        "natural_materials": 0.75,
        "water_feature": 0.50,
        "warm_temperature_24C": 0.80,
        "solo_or_dyad": 0.90,
    },
}


# ─── Lighting × Time × Task Interaction Model ───────────────────

def compute_lighting_task_fit(
    illuminance_lux: float,
    cct_kelvin: float,
    time_of_day: str,
    activity_type: str
) -> dict:
    """
    Compute how well a lighting condition fits a task at a given time.
    Returns fit score (0-1) and specific interaction predictions.

    Based on:
    - Kruithof (1941) comfort region (CCT × illuminance)
    - L2 template (circadian regulation via melanopic irradiance)
    - Steidle & Werth (2013): dim light → creative; bright light → analytical
    - Time-of-day circadian modulation
    """
    result = {
        "fit_score": 0.0,
        "kruithof_region": "",
        "circadian_alignment": "",
        "task_alignment": "",
        "interactions": [],
        "predictions": [],
    }

    # Get activity profile
    profile = ACTIVITY_PROFILES.get(activity_type)
    if not profile:
        result["fit_score"] = 0.5
        result["task_alignment"] = "unknown_activity"
        return result

    # Get time modifier
    time_mod = TIME_OF_DAY_MODIFIERS.get(time_of_day, {})

    # ── Kruithof comfort check ──
    # Warm light (2700K) at low lux = comfortable
    # Cool light (6500K) at high lux = comfortable
    # Cool light at low lux = cold/dim (uncomfortable)
    # Warm light at high lux = unnatural (uncomfortable)
    kruithof_score = 0.5
    if cct_kelvin < 3500 and illuminance_lux < 200:
        kruithof_score = 0.8  # warm + dim = cozy
        result["kruithof_region"] = "warm_dim_comfortable"
    elif cct_kelvin > 5000 and illuminance_lux > 300:
        kruithof_score = 0.7  # cool + bright = alerting
        result["kruithof_region"] = "cool_bright_alerting"
    elif cct_kelvin > 5000 and illuminance_lux < 150:
        kruithof_score = 0.2  # cool + dim = cold/uncomfortable
        result["kruithof_region"] = "cool_dim_UNCOMFORTABLE"
    elif cct_kelvin < 3000 and illuminance_lux > 500:
        kruithof_score = 0.3  # warm + very bright = unnatural
        result["kruithof_region"] = "warm_bright_UNNATURAL"
    else:
        kruithof_score = 0.6
        result["kruithof_region"] = "neutral_zone"

    # ── Circadian alignment ──
    circadian_score = 0.5
    circadian_need = time_mod.get("circadian_alerting_need", "MODERATE")

    if circadian_need == "HIGH":
        # Morning: need bright, blue-enriched light
        if illuminance_lux > 300 and cct_kelvin > 4000:
            circadian_score = 0.9
            result["circadian_alignment"] = "EXCELLENT: bright cool light supports morning cortisol rise"
        elif illuminance_lux < 150:
            circadian_score = 0.2
            result["circadian_alignment"] = "POOR: insufficient melanopic irradiance for morning alerting"
            result["predictions"].append(
                "Prediction: occupants will show delayed cortisol peak (30-60 min late) "
                "and slower cognitive warm-up (Figueiro et al., 2017)"
            )
    elif circadian_need == "AVOID" or circadian_need == "CONTRAINDICATED":
        # Evening/night: bright cool light disrupts melatonin
        if illuminance_lux > 200 and cct_kelvin > 4000:
            circadian_score = 0.1
            result["circadian_alignment"] = "HARMFUL: bright cool evening light suppresses melatonin onset"
            result["predictions"].append(
                "Prediction: melatonin onset delayed 30-90 min; sleep onset delayed; "
                "next-day cognitive performance reduced (Chang et al., 2015). "
                "This NEGATES any restorative benefit from other environmental features."
            )
            result["interactions"].append({
                "type": "NEGATION",
                "source": "evening_blue_light",
                "target": "ALL_restorative_templates",
                "mechanism": "HPA/circadian disruption overrides parasympathetic restoration",
            })
        elif illuminance_lux < 50 and cct_kelvin < 3000:
            circadian_score = 0.9
            result["circadian_alignment"] = "EXCELLENT: warm dim light supports melatonin onset"

    # ── Task alignment ──
    # Steidle & Werth (2013): dim → creative, bright → analytical
    task_score = 0.5
    target_arousal = profile.arousal_target

    if target_arousal < -0.2:  # low arousal tasks (rest, meditation, intimate conversation)
        if illuminance_lux < 200 and cct_kelvin < 3500:
            task_score = 0.9
            result["task_alignment"] = "EXCELLENT: dim warm light supports low-arousal activity"
        elif illuminance_lux > 500:
            task_score = 0.2
            result["task_alignment"] = "POOR: bright light raises arousal, counteracting rest/relaxation"
            result["predictions"].append(
                f"Prediction: {activity_type} effectiveness reduced 20-40% under bright lighting "
                "due to arousal-task mismatch (Steidle & Werth, 2013)"
            )
    elif target_arousal > 0.2:  # high arousal tasks (brainstorming, socializing)
        if illuminance_lux > 200 and cct_kelvin > 3500:
            task_score = 0.8
            result["task_alignment"] = "GOOD: moderate-bright light supports alert engagement"
        elif illuminance_lux < 100:
            task_score = 0.4
            result["task_alignment"] = "SUBOPTIMAL: dim light may reduce alertness for high-arousal task"
    else:  # neutral arousal tasks (reading, focused work)
        lux_min, lux_max = profile.illuminance_lux_range
        if lux_min <= illuminance_lux <= lux_max:
            task_score = 0.8
            result["task_alignment"] = f"GOOD: illuminance within optimal range for {activity_type}"
        else:
            task_score = 0.4
            result["task_alignment"] = f"SUBOPTIMAL: illuminance outside optimal range ({lux_min}-{lux_max} lux)"

    # ── Combined fit ──
    result["fit_score"] = round(0.3 * kruithof_score + 0.35 * circadian_score + 0.35 * task_score, 3)
    return result


# ─── Noise × Activity Interaction Model ──────────────────────────

def compute_noise_activity_fit(
    noise_dB: float,
    speech_intelligibility: float,
    natural_sound_fraction: float,
    activity_type: str
) -> dict:
    """
    Compute how well an acoustic condition fits an activity.

    Based on:
    - Mehta et al. (2012): 70dB ambient noise → creative boost
    - Evans & Johnson (2000): open-plan speech noise → cognitive decrement
    - SND1 template: 1/f natural sounds → parasympathetic activation
    - MS_ACOUSTIC_ECOLOGY: source identification → pleasantness
    """
    result = {
        "fit_score": 0.0,
        "noise_assessment": "",
        "speech_interference": "",
        "natural_sound_benefit": "",
        "interactions": [],
        "predictions": [],
    }

    profile = ACTIVITY_PROFILES.get(activity_type)
    if not profile:
        result["fit_score"] = 0.5
        return result

    target_noise_min, target_noise_max = profile.background_noise_dB
    target_speech = profile.speech_intelligibility

    # Noise level fit
    noise_score = 0.5
    if target_noise_min <= noise_dB <= target_noise_max:
        noise_score = 0.8
        result["noise_assessment"] = f"GOOD: {noise_dB}dB within target range for {activity_type}"
    elif noise_dB > target_noise_max + 15:
        noise_score = 0.1
        result["noise_assessment"] = f"POOR: {noise_dB}dB exceeds comfortable range by {noise_dB - target_noise_max}dB"
        result["predictions"].append(
            f"Prediction: {activity_type} performance degraded 15-30% by excessive noise "
            "(Banbury & Berry, 2005). Cortisol elevated, HRV reduced."
        )
    elif noise_dB < target_noise_min - 10:
        noise_score = 0.5
        result["noise_assessment"] = f"TOO QUIET: {noise_dB}dB may produce discomfort from silence/isolation"

    # Speech interference check
    speech_score = 0.5
    if speech_intelligibility > target_speech + 0.3:
        speech_score = 0.2
        result["speech_interference"] = "HIGH: unwanted intelligible speech captures attention"
        result["interactions"].append({
            "type": "NEGATION",
            "source": "intelligible_speech",
            "target": "all_cognitive_templates",
            "mechanism": "Obligatory semantic processing via left-lateralized language network",
        })
        result["predictions"].append(
            "Prediction: intelligible speech NEGATES visual restoration (ART), "
            "fractal fluency aesthetic response, and focused cognition. "
            "Effect is independent of speech volume — 50dB intelligible speech "
            "is more disruptive than 70dB unintelligible babble (Banbury et al., 2001)."
        )
    else:
        speech_score = 0.7
        result["speech_interference"] = "LOW: speech intelligibility within acceptable range"

    # Natural sound benefit
    natural_score = 0.5
    if natural_sound_fraction > 0.3:
        natural_score = 0.8
        result["natural_sound_benefit"] = f"ACTIVE: {natural_sound_fraction:.0%} natural sounds engage 1/f restoration"
        result["predictions"].append(
            "Prediction: natural soundscape component provides parasympathetic benefit "
            "independent of noise level. Even at 55dB, natural 1/f sounds reduce "
            "cortisol vs. mechanical noise at same level (Alvarsson et al., 2010)."
        )
    elif natural_sound_fraction > 0:
        natural_score = 0.6
        result["natural_sound_benefit"] = f"PARTIAL: {natural_sound_fraction:.0%} natural sounds present"
    else:
        natural_score = 0.5
        result["natural_sound_benefit"] = "ABSENT: no natural sound component"

    result["fit_score"] = round(0.4 * noise_score + 0.35 * speech_score + 0.25 * natural_score, 3)
    return result


# ─── Co-occurrence Anomaly Detection ─────────────────────────────

def detect_anomalous_combinations(features: list) -> list:
    """
    Given a set of environmental features, identify which combinations
    are anomalous (rare in real interiors) and therefore more informative
    to test experimentally.
    """
    anomalies = []

    # Check each pair against co-occurrence priors
    for anchor in features:
        if anchor in FEATURE_COOCCURRENCE:
            cooccur = FEATURE_COOCCURRENCE[anchor]
            for other_feature in features:
                if other_feature == anchor:
                    continue
                # Check if this feature is expected
                prob = cooccur.get(other_feature, None)
                if prob is not None and prob < 0.15:
                    anomalies.append({
                        "anchor": anchor,
                        "co_feature": other_feature,
                        "expected_probability": prob,
                        "classification": "ANOMALOUS_RARE",
                        "informativeness": "HIGH — this combination rarely occurs naturally, "
                                          "so testing it would reveal whether the mechanism "
                                          "operates independently of typical context",
                    })
                elif prob is None:
                    # Not in the co-occurrence table at all — check for obvious clashes
                    anomalies.append({
                        "anchor": anchor,
                        "co_feature": other_feature,
                        "expected_probability": "unknown",
                        "classification": "UNATTESTED",
                        "informativeness": "MODERATE — this combination is not attested in "
                                          "the co-occurrence data, suggesting it is either "
                                          "very rare or meaningfully unusual",
                    })

    return anomalies


# ─── Export ──────────────────────────────────────────────────────

def export_all_profiles() -> dict:
    """Export all profiles, modifiers, and co-occurrence data as JSON."""
    return {
        "activity_profiles": {
            name: asdict(profile) for name, profile in ACTIVITY_PROFILES.items()
        },
        "time_of_day_modifiers": TIME_OF_DAY_MODIFIERS,
        "feature_cooccurrence": FEATURE_COOCCURRENCE,
        "metadata": {
            "version": "1.0.0",
            "frameworks": [
                "Mehrabian & Russell (1974) PAD dimensions",
                "Bitner (1992) Servicescape",
                "Kruithof (1941) CCT × illuminance comfort",
                "Steidle & Werth (2013) light level × creativity",
                "Figueiro et al. (2017) circadian light timing",
            ],
        }
    }


if __name__ == "__main__":
    import sys

    # Demo: test a few scenarios
    print("=" * 70)
    print("AMBIENCE-ACTIVITY PRIOR MODEL — DEMO SCENARIOS")
    print("=" * 70)

    scenarios = [
        ("Evening reading in warm dim light",
         {"illuminance_lux": 80, "cct_kelvin": 2700,
          "time_of_day": "evening_1900_2200", "activity_type": "deep_reading"}),
        ("Evening reading under bright cool light (MISMATCH)",
         {"illuminance_lux": 500, "cct_kelvin": 6500,
          "time_of_day": "evening_1900_2200", "activity_type": "deep_reading"}),
        ("Morning focused work in daylit office",
         {"illuminance_lux": 400, "cct_kelvin": 5000,
          "time_of_day": "morning_0800_1200", "activity_type": "focused_computer_work"}),
        ("Creative brainstorming in dim afternoon studio",
         {"illuminance_lux": 150, "cct_kelvin": 3000,
          "time_of_day": "afternoon_1200_1700", "activity_type": "creative_brainstorming"}),
        ("Meditation in bright fluorescent office (MISMATCH)",
         {"illuminance_lux": 500, "cct_kelvin": 5000,
          "time_of_day": "evening_1900_2200", "activity_type": "meditation_quiet_rest"}),
    ]

    for desc, params in scenarios:
        print(f"\n{'─' * 60}")
        print(f"Scenario: {desc}")
        result = compute_lighting_task_fit(**params)
        print(f"  Fit score:    {result['fit_score']:.3f}")
        print(f"  Kruithof:     {result['kruithof_region']}")
        print(f"  Circadian:    {result['circadian_alignment']}")
        print(f"  Task fit:     {result['task_alignment']}")
        for pred in result.get("predictions", []):
            print(f"  PREDICTION:   {pred[:100]}")
        for interaction in result.get("interactions", []):
            print(f"  INTERACTION:  {interaction['type']}: {interaction['source']} → {interaction['target']}")

    # Noise scenarios
    print(f"\n{'=' * 70}")
    print("NOISE × ACTIVITY SCENARIOS")
    print(f"{'=' * 70}")

    noise_scenarios = [
        ("Quiet library reading",
         {"noise_dB": 30, "speech_intelligibility": 0.0,
          "natural_sound_fraction": 0.0, "activity_type": "deep_reading"}),
        ("Open-plan office focused work (speech noise)",
         {"noise_dB": 55, "speech_intelligibility": 0.6,
          "natural_sound_fraction": 0.0, "activity_type": "focused_computer_work"}),
        ("Cafe brainstorming (babble + music)",
         {"noise_dB": 65, "speech_intelligibility": 0.2,
          "natural_sound_fraction": 0.0, "activity_type": "creative_brainstorming"}),
        ("Garden meditation (birdsong + breeze)",
         {"noise_dB": 40, "speech_intelligibility": 0.0,
          "natural_sound_fraction": 0.7, "activity_type": "meditation_quiet_rest"}),
    ]

    for desc, params in noise_scenarios:
        print(f"\n{'─' * 60}")
        print(f"Scenario: {desc}")
        result = compute_noise_activity_fit(**params)
        print(f"  Fit score:    {result['fit_score']:.3f}")
        print(f"  Noise:        {result['noise_assessment']}")
        print(f"  Speech:       {result['speech_interference']}")
        print(f"  Natural:      {result['natural_sound_benefit']}")
        for pred in result.get("predictions", []):
            print(f"  PREDICTION:   {pred[:100]}")
        for interaction in result.get("interactions", []):
            print(f"  INTERACTION:  {interaction['type']}: {interaction['source']} → {interaction['target']}")

    # Anomaly detection
    print(f"\n{'=' * 70}")
    print("CO-OCCURRENCE ANOMALY DETECTION")
    print(f"{'=' * 70}")

    test_sets = [
        ("Typical spa", ["spa_treatment_room", "dim_warm_lighting_2700K", "nature_soundscape"]),
        ("Anomalous: teak walls + fluorescent", ["teak_wall_paneling", "cool_lighting_5000K"]),
        ("Anomalous: open plan + nature sounds", ["open_plan_office", "natural_soundscape"]),
        ("Typical cafe", ["cafe_setting", "warm_lighting_3000K", "coffee_aroma"]),
    ]

    for desc, features in test_sets:
        anomalies = detect_anomalous_combinations(features)
        print(f"\n{desc}: {features}")
        if anomalies:
            for a in anomalies[:3]:
                print(f"  {a['classification']}: {a['anchor']} + {a['co_feature']} "
                      f"(P={a['expected_probability']})")
        else:
            print("  No anomalies detected (all combinations are typical)")
