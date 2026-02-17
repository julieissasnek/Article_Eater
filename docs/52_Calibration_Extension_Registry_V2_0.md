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
| 56 | TP-II: Temporal Calibration | Calibration (deepening) | 618 | TP1–TP4 ✗ → ~ Partial |
| 57 | SOC-II: Social Calibration | Calibration (deepening) | 513 | SOC1–SOC3 ✗ → ~ Partial/✓ Good |
| 58 | CREA-II: Creative Calibration | Calibration (deepening) | 446 | CREA1–CREA3 ✗ → ~ Partial |
| 59 | VIEW-II: Nature View Calibration | Calibration (deepening) | 378 | VIEW1 ✗ → ~ Partial + ✓ Good (VQI) |
| 60 | AGE-I: Aging & Architecture | Cross-cutting moderation | 369 | Age moderation for L, MAT, TP, SOC, CREA, VIEW |
| 61 | DEV-I: Child Development | Cross-cutting moderation | 309 | Developmental moderation for L, TP, SOC, CREA, VIEW + school design |
| 62 | SC-II: Spatial Configuration Calibration | Calibration (deepening) | 384 | SC1-SC4 calibrated: promenade parameters, integration-emotion, 3D vertical PE |
| 63 | COL-II: Color Calibration | Calibration (deepening) | 274 | COL1-2 calibrated: hue×context matrix, arousal dose-response, habituation τ |

### Panels NOT YET Revised (Still at Original Prospectus Format)

| Doc | Panel | Status | Action Needed |
|-----|-------|--------|---------------|
| 45 | COL-I: Color | Complete (V1.0, 630 lines) | COL1–COL2 templates + calibration + COL-II prospectus. A6.3 ★★ → ★★★ |
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

### VIEW-Series — CALIBRATED by Doc 59 (VIEW-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **VIEW1** | Nature View Multi-Channel Convergence | Supported | ~ Partial + ✓ Good (VQI) | Channel weights: Ch5 0.30, Ch3 0.24, Ch1 0.18, Ch2 0.18, Ch4 0.10. Two convergence models (additive + gated). Synthetic nature hierarchy (9 levels). VQI 0–100 with design thresholds. Blue-space bonus +15–20%. Temporal accumulation principle. | Doc 59 §Cal1–3 |

### TP-Series — CALIBRATED by Doc 56 (TP-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **TP1** | Motor Prediction & Proprioceptive PE | Supported | ~ Partial | MFI metric defined (DFA scaling exponent); architectural ranges estimated; age moderation 1.0–4.0× attentional cost multiplier. | Doc 56 §Cal3 |
| **TP2** | Architectural Threshold as Episodic Boundary | Supported | ~ Partial | Channel-count gradient calibrated (d ≈ 0.25 per channel, additive + 17% super-additivity); channel weights estimated; threshold density Goldilocks 3–6/10min. | Doc 56 §Cal1 |
| **TP3** | Material Aging & Temporal Depth | Supported-preliminary | ~ Partial | Material-specific exponential aging trajectories for 8 materials. Universal D ≈ 1.3 convergence replaced by material-specific D_max values. | Doc 56 §Cal2 |
| **TP4** | Temporal Hierarchy of Architectural PE | Preliminary | ~ Partial | Multi-timescale variance decomposition estimated (combined R² ~0.55). PE density → subjective time: logarithmic function with k ≈ 0.35. | Doc 56 §Cal4 |

### SOC-Series — CALIBRATED by Doc 57 (SOC-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **SOC1** | Proxemic PE | Supported | ~ Partial | 5-cluster cultural zone boundaries calibrated (42-country, N≈9,000); CPP parameter proposed; architectural dimensions culture-specific. | Doc 57 §Cal1 |
| **SOC2** | Architectural Privacy Gradient | Supported | ✓ Good | Privacy-encounter curve quantified (3 independent data streams, N>42,000); optimal ratio 0.50; cost knee 0.70; encounter paradox >0.80; privacy mechanism ranking. | Doc 57 §Cal2 |
| **SOC3** | Territorial Affordance Gradient | Supported | ~ Partial | Dunbar layers mapped to physical distances (exponential decay λ≈8m); floor tax ~8×; layer-specific enclosure/acoustic/amenity parameters. | Doc 57 §Cal3 |

### CREA-Series — CALIBRATED by Doc 58 (CREA-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **CREA1** | Creative Network Dynamics | Supported | ~ Partial | Three-phase model calibrated (generation 60±20s, selective 50±15s, evaluation 70±25s). Phase-environment d matrix specified. Generative environments extend Phase 1 by ~30%. Alpha power as real-time phase marker. | Doc 58 §Cal2 |
| **CREA2** | Multi-Channel Processing Style Modulation | Supported with dissent | ~ Partial | Three-pathway d values: A (noise) 0.40, B (space+light) 0.38, C (demand) 0.30. Sub-additivity: ~75–80% of additive acute, ~85–90% sustained. Creativity Goldilocks Ceiling d ≈ 0.75–0.80. Two-pathway optimum d ≈ 0.55–0.65. | Doc 58 §Cal1 |
| **CREA3** | Incubation Architecture | Supported-preliminary | ~ Partial | Walk duration dose-response: peak 10–15 min. Indoor d ≈ 0.55–0.60; outdoor d ≈ 0.70–0.78. Threshold spacing 50–100m. Post-walk persistence 6–10 min. Evaluative workspace within 2-min walk. | Doc 58 §Cal3 |

