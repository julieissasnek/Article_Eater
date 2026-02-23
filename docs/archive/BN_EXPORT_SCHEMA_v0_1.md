
# Article Eater v20.7.11 — RuleGraph BN Export Schema (v0.1)

This document describes the JSON schema returned by the Admin API
endpoint:

- `POST /api/admin/rulegraph_v2/export_bn`

and explains how to interpret the **nodes**, **edges**, and
**rules** sections when building Bayes nets downstream (e.g. in
BN‑Maker).

## Top-level structure

The export payload is a single JSON object with the following shape:

```json
{{
  "bn_version": "0.2",
  "generator": "article_eater_rulegraph_v2",
  "filters": {{
    "paper_id": "<paper id or null>",
    "text_filter": "<text filter or null>",
    "age_band": "<age band or null>",
    "trait": "<trait name or null>"
  }},
  "meta": {{
    "rules_count": 12,
    "papers": ["Ulrich_1984", "Kaplan_1995"]
  }},
  "nodes": [ /* list of node objects */ ],
  "edges": [ /* list of edge objects */ ],
  "rules": [ /* list of rule payloads */ ]
}}
```

### `bn_version`

A semantic version string for the BN export format. The current
value is `"0.2"`. Increment this when the node / edge or rule
payload structure changes in a way that would break downstream
tools.

### `generator`

A short identifier for the component that produced this export.
Currently: `"article_eater_rulegraph_v2"`.

### `filters`

Echoes the filter state that was applied in the Admin GUI at the
time of export:

- `paper_id`: either a concrete paper identifier (e.g.
  `"Ulrich_1984"`) or `null` if no filter was set.
- `text_filter`: the free-text search string used to prune rules, or
  `null` if blank.
- `age_band`: a single age band (e.g. `"young_adult"`) or `null`.
- `trait`: a single trait name (e.g. `"SPS"`, `"openness"`) or
  `null`.

These fields are **informational only** but are important for
reproducibility and debugging.

### `meta`

- `rules_count`: number of rules that survived all filters.
- `papers`: sorted list of all paper IDs that contributed at least
  one rule to this export.

## Node objects

Each entry in `nodes` has at least these fields:

```json
{{
  "id": "age_band:young_adult",
  "type": "subject_age_band",
  "label": "young_adult"
}}
```

or

```json
{{
  "id": "trait:SPS",
  "type": "subject_trait",
  "label": "SPS"
}}
```

or

```json
{{
  "id": "rule:Ulrich_1984:R1",
  "type": "rule",
  "label": "R1",
  "paper_id": "Ulrich_1984"
}}
```

Supported node `type` values:
- `"subject_age_band"` — represents a **demographic age band**
  extracted from `rule.subject_scope.demographics.age_band`.
  - `id` format: `"age_band:{band}"`.
  - `label`: human-readable age band (same string as in the scope).

- `"subject_trait"` — represents a **psychological trait** or
  measured dimension extracted from
  `rule.subject_scope.traits_measured[].name`.
  - `id` format: `"trait:{name}"`.
  - `label`: trait name.

- `"subject_clinical_population"` — represents the **clinical
  population** of the sample extracted from
  `rule.subject_scope.clinical_status.population`
  (e.g. `healthy`, `clinical`, `mixed`).
  - `id` format: `"clinical_population:{population}"`.
  - `label`: population string.

- `"subject_culture_region"` — represents whether the sample is
  WEIRD / non-WEIRD, etc., from
  `rule.subject_scope.culture.region`.
  - `id` format: `"culture_region:{region}"`.
  - `label`: region string.

- `"subject_self_construal"` — represents the predominant
  self-construal profile from
  `rule.subject_scope.culture.self_construal_profile`.
  - `id` format: `"self_construal:{profile}"`.
  - `label`: profile string.

- `"subject_education_band"` — represents the education band
  (e.g. `"university_undergrads"`) from
  `rule.subject_scope.demographics.education_band`.
  - `id` format: `"education_band:{band}"`.
  - `label`: band string.

