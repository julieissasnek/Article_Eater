# PROMPTS FOR THREE AIs
## Paste each into the appropriate terminal
## February 15, 2026

---

# PROMPT FOR CLAUDE CODE

```
READ FIRST: docs/02-15_09_Canonical_Decisions_Record_V1_0.md

You have completed Sprint 0 tasks 0.1–0.3. Well done. Here is your next sequence of tasks.

## TASK 1 (Immediate): Review Codex Migration Patches

Codex has staged 5 migration artifacts in `migration_artifacts/` (or a branch — check for a recent branch from Codex). These are:

1. migrate_gap_type.py — patches local enum definitions → imports from canonical location
2. migrate_ci_shape.py — adapter functions for CI wire shape inconsistency
3. migrate_claim_type.py — adapter for BN→AE bridge ClaimType
4. migrate_evidence_type.py — adapter for EvidenceType across repos
5. migrate_article_type.py — crosswalk for TemplateFamily ↔ ArticleType

For each:
- Review the patch/adapter for correctness
- Check it doesn't conflict with your Sprint 0 directory changes
- Apply clean patches; flag any that conflict
- Run tests after each application to confirm nothing breaks
- If all 5 are clean, commit everything (Sprint 0 + migrations) as a single coherent commit

Expected time: 30–60 minutes. These patches are small.

## TASK 2 (Sprint 1.1): Claim Node Extensions

Add `argument_scheme` and `critical_questions` fields to claim nodes.

Reference: doc 09 Decision 1 — the canonical GapType includes CRITICAL_QUESTION and ARGUMENT_ATTACK. The claim node model needs fields to store:
- `argument_scheme: Optional[str]` — the argumentation scheme used (e.g., "argument from expert opinion", "argument from analogy")
- `critical_questions: Optional[List[str]]` — the scheme's critical questions that could defeat the argument

Update the SQLAlchemy model, create a migration, and add tests that verify:
- Existing claims still load correctly (backward compatible)
- New claims can store argument_scheme and critical_questions
- The GapType stubs `find_critical_question_gaps()` and `find_argument_attack_gaps()` can query these fields

## TASK 3 (Sprint 1.2–1.3): Enum Consolidation

Two competing enum pairs need to merge:

**1.2 Edge types**: ConstraintType (13 values) + EdgeType (19 values) → one canonical enum.
Read doc 08 (Audit Synthesis) for the collision details.

**1.3 Node types**: NodeDomain + NodeTypeFamily → one canonical enum.

For EACH consolidation:
1. Produce a reconciliation proposal FIRST — a document showing: old enum A values, old enum B values, proposed merged enum values, and the mapping from old → new.
2. Save the proposal to `docs/sprint1_enum_reconciliation.md`
3. If any mapping is ambiguous or involves a theoretical judgment call (e.g., "should EPISTEMIC_DERIVATION and COHERENCE_SUPPORT be merged or kept distinct?"), flag it explicitly with the note: "NEEDS OPUS REVIEW" — David will relay it to Opus for adjudication.
4. Only after the proposal is reviewed, implement the merge: update all imports, update DB migration, update tests.

After completing 1.2 and 1.3, run the full test suite and report results.

## IMPORTANT CONTEXT

- Total templates are now 47 (40 original + 7 from Panel IV doc 14). You don't need to encode these yet — that's Sprint 7. But be aware they exist.
- Codex will run drift checks (Sprint 1.4) after you finish the enum consolidation.
- If you hit any theoretical ambiguity, flag it for Opus rather than guessing.
- Sprint 0 gate condition: all tests pass after migration patches are applied.
```

---

# PROMPT FOR CODEX

```
READ FIRST: docs/02-15_09_Canonical_Decisions_Record_V1_0.md

## TASK 1 (Immediate): Stage Migration Artifacts

You created 5 migration scripts in Sprint 0.7. Now:

1. Run all 5 scripts in non-dry mode
2. Stage all generated artifacts (patches, adapters, reports) into `migration_artifacts/` directory
3. Commit on a SEPARATE BRANCH (e.g., `codex/sprint0-migrations`) so CC can review and cherry-pick
4. Include a README.md in `migration_artifacts/` listing each file, what it does, and what CC needs to do with it
5. Run `test_migration_lossless()` for each script one final time and include the test output in the README

CC has been instructed to review these artifacts as their immediate next task.

## TASK 2 (After CC finishes Sprint 1.2–1.3): Sprint 1.4 — Drift Check

Once CC notifies you (or David tells you) that the enum consolidation is complete:

1. Run `check_enum_drift.py` against the newly consolidated enums
2. Report ANY new cross-repo drift introduced by the merge
3. Pay special attention to:
   - The merged EdgeType/ConstraintType enum — does it match across all 5 repos?
   - The merged NodeDomain/NodeTypeFamily enum — same check
   - Any downstream services that imported the old enum values — are they updated?
4. Produce a drift report: `reports/sprint1_drift_check.md`

## TASK 3 (Background): Prepare TheoryLevel Cross-Repo Contract

This is prep work for a future sprint, but you can start now:

1. The AE-local `TheoryLevel` enum (`theory_models.py:20`) currently has `framework_theory`, `domain_theory`, etc.
2. Opus is designing a `ReductionClaim` model (Panel D-1) that will require a cross-repo theory-level enum
3. When that spec arrives, you'll need to add `TheoryLevel` to `canonical_enums.json` and update `check_enum_drift.py` to validate it
4. For now: survey all 5 repos for any existing theory-level or tier-related enums/strings/constants. Produce a preliminary inventory: `reports/theory_level_inventory.md`
5. This helps Opus and CC avoid surprises when the ReductionClaim model is implemented

## TASK 4 (Background): Characterize the 1,361 Staging Theory-Links

You reported 1,361 theory-link rows in staging (`data/review/tranche80_confirmed_rows.csv`): 1,251 ART, 102 biophilia, 3 SRT.

Please produce a detailed characterization:
1. For each theory (ART, biophilia, SRT): list the distinct edge labels used, count per label
2. What columns/fields are present in these rows? Schema description.
3. Which of the 1,170 integrated papers do these links reference? Top 10 most-linked papers.
4. Are there any rows that reference specific template IDs (T1, T2, etc.) or just theory names?
5. Save to: `reports/staging_theory_links_characterization.md`

This report will be consumed by Opus when running the Tier 2 reduction panels (Panels T2-A, T2-B, T2-C). The more detail you provide, the better those panels will work.
```

