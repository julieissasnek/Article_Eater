"""
Prediction Error Subtype Classifier (Sprint 4 / Task 4.4).

Classifies prediction error claims by their subtype:
- FUNCTIONAL_PE: Affordance mismatch (what the space is for)
- NAVIGATIONAL_PE: Spatial model mismatch (where things are)
- SOCIAL_PE: Social script mismatch (who belongs, appropriate behavior)

References:
- Predictive processing framework (Clark, 2013; Friston, 2010)
- Environmental prediction errors (Epistemic Tier 2)
"""

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# KEYWORD LISTS
# =============================================================================

# Indicators that a claim involves prediction error
PE_INDICATORS = [
    "prediction error",
    "prediction-error",
    "predictive error",
    "surprise",
    "expectation violation",
    "violated expectation",
    "mismatch",
    "unexpected",
    "incongruent",
    "incongruence",
    "discrepancy",
    "deviation",
    "anomaly",
    "schema violation",
    "expectancy violation",
]

FUNCTIONAL_PE_KEYWORDS = [
    # Affordance-related
    "affordance",
    "affordances",
    "action possibility",
    "action possibilities",

    # Function/purpose
    "function",
    "functional",
    "purpose",
    "use",
    "using",
    "activity",
    "activities",
    "task",
    "what the space is for",
    "intended use",
    "designed for",

    # Interaction
    "interaction",
    "interact",
    "manipulation",
    "manipulate",
    "operate",
    "operating",
    "control",
    "interface",

    # Object/tool
    "object",
    "tool",
    "equipment",
    "device",
    "furniture",
    "fixture",
]

NAVIGATIONAL_PE_KEYWORDS = [
    # Wayfinding
    "wayfinding",
    "way-finding",
    "navigate",
    "navigation",
    "navigating",
    "route",
    "path",
    "direction",
    "directions",

    # Spatial
    "spatial",
    "layout",
    "configuration",
    "arrangement",
    "structure",
    "spatial structure",

    # Disorientation
    "lost",
    "disorientation",
    "disoriented",
    "confusion",
    "confused",
    "landmark",
    "landmarks",

    # Location
    "location",
    "locate",
    "locating",
    "position",
    "place",
    "where",
    "destination",

    # Maps/models
    "cognitive map",
    "mental map",
    "spatial model",
    "survey knowledge",
    "route knowledge",
]

SOCIAL_PE_KEYWORDS = [
    # Social norms
    "appropriate behavior",
    "appropriate behaviour",
    "social norm",
    "social norms",
    "normative",
    "etiquette",
    "propriety",

    # Belonging
    "who belongs",
    "belonging",
    "exclusion",
    "inclusion",
    "welcome",
    "unwelcome",

    # Institutional
    "institutional",
    "institution",
    "institutional meaning",
    "social coding",
    "social meaning",
    "symbolic",
    "status",

    # Identity
    "identity",
    "role",
    "roles",
    "social role",
    "social identity",

    # Expectation of others
    "social expectation",
    "social expectations",
    "behavioral script",
    "behavioural script",
    "social script",
    "social cue",
    "social cues",
]


# =============================================================================
# DATACLASS
# =============================================================================

@dataclass
class PEClassification:
    """
    Classification of a prediction error claim.

    Attributes:
        pe_subtype: One of "functional_pe", "navigational_pe", "social_pe", or None
        is_pe_claim: Whether this claim involves prediction error
        functional_score: Count of functional PE keywords
        navigational_score: Count of navigational PE keywords
        social_score: Count of social PE keywords
        confidence: Confidence in classification
        rationale: Brief explanation
    """
    pe_subtype: Optional[str]
    is_pe_claim: bool
    functional_score: int
    navigational_score: int
    social_score: int
    confidence: float
    rationale: str

    def to_dict(self) -> dict:
        return {
            "pe_subtype": self.pe_subtype,
            "is_pe_claim": self.is_pe_claim,
            "functional_score": self.functional_score,
            "navigational_score": self.navigational_score,
            "social_score": self.social_score,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


# =============================================================================
# CLASSIFICATION FUNCTION
# =============================================================================

def classify_pe_subtype(
    claim_text: str,
    return_details: bool = False
) -> Optional[str] | PEClassification:
    """
    Classify prediction error subtype for a claim.

    First checks if the claim involves prediction error at all.
    If so, classifies into one of three subtypes.

    Args:
        claim_text: The claim text to classify
        return_details: If True, return PEClassification object
                       If False (default), return subtype string or None

    Returns:
        PE subtype string ("functional_pe", "navigational_pe", "social_pe")
        OR None if not a PE claim
        OR PEClassification object if return_details=True

    Example:
        >>> classify_pe_subtype("wayfinding mismatch causes disorientation")
        "navigational_pe"
        >>> classify_pe_subtype("affordance prediction error in hospital design")
        "functional_pe"
        >>> classify_pe_subtype("cortisol levels increased")
        None  # Not a PE claim
    """
    text_lower = claim_text.lower()

    # First check if this is a PE claim at all
    is_pe_claim = any(indicator in text_lower for indicator in PE_INDICATORS)

    if not is_pe_claim:
        if return_details:
            return PEClassification(
                pe_subtype=None,
                is_pe_claim=False,
                functional_score=0,
                navigational_score=0,
                social_score=0,
                confidence=0.9,
                rationale="No prediction error indicators found",
            )
        return None

    # Count keyword matches for each subtype
    functional_score = sum(1 for kw in FUNCTIONAL_PE_KEYWORDS if kw in text_lower)
    navigational_score = sum(1 for kw in NAVIGATIONAL_PE_KEYWORDS if kw in text_lower)
    social_score = sum(1 for kw in SOCIAL_PE_KEYWORDS if kw in text_lower)

    scores = {
        "functional_pe": functional_score,
        "navigational_pe": navigational_score,
        "social_pe": social_score,
    }

    max_score = max(scores.values())

    if max_score == 0:
        # PE claim but no clear subtype - default to functional
        pe_subtype = "functional_pe"
        confidence = 0.4
        rationale = "PE indicators found but no clear subtype; defaulting to functional"
    else:
        # Take the highest scoring subtype
        pe_subtype = max(scores, key=scores.get)
        confidence = min(0.9, 0.5 + (max_score * 0.1))
        rationale = f"Highest score for {pe_subtype}: {max_score} keywords"

    if return_details:
        return PEClassification(
            pe_subtype=pe_subtype,
            is_pe_claim=True,
            functional_score=functional_score,
            navigational_score=navigational_score,
            social_score=social_score,
            confidence=confidence,
            rationale=rationale,
        )

    return pe_subtype


def get_pe_keywords(pe_subtype: str) -> list:
    """
    Get the keywords associated with a PE subtype.

    Useful for highlighting which terms triggered classification.
    """
    if pe_subtype == "functional_pe":
        return FUNCTIONAL_PE_KEYWORDS
    elif pe_subtype == "navigational_pe":
        return NAVIGATIONAL_PE_KEYWORDS
    elif pe_subtype == "social_pe":
        return SOCIAL_PE_KEYWORDS
    else:
        return []
