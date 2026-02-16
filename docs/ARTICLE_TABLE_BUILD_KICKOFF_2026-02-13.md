# Article Table Build Kickoff (2026-02-13)

## Objective
Build structured evidence tables from papers/tables for AE ingestion with reproducible JSONL artifacts.

## Task Alignment
From `docs/CHAT_TASK_LIST_2026-02-12.md`:
- Table extraction is `CHAT-T2-TABLE-EXTRACTION`.
- Recommended task sequence: `T3 -> T1 -> T4 -> T5 -> T6 -> T2 -> T7 -> T8`.

## Practical Plan
1. Start immediately with table pipeline scaffolding, but keep outputs marked `provisional` until T4/T6 normalization is complete.
2. Define one canonical row schema for table-derived findings.
3. Emit JSONL batches under `data/processed_tables/`.
4. Add validation script for required fields and effect-sign consistency.

## Canonical Row Schema (provisional)
- `paper_id`
- `doi`
- `table_id`
- `row_id`
- `independent_variable_raw`
- `dependent_variable_raw`
- `independent_variable_canonical`
- `dependent_variable_canonical`
- `effect_direction`
- `statistic_type`
- `statistic_value`
- `p_value`
- `confidence_interval`
- `sample_size`
- `scope_conditions`
- `notes`
- `extraction_confidence`

## Immediate Build Steps
1. Create `data/processed_tables/` and `data/processed_tables/batches/`.
2. Add extraction prompt template file for stable operator use.
3. Add validator script to reject malformed table rows.
4. Run first pilot batch and inspect mapping drift.

## Exit Criteria For Kickoff
- First batch file generated.
- Validator passes schema checks.
- Mapping mismatch report produced for canonicalization backlog.
