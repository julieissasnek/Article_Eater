"""
Task-Ecological Validity (Sprint 4b / Task 4b.3).

Scoring system for how well experimental tasks represent real building use.
Addresses the "passive observer fallacy" in CNFA research.

Five components, weighted:
- task_authenticity (0.30) — ecological task vs. artificial evaluation
- state_characterization (0.20) — incoming state measured?
- attentional_ecology (0.20) — attention naturally distributed?
- temporal_ecology (0.15) — exposure duration representative?
- social_ecology (0.15) — social context representative?

References:
- Ecological_Validity_CNFA_Background_Notes_V1.0.docx
- Missing_Fourth_Channel_Epistemic_Tier2_V1.0.docx
"""

from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class TaskClass(str, Enum):
    """
    Hierarchy of task authenticity.

    Higher values indicate more ecologically valid tasks.
    """
    EXPLICIT_EVALUATION = "explicit_evaluation"    # rate, judge, evaluate (0.2)
    LAB_COGNITIVE_TASK = "lab_cognitive_task"      # Stroop, digit span (0.4)
    SIMULATED_ECOLOGICAL = "simulated_ecological"  # VR wayfinding, TSST (0.6)
    REAL_TASK_CONTROLLED = "real_task_controlled"  # real work, real navigation (0.8)
    NATURAL_BEHAVIOR = "natural_behavior"          # POE, ESM, longitudinal (1.0)


class EffectPathway(str, Enum):
    """
    How the environmental effect operates (Canonical Decision 4).

    Canonical values per contracts/vocab/canonical_enums.json:
    - SUBPERSONAL: Non-conscious mechanisms (physiological, implicit priming)
    - PERSONAL_EPISTEMIC: Requires conscious engagement or evaluation
    - MIXED: Both pathways plausibly active

    Determines what methods are appropriate for measurement.
    """
    SUBPERSONAL = "subpersonal"                   # Below awareness, physiological/implicit
    PERSONAL_EPISTEMIC = "personal_epistemic"     # Requires conscious awareness/evaluation
    MIXED = "mixed"                               # Both pathways active
    # DEPRECATED aliases (Sprint 1.5, 2026-02-16):
    # - "explicit" → "personal_epistemic"
    # - "implicit_cognitive" → "personal_epistemic"
    # - "implicit_physiological" → "subpersonal"


class ClaimBifurcationType(str, Enum):
    """
    Type A / Type B claim bifurcation per Missing Fourth Channel.

    NOTE: This is NOT the same as epistemic ClaimType (causal, associational, etc.).
    This enum captures the evaluative-vs-functional distinction specific to CNFA
    ecological validity assessment.

    Type A claims (evaluative) are well-supported by standard CNFA paradigm.
    Type B claims (functional) require ecological evidence.

    Renamed from ClaimType → ClaimBifurcationType in Sprint 1.5 (2026-02-16)
    to avoid collision with canonical ClaimType in contracts/vocab/canonical_enums.json.
    """
    EVALUATIVE_RESPONSE = "evaluative_response"   # "People prefer X" (Type A)
    FUNCTIONAL_EFFECT = "functional_effect"       # "X reduces stress" (Type B)


# =============================================================================
# TASK AUTHENTICITY SCORES
# =============================================================================

TASK_AUTHENTICITY_SCORES: Dict[TaskClass, float] = {
    TaskClass.EXPLICIT_EVALUATION: 0.2,
    TaskClass.LAB_COGNITIVE_TASK: 0.4,
    TaskClass.SIMULATED_ECOLOGICAL: 0.6,
    TaskClass.REAL_TASK_CONTROLLED: 0.8,
    TaskClass.NATURAL_BEHAVIOR: 1.0,
}


# =============================================================================
# GENERALIZABILITY WARRANT WEIGHTS (D-PANEL.10)
# =============================================================================

# Modality-conditional weights for Type A → Type B claim generalization
# These weights reflect how well findings from each presentation modality
# generalize to real-world functional effects
GENERALIZABILITY_WEIGHTS: Dict[str, float] = {
    "real_building_controlled": 0.9,   # Nearly direct transfer
    "vr_cave": 0.7,                    # Good ecological validity (Fich et al.)
    "vr_hmd_room_scale": 0.6,          # Locomotion preserved
    "vr_hmd_stationary": 0.5,          # Visual immersion only
    "photographs_2d": 0.35,            # Limited to visual preference
}

