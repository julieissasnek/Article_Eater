"""Researcher-specific VOI adjustment based on CollectorProfile characteristics.

Implements personalized VOI scoring by adjusting base VOI scores based on:
- Domain expertise alignment
- Access capability match
- Collector type fit with gap complexity
- Historical performance (gap closure rate)
- Current workload capacity
"""

from __future__ import annotations

from src.epistemic.gap_types import GapType
from src.queue.models import CollectorProfile, CollectorType, ResearchTarget


def compute_researcher_fit(collector: CollectorProfile, target: ResearchTarget) -> float:
    """
    Compute a 0.0-2.0 fit multiplier for how well this collector matches this target.

    Factors considered:
    - Domain expertise alignment: boost if target domain matches collector's preferred domains
    - Access alignment: boost if target requires paywalled sources and collector has access
    - Collector type fit: boost if collector type suits the gap complexity
    - Historical performance: boost/penalty based on gap closure rate
    - Workload capacity: penalty if collector is near max concurrent targets

    Args:
        collector: CollectorProfile instance with preferences and stats
        target: ResearchTarget instance describing the gap to close

    Returns:
        Float multiplier in range [0.0, 2.0]. 1.0 = neutral fit.
    """
    fit = 1.0

    # Domain alignment: boost if target domain matches collector preferences
    fit *= _compute_domain_fit(collector, target)

    # Access alignment: boost if paywalled content needed and collector can access it
    fit *= _compute_access_fit(collector, target)

    # Collector type fit: HUMAN_RESEARCHER suited to complex/theoretical gaps,
    # AUTOMATED_SEARCHER suited to simple/empirical gaps
    fit *= _compute_type_fit(collector, target)

    # Historical closure rate: reward high performers, penalize low performers
    fit *= _compute_performance_fit(collector)

    # Workload capacity: slight penalty if near capacity
    fit *= _compute_capacity_fit(collector)

    # Clamp to [0.0, 2.0] range
    return min(2.0, max(0.0, fit))


def adjust_voi_for_collector(
    base_voi: float, collector: CollectorProfile, target: ResearchTarget
) -> float:
    """
    Return personalized VOI = base_voi * researcher_fit_factor, clamped to [0, 1].

    This function adjusts the base VOI score to reflect how suitable a particular
    collector is for a particular target. A good fit increases the effective VOI;
    a poor fit decreases it.

    Args:
        base_voi: Base VOI score (typically in [0, 1])
        collector: CollectorProfile describing the collector
        target: ResearchTarget describing the gap to close

    Returns:
        Adjusted VOI score in range [0, 1]
    """
    if base_voi <= 0.0:
        return 0.0

    fit = compute_researcher_fit(collector, target)
    adjusted = base_voi * fit

    # Clamp final result to [0, 1]
    return min(1.0, max(0.0, adjusted))


# ------------------------------------------------------------------
# Internal fit computation helpers
# ------------------------------------------------------------------


def _compute_domain_fit(collector: CollectorProfile, target: ResearchTarget) -> float:
    """
    Boost VOI if target domain matches collector's preferred domains.

    Heuristic: Extract domain hints from gap type and optional theory drivers,
    then check against collector's preferred_domains list.

    Returns:
        Multiplier: 1.3 if strong match, 1.1 if weak match, 1.0 if no match
    """
    if not collector.preferred_domains:
        return 1.0

    # Extract domain hints from target
    domain_hints = _extract_domain_hints(target)
    if not domain_hints:
        return 1.0

    # Check for overlap with collector's preferred domains
    collector_domains = {d.lower().strip() for d in collector.preferred_domains}
    hint_domains = {d.lower().strip() for d in domain_hints}

    overlap = collector_domains.intersection(hint_domains)
    if len(overlap) > 1:
        return 1.3  # Strong match: multiple domain overlaps
    elif overlap:
        return 1.1  # Weak match: single domain overlap
    return 1.0


