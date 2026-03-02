"""
stimulus_taxonomy.py — T3 IV-Side Hierarchical Stimulus Taxonomy
================================================================

Multi-faceted taxonomy for architectural/environmental independent variables.
Supports belief generalization by providing subsumption, common-ancestor
computation, and parametric-range encoding.

Design principles (from expanded expert panel):
  1. Every stimulus has a DOMAIN (what), a DELIVERY MODE (how perceived),
     a SENSORY MODALITY (which sense), and optional CULTURE facet.
  2. Numerical stimuli encode parametric ranges: 9' ceiling → spatial.height
  3. Person-state manipulations (e.g., "increase cognitive load") are first-class
  4. Generalization requires mechanism identity, not just taxonomic proximity

Informed by:
  - Rosch (1975) prototype theory — natural categories have graded membership
  - Tenenbaum & Griffiths (2001) — Bayesian generalization from examples
  - Lake et al. (2015) — compositionality in concept learning
  - Miller (1995) WordNet — hierarchical lexical organization
  - Biederman (1987) RBC — recognition-by-components → structural primitives

ADR: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Facet Enums
# ══════════════════════════════════════════════════════════════════

class DeliveryMode(Enum):
    """How the stimulus is presented/experienced."""
    REAL = "real"                  # Full 3D physical environment
    VR = "vr"                      # Virtual reality (immersive 3D)
    AR = "ar"                      # Augmented reality overlay
    PHOTOGRAPH = "photograph"      # Still image
    VIDEO = "video"                # Moving image
    PLAN_DRAWING = "plan_drawing"  # Architectural plan/elevation
    RENDER_3D = "render_3d"        # 3D rendering (non-immersive)
    SKETCH = "sketch"              # Hand-drawn representation
    DESCRIPTION = "description"    # Text/verbal description only
    UNSPECIFIED = "unspecified"


class SensoryModality(Enum):
    """Primary sensory channel engaged by the stimulus."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    OLFACTORY = "olfactory"
    HAPTIC = "haptic"
    THERMAL = "thermal"
    GUSTATORY = "gustatory"
    VESTIBULAR = "vestibular"      # Balance, spatial orientation
    MULTISENSORY = "multisensory"
    UNSPECIFIED = "unspecified"


class ManipulationType(Enum):
    """What kind of experimental manipulation."""
    ENVIRONMENTAL = "environmental"    # Physical feature of the space
    PERSON_STATE = "person_state"      # Manipulating the person's state
    TASK = "task"                       # Changing what the person does
    CULTURAL = "cultural"              # Cultural context/group
    TEMPORAL = "temporal"              # Time-based manipulation
    SOCIAL = "social"                  # Social context manipulation


# ══════════════════════════════════════════════════════════════════
# Taxonomy Node
# ══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TaxonomyNode:
    """A single node in the stimulus taxonomy tree."""
    node_id: str                           # e.g., "spatial.height.9ft"
    label: str                             # Human-readable name
    parent_id: Optional[str] = None        # None = root
    depth: int = 0                         # 0 = root domain
    keywords: Tuple[str, ...] = ()         # Search terms
    parametric_range: Optional[Tuple[float, float]] = None  # (min, max) if numerical
    parametric_unit: Optional[str] = None  # e.g., "feet", "lux", "dB"
    typical_modality: SensoryModality = SensoryModality.VISUAL
    typical_delivery: DeliveryMode = DeliveryMode.UNSPECIFIED
    manipulation_type: ManipulationType = ManipulationType.ENVIRONMENTAL
    mechanism_ids: Tuple[str, ...] = ()    # T2 template IDs this maps to


# ══════════════════════════════════════════════════════════════════
# Stimulus Taxonomy
# ══════════════════════════════════════════════════════════════════

# ---------- Root Domains ----------
_ROOTS = {
    "spatial": TaxonomyNode("spatial", "Spatial Properties", depth=0,
        keywords=("space", "room", "building", "floor plan", "layout")),
    "natural": TaxonomyNode("natural", "Natural Elements", depth=0,
        keywords=("nature", "green", "plant", "water", "biophilic")),
    "material": TaxonomyNode("material", "Material & Surface Properties", depth=0,
        keywords=("material", "surface", "texture", "finish")),
    "luminous": TaxonomyNode("luminous", "Light & Color", depth=0,
        keywords=("light", "color", "colour", "illumination", "daylight")),
    "acoustic": TaxonomyNode("acoustic", "Acoustic Environment", depth=0,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("sound", "noise", "acoustic", "audio")),
    "thermal": TaxonomyNode("thermal", "Thermal Environment", depth=0,
        typical_modality=SensoryModality.THERMAL,
        keywords=("temperature", "thermal", "heat", "cold", "hvac")),
    "olfactory": TaxonomyNode("olfactory", "Olfactory Environment", depth=0,
        typical_modality=SensoryModality.OLFACTORY,
        keywords=("smell", "odor", "scent", "fragrance", "aroma")),
    "social_spatial": TaxonomyNode("social_spatial", "Social-Spatial Configuration", depth=0,
        keywords=("social", "seating", "arrangement", "density", "crowding")),
    "person_state": TaxonomyNode("person_state", "Person-State Manipulations", depth=0,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("cognitive load", "fatigue", "arousal", "mood induction")),
    "cultural": TaxonomyNode("cultural", "Cultural Context", depth=0,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("culture", "cultural", "western", "eastern", "indigenous")),
    "temporal_env": TaxonomyNode("temporal_env", "Temporal/Dynamic Environment", depth=0,
        manipulation_type=ManipulationType.TEMPORAL,
        keywords=("time of day", "season", "circadian", "duration", "exposure time")),
}

