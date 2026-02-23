# Article Type Question-Field Contract (Sprint D Precision Extension)

Date: 2026-02-18
Owner: Codex

## Problem
Current extraction paths still over-prioritize empirical result fields. That creates systematic quality loss for non-empirical papers and weakens downstream reasoning.

## Goal
Define a stable contract for extraction by article type family so every paper is evaluated against the right scientific questions, with explicit provenance depth.

## Universal Question Set
Use these questions for all papers, but allow type-specific NA values.

- Q1: What is the core claim or contribution?
- Q2: What is being studied (constructs, entities, phenomena)?
- Q3: What evidence basis supports the claim (data type/method)?
- Q4: What are the key findings or conclusions?
- Q5: What are the boundary conditions or limitations?
- Q6: What mechanisms/theoretical explanations are given?
- Q7: How does this connect to prior work or competing findings?
- Q8: What practical or scientific significance is stated?

## Provenance Depth (Required)
Each extracted field must carry one depth label.

- `abstract`: from abstract text only
- `caption`: from figure/table captions
- `table`: from table body/statistical rows
- `section`: from section body (methods/results/discussion)
- `fulltext_multi`: corroborated from multiple full-text sections
- `external`: from citation metadata or external API

## Family-Specific Required Fields

### 1) Empirical Families (`empirical_v2`, `observational_field`, `case_study`, `mixed_methods`)
Required:
- `research_question`
- `design_type`
- `participants`
- `stimuli_or_exposures`
- `measures`
- `findings` (IV, DV, direction, stats if present)
- `limitations`
Optional:
- `mechanisms`
- `moderators`
- `implementation_implications`

### 2) Synthesis Families (`meta_analysis`, `systematic_review`, `narrative_review`)
Required:
- `review_question`
- `inclusion_exclusion_criteria`
- `evidence_base_summary`
- `synthesis_conclusions`
- `evidence_gaps`
Optional:
- `pooled_effects` (meta-analysis only)
- `risk_of_bias_assessment`
- `heterogeneity_sources`

### 3) Theory Families (`theoretical`, `conceptual_framework`, `thought_piece`)
Required:
- `central_proposition`
- `concept_definitions`
- `argument_structure`
- `mechanism_or_causal_logic`
- `testable_hypotheses_or_predictions`
Optional:
- `bridge_warrants`
- `methodological_critiques`

### 4) Qualitative Families (`interview_study`, `ethnographic`, `grounded_theory`, `phenomenological`)
Required:
- `research_focus`
- `sample_context`
- `data_collection_method`
- `coding_or_analysis_approach`
- `themes_or_constructs`
- `supporting_quotes_or_evidence_snippets`
- `transferability_limits`
Optional:
- `derived_hypotheses`
- `mechanism_candidates`

### 5) Unknown (`unknown`)
Required:
- `classification_diagnostics`
- `minimum_safe_summary` (Q1, Q4, Q5 only)
Optional:
- any field with confidence >= threshold

## Quality Gates

- Reject forced mappings when confidence is below threshold.
- Reject self-matches (`iv == dv`) unless explicitly marked as identity/construct validity.
- Do not emit NA fields as null noise for families where the field is structurally irrelevant.
- Require at least one anchored evidence snippet for each major extracted claim.

## D10/D15 Wiring Guidance

- D10 table extraction should populate only fields valid for the paper family.
- D15 merged claims should preserve `provenance_depth` and `article_type_family` per claim.
- Abstract-only claims remain admissible but must be tagged `provenance_depth=abstract` for downstream uncertainty handling.

## Immediate Implementation Delta

- Keep `claim_extractor.py` focused on table/caption claims.
- Add family-aware filtering in batch integration layer before writing `structured_claims.json`.
- Route non-empirical papers to section/argument extraction path rather than forcing IV->DV tables.

