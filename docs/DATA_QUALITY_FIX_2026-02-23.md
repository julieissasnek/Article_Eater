# Data Quality Gap Resolution Report

**Date**: 2026-02-23
**Status**: COMPLETE

## Summary

Fixed two critical data quality gaps in 103 calibrated templates using automated script (`scripts/fix_remaining_gaps.py`).

## Gap 1: Empty t1_frameworks (15 templates)

**Problem**: 15 calibrated templates lacked framework assignments (`t1_frameworks` field).

**Solution**: Assigned frameworks based on mechanistic content:

### Memory Systems (MS) - 7 templates
- `ED_HIPPOCAMPAL_ENCODING_001` → `['MS', 'SN']` (hippocampal encoding + spatial navigation)
- `ED_PATTERN_SEP_COMP_001` → `['MS', 'PP']` (pattern separation + predictive processing)
- `ED_PE_ENCODING_PRINCIPLE_001` → `['MS', 'PP']` (prediction error in memory)
- `ED_RECONSOLIDATION_001` → `['MS']` (memory consolidation)
- `ED_SCHEMA_ENCODING_001` → `['MS', 'PP']` (schema-based prediction)
- `ED_SYSTEMS_CONSOLIDATION_001` → `['MS']` (systems-level consolidation)
- `THRESHOLD_EPISODIC_BOUNDARY_001` → `['MS', 'SN']` (episodic memory + spatial)

### Visual/Predictive Processing (PP) - 7 templates
- `L1_luminance_contrast_pe` → `['PP']` (luminance contrast prediction error)
- `VF1_contour_pe_curvature` → `['PP']` (contour curvature prediction)
- `VF2_visual_rhythm_scaling` → `['PP']` (visual rhythm/saccadic prediction)
- `VF3` → `['PP']` (spatial proportion prediction)
- Architecture thermal templates:
  - `T1` → `['PP', 'NM']` (fractal/1f spectral + neuromodulation)
  - `T2` → `['PP', 'NM']` (complexity prediction)
  - `T22` → `['PP', 'NM']` (proportional/LSF prediction)

### Social/Environmental (IC + NM + PP) - 1 template
- `VIEW1` → `['PP', 'NM', 'IC']` (nature view: predictive + neuromodulatory + interoceptive)

**Result**: All 15 templates now have framework assignments. Distribution:
- Memory systems (MS): 13 templates
- Predictive processing (PP): 52 templates
- Neuromodulation (NM): 11 templates
- Spatial navigation (SN): 2 templates
- Interoception (IC): 2 templates

## Gap 2: Missing Root-Level Confidence (23 templates)

**Problem**: 23 calibrated templates had `confidence: null`, preventing downstream Bayesian inference.

**Solution**: Computed confidence as mean of step-level confidences in `mechanism_chain`:

1. For each step in the chain, used step's `confidence` if present
2. If step confidence was null, applied default based on `bridge_warrant` type:
   - `CONSTITUTIVE`: 0.70
   - `MECHANISM`: 0.55
   - `EMPIRICAL_COVARIANCE`: 0.50
   - `FUNCTIONAL`: 0.45
   - `CAPACITY`: 0.40
   - `THEORETICAL_DEFAULT`: 0.35
   - `ANALOGICAL`: 0.30

3. Rounded mean to 2 decimal places

**Result**: All 23 templates now have confidence values:
- Mean across all calibrated templates: 0.536
- Range: [0.35, 0.71]
- Distribution:
  - High confidence (≥0.60): 30 templates
  - Medium confidence (0.40–0.60): 72 templates
  - Low confidence (<0.40): 1 template

## Validation Results

```
Calibrated templates: 103/103 now pass
- t1_frameworks present: 103/103 (100%)
- confidence present: 103/103 (100%)
- No gaps remaining: 0
```

## Files Modified

- `scripts/fix_remaining_gaps.py` (NEW) — Automated gap fixing script
- `data/templates/*.json` (MODIFIED) — All 15+23 affected templates

## Technical Notes

- Script is idempotent: safe to run multiple times
- Confidence computation preserves existing step-level values
- Framework assignments align with domain literature on neurocognitive architectures
- All changes validated against `scripts/validate_templates.py`

## Next Steps

- Monitor for new calibrated templates; apply same framework logic
- Consider parameterizing framework inference rules for maintenance
- Validate confidence distributions in downstream Bayesian network inference
