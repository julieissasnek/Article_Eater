"""Entrenchment computation contracts and helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.services.web_of_belief_components import BeliefStatus, EpistemicLevel


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


DEFAULT_LEVEL_WEIGHTS: dict[EpistemicLevel, float] = {
    EpistemicLevel.THEORETICAL: 0.8,
    EpistemicLevel.INTERMEDIATE: 0.5,
    EpistemicLevel.EMPIRICAL: 0.3,
    EpistemicLevel.OBSERVATIONAL: 0.2,
}

_STATUS_BONUS: dict[BeliefStatus, float] = {
    BeliefStatus.ESTABLISHED: 0.2,
    BeliefStatus.ENTRENCHED: 0.3,
    BeliefStatus.TENTATIVE: 0.0,
    BeliefStatus.STUB: -0.1,
    BeliefStatus.ANOMALOUS: -0.2,
}


@dataclass(frozen=True)
class EntrenchmentInput:
    """Contract for entrenchment computation."""

    belief_id: str
    belief_level: EpistemicLevel
    credence_value: float
    credence_uncertainty: float
    belief_status: BeliefStatus
    constraint_count: int

    def validate(self) -> None:
        if not self.belief_id:
            raise ValueError("belief_id must be non-empty")
        if self.constraint_count < 0:
            raise ValueError("constraint_count must be >= 0")


@dataclass(frozen=True)
class EntrenchmentComponents:
    """Structured result for entrenchment component diagnostics."""

    entrenchment: float
    connectivity: float
    level_weight: float
    coherence_contrib: float
    constraint_count: int

    def to_dict(self) -> dict[str, float | int]:
        return {
            "entrenchment": self.entrenchment,
            "connectivity": self.connectivity,
            "level_weight": self.level_weight,
            "coherence_contrib": self.coherence_contrib,
            "constraint_count": self.constraint_count,
        }


def empty_entrenchment_components() -> EntrenchmentComponents:
    return EntrenchmentComponents(
        entrenchment=0.0,
        connectivity=0.0,
        level_weight=0.0,
        coherence_contrib=0.0,
        constraint_count=0,
    )


def compute_entrenchment_components(
    payload: EntrenchmentInput,
    level_weights: Mapping[EpistemicLevel, float] | None = None,
) -> EntrenchmentComponents:
    """Compute entrenchment with strict contracts and bounded outputs."""

    payload.validate()

    weights = level_weights or DEFAULT_LEVEL_WEIGHTS
    connectivity = min(1.0, payload.constraint_count / 10.0)

    level_weight = _clamp_01(weights.get(payload.belief_level, 0.3))
    credence = _clamp_01(payload.credence_value)
    uncertainty = _clamp_01(payload.credence_uncertainty)
    credence_factor = credence * (1.0 - uncertainty)
    status_bonus = _STATUS_BONUS.get(payload.belief_status, 0.0)
    coherence_contrib = _clamp_01(credence_factor + status_bonus)

    entrenchment = _clamp_01(
        0.4 * connectivity + 0.3 * level_weight + 0.3 * coherence_contrib
    )

    return EntrenchmentComponents(
        entrenchment=entrenchment,
        connectivity=connectivity,
        level_weight=level_weight,
        coherence_contrib=coherence_contrib,
        constraint_count=payload.constraint_count,
    )

