"""
Per-Claim Validity Scoring (Sprint 4b / Task 4b.6).

Computes three validity scores for each extracted claim:
- presentation_validity: How well does the stimulus capture real architecture?
- measurement_validity: How well does the instrument capture the construct?
- task_ecological_validity: How well does the task represent real use?

Generates automatic challenges when methods don't match claims.

References:
- Methodological_Validity_Framework_Tier2b_V1.0.docx
- Five Types of Automatic Argumentative Challenges
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict

from src.methods.registry import MethodRegistry, MethodEntry
from src.methods.method_identifier import MethodIdentificationResult
from src.methods.task_ecology import (
    TaskClass,
    ClaimType,
    EffectPathway,
    compute_task_ecological_validity,
    classify_claim_type,
    get_pathway_for_construct,
)


# =============================================================================
# AUTO-CHALLENGE TYPES
# =============================================================================

AUTO_CHALLENGE_TYPES = {
    "temporal_misalignment": "Instrument temporal dynamics don't match sampling protocol",
    "construct_presentation_mismatch": "Presentation modality strips channels required for construct",
    "vr_confound_uncontrolled": "VR study without cybersickness measurement/control",
    "single_modality": "Only one measurement modality used (no triangulation)",
    "exposure_duration_inadequate": "Exposure too short for construct to manifest",
    "attention_directed": "Explicit evaluation task for implicit effect claim",
}

# Constructs that require specific presentation channels
CONSTRUCT_CHANNEL_REQUIREMENTS: Dict[str, List[str]] = {
    "wayfinding": ["locomotion", "spatial_updating", "proprioception"],
    "spatial_cognition": ["locomotion", "vestibular", "proprioception"],
    "thermal_comfort": ["thermal"],
    "acoustic_experience": ["acoustic"],
    "material_preference": ["haptic", "high_resolution"],
    "social_behavior": ["social_presence", "full_body"],
    "stress_response": [],  # No specific channel required
    "preference": [],  # Works with visual only
    "aesthetic_judgment": [],  # Works with visual only
}

# What channels each presentation modality provides
MODALITY_CHANNELS: Dict[str, List[str]] = {
    "photographs_2d": ["visual_central"],
    "vr_hmd_stationary": ["visual_immersive", "head_tracking"],
    "vr_hmd_room_scale": ["visual_immersive", "head_tracking", "locomotion", "proprioception"],
    "vr_cave": ["visual_immersive", "peripheral_vision", "locomotion", "proprioception"],
    "real_building_controlled": [
        "visual_immersive", "locomotion", "proprioception", "vestibular",
        "thermal", "acoustic", "haptic", "olfactory", "social_presence"
    ],
}


# =============================================================================
# RESULT DATACLASS
# =============================================================================

@dataclass
class ClaimValidityResult:
    """
    Validity assessment for a single claim.

    Includes three validity scores and any auto-generated challenges.
    """
    presentation_validity: float = 0.0
    measurement_validity: float = 0.0
    task_ecological_validity: float = 0.0
    composite_validity: float = 0.0
    auto_challenges: List[str] = field(default_factory=list)
    challenge_details: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "presentation_validity": self.presentation_validity,
            "measurement_validity": self.measurement_validity,
            "task_ecological_validity": self.task_ecological_validity,
            "composite_validity": self.composite_validity,
            "auto_challenges": self.auto_challenges,
            "challenge_details": self.challenge_details,
        }

    @property
    def has_challenges(self) -> bool:
        return len(self.auto_challenges) > 0


# =============================================================================
# VALIDITY COMPUTATION
# =============================================================================

def _compute_presentation_validity(
    construct: str,
    modality_id: Optional[str],
    registry: Optional[MethodRegistry] = None
) -> float:
    """
    Compute how well the presentation modality captures the construct.

    Uses construct_validity_map from registry if available,
    otherwise estimates from channel requirements.
    """
    if modality_id is None:
        return 0.5  # Unknown modality, neutral score

    # Try registry lookup first
    if registry:
        entry = registry.get(modality_id)
        if entry and entry.construct_validity_map:
            # Look for construct in validity map
            validity = entry.get_construct_validity(construct)
            if validity > 0:
                return validity

    # Fallback: check channel requirements
    required_channels = CONSTRUCT_CHANNEL_REQUIREMENTS.get(construct.lower(), [])
    provided_channels = MODALITY_CHANNELS.get(modality_id, [])

    if not required_channels:
        # No specific requirements, assume modality is adequate
        return 0.7

    # Score based on channel coverage
    matched = sum(1 for c in required_channels if c in provided_channels)
    if len(required_channels) > 0:
        return matched / len(required_channels)

    return 0.5


def _compute_measurement_validity(
    construct: str,
    instruments: List[Dict],
    registry: Optional[MethodRegistry] = None
) -> float:
    """
    Compute how well the instruments measure the construct.

    Considers:
    - Construct validity map scores
    - Number of instruments (triangulation)
    """
    if not instruments:
        return 0.3  # No instruments found

    max_validity = 0.0

    for instrument in instruments:
        method_id = instrument["method_id"]

        if registry:
            entry = registry.get(method_id)
            if entry:
                validity = entry.get_construct_validity(construct)
                max_validity = max(max_validity, validity)

    # Bonus for multiple instruments (triangulation)
    if len(instruments) > 1:
        max_validity = min(1.0, max_validity + 0.1)

    return max_validity if max_validity > 0 else 0.5


def _generate_auto_challenges(
    claim_text: str,
    construct: str,
    methods_info: MethodIdentificationResult,
    claim_type: ClaimType,
    registry: Optional[MethodRegistry] = None
) -> List[str]:
    """
    Generate automatic argumentative challenges for a claim.

    Checks for five types of methodological issues:
    1. Temporal misalignment
    2. Construct-presentation mismatch
    3. VR confound uncontrolled
    4. Single modality measurement
    5. Attention directed for implicit claim
    """
    challenges = []

    # 1. Temporal misalignment (from method identification)
    if methods_info.temporal_alignment_flags:
        challenges.extend(methods_info.temporal_alignment_flags)

    # 2. Construct-presentation mismatch
    if methods_info.presentation_modality:
        modality_id = methods_info.presentation_modality["method_id"]
        required_channels = CONSTRUCT_CHANNEL_REQUIREMENTS.get(construct.lower(), [])
        provided_channels = MODALITY_CHANNELS.get(modality_id, [])

        missing_channels = [c for c in required_channels if c not in provided_channels]
        if missing_channels:
            challenges.append("construct_presentation_mismatch")

    # 3. VR confound uncontrolled
    vr_modalities = {"vr_hmd_stationary", "vr_hmd_room_scale", "vr_cave"}
    if methods_info.presentation_modality:
        modality_id = methods_info.presentation_modality["method_id"]
        if modality_id in vr_modalities:
            # Check if cybersickness was measured
            instrument_ids = [i["method_id"] for i in methods_info.instruments_found]
            cybersickness_measured = any(
                "cybersickness" in str(methods_info.to_dict()).lower()
                for _ in [1]
            )
            # Check for SSQ or similar
            ssq_terms = ["ssq", "simulator sickness", "cybersickness", "motion sickness"]
            if not any(term in str(methods_info.to_dict()).lower() for term in ssq_terms):
                challenges.append("vr_confound_uncontrolled")

    # 4. Single modality measurement
    if len(methods_info.instruments_found) == 1:
        challenges.append("single_modality")

    # 5. Attention directed for implicit effect claim
    effect_pathway = get_pathway_for_construct(construct)
    if effect_pathway in [EffectPathway.IMPLICIT_COGNITIVE, EffectPathway.IMPLICIT_PHYSIOLOGICAL]:
        if methods_info.task_class == TaskClass.EXPLICIT_EVALUATION:
            challenges.append("attention_directed")

    # 6. Exposure duration inadequate (if we can detect it)
    # This would require parsing exposure duration from text

    return challenges


def compute_claim_validity(
    claim_text: str,
    construct: str,
    methods_info: MethodIdentificationResult,
    registry: Optional[MethodRegistry] = None,
    weights: Optional[Dict[str, float]] = None
) -> ClaimValidityResult:
    """
    Compute validity scores and auto-challenges for a claim.

    This is the main entry point for claim validity assessment.

    Args:
        claim_text: The claim statement
        construct: The construct being measured/claimed
        methods_info: Result from identify_methods()
        registry: Optional MethodRegistry for lookup
        weights: Optional weights for composite score

    Returns:
        ClaimValidityResult with three validity scores and auto-challenges

    Example:
        >>> methods = identify_methods("We used photographs to assess wayfinding...")
        >>> validity = compute_claim_validity(
        ...     "Spatial complexity reduces wayfinding efficiency",
        ...     "wayfinding",
        ...     methods
        ... )
        >>> assert "construct_presentation_mismatch" in validity.auto_challenges
    """
    if weights is None:
        weights = {
            "presentation": 0.35,
            "measurement": 0.35,
            "task_ecological": 0.30,
        }

    # Get modality ID if available
    modality_id = None
    if methods_info.presentation_modality:
        modality_id = methods_info.presentation_modality["method_id"]

    # Compute three validity scores
    presentation_validity = _compute_presentation_validity(
        construct, modality_id, registry
    )

    measurement_validity = _compute_measurement_validity(
        construct, methods_info.instruments_found, registry
    )

    task_eco_validity = compute_task_ecological_validity(
        methods_info.task_class,
        methods_info.state_measured,
        attention_directed_to_features=(methods_info.task_class == TaskClass.EXPLICIT_EVALUATION),
    )

    # Composite score
    composite = (
        weights["presentation"] * presentation_validity +
        weights["measurement"] * measurement_validity +
        weights["task_ecological"] * task_eco_validity
    )

    # Classify claim type
    claim_type = classify_claim_type(claim_text)

    # Generate auto-challenges
    challenges = _generate_auto_challenges(
        claim_text, construct, methods_info, claim_type, registry
    )

    # Build challenge details
    challenge_details = {
        c: AUTO_CHALLENGE_TYPES.get(c, "Unknown challenge type")
        for c in challenges
    }

    return ClaimValidityResult(
        presentation_validity=presentation_validity,
        measurement_validity=measurement_validity,
        task_ecological_validity=task_eco_validity,
        composite_validity=composite,
        auto_challenges=challenges,
        challenge_details=challenge_details,
    )
