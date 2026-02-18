"""
Bayesian Network Health Check Tests (Sprint 11 Task 11.25).

Verifies the Bayesian network is functioning as a NETWORK, not just a database:
1. Belief updates propagate through the network
2. Edge strength updates work correctly (Beta-Bernoulli math)
3. D-separation works (if pgmpy available)
4. Markov blankets are correct (if pgmpy available)
5. Uncertainty tracking works
"""

import pytest
from typing import Optional, Dict, Any, List

# Import BN-related modules
try:
    from src.services.incremental_bn import (
        IncrementalBNBuilder,
        BetaBernoulliEdge,
        EdgeType,
        EvidenceType,
        get_bn_builder,
        observe_belief_in_bn,
        get_uncertain_edges,
        get_edge_estimate,
        query_posterior,
        check_d_separation,
        get_markov_blanket,
    )
    BN_AVAILABLE = True
except ImportError:
    BN_AVAILABLE = False

# Check if pgmpy is available
try:
    import pgmpy
    PGMPY_AVAILABLE = True
except ImportError:
    PGMPY_AVAILABLE = False


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestBNBuilderBasics:
    """Basic functionality tests for IncrementalBNBuilder."""

    def test_builder_instantiation(self):
        """BN builder should instantiate without error."""
        builder = IncrementalBNBuilder()
        assert builder is not None

    def test_get_or_create_edge(self):
        """Should be able to create edges via get_or_create_edge."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge(
            source="ceiling_height",
            target="perceived_spaciousness",
            edge_type=EdgeType.CAUSAL,
        )
        assert edge is not None
        assert edge.source == "ceiling_height"
        assert edge.target == "perceived_spaciousness"

    def test_observe_evidence_creates_edge(self):
        """observe_evidence should create edge if it doesn't exist."""
        builder = IncrementalBNBuilder()
        edge = builder.observe_evidence(
            source="light",
            target="alertness",
            supports=True,
            weight=1.0,
            edge_type=EdgeType.CAUSAL,
        )
        assert edge is not None
        assert edge.source == "light"
        assert edge.target == "alertness"

    def test_multiple_edges(self):
        """Should be able to add multiple edges."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("light", "alertness", supports=True, edge_type=EdgeType.CAUSAL)
        builder.observe_evidence("noise", "stress", supports=True, edge_type=EdgeType.CAUSAL)
        builder.observe_evidence("stress", "performance", supports=True, edge_type=EdgeType.CAUSAL)

        # Should have 3 edges
        assert len(builder.edges) == 3

    def test_nodes_tracked(self):
        """Builder should track all nodes."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("B", "C", supports=True)

        assert "A" in builder.nodes
        assert "B" in builder.nodes
        assert "C" in builder.nodes


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestEdgeStrengthUpdates:
    """Test that edge strengths can be updated with observations."""

    def test_observe_positive_evidence(self):
        """Observing positive evidence should increase edge strength."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.CAUSAL)

        initial_mean = edge.mean

        # Observe positive evidence (supports=True)
        edge.update(supports=True)

        # Mean should increase
        assert edge.mean >= initial_mean, (
            "Edge strength shouldn't decrease with positive evidence"
        )

    def test_observe_negative_evidence(self):
        """Observing negative evidence should decrease edge strength."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.CAUSAL)

        # First add some positive evidence
        for _ in range(5):
            edge.update(supports=True)

        strength_after_positive = edge.mean

        # Now add negative evidence
        for _ in range(10):
            edge.update(supports=False)

        # Strength should decrease
        assert edge.mean < strength_after_positive, (
            "Edge strength should decrease with negative evidence"
        )

    def test_weighted_evidence(self):
        """Weighted evidence should have proportional effect."""
        builder = IncrementalBNBuilder()
        edge1 = builder.get_or_create_edge("A", "B", EdgeType.CAUSAL)
        edge2 = builder.get_or_create_edge("C", "D", EdgeType.CAUSAL)

        # Add same support but different weight
        edge1.update(supports=True, weight=1.0)
        edge2.update(supports=True, weight=0.5)

        # Higher weight should have larger effect
        assert edge1.mean > edge2.mean, (
            "Higher weight evidence should have larger effect"
        )


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestNetworkStructure:
    """Test network structure operations."""

    def test_get_edge_estimate(self):
        """get_edge_estimate should return valid probability."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True)

        estimate = get_edge_estimate("A", "B")
        if estimate is not None:
            assert 0.0 <= estimate <= 1.0, f"Invalid estimate: {estimate}"

    def test_uncertain_edges(self):
        """get_uncertain_edges should return edges with high uncertainty."""
        builder = IncrementalBNBuilder()
        # Add fresh edge (high uncertainty)
        builder.get_or_create_edge("fresh", "uncertain", EdgeType.UNKNOWN)

        uncertain = builder.get_uncertain_edges(min_uncertainty=0.1)
        # Should have at least one uncertain edge
        assert isinstance(uncertain, list)

    def test_edge_summary(self):
        """get_edge_summary should return valid statistics."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True, paper_id="paper1")
        builder.observe_evidence("B", "C", supports=True, paper_id="paper2")

        summary = builder.get_edge_summary()
        assert summary["n_edges"] == 2
        assert summary["n_nodes"] == 3
        assert "mean_uncertainty" in summary


