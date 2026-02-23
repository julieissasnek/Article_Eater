"""Reflective-equilibrium adjustment contracts and helpers (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class EquilibriumChoice:
    """Selection of which belief to adjust for a tension."""

    belief_id: str
    reason: str


@dataclass(frozen=True)
class CredenceAdjustment:
    """One-step credence adjustment contract."""

    old_credence: float
    old_uncertainty: float
    n_supporting: int
    n_contradicting: int
    n_observations: int
    credence_decay: float = 0.85
    uncertainty_growth: float = 1.1
    uncertainty_cap: float = 0.5
    anomalous_threshold: float = 0.3

    def validate(self) -> None:
        if self.n_supporting < 0 or self.n_contradicting < 0 or self.n_observations < 0:
            raise ValueError("evidence counters must be >= 0")
        if not (0.0 < self.credence_decay <= 1.0):
            raise ValueError("credence_decay must be in (0, 1]")
        if self.uncertainty_growth <= 0.0:
            raise ValueError("uncertainty_growth must be > 0")
        if not (0.0 <= self.uncertainty_cap <= 1.0):
            raise ValueError("uncertainty_cap must be in [0, 1]")
        if not (0.0 <= self.anomalous_threshold <= 1.0):
            raise ValueError("anomalous_threshold must be in [0, 1]")


@dataclass(frozen=True)
class CredenceAdjustmentResult:
    """Output of one equilibrium adjustment step."""

    new_credence: float
    new_uncertainty: float
    new_n_supporting: int
    new_n_contradicting: int
    new_n_observations: int
    should_mark_anomalous: bool


def choose_adjustment_target(
    source_id: str,
    target_id: str,
    source_entrenchment: float,
    target_entrenchment: float,
) -> EquilibriumChoice:
    """Pick the less-entrenched belief as revision target."""

    if source_entrenchment < target_entrenchment:
        return EquilibriumChoice(
            belief_id=source_id,
            reason=f"in contradiction with more entrenched {target_id}",
        )
    return EquilibriumChoice(
        belief_id=target_id,
        reason=f"in contradiction with more entrenched {source_id}",
    )


def compute_credence_adjustment(payload: CredenceAdjustment) -> CredenceAdjustmentResult:
    """Apply bounded one-step equilibrium update to a belief credence."""

    payload.validate()
    new_credence = _clamp_01(payload.old_credence * payload.credence_decay)
    new_uncertainty = min(payload.uncertainty_cap, payload.old_uncertainty * payload.uncertainty_growth)
    return CredenceAdjustmentResult(
        new_credence=new_credence,
        new_uncertainty=new_uncertainty,
        new_n_supporting=payload.n_supporting,
        new_n_contradicting=payload.n_contradicting + 1,
        new_n_observations=payload.n_observations,
        should_mark_anomalous=new_credence < payload.anomalous_threshold,
    )

