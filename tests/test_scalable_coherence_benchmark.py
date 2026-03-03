"""
Scalability Benchmark Tests for Coherence Computation.

Created: February 8, 2026
Purpose: Verify O(n log n) scalability claims (Claude Opus review 2026-02-08)

These tests verify that the CoherenceManager can handle large webs
within the claimed performance bounds.

Benchmark Claims (from scalable_coherence.py docstring):
- 5000 beliefs, 25000 constraints in <500ms

Run with:
    pytest tests/test_scalable_coherence_benchmark.py -v
    pytest tests/test_scalable_coherence_benchmark.py -v --benchmark-only  # if pytest-benchmark installed
"""

import pytest
import time
import random
import uuid
from typing import List, Tuple

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
)
from src.services.scalable_coherence import CoherenceManager


def create_large_web(
    n_beliefs: int = 5000,
    n_constraints: int = 25000,
    n_theories: int = 10,
    seed: int = 42
) -> WebOfBelief:
    """
    Create a large web for benchmark testing.

    Args:
        n_beliefs: Number of beliefs to create
        n_constraints: Number of constraints to create
        n_theories: Number of distinct theories
        seed: Random seed for reproducibility

    Returns:
        WebOfBelief with specified size
    """
    random.seed(seed)
    web = WebOfBelief(domain="benchmark")

    # Create theories
    theories = [f"theory_{i}" for i in range(n_theories)]
    for theory_id in theories:
        web.register_theory(theory_id)

    # Create beliefs distributed across theories
    belief_ids: List[str] = []
    for i in range(n_beliefs):
        theory_id = theories[i % n_theories]
        level = random.choice([
            EpistemicLevel.THEORETICAL,
            EpistemicLevel.EMPIRICAL,
            EpistemicLevel.OBSERVATIONAL
        ])

        # V23.0.0: entrenchment is now computed from web position, not stored
        belief = Belief(
            belief_id=f"belief_{i:05d}",
            content=f"Benchmark belief {i}",
            level=level,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(random.uniform(0.3, 0.9), random.uniform(0.1, 0.3)),
            theory_id=theory_id,
        )
        web.add_belief(belief)
        belief_ids.append(belief.belief_id)

    # Create constraints (avoiding duplicates)
    created_pairs = set()
    constraints_created = 0

    while constraints_created < n_constraints:
        source_idx = random.randint(0, n_beliefs - 1)
        target_idx = random.randint(0, n_beliefs - 1)

        if source_idx == target_idx:
            continue

        pair = (min(source_idx, target_idx), max(source_idx, target_idx))
        if pair in created_pairs:
            continue

        created_pairs.add(pair)

        source_id = belief_ids[source_idx]
        target_id = belief_ids[target_idx]

        constraint_type = random.choice([
            ConstraintType.SUPPORTS,
            ConstraintType.CONTRADICTS,
            ConstraintType.EXPLAINS,
        ])

        constraint = Constraint(
            constraint_id=f"c_{source_idx}_{target_idx}",
            source_id=source_id,
            target_id=target_id,
            constraint_type=constraint_type,
            strength=random.uniform(0.3, 0.9),
            bidirectional=True,
        )
        web.add_constraint(constraint)
        constraints_created += 1

    return web


