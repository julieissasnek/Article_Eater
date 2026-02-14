"""
Expert Synthesis Discount Factor (Sprint 6b / Task 6b.6).

Implements the discount for EXPERT_SYNTHESIS relative to SYNTHESIS_CONCLUSION.

Per spec §4.2:
"EXPERT_SYNTHESIS nodes are DISCOUNTED relative to SYNTHESIS_CONCLUSION nodes.
An expert's narrative interpretation gets less weight than a systematic
meta-analysis reaching the same conclusion. The discount factor should be
configurable (default: 0.7 × equivalent systematic finding)."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §4.2
"""

from typing import Optional


# Default discount factor: expert synthesis = 0.7 × equivalent systematic
EXPERT_SYNTHESIS_DISCOUNT = 0.7


def apply_expert_synthesis_discount(
    equivalent_synthesis_entrenchment: float,
    discount_factor: float = EXPERT_SYNTHESIS_DISCOUNT
) -> float:
    """
    Apply discount to EXPERT_SYNTHESIS relative to equivalent SYNTHESIS_CONCLUSION.

    Args:
        equivalent_synthesis_entrenchment: Entrenchment that a systematic
            synthesis with the same conclusion would have
        discount_factor: Discount to apply (default 0.7)

    Returns:
        Discounted entrenchment for the expert synthesis

    Example:
        >>> apply_expert_synthesis_discount(0.70)
        0.49  # 0.70 * 0.7
    """
    return equivalent_synthesis_entrenchment * discount_factor


def compute_expert_synthesis_entrenchment(
    author_expertise: str = "unknown",
    consistent_with_systematic: bool = False,
    n_studies_cited: int = 0,
    theoretical_commitment_declared: bool = False,
    discount_factor: float = EXPERT_SYNTHESIS_DISCOUNT
) -> float:
    """
    Compute entrenchment for an EXPERT_SYNTHESIS node.

    Base range: 0.35-0.55 (lower than systematic because non-systematic
    selection introduces bias risk).

    Args:
        author_expertise: "established" | "emerging" | "unknown"
        consistent_with_systematic: True if consistent with systematic reviews
        n_studies_cited: Number of studies cited
        theoretical_commitment_declared: True if author declares perspective
        discount_factor: Base discount factor

    Returns:
        Computed entrenchment value
    """
    # Start with base (midpoint of 0.35-0.55)
    base = 0.45

    # Author expertise modifier
    if author_expertise == "established":
        base += 0.10
    elif author_expertise == "emerging":
        base += 0.05
    elif author_expertise == "unknown":
        base -= 0.05

    # Consistency with systematic reviews is a strong signal
    if consistent_with_systematic:
        base += 0.10

    # More cited studies = more evidence base
    if n_studies_cited >= 20:
        base += 0.05
    elif n_studies_cited >= 10:
        base += 0.02

    # Declared theoretical commitment is actually good (transparency)
    if theoretical_commitment_declared:
        base += 0.02  # Small bonus for transparency

    # Clamp to valid range
    return max(0.0, min(1.0, base))


def compare_expert_vs_systematic(
    expert_entrenchment: float,
    systematic_entrenchment: float,
    same_conclusion: bool = True
) -> dict:
    """
    Compare an expert synthesis to a systematic synthesis.

    Args:
        expert_entrenchment: Entrenchment of expert synthesis
        systematic_entrenchment: Entrenchment of systematic synthesis
        same_conclusion: Whether they reach the same conclusion

    Returns:
        Dict with comparison analysis
    """
    ratio = expert_entrenchment / systematic_entrenchment if systematic_entrenchment > 0 else 0

    if same_conclusion:
        if ratio <= EXPERT_SYNTHESIS_DISCOUNT:
            status = "appropriate_discount"
            explanation = "Expert synthesis appropriately discounted"
        else:
            status = "expert_overweighted"
            explanation = f"Expert synthesis may be overweighted (ratio={ratio:.2f})"
    else:
        if systematic_entrenchment > expert_entrenchment:
            status = "prefer_systematic"
            explanation = "Systematic review should be preferred on conflicting conclusion"
        else:
            status = "anomaly"
            explanation = "Expert synthesis higher than systematic - investigate"

    return {
        "expert_entrenchment": expert_entrenchment,
        "systematic_entrenchment": systematic_entrenchment,
        "ratio": ratio,
        "expected_ratio": EXPERT_SYNTHESIS_DISCOUNT,
        "same_conclusion": same_conclusion,
        "status": status,
        "explanation": explanation
    }


def get_recommended_discount(
    author_expertise: str,
    field_consensus: Optional[str] = None
) -> float:
    """
    Get recommended discount factor based on context.

    Args:
        author_expertise: Level of author expertise
        field_consensus: "strong" | "moderate" | "weak" | None

    Returns:
        Recommended discount factor
    """
    base_discount = EXPERT_SYNTHESIS_DISCOUNT

    # More established authors get less discount
    if author_expertise == "established":
        base_discount += 0.05  # 0.75 instead of 0.70

    # In fields with weak consensus, experts matter more
    if field_consensus == "weak":
        base_discount += 0.10  # 0.80 instead of 0.70
    elif field_consensus == "strong":
        base_discount -= 0.05  # 0.65 instead of 0.70

    return min(1.0, base_discount)
