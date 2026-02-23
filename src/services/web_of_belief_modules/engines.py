"""Engine facades for decomposed WebOfBelief subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence

from .coherence import CoherenceResult, compute_coherence_state
from .reporting import build_web_dict, build_web_summary
from .snapshots import (
    build_snapshot_fields,
    snapshot_anomalies,
    snapshot_beliefs_by_level,
    snapshot_stubs,
    snapshot_to_dict,
)
from .theory_worlds import (
    build_theory_worlds,
    canonical_world_id,
    conditional_probability,
    joint_probability,
    marginal_probability,
    update_world_posteriors,
)


@dataclass
class CoherenceEngine:
    def recompute(
        self,
        *,
        beliefs: Mapping[str, Any],
        constraints: Iterable[Any],
    ) -> CoherenceResult:
        return compute_coherence_state(beliefs=beliefs, constraints=constraints)


@dataclass
class TheoryWorldEngine:
    def rebuild_worlds(
        self,
        *,
        theory_ids: Iterable[str],
        theory_priors: Mapping[str, float],
    ) -> dict[str, Any]:
        return build_theory_worlds(theory_ids=theory_ids, theory_priors=theory_priors)

    def world_id(self, true_set: set[str], false_set: set[str]) -> str:
        return canonical_world_id(true_set=true_set, false_set=false_set)

    def update_posteriors(
        self,
        *,
        worlds: Mapping[str, Any],
        theory_ids: Iterable[str],
        theory_likelihoods: Mapping[str, float],
    ) -> None:
        update_world_posteriors(
            worlds=worlds,
            theory_ids=theory_ids,
            theory_likelihoods=theory_likelihoods,
        )

    def marginal(
        self,
        *,
        worlds: Mapping[str, Any],
        theory_id: str,
        default: float = 0.5,
    ) -> float:
        return marginal_probability(worlds=worlds, theory_id=theory_id, default=default)

    def joint(
        self,
        *,
        worlds: Mapping[str, Any],
        true_theories: set[str],
    ) -> float:
        return joint_probability(worlds=worlds, true_theories=true_theories)

    def conditional(
        self,
        *,
        worlds: Mapping[str, Any],
        target_theory: str,
        given_theories: Mapping[str, bool],
        default: float = 0.5,
    ) -> float:
        return conditional_probability(
            worlds=worlds,
            target_theory=target_theory,
            given_theories=given_theories,
            default=default,
        )


@dataclass
class ReportingEngine:
    def summary(
        self,
        *,
        domain: str,
        version: int,
        coherence_score: float,
        tensions: Sequence[Mapping[str, Any]],
        beliefs_by_level: Mapping[Any, Sequence[Any]],
        stubs: Sequence[Any],
        n_stubs_total: int,
        theory_ids: Iterable[str],
        theory_worlds: Mapping[str, Any],
        theory_marginals: Mapping[str, float],
    ) -> str:
        return build_web_summary(
            domain=domain,
            version=version,
            coherence_score=coherence_score,
            tensions=tensions,
            beliefs_by_level=beliefs_by_level,
            stubs=stubs,
            n_stubs_total=n_stubs_total,
            theory_ids=theory_ids,
            theory_worlds=theory_worlds,
            theory_marginals=theory_marginals,
        )

    def to_dict(
        self,
        *,
        domain: str,
        version: int,
        n_beliefs: int,
        n_constraints: int,
        n_stubs: int,
        coherence: float,
        n_tensions: int,
        theory_marginals: Mapping[str, float],
    ) -> dict[str, Any]:
        return build_web_dict(
            domain=domain,
            version=version,
            n_beliefs=n_beliefs,
            n_constraints=n_constraints,
            n_stubs=n_stubs,
            coherence=coherence,
            n_tensions=n_tensions,
            theory_marginals=theory_marginals,
        )


@dataclass
class SnapshotEngine:
    def build_fields(
        self,
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
        return build_snapshot_fields(
            domain=domain,
            version=version,
            beliefs=beliefs,
            constraints=constraints,
            coherence_score=coherence_score,
            tensions=tensions,
            theory_ids=theory_ids,
            stubs=stubs,
        )

    def beliefs_by_level(self, beliefs: Mapping[str, Any], level: Any) -> list[Any]:
        return snapshot_beliefs_by_level(beliefs, level)

    def stubs(self, beliefs: Mapping[str, Any], stubs: set[str]) -> list[Any]:
        return snapshot_stubs(beliefs, stubs)

    def anomalies(self, beliefs: Mapping[str, Any], anomalous_status: Any) -> list[Any]:
        return snapshot_anomalies(beliefs, anomalous_status)

    def to_dict(
        self,
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
        return snapshot_to_dict(
            domain=domain,
            version=version,
            beliefs=beliefs,
            constraints=constraints,
            stubs=stubs,
            coherence_score=coherence_score,
            tensions=tensions,
            snapshot_at=snapshot_at,
        )


@dataclass
class WebOfBeliefEngines:
    """Engine bundle attached to WebOfBelief facade."""

    coherence: CoherenceEngine = field(default_factory=CoherenceEngine)
    theory_worlds: TheoryWorldEngine = field(default_factory=TheoryWorldEngine)
    reporting: ReportingEngine = field(default_factory=ReportingEngine)
    snapshots: SnapshotEngine = field(default_factory=SnapshotEngine)

