# Article Recommendation Sources: Detailed Inventory

**Date**: March 2, 2026
**Purpose**: Complete inventory of all sources that generate article search recommendations

---

## Quick Reference Matrix

| Source | Module | Status | Lines | Generates | Calls Queue | VOI Used | User-Specific |
|--------|--------|--------|-------|-----------|-------------|----------|---------------|
| QA System | arbitrary_qa_handler.py | STUB | 51.8 KB | Follow-ups | No | No | No |
| Interpretation Space | overseer_management.py | ASPIRATIONAL | N/A | [Undefined] | [Undefined] | [Assumed] | No |
| Gap Predictor | gap_predictor.py | REAL | 1582 | PredictedGap | Yes | Hardcoded 0.5 | No |
| VOI Scorer | voi_search.py | REAL | 1945 | SearchRecommendation | Optional | Yes | No |
| Discovery Funnel | discovery_funnel.py | TRACKING | N/A | Gap Status | No | Reads only | No |
| Automated Searcher | automated_searcher.py | REAL | 188 | Search Results | Integrated | Optional | No |

---

## Source A: QA System (arbitrary_qa_handler.py)

### Overview
- **Status**: STUB (generates suggestions, not integrated)
- **Size**: 51.8 KB
- **Purpose**: Handles arbitrary user questions about system knowledge
- **Creates recommendations**: Yes (follow-up suggestions)
- **Feeds into queue**: No

### Implementation Details

**Entry point**:
```python
class ArbitraryQAHandler:
    def answer(self, question: str) -> Dict[str, Any]:
        # Classifies question → routes to handler → returns response
```

**Question classification**:
- catalog: "show me all theories"
- evidence: "what evidence supports X?"
- comparison: "how do A and B differ?"
- mechanism: "what's the mechanism?"
- definition: "what is X?"
- meta: questions about the system itself

**Response structure**:
```python
{
    "headline": str,
    "summary": str,
    "details": [list],
    "confidence": float,
    "follow_ups": [
        {"question": str, "type": str}
    ]
}
```

**Follow-ups generated**:
```python
# Line 690: Follow-up suggestion
"follow_ups": [
    {
        "question": "What evidence supports these recommendations?",
        "type": "deeper"
    }
]
```

**Integration with article search**:
- **No integration**: Follow-ups are suggestions for further questioning
- **Not actionable**: No mechanism to trigger article search from follow-ups
- **Reactive only**: Responds to user questions, doesn't proactively recommend

### Why It's a STUB

1. No code path converts follow-up suggestions to article recommendations
2. No queue integration
3. No VOI scoring
4. No distinction between researcher types
5. Serves Q&A function only

---

## Source B: Interpretation Space (overseer_management.py)

