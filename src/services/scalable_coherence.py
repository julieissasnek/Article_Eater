"""
Scalable Coherence Computation for Web of Belief
=================================================

Sprint: TD-C (Technical Debt - Scalability)
Created: February 8, 2026

This module implements O(n log n) coherence computation through:
1. Theory-based belief clustering
2. Hierarchical coherence (intra-cluster + inter-cluster)
3. Caching with targeted invalidation
4. Constraint network for O(1) relation lookups

The current O(n²) approach recomputes all constraints on every update.
This module provides a drop-in replacement that scales to 5000+ beliefs
with <100ms update time.

Architecture:
-------------
```
                    WebOfBelief
                         │
                         ▼
              ┌─────────────────────┐
              │  CoherenceManager   │
              │  (this module)      │
              └─────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐    ┌─────────────┐   ┌──────────┐
   │ Cluster │    │ Constraint  │   │ Coherence│
   │ Manager │    │ Network     │   │ Cache    │
   └─────────┘    └─────────────┘   └──────────┘
```

Per P-TD Panel:
- Thagard: Use hierarchical clustering by theory/domain
- Simon: Satisficing over exact computation
- Cartwright: Scope-aware clustering
- Manning: Efficient indexing structures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from enum import Enum
from collections import defaultdict
import time
import logging
import math

logger = logging.getLogger(__name__)


# =============================================================================
# CLUSTER TYPES
# =============================================================================

class ClusterType(Enum):
    """Types of belief clusters."""
    THEORY = "theory"          # Beliefs sharing a theory_id
    LEVEL = "level"            # Beliefs at same epistemic level
    DOMAIN = "domain"          # Beliefs in same domain
    OUTCOME = "outcome"        # Beliefs about same outcome
    ENVIRONMENT = "environment"  # Beliefs about same environment
    UNCLUSTERED = "unclustered"  # Orphan beliefs without cluster


@dataclass
class BeliefCluster:
    """
    A cluster of related beliefs for hierarchical coherence.

    Intra-cluster coherence is computed densely (all pairs).
    Inter-cluster coherence is computed sparsely (boundary beliefs only).
    """
    cluster_id: str
    cluster_type: ClusterType
    belief_ids: Set[str] = field(default_factory=set)

    # Cached coherence values
    intra_coherence: float = 0.5
    intra_coherence_valid: bool = False

    # Boundary beliefs that have cross-cluster constraints
    boundary_beliefs: Set[str] = field(default_factory=set)

    # Connected clusters (for inter-cluster computation)
    connected_clusters: Set[str] = field(default_factory=set)

    # Statistics
    last_updated: float = 0.0  # timestamp
    constraint_count: int = 0

    def invalidate(self) -> None:
        """Mark this cluster's coherence as needing recomputation."""
        self.intra_coherence_valid = False


# =============================================================================
# CONSTRAINT NETWORK
# =============================================================================

@dataclass
class ConstraintNode:
    """
    A node in the constraint network for O(1) lookups.

    Each belief gets a node tracking its incoming and outgoing constraints.
    """
    belief_id: str

    # Outgoing constraints: belief_id -> (constraint_id, type, strength)
    outgoing: Dict[str, Tuple[str, str, float]] = field(default_factory=dict)

    # Incoming constraints: belief_id -> (constraint_id, type, strength)
    incoming: Dict[str, Tuple[str, str, float]] = field(default_factory=dict)

    # Cluster membership
    cluster_id: Optional[str] = None

    # Is this a boundary node (has cross-cluster constraints)?
    is_boundary: bool = False

    def add_outgoing(self, target_id: str, constraint_id: str,
                     constraint_type: str, strength: float) -> None:
        """Add an outgoing constraint."""
        self.outgoing[target_id] = (constraint_id, constraint_type, strength)

    def add_incoming(self, source_id: str, constraint_id: str,
                     constraint_type: str, strength: float) -> None:
        """Add an incoming constraint."""
        self.incoming[source_id] = (constraint_id, constraint_type, strength)

    def remove_constraint(self, other_id: str) -> None:
        """Remove a constraint to/from another belief."""
        self.outgoing.pop(other_id, None)
        self.incoming.pop(other_id, None)

    @property
    def degree(self) -> int:
        """Total number of constraints."""
        return len(self.outgoing) + len(self.incoming)

    def neighbors(self) -> Set[str]:
        """All connected belief IDs."""
        return set(self.outgoing.keys()) | set(self.incoming.keys())