### COL-Series — COMPLETE, NOT YET CALIBRATED (Doc 45 V1.0)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **COL1** | Chromatic PE in Architectural Context | Supported | ✗ Uncalibrated | Three-source model (EVT + Color-in-Context + geography of color). Habituation clause specified qualitatively. Awaiting COL-II for hue × context matrix. | Doc 45 |
| **COL2** | Color-Arousal Modulation | Supported | ✗ Uncalibrated | PAD dimensional framework. Arousal = f(brightness, saturation). Dose-response unparameterized. Awaiting COL-II. | Doc 45 |

### OLF-Series

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **OLF1** | Olfactory Transition PE | Supported | ✗ Uncalibrated | Transition function specified but not parameterized. Adaptation timecourse (15–20 min) from Dalton (2000). MAT-II references OLF1 for wood olfactory channel. | Doc 46 |

### SC-Series — CALIBRATED by Doc 62 (SC-II)

| Template | Name | Maturity | Calibration | Status | Source |
|----------|------|----------|-------------|--------|--------|
| **SC1** | Spatial Integration PE | Supported | ✓ Good | Integration-valence r=0.55; combined R²~0.50; 3D vertical multiplier 1.5-2.5× per floor; atrium mitigation 30-50%. | Doc 38, 62 §Cal2-3 |
| **SC2** | Isovist Dynamics | Supported | ~ Partial | Isovist-contrast → GSR: 0.30×ln(ratio). Compression-release 1:3 to 1:8 optimal. | Doc 38, 62 §Cal1 |
| **SC3** | Architectural Promenade | Supported | ~ Partial | Threshold density Goldilocks 20-45s. Compositional temporal shape (approach/development/climax/denouement). GSR peaks 2-3× for compression-release vs. simple doorway. | Doc 38, 62 §Cal1 |
| **SC4** | Social Encounter Prediction | Supported | ✓ Good | Already well-calibrated via Space Syntax behavioral validation. | Doc 38 |

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
| A2 Spatial Scale | **★★★★** | SC1–2, VF3, T2, Volumetric Proportion PE | VF3~, SC2~ | **CLOSED by Doc 54** — targeted extension complete |
| A3 Spatial Configuration | **★★★★** | SC1–4, T-series | SC ✗ | SC-II if needed |
| A4 Light & Luminance | **★★★★** | L1–5 | L1~, L2✓, L3~, L4~, L5✗ | L-III for remaining calibration |
| A5 Acoustic | **★★★★** | M1–17, AX1 | M ✗ | M-II if needed |
| A6 Visual Pattern & Form | **★★★★** | T1, T2, VF1–2, COL1–2 | T1 indirectly ~ | Stable |
| A7 Haptic & Thermal | **★★★★** | MAT1–2, MAT4 haptic | MAT1 ✓, MAT2 ~ | MAT-III neuroimaging |
| A8 Social Configuration | **★★★★** | SOC1–3, SC4 | SOC ~ / ✓ | SOC-II cultural + privacy-encounter calibration complete |
| A9 Task & Cognition | **★★★★/★★+** | T25, L2, VIEW1 attention / creativity weak | Attention ~, Creativity ✗ | Creativity panel needed |
| A10 Temporal | **★★★★** | TP1–4, L2, L5 | TP ✗ | TP-II for calibration |

**Domains at ★★★★**: 10 of 10  
**ALL 10 DOMAINS AT ★★★★** — No remaining structural gaps  
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
| 45 | COL-I | ✓ COMPLETE — V1.0 delivered Feb 17. COL-II prospectus included. |

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

*Calibration & Extension Registry — Document 52 V1.2*
*February 16, 2026*
*Purpose: Consolidated lookup table for template encoding, calibration data, and panel update tracking*
*Updates when: Any panel is calibrated, revised, or extended*
*Next update trigger: TP-II completion*

### ADDENDUM (V1.1): A2 Extension Calibration Data (from Doc 54)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **VF3** | Ceiling Height & Cognitive Mode | Supported | ~ Partial | Proportional ratio R_h = height/√(area). Goldilocks: confinement <0.25; balanced 0.25–0.35; liberating 0.35–0.50; impressive 0.50–0.80; overwhelming >0.80. Perception corrections: light color +5–10%, ceiling-wash +5–8%, coffering −10–15%. | Doc 54 §VF3 |
| **SC2** | Isovist-Based Spatial PE | Supported | ~ Partial | Weber's law: PE ∝ ln(A_new/A_old). Reveal-compression asymmetry: compressions ~1.5× reveals with negative valence shift. Optimal spatial rhythm: 2–4× area change per transition, every 15–40m. | Doc 54 §SC2 |
| **NEW** | Volumetric Proportion PE | Preliminary | ○ Framework | H_expected = k × area^p (p ≈ 0.3–0.4). PE_volumetric = |H_actual − H_expected| / H_expected. Integrates VF3 + SC2. Needs psychophysical validation. | Doc 54 §Target3 |

**Coverage change**: A2 ★★★+ → ★★★★. **ALL 10 DOMAINS NOW AT ★★★★.**

