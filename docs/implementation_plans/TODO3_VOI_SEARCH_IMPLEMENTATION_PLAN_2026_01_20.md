# Implementation Plan: TODO 3 — VOI-Driven Article Search

**Date:** January 20, 2026
**Phase:** B (Implementation Plan)
**Status:** Ready for critique
**Incorporates:** Expert Panel Review 2026-01-20

---

## 1. Executive Summary

This plan details the implementation of a Value of Information-driven article search system that translates epistemic gaps in the web into effective literature search strategies. The system implements nine gap types, maintains a portfolio of search strategies, includes cross-field vocabulary expansion, and incorporates a feedback loop for continuous improvement.

**Core Design Principle (from Simon):** Satisficing with exploration—allocate search effort efficiently across gaps, balance exploitation of known strategies with exploration of new ones, and stop when marginal yield drops below threshold.

---

## 2. Architecture Overview

```
                    ┌─────────────────────────┐
                    │    Web of Belief        │
                    │    (current state)      │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Gap Identifier       │
                    │  - Scope boundaries     │
                    │  - Mechanism gaps       │
                    │  - Bridge evidence      │
                    │  - Causal identification│
                    │  - Null result needs    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    VOI Calculator       │
                    │  - Uncertainty reduction│
                    │  - Belief importance    │
                    │  - Expected yield       │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Gap Prioritizer      │
                    │  (top N by VOI)         │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────────────────┐
                    │                                   │
                    ▼                                   ▼
          ┌─────────────────┐               ┌─────────────────┐
          │  Query Generator │               │  Strategy       │
          │  (gap → queries) │               │  Selector       │
          └────────┬────────┘               │  (explore/exploit)│
                   │                        └────────┬────────┘
                   │                                 │
                   └──────────────┬─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Cross-Field Vocabulary │
                    │  Expander               │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Multi-Source Search    │
                    │  - Semantic Scholar     │
                    │  - PubMed               │
                    │  - Citation search      │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Result Ranker          │
                    │  - Relevance            │
                    │  - Quality              │
                    │  - Novelty              │
                    │  - Expected info gain   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Acquisition Report     │
                    │  - Ranked papers        │
                    │  - Search record        │
                    │  - Not-found log        │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  Feedback Loop          │
                    │  - Track utility        │
                    │  - Update strategy priors│
                    │  - Refine vocabulary    │
                    └─────────────────────────┘
```

---

## 3. Gap Types and Identification

### 3.1 Gap Type Enumeration

```python
# Location: src/services/voi_search.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Set

class GapType(Enum):
    """
    Types of epistemic gaps (expanded per Pearl, Cartwright).
    """
    # Original types
    SCOPE_BOUNDARY = "scope_boundary"           # Need evidence for different population/setting
    MECHANISM = "mechanism"                     # Need mechanism testing
    BRIDGE_EVIDENCE = "bridge_evidence"         # Need cross-theory covariance
    REPLICATION = "replication"                 # Need independent replication
    NULL_RESULT = "null_result"                 # Need calibration from null findings
    THEORY_CHALLENGE = "theory_challenge"       # Need evidence testing alternatives

    # Added per Pearl
    CAUSAL_IDENTIFICATION = "causal_identification"  # Need experimental evidence
    CONFOUNDER = "confounder"                        # Need studies controlling for confound
    MEDIATOR = "mediator"                            # Need mediator pathway tests

@dataclass
class EpistemicGap:
    """A gap in the web's knowledge."""
    gap_type: GapType
    description: str

    # Affected beliefs
    primary_belief_id: str
    related_belief_ids: List[str]

    # Gap-specific details
    details: Dict[str, Any]

    # VOI components
    uncertainty_reduction: float    # Expected reduction in uncertainty if filled
    belief_importance: float        # How central is the affected belief?
    feasibility: float              # How likely to find papers addressing this?

    # Computed
    voi_score: float = 0.0

    def compute_voi(self, search_cost: float = 0.1) -> float:
        """
        Compute Value of Information.
        VOI = P(finding) × E[uncertainty_reduction] × importance - cost
        """
        self.voi_score = (
            self.feasibility *
            self.uncertainty_reduction *
            self.belief_importance -
            search_cost
        )
        return self.voi_score
```

### 3.2 Gap Identification

