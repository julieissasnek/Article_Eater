# Calibration Review: CH-1 through CH-6 Parameters for CVA-1-REV Integration

**Date**: March 1, 2026
**Reviewer**: Claude Code (Haiku 4.5)
**Status**: Complete — 6 research reports + 6 parameter JSON files generated
**Purpose**: Assess cultural calibration parameters for integration into CVA-1-REV (Tier 2 constraint calibration via ψ_culture)

---

## Executive Summary

CW (Cowork/Claude) has completed comprehensive research on cultural habituation across six dimensions (CH-1 through CH-6), producing:

1. **6 literature review documents** (2,000–5,000 words each)
2. **6 machine-readable parameter JSON files** (newly created by reviewer)

**Overall Assessment**: Parameters are **PLAUSIBLE and WELL-RESEARCHED** but require **MEDIUM confidence** labels (0.65–0.80 range) due to:
- Limited direct quantitative validation across cultural groups
- Mechanistic assumptions about neural implementation (sensory gating, prediction error circuits)
- Individual/contextual variation potentially larger than cultural averages

**Recommendation**: **PROCEED WITH INTEGRATION** into CVA-1-REV with explicit uncertainty quantification. Use research-backed defaults but implement sensitivity analysis to test impact of ±20% parameter perturbation.

---

## Part 1: Dimension-by-Dimension Assessment

### CH-1: Noise Tolerance (ProcessingCost, SensoryGatingEfficiency)

**Research Quality**: ★★★★☆ (4/5)

**Strengths**:
- Comprehensive cross-cultural dataset (Hong Kong, Japan, Germany, Korea, USA, UK)
- Clear quantitative inflection points (65 dB(A) variation: 0.78%–56.41% highly annoyed)
- Well-articulated mechanistic theory: adaptation-level shifts based on chronic exposure

**Parameters**:
| Cultural Context | ProcessingCost Modifier | SensoryGating % | Confidence |
|---|---|---|---|
| East Asia High-Density | 0.72 | 68% | 0.70 |
| Western Urban (baseline) | 1.00 | 52% | 0.85 |
| Western Suburban | 1.05 | 45% | 0.65 |

**Issues & Recommendations**:

1. **Mechanism uncertainty**: Sensory gating efficiency claim (68% vs 52%) is theoretically motivated but **NOT empirically validated in this dataset**. The research supports *behavioral* tolerance (adaptation-level shifts) but neurobiological claims require fMRI validation.
   - **Action**: Label confidence 0.70 (MEDIUM); flag for panel review on neural implementation assumptions

2. **Generational effects unknown**: Do second-generation residents maintain parents' baseline, or adapt to current environment?
   - **Action**: Document as "Open Question Q1" for future validation

3. **Adaptation reversibility**: If migrant moves to quiet area, does ProcessingCost revert?
   - **Action**: Document as "Open Question Q2"; implement as research priority

**Integration readiness**: ✓ **GREEN** — Use 0.72 modifier for East Asian high-density; 1.00 baseline for Western; apply continuously via urban_density_percentile interpolation.

---

### CH-2: Proxemics (SocialCueDensity, AffordanceDensity)

**Research Quality**: ★★★★☆ (4/5)

**Strengths**:
- Sorokowska et al. (2017): Large, multi-national dataset (8,943 subjects, 42 countries)
- Clear quantitative norms (intimate: 31.9 cm ± 8.2; social: 135.1 cm ± 21.8)
- Consistent demographic modifiers (gender +5.5 cm, age effects linear)

**Parameters**:
| Cultural Cluster | Mean Distance (cm) | Social Cue Modifier | Confidence |
|---|---|---|---|
| High-distance (Romania, Germany) | 119–140 | 0.75 | 0.80 |
| Medium-distance (France, Australia) | 95–115 | 0.90 | 0.75 |
| Low-distance (Argentina, Brazil) | 80–95 | 1.15 | 0.80 |

**Issues & Recommendations**:

1. **Measurement ecological validity**: Graphic-based survey may not predict actual behavioral distances. Real-world proxemics can be 10–20% larger than lab preferences.
   - **Action**: Use "virtual preference distance" interpretation; acknowledge ±15% real-world variance

2. **Interaction effects not fully specified**: Gender × Culture and Urban Density × Culture multiplicative effects are hypothesized but not empirically validated.
   - **Action**: Document as "Medium confidence assumptions"; recommend empirical validation before high-stakes applications

3. **Urban density effects strong**: High-density residents globally show compressed proxemics (China cities, Tokyo, NYC, Mumbai all ~80–90 cm despite cultural baseline). This is under-weighted in current spec.
   - **Action**: Increase urban_density_percentile weighting; consider making it primary modifier after culture cluster

**Integration readiness**: ✓ **GREEN** — Use cluster-based lookup for baseline; apply gender (+5.5 cm) and age (linear +3–6 cm) modifiers; implement continuous urban_density_percentile interpolation.

---

### CH-3: Visual Complexity (PredictionError, LoadRate, ProcessingCost)

**Research Quality**: ★★★☆☆ (3/5)

**Strengths**:
- Berlyne inverted-U framework well-established (2,471 citations)
- Visual diet hypothesis theoretically motivated and empirically supported (Höchsmann, Regan)
- Clear quantitative metrics (Fractal Dimension, Shannon Entropy)

**Parameters**:
| Cultural Tradition | Optimal FD | Entropy | PE Tolerance | Confidence |
|---|---|---|---|---|
| Japanese minimalist | 1.1 | 0.35 | 0.30 | 0.75 |
| Western romantic | 1.45 | 0.50 | 0.50 | 0.80 |
| Baroque/Islamic ornate | 1.75 | 0.65 | 0.70 | 0.70 |

**Issues & Recommendations**:

1. **No direct cross-cultural preference comparison**: We have FD measurements of architectural styles but **no direct rating study** where Japanese and Baroque-tradition subjects rated the same scaled-complexity images.
   - **Action**: Mark confidence 0.70 (MEDIUM); flag as HIGH PRIORITY for validation study

2. **Individual differences underestimated**: Personality traits (openness to experience, need for cognition) may predict complexity preference better than culture. Within-culture variance may exceed between-culture variance.
   - **Action**: Implement as additive model: BaselinePE = CulturePE + PersonalityPE

3. **Context matters**: Same fractal dimension acceptable in museum vs. home vs. street. Parameters may need context modifier.
   - **Action**: Document context factor (±20% PE adjustment) for integration guidance

4. **Measurement circularity**: We measure FD of existing architecture, then assume people prefer FD similar to their childhood FD. This is somewhat circular (explains observed preferences via observed architecture, not independent causation).
   - **Action**: Label as "correlational, not causal"; recommend fMRI validation of prediction error signal

**Integration readiness**: ⚠ **YELLOW** — Use parameters as empirically-grounded priors, but implement sensitivity analysis (±0.15 FD variation) to test impact. Require validation before production use in high-stakes contexts.

---

### CH-4: Ceiling Height (ControlEfficacy, NarrativeCoherence)

**Research Quality**: ★★★★☆ (4/5)

**Strengths**:
- Meyers-Levy & Zhu (2007) is landmark study with robust lab validation (3 experiments)
- Clear mechanistic theory: height primes freedom (high) vs confinement (low)
- Quantitative cultural baselines well-documented (Japan 2.4 m, USA 2.74 m, Europe 2.5 m)

**Parameters**:
| Culture | Baseline (m) | Tolerance (m) | Control Mod (high) | Confidence |
|---|---|---|---|---|
| Japan | 2.4 | ±0.3 | 0.75 (low = constraint) | 0.80 |
| USA | 2.74 | ±0.4 | 1.15 (high = freedom) | 0.85 |
| Europe | 2.5 | ±0.35 | 0.90 | 0.80 |

**Issues & Recommendations**:

