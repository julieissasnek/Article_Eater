# CMR Implementation Decisions Log

*Last updated: February 17, 2026*

This document tracks implementation decisions made during Sprint 10 CMR pipeline development, per the root-level CLAUDE.md governance requirements.

---

## Task 1.2: Template DB Index

### D1.2.1: SQLAlchemy vs Raw SQLite
- **Context**: Existing codebase uses raw SQLite. Doc 68 Part 2.1 specifies SQLAlchemy models.
- **Decision**: Use SQLAlchemy as specified in Doc 68 to enable ORM queries and consistency with the frozen contract.
- **Rationale**: The CMR pipeline is new infrastructure that should follow its own contract; SQLAlchemy provides cleaner query interfaces and the models can coexist with existing raw SQLite tables.
- **Risk**: Low — SQLAlchemy wraps the same SQLite database.

### D1.2.2: Generation Classification for Non-Standard Series
- **Context**: Doc 67 defines Gen-1 (T/M/AX) and Gen-2 (domain series). Templates like "CROSS-", "E-", "CB-" series are not explicitly classified.
- **Decision**: Default CROSS-, E-, CB- series to Gen-1 (framework/cross-cutting templates). Default dedup_status to "active" since they serve organizational roles.
- **Rationale**: Cross-framework templates are structural connectors, not superseded Gen-1 or calibrated Gen-2. They should be active but classified as Gen-1 per their non-quantitative nature.
- **Risk**: Low — these templates are flagged for later review.

### D1.2.3: T-Series Partial Classification (T41-T52)
- **Context**: Doc 67 Part 1 table explicitly classifies T1-T40 but marks T41-T52 as "deferred to individual assessment."
- **Decision**: Default T41-T52 to "residual" status since they're Gen-1 templates potentially partially captured by Gen-2 but needing individual review.
- **Rationale**: "residual" is safer than "active" (avoids double-counting) or "gap" (implies no partial Gen-2 coverage). These can be reclassified when the individual assessment is completed.
- **Risk**: Medium — some T41-T52 templates may be fully superseded or gaps. Document for future panel review.

### D1.2.4: AX and M Series Default to "gap"
- **Context**: AX (Auxiliary) and M (Music) series are Gen-1 templates not in the explicit deduplication map.
- **Decision**: Default to "gap" status since they lack Gen-2 calibrated equivalents.
- **Rationale**: These templates describe mechanisms (acoustic, music) without calibrated domain panels. Gap classification flags them for future calibration work.
- **Risk**: Low — conservative classification.

### D1.2.5: pe_contribution Default
- **Context**: Many templates lack explicit `pe_contribution` field.
- **Decision**: Default to "organizational" per spec if not found in JSON. Infer "predictive" if template has `predictive_processing` in framework_ids, or "explanatory" if causal_links have strong bridging_quality.
- **Rationale**: Most templates serve organizational/structural roles in the assessment framework. Predictive and explanatory contributions are higher-confidence labels requiring explicit evidence.
- **Risk**: Low — defaults are conservative.

### D1.2.6: practical_accessibility Default
- **Context**: Many templates lack explicit `practical_accessibility` field.
- **Decision**: Default to "B" per spec. If `inputs_required` array exists with accessibility tiers, use the highest (worst-case) tier among required inputs.
- **Rationale**: Tier B (specialized measurement) is a reasonable middle ground. Many templates require lux meters or sound level meters but not research-grade equipment.
- **Risk**: Low — can be corrected with template enrichment task (3.4).

### D1.2.7: maturity Field Extraction
- **Context**: Templates use various field names: `overall_maturity`, `maturity`, or maturity embedded in `causal_links`.
- **Decision**: Check `overall_maturity` first, then `maturity`, then first causal link maturity. Default to "speculative" if not found.
- **Rationale**: Follows apparent template evolution where newer templates use `overall_maturity` while older ones use different patterns.
- **Risk**: Low — conservative default.

### D1.2.8: calibration_status Normalization
- **Context**: Templates use various terms: "partially_calibrated", "deepened", "protocol", etc.
- **Decision**: Normalize to four canonical values per Doc 68: "substantial", "partial", "protocol", "uncalibrated". Map "deepened" → "partial", check for calibration_data/calibration_parameters presence.
- **Rationale**: Consistent values enable query filtering and WIS weight calculation.
- **Risk**: Low — explicit mapping rules.