```python
class GapIdentifier:
    """Identify epistemic gaps from web structure."""

    def __init__(self, web: WebOfBelief):
        self.web = web

    def identify_all_gaps(self) -> List[EpistemicGap]:
        """Identify all gaps in the web."""
        gaps = []

        gaps.extend(self._identify_scope_boundaries())
        gaps.extend(self._identify_mechanism_gaps())
        gaps.extend(self._identify_bridge_gaps())
        gaps.extend(self._identify_replication_needs())
        gaps.extend(self._identify_null_result_needs())
        gaps.extend(self._identify_causal_identification_gaps())
        gaps.extend(self._identify_confounder_gaps())

        # Compute VOI for all
        for gap in gaps:
            gap.compute_voi()

        # Sort by VOI
        gaps.sort(key=lambda g: g.voi_score, reverse=True)

        return gaps

    def _identify_scope_boundaries(self) -> List[EpistemicGap]:
        """
        Find beliefs that need evidence in unexplored populations/settings.
        Per Cartwright: Most valuable scope extensions.
        """
        gaps = []

        # Define target scopes we want coverage for
        target_populations = ["children", "elderly", "clinical", "non-WEIRD"]
        target_settings = ["field", "workplace", "healthcare", "education"]

        for belief in self.web.beliefs.values():
            if belief.level == EpistemicLevel.EMPIRICAL:
                # Check what scopes we have evidence for
                covered_pops = self._get_covered_populations(belief)
                covered_settings = self._get_covered_settings(belief)

                for pop in target_populations:
                    if pop not in covered_pops:
                        gaps.append(EpistemicGap(
                            gap_type=GapType.SCOPE_BOUNDARY,
                            description=f"Need evidence for {belief.content[:50]}... in {pop} population",
                            primary_belief_id=belief.id,
                            related_belief_ids=[],
                            details={
                                "missing_scope": "population",
                                "scope_value": pop,
                                "current_coverage": list(covered_pops)
                            },
                            uncertainty_reduction=0.15,  # Moderate reduction
                            belief_importance=self._compute_belief_importance(belief),
                            feasibility=0.4  # Scope-specific studies less common
                        ))

        return gaps

    def _identify_causal_identification_gaps(self) -> List[EpistemicGap]:
        """
        Find correlational evidence that needs experimental confirmation.
        Per Pearl: Causal knowledge is more valuable than correlational.
        """
        gaps = []

        for belief in self.web.beliefs.values():
            if belief.level == EpistemicLevel.EMPIRICAL:
                # Check if evidence is correlational
                constraints = self.web.get_constraints_for_belief(belief.id)
                has_causal_evidence = any(
                    c.causal_direction in [CausalDirection.FORWARD, CausalDirection.REVERSE]
                    for c in constraints
                )

                if not has_causal_evidence and belief.credence.value > 0.5:
                    gaps.append(EpistemicGap(
                        gap_type=GapType.CAUSAL_IDENTIFICATION,
                        description=f"Need experimental evidence for: {belief.content[:50]}...",
                        primary_belief_id=belief.id,
                        related_belief_ids=[],
                        details={
                            "current_evidence": "correlational",
                            "needed_evidence": "experimental"
                        },
                        uncertainty_reduction=0.25,  # High value for causal evidence
                        belief_importance=self._compute_belief_importance(belief),
                        feasibility=0.3  # Experiments are less common
                    ))

        return gaps

    def _identify_null_result_needs(self) -> List[EpistemicGap]:
        """
        Find beliefs that need calibration from null findings.
        Per Cartwright: Absence of evidence is evidence.
        """
        gaps = []

        for belief in self.web.beliefs.values():
            # High credence with only supporting evidence = needs null calibration
            n_supporting = belief.credence.n_supporting
            n_contradicting = belief.credence.n_contradicting

            if n_supporting >= 3 and n_contradicting == 0 and belief.credence.value > 0.7:
                gaps.append(EpistemicGap(
                    gap_type=GapType.NULL_RESULT,
                    description=f"Need null result search for calibration: {belief.content[:50]}...",
                    primary_belief_id=belief.id,
                    related_belief_ids=[],
                    details={
                        "current_supporting": n_supporting,
                        "current_contradicting": n_contradicting,
                        "concern": "Publication bias likely"
                    },
                    uncertainty_reduction=0.20,  # Calibration is valuable
                    belief_importance=self._compute_belief_importance(belief),
                    feasibility=0.2  # Null results hard to find
                ))

        return gaps

    def _compute_belief_importance(self, belief: Belief) -> float:
        """
        Compute how important/central a belief is.
        Based on connectivity, credence, and level.
        """
        # Connectivity (more constraints = more central)
        n_constraints = len(self.web.get_constraints_for_belief(belief.id))
        connectivity_score = min(n_constraints / 10, 1.0)

        # Level (theoretical more central than observational)
        level_weights = {
            EpistemicLevel.THEORETICAL: 1.0,
            EpistemicLevel.INTERMEDIATE: 0.8,
            EpistemicLevel.EMPIRICAL: 0.6,
            EpistemicLevel.OBSERVATIONAL: 0.4
        }
        level_score = level_weights.get(belief.level, 0.5)

        # Combined
        return 0.5 * connectivity_score + 0.5 * level_score
```

