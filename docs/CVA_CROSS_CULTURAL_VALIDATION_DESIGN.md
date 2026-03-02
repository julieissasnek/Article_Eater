# CVA-8: Cross-Cultural Validation Design
**Sprint CVA-8 — Phase C: Empirical Design**

> Study protocol for validating that CVA cultural variants represent
> structurally different valuation decompositions (not just parameter shifts).

---

## Core Hypothesis

CVA posits 4 structurally distinct valuation decompositions:
- **Western**: 9D orthogonal (all axes independent)
- **Japanese**: 7D with 間 (ma) subsumption (Safety+Restoration→Ma)
- **West African**: 8D with Àṣà embedding (Identity→Àṣà community axis)
- **Indian**: 10D with Rasa/Dharma additions (non-Western beauty and duty axes)

**H₁**: Factor analysis of valuation ratings will recover different dimensionality
across cultural groups (9D Western vs 7D Japanese vs 8D West African vs 10D Indian).

**H₀**: A single 9D factor structure fits all groups equally well (cultural
differences are parameter-only, not structural).

---

## Study Design

### Participants
| Culture | Location | N | Recruitment |
|---------|----------|---|-------------|
| Western | US/UK university | 80 | Online + lab |
| Japanese | Tokyo/Kyoto university | 80 | Lab |
| West African (Yoruba) | University of Ibadan | 60 | Lab |
| Indian (Hindi/Sanskrit) | IIT Delhi / Banaras Hindu | 80 | Lab |

**Total N = 300** (accounting for 15% attrition → target 255 complete)

### Power Analysis
- For CFA model comparison (ΔCFI > 0.01): N = 60/group minimum
- For MGCFA invariance testing: N = 80/group recommended (Cheung & Rensvold, 2002)

### Stimuli
**40 scenes** selected for cross-cultural applicability:
- 10 architectural (mix of sacred, residential, commercial, public)
- 10 natural (landscapes, gardens, water features)
- 10 social (gathering, solitary, group)
- 10 hybrid (parks with architecture, market scenes)

**Selection criteria**:
- Culturally neutral baseline (no culture-specific symbols)
- Balanced on constraint dimensions (processing cost, prediction error, etc.)
- Reviewed by cultural consultants from each target culture

### Measurement Instruments

#### A. CVA Valuation Rating Scale (CVA-VRS)
- 9-axis universal scale (all cultures)
- Plus culture-specific axes:
  - Japanese: Ma (間) scale, Amae (甘え) scale
  - West African: Àṣà scale
  - Indian: Rasa scale (9 rasas), Dharma scale
- 7-point Likert per axis, plus 100mm VAS beauty rating

#### B. Constraint Assessment Battery
- Processing Cost: RT + complexity rating
- Prediction Error: Surprise + novelty rating
- Control Efficacy: Way-finding confidence
- Social Cue Density: Social scene count
- Multisensory Coherence: Gestalt completion task

#### C. Activity Frame Protocol
- Participants rate each scene under 3 frames (randomized):
  - Relaxation, Work/Study, Social gathering
- Tests frame × culture interaction on valuation weights

### Translation Protocol
1. Forward translation (2 translators per language)
2. Back-translation (independent translator)
3. Expert panel reconciliation
4. Cognitive interview pilot (N = 5/language)
5. Final revision

---

## Analysis Plan

### Step 1: Confirmatory Factor Analysis (per culture)
- Fit cultural-specific models:
  - Western: 9-factor model
  - Japanese: 7-factor model (Ma subsumption)
  - West African: 8-factor model (Àṣà embedding)
  - Indian: 10-factor model (Rasa + Dharma)
- Fit universal 9-factor model to all groups
- Compare: ΔCFI, ΔRMSEA, AIC

### Step 2: Multi-Group CFA (MGCFA)
- Test measurement invariance hierarchy:
  1. Configural invariance (same structure?)
  2. Metric invariance (same loadings?)
  3. Scalar invariance (same intercepts?)
- **Prediction**: Configural invariance will FAIL across all groups
  (different structures, not just different parameters)

### Step 3: Beauty Readout Model Comparison
- Which beauty readout model (Linear/Quadratic/Neural/Rasa) fits best per culture?
- **Prediction**: Rasa model fits Indian sample best; Linear fits Western best

### Step 4: Cluster Analysis
- Unsupervised clustering of valuation profiles (K-means, K = 4-10)
- Do clusters align with cultural groups?
- **Prediction**: ≥3 culturally coherent clusters emerge

---

## Collaborator Network

| Role | Expertise | Institution | Status |
|------|-----------|------------|--------|
| PI | CVA architecture, computational modeling | [Lead institution] | Active |
| Co-I (Japan) | Environmental psychology, Ma concept | Tokyo University | To contact |
| Co-I (Nigeria) | Yoruba aesthetics, Àṣà | University of Ibadan | To contact |
| Co-I (India) | Rasa theory, Indian aesthetics | IIT Delhi | To contact |
| Statistician | MGCFA, cross-cultural psychometrics | [Stats dept] | To recruit |
| Cultural consultants | ×4 (one per culture) | Various | To recruit |

---

## IRB Considerations

### Ethics Protocol
- Minimal risk (scene viewing + questionnaire)
- Informed consent in local language
- Data anonymization before cross-site sharing
- Cultural sensitivity review by local consultants
- GDPR compliance for EU data; local equivalents elsewhere

### Data Management
- Raw data stored at collection site
- Anonymized data shared via secure repository
- Pre-registered analysis script published with data

---

## Timeline

| Month | Activity |
|-------|---------|
| 1-2 | Instrument development + translation |
| 3 | Pilot testing (N=5/site) |
| 4-6 | Data collection |
| 7-8 | Analysis |
| 9 | Report writing |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Insufficient N in West Africa | Reduced power | Over-recruit by 25% |
| Translation non-equivalence | Invalid comparison | Rigorous back-translation + cognitive interviews |
| Scene cultural bias | Confounded results | Cultural consultant review + pilot |
| Configural invariance found | Undermines CVA cultural variant claim | Report honestly; consider hybrid models |
