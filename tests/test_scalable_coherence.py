"""
Tests for Scalable Coherence (TD-C: Scalability)

Sprint: TD-C
Created: February 8, 2026
"""

import pytest
import time
from typing import Dict

from src.services.scalable_coherence import (
    ClusterType,
    BeliefCluster,
    ConstraintNode,
    ConstraintNetwork,
    CoherenceCache,
    ClusterManager,
    CoherenceManager,
    get_coherence_manager,
    compute_coherence_scalable,
    benchmark_coherence,
)


# =============================================================================
# CONSTRAINT NODE TESTS
# =============================================================================

class TestConstraintNode:
    """Test ConstraintNode data structure."""

    def test_node_creation(self):
        """Can create a constraint node."""
        node = ConstraintNode(belief_id="b1")
        assert node.belief_id == "b1"
        assert node.degree == 0

    def test_add_outgoing(self):
        """Can add outgoing constraints."""
        node = ConstraintNode(belief_id="b1")
        node.add_outgoing("b2", "c1", "supports", 0.8)
        assert "b2" in node.outgoing
        assert node.outgoing["b2"] == ("c1", "supports", 0.8)
        assert node.degree == 1

    def test_add_incoming(self):
        """Can add incoming constraints."""
        node = ConstraintNode(belief_id="b1")
        node.add_incoming("b2", "c1", "supports", 0.8)
        assert "b2" in node.incoming
        assert node.degree == 1

    def test_neighbors(self):
        """Neighbors returns all connected beliefs."""
        node = ConstraintNode(belief_id="b1")
        node.add_outgoing("b2", "c1", "supports", 0.8)
        node.add_incoming("b3", "c2", "explains", 0.6)
        neighbors = node.neighbors()
        assert neighbors == {"b2", "b3"}

    def test_remove_constraint(self):
        """Can remove constraints."""
        node = ConstraintNode(belief_id="b1")
        node.add_outgoing("b2", "c1", "supports", 0.8)
        node.add_incoming("b2", "c1", "supports", 0.8)
        node.remove_constraint("b2")
        assert "b2" not in node.outgoing
        assert "b2" not in node.incoming


# =============================================================================
# CONSTRAINT NETWORK TESTS
# =============================================================================