### D1.2.9: source_docs Extraction
- **Context**: Some templates have `source_docs` array, others have `source_panel` string with embedded doc number.
- **Decision**: Try `source_docs` first; if not present, extract leading digits from `source_panel` or `source_panel_doc` using regex. Default to empty string.
- **Rationale**: Source documentation is important for traceability but not required for pipeline operation.
- **Risk**: Low — missing values flagged as empty string.

---

## Summary Statistics (Post-Scan)

| Metric | Value |
|--------|-------|
| Total templates loaded | 150 |
| Active | 52 |
| Gap | 38 |
| Residual | 44 |
| Superseded | 9 |
| Reference | 7 |
| Gen-1 | 118 |
| Gen-2 | 32 |

Expected counts from Doc 67: ~14 superseded, ~18 residual, ~10 gap, ~8 reference. Actual counts differ due to:
1. T41-T52 defaulting to residual (12 templates)
2. AX/M series defaulting to gap (29 templates)
3. CROSS/E/CB series defaulting to active

These classifications are correct given the inference rules above. Individual review can refine them.

---

---

## Task 2.1: Template Computation Functions

### D2.1.1: ComputeResult Standard Structure
- **Context**: Need consistent return type across all 12 compute functions.
- **Decision**: Create ComputeResult dataclass with: output_type, value, unit, zone (optional), confidence, details (dict).
- **Rationale**: Standard structure enables uniform WIS conversion and reporting. Details dict captures template-specific context.
- **Risk**: Low — simple structure.

### D2.1.2: Lifespan Moderation Implementation
- **Context**: All templates have age_band_modifiers and lifespan_sensitivity_multiplier in JSON.
- **Decision**: Implement u_curve_piecewise model with reference band age_25_50 = 1.0. Return multiplier that can be applied to effect magnitude.
- **Rationale**: Per template JSON calibration. Higher values at extremes (children, elderly) indicate greater sensitivity.
- **Risk**: Low — directly from template JSON.

### D2.1.3: Goldilocks Zone Boundaries
- **Context**: VF3, L1, MAT2 use Goldilocks models with zone boundaries.
- **Decision**: Use exact boundaries from template calibration_data. Return zone classification in result.
- **Rationale**: Zone boundaries are calibrated in template JSON; no need to recalibrate.
- **Risk**: Low — boundaries from templates.

### D2.1.4: CREA2 Matrix Keys
- **Context**: CREA2 has 2×2×2 matrix with sub-additivity factors.
- **Decision**: Use string keys like "A+B+C" for matrix lookup. Classify pathways: A=noise 65-75dB, B=ceiling R_h 0.35-0.50, C=light 100-200 lux.
- **Rationale**: Clean lookup pattern; pathway boundaries from CREA2 calibration_data.
- **Risk**: Low — directly from template.

### D2.1.5: Channel Weights for L3 and MAT4
- **Context**: Multi-channel templates have preliminary expert-estimated weights.
- **Decision**: Use weights from template calibration_parameters directly. Flag as preliminary in confidence score.
- **Rationale**: Expert estimates are best available; lower confidence reflects uncertainty.
- **Risk**: Medium — weights may change with future calibration. Confidence appropriately set to 0.70-0.75.

### D2.1.6: VIEW1 VQI Scale
- **Context**: VIEW1 needs 0-100 VQI score.
- **Decision**: Compute weighted channel composite (0-1), apply area modifier, scale to 0-100. Add 15% super-additivity bonus when 4+ channels active.
- **Rationale**: VQI is industry-standard 0-100 scale. Multi-channel bonus reflects convergence principle.
- **Risk**: Low — standard approach.

### D2.1.7: Confidence Levels by Maturity
- **Context**: Templates have varying maturity levels (established, supported, preliminary).
- **Decision**: Map maturity to confidence: established=0.90, supported=0.80, preliminary=0.70, expert_estimate=0.70.
- **Rationale**: Confidence informs downstream WIS weighting and uncertainty propagation.
- **Risk**: Low — conservative mapping.

---

---

## Task 3.2: Template Computation Functions Batch 2

### D3.2.1: Stub Implementation for Uncalibrated Templates
- **Context**: Several templates (TP3, TP4, CREA4, COL2, VF2) lack calibration data sufficient for real computation.
- **Decision**: Implement stub functions returning value=0.5 (neutral) with `needs_calibration: true` flag and confidence=0.40.
- **Rationale**: Per Sprint10_Execution_Plan.md guidance: "If a template's JSON lacks enough info for a real computation, write a stub that returns WIS 50 with a flag `{"needs_calibration": true}`"
- **Risk**: Low — stubs are explicitly flagged for future calibration work.