1. **Priming study limited to Western subjects**: Meyers-Levy & Zhu used university undergraduates (mostly North American). **No direct replication in East Asian or other populations**.
   - **Action**: Mark confidence 0.75 for non-Western generalization; recommend fMRI validation in Japanese subjects

2. **Causality direction unclear**: Does height prime cognition, or do primed/stress-seeking individuals choose high-ceiling environments? Longitudinal data needed.
   - **Action**: Implement as "sufficiency assumption"; acknowledge alternative explanations

3. **Adaptation timeline unknown**: How long before chronically exposed person adapts baseline? Days? Weeks? Never?
   - **Action**: Document as "Open Question Q3"; implement as research priority

4. **Effect size may be small in natural settings**: Lab studies show robust effects; real-world architectural effects likely smaller (competing factors: lighting, furniture, social context).
   - **Action**: Recommend 50% effect size reduction for real-world integration; implement sensitivity analysis

**Integration readiness**: ✓ **GREEN** — Parameters are production-ready for Western contexts. For East Asian/other cultures, use as first-order approximation with explicit uncertainty flagging.

---

### CH-5: Nature-Artifice Spectrum (AffordanceDensity, NarrativeCoherence, MultisensoryCoherence)

**Research Quality**: ★★★☆☆ (3/5)

**Strengths**:
- Clear cultural pattern differences (East Asian curated vs Scandinavian wild)
- Mechanistic explanations well-articulated (post-industrial nostalgia, agricultural heritage, climate adaptation)
- Eglash fractal work (547 citations) provides rigorous validation for intentional African design

**Parameters**:
| Culture | Optimal Point (0–100) | Mechanism Confidence | Empirical Confidence |
|---|---|---|---|
| East Asian | 85 (curated) | 0.8 | 0.65 |
| Scandinavian | 15 (wild) | 0.75 | 0.60 |
| Western intermediate | 50 | 0.80 | 0.70 |
| Islamic/Middle Eastern | 80 (controlled) | 0.75 | 0.70 |
| West African | 60 (recursive design) | 0.80 | 0.65 |

**Issues & Recommendations**:

1. **NO direct quantitative preference comparison**: We have architectural examples but **no direct study** where Japanese, Scandinavian, and African subjects rated the same set of scaled landscape images.
   - **Action**: Mark empirical confidence 0.65 (MEDIUM); flag as HIGHEST PRIORITY for validation

2. **Individual variation likely large**: Within Japan, some people prefer wilderness; within Scandinavia, some prefer formal gardens. Variance around cultural mean probably ±20 points.
   - **Action**: Implement as probabilistic distribution around optimal point, not point estimate

3. **Generational drift underestimated**: Younger generations globally adopting "wilderness conservation" narrative from Western environmental movement. Traditional preferences may not transmit to Gen-Z.
   - **Action**: Implement age modifier; younger = shift toward Western wilderness preference

4. **Context collapse risk**: Scale is 0–100 but some environments are genuinely NEITHER (abstract artscape, urban concrete minimalism). May need to add "orthogonal axis" for whether nature/artifice distinction is salient.
   - **Action**: Document limitation; recommend qualitative descriptor field alongside scalar

**Integration readiness**: ⚠ **YELLOW** — Use as directional guide only. Requires quantitative validation study before full integration. Recommended: implement A/B testing with real subjects before production deployment.

---

### CH-6: Spatial Symmetry (NarrativeCoherence, PredictionError, AffordanceDensity, ControlEfficacy)

**Research Quality**: ★★★★☆ (4/5)

**Strengths**:
- Universal symmetry bias well-documented (Bertamini, Evans; consistent across all populations)
- Eglash fractal validation (547 citations) provides rigorous proof of intentional African design (not accidental)
- Clear contrast: Western bilateral vs West African fractal vs East Asian dual-mode vs Islamic radial

