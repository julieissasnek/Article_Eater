"""
Tests for ARCH-4 P2-P6 Epistemic Services.

Tests the formal epistemic calculus implementation:
- P2: RankingService (Spohn)
- P3: WarrantService (Pollock)
- P4: GroundingService (Haack)
- P5: GraphConfidenceService (Pearl)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import unittest
from unittest.mock import MagicMock, patch
from services.ranking_service import (
    RankingService,
    RankPair,
    RankingResult,
    credence_to_ranks,
    MAX_RANK
)
from services.warrant_service import (
    WarrantService,
    WarrantStatus,
    DefeatType,
    DefeatRelation,
    DefeatChain,
    WarrantResult,
    create_defeat_relation
)
from services.grounding_service import (
    GroundingService,
    GroundingStatus,
    JustificationStatus,
    ExperientialClaim,
    GroundingChain,
    FoundherentistScore,
    GroundingResult,
    create_experiential_claim
)
from services.graph_confidence_service import (
    GraphConfidenceService,
    IdentifiabilityStatus,
    EdgeConfidence,
    StructureUncertainty,
    CausalEffectBounds,
    GraphConfidenceResult
)


# ============================================================
# P2: RANKING SERVICE TESTS
# ============================================================

class TestRankPair(unittest.TestCase):
    """Test RankPair dataclass."""

    def test_believed_when_neg_rank_higher(self):
        """Belief is believed when κ(¬B) > κ(B)."""
        rp = RankPair(rank=0, neg_rank=5)
        self.assertTrue(rp.believed)
        self.assertFalse(rp.disbelieved)
        self.assertFalse(rp.suspended)

    def test_disbelieved_when_rank_higher(self):
        """Belief is disbelieved when κ(B) > κ(¬B)."""
        rp = RankPair(rank=5, neg_rank=0)
        self.assertFalse(rp.believed)
        self.assertTrue(rp.disbelieved)
        self.assertFalse(rp.suspended)

    def test_suspended_when_equal(self):
        """Belief is suspended when κ(B) = κ(¬B)."""
        rp = RankPair(rank=3, neg_rank=3)
        self.assertFalse(rp.believed)
        self.assertFalse(rp.disbelieved)
        self.assertTrue(rp.suspended)

    def test_firmness(self):
        """Firmness is absolute difference."""
        rp = RankPair(rank=2, neg_rank=7)
        self.assertEqual(rp.firmness, 5)

    def test_clamping(self):
        """Ranks should be clamped to valid range."""
        rp = RankPair(rank=-5, neg_rank=200)
        self.assertEqual(rp.rank, 0)
        self.assertEqual(rp.neg_rank, MAX_RANK)

    def test_to_dict(self):
        """Should serialize correctly."""
        rp = RankPair(rank=1, neg_rank=4)
        d = rp.to_dict()
        self.assertEqual(d["rank"], 1)
        self.assertEqual(d["neg_rank"], 4)
        self.assertTrue(d["believed"])


class TestCredenceToRanks(unittest.TestCase):
    """Test credence to rank conversion."""

    def test_high_credence_is_believed(self):
        """High credence (>0.5) should produce believed state."""
        rp = credence_to_ranks(0.9)
        self.assertTrue(rp.believed)
        self.assertEqual(rp.rank, 0)
        self.assertGreater(rp.neg_rank, 0)

    def test_low_credence_is_disbelieved(self):
        """Low credence (<0.5) should produce disbelieved state."""
        rp = credence_to_ranks(0.2)
        self.assertTrue(rp.disbelieved)
        self.assertGreater(rp.rank, 0)
        self.assertEqual(rp.neg_rank, 0)

    def test_neutral_credence_is_suspended(self):
        """Neutral credence (0.5) should produce suspended state."""
        rp = credence_to_ranks(0.5)
        self.assertTrue(rp.suspended)
        self.assertEqual(rp.rank, 0)
        self.assertEqual(rp.neg_rank, 0)

    def test_uncertainty_affects_firmness(self):
        """Higher uncertainty should reduce firmness."""
        certain = credence_to_ranks(0.8, uncertainty=0.1)
        uncertain = credence_to_ranks(0.8, uncertainty=0.8)
        self.assertGreater(certain.firmness, uncertain.firmness)


class TestRankingService(unittest.TestCase):
    """Test RankingService."""

    def setUp(self):
        self.service = RankingService()

    def test_ranks_to_credence_roundtrip(self):
        """Ranks -> credence -> ranks should preserve direction."""
        original = RankPair(rank=0, neg_rank=5)
        credence, uncertainty = self.service.ranks_to_credence(original)

        self.assertGreater(credence, 0.5)  # Should be believed

        recovered = self.service.credence_to_ranks(credence, uncertainty)
        self.assertTrue(recovered.believed)


# ============================================================
# P3: WARRANT SERVICE TESTS
# ============================================================

class TestDefeatRelation(unittest.TestCase):
    """Test DefeatRelation dataclass."""

    def test_create_defeat_relation(self):
        """Should create defeat relation."""
        dr = create_defeat_relation("d1", "b1", "REBUTTING", 0.8)
        self.assertEqual(dr.defeater_id, "d1")
        self.assertEqual(dr.defeated_id, "b1")
        self.assertEqual(dr.defeat_type, DefeatType.REBUTTING)
        self.assertEqual(dr.strength, 0.8)

    def test_to_dict(self):
        """Should serialize correctly."""
        dr = create_defeat_relation("d1", "b1", "UNDERCUTTING")
        d = dr.to_dict()
        self.assertEqual(d["defeat_type"], "UNDERCUTTING")


class TestWarrantService(unittest.TestCase):
    """Test WarrantService."""

    def setUp(self):
        self.service = WarrantService()

    def test_observational_is_warranted(self):
        """Observational beliefs should be warranted without support."""
        # Create mock web
        mock_web = MagicMock()
        mock_web.beliefs = {"obs1": MagicMock()}
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []

        # Mock level
        mock_web.beliefs["obs1"].level.value = "OBSERVATIONAL"

        ranks = {"obs1": RankPair(rank=0, neg_rank=5)}

        result = self.service.compute_warrant(
            mock_web, ranks, [], observational_beliefs={"obs1"}
        )

        self.assertIn("obs1", result.warranted)

    def test_unsupported_is_ungrounded(self):
        """Non-observational belief without support should be ungrounded."""
        mock_web = MagicMock()
        mock_web.beliefs = {"emp1": MagicMock()}
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []
        mock_web.beliefs["emp1"].level.value = "EMPIRICAL"

        ranks = {"emp1": RankPair(rank=0, neg_rank=5)}

        result = self.service.compute_warrant(
            mock_web, ranks, [], observational_beliefs=set()
        )

        self.assertIn("emp1", result.ungrounded)

    def test_defeated_belief_not_warranted(self):
        """Belief with warranted defeater should be defeated."""
        mock_web = MagicMock()
        mock_web.beliefs = {
            "b1": MagicMock(),
            "d1": MagicMock()
        }
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []
        mock_web.beliefs["b1"].level.value = "EMPIRICAL"
        mock_web.beliefs["d1"].level.value = "OBSERVATIONAL"

        ranks = {
            "b1": RankPair(rank=0, neg_rank=5),
            "d1": RankPair(rank=0, neg_rank=5)
        }

        defeat_rel = create_defeat_relation("d1", "b1", "REBUTTING")

        result = self.service.compute_warrant(
            mock_web, ranks, [defeat_rel],
            observational_beliefs={"d1", "b1"}  # Both have prima facie warrant
        )

        # d1 should be warranted (observational, no defeaters)
        self.assertIn("d1", result.warranted)
        # b1 should be defeated (d1 defeats it)
        self.assertIn("b1", result.defeated)


class TestDefeatChain(unittest.TestCase):
    """Test DefeatChain dataclass."""

    def test_to_dict(self):
        """Should serialize correctly."""
        chain = DefeatChain(
            belief_id="b1",
            status=WarrantStatus.DEFEATED,
            defeaters=["d1"],
            reinstaters=[],
            cycle_members=[],
            depth=1
        )
        d = chain.to_dict()
        self.assertEqual(d["status"], "DEFEATED")
        self.assertEqual(d["defeaters"], ["d1"])


# ============================================================
# P4: GROUNDING SERVICE TESTS
# ============================================================

class TestExperientialClaim(unittest.TestCase):
    """Test ExperientialClaim dataclass."""

    def test_create_experiential_claim(self):
        """Should create experiential claim."""
        ec = create_experiential_claim(
            claim_id="ec1",
            source="paper_123",
            content="Observed natural light",
            directness=0.9
        )
        self.assertEqual(ec.directness, 0.9)
        self.assertEqual(ec.source_type, "observation")

    def test_to_dict(self):
        """Should serialize correctly."""
        ec = create_experiential_claim("ec1", "paper", "content")
        d = ec.to_dict()
        self.assertIn("directness", d)


class TestGroundingService(unittest.TestCase):
    """Test GroundingService."""

    def setUp(self):
        self.service = GroundingService()

    def test_observational_is_grounded(self):
        """Observational beliefs should be grounded."""
        mock_web = MagicMock()
        mock_web.beliefs = {"obs1": MagicMock()}
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []
        mock_web.beliefs["obs1"].level.value = "OBSERVATIONAL"

        result = self.service.compute_grounding(
            mock_web, warranted_beliefs={"obs1"}
        )

        self.assertIn("obs1", result.grounded_beliefs)

    def test_unsupported_empirical_ungrounded(self):
        """Empirical belief without support path should be ungrounded."""
        mock_web = MagicMock()
        mock_web.beliefs = {"emp1": MagicMock()}
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []
        mock_web.beliefs["emp1"].level.value = "EMPIRICAL"

        result = self.service.compute_grounding(
            mock_web, warranted_beliefs=set()
        )

        self.assertIn("emp1", result.ungrounded_beliefs)


class TestFoundherentistScore(unittest.TestCase):
    """Test FoundherentistScore dataclass."""

    def test_to_dict(self):
        """Should serialize correctly."""
        score = FoundherentistScore(
            belief_id="b1",
            grounding_component=0.8,
            coherence_component=0.6,
            combined_score=0.7,
            justification_status=JustificationStatus.WELL_JUSTIFIED,
            grounding_chain=None
        )
        d = score.to_dict()
        self.assertEqual(d["justification_status"], "WELL_JUSTIFIED")


# ============================================================
# P5: GRAPH CONFIDENCE SERVICE TESTS
# ============================================================

class TestEdgeConfidence(unittest.TestCase):
    """Test EdgeConfidence dataclass."""

    def test_to_dict(self):
        """Should serialize correctly."""
        ec = EdgeConfidence(
            source="X",
            target="Y",
            confidence=0.75,
            warrant_component=0.8,
            grounding_component=0.7,
            rank_component=0.6,
            supporting_belief_ids=["b1", "b2"],
            identifiability=IdentifiabilityStatus.IDENTIFIABLE
        )
        d = ec.to_dict()
        self.assertEqual(d["confidence"], 0.75)
        self.assertEqual(d["identifiability"], "IDENTIFIABLE")


class TestGraphConfidenceService(unittest.TestCase):
    """Test GraphConfidenceService."""

    def setUp(self):
        self.service = GraphConfidenceService()

    def test_compute_causal_effect_bounds(self):
        """Should compute bounds based on confidence."""
        edge_conf = {
            ("X", "Y"): EdgeConfidence(
                source="X",
                target="Y",
                confidence=0.8,
                warrant_component=0.8,
                grounding_component=0.8,
                rank_component=0.8,
                supporting_belief_ids=["b1"],
                identifiability=IdentifiabilityStatus.IDENTIFIABLE
            )
        }

        bounds = self.service.compute_causal_effect_bounds(
            "X", "Y", edge_conf,
            base_effect_size=0.5,
            max_effect_size=1.0
        )

        self.assertLess(bounds.lower_bound, bounds.upper_bound)
        self.assertEqual(bounds.identifiability, IdentifiabilityStatus.IDENTIFIABLE)

    def test_missing_edge_returns_unknown(self):
        """Missing edge should return unknown identifiability."""
        bounds = self.service.compute_causal_effect_bounds(
            "X", "Y", {},
            base_effect_size=0.5
        )

        self.assertEqual(bounds.identifiability, IdentifiabilityStatus.UNKNOWN)
        self.assertEqual(bounds.confidence, 0.0)


class TestStructureUncertainty(unittest.TestCase):
    """Test StructureUncertainty dataclass."""

    def test_to_dict(self):
        """Should serialize correctly."""
        su = StructureUncertainty(
            overall_confidence=0.8,
            edge_confidences={("X", "Y"): 0.9},
            missing_edges=[],
            uncertain_edges=[("A", "B")],
            structure_entropy=0.3
        )
        d = su.to_dict()
        self.assertIn("X->Y", d["edge_confidences"])


# ============================================================
# INVARIANT TESTS
# ============================================================

class TestInvariants(unittest.TestCase):
    """Test formal invariants (INV-1 through INV-5)."""

    def test_inv1_consistency_detected(self):
        """INV-1: Should detect when both rebutter and rebuttee warranted."""
        service = WarrantService()

        mock_web = MagicMock()
        mock_web.beliefs = {"b1": MagicMock(), "r1": MagicMock()}
        mock_web.constraints = MagicMock()
        mock_web.constraints.values.return_value = []

        # Both observational (so both warranted)
        mock_web.beliefs["b1"].level.value = "OBSERVATIONAL"
        mock_web.beliefs["r1"].level.value = "OBSERVATIONAL"

        ranks = {
            "b1": RankPair(rank=0, neg_rank=5),
            "r1": RankPair(rank=0, neg_rank=5)
        }

        # r1 rebuts b1
        defeat_rel = create_defeat_relation("r1", "b1", "REBUTTING")

        result = service.compute_warrant(
            mock_web, ranks, [defeat_rel],
            observational_beliefs={"b1", "r1"}
        )

        # With proper defeat logic, b1 should be defeated, not both warranted
        # This is the INV-1 check - both shouldn't be warranted
        both_warranted = "b1" in result.warranted and "r1" in result.warranted
        self.assertFalse(both_warranted, "INV-1 violation: both rebutter and rebuttee warranted")

    def test_inv5_bridge_coherence(self):
        """INV-5: Confident edge should have warranted support."""
        service = GraphConfidenceService()

        edge_confidences = {
            ("X", "Y"): EdgeConfidence(
                source="X",
                target="Y",
                confidence=0.8,  # Above threshold
                warrant_component=0.0,  # No warrant!
                grounding_component=0.8,
                rank_component=0.8,
                supporting_belief_ids=["b1"],
                identifiability=IdentifiabilityStatus.IDENTIFIABLE
            )
        }

        violations = service._check_bridge_coherence(
            edge_confidences,
            warranted_beliefs=set()  # No warranted beliefs
        )

        self.assertGreater(len(violations), 0)
        self.assertIn("INV-5", violations[0])


if __name__ == '__main__':
    unittest.main()
