"""
cva_constraint_engine.py — CVA Constraint Computation Engine
=============================================================

Computes c = f(x; θ(ψ)):
  1. Extract Tier 1 perceptual primitives from scene
  2. Apply θ(ψ) to compute Tier 2 interpretive constraints
  3. Apply neurotype and cultural modulation

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §2.1
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from src.models.cva_constraint import (
    Tier1ConstraintVector,
    Tier2ConstraintVector,
    CVAConstraintVector,
    ConstraintTheta,
    DEFAULT_TIER2_THETA,
)
from src.models.subject_characteristics import (
    SubjectCharacteristics,
    NeurotypeName,
    NEUROTYPE_PROFILES,
)


# ──────────────────────────────────────────────────────────────────
# Neurotype Constraint Modifiers
# ──────────────────────────────────────────────────────────────────

# Per-neurotype gain/bias for Tier 2 constraints (from spec §3.1–3.10)
NEUROTYPE_CONSTRAINT_MODS: Dict[str, Dict[str, Dict[str, float]]] = {
    "ptsd": {
        "prediction_error": {"gain": 2.0},
        "processing_cost": {"gain": 1.5},
        "load_rate": {"gain": 1.3},
        "control_efficacy": {"gain": 0.6},
    },
    "asd": {
        "multisensory_coherence": {"gain": 0.5},
        "processing_cost": {"gain": 1.3},      # for social navigation
        "social_cue_density": {"gain": 0.7},    # salience reduced
    },
    "adhd": {
        "processing_cost": {"gain": 0.7},       # ignored
        "load_rate": {"gain": 1.3},
        "affordance_density": {"gain": 1.3},    # prefers higher
    },
    "older_adult": {
        "processing_cost": {"gain": 1.5},
        "load_rate": {"gain": 0.7},
        "control_efficacy": {"gain": 0.7},
        "multisensory_coherence": {"gain": 0.7},
    },
    "alzheimers": {
        "processing_cost": {"gain": 2.0},
        "prediction_error": {"gain": 1.8},
        "control_efficacy": {"gain": 0.3},
        "narrative_coherence": {"gain": 0.3},
    },
    "depression": {
        "processing_cost": {"gain": 1.3},
        "social_cue_density": {"gain": 0.7},
    },
    "anxiety": {
        "prediction_error": {"gain": 1.8},
        "processing_cost": {"gain": 1.3},
        "control_efficacy": {"gain": 0.6},
        "social_cue_density": {"gain": 1.5},    # for social anxiety
    },
    "bipolar_manic": {
        "affordance_density": {"gain": 1.5},
        "load_rate": {"gain": 1.5},
    },
    "gifted": {
        "processing_cost": {"gain": 0.6},       # rapid model building
        "affordance_density": {"gain": 1.3},    # abstract affordances
        "narrative_coherence": {"gain": 1.3},
    },
}


class CVAConstraintEngine:
    """
    Constraint computation engine: c = f(x; θ(ψ))

    Takes a scene descriptor (feature vector or dict) and subject
    characteristics, returns a full CVAConstraintVector.
    """

    def __init__(
        self,
        theta_overrides: Optional[Dict[str, ConstraintTheta]] = None,
    ):
        """
        Args:
            theta_overrides: Custom θ(ψ) mappings. Defaults to DEFAULT_TIER2_THETA.
        """
        self.theta = dict(DEFAULT_TIER2_THETA)
        if theta_overrides:
            self.theta.update(theta_overrides)

    def compute(
        self,
        scene_features: Dict[str, float],
        subject: Optional[SubjectCharacteristics] = None,
    ) -> CVAConstraintVector:
        """
        Compute full constraint vector from scene and subject.

        Args:
            scene_features: Dict with Tier 1 primitive values.
                Keys: edge, motion, contrast, figure_ground,
                      temporal_coherence, symmetry
            subject: Subject characteristics (ψ). If None, uses typical defaults.

        Returns:
            CVAConstraintVector with Tier 1 and ψ-calibrated Tier 2.
        """
        if subject is None:
            subject = SubjectCharacteristics()

        # Step 1: Extract Tier 1
        tier1 = self._extract_tier1(scene_features, subject)

        # Step 2: Compute Tier 2 from Tier 1 + θ(ψ)
        tier2 = self._compute_tier2(tier1, subject)

        # Step 3: Apply neurotype modulation to Tier 2
        tier2 = self._apply_neurotype_mods(tier2, subject)

        return CVAConstraintVector(
            tier1=tier1,
            tier2=tier2,
            subject_id=subject.subject_id,
        )

    def _extract_tier1(
        self,
        features: Dict[str, float],
        subject: SubjectCharacteristics,
    ) -> Tier1ConstraintVector:
        """
        Extract Tier 1 perceptual primitives.
        Apply aging-related decline if subject is older.
        """
        tier1 = Tier1ConstraintVector(
            edge=max(0, min(1, features.get("edge", 0.0))),
            motion=max(0, min(1, features.get("motion", 0.0))),
            contrast=max(0, min(1, features.get("contrast", 0.0))),
            figure_ground=max(0, min(1, features.get("figure_ground", 0.0))),
            temporal_coherence=max(0, min(1, features.get("temporal_coherence", 0.0))),
            symmetry=max(0, min(1, features.get("symmetry", 0.0))),
        )

        # Apply aging decline
        age = subject.development.age
        if age > 40:
            tier1 = tier1.apply_aging_decline(age)

        return tier1

    def _compute_tier2(
        self,
        tier1: Tier1ConstraintVector,
        subject: SubjectCharacteristics,
    ) -> Tier2ConstraintVector:
        """
        c_Tier2 = g(c_Tier1; θ(ψ))

        Apply θ mapping: each Tier 2 constraint is a weighted
        function of Tier 1 primitives.
        """
        tier1_dict = {
            "edge": tier1.edge,
            "motion": tier1.motion,
            "contrast": tier1.contrast,
            "figure_ground": tier1.figure_ground,
            "temporal_coherence": tier1.temporal_coherence,
            "symmetry": tier1.symmetry,
        }

        tier2_values = {}
        for constraint_name, theta in self.theta.items():
            # Apply experience-modulated gain
            exp_gain = self._experience_gain(constraint_name, subject)
            effective_theta = ConstraintTheta(
                gain=theta.gain * exp_gain,
                bias=theta.bias,
                source_weights=theta.source_weights,
            )
            tier2_values[constraint_name] = effective_theta.apply(tier1_dict)

        return Tier2ConstraintVector(**tier2_values)

    def _experience_gain(
        self, constraint_name: str, subject: SubjectCharacteristics
    ) -> float:
        """
        Experience modulates processing cost (experts have lower cost)
        and prediction error (experts have richer internal models).
        """
        mastery = subject.experience.mastery
        if constraint_name == "processing_cost":
            return 1.0 - (mastery * 0.4)  # Up to 40% reduction for experts
        elif constraint_name == "prediction_error":
            return 1.0 - (mastery * 0.3)  # Experts predict better
        return 1.0

    def _apply_neurotype_mods(
        self,
        tier2: Tier2ConstraintVector,
        subject: SubjectCharacteristics,
    ) -> Tier2ConstraintVector:
        """Apply neurotype-specific constraint modulations."""
        neuro_name = subject.neurotype.name.value
        mods = NEUROTYPE_CONSTRAINT_MODS.get(neuro_name, {})

        if not mods:
            return tier2

        values = tier2.as_dict()
        for constraint, mod in mods.items():
            if constraint in values:
                val = values[constraint]
                gain = mod.get("gain", 1.0)
                bias = mod.get("bias", 0.0)
                values[constraint] = max(0.0, min(1.0, val * gain + bias))

        return Tier2ConstraintVector(**values)

    # ── R2.1: Probabilistic Constraint Recognition ───────────────

    def recognize_constraints_probabilistic(
        self,
        scene_features: Dict[str, float],
        activity_frame: str,
        subject: Optional[SubjectCharacteristics] = None,
    ) -> "ConstraintDistribution":
        """Recognize constraints as probabilistic distribution p(c|x,A,ψ).

        Returns a ConstraintDistribution with:
          mean = f(x; θ(ψ))  [existing deterministic output]
          precision = π(A)   [from activity frame precision weights]

        Args:
            scene_features: Scene feature dict
            activity_frame: Activity context (e.g., 'RESTING')
            subject: Subject characteristics (ψ)

        Returns:
            ConstraintDistribution with mean, precision, sampling
        """
        # Step 1: Compute deterministic mean via existing engine
        cva = self.compute(scene_features, subject)
        mean_vec = cva.tier2.as_vector()  # [8]

        # Step 2: Get precision from activity frame
        precision_vec = FRAME_PRECISIONS.get(
            activity_frame, [1.0] * 8
        )

        return ConstraintDistribution(
            mean=mean_vec,
            precision=precision_vec,
            activity_frame=activity_frame,
        )


# ══════════════════════════════════════════════════════════════════
# R2.1: ConstraintDistribution
# ══════════════════════════════════════════════════════════════════

import numpy as np
import math as _math


@dataclass
class ConstraintDistribution:
    """Probabilistic constraint posterior p(c|x,A,ψ) ~ N(c|μ, Σ).

    where:
      μ = f(x; θ(ψ))         [existing deterministic engine]
      Σ = diag(π(A)⁻¹)       [frame-dependent covariance]
      π(A) ∈ ℝ⁸              [precision vector from ActivityFrame]

    Reference: AG_PHASE2_REMEDIATION R2.1 (Chat's Q1: Spohn/Epistemic Uncertainty)
    """
    mean: list                # [8] — deterministic output f(x; θ(ψ))
    precision: list           # [8] — diagonal precisions from π(A)
    activity_frame: str       # for reference/debugging

    def sample(self, n: int = 1) -> np.ndarray:
        """Draw n samples from p(c|x,A,ψ). Returns [n, 8] array."""
        mean = np.asarray(self.mean, dtype=float)
        prec = np.asarray(self.precision, dtype=float)
        std = 1.0 / np.sqrt(prec + 1e-8)
        return np.random.normal(mean, std, size=(n, 8))

    def map_estimate(self) -> np.ndarray:
        """Return MAP estimate = mean (backward compatible with deterministic)."""
        return np.asarray(self.mean, dtype=float).copy()

    def entropy(self) -> float:
        """Differential entropy H = 0.5 * Σ log(2πe/π_i).

        Higher precision → lower entropy (more certain).
        """
        prec = np.asarray(self.precision, dtype=float)
        return float(0.5 * np.sum(np.log(2 * np.pi * np.e / (prec + 1e-8))))

    def covariance_diagonal(self) -> np.ndarray:
        """Return diagonal covariances σ²_i = 1/π_i."""
        prec = np.asarray(self.precision, dtype=float)
        return 1.0 / (prec + 1e-8)

    def std_dev(self) -> np.ndarray:
        """Return standard deviations."""
        return np.sqrt(self.covariance_diagonal())


# ── Activity Frame Precision Values (from spec table) ────────────

# [Safe, Stable, Path, Attract, Repel, Support, Push, Resist]
FRAME_PRECISIONS: Dict[str, list] = {
    "RESTING":     [2.0, 2.0, 0.3, 0.3, 0.3, 2.0, 0.3, 0.3],
    "STUDYING":    [1.5, 1.5, 1.5, 1.0, 1.0, 1.0, 1.5, 0.8],
    "EXPLORING":   [0.5, 0.8, 2.0, 1.0, 1.0, 0.5, 0.5, 0.5],
    "CREATING":    [0.3, 0.5, 1.0, 2.0, 2.0, 0.3, 2.0, 0.5],
    "WORSHIPPING": [1.5, 1.5, 0.5, 1.5, 2.0, 2.0, 0.3, 0.3],
    "PLAYING":     [0.5, 0.5, 1.5, 2.0, 1.0, 0.5, 1.0, 0.5],
    "EATING":      [1.0, 1.5, 0.5, 1.0, 0.3, 1.5, 0.3, 0.3],
    "SOCIALIZING": [1.0, 1.0, 1.0, 1.5, 1.0, 1.5, 1.0, 0.8],
    "SLEEPING":    [2.0, 2.0, 0.2, 0.2, 0.2, 2.0, 0.2, 0.2],
    "EXERCISING":  [0.5, 1.0, 2.0, 1.5, 1.5, 1.0, 2.0, 1.0],
}
