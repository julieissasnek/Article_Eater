# Engineering Decisions

## 2026-02-17 — Sprint 10 Task 2.2 (CMR Data Models)

- The sprint text says "Alembic migration", but this repository currently uses
  SQL file migrations under `migrations/` and does not have an Alembic setup.
- Decision: implement migration as `migrations/021_add_cmr_models.sql` to stay
  consistent with existing migration infrastructure and runtime patterns.

## 2026-02-18 — Sprint D Task D.4 (Full CSV Audit)

- Audit of `realtime_pdf_confirmed_rows.csv` confirms significant data quality issues.
- Only ~7% of rows contain structured table data (`codex_pdfplumber`).
- ~4% of rows have identical Environment/Outcome variable strings (major parsing artifacts).
- Paper coverage is incomplete; 154 papers have zero extracted tables.
- Remediation strategy (Sprint D) confirmed as necessary.

## 2026-02-18 — Sprint D Task D.8 (Effect Size Converter)

- Implemented `src/extraction/effect_size_converter.py` as a deterministic converter with
  support for `t`, `F`, `r`, `eta_squared`, `beta`, `odds_ratio`, `cohens_d`, and
  `p_value_only`.
- `to_cohens_d()` returns Cohen's d plus uncertainty metadata (`se`, CI bounds),
  assumptions/warnings, and a Hedges' g correction (`hedges_g`) instead of silently
  replacing d.
- Chose standard-library normal quantiles (`statistics.NormalDist`) for p-value-only
  conversion to avoid adding SciPy as a new dependency.

## 2026-02-18 — Sprint D Task D.3 (Table Classifier) Dependency Gating

- Implemented `src/extraction/table_classifier.py` and unit tests now so the
  classification pass is ready.
- Did not mark D.3 complete yet because `docs/DONE.md` still lacks `D.2 DONE`,
  and Sprint D explicitly gates D.3 execution on D.2 completion.

## 2026-02-18 — Sprint D Task D.3 (Execution + Triage Format)

- Executed D.3 classification using `data/production/paper_triage.json` generated
  by `paper_triage.py`.
- Updated table classifier triage loader to support both expected structures:
  `{"paper_id": {...}}` mappings and summary format with a `papers` list.
- Produced `data/production/table_classifications.json` (2,422 tables classified).

## 2026-02-18 — Codex Isolated D10 Precision Pass (Table Semantics Layer)

- Added `src/extraction/row_classifier_codex.py` for row-level semantic labels and OCR
  normalization (header/stat/citation/demographic/model-fit/junk classification).
- Added `src/extraction/table_semantics_codex.py` to profile full tables and gate
  extractability by semantic type (`statistical_results`, `regression_coefficients`,
  `study_summary`, etc.) with explicit exclusion reasons.
- Wired `src/extraction/batch_extract_codex.py` to apply semantic profiles before D.6/D.8
  extraction and emit an isolated profile artifact:
  `data/production/table_content_profiles_codex.for_d10.json`.
- Kept all changes isolated to Codex paths to avoid contention with parallel D10 work.

## 2026-02-18 — D10 Precision/Recall Hardening from Doc71 + Addendum

- Updated `src/extraction/batch_processor.py` (AG D10 path) with:
  - robust triage format loading,
  - OCR pre-gate at table level (skip heavily corrupted tables),
  - table-type transforms for correlation matrices and stepwise regression,
  - precision gate that rejects self-matches and low-confidence forced mappings,
  - structured JSON output alongside JSONL stream output.
- Updated `src/extraction/claim_extractor.py` with:
  - numbered-header correlation matrix parsing via row-index/column-index mapping,
  - caption-first DV extraction for stepwise regression tables,
  - explicit IV header patterns for header inference,
  - semantic routing fallback from table type hints (`RESULTS_CORRELATION`, `RESULTS_REGRESSION`)
    into specialized parsers.
- Added regression tests for special table modes in `tests/test_claim_extractor.py`
  to lock correlation-matrix and stepwise-regression behavior.

## 2026-02-18 — D15 Addendum Integration (Abstract + Caption + Table Merge)

- Implemented `src/extraction/batch_extract.py` as the official D15 merge pipeline:
  - loads triage/table classification/CSV rows,
  - runs table extraction via D6,
  - applies `caption_dv_lookup.json` overrides to table DVs,
  - merges table + abstract + caption claims with provenance and conflict/corroboration tracking,
  - writes `structured_claims.json` with summary stats required by addendum.
