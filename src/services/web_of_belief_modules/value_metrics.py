"""Belief value metric contracts and helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class CentralityInput:
    """Contract for centrality computation."""

    belief_id: str
    constraint_count: int
    total_beliefs: int

    def validate(self) -> None:
        if not self.belief_id:
            raise ValueError("belief_id must be non-empty")
        if self.constraint_count < 0:
            raise ValueError("constraint_count must be >= 0")
        if self.total_beliefs < 0:
            raise ValueError("total_beliefs must be >= 0")


@dataclass(frozen=True)
class EpistemicValueInput:
    """Contract for combined value score."""

    centrality: float
    sensitivity: float
    centrality_weight: float = 0.5

    def validate(self) -> None:
        if not 0.0 <= self.centrality_weight <= 1.0:
            raise ValueError("centrality_weight must be in [0, 1]")


@dataclass(frozen=True)
class BeliefValueRecord:
    """Portable value tuple with explicit field names."""

    belief_id: str
    value: float
    centrality: float
    sensitivity: float

    def to_tuple(self) -> tuple[str, float, float, float]:
        return (self.belief_id, self.value, self.centrality, self.sensitivity)


def compute_centrality(payload: CentralityInput) -> float:
    payload.validate()
    max_connections = payload.total_beliefs - 1
    if max_connections <= 0:
        return 0.0
    return _clamp_01(payload.constraint_count / max_connections)


def compute_epistemic_value(payload: EpistemicValueInput) -> float:
    payload.validate()
    centrality = _clamp_01(payload.centrality)
    sensitivity = _clamp_01(payload.sensitivity)
    weight = payload.centrality_weight
    return _clamp_01(weight * centrality + (1.0 - weight) * sensitivity)


def sort_value_records(
    records: Iterable[BeliefValueRecord],
    top_n: int | None = None,
) -> list[BeliefValueRecord]:
    ranked = sorted(records, key=lambda record: record.value, reverse=True)
    if top_n is None:
        return ranked
    if top_n <= 0:
        return []
    return ranked[:top_n]

