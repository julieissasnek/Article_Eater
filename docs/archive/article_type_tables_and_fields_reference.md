# Article Type Tables and Fields Reference

Updated: 2026-02-17

## 1) Canonical Source of Truth

- `src/epistemic/extraction/paper_classifier.py:24`
  - `TemplateFamily` enum (canonical template/article families).
- `contracts/vocab/canonical_enums.json:101`
  - `enums.ArticleTypeCrosswalk` canonical values, deprecated aliases, and crosswalk mappings.
  - Declares source of truth: `src/epistemic/extraction/paper_classifier.py#TemplateFamily`.

## 2) Where Per-Article-Type "Tables" Are Defined (CSV Split Outputs)

- `scripts/build_article_type_tables.py:21`
  - `ARTICLE_TYPES` list.
- `scripts/build_article_type_tables.py:36`
  - `TEMPLATE_FAMILIES` list.
- `scripts/build_article_type_tables.py:220`
  - Writes per-article-type files:
  - `gold_rows__{article_type}.csv`
  - `reduced_rows__{article_type}.csv`
- `scripts/build_article_type_tables.py:224`
  - Writes per-template-family files:
  - `gold_rows__template__{family}.csv`
  - `reduced_rows__template__{family}.csv`

## 3) Runtime Field Schema for `article_type_*`

Primary schema-bearing locations:

- `scripts/run_realtime_table_rule_intake.py:1028`
  - Populates these fields on table records:
  - `article_type_family`
  - `article_type_predicted_family`
  - `article_type_confidence`
  - `article_type_runner_up`
  - `article_type_margin`
  - `article_type_needs_review`
  - `article_type_signals`
  - `article_type_diagnostics`
  - `article_type_classifier_version`
- `scripts/process_realtime_pdf_completion_queue.py:1816`
  - Explicit output fieldnames list containing the same `article_type_*` schema fields.
- `scripts/backfill_confirmed_row_article_types.py:74`
  - `target_fields` list for syncing/backfilling `article_type_*` fields.
- `scripts/reclassify_pdf_queue_article_types.py:86`
  - Review CSV field list including major `article_type_*` fields.

Related family/value constraints and gating:

- `scripts/process_realtime_pdf_completion_queue.py:180`
  - `CANONICAL_FAMILIES` set.
- `scripts/run_realtime_table_rule_intake.py:92`
  - `EMPIRICAL_ABSTRACT_RULE_FAMILIES` (families eligible for abstract-rule gate).

## 4) DB / Migration Schema Touchpoints

- `app/db.py:210`
  - `CREATE TABLE IF NOT EXISTS article_essence (...)`
  - Includes `article_type` and `extraction_template` columns.
- `migrations/020_rename_seven_panel_to_article_essence.sql:9`
  - Rename migration and rationale for broader multi-article-type extraction.
- `migrations/006_discovery_funnel.sql:41`
  - `voi_gaps.target_article_types` JSON-array field.

## 5) Contract-Level Field

- `src/epistemic/contracts/claim_v2.py:104`
  - Contract field: `article_type_family`.

## 6) Crosswalk / Migration Utilities

- `scripts/migrate_article_type.py:18`
  - Adapter generation around canonical section `enums.ArticleTypeCrosswalk`.
  - Includes outcome<->AE mappings and lossiness checks.

## 7) Additional Supporting Files That Use Article-Type Fields

These are relevant consumers/maintainers of the same schema:

- `scripts/reprocess_article_type_tranche_safe.py`
- `scripts/prioritize_and_requeue_article_type_tranche.py`
- `scripts/repair_pdf_confirmed_rules.py`
- `scripts/check_table_extraction_quality.py`
- `scripts/repair_problem_pdfs.py`
- `scripts/generate_batch_15_queue.py`
- `scripts/check_enum_drift.py`
- `src/epistemic/validation/node_template_mapping.py`
- `src/epistemic/extraction/synthesis_ingester.py`
- `src/epistemic/extraction/theoretical_extractor.py`
- `src/epistemic/extraction/rule_to_claim_mapper.py`

## Notes

- If you need one single canonical list of valid families, use `TemplateFamily` in `src/epistemic/extraction/paper_classifier.py` and the canonical crosswalk in `contracts/vocab/canonical_enums.json`.
- If you need the practical row schema for pipeline CSVs, use `scripts/run_realtime_table_rule_intake.py` and `scripts/process_realtime_pdf_completion_queue.py`.
