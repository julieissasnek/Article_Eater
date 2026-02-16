# Pipeline Foundation Audit (2026-02-14)

## Scope
Audit of the data path:
1. Article intake (`run_realtime_table_rule_intake.py`)
2. Queue classification and PDF completion (`process_realtime_pdf_completion_queue.py`)
3. Confirmed row integrity (`realtime_pdf_confirmed_rows.csv`)
4. Quality gate before full table encoding (`check_table_extraction_quality.py`)

## Critical Problems Found
- Old article-type classifier was first-match substring logic and produced systematic false labels.
- Type logic was duplicated across intake and PDF scripts, causing drift and repeated misclassification.
- Historical confirmed rows lacked article-type metadata for most rows.
- No explicit article-type verification queue existed before table encoding.

## Fixes Implemented
- Replaced brittle per-script type logic with shared classifier:
  - `src/epistemic/extraction/paper_classifier.py` upgraded with:
    - phrase-boundary matching (prevents `trial` -> `industrial` false hits)
    - conflict handling (review-vs-empirical, theory-vs-empirical)
    - structured signal inference from title/abstract/venue
    - confidence, runner-up, score margin, diagnostics, manual-review flag
- Wired both pipeline stages to shared classifier:
  - `scripts/run_realtime_table_rule_intake.py`
  - `scripts/process_realtime_pdf_completion_queue.py`
- Added type verification artifacts:
  - queue columns now include
    - `article_type_confidence`
    - `article_type_runner_up`
    - `article_type_margin`
    - `article_type_needs_review`
    - `article_type_signals`
    - `article_type_diagnostics`
    - `article_type_classifier_version`
  - article-type review CSV generation in PDF queue processor
- Added repair/backfill tools:
  - `scripts/reclassify_pdf_queue_article_types.py` (full queue relabel + review queue)
  - `scripts/backfill_confirmed_row_article_types.py` (propagate type metadata into confirmed rows)
- Extended quality gates:
  - `scripts/check_table_extraction_quality.py`
  - `config/table_extraction_quality_thresholds.json`
  - new article-type metrics:
    - metadata coverage
    - low-confidence rate
    - review-rate

## Verification Run (Post-Fix)
- `pytest -q tests/test_sprint6c_ingestion.py`
  - `28 passed`
- `python3 scripts/reclassify_pdf_queue_article_types.py`
  - `Rows scanned: 514`
  - `Family changes: 221` (with low-confidence downgrade-to-unknown gate)
  - `Type review rows: 323`
- `python3 scripts/backfill_confirmed_row_article_types.py`
  - `Confirmed rows scanned: 147903`
  - `Rows updated: 147903`
- `python3 scripts/check_table_extraction_quality.py`
  - `quality_gate: PASS`
  - `article_type_metadata_coverage: 1.0000`
  - `article_type_low_confidence_rate: 0.6187`
  - `article_type_review_rate: 0.6265`

- Queue family distribution after gated backfill:
  - `unknown: 317`
  - `narrative_review: 86`
  - `empirical_v2: 56`
  - remaining families: `55`

## Current Risk State
- Hard failure modes from substring/ordering classifier bugs are fixed.
- Foundation still requires curation:
  - high type-ambiguity pool (`article_type_manual_queue.csv`: 323 rows)
  - no-claims volume remains high (`223/511 processed PDFs`)
- Conclusion:
  - pipeline is now instrumented and gateable rather than blind,
  - but manual adjudication + targeted parser upgrades are still required for gold-grade table integrity.
