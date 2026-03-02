# ATLAS Documentation Visualization Generation Guide

**Created**: 2026-03-02  
**Version**: 1.0  
**Status**: Complete (Phases 4–5 implemented)

## Overview

Two comprehensive Python scripts generate 6 publication-quality SVG figures for the ATLAS documentation, covering system operations and data dashboards.

## Files

### Script 1: `scripts/generate_operations_figures.py`
**Phase 4: System Operations** (M-19, M-20, M-21)

**Dependencies**: matplotlib, numpy

**Generated Figures**:

| ID | Figure | File | Size |
|----|--------|------|------|
| M-19 | The Nightly Pipeline: 13 Stages | `m19_nightly_pipeline.svg` | 135 KB |
| M-20 | The Recommendation Loop | `m20_recommendation_loop.svg` | 108 KB |
| M-21 | AESHI Score (System Health Index) | `m21_aeshi_score.svg` | 71 KB |

**Design Principles**:
- Color-coded by function type (data flow, quality checks, computation)
- Tufte-compliant minimal design
- ATLAS visual palette applied throughout
- Direct labeling, no legends where possible

---

### Script 2: `scripts/generate_dashboard_figures.py`
**Phase 5: Data Dashboards** (M-22, M-23, M-24)

**Dependencies**: matplotlib, numpy

**Generated Figures**:

| ID | Figure | File | Size |
|----|--------|------|------|
| M-22 | Evidence Landscape | `m22_evidence_landscape.svg` | 89 KB |
| M-23 | Warrant Distribution | `m23_warrant_distribution.svg` | 89 KB |
| M-24 | Schema Gaps Heatmap | `m24_schema_gaps.svg` | 129 KB |

**Design Principles**:
- Data-driven, using realistic synthetic datasets
- Multiple visual encodings (color, position, size, annotation)
- WCAG 2.1 AA accessible color choices
- Publication-ready SVG format

---

## ATLAS Visual Palette

All figures use the standardized ATLAS palette:

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Deep Navy | Titles, main text | #1B2A4A | Section headers, emphasis |
| Slate Blue | Borders, axes | #2E5090 | Data flow, primary encodings |
| Warm Gold | Highlights | #D4A843 | Computation, emphasis |
| Sage Green | Evidence strength | #5B8C5A | Validation, success states |
| Terracotta | Warnings | #C17B4A | Gaps, failures, low confidence |
| Cool Gray | Secondary | #8B9DAF | Analogical, low priority |
| Cream | Canvas | #F5F0E8 | Background |

---

## Figure Descriptions

### M-19: The Nightly Pipeline (13 Stages)

**Purpose**: Show all stages of the nightly scheduled maintenance pipeline

**Components**:
- 13 stage boxes arranged in 2 rows
- Color-coded by function: blue (data flow), green (quality checks), gold (computation)
- Sequential flow arrows connecting stages
- Failure mode annotations for each stage
- OVERSEER monitoring bar at top
- Total runtime: ~54 minutes

**Data**: Pipeline stage names, durations, and failure modes

---

### M-20: The Recommendation Loop (Circular)

**Purpose**: Illustrate the cyclical nature of gap detection and evidence discovery

**Components**:
- 8 core stages arranged in a circle
- Curved arrows showing flow direction
- Central steady-state annotation (15-20 articles/day, 50 new beliefs/day)
- Script responsibilities labeled between stages
- Quality metrics shown for each stage

**Data**: Stage names, quality thresholds, script names

---

### M-21: AESHI Score (System Health Index)

**Purpose**: Display 6 weighted subscores combining into system health metric

**Components**:
- Horizontal stacked bars for each subscore
- Current score vs. target (7.5/10)
- Color-coded by performance: red (<4), yellow (4–6), green (>6)
- Weighted average formula displayed
- Legend showing score ranges

**Data**: Six subscore categories with weights and current values

---

### M-22: Evidence Landscape

**Purpose**: Show belief distribution across 10 T1 frameworks

**Components**:
- Horizontal bar chart ranked by belief count
- Color-coded by framework dominance
- Percentage labels on each bar
- Confidence distribution annotation (high/medium/low)
- Total beliefs: 3,420

**Data**: Framework names and belief counts (synthetic, realistic distribution)

---

### M-23: Warrant Distribution

**Purpose**: Display warrant type composition across 12 domain panels

**Components**:
- Stacked bar chart (12 domains, 4 warrant types)
- Color-coded warrant types: empirical (green), mechanism (gold), theory-derived (terracotta), analogical (gray)
- Percentage labels on segments
- System average reference line
- Overall composition: ~40% empirical, ~30% mechanism, ~20% theory-derived, ~10% analogical

**Data**: 12 domain names, belief counts, warrant type percentages

---

### M-24: Schema Gaps Heatmap

**Purpose**: Identify gap density across domain panels and epistemic categories

**Components**:
- 12 × 5 heatmap (domains × gap categories)
- Red color intensity indicates gap count
- Cell annotations with gap numbers
- Star markers for hotspots (>15 gaps)
- Summary row showing total gaps per category
- Hotspot text box describing NEUROMOD-I and CROSSCUT-I gaps

**Data**: Gap counts by domain and epistemic category (synthetic, with real hotspots)

---

## Running the Scripts

### Generate Phase 4 (Operations):
```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/generate_operations_figures.py
```

### Generate Phase 5 (Dashboards):
```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/generate_dashboard_figures.py
```

### Generate All (Both Phases):
```bash
python scripts/generate_operations_figures.py && python scripts/generate_dashboard_figures.py
```

---

## Output Location

All SVG files are saved to:
```
/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/figures/
```

Files follow naming convention: `m{number}_{description}.svg`

---

## Customization

To modify figures, edit the relevant script:

1. **Colors**: Update the `PALETTE` dictionary at the top of each script
2. **Data**: Modify the data structures within each function (e.g., `stages`, `frameworks`, `domains`)
3. **Dimensions**: Adjust `figsize` in `plt.figure()` or `plt.subplots()`
4. **Labels**: Edit text content directly in the code

---

## Quality Assurance

All figures have been verified for:
- Correct color application (ATLAS palette)
- Proper SVG format generation
- Reasonable file sizes (>30KB)
- Readable text and clear visual hierarchy
- WCAG 2.1 AA accessibility compliance
- Tufte principles (minimize ink-to-data ratio)

---

## Future Extensions

Possible enhancements:

1. **Interactive version**: Convert static SVGs to interactive D3.js visualizations
2. **Real data integration**: Connect to actual ATLAS database for live updates
3. **Animation**: Add transitions showing temporal changes
4. **Additional panels**: Expand M-22 to show confidence-based treemap
5. **Export formats**: Add PDF, PNG options alongside SVG

---

## Technical Notes

- **SVG Backend**: matplotlib's SVG backend used for vector output
- **DPI**: 150 DPI for screen viewing; higher DPI available if needed
- **Fonts**: System fonts (no embedded fonts) for maximum compatibility
- **Accessibility**: All figures meet WCAG 2.1 AA color contrast standards
- **Scalability**: SVG format ensures perfect scaling at any size

---

**End of Visualization Generation Guide**
