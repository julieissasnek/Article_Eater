"""
Asymmetric Popperian Updating for Theories (Sprint 6b / Task 6b.2).

Implements asymmetric confirmation/disconfirmation for THEORETICAL_PROPOSITIONs.

Per spec §4.2:
"Confirmation/disconfirmation is ASYMMETRIC. A single clear disconfirmation
should reduce entrenchment more than a single confirmation raises it.
This implements a Popperian correction within the Quinean framework."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §4.2
"""

from typing import Tuple


# =============================================================================
# POPPERIAN ASYMMETRY CONSTANTS
# =============================================================================

# Per spec: disconfirmation hurts more than confirmation helps
CONFIRMATION_BONUS = 0.05         # Per confirmed prediction
DISCONFIRMATION_PENALTY = 0.10    # Per disconfirmed prediction (2× asymmetric)

# Damping factor for propagation to parent theory
PROPAGATION_DAMPING = 0.5         # Theories can survive some disconfirmation


# =============================================================================
# THEORY ENTRENCHMENT UPDATING
# =============================================================================

def update_theory_entrenchment(
    current_entrenchment: float,
    confirmations: int = 0,
    disconfirmations: int = 0,
    confirmation_bonus: float = CONFIRMATION_BONUS,
    disconfirmation_penalty: float = DISCONFIRMATION_PENALTY
) -> float:
    """
    Update theoretical proposition entrenchment based on prediction outcomes.

    Implements Popperian asymmetry: disconfirmation hurts more than
    confirmation helps.

    Args:
        current_entrenchment: Current entrenchment value [0, 1]
        confirmations: Number of confirmed predictions
        disconfirmations: Number of disconfirmed predictions
        confirmation_bonus: Bonus per confirmation (default 0.05)
        disconfirmation_penalty: Penalty per disconfirmation (default 0.10)

    Returns:
        Updated entrenchment value, clamped to [0, 1]

    Example:
        >>> update_theory_entrenchment(0.35, confirmations=1, disconfirmations=0)
        0.4
        >>> update_theory_entrenchment(0.35, confirmations=0, disconfirmations=1)
        0.25
        >>> update_theory_entrenchment(0.35, confirmations=1, disconfirmations=1)
        0.3  # Net loss due to asymmetry
    """
    adjustment = (confirmations * confirmation_bonus) - (disconfirmations * disconfirmation_penalty)
    new_entrenchment = current_entrenchment + adjustment
    return max(0.0, min(1.0, new_entrenchment))


def propagate_to_parent_theory(
    parent_entrenchment: float,
    child_confirmed: bool,
    damping: float = PROPAGATION_DAMPING
) -> float:
    """
    Propagate hypothesis confirmation/disconfirmation to parent theory.

    When a DERIVED_HYPOTHESIS is confirmed, the parent THEORETICAL_PROPOSITION
    gains entrenchment. When disconfirmed, it loses (with damping).

    Args:
        parent_entrenchment: Current entrenchment of parent theory
        child_confirmed: Whether the derived hypothesis was confirmed
        damping: Damping factor for disconfirmation (default 0.5)

    Returns:
        Updated parent entrenchment

    Per spec §4.2:
    "When a DERIVED_HYPOTHESIS is confirmed, entrenchment increase propagates
    UPWARD to the parent THEORETICAL_PROPOSITION. When disconfirmed,
    entrenchment decrease propagates upward too but with a damping factor."
    """
    if child_confirmed:
        # Full propagation for confirmation
        return update_theory_entrenchment(parent_entrenchment, confirmations=1)
    else:
        # Damped propagation for disconfirmation
        penalty = DISCONFIRMATION_PENALTY * damping
        return max(0.0, parent_entrenchment - penalty)


def compute_theory_trajectory(
    base_entrenchment: float,
    confirmation_history: list[bool]
) -> list[float]:
    """
    Compute entrenchment trajectory given a sequence of confirmations/disconfirmations.

    Useful for visualizing how a theory's entrenchment evolves over time.

    Args:
        base_entrenchment: Initial entrenchment
        confirmation_history: List of True (confirmed) / False (disconfirmed)

    Returns:
        List of entrenchment values after each event
    """
    trajectory = [base_entrenchment]
    current = base_entrenchment

    for confirmed in confirmation_history:
        if confirmed:
            current = update_theory_entrenchment(current, confirmations=1)
        else:
            current = update_theory_entrenchment(current, disconfirmations=1)
        trajectory.append(current)

    return trajectory


def assess_theory_health(
    entrenchment: float,
    confirmations: int,
    disconfirmations: int
) -> Tuple[str, str]:
    """
    Assess the epistemic health of a theory.

    Args:
        entrenchment: Current entrenchment
        confirmations: Total confirmation count
        disconfirmations: Total disconfirmation count

    Returns:
        Tuple of (status, explanation)
    """
    total_tests = confirmations + disconfirmations

    if total_tests == 0:
        if entrenchment > 0.5:
            return "suspect", "High entrenchment with no empirical tests"
        return "untested", "Theory has not been tested empirically"

    success_rate = confirmations / total_tests if total_tests > 0 else 0

    if success_rate >= 0.8 and entrenchment >= 0.5:
        return "well_supported", f"Strong track record ({confirmations}/{total_tests} confirmed)"

    if success_rate >= 0.6:
        return "moderately_supported", f"Mixed record ({confirmations}/{total_tests} confirmed)"

    if success_rate < 0.4:
        return "problematic", f"Poor track record ({confirmations}/{total_tests} confirmed)"

    return "needs_revision", f"Theory may need refinement ({confirmations}/{total_tests} confirmed)"
