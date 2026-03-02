# Article Recommendation Flow Audit
## Article_Eater_PostQuinean_v1

**Date**: March 2, 2026
**Auditor**: Claude Code
**Scope**: How article search recommendations flow from different sources; VOI integration status; user-specific VOI

---

## Executive Summary

This audit reveals a **significant disconnect between aspirational architecture and actual implementation**:

1. **Recommendation sources exist** but are largely **DISCONNECTED** from actual article search execution
2. **VOI is partially wired** — it computes scores but recommendations are not consistently using them
3. **User-specific VOI is MISSING** — system treats all researchers identically
4. **Key infrastructure tables are assumed but undefined** — the overseer queries tables that don't exist in the codebase
5. **Three of four recommendation sources are STUBS** — code exists but nothing calls them

---

## Part 1: Article Recommendation Sources

### Source A: QA System (arbitrary_qa_handler.py)

**Status**: STUB — Code exists, not called for article recommendations

**Location**: `/src/services/arbitrary_qa_handler.py` (51.8 KB)

**What it does**:
- Handles arbitrary user questions about system knowledge
- Routes to QA handlers (catalog, evidence, comparison, mechanism, definition, meta)
- Static handlers return pre-computed answers from KnowledgeCatalog
- AI-routed handlers build context packages from annotations

**Article recommendation capability**:
- Line 690: Includes follow-up suggestion `"What evidence supports these recommendations?"`
- But this is **reactive only** — it suggests asking about evidence after answering, not proactively recommending articles

**Actual call chain**:
- `ArbitraryQAHandler.answer(question)` → routes to handler → returns response with follow-ups
- No integration with `ResearchQueueService`
- No VOI scoring
- No article search execution

**Verdict**: **STUB** — Can suggest follow-ups but doesn't generate article search recommendations

---

### Source B: Annotation / Interpretation Space (overseer_management.py)

**Status**: ASPIRATIONAL — Infrastructure queries tables that don't exist

**Location**: `/src/services/overseer_management.py` lines 518-649

**What it does**:
- `SearchSuggestionTracker.check_suggestion_backlog()` queries from `interpretation_space_suggestions` table
- Tracks suggestions by source: argumentation, VOI, QA, interpretation_space, other
- Ages suggestions and alerts on staleness
- Designed to monitor whether suggestions are being acted upon

**Table schema (assumed but UNDEFINED)**:
```sql
CREATE TABLE interpretation_space_suggestions (
    id INTEGER,
    source TEXT,          -- 'interpretation_space', 'voi', 'qa', 'argumentation', etc.
    status TEXT,          -- 'proposed', 'identified'
    created_at TEXT,
    ...
)
```

**Where suggestions would originate**:
- Lines 598-599: Counts by source, explicitly expects `interpretation_space` as a source
- Comments mention "Assumes: interpretation_space_suggestions or similar table" (line 545)
- Overseer registry declares this as component of article-discovery pipeline (line 115)

**Actual call chain**:
```
SearchSuggestionTracker.check_suggestion_backlog()
  ├─ Queries interpretation_space_suggestions (table undefined)
  └─ Returns SuggestionBacklogReport with source breakdown
```

**Verdict**: **ASPIRATIONAL** — Code assumes infrastructure that doesn't exist. The interpretation_space data directory contains JSON and markdown files (phase2-4 outputs) but no table insertion code or schema definition.

---

### Source C: Argumentation Structure / Gap Predictor (gap_predictor.py)

**Status**: PARTIALLY REAL — Computes gaps, generates search suggestions, but doesn't trigger actual searches

**Location**: `/src/services/gap_predictor.py` (1582 lines)

**What it does**:
- Predicts 6 knowledge gap types from argument structure:
  1. Mediation gaps (missing direct relationships)
  2. Mechanism gaps (missing explanations)
  3. Boundary gaps (limited scope)
  4. Direction gaps (causal ambiguity)
  5. Validation gaps (theory without empirical support)
  6. Interaction gaps (independent effects without interactions)

