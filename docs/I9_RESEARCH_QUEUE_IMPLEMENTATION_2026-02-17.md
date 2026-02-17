# Sprint 9 Queue Implementation (I9.1-I9.7)

Date: 2026-02-17
Owner: Codex

## Completed

- I9.1: Implemented `ResearchQueueService` in `src/queue/service.py`
  - `refresh_queue()` integrates `GapPredictor` output into queue targets
  - `get_next_target()` assigns highest-priority open targets
  - `report_search_result()` updates target status and opportunity framing
  - queue state persisted to `data/production/research_queue_state.json`

- I9.2: Added theory-driven gap detection
  - `detect_theory_gaps()` generates validation targets from Tier 1 framework predictions
  - `get_theory_predictions()` returns framework-specific targets
  - theory coverage metric included in `ResearchQueueState.theory_coverage`

- I9.3: Connected queue to Zotero watcher
  - Added `src/queue/zotero_watcher.py`
  - BibTeX delta scanning with persistent watcher state
  - lexical match of new entries to open/searching targets
  - `ResearchQueueService.sync_zotero_to_queue()` auto-reports matched entries as `FOUND`

- I9.4: Added VOI collector registration + claiming
  - Added collector contract models in `src/queue/models.py`:
    - `CollectorProfile`, `CollectorType`, `SearchGuidance`, `ClaimResult`
  - Added service APIs in `src/queue/service.py`:
    - `register_collector()`, `get_collector()`, `list_collectors()`, `claim_target()`
  - Added collector capacity enforcement and target claim deadlines
  - Persisted collector profiles in queue state JSON

- I9.5: Added research opportunity registry
  - Added `OpportunityStatus` + `ResearchOpportunity` models in `src/queue/models.py`
  - Added registry APIs in `src/queue/service.py`:
    - `list_research_opportunities()`, `get_research_opportunity()`, `update_research_opportunity()`
  - Automatic opportunity creation from `report_search_result(... NOT_FOUND ...)` when opportunity criteria are met
  - Persisted `research_opportunities` in queue state JSON

- I9.6: Added Streamlit queue dashboard
  - Added `streamlit_app/pages/6_research_queue.py`
  - Queue metrics + filters by status/priority
  - Manual claim and status-update controls
  - Collector registration and opportunity update forms
  - Automation controls for bot runs and Zotero sync

- I9.7: Added automated searcher bot
  - Added `src/queue/automated_searcher.py`
  - Semantic Scholar-backed bulk screening cycle:
    - claim target
    - run query set
    - score candidates
    - report `FOUND`/`NOT_FOUND` back to queue
  - Added `ResearchQueueService.run_automated_searcher()` wrapper

## New/Updated Files

- `src/queue/models.py`
- `src/queue/service.py`
- `src/queue/zotero_watcher.py`
- `src/queue/__init__.py`
- `tests/test_research_queue_service.py`
- `tests/test_research_queue_zotero_sync.py`
- `tests/test_research_queue_collectors.py`
- `tests/test_research_opportunity_registry.py`
- `tests/test_research_queue_dashboard.py`
- `tests/test_research_queue_automated_searcher.py`
- `streamlit_app/pages/6_research_queue.py`
- `src/queue/automated_searcher.py`

## Validation

- `pytest -q tests/test_research_queue_service.py tests/test_research_queue_zotero_sync.py tests/test_research_queue_collectors.py tests/test_research_opportunity_registry.py tests/test_research_queue_dashboard.py tests/test_research_queue_automated_searcher.py`
- Result: `16 passed`

## Notes

- `src/services/voi_search.py` depends on `pyyaml`; queue service now has a fallback query generator when VOI query dependencies are unavailable.
- Zotero matching currently uses token-overlap heuristics and a configurable threshold (`min_score`).