class ConstraintNetwork:
    """
    Graph structure for O(1) constraint lookups.

    Instead of iterating through all constraints, we can:
    1. Look up constraints for a specific belief in O(1)
    2. Find cross-cluster constraints in O(boundary nodes)
    3. Check if two beliefs are connected in O(1)
    """

    def __init__(self):
        self.nodes: Dict[str, ConstraintNode] = {}
        self._constraint_index: Dict[str, Tuple[str, str]] = {}  # constraint_id -> (source, target)

    def add_belief(self, belief_id: str, cluster_id: Optional[str] = None) -> ConstraintNode:
        """Add a belief node to the network."""
        if belief_id not in self.nodes:
            self.nodes[belief_id] = ConstraintNode(belief_id=belief_id, cluster_id=cluster_id)
        else:
            self.nodes[belief_id].cluster_id = cluster_id
        return self.nodes[belief_id]

    def add_constraint(self, constraint_id: str, source_id: str, target_id: str,
                       constraint_type: str, strength: float, bidirectional: bool = True) -> None:
        """Add a constraint edge to the network."""
        # Ensure nodes exist
        if source_id not in self.nodes:
            self.add_belief(source_id)
        if target_id not in self.nodes:
            self.add_belief(target_id)

        # Add edges
        self.nodes[source_id].add_outgoing(target_id, constraint_id, constraint_type, strength)
        self.nodes[target_id].add_incoming(source_id, constraint_id, constraint_type, strength)

        if bidirectional:
            self.nodes[target_id].add_outgoing(source_id, constraint_id, constraint_type, strength)
            self.nodes[source_id].add_incoming(target_id, constraint_id, constraint_type, strength)

        # Index constraint
        self._constraint_index[constraint_id] = (source_id, target_id)

        # Update boundary status
        self._update_boundary_status(source_id)
        self._update_boundary_status(target_id)

    def remove_constraint(self, constraint_id: str) -> None:
        """Remove a constraint from the network."""
        if constraint_id not in self._constraint_index:
            return

        source_id, target_id = self._constraint_index.pop(constraint_id)

        if source_id in self.nodes:
            self.nodes[source_id].remove_constraint(target_id)
        if target_id in self.nodes:
            self.nodes[target_id].remove_constraint(source_id)

        # Fix: Recompute boundary status after constraint removal (ChatGPT review 2026-02-08)
        self._update_boundary_status(source_id)
        self._update_boundary_status(target_id)

    def remove_belief(self, belief_id: str) -> None:
        """Remove a belief and all its constraints from the network."""
        if belief_id not in self.nodes:
            return

        node = self.nodes[belief_id]

        # Fix: Purge _constraint_index entries for this belief (ChatGPT review 2026-02-08)
        # Collect constraint IDs to remove
        constraint_ids_to_remove = [
            cid for cid, (src, tgt) in self._constraint_index.items()
            if src == belief_id or tgt == belief_id
        ]
        for cid in constraint_ids_to_remove:
            del self._constraint_index[cid]

        # Collect neighbors before removal for boundary status update
        neighbors_to_update = list(node.neighbors())

        # Remove all constraints involving this belief
        for other_id in neighbors_to_update:
            if other_id in self.nodes:
                self.nodes[other_id].remove_constraint(belief_id)

        del self.nodes[belief_id]

        # Fix: Recompute boundary status for affected neighbors (ChatGPT review 2026-02-08)
        for other_id in neighbors_to_update:
            self._update_boundary_status(other_id)

    def _update_boundary_status(self, belief_id: str) -> None:
        """Update whether a belief is a boundary node."""
        if belief_id not in self.nodes:
            return

        node = self.nodes[belief_id]
        if node.cluster_id is None:
            node.is_boundary = False
            return

        # Check if any neighbor is in a different cluster
        for neighbor_id in node.neighbors():
            if neighbor_id in self.nodes:
                neighbor_cluster = self.nodes[neighbor_id].cluster_id
                if neighbor_cluster is not None and neighbor_cluster != node.cluster_id:
                    node.is_boundary = True
                    return

        node.is_boundary = False

    def get_constraints_for(self, belief_id: str) -> List[Tuple[str, str, str, float]]:
        """
        Get all constraints involving a belief.

        Returns: List of (other_belief_id, constraint_id, type, strength)
        """
        if belief_id not in self.nodes:
            return []

        node = self.nodes[belief_id]
        result = []

        for other_id, (cid, ctype, strength) in node.outgoing.items():
            result.append((other_id, cid, ctype, strength))

        # Include incoming that aren't bidirectional
        for other_id, (cid, ctype, strength) in node.incoming.items():
            if other_id not in node.outgoing:
                result.append((other_id, cid, ctype, strength))

        return result

    def get_boundary_beliefs(self, cluster_id: str) -> Set[str]:
        """Get all boundary beliefs in a cluster."""
        return {
            bid for bid, node in self.nodes.items()
            if node.cluster_id == cluster_id and node.is_boundary
        }

    def get_cross_cluster_constraints(self, cluster_a: str, cluster_b: str) -> List[Tuple[str, str, str, float]]:
        """Get constraints between two clusters."""
        result = []

        for bid, node in self.nodes.items():
            if node.cluster_id != cluster_a:
                continue

            for other_id, (cid, ctype, strength) in node.outgoing.items():
                if other_id in self.nodes and self.nodes[other_id].cluster_id == cluster_b:
                    result.append((bid, other_id, ctype, strength))

        return result