- `"subject_moderator"` — represents a **subject-related
  moderation dimension** derived from entries in
  `rule.subject_moderators` (e.g. dimension `traits`,
  attribute `SPS`).
  - `id` format: `"mod:{dimension}:{attribute}"`.
  - `label`: `"dimension:attribute"`.

- `"rule"` — represents a **single extracted rule** from
  RuleGraph v2.
  - `id` format:
    - `"rule:{paper_id}:{rule_id}"` if `rule_id` is non-empty.
    - `"rule:{paper_id}"` if `rule_id` is missing.
  - `label`: the `rule_id` where available, otherwise `"rule"`.
  - `paper_id`: the originating paper identifier.



- `"subject_age_band"` — represents a **demographic age band**
  extracted from `rule.subject_scope.demographics.age_band`.
  - `id` format: `"age_band:{band}"`.
  - `label`: human-readable age band (same string as in the scope).

- `"subject_trait"` — represents a **psychological trait** or
  measured dimension extracted from
  `rule.subject_scope.traits_measured[].name`.
  - `id` format: `"trait:{name}"`.
  - `label`: trait name.

- `"rule"` — represents a **single extracted rule** from
  RuleGraph v2.
  - `id` format:
    - `"rule:{paper_id}:{rule_id}"` if `rule_id` is non-empty.
    - `"rule:{paper_id}"` if `rule_id` is missing.
  - `label`: the `rule_id` where available, otherwise `"rule"`.
  - `paper_id`: the originating paper identifier.

Downstream BN tools will typically:

- Treat `subject_age_band` and `subject_trait` nodes as **input
  variables** describing a subject segment.
- Treat `rule` nodes as **latent policy / effect nodes** that can
  be wired to outcome variables in a second pass.

## Edge objects

Each entry in `edges` has the form:

```json
{{
  "from": "age_band:young_adult",
  "to": "rule:Ulrich_1984:R1",
  "type": "subject_scope"
}}
```

or

```json
{{
  "from": "trait:SPS",
  "to": "rule:Ulrich_1984:R1",
  "type": "subject_scope"
}}
```

Interpretation:

- The `"from"` node is always a `subject_age_band` or `subject_trait`
  node.
- The `"to"` node is always a `rule` node.
- `"type"` currently uses the single value `"subject_scope"` to
  indicate that the edge encodes a **subject scoping relation**:
  the rule is intended to apply to subjects with that age band or
  trait.

For BN construction, it is natural to interpret each such edge as a
**directed dependency**: the subject descriptor is a *parent* of
the rule node in the graphical model.

## Rule payloads

The `rules` list carries the full payloads for all rules that
survived filtering:

```json
{{
  "rule_id": "R1",
  "paper_id": "Ulrich_1984",
  "rule_text": "<natural language rule>",
  "subject_scope": {{ ... }},
  "subject_moderators": [ ... ],
  "subject_scope_summary": "<short text summary>",
  "moderators_summary": "<short text summary>",
  "evidence": {{ ... }},
  "provenance": {{ ... }},
  "graph_version": "2.0",
  "status": "accepted"
}}
```

- `subject_scope` is the **structured** representation (with
  demographics, traits, etc.).
- `subject_moderators` encodes additional conditions (e.g. task
  type, environment).
- `*_summary` fields are concise text summaries used for searching
  and UI display.
- `evidence` / `provenance` / `status` support traceability.

When turning this export into a concrete BN:

1. Use `nodes` / `edges` as the **graph skeleton**.
2. Use `rules` to:
   - decide which **outcome variables** to introduce;
   - derive **conditional probability tables** (CPDs) or at least
     entry templates, with human experts filling in numbers.

## Relationship to BN‑Maker CPD spreadsheets

A downstream CLI (`bn_export_to_csv.py`) can consume this JSON and
emit a tabular representation suitable for BN‑Maker, for example:

- one CSV listing all nodes and their types;
- one CSV listing all edges;
- one or more CSVs listing CPD templates for outcome variables
  keyed by subject descriptors and rule nodes.

The current repo ships such a CLI as a reference implementation;
see `src/tools/bn_export_to_csv.py` for the concrete CSV schema it
produces.