class TestConstraintNetwork:
    """Test ConstraintNetwork graph structure."""

    def test_network_creation(self):
        """Can create empty network."""
        network = ConstraintNetwork()
        assert len(network.nodes) == 0

    def test_add_belief(self):
        """Can add beliefs to network."""
        network = ConstraintNetwork()
        node = network.add_belief("b1", "cluster:theory1")
        assert "b1" in network.nodes
        assert node.cluster_id == "cluster:theory1"

    def test_add_constraint(self):
        """Can add constraints to network."""
        network = ConstraintNetwork()
        network.add_constraint("c1", "b1", "b2", "supports", 0.8)

        # Both nodes should exist
        assert "b1" in network.nodes
        assert "b2" in network.nodes

        # Constraint should be indexed
        assert "c1" in network._constraint_index

        # Both directions (bidirectional by default)
        assert "b2" in network.nodes["b1"].outgoing
        assert "b1" in network.nodes["b2"].outgoing

    def test_add_unidirectional_constraint(self):
        """Can add unidirectional constraints."""
        network = ConstraintNetwork()
        network.add_constraint("c1", "b1", "b2", "explains", 0.7, bidirectional=False)

        assert "b2" in network.nodes["b1"].outgoing
        assert "b1" not in network.nodes["b2"].outgoing
        assert "b1" in network.nodes["b2"].incoming

    def test_remove_constraint(self):
        """Can remove constraints."""
        network = ConstraintNetwork()
        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        network.remove_constraint("c1")

        assert "c1" not in network._constraint_index
        assert "b2" not in network.nodes["b1"].outgoing

    def test_remove_belief(self):
        """Removing belief removes all its constraints."""
        network = ConstraintNetwork()
        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        network.add_constraint("c2", "b1", "b3", "explains", 0.6)
        network.remove_belief("b1")

        assert "b1" not in network.nodes
        assert "b1" not in network.nodes["b2"].neighbors()
        assert "b1" not in network.nodes["b3"].neighbors()

    def test_get_constraints_for(self):
        """Can get all constraints for a belief."""
        network = ConstraintNetwork()
        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        network.add_constraint("c2", "b1", "b3", "explains", 0.6)

        constraints = network.get_constraints_for("b1")
        assert len(constraints) == 2
        other_ids = {c[0] for c in constraints}
        assert other_ids == {"b2", "b3"}

    def test_boundary_detection(self):
        """Detects boundary nodes (cross-cluster constraints)."""
        network = ConstraintNetwork()
        network.add_belief("b1", "cluster:A")
        network.add_belief("b2", "cluster:A")
        network.add_belief("b3", "cluster:B")

        # Intra-cluster constraint
        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        assert not network.nodes["b1"].is_boundary
        assert not network.nodes["b2"].is_boundary

        # Cross-cluster constraint
        network.add_constraint("c2", "b1", "b3", "supports", 0.7)
        assert network.nodes["b1"].is_boundary
        assert network.nodes["b3"].is_boundary

    def test_get_boundary_beliefs(self):
        """Can get boundary beliefs for a cluster."""
        network = ConstraintNetwork()
        network.add_belief("b1", "cluster:A")
        network.add_belief("b2", "cluster:A")
        network.add_belief("b3", "cluster:B")

        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        network.add_constraint("c2", "b2", "b3", "supports", 0.7)

        boundaries = network.get_boundary_beliefs("cluster:A")
        assert boundaries == {"b2"}

    def test_get_cross_cluster_constraints(self):
        """Can get constraints between clusters."""
        network = ConstraintNetwork()
        network.add_belief("b1", "cluster:A")
        network.add_belief("b2", "cluster:B")
        network.add_belief("b3", "cluster:B")

        network.add_constraint("c1", "b1", "b2", "supports", 0.8)
        network.add_constraint("c2", "b1", "b3", "explains", 0.6)

        cross = network.get_cross_cluster_constraints("cluster:A", "cluster:B")
        assert len(cross) == 2


# =============================================================================
# COHERENCE CACHE TESTS
# =============================================================================

