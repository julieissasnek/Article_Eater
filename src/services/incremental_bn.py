"""
Incremental Bayesian Network Learning

Sprint: TD-E (Incremental BN Learning)
Panel: P-TD (Technical Debt)
Created: February 8, 2026

This module implements incremental learning for Bayesian Network parameters.
Articles drip in over time, rules accumulate in Article Eater, then flow
to the BN where parameters are refined. The system gets smarter the longer
it runs.

Key insight from P-TD Panel:
"Posterior updating is inherently incremental. Each new paper updates the
posterior over BN parameters. The previous posterior becomes the new prior.
No need to reprocess all papers." - Dr. Michael Jordan

Architecture:
    Articles → AE extracts rules → Beliefs accumulate → BN params refine
                                          ↑
         VOI search finds gaps ← Uncertainty tracking identifies weak edges

Uses conjugate priors (Beta-Bernoulli) for closed-form updates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import logging
import json
from pathlib import Path
from datetime import datetime, timezone
import math
from itertools import product

logger = logging.getLogger(__name__)

try:
    from pgmpy.models import DiscreteBayesianNetwork as _PgmpyBN  # pgmpy>=0.1.24
except Exception:
    try:
        from pgmpy.models import BayesianNetwork as _PgmpyBN  # older pgmpy
    except Exception:
        _PgmpyBN = None

try:
    from pgmpy.factors.discrete import TabularCPD as _TabularCPD
    from pgmpy.inference import VariableElimination as _VariableElimination
except Exception:
    _TabularCPD = None
    _VariableElimination = None


# =============================================================================
# EDGE TYPES
# =============================================================================

class EdgeType(Enum):
    """Type of causal/correlational edge."""
    CAUSAL = "causal"              # X causes Y
    CORRELATIONAL = "correlational"  # X associated with Y
    MECHANISM = "mechanism"         # X mediates Y→Z
    MODERATION = "moderation"       # X moderates Y→Z effect
    UNKNOWN = "unknown"


class EvidenceType(Enum):
    """Type of evidence for edge. Canonical values per contracts/vocab/canonical_enums.json."""
    EXPERIMENTAL = "experimental"   # RCT, controlled experiment
    OBSERVATIONAL = "observational" # Cross-sectional, survey (also default for unknown)
    META_ANALYSIS = "meta_analysis" # Aggregated studies
    THEORETICAL = "theoretical"     # Derived from theory
    # DEPRECATED: "unknown" mapped to "observational" per Sprint 1.5 enum consolidation (2026-02-16)


# =============================================================================
# BETA-BERNOULLI EDGE
# =============================================================================

@dataclass
class BetaBernoulliEdge:
    """
    Edge strength with Beta prior, Bernoulli likelihood.

    Per Dr. Andrew Gelman (P-TD Panel):
    "For credences and BN edge strengths, use conjugate priors for
    closed-form updates."

    The Beta distribution is conjugate to Bernoulli, meaning:
    - Prior: Beta(α, β)
    - Likelihood: Bernoulli observations
    - Posterior: Beta(α + successes, β + failures)

    This allows O(1) updates without reprocessing all data.
    """
    # Edge identity
    source: str
    target: str
    edge_type: EdgeType = EdgeType.UNKNOWN

    # Beta distribution parameters
    # Start with weak prior: Beta(1, 1) = uniform
    alpha: float = 1.0  # Prior "successes" (evidence FOR edge)
    beta: float = 1.0   # Prior "failures" (evidence AGAINST edge)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    n_papers: int = 0  # Number of papers contributing evidence
    paper_ids: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)  # Explicit rule topics/categories

    # Evidence quality weighting
    total_weight: float = 0.0  # Sum of evidence weights

    def update(
        self,
        supports: bool,
        weight: float = 1.0,
        paper_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Update edge estimate with new evidence.

        Args:
            supports: True if evidence supports edge, False if contradicts
            weight: Evidence quality weight (0-1, higher = more reliable)
            paper_id: Source paper for tracking
            tags: List of topic/category tags from the evidence source
        """
        weighted_evidence = weight

        if supports:
            self.alpha += weighted_evidence
        else:
            self.beta += weighted_evidence

        self.total_weight += weight
        self.n_papers += 1
        self.last_updated = datetime.now(timezone.utc).isoformat()

        if paper_id:
            self.paper_ids.add(paper_id)
            
        if tags:
            self.tags.update(tags)

    def update_batch(
        self,
        n_supporting: int,
        n_contradicting: int,
        avg_weight: float = 1.0,
        paper_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Update with batch of evidence (e.g., from meta-analysis).

        Args:
            n_supporting: Number of studies supporting edge
            n_contradicting: Number of studies contradicting edge
            avg_weight: Average quality weight of studies
            paper_ids: Source papers
            tags: Mixed tags/topics across the batch
        """
        self.alpha += n_supporting * avg_weight
        self.beta += n_contradicting * avg_weight
        self.total_weight += (n_supporting + n_contradicting) * avg_weight
        self.n_papers += n_supporting + n_contradicting
        self.last_updated = datetime.now(timezone.utc).isoformat()

        if paper_ids:
            self.paper_ids.update(paper_ids)
            
        if tags:
            self.tags.update(tags)

    @property
    def mean(self) -> float:
        """
        Posterior mean (point estimate of edge strength).

        E[Beta(α, β)] = α / (α + β)
        """
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        """
        Posterior variance (uncertainty in estimate).

        Var[Beta(α, β)] = αβ / ((α + β)² (α + β + 1))
        """
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))

    @property
    def std(self) -> float:
        """Standard deviation of estimate."""
        return math.sqrt(self.variance)

    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval for edge strength.

        Args:
            confidence: Confidence level (default 95%)

        Returns:
            Tuple of (lower, upper) bounds
        """
        try:
            from scipy.stats import beta as beta_dist
            tail = (1 - confidence) / 2
            lower = beta_dist.ppf(tail, self.alpha, self.beta)
            upper = beta_dist.ppf(1 - tail, self.alpha, self.beta)
            return (lower, upper)
        except ImportError:
            # Fallback: approximate with mean ± 2*std
            lower = max(0, self.mean - 2 * self.std)
            upper = min(1, self.mean + 2 * self.std)
            return (lower, upper)

    @property
    def effective_sample_size(self) -> float:
        """
        Effective sample size (how much data underlies estimate).

        ESS = α + β - 2 (subtract prior pseudo-counts)
        """
        return max(0, self.alpha + self.beta - 2)

    @property
    def uncertainty(self) -> float:
        """
        Uncertainty score (0-1, higher = more uncertain).

        Based on credible interval width and sample size.
        """
        ci = self.credible_interval()
        ci_width = ci[1] - ci[0]

        # Normalize by sample size (more samples = less uncertainty)
        sample_factor = 1 / (1 + self.effective_sample_size / 10)

        return min(1.0, ci_width * 0.5 + sample_factor * 0.5)

    @property
    def is_reliable(self) -> bool:
        """
        Whether estimate is reliable enough for inference.

        Reliable if:
        - Effective sample size >= 3
        - 95% CI width < 0.5
        """
        ci = self.credible_interval()
        return (
            self.effective_sample_size >= 3 and
            (ci[1] - ci[0]) < 0.5
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ci = self.credible_interval()
        return {
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type.value,
            'alpha': self.alpha,
            'beta': self.beta,
            'mean': self.mean,
            'std': self.std,
            'credible_interval_95': list(ci),
            'uncertainty': self.uncertainty,
            'effective_sample_size': self.effective_sample_size,
            'is_reliable': self.is_reliable,
            'n_papers': self.n_papers,
            'paper_ids': list(self.paper_ids),
            'tags': list(self.tags),
            'created_at': self.created_at,
            'last_updated': self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BetaBernoulliEdge':
        """Deserialize from dictionary."""
        return cls(
            source=data['source'],
            target=data['target'],
            edge_type=EdgeType(data.get('edge_type', 'unknown')),
            alpha=data.get('alpha', 1.0),
            beta=data.get('beta', 1.0),
            created_at=data.get('created_at', ''),
            last_updated=data.get('last_updated', ''),
            n_papers=data.get('n_papers', 0),
            paper_ids=set(data.get('paper_ids', [])),
            tags=set(data.get('tags', [])),
            total_weight=data.get('total_weight', 0.0),
        )


# =============================================================================
# EDGE GAP (For Active Learning)
# =============================================================================

@dataclass
class EdgeGap:
    """
    Represents a gap in edge knowledge for active learning.

    Per Dr. Tom Griffiths (P-TD Panel):
    "The system should track what it doesn't know and prioritize learning."
    """
    source: str
    target: str
    uncertainty: float  # How uncertain is this edge?
    relevance: float    # How important is this edge for decisions?
    priority: float = 0.0  # Combined priority score

    # Suggested search queries
    search_queries: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Priority = uncertainty * relevance
        self.priority = self.uncertainty * self.relevance


# =============================================================================
# INCREMENTAL BN BUILDER
# =============================================================================

class IncrementalBNBuilder:
    """
    Builds and updates Bayesian Network parameters incrementally.

    Per Dr. David Blei (P-TD Panel):
    "For large-scale systems, consider streaming variational inference:
    1. Process articles in mini-batches
    2. Update global parameters with stochastic gradient
    3. Never revisit old articles"

    This class manages:
    - Edge parameter estimates (Beta-Bernoulli)
    - Node definitions
    - Uncertainty tracking
    - Active learning suggestions
    """

    def __init__(self, persistence_path: Optional[Path] = None):
        """
        Initialize builder.

        Args:
            persistence_path: Optional path to persist state
        """
        self.edges: Dict[Tuple[str, str], BetaBernoulliEdge] = {}
        self.nodes: Set[str] = set()
        self.persistence_path = persistence_path

        # Load existing state if available
        if persistence_path and persistence_path.exists():
            self._load_state()

    def _edge_key(self, source: str, target: str) -> Tuple[str, str]:
        """Create canonical edge key."""
        return (source, target)

    def get_edge(self, source: str, target: str) -> Optional[BetaBernoulliEdge]:
        """Get edge if it exists."""
        return self.edges.get(self._edge_key(source, target))

    def get_or_create_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType = EdgeType.UNKNOWN
    ) -> BetaBernoulliEdge:
        """Get existing edge or create new one."""
        key = self._edge_key(source, target)

        if key not in self.edges:
            self.edges[key] = BetaBernoulliEdge(
                source=source,
                target=target,
                edge_type=edge_type
            )
            self.nodes.add(source)
            self.nodes.add(target)

        return self.edges[key]

    def observe_evidence(
        self,
        source: str,
        target: str,
        supports: bool,
        weight: float = 1.0,
        paper_id: Optional[str] = None,
        edge_type: EdgeType = EdgeType.UNKNOWN,
        tags: Optional[List[str]] = None
    ) -> BetaBernoulliEdge:
        """
        Observe evidence for an edge.

        Args:
            source: Source node
            target: Target node
            supports: True if evidence supports edge
            weight: Quality weight (0-1)
            paper_id: Source paper
            edge_type: Type of edge
            tags: Topic classification tags

        Returns:
            Updated edge
        """
        edge = self.get_or_create_edge(source, target, edge_type)
        edge.update(supports=supports, weight=weight, paper_id=paper_id, tags=tags)

        logger.debug(
            f"Updated edge {source}→{target}: "
            f"mean={edge.mean:.3f}, uncertainty={edge.uncertainty:.3f}"
        )

        return edge

    def observe_belief(
        self,
        belief: Any,  # Belief from web_of_belief
        weight: float = 1.0
    ) -> List[BetaBernoulliEdge]:
        """
        Observe evidence from a Belief object.

        Extracts edges from belief's constructs and updates estimates.

        Args:
            belief: Belief object from WebOfBelief
            weight: Quality weight

        Returns:
            List of updated edges
        """
        updated_edges = []

        # Extract environment → outcome edge
        env_id = getattr(belief, 'environment_id', None)
        outcome_id = getattr(belief, 'outcome_id', None)

        if env_id and outcome_id:
            # Determine if belief supports or contradicts effect
            credence = getattr(belief, 'credence', None)
            if credence:
                credence_value = credence.value if hasattr(credence, 'value') else credence
                supports = credence_value > 0.5
            else:
                supports = True  # Default to supporting

            paper_ids = getattr(belief, 'paper_ids', [])
            tags = getattr(belief, 'tags', [])

            edge = self.observe_evidence(
                source=env_id,
                target=outcome_id,
                supports=supports,
                weight=weight,
                paper_id=paper_id,
                edge_type=EdgeType.CAUSAL,
                tags=tags
            )
            updated_edges.append(edge)

        return updated_edges

    def observe_constraint(
        self,
        constraint: Any,  # Constraint from web_of_belief
        weight: float = 1.0
    ) -> Optional[BetaBernoulliEdge]:
        """
        Observe evidence from a Constraint object.

        Args:
            constraint: Constraint from WebOfBelief
            weight: Quality weight

        Returns:
            Updated edge if applicable
        """
        source_id = getattr(constraint, 'source_id', None)
        target_id = getattr(constraint, 'target_id', None)

        if not source_id or not target_id:
            return None

        # Determine constraint type
        constraint_type = getattr(constraint, 'constraint_type', None)
        if constraint_type:
            supports = constraint_type.value in ['supports', 'entails', 'explains']
        else:
            supports = True

        tags = getattr(constraint, 'tags', [])

        edge = self.observe_evidence(
            source=source_id,
            target=target_id,
            supports=supports,
            weight=weight,
            edge_type=EdgeType.CORRELATIONAL,
            tags=tags
        )

        return edge

    def get_uncertain_edges(
        self,
        min_uncertainty: float = 0.3,
        max_results: int = 10
    ) -> List[BetaBernoulliEdge]:
        """
        Get edges with high uncertainty (need more evidence).

        Args:
            min_uncertainty: Minimum uncertainty threshold
            max_results: Maximum edges to return

        Returns:
            List of uncertain edges sorted by uncertainty
        """
        uncertain = [
            edge for edge in self.edges.values()
            if edge.uncertainty >= min_uncertainty
        ]

        return sorted(
            uncertain,
            key=lambda e: e.uncertainty,
            reverse=True
        )[:max_results]

    def get_unreliable_edges(self) -> List[BetaBernoulliEdge]:
        """Get edges that are not yet reliable."""
        return [
            edge for edge in self.edges.values()
            if not edge.is_reliable
        ]

    def identify_gaps(
        self,
        relevance_scores: Optional[Dict[Tuple[str, str], float]] = None,
        max_gaps: int = 10
    ) -> List[EdgeGap]:
        """
        Identify gaps in edge knowledge for active learning.

        Per Dr. Tom Griffiths (P-TD Panel):
        "Which edges need more evidence? Where does uncertainty matter most?"

        Args:
            relevance_scores: Optional dict of (source, target) → relevance
            max_gaps: Maximum gaps to return

        Returns:
            List of EdgeGaps sorted by priority
        """
        gaps = []

        for key, edge in self.edges.items():
            uncertainty = edge.uncertainty

            # Get relevance (default to 0.5 if not provided)
            if relevance_scores:
                relevance = relevance_scores.get(key, 0.5)
            else:
                # Default: more connected edges are more relevant
                relevance = 0.5

            gap = EdgeGap(
                source=edge.source,
                target=edge.target,
                uncertainty=uncertainty,
                relevance=relevance,
                search_queries=self._generate_search_queries(edge)
            )
            gaps.append(gap)

        return sorted(gaps, key=lambda g: g.priority, reverse=True)[:max_gaps]

    def _generate_search_queries(self, edge: BetaBernoulliEdge) -> List[str]:
        """Generate search queries for an edge gap."""
        queries = []

        source = edge.source.replace('_', ' ')
        target = edge.target.replace('_', ' ')

        # Basic relationship query
        queries.append(f'"{source}" AND "{target}"')

        # Causal query
        queries.append(f'"{source}" effect on "{target}"')

        # Mechanism query
        queries.append(f'"{source}" mechanism "{target}"')

        return queries

    def get_bn_parameters(self) -> Dict[Tuple[str, str], float]:
        """
        Export current best estimates for all edges.

        Returns:
            Dict mapping (source, target) to edge strength
        """
        return {
            key: edge.mean
            for key, edge in self.edges.items()
        }

    def get_edge_summary(self) -> Dict[str, Any]:
        """Get summary statistics about edges."""
        if not self.edges:
            return {
                'n_edges': 0,
                'n_nodes': 0,
                'n_reliable': 0,
                'mean_uncertainty': 0.0,
                'total_papers': 0
            }

        uncertainties = [e.uncertainty for e in self.edges.values()]
        all_papers = set()
        for e in self.edges.values():
            all_papers.update(e.paper_ids)

        return {
            'n_edges': len(self.edges),
            'n_nodes': len(self.nodes),
            'n_reliable': sum(1 for e in self.edges.values() if e.is_reliable),
            'n_unreliable': sum(1 for e in self.edges.values() if not e.is_reliable),
            'mean_uncertainty': sum(uncertainties) / len(uncertainties),
            'min_uncertainty': min(uncertainties),
            'max_uncertainty': max(uncertainties),
            'total_papers': len(all_papers)
        }

    # ---------------------------------------------------------------------
    # Optional pgmpy integration (P8.4)
    # ---------------------------------------------------------------------
    def _pgmpy_available(self) -> bool:
        return _PgmpyBN is not None and _TabularCPD is not None and _VariableElimination is not None

    @staticmethod
    def _coerce_binary(value: Any) -> int:
        """Coerce evidence values into binary {0,1}."""
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, (int, float)):
            return 1 if float(value) >= 0.5 else 0
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"1", "true", "yes", "present", "high", "on", "affected"}:
                return 1
        return 0

    def build_pgmpy_model(self) -> Optional[Any]:
        """
        Build a pgmpy Bayesian network from current edges.

        Returns None when pgmpy is unavailable or when the graph cannot be
        converted into a valid DAG model.
        """
        if not self._pgmpy_available():
            logger.debug("pgmpy unavailable; skipping BN model build")
            return None

        if not self.nodes:
            return None

        try:
            edges = [(e.source, e.target) for e in self.edges.values() if e.source != e.target]
            model = _PgmpyBN(edges) if edges else _PgmpyBN()
            model.add_nodes_from(sorted(self.nodes))
        except Exception as exc:
            logger.warning("Failed to initialize pgmpy network: %s", exc)
            return None

        cpds: List[Any] = []
        for node in sorted(self.nodes):
            parents = list(model.get_parents(node))
            n_parents = len(parents)
            # Root prior defaults to uncertainty-neutral 0.5
            if n_parents == 0:
                cpd = _TabularCPD(variable=node, variable_card=2, values=[[0.5], [0.5]])
                cpds.append(cpd)
                continue

            parent_card = [2] * n_parents
            p1_values: List[float] = []
            for assignment in product([0, 1], repeat=n_parents):
                active_scores: List[float] = []
                for idx, parent in enumerate(parents):
                    if assignment[idx] == 1:
                        edge = self.get_edge(parent, node)
                        if edge:
                            active_scores.append(edge.mean)
                if active_scores:
                    p1 = sum(active_scores) / len(active_scores)
                else:
                    p1 = 0.5
                p1 = min(0.99, max(0.01, p1))
                p1_values.append(p1)

            p0_values = [1.0 - p for p in p1_values]
            cpd = _TabularCPD(
                variable=node,
                variable_card=2,
                values=[p0_values, p1_values],
                evidence=parents,
                evidence_card=parent_card,
            )
            cpds.append(cpd)

        try:
            model.add_cpds(*cpds)
            if not model.check_model():
                logger.warning("pgmpy model failed validation check")
                return None
            return model
        except Exception as exc:
            logger.warning("Failed to attach pgmpy CPDs: %s", exc)
            return None

    def query_posterior(self, target: str, evidence: Optional[Dict[str, Any]] = None) -> Optional[float]:
        """
        Query posterior P(target=1 | evidence) using pgmpy VariableElimination.
        """
        model = self.build_pgmpy_model()
        if model is None:
            return None
        if target not in self.nodes:
            return None

        evidence_map = {
            key: self._coerce_binary(value)
            for key, value in (evidence or {}).items()
            if key in self.nodes and key != target
        }
        try:
            infer = _VariableElimination(model)
            q = infer.query(variables=[target], evidence=evidence_map or None, show_progress=False)
            vals = q.values
            if len(vals) >= 2:
                return float(vals[1])
            return None
        except Exception as exc:
            logger.warning("pgmpy posterior query failed (%s): %s", target, exc)
            return None

    def is_d_separated(self, x: str, y: str, observed: Optional[List[str]] = None) -> Optional[bool]:
        """
        Check whether x and y are d-separated given observed nodes.
        """
        model = self.build_pgmpy_model()
        if model is None or x not in self.nodes or y not in self.nodes:
            return None
        obs = [node for node in (observed or []) if node in self.nodes and node not in {x, y}]
        try:
            if hasattr(model, "is_dconnected"):
                return not bool(model.is_dconnected(x, y, observed=obs))
            if hasattr(model, "is_dconnected_to"):
                return not bool(model.is_dconnected_to(x, y, observed=obs))
        except Exception as exc:
            logger.warning("pgmpy d-separation check failed (%s, %s): %s", x, y, exc)
            return None
        return None

    def get_markov_blanket(self, node: str) -> Optional[List[str]]:
        """
        Get Markov blanket for a node via pgmpy model.
        """
        model = self.build_pgmpy_model()
        if model is None or node not in self.nodes:
            return None
        try:
            blanket = model.get_markov_blanket(node)
            return sorted(list(blanket))
        except Exception as exc:
            logger.warning("pgmpy markov blanket failed (%s): %s", node, exc)
            return None

    def save_state(self, path: Optional[Path] = None) -> None:
        """Save state to JSON file."""
        save_path = path or self.persistence_path
        if not save_path:
            logger.warning("No persistence path configured")
            return

        state = {
            'edges': {
                f"{k[0]}→{k[1]}": v.to_dict()
                for k, v in self.edges.items()
            },
            'nodes': list(self.nodes),
            'saved_at': datetime.now(timezone.utc).isoformat()
        }

        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(state, indent=2))
        logger.info(f"Saved BN state to {save_path}")

    def _load_state(self) -> None:
        """Load state from JSON file."""
        if not self.persistence_path or not self.persistence_path.exists():
            return

        try:
            state = json.loads(self.persistence_path.read_text())

            for edge_key, edge_data in state.get('edges', {}).items():
                edge = BetaBernoulliEdge.from_dict(edge_data)
                key = self._edge_key(edge.source, edge.target)
                self.edges[key] = edge

            self.nodes = set(state.get('nodes', []))
            logger.info(f"Loaded BN state: {len(self.edges)} edges, {len(self.nodes)} nodes")

        except Exception as e:
            logger.error(f"Failed to load BN state: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Export full state as dictionary."""
        return {
            'edges': [e.to_dict() for e in self.edges.values()],
            'nodes': list(self.nodes),
            'summary': self.get_edge_summary()
        }


# =============================================================================
# ACTIVE LEARNING SCHEDULER
# =============================================================================

class ActiveLearningScheduler:
    """
    Prioritizes which edges need more evidence.

    Per Dr. Tom Griffiths (P-TD Panel):
    "The system should track what it doesn't know and prioritize learning."

    Combines:
    1. Uncertainty (high uncertainty → need more evidence)
    2. Relevance (important edges → prioritize)
    3. Accessibility (can we find papers?)
    """

    def __init__(self, bn_builder: IncrementalBNBuilder):
        """Initialize with BN builder."""
        self.bn_builder = bn_builder
        self.search_history: Dict[Tuple[str, str], int] = {}  # Track search attempts

    def prioritize_edges(
        self,
        relevance_scores: Optional[Dict[Tuple[str, str], float]] = None,
        max_results: int = 5
    ) -> List[EdgeGap]:
        """
        Get priority-ordered list of edges needing evidence.

        Args:
            relevance_scores: Optional relevance weights
            max_results: Maximum edges to return

        Returns:
            List of EdgeGaps with search suggestions
        """
        gaps = self.bn_builder.identify_gaps(relevance_scores, max_gaps=max_results * 2)

        # Adjust priority based on search history
        for gap in gaps:
            key = (gap.source, gap.target)
            n_searches = self.search_history.get(key, 0)

            # Reduce priority for edges we've already searched for
            if n_searches > 0:
                gap.priority *= (1 / (1 + n_searches * 0.2))

        return sorted(gaps, key=lambda g: g.priority, reverse=True)[:max_results]

    def record_search(self, source: str, target: str) -> None:
        """Record that we searched for evidence on an edge."""
        key = (source, target)
        self.search_history[key] = self.search_history.get(key, 0) + 1

    def get_search_queries(self, max_queries: int = 5) -> List[str]:
        """
        Get suggested search queries for highest-priority gaps.

        Returns:
            List of search query strings
        """
        gaps = self.prioritize_edges(max_results=max_queries)

        queries = []
        for gap in gaps:
            queries.extend(gap.search_queries[:2])  # 2 queries per gap

        return queries[:max_queries]


# =============================================================================
# VOI INTEGRATION
# =============================================================================

def connect_to_voi_search(
    bn_builder: IncrementalBNBuilder,
    voi_coordinator: Any  # VOISearchCoordinator from voi_search.py
) -> None:
    """
    Connect BN uncertainty to VOI search.

    Per Dr. Tom Griffiths (P-TD Panel):
    "This connects back to VOI search—the system should actively
    seek papers that fill gaps."

    Args:
        bn_builder: Incremental BN builder
        voi_coordinator: VOI search coordinator
    """
    # Get uncertain edges
    uncertain_edges = bn_builder.get_uncertain_edges(min_uncertainty=0.4)

    # Convert to search priorities
    for edge in uncertain_edges:
        # Create search context from edge
        search_context = {
            'source': edge.source,
            'target': edge.target,
            'uncertainty': edge.uncertainty,
            'current_estimate': edge.mean,
            'credible_interval': edge.credible_interval()
        }

        # Add to VOI search if coordinator has the method
        if hasattr(voi_coordinator, 'add_edge_gap'):
            voi_coordinator.add_edge_gap(search_context)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Singleton instance
_bn_builder_instance: Optional[IncrementalBNBuilder] = None


def get_bn_builder(persistence_path: Optional[Path] = None) -> IncrementalBNBuilder:
    """Get singleton BN builder instance."""
    global _bn_builder_instance
    if _bn_builder_instance is None:
        _bn_builder_instance = IncrementalBNBuilder(persistence_path)
    return _bn_builder_instance


def observe_belief_in_bn(belief: Any, weight: float = 1.0) -> List[BetaBernoulliEdge]:
    """
    Convenience function to observe a belief in the BN.

    Args:
        belief: Belief from WebOfBelief
        weight: Quality weight

    Returns:
        List of updated edges
    """
    builder = get_bn_builder()
    return builder.observe_belief(belief, weight)


def get_uncertain_edges(min_uncertainty: float = 0.3) -> List[BetaBernoulliEdge]:
    """Get edges with high uncertainty."""
    builder = get_bn_builder()
    return builder.get_uncertain_edges(min_uncertainty)


def get_edge_estimate(source: str, target: str, use_pgmpy_fallback: bool = False) -> Optional[float]:
    """
    Get current estimate for an edge.

    If direct edge estimate is missing and `use_pgmpy_fallback=True`, attempt
    posterior inference P(target=1 | source=1) via optional pgmpy integration.
    """
    builder = get_bn_builder()
    edge = builder.get_edge(source, target)
    if edge:
        return edge.mean
    if use_pgmpy_fallback:
        return builder.query_posterior(target, evidence={source: 1})
    return None


def query_posterior(target: str, evidence: Optional[Dict[str, Any]] = None) -> Optional[float]:
    """Convenience wrapper for pgmpy posterior queries."""
    builder = get_bn_builder()
    return builder.query_posterior(target, evidence)


def check_d_separation(x: str, y: str, observed: Optional[List[str]] = None) -> Optional[bool]:
    """Convenience wrapper for pgmpy d-separation checks."""
    builder = get_bn_builder()
    return builder.is_d_separated(x, y, observed)


def get_markov_blanket(node: str) -> Optional[List[str]]:
    """Convenience wrapper for pgmpy Markov blanket retrieval."""
    builder = get_bn_builder()
    return builder.get_markov_blanket(node)