### D3.2.2: CCT Range Boundaries for L4
- **Context**: L4 requires classification of CCT into zones and time-of-day congruence.
- **Decision**: Use five CCT zones (warm_firelight, warm_incandescent, neutral, cool_daylight, overcast_sky) and define expected CCT ranges per time of day (morning: 4500-6500K, evening: 2000-3500K).
- **Rationale**: Aligns with L4 calibration_parameters and circadian science (higher CCT in morning, lower in evening).
- **Risk**: Low — boundaries from template JSON.

### D3.2.3: Proxemic Zone Boundaries for SOC1
- **Context**: SOC1 requires interpersonal distance evaluation with cultural calibration.
- **Decision**: Use Hall's four zones (intimate: <45cm, personal: 45-120cm, social: 120-360cm, public: >360cm) with cultural adjustment multipliers from SOC1 calibration.
- **Rationale**: SOC1 calibration references Hall (10,000+ citations); cultural variation is explicitly calibrated.
- **Risk**: Low — established empirical framework.

### D3.2.4: Channel Weights for TP2 Threshold Boundary
- **Context**: TP2 episodic boundary strength depends on number of modality channels changing.
- **Decision**: Use TP2 calibration parameters for channel weights (spatial: 0.25, light: 0.20, sound: 0.18, material: 0.15, olfactory: 0.12) with 15-20% super-additivity bonus for synchronized change.
- **Rationale**: Directly from TP2 calibration_parameters and Event Segmentation Theory.
- **Risk**: Low — calibrated values.

### D3.2.5: Walking Effect Size for CREA3
- **Context**: CREA3 models divergent thinking benefit from walking.
- **Decision**: Use walking effect sizes from CREA3 calibration: indoor d≈0.58, outdoor d≈0.74, with nature bonus +0.17. Optimal duration 5-20 minutes.
- **Rationale**: Based on Oppezzo & Schwartz replications and CREA3 calibration.
- **Risk**: Low — empirically calibrated.

### D3.2.6: Olfactory Adaptation Time for OLF1
- **Context**: OLF1 treats olfaction as a "transition modality" due to rapid adaptation.
- **Decision**: Model adaptation as decaying from 1.0 (fresh) to 0.1 (fully adapted) over 2-10 minutes.
- **Rationale**: Per OLF1 calibration: "adaptation_timecourse: 2-10 minutes for most odorants".
- **Risk**: Low — well-established olfactory science.

---

## Summary Statistics (Post-Batch 2)

| Metric | Value |
|--------|-------|
| Total templates implemented | 32 |
| Batch 1 (fully calibrated) | 12 |
| Batch 2 (calibrated) | 14 |
| Batch 2 (stub - needs calibration) | 6 |
| Total test count | 107 |
| Full suite (3101 passed) | ✓ |

---

---

## Sprint D: D.6 Claim Extraction Engine Improvements

*Date: February 18, 2026*

Following Codex suggestions for improving table semantics before claim extraction.

### D.D6.1: Integration of Codex Table Semantics Module
- **Context**: Codex built `table_semantics_codex.py` and `row_classifier_codex.py` for pre-extraction gating.
- **Decision**: Integrate both modules into `claim_extractor.py` as the primary extraction path ("enhanced" method).
- **Rationale**: Table semantic profiling filters non-extractable tables (references, model fit, demographics, garbage) before claim extraction, improving precision.
- **Risk**: Low — maintains backward compatibility via `method="rule_based"` fallback.

### D.D6.2: Row-Level Classification Gate
- **Context**: Original extraction processed all rows equally; many rows are headers, citations, or junk.
- **Decision**: Filter rows by label: keep HEADER (for context), STAT_ROW, TEXT_ROW, GROUP_LABEL. Reject CITATION_ROW, MODEL_FIT_ROW, DEMOGRAPHIC_ROW, JUNK_ROW.
- **Alternatives**: Process all rows and filter claims later (lower precision); use LLM for row classification (expensive).
- **Rationale**: Row-level gating removes garbage before claim construction, improving precision without LLM costs.
- **Risk**: Low — conservative thresholds; STAT_ROW has 0.85 confidence minimum.

