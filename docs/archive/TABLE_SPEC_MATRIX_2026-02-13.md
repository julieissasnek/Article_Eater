# Table Specification Matrix (2026-02-13)

## Scope
This document consolidates the table/extraction specification currently spread across:
- `docs/EXTRACTION_TEMPLATE_*.md`
- `docs/STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md`
- `docs/SevenPanel_v2_Spec.md`
- `docs/Extraction_QC_Checklist_v18_3.md`

The goal is to define what "deep enough" means for production-grade article tables.

## Canonical Type Inventory
- Extraction template files: `17`
- Distinct extraction template families: `15`
- Stimulus schema family: `1` (`ae.stimulus.v1`)
- Seven-panel staging families: `7`
- Runtime table extractor enum families: `7` (includes `unknown`)
- Current article-type split buckets in scripts: `11`

## Distinct Extraction Template Families (15)
1. `empirical_v2`
2. `meta_analysis`
3. `systematic_review`
4. `narrative_review`
5. `theoretical`
6. `conceptual_framework`
7. `mixed_methods`
8. `observational_field`
9. `case_study`
10. `interview_study`
11. `ethnographic`
12. `grounded_theory`
13. `phenomenological`
14. `thought_piece`
15. `panel_additions` (cross-cutting requirements)

## Mandatory Depth By Family
| Family | Required minimum content depth |
|---|---|
| Empirical | Hypotheses, design, participants, scope conditions, ecological validity, measurement classification, environment/outcome canonical IDs, stimulus materials, procedure timeline, effect sizes and inferential stats, temporal dynamics, enabling conditions, causal structure, conflict assessment, limitations, reproducibility gaps, machine-readable output. |
| Meta-analysis | Search protocol, PRISMA flow, coding protocol, pooling method, heterogeneity diagnostics, moderator analyses, publication bias, homogeneity/causal coherence checks, scope from moderators, decision summary, machine-readable synthesis. |
| Systematic review | Search databases/terms, inclusion/exclusion (scope boundaries), PRISMA counts, quality tool and per-study ratings, theme-level evidence direction, conflict handling, scope/ecological validity, synthesized causal direction limits, machine-readable output. |
| Narrative review | Explicit low-confidence handling, evidence-basis tagging per claim (cited evidence vs expert opinion vs consensus), historical context, terminology usage, inferential boundaries, hard cap against treating opinion as causal evidence. |
| Theoretical | Propositions, derivation chain, proposed/forbidden edges, mediators, explicit/implicit scope and boundary silence, testability/falsification criteria, bridge warrants, machine-readable causal structure as proposed (not confirmed). |
| Conceptual framework | New terms/distinctions/taxonomy, organizing principles, implications for research and measurement, out-of-scope declarations, comparison to alternatives, conversion guidance for framework-derived rules. |
| Mixed methods | Separate quantitative and qualitative strands, integration strategy, convergence/divergence matrix, meta-inferences, integration quality scoring, causal level inherited from stronger strand with explicit caveats. |
| Observational field | Naturalistic setting description, observation protocol, inter-rater reliability, descriptive associations, ecological validity, explicit "association only" causal limit, hypotheses for experimental follow-up. |
| Case study | Case context, event timeline, data source triangulation, process tracing, outcomes, generalization limits, "what this cannot tell us", hypothesis generation. |
| Interview study | Participant profile, interview design, analytic method, themes, convergence/divergence across participants, credibility limits of self-report, perspectival scope. |
| Ethnographic | Fieldwork characteristics, cultural themes, social organization, tacit rules, transferability limits, interpretive evidence quality. |
| Grounded theory | Sampling logic, coding path, core category, category system, theory statement, substantive vs formal scope, saturation quality, generated hypotheses for later testing. |
| Phenomenological | Essence/structure of experience, first-person evidence grounding, bracketing quality, explicit non-causal stance, experiential scope boundaries. |
| Thought piece | Claim/recommendation extraction with strict opinion-vs-evidence separation, conflict-of-interest capture, asserted-causal flagging requiring external evidence. |
| Panel additions | Cross-template requirement for causal level, argument scheme, contrast class, extraction difficulty metadata, and updated rule conversion fields. |

## Stimulus Documentation: Non-Negotiable Fields
From `ae.stimulus.v1`, minimum acceptable coverage includes:
- Stimulus classification:
  - modality, source type, content type, representational level.
- Physical specification:
  - dimensions/resolution/intensity where relevant.
- Temporal parameters:
  - duration, timing, order/counterbalancing, inter-stimulus interval.
- Selection methodology:
  - source pool, inclusion logic, rating dimensions, thresholding.
- Control condition:
  - control type, matching criteria, constants held.
- Ecological validity:
  - classification + rationale + known departures from real-world exposure.
- CNfA domain features:
  - environment descriptors tied to cognition/affect mechanisms.
- Validation checklist completion.

If these are absent, stimulus descriptions are not production quality for user-facing tables or rule generation.

## Seven-Panel v2 Minimums (for downstream integration)
- `panel_subjects`: sample structure and demographic/cultural/clinical scope.
- `panel_context`: task/setting/environment typing.
- `panel_measures`: indicator modality, instrument, construct mapping.
- `panel_findings`: finding text + statistics + quote/page span when available.
- `panel_heterogeneity`: moderators and subgroup patterns.
- `panel_mechanisms`: mechanism/theory claims with support strength.
- `panel_limits`: generalization and validity threats.

## Current Script Buckets vs Template Families
`scripts/build_article_type_tables.py` currently uses 11 buckets:
- `meta_analysis`
- `systematic_review`
- `narrative_review`
- `rct_interventional`
- `quasi_experimental`
- `observational`
- `cross_sectional_survey`
- `qualitative`
- `theoretical_conceptual`
- `methods_protocol`
- `unknown`

These are useful as routing buckets, but they are coarser than the 15 template families and should not be treated as final extraction schema types.

## Quality Gate (must hold before claiming "final tables")
- Template family identified explicitly.
- Required fields for that family present or marked `unknown_with_reason`.
- Stimulus section completed to `ae.stimulus.v1` depth when environmental exposure is central.
- Scope conditions and causal level explicitly represented.
- Evidence provenance includes quote/page span when available.
- Machine-readable payload aligns with downstream claim/rule contracts.

## Provenance Markers (Mandatory)
- Abstract-derived table/rule artifacts:
  - `evidence_level`: `abstract_only_reduced_table` or `abstract_finding_rule`
  - `provenance_tier`: `abstract_provisional`
  - `requires_pdf_confirmation`: `true`
- PDF-derived table artifacts:
  - `evidence_level`: `pdf_table_extracted`
  - `provenance_tier`: `pdf_confirmed`
  - `requires_pdf_confirmation`: `no`

These markers are required so UI, rules, and BN bridge logic can distinguish provisional breadth coverage from confirmed evidence extraction.
