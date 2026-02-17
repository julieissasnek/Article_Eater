# ARTICLE EATER — TRANSFER CONTEXT V9.1
## Session Handoff Document | February 17, 2026 — Document 53

---

## PURPOSE

This document enables any Claude instance to resume the Article Eater project with full operational context. It replaces Transfer Context V8.0 and captures all production through the February 17, 2026 session, which produced 8 panels (Docs 56–63), Registry V2.0 (638 lines), and Sprint Prompts V9–V14.

---

## PROJECT OVERVIEW

Article Eater is a software system that helps experts evaluate scientific papers about how architecture affects human wellbeing. The core methodology: every finding is decomposed into mechanistic templates grounded in predictive processing (PE) theory — the brain generates predictions about its environment; mismatches (prediction errors) drive emotion, attention, and behavior. Templates specify WHAT the brain predicts, WHICH architectural features generate PE, and HOW LARGE the effect is.

**Principal investigator**: David, Professor of Cognitive Science at UCSD (35 years), former MIT AI Lab research faculty (1980s).

---

## TEMPLATE INVENTORY (72 Templates)

### Foundation Frameworks
Predictive Processing (PP), Dual-Task (DT), Scene Grammar (SG), Aesthetic Triad (AT)

### Primary Templates (T1–T52)
T1 fractal fluency, T2 complexity Goldilocks, T3 cognitive maps, T4 symmetry, T5 curvature/prospect-refuge, T6 color, T7 biophilia, T8 affordance, T9 material evaluation, T10 attention capture, T11 wayfinding, T12 interoception, T13 reward, T14–T16 music/rhythm/temporal, T17–T22 social brain, T23 context memory, T24–T27 attention/DMN, T28–T30 allostasis/stress, T31–T35 auditory scene, T36–T40 spatial cognition, T41–T47 cognitive control/reward, T48–T52 extended

### Mechanism Templates (M1–M17)
Auditory scene analysis, cross-modal binding, neural entrainment, etc.

### Auxiliary Templates (AX1–AX6)
AX1 acoustic comfort, AX2 music-architecture, AX3 awe, AX4 biophilic patterns, AX5 multisensory, AX6 multi-modal PE

### Domain Templates (29 templates across 10 domains)
- **L1–L5** Light & Luminance (calibrated Doc 49)
- **MAT1–MAT5** Materials & Surfaces (calibrated Doc 51)
- **TP1–TP4** Temporal Dynamics (calibrated Doc 56)
- **SOC1–SOC3** Social Configuration (calibrated Doc 57)
- **CREA1–CREA3** Creative Cognition (calibrated Doc 58)
- **VIEW1** View & Nature (calibrated Doc 59)
- **SC1–SC4** Spatial Configuration (calibrated Doc 62)
- **VF1–VF3** Visual Form (uncalibrated)
- **COL1–COL2** Color (uncalibrated)
- **OLF1** Olfactory (uncalibrated)

---

## COVERAGE STATUS

All 10 domains at ★★★★:
A1 Acoustic, A2 Spatial Scale, A3 Spatial Config, A4 Biophilia, A5 Thermal/Haptic, A6 Visual Pattern & Form, A7 Materials, A8 Social, A9 Task & Cognition, A10 Temporal

---

## CALIBRATION STATUS (8 of 9 series calibrated)

