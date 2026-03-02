"""
epistemic_projection_cva.py — CVA-5: Goal-Modulated Epistemic Projection
=========================================================================

Extends ATLAS epistemic projection with CVA goal and activity-frame modulation.

Baseline ATLAS:
    logit(p_target) = d(τ) · ω · δ · logit(p_lab)

CVA Extension:
    logit(p_target) = d(τ, goal, frame) · ω · δ · logit(p_lab)
    where d(τ, goal, frame) = d_base(τ) · d_goal(goal, τ) · d_frame(frame, τ, c)

Key features:
  1. Goal-warrant alignment matrix (9 valuations × 7 warrant types)
  2. Frame-dependent discount adjustments
  3. Multi-edge aggregation with goal modulation
  4. Path composition for entailment chains
  5. Side-by-side comparison with baseline

Reference: CVA_SPRINT_PLAN §Sprint CVA-5
Does NOT replace existing epistemic_projection.py — parallel system.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import baseline functions
from src.services.epistemic_projection import (
    CANONICAL_DISCOUNT_FACTORS,
    logit,
    sigmoid,
    project_single_edge,
    project_serial_chain,
    project_parallel,
    ProjectionResult,
)

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Goal-Warrant Alignment Matrix (Sprint CVA-5 §6)
# ══════════════════════════════════════════════════════════════════
#
# 9 valuation axes × 7 warrant types = 63-cell matrix
# Each cell is d_goal(valuation, warrant_type) ∈ [0.3, 1.0]
#
# Interpretation:
#   d_goal = 1.0  → warrant type is fully relevant to this goal
#   d_goal = 0.5  → moderate relevance
#   d_goal = 0.3  → low relevance (floor; never zero)
#
# Sources: Expert judgment + CVA sprint spec alignment analysis

GOAL_WARRANT_ALIGNMENT: Dict[str, Dict[str, float]] = {
    "SafetyValue": {
        "constitutive":        0.95,  # definitional safety facts transfer perfectly
        "mechanism":           0.90,  # causal mechanisms for safety well-understood
        "empirical_association": 0.85,  # replicated safety associations
        "functional":          0.75,  # functional roles of safety features
        "capacity":            0.60,  # system capacity for safety
        "analogical":          0.50,  # analogies can mislead on safety
        "theory_derived":      0.40,  # theoretical safety predictions risky
    },
    "InterestValue": {
        "constitutive":        0.70,  # definitions matter less for interest/novelty
        "mechanism":           0.75,  # curiosity mechanisms moderately transferable
        "empirical_association": 0.80,  # replicated interest findings
        "functional":          0.70,  # functional novelty
        "capacity":            0.55,  # capacity for interest
        "analogical":          0.80,  # analogies ARE how novelty works
        "theory_derived":      0.60,  # theoretical novelty predictions reasonable
    },
    "RestorationValue": {
        "constitutive":        0.85,  # definitional restoration
        "mechanism":           0.90,  # stress recovery mechanisms well-studied
        "empirical_association": 0.85,  # Kaplan/Ulrich well-replicated
        "functional":          0.80,  # restorative environments functional evidence
        "capacity":            0.65,  # restorative capacity
        "analogical":          0.55,  # restoration analogies moderate
        "theory_derived":      0.50,  # ART predictions
    },
    "StatusValue": {
        "constitutive":        0.60,  # status definitions culturally variable
        "mechanism":           0.65,  # social hierarchy mechanisms
        "empirical_association": 0.70,  # status associations
        "functional":          0.55,  # functional status signals
        "capacity":            0.45,  # capacity for status
        "analogical":          0.50,  # cross-domain status analogies
        "theory_derived":      0.35,  # theoretical status predictions weak
    },
    "BelongingValue": {
        "constitutive":        0.70,  # belonging definitions
        "mechanism":           0.75,  # belonging mechanisms (oxytocin, etc.)
        "empirical_association": 0.80,  # belonging-wellbeing associations
        "functional":          0.70,  # functional belonging
        "capacity":            0.55,  # capacity for belonging
        "analogical":          0.45,  # belonging analogies fragile
        "theory_derived":      0.40,  # theoretical belonging predictions
    },
    "IdentityCongruenceValue": {
        "constitutive":        0.65,  # identity congruence definitions
        "mechanism":           0.60,  # identity mechanisms less understood
        "empirical_association": 0.70,  # identity-environment fit associations
        "functional":          0.60,  # functional identity
        "capacity":            0.45,  # capacity for identity
        "analogical":          0.50,  # identity analogies moderate
        "theory_derived":      0.40,  # theoretical identity predictions
    },
    "AutonomySupportValue": {
        "constitutive":        0.80,  # SDT clear definitions
        "mechanism":           0.85,  # autonomy mechanisms (SDT)
        "empirical_association": 0.85,  # strong SDT empirical base
        "functional":          0.75,  # functional autonomy support
        "capacity":            0.60,  # capacity for autonomy
        "analogical":          0.55,  # autonomy analogies moderate
        "theory_derived":      0.60,  # SDT predictions well-grounded
    },
    "CompetenceSupportValue": {
        "constitutive":        0.80,  # SDT definitions
        "mechanism":           0.85,  # competence/flow mechanisms
        "empirical_association": 0.85,  # replicated SDT findings
        "functional":          0.80,  # challenge-skill functional
        "capacity":            0.65,  # capacity for competence
        "analogical":          0.60,  # competence analogies moderate
        "theory_derived":      0.55,  # flow theory predictions
    },
    "RelatednessSupportValue": {
        "constitutive":        0.75,  # relatedness definitions
        "mechanism":           0.80,  # relatedness mechanisms (TPJ, mentalizing)
        "empirical_association": 0.80,  # social connection empirical base
        "functional":          0.75,  # functional relatedness
        "capacity":            0.55,  # capacity for relatedness
        "analogical":          0.45,  # relatedness analogies fragile
        "theory_derived":      0.45,  # theoretical relatedness predictions
    },
}

# Frame-warrant alignment: how well different warrant types transfer
# under different activity frames (d_frame)
FRAME_WARRANT_ALIGNMENT: Dict[str, Dict[str, float]] = {
    "hospital_recovery": {
        "constitutive": 1.0,
        "mechanism": 0.95,
        "empirical_association": 0.90,
        "functional": 0.85,
        "capacity": 0.70,
        "analogical": 0.45,  # analogies risky in clinical settings
        "theory_derived": 0.35,
    },
    "office_work": {
        "constitutive": 0.95,
        "mechanism": 0.85,
        "empirical_association": 0.85,
        "functional": 0.80,
        "capacity": 0.65,
        "analogical": 0.65,  # office analogies sometimes useful
        "theory_derived": 0.50,
    },
    "social_gathering": {
        "constitutive": 0.80,
        "mechanism": 0.75,
        "empirical_association": 0.80,
        "functional": 0.70,
        "capacity": 0.55,
        "analogical": 0.60,
        "theory_derived": 0.45,
    },
    "museum_visiting": {
        "constitutive": 0.85,
        "mechanism": 0.80,
        "empirical_association": 0.85,
        "functional": 0.75,
        "capacity": 0.60,
        "analogical": 0.80,  # analogies valued in aesthetic contexts
        "theory_derived": 0.55,
    },
    "sacred_space": {
        "constitutive": 0.75,
        "mechanism": 0.65,
        "empirical_association": 0.70,
        "functional": 0.65,
        "capacity": 0.50,
        "analogical": 0.70,  # symbolic analogies central
        "theory_derived": 0.55,
    },
}


# ══════════════════════════════════════════════════════════════════
# Core Functions
# ══════════════════════════════════════════════════════════════════

def d_goal(
    goal_vector: List[str],
    warrant_type: str,
) -> float:
    """
    Compute goal-dependent discount adjustment.

    d_goal = average alignment between active goals and warrant type.
    If no goals are active, returns 1.0 (no adjustment).

    Args:
        goal_vector: List of active valuation axis names
        warrant_type: Bridge warrant type string

    Returns:
        Discount adjustment factor ∈ [0.3, 1.0]
    """
    if not goal_vector:
        return 1.0

    alignments = []
    for goal in goal_vector:
        if goal in GOAL_WARRANT_ALIGNMENT:
            alignment = GOAL_WARRANT_ALIGNMENT[goal].get(warrant_type, 0.5)
            alignments.append(alignment)

    if not alignments:
        return 1.0

    return sum(alignments) / len(alignments)


def d_frame(
    frame_name: str,
    warrant_type: str,
    constraint_vector: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute frame-dependent discount adjustment.

    d_frame adjusts warrant reliability based on activity context.
    Example: In recovery frame, ANALOGY warrants are down-weighted
    because analogies transfer poorly in clinical contexts.

    Args:
        frame_name: Activity frame name
        warrant_type: Bridge warrant type
        constraint_vector: Optional constraint values for context-sensitivity

    Returns:
        Discount adjustment ∈ [0.3, 1.0]
    """
    if frame_name in FRAME_WARRANT_ALIGNMENT:
        base = FRAME_WARRANT_ALIGNMENT[frame_name].get(warrant_type, 0.7)
    else:
        base = 0.8  # default: mild discount for unknown frames

    # Context sensitivity: if prediction_error is high and warrant is analogical,
    # further reduce (analogies break in surprising environments)
    if constraint_vector and warrant_type == "analogical":
        pred_err = constraint_vector.get("prediction_error", 0.5)
        if pred_err > 0.7:
            base *= 0.8  # 20% further reduction

    return max(0.3, min(1.0, base))


