# SYSTEM_AUDIT_REPORT_Feb22_2026

Status: IN PROGRESS (incremental checkpoint)
Date: 2026-02-22
Auditor: Codex (CX)
Scope: `docs/RUTHLESS_SYSTEM_AUDIT_PROMPT_Feb22.md`

---

## Checkpoint Summary (current)

This is an incremental save so results are recoverable if the session crashes. Findings below are evidence-backed and line-cited.

### High-confidence findings already verified

1. Core formula is mostly consistent, but there is terminology drift.
- Canonical formula appears in `docs/TRANSFER_Feb21_Session8_CORRECTED.md:71`, `docs/OPUS_REVIEW_GUIDE.md:82`, and code in `src/services/bridge_warrants.py:656`.
- Drift variant found at `docs/THEORY_HIERARCHY_AND_MECHANISMS.md:453` using `P(CNFA-specific evidence)` instead of `P(CNFA-specific)`.

2. T1 roster authority is clear, and known error docs still exist.
- Authoritative T1=10 is explicit at `docs/TRANSFER_Feb21_Session8_CORRECTED.md:77-90`.
- Explicit warning that ART/SRT are not T1 and IE-DPT is not #11 at `docs/TRANSFER_Feb21_Session8_CORRECTED.md:94-97`.
- IE-DPT error still documented at `docs/TRANSFER_Feb21_Session8_CORRECTED.md:147-150`.
- Known problematic briefing still contains bad framing (e.g., references to "new Tier 1 theory" and ART/SRT as current T1 context) at `docs/02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md:8,20,24-25,151,153`.

3. Bridge warrant priors are inconsistent between older code comments and current authority.
- Current authority (Transfer + OPUS): CONSTITUTIVE 0.75, MECHANISM 0.60, EMPIRICAL_COVARIANCE 0.60, FUNCTIONAL 0.50, CAPACITY 0.45, ANALOGICAL 0.35 (`docs/TRANSFER_Feb21_Session8_CORRECTED.md:124-131`, `docs/OPUS_REVIEW_GUIDE.md:9-17`).
- `src/services/bridge_warrants.py` has stale docstring text showing constitutive 0.85 at `src/services/bridge_warrants.py:30`, while actual runtime defaults map to 0.75 in `src/services/bridge_warrants.py:102-109`.

4. Template-count governance is currently contradictory across core docs/tools.
- `docs/TRANSFER_Feb21_Session8_CORRECTED.md` now states 151 total, 34 calibrated, 117 remaining at `docs/TRANSFER_Feb21_Session8_CORRECTED.md:156-170`.
- `docs/OPUS_REVIEW_GUIDE.md` still states 23/128/151 at `docs/OPUS_REVIEW_GUIDE.md:106`.
- `scripts/gap_tracker.py` runtime output currently reports 153 total, 30 calibrated, 120 open (run on 2026-02-22).
- Generated report confirms that mismatch at `docs/gap_registry_report.md:3,14,154`.

5. Completed panel calibrated counts from panel output files:
- `docs/STRESS_I_Panel_Output_Feb21.md`: 3 entries with `"status": "calibrated"`
- `docs/LIGHT_I_Panel_Output_Feb21.md`: 8
- `docs/SPATIAL_I_Panel_Output_Feb21.md`: 4
- `docs/VISUAL_I_Panel_Output_Feb21.md`: 8
- `docs/SOCIAL_I_Panel_Output.md`: 11
- Total observed across these 5 files: 34.

6. Panel structural-field naming drift exists.
- SPATIAL/VISUAL use `architectural_modifier_coefficients` (`docs/SPATIAL_I_Panel_Output_Feb21.md:284`, `docs/VISUAL_I_Panel_Output_Feb21.md:316`).
- Prompt/checklist language asks for "architectural modifier coefficients" (`docs/OPUS_REVIEW_GUIDE.md:55`) but some code/docs expect `architectural_modifiers` naming in places.
- This is a schema-normalization risk for ingestion.

7. Extraction-corpus quality split is real and still bifurcated.
- `data/production/realtime_tables.jsonl` currently has 12,596 rows, all `abstract_only_reduced_table` and `abstract_provisional`.
- `data/production/realtime_pdf_confirmed_rows.csv` currently has 183,582 rows.
- Queue status now (counted from `data/production/realtime_pdf_completion_queue.csv`):
  - `queued_pdf_backfill`: 452
  - `completed_pdf_extracted`: 388
  - `completed_pdf_no_claims`: 163
  - `error_pdf_processing`: 30

8. Runtime DB reality does not match some prior narrative docs.
- In `ae.db`: `articles=53`, `findings=172094`, `beliefs=0`, `templates=150`, `cmr_staging_theory_links=1045`, `rules=115`, `bridges=0`, `constraints=0`, `theories=0`.
- This means ingestion into findings is active, but web/belief graph persistence is effectively empty in this DB snapshot.