---

## 4. Search Strategy Portfolio

### 4.1 Strategy Definitions

```python
class SearchStrategy(Enum):
    """
    Portfolio of search strategies.
    Per Bates: Different strategies for different needs.
    """
    KEYWORD_SUBJECT = "keyword_subject"           # Standard keyword search
    KEYWORD_EXPANDED = "keyword_expanded"         # With synonym expansion
    CITATION_FORWARD = "citation_forward"         # Papers citing known relevant
    CITATION_BACKWARD = "citation_backward"       # Papers cited by known relevant
    AUTHOR_FOLLOW = "author_follow"               # Other work by relevant authors
    SEMANTIC_SIMILARITY = "semantic_similarity"   # Dense retrieval
    METHOD_FILTER = "method_filter"               # Filter by study design
    NULL_RESULT_SPECIAL = "null_result_special"   # Special queries for null results
    CROSS_FIELD = "cross_field"                   # Search adjacent fields

@dataclass
class SearchStrategyConfig:
    """Configuration for a search strategy."""
    strategy: SearchStrategy
    expected_precision: float
    expected_recall: float
    applicable_gap_types: List[GapType]
    sources: List[str]  # Which databases to query

# Strategy configurations
STRATEGY_CONFIGS = {
    SearchStrategy.KEYWORD_SUBJECT: SearchStrategyConfig(
        strategy=SearchStrategy.KEYWORD_SUBJECT,
        expected_precision=0.3,
        expected_recall=0.6,
        applicable_gap_types=[GapType.SCOPE_BOUNDARY, GapType.REPLICATION, GapType.MECHANISM],
        sources=["semantic_scholar", "pubmed"]
    ),
    SearchStrategy.CITATION_FORWARD: SearchStrategyConfig(
        strategy=SearchStrategy.CITATION_FORWARD,
        expected_precision=0.5,
        expected_recall=0.3,
        applicable_gap_types=[GapType.REPLICATION, GapType.THEORY_CHALLENGE],
        sources=["semantic_scholar"]
    ),
    SearchStrategy.NULL_RESULT_SPECIAL: SearchStrategyConfig(
        strategy=SearchStrategy.NULL_RESULT_SPECIAL,
        expected_precision=0.2,
        expected_recall=0.4,
        applicable_gap_types=[GapType.NULL_RESULT],
        sources=["semantic_scholar", "pubmed", "psyarxiv"]
    ),
    SearchStrategy.METHOD_FILTER: SearchStrategyConfig(
        strategy=SearchStrategy.METHOD_FILTER,
        expected_precision=0.4,
        expected_recall=0.3,
        applicable_gap_types=[GapType.CAUSAL_IDENTIFICATION, GapType.CONFOUNDER],
        sources=["pubmed", "semantic_scholar"]
    ),
    SearchStrategy.CROSS_FIELD: SearchStrategyConfig(
        strategy=SearchStrategy.CROSS_FIELD,
        expected_precision=0.2,
        expected_recall=0.5,
        applicable_gap_types=[GapType.BRIDGE_EVIDENCE, GapType.MECHANISM],
        sources=["semantic_scholar", "web_of_science"]
    ),
    # ... other strategies
}
```

### 4.2 Strategy Selection (Epsilon-Greedy)

