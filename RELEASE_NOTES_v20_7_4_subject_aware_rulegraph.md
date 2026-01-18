# Article Eater v20.7.4 — Subject-Aware RuleGraph Foundations

## Overview

This release introduces subject-aware RuleGraph v2 scaffolding and a richer Seven-Panel v2 article staging format.
Changes are structural and backward-compatible; existing pipelines should continue to run as before.

## Changes

1. **RuleGraph v2 documentation and schema**
   - Added `docs/RuleGraph_v2_Spec.md` describing the v2 rule format.
   - Extended `schemas/rule_graph.schema.json` with:
     - `graph_version`, `relation_type`,
     - typed `factor_nodes` / `outcome_nodes` (`NodeRef`),
     - structured `subject_scope` (`SubjectScope`),
     - structured `subject_moderators` (`SubjectModerator`),
     - optional `tags`, `notes`, `created_at`, `updated_at`.
   - All new fields are optional; legacy RuleGraph objects remain valid.

2. **Seven-Panel v2 documentation and schemas**
   - Added `docs/SevenPanel_v2_Spec.md` for the S/C/M/F/H/X/L panel set:
     - S (`panel_subjects`), C (`panel_context`), M (`panel_measures`),
       F (`panel_findings` v2), H (`panel_heterogeneity`),
       X (`panel_mechanisms`), L (`panel_limits`).
   - Added matching JSON schemas in `schemas/` for each panel type.

3. **BN design note**
   - Added `docs/BN_Design_with_Subjects.md` outlining how RuleGraph v2
     feeds BN design:
     - environment/context nodes,
     - subject nodes,
     - latent constructs,
     - indicators and measurement edges.

4. **Pydantic models for new panels**
   - Extended `src/contracts/schemas.py` with models for:
     - `SubjectTrait`, `SubjectDemographics`, `SubjectCulture`,
       `SubjectClinicalStatus`, `SubjectScope`,
     - `PanelSubjects`, `PanelContext`, `PanelMeasures`,
       `PanelFindingsV2`, `PanelHeterogeneity`,
       `PanelMechanisms`, `PanelLimits`.

## Compatibility and next steps

- Existing Seven-Panel uses and RuleGraph consumers are unchanged.
- New fields and panel types are currently unused by the main pipeline.
- Future sprints will:
  - wire LLM passes to populate the new panels,
  - build RuleGraph v2 rules (with subject_scope and subject_moderators),
  - surface subject-aware and relation-typed rules in the UI and BN exports.