- Added `tests/test_batch_extract_d15.py` for:
  - caption DV override behavior,
  - 3-source merge accounting (abstract/caption/table),
  - conflict/corroboration status assignment.
- Kept D15 completion unmarked in `docs/DONE.md` because dependency `D.14 DONE` is not yet logged.

## 2026-02-18 — D10 Precision Patch (Correlation/Stepwise + Hard Negatives + Type Contract)

- Hardened `src/extraction/claim_extractor.py` correlation handling with two complementary paths:
  - structured matrix parsing with robust numeric header detection and row-index mapping,
  - sentence-level fallback for messy/non-tabular correlation rows (e.g., `X and Y: r = ...`, `X r = ... with Y`).
- Added self-match guard (`iv == dv`) in enhanced extraction paths to reduce false positives from noisy OCR and forced mapping artifacts.
- Expanded `src/extraction/hard_negatives.py` patterns and detection heuristics to catch frequent misses observed in tests (`author_bio` phrasing and doubled-letter OCR garbage).
- Added article-type field contract artifact:
  - `docs/ARTICLE_TYPE_QUESTION_FIELD_CONTRACT_2026-02-18.md`
  - `src/extraction/article_type_contract.py`
- Wired D15 merge output to carry per-claim `article_type_family`, `field_contract_family`, and `provenance_depth` in `src/extraction/batch_extract.py` so downstream reasoning can distinguish abstract/caption/table evidence depth.

## 2026-02-18 — LLM Table Pilot Benchmark Harness (Upper-Bound + Degradation Curve)

- Added `scripts/run_llm_table_pilot.py` to benchmark LLM table extraction on a fixed PDF subset with controlled variants.
- Added `config/llm_table_pilot_profiles.json` with tiered model profiles (`upper_openai`, `mid_openai`, `cheap_openai`) so we can measure quality degradation as model cost decreases.
- Runner supports method variants:
  - `strict_gate`: LLM authenticity gate before extraction,
  - `heuristic_gate`: regex-based gate,
  - `no_gate`: direct extraction (recall-heavy baseline).
- Output artifacts include per-run detailed claims/table decisions plus summary metrics, enabling direct A/B comparison by profile and variant.

## 2026-02-18 — Codex Session Mode Helper

- Added `scripts/codex_mode.sh` to standardize per-session model switching while keeping global default unchanged.
- Supports modes: `max`, `balanced`, `low`, with optional task prompt and dry-run.
- Explicitly launches a NEW session (no in-place model mutation), matching Codex CLI behavior.
- Updated `docs/CODEX_MODEL_SWITCH_PLAYBOOK.md` with helper usage and a recommended low->balanced->max workflow loop.

## 2026-02-18 — Detached LLM Ladder Agent for Cross-Agent Benchmarking

- Added `scripts/run_llm_table_ladder_agent.py` to run high/balanced/low extraction tiers as managed jobs with:
  - detached background execution (`start --detach`),
  - status checks (`status --manifest ...`),
  - merged quality summary (`summarize --manifest ...`).
- Added `config/llm_table_pilot_profiles.codex.json` using `provider: codex_exec` so Codex-backed runs do not require external API keys.
- Added `docs/LLM_LADDER_AGENT_PROTOCOL.md` as the portable execution contract for Codex, CC, and AG (same inputs, same output metrics schema).

## 2026-02-18 — Single-File Operator Prompt for All Agents

- Added `docs/Pricing_Table_extraction_methods.md` as the single entrypoint file.
- Operator can now instruct any agent with one line and a role token:
  - `Follow docs/Pricing_Table_extraction_methods.md for role <ROLE> and execute it.`
- The file contains one universal prompt, required references, execution commands, and exact reporting format for comparable results.
- Added explicit CC in-session tier switching note (`/model opus|sonnet|haiku`) while preserving the same benchmark contract and outputs.
- Added AG clarification: no second conversational AG instance; use `run_llm_table_ladder_agent.py` for parallel tier benchmarking.

## 2026-02-18 — Semantic Target Pivot (Article Output, Not Grid Tables)

- Reframed extraction objective as article-type semantic records used for Web/BN rule generation, not syntactic PDF table detection.
- Updated single control file `docs/Pricing_Table_extraction_methods.md` to encode this definition and require rule-type coverage auditing.
- Added `scripts/audit_rule_type_coverage.py` to quantify:
  - missing explicit `claim_type`,
  - inferred candidate rule families,
  - candidate missing rule types,
  - coverage by article type family.
