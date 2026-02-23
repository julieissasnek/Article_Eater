# ⚠️ SUPERSEDED — See 52_Calibration_Extension_Registry_V2_1.md for current version

# CALIBRATION & EXTENSION REGISTRY
## Consolidated Record of All Panel Updates, Parameter Values, and Broadening/Deepening Priorities
## February 16, 2026 — Document 52

---

## Purpose

This document provides a single lookup table for encoding calibration data into templates. When Claude Code, Codex, or Antigravity encodes templates, this registry tells them: (a) which templates have been calibrated and what parameter values to attach; (b) which panels have been revised with broadening/deepening prospectus sections; (c) the maturity status of every template; and (d) what each future panel (Level II or III) would accomplish. Every parameter value listed here traces to a specific source document.

---

## PART A: PANEL VERSION HISTORY

### Panels Revised with Broadening/Deepening Framework

| Doc | Panel | Original Version | Revised Version | What Changed |
|-----|-------|-----------------|-----------------|-------------|
| 34 | L-I: Light & Luminance | V1.0 (1378 lines) | **V1.1** (1413 lines) | L-II Prospectus restructured into DEEPENING (4 priorities) + BROADENING (2 priorities). 4 new references added (Cuttle, Turner & Mainster, Wilkins ×2). |
| 42 | TP-I: Temporal Dynamics | V1.0 (1174 lines) | **V1.1** (1236 lines) | TP-II Prospectus restructured: DEEPENING (4 priorities: doorway gradient, fractal tracking, motor PE instrumentation, multi-timescale measurement) + BROADENING (3 priorities: circadian design, aging, responsive environments). |
| 44 | SOC-I: Social Configuration | V1.0 (970 lines) | **V1.1** (1023 lines) | SOC-II Prospectus restructured: DEEPENING (3 priorities: cultural calibration, privacy-encounter curve, Dunbar validation) + BROADENING (3 priorities: digital-physical privacy, healthcare, lifespan). |
| 47 | VIEW-I: Nature View | Completed from WIP | **V1.0** (640 lines) | Built with broadening/deepening from the start: DEEPENING (3 priorities: channel weights, synthetic nature, view quality index) + BROADENING (2 priorities: cultural/developmental moderators, blue space). |

### Calibration Panels Completed

| Doc | Panel | Type | Lines | Coverage Impact |
|-----|-------|------|-------|-----------------|
| 49 | L-II: Light Calibration | Calibration (deepening) | 534 | A4 ★★★ → ★★★★ |
| 51 | MAT-II: Materials Calibration | Calibration (deepening + broadening) | 710 | A1 ★★★ → ★★★★; A7 ★★★ → ★★★★ |

### Panels NOT YET Revised (Still at Original Prospectus Format)

| Doc | Panel | Status | Action Needed |
|-----|-------|--------|---------------|
| 45 | COL-I: Color | WIP (628 lines — only COL1 + COL2 templates) | Needs closing apparatus + broadening/deepening when completed |
| 46 | OLF-I: Olfaction | Complete (439 lines) | Needs broadening/deepening retrofit to OLF-II Prospectus |
| 37 | MAT-I: Materials | Complete | Superseded by MAT-II (Doc 51); original prospectus now replaced by MAT-III prospectus in Doc 51 |
| 38 | SC-I: Spatial Configuration | Complete | Needs broadening/deepening retrofit |
| 39 | VF-I: Visual Form | Complete | Needs broadening/deepening retrofit |
| 14–19 | Panels I–V (T-series) | Complete | Foundation panels; broadening/deepening retrofit low priority |
| 24–26 | Music Panels M-I to M-III | Complete | Broadening/deepening retrofit low priority |
| 27 | AX-I: Auxiliary | Complete | Broadening/deepening retrofit low priority |

---

## PART B: TEMPLATE-BY-TEMPLATE CALIBRATION STATUS

### Legend

- **Maturity**: established / supported / supported with dissent / preliminary / supported-preliminary / speculative
- **Calibration**: ✓ substantially calibrated / ~ partially calibrated / ○ protocol specified / ✗ uncalibrated
- **Source**: document providing the calibration data

---

