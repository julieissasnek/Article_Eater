"""
Tests for Incremental BN Learning (TD-E)

Sprint: TD-E
Created: February 8, 2026
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict

from src.services.incremental_bn import (
    BetaBernoulliEdge,
    EdgeType,
    EvidenceType,
    EdgeGap,
    IncrementalBNBuilder,
    ActiveLearningScheduler,
    get_bn_builder,
    observe_belief_in_bn,
    get_uncertain_edges,
    get_edge_estimate,
    query_posterior,
    check_d_separation,
    get_markov_blanket,
)


# =============================================================================
# BETA-BERNOULLI EDGE TESTS
# =============================================================================

class TestBetaBernoulliEdge:
    """Test BetaBernoulliEdge class."""

    def test_edge_creation(self):
        """Can create edge with default priors."""
        edge = BetaBernoulliEdge(source="nature", target="stress")
        assert edge.source == "nature"
        assert edge.target == "stress"
        assert edge.alpha == 1.0
        assert edge.beta == 1.0

    def test_prior_mean(self):
        """Default prior has mean 0.5 (uniform)."""
        edge = BetaBernoulliEdge(source="A", target="B")
        assert edge.mean == 0.5

    def test_update_supporting(self):
        """Supporting evidence increases alpha."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update(supports=True, weight=1.0)

        assert edge.alpha == 2.0
        assert edge.beta == 1.0
        assert edge.mean > 0.5  # Shifted toward 1

    def test_update_contradicting(self):
        """Contradicting evidence increases beta."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update(supports=False, weight=1.0)

        assert edge.alpha == 1.0
        assert edge.beta == 2.0
        assert edge.mean < 0.5  # Shifted toward 0

    def test_weighted_update(self):
        """Weighted updates affect parameters proportionally."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update(supports=True, weight=0.5)

        assert edge.alpha == 1.5
        assert edge.beta == 1.0

    def test_batch_update(self):
        """Batch update works correctly."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update_batch(n_supporting=5, n_contradicting=2, avg_weight=1.0)

        assert edge.alpha == 6.0  # 1 + 5
        assert edge.beta == 3.0   # 1 + 2
        assert edge.n_papers == 7

    def test_credible_interval(self):
        """Credible interval is computed."""
        edge = BetaBernoulliEdge(source="A", target="B")
        ci = edge.credible_interval(0.95)

        assert len(ci) == 2
        assert ci[0] < ci[1]
        assert 0 <= ci[0] <= 1
        assert 0 <= ci[1] <= 1

    def test_credible_interval_narrows_with_data(self):
        """More data → narrower credible interval."""
        edge_sparse = BetaBernoulliEdge(source="A", target="B")
        edge_dense = BetaBernoulliEdge(source="A", target="B")

        # Add lots of data to dense edge
        edge_dense.update_batch(n_supporting=20, n_contradicting=10)

        ci_sparse = edge_sparse.credible_interval()
        ci_dense = edge_dense.credible_interval()

        width_sparse = ci_sparse[1] - ci_sparse[0]
        width_dense = ci_dense[1] - ci_dense[0]

        assert width_dense < width_sparse

    def test_effective_sample_size(self):
        """ESS increases with observations."""
        edge = BetaBernoulliEdge(source="A", target="B")
        assert edge.effective_sample_size == 0  # Prior only

        edge.update_batch(n_supporting=5, n_contradicting=5)
        assert edge.effective_sample_size == 10

    def test_uncertainty_decreases_with_data(self):
        """Uncertainty decreases with more data."""
        edge_sparse = BetaBernoulliEdge(source="A", target="B")
        edge_dense = BetaBernoulliEdge(source="A", target="B")

        edge_dense.update_batch(n_supporting=10, n_contradicting=5)

        assert edge_dense.uncertainty < edge_sparse.uncertainty

    def test_is_reliable(self):
        """Reliability requires sufficient data."""
        edge = BetaBernoulliEdge(source="A", target="B")
        assert not edge.is_reliable  # Not enough data

        edge.update_batch(n_supporting=10, n_contradicting=2)
        assert edge.is_reliable  # Now reliable

    def test_paper_tracking(self):
        """Paper IDs are tracked."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update(supports=True, paper_id="paper1")
        edge.update(supports=True, paper_id="paper2")
        edge.update(supports=False, paper_id="paper1")  # Duplicate

        assert "paper1" in edge.paper_ids
        assert "paper2" in edge.paper_ids
        assert len(edge.paper_ids) == 2  # No duplicates

    def test_to_dict(self):
        """Edge serializes to dict."""
        edge = BetaBernoulliEdge(
            source="nature",
            target="stress",
            edge_type=EdgeType.CAUSAL
        )
        edge.update(supports=True, paper_id="paper1")

        d = edge.to_dict()

        assert d['source'] == "nature"
        assert d['target'] == "stress"
        assert d['edge_type'] == "causal"
        assert d['mean'] > 0.5
        assert 'credible_interval_95' in d

    def test_from_dict(self):
        """Edge deserializes from dict."""
        original = BetaBernoulliEdge(source="A", target="B")
        original.update_batch(n_supporting=5, n_contradicting=2)

        d = original.to_dict()
        restored = BetaBernoulliEdge.from_dict(d)

        assert restored.source == original.source
        assert restored.alpha == original.alpha
        assert restored.beta == original.beta


