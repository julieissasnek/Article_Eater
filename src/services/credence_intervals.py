"""
Credence Confidence Intervals via Delta Method Uncertainty Propagation

Implements uncertainty quantification for the ATLAS credence projection formula:
    logit(p_target) = d · ω · δ · logit(p_lab)

Expert panel member Roger Cooke (risk analysis) flagged that credence estimates
without confidence intervals convey false precision. This module uses first-order
error propagation (Delta method) to compute confidence intervals around the credence
estimate, accounting for uncertainty in all parameters.

Key Components:
1. CredenceEstimate: Dataclass holding point estimate + confidence interval bounds
2. compute_credence_with_ci(): Main entry point for single belief credence with CI
3. batch_credence_intervals(): Vectorized computation for multiple beliefs
4. uncertainty_decomposition(): Variance contribution analysis per parameter

Reference:
    Cooke, R. M. (1991). Experts in Uncertainty. Oxford University Press.
    Woodward, J. (2003). Making Things Happen. Oxford University Press. (Chapter 5: Uncertainty)
    Pearl, J. (2009). Causality (2nd ed.). Cambridge University Press.

Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Date: 2026-03-02
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Standard quantile for 95% confidence interval
Z_CRITICAL_95 = 1.96  # scipy.stats.norm.ppf(0.975)
Z_CRITICAL_90 = 1.645  # scipy.stats.norm.ppf(0.95)
Z_CRITICAL_99 = 2.576  # scipy.stats.norm.ppf(0.995)

# Default standard errors for parameter uncertainty per sensitivity analysis (§48.1A)
DEFAULT_D_SE = 0.10            # d (discount factor) uncertainty
DEFAULT_OMEGA_SE = 0.05        # ω (warrant strength) uncertainty
DEFAULT_DELTA_SE = 0.05        # δ (population transfer) uncertainty
DEFAULT_P_LAB_SE = 0.15        # p_lab (laboratory probability) uncertainty


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CredenceEstimate:
    """
    Complete credence estimate with confidence interval and component uncertainties.

    This dataclass provides full transparency for epistemic assessment: not just
    the point estimate, but its uncertainty bounds and the sources of that uncertainty.

    Attributes:
        point: Point estimate of target credence p_target ∈ (0, 1)
        lower: Lower bound of confidence interval
        upper: Upper bound of confidence interval
        se: Standard error of p_target (on probability scale)
        confidence_level: Confidence level (0.90, 0.95, 0.99, etc.)
        components: Dict mapping parameter names to their variance contributions
                   {"d": percent_var, "omega": percent_var, "delta": percent_var, "p_lab": percent_var}
        logit_se: Standard error of logit(p_target) (on log-odds scale, for diagnostics)
        notes: Auditable explanation of computation (for panel review)
    """
    point: float
    lower: float
    upper: float
    se: float
    confidence_level: float = 0.95
    components: Dict[str, float] = field(default_factory=dict)
    logit_se: float = 0.0
    notes: str = ""

    def __post_init__(self):
        """Validate bounds."""
        if not (0.0 <= self.lower <= self.point <= self.upper <= 1.0):
            logger.warning(
                f"CredenceEstimate bounds validation: "
                f"lower={self.lower:.3f}, point={self.point:.3f}, upper={self.upper:.3f}. "
                f"Clipping to [0.01, 0.99] to avoid boundary artifacts."
            )
            # Clip point to avoid edge cases
            self.point = max(0.01, min(0.99, self.point))
            self.lower = max(0.01, min(self.point, self.lower))
            self.upper = max(self.point, min(0.99, self.upper))

    def width(self) -> float:
        """Width of confidence interval."""
        return self.upper - self.lower

    def to_dict(self) -> Dict:
        """Serialize to dictionary for logging/storage."""
        return {
            "point": float(self.point),
            "lower": float(self.lower),
            "upper": float(self.upper),
            "se": float(self.se),
            "confidence_level": float(self.confidence_level),
            "ci_width": float(self.width()),
            "logit_se": float(self.logit_se),
            "components": {k: float(v) for k, v in self.components.items()},
            "notes": str(self.notes),
        }


@dataclass
class BatchCredenceResult:
    """Result container for batch credence interval computation."""
    estimates: List[CredenceEstimate]
    summary_stats: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize batch results."""
        return {
            "estimates": [e.to_dict() for e in self.estimates],
            "summary_stats": self.summary_stats,
        }


