# Article Types and Table Standards (Unified)

Date: 2026-02-14  
Audience: Codex/Claude table extraction and QA work  
Scope: Article types, table schemas, rule conversion standards, provenance rules, and quality gates.

## 1) Purpose
This is the single consolidation document for how Article_Eater should build and validate article tables by type.

Use this as the operational source of truth for:
- Table construction by article family.
- Abstract-reduced vs PDF-confirmed outputs.
- Rule conversion expectations.
- Theory/inter-article relation extraction.
- Gold-standard quality checks.

## 2) Source-of-Truth Precedence
If guidance conflicts, use this order:
1. `docs/GOLD_STANDARD_TABLES_AND_RULES_SPEC.md`
2. `docs/TABLE_SPEC_MATRIX_2026-02-13.md`
3. `docs/STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md`
4. `docs/EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md`
5. Latest dated family template for that article type (normally `2026_02_09` where present)
6. Older family templates (`2026_02_03`/`2026_02_04`) for non-conflicting detail only

## 3) Canonical Article-Type Families
The canonical inventory is 15 families:
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
15. `panel_additions` (cross-cutting, mandatory)

Coarse routing buckets in scripts are not final schemas and must not replace these families.

## 4) Canonical Template Files by Family
Use these as primary templates:

| Family | Canonical template |
|---|---|
| empirical_v2 | `docs/EXTRACTION_TEMPLATE_EMPIRICAL_v2_2026_02_03.md` |
| meta_analysis | `docs/EXTRACTION_TEMPLATE_META_ANALYSIS_2026_02_03.md` |
| systematic_review | `docs/EXTRACTION_TEMPLATE_SYSTEMATIC_REVIEW_2026_02_03.md` |
| narrative_review | `docs/EXTRACTION_TEMPLATE_NARRATIVE_REVIEW_2026_02_09.md` |
| theoretical | `docs/EXTRACTION_TEMPLATE_THEORETICAL_2026_02_09.md` + retain non-conflicting rigor checks from `docs/EXTRACTION_TEMPLATE_THEORETICAL_2026_02_03.md` |
| conceptual_framework | `docs/EXTRACTION_TEMPLATE_CONCEPTUAL_FRAMEWORK_2026_02_04.md` |
| mixed_methods | `docs/EXTRACTION_TEMPLATE_MIXED_METHODS_2026_02_09.md` |
| observational_field | `docs/EXTRACTION_TEMPLATE_OBSERVATIONAL_FIELD_2026_02_09.md` |
| case_study | `docs/EXTRACTION_TEMPLATE_CASE_STUDY_2026_02_09.md` |
| interview_study | `docs/EXTRACTION_TEMPLATE_INTERVIEW_STUDY_2026_02_09.md` |
| ethnographic | `docs/EXTRACTION_TEMPLATE_ETHNOGRAPHIC_2026_02_09.md` |
| grounded_theory | `docs/EXTRACTION_TEMPLATE_GROUNDED_THEORY_2026_02_09.md` |
| phenomenological | `docs/EXTRACTION_TEMPLATE_PHENOMENOLOGICAL_2026_02_09.md` |
| thought_piece | `docs/EXTRACTION_TEMPLATE_THOUGHT_PIECE_2026_02_09.md` |
| panel_additions | `docs/EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md` |

## 5) Family-Specific Minimum Content Depth
Each table must include these minimums (or `unknown_with_reason`):

