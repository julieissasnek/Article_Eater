"""
Canonical GapType Enum — Single Source of Truth.

Per Canonical Decisions Record (02-15_09), Decision 1:
All gap-related services MUST import GapType from this module.

This replaces local enums in:
- src/services/gap_predictor.py
- src/services/voi_search.py
- src/services/discovery_funnel.py

Gap Types (per Panel P-LAYER):
1. MEDIATION: A→X→Y exists but direct A→Y missing
2. MECHANISM: Empirical beliefs but no theoretical explanation
3. BOUNDARY: Narrow scope conditions
4. DIRECTION: Conflicting causal directions
5. INTERACTION: Independent effects without interaction beliefs
6. VALIDATION: Theoretical beliefs without empirical support
7. UNJUSTIFIED_EDGE: BN edge without belief support
8. CRITICAL_QUESTION: Walton critical question unaddressed (Sprint 10)
9. ARGUMENT_ATTACK: Known attack type applies (Sprint 10)
"""

from enum import Enum


class GapType(str, Enum):
    """
    Canonical gap types for knowledge gap prediction.

    Used by GapPredictor, VOISearch, DiscoveryFunnel, and ResearchQueue.
    """
    MEDIATION = "mediation"        # A→X→Y exists but direct A→Y missing
    MECHANISM = "mechanism"        # Empirical but no theoretical explanation
    BOUNDARY = "boundary"          # Narrow scope conditions
    DIRECTION = "direction"        # Conflicting causal directions
    INTERACTION = "interaction"    # Independent effects, no interaction
    VALIDATION = "validation"      # Theoretical but no empirical support
    UNJUSTIFIED_EDGE = "unjustified_edge"  # BN edge without belief support
    CRITICAL_QUESTION = "critical_question"  # Walton CQ unaddressed
    ARGUMENT_ATTACK = "argument_attack"      # Known attack type applies


class GapPriority(str, Enum):
    """Priority levels for gaps."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Priority weights per gap type (per Panel P-QUEUE-1)
GAP_TYPE_WEIGHTS = {
    GapType.DIRECTION: 0.9,         # Causal confusion propagates
    GapType.MECHANISM: 0.7,         # Explanatory gap
    GapType.VALIDATION: 0.6,        # Theory needs grounding
    GapType.MEDIATION: 0.5,         # Structural completeness
    GapType.BOUNDARY: 0.4,          # Scope clarification
    GapType.INTERACTION: 0.5,       # Combinatorial effects
    GapType.UNJUSTIFIED_EDGE: 0.85, # HIGH - edge has no evidence
    GapType.CRITICAL_QUESTION: 0.6, # Argument structure
    GapType.ARGUMENT_ATTACK: 0.7,   # Known vulnerability
}


# Mapping from legacy enum values (voi_search, discovery_funnel) to canonical
LEGACY_GAP_TYPE_MAP = {
    # voi_search.py legacy values
    "contradiction": GapType.DIRECTION,
    "uncertain": GapType.VALIDATION,
    "unexplored": GapType.MECHANISM,
    "boundary_unclear": GapType.BOUNDARY,
    # discovery_funnel.py legacy values
    "missing_evidence": GapType.MECHANISM,
    "weak_support": GapType.VALIDATION,
}


def convert_legacy_gap_type(legacy_value: str) -> GapType:
    """Convert legacy gap type string to canonical GapType."""
    # Try direct match first
    try:
        return GapType(legacy_value)
    except ValueError:
        pass

    # Try legacy mapping
    if legacy_value.lower() in LEGACY_GAP_TYPE_MAP:
        return LEGACY_GAP_TYPE_MAP[legacy_value.lower()]

    # Default fallback
    return GapType.MECHANISM