```python
class StrategySelector:
    """
    Select search strategies using epsilon-greedy.
    Per Simon: Balance exploration vs exploitation.
    """

    def __init__(self, epsilon: float = 0.2):
        self.epsilon = epsilon
        self.strategy_performance: Dict[Tuple[GapType, SearchStrategy], float] = {}
        self.strategy_counts: Dict[Tuple[GapType, SearchStrategy], int] = {}

    def select_strategies(
        self,
        gap: EpistemicGap,
        n_strategies: int = 3
    ) -> List[SearchStrategy]:
        """Select strategies for a gap."""
        selected = []

        # Get applicable strategies
        applicable = [
            s for s, config in STRATEGY_CONFIGS.items()
            if gap.gap_type in config.applicable_gap_types
        ]

        for _ in range(min(n_strategies, len(applicable))):
            if random.random() < self.epsilon:
                # Explore: random strategy
                strategy = random.choice([s for s in applicable if s not in selected])
            else:
                # Exploit: best-performing strategy for this gap type
                strategy = self._get_best_strategy(gap.gap_type, applicable, selected)

            selected.append(strategy)

        return selected

    def _get_best_strategy(
        self,
        gap_type: GapType,
        applicable: List[SearchStrategy],
        exclude: List[SearchStrategy]
    ) -> SearchStrategy:
        """Get best-performing strategy for gap type."""
        candidates = [s for s in applicable if s not in exclude]

        best = None
        best_score = -1

        for strategy in candidates:
            key = (gap_type, strategy)
            if key in self.strategy_performance:
                score = self.strategy_performance[key]
            else:
                # Use prior from config
                config = STRATEGY_CONFIGS[strategy]
                score = config.expected_precision * config.expected_recall

            if score > best_score:
                best_score = score
                best = strategy

        return best or candidates[0]

    def update_performance(
        self,
        gap_type: GapType,
        strategy: SearchStrategy,
        n_relevant: int,
        n_total: int
    ):
        """Update strategy performance based on search results."""
        key = (gap_type, strategy)
        current_count = self.strategy_counts.get(key, 0)
        current_perf = self.strategy_performance.get(key, 0.5)

        # Incremental update
        precision = n_relevant / n_total if n_total > 0 else 0
        new_perf = (current_perf * current_count + precision) / (current_count + 1)

        self.strategy_performance[key] = new_perf
        self.strategy_counts[key] = current_count + 1
```

---

## 5. Query Generation

### 5.1 Query Generator

```python
class QueryGenerator:
    """Generate search queries from gaps."""

    def __init__(self, vocab: CrossFieldVocabulary):
        self.vocab = vocab

    def generate_queries(
        self,
        gap: EpistemicGap,
        strategy: SearchStrategy,
        max_queries: int = 5
    ) -> List[SearchQuery]:
        """Generate queries for a gap using a strategy."""

        generator_method = getattr(self, f"_generate_{strategy.value}", None)
        if generator_method:
            return generator_method(gap, max_queries)
        else:
            return self._generate_keyword_subject(gap, max_queries)

    def _generate_keyword_subject(self, gap: EpistemicGap, max_queries: int) -> List[SearchQuery]:
        """Standard keyword queries."""
        queries = []
        belief = self._get_primary_belief(gap)

        # Base concepts from belief
        concepts = self._extract_concepts(belief)

        # Generate query strings
        for i, concept_combo in enumerate(self._concept_combinations(concepts)):
            if i >= max_queries:
                break

            query_string = " AND ".join(f'"{c}"' for c in concept_combo)

            # Add gap-specific terms
            if gap.gap_type == GapType.SCOPE_BOUNDARY:
                scope_term = gap.details.get("scope_value", "")
                query_string = f'({query_string}) AND "{scope_term}"'

            queries.append(SearchQuery(
                query_string=query_string,
                strategy=SearchStrategy.KEYWORD_SUBJECT,
                gap_id=gap.primary_belief_id,
                expected_precision=0.3,
                expected_recall=0.5
            ))

        return queries

    def _generate_null_result_special(self, gap: EpistemicGap, max_queries: int) -> List[SearchQuery]:
        """
        Special queries for finding null results.
        Per Cartwright: Essential for calibration.
        """
        queries = []
        belief = self._get_primary_belief(gap)
        concepts = self._extract_concepts(belief)

        # Null result indicators
        null_terms = [
            '"no effect"',
            '"no significant"',
            '"failed to replicate"',
            '"did not find"',
            '"non-significant"',
            '"null result"'
        ]

        base_query = " AND ".join(f'"{c}"' for c in concepts[:2])

        for i, null_term in enumerate(null_terms):
            if i >= max_queries:
                break

            query_string = f'({base_query}) AND {null_term}'
            queries.append(SearchQuery(
                query_string=query_string,
                strategy=SearchStrategy.NULL_RESULT_SPECIAL,
                gap_id=gap.primary_belief_id,
                expected_precision=0.15,
                expected_recall=0.3
            ))

        return queries

    def _generate_method_filter(self, gap: EpistemicGap, max_queries: int) -> List[SearchQuery]:
        """
        Queries filtered by methodology.
        Per Pearl: For causal identification, need experimental studies.
        """
        queries = []
        belief = self._get_primary_belief(gap)
        concepts = self._extract_concepts(belief)

        base_query = " AND ".join(f'"{c}"' for c in concepts[:2])

        # Method terms based on gap type
        if gap.gap_type == GapType.CAUSAL_IDENTIFICATION:
            method_terms = [
                '"randomized controlled"',
                '"experiment"',
                '"randomized trial"',
                '"causal effect"',
                '"intervention study"'
            ]
        elif gap.gap_type == GapType.CONFOUNDER:
            method_terms = [
                '"controlled for"',
                '"adjusted for"',
                '"propensity score"',
                '"instrumental variable"',
                '"confound"'
            ]
        else:
            method_terms = ['"systematic review"', '"meta-analysis"']

        for i, method_term in enumerate(method_terms):
            if i >= max_queries:
                break

            query_string = f'({base_query}) AND {method_term}'
            queries.append(SearchQuery(
                query_string=query_string,
                strategy=SearchStrategy.METHOD_FILTER,
                gap_id=gap.primary_belief_id,
                expected_precision=0.35,
                expected_recall=0.25
            ))

        return queries

    def _generate_cross_field(self, gap: EpistemicGap, max_queries: int) -> List[SearchQuery]:
        """
        Cross-field queries using vocabulary expansion.
        Per Kaplan: Different fields use different terms.
        """
        queries = []
        belief = self._get_primary_belief(gap)
        concepts = self._extract_concepts(belief)

        # Expand to other fields
        for field in ["psychology", "neuroscience", "architecture"]:
            expanded_concepts = [
                self.vocab.expand_term(c, field)
                for c in concepts[:2]
            ]

            # Flatten
            expanded_flat = []
            for ec in expanded_concepts:
                expanded_flat.extend(ec)

            if expanded_flat:
                query_string = " OR ".join(f'"{t}"' for t in expanded_flat[:4])
                queries.append(SearchQuery(
                    query_string=query_string,
                    strategy=SearchStrategy.CROSS_FIELD,
                    gap_id=gap.primary_belief_id,
                    expected_precision=0.2,
                    expected_recall=0.4,
                    metadata={"target_field": field}
                ))

        return queries[:max_queries]
```