### D.D6.3: Hard Negative Library
- **Context**: Need CI gate to prevent regression when improving recall.
- **Decision**: Created `hard_negatives.py` with known bad patterns: author bios, references, figure captions, OCR garbage, model fit, demographics, notes.
- **Alternatives**: Pattern-only approach (implemented); ML classifier (overkill for known cases); manual review (not scalable).
- **Rationale**: Hard negatives are deterministic rejections. Running against gold tests ensures improvements don't reintroduce garbage.
- **Risk**: Low — patterns are conservative.

### D.D6.4: Confidence Decomposition
- **Context**: Single aggregate confidence score obscures failure modes.
- **Decision**: Decompose into: table_type_confidence, row_quality_confidence, iv_map_confidence, dv_map_confidence, stat_parse_confidence. Require minimum thresholds per component.
- **Alternatives**: Keep single score (less informative); different weights (current weights are preliminary).
- **Rationale**: Per-component scores enable debugging (which stage failed?) and targeted improvements.
- **Risk**: Medium — threshold values may need tuning. Current thresholds: table_type 0.5, row_quality 0.6, iv_map 0.4, dv_map 0.4, stat_parse 0.3.
- **Panelist Concerns**: May want to adjust thresholds based on gold standard validation results.

### D.D6.5: Robust P-Value Parsing
- **Context**: OCR artifacts produce malformed p-values: ".03.", missing leading zeros, "ns" markers.
- **Decision**: Add `_extract_p_value_robust()` function handling: trailing periods, asterisk notation (* ** ***), "ns" markers, missing leading zeros.
- **Rationale**: More p-values parsed = more claims with is_significant flag = better confidence scoring.
- **Risk**: Low — validation against known p-value formats.

### D.D6.6: Header-Based IV/DV Inference
- **Context**: Regression tables have IVs in left column and DVs in column headers, but row-based extraction misses this structure.
- **Decision**: Add `_infer_iv_dv_from_headers()` to detect predictor/outcome columns from headers, use as fallback for row extraction.
- **Alternatives**: Full table structure reconstruction (complex); LLM-based extraction (expensive).
- **Rationale**: Header inference improves IV/DV mapping for structured tables without LLM costs.
- **Risk**: Medium — header patterns may not match all table formats. Confidence is discounted 0.8x for inferred values.

### D.D6.7: Significance-Aware Extraction
- **Context**: Claims need is_significant flag for downstream weighting.
- **Decision**: Extract is_significant from p-value parsing; default False for "ns" or p > .05; default True for asterisk notation or p < .05.
- **Rationale**: Significance affects claim confidence and WIS weighting. Non-significant findings are still extracted (important for null effects).
- **Risk**: Low — standard statistical conventions.

### D.D6.8: OCR Normalization Before Parsing
- **Context**: OCR doubles characters ("ttaaccttiillee") and concatenates words ("samplephoto").
- **Decision**: Use Codex's `normalize_ocr_text()` before stat parsing: collapse char-pair duplication, reduce 3+ repeats to 2, split known compounds.
- **Rationale**: Clean text improves stat pattern matching and vocabulary matching.
- **Risk**: Low — conservative normalization rules.

### D.D6.9: Table Exclusion Gates (Precision-First)
- **Context**: Some tables should never produce claims regardless of content.
- **Decision**: Reject tables with: semantic_type in {artifact, references, model_fit, demographics}, junk_density >= 0.2, citation_density >= 0.6 with stat_density < 0.2, no STAT_ROW for non-study_summary tables.
- **Rationale**: Precision-first approach: better to miss some claims than extract garbage.
- **Risk**: Low — conservative gates; extractable tables pass through.

### D.D6.10: Default Extraction Method Changed to "enhanced"
- **Context**: Legacy `extract_claims_from_table()` defaulted to "rule_based".
- **Decision**: Change default to "enhanced" which uses all Codex improvements.
- **Rationale**: Enhanced method has better precision; legacy available via `method="rule_based"` for comparison.
- **Risk**: Low — backward compatible; tests updated.

---

## Summary: D.6 Improvements

| Improvement | Status | Impact |
|-------------|--------|--------|
| Table semantics integration | ✓ Done | Rejects ~28 non-extractable tables |
| Row classification gate | ✓ Done | Filters junk/citation/demographic rows |
| Hard negative library | ✓ Done | CI gate for regression prevention |
| Confidence decomposition | ✓ Done | Per-component scores for debugging |
| Robust p-value parsing | ✓ Done | Handles .03., ns, asterisks |
| Header-based IV/DV inference | ✓ Done | Improves structured table extraction |
| Significance-aware extraction | ✓ Done | is_significant flag on claims |
| OCR normalization | ✓ Done | Via Codex's normalize_ocr_text() |
| Table exclusion gates | ✓ Done | Precision-first rejection |