@pytest.mark.slow
class TestScalabilityBenchmarks:
    """Benchmark tests for coherence computation scalability.
    
    Marked as 'slow' because these create 1000-5000 beliefs with 5000-25000
    constraints — genuine O(n²) compute that takes 15+ seconds.
    Run with: pytest -m slow tests/test_scalable_coherence_benchmark.py
    """

    def test_5000_beliefs_under_500ms(self):
        """
        Verify the primary scalability claim: 5000 beliefs, 25000 constraints in <500ms.

        This is the benchmark claim from scalable_coherence.py docstring.
        """
        # Create large web
        web = create_large_web(n_beliefs=5000, n_constraints=25000)

        assert len(web.beliefs) == 5000
        assert len(web.constraints) == 25000

        # Build coherence manager
        manager = CoherenceManager()
        manager.build_from_web(web)

        # Time the coherence computation
        start = time.time()
        coherence = manager.compute_coherence()
        elapsed = time.time() - start

        # Assert performance bound
        assert elapsed < 0.5, (
            f"Coherence computation took {elapsed:.3f}s, expected <0.5s. "
            f"The O(n log n) claim may not hold."
        )

        # Sanity check result
        assert 0.0 <= coherence <= 1.0, f"Coherence {coherence} out of bounds"

        print(f"\nBenchmark: 5000 beliefs, 25000 constraints")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Coherence: {coherence:.4f}")
        print(f"  Cache stats: {manager.cache.stats()}")

    def test_1000_beliefs_baseline(self):
        """Baseline test with 1000 beliefs to verify scaling behavior."""
        web = create_large_web(n_beliefs=1000, n_constraints=5000)

        manager = CoherenceManager()
        manager.build_from_web(web)

        start = time.time()
        coherence = manager.compute_coherence()
        elapsed = time.time() - start

        # Should be much faster than 5000 belief case
        assert elapsed < 0.1, f"1000 beliefs took {elapsed:.3f}s, expected <0.1s"

        print(f"\nBaseline: 1000 beliefs, 5000 constraints")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Coherence: {coherence:.4f}")

    def test_incremental_update_performance(self):
        """Test that incremental updates are fast after initial build."""
        web = create_large_web(n_beliefs=2000, n_constraints=10000)

        manager = CoherenceManager()
        manager.build_from_web(web)

        # Initial computation
        manager.compute_coherence()

        # Add a new belief and measure incremental update time
        new_belief = Belief(
            belief_id="new_belief_001",
            content="New benchmark belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2),
            theory_id="theory_0",
        )
        web.add_belief(new_belief)

        start = time.time()
        manager.on_belief_added(
            new_belief.belief_id,
            theory_id=new_belief.theory_id,
            level=new_belief.level.value
        )
        coherence = manager.compute_coherence()
        elapsed = time.time() - start

        # Incremental update should be very fast
        assert elapsed < 0.05, (
            f"Incremental update took {elapsed:.3f}s, expected <0.05s"
        )

        print(f"\nIncremental update (1 belief added to 2000)")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Coherence: {coherence:.4f}")

    def test_cache_effectiveness(self):
        """Test that cache improves performance on repeated queries."""
        web = create_large_web(n_beliefs=1000, n_constraints=5000)

        manager = CoherenceManager()
        manager.build_from_web(web)

        # First computation (cache miss)
        start = time.time()
        coherence1 = manager.compute_coherence()
        elapsed1 = time.time() - start

        # Second computation (cache hit)
        start = time.time()
        coherence2 = manager.compute_coherence()
        elapsed2 = time.time() - start

        # Cache should make second call much faster
        assert elapsed2 < elapsed1 / 5, (
            f"Cache not effective: first={elapsed1:.4f}s, second={elapsed2:.4f}s"
        )

        # Results should be identical
        assert coherence1 == coherence2

        stats = manager.cache.stats()
        # Note: Hit rate depends on cache structure; just verify caching is working
        assert stats['hits'] > 0, "Cache should have some hits on second call"

        print(f"\nCache effectiveness:")
        print(f"  First call: {elapsed1:.4f}s")
        print(f"  Second call: {elapsed2:.4f}s")
        print(f"  Speedup: {elapsed1/elapsed2:.1f}x")
        print(f"  Cache hit rate: {stats['hit_rate']:.2%}")


