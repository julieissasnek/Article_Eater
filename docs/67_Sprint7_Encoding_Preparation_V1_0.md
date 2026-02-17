# DOCUMENT 67: SPRINT 7 ENCODING PREPARATION
## Deduplication Map, Machine-Readable Format, Common Effect Metric, and Accessibility Tiers
## February 17, 2026

---

## Purpose

Doc 66 (Comprehensive Audit) identified structural prerequisites that must be resolved before Claude Code begins Sprint 7 template encoding. This document resolves them. It is the ENCODING BIBLE — Claude Code should read this before touching a template.

---

## PART 1: DEDUPLICATION MAP

### The Problem

The system has two template generations:
- **Generation 1 (T-series, M-series, AX-series)**: 75 templates from Panels I–V and Music/Auxiliary panels. Rich narrative, qualitative mechanisms, minimal quantitative calibration.
- **Generation 2 (Domain series)**: 34 templates (L1–L5, MAT1–MAT5, TP1–TP4, SOC1–SOC3, CREA1–CREA4, VIEW1, SC1–SC4, COL1–COL2, VF1–VF3, OLF1) from domain panels + calibration panels. Quantitative parameters, YAML structure, calibrated.

Many Gen-2 templates SUPERSEDE Gen-1 templates. Some Gen-1 templates have NO Gen-2 equivalent. Encoding both generations without deduplication will cause double-counting.

### Classification

Every Gen-1 template falls into one of four categories:

**Category S (Superseded)**: A Gen-2 template fully captures this mechanism. Deprecate — do NOT encode the Gen-1 version. Reference the Gen-2 template instead.

**Category P (Partially Captured)**: A Gen-2 template covers PART of this mechanism. Encode only the RESIDUAL — the part not captured by Gen-2.

**Category G (Gap)**: No Gen-2 equivalent exists. This template describes a mechanism the calibrated system CANNOT assess. Encode as-is from Gen-1 source, flag for future calibration.

**Category R (Reference)**: This template describes a general principle or constraint (e.g., working memory capacity) that other templates reference. Encode as a CONSTRAINT template, not a standalone assessment.

### T-Series Deduplication (T1–T52)