# ---------- Spatial subtree ----------
_SPATIAL = {
    "spatial.height": TaxonomyNode("spatial.height", "Ceiling Height", parent_id="spatial", depth=1,
        keywords=("ceiling height", "room height", "vertical dimension", "tall ceiling", "low ceiling", "ceiling"),
        mechanism_ids=("VIEW1", "T9")),
    "spatial.height.low": TaxonomyNode("spatial.height.low", "Low Ceiling (<8ft)", parent_id="spatial.height", depth=2,
        parametric_range=(0, 8.0), parametric_unit="feet",
        keywords=("low ceiling", "8 foot", "standard ceiling", "2.4m", "2.5m")),
    "spatial.height.standard": TaxonomyNode("spatial.height.standard", "Standard Ceiling (8-9ft)", parent_id="spatial.height", depth=2,
        parametric_range=(8.0, 9.0), parametric_unit="feet",
        keywords=("standard ceiling", "normal ceiling", "2.7m", "conventional height")),
    "spatial.height.high": TaxonomyNode("spatial.height.high", "High Ceiling (>9ft)", parent_id="spatial.height", depth=2,
        parametric_range=(9.0, 30.0), parametric_unit="feet",
        keywords=("high ceiling", "tall ceiling", "cathedral ceiling", "double height", "9 foot", "10 foot", "12 foot", "3m", "4m")),
    "spatial.volume": TaxonomyNode("spatial.volume", "Room Volume / Size", parent_id="spatial", depth=1,
        keywords=("room size", "volume", "spaciousness", "area", "square footage", "room area", "floor area")),
    "spatial.shape": TaxonomyNode("spatial.shape", "Room Shape / Geometry", parent_id="spatial", depth=1,
        keywords=("room shape", "geometry", "rectangular", "circular", "curved", "irregular", "room geometry")),
    "spatial.shape.rectangular": TaxonomyNode("spatial.shape.rectangular", "Rectangular", parent_id="spatial.shape", depth=2,
        keywords=("rectangular", "rectilinear", "orthogonal", "L-shaped")),
    "spatial.shape.circular": TaxonomyNode("spatial.shape.circular", "Circular / Curved", parent_id="spatial.shape", depth=2,
        keywords=("circular", "curved", "round", "organic", "curvilinear")),
    "spatial.shape.irregular": TaxonomyNode("spatial.shape.irregular", "Irregular / Complex", parent_id="spatial.shape", depth=2,
        keywords=("irregular", "complex", "angular", "non-standard", "deconstructivist")),
    "spatial.openness": TaxonomyNode("spatial.openness", "Openness / Enclosure", parent_id="spatial", depth=1,
        keywords=("open plan", "enclosed", "partition", "wall", "boundary", "prospect", "refuge", "enclosure",
                  "relocation from private office", "open-plan")),
    "spatial.openness.open_plan": TaxonomyNode("spatial.openness.open_plan", "Open Plan", parent_id="spatial.openness", depth=2,
        keywords=("open plan", "open office", "no partitions", "open-plan", "hot desk", "hot desking")),
    "spatial.openness.enclosed": TaxonomyNode("spatial.openness.enclosed", "Enclosed / Private", parent_id="spatial.openness", depth=2,
        keywords=("enclosed", "private office", "closed room", "cell office", "private room")),
    "spatial.openness.semi": TaxonomyNode("spatial.openness.semi", "Semi-enclosed", parent_id="spatial.openness", depth=2,
        keywords=("semi-enclosed", "cubicle", "partial partition", "activity-based", "ABW")),
    "spatial.layout": TaxonomyNode("spatial.layout", "Spatial Layout / Configuration", parent_id="spatial", depth=1,
        keywords=("layout", "configuration", "floor plan", "circulation", "wayfinding", "spatial layout",
                  "spatial accessibility", "connectivity", "integration", "spatial arrangement"),
        mechanism_ids=("SN1", "WF1")),
    "spatial.view": TaxonomyNode("spatial.view", "Window / View", parent_id="spatial", depth=1,
        keywords=("window", "view", "outlook", "vista", "prospect", "visual connection", "glazing ratio"),
        mechanism_ids=("VIEW1",)),
    "spatial.view.window": TaxonomyNode("spatial.view.window", "Window Presence/Absence", parent_id="spatial.view", depth=2,
        keywords=("window", "windowless", "presence of windows", "absence of windows", "visual connection to outdoors")),
    "spatial.view.nature_view": TaxonomyNode("spatial.view.nature_view", "Nature View from Window", parent_id="spatial.view", depth=2,
        keywords=("nature view", "green view", "garden view", "tree view", "view to nature")),
    "spatial.view.skylight": TaxonomyNode("spatial.view.skylight", "Skylight / Rooflight", parent_id="spatial.view", depth=2,
        keywords=("skylight", "rooflight", "toplighting", "zenithal")),
    "spatial.contour": TaxonomyNode("spatial.contour", "Contour / Edge Properties", parent_id="spatial", depth=1,
        keywords=("contour", "edge", "curved contour", "angular contour", "sharp", "soft", "curvilinear")),
    "spatial.density": TaxonomyNode("spatial.density", "Spatial Density / Crowding", parent_id="spatial", depth=1,
        keywords=("density", "crowding", "personal space", "proxemics", "crowding perception", "overcrowding",
                  "number of people", "social density"),
        mechanism_ids=("T5",)),
    "spatial.complexity": TaxonomyNode("spatial.complexity", "Spatial Complexity", parent_id="spatial", depth=1,
        keywords=("complexity", "visual complexity", "information density", "clutter", "environmental complexity")),
    "spatial.symmetry": TaxonomyNode("spatial.symmetry", "Symmetry / Balance", parent_id="spatial", depth=1,
        keywords=("symmetry", "asymmetry", "balance", "proportion", "golden ratio")),
    "spatial.proportion": TaxonomyNode("spatial.proportion", "Room Proportions / Aspect Ratio", parent_id="spatial", depth=1,
        keywords=("proportion", "aspect ratio", "room ratio", "width-to-depth", "room width")),
    "spatial.navigation": TaxonomyNode("spatial.navigation", "Wayfinding / Navigation", parent_id="spatial", depth=1,
        keywords=("wayfinding", "navigation", "signage", "legibility", "spatial orientation"),
        mechanism_ids=("SN1",)),
    "spatial.furniture": TaxonomyNode("spatial.furniture", "Furniture / Interior Elements", parent_id="spatial", depth=1,
        keywords=("furniture", "desk", "chair", "table", "workstation", "interior design", "furnishing")),
}