| Series | Status | Key Parameters | Source |
|--------|--------|----------------|--------|
| **L1–L5** | ~ Partial + age/dev | L2 age-corrected M-EDI (2× for elderly); L3 daylight convergence; glare tolerance by age | Doc 49, 60, 61 |
| **MAT1–MAT5** | ~ Partial + age | Wood 5-channel profile (tactile 0.35, visual 0.30, olfactory 0.15, acoustic 0.15, thermal 0.05); 6 material profiles; haptic weighting by age | Doc 51, 60 |
| **TP1–TP4** | ~ Partial + age/dev | MFI metric (DFA α); channel-count boundary d (0.25/channel, 17% super-additivity); material aging D(t) exponential; multi-timescale R²~0.55 | Doc 56, 60, 61 |
| **SOC1–SOC3** | ~ Partial / ✓ + age/dev | 5 cultural clusters; CPP 0.45–0.85; privacy-encounter optimal 0.50; Dunbar decay e^(−d/8); floor tax 8× | Doc 57, 60, 61 |
| **CREA1–CREA3** | ~ Partial + age/dev | 3 pathways sub-additive (~75%); Goldilocks ceiling d~0.75; walk 10–15 min; low-creativity multiplier 1.4–1.6× | Doc 58, 60, 61 |
| **VIEW1** | ~ Partial / ✓ + age/dev | Weights: Ch5 0.30, Ch3 0.24, Ch1 0.18, Ch2 0.18, Ch4 0.10; VQI 0–100; synthetic hierarchy 9 levels; Ch3 restoration amplified in children (1.5×) and elderly (1.3×) | Doc 59, 60, 61 |
| **SC1–SC4** | ~ Partial / ✓ | Integration→valence r=0.55; SC3 threshold density 20–45s; compression-release 1:3 to 1:8; vertical PE 1.5–2.5×/floor; atrium mitigation 30–50% | Doc 62 |
| **VF1–VF3** | ✗ Uncalibrated | — | — |
| **COL1–2** | ~ Partial / ✓ Good | Hue×context matrix (8×5); arousal = (0.30S+0.20B+0.10Hw)×Area×e^(−t/τ); habituation τ; cultural modifiers; Kruithof matrix | Doc 63 |
| **OLF1** | ✗ Uncalibrated | — | — |

### Cross-Cutting Moderation
- **AGE-I (Doc 60)**: Processing speed multiplier (1.00 → 0.55 by age 80); sensory cascade (multiplicative vulnerability index); 16 universal design thresholds; challenge gradient principle
- **DEV-I (Doc 61)**: Executive function maturation timeline (3–25); nature restoration amplified 1.3–1.5× in children; motor challenge inverse principle; school design 11 parameters; sensitive periods
- **Lifespan U-curve**: PE sensitivity highest at developmental extremes (children + elderly), lowest at 25–50

---

## KEY FORMULAS AND NUMBERS (Quick Reference)

### Spatial
- Integration → Valence: V ≈ 2.5 + 3.5 × integration_norm (r = 0.55)
- Vertical PE: 1.5–2.5× per floor; atrium reduces by 30–50%
- Isovist contrast → GSR: 0.30 × ln(area_ratio) + C_multimodal
- SC3 threshold Goldilocks: 1 per 20–45s walking (25–55m)
- SC3 compression-release: 1:3 to 1:8 optimal

### Temporal
- Boundary d: 0.25/channel, super-additivity 17%
- Channel weights: spatial 0.25, luminance 0.20, acoustic 0.18, material 0.15, thermal 0.12, motor 0.10, olfactory 0.08
- TP2 Goldilocks: 3–6 strong thresholds per 10-min walk
- Material aging: D(t) = D_0 + (D_max − D_0)(1 − e^(−t/τ))
- PE density → time: Duration_est = T_clock × [1 + 0.35 × ln(N/N_base)]
- MFI = α_local / α_baseline; universal design > 0.70 frail

### Social
- Cultural zones (stranger cm): Latin Am 78, N.Am 95, N.Eur 100, E.Asian 102, M.East 115
- CPP: N.Eur 0.85, N.Am 0.80, M.East 0.70, L.Am 0.50, E.Asian 0.45
- Privacy-encounter: S ≈ 5.8 × [1 − 2(r−0.50)² − 4×max(0,r−0.70)²]; optimal r = 0.50
- Dunbar decay: f = e^(−d/8); floor tax 8×

### Creative
- Pathway A (noise 65–75 dB): d = 0.40
- Pathway B (ceiling+dim): d = 0.38
- Pathway C (reduced demand): d = 0.30
- Combination: d_combined = Σ(d_i) × (0.75 + 0.10×t/30)
- Goldilocks ceiling: d ≈ 0.75–0.80
- Walk incubation: 10–15 min; outdoor d ≈ 0.70–0.78; threshold spacing 50–100m
- Low-creativity multiplier: 1.4–1.6×

