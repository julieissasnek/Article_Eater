"""
Epistemic Mediation Pathway Classifier (Sprint 4 / Task 4.3).

Classifies claims by their effect pathway:
- SUBPERSONAL: Direct physiological effects (no interpretation needed)
- PERSONAL_EPISTEMIC: Fully interpretation-mediated effects
- MIXED: Both pathways active

References:
- Missing Fourth Channel document (Epistemic Tier 2)
- Bermúdez (1995): Subpersonal vs personal level explanations
"""

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# KEYWORD LISTS
# =============================================================================

EPISTEMIC_KEYWORDS = [
    # Cognitive interpretation
    "interpretation",
    "comprehension",
    "understanding",
    "sense-making",
    "sensemaking",
    "meaning",
    "recognition",
    "categorization",
    "categorisation",

    # Spatial cognition
    "legibility",
    "wayfinding",
    "navigation",
    "spatial understanding",
    "cognitive map",
    "mental map",

    # Expectation/prediction
    "expectation",
    "prediction",
    "anticipation",
    "surprise",
    "mismatch",
    "violation",

    # Belief/judgment
    "belief",
    "judgment",
    "judgement",
    "appraisal",
    "evaluation",
    "assessment",
    "perception of",
    "perceived",

    # Social cognition
    "social meaning",
    "symbolic",
    "cultural meaning",
    "affordance",
    "function",
    "purpose",
]

SUBPERSONAL_KEYWORDS = [
    # Thermal
    "thermal",
    "temperature",
    "heat",
    "cold",
    "thermoregulation",

    # Circadian
    "circadian",
    "melatonin",
    "sleep-wake",
    "chronotype",
    "biological clock",

    # Acoustic (physical)
    "decibel",
    "dB",
    "acoustic",
    "sound pressure",
    "noise level",

    # Light (physical)
    "illuminance",
    "lux",
    "luminance",
    "spectral",
    "wavelength",

    # Air quality
    "air quality",
    "ventilation",
    "CO2",
    "carbon dioxide",
    "humidity",
    "particulate",

    # Physiological
    "cortisol",
    "physiological",
    "autonomic",
    "hormonal",
    "endocrine",
    "HPA",
    "heart rate",
    "blood pressure",
    "skin conductance",
    "galvanic",
    "electrodermal",

    # Direct sensory
    "retinal",
    "pupil",
    "vestibular",
]


# =============================================================================
# DATACLASS
# =============================================================================

@dataclass
class PathwayClassification:
    """
    Classification of a claim's effect pathway.

    Attributes:
        pathway: One of "subpersonal", "personal_epistemic", or "mixed"
        epistemic_score: Count of epistemic keywords found
        subpersonal_score: Count of subpersonal keywords found
        confidence: Confidence in classification (0.0 to 1.0)
        rationale: Brief explanation of classification
    """
    pathway: str
    epistemic_score: int
    subpersonal_score: int
    confidence: float
    rationale: str

    def to_dict(self) -> dict:
        return {
            "pathway": self.pathway,
            "epistemic_score": self.epistemic_score,
            "subpersonal_score": self.subpersonal_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


# =============================================================================
# CLASSIFICATION FUNCTION
# =============================================================================

def classify_pathway(
    claim_text: str,
    return_details: bool = False
) -> str | PathwayClassification:
    """
    Classify the epistemic mediation pathway for a claim.

    Per the three-pathway model:
    - SUBPERSONAL: Effect operates through direct physiological pathways
      (e.g., "Temperature affects circadian rhythm")
    - PERSONAL_EPISTEMIC: Effect is fully interpretation-mediated
      (e.g., "Spatial legibility affects wayfinding comprehension")
    - MIXED: Both pathways plausibly active
      (e.g., "Lighting color temperature affects mood interpretation")

    Args:
        claim_text: The claim text to classify
        return_details: If True, return PathwayClassification object
                       If False (default), return pathway string only

    Returns:
        Pathway string ("subpersonal", "personal_epistemic", or "mixed")
        OR PathwayClassification object if return_details=True

    Example:
        >>> classify_pathway("Temperature affects circadian rhythm")
        "subpersonal"
        >>> classify_pathway("Spatial legibility affects wayfinding comprehension")
        "personal_epistemic"
        >>> classify_pathway("Lighting color temperature affects mood interpretation")
        "mixed"
    """
    text_lower = claim_text.lower()

    # Count keyword matches
    epistemic_count = sum(1 for kw in EPISTEMIC_KEYWORDS if kw in text_lower)
    subpersonal_count = sum(1 for kw in SUBPERSONAL_KEYWORDS if kw in text_lower)

    # Determine pathway
    if epistemic_count > 0 and subpersonal_count > 0:
        pathway = "mixed"
        confidence = 0.8  # Clear evidence of both
        rationale = f"Found {epistemic_count} epistemic and {subpersonal_count} subpersonal indicators"
    elif epistemic_count > 0 and subpersonal_count == 0:
        pathway = "personal_epistemic"
        confidence = min(0.9, 0.5 + (epistemic_count * 0.1))
        rationale = f"Found {epistemic_count} epistemic indicators, no subpersonal"
    elif subpersonal_count > 0 and epistemic_count == 0:
        pathway = "subpersonal"
        confidence = min(0.9, 0.5 + (subpersonal_count * 0.1))
        rationale = f"Found {subpersonal_count} subpersonal indicators, no epistemic"
    else:
        # Default to mixed when uncertain
        pathway = "mixed"
        confidence = 0.3
        rationale = "No clear indicators found; defaulting to mixed"

    if return_details:
        return PathwayClassification(
            pathway=pathway,
            epistemic_score=epistemic_count,
            subpersonal_score=subpersonal_count,
            confidence=confidence,
            rationale=rationale,
        )

    return pathway


def get_pathway_keywords(pathway: str) -> list:
    """
    Get the keywords associated with a pathway type.

    Useful for highlighting which terms triggered classification.
    """
    if pathway == "subpersonal":
        return SUBPERSONAL_KEYWORDS
    elif pathway == "personal_epistemic":
        return EPISTEMIC_KEYWORDS
    else:  # mixed
        return EPISTEMIC_KEYWORDS + SUBPERSONAL_KEYWORDS