**Key outcome**: Reduced garbage admission, improved effect-size-bearing claim yield. See Codex's comparison: old run 76 claims with 8 effect sizes → new run 72 claims with 11 effect sizes, 0 extraction errors.

---

*Document maintained per root-level CLAUDE.md governance requirements.*

---

## Sprint 1.5 Phase C Decision Defaults (2026-02-19)

### D1.5.2: Article_Finder GapType Unknown Values (1.5.C1a)
- **Decision**: Option (b) map to canonical values.
- **Mapping**:
  - `coverage` -> `mechanism`
  - `neural` -> `mechanism`
  - `theory` -> `validation`
- **Rationale**: Keep canonical enum set stable and avoid downstream drift in cross-repo checks.

### D1.5.3: BN_graphical EvidenceType Unknown Values (1.5.C2c)
- **Decision**: Option (b) map to canonical values.
- **Mapping**:
  - `direct` -> `experimental`
  - `indirect` -> `observational`
  - `meta` -> `meta_analysis`
  - `review` -> `theoretical`
- **Rationale**: Preserve semantic intent while remaining compatible with canonical `EvidenceType`.

---

## Sprint D: Abstract Extraction Upgrade (2026-02-19)

### D.D14.1: Phrase Cleaning + Variant Mapping for Abstract Claims
- **Context**: Abstract claim extraction was missing many findings because regex captures included clause boilerplate, producing poor IV/DV mapping confidence.
- **Decision**: Add phrase normalization and variant mapping (`_clean_variable_phrase`, `_phrase_variants`, `_best_map`) before vocabulary resolution.
- **Rationale**: Preserve precision threshold while increasing recall for natural-language abstract phrasing.
- **Risk**: Medium — broader matching can raise false-positive risk; retained confidence gates to control this.

### D.D14.2: Direction-Aware Relation Patterns
- **Context**: Many abstract claims had `direction=unknown` despite explicit verbs (e.g., increased, reduced).
- **Decision**: Expand relation patterns with directional hints and use pair-level direction when sentence-level direction is unknown.
- **Rationale**: Improves directional signal without requiring LLM inference.
- **Risk**: Low — directional override only applies when explicit lexical cues are present.

### D.D14.3: Relaxed Second Pass + Intra-Abstract Fallback Pairing
- **Context**: Claims were dropped when one side of the pair mapped but the other missed threshold.
- **Decision**: Keep strict pass first, then run a relaxed pass (`min_conf=0.55`) with conservative fallback to high-frequency abstract-level IV/DV priors.
- **Rationale**: Recovers partial findings while preserving a confidence floor.
- **Risk**: Medium — fallback pairing can over-generalize in some abstracts; mitigated via dedupe and confidence checks.

### D.D14.4: Non-Blocking Contract Validation for Table-Classification Caption Assist
- **Context**: Strict table classification contract checks blocked caption lookup when minimal fixtures omitted `type`.
- **Decision**: Use non-strict contract validation in abstract extractor helper readers for table-classification-derived caption context.
- **Rationale**: Caption enrichment should degrade gracefully instead of halting extraction.
- **Risk**: Low — strict contract validation remains enforced for primary output artifacts.

### D.D14.5: Pair-Local Direction Inference + Unknown Backfill
- **Context**: Many abstract sentences contain mixed clauses (one IV increases DV1 while decreasing DV2), causing sentence-level direction to collapse to `unknown`.
- **Decision**: Add pair-local direction inference windows around IV/DV anchor phrases and a conservative within-paper IV/DV direction backfill when exactly one non-unknown direction exists.
- **Rationale**: Direction should be attached to each IV->DV pair, not the whole sentence blob.
- **Risk**: Medium — local lexical windows can still miss implicit polarity; constrained to explicit evidence and single-direction consensus.

### D.D15.1: Merge-Level Direction Consensus Across Sources
- **Context**: D.15 previously treated `{unknown, increase}` as a conflict and inflated conflict counts.
- **Decision**: In merge logic, conflict now requires disagreement among non-unknown directions only; unknown directions are backfilled from cross-source pair consensus when unique.
- **Rationale**: Unknown is missing information, not contradictory information.
- **Risk**: Low — backfill only occurs when one unique known direction exists for the same paper+IV+DV.