- Added `docs/ARTICLE_SEMANTIC_EXTRACTION_AND_RULE_TYPES_RETHINK_2026-02-18.md` documenting the rule-family rethink and acceptance criteria.

## 2026-02-18 — Claim Type Enforcement + Field-Targeted Extraction Metadata

- Fixed missing `claim_type` at extraction source:
  - `src/extraction/claim_extractor.py` now annotates every extracted claim with:
    - `claim_type`
    - `rule_type`
    - `article_type_family`
    - `field_contract_family`
    - `field_targets`
- Added deterministic claim-type inference heuristics (null/moderated/mechanistic/causal/associational/sample/methodology/theory/descriptive) so claims are typed even when raw extraction rows do not provide labels.
- Added field-target projection from article-family contracts, so extracted claims are explicitly tied to required/optional contract fields rather than being context-free fragments.
- Updated `src/extraction/batch_extract.py` to:
  - preserve/use `article_type_family` from triage,
  - backfill `claim_type`/`rule_type`/`field_targets` for merged abstract/caption/table claims.
- Added tests:
  - `tests/test_claim_extractor.py` (typed claims + field contract hints),
  - `tests/test_batch_extract_d15.py` (typed merged table claim contract fields).

## 2026-02-18 — D10 Deterministic Precision Iteration (No-LLM Path)

- Added robust column-semantic statistic parsing to `src/extraction/claim_extractor.py`:
  - infers `beta/r/p/t/F/eta/d/N` from header columns in `col_N` row format,
  - applies inferred semantics to numeric-only data rows.
- Expanded stat regex tolerance (`=/: optional`, signed values, noisy OCR punctuation) and direction cues (`positive/direct`, `negative/inverse` association phrases).
- Upgraded stepwise-regression extraction to use semantic column stats + sample-size inference from parsed stats.
- Added sample-size fallback inference from dfs (`t(df)` and `F(df1,df2)`).
- Fixed D15 article-family propagation in `src/extraction/batch_extract.py`:
  - if `article_type_family` is `"unknown"`, now falls back to triage `type`,
  - removed `or`-logic bug that preserved `"unknown"` and discarded usable type.
- Validation on the same 50-paper slice:
  - baseline: `data/production/structured_claims_iter1.limit50.json`
  - current: `data/production/structured_claims_iter5.limit50.json`
  - deltas: `claims +1`, `effect_size_pct +0.0617`, `unknown_direction_pct -0.0474`,
    `known_article_family_pct +0.4125` (to `1.0`).
- Recorded iteration report: `data/production/d10_iteration_report_iter5.json`.

## 2026-02-18 — Abstract/Caption Precision Upgrade (D14 Support for D15)

- Extended `src/extraction/abstract_extractor.py` to resolve abstract text from high-trust sources in priority order:
  - triage payload abstract (if quality-valid),
  - DOI-validated `article_finder.db` abstract,
  - preprocess-cache abstract fallback.
- Added title-consistency guard for DB backfill (`Jaccard >= 0.30` when both titles exist) to avoid metadata cross-link contamination.
- Added preprocess caption harvesting (`pdf_preprocess_cache`) and merged it with existing CSV caption candidates.
- Tightened caption precision rules:
  - stronger results-caption gating,
  - figure captions require explicit statistical markers,
  - non-results/schematic caption rejection expanded.
- Tightened claim emission rules for abstract/caption extraction:
  - require both IV and DV to be mapped (reject one-sided claims),
  - keep caption DV lookup generation as a separate artifact for table override.
- Added/updated tests in `tests/test_abstract_extractor.py` for:
  - DB abstract backfill,
  - preprocess abstract fallback,
  - preprocess caption extraction path.
- Regenerated artifacts:
  - `data/production/abstract_claims.json`
  - `data/production/caption_dv_lookup.json`
  - then merged via `src/extraction/batch_extract.py` into `data/production/structured_claims.json`.

## 2026-02-19 — D15 Production-Hardening Pass (Precision-First, Web-Safe Isolation)

- Scope isolation: explicitly avoided edits in `src/services/web_of_belief*` to prevent collision with parallel web modularization/performance work.
- Strengthened noisy-row suppression in `src/extraction/claim_extractor.py`:
  - header-fallback candidate generation now requires relation/statistical signal (instead of emitting from nearly any row when header hints exist),
  - conservative row-level vocabulary mapping thresholds for fallback mode,
  - explicit garbage gate applied in enhanced extraction path,
  - low-signal unknown-direction claim suppression (`unknown` + no stats + low confidence).