| Family | Required minimum depth |
|---|---|
| Empirical | Hypotheses, design, participants, scope conditions, ecological validity, measurement classification, canonical environment/outcome IDs, stimulus materials, timeline, effect sizes/inferential stats, temporal dynamics, enabling conditions, causal structure, conflict assessment, limitations, reproducibility gaps, machine-readable payload. |
| Meta-analysis | Search protocol, PRISMA flow, coding protocol, pooling method, heterogeneity diagnostics, moderators, publication bias, homogeneity/causal coherence checks, scope from moderators, decision summary, machine-readable synthesis. |
| Systematic review | Search/inclusion/exclusion boundaries, PRISMA counts, quality tool/ratings, theme-level evidence direction, conflict handling, scope/ecological validity, explicit causal-direction limits, machine-readable synthesis. |
| Narrative review | Low-confidence handling, evidence-basis tags per claim (evidence vs opinion), historical context, terminology usage, inferential boundaries, strict cap against treating opinion as causal evidence. |
| Theoretical | Propositions, derivation chain, proposed/forbidden edges, mediators, explicit/implicit scope, boundary silence, testability/falsification criteria, bridge warrants, machine-readable proposed structure (not confirmed). |
| Conceptual framework | Terms/distinctions/taxonomy, organizing logic, implications for research/measurement, out-of-scope declarations, alternatives comparison, framework-to-rule conversion guidance. |
| Mixed methods | Separate quantitative and qualitative strands, integration strategy, convergence/divergence matrix, meta-inferences, integration quality, causal level inherited from stronger strand with caveats. |
| Observational field | Naturalistic setting, observation protocol, inter-rater reliability, descriptive associations, ecological validity, explicit association-only causal boundary, hypotheses for experiments. |
| Case study | Case context, timeline, triangulation, process tracing, outcomes, generalization limits, explicit non-claims, hypothesis generation. |
| Interview study | Participant profile, interview design, analytic method, themes, participant convergence/divergence, self-report credibility limits, perspectival scope. |
| Ethnographic | Fieldwork characteristics, cultural themes, social organization, tacit rules, transferability limits, interpretive evidence quality. |
| Grounded theory | Sampling logic, coding path, core category, category system, theory statement, substantive/formal scope, saturation quality, generated hypotheses. |
| Phenomenological | Essence/structure of lived experience, first-person evidence grounding, bracketing quality, explicit non-causal stance, experiential scope boundaries. |
| Thought piece | Claims/recommendations extraction with hard opinion-vs-evidence separation, COI capture, asserted-causal flagging requiring external verification. |

## 6) Mandatory Cross-Cutting Fields (Panel Additions)
All extraction families must include:

1. `causal_level`
- Allowed: `association|intervention|counterfactual`
- Required for empirical claims.

2. `argument_scheme`
- Required for all claims.
- Include critical questions and unaddressed questions.

3. `contrast_class` and `difference_maker`
- Required for explanatory claims.

4. `extraction_difficulty` and `source_zone`
- Required for audit/calibration.
- `source_zone`: `abstract|introduction|methods|results|discussion|conclusion|table|figure`.

## 7) Stimulus Standard (Non-Negotiable)
When stimulus/exposure is central, include structured `ae.stimulus.v1` data with:
- Classification: modality, format, environment type, representational level.
- Physical specs: dimensions/resolution/intensity (as applicable).
- Temporal parameters: duration, order/counterbalancing, ISI.
- Selection methodology: source, inclusion logic, thresholds, matching.
- Control condition: type, matching criteria, constants held.
- Ecological validity: level + rationale + transfer caveats.
- CNfA domain features and design implications.
- Validation checklist completion.

If this depth is missing, output is not production quality for stimulus-driven claims.

## 8) Provenance and Tiering Policy (Abstract vs PDF)
Abstract-derived outputs must be marked:
- `evidence_level`: `abstract_only_reduced_table` (table) or `abstract_finding_rule` (rule)
- `provenance_tier`: `abstract_provisional`
- `requires_pdf_confirmation`: `true`

PDF-derived outputs must be marked:
- `evidence_level`: `pdf_table_extracted`
- `provenance_tier`: `pdf_confirmed`
- `requires_pdf_confirmation`: `no`

Both tiers are required in production. Abstract outputs give breadth early; PDF outputs are confirmation-grade.

## 9) Required Claim/Rule Traceability
Each claim/rule must include:
- `paper_id`
- `claim_id` or `rule_id`
- `source_section`
- `source_page_start` and `source_page_end`
- `source_quote`
- `source_quote_hash`
- `provenance_tier`
- `evidence_level`

Figure policy:
- Gold review uses stored figure assets in project-controlled storage.
- External figure URLs are not acceptable for gold artifacts.

## 10) Theory and Inter-Article Relation Requirements
For PDF outputs, extraction must scan introduction/related work/discussion/conclusion and emit:
- `claim_type=theory_link`
- `claim_type=inter_article_relation`

