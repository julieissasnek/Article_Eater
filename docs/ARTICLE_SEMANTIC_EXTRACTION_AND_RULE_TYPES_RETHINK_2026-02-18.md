# Article Semantic Extraction and Rule Types Rethink

Date: 2026-02-18  
Owner: Codex

## Reframed Target

Primary objective is not syntactic table parsing.  
Primary objective is article-type-appropriate semantic extraction that can generate valid Web/BN rules.

## Required Semantic Record (Per Paper)

Each paper should emit an article-semantic record containing, where applicable:
- research question / hypothesis
- design + methods + measures
- population/sample and scope
- interventions/exposures and outcomes
- result claims (direction, uncertainty, effect evidence)
- mechanism/theory statements
- limitations and boundary conditions
- links to prior work (agreement/contradiction/extension)

## Rule Family Set (Current + Needed)

Current commonly used labels:
- causal
- associational
- moderated
- mechanistic
- descriptive
- null
- methodology
- sample
- theory_link
- inter_article_relation

Candidate missing or under-specified families:
- mediated_effect
- boundary_condition
- dose_response
- population_scope
- methodological_constraint
- measurement_validity
- replication_or_failure_to_replicate
- contradiction_with_prior
- transportability_constraint

## Why This Matters for Web/BN

- Web needs semantically typed belief/constraint objects with correct edge semantics.
- BN needs effect-oriented and scope-aware claims, not only flat relation claims.
- If rule families are missing, extraction appears "complete" but the graph becomes structurally biased.

## Immediate Protocol

1. Run extraction benchmark across model tiers.
2. Audit semantic outputs for rule-type coverage:
   - `scripts/audit_rule_type_coverage.py`
3. Add missing-rule candidates to a managed review queue.
4. Expand claim_type/rule_type mapping in integration only after review.

## Acceptance Criteria

- Non-trivial coverage across article families (not only empirical effect claims).
- Rule-type audit reports low "missing claim_type" and explicit candidate missing families.
- Web/BN integration receives typed, scoped, provenance-aware claims.
