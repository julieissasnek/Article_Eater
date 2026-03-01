# Restoration of Clamped Confidence Values

**Date**: 2026-02-23  
**Baseline Commit**: 90a53c6 (pre-clamping state)  
**Status**: COMPLETED  

---

## Executive Summary

A destructive operation had previously clamped 97 confidence values to ceiling maximums across 25 templates with mechanism chains. This report documents the restoration of 69 of those values (via `scripts/restore_clamped_values.py`), the updating of the lint infrastructure to be report-only, and the current state of ceiling violations flagged for expert panel review.

### Key Numbers

| Metric | Value |
|--------|-------|
| **Total Restorations** | 69 |
| **Templates Affected** | 25 |
| **Warrant Types** | 6 (MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, CONSTITUTIVE, ANALOGICAL) |
| **Total Epistemic Loss Recovered** | 5.66 confidence units |
| **Current Violations (Restored)** | 69 steps flagged with `ceiling_status: "exceeds"` |
| **Current Violations (Unflagged)** | 19 bridge-warrant violations (root-level confidences recalculated from restored step values) |

---

## What Was Clamped

The `scripts/auto_cap_ceilings.py` script had destructively reduced confidence values to exactly match ceiling limits whenever:
- A step confidence > ceiling for its warrant type
- The value was written back to the JSON file with no recovery path

### Ceiling Limits

```
MECHANISM:               0.60
EMPIRICAL_COVARIANCE:   0.60
FUNCTIONAL:             0.50
CAPACITY:               0.45
CONSTITUTIVE:           0.75
ANALOGICAL:             0.35
THEORETICAL_DEFAULT:    0.40
```

### Example of Clamping

**CB_SLEEP_ARCHITECTURE_002, Step 1** (MECHANISM warrant):
- Original value: 0.78
- Clamped to: 0.60
- Loss: 0.18 confidence units

---

## Restoration Process

### Script: `scripts/restore_clamped_values.py`

The restoration script performs the following steps:

1. **Load current and baseline versions** — For each template with `mechanism_chain`:
   - Load the current JSON from disk
   - Fetch the same template from git commit 90a53c6
   - Skip if the template doesn't exist in the baseline commit

2. **Detect clamping** — For each mechanism chain step:
   - Check if `current_confidence == ceiling AND original_confidence > ceiling`
   - If true, restoration is needed

3. **Restore values** — When clamping is detected:
   - Restore `step.confidence = original_value`
   - Add field `step.ceiling_status = "exceeds"` to flag for panel review

4. **Recalculate root confidence** — For any modified template:
   - Calculate mean of all step confidences
   - Update the template's root `confidence` field

5. **Write back to disk** — Modified templates are persisted with updated values

6. **Generate report** — Save `data/restorations.json` with full audit trail

### Execution

```bash
python3 scripts/restore_clamped_values.py
```

**Output Summary**:
```
Processed 208 templates
Modified 25 templates
Restored 69 confidence values
```

---

## Restoration Details

### Restorations by Warrant Type

#### MECHANISM (47 restorations)
- **Ceiling**: 0.60
- **Original value range**: 0.62–0.85
- **Total loss recovered**: 3.85 confidence units
- **Maximum single loss**: 0.25 (T6, step 3)
- **Affected templates**: CB2, CIRCADIAN_ARCH_*, DAYLIGHT_MULTICHANNEL, PP_*, NM_CIRCADIAN_*, T6, T7, VF1_*, and others

#### EMPIRICAL_COVARIANCE (7 restorations)
- **Ceiling**: 0.60
- **Original value range**: 0.65–0.80
- **Total loss recovered**: 0.83 confidence units
- **Maximum single loss**: 0.20 (LUM_CONTRAST_PE_001, step 4)
- **Affected templates**: CB2, LUM_CONTRAST_PE_001, DYNAMIC_LIGHT_TEMPORAL_001, T6, NATURE_VIEW_CONVERGENCE_001

#### FUNCTIONAL (7 restorations)
- **Ceiling**: 0.50
- **Original value range**: 0.52–0.60
- **Total loss recovered**: 0.37 confidence units
- **Maximum single loss**: 0.10
- **Affected templates**: CCT_TEMPORAL_ECOLOGICAL_001, CIRCADIAN_ARCH_REGULATION_001, DAYLIGHT_MULTICHANNEL_001

#### CAPACITY (3 restorations)
- **Ceiling**: 0.45
- **Original value range**: 0.48–0.55
- **Total loss recovered**: 0.18 confidence units
- **Maximum single loss**: 0.10 (T7, step 4)
- **Affected templates**: T7, T14, DYNAMIC_LIGHT_TEMPORAL_001

#### CONSTITUTIVE (3 restorations)
- **Ceiling**: 0.75
- **Original value range**: 0.80–0.88
- **Total loss recovered**: 0.28 confidence units
- **Maximum single loss**: 0.13 (CCT_TEMPORAL_ECOLOGICAL_001, step 1)
- **Affected templates**: CCT_TEMPORAL_ECOLOGICAL_001, T6

#### ANALOGICAL (2 restorations)
- **Ceiling**: 0.35
- **Original value range**: 0.40–0.45
- **Total loss recovered**: 0.15 confidence units
- **Maximum single loss**: 0.10 (VF2_VISUAL_RHYTHM_001, step 2)
- **Affected templates**: VF2_VISUAL_RHYTHM_001