# =============================================================================
# COHERENCE CACHE
# =============================================================================

@dataclass
class CacheEntry:
    """A single cached coherence value."""
    value: float
    timestamp: float
    valid: bool = True
    dependencies: Set[str] = field(default_factory=set)  # belief_ids that affect this


class CoherenceCache:
    """
    LRU cache for coherence scores with dependency-based invalidation.

    Cache keys:
    - "global": Overall web coherence
    - "cluster:{cluster_id}": Intra-cluster coherence
    - "pair:{cluster_a}:{cluster_b}": Inter-cluster coherence
    - "belief:{belief_id}": Local coherence for a belief
    """

    def __init__(self, max_size: int = 10000, ttl_seconds: float = 300.0):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._belief_to_keys: Dict[str, Set[str]] = defaultdict(set)  # Inverse index
        self._access_order: List[str] = []  # For LRU eviction

        # Statistics
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[float]:
        """Get a cached value if valid."""
        if key not in self._cache:
            self.misses += 1
            return None

        entry = self._cache[key]

        # Check validity
        if not entry.valid:
            self.misses += 1
            return None

        # Check TTL
        if time.time() - entry.timestamp > self.ttl_seconds:
            entry.valid = False
            self.misses += 1
            return None

        self.hits += 1
        self._update_access(key)
        return entry.value

    def set(self, key: str, value: float, dependencies: Set[str] = None) -> None:
        """Cache a coherence value."""
        if dependencies is None:
            dependencies = set()

        # Evict if necessary
        while len(self._cache) >= self.max_size:
            self._evict_lru()

        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            valid=True,
            dependencies=dependencies
        )
        self._cache[key] = entry

        # Update inverse index
        for belief_id in dependencies:
            self._belief_to_keys[belief_id].add(key)

        self._update_access(key)

    def invalidate_for_belief(self, belief_id: str) -> int:
        """Invalidate all cache entries that depend on a belief."""
        count = 0
        for key in self._belief_to_keys.get(belief_id, set()):
            if key in self._cache:
                self._cache[key].valid = False
                count += 1
        return count

    def invalidate_for_cluster(self, cluster_id: str) -> int:
        """Invalidate cluster-related entries."""
        count = 0
        prefix = f"cluster:{cluster_id}"
        for key in list(self._cache.keys()):
            if key.startswith(prefix) or cluster_id in key:
                self._cache[key].valid = False
                count += 1
        # Also invalidate global
        if "global" in self._cache:
            self._cache["global"].valid = False
            count += 1
        return count

    def invalidate_all(self) -> None:
        """Invalidate entire cache."""
        for entry in self._cache.values():
            entry.valid = False

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._belief_to_keys.clear()
        self._access_order.clear()

    def _update_access(self, key: str) -> None:
        """Update access order for LRU."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._access_order:
            return

        key = self._access_order.pop(0)
        if key in self._cache:
            entry = self._cache.pop(key)
            # Clean up inverse index
            for bid in entry.dependencies:
                self._belief_to_keys[bid].discard(key)

    @property
    def hit_rate(self) -> float:
        """Cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate,
            'valid_entries': sum(1 for e in self._cache.values() if e.valid)
        }


