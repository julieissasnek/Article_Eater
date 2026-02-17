# ARTICLE EATER — AGENT SPRINT PROMPT V9.0
## Post TP-II Calibration | February 17, 2026

---

## CURRENT STATE

The Article Eater template system now has **72 mechanistic templates** organized across 10 architectural attribute domains. All 10 domains are at ★★★★ coverage. The most recent production was **Doc 56: Panel TP-II Temporal Calibration** (618 lines), which advanced TP1–TP4 from ✗ Uncalibrated to ~ Partially Calibrated.

### Template Inventory (Complete)

**Tier 1 Frameworks**: Predictive Processing (PP), Dual-Task (DT), Scene Grammar (SG), Aesthetic Triad (AT)

**Primary Templates (T1–T52)**: T1 fractal fluency, T2 complexity, T3 cognitive maps, T4 symmetry, T5 curvature, T6 color, T7 biophilia, T8 affordance, T9 material evaluation, T10 attention, T11 wayfinding, T12 interoception, T13 reward, T14–T16 music/rhythm, T17–T22 social brain, T23 context memory, T24–T27 attention/DMN, T28–T30 allostasis/stress, T31–T35 auditory, T36–T40 spatial cognition, T41–T47 cognitive control/reward, T48–T52 extended

**Mechanism Templates (M1–M17)**: Auditory scene, cross-modal, entrainment, etc.

**Auxiliary Templates (AX1–AX6)**: Acoustic comfort, music-architecture, awe, biophilic patterns, multisensory, multi-modal PE

**Domain Templates**:
- **L1–L5**: Light & Luminance (L-II calibrated, Doc 49)
- **MAT1–MAT5**: Materials & Surfaces (MAT-II calibrated, Doc 51)
- **SC1–SC4**: Spatial Configuration (Doc 38)
- **VF1–VF4**: Visual Form (Doc 39, VF3 extended Doc 54)
- **OLF1–OLF2**: Olfactory (Doc 46)
- **SOC1–SOC3**: Social Configuration (Doc 44)
- **VIEW1–VIEW3**: View & Nature (Doc 47)
- **COL1–COL2**: Color (Doc 45, WIP)
- **TP1–TP4**: Temporal Dynamics (Doc 42, calibrated Doc 56)
- **CREA1–CREA3**: Creative Cognition (Doc 55)

### Calibration Status

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial | Doc 49 (L-II) |
| MAT1–MAT5 | ~ Partial | Doc 51 (MAT-II) |
| TP1–TP4 | ~ Partial | Doc 56 (TP-II) |
| CREA1–CREA3 | ✗ Uncalibrated | Awaiting CREA-II |
| SC1–SC4 | ✗ Uncalibrated | Awaiting SC-II |
| SOC1–SOC3 | ✗ Uncalibrated | Awaiting SOC-II |
| All others | ✗ Uncalibrated | Per registry priority |

---

## AGENT ASSIGNMENTS

### CLAUDE CODE — Schema Encoding Sprint

**Priority 1: Encode TP-II Calibration Data (Doc 56)**
- Add Motor Fluency Index (MFI) fields to TP1 schema:
  - `mfi_baseline: number` (DFA α, population-specific)
  - `mfi_range: {condition: string, mfi_low: number, mfi_high: number}[]`
  - `age_moderation: {population: string, baseline_alpha: number, attentional_cost_multiplier: number}[]`
- Add channel-count gradient to TP2 schema:
  - `channel_weights: {channel: string, d_contribution: number, confidence: string}[]`
  - `boundary_strength_function: "additive_with_superadditivity"` 
  - `superadditivity_coefficient: 1.17`
  - `threshold_density_goldilocks: {min: 3, max: 6, per_minutes: 10}`
  - `attentional_boost: {wm_disruption_d: number, encoding_enhancement_d: number}[]`
- Add fractal aging trajectories to TP3 schema:
  - `aging_model: "exponential_approach"`
  - `material_trajectories: {material: string, d_initial: number, d_max: number, tau_years: number, climate_sensitivity: string}[]`
  - `maintenance_regimes: ["managed_positive", "unmanaged", "restorative"]`
  - `spectral_vs_geometric: boolean` (flag for copper/steel where spectral D dominates)
- Add variance decomposition to TP4 schema:
  - `timescale_variance: {timescale: string, unique_r2: number, confidence: string}[]`
  - `pe_density_time_function: {k: 0.35, baseline_events_per_min: 0.4}`

**Priority 2: Encode CREA1–CREA3 (Doc 55)**
- Three-zone model metadata: `creative_zone: "generative" | "evaluative" | "transitional"`
- Phase affinity tagging: `creative_phase_affinity: "generative" | "evaluative" | "incubation" | "phase_neutral"`
- Convergent tradeoff flag: `convergent_tradeoff: boolean`
- CREA2 three-pathway structure: `pathway: "disfluency" | "spaciousness" | "resource_reallocation"`
- CREA3 incubation parameters: `walking_effect_d: 0.8`, `soft_fascination_bonus: 0.15-0.20`, `optimal_break_minutes: {min: 5, max: 20}`

**Priority 3: Cross-template metadata fields** (from Doc 52 V1.3)
- All movement templates: add `mfi_range` field
- All threshold templates: add `threshold_channel_count` and `estimated_boundary_d`
- All material templates: add `aging_trajectory` structure
- All path-based templates: add `pe_density_index`

### CODEX — Task Board and Validation

**Sprint 1**: Update task board with Docs 55 and 56. Mark TP-II as complete. Mark CREA-I as complete.

