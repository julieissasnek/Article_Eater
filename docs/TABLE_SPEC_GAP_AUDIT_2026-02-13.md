# Table Spec Gap Audit (2026-02-13)

## Standard Used
Audit baseline is `docs/TABLE_SPEC_MATRIX_2026-02-13.md` (template families + stimulus depth + seven-panel integration).

## Critical Findings

### C1) Table claim payload is not contract-compatible with web ingestion
- Evidence:
  - `src/services/table_to_claims.py:46` emits `claim_text`, `confidence`, `metadata`.
  - `src/services/extraction_to_web.py:646` expects `statement`.
  - `src/services/extraction_to_web.py:649` expects `ae_confidence`.
  - `src/services/extraction_to_web.py:648`/`src/services/extraction_to_web.py:650`/`src/services/extraction_to_web.py:651` expect `statistics`, `constructs`, `study`.
- Impact:
  - Table-derived claims lose semantic payload during mapping (empty/partial belief content and weak theory/scope inference).
- Severity: `CRITICAL`
- Required fix:
  - Emit strict `ae.claim.v1`-compatible keys from table path, including `statement`, `ae_confidence`, `statistics`, `constructs`, and `study`.

### C2) Table claim-type vocabulary is outside epistemic mapper contract
- Evidence:
  - `src/services/table_to_claims.py:36` uses `finding|methodology|sample|effect`.
  - `src/services/extraction_to_web.py:102` supports `mechanistic|causal|associational|moderated|descriptive|null`.
- Impact:
  - Table claims get degraded/default epistemic mapping; intended rule-level semantics are not preserved.
- Severity: `CRITICAL`
- Required fix:
  - Introduce explicit table-to-claim-type mapping into supported ontology.

### C3) Extraction coverage is far below template requirements
- Evidence:
  - Runtime types are only `study_characteristics|results|demographics|quality_assessment|intervention|outcomes|unknown` in `src/services/table_extractor.py:32`.
  - Prompt coverage is only 4 concrete prompt families in `src/services/table_extractor.py:154`.
  - Spec requires 15 extraction template families + stimulus schema.
- Impact:
  - Current extractor cannot produce template-complete tables for many article types (meta/systematic/theoretical/qualitative families).
- Severity: `CRITICAL`
- Required fix:
  - Add family-aware extraction mode keyed by article type/template family with per-family required fields.

### C4) Stimulus depth contract is missing from extraction and row schema
- Evidence:
  - Stimulus template requires classification + physical specs + timing + selection + controls + ecological validity (`docs/STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md`).
  - Current `table_to_claims` metadata does not include a structured stimulus object (`src/services/table_to_claims.py:206` and surrounding claim metadata blocks).
- Impact:
  - User-visible stimulus descriptions and rule-quality signals are under-specified.
- Severity: `CRITICAL`
- Required fix:
  - Add `ae.stimulus.v1` extraction object and link by `stimulus_set_id` from claim/rule outputs.

## Major Findings

### M1) Fallback table detection can skip pages after first detection
- Evidence:
  - `src/services/table_extractor.py:482` checks `and not detected`, but `detected` is global across all pages in the loop.
- Impact:
  - If early pages match patterns, later pages with table-like text but no explicit "Table N" markers can be missed.
- Severity: `MAJOR`
- Required fix:
  - Use per-page detection state (e.g., `page_detected`) for fallback.

### M2) Article-type split buckets are coarser than extraction families
- Evidence:
  - Buckets in `scripts/build_article_type_tables.py:21` are only 11 broad classes.
  - Classifier logic is keyword-only at `scripts/build_article_type_tables.py:40`.
- Impact:
  - Routing output is useful, but not sufficient to select the right extraction template family reliably.
- Severity: `MAJOR`
- Required fix:
  - Promote classifier to a template-family router (15 families) with confidence + manual-review threshold.

## Medium Findings

### D1) Gold-pack manifest previously hid path normalization details
- Evidence:
  - Resolved in this pass by adding explicit path resolver + `resolved_pdf_path` in manifest:
    - `scripts/build_table_gold_pack.py:75`
    - `scripts/build_table_gold_pack.py:152`
    - `scripts/build_table_gold_pack.py:233`
- Impact:
  - Improves reproducibility/debuggability of "missing PDF" diagnosis.
- Severity: `MEDIUM` (fixed)
- Status: `DONE`

## Immediate Remediation Order
1. Fix table claim contract compatibility (`C1`, `C2`) before generating more final tables.
2. Add family-aware extraction paths for at least: empirical, systematic review, meta-analysis, theoretical (`C3`).
3. Add structured stimulus extraction + linkage (`C4`).
4. Patch page-local fallback detection (`M1`).
5. Upgrade article-type router from coarse buckets to template-family routing (`M2`).

## Exit Criteria For "Production-Grade Tables"
- Table-derived claims pass schema compatibility checks against web ingestion contract.
- Each processed paper has an explicit template family and required-field completeness score.
- Stimulus-rich papers include `ae.stimulus.v1` payload with validation checklist completion.
- Missing/unknown fields are explicit and justified; no silent drops.