# =============================================================================
# CLUSTER MANAGER
# =============================================================================

class ClusterManager:
    """
    Manages belief clustering for hierarchical coherence.

    Clustering strategy (per P-TD panel):
    1. Primary: theory_id (most predictive of constraint patterns)
    2. Secondary: epistemic level (theoretical/empirical/observational)
    3. Tertiary: domain (for cross-theory beliefs)
    """

    def __init__(self):
        self.clusters: Dict[str, BeliefCluster] = {}
        self._belief_to_cluster: Dict[str, str] = {}
        self._orphan_cluster_id = "__orphan__"

        # Create orphan cluster for unassigned beliefs
        self.clusters[self._orphan_cluster_id] = BeliefCluster(
            cluster_id=self._orphan_cluster_id,
            cluster_type=ClusterType.UNCLUSTERED
        )

    def assign_belief(self, belief_id: str, theory_id: Optional[str] = None,
                      level: Optional[str] = None, domain: Optional[str] = None) -> str:
        """
        Assign a belief to a cluster.

        Returns the cluster_id assigned.
        """
        # Remove from old cluster if reassigning
        if belief_id in self._belief_to_cluster:
            old_cluster_id = self._belief_to_cluster[belief_id]
            if old_cluster_id in self.clusters:
                self.clusters[old_cluster_id].belief_ids.discard(belief_id)
                self.clusters[old_cluster_id].invalidate()

        # Determine cluster
        if theory_id:
            cluster_id = f"theory:{theory_id}"
            cluster_type = ClusterType.THEORY
        elif level:
            cluster_id = f"level:{level}"
            cluster_type = ClusterType.LEVEL
        elif domain:
            cluster_id = f"domain:{domain}"
            cluster_type = ClusterType.DOMAIN
        else:
            cluster_id = self._orphan_cluster_id
            cluster_type = ClusterType.UNCLUSTERED

        # Create cluster if new
        if cluster_id not in self.clusters:
            self.clusters[cluster_id] = BeliefCluster(
                cluster_id=cluster_id,
                cluster_type=cluster_type
            )

        # Assign
        self.clusters[cluster_id].belief_ids.add(belief_id)
        self.clusters[cluster_id].invalidate()
        self._belief_to_cluster[belief_id] = cluster_id

        return cluster_id

    def remove_belief(self, belief_id: str) -> None:
        """Remove a belief from its cluster."""
        if belief_id not in self._belief_to_cluster:
            return

        cluster_id = self._belief_to_cluster.pop(belief_id)
        if cluster_id in self.clusters:
            self.clusters[cluster_id].belief_ids.discard(belief_id)
            self.clusters[cluster_id].boundary_beliefs.discard(belief_id)
            self.clusters[cluster_id].invalidate()

    def get_cluster(self, belief_id: str) -> Optional[str]:
        """Get the cluster ID for a belief."""
        return self._belief_to_cluster.get(belief_id)

    def update_cluster_connections(self, network: ConstraintNetwork) -> None:
        """Update which clusters are connected via cross-cluster constraints."""
        # Reset connections
        for cluster in self.clusters.values():
            cluster.connected_clusters.clear()
            cluster.boundary_beliefs.clear()

        # Find connections
        for belief_id, node in network.nodes.items():
            if node.cluster_id is None:
                continue

            for neighbor_id in node.neighbors():
                if neighbor_id not in network.nodes:
                    continue

                neighbor_cluster = network.nodes[neighbor_id].cluster_id
                if neighbor_cluster and neighbor_cluster != node.cluster_id:
                    # Cross-cluster connection
                    self.clusters[node.cluster_id].connected_clusters.add(neighbor_cluster)
                    self.clusters[node.cluster_id].boundary_beliefs.add(belief_id)

    def get_connected_clusters(self, cluster_id: str) -> Set[str]:
        """Get clusters connected to the given cluster."""
        if cluster_id not in self.clusters:
            return set()
        return self.clusters[cluster_id].connected_clusters.copy()

    def stats(self) -> Dict[str, Any]:
        """Return clustering statistics."""
        sizes = [len(c.belief_ids) for c in self.clusters.values()]
        orphan_cluster = self.clusters.get(self._orphan_cluster_id)
        orphan_count = len(orphan_cluster.belief_ids) if orphan_cluster else 0
        return {
            'n_clusters': len(self.clusters),
            'n_beliefs': sum(sizes),
            'avg_cluster_size': sum(sizes) / len(sizes) if sizes else 0,
            'max_cluster_size': max(sizes) if sizes else 0,
            'orphan_count': orphan_count
        }


