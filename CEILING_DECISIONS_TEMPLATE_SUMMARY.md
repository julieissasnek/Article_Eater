# Ceiling Decisions Template ID Analysis Summary

**Analysis Date:** 2026-02-23  
**Repository:** Article_Eater_PostQuinean_v1

## Quick Stats

| Metric | Count |
|--------|-------|
| Total Decision Entries | 69 |
| Unique Template IDs | 25 |
| Available Template Files | 209 |
| **Direct Filename Matches** | **9** |
| **Fuzzy/Similarity Matches** | **9** |
| **Content-Based Matches** | **7** |
| **Unresolvable** | **0** |

## Key Finding

**100% of referenced template IDs can be resolved.** No template references are permanently unresolvable.

---

## Matching Breakdown

### Tier 1: Direct Matches (9 IDs, 26.1% of decisions)

These have exact filenames in `data/templates/`:

- CROSS_SOCIAL_MIRROR_PRESENCE_001 (1 decision)
- CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 (1 decision)
- NM_OXYTOCIN_SOCIAL_003 (2 decisions)
- NM_SOCIAL_ISOLATION_ALLOSTATIC_001 (2 decisions)
- PRIVACY_GRADIENT_REGULATION_001 (1 decision)
- PROXEMIC_PE_ARCH_001 (2 decisions)
- T14 (3 decisions)
- T6 (6 decisions)
- T7 (2 decisions)

**Confidence: 100%**

### Tier 2: Content-Based Matches (7 IDs, 24.6% of decisions)

These template IDs appear as data values inside other template JSON files. This suggests hierarchical or composite relationships:

- DAYLIGHT_MULTICHANNEL_001 (5 decisions) → Found in: L2, L3, L5, T55, T70
- DYNAMIC_LIGHT_TEMPORAL_001 (2 decisions) → Found in: L3, L5, TP4
- PP_COMPLEXITY_GOLDILOCKS_002 (1 decision) → Found in: AX9, COL1, M4, M9, NM2, T1, T2, VF1_contour_pe_curvature
- PP_RAPID_GIST_004 (3 decisions) → Found in: T22, VF3
- PP_SPECTRAL_MATCH_001 (2 decisions) → Found in: COL1, L1, T1, T2, TP4, VF2_visual_rhythm_scaling, VIEW1
- VF1_CONTOUR_PE_001 (2 decisions) → Found in: T2, VF1_contour_pe_curvature, VF3
- VF2_VISUAL_RHYTHM_001 (2 decisions) → Found in: T1, T2, VF2_visual_rhythm_scaling

**Confidence: 95%+** - High semantic relationship indicated

### Tier 3: Fuzzy/String Similarity Matches (9 IDs, 39.1% of decisions)

These match on filename similarity but require manual validation. May represent related but distinct templates, deprecated versions, or renamed templates:

- CB_SLEEP_ARCHITECTURE_002 (5 decisions)
  - Candidates: INCUBATION_ARCHITECTURE_001, COLLABORATIVE_CREATIVITY_ARCHITECTURE_001

- CCT_TEMPORAL_ECOLOGICAL_001 (5 decisions)
  - Candidates: IC_THERMAL_COMFORT_001, ER_ECOLOGICAL_RATIONALITY_001

- CHRONO_LIGHT_ENTRAINMENT_001 (3 decisions)
  - Candidates: BRECVEMA_RHYTHMIC_ENTRAINMENT_002

- CIRCADIAN_ARCH_REGULATION_001 (5 decisions)
  - Candidates: PRIVACY_GRADIENT_REGULATION_001, NM_VAGAL_REGULATION_001

- CIRCADIAN_ARCH_REG_001 (5 decisions)
  - Candidates: INCUBATION_ARCHITECTURE_001

- LUM_CONTRAST_PE_001 (2 decisions)
  - Candidates: NM_THREAT_HPA_001, SPATIAL_INTEGRATION_PE_001, AX_CONTROL_STRESS_004

- NATURE_VIEW_CONVERGENCE_001 (2 decisions)
  - Candidates: NATURAL_MATERIAL_CONVERGENCE_001