# ---------- Natural subtree ----------
_NATURAL = {
    "natural.vegetation": TaxonomyNode("natural.vegetation", "Vegetation / Plants", parent_id="natural", depth=1,
        keywords=("plant", "vegetation", "greenery", "tree", "garden", "biophilia", "indoor plant",
                  "potted plant", "green wall", "living wall"),
        mechanism_ids=("BIO1", "ART1")),
    "natural.water": TaxonomyNode("natural.water", "Water Features", parent_id="natural", depth=1,
        keywords=("water", "fountain", "stream", "pond", "aquatic", "water feature", "waterfall")),
    "natural.view_nature": TaxonomyNode("natural.view_nature", "Nature Views", parent_id="natural", depth=1,
        keywords=("nature view", "green view", "window nature", "outdoor view", "scenic beauty",
                  "natural scenery", "landscape view", "nature scene"),
        mechanism_ids=("VIEW1", "SRT1")),
    "natural.materials": TaxonomyNode("natural.materials", "Natural Materials (wood, stone)", parent_id="natural", depth=1,
        keywords=("natural material", "natural materials", "bamboo", "rattan", "stone",
                  "natural vs artificial", "natural vs. artificial")),
    "natural.outdoor": TaxonomyNode("natural.outdoor", "Outdoor / Park Settings", parent_id="natural", depth=1,
        keywords=("outdoor", "park", "garden", "forest", "wilderness", "natural settings",
                  "urban park", "green space", "natural environment")),
    "natural.biomorphic": TaxonomyNode("natural.biomorphic", "Biomorphic Patterns", parent_id="natural", depth=1,
        keywords=("biomorphic", "organic pattern", "natural pattern", "biophilic pattern", "biophilic design")),
    "natural.biomorphic.fractal": TaxonomyNode("natural.biomorphic.fractal", "Fractal Patterns / Dimension", parent_id="natural.biomorphic", depth=2,
        keywords=("fractal", "fractal dimension", "D-value", "self-similar", "fractal pattern",
                  "global-forest", "fractal complexity")),
    "natural.biomorphic.organic_shape": TaxonomyNode("natural.biomorphic.organic_shape", "Organic / Non-Rectilinear Shapes", parent_id="natural.biomorphic", depth=2,
        keywords=("organic shape", "biomorphic form", "natural form", "non-rectilinear")),
    "natural.nature_sound": TaxonomyNode("natural.nature_sound", "Nature Sounds (cross-sensory)", parent_id="natural", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("birdsong", "bird song", "water sound", "nature sound", "natural soundscape")),
}

# ---------- Material subtree ----------
_MATERIAL = {
    "material.wood": TaxonomyNode("material.wood", "Wood / Timber", parent_id="material", depth=1,
        keywords=("wood", "timber", "wooden", "plywood", "CLT", "cedar", "pine", "oak",
                  "wood panel", "lumber", "wood finishing", "Japanese cedar")),
    "material.concrete": TaxonomyNode("material.concrete", "Concrete / Masite", parent_id="material", depth=1,
        keywords=("concrete", "cement", "brutalist", "exposed concrete")),
    "material.glass": TaxonomyNode("material.glass", "Glass / Transparent", parent_id="material", depth=1,
        keywords=("glass", "glazing", "transparent", "translucent", "transparency")),
    "material.fabric": TaxonomyNode("material.fabric", "Fabric / Soft Materials", parent_id="material", depth=1,
        keywords=("fabric", "textile", "upholstery", "carpet", "curtain", "soft furnishing")),
    "material.texture": TaxonomyNode("material.texture", "Surface Texture", parent_id="material", depth=1,
        keywords=("texture", "rough", "smooth", "matte", "glossy", "tactile", "haptic texture")),
    "material.natural_vs_artificial": TaxonomyNode("material.natural_vs_artificial", "Natural vs Artificial Materials", parent_id="material", depth=1,
        keywords=("natural materials", "artificial materials", "natural vs artificial",
                  "resin", "synthetic", "printed grain", "WPC")),
    "material.metal": TaxonomyNode("material.metal", "Metal / Steel", parent_id="material", depth=1,
        keywords=("metal", "steel", "aluminum", "copper", "brass", "metallic")),
}