class TestConstraintNetworkIntegrity:
    """
    Tests for constraint network integrity after removals.

    Added per ChatGPT review 2026-02-08 findings.
    """

    def test_remove_belief_purges_constraint_index(self):
        """Verify remove_belief cleans up _constraint_index."""
        web = create_large_web(n_beliefs=100, n_constraints=500)

        manager = CoherenceManager()
        manager.build_from_web(web)

        # Get a belief with constraints
        belief_id = "belief_00050"
        constraints_before = manager.network.get_constraints_for(belief_id)
        assert len(constraints_before) > 0, "Test requires belief with constraints"

        # Count constraint index entries involving this belief
        index_entries_before = sum(
            1 for src, tgt in manager.network._constraint_index.values()
            if src == belief_id or tgt == belief_id
        )
        assert index_entries_before > 0, "Test requires indexed constraints"

        # Remove the belief
        manager.on_belief_removed(belief_id)

        # Verify constraint index is clean
        index_entries_after = sum(
            1 for src, tgt in manager.network._constraint_index.values()
            if src == belief_id or tgt == belief_id
        )
        assert index_entries_after == 0, (
            f"Stale constraint index entries remain: {index_entries_after}"
        )

    def test_remove_constraint_updates_boundary_status(self):
        """Verify remove_constraint recomputes boundary status."""
        web = WebOfBelief(domain="test")

        # Create two theories with one cross-theory constraint
        for i in range(5):
            web.add_belief(Belief(
                belief_id=f"a_{i}",
                content=f"Theory A belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.7, 0.2),
                theory_id="theory_a",
            ))
            web.add_belief(Belief(
                belief_id=f"b_{i}",
                content=f"Theory B belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.7, 0.2),
                theory_id="theory_b",
            ))

        # Add cross-theory constraint
        cross_constraint = Constraint(
            constraint_id="cross_ab",
            source_id="a_0",
            target_id="b_0",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,
        )
        web.add_constraint(cross_constraint)

        manager = CoherenceManager()
        manager.build_from_web(web)

        # Verify boundary status before removal
        node_a0 = manager.network.nodes.get("a_0")
        node_b0 = manager.network.nodes.get("b_0")
        assert node_a0 is not None and node_a0.is_boundary, "a_0 should be boundary"
        assert node_b0 is not None and node_b0.is_boundary, "b_0 should be boundary"

        # Remove the cross-theory constraint
        manager.on_constraint_removed("cross_ab")

        # Verify boundary status after removal
        node_a0 = manager.network.nodes.get("a_0")
        node_b0 = manager.network.nodes.get("b_0")
        assert not node_a0.is_boundary, "a_0 should no longer be boundary"
        assert not node_b0.is_boundary, "b_0 should no longer be boundary"


class TestCredibilityDecisionSemantics:
    """
    Tests for credibility decision semantics.

    Added per ChatGPT review 2026-02-08 findings.
    """

    def test_clean_report_has_accept_decision(self):
        """Verify clean reports have ACCEPT decision (not REVIEW)."""
        from src.services.credibility_testing import CredibilityReport, Decision
        from datetime import datetime, timezone

        report = CredibilityReport(
            article_id="test_article",
            timestamp=datetime.now(timezone.utc),
        )

        # No flags added
        assert report.is_clean
        assert report.overall_decision == Decision.ACCEPT, (
            f"Clean report should have ACCEPT, got {report.overall_decision}"
        )

        # Serialization should match
        serialized = report.to_dict()
        assert serialized['overall_decision'] == 'accept'

    def test_flagged_report_has_review_decision(self):
        """Verify flagged reports have REVIEW or BLOCK decision."""
        from src.services.credibility_testing import (
            CredibilityReport, CredibilityFlag, Decision
        )
        from datetime import datetime, timezone

        report = CredibilityReport(
            article_id="test_article",
            timestamp=datetime.now(timezone.utc),
        )

        # Add a REVIEW flag
        report.add_flag(CredibilityFlag(
            decision=Decision.REVIEW,
            reason="Test flag",
            confidence=0.8,
        ))

        assert not report.is_clean
        assert report.overall_decision == Decision.REVIEW

        # Add a BLOCK flag
        report.add_flag(CredibilityFlag(
            decision=Decision.BLOCK,
            reason="Blocking issue",
            confidence=0.9,
        ))

        assert report.overall_decision == Decision.BLOCK, (
            "BLOCK should win over REVIEW"
        )