### ADDENDUM (V1.2): CREA-I Creative Cognition Templates (from Doc 55)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **CREA1** | Creative Network Dynamics — DMN–ECN–SN Coupling | Supported | ~ Partial | Three-network coupling: DMN (generation), ECN (evaluation), SN (switching). Generative phase: DMN-dominant, weak ECN coupling, posterior alpha↑. Evaluative phase: strong ECN coupling, frontal alpha↑. Optimal environment: moderate sensory richness → SN engaged at flexible switching rate. | Doc 55 §CREA1 |
| **CREA2** | Multi-Channel Environmental Processing Style Modulation | Supported with dissent | ~ Partial | Three pathways: (A) Disfluency — noise 65–75 dB non-semantic → abstract construal, d ≈ 0.4–0.6 divergent; (B) Spaciousness — ceiling R_h 0.35–0.50 (VF3 liberating) + dim ~150 lux → expanded prediction envelope; (C) Resource reallocation — reduced external demand → freed executive resources → internal search. FUNDAMENTAL TRADEOFF: divergent-promoting features impair convergent thinking. | Doc 55 §CREA2 |
| **CREA3** | Incubation Architecture — Movement & Creative Mind-Wandering | Supported-preliminary | ~ Partial | Walking at self-selected pace: d ≈ 0.8 divergent thinking (Oppezzo). Mechanism: motor-proprioceptive PE maintains meta-aware mind-wandering (Schooler). Treadmill effect confirms motor primacy. Soft fascination adds ~15–20%. Optimal break 5–20 min. Convergent thinking: null to negative. | Doc 55 §CREA3 |

**Coverage change**: A9 Creativity ★★+ → ★★★★. **ALL A9 SUB-DOMAINS NOW AT ★★★★.**

### Updated Coverage Scorecard

| Domain | Rating | Change | Notes |
|--------|--------|--------|-------|
| A9 Task & Cognition | **★★★★** | Creativity ★★+ → ★★★★ (CREA-I) | Attention ★★★★ (unchanged); Creativity now ★★★★ |

### Updated Priority Queue

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **TP-II** | TP1–4 boundary values | A10 consolidation | Doc 42 V1.1 |
| 2 | **SOC-II** | SOC1–3 cultural calibration + privacy-encounter curve | A8 consolidation | Doc 44 V1.1 |
| 3 | **CREA-II** | Multi-channel interaction coefficients, walking path parameters, phase-environment mapping | A9 deepening | Doc 55 |
| 4 | **Aging & Architecture** | Age moderators across 10+ templates | Cross-cutting | All calibrated panels |
| 5 | **Child Development** | Developmental moderators, school design | Cross-cutting | Docs 47, 42 |
| 6 | **VIEW-II** | Channel weights, synthetic nature, blue space | A6/A9 enrichment | Doc 47 |

### CREA Cross-Template Encoding Patterns

**Three-Zone Model**: CREA templates collectively define a three-zone architectural model (generative / evaluative / transitional) that should be encoded as a `workspace_zone` metadata structure on all creativity-relevant templates.

**Phase Tagging**: Templates interacting with CREA should be tagged with `creative_phase_affinity: generative | evaluative | incubation | phase_neutral` to enable automatic zone-assignment recommendations.

**Divergent-Convergent Tradeoff Flag**: Any template parameter that promotes divergent processing should carry a `convergent_tradeoff: true` warning to prevent naive optimization for creativity at the expense of analytical capability.

### ADDENDUM (V1.3): TP-II Temporal Calibration Data (from Doc 56)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **TP1** | Motor Prediction PE | Supported | ~ Partial | Motor Fluency Index (MFI) = α_local / α_baseline (DFA scaling exponent). Ranges: level corridor MFI 0.95–1.00; good staircase 0.80–0.90; steep staircase 0.65–0.80; irregular surface 0.60–0.75; challenging 0.45–0.65. Age moderation: attentional cost multiplier 1.0× (young) to 2.5–4.0× (frail older). | Doc 56 §Cal3 |
| **TP2** | Threshold Episodic Boundary | Supported | ~ Partial | Channel-count → boundary strength: 1 channel d ≈ 0.25; 2 channels d ≈ 0.45; 3 channels d ≈ 0.68; 4 channels d ≈ 0.88; 5+ channels d ≈ 1.00–1.15. Combination rule: additive with 17% super-additivity for synchronized changes. Channel weights: spatial 0.25, luminance 0.20, acoustic 0.18, material 0.15, thermal 0.12, motor 0.10, olfactory 0.08. Threshold density Goldilocks: 3–6 strong per 10-min walk. | Doc 56 §Cal1 |
| **TP3** | Material Aging & Temporal Depth | Supported-preliminary | ~ Partial | Exponential approach model: D(t) = D_0 + (D_max − D_0) × (1 − e^(−t/τ)). Limestone: D_0 1.05, D_max 1.40, τ 30–60 yr. Brick: D_0 1.08, D_max 1.30, τ 50–100 yr. Hardwood: D_0 1.15, D_max 1.35, τ 15–30 yr. Concrete: D_0 1.05, D_max 1.15, τ 20–40 yr (variable, may age negatively). Three maintenance regimes: managed positive / unmanaged / restorative. | Doc 56 §Cal2 |
| **TP4** | Temporal Hierarchy | Preliminary | ~ Partial | Multi-timescale variance decomposition: T-1 R² ~0.08 unique, T-2 ~0.13, T-3 ~0.16, T-4 ~0.12; combined R² ~0.55. PE density → subjective time: Duration_est = T_clock × [1 + 0.35 × ln(N_events / N_baseline)]. | Doc 56 §Cal4 |