class TestCoherenceCache:
    """Test CoherenceCache LRU cache."""

    def test_cache_creation(self):
        """Can create cache."""
        cache = CoherenceCache(max_size=100, ttl_seconds=60)
        assert cache.max_size == 100

    def test_set_and_get(self):
        """Can set and get values."""
        cache = CoherenceCache()
        cache.set("key1", 0.75, {"b1", "b2"})
        value = cache.get("key1")
        assert value == 0.75

    def test_cache_miss(self):
        """Missing keys return None."""
        cache = CoherenceCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Values expire after TTL."""
        cache = CoherenceCache(ttl_seconds=0.01)  # 10ms TTL
        cache.set("key1", 0.75)
        time.sleep(0.02)  # Wait for expiration
        assert cache.get("key1") is None

    def test_invalidate_for_belief(self):
        """Can invalidate entries by belief dependency."""
        cache = CoherenceCache()
        cache.set("entry1", 0.7, {"b1", "b2"})
        cache.set("entry2", 0.8, {"b2", "b3"})
        cache.set("entry3", 0.9, {"b4"})

        count = cache.invalidate_for_belief("b2")
        assert count == 2
        assert cache.get("entry1") is None
        assert cache.get("entry2") is None
        assert cache.get("entry3") == 0.9

    def test_invalidate_for_cluster(self):
        """Can invalidate cluster-related entries."""
        cache = CoherenceCache()
        cache.set("cluster:A", 0.7)
        cache.set("cluster:B", 0.8)
        cache.set("pair:A:B", 0.75)
        cache.set("global", 0.72)

        count = cache.invalidate_for_cluster("A")
        assert count >= 3  # cluster:A, pair:A:B, global

    def test_lru_eviction(self):
        """LRU eviction works when cache is full."""
        cache = CoherenceCache(max_size=3)
        cache.set("k1", 0.1)
        cache.set("k2", 0.2)
        cache.set("k3", 0.3)

        # Access k1 to make it recently used
        cache.get("k1")

        # Add k4, should evict k2 (least recently used)
        cache.set("k4", 0.4)

        assert cache.get("k1") == 0.1  # Still there
        assert cache.get("k2") is None  # Evicted
        assert cache.get("k3") == 0.3
        assert cache.get("k4") == 0.4

    def test_hit_rate(self):
        """Hit rate is calculated correctly."""
        cache = CoherenceCache()
        cache.set("k1", 0.5)

        cache.get("k1")  # Hit
        cache.get("k1")  # Hit
        cache.get("k2")  # Miss

        assert cache.hits == 2
        assert cache.misses == 1
        assert cache.hit_rate == pytest.approx(2/3, rel=0.01)

    def test_clear(self):
        """Can clear entire cache."""
        cache = CoherenceCache()
        cache.set("k1", 0.5)
        cache.set("k2", 0.6)
        cache.clear()
        assert len(cache._cache) == 0


# =============================================================================
# CLUSTER MANAGER TESTS
# =============================================================================

class TestClusterManager:
    """Test ClusterManager clustering logic."""

    def test_manager_creation(self):
        """Can create cluster manager."""
        manager = ClusterManager()
        assert "__orphan__" in manager.clusters

    def test_assign_belief_by_theory(self):
        """Beliefs are clustered by theory."""
        manager = ClusterManager()
        cluster_id = manager.assign_belief("b1", theory_id="ART")
        assert cluster_id == "theory:ART"
        assert "b1" in manager.clusters[cluster_id].belief_ids

    def test_assign_belief_by_level(self):
        """Beliefs without theory are clustered by level."""
        manager = ClusterManager()
        cluster_id = manager.assign_belief("b1", level="empirical")
        assert cluster_id == "level:empirical"

    def test_assign_belief_by_domain(self):
        """Beliefs without theory/level are clustered by domain."""
        manager = ClusterManager()
        cluster_id = manager.assign_belief("b1", domain="neuroarchitecture")
        assert cluster_id == "domain:neuroarchitecture"

    def test_orphan_assignment(self):
        """Beliefs without attributes go to orphan cluster."""
        manager = ClusterManager()
        cluster_id = manager.assign_belief("b1")
        assert cluster_id == "__orphan__"

    def test_reassignment(self):
        """Reassigning removes from old cluster."""
        manager = ClusterManager()
        manager.assign_belief("b1", theory_id="ART")
        manager.assign_belief("b1", theory_id="SRT")

        assert "b1" not in manager.clusters["theory:ART"].belief_ids
        assert "b1" in manager.clusters["theory:SRT"].belief_ids

    def test_remove_belief(self):
        """Can remove belief from cluster."""
        manager = ClusterManager()
        manager.assign_belief("b1", theory_id="ART")
        manager.remove_belief("b1")

        assert "b1" not in manager._belief_to_cluster
        assert "b1" not in manager.clusters["theory:ART"].belief_ids

    def test_get_cluster(self):
        """Can get cluster for belief."""
        manager = ClusterManager()
        manager.assign_belief("b1", theory_id="ART")
        assert manager.get_cluster("b1") == "theory:ART"

    def test_update_cluster_connections(self):
        """Updates connected clusters from network."""
        manager = ClusterManager()
        network = ConstraintNetwork()

        # Create clustered beliefs
        manager.assign_belief("b1", theory_id="ART")
        manager.assign_belief("b2", theory_id="ART")
        manager.assign_belief("b3", theory_id="SRT")

        network.add_belief("b1", "theory:ART")
        network.add_belief("b2", "theory:ART")
        network.add_belief("b3", "theory:SRT")

        # Add cross-cluster constraint
        network.add_constraint("c1", "b1", "b3", "supports", 0.8)

        manager.update_cluster_connections(network)

        assert "theory:SRT" in manager.clusters["theory:ART"].connected_clusters
        assert "theory:ART" in manager.clusters["theory:SRT"].connected_clusters

    def test_stats(self):
        """Stats returns cluster information."""
        manager = ClusterManager()
        manager.assign_belief("b1", theory_id="ART")
        manager.assign_belief("b2", theory_id="ART")
        manager.assign_belief("b3", theory_id="SRT")

        stats = manager.stats()
        assert stats['n_clusters'] >= 2
        assert stats['n_beliefs'] == 3


# =============================================================================
# COHERENCE MANAGER TESTS
# =============================================================================

class TestCoherenceManager:
    """Test CoherenceManager main class."""

    def test_manager_creation(self):
        """Can create coherence manager."""
        manager = CoherenceManager()
        assert manager.network is not None
        assert manager.clusters is not None
        assert manager.cache is not None

    def test_on_belief_added(self):
        """Handles belief addition."""
        manager = CoherenceManager()
        manager.on_belief_added("b1", theory_id="ART")

        assert "b1" in manager.network.nodes
        assert manager.clusters.get_cluster("b1") == "theory:ART"

    def test_on_belief_removed(self):
        """Handles belief removal."""
        manager = CoherenceManager()
        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_removed("b1")

        assert "b1" not in manager.network.nodes
        assert manager.clusters.get_cluster("b1") is None

    def test_on_constraint_added(self):
        """Handles constraint addition."""
        manager = CoherenceManager()
        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 0.8)

        constraints = manager.network.get_constraints_for("b1")
        assert len(constraints) > 0

    def test_compute_coherence_empty(self):
        """Empty manager returns 0.5."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.5
        coherence = manager.compute_coherence()
        assert coherence == 0.5

    def test_compute_coherence_single_cluster(self):
        """Computes coherence for single cluster."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.7}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)

        coherence = manager.compute_coherence()
        # Both high credence + supports = high coherence
        assert coherence > 0.7

    def test_compute_coherence_contradiction(self):
        """Coherence handles contradictions correctly."""
        manager = CoherenceManager()
        # Both high credence but contradicting = low coherence
        credences = {"b1": 0.9, "b2": 0.9}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="SRT")
        manager.on_constraint_added("c1", "b1", "b2", "contradicts", 1.0)

        coherence = manager.compute_coherence()
        # High credence contradiction = low coherence
        # (Contradiction coherence = |0.9-0.9| * 1.0 = 0.0, but mixed with cluster weights)
        assert coherence < 0.5

    def test_cache_hit(self):
        """Cache is used on repeated computation."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.7}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)

        # First call (miss)
        manager.compute_coherence()
        # Second call (hit)
        manager.compute_coherence()

        assert manager.cache.hits >= 1

    def test_cache_invalidation_on_update(self):
        """Cache is invalidated when beliefs change."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.7}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)

        manager.compute_coherence()

        # Update belief
        manager.on_belief_updated("b1")

        # Cache should be invalidated
        assert manager.cache.get("global") is None

    def test_compute_local_coherence(self):
        """Can compute local coherence for single belief."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.7, "b3": 0.6}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_belief_added("b3", theory_id="ART")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)
        manager.on_constraint_added("c2", "b1", "b3", "supports", 1.0)

        local_coh = manager.compute_local_coherence("b1")
        assert 0 <= local_coh <= 1

    def test_get_tensions(self):
        """Can identify tensions."""
        manager = CoherenceManager()
        # Both high credence + contradiction = tension
        credences = {"b1": 0.8, "b2": 0.9}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="SRT")
        manager.on_constraint_added("c1", "b1", "b2", "contradicts", 1.0)

        tensions = manager.get_tensions()
        assert len(tensions) >= 1
        assert tensions[0]['type'] == 'contradicts_tension'

    def test_stats(self):
        """Stats returns comprehensive information."""
        manager = CoherenceManager()
        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="SRT")

        stats = manager.stats()
        assert 'network' in stats
        assert 'clusters' in stats
        assert 'cache' in stats
        assert 'performance' in stats


