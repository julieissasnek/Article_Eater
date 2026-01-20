"""
VOI-Driven Search for Article Eater Post-Quinean.

TODO 3: VOI-Driven Search

Sprints:
- Sprint H: Core structures, VOI scoring, source selection
- Sprint I: Strategy selection with epsilon decay, stopping rules,
            null result detection
- Sprint J: TODO 1 integration, pipeline helpers

Per Phase D revised plan:
- Two gap types initially: UNCERTAIN, UNEXPLORED (per Lampson)
- Source selection by domain (per Giles)
- Epsilon-greedy with decay (per Simon)
- Expanded null result vocabulary (per Cartwright)
- Satisficing stopping rules (per Simon)

Date: January 20, 2026
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from src.services.web_of_belief import WebOfBelief, Belief, Credence

logger = logging.getLogger(__name__)


# =============================================================================
# CORE DATA STRUCTURES (per Lampson)
# =============================================================================

class GapType(Enum):
    """
    Two gap types initially (per Lampson).

    Add CAUSAL, SCOPE, etc. when we have ≥10 cases each.
    """
    UNCERTAIN = "uncertain"       # High uncertainty on existing belief
    UNEXPLORED = "unexplored"     # Topic area with sparse coverage


@dataclass
class EpistemicGap:
    """
    Minimal gap structure.

    Represents a knowledge gap that could be addressed by searching
    for additional literature.
    """
    gap_type: GapType
    description: str
    primary_belief_id: str
    voi_score: float  # Value of information (0-1)

    def to_search_context(self) -> Dict[str, Any]:
        """Context for query generation."""
        return {
            "gap_type": self.gap_type.value,
            "belief_id": self.primary_belief_id,
            "description": self.description,
            "voi_score": self.voi_score
        }


@dataclass
class SearchRecommendation:
    """
    Minimal recommendation structure.

    Represents a paper found during search that may address a gap.
    """
    paper_id: str
    title: str
    relevance_score: float
    ranking_explanation: str

    # For TODO 1 integration (Sprint J)
    expected_credibility_profile: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'relevance_score': self.relevance_score,
            'ranking_explanation': self.ranking_explanation,
            'expected_credibility_profile': self.expected_credibility_profile
        }


@dataclass
class SearchResult:
    """Result from a single search query."""
    query: str
    source: str
    recommendations: List[SearchRecommendation]
    raw_count: int  # Total results before filtering
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'source': self.source,
            'n_recommendations': len(self.recommendations),
            'raw_count': self.raw_count,
            'execution_time_ms': self.execution_time_ms
        }


@dataclass
class SearchSession:
    """
    A complete search session for addressing a gap.

    Tracks all queries and results for a single gap.
    """
    gap: EpistemicGap
    results: List[SearchResult] = field(default_factory=list)
    total_queries: int = 0
    stopped_reason: Optional[str] = None

    @property
    def all_recommendations(self) -> List[SearchRecommendation]:
        """All recommendations across all results."""
        all_recs = []
        for result in self.results:
            all_recs.extend(result.recommendations)
        return all_recs

    @property
    def unique_papers(self) -> int:
        """Count of unique paper IDs found."""
        return len(set(r.paper_id for r in self.all_recommendations))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'gap': self.gap.to_search_context(),
            'total_queries': self.total_queries,
            'unique_papers': self.unique_papers,
            'stopped_reason': self.stopped_reason,
            'results': [r.to_dict() for r in self.results]
        }


# =============================================================================
# VOI SCORING (per Pearl)
# =============================================================================

class VOICalculator:
    """
    Calculate Value of Information for epistemic gaps.

    Per Pearl: VOI should reflect how much the gap's resolution
    would reduce uncertainty in the overall web.
    """

    # Weights for VOI components
    UNCERTAINTY_WEIGHT = 0.4
    CENTRALITY_WEIGHT = 0.3
    SPARSITY_WEIGHT = 0.3

    def calculate_voi(
        self,
        gap_type: GapType,
        belief: Belief,
        web: Optional[WebOfBelief] = None
    ) -> float:
        """
        Calculate VOI score for a gap.

        Args:
            gap_type: Type of gap (uncertain vs unexplored)
            belief: The belief associated with the gap
            web: Optional web for centrality calculation

        Returns:
            VOI score between 0 and 1
        """
        components = []

        # Uncertainty component
        uncertainty_score = self._uncertainty_component(belief)
        components.append(uncertainty_score * self.UNCERTAINTY_WEIGHT)

        # Centrality component (how connected is this belief?)
        if web:
            centrality_score = self._centrality_component(belief, web)
            components.append(centrality_score * self.CENTRALITY_WEIGHT)
        else:
            # Default centrality if no web provided
            components.append(0.5 * self.CENTRALITY_WEIGHT)

        # Sparsity component (how little evidence do we have?)
        sparsity_score = self._sparsity_component(gap_type, belief)
        components.append(sparsity_score * self.SPARSITY_WEIGHT)

        return min(sum(components), 1.0)

    def _uncertainty_component(self, belief: Belief) -> float:
        """Score based on credence uncertainty."""
        # Higher uncertainty = higher VOI
        return belief.credence.uncertainty

    def _centrality_component(self, belief: Belief, web: WebOfBelief) -> float:
        """Score based on belief's centrality in the web."""
        # Count constraints involving this belief
        n_constraints = 0
        for constraint in web.constraints.values():
            if constraint.source_id == belief.belief_id or \
               constraint.target_id == belief.belief_id:
                n_constraints += 1

        # Normalize (assuming max ~20 constraints for a central belief)
        return min(n_constraints / 20.0, 1.0)

    def _sparsity_component(self, gap_type: GapType, belief: Belief) -> float:
        """Score based on evidence sparsity."""
        if gap_type == GapType.UNEXPLORED:
            # Unexplored gaps have high sparsity by definition
            return 0.8

        # For uncertain gaps, base on number of supporting papers
        n_papers = len(belief.paper_ids) if belief.paper_ids else 0
        if n_papers == 0:
            return 1.0
        elif n_papers < 3:
            return 0.7
        elif n_papers < 5:
            return 0.4
        else:
            return 0.2


