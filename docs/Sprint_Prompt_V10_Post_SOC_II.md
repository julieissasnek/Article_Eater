# ⚠️ SUPERSEDED — See Sprint_Prompt_V15_Post_VF_II_CREA_III.md for current version

# ARTICLE EATER — AGENT SPRINT PROMPT V10.0
## Post SOC-II Calibration | February 17, 2026

---

## CURRENT STATE

The Article Eater template system now has **72 mechanistic templates** organized across 10 architectural attribute domains. All 10 domains are at ★★★★ coverage. Three calibration panels are now complete: L-II (Doc 49), MAT-II (Doc 51), TP-II (Doc 56), and **SOC-II (Doc 57)**. The most recent production was **Doc 57: Panel SOC-II Social Calibration** (513 lines), which advanced SOC1 and SOC3 from ✗ Uncalibrated to ~ Partial, and SOC2 to ✓ Good.

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
- **SOC1–SOC3**: Social Configuration (SOC-II calibrated, Doc 57)
- **VIEW1–VIEW3**: View & Nature (Doc 47)
- **COL1–COL2**: Color (Doc 45, WIP)
- **TP1–TP4**: Temporal Dynamics (TP-II calibrated, Doc 56)
- **CREA1–CREA3**: Creative Cognition (Doc 55)

### Calibration Status

| Template Set | Calibration | Source |
|-------------|-------------|--------|
| L1–L5 | ~ Partial | Doc 49 (L-II) |
| MAT1–MAT5 | ~ Partial | Doc 51 (MAT-II) |
| TP1–TP4 | ~ Partial | Doc 56 (TP-II) |
| **SOC1–SOC3** | **~ Partial / ✓ Good** | **Doc 57 (SOC-II)** |
| CREA1–CREA3 | ✗ Uncalibrated | Awaiting CREA-II |
| SC1–SC4 | ✗ Uncalibrated | Awaiting SC-II |
| All others | ✗ Uncalibrated | Per registry priority |

---

## AGENT ASSIGNMENTS

### CLAUDE CODE — Schema Encoding Sprint

**Priority 1: Encode SOC-II Calibration Data (Doc 57)**
- Add cultural proxemic zones to SOC1 schema:
  - `cultural_cluster: "latin_american" | "north_american" | "northern_european" | "east_asian" | "middle_eastern"`
  - `zone_boundaries: {cluster: string, stranger_distance_cm: number, close_friend_cm: number, intimate_cm: number}[]`
  - `cultural_privacy_parameter: {cluster: string, cpp: number}[]` (range 0–1; N.Eur 0.85, E.Asian 0.45)
  - `architectural_dimension_scaling: {dimension: string, culture_multiplier: number}[]`
- Add privacy-encounter curve to SOC2 schema:
  - `privacy_encounter_ratio: number` (shared area / total area)
  - `satisfaction_function: "concave_with_knee"` 
  - `optimal_ratio: 0.50 ± 0.08`
  - `cost_knee: 0.70` (satisfaction drops sharply above this)
  - `encounter_paradox_threshold: 0.80` (>80% shared → 70% reduction in face-to-face)
  - `privacy_mechanism_ranking: ["withdrawal_spaces", "acoustic_enclosure", "visual_screen", "territorial_marker", "spatial_distance"]`
  - `minimum_prescriptions: {phone_booths_per_workers: 0.125, quiet_rooms_per_workers: 0.04, private_meeting_per_workers: 0.067}`
- Add Dunbar layer mapping to SOC3 schema:
  - `dunbar_layers: {layer_size: number, physical_distance_m: number, enclosure_stc: number}[]`
  - `interaction_decay_function: "exponential"`, `lambda_m: 8`
  - `floor_tax_multiplier: 8`
  - `pod_acoustic_target_stc: {min: 35, max: 40}`
  - `zone_masking_dba: 45`

**Priority 2: Encode TP-II Calibration Data (Doc 56)** — as per V9.0

**Priority 3: Encode CREA1–CREA3 (Doc 55)** — as per V9.0

**Priority 4: Cross-template metadata fields** (from Doc 52 V1.4)
- All templates involving interpersonal distance: add `cultural_cluster` moderator
- All shared/private space templates: add `shared_private_ratio` and compute satisfaction via SOC2 concave function
- All social grouping templates: add `dunbar_layer` field with exponential decay
- All movement templates: add `mfi_range` field
- All threshold templates: add `threshold_channel_count` and `estimated_boundary_d`
- All material templates: add `aging_trajectory` structure
- All path-based templates: add `pe_density_index`

### CODEX — Task Board and Validation

**Sprint 1**: Update task board with Docs 55, 56, and 57. Mark TP-II, SOC-II, CREA-I as complete.

