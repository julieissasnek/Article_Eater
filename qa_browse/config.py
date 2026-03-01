"""
qa_browse.config — Domain configuration and constants.
======================================================

All configurable constants for the QA Browse System live here.
To add a new domain, update DOMAIN_CONFIG and TEMPLATE_DOMAIN_MAP.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

# ── Project Paths ──

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = DATA_DIR / "templates"
MOLECULES_DIR = DATA_DIR / "molecules"
QA_CACHE_DIR = DATA_DIR / "qa_cache"
ATTRIBUTES_DIR = DATA_DIR / "attributes"
EXTRACTIONS_DIR = DATA_DIR / "extractions"

MASTER_DOC_CANDIDATES = [
    PROJECT_ROOT / "docs" / "MASTER_DOC_CMR_2026-02-25.md",
    PROJECT_ROOT.parent / "MASTER_DOC_CMR_2026-02-25.md",
]


# ── Domain Configuration ──
# Each domain has an emoji, a hex color, and a human-readable label.

DOMAIN_CONFIG: Dict[str, Dict[str, str]] = {
    "visual": {"emoji": "👁️", "color": "#4A90D9", "label": "Visual"},
    "auditory": {"emoji": "👂", "color": "#9B59B6", "label": "Auditory"},
    "thermal": {"emoji": "🌡️", "color": "#E67E22", "label": "Thermal"},
    "haptic": {"emoji": "🤲", "color": "#27AE60", "label": "Haptic & Material"},
    "spatial": {"emoji": "🏗️", "color": "#1ABC9C", "label": "Spatial"},
    "circadian": {"emoji": "🌙", "color": "#F39C12", "label": "Circadian"},
    "social": {"emoji": "👥", "color": "#E74C3C", "label": "Social"},
    "creative": {"emoji": "💡", "color": "#8E44AD", "label": "Creativity"},
    "memory": {"emoji": "🧠", "color": "#2980B9", "label": "Memory & Learning"},
    "stress": {"emoji": "🫁", "color": "#16A085", "label": "Stress & Allostasis"},
    "multisensory": {"emoji": "🔗", "color": "#D35400", "label": "Multisensory"},
    "olfactory": {"emoji": "👃", "color": "#7D3C98", "label": "Olfactory"},
}


# ── Template → Domain Prefix Map ──
# Longest-prefix-first matching determines domain assignment.

TEMPLATE_DOMAIN_MAP: Dict[str, str] = {
    # Visual
    "VF": "visual", "VIEW": "visual", "COL": "visual", "L1": "visual",
    # Auditory
    "AUD": "auditory", "ACOUSTIC": "auditory", "BRECVEMA": "auditory",
    "NEURAL_MUSIC": "auditory", "PLEASURABLE": "auditory", "MS_ACOUSTIC": "auditory",
    # Thermal
    "THERMAL": "thermal", "MAT": "thermal", "IC_THERMAL": "thermal", "IC": "thermal",
    # Haptic
    "HAP": "haptic", "CT_AFFECTIVE": "haptic", "MATERIAL": "haptic",
    "NATURAL_MATERIAL": "haptic",
    # Spatial
    "SC": "spatial", "SPATIAL": "spatial", "PROXEMIC": "spatial",
    "THRESHOLD": "spatial", "ARCH_PROMENADE": "spatial", "ENCLOSURE": "spatial",
    "PRIVACY": "spatial", "TERRITORIAL": "spatial",
    # Circadian
    "L2": "circadian", "L3": "circadian", "L4": "circadian", "L5": "circadian",
    "CB": "circadian",
    # Social
    "SOC": "social", "XF_SOCIAL": "social", "CROSS_SOCIAL": "social",
    "COLLABORATIVE": "social",
    # Creative
    "CREA": "creative", "HC_CREATIVE": "creative", "CREATIVE": "creative",
    "PROCESSING": "creative", "INCUBATION": "creative",
    # Memory
    "ED": "memory", "MS_CONSOLIDATION": "memory", "MS_RIPPLE": "memory",
    "SN_CONTEXT": "memory",
    # Stress & Allostasis
    "AX": "stress", "ALLOSTATIC": "stress", "NM": "stress",
    "SALIENCE": "stress", "DT": "stress",
    # Multisensory
    "MSI": "multisensory", "CROSSMODAL": "multisensory", "CROSS_": "multisensory",
    "MULTIMODAL": "multisensory",
    # Olfactory
    "OLF": "olfactory",
}


# ── Bridge Warrant Labels ──
# (emoji, default_prior, one-line description)

BRIDGE_WARRANT_LABELS: Dict[str, Tuple[str, float, str]] = {
    "CONSTITUTIVE": ("🟢", 0.75, "Architectural feature IS the mechanism"),
    "MECHANISM": ("🔵", 0.60, "Complete causal pathway traced"),
    "EMPIRICAL_COVARIANCE": ("🔵", 0.60, "Strong replicated correlation"),
    "FUNCTIONAL": ("🟡", 0.50, "Same functional role, unspecified mechanism"),
    "CAPACITY": ("🟠", 0.45, "Demonstrated capacity, no direct evidence"),
    "ANALOGICAL": ("🔴", 0.35, "Structural analogy only"),
}


# ── Confidence Score Ranges ──

CONFIDENCE_RANGES = {
    "high": (0.50, 1.0, "#D5F5E3", "#196F3D"),
    "moderate": (0.35, 0.50, "#FEF9E7", "#7D6608"),
    "low": (0.20, 0.35, "#FADBD8", "#922B21"),
    "speculative": (0.0, 0.20, "#F2F3F4", "#7F8C8D"),
}


# ── Domain Browse Descriptions ──
# Short descriptions shown on browse cards.

DOMAIN_DESCRIPTIONS: Dict[str, str] = {
    "visual": "Prediction error, fractal scaling, visual complexity, nature views",
    "auditory": "Soundscapes, music emotion (BRECVEMA), reverberation, acoustics",
    "thermal": "Adaptive comfort, thermal PE, interoceptive body budget",
    "spatial": "Wayfinding, isovists, prospect-refuge, enclosure, spatial integration",
    "circadian": "Daylight, melanopic irradiance, melatonin, sleep quality",
    "haptic": "Surfaces, materials, CT-afferent touch, texture perception",
    "stress": "Allostatic load, neuromodulators, HPA axis, DMN/TPN dynamics",
    "creative": "Incubation architecture, divergent thinking, network switching",
    "social": "Proxemics, privacy-encounter gradient, social affordance, density",
    "memory": "Episodic encoding, consolidation, schema, hippocampal replay",
    "multisensory": "Crossmodal binding, congruence, inverse effectiveness",
    "olfactory": "Olfactory prediction error, scent-space transitions",
}
