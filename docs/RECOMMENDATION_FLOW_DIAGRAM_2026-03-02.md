# Article Recommendation Flow Diagrams

**Date**: March 2, 2026
**Purpose**: Visual representation of actual vs. intended recommendation flows

---

## Diagram 1: Current (Actual) Implementation

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ARTICLE RECOMMENDATION FLOW                             │
│                          (What Actually Exists)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─ FOUR RECOMMENDATION SOURCES ─┐

    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
    │ Source A: QA     │    │ Source B: Interp │    │ Source C: Gaps   │
    │ arbitrary_qa_    │    │ Interpretation   │    │ gap_predictor.py │
    │ handler.py       │    │ Space Tables     │    │ (1582 lines)     │
    │ (STUB)           │    │ (ASPIRATIONAL)   │    │ (REAL)           │
    └──────────────────┘    └──────────────────┘    └──────────────────┘
            │                        │                        │
            │ Follow-up              │ [Table undefined]      │ find_all_gaps()
            │ suggestions            │ No population code     │ → PredictedGap
            │ (reactive)             │                        │ + voi_score=0.5
            │                        │ Overseer queries       │ + suggested_search
            ├─────────────────────────────────────────────────┘
            │
            ▼
        ┌──────────────────────────────────────────┐
        │   Source D: VOI (voi_search.py)          │
        │   (COMPUTED BUT NOT INTEGRATED)          │
        │                                          │
        │   - VOIGapScorer.calculate_voi()        │
        │   - QueryGenerator.generate_queries()    │
        │   - Called ONLY if QueryGenerator        │
        │     explicitly instantiated              │
        │   - Falls back to _FallbackQueryGenerator│
        │     if voi_search import fails           │
        └──────────────────────────────────────────┘
            │
            │ [OPTIONAL ENHANCEMENT]
            │
            ▼
        ┌──────────────────────────────────────────┐
        │     ResearchQueueService                 │
        │     (queue/service.py)                   │
        │                                          │
        │  refresh_queue():                        │
        │  ├─ Call gap_predictor.find_all_gaps()  │
        │  ├─ Convert to ResearchTarget objects    │
        │  └─ Store in self._targets               │
        │                                          │
        │  [NO VOI RANKING - FIFO ONLY]           │
        │                                          │
        │  claim_target(collector_id):             │
        │  ├─ Return first unassigned              │
        │  ├─ Generate SearchGuidance              │
        │  │  ├─ Try: QueryGenerator (with VOI)   │
        │  │  └─ Fallback: _FallbackQueryGenerator│
        │  └─ No researcher-specific adjustment   │
        └──────────────────────────────────────────┘
            │
            ├─────────────────────────────────┐
            │                                 │
            ▼                                 ▼
    ┌───────────────────┐        ┌─────────────────────────┐
    │ Human Researcher  │        │ AutomatedQueueSearcher  │
    │ (Manual work)     │        │ (queue/automated_       │
    │                   │        │  searcher.py)           │
    │ Gets SearchGuid-  │        │ (OPT-IN - must be       │
    │ ance, executes    │        │ explicitly instantiated)│
    │ search manually   │        │                         │
    │                   │        │ run_once():             │
    │                   │        │ ├─ Claim targets        │
    │                   │        │ ├─ Execute queries      │
    │                   │        │ └─ Report results       │
    └───────────────────┘        └─────────────────────────┘
            │                                │
            └────────────┬───────────────────┘
                         │
                         ▼ report_search_result()
            ┌─────────────────────────────────┐
            │  Search Outcome (FOUND/NOT)     │
            │                                 │
            │  Returns SearchResult with:     │
            │  - articles_found               │
            │  - is_research_opportunity      │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │  Queue Status Update             │
            │                                 │
            │  ├─ Target marked FOUND/CLOSED  │
            │  └─ Articles stored in target   │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │  PDF Retrieval (if found)       │
            │  (external service)             │
            │                                 │
            │  Methods:                       │
            │  - direct_link                  │
            │  - unpaywall                    │
            │  - scihub                       │
            │  - library proxy                │
            │  - author_request               │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │  Paper Extraction (Gemini)      │
            │  (extraction/pdf_extraction_    │
            │   module.py)                    │
            │                                 │
            │  Extracts findings and claims   │
            │  → belief format               │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │  Integration into Web           │
            │  (paper_integration/            │
            │   orchestrator.py)              │
            │                                 │
            │  ├─ Add/revise beliefs          │
            │  ├─ Update BN edges             │
            │  └─ Update discovery_funnel     │
            │     gap tracking                │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │ [MONITORING ONLY]               │
            │ Discovery Funnel Service        │
            │ (discovery_funnel.py)           │
            │                                 │
            │ Gap Status:                     │
            │ OPEN → SEARCHING → FOUND →     │
            │ CLOSED / STALE                  │
            │                                 │
            │ Tracks: when gaps are resolved │
            │ Does NOT: feed back to queue   │
            └─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │  [END]                          │
            │  No feedback loop to VOI        │
            │  No researcher learning         │
            │  No queue re-prioritization     │
            └─────────────────────────────────┘


KEY CHARACTERISTICS OF ACTUAL FLOW:

✓ Working:
  - Gap detection works
  - Queue management works
  - Automated searcher (if invoked) works
  - PDF retrieval infrastructure exists

✗ Broken:
  - VOI not used for queue prioritization
  - No automatic searcher invocation
  - No researcher-specific adjustment
  - No feedback loop
  - Interpretation space assumptions invalid
  - QA doesn't feed into queue

[DISCONNECTS] marked in purple → between sources and search execution
[ASPIRATIONAL] marked in red → assumes infrastructure that doesn't exist
[OPT-IN] marked in orange → exists but must be manually triggered
[OPTIONAL] marked in blue → can be enabled but defaults to fallback