- Hardened merge stage in `src/extraction/batch_extract.py`:
  - added intra-source duplicate collapse (`paper_id + iv + dv + source`) using evidence-weighted selection,
  - added low-signal table claim filter (drops malformed/self/very-low-confidence claims while retaining stat-backed entries),
  - added diagnostics: `table_claims_after_filter`, `table_claims_dropped_low_signal`.
- Produced isolated candidate artifacts for side-by-side evaluation:
  - `data/production/structured_claims.codex_candidate_v2.json`
  - `data/web_persistence_v2.codex_candidate.db`
  - `docs/web_health_report_post_rebuild.codex_candidate.md`
- Observed tradeoff on full 251-paper eligible run:
  - claims: `502 -> 382`,
  - unknown direction: `51.39% -> 45.03%`,
  - table claims: `123 -> 31`,
  - conflicts: `47 -> 0` (intra-source contradictory variants collapsed),
  - gold-standard heuristic precision (script metric): `0.0312 -> 0.0769`,
  - gold-standard heuristic recall (script metric): unchanged at `0.0072`.

## 2026-02-19 — Codex Release Candidate Packaging

- Built `data/production/structured_claims.codex_release_candidate.json` from the hardened extraction path.
- Added lightweight lexical direction backfill for unknown-direction claims at merge time (`batch_extract`):
  - no-effect cue (`no significant/non-significant/ns/p>=.05`),
  - positive/negative lexical cues.
- Net change vs hardened v2 was intentionally conservative:
  - unknown direction `172 -> 171` claims.
- Rebuilt isolated web database and report from release candidate:
  - `data/web_persistence_v2.codex_release_candidate.db`
  - `docs/web_health_report_post_rebuild.codex_release_candidate.md`
- Kept canonical shared production files untouched to avoid cross-agent collisions.

## 2026-02-19 — Promotion Decision (Both Paths)

- Executed both:
  - preserved isolated RC artifacts for side-by-side comparison, and
  - promoted RC to canonical production artifacts with timestamped backups.
- Canonical promoted files:
  - `data/production/structured_claims.json` (from `structured_claims.codex_release_candidate.json`)
  - `data/web_persistence_v2.db` rebuilt from promoted claims
  - `docs/web_health_report_post_rebuild.md` regenerated
- Rollback snapshots:
  - `data/production/structured_claims.json.20260219_130732.bak`
  - `data/web_persistence_v2.db.20260219_130732.bak`
  - `docs/web_health_report_post_rebuild.md.20260219_130732.bak`

## 2026-02-19 — Theory-Guided Direction Tension Guard

- Added theory-direction tension annotation to `src/extraction/batch_extract.py`.
- For each merged claim:
  - infer candidate theory priors (ART, SRT, Biophilia, Prospect-Refuge) from IV/DV/text,
  - derive theory-expected direction for mapped outcomes,
  - flag mismatches as `theory_direction_tension` (and null-vs-theory as `theory_null_tension`) without mutating raw extraction.
- New output metadata fields on claims:
  - `theory_candidates`
  - `theory_direction_expectations`
  - `theory_direction_tension`
  - `theory_direction_conflicts`
  - `theory_null_tension`
  - `theory_null_conflicts`
- New summary counters:
  - `theory_annotated_claims`
  - `theory_direction_tension_claims`
  - `theory_null_tension_claims`
- Generated review + conservative artifacts:
  - `data/review/theory_direction_tension_queue.json` (38 flagged items)
  - `data/production/structured_claims.codex_theory_tension.json`
  - `data/production/structured_claims.codex_direction_safe.json` (37 directed claims demoted to `unknown`)
  - `data/web_persistence_v2.codex_direction_safe.db`
  - `docs/web_health_report_post_rebuild.codex_direction_safe.md`

## 2026-02-19 — Canonical Promotion to Direction-Safe Claims

- Promoted `data/production/structured_claims.codex_direction_safe.json` to canonical `data/production/structured_claims.json`.
- Rebuilt canonical `data/web_persistence_v2.db` and `docs/web_health_report_post_rebuild.md` from the promoted claims.
- New canonical state emphasizes direction safety:
  - `direction_demoted_theory_tension=37`
  - web contradiction links reduced to 22 in rebuild report.
- Rollback snapshots for this promotion:
  - `data/production/structured_claims.json.20260219_132558.bak`
  - `data/web_persistence_v2.db.20260219_132558.bak`
  - `docs/web_health_report_post_rebuild.md.20260219_132558.bak`