### L-Series (Light) — Calibrated by Doc 49 (L-II)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **L1** | Luminance Contrast PE | Supported | ~ Partial | CV-of-luminance Goldilocks: comfort < 0.5; aesthetic 0.5–1.5; dramatic 1.5–3.0; discomfort > 3.0. Photosensitivity correction: ±30–50% shift. | Doc 49 §Cal1 |
| **L2** | Circadian Regulation Pathway | Established | ✓ Substantial | Age-corrected M-EDI: M-EDI(age) ≈ M-EDI(25) × (1 + 0.015 × (age − 25)). Elderly need ~2× melanopic irradiance. CS ≥ 0.3 for ≥ 2 hours threshold confirmed. | Doc 49 §Cal2 |
| **L3** | Daylight Multi-Channel Convergence | Supported | ~ Partial | Channel weights: circadian ~0.35, view ~0.25, contrast ~0.15, CCT ~0.10, dynamics ~0.15. Super-additivity ~15–25%. | Doc 49 §Cal3 |
| **L4** | CCT as Ecological Prediction Signal | Supported with dissent | ~ Partial | Ecological framing retained. Arousal-mediation alternative acknowledged. Steidle-Veitch debate: warm CCT = evening → relaxation (supported) vs. low-arousal mediation (alternative). | Doc 49 §Cal4 |
| **L5** | Dynamic Light & Temporal PE Engagement | Supported-preliminary | ✗ Uncalibrated | Maturity upgraded from "preliminary" to "supported-preliminary." No quantitative rate-of-change parameters. | Doc 49 §Cal5 |

### MAT-Series (Materials) — Calibrated by Doc 51 (MAT-II)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **MAT1** | Thermal Adaptive PE | Supported | ✓ Substantial | Adaptive neutral: T_n = 0.31 × T_running_mean + 17.8°C. Goldilocks: neutral ±1°C; positive PE ±1–3°C (directionally corrective); tolerance ±3–5°C; discomfort >±5°C. Alliesthesia requires DIRECTIONAL correction. | Doc 51 §Cal2 |
| **MAT2** | Contact Thermal PE | Supported | ~ Partial | CT-afferent: pleasurable 28–36°C contact temp; optimal stroke 1–10 cm/s, peak ~3 cm/s. Effusivity classes: warm <500; neutral 500–1,500; cool-alerting 1,500–3,000; cold-aversive >7,000 J m⁻² K⁻¹ s⁻¹/². Wood at room temp → pleasurable; metal → aversive; stone → cool-alerting (climate-dependent valence). | Doc 51 §Cal2, §PS-McGlone |
| **MAT3** | Cross-Modal Material Identity | Supported | ○ Protocol specified | 8-condition factorial (visual × haptic × thermal congruence). Predicted: haptic incongruence penalty > visual (d ≈ 0.6–0.8 vs. 0.4–0.6). Full incongruence d ≈ 0.8–1.2. SCR latency < 500ms at incongruent touch. NOT YET EXECUTED. | Doc 51 §Cal3 |
| **MAT4** | Natural Material Convergence (Wood) | Supported | ~ Partial | Channel weights: visual 0.30 (±0.08), haptic 0.20 (±0.10), acoustic 0.10 (±0.08), olfactory 0.15 (±0.10, TIME-DEPENDENT — 25–35% at 0–5 min, near-zero at 20+ min), biophilic-cultural 0.25 (±0.12, CULTURALLY VARIABLE — Western/Japanese estimate). Super-additivity: 20–30%. | Doc 51 §Cal1 |
| **MAT5** | Material-Cultural Conditioning | Preliminary | ○ Framework specified | Multiplicative moderator: MAT5 scales other channel weights by cultural exposure factor. Cross-cultural prediction made (4 cultures min). NOT YET CALIBRATED. | Doc 51 §PS-Majid, §Pred4 |

### MAT-II Additional Outputs: Non-Wood Channel Profiles (Preliminary)

| Material | Visual | Haptic-thermal | Acoustic | Olfactory | Cultural | Super-additivity | Source |
|----------|--------|---------------|----------|-----------|----------|-----------------|--------|
| **Stone** | 0.35 | 0.30 (climate-dependent valence) | 0.20 | 0.05 | 0.10 (geological) | 10–15% | Doc 51 §Cal4 |
| **Concrete** | 0.40 | 0.20 | 0.15 | 0.05 | 0.20 (polarizing) | 10–15% | Doc 51 §Cal4 |
| **Metal** | 0.35 | 0.25 (typically aversive cold) | 0.25 (distinctive resonance) | 0.05 | 0.10 (industrial) | 15–20% | Doc 51 §Cal4 |