### Overview
- **Status**: ASPIRATIONAL (infrastructure assumed but doesn't exist)
- **Location**: overseer_management.py, lines 518-649
- **Purpose**: Monitor whether gap-derived suggestions are being acted upon
- **Creates recommendations**: Assumed yes, but undefined
- **Feeds into queue**: Assumed, but no code

### What Code Expects

**SearchSuggestionTracker class**:
```python
def check_suggestion_backlog(self) -> SuggestionBacklogReport:
    """
    Monitor unacted suggestions from 4 sources.
    """
    cursor.execute("""
        SELECT COUNT(*) FROM interpretation_space_suggestions
        WHERE status = 'proposed' OR status = 'identified'
    """)
```

**Queries by source**:
```sql
SUM(CASE WHEN source = 'argumentation' THEN 1 ELSE 0 END) as arg,
SUM(CASE WHEN source = 'voi' THEN 1 ELSE 0 END) as voi,
SUM(CASE WHEN source = 'qa' THEN 1 ELSE 0 END) as qa,
SUM(CASE WHEN source = 'interpretation_space' THEN 1 ELSE 0 END) as interp,
```

**Expected schema**:
```sql
CREATE TABLE interpretation_space_suggestions (
    id INTEGER PRIMARY KEY,
    source TEXT,              -- 'argumentation', 'voi', 'qa', 'interpretation_space', 'other'
    status TEXT,              -- 'proposed', 'identified', 'acted_upon', 'closed'
    created_at TEXT,          -- ISO timestamp
    description TEXT,         -- Gap description
    suggested_search TEXT,    -- Query to execute
    [other fields...]
)
```

### What Actually Exists

**Interpretation space data directory**:
```
data/interpretation_space/
├─ phase2/          # Phase 2 outputs
├─ phase3/          # Phase 3 outputs
├─ phase4/          # Phase 4 outputs
├─ interrogation_results_raw.json
├─ interrogation_evaluations.json
├─ followup_questions.json
└─ README.md
```

**No SQL table** created anywhere in codebase
**No insertion code** populates these records
**No integration** from phase2-4 outputs to database

### Why It's ASPIRATIONAL

1. **Table doesn't exist** — referenced but never created
2. **No population mechanism** — interpretation_space outputs are JSON/markdown files offline
3. **Comments acknowledge uncertainty**: "Assumes: interpretation_space_suggestions or similar table"
4. **Overseer gracefully degrades** — catches exception if table missing
5. **No wiring** between interpretation_space phase outputs and queue

---

## Source C: Gap Predictor (gap_predictor.py)

### Overview
- **Status**: REAL (fully functional, integrated)
- **Size**: 1582 lines
- **Purpose**: Predict knowledge gaps from argument structure
- **Creates recommendations**: PredictedGap objects with suggested_search
- **Feeds into queue**: Yes, directly

### Gap Types Detected

```python
class GapType(Enum):
    MEDIATION = "mediation"              # A→X→Y exists, A→Y missing
    MECHANISM = "mechanism"              # Empirical but no theory
    BOUNDARY = "boundary"                # Narrow scope
    DIRECTION = "direction"              # Conflicting causal direction
    INTERACTION = "interaction"          # Independent effects, no interaction
    VALIDATION = "validation"            # Theory without empirical support
    OPEN_QUESTION = "open_question"      # User-identified gap
    CRITICAL_QUESTION = "critical_question"  # Walton argumentation framework
    ATTACK_VULNERABILITY = "attack_vulnerability"  # Argument attack vectors
```

### Gap Detection Methods

**find_all_gaps(max_gaps=50)**:
```python
def find_all_gaps(self, max_gaps: int = 50) -> GapReport:
    """
    Runs all gap detection methods and aggregates results.
    """
    gaps = []
    gaps.extend(self.find_mediation_gaps())
    gaps.extend(self.find_mechanism_gaps())
    gaps.extend(self.find_boundary_gaps())
    gaps.extend(self.find_direction_gaps())
    gaps.extend(self.find_interaction_gaps())
    gaps.extend(self.find_validation_gaps())
    gaps.extend(self.find_critical_question_gaps())
    gaps.extend(self.find_argument_attack_gaps())
    gaps.extend(self.harvest_gaps_from_annotations())

    return GapReport(gaps=gaps[:max_gaps])
```

**Critical Questions** (Walton framework):
```python
def find_critical_question_gaps(self) -> List[PredictedGap]:
    """
    Use Walton argumentation framework to find critical questions
    that the argument doesn't address.
    """
    # Per argument type (causal, explanatory, effect-to-cause, etc.)
    # Generate critical questions
    # Check if they're answered in the local corpus
    # If not answered, create gap
```

**Argument Attack Gaps** (4 detectors):
```python
def find_argument_attack_gaps(self) -> List[PredictedGap]:
    """
    Detect vulnerabilities to argument attacks:
    1. Begging the question (circular reasoning)
    2. Straw man (misrepresentation)
    3. False analogy
    4. Insufficient evidence
    """
```

**Annotation Harvesting**:
```python
def harvest_gaps_from_annotations(self) -> List[PredictedGap]:
    """
    Extract open questions and search prompts that annotators
    have manually identified.
    """
    open_questions = ann_svc.get_annotations_by_type('open_question')
    search_prompts = ann_svc.get_annotations_by_type('search_prompt')

    for ann in open_questions:
        gaps.append(PredictedGap(
            gap_id=...,
            gap_type=GapType.OPEN_QUESTION,
            description=f"User-identified gap: {ann.content[:200]}",
            suggested_search=ann.content,
            ...
        ))
```

### PredictedGap Data Structure

```python
@dataclass
class PredictedGap:
    gap_id: str
    gap_type: GapType
    description: str
    priority: GapPriority = GapPriority.MEDIUM

    # VOI FIELD (PROBLEMATIC)
    voi_score: float = 0.5  # HARDCODED DEFAULT

    affected_edge: Optional[str] = None
    affected_beliefs: List[str] = field(default_factory=list)

    # SEARCH GUIDANCE
    suggested_search: str = ""
    resolution_approach: str = ""

    # METADATA
    confidence: float = 0.7
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

### Integration into Queue

**ResearchQueueService.refresh_queue()**:
```python
def refresh_queue(self, max_gaps: int = 50, include_theory: bool = True) -> ResearchQueueState:
    try:
        gap_report = self.gap_predictor.find_all_gaps(max_gaps=max_gaps)
        for gap in gap_report.gaps:
            generated_targets.append(self._target_from_predicted_gap(gap))
    except Exception as exc:
        logger.warning("GapPredictor refresh failed (%s)", exc)
```

**Conversion to ResearchTarget**:
```python
def _target_from_predicted_gap(self, gap: PredictedGap) -> ResearchTarget:
    return ResearchTarget(
        target_id=f"gap_{gap.gap_id}",
        gap_description=gap.description,
        gap_type=gap.gap_type,
        priority=gap.priority,
        voi_score=gap.voi_score,  # Carries hardcoded 0.5
        suggested_searches=[gap.suggested_search],
        ...
    )
```

### VOI Problem: Hardcoded Default

**Issue**: Every gap gets voi_score=0.5 regardless of actual importance

**Why it matters**:
- Queue doesn't rank by VOI (only FIFO)
- So hardcoded values have no effect
- But prevents VOI-driven prioritization if queue is fixed

**Solution needed**:
```python
# Gap predictor should compute VOI or accept external scoring
gap.voi_score = self.voi_scorer.calculate_voi(gap, self.web) if self.voi_scorer else 0.5
```

### Why It's REAL

1. ✓ Code fully implements gap detection
2. ✓ Integrated into ResearchQueueService
3. ✓ Generates article recommendations (suggested_search field)
4. ✓ Feeds directly into queue
5. ✗ But VOI is hardcoded
6. ✗ And queue doesn't use VOI for prioritization

---

## Source D: VOI System (voi_search.py)

### Overview
- **Status**: REAL (code exists and functions, but underutilized)
- **Size**: 1945 lines
- **Purpose**: Compute value of information and generate prioritized search queries
- **Creates recommendations**: SearchRecommendation objects with VOI scores
- **Feeds into queue**: Optional (lazy import, fallback available)

### VOI Computation Method

**VOIGapScorer class**:
```python
class VOIGapScorer:
    def calculate_voi(self, gap: EpistemicGap, belief: Belief, web: WebOfBelief) -> float:
        """
        VOI = 0.5 * structural_voi + 0.5 * epistemic_voi
        """
        structural = self._structural_voi(gap)
        epistemic = self._epistemic_voi(belief)
        return 0.5 * structural + 0.5 * epistemic

    def _structural_voi(self, gap: EpistemicGap) -> float:
        """
        How central is this gap in the belief structure?
        - Centrality: affects how many other beliefs?
        - Criticality: is it a linchpin for major chains?
        """
        # Implementation in lines 550-573
        return centrality_score

    def _epistemic_voi(self, belief: Belief) -> float:
        """
        How uncertain is this belief?
        VOI_epistemic = 0.4 * uncertainty + 0.4 * centrality + 0.2 * sparsity
        """
        # Lines 575-620
        return (
            0.4 * self._uncertainty_component(belief) +
            0.4 * self._centrality_component(belief, web) +
            0.2 * self._sparsity_component(gap_type, belief)
        )
```

### Search Query Generation

**QueryGenerator class**:
```python
class QueryGenerator:
    def generate_queries(self, gaps: List[EpistemicGap],
                        max_queries_per_gap: int = 3) -> List[SearchRecommendation]:
        """
        For each gap, generate targeted queries with VOI scoring.
        """
        recommendations = []
        for gap in gaps:
            voi = self.voi_scorer.calculate_voi(gap)
            sources = self.source_selector.select_sources(gap)
            queries = self._build_queries(gap, sources)

            recommendations.append(SearchRecommendation(
                gap_id=gap.gap_id,
                voi_score=voi,
                queries=queries,
                sources=sources,
                stopping_condition=self._suggest_stopping(gap, voi)
            ))

        # Sort by VOI (highest first)
        return sorted(recommendations, key=lambda r: r.voi_score, reverse=True)
```

### Cross-Field Vocabulary (Sprint K)

**CrossFieldVocabulary class**:
```python
class CrossFieldVocabulary:
    """
    Translate neuroarchitecture terms to adjacent field terminology.
    Example: "attention restoration" → ["stress recovery", "psychophysiological recovery"]
    """
    def expand_query(self, concept: str) -> List[str]:
        """Get all equivalent terms across fields."""
        return [canonical_term] + field_terms
```

### Integration Points

**Where voi_search is imported**:
1. `queue/service.py:153` (lazy import)
   ```python
   try:
       from src.services.voi_search import QueryGenerator
       self._query_generator = QueryGenerator()
   except Exception as exc:
       logger.warning("VOI query generator unavailable; using fallback")
       self._query_generator = _FallbackQueryGenerator()
   ```

2. `services/query_engine.py:57` (optional import)
   ```python
   try:
       from src.services.voi_search import VOIGapScorer, ...
       VOI_AVAILABLE = True
   except ImportError:
       VOI_AVAILABLE = False
   ```

3. `services/discovery_funnel.py:47` (optional import)

### Fallback Mechanism

**_FallbackQueryGenerator** (if voi_search import fails):
```python
def generate_queries(self, text: str, gap_type: GapType, max_queries: int = 5) -> list[str]:
    """
    Simple keyword extraction without VOI scoring.
    """
    terms = self._extract_terms(text)  # Remove stopwords

    queries = [" ".join(terms[:6])]
    if gap_type == GapType.VALIDATION:
        queries.append(f"{base} replication")
        queries.append(f"{base} meta analysis")
    elif gap_type == GapType.MECHANISM:
        queries.append(f"{base} mechanism")
        queries.append(f"{base} pathway")
    # ...
    return queries[:max_queries]
```

**Implications**:
- If voi_search fails to import, system **silently degrades**
- Users get simple keyword queries instead of VOI-ranked
- No error, no warning beyond debug log
- Results in less effective search recommendations

### Why It's COMPUTED BUT UNDERUTILIZED

1. ✓ VOI scoring code fully implemented
2. ✓ Cross-field vocabulary support added (Sprint K)
3. ✓ Source selection per domain (Giles framework)
4. ✗ Only used if QueryGenerator explicitly instantiated
5. ✗ Optional import means system works without it
6. ✗ Gap predictor doesn't call it
7. ✗ Queue doesn't use VOI scores for prioritization

---

## Source E: Discovery Funnel (discovery_funnel.py)

### Overview
- **Status**: TRACKING ONLY (records progress, no decision-making)
- **Purpose**: Track gaps from identification through search and closure
- **Creates recommendations**: No
- **Feeds into queue**: No (passive read-only)
- **Used for prioritization**: No

### Gap Status Lifecycle

```python
class GapStatus(Enum):
    OPEN = "open"               # Not yet searched
    SEARCHING = "searching"     # Active searches underway
    FOUND = "found"             # Articles found, awaiting retrieval
    CLOSED = "closed"           # Gap addressed
    STALE = "stale"             # Gap no longer relevant
```

### Closure Types

```python
class ClosureType(Enum):
    REFUTED = "refuted"                    # Found contradicting evidence
    WEAKLY_SUPPORTED = "weakly_supported"  # Some supporting evidence
    STRONGLY_SUPPORTED = "strongly_supported"
    INDEFINITE = "indefinite"              # Mixed evidence
```

### Usage in Pipeline

**Only used in paper_integration/orchestrator.py**:
```python
# List all gaps to track
open_gaps = funnel.list_gaps(status=GapStatus.OPEN)
searching_gaps = funnel.list_gaps(status=GapStatus.SEARCHING)

# Update when paper integrated
funnel.record_gap_closure(
    gap_id=gap_id,
    closure_type=ClosureType.STRONGLY_SUPPORTED,
    closing_paper=paper_id
)
```

### No Feedback Loop

**Missing**: Closure assessment → VOI revision → queue re-ranking

Currently:
- Gap OPEN → Queue tracks it
- Search executed → Gap SEARCHING
- Paper found → Gap FOUND → CLOSED
- But closure doesn't affect queue prioritization
- And closure assessment doesn't revise VOI scores

---

## Source F: Automated Searcher (automated_searcher.py)

### Overview
- **Status**: REAL (functional, but opt-in)
- **Size**: 188 lines
- **Purpose**: Claim queue targets and execute searches via Semantic Scholar
- **Creates recommendations**: No (consumes them)
- **Feeds into queue**: Yes (reports results back)

### How It Works

```python
class AutomatedQueueSearcher:
    def run_once(self) -> List[AutomatedTargetRun]:
        """
        Claim and process up to max_targets_per_run open queue targets.
        """
        runs = []
        for _ in range(self.config.max_targets_per_run):
            claim = self.queue_service.claim_target(self.config.collector_id)
            if not claim.success:
                break

            target = claim.target
            guidance = claim.search_guidance
            queries = guidance.primary_queries[:self.config.max_queries_per_target]

            # Execute search
            candidates = self._run_queries(queries)

            # Report back
            assessment = self.queue_service.report_search_result(...)
            runs.append(AutomatedTargetRun(...))

        return runs
```

### Search Execution

```python
def _run_queries(self, queries: list[str]) -> list[ArticleReference]:
    """Execute search queries and deduplicate results."""
    found = {}
    for query in queries:
        rows = self.search_fn(query, limit=self.config.max_results_per_query)
        for row in rows or []:
            ref = self._row_to_reference(row)
            if ref is None:
                continue
            key = (ref.doi or ref.title or "").lower().strip()
            if key not in found or ref.relevance_score > found[key].relevance_score:
                found[key] = ref

    return sorted(found.values(), key=lambda x: x.relevance_score, reverse=True)
```

### Search Source

**Default**: Semantic Scholar API
```python
# Line 54
from app.services.semantic_scholar import search as semantic_scholar_search
self.search_fn = semantic_scholar_search
```

**Customizable**: Can inject mock search function for testing

### Invocation

**Current state**: Must be explicitly instantiated and run
```python
searcher = AutomatedQueueSearcher(queue_service, config=AutomatedSearcherConfig())
results = searcher.run_once()  # Manual invocation needed
```

**Missing**: No automatic scheduling or worker invocation

---

## Summary: Sources Comparison

| Aspect | Gap Predictor | VOI Scorer | Automated Searcher | Interpretation Space | Discovery Funnel |
|--------|---------------|-----------|-------------------|----------------------|------------------|
| Status | REAL | REAL | REAL | ASPIRATIONAL | TRACKING |
| Generates | PredictedGap | SearchRec | Search Results | [Undefined] | Gap Status |
| VOI Used | Hardcoded 0.5 | Yes | Not aware | Assumed | No |
| Integrated | Yes | Optional | Opt-in | No | Passive |
| User Context | No | No | No | Unknown | No |
| Feeds Queue | Yes | Optional | Reports back | Would be | No |
| Researcher Specific | No | No | No | Unknown | No |

---

## Critical Missing Layer: Researcher-Specific VOI

None of the sources implement researcher-specific VOI adjustments:

```python
# Currently: All researchers get same VOI for all gaps
gap_voi = 0.5  # Hardcoded

# Should be:
researcher_fit = compute_researcher_fit(researcher_profile, gap)
gap_voi_adjusted = base_voi * researcher_fit
# where researcher_fit accounts for:
# - Expertise level
# - Domain interest
# - Theoretical alignment
# - Access level
# - Previous closure rates
```

This is **critical** per David's statement: *"before we can recommend to a researcher that they pursue a topic, we need researcher-specific VOI"*

---

## Recommendations

1. **Complete VOI integration**: Gap predictor should call VOI scorer
2. **Queue prioritization**: Add `get_highest_voi_targets()` method
3. **Researcher modeling**: Extend CollectorProfile → researcher-specific VOI adjustment
4. **Interpret space**: Either define table + populate, or remove monitoring
5. **Automated search**: Add scheduler to auto-invoke searcher bot
6. **Feedback loops**: Closure assessment → VOI revision → queue re-ranking
