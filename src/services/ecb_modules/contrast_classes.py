"""Extracted contrast class data structures from epistemic_causal_bridge.py (ARCH-5e).

Contains van Fraassen contrast class structures, population contexts,
baseline specs, temporal specs, and transportability assessment types.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ContrastType(Enum):
    """Types of contrast class (van Fraassen)."""
    NULL = "null"
    ALTERNATIVE = "alternative"
    GRADIENT = "gradient"
    FACTORIAL = "factorial"
    POPULATION = "population"


class ContrastTransferType(Enum):
    """Types of contrast class transfer (van Fraassen, Panel P-ECB-R).

    ECB-3.1: Determines how to handle generalization across populations/contexts.
    """
    DIRECT = "direct"
    BASELINE_SHIFT = "baseline_shift"
    POPULATION_SHIFT = "population_shift"
    MEANING_SHIFT = "meaning_shift"
    UNDEFINED = "undefined"


CONTRAST_TRANSFER_THRESHOLDS: Dict[ContrastTransferType, float] = {
    ContrastTransferType.DIRECT: float(os.environ.get('AE_CONTRAST_THRESHOLD_DIRECT', '0.9')),
    ContrastTransferType.BASELINE_SHIFT: float(os.environ.get('AE_CONTRAST_THRESHOLD_BASELINE', '0.7')),
    ContrastTransferType.POPULATION_SHIFT: float(os.environ.get('AE_CONTRAST_THRESHOLD_POPULATION', '0.5')),
}


@dataclass
class ConditionSpec:
    """Specification of a condition in a contrast."""
    variable: str
    value: Any
    description: str
    contextual_meaning: Dict[str, str] = field(default_factory=dict)


@dataclass
class BaselineSpec:
    """Baseline level of a variable in a population."""
    variable: str
    typical_value: float
    variance: float
    characterization: str
    source_studies: List[str] = field(default_factory=list)
    temporal_variation: Optional[Dict[str, float]] = None

    def is_saturated(self) -> bool:
        return self.characterization in ["high", "saturated"]

    def distance_from(self, other: BaselineSpec) -> float:
        levels = ["very_low", "low", "moderate", "high", "saturated"]
        try:
            self_idx = levels.index(self.characterization)
            other_idx = levels.index(other.characterization)
            return abs(self_idx - other_idx) / (len(levels) - 1)
        except ValueError:
            return 0.5


@dataclass
class TemporalSpec:
    """Structured temporal specification for enabling conditions (PA-6)."""
    magnitude: float
    unit: str = "seconds"
    direction: str = "precedes"

    @property
    def seconds(self) -> float:
        multipliers = {
            'second': 1, 'seconds': 1, 'sec': 1, 's': 1,
            'minute': 60, 'minutes': 60, 'min': 60, 'm': 60,
            'hour': 3600, 'hours': 3600, 'hr': 3600, 'h': 3600,
            'day': 86400, 'days': 86400, 'd': 86400,
        }
        return self.magnitude * multipliers.get(self.unit.lower(), 1)

    def display(self, target_unit: Optional[str] = None) -> str:
        if target_unit:
            divisors = {'seconds': 1, 'minutes': 60, 'hours': 3600, 'days': 86400}
            value = self.seconds / divisors.get(target_unit, 1)
            return f"{value:.1f} {target_unit} ({self.direction})"
        secs = self.seconds
        if secs < 60:
            return f"{secs:.0f} seconds ({self.direction})"
        elif secs < 3600:
            return f"{secs/60:.1f} minutes ({self.direction})"
        elif secs < 86400:
            return f"{secs/3600:.1f} hours ({self.direction})"
        else:
            return f"{secs/86400:.1f} days ({self.direction})"

    @classmethod
    def parse(cls, condition: str) -> Optional[TemporalSpec]:
        direction = "precedes"
        if 'follows' in condition.lower():
            direction = "follows"
        elif 'precedes' in condition.lower():
            direction = "precedes"

        pattern = r'[><= ]*\s*(\d+(?:\.\d+)?)\s*(second|minute|hour|day|sec|min|hr|s|m|h|d)s?'
        match = re.search(pattern, condition.lower())
        if not match:
            return None

        magnitude = float(match.group(1))
        unit = match.group(2)
        unit_map = {
            'second': 'seconds', 'sec': 'seconds', 's': 'seconds',
            'minute': 'minutes', 'min': 'minutes', 'm': 'minutes',
            'hour': 'hours', 'hr': 'hours', 'h': 'hours',
            'day': 'days', 'd': 'days',
        }
        unit = unit_map.get(unit, 'seconds')
        return cls(magnitude=magnitude, unit=unit, direction=direction)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'magnitude': self.magnitude,
            'unit': self.unit,
            'direction': self.direction,
            'seconds': self.seconds,
        }


@dataclass
class CulturalMeaning:
    """Cultural meaning of a construct."""
    culture: str
    meaning: str
    associations: List[str]
    valence: str
    behavioral_implications: str


@dataclass
class DistributionSpec:
    """Distribution of an individual difference in a population."""
    mean: float
    sd: float
    skew: float = 0.0
    note: str = ""


@dataclass
class PopulationContext:
    """Population context defining the contrast class."""
    population_id: str
    region: Optional[str] = None
    culture: Optional[str] = None
    baselines: Dict[str, BaselineSpec] = field(default_factory=dict)
    cultural_meanings: Dict[str, CulturalMeaning] = field(default_factory=dict)
    individual_difference_distributions: Dict[str, DistributionSpec] = field(
        default_factory=dict
    )

    def get_baseline(self, variable: str) -> Optional[BaselineSpec]:
        return self.baselines.get(variable)

    def get_meaning(self, construct: str) -> Optional[CulturalMeaning]:
        return self.cultural_meanings.get(construct)


@dataclass
class ContrastClass:
    """Van Fraassen contrast class specification."""
    contrast_id: str
    focal: ConditionSpec
    contrasts: List[ConditionSpec]
    contrast_type: ContrastType
    population_context: PopulationContext
    explicit: bool = False
    source: str = "inferred"

    def describe(self) -> str:
        focal_desc = self.focal.description
        contrast_descs = [c.description for c in self.contrasts]
        return f"{focal_desc} rather than {', '.join(contrast_descs)}"

    def involves_variable(self, variable: str) -> bool:
        if self.focal.variable == variable:
            return True
        return any(c.variable == variable for c in self.contrasts)


@dataclass
class BeliefScope:
    """Scope constraints on a belief (van Fraassen contrast terms)."""
    populations: List[str] = field(default_factory=list)
    settings: List[str] = field(default_factory=list)
    temporal_bounds: Optional[Tuple[float, float]] = None
    n_studies: int = 0
    population_coverage: Dict[str, int] = field(default_factory=dict)
    setting_coverage: Dict[str, int] = field(default_factory=dict)
    tested_contrasts: List[ContrastClass] = field(default_factory=list)
    untested_contrasts: List[ContrastClass] = field(default_factory=list)
    assumed_contrasts: List[ContrastClass] = field(default_factory=list)

    def coverage_for(self, population: str) -> float:
        if self.n_studies == 0:
            return 0.0
        return self.population_coverage.get(population, 0) / self.n_studies


@dataclass
class SelectionVariable:
    """Pearl/Bareinboim selection-node style descriptor."""
    name: str
    source_value: str
    target_value: str
    impact: str


@dataclass
class TransportabilityAssessment:
    """Summary of transportability analysis."""
    belief_id: str
    transfer_type: ContrastTransferType
    similarity: float
    selection_variables: List[SelectionVariable] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


__all__ = [
    "ContrastType",
    "ContrastTransferType",
    "CONTRAST_TRANSFER_THRESHOLDS",
    "ConditionSpec",
    "BaselineSpec",
    "TemporalSpec",
    "CulturalMeaning",
    "DistributionSpec",
    "PopulationContext",
    "ContrastClass",
    "BeliefScope",
    "SelectionVariable",
    "TransportabilityAssessment",
]