# ---------- Luminous subtree ----------
_LUMINOUS = {
    "luminous.daylight": TaxonomyNode("luminous.daylight", "Daylight / Natural Light", parent_id="luminous", depth=1,
        keywords=("daylight", "natural light", "sunlight", "daylighting", "daylight access",
                  "NLD", "natural light design", "daylight factor", "daylight color"),
        mechanism_ids=("CB1",)),
    "luminous.artificial": TaxonomyNode("luminous.artificial", "Artificial Lighting", parent_id="luminous", depth=1,
        keywords=("artificial light", "electric light", "LED", "fluorescent",
                  "dynamic lighting", "static lighting", "lighting pattern")),
    "luminous.color_temp": TaxonomyNode("luminous.color_temp", "Color Temperature (CCT)", parent_id="luminous", depth=1,
        keywords=("color temperature", "warm light", "cool light", "kelvin", "CCT",
                  "correlated color temperature", "blue-enriched", "white light"),
        parametric_unit="kelvin"),
    "luminous.color_temp.warm": TaxonomyNode("luminous.color_temp.warm", "Warm CCT (<3500K)", parent_id="luminous.color_temp", depth=2,
        parametric_range=(1800, 3500), parametric_unit="kelvin",
        keywords=("warm light", "2700K", "3000K", "warm white", "incandescent")),
    "luminous.color_temp.neutral": TaxonomyNode("luminous.color_temp.neutral", "Neutral CCT (3500-5000K)", parent_id="luminous.color_temp", depth=2,
        parametric_range=(3500, 5000), parametric_unit="kelvin",
        keywords=("neutral light", "4000K", "neutral white")),
    "luminous.color_temp.cool": TaxonomyNode("luminous.color_temp.cool", "Cool CCT (5000-6500K)", parent_id="luminous.color_temp", depth=2,
        parametric_range=(5000, 6500), parametric_unit="kelvin",
        keywords=("cool light", "5700K", "6500K", "cool white", "daylight CCT")),
    "luminous.color_temp.enriched": TaxonomyNode("luminous.color_temp.enriched", "Blue-Enriched (>6500K)", parent_id="luminous.color_temp", depth=2,
        parametric_range=(6500, 20000), parametric_unit="kelvin",
        keywords=("blue-enriched", "17000K", "high CCT", "blue-enriched white light")),
    "luminous.illuminance": TaxonomyNode("luminous.illuminance", "Illuminance Level", parent_id="luminous", depth=1,
        keywords=("illuminance", "lux", "light level", "brightness", "dimming",
                  "light intensity", "ambient illumination"),
        parametric_unit="lux"),
    "luminous.illuminance.low": TaxonomyNode("luminous.illuminance.low", "Low Illuminance (<200 lux)", parent_id="luminous.illuminance", depth=2,
        parametric_range=(0, 200), parametric_unit="lux",
        keywords=("dim", "low light", "50 lux", "100 lux", "dim lighting")),
    "luminous.illuminance.standard": TaxonomyNode("luminous.illuminance.standard", "Standard Illuminance (200-500 lux)", parent_id="luminous.illuminance", depth=2,
        parametric_range=(200, 500), parametric_unit="lux",
        keywords=("standard lighting", "300 lux", "500 lux", "office lighting")),
    "luminous.illuminance.high": TaxonomyNode("luminous.illuminance.high", "High Illuminance (>500 lux)", parent_id="luminous.illuminance", depth=2,
        parametric_range=(500, 10000), parametric_unit="lux",
        keywords=("bright", "high lux", "1000 lux", "bright light")),
    "luminous.color": TaxonomyNode("luminous.color", "Wall/Surface Color", parent_id="luminous", depth=1,
        keywords=("color", "colour", "hue", "wall color", "paint", "room color",
                  "color samples", "chromatic", "achromatic")),
    "luminous.color.warm_hue": TaxonomyNode("luminous.color.warm_hue", "Warm Hues (Red/Orange/Yellow)", parent_id="luminous.color", depth=2,
        keywords=("red", "orange", "yellow", "warm hue", "warm color")),
    "luminous.color.cool_hue": TaxonomyNode("luminous.color.cool_hue", "Cool Hues (Blue/Green)", parent_id="luminous.color", depth=2,
        keywords=("blue", "green", "cool hue", "blue room", "green room")),
    "luminous.color.neutral_hue": TaxonomyNode("luminous.color.neutral_hue", "Neutral Colors (White/Grey/Beige)", parent_id="luminous.color", depth=2,
        keywords=("white", "grey", "gray", "beige", "neutral", "white room")),
    "luminous.glare": TaxonomyNode("luminous.glare", "Glare / Visual Discomfort", parent_id="luminous", depth=1,
        keywords=("glare", "discomfort glare", "disability glare", "UGR", "visual discomfort")),
    "luminous.color_rendering": TaxonomyNode("luminous.color_rendering", "Color Rendering (CRI)", parent_id="luminous", depth=1,
        keywords=("CRI", "color rendering", "color rendering index", "Ra")),
    "luminous.personal_control": TaxonomyNode("luminous.personal_control", "Personal Lighting Control", parent_id="luminous", depth=1,
        keywords=("personal control", "lighting control", "user control", "dimmer",
                  "having and exercising control", "tunable")),
}