| T# | Name | Category | Gen-2 Equivalent | Action |
|----|------|----------|-------------------|--------|
| T1 | Spectral/Fractal Match (1/f) | P | VF1 (contour), VF2 (SCI scaling) | Residual: 1/f TEMPORAL spectral matching (auditory). VF covers spatial. Encode auditory 1/f only. |
| T2 | Prospect-Refuge | P | SC2 (isovist), VF3 (ceiling/enclosure) | Residual: the REFUGE component specifically — enclosed safety niche. SC2 handles prospect (vista). Encode refuge parameterization. |
| T3 | Biophilic Fractal Fluency | S | VF1 (CCI), VF2 (SCI), T1 residual | Fully covered by VF visual form + T1 auditory residual. Deprecate. |
| T4 | Attentional Demand/Restoration | G | None | **GAP.** General attention demand is not in any Gen-2 template. CREA handles creative attention only. Encode from Gen-1. Flag for ATTENTION-I panel. |
| T5 | Enclosure Threat Detection | P | VF3 (R_h ceiling), SOC2 (privacy) | Residual: the THREAT pathway — amygdala-mediated response to spatial confinement independent of ceiling height. VF3 handles the cognitive-mode shift; T5 residual is the visceral threat signal at extreme confinement. |
| T6 | Cortisol-Hippocampal Cascade | G | None | **GAP.** Chronic stress → cortisol → hippocampal volume → memory impairment. Critical mechanism for healthcare, eldercare, workplace. No Gen-2 equivalent. Encode from Gen-1. Flag for STRESS-I panel. |
| T7 | Allostatic Anticipation | G | None | **GAP.** Anticipatory stress responses to environmental unpredictability. No Gen-2 equivalent. Encode from Gen-1. |
| T8 | Place Cell / Grid Cell Spatial Model | P | SC1 (legibility), SC4 (wayfinding) | Residual: the NEURAL mechanism (place/grid cell spatial mapping). SC templates handle behavioral wayfinding outcomes. Encode neural constraint. |
| T9 | Boundary/Landmark Anchoring | S | SC4 (wayfinding calibrated) | Fully captured by SC4's wayfinding model. Deprecate. |
| T10 | Sleep Consolidation & Restoration | G | None | **GAP.** Sleep-dependent memory consolidation as affected by bedroom environment. VIEW1 handles daytime restoration but NOT sleep architecture. Encode from Gen-1. |
| T11 | Noradrenergic Exploration | P | TP3 (novelty temporal), CREA2 (disfluency) | Residual: the LC-NE arousal → exploration mode shift as a general mechanism. TP3 and CREA2 handle specific application contexts. Encode as general arousal-exploration constraint. |
| T12 | Predictive Coding Hierarchy | R | Referenced by all PE templates | **REFERENCE.** The general PE computational framework. Not a standalone assessment template. Encode as theoretical constraint document. |
| T13 | Nature View Multi-Path | S | VIEW1 (fully calibrated with VQI) | Fully superseded. Deprecate. |
| T14 | Navigation-Stress Vicious Cycle | G | None | **GAP.** Wayfinding failure → stress → cognitive impairment → worse wayfinding. SC4 handles wayfinding but NOT the stress cascade loop. Encode from Gen-1. |
| T15 | Environmental Mastery / Control | P | SOC templates (partial) | Residual: personal CONTROL over environment (thermostat, blinds, furniture) as independent predictor of satisfaction. SOC handles social territory but not individual environmental control. |
| T16 | Restoration Time-Course | P | VIEW1 (restoration channel), CREA3 (incubation) | Residual: the GENERAL restoration time-course (fast Pathway A: 5 min; slow Pathway B: 20-40 min) independent of nature view or walking. Encode as general restoration dynamics. |
| T17 | Dopaminergic Novelty Reward | G | None | **GAP.** Environmental novelty → DA release → approach behavior → reward learning. Critical for understanding why novel architecture initially attracts (and why the effect wanes). No Gen-2 equivalent. Encode from Gen-1. Flag for REWARD-I panel. |
| T18 | Vestibular-Spatial Cognition | G | None | **GAP.** Vestibular input from level changes, ramps, stairs → spatial orientation and embodied cognition. No Gen-2 equivalent. |
| T19 | Social Affordance Density | S | SOC1, SOC2, SOC3 (fully calibrated) | Fully superseded. Deprecate. |
| T20 | Environment-Cognitive Performance | P | CREA1-4 (creativity), T4 (attention gap) | Residual: CONVERGENT cognitive performance (analytical work, sustained attention) as modulated by environment. CREA covers divergent. T4 covers attentional demand. T20 residual is the analytical performance model. |
| T21 | Active Inference General | R | Referenced by PE templates | **REFERENCE.** General active inference framework. Encode as theoretical constraint. |
| T22 | Rapid Gist (LSF) | P | VF1 (contour PE onset ~84ms) | Residual: the LSF magnocellular pathway (~130ms) for SCENE CATEGORIZATION specifically. VF1 handles contour processing. T22 adds scene-level gist. |
| T23 | Context-Dependent Memory | G | None | **GAP.** Environmental context reinstated at retrieval → 20–40% recall advantage. Critical for learning environments. No Gen-2 equivalent. Encode from Gen-1. Flag for MEMORY-I panel. |
| T24 | Theta Sequence / Spatial Navigation | P | SC4 (wayfinding) | Residual: hippocampal theta oscillation as neural mechanism. SC4 handles behavioral outcomes. Encode as neural constraint. |
| T25 | Soft Fascination | S | VIEW1 Channel 3 (soft fascination weighted) | Fully captured. Deprecate. |
| T26 | Cholinergic Gating | R | Referenced by attention templates | **REFERENCE.** ACh-mediated attention gating mechanism. Encode as neural constraint. |
| T27 | Interoceptive Inference | P | MAT1 (thermal), MAT2 (contact) | Residual: general interoceptive PE framework beyond thermal. Hunger, fatigue, air quality as interoceptive signals. Encode non-thermal interoception. |
| T28 | Cognitive Offloading | G | None (referenced by CREA4 but not standalone) | **GAP.** Externalization of WM to environment (notes, displays, spatial arrangements). Referenced in CREA4 but deserves standalone treatment for general workspace design. Encode from Gen-1. |
| T29 | Multi-Channel Summation | R | Used by L3, MAT4, VIEW1 convergence models | **REFERENCE.** The general principle of multi-sensory channel summation. Challenged by Altomonte's multiplicative interaction finding. Encode as computational constraint with additive/multiplicative flag. |
| T30 | Precision Weighting | R | Referenced by PE templates | **REFERENCE.** Precision (inverse variance) modulates PE magnitude. Encode as computational constraint. |
| T31 | Thermoregulatory Affect | S | MAT1 (thermal adaptive PE, fully calibrated) | Fully superseded. Deprecate. |
| T32 | Subcortical Auditory Encoding | P | M-series, acoustic domain | Partially captured by acoustic standards. Residual: the specific subcortical (inferior colliculus → auditory cortex) encoding pathway. Encode SNR and RT60 parameters. |
| T33 | Reverberation-Space Perception | P | SC templates (spatial) | Residual: acoustic estimation of room volume. RT60 correlation with perceived spaciousness. Encode as acoustic-spatial cross-modal template. |
| T34 | Haptic Surface Material | S | MAT2 (CT-afferent calibrated) | Fully superseded. Deprecate. |
| T35 | Olfactory Context-Affect | S | OLF1 + MAT4 olfactory channel | Fully superseded. Deprecate. |
| T36 | Working Memory Load | R | Referenced by CREA4, T28, T38 | **REFERENCE.** WM capacity 3–4 items as environmental design constraint. Encode as constraint (not assessment). |
| T37 | Ecological Rationality | R | Referenced by multiple templates | **REFERENCE.** Bounded rationality in environmental decision-making. Encode as theoretical constraint. |
| T38 | Hierarchical Control (PFC) | P | CREA1 (DMN-ECN-SN) | Residual: nesting depth limit ~3–4 levels for task hierarchy. CREA1 handles network dynamics but not hierarchical depth constraint. Encode depth constraint. |
| T39 | MSI Congruency Principle | S | MAT3 (cross-modal congruence, calibrated) | Fully superseded. Deprecate. |
| T40 | MSI Inverse Effectiveness | P | MAT3 (congruence protocol) | Residual: the principle that multisensory enhancement is GREATEST when unisensory signals are weak. MAT3 handles congruence but not inverse effectiveness specifically. Encode the principle. |
| T41–T47 | Panel IV templates | P/G | Various | These need individual assessment. Many overlap with calibrated templates. Defer to a separate audit. |
| T48–T52 | Panel V Social Brain | P/S | SOC1-3 | Mostly superseded by SOC calibration. Some residual TPJ/mentalizing mechanisms. |