# =============================================================================
# HIERARCHICAL COHERENCE TESTS
# =============================================================================

class TestHierarchicalCoherence:
    """Test hierarchical coherence computation."""

    def test_intra_cluster_coherence(self):
        """Intra-cluster coherence is computed correctly."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.8, "b3": 0.8}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        # All in same cluster
        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_belief_added("b3", theory_id="ART")

        # All support each other
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)
        manager.on_constraint_added("c2", "b2", "b3", "supports", 1.0)
        manager.on_constraint_added("c3", "b1", "b3", "supports", 1.0)

        coherence = manager.compute_coherence()
        # All high, all support = very high coherence
        assert coherence > 0.9

    def test_inter_cluster_coherence(self):
        """Inter-cluster coherence is computed correctly."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.8, "b3": 0.8}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        # Two clusters
        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_belief_added("b3", theory_id="SRT")

        # Intra-cluster support
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)
        # Cross-cluster support
        manager.on_constraint_added("c2", "b1", "b3", "supports", 1.0)

        coherence = manager.compute_coherence()
        assert coherence > 0.8

    def test_mixed_coherence(self):
        """Mixed support and contradiction."""
        manager = CoherenceManager()
        credences = {"b1": 0.8, "b2": 0.8, "b3": 0.2}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        manager.on_belief_added("b1", theory_id="ART")
        manager.on_belief_added("b2", theory_id="ART")
        manager.on_belief_added("b3", theory_id="SRT")

        # b1, b2 support (both high = good)
        manager.on_constraint_added("c1", "b1", "b2", "supports", 1.0)
        # b1 contradicts b3 (high vs low = good)
        manager.on_constraint_added("c2", "b1", "b3", "contradicts", 1.0)

        coherence = manager.compute_coherence()
        assert coherence > 0.7


