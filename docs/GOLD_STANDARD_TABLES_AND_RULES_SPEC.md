# Gold Standard Tables and Rules Specification

Date: February 14, 2026
Status: Canonical standard for table/rule quality
Owner: Article_Eater production pipeline
Human-readable companion: `docs/GOLD_STANDARD_TABLES_AND_RULES_HUMAN_GUIDE.md`

## 1) Purpose
This document defines what counts as **gold-standard** table and rule output for Article_Eater.
It consolidates prior guidance into one executable quality standard.

## 2) Source Documents Consolidated
- `docs/TABLE_SPEC_MATRIX_2026-02-13.md`
- `docs/STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md`
- `docs/TABLE_SPEC_GAP_AUDIT_2026-02-13.md`
- `docs/REALTIME_TABLE_RULE_PRODUCTION_LINE_2026-02-13.md`
- `docs/TABLE_EXTRACTION_QUALITY_MONITORING_2026-02-14.md`

If there is conflict, this spec is authoritative.

## 3) Gold Standard Definition
A paper output is gold-standard only if all required criteria below pass.

### 3.1 Required provenance and traceability
Every claim/rule must include:
- `paper_id`
- `claim_id` / `rule_id`
- `source_section`
- `source_page_start` and `source_page_end`
- `source_quote` and `source_quote_hash`
- `provenance_tier`
- `evidence_level`

Figure provenance policy:
- Figures used for provenance/review must be stored in project-controlled storage.
- External figure URLs are not acceptable for gold-standard artifacts.
- Allowed links are only internal links that resolve to our own database/storage assets.

### 3.2 Required semantic structure
Every paper with PDF must produce:
- Table-derived structured claims (not only abstract fallback)
- Theory linkage claims when theory language is present
- Inter-article relation claims when citation language is present
- Rule outputs linked to canonical environment/outcome IDs where resolvable

### 3.3 Stimulus depth (when exposure/stimulus is central)
Stimulus documentation must satisfy `ae.stimulus.v1` depth, including:
- Modality/type
- Physical specification (where available)
- Timing/duration/order/ISI
- Control condition and matching
- Ecological validity classification + rationale

### 3.4 Article-type completeness
Extraction must align with the paper family/template and include required fields (or `unknown_with_reason`).
No silent field drops are allowed.

### 3.5 Argument and relation quality
Claims should use explicit relation semantics where justified:
- `supports`
- `explains`
- `contradicts`
- plus argument subtype (e.g., verifies/refines/challenges/fails_to_replicate)

## 4) Quantitative Quality Gates
Primary gate runner:
- `scripts/check_table_extraction_quality.py`

Thresholds source:
- `config/table_extraction_quality_thresholds.json`

Minimum pass targets (current production gate):
- `no_claims_rate <= 0.60`
- `anchor_coverage >= 0.90`
- `unresolved_environment_rate <= 0.65`
- `unresolved_outcome_rate <= 0.65`
- `relation_type_diversity >= 6`
- `theory_link_paper_coverage >= 0.40`
- `inter_article_paper_coverage >= 0.40`

A release candidate is not gold-standard if the quality gate fails.

## 5) Gold Artifacts
Gold-standard package for a run consists of:
- `data/production/realtime_pdf_confirmed_rows.csv`
- `data/production/realtime_extraction_audit.jsonl`
- `data/review/table_quality_manual_queue.csv`
- `data/production/realtime_pdf_no_claims_review.csv`
- quality gate report output from `scripts/check_table_extraction_quality.py`

## 6) Human-in-the-Loop (Required)
Codex automation reduces workload but does not replace final adjudication.
Manual adjudication is required for:
- `manual_queue` flagged papers
- low-confidence theory links
- unresolved high-impact canonical mappings
- contradictory high-impact findings where relation type is uncertain

## 7) Cross-Model Elevation (Codex + Claude)
Using Claude Code on overlapping PDFs can raise standard **if done as independent adjudication, not overwrite**.

### 7.1 Recommended protocol
1. Select overlap sample:
- all high-impact papers + random stratified sample of remaining PDFs.
2. Run Codex and Claude independently on the same PDFs.
3. Compare field-by-field outputs (stimulus fields, canonical mapping, claim types, relations, theory links).
4. Route disagreements to human adjudication.
5. Feed adjudicated outcomes back into benchmark set.

### 7.2 Acceptance criterion for model-assisted gold
A paper can be labeled `gold_verified` when either:
- model agreement is high and no critical conflicts, or
- conflicts were human-adjudicated and resolved.

## 8) What Codex Substitutes For vs What It Does Not
Codex substitutes for:
- Large-scale deterministic validation
- Consistency checking and provenance enforcement
- High-throughput candidate extraction and relation mining

Codex does not substitute for:
- Final scientific judgment on ambiguous interpretation
- Borderline causal-vs-associational adjudication
- Nuanced stimulus interpretation when text is underspecified

## 9) Operational Commands
Run quality gate:
```bash
python3 scripts/check_table_extraction_quality.py
```

Run continuous worker with quality gate:
```bash
python3 scripts/run_realtime_production_worker.py --quality-gate
```

## 10) Versioning
When thresholds or required fields change, update:
- this document
- `config/table_extraction_quality_thresholds.json`
- relevant pipeline docs
in the same change set.