### Summary Counts

| Category | Count | Action |
|----------|-------|--------|
| **S (Superseded)** | ~14 | Deprecate. Reference Gen-2 equivalent. |
| **P (Partial)** | ~18 | Encode RESIDUAL only. Link to Gen-2 equivalent. |
| **G (Gap)** | ~10 | Encode from Gen-1. Flag for future calibration panels. |
| **R (Reference)** | ~8 | Encode as constraints/principles, not standalone assessments. |
| **T41–T52 (Deferred)** | ~12 | Individual assessment needed for Panels IV–V templates. |

### Critical Gaps Identified

These Gen-1 templates describe mechanisms the calibrated system CANNOT assess:

| Gap | Templates | Mechanism | Priority | Recommended Panel |
|-----|-----------|-----------|----------|-------------------|
| **Attention** | T4, T20-residual | General attentional demand & analytical performance | HIGH | ATTENTION-I |
| **Stress** | T6, T7, T14 | Cortisol cascade, allostatic load, nav-stress loop | HIGH | STRESS-I |
| **Reward** | T17 | Novelty → dopamine → approach → habituation | MEDIUM | REWARD-I |
| **Memory** | T10, T23 | Sleep consolidation, context-dependent recall | MEDIUM | MEMORY-I |
| **Control** | T15, T28 | Environmental mastery, cognitive offloading | MEDIUM | CONTROL-I |
| **Vestibular** | T18 | Level changes, embodied spatial cognition | LOW | — |

