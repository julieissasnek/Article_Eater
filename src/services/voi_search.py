"""
VOI-Driven Search for Article Eater Post-Quinean.

TODO 3: VOI-Driven Search

Sprints:
- Sprint H: Core structures, VOI scoring, source selection
- Sprint I: Strategy selection, null result vocabulary
- Sprint J: Stopping rules, TODO 1 integration

Per Phase D revised plan:
- Two gap types initially: UNCERTAIN, UNEXPLORED (per Lampson)
- Source selection by domain (per Giles)
- Epsilon-greedy with decay (per Simon)
- Expanded null result vocabulary (per Cartwright)

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