def compute_d_cva(
    warrant_type: str,
    goal_vector: List[str],
    frame_name: str = "",
    constraint_vector: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute full CVA discount factor.

    d(τ, goal, frame) = d_base(τ) · d_goal(goal, τ) · d_frame(frame, τ, c)

    Args:
        warrant_type: Bridge warrant type
        goal_vector: List of active valuation axes
        frame_name: Activity frame name
        constraint_vector: Optional constraint values

    Returns:
        Full CVA discount factor ∈ (0, 1)
    """
    d_base = CANONICAL_DISCOUNT_FACTORS.get(warrant_type, 0.25)
    d_g = d_goal(goal_vector, warrant_type)
    d_f = d_frame(frame_name, warrant_type, constraint_vector) if frame_name else 1.0

    return d_base * d_g * d_f


# ══════════════════════════════════════════════════════════════════
# Goal-Modulated Projection Functions
# ══════════════════════════════════════════════════════════════════

def project_goal_modulated(
    p_lab: float,
    warrant_type: str,
    goal_vector: List[str],
    frame_name: str,
    constraint_vector: Optional[Dict[str, float]] = None,
    omega: float = 1.0,
    delta: float = 1.0,
) -> float:
    """
    Goal-modulated single-edge projection.

    Formula:
        logit(p_target) = d(τ, goal, frame) · ω · δ · logit(p_lab)

    Args:
        p_lab: Laboratory effect probability (0, 1)
        warrant_type: Bridge warrant type
        goal_vector: Active valuation axes
        frame_name: Activity frame
        constraint_vector: Constraint values for context-sensitivity
        omega: Warrant quality ∈ [0, 1]
        delta: Population similarity ∈ [0, 1]

    Returns:
        Goal-modulated target probability ∈ (0, 1)
    """
    d = compute_d_cva(warrant_type, goal_vector, frame_name, constraint_vector)
    logit_p_lab = logit(p_lab)
    logit_p_target = d * omega * delta * logit_p_lab
    return sigmoid(logit_p_target)


def aggregate_projections_goal_modulated(
    edges: List[Dict[str, Any]],
    goal_vector: List[str],
    frame_name: str,
    constraint_vector: Optional[Dict[str, float]] = None,
) -> float:
    """
    Multi-edge parallel aggregation with goal modulation.

    Formula:
        logit(p_combined) = Σᵢ d(τᵢ, goal, frame) · ωᵢ · δᵢ · logit(p_labᵢ)

    Args:
        edges: List of edge dicts with p_lab, tau, omega, delta
        goal_vector: Active valuation axes
        frame_name: Activity frame
        constraint_vector: Constraint vector

    Returns:
        Combined projected probability ∈ (0, 1)
    """
    if not edges:
        return 0.5

    logit_sum = 0.0
    for edge in edges:
        d = compute_d_cva(
            edge["tau"], goal_vector, frame_name, constraint_vector
        )
        omega = edge.get("omega", 1.0)
        delta = edge.get("delta", 1.0)
        p_lab = edge["p_lab"]

        logit_sum += d * omega * delta * logit(p_lab)

    return sigmoid(logit_sum)


def compose_path_discounts_goal_modulated(
    path_edges: List[Dict[str, Any]],
    goal_vector: List[str],
    frame_name: str,
    constraint_vector: Optional[Dict[str, float]] = None,
    method: str = "min",
) -> float:
    """
    Compose discount factors along an entailment path with goal modulation.

    For serial chains (B1 → B2 → B3), compose discounts:
      - "min":  d_effective = min(d_i(goal, frame))
      - "product": d_effective = Π d_i(goal, frame)

    Args:
        path_edges: List of edge dicts along the path
        goal_vector: Active goals
        frame_name: Activity frame
        constraint_vector: Constraint values
        method: "min" or "product"

    Returns:
        Effective discount for the path
    """
    if not path_edges:
        return 0.0

    discounts = []
    for edge in path_edges:
        d = compute_d_cva(
            edge["tau"], goal_vector, frame_name, constraint_vector
        )
        discounts.append(d * edge.get("omega", 1.0) * edge.get("delta", 1.0))

    if method == "min":
        return min(discounts)
    elif method == "product":
        result = 1.0
        for d in discounts:
            result *= d
        return result
    else:
        raise ValueError(f"Unknown method: {method}. Use 'min' or 'product'.")


# ══════════════════════════════════════════════════════════════════
# Comparison Utilities (Sprint CVA-5 §7)
# ══════════════════════════════════════════════════════════════════

@dataclass
class ProjectionComparison:
    """Side-by-side comparison of baseline vs goal-modulated projection."""
    p_baseline: float
    p_goal_modulated: float
    difference: float
    d_baseline: float
    d_goal_modulated: float
    goal_vector: List[str]
    frame_name: str
    warrant_type: str

    @property
    def improvement(self) -> float:
        """Positive = goal-modulated is higher (more confident)."""
        return self.p_goal_modulated - self.p_baseline

    @property
    def relative_change(self) -> float:
        """Relative change from baseline."""
        if abs(self.p_baseline - 0.5) < 1e-10:
            return 0.0
        return (self.p_goal_modulated - self.p_baseline) / abs(self.p_baseline - 0.5)

    def to_dict(self) -> dict:
        return {
            "p_baseline": round(self.p_baseline, 4),
            "p_goal_modulated": round(self.p_goal_modulated, 4),
            "difference": round(self.difference, 4),
            "d_baseline": round(self.d_baseline, 4),
            "d_goal_modulated": round(self.d_goal_modulated, 4),
            "goal_vector": self.goal_vector,
            "frame_name": self.frame_name,
            "warrant_type": self.warrant_type,
            "improvement": round(self.improvement, 4),
            "relative_change": round(self.relative_change, 4),
        }


def project_comparison(
    p_lab: float,
    warrant_type: str,
    omega: float,
    goal_vector: List[str],
    frame_name: str,
    constraint_vector: Optional[Dict[str, float]] = None,
    delta: float = 1.0,
) -> ProjectionComparison:
    """
    Compare baseline ATLAS projection with goal-modulated CVA projection.

    Args:
        p_lab: Laboratory probability
        warrant_type: Warrant type
        omega: Warrant quality
        goal_vector: Active goals
        frame_name: Activity frame
        constraint_vector: Constraint values
        delta: Population similarity

    Returns:
        ProjectionComparison with both projections and diagnostics
    """
    # Baseline
    d_base = CANONICAL_DISCOUNT_FACTORS.get(warrant_type, 0.25)
    p_baseline = project_single_edge(p_lab, warrant_type, omega, delta)

    # Goal-modulated
    d_cva = compute_d_cva(warrant_type, goal_vector, frame_name, constraint_vector)
    p_goal_mod = project_goal_modulated(
        p_lab, warrant_type, goal_vector, frame_name,
        constraint_vector, omega, delta,
    )

    return ProjectionComparison(
        p_baseline=p_baseline,
        p_goal_modulated=p_goal_mod,
        difference=p_goal_mod - p_baseline,
        d_baseline=d_base,
        d_goal_modulated=d_cva,
        goal_vector=goal_vector,
        frame_name=frame_name,
        warrant_type=warrant_type,
    )


def project_with_full_diagnostic(
    edges: List[Dict[str, Any]],
    goal_vector: List[str],
    frame_name: str,
    constraint_vector: Optional[Dict[str, float]] = None,
    is_serial: bool = False,
) -> Dict[str, Any]:
    """
    Full diagnostic projection: baseline + goal-modulated + comparison.

    Returns complete diagnostic dict with both projections,
    per-edge breakdowns, and aggregate comparison.
    """
    # Baseline
    if is_serial:
        p_baseline = project_serial_chain(edges)
    else:
        p_baseline = project_parallel(edges)

    # Goal-modulated
    p_goal_mod = aggregate_projections_goal_modulated(
        edges, goal_vector, frame_name, constraint_vector,
    )

    # Per-edge breakdown
    edge_details = []
    for edge in edges:
        d_base = CANONICAL_DISCOUNT_FACTORS.get(edge["tau"], 0.25)
        d_cva = compute_d_cva(
            edge["tau"], goal_vector, frame_name, constraint_vector
        )
        edge_details.append({
            "tau": edge["tau"],
            "p_lab": edge["p_lab"],
            "d_baseline": round(d_base, 4),
            "d_goal_modulated": round(d_cva, 4),
            "d_goal_factor": round(d_goal(goal_vector, edge["tau"]), 4),
            "d_frame_factor": round(d_frame(frame_name, edge["tau"], constraint_vector), 4),
        })

    return {
        "p_baseline": round(p_baseline, 4),
        "p_goal_modulated": round(p_goal_mod, 4),
        "difference": round(p_goal_mod - p_baseline, 4),
        "goal_vector": goal_vector,
        "frame_name": frame_name,
        "n_edges": len(edges),
        "is_serial": is_serial,
        "edge_details": edge_details,
    }


# ══════════════════════════════════════════════════════════════════
# Export Functions
# ══════════════════════════════════════════════════════════════════

def export_goal_warrant_matrix(output_path: str) -> int:
    """Export the goal-warrant alignment matrix to JSON."""
    data = {
        "title": "Goal-Warrant Alignment Matrix",
        "description": "d_goal(valuation, warrant_type) values for CVA projection",
        "dimensions": {
            "valuations": list(GOAL_WARRANT_ALIGNMENT.keys()),
            "warrant_types": list(CANONICAL_DISCOUNT_FACTORS.keys()),
        },
        "matrix": GOAL_WARRANT_ALIGNMENT,
        "baseline_discounts": CANONICAL_DISCOUNT_FACTORS,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    LOGGER.info("Exported goal-warrant matrix to %s", output_path)
    return len(GOAL_WARRANT_ALIGNMENT) * len(CANONICAL_DISCOUNT_FACTORS)