# Default for unknown modalities
DEFAULT_GENERALIZABILITY_WEIGHT: float = 0.5


def get_generalizability_weight(modality_id: Optional[str]) -> float:
    """
    Get the generalizability warrant weight for a presentation modality.

    Per D-PANEL.10, Type A → Type B claim generalization depends on
    how well the presentation modality captures real-world experience.

    Args:
        modality_id: The presentation modality method_id (e.g., "photographs_2d")

    Returns:
        Generalizability weight in [0.35, 0.9]
    """
    if modality_id is None:
        return DEFAULT_GENERALIZABILITY_WEIGHT
    return GENERALIZABILITY_WEIGHTS.get(modality_id, DEFAULT_GENERALIZABILITY_WEIGHT)


# =============================================================================
# STATE CHARACTERIZATION
# =============================================================================

@dataclass
class StateCharacterization:
    """
    How well incoming participant state was characterized.

    Each dimension scored 0.0-1.0:
    - 0.0 = not addressed
    - 0.3 = mentioned as limitation
    - 0.7 = measured but not controlled
    - 1.0 = measured and controlled/counterbalanced
    """
    affective_state: float = 0.0      # Mood, stress level at entry
    cognitive_load: float = 0.0       # Prior cognitive demands
    goal_urgency: float = 0.0         # Time pressure, task importance
    familiarity: float = 0.0          # Prior exposure to environment type
    physical_state: float = 0.0       # Fatigue, hunger, caffeine
    social_context: float = 0.0       # Alone vs. with others

    @property
    def score(self) -> float:
        """Compute average state characterization score."""
        vals = [
            self.affective_state,
            self.cognitive_load,
            self.goal_urgency,
            self.familiarity,
            self.physical_state,
            self.social_context,
        ]
        return sum(vals) / len(vals)

    def to_dict(self) -> dict:
        return {
            "affective_state": self.affective_state,
            "cognitive_load": self.cognitive_load,
            "goal_urgency": self.goal_urgency,
            "familiarity": self.familiarity,
            "physical_state": self.physical_state,
            "social_context": self.social_context,
            "composite_score": self.score,
        }


# =============================================================================
# ECOLOGICAL VALIDITY COMPUTATION
# =============================================================================

DEFAULT_TASK_ECOLOGY_WEIGHTS: Dict[str, float] = {
    "task": 0.30,       # Task authenticity
    "state": 0.20,      # State characterization
    "attention": 0.20,  # Attentional ecology
    "temporal": 0.15,   # Temporal ecology
    "social": 0.15,     # Social ecology
}