---

## 6. Cross-Field Vocabulary

### 6.1 Vocabulary Structure

```yaml
# Location: contracts/vocab/cross_field_vocabulary.yaml

version: "1.0"
fields: ["cnfa", "psychology", "neuroscience", "architecture", "healthcare"]

concepts:
  stress_recovery:
    cnfa:
      primary: "stress recovery"
      variants: ["restoration from stress", "stress reduction", "psychophysiological restoration"]
    psychology:
      primary: "relaxation response"
      variants: ["stress relief", "coping recovery", "emotional regulation"]
    neuroscience:
      primary: "autonomic restoration"
      variants: ["HPA axis recovery", "parasympathetic activation", "cortisol reduction"]
    healthcare:
      primary: "therapeutic environment"
      variants: ["healing environment", "salutogenic design", "patient recovery"]

  attention_restoration:
    cnfa:
      primary: "attention restoration"
      variants: ["directed attention recovery", "cognitive restoration", "ART"]
    psychology:
      primary: "executive function recovery"
      variants: ["mental fatigue recovery", "concentration restoration"]
    neuroscience:
      primary: "prefrontal recovery"
      variants: ["cognitive control recovery", "dorsolateral PFC restoration"]
    education:
      primary: "learning readiness"
      variants: ["focus recovery", "attention capacity"]

  natural_environment:
    cnfa:
      primary: "natural environment"
      variants: ["nature views", "biophilic elements", "green space"]
    psychology:
      primary: "restorative environment"
      variants: ["natural setting", "green exposure"]
    ecology:
      primary: "urban green space"
      variants: ["urban nature", "urban forest", "green infrastructure"]
    architecture:
      primary: "biophilic design"
      variants: ["nature-inspired design", "organic architecture"]

  # ... 17 more concepts (20 total per panel recommendation)
```

### 6.2 Vocabulary Expander

```python
class CrossFieldVocabulary:
    """Handle cross-field vocabulary expansion."""

    def __init__(self, vocab_path: str):
        self.vocab = self._load_vocab(vocab_path)
        self._build_term_index()

    def _build_term_index(self):
        """Build reverse index from terms to concepts."""
        self.term_to_concept: Dict[str, str] = {}
        self.concept_to_fields: Dict[str, Dict[str, List[str]]] = {}

        for concept_id, concept_data in self.vocab["concepts"].items():
            self.concept_to_fields[concept_id] = {}

            for field, field_data in concept_data.items():
                if isinstance(field_data, dict):
                    terms = [field_data["primary"]] + field_data.get("variants", [])
                    self.concept_to_fields[concept_id][field] = terms

                    for term in terms:
                        self.term_to_concept[term.lower()] = concept_id

    def expand_term(self, term: str, target_field: str) -> List[str]:
        """
        Expand a term to equivalents in target field.
        Per Bates: Conceptual equivalence, not just synonyms.
        """
        term_lower = term.lower()

        # Find concept
        concept_id = self.term_to_concept.get(term_lower)
        if not concept_id:
            # Try partial match
            for known_term, cid in self.term_to_concept.items():
                if term_lower in known_term or known_term in term_lower:
                    concept_id = cid
                    break

        if not concept_id:
            return [term]  # Return original if no mapping

        # Get target field terms
        field_terms = self.concept_to_fields.get(concept_id, {}).get(target_field, [])

        if field_terms:
            return field_terms
        else:
            return [term]

    def expand_query_terms(self, terms: List[str], fields: List[str]) -> Dict[str, List[str]]:
        """Expand multiple terms across multiple fields."""
        result = {}
        for field in fields:
            expanded = []
            for term in terms:
                expanded.extend(self.expand_term(term, field))
            result[field] = list(set(expanded))
        return result
```