**Parameters**:
| Culture | Preferred Regime | Discomfort Zone | Narrative Coherence Match | Confidence |
|---|---|---|---|---|
| Western | Bilateral | Fractal/asymmetric | 1.0 bilateral / 0.25 fractal | 0.85 |
| West African | Fractal (D_f 1.8–2.0) | Rigid bilateral | 1.0 fractal / 0.30 bilateral | 0.75 |
| East Asian | Dual (bilateral formal + asymmetric intimate) | Extremes either way | 1.0 in context / 0.6 out-of-context | 0.75 |
| Islamic | Radial/tessellation | Random asymmetry | 1.0 tessellation / 0.4 bilateral | 0.70 |

**Issues & Recommendations**:

1. **Neural mechanism not directly validated**: LOC (lateral occipital complex) symmetry detection bias is universal; cultural modulation of prediction error is inferred, not measured.
   - **Action**: Mark confidence 0.75 for neural claims; flag as requiring fMRI validation

2. **Eglash validation is architectural, not perceptual**: We know African compounds ARE fractal; we don't know whether West African residents *prefer* fractals or whether fractals are just the default they adapted to.
   - **Action**: Design preference rating study; present bilateral vs fractal layouts at same complexity level

3. **Generational transmission unclear**: Do children inherit spatial preferences, or do they learn them? Critical for migration/diaspora prediction.
   - **Action**: Document as "Open Question Q4"; implement developmental longitudinal study

4. **Parameter mapping incomplete**: How does "discomfort with bilateral" translate to specific CVA constraint modifiers? Need quantified mapping (e.g., "bilateral space for West African subject = NarrativeCoherence 0.30, PredictionError +0.50").
   - **Action**: Completed in parameter JSON; recommend careful testing during CVA integration

**Integration readiness**: ✓ **GREEN** — Parameters are well-specified and theoretically grounded. Validate in 2–3 integration tests before full production use.

---

## Part 2: Cross-Cutting Assessment

### Parameter Range Consistency

All six dimensions use similar scales (0–1 for modifiers, culturally-relative baselines for measurements). ✓ **CONSISTENT**

**Potential issue**: Some parameters are absolute (cm distances in CH-2, dB in CH-1) while others are relative (0–100 scale in CH-5, FD 1.0–2.0 in CH-3). CVA integration layer must normalize these carefully.

**Recommendation**: Implement unitless mapping layer in CVA constraint vector initialization.

---

### Plausibility Cross-Check: Internal Consistency

**Q: Do the six dimensions cohere? Would someone with high noise tolerance also prefer complex visuals?**

Partial data:
- East Asian high-density: high noise tolerance (0.72 modifier), preference for SIMPLE visuals (FD 1.1)
- Western: medium noise tolerance (1.0), medium visual complexity (FD 1.45)
- Baroque/Islamic: low noise tolerance (implied), high visual complexity (FD 1.75)

**Pattern**: There's NO strong latent "complexity tolerance" factor; instead, each dimension is independently calibrated. This suggests cultures develop specialized adaptations to their *specific* environmental constraints, not a general "tolerance for stimulation."

**Implication**: ✓ **COHERENT** — Don't assume redundancy across dimensions.

---

### Error Bounds and Confidence Intervals

**Summary of confidence levels**:

| Dimension | Mechanism Confidence | Empirical Confidence | Overall |
|---|---|---|---|
| CH-1 Noise | 0.80 | 0.70 | **0.70 (MEDIUM)** |
| CH-2 Proxemics | 0.85 | 0.80 | **0.80 (MEDIUM-HIGH)** |
| CH-3 Complexity | 0.80 | 0.70 | **0.70 (MEDIUM)** |
| CH-4 Ceiling | 0.85 | 0.75 | **0.75 (MEDIUM)** |
| CH-5 Nature-Artifice | 0.75 | 0.65 | **0.65 (MEDIUM)** |
| CH-6 Symmetry | 0.80 | 0.75 | **0.75 (MEDIUM)** |

**Average**: 0.72 (MEDIUM confidence)

**Interpretation**: Reasonable empirical grounding; not gold-standard validation. Suitable for research/prototype use; requires validation before high-stakes deployment.

---

### Validation Gaps Ranked by Priority

