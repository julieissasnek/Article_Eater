#!/usr/bin/env python3
"""
Architectural Typology Priors for CMR Prediction Grounding
==========================================================

Encodes the conditional probability structure of architectural features
within room types designed for specific activities.

The central insight: rooms designed for particular activities have
characteristic architectural signatures — non-random joint distributions
of ceiling height, materials, lighting, acoustics, spatial proportions,
olfaction, biophilic elements, and thermal strategy. These regularities
constrain which CMR predictions are ecologically valid, and deviations
from prototypical profiles represent high-informativeness test conditions.

Structure:
    SpaceType       — a canonical room type (library, hospital room, studio, etc.)
    FeatureDomain   — a dimension of architectural specification (lighting, acoustics, etc.)
    FeatureProfile  — the conditional distribution of features within a space type
    ConditionalEdge — P(feature_B | feature_A, space_type) for cross-domain dependencies

Grounded in:
    - Neufert, Architects' Data (4th ed.)
    - WELL Building Standard v2 (IWBI, 2020)
    - ASHRAE 55-2023 (thermal), ASHRAE 90.1 (energy)
    - EN 12464-1 (lighting), ANSI S12.60 (classroom acoustics)
    - Bitner (1992), servicescape theory
    - Mehrabian & Russell (1974), PAD model

Author: David Kirsh & Claude Opus 4.6
Date:   2026-02-24
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import defaultdict
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# SPACE TYPES — Canonical interior typologies
# ═══════════════════════════════════════════════════════════════

@dataclass
class FeatureRange:
    """A range or distribution for a single architectural feature."""
    feature: str
    typical_value: str          # descriptive
    min_val: float = 0.0
    max_val: float = 0.0
    unit: str = ""
    probability: float = 0.9   # P(feature in this range | space_type)
    source: str = ""

@dataclass
class SpaceType:
    """A canonical interior space type with full architectural profile."""
    space_id: str
    name: str
    prototypical_activities: list = field(default_factory=list)
    description: str = ""

    # Spatial envelope
    ceiling_height_m: tuple = (2.7, 3.0)          # (min, max) typical
    floor_area_per_person_m2: tuple = (2.0, 5.0)
    aspect_ratio: tuple = (1.0, 1.5)              # length:width
    window_to_wall_ratio: tuple = (0.2, 0.4)

    # Materials
    floor_materials: dict = field(default_factory=dict)    # {material: probability}
    wall_materials: dict = field(default_factory=dict)
    ceiling_materials: dict = field(default_factory=dict)
    dominant_material_warmth: str = "mixed"  # warm, cool, mixed

    # Lighting
    illuminance_lux: tuple = (300, 500)
    cct_kelvin: tuple = (3500, 4500)
    daylight_fraction: float = 0.3
    glare_control: str = "moderate"
    lighting_layers: int = 2                       # 1=ambient only, 2=+task, 3=+accent

    # Acoustics
    rt60_seconds: tuple = (0.4, 0.8)
    background_noise_dB: tuple = (35, 45)
    speech_intelligibility_target: float = 0.5     # 0=none, 1=full
    acoustic_treatment_level: str = "moderate"     # minimal, moderate, high

    # Thermal
    temperature_C: tuple = (20, 23)
    humidity_pct: tuple = (40, 60)
    air_changes_per_hour: float = 4.0
    personal_thermal_control: bool = False

    # Olfactory
    olfactory_character: str = "neutral"
    scent_sources: dict = field(default_factory=dict)  # {source: probability}
    voc_sensitivity: str = "moderate"              # low, moderate, high

    # Biophilic
    biophilic_elements: dict = field(default_factory=dict)  # {element: probability}
    nature_view_probability: float = 0.3
    fractal_content: str = "low"                   # low, moderate, high

    # Social
    social_density: str = "moderate"               # solitary, low, moderate, high
    privacy_level: str = "moderate"                # open, low, moderate, high
    interaction_mode: str = "mixed"                # solitary, dyadic, small_group, large_group, mixed

    # Affective target (Mehrabian & Russell PAD)
    pad_pleasure: float = 0.5
    pad_arousal: float = 0.5
    pad_dominance: float = 0.5


# ═══════════════════════════════════════════════════════════════
# CANONICAL SPACE TYPES — 16 typologies with full profiles
# ═══════════════════════════════════════════════════════════════

SPACE_TYPES = {}

# ── 1. LIBRARY READING ROOM ──────────────────────────────────

SPACE_TYPES["library_reading_room"] = SpaceType(
    space_id="library_reading_room",
    name="Library Reading Room",
    prototypical_activities=["deep_reading", "focused_study", "quiet_contemplation"],
    description="Traditional reading room with high ceilings, natural materials, and controlled acoustics",

    ceiling_height_m=(3.5, 5.0),
    floor_area_per_person_m2=(2.3, 3.3),
    aspect_ratio=(1.2, 2.0),
    window_to_wall_ratio=(0.25, 0.40),

    floor_materials={"carpet": 0.60, "sealed_hardwood": 0.25, "stone": 0.10, "vinyl": 0.05},
    wall_materials={"wood_paneling": 0.40, "painted_plaster": 0.35, "exposed_brick": 0.15, "fabric_panel": 0.10},
    ceiling_materials={"acoustic_tile": 0.45, "coffered_wood": 0.30, "painted_plaster": 0.20, "exposed_beam": 0.05},
    dominant_material_warmth="warm",

    illuminance_lux=(300, 500),
    cct_kelvin=(2700, 3500),
    daylight_fraction=0.40,
    glare_control="high",
    lighting_layers=3,

    rt60_seconds=(0.5, 0.8),
    background_noise_dB=(25, 35),
    speech_intelligibility_target=0.2,
    acoustic_treatment_level="high",

    temperature_C=(21, 23),
    humidity_pct=(40, 55),
    air_changes_per_hour=3.0,
    personal_thermal_control=False,

    olfactory_character="paper_and_wood",
    scent_sources={"book_paper": 0.85, "wood_polish": 0.50, "leather": 0.30, "dust": 0.40},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.45, "natural_wood_surfaces": 0.80, "nature_view": 0.50, "water_feature": 0.05},
    nature_view_probability=0.50,
    fractal_content="moderate",

    social_density="low",
    privacy_level="moderate",
    interaction_mode="solitary",

    pad_pleasure=0.6,
    pad_arousal=0.2,
    pad_dominance=0.6,
)

# ── 2. OPEN-PLAN OFFICE ──────────────────────────────────────

SPACE_TYPES["open_plan_office"] = SpaceType(
    space_id="open_plan_office",
    name="Open-Plan Office",
    prototypical_activities=["focused_computer_work", "collaborative_work", "phone_calls"],
    description="Modern open-plan workspace with acoustic challenges and high visual exposure",

    ceiling_height_m=(2.7, 3.3),
    floor_area_per_person_m2=(4.5, 7.0),
    aspect_ratio=(1.2, 2.5),
    window_to_wall_ratio=(0.30, 0.45),

    floor_materials={"carpet_tile": 0.55, "polished_concrete": 0.20, "vinyl_plank": 0.15, "raised_access": 0.10},
    wall_materials={"glass_partition": 0.40, "painted_drywall": 0.30, "fabric_panel": 0.20, "whiteboard_surface": 0.10},
    ceiling_materials={"acoustic_tile": 0.65, "exposed_ductwork": 0.20, "acoustic_baffle": 0.10, "painted_slab": 0.05},
    dominant_material_warmth="cool",

    illuminance_lux=(300, 500),
    cct_kelvin=(4000, 5000),
    daylight_fraction=0.35,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.5, 0.7),
    background_noise_dB=(45, 55),
    speech_intelligibility_target=0.7,
    acoustic_treatment_level="moderate",

    temperature_C=(21, 23),
    humidity_pct=(40, 55),
    air_changes_per_hour=5.0,
    personal_thermal_control=False,

    olfactory_character="neutral_synthetic",
    scent_sources={"hvac_conditioned_air": 0.90, "carpet_offgas": 0.40, "coffee": 0.60, "cleaning_products": 0.30},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.55, "natural_wood_surfaces": 0.25, "nature_view": 0.40, "green_wall": 0.10},
    nature_view_probability=0.40,
    fractal_content="low",

    social_density="high",
    privacy_level="low",
    interaction_mode="mixed",

    pad_pleasure=0.4,
    pad_arousal=0.6,
    pad_dominance=0.3,
)

# ── 3. PRIVATE OFFICE ────────────────────────────────────────

SPACE_TYPES["private_office"] = SpaceType(
    space_id="private_office",
    name="Private Office",
    prototypical_activities=["focused_computer_work", "confidential_meetings", "phone_calls"],
    description="Enclosed individual office with speech privacy and personal control",

    ceiling_height_m=(2.7, 3.0),
    floor_area_per_person_m2=(9.0, 14.0),
    aspect_ratio=(1.0, 1.5),
    window_to_wall_ratio=(0.25, 0.40),

    floor_materials={"carpet": 0.50, "hardwood": 0.25, "laminate": 0.15, "vinyl": 0.10},
    wall_materials={"painted_drywall": 0.55, "wood_paneling": 0.25, "glass_partition": 0.15, "fabric_panel": 0.05},
    ceiling_materials={"acoustic_tile": 0.70, "painted_drywall": 0.20, "coffered_wood": 0.10},
    dominant_material_warmth="mixed",

    illuminance_lux=(300, 500),
    cct_kelvin=(3500, 4500),
    daylight_fraction=0.35,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.3, 0.5),
    background_noise_dB=(35, 42),
    speech_intelligibility_target=0.9,
    acoustic_treatment_level="high",

    temperature_C=(21, 23),
    humidity_pct=(40, 55),
    air_changes_per_hour=4.0,
    personal_thermal_control=True,

    olfactory_character="neutral",
    scent_sources={"hvac_conditioned_air": 0.85, "wood_furniture": 0.35, "personal_items": 0.40},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.50, "natural_wood_surfaces": 0.45, "nature_view": 0.55, "water_feature": 0.02},
    nature_view_probability=0.55,
    fractal_content="low",

    social_density="solitary",
    privacy_level="high",
    interaction_mode="solitary",

    pad_pleasure=0.5,
    pad_arousal=0.4,
    pad_dominance=0.7,
)

# ── 4. HOSPITAL PATIENT ROOM ─────────────────────────────────

SPACE_TYPES["hospital_patient_room"] = SpaceType(
    space_id="hospital_patient_room",
    name="Hospital Patient Room",
    prototypical_activities=["rest_recovery", "medical_examination", "family_visits"],
    description="Clinical environment balancing medical function with restorative design",

    ceiling_height_m=(2.7, 3.0),
    floor_area_per_person_m2=(11.0, 13.0),
    aspect_ratio=(1.2, 1.6),
    window_to_wall_ratio=(0.20, 0.35),

    floor_materials={"vinyl_sheet": 0.55, "linoleum": 0.25, "epoxy": 0.15, "rubber": 0.05},
    wall_materials={"painted_drywall": 0.60, "vinyl_wallcovering": 0.25, "antimicrobial_panel": 0.10, "wood_accent": 0.05},
    ceiling_materials={"acoustic_tile": 0.75, "painted_gypsum": 0.20, "metal_panel": 0.05},
    dominant_material_warmth="cool",

    illuminance_lux=(100, 300),
    cct_kelvin=(2700, 4000),
    daylight_fraction=0.30,
    glare_control="high",
    lighting_layers=3,

    rt60_seconds=(0.4, 0.6),
    background_noise_dB=(35, 45),
    speech_intelligibility_target=0.8,
    acoustic_treatment_level="moderate",

    temperature_C=(21, 24),
    humidity_pct=(40, 60),
    air_changes_per_hour=6.0,
    personal_thermal_control=True,

    olfactory_character="clinical",
    scent_sources={"disinfectant": 0.80, "hvac_filtered": 0.90, "medical_supplies": 0.50, "food_service": 0.30},
    voc_sensitivity="high",

    biophilic_elements={"indoor_plants": 0.15, "natural_wood_surfaces": 0.10, "nature_view": 0.55, "nature_artwork": 0.45},
    nature_view_probability=0.55,
    fractal_content="low",

    social_density="low",
    privacy_level="moderate",
    interaction_mode="dyadic",

    pad_pleasure=0.3,
    pad_arousal=0.3,
    pad_dominance=0.2,
)

# ── 5. CAFE / COFFEE SHOP ────────────────────────────────────

SPACE_TYPES["cafe"] = SpaceType(
    space_id="cafe",
    name="Café / Coffee Shop",
    prototypical_activities=["creative_brainstorming", "casual_socializing", "light_work", "people_watching"],
    description="Third-place social environment with layered sensory experience",

    ceiling_height_m=(2.7, 4.0),
    floor_area_per_person_m2=(1.4, 2.0),
    aspect_ratio=(1.0, 2.0),
    window_to_wall_ratio=(0.35, 0.60),

    floor_materials={"tile": 0.35, "polished_concrete": 0.30, "hardwood": 0.25, "vinyl": 0.10},
    wall_materials={"exposed_brick": 0.35, "painted_plaster": 0.30, "reclaimed_wood": 0.20, "chalkboard_paint": 0.10},
    ceiling_materials={"exposed_ductwork": 0.40, "pressed_tin": 0.20, "painted_plaster": 0.25, "wood_beam": 0.15},
    dominant_material_warmth="warm",

    illuminance_lux=(100, 300),
    cct_kelvin=(2700, 3500),
    daylight_fraction=0.45,
    glare_control="low",
    lighting_layers=3,

    rt60_seconds=(0.5, 0.9),
    background_noise_dB=(55, 70),
    speech_intelligibility_target=0.4,
    acoustic_treatment_level="minimal",

    temperature_C=(20, 23),
    humidity_pct=(35, 55),
    air_changes_per_hour=5.0,
    personal_thermal_control=False,

    olfactory_character="coffee_dominant",
    scent_sources={"coffee_roast": 0.95, "baked_goods": 0.70, "milk_steam": 0.60, "wood_furniture": 0.30},
    voc_sensitivity="low",

    biophilic_elements={"indoor_plants": 0.65, "natural_wood_surfaces": 0.70, "nature_view": 0.35, "natural_light": 0.60},
    nature_view_probability=0.35,
    fractal_content="moderate",

    social_density="high",
    privacy_level="low",
    interaction_mode="mixed",

    pad_pleasure=0.7,
    pad_arousal=0.6,
    pad_dominance=0.4,
)

# ── 6. ART STUDIO ────────────────────────────────────────────

SPACE_TYPES["art_studio"] = SpaceType(
    space_id="art_studio",
    name="Art Studio",
    prototypical_activities=["painting_drawing", "sculpture", "creative_work", "visual_assessment"],
    description="Maker space optimized for color accuracy, large-scale work, and creative flow",

    ceiling_height_m=(3.0, 4.5),
    floor_area_per_person_m2=(14.0, 28.0),
    aspect_ratio=(1.0, 1.8),
    window_to_wall_ratio=(0.35, 0.55),

    floor_materials={"sealed_concrete": 0.50, "epoxy": 0.25, "hardwood_paint_splattered": 0.15, "vinyl": 0.10},
    wall_materials={"white_painted_plaster": 0.55, "exposed_brick": 0.20, "pegboard": 0.15, "raw_concrete": 0.10},
    ceiling_materials={"exposed_structure": 0.50, "painted_white": 0.30, "skylight": 0.15, "industrial_grid": 0.05},
    dominant_material_warmth="cool",

    illuminance_lux=(500, 750),
    cct_kelvin=(5000, 6000),
    daylight_fraction=0.55,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.4, 0.7),
    background_noise_dB=(30, 45),
    speech_intelligibility_target=0.5,
    acoustic_treatment_level="minimal",

    temperature_C=(18, 22),
    humidity_pct=(40, 55),
    air_changes_per_hour=6.0,
    personal_thermal_control=False,

    olfactory_character="material_rich",
    scent_sources={"paint_solvents": 0.65, "linseed_oil": 0.40, "turpentine": 0.35, "clay_plaster": 0.25, "wood_sawdust": 0.20},
    voc_sensitivity="low",

    biophilic_elements={"large_windows": 0.70, "natural_light": 0.80, "nature_view": 0.35, "indoor_plants": 0.30},
    nature_view_probability=0.35,
    fractal_content="moderate",

    social_density="solitary",
    privacy_level="moderate",
    interaction_mode="solitary",

    pad_pleasure=0.6,
    pad_arousal=0.5,
    pad_dominance=0.8,
)

# ── 7. SPA / MEDITATION ROOM ─────────────────────────────────

SPACE_TYPES["spa_meditation"] = SpaceType(
    space_id="spa_meditation",
    name="Spa / Meditation Room",
    prototypical_activities=["meditation_quiet_rest", "massage", "contemplation", "body_awareness"],
    description="Restorative cocoon emphasizing parasympathetic activation and sensory gentleness",

    ceiling_height_m=(2.4, 3.0),
    floor_area_per_person_m2=(8.0, 13.0),
    aspect_ratio=(1.0, 1.3),
    window_to_wall_ratio=(0.05, 0.20),

    floor_materials={"natural_stone": 0.35, "wood": 0.30, "bamboo": 0.20, "heated_tile": 0.15},
    wall_materials={"natural_stone": 0.30, "wood_panel": 0.35, "plaster": 0.20, "fabric_panel": 0.15},
    ceiling_materials={"wood_slat": 0.35, "fabric_drape": 0.25, "plaster_cove": 0.25, "bamboo": 0.15},
    dominant_material_warmth="warm",

    illuminance_lux=(10, 50),
    cct_kelvin=(2000, 2700),
    daylight_fraction=0.10,
    glare_control="high",
    lighting_layers=3,

    rt60_seconds=(0.3, 0.5),
    background_noise_dB=(20, 30),
    speech_intelligibility_target=0.1,
    acoustic_treatment_level="high",

    temperature_C=(22, 25),
    humidity_pct=(45, 65),
    air_changes_per_hour=4.0,
    personal_thermal_control=True,

    olfactory_character="essential_oil",
    scent_sources={"lavender": 0.70, "eucalyptus": 0.50, "sandalwood": 0.40, "cedar": 0.35, "chamomile": 0.25, "water_mineral": 0.30},
    voc_sensitivity="high",

    biophilic_elements={"water_feature": 0.65, "indoor_plants": 0.60, "natural_stone": 0.70, "natural_wood": 0.75, "moss_wall": 0.15},
    nature_view_probability=0.20,
    fractal_content="high",

    social_density="solitary",
    privacy_level="high",
    interaction_mode="solitary",

    pad_pleasure=0.8,
    pad_arousal=0.1,
    pad_dominance=0.5,
)

# ── 8. CLASSROOM ─────────────────────────────────────────────

SPACE_TYPES["classroom"] = SpaceType(
    space_id="classroom",
    name="Classroom / Lecture Hall",
    prototypical_activities=["classroom_lecture", "note_taking", "group_discussion", "presentation"],
    description="Instructional space optimized for speech intelligibility and visual attention",

    ceiling_height_m=(2.7, 3.7),
    floor_area_per_person_m2=(2.3, 2.8),
    aspect_ratio=(1.0, 1.5),
    window_to_wall_ratio=(0.20, 0.35),

    floor_materials={"vinyl_composition_tile": 0.40, "carpet": 0.30, "polished_concrete": 0.20, "rubber": 0.10},
    wall_materials={"painted_drywall": 0.50, "acoustic_panel": 0.25, "whiteboard_surface": 0.15, "fabric_panel": 0.10},
    ceiling_materials={"acoustic_tile": 0.70, "acoustic_panel": 0.20, "painted_gypsum": 0.10},
    dominant_material_warmth="cool",

    illuminance_lux=(300, 500),
    cct_kelvin=(4000, 5000),
    daylight_fraction=0.30,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.4, 0.6),
    background_noise_dB=(30, 40),
    speech_intelligibility_target=0.95,
    acoustic_treatment_level="high",

    temperature_C=(21, 23),
    humidity_pct=(40, 55),
    air_changes_per_hour=5.0,
    personal_thermal_control=False,

    olfactory_character="neutral",
    scent_sources={"hvac_conditioned": 0.85, "marker_whiteboard": 0.40, "cleaning": 0.25},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.20, "nature_view": 0.40, "natural_wood_trim": 0.25},
    nature_view_probability=0.40,
    fractal_content="low",

    social_density="high",
    privacy_level="low",
    interaction_mode="large_group",

    pad_pleasure=0.4,
    pad_arousal=0.5,
    pad_dominance=0.3,
)

# ── 9. MUSEUM GALLERY ────────────────────────────────────────

SPACE_TYPES["museum_gallery"] = SpaceType(
    space_id="museum_gallery",
    name="Museum / Gallery",
    prototypical_activities=["aesthetic_contemplation", "visual_assessment", "slow_walking", "cultural_engagement"],
    description="Contemplative space with controlled lighting and minimal distraction",

    ceiling_height_m=(3.5, 6.0),
    floor_area_per_person_m2=(2.0, 3.0),
    aspect_ratio=(1.0, 2.5),
    window_to_wall_ratio=(0.0, 0.15),

    floor_materials={"polished_concrete": 0.40, "natural_stone": 0.30, "hardwood": 0.20, "terrazzo": 0.10},
    wall_materials={"white_plaster": 0.60, "painted_drywall": 0.25, "raw_concrete": 0.10, "fabric_panel": 0.05},
    ceiling_materials={"painted_white": 0.45, "coffered": 0.20, "skylight_filtered": 0.20, "track_grid": 0.15},
    dominant_material_warmth="cool",

    illuminance_lux=(50, 300),
    cct_kelvin=(3000, 4000),
    daylight_fraction=0.15,
    glare_control="high",
    lighting_layers=3,

    rt60_seconds=(0.6, 1.2),
    background_noise_dB=(30, 40),
    speech_intelligibility_target=0.4,
    acoustic_treatment_level="moderate",

    temperature_C=(19, 21),
    humidity_pct=(45, 55),
    air_changes_per_hour=4.0,
    personal_thermal_control=False,

    olfactory_character="neutral",
    scent_sources={"climate_controlled_air": 0.90, "wood_floor_finish": 0.20, "stone": 0.15},
    voc_sensitivity="high",

    biophilic_elements={"natural_stone": 0.40, "natural_light_filtered": 0.30, "indoor_plants": 0.10, "water_feature": 0.08},
    nature_view_probability=0.15,
    fractal_content="moderate",

    social_density="moderate",
    privacy_level="low",
    interaction_mode="mixed",

    pad_pleasure=0.6,
    pad_arousal=0.3,
    pad_dominance=0.5,
)

# ── 10. RESTAURANT (FINE DINING) ─────────────────────────────

SPACE_TYPES["fine_dining"] = SpaceType(
    space_id="fine_dining",
    name="Fine Dining Restaurant",
    prototypical_activities=["formal_dining", "intimate_conversation", "sensory_appreciation"],
    description="Multi-sensory environment designed for gustatory pleasure and social intimacy",

    ceiling_height_m=(2.7, 4.0),
    floor_area_per_person_m2=(1.4, 2.0),
    aspect_ratio=(1.0, 2.0),
    window_to_wall_ratio=(0.15, 0.35),

    floor_materials={"hardwood": 0.40, "stone": 0.25, "tile": 0.20, "carpet": 0.15},
    wall_materials={"fabric_upholstery": 0.30, "wood_paneling": 0.30, "plaster": 0.25, "exposed_brick": 0.15},
    ceiling_materials={"plaster_molding": 0.35, "wood_coffered": 0.25, "fabric_drape": 0.20, "painted": 0.20},
    dominant_material_warmth="warm",

    illuminance_lux=(30, 100),
    cct_kelvin=(2200, 3000),
    daylight_fraction=0.10,
    glare_control="high",
    lighting_layers=3,

    rt60_seconds=(0.5, 0.8),
    background_noise_dB=(50, 65),
    speech_intelligibility_target=0.6,
    acoustic_treatment_level="moderate",

    temperature_C=(20, 22),
    humidity_pct=(40, 55),
    air_changes_per_hour=5.0,
    personal_thermal_control=False,

    olfactory_character="cuisine_dominant",
    scent_sources={"food_aromas": 0.95, "wine": 0.60, "candle_wax": 0.40, "fresh_flowers": 0.35, "bread": 0.55},
    voc_sensitivity="low",

    biophilic_elements={"fresh_flowers": 0.70, "natural_wood": 0.65, "candle_flame": 0.60, "natural_stone": 0.30},
    nature_view_probability=0.20,
    fractal_content="moderate",

    social_density="moderate",
    privacy_level="moderate",
    interaction_mode="dyadic",

    pad_pleasure=0.8,
    pad_arousal=0.4,
    pad_dominance=0.5,
)

# ── 11. RESIDENTIAL BEDROOM ──────────────────────────────────

SPACE_TYPES["residential_bedroom"] = SpaceType(
    space_id="residential_bedroom",
    name="Residential Bedroom",
    prototypical_activities=["sleep", "rest", "reading_in_bed", "dressing"],
    description="Personal retreat optimized for sleep onset and circadian rhythm support",

    ceiling_height_m=(2.4, 2.7),
    floor_area_per_person_m2=(10.0, 14.0),
    aspect_ratio=(1.0, 1.5),
    window_to_wall_ratio=(0.15, 0.30),

    floor_materials={"carpet": 0.45, "hardwood": 0.35, "laminate": 0.15, "rug_over_hard": 0.05},
    wall_materials={"painted_drywall": 0.60, "wallpaper": 0.20, "fabric_panel": 0.10, "wood_accent": 0.10},
    ceiling_materials={"painted_drywall": 0.85, "textured_plaster": 0.10, "wood_beam": 0.05},
    dominant_material_warmth="warm",

    illuminance_lux=(50, 200),
    cct_kelvin=(2200, 3000),
    daylight_fraction=0.30,
    glare_control="high",
    lighting_layers=2,

    rt60_seconds=(0.3, 0.5),
    background_noise_dB=(20, 30),
    speech_intelligibility_target=0.0,
    acoustic_treatment_level="moderate",

    temperature_C=(16, 19),
    humidity_pct=(40, 55),
    air_changes_per_hour=2.0,
    personal_thermal_control=True,

    olfactory_character="personal",
    scent_sources={"laundered_linen": 0.85, "personal_fragrance": 0.40, "wood_furniture": 0.30, "candle": 0.20},
    voc_sensitivity="high",

    biophilic_elements={"indoor_plants": 0.35, "natural_wood_furniture": 0.55, "nature_view": 0.40, "natural_textiles": 0.65},
    nature_view_probability=0.40,
    fractal_content="low",

    social_density="solitary",
    privacy_level="high",
    interaction_mode="solitary",

    pad_pleasure=0.7,
    pad_arousal=0.1,
    pad_dominance=0.7,
)

# ── 12. RESIDENTIAL LIVING ROOM ──────────────────────────────

SPACE_TYPES["residential_living"] = SpaceType(
    space_id="residential_living",
    name="Residential Living Room",
    prototypical_activities=["casual_socializing", "tv_watching", "reading", "family_time"],
    description="Multi-function family space with adaptable lighting and mixed-use zones",

    ceiling_height_m=(2.4, 3.0),
    floor_area_per_person_m2=(4.0, 8.0),
    aspect_ratio=(1.0, 1.6),
    window_to_wall_ratio=(0.25, 0.40),

    floor_materials={"hardwood": 0.40, "carpet": 0.25, "laminate": 0.20, "tile": 0.15},
    wall_materials={"painted_drywall": 0.55, "wallpaper": 0.15, "wood_accent": 0.15, "exposed_brick": 0.15},
    ceiling_materials={"painted_drywall": 0.75, "wood_beam": 0.15, "textured_plaster": 0.10},
    dominant_material_warmth="warm",

    illuminance_lux=(100, 400),
    cct_kelvin=(2700, 3500),
    daylight_fraction=0.40,
    glare_control="low",
    lighting_layers=3,

    rt60_seconds=(0.3, 0.6),
    background_noise_dB=(30, 45),
    speech_intelligibility_target=0.7,
    acoustic_treatment_level="minimal",

    temperature_C=(20, 22),
    humidity_pct=(40, 55),
    air_changes_per_hour=3.0,
    personal_thermal_control=False,

    olfactory_character="domestic",
    scent_sources={"cooking_from_kitchen": 0.60, "wood_furniture": 0.40, "candle": 0.35, "fresh_air": 0.30, "pet": 0.25},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.55, "natural_wood_furniture": 0.60, "nature_view": 0.50, "fireplace": 0.25},
    nature_view_probability=0.50,
    fractal_content="moderate",

    social_density="moderate",
    privacy_level="moderate",
    interaction_mode="small_group",

    pad_pleasure=0.7,
    pad_arousal=0.4,
    pad_dominance=0.6,
)

# ── 13. HEALING GARDEN / OUTDOOR THERAPEUTIC ──────────────────

SPACE_TYPES["healing_garden"] = SpaceType(
    space_id="healing_garden",
    name="Healing Garden / Therapeutic Outdoor Space",
    prototypical_activities=["nature_walk_garden", "meditation_quiet_rest", "gentle_exercise", "social_strolling"],
    description="Designed outdoor environment with curated planting, water, and path structure",

    ceiling_height_m=(0.0, 0.0),  # open sky
    floor_area_per_person_m2=(15.0, 40.0),
    aspect_ratio=(1.0, 3.0),
    window_to_wall_ratio=(1.0, 1.0),  # fully open

    floor_materials={"gravel_path": 0.35, "stone_paver": 0.30, "grass": 0.20, "wood_boardwalk": 0.10, "compacted_earth": 0.05},
    wall_materials={"hedge": 0.35, "stone_wall": 0.25, "trellis_vine": 0.25, "bamboo_screen": 0.15},
    ceiling_materials={"open_sky": 0.60, "tree_canopy": 0.30, "pergola": 0.10},
    dominant_material_warmth="warm",

    illuminance_lux=(2000, 100000),  # daylight
    cct_kelvin=(5500, 6500),
    daylight_fraction=1.0,
    glare_control="natural",
    lighting_layers=1,

    rt60_seconds=(0.0, 0.0),  # open air
    background_noise_dB=(35, 55),
    speech_intelligibility_target=0.5,
    acoustic_treatment_level="minimal",

    temperature_C=(15, 28),  # outdoor range
    humidity_pct=(30, 70),
    air_changes_per_hour=999.0,  # fully ventilated
    personal_thermal_control=False,

    olfactory_character="botanical",
    scent_sources={"flowering_plants": 0.80, "cut_grass": 0.55, "wet_earth_petrichor": 0.45, "pine_resin": 0.30, "water_mineral": 0.25},
    voc_sensitivity="low",

    biophilic_elements={"diverse_planting": 0.95, "water_feature": 0.70, "birdsong": 0.85, "natural_stone": 0.60, "tree_canopy": 0.75},
    nature_view_probability=1.0,
    fractal_content="high",

    social_density="low",
    privacy_level="moderate",
    interaction_mode="mixed",

    pad_pleasure=0.8,
    pad_arousal=0.2,
    pad_dominance=0.6,
)

# ── 14. RETAIL STORE ──────────────────────────────────────────

SPACE_TYPES["retail_store"] = SpaceType(
    space_id="retail_store",
    name="Retail Store",
    prototypical_activities=["browsing", "product_evaluation", "purchase_decision", "social_shopping"],
    description="Commercial environment designed to attract attention and sustain exploration",

    ceiling_height_m=(3.0, 5.0),
    floor_area_per_person_m2=(1.4, 2.0),
    aspect_ratio=(1.0, 3.0),
    window_to_wall_ratio=(0.40, 0.70),

    floor_materials={"polished_concrete": 0.30, "tile": 0.30, "hardwood": 0.20, "vinyl": 0.20},
    wall_materials={"painted_drywall": 0.35, "glass": 0.25, "wood_panel": 0.20, "exposed_brick": 0.20},
    ceiling_materials={"exposed_structure": 0.40, "painted_drywall": 0.30, "acoustic_tile": 0.15, "track_lighting_grid": 0.15},
    dominant_material_warmth="mixed",

    illuminance_lux=(300, 1000),
    cct_kelvin=(3000, 4000),
    daylight_fraction=0.30,
    glare_control="low",
    lighting_layers=3,

    rt60_seconds=(0.5, 1.0),
    background_noise_dB=(55, 70),
    speech_intelligibility_target=0.5,
    acoustic_treatment_level="minimal",

    temperature_C=(20, 22),
    humidity_pct=(40, 55),
    air_changes_per_hour=5.0,
    personal_thermal_control=False,

    olfactory_character="branded",
    scent_sources={"brand_fragrance": 0.50, "new_product": 0.40, "hvac": 0.80, "coffee_area": 0.25},
    voc_sensitivity="low",

    biophilic_elements={"indoor_plants": 0.35, "natural_materials": 0.40, "natural_light": 0.45, "water_feature": 0.05},
    nature_view_probability=0.30,
    fractal_content="low",

    social_density="high",
    privacy_level="low",
    interaction_mode="mixed",

    pad_pleasure=0.6,
    pad_arousal=0.7,
    pad_dominance=0.4,
)

# ── 15. CONFERENCE / MEETING ROOM ─────────────────────────────

SPACE_TYPES["conference_room"] = SpaceType(
    space_id="conference_room",
    name="Conference / Meeting Room",
    prototypical_activities=["group_discussion", "presentation", "brainstorming", "decision_making"],
    description="Enclosed group space with high speech intelligibility and flexible configuration",

    ceiling_height_m=(2.7, 3.3),
    floor_area_per_person_m2=(2.5, 4.0),
    aspect_ratio=(1.0, 2.0),
    window_to_wall_ratio=(0.15, 0.35),

    floor_materials={"carpet": 0.55, "carpet_tile": 0.25, "hardwood": 0.10, "vinyl": 0.10},
    wall_materials={"painted_drywall": 0.40, "glass_partition": 0.25, "whiteboard_surface": 0.20, "acoustic_panel": 0.15},
    ceiling_materials={"acoustic_tile": 0.70, "painted_gypsum": 0.20, "acoustic_cloud": 0.10},
    dominant_material_warmth="cool",

    illuminance_lux=(300, 500),
    cct_kelvin=(3500, 4500),
    daylight_fraction=0.25,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.4, 0.6),
    background_noise_dB=(30, 40),
    speech_intelligibility_target=0.95,
    acoustic_treatment_level="high",

    temperature_C=(21, 23),
    humidity_pct=(40, 55),
    air_changes_per_hour=6.0,
    personal_thermal_control=False,

    olfactory_character="neutral",
    scent_sources={"hvac": 0.90, "marker": 0.30, "coffee_brought_in": 0.50},
    voc_sensitivity="moderate",

    biophilic_elements={"indoor_plants": 0.30, "nature_view": 0.35, "wood_table": 0.45},
    nature_view_probability=0.35,
    fractal_content="low",

    social_density="moderate",
    privacy_level="high",
    interaction_mode="small_group",

    pad_pleasure=0.4,
    pad_arousal=0.5,
    pad_dominance=0.4,
)

# ── 16. WORKSHOP / MAKERSPACE ─────────────────────────────────

SPACE_TYPES["workshop_makerspace"] = SpaceType(
    space_id="workshop_makerspace",
    name="Workshop / Makerspace",
    prototypical_activities=["fabrication", "prototyping", "collaborative_making", "experimentation"],
    description="Tool-rich environment for hands-on creation with robust materials and ventilation",

    ceiling_height_m=(3.0, 5.0),
    floor_area_per_person_m2=(8.0, 15.0),
    aspect_ratio=(1.0, 2.5),
    window_to_wall_ratio=(0.20, 0.35),

    floor_materials={"sealed_concrete": 0.60, "epoxy": 0.25, "rubber_mat": 0.10, "steel_plate": 0.05},
    wall_materials={"painted_cinder_block": 0.35, "pegboard": 0.25, "painted_drywall": 0.20, "metal_panel": 0.20},
    ceiling_materials={"exposed_structure": 0.60, "metal_deck": 0.25, "painted_slab": 0.15},
    dominant_material_warmth="cool",

    illuminance_lux=(500, 1000),
    cct_kelvin=(4500, 5500),
    daylight_fraction=0.25,
    glare_control="moderate",
    lighting_layers=2,

    rt60_seconds=(0.5, 0.8),
    background_noise_dB=(55, 75),
    speech_intelligibility_target=0.6,
    acoustic_treatment_level="minimal",

    temperature_C=(18, 22),
    humidity_pct=(35, 50),
    air_changes_per_hour=8.0,
    personal_thermal_control=False,

    olfactory_character="industrial",
    scent_sources={"sawdust": 0.55, "metal_oil": 0.40, "adhesive": 0.35, "solder_flux": 0.25, "fresh_cut_wood": 0.45},
    voc_sensitivity="low",

    biophilic_elements={"natural_wood_workbench": 0.50, "large_windows": 0.35, "indoor_plants": 0.10},
    nature_view_probability=0.25,
    fractal_content="low",

    social_density="moderate",
    privacy_level="low",
    interaction_mode="small_group",

    pad_pleasure=0.6,
    pad_arousal=0.7,
    pad_dominance=0.7,
)


# ═══════════════════════════════════════════════════════════════
# CROSS-DOMAIN CONDITIONAL PROBABILITIES
# ═══════════════════════════════════════════════════════════════
#
# These encode P(feature_B | feature_A) — the structural dependencies
# between architectural attributes that hold ACROSS space types.
# A room with warm wood paneling is unlikely to have cool fluorescent
# lighting; a room with high ceilings is more likely to have reverberant
# acoustics unless treated. These are design regularities.
#

CROSS_DOMAIN_CONDITIONALS = {
    # ── Material → Lighting ──
    ("warm_wood_surfaces", "warm_cct_below_3500K"):       0.80,
    ("warm_wood_surfaces", "cool_cct_above_4500K"):       0.10,
    ("exposed_concrete", "cool_cct_above_4500K"):         0.55,
    ("exposed_concrete", "warm_cct_below_3500K"):         0.20,
    ("natural_stone_floor", "warm_cct_below_3500K"):      0.60,
    ("fabric_upholstery", "warm_cct_below_3500K"):        0.75,
    ("glass_partition", "cool_cct_above_4500K"):          0.60,
    ("white_plaster_walls", "neutral_cct_3500_4500K"):    0.50,

    # ── Material → Acoustics ──
    ("carpet_floor", "low_background_noise_below_35dB"):  0.55,
    ("carpet_floor", "high_background_noise_above_55dB"): 0.10,
    ("polished_concrete_floor", "high_reverberation"):    0.70,
    ("polished_concrete_floor", "low_reverberation"):     0.15,
    ("fabric_upholstery", "low_reverberation"):           0.65,
    ("acoustic_tile_ceiling", "low_reverberation"):       0.80,
    ("exposed_ductwork_ceiling", "high_background_noise_above_55dB"): 0.55,

    # ── Ceiling height → Acoustics ──
    ("high_ceiling_above_4m", "high_reverberation"):      0.65,
    ("high_ceiling_above_4m", "low_reverberation"):       0.15,
    ("low_ceiling_below_2.7m", "low_reverberation"):      0.60,
    ("high_ceiling_above_4m", "acoustic_treatment_needed"): 0.75,

    # ── Lighting → Thermal ──
    ("high_daylight_fraction_above_50pct", "solar_heat_gain_present"): 0.70,
    ("high_daylight_fraction_above_50pct", "glare_control_needed"):   0.75,
    ("low_artificial_light_below_50lux", "warm_temperature_above_22C"): 0.55,

    # ── Materials → Olfactory ──
    ("natural_wood_surfaces", "wood_scent_present"):      0.65,
    ("carpet_floor", "synthetic_offgas_present"):         0.40,
    ("natural_stone", "mineral_scent"):                   0.30,
    ("exposed_brick", "earthy_scent"):                    0.25,

    # ── Biophilic → Other domains ──
    ("indoor_plants_present", "improved_air_quality"):    0.45,
    ("water_feature_present", "masking_noise_present"):   0.70,
    ("water_feature_present", "humidity_elevated"):       0.40,
    ("nature_view_present", "daylight_present"):          0.80,
    ("tree_canopy_present", "dappled_light"):             0.75,
    ("tree_canopy_present", "birdsong_present"):          0.60,

    # ── Window → Multiple domains ──
    ("large_windows", "daylight_present"):                0.90,
    ("large_windows", "external_noise_ingress"):          0.50,
    ("large_windows", "nature_view_present"):             0.55,
    ("large_windows", "glare_control_needed"):            0.70,
    ("minimal_windows", "artificial_light_dominant"):     0.85,
    ("minimal_windows", "low_external_noise"):            0.65,

    # ── Social density → Acoustics ──
    ("high_social_density", "speech_noise_present"):      0.80,
    ("high_social_density", "high_background_noise_above_55dB"): 0.65,
    ("solitary_occupancy", "quiet_below_30dB"):           0.50,

    # ── Privacy → Materials/Spatial ──
    ("high_privacy", "sound_rated_partitions"):           0.70,
    ("high_privacy", "carpet_floor"):                     0.55,
    ("low_privacy", "glass_partition"):                   0.50,
    ("low_privacy", "open_sightlines"):                   0.75,
}


# ═══════════════════════════════════════════════════════════════
# CONDITIONAL PROBABILITY COMPUTATION
# ═══════════════════════════════════════════════════════════════

def get_feature_profile(space_type_id: str) -> dict:
    """
    Return the full feature profile for a space type as a flat dictionary
    of {feature_tag: probability}.
    """
    st = SPACE_TYPES.get(space_type_id)
    if not st:
        return {}

    profile = {}

    # Materials
    for mat, prob in st.floor_materials.items():
        profile[f"floor:{mat}"] = prob
    for mat, prob in st.wall_materials.items():
        profile[f"wall:{mat}"] = prob
    for mat, prob in st.ceiling_materials.items():
        profile[f"ceiling:{mat}"] = prob

    # Lighting
    profile["lighting:warm_cct"] = 1.0 if st.cct_kelvin[1] <= 3500 else (0.5 if st.cct_kelvin[0] <= 3500 else 0.0)
    profile["lighting:cool_cct"] = 1.0 if st.cct_kelvin[0] >= 4500 else (0.5 if st.cct_kelvin[1] >= 4500 else 0.0)
    profile["lighting:high_illuminance"] = 1.0 if st.illuminance_lux[0] >= 400 else (0.5 if st.illuminance_lux[1] >= 400 else 0.0)
    profile["lighting:dim"] = 1.0 if st.illuminance_lux[1] <= 100 else (0.5 if st.illuminance_lux[0] <= 100 else 0.0)
    profile["lighting:daylight_dominant"] = st.daylight_fraction

    # Acoustics
    profile["acoustic:quiet"] = 1.0 if st.background_noise_dB[1] <= 35 else (0.5 if st.background_noise_dB[0] <= 35 else 0.0)
    profile["acoustic:noisy"] = 1.0 if st.background_noise_dB[0] >= 55 else (0.5 if st.background_noise_dB[1] >= 55 else 0.0)
    profile["acoustic:speech_privacy"] = 1.0 - st.speech_intelligibility_target
    profile["acoustic:reverberant"] = 1.0 if st.rt60_seconds[0] >= 0.8 else (0.5 if st.rt60_seconds[1] >= 0.8 else 0.0)

    # Thermal
    profile["thermal:cool_for_sleep"] = 1.0 if st.temperature_C[1] <= 19 else 0.0
    profile["thermal:warm_for_comfort"] = 1.0 if st.temperature_C[0] >= 22 else (0.5 if st.temperature_C[1] >= 22 else 0.0)
    profile["thermal:personal_control"] = 1.0 if st.personal_thermal_control else 0.0

    # Olfactory
    for source, prob in st.scent_sources.items():
        profile[f"scent:{source}"] = prob

    # Biophilic
    for element, prob in st.biophilic_elements.items():
        profile[f"biophilic:{element}"] = prob
    profile["biophilic:nature_view"] = st.nature_view_probability
    profile["biophilic:fractal_content"] = {"low": 0.2, "moderate": 0.5, "high": 0.8}.get(st.fractal_content, 0.3)

    # Spatial
    profile["spatial:high_ceiling"] = 1.0 if st.ceiling_height_m[0] >= 3.5 else (0.5 if st.ceiling_height_m[1] >= 3.5 else 0.0)
    profile["spatial:low_ceiling"] = 1.0 if st.ceiling_height_m[1] <= 2.7 else 0.0
    profile["spatial:spacious"] = 1.0 if st.floor_area_per_person_m2[0] >= 8.0 else (0.5 if st.floor_area_per_person_m2[1] >= 8.0 else 0.0)

    # Social
    profile["social:solitary"] = 1.0 if st.social_density == "solitary" else 0.0
    profile["social:high_density"] = 1.0 if st.social_density == "high" else 0.0
    profile["social:high_privacy"] = 1.0 if st.privacy_level == "high" else (0.5 if st.privacy_level == "moderate" else 0.0)

    return profile


def compute_feature_conditional(feature_a: str, feature_b: str, space_type_id: str = None) -> dict:
    """
    Compute P(feature_B | feature_A) across all space types, or within a specific space type.

    Returns: {space_type: probability} or single float if space_type specified.
    """
    results = {}

    target_spaces = [space_type_id] if space_type_id else list(SPACE_TYPES.keys())

    for sid in target_spaces:
        profile = get_feature_profile(sid)
        p_a = profile.get(feature_a, 0.0)
        p_b = profile.get(feature_b, 0.0)

        # Simple conditional: P(B|A) ≈ P(A ∩ B) / P(A)
        # For architectural features within a space type, co-occurrence ≈ min(P(A), P(B))
        # when both are characteristic of the space, or product when independent
        if p_a > 0:
            # Check cross-domain conditional table
            cross_key = None
            for (ca, cb), cp in CROSS_DOMAIN_CONDITIONALS.items():
                if ca in feature_a and cb in feature_b:
                    cross_key = cp
                    break
                if ca in feature_b and cb in feature_a:
                    cross_key = cp
                    break

            if cross_key is not None:
                results[sid] = cross_key * p_a
            else:
                # Default: features within a space type are somewhat positively correlated
                results[sid] = min(p_a, p_b) * 0.8 + p_a * p_b * 0.2
        else:
            results[sid] = 0.0

    if space_type_id:
        return results.get(space_type_id, 0.0)
    return results


def find_anomalous_feature_in_space(feature_tag: str, threshold: float = 0.15) -> list:
    """
    Find space types where a given feature is anomalous (probability below threshold).
    These are high-informativeness test conditions.
    """
    anomalous = []
    for sid, st in SPACE_TYPES.items():
        profile = get_feature_profile(sid)
        prob = profile.get(feature_tag, 0.0)
        if 0 < prob <= threshold:
            anomalous.append({
                "space_type": sid,
                "feature": feature_tag,
                "probability": prob,
                "informativeness": f"Testing {feature_tag} in {st.name} is highly informative (P={prob:.2f})",
            })
        elif prob == 0.0:
            # Completely absent — even more informative
            anomalous.append({
                "space_type": sid,
                "feature": feature_tag,
                "probability": 0.0,
                "informativeness": f"Feature {feature_tag} is absent from {st.name} — introducing it would be a maximally informative test",
            })
    anomalous.sort(key=lambda x: x["probability"])
    return anomalous


def compute_space_similarity(space_a: str, space_b: str) -> dict:
    """
    Compute similarity between two space types across all feature domains.
    Returns domain-level similarities and overall score.
    """
    profile_a = get_feature_profile(space_a)
    profile_b = get_feature_profile(space_b)

    all_features = set(profile_a.keys()) | set(profile_b.keys())

    # Group by domain
    domains = defaultdict(list)
    for f in all_features:
        domain = f.split(":")[0]
        val_a = profile_a.get(f, 0.0)
        val_b = profile_b.get(f, 0.0)
        domains[domain].append(1.0 - abs(val_a - val_b))

    domain_sims = {}
    for domain, sims in domains.items():
        domain_sims[domain] = sum(sims) / len(sims) if sims else 0.0

    overall = sum(domain_sims.values()) / len(domain_sims) if domain_sims else 0.0

    return {
        "space_a": space_a,
        "space_b": space_b,
        "overall_similarity": overall,
        "domain_similarities": domain_sims,
    }


def generate_activity_space_matrix() -> dict:
    """
    Generate the full activity → space_type mapping with conditional
    probabilities of each architectural feature given the activity.

    This is the central deliverable: P(arch_feature | activity)
    """
    # First, build activity → space_types mapping
    activity_spaces = defaultdict(list)
    for sid, st in SPACE_TYPES.items():
        for activity in st.prototypical_activities:
            activity_spaces[activity].append(sid)

    # For each activity, compute the expected feature profile
    # (weighted average across space types that support that activity)
    matrix = {}
    for activity, space_ids in activity_spaces.items():
        profiles = [get_feature_profile(sid) for sid in space_ids]
        all_features = set()
        for p in profiles:
            all_features.update(p.keys())

        # Average probability of each feature across supporting spaces
        avg_profile = {}
        for f in all_features:
            vals = [p.get(f, 0.0) for p in profiles]
            avg_profile[f] = sum(vals) / len(vals)

        # Sort by probability descending
        sorted_features = sorted(avg_profile.items(), key=lambda x: -x[1])

        matrix[activity] = {
            "supporting_spaces": space_ids,
            "feature_profile": dict(sorted_features),
            "high_probability_features": [(f, p) for f, p in sorted_features if p >= 0.5],
            "low_probability_features": [(f, p) for f, p in sorted_features if 0 < p <= 0.15],
        }

    return matrix


# ═══════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_typology_report() -> str:
    """Generate a comprehensive report of the architectural typology."""
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 80)
    lines.append("ARCHITECTURAL TYPOLOGY PRIOR MODEL")
    lines.append(f"Generated: {ts}")
    lines.append("=" * 80)
    lines.append("")

    lines.append(f"Space types: {len(SPACE_TYPES)}")
    lines.append(f"Cross-domain conditionals: {len(CROSS_DOMAIN_CONDITIONALS)}")
    lines.append("")

    # ── Space type summaries ──
    lines.append("=" * 80)
    lines.append("SPACE TYPE PROFILES")
    lines.append("=" * 80)
    lines.append("")

    for sid, st in SPACE_TYPES.items():
        lines.append(f"  {st.name} [{sid}]")
        lines.append(f"    Activities:    {', '.join(st.prototypical_activities)}")
        lines.append(f"    Ceiling:       {st.ceiling_height_m[0]}-{st.ceiling_height_m[1]}m")
        lines.append(f"    Lighting:      {st.illuminance_lux[0]}-{st.illuminance_lux[1]} lux, {st.cct_kelvin[0]}-{st.cct_kelvin[1]}K")
        lines.append(f"    Acoustics:     {st.background_noise_dB[0]}-{st.background_noise_dB[1]} dB, RT60 {st.rt60_seconds[0]}-{st.rt60_seconds[1]}s")
        lines.append(f"    Temperature:   {st.temperature_C[0]}-{st.temperature_C[1]}°C")
        lines.append(f"    Materials:     {st.dominant_material_warmth}")
        lines.append(f"    Privacy:       {st.privacy_level} | Social: {st.social_density}")
        lines.append(f"    PAD:           P={st.pad_pleasure:.1f} A={st.pad_arousal:.1f} D={st.pad_dominance:.1f}")

        # Top floor/wall/ceiling materials
        top_floor = max(st.floor_materials.items(), key=lambda x: x[1]) if st.floor_materials else ("none", 0)
        top_wall = max(st.wall_materials.items(), key=lambda x: x[1]) if st.wall_materials else ("none", 0)
        top_ceil = max(st.ceiling_materials.items(), key=lambda x: x[1]) if st.ceiling_materials else ("none", 0)
        lines.append(f"    Dominant:      floor={top_floor[0]}({top_floor[1]:.0%}) wall={top_wall[0]}({top_wall[1]:.0%}) ceil={top_ceil[0]}({top_ceil[1]:.0%})")

        # Biophilic
        top_bio = sorted(st.biophilic_elements.items(), key=lambda x: -x[1])[:3]
        if top_bio:
            bio_str = ", ".join(f"{e}({p:.0%})" for e, p in top_bio)
            lines.append(f"    Biophilic:     {bio_str}")

        # Scent
        top_scent = sorted(st.scent_sources.items(), key=lambda x: -x[1])[:3]
        if top_scent:
            scent_str = ", ".join(f"{s}({p:.0%})" for s, p in top_scent)
            lines.append(f"    Scent:         {scent_str}")

        lines.append("")

    # ── Cross-domain conditionals ──
    lines.append("=" * 80)
    lines.append("CROSS-DOMAIN CONDITIONAL PROBABILITIES")
    lines.append("P(feature_B | feature_A) — design regularities across space types")
    lines.append("=" * 80)
    lines.append("")

    # Group by domain pair
    domain_groups = defaultdict(list)
    for (fa, fb), prob in sorted(CROSS_DOMAIN_CONDITIONALS.items(), key=lambda x: -x[1]):
        # Determine domains
        domain_a = fa.split("_")[0] if "_" in fa else "material"
        domain_b = fb.split("_")[0] if "_" in fb else "material"
        domain_groups[f"{domain_a} → {domain_b}"].append((fa, fb, prob))

    for domain_pair, entries in sorted(domain_groups.items()):
        lines.append(f"  {domain_pair}:")
        for fa, fb, prob in entries:
            marker = "●" if prob >= 0.6 else ("○" if prob >= 0.3 else "·")
            lines.append(f"    {marker} P({fb:45s} | {fa:35s}) = {prob:.2f}")
        lines.append("")

    # ── Activity-space matrix ──
    lines.append("=" * 80)
    lines.append("ACTIVITY → SPACE TYPE → FEATURE PROFILE")
    lines.append("P(architectural_feature | activity)")
    lines.append("=" * 80)
    lines.append("")

    matrix = generate_activity_space_matrix()
    for activity, data in sorted(matrix.items()):
        lines.append(f"  {activity}")
        lines.append(f"    Spaces: {', '.join(data['supporting_spaces'])}")
        high = data["high_probability_features"][:8]
        if high:
            lines.append(f"    HIGH P features:")
            for f, p in high:
                lines.append(f"      {f:50s} {p:.2f}")
        low = data["low_probability_features"][:5]
        if low:
            lines.append(f"    LOW P features (informative to test):")
            for f, p in low:
                lines.append(f"      {f:50s} {p:.2f}")
        lines.append("")

    # ── Space similarity matrix ──
    lines.append("=" * 80)
    lines.append("SPACE TYPE SIMILARITY MATRIX (top pairs)")
    lines.append("=" * 80)
    lines.append("")

    space_ids = list(SPACE_TYPES.keys())
    pairs = []
    for i, sa in enumerate(space_ids):
        for sb in space_ids[i+1:]:
            sim = compute_space_similarity(sa, sb)
            pairs.append(sim)

    pairs.sort(key=lambda x: -x["overall_similarity"])

    lines.append("  Most similar space pairs:")
    for sim in pairs[:10]:
        lines.append(f"    {sim['space_a']:30s} × {sim['space_b']:30s}  sim={sim['overall_similarity']:.3f}")
    lines.append("")
    lines.append("  Most dissimilar space pairs:")
    for sim in pairs[-5:]:
        lines.append(f"    {sim['space_a']:30s} × {sim['space_b']:30s}  sim={sim['overall_similarity']:.3f}")
    lines.append("")

    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Architectural Typology Priors")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument("--json", action="store_true", help="Export as JSON")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--matrix", action="store_true", help="Activity-space matrix only")
    parser.add_argument("--anomalous", type=str, default=None,
        help="Find spaces where a feature is anomalous (e.g., 'biophilic:water_feature')")

    args = parser.parse_args()

    if args.anomalous:
        results = find_anomalous_feature_in_space(args.anomalous)
        for r in results:
            print(f"  {r['space_type']:30s} P={r['probability']:.2f}  {r['informativeness']}")
        return

    if args.matrix:
        matrix = generate_activity_space_matrix()
        print(json.dumps(matrix, indent=2, default=str))
        return

    if args.json:
        data = {
            "timestamp": datetime.now().isoformat(),
            "space_types": {sid: asdict(st) for sid, st in SPACE_TYPES.items()},
            "cross_domain_conditionals": {
                f"{fa}|{fb}": prob for (fa, fb), prob in CROSS_DOMAIN_CONDITIONALS.items()
            },
            "activity_space_matrix": generate_activity_space_matrix(),
        }
        out = json.dumps(data, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(out)
            print(f"JSON written to: {args.output}", file=sys.stderr)
        else:
            print(out)
        return

    report = generate_typology_report()
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