# =============================================================================
# COHERENCE MANAGER
# =============================================================================

class CoherenceManager:
    """
    Main class for scalable coherence computation.

    Provides a drop-in replacement for WebOfBelief._update_coherence()
    with O(n log n) scaling instead of O(n²).

    Usage:
    ```python
    manager = CoherenceManager()
    manager.build_from_web(web_of_belief)

    # On belief/constraint changes:
    manager.on_belief_added(belief)
    manager.on_constraint_added(constraint)

    # Get coherence:
    coherence = manager.compute_coherence()
    ```
    """

    def __init__(self, cache_ttl: float = 300.0):
        self.network = ConstraintNetwork()
        self.clusters = ClusterManager()
        self.cache = CoherenceCache(ttl_seconds=cache_ttl)

        # Coherence computation parameters
        self.intra_weight = 0.7  # Weight for intra-cluster coherence
        self.inter_weight = 0.3  # Weight for inter-cluster coherence

        # For computing local coherence (injected from web)
        self._get_belief_credence: Optional[Callable[[str], float]] = None

        # Statistics
        self.last_compute_time: float = 0.0
        self.total_computations: int = 0

    def build_from_web(self, web: 'WebOfBelief') -> None:
        """
        Build the scalable coherence structures from a WebOfBelief.

        Call this once on initialization, then use incremental updates.
        """
        # Store credence lookup function
        self._get_belief_credence = lambda bid: web.beliefs[bid].credence.value if bid in web.beliefs else 0.5

        # Build network and clusters
        for belief in web.beliefs.values():
            # Add to network
            cluster_id = self.clusters.assign_belief(
                belief.belief_id,
                theory_id=belief.theory_id,
                level=belief.level.value if belief.level else None,
                domain=belief.domain
            )
            self.network.add_belief(belief.belief_id, cluster_id)

        # Add constraints
        for constraint in web.constraints.values():
            self.network.add_constraint(
                constraint.constraint_id,
                constraint.source_id,
                constraint.target_id,
                constraint.constraint_type.value,
                constraint.strength,
                constraint.bidirectional
            )

        # Update cluster connections
        self.clusters.update_cluster_connections(self.network)

        # Invalidate cache (fresh build)
        self.cache.clear()

    def on_belief_added(self, belief_id: str, theory_id: Optional[str] = None,
                        level: Optional[str] = None, domain: Optional[str] = None) -> None:
        """Handle a new belief being added."""
        cluster_id = self.clusters.assign_belief(belief_id, theory_id, level, domain)
        self.network.add_belief(belief_id, cluster_id)
        self.cache.invalidate_for_cluster(cluster_id)

    def on_belief_removed(self, belief_id: str) -> None:
        """Handle a belief being removed."""
        cluster_id = self.clusters.get_cluster(belief_id)
        self.clusters.remove_belief(belief_id)
        self.network.remove_belief(belief_id)

        if cluster_id:
            self.cache.invalidate_for_cluster(cluster_id)
        self.cache.invalidate_for_belief(belief_id)

    def on_belief_updated(self, belief_id: str) -> None:
        """Handle a belief's credence being updated."""
        self.cache.invalidate_for_belief(belief_id)

        cluster_id = self.clusters.get_cluster(belief_id)
        if cluster_id:
            self.cache.invalidate_for_cluster(cluster_id)

    def on_constraint_added(self, constraint_id: str, source_id: str, target_id: str,
                            constraint_type: str, strength: float, bidirectional: bool = True) -> None:
        """Handle a new constraint being added."""
        self.network.add_constraint(
            constraint_id, source_id, target_id,
            constraint_type, strength, bidirectional
        )

        # Update cluster connections
        self.clusters.update_cluster_connections(self.network)

        # Invalidate affected caches
        self.cache.invalidate_for_belief(source_id)
        self.cache.invalidate_for_belief(target_id)

        source_cluster = self.clusters.get_cluster(source_id)
        target_cluster = self.clusters.get_cluster(target_id)

        if source_cluster:
            self.cache.invalidate_for_cluster(source_cluster)
        if target_cluster and target_cluster != source_cluster:
            self.cache.invalidate_for_cluster(target_cluster)

    def on_constraint_removed(self, constraint_id: str) -> None:
        """Handle a constraint being removed."""
        # Get endpoints before removal
        if constraint_id in self.network._constraint_index:
            source_id, target_id = self.network._constraint_index[constraint_id]
            self.cache.invalidate_for_belief(source_id)
            self.cache.invalidate_for_belief(target_id)

            source_cluster = self.clusters.get_cluster(source_id)
            target_cluster = self.clusters.get_cluster(target_id)

            if source_cluster:
                self.cache.invalidate_for_cluster(source_cluster)
            if target_cluster and target_cluster != source_cluster:
                self.cache.invalidate_for_cluster(target_cluster)

        self.network.remove_constraint(constraint_id)
        self.clusters.update_cluster_connections(self.network)

    def compute_coherence(self, full_recompute: bool = False) -> float:
        """
        Compute overall coherence efficiently.

        Uses hierarchical computation:
        1. Compute intra-cluster coherence for each cluster
        2. Compute inter-cluster coherence (boundary nodes only)
        3. Combine with weights

        Args:
            full_recompute: If True, ignore cache and recompute everything

        Returns:
            Overall coherence score (0.0 to 1.0)
        """
        start_time = time.time()

        # Check cache
        if not full_recompute:
            cached = self.cache.get("global")
            if cached is not None:
                self.last_compute_time = time.time() - start_time
                return cached

        # Compute intra-cluster coherence
        intra_scores = []
        intra_weights = []

        for cluster_id, cluster in self.clusters.clusters.items():
            if not cluster.belief_ids:
                continue

            # Try cache first
            cache_key = f"cluster:{cluster_id}"
            cached_intra = None if full_recompute else self.cache.get(cache_key)

            if cached_intra is not None:
                intra_coh = cached_intra
            else:
                intra_coh = self._compute_intra_cluster_coherence(cluster)
                self.cache.set(cache_key, intra_coh, cluster.belief_ids)

            # Weight by cluster size
            weight = len(cluster.belief_ids)
            intra_scores.append(intra_coh * weight)
            intra_weights.append(weight)

        intra_coherence = sum(intra_scores) / sum(intra_weights) if intra_weights else 0.5

        # Compute inter-cluster coherence (sparse)
        inter_scores = []
        inter_weights = []

        processed_pairs = set()
        for cluster_id, cluster in self.clusters.clusters.items():
            for connected_id in cluster.connected_clusters:
                pair = tuple(sorted([cluster_id, connected_id]))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)

                cache_key = f"pair:{pair[0]}:{pair[1]}"
                cached_inter = None if full_recompute else self.cache.get(cache_key)

                if cached_inter is not None:
                    inter_coh = cached_inter
                else:
                    inter_coh = self._compute_inter_cluster_coherence(cluster_id, connected_id)
                    self.cache.set(cache_key, inter_coh,
                                   cluster.boundary_beliefs | self.clusters.clusters[connected_id].boundary_beliefs)

                # Weight by number of cross-cluster constraints
                n_constraints = len(self.network.get_cross_cluster_constraints(cluster_id, connected_id))
                if n_constraints > 0:
                    inter_scores.append(inter_coh * n_constraints)
                    inter_weights.append(n_constraints)

        inter_coherence = sum(inter_scores) / sum(inter_weights) if inter_weights else 0.5

        # Combine
        if inter_weights:
            overall = self.intra_weight * intra_coherence + self.inter_weight * inter_coherence
        else:
            # No inter-cluster constraints, just use intra
            overall = intra_coherence

        # Cache result
        all_beliefs = {bid for c in self.clusters.clusters.values() for bid in c.belief_ids}
        self.cache.set("global", overall, all_beliefs)

        self.last_compute_time = time.time() - start_time
        self.total_computations += 1

        return overall

    def compute_local_coherence(self, belief_id: str) -> float:
        """
        Compute local coherence for a single belief.

        This is the contribution of this belief to overall coherence.
        Useful for identifying problematic beliefs.
        """
        cache_key = f"belief:{belief_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        if belief_id not in self.network.nodes:
            return 0.5

        constraints = self.network.get_constraints_for(belief_id)
        if not constraints:
            return 0.5

        if self._get_belief_credence is None:
            return 0.5

        source_cred = self._get_belief_credence(belief_id)
        total = 0.0
        count = 0

        for other_id, _, ctype, strength in constraints:
            target_cred = self._get_belief_credence(other_id)
            local_coh = self._compute_pairwise_coherence(source_cred, target_cred, ctype, strength)
            total += local_coh
            count += 1

        result = total / count if count > 0 else 0.5
        self.cache.set(cache_key, result, {belief_id})
        return result

    def get_tensions(self) -> List[Dict[str, Any]]:
        """
        Identify tensions (high-credence contradictions) efficiently.

        Only checks contradiction-type constraints.
        """
        tensions = []

        for belief_id, node in self.network.nodes.items():
            if self._get_belief_credence is None:
                continue

            source_cred = self._get_belief_credence(belief_id)
            if source_cred <= 0.6:
                continue  # Only high-credence beliefs

            for other_id, (cid, ctype, strength) in node.outgoing.items():
                if ctype not in ('contradicts', 'strong_tension'):
                    continue

                target_cred = self._get_belief_credence(other_id)
                if target_cred > 0.6:
                    tensions.append({
                        'source': belief_id,
                        'target': other_id,
                        'source_credence': source_cred,
                        'target_credence': target_cred,
                        'type': f'{ctype}_tension',
                        'constraint_id': cid
                    })

        return tensions

    def _compute_intra_cluster_coherence(self, cluster: BeliefCluster) -> float:
        """Compute coherence within a cluster (dense computation)."""
        if not cluster.belief_ids or self._get_belief_credence is None:
            return 0.5

        total = 0.0
        count = 0

        for belief_id in cluster.belief_ids:
            constraints = self.network.get_constraints_for(belief_id)
            source_cred = self._get_belief_credence(belief_id)

            for other_id, _, ctype, strength in constraints:
                # Only count intra-cluster constraints
                if other_id not in cluster.belief_ids:
                    continue

                target_cred = self._get_belief_credence(other_id)
                local_coh = self._compute_pairwise_coherence(source_cred, target_cred, ctype, strength)
                total += local_coh
                count += 1

        return total / count if count > 0 else 0.5

    def _compute_inter_cluster_coherence(self, cluster_a: str, cluster_b: str) -> float:
        """Compute coherence between two clusters (sparse, boundary only)."""
        if self._get_belief_credence is None:
            return 0.5

        constraints = self.network.get_cross_cluster_constraints(cluster_a, cluster_b)
        if not constraints:
            return 0.5

        total = 0.0
        for source_id, target_id, ctype, strength in constraints:
            source_cred = self._get_belief_credence(source_id)
            target_cred = self._get_belief_credence(target_id)
            local_coh = self._compute_pairwise_coherence(source_cred, target_cred, ctype, strength)
            total += local_coh

        return total / len(constraints)

    def _compute_pairwise_coherence(self, source_cred: float, target_cred: float,
                                     constraint_type: str, strength: float) -> float:
        """
        Compute coherence for a single constraint.

        Same logic as WebOfBelief._update_coherence() but for one pair.
        """
        if constraint_type == 'supports':
            # Coherent if both high or both low
            agreement = 1 - abs(source_cred - target_cred)
            return agreement * strength

        elif constraint_type == 'contradicts':
            # Coherent if one high and one low
            disagreement = abs(source_cred - target_cred)
            return disagreement * strength

        elif constraint_type in ('explains', 'instantiates'):
            # Explanatory coherence
            return (source_cred * target_cred) * strength

        elif constraint_type == 'bridges':
            # Bridge constraint
            agreement = 1 - abs(source_cred - target_cred)
            return agreement * strength * 0.8

        elif constraint_type == 'strong_tension':
            # Strong tension (failed bridge)
            disagreement = abs(source_cred - target_cred)
            return disagreement * strength * 0.5

        else:
            return 0.5 * strength

    def stats(self) -> Dict[str, Any]:
        """Return comprehensive statistics."""
        return {
            'network': {
                'n_nodes': len(self.network.nodes),
                'n_constraints': len(self.network._constraint_index)
            },
            'clusters': self.clusters.stats(),
            'cache': self.cache.stats(),
            'performance': {
                'last_compute_ms': self.last_compute_time * 1000,
                'total_computations': self.total_computations
            }
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_manager: Optional[CoherenceManager] = None


def get_coherence_manager() -> CoherenceManager:
    """Get or create the default coherence manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = CoherenceManager()
    return _default_manager


def compute_coherence_scalable(web: 'WebOfBelief', rebuild: bool = False) -> float:
    """
    Compute coherence using the scalable algorithm.

    Drop-in replacement for web._update_coherence().

    Args:
        web: The WebOfBelief instance
        rebuild: If True, rebuild all structures from scratch

    Returns:
        Coherence score (0.0 to 1.0)
    """
    manager = get_coherence_manager()

    if rebuild or not manager.network.nodes:
        manager.build_from_web(web)

    return manager.compute_coherence()


def benchmark_coherence(n_beliefs: int = 5000, n_constraints_per_belief: int = 5,
                        n_clusters: int = 20) -> Dict[str, Any]:
    """
    Benchmark coherence computation.

    Creates a synthetic web with the specified parameters and measures
    computation time.

    Args:
        n_beliefs: Number of beliefs to create
        n_constraints_per_belief: Average constraints per belief
        n_clusters: Number of theory clusters

    Returns:
        Benchmark results including timing
    """
    import random

    manager = CoherenceManager()

    # Create synthetic beliefs
    belief_ids = [f"b_{i}" for i in range(n_beliefs)]
    theory_ids = [f"theory_{i}" for i in range(n_clusters)]

    # Assign to clusters
    for bid in belief_ids:
        theory_id = random.choice(theory_ids)
        cluster_id = manager.clusters.assign_belief(bid, theory_id=theory_id)
        manager.network.add_belief(bid, cluster_id)

    # Create constraints (within and across clusters)
    n_constraints = n_beliefs * n_constraints_per_belief
    constraint_types = ['supports', 'contradicts', 'explains', 'bridges']

    for i in range(n_constraints):
        source = random.choice(belief_ids)
        target = random.choice(belief_ids)
        if source == target:
            continue

        ctype = random.choice(constraint_types)
        strength = random.uniform(0.3, 1.0)

        manager.network.add_constraint(
            f"c_{i}", source, target, ctype, strength, bidirectional=True
        )

    manager.clusters.update_cluster_connections(manager.network)

    # Create fake credence lookup
    credences = {bid: random.uniform(0.3, 0.9) for bid in belief_ids}
    manager._get_belief_credence = lambda bid: credences.get(bid, 0.5)

    # Benchmark cold start
    manager.cache.clear()
    start = time.time()
    coherence_cold = manager.compute_coherence(full_recompute=True)
    cold_time = time.time() - start

    # Benchmark warm (cached)
    start = time.time()
    coherence_warm = manager.compute_coherence()
    warm_time = time.time() - start

    # Benchmark incremental update
    updated_belief = random.choice(belief_ids)
    manager.on_belief_updated(updated_belief)

    start = time.time()
    coherence_incr = manager.compute_coherence()
    incr_time = time.time() - start

    return {
        'parameters': {
            'n_beliefs': n_beliefs,
            'n_constraints': n_constraints,
            'n_clusters': n_clusters
        },
        'timing_ms': {
            'cold_start': cold_time * 1000,
            'cached': warm_time * 1000,
            'incremental': incr_time * 1000
        },
        'coherence': {
            'cold': coherence_cold,
            'warm': coherence_warm,
            'incremental': coherence_incr
        },
        'target_met': cold_time * 1000 < 100,  # <100ms target
        'stats': manager.stats()
    }
