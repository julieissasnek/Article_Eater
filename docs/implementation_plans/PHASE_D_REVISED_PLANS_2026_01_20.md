# Phase D: Revised Implementation Plans

**Date:** January 20, 2026
**Phase:** D (Replan Based on Critique)
**Incorporates:** Phase C critique from Lampson, Pearl, Cartwright, Simon, Bates, Mayo, Wilson, Giles, Kaplan

---

## Executive Summary of Changes

The Phase C critique identified six must-fix issues and numerous should-fix items. This document presents revised plans addressing all must-fix issues and the highest-priority should-fix items.

### Key Changes Applied

| Critique | Resolution |
|----------|------------|
| Premature abstraction | Reduced enums to ≤3 initial categories |
| Interface complexity | Minimal interfaces (3-5 fields) |
| State management ambiguity | Snapshot isolation specified |
| Feedback loop complexity | Unified feedback store |
| Missing failure modes | Top 3 per component documented |
| Testing vs metrics confusion | Separated into four categories |

---

## Part I: Architectural Decisions (All TODOs)

### 1.1 Concurrency Model: Snapshot Isolation

All three TODOs will operate on web snapshots, not the live web.

```python
# Location: src/services/web_of_belief.py (addition)

@dataclass
class WebSnapshot:
    """Immutable snapshot of web state for consistent reads."""
    snapshot_id: str
    timestamp: datetime
    beliefs: Dict[str, Belief]  # Frozen copy
    constraints: List[Constraint]  # Frozen copy

    @classmethod
    def from_web(cls, web: WebOfBelief) -> 'WebSnapshot':
        """Create snapshot from current web state."""
        return cls(
            snapshot_id=f"snap_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            beliefs=copy.deepcopy(web.beliefs),
            constraints=copy.deepcopy(list(web.constraints))
        )

# Usage in TODOs:
# snapshot = WebSnapshot.from_web(web)
# credibility_tester.evaluate(snapshot, extracted)  # Works on snapshot
# interpreter.explain(snapshot, belief_id)  # Works on snapshot
# gap_identifier.identify_all(snapshot)  # Works on snapshot
```

**Decision recorded:** All read operations use snapshots. Only the pipeline's commit step modifies the live web.

### 1.2 Unified Feedback Store

Single feedback store for all three TODOs.

```python
# Location: src/services/feedback_store.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Literal

@dataclass
class SystemFeedback:
    """Unified feedback record for all system operations."""
    feedback_id: str
    timestamp: datetime
    component: Literal["credibility", "explanation", "search"]
    operation_id: str  # Links to specific check/explanation/search

    # Core outcome
    outcome: Literal["positive", "negative", "neutral", "deferred"]

    # Component-specific details (flexible)
    details: Dict[str, Any]

    # For reviewer
    reviewer_notes: Optional[str] = None

class FeedbackStore:
    """Unified storage for all system feedback."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def record(self, feedback: SystemFeedback):
        """Record feedback."""
        ...

    def get_by_component(self, component: str) -> List[SystemFeedback]:
        """Get all feedback for a component."""
        ...

    def cross_component_analysis(self) -> Dict[str, Any]:
        """Analyze patterns across components."""
        # E.g., "Do credibility-flagged papers correlate with low search utility?"
        ...
```

**Decision recorded:** One SQLite database (`system_feedback.db`) instead of three.

### 1.3 Simplified Type Hierarchies

**Original enums → Simplified versions:**

| TODO | Original | Simplified (Phase 1) |
|------|----------|---------------------|
| TODO 1 | 12 FlagTypes, 3 Severities | 2 categories: BLOCK, REVIEW |
| TODO 2 | 7 ExplanationPatterns, 4 UserModes | 2 patterns: EVIDENCE, PRACTICAL |
| TODO 3 | 9 GapTypes, 9 Strategies | 2 gap types: UNCERTAIN, UNEXPLORED |

Expansion criteria: Add new category only when ≥10 cases don't fit existing categories.

---

## Part II: TODO 1 Revised — Credibility Testing

### 2.1 Simplified Data Structures

