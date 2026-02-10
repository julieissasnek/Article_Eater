"""
ARCHIVED: Individual Difference System
=======================================

Date Archived: 2026-02-10
Reason: Simplification sprint - stabilizing core bridge before adding complexity
Original Location: src/services/epistemic_causal_bridge.py (lines 352-406)

This module contains classes for personalized counterfactual inference based on
individual characteristics like chronotype, nature connectedness, and stress levels.

WHY IT'S VALUABLE:
- Enables precision-medicine-style personalized recommendations
- Known moderators exist in CNfA literature (Mayer & Frantz 2004, Nisbet et al. 2009)
- Design implications: personalized neuroarchitecture recommendations

DEPENDENCIES FOR REINTEGRATION:
- Core bridge must be stable (EpistemicCausalBridge working end-to-end)
- Need literature review of moderator effect sizes
- Need UI for individual profile input (CNS questionnaire, etc.)
- Need validation against actual individual data

FUTURE TODOs:
- IND-1: Literature review of individual difference moderators in CNfA
- IND-2: Populate IndividualDifferenceFactor with literature data
- IND-3: Add CNS questionnaire to Streamlit UI
- IND-4: Validate personalized predictions

KEY REFERENCES:
- Mayer, F.S., & Frantz, C.M. (2004). The connectedness to nature scale. Environment and Behavior.
- Nisbet, E.K., Zelenski, J.M., & Murphy, S.A. (2009). The nature relatedness scale. Environment and Behavior.
- Roenneberg, T., et al. (2003). Life between clocks: Daily temporal patterns of human chronotypes.

See: docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md for full documentation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

# Note: These imports would need updating when reintegrating
# from src.services.epistemic_causal_bridge import Belief, PopulationContext


@dataclass
class IndividualDifferenceProfile:
    """
    Individual difference profile for personalized inference.

    Contains trait factors (stable individual characteristics),
    state factors (current conditions), and context factors.
    """

    # Trait factors (stable characteristics)
    chronotype: Optional[float] = None  # MEQ score (morningness-eveningness)
    nature_connectedness: Optional[float] = None  # CNS score (0-5 scale)
    big_five: Dict[str, float] = field(default_factory=dict)  # O, C, E, A, N

    # State factors (current conditions)
    current_stress: Optional[float] = None  # 0-10 scale
    current_fatigue: Optional[float] = None  # 0-10 scale
    baseline_mood: Optional[float] = None  # -1 to 1 scale

    # History/context factors
    typical_nature_exposure: Optional[float] = None  # hours/week
    typical_sunlight_exposure: Optional[float] = None  # hours/day
    urbanicity: Optional[float] = None  # 0-1 scale (0=rural, 1=dense urban)

    # Cultural background
    cultural_background: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def is_complete(self) -> bool:
        """Check if profile has minimum required fields."""
        return self.nature_connectedness is not None or self.urbanicity is not None


@dataclass
class IndividualDifferenceFactor:
    """
    Specification of how an individual difference affects inference.

    Used to model how traits like nature connectedness or chronotype
    modify the expected effect of environmental interventions.
    """
    factor_id: str
    construct: str  # e.g., "nature_connectedness"
    measures: List[str]  # e.g., ["CNS", "NR-6"]

    # Effect on baseline (what's the person's starting point?)
    effect_on_baseline: Dict[str, str]  # variable -> direction

    # Effect on intervention response (how much benefit do they get?)
    effect_on_response: Dict[str, str]  # variable -> direction

    # Research references supporting this factor
    key_references: List[str] = field(default_factory=list)

    # Cultural interactions (how does this vary by culture?)
    cultural_interactions: Dict[str, str] = field(default_factory=dict)

    def compute_modifier(
        self,
        individual_value: float,
        belief: Any,  # Would be Belief when reintegrated
        context: Any  # Would be PopulationContext when reintegrated
    ) -> Tuple[float, str]:
        """
        Compute effect modifier for an individual.

        Args:
            individual_value: The person's score on this factor
            belief: The belief being modified
            context: The population context

        Returns:
            Tuple of (multiplier, explanation)
        """
        # Default implementation - would be extended with actual effect sizes
        # from literature when reintegrated
        return (1.0, "No specific modifier computed - needs literature data")


# Example usage (for documentation):
"""
# Creating a profile for a specific user:
profile = IndividualDifferenceProfile(
    nature_connectedness=4.2,  # High CNS
    chronotype=65,  # Morning type
    urbanicity=0.9,  # Very urban
    typical_nature_exposure=2.0,  # 2 hours/week (low)
    current_stress=7.0  # High stress
)

# This profile would predict larger-than-average benefits from nature exposure:
# - High nature connectedness → stronger affective response
# - Low baseline exposure → not saturated
# - High stress → more room for recovery
"""