---

## 7. Multi-Source Search

### 7.1 Search Sources

```python
from abc import ABC, abstractmethod

class SearchSource(ABC):
    """Abstract base for search sources."""

    @abstractmethod
    def search(self, query: SearchQuery, max_results: int) -> List[SearchResult]:
        pass

class SemanticScholarSource(SearchSource):
    """Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers["x-api-key"] = api_key

    def search(self, query: SearchQuery, max_results: int = 50) -> List[SearchResult]:
        """Execute search against Semantic Scholar."""
        params = {
            "query": query.query_string,
            "limit": max_results,
            "fields": "paperId,title,abstract,year,citationCount,authors,venue"
        }

        response = self.session.get(f"{self.BASE_URL}/paper/search", params=params)

        if response.status_code != 200:
            logger.error(f"Semantic Scholar search failed: {response.status_code}")
            return []

        data = response.json()
        results = []

        for paper in data.get("data", []):
            results.append(SearchResult(
                paper_id=paper["paperId"],
                title=paper.get("title", ""),
                abstract=paper.get("abstract", ""),
                year=paper.get("year"),
                citation_count=paper.get("citationCount", 0),
                authors=[a.get("name", "") for a in paper.get("authors", [])],
                source="semantic_scholar",
                query=query
            ))

        return results

class PubMedSource(SearchSource):
    """PubMed E-utilities API."""

    def search(self, query: SearchQuery, max_results: int = 50) -> List[SearchResult]:
        """Execute search against PubMed."""
        # PubMed search implementation
        ...

class SearchAggregator:
    """Aggregate searches across multiple sources."""

    def __init__(self, sources: Dict[str, SearchSource]):
        self.sources = sources

    def search(
        self,
        queries: List[SearchQuery],
        sources: List[str],
        max_results_per_query: int = 20
    ) -> List[SearchResult]:
        """Execute queries across sources and aggregate."""
        all_results = []
        seen_ids = set()

        for query in queries:
            for source_name in sources:
                if source_name in self.sources:
                    source = self.sources[source_name]
                    results = source.search(query, max_results_per_query)

                    for result in results:
                        # Deduplicate
                        if result.paper_id not in seen_ids:
                            seen_ids.add(result.paper_id)
                            all_results.append(result)

        return all_results
```

---

## 8. Result Ranking