```python
# Location: src/services/credibility_testing.py

from dataclasses import dataclass
from typing import Literal, Optional

class Decision(Enum):
    """Two-category initial system (per Lampson)."""
    BLOCK = "block"      # Cannot proceed automatically
    REVIEW = "review"    # Flag for human review
    # ACCEPT is implicit (no flags = accept)

@dataclass
class CredibilityFlag:
    """Simplified flag structure."""
    decision: Decision
    reason: str
    confidence: float  # How sure are we this is a problem?

    # Minimal details
    field_name: Optional[str] = None
    expected: Optional[str] = None
    observed: Optional[str] = None

@dataclass
class CredibilityReport:
    """Minimal interface (per Lampson)."""
    article_id: str
    flags: List[CredibilityFlag]
    overall_decision: Decision  # Worst flag wins

    def to_explanation_context(self) -> Dict[str, Any]:
        """Interface for TODO 2 integration."""
        return {
            "article_id": self.article_id,
            "decision": self.overall_decision.value,
            "reasons": [f.reason for f in self.flags],
            "n_flags": len(self.flags)
        }
```

### 2.2 Study Design Strength (Pearl)

```python
# Per Pearl: Don't reject correlational studies outright
# Instead, check if claimed strength exceeds warranted strength

DESIGN_STRENGTH = {
    "correlational": 0.4,  # Can support weak associations
    "longitudinal": 0.5,   # Temporal precedence helps
    "quasi_experiment": 0.7,
    "natural_experiment": 0.8,
    "rct": 1.0
}

def check_causal_warrant(
    constraint: Constraint,
    study_design: str,
    claimed_strength: float
) -> Optional[CredibilityFlag]:
    """Check if causal claim exceeds design's warrant."""
    max_warranted = DESIGN_STRENGTH.get(study_design, 0.5)

    if claimed_strength > max_warranted + 0.1:  # 10% tolerance
        return CredibilityFlag(
            decision=Decision.REVIEW,
            reason=f"Causal claim strength ({claimed_strength:.0%}) exceeds "
                   f"study design warrant ({max_warranted:.0%} for {study_design})",
            confidence=0.7,
            field_name="causal_direction",
            expected=f"≤{max_warranted:.0%}",
            observed=f"{claimed_strength:.0%}"
        )
    return None
```

### 2.3 Scope Distance (Cartwright)

```python
# Per Cartwright: Scope overreach depends on distance, not binary

POPULATION_CATEGORIES = {
    "specific_clinical": 1,  # e.g., "ADHD children"
    "demographic_subset": 2,  # e.g., "elderly", "students"
    "cultural_specific": 3,   # e.g., "Japanese", "Western"
    "general_adult": 4,       # e.g., "adults"
    "universal": 5            # No population specified
}

def scope_distance(sample_pop: str, claimed_scope: Optional[str]) -> float:
    """Compute how far claim extends beyond sample."""
    sample_level = _classify_population(sample_pop)
    claim_level = POPULATION_CATEGORIES.get(claimed_scope, 5) if claimed_scope else 5

    distance = claim_level - sample_level
    return max(0, distance) / 4  # Normalize to 0-1

def check_scope_overreach(
    belief: Belief,
    sample_description: str
) -> Optional[CredibilityFlag]:
    """Flag if scope extends too far beyond sample."""
    distance = scope_distance(sample_description, belief.scope.population)

    if distance > 0.5:  # More than 2 levels
        return CredibilityFlag(
            decision=Decision.REVIEW,
            reason=f"Scope may extend beyond sample ({sample_description})",
            confidence=0.6 + 0.2 * distance,  # More confident for larger distances
            field_name="scope",
            expected=f"Scope matching sample: {sample_description}",
            observed=f"Scope: {belief.scope.population or 'universal'}"
        )
    return None
```

### 2.4 Failure Modes (per Lampson)

| Failure Mode | Behavior | Logging |
|--------------|----------|---------|
| Gold Standard empty | Use conservative defaults (flag more), warn | WARNING level |
| Check throws exception | Catch, record as REVIEW flag, continue | ERROR level |
| Extraction missing fields | Skip checks requiring that field, note | INFO level |

```python
def safe_check(check_fn: Callable, *args) -> List[CredibilityFlag]:
    """Wrapper that handles check failures gracefully."""
    try:
        return check_fn(*args)
    except Exception as e:
        logger.error(f"Check {check_fn.__name__} failed: {e}")
        return [CredibilityFlag(
            decision=Decision.REVIEW,
            reason=f"Check failed: {check_fn.__name__} ({type(e).__name__})",
            confidence=0.3
        )]
```