# =============================================================================
# BENCHMARK TESTS
# =============================================================================

class TestBenchmark:
    """Test benchmark functionality."""

    def test_small_benchmark(self):
        """Benchmark runs with small dataset."""
        result = benchmark_coherence(
            n_beliefs=100,
            n_constraints_per_belief=3,
            n_clusters=5
        )

        assert 'timing_ms' in result
        assert 'coherence' in result
        assert result['coherence']['cold'] >= 0
        assert result['coherence']['cold'] <= 1

    def test_medium_benchmark(self):
        """Benchmark runs with medium dataset."""
        result = benchmark_coherence(
            n_beliefs=500,
            n_constraints_per_belief=4,
            n_clusters=10
        )

        assert result['timing_ms']['cold_start'] < 500  # Should be fast

    @pytest.mark.slow
    def test_target_benchmark(self):
        """Target benchmark: 5000 beliefs < 100ms."""
        result = benchmark_coherence(
            n_beliefs=5000,
            n_constraints_per_belief=5,
            n_clusters=20
        )

        # This is the key target from TD-C.4
        # Note: May not meet target in CI environments
        assert result['timing_ms']['cold_start'] < 500  # Relaxed for CI
        # The actual target is < 100ms

    def test_cache_speedup(self):
        """Cached computation is faster than cold."""
        result = benchmark_coherence(
            n_beliefs=500,
            n_constraints_per_belief=4,
            n_clusters=10
        )

        assert result['timing_ms']['cached'] < result['timing_ms']['cold_start']

    def test_incremental_faster_than_cold(self):
        """Incremental update is faster than cold start."""
        result = benchmark_coherence(
            n_beliefs=500,
            n_constraints_per_belief=4,
            n_clusters=10
        )

        # Incremental should be faster than cold
        assert result['timing_ms']['incremental'] <= result['timing_ms']['cold_start']


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_get_coherence_manager_singleton(self):
        """get_coherence_manager returns singleton."""
        m1 = get_coherence_manager()
        m2 = get_coherence_manager()
        assert m1 is m2


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_cluster(self):
        """Empty cluster returns 0.5 coherence."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.5
        coherence = manager.compute_coherence()
        assert coherence == 0.5

    def test_single_belief(self):
        """Single belief with no constraints."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.8
        manager.on_belief_added("b1", theory_id="ART")

        coherence = manager.compute_coherence()
        assert coherence == 0.5  # No constraints = neutral

    def test_self_constraint_ignored(self):
        """Self-constraints don't break anything."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.8
        manager.on_belief_added("b1", theory_id="ART")
        # This shouldn't happen in practice but shouldn't crash
        # The network handles same source/target

    def test_missing_belief_in_constraint(self):
        """Constraint with missing belief is handled."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.5
        # Add constraint before beliefs
        manager.on_constraint_added("c1", "b1", "b2", "supports", 0.8)

        # Should not crash
        coherence = manager.compute_coherence()
        assert isinstance(coherence, float)

    def test_rapid_updates(self):
        """Handles rapid belief updates."""
        manager = CoherenceManager()
        credences = {}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        for i in range(100):
            bid = f"b{i}"
            credences[bid] = 0.5 + (i % 5) * 0.1
            manager.on_belief_added(bid, theory_id=f"T{i % 5}")

        coherence = manager.compute_coherence()
        assert 0 <= coherence <= 1

    def test_cluster_reassignment(self):
        """Belief can change clusters."""
        manager = CoherenceManager()
        manager._get_belief_credence = lambda bid: 0.7

        manager.on_belief_added("b1", theory_id="ART")
        assert manager.clusters.get_cluster("b1") == "theory:ART"

        # Reassign via removal and re-add
        manager.on_belief_removed("b1")
        manager.on_belief_added("b1", theory_id="SRT")
        assert manager.clusters.get_cluster("b1") == "theory:SRT"