---

# PROMPT FOR ANTIGRAVITY

```
## TASK 1 (Immediate): Update Template ID Alias Map with T41–T47

Open `docs/template_id_aliases.json` and append these 7 entries to the existing array of 40:

{
  "id": "NM_REWARD_PREDICTION_ERROR_001",
  "number": 41,
  "name": "Environmental Reward Prediction Error",
  "aliases": ["NM_RPE_001"],
  "frameworks": ["NM"]
},
{
  "id": "NM_WANTING_LIKING_DISSOCIATION_001",
  "number": 42,
  "name": "Architectural Wanting-Liking Dissociation",
  "aliases": [],
  "frameworks": ["NM"]
},
{
  "id": "CROSS_MB_MF_ARBITRATION_001",
  "number": 43,
  "name": "Model-Based / Model-Free Navigation Arbitration",
  "aliases": [],
  "frameworks": ["SN", "DP", "NM"]
},
{
  "id": "CROSS_HIERARCHICAL_CONTROL_001",
  "number": 44,
  "name": "Hierarchical Control Gradient in Architectural Demands",
  "aliases": [],
  "frameworks": ["PP", "DT", "MS"]
},
{
  "id": "CROSS_PROACTIVE_REACTIVE_CONTROL_001",
  "number": 45,
  "name": "Proactive-Reactive Control Mode and Architectural Predictability",
  "aliases": ["CROSS_PROACTIVE_REACTIVE_001"],
  "frameworks": ["PP", "DT", "NM"]
},
{
  "id": "CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001",
  "number": 46,
  "name": "Thalamic Environmental Filtering (Pulvinar)",
  "aliases": [],
  "frameworks": ["MSI", "PP"]
},
{
  "id": "CROSS_WM_GAMMA_BETA_DYNAMICS_001",
  "number": 47,
  "name": "WM Gamma/Beta Dynamics in Environmental Processing",
  "aliases": [],
  "frameworks": ["MS", "DT"]
}

After appending, verify the file parses:
python3 -c "import json; data=json.load(open('docs/template_id_aliases.json')); print(f'{len(data)} templates loaded')"

Expected output: 47 templates loaded.

## TASK 2 (Prep for Sprint 7.5): Preliminary Template Extraction Inventory

While you wait for CC to build the DB models (Sprint 7.1–7.3), you can get a head start on the big Sprint 7.5 job (encoding 28 remaining templates).

For each of the 28 templates you'll need to encode (T1, T4, T6, T7, T10, T11, T13, T14, T16, T17, T18, T19, T20, T21, T22, T23, T24, T26, T28, T32, T33, T34, T35, T36, T37, T38, T39, T40):

1. Identify which source document contains the narrative specification:
   - T1–T20: `docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2_0.md`
   - T21–T30: `docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md`
   - T31–T40: `docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1_0.md`

2. For each template, extract and list:
   - Template number and name
   - Source document and approximate line range
   - Framework(s)
   - Number of causal links described in the narrative
   - Whether bridging quality and maturity are explicitly stated or need inference
   - Any Tier 2 theory references (ART, SRT, biophilia, prospect-refuge, etc.) mentioned in the narrative — flag these for Opus

3. Save to: `docs/sprint7_5_template_extraction_inventory.md`

This inventory will make the actual encoding much faster and will provide Opus with the Tier 2 cross-references needed for the reduction panels.

## IMPORTANT NOTES
- Do NOT start encoding templates into Python dataclasses yet. Wait for CC to build the DB models.
- The inventory is a planning document, not implementation.
- Pay special attention to Templates 31–40 (Panel III): Codex's audit noted that bridging quality and maturity for these are in the prose but not in structured fields. Your inventory should confirm whether you can find them in the narrative.
```

---

*Prompts created: February 15, 2026*
*All three AIs have clear immediate tasks + prep work to keep them productive.*