---

## PART 2: MACHINE-READABLE TEMPLATE FORMAT

### Design Principles

1. **One format, two representations.** Each template exists as (a) a narrative Markdown document (for humans) and (b) a structured JSON file (for software). The JSON is the ENCODING; the Markdown is the DOCUMENTATION.
2. **Computable core, narrative periphery.** The JSON captures everything needed for computation. Debate records, nuanced scope conditions, and historical context remain in Markdown only.
3. **Flat where possible, nested where necessary.** Avoid deep nesting. Most fields are top-level key-value pairs.

### Template JSON Schema

```json
{
  "$schema": "article_eater_template_v1",
  "template_id": "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001",
  "display_id": "CREA4",
  "generation": 2,
  "name": "Collaborative Creativity Architecture",
  "series": "CREA",
  "source_docs": [55, 58, 65],
  
  "pe_contribution": "explanatory",
  
  "maturity": "supported-preliminary",
  "calibration_status": "partial",
  "ecological_validation": false,
  
  "practical_accessibility": "B",
  
  "parameters": [
    {
      "name": "alternation_cycle_individual_min",
      "value": [8, 15],
      "unit": "minutes",
      "type": "range",
      "confidence": "supported",
      "source": "Doc 65, Paulus & Brown 2007"
    },
    {
      "name": "alternation_cycle_group_min",
      "value": [5, 10],
      "unit": "minutes",
      "type": "range",
      "confidence": "supported",
      "source": "Doc 65, Paulus & Brown 2007"
    },
    {
      "name": "optimal_group_size",
      "value": [3, 6],
      "unit": "persons",
      "type": "range",
      "confidence": "supported",
      "source": "Doc 65, Dunbar/Paulus consensus"
    },
    {
      "name": "display_density_threshold",
      "value": 1.5,
      "unit": "m2_writable_per_person",
      "type": "minimum",
      "confidence": "preliminary",
      "source": "Doc 65, Cho 2021"
    },
    {
      "name": "transition_time_max",
      "value": 30,
      "unit": "seconds",
      "type": "maximum",
      "confidence": "expert_estimate",
      "source": "Doc 65, panel consensus"
    },
    {
      "name": "psychological_safety_multiplier",
      "value": "d_arch = d_max * safety_baseline",
      "type": "formula",
      "input_required": "organizational_safety_baseline (0-1)",
      "confidence": "preliminary",
      "source": "Doc 65, Amabile 1996"
    }
  ],
  
  "inputs_required": [
    {
      "name": "room_area_m2",
      "type": "numeric",
      "accessibility": "A",
      "measurement": "floor plan"
    },
    {
      "name": "writable_surface_m2",
      "type": "numeric",
      "accessibility": "A",
      "measurement": "direct measurement"
    },
    {
      "name": "transition_distance_m",
      "type": "numeric",
      "accessibility": "A",
      "measurement": "floor plan"
    },
    {
      "name": "organizational_safety_baseline",
      "type": "numeric_0_1",
      "accessibility": "C",
      "measurement": "Edmondson Psychological Safety Scale"
    }
  ],
  
  "outputs": [
    {
      "name": "production_blocking_reduction",
      "type": "percentage",
      "range": [40, 60],
      "unit": "percent_vs_continuous_group",
      "metric_class": "relative_improvement"
    },
    {
      "name": "collaborative_creativity_effect",
      "type": "cohens_d",
      "range": [0.20, 0.40],
      "condition": "safety_baseline > 0.3",
      "metric_class": "effect_size"
    }
  ],
  
  "interactions": [
    {"template": "CREA1", "nature": "wraps", "note": "CREA4 Phase 1 IS CREA1 Phase 1"},
    {"template": "CREA3", "nature": "wraps", "note": "CREA4 Phase 3 IS CREA3 micro-incubation"},
    {"template": "SOC3", "nature": "maps_to", "note": "4-6 person cluster = Dunbar sympathy group"},
    {"template": "SOC2", "nature": "requires", "note": "Privacy gradient individual→group→transition"}
  ],
  
  "deduplication": {
    "supersedes": [],
    "superseded_by": [],
    "overlaps_with": ["T19", "T28"],
    "overlap_resolution": "T19 fully superseded by SOC series; T28 residual (general offloading) should be encoded separately"
  },
  
  "scope_conditions": [
    "collaborative knowledge work (not solo artistic production)",
    "group size 3-6 (sub-group for 7-20)",
    "organizational safety_baseline > 0.3 for meaningful effect",
    "cycle timing assumes knowledge work (not physical fabrication)"
  ],

  "lifespan_moderation": {
    "aging": {"source": "Doc 60", "key_modifier": "WM decline amplifies offloading benefit"},
    "developmental": {"source": "Doc 61", "key_modifier": "shorter individual phases for children"}
  },

  "cultural_moderation": {
    "present": true,
    "note": "Psychological safety norms vary by national culture; hierarchy distance affects spatial equality requirements"
  }
}
```