# =============================================================================
# SOURCE SELECTION (per Giles)
# =============================================================================

# Per Giles: Different sources for different domains
SOURCE_BY_DOMAIN = {
    "neuroscience": ["pubmed", "semantic_scholar"],
    "psychology": ["semantic_scholar", "pubmed", "psycinfo"],
    "architecture": ["semantic_scholar", "avery_index"],
    "healthcare": ["pubmed", "cochrane"],
    "education": ["eric", "semantic_scholar"],
    "environmental_psychology": ["semantic_scholar", "pubmed", "psycinfo"],
    "default": ["semantic_scholar"]
}


class SourceSelector:
    """
    Select appropriate sources for a search.

    Per Giles: Different sources have different coverage strengths.
    """

    def __init__(self, source_map: Optional[Dict[str, List[str]]] = None):
        """
        Initialize with source mapping.

        Args:
            source_map: Optional custom source mapping. Uses default if None.
        """
        self.source_map = source_map or SOURCE_BY_DOMAIN

    def select_sources(
        self,
        gap: EpistemicGap,
        belief: Optional[Belief] = None
    ) -> List[str]:
        """
        Choose sources based on gap and belief's domain.

        Args:
            gap: The epistemic gap to search for
            belief: Optional belief for domain inference

        Returns:
            List of source identifiers
        """
        if belief:
            domain = self._infer_domain(belief)
        else:
            domain = "default"

        return self.source_map.get(domain, self.source_map["default"])

    def _infer_domain(self, belief: Belief) -> str:
        """Infer domain from belief content and IDs."""
        content_lower = belief.content.lower()

        # Check for domain-specific terms
        if any(term in content_lower for term in ["cortisol", "amygdala", "brain", "neural"]):
            return "neuroscience"
        elif any(term in content_lower for term in ["patient", "hospital", "clinical", "treatment"]):
            return "healthcare"
        elif any(term in content_lower for term in ["building", "space", "design", "architectural"]):
            return "architecture"
        elif any(term in content_lower for term in ["student", "learning", "classroom", "teaching"]):
            return "education"
        elif any(term in content_lower for term in ["nature", "stress", "wellbeing", "restoration"]):
            # CNfA domain
            return "environmental_psychology"
        else:
            return "psychology"  # Default for CNfA

    def get_source_priority(self, source: str, domain: str) -> int:
        """
        Get priority of a source for a domain.

        Lower number = higher priority.
        """
        sources = self.source_map.get(domain, self.source_map["default"])
        try:
            return sources.index(source)
        except ValueError:
            return 999  # Not in list