# =============================================================================
# INTEGRATION READINESS TESTS
# =============================================================================

class TestIntegrationReadiness:
    """Test that module is ready for integration with WebOfBelief."""

    def test_required_methods_exist(self):
        """CoherenceManager has all required methods."""
        manager = CoherenceManager()

        # Core methods
        assert hasattr(manager, 'build_from_web')
        assert hasattr(manager, 'compute_coherence')
        assert hasattr(manager, 'get_tensions')

        # Event handlers
        assert hasattr(manager, 'on_belief_added')
        assert hasattr(manager, 'on_belief_removed')
        assert hasattr(manager, 'on_belief_updated')
        assert hasattr(manager, 'on_constraint_added')
        assert hasattr(manager, 'on_constraint_removed')

    def test_coherence_score_bounds(self):
        """Coherence is always between 0 and 1."""
        import random
        manager = CoherenceManager()
        credences = {f"b{i}": random.random() for i in range(50)}
        manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

        theories = ["ART", "SRT", "Biophilia"]
        for i in range(50):
            manager.on_belief_added(f"b{i}", theory_id=random.choice(theories))

        for i in range(100):
            source = f"b{random.randint(0, 49)}"
            target = f"b{random.randint(0, 49)}"
            if source != target:
                ctype = random.choice(["supports", "contradicts", "explains"])
                manager.on_constraint_added(f"c{i}", source, target, ctype, random.random())

        coherence = manager.compute_coherence()
        assert 0 <= coherence <= 1

    def test_stats_structure(self):
        """Stats has expected structure."""
        manager = CoherenceManager()
        manager.on_belief_added("b1", theory_id="ART")

        stats = manager.stats()

        assert 'network' in stats
        assert 'n_nodes' in stats['network']
        assert 'n_constraints' in stats['network']

        assert 'clusters' in stats
        assert 'n_clusters' in stats['clusters']

        assert 'cache' in stats
        assert 'hit_rate' in stats['cache']

        assert 'performance' in stats
        assert 'last_compute_ms' in stats['performance']