**Note**: All non-wood profiles are EXPERT JUDGMENT, not empirical calibration. Uncertainty ±0.10–0.15 per weight.

---

### VIEW-Series — NOT YET CALIBRATED (Awaiting VIEW-II)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **VIEW1** | Nature View Multi-Channel Convergence | Supported | ✗ Uncalibrated | 5 channels identified (fractal fluency, prospect/depth, soft fascination, temporal variation, ecological safety). Individual channels calibrated through parent templates (T1, SC2, T25, L5, T5). Convergence model NOT parameterized — no channel weights, no super-additivity estimate. 120 min/week dose-response (White et al., 2019) provides overall anchor. | Doc 47 §Cal |

### TP-Series — NOT YET CALIBRATED (Awaiting TP-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **TP1** | Motor Prediction & Proprioceptive PE | Supported | ✗ Uncalibrated | Structurally complete, parametrically empty. Needs IMU-validated motor PE metric. | Doc 42 |
| **TP2** | Architectural Threshold as Episodic Boundary | Supported | ✗ Uncalibrated | Channel-count → boundary-strength function unknown. Needs VR graded-stimulus experiment. | Doc 42 |
| **TP3** | Material Aging & Temporal Depth | Supported-preliminary | ✗ Uncalibrated | Fractal convergence-toward-1.3 hypothesis untested. Needs cross-sectional surface measurement. | Doc 42 |
| **TP4** | Temporal Hierarchy of Architectural PE | Supported | ✗ Uncalibrated | Multi-timescale integration claim untested. Needs ambulatory multi-measure validation. | Doc 42 |

### SOC-Series — NOT YET CALIBRATED (Awaiting SOC-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **SOC1** | Proxemic PE | Supported | ✗ Uncalibrated | Zone boundaries from Hall's NA data only. Needs cross-cultural proxemic measurement in real buildings. | Doc 44 |
| **SOC2** | Architectural Privacy Gradient | Supported | ✗ Uncalibrated | 5 physical mechanisms identified. Privacy-encounter trade-off curve shape unknown. | Doc 44 |
| **SOC3** | Territorial Affordance Gradient | Supported | ✗ Uncalibrated | Dunbar-layer scaling untested. Needs intervention study (open floor → Dunbar pods). | Doc 44 |

### COL-Series — NOT YET CALIBRATED (Doc 45 is WIP)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **COL1** | Chromatic PE in Architectural Context | Supported | ✗ Uncalibrated | Template complete; no panel closing apparatus yet. | Doc 45 |
| **COL2** | Color-Arousal Modulation | Supported | ✗ Uncalibrated | Template complete; no panel closing apparatus yet. | Doc 45 |

### OLF-Series

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **OLF1** | Olfactory Transition PE | Supported | ✗ Uncalibrated | Transition function specified but not parameterized. Adaptation timecourse (15–20 min) from Dalton (2000). MAT-II references OLF1 for wood olfactory channel. | Doc 46 |

### SC-Series — NOT YET CALIBRATED

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **SC1** | Enclosure Gradient PE | Supported | ✗ Uncalibrated | | Doc 38 |
| **SC2** | Isovist-Based Spatial PE | Supported | ✗ Uncalibrated | | Doc 38 |
| **SC3** | Path Integration PE | Supported | ✗ Uncalibrated | | Doc 38 |
| **SC4** | Encounter Probability Gradient | Supported | ✗ Uncalibrated | | Doc 38 |

### VF-Series — NOT YET CALIBRATED

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **VF1** | Façade Complexity Goldilocks | Supported | ✗ Uncalibrated | | Doc 39 |
| **VF2** | Symmetry & Pattern PE | Supported | ✗ Uncalibrated | | Doc 39 |
| **VF3** | Ceiling Height & Vertical Scale | Supported | ✗ Uncalibrated | Key target for A2 extension | Doc 39 |

### T-Series, M-Series, AX-Series — Foundation Templates

