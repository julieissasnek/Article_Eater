# Ruthless V13 Codex Audit: End-to-End Reliability (Article Eater / ATLAS)

**Date:** 2026-03-03  
**Auditor:** Codex (GPT-5)  
**Mode:** Fresh retest (code read + full pytest + live runtime probes)

## 0) What was rerun

1. Re-read required files:
   - `docs/RUTHLESS_V12_AUDIT_REPORT_2026-03-02.md`
   - `src/services/answer_enrichment_orchestrator.py`
   - `src/services/integrated_query_service.py`
   - `tests/test_e2e_qa_pipeline.py`
2. Re-ran full suite exactly as requested:
   - `pytest tests/ -v --tb=short`
   - Result: **5853 passed, 38 skipped, 6 deselected, 1 xfailed, 289 warnings** in **214.63s**
3. Ran fresh non-mocked probes for:
   - 9-step enrichment runtime behavior
   - integrated query behavior with/without article grounding
   - corpus counts and local evidence lookup
   - unanswerable query behavior

## 1) Brutal verdict

The system is **better than the prior run** (test suite now green), but still **NO-GO for production-trustworthy evidence QA**.

**Go/No-Go Score: 3.9 / 10 (NO-GO)**

Reason: one core path still hard-crashes (`IntegratedQueryService.query(... include_articles=True)`), provenance target directory is missing (`data/articles/`), and the claimed 33k findings corpus is not wired to the query-time readers.

## 2) Answers to the required evaluation questions

### A) Does the 9-step enrichment pipeline actually enrich or silently skip?

**Answer: It partially enriches, but still degrades in a way that can look healthier than it is.**

Fresh runtime probe (no test mocks):
- `services_attempted`: 9/9
- `services_failed`: `['follow_up_suggestions']`
- `services_skipped`: `['figure_suggestions']`
- Successful outputs:
  - `enriched_beliefs`: 2
  - beliefs with `warrant_trace`: 2
  - beliefs with `confounder_risk`: 2
  - `framework_voices`: 3
  - `gaps`: 5
  - `interpretation_context`: present
  - `language_adaptation`: present
- Broken output:
  - `follow_ups`: 0 due to runtime contract mismatch

Root cause of failure:
- Orchestrator calls `follow_up_service.generate_follow_ups(...)` in `src/services/answer_enrichment_orchestrator.py:852`, but fallback `RecommendationLoopService` has no such method (class in `src/services/recommendation_loop.py:35` only exposes loop orchestration methods like `run_single_pass`).

Additional reliability concern:
- `health_check()` reports all services healthy (`9/9`) even though follow-up generation fails at runtime. So the health signal is optimistic.

### B) Can answers be traced back to real source papers in `data/articles/`?

**Answer: No.**

- `data/articles/` does not exist in this workspace.
- Integrated evidence query path currently crashes before returning article evidence:
  - `IntegratedQueryService.web` stores `self._accumulator.get_master_web()` directly (`src/services/integrated_query_service.py:362`).
  - `WebAccumulator.get_master_web()` returns a `(WebOfBelief, BridgeRegistry)` tuple (`src/services/web_accumulator.py:295-303`).
  - `_find_article_evidence()` then calls `self.web.beliefs` (`src/services/integrated_query_service.py:409`) and raises:
    - `AttributeError: 'tuple' object has no attribute 'beliefs'`

Bottom line: requested paper-traceability path to `data/articles/` is currently non-functional.

### C) Are the 33,000+ extraction findings in `data/extracted_findings/` actually queryable?

**Answer: No, not as claimed.**

Observed corpus reality:
- `data/extractions/`: **1069 JSON files**, with summed `n_findings` = **33,065**.
- `data/extracted_findings/`: **9 JSONL files**, **31 total lines**.

Query-time mismatch:
- `PredictionGenerator` fallback reads `data/extracted_findings/*.jsonl` (`src/services/prediction_generator.py:695-699`) -> only sees the 31-row mini-corpus.
- `GapPredictor.find_local_evidence_for_gap` now points at `data/extractions` but still iterates `*.jsonl` (`src/services/gap_predictor.py:295-298`) while the directory contains `.json` files. Net result: extracted finding hits are zero.

Fresh probe result:
- `GapPredictor.find_local_evidence_for_gap(...)` returned:
  - `extracted_findings_hits = 0`
  - `keyword_matched_beliefs_hits = 10`

So the 33k extraction corpus exists on disk but is effectively disconnected from live retrieval logic.

### D) What happens when the system is asked something it genuinely cannot answer?

**Answer: default integrated path crashes; abstention logic exists but is bypassed in the crash path.**

Unanswerable probe question:
- `"What is the effect of lunar basalt acoustics on office cognition in Martian habitats?"`

Results:
- `IntegratedQueryService.query(... include_articles=True)` -> hard exception:
  - `AttributeError: 'tuple' object has no attribute 'beliefs'`
- If articles are manually disabled (`include_articles=False`), abstention logic does fire:
  - confidence collapsed from `0.55` to `0.20`
  - evidence summary marked speculative.

So abstention is implemented, but currently not reliable in the default evidence-enabled path.

## 3) Subsystem scorecard

| Subsystem | Score | Evidence |
|---|---:|---|
| Test suite status | 8/10 | Full suite now passes (5853 passed), but runtime integration defects still escape tests. |
| E2E test signal quality | 4/10 | `tests/test_e2e_qa_pipeline.py` still mocks core services (`lines 38-57`), masking real contracts. |
| 9-step enrichment runtime | 6/10 | 7/9 outputs meaningful; follow-ups fail by contract, figures skip. |
| Integrated query grounding | 1/10 | Default `include_articles=True` crashes due tuple/web mismatch. |
| Provenance to source papers (`data/articles/`) | 1/10 | Directory missing; required trace path absent. |
| Extraction findings queryability | 2/10 | 33k findings in `data/extractions` not consumed by readers expecting JSONL. |
| Unanswerable-question behavior | 5/10 | Abstention mechanism exists, but default path crashes before reliable use. |

**Overall Reliability Score: 3.9 / 10 (NO-GO)**

## 4) Top 3 failure modes

1. **Article-grounding hard crash in integrated query (highest severity)**
   - Trigger: `include_articles=True` query path.
   - Mechanism: tuple returned by `get_master_web()` is treated like a web object.
   - Impact: no article evidence, no abstention path, query aborts.

2. **Follow-up enrichment contract mismatch**
   - Trigger: orchestrator fallback to `RecommendationLoopService`.
   - Mechanism: expects `generate_follow_ups(...)` method that service does not implement.
   - Impact: step marked failed; research follow-up layer dead at runtime.

3. **Extraction corpus wiring split (33k present, not queryable)**
   - Trigger: consumers read JSONL paths/format, while bulk corpus sits in JSON files.
   - Mechanism: `data/extractions/*.json` vs readers coded for `*.jsonl` and/or `data/extracted_findings`.
   - Impact: local evidence retrieval underuses corpus and produces false scarcity.

## 5) Bottom line

The retest confirms real progress from the previous audit (test suite fixed; several enrichment steps now genuinely execute), but the system is still **not reliable end-to-end** for evidence-grounded QA until the integrated article path and corpus wiring are corrected.
