# Article Eater v20.7.13 — BN Outcome Template Suggestions (v0.1)

This document describes the helper script:

- `src/tools/bn_suggest_outcome_templates.py`

which takes a RuleGraph BN export JSON (from
`POST /api/admin/rulegraph_v2/export_bn`) and emits a CSV listing
**candidate outcome variables** and their recommended parent sets.

The goal is to provide a light-weight bridge from Article Eater's
subject-typed rules to BN-Maker, without making any probabilistic
commitments.

## Input

- A BN export JSON file produced by the Admin GUI:

  1. Go to the **RuleGraph v2 / subject panel** tab.
  2. Set any filters you want (paper, text, age band, trait).
  3. Click **"Export BN (JSON)"**.
  4. Save the file (e.g.
     `article_eater_bn_export_2025-11-25T10-30-00.json`).

## Usage

From the repo root:

```bash
python -m src.tools.bn_suggest_outcome_templates \
    --input article_eater_bn_export_2025-11-25T10-30-00.json \
    --out bn_outcome_templates.csv
```

This will create `bn_outcome_templates.csv` in the current
directory.

## Output CSV

Columns:

- `outcome_node_id` — proposed BN node id, e.g.
  `outcome:Ulrich_1984:R1:preference`.
- `outcome_family` — coarse outcome category inferred heuristically
  from rule text and summaries (e.g. `preference`,
  `stress_arousal`, `restoration`, `performance`, `memory`,
  `attention`, `affect_valence`, `unspecified`).
- `outcome_label` — human-readable label for the outcome. By
  default this is the same as `outcome_family` unless the family is
  `unspecified`, in which case a generic label is used.
- `paper_id` — originating paper.
- `rule_id` — originating rule id (if present).
- `rule_node_id` — id of the rule node in the BN skeleton
  (e.g. `rule:Ulrich_1984:R1`).
- `rule_text` — single-line version of the rule's natural language
  description.
- `subject_parents_ids` — `;`-separated list of subject and trait
  node ids wired to the rule (age bands, traits, clinical
  population, culture region, self-construal, education band).
- `subject_parent_types` — `;`-separated list of node types
  present among subject parents (e.g. `subject_age_band`,
  `subject_trait`, `subject_culture_region`, etc.).
- `moderator_parent_ids` — `;`-separated list of moderator node
  ids (e.g. `mod:traits:SPS`).
- `recommended_parent_nodes` — `;`-separated list of node ids
  recommended as parents for this outcome: all subject parents,
  all moderator parents, plus the rule node itself.
- `notes` — free-text field for human modellers to annotate
  decisions.

## How to use this with BN-Maker

1. Generate both the **BN skeleton JSON** and the **outcome
   templates CSV** for the same filtered slice of rules.
2. Use:
   - `nodes.csv` / `edges.csv` from `bn_export_to_csv.py` for the
     structural graph.
   - `rules.csv` from `bn_export_to_csv.py` for detailed rule
     metadata.
   - `bn_outcome_templates.csv` from
     `bn_suggest_outcome_templates.py` to define:
       - which outcome nodes to include;
       - which subject and moderator nodes should be parents.

3. In BN-Maker:
   - Create BN variables for each chosen outcome_node_id.
   - Wire the parents exactly as listed in
     `recommended_parent_nodes`.
   - Define CPDs with human-chosen levels and probability values.

The heuristics in `bn_suggest_outcome_templates.py` are
intentionally conservative: they detect broad families such as
`preference` or `stress_arousal` from keywords. You can always
override or refine these families when curating the outcome
catalogue.