9. Web/BN/code existence check: substantial implementation exists in code.
- Web of belief module present at `src/services/web_of_belief.py`.
- Bridge warrant system present with credence product function at `src/services/bridge_warrants.py:648-683`.
- Incremental BN module present at `src/services/incremental_bn.py`.
- Staging loader for template theory links present at `src/cmr/staging_theory_loader.py`.

10. Enum drift check is currently clean.
- `python3 scripts/check_enum_drift.py` completed with `Summary: 0 drift issue(s) detected.`

---

## Evidence Extracts (verbatim snippets)

- `docs/TRANSFER_Feb21_Session8_CORRECTED.md:97`
  - "The Feb 20 panel briefing (02-20_10) contains incorrect T1 roster — do not use"
- `docs/TRANSFER_Feb21_Session8_CORRECTED.md:157`
  - "Calibrated: 34 total"
- `docs/TRANSFER_Feb21_Session8_CORRECTED.md:169`
  - "Remaining: 117 (151 − 34)"
- `docs/OPUS_REVIEW_GUIDE.md:106`
  - "23 calibrated / 128 remaining / 151 total"
- `src/services/bridge_warrants.py:30`
  - "Constitutive: 0.85"
- `src/services/bridge_warrants.py:103`
  - `BridgeType.CONSTITUTIVE: 0.75`

---

## Infra Snapshot (in progress)

- `pytest --collect-only -q` result: 4,082 tests collected.
- Full `pytest -q` run is currently in progress at the time of this checkpoint.

---

## Pending sections to complete in this same file

- Full Section 1 matrices (T1/T1.5/bridge/prior tables + compliance matrix)
- Section 2 architecture reality map and consume-panel-json verdict with field-by-field mapping
- Section 3 doc inventory current-vs-superseded map and terminology drift catalog
- Sections 4-8 completeness, sprint risk, gap tracker reconciliation, extraction pipeline health, web/BN operational status
- Section 9 top risks and go/no-go recommendation for Cowork


---

## Checkpoint 2 (incremental append)

### New critical findings since checkpoint 1

1. `SPRINT_TASK_BRIEF_for_Cowork.md` is empty.
- File exists but has 0 lines (`wc -l docs/SPRINT_TASK_BRIEF_for_Cowork.md` = 0).
- This directly breaks the audit prompt assumption that this file is the active autonomous execution authority.

2. Sprint brief references include filename drift that creates false-missing dependencies.
- `docs/SPRINT_TASK_BRIEF.md` references `_GENERALIZED_PANEL_META_PROMPT_Feb21.md`, but the actual file name on disk is `docs/*GENERALIZED_PANEL_META_PROMPT_Feb21.md` (leading `*` in filename).
- `docs/SPRINT_TASK_BRIEF.md` references `02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md`, but existing file is `docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md`.
- These are avoidable dependency-resolution failures for autonomous agents.

3. Bridge-warrant ceiling compliance is violated in template JSON artifacts.
- Automated scan across `data/templates/*.json`: 145 `(bridge_warrant, confidence)` pairs checked, 62 ceiling violations.
- Examples:
  - `data/templates/T30.json` `evening_delay_contamination_threshold`: MECHANISM 0.68 (>0.60)
  - `data/templates/L4_cct_temporal_ecological.json` `photopic_to_melanopic_conversion_by_CCT`: CONSTITUTIVE 0.88 (>0.75)
  - `data/templates/MS_RIPPLE_REPLAY_002.json` multiple MECHANISM entries at 0.65–0.80 (>0.60)
- This directly conflicts with OPUS hard rule at `docs/OPUS_REVIEW_GUIDE.md:18`.

4. Template corpus structure is heterogeneous and partially normalized.
- `data/templates/*.json` count: 184 files.
- Presence across files:
  - `display_id`: 156
  - `causal_links`: 128
  - `mechanism_chain`: 44
  - `calibrated_parameters`: 44
  - `bridge_warrant` (top-level key occurrence): 30
  - `architectural_modifier_coefficients`: 16
  - `architectural_modifiers`: 0
- This indicates mixed schema generations and incomplete harmonization.

5. Runtime template DB snapshot diverges from template-file inventory.
- `ae.db` `templates` table has 150 rows (`active` 52, `residual` 43, `gap` 39, `superseded` 9, `reference` 7).
- Files in `data/templates/` are 184.
- There is no single synchronized source-of-truth state across file corpus, template table, and gap tracker outputs.

### Test run status snapshot

- `pytest --collect-only -q`: 4,082 tests collected.
- Full `pytest -q` is still in progress at time of this append (no final pass/fail summary captured yet in this checkpoint).