**Key methods**:
- `find_all_gaps(max_gaps)` — generates PredictedGap objects with VOI scores
- `find_critical_question_gaps()` — uses Walton argumentation framework
- `find_argument_attack_gaps()` — 4 attack vulnerability detectors
- `harvest_gaps_from_annotations()` — reads open_questions and search_prompts annotations
- `PredictedGap` dataclass includes `suggested_search` field (line 63)

**VOI scoring**:
- Each gap gets `voi_score: float = 0.5` (line 55)
- **But values are HARDCODED defaults** — actual VOI calculation missing in gap_predictor itself
- Relies on external VOI modules for scoring

**Article generation**:
```python
# Lines 771-795: Harvest gaps from annotations
for ann in open_questions:
    gaps.append(PredictedGap(
        gap_id=...,
        gap_type=GapType.OPEN_QUESTION,
        description=f"User-identified gap: {ann.content}",
        suggested_search=ann.content[:100],  # Puts annotation text as search query
        ...
    ))
```

**Actual call chain**:
```
ResearchQueueService.refresh_queue()
  └─ GapPredictor.find_all_gaps()
      └─ Returns List[PredictedGap] with:
           - gap_id, gap_type, description
           - voi_score (default 0.5)
           - suggested_search (optional)
           - confidence
           - resolution_approach
```

Then:
```
ResearchQueueService._target_from_predicted_gap(gap)
  └─ Creates ResearchTarget object
      └─ Target is added to ResearchQueueService._targets
          └─ [DISCONNECTED] Nothing consumes these for actual search
```

**Actual integration**:
- Line 37, queue/service.py: `from src.services.gap_predictor import GapPredictor`
- Lines 173-175: Calls `gap_predictor.find_all_gaps()` and converts to `ResearchTarget`
- Targets stored in `self._targets` dictionary
- No automatic execution of searches based on these targets

**Verdict**: **PARTIALLY REAL** — Gap detection works, generates suggestions with VOI placeholders, but:
- VOI scores are hardcoded, not actually computed
- Suggestions feed into research queue
- Queue management layer exists (`ResearchQueueService`)
- But automatic execution is missing (would need external searcher bot to claim targets)

---

### Source D: VOI (Value of Information) System

**Status**: COMPLEX — Multiple modules, partial integration, no user-specific logic

**Components**:

#### D1. voi_search.py (1945 lines)

**Key structures**:
- `VOIGapScorer` — computes VOI for gaps using epistemic + structural components
- `SearchRecommendation` — output of gap→search translation
- `EpistemicGap` — wrapper for gaps with VOI context
- `SourceSelector` — domain-based source selection (Giles framework)
- `QueryGenerator` — creates search queries from gaps

**VOI calculation methods** (lines 512-614):
```python
class VOIGapScorer:
    def calculate_voi(self, gap: EpistemicGap, belief: Belief, web: WebOfBelief) -> float:
        structural = self._structural_voi(gap)
        epistemic = self._epistemic_voi(belief)
        return 0.5 * structural + 0.5 * epistemic

    def _epistemic_voi(self, belief: Belief) -> float:
        return (
            0.4 * self._uncertainty_component(belief) +
            0.4 * self._centrality_component(belief, web) +
            0.2 * self._sparsity_component(gap_type, belief)
        )
```

**But**:
- Called by `QueryGenerator.generate_queries()` (line 740+)
- Not integrated into actual queue management
- No calls to this from `ResearchQueueService.refresh_queue()`

**SearchRecommendation output**:
```python
@dataclass
class SearchRecommendation:
    gap_id: str
    gap_type: str
    belief_id: Optional[str]
    voi_score: float
    queries: List[str]
    sources: List[str]
    stopping_condition: str
```

**Actual call chain**:
```
QueryGenerator.generate_queries(gaps)
  └─ For each gap:
      ├─ VOIGapScorer.calculate_voi()
      ├─ SourceSelector.select_sources()
      ├─ QueryGenerator._build_queries()
      └─ Returns SearchRecommendation
```

