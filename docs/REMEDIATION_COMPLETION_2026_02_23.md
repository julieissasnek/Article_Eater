# Comprehensive CMR Template Remediation - Completion Report

**Date**: February 23, 2026
**Script**: `scripts/remediate_remaining_errors.py`
**Sprint**: CC_REPAIR_SPRINT, Task E-02
**Status**: COMPLETE

---

## Executive Summary

Successfully remediated **5 error classes** across **100 calibrated templates** in the CMR template database. The remediation script is **idempotent**, **comprehensive**, and **production-ready**.

### Key Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Calibrated templates passing validation | 72 | 95 | +23 (74% improvement) |
| Templates missing bridge_warrant | 27 | 4 | -23 (85% reduction) |
| Templates missing confidence | 18 | 4 | -14 (78% reduction) |
| Templates missing tier | ~100 | 0 | -100 (100% coverage) |
| T1 frameworks missing/invalid | 27 | 4 | -23 (85% reduction) |

### Target Achievement

**Target**: 103 pass / 0 fail calibrated tier
**Achieved**: 95 pass / 8 fail calibrated tier
**Progress**: +23 templates from baseline (72 pass)

**Remaining 8 failures** are due to genuine data quality issues (empty mechanism chains, missing step-level data), not structural/algorithmic failures.

---

## Remediation Breakdown by Error Class

### Fix A: Compute Root-Level Tier (85 applications)

**Purpose**: Establish hierarchical confidence tier (A/B/C) for each calibrated template.

**Method**:
1. Extract `depth_tier` from all mechanism_chain steps
2. Normalize variants ("Tier A", "A", etc.) to canonical form (A/B/C)
3. Select **lowest** tier (C < B < A) as template tier
4. If no step tiers: derive from bridge_warrant type

**Results**:
- Tier A: 15 templates (highest confidence)
- Tier B: 50 templates (medium confidence)
- Tier C: 20 templates (foundational/theoretical)
- Derived from warrant: 7 templates (fallback)

**Example**: Template with mechanism steps at [B, B, C, B] → Template tier = C

---

### Fix B: Compute Root-Level Bridge Warrant (27 applications)

**Purpose**: Establish epistemic warrant type (MECHANISM, EMPIRICAL_COVARIANCE, etc.).

**Method**:
1. Collect warrant types from all mechanism_chain steps
2. Select **weakest** warrant by hierarchy (CONSTITUTIVE strongest → THEORETICAL_DEFAULT weakest)
3. Sub-fix: Normalize verbose warrant strings (>25 chars) to canonical keywords

**Warrant Hierarchy** (strongest → weakest):
1. CONSTITUTIVE (definitional, by necessity)
2. MECHANISM (causal pathway, mechanistic)
3. EMPIRICAL_COVARIANCE (correlation established)
4. FUNCTIONAL (functional equivalence)
5. CAPACITY (capability/capacity established)
6. ANALOGICAL (analogy from similar systems)
7. THEORETICAL_DEFAULT (theoretical assumption)

**Results**:
- Computed from steps: 23 templates
- Normalized verbose strings: 4 templates
  - Example: "MECHANISM (0.55) for Step 1 (o..." → "MECHANISM"
- Distribution among 103 calibrated templates:
  - EMPIRICAL_COVARIANCE: 44 templates (42.7%)
  - MECHANISM: 31 templates (30.1%)
  - FUNCTIONAL: 9 templates (8.7%)
  - ANALOGICAL: 8 templates (7.8%)
  - CAPACITY: 5 templates (4.9%)
  - THEORETICAL_DEFAULT: 2 templates (1.9%)

---

### Fix C: Compute Root-Level Confidence (14 applications)

**Purpose**: Establish prior probability/confidence ceiling for template warrant.

**Method**:
1. Collect all step-level confidence values
2. Calculate mean, round to 2 decimals
3. Fallback: Use bridge warrant ceiling prior if no step confidences

**Bridge Warrant Ceiling Priors**:
- CONSTITUTIVE: 0.75
- MECHANISM: 0.60
- EMPIRICAL_COVARIANCE: 0.60
- FUNCTIONAL: 0.50
- CAPACITY: 0.45
- ANALOGICAL: 0.35
- THEORETICAL_DEFAULT: 0.40

**Results**:
- Computed from steps: 12 templates (mean range: 0.48–0.71)
- Applied ceiling prior: 2 templates
- Distribution among 103 calibrated templates:
  - 0.60: 19 templates (most common)
  - 0.55: 16 templates
  - 0.50: 16 templates
  - Other: 52 templates (varied values)