---

## Checkpoint 3 (incremental append)

### Test health snapshot (captured before timeout)

- `pytest --collect-only -q`: **4,082 tests collected**.
- `pytest -q --maxfail=1`: **1 failed, 104 passed** (stopped at first failure).
- First failing test:
  - `tests/test_argument_tracing.py::test_full_trace_nature_view_claim`
  - Assertion expected `VIEW1` in matched template IDs; actual was `{'MAT4', 'SOC1'}`.

### Failure-adjacent structural evidence

During test setup, `src/cmr/template_scanner.py` emitted many warnings that template JSON files were skipped for missing required fields (commonly missing `display_id` and/or `name`).

Examples from pytest captured logs:
- `data/templates/CB2.json` skipped (missing `display_id`)
- `data/templates/T6.json`, `data/templates/T7.json`, `data/templates/T14.json` skipped (missing `display_id`)
- `data/templates/ED_HIPPOCAMPAL_ENCODING_001.json` and other MEMORY-I files skipped (missing `display_id`, `name`)
- multiple SOCIAL-I template files skipped for missing `display_id`

This strongly indicates the template corpus normalization problem is not only theoretical; it is actively impacting template matching behavior in tests.


---

## Checkpoint 4 (incremental append)

### Panel output compliance matrix update (STRESS/LIGHT/SPATIAL/VISUAL)

Automated keyword scan result against OPUS mandatory outputs (`docs/OPUS_REVIEW_GUIDE.md:47-60`):

- STRESS-I:
  - PRESENT: calibrated status markers, confidence, bridge_warrant, population modifiers, architectural modifier field, IC2, AX4, CMR integration, DOI references.
  - ABSENT/PARTIAL: explicit `RESIDUAL GAPS` section label and explicit `THEORETICAL_DEFAULT` tagging not detected.
- LIGHT-I:
  - PRESENT for all scanned mandatory categories.
- SPATIAL-I:
  - PRESENT for all scanned mandatory categories.
- VISUAL-I:
  - PRESENT for all scanned mandatory categories.

### Cross-template interaction accounting update

- STRESS-I: effectively no formal cross-template flag block detected (only a passing reference).
- LIGHT-I: multiple explicit cross-template flags (VISUAL-I L1, NEUROMOD-I T29/T6 links, MEMORY-I ED_HIPPOCAMPAL_ENCODING_001).
- SPATIAL-I: explicit cross-template set includes VISUAL-I L1, IC2, T5, MEMORY-I, AX3, AX4, Social Brain, and theory reduction linkage.
- VISUAL-I: extensive cross-template flags with targets LIGHT-I, SPATIAL-II/SC-III, VF-III, AWE/CROSSCUT, NEUROMOD-I, THEORY-REVIEW.
- SOCIAL-I: explicit cross-template flags mainly to NEUROMOD-I plus MULTI-I touch pathway.

### Parser/ingestion risk update

