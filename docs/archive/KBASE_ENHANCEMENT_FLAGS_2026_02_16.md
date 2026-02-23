# Knowledge Base Enhancement Flags

**Date**: February 16, 2026
**Source**: QA Agent Specification Testing
**Priority**: HIGH — These gaps block QA agent from answering important questions

---

## Overview

During testing of the QA Agent Specification against real queries, we discovered a systematic gap: **Article Eater has rich Tier 1 theory templates that are NOT connected to the BN mechanism registry**. This means:
- The knowledge EXISTS in the system
- But the QA agent cannot find it via mechanism lookup
- The bridge between templates and registry is missing

---

## Enhancement #1: Curvature / Contour Preference

### Query That Exposed Gap
> "How strong (i.e., angle of curvature) are the walls that people most prefer over rectilinear spaces?"

### What EXISTS (Article Eater)

**File**: `data/templates/VF1_contour_pe_curvature.json`

Rich Tier 1 theory including:
- **Framework alignment**: Predictive Processing, approach-avoidance, processing fluency, neuroaesthetics
- **Mechanism**: Curved contours → low prediction error (gradual change); angular contours → high PE at vertices (abrupt direction change)
- **Causal links**: contour_curvature → processing_fluency → preference; curved_contours → approach_tendency
- **Evidence base**: Bar & Neta (2006), Vartanian et al. (2013)
- **Neural pathway**: Visual cortex curvature detectors → fusiform gyrus → amygdala

### What's MISSING (BN Mechanism Registry)

No entry for `curvature` or `contour` in `BN_graphical/src/mechanisms/mechanism_registry.json`

### Required Enhancement

1. **Create mechanism registry entry**:
   ```json
   {
     "mechanism_id": "curvature_preference",
     "attribute": "contour_curvature",
     "outcome": "aesthetic_preference",
     "goldilocks": {
       "optimal_value": "TBD - extract from meta-analysis",
       "optimal_width": "TBD",
       "asymmetry": "too angular worse than too curved"
     }
   }
   ```

2. **Extract quantitative parameters** from:
   - Meta-analysis DOI: 10.1111/nyas.14919 (currently in no_claims queue)
   - Specific angle measurements for optimal curvature

3. **Bridge VF1 template to mechanism registry**

### Priority
**HIGH** — Curvature is a core architectural variable with well-established theory

---

## Enhancement #2: Wall Color → Arousal/Agitation

### Query That Exposed Gap
> "Do red walls produce more agitation than light green walls?"

### What EXISTS (Article Eater)

**Files**:
- `data/templates/COL2_color_arousal.json` — Color-Arousal Modulation
- `data/templates/COL1_chromatic_pe.json` — Chromatic Prediction Error
- `data/templates/COLOR_AFFECT_024.json` — Color properties → arousal/valence

Rich theory including:
- **Three arousal dimensions** (in order of effect magnitude):
  1. Saturation (primary) — higher saturation → higher arousal
  2. Brightness (secondary) — brighter → higher arousal
  3. Hue (tertiary) — warm > cool at equivalent saturation/brightness
- **Key finding**: "Highly saturated cool blue is MORE arousing than desaturated warm pink"
- **Evidence base**: Valdez & Mehrabian (1994, ~1,500 citations)
- **Framework alignment**: Arousal theory, PAD model, Predictive Processing, retinal activation

### What's MISSING (BN Mechanism Registry)

Only `color_temperature → affective_quality` entry exists (for LIGHTING CCT, not wall color)

No entry for:
- `wall_color_saturation → arousal`
- `wall_color_hue → arousal`
- `chromatic_warmth → agitation`

### Required Enhancement

1. **Create mechanism registry entries**:
   ```json
   {
     "mechanism_id": "color_saturation_arousal",
     "attribute": "color_saturation",
     "outcome": "physiological_arousal",
     "functional_form": "monotonic_increasing",
     "effect_magnitude": "primary"
   },
   {
     "mechanism_id": "color_warmth_arousal",
     "attribute": "color_hue_warmth",
     "outcome": "physiological_arousal",
     "functional_form": "monotonic_increasing",
     "effect_magnitude": "tertiary",
     "note": "Warm hues produce slightly higher arousal than cool at equivalent saturation/brightness"
   }
   ```

2. **Extract quantitative effect sizes** from Valdez & Mehrabian (1994)

3. **Bridge COL1/COL2 templates to mechanism registry**

### Priority
**HIGH** — Color is a primary architectural design variable; the theory is well-established

---

## Enhancement #3: Plants vs Wood Direct Comparison

### Query That Exposed Gap
> "Do wood walls reduce stress as much as plants in a room?"

### What EXISTS

Both mechanisms exist in BN registry:
- `wood_coverage → stress_reduction` (1 pathway, 64% confidence)
- `plant_density → stress_reduction` (2 pathways, ~70% via redundancy)

### What's MISSING

- No **direct comparison studies** in evidence base
- No **effect size data** to enable magnitude comparison
- Cannot answer "as much as" quantitatively

### Required Enhancement

1. **Flag as research gap** — No direct comparison studies exist
2. **Extract effect sizes** (Cohen's d or similar) from:
   - Wood studies (Burnard & Kutnar)
   - Plant studies (Bringslimark et al.)
3. **Add effect_size field** to mechanism registry entries:
   ```json
   "effect_size": {
     "cohens_d": 0.45,
     "confidence_interval": [0.25, 0.65],
     "study_count": 8
   }
   ```

### Priority
**MEDIUM** — Comparison questions are common; indirect reasoning is possible but not ideal

---

## Systematic Pattern Identified

The gap pattern is consistent:
1. **Article Eater templates** contain rich Tier 1 theory (PP, approach-avoidance, etc.)
2. **BN mechanism registry** is missing corresponding entries
3. **QA agent** cannot find theory because it queries mechanisms, not templates

### Recommended Solution

Create **template-to-mechanism bridge** that:
1. Parses all VF*, COL*, etc. templates
2. Extracts mechanism-relevant fields (attribute, outcome, causal_power)
3. Generates skeleton mechanism registry entries
4. Flags for human review to add quantitative parameters

---

## Data Quality Priorities

| Field | Current Status | Priority |
|-------|---------------|----------|
| `mechanism.confidence` | Available | — |
| `claim.effect_size` | Sparse | **HIGH** |
| `goldilocks.optimal_value` | Partial | **HIGH** |
| `mechanism.theory_alignment` | Available | — |
| Direct comparison claims | Missing | **MEDIUM** |
| Effect size units/types | Inconsistent | **HIGH** |

---

## Next Steps

1. [ ] Process curvature meta-analysis (10.1111/nyas.14919) for quantitative parameters
2. [ ] Create mechanism registry entries for curvature, wall color
3. [ ] Extract effect sizes from existing evidence for wood, plants, color
4. [ ] Design template-to-mechanism bridge utility
5. [ ] Audit all VF*, COL*, etc. templates for mechanism coverage

---

*End of Enhancement Flags*