# ---------- Acoustic subtree ----------
_ACOUSTIC = {
    "acoustic.noise": TaxonomyNode("acoustic.noise", "Noise Level", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("noise", "noise level", "decibel", "loudness", "ambient noise",
                  "background noise", "occupied background noise", "Ln", "dBA",
                  "noise annoyance", "noise exposure"),
        parametric_unit="dB"),
    "acoustic.noise.low": TaxonomyNode("acoustic.noise.low", "Low Noise (<40 dBA)", parent_id="acoustic.noise", depth=2,
        typical_modality=SensoryModality.AUDITORY,
        parametric_range=(0, 40), parametric_unit="dBA",
        keywords=("quiet", "low noise", "silent")),
    "acoustic.noise.moderate": TaxonomyNode("acoustic.noise.moderate", "Moderate Noise (40-65 dBA)", parent_id="acoustic.noise", depth=2,
        typical_modality=SensoryModality.AUDITORY,
        parametric_range=(40, 65), parametric_unit="dBA",
        keywords=("moderate noise", "office noise", "typical indoor")),
    "acoustic.noise.high": TaxonomyNode("acoustic.noise.high", "High Noise (>65 dBA)", parent_id="acoustic.noise", depth=2,
        typical_modality=SensoryModality.AUDITORY,
        parametric_range=(65, 120), parametric_unit="dBA",
        keywords=("loud", "high noise", "noisy")),
    "acoustic.speech": TaxonomyNode("acoustic.speech", "Speech / Conversation Noise", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("speech", "conversation", "speech intelligibility", "privacy",
                  "speech privacy", "irrelevant speech", "STI", "intelligibility")),
    "acoustic.nature_sound": TaxonomyNode("acoustic.nature_sound", "Nature Sounds", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("birdsong", "water sound", "nature sound", "wind", "natural soundscape")),
    "acoustic.music": TaxonomyNode("acoustic.music", "Music", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("music", "background music", "tempo", "genre", "musical")),
    "acoustic.reverberation": TaxonomyNode("acoustic.reverberation", "Reverberation / RT60", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("reverberation", "RT60", "echo", "acoustic absorption", "wet recordings", "dry recordings"),
        parametric_unit="seconds"),
    "acoustic.soundscape": TaxonomyNode("acoustic.soundscape", "Soundscape Quality", parent_id="acoustic", depth=1,
        typical_modality=SensoryModality.AUDITORY,
        keywords=("soundscape", "acoustic environment", "sound environment", "sonic environment",
                  "soundscape quality", "acoustic satisfaction")),
}

# ---------- Thermal subtree ----------
_THERMAL = {
    "thermal.temperature": TaxonomyNode("thermal.temperature", "Air Temperature", parent_id="thermal", depth=1,
        typical_modality=SensoryModality.THERMAL,
        keywords=("temperature", "air temperature", "thermostat", "indoor temperature",
                  "operative temperature", "thermal condition"),
        parametric_unit="celsius"),
    "thermal.temperature.cool": TaxonomyNode("thermal.temperature.cool", "Cool (<20°C)", parent_id="thermal.temperature", depth=2,
        typical_modality=SensoryModality.THERMAL,
        parametric_range=(0, 20), parametric_unit="celsius",
        keywords=("cool", "cold", "low temperature")),
    "thermal.temperature.comfortable": TaxonomyNode("thermal.temperature.comfortable", "Comfortable (20-26°C)", parent_id="thermal.temperature", depth=2,
        typical_modality=SensoryModality.THERMAL,
        parametric_range=(20, 26), parametric_unit="celsius",
        keywords=("comfortable", "neutral temperature", "24°C", "22°C")),
    "thermal.temperature.warm": TaxonomyNode("thermal.temperature.warm", "Warm (>26°C)", parent_id="thermal.temperature", depth=2,
        typical_modality=SensoryModality.THERMAL,
        parametric_range=(26, 50), parametric_unit="celsius",
        keywords=("warm", "hot", "high temperature", "29°C", "overheating")),
    "thermal.ventilation": TaxonomyNode("thermal.ventilation", "Ventilation Type", parent_id="thermal", depth=1,
        typical_modality=SensoryModality.THERMAL,
        keywords=("ventilation", "natural ventilation", "HVAC", "air conditioning",
                  "mechanical ventilation", "mixed-mode", "air quality", "IAQ")),
    "thermal.humidity": TaxonomyNode("thermal.humidity", "Humidity", parent_id="thermal", depth=1,
        typical_modality=SensoryModality.THERMAL,
        keywords=("humidity", "relative humidity", "moisture", "RH"),
        parametric_unit="percent"),
    "thermal.radiant": TaxonomyNode("thermal.radiant", "Radiant Temperature / Asymmetry", parent_id="thermal", depth=1,
        typical_modality=SensoryModality.THERMAL,
        keywords=("radiant", "radiant temperature", "mean radiant temperature", "MRT",
                  "radiant asymmetry", "radiant heating")),
}