# =============================================================================
# UTILITY FUNCTIONS: LOGIT/SIGMOID AND DERIVATIVES
# =============================================================================

def logit(p: float) -> float:
    """Log-odds transformation: logit(p) = ln(p / (1 - p))."""
    p = max(1e-10, min(1.0 - 1e-10, p))
    return math.log(p / (1.0 - p))


def sigmoid(x: float) -> float:
    """Sigmoid (logistic) function: σ(x) = 1 / (1 + exp(-x))."""
    if x > 100:
        return 1.0
    if x < -100:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivative(x: float) -> float:
    """Derivative of sigmoid: σ'(x) = σ(x) · (1 - σ(x))."""
    s = sigmoid(x)
    return s * (1.0 - s)


def logit_derivative(p: float) -> float:
    """Derivative of logit: logit'(p) = 1 / (p · (1 - p))."""
    p = max(1e-10, min(1.0 - 1e-10, p))
    return 1.0 / (p * (1.0 - p))


# =============================================================================
# DELTA METHOD UNCERTAINTY PROPAGATION
# =============================================================================

def compute_logit_variance(
    p_lab: float,
    d: float,
    omega: float,
    delta: float,
    p_lab_se: float = DEFAULT_P_LAB_SE,
    d_se: float = DEFAULT_D_SE,
    omega_se: float = DEFAULT_OMEGA_SE,
    delta_se: float = DEFAULT_DELTA_SE,
) -> Tuple[float, Dict[str, float]]:
    """
    Compute variance of z = d · ω · δ · logit(p_lab) via Delta method.

    Using first-order error propagation:
        Var(z) ≈ (∂z/∂d)² · Var(d) + (∂z/∂ω)² · Var(ω) + (∂z/∂δ)² · Var(δ) + (∂z/∂p_lab)² · Var(p_lab)

    Partial derivatives:
        ∂z/∂d = ω · δ · logit(p_lab)
        ∂z/∂ω = d · δ · logit(p_lab)
        ∂z/∂δ = d · ω · logit(p_lab)
        ∂z/∂p_lab = d · ω · δ / (p_lab · (1 - p_lab))  [chain rule through logit]

    Args:
        p_lab: Laboratory effect probability
        d: Discount factor
        omega: Warrant strength
        delta: Population transfer factor
        p_lab_se: Standard error of p_lab
        d_se: Standard error of d
        omega_se: Standard error of omega
        delta_se: Standard error of delta

    Returns:
        Tuple of (total_variance, component_variances_dict)
        Where component_variances_dict maps parameter names to their variance contributions
    """
    logit_p_lab = logit(p_lab)

    # Compute partial derivatives at observed point
    dz_dd = omega * delta * logit_p_lab
    dz_domega = d * delta * logit_p_lab
    dz_ddelta = d * omega * logit_p_lab
    dz_dp_lab = d * omega * delta * logit_derivative(p_lab)

    # Variance contributions
    var_d = (dz_dd ** 2) * (d_se ** 2)
    var_omega = (dz_domega ** 2) * (omega_se ** 2)
    var_delta = (dz_ddelta ** 2) * (delta_se ** 2)
    var_p_lab = (dz_dp_lab ** 2) * (p_lab_se ** 2)

    total_var = var_d + var_omega + var_delta + var_p_lab

    components = {
        "d": var_d,
        "omega": var_omega,
        "delta": var_delta,
        "p_lab": var_p_lab,
    }

    logger.debug(
        f"compute_logit_variance: "
        f"var_d={var_d:.6f}, var_omega={var_omega:.6f}, var_delta={var_delta:.6f}, var_p_lab={var_p_lab:.6f} "
        f"→ total_var={total_var:.6f}"
    )

    return total_var, components


