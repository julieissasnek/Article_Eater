# ⚠️ SUPERSEDED — See Sprint_Prompt_V15_Post_VF_II_CREA_III.md for current version

# ARTICLE EATER — AGENT SPRINT PROMPT V14.0
## Post DEV-I + AGE-I Cross-Cutting Panels | February 17, 2026

---

## CURRENT STATE

The Article Eater template system has **72 mechanistic templates** across 10 domains at ★★★★. **Six calibration panels** (L-II, MAT-II, TP-II, SOC-II, CREA-II, VIEW-II) plus **two cross-cutting panels** (AGE-I, DEV-I) are complete. Six of nine template series now calibrated with both aging and developmental moderation — a complete lifespan model. This session produced **6 panels** (Docs 56–61, ~2,633 lines).

### Session Production

| Doc | Panel | Lines | Type |
|-----|-------|-------|------|
| 56 | TP-II | 618 | Calibration |
| 57 | SOC-II | 513 | Calibration |
| 58 | CREA-II | 446 | Calibration |
| 59 | VIEW-II | 378 | Calibration |
| 60 | AGE-I | 369 | Cross-cutting |
| 61 | DEV-I | 309 | Cross-cutting |
| 52 | Registry | 571 | V1.8 |

### Calibration + Lifespan Status

| Template Set | Calibration | Age Mod | Dev Mod | Sources |
|-------------|-------------|---------|---------|---------|
| L1–L5 | ~ Partial | ✓ | ✓ | Docs 49, 60, 61 |
| MAT1–MAT5 | ~ Partial | ✓ | — | Docs 51, 60 |
| TP1–TP4 | ~ Partial | ✓ | ✓ | Docs 56, 60, 61 |
| SOC1–SOC3 | ~ Partial / ✓ | ✓ | ✓ | Docs 57, 60, 61 |
| CREA1–CREA3 | ~ Partial | ✓ | ✓ | Docs 58, 60, 61 |
| VIEW1 | ~ Partial / ✓ | ✓ | ✓ | Docs 59, 60, 61 |
| SC1–SC4 | ✗ | — | — | — |
| VF1–VF3 | ✗ | — | — | — |
| COL1–2, OLF1 | ✗ | — | — | — |

---

## AGENT ASSIGNMENTS

### CLAUDE CODE — Schema Encoding Sprint

**Priority 1: Encode DEV-I Developmental Moderation (Doc 61)**
- Extend `age_band_modifiers` with 6 developmental bands (toddler through emerging adult)
- Add `lifespan_sensitivity_multiplier` U-curve computation
- Add `developmental_challenge_benefit: boolean` flag
- Add `context: "school"` mode with 11-parameter classroom specification
- Template-specific developmental modifiers:
  - VIEW1 Ch3: `dev_restoration_multiplier: {age_3_6: 1.5, age_6_9: 1.4, age_9_12: 1.3, age_12_16: 1.15}`
  - TP1: `dev_mfi_baseline: {age_3_6: 0.65, age_6_9: 0.78, age_9_12: 0.87, age_12_16: 0.93}`
  - TP2: `dev_channel_capacity: {age_3_6: 2, age_6_9: 3, age_9_12: 4, age_12_16: "adult"}`
  - SOC1: `dev_personal_space_cm: {age_3_6: 40, age_6_9: 60, age_9_12: 78, age_12_16: 90}`

**Priority 2: Encode AGE-I Data (Doc 60)** — as per V13

**Priority 3: Encode VIEW-II + CREA-II + SOC-II + TP-II** — as per V12/V11/V10/V9

### CODEX — Task Board and Validation

**Sprint 1**: Update task board with Docs 59, 60, 61. All panels complete.

**Sprint 2**: Validate lifespan U-curve computation — ensure developmental and aging multipliers combine correctly at boundary ages (16–25 emerging adult zone).

**Sprint 3**: School design mode audit — verify classroom parameters activate correctly when `context: "school"` is set.

### ANTIGRAVITY — Round-Trip Validation

**Sprint 1**: Lifespan round-trip. Take one building, run all templates for 5 user profiles: child (age 7), adolescent (14), young adult (30), older adult (72), frail elder (85). Verify parameter shifts are consistent across AGE-I and DEV-I.

