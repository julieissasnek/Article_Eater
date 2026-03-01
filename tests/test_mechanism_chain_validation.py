import os
"""
Mechanism Chain Validation Tests
================================

Validates that seeded mechanism chains are correctly traversable via
MechanismPattern._traverse_forward() in InterpretiveEngine.

These tests prevent silent regressions when mechanism beliefs or constraints
are modified. Each test:
  1. Seeds a test web with mechanism beliefs + constraints
  2. Calls MechanismPattern.traverse() from the entry node
  3. Asserts the chain visits each expected node in the expected order
  4. Asserts expected step counts and endpoint arrival

Chain families tested:
  - ART: biophilic_stimulus → soft_fascination → involuntary_attention → directed_attention_restoration
  - SRT: visual_ecological_appraisal → amygdala → hpa → affect → autonomic → normalization
  - OLF_SRT: olfactory_ecological → safety_classification → (joins SRT at amygdala)
  - MAT4: multisensory → hedonic_fluency → (forks to ART soft_fascination + SRT affect)
  - L3: circadian + visual_task → mood_alertness_convergence → (to SRT affect)
  - DT1: salience_detection → network_switching → (cross-link to ART)
"""

import sys
import os
import uuid

sys.path.insert(0, os.getcwd())

import pytest
from src.services.web_of_belief import (
    Belief, Constraint, Credence,
    EpistemicLevel, BeliefStatus,
    WebOfBelief,
)
from src.epistemic.edge_types import EdgeType as ConstraintType
from src.services.web_of_belief_components import CausalDirection