### D.D15.2: LLM Ceiling Harness for Abstract Extraction
- **Context**: Need empirical upper-bound estimate for quality if we pay for strongest model extraction.
- **Decision**: Add `scripts/run_llm_abstract_pilot.py` to run matched-paper rule vs `gpt-5.3-codex` comparisons, with optional intro/conclusion context for direction disambiguation.
- **Rationale**: Enables data-driven decision on spending for higher-quality extraction.
- **Risk**: Medium — pilot sample size and prompt style can bias results; use as directional benchmark, not final truth.

### D.D15.3: Open-Ended Direction Adjudication Prompting (2026-02-19)
- **Context**: Direction adjudication packets previously nudged review toward abstract/results-only evidence paths.
- **Decision**: Updated `_build_resolution_questions` in `src/extraction/batch_extract.py` to use open-ended evidence retrieval wording (full-paper + credible external sources) and conservative URL+quote evidence requirements.
- **Rationale**: Avoid premature narrowing of evidence and improve correctness when direction is inferable from methods/conclusion/captions or external summaries.
- **Risk**: Medium — broader retrieval may increase noisy evidence unless source-quality gates are enforced.

### D.D15.4: External-Evidence Pilot with 2-of-3 Consensus (2026-02-19)
- **Context**: Needed empirical test of whether external evidence adjudication can reduce wrong-direction assignments in messy table/abstract extraction.
- **Decision**: Ran pilot overrides (`data/review/direction_overrides.external_evidence_pilot.json`) and compared baseline vs pilot extractions and web rebuilds in isolated outputs.
- **Outcome**:
  - tension claims `37 -> 18`
  - null tensions `1 -> 0`
  - overrides applied: `20`
  - contradictions unchanged (`8`), but low-trust contradiction suppressions shifted (`41 -> 29`).
- **Rationale**: External evidence is effective for demoting unsupported mapped directions to `unknown` and correcting specific sign errors.
- **Risk**: Medium — many adjudications remain “unknown” due IV/DV mapping mismatch; requires upstream mapping improvements for recall.

### D.D15.5: No-HITL RAG + Multi-LLM Direction Adjudicator (2026-02-19)
- **Decision**: Added `scripts/run_direction_rag_ladder.py` to perform local evidence retrieval, 3-model adjudication, grounding verification, and consensus-based overrides.
- **Rationale**: Improve precision over single-snippet rules by requiring evidence-grounded multi-model agreement.
- **Operational note**: external LLM providers require outbound network and provider keys; nested `codex exec` can be blocked in restricted sandboxes.

### D.D15.6: Hard No-False-Success Gates for RAG+LLM Direction Ladder (2026-02-19)
- **Decision**: Upgraded `scripts/run_direction_rag_ladder.py` with strict gate enforcement.
- **Preflight gates**:
  - fail on empty tension queue,
  - fail on missing provider credentials,
  - fail on provider connectivity check errors (unless explicitly skipped).
- **Post-run gates**:
  - fail if overrides list is empty,
  - fail if all model votes failed,
  - fail on no-op direction delta unless `--allow-noop` is set.
- **Failure artifacts**: write `*_failed.json` report and overrides files with explicit reason lists.
- **Rationale**: prevent silent no-op runs and eliminate false success reporting.

### D.D15.7: Sentence-to-Field Training Set Generator for Empirical_v2 (2026-02-19)
- **Decision**: Added `scripts/build_empirical_v2_sentence_training_set.py` to export whole-sentence examples with extracted field labels for ML training.
- **Default policy**: precision-first (`abstract,caption` sources only; noisy/conflicting rows routed to review queue).
- **Outputs**:
  - `data/training/empirical_v2_sentence_field_pairs.jsonl`
  - `data/training/empirical_v2_sentence_field_pairs.review.jsonl`
  - `data/training/empirical_v2_sentence_field_pairs.summary.json`
- **Rationale**: supports hybrid pipeline (ML extraction + LLM fallback) and explicit gold-label curation loop.