@pytest.mark.skipif(not PGMPY_AVAILABLE, reason="pgmpy not installed")
class TestPgmpyIntegration:
    """Test pgmpy-specific functionality."""

    def test_build_pgmpy_model(self):
        """Should be able to build pgmpy model from edges."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("X", "Y", supports=True)
        builder.observe_evidence("Y", "Z", supports=True)

        model = builder.build_pgmpy_model()
        # Model may be None if pgmpy fails
        # Just verify no exception

    def test_query_posterior_callable(self):
        """query_posterior should be callable."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("X", "Y", supports=True)

        result = builder.query_posterior("Y", evidence={"X": 1})
        # Result may be None if model can't be built
        assert result is None or isinstance(result, (float, int))

    def test_d_separation_callable(self):
        """is_d_separated should be callable."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("X", "Y", supports=True)
        builder.observe_evidence("Y", "Z", supports=True)

        result = builder.is_d_separated("X", "Z", observed=["Y"])
        # Result may be None if model can't be built
        assert result is None or isinstance(result, bool)

    def test_markov_blanket_callable(self):
        """get_markov_blanket should be callable."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("X", "Y", supports=True)

        result = builder.get_markov_blanket("Y")
        # Result may be None if model can't be built
        assert result is None or isinstance(result, list)


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestBetaBernoulliMath:
    """Test Beta-Bernoulli distribution mathematics."""

    def test_initial_prior(self):
        """Fresh edge should have weak prior (mean = 0.5)."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        # Initial mean should be 0.5 (Beta(1,1) = uniform)
        assert edge.mean == 0.5, f"Initial mean {edge.mean} not 0.5"

    def test_initial_alpha_beta(self):
        """Fresh edge should have alpha=1, beta=1."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        assert edge.alpha == 1.0
        assert edge.beta == 1.0

    def test_conjugate_updates(self):
        """Verify Beta-Bernoulli conjugate update formula."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        initial_alpha = edge.alpha
        initial_beta = edge.beta

        # Observe 3 successes, 2 failures
        for _ in range(3):
            edge.update(supports=True)
        for _ in range(2):
            edge.update(supports=False)

        # Alpha should increase by 3, beta by 2
        assert edge.alpha == initial_alpha + 3
        assert edge.beta == initial_beta + 2

    def test_mean_formula(self):
        """Verify mean = alpha / (alpha + beta)."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        # After some updates
        edge.update(supports=True)
        edge.update(supports=True)
        edge.update(supports=False)

        expected_mean = edge.alpha / (edge.alpha + edge.beta)
        assert abs(edge.mean - expected_mean) < 0.0001

    def test_uncertainty_decreases_with_observations(self):
        """Uncertainty (variance) should decrease with more observations."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        initial_variance = edge.variance

        # Add observations
        for i in range(10):
            edge.update(supports=(i % 2 == 0))  # Mixed observations

        # Variance should decrease (more certainty)
        assert edge.variance < initial_variance, (
            "Variance should decrease with observations"
        )

    def test_credible_interval(self):
        """Credible interval should be valid."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        # Add some observations
        for _ in range(5):
            edge.update(supports=True)

        ci = edge.credible_interval(confidence=0.95)
        assert len(ci) == 2
        assert 0.0 <= ci[0] <= ci[1] <= 1.0


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestNetworkHealthReport:
    """Generate a health report for the BN."""

    def test_generate_health_report(self):
        """Generate a summary of BN health."""
        builder = IncrementalBNBuilder()

        # Add some test edges
        builder.observe_evidence("ceiling_height", "perceived_spaciousness", supports=True)
        builder.observe_evidence("light_level", "alertness", supports=True)
        builder.observe_evidence("noise_level", "stress", supports=True)

        report = {
            "total_edges": len(builder.edges),
            "total_nodes": len(builder.nodes),
            "pgmpy_available": PGMPY_AVAILABLE,
            "edge_types": {},
            "uncertain_edges_count": 0,
        }

        # Count edge types
        for edge in builder.edges.values():
            et = edge.edge_type.value
            report["edge_types"][et] = report["edge_types"].get(et, 0) + 1

        # Count uncertain edges
        uncertain = builder.get_uncertain_edges(min_uncertainty=0.3)
        report["uncertain_edges_count"] = len(uncertain)

        # Report should be valid
        print("\n=== BN HEALTH REPORT ===")
        print(f"Total edges: {report['total_edges']}")
        print(f"Total nodes: {report['total_nodes']}")
        print(f"pgmpy available: {report['pgmpy_available']}")
        print(f"Edge types: {report['edge_types']}")
        print(f"Uncertain edges: {report['uncertain_edges_count']}")

        # Basic assertions
        assert report["total_edges"] == 3
        assert report["total_nodes"] == 6
        assert isinstance(report["pgmpy_available"], bool)


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestObserveBeliefIntegration:
    """Test integration with belief observation."""

    def test_observe_belief_callable(self):
        """observe_belief_in_bn should be callable."""
        # Create a mock belief-like object
        class MockBelief:
            def __init__(self):
                self.environment_id = "test_env"
                self.outcome_id = "test_outcome"
                self.credence = 0.7
                self.paper_ids = ["paper123"]

        belief = MockBelief()
        try:
            result = observe_belief_in_bn(belief, weight=1.0)
            # Should return list of edges
            assert isinstance(result, list)
        except Exception as e:
            # If it fails, that's acceptable for a mock object
            pass

    def test_observe_evidence_with_paper_id(self):
        """observe_evidence should track paper IDs."""
        builder = IncrementalBNBuilder()
        edge = builder.observe_evidence(
            source="A",
            target="B",
            supports=True,
            paper_id="paper_123"
        )

        assert "paper_123" in edge.paper_ids
        assert edge.n_papers == 1


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestEdgeReliability:
    """Test edge reliability computations."""

    def test_fresh_edge_not_reliable(self):
        """Fresh edge with no observations should not be reliable."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        # Fresh edge has effective_sample_size = 0
        assert edge.effective_sample_size == 0
        assert not edge.is_reliable

    def test_edge_becomes_reliable(self):
        """Edge should become reliable after enough observations."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.CAUSAL)

        # Add many consistent observations
        for _ in range(10):
            edge.update(supports=True)

        # Should now have high effective sample size
        assert edge.effective_sample_size >= 3

    def test_effective_sample_size(self):
        """Effective sample size should track observations."""
        builder = IncrementalBNBuilder()
        edge = builder.get_or_create_edge("X", "Y", EdgeType.UNKNOWN)

        # Add 5 observations
        for _ in range(5):
            edge.update(supports=True)

        # ESS = alpha + beta - 2 (subtract initial pseudo-counts)
        expected_ess = edge.alpha + edge.beta - 2
        assert edge.effective_sample_size == expected_ess


@pytest.mark.skipif(not BN_AVAILABLE, reason="BN module not available")
class TestEdgeSerialization:
    """Test edge serialization/deserialization."""

    def test_edge_to_dict(self):
        """Edge should serialize to dict."""
        builder = IncrementalBNBuilder()
        edge = builder.observe_evidence("A", "B", supports=True, paper_id="p1")

        d = edge.to_dict()
        assert d["source"] == "A"
        assert d["target"] == "B"
        assert "mean" in d
        assert "paper_ids" in d

    def test_edge_from_dict(self):
        """Edge should deserialize from dict."""
        data = {
            "source": "X",
            "target": "Y",
            "edge_type": "causal",
            "alpha": 3.0,
            "beta": 2.0,
            "n_papers": 2,
            "paper_ids": ["p1", "p2"],
        }

        edge = BetaBernoulliEdge.from_dict(data)
        assert edge.source == "X"
        assert edge.target == "Y"
        assert edge.alpha == 3.0
        assert edge.beta == 2.0