# ---------- Social-Spatial subtree ----------
_SOCIAL = {
    "social_spatial.seating": TaxonomyNode("social_spatial.seating", "Seating Arrangement", parent_id="social_spatial", depth=1,
        keywords=("seating", "chair", "desk arrangement", "furniture layout")),
    "social_spatial.occupancy": TaxonomyNode("social_spatial.occupancy", "Occupancy / Density", parent_id="social_spatial", depth=1,
        keywords=("occupancy", "people density", "number of people")),
    "social_spatial.privacy": TaxonomyNode("social_spatial.privacy", "Privacy Gradient", parent_id="social_spatial", depth=1,
        keywords=("privacy", "personal space", "visual privacy", "acoustic privacy")),
    "social_spatial.territory": TaxonomyNode("social_spatial.territory", "Territoriality / Personalization", parent_id="social_spatial", depth=1,
        keywords=("territory", "personalization", "ownership", "place attachment")),
}

# ---------- Person-state subtree ----------
_PERSON_STATE = {
    "person_state.cognitive_load": TaxonomyNode("person_state.cognitive_load", "Cognitive Load", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("cognitive load", "mental load", "dual task", "working memory load")),
    "person_state.fatigue": TaxonomyNode("person_state.fatigue", "Fatigue / Depletion", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("fatigue", "mental fatigue", "depletion", "directed attention fatigue")),
    "person_state.arousal": TaxonomyNode("person_state.arousal", "Arousal Level", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("arousal", "activation", "alertness", "caffeine")),
    "person_state.mood": TaxonomyNode("person_state.mood", "Mood Induction", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("mood", "mood induction", "positive affect", "negative affect")),
    "person_state.expertise": TaxonomyNode("person_state.expertise", "Expertise / Familiarity", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("expertise", "familiarity", "architect", "novice", "expert")),
    "person_state.health": TaxonomyNode("person_state.health", "Health Status / Clinical", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("patient", "clinical", "health condition", "recovery", "rehabilitation")),
}

# ---------- Psychological Constructs (V10 panel experts #5, #9) ----------
_PSYCHOLOGICAL = {
    "person_state.perceived_control": TaxonomyNode(
        "person_state.perceived_control", "Perceived Control", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("perceived control", "personal control", "locus of control",
                  "environmental control", "controllability", "autonomy",
                  "having and exercising control", "sense of control"),
        mechanism_ids=("VIEW1",)),
    "person_state.fascination": TaxonomyNode(
        "person_state.fascination", "Fascination (Kaplan ART)", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("fascination", "involuntary attention", "soft fascination",
                  "hard fascination", "ART", "attention restoration",
                  "attentional fascination", "effortless attention"),
        mechanism_ids=("ART1", "SRT1")),
    "person_state.restorativeness": TaxonomyNode(
        "person_state.restorativeness", "Restorativeness", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.PERSON_STATE,
        keywords=("restorativeness", "restorative", "PRS", "perceived restorativeness",
                  "restoration", "stress recovery", "directed attention restoration",
                  "being away", "extent", "compatibility"),
        mechanism_ids=("SRT1", "ART1")),
    "person_state.env_complexity": TaxonomyNode(
        "person_state.env_complexity", "Environmental Complexity", parent_id="person_state", depth=1,
        manipulation_type=ManipulationType.ENVIRONMENTAL,
        keywords=("environmental complexity", "stimulus richness", "information rate",
                  "environmental stimulation", "understimulation", "overstimulation")),
    "natural.biophilia": TaxonomyNode(
        "natural.biophilia", "Biophilia (Integrated)", parent_id="natural", depth=1,
        keywords=("biophilia", "biophilic", "biophilic design", "nature connection",
                  "connectedness to nature", "nature relatedness", "14 patterns",
                  "nature affinity", "love of nature"),
        mechanism_ids=("BIO1",)),
}

# ---------- Cultural subtree ----------
_CULTURAL = {
    "cultural.western": TaxonomyNode("cultural.western", "Western / WEIRD", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("western", "WEIRD", "American", "European", "individualist")),
    "cultural.east_asian": TaxonomyNode("cultural.east_asian", "East Asian", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("Japanese", "Chinese", "Korean", "East Asian", "collectivist")),
    "cultural.south_asian": TaxonomyNode("cultural.south_asian", "South Asian", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("Indian", "South Asian", "Hindu", "Buddhist")),
    "cultural.african": TaxonomyNode("cultural.african", "African", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("African", "Yoruba", "Sub-Saharan", "Bantu")),
    "cultural.middle_eastern": TaxonomyNode("cultural.middle_eastern", "Middle Eastern", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("Middle Eastern", "Islamic", "Arabic")),
    "cultural.indigenous": TaxonomyNode("cultural.indigenous", "Indigenous / Traditional", parent_id="cultural", depth=1,
        manipulation_type=ManipulationType.CULTURAL,
        keywords=("indigenous", "traditional", "vernacular", "tribal")),
}