```python
@dataclass
class RankedPaper:
    """A paper ranked by expected information value."""
    result: SearchResult
    relevance_score: float
    quality_score: float
    novelty_score: float
    expected_info_gain: float
    rank: int
    ranking_explanation: str

class ResultRanker:
    """
    Rank search results by expected information value.
    Per Giles: Not just relevance, but expected utility.
    """

    def __init__(self, web: WebOfBelief):
        self.web = web

    def rank_results(
        self,
        results: List[SearchResult],
        gap: EpistemicGap
    ) -> List[RankedPaper]:
        """Rank results for a specific gap."""
        ranked = []

        for result in results:
            relevance = self._compute_relevance(result, gap)
            quality = self._compute_quality(result)
            novelty = self._compute_novelty(result)

            # Expected information gain
            info_gain = relevance * quality * novelty

            explanation = self._generate_explanation(relevance, quality, novelty)

            ranked.append(RankedPaper(
                result=result,
                relevance_score=relevance,
                quality_score=quality,
                novelty_score=novelty,
                expected_info_gain=info_gain,
                rank=0,  # Set after sorting
                ranking_explanation=explanation
            ))

        # Sort by expected info gain
        ranked.sort(key=lambda r: r.expected_info_gain, reverse=True)

        # Assign ranks
        for i, paper in enumerate(ranked):
            paper.rank = i + 1

        return ranked

    def _compute_relevance(self, result: SearchResult, gap: EpistemicGap) -> float:
        """Compute relevance to gap."""
        # Check title/abstract for gap-relevant terms
        text = f"{result.title} {result.abstract or ''}".lower()

        gap_terms = self._get_gap_terms(gap)
        matches = sum(1 for term in gap_terms if term.lower() in text)

        return min(matches / len(gap_terms), 1.0) if gap_terms else 0.5

    def _compute_quality(self, result: SearchResult) -> float:
        """Compute paper quality estimate."""
        # Citation-based quality (log scale)
        citations = result.citation_count or 0
        citation_score = min(math.log10(citations + 1) / 3, 1.0)

        # Recency bonus
        current_year = 2026
        age = current_year - (result.year or current_year)
        recency_score = max(0, 1 - age / 20)

        return 0.6 * citation_score + 0.4 * recency_score

    def _compute_novelty(self, result: SearchResult) -> float:
        """Compute how novel this paper is to our web."""
        # Check if paper already processed
        if self._paper_in_web(result.paper_id):
            return 0.0

        # Check if authors already represented
        known_authors = self._get_known_authors()
        author_overlap = sum(1 for a in result.authors if a in known_authors)

        # Novel if few overlapping authors
        novelty = 1.0 - (author_overlap / max(len(result.authors), 1))

        return novelty

    def _generate_explanation(self, relevance: float, quality: float, novelty: float) -> str:
        """Generate human-readable ranking explanation."""
        parts = []

        if relevance > 0.7:
            parts.append("highly relevant to gap")
        elif relevance > 0.4:
            parts.append("moderately relevant")
        else:
            parts.append("tangentially relevant")

        if quality > 0.7:
            parts.append("well-cited")
        elif quality > 0.4:
            parts.append("adequately cited")

        if novelty > 0.8:
            parts.append("from new research group")

        return "; ".join(parts) if parts else "low priority"
```

---

## 9. Feedback Loop

```python
@dataclass
class AcquisitionFeedback:
    """Feedback on an acquired paper."""
    paper_id: str
    gap_id: str
    gap_type: GapType
    strategies_used: List[SearchStrategy]

    # Outcome
    was_useful: bool
    beliefs_affected: int
    credence_change_magnitude: float

    # Details
    reviewer_notes: Optional[str] = None

class FeedbackTracker:
    """
    Track search feedback for continuous improvement.
    Per Giles: Learn which strategies work.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def record_feedback(self, feedback: AcquisitionFeedback):
        """Record feedback on acquired paper."""
        ...

    def get_strategy_effectiveness(self) -> Dict[Tuple[GapType, SearchStrategy], float]:
        """Compute effectiveness of each strategy for each gap type."""
        feedbacks = self._get_all_feedbacks()

        effectiveness = {}
        counts = {}

        for fb in feedbacks:
            for strategy in fb.strategies_used:
                key = (fb.gap_type, strategy)
                current = effectiveness.get(key, 0)
                count = counts.get(key, 0)

                # Usefulness weighted by impact
                value = 1.0 if fb.was_useful else 0.0
                value *= (1 + fb.credence_change_magnitude)  # Bonus for high impact

                effectiveness[key] = (current * count + value) / (count + 1)
                counts[key] = count + 1

        return effectiveness

    def update_strategy_priors(self, selector: StrategySelector):
        """Update strategy selector with learned effectiveness."""
        effectiveness = self.get_strategy_effectiveness()

        for key, eff in effectiveness.items():
            selector.strategy_performance[key] = eff
```

---

## 10. Main Interface