**Sprint 2**: Validate schema for new metadata fields:
- `cultural_cluster` enum (5 values)
- `privacy_encounter_ratio` range 0.0–1.0
- `dunbar_layer` valid sizes (5, 15, 50, 150)
- `floor_tax_multiplier` positive integer
- `creative_phase_affinity` enum values
- `mfi_range` numerical ranges (MFI 0.0–1.0)
- `aging_trajectory` parameter bounds (D 1.0–2.0; tau > 0)
- `threshold_channel_count` integer 0–7

**Sprint 3**: Cross-reference audit — verify bidirectional encoding for all template interactions in Docs 55, 56, and 57.

### ANTIGRAVITY — Round-Trip Validation

**Sprint 1**: SOC1–SOC3 calibrated round-trip. Test cultural proxemic zones against test building corpus (apply each of 5 cultural clusters). Verify privacy-encounter curve produces reasonable satisfaction scores for known office layouts. Test Dunbar decay function against published workplace interaction data.

**Sprint 2**: CREA1–CREA3 round-trip. Test three-zone model tagging. Verify CREA2 three-pathway independence.

**Sprint 3**: Full integration test. Select 3 buildings, run all 72 templates. Flag conflicts, impossible combinations, missing links.

---

## KEY PARAMETERS REFERENCE (Quick-Look for All Agents)

### SOC1 Cultural Proxemic Zones (Doc 57)
| Cluster | Stranger (cm) | Close Friend (cm) | CPP |
|---------|--------------|-------------------|-----|
| Latin American | 78 | 40 | 0.50 |
| North American | 95 | 50 | 0.80 |
| Northern European | 100 | 48 | 0.85 |
| East Asian | 102 | 55 | 0.45 |
| Middle Eastern | 115 | 60 | 0.70 |

### SOC2 Privacy-Encounter Curve (Doc 57)
- Optimal shared/total ratio: **0.50 ± 0.08**
- Satisfaction: S ≈ 5.8 × [1 − 2.0(r − 0.50)² − 4.0 × max(0, r − 0.70)²]
- Cost knee: 0.70 (sharp satisfaction drop above)
- Encounter paradox: >0.80 shared → 70% reduction in face-to-face
- Privacy mechanism ranking: withdrawal > acoustic > visual > territorial > distance
- Minimums: 1 phone booth / 8 workers; 1 quiet room / 25; 1 private meeting / 15

### SOC3 Dunbar Layer Distances (Doc 57)
| Layer | Distance (m) | Enclosure (STC) |
|-------|-------------|-----------------|
| 5 (intimate) | 0–6 | 35–40 |
| 15 (close) | 6–15 | Acoustic zoning |
| 50 (band) | 15–30 | Same floor |
| 150 (clan) | Same building | Floor tax 8× |
Interaction decay: f = e^(−d/8)

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

## PRIORITY QUEUE (from Doc 52 V1.4)

| # | Panel | Status | Next Action |
|---|-------|--------|-------------|
| 1 | **CREA-II** | Ready | Multi-channel interaction (2×2×2 factorial design) |
| 2 | **TP-III** | Blocked (needs empirical data) | VR channel-count study, surface fractal measurement |
| 3 | **SOC-III** | Ready | Multicultural design parameters, healthcare application |
| 4 | **Aging & Architecture** | Ready | Cross-cutting age moderators |
| 5 | **Child Development** | Ready | Developmental moderators |
| 6 | **VIEW-II** | Ready | Channel weights, synthetic nature |

### Smaller Tasks (Retrofits)
- **COL-I completion** (Doc 45): WIP at 628 lines, needs closing apparatus (calibration table, prospectus, scope)
- **SC-I, VF-I, OLF-I retrofits**: Add broadening/deepening frameworks following Doc 34 V1.1 exemplar
- **Companion assessments**: Earlier panels (Music M-I to M-III, AX-I, Arch I–V) need calibration table + X-II prospectus addenda

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
| 45 | Panel COL-I: Color (WIP) | ~628 | V1.0 |
| 46 | Panel OLF-I: Olfactory | ~700 | V1.0 |
| 47 | Panel VIEW-I: View & Nature | ~800 | V1.0 |
| 49 | Panel L-II: Light Calibration | ~534 | V1.0 |
| 51 | Panel MAT-II: Materials Calibration | ~710 | V1.0 |
| 52 | Calibration & Extension Registry | ~371 | V1.4 |
| 53 | Transfer Context | ~large | V8.0 |
| 54 | A2 Spatial Scale Extension | ~400 | V1.0 |
| 55 | Panel CREA-I: Creative Cognition | ~1,097 | V1.0 |
| 56 | Panel TP-II: Temporal Calibration | ~618 | V1.0 |
| **57** | **Panel SOC-II: Social Calibration** | **~513** | **V1.0** |

---

*Sprint Prompt V10.0 — Generated February 17, 2026*
*Covers: Doc 55 (CREA-I), Doc 56 (TP-II), Doc 57 (SOC-II), Doc 52 V1.4*