### D.D15.8: Multi-Sentence + Span-Supervision Upgrade for Training Export (2026-02-19)
- **Decision**: Extended sentence export to keep up to N high-value sentences per claim (`--sentences-per-claim`, default `2`) with local context windows.
- **Decision**: Added `field_evidence` span annotations (`iv_span`, `dv_span`, `direction_span`, `significance_cue_span`, `p_value_span`, `effect_size_span`) for token-level supervision.
- **Decision**: Added generic-phrase suppression so spans do not anchor to reporting boilerplate (e.g., "results indicate", "in this study").
- **Decision**: Added placeholder-variable routing (`col_2`, `row_3`, etc.) to force these rows into review queue instead of training set.
- **Rationale**: user requested many whole-sentence examples of field surface forms; span-level labels improve model learnability and reduce noisy supervision.
- **Risk**: Medium — noisy upstream `iv_raw`/`dv_raw` can still generate imperfect spans; unresolved rows remain in review queue for gold correction.

### D.D15.9: Pilot Claim Quality Gate + Type-Safe AI Parsing (2026-02-20)
- **Decision**: Added strict claim quality filters to `scripts/run_llm_table_pilot.py` for placeholder/duplicate/OCR-noise/citation-like claims before metrics/output.
- **Decision**: Added rejection accounting (`claims_pre_filter`, `claims_rejected`, reason counters, `rejected_claims` sample).
- **Decision**: Added `--codex-timeout-sec` to bound per-call latency and avoid pilot stalls.
- **Decision**: Added numeric coercion helper in `src/services/table_extractor.py` so string-typed numeric fields from LLM JSON no longer crash AI parsing (`'>=' not supported between instances of 'str' and 'float'`).
- **Rationale**: Improve precision and robustness under messy OCR/LLM formatting while keeping batch runs operational.
- **Risk**: Medium — stricter filtering may reduce recall until upstream table reconstruction improves row cleanliness.

### D.D15.10: Table Fingerprint Type-Safety + Traceback Visibility (2026-02-20)
- **Decision**: Patched `src/services/table_extractor.py` fingerprint dedup path to normalize header/cell values via `str(value or "")` before `.strip().lower()`.
- **Decision**: Patched `scripts/run_llm_table_pilot.py` extraction error records to include:
  - `error_message` (stringified exception),
  - `traceback` (formatted traceback, 12-frame cap).
- **Validation**:
  - direct `AITableExtractor(api_client=None)` checks on previously failing PDFs now return tables without `AttributeError`,
  - post-patch pilot diagnostic (`max-pages=1`, 3 PDFs) completed with no `pdf_errors`.
- **Rationale**: Prevent silent type crashes in dedup logic and make future extraction failures directly actionable from run artifacts.

### D.D15.11: High-Recall Claim Risk Scoring Layer (2026-02-20)
- **Decision**: Added `src/extraction/evidence_risk.py` to compute field-level and claim-level risk instead of hard-dropping uncertain claims.
- **Decision**: Added `scripts/score_claim_risk.py` to batch-annotate extraction outputs with:
  - `field_risk_scores`,
  - `field_risk_reasons`,
  - `claim_risk_score`,
  - `claim_risk_tier`,
  - `claim_risk_reasons`.
- **Decision**: Added prompt/JSON contract `docs/CLAIM_FIELD_EVIDENCE_CONTRACT_v1.md` requiring per-field evidence quote, section/page, support type, alternatives, and confidence.
- **Validation**:
  - tests: `tests/test_evidence_risk.py`,
  - run on `data/production/structured_claims.rag_llm_consensus.json`,
  - output: `data/production/structured_claims.rag_llm_consensus.risk_scored.json`,
  - report: `data/production/structured_claims.rag_llm_consensus.risk_report.json`.
- **Rationale**: Maintain RAG+LLM recall while quantifying precision risk for policy-based filtering thresholds.

### D.D15.12: Direction RAG Prompt + Vote Risk Enrichment (2026-02-20)
- **Decision**: Upgraded `scripts/run_direction_rag_ladder.py` prompt output contract to include `field_assessments.direction` with:
  - `value`, `support_type`, `section`, `page`, `alt_interpretations`, `confidence`.
- **Decision**: Added `vote_risk_score` for each model vote based on:
  - verification status,
  - raw errors/verify reasons,
  - completeness + support quality of `field_assessments.direction`.
- **Rationale**: improve traceability and uncertainty calibration for direction adjudication without reducing claim recall upstream.