1. **HIGH PRIORITY** (Needed before production use):
   - CH-5 (Nature-Artifice): Direct preference rating study across cultures
   - CH-3 (Complexity): Cross-cultural preference comparison on scaled images
   - CH-6 (Symmetry): Perceptual validation that West African subjects prefer fractals (not just architectural fact)

2. **MEDIUM PRIORITY** (Recommended but not blocking):
   - CH-1 (Noise): fMRI validation of sensory gating efficiency claims
   - CH-4 (Ceiling): Replication of Meyers-Levy in East Asian subjects
   - CH-2 (Proxemics): Behavioral observation (video-recorded distances) vs graphic survey validation

3. **EXPLORATORY** (Research questions):
   - All dimensions: Generational effects (second-generation migrants)
   - All dimensions: Individual trait modulation (personality, education, trauma history)
   - All dimensions: Context effects (formal vs intimate, high-stakes vs casual)

---

## Part 3: Integration Guidance for CVA-1-REV

### Constraint Vector Mapping

Each parameter JSON specifies which CVA Tier2ConstraintVector components it affects:

| Dimension | ProcessingCost | LoadRate | PredictionError | ControlEfficacy | SocialCueDensity | AffordanceDensity | MultiSensoryCoherence | NarrativeCoherence |
|---|---|---|---|---|---|---|---|---|
| CH-1 Noise | ✓ | ✓ | ✓ | | | | ✓ | |
| CH-2 Proxemics | | | | | ✓ | ✓ | | |
| CH-3 Complexity | ✓ | ✓ | ✓ | | | | | |
| CH-4 Ceiling | | | | ✓ | | | | ✓ |
| CH-5 Nature-Artifice | | | | | | ✓ | ✓ | ✓ |
| CH-6 Symmetry | | | ✓ | ✓ | | ✓ | | ✓ |

**Integration Implementation**:

```python
class CVAConstraintVectorCulturalCalibration:
    def __init__(self, culture, context):
        # Load CH-1 through CH-6 parameters
        ch_params = load_ch_parameters(culture)

        # Apply modifiers
        self.processing_cost = ch1.modifier * ch3.modifier
        self.load_rate = ch1.load_modifier * ch3.load_modifier
        self.prediction_error = ch1.pe * ch3.pe * ch6.pe
        self.control_efficacy = ch4.modifier * ch6.modifier
        self.social_cue_density = ch2.modifier
        self.affordance_density = ch2.modifier * ch5.modifier * ch6.modifier
        self.multisensory_coherence = ch1.modifier * ch5.modifier
        self.narrative_coherence = ch4.coherence * ch5.coherence * ch6.coherence

        # Flag uncertainty
        self.confidence = CALIBRATION_CONFIDENCE_SCORES[culture]
```

---

### Recommended Integration Order

1. **Phase 1 (Low Risk)**: Integrate CH-2 (Proxemics) — highest confidence (0.80); simplest mechanistic (distance → affordance)
2. **Phase 2 (Medium Risk)**: CH-4 (Ceiling), CH-1 (Noise) — confidence 0.75, 0.70; good mechanistic clarity
3. **Phase 3 (Higher Risk)**: CH-3 (Complexity), CH-6 (Symmetry) — confidence 0.70–0.75; more assumptions about perception
4. **Phase 4 (Exploratory)**: CH-5 (Nature-Artifice) — confidence 0.65; requires user testing

---

### Testing Before Production

**Recommended validation approach**:

1. **Unit-level testing**: For each dimension, verify constraint vector modifiers change in expected direction (e.g., East Asian high-density → lower ProcessingCost)
2. **Integration testing**: Run full CVA-1-REV pipeline on 10–20 manually-scored test scenarios; measure prediction error against expert judgment
3. **User testing (critical)**: Show CVA-1-REV outputs to 5–10 subjects from each major cultural group; collect naturalness/fit ratings
4. **Sensitivity analysis**: Perturb each CH parameter ±20%; measure impact on downstream constraints and final valuation output

---

## Part 4: Issues and Warnings