**Integration**:
- Imported in `queue/service.py` line 153 (lazy import with fallback)
- Used in `ResearchQueueService.query_generator` property (lines 150-162)
- **Key**: If import fails, falls back to `_FallbackQueryGenerator` (lines 42-96)
- No VOI scoring in fallback — just stopword removal and keyword extraction

**Verdict**: **COMPUTED BUT UNDERUTILIZED** — VOI calculations exist but are only used when QueryGenerator is instantiated, which is optional

---

#### D2. voi_scoring.py (108 lines)

**Simple utility module**:
```python
def score_voi(findings: list[dict]) -> list[dict]:
    """Score findings by VOI (0-1 scale)"""
    for finding in findings:
        score = _score_single_finding(finding)
        bucket = "high" | "medium" | "low"
```

**Used by**:
- `cmr/paper_eval.py` — aggregates VOI for paper-level assessment
- `cmr/__init__.py` — public import

**NOT used by**:
- Gap predictor
- Research queue
- Discovery funnel

**Verdict**: **SPECIALIZED MODULE** — Scores individual findings from extraction, not integrated with gap-driven search

---

#### D3. discovery_funnel.py (Large service)

**Purpose**: Track gaps from identification → search → PDF retrieval → ingestion → closure

**Key enum**: `GapStatus.OPEN → SEARCHING → FOUND → CLOSED | STALE`

**What's tracked**:
- VOI gaps identified
- Search execution progress
- PDF retrieval attempts
- Paper ingestion completion
- Gap closure assessment

**How it's used**:
```python
# In orchestrator.py (paper integration):
funnel = DiscoveryFunnelService(db_path=...)
open_gaps = funnel.list_gaps(status=GapStatus.OPEN)
searching_gaps = funnel.list_gaps(status=GapStatus.SEARCHING)
```

**Verdict**: **TRACKING INFRASTRUCTURE** — Records funnel progress but doesn't drive search initiation. Passive monitoring layer.

---

## Part 2: Is VOI Actually Hooked Up?

### Import Analysis

**Where voi_search is imported**:
1. `queue/service.py:153` — Lazy import, with fallback
2. `services/query_engine.py:57` — Optional import, `VOI_AVAILABLE` flag
3. `services/voi_search.py` — self-references only

**Where voi_scoring is imported**:
1. `cmr/__init__.py` — Public export
2. `cmr/paper_eval.py` — For paper-level VOI aggregation

**Where gap_predictor is imported**:
1. `queue/service.py:37` — Direct, used in `refresh_queue()`
2. `services/query_engine.py:67` — Optional import, with fallback
3. `services/discovery_funnel.py` — Not imported
4. `services/voi_search.py` — Optional import (line 47)

**Where discovery_funnel is imported**:
1. `services/voi_search.py:47` — Optional import
2. `services/paper_integration/orchestrator.py:122` — Used for gap tracking
3. `services/system_setup.py` — Setup initialization

### Call Chain Analysis

**Primary chain**:
```
ResearchQueueService.refresh_queue()
  └─ gap_predictor.find_all_gaps()
      └─ Returns gaps with default VOI=0.5
  └─ For each gap:
      └─ _target_from_predicted_gap(gap)
          └─ Create ResearchTarget
          └─ Add to self._targets

[STOPS HERE — no automatic search execution]
```

**Optional secondary chain**:
```
ResearchQueueService.query_generator property
  └─ Try: from src.services.voi_search import QueryGenerator
  └─ Fallback: _FallbackQueryGenerator()
  └─ If successful: VOIGapScorer and cross-field vocabulary used
  └─ If failed: Simple keyword extraction only
```

**Discovery funnel (passive monitoring)**:
```
Paper integration orchestrator
  ├─ Ingest PDF findings
  └─ Update web_of_belief
      └─ query_funnel.list_gaps(status=GapStatus.OPEN)
      └─ [Observation only, no feedback to queue]
```