# =============================================================================
# EDGE GAP TESTS
# =============================================================================

class TestEdgeGap:
    """Test EdgeGap dataclass."""

    def test_gap_creation(self):
        """Can create edge gap."""
        gap = EdgeGap(
            source="nature",
            target="attention",
            uncertainty=0.7,
            relevance=0.8
        )
        assert gap.source == "nature"
        assert gap.priority == 0.7 * 0.8  # uncertainty * relevance

    def test_priority_calculation(self):
        """Priority is uncertainty * relevance."""
        gap = EdgeGap(source="A", target="B", uncertainty=0.5, relevance=0.6)
        assert gap.priority == pytest.approx(0.3)


# =============================================================================
# INCREMENTAL BN BUILDER TESTS
# =============================================================================

class TestIncrementalBNBuilder:
    """Test IncrementalBNBuilder class."""

    def test_builder_creation(self):
        """Can create builder."""
        builder = IncrementalBNBuilder()
        assert len(builder.edges) == 0
        assert len(builder.nodes) == 0

    def test_get_or_create_edge(self):
        """get_or_create_edge creates new edges."""
        builder = IncrementalBNBuilder()

        edge = builder.get_or_create_edge("A", "B")
        assert edge.source == "A"
        assert edge.target == "B"
        assert "A" in builder.nodes
        assert "B" in builder.nodes

        # Same edge returned on second call
        edge2 = builder.get_or_create_edge("A", "B")
        assert edge is edge2

    def test_observe_evidence(self):
        """observe_evidence updates edge."""
        builder = IncrementalBNBuilder()

        edge = builder.observe_evidence(
            source="nature",
            target="stress",
            supports=True,
            weight=1.0,
            paper_id="paper1"
        )

        assert edge.mean > 0.5
        assert "paper1" in edge.paper_ids

    def test_multiple_observations(self):
        """Multiple observations accumulate."""
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("A", "B", supports=False)

        edge = builder.get_edge("A", "B")
        assert edge.n_papers == 3
        assert edge.alpha == 3.0  # 1 + 2
        assert edge.beta == 2.0   # 1 + 1

    def test_get_uncertain_edges(self):
        """get_uncertain_edges returns high-uncertainty edges."""
        builder = IncrementalBNBuilder()

        # Create sparse edge (high uncertainty)
        builder.observe_evidence("A", "B", supports=True)

        # Create dense edge (low uncertainty)
        for _ in range(20):
            builder.observe_evidence("C", "D", supports=True)

        uncertain = builder.get_uncertain_edges(min_uncertainty=0.3)

        # Sparse edge should be in uncertain list
        sources = [e.source for e in uncertain]
        assert "A" in sources

    def test_get_unreliable_edges(self):
        """get_unreliable_edges returns edges needing more data."""
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", supports=True)  # Unreliable
        for _ in range(10):
            builder.observe_evidence("C", "D", supports=True)  # Reliable

        unreliable = builder.get_unreliable_edges()
        sources = [e.source for e in unreliable]

        assert "A" in sources

    def test_identify_gaps(self):
        """identify_gaps returns prioritized gaps."""
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("C", "D", supports=True)

        gaps = builder.identify_gaps(max_gaps=5)

        assert len(gaps) <= 5
        assert all(isinstance(g, EdgeGap) for g in gaps)

    def test_get_bn_parameters(self):
        """get_bn_parameters exports edge means."""
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("C", "D", supports=False)

        params = builder.get_bn_parameters()

        assert ("A", "B") in params
        assert ("C", "D") in params
        assert params[("A", "B")] > 0.5
        assert params[("C", "D")] < 0.5

    def test_get_edge_summary(self):
        """get_edge_summary returns statistics."""
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", supports=True, paper_id="p1")
        builder.observe_evidence("C", "D", supports=True, paper_id="p2")

        summary = builder.get_edge_summary()

        assert summary['n_edges'] == 2
        assert summary['n_nodes'] == 4
        assert summary['total_papers'] == 2

    def test_persistence(self):
        """State persists to file and loads back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bn_state.json"

            # Create and save
            builder1 = IncrementalBNBuilder(persistence_path=path)
            builder1.observe_evidence("nature", "stress", supports=True, paper_id="p1")
            builder1.observe_evidence("nature", "stress", supports=True, paper_id="p2")
            builder1.save_state()

            # Load in new builder
            builder2 = IncrementalBNBuilder(persistence_path=path)

            edge = builder2.get_edge("nature", "stress")
            assert edge is not None
            assert edge.n_papers == 2
            assert edge.alpha == 3.0  # 1 + 2

    def test_to_dict(self):
        """to_dict exports full state."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True)

        state = builder.to_dict()

        assert 'edges' in state
        assert 'nodes' in state
        assert 'summary' in state