def _extract_domain_hints(target: ResearchTarget) -> list[str]:
    """Extract domain names from target's gap type, theory drivers, and description."""
    hints = []

    # Gap type as domain hint
    gap_domain_map = {
        GapType.MECHANISM: "mechanism",
        GapType.VALIDATION: "validation",
        GapType.DIRECTION: "causal",
        GapType.BOUNDARY: "boundary",
    }
    if target.gap_type in gap_domain_map:
        hints.append(gap_domain_map[target.gap_type])

    # Theory drivers (e.g., "cognition", "neuroscience")
    hints.extend(target.theory_drivers[:2])

    # Keywords from description
    keywords = _extract_keywords(target.gap_description)
    hints.extend(keywords[:2])

    return hints


def _extract_keywords(text: str, max_keywords: int = 3) -> list[str]:
    """Extract domain-like keywords from text (simple heuristic)."""
    import re

    keywords = []
    # Look for capitalized words or common domain terms
    domain_terms = {
        "cognition",
        "cognitive",
        "neuroscience",
        "neural",
        "psychology",
        "architectural",
        "architecture",
        "environment",
        "social",
        "behavior",
        "learning",
        "memory",
        "attention",
    }

    text_lower = text.lower()
    for term in domain_terms:
        if term in text_lower:
            keywords.append(term)

    return keywords[:max_keywords]


def _compute_access_fit(collector: CollectorProfile, target: ResearchTarget) -> float:
    """
    Boost VOI if target requires paywalled sources and collector can access them.

    Heuristic: Check if target databases include paywalled vendors and if
    collector.can_access_paywalled is True.

    Returns:
        Multiplier: 1.2 if paywalled access needed and available, 1.0 otherwise
    """
    if not collector.can_access_paywalled:
        return 1.0

    # Check if target databases suggest paywalled content
    paywalled_indicators = {
        "proquest",
        "scopus",
        "web_of_science",
        "sage",
        "jstor",
        "psycinfo",
    }

    target_dbs = {db.lower().strip() for db in target.target_databases}
    has_paywalled = bool(paywalled_indicators.intersection(target_dbs))

    if has_paywalled:
        return 1.2
    return 1.0


def _compute_type_fit(collector: CollectorProfile, target: ResearchTarget) -> float:
    """
    Boost VOI if collector type matches target complexity.

    - HUMAN_RESEARCHER: suited to complex/theoretical gaps (high VOI, MECHANISM/BOUNDARY)
    - AUTOMATED_SEARCHER: suited to simple/empirical gaps (lower VOI, VALIDATION)
    - HUMAN_ASSISTANT: neutral fit (1.0)
    - ZOTERO_WATCHER: neutral fit (1.0)

    Returns:
        Multiplier: 1.15 if strong type fit, 1.0 otherwise
    """
    collector_type = collector.collector_type

    # Complex gaps: MECHANISM, DIRECTION, BOUNDARY
    complex_gaps = {GapType.MECHANISM, GapType.DIRECTION, GapType.BOUNDARY}
    is_complex = target.gap_type in complex_gaps

    if collector_type == CollectorType.HUMAN_RESEARCHER and is_complex:
        return 1.15
    elif collector_type == CollectorType.AUTOMATED_SEARCHER and target.gap_type == GapType.VALIDATION:
        return 1.15
    # Other combinations are neutral
    return 1.0


def _compute_performance_fit(collector: CollectorProfile) -> float:
    """
    Reward high performers based on historical gap closure rate, penalize low performers.

    Returns:
        Multiplier: 1.1 if gap_closure_rate > 0.5, 0.8 if < 0.3, 1.0 otherwise
    """
    rate = collector.gap_closure_rate
    if rate > 0.5:
        return 1.1  # Reward proven high performer
    elif rate < 0.3:
        return 0.8  # Penalize low performer
    return 1.0


def _compute_capacity_fit(collector: CollectorProfile) -> float:
    """
    Slight penalty if collector is near max concurrent targets.

    Note: This function doesn't have access to active assignments, so it uses a
    heuristic based on the collector's targets_completed history. A collector with
    few completions but high max_concurrent_targets is assumed to be less experienced.

    Returns:
        Multiplier: 0.9 if likely near capacity, 1.0 otherwise
    """
    # Simple heuristic: if max_concurrent_targets is very high relative to
    # targets_completed, assume the collector is ambitious but untested.
    if collector.targets_completed == 0 and collector.max_concurrent_targets > 3:
        return 0.9

    return 1.0