### Encoding Priority Order

Claude Code should encode templates in this order:

**Batch 1: High-value Gen-2 templates with complete calibration (12 templates)**
L1, L2, L3, MAT1, MAT2, MAT4, SOC2, SC1, SC4, VIEW1, VF3, CREA2

Rationale: These have the most complete parameter sets and the highest practical utility. They form the core of a working assessment system.

**Batch 2: Remaining Gen-2 templates (22 templates)**
L4, L5, MAT3, MAT5, TP1-4, SOC1, SOC3, CREA1, CREA3, CREA4, SC2, SC3, COL1, COL2, VF1, VF2, OLF1

**Batch 3: Gen-1 Gap templates (10 templates)**
T4, T6, T7, T10, T14, T15, T17, T18, T23, T28

**Batch 4: Gen-1 Residual templates (~18 templates)**
Partial-capture residuals from T-series. Encode only the residual mechanism.

**Batch 5: Gen-1 Reference/Constraint templates (~8 templates)**
T12, T21, T26, T29, T30, T36, T37 — encode as computational constraints.

**Batch 6: Deprecated Gen-1 templates (~14 templates)**
T3, T9, T13, T19, T25, T31, T34, T35, T39, etc. — create deprecation records pointing to Gen-2 equivalents. Do NOT encode as active templates.

---

## PART 3: COMMON EFFECT METRIC

### The Problem

Templates produce heterogeneous outputs:
- Cohen's d effect sizes (VF1, CREA2, CREA3)
- Quality indices on custom scales (VIEW1 VQI: 0–100)
- Categorical Goldilocks zones (L1 luminance CV, MAT1 thermal)
- Thresholds (L2 CS ≥ 0.3)
- Relative improvements (CREA4 production blocking: 40–60%)
- Ordinal ratings (coverage ★ ratings)

These cannot be combined without a linking function.

### Solution: The Wellbeing Impact Score (WIS)

Define a common currency: **Wellbeing Impact Score (WIS)**, scaled 0–100, where:

| WIS | Meaning |
|-----|---------|
| 0–20 | Actively harmful / severe deficit |
| 20–40 | Below threshold / deficit |
| 40–60 | Adequate / neutral |
| 60–80 | Good / positive contribution |
| 80–100 | Excellent / optimal |

**Conversion rules by output type:**

