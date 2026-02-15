# Theory-Level / Tier Inventory Across 5 Repos

Date: 2026-02-15
Scope: `Article_Eater_PostQuinean_v1`, `BN_graphical`, `Article_Finder_v3_2_3`, `Tagging_Contractor`, `Outcome_Contractor`

## Executive summary

- Only `Article_Eater_PostQuinean_v1` currently has a formal `TheoryLevel` enum in production code.
- No repo currently contains an implemented `ReductionClaim` model or `reduce_tier2_theory()` function in code.
- Tier terminology exists cross-repo, but mostly as:
  - extraction-layer tiers (`tier1`, `tier2`, `tier3`) in BN docs/contracts,
  - institution-quality tiers (`tier_1`, `tier_2`, `tier_3`) in AE vocab,
  - theory keyword taxonomies (ART/SRT/biophilia) in AF/Outcome/Tagging.
- There is no cross-repo canonical theory-tier contract yet.

## Repo-by-repo inventory

| Repo | Formal theory-level enum | Tier constants | Reduction claim model | Notes |
|---|---|---|---|---|
| `Article_Eater_PostQuinean_v1` | Yes (`TheoryLevel`) | Yes (`tier_1/2/3` institution tiers) | No | Has closest placeholders for future reduction model |
| `BN_graphical` | No | Yes (`tier1/2/3` extraction schema in docs) | No | Theory framework strings (ART/SRT/etc.) but no theory-tier enum |
| `Article_Finder_v3_2_3` | No | No formal theory-tier enum | No | Theory taxonomy IDs/keywords only |
| `Tagging_Contractor` | No | No | No | Tag registry includes biophilia-related tags only |
| `Outcome_Contractor` | No | No formal theory-tier enum | No | Theory keywords and IDs in extraction/taxonomy utilities |

## Evidence by repo

### 1) Article_Eater_PostQuinean_v1

- Canonical local enum:
  - `src/models/theory_models.py:20` defines `class TheoryLevel(Enum)`.
  - Includes `framework_theory`, `domain_theory`, `methodological`, `mechanism` plus legacy compatibility values (`meta_principle`, `theory`, `principle`) at `src/models/theory_models.py:43` through `src/models/theory_models.py:57`.
- DB layer aligned to local enum + legacy values:
  - `db/sql/017_theories.sql:47` through `db/sql/017_theories.sql:50`.
- Adjacent tier constructs:
  - `contracts/vocab/institution_tiers.json:47`, `contracts/vocab/institution_tiers.json:61`, `contracts/vocab/institution_tiers.json:79` (`tier_1/2/3`, institutional quality, not theory level).
  - `src/services/abstraction_levels.py:62` (`AbstractionLevel` with `DOMAIN`, `GROUNDED`, etc.).
- Closest existing placeholders for reduction-claim architecture:
  - Theory parent links: `db/sql/017_theories.sql:58`, `src/models/theory_models.py:431`.
  - Belief derivation path: `src/services/web_of_belief.py:672`.
  - Constraint types: `src/services/web_of_belief.py:122`, `src/services/web_of_belief.py:123`.
  - Commented link stub: `src/epistemic/edge_types.py:321`.

### 2) BN_graphical

- No `TheoryLevel` enum found in runtime code.
- Tiered extraction schema exists in docs:
  - `docs/research/CONTRACT_SPECIFICATIONS.md:33` (`tier1`),
  - `docs/research/CONTRACT_SPECIFICATIONS.md:66` (`tier2`),
  - `docs/research/CONTRACT_SPECIFICATIONS.md:113` (`tier3`).
- Theory framework strings exist without tier model:
  - `src/ai_extraction/mechanism_classifier.py:102` through `src/ai_extraction/mechanism_classifier.py:103` (ART/SRT context),
  - `src/schemas/mechanism_specification.py:61` through `src/schemas/mechanism_specification.py:62`.

### 3) Article_Finder_v3_2_3

- No `TheoryLevel`/tier enum found in code.
- Theory taxonomy IDs/keywords exist:
  - `config/taxonomy.yaml:1757` (`theo.preference.biophilia`),
  - `search/ae_feedback.py:342` through `search/ae_feedback.py:344` (ART/SRT/biophilia mappings),
  - `config/environment_lookup.json:61` (`biophilia.plant_count`).

### 4) Tagging_Contractor

- No formal theory-level/tier enum.
- Theory-adjacent content appears as tag registry entries:
  - `core/trs-core/v0.2.8/registry/cnfa_tag_registry_canonical_v0.2.8.yaml:10574` (`biophilia.plant_count`),
  - `core/trs-core/v0.2.8/contracts/preference_testing_contract_v0.2.8.json:145`.

### 5) Outcome_Contractor

- No formal theory-level/tier enum.
- Theory keywords used in extraction/routing:
  - `article_finder/seven_panel_extractor.py:433` through `article_finder/seven_panel_extractor.py:442` (ART/SRT/biophilia keyword dictionaries),
  - `core/argument_taxonomy.py:400` (theory warrant-type examples).

## ReductionClaim status (cross-repo)

- Search across all five repos found no implemented `ReductionClaim` class or `reduce_tier2_theory()` function in source code.
- Mentions are currently planning/docs only (e.g., AE docs task plans).

## Contract implications

For the future cross-repo `TheoryLevel` contract:

1. Use AE `TheoryLevel` as starting source of truth.
2. Keep extraction tier (`tier1/2/3`) separate from theory-level (`framework_theory`, `domain_theory`, etc.) to avoid semantic conflation.
3. Add explicit migration aliases for legacy AE values (`theory`, `principle`, `meta_principle`).
4. Add explicit non-goal statement: article/table extraction tiers are not equivalent to theory-level ontology.
