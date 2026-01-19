"""
Environment Taxonomy for Article Eater Post-Quinean.

Sprint 7.1: Environment hierarchy with synonyms and antonyms.
Per expert panel (Bates): Create structured ontology for terminology resolution.

This module provides:
1. ENVIRONMENT_HIERARCHY - Hierarchical taxonomy of environment terms
2. Synonym resolution across terminology variations
3. Antonym detection for conflict resolution
4. Theory linkages for relevant constructs
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


# =============================================================================
# ENVIRONMENT TAXONOMY (Expert Panel: Bates)
# =============================================================================

ENVIRONMENT_HIERARCHY: Dict = {
    "spatial": {
        "_description": "Volumetric and geometric properties",
        "spatial.volume": {
            "_synonyms": ["ceiling height", "room volume", "volumetric capacity", "height"],
            "_related": ["spatial.openness"],
            "_measurement_units": ["meters", "cubic_meters", "feet"]
        },
        "spatial.openness": {
            "_synonyms": ["open plan", "visual openness", "spaciousness", "expansiveness", "open",
                        "spatial openness", "openness"],
            "_related": ["spatial.volume", "spatial.prospect"],
            "_antonym": "spatial.enclosure"
        },
        "spatial.enclosure": {
            "_synonyms": ["enclosed", "contained", "bounded", "closed", "confined",
                        "spatial enclosure", "enclosure"],
            "_antonym": "spatial.openness"
        },
        "spatial.prospect": {
            "_synonyms": ["view distance", "overlook", "vantage", "outlook", "vista"],
            "_related": ["spatial.openness"],
            "_theory_link": "prospect_refuge"
        },
        "spatial.refuge": {
            "_synonyms": ["shelter", "protected space", "nook", "alcove", "hideaway"],
            "_antonym": "spatial.prospect",
            "_theory_link": "prospect_refuge"
        }
    },
    "natural": {
        "_description": "Biophilic and natural elements",
        "natural.vegetation": {
            "_synonyms": ["plants", "greenery", "biophilic", "flora", "green", "foliage",
                        "indoor plants", "potted plants"],
            "_related": ["natural.views"]
        },
        "natural.water": {
            "_synonyms": ["water features", "fountains", "aquatic", "blue space",
                        "water views", "streams", "ponds"]
        },
        "natural.daylight": {
            "_synonyms": ["natural light", "sunlight", "daylighting", "natural illumination",
                        "daylit", "sun exposure"],
            "_related": ["sensory.lighting"]
        },
        "natural.views": {
            "_synonyms": ["nature views", "window views", "green views", "prospect",
                        "outdoor views", "scenic views", "natural scenery"],
            "_ecological_validity_note": "photos vs. real differ"
        },
        "natural.sounds": {
            "_synonyms": ["nature sounds", "birdsong", "water sounds", "natural soundscape"]
        }
    },
    "sensory": {
        "_description": "Non-visual environmental qualities",
        "sensory.lighting": {
            "_synonyms": ["artificial lighting", "illumination", "light levels", "lux",
                        "luminance", "lighting design", "electric lighting"],
            "_antonym": "sensory.darkness"
        },
        "sensory.darkness": {
            "_synonyms": ["dim", "dark", "low light", "shadowy"],
            "_antonym": "sensory.lighting"
        },
        "sensory.acoustics": {
            "_synonyms": ["noise", "sound", "acoustic quality", "sound masking",
                        "noise levels", "ambient sound", "soundscape"]
        },
        "sensory.thermal": {
            "_synonyms": ["temperature", "thermal comfort", "HVAC", "warmth", "coolness",
                        "climate control", "heating", "cooling"]
        },
        "sensory.air": {
            "_synonyms": ["air quality", "ventilation", "IAQ", "CO2", "fresh air",
                        "air circulation", "indoor air"]
        },
        "sensory.odor": {
            "_synonyms": ["smell", "scent", "aroma", "fragrance", "olfactory"]
        }
    },
    "config": {
        "_description": "Layout and spatial organization",
        "config.wayfinding": {
            "_synonyms": ["navigation", "legibility", "orientation", "signage",
                        "spatial navigation", "pathfinding"]
        },
        "config.complexity": {
            "_synonyms": ["spatial complexity", "layout complexity", "plan complexity"],
            "_note": "DISTINCT from aesthetic.complexity"
        },
        "config.connectivity": {
            "_synonyms": ["integration", "accessibility", "permeability", "circulation",
                        "spatial integration"]
        },
        "config.density": {
            "_synonyms": ["occupant density", "crowding", "occupancy", "people density"],
            "_note": "DISTINCT from building density",
            "_antonym": "config.spaciousness"
        },
        "config.spaciousness": {
            "_synonyms": ["uncrowded", "low density", "personal space"],
            "_antonym": "config.density"
        },
        "config.privacy": {
            "_synonyms": ["private", "enclosed office", "individual workspace"],
            "_antonym": "config.exposure"
        },
        "config.exposure": {
            "_synonyms": ["visible", "open office", "shared workspace", "lack of privacy"],
            "_antonym": "config.privacy"
        }
    },
    "aesthetic": {
        "_description": "Visual and stylistic properties",
        "aesthetic.complexity": {
            "_synonyms": ["visual complexity", "ornamentation", "detail", "decoration",
                        "visual richness", "ornate"],
            "_note": "DISTINCT from config.complexity",
            "_antonym": "aesthetic.simplicity"
        },
        "aesthetic.simplicity": {
            "_synonyms": ["minimal", "minimalist", "plain", "unadorned", "sparse"],
            "_antonym": "aesthetic.complexity"
        },
        "aesthetic.color": {
            "_synonyms": ["hue", "chromatic", "color temperature", "color scheme",
                        "palette", "colorful"]
        },
        "aesthetic.materials": {
            "_synonyms": ["texture", "surface", "materiality", "finish", "material palette"]
        },
        "aesthetic.order": {
            "_synonyms": ["symmetry", "pattern", "regularity", "organized", "neat", "tidy"],
            "_antonym": "aesthetic.disorder"
        },
        "aesthetic.disorder": {
            "_synonyms": ["asymmetry", "irregular", "messy", "cluttered", "chaotic"],
            "_antonym": "aesthetic.order"
        },
        "aesthetic.biomorphic": {
            "_synonyms": ["organic shapes", "curved", "natural forms", "flowing lines"]
        },
        "aesthetic.geometric": {
            "_synonyms": ["angular", "rectilinear", "straight lines", "rigid forms"]
        }
    }
}


# =============================================================================
# TAXONOMY UTILITIES
# =============================================================================

@dataclass
class EnvironmentMatch:
    """Result of matching text to environment taxonomy."""
    environment_id: str
    matched_term: str
    confidence: float  # 1.0 for exact, 0.9 for synonym, 0.7 for partial
    category: str


def _build_synonym_index() -> Dict[str, str]:
    """Build reverse index from synonyms to canonical IDs."""
    index = {}
    for category, items in ENVIRONMENT_HIERARCHY.items():
        if category.startswith("_"):
            continue
        for env_id, props in items.items():
            if env_id.startswith("_"):
                continue
            # Add canonical ID
            index[env_id.lower()] = env_id
            # Add synonyms
            for syn in props.get("_synonyms", []):
                index[syn.lower()] = env_id
    return index


def _build_antonym_index() -> Dict[str, str]:
    """Build antonym mapping from environment IDs."""
    index = {}
    for category, items in ENVIRONMENT_HIERARCHY.items():
        if category.startswith("_"):
            continue
        for env_id, props in items.items():
            if env_id.startswith("_"):
                continue
            antonym = props.get("_antonym")
            if antonym:
                index[env_id] = antonym
                # Bidirectional
                index[antonym] = env_id
    return index


# Pre-built indices
_SYNONYM_INDEX = _build_synonym_index()
_ANTONYM_INDEX = _build_antonym_index()


def resolve_environment_term(text: str) -> Optional[EnvironmentMatch]:
    """
    Resolve a text string to a canonical environment ID.

    Args:
        text: The text to match (e.g., "indoor plants", "spaciousness")

    Returns:
        EnvironmentMatch if found, None otherwise
    """
    text_lower = text.lower().strip()

    # Direct match
    if text_lower in _SYNONYM_INDEX:
        env_id = _SYNONYM_INDEX[text_lower]
        category = env_id.split(".")[0]
        return EnvironmentMatch(
            environment_id=env_id,
            matched_term=text,
            confidence=1.0 if env_id.lower() == text_lower else 0.9,
            category=category
        )

    # Partial match - check if text contains any known term
    for term, env_id in _SYNONYM_INDEX.items():
        if term in text_lower or text_lower in term:
            if len(term) >= 4 or len(text_lower) >= 4:  # Avoid short false matches
                category = env_id.split(".")[0]
                return EnvironmentMatch(
                    environment_id=env_id,
                    matched_term=term,
                    confidence=0.7,
                    category=category
                )

    return None


def get_environment_category(env_id: str) -> Optional[str]:
    """Get the category for an environment ID."""
    if "." in env_id:
        return env_id.split(".")[0]
    return None


def get_synonyms(env_id: str) -> List[str]:
    """Get all synonyms for an environment ID."""
    category = get_environment_category(env_id)
    if category and category in ENVIRONMENT_HIERARCHY:
        props = ENVIRONMENT_HIERARCHY[category].get(env_id, {})
        return props.get("_synonyms", [])
    return []


def are_antonyms(env_id1: str, env_id2: str) -> bool:
    """
    Check if two environment IDs are antonyms.

    Per expert panel (Bates): If environments are antonyms and effects are
    opposite, this is the SAME finding expressed differently, not a conflict.
    """
    return _ANTONYM_INDEX.get(env_id1) == env_id2


def get_antonym(env_id: str) -> Optional[str]:
    """Get the antonym for an environment ID, if one exists."""
    return _ANTONYM_INDEX.get(env_id)


def get_related(env_id: str) -> List[str]:
    """Get related environment IDs."""
    category = get_environment_category(env_id)
    if category and category in ENVIRONMENT_HIERARCHY:
        props = ENVIRONMENT_HIERARCHY[category].get(env_id, {})
        return props.get("_related", [])
    return []


def get_theory_link(env_id: str) -> Optional[str]:
    """Get the theory linked to an environment construct, if any."""
    category = get_environment_category(env_id)
    if category and category in ENVIRONMENT_HIERARCHY:
        props = ENVIRONMENT_HIERARCHY[category].get(env_id, {})
        return props.get("_theory_link")
    return None


def get_all_environment_ids() -> Set[str]:
    """Get all environment IDs in the taxonomy."""
    ids = set()
    for category, items in ENVIRONMENT_HIERARCHY.items():
        if category.startswith("_"):
            continue
        for env_id in items.keys():
            if not env_id.startswith("_"):
                ids.add(env_id)
    return ids


def get_all_synonyms() -> Dict[str, List[str]]:
    """Get all synonyms mapped by environment ID."""
    result = {}
    for env_id in get_all_environment_ids():
        synonyms = get_synonyms(env_id)
        if synonyms:
            result[env_id] = synonyms
    return result


def get_environment_description(env_id: str) -> Optional[str]:
    """Get the description for an environment category."""
    category = get_environment_category(env_id)
    if category and category in ENVIRONMENT_HIERARCHY:
        return ENVIRONMENT_HIERARCHY[category].get("_description")
    return None


# =============================================================================
# TERMINOLOGY VARIATION RESOLUTION
# =============================================================================

def normalize_environment_in_content(content: str) -> Tuple[str, List[EnvironmentMatch]]:
    """
    Identify and normalize environment terms in belief content.

    Args:
        content: The belief content text

    Returns:
        Tuple of (content with canonical terms, list of matches found)
    """
    matches = []
    content_lower = content.lower()

    # Find all matches, longest first to avoid subsuming shorter terms
    sorted_terms = sorted(_SYNONYM_INDEX.keys(), key=len, reverse=True)

    for term in sorted_terms:
        if term in content_lower:
            env_id = _SYNONYM_INDEX[term]
            # Check if we already matched this environment
            if not any(m.environment_id == env_id for m in matches):
                category = env_id.split(".")[0]
                matches.append(EnvironmentMatch(
                    environment_id=env_id,
                    matched_term=term,
                    confidence=0.9,
                    category=category
                ))

    return content, matches


def check_construct_distinction(env_id1: str, env_id2: str) -> Optional[str]:
    """
    Check if two environment IDs might be confused constructs.

    Per expert panel (Bates): Same word can mean different things in different
    contexts (e.g., "complexity" can be spatial or aesthetic).

    Returns:
        Warning message if disambiguation needed, None otherwise
    """
    # Check for complexity disambiguation
    complexity_ids = {"config.complexity", "aesthetic.complexity"}
    if env_id1 in complexity_ids and env_id2 in complexity_ids and env_id1 != env_id2:
        return (
            "Note: 'complexity' can refer to spatial/configurational complexity "
            "or aesthetic/visual complexity. These are distinct constructs."
        )

    # Check for density disambiguation
    if "density" in env_id1 and "density" in env_id2:
        return (
            "Note: 'density' can refer to occupant density (crowding) "
            "or building/structural density. Context determines meaning."
        )

    return None


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    "ENVIRONMENT_HIERARCHY",
    "EnvironmentMatch",
    "resolve_environment_term",
    "get_environment_category",
    "get_synonyms",
    "are_antonyms",
    "get_antonym",
    "get_related",
    "get_theory_link",
    "get_all_environment_ids",
    "get_all_synonyms",
    "get_environment_description",
    "normalize_environment_in_content",
    "check_construct_distinction",
]
