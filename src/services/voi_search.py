"""
VOI-Driven Search for Article Eater Post-Quinean.

TODO 3: VOI-Driven Search

Sprints:
- Sprint H: Core structures, VOI scoring, source selection
- Sprint I: Strategy selection with epsilon decay, stopping rules,
            null result detection
- Sprint J: Credibility profile estimation, pipeline helpers
- Sprint K: Cross-field vocabulary integration (Lane E, 2026-02-08)

Per Phase D revised plan:
- Two gap types initially: validation and mechanism
  (legacy labels: UNCERTAIN, UNEXPLORED; per Lampson)
- Source selection by domain (per Giles)
- Epsilon-greedy with decay (per Simon)
- Expanded null result vocabulary (per Cartwright)
- Satisficing stopping rules (per Simon)
- Cross-field vocabulary for query expansion (Lane E enhancement)

Date: January 20, 2026
Updated: February 8, 2026 (Lane E: Cross-field vocabulary)
"""

import logging
import random
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pathlib import Path

import yaml

from src.services.web_of_belief import WebOfBelief, Belief

# Import canonical gap types from single source of truth
# Per Canonical Decisions Record (02-15_09), Decision 1
from src.epistemic.gap_types import (
    GapType as CanonicalGapType,
    convert_legacy_gap_type,
)

# Optional import for discovery funnel integration
try:
    from src.services.discovery_funnel import (
        DiscoveryFunnelService,
        VOIGap,
        GapType as FunnelGapType,
        GapStatus,
    )
    FUNNEL_AVAILABLE = True
except ImportError:
    FUNNEL_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# GAP TYPE COMPATIBILITY
# =============================================================================

class GapType(str, Enum):
    """
    VOI gap enum aligned to canonical GapType values.

    Legacy member names are retained as aliases for module compatibility.
    """
    VALIDATION = "validation"
    MECHANISM = "mechanism"
    DIRECTION = "direction"
    BOUNDARY = "boundary"

    # Backward-compatible aliases (same canonical values)
    UNCERTAIN = "validation"
    UNEXPLORED = "mechanism"
    CONTRADICTION = "direction"
    BOUNDARY_UNCLEAR = "boundary"


LEGACY_TO_CANONICAL_GAP_TYPE = {
    GapType.VALIDATION: CanonicalGapType.VALIDATION,
    GapType.MECHANISM: CanonicalGapType.MECHANISM,
    GapType.DIRECTION: CanonicalGapType.DIRECTION,
    GapType.BOUNDARY: CanonicalGapType.BOUNDARY,
}

CANONICAL_TO_LEGACY_GAP_TYPE = {
    CanonicalGapType.VALIDATION: GapType.VALIDATION,
    CanonicalGapType.MECHANISM: GapType.MECHANISM,
    CanonicalGapType.DIRECTION: GapType.DIRECTION,
    CanonicalGapType.BOUNDARY: GapType.BOUNDARY,
}

# Preserve historical external labels where string keys are user-visible.
CANONICAL_TO_LEGACY_LABEL = {
    GapType.VALIDATION: "uncertain",
    GapType.MECHANISM: "unexplored",
    GapType.DIRECTION: "contradiction",
    GapType.BOUNDARY: "boundary",
}


def to_canonical_gap_type(value: GapType | CanonicalGapType | str) -> CanonicalGapType:
    """Normalize VOI gap input to canonical GapType."""
    if isinstance(value, CanonicalGapType):
        return value
    if isinstance(value, GapType):
        return LEGACY_TO_CANONICAL_GAP_TYPE[value]
    return convert_legacy_gap_type(value)


def to_legacy_gap_type(value: GapType | CanonicalGapType | str) -> GapType:
    """Normalize canonical/legacy gap input to VOI module GapType."""
    if isinstance(value, GapType):
        return value
    canonical = to_canonical_gap_type(value)
    return CANONICAL_TO_LEGACY_GAP_TYPE.get(canonical, GapType.MECHANISM)


def legacy_gap_type_label(value: GapType | CanonicalGapType | str) -> str:
    """Return compatibility label used by historical VOI outputs."""
    module_gap = to_legacy_gap_type(value)
    return CANONICAL_TO_LEGACY_LABEL.get(module_gap, module_gap.value)


# =============================================================================
# CROSS-FIELD VOCABULARY (Sprint K - Lane E)
# =============================================================================

