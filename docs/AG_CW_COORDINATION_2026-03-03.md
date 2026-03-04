# AG ↔ CW Coordination — March 3, 2026

## Current State (1:32 PM)

**AG** (this window — Antigravity/Gemini):
- ✅ P0 #1-4 applied and CW-reviewed
- ✅ Precomputed card retrieval wired into QA handler (39ms lookups)
- ✅ IncrementalUpdater wired into ingestion pipeline
- ✅ SUCCESS_CONDITIONS_2026-03-03.md — comprehensive: ~128 conditions across ~45 subsystems from 5 sources
- ✅ SUBSYSTEM_INVENTORY_FOR_MASTER_DOC_2026-03-03.md — CW should add this to master doc
- ✅ P1 fixes: GapPredictor *.jsonl→*.json, language adaptation now transforms text
- ✅ Functional circuits analysis — mapped 22 circuits onto existing T-level infrastructure
- ✅ PANEL_PROMPT_T_LEVELS_FUNCTIONAL_CIRCUITS_2026-03-03.md — **CW must contribute before panel**

**CW** (other window — Claude Code):
- 🔄 Writing additional systemic tests
- 🔄 Inventorying success condition gaps across codebase
- 🔄 Reading existing test infrastructure
- **NEW**: Must contribute to panel prompt (see `docs/PANEL_PROMPT_T_LEVELS_FUNCTIONAL_CIRCUITS_2026-03-03.md`)

---

## Files AG Owns (CW should not edit simultaneously):
- `src/qa/card_retriever.py` (NEW — AG created)
- `src/services/answer_enrichment_orchestrator.py` (AG modified for P0 fixes)
- `src/services/integrated_query_service.py` (AG fixed tuple bug)
- `src/services/arbitrary_qa_handler.py` (AG wired card retrieval)
- `scripts/auto_ingest_pdfs.py` (AG added IncrementalUpdater hook)
- `tests/test_card_retrieval.py` (NEW — AG created)
- `docs/SUCCESS_CONDITIONS_2026-03-03.md` (AG created + expanded)
- `docs/P0_FIXES_CW_REVIEW_2026-03-03.md` (AG created)
- `docs/SUBSYSTEM_INVENTORY_FOR_MASTER_DOC_2026-03-03.md` (AG created — CW should use for master doc additions)

## Files AG Is About To Modify (P1 fixes):
- `src/services/gap_predictor.py` — Fix corpus path mismatch (searches wrong directory)
- `src/services/answer_enrichment_orchestrator.py` — Fix language adaptation (returns metadata not prose)

## For CW to Do:
1. Add subsystem inventory to Master Document (use `docs/SUBSYSTEM_INVENTORY_FOR_MASTER_DOC_2026-03-03.md`)
2. Write tests for untested services (see list below)
3. Review AG's success conditions additions

## Services Missing Tests (12 total — for CW to pick up):
1. evidence_integration
2. extraction_to_web
3. bbn_calibrator
4. epistemic_orchestrator
5. argumentation_graph
6. grounding_service
7. integrated_query_service
8. export_engine
9. knowledge_catalog
10. belief_clustering
11. card_generator
12. incremental_updater / precompute_pipeline