### 2.5 Subtle Failure Cases (Mayo)

Added to Failure Standard corpus:

```yaml
# Location: gold_standard/failure_standard/manifest.yaml (additions)

subtle_failures:
  - id: "fail_subtle_subgroup_n"
    description: "N=200 total but critical comparison is N=45 subgroup"
    expected_behavior: "flag_for_review"

  - id: "fail_subtle_effect_metric"
    description: "Cohen's d reported but Hedges' g calculation used"
    expected_behavior: "flag_for_review"

  - id: "fail_subtle_ci_zero"
    description: "CI spans zero but reported as marginally significant"
    expected_behavior: "flag_for_review"

  - id: "fail_subtle_multiple_comparison"
    description: "15 comparisons, 2 significant, no correction"
    expected_behavior: "flag_for_review"
```

### 2.6 Calibration Procedure (Simon)

```python
def calibrate_thresholds(
    gold_standard: List[ProcessedArticle],
    expert_labels: Dict[str, str],  # article_id -> "ok" | "problem"
    target_sensitivity: float = 0.8
) -> Dict[str, float]:
    """
    Explicit calibration procedure (per Simon).

    Steps:
    1. Run all checks with very low thresholds
    2. Compare flags to expert labels
    3. Compute ROC curves
    4. Select thresholds at target sensitivity
    """
    thresholds = {}

    for check_name in CHECK_FUNCTIONS:
        # Sweep threshold from 0 to 1
        thresholds_tested = np.linspace(0, 1, 50)
        sensitivities = []
        specificities = []

        for thresh in thresholds_tested:
            tp, fp, tn, fn = 0, 0, 0, 0
            for article in gold_standard:
                flagged = check_name(article, threshold=thresh)
                is_problem = expert_labels[article.id] == "problem"

                if flagged and is_problem: tp += 1
                elif flagged and not is_problem: fp += 1
                elif not flagged and not is_problem: tn += 1
                else: fn += 1

            sens = tp / (tp + fn) if (tp + fn) > 0 else 0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0
            sensitivities.append(sens)
            specificities.append(spec)

        # Find threshold achieving target sensitivity
        for i, sens in enumerate(sensitivities):
            if sens >= target_sensitivity:
                thresholds[check_name] = thresholds_tested[i]
                logger.info(f"{check_name}: threshold={thresholds_tested[i]:.3f} "
                           f"achieves sensitivity={sens:.0%}, specificity={specificities[i]:.0%}")
                break

    return thresholds
```

### 2.7 Revised Sprint Plan

**Sprint B (2 weeks):**
- Implement simplified two-category system (BLOCK, REVIEW)
- Implement core checks: numeric validity, self-contradiction, causal warrant
- Create basic Failure Standard (5 obvious + 5 subtle cases)
- Unit tests for each check function

**Sprint C (2 weeks):**
- Add scope distance check
- Add effect size plausibility
- Expand Failure Standard (20 cases)
- Integration tests with pipeline

**Sprint D (2 weeks):**
- Run calibration procedure
- Document thresholds with rationale
- Evaluation metrics (precision, recall on test set)
- Prepare for handoff to TODO 2

---

## Part III: TODO 2 Revised — Interpretive Intelligence

### 3.1 Simplified Data Structures

```python
# Location: src/services/interpretive_intelligence.py

class ExplanationPattern(Enum):
    """Two patterns initially (per Lampson)."""
    EVIDENCE = "evidence"      # What supports this belief?
    PRACTICAL = "practical"    # What should I do with this?
    # Add more only when these can't answer common questions

class DetailLevel(Enum):
    """Separated from expertise (per Simon)."""
    SUMMARY = 1     # One paragraph
    STANDARD = 2    # Full explanation
    COMPREHENSIVE = 3  # All details

class ExpertiseLevel(Enum):
    """Separated from detail (per Simon)."""
    NOVICE = 1       # Define technical terms
    PRACTITIONER = 2  # Assume domain knowledge
    RESEARCHER = 3    # Assume methodological sophistication

@dataclass
class ExplanationRequest:
    """Minimal request structure."""
    pattern: ExplanationPattern
    belief_id: str
    detail: DetailLevel = DetailLevel.STANDARD
    expertise: ExpertiseLevel = ExpertiseLevel.PRACTITIONER

@dataclass
class ExplanationResponse:
    """Minimal response structure."""
    success: bool
    explanation: str
    identified_gaps: List[str] = field(default_factory=list)  # For TODO 3 integration
```