**Sprint 2**: School assessment. Apply full template suite to 3 classroom designs (excellent, average, poor per HEAD criteria). Verify developmental modifiers produce appropriate sensitivity amplification.

---

## KEY PARAMETERS (NEW in V14)

### DEV-I Lifespan U-Curve

| Age | PE Sensitivity | Mechanism |
|-----|---------------|-----------|
| 0–6 | HIGH | Developing systems, sensitive periods |
| 6–12 | MOD-HIGH | Growing capacity, high learning stakes |
| 12–25 | MODERATE | Approaching adult, prefrontal still maturing |
| 25–50 | LOW (reference) | Peak capacity |
| 50–65 | MODERATE | Beginning decline |
| 65–80 | MOD-HIGH | Cascade multiplicative |
| 80+ | HIGH | Minimal safety margin |

### DEV-I Inverse Challenge Principle

Where AGE-I says: reduce challenge → protect declining capacity
DEV-I says: provide challenge → build developing capacity
Both agree: GRADED challenge, never overwhelming

### School Design Quick Reference (Primary 5–9)

| Parameter | Value |
|-----------|-------|
| Daylight | VQI > 50 |
| Illuminance | 300–500 lux |
| RT60 | ≤ 0.4s |
| Background noise | ≤ 35 dBA |
| Nature view | Essential |
| Movement break | Every 15–20 min |

---

## PRIORITY QUEUE (Doc 52 V1.8)

| # | Panel | Status | Next Action |
|---|-------|--------|-------------|
| 1 | **SOC-III** | Ready | Multicultural design, healthcare, digital-physical privacy |
| 2 | **CREA-III** | Ready | 2×2×2 factorial, collaborative creativity (CREA4) |
| 3 | **VIEW-III** | Ready | Channel degradation, VQI validation |
| 4 | **AGE-II** | Ready | Dementia-specific, cascade validation |
| 5 | **DEV-II** | Ready | ADHD parameters, adolescent risk, U-curve validation |
| 6 | **TP-III** | Blocked | Needs empirical data |

---

## DOCUMENT INVENTORY

| Doc | Title | Lines | Version |
|-----|-------|-------|---------|
| 14 | Panel IV: Cognitive Control & Reward | ~1,100 | V1.0 |
| 20 | Panel V: Social Brain | ~900 | V1.0 |
| 21 | ART Reduction | ~200 | V1.0 |
| 33 | Dual-Index Cross-Reference | ~870 | V1.0 |
| 34 | Panel L-I | ~900 | V1.1 |
| 38 | Panel SC-I | ~1,000 | V1.0 |
| 39 | Panel VF-I | ~900 | V1.0 |
| 42 | Panel TP-I | ~1,239 | V1.1 |
| 44 | Panel SOC-I | ~1,025 | V1.1 |
| 45 | Panel COL-I | ~649 | V1.0 |
| 46 | Panel OLF-I | ~700 | V1.0 |
| 47 | Panel VIEW-I | ~640 | V1.0 |
| 49 | Panel L-II | ~534 | V1.0 |
| 51 | Panel MAT-II | ~710 | V1.0 |
| 52 | Registry | ~571 | V1.8 |
| 53 | Transfer Context | ~large | V8.0 |
| 54 | A2 Extension | ~400 | V1.0 |
| 55 | Panel CREA-I | ~1,097 | V1.0 |
| 56 | Panel TP-II | ~618 | V1.0 |
| 57 | Panel SOC-II | ~513 | V1.0 |
| 58 | Panel CREA-II | ~446 | V1.0 |
| 59 | Panel VIEW-II | ~378 | V1.0 |
| 60 | Panel AGE-I | ~369 | V1.0 |
| **61** | **Panel DEV-I** | **~309** | **V1.0** |

---

*Sprint Prompt V14.0 — Generated February 17, 2026*
*Session: 6 panels (Docs 56–61, ~2,633 lines), Registry V1.8 (571 lines)*
*Complete lifespan model: DEV-I (childhood) + adult baseline + AGE-I (aging)*
*72 templates, 61 documents, 10 domains at ★★★★*
*Six template series calibrated with lifespan moderation*