## 2026-02-19 — Direction Reliability Expansion (Hard Mode + Adjudication + Trust Gating)

- Implemented `direction_mode` controls in `src/extraction/batch_extract.py`:
  - `default`: preserve extracted direction, attach `direction_confidence` + `direction_evidence`.
  - `hard`: demote low-confidence directed claims to `unknown` using configurable threshold (`--direction-hard-threshold`).
- Added automatic override ingestion:
  - reads `data/review/direction_overrides.json` when present,
  - applies approved per-claim direction corrections at merge time.
- Added automatic adjudication packet generation:
  - `data/review/theory_direction_tension_queue.json`
  - `docs/HITL_LLM_RAG_direction_questions.md`
  - `data/review/direction_overrides.template.json`
  - includes HITL question, RAG query, LLM prompt, and explicit web-verification instruction.
- Added theory-direction annotation refresh after overrides/demotion so tension stats reflect final output.
- Added direction-trust-aware contradiction gating in `scripts/rebuild_web_db.py`:
  - contradiction links now require sufficient directional trust,
  - low-trust contradictions are suppressed and counted in report.
- Extended `scripts/validate_extraction.py` to emit direction-specific validation metrics section.
- Added reusable operating guide:
  - `docs/Direction_Adjudication_Protocol.md`.

## 2026-02-19 — External-Evidence Direction Pilot + Prompt Broadening

- Updated direction adjudication question generation in `src/extraction/batch_extract.py` to avoid abstract-only framing and require URL+quote support from full-paper/credible external evidence.
- Ran isolated pilot with `2-of-3` consensus overrides:
  - overrides file: `data/review/direction_overrides.external_evidence_pilot.json`
  - baseline output: `data/production/structured_claims.external_pilot_baseline.json`
  - pilot output: `data/production/structured_claims.external_pilot_with_overrides.json`
- Measured effect in pilot:
  - theory-direction tensions: `37 -> 18`
  - theory-null tensions: `1 -> 0`
  - overrides applied: `20`
- Rebuilt isolated web DBs for comparison:
  - contradictions remained `8`, while `contradiction_suppressed_low_trust` changed `41 -> 29`.

## 2026-02-19 — Added RAG + Multi-LLM Direction Ladder (No HITL)

- Added `scripts/run_direction_rag_ladder.py`:
  - local RAG retrieval from preprocess cache + existing claim quotes,
  - multi-model direction adjudication,
  - verifier checks (chunk grounding, quote presence, lexical/stat sign consistency),
  - consensus override output for `batch_extract`.
- Added runbook: `docs/RAG_LLM_Direction_Consensus_Runbook.md`.
- Added profile template: `config/direction_rag_profiles.openai.example.json`.

## 2026-02-19 — Enforced Hard Gates for Direction RAG/LLM Runner

- `scripts/run_direction_rag_ladder.py` now hard-fails with `*_failed.json` artifacts when:
  - queue is empty,
  - credentials/connectivity are missing,
  - overrides are empty,
  - all votes fail,
  - or run is no-op without explicit `--allow-noop`.
- Added optional extraction-output validation gate:
  - requires `direction_overrides_applied > 0`,
  - plus tension reduction or direction-count delta vs baseline.

## 2026-02-19 — Added Empirical_v2 Sentence->Field Training Export

- Added `scripts/build_empirical_v2_sentence_training_set.py` to build ML-ready examples from extraction outputs.
- Added runbook: `docs/EMPIRICAL_V2_TRAINING_SET_RUNBOOK.md`.
- Default export is precision-first and routes noisy/conflicting rows to review queue for gold labeling.

## 2026-02-19 — Hardened Sentence->Field Export for ML Supervision

- Upgraded `scripts/build_empirical_v2_sentence_training_set.py` to export up to N high-value sentences per claim (`--sentences-per-claim`, default `2`) instead of a single sentence.
- Added sentence-level evidence spans for `iv`, `dv`, direction cue, significance cue, `p`-value, and effect-size mention.
- Added local context windows (`context_window_text`) so each training row preserves paragraph-level expression patterns.
- Added generic-span suppression (e.g., "results indicate", "in this study") to avoid bad IV/DV span supervision.
- Added placeholder-variable guard (`col_2`, `row_3`, etc.) so noisy table labels are routed to review, not training.
- Added regression tests: `tests/test_build_empirical_v2_sentence_training_set.py`.