# =============================================================================
# QUERY GENERATION
# =============================================================================

class QueryGenerator:
    """
    Generate search queries from epistemic gaps.

    Creates queries appropriate for the gap type and target sources.
    """

    def generate_queries(
        self,
        gap: EpistemicGap,
        belief: Optional[Belief] = None,
        max_queries: int = 5
    ) -> List[str]:
        """
        Generate search queries for a gap.

        Args:
            gap: The epistemic gap
            belief: Optional belief for context
            max_queries: Maximum number of queries to generate

        Returns:
            List of query strings
        """
        queries = []

        # Base query from gap description
        base_terms = self._extract_terms(gap.description)
        if base_terms:
            queries.append(" ".join(base_terms))

        # Add belief-based queries if available
        if belief:
            belief_terms = self._extract_terms(belief.content)
            if belief_terms:
                queries.append(" ".join(belief_terms))

            # Add scope-based query if available
            if belief.scope:
                scope_terms = []
                if hasattr(belief.scope, 'population') and belief.scope.population:
                    scope_terms.append(belief.scope.population)
                if hasattr(belief.scope, 'setting') and belief.scope.setting:
                    scope_terms.append(belief.scope.setting)
                if scope_terms and belief_terms:
                    queries.append(" ".join(belief_terms[:2] + scope_terms))

        # Add gap-type specific queries
        if gap.gap_type == GapType.UNCERTAIN:
            # For uncertain gaps, look for replication/meta-analysis
            if belief:
                key_terms = self._extract_terms(belief.content)[:3]
                queries.append(" ".join(key_terms + ["meta-analysis"]))
                queries.append(" ".join(key_terms + ["replication"]))

        elif gap.gap_type == GapType.UNEXPLORED:
            # For unexplored, look for any evidence
            if belief:
                key_terms = self._extract_terms(belief.content)[:3]
                queries.append(" ".join(key_terms + ["systematic review"]))

        # Deduplicate and limit
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)

        return unique_queries[:max_queries]

    def _extract_terms(self, text: str) -> List[str]:
        """Extract search terms from text."""
        # Remove common words
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'to', 'of', 'in', 'for', 'on', 'with', 'that', 'this', 'it',
            'what', 'how', 'why', 'does', 'do', 'can', 'should', 'and',
            'or', 'but', 'not', 'from', 'at', 'by', 'as', 'into', 'through'
        }

        words = text.lower().split()
        terms = [w for w in words if w not in stopwords and len(w) > 2]

        return terms


# =============================================================================
# GAP DETECTOR (Enhanced from TODO 2)
# =============================================================================

