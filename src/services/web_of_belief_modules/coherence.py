"""Coherence computation contracts and pure helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from src.epistemic.edge_types import EdgeType as ConstraintType


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class CoherenceResult:
    coherence_score: float
    tensions: list[dict[str, Any]]


def compute_coherence_state(
    beliefs: Mapping[str, Any],
    constraints: Iterable[Any],
) -> CoherenceResult:
    """Compute coherence score and tension list from belief/constraint state."""

    constraints_list = list(constraints)
    if not constraints_list:
        return CoherenceResult(coherence_score=0.5, tensions=[])

    total_coherence = 0.0
    n_constraints = 0
    tensions: list[dict[str, Any]] = []

    for constraint in constraints_list:
        source = beliefs.get(getattr(constraint, "source_id", ""))
        target = beliefs.get(getattr(constraint, "target_id", ""))
        if not source or not target:
            continue

        n_constraints += 1
        source_cred = _clamp_01(getattr(getattr(source, "credence", None), "value", 0.5))
        target_cred = _clamp_01(getattr(getattr(target, "credence", None), "value", 0.5))
        strength = _clamp_01(getattr(constraint, "strength", 0.0))
        ctype = getattr(constraint, "constraint_type", None)

        if ctype == ConstraintType.SUPPORTS:
            agreement = 1.0 - abs(source_cred - target_cred)
            local_coherence = agreement * strength
        elif ctype == ConstraintType.CONTRADICTS:
            disagreement = abs(source_cred - target_cred)
            local_coherence = disagreement * strength
            if source_cred > 0.6 and target_cred > 0.6:
                tensions.append(
                    {
                        "source": constraint.source_id,
                        "target": constraint.target_id,
                        "source_credence": source_cred,
                        "target_credence": target_cred,
                        "type": "contradiction_tension",
                    }
                )
        elif ctype in (ConstraintType.EXPLAINS, ConstraintType.INSTANTIATES):
            local_coherence = (source_cred * target_cred) * strength
        elif ctype == ConstraintType.BRIDGES:
            agreement = 1.0 - abs(source_cred - target_cred)
            local_coherence = agreement * strength * 0.8
        elif ctype == ConstraintType.STRONG_TENSION:
            disagreement = abs(source_cred - target_cred)
            local_coherence = disagreement * strength * 0.5
            if source_cred > 0.5 and target_cred > 0.5:
                tensions.append(
                    {
                        "source": constraint.source_id,
                        "target": constraint.target_id,
                        "source_credence": source_cred,
                        "target_credence": target_cred,
                        "type": "bridge_failure_tension",
                    }
                )
        else:
            local_coherence = 0.5 * strength

        total_coherence += local_coherence

    if n_constraints == 0:
        return CoherenceResult(coherence_score=0.5, tensions=tensions)

    return CoherenceResult(
        coherence_score=total_coherence / n_constraints,
        tensions=tensions,
    )

