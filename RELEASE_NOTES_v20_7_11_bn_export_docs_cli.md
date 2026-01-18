
# Article Eater v20.7.11 — BN export schema doc + CSV CLI

## Overview

This sprint makes the RuleGraph BN export **inspectable and portable**
for BN-Maker:

1. Adds a docs page explaining the BN export JSON schema and how to
   interpret nodes, edges, and rules.
2. Adds a small CLI (`bn_export_to_csv.py`) that converts a BN export
   JSON into three CSV tables (`nodes.csv`, `edges.csv`, `rules.csv`)
   suitable as inputs to BN-Maker or other BN tooling.

## 1. Documentation: BN export schema

- **File:** `docs/BN_EXPORT_SCHEMA_v0_1.md`

  Describes:

  - The top-level JSON structure returned by
    `POST /api/admin/rulegraph_v2/export_bn`.
  - Meaning of `bn_version`, `generator`, `filters`, and `meta`.
  - Node types:
      - `subject_age_band` (id: `age_band:<band>`)
      - `subject_trait` (id: `trait:<name>`)
      - `rule` (id: `rule:<paper_id>:<rule_id>` or `rule:<paper_id>`)
  - Edge semantics:
      - `from` is always a subject node (age band or trait).
      - `to` is always a rule node.
      - `type == "subject_scope"` encodes that the rule is scoped to
        that subject descriptor.
  - Rule payloads and how they can be used to define outcome variables
    and CPDs in a second pass.

  The doc also explains how this export sits upstream of BN-Maker:
  it defines a **graph skeleton and rule catalogue**, not yet a
  full BN with CPDs.

## 2. CLI: JSON → CSV for BN-Maker

- **File:** `src/tools/bn_export_to_csv.py`
- **Entry point:** can be run as

  ```bash
  python -m src.tools.bn_export_to_csv \
      --input article_eater_bn_export_2025-11-25T10-30-00.json \
      --out-dir bn_csv/
  ```

  This will create:

  - `bn_csv/nodes.csv`
  - `bn_csv/edges.csv`
  - `bn_csv/rules.csv`

### 2.1 nodes.csv

- Columns:

  - `id` — node id from the export (e.g. `age_band:young_adult`,
    `trait:SPS`, `rule:Ulrich_1984:R1`).
  - `type` — node type (`subject_age_band`, `subject_trait`, `rule`).
  - `label` — human-readable label.
  - `paper_id` — populated for `rule` nodes, empty otherwise.

- Derived directly from `export["nodes"]`.

### 2.2 edges.csv

- Columns:

  - `from` — id of the parent node.
  - `to` — id of the child node (always a rule node in the current
    export).
  - `type` — edge type (currently `subject_scope`).

- Derived directly from `export["edges"]`.

### 2.3 rules.csv

- Columns:

  - `rule_id`
  - `paper_id`
  - `age_bands` — `;`-separated list of age bands extracted from
    `subject_scope.demographics.age_band`.
  - `traits` — `;`-separated list of trait names extracted from
    `subject_scope.traits_measured[].name`.
  - `rule_text` — single-line version of the rule text (newlines
    collapsed to spaces).
  - `subject_scope_json` — JSON-encoded `subject_scope`.
  - `subject_moderators_json` — JSON-encoded `subject_moderators`.
  - `evidence_json` — JSON-encoded `evidence`.
  - `provenance_json` — JSON-encoded `provenance`.
  - `status` — rule status.

- Rules are taken from `export["rules"]`. A helper function
  `_extract_scope_descriptors()` pulls out the age band and trait
  names from the structured `subject_scope`.

### 2.4 Intended BN-Maker usage

BN-Maker (or any BN-building workflow) can:

- Use `nodes.csv` and `edges.csv` to reconstitute the **graph
  skeleton**.
- Use `rules.csv` to:
    - label variables and parent sets by subject descriptors;
    - define one or more outcome nodes whose CPDs are conditioned on
      (age band, traits, rule nodes);
    - keep a direct pointer back to the original paper and rule
      text (`paper_id`, `rule_text`) for justification.

The CLI intentionally does **not** guess any probabilities; it is a
bridge from Article Eater's subject-aware rules into the structured
tables that BN-Maker expects.

## Compatibility

- Changes are additive; existing APIs and GUIs are unchanged.
- The CLI is a standalone utility. It does not depend on the web app
  context and can be run wherever Python 3 is available.
