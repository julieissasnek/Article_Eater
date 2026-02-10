"""
ARCHIVED: Argument Attack Analysis System
==========================================

Date Archived: 2026-02-10
Reason: Simplification sprint - stabilizing core bridge before adding complexity
Original Location: src/services/epistemic_causal_bridge.py (lines 83-92, 413-465)

This module contains classes for analyzing scientific disagreements as
contrast class shifts rather than simple refutations.

WHY IT'S VALUABLE:
- Many apparent contradictions are contrast shifts, not true refutations
- Resolves "Paper A says X, Paper B says not-X" when they used different contrasts
- Improves coherence assessment (false alarms from pseudo-contradictions)
- Literature synthesis should categorize disagreements by type

DEPENDENCIES FOR REINTEGRATION:
- Core contrast class system working
- Need attack detection in claim extraction (NLP to identify critiques)
- Need shift classification rules or ML classifier
- Need integration with coherence violation detection

FUTURE TODOs:
- ATK-1: Integrate attack analysis with coherence violation detection
- ATK-2: Add attack detection to claim extraction pipeline
- ATK-3: Train classifier for shift type identification
- ATK-4: UI for reviewing detected attacks

KEY REFERENCES:
- Ioannidis, J.P.A. (2005). Contradicted and initially stronger effects. JAMA.
- Walton, D. (2008). Informal Logic: A Pragmatic Approach.
- Van Fraassen, B.C. (1980). The Scientific Image.

See: docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md for full documentation.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Note: ContrastClass and ContrastShiftType would need importing when reintegrated


class AttackType(Enum):
    """Types of argument attack in scientific literature."""
    CONFOUNDER = "confounder"  # "Effect is due to unmeasured confounder"
    BOUNDARY_CONDITION = "boundary_condition"  # "Only true under condition X"
    OVERGENERALIZATION = "overgeneralization"  # "Claim is too broad"
    MECHANISM = "mechanism"  # "Proposed mechanism is wrong"
    MEASUREMENT = "measurement"  # "Measurement was flawed"
    REPLICATION = "replication"  # "Failed to replicate"
    DOSE_RESPONSE = "dose_response"  # "Effect depends on dose differently"
    TEMPORAL = "temporal"  # "Timing/duration matters"


class ContrastShiftType(Enum):
    """How an attack shifts the contrast class."""
    PRESERVING = "preserving"  # Same contrast, disputes finding directly
    POPULATION_SHIFT = "population"  # Different population studied
    BASELINE_SHIFT = "baseline"  # Different baseline level assumed
    MEANING_SHIFT = "meaning"  # Different cultural/contextual meaning
    ALTERNATIVE_SHIFT = "alternative"  # Different comparison condition
    COMPLEX_SHIFT = "complex"  # Multiple shifts simultaneously


@dataclass
class ArgumentAttack:
    """
    An argument attack with contrast class analysis.

    Key insight: Many attacks are contrast shifts, not refutations.
    "Paper B contradicts Paper A" often means "Paper B tested a
    different population/setting/contrast and found different results."
    Both may be correct within their contrast classes.
    """
    attack_id: str
    source_paper_id: str  # Paper making the attack
    target_belief_id: str  # Belief being attacked
    attack_type: AttackType

    # The attack claim
    attack_claim: str  # e.g., "Effect disappears in rural populations"
    attack_credence: float  # How confident is the attack?

    # Contrast class analysis
    original_contrast: Optional[Any] = None  # ContrastClass when reintegrated
    shifted_contrast: Optional[Any] = None  # ContrastClass when reintegrated
    shift_type: ContrastShiftType = ContrastShiftType.PRESERVING

    # Outcome under each contrast
    outcome_under_original: Optional[str] = None  # e.g., "Effect present"
    outcome_under_shifted: Optional[str] = None  # e.g., "No effect"

    # Resolution
    resolution: Optional[str] = None  # e.g., "Boundary condition identified"
    resolution_credence: Optional[float] = None

    def is_contrast_preserving(self) -> bool:
        """True if attack disputes finding within same contrast class."""
        return self.shift_type == ContrastShiftType.PRESERVING

    def is_contrast_shifting(self) -> bool:
        """True if attack shifts to different contrast class."""
        return self.shift_type != ContrastShiftType.PRESERVING


@dataclass
class AttackContrastAnalysis:
    """
    Analysis of how an attack relates to contrast class.

    Used to determine whether an apparent contradiction is:
    1. A true refutation (same contrast, opposite finding)
    2. A boundary condition (different contrast, consistent findings)
    """
    attack_id: str
    analysis_type: str  # "preserving" or "shifting"

    original_contrast: Any  # ContrastClass when reintegrated
    attack_contrast: Any  # ContrastClass when reintegrated

    shift_type: Optional[ContrastShiftType] = None

    implication: str = ""  # What this means for the original claim
    resolution_approach: str = ""  # How to resolve the tension

    # For shifting attacks, both may be valid
    original_validity: str = ""  # e.g., "Valid for urban populations"
    attack_validity: str = ""  # e.g., "Valid for rural populations"


# Example usage:
"""
# Paper A: "Nature exposure reduces stress" (urban office workers, vs. office)
# Paper B: "No effect of nature on stress" (rural residents, vs. outdoors)

attack = ArgumentAttack(
    attack_id='attack_001',
    source_paper_id='paper_b_2020',
    target_belief_id='belief:nature_reduces_stress',
    attack_type=AttackType.BOUNDARY_CONDITION,
    attack_claim="No effect of nature on stress in rural populations",
    attack_credence=0.75,
    shift_type=ContrastShiftType.POPULATION_SHIFT,
    outcome_under_original="Stress reduction observed",
    outcome_under_shifted="No stress reduction observed",
    resolution="Boundary condition: effect depends on baseline nature exposure"
)

# Analysis reveals this is NOT a refutation:
# - Paper A: Nature (focal) vs. Office (contrast) → Effect
# - Paper B: Nature (focal) vs. Outdoors (contrast) → No effect
# Different contrasts → both papers may be correct
"""
