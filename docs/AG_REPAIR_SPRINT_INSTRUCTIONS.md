# AG REPAIR SPRINT — VARIABLE ONTOLOGY + DOCUMENT GOVERNANCE
## February 22, 2026
## Read PROJECT_STATE.md first. Claim tasks before starting. Update after completing.

---

# CONTEXT

Four audits revealed that the 184 template JSONs use 931 unique root
variable names, of which only 33 appear in more than one template. This
makes cross-template composition — the CMR's core value — mechanically
impossible. Your job is to build the canonical variable ontology that
makes it possible.

You're also doing the document lifecycle pass (479 files → ~40 current).

CC is working in parallel on JSON schema normalization (E-01 → M-01).
Your variable ontology (E-03a) feeds into CC's variable migration (M-03b),
which runs AFTER CC's schema migration (M-01). So you have time — but
E-03a should be done before CC finishes M-01.

---

# TASK 1: E-03a — CANONICAL VARIABLE ONTOLOGY

## Input

`docs/SYSTEM_AUDIT_VARIABLE_INVENTORY_Feb22_2026.csv`
- 1,533 entries, 931 unique roots
- Columns: variable, category, source_count, sample_sources
- Category distribution: UNCLASSIFIED (904), ENV_ARCH (261), PSYCH_COG
  (184), NEURAL_PHYS (112), BEHAV_OUTCOME (51), POP_MOD (21)

## What To Build

`schemas/canonical_variables.json` — a JSON file with this structure:

```json
{
  "version": "1.0",
  "date": "2026-02-22",
  "domains": {
    "ENVIRONMENTAL_INPUT": {
      "description": "Physical properties of the architectural environment that serve as stimulus inputs to neural/cognitive mechanisms",
      "variables": {
        "luminance_level": {
          "description": "Ambient light intensity",
          "unit": "lux or cd/m2",
          "aliases": ["luminance", "ambient_luminance", "light_level", "illuminance"],
          "typical_range": [0, 100000],
          "used_by_templates": ["L1", "T69", "..."]
        },
        "spatial_enclosure_ratio": {
          "description": "Ratio of ceiling height to floor area, indexing perceived spaciousness",
          "unit": "dimensionless",
          "aliases": ["R_h", "R_h_goldilocks", "ceiling_height_ratio", "enclosure_ratio"],
          "typical_range": [0.5, 5.0],
          "used_by_templates": ["VF1", "VF2", "VF3", "T22", "..."]
        }
      }
    },
    "NEURAL_MECHANISM": {
      "description": "Neural processes that mediate between environmental input and psychological/behavioral outcomes",
      "variables": {
        "prediction_error_magnitude": {
          "description": "Unsigned PE signal magnitude in predictive processing framework",
          "unit": "arbitrary (model-dependent)",
          "aliases": ["PE_magnitude", "prediction_error", "surprise_signal", "PE_unsigned"],
          "used_by_templates": ["T1", "T2", "ED_PE_ENCODING_PRINCIPLE_001", "..."]
        }
      }
    },
    "PSYCHOLOGICAL_STATE": { "..." },
    "BEHAVIORAL_OUTCOME": { "..." },
    "POPULATION_MODIFIER": { "..." },
    "ARCHITECTURAL_MODIFIER": { "..." }
  },
  "alias_map": {
    "R_h": "spatial_enclosure_ratio",
    "R_h_goldilocks": "spatial_enclosure_ratio",
    "ceiling_height_ratio": "spatial_enclosure_ratio",
    "luminance": "luminance_level",
    "PE_magnitude": "prediction_error_magnitude"
  }
}
```

## Design Principles

1. **Canonical names are human-readable snake_case.** Not abbreviations,
   not camelCase. `prediction_error_magnitude` not `PE_mag`.

2. **Every current variable name maps to exactly one canonical name.**
   The `alias_map` at the bottom is the complete lookup: given any variable
   name found in any template, you can find its canonical equivalent.

3. **Domains organize by role in the causal chain**, not by academic
   discipline. The CMR mechanism chain goes:
   ENVIRONMENTAL_INPUT → NEURAL_MECHANISM → PSYCHOLOGICAL_STATE → BEHAVIORAL_OUTCOME
   with POPULATION_MODIFIER and ARCHITECTURAL_MODIFIER as moderators.

4. **Not every current variable gets its own canonical entry.** Many of
   the 931 roots are sub-parameters (e.g., `R_h_goldilocks.balanced`,
   `R_h_goldilocks.confining`). These are parameter LEVELS, not separate
   variables. The canonical variable is `spatial_enclosure_ratio`; the
   levels are values within its range.

5. **Target: 80-120 canonical variables.** This is an order of magnitude
   reduction from 931. Most of the reduction comes from:
   - Merging synonyms (different names for same construct)
   - Absorbing parameter levels into their parent variable
   - Absorbing sub-field notation (X.source, X.warrant, X.CI_95) into
     metadata, not separate variables

