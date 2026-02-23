"""Graph-level models extracted from web_of_belief monolith (ARCH-5d)."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional

from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief_components.enums import CausalDirection, PathwayType


@dataclass
class UncertainQuantity:
    """A quantity with uncertainty that can be refined by evidence."""

    estimate: float
    standard_error: float
    n_observations: int = 0
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    by_moderator: Dict[str, "UncertainQuantity"] = field(default_factory=dict)

    def update(
        self,
        observed: float,
        obs_se: float,
        weight: float = 1.0,
        moderator_key: Optional[str] = None,
    ) -> "UncertainQuantity":
        if self.n_observations == 0:
            new_estimate = observed
            new_se = obs_se
        else:
            prior_precision = 1 / (self.standard_error**2 + 1e-10)
            obs_precision = weight / (obs_se**2 + 1e-10)
            post_precision = prior_precision + obs_precision
            new_estimate = (
                prior_precision * self.estimate + obs_precision * observed
            ) / post_precision
            new_se = 1 / math.sqrt(post_precision)

        if self.lower_bound is not None:
            new_estimate = max(new_estimate, self.lower_bound)
        if self.upper_bound is not None:
            new_estimate = min(new_estimate, self.upper_bound)

        result = UncertainQuantity(
            estimate=new_estimate,
            standard_error=new_se,
            n_observations=self.n_observations + 1,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            by_moderator=copy.deepcopy(self.by_moderator),
        )

        if moderator_key:
            if moderator_key not in result.by_moderator:
                result.by_moderator[moderator_key] = UncertainQuantity(
                    estimate=observed,
                    standard_error=obs_se,
                    n_observations=1,
                    lower_bound=self.lower_bound,
                    upper_bound=self.upper_bound,
                )
            else:
                result.by_moderator[moderator_key] = result.by_moderator[
                    moderator_key
                ].update(observed, obs_se, weight)
        return result

    def heterogeneity(self) -> float:
        if len(self.by_moderator) < 2:
            return 0.0
        estimates = [uq.estimate for uq in self.by_moderator.values()]
        mean_est = sum(estimates) / len(estimates)
        variance = sum((e - mean_est) ** 2 for e in estimates) / len(estimates)
        if mean_est == 0:
            return 0.0
        return math.sqrt(variance) / abs(mean_est)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimate": self.estimate,
            "se": self.standard_error,
            "n": self.n_observations,
            "heterogeneity": self.heterogeneity(),
            "by_moderator": {k: v.estimate for k, v in self.by_moderator.items()},
        }


@dataclass
class Constraint:
    """A constraint relationship between beliefs."""

    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: ConstraintType
    strength: float = 0.5
    bidirectional: bool = True
    evidence_ids: List[str] = field(default_factory=list)
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    causal_evidence: Optional[str] = None
    mediator: Optional[str] = None
    pathway_type: Optional[PathwayType] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "source": self.source_id,
            "target": self.target_id,
            "type": self.constraint_type.value,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "causal_direction": self.causal_direction.value,
            "causal_evidence": self.causal_evidence,
            "mediator": self.mediator,
            "evidence_ids": self.evidence_ids.copy(),
            "pathway_type": self.pathway_type.value if self.pathway_type else None,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Constraint":
        causal_dir = d.get("causal_direction", "unknown")
        try:
            causal_direction = CausalDirection(causal_dir)
        except ValueError:
            causal_direction = CausalDirection.UNKNOWN

        pathway_type = None
        if d.get("pathway_type"):
            try:
                pathway_type = PathwayType(d["pathway_type"])
            except ValueError:
                pathway_type = None

        return cls(
            constraint_id=d.get("constraint_id", f"c:{d.get('source')}:{d.get('target')}"),
            source_id=d.get("source", d.get("source_id")),
            target_id=d.get("target", d.get("target_id")),
            constraint_type=ConstraintType(d.get("type", "supports")),
            strength=d.get("strength", 0.5),
            bidirectional=d.get("bidirectional", True),
            evidence_ids=d.get("evidence_ids", []),
            causal_direction=causal_direction,
            causal_evidence=d.get("causal_evidence"),
            mediator=d.get("mediator"),
            pathway_type=pathway_type,
        )


@dataclass
class TheoryWorld:
    """A possible world defined by which theories are true."""

    world_id: str
    theories_true: FrozenSet[str]
    theories_false: FrozenSet[str]
    prior: float = 0.0
    posterior: float = 0.0
    log_likelihood: float = 0.0

    def __hash__(self) -> int:
        return hash(self.world_id)

    def contains_theory(self, theory_id: str) -> Optional[bool]:
        if theory_id in self.theories_true:
            return True
        if theory_id in self.theories_false:
            return False
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "theories_true": list(self.theories_true),
            "theories_false": list(self.theories_false),
            "prior": self.prior,
            "posterior": self.posterior,
        }


__all__ = [
    "UncertainQuantity",
    "Constraint",
    "TheoryWorld",
]