Core relation families for argument layer:
- Web-level relation: `supports|explains|contradicts`
- Subtype examples: `verifies`, `tests`, `refines`, `elaborates`, `challenges`, `fails_to_replicate`, `cites_background`

Relations must be evidenced, not decorative.

## 11) Seven-Panel v2 Compatibility
Per-paper staging must support:
1. `panel_subjects`
2. `panel_context`
3. `panel_measures`
4. `panel_findings`
5. `panel_heterogeneity`
6. `panel_mechanisms`
7. `panel_limits`

QC minimum:
- All 7 panels present or explicit `unknown` with reason.
- Findings include quote + page span when available.
- Stats/effect sizes included if reported.
- Limits/confounds captured when present.

## 12) Quality Gate Thresholds (Production)
From `config/table_extraction_quality_thresholds.json`:
- `no_claims_rate <= 0.60`
- `anchor_coverage >= 0.90`
- `unresolved_environment_rate <= 0.65`
- `unresolved_outcome_rate <= 0.65`
- `relation_type_diversity >= 6`
- `theory_link_paper_coverage >= 0.40`
- `inter_article_paper_coverage >= 0.40`
- `manual_review_backlog <= 400`

Per-PDF minima:
- `min_theory_links_per_pdf >= 1`
- `min_inter_article_relations_per_pdf >= 1`

## 13) Family-Aware Confidence Baselines (Guide)
Use template-native confidence scaffolds:

| Family | Baseline guidance |
|---|---|
| empirical_v2 | base around `0.65` (single empirical study, adjusted by design/statistics/ecology/coherence) |
| meta_analysis | base around `0.75` (adjust for heterogeneity/bias/quality mix) |
| systematic_review | base around `0.65` |
| narrative_review | base around `0.40` |
| theoretical | proposed relationships conservative (around `0.35-0.50`), constraints can be higher when logically necessary |
| conceptual_framework | base around `0.65` |
| mixed_methods | strand-dependent with convergence bonus/penalty |
| observational_field | base around `0.50` |
| case_study | base around `0.40` |
| interview_study | base around `0.50` |
| ethnographic | base around `0.55` |
| grounded_theory | base around `0.45` |
| phenomenological | base around `0.55` |
| thought_piece | base around `0.25` (opinion-heavy; not evidence-equivalent) |

## 14) Known Structural Risks (Must Be Checked During Table Work)
From the gap audit, verify these are handled in current runs:
- Table claim payload must match web ingestion contract (`statement`, `ae_confidence`, and structured fields).
- Table claim-type vocabulary must map to epistemic mapper ontology.
- Family-aware extraction routing must cover the 15-family standard.
- Structured `ae.stimulus.v1` payload must be linked where stimulus is central.

Do not mark runs production-grade if these fail.

## 15) Operational Runbook (Current Pipeline)
Immediate intake:
```bash
python3 scripts/run_realtime_table_rule_intake.py --limit 250
```

PDF completion:
```bash
python3 scripts/process_realtime_pdf_completion_queue.py --batch-size 80 --max-workers 6 --integrate-web --update-bn
```

Continuous worker:
```bash
python3 scripts/run_realtime_production_worker.py --poll-seconds 20 --intake-limit 40 --pdf-batch-size 80 --pdf-workers 6 --quality-gate
```

Quality gate:
```bash
python3 scripts/check_table_extraction_quality.py
```

## 16) Definition of “Gold” for Article-Type Tables
A paper is `gold_verified` only when all apply:
1. Provenance anchors are complete and auditable.
2. Article-family required fields are complete or explicit `unknown_with_reason`.
3. Stimulus depth is complete when stimulus is central.
4. Theory/inter-article relations are evidence-backed.
5. Quality gate passes.
6. Manual review queue decisions are resolved for flagged high-impact ambiguities.

## 17) Practical Use with Claude
When asking Claude to improve tables:
1. Require explicit family identification per paper before extraction.
2. Require output labels distinguishing abstract provisional vs PDF confirmed.
3. Require theory_link and inter_article_relation extraction with anchors.
4. Require explicit non-claims and causal-boundary statements.
5. Require stimulus packet depth for stimulus-driven papers.
6. Reject outputs with silent field drops.

This enforces breadth coverage without sacrificing scientific interpretability.