**Cohen's d → WIS:** Use the cumulative normal distribution. d = 0 → WIS 50 (neutral); d = 0.5 → WIS 69; d = 0.8 → WIS 79; d = −0.5 → WIS 31.
Formula: WIS = Φ(d/√2) × 100, where Φ is the standard normal CDF.
This places "no effect" at 50 and maps effect sizes to percentile-equivalents.

**Goldilocks zones → WIS:**
- Extreme aversive zone → WIS 10–20
- Outside Goldilocks, not extreme → WIS 25–40
- Goldilocks boundary → WIS 50–60
- Goldilocks center → WIS 75–85
- Optimal point (if known) → WIS 85–90

**Threshold metrics → WIS:**
- Below threshold by >50% → WIS 15–25
- Below threshold by <50% → WIS 30–45
- At threshold → WIS 55
- Above threshold by moderate amount → WIS 65–75
- Well above threshold → WIS 80–85

**Quality indices → WIS:** Direct linear rescaling if the index is 0–100 (e.g., VQI maps directly). For other scales, define an affine mapping.

### Aggregation Rules

**Within-domain aggregation:** Templates within the same domain (e.g., L1–L5) produce domain-level WIS via WEIGHTED AVERAGE, weights proportional to calibration confidence:
- Established/substantially calibrated: weight 1.0
- Supported/partially calibrated: weight 0.7
- Preliminary/expert estimate: weight 0.4
- Speculative/uncalibrated: weight 0.2

**Cross-domain aggregation:** Domain-level WIS values combine via WEIGHTED GEOMETRIC MEAN (not arithmetic mean). Geometric mean penalizes severe deficits more than arithmetic mean — a building with WIS 90 on light but WIS 15 on acoustics should NOT average to 52.5 (which sounds okay). Geometric mean: √(90 × 15) = 36.7 (which correctly signals a problem).

**Interaction adjustments:** Where interaction matrices exist (CREA2 sub-additivity, convergence triad super-additivity), apply them AFTER individual template WIS computation but BEFORE domain aggregation.

### Maturity of the WIS System

This is a PRELIMINARY DESIGN. The conversion rules (especially Goldilocks → WIS) involve judgment calls that need empirical calibration. The weighting scheme privileges better-calibrated templates, which is defensible but means the aggregate WIS is dominated by a few well-studied templates. The geometric mean for cross-domain aggregation is a principled choice but has not been validated against post-occupancy evaluation data.

**WIS should be presented with uncertainty bands.** A building assessed as WIS 72 ± 12 is more honest than WIS 72.

---

## PART 4: PRACTICAL ACCESSIBILITY TIERS

### Classification

Every template INPUT is classified by how easily an architect can obtain it:

| Tier | Definition | Examples |
|------|-----------|----------|
| **A** (Standard practice) | Measurable with standard architectural tools or derivable from drawings | Floor area, ceiling height, R_h, window area, room dimensions, material identification, illuminance (lux meter), RT60 (acoustic meter or from standards), occupancy count |
| **B** (Specialized measurement) | Requires specialized equipment or trained assessment | Spectral power distribution (spectrometer), CCI/SCI (image processing software), precise dBA levels (sound level meter), surface temperature (IR thermometer), effusivity (material databases) |
| **C** (Research-grade) | Requires psychometric instruments, organizational assessment, or observer-rated protocols | Psychological safety scale (Edmondson), cultural distance measures, perceived restorativeness (PRS), behavioral observation coding, EEG/fMRI |
| **D** (Currently unavailable) | Requires technology or data that does not exist in routine practice | Automated CCI computation from BIM models, real-time PE estimation, dynamic SRV from eye-tracking, place cell firing patterns |

### Template Accessibility Map

