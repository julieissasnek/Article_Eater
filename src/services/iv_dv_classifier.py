"""
iv_dv_classifier.py — Smart Taxonomy Classifier for T3
=======================================================

Three-stage classifier that maps raw antecedent/consequent strings
from extraction JSONs → taxonomy node IDs.

Stage 1: Pattern-based exact/regex matching (fast, deterministic)
Stage 2: Enhanced keyword matching with scoring (fast, cached)
Stage 3: Pre-built semantic mapping table (domain-expert knowledge)

The mapping table encodes the LLM's interpretation of the top-frequency
IVs and common patterns, amortizing the "LLM call" to a one-time
offline classification that's stored as code.

Design principles:
  - Tenenbaum: Probabilistic — returns confidence scores, not just labels
  - Bengio: Disentangled — extracts abstract attributes alongside node ID
  - Barrett: Access-level aware — DV classification detects measurement type
  - Cartwright: Mechanism-preserving — maps to deepest node that shares mechanism
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.services.stimulus_taxonomy import get_stimulus_taxonomy, StimulusTaxonomy
from src.services.dv_generalization import (
    DVAccessLevel, DVMeasurementType, get_dv_node
)

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Classification Results
# ══════════════════════════════════════════════════════════════════

@dataclass
class IVClassification:
    """Result of classifying an IV (antecedent) string."""
    node_id: str                           # Taxonomy node ID or raw text if unclassified
    confidence: float                      # 0-1 classification confidence
    method: str                            # "pattern", "keyword", "semantic_map", "unclassified"
    raw_text: str                          # Original input
    abstract_attributes: Dict[str, Any] = field(default_factory=dict)
    # Cross-cutting attributes: fractal_dimension, visual_complexity, CCT_K, etc.

@dataclass
class DVClassification:
    """Result of classifying a DV (consequent) string."""
    node_id: str
    confidence: float
    method: str
    raw_text: str
    access_level: DVAccessLevel = DVAccessLevel.UNSPECIFIED
    measure_type: DVMeasurementType = DVMeasurementType.UNSPECIFIED


# ══════════════════════════════════════════════════════════════════
# Stage 1: Pattern Matchers (regex-based, deterministic)
# ══════════════════════════════════════════════════════════════════

# IV patterns: compiled regex → (node_id, confidence, optional_attribute_extractor)
_IV_PATTERNS: List[Tuple[re.Pattern, str, float, Optional[str]]] = [
    # CCT / Color Temperature with numeric values
    (re.compile(r'(?:CCT|color\s*temperature|correlated\s*color)\s*.*?(\d{3,5})\s*K', re.I),
     "luminous.color_temp", 0.95, "CCT_K"),
    (re.compile(r'(\d{3,5})\s*K\b.*?(?:vs|compared|versus)', re.I),
     "luminous.color_temp", 0.90, "CCT_K"),
    (re.compile(r'(?:blue-enriched|blue.enriched)\s*(?:white\s*)?light', re.I),
     "luminous.color_temp.enriched", 0.92, None),
    (re.compile(r'warm\s+(?:white\s+)?light', re.I),
     "luminous.color_temp.warm", 0.85, None),

    # Illuminance with lux values
    (re.compile(r'(\d+)\s*lux', re.I),
     "luminous.illuminance", 0.90, "illuminance_lux"),
    (re.compile(r'illuminance.*?(\d+)', re.I),
     "luminous.illuminance", 0.85, "illuminance_lux"),

    # Ceiling height with numeric values
    (re.compile(r'ceiling\s*height.*?(\d+\.?\d*)\s*(?:ft|foot|feet|m\b|meter)', re.I),
     "spatial.height", 0.95, "ceiling_height"),
    (re.compile(r'(\d+\.?\d*)\s*(?:ft|foot|feet)\s*ceiling', re.I),
     "spatial.height", 0.90, "ceiling_height"),

    # Temperature with °C values
    (re.compile(r'(?:temperature|thermal).*?(\d+)\s*°?\s*C\b', re.I),
     "thermal.temperature", 0.90, "temperature_C"),
    (re.compile(r'(\d+)\s*°\s*C\s*(?:vs|compared)', re.I),
     "thermal.temperature", 0.85, "temperature_C"),

    # Noise with dB values
    (re.compile(r'(?:noise|sound\s*level).*?(\d+)\s*dB', re.I),
     "acoustic.noise", 0.90, "noise_dB"),
    (re.compile(r'(\d+)\s*dBA?\b', re.I),
     "acoustic.noise", 0.80, "noise_dB"),

    # Fractal dimension
    (re.compile(r'fractal\s*(?:dimension|D-value|complexity)', re.I),
     "natural.biomorphic.fractal", 0.95, None),
    (re.compile(r'D-value', re.I),
     "natural.biomorphic.fractal", 0.90, None),

    # Open plan / private office relocation
    (re.compile(r'relocation\s*(?:from|to)\s*(?:private|open)', re.I),
     "spatial.openness", 0.90, None),
    (re.compile(r'(?:open-plan|open\s*plan)\s*(?:office|workspace)', re.I),
     "spatial.openness.open_plan", 0.90, None),

    # LEED / Green building
    (re.compile(r'LEED\s*(?:certification|certified|rated)', re.I),
     "spatial.layout", 0.70, None),

    # Gender (person_state — not environmental)
    (re.compile(r'^gender\b', re.I),
     "person_state.expertise", 0.50, None),  # Low confidence — gender is a demographic, not a state
    (re.compile(r'(?:male|female)\s*(?:vs|versus|gender)', re.I),
     "person_state.expertise", 0.50, None),
]

# DV patterns
_DV_PATTERNS: List[Tuple[re.Pattern, str, float, DVAccessLevel, DVMeasurementType]] = [
    # Physiological measures
    (re.compile(r'\bHeart\s*Rate\b|\bHR\b', re.I),
     "cog.physiology.heart_rate", 0.95, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bRMSSD\b', re.I),
     "cog.physiology.hrv", 0.95, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bHRV\b|heart\s*rate\s*variability', re.I),
     "cog.physiology.hrv", 0.95, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bcortisol\b', re.I),
     "cog.physiology.cortisol", 0.95, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bEDA\b|electrodermal|skin\s*conductance', re.I),
     "cog.physiology.eda", 0.95, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bblood\s*pressure\b|\bBP\b', re.I),
     "cog.physiology.blood_pressure", 0.90, DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    (re.compile(r'\bEEG\b|alpha\s*(?:power|wave)', re.I),
     "cog.physiology.eeg", 0.90, DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),

    # Performance measures
    (re.compile(r'\breaction\s*time\b|\bRT\b', re.I),
     "cog.performance.reaction_time", 0.90, DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    (re.compile(r'error\s*rate|accuracy', re.I),
     "cog.performance.accuracy", 0.85, DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    (re.compile(r'task\s*performance|work\s*performance', re.I),
     "cog.performance.task", 0.80, DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),

    # Comfort measures
    (re.compile(r'visual\s*comfort', re.I),
     "affect.comfort.visual", 0.95, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'thermal\s*comfort', re.I),
     "affect.comfort.thermal", 0.95, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'acoustic\s*comfort', re.I),
     "affect.comfort.acoustic", 0.95, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'(?:overall|indoor|environmental)\s*(?:comfort|satisfaction)', re.I),
     "affect.comfort.overall", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'(?:overall|workspace)\s*satisfaction', re.I),
     "affect.satisfaction.overall", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'visual\s*satisfaction', re.I),
     "affect.satisfaction.visual", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Affect measures
    (re.compile(r'(?:perceived\s*)?happiness|positive\s*(?:mood|affect)', re.I),
     "affect.positive.happiness", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'(?:perceived\s*)?sadness|negative\s*(?:mood|affect)', re.I),
     "affect.negative.sadness", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'anxiety|anxious', re.I),
     "affect.negative.anxiety", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'stress|psychological\s*stress', re.I),
     "affect.negative.stress", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'warmth\s*(?:rating|perception|perceived)', re.I),
     "affect.perceived.warmth", 0.80, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'pleasantness|pleasant.*rating', re.I),
     "affect.positive.pleasantness", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'PANAS', re.I),
     "affect.panas", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Creativity
    (re.compile(r'creativ(?:ity|e)', re.I),
     "cog.creativity", 0.80, DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    (re.compile(r'divergent\s*thinking|fluency|originality', re.I),
     "cog.creativity.divergent", 0.85, DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),

    # Spatial cognition
    (re.compile(r'place\s*attachment', re.I),
     "spatial_behavior.place_attachment", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'sense\s*of\s*(?:privacy|territory)', re.I),
     "spatial_behavior.privacy", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'belonging|sense\s*of\s*belonging', re.I),
     "spatial_behavior.belonging", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'intention\s*to\s*(?:revisit|return|stay)', re.I),
     "spatial_behavior.revisit_intention", 0.90, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Soundscape / acoustic perception
    (re.compile(r'(?:sound|acoustic)\s*(?:satisfaction|preference|quality)', re.I),
     "affect.comfort.acoustic", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'soundscape\b', re.I),
     "affect.soundscape", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    (re.compile(r'scenic\s*beauty', re.I),
     "affect.aesthetic.scenic_beauty", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Perception
    (re.compile(r'(?:perceived\s*)?translucen', re.I),
     "perception.translucency", 0.85, DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
]


# ══════════════════════════════════════════════════════════════════
# Stage 3: Pre-built Semantic Mapping Table
# ══════════════════════════════════════════════════════════════════
# This encodes the "LLM classification" as a lookup table.
# Built from domain expert analysis of top-frequency raw IVs/DVs.

_IV_SEMANTIC_MAP: Dict[str, str] = {
    # Top IVs from data audit → taxonomy nodes
    "CCT": "luminous.color_temp",
    "cct": "luminous.color_temp",
    "correlated color temperature": "luminous.color_temp",
    "color temperature": "luminous.color_temp",
    "dynamic lighting": "luminous.artificial",
    "static lighting": "luminous.artificial",
    "dynamic lighting pattern": "luminous.artificial",
    "daylight": "luminous.daylight",
    "natural light": "luminous.daylight",
    "daylight color": "luminous.daylight",
    "color samples": "luminous.color",
    "room color": "luminous.color",
    "blue room color": "luminous.color.cool_hue",
    "red room color": "luminous.color.warm_hue",
    "warm white light": "luminous.color_temp.warm",
    "cool white light": "luminous.color_temp.cool",
    "personal control": "luminous.personal_control",
    "lighting control": "luminous.personal_control",
    "glare": "luminous.glare",

    # Natural / Biophilic
    "natural materials": "natural.materials",
    "artificial materials": "material.natural_vs_artificial",
    "wood": "material.wood",
    "timber": "material.wood",
    "japanese cedar": "material.wood",
    "cedar lumber": "material.wood",
    "plants": "natural.vegetation",
    "indoor plants": "natural.vegetation",
    "greenery": "natural.vegetation",
    "green wall": "natural.vegetation",
    "nature view": "natural.view_nature",
    "scenic beauty": "natural.view_nature",
    "outdoor view": "natural.view_nature",
    "fractal dimension": "natural.biomorphic.fractal",
    "fractal": "natural.biomorphic.fractal",
    "biomorphic": "natural.biomorphic",
    "biophilic design": "natural.biomorphic",

    # Spatial
    "ceiling height": "spatial.height",
    "high ceiling": "spatial.height.high",
    "low ceiling": "spatial.height.low",
    "open plan": "spatial.openness.open_plan",
    "open-plan": "spatial.openness.open_plan",
    "private office": "spatial.openness.enclosed",
    "enclosed office": "spatial.openness.enclosed",
    "spatial layout": "spatial.layout",
    "floor plan": "spatial.layout",
    "window": "spatial.view.window",
    "windowless": "spatial.view.window",
    "presence of windows": "spatial.view.window",
    "absence of windows": "spatial.view.window",
    "visual connection to outdoors": "spatial.view.window",
    "crowding": "spatial.density",
    "crowding perception": "spatial.density",
    "density": "spatial.density",
    "room size": "spatial.volume",
    "spaciousness": "spatial.volume",
    "symmetry": "spatial.symmetry",
    "furniture": "spatial.furniture",
    "wayfinding": "spatial.navigation",
    "room shape": "spatial.shape",
    "contour": "spatial.contour",
    "curved contour": "spatial.contour",
    "visual complexity": "spatial.complexity",

    # Acoustic
    "noise": "acoustic.noise",
    "background noise": "acoustic.noise",
    "occupied background noise": "acoustic.noise",
    "noise level": "acoustic.noise",
    "speech": "acoustic.speech",
    "speech intelligibility": "acoustic.speech",
    "speech privacy": "acoustic.speech",
    "music": "acoustic.music",
    "background music": "acoustic.music",
    "birdsong": "acoustic.nature_sound",
    "nature sound": "acoustic.nature_sound",
    "reverberation": "acoustic.reverberation",
    "RT60": "acoustic.reverberation",
    "acoustic environment": "acoustic.soundscape",
    "soundscape": "acoustic.soundscape",
    "acoustic absorption": "acoustic.reverberation",

    # Thermal
    "temperature": "thermal.temperature",
    "air temperature": "thermal.temperature",
    "ventilation": "thermal.ventilation",
    "natural ventilation": "thermal.ventilation",
    "HVAC": "thermal.ventilation",
    "humidity": "thermal.humidity",
    "relative humidity": "thermal.humidity",

    # Social-Spatial
    "seating": "social_spatial.seating",
    "seating arrangement": "social_spatial.seating",
    "occupancy": "social_spatial.occupancy",
    "privacy": "social_spatial.privacy",
    "territory": "social_spatial.territory",
    "personalization": "social_spatial.territory",

    # Person State
    "cognitive load": "person_state.cognitive_load",
    "mental load": "person_state.cognitive_load",
    "fatigue": "person_state.fatigue",
    "mental fatigue": "person_state.fatigue",
    "arousal": "person_state.arousal",
    "mood": "person_state.mood",
    "mood induction": "person_state.mood",
    "expertise": "person_state.expertise",
    "familiarity": "person_state.expertise",
    "gender": "person_state.expertise",  # demographic moderator

    # Cultural
    "culture": "cultural",
    "western": "cultural.western",
    "japanese": "cultural.east_asian",
    "korean": "cultural.east_asian",
    "chinese": "cultural.east_asian",

    # Temporal
    "time of day": "temporal_env.time_of_day",
    "morning": "temporal_env.time_of_day",
    "season": "temporal_env.season",
    "exposure duration": "temporal_env.exposure_duration",

    # Olfactory — must be specific enough to avoid false matches
    "smell": "olfactory",
    "scent": "olfactory",
    "fragrance": "olfactory",
    "odor type": "olfactory",
    "odor": "olfactory",
    "aroma": "olfactory",
    "lavender": "olfactory",
    "essential oil": "olfactory",
    "olfactory stimuli": "olfactory",

    # Additional common patterns from actual data
    "attractiveness": "spatial.complexity",       # aesthetic evaluation = complexity domain
    "antiquarian": "cultural",                     # historical preservation context

    # ──────────────────────────────────────────────────────────────
    # Root-domain leakage fixes (Sprint S1-2)
    # Lighting patterns that should not stay at "luminous" root
    # ──────────────────────────────────────────────────────────────
    "lighting condition": "luminous.artificial",
    "lighting conditions": "luminous.artificial",
    "fluorescent": "luminous.artificial",
    "LED": "luminous.artificial",
    "lighting mode": "luminous.artificial",
    "direct lighting": "luminous.artificial",
    "indirect lighting": "luminous.artificial",
    "direct/indirect lighting": "luminous.artificial",
    "lighting quality": "luminous.artificial",
    "lighting quality appraisal": "luminous.artificial",
    "lighting environment": "luminous.artificial",
    "light level": "luminous.illuminance",
    "illumination level": "luminous.illuminance",
    "illumination": "luminous.illuminance",
    "light intensity": "luminous.illuminance",
    "availability of choice over lighting": "luminous.personal_control",
    "colour chroma": "luminous.color",
    "colour value": "luminous.color",
    "color hue": "luminous.color",

    # Acoustic patterns that should not stay at "acoustic" root
    "acoustic intervention": "acoustic.noise",
    "acoustic condition": "acoustic.noise",
    "acoustic attribute": "acoustic.noise",
    "acoustic comfort": "acoustic.noise",
    "acoustic environment": "acoustic.soundscape",
    "sound signal": "acoustic.noise",
    "sound absorption": "acoustic.reverberation",
    "sound-absorption": "acoustic.reverberation",
    "sound-absorbent": "acoustic.reverberation",
    "sound level": "acoustic.noise",
    "aircraft sounds": "acoustic.noise",
    "interior sounds": "acoustic.noise",
    "knocking sound": "acoustic.noise",
    "footstep": "acoustic.noise",
    "audio information": "acoustic.noise",
    "natural sounds": "acoustic.nature_sound",
    "human sounds": "acoustic.speech",

    # Spatial patterns
    "virtual space": "spatial.layout",
    "learning space": "spatial.layout",
    "office layout": "spatial.layout",
    "indoor visual environment": "spatial.layout",
    "workspace planning": "spatial.layout",
    "modern buildings": "spatial.layout",
    "number of rooms": "spatial.volume",
    "landscape shape": "spatial.layout",

    # Nature / exposure patterns
    "exposure to nature": "natural.view_nature",
    "nature environment": "natural.view_nature",
    "urban planting": "natural.vegetation",
    "visit to": "natural.view_nature",
    "natural features": "natural.vegetation",
    "sit-stand desk": "spatial.furniture",
    "workstation": "spatial.furniture",
    "desk": "spatial.furniture",

    # Psychological constructs (V10 panel #5, #9)
    "perceived control": "person_state.perceived_control",
    "personal control": "person_state.perceived_control",
    "locus of control": "person_state.perceived_control",
    "environmental control": "person_state.perceived_control",
    "controllability": "person_state.perceived_control",
    "sense of control": "person_state.perceived_control",
    "fascination": "person_state.fascination",
    "soft fascination": "person_state.fascination",
    "hard fascination": "person_state.fascination",
    "involuntary attention": "person_state.fascination",
    "attention restoration": "person_state.fascination",
    "restorativeness": "person_state.restorativeness",
    "perceived restorativeness": "person_state.restorativeness",
    "restoration": "person_state.restorativeness",
    "stress recovery": "person_state.restorativeness",
    "being away": "person_state.restorativeness",
    "environmental complexity": "person_state.env_complexity",
    "stimulus richness": "person_state.env_complexity",
    "information rate": "person_state.env_complexity",
    "biophilia": "natural.biophilia",
    "biophilic design": "natural.biophilia",
    "nature connection": "natural.biophilia",
    "connectedness to nature": "natural.biophilia",
    "nature relatedness": "natural.biophilia",
}

# DV semantic map for common outcome strings
_DV_SEMANTIC_MAP: Dict[str, Tuple[str, DVAccessLevel, DVMeasurementType]] = {
    "visual comfort": ("affect.comfort.visual", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "thermal comfort": ("affect.comfort.thermal", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "acoustic comfort": ("affect.comfort.acoustic", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "indoor environmental comfort": ("affect.comfort.overall", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "overall satisfaction": ("affect.satisfaction.overall", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "visual satisfaction": ("affect.satisfaction.visual", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "overall workspace satisfaction": ("affect.satisfaction.overall", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "overall impression": ("affect.aesthetic.overall", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "perceived happiness": ("affect.positive.happiness", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "perceived sadness": ("affect.negative.sadness", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "perceived warmth": ("affect.perceived.warmth", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "student anxiety": ("affect.negative.anxiety", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "psychological stress level": ("affect.negative.stress", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "stress": ("affect.negative.stress", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "pleasantness rating": ("affect.positive.pleasantness", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "scenic beauty": ("affect.aesthetic.scenic_beauty", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "comfort scores": ("affect.comfort.overall", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "sound satisfaction": ("affect.comfort.acoustic", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "soundscape": ("affect.soundscape", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "appropriateness of soundscape": ("affect.soundscape", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "overall impression of soundscape": ("affect.soundscape", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "supportive quality": ("affect.aesthetic.supportive", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Performance
    "reaction time": ("cog.performance.reaction_time", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "task performance": ("cog.performance.task", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "mean error rate": ("cog.performance.accuracy", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),

    # Physiological
    "heart rate": ("cog.physiology.heart_rate", DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    "RMSSD": ("cog.physiology.hrv", DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),
    "cortisol": ("cog.physiology.cortisol", DVAccessLevel.AUTONOMIC, DVMeasurementType.PHYSIOLOGICAL),

    # Spatial behavior
    "place attachment": ("spatial_behavior.place_attachment", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "sense of belonging": ("spatial_behavior.belonging", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "sense of privacy": ("spatial_behavior.privacy", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "sense of territoriality": ("spatial_behavior.territoriality", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "intention to revisit": ("spatial_behavior.revisit_intention", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Cognition
    "creativity": ("cog.creativity", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "divergent thinking": ("cog.creativity.divergent", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "convergent thinking": ("cog.creativity.convergent", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "attention": ("cog.attention", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "concentration": ("cog.attention", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "memory": ("cog.memory", DVAccessLevel.BEHAVIORAL, DVMeasurementType.PERFORMANCE_TASK),
    "preference": ("affect.preference", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Affect — Wave 8b (V10 #9 Affect Researcher)
    "awe": ("affect.awe", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "sense of awe": ("affect.awe", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "fascination": ("affect.fascination", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "involuntary attention": ("affect.fascination", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "soft fascination": ("affect.fascination", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "restorativeness": ("affect.restoration.restorativeness", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "perceived restorativeness": ("affect.restoration.restorativeness", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "restoration": ("affect.restoration", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "stress recovery": ("affect.restoration", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "environmental satisfaction": ("affect.satisfaction", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "workplace satisfaction": ("affect.satisfaction", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "valence": ("affect.valence", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "affective valence": ("affect.valence", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),
    "arousal": ("affect.arousal_affect", DVAccessLevel.CONSCIOUS, DVMeasurementType.SELF_REPORT),

    # Neural — Wave 8d (V10 #6 Neuroscientist)
    "alpha power": ("neural.eeg.alpha_power", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "alpha oscillation": ("neural.eeg.alpha_power", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "frontal alpha asymmetry": ("neural.eeg.alpha_asymmetry", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "theta power": ("neural.eeg.theta_power", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "frontal midline theta": ("neural.eeg.theta_fm", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "beta power": ("neural.eeg.beta_power", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "gamma power": ("neural.eeg.gamma_power", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "eeg": ("neural.eeg", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "bold signal": ("neural.fmri_bold", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
    "brain activation": ("neural.fmri_bold", DVAccessLevel.NEURAL, DVMeasurementType.NEUROIMAGING),
}


# ══════════════════════════════════════════════════════════════════
# Measure Type Inference
# ══════════════════════════════════════════════════════════════════

_MEASURE_TYPE_KEYWORDS = {
    DVMeasurementType.SELF_REPORT: [
        "self-report", "self report", "rating", "scale", "questionnaire",
        "survey", "perceived", "satisfaction", "likert", "1-7", "1-5",
        "VAS", "subjective",
    ],
    DVMeasurementType.PHYSIOLOGICAL: [
        "heart rate", "HR", "RMSSD", "HRV", "cortisol", "EDA",
        "skin conductance", "blood pressure", "SpO2", "EMG",
        "salivary", "galvanic",
    ],
    DVMeasurementType.PERFORMANCE_TASK: [
        "reaction time", "accuracy", "error rate", "task",
        "performance", "score", "correct", "recall", "VMT", "BDST",
        "serial recall", "d-prime", "throughput",
    ],
    DVMeasurementType.NEUROIMAGING: [
        "fMRI", "EEG", "alpha", "beta", "theta", "BOLD",
        "MEG", "NIRS", "fNIRS",
    ],
    DVMeasurementType.OBSERVATIONAL: [
        "observer", "behavioral observation", "coded",
        "movement", "posture", "gaze",
    ],
}


def _infer_measure_type(text: str) -> DVMeasurementType:
    """Infer measurement type from DV text."""
    text_lower = text.lower()
    best = DVMeasurementType.UNSPECIFIED
    best_count = 0
    for mtype, keywords in _MEASURE_TYPE_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in text_lower)
        if count > best_count:
            best = mtype
            best_count = count
    return best


def _infer_access_level(text: str, measure_type: DVMeasurementType) -> DVAccessLevel:
    """Infer access level from text and measurement type."""
    if measure_type == DVMeasurementType.PHYSIOLOGICAL:
        return DVAccessLevel.AUTONOMIC
    if measure_type == DVMeasurementType.NEUROIMAGING:
        return DVAccessLevel.NEURAL
    if measure_type == DVMeasurementType.SELF_REPORT:
        return DVAccessLevel.CONSCIOUS
    if measure_type == DVMeasurementType.PERFORMANCE_TASK:
        return DVAccessLevel.BEHAVIORAL
    # Heuristic from text
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["perceived", "rating", "satisfaction", "subjective", "impression"]):
        return DVAccessLevel.CONSCIOUS
    if any(kw in text_lower for kw in ["performance", "accuracy", "reaction time", "behavior"]):
        return DVAccessLevel.BEHAVIORAL
    return DVAccessLevel.UNSPECIFIED


# ══════════════════════════════════════════════════════════════════
# Main Classifier
# ══════════════════════════════════════════════════════════════════

class IVDVClassifier:
    """
    Three-stage IV/DV classifier.
    
    Stage 1: Pattern matching (regex with parametric extraction)
    Stage 2: Enhanced keyword matching against taxonomy
    Stage 3: Pre-built semantic mapping table
    """

    def __init__(self, taxonomy: Optional[StimulusTaxonomy] = None):
        self.taxonomy = taxonomy or get_stimulus_taxonomy()
        self._cache: Dict[str, IVClassification] = {}
        self._dv_cache: Dict[str, DVClassification] = {}
        self._stats = {"pattern": 0, "keyword": 0, "semantic_map": 0, "tfidf": 0, "unclassified": 0}

    def classify_iv(self, raw_text: str) -> IVClassification:
        """Classify an IV (antecedent) string to a taxonomy node."""
        if not raw_text or not isinstance(raw_text, str):
            return IVClassification(
                node_id="unclassified", confidence=0.0,
                method="unclassified", raw_text=raw_text or ""
            )

        # Stage 0: NLP preprocessing (S2-2b — abbreviation expansion + normalization)
        try:
            from src.services.nlp_preprocessing import expand_abbreviations, normalize_iv_text
            processed_text = normalize_iv_text(raw_text)
            expanded_text = expand_abbreviations(raw_text)
        except ImportError:
            processed_text = raw_text.lower().strip()
            expanded_text = raw_text

        # Check cache with ORIGINAL text (consistent look-up)
        if raw_text in self._cache:
            return self._cache[raw_text]

        # Try classification on both original and expanded text
        result = self._classify_iv_inner(raw_text, processed_text, expanded_text)
        self._cache[raw_text] = result
        self._stats[result.method] += 1
        return result

    def _classify_iv_inner(self, raw_text: str, processed_text: str, expanded_text: str) -> IVClassification:
        """Internal: run 3-stage classification."""
        # Stage 1: Pattern matching (highest confidence)
        for pattern, node_id, confidence, attr_name in _IV_PATTERNS:
            m = pattern.search(raw_text)
            if m:
                attrs = {}
                if attr_name and m.groups():
                    try:
                        attrs[attr_name] = float(m.group(1))
                    except (ValueError, IndexError):
                        pass
                return IVClassification(
                    node_id=node_id, confidence=confidence,
                    method="pattern", raw_text=raw_text,
                    abstract_attributes=attrs
                )

        # Stage 3 before Stage 2: Semantic map (exact substring match)
        text_lower = raw_text.lower().strip()
        expanded_lower = expanded_text.lower().strip()
        # Try exact match first (original text)
        if text_lower in _IV_SEMANTIC_MAP:
            return IVClassification(
                node_id=_IV_SEMANTIC_MAP[text_lower], confidence=0.85,
                method="semantic_map", raw_text=raw_text
            )
        # Try substring containment (longest match first)
        best_map_match = None
        best_map_len = 0
        for key, node_id in _IV_SEMANTIC_MAP.items():
            if key in text_lower and len(key) > best_map_len:
                best_map_match = node_id
                best_map_len = len(key)
        if best_map_match and best_map_len >= 4:  # Min 4 chars to avoid spurious
            return IVClassification(
                node_id=best_map_match,
                confidence=min(0.80, 0.50 + 0.03 * best_map_len),
                method="semantic_map", raw_text=raw_text
            )

        # Try expanded text (abbreviation-expanded) against semantic map
        if expanded_lower != text_lower:
            if expanded_lower in _IV_SEMANTIC_MAP:
                return IVClassification(
                    node_id=_IV_SEMANTIC_MAP[expanded_lower], confidence=0.80,
                    method="semantic_map", raw_text=raw_text
                )
            for key, node_id in _IV_SEMANTIC_MAP.items():
                if key in expanded_lower and len(key) > best_map_len:
                    best_map_match = node_id
                    best_map_len = len(key)
            if best_map_match and best_map_len >= 4:
                return IVClassification(
                    node_id=best_map_match,
                    confidence=min(0.78, 0.48 + 0.03 * best_map_len),
                    method="semantic_map", raw_text=raw_text
                )

        # Stage 2: Enhanced keyword matching
        matches = self.taxonomy.match_keywords(raw_text)
        if matches:
            top_id, top_score = matches[0]
            # Prefer deeper (more specific) nodes among close scores
            top_matches = [(nid, s) for nid, s in matches if s >= top_score * 0.8]
            top_matches.sort(key=lambda x: -(self.taxonomy.get(x[0]).depth if self.taxonomy.get(x[0]) else 0))
            best_id = top_matches[0][0]
            best_score = top_matches[0][1]
            if best_score >= 0.15:  # At least 15% of keywords matched
                return IVClassification(
                    node_id=best_id, confidence=min(0.75, best_score),
                    method="keyword", raw_text=raw_text
                )

        # Stage 4: TF-IDF cosine similarity fallback (S3-4)
        # Uses taxonomy labels + keywords as "documents", computes cosine
        # similarity against the input text. Zero external dependencies.
        tfidf_result = self._tfidf_classify(raw_text)
        if tfidf_result:
            return tfidf_result

        # Unclassified — use raw text as node_id
        return IVClassification(
            node_id=raw_text, confidence=0.0,
            method="unclassified", raw_text=raw_text
        )

    def classify_dv(self, raw_text: str) -> DVClassification:
        """Classify a DV (consequent) string."""
        if raw_text in self._dv_cache:
            return self._dv_cache[raw_text]

        result = self._classify_dv_impl(raw_text)
        self._dv_cache[raw_text] = result
        return result

    def _classify_dv_impl(self, raw_text: str) -> DVClassification:
        """Internal: run DV classification."""
        # Stage 1: Pattern matching
        for pattern, node_id, confidence, access, measure in _DV_PATTERNS:
            if pattern.search(raw_text):
                return DVClassification(
                    node_id=node_id, confidence=confidence,
                    method="pattern", raw_text=raw_text,
                    access_level=access, measure_type=measure
                )

        # Stage 3: Semantic map
        text_lower = raw_text.lower().strip()
        if text_lower in _DV_SEMANTIC_MAP:
            node_id, access, measure = _DV_SEMANTIC_MAP[text_lower]
            return DVClassification(
                node_id=node_id, confidence=0.85,
                method="semantic_map", raw_text=raw_text,
                access_level=access, measure_type=measure
            )
        # Substring match
        best_match = None
        best_len = 0
        for key, (node_id, access, measure) in _DV_SEMANTIC_MAP.items():
            if key in text_lower and len(key) > best_len:
                best_match = (node_id, access, measure)
                best_len = len(key)
        if best_match and best_len >= 4:
            return DVClassification(
                node_id=best_match[0],
                confidence=min(0.80, 0.50 + 0.03 * best_len),
                method="semantic_map", raw_text=raw_text,
                access_level=best_match[1], measure_type=best_match[2]
            )

        # Infer measure type and access level even if no node match
        measure = _infer_measure_type(raw_text)
        access = _infer_access_level(raw_text, measure)

        return DVClassification(
            node_id=raw_text, confidence=0.0,
            method="unclassified", raw_text=raw_text,
            access_level=access, measure_type=measure
        )

    def batch_classify(
        self, findings: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Classify a batch of findings.
        
        Each finding should have 'antecedent' and 'consequent' keys.
        Returns enriched dicts with iv_node, dv_node, confidence, etc.
        """
        results = []
        for f in findings:
            iv = self.classify_iv(f.get("antecedent", ""))
            dv = self.classify_dv(f.get("consequent", ""))
            enriched = dict(f)
            enriched["iv_node"] = iv.node_id
            enriched["iv_confidence"] = iv.confidence
            enriched["iv_method"] = iv.method
            enriched["iv_abstract_attributes"] = iv.abstract_attributes
            enriched["dv_node"] = dv.node_id
            enriched["dv_confidence"] = dv.confidence
            enriched["dv_method"] = dv.method
            enriched["dv_access_level"] = dv.access_level.value
            enriched["dv_measure_type"] = dv.measure_type.value
            results.append(enriched)
        return results

    def _build_tfidf_index(self) -> None:
        """
        Build TF-IDF index from taxonomy node labels and keywords.
        Lazy-initialized on first call to _tfidf_classify.
        """
        import re as _re
        from collections import Counter as _Counter

        self._tfidf_docs: Dict[str, Dict[str, float]] = {}  # node_id → term→tfidf
        self._idf: Dict[str, float] = {}

        # Build corpus: each taxonomy node = one "document"
        corpus: Dict[str, List[str]] = {}
        for node_id, node in self.taxonomy._nodes.items():
            tokens = _re.findall(r'[a-z]+', node.label.lower())
            tokens += _re.findall(r'[a-z]+', ' '.join(node.keywords).lower())
            corpus[node_id] = tokens

        # Compute IDF
        n_docs = len(corpus)
        doc_freq: Dict[str, int] = _Counter()
        for tokens in corpus.values():
            for term in set(tokens):
                doc_freq[term] += 1

        import math as _math
        self._idf = {
            term: _math.log((n_docs + 1) / (df + 1)) + 1
            for term, df in doc_freq.items()
        }

        # Compute TF-IDF vectors
        for node_id, tokens in corpus.items():
            if not tokens:
                continue
            tf = _Counter(tokens)
            max_tf = max(tf.values()) if tf else 1
            tfidf_vec = {}
            for term, count in tf.items():
                tfidf_vec[term] = (0.5 + 0.5 * count / max_tf) * self._idf.get(term, 1.0)
            # Normalize
            norm = _math.sqrt(sum(v * v for v in tfidf_vec.values()))
            if norm > 0:
                tfidf_vec = {k: v / norm for k, v in tfidf_vec.items()}
            self._tfidf_docs[node_id] = tfidf_vec

    def _tfidf_classify(self, raw_text: str) -> Optional[IVClassification]:
        """
        Stage 4: TF-IDF cosine similarity classification.

        Falls back to cosine similarity between input text and taxonomy
        node label+keyword "documents". Returns None if no good match.
        """
        import re as _re
        import math as _math

        # Lazy init
        if not hasattr(self, '_tfidf_docs') or not self._tfidf_docs:
            try:
                self._build_tfidf_index()
            except Exception:
                return None

        # Tokenize input
        tokens = _re.findall(r'[a-z]+', raw_text.lower())
        if not tokens:
            return None

        # Build query TF-IDF vector
        from collections import Counter as _Counter
        tf = _Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        query_vec: Dict[str, float] = {}
        for term, count in tf.items():
            query_vec[term] = (0.5 + 0.5 * count / max_tf) * self._idf.get(term, 1.0)
        # Normalize
        norm = _math.sqrt(sum(v * v for v in query_vec.values()))
        if norm > 0:
            query_vec = {k: v / norm for k, v in query_vec.items()}
        else:
            return None

        # Compute cosine similarity against all nodes
        best_node = None
        best_sim = 0.0
        for node_id, doc_vec in self._tfidf_docs.items():
            sim = sum(query_vec.get(t, 0) * w for t, w in doc_vec.items())
            if sim > best_sim:
                best_sim = sim
                best_node = node_id

        # Minimum threshold: 0.25 cosine similarity
        if best_node and best_sim >= 0.25:
            # Prefer deeper nodes: check if a child has similar score
            parent_node = self.taxonomy.get(best_node)
            if parent_node:
                children = [n for n in self.taxonomy._nodes.values()
                            if n.parent_id == best_node]
                for child in children:
                    child_vec = self._tfidf_docs.get(child.node_id, {})
                    child_sim = sum(query_vec.get(t, 0) * w for t, w in child_vec.items())
                    if child_sim >= best_sim * 0.85:  # Within 15% of parent
                        best_node = child.node_id
                        best_sim = child_sim
                        break

            return IVClassification(
                node_id=best_node,
                confidence=min(0.65, best_sim),
                method="tfidf",
                raw_text=raw_text,
            )

        return None

    def classification_stats(self) -> Dict[str, Any]:
        """Return classification performance statistics."""
        total = sum(self._stats.values())
        return {
            "total_classified": total,
            "by_method": dict(self._stats),
            "classification_rate": (total - self._stats["unclassified"]) / max(total, 1),
            "iv_cache_size": len(self._cache),
            "dv_cache_size": len(self._dv_cache),
        }


# Singleton
_classifier: Optional[IVDVClassifier] = None

def get_classifier() -> IVDVClassifier:
    """Get or create the IV/DV classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = IVDVClassifier()
    return _classifier