class GapDetector:
    """
    Detect epistemic gaps in a web of belief.

    Enhanced from TODO 2's GapIdentifier to create EpistemicGap objects.
    """

    UNCERTAINTY_THRESHOLD = 0.3
    MIN_SUPPORTING_STUDIES = 3

    def __init__(self, voi_calculator: Optional[VOICalculator] = None):
        self.voi_calculator = voi_calculator or VOICalculator()

    def detect_gaps(
        self,
        web: WebOfBelief,
        max_gaps: int = 10
    ) -> List[EpistemicGap]:
        """
        Detect epistemic gaps in the web.

        Args:
            web: Web of belief to analyze
            max_gaps: Maximum gaps to return

        Returns:
            List of EpistemicGap objects sorted by VOI
        """
        gaps = []

        for belief_id, belief in web.beliefs.items():
            # Check for uncertain gap
            if belief.credence.uncertainty > self.UNCERTAINTY_THRESHOLD:
                voi = self.voi_calculator.calculate_voi(
                    GapType.UNCERTAIN, belief, web
                )
                gaps.append(EpistemicGap(
                    gap_type=GapType.UNCERTAIN,
                    description=f"High uncertainty ({belief.credence.uncertainty:.0%}) on: {belief.content[:50]}...",
                    primary_belief_id=belief_id,
                    voi_score=voi
                ))

            # Check for unexplored gap
            n_papers = len(belief.paper_ids) if belief.paper_ids else 0
            if n_papers < self.MIN_SUPPORTING_STUDIES:
                voi = self.voi_calculator.calculate_voi(
                    GapType.UNEXPLORED, belief, web
                )
                gaps.append(EpistemicGap(
                    gap_type=GapType.UNEXPLORED,
                    description=f"Only {n_papers} supporting studies for: {belief.content[:50]}...",
                    primary_belief_id=belief_id,
                    voi_score=voi
                ))

        # Sort by VOI and return top gaps
        gaps.sort(key=lambda g: g.voi_score, reverse=True)
        return gaps[:max_gaps]


# =============================================================================
# MAIN SEARCH COORDINATOR
# =============================================================================

class VOISearchCoordinator:
    """
    Main coordinator for VOI-driven search.

    Orchestrates gap detection, query generation, and search execution.
    """

    def __init__(
        self,
        web: WebOfBelief,
        gap_detector: Optional[GapDetector] = None,
        source_selector: Optional[SourceSelector] = None,
        query_generator: Optional[QueryGenerator] = None
    ):
        self.web = web
        self.gap_detector = gap_detector or GapDetector()
        self.source_selector = source_selector or SourceSelector()
        self.query_generator = query_generator or QueryGenerator()

    def identify_search_priorities(self, max_gaps: int = 5) -> List[EpistemicGap]:
        """
        Identify highest-priority gaps for search.

        Returns gaps sorted by VOI score.
        """
        return self.gap_detector.detect_gaps(self.web, max_gaps)

    def create_search_session(self, gap: EpistemicGap) -> SearchSession:
        """
        Create a search session for a gap.

        Does not execute searches, just prepares the session.
        """
        return SearchSession(gap=gap)

    def generate_search_plan(
        self,
        gap: EpistemicGap
    ) -> Dict[str, Any]:
        """
        Generate a search plan for a gap.

        Returns a plan with sources and queries.
        """
        belief = self.web.beliefs.get(gap.primary_belief_id)

        sources = self.source_selector.select_sources(gap, belief)
        queries = self.query_generator.generate_queries(gap, belief)

        return {
            'gap': gap.to_search_context(),
            'sources': sources,
            'queries': queries,
            'estimated_searches': len(sources) * len(queries)
        }

    def export_search_priorities(
        self,
        output_path: Optional[str] = None,
        max_gaps: int = 10
    ) -> Dict[str, Any]:
        """
        Export search priorities for external processing.

        Args:
            output_path: Optional path to write JSON
            max_gaps: Maximum gaps to include

        Returns:
            Dict with gaps and search plans
        """
        gaps = self.identify_search_priorities(max_gaps)

        result = {
            'n_gaps': len(gaps),
            'gaps': [],
        }

        for gap in gaps:
            plan = self.generate_search_plan(gap)
            result['gaps'].append(plan)

        if output_path:
            import json
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)

        return result


# =============================================================================
# SPRINT I: STRATEGY SELECTION (per Simon)
# =============================================================================

class SearchStrategy(Enum):
    """Available search strategies."""
    KEYWORD = "keyword"       # Standard keyword search
    CITATION = "citation"     # Citation-based search (find citing papers)
    SEMANTIC = "semantic"     # Semantic similarity search