| Template | Primary Inputs | Tier | Notes |
|----------|---------------|------|-------|
| **L1** | Illuminance distribution | A/B | Lux meter (A); full luminance mapping (B) |
| **L2** | Melanopic EDI, exposure duration | B | Requires spectral measurement or modeled from fixture data |
| **L3** | Daylight factor, window area, orientation | A | Standard daylight analysis |
| **L4** | CCT of lighting | A/B | Fixture spec (A); measured (B) |
| **L5** | Rate of light change | B | Requires logging |
| **MAT1** | Operative temperature, running mean | A | Standard HVAC data |
| **MAT2** | Surface material, contact temperature | A/B | Material identification (A); effusivity lookup (B) |
| **MAT3** | Cross-modal material properties | B | Requires multi-modal assessment protocol |
| **MAT4** | Material identification + channel weights | A/B | Identification (A); acoustic measurement (B) |
| **MAT5** | Cultural context of users | C | Cultural assessment required |
| **TP1** | Floor surface properties, stair dimensions | A | From drawings |
| **TP2** | Sequence of spatial transitions | A/B | Plan analysis (A); timing measurement (B) |
| **TP3** | Novelty assessment of design features | C | Expert or occupant rating |
| **TP4** | Temporal layering of environmental change | B/C | Requires observation over time |
| **SOC1** | Seating arrangement, cultural composition | A/C | Layout (A); cultural assessment (C) |
| **SOC2** | Acoustic isolation, visual privacy, density | A/B | Plan + acoustic measurement |
| **SOC3** | Group sizes, proximity relationships | A | From layout |
| **CREA1** | Sensory richness assessment | B/C | Multi-factor assessment |
| **CREA2** | Noise level, ceiling height, illuminance | A/B | Standard measurements |
| **CREA3** | Walking path availability, nature access | A | Plan analysis |
| **CREA4** | Layout + display surfaces + organizational safety | A/C | Physical (A); organizational (C) |
| **VIEW1** | Window properties, view content | A | VQI rubric from plan + site |
| **SC1** | Plan connectivity, visual access | A/B | Graph analysis of plan (A); isovist computation (B) |
| **SC2** | Isovist area sequence | B | Isovist computation software |
| **SC3** | Plan topology, path choice | A/B | Plan analysis |
| **SC4** | Signage, landmarks, decision points | A | Inspection or plan review |
| **COL1** | Surface colors (Munsell or similar) | A | Color specification |
| **COL2** | Color sequence through space | A | Plan + color schedule |
| **VF1** | Contour curvature distribution | B/D | Image processing needed; automated from BIM (D) |
| **VF2** | Element spacing, scaling hierarchy | B/D | SRV/SCI computation from images or models |
| **VF3** | Ceiling height, floor area | A | From drawings |
| **OLF1** | Olfactory sources | B/C | Source identification + concentration measurement |

### Tier Distribution

| Tier | Templates fully at this level | Templates with this as highest-tier input |
|------|-------------------------------|------------------------------------------|
| A | VF3, SC4, CREA3, VIEW1, COL1, COL2, TP1 | ~10 templates fully accessible now |
| A/B | L1, MAT1, MAT2, MAT4, SOC2, SOC3, SC1, CREA2 | ~12 templates with minor specialized input |
| B | L2, L5, TP2, SC2, VF1, VF2 | ~8 templates needing specialized tools |
| B/C | CREA1, TP4, OLF1 | ~4 templates |
| C | MAT5, TP3, SOC1 (cultural), CREA4 (safety) | ~4 templates needing organizational assessment |
| D | VF1 (automated), VF2 (automated) | ~2 templates awaiting technology |

### The Practical Minimum Assessment

An architect with NO specialized equipment can apply approximately **10 templates** using only Tier A inputs: VF3 (ceiling proportions), VIEW1 (view quality), CREA3 (walking paths), SC4 (wayfinding), COL1/COL2 (color), TP1 (floor/stair), MAT1 (thermal from HVAC specs), SOC3 (group sizing), and MAT4 (material identification).

With a lux meter and sound level meter (Tier A/B, ~$200 total), this expands to **~22 templates** — covering light, acoustics, spatial quality, and basic material assessment.

**This is the PRACTICAL CORE of the system** and should be the first thing Claude Code makes operational.

---

## PART 5: REVISED COVERAGE RATINGS

### New Rubric (from Doc 66 Stress Test 5)

