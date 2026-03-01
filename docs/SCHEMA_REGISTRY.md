# SCHEMA_REGISTRY.md — Data Contracts and Schema Index

*Last updated: February 26, 2026*

This document indexes all data contracts, schemas, and validation entry points in the ATLAS system. If you change a schema, update this file.

---

## Core Contracts

### ClaimV2 — `src/epistemic/contracts/claim_v2.py`

The canonical claim representation. Every belief in the web of belief ultimately derives from a ClaimV2 instance.

Key enums:
- `ProvenanceTier`: ABSTRACT_PROVISIONAL | PDF_CONFIRMED
- `CausalLevel`: ASSOCIATION | INTERVENTION | COUNTERFACTUAL
- `EvidenceBasis`: CITED_EVIDENCE | EXPERT_OPINION | CONSENSUS
- `ExtractionDifficulty`: EASY | MODERATE | HARD

### EdgeV2 — `src/epistemic/contracts/edge_v2.py`

The canonical edge representation for typed, weighted, justified links between beliefs.

Required fields: edge_id, edge_type, source_node_id, target_node_id, weight, paper_id
Optional fields: evidence_basis (EvidenceBasisEdge), justification, provenance_tier, needs_verification

### Pydantic Schemas — `src/contracts/schemas.py`

Statistical and demographic models used in extraction:
- `Stats`: p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper
- `SevenPanelItem`: finding_text, statistics, quote, page_span, raw_abstract
- `SevenPanelArtifact`: items (list of SevenPanelItem), provider, model, cost_usd
- `SubjectDemographics`: age_mean, age_sd, age_range, sex_gender_distribution, sample_size
- `SubjectCulture`: countries, region, self_construal_profile
- `SubjectClinicalStatus`: population, key_inclusions, key_exclusions
- `SubjectTrait`: name, scale, used_as_moderator

---

## Web of Belief Contracts

### Enums — `src/services/web_of_belief_components/enums.py`

- `EpistemicLevel`: THEORETICAL | INTERMEDIATE | EMPIRICAL | OBSERVATIONAL
- `BeliefStatus`: STUB | TENTATIVE | ESTABLISHED | ENTRENCHED | ANOMALOUS
- `InferenceType`: INDUCTIVE | DEDUCTIVE | ABDUCTIVE | MIXED | UNKNOWN
- `BeliefKind`: MECHANISTIC | EVIDENTIAL | THEORETICAL | METHODOLOGICAL | BRIDGE
- `CausalDirection`: (see source for full enum)

### Graph Models — `src/services/web_of_belief_components/graph_models.py`

Typed graph representation of the epistemic warrant graph. See source for node/edge classes.

### Scope Models — `src/services/web_of_belief_components/scope_models.py`

Scope/boundary modeling for claim applicability (population, context, dose, method).

---

## Bridge Warrant Contract

### Bridge Type Ceilings — `src/services/bridge_warrants.py`

Source of truth for warrant type ceiling values:

```python
DEFAULT_BRIDGE_CONFIDENCE = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_COVARIANCE": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "THEORETICAL_DEFAULT": 0.40,
    "ANALOGICAL": 0.35,
}
```

Bridge lifecycle states: HYPOTHESIZED → SUPPORTED | CONTESTED | FAILED | REVISED

### Warrant Scaling — `src/epistemic/warrant_scaling.py`

Base values (panel-approved):
- BASE_COHERENCE_WARRANT = 0.55 (Decision D1.5)
- BASE_ARGUMENTATIVE_WARRANT = 0.70 (Decision D1.6)
- BASE_VIGILANCE_WARRANT = 0.50 (Decision D-PANEL.2)

Combination: noisy-OR — P(total) = 1 - Π(1 - warrant_i)

---

## Extraction Contracts

### Article Type Classification

Managed by `src/extraction/paper_triage.py`. Types: EMPIRICAL, META_ANALYSIS, REVIEW, THEORETICAL, CASE_STUDY, OTHER.

### ae.claim.v1 Format

The extraction pipeline produces claims in ae.claim.v1 format (see `src/extraction/claim_extractor.py`). Claims include: finding text, statistics, theory links, domain tags (A1-A10), qualifiers.

---

## Template Contract

Templates live in `data/templates/` as JSON files. Each template must have:
- `template_id` (unique identifier)
- `bridge_warrant` with `type` and `confidence` (subject to ceiling enforcement)
- Mechanism chain entries (each with its own warrant type and confidence)
- Toulmin structure (claim, data, warrant, backing, qualifier, rebuttal)

Validation: `scripts/validate_all_templates.py`, `scripts/validate_toulmin.py`

---

## Validation Entry Points

| Script | What It Validates |
|--------|-------------------|
| `scripts/validate_all_templates.py` | All template JSON against schema |
| `scripts/validate_templates.py` | Individual template validation |
| `scripts/validate_toulmin.py` | Toulmin argument structure completeness |
| `scripts/lint_bridge_ceilings.py` | Bridge warrant ≤ ceiling per type |
| `scripts/lint_ceilings.py` | General ceiling enforcement |
| `scripts/audit_template_compliance.py` | Template compliance with conventions |
| `src/config/validate.py` | Configuration validation |
| `src/services/validation.py` | Runtime validation service |

---

## Change Protocol

When modifying any contract or schema:

1. Update the source file
2. Update this document
3. Run `scripts/validate_all_templates.py` to check for breakage
4. Run `scripts/lint_bridge_ceilings.py` if ceiling values changed
5. Log the decision in `docs/DECISIONS_LOG.md` per CLAUDE.md protocol
6. Run affected tests: `python -m pytest tests/ -k "relevant_test_pattern"`