class CrossFieldVocabulary:
    """
    Loads and provides access to cross-field vocabulary mappings.

    Enables translation of CNfA concepts to terminology in adjacent fields.
    This allows search queries to find relevant literature across disciplines
    that use different terminology for related concepts.

    Example:
        vocab = CrossFieldVocabulary()
        terms = vocab.expand_query("stress recovery")
        # Returns: ["stress recovery", "psychophysiological recovery",
        #           "relaxation response", "HPA axis recovery", ...]
    """

    def __init__(self, vocab_path: Optional[Path] = None):
        """
        Initialize vocabulary loader.

        Args:
            vocab_path: Path to cross_field_vocabulary.yaml.
                       Uses default location if None.
        """
        if vocab_path is None:
            vocab_path = Path(__file__).parent.parent.parent / \
                        "contracts" / "vocab" / "cross_field_vocabulary.yaml"

        self.vocab_path = vocab_path
        self.concepts: Dict[str, Dict] = {}
        self.query_templates: Dict[str, Dict] = {}
        self.fields: Dict[str, Dict] = {}

        self._load_vocabulary()

    def _load_vocabulary(self) -> None:
        """Load vocabulary from YAML file."""
        if not self.vocab_path.exists():
            logger.warning(f"Cross-field vocabulary not found: {self.vocab_path}")
            return

        try:
            with open(self.vocab_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load vocabulary: {e}")
            return

        # Load concepts
        for key, value in data.items():
            if key in ('version', 'created', 'description',
                       'query_templates', 'fields', 'measurement_methods'):
                continue
            if isinstance(value, dict) and 'canonical_term' in value:
                self.concepts[key] = value

        self.query_templates = data.get('query_templates', {})
        self.fields = data.get('fields', {})
        logger.info(f"Loaded {len(self.concepts)} cross-field concepts")

    def get_all_terms(self, concept: str) -> List[str]:
        """
        Get all terms (across all fields) for a concept.

        Args:
            concept: Concept identifier (e.g., "stress_recovery")

        Returns:
            List of all equivalent terms across fields
        """
        if concept not in self.concepts:
            return [concept]

        all_terms = []
        concept_data = self.concepts[concept]

        for key, value in concept_data.items():
            if key.endswith('_terms') and isinstance(value, list):
                all_terms.extend(value)

        return list(set(all_terms))

    def get_field_terms(self, concept: str, field: str) -> List[str]:
        """
        Get terms for a concept in a specific field.

        Args:
            concept: Concept identifier
            field: Field name (e.g., "neuroscience", "architecture")

        Returns:
            List of terms used in that field
        """
        if concept not in self.concepts:
            return [concept]

        field_key = f"{field}_terms"
        return self.concepts[concept].get(field_key, [])

    def expand_query(
        self,
        base_term: str,
        target_fields: Optional[List[str]] = None,
        max_terms: int = 5
    ) -> List[str]:
        """
        Expand a term to include synonyms from target fields.

        This is the primary method for cross-field query expansion.

        Args:
            base_term: The CNfA term to expand
            target_fields: Fields to include (None = all)
            max_terms: Maximum terms to return

        Returns:
            List of equivalent terms across fields
        """
        # Find matching concept by searching all terms
        matching_concept = None
        for concept_name, concept_data in self.concepts.items():
            all_terms = self.get_all_terms(concept_name)
            if base_term.lower() in [t.lower() for t in all_terms]:
                matching_concept = concept_name
                break

        if not matching_concept:
            return [base_term]

        if target_fields:
            terms = []
            for field in target_fields:
                terms.extend(self.get_field_terms(matching_concept, field))
            result = list(set(terms)) if terms else [base_term]
        else:
            result = self.get_all_terms(matching_concept)

        # Ensure base term is first in results (important for truncation)
        result_lower = [r.lower() for r in result]
        if base_term.lower() in result_lower:
            # Remove it from current position and put at front
            idx = result_lower.index(base_term.lower())
            original_term = result[idx]
            result = [original_term] + result[:idx] + result[idx+1:]
        else:
            result = [base_term] + result

        return result[:max_terms]

    def get_journals_for_field(self, field: str) -> List[str]:
        """Get relevant journals for a field."""
        if field in self.fields:
            return self.fields[field].get('journals', [])
        return []

    def find_concept(self, term: str) -> Optional[str]:
        """
        Find which concept a term belongs to.

        Args:
            term: Term to look up

        Returns:
            Concept name or None if not found
        """
        term_lower = term.lower()
        for concept_name, concept_data in self.concepts.items():
            all_terms = self.get_all_terms(concept_name)
            if term_lower in [t.lower() for t in all_terms]:
                return concept_name
        return None


# Singleton instance for convenience
_vocabulary_instance: Optional[CrossFieldVocabulary] = None


def get_cross_field_vocabulary() -> CrossFieldVocabulary:
    """Get or create singleton vocabulary instance."""
    global _vocabulary_instance
    if _vocabulary_instance is None:
        _vocabulary_instance = CrossFieldVocabulary()
    return _vocabulary_instance


# =============================================================================
# CORE DATA STRUCTURES (per Lampson)
# =============================================================================

# Per P-VOI Panel (Thagard): Gap types have different VOI priorities
# Contradictions actively hurt coherence until resolved
# NOTE: Exposed using canonical values with compatibility aliases.
GAP_TYPE_PRIORITY_WEIGHTS = {
    GapType.DIRECTION: 1.0,   # Highest priority - active harm
    GapType.VALIDATION: 0.7,       # High uncertainty needs resolution
    GapType.MECHANISM: 0.5,      # Missing evidence
    GapType.BOUNDARY: 0.4,  # Scope clarification
}


@dataclass
class EpistemicGap:
    """
    Represents a knowledge gap that could be addressed by searching
    for additional literature.

    VOI Semantics (per P-VOI Panel 2026-02-09):
    - 'voi_score' means Expected Epistemic Gain (EEG), not classical VOI
    - Computed as weighted combination of structural and epistemic factors
    - Bounded/satisficing computation, not theoretical maximum

    Per Howard: The "decision" being informed is "which paper to read next"
    Per Pearl: Structural and epistemic VOI should be tracked separately
    Per Thagard: Gap type determines priority weighting
    """
    gap_type: GapType
    description: str
    primary_belief_id: str
    voi_score: float  # Expected Epistemic Gain (0-1) - legacy name for compatibility

    # Per P-VOI Panel: Separate structural from epistemic VOI
    structural_voi: float = 0.0   # Value from filling structural gap (counterfactual coherence)
    epistemic_voi: float = 0.0    # Value from reducing uncertainty

    def to_search_context(self) -> Dict[str, Any]:
        """Context for query generation."""
        return {
            "gap_type": legacy_gap_type_label(self.gap_type),
            "belief_id": self.primary_belief_id,
            "description": self.description,
            "voi_score": self.voi_score
        }

    def to_funnel_gap(
        self,
        web_id: Optional[str] = None,
        theory_id: Optional[str] = None,
        search_terms: Optional[List[str]] = None
    ) -> Optional["VOIGap"]:
        """
        Convert to discovery funnel VOIGap.

        Args:
            web_id: Web of belief ID
            theory_id: Theory this gap relates to
            search_terms: Suggested search terms

        Returns:
            VOIGap object if funnel is available, None otherwise
        """
        if not FUNNEL_AVAILABLE:
            logger.debug("Discovery funnel not available, skipping gap registration")
            return None

        # Map VOI gap types to discovery funnel gap types.
        gap_type_map = {
            GapType.VALIDATION: FunnelGapType.VALIDATION,
            GapType.MECHANISM: FunnelGapType.MECHANISM,
            GapType.DIRECTION: FunnelGapType.DIRECTION,
            GapType.BOUNDARY: FunnelGapType.BOUNDARY,
        }

        return VOIGap(
            gap_id=str(uuid.uuid4()),
            topic=self.description,
            gap_type=gap_type_map.get(self.gap_type, FunnelGapType.MECHANISM),
            predicted_voi=self.voi_score,
            belief_id=self.primary_belief_id,
            theory_id=theory_id,
            web_id=web_id,
            search_terms=search_terms or [],
            identified_by="voi_search",
        )


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

    Per P-VOI Panel (2026-02-09):
    - VOI = Expected Epistemic Gain (EEG), bounded/satisficing computation
    - Separates structural VOI (counterfactual coherence) from epistemic VOI (uncertainty)
    - Gap type determines α weighting between structural and epistemic
    - Centrality affects propagation factor for structural changes

    Panelists: Howard, Pearl, Simon, Thagard, Haack, Bates
    """

    # Per P-VOI Panel: Alpha determines structural vs epistemic weighting
    # Based on gap type - structural gaps weight structural VOI higher
    # NOTE: Uses canonical values with legacy aliases.
    ALPHA_BY_GAP_TYPE = {
        GapType.MECHANISM: 0.7,       # Missing evidence = structural
        GapType.VALIDATION: 0.4,        # Uncertainty = epistemic
        GapType.DIRECTION: 0.5,    # Equal weight - both matter
        GapType.BOUNDARY: 0.3,  # Scope = more epistemic
    }

    def calculate_voi(
        self,
        gap_type: GapType,
        belief: Belief,
        web: Optional[WebOfBelief] = None
    ) -> Tuple[float, float, float]:
        """
        Calculate VOI score for a gap.

        Per P-VOI Panel (Pearl):
        - Structural VOI = counterfactual coherence improvement
        - Epistemic VOI = uncertainty reduction × belief importance
        - Combined with α weighting based on gap type

        Args:
            gap_type: Type of gap
            belief: The belief associated with the gap
            web: Optional web for centrality calculation

        Returns:
            Tuple of (combined_voi, structural_voi, epistemic_voi)
        """
        # Calculate structural VOI (per Pearl)
        structural_voi = self._structural_voi(gap_type, belief, web)

        # Calculate epistemic VOI
        epistemic_voi = self._epistemic_voi(belief)

        # Combine with alpha weighting (per panel)
        alpha = self.ALPHA_BY_GAP_TYPE.get(gap_type, 0.5)
        base_voi = alpha * structural_voi + (1 - alpha) * epistemic_voi

        # Apply gap type priority weight (per Thagard)
        priority_weight = GAP_TYPE_PRIORITY_WEIGHTS.get(gap_type, 0.5)
        combined_voi = min(base_voi * priority_weight, 1.0)

        return combined_voi, structural_voi, epistemic_voi

    def _structural_voi(
        self,
        gap_type: GapType,
        belief: Belief,
        web: Optional[WebOfBelief] = None
    ) -> float:
        """
        Structural VOI: value from filling a structural gap.

        Per Pearl: Counterfactual coherence improvement.
        Approximated by centrality × sparsity (how much would filling help).
        """
        # Centrality component (how connected is this belief?)
        if web:
            centrality = self._centrality_component(belief, web)
        else:
            centrality = 0.5  # Default if no web

        # Sparsity component (how little evidence do we have?)
        sparsity = self._sparsity_component(gap_type, belief)

        # Structural VOI = how much impact would filling this have?
        # High centrality + high sparsity = high structural value
        return (centrality * 0.6 + sparsity * 0.4)

    def _epistemic_voi(self, belief: Belief) -> float:
        """
        Epistemic VOI: value from reducing uncertainty.

        Per Panel: uncertainty_reduction × belief_importance
        """
        uncertainty = self._uncertainty_component(belief)

        # Belief importance based on epistemic level
        level_importance = {
            "theoretical": 0.9,
            "intermediate": 0.7,
            "empirical": 0.5,
            "observational": 0.4,
        }
        importance = level_importance.get(
            getattr(belief, 'level', 'empirical'),
            0.5
        )

        return uncertainty * importance

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
        if gap_type == GapType.MECHANISM:
            # Mechanism gaps have high sparsity by definition (was UNEXPLORED)
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
    Enhanced with cross-field vocabulary expansion (Sprint K).
    """

    def __init__(self, vocabulary: Optional[CrossFieldVocabulary] = None):
        """
        Initialize query generator.

        Args:
            vocabulary: Cross-field vocabulary for query expansion.
                       Uses singleton if None.
        """
        self.vocabulary = vocabulary or get_cross_field_vocabulary()

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
        if gap.gap_type == GapType.VALIDATION:
            # For validation gaps (was UNCERTAIN), look for replication/meta-analysis
            if belief:
                key_terms = self._extract_terms(belief.content)[:3]
                queries.append(" ".join(key_terms + ["meta-analysis"]))
                queries.append(" ".join(key_terms + ["replication"]))

        elif gap.gap_type == GapType.MECHANISM:
            # For mechanism gaps (was UNEXPLORED), look for any evidence
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

    def generate_cross_field_queries(
        self,
        gap: EpistemicGap,
        belief: Optional[Belief] = None,
        target_fields: Optional[List[str]] = None,
        max_queries: int = 5
    ) -> List[str]:
        """
        Generate queries with cross-field vocabulary expansion.

        Sprint K (Lane E): Uses the cross-field vocabulary to find
        papers in adjacent disciplines using different terminology.

        Args:
            gap: The epistemic gap
            belief: Optional belief for context
            target_fields: Fields to target (None = all)
            max_queries: Maximum queries to generate

        Returns:
            List of cross-field expanded queries
        """
        queries = []

        # Extract key terms
        base_terms = self._extract_terms(gap.description)
        if belief:
            base_terms.extend(self._extract_terms(belief.content)[:3])

        # Default fields for CNfA
        if target_fields is None:
            target_fields = ['psychology', 'neuroscience', 'architecture', 'medicine']

        # Expand each key term across fields
        for term in base_terms[:3]:
            expanded = self.vocabulary.expand_query(term, target_fields)
            if expanded and len(expanded) > 1:
                # Create OR query with expanded terms
                or_terms = " OR ".join([f'"{t}"' for t in expanded[:4]])
                queries.append(f"({or_terms})")

        # Field-specific queries
        for field in target_fields:
            field_queries = []
            for term in base_terms[:2]:
                field_terms = self.vocabulary.get_field_terms(
                    self.vocabulary.find_concept(term) or term,
                    field
                )
                if field_terms:
                    field_queries.extend(field_terms[:2])

            if field_queries:
                query = " AND ".join([f'"{t}"' for t in field_queries[:3]])
                queries.append(query)

        # Deduplicate
        seen = set()
        unique = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique.append(q)

        return unique[:max_queries]

    def expand_query_terms(
        self,
        query: str,
        target_fields: Optional[List[str]] = None
    ) -> List[str]:
        """
        Expand a query with cross-field terminology.

        Args:
            query: Original query string
            target_fields: Fields to target

        Returns:
            List of expanded query variants
        """
        expanded = [query]

        # Extract quoted terms
        import re
        quoted = re.findall(r'"([^"]+)"', query)

        for term in quoted:
            synonyms = self.vocabulary.expand_query(term, target_fields)
            for syn in synonyms[:2]:
                if syn.lower() != term.lower():
                    variant = query.replace(f'"{term}"', f'"{syn}"')
                    if variant not in expanded:
                        expanded.append(variant)

        return expanded


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
            # Check for validation gap (was "uncertain gap")
            if belief.credence.uncertainty > self.UNCERTAINTY_THRESHOLD:
                # Per P-VOI Panel: calculate_voi now returns (combined, structural, epistemic)
                combined_voi, structural_voi, epistemic_voi = self.voi_calculator.calculate_voi(
                    GapType.VALIDATION, belief, web
                )
                gaps.append(EpistemicGap(
                    gap_type=GapType.VALIDATION,
                    description=f"High uncertainty ({belief.credence.uncertainty:.0%}) on: {belief.content[:50]}...",
                    primary_belief_id=belief_id,
                    voi_score=combined_voi,
                    structural_voi=structural_voi,
                    epistemic_voi=epistemic_voi
                ))

            # Check for mechanism gap (was "unexplored gap")
            n_papers = len(belief.paper_ids) if belief.paper_ids else 0
            if n_papers < self.MIN_SUPPORTING_STUDIES:
                # Per P-VOI Panel: calculate_voi now returns (combined, structural, epistemic)
                combined_voi, structural_voi, epistemic_voi = self.voi_calculator.calculate_voi(
                    GapType.MECHANISM, belief, web
                )
                gaps.append(EpistemicGap(
                    gap_type=GapType.MECHANISM,
                    description=f"Only {n_papers} supporting studies for: {belief.content[:50]}...",
                    primary_belief_id=belief_id,
                    voi_score=combined_voi,
                    structural_voi=structural_voi,
                    epistemic_voi=epistemic_voi
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

    With discovery funnel integration (DISC-2), gaps can be automatically
    registered in the funnel for tracking through the full discovery pipeline.
    """

    def __init__(
        self,
        web: WebOfBelief,
        gap_detector: Optional[GapDetector] = None,
        source_selector: Optional[SourceSelector] = None,
        query_generator: Optional[QueryGenerator] = None,
        funnel_service: Optional["DiscoveryFunnelService"] = None,
        track_in_funnel: bool = False,
        web_id: Optional[str] = None
    ):
        """
        Initialize VOI search coordinator.

        Args:
            web: Web of belief to analyze
            gap_detector: Gap detection service
            source_selector: Source selection service
            query_generator: Query generation service
            funnel_service: Optional discovery funnel service for tracking
            track_in_funnel: Whether to register gaps in the funnel
            web_id: Web ID for funnel tracking
        """
        self.web = web
        self.gap_detector = gap_detector or GapDetector()
        self.source_selector = source_selector or SourceSelector()
        self.query_generator = query_generator or QueryGenerator()

        # Discovery funnel integration
        self.funnel_service = funnel_service
        self.track_in_funnel = track_in_funnel and FUNNEL_AVAILABLE
        self.web_id = web_id

        if self.track_in_funnel and not self.funnel_service:
            logger.warning("track_in_funnel=True but no funnel_service provided")

    def identify_search_priorities(
        self,
        max_gaps: int = 5,
        register_in_funnel: Optional[bool] = None
    ) -> List[EpistemicGap]:
        """
        Identify highest-priority gaps for search.

        Args:
            max_gaps: Maximum gaps to return
            register_in_funnel: Override track_in_funnel setting

        Returns:
            List of EpistemicGap objects sorted by VOI score
        """
        gaps = self.gap_detector.detect_gaps(self.web, max_gaps)

        # Register gaps in funnel if enabled
        should_register = register_in_funnel if register_in_funnel is not None else self.track_in_funnel
        if should_register and self.funnel_service:
            self._register_gaps_in_funnel(gaps)

        return gaps

    def _register_gaps_in_funnel(self, gaps: List[EpistemicGap]) -> List[str]:
        """
        Register gaps in the discovery funnel.

        Args:
            gaps: List of epistemic gaps to register

        Returns:
            List of funnel gap IDs
        """
        if not self.funnel_service or not FUNNEL_AVAILABLE:
            return []

        registered_ids = []
        for gap in gaps:
            # Get belief for context
            belief = self.web.beliefs.get(gap.primary_belief_id)
            theory_id = getattr(belief, 'theory_id', None) if belief else None

            # Generate search terms from the gap
            search_terms = self.query_generator.generate_queries(gap, belief, max_queries=3)

            # Convert to funnel gap
            funnel_gap = gap.to_funnel_gap(
                web_id=self.web_id,
                theory_id=theory_id,
                search_terms=search_terms
            )

            if funnel_gap:
                # Get sources for target_sources field
                sources = self.source_selector.select_sources(gap, belief)
                funnel_gap.target_sources = sources

                try:
                    self.funnel_service.create_gap(funnel_gap)
                    registered_ids.append(funnel_gap.gap_id)
                    logger.info(f"Registered gap in funnel: {funnel_gap.gap_id} - {funnel_gap.topic[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to register gap in funnel: {e}")

        return registered_ids

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
        max_gaps: int = 10,
        register_in_funnel: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Export search priorities for external processing.

        Args:
            output_path: Optional path to write JSON
            max_gaps: Maximum gaps to include
            register_in_funnel: Whether to register gaps in discovery funnel

        Returns:
            Dict with gaps and search plans
        """
        # Pass register_in_funnel to identify_search_priorities
        gaps = self.identify_search_priorities(max_gaps, register_in_funnel=register_in_funnel)

        result = {
            'n_gaps': len(gaps),
            'funnel_tracking': self.track_in_funnel and self.funnel_service is not None,
            'web_id': self.web_id,
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
    Strategy selection with adaptive exploration.

    Per P-VOI Panel (Simon, 2026-02-09):
    - Epsilon decay should be SUCCESS-ADAPTIVE, not fixed decay
    - Exploration increases when searches fail (need to try new approaches)
    - Exploration decreases when searches succeed (exploit what works)
    - This is bounded rationality: adjust strategy based on feedback
    """

    def __init__(
        self,
        initial_epsilon: float = 0.3,
        min_epsilon: float = 0.05,
        max_epsilon: float = 0.5,
        success_threshold_low: float = 0.2,
        success_threshold_high: float = 0.6,
        lookback_window: int = 5
    ):
        """
        Initialize strategy selector with adaptive epsilon.

        Per P-VOI Panel (Simon): Adaptive exploration based on recent success.

        Args:
            initial_epsilon: Initial exploration rate (0-1)
            min_epsilon: Minimum exploration rate (never go below)
            max_epsilon: Maximum exploration rate (never go above)
            success_threshold_low: Below this, increase exploration
            success_threshold_high: Above this, decrease exploration
            lookback_window: Number of recent searches to consider
        """
        self.initial_epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.max_epsilon = max_epsilon
        self.success_threshold_low = success_threshold_low
        self.success_threshold_high = success_threshold_high
        self.lookback_window = lookback_window

        self._current_epsilon = initial_epsilon
        self.total_searches = 0

        # Track strategy performance by gap type
        self._strategy_successes: Dict[Tuple[GapType, SearchStrategy], int] = {}
        self._strategy_attempts: Dict[Tuple[GapType, SearchStrategy], int] = {}

        # Per P-VOI Panel: Track recent search outcomes for adaptive epsilon
        self._recent_outcomes: List[bool] = []

    @property
    def epsilon(self) -> float:
        """Current epsilon (adapts based on recent success)."""
        return self._current_epsilon

    def _update_epsilon(self) -> None:
        """
        Update epsilon based on recent search success.

        Per P-VOI Panel (Simon):
        - If recent success rate < 0.2: explore more (try new strategies)
        - If recent success rate > 0.6: exploit more (use what works)
        - Otherwise: maintain current balance
        """
        if len(self._recent_outcomes) < 3:
            return  # Not enough data yet

        recent_success_rate = sum(self._recent_outcomes[-self.lookback_window:]) / \
                              min(len(self._recent_outcomes), self.lookback_window)

        if recent_success_rate < self.success_threshold_low:
            # Searches failing - explore more
            self._current_epsilon = min(self._current_epsilon * 1.2, self.max_epsilon)
            logger.debug(f"Epsilon increased to {self._current_epsilon:.3f} (success rate: {recent_success_rate:.2f})")
        elif recent_success_rate > self.success_threshold_high:
            # Searches succeeding - exploit more
            self._current_epsilon = max(self._current_epsilon * 0.95, self.min_epsilon)
            logger.debug(f"Epsilon decreased to {self._current_epsilon:.3f} (success rate: {recent_success_rate:.2f})")

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

        Per P-VOI Panel (Simon): Also updates adaptive epsilon.

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

        # Per P-VOI Panel: Track for adaptive epsilon
        self._recent_outcomes.append(success)
        if len(self._recent_outcomes) > self.lookback_window * 2:
            self._recent_outcomes = self._recent_outcomes[-self.lookback_window:]

        # Update epsilon based on recent success
        self._update_epsilon()

    def get_stats(self) -> Dict[str, Any]:
        """Get strategy performance statistics."""
        stats = {
            'total_searches': self.total_searches,
            'current_epsilon': self.epsilon,
            'strategy_performance': {}
        }

        for (gap_type, strategy), attempts in self._strategy_attempts.items():
            successes = self._strategy_successes.get((gap_type, strategy), 0)
            key = f"{legacy_gap_type_label(gap_type)}_{strategy.value}"
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
        if not relevant_categories:
            relevant_categories = relevance.get(legacy_gap_type_label(gap_type), [])

        for category in detection['categories_detected']:
            if category in relevant_categories:
                boost += 0.2

        return min(boost, 2.5)  # Cap at 2.5x


# =============================================================================
# SPRINT J: TODO 1 INTEGRATION (Credibility Expectations)
# =============================================================================

class CredibilityProfileEstimator:
    """
    Estimate credibility profile for search results.

    Helps prioritize papers less likely to be rejected by TODO 1.
    """

    # Expected issue probabilities by study type
    STUDY_TYPE_PROFILES = {
        "meta-analysis": {
            "sample_size_issue": 0.05,
            "scope_issue": 0.15,
            "causal_direction_issue": 0.10,
            "expected_credibility": 0.85
        },
        "systematic_review": {
            "sample_size_issue": 0.10,
            "scope_issue": 0.20,
            "causal_direction_issue": 0.15,
            "expected_credibility": 0.80
        },
        "rct": {
            "sample_size_issue": 0.15,
            "scope_issue": 0.25,
            "causal_direction_issue": 0.05,
            "expected_credibility": 0.75
        },
        "longitudinal": {
            "sample_size_issue": 0.20,
            "scope_issue": 0.20,
            "causal_direction_issue": 0.15,
            "expected_credibility": 0.70
        },
        "cross_sectional": {
            "sample_size_issue": 0.25,
            "scope_issue": 0.30,
            "causal_direction_issue": 0.40,
            "expected_credibility": 0.55
        },
        "case_study": {
            "sample_size_issue": 0.60,
            "scope_issue": 0.50,
            "causal_direction_issue": 0.30,
            "expected_credibility": 0.40
        },
        "unknown": {
            "sample_size_issue": 0.35,
            "scope_issue": 0.35,
            "causal_direction_issue": 0.35,
            "expected_credibility": 0.50
        }
    }

    def estimate_profile(
        self,
        title: str,
        abstract: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Estimate credibility profile from paper metadata.

        Args:
            title: Paper title
            abstract: Optional abstract text

        Returns:
            Dict with issue probabilities and expected credibility
        """
        text = f"{title} {abstract or ''}".lower()
        study_type = self._infer_study_type(text)

        profile = self.STUDY_TYPE_PROFILES.get(
            study_type,
            self.STUDY_TYPE_PROFILES["unknown"]
        ).copy()

        # Adjust based on content indicators
        profile = self._adjust_for_content(profile, text)

        return profile

    def _infer_study_type(self, text: str) -> str:
        """Infer study type from text."""
        if "meta-analysis" in text or "meta analysis" in text:
            return "meta-analysis"
        elif "systematic review" in text:
            return "systematic_review"
        elif "randomized controlled" in text or "randomised controlled" in text or "rct" in text:
            return "rct"
        elif "longitudinal" in text or "follow-up" in text or "prospective" in text:
            return "longitudinal"
        elif "case study" in text or "case report" in text:
            return "case_study"
        elif "cross-sectional" in text or "survey" in text:
            return "cross_sectional"
        else:
            return "unknown"

    def _adjust_for_content(
        self,
        profile: Dict[str, float],
        text: str
    ) -> Dict[str, float]:
        """Adjust profile based on content indicators."""
        adjusted = profile.copy()

        # Positive indicators
        if "large sample" in text or "n = " in text or "n=" in text:
            adjusted["sample_size_issue"] *= 0.7
            adjusted["expected_credibility"] = min(adjusted["expected_credibility"] + 0.05, 1.0)

        if "replication" in text:
            adjusted["expected_credibility"] = min(adjusted["expected_credibility"] + 0.1, 1.0)

        if "pre-registered" in text or "preregistered" in text:
            adjusted["expected_credibility"] = min(adjusted["expected_credibility"] + 0.1, 1.0)

        # Negative indicators
        if "pilot" in text or "preliminary" in text:
            adjusted["expected_credibility"] *= 0.9

        if "small sample" in text or "limited sample" in text:
            adjusted["sample_size_issue"] = min(adjusted["sample_size_issue"] + 0.2, 1.0)
            adjusted["expected_credibility"] *= 0.85

        return adjusted


# =============================================================================
# SPRINT J: PIPELINE INTEGRATION
# =============================================================================

def create_search_plan_for_web(
    web: WebOfBelief,
    max_gaps: int = 5,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Pipeline helper: Create comprehensive search plan for a web.

    Args:
        web: Web of belief to analyze
        max_gaps: Maximum gaps to include
        output_path: Optional path to write JSON

    Returns:
        Dict with prioritized gaps and search plans
    """
    coordinator = VOISearchCoordinator(web)
    return coordinator.export_search_priorities(output_path, max_gaps)


def estimate_search_value(
    web: WebOfBelief,
    max_gaps: int = 10
) -> Dict[str, Any]:
    """
    Pipeline helper: Estimate total value of searching.

    Returns summary of potential knowledge gain from searching.

    Args:
        web: Web of belief
        max_gaps: Maximum gaps to consider

    Returns:
        Dict with search value estimates
    """
    gaps = detect_gaps(web, max_gaps)

    if not gaps:
        return {
            'n_gaps': 0,
            'total_voi': 0.0,
            'average_voi': 0.0,
            'gap_type_breakdown': {},
            'recommendation': 'No significant gaps identified.'
        }

    total_voi = sum(g.voi_score for g in gaps)
    avg_voi = total_voi / len(gaps)

    # Breakdown by type
    type_counts = {}
    type_voi = {}
    for gap in gaps:
        gap_type = legacy_gap_type_label(gap.gap_type)
        type_counts[gap_type] = type_counts.get(gap_type, 0) + 1
        type_voi[gap_type] = type_voi.get(gap_type, 0.0) + gap.voi_score

    # Generate recommendation
    if avg_voi > 0.6:
        recommendation = 'High value: Strongly recommend searching for new literature.'
    elif avg_voi > 0.4:
        recommendation = 'Moderate value: Consider searching for specific gaps.'
    else:
        recommendation = 'Low value: Current evidence may be sufficient.'

    return {
        'n_gaps': len(gaps),
        'total_voi': total_voi,
        'average_voi': avg_voi,
        'gap_type_breakdown': {
            t: {'count': type_counts[t], 'total_voi': type_voi[t]}
            for t in type_counts
        },
        'recommendation': recommendation
    }


def prioritize_recommendations(
    recommendations: List[SearchRecommendation],
    gap: EpistemicGap,
    null_detector: Optional[NullResultDetector] = None
) -> List[SearchRecommendation]:
    """
    Pipeline helper: Prioritize recommendations with credibility and null boosts.

    Args:
        recommendations: List of search recommendations
        gap: The gap being addressed
        null_detector: Optional null result detector

    Returns:
        Recommendations sorted by adjusted priority
    """
    estimator = CredibilityProfileEstimator()
    null_detector = null_detector or NullResultDetector()

    scored = []
    for rec in recommendations:
        # Base score from relevance
        score = rec.relevance_score

        # Add credibility profile
        profile = estimator.estimate_profile(rec.title)
        rec.expected_credibility_profile = profile

        # Boost by expected credibility
        score *= (0.5 + 0.5 * profile['expected_credibility'])

        # Boost for null results
        null_boost = null_detector.get_search_boost(rec.title, gap.gap_type)
        score *= null_boost

        scored.append((rec, score))

    # Sort by adjusted score
    scored.sort(key=lambda x: x[1], reverse=True)

    return [rec for rec, _ in scored]


def export_todo3_summary(
    web: WebOfBelief,
    output_path: str
) -> Dict[str, Any]:
    """
    Pipeline helper: Export comprehensive TODO 3 summary.

    Creates a JSON file with all search-related analysis.

    Args:
        web: Web of belief
        output_path: Path to write JSON

    Returns:
        Summary dict
    """
    # Get gaps and value estimate
    value_estimate = estimate_search_value(web)
    gaps = detect_gaps(web, max_gaps=10)

    # Generate search plans
    coordinator = VOISearchCoordinator(web)
    plans = []
    for gap in gaps:
        plan = coordinator.generate_search_plan(gap)
        plans.append(plan)

    summary = {
        'value_estimate': value_estimate,
        'n_gaps': len(gaps),
        'search_plans': plans,
        'metadata': {
            'generated_by': 'TODO 3: VOI-Driven Search',
            'version': '1.0'
        }
    }

    import json
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    return summary


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_voi_coordinator(
    web: WebOfBelief,
    track_in_funnel: bool = False,
    db_path: str = "ae.db",
    web_id: Optional[str] = None
) -> VOISearchCoordinator:
    """
    Create a VOI search coordinator with optional funnel tracking.

    Args:
        web: Web of belief to analyze
        track_in_funnel: Whether to register gaps in discovery funnel
        db_path: Database path for funnel service
        web_id: Web ID for funnel tracking

    Returns:
        Configured VOISearchCoordinator
    """
    funnel_service = None
    if track_in_funnel and FUNNEL_AVAILABLE:
        funnel_service = DiscoveryFunnelService(db_path)

    return VOISearchCoordinator(
        web=web,
        funnel_service=funnel_service,
        track_in_funnel=track_in_funnel,
        web_id=web_id
    )


def detect_gaps(web: WebOfBelief, max_gaps: int = 10) -> List[EpistemicGap]:
    """Quick function to detect gaps in a web."""
    detector = GapDetector()
    return detector.detect_gaps(web, max_gaps)


def calculate_voi(
    gap_type: GapType,
    belief: Belief,
    web: Optional[WebOfBelief] = None
) -> float:
    """
    Calculate VOI for a specific gap.

    Per P-VOI Panel (2026-02-09): Returns the combined Expected Epistemic Gain.
    For separated structural/epistemic VOI, use VOICalculator directly.
    """
    calculator = VOICalculator()
    combined, _, _ = calculator.calculate_voi(gap_type, belief, web)
    return combined


def identify_and_track_gaps(
    web: WebOfBelief,
    max_gaps: int = 10,
    db_path: str = "ae.db",
    web_id: Optional[str] = None
) -> Tuple[List[EpistemicGap], List[str]]:
    """
    Identify gaps and register them in the discovery funnel.

    This is the primary integration point between VOI search and
    the discovery funnel. Gaps are identified, scored, and registered
    for tracking through the full discovery pipeline.

    Args:
        web: Web of belief to analyze
        max_gaps: Maximum gaps to identify
        db_path: Database path for funnel service
        web_id: Web ID for funnel tracking

    Returns:
        Tuple of (list of EpistemicGap, list of funnel gap IDs)
    """
    if not FUNNEL_AVAILABLE:
        # Fall back to basic gap detection without funnel
        detector = GapDetector()
        gaps = detector.detect_gaps(web, max_gaps)
        return gaps, []

    coordinator = create_voi_coordinator(
        web=web,
        track_in_funnel=True,
        db_path=db_path,
        web_id=web_id
    )

    gaps = coordinator.identify_search_priorities(max_gaps, register_in_funnel=True)

    # Get the funnel gap IDs that were registered
    funnel_ids = []
    if coordinator.funnel_service:
        funnel_gaps = coordinator.funnel_service.list_gaps(limit=max_gaps)
        funnel_ids = [g.gap_id for g in funnel_gaps]

    return gaps, funnel_ids