# ---------- Temporal subtree ----------
_TEMPORAL = {
    "temporal_env.time_of_day": TaxonomyNode("temporal_env.time_of_day", "Time of Day", parent_id="temporal_env", depth=1,
        manipulation_type=ManipulationType.TEMPORAL,
        keywords=("morning", "afternoon", "evening", "night", "circadian")),
    "temporal_env.exposure_duration": TaxonomyNode("temporal_env.exposure_duration", "Exposure Duration", parent_id="temporal_env", depth=1,
        manipulation_type=ManipulationType.TEMPORAL,
        keywords=("duration", "exposure time", "minutes", "acute", "chronic"),
        parametric_unit="minutes"),
    "temporal_env.season": TaxonomyNode("temporal_env.season", "Season / Climate", parent_id="temporal_env", depth=1,
        manipulation_type=ManipulationType.TEMPORAL,
        keywords=("season", "winter", "summer", "climate")),
}


# ══════════════════════════════════════════════════════════════════
# Taxonomy Registry
# ══════════════════════════════════════════════════════════════════

# Merge all subtrees
ALL_NODES: Dict[str, TaxonomyNode] = {}
for _subtree in [_ROOTS, _SPATIAL, _NATURAL, _MATERIAL, _LUMINOUS,
                 _ACOUSTIC, _THERMAL, _SOCIAL, _PERSON_STATE,
                 _PSYCHOLOGICAL, _CULTURAL, _TEMPORAL]:
    ALL_NODES.update(_subtree)