6. **New variables can be added by future panels**, but they must be
   registered in this file. No silent invention.

## Process

1. Start with the 33 variables that appear in 2+ templates (from the CSV,
   source_count > 1). These are the ones where cross-template composition
   already attempts to work. Get these right first.

2. Then work through the UNCLASSIFIED category (904 entries) by
   template source. Group by semantic similarity, assign canonical names.

3. For variables that are genuinely template-specific (e.g.,
   `thermal_effusivity_categories` only appears in materials templates),
   still register them — but note they're domain-specific.

4. Build the alias_map as you go. Every variable name in the Codex CSV
   should have an entry in alias_map pointing to its canonical name.

## Acceptance

- `schemas/canonical_variables.json` exists
- alias_map covers all 931 root variable names from the inventory
- 80-120 canonical variables defined across 6 domains
- Each canonical variable has: description, aliases, used_by_templates
- HUMAN approves the ontology (canonical names are theoretical decisions)

---

# TASK 2: M-03a — VARIABLE MIGRATION SCRIPT

## Depends on: E-03a complete

## What To Build

`scripts/migrate_variables.py`:
1. Reads `schemas/canonical_variables.json`
2. For each template JSON in `data/templates/`:
   - Walks `mechanism_chain` steps: renames `from` and `to` fields using
     alias_map
   - Walks `calibrated_parameters` keys: renames using alias_map
   - Walks `population_modifiers` keys: renames using alias_map
   - Walks `architectural_modifiers` keys: renames using alias_map
   - Walks `cross_template_interactions` references: renames variables
3. Logs every rename: template_id, field_path, old_name → new_name
4. Writes migrated JSON back

## IMPORTANT: This script should NOT be run until CC completes M-01
(schema migration). Run order is: E-01 → M-01 (field names normalized) →
M-03b (variable names normalized). Build the script now; execute it later.

## Acceptance

- Script exists and is tested against a few sample templates
- Dry-run mode available (reports what would change without writing)
- Log output shows rename map

---

# TASK 3: E-03b — VARIABLE LINT SCRIPT

## Depends on: E-03a complete

## What To Build

`scripts/lint_variables.py`:
1. Reads `schemas/canonical_variables.json`
2. For each template JSON:
   - Extracts all variable names from mechanism_chain, parameters, modifiers
   - Checks each against alias_map
   - Reports any variable NOT in the registry
3. Output: PASS (all variables registered) or FAIL (with unregistered list)

This becomes a CI/pre-commit check for new templates.

## Acceptance

- Script runs against current corpus
- After M-03b migration, all templates should PASS (0 unregistered variables)

---

# TASK 4: G-01 — DOCUMENT LIFECYCLE PASS

## Can run in parallel with everything above.

## Input

`docs/SYSTEM_AUDIT_DOC_INVENTORY_Feb22_2026.csv`
- 480 files
- Columns: filename, line_count, date_guess, status_heuristic, purpose_headline

## Action

1. Create `docs/DOCUMENT_LIFECYCLE_REPORT.md` classifying every file:

   **CURRENT** — actively referenced by PROJECT_STATE.md, Sprint Brief,
   or panel outputs. Should stay in docs/.

   **SUPERSEDED** — replaced by a newer version. Add header banner:
   `# ⚠️ SUPERSEDED — See [newer file] for current version`

   **ARCHIVE** — historical, no longer referenced. Move to `docs/archive/`

2. Use these heuristics:
   - If a file is listed in PROJECT_STATE.md Section 6: CURRENT
   - If a file has a newer version (e.g., Transfer V1 < V2 < Session8): older = SUPERSEDED
   - If a file is from Feb 14-15 and has a Feb 16+ replacement: SUPERSEDED
   - If a file is a panel config (02-15_20, 44_Panel_SOC, etc.) and the
     panel output exists: ARCHIVE (the config was consumed, output is current)
   - If a file is a one-off prompt or session summary: ARCHIVE

3. DO NOT delete any files. Move ARCHIVE files to `docs/archive/`.
   Add SUPERSEDED banners to superseded files.

## Acceptance

- DOCUMENT_LIFECYCLE_REPORT.md exists with classification for all 480 files
- docs/ contains only CURRENT + SUPERSEDED files (~50-80)
- docs/archive/ contains the rest
- No files deleted

---

# CLAIMING TASKS

Before starting any task:
1. Open docs/PROJECT_STATE.md
2. Find the task in the task board
3. Write "OPUS/AG" in the Claimed By field
4. Save the file
5. Begin work

After completing:
1. Mark COMPLETED in PROJECT_STATE.md
2. Write output file paths
3. Append to changelog
4. Save

---

*AG_REPAIR_SPRINT_INSTRUCTIONS.md — CMR Project*
*Variable Ontology + Document Governance, February 22, 2026*
