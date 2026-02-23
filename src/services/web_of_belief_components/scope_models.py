"""Scope and provenance support models extracted from web_of_belief (ARCH-5d)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ScopeConditions:
    """Scope conditions for beliefs."""

    population: Optional[str] = None
    setting: Optional[str] = None
    duration: Optional[str] = None
    measurement: Optional[str] = None
    geography: Optional[str] = None
    moderators: List[str] = field(default_factory=list)
    scope_specified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "population": self.population,
            "setting": self.setting,
            "duration": self.duration,
            "measurement": self.measurement,
            "geography": self.geography,
            "moderators": self.moderators.copy(),
            "scope_specified": self.scope_specified,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ScopeConditions":
        return cls(
            population=d.get("population"),
            setting=d.get("setting"),
            duration=d.get("duration"),
            measurement=d.get("measurement"),
            geography=d.get("geography"),
            moderators=d.get("moderators", []),
            scope_specified=d.get("scope_specified", False),
        )


@dataclass
class EnablingConditions:
    """Enabling conditions for a belief to manifest its effect."""

    minimum_exposure: Optional[str] = None
    baseline_state: Optional[str] = None
    concurrent_factors: List[str] = field(default_factory=list)
    blocking_factors: List[str] = field(default_factory=list)
    threshold: Optional[str] = None
    dosage: Optional[str] = None
    temporal_order: Optional[str] = None
    dose_response: Optional[bool] = None
    dosage_satisfies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimum_exposure": self.minimum_exposure,
            "baseline_state": self.baseline_state,
            "concurrent_factors": self.concurrent_factors.copy(),
            "blocking_factors": self.blocking_factors.copy(),
            "threshold": self.threshold,
            "dosage": self.dosage,
            "dosage_satisfies": self.dosage_satisfies.copy(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EnablingConditions":
        return cls(
            minimum_exposure=d.get("minimum_exposure"),
            baseline_state=d.get("baseline_state"),
            concurrent_factors=d.get("concurrent_factors", []),
            blocking_factors=d.get("blocking_factors", []),
            threshold=d.get("threshold"),
            dosage=d.get("dosage"),
            dosage_satisfies=d.get("dosage_satisfies", []),
        )

    def is_empty(self) -> bool:
        return (
            self.minimum_exposure is None
            and self.baseline_state is None
            and len(self.concurrent_factors) == 0
            and len(self.blocking_factors) == 0
            and self.threshold is None
            and self.dosage is None
        )


@dataclass
class CredenceHistoryEntry:
    """A single entry in a belief's credence history."""

    timestamp: datetime
    credence_value: float
    delta: float
    triggered_by: Optional[str]
    update_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "credence_value": self.credence_value,
            "delta": self.delta,
            "triggered_by": self.triggered_by,
            "update_reason": self.update_reason,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CredenceHistoryEntry":
        ts = d.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return cls(
            timestamp=ts,
            credence_value=d.get("credence_value", 0.5),
            delta=d.get("delta", 0.0),
            triggered_by=d.get("triggered_by"),
            update_reason=d.get("update_reason", ""),
        )


__all__ = [
    "ScopeConditions",
    "EnablingConditions",
    "CredenceHistoryEntry",
]