Attempted extraction of fenced JSON blocks (` ```json `) from the four completed panel output docs returned **0 parseable fenced JSON blocks** in each file.

Implication:
- Panel output docs are structured as narrative + inline JSON-like blocks but not consistently fenced machine-parseable JSON.
- Direct automatic ingestion from panel output markdown is therefore fragile.
- Current computational flow relies on separately normalized `data/templates/*.json` artifacts, which themselves show schema heterogeneity and missing fields.


---

## Checkpoint 5 (incremental append)

### Document inventory artifact generated

- Full docs inventory exported to: `docs/SYSTEM_AUDIT_DOC_INVENTORY_Feb22_2026.csv`
- Rows: 479 markdown documents in `docs/`.
- Heuristic status labels include `CURRENT`, `SUPERSEDED_OR_CAUTION`, `UNKNOWN`, and `EMPTY`.

Notable inventory outcomes:
- `docs/SPRINT_TASK_BRIEF_for_Cowork.md` flagged `EMPTY` (0 lines).
- `docs/TRANSFER_Feb21_Session8_CORRECTED.md`, `docs/GAP_PANEL_MASTER_PLAN_Feb21.md`, `docs/OPUS_REVIEW_GUIDE.md`, `docs/SPRINT_TASK_BRIEF.md` flagged current authority candidates.

### Context window risk estimates (from sprint brief input lists)

Computed approximate input-line loads per sprint (after resolving known filename drifts):
- S-01: 3,673 lines
- S-02: 5,230 lines
- S-03: 3,201 lines
- S-04: 4,848 lines
- S-05: 2,316 lines
- S-06: 4,903 lines
- S-07: 6,288 lines (highest)
- S-08: 1,844 lines from explicit list, but this underestimates reality because S-08 header states all prior panel outputs are required.

Interpretation:
- S-07 and S-02/S-06 are high context-pressure runs.
- S-08 is likely underspecified in concrete file listing relative to its stated dependency intent (`## Input files — ALL prior panel outputs required`).

### Dependency chain validation (brief-level)

- No explicit future-output dependency inversion found among outputs listed inside `docs/SPRINT_TASK_BRIEF.md`.
- Dependencies on pre-existing completed panels (STRESS/LIGHT/SPATIAL/VISUAL) are treated as external prerequisites and are present on disk.
- Main dependency risk is naming drift (`_GENERALIZED...` vs `*GENERALIZED...`, `V1_0` vs `V1.0`) rather than ordering.

### Remaining-template structural readiness (from `data/templates/*.json`)

File-level structural scan across 184 template JSON files:
- `calibrated`: 44
- `uncalibrated scaffold + mechanism present`: 128
- `uncalibrated scaffold only`: 12
- `minimal/broken`: 0 by heuristic

Caveat:
- These numbers conflict with transfer/gap-registry governance counts (151 total templates in authority docs vs 153 in gap tracker vs 184 JSON files).
- Therefore, readiness depends on first reconciling the authoritative template universe.

### Variable vocabulary artifact generated

- File: `docs/SYSTEM_AUDIT_VARIABLE_INVENTORY_Feb22_2026.csv`
- Extracted variable-like identifiers from template mechanisms/causal links/parameters/modifiers: 1,533 entries.
- Includes heuristic domain category and source counts for canonicalization follow-up.


---

## Checkpoint 6 (incremental append)

### Gap tracker root-cause analysis

`gap_tracker.py` is built on a legacy schema assumption and therefore misclassifies modern templates:

- Uses `parameter_range` missingness as a primary gap signal (`scripts/gap_tracker.py:17-21`).
- Uses `evidence_base` emptiness (`scripts/gap_tracker.py:23-26`).
- Uses boolean `calibrated` and/or `status` checks (`scripts/gap_tracker.py:27-31`, `93-95`).

Modern calibrated templates frequently use richer fields (`calibrated_parameters`, mechanism-level confidence/warrants, super-template interactions) that are not the same as old `parameter_range/evidence_base` patterns.

Consequence:
- The gap tracker can report templates as high/medium gaps even when other artifacts treat them as calibrated or partially calibrated.
- This is a direct mechanism for the observed 151 vs 153 vs 184 and 34 vs 30 drift patterns.

### Codebase reality map (implementation exists, integration is partial)

1. Implemented reasoning components exist in code:
- Credence product function: `src/services/bridge_warrants.py:648-683`
- Web of belief framework: `src/services/web_of_belief.py`
- Incremental BN: `src/services/incremental_bn.py`
- Template staging linker: `src/cmr/staging_theory_loader.py`

2. Template ingestion into operational tables is brittle:
- `src/cmr/template_scanner.py` requires all of `template_id`, `display_id`, and `name` or skips the file (`src/cmr/template_scanner.py:328-338`).
- Current corpus contains many files missing `display_id` and/or `name` (observed in pytest captured warnings), so scanner-level coverage is incomplete.

3. Direct parsing of panel markdown outputs is not general-purpose:
- `scripts/extract_panel_json.py` targets a hardcoded list currently containing only `VISUAL_I_Panel_Output_Feb21.md` (`scripts/extract_panel_json.py:9-11`).
- This is a one-off extraction path, not a robust panel-ingestion pipeline for all completed panels.

4. Operational DB snapshot indicates disconnected runtime graph state:
- `findings` high volume; `beliefs=0`, `bridges=0`, `constraints=0`, `theories=0` in `ae.db` snapshot.
- So foundational code exists, but active persisted web-graph instantiation is not populated in this DB.

### CMR panel-output consumability verdict (current)

- **Can code consume normalized template JSON in principle?** Yes, partially.
- **Can code reliably consume panel markdown outputs as generated?** No, not robustly; requires conversion/normalization step and schema enforcement.
- **Are panel outputs and runtime computation fully integrated end-to-end by default?** No.


---

## Checkpoint 7 (incremental append): Top Risks and Go/No-Go

### Top 5 structural risks (ordered)

1. **Template universe inconsistency (151 vs 153 vs 184)**
- Breaks planning, coverage accounting, and downstream calibration guarantees.

2. **Gap tracker legacy-schema logic**
- Current tracker (`scripts/gap_tracker.py`) relies on outdated fields and over/under-classifies calibration state.

3. **Template schema normalization failure (missing `display_id`/`name`)**
- Causes scanner skips (`src/cmr/template_scanner.py:333-338`) and directly contributes to matching/integration failures.

4. **Bridge warrant ceiling violations in template artifacts**
- 62/145 detected `bridge_warrant` + `confidence` pairs exceed declared warrant ceilings.
- Violates OPUS hard rule (`docs/OPUS_REVIEW_GUIDE.md:18`).

5. **Execution-control drift in sprint docs**
- `docs/SPRINT_TASK_BRIEF_for_Cowork.md` is empty.
- Filename mismatches in `docs/SPRINT_TASK_BRIEF.md` create avoidable dependency misses.

### Top 5 spec/doc revisions needed before next 8-panel run

1. Update `docs/OPUS_REVIEW_GUIDE.md` counts from 23/128/151 to current reconciled state.
2. Replace/repair `docs/SPRINT_TASK_BRIEF_for_Cowork.md` (empty authority doc is operationally unsafe).
3. Normalize filename references in sprint brief (`_GENERALIZED...` and `V1_0` naming drift).
4. Add explicit "superseded / do-not-use" banner to known bad docs (especially `02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md`).
5. Add canonical schema doc for template JSON v2 and enforce it pre-commit/CI.

### Shortest code-theory integration plan

1. **Schema normalizer pass (required first)**
- Backfill `display_id` and `name` for all template JSON.
- Normalize modifier field names (`architectural_modifier_coefficients` vs alternatives).

2. **Gap tracker v2 update**
- Rebase `scripts/gap_tracker.py` on current calibrated template fields (`calibrated_parameters`, mechanism-level confidence/warrant, residual gap structures) instead of legacy `parameter_range/evidence_base` assumptions.

3. **Bridge-ceiling lint stage**
- Add automated lint that fails on `confidence > prior(bridge_warrant)` and writes per-file fixes queue.

4. **Panel-output ingestion standardization**
- Require fenced JSON blocks or direct JSON artifacts for each panel output block.
- Replace one-off extractor behavior with a deterministic panel artifact loader.

5. **Live registry reconciliation command**
- Single command to reconcile template counts across: transfer authority, templates table, template files, and gap registry.

### Retroactive compliance estimate

- **STRESS-I + LIGHT-I + SPATIAL-I retroactive normalization/validation**:
  - Schema normalization + field harmonization: ~4–8 engineering hours
  - Bridge-ceiling and THEORETICAL_DEFAULT audit/fixes: ~4–6 hours
  - Total: ~1–2 focused engineering days

### Should Cowork proceed now?

**Recommendation: CONDITIONAL PAUSE (short).**

Proceed only after these blockers are fixed:
1. Restore a non-empty authoritative Cowork brief.
2. Resolve sprint input filename drift.
3. Run template normalization so scanner no longer skips core templates.
4. Update gap tracker to current schema and rebaseline counts.

If those are completed, autonomous panel execution can continue with materially lower risk.


---

## Checkpoint 8 (incremental append): Cross-template flag routing health

Automated extraction across LIGHT/SPATIAL/VISUAL/SOCIAL panel outputs found 79 explicit assignment references to 15 target labels.

Most frequent targets:
- `NEUROMOD-I`: 15
- `SOCIAL-I`: 12
- `LIGHT-I`: 10
- `VISUAL-I`: 10
- `SC-III`: 6
- `AWE-I`: 5
- `VF-III`: 4

### Orphan / non-brief targets

Targets found in flags but not represented as sprint panels in the current sprint brief include:
- `SC-III`
- `VF-III`
- `SPATIAL-II`
- `THEORY-REVIEW`
- `STRESS-I-ADDENDUM-UPDATE`
- `AX-I`
- `THEORY-REDUCTION`

This indicates unresolved routing between panel-era flags and current sprint-era panel nomenclature.

### Circular dependencies observed

At least one bidirectional flag loop exists:
- LIGHT-I flags VISUAL-I (L1-related interactions)
- VISUAL-I flags LIGHT-I (T1/L1 dapple and overlap interactions)

Circular interaction references are not necessarily wrong, but they require explicit anti-double-counting rules and tie-break logic in the integration layer.

### AWE-I naming inconsistency persists in artifacts

Transfer authority explicitly states AWE-I should not exist as a standalone panel and AX3 belongs to CROSSCUT-I (`docs/TRANSFER_Feb21_Session8_CORRECTED.md:181-185`).
Yet multiple output artifacts still assign flags to `AWE-I`.


---

## Checkpoint 9 (incremental append): Provisional section-level verdicts

### Section 1 (theoretical integrity)
- Formula: mostly consistent; minor terminology drift.
- T1 roster: authoritative source clear; old conflicting docs still present.
- Bridge hierarchy: authoritative priors consistent in key docs, but artifact-level confidence-ceiling violations exist.
- Template count: not reconciled across authority docs, gap tracker, DB, and file corpus.

### Section 2 (code reality)
- Core reasoning code exists (web, bridge, BN, CMR services).
- Integration is partial and brittle: template normalization and ingestion path inconsistencies block reliable end-to-end operation.

### Section 3 (spec vs reality)
- Significant document/version sprawl; inventory artifact generated.
- Execution authority drift present (`SPRINT_TASK_BRIEF_for_Cowork.md` empty).
- Terminology and filename drift produce operational risk.

### Section 4 (template completeness)
- Many templates structurally present; calibrated subset depends on which corpus is treated as authoritative.
- Schema heterogeneity remains high across template JSON files.

### Section 5 (sprint risk)
- Dependency ordering mostly workable.
- Main risks are naming drift, high context load, and review-bottleneck process overhead.

### Section 6 (gap tracker)
- Script exists and runs, but logic is legacy and not aligned with modern calibration schema.

### Section 7 (extraction pipeline)
- Strong production volume exists (CSV stream), but abstract/provisional and PDF-confirmed streams remain split and easy to misread.

### Section 8 (web/BN status)
- Implementation exists in code.
- Runtime DB snapshot shows no active populated belief/bridge/constraint graph in `ae.db`.

### Section 9 (recommendation)
- Short conditional pause, reconcile schema/count/governance, then resume autonomous panels.


---

## Checkpoint 10 (incremental append): T1 roster discrepancy table (manual adjudication)

| Document | T1 count stated | Includes ART/SRT as T1? | Includes IE-DPT as T1 #11? | Evidence |
|---|---:|---|---|---|
| `docs/TRANSFER_Feb21_Session8_CORRECTED.md` | 10 | No | No | Explicitly states both are errors (`:94-97`, `:147-150`) |
| `docs/02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md` | Implies legacy set | **Yes** | **Yes** | Calls for a "new Tier 1 theory" (`:1`, `:8`) and lists ART/SRT under current T1 framing (`:20-25`, `:151-153`), then says new theory would be #11 (`:160`) |
| `docs/IE_DPT_Full_T1_Specification.md` | 10 | No (after revision note) | No (after revision note) | Feb 22 revision note corrects prior error (`:7`) |
| `docs/OPUS_REVIEW_GUIDE.md` | Not listing full roster | No | No | Explicitly treats both as errors (`:73-74`) |
| `docs/02-14_07_Theory_Tier_Architecture_V1.0.md` | Historical 8-framework phase | No | No | Pre-later expansions; not current authority |


---

## Checkpoint 11 (incremental append): Bridge prior consistency table

| Warrant Type | Prior P (OPUS) | Prior P (Transfer) | Prior P (code defaults) | Artifact compliance snapshot |
|---|---:|---:|---:|---|
| CONSTITUTIVE | 0.75 | 0.75 | 0.75 | Violations observed (e.g., 0.88 in `L4_cct_temporal_ecological.json`) |
| MECHANISM | 0.60 | 0.60 | 0.60 | Frequent >0.60 confidence values in artifacts |
| EMPIRICAL_COVARIANCE | 0.60 | 0.60 | 0.60 | Some >0.60 in artifacts |
| FUNCTIONAL | 0.50 | 0.50 | 0.50 | Some >0.50 in artifacts |
| CAPACITY | 0.45 | 0.45 | 0.45 | Some >0.45 in artifacts |
| ANALOGICAL | 0.35 | 0.35 | 0.35 | Some >0.35 in artifacts |

Notes:
- OPUS table: `docs/OPUS_REVIEW_GUIDE.md:9-17`.
- Transfer table: `docs/TRANSFER_Feb21_Session8_CORRECTED.md:124-131`.
- Code defaults: `src/services/bridge_warrants.py:102-109`.
- Hard-rule ceiling statement: `docs/OPUS_REVIEW_GUIDE.md:18`.
- Legacy comment drift remains in code docstring (`Constitutive 0.85`) at `src/services/bridge_warrants.py:30`.


---

## Checkpoint 12 (incremental append): Extraction pipeline health snapshot

### Spot-check and coverage (PDF-confirmed stream)

Artifact examined: `data/production/realtime_pdf_confirmed_rows.csv`

- Header width: 74 columns.
- Parsed row count via CSV reader: 172,091 rows.
- `provenance_tier`: `pdf_confirmed` on all parsed rows.
- `evidence_level` split:
  - `pdf_discourse_extracted`: 159,707
  - `pdf_table_extracted`: 12,384

### Critical quality issue in this artifact

The column set includes no populated free-text claim field under `claim_text` in parsed rows:
- `null_claim_text`: 172,091 / 172,091 (100%)

Interpretation:
- This artifact appears to represent structured relation rows/metadata, not directly human-readable extracted claim text.
- It can still be useful for downstream structured pipelines, but it is not self-sufficient for manual semantic QA without joining to other artifacts.

### Additional caveat

Line-count based row estimates and CSV-parser row counts differ significantly, indicating embedded newlines/quoting effects in records. Downstream counters should use robust CSV parsing, not plain line counts.


---

## Checkpoint 13 (incremental append): DB schema state for calibration metadata

`ae.db` schema snapshot shows calibration metadata is mostly indirect (JSON blobs), not strongly typed relational columns.

- `cmr_template_activations`:
  - Has `inputs` (JSON), `outputs` (JSON), `interaction_adjustments` (JSON), `wis_score`, `wis_confidence`.
  - Does **not** expose explicit typed columns for parameter tables, boundary values, channel weights, uncertainty estimates, or lifespan moderation.
- `templates` table:
  - Stores high-level metadata + `json_path` pointer, but not detailed calibrated parameter structures as typed columns.
- `findings` table:
  - Stores effect size / CI / sample size but no direct bridge-warrant or panel-calibration metadata.

Conclusion:
- System can store rich calibration details only if serialized into JSON payloads and referenced consistently.
- Strongly typed DB-level enforcement for calibration schema is currently absent.


---

## Checkpoint 14 (incremental append): Template-field coverage for code consumption

Coverage scan across `data/templates/*.json` (184 files):

| Field | Files with non-empty field |
|---|---:|
| `mechanism_chain` | 44 |
| `causal_links` | 128 |
| `bridge_warrant` | 30 |
| `calibrated_parameters` | 44 |
| `population_modifiers` | 18 |
| `architectural_modifier_coefficients` | 16 |
| `super_template_interactions` | 33 |
| `cross_template_flags` | 0 |

Interpretation:
- The corpus is mixed across schema generations.
- Required CMR fields for full integration are only present on a subset of template files.
- `cross_template_flags` are represented in narrative panel docs and assignment commands, but not as normalized top-level field in current template JSON corpus.


---

## Checkpoint 15 (incremental append): Specification-code alignment (coarse)

| Document | Implementation % (coarse) | Stale assumptions | Contradictions |
|---|---:|---|---|
| `docs/TRANSFER_Feb21_Session8_CORRECTED.md` | ~65% | Some sprint references still rely on legacy panel names/files | Count drift vs gap tracker/template corpus |
| `docs/GAP_PANEL_MASTER_PLAN_Feb21.md` | ~60% | Assumes stable registry identity | Registry currently unresolved (151/153/184 split) |
| `docs/OPUS_REVIEW_GUIDE.md` | ~70% | Header counts stale (23/128) | Artifact confidence exceeds bridge ceilings in many files |
| `docs/SPRINT_TASK_BRIEF.md` | ~55% | Filename references with drift; assumes companion Cowork brief | `SPRINT_TASK_BRIEF_for_Cowork.md` empty |
| `docs/*GENERALIZED_PANEL_META_PROMPT_Feb21.md` | ~50% | Assumes deterministic panel-output JSON blocks | Panel markdown not consistently machine-parseable fenced JSON |
| `docs/IE_DPT_Full_T1_Specification.md` | ~75% | Historical contamination documented | Revision note correct, but ecosystem still contains old conflicting briefing artifacts |


---

## Checkpoint 16 (incremental append): Unresolved items + immediate fix order

### Still unresolved in this audit pass

1. Full manual per-template audit table for all 23/34 calibrated templates at parameter-granularity (time-intensive; partially covered via scans).
2. Exhaustive orphan-reference graph across all 479 docs (inventory artifact generated; full graph extraction not yet appended).
3. Automated normalization of all template files (identified, not executed in this audit-only run).

### Immediate fix order (execution sequence)

1. **Governance hotfix**
- Populate `docs/SPRINT_TASK_BRIEF_for_Cowork.md` or retire it and point all automation to `docs/SPRINT_TASK_BRIEF.md`.
- Fix filename drift references in sprint brief.

2. **Registry reconciliation**
- Decide authoritative template universe.
- Rebuild `templates` table + `gap_registry.json` from normalized source set.

3. **Schema normalization**
- Backfill missing `display_id`/`name` for templates currently skipped by scanner.
- Normalize key fields for modifiers/interactions.

4. **Rule/ceiling lints**
- Enforce bridge-warrant confidence ceilings in CI.
- Fail fast on violations before panel outputs are accepted.

5. **Integration smoke test**
- Re-run `pytest -q --maxfail=1` until the `test_full_trace_nature_view_claim` path reliably maps expected templates (including `VIEW1`).


---

## Checkpoint 17 (incremental append): Terminology drift audit

### Bridge-warrant vocabulary drift

Canonical 6-level warrant set in authority docs:
- CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL

But code-level enum in `src/services/bridge_warrants.py` adds three extra types:
- `EPISTEMIC_COHERENCE_WARRANT`
- `ARGUMENTATIVE_WARRANT`
- `EPISTEMIC_VIGILANCE_WARRANT`

This is a spec-code drift unless explicitly ratified in the authoritative docs.

### Artifact warrant-value hygiene drift

Template JSON scan found non-canonical/dirty `bridge_warrant` values, e.g.:
- `THEORETICAL_DEFAULT` used as if it were a warrant value
- `see_SC1`
- long free-text warrant strings

These should be normalized to canonical enum values and moved explanatory text to notes/flags fields.

### Template ID format drift

Across docs corpus, three active ID regimes coexist heavily:
- Legacy `T#` IDs (e.g., T1, T22, T55) — high frequency.
- Series short IDs (e.g., VF3, SC4, L2, CREA4) — high frequency.
- Long-form canonical IDs (e.g., `NATURE_VIEW_CONVERGENCE_001`) — high frequency.

This multi-regime usage is expected historically, but computational pipelines need deterministic crosswalk mapping to avoid duplicate references and mismatched joins.

### Panel-target naming drift in cross-template routing

Cross-template assignment targets include non-sprint labels (`SC-III`, `VF-III`, `SPATIAL-II`, `THEORY-REVIEW`, `AX-I`, etc.) that are not first-class sprint panels in current brief naming.

Net effect:
- Routing from panel flags to active sprint task board remains partially manual and error-prone.


---

## Checkpoint 18 (incremental append): Web-of-belief operational status correction

Important correction to earlier DB interpretation:

- `ae.db` has `beliefs=0`, but this is **not** the only runtime web store.
- Canonical web DB resolution (`src/services/db_locator.py`) chooses between:
  - `data/web_persistence.db`
  - `data/web_persistence_v2.db`

Current profiles:
- `data/web_persistence.db`:
  - beliefs: 12,668
  - constraints: 37,657
  - bridges: 1,898
- `data/web_persistence_v2.db`:
  - beliefs: 106
  - constraints: 527
  - bridges: 0

`resolve_web_db(prefer='integrated')` selects `data/web_persistence.db`.
`resolve_web_db(prefer='latest')` selects `data/web_persistence_v2.db`.

Therefore:
- The web-of-belief system is operational and populated in the integrated DB path.
- There is a **multi-DB ambiguity risk**: tools choosing `latest` may see a much smaller graph and report misleadingly sparse state.


---

## Checkpoint 19 (immediate save on request)

User-requested immediate checkpoint saved.

Live test run status at save time (`pytest -q --maxfail=20`):
- Passed through at least 61% progress before output paused.
- Multiple failures already observed in progress stream (beyond the first known argument-tracing failure).
- Final failure summary not yet captured at this exact checkpoint.


---

## Checkpoint 20 (finalized snapshot): Full test-suite result and implications

Completed run:
- Command: `pytest -q --maxfail=20`
- Runtime: ~21m49s
- Result: **15 failed, 4049 passed, 18 skipped**

High-signal failing tests (representative):
1. `tests/test_argument_tracing.py::test_full_trace_nature_view_claim`
2. `tests/test_cross_pipeline.py::test_cross_pipeline_salk_view_consistency`
3. `tests/test_template_record.py::TestScanTemplates::test_all_150_files_load`
4. `tests/test_template_theory_dependencies.py::...active_templates_map_to_existing_theories`
5. `tests/test_sprint_verification.py::test_s10_no_orphan_json_files`
6. `tests/test_sprint_verification.py::test_s11_paper_eval_finds_view1`

Observed root-cause cluster from failing logs:
- Many template files are skipped by scanner due to missing required fields (`display_id` and/or `name`) per `src/cmr/template_scanner.py:333-338`.
- This directly impacts template matching and cross-pipeline expected mappings (e.g., missing `VIEW1` match paths).
- Theory-reference integrity test reports 108 templates with invalid theory refs (70 unique missing theory IDs), indicating unresolved ontology crosswalk between template `framework_ids` and web theory IDs.

Final audit stance (unchanged):
- Core architecture is substantial and valuable.
- Main blockers are integration hygiene and governance drift (schema normalization, registry reconciliation, and naming authority consistency), not absence of foundational code.

---

## Finalization Note

This report is intentionally checkpoint-structured for crash resilience and has been incrementally saved throughout the run.
Companion artifacts generated:
- `docs/SYSTEM_AUDIT_DOC_INVENTORY_Feb22_2026.csv`
- `docs/SYSTEM_AUDIT_VARIABLE_INVENTORY_Feb22_2026.csv`


[save-marker] manual resave confirmation requested by user (Codex).