def compute_credence_se(
    p_target: float,
    logit_se: float,
) -> float:
    """
    Transform standard error from log-odds to probability scale.

    Since p_target = σ(logit(p_target)), we use chain rule:
        SE(p_target) = |dσ/dz| · SE(z)
                     = σ(z) · (1 - σ(z)) · SE(z)
                     = p_target · (1 - p_target) · SE(z)

    This delta-method transformation accounts for the nonlinearity of the sigmoid
    function when uncertainty is large.

    Args:
        p_target: Target probability (output of sigmoid)
        logit_se: Standard error of log-odds (input to sigmoid)

    Returns:
        Standard error on probability scale ∈ [0, 1]
    """
    # Derivative of sigmoid: σ'(z) = σ(z) · (1 - σ(z))
    derivative = p_target * (1.0 - p_target)
    se = derivative * logit_se

    return se


# =============================================================================
# MAIN ENTRY POINT: CREDENCE WITH CONFIDENCE INTERVALS
# =============================================================================

def compute_credence_with_ci(
    p_lab: float,
    d: float,
    omega: float,
    delta: float = 1.0,
    p_lab_se: float = DEFAULT_P_LAB_SE,
    d_se: float = DEFAULT_D_SE,
    omega_se: float = DEFAULT_OMEGA_SE,
    delta_se: float = DEFAULT_DELTA_SE,
    confidence_level: float = 0.95,
) -> CredenceEstimate:
    """
    Compute credence with confidence interval via Delta method.

    This is the main entry point for adding uncertainty quantification to the ATLAS
    credence projection formula. It takes point estimates and their uncertainties,
    propagates those uncertainties through the logit-sigmoid transform, and returns
    both the point estimate and confidence bounds.

    Formula:
        logit(p_target) = d · ω · δ · logit(p_lab)

    Uncertainty propagation:
        1. Compute variance of logit(p_target) via first-order partial derivatives
        2. Take square root to get SE on log-odds scale
        3. Transform to probability scale using: SE(p_target) = p_target · (1 - p_target) · SE(logit)
        4. Construct symmetric CI: p_target ± z_α/2 · SE(p_target)
        5. Clip to [0.01, 0.99] to avoid boundary artifacts

    Args:
        p_lab: Laboratory effect probability ∈ (0, 1)
        d: Discount factor (from CANONICAL_DISCOUNT_FACTORS)
        omega: Warrant strength ∈ [0, 1]
        delta: Population transfer factor ∈ [0, 1] (default 1.0)
        p_lab_se: Standard error of p_lab (default 0.15)
        d_se: Standard error of d (default 0.10)
        omega_se: Standard error of omega (default 0.05)
        delta_se: Standard error of delta (default 0.05)
        confidence_level: CI level, typically 0.90, 0.95, or 0.99 (default 0.95)

    Returns:
        CredenceEstimate with point, lower, upper, se, confidence_level, and components

    Raises:
        ValueError: if confidence_level not in (0.0, 1.0) or p_lab not in (0, 1)

    Example:
        >>> estimate = compute_credence_with_ci(
        ...     p_lab=0.75,
        ...     d=0.80,      # mechanism warrant type
        ...     omega=0.85,   # good warrant strength
        ...     delta=0.90,   # similar population
        ... )
        >>> print(f"Credence: {estimate.point:.3f} 95% CI [{estimate.lower:.3f}, {estimate.upper:.3f}]")
        >>> print(f"Variance contributions: {estimate.components}")

    Reference:
        Cooke, R. M. (1991). Experts in Uncertainty. §3.2: Probability assessment with uncertainty.
        Delta method: Casella & Berger (2002). Statistical Inference (2nd ed.). §5.5.
    """
    # Validate inputs
    if not (0.0 < confidence_level < 1.0):
        raise ValueError(f"confidence_level must be in (0, 1), got {confidence_level}")
    if not (0.0 < p_lab < 1.0):
        raise ValueError(f"p_lab must be in (0, 1), got {p_lab}")

    # Compute point estimate
    logit_p_lab = logit(p_lab)
    logit_p_target = d * omega * delta * logit_p_lab
    p_target = sigmoid(logit_p_target)

    # Compute variance of logit(p_target)
    logit_var, component_vars = compute_logit_variance(
        p_lab=p_lab,
        d=d,
        omega=omega,
        delta=delta,
        p_lab_se=p_lab_se,
        d_se=d_se,
        omega_se=omega_se,
        delta_se=delta_se,
    )

    # Standard error on log-odds scale
    logit_se = math.sqrt(max(0.0, logit_var))  # Clamp to avoid sqrt(negative)

    # Transform to probability scale
    p_target_se = compute_credence_se(p_target, logit_se)

    # Get critical value for confidence level
    if confidence_level == 0.95:
        z_crit = Z_CRITICAL_95
    elif confidence_level == 0.90:
        z_crit = Z_CRITICAL_90
    elif confidence_level == 0.99:
        z_crit = Z_CRITICAL_99
    else:
        # General case: use standard normal quantile
        import scipy.stats
        z_crit = scipy.stats.norm.ppf(0.5 + confidence_level / 2.0)

    # Construct confidence interval
    margin_of_error = z_crit * p_target_se
    lower = max(0.01, p_target - margin_of_error)
    upper = min(0.99, p_target + margin_of_error)

    # Compute percentage variance contribution from each component
    total_var = sum(component_vars.values())
    if total_var > 0:
        component_pct = {k: (v / total_var) * 100.0 for k, v in component_vars.items()}
    else:
        component_pct = {k: 0.0 for k in component_vars.keys()}

    notes = (
        f"Δ-method CI: p_lab={p_lab:.3f}±{p_lab_se:.3f}, "
        f"d={d:.3f}±{d_se:.3f}, ω={omega:.3f}±{omega_se:.3f}, "
        f"δ={delta:.3f}±{delta_se:.3f}; "
        f"logit_SE={logit_se:.3f}, p_SE={p_target_se:.3f}"
    )

    result = CredenceEstimate(
        point=p_target,
        lower=lower,
        upper=upper,
        se=p_target_se,
        confidence_level=confidence_level,
        components=component_pct,
        logit_se=logit_se,
        notes=notes,
    )

    logger.info(
        f"compute_credence_with_ci: point={p_target:.3f}, "
        f"CI[{lower:.3f}, {upper:.3f}], width={result.width():.3f}, "
        f"se={p_target_se:.3f}, confidence={confidence_level:.2%}"
    )

    return result