**Sprint 2**: Validate schema for new metadata fields:
- `creative_phase_affinity` enum values
- `convergent_tradeoff` boolean
- `mfi_range` numerical ranges (MFI should be 0.0–1.0)
- `aging_trajectory` parameter bounds (D values 1.0–2.0; tau in years > 0)
- `threshold_channel_count` integer 0–7
- `pe_density_index` float ≥ 0

**Sprint 3**: Cross-reference audit — verify that all template interactions listed in Docs 55 and 56 are bidirectionally encoded in the schema (if CREA1 references T27, then T27 should reference CREA1).

### ANTIGRAVITY — Round-Trip Validation

**Sprint 1**: CREA1–CREA3 round-trip. Test that the three-zone architectural model (generative/evaluative/transitional) correctly tags spaces in the test building corpus. Verify that CREA2's three pathways produce independent predictions.

**Sprint 2**: TP1–TP4 calibrated round-trip. Test that the MFI metric produces meaningful differentiation across the test building corpus. Verify that TP2's channel-count gradient produces sensible boundary-strength scores for known thresholds. Test TP3's aging model against at least one known aged building.

**Sprint 3**: Cross-domain integration test. Select 3 buildings from the corpus and run FULL template evaluation across all 72 templates. Flag any conflicts, impossible parameter combinations, or missing interaction links.

---

## KEY PARAMETERS REFERENCE (Quick-Look for All Agents)

### TP2 Channel Weights (Doc 56)
| Channel | d | 
|---------|---|
| Spatial configuration | 0.25 |
| Luminance/light | 0.20 |
| Acoustic | 0.18 |
| Material surface | 0.15 |
| Thermal | 0.12 |
| Motor demand | 0.10 |
| Olfactory | 0.08 |
Combination: Σ(d_i) × 1.17

### TP1 MFI Ranges (Doc 56)
| Condition | MFI |
|-----------|-----|
| Level corridor | 0.95–1.00 |
| Good staircase | 0.80–0.90 |
| Steep staircase | 0.65–0.80 |
| Irregular surface | 0.60–0.75 |
| Challenging | 0.45–0.65 |

### TP3 Material Aging (Doc 56)
| Material | D_0 | D_max | τ (yr) |
|----------|-----|-------|--------|
| Limestone | 1.05 | 1.40 | 30–60 |
| Brick | 1.08 | 1.30 | 50–100 |
| Hardwood | 1.15 | 1.35 | 15–30 |
| Copper | 1.05 | 1.20 | 10–25 |
| Concrete | 1.05 | 1.15 | 20–40 |

### CREA Key Parameters (Doc 55)
- DMN-ECN coupling: moderate sensory richness optimal
- Noise disfluency: 65–75 dB optimal for divergent
- Spaciousness: R_h 0.35–0.50 + dim 150 lux
- Walking: d ≈ 0.8 divergent; break 5–20 min
- Soft fascination bonus: +15–20%
- **TRADEOFF**: divergent-promoting features impair convergent

---

## PRIORITY QUEUE (from Doc 52 V1.3)

| # | Panel | Status | Next Action |
|---|-------|--------|-------------|
| 1 | SOC-II | Ready | Cultural calibration of SOC1–3; privacy-encounter curve |
| 2 | CREA-II | Ready | Multi-channel interaction (2×2×2 factorial design) |
| 3 | TP-III | Blocked (needs TP-II empirical data) | VR channel-count study, surface fractal measurement |
| 4 | Aging & Architecture | Ready | Cross-cutting age moderators |
| 5 | Child Development | Ready | Developmental moderators |
| 6 | VIEW-II | Ready | Channel weights, synthetic nature |

---

## DOCUMENT INVENTORY (Current as of Feb 17, 2026)

| Doc | Title | Lines | Version |
|-----|-------|-------|---------|
| 14 | Panel IV: Cognitive Control & Reward | ~1,100 | V1.0 |
| 20 | Panel V: Social Brain | ~900 | V1.0 |
| 21 | ART Reduction | ~200 | V1.0 |
| 33 | Dual-Index Cross-Reference Layer | ~870 | V1.0 |
| 34 | Panel L-I: Light & Luminance | ~900 | V1.1 |
| 38 | Panel SC-I: Spatial Configuration | ~1,000 | V1.0 |
| 39 | Panel VF-I: Visual Form | ~900 | V1.0 |
| 42 | Panel TP-I: Temporal Dynamics | ~1,239 | V1.1 |
| 44 | Panel SOC-I: Social Configuration | ~800 | V1.1 |
| 45 | Panel COL-I: Color (WIP) | ~628 | V1.0 |
| 46 | Panel OLF-I: Olfactory | ~700 | V1.0 |
| 47 | Panel VIEW-I: View & Nature | ~800 | V1.0 |
| 49 | Panel L-II: Light Calibration | ~534 | V1.0 |
| 51 | Panel MAT-II: Materials Calibration | ~710 | V1.0 |
| 52 | Calibration & Extension Registry | ~348 | V1.3 |
| 53 | Transfer Context | ~large | V8.0 |
| 54 | A2 Spatial Scale Extension | ~400 | V1.0 |
| 55 | Panel CREA-I: Creative Cognition | ~1,097 | V1.0 |
| **56** | **Panel TP-II: Temporal Calibration** | **~618** | **V1.0** |

---

*Sprint Prompt V9.0 — Generated February 17, 2026*
*Covers: Doc 55 (CREA-I), Doc 56 (TP-II), Doc 52 V1.3*