### 3.2 Question Clarification (Wilson)

```python
class QuestionClassifier:
    """Classify questions with confidence thresholding."""

    PATTERN_KEYWORDS = {
        ExplanationPattern.EVIDENCE: ["evidence", "support", "studies", "research", "proof"],
        ExplanationPattern.PRACTICAL: ["should", "recommend", "design", "apply", "use"]
    }

    def classify(self, question: str) -> Tuple[ExplanationPattern, float]:
        """Classify question and return confidence."""
        q_lower = question.lower()
        scores = {}

        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            scores[pattern] = score

        best_pattern = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best_pattern] / total if total > 0 else 0.5

        return best_pattern, confidence

    def classify_or_clarify(self, question: str) -> Union[ExplanationPattern, ClarifyingQuestion]:
        """Return pattern or ask for clarification (per Wilson)."""
        pattern, confidence = self.classify(question)

        if confidence < 0.6:
            return ClarifyingQuestion(
                prompt="What kind of answer are you looking for?",
                options=[
                    ("Evidence summary", ExplanationPattern.EVIDENCE),
                    ("Design recommendations", ExplanationPattern.PRACTICAL)
                ]
            )

        return pattern

@dataclass
class ClarifyingQuestion:
    """Question to ask user when classification uncertain."""
    prompt: str
    options: List[Tuple[str, ExplanationPattern]]
```

### 3.3 Credibility Integration

```python
class InterpretiveEngine:
    """Main interface with credibility integration."""

    def explain_credibility_decision(
        self,
        report: CredibilityReport,
        detail: DetailLevel = DetailLevel.STANDARD
    ) -> str:
        """
        Explain why a paper was flagged (integration with TODO 1).
        """
        context = report.to_explanation_context()

        if detail == DetailLevel.SUMMARY:
            return f"This paper was {context['decision']} due to {context['n_flags']} concerns: " + \
                   ", ".join(context['reasons'][:2])

        elif detail == DetailLevel.STANDARD:
            lines = [f"## Credibility Assessment: {context['decision'].upper()}"]
            lines.append(f"\n{context['n_flags']} concerns were identified:\n")
            for i, reason in enumerate(context['reasons'], 1):
                lines.append(f"{i}. {reason}")
            return "\n".join(lines)

        else:  # COMPREHENSIVE
            # Include all details, methodology notes, etc.
            ...
```

### 3.4 Gap Identification for TODO 3

```python
@dataclass
class IdentifiedGap:
    """Gap discovered during explanation (feeds TODO 3)."""
    gap_type: str  # "uncertain" or "unexplored" initially
    description: str
    belief_id: str
    priority: float  # Higher = more important to fill

class InterpretiveEngine:

    def explain(self, request: ExplanationRequest) -> ExplanationResponse:
        """Generate explanation, noting gaps found."""
        # ... existing explanation logic ...

        # Identify gaps while explaining
        gaps = self._identify_gaps_during_explanation(belief)

        return ExplanationResponse(
            success=True,
            explanation=explanation_text,
            identified_gaps=[g.description for g in gaps]
        )

    def _identify_gaps_during_explanation(self, belief: Belief) -> List[IdentifiedGap]:
        """Find gaps relevant to this belief."""
        gaps = []

        # High uncertainty
        if belief.credence.uncertainty > 0.3:
            gaps.append(IdentifiedGap(
                gap_type="uncertain",
                description=f"High uncertainty ({belief.credence.uncertainty:.0%}) - need more evidence",
                belief_id=belief.id,
                priority=belief.credence.uncertainty
            ))

        # Few supporting studies
        if belief.credence.n_supporting < 3:
            gaps.append(IdentifiedGap(
                gap_type="unexplored",
                description=f"Only {belief.credence.n_supporting} supporting studies",
                belief_id=belief.id,
                priority=0.5 / max(belief.credence.n_supporting, 1)
            ))

        return gaps
```

### 3.5 Failure Modes

| Failure Mode | Behavior | Logging |
|--------------|----------|---------|
| Vocabulary bridge no mapping | Use original term, flag for bridge expansion | INFO level |
| Template rendering fails | Return plain text summary | ERROR level |
| Belief not found | Return helpful error message | WARNING level |

