"""
cva_constraint.py — CVA Constraint Vector Data Structures
==========================================================

Implements the 8-dimensional Tier 2 constraint vector and
6-primitive Tier 1 constraint set from CVA architecture.

Tier 1 (universal perceptual primitives):
    Edge, Motion, Contrast, FigureGround, TemporalCoherence, Symmetry

Tier 2 (ψ-calibrated interpretive constraints):
    ProcessingCost, LoadRate, PredictionError, ControlEfficacy,
    AffordanceDensity, SocialCueDensity, MultisensoryCoherence,
    NarrativeCoherence

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §2.1, §4.1–4.2
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json
import math


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────

class ConstraintTier(Enum):
    """Whether a constraint is a perceptual primitive or interpretive overlay."""
    TIER_1 = "tier_1"  # Universal perceptual primitive
    TIER_2 = "tier_2"  # ψ-calibrated interpretive constraint


class ConstraintName(Enum):
    """The 8 Tier 2 CVA constraints."""
    PROCESSING_COST = "ProcessingCost"
    LOAD_RATE = "LoadRate"
    PREDICTION_ERROR = "PredictionError"
    CONTROL_EFFICACY = "ControlEfficacy"
    AFFORDANCE_DENSITY = "AffordanceDensity"
    SOCIAL_CUE_DENSITY = "SocialCueDensity"
    MULTISENSORY_COHERENCE = "MultisensoryCoherence"
    NARRATIVE_COHERENCE = "NarrativeCoherence"


class Tier1Primitive(Enum):
    """The 6 Tier 1 perceptual primitives."""
    EDGE_DETECTION = "edge_detection"
    MOTION_DETECTION = "motion_detection"
    FIGURE_GROUND = "figure_ground"
    LUMINANCE_CONTRAST = "luminance_contrast"
    TEMPORAL_COHERENCE = "temporal_coherence"
    SYMMETRY_DETECTION = "symmetry_detection"


# ──────────────────────────────────────────────────────────────────
# Tier 1: Universal Perceptual Primitives
# ──────────────────────────────────────────────────────────────────

@dataclass
class Tier1ConstraintVector:
    """
    c_Tier1 = f_universal(x; a, ν_sensory)

    Six perceptual primitives, approximately invariant across
    neurotypes except for aging-related sensory decline.
    All values in [0, 1].
    """
    edge: float = 0.0
    motion: float = 0.0
    contrast: float = 0.0
    figure_ground: float = 0.0
    temporal_coherence: float = 0.0
    symmetry: float = 0.0

    def __post_init__(self):
        for name in ("edge", "motion", "contrast", "figure_ground",
                     "temporal_coherence", "symmetry"):
            val = getattr(self, name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(
                    f"Tier 1 constraint {name}={val} outside [0, 1]"
                )

    def as_vector(self) -> List[float]:
        """Return as ordered list [edge, motion, contrast, fg, tc, sym]."""
        return [
            self.edge, self.motion, self.contrast,
            self.figure_ground, self.temporal_coherence, self.symmetry,
        ]

    def apply_aging_decline(self, age: float) -> "Tier1ConstraintVector":
        """
        Apply aging-related sensory decline.
        Ages ≤40: no effect. 40–90: gradual decline in contrast and temporal_coherence.
        """
        if age <= 40:
            return self

        # contrast sensitivity declines: 65yo needs ~3x contrast of 25yo
        contrast_factor = max(0.3, 1.0 - (age - 40) * 0.014)
        # temporal binding window widens with age
        tc_factor = max(0.5, 1.0 - (age - 40) * 0.01)

        return Tier1ConstraintVector(
            edge=self.edge,
            motion=self.motion,
            contrast=min(1.0, self.contrast * contrast_factor),
            figure_ground=self.figure_ground,
            temporal_coherence=min(1.0, self.temporal_coherence * tc_factor),
            symmetry=self.symmetry,
        )


# ──────────────────────────────────────────────────────────────────
# Tier 2: ψ-Calibrated Interpretive Constraints
# ──────────────────────────────────────────────────────────────────

@dataclass
class Tier2ConstraintVector:
    """
    c_Tier2 = g(c_Tier1; θ(ψ))

    Eight interpretive constraints calibrated by subject characteristics.
    All values in [0, 1] representing normalized constraint activation.
    """
    processing_cost: float = 0.5
    load_rate: float = 0.5
    prediction_error: float = 0.5
    control_efficacy: float = 0.5
    affordance_density: float = 0.5
    social_cue_density: float = 0.5
    multisensory_coherence: float = 0.5
    narrative_coherence: float = 0.5

    _FIELD_NAMES = (
        "processing_cost", "load_rate", "prediction_error",
        "control_efficacy", "affordance_density", "social_cue_density",
        "multisensory_coherence", "narrative_coherence",
    )

    def __post_init__(self):
        for name in self._FIELD_NAMES:
            val = getattr(self, name)
            if not isinstance(val, (int, float)):
                raise TypeError(f"Constraint {name} must be numeric, got {type(val)}")
            # Clamp to [0, 1]
            setattr(self, name, max(0.0, min(1.0, float(val))))

    def as_vector(self) -> List[float]:
        """Return as ordered 8-element list."""
        return [getattr(self, n) for n in self._FIELD_NAMES]

    def as_dict(self) -> Dict[str, float]:
        """Return as name→value dict."""
        return {n: getattr(self, n) for n in self._FIELD_NAMES}

    def distance(self, other: "Tier2ConstraintVector") -> float:
        """Euclidean distance between two constraint vectors."""
        return math.sqrt(sum(
            (a - b) ** 2 for a, b in zip(self.as_vector(), other.as_vector())
        ))

    def __getitem__(self, name: str) -> float:
        return getattr(self, name)


# ──────────────────────────────────────────────────────────────────
# Combined Constraint Vector
# ──────────────────────────────────────────────────────────────────

@dataclass
class CVAConstraintVector:
    """
    Full constraint vector c = [c_Tier1, c_Tier2(ψ)]

    Combines universal perceptual primitives with ψ-calibrated
    interpretive constraints.
    """
    tier1: Tier1ConstraintVector = field(default_factory=Tier1ConstraintVector)
    tier2: Tier2ConstraintVector = field(default_factory=Tier2ConstraintVector)

    # Metadata
    scene_id: Optional[str] = None
    timestamp: Optional[str] = None
    subject_id: Optional[str] = None

    def as_full_vector(self) -> List[float]:
        """14-element vector: [6 Tier1 + 8 Tier2]."""
        return self.tier1.as_vector() + self.tier2.as_vector()

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "tier1": asdict(self.tier1),
            "tier2": asdict(self.tier2),
            "scene_id": self.scene_id,
            "timestamp": self.timestamp,
            "subject_id": self.subject_id,
        })

    @classmethod
    def from_json(cls, data: str | dict) -> "CVAConstraintVector":
        """Deserialize from JSON string or dict."""
        if isinstance(data, str):
            data = json.loads(data)
        return cls(
            tier1=Tier1ConstraintVector(**data.get("tier1", {})),
            tier2=Tier2ConstraintVector(**data.get("tier2", {})),
            scene_id=data.get("scene_id"),
            timestamp=data.get("timestamp"),
            subject_id=data.get("subject_id"),
        )


# ──────────────────────────────────────────────────────────────────
# Tier 1 → Tier 2 Mapping (parameterized by θ(ψ))
# ──────────────────────────────────────────────────────────────────

@dataclass
class ConstraintTheta:
    """
    θ(ψ) — per-constraint parameters that calibrate Tier 2 from Tier 1.

    Each Tier 2 constraint has:
      - gain: multiplicative scaling
      - bias: additive offset
      - source_weights: weights on Tier 1 inputs
    """
    gain: float = 1.0
    bias: float = 0.0
    source_weights: Dict[str, float] = field(default_factory=dict)

    def apply(self, tier1_values: Dict[str, float]) -> float:
        """Compute Tier 2 value from Tier 1 inputs."""
        weighted_sum = sum(
            tier1_values.get(src, 0.0) * w
            for src, w in self.source_weights.items()
        )
        result = self.gain * weighted_sum + self.bias
        return max(0.0, min(1.0, result))


# Default Tier 1 → Tier 2 mappings (from spec §4.2)
DEFAULT_TIER2_THETA: Dict[str, ConstraintTheta] = {
    "processing_cost": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"contrast": 0.3, "motion": 0.3, "edge": 0.4},
    ),
    "load_rate": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"temporal_coherence": 0.7, "motion": 0.3},
    ),
    "prediction_error": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"edge": 0.4, "motion": 0.3, "symmetry": 0.3},
    ),
    "control_efficacy": ConstraintTheta(
        gain=1.0, bias=0.3,
        source_weights={"figure_ground": 0.5, "symmetry": 0.5},
    ),
    "affordance_density": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"symmetry": 0.4, "figure_ground": 0.6},
    ),
    "social_cue_density": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"figure_ground": 0.5, "motion": 0.3, "edge": 0.2},
    ),
    "multisensory_coherence": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={"temporal_coherence": 0.8, "motion": 0.2},
    ),
    "narrative_coherence": ConstraintTheta(
        gain=1.0, bias=0.0,
        source_weights={
            "temporal_coherence": 0.4, "figure_ground": 0.3, "edge": 0.3,
        },
    ),
}