**Calibration change**: TP1 ✗→~; TP2 ✗→~; TP3 ✗→~; TP4 ✗→~. All four TP templates now ~ Partially calibrated.

### Updated Priority Queue (V1.4)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **CREA-II** | Multi-channel interaction coefficients, walking path parameters | A9 deepening | Doc 55 |
| 2 | **TP-III** | Empirical validation of TP-II estimates (VR study, surface measurement, gait study) | A10 deepening | Doc 56 |
| 3 | **SOC-III** | Multicultural design parameters, privacy mechanism dose-response, healthcare application | A8 deepening | Doc 57 |
| 4 | **Aging & Architecture** | Age moderators across 10+ templates | Cross-cutting | All calibrated panels |
| 5 | **Child Development** | Developmental moderators, school design | Cross-cutting | Docs 47, 42 |
| 6 | **VIEW-II** | Channel weights, synthetic nature, blue space | A6/A9 enrichment | Doc 47 |

### TP-II Cross-Template Encoding Patterns

**Motor Fluency Index (MFI)**: Templates involving movement through architecture (TP1, SC3, CREA3) should include an `mfi_range` metadata field with expected Motor Fluency Index ranges for the architectural condition. Encoding agents should attach MFI age-moderation multipliers for universal design assessment.

**Threshold Strength Scoring**: TP2's channel-count framework provides a quantitative method for scoring any architectural threshold. Templates involving spatial transitions (TP2, SC3, AX3, AX6) should include `threshold_channel_count` and `estimated_boundary_d` metadata fields. This connects directly to CREA3's threshold-segmented incubation prediction.

**Temporal Depth Trajectory**: Templates involving material properties (MAT1–MAT5, TP3) should include an `aging_trajectory` metadata structure: {material, D_0, D_max, tau_years, maintenance_regime}. Encoding agents can compute estimated surface D at any building age.

**PE Density Index**: For any path-based architectural assessment, templates should compute a `pe_density_index` = N_events / T_walk_minutes. Wittmann's formula then predicts the subjective temporal experience: expansive (index > 3 events/min), moderate (1–3), compressed (< 1).

### ADDENDUM (V1.4): SOC-II Social Calibration Data (from Doc 57)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **SOC1** | Proxemic PE | Supported | ~ Partial | 5-cluster cultural zone boundaries: Latin Am (stranger 78cm, close 40cm), N.Am (95cm, 50cm), N.Eur (100cm, 48cm), E.Asian (102cm, 55cm), M.East (115cm, 60cm). Cultural Privacy Parameter (CPP): N.Eur 0.85, N.Am 0.80, M.East 0.70, L.Am 0.50, E.Asian 0.45. | Doc 57 §Cal1 |
| **SOC2** | Privacy Gradient | Supported | ✓ Good | Privacy-encounter optimal ratio 0.50 ± 0.08 (3 independent data streams, N>42,000). Cost knee at 0.70. Encounter paradox above 0.80 (70% face-to-face reduction). Privacy mechanism ranking: withdrawal spaces > acoustic enclosure > visual screen > territorial marker > spatial distance. Minimum prescription: 1 phone booth / 8 workers; 1 quiet room / 25; 1 private meeting / 15. | Doc 57 §Cal2 |
| **SOC3** | Territorial Affordance | Supported | ~ Partial | Dunbar-layer distance mapping: 5-layer 0–6m, 15-layer 6–15m, 50-layer 15–30m, 150-layer same building. Interaction decay: e^(−d/8). Floor tax ~8×. Pod enclosure: STC 35–40; zone masking: 45 dBA. | Doc 57 §Cal3 |

**Calibration change**: SOC1 ✗→~; SOC2 ✗→✓; SOC3 ✗→~.

**Coverage change**: A8 Social Configuration ★★+ → ★★★★.

### SOC-II Cross-Template Encoding Patterns

**Cultural Proxemic Zones**: All templates involving interpersonal distance (SOC1, SC4, SOC3) should include `cultural_cluster` as a required moderator field. Zone boundaries should be parameterized per-cluster, not hardcoded to North American defaults. Encoding agents should tag parameters with `{culture: "north_american" | "northern_european" | "east_asian" | "latin_american" | "middle_eastern"}`.

**Privacy-Encounter Ratio**: Templates involving shared/private space design (SOC2, SC4) should include `shared_private_ratio` as an input variable and compute expected satisfaction using the concave function: S ≈ 5.8 × [1 − 2.0(r − 0.50)² − 4.0 × max(0, r − 0.70)²]. The encounter paradox flag should trigger when ratio > 0.80.

**Dunbar-Layer Distance**: Templates involving social grouping (SOC3, SC4) should include `dunbar_layer` field and compute expected interaction frequency using exponential decay: f = e^(−d/8). The `floor_tax_multiplier: 8` should be applied to all inter-floor calculations.

