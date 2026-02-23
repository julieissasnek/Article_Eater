# Seven Panel Reference Classification (2026-02-20)

## Executive Answer
- `seven_panel` is **not** a pure ancient dead spec.
- It is a **mixed state**: active compatibility layer + stale naming + newer article-type contracts.
- AESHI bad numbers were **not** caused by counting seven-panel files/mentions.

## Why AESHI Is Low (Evidence)
- Current hard-gate failures from `/tmp/aeshi_second_pass_full.json`:
  - `sanity_check` (repo compile issues)
  - `offline_pipeline_v2_smoke` (fixed in this pass)
  - `web_bn_minimum_viable` (fails on `bn.unresolved_pct`)
- Score inputs show drivers:
  - `minimum_ratio=0.9167`
  - `target_ratio=0.1429`
  - `cci_ratio=0.4084`
  - failing metric in minimum gate: `bn.unresolved_pct`
- No AESHI formula term uses file-reference counts for `seven_panel`.

## Classification

### 1) Active Core (current extraction/claim pipeline)
- `app/services/extract_article_essence.py`
  - primary extraction service and prompt path (`ARTICLE_ESSENCE_findings.md`)
- `app/tasks/pipeline.py`
  - runtime calls `extract_findings_from_text(...)`
- `src/extraction/article_type_contract.py`
  - per-article-type field contracts
- `src/extraction/claim_extractor.py`
  - applies family contract and field targets

Status: **core runtime**

### 2) Active Compatibility Layer (still executed in some paths)
- `src/agents/agent_stubs.py`
  - classic `SevenPanelArtifact` path, used by smoke tooling and compatibility flows
- `src/agents/json_utils.py`
  - validates legacy `prompts/seven_panel_schema.json` array format
- `src/services/graph_service_fallback.py`
  - emits graph event type `"seven_panel"`
- `app/core/policy.py`
  - legacy task alias `seven_panel` -> `article_essence_extraction`
- `app/routes/graph.py`
  - graph filter docs mention `"seven_panel"`

Status: **active compat**

### 3) Transitional v2 Layer
- `src/agents/agent_panels_v2.py`
  - Seven-Panel v2 bundle extraction (subject-aware panel schema)
- `src/services/rulegraph_v2_builder.py`
  - maps v2 bundle -> RuleGraph v2

Status: **active adjunct path**

### 4) Stale or Likely Dead
- `schemas/seven_panel.schema.json`
  - old object-with-`panels` schema, not used by active runtime paths
- `scripts/upgrade_to_v19_1_4.py`, `scripts/upgrade_to_v19_1_5.py`
  - migration-era references
- `scripts/cost_model.yaml` key `seven_panel_pred_usd`
  - stale naming, not evidence of current extraction contract

Status: **stale/deprecated**

## Repairs Applied in This Pass
- `app/worker.py`
  - switched primary import to `extract_article_essence`, kept legacy fallback.
- `scripts/test_extract_7panel_parsing.py`
  - now imports parser from `extract_article_essence`.
- `scripts/offline_pipeline_v2_smoke.py`
  - now returns schema-valid classic findings array for the legacy sub-call inside `Agent_Finder_v2`.

## Recommended Next Cleanup (safe order)
1. Rename compatibility symbols, not behavior:
   - `attach_seven_panel` -> `attach_article_essence` (keep alias one release).
2. Move legacy schema names behind explicit compatibility module:
   - isolate `prompts/seven_panel_schema.json` usage to one place.
3. Remove stale object schema if unreferenced after one release:
   - `schemas/seven_panel.schema.json`.
4. Update docs/UI labels from `seven_panel` -> `article_essence`.

## Bottom Line
- Your intuition about naming debt was correct.
- The bad health number is mainly **data/graph quality** (`bn.unresolved_pct`, weak BN connectivity, low CCI), not string matches or file counts of `seven_panel`.