### VOI Integration Verdict

**PARTIALLY CONNECTED, NOT FUNCTIONAL FOR SEARCH PRIORITIZATION**:

1. **VOI is computed** but only when QueryGenerator is explicitly used
2. **QueryGenerator is optional** — system falls back gracefully if import fails
3. **Gap predictor uses hardcoded VOI=0.5** — doesn't call VOI computation modules
4. **ResearchQueueService doesn't use VOI scores** for prioritization
   - Targets are stored but not ranked by VOI
   - No property like `get_next_highest_voi_target()`
5. **Discovery funnel is read-only** — tracks progress but doesn't influence search prioritization

**Real vs. Stub Status**:
- VOI scoring code: **REAL** (executes, produces scores)
- VOI integration into search: **STUB** (code present, not called)
- VOI-driven queue prioritization: **MISSING** (no code)

---

## Part 3: User-Specific VOI

### Current State: No User/Role/Researcher Modeling

**Search for "user", "researcher", "role", "persona" in VOI/gap code**:

Found in `queue/models.py`:
```python
@dataclass
class CollectorProfile:
    """Profile for a VOI collector."""
    collector_id: str
    collector_type: CollectorType  # HUMAN_RESEARCHER, HUMAN_ASSISTANT, AUTOMATED_SEARCHER, ZOTERO_WATCHER
    name: str
    can_access_databases: List[str]
    can_access_paywalled: bool
    preferred_domains: List[str]
    max_concurrent_targets: int
    typical_turnaround_hours: float
    targets_completed: int
    gap_closure_rate: float
    avg_articles_per_target: float
```

**What this enables**:
- Collectors can have role types
- Collectors have domain preferences
- Collectors have access profiles (paywalled vs. open)

**What's MISSING**:
1. **No VOI adjustment by collector type** — all collectors see same VOI scores
2. **No researcher-specific weighting** — theory researcher vs. practitioner vs. developer
3. **No domain specialization in VOI** — VOI doesn't increase for collector's preferred domains
4. **No expertise modeling** — system doesn't know if collector needs validation vs. mechanism evidence
5. **No research agenda alignment** — system doesn't know what gaps matter to this researcher

**Evidence from queue/service.py**:
```python
def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Get next unassigned target for collector."""
    # Line 200+: Doesn't consider collector's preferred_domains or expertise
    # Just returns unassigned targets in order
```

**No personalization logic found**:
- No scoring adjustment per collector
- No re-ranking based on collector profile
- No feedback loop from collector performance to VOI

### User-Specific VOI: MISSING