**Interaction Quality Index (IQI)**: Templates assessing social design quality should compute IQI = frequency × quality, where frequency comes from Waber's decay function and quality from Pentland's engagement scoring. Semi-enclosed pods (IQI ≈ 0.45) should be flagged as the optimal configuration.

### ADDENDUM (V1.5): CREA-II Creative Calibration Data (from Doc 58)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **CREA1** | Creative Network Dynamics | Supported | ~ Partial | Three-phase model: Phase 1 (generation, 60±20s, DMN-dominant), Phase 2 (selective, 50±15s, increasing coupling), Phase 3 (evaluation, 70±25s, ECN-dominant). Generative environments extend Phase 1 by ~30%. Alpha power (10–12 Hz frontal) as real-time phase marker. Phase-environment d matrix calibrated. | Doc 58 §Cal2 |
| **CREA2** | Multi-Channel Modulation | Supported with dissent | ~ Partial | Pathway A (noise 65–75 dB): d ≈ 0.40. Pathway B (ceiling + dim light): d ≈ 0.38. Pathway C (reduced demand): d ≈ 0.30. Sub-additivity: acute ~75–80%, sustained ~85–90% of additive. Formula: d_combined = [Σd_i] × (0.75 + 0.10×t/30). **Creativity Goldilocks Ceiling: d ≈ 0.75–0.80.** Two-pathway optimum: d ≈ 0.55–0.65. Convergent tradeoff per pathway quantified. | Doc 58 §Cal1 |
| **CREA3** | Incubation Architecture | Supported-preliminary | ~ Partial | Walk duration peak: 10–15 min. Indoor treadmill d ≈ 0.55–0.60; outdoor with nature d ≈ 0.70–0.78. Threshold spacing: 1 moderate per 50–100m (meta-awareness cycling). Post-walk persistence: 6–10 min. Evaluative workspace within 2-min walk. | Doc 58 §Cal3 |

**Calibration change**: CREA1 ✗→~; CREA2 ✗→~; CREA3 ✗→~. All three CREA templates now ~ Partially calibrated.

**Individual difference moderation**: Low-creativity individuals benefit 1.3–1.6× more from environmental creativity support (equity finding).

### Updated Priority Queue (V1.5)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **TP-III** | Empirical validation of TP-II estimates (VR channel study, fractal surface measurement, gait validation) | A10 deepening | Doc 56 |
| 2 | **SOC-III** | Multicultural design parameters, privacy mechanism dose-response, healthcare | A8 deepening | Doc 57 |
| 3 | **CREA-III** | Run 2×2×2 factorial, sustained creative work study, collaborative creativity | A9 deepening + CREA4 | Doc 58 |
| 4 | **Aging & Architecture** | Age moderators across 10+ templates (TP1, SOC1, MAT1, L2, CREA) | Cross-cutting | All calibrated panels |
| 5 | **Child Development** | Developmental moderators, school design | Cross-cutting | Docs 47, 42 |
| 6 | **VIEW-II** | Channel weights, synthetic nature, blue space | VIEW1 calibration | Doc 47 |

### Calibration Status Summary (V1.5)

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial | Doc 49 (L-II) |
| MAT1–MAT5 | ~ Partial | Doc 51 (MAT-II) |
| TP1–TP4 | ~ Partial | Doc 56 (TP-II) |
| SOC1–SOC3 | ~ Partial / ✓ Good | Doc 57 (SOC-II) |
| **CREA1–CREA3** | **~ Partial** | **Doc 58 (CREA-II)** |
| SC1–SC4 | ✗ Uncalibrated | Awaiting SC-II |
| VF1–VF3 | ✗ Uncalibrated | Awaiting VF-II |
| VIEW1 | ✗ Uncalibrated | Awaiting VIEW-II |
| COL1–COL2 | ✗ Uncalibrated | Awaiting COL-II |
| OLF1 | ✗ Uncalibrated | — |

**Six of nine template series now calibrated (L, MAT, TP, SOC, CREA, VIEW). Three remain uncalibrated (SC, VF, COL/OLF).**

### CREA-II Cross-Template Encoding Patterns

**Creativity Goldilocks Ceiling**: Any workspace assessment should compute total environmental creativity dose d_combined and flag when d > 0.75 (diminishing returns) or d > 0.85 (likely counterproductive — excessive abstraction, severe convergent tradeoff).

**Phase-Environment Tagging**: Extend `creative_phase_affinity` with phase-specific d values from the phase-environment matrix. Encoding agents should tag environmental features with `{phase_1_d: number, phase_2_d: number, phase_3_d: number}`.

**Incubation Path Specification**: Templates involving walking paths (TP1, TP2, CREA3, SC3) should include `incubation_suitability` metadata: `{duration_min: 10–15, threshold_spacing_m: 50–100, nature_content: boolean, post_walk_proximity_min: 2}`.

**Individual Difference Multiplier**: All CREA parameters should carry `baseline_creativity_multiplier: {low: 1.4–1.6, medium: 1.0, high: 0.6–0.8}` to enable equity-aware design assessment.

