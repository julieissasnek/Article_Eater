"""
cva_valuation_engine.py — CVA Valuation Computation Engine
===========================================================

Computes v = V(c; g(ψ), τ(ψ), κ(ψ)):
  1. Select cultural valuation structure (κ)
  2. Map constraint vector to valuations
  3. Apply neurotype modulation
  4. Apply activity frame precision weighting

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §2.2
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from typing import Dict, Optional
import math

from src.models.cva_constraint import Tier2ConstraintVector, CVAConstraintVector
from src.models.cva_valuation import (
    CVAValuationVector,
    CulturalVariant,
    NEUROTYPE_MODIFIERS,
)
from src.models.subject_characteristics import (
    SubjectCharacteristics,
    SelfConstrual,
    NeurotypeName,
)
from src.models.activity_frame import ActivityFrame


# ──────────────────────────────────────────────────────────────────
# Constraint → Valuation Mappings
# ──────────────────────────────────────────────────────────────────

# How each constraint maps to each valuation (weight matrix)
# Rows = valuations, columns = constraints
CONSTRAINT_VALUATION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "SafetyValue": {
        "prediction_error": -0.4,
        "control_efficacy": 0.3,
        "processing_cost": -0.2,
        "social_cue_density": -0.1,
    },
    "InterestValue": {
        "prediction_error": 0.3,     # moderate surprise is interesting
        "affordance_density": 0.3,
        "narrative_coherence": 0.2,
        "processing_cost": -0.2,     # too expensive = not interesting
    },
    "RestorationValue": {
        "processing_cost": -0.5,     # low cost → restorative
        "load_rate": -0.3,
        "multisensory_coherence": 0.3,
    },
    "StatusValue": {
        "social_cue_density": 0.3,
        "affordance_density": 0.2,
        "control_efficacy": 0.3,
    },
    "BelongingValue": {
        "social_cue_density": 0.5,
        "narrative_coherence": 0.2,
        "multisensory_coherence": 0.2,
    },
    "IdentityCongruenceValue": {
        "narrative_coherence": 0.4,
        "control_efficacy": 0.3,
        "affordance_density": 0.2,
    },
    "AutonomySupportValue": {
        "control_efficacy": 0.5,
        "affordance_density": 0.3,
        "processing_cost": -0.2,
    },
    "CompetenceSupportValue": {
        "control_efficacy": 0.4,
        "prediction_error": 0.2,     # moderate challenge
        "affordance_density": 0.2,
    },
    "RelatednessSupportValue": {
        "social_cue_density": 0.4,
        "narrative_coherence": 0.3,
        "multisensory_coherence": 0.2,
    },
    # Cultural-specific valuations
    "AmaeValue": {
        "social_cue_density": 0.4,
        "control_efficacy": -0.2,    # yielding control to trusted authority
        "narrative_coherence": 0.3,
    },
    "MaValue": {
        "affordance_density": -0.5,  # emptiness valued
        "processing_cost": -0.3,
        "multisensory_coherence": 0.4,
    },
    "ÀṣàValue": {
        "social_cue_density": 0.4,
        "narrative_coherence": 0.3,
        "control_efficacy": 0.2,
    },
    "RasaValue": {
        "multisensory_coherence": 0.4,
        "narrative_coherence": 0.3,
        "prediction_error": 0.2,
    },
    "DharmaValue": {
        "narrative_coherence": 0.5,
        "social_cue_density": 0.2,
        "control_efficacy": 0.2,
    },
}


class CVAValuationEngine:
    """
    Valuation computation engine: v = V(c; g(ψ), τ(ψ), κ(ψ))

    Takes constraints + subject characteristics → valuation vector.
    """

    def __init__(
        self,
        weight_overrides: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        self.weights = dict(CONSTRAINT_VALUATION_WEIGHTS)
        if weight_overrides:
            self.weights.update(weight_overrides)

    def compute(
        self,
        constraints: CVAConstraintVector | Tier2ConstraintVector,
        subject: Optional[SubjectCharacteristics] = None,
        frame: Optional[ActivityFrame] = None,
    ) -> CVAValuationVector:
        """
        Compute valuation vector from constraints and subject.

        Args:
            constraints: Full or Tier 2 constraint vector
            subject: Subject characteristics (ψ). Defaults to typical.
            frame: Activity frame for precision weighting. Optional.

        Returns:
            CVAValuationVector with culture-appropriate dimensionality.
        """
        if subject is None:
            subject = SubjectCharacteristics()

        # Step 1: Select cultural variant
        variant = self._select_variant(subject)

        # Step 2: Compute base valuations from constraints
        base = self._compute_base_valuations(constraints, variant)

        # Step 3: Apply neurotype modulation
        modulated = self._apply_neurotype(base, subject)

        # Step 4: Apply activity frame precision
        if frame:
            modulated = self._apply_frame_precision(modulated, frame, subject)

        return modulated

    def _select_variant(self, subject: SubjectCharacteristics) -> CulturalVariant:
        """κ(ψ_culture) → cultural valuation variant."""
        mapping = {
            SelfConstrual.INDEPENDENT: CulturalVariant.WESTERN,
            SelfConstrual.INTERDEPENDENT: CulturalVariant.JAPANESE,
            SelfConstrual.RELATIONAL: CulturalVariant.WEST_AFRICAN,
            SelfConstrual.DHARMIC: CulturalVariant.INDIAN,
        }
        return mapping.get(subject.culture.kappa_self, CulturalVariant.WESTERN)

    def _compute_base_valuations(
        self,
        constraints: CVAConstraintVector | Tier2ConstraintVector,
        variant: CulturalVariant,
    ) -> CVAValuationVector:
        """Map constraint vector to valuation space."""
        # Get Tier 2 values
        if isinstance(constraints, CVAConstraintVector):
            c = constraints.tier2.as_dict()
        else:
            c = constraints.as_dict()

        # Create empty valuation vector for this variant
        val = CVAValuationVector(variant=variant)

        # Compute each valuation dimension
        for dim_name in val.values:
            weights = self.weights.get(dim_name, {})
            if not weights:
                continue
            # Weighted sum of constraints + sigmoid squash
            raw = sum(c.get(cn, 0.5) * w for cn, w in weights.items())
            # Sigmoid to [0, 1]
            val.values[dim_name] = 1.0 / (1.0 + math.exp(-4.0 * raw))

        return val

    def _apply_neurotype(
        self,
        valuation: CVAValuationVector,
        subject: SubjectCharacteristics,
    ) -> CVAValuationVector:
        """Apply neurotype-specific valuation modifiers."""
        neuro_name = subject.neurotype.name.value
        modifier = NEUROTYPE_MODIFIERS.get(neuro_name)
        if modifier:
            return modifier.apply(valuation)
        return valuation

    def _apply_frame_precision(
        self,
        valuation: CVAValuationVector,
        frame: ActivityFrame,
        subject: SubjectCharacteristics,
    ) -> CVAValuationVector:
        """
        Apply activity frame precision weighting.

        precision(ψ) × frame_precision → effective filtering of valuations.
        Dimensions with low precision are attenuated.
        """
        subject_precision = subject.compute_precision()
        effective = frame.get_effective_precision(subject_precision)

        # Precision-weighted softmax (higher precision → sharper discrimination)
        weighted = frame.weighted_valuation(valuation.values)
        # Scale by effective precision (normalized)
        scale = min(effective / 2.0, 2.0)  # Prevent extreme scaling

        new_values = {}
        for name, val in valuation.values.items():
            w = weighted.get(name, val * 0.5)
            # Blend: original value × (1 − weight) + precision-weighted × weight
            blended = val * 0.6 + (w * scale) * 0.4
            new_values[name] = max(0.0, min(1.0, blended))

        return CVAValuationVector(
            values=new_values,
            variant=valuation.variant,
            subject_id=valuation.subject_id,
            scene_id=valuation.scene_id,
        )

    # ── R2.3: Sparse Auxiliary Activation ────────────────────────

    CORE_AXIS_NAMES = [
        "SafetyValue", "InterestValue", "RestorationValue",
        "StatusValue", "BelongingValue", "IdentityCongruenceValue",
        "AutonomySupportValue", "CompetenceSupportValue",
        "RelatednessSupportValue",
    ]

    def compute_valuation_with_frame(
        self,
        constraints: CVAConstraintVector | Tier2ConstraintVector,
        activity_frame_name: str,
        subject: Optional[SubjectCharacteristics] = None,
    ) -> "CompleteValuationVector":
        """Compute valuation with frame-aware core/auxiliary split.

        v_core (9D, always) + v_aux (sparse, frame-dependent)
        + frame precision gains W(A) modulation.

        Reference: AG_PHASE2_REMEDIATION R2.3 (Chat's Q3: Multiple Realizability)
        """
        import numpy as np

        if subject is None:
            subject = SubjectCharacteristics()

        # Step 1: Compute base core valuation
        variant = self._select_variant(subject)
        base_val = self._compute_base_valuations(constraints, variant)
        base_val = self._apply_neurotype(base_val, subject)

        v_core = np.array([
            base_val.values.get(name, 0.5) for name in self.CORE_AXIS_NAMES
        ])

        # Step 2: Get frame config
        frame_config = AUXILIARY_FRAME_CONFIG.get(
            activity_frame_name,
            {"auxiliary_axes": [], "core_gains": [1.0] * 9},
        )

        # Step 3: Compute auxiliary valuations (only active ones)
        active_aux = frame_config["auxiliary_axes"]
        aux_values = {}
        if isinstance(constraints, CVAConstraintVector):
            c_dict = constraints.tier2.as_dict()
        else:
            c_dict = constraints.as_dict()

        all_aux = self._compute_all_auxiliaries(c_dict, subject)
        for axis in active_aux:
            if axis in all_aux:
                aux_values[axis] = all_aux[axis]

        # Step 4: Apply frame precision gains to core
        gains = np.array(frame_config.get("core_gains", [1.0] * 9))
        v_core_modulated = v_core * gains

        return CompleteValuationVector(
            core=v_core_modulated,
            auxiliary=aux_values,
            active_auxiliary_axes=active_aux,
            activity_frame=activity_frame_name,
            precision_gains=gains,
        )

    def _compute_all_auxiliaries(
        self,
        constraints: Dict[str, float],
        subject: SubjectCharacteristics,
    ) -> Dict[str, float]:
        """Compute all possible auxiliary dimensions."""
        # Sacredness: high coherence + high social → sacred space
        sacredness = 1.0 / (1 + math.exp(-4.0 * (
            constraints.get("narrative_coherence", 0.5) * 0.5
            + constraints.get("social_cue_density", 0.5) * 0.3
            + constraints.get("multisensory_coherence", 0.5) * 0.2
        )))

        # Originality: high prediction error + high affordance → novel creation
        originality = 1.0 / (1 + math.exp(-4.0 * (
            constraints.get("prediction_error", 0.5) * 0.4
            + constraints.get("affordance_density", 0.5) * 0.4
            - constraints.get("processing_cost", 0.5) * 0.2
        )))

        # Humor: moderate prediction error + low processing cost → playful
        humor = 1.0 / (1 + math.exp(-4.0 * (
            constraints.get("prediction_error", 0.5) * 0.3
            - constraints.get("processing_cost", 0.5) * 0.3
            + constraints.get("social_cue_density", 0.5) * 0.3
        )))

        # Danger: high prediction error + low control → threat
        danger = 1.0 / (1 + math.exp(-4.0 * (
            constraints.get("prediction_error", 0.5) * 0.5
            - constraints.get("control_efficacy", 0.5) * 0.4
        )))

        return {
            "sacredness": sacredness,
            "originality": originality,
            "humor": humor,
            "danger": danger,
        }


# ══════════════════════════════════════════════════════════════════
# R2.3: CompleteValuationVector
# ══════════════════════════════════════════════════════════════════

import numpy as np
from dataclasses import dataclass, field


@dataclass
class CompleteValuationVector:
    """Valuation with frame-aware core/auxiliary split.

    core [9D]: always-active valuation dimensions, modulated by frame precision gains
    auxiliary: sparse dict of frame-activated extra dimensions
    """
    core: np.ndarray                      # [9] modulated core
    auxiliary: Dict[str, float]           # {axis: value} sparse
    active_auxiliary_axes: list           # which auxiliaries active
    activity_frame: str
    precision_gains: np.ndarray           # [9] gain multipliers applied

    def __post_init__(self):
        self.core = np.asarray(self.core, dtype=float)
        self.precision_gains = np.asarray(self.precision_gains, dtype=float)

    def get_full_valuation(self) -> np.ndarray:
        """Return core + active auxiliaries concatenated."""
        aux_vals = list(self.auxiliary.values())
        if aux_vals:
            return np.concatenate([self.core, aux_vals])
        return self.core.copy()

    def core_only(self) -> np.ndarray:
        """Return just the 9D core."""
        return self.core.copy()


# ── Frame-specific auxiliary configurations ──────────────────────

AUXILIARY_FRAME_CONFIG: Dict[str, Dict] = {
    "RESTING": {
        "auxiliary_axes": [],
        "core_gains": [2.0, 0.5, 2.0, 0.3, 1.0, 0.5, 2.0, 0.3, 1.0],
    },
    "STUDYING": {
        "auxiliary_axes": [],
        "core_gains": [1.0, 2.0, 0.5, 0.5, 1.0, 1.5, 1.5, 2.0, 0.8],
    },
    "EXPLORING": {
        "auxiliary_axes": ["danger"],
        "core_gains": [1.5, 2.0, 0.5, 0.3, 0.5, 0.5, 1.5, 1.0, 0.5],
    },
    "CREATING": {
        "auxiliary_axes": ["originality"],
        "core_gains": [0.5, 1.5, 0.5, 0.5, 1.0, 1.5, 0.5, 2.0, 0.5],
    },
    "WORSHIPPING": {
        "auxiliary_axes": ["sacredness"],
        "core_gains": [1.0, 0.5, 1.0, 0.3, 1.5, 2.0, 1.5, 0.5, 1.5],
    },
    "PLAYING": {
        "auxiliary_axes": ["humor"],
        "core_gains": [0.5, 2.0, 0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 1.5],
    },
    "EATING": {
        "auxiliary_axes": [],
        "core_gains": [1.5, 0.5, 1.5, 0.3, 1.0, 0.5, 1.5, 0.3, 1.0],
    },
    "SOCIALIZING": {
        "auxiliary_axes": ["humor"],
        "core_gains": [1.0, 1.0, 0.5, 1.5, 2.0, 1.0, 1.0, 0.5, 2.0],
    },
    "SLEEPING": {
        "auxiliary_axes": [],
        "core_gains": [2.0, 0.2, 2.0, 0.2, 0.5, 0.2, 2.0, 0.2, 0.5],
    },
    "EXERCISING": {
        "auxiliary_axes": [],
        "core_gains": [1.0, 1.5, 0.5, 0.5, 0.5, 0.5, 1.0, 2.0, 1.5],
    },
}
