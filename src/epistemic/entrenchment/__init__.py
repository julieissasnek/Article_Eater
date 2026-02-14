"""
Entrenchment Dynamics for Non-Empirical Web Integration (Sprint 6b).

Implements per-type entrenchment computation following spec §4.2:
- Base entrenchment values by node type
- Asymmetric Popperian updating for theoretical propositions
- Methodological critique propagation
- Prediction tracking ledger
- Synthesis floor rules
- Expert discount factors
"""

from .node_type_entrenchment import (
    BASE_ENTRENCHMENT,
    EntrenchmentParams,
    compute_base_entrenchment,
    compute_entrenchment_with_modifiers,
)

from .theory_updating import (
    CONFIRMATION_BONUS,
    DISCONFIRMATION_PENALTY,
    update_theory_entrenchment,
    propagate_to_parent_theory,
)

from .critique_propagation import (
    propagate_critique_to_registry,
    CritiquePropagationResult,
)

from .prediction_ledger import (
    PredictionLedger,
    PredictionLedgerEntry,
)

from .synthesis_rules import (
    compute_synthesis_entrenchment,
    compute_median_entrenchment,
)

from .expert_discount import (
    EXPERT_SYNTHESIS_DISCOUNT,
    apply_expert_synthesis_discount,
)

__all__ = [
    # Base entrenchment
    "BASE_ENTRENCHMENT",
    "EntrenchmentParams",
    "compute_base_entrenchment",
    "compute_entrenchment_with_modifiers",
    # Theory updating
    "CONFIRMATION_BONUS",
    "DISCONFIRMATION_PENALTY",
    "update_theory_entrenchment",
    "propagate_to_parent_theory",
    # Critique propagation
    "propagate_critique_to_registry",
    "CritiquePropagationResult",
    # Prediction ledger
    "PredictionLedger",
    "PredictionLedgerEntry",
    # Synthesis rules
    "compute_synthesis_entrenchment",
    "compute_median_entrenchment",
    # Expert discount
    "EXPERT_SYNTHESIS_DISCOUNT",
    "apply_expert_synthesis_discount",
]