| Level | Meaning |
|-------|---------|
| ★ | Domain identified; no templates |
| ★★ | Templates exist, uncalibrated — qualitative only |
| ★★★ | Calibrated with quantitative parameters; expert estimates; Goldilocks boundaries |
| ★★★★ | Calibrated with empirical data; some architectural-context validation |
| ★★★★★ | End-to-end validated in built environments |

### Honest Ratings

| Domain | Previous | Revised | What's Needed for Next Star |
|--------|----------|---------|---------------------------|
| A1 Materials | ★★★★ | ★★★ | Execute MAT3 congruence experiment; validate non-wood profiles empirically |
| A2 Spatial Scale | ★★★★ | ★★★ | Validate R_h predictions psychophysically; test volumetric PE |
| A3 Spatial Config | ★★★★ | ★★★ | Validate SC2 isovist rhythm in real buildings; test SC3 Dunbar distances |
| A4 Light | ★★★★ | ★★★½ | Validate L1 CV boundaries in field; calibrate L5 dynamic parameters |
| A5 Acoustic | ★★★★ | ★★★ | M-series calibration panel; validate beyond existing standards |
| A6 Visual Pattern | ★★★★ | ★★★ | Direct psychophysical validation of SRV/SCI; field-test CCI |
| A7 Haptic/Thermal | ★★★★ | ★★★ | Validate effusivity predictions in architectural surfaces |
| A8 Social | ★★★★ | ★★★½ | Cross-cultural field validation of SOC1-3 parameters |
| A9 Task/Cognition | ★★★★ | ★★★ | Measure remaining CREA2 2×2×2 cells; validate CREA4 cycle |
| A10 Temporal | ★★★★ | ★★★ | Field-validate TP1-4 boundary values |

---

## PART 6: SPRINT 7 TASK BREAKDOWN FOR CLAUDE CODE

### Prerequisites (from this document)

Before encoding begins, Claude Code must:

1. **Read this document.** Especially Part 1 (deduplication) and Part 2 (JSON schema).
2. **Implement the JSON schema** as a Python dataclass or Pydantic model.
3. **Implement the WIS conversion functions** (Part 3) as a utility module.
4. **Set up the accessibility tier metadata** in the template model.

### Encoding Tasks (in Batch order)

**Batch 1 (Core 12)**: Estimated 2–3 sessions.
Encode L1, L2, L3, MAT1, MAT2, MAT4, SOC2, SC1, SC4, VIEW1, VF3, CREA2.
Source: Doc 52 (Registry) for parameter values. Doc 67 (this doc) for JSON structure.
Validate: Each template must round-trip (JSON → computation → WIS output).

**Batch 2 (Remaining Gen-2, 22 templates)**: Estimated 3–4 sessions.
**Batch 3 (Gap templates, 10)**: Estimated 1–2 sessions.
**Batch 4 (Residuals, ~18)**: Estimated 2–3 sessions.
**Batch 5 (Reference/Constraint, ~8)**: Estimated 1 session.
**Batch 6 (Deprecation records, ~14)**: Estimated 0.5 sessions.

**Total estimated encoding: 10–14 sessions for full template base.**

### Validation Protocol

For each batch:
1. Encode templates per JSON schema
2. Run WIS conversion on test inputs
3. Check cross-template consistency (no double-counting per deduplication map)
4. Verify interaction matrices produce correct combined outputs
5. Confirm lifespan moderation (AGE-I + DEV-I) applies correctly

---

*Document 67: Sprint 7 Encoding Preparation — V1.0*
*February 17, 2026*
*Parts: (1) Deduplication Map, (2) JSON Schema, (3) WIS Common Metric, (4) Accessibility Tiers, (5) Revised Coverage Ratings, (6) Sprint 7 Task Breakdown*
*Templates classified: 14 Superseded, 18 Partial, 10 Gap, 8 Reference, 12 Deferred*
*Encoding priority: 6 batches, estimated 10–14 Claude Code sessions*
*Critical finding: 10 templates immediately usable by architects with no specialized equipment*