```python
class VOISearchEngine:
    """Main interface for VOI-driven article search."""

    def __init__(
        self,
        web: WebOfBelief,
        vocab_path: str,
        sources: Dict[str, SearchSource]
    ):
        self.web = web
        self.vocab = CrossFieldVocabulary(vocab_path)
        self.gap_identifier = GapIdentifier(web)
        self.query_generator = QueryGenerator(self.vocab)
        self.strategy_selector = StrategySelector()
        self.search_aggregator = SearchAggregator(sources)
        self.ranker = ResultRanker(web)
        self.feedback_tracker = FeedbackTracker("search_feedback.db")

    def run_search_cycle(
        self,
        max_gaps: int = 10,
        max_papers_per_gap: int = 20
    ) -> AcquisitionReport:
        """
        Run one search cycle.
        Per Simon: Satisficing with resource budget.
        """
        # Identify and prioritize gaps
        gaps = self.gap_identifier.identify_all_gaps()[:max_gaps]

        all_recommendations = []
        search_log = []

        for gap in gaps:
            # Select strategies
            strategies = self.strategy_selector.select_strategies(gap)

            # Generate queries
            queries = []
            for strategy in strategies:
                queries.extend(self.query_generator.generate_queries(gap, strategy))

            # Execute search
            config = STRATEGY_CONFIGS[strategies[0]]
            results = self.search_aggregator.search(queries, config.sources)

            # Rank results
            ranked = self.ranker.rank_results(results, gap)[:max_papers_per_gap]

            all_recommendations.extend(ranked)

            # Log search
            search_log.append(SearchLogEntry(
                gap=gap,
                strategies=strategies,
                queries_executed=len(queries),
                results_found=len(results),
                top_ranked=ranked[:3] if ranked else []
            ))

        # Deduplicate across gaps
        all_recommendations = self._deduplicate_recommendations(all_recommendations)

        # Sort by overall expected value
        all_recommendations.sort(key=lambda r: r.expected_info_gain, reverse=True)

        return AcquisitionReport(
            recommendations=all_recommendations[:50],  # Top 50
            search_log=search_log,
            gaps_searched=len(gaps),
            total_results=sum(len(s.top_ranked) for s in search_log)
        )

    def _deduplicate_recommendations(self, recs: List[RankedPaper]) -> List[RankedPaper]:
        """Remove duplicate papers across gaps."""
        seen = set()
        unique = []
        for rec in recs:
            if rec.result.paper_id not in seen:
                seen.add(rec.result.paper_id)
                unique.append(rec)
        return unique
```

---

## 11. Sprint Plan

### Sprint B: Gap Identification and Vocabulary (2 weeks)

**Goals:**
- Implement gap identification for all 9 types
- Build cross-field vocabulary for 20 concepts
- Implement VOI calculation
- Basic query generation

**Deliverables:**
- `src/services/voi_search.py` (core)
- `src/services/cross_field_vocabulary.py`
- `contracts/vocab/cross_field_vocabulary.yaml`
- Tests for gap identification

**Decision Points to Track:**
- VOI calculation weights
- Which 20 concepts to prioritize for vocabulary
- Gap detection thresholds

### Sprint C: Search Execution (2 weeks)

**Goals:**
- Integrate Semantic Scholar API
- Integrate PubMed API
- Implement strategy selection (epsilon-greedy)
- Generate queries for all strategies

**Deliverables:**
- `src/services/search_sources.py`
- All query generation methods
- Strategy selection with exploration/exploitation
- Integration tests with real APIs

**Decision Points to Track:**
- Epsilon value for exploration
- Rate limiting approach
- How to handle API failures

### Sprint D: Ranking and Feedback (2 weeks)

**Goals:**
- Implement result ranking
- Build feedback tracking
- Create acquisition report format
- Test full pipeline

**Deliverables:**
- `src/services/result_ranker.py`
- `src/services/search_feedback.py`
- Acquisition report generation
- End-to-end tests

**Decision Points to Track:**
- Ranking weight allocation
- How to handle "no results found"
- Feedback collection UX

### Sprint E: Calibration and Iteration (2 weeks)

**Goals:**
- Run searches for 10+ gaps
- Collect feedback on recommendations
- Tune strategy effectiveness
- Evaluate search quality

**Deliverables:**
- Performance report
- Tuned strategy priors
- Vocabulary refinements
- Documentation

**Decision Points to Track:**
- Which strategies underperformed?
- Which vocabulary gaps emerged?
- What's the actual precision@10?

---

## 12. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Precision@10 | 40% | Manual relevance assessment |
| Precision@10 (cross-field) | 25% | Papers from adjacent fields |
| Gap coverage | 80% | Fraction of top-10 gaps with ≥1 relevant paper |
| Null result discovery | 5 papers/month | Papers with null findings found |
| Strategy learning | Improvement over baseline | Performance increase over 3 months |
| Vocabulary coverage | 80% of concepts | Queries successfully expanded |

---

## 13. Files to Create

```
src/services/voi_search.py              # Main engine
src/services/gap_identifier.py          # Gap identification
src/services/query_generator.py         # Query generation
src/services/cross_field_vocabulary.py  # Vocabulary expansion
src/services/search_sources.py          # API integrations
src/services/result_ranker.py           # Result ranking
src/services/search_feedback.py         # Feedback tracking
contracts/vocab/cross_field_vocabulary.yaml  # Vocabulary data
tests/test_voi_search.py
tests/test_gap_identifier.py
tests/test_vocabulary.py
docs/VOI_SEARCH_USER_GUIDE.md
```

---

*Plan ready for critique*
*Next step: Review by team + world-class system designer*