Status: ~78 templates across Docs 14–19, 24–27. These are the theoretical backbone of the system. Most are at "supported" maturity. None have been through a dedicated calibration panel. Calibration priorities are domain-specific and would be driven by the calibration panels above (e.g., T1 fractal fluency is indirectly calibrated through L-II and MAT-II channel-weight estimation).

---

## PART C: COVERAGE SCORECARD (Current as of Doc 52)

| Domain | Rating | Key Templates | Calibration Status | Next Action |
|--------|--------|--------------|-------------------|-------------|
| A1 Materials & Surfaces | **★★★★** | MAT1–5, L4 | MAT1 ✓, MAT2 ~, MAT4 ~ | MAT-III for empirical validation |
| A2 Spatial Scale | **★★★+** | SC1–2, VF3, T2 | All ✗ | **HIGHEST PRIORITY GAP**: VF3 targeted extension |
| A3 Spatial Configuration | **★★★★** | SC1–4, T-series | SC ✗ | SC-II if needed |
| A4 Light & Luminance | **★★★★** | L1–5 | L1~, L2✓, L3~, L4~, L5✗ | L-III for remaining calibration |
| A5 Acoustic | **★★★★** | M1–17, AX1 | M ✗ | M-II if needed |
| A6 Visual Pattern & Form | **★★★★** | T1, T2, VF1–2, COL1–2 | T1 indirectly ~ | Stable |
| A7 Haptic & Thermal | **★★★★** | MAT1–2, MAT4 haptic | MAT1 ✓, MAT2 ~ | MAT-III neuroimaging |
| A8 Social Configuration | **★★★★** | SOC1–3, SC4 | SOC ✗ | SOC-II cultural calibration |
| A9 Task & Cognition | **★★★★/★★+** | T25, L2, VIEW1 attention / creativity weak | Attention ~, Creativity ✗ | Creativity panel needed |
| A10 Temporal | **★★★★** | TP1–4, L2, L5 | TP ✗ | TP-II for calibration |

**Domains at ★★★★**: 9 of 10  
**Remaining gap**: A2 (★★★+) — needs targeted extension, not a full panel  
**Weakest calibration**: TP, SOC, SC series (all structurally complete, parametrically empty)

---

## PART D: BROADENING/DEEPENING PRIORITY QUEUE

### Calibration Panels Needed (DEEPENING)

| Priority | Panel | What It Calibrates | Coverage Impact | Prerequisite Docs |
|----------|-------|-------------------|-----------------|-------------------|
| 1 | **A2 Targeted Extension** | VF3 (ceiling height), SC2 (isovist-scale) | A2 ★★★+ → ★★★★ | Docs 38, 39 |
| 2 | **TP-II** | TP1–4 boundary values | A10 consolidation | Doc 42 V1.1 |
| 3 | **SOC-II** | SOC1–3 cultural calibration + privacy-encounter curve | A8 consolidation | Doc 44 V1.1 |
| 4 | **A9 Creativity Panel** | New template(s) for creative cognition | A9 creativity ★★+ → ★★★+ | Docs 18, 19 |

### Extension Panels Needed (BROADENING)

| Priority | Panel | What It Extends | Cross-Cutting Impact | Prerequisite Docs |
|----------|-------|----------------|---------------------|-------------------|
| 5 | **Aging & Architecture** | Age moderators across 10+ templates | Cross-cutting — affects MAT1/2, TP1, SOC1, L2 | All calibrated panels |
| 6 | **Child Development** | Developmental moderators, school design | Cross-cutting — attention restoration, nature-deficit | Docs 47, 42 |
| 7 | **VIEW-II** | Channel weights, synthetic nature, blue space | A6/A9 enrichment | Doc 47 |

### Remaining Retrofits Needed

| Doc | Panel | What Needs Adding |
|-----|-------|------------------|
| 46 | OLF-I | Broadening/deepening framework to OLF-II Prospectus |
| 38 | SC-I | Broadening/deepening framework to SC-II Prospectus |
| 39 | VF-I | Broadening/deepening framework to VF-II Prospectus |
| 45 | COL-I | Complete panel (closing apparatus + broadening/deepening) |

---

## PART E: KEY CROSS-TEMPLATE PATTERNS FOR ENCODING

