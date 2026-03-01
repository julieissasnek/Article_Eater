"""
T2 Mechanism Template Archetypes — Sprint 7
============================================
Created: 2026-02-28
Panel: B (Computational Architecture), Decisions B1, B3

Six computational archetypes that recur across T2 empirical templates.
These provide a grammar for composing mechanistic explanations.

References:
- Friston, K. (2010). The free-energy principle. Nature Reviews Neuroscience.
- Clark, A. (2013). Whatever next? Predictive brains, situated agents.
- Ratcliff, R. & McKoon, G. (2008). The diffusion decision model.
- Desimone, R. & Duncan, J. (1995). Neural mechanisms of selective attention.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class T2ArchetypeType(Enum):
    """Six computational archetypes recurring across T2 empirical templates."""
    PREDICTIVE_CODING = "predictive_coding"
    HOMEOSTATIC_REGULATION = "homeostatic_regulation"
    ACCUMULATION_TO_BOUND = "accumulation_to_bound"
    COMPETITIVE_SELECTION = "competitive_selection"
    GATED_PROPAGATION = "gated_propagation"
    CONVERGENT_STATE_MONITORING = "convergent_state_monitoring"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ParameterSpec:
    """Specification of a parameter in a mechanistic archetype."""
    name: str
    default_value: float
    min_value: float
    max_value: float
    unit: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ParameterSpec:
        """Create from dictionary."""
        return ParameterSpec(**d)


@dataclass
class DomainExample:
    """Example of an archetype applied in a specific domain."""
    domain: str
    template_id: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> DomainExample:
        """Create from dictionary."""
        return DomainExample(**d)


@dataclass
class T2Archetype:
    """Base class for T2 computational archetypes."""
    archetype_id: str
    archetype_type: T2ArchetypeType
    name: str
    description: str
    theoretical_basis: List[str]  # Key citations
    input_variables: List[str]
    output_variables: List[str]
    parameters: Dict[str, ParameterSpec]
    domain_examples: List[DomainExample]
    computational_signature: str
    t1_framework_links: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["archetype_type"] = self.archetype_type.value
        d["parameters"] = {k: v.to_dict() for k, v in self.parameters.items()}
        d["domain_examples"] = [ex.to_dict() for ex in self.domain_examples]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> T2Archetype:
        """Create from dictionary."""
        d = d.copy()
        d["archetype_type"] = T2ArchetypeType(d["archetype_type"])
        d["parameters"] = {
            k: ParameterSpec.from_dict(v)
            for k, v in d.get("parameters", {}).items()
        }
        d["domain_examples"] = [
            DomainExample.from_dict(ex)
            for ex in d.get("domain_examples", [])
        ]

        # Only pass base class fields to T2Archetype
        base_fields = {
            "archetype_id", "archetype_type", "name", "description",
            "theoretical_basis", "input_variables", "output_variables",
            "parameters", "domain_examples", "computational_signature",
            "t1_framework_links"
        }
        base_dict = {k: v for k, v in d.items() if k in base_fields}
        return T2Archetype(**base_dict)


@dataclass
class PredictiveCodingArchetype(T2Archetype):
    """
    Predictive Coding: Prediction error minimization via hierarchical
    inference and precision-weighted belief updating.
    """
    precision_weighted: bool = True
    hierarchical_levels: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["precision_weighted"] = self.precision_weighted
        d["hierarchical_levels"] = self.hierarchical_levels
        return d


@dataclass
class HomeostaticRegulationArchetype(T2Archetype):
    """
    Homeostatic Regulation: Deviation from setpoint triggers corrective
    responses via negative feedback. Includes adaptation over time.
    """
    setpoint_variable: str = ""
    feedback_type: str = "negative"
    adaptation_rate: float = 0.1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["setpoint_variable"] = self.setpoint_variable
        d["feedback_type"] = self.feedback_type
        d["adaptation_rate"] = self.adaptation_rate
        return d


@dataclass
class AccumulationToBoundArchetype(T2Archetype):
    """
    Accumulation to Bound: Evidence accumulation over time until
    reaching a decision threshold. Generates reaction time distributions.
    """
    threshold: float = 1.0
    drift_rate: float = 0.0
    noise_level: float = 0.5
    boundary_type: str = "absorbing"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["threshold"] = self.threshold
        d["drift_rate"] = self.drift_rate
        d["noise_level"] = self.noise_level
        d["boundary_type"] = self.boundary_type
        return d


@dataclass
class CompetitiveSelectionArchetype(T2Archetype):
    """
    Competitive Selection: Multiple options compete via mutual inhibition
    until one 'wins' via lateral inhibition or divisive normalization.
    """
    n_competitors: int = 4
    selection_mechanism: str = "winner_take_all"
    inhibition_type: str = "lateral"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["n_competitors"] = self.n_competitors
        d["selection_mechanism"] = self.selection_mechanism
        d["inhibition_type"] = self.inhibition_type
        return d


@dataclass
class GatedPropagationArchetype(T2Archetype):
    """
    Gated Propagation: Information flow is modulated by a gate signal
    (multiplicative or additive gating). Implements selective attention
    and working memory constraints.
    """
    gate_variable: str = ""
    modulation_type: str = "multiplicative"
    default_state: str = "closed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["gate_variable"] = self.gate_variable
        d["modulation_type"] = self.modulation_type
        d["default_state"] = self.default_state
        return d


@dataclass
class ConvergentStateMonitoringArchetype(T2Archetype):
    """
    Convergent State Monitoring: Multiple noisy sensors/modalities are
    integrated into a coherent state estimate. Confidence reflects
    agreement among sensors.
    """
    n_sensors: int = 3
    convergence_criterion: str = "weighted_mean"
    conflict_resolution: str = "reliability_weighted"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = super().to_dict()
        d["n_sensors"] = self.n_sensors
        d["convergence_criterion"] = self.convergence_criterion
        d["conflict_resolution"] = self.conflict_resolution
        return d


# =============================================================================
# REGISTRY
# =============================================================================

class T2ArchetypeRegistry:
    """Registry of T2 computational archetypes."""

    def __init__(self):
        """Initialize empty registry."""
        self._archetypes: Dict[str, T2Archetype] = {}

    def register(self, archetype: T2Archetype) -> None:
        """Register an archetype."""
        self._archetypes[archetype.archetype_id] = archetype

    def get(self, archetype_id: str) -> Optional[T2Archetype]:
        """Get archetype by ID."""
        return self._archetypes.get(archetype_id)

    def get_by_type(self, archetype_type: T2ArchetypeType) -> List[T2Archetype]:
        """Get all archetypes of a given type."""
        return [
            a for a in self._archetypes.values()
            if a.archetype_type == archetype_type
        ]

    def list_all(self) -> List[T2Archetype]:
        """List all registered archetypes."""
        return list(self._archetypes.values())

    def match_mechanism_text(
        self, text: str
    ) -> List[Tuple[T2Archetype, float]]:
        """
        Fuzzy match mechanism description to known archetypes.

        Uses keyword overlap scoring:
        - Exact name matches: 1.0
        - Keyword hits in description: partial score
        - Computational signature matches: partial score

        Args:
            text: Mechanism description to match

        Returns:
            List of (archetype, score) tuples, sorted by score descending
        """
        text_lower = text.lower()
        scores = []

        for archetype in self._archetypes.values():
            score = 0.0

            # Exact name match
            if archetype.name.lower() in text_lower:
                score += 1.0

            # Check description keywords
            for keyword in archetype.description.lower().split():
                if keyword in text_lower:
                    score += 0.05

            # Check computational signature
            if archetype.computational_signature.lower() in text_lower:
                score += 0.3

            if score > 0:
                scores.append((archetype, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def validate_template_mechanism(
        self, template: Dict[str, Any]
    ) -> List[str]:
        """
        Validate template mechanism chain against known archetypes.

        Args:
            template: Template dictionary with mechanism_chain

        Returns:
            List of warning strings (empty if all valid)
        """
        warnings = []

        if "mechanism_chain" not in template:
            warnings.append("No mechanism_chain field found")
            return warnings

        mechanism_chain = template.get("mechanism_chain", [])
        if not mechanism_chain:
            warnings.append("mechanism_chain is empty")
            return warnings

        for i, step in enumerate(mechanism_chain):
            if not isinstance(step, dict):
                warnings.append(f"Step {i}: not a dict")
                continue

            mechanism_text = step.get("mechanism", "")
            if not mechanism_text:
                warnings.append(f"Step {i}: no mechanism text")
                continue

            matches = self.match_mechanism_text(mechanism_text)
            if not matches or matches[0][1] < 0.1:
                warnings.append(
                    f"Step {i}: mechanism '{mechanism_text}' "
                    f"does not match known archetypes"
                )

        return warnings

    def load_from_json_file(self, json_path: Path) -> None:
        """
        Load archetypes from JSON file.

        Expected format:
        {
            "archetypes": [
                { archetype dict 1 },
                { archetype dict 2 },
                ...
            ]
        }
        """
        with open(json_path, "r") as f:
            data = json.load(f)

        archetype_dicts = data.get("archetypes", [])
        for arch_dict in archetype_dicts:
            arch_dict = arch_dict.copy()
            arch_dict["archetype_type"] = T2ArchetypeType(
                arch_dict["archetype_type"]
            )
            arch_dict["parameters"] = {
                k: ParameterSpec.from_dict(v)
                for k, v in arch_dict.get("parameters", {}).items()
            }
            arch_dict["domain_examples"] = [
                DomainExample.from_dict(ex)
                for ex in arch_dict.get("domain_examples", [])
            ]

            archetype_type = arch_dict["archetype_type"]

            # Create appropriate subclass based on type
            if archetype_type == T2ArchetypeType.PREDICTIVE_CODING:
                arch = PredictiveCodingArchetype(**arch_dict)
            elif archetype_type == T2ArchetypeType.HOMEOSTATIC_REGULATION:
                arch = HomeostaticRegulationArchetype(**arch_dict)
            elif archetype_type == T2ArchetypeType.ACCUMULATION_TO_BOUND:
                arch = AccumulationToBoundArchetype(**arch_dict)
            elif archetype_type == T2ArchetypeType.COMPETITIVE_SELECTION:
                arch = CompetitiveSelectionArchetype(**arch_dict)
            elif archetype_type == T2ArchetypeType.GATED_PROPAGATION:
                arch = GatedPropagationArchetype(**arch_dict)
            elif archetype_type == T2ArchetypeType.CONVERGENT_STATE_MONITORING:
                arch = ConvergentStateMonitoringArchetype(**arch_dict)
            else:
                arch = T2Archetype(**arch_dict)

            self.register(arch)

    def save_to_json_file(self, json_path: Path) -> None:
        """Save all archetypes to JSON file."""
        data = {
            "archetypes": [a.to_dict() for a in self._archetypes.values()]
        }
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
