# Codex Handoff: Table System State (2026-02-13)

## What Was Completed In This Pass

1. Full table-spec consolidation docs created:
- `docs/TABLE_SPEC_MATRIX_2026-02-13.md`
- `docs/TABLE_SPEC_GAP_AUDIT_2026-02-13.md`

2. Gold-pack PDF path resolution fixed:
- `scripts/build_table_gold_pack.py`
- Added robust resolver for:
  - absolute paths
  - queue-relative paths
  - project-relative paths
  - Article Finder repo-relative paths (`data/pdfs/...`)
- Manifest now includes:
  - `pdf_path` (raw input)
  - `resolved_pdf_path` (actual resolved path)

3. Full gold-pack rebuild re-run:
- Output dir: `data/table_gold/codex_gold_v1`
- Summary now:
  - Queue input rows: `98`
  - Processed PDFs: `98`
  - Missing PDFs: `0`
  - Failed: `0`
  - Gold rows: `174`

4. Article-type split regenerated and upgraded:
- Script updated: `scripts/build_article_type_tables.py`
- Still emits coarse 11-type split.
- Now also emits template-family split aligned to extraction templates.
- Summary: `data/table_gold/by_article_type/summary.md`

5. Realtime production-line automation added:
- `scripts/run_realtime_table_rule_intake.py`
  - now supports `--integrate-web` and `--update-bn`
- `scripts/process_realtime_pdf_completion_queue.py`
  - batch PDF queue drain + PDF-confirmed integration
- `scripts/run_realtime_production_worker.py`
  - continuous orchestration loop (intake + PDF completion)

## Current Key Findings (Do Not Lose)

### Critical
1. `table_to_claims` output is not fully compatible with `extraction_to_web` claim contract:
- Emits `claim_text` + `confidence` + `metadata`
- Mapper expects `statement` + `ae_confidence` + `statistics` + `constructs` + `study`

2. Table claim-type vocabulary mismatch:
- Emits `finding|methodology|sample|effect`
- Mapper ontology expects `mechanistic|causal|associational|moderated|descriptive|null`

3. Extraction family coverage mismatch:
- Runtime extractor has only a few generic table prompt types; templates require 15 families + stimulus schema depth.

4. Stimulus detail is not represented at required `ae.stimulus.v1` depth in table outputs.

### Major
5. Table-detection fallback logic uses global `detected` state and can skip fallback on later pages if earlier pages already matched.

## Generated Artifacts to Use Immediately
- Gold rows: `data/table_gold/codex_gold_v1/codex_gold_rows.csv`
- Manifest (with resolved path): `data/table_gold/codex_gold_v1/manifest.csv`
- Raw extracted tables: `data/table_gold/codex_gold_v1/raw_tables.jsonl`
- Type-split outputs: `data/table_gold/by_article_type/`

## Next Required Work (Priority Order)
1. Fix table-claim contract mapping (`C1` + `C2`) in `src/services/table_to_claims.py`.
2. Add template-family-aware extraction adapters (at least empirical/systematic/meta/theoretical first).
3. Add explicit stimulus extraction object (`ae.stimulus.v1`) and linkage via `stimulus_set_id`.
4. Patch page-local fallback detection bug in `src/services/table_extractor.py`.
5. Tighten article-type/template router confidence and manual-review path.

## Epistemic Layer Coordination Constraint
Do not design bridge payloads around legacy `credence/entrenchment` only.
Coordinate with:
- `docs/CODEX_HANDOFF_EPISTEMIC_CALCULUS_2026-02-12.md`
Future bridge contract must support `rank`, `neg_rank`, `warrant`, `grounding`.
