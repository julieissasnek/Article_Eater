
# Article Eater v20.7.12 — Deeper subject/moderator typing in BN export

## Overview

This sprint enriches the RuleGraph BN export with **deeper subject
typing** and **explicit moderator nodes**, and propagates those changes
into the CSV helper.

Concretely:

- The BN export JSON now includes:
  - subject clinical population, culture region, self-construal profile,
    and education band as dedicated node types.
  - subject moderator nodes derived from heterogeneity patterns
    (dimension + attribute).
- Edges are added from these nodes to rule nodes.
- `bn_version` is bumped from `0.1` to `0.2`.
- `bn_export_to_csv.py` now exposes these descriptors as additional
  columns in `rules.csv`.
- `docs/BN_EXPORT_SCHEMA_v0_1.md` is updated to describe the new
  node types and `bn_version = "0.2"`.

## 1. BN export JSON changes

- **Endpoint:** `POST /api/admin/rulegraph_v2/export_bn`
- **File:** `src/services/admin_service.py`

Enhancements:

- Subject attribute node types now include:
  - `subject_age_band` (unchanged)
  - `subject_trait` (unchanged)
  - `subject_clinical_population` from
    `subject_scope.clinical_status.population` (excluding `unknown`).
  - `subject_culture_region` from `subject_scope.culture.region`
    (excluding `unknown`).
  - `subject_self_construal` from
    `subject_scope.culture.self_construal_profile` (excluding
    `unknown`).
  - `subject_education_band` from
    `subject_scope.demographics.education_band` (excluding
    `unknown`).

- Subject moderator node type:
  - `subject_moderator` derived from `subject_moderators` entries.
  - Node ID: `mod:{dimension}:{attribute}`.
  - Edge type: `"subject_moderator"` pointing from moderator node to
    rule node.

- Each rule node is still created as before, but now receives:
  - `subject_scope` edges from all applicable subject attribute nodes
    (age band, traits, clinical population, culture region,
    self-construal, education band).
  - `subject_moderator` edges from moderator nodes.

- `bn_version` in the export payload is now `"0.2"` to reflect these
  added node types and edges.

## 2. Export schema documentation

- **File:** `docs/BN_EXPORT_SCHEMA_v0_1.md`

Updates:

- Example JSON now shows `"bn_version": "0.2"`.
- Node type section expanded to describe:
  - `subject_clinical_population`
  - `subject_culture_region`
  - `subject_self_construal`
  - `subject_education_band`
  - `subject_moderator`
- Clarifies that subject moderator nodes are keyed by heterogeneity
  **dimension** and **attribute**, while the concrete pattern remains
  in `subject_moderators` within each rule payload.

## 3. CSV helper (`bn_export_to_csv.py`)

- **File:** `src/tools/bn_export_to_csv.py`

Changes:

- `rules.csv` header now includes:

  - `clinical_population`
  - `culture_region`
  - `self_construal_profile`
  - `education_band`
  - `moderator_dimensions`
  - `moderator_attributes`

- `_extract_scope_descriptors()` now returns:

  - `age_bands`
  - `traits`
  - `clinical_population`
  - `culture_region`
  - `self_construal_profile`
  - `education_band`

- New helper `_extract_moderator_descriptors()` aggregates:
  - distinct `dimensions` from `subject_moderators`.
  - distinct `attributes` from `subject_moderators`.

- For each rule row:

  - `clinical_population` is taken from
    `subject_scope.clinical_status.population`.
  - `culture_region` from `subject_scope.culture.region`.
  - `self_construal_profile` from
    `subject_scope.culture.self_construal_profile`.
  - `education_band` from `subject_scope.demographics.education_band`.
  - `moderator_dimensions` is a `;`-separated list of distinct
    moderator `dimension` values.
  - `moderator_attributes` is a `;`-separated list of distinct
    moderator `attribute` values.

These additions are backward compatible for downstream consumers that
only care about the existing columns; the new columns can be ignored or
used to define richer subject-typed CPDs.

## Compatibility

- The export remains **read-only** and only inspects in-memory
  RuleGraph v2 events; no mutation of graph storage.
- Existing fields (`nodes`, `edges`, `rules`) are preserved; we only
  add more node types and edges and bump `bn_version`.
- The CSV helper still produces `nodes.csv` and `edges.csv` unchanged;
  `rules.csv` is extended with extra columns.