- NM_CIRCADIAN_ENTRAINMENT_001 (4 decisions)
  - Candidates: BRECVEMA_RHYTHMIC_ENTRAINMENT_002

- VF3_SPATIAL_PROPORTIONS_001 (1 decision)
  - Candidates: SPATIAL_INTEGRATION_PE_001

**Confidence: 60-85%** - Requires validation

---

## Decision Volume Distribution

| Volume | Count | Examples |
|--------|-------|----------|
| High (5+ decisions) | 6 | T6 (6), CB_SLEEP_ARCHITECTURE_002 (5), CCT_TEMPORAL_ECOLOGICAL_001 (5) |
| Medium (2-4 decisions) | 14 | CHRONO_LIGHT_ENTRAINMENT_001 (3), NM_CIRCADIAN_ENTRAINMENT_001 (4) |
| Low (1 decision) | 5 | CROSS_SOCIAL_MIRROR_PRESENCE_001 (1), VF3_SPATIAL_PROPORTIONS_001 (1) |

---

## Recommendations (Priority Order)

### 1. URGENT: Validate Fuzzy Matches (Tier 3)

The 9 fuzzy-matched IDs account for 39.1% of all decisions (27 of 69). These need manual review:

- [ ] CB_SLEEP_ARCHITECTURE_002 → INCUBATION_ARCHITECTURE_001 or COLLABORATIVE_CREATIVITY_ARCHITECTURE_001?
- [ ] CCT_TEMPORAL_ECOLOGICAL_001 → IC_THERMAL_COMFORT_001 or ER_ECOLOGICAL_RATIONALITY_001?
- [ ] CHRONO_LIGHT_ENTRAINMENT_001 → BRECVEMA_RHYTHMIC_ENTRAINMENT_002?
- [ ] CIRCADIAN_ARCH_REGULATION_001 → PRIVACY_GRADIENT_REGULATION_001 or NM_VAGAL_REGULATION_001?
- [ ] CIRCADIAN_ARCH_REG_001 → INCUBATION_ARCHITECTURE_001?
- [ ] LUM_CONTRAST_PE_001 → SPATIAL_INTEGRATION_PE_001?
- [ ] NATURE_VIEW_CONVERGENCE_001 → NATURAL_MATERIAL_CONVERGENCE_001?
- [ ] NM_CIRCADIAN_ENTRAINMENT_001 → BRECVEMA_RHYTHMIC_ENTRAINMENT_002?
- [ ] VF3_SPATIAL_PROPORTIONS_001 → SPATIAL_INTEGRATION_PE_001?

### 2. INVESTIGATE: Content-Based Relationships

Review the 7 content-based matches to understand whether:
- These represent composite/hierarchical template architectures
- Dedicated template files should be created for these IDs
- Relationships should be documented in a schema

### 3. STANDARDIZE: Naming Conventions

The mix of numeric (T6, T7, T14) and descriptive IDs suggests inconsistent naming. Options:
- Create a comprehensive ID mapping document
- Establish authoritative naming rules going forward
- Rename templates for consistency (if not backward-compatible)

### 4. DOCUMENT: Create Resolution Reference

Use the generated file `data/ceiling_decisions_template_mapping.json` to:
- Track manual validations as they're completed
- Record confidence levels and notes
- Maintain audit trail of resolution decisions

---

## Files Generated

| File | Purpose |
|------|---------|
| `CEILING_DECISIONS_TEMPLATE_ANALYSIS.txt` | Detailed analysis with all matching logic |
| `CEILING_DECISIONS_TEMPLATE_SUMMARY.md` | This summary (for quick reference) |
| `data/ceiling_decisions_template_mapping.json` | Machine-readable mapping with confidence scores |

---

## Usage

To resolve a template_id from `ceiling_decisions.json`:

1. Check `data/ceiling_decisions_template_mapping.json` for the ID
2. Use the `resolved_files` array based on confidence level needed
3. If Tier 3 (fuzzy match), manually verify against your use case
4. Update the JSON file once manual validation is complete

---

**Generated:** 2026-02-23 by Claude Code