### The Convergence Triad (L3, MAT4, VIEW1)

All three share the same structural pattern: natural stimulus engages 5+ PE channels simultaneously with super-additive combination.

| Property | L3 (Daylight) | MAT4 (Wood) | VIEW1 (Nature View) |
|----------|--------------|-------------|---------------------|
| Channels | 5–6 | 5 | 5 |
| Calibration status | ~ Partial (weights estimated) | ~ Partial (weights estimated) | ✗ Uncalibrated |
| Dominant channel | Circadian (0.35) | Visual grain (0.30) | Unknown (fractal fluency likely) |
| Super-additivity | 15–25% | 20–30% | Not yet estimated |
| Time structure | Continuous (daytime) | Continuous (visual) + transitional (olfactory) + intermittent (haptic) | Continuous (visual) |
| Cultural moderation | Low (biological) | Moderate (MAT5) | Moderate |

**Encoding note**: These three templates should share a `convergence_model` metadata structure with parallel fields for channel_weights, super_additivity_estimate, time_structure, and cultural_moderation_level.

### Climate-Dependent Valence Reversal

Affects: MAT1, MAT2, stone/concrete/metal profiles. In hot climates, cool materials (high effusivity) produce POSITIVE affective valence; in cold climates they produce NEGATIVE valence. The PE sign depends on direction of deviation from thermal expectation.

**Encoding note**: Templates with thermal parameters need a `climate_context` field: {climate_type: hot/temperate/cold, valence_direction: +/-/neutral}.

### Cultural Moderation as Multiplicative Factor

Affects: MAT4 (Channel 5), MAT5, SOC1, SOC3, VIEW1 (Channel 5), COL1/COL2. The cultural channel does not ADD a fixed increment — it SCALES the other channel weights.

**Encoding note**: Templates with cultural moderation need a `cultural_modifier` metadata field: {population: "Western/Japanese", modifier_type: "multiplicative", confidence: "low"}.

### Preattentive vs. Attentive Processing Distinction

MAT-II established that material convergence operates preattentively (below conscious awareness). This is architecturally consequential: material effects are continuous background signals, not discrete events.

Affects: MAT3, MAT4, and by extension any template involving multi-modal integration. Templates should be tagged with `processing_mode: preattentive | attentive | mixed`.

### Olfactory Transition Function

OLF1 and MAT4 Channel 4 share a common pattern: olfactory contribution is HIGH at arrival (0–5 minutes) and NEAR-ZERO at steady state (20+ minutes) due to adaptation. This is a general pattern that may apply to any olfactory-involving template.

**Encoding note**: Olfactory channel weights should include a `time_function` field: {peak_window_min: 0–5, adaptation_onset_min: 15–20, steady_state_contribution: "near-zero"}.

---

## PART F: AGENT TASK ASSIGNMENTS

### Claude Code

1. Encode 11 new templates from Docs 42–47 (TP1–4, SOC1–3, COL1–2, OLF1, VIEW1) into template.ts schema
2. Attach L-II calibration parameters to L1–L5 (from Part B, L-Series table above)
3. Attach MAT-II calibration parameters to MAT1–MAT5 (from Part B, MAT-Series table above)
4. Create `convergence_model` metadata structure for L3, MAT4, VIEW1
5. Add non-wood channel profiles (stone, concrete, metal) as material reference data
6. Build Doc 43 Master Reference Inventory (extract all APA refs from all panel docs, deduplicate)

### Codex

1. Update task board with Docs 47–52
2. Validate template.ts schema handles calibration metadata (parameter tables, boundary values, channel weights, uncertainty estimates)
3. Ensure `climate_context`, `cultural_modifier`, `processing_mode`, and `time_function` fields exist in schema

### Antigravity

1. 11 new templates from Docs 42–47 for round-trip validation
2. L-II and MAT-II calibration parameters for round-trip testing
3. Non-wood material profiles for validation

---

*Calibration & Extension Registry — Document 52 V1.0*
*February 16, 2026*
*Purpose: Consolidated lookup table for template encoding, calibration data, and panel update tracking*
*Updates when: Any panel is calibrated, revised, or extended*
*Next update trigger: A2 targeted extension or TP-II completion*
