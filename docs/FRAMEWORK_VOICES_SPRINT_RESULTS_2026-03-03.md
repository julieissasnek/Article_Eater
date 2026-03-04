# P0 #5 Framework Voices — Sprint Results & System Impact

**Date**: 2026-03-03  
**Sprint**: FV-A + FV-B  
**Status**: ✅ COMPLETE — 72 tests pass, 0 fail

---

## What Changed

### Problem
Framework voices returned identical canned text for every query. `_generate_framework_perspective()` was a hardcoded if/elif chain that ignored the `topic` parameter. This violated CW's foundherentist norm: claims must trace to evidence.

### Solution: Corpus-Grounded Voices (Option B)

All 10 T1 framework voices are now generated from the actual extraction corpus:
- **4,868 paper-framework links** across 10 frameworks
- **45,330 finding-framework links** with effect sizes, mechanisms, scope conditions
- Voices differ per topic because the underlying evidence differs

---

## Files Modified

| File | Change | Impact |
|:-----|:-------|:-------|
| `src/qa/mv_builder.py` | Rewrote `build_framework_voices()` — scans extractions, matches `theory_links`/`theory_commitments` against T1 aliases from `tier1_frameworks.json` | Data pipeline now produces real per-framework evidence summaries |
| `src/services/integrated_query_service.py` | Replaced `get_theoretical_voices()` — 3-tier fallback (MV cache → on-the-fly → quarantined template). Added `_select_relevant_frameworks()`, `_render_corpus_perspective()` | Voices are topic-sensitive and include paper counts + source metadata |
| `src/services/answer_enrichment_orchestrator.py` | Updated `_get_framework_voices()` — uses `FrameworkVoiceRenderer` with MV data, tracks `framework_voice_source` in metadata. Updated SC-FV-1 through SC-FV-8 | Enrichment Step 4 now produces grounded voices |
| `src/qa/framework_voice_renderer.py` | **NEW** — `FrameworkVoiceRenderer` class with confidence-calibrated language, `RenderedVoice` dataclass, optional prose quality gate | Rendering separated from data (clean architecture) |
| `tests/test_framework_voices.py` | **NEW** — 13 tests covering MV builder, service integration, quarantine labels, topic differentiation | Prevents regression to canned voices |
| `tests/test_mv_builder.py` | Updated `test_build_framework_voices` to expect new schema (`name`, `n_papers`, `source` instead of `perspective`) | Test alignment |
| `.agent_coord/MESSAGE_BOARD.md` | Message 010: CW notification of sprint plan, file locks, system interactions, outdated components | Cross-agent coordination |

---

## System Interactions & What's Outdated

### Now Outdated
1. **`FRAMEWORK_VOICES` dict** (IQS lines 70-230): Still present as fallback metadata but no longer used for generating perspectives. Will be kept for quarantine fallback only.
2. **`_generate_framework_perspective()`** (IQS lines 481-528): Hardcoded if/elif chain — **deprecated**. The corpus-grounded renderer replaces this entirely.
3. **`_synthesize_panel()`** (IQS lines 598-628): Still produces generic debates. Should be updated in a future sprint to synthesize from corpus evidence.
4. **Old SC-FV-4**: Expected `{framework, voice, implications}` — now expects `{framework, voice, n_papers, source, confidence_level}`.

### Interactions with Existing Systems
1. **Enrichment Orchestrator** (Steps 1-3, 5-9): Unchanged. Step 4 is the only modified enrichment step.
2. **`prose_revision_service.py`**: The renderer supports optional prose quality gating via `use_prose_gate=True`, but this is NOT enabled by default (performance).
3. **`answer_renderer.py`**: Consumes `enriched.framework_voices`. The new schema adds `n_papers`, `source`, and `confidence_level` fields that answer_renderer can optionally use for display.
4. **`tier1_frameworks.json`**: Used as the canonical alias source for framework matching. If frameworks are added/renamed, `build_framework_voices()` automatically picks up changes.
5. **V3 extraction fields**: `theory_commitments` (article-level) and `theory_links` (finding-level) are the semantic backbone. The V3 campaign (677+ papers) made this work.

### P0 Status Summary

| P0 Item | Status |
|:--------|:-------|
| P0 #1: Paper traceability | ✅ Fixed |
| P0 #2: Grounding gate abstention | ✅ Fixed |
| P0 #3: Tuple unpacking | ✅ Fixed |
| P0 #4: Answer status | ✅ Fixed |
| **P0 #5: Framework voices** | ✅ **Fixed** — corpus-grounded |

**All P0 items are now resolved.**

---

## Corpus Coverage per Framework

| Framework | Papers | Findings |
|:----------|-------:|---------:|
| PP (Predictive Processing) | 895 | 13,880 |
| NM (Neuromodulatory Systems) | 653 | 6,710 |
| IC (Interoceptive/Constructionist) | 618 | 5,709 |
| DT (DMN/TPN Dynamics) | 574 | 4,506 |
| DP (Dual-Process Evaluation) | 487 | 3,057 |
| MSI (Multisensory Integration) | 410 | 3,349 |
| EC (Embodied Cognition) | 356 | 1,763 |
| MS (Memory Systems) | 314 | 1,874 |
| SN (Spatial Navigation) | 304 | 2,158 |
| CB (Chronobiological Regulation) | 257 | 2,324 |
| **Total** | **4,868** | **45,330** |

---

## Verification

```
$ python3 -m pytest tests/test_answer_enrichment_orchestrator.py tests/test_mv_builder.py tests/test_framework_voices.py -v
72 passed, 1 skipped, 0 failed (72.91s)
```
