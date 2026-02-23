# RuleGraph v2 Mapping from Seven-Panel v2

This document specifies how Seven-Panel v2 panels are transformed into RuleGraph v2 rules.

## Inputs per paper

- `panel_subjects` (S)
- `panel_context` (C)
- `panel_measures` (M)
- `panel_findings` (F)
- `panel_heterogeneity` (H)
- `panel_mechanisms` (X)
- `panel_limits` (L)

## Outputs

- A set of RuleGraph v2 rules with:
  - `relation_type` and `status`,
  - typed `factor_nodes` and `outcome_nodes`,
  - `subject_scope` and `subject_moderators`,
  - `evidence` and `provenance`,
  - generalization notes and tags.

## Mapping outline

1. From Panel F (findings):
   - Identify environment/context factors and outcome constructs.
   - Create candidate factor→outcome pairs.
   - Decide `relation_type` (causal vs correlational) from design/statements.
   - Set `status` from amount and consistency of evidence.

2. From Panel S (subjects):
   - Populate `subject_scope`:
     - demographics, culture, clinical_status, traits_measured.
   - For multi-paper rules, aggregate and mark mixed samples.

3. From Panel H (heterogeneity):
   - Populate `subject_moderators` by attaching moderation patterns to rules referencing the corresponding `finding_id`.

4. From Panel M (measures):
   - Create measurement rules (`relation_type = "indicator"` / "operationalization") linking constructs to indicators.

5. From Panel C (context):
   - Optionally create structural/context rules (`relation_type = "structural"`) for context hierarchies.

6. From Panel X (mechanisms):
   - Create explanatory rules (`relation_type = "explanatory"`) linking theory nodes to phenomena.

7. From Panel L (limits):
   - Attach generalization notes and validity threats to rule `notes` and `tags`.

## Missing panels

- If a panel is missing, the corresponding fields remain null/empty (e.g., unknown subject scope, no moderators).
