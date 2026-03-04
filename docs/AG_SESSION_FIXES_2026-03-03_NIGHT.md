# AG Session Fixes — 2026-03-03 Night Session

## For Master Doc Integration

This document describes all fixes and new modules from the March 3 night session.
CW: please integrate the relevant parts into the master doc.

---

## 1. Nightly Pipeline Wiring Gap (Critical)

**Problem**: The Materialized View (MV) rebuild system and molecule QA precomputation pipeline
were fully implemented but **never triggered** — neither `nightly_integration_pipeline.py` nor
`overseer_nightly_v3.py` contained any reference to `MaterializedViewBuilder`, `build_all`,
`IncrementalUpdater`, or `precompute_pipeline`. This meant that stale materialized views
(omega scores, evidence index, gap analysis, framework voices) were never rebuilt, and
molecule QA summaries were never refreshed.

**Fix**: Added two new stages to `nightly_integration_pipeline.py` (now 16 stages total):

- **`stage_mv_rebuild`** — Calls `build_all(incremental=True)`, only rebuilds STALE views.
  No LLM calls, fast. Runs after web health check.
- **`stage_precompute`** — Regenerates molecule L1/L2/L3 QA summaries via LLM.
  Gates on `GEMINI_API_KEY` (skips gracefully without it). Runs after MV rebuild.

The ordering ensures MV views are fresh before precomputation runs.

## 2. Enum Mismatches in MV Builder (P1)

Fixed three enum crashes in `mv_builder.py::build_omega_scores`:
- `DesignType.RCT` → `DesignType.STANDARD_RCT`
- `blinding` parameter → correct name per `compute_omega_sev` signature
- `PublicationType` string → proper enum value

## 3. Confounder Risk Checker (P1)

**Problem**: The `_enrich_confounder_risk` method only checked for a literal string `"observational"`
and depended on a non-existent `checker` service.

**Fix**: Implemented a 4-tier classification system:
- **High risk**: Observational, cross-sectional, ecological, survey (~12 design strings)
- **Medium risk**: Quasi-experimental, natural experiment, longitudinal (~8 design strings)
- **Low/synthesis**: Meta-analysis, systematic review (~5 design strings)
- **Low/experimental**: RCT, randomized, blinded (~8 design strings)

Normalized design strings (lowercase, strip) and added bounds-checking for beliefs array.

## 4. Missing Service Modules — Properly Created (not band-aids)

### 4a. `follow_up_suggestion_service.py` [NEW]

**Was**: Inline template-based fallback generating generic questions like
"What are boundary conditions?" with no corpus grounding.

**Now**: Proper service with 5 data sources in priority order:
1. **GapPredictor** — corpus-grounded evidence gaps
2. **Pre-computed gaps** — from earlier in the pipeline
3. **Adjacent molecules** — via MoleculeRegistry keyword overlap
4. **Underexplored findings** — extraction corpus findings not covered by existing answer
5. **Templates** — last resort, lowest VOI (0.35-0.45 vs 0.55-0.8 for corpus-grounded)

### 4b. `figure_suggestion_service.py` [NEW]

**Was**: Scanning 200 random JSON files per query (O(N) per query, unreliable).

**Now**: Pre-built keyword index that maps terms → figure references + paper metadata.
Index is built once on first use and cached. Lookups are O(query_words) instead of O(corpus_size).
Also indexes tables with captions.

Both wired into ServiceRegistry with lazy-load getters and proper `all_service_names` registration.

## 5. QA Router Upgrade — T2 Archetype + Molecule Type Routing

**Problem**: `MoleculeAwareRouter._classify_question` only matched molecule names by keyword.
Questions like "what uses predictive coding?" or "show me functional circuits" couldn't be routed.

**Fix**: Added two new classification branches:
- **Archetype queries**: 6 archetypes × 4 aliases each = 24 trigger phrases
  (e.g., "predictive coding", "bayesian brain", "free energy" → PREDICTIVE_CODING)
- **Molecule type queries**: 5 types (FUNCTIONAL_CIRCUIT, MECHANISM, THEORY, PHENOMENON, DESIGN_PATTERN)
  triggered by listing keywords ("what", "list", "show", "which", "all")

Added matching `route_query` handlers that return structured molecule listings.

## 6. Timezone Bug Fix

Fixed `datetime.now(datetime.UTC)` → `datetime.now(timezone.utc)` in `precompute_pipeline.py`.
`datetime.UTC` doesn't exist as an attribute; the correct constant is `timezone.utc` from the
`datetime` module. Would crash at runtime.

## 7. End-to-End Reachability Audit

Created permanent health check: `tests/test_reachability_audit.py`
- 50+ tests across 6 test classes
- Tests that all services resolve, all pipeline stage deps import, all QA router handlers work,
  and all referenced modules exist on disk
- Takes 0.6s to run
- Uses `xfail` for known-missing with documented reason, `skipif` for optional deps
- Only remaining xfail: `academic_presentation_service` (replaced by `figure_suggestion_service`)

---

## Files Modified

| File | Change |
|------|--------|
| `scripts/nightly_integration_pipeline.py` | +2 stages, +os import |
| `src/qa/mv_builder.py` | Enum fixes |
| `src/qa/precompute_pipeline.py` | datetime.UTC fix |
| `src/qa/router.py` | T2 archetype + molecule type routing |
| `src/services/answer_enrichment_orchestrator.py` | Confounder risk, service hookups, registry updates |
| `src/services/follow_up_suggestion_service.py` | [NEW] proper follow-up generation |
| `src/services/figure_suggestion_service.py` | [NEW] indexed figure suggestions |
| `tests/test_reachability_audit.py` | [NEW] permanent health check |
