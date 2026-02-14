"""
Warrant Scaling Functions (Panel-Approved Revisions).

Implements dynamic warrant confidence computation based on panel consensus:
- D-PANEL.1: Coherence warrant scales with link count (Haack, Spohn)
- D-PANEL.2: Vigilance warrant scales with source quality (Cartwright)

These functions provide context-sensitive warrant confidences rather than
fixed values, allowing the system to better calibrate epistemic support.

References:
- Panel consensus: 2026-02-14
- Haack, S. (1993). Evidence and Inquiry
- Spohn, W. (2012). The Laws of Belief
"""

from typing import Optional
import math


# =============================================================================
# BASE WARRANT VALUES (from Sprint 1)
# =============================================================================

BASE_COHERENCE_WARRANT = 0.55      # D1.5: Base value, scales with links
BASE_ARGUMENTATIVE_WARRANT = 0.70  # D1.6: Fixed (approved as-is)
BASE_VIGILANCE_WARRANT = 0.50      # D-PANEL.2: Base for scaling


# =============================================================================
# COHERENCE WARRANT (D-PANEL.1)
# =============================================================================

def compute_coherence_warrant(
    link_count: int = 1,
    base: float = BASE_COHERENCE_WARRANT,
    max_boost: float = 0.15,
    cap: float = 0.75
) -> float:
    """
    Compute coherence warrant with link-count scaling.

    Per panel consensus (Haack, Spohn): A claim supported by coherence with
    many other claims has stronger warrant than one coherent with few.
    Uses sqrt scaling for diminishing returns.

    Args:
        link_count: Number of coherence-supporting links (default 1)
        base: Base warrant value (default 0.55)
        max_boost: Maximum additional boost from links (default 0.15)
        cap: Maximum total warrant (default 0.75)

    Returns:
        Warrant confidence in [base, cap]

    Example:
        >>> compute_coherence_warrant(1)   # Single link
        0.55
        >>> compute_coherence_warrant(4)   # Four links
        0.65  # Base + sqrt(4) * 0.05 = 0.55 + 0.10
        >>> compute_coherence_warrant(16)  # Many links
        0.70  # Approaches cap with diminishing returns
    """
    if link_count < 1:
        link_count = 1

    # Sqrt scaling for diminishing returns
    # Each link adds 0.05 * sqrt(n) boost, capped at max_boost
    boost = min(max_boost, 0.05 * math.sqrt(link_count))

    return min(cap, base + boost)


def get_coherence_warrant_for_belief(
    coherence_links: int,
    contradicting_links: int = 0
) -> float:
    """
    Compute coherence warrant accounting for both support and tension.

    Args:
        coherence_links: Number of supporting coherence links
        contradicting_links: Number of tension/contradicting links

    Returns:
        Net coherence warrant, reduced by contradictions
    """
    base_warrant = compute_coherence_warrant(coherence_links)

    # Each contradiction reduces warrant (diminishing impact)
    if contradicting_links > 0:
        reduction = min(0.20, 0.05 * math.sqrt(contradicting_links))
        return max(0.40, base_warrant - reduction)

    return base_warrant


# =============================================================================
# ARGUMENTATIVE WARRANT (D1.6 - Approved as-is)
# =============================================================================

def compute_argumentative_warrant(
    adversarial_scrutiny_survived: bool = False,
    base: float = BASE_ARGUMENTATIVE_WARRANT
) -> float:
    """
    Compute argumentative warrant for claims that survived adversarial scrutiny.

    Per panel consensus (Pollock, Longino): 0.70 is appropriate for claims
    that have been tested by researchers from rival theoretical traditions.

    Args:
        adversarial_scrutiny_survived: Whether claim survived adversarial testing
        base: Warrant value for adversarial survival (default 0.70)

    Returns:
        0.70 if adversarial scrutiny survived, 0.50 otherwise

    Note:
        Adversarial scrutiny is operationally defined as:
        1. Replication attempt by competing theoretical tradition
        2. Inclusion in multi-tradition meta-analysis
        3. Survival of formal commentary/response cycle
    """
    if adversarial_scrutiny_survived:
        return base
    return 0.50  # No adversarial warrant without scrutiny


# =============================================================================
# VIGILANCE WARRANT (D-PANEL.2)
# =============================================================================

def compute_vigilance_warrant(
    source_quality: float,
    base: float = BASE_VIGILANCE_WARRANT,
    scale: float = 0.25,
    min_warrant: float = 0.50,
    max_warrant: float = 0.75
) -> float:
    """
    Compute vigilance warrant scaled by source quality.

    Per panel consensus (Cartwright): The warrant should scale with the
    actual source quality score. Passing a quality check with score 0.9
    warrants more confidence than passing with score 0.55.

    Args:
        source_quality: Source quality score in [0, 1]
        base: Base warrant at source_quality=0 (default 0.50)
        scale: Scaling factor for quality (default 0.25)
        min_warrant: Minimum warrant value (default 0.50)
        max_warrant: Maximum warrant value (default 0.75)

    Returns:
        Warrant confidence in [min_warrant, max_warrant]

    Example:
        >>> compute_vigilance_warrant(0.0)  # Zero quality
        0.50
        >>> compute_vigilance_warrant(0.5)  # Medium quality
        0.625
        >>> compute_vigilance_warrant(1.0)  # Perfect quality
        0.75
    """
    if not 0.0 <= source_quality <= 1.0:
        raise ValueError(f"source_quality must be in [0, 1], got {source_quality}")

    warrant = base + (scale * source_quality)
    return max(min_warrant, min(max_warrant, warrant))


# =============================================================================
# COMPOSITE WARRANT COMPUTATION
# =============================================================================

def compute_total_warrant(
    coherence_links: int = 0,
    adversarial_scrutiny: bool = False,
    source_quality: Optional[float] = None,
    contradicting_links: int = 0
) -> float:
    """
    Compute total warrant from all available sources.

    Combines coherence, argumentative, and vigilance warrants using
    a noisy-OR combination (each warrant type contributes independently).

    Args:
        coherence_links: Number of coherence-supporting links
        adversarial_scrutiny: Whether claim survived adversarial testing
        source_quality: Source quality score (enables vigilance warrant)
        contradicting_links: Number of contradicting links

    Returns:
        Combined warrant confidence in [0, 1]
    """
    warrants = []

    # Coherence warrant (always applicable if links > 0)
    if coherence_links > 0:
        warrants.append(get_coherence_warrant_for_belief(
            coherence_links, contradicting_links
        ))

    # Argumentative warrant (only if scrutiny survived)
    if adversarial_scrutiny:
        warrants.append(compute_argumentative_warrant(True))

    # Vigilance warrant (only if quality assessed)
    if source_quality is not None:
        warrants.append(compute_vigilance_warrant(source_quality))

    if not warrants:
        return 0.50  # Prior/neutral warrant

    # Noisy-OR combination: P(support) = 1 - product(1 - p_i)
    # This allows multiple warrants to combine without exceeding 1.0
    complement_product = 1.0
    for w in warrants:
        complement_product *= (1.0 - w)

    return 1.0 - complement_product