# =============================================================================
# BATCH COMPUTATION
# =============================================================================

def batch_credence_intervals(
    beliefs: List[Dict],
    confidence_level: float = 0.95,
) -> BatchCredenceResult:
    """
    Compute confidence intervals for multiple beliefs in batch.

    This is a convenience wrapper for computing credence estimates across
    a list of belief specifications (e.g., from a web-of-belief knowledge base).

    Args:
        beliefs: List of dict, each with keys:
            - "p_lab": Laboratory effect probability
            - "d": Discount factor
            - "omega": Warrant strength
            - "delta": Population transfer factor (optional, default 1.0)
            - "p_lab_se": SE of p_lab (optional, default 0.15)
            - "d_se": SE of d (optional, default 0.10)
            - "omega_se": SE of omega (optional, default 0.05)
            - "delta_se": SE of delta (optional, default 0.05)
            - "belief_id": Identifier for tracking (optional)
        confidence_level: CI level for all estimates (default 0.95)

    Returns:
        BatchCredenceResult with:
        - estimates: List of CredenceEstimate objects (one per belief)
        - summary_stats: Dict with aggregate statistics (mean CI width, etc.)

    Example:
        >>> beliefs = [
        ...     {"belief_id": "B1", "p_lab": 0.75, "d": 0.80, "omega": 0.85},
        ...     {"belief_id": "B2", "p_lab": 0.65, "d": 0.80, "omega": 0.70},
        ... ]
        >>> result = batch_credence_intervals(beliefs)
        >>> for est in result.estimates:
        ...     print(f"{est}: {est.point:.3f} [{est.lower:.3f}, {est.upper:.3f}]")
    """
    estimates = []

    for belief_dict in beliefs:
        p_lab = belief_dict.get("p_lab")
        d = belief_dict.get("d")
        omega = belief_dict.get("omega")

        if p_lab is None or d is None or omega is None:
            logger.warning(f"Belief dict missing required keys: {belief_dict}")
            continue

        delta = belief_dict.get("delta", 1.0)
        p_lab_se = belief_dict.get("p_lab_se", DEFAULT_P_LAB_SE)
        d_se = belief_dict.get("d_se", DEFAULT_D_SE)
        omega_se = belief_dict.get("omega_se", DEFAULT_OMEGA_SE)
        delta_se = belief_dict.get("delta_se", DEFAULT_DELTA_SE)

        estimate = compute_credence_with_ci(
            p_lab=p_lab,
            d=d,
            omega=omega,
            delta=delta,
            p_lab_se=p_lab_se,
            d_se=d_se,
            omega_se=omega_se,
            delta_se=delta_se,
            confidence_level=confidence_level,
        )

        # Store belief_id in notes if provided
        if "belief_id" in belief_dict:
            estimate.notes = f"belief_id={belief_dict['belief_id']}; " + estimate.notes

        estimates.append(estimate)

    # Compute summary statistics
    if estimates:
        widths = [e.width() for e in estimates]
        ses = [e.se for e in estimates]
        points = [e.point for e in estimates]

        summary_stats = {
            "n_beliefs": len(estimates),
            "mean_point": sum(points) / len(points),
            "mean_ci_width": sum(widths) / len(widths),
            "median_ci_width": sorted(widths)[len(widths) // 2],
            "mean_se": sum(ses) / len(ses),
            "max_ci_width": max(widths),
            "min_ci_width": min(widths),
        }
    else:
        summary_stats = {}

    logger.info(f"batch_credence_intervals: processed {len(estimates)} beliefs")

    return BatchCredenceResult(estimates=estimates, summary_stats=summary_stats)


# =============================================================================
# UNCERTAINTY DECOMPOSITION ANALYSIS
# =============================================================================

def uncertainty_decomposition(
    p_lab: float,
    d: float,
    omega: float,
    delta: float = 1.0,
    p_lab_se: float = DEFAULT_P_LAB_SE,
    d_se: float = DEFAULT_D_SE,
    omega_se: float = DEFAULT_OMEGA_SE,
    delta_se: float = DEFAULT_DELTA_SE,
) -> Dict[str, float]:
    """
    Analyze which parameters contribute most to overall uncertainty in credence.

    Returns a dictionary mapping parameter names to their percentage contribution
    to total variance. This is useful for identifying which sources of uncertainty
    dominate and where to focus effort on reducing uncertainty.

    Args:
        p_lab: Laboratory effect probability
        d: Discount factor
        omega: Warrant strength
        delta: Population transfer factor
        p_lab_se: Standard error of p_lab
        d_se: Standard error of d
        omega_se: Standard error of omega
        delta_se: Standard error of delta

    Returns:
        Dict mapping:
            - "d": % of variance from d uncertainty
            - "omega": % of variance from omega uncertainty
            - "delta": % of variance from delta uncertainty
            - "p_lab": % of variance from p_lab uncertainty
            - "total_var": Absolute total variance value

    Example:
        >>> decomp = uncertainty_decomposition(
        ...     p_lab=0.75, d=0.80, omega=0.85, delta=0.90,
        ...     d_se=0.10, omega_se=0.05, delta_se=0.05, p_lab_se=0.15
        ... )
        >>> for param, pct in decomp.items():
        ...     if param != "total_var":
        ...         print(f"{param}: {pct:.1f}%")
    """
    _, component_vars = compute_logit_variance(
        p_lab=p_lab,
        d=d,
        omega=omega,
        delta=delta,
        p_lab_se=p_lab_se,
        d_se=d_se,
        omega_se=omega_se,
        delta_se=delta_se,
    )

    total_var = sum(component_vars.values())

    if total_var > 0:
        decomposition = {k: (v / total_var) * 100.0 for k, v in component_vars.items()}
    else:
        decomposition = {k: 0.0 for k in component_vars.keys()}

    decomposition["total_var"] = total_var

    logger.debug(f"uncertainty_decomposition: {decomposition}")

    return decomposition


# =============================================================================
# SENSITIVITY ANALYSIS HELPER
# =============================================================================

def sensitivity_analysis(
    p_lab: float,
    d: float,
    omega: float,
    delta: float = 1.0,
    p_lab_se_range: Tuple[float, float] = (0.05, 0.25),
    d_se_range: Tuple[float, float] = (0.05, 0.20),
    omega_se_range: Tuple[float, float] = (0.02, 0.10),
    delta_se_range: Tuple[float, float] = (0.02, 0.10),
    n_points: int = 5,
) -> Dict:
    """
    Perform sensitivity analysis on how CI width varies with input uncertainties.

    Useful for evaluating the robustness of credence estimates to different
    assumptions about parameter uncertainty (e.g., what if p_lab_se was higher?).

    Args:
        p_lab, d, omega, delta: Point estimates
        p_lab_se_range: Range of p_lab_se to test (min, max)
        d_se_range: Range of d_se to test
        omega_se_range: Range of omega_se to test
        delta_se_range: Range of delta_se to test
        n_points: Number of points to test in each range (default 5)

    Returns:
        Dict mapping parameter names to lists of (se_value, ci_width) tuples

    Example:
        >>> sens = sensitivity_analysis(p_lab=0.75, d=0.80, omega=0.85)
        >>> for param, results in sens.items():
        ...     print(f"\n{param}:")
        ...     for se, width in results:
        ...         print(f"  SE={se:.3f} → CI width={width:.3f}")
    """
    results = {}

    # Test p_lab_se sensitivity
    p_lab_se_values = [
        p_lab_se_range[0] + (p_lab_se_range[1] - p_lab_se_range[0]) * i / (n_points - 1)
        for i in range(n_points)
    ]
    results["p_lab_se"] = []
    for p_lab_se in p_lab_se_values:
        est = compute_credence_with_ci(p_lab, d, omega, delta, p_lab_se=p_lab_se)
        results["p_lab_se"].append((p_lab_se, est.width()))

    # Test d_se sensitivity
    d_se_values = [
        d_se_range[0] + (d_se_range[1] - d_se_range[0]) * i / (n_points - 1)
        for i in range(n_points)
    ]
    results["d_se"] = []
    for d_se in d_se_values:
        est = compute_credence_with_ci(p_lab, d, omega, delta, d_se=d_se)
        results["d_se"].append((d_se, est.width()))

    # Test omega_se sensitivity
    omega_se_values = [
        omega_se_range[0] + (omega_se_range[1] - omega_se_range[0]) * i / (n_points - 1)
        for i in range(n_points)
    ]
    results["omega_se"] = []
    for omega_se in omega_se_values:
        est = compute_credence_with_ci(p_lab, d, omega, delta, omega_se=omega_se)
        results["omega_se"].append((omega_se, est.width()))

    # Test delta_se sensitivity
    delta_se_values = [
        delta_se_range[0] + (delta_se_range[1] - delta_se_range[0]) * i / (n_points - 1)
        for i in range(n_points)
    ]
    results["delta_se"] = []
    for delta_se in delta_se_values:
        est = compute_credence_with_ci(p_lab, d, omega, delta, delta_se=delta_se)
        results["delta_se"].append((delta_se, est.width()))

    logger.info(f"sensitivity_analysis: completed for {len(results)} parameters")

    return results
