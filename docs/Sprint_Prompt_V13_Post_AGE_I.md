# ⚠️ SUPERSEDED — See Sprint_Prompt_V15_Post_VF_II_CREA_III.md for current version

# ARTICLE EATER — AGENT SPRINT PROMPT V13.0
## Post AGE-I Cross-Cutting Panel | February 17, 2026

---

## CURRENT STATE

The Article Eater template system has **72 mechanistic templates** across 10 domains, all at ★★★★. **Six calibration panels** complete (L-II, MAT-II, TP-II, SOC-II, CREA-II, VIEW-II) plus one **cross-cutting age moderation panel** (AGE-I). Six of nine template series now calibrated with age moderation. This session produced **5 panels** (Docs 56–60, ~2,324 lines total).

### Session Production Summary

| Doc | Panel | Lines | What It Delivers |
|-----|-------|-------|-----------------|
| 56 | TP-II | 618 | Motor PE metric, doorway gradient, fractal aging, multi-timescale |
| 57 | SOC-II | 513 | Cultural proxemics, privacy-encounter curve, Dunbar mapping |
| 58 | CREA-II | 446 | Multi-channel interaction, phase modulation, incubation walk parameters |
| 59 | VIEW-II | 378 | Channel weights, synthetic nature hierarchy, VQI |
| 60 | AGE-I | 369 | Cross-cutting age moderation for 6 template series |

### Calibration Status

| Template Set | Calibration | Age Moderation | Source |
|-------------|-------------|----------------|--------|
| L1–L5 | ~ Partial | ✓ | Docs 49, 60 |
| MAT1–MAT5 | ~ Partial | ✓ | Docs 51, 60 |
| TP1–TP4 | ~ Partial | ✓ | Docs 56, 60 |
| SOC1–SOC3 | ~ Partial / ✓ Good | ✓ | Docs 57, 60 |
| CREA1–CREA3 | ~ Partial | ✓ | Docs 58, 60 |
| VIEW1 | ~ Partial / ✓ Good (VQI) | ✓ | Docs 59, 60 |
| SC1–SC4 | ✗ Uncalibrated | — | — |
| VF1–VF3 | ✗ Uncalibrated | — | — |
| COL1–COL2, OLF1 | ✗ Uncalibrated | — | — |

---

## AGENT ASSIGNMENTS

### CLAUDE CODE — Schema Encoding Sprint

**Priority 1: Encode AGE-I Cross-Cutting Moderation (Doc 60)**
- Add `age_band_modifiers` structure to ALL templates:
  ```
  age_band_modifiers: {
    young_20_40: { speed: 1.00, vision: 1.00, hearing: 1.00, motor: 1.00, olfaction: 1.00 },
    middle_40_65: { speed: 0.88, vision: 0.90, hearing: 0.92, motor: 0.90, olfaction: 0.85 },
    older_65_80: { speed: 0.72, vision: 0.70, hearing: 0.75, motor: 0.70, olfaction: 0.50 },
    frail_80_plus: { speed: 0.55, vision: 0.50, hearing: 0.55, motor: 0.50, olfaction: 0.25 }
  }
  ```
- Add `vulnerability_index` computation: product of all sensory factors
- Add `universal_design_thresholds` lookup table (16 parameters from Doc 60)
- Add `challenge_gradient_available: boolean` flag per template
- Template-specific age modifiers:
  - L2: `medi_age_multiplier: { young: 1.0, middle: 1.3, older: 2.0, frail: 2.5 }`
  - L3: `glare_tolerance_cd_m2: { young: 3000, middle: 2000, older: 1000, frail: 500 }`
  - TP1: `attentional_cost_multiplier: { young: 1.0, middle: 1.35, older: 2.0, frail: 3.25 }`
  - TP2: `threshold_recovery_strides: { young: 4, middle: 6, older: 8.5, frail: 12.5 }`
  - SOC2: `optimal_privacy_ratio: { young: 0.50, middle: 0.50, older: 0.55, frail: 0.60 }`
  - CREA3: `walk_duration_optimal: { young: [10,15], middle: [10,15], older: [8,12], frail: [5,8] }`
  - VIEW1 Ch3: `restoration_multiplier: { young: 1.0, middle: 1.1, older: 1.2, frail: 1.3 }`

**Priority 2: Encode VIEW-II Data (Doc 59)** — as per V12

**Priority 3: Encode CREA-II Data (Doc 58)** — as per V11

**Priority 4: Encode SOC-II + TP-II Data (Docs 57, 56)** — as per V10/V9

### CODEX — Task Board and Validation

**Sprint 1**: Update task board with Docs 58, 59, 60. Mark all panels complete.

