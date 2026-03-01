"""
ATLAS Epistemic Projection (π)
==============================

Implements the projection function π: EN → BN that translates epistemic
assessments into operational causal parameters.

The π function bridges two categorically different representations:
- The Epistemic Network (EN): a coherentist structure (Quinean web) carrying
  warrant types (τ), warrant strengths (ω), and population metadata
- The Bayesian Network (BN): a Pearl SCM with conditional probability tables

The core operation is log-odds attenuation:
    logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)

Three multiplicative factors, each doing different work:
    d: how well does this TYPE of evidence transfer? (fixed by warrant type)
    ω: how good is this SPECIFIC piece of evidence? (set by study quality)
    δ: how well does evidence from THIS population transfer to THAT population?

References:
    Woodward, J. (2003). Making Things Happen. Oxford University Press.
    Pearl, J. (2009). Causality (2nd ed.). Cambridge University Press.
    Pearl, J., & Bareinboim, E. (2014). External validity. Statistical Science, 29(4).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class TheoryDependence(Enum):
    """
    Characterizes how much of a projection depends on untested theory
    versus empirically grounded evidence.

    EMPIRICALLY_GROUNDED: ratio > 0.80
        The projection rests primarily on empirical evidence (constitutive,
        mechanism, empirical_association, functional warrant types).
        Theory plays a minor role.

    THEORY_AUGMENTED: ratio 0.40–0.80
        Mixed dependence on empirical evidence and theory. Theory fills
        gaps in empirical coverage but doesn't dominate.

    THEORY_SCAFFOLDED: ratio < 0.40 or chain breaks
        The projection is heavily dependent on untested theory. A specific
        theory (if identified) is named. Use with caution; vulnerable to
        theory revision.
    """
    EMPIRICALLY_GROUNDED = "empirically_grounded"
    THEORY_AUGMENTED = "theory_augmented"
    THEORY_SCAFFOLDED = "theory_scaffolded"


# Empirical warrant types (per ATLAS technical appendix)
# These types have robust empirical grounding and should be heavily weighted
# in the empirical floor computation
EMPIRICALLY_GROUNDED_TYPES = frozenset({
    "constitutive",
    "mechanism",
    "empirical_association",
    "functional"
})

# Canonical discount factors per Woodward invariance framework
# These are TRANSFER RELIABILITY values (d), not credences
# d determines how much evidence of this TYPE survives transfer to a new context
CANONICAL_DISCOUNT_FACTORS: Dict[str, float] = {
    "constitutive": 0.95,           # Identity/definitional; near-perfect transfer
    "mechanism": 0.80,              # Known causal pathway; robust to context
    "empirical_association": 0.80,  # Replicated association; robust but confound risk
    "functional": 0.65,             # Known function, unknown mechanism; moderate transfer
    "capacity": 0.55,               # System CAN produce effect; conservative
    "analogical": 0.40,             # Cross-domain analogy; fragile transfer
    "theory_derived": 0.25,         # Prediction from named theory; speculative
}


# =============================================================================
# UTILITY FUNCTIONS: LOGIT/SIGMOID TRANSFORMATIONS
# =============================================================================

def logit(p: float) -> float:
    """
    Log-odds transformation: logit(p) = ln(p / (1 - p))

    Maps probability p ∈ (0, 1) to log-odds space ℝ.

    Args:
        p: Probability value in (0, 1)

    Returns:
        Log-odds, unbounded real number

    Raises:
        ValueError: if p is not in (0, 1) after clipping

    Notes:
        - Input is clipped to [1e-10, 1 - 1e-10] to handle edge cases
        - logit(0.5) = 0 (neutral)
        - logit(p) → -∞ as p → 0
        - logit(p) → +∞ as p → 1
    """
    p_clipped = max(1e-10, min(1.0 - 1e-10, p))
    return math.log(p_clipped / (1.0 - p_clipped))


def sigmoid(x: float) -> float:
    """
    Sigmoid (logistic) function: σ(x) = 1 / (1 + exp(-x))

    Inverse of logit; maps log-odds x ∈ ℝ to probability (0, 1).

    Args:
        x: Log-odds (unbounded real number)

    Returns:
        Probability in (0, 1)

    Notes:
        - σ(0) = 0.5
        - σ(x) → 0 as x → -∞
        - σ(x) → 1 as x → +∞
        - Numerically stable for all real x
    """
    if x > 100:
        return 1.0
    if x < -100:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


# =============================================================================
# SINGLE-EDGE PROJECTION
# =============================================================================

def project_single_edge(
    p_lab: float,
    warrant_type: str,
    omega: float,
    delta: float = 1.0
) -> float:
    """
    Project laboratory effect probability to target via single bridge warrant.

    Formula (ATLAS):
        logit(p_target) = d(τ) · ω · δ · logit(p_lab)

    Args:
        p_lab: Laboratory effect probability (0, 1)
        warrant_type: Bridge warrant type (e.g., 'mechanism', 'functional')
        omega: Warrant strength modifier ∈ [0, 1]
                (represents effect size, study quality, etc.)
        delta: Population similarity factor ∈ [0, 1]
               (default 1.0 = populations identical)

    Returns:
        Target population effect probability p_target ∈ (0, 1)

    Raises:
        KeyError: if warrant_type not in CANONICAL_DISCOUNT_FACTORS

    Notes:
        - d is looked up from CANONICAL_DISCOUNT_FACTORS
        - All three multiplicative factors (d, ω, δ) are treated equally
        - Each factor independently scales the evidence strength
    """
    if warrant_type not in CANONICAL_DISCOUNT_FACTORS:
        raise KeyError(f"Unknown warrant type: {warrant_type}")

    d = CANONICAL_DISCOUNT_FACTORS[warrant_type]

    # Compute log-odds attenuation
    logit_p_lab = logit(p_lab)
    attenuation_factor = d * omega * delta
    logit_p_target = attenuation_factor * logit_p_lab

    p_target = sigmoid(logit_p_target)
    return p_target


# =============================================================================
# SERIAL CHAIN PROJECTION (THROUGH INTERMEDIATES)
# =============================================================================

def project_serial_chain(edges: List[Dict[str, Any]]) -> float:
    """
    Project laboratory effect through serial chain of intermediates.

    When evidence reaches the target through a sequence of intermediate
    nodes (A → B → C → Target), the chain is only as strong as its
    weakest link. This implements the bottleneck principle.

    Formula (ATLAS):
        d_eff = min(d_i)           (weakest link)
        ω_eff = ∏ ω_i              (product of all warrant strengths)
        δ_eff = min(δ_i)           (weakest population match)
        logit(p_target) = d_eff · ω_eff · δ_eff · logit(p_lab)

    Args:
        edges: List of edge dictionaries, each with:
            - p_lab: Laboratory effect probability
            - tau: Warrant type (string)
            - omega: Warrant strength ∈ [0, 1]
            - delta: Population similarity ∈ [0, 1] (default 1.0)

    Returns:
        Target population effect probability ∈ (0, 1)
        Returns 0.5 if chain breaks (any d_i is 0)

    Notes:
        - Only the FIRST edge's p_lab is used (the root effect)
        - d values are multiplied together; weakest is still a bottleneck
        - ω values are multiplied (product of all warrant qualities)
        - δ values are minimized (worst population mismatch breaks the chain)
    """
    if not edges:
        return 0.5

    if len(edges) == 1:
        edge = edges[0]
        return project_single_edge(
            edge['p_lab'],
            edge['tau'],
            edge['omega'],
            edge.get('delta', 1.0)
        )

    # Compute effective parameters
    d_values = [CANONICAL_DISCOUNT_FACTORS.get(edge['tau'], 0.0) for edge in edges]
    omega_values = [edge.get('omega', 1.0) for edge in edges]
    delta_values = [edge.get('delta', 1.0) for edge in edges]

    d_eff = min(d_values) if d_values else 0.0
    omega_eff = 1.0
    for omega in omega_values:
        omega_eff *= omega
    delta_eff = min(delta_values) if delta_values else 0.0

    # If any d is 0, the chain is broken
    if d_eff == 0.0:
        return 0.5

    # Apply to root laboratory effect
    p_lab = edges[0]['p_lab']
    logit_p_lab = logit(p_lab)
    attenuation_factor = d_eff * omega_eff * delta_eff
    logit_p_target = attenuation_factor * logit_p_lab

    p_target = sigmoid(logit_p_target)
    return p_target


# =============================================================================
# PARALLEL COMBINATION (CONVERGENT EVIDENCE)
# =============================================================================

def project_parallel(edges: List[Dict[str, Any]]) -> float:
    """
    Combine multiple independent lines of evidence via parallel projection.

    When multiple independent bridges converge on the same target (e.g.,
    evidence A, B, C all support the same claim), their contributions
    are additive in log-odds space.

    Formula (ATLAS):
        logit(p_target) = Σ d_i · ω_i · δ_i · logit(p_lab_i)

    Args:
        edges: List of independent edge dictionaries, each with:
            - p_lab: Laboratory effect probability
            - tau: Warrant type (string)
            - omega: Warrant strength ∈ [0, 1]
            - delta: Population similarity ∈ [0, 1] (default 1.0)

    Returns:
        Target population effect probability ∈ (0, 1)
        Returns 0.5 if no edges provided

    Notes:
        - Each edge is treated independently
        - Log-odds are summed (equivalent to Bayes' rule for independent evidence)
        - Multiple weak signals can reinforce each other
    """
    if not edges:
        return 0.5

    logit_sum = 0.0
    for edge in edges:
        d = CANONICAL_DISCOUNT_FACTORS.get(edge['tau'], 0.0)
        omega = edge.get('omega', 1.0)
        delta = edge.get('delta', 1.0)
        p_lab = edge['p_lab']

        logit_p_lab = logit(p_lab)
        contribution = d * omega * delta * logit_p_lab
        logit_sum += contribution

    p_target = sigmoid(logit_sum)
    return p_target


# =============================================================================
# EMPIRICAL FLOOR COMPUTATION
# =============================================================================

def compute_empirical_floor(
    edges: List[Dict[str, Any]],
    is_serial: bool = True
) -> float:
    """
    Recompute projection using only empirically grounded warrant types.

    To assess theory dependence, we compute a "floor" probability using
    only warrant types with strong empirical grounding:
    CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL

    Theory-derived and analogical evidence is excluded from the floor.

    Formula (ATLAS):
        Recompute projection using only edges where τ ∈ EMPIRICALLY_GROUNDED_TYPES
        If chain breaks (no valid edges in serial case), return 0.5

    Args:
        edges: Full list of edges (will be filtered)
        is_serial: If True, use serial chain logic; else use parallel logic

    Returns:
        Target population effect probability ∈ (0, 1)
        Returns 0.5 if no empirically grounded edges remain

    Notes:
        - Filtering is strict: only EMPIRICALLY_GROUNDED_TYPES are retained
        - For serial chains, if any remaining edge is broken, returns 0.5
        - For parallel, simply sums the filtered contributions
    """
    empirical_edges = [
        e for e in edges
        if e.get('tau', '').lower() in EMPIRICALLY_GROUNDED_TYPES
    ]

    if not empirical_edges:
        return 0.5

    if is_serial:
        return project_serial_chain(empirical_edges)
    else:
        return project_parallel(empirical_edges)


# =============================================================================
# THEORY DEPENDENCE DIAGNOSTIC
# =============================================================================

def theory_dependence_diagnostic(
    full_projection: float,
    empirical_floor: float
) -> TheoryDependence:
    """
    Diagnose how much the projection depends on untested theory.

    By comparing full projection (all evidence) against empirical floor
    (only empirically grounded evidence), we can characterize how much
    the estimate relies on theoretical scaffolding.

    Formula (ATLAS):
        ratio = (empirical_floor - 0.50) / (full_projection - 0.50)

        If ratio > 0.80:
            Return EMPIRICALLY_GROUNDED (theory plays minor role)
        If 0.40 ≤ ratio ≤ 0.80:
            Return THEORY_AUGMENTED (mixed dependence)
        If ratio < 0.40 or chain breaks:
            Return THEORY_SCAFFOLDED (heavy theory dependence)

    Args:
        full_projection: Probability from all edges (p_target, all evidence)
        empirical_floor: Probability from empirical edges only

    Returns:
        TheoryDependence enum value

    Notes:
        - Ratio is undefined if full_projection ≈ 0.5; defaults to THEORY_AUGMENTED
        - Ratio > 1 indicates empirical floor exceeds full projection
          (can occur due to opposite-sign effects); treated as EMPIRICALLY_GROUNDED
        - If empirical_floor ≈ 0.5, ratio ≈ 0, triggering THEORY_SCAFFOLDED
    """
    # Avoid division by zero
    denominator = full_projection - 0.50
    if abs(denominator) < 1e-10:
        return TheoryDependence.THEORY_AUGMENTED

    numerator = empirical_floor - 0.50
    ratio = numerator / denominator

    # Handle edge cases
    if ratio > 0.80 or ratio > 1.0:
        return TheoryDependence.EMPIRICALLY_GROUNDED
    elif ratio < 0.40:
        return TheoryDependence.THEORY_SCAFFOLDED
    else:
        return TheoryDependence.THEORY_AUGMENTED


# =============================================================================
# RESULT DATA STRUCTURES
# =============================================================================

@dataclass
class ProjectionResult:
    """
    Complete result of π projection with diagnostic information.

    Attributes:
        p_target: Projected target population effect probability ∈ (0, 1)
        empirical_floor: Probability using only empirical edges
        theory_dependence: Enum characterizing theory reliance
        effective_d: Effective discount factor (d_eff)
        effective_omega: Effective warrant strength (ω_eff)
        contributing_edges: Number of edges that contributed to projection
        projection_method: 'serial' or 'parallel' or 'single'
    """
    p_target: float
    empirical_floor: float
    theory_dependence: TheoryDependence
    effective_d: float
    effective_omega: float
    contributing_edges: int
    projection_method: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "p_target": self.p_target,
            "empirical_floor": self.empirical_floor,
            "theory_dependence": self.theory_dependence.value,
            "effective_d": self.effective_d,
            "effective_omega": self.effective_omega,
            "contributing_edges": self.contributing_edges,
            "projection_method": self.projection_method
        }


# =============================================================================
# MAIN ENTRY POINT: PROJECT WITH DIAGNOSTIC
# =============================================================================

def project_with_diagnostic(
    edges: List[Dict[str, Any]],
    is_serial: bool = True,
    projection_method: Optional[str] = None
) -> ProjectionResult:
    """
    Main entry point: Project epistemic evidence to BN with full diagnostic.

    This function combines single-edge, serial, or parallel projection with
    empirical floor computation and theory dependence diagnosis.

    Args:
        edges: List of edge dictionaries, each with:
            - p_lab: Laboratory effect probability (0, 1)
            - tau: Warrant type (string, from CANONICAL_DISCOUNT_FACTORS)
            - omega: Warrant strength ∈ [0, 1]
            - delta: Population similarity ∈ [0, 1] (default 1.0)
        is_serial: If True, use serial chain logic (default); else parallel
        projection_method: Override auto-detection ('single', 'serial', 'parallel')
                          Mainly for diagnostics; auto-detection is preferred

    Returns:
        ProjectionResult with p_target, empirical_floor, theory_dependence,
        and effective attenuation parameters

    Raises:
        ValueError: if edges list is empty or malformed

    Examples:
        Single edge:
            result = project_with_diagnostic([{
                'p_lab': 0.75,
                'tau': 'mechanism',
                'omega': 0.90,
                'delta': 0.85
            }])

        Serial chain:
            result = project_with_diagnostic([
                {'p_lab': 0.75, 'tau': 'mechanism', 'omega': 0.90, 'delta': 1.0},
                {'p_lab': 0.70, 'tau': 'functional', 'omega': 0.80, 'delta': 0.85}
            ], is_serial=True)

        Parallel convergence:
            result = project_with_diagnostic([
                {'p_lab': 0.70, 'tau': 'empirical_association', 'omega': 0.85},
                {'p_lab': 0.65, 'tau': 'mechanism', 'omega': 0.90}
            ], is_serial=False)
    """
    if not edges:
        raise ValueError("edges list cannot be empty")

    # Auto-detect projection method if not provided
    if projection_method is None:
        if len(edges) == 1:
            projection_method = "single"
        elif is_serial:
            projection_method = "serial"
        else:
            projection_method = "parallel"

    # Compute full projection
    if projection_method == "single":
        edge = edges[0]
        p_target = project_single_edge(
            edge['p_lab'],
            edge['tau'],
            edge.get('omega', 1.0),
            edge.get('delta', 1.0)
        )
        effective_d = CANONICAL_DISCOUNT_FACTORS.get(edge['tau'], 0.0)
        effective_omega = edge.get('omega', 1.0)
    elif projection_method == "serial":
        p_target = project_serial_chain(edges)
        # Compute effective parameters for diagnostics
        d_values = [CANONICAL_DISCOUNT_FACTORS.get(e['tau'], 0.0) for e in edges]
        omega_values = [e.get('omega', 1.0) for e in edges]
        effective_d = min(d_values) if d_values else 0.0
        effective_omega = 1.0
        for omega in omega_values:
            effective_omega *= omega
    elif projection_method == "parallel":
        p_target = project_parallel(edges)
        # For parallel, report average d and product of ω
        d_values = [CANONICAL_DISCOUNT_FACTORS.get(e['tau'], 0.0) for e in edges]
        omega_values = [e.get('omega', 1.0) for e in edges]
        effective_d = sum(d_values) / len(d_values) if d_values else 0.0
        effective_omega = 1.0
        for omega in omega_values:
            effective_omega *= omega
    else:
        raise ValueError(f"Unknown projection_method: {projection_method}")

    # Compute empirical floor
    empirical_floor = compute_empirical_floor(edges, is_serial=is_serial)

    # Diagnose theory dependence
    theory_dependence = theory_dependence_diagnostic(p_target, empirical_floor)

    return ProjectionResult(
        p_target=p_target,
        empirical_floor=empirical_floor,
        theory_dependence=theory_dependence,
        effective_d=effective_d,
        effective_omega=effective_omega,
        contributing_edges=len(edges),
        projection_method=projection_method
    )
