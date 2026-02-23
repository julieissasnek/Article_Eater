# RuleGraph v2 Specification

## Purpose

RuleGraph v2 is the canonical intermediate representation of CNfA-relevant knowledge extracted from articles. It:

- encodes typed relations between typed entities (environment features, subject attributes, latent constructs, indicators, theories),
- records subject scope (who was studied),
- records subject-specific moderation (how effects differ across subject types),
- remains backward-compatible with existing RuleGraph v1 fields (`factors`, `outcomes`, `moderators`).

RuleGraph v2 is intended to be consumable by:

- the BN builder (candidate nodes and edges),
- the RAG layer (subject- and context-qualified claims),
- the UI (filtering by relation type, subject attributes, etc.).

## Core object

Each rule is a JSON object with:

- identity and versioning (`rule_id`, `graph_version`, `created_at`, `updated_at`),
- relation status and type (`status`, `relation_type`),
- typed factor and outcome nodes (`factor_nodes`, `outcome_nodes`),
- subject annotations (`subject_scope`, `subject_moderators`),
- evidence and provenance,
- auxiliary metrics (`confidence`, `triangulation_score`, `cluster_id`, `tags`, `notes`).

The legacy summary fields `factors` and `outcomes` are retained.

### NodeRef

```json
{
  "id": "string",
  "label": "string",
  "kind": "environment_feature | structural_property | latent_construct | indicator | subject_attribute | theory | activity | context_feature | other",
  "ontology_ref": "string | null"
}
```

### SubjectScope (high-level)

- `demographics`: age statistics, age band, sex/gender distribution, education band, sample size.
- `culture`: countries, region (WEIRD / non_WEIRD / mixed / unknown), self-construal profile.
- `clinical_status`: population (healthy / clinical / mixed / unknown), key inclusions/exclusions.
- `traits_measured`: list of trait measures (name, scale, used_as_moderator).
- `notes`.

### SubjectModerator (high-level)

- `attribute`: which attribute moderates the effect (e.g., SPS, age).
- `dimension`: demographics / culture / traits / clinical / sensory / context / other.
- `levels`: levels compared (e.g., high vs low).
- `pattern`: qualitative pattern (e.g., stronger in high SPS).
- `evidence_ids`: link back to findings.

For a full worked example, see the fixtures in `tests/fixtures/rulegraph_v2_example.json` (to be added in later sprints).
