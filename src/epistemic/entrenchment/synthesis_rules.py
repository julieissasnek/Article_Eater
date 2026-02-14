"""
Synthesis Entrenchment Rules (Sprint 6b / Task 6b.5).

Implements the floor rule for SYNTHESIS_CONCLUSION entrenchment.

Per spec §4.2:
"A SYNTHESIS_CONCLUSION's entrenchment should ALWAYS be >= the median
entrenchment of its included studies (it represents their aggregate,
not a new claim)."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §4.2
"""

from typing import List, Optional


def compute_median_entrenchment(entrenchments: List[float]) -> Optional[float]:
    """
    Compute median entrenchment from a list of values.

    Args:
        entrenchments: List of entrenchment values

    Returns:
        Median value, or None if empty list
    """
    if not entrenchments:
        return None

    sorted_values = sorted(entrenchments)
    n = len(sorted_values)

    if n % 2 == 1:
        return sorted_values[n // 2]
    else:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2


def compute_synthesis_entrenchment(
    base_entrenchment: float,
    included_study_entrenchments: List[float],
    heterogeneity_i2: float = 0.0,
    publication_bias: str = "none",
    grade_quality: str = "moderate"
) -> float:
    """
    Compute entrenchment for SYNTHESIS_CONCLUSION with floor rule.

    The floor rule ensures that a synthesis's entrenchment is always
    >= the median entrenchment of its included studies.

    Args:
        base_entrenchment: Starting entrenchment (typically 0.75)
        included_study_entrenchments: Entrenchments of included studies
        heterogeneity_i2: I² statistic [0, 100]
        publication_bias: "none" | "marginal" | "significant"
        grade_quality: "high" | "moderate" | "low"

    Returns:
        Final entrenchment value with floor rule applied

    Example:
        >>> included = [0.3, 0.4, 0.5, 0.6, 0.7]  # median = 0.5
        >>> compute_synthesis_entrenchment(0.40, included)
        0.5  # Floor kicks in because 0.40 < 0.5 (median)
    """
    # Start with base
    entrenchment = base_entrenchment

    # Apply heterogeneity penalty
    if heterogeneity_i2 > 75:
        entrenchment -= 0.15
    elif heterogeneity_i2 > 50:
        entrenchment -= 0.05

    # Apply publication bias penalty
    if publication_bias == "significant":
        entrenchment -= 0.10
    elif publication_bias == "marginal":
        entrenchment -= 0.05

    # Apply GRADE quality modifier
    if grade_quality == "high":
        entrenchment += 0.05
    elif grade_quality == "low":
        entrenchment -= 0.05

    # Apply floor rule: synthesis >= median of included studies
    if included_study_entrenchments:
        median = compute_median_entrenchment(included_study_entrenchments)
        if median is not None:
            entrenchment = max(entrenchment, median)

    # Clamp to valid range
    return max(0.0, min(1.0, entrenchment))


def assess_synthesis_quality(
    heterogeneity_i2: float,
    publication_bias: str,
    n_studies: int,
    included_study_entrenchments: Optional[List[float]] = None
) -> dict:
    """
    Assess the quality of a synthesis based on its characteristics.

    Args:
        heterogeneity_i2: I² statistic [0, 100]
        publication_bias: "none" | "marginal" | "significant"
        n_studies: Number of included studies
        included_study_entrenchments: Optional entrenchments of included studies

    Returns:
        Dict with quality assessment
    """
    quality_score = 1.0
    issues = []

    # Heterogeneity check
    if heterogeneity_i2 > 75:
        quality_score -= 0.3
        issues.append(f"High heterogeneity (I²={heterogeneity_i2:.1f}%)")
    elif heterogeneity_i2 > 50:
        quality_score -= 0.15
        issues.append(f"Moderate heterogeneity (I²={heterogeneity_i2:.1f}%)")

    # Publication bias check
    if publication_bias == "significant":
        quality_score -= 0.2
        issues.append("Significant publication bias detected")
    elif publication_bias == "marginal":
        quality_score -= 0.1
        issues.append("Marginal publication bias")

    # Sample size check
    if n_studies < 5:
        quality_score -= 0.15
        issues.append(f"Small number of studies (n={n_studies})")

    # Included study quality check
    if included_study_entrenchments:
        median = compute_median_entrenchment(included_study_entrenchments)
        if median is not None and median < 0.4:
            quality_score -= 0.15
            issues.append(f"Low median study quality (median={median:.2f})")

    # Determine overall rating
    if quality_score >= 0.8:
        rating = "high"
    elif quality_score >= 0.6:
        rating = "moderate"
    elif quality_score >= 0.4:
        rating = "low"
    else:
        rating = "very_low"

    return {
        "quality_score": max(0.0, quality_score),
        "rating": rating,
        "issues": issues,
        "n_studies": n_studies,
        "heterogeneity_i2": heterogeneity_i2,
        "publication_bias": publication_bias
    }


def should_trust_synthesis_over_primary(
    synthesis_entrenchment: float,
    primary_study_entrenchment: float,
    synthesis_n_studies: int
) -> bool:
    """
    Determine if a synthesis should be trusted over a conflicting primary study.

    Generally, a synthesis aggregates multiple studies and should be trusted
    over a single study unless the primary study is of much higher quality.

    Args:
        synthesis_entrenchment: Entrenchment of the synthesis
        primary_study_entrenchment: Entrenchment of the primary study
        synthesis_n_studies: Number of studies in the synthesis

    Returns:
        True if synthesis should be preferred
    """
    # If synthesis includes many studies and has reasonable entrenchment, prefer it
    if synthesis_n_studies >= 5 and synthesis_entrenchment >= 0.5:
        return True

    # If primary study is substantially higher quality, prefer it
    if primary_study_entrenchment > synthesis_entrenchment + 0.2:
        return False

    # Default: prefer synthesis if it has more studies
    return synthesis_n_studies >= 3