### ADDENDUM (V1.6): VIEW-II Nature View Calibration Data (from Doc 59)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **VIEW1** | Nature View Convergence | Supported | ~ Partial + ✓ Good (VQI) | Channel weights: Ch1 fractal 0.18, Ch2 prospect 0.18, Ch3 restoration 0.24, Ch4 temporal 0.10, Ch5 safety 0.30. Gated model: Ch5_gate × Σ(w_1–4 × Ch_1–4) + w_5 × Ch5_direct; gate range 0.2–1.2. Super-additivity ~15–20% at full engagement. Synthetic hierarchy: real window 1.00, courtyard 0.81–0.85, video 0.52, VR 0.54, living wall 0.37, photo 0.24. Blue bonus +15–20%. VQI 0–100 with 5-channel rubric. Temporal accumulation: Cumulative ≈ Acute × Exposure_hrs. | Doc 59 §Cal1–3 |

**Calibration change**: VIEW1 ✗ → ~ Partial (channel weights, synthetic hierarchy) + ✓ Good (VQI translation).

### Updated Priority Queue (V1.6)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **TP-III** | Empirical validation of TP-II estimates | A10 deepening | Doc 56 |
| 2 | **SOC-III** | Multicultural design, healthcare application | A8 deepening | Doc 57 |
| 3 | **CREA-III** | 2×2×2 factorial, collaborative creativity (CREA4) | A9 deepening | Doc 58 |
| 4 | **VIEW-III** | Channel degradation experiment, VQI validation | VIEW1 deepening | Doc 59 |
| 5 | **Aging & Architecture** | Cross-cutting age moderators | All domains | All calibrated panels |
| 6 | **Child Development** | Developmental moderators, school design | Cross-cutting | Docs 47, 42 |

### Calibration Status Summary (V1.6)

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial | Doc 49 (L-II) |
| MAT1–MAT5 | ~ Partial | Doc 51 (MAT-II) |
| TP1–TP4 | ~ Partial | Doc 56 (TP-II) |
| SOC1–SOC3 | ~ Partial / ✓ Good | Doc 57 (SOC-II) |
| CREA1–CREA3 | ~ Partial | Doc 58 (CREA-II) |
| **VIEW1** | **~ Partial + ✓ Good (VQI)** | **Doc 59 (VIEW-II)** |
| SC1–SC4 | ✗ Uncalibrated | Awaiting SC-II |
| VF1–VF3 | ✗ Uncalibrated | Awaiting VF-II |
| COL1–COL2 | ✗ Uncalibrated | Awaiting COL-II |
| OLF1 | ✗ Uncalibrated | — |

**Six of nine template series now calibrated (L, MAT, TP, SOC, CREA, VIEW). Three remain uncalibrated (SC, VF, COL/OLF).**

### VIEW-II Cross-Template Encoding Patterns

**View Quality Index**: All templates involving window views or nature access should include `vqi_score: number` (0–100) and `vqi_channel_scores: {ch1: number, ch2: number, ch3: number, ch4: number, ch5: number}`. Encoding agents should compute VQI from the five-channel rubric.

**Synthetic Nature Efficacy**: Templates involving nature-substitute interventions (living walls, video nature, VR nature, photographs) should include `synthetic_efficacy: number` (fraction of real-window benchmark) and `cumulative_benefit_hours: number` (efficacy × exposure hours).

**Channel 5 Gating**: All multi-channel convergence templates (L3, MAT4, VIEW1) should include `ecological_safety_gate: number` (0.2–1.2) to model the amplification/suppression effect of ecological context on other channels.

**Blue-Space Bonus**: Views including water should carry `blue_space_present: boolean` and `blue_bonus_multiplier: 1.15–1.20` applied to the base VQI.

### ADDENDUM (V1.7): AGE-I Cross-Cutting Age Moderation (from Doc 60)

**Panel type**: Cross-cutting moderation (not a template-series calibration).

AGE-I provides age moderation parameters for all six calibrated template series. Key deliverables:

| Component | Description | Source |
|-----------|-------------|--------|
| Processing speed multiplier | 1.00 (20s) → 0.55 (80s), per-decade curve | Doc 60 §Salthouse |
| Sensory cascade model | Vulnerability = Speed × Vision × Hearing × Motor × Olfaction (multiplicative) | Doc 60 §Cascade |
| Universal design thresholds | 16 parameters across light, acoustic, surface, visual, wayfinding, social domains | Doc 60 §Thresholds |
| Challenge gradient principle | Universal floors + optional challenge layers for active aging | Doc 60 §Debate2 |
| VIEW1 Ch3 age amplification | Nature restoration benefit INCREASES 20-30% for older adults | Doc 60 §VIEW |
| CREA3 age limitation | Walking incubation restricted to smooth surfaces for 65+; minimal for frail 80+ | Doc 60 §CREA |

**Age bands used throughout**: Young (20-40), Middle (40-65), Older (65-80), Frail (80+).

### Updated Priority Queue (V1.7)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **Child Development** | Developmental moderators, school design, full lifespan model with AGE-I | Cross-cutting | Docs 47, 42, 60 |
| 2 | **TP-III** | Empirical validation of TP-II estimates | A10 deepening | Doc 56 |
| 3 | **SOC-III** | Multicultural design, healthcare, digital-physical privacy | A8 deepening | Doc 57 |
| 4 | **CREA-III** | 2×2×2 factorial, collaborative creativity (CREA4) | A9 deepening | Doc 58 |
| 5 | **VIEW-III** | Channel degradation experiment, VQI validation | VIEW1 deepening | Doc 59 |
| 6 | **AGE-II** | Dementia-specific parameters, cascade model validation | Cross-cutting | Doc 60 |