```python
def safe_render(template: Template, context: Dict) -> str:
    """Wrapper for template rendering."""
    try:
        return template.render(**context)
    except Exception as e:
        logger.error(f"Template render failed: {e}")
        # Fallback to plain text
        return f"Information about {context.get('belief', 'unknown')}: " + \
               str(context.get('evidence_summary', 'Details unavailable'))
```

### 3.6 Revised Sprint Plan

**Sprint E (2 weeks):**
- Implement Evidence pattern
- Build vocabulary bridge (20 concepts)
- Question classification with clarification
- Unit tests for pattern traversal

**Sprint F (2 weeks):**
- Implement Practical pattern
- Add credibility explanation integration
- Gap identification during explanation
- Integration tests

**Sprint G (2 weeks):**
- Template refinement based on internal review
- Add COMPREHENSIVE detail level
- Documentation
- Handoff preparation for TODO 3

---

## Part IV: TODO 3 Revised — VOI-Driven Search

### 4.1 Simplified Data Structures

```python
# Location: src/services/voi_search.py

class GapType(Enum):
    """Two types initially (per Lampson)."""
    UNCERTAIN = "uncertain"     # High uncertainty on existing belief
    UNEXPLORED = "unexplored"   # Topic area with sparse coverage
    # Add CAUSAL, SCOPE, etc. when we have ≥10 cases each

@dataclass
class EpistemicGap:
    """Minimal gap structure."""
    gap_type: GapType
    description: str
    primary_belief_id: str
    voi_score: float  # Value of information

    def to_search_context(self) -> Dict[str, Any]:
        """Context for query generation."""
        return {
            "gap_type": self.gap_type.value,
            "belief_id": self.primary_belief_id,
            "description": self.description
        }

@dataclass
class SearchRecommendation:
    """Minimal recommendation structure."""
    paper_id: str
    title: str
    relevance_score: float
    ranking_explanation: str
```

### 4.2 Source Selection (Giles)

```python
# Per Giles: Different sources for different domains

SOURCE_BY_DOMAIN = {
    "neuroscience": ["pubmed", "semantic_scholar"],
    "psychology": ["semantic_scholar", "pubmed", "psycinfo"],
    "architecture": ["semantic_scholar", "avery_index"],
    "healthcare": ["pubmed", "cochrane"],
    "education": ["eric", "semantic_scholar"],
    "default": ["semantic_scholar"]
}

def select_sources(gap: EpistemicGap, belief: Belief) -> List[str]:
    """Choose sources based on belief's domain."""
    # Infer domain from belief's taxonomy IDs
    domain = _infer_domain(belief)
    return SOURCE_BY_DOMAIN.get(domain, SOURCE_BY_DOMAIN["default"])

def _infer_domain(belief: Belief) -> str:
    """Infer domain from belief content and IDs."""
    content_lower = belief.content.lower()

    if any(term in content_lower for term in ["cortisol", "amygdala", "brain"]):
        return "neuroscience"
    elif any(term in content_lower for term in ["patient", "hospital", "clinical"]):
        return "healthcare"
    elif any(term in content_lower for term in ["building", "space", "design"]):
        return "architecture"
    else:
        return "psychology"  # Default for CNfA
```

### 4.3 Epsilon Decay (Simon)

```python
class StrategySelector:
    """Strategy selection with decaying exploration."""

    def __init__(self, initial_epsilon: float = 0.3, min_epsilon: float = 0.05, decay: float = 0.99):
        self.initial_epsilon = initial_epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay
        self.total_searches = 0

    @property
    def epsilon(self) -> float:
        """Current epsilon (decays with experience)."""
        return max(
            self.initial_epsilon * (self.decay ** self.total_searches),
            self.min_epsilon
        )

    def select_strategy(self, gap: EpistemicGap) -> str:
        """Select strategy with epsilon-greedy + decay."""
        if random.random() < self.epsilon:
            # Explore: random strategy
            return random.choice(["keyword", "citation"])
        else:
            # Exploit: best known strategy for this gap type
            return self._best_strategy_for(gap.gap_type)

    def record_search(self, success: bool):
        """Record search outcome, increment counter."""
        self.total_searches += 1
        # Also update strategy performance...
```

### 4.4 Expanded Null Result Vocabulary (Cartwright)

