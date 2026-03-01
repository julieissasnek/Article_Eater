"""
activity_frame.py — Activity Frame + Precision Modulation
=========================================================

An ActivityFrame represents the task/goal context that modulates
CVA constraint perception and valuation via precision weighting.

From spec §2.3: precision(ψ) controls how reliably valuations
drive behavior. Activity frames set the precision regime.

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §2.3
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import json


# ──────────────────────────────────────────────────────────────────
# Activity Frame Enum
# ──────────────────────────────────────────────────────────────────

class ActivityFrameType(Enum):
    """
    Canonical activity frames that set precision regimes.

    High precision = behavior tightly coupled to valuations
    Low precision  = exploration, serendipity, loose coupling
    """
    GOAL_DIRECTED = "goal_directed"       # Task-focused (high precision)
    EXPLORATORY = "exploratory"           # Wandering/browsing (low precision)
    RESTORATIVE = "restorative"           # Rest/recovery (medium precision)
    SOCIAL = "social"                     # Social interaction (variable)
    CREATIVE = "creative"                 # Making/ideation (medium-low)
    EMERGENCY = "emergency"              # Threat response (maximum precision)
    HABITUAL = "habitual"                 # Automated routine (minimal precision)
    CONTEMPLATIVE = "contemplative"       # Reflection/meditation (low precision)
    PLAYFUL = "playful"                   # Play/experimentation (low precision)
    WAYFINDING = "wayfinding"            # Navigation (high spatial precision)


# ──────────────────────────────────────────────────────────────────
# Precision Profile
# ──────────────────────────────────────────────────────────────────

@dataclass
class PrecisionProfile:
    """
    Per-dimension precision weights for an activity frame.

    Higher precision on a valuation dimension means behavior is
    more tightly coupled to that dimension's value signal.
    """
    # Precision weights per valuation dimension [0, 1]
    safety: float = 0.5
    interest: float = 0.5
    restoration: float = 0.5
    status: float = 0.5
    belonging: float = 0.5
    identity: float = 0.5
    autonomy: float = 0.5
    competence: float = 0.5
    relatedness: float = 0.5

    # Global precision multiplier (inverse temperature β)
    global_precision: float = 1.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "safety": self.safety,
            "interest": self.interest,
            "restoration": self.restoration,
            "status": self.status,
            "belonging": self.belonging,
            "identity": self.identity,
            "autonomy": self.autonomy,
            "competence": self.competence,
            "relatedness": self.relatedness,
            "global_precision": self.global_precision,
        }


# Default precision profiles per activity frame
FRAME_PRECISION_PROFILES: Dict[ActivityFrameType, PrecisionProfile] = {
    ActivityFrameType.GOAL_DIRECTED: PrecisionProfile(
        safety=0.3, interest=0.4, restoration=0.1,
        status=0.3, belonging=0.2, identity=0.5,
        autonomy=0.6, competence=0.9, relatedness=0.2,
        global_precision=1.8,
    ),
    ActivityFrameType.EXPLORATORY: PrecisionProfile(
        safety=0.3, interest=0.9, restoration=0.2,
        status=0.1, belonging=0.3, identity=0.3,
        autonomy=0.7, competence=0.3, relatedness=0.3,
        global_precision=0.8,
    ),
    ActivityFrameType.RESTORATIVE: PrecisionProfile(
        safety=0.6, interest=0.1, restoration=0.9,
        status=0.0, belonging=0.3, identity=0.2,
        autonomy=0.4, competence=0.0, relatedness=0.4,
        global_precision=1.0,
    ),
    ActivityFrameType.SOCIAL: PrecisionProfile(
        safety=0.3, interest=0.4, restoration=0.1,
        status=0.6, belonging=0.8, identity=0.5,
        autonomy=0.3, competence=0.2, relatedness=0.9,
        global_precision=1.2,
    ),
    ActivityFrameType.CREATIVE: PrecisionProfile(
        safety=0.1, interest=0.8, restoration=0.1,
        status=0.2, belonging=0.1, identity=0.7,
        autonomy=0.8, competence=0.7, relatedness=0.2,
        global_precision=0.7,
    ),
    ActivityFrameType.EMERGENCY: PrecisionProfile(
        safety=1.0, interest=0.0, restoration=0.0,
        status=0.0, belonging=0.0, identity=0.0,
        autonomy=0.2, competence=0.3, relatedness=0.0,
        global_precision=2.5,
    ),
    ActivityFrameType.HABITUAL: PrecisionProfile(
        safety=0.2, interest=0.1, restoration=0.2,
        status=0.1, belonging=0.1, identity=0.1,
        autonomy=0.1, competence=0.1, relatedness=0.1,
        global_precision=0.4,
    ),
    ActivityFrameType.CONTEMPLATIVE: PrecisionProfile(
        safety=0.2, interest=0.3, restoration=0.6,
        status=0.0, belonging=0.2, identity=0.6,
        autonomy=0.5, competence=0.1, relatedness=0.3,
        global_precision=0.6,
    ),
    ActivityFrameType.PLAYFUL: PrecisionProfile(
        safety=0.2, interest=0.9, restoration=0.1,
        status=0.1, belonging=0.5, identity=0.2,
        autonomy=0.6, competence=0.6, relatedness=0.5,
        global_precision=0.7,
    ),
    ActivityFrameType.WAYFINDING: PrecisionProfile(
        safety=0.5, interest=0.2, restoration=0.1,
        status=0.0, belonging=0.1, identity=0.1,
        autonomy=0.7, competence=0.8, relatedness=0.1,
        global_precision=1.5,
    ),
}


# ──────────────────────────────────────────────────────────────────
# Activity Frame
# ──────────────────────────────────────────────────────────────────

@dataclass
class ActivityFrame:
    """
    Task/goal context for CVA evaluation.

    Determines precision regime (how tightly valuations drive behavior)
    and which constraint dimensions are most salient.
    """
    frame_type: ActivityFrameType = ActivityFrameType.EXPLORATORY
    precision: Optional[PrecisionProfile] = None
    duration_minutes: Optional[float] = None
    description: str = ""
    sub_goals: list = field(default_factory=list)

    def __post_init__(self):
        if self.precision is None:
            self.precision = FRAME_PRECISION_PROFILES.get(
                self.frame_type,
                PrecisionProfile(),
            )

    def get_effective_precision(self, subject_precision: float) -> float:
        """
        Combine frame-level global precision with subject-level precision.

        effective = frame_global × subject_precision
        """
        return self.precision.global_precision * subject_precision

    def weighted_valuation(
        self, valuations: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Apply precision-weighted filtering to valuations.

        Returns valuations scaled by their per-dimension precision weight.
        """
        precision_map = self.precision.as_dict()
        result = {}
        for name, val in valuations.items():
            # Match valuation name to precision dimension
            key = name.lower().replace("value", "").replace("support", "").replace("congruence", "").strip("_")
            weight = precision_map.get(key, 0.5)
            result[name] = val * weight
        return result

    def to_json(self) -> str:
        """Serialize."""
        return json.dumps({
            "frame_type": self.frame_type.value,
            "precision": self.precision.as_dict() if self.precision else None,
            "duration_minutes": self.duration_minutes,
            "description": self.description,
            "sub_goals": self.sub_goals,
        })

    @classmethod
    def from_json(cls, data: str | dict) -> "ActivityFrame":
        """Deserialize."""
        if isinstance(data, str):
            data = json.loads(data)
        frame_type = ActivityFrameType(data.get("frame_type", "exploratory"))
        precision = None
        if data.get("precision"):
            p = data["precision"]
            precision = PrecisionProfile(
                safety=p.get("safety", 0.5),
                interest=p.get("interest", 0.5),
                restoration=p.get("restoration", 0.5),
                status=p.get("status", 0.5),
                belonging=p.get("belonging", 0.5),
                identity=p.get("identity", 0.5),
                autonomy=p.get("autonomy", 0.5),
                competence=p.get("competence", 0.5),
                relatedness=p.get("relatedness", 0.5),
                global_precision=p.get("global_precision", 1.0),
            )
        return cls(
            frame_type=frame_type,
            precision=precision,
            duration_minutes=data.get("duration_minutes"),
            description=data.get("description", ""),
            sub_goals=data.get("sub_goals", []),
        )
