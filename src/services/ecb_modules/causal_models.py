"""Extracted causal model structures from epistemic_causal_bridge.py (ARCH-5e).

Contains Variable, StructuralEquation, TheoryRelativeModel,
and MultiTheoryModel — the Pearlian causal layer data types.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Variable:
    """A variable in the causal model."""
    var_id: str
    name: str
    var_type: str  # "continuous", "binary", "categorical"
    domain: Optional[Tuple[float, float]] = None
    categories: Optional[List[str]] = None


@dataclass
class StructuralEquation:
    """A structural equation: Y = f(parents, U).

    Extended with epistemic metadata from the Quinean layer.
    ECB-2.2 (Cartwright): Enabling conditions GATE computation.
    """
    equation_id: str
    outcome_var: str
    parent_vars: List[str]

    functional_form: str = "linear"
    parameters: Dict[str, float] = field(default_factory=dict)

    supporting_beliefs: List[str] = field(default_factory=list)
    credence: float = 0.5
    uncertainty: float = 0.3
    entrenchment: float = 0.3

    theory_id: Optional[str] = None
    enabling_conditions: Optional[Any] = None

    def is_applicable(self, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Check if this equation is applicable given the context."""
        if self.enabling_conditions is None:
            return (True, "No enabling conditions specified")
        if context is None:
            return (False, "Context required but not provided")

        ec = self.enabling_conditions

        if hasattr(ec, 'minimum_exposure') and ec.minimum_exposure:
            exposure = context.get('exposure_duration')
            if exposure is None:
                return (False, f"Minimum exposure required: {ec.minimum_exposure}")
            satisfied, reason, operator_inferred = self._check_threshold_condition(
                ec.minimum_exposure, exposure, 'exposure_duration'
            )
            if operator_inferred:
                logger.warning(
                    "Operator inferred as '>=' for condition '%s'. "
                    "Consider using explicit operator.", ec.minimum_exposure
                )
            if not satisfied:
                return (False, reason)

        if hasattr(ec, 'baseline_state') and ec.baseline_state:
            baseline = context.get('baseline_state')
            if baseline != ec.baseline_state:
                return (False, f"Baseline state required: {ec.baseline_state}, got: {baseline}")

        if hasattr(ec, 'concurrent_factors') and ec.concurrent_factors:
            present = set(context.get('concurrent_factors', []))
            required = set(ec.concurrent_factors)
            missing = required - present
            if missing:
                return (False, f"Missing concurrent factors: {missing}")

        if hasattr(ec, 'blocking_factors') and ec.blocking_factors:
            present = set(context.get('blocking_factors', []))
            blockers = set(ec.blocking_factors)
            blocking = present & blockers
            if blocking:
                return (False, f"Blocking factors present: {blocking}")

        if hasattr(ec, 'threshold') and ec.threshold:
            threshold_val = context.get('threshold_value')
            if threshold_val is None:
                return (False, f"Threshold required: {ec.threshold}")
            satisfied, reason, operator_inferred = self._check_threshold_condition(
                ec.threshold, threshold_val, 'threshold_value'
            )
            if operator_inferred:
                logger.warning(
                    "Operator inferred as '>=' for condition '%s'. "
                    "Consider using explicit operator.", ec.threshold
                )
            if not satisfied:
                return (False, reason)

        if hasattr(ec, 'dosage') and ec.dosage:
            dosage_freq = context.get('dosage_frequency')
            if dosage_freq is None:
                return (False, f"Dosage requirement: {ec.dosage}")
            required_dosage = ec.dosage.lower()
            actual_dosage = str(dosage_freq).lower()
            acceptable = getattr(ec, 'dosage_satisfies', None) or []
            if not self._dosage_satisfies(required_dosage, actual_dosage, acceptable):
                return (False, f"Dosage insufficient: requires {ec.dosage}, got {dosage_freq}")

        if hasattr(ec, 'temporal_order') and ec.temporal_order:
            temporal_lag = context.get('temporal_lag')
            if temporal_lag is None:
                return (False, f"Temporal order required: {ec.temporal_order}")
            check_result = self._check_temporal_condition(ec.temporal_order, temporal_lag)
            if not check_result[0]:
                return check_result

        return (True, "All enabling conditions met")

    def _check_threshold_condition(
        self, condition: str, value: Any, var_name: str
    ) -> Tuple[bool, str, bool]:
        """Parse and check threshold conditions."""
        pattern = r'^([><= ]+)?\s*(\d+(?:\.\d+)?)\s*(.*)$'
        match = re.match(pattern, condition.strip())
        if not match:
            return (True, f"Threshold condition '{condition}' not parseable, allowing", False)

        explicit_operator = match.group(1)
        operator_inferred = explicit_operator is None
        op = (explicit_operator or '>=').strip()
        threshold_num = float(match.group(2))

        try:
            if isinstance(value, (int, float)):
                actual_val = float(value)
            elif isinstance(value, str):
                val_match = re.search(r'(\d+(?:\.\d+)?)', value)
                if val_match:
                    actual_val = float(val_match.group(1))
                else:
                    return (False, f"Cannot parse numeric value from: {value}", operator_inferred)
            else:
                return (False, f"Cannot compare threshold with type: {type(value)}", operator_inferred)
        except (ValueError, TypeError):
            return (False, f"Cannot convert {value} to number for threshold check", operator_inferred)

        if op == '>':
            satisfied = actual_val > threshold_num
        elif op == '>=':
            satisfied = actual_val >= threshold_num
        elif op == '<':
            satisfied = actual_val < threshold_num
        elif op == '<=':
            satisfied = actual_val <= threshold_num
        elif op in ('=', '=='):
            satisfied = abs(actual_val - threshold_num) < 0.001
        else:
            return (True, f"Unknown operator '{op}', allowing", operator_inferred)

        if satisfied:
            return (True, f"{var_name} {actual_val} satisfies {condition}", operator_inferred)
        else:
            return (False, f"{var_name} {actual_val} does not satisfy {condition}", operator_inferred)

    def _dosage_satisfies(
        self, required: str, actual: str,
        acceptable_patterns: Optional[List[str]] = None,
    ) -> bool:
        """Check if actual dosage frequency satisfies requirement (PA-2)."""
        if acceptable_patterns:
            return actual in [p.lower() for p in acceptable_patterns] or actual == required
        return actual == required

    def _check_temporal_condition(
        self, condition: str, temporal_lag: Any,
    ) -> Tuple[bool, str]:
        """Check temporal order conditions (D2.5, PA-6)."""
        from .contrast_classes import TemporalSpec

        spec = TemporalSpec.parse(condition)
        if spec is None:
            return (True, f"Cannot parse temporal condition '{condition}', allowing")

        if isinstance(temporal_lag, (int, float)):
            lag_seconds = float(temporal_lag)
        elif hasattr(temporal_lag, 'seconds'):
            lag_seconds = temporal_lag.seconds
        else:
            return (False, f"Cannot interpret temporal_lag: {temporal_lag}")

        if lag_seconds >= spec.seconds:
            return (True, f"Temporal lag {lag_seconds}s >= required {spec.seconds}s")
        else:
            return (False, f"Temporal lag {lag_seconds}s < required {spec.seconds}s ({spec.display()})")

    def compute(self, parent_values: Dict[str, float], noise: float = 0.0) -> float:
        """Compute outcome given parent values."""
        if self.functional_form == "linear":
            result = sum(
                self.parameters.get(f"beta_{var}", 0.0) * parent_values.get(var, 0.0)
                for var in self.parent_vars
            )
            result += self.parameters.get("intercept", 0.0) + noise
            return result
        elif self.functional_form == "threshold":
            input_var = self.parent_vars[0] if self.parent_vars else ""
            threshold = self.parameters.get("threshold", 0.5)
            effect = self.parameters.get("effect", 1.0)
            val = parent_values.get(input_var, 0.0)
            return effect if val >= threshold else 0.0
        else:
            return sum(parent_values.values()) / max(len(parent_values), 1) + noise