### Issue 1: "Culture" as Monolithic
**Problem**: All parameters assume culture is fixed, binary (Japan vs USA, etc.). Reality is:
- Massive within-country variation (Tokyo vs rural Japan, NYC vs rural USA)
- Second-generation effects
- Gender effects (already accounted for in CH-2, but not others)
- Education/SES effects
- Trauma/neurodivergence effects

**Mitigation**: Implement as **priors**, not fixed values. Allow individual-level calibration via observable context clues (urban_density_percentile, age, etc.). Flag confidence intervals prominently.

---

### Issue 2: Mechanistic Assumptions Not Validated
**Problem**: Parameters justify claims via neuroscientific mechanisms (sensory gating, prediction error circuits, etc.) that haven't been directly measured in these cultural groups.

**Mitigation**: Label all neural mechanism claims as "theoretical mechanistic hypothesis, not empirically demonstrated." Recommend fMRI validation before high-stakes use.

---

### Issue 3: Reciprocal Causation vs Adaptation
**Problem**: We don't know whether:
- (A) Cultures prefer certain environments because of genetic inheritance, or
- (B) Cultures prefer certain environments because of chronic exposure (learned adaptation)

If (A), effects should be stable across generations. If (B), second-generation migrants should show intermediate preferences.

**Mitigation**: Implement as "empirically derived adaptation model" not "genetic model." Document that effects may reverse/attenuate in diaspora contexts.

---

### Issue 4: Discrete Cultural Clusters vs Continuous Spectra
**Problem**: Parameters group cultures (Romania, Hungary, Saudi Arabia, Estonia, Pakistan, Germany in "high-distance" cluster for CH-2). Within-cluster variance may be large.

**Mitigation**: Where possible (CH-2, CH-1), implement continuous models (urban_density_percentile, latitude/climate) instead of discrete clusters. Reserve discrete clusters for exploratory analysis only.

---

## Part 5: Recommendations for CVA Integration

### For CW (Cowork):

1. ✓ **APPROVED for integration**: Use CH-1, CH-2, CH-4 parameters as-is; label confidence 0.70–0.80
2. ⚠ **CONDITIONAL**: CH-3, CH-6 pending sensitivity analysis during CVA integration
3. ❌ **HOLD PENDING VALIDATION**: CH-5 (Nature-Artifice) requires quantitative preference study before production use

### For DK (David Kirsh / Panel):

1. **Panel Review Requested** on:
   - Neural mechanism assumptions (sensory gating efficiency, prediction error implementation)
   - Individual/contextual variance relative to cultural averages
   - Generational transmission (second-generation effects)

2. **Recommended Panel Consultation** on:
   - Whether "culture-based defaults with individual calibration" is epistemologically acceptable vs "population norms with variance"
   - Risk tolerance for deploying medium-confidence (0.65–0.75) parameters in user-facing system
   - Prioritization of validation studies (fMRI, preference rating, longitudinal migration follow-up)

### For AG (Agent Group):

1. **Create integration tests**: Verify constraint vector modifiers change in expected direction
2. **Run sensitivity analysis**: ±20% parameter perturbation; measure impact on CVA output
3. **Flag uncertainty**: Implement confidence_level field in all CVA-1-REV outputs; surface confidence to end users
4. **Plan validation studies**: Schedule CH-5 preference rating study and fMRI validation for Q2 2026

---

## Conclusion

The CH-1 through CH-6 calibration parameters represent **well-researched, theory-grounded, but empirically medium-confidence** specifications for cultural variation in environmental perception. Suitable for research prototype and early-stage integration. Recommend phased deployment with explicit confidence labeling and user-facing uncertainty communication.

**Overall readiness for CVA-1-REV**: 🟡 **YELLOW** — Proceed with integration (CH-1, CH-2, CH-4 priority); validate before full production use; prioritize CH-5 quantitative study and neural mechanism fMRI validation.

---

**Reviewed by**: Claude Code (Haiku 4.5)
**Date**: March 1, 2026
**Classification**: Research Review — Internal Documentation