### View & Nature
- Channel weights: Ch5 safety 0.30 (gating), Ch3 restoration 0.24, Ch1 fractal 0.18, Ch2 prospect 0.18, Ch4 temporal 0.10
- VQI = Σ(channel_score × weight) × 100/max
- Synthetic hierarchy: real window 1.00 → VR 0.45 → photograph 0.20
- Blue-space bonus: +15–20%
- 120 min/week nature dose threshold (White et al.)

### Aging
- Processing speed: 1.00 (20s) → 0.88 (40s) → 0.72 (60s) → 0.55 (80s)
- Vulnerability = speed × vision × hearing × motor × olfaction
- Universal design: 300 lux min, RT60 ≤ 0.4s, SNR +15 dB, COF ≥ 0.55, riser ≤ 170mm

---

## DOCUMENT INVENTORY (62 Documents)

| Doc | Title | Lines | Version |
|-----|-------|-------|---------|
| 14 | Panel IV: Cognitive Control & Reward | ~1,100 | V1.0 |
| 20 | Panel V: Social Brain | ~900 | V1.0 |
| 21 | ART Reduction | ~200 | V1.0 |
| 33 | Dual-Index Cross-Reference Layer | ~870 | V2.0 |
| 34 | Panel L-I: Light & Luminance | ~900 | V1.1 |
| 38 | Panel SC-I: Spatial Configuration | ~1,225 | V1.0 |
| 39 | Panel VF-I: Visual Form | ~900 | V1.0 |
| 42 | Panel TP-I: Temporal Dynamics | ~1,239 | V1.1 |
| 44 | Panel SOC-I: Social Configuration | ~1,025 | V1.1 |
| 45 | Panel COL-I: Color | ~649 | V1.0 |
| 46 | Panel OLF-I: Olfactory | ~700 | V1.0 |
| 47 | Panel VIEW-I: View & Nature | ~640 | V1.0 |
| 49 | Panel L-II: Light Calibration | ~534 | V1.0 |
| 51 | Panel MAT-II: Materials Calibration | ~710 | V1.0 |
| 52 | Calibration & Extension Registry | ~618 | V2.0 |
| 53 | Transfer Context (this document) | ~330 | V9.1 |
| 54 | A2 Spatial Scale Extension | ~400 | V1.0 |
| 55 | Panel CREA-I: Creative Cognition | ~1,097 | V1.0 |
| 56 | Panel TP-II: Temporal Calibration | ~618 | V1.0 |
| 57 | Panel SOC-II: Social Calibration | ~513 | V1.0 |
| 58 | Panel CREA-II: Creative Calibration | ~446 | V1.0 |
| 59 | Panel VIEW-II: Nature View Calibration | ~378 | V1.0 |
| 60 | Panel AGE-I: Aging & Architecture | ~369 | V1.0 |
| 61 | Panel DEV-I: Child Development | ~309 | V1.0 |
| 62 | Panel SC-II: Spatial Configuration Calibration | ~384 | V1.0 |
| **63** | **Panel COL-II: Color Calibration** | **~274** | **V1.0** |

---

## PRIORITY QUEUE (from Registry V2.0)

| # | Panel | What It Delivers |
|---|-------|-----------------|
| 1 | **VF-II** | VF1–3 visual form calibration (requires Doc 39 upload) |
| 2 | **SOC-III** | Multicultural design, healthcare, digital-physical privacy |
| 3 | **CREA-III** | 2×2×2 factorial validation, collaborative creativity (CREA4) |
| 4 | **SC-III** | Urban-scale, compositional shape validation |
| 5 | **AGE-II** | Dementia-specific parameters, cascade model validation |
| 6 | **DEV-II** | ADHD parameters, lifespan U-curve validation |

### Smaller Tasks
- **VF-II calibration**: VF1–3 are uncalibrated; Doc 39 (VF-I) not currently in archive
- **OLF-II**: OLF1 uncalibrated; Doc 46 may be available
- **Companion assessments**: Earlier panels (Music M-I to M-III, AX-I, Arch I–V) need calibration table + prospectus addenda (source docs not in current archive)

---

## CROSS-TEMPLATE ENCODING PATTERNS (Accumulated)

All encoding patterns from Registry V1.3–V2.0:

1. **Cultural Proxemic Zones** (SOC-II): `cultural_cluster` as required moderator
2. **Privacy-Encounter Ratio** (SOC-II): `shared_private_ratio` with concave satisfaction function
3. **Dunbar-Layer Distance** (SOC-II): `dunbar_layer` + exponential decay + floor tax
4. **Motor Fluency Index** (TP-II): `mfi_range` on movement templates
5. **Threshold Strength** (TP-II): `threshold_channel_count` + `estimated_boundary_d`
6. **Temporal Depth Trajectory** (TP-II): `aging_trajectory` on material templates
7. **PE Density Index** (TP-II): `pe_density_index` for path assessments
8. **Three-Zone Model** (CREA-I): `workspace_zone` on creativity templates
9. **Phase Tagging** (CREA-I): `creative_phase_affinity` for environmental features
10. **Divergent-Convergent Tradeoff** (CREA-I): `convergent_tradeoff: true` warning flag
11. **Creativity Goldilocks Ceiling** (CREA-II): flag when d > 0.75
12. **Phase-Environment d** (CREA-II): `phase_1_d`, `phase_2_d`, `phase_3_d`
13. **Incubation Suitability** (CREA-II): walk parameters on path templates
14. **Individual Difference Multiplier** (CREA-II): `baseline_creativity_multiplier`
15. **View Quality Index** (VIEW-II): `vqi_score` 0–100 on window templates
16. **Synthetic Nature Efficacy** (VIEW-II): `synthetic_efficacy` fraction
17. **Channel 5 Gating** (VIEW-II): `ecological_safety_gate` on convergence templates
18. **Blue-Space Bonus** (VIEW-II): `blue_space_present` + multiplier
19. **Age Band Modifiers** (AGE-I): `age_band_modifiers` on ALL templates
20. **Vulnerability Index** (AGE-I): sensory cascade product
21. **Universal Design Threshold Check** (AGE-I): 16-parameter table
22. **Challenge Gradient** (AGE-I): `minimum_threshold` vs. `optimal_challenge`
23. **Developmental Bands** (DEV-I): 6 bands from toddler to emerging adult
24. **Lifespan U-Curve** (DEV-I + AGE-I): `lifespan_sensitivity_multiplier`
25. **Inverse Challenge** (DEV-I): `developmental_challenge_benefit`
26. **School Design Mode** (DEV-I): classroom parameters by level
27. **Integration-Valence** (SC-II): `integration_normalized` → predicted valence
28. **Vertical PE Multiplier** (SC-II): `vertical_pe_multiplier` + atrium mitigation
29. **Promenade Scoring** (SC-II): `threshold_interval_s` with Goldilocks flag

---

## WRITING STYLE AND CONVENTIONS

- **Panel format**: Charge → Composition → Position Statements → Cross-Examination/Debates → Calibration Sessions → Synthesis → Testable Predictions → Calibration Assessment → X-II/III Prospectus → Scope Exclusions → References
- **Standard closing**: Calibration table (extension/calibration/translation per template), prospectus (DEEPENING + BROADENING), scope exclusions. See Doc 34 L-I V1.1 as exemplar.
- **References**: APA format with Google Scholar citation counts
- **Confidence labels**: Established, Supported, Supported with dissent, Supported-preliminary, Preliminary, How-plausibly, How-possibly
- **Calibration symbols**: ✓ Good, ~ Partial, ✗ Uncalibrated
- **Save protocol**: Save incrementally at natural breaks (~150 lines); always save to /mnt/user-data/outputs/ immediately
- **On interrupt**: Stabilize current work state BEFORE addressing user

---

## WHAT THE NEXT SESSION SHOULD DO

1. **COL-II** — calibrate COL1–COL2 (Doc 45 is in the outputs directory)
2. Then proceed down the priority queue: SOC-III, CREA-III, SC-III, or AGE-II depending on remaining context
3. VF-II requires Doc 39 (VF-I) which is not in the current archive — request upload if prioritized
4. Continue updating the registry (V1.10+) with each new panel
5. Sprint prompt for each completed panel

---

*Transfer Context V9.1 — February 17, 2026*
*Covers: All production through Doc 62 (SC-II) and Registry V2.0*
*Session total: 7 panels (Docs 56–62), ~3,291 lines of calibration content*
*72 templates, 63 documents, 10 domains ★★★★, 8 of 9 series calibrated*