class StrategySelector:
    """
    Strategy selection with decaying exploration.

    Per Simon: Start with exploration, gradually shift to exploitation
    as we learn which strategies work best for each gap type.
    """

    def __init__(
        self,
        initial_epsilon: float = 0.3,
        min_epsilon: float = 0.05,
        decay: float = 0.99
    ):
        """
        Initialize strategy selector.

        Args:
            initial_epsilon: Initial exploration rate (0-1)
            min_epsilon: Minimum exploration rate
            decay: Decay factor per search
        """
        self.initial_epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay
        self.total_searches = 0

        # Track strategy performance by gap type
        self._strategy_successes: Dict[Tuple[GapType, SearchStrategy], int] = {}
        self._strategy_attempts: Dict[Tuple[GapType, SearchStrategy], int] = {}

    @property
    def epsilon(self) -> float:
        """Current epsilon (decays with experience)."""
        return max(
            self.initial_epsilon * (self.decay ** self.total_searches),
            self.min_epsilon
        )

    def select_strategy(self, gap: EpistemicGap) -> SearchStrategy:
        """
        Select strategy with epsilon-greedy + decay.

        Args:
            gap: The epistemic gap to search for

        Returns:
            Selected search strategy
        """
        if random.random() < self.epsilon:
            # Explore: random strategy
            return random.choice(list(SearchStrategy))
        else:
            # Exploit: best known strategy for this gap type
            return self._best_strategy_for(gap.gap_type)

    def _best_strategy_for(self, gap_type: GapType) -> SearchStrategy:
        """Get best performing strategy for gap type."""
        best_strategy = SearchStrategy.KEYWORD
        best_rate = 0.0

        for strategy in SearchStrategy:
            key = (gap_type, strategy)
            attempts = self._strategy_attempts.get(key, 0)

            if attempts > 0:
                success_rate = self._strategy_successes.get(key, 0) / attempts
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_strategy = strategy

        return best_strategy

    def record_search(
        self,
        gap_type: GapType,
        strategy: SearchStrategy,
        success: bool
    ) -> None:
        """
        Record search outcome for learning.

        Args:
            gap_type: Type of gap searched
            strategy: Strategy used
            success: Whether search found relevant results
        """
        self.total_searches += 1
        key = (gap_type, strategy)

        self._strategy_attempts[key] = self._strategy_attempts.get(key, 0) + 1
        if success:
            self._strategy_successes[key] = self._strategy_successes.get(key, 0) + 1

    def get_stats(self) -> Dict[str, Any]:
        """Get strategy performance statistics."""
        stats = {
            'total_searches': self.total_searches,
            'current_epsilon': self.epsilon,
            'strategy_performance': {}
        }

        for (gap_type, strategy), attempts in self._strategy_attempts.items():
            successes = self._strategy_successes.get((gap_type, strategy), 0)
            key = f"{gap_type.value}_{strategy.value}"
            stats['strategy_performance'][key] = {
                'attempts': attempts,
                'successes': successes,
                'success_rate': successes / attempts if attempts > 0 else 0
            }

        return stats


# =============================================================================
# SPRINT I: STOPPING RULES (per Simon)
# =============================================================================

@dataclass
class StoppingDecision:
    """Result of stopping rule evaluation."""
    should_stop: bool
    reason: str
    relevant_found: int
    queries_executed: int


def should_stop_searching(
    gap: EpistemicGap,
    results_so_far: List[SearchRecommendation],
    queries_executed: int,
    max_queries: int = 20,
    min_relevance: float = 0.3,
    sufficient_results: int = 10
) -> StoppingDecision:
    """
    Determine if we should stop searching for this gap.

    Per Simon: satisficing with diminishing returns.

    Args:
        gap: The epistemic gap being searched
        results_so_far: All recommendations collected
        queries_executed: Number of queries run
        max_queries: Hard limit on queries
        min_relevance: Minimum relevance score to count
        sufficient_results: Stop when this many relevant found

    Returns:
        StoppingDecision with should_stop flag and reason
    """
    relevant_results = [r for r in results_so_far if r.relevance_score >= min_relevance]
    n_relevant = len(relevant_results)

    # Hard limit
    if queries_executed >= max_queries:
        return StoppingDecision(
            should_stop=True,
            reason=f"Reached query limit ({max_queries})",
            relevant_found=n_relevant,
            queries_executed=queries_executed
        )

    # Sufficient results
    if n_relevant >= sufficient_results:
        return StoppingDecision(
            should_stop=True,
            reason=f"Found sufficient relevant papers ({n_relevant})",
            relevant_found=n_relevant,
            queries_executed=queries_executed
        )

    # Diminishing returns
    if queries_executed >= 5:
        # Check last 10 results
        recent_results = results_so_far[-10:] if len(results_so_far) >= 10 else results_so_far
        recent_relevant = sum(1 for r in recent_results if r.relevance_score >= min_relevance)

        if recent_relevant == 0:
            return StoppingDecision(
                should_stop=True,
                reason="No relevant papers in recent results (diminishing returns)",
                relevant_found=n_relevant,
                queries_executed=queries_executed
            )

    # Continue searching
    return StoppingDecision(
        should_stop=False,
        reason="Continue searching",
        relevant_found=n_relevant,
        queries_executed=queries_executed
    )


