"""Evidence-propagation contracts and payload helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class EvidenceUpdateInput:
    """Validated/normalized input contract for WebOfBelief.add_evidence()."""

    belief_id: str
    content: str
    paper_id: str
    credence: float
    supports_beliefs: Mapping[str, float]
    contradicts_beliefs: Mapping[str, float]
    theory_relevance: Mapping[str, float]
    observed_temporal: Mapping[str, tuple[float, float]]
    moderator: Optional[str]

    def validate(self) -> None:
        if not self.belief_id:
            raise ValueError("belief_id must be non-empty")
        if not self.content:
            raise ValueError("content must be non-empty")
        if not self.paper_id:
            raise ValueError("paper_id must be non-empty")


def normalize_strength_map(raw: Optional[Mapping[str, Any]]) -> dict[str, float]:
    """Normalize relation strengths into bounded [0, 1] values."""
    if not raw:
        return {}
    normalized: dict[str, float] = {}
    for key, value in raw.items():
        key_str = str(key).strip()
        if not key_str:
            continue
        try:
            normalized[key_str] = _clamp_01(float(value))
        except (TypeError, ValueError):
            continue
    return normalized


def normalize_temporal_observations(
    raw: Optional[Mapping[str, Any]],
) -> dict[str, tuple[float, float]]:
    """Normalize temporal updates to (estimate, se) with non-negative SE."""
    if not raw:
        return {}
    normalized: dict[str, tuple[float, float]] = {}
    for param_name, value in raw.items():
        key_str = str(param_name).strip()
        if not key_str:
            continue
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            continue
        try:
            estimate = float(value[0])
            standard_error = abs(float(value[1]))
        except (TypeError, ValueError):
            continue
        normalized[key_str] = (estimate, standard_error)
    return normalized


def build_evidence_input(
    *,
    belief_id: str,
    content: str,
    paper_id: str,
    supports_beliefs: Optional[Mapping[str, float]] = None,
    contradicts_beliefs: Optional[Mapping[str, float]] = None,
    theory_relevance: Optional[Mapping[str, float]] = None,
    observed_temporal: Optional[Mapping[str, tuple[float, float]]] = None,
    moderator: Optional[str] = None,
    credence: float = 0.6,
) -> EvidenceUpdateInput:
    payload = EvidenceUpdateInput(
        belief_id=str(belief_id).strip(),
        content=str(content).strip(),
        paper_id=str(paper_id).strip(),
        credence=_clamp_01(credence),
        supports_beliefs=normalize_strength_map(supports_beliefs),
        contradicts_beliefs=normalize_strength_map(contradicts_beliefs),
        theory_relevance=normalize_strength_map(theory_relevance),
        observed_temporal=normalize_temporal_observations(observed_temporal),
        moderator=moderator,
    )
    payload.validate()
    return payload


def init_updates_payload(coherence_before: float) -> dict[str, Any]:
    return {
        "belief_updates": [],
        "theory_world_updates": {},
        "temporal_updates": [],
        "coherence_before": float(coherence_before),
        "coherence_after": 0.0,
    }


def make_belief_update_record(
    belief_id: str,
    direction: str,
    old_credence: float,
    new_credence: float,
) -> dict[str, Any]:
    return {
        "belief_id": belief_id,
        "direction": direction,
        "old_credence": float(old_credence),
        "new_credence": float(new_credence),
    }


def make_temporal_update_record(
    belief_id: str,
    parameter: str,
    old_estimate: float,
    new_estimate: float,
    moderator: Optional[str],
) -> dict[str, Any]:
    return {
        "belief_id": belief_id,
        "parameter": parameter,
        "old_estimate": float(old_estimate),
        "new_estimate": float(new_estimate),
        "moderator": moderator,
    }


def ensure_theory_relevance(
    theory_relevance: dict[str, float],
    *,
    theory_id: Optional[str],
    strength: float,
    direction: str,
) -> None:
    """Fill inferred theory relevance only if the caller didn't provide it."""
    if not theory_id or theory_id in theory_relevance:
        return
    if direction == "supported":
        theory_relevance[theory_id] = _clamp_01(0.5 + 0.3 * strength)
        return
    theory_relevance[theory_id] = _clamp_01(0.5 - 0.3 * strength)


def make_theory_world_update_records(
    theory_ids: set[str],
    old_marginals: Mapping[str, float],
    new_marginals: Mapping[str, float],
) -> dict[str, dict[str, float]]:
    return {
        theory_id: {
            "old": float(old_marginals.get(theory_id, 0.5)),
            "new": float(new_marginals.get(theory_id, 0.5)),
        }
        for theory_id in theory_ids
    }