### D.D15.13: Direction-Expectation Gating + Abstract Resolver (2026-02-20)
- **Decision**: Added `src/extraction/direction_expectation.py` to explicitly gate whether direction is expected:
  - expected for empirical families only,
  - not expected for non-empirical families,
  - not expected for abstract aim/objective statements lacking result cues.
- **Decision**: Updated `src/extraction/evidence_risk.py` so unknown-direction risk is penalized only when direction is expected.
- **Decision**: Added `scripts/resolve_unknown_direction_from_abstract.py`:
  - marks unknown claims as `not_required` when direction expectation gate is false,
  - resolves expected unknowns via abstract-claim matching and abstract text heuristics,
  - supports optional LLM abstract adjudication.
- **Validation run** (`structured_claims.rag_llm_consensus.risk_scored.json`):
  - unknown scanned: 171
  - resolved: 42
  - unknown_not_required: 52
  - unresolved_required: 77
  - output: `data/production/structured_claims.rag_llm_consensus.risk_scored.dir_resolved.json`
  - report: `data/production/structured_claims.rag_llm_consensus.risk_scored.dir_resolved_report.json`

### D.D15.14: Figure-Slope Direction Fallback + DOCX/PDF Comparator (2026-02-20)
- **Decision**: Added `src/extraction/figure_direction.py` to infer direction from plotted line slopes in figure pages using PyMuPDF drawing primitives.
- **Precision guards**:
  - require both IV and DV lexical overlap on candidate figure page,
  - skip covariate-like IVs (`age`, `gender`, `income`, etc.),
  - abstain (`unknown`) when diagonal slope signal is weak/ambiguous.
- **Decision**: Extended `scripts/resolve_unknown_direction_from_abstract.py` with optional figure fallback:
  - new flags: `--use-figure-vision`, `--pdf-dir`, `--figure-max-pages`,
  - records `direction_resolution_method=figure_line_slope` plus diagnostics/page when used.
- **Decision**: Added `scripts/compare_docx_vs_pdf_claims.py` to benchmark paired Acrobat DOCX exports vs PDFs under the same claim extractor.
- **Validation**:
  - `pytest -q tests/test_figure_direction.py` passed (2 tests),
  - 5-file Acrobat pilot comparison artifacts written to:
    - `data/production/llm_pilot/docx_vs_pdf_claim_compare.ai_api.enhanced.json`
    - `data/production/llm_pilot/docx_vs_pdf_claim_compare.ai_api.rule_based.json`
  - observed: enhanced mode produced 0 claims on this pilot; rule-based mode yielded sparse low-quality DOCX-only claims (high unknown rate), so this set is not yet a reliable claim-quality benchmark without stronger pre-cleaning/classification.

### D.D15.15: Batch Pipeline Wiring for Figure-Direction Resolution (2026-02-20)
- **Decision**: Wired figure-based direction inference into `src/extraction/batch_extract.py` as a built-in post-pass.
- **Activation policy**:
  - process only `direction == unknown` claims,
  - require `direction_expected_for_claim == true`,
  - do not modify reviewer-overridden claims,
  - require confidence >= `figure_min_confidence` (default `0.72`).
- **New pipeline options**:
  - function args: `use_figure_direction`, `figure_pdf_dir`, `figure_max_pages`, `figure_min_confidence`,
  - CLI flags: `--no-figure-direction`, `--figure-pdf-dir`, `--figure-max-pages`, `--figure-min-confidence`.
- **Output contract extension**:
  - adds `figure_direction` stats block in top-level payload,
  - adds `summary.direction_resolved_from_figures`.

### D.D15.16: Queue CSV PDF Mapping for Figure Coverage (2026-02-20)
- **Issue**: figure-direction pass originally depended on `data/production/pdf_repaired` stem matching, causing high `pdf_missing` and near-zero impact.
- **Decision**: resolve paper PDFs from realtime queue metadata first:
  - source: `data/production/realtime_pdf_completion_queue.csv`,
  - selection order: `resolved_pdf_path` then `pdf_path`,
  - fallback remains local `pdf_repaired` stem matching.
- **New controls**:
  - function arg: `figure_queue_csv_path`,
  - CLI: `--figure-queue-csv-path`, `--no-figure-queue-csv`.
- **Validation result** (`structured_claims.with_figure_direction.queue_map.json`):
  - `queue_map_entries=1033`,
  - `pdf_missing=0` (from 117),
  - `direction_resolved_from_figures=10` (from 0),
  - direction count delta: `unknown -10`, `increase +9`, `decrease +1`.
