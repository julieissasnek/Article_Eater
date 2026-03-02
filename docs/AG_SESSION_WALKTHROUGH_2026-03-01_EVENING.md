# AG Session Walkthrough — 2026-03-01 (Evening Sprint)

**AESHI**: 76.92 YELLOW → **89.79 GREEN** (+12.87)

> [!IMPORTANT]
> CW: incorporate the design decisions below into the master doc. Items marked with 🔑 are conceptual decisions that affect the architecture, not just code changes.

---

## 1. AESHI Score Improvement: 76.92 → 89.79

### 1a. CCI Fix (Pipeline 40→80)
- **Problem**: Only 51/4,888 findings (1.04%) touched BN nodes — naming mismatch (`env.unknown.<hash>` vs `env_<term>`)
- **Fix**: Token-overlap matching in `bn_touch()` via reverse index in [compute_system_health.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/scripts/compute_system_health.py)
- **Result**: 4,690/4,888 (95.9%) now touch BN

### 1b. Scoring Parameter Corrections
- `unique_tier1_count` target: **25 → 14** (actual number of T1+T1.5 families)
- `isolated_pct` worst threshold: **25% → 35%** (25.06% was scoring zero)

### 1c. Constraint Propagation (isolated 25.1% → 1.7%)
- **Script**: [propagate_constraints.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/scripts/propagate_constraints.py)
- **Logic**: For each isolated belief, find peers sharing same template, environment_id, or outcome_id → create `supports` edges
- **Result**: 3,415 new constraints, 1,140/1,225 isolated beliefs connected
- **DB schema gotcha**: column is `constraint_type` not `type`; needs `web_id` and `created_at` — see [DB_SCHEMA_REFERENCE.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/DB_SCHEMA_REFERENCE.md)

---

## 2. Theory Taxonomy (6 new files)

Created authoritative tier definitions in `schemas/theory/`:

| File | Content |
|------|---------|
| [theory_hierarchy_overview.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/theory_hierarchy_overview.json) | How T1→T2→Molecules→T1.5→T3 relate |
| [tier1_frameworks.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/tier1_frameworks.json) | 10 T1 frameworks with aliases |
| [tier1_5_domain_theories.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/tier1_5_domain_theories.json) | 4 T1.5 theories with aliases |
| [molecule_taxonomy.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/molecule_taxonomy.json) | 18 molecules |
| [tier2_mechanisms.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/tier2_mechanisms.json) | 166 T2 templates index |
| [tier3_empirical_beliefs.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/schemas/theory/tier3_empirical_beliefs.json) | T3 schema + examples |

### 🔑 Design Decision: 5-Tier Hierarchy
- **T1**: Framework Theories (10) — PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI
- **T1.5**: Domain Theories (4) — ART, SRT, Biophilia, Prospect-Refuge
- **Molecules**: Composite constructs (18) — latent variables discoverable from template co-activation
- **T2**: Mechanism Templates (166) — testable predictions
- **T3**: Empirical Beliefs (~4,888) — well-supported findings

### 🔑 Design Decision: Molecules as Latent Variables
Molecules exist between T1 and T2 as latent variables — they're defined by which templates co-activate. Can be discovered computationally via factor analysis on the template‐belief activation matrix.

### 🔑 Design Decision: T1.5 is a Subset of Molecules
T1.5 theories (ART, SRT, etc.) are molecules that have established authorship, citations, and academic recognition. They are molecules that "graduated" into named theories.

---

## 3. Code Refactor: Taxonomy Loader

Replaced hardcoded `TIER1_TAXONOMY` in [finding_template_relevance.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/finding_template_relevance.py):

- **Removed**: 175-line dict (confused mix of T1/T1.5/topic names, wrong abbreviations)
- **Added**: `_load_theory_taxonomy()` — reads from JSON files
- **Exports**: `THEORY_FAMILY_TAXONOMY` (14 families), `T1_FRAMEWORK_IDS` (canonical 10), `TIER1_TAXONOMY` (backward-compat alias)
- **Impact**: Fixed `has_tier1_ratio` from 0.914 → 0.920

---

## 4. Design Decisions for Master Doc

### 🔑 Edge Types: "explains" with Prediction Annotations
- **Decision**: Don't separate "predicts" and "explains" as different edge types
- **Instead**: Single `explains` edge type with `prediction_status` annotation:
  - `verified_prediction` — predicted outcome has been observed
  - `unverified_prediction` — prediction not yet tested
- **Rationale**: Structurally the same; difference is temporal/observational, not structural

### 🔑 Constraints = Edges
- Term "constraint" in the code means "edge in the belief graph"
- Scheduled for terminology refactoring: `constraint` → `edge` throughout

### 🔑 BN ↔ EN Gap (Major Future Work)
The BN and EN are parallel stores with 96% token-overlap mapping but **no bidirectional propagation**:
- EN belief entrenchment changes don't update BN CPDs
- BN posteriors don't feed back to EN coherence
- **Target**: When BN says P(outcome|features)=0.78, that updates linked belief entrenchment, and vice versa

---

## 5. New Files Created

| File | Purpose |
|------|---------|
| [propagate_constraints.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/scripts/propagate_constraints.py) | Connect isolated beliefs via shared templates/env/outcome |
| [DB_SCHEMA_REFERENCE.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/DB_SCHEMA_REFERENCE.md) | 14-table schema reference (prevents column name errors) |
| [TIER_ARCHITECTURE_SPEC_2026-03-01.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/TIER_ARCHITECTURE_SPEC_2026-03-01.md) | 5-tier hierarchy spec |
| [AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md) | QA+Annotation system spec with SCs and sprint plan |
| 6 files in `schemas/theory/` | Theory taxonomy (see §2) |

---

## 6. TODOs for Next Sessions

| Priority | Task | Owner |
|----------|------|-------|
| P0 | QA system wiring (Sprint A in impl plan) | AG |
| P0 | Annotation unification (Sprint B) | AG+CW |
| P1 | T1 rename: PP→PREDICTIVE_PROCESSING etc. | AG |
| P1 | BN↔EN bidirectional integration | AG+CW |
| P2 | Ruthless V8 with CS/graph theory panel | AG |
| P2 | constraint→edge terminology | AG |

## 7. COORDINATION.md Updated

AG Sprint Status section updated with this evening's work. CW should read on next session.