```yaml
# Location: contracts/vocab/null_result_indicators.yaml

null_result_vocabulary:
  direct_null:
    - "no effect"
    - "no significant"
    - "null result"
    - "no difference"

  replication_failure:
    - "failed to replicate"
    - "did not replicate"
    - "replication failure"
    - "unsuccessful replication"

  hedged_null:
    - "not robust"
    - "did not reach significance"
    - "marginally significant"
    - "trending but not significant"

  contrary_to_hypothesis:
    - "contrary to hypotheses"
    - "unexpected null"
    - "surprising absence"
    - "hypothesis not supported"

  methodological_null:
    - "underpowered"
    - "insufficient power"
    - "wide confidence interval"

# Weights for search priority
category_weights:
  direct_null: 1.0
  replication_failure: 0.9
  hedged_null: 0.7
  contrary_to_hypothesis: 0.8
  methodological_null: 0.6
```

### 4.5 Stopping Rule

```python
def should_stop_searching(
    gap: EpistemicGap,
    results_so_far: List[SearchRecommendation],
    queries_executed: int,
    max_queries: int = 20,
    min_relevance: float = 0.3
) -> Tuple[bool, str]:
    """
    Determine if we should stop searching for this gap.
    Per Simon: satisficing with diminishing returns.
    """
    # Hard limit
    if queries_executed >= max_queries:
        return True, f"Reached query limit ({max_queries})"

    # Sufficient results
    relevant_results = [r for r in results_so_far if r.relevance_score >= min_relevance]
    if len(relevant_results) >= 10:
        return True, f"Found sufficient relevant papers ({len(relevant_results)})"

    # Diminishing returns
    if queries_executed >= 5:
        recent_yield = sum(1 for r in results_so_far[-10:] if r.relevance_score >= min_relevance)
        if recent_yield == 0:
            return True, "No relevant papers in last 10 results (diminishing returns)"

    return False, "Continue searching"
```

### 4.6 Integration with TODO 1 Expectations

```python
@dataclass
class SearchRecommendation:
    """Extended with credibility expectations."""
    paper_id: str
    title: str
    relevance_score: float
    ranking_explanation: str

    # For TODO 1 integration
    expected_credibility_profile: Dict[str, float] = field(default_factory=dict)

def estimate_credibility_profile(result: SearchResult) -> Dict[str, float]:
    """
    Estimate likelihood of credibility issues before processing.
    Helps prioritize papers less likely to be rejected.
    """
    profile = {}

    # Sample size indicator
    abstract = (result.abstract or "").lower()
    if any(term in abstract for term in ["n=", "participants", "sample"]):
        profile["has_sample_info"] = 0.8
    else:
        profile["has_sample_info"] = 0.3

    # Study design indicator
    if any(term in abstract for term in ["randomized", "experiment", "rct"]):
        profile["experimental"] = 0.7
    elif any(term in abstract for term in ["survey", "correlational", "observational"]):
        profile["experimental"] = 0.2
    else:
        profile["experimental"] = 0.4

    # Effect size indicator
    if any(term in abstract for term in ["effect size", "cohen", "d="]):
        profile["has_effect_size"] = 0.7
    else:
        profile["has_effect_size"] = 0.3

    return profile
```

### 4.7 Failure Modes

| Failure Mode | Behavior | Logging |
|--------------|----------|---------|
| API down | Use cached results if available, skip source | ERROR level |
| Zero results for gap | Log as "no_papers_found", suggest vocabulary expansion | WARNING level |
| Rate limited | Exponential backoff, max 3 retries | INFO level |

```python
async def search_with_fallback(
    source: SearchSource,
    query: SearchQuery,
    cache: ResultCache
) -> List[SearchResult]:
    """Search with caching and error handling."""
    # Try cache first
    cached = cache.get(query.query_string, source.name)
    if cached:
        logger.info(f"Using cached results for {source.name}")
        return cached

    # Try live search with retries
    for attempt in range(3):
        try:
            results = await source.search(query)
            cache.store(query.query_string, source.name, results)
            return results
        except RateLimitError:
            wait = 2 ** attempt
            logger.info(f"Rate limited, waiting {wait}s")
            await asyncio.sleep(wait)
        except APIError as e:
            logger.error(f"{source.name} API error: {e}")
            break

    # Fallback to cache or empty
    return cache.get(query.query_string, source.name) or []
```