**Why this matters** (per David's concern):
> "before we can recommend to a researcher that they pursue a topic, we need researcher-specific VOI"

**What would be needed**:
1. Researcher model: expertise, interests, access, theoretical alignment
2. VOI_adjusted = base_VOI * researcher_fit_factor
3. Feedback loop: track closure_rate per gap per researcher to learn fit

**Current state**: System provides same recommendations to all researchers regardless of expertise or context.

---

## Part 4: Actual Article Search Execution

### Who Actually Searches?

**The only functional article searcher found**:

**AutomatedQueueSearcher** (`src/queue/automated_searcher.py`, 188 lines):

```python
class AutomatedQueueSearcher:
    def run_once(self):
        """Claim and process up to max_targets_per_run open queue targets."""
        for _ in range(max_targets):
            claim = self.queue_service.claim_target(collector_id)
            if claim.success:
                guidance = claim.search_guidance
                queries = guidance.primary_queries
                candidates = self._run_queries(queries)
                # Report results back to queue
                self.queue_service.report_search_result(target_id, result)
```

**How it works**:
1. Claims a `ResearchTarget` from queue
2. Gets `SearchGuidance` with queries from gap predictor (or fallback generator)
3. Executes queries via Semantic Scholar API
4. Reports results back to queue

**Actual search source**:
```python
# Line 54: Default import from semantic_scholar
from app.services.semantic_scholar import search as semantic_scholar_search
self.search_fn = semantic_scholar_search  # Can be overridden
```

**What's MISSING**:
- Automated searcher is **opt-in** — must be explicitly instantiated and run
- Not integrated into main pipeline
- No automatic invocation
- Would need external scheduler/worker to call `run_once()` periodically

**Verdict**: Searcher exists but is not automatically triggered by gap predictions

---

## Part 5: Complete Flow Diagram

### Current (Actual) Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Article Recommendation Flow — Article_Eater (Actual)            │
└─────────────────────────────────────────────────────────────────┘

INPUT SOURCES (Gaps Generated)
├─ Source A: QA System (arbitrary_qa_handler.py)
│   └─ Generates follow-up suggestions [STUB — never calls queue]
│
├─ Source B: Interpretation Space (overseer_management.py)
│   └─ Queries from table that doesn't exist [ASPIRATIONAL]
│
├─ Source C: Gap Predictor (gap_predictor.py) [REAL]
│   ├─ find_all_gaps() → List[PredictedGap]
│   ├─ VOI = hardcoded 0.5
│   └─ suggested_search field populated
│
└─ Source D: VOI System (voi_search.py) [PARTIALLY REAL]
    ├─ VOI calculations exist but unused
    └─ Only called if QueryGenerator explicitly instantiated

                          ↓

RESEARCH QUEUE SERVICE (queue/service.py)
├─ refresh_queue():
│   ├─ Calls gap_predictor.find_all_gaps()
│   ├─ Converts to ResearchTarget objects
│   └─ Stores in self._targets (no ranking by VOI)
│
└─ claim_target(collector_id):
    ├─ Returns unassigned target (FIFO, no VOI ordering)
    └─ Generates SearchGuidance (uses QueryGenerator if available)

                          ↓

DISCOVERY FUNNEL SERVICE (discovery_funnel.py) [PASSIVE]
├─ Tracks VOI gaps: OPEN → SEARCHING → FOUND → CLOSED
└─ No feedback to queue prioritization

                          ↓

AUTOMATED SEARCHER (queue/automated_searcher.py) [OPT-IN]
├─ Must be explicitly instantiated
├─ Claims targets from queue
├─ Executes search queries
└─ Reports results → gap closure assessment

                          ↓

INTEGRATION (paper_integration/orchestrator.py)
├─ Ingests PDF findings
├─ Updates web_of_belief
└─ [No feedback to VOI or queue]

KEY DISCONNECTS:
- Gap predictor → Queue: CONNECTED (targets created)
- Queue → VOI prioritization: DISCONNECTED (no VOI ranking)
- Queue → Automated searcher: CONNECTED (claims work)
- Searcher → Discovery funnel: PARTIAL (status updated, no feedback)
- User/researcher context: MISSING (all searches treated identically)
```

### Aspirational (Intended) Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Article Recommendation Flow — Intended Design                   │
└─────────────────────────────────────────────────────────────────┘

Gap Predictor → VOI Scorer → ResearchQueue → VOI Ranker → AutomatedSearcher
                                                          ↓
                                                    SemanticScholar
                                                          ↓
                                                    PDFRetriever
                                                          ↓
                                                    Extraction
                                                          ↓
                                                    WebOfBeliefIntegration
                                                          ↓
                                                    DiscoveryFunnelTracking
                                                          ↓
                                                    GapClosureAssessment
                                                          ↓
                                                    Researcher-Specific VOI Feedback
```

---

## Part 6: Master Doc Topics to Add/Revise

### Critical Missing Sections

1. **VOI Integration Architecture** (New doc)
   - Current: VOI computes scores but recommendations don't use them
   - Needed: How VOI feeds queue prioritization
   - Include: VOI_adjusted = f(base_VOI, collector_profile, domain, urgency)

2. **User/Researcher VOI** (New section)
   - Why: David stated "before we can recommend to a researcher, we need researcher-specific VOI"
   - Design: Researcher expertise model + fit factor
   - Feedback: Closure rate per researcher per gap type

3. **Interpretation Space Suggestions Schema** (Fix)
   - Current: overseer_management.py queries `interpretation_space_suggestions` table
   - Missing: Table definition, insertion code, population logic
   - Need: Either:
     - Define table in schema and wire up phase2-4 outputs to populate it, OR
     - Remove aspiration and acknowledge interpretation_space outputs are offline

4. **Article Search Execution Pipeline** (New doc)
   - Current: Fragmented (automated_searcher exists but not auto-invoked)
   - Design: When/how/why gaps trigger article searches
   - Define: External scheduler, worker pool, rate limiting

5. **VOI Computation Defaults** (Fix)
   - Current: gap_predictor hardcodes voi_score=0.5
   - Issue: Ignores epistemic_voi and structural_voi calculations
   - Fix: gap_predictor should optionally call VOIGapScorer

6. **Research Queue Prioritization** (Fix/Complete)
   - Current: FIFO (first-unassigned returned)
   - Missing: VOI-based prioritization
   - Add: get_next_highest_voi_target(), prioritized_targets_by_voi()

7. **CollectorProfile Integration** (Incomplete)
   - Current: Profile exists but not used for VOI adjustment
   - Missing: Logic to personalize VOI by collector expertise/domain
   - Add: adjust_voi_by_collector(base_voi, collector_profile) → adjusted_voi

8. **Query Generator Integration** (Clarify)
   - Current: Optional import with fallback
   - Issue: Unclear when QueryGenerator is used vs. _FallbackQueryGenerator
   - Document: When VOI-enhanced queries are available vs. keyword-only

9. **Discovery Funnel Feedback Loop** (Missing)
   - Current: One-way tracking only
   - Missing: How gap closure affects queue prioritization
   - Needed: Closure assessment → VOI revision → queue re-ranking

10. **Overseer Management Database Schema** (Missing)
    - Current: SQL queries assume tables that don't exist
    - Missing: `management_pipelines`, `interpretation_space_suggestions`, etc.
    - Define: Complete schema for all tables referenced in overseer_management.py

---

## Part 7: Specific Code Issues

### Issue 1: Hardcoded VOI in Gap Predictor

**File**: `src/services/gap_predictor.py`, line 55
```python
@dataclass
class PredictedGap:
    voi_score: float = 0.5  # DEFAULT VALUE NEVER OVERRIDDEN
```

**Problem**: Every gap gets 0.5 regardless of epistemic importance

**Solution**:
```python
# Option A: Accept VOI scorer as dependency
def __init__(self, web=None, edge_justification_service=None, voi_scorer=None):
    self.voi_scorer = voi_scorer or VOIGapScorer()

# Option B: Compute VOI during gap generation
for gap in gaps:
    if self.voi_scorer:
        gap.voi_score = self.voi_scorer.calculate_voi(gap, ...)
```

---

### Issue 2: Interpretation Space Suggestions Table Undefined

**File**: `src/services/overseer_management.py`, lines 545-602

**Problem**: Queries a table that doesn't exist anywhere in codebase
```sql
SELECT COUNT(*) FROM interpretation_space_suggestions  -- TABLE DOES NOT EXIST
```

**Current workaround**: Code catches exception silently (try/except with returns)

**Solution**: Either
1. Create table and wire phase2-4 outputs to populate it, OR
2. Document that interpretation_space is offline and remove from monitoring

---

### Issue 3: VOI Optional But Unused

**File**: `src/services/query_engine.py`, lines 56-62
```python
try:
    from src.services.voi_search import (
        VOIGapScorer, GapType, ResearchGap, SuggestedSearch
    )
    VOI_AVAILABLE = True
except ImportError:
    VOI_AVAILABLE = False
```

**Problem**: VOI_AVAILABLE is set but never used in query_engine
- Imports are optional
- No code path that actually calls VOIGapScorer
- Set up as safety fallback but not actually required

---

### Issue 4: Queue Doesn't Rank by VOI

**File**: `src/queue/service.py`, line 200+
```python
def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Get next unassigned target for collector."""
    # Returns first unassigned target (FIFO)
    # Should be: sorted by voi_score descending
```

**Problem**: Targets could be ranked by VOI but aren't

**Impact**: Researchers always work on oldest gaps, not most valuable ones

---

### Issue 5: No Researcher Context in Recommendations

**File**: Entire codebase

**Problem**: VOI calculation never considers:
- Researcher expertise (novice vs. expert)
- Researcher domain interest
- Researcher access level (paywalled journals)
- Researcher theoretical alignment

**Evidence**:
- `CollectorProfile.preferred_domains` exists but unused
- No researcher_fit_factor in any VOI calculation
- All queries same for all researchers

---

## Conclusion

### Summary of Findings

| Component | Status | Evidence |
|-----------|--------|----------|
| Gap Predictor | REAL | Generates 6 gap types, produces suggested_search |
| VOI Scoring | REAL BUT UNUSED | Code computes scores, nothing consumes them |
| Query Generator | OPTIONAL | Lazy import with fallback, unclear when used |
| Research Queue | REAL | Stores targets, claims targets via collectors |
| Automated Searcher | REAL BUT OPT-IN | Must be explicitly instantiated; not auto-invoked |
| Discovery Funnel | TRACKING ONLY | Records progress but no feedback loop |
| User-Specific VOI | MISSING | No researcher modeling, no fit factors |
| QA Recommendations | STUB | Generates follow-ups but no queue integration |
| Interpretation Space | ASPIRATIONAL | Queries undefined table; phase outputs offline |

### Critical Gaps

1. **VOI not actually used for search prioritization** — computed but recommendations don't rank by it
2. **User-specific VOI missing entirely** — all researchers get same recommendations
3. **Infrastructure tables don't exist** — overseer assumes `interpretation_space_suggestions` table
4. **Automated search not triggered** — searcher exists but must be manually invoked
5. **Feedback loops missing** — no closure assessment → VOI revision cycle

### What Works

1. Gap detection from argumentation structure ✓
2. Query generation from gaps ✓
3. Queue management and collector claiming ✓
4. Semantic Scholar integration (when triggered) ✓
5. VOI score computation (as utility) ✓

### What's Broken/Incomplete

1. VOI integration into queue prioritization ✗
2. User-specific VOI ✗
3. Automated search triggering ✗
4. Interpretation space backend ✗
5. Feedback loops (closure → VOI revision) ✗

---

## Appendix: File Inventory

**Core Recommendation Components**:
- `/src/services/gap_predictor.py` — 1582 lines, 6 gap types, VOI=0.5
- `/src/services/voi_search.py` — 1945 lines, VOI scorer, query generator
- `/src/cmr/voi_scoring.py` — 108 lines, finding-level VOI utility
- `/src/queue/service.py` — ResearchQueueService, FIFO claiming
- `/src/queue/automated_searcher.py` — Opt-in searcher bot
- `/src/services/discovery_funnel.py` — Funnel tracking (no prioritization)
- `/src/services/overseer_management.py` — Monitoring, assumes undefined tables
- `/src/services/arbitrary_qa_handler.py` — QA routing, no search recommendations
- `/src/queue/models.py` — CollectorProfile exists but context unused

**Integration Points**:
- `/src/services/query_engine.py` — Optional VOI import, not used
- `/src/services/paper_integration/orchestrator.py` — Uses discovery_funnel for tracking
- `/src/queue/zotero_watcher.py` — Syncs external Zotero library

---

**Report Generated**: 2026-03-02
**Recommended Action**: Schedule panel review to decide:
1. Complete VOI integration or document as aspirational
2. Implement researcher-specific VOI or clarify system is domain-agnostic
3. Define/populate interpretation_space_suggestions or remove monitoring
4. Auto-trigger searcher or document as manual workflow