def compute_task_ecological_validity(
    task_class: TaskClass,
    state: Optional[StateCharacterization] = None,
    attention_directed_to_features: bool = True,
    exposure_representative: bool = False,
    social_context_representative: bool = False,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Compute task-ecological validity score.

    This score captures how well the experimental task represents real
    building use. Low scores indicate the "passive observer fallacy":
    treating participants as spectators rather than goal-directed agents.

    Args:
        task_class: Type of task (explicit evaluation to natural behavior)
        state: State characterization object (defaults to zeros)
        attention_directed_to_features: True if attention explicitly directed
                                       to architectural features (REDUCES validity)
        exposure_representative: True if exposure duration matches real use
        social_context_representative: True if social context matches real use
        weights: Optional weight dictionary

    Returns:
        Ecological validity score in [0, 1]

    Example:
        >>> # Photo preference rating: low ecological validity
        >>> state_none = StateCharacterization()
        >>> score_low = compute_task_ecological_validity(
        ...     TaskClass.EXPLICIT_EVALUATION, state_none, True, False, False)
        >>> assert score_low < 0.3

        >>> # Real hospital wayfinding with state measurement
        >>> state_good = StateCharacterization(0.7, 0.7, 1.0, 1.0, 0.3, 0.7)
        >>> score_high = compute_task_ecological_validity(
        ...     TaskClass.REAL_TASK_CONTROLLED, state_good, False, True, True)
        >>> assert score_high > 0.7
    """
    if weights is None:
        weights = DEFAULT_TASK_ECOLOGY_WEIGHTS

    if state is None:
        state = StateCharacterization()

    # Task authenticity score
    task_score = TASK_AUTHENTICITY_SCORES[task_class]

    # Attention ecology: LOWER if attention explicitly directed to features
    # Real building users don't consciously evaluate architecture
    attention_score = 0.3 if attention_directed_to_features else 0.9

    # Temporal ecology: HIGHER if exposure matches real-world duration
    temporal_score = 0.9 if exposure_representative else 0.3

    # Social ecology: HIGHER if social context matches real-world
    social_score = 0.9 if social_context_representative else 0.2

    # Weighted combination
    validity = (
        weights["task"] * task_score +
        weights["state"] * state.score +
        weights["attention"] * attention_score +
        weights["temporal"] * temporal_score +
        weights["social"] * social_score
    )

    return max(0.0, min(1.0, validity))


def classify_task_from_text(methods_text: str) -> TaskClass:
    """
    Classify task type from methods section text.

    Uses keyword matching to identify task authenticity level.
    """
    text_lower = methods_text.lower()

    # Natural behavior indicators
    natural_keywords = [
        "post-occupancy", "poe", "experience sampling", "esm",
        "longitudinal", "field study", "naturalistic", "daily diary"
    ]
    if any(kw in text_lower for kw in natural_keywords):
        return TaskClass.NATURAL_BEHAVIOR

    # Real task controlled indicators
    real_task_keywords = [
        "real building", "actual office", "actual hospital",
        "workplace", "in situ", "real environment", "field experiment"
    ]
    if any(kw in text_lower for kw in real_task_keywords):
        return TaskClass.REAL_TASK_CONTROLLED

    # Simulated ecological indicators
    simulated_keywords = [
        "vr wayfinding", "virtual wayfinding", "navigation task",
        "tsst", "trier", "stress task", "simulated"
    ]
    if any(kw in text_lower for kw in simulated_keywords):
        return TaskClass.SIMULATED_ECOLOGICAL

    # Lab cognitive task indicators
    lab_keywords = [
        "stroop", "digit span", "working memory", "attention task",
        "cognitive task", "laboratory"
    ]
    if any(kw in text_lower for kw in lab_keywords):
        return TaskClass.LAB_COGNITIVE_TASK

    # Default to explicit evaluation (most common in CNFA)
    return TaskClass.EXPLICIT_EVALUATION


def get_pathway_for_construct(construct: str) -> EffectPathway:
    """
    Determine likely effect pathway for a given construct.

    Used to validate measurement method appropriateness.
    """
    construct_lower = construct.lower()

    # Explicit pathway constructs
    explicit_constructs = [
        "preference", "aesthetic", "beauty", "judgment",
        "evaluation", "rating", "satisfaction"
    ]
    if any(c in construct_lower for c in explicit_constructs):
        return EffectPathway.EXPLICIT

    # Implicit physiological constructs
    physio_constructs = [
        "cortisol", "hrv", "heart rate", "blood pressure",
        "eda", "skin conductance", "circadian", "melatonin"
    ]
    if any(c in construct_lower for c in physio_constructs):
        return EffectPathway.IMPLICIT_PHYSIOLOGICAL

    # Implicit cognitive constructs
    cognitive_constructs = [
        "attention restoration", "cognitive load", "wayfinding",
        "spatial cognition", "memory", "legibility"
    ]
    if any(c in construct_lower for c in cognitive_constructs):
        return EffectPathway.IMPLICIT_COGNITIVE

    # Default to mixed
    return EffectPathway.MIXED


def classify_claim_type(claim_text: str) -> ClaimType:
    """
    Classify claim as evaluative response (Type A) or functional effect (Type B).

    Type A: "People prefer/like/find attractive..."
    Type B: "X reduces stress/improves performance/affects health..."
    """
    text_lower = claim_text.lower()

    # Type A indicators (evaluative)
    evaluative_keywords = [
        "prefer", "like", "attractive", "pleasant", "beautiful",
        "aesthetic", "appealing", "rate", "perceive as", "judge"
    ]
    if any(kw in text_lower for kw in evaluative_keywords):
        return ClaimBifurcationType.EVALUATIVE_RESPONSE

    # Type B indicators (functional)
    functional_keywords = [
        "reduce", "improve", "affect", "increase", "decrease",
        "enhance", "facilitate", "impair", "health", "performance",
        "stress", "recovery", "productivity", "wellbeing"
    ]
    if any(kw in text_lower for kw in functional_keywords):
        return ClaimBifurcationType.FUNCTIONAL_EFFECT

    # Default to evaluative (more conservative)
    return ClaimBifurcationType.EVALUATIVE_RESPONSE