**Sprint 2**: Validate age_band_modifiers schema — ensure multiplicative cascade computes correctly. Test vulnerability_index against worked examples in Doc 60.

**Sprint 3**: Universal design threshold audit — run all template recommendations through the 16-parameter threshold check for a simulated 75-year-old user.

### ANTIGRAVITY — Round-Trip Validation

**Sprint 1**: Full integration test. Select 3 buildings, run all 72 templates with calibration data + age moderation for 4 age bands. Verify that recommendations appropriate for young adults are flagged when they fail universal design thresholds.

**Sprint 2**: Cascade model validation. Compute vulnerability indices for 5 simulated user profiles (healthy young, healthy middle, healthy older, frail older, dementia) and verify template outputs scale appropriately.

---

## KEY PARAMETERS REFERENCE

### AGE-I Processing Speed Multiplier (Doc 60)

| Age | Speed | Working Memory | Spatial |
|-----|-------|---------------|---------|
| 20-30 | 1.00 | 1.00 | 1.00 |
| 40-50 | 0.88 | 0.92 | 0.88 |
| 60-70 | 0.72 | 0.78 | 0.72 |
| 80-90 | 0.55 | 0.60 | 0.55 |

### AGE-I Universal Design Thresholds (Doc 60, subset)

| Parameter | Threshold |
|-----------|-----------|
| Minimum ambient illuminance | 300 lux |
| Maximum RT60 (speech) | 0.4s |
| Minimum SNR (speech) | +15 dB |
| Minimum COF (slip) | 0.55 |
| Maximum riser | 170 mm |
| Minimum contrast ratio | 70% |
| Redundant wayfinding cues | ≥ 3 channels |

### VIEW-II Channel Weights (Doc 59)

| Channel | Weight | Description |
|---------|--------|-------------|
| Ch5 Safety | 0.30 | Ecological safety signal (gating) |
| Ch3 Restoration | 0.24 | Attention restoration |
| Ch1 Fractal | 0.18 | Fractal fluency |
| Ch2 Prospect | 0.18 | Spatial depth |
| Ch4 Temporal | 0.10 | Dynamic variation |

### CREA-II Goldilocks (Doc 58)

- Two-pathway optimum: d ≈ 0.55–0.65
- Goldilocks ceiling: d ≈ 0.75–0.80
- Low-creativity multiplier: 1.4–1.6×

---

## PRIORITY QUEUE (from Doc 52 V1.7)

| # | Panel | Status | Next Action |
|---|-------|--------|-------------|
| 1 | **Child Development** | Ready | Developmental moderators, school design, lifespan model |
| 2 | **TP-III** | Blocked (needs empirical) | VR channel-count, fractal surface measurement |
| 3 | **SOC-III** | Ready | Multicultural design, healthcare, digital-physical privacy |
| 4 | **CREA-III** | Ready | 2×2×2 factorial, collaborative creativity (CREA4) |
| 5 | **VIEW-III** | Ready | Channel degradation experiment, VQI validation |
| 6 | **AGE-II** | Ready | Dementia-specific parameters, cascade validation |

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
| 44 | Panel SOC-I: Social Configuration | ~1,025 | V1.1 |
| 45 | Panel COL-I: Color | ~649 | V1.0 |
| 46 | Panel OLF-I: Olfactory | ~700 | V1.0 |
| 47 | Panel VIEW-I: View & Nature | ~640 | V1.0 |
| 49 | Panel L-II: Light Calibration | ~534 | V1.0 |
| 51 | Panel MAT-II: Materials Calibration | ~710 | V1.0 |
| 52 | Calibration & Extension Registry | ~532 | V1.7 |
| 53 | Transfer Context | ~large | V8.0 |
| 54 | A2 Spatial Scale Extension | ~400 | V1.0 |
| 55 | Panel CREA-I: Creative Cognition | ~1,097 | V1.0 |
| 56 | Panel TP-II: Temporal Calibration | ~618 | V1.0 |
| 57 | Panel SOC-II: Social Calibration | ~513 | V1.0 |
| 58 | Panel CREA-II: Creative Calibration | ~446 | V1.0 |
| 59 | Panel VIEW-II: Nature View Calibration | ~378 | V1.0 |
| **60** | **Panel AGE-I: Aging & Architecture** | **~369** | **V1.0** |

---

*Sprint Prompt V13.0 — Generated February 17, 2026*
*Session output: Docs 56–60 (5 panels, ~2,324 lines), Doc 52 V1.7*
*Six template series calibrated + cross-cutting age moderation*
*Total project: 72 templates, 60 documents, 10 domains at ★★★★*