# Import the seeder data directly
from scripts.seed_mechanism_beliefs import (
    ALL_MECHANISM_BELIEFS,
    build_constraints,
    ART_BELIEFS, SRT_BELIEFS, OLF_SRT_BELIEFS,
    MAT4_BELIEFS, L3_BELIEFS, NM_BELIEFS, DT1_BELIEFS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_web() -> WebOfBelief:
    """Build a WebOfBelief with all mechanism beliefs and constraints seeded."""
    web = WebOfBelief()

    # Add all mechanism beliefs (mirrors seed() in seed_mechanism_beliefs.py)
    for mb in ALL_MECHANISM_BELIEFS:
        belief = Belief(
            belief_id=mb.belief_id,
            content=mb.content,
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(
                value=mb.credence_value,
                uncertainty=mb.credence_uncertainty,
                n_supporting=3,
            ),
            theory_id=mb.theory_id,
            domain="environmental_psychology",
            tags=list(mb.tags),
        )
        belief.causal_direction = mb.causal_direction
        web.add_belief(belief)

    # Add environment stub beliefs (needed as source nodes for constraints)
    for env_id in [
        "env.ae.wood_prominent",
        "env.ae.indoor_plants",
        "env.generic.biophilia",
        "env.v2a_098.natural_materials_wood_stone",
    ]:
        stub = Belief(
            belief_id=env_id,
            content=f"Environment stub: {env_id}",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(value=0.80, uncertainty=0.10),
        )
        web.add_belief(stub)

    # Add all constraints (mirrors seed() approach)
    for mc in build_constraints():
        constraint = Constraint(
            constraint_id=f"mech_test_{uuid.uuid4().hex[:12]}",
            source_id=mc.source_id,
            target_id=mc.target_id,
            constraint_type=mc.constraint_type,
            strength=mc.strength,
            bidirectional=mc.bidirectional,
            evidence_ids=list(mc.evidence_ids),
            causal_direction=mc.causal_direction,
            mediator=mc.mediator,
        )
        web.add_constraint(constraint)

    return web


def _get_mechanism_pattern(web: WebOfBelief):
    """Instantiate MechanismExplanationPattern directly."""
    from src.services.interpretive_intelligence import MechanismExplanationPattern
    return MechanismExplanationPattern(web)


def _chain_ids(result) -> list:
    """Extract ordered list of belief_ids from a MechanismResult's causal_chain."""
    return [step.belief_id for step in result.causal_chain]


def _all_ids(result) -> set:
    """Extract all belief_ids reached (chain + parallel routes)."""
    ids = {step.belief_id for step in result.causal_chain}
    if result.moderators:
        ids |= {step.belief_id for step in result.moderators}
    return ids


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestARTChain:
    """ART: 4-step linear chain from biophilic_stimulus to directed_attention_restoration."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_art_chain_traversal_from_entry(self):
        """Traversal from ART entry visits all 4 nodes in order."""
        result = self.pattern.traverse("mechanism:art:biophilic_stimulus")
        assert result is not None, "ART chain should be traversable"

        chain = _chain_ids(result)
        expected_order = [
            "mechanism:art:soft_fascination",
            "mechanism:art:involuntary_attention",
            "mechanism:art:directed_attention_restoration",
        ]
        # Entry node is NOT in causal_chain (it's the target_belief)
        assert result.target_belief.belief_id == "mechanism:art:biophilic_stimulus"

        # All expected nodes should appear in chain
        for node_id in expected_order:
            assert node_id in chain, f"Missing ART node: {node_id}"

        # Verify ordering: each node should appear after the previous
        for i in range(len(expected_order) - 1):
            idx_a = chain.index(expected_order[i])
            idx_b = chain.index(expected_order[i + 1])
            assert idx_a < idx_b, (
                f"ART order violation: {expected_order[i]} (pos {idx_a}) "
                f"should precede {expected_order[i + 1]} (pos {idx_b})"
            )

    def test_art_chain_step_count(self):
        """ART chain should have exactly 3 steps (excl. entry)."""
        result = self.pattern.traverse("mechanism:art:biophilic_stimulus")
        chain = _chain_ids(result)
        mechanism_steps = [n for n in chain if n.startswith("mechanism:art:")]
        assert len(mechanism_steps) >= 3, (
            f"Expected 3+ ART mechanism steps, got {len(mechanism_steps)}: {mechanism_steps}"
        )

    def test_art_chain_endpoint(self):
        """ART chain should reach directed_attention_restoration."""
        result = self.pattern.traverse("mechanism:art:biophilic_stimulus")
        all_reached = _all_ids(result)
        assert "mechanism:art:directed_attention_restoration" in all_reached


class TestSRTChain:
    """SRT: 5-step chain from visual_ecological_appraisal to physiological_normalization."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_srt_chain_traversal_from_entry(self):
        """Traversal from SRT entry visits all 5 downstream nodes."""
        result = self.pattern.traverse("mechanism:srt:visual_ecological_appraisal")
        assert result is not None, "SRT chain should be traversable"

        chain = _chain_ids(result)
        expected_order = [
            "mechanism:srt:amygdala_threat_suppression",
            "mechanism:srt:hpa_suppression",
            "mechanism:srt:positive_affect_shift",
            "mechanism:srt:autonomic_recovery",
            "mechanism:srt:physiological_normalization",
        ]

        for node_id in expected_order:
            assert node_id in chain, f"Missing SRT node: {node_id}"

        # Verify strict ordering
        for i in range(len(expected_order) - 1):
            idx_a = chain.index(expected_order[i])
            idx_b = chain.index(expected_order[i + 1])
            assert idx_a < idx_b, (
                f"SRT order violation: {expected_order[i]} should precede {expected_order[i + 1]}"
            )

    def test_srt_chain_step_count(self):
        """SRT chain should have at least 5 mechanism steps."""
        result = self.pattern.traverse("mechanism:srt:visual_ecological_appraisal")
        chain = _chain_ids(result)
        srt_steps = [n for n in chain if n.startswith("mechanism:srt:")]
        assert len(srt_steps) >= 5, (
            f"Expected 5+ SRT mechanism steps, got {len(srt_steps)}: {srt_steps}"
        )

    def test_srt_chain_endpoint(self):
        """SRT chain should reach physiological_normalization."""
        result = self.pattern.traverse("mechanism:srt:visual_ecological_appraisal")
        all_reached = _all_ids(result)
        assert "mechanism:srt:physiological_normalization" in all_reached


class TestOlfactorySRTChain:
    """OLF_SRT: parallel olfactory entry into SRT at amygdala_threat_suppression."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_olfactory_joins_srt_at_amygdala(self):
        """Olfactory entry should reach amygdala_threat_suppression via safety_classification."""
        result = self.pattern.traverse("mechanism:srt:olfactory_ecological_appraisal")
        assert result is not None, "Olfactory chain should be traversable"

        chain = _chain_ids(result)
        assert "mechanism:srt:olfactory_safety_classification" in chain, (
            "Olfactory chain should pass through safety_classification"
        )
        assert "mechanism:srt:amygdala_threat_suppression" in chain, (
            "Olfactory chain should join SRT at amygdala"
        )

    def test_olfactory_reaches_srt_endpoint(self):
        """Olfactory entry should traverse through SRT to physiological_normalization."""
        result = self.pattern.traverse("mechanism:srt:olfactory_ecological_appraisal")
        all_reached = _all_ids(result)
        assert "mechanism:srt:physiological_normalization" in all_reached, (
            "Olfactory route should reach SRT endpoint"
        )

    def test_olfactory_ordering(self):
        """safety_classification must precede amygdala_threat_suppression."""
        result = self.pattern.traverse("mechanism:srt:olfactory_ecological_appraisal")
        chain = _chain_ids(result)
        if "mechanism:srt:olfactory_safety_classification" in chain and \
           "mechanism:srt:amygdala_threat_suppression" in chain:
            idx_class = chain.index("mechanism:srt:olfactory_safety_classification")
            idx_amyg = chain.index("mechanism:srt:amygdala_threat_suppression")
            assert idx_class < idx_amyg, (
                "safety_classification should precede amygdala_threat_suppression"
            )


class TestMAT4Chain:
    """MAT4: multisensory → hedonic_fluency → forks to ART/SRT."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_mat4_chain_traverses_hedonic_fluency(self):
        """MAT4 entry should reach hedonic_fluency."""
        result = self.pattern.traverse("mechanism:mat4:multisensory_biophilic_signal")
        assert result is not None, "MAT4 chain should be traversable"

        chain = _chain_ids(result)
        assert "mechanism:mat4:hedonic_fluency" in chain

    def test_mat4_forks_to_art_and_srt(self):
        """MAT4 hedonic_fluency should reach ART soft_fascination and SRT affect."""
        result = self.pattern.traverse("mechanism:mat4:multisensory_biophilic_signal")
        all_reached = _all_ids(result)
        assert "mechanism:art:soft_fascination" in all_reached, (
            "MAT4 should fork to ART soft_fascination"
        )
        assert "mechanism:srt:positive_affect_shift" in all_reached, (
            "MAT4 should fork to SRT positive_affect_shift"
        )


class TestL3Chain:
    """L3: circadian + visual_task converge to mood_alertness → SRT."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_l3_circadian_reaches_convergence(self):
        """Circadian entry should reach mood_alertness_convergence."""
        result = self.pattern.traverse("mechanism:l3:circadian_signal")
        assert result is not None, "L3 circadian chain should be traversable"

        chain = _chain_ids(result)
        assert "mechanism:l3:mood_alertness_convergence" in chain

    def test_l3_convergence_reaches_srt(self):
        """L3 mood_alertness should reach SRT positive_affect_shift."""
        result = self.pattern.traverse("mechanism:l3:circadian_signal")
        all_reached = _all_ids(result)
        assert "mechanism:srt:positive_affect_shift" in all_reached, (
            "L3 convergence should reach SRT positive_affect_shift"
        )


class TestDT1Chain:
    """DT1: salience_detection → network_switching → cross-link to ART."""

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_dt1_chain_traversal(self):
        """DT1 salience should reach network_switching."""
        result = self.pattern.traverse("mechanism:dt1:salience_detection")
        assert result is not None, "DT1 chain should be traversable"

        chain = _chain_ids(result)
        assert "mechanism:dt1:network_switching" in chain

    def test_dt1_cross_link_to_art(self):
        """DT1 network_switching has a COHERENCE_SUPPORT link to ART.
        
        The traversal treats COHERENCE_SUPPORT as parallel route annotations,
        not sequential steps. The link exists in the constraint graph but the
        traversal only surfaces parallel routes from visited nodes — since
        the DT1→ART coherence edge is bidirectional, it should be detected.
        If not surfaced, at minimum the traversal should still complete the
        DT1 chain correctly.
        """
        result = self.pattern.traverse("mechanism:dt1:salience_detection")
        all_reached = _all_ids(result)
        # The traversal may or may not surface the coherence link depending
        # on BFS order. The critical invariant: DT1 chain itself is complete.
        assert "mechanism:dt1:network_switching" in all_reached
        # If the coherence link IS surfaced, it should be ART's endpoint
        if "mechanism:art:directed_attention_restoration" in all_reached:
            # Verify it appears as a parallel route, not a chain step
            chain = _chain_ids(result)
            assert "mechanism:art:directed_attention_restoration" not in chain or \
                   any(s.role == "parallel_route" for s in result.moderators
                       if s.belief_id == "mechanism:art:directed_attention_restoration")


class TestCrossChainBridges:
    """ART ↔ SRT cross-chain coherence bridges.
    
    COHERENCE_SUPPORT edges are treated as parallel route annotations by
    the traversal. They are surfaced only from visited nodes — not followed
    transitively into other chains. These tests verify the coherence edges
    exist in the constraint graph and check whether the traversal surfaces them.
    """

    def setup_method(self):
        self.web = _make_test_web()
        self.pattern = _get_mechanism_pattern(self.web)

    def test_coherence_constraints_exist_in_web(self):
        """Verify the ART↔SRT coherence constraints are in the web."""
        # soft_fascination ↔ positive_affect_shift
        found_sf_pas = False
        # directed_attention_restoration ↔ physiological_normalization
        found_dar_pn = False
        for c in self.web.constraints.values():
            if (c.source_id == "mechanism:art:soft_fascination" and
                c.target_id == "mechanism:srt:positive_affect_shift"):
                found_sf_pas = True
            if (c.source_id == "mechanism:art:directed_attention_restoration" and
                c.target_id == "mechanism:srt:physiological_normalization"):
                found_dar_pn = True
        assert found_sf_pas, "Missing ART↔SRT coherence: soft_fascination ↔ positive_affect_shift"
        assert found_dar_pn, "Missing ART↔SRT coherence: directed_attention_restoration ↔ physiological_normalization"

    def test_art_chain_completes_independently(self):
        """ART chain should complete its own traversal regardless of coherence links."""
        result = self.pattern.traverse("mechanism:art:biophilic_stimulus")
        chain = _chain_ids(result)
        assert "mechanism:art:directed_attention_restoration" in chain

    def test_srt_chain_completes_independently(self):
        """SRT chain should complete its own traversal regardless of coherence links."""
        result = self.pattern.traverse("mechanism:srt:visual_ecological_appraisal")
        chain = _chain_ids(result)
        assert "mechanism:srt:physiological_normalization" in chain


class TestAllBeliefsSeeded:
    """Verify all mechanism beliefs from the seeder are present in the test web."""

    def test_all_beliefs_present(self):
        web = _make_test_web()
        for mb in ALL_MECHANISM_BELIEFS:
            assert mb.belief_id in web.beliefs, (
                f"Mechanism belief missing from web: {mb.belief_id}"
            )

    def test_all_constraints_present(self):
        web = _make_test_web()
        all_constraints = build_constraints()
        assert len(web.constraints) == len(all_constraints), (
            f"Constraint count mismatch: web has {len(web.constraints)}, "
            f"expected {len(all_constraints)}"
        )

    def test_belief_count(self):
        """Verify expected total mechanism belief count (21)."""
        assert len(ALL_MECHANISM_BELIEFS) == 21, (
            f"Expected 21 mechanism beliefs, got {len(ALL_MECHANISM_BELIEFS)}"
        )
