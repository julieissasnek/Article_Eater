"""
ARCHIVED: Demo Functions and Stub WebOfBelief
==============================================

Date Archived: 2026-02-10
Reason: Sprint ECB-2 simplification - removing duplicates, demos use deprecated classes
Original Location: src/services/epistemic_causal_bridge.py (lines ~2000-2330)

This module contains:
1. A minimal stub WebOfBelief for standalone testing
2. A Constraint class stub
3. create_demo_system() function with example neuroarchitecture data
4. Demo main block showing counterfactual queries

WHY IT'S VALUABLE:
- Shows how to construct a complete EpistemicCausalBridge setup
- Demonstrates PopulationContext registration
- Demonstrates ContrastClass specification
- Good template for future integration tests
- Shows the three main query types: counterfactual, generalization, epistemic_counterfactual

DEPENDENCIES FOR REINTEGRATION:
- Would need to use web_of_belief.WebOfBelief instead of stub
- Would need to use web_of_belief.Constraint instead of local
- Would need emergent entrenchment (remove explicit entrenchment values)
- CulturalMeaning reintegration (CULT-1 to CULT-5)

NOTES:
- The stub WebOfBelief uses stored entrenchment (V22), not emergent (V23)
- Demo creates beliefs with explicit entrenchment=0.8 (violates V23.0.0)
- PopulationContext examples show Nordic vs Miami contrast (good test case)

WARNING - CONTRAST CLASS LIMITATIONS (van Fraassen, Panel P-ECB-R):
=====================================================================
This stub does NOT properly model contrast classes:
- Beliefs created here lack the contrast_class field
- The stub WebOfBelief doesn't track contrast metadata
- Tests using this stub do NOT validate contrast handling
- Contrast transfer classification (DIRECT, BASELINE_SHIFT, etc.) is not testable

Any tests using this stub may give FALSE CONFIDENCE about contrast handling.
Use the real WebOfBelief from web_of_belief.py for production and for any
tests that need to validate van Fraassen contrast class functionality.

See: docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md for context.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, List, Any
from datetime import datetime, timezone

# NOTE: When reintegrating, import these from web_of_belief.py instead:
# from src.services.web_of_belief import (
#     WebOfBelief, Belief, Constraint, Credence,
#     EpistemicLevel, BeliefStatus, ConstraintType
# )

# For reference, here are the stub classes that were used:


@dataclass
class Constraint:
    """
    ARCHIVED STUB: Use web_of_belief.Constraint instead.

    Constraint between beliefs.
    """
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: Any  # ConstraintType enum
    strength: float = 0.5
    bidirectional: bool = True


class WebOfBelief:
    """
    ARCHIVED STUB: Use web_of_belief.WebOfBelief instead.

    Minimal web of belief implementation for demo functions.
    Full implementation in web_of_belief.py.

    NOTE: This stub's get_entrenchment() returns stored values, while the
    canonical WebOfBelief computes emergent entrenchment per V23.0.0.
    """

    def __init__(self, domain: str = "default"):
        self.domain = domain
        self.beliefs: Dict[str, Any] = {}  # Belief objects
        self.constraints: Dict[str, Constraint] = {}
        self.theory_ids: Set[str] = set()
        self._coherence: float = 0.5

    def add_belief(self, belief: Any):
        self.beliefs[belief.belief_id] = belief
        if hasattr(belief, 'theory_ids'):
            for tid in belief.theory_ids:
                self.theory_ids.add(tid)

    def add_constraint(self, constraint: Constraint):
        self.constraints[constraint.constraint_id] = constraint

    def coherence_score(self) -> float:
        return self._coherence

    def marginal_theory_probability(self, theory_id: str) -> float:
        # Simplified: average credence of theory's beliefs
        theory_beliefs = [
            b for b in self.beliefs.values()
            if hasattr(b, 'theory_ids') and theory_id in b.theory_ids
        ]
        if not theory_beliefs:
            return 0.5
        return sum(b.credence.value for b in theory_beliefs) / len(theory_beliefs)

    def get_entrenchment(self, belief_id: str) -> float:
        """
        V23.0.0: Entrenchment is emergent in the main WebOfBelief.
        This minimal implementation uses the stored value for simplicity.
        """
        if belief_id not in self.beliefs:
            return 0.5
        belief = self.beliefs[belief_id]
        return getattr(belief, 'entrenchment', 0.5)

    def seek_equilibrium(self, max_iterations: int = 10):
        """Simplified equilibrium seeking."""
        # Propagation logic was here - see original for details
        pass

    def _update_coherence(self):
        if not self.constraints:
            self._coherence = 0.5
            return
        # Coherence computation was here - see original for details
        self._coherence = 0.5


# =============================================================================
# DEMO FUNCTION (for reference)
# =============================================================================

"""
def create_demo_system() -> EpistemicCausalBridge:
    '''
    Create a demo system with example neuroarchitecture data.

    This shows:
    1. Creating a WebOfBelief with theoretical and empirical beliefs
    2. Adding ContrastClass to empirical beliefs
    3. Registering PopulationContexts with different baselines
    4. Creating an EpistemicCausalBridge

    REINTEGRATION NOTES:
    - Replace local WebOfBelief with web_of_belief.WebOfBelief
    - Remove explicit entrenchment=0.8 (V23.0.0 computes emergent)
    - CulturalMeaning requires CULT-1 to CULT-5 completion
    '''

    # Create web
    web = WebOfBelief(domain="neuroarchitecture")

    # Add theoretical beliefs
    art_core = Belief(
        belief_id="ART_core",
        content="Natural environments restore directed attention",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.72, 0.2),
        entrenchment=0.8,  # REMOVE for V23.0.0
        theory_ids={"ART": 1.0},
        tags=["outcome:attention", "exposure:nature"]
    )
    web.add_belief(art_core)

    srt_core = Belief(
        belief_id="SRT_core",
        content="Natural environments reduce physiological stress",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.18),
        entrenchment=0.75,  # REMOVE for V23.0.0
        theory_ids={"SRT": 1.0},
        tags=["outcome:stress", "exposure:nature"]
    )
    web.add_belief(srt_core)

    # Add empirical beliefs with contrast class
    sunlight_mood = Belief(
        belief_id="sunlight_mood",
        content="Bright light exposure improves mood",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.68, 0.22),
        entrenchment=0.55,  # REMOVE for V23.0.0
        theory_ids={"SRT": 0.7},
        tags=["outcome:mood", "exposure:light"],
        contrast_class=ContrastClass(
            contrast_id="cc_sunlight",
            focal=ConditionSpec("light", "bright", "Bright light exposure"),
            contrasts=[ConditionSpec("light", "dim", "Dim indoor light")],
            contrast_type=ContrastType.NULL,
            population_context=PopulationContext(
                population_id="Nordic_winter_SAD",
                region="Scandinavia",
                baselines={
                    "light_exposure": BaselineSpec(
                        variable="daily_lux_hours",
                        typical_value=500,
                        variance=200,
                        characterization="very_low"
                    )
                }
            )
        )
    )
    web.add_belief(sunlight_mood)

    # Add constraints
    web.add_constraint(Constraint(
        constraint_id="c1",
        source_id="sunlight_mood",
        target_id="SRT_core",
        constraint_type=ConstraintType.INSTANTIATES,
        strength=0.6
    ))

    # Create bridge
    bridge = EpistemicCausalBridge(web)

    # Register population contexts
    # NORDIC WINTER - Low light baseline
    bridge.register_population_context(PopulationContext(
        population_id="Nordic_winter",
        region="Scandinavia",
        baselines={
            "light_exposure": BaselineSpec(
                variable="daily_lux_hours",
                typical_value=500,
                variance=200,
                characterization="very_low"
            ),
            "nature_exposure": BaselineSpec(
                variable="daily_nature_minutes",
                typical_value=30,
                variance=20,
                characterization="low"
            )
        },
        cultural_meanings={
            "nature": CulturalMeaning(
                culture="Nordic",
                meaning="friluftsliv",
                associations=["identity", "routine", "allemansrätten"],
                valence="positive_normal",
                behavioral_implications="integrated_daily"
            )
        }
    ))

    # MIAMI OUTDOOR - High light baseline
    bridge.register_population_context(PopulationContext(
        population_id="Miami_outdoor",
        region="Florida",
        baselines={
            "light_exposure": BaselineSpec(
                variable="daily_lux_hours",
                typical_value=5000,
                variance=1000,
                characterization="high"
            ),
            "nature_exposure": BaselineSpec(
                variable="daily_nature_minutes",
                typical_value=60,
                variance=40,
                characterization="moderate"
            )
        },
        cultural_meanings={
            "sunlight": CulturalMeaning(
                culture="Floridian",
                meaning="ambient_abundant",
                associations=["beach", "outdoor_lifestyle"],
                valence="positive_normal",
                behavioral_implications="not_scarce"
            )
        }
    ))

    return bridge


# DEMO MAIN BLOCK
if __name__ == "__main__":
    print("=" * 60)
    print("EPISTEMIC-CAUSAL INTEGRATION DEMO")
    print("=" * 60)

    bridge = create_demo_system()
    bridge.build_causal_models(credence_threshold=0.4)

    print("\\n1. COUNTERFACTUAL QUERY")
    print("-" * 40)
    result = bridge.counterfactual(
        intervention={"light": 10000},
        outcome="mood",
        target_population="Nordic_winter"
    )
    print(result.summary())

    print("\\n2. GENERALIZATION ASSESSMENT")
    print("-" * 40)
    gen_result = bridge.assess_generalization(
        belief_id="sunlight_mood",
        target_population="Miami_outdoor"
    )
    print(gen_result.summary())

    print("\\n3. EPISTEMIC COUNTERFACTUAL")
    print("-" * 40)
    ep_result = bridge.epistemic_counterfactual({
        "new_study": {
            "new_belief": "Light therapy ineffective for non-SAD populations",
            "credence": 0.65,
            "contradicts": ["sunlight_mood"]
        }
    })
    print(ep_result.summary())
"""
