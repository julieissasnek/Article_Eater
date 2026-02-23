"""Snapshot construction/helpers for WebOfBelief (ARCH-5d)."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Mapping


def build_snapshot_fields(
    *,
    domain: str,
    version: int,
    beliefs: Mapping[str, Any],
    constraints: Mapping[str, Any],
    coherence_score: float,
    tensions: list[dict[str, Any]],
    theory_ids: set[str],
    stubs: set[str],
) -> dict[str, Any]:
    """Create deep-copied snapshot fields for immutable query state."""
    return {
        "domain": domain,
        "version": version,
        "beliefs": copy.deepcopy(beliefs),
        "constraints": copy.deepcopy(constraints),
        "coherence_score": coherence_score,
        "tensions": copy.deepcopy(tensions),
        "theory_ids": copy.deepcopy(theory_ids),
        "stubs": copy.deepcopy(stubs),
        "snapshot_at": datetime.now(timezone.utc),
    }


def snapshot_beliefs_by_level(
    beliefs: Mapping[str, Any],
    level: Any,
) -> list[Any]:
    return [belief for belief in beliefs.values() if belief.level == level]


def snapshot_stubs(
    beliefs: Mapping[str, Any],
    stubs: set[str],
) -> list[Any]:
    return [beliefs[belief_id] for belief_id in stubs if belief_id in beliefs]


def snapshot_anomalies(
    beliefs: Mapping[str, Any],
    anomalous_status: Any,
) -> list[Any]:
    return [belief for belief in beliefs.values() if belief.status == anomalous_status]


def snapshot_to_dict(
    *,
    domain: str,
    version: int,
    beliefs: Mapping[str, Any],
    constraints: Mapping[str, Any],
    stubs: set[str],
    coherence_score: float,
    tensions: list[dict[str, Any]],
    snapshot_at: datetime,
) -> dict[str, Any]:
    return {
        "domain": domain,
        "version": version,
        "n_beliefs": len(beliefs),
        "n_constraints": len(constraints),
        "n_stubs": len(stubs),
        "coherence": coherence_score,
        "n_tensions": len(tensions),
        "snapshot_at": snapshot_at.isoformat(),
    }