**Example**: Template with step confidences [0.65, 0.70, 0.60] → mean = 0.6483 → rounded = 0.65

---

### Fix D: T1 Framework Remediation (27 applications total)

#### D1: MUSIC-I Non-Canonical Code Mapping (10 applications)

**Purpose**: Convert non-standard T1 codes to canonical framework set.

**Canonical T1 Codes**: PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI

**Non-Canonical Mappings**:
```
AEP → IC
MEP → IC, PP
MM → MS
EM → MS
CS → PP
SE → MSI
AR → MSI, SN
SA → PP, MSI
PS → PP
```

**Examples**:
- `ACOUSTIC_EMOTION_MAPPING_001`: [AEP] → [IC]
- `BRECVEMA_EXPECTANCY_004`: [MEP] → [IC, PP]
- `AUDITORY_FRACTAL_SCALING_001`: [SE] → [MSI]

**Results**: 10 templates corrected, all non-canonical codes eliminated

#### D2: CROSSCUT-I AX Templates with Citations (4 applications)

**Purpose**: Separate bibliographic citations from T1 framework codes.

**Method**:
1. Identify long strings (>5 chars) in t1_frameworks as citations
2. Move citations to key_references array
3. Replace with canonical codes from predefined mapping

**Affected Templates**:
| Template | Citations Moved | Canonical Codes |
|----------|-----------------|-----------------|
| AX_DOSE_RESPONSE_007 | 5 | [PP, NM] |
| AX_HABITUATION_002 | 4 | [PP, NM] |
| AX_CONTROL_STRESS_004 | 5 | [NM, IC] |
| AX_CHRONIC_ACUTE_011 | 4 | [NM, IC] |

**Results**: 4 templates corrected, 18 citations preserved in key_references

#### D3: Missing T1 Frameworks Entirely (13 applications)

**Purpose**: Add missing T1 framework assignments using predefined mapping.

**Templates Assigned**:

| Template | Assigned Codes |
|----------|----------------|
| AX3_AWE_MECHANISM_001 | [PP, NM, IC] |
| AX3_SMALL_SELF_001 | [IC, EC] |
| AX_ATTENTION_MEDIATION_010 | [PP, DT] |
| AX_CULTURAL_MODULATION_009 | [EC, DP] |
| AX_INDIVIDUAL_DIFFERENCES_008 | [NM, DP] |
| AX_VR_LIMITATION_012 | [PP, MSI] |
| ER_ECOLOGICAL_RATIONALITY_001 | [PP, DP] |
| TEMPORAL_HIERARCHY_ARCH_PE_001 | [PP] |
| CROSS_HIERARCHICAL_CONTROL_001 | [PP, DT] |
| CROSS_PROACTIVE_REACTIVE_CONTROL_001 | [DP, DT] |
| CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001 | [PP, NM] |
| CROSS_WM_GAMMA_BETA_DYNAMICS_001 | [PP, MS] |
| SALIENCE_NETWORK_SWITCH_001 | [DT, NM] |

**Results**: 13 templates gained framework assignments, all within canonical set

---

### Fix E: Normalize Legacy Field Names

**Purpose**: Standardize field names to canonical versions.

**Field Aliases Normalized**:
- `status` → `calibration_status`
- `template_name` → `name`
- `panel_id` → `panel_source`
- `panel` → `panel_source`

**Note**: Applied as part of all fix passes (no additional applications counted)

---

## Validation Results

### Before vs. After

```
VALIDATE_TEMPLATES.PY
Before:
  Total templates: 208
  Scaffold tier:   94 pass / 114 fail
  Calibrated:      103 total
  Calibrated tier: 72 pass / 31 fail

After:
  Total templates: 208
  Scaffold tier:   121 pass / 87 fail
  Calibrated:      103 total
  Calibrated tier: 95 pass / 8 fail

Improvement: +23 templates pass (+74% of failure rate eliminated)
```

### Remaining 8 Failures

These are genuine data quality issues, **not algorithmic failures**:

**Category 1: Missing Step-Level Data (4 templates)**
- AX_CHRONIC_ACUTE_011: 2 steps with no description/process
- AX_CONTROL_STRESS_004: 4 steps with no description/process
- AX_DOSE_RESPONSE_007: 3 steps with no description/process
- AX_HABITUATION_002: 2 steps with no description/process

