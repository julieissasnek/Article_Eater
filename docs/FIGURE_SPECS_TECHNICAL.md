# ATLAS Visualization Technical Specifications

**Created**: 2026-03-02  
**Version**: 1.0  
**Last Updated**: 2026-03-02

## Index

1. [M-19: The Nightly Pipeline](#m-19-the-nightly-pipeline)
2. [M-20: The Recommendation Loop](#m-20-the-recommendation-loop)
3. [M-21: AESHI Score](#m-21-aeshi-score)
4. [M-22: Evidence Landscape](#m-22-evidence-landscape)
5. [M-23: Warrant Distribution](#m-23-warrant-distribution)
6. [M-24: Schema Gaps](#m-24-schema-gaps)

---

## M-19: The Nightly Pipeline

**File**: `m19_nightly_pipeline.svg` (135 KB)  
**Script**: `generate_operations_figures.py` → `generate_m19_nightly_pipeline()`  
**Purpose**: Visualize all 13 stages of nightly evidence maintenance pipeline

### Data Structure

```python
stages = [
    {'num': 1, 'name': 'DOI Duplicate\nCheck', 'duration': '2 min', 'color': 'slate_blue'},
    {'num': 2, 'name': 'Triage Queue\nScan', 'duration': '1 min', 'color': 'slate_blue'},
    # ... (13 total stages)
]

failure_modes = {
    1: 'Duplicate not detected',
    2: 'Articles missed',
    # ... (one per stage)
}
```

### Design Elements

- **Layout**: 2 rows × 7 columns (S1–S7 in row 1, S8–S13 in row 2)
- **Stage Boxes**: FancyBboxPatch with rounded corners
  - Width: 0.9 units
  - Height: 1.0 units
  - Spacing: 1.1 units
  - Border: PALETTE['deep_navy'], linewidth 1.5
- **Colors by Function**:
  - Data Flow (blue): S1, S2, S4, S7, S10
  - Quality Checks (green): S5, S8, S13
  - Computation (gold): S3, S6, S9, S11, S12
- **OVERSEER Bar**: Top of figure, terracotta border, cream background
- **Arrows**: FancyArrowPatch connecting consecutive stages
- **Annotations**: Failure modes displayed above/below boxes

### Metrics

| Metric | Value |
|--------|-------|
| Total runtime | ~54 minutes |
| Optimal max | 60 minutes |
| Num stages | 13 |
| Figure size | 16 × 10 inches |
| DPI | 150 |

---

## M-20: The Recommendation Loop

**File**: `m20_recommendation_loop.svg` (108 KB)  
**Script**: `generate_operations_figures.py` → `generate_m20_recommendation_loop()`  
**Purpose**: Show cyclical gap detection → evidence discovery process

### Data Structure

```python
stages = [
    {'name': 'Gap\nDetection', 'metric': 'VOI > 0.0', 'script': 'detect_gaps.py'},
    {'name': 'VOI\nScoring', 'metric': 'VOI Score', 'script': 'score_gaps.py'},
    # ... (8 total stages)
]
```

### Design Elements

- **Topology**: Polar coordinate system with Cartesian overlay
- **Stage Boxes**: 8 boxes arranged in circle, radius 4.5 units
- **Colors**: All slate_blue (PALETTE['slate_blue'])
- **Arrows**: Curved arrows (arc3,rad=0.3) connecting stages
- **Central Circle**: 
  - Radius: 2.5 units
  - Color: PALETTE['cream'] with deep_navy border
  - Steady-state annotation: "~15-20 Articles/Day\n~50 New Beliefs/Day"
- **Script Labels**: Between stages, in rounded boxes
- **Metrics**: Quality thresholds shown on stage boxes

### Steady-State Assumptions

- Articles discovered/day: 15–20
- New beliefs integrated/day: ~50
- Loop frequency: Continuous (gap detection ↔ evidence discovery)

---

## M-21: AESHI Score

**File**: `m21_aeshi_score.svg` (71 KB)  
**Script**: `generate_operations_figures.py` → `generate_m21_aeshi_score()`  
**Purpose**: Display system health index as weighted subscores

### Data Structure

```python
subscores = [
    ('Extraction Quality', 0.20, 3.5),
    ('Tagging Accuracy', 0.15, 3.5),
    ('Evidence Coverage', 0.20, 6.0),
    ('Coherence Level', 0.20, 7.0),
    ('Pipeline Reliability', 0.15, 5.0),
    ('Calibration Accuracy', 0.10, 6.2),
]
```

### Design Elements

- **Layout**: Horizontal stacked bars
- **Score Range**: 0–10 per subscore
- **Colors by Performance**:
  - Red (terracotta): score < 4.0
  - Yellow (warm_gold): 4.0–6.0
  - Green (sage_green): > 6.0
- **Weighted Calculation**:
  ```
  AESHI = Σ(w_i × s_i) / Σ(w_i)
         = (0.20×3.5 + 0.15×3.5 + 0.20×6.0 + ... ) / 1.0
         ≈ 5.1/10
  ```
- **Target Line**: Dashed green line at 7.5
- **Legend**: Score ranges (< 4.0, 4–6, > 6)

### Metrics

| Subscale | Weight | Current | Status |
|----------|--------|---------|--------|
| Extraction Quality | 0.20 | 3.5 | Low |
| Tagging Accuracy | 0.15 | 3.5 | Low |
| Evidence Coverage | 0.20 | 6.0 | Medium |
| Coherence Level | 0.20 | 7.0 | High |
| Pipeline Reliability | 0.15 | 5.0 | Medium |
| Calibration Accuracy | 0.10 | 6.2 | Medium |
| **AESHI Total** | **1.00** | **5.1** | **Below Target** |

---

## M-22: Evidence Landscape

**File**: `m22_evidence_landscape.svg` (89 KB)  
**Script**: `generate_dashboard_figures.py` → `generate_m22_evidence_landscape()`  
**Purpose**: Show belief distribution across T1 frameworks

### Data Structure

```python
frameworks = [
    ('Predictive\nProcessing', 800),     # 23.4% of 3,420
    ('Allostasis', 500),                 # 14.6%
    ('Environmental\nPsychology', 450),  # 13.2%
    ('Neuroaesthetics', 350),            # 10.2%
    ('Proxemics', 300),                  # 8.8%
    ('Chronobiology', 250),              # 7.3%
    ('Adaptive\nComfort', 200),          # 5.8%
    ('Flow\nTheory', 180),               # 5.3%
    ('Cognitive\nMap', 170),             # 5.0%
    ('Multisensory\nIntegration', 120),  # 3.5%
]
# Total: 3,420 beliefs
```

### Design Elements

- **Chart Type**: Horizontal stacked bar chart
- **Color Scheme**:
  - > 700 beliefs: sage_green (high)
  - 400–700 beliefs: warm_gold (medium-high)
  - 200–400 beliefs: slate_blue (medium)
  - < 200 beliefs: cool_gray (low)
- **Labels**: Framework name (left), percentage (inside bar), belief count (right)
- **Legend**: Confidence distribution within frameworks
  - High (>0.7): sage_green
  - Medium (0.5–0.7): warm_gold
  - Low (<0.5): terracotta
- **Title**: Points out Predictive Processing dominance

### Confidence Assumptions

- High confidence: 50% of beliefs per framework
- Medium confidence: 35% of beliefs per framework
- Low confidence: 15% of beliefs per framework

---

## M-23: Warrant Distribution

**File**: `m23_warrant_distribution.svg` (89 KB)  
**Script**: `generate_dashboard_figures.py` → `generate_m23_warrant_distribution()`  
**Purpose**: Show warrant type composition across 12 domain panels

### Data Structure

```python
domains = [
    'Visual', 'Acoustic', 'Thermal', 'Light', 'Stress', 'Social',
    'Memory', 'Multimodal', 'Creative', 'NEUROMOD-I', 'CROSSCUT-I', 'Ambient',
]

warrant_types = [
    ('EMPIRICAL_ASSOC', 0.40, sage_green),
    ('MECHANISM', 0.30, warm_gold),
    ('THEORY_DERIVED', 0.20, terracotta),
    ('ANALOGICAL', 0.10, cool_gray),
]

belief_counts = [280, 295, 270, 265, 290, 310, 275, 260, 245, 310, 320, 290]
# Total: 3,420 beliefs across 12 domains
```

### Design Elements

- **Chart Type**: Stacked bar chart (100% composition)
- **X-axis**: 12 domain panels
- **Y-axis**: Number of beliefs (0–~110 per segment)
- **Segment Colors**:
  - EMPIRICAL_ASSOC: sage_green
  - MECHANISM: warm_gold
  - THEORY_DERIVED: terracotta
  - ANALOGICAL: cool_gray
- **Labels**: Percentage on each segment (if visible)
- **Reference Line**: System average at ~40% empirical across all domains
- **Variation**: ±2% random variation per domain for realism

### System Composition

| Warrant Type | % | Interpretation |
|--------------|---|-----------------|
| Empirical Association | 40% | Direct evidence from research |
| Mechanism | 30% | Theory about causal pathways |
| Theory-Derived | 20% | Predictions from frameworks |
| Analogical | 10% | Inferences from similar domains |

---

## M-24: Schema Gaps

**File**: `m24_schema_gaps.svg` (129 KB)  
**Script**: `generate_dashboard_figures.py` → `generate_m24_schema_gaps()`  
**Purpose**: Identify epistemic gaps by domain and category

### Data Structure

```python
domains = [
    'Visual', 'Acoustic', 'Thermal', 'Light', 'Stress', 'Social',
    'Memory', 'Multimodal', 'Creative', 'NEUROMOD-I', 'CROSSCUT-I', 'Ambient',
]

gap_categories = [
    'Mediation\nGaps', 'Mechanism\nGaps', 'Boundary\nGaps',
    'Direction\nGaps', 'Validation\nGaps',
]

# gap_data: 12 × 5 matrix
# Realistic values: 2–15 per cell (except hotspots)
# NEUROMOD-I (row 9): [18, 15, 20, 14, 16] → High gaps by design
# CROSSCUT-I (row 10): [16, 19, 18, 17, 15] → High gaps by design
```

### Design Elements

- **Chart Type**: Heatmap (imshow with 'Reds' colormap)
- **Dimensions**: 12 domains × 5 epistemic categories
- **Color Scale**: White (0 gaps) → Deep Red (many gaps)
- **Cell Annotations**: Gap count (numeric label)
- **Hotspot Markers**: ★ symbol on cells with >15 gaps
- **Summary Row**: Total gaps per category (displayed below)
- **Hotspot Text Box**: Explains why NEUROMOD-I and CROSSCUT-I have high gaps

### Gap Categories

| Category | Description |
|----------|-------------|
| Mediation Gaps | Indirect pathways not fully specified |
| Mechanism Gaps | Causal mechanisms unclear |
| Boundary Gaps | Scope and applicability uncertain |
| Direction Gaps | Bidirectional or feedback effects unclear |
| Validation Gaps | Insufficient empirical support |

### Known Hotspots

- **NEUROMOD-I**: Intentionally high gaps (complex neuromodulation domain)
  - Highest: Boundary & Mediation gaps (requires cross-domain synthesis)
- **CROSSCUT-I**: Intentionally high gaps (spans multiple domains)
  - Highest: Mechanism & Direction gaps (bidirectional effects complex)

---

## Implementation Notes

### SVG Output Settings

All scripts use consistent SVG generation settings:

```python
plt.savefig(output_path, 
            format='svg', 
            facecolor=PALETTE['cream'],
            edgecolor='none',
            bbox_inches='tight',
            dpi=150)
```

### Color Palette Definition

```python
PALETTE = {
    'deep_navy': '#1B2A4A',      # RGB(27, 42, 74)
    'slate_blue': '#2E5090',     # RGB(46, 80, 144)
    'warm_gold': '#D4A843',      # RGB(212, 168, 67)
    'sage_green': '#5B8C5A',     # RGB(91, 140, 90)
    'terracotta': '#C17B4A',     # RGB(193, 123, 74)
    'cool_gray': '#8B9DAF',      # RGB(139, 157, 175)
    'cream': '#F5F0E8',          # RGB(245, 240, 232)
}
```

### Reproducibility

- Fixed random seed: `np.random.seed(42)`
- Deterministic data generation
- No external data dependencies
- All data embedded in scripts

---

## File Format & Compatibility

### SVG Specifications

- **Format**: Scalable Vector Graphics (SVG 1.1)
- **Size**: 71–135 KB per figure
- **DPI**: 150 (for screen viewing)
- **Fonts**: System fonts (no embedded fonts)
- **Compatibility**: All modern browsers, vector editors, PDF converters

### Export Options

From SVG, can generate:

```bash
# Convert to PDF (using ImageMagick or Inkscape)
convert m19_nightly_pipeline.svg m19_nightly_pipeline.pdf

# Convert to PNG (300 DPI)
convert -density 300 m19_nightly_pipeline.svg m19_nightly_pipeline.png

# Convert to PDF (using Inkscape)
inkscape m19_nightly_pipeline.svg -A m19_nightly_pipeline.pdf
```

---

## Maintenance & Updates

### When to Update Figures

1. **Pipeline Changes**: If stages are added/removed, update M-19 data structure
2. **AESHI Targets**: If thresholds change, update subscores in M-21
3. **Belief Distribution**: If frameworks or belief counts change, update M-22
4. **Warrant Composition**: If warrant type percentages shift, update M-23
5. **Gap Status**: If schema gaps are resolved, update gap counts in M-24

### Update Process

1. Edit relevant script (data structure only)
2. Run regeneration command
3. Verify SVG in browser
4. Update VISUALIZATION_GENERATION_GUIDE.md if needed
5. Commit changes to version control

---

**End of Technical Specifications**