### Calibration Status Summary (V1.7)

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial + age moderation | Doc 49, Doc 60 |
| MAT1–MAT5 | ~ Partial + age moderation | Doc 51, Doc 60 |
| TP1–TP4 | ~ Partial + age moderation | Doc 56, Doc 60 |
| SOC1–SOC3 | ~ Partial / ✓ Good + age moderation | Doc 57, Doc 60 |
| CREA1–CREA3 | ~ Partial + age moderation | Doc 58, Doc 60 |
| VIEW1 | ~ Partial / ✓ Good (VQI) + age moderation | Doc 59, Doc 60 |
| SC1–SC4 | ✗ Uncalibrated | — |
| VF1–VF3 | ✗ Uncalibrated | — |
| COL1–COL2, OLF1 | ✗ Uncalibrated | — |

**Six of nine template series now calibrated with cross-cutting age moderation.**

### AGE-I Cross-Template Encoding Patterns

**Age Band Metadata**: ALL templates should carry `age_band_modifiers: {young: {...}, middle: {...}, older: {...}, frail: {...}}` with parameter-specific multipliers from Doc 60.

**Sensory Cascade Index**: Templates involving multi-sensory assessment should compute `vulnerability_index: number` (0.0–1.0) as the product of sensory channel integrities. Flag when index < 0.20 (severe vulnerability).

**Universal Design Threshold Check**: Any template-generated design recommendation should be checked against the 16-parameter universal design threshold table. Flag when a recommendation would fail the 10th-percentile community-dwelling 75+ adult.

**Challenge Gradient Encoding**: Templates should distinguish `minimum_threshold` (universal design floor) from `optimal_challenge` (active aging target). Both should be encoded, with a `challenge_gradient_available: boolean` flag.

### ADDENDUM (V1.8): DEV-I Child Development Moderation (from Doc 61)

**Panel type**: Cross-cutting moderation (developmental lifespan complement to AGE-I).

DEV-I provides developmental moderation parameters for six calibrated template series. Key deliverables:

| Component | Description | Source |
|-----------|-------------|--------|
| Executive function maturation | Prefrontal development timeline 3–25; age-specific EF capacity | Doc 61 §Diamond |
| Nature restoration amplification | VIEW1 Ch3 multiplier: 1.5× (age 3–6) to 1.0× (adult) | Doc 61 §Kuo |
| Motor development trajectory | MFI baseline: 0.50 (toddler) → 0.95 (adult); inverse of AGE-I | Doc 61 §Adolph |
| School design parameters | 11 parameters for primary/upper/secondary (HEAD study basis) | Doc 61 §Barrett |
| Lifespan U-curve | PE sensitivity highest at extremes (children + elderly) | Doc 61 §Synthesis |
| Sensitive periods | 6 domains with critical windows for environmental influence | Doc 61 §Maurer |

**Lifespan U-curve**: High sensitivity (0–12) → Low (25–50) → Rising again (65+). Combined DEV-I + AGE-I.

### Updated Priority Queue (V1.8)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **SOC-III** | Multicultural design, healthcare, digital-physical privacy | A8 deepening | Doc 57 |
| 2 | **CREA-III** | 2×2×2 factorial, collaborative creativity (CREA4) | A9 deepening | Doc 58 |
| 3 | **VIEW-III** | Channel degradation experiment, VQI validation | VIEW1 deepening | Doc 59 |
| 4 | **AGE-II** | Dementia-specific parameters, cascade model validation | Cross-cutting | Doc 60 |
| 5 | **DEV-II** | ADHD-specific parameters, lifespan U-curve validation, adolescent risk | Cross-cutting | Doc 61 |
| 6 | **TP-III** | Empirical validation (VR channel study, fractal measurement, gait) | A10 deepening | Doc 56 |

### DEV-I Cross-Template Encoding Patterns

**Age Band Metadata (Development)**: All templates should extend `age_band_modifiers` with developmental bands: `{toddler_1_3: {...}, preschool_3_6: {...}, primary_6_9: {...}, upper_9_12: {...}, adolescent_12_16: {...}, emerging_adult_16_25: {...}}`.

**Lifespan PE Sensitivity**: Templates should include `lifespan_sensitivity_multiplier` computed from the U-curve: high at developmental extremes, lowest at 25–50.

**Inverse Challenge Principle**: For child populations, templates should encode `developmental_challenge_benefit: boolean` — the inverse of AGE-I's protective principle. Motor challenge, spatial complexity, and environmental novelty BUILD developing capacity rather than threatening declining capacity.

**School Design Mode**: When `context: "school"` and `age_band: "primary" | "upper" | "secondary"`, templates should apply the 11-parameter classroom design specifications from Doc 61.

### ADDENDUM (V1.9): SC-II Spatial Configuration Calibration (from Doc 62)