# =============================================================================
# SPRINT I: NULL RESULT DETECTION (per Cartwright)
# =============================================================================

class NullResultDetector:
    """
    Detect null result indicators in paper text.

    Per Cartwright: Papers with null results are underrepresented
    but crucial for accurate belief calibration.
    """

    def __init__(self, vocab_path: Optional[str] = None):
        """
        Initialize detector.

        Args:
            vocab_path: Path to null_result_indicators.yaml
        """
        self.vocabulary = self._load_vocabulary(vocab_path)

    def _load_vocabulary(self, vocab_path: Optional[str]) -> Dict[str, Any]:
        """Load null result vocabulary."""
        if vocab_path is None:
            # Default path
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            vocab_path = os.path.join(project_root, "contracts", "vocab", "null_result_indicators.yaml")

        try:
            import yaml
            from pathlib import Path
            path = Path(vocab_path)
            if path.exists():
                with open(path) as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load null result vocabulary: {e}")

        return {'null_result_vocabulary': {}}

    def detect_null_indicators(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Detect null result indicators in text.

        Args:
            text: Abstract or title text to analyze

        Returns:
            Dict with detected categories and terms
        """
        text_lower = text.lower()
        results = {
            'has_null_indicators': False,
            'categories_detected': [],
            'terms_found': [],
            'total_weight': 0.0
        }

        vocab = self.vocabulary.get('null_result_vocabulary', {})

        for category, data in vocab.items():
            terms = data.get('terms', [])
            weight = data.get('weight', 1.0)

            for term in terms:
                if term.lower() in text_lower:
                    results['has_null_indicators'] = True
                    if category not in results['categories_detected']:
                        results['categories_detected'].append(category)
                    results['terms_found'].append(term)
                    results['total_weight'] += weight

        return results

    def get_search_boost(
        self,
        text: str,
        gap_type: GapType
    ) -> float:
        """
        Calculate search priority boost for a paper.

        Higher boost = prioritize papers with null results.

        Args:
            text: Paper text to analyze
            gap_type: Type of gap being searched

        Returns:
            Boost factor (1.0 = no boost)
        """
        detection = self.detect_null_indicators(text)

        if not detection['has_null_indicators']:
            return 1.0

        # Base boost from detected weight
        boost = 1.0 + (detection['total_weight'] * 0.2)

        # Additional boost if categories match gap type relevance
        relevance = self.vocabulary.get('gap_type_relevance', {})
        relevant_categories = relevance.get(gap_type.value, [])

        for category in detection['categories_detected']:
            if category in relevant_categories:
                boost += 0.2

        return min(boost, 2.5)  # Cap at 2.5x


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_voi_coordinator(web: WebOfBelief) -> VOISearchCoordinator:
    """Create a VOI search coordinator."""
    return VOISearchCoordinator(web)


def detect_gaps(web: WebOfBelief, max_gaps: int = 10) -> List[EpistemicGap]:
    """Quick function to detect gaps in a web."""
    detector = GapDetector()
    return detector.detect_gaps(web, max_gaps)


def calculate_voi(
    gap_type: GapType,
    belief: Belief,
    web: Optional[WebOfBelief] = None
) -> float:
    """Calculate VOI for a specific gap."""
    calculator = VOICalculator()
    return calculator.calculate_voi(gap_type, belief, web)
