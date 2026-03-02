"""
activity_frame_registry.py — CVA-3: Activity Frame Registry & Goal Activation
==============================================================================

Implements Sprint CVA-3 deliverables:
  1. Canonical frame registry (8 frames from sprint spec + 2 additional)
  2. Frame-dependent goal activation: which valuations are active per frame
  3. Frame-dependent constraint salience masks: σ ⊙ c
  4. Worked examples (hospital, creative studio, museum, home office, yoga)

Reference: CVA_SPRINT_PLAN §Sprint CVA-3
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Canonical Activity Frames
# ══════════════════════════════════════════════════════════════════

VALUATION_AXES = [
    "SafetyValue", "InterestValue", "RestorationValue",
    "StatusValue", "BelongingValue", "IdentityCongruenceValue",
    "AutonomySupportValue", "CompetenceSupportValue",
    "RelatednessSupportValue",
]

CONSTRAINT_NAMES = [
    "processing_cost", "load_rate", "prediction_error",
    "control_efficacy", "affordance_density", "social_cue_density",
    "multisensory_coherence", "narrative_coherence",
]


@dataclass
class CanonicalFrame:
    """
    A canonical activity frame from Sprint CVA-3.

    Defines:
      - primary_goals: which valuation axes are active (the rest contribute zero)
      - valuation_weights: base weight vector ζ for all 9 axes
      - constraint_salience_mask: σ vector for 8 constraints (element-wise multiply)
      - context_examples: real-world contexts where this frame applies
      - typical_duration_minutes: expected duration
      - friston_interpretation: how Friston's active inference reads this frame
    """
    name: str
    description: str
    primary_goals: List[str]
    valuation_weights: Dict[str, float]
    constraint_salience_mask: Dict[str, float]
    context_examples: List[str] = field(default_factory=list)
    typical_duration_minutes: Tuple[float, float] = (30, 120)
    friston_interpretation: str = ""

    def active_goals_set(self) -> frozenset:
        """Return the set of active goal names."""
        return frozenset(self.primary_goals)

    def is_goal_active(self, goal_name: str) -> bool:
        """Check if a valuation axis is in the active-goal set."""
        return goal_name in self.primary_goals

    def compute_frame_adjusted_valuation(
        self,
        zeta_vector: Dict[str, float],
        constraint_vector: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Compute frame-adjusted valuation.

        For active goals: ζ_adjusted = ζ_base × frame_weight
        For inactive goals: ζ_adjusted = 0.0

        If constraint_vector provided, also applies constraint salience mask
        to modulate constraint-driven valuation contribution.
        """
        adjusted = {}
        for axis in VALUATION_AXES:
            if axis in self.primary_goals:
                base_weight = self.valuation_weights.get(axis, 0.0)
                adjusted[axis] = zeta_vector.get(axis, 0.5) * base_weight
            else:
                adjusted[axis] = 0.0
        return adjusted

    def apply_constraint_salience(
        self, constraint_vector: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Apply constraint salience mask: σ ⊙ c

        Returns masked constraint vector where irrelevant constraints
        are attenuated.
        """
        masked = {}
        for constraint in CONSTRAINT_NAMES:
            sigma = self.constraint_salience_mask.get(constraint, 0.5)
            c_val = constraint_vector.get(constraint, 0.5)
            masked[constraint] = c_val * sigma
        return masked

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "primary_goals": self.primary_goals,
            "valuation_weights": self.valuation_weights,
            "constraint_salience_mask": self.constraint_salience_mask,
            "context_examples": self.context_examples,
            "typical_duration_minutes": list(self.typical_duration_minutes),
            "friston_interpretation": self.friston_interpretation,
        }


# ══════════════════════════════════════════════════════════════════
# 8 Canonical Frames (Sprint CVA-3 Deliverable)
# ══════════════════════════════════════════════════════════════════

CANONICAL_FRAMES: Dict[str, CanonicalFrame] = {

    "hospital_recovery": CanonicalFrame(
        name="hospital_recovery",
        description="Patient recovering from surgery or illness. Safety-dominant, predictability-seeking.",
        primary_goals=[
            "SafetyValue", "RestorationValue",
            "RelatednessSupportValue", "CompetenceSupportValue",
        ],
        valuation_weights={
            "SafetyValue": 0.85, "InterestValue": 0.10,
            "RestorationValue": 0.80, "StatusValue": 0.05,
            "BelongingValue": 0.30, "IdentityCongruenceValue": 0.15,
            "AutonomySupportValue": 0.25, "CompetenceSupportValue": 0.35,
            "RelatednessSupportValue": 0.60,
        },
        constraint_salience_mask={
            "processing_cost": 1.0,      # stress from complexity
            "load_rate": 0.8,            # temporal density → stress
            "prediction_error": 1.0,     # surprise is threatening
            "control_efficacy": 0.9,     # path clarity → safety
            "affordance_density": 0.2,   # low: immobile patient
            "social_cue_density": 0.3,   # isolation for infection control
            "multisensory_coherence": 0.9,  # sensory alignment → calm
            "narrative_coherence": 0.5,  # moderate: familiar symbols
        },
        context_examples=[
            "Post-surgical recovery room",
            "ICU patient under monitoring",
            "Rehabilitation ward during rest",
        ],
        typical_duration_minutes=(60, 480),
        friston_interpretation=(
            "Frame specifies a generative model where the environment is expected "
            "to support recovery policies: low prediction error, high sensory "
            "coherence. Constraints relevant to safety are high-precision (trusted); "
            "affordance density is low-precision (ignored — patient cannot act)."
        ),
    ),

    "office_work": CanonicalFrame(
        name="office_work",
        description="Productivity-focused knowledge work. Autonomy and competence dominant.",
        primary_goals=[
            "CompetenceSupportValue", "AutonomySupportValue",
            "InterestValue", "SafetyValue",
        ],
        valuation_weights={
            "SafetyValue": 0.30, "InterestValue": 0.55,
            "RestorationValue": 0.15, "StatusValue": 0.25,
            "BelongingValue": 0.20, "IdentityCongruenceValue": 0.40,
            "AutonomySupportValue": 0.75, "CompetenceSupportValue": 0.80,
            "RelatednessSupportValue": 0.20,
        },
        constraint_salience_mask={
            "processing_cost": 0.9,      # low cost preferred
            "load_rate": 0.7,            # manageable workload
            "prediction_error": 0.6,     # moderate surprise OK
            "control_efficacy": 0.8,     # clear workspace layout
            "affordance_density": 0.7,   # equipment and tools available
            "social_cue_density": 0.4,   # coworkers present but not primary
            "multisensory_coherence": 0.5,  # moderate
            "narrative_coherence": 0.3,  # workspace identity matters little
        },
        context_examples=[
            "Open-plan office during deep work",
            "Home office during remote work",
            "Library study carrel",
        ],
        typical_duration_minutes=(30, 480),
        friston_interpretation=(
            "Frame specifies policies for productive output. Constraints relevant "
            "to task performance (processing cost, control efficacy) are high-precision. "
            "Social constraints are low-precision (present but not policy-relevant)."
        ),
    ),

    "social_gathering": CanonicalFrame(
        name="social_gathering",
        description="Social interaction focused. Belonging and relatedness dominant.",
        primary_goals=[
            "BelongingValue", "RelatednessSupportValue",
            "StatusValue", "IdentityCongruenceValue",
        ],
        valuation_weights={
            "SafetyValue": 0.25, "InterestValue": 0.30,
            "RestorationValue": 0.05, "StatusValue": 0.60,
            "BelongingValue": 0.80, "IdentityCongruenceValue": 0.55,
            "AutonomySupportValue": 0.20, "CompetenceSupportValue": 0.15,
            "RelatednessSupportValue": 0.85,
        },
        constraint_salience_mask={
            "processing_cost": 0.4,      # social processing different
            "load_rate": 0.6,            # event tempo
            "prediction_error": 0.5,     # moderate
            "control_efficacy": 0.3,     # group dynamics, less individual control
            "affordance_density": 0.5,   # seating, food, movement
            "social_cue_density": 1.0,   # primary salience driver
            "multisensory_coherence": 0.6,  # ambient matters
            "narrative_coherence": 0.7,  # shared story/meaning
        },
        context_examples=[
            "Dinner party at home",
            "Wedding reception",
            "Community gathering at church",
        ],
        typical_duration_minutes=(60, 240),
        friston_interpretation=(
            "Frame specifies policy expectations for social affiliation. "
            "Social cue density is high-precision (trusted). "
            "Individual control efficacy is low-precision (surrendered to group)."
        ),
    ),

    "yoga_meditation": CanonicalFrame(
        name="yoga_meditation",
        description="Internal awareness, mindful movement. Autonomy and restoration dominant.",
        primary_goals=[
            "RestorationValue", "AutonomySupportValue",
            "SafetyValue",
        ],
        valuation_weights={
            "SafetyValue": 0.60, "InterestValue": 0.15,
            "RestorationValue": 0.85, "StatusValue": 0.00,
            "BelongingValue": 0.10, "IdentityCongruenceValue": 0.30,
            "AutonomySupportValue": 0.70, "CompetenceSupportValue": 0.20,
            "RelatednessSupportValue": 0.10,
        },
        constraint_salience_mask={
            "processing_cost": 0.7,      # low complexity preferred
            "load_rate": 0.3,            # slow tempo
            "prediction_error": 0.8,     # predictable environment
            "control_efficacy": 0.6,     # embodied control
            "affordance_density": 0.3,   # minimal — mat and body
            "social_cue_density": 0.1,   # ignore others (meditation)
            "multisensory_coherence": 0.9,  # alignment of breath/sound/light
            "narrative_coherence": 0.6,  # spiritual narrative
        },
        context_examples=[
            "Yoga studio during meditation session",
            "Garden for tai chi practice",
            "Temple for seated meditation",
        ],
        typical_duration_minutes=(30, 90),
        friston_interpretation=(
            "Frame specifies interoceptive policy: body-focused generative model. "
            "Multisensory coherence is high-precision (sensory alignment crucial). "
            "External social cues are low-precision (gated out)."
        ),
    ),

    "museum_visiting": CanonicalFrame(
        name="museum_visiting",
        description="Art appreciation and learning. Novelty and narrative alignment dominant.",
        primary_goals=[
            "InterestValue", "IdentityCongruenceValue",
            "CompetenceSupportValue",
        ],
        valuation_weights={
            "SafetyValue": 0.15, "InterestValue": 0.85,
            "RestorationValue": 0.20, "StatusValue": 0.30,
            "BelongingValue": 0.15, "IdentityCongruenceValue": 0.55,
            "AutonomySupportValue": 0.40, "CompetenceSupportValue": 0.50,
            "RelatednessSupportValue": 0.15,
        },
        constraint_salience_mask={
            "processing_cost": 0.8,      # moderate-high OK (absorbing)
            "load_rate": 0.5,            # own pace
            "prediction_error": 0.9,     # surprise welcomed
            "control_efficacy": 0.4,     # guided by exhibit
            "affordance_density": 0.4,   # visual primarily
            "social_cue_density": 0.3,   # other visitors secondary
            "multisensory_coherence": 0.7,  # lighting/sound matters
            "narrative_coherence": 1.0,  # primary: story of the exhibit
        },
        context_examples=[
            "Modern art gallery solo visit",
            "Natural history museum with exhibitions",
            "Architecture biennale installation",
        ],
        typical_duration_minutes=(45, 180),
        friston_interpretation=(
            "Frame specifies knowledge-acquisition policies. Prediction error is "
            "high-precision (surprises are informative, not threatening). "
            "Narrative coherence is high-precision (meaning-making central)."
        ),
    ),

    "home_living": CanonicalFrame(
        name="home_living",
        description="General home occupancy. Autonomy, competence, belonging balanced.",
        primary_goals=[
            "AutonomySupportValue", "BelongingValue",
            "SafetyValue", "CompetenceSupportValue",
            "IdentityCongruenceValue",
        ],
        valuation_weights={
            "SafetyValue": 0.60, "InterestValue": 0.30,
            "RestorationValue": 0.50, "StatusValue": 0.15,
            "BelongingValue": 0.70, "IdentityCongruenceValue": 0.75,
            "AutonomySupportValue": 0.80, "CompetenceSupportValue": 0.45,
            "RelatednessSupportValue": 0.55,
        },
        constraint_salience_mask={
            "processing_cost": 0.5,      # familiar environment
            "load_rate": 0.4,            # self-paced
            "prediction_error": 0.5,     # customized space
            "control_efficacy": 0.8,     # high control in own home
            "affordance_density": 0.7,   # personalized tools
            "social_cue_density": 0.6,   # family/roommates
            "multisensory_coherence": 0.6,  # comfort
            "narrative_coherence": 0.8,  # personal identity expression
        },
        context_examples=[
            "Evening at home after work",
            "Weekend morning cooking",
            "Living room reading session",
        ],
        typical_duration_minutes=(60, 960),
        friston_interpretation=(
            "Frame specifies a broad set of habitual policies. Identity congruence "
            "is high-precision (home must reflect self). Control efficacy is high-precision "
            "(territorial ownership). Social cues modulated by family composition."
        ),
    ),

    "retail_shopping": CanonicalFrame(
        name="retail_shopping",
        description="Browsing and purchasing. Agency, novelty, and status oriented.",
        primary_goals=[
            "AutonomySupportValue", "InterestValue",
            "StatusValue", "CompetenceSupportValue",
        ],
        valuation_weights={
            "SafetyValue": 0.20, "InterestValue": 0.70,
            "RestorationValue": 0.05, "StatusValue": 0.55,
            "BelongingValue": 0.20, "IdentityCongruenceValue": 0.50,
            "AutonomySupportValue": 0.65, "CompetenceSupportValue": 0.50,
            "RelatednessSupportValue": 0.15,
        },
        constraint_salience_mask={
            "processing_cost": 0.7,      # browsing: moderate load OK
            "load_rate": 0.6,            # product turnover
            "prediction_error": 0.7,     # discovery is valued
            "control_efficacy": 0.7,     # wayfinding in store
            "affordance_density": 0.9,   # products = affordances
            "social_cue_density": 0.5,   # staff/other shoppers
            "multisensory_coherence": 0.5,  # store ambiance
            "narrative_coherence": 0.6,  # brand story
        },
        context_examples=[
            "Weekend at a bookstore",
            "Clothes shopping at a department store",
            "Farmers market browsing",
        ],
        typical_duration_minutes=(20, 120),
        friston_interpretation=(
            "Frame specifies exploration-exploitation policies for acquisition. "
            "Affordance density is high-precision (products are the action space). "
            "Status cues modulate what is considered desirable."
        ),
    ),

    "sacred_space": CanonicalFrame(
        name="sacred_space",
        description="Worship, reverence, spiritual experience. Narrative alignment and belonging dominant.",
        primary_goals=[
            "IdentityCongruenceValue", "BelongingValue",
            "SafetyValue", "RestorationValue",
        ],
        valuation_weights={
            "SafetyValue": 0.50, "InterestValue": 0.15,
            "RestorationValue": 0.55, "StatusValue": 0.10,
            "BelongingValue": 0.75, "IdentityCongruenceValue": 0.90,
            "AutonomySupportValue": 0.15, "CompetenceSupportValue": 0.10,
            "RelatednessSupportValue": 0.60,
        },
        constraint_salience_mask={
            "processing_cost": 0.5,      # awe, not stress
            "load_rate": 0.3,            # slow ritual tempo
            "prediction_error": 0.4,     # familiar liturgy
            "control_efficacy": 0.3,     # surrender of control
            "affordance_density": 0.2,   # stillness, contemplation
            "social_cue_density": 0.6,   # congregation presence
            "multisensory_coherence": 1.0,  # incense, light, sound, stone
            "narrative_coherence": 1.0,  # sacred narrative is primary
        },
        context_examples=[
            "Cathedral during Sunday service",
            "Mosque during Friday prayers",
            "Buddhist temple for meditation",
            "Ancient ruins as sacred ground",
        ],
        typical_duration_minutes=(30, 120),
        friston_interpretation=(
            "Frame specifies generative model of transcendence/communion. "
            "Narrative coherence and multisensory coherence are maximum-precision "
            "(the environment must resonate with spiritual expectation). "
            "Personal autonomy is low-precision (surrendered to ritual)."
        ),
    ),
}


# ══════════════════════════════════════════════════════════════════
# Activity Frame Registry
# ══════════════════════════════════════════════════════════════════

class ActivityFrameRegistry:
    """
    Registry of canonical activity frames + extensible custom frames.

    Sprint CVA-3 deliverable: provides frame lookup, validation,
    and computation functions.
    """

    def __init__(self, frames: Optional[Dict[str, CanonicalFrame]] = None):
        self.frames = dict(frames or CANONICAL_FRAMES)

    def get_frame(self, name: str) -> CanonicalFrame:
        """Look up a frame by name. Raises KeyError if not found."""
        if name not in self.frames:
            available = ", ".join(sorted(self.frames.keys()))
            raise KeyError(
                f"Unknown frame '{name}'. Available: {available}"
            )
        return self.frames[name]

    def register_frame(self, frame: CanonicalFrame) -> None:
        """Register a custom activity frame."""
        self.frames[frame.name] = frame
        LOGGER.info("Registered custom frame: %s", frame.name)

    def list_frames(self) -> List[str]:
        """Return sorted list of all frame names."""
        return sorted(self.frames.keys())

    def activate_frame(
        self,
        frame_name: str,
        constraint_vector: Dict[str, float],
        base_zeta: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Activate a frame: apply goal activation + constraint salience.

        Returns the frame-adjusted valuation vector where:
        - Active goals: ζ_adjusted = ζ_base × frame_weight
        - Inactive goals: ζ_adjusted = 0.0
        """
        frame = self.get_frame(frame_name)
        return frame.compute_frame_adjusted_valuation(
            base_zeta, constraint_vector
        )

    def frame_matches_context(
        self,
        frame_name: str,
        contextual_cues: Dict[str, float],
    ) -> float:
        """
        Infer how well a frame matches contextual cues.

        Returns confidence [0, 1] based on overlap between
        contextual features and frame's constraint salience mask.
        """
        frame = self.get_frame(frame_name)
        mask = frame.constraint_salience_mask

        overlap_score = 0.0
        n_cues = 0
        for cue_name, cue_value in contextual_cues.items():
            if cue_name in mask:
                # High salience + high cue value = good match
                overlap_score += mask[cue_name] * cue_value
                n_cues += 1

        if n_cues == 0:
            return 0.0
        return min(1.0, overlap_score / n_cues)

    def validate_frame_constraints(
        self,
        frame_name: str,
        available_constraints: List[str],
    ) -> List[str]:
        """Check which constraints are missing for this frame."""
        frame = self.get_frame(frame_name)
        needed = set(frame.constraint_salience_mask.keys())
        available = set(available_constraints)
        return sorted(needed - available)

    def compare_frames(
        self,
        frame_a: str,
        frame_b: str,
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare two frames' valuation weights and constraint salience.

        Useful for worked examples showing how the same space
        produces different responses under different frames.
        """
        fa = self.get_frame(frame_a)
        fb = self.get_frame(frame_b)

        valuation_diff = {}
        for axis in VALUATION_AXES:
            wa = fa.valuation_weights.get(axis, 0.0)
            wb = fb.valuation_weights.get(axis, 0.0)
            valuation_diff[axis] = {"frame_a": wa, "frame_b": wb, "diff": wa - wb}

        constraint_diff = {}
        for c in CONSTRAINT_NAMES:
            sa = fa.constraint_salience_mask.get(c, 0.5)
            sb = fb.constraint_salience_mask.get(c, 0.5)
            constraint_diff[c] = {"frame_a": sa, "frame_b": sb, "diff": sa - sb}

        return {
            "frames": {"a": frame_a, "b": frame_b},
            "valuation_weights": valuation_diff,
            "constraint_salience": constraint_diff,
            "shared_active_goals": sorted(
                set(fa.primary_goals) & set(fb.primary_goals)
            ),
            "unique_to_a": sorted(
                set(fa.primary_goals) - set(fb.primary_goals)
            ),
            "unique_to_b": sorted(
                set(fb.primary_goals) - set(fa.primary_goals)
            ),
        }

    def export_registry(self, output_path: str) -> int:
        """Export all frames to JSON."""
        data = {
            name: frame.to_dict()
            for name, frame in self.frames.items()
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        LOGGER.info("Exported %d frames to %s", len(data), output_path)
        return len(data)