| Template | Name | Maturity | Calibration | Key Parameters | Source |
|----------|------|----------|-------------|----------------|--------|
| **SC1** | Spatial Integration PE | Supported | ✓ Good | Integration → valence: V ≈ 2.5 + 3.5×integration_norm (r=0.55, R²~0.50 combined). Vertical PE multiplier: 1.5–2.5× per floor (enclosed stair 2.0×, elevator 2.5×). Atrium mitigation: 30–50% reduction. Multi-story weighting: 1 floor ≈ 3–5 horizontal turns. | Doc 62 §Cal2–3 |
| **SC2** | Isovist Dynamics | Supported | ~ Partial | Isovist contrast → GSR: 0.30×ln(area_ratio) + C_multimodal. C_multimodal: spatial only +0.00, +light +0.25, +light+material +0.40, full convergence +0.70. | Doc 62 §Cal1 |
| **SC3** | Architectural Promenade | Supported | ~ Partial | Threshold density Goldilocks: 1 per 20–45s walking (25–55m). Compression-release optimal ratio 1:3 to 1:8. Compositional shape: approach 15–20%, development 30–40%, climax 10–15%, denouement 20–30%. | Doc 62 §Cal1 |
| **SC4** | Social Encounter | Supported | ✓ Good | Unchanged — already well-calibrated via Space Syntax. | Doc 38 |

**Calibration change**: SC1 ✓→✓+ (emotion + 3D); SC2 ~→~ (improved); SC3 ✗→~; SC4 ✓ unchanged.

### Updated Priority Queue (V1.9)

| Priority | Panel | What It Delivers | Impact | Prerequisite Docs |
|----------|-------|-----------------|--------|-------------------|
| 1 | **COL-II** | COL1–2 hue×context matrix, arousal dose-response | A6 color calibration | Doc 45 |
| 2 | **SOC-III** | Multicultural design, healthcare, digital-physical privacy | A8 deepening | Doc 57 |
| 3 | **CREA-III** | 2×2×2 factorial, collaborative creativity (CREA4) | A9 deepening | Doc 58 |
| 4 | **SC-III** | Urban-scale, compositional shape validation | A3 deepening | Doc 62 |
| 5 | **AGE-II** | Dementia-specific, cascade validation | Cross-cutting | Doc 60 |
| 6 | **DEV-II** | ADHD parameters, U-curve validation | Cross-cutting | Doc 61 |

### Calibration Status Summary (V1.9)

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial | Doc 49 |
| MAT1–MAT5 | ~ Partial | Doc 51 |
| TP1–TP4 | ~ Partial | Doc 56 |
| SOC1–SOC3 | ~ Partial / ✓ Good | Doc 57 |
| CREA1–CREA3 | ~ Partial | Doc 58 |
| VIEW1 | ~ Partial / ✓ Good (VQI) | Doc 59 |
| **SC1–SC4** | **~ Partial / ✓ Good** | **Doc 62** |
| VF1–VF3 | ✗ Uncalibrated | — |
| COL1–COL2, OLF1 | ✗ Uncalibrated | — |

**Eight of nine template series now calibrated. One remains: VF (Visual Form). OLF1 also uncalibrated.**

### SC-II Cross-Template Encoding Patterns

**Integration-Valence Prediction**: All templates involving spatial navigation should include `integration_normalized: number` (0–1) and compute predicted valence via V ≈ 2.5 + 3.5×integration_norm.

**Vertical PE Multiplier**: Multi-story transitions should carry `vertical_pe_multiplier: number` (1.0 for same floor; 1.5–2.5 per floor) with `atrium_mitigation: number` (0.5–1.0).

**Promenade Scoring**: Templates involving spatial sequences (SC3, TP2, CREA3) should include `threshold_interval_s: number` and flag when outside the 20–45s Goldilocks range. Compression-release ratio should be computed from consecutive isovist areas.

### ADDENDUM (V2.0): COL-II Color Calibration (from Doc 63)

| Template | Calibration | Key Parameters | Source |
|----------|-------------|----------------|--------|
| **COL1** | ~ Partial / ✓ Good (translation) | Three-source formula: PE = 0.40×eco + 0.45×ctx + 0.15×reg. Hue×context d matrix (8 hues × 5 contexts). Cultural modifiers (5 clusters). Categorical boundary bonus: ×(1 + 0.5×n_crossings). | Doc 63 §Cal |
| **COL2** | ~ Partial / ✓ Good (translation) | Arousal = (0.30S + 0.20B + 0.10H_w) × Area × e^(−t/τ). Habituation τ: immersive 3h arousal / 2wk hedonic; threshold accent 2–3d / 8+wk. Context arousal targets (5 contexts). Kruithof light×color matrix. | Doc 63 §Cal |

**Eight of nine template series now calibrated.**

### COL-II Cross-Template Encoding Patterns

**Hue-Context Lookup**: Templates involving colored surfaces should include `hue_category` and `context_type`, then look up predicted d from the 8×5 matrix. Cultural modifier applied when `cultural_cluster` is specified.

**Arousal Budget**: Templates should compute `color_arousal_shift` from the Valdez formula and compare against `target_arousal` for the context. Flag when |shift − target| > 0.20.

**Habituation Decay**: For sustained-occupancy templates, apply `habituation_factor: e^(−t/τ)` based on color configuration. Threshold-accent configurations should be flagged as habituation-resistant.

**Categorical Boundary at Thresholds**: When a spatial threshold (TP2/SC3) also involves a color category change, add +1 to the channel count for boundary strength calculation.