# =============================================================================
# ACTIVE LEARNING SCHEDULER TESTS
# =============================================================================

class TestActiveLearningScheduler:
    """Test ActiveLearningScheduler class."""

    def test_scheduler_creation(self):
        """Can create scheduler."""
        builder = IncrementalBNBuilder()
        scheduler = ActiveLearningScheduler(builder)
        assert scheduler.bn_builder is builder

    def test_prioritize_edges(self):
        """prioritize_edges returns gaps."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("C", "D", supports=True)

        scheduler = ActiveLearningScheduler(builder)
        gaps = scheduler.prioritize_edges(max_results=5)

        assert len(gaps) <= 5
        assert all(isinstance(g, EdgeGap) for g in gaps)

    def test_search_history_affects_priority(self):
        """Previously searched edges get lower priority."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True)
        builder.observe_evidence("C", "D", supports=True)

        scheduler = ActiveLearningScheduler(builder)

        # Get initial priorities
        gaps1 = scheduler.prioritize_edges()
        priorities1 = {(g.source, g.target): g.priority for g in gaps1}

        # Record search for one edge
        scheduler.record_search("A", "B")

        # Get new priorities
        gaps2 = scheduler.prioritize_edges()
        priorities2 = {(g.source, g.target): g.priority for g in gaps2}

        # A→B should have lower priority now
        assert priorities2[("A", "B")] < priorities1[("A", "B")]

    def test_get_search_queries(self):
        """get_search_queries returns query strings."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("nature", "stress", supports=True)

        scheduler = ActiveLearningScheduler(builder)
        queries = scheduler.get_search_queries(max_queries=5)

        assert len(queries) <= 5
        assert all(isinstance(q, str) for q in queries)


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_bn_builder_singleton(self):
        """get_bn_builder returns singleton."""
        # Reset singleton for test
        import src.services.incremental_bn as module
        module._bn_builder_instance = None

        b1 = get_bn_builder()
        b2 = get_bn_builder()
        assert b1 is b2

    def test_get_edge_estimate(self):
        """get_edge_estimate returns edge mean."""
        import src.services.incremental_bn as module
        module._bn_builder_instance = None

        builder = get_bn_builder()
        builder.observe_evidence("test_a", "test_b", supports=True)

        estimate = get_edge_estimate("test_a", "test_b")
        assert estimate is not None
        assert estimate > 0.5

    def test_get_edge_estimate_missing(self):
        """get_edge_estimate returns None for missing edge."""
        import src.services.incremental_bn as module
        module._bn_builder_instance = None

        estimate = get_edge_estimate("nonexistent", "edge")
        assert estimate is None

    def test_pgmpy_wrappers_graceful_without_dependency(self):
        """pgmpy wrappers should degrade gracefully when pgmpy is unavailable."""
        import src.services.incremental_bn as module
        module._bn_builder_instance = None

        builder = get_bn_builder()
        builder.observe_evidence("A", "B", supports=True)

        # In this runtime pgmpy may be absent; wrappers must not crash.
        posterior = query_posterior("B", {"A": 1})
        dsep = check_d_separation("A", "B", [])
        blanket = get_markov_blanket("B")

        if module._PgmpyBN is None:
            assert posterior is None
            assert dsep is None
            assert blanket is None

    def test_get_edge_estimate_pgmpy_fallback_no_crash(self):
        """Fallback inference path should return None or float, never raise."""
        import src.services.incremental_bn as module
        module._bn_builder_instance = None

        builder = get_bn_builder()
        builder.observe_evidence("X", "Y", supports=True)

        estimate = get_edge_estimate("A_missing", "B_missing", use_pgmpy_fallback=True)
        assert estimate is None or isinstance(estimate, float)


# =============================================================================
# BAYESIAN UPDATE PROPERTY TESTS
# =============================================================================

class TestBayesianUpdateProperties:
    """Test mathematical properties of Bayesian updates."""

    def test_mean_bounded(self):
        """Mean is always between 0 and 1."""
        edge = BetaBernoulliEdge(source="A", target="B")

        for _ in range(100):
            edge.update(supports=True)

        assert 0 <= edge.mean <= 1

        for _ in range(200):
            edge.update(supports=False)

        assert 0 <= edge.mean <= 1

    def test_convergence_with_strong_evidence(self):
        """Mean converges to observed proportion with enough data."""
        edge = BetaBernoulliEdge(source="A", target="B")

        # Observe 70% support
        for _ in range(70):
            edge.update(supports=True)
        for _ in range(30):
            edge.update(supports=False)

        # Mean should be close to 0.7
        assert abs(edge.mean - 0.7) < 0.05

    def test_variance_decreases_with_data(self):
        """Variance decreases as more data is observed."""
        edge = BetaBernoulliEdge(source="A", target="B")
        initial_var = edge.variance

        for _ in range(20):
            edge.update(supports=True)

        assert edge.variance < initial_var

    def test_order_independence(self):
        """Order of updates doesn't affect final state."""
        edge1 = BetaBernoulliEdge(source="A", target="B")
        edge2 = BetaBernoulliEdge(source="A", target="B")

        # Order 1: supports first
        for _ in range(5):
            edge1.update(supports=True)
        for _ in range(3):
            edge1.update(supports=False)

        # Order 2: contradicts first
        for _ in range(3):
            edge2.update(supports=False)
        for _ in range(5):
            edge2.update(supports=True)

        assert edge1.mean == edge2.mean
        assert edge1.alpha == edge2.alpha
        assert edge1.beta == edge2.beta


# =============================================================================
# INTEGRATION READINESS TESTS
# =============================================================================

class TestIntegrationReadiness:
    """Test that module is ready for integration."""

    def test_edge_has_required_fields(self):
        """Edge has all fields needed for BN export."""
        edge = BetaBernoulliEdge(source="A", target="B")
        edge.update(supports=True)

        assert hasattr(edge, 'mean')
        assert hasattr(edge, 'credible_interval')
        assert hasattr(edge, 'uncertainty')
        assert hasattr(edge, 'is_reliable')

    def test_builder_works_with_empty_inputs(self):
        """Builder handles edge cases gracefully."""
        builder = IncrementalBNBuilder()

        # Empty state operations
        assert builder.get_bn_parameters() == {}
        assert builder.get_uncertain_edges() == []
        assert builder.get_unreliable_edges() == []

        summary = builder.get_edge_summary()
        assert summary['n_edges'] == 0

    def test_json_serialization(self):
        """Full state is JSON serializable."""
        builder = IncrementalBNBuilder()
        builder.observe_evidence("A", "B", supports=True, paper_id="p1")

        state = builder.to_dict()
        json_str = json.dumps(state)

        assert 'edges' in json_str
        assert 'A' in json_str
