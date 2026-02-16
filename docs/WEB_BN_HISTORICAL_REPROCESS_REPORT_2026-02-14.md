# Web/BN Historical Reprocess Report (2026-02-14)

## Scope
- Repo: `Article_Eater_PostQuinean_v1`
- Objective: Historical reprocess to improve web relation diversity and bridge coverage using active worker logic.
- Script added: `scripts/reprocess_web_relations_and_bridges.py`

## Baseline (Before Reprocess)
- Beliefs: `5880`
- Constraints: `8718`
- Bridges: `7`
- Constraint type counts:
  - `supports`: `8670`
  - `explains`: `43`
  - `contradicts`: `5`

## Applied Reprocess
- Legacy constraint reclassification pass (conservative):
  - `legacy_constraints`: `8705`
  - `reclass_counts`: `supports->contradicts: 1`
- Cross-paper relation backfill (shared `environment_id` + `outcome_id`):
  - `new_cross_paper_constraints`: `8680`
  - by type:
    - `explains`: `8663`
    - `supports`: `13`
    - `contradicts`: `4`
- Bridge warrant backfill from historical beliefs:
  - `new_bridges`: `969`

## Result (After Reprocess)
- Beliefs: `5880`
- Constraints: `17398`
- Bridges: `976`
- Constraint type counts:
  - `explains`: `8706`
  - `supports`: `8682`
  - `contradicts`: `10`
- Bridge type counts:
  - `analogical`: `842`
  - `functional`: `69`
  - `mechanism`: `62`
  - `constitutive`: `3`

## Connectivity Snapshot
- Isolated beliefs: `1242` (`21.12%`)
- Avg in-degree: `2.959`
- Avg out-degree: `2.959`
- Beliefs with both in/out degree > 0: `2674`

## Idempotency Check
- Re-running `scripts/reprocess_web_relations_and_bridges.py --dry-run` after apply:
  - `legacy_constraints=0`
  - `new_cross_paper_constraints=0`
  - `new_bridges=0`

## Related Runtime Fixes (Applied Earlier This Session)
- `scripts/process_realtime_pdf_completion_queue.py`
  - metadata-aware `effect_direction`
  - structured relation typing (`supports`/`explains`/`contradicts`)
  - bridge detection integrated in worker path
  - explicit provenance-bearing constraint writes
- `scripts/run_realtime_table_rule_intake.py`
  - abstract-stage relation classification
  - bridge detection + persistence in worker path
- `src/services/web_persistence.py`
  - `_row_to_constraint` now restores `warrant_type` and `provenance` (prevents metadata loss on round-trip)