@dataclass
class TheoryRelativeModel:
    """A causal model relative to a specific theory."""
    model_id: str
    theory_id: str
    theory_credence: float
    variables: Dict[str, Variable] = field(default_factory=dict)
    equations: Dict[str, StructuralEquation] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)

    def get_parents(self, var: str) -> List[str]:
        return [src for src, tgt in self.edges if tgt == var]

    def get_children(self, var: str) -> List[str]:
        return [tgt for src, tgt in self.edges if src == var]

    def topological_sort(self) -> List[str]:
        in_degree: Dict[str, int] = {v: 0 for v in self.variables}
        for src, tgt in self.edges:
            if tgt in in_degree:
                in_degree[tgt] += 1
        queue = [v for v, d in in_degree.items() if d == 0]
        result: List[str] = []
        while queue:
            v = queue.pop(0)
            result.append(v)
            for child in self.get_children(v):
                if child in in_degree:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        queue.append(child)
        return result


@dataclass
class MultiTheoryModel:
    """Collection of theory-relative models for integrated inference."""
    domain: str
    theory_models: Dict[str, TheoryRelativeModel] = field(default_factory=dict)
    theory_credences: Dict[str, float] = field(default_factory=dict)

    def add_theory_model(self, model: TheoryRelativeModel) -> None:
        self.theory_models[model.theory_id] = model
        self.theory_credences[model.theory_id] = model.theory_credence

    def get_all_variables(self) -> set:
        all_vars = set()
        for model in self.theory_models.values():
            all_vars.update(model.variables.keys())
        return all_vars


__all__ = [
    "Variable",
    "StructuralEquation",
    "TheoryRelativeModel",
    "MultiTheoryModel",
]