class StimulusTaxonomy:
    """
    Hierarchical stimulus taxonomy with subsumption and generalization.

    Provides:
      - Node lookup by ID or keyword
      - Ancestry / descendant queries
      - Common ancestor computation
      - Generalization distance metric
      - Parametric range matching
      - Facet-based filtering

    Informed by:
      - Tenenbaum & Griffiths (2001): Bayesian generalization —
        probability of generalizing from examples is proportional to
        the size of the smallest hypothesis consistent with all examples.
      - Rosch (1975): Basic-level categories are the most informative.
    """

    def __init__(self, nodes: Optional[Dict[str, TaxonomyNode]] = None):
        self._nodes = dict(nodes or ALL_NODES)
        self._children: Dict[str, List[str]] = {}
        self._build_children_index()

    def _build_children_index(self) -> None:
        """Build parent → children index."""
        self._children = {node_id: [] for node_id in self._nodes}
        for node_id, node in self._nodes.items():
            if node.parent_id and node.parent_id in self._children:
                self._children[node.parent_id].append(node_id)

    # ── Lookup ──

    def get(self, node_id: str) -> Optional[TaxonomyNode]:
        return self._nodes.get(node_id)

    def roots(self) -> List[TaxonomyNode]:
        return [n for n in self._nodes.values() if n.parent_id is None]

    def children(self, node_id: str) -> List[TaxonomyNode]:
        return [self._nodes[cid] for cid in self._children.get(node_id, [])]

    def descendants(self, node_id: str) -> List[TaxonomyNode]:
        """All descendants (recursive)."""
        result = []
        for cid in self._children.get(node_id, []):
            result.append(self._nodes[cid])
            result.extend(self.descendants(cid))
        return result

    def ancestors(self, node_id: str) -> List[TaxonomyNode]:
        """All ancestors (root last)."""
        result = []
        node = self._nodes.get(node_id)
        while node and node.parent_id:
            parent = self._nodes.get(node.parent_id)
            if parent:
                result.append(parent)
                node = parent
            else:
                break
        return result

    # ── Subsumption ──

    def is_ancestor_of(self, ancestor_id: str, descendant_id: str) -> bool:
        """Is ancestor_id an ancestor of descendant_id?"""
        current = descendant_id
        while current:
            node = self._nodes.get(current)
            if not node:
                return False
            if node.parent_id == ancestor_id:
                return True
            current = node.parent_id
        return False

    def common_ancestor(self, id_a: str, id_b: str) -> Optional[str]:
        """
        Find the lowest common ancestor (LCA) of two nodes.

        Uses the Tenenbaum principle: the LCA defines the minimal
        generalizing hypothesis that covers both examples.
        """
        # Get ancestor sets
        ancestors_a = {id_a}
        current = id_a
        while current:
            node = self._nodes.get(current)
            if node and node.parent_id:
                ancestors_a.add(node.parent_id)
                current = node.parent_id
            else:
                break

        # Walk up from id_b until we hit an ancestor of id_a
        current = id_b
        while current:
            if current in ancestors_a:
                return current
            node = self._nodes.get(current)
            if node and node.parent_id:
                current = node.parent_id
            else:
                break
        return None

    def generalization_distance(self, id_a: str, id_b: str) -> int:
        """
        Distance between two nodes in the taxonomy tree.

        = depth(a) + depth(b) - 2 * depth(LCA)

        Lower distance → easier to generalize.
        """
        lca = self.common_ancestor(id_a, id_b)
        if lca is None:
            return 999  # No common ancestor
        node_a = self._nodes.get(id_a)
        node_b = self._nodes.get(id_b)
        lca_node = self._nodes.get(lca)
        if not (node_a and node_b and lca_node):
            return 999
        return (node_a.depth + node_b.depth) - 2 * lca_node.depth

    # ── Keyword matching ──

    def match_keywords(self, text: str) -> List[Tuple[str, float]]:
        """
        Match a text string against taxonomy nodes by keyword overlap.

        Returns list of (node_id, score) sorted by score descending.
        Score is fraction of keywords matched.
        """
        text_lower = text.lower()
        matches = []
        for node_id, node in self._nodes.items():
            if not node.keywords:
                continue
            n_matched = sum(1 for kw in node.keywords if kw in text_lower)
            if n_matched > 0:
                score = n_matched / len(node.keywords)
                matches.append((node_id, score))
        matches.sort(key=lambda x: (-x[1], x[0]))
        return matches

    def classify_stimulus(self, text: str) -> Optional[str]:
        """
        Classify a stimulus description to its best taxonomy node.

        Prefers deeper (more specific) nodes when multiple match.
        """
        matches = self.match_keywords(text)
        if not matches:
            return None
        # Among top matches, prefer deeper nodes
        top_score = matches[0][1]
        top_matches = [(nid, s) for nid, s in matches if s >= top_score * 0.8]
        # Sort by depth (deeper = more specific)
        top_matches.sort(key=lambda x: -(self._nodes[x[0]].depth))
        return top_matches[0][0]

    # ── Parametric matching ──

    def match_parametric(self, parent_id: str, value: float) -> Optional[str]:
        """
        Find the child node whose parametric range contains the value.

        Example: match_parametric("spatial.height", 9.5) → "spatial.height.high"
        """
        for child in self.children(parent_id):
            if child.parametric_range:
                lo, hi = child.parametric_range
                if lo <= value <= hi:
                    return child.node_id
        return parent_id  # Fall back to parent if no range matches

    # ── Facet queries ──

    def nodes_by_modality(self, modality: SensoryModality) -> List[TaxonomyNode]:
        """Get all nodes for a specific sensory modality."""
        return [n for n in self._nodes.values() if n.typical_modality == modality]

    def nodes_by_manipulation_type(self, mtype: ManipulationType) -> List[TaxonomyNode]:
        """Get all nodes for a specific manipulation type."""
        return [n for n in self._nodes.values() if n.manipulation_type == mtype]

    def nodes_by_delivery_mode(self, mode: DeliveryMode) -> List[TaxonomyNode]:
        """Get all nodes typically delivered via a specific mode."""
        return [n for n in self._nodes.values() if n.typical_delivery == mode]

    # ── Generalization rules ──

    def can_merge(
        self,
        id_a: str,
        id_b: str,
        require_mechanism_identity: bool = True,
    ) -> Tuple[bool, str]:
        """
        Can two stimulus nodes be merged for T3 generalization?

        Rules:
        1. Must share a common ancestor
        2. If mechanism_identity required, must share at least one T2 template
        3. Must be in the same root domain

        Returns (can_merge, reason).
        """
        node_a = self._nodes.get(id_a)
        node_b = self._nodes.get(id_b)
        if not node_a or not node_b:
            return False, "Node not found"

        lca = self.common_ancestor(id_a, id_b)
        if lca is None:
            return False, "No common ancestor"

        # Must be in same root domain
        root_a = id_a.split(".")[0]
        root_b = id_b.split(".")[0]
        if root_a != root_b:
            return False, f"Different root domains: {root_a} vs {root_b}"

        # Mechanism identity check (Cartwright's capacities principle)
        if require_mechanism_identity:
            mechs_a = set(node_a.mechanism_ids)
            mechs_b = set(node_b.mechanism_ids)
            if mechs_a and mechs_b and not mechs_a.intersection(mechs_b):
                return False, f"Different mechanisms: {mechs_a} vs {mechs_b}"

        return True, f"Merge at LCA={lca}"

    def sufficient_coverage(
        self,
        parent_id: str,
        tested_children: Set[str],
        min_coverage: float = 0.5,
    ) -> Tuple[bool, float]:
        """
        Has enough of a category's subtypes been tested to warrant
        a category-level generalization?

        Returns (sufficient, coverage_fraction).
        """
        all_children = self._children.get(parent_id, [])
        if not all_children:
            return True, 1.0  # Leaf node — full coverage by definition
        covered = sum(1 for c in all_children if c in tested_children)
        coverage = covered / len(all_children)
        return coverage >= min_coverage, coverage

    # ── Export ──

    def to_dict(self) -> Dict[str, Any]:
        """Export full taxonomy as serializable dict."""
        return {
            "n_nodes": len(self._nodes),
            "n_roots": len(self.roots()),
            "roots": [r.node_id for r in self.roots()],
            "nodes": {
                nid: {
                    "label": n.label,
                    "parent": n.parent_id,
                    "depth": n.depth,
                    "keywords": list(n.keywords),
                    "modality": n.typical_modality.value,
                    "manipulation_type": n.manipulation_type.value,
                    "mechanism_ids": list(n.mechanism_ids),
                }
                for nid, n in sorted(self._nodes.items())
            },
        }

    def register_node(self, node: TaxonomyNode) -> None:
        """Register a new node (for runtime extension)."""
        self._nodes[node.node_id] = node
        self._build_children_index()

    @property
    def size(self) -> int:
        return len(self._nodes)


# Singleton
_taxonomy: Optional[StimulusTaxonomy] = None

def get_stimulus_taxonomy() -> StimulusTaxonomy:
    """Get or create the stimulus taxonomy singleton."""
    global _taxonomy
    if _taxonomy is None:
        _taxonomy = StimulusTaxonomy()
    return _taxonomy