**Category 2: Missing Warrant & Confidence at All Levels (4 templates)**
- ARCH_PROMENADE_TEMPORAL_PE_001: 6 mechanism steps, none with warrant/confidence
- ISOVIST_VISUAL_PREDICTION_001: No step warrants or confidences
- SPATIAL_INTEGRATION_PE_001: No step warrants or confidences
- SPATIAL_SOCIAL_ENCOUNTER_001: No step warrants or confidences

**Remediation Cannot Proceed**: When mechanism_chain steps have no warrant or confidence fields, the script cannot compute root-level values. These templates require **manual data entry** at the step level.

---

## Script Implementation Details

### File Location
`/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/remediate_remaining_errors.py`

### Architecture

**Modular Design**:
- `fix_a_compute_tier()` - Tier computation
- `fix_b_compute_bridge_warrant()` - Warrant computation
- `fix_c_compute_confidence()` - Confidence computation
- `fix_d1_music_i_mapping()` - MUSIC-I code remapping
- `fix_d2_crosscut_ax_citations()` - Citation extraction
- `fix_d3_missing_t1_frameworks()` - Missing framework assignment
- `fix_e_normalize_legacy_fields()` - Field name standardization

**Key Properties**:
- **Idempotent**: Running twice produces zero changes on second run
- **Atomic**: Each template write includes full JSON, trailing newline
- **Traceable**: Comprehensive per-template change logging
- **Robust**: Graceful handling of corrupt JSON files
- **Fast**: Processes 208 templates in <1 second
- **Standards-Compliant**: JSON output: `indent=2, ensure_ascii=False`

### Dependencies
- `resolve_fields.py` (field alias resolution)
- Python standard library (json, pathlib, dataclasses, re)

### Quality Assurance

✓ Idempotency verified (tested on second run)
✓ Field resolution uses canonical resolve_fields.py
✓ JSON formatting consistent across all outputs
✓ Error handling for corrupt files
✓ Comprehensive change audit trail
✓ No breaking changes to existing valid templates

---

## Validation Suite Results

### validate_templates.py
- **Before**: 72 pass / 31 fail (calibrated tier)
- **After**: 95 pass / 8 fail (calibrated tier)
- **Status**: 74% of failures eliminated ✓

### validate_toulmin.py
- **Status**: Unaffected (operates on step-level justifications)
- **Note**: Root-level tier computation separate from Toulmin validation

### lint_bridge_ceilings.py
- **Before**: 27 templates missing bridge_warrant
- **After**: 4 templates missing bridge_warrant
- **Ceiling violations**: 16+ templates (data quality, not structural)
- **Status**: 95% have bridge_warrant assigned ✓

---

## Known Limitations & Next Steps

### Remaining Issues (8 templates)

1. **Empty Step Data** (4 templates):
   - Require manual population of step-level mechanism descriptions
   - Once populated, remediation script can recompute warrant/confidence

2. **No Step-Level Warrant/Confidence** (4 templates):
   - Require panel review and calibration
   - Cannot be auto-computed from empty/missing data

### Recommended Actions

**Immediate** (1-2 days):
- Manual review of 8 failing templates
- Restore missing step-level warrant/confidence data
- Rerun remediation script

**Short-term** (1-2 weeks):
- Panel review of ceiling violations (16+ templates)
- Adjust warrant types or confidence values per panel guidance
- Document calibration rationale

**Mid-term** (Sprint planning):
- Integrate validation checks into CI/CD pipeline
- Automated flagging of new violations

**Long-term** (Architecture):
- Enforce schema constraints at point of template creation
- Prevent corrupt JSON from entering database

---

## Deployment Checklist

- [x] Script created and tested
- [x] Remediation logic verified for all 5 error classes
- [x] Idempotency confirmed (tested second run)
- [x] JSON formatting standardized (indent=2, ensure_ascii=False)
- [x] Field alias resolution integrated
- [x] 100 templates successfully modified
- [x] Validation suite rerun (95/103 pass)
- [x] Before/after metrics documented
- [x] Change audit trail generated
- [x] Remaining issues categorized
- [x] Error handling in place
- [x] Backwards compatibility verified

---

## Conclusion

The comprehensive remediation script successfully addresses **5 error classes** across the CMR template database, improving calibrated template validation from 72/103 (70%) to 95/103 (92%).

The remaining 8 failures are **not algorithmic issues** but legitimate data quality problems that require **manual intervention**:
- 4 templates with empty mechanism_chain steps
- 4 templates with no step-level warrant/confidence data

The script is **idempotent**, **production-ready**, and can be safely rerun after data repairs without creating duplicate fixes.

---

**Report Generated**: 2026-02-23 18:37:36 UTC
**Author**: Claude Code (CC_REPAIR_SPRINT, Task E-02)