---

## Updated Lint Infrastructure

### Script: `scripts/lint_bridge_ceilings.py` (UPDATED)

The lint script has been updated to:
- **REPORT violations** but NOT auto-fix them
- **Detect `ceiling_status` field** on mechanism chain steps
- **Separate violations into two categories**:
  1. **Flagged for panel review** (`ceiling_status: "exceeds"`) — 69 violations
  2. **Unflagged** (no `ceiling_status` set) — 19 violations

### Current Violation Report

**Total violations**: 88 across 25 templates

#### Flagged for Panel Review (69)
All mechanism chain steps that were restored from clamped values are flagged with `ceiling_status: "exceeds"` and appear in the output with a **★** marker.

Examples:
```
★ CB_SLEEP_ARCHITECTURE_002 | mechanism_chain[1].confidence  | MECHANISM            | conf=0.78 > ceil=0.60 (Δ=0.180)
★ T6                   | mechanism_chain[3].confidence  | MECHANISM            | conf=0.85 > ceil=0.60 (Δ=0.250)
★ NATURE_VIEW_CONVERGENCE_001 | mechanism_chain[2].confidence  | EMPIRICAL_COVARIANCE | conf=0.75 > ceil=0.60 (Δ=0.150)
```

#### Unflagged (19)
These are **bridge-warrant violations** (root-level confidences) that exceed ceilings. They are not flagged for panel review because:
- They resulted from **recalculating** root confidence as the mean of restored step values
- They represent the aggregate epistemic standing of the template
- They should be addressed through principled re-calibration rather than simple restoration

Examples:
```
  T6                   | bridge_warrant                 | MECHANISM            | conf=0.74 > ceil=0.60 (Δ=0.143)
  NATURE_VIEW_CONVERGENCE_001 | bridge_warrant                 | EMPIRICAL_COVARIANCE | conf=0.68 > ceil=0.60 (Δ=0.083)
```

---

## Running the Lint Check

To see current ceiling violations with restoration status:

```bash
python3 scripts/lint_bridge_ceilings.py
```

This produces:
1. A JSON report at `data/ceiling_violation_report.json`
2. Terminal output showing violations separated by flag status
3. A message confirming that violations are reported but NOT auto-fixed

---

## Epistemic Impact

### Loss Recovered

By restoring 69 confidence values:
- **Total confidence units recovered**: 5.66
- **Largest single recovery**: 0.25 (T6, step 3, MECHANISM warrant)
- **Average recovery per restoration**: 0.082 confidence units

### Root-Level Recalculation

When mechanism chain steps are modified, the root confidence is recalculated as:

$$\text{root\_confidence} = \frac{1}{n} \sum_{i=1}^{n} \text{step\_confidence}_i$$

This creates a cascading effect:
- **Increases in step confidence** → increases root confidence
- **Root confidence may exceed ceiling** → creates unflagged violations
- **Example**: T6 root confidence was 0.60 (at ceiling); after restoring 6 steps (mean 0.747), root is now 0.74 (Δ = +0.14)

---

## Files Modified

### Created

- `scripts/restore_clamped_values.py` — Restoration script with full audit trail
- `docs/RESTORATION_CLAMPED_VALUES_2026-02-23.md` — This document

### Updated

- `scripts/lint_bridge_ceilings.py` — Now report-only; detects `ceiling_status` field
- 25 template JSON files — Steps restored, `ceiling_status: "exceeds"` added, root confidence recalculated

### Generated

- `data/restorations.json` — Full audit log with original/clamped values for each restoration

---

## Next Steps for Panel Review

The expert panel should:

1. **Review flagged steps** (69 with `ceiling_status: "exceeds"`):
   - Evaluate whether the restored original values are justified
   - Consider whether ceilings should be adjusted upward for certain warrant types
   - Assess if particular templates warrant special handling

2. **Review unflagged bridge violations** (19 root-level):
   - Decide whether to accept elevated root confidences
   - Consider re-calibrating affected templates
   - Possibly adjust ceiling policies for aggregate confidence

3. **Assess ceiling ceiling policy** itself:
   - Are current ceilings appropriate for their warrant types?
   - Should different templates have different ceiling policies?
   - Is there a principled epistemic reason for the current ceilings?

---

## Audit Trail

### Data Files

| File | Purpose |
|------|---------|
| `data/restorations.json` | Full log of all 69 restorations with original/clamped values |
| `data/ceiling_violation_report.json` | Current violation report (88 violations, flagged and unflagged) |

### Scripts

| Script | Mode | Purpose |
|--------|------|---------|
| `scripts/restore_clamped_values.py` | Active | Restore values and flag for panel review |
| `scripts/lint_bridge_ceilings.py` | Report-only | Detect and report violations (not auto-fix) |
| `scripts/auto_cap_ceilings.py` | Deprecated | Original destructive clamping (kept for reference) |

---

## References

- **Commit 90a53c6**: Pre-clamping baseline (used for restoration)
- **Restoration Date**: 2026-02-23
- **Confidence Ceiling Architecture**: E-02 (Epistemic Tier 2)

---

**Status**: READY FOR PANEL REVIEW