### 4.8 Revised Sprint Plan

**Sprint H (2 weeks):**
- Implement two-category gap identification (UNCERTAIN, UNEXPLORED)
- Build cross-field vocabulary (20 concepts)
- Basic query generation
- Unit tests

**Sprint I (2 weeks):**
- Integrate Semantic Scholar API
- Implement strategy selection with epsilon decay
- Source selection by domain
- Integration tests

**Sprint J (2 weeks):**
- Implement result ranking
- Add stopping rules
- Create feedback tracking (using unified store)
- End-to-end tests

**Sprint K (2 weeks):**
- Calibration runs
- Vocabulary refinement
- Integration with TODO 1 expectations
- Documentation

---

## Part V: Integration Architecture

### 5.1 Cross-TODO Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web of Belief                            │
│                     (snapshot isolation)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    TODO 1       │  │    TODO 2       │  │    TODO 3       │
│   Credibility   │  │  Interpretive   │  │   VOI Search    │
│    Testing      │  │  Intelligence   │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                   │                   │
         │    ┌──────────────┘                   │
         │    │  explain_credibility()           │
         │    ▼                                  │
         │  ┌─────────────────────┐              │
         │  │ Credibility flags   │              │
         │  │ → explanations      │              │
         │  └─────────────────────┘              │
         │                                       │
         │           ┌───────────────────────────┘
         │           │  identified_gaps
         │           ▼
         │  ┌─────────────────────┐
         │  │ Explanation gaps    │
         │  │ → search priorities │
         │  └─────────────────────┘
         │                   │
         │                   │  expected_credibility_profile
         │◄──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Unified Feedback Store                      │
│                    (system_feedback.db)                         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Integration Interfaces

```python
# src/services/integration.py

# TODO 1 → TODO 2
@dataclass
class CredibilityExplanationContext:
    """What TODO 2 needs from TODO 1."""
    article_id: str
    decision: str
    reasons: List[str]

# TODO 2 → TODO 3
@dataclass
class IdentifiedSearchGap:
    """What TODO 3 needs from TODO 2."""
    gap_type: str
    description: str
    belief_id: str
    priority: float

# TODO 3 → TODO 1
@dataclass
class CredibilityExpectations:
    """What TODO 1 should expect from TODO 3's papers."""
    paper_id: str
    has_sample_info: float
    likely_experimental: float
    has_effect_size: float
```

---

## Part VI: Revised Timeline

```
Phase B-D:  Sprints B-D  (6 weeks)  - TODO 1: Credibility Testing
Phase E-G:  Sprints E-G  (6 weeks)  - TODO 2: Interpretive Intelligence
Phase H-K:  Sprints H-K  (8 weeks)  - TODO 3: VOI Search
Phase L:    Sprint L     (2 weeks)  - Integration Testing

Total: 22 weeks (~5.5 months)
```

### Milestones

| Week | Milestone |
|------|-----------|
| 6 | TODO 1 complete, credibility testing operational |
| 12 | TODO 2 complete, explanations working |
| 20 | TODO 3 complete, search operational |
| 22 | Integration complete, full system operational |

---

## Part VII: Revised Success Criteria

### TODO 1: Credibility Testing
- [ ] Two-category system (BLOCK, REVIEW) operational
- [ ] Thresholds documented with calibration data
- [ ] Subtle failure cases detected (≥80% of Failure Standard)
- [ ] Failure modes handled gracefully
- [ ] Integration interface to TODO 2 working

### TODO 2: Interpretive Intelligence
- [ ] Two patterns (EVIDENCE, PRACTICAL) answering 80% of queries
- [ ] Question clarification for uncertain classifications
- [ ] Credibility explanation integration working
- [ ] Gap identification feeding TODO 3
- [ ] Detail and expertise levels separated

### TODO 3: VOI Search
- [ ] Two gap types (UNCERTAIN, UNEXPLORED) identifying real gaps
- [ ] Source selection by domain
- [ ] Epsilon decaying with experience
- [ ] Stopping rule preventing wasted queries
- [ ] Credibility expectations feeding TODO 1

### Cross-TODO
- [ ] Unified feedback store operational
- [ ] Snapshot isolation working
- [ ] Integration interfaces tested
- [ ] End-to-end pipeline functional

---

*Revised plans complete*
*Next step: Phase E — Implement*
