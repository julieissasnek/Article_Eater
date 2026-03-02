# Expert Panel Review: Cultural Habituation Calibration Parameters

**Date**: 2026-03-02
**Review Period**: Full manuscript analysis of 7 CH parameter files
**Panel Convening**: Remote expert consultation

---

## Executive Summary

This panel review evaluates seven Cultural Habituation (CH-1 through CH-7) calibration parameter files for the ATLAS system. The files represent literature-derived, evidence-based calibrations intended to adjust universal perceptual thresholds (Tier 1) for culture-specific populations (Tier 2).

### Overall Assessment

**CONDITIONAL APPROVAL with mandatory revisions before deployment.** The parameter files demonstrate strong conceptual coherence, appropriate epistemological humility, and careful documentation of evidence sources. However, systematic gaps in cross-cultural empirical validation, uncalibrated ψ_culture multipliers, and several confidence overstatements require correction before the system goes live.

### Vote Tally (5/5 panelists)

| File | Recommendation | Vote | Notes |
|------|---------------|------|-------|
| **CH-1: Noise Tolerance** | APPROVE WITH REVISIONS | 3/5 Approve, 2/5 Revisions | Sensory gating (0.40–0.45 confidence) overstated for empirical grounding |
| **CH-2: Proxemics** | APPROVE | 5/5 Approve | Sorokowska data strong; confident regional calibration |
| **CH-3: Visual Complexity** | APPROVE WITH REVISIONS | 3/5 Approve, 2/5 Revisions | Small samples (n<100) in cross-cultural studies; confidence should be medium, not high |
| **CH-4: Ceiling Height** | APPROVE WITH REVISIONS | 4/5 Approve, 1/5 Revisions | Meyers-Levy replication status concerning; individual differences not modeled |
| **CH-5: Nature/Artifice** | APPROVE WITH REVISIONS | 3/5 Approve, 2/5 Revisions | Immigrant adaptation rates (1%/year) speculative; confidence too high |
| **CH-6: Symmetry** | APPROVE WITH REVISIONS | 4/5 Approve, 1/5 Revisions | Eglash documentation strong; cross-cultural measurement gap critical |
| **CH-7: Color Temperature** | REVISE AND RESUBMIT | 1/5 Approve, 3/5 Revisions, 1/5 Reject | Untested Kruithof hypothesis; migration data missing; confidence inflation |

### Summary of Recommended Actions

1. **Before deployment**: Revise confidence levels downward where cross-cultural empirical validation is absent
2. **Before deployment**: Remove or substantially qualify the 1%/year immigrant adaptation rate (CH-5)
3. **Before deployment**: Validate ψ_culture multipliers against held-out cross-cultural populations
4. **Field trial phase**: Establish empirical feedback loop to recalibrate parameters from real usage
5. **Critical research gaps**: Fund replication studies for Meyers-Levy ceiling height (CH-4) and Kruithof curve (CH-7) cross-culturally

---

## CH-1: Noise Tolerance Parameters

### File Metadata
- **Dimensions**: 4 parameter groups (primary baseline, annoyance thresholds, adaptation level, sensory gating)
- **Regions**: 5 regional baselines (East Asia high/mid-density, Western urban/suburban, rural)
- **Evidence quality**: Mixed; high for exposure data (Kang & Yang), medium for annoyance thresholds, low for sensory gating

### Evaluation by Dimension

#### 1. Empirical Grounding (Scores)
- **Cross-Cultural Psychologist**: 7/10 — Exposure baselines well-documented (Kang & Yang Hong Kong, WHO standards); annoyance thresholds derived from solid Miedema-Vos model. However, cross-cultural annoyance divergence inferred, not directly measured.
- **Environmental Psychologist**: 7/10 — CVA mappings (ProcessingCost, MultisensoryCoherence) theoretically sound but lack behavioral validation. The claim that Tokyo residents incur 70% ProcessingCost vs. London (0.70 multiplier) is not empirically tested.
- **Psychometrician**: 6/10 — Annoyance threshold confidence (0.65–0.80) appropriately calibrated for Western populations. East Asian thresholds (0.65–0.75 for Japan/Korea/China) represent inference from limited direct measurement.
- **Architectural Researcher**: 8/10 — Practical ranges defensible; Tokyo/Seoul/Hong Kong exposure data directly applicable to design. Speech-in-noise disruption thresholds operationally useful.
- **Epistemologist**: 6/10 — Causality chain (urban density → neural adaptation → higher annoyance thresholds) is mechanistically plausible but depends on low-confidence sensory gating evidence.

**Median Score**: 7/10

#### 2. Regional Differentiation (Avoiding Stereotypes)
- **Cross-Cultural Psychologist**: 7/10 — Groupings defensible: East Asia high/mid-density captures real density variance; Western urban/suburban captures economic development patterns. Risk: Treats "East Asia" as monolith (ignoring Shanghai vs. rural Jiangxi). Geographic granularity insufficient.
- **Environmental Psychologist**: 6/10 — Proximal density (people/km²) is the correct clustering variable, but file doesn't explicitly justify why Tokyo (37.4M, ~2,700/km²) and Seoul (~10,000/km²) cluster together as "East Asian high-density." Cultural homogeneity assumption weak.
- **Psychometrician**: 7/10 — Confidence values reflect regional data availability, which is appropriate. Japan and Germany have direct comparative studies; China/Korea inferred from exposure + annoyance gradient.

**Median Score**: 6.7/10 — **CONCERN**: File treats East Asian region monolithically; misses within-region socioeconomic and cultural variation (rural vs. urban China, South Korea pre/post-industrialization).

#### 3. Parameter Calibration (Numeric Defense)
- **Cross-Cultural Psychologist**: 6/10 — Baselines defensible (Tokyo 65 dB aligns with Japanese standard; WHO 45 dB aligns with international guideline). Adaptation-level upward shift (Helson theory) is theoretically sound but not directly measured.
- **Environmental Psychologist**: 5/10 — **FLAG**: Sensory gating efficiency (0.40–0.45 confidence) is highly speculative. Confidence range 40–45% suggests mechanisms drawn from animal stimulus-specific adaptation (SSA) literature, not human urban populations. File acknowledges this ("untested in East Asian urban populations") but permits inclusion anyway.
- **Psychometrician**: 7/10 — Annoyance thresholds (Japan 68 dB, USA 62 dB) have defensible 6 dB gap. Speech-in-noise disruption curves (0.20 vs. 0.30 at 65 dB) represent reasonable proportional reduction.
- **Architectural Researcher**: 7/10 — Practical thresholds usable in design (e.g., "maximize quiet to <50 dB for suburban Western, <60 dB for East Asian high-density").
- **Epistemologist**: 5/10 — ProcessingCost multiplier (0.70 for Tokyo, 1.00 for London) lacks explicit derivation. Formula given: `ProcessingCost_effective = Base × (1.0 - 0.15 × density_factor) × (1.0 - 0.10 × habituation_years)` is ad-hoc; no validation shown.

**Median Score**: 6/10 — **CONCERN**: Sensory gating and ProcessingCost multiplier justified post-hoc, not derived from empirical calibration.

#### 4. Confidence Accuracy (Honesty About Uncertainty)
- **Cross-Cultural Psychologist**: 6/10 — File appropriately segregates "high," "medium," and "low" confidence. However, places sensory gating in "low_confidence" section yet permits baselines of 40–70% in parameters, risking uncalibrated reliance.
- **Psychometrician**: 5/10 — **CRITICAL**: Confidence in sensory gating (0.40) is too high relative to evidence basis. Confidence of 0.20–0.25 would better reflect animal literature + zero direct human cross-cultural measurement.
- **Architectural Researcher**: 7/10 — Adapting-level (0.65–0.70) appropriately medium. Annoyance thresholds (0.70–0.80) appropriate; Hong Kong direct measurement justifies 0.75.
- **Epistemologist**: 5/10 — File conflates "confidence in parameter existence" with "confidence in mechanism." E.g., East Asians tolerate higher noise is HIGH confidence; *why* is the mechanism unclear, yet mechanism drives ProcessingCost formula.

**Median Score**: 5.8/10 — **CONCERN**: Sensory gating efficiency baseline and confidence are inflated relative to evidence. Should revise downward.

#### 5. Practical Utility (Architectural Impact)
- **Architectural Researcher**: 8/10 — Design thresholds (Tokyo tolerance ≤70 dB vs. London ≤55 dB) are actionable. Directly affects open-plan vs. enclosed space decisions, HVAC specs, acoustic treatment requirements. Practical value high.
- **Environmental Psychologist**: 8/10 — Multisensory coherence disruption (speech-in-noise intelligibility) operationalizes CVA constraint; allows real-time prediction of cognitive load.
- **Epistemologist**: 6/10 — Utility depends on validation of ψ_culture multipliers in real buildings. Field deployment will reveal miscalibration.

**Median Score**: 7.3/10

### Issues Flagged

1. **Sensory gating confidence inflated**: 0.40–0.45 confidence is inappropriate for animal-study-derived inference in human cross-cultural context. Recommend revision to 0.20–0.30.
2. **ProcessingCost multiplier unjustified**: Formula `(1.0 - 0.15 × density_factor) × (1.0 - 0.10 × habituation_years)` lacks calibration. No evidence that 15% density factor or 10% per-year habituation is correct.
3. **Regional monolithicism**: "East Asia high-density" bundles Tokyo (2,700/km²), Seoul (~10,000/km²), Hong Kong (~6,800/km²). Consider splitting.
4. **Missing cross-cultural annoyance study**: No direct comparison of Japanese vs. German vs. USA populations exposed to identical soundscapes. File infers divergence from indirect evidence.

### Recommended Adjustments

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| Sensory gating confidence | 0.40–0.45 | 0.20–0.25 | Animal SSA + zero human cross-cultural data |
| Adaptation level confidence (E. Asia) | 0.70 | 0.65 | Theoretical, not empirically measured |
| ProcessingCost multiplier derivation | Ad-hoc formula | Empirical validation required | No calibration shown |

### Vote: APPROVE WITH REVISIONS

**3 Approve + 2 Revisions (4/5 threshold met with revision conditions)**

**Conditions**:
- Reduce sensory gating confidence to 0.20–0.30
- Remove or empirically justify ProcessingCost formula
- Conduct cross-cultural study of East Asian vs. Western populations in identical noise fields before deployment

---

## CH-2: Proxemics Parameters

### File Metadata
- **Dimensions**: 3 core parameter groups (Hall zones, Sorokowska cross-cultural study, CVA calibration)
- **Regions**: 8+ regional baselines derived from Sorokowska et al. (2017) n=8,943
- **Evidence quality**: High; Sorokowska is largest cross-cultural proxemics dataset available

### Evaluation by Dimension

#### 1. Empirical Grounding
- **Cross-Cultural Psychologist**: 9/10 — Sorokowska et al. (2017) is exemplary: large sample, 42 countries, standardized methodology, replicated findings. Hall (1966) foundational. Confidence levels appropriate.
- **Environmental Psychologist**: 8/10 — CVA mappings (SocialCueDensity threshold = 1/[d/100]² people/m²) mathematically sound. Regional thresholds (1.5–2.0 for Romania, 3.5–4.5 for Argentina) consistent with density tolerance.
- **Psychometrician**: 9/10 — Sorokowska confidence (0.742 citations, n=8,943) justifies HIGH confidence rating. Standard deviations and regional means well-documented.
- **Architectural Researcher**: 9/10 — Ranges directly translate to design spec. Romanian preference (140 cm) → max 1.6 people/m² comfortable; Argentine preference (80 cm) → 4.0 people/m² comfortable. Operationally clear.
- **Epistemologist**: 8/10 — Causal chain (climate → density → habituation → proxemic distance) is well-supported. Temperature correlation (12–18% variance) appropriately qualified.

**Median Score**: 8.6/10 — **STRONG**

#### 2. Regional Differentiation

- **Cross-Cultural Psychologist**: 9/10 — Sorokowska explicitly maps 42 countries; file summarizes into coherent regional clusters (North/East Europe, Central/South Europe, Latin America/Mediterranean, Middle East/South Asia). Groupings match cultural-linguistic families AND density patterns.
- **Environmental Psychologist**: 8/10 — Important deviations noted (e.g., Saudi Arabia high distance despite warm climate, due to religious/gender norms). Avoids simplistic climate determinism.
- **Architectural Researcher**: 9/10 — Clusters are actionable for design: "Rocky Mountain suburbs vs. dense Buenos Aires require different affordance concentrations."

**Median Score**: 8.7/10 — **EXCELLENT**: No stereotyping; explicitly notes deviations and confounds.

#### 3. Parameter Calibration

- **Cross-Cultural Psychologist**: 9/10 — Sorokowska ranges defensible. Romania 140 cm (highest), Argentina 80 cm (lowest) represent actual measured preferences, not inferred.
- **Psychometrician**: 9/10 — Gender and age effects quantified (women +4–7 cm, older +4–8 cm). Confidence levels reflect measurement variability appropriately.
- **Environmental Psychologist**: 8/10 — Social cue density thresholds (e.g., Romania 1.5–2.0 people/m² vs. Argentina 3.5–4.5) are derived from proxemic distance via geometry. Scaling is mathematically sound.
- **Architectural Researcher**: 8/10 — Affordance density requirement ("1 affordance per 2–3 people") is heuristic but defensible and testable.

**Median Score**: 8.5/10

#### 4. Confidence Accuracy

- **Psychometrician**: 9/10 — HIGH confidence justified by sample size, replication, and consistency. MEDIUM confidence for moderators (temperature, density) appropriate—variance explained 12–22% leaves substantial unexplained.
- **Epistemologist**: 8/10 — LOW confidence appropriately assigned to immigrant adaptation rates, virtual vs. in-person gaps, and critical periods. No overclaiming.

**Median Score**: 8.5/10

#### 5. Practical Utility

- **Architectural Researcher**: 9/10 — File enables concrete design decisions: "Design for Romanian low-income housing: max 2 people/m² comfortable → 15 people per 75 m² unit practical." Translates directly to floor-area allocations.
- **Environmental Psychologist**: 9/10 — Affordance guidance ("varied seating, visual zones, social focal points") operationalizes constraint satisfaction.
- **Cross-Cultural Psychologist**: 8/10 — Utility for multicultural spaces high; file acknowledges impossibility of satisfying all preferences simultaneously and recommends "compromise design, moderate satisfaction."

**Median Score**: 8.7/10

### Issues Flagged

1. **Stated vs. actual behavior gap noted but not calibrated**: File acknowledges 15–20 cm discrepancy between survey-stated and real-world behavior; ψ_culture multipliers do not appear to account for this.
2. **Immigrant effects underexplored**: "Do immigrants maintain or adopt host norms?" is open question. Field data needed.

### Recommended Adjustments

None critical. Minor enhancement: Add explicit note that ψ_culture multiplier for stated-vs-actual gap should be incorporated in constraint solver (recommended +0.12 m distance adjustment for application in real buildings).

### Vote: APPROVE

**5/5 Approve**

---

## CH-3: Visual Complexity Parameters

### File Metadata
- **Dimensions**: 3 core metrics (Berlyne inverted-U, fractal dimension, Shannon entropy)
- **Cross-cultural studies**: 2–3 direct comparative studies (Redies et al. 2020 Japanese vs. German; Van Geert 2025 Chinese vs. Dutch; Vartanian fMRI)
- **Evidence quality**: Mixed; strong theory, small sample sizes

### Evaluation by Dimension

#### 1. Empirical Grounding

- **Environmental Psychologist**: 7/10 — Berlyne inverted-U is robust and extensively replicated (2,471 citations). Cross-cultural validation less extensive: Redies (n=100+), Vartanian fMRI (n≈40 total), Van Geert (n presumably moderate, published 2025). Sample sizes small relative to claim scope.
- **Psychometrician**: 6/10 — **FLAG**: "Cross-cultural preference divergence" claims rest on studies with n<100 per group. Van Geert 2025 sample size not specified in file. Small-n studies are vulnerable to publication bias and have wide confidence intervals.
- **Architectural Researcher**: 8/10 — Fractal dimension (FD) is measurable metric; box-counting methodology standard. Japanese architectural mean FD=1.1, Baroque 1.80 are defensible estimates from visual inspection of exemplars.
- **Epistemologist**: 6/10 — Causal claim ("cultural aesthetic values directly calibrate preference thresholds") supported by cross-sectional correlation, not longitudinal or experimental design. Visual diet hypothesis is plausible but not conclusively proven.

**Median Score**: 6.75/10 — **CONCERN**: Small samples in cross-cultural studies inflate generalizability risk.

#### 2. Regional Differentiation

- **Cross-Cultural Psychologist**: 6/10 — Groupings (Japanese, Scandinavian, Baroque, Islamic, Western average) are architectural-tradition-based, not ethnographic/cultural. Risk: Conflates architectural tradition with population preference. E.g., Japanese FD preference 1.1 describes traditional temple architecture, not contemporary Tokyo resident preference (may have shifted toward 1.3 due to modernization).
- **Environmental Psychologist**: 7/10 — File acknowledges "confounding_factors: SES, education, personality (openness)" but does not control or quantify. Preference may be driven by education level, not culture.
- **Architectural Researcher**: 7/10 — Traditions are appropriately complex (e.g., "Baroque European" vs. "Western average" distinction); avoids oversimplification.

**Median Score**: 6.7/10

#### 3. Parameter Calibration

- **Environmental Psychologist**: 6/10 — Expected FD baselines (Japanese 1.10, Scandinavian 1.15, Islamic 1.65, Baroque 1.80) are reasonable but drawn from inspection of exemplars, not measurement of population samples.
- **Psychometrician**: 5/10 — LoadRate formula (0.3×FD + 0.4×EdgeDensity + 0.3×EntropyRate) is ad-hoc. No empirical calibration shown. Coefficients (0.3, 0.4, 0.3) appear arbitrary.
- **Architectural Researcher**: 7/10 — Error tolerance ranges (±0.15–0.25 FD) are defensible as ±1 SD but lack empirical grounding. Japanese tolerance ±0.15 vs. Baroque ±0.25 implies different variability, but where measured?

**Median Score**: 6/10 — **CONCERN**: LoadRate formula and tolerance ranges lack empirical calibration.

#### 4. Confidence Accuracy

- **Psychometrician**: 5/10 — File assigns HIGH confidence to Berlyne's inverted-U (appropriate) but then assigns MEDIUM confidence to "cross-cultural preference divergence" based on Redies et al. + Van Geert. Medium is appropriate for n<100 per-group studies, but file should note: replication needed in larger samples, and controlling for SES/education/personality.
- **Epistemologist**: 5/10 — File correctly identifies low-confidence items (individual differences, temporal plasticity, exact functional form). However, places unjustified confidence in LoadRate formula (no empirical basis).

**Median Score**: 5/10 — **CRITICAL**: Confidence in cross-cultural divergence should be MEDIUM, not used to support HIGH confidence in LoadRate calibration.

#### 5. Practical Utility

- **Architectural Researcher**: 8/10 — Fractal dimension as operationalized metric is useful. Designers can measure FD of facade and compare against cultural baseline. Predicts visual fatigue and cognitive load.
- **Environmental Psychologist**: 7/10 — Utility moderate; depends on accurate FD measurement and cultural baseline assignment. Measurement procedure (box-counting sensitivity) needs specification.

**Median Score**: 7.5/10

### Issues Flagged

1. **Small sample sizes in cross-cultural studies**: Redies et al., Vartanian, Van Geert are all n<100 per cultural group. Recommendation: larger replication studies before deployment.
2. **LoadRate formula not empirically derived**: Coefficients (0.3, 0.4, 0.3) are weights, but no data shown they predict cognitive load or fatigue in real populations.
3. **SES/education/personality confounds not controlled**: File acknowledges these but doesn't quantify effect. May explain apparent "cultural" divergence.
4. **Architectural traditions vs. contemporary preferences**: Japanese traditional FD≠contemporary Tokyo resident preference. Need contemporary sampling.

### Recommended Adjustments

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| Cross-cultural confidence | Mixed (some HIGH) | All MEDIUM | n<100 per group studies |
| LoadRate formula | Ad-hoc (0.3, 0.4, 0.3) | Empirical validation required | No calibration shown |
| Contemporary sampling | Traditional architecture | Add contemporary preferences | 100-year-old norms may not hold today |

### Vote: APPROVE WITH REVISIONS

**3 Approve + 2 Revisions**

**Conditions**:
- Downgrade cross-cultural divergence confidence to MEDIUM (currently some HIGH)
- Empirically validate LoadRate formula or remove it pending validation
- Add contemporary visual preference data (not just architectural tradition exemplars)

---

## CH-4: Ceiling Height Parameters

### File Metadata
- **Dimensions**: 2 core parameter groups (Meyers-Levy-Zhu priming, CVA calibration)
- **Empirical basis**: Single landmark study (Meyers-Levy & Zhu 2007, 1283 citations) + architectural standards
- **Evidence quality**: High for Meyers-Levy effect, uncertain for cross-cultural generalization

### Evaluation by Dimension

#### 1. Empirical Grounding

- **Environmental Psychologist**: 8/10 — Meyers-Levy & Zhu (2007) is robust and influential (1283 citations). Three laboratory studies with consistent effects: high ceiling → abstract/relational thinking; low ceiling → concrete/detail thinking. Effect sizes d~0.5–0.8 defensible.
- **Psychometrician**: 6/10 — **FLAG**: "No published replication studies or replication failures located; effect plausible but not validated via modern replication initiatives." This is significant. 2007 landmark study predates Registered Reports era. Reproducibility not confirmed.
- **Architectural Researcher**: 8/10 — Residential ceiling height standards (Japan 2.4m, USA 2.70m, N. Europe 2.5–2.6m) are well-documented from building codes.
- **Epistemologist**: 6/10 — Causal mechanism (ceiling height → vertical volume → freedom vs. confinement prime) is plausible but not mechanistically proven. Why does vertical space (not horizontal) prime conceptual freedom? Speculative.
- **Cross-Cultural Psychologist**: 5/10 — **CRITICAL**: "No evidence that non-residential Meyers-Levy effect generalizes cross-culturally to residential habituation." File explicitly notes this limitation but proceeds with CV calibration anyway. Residential adaptation may differ from lab priming.

**Median Score**: 6.6/10 — **CONCERN**: Central empirical basis (Meyers-Levy) lacks replication; generalization to residential cross-cultural contexts untested.

#### 2. Regional Differentiation

- **Architectural Researcher**: 8/10 — Three regional clusters (Japan, USA, Northern Europe) match economic development and housing constraints. Defensible.
- **Cross-Cultural Psychologist**: 6/10 — File groups Japan as monolith; ignores regional variation (Tokyo luxury 3.0m vs. rural 2.2m). "Residential ceiling heights" implies owner-occupied; doesn't address rental stock, which may differ.

**Median Score**: 7/10

#### 3. Parameter Calibration

- **Environmental Psychologist**: 7/10 — Expectancy violation formula (Δ_height = measured − baseline; Z_ceil = Δ_height / SD, SD≈0.25m) is defensible. Japanese in US living room example (2.4→2.7m, Δ=0.3m, Z=1.2) shows moderate effect.
- **Psychometrician**: 5/10 — SD_cultural=0.25m is assumed, not measured. Building code compliance ranges suggest variation (Japan 2.1–3.0m across residential stock), implying larger SD. If true SD is 0.35m, Z-scores shift downward, effect sizes smaller.
- **Architectural Researcher**: 7/10 — ControlEfficacy and NarrativeCoherence formulas (α_ceil=0.15, β_ceil=0.08) are reasonable but lack empirical validation.

**Median Score**: 6.3/10 — **CONCERN**: Critical parameters (SD_cultural, α_ceil, β_ceil) not empirically calibrated.

#### 4. Confidence Accuracy

- **Psychometrician**: 6/10 — HIGH confidence in Meyers-Levy effect is justified; HIGH confidence in residential calibration is NOT. File conflates lab effect robustness with real-world applicability.
- **Environmental Psychologist**: 7/10 — Confidence assessment section appropriately notes MEDIUM confidence for expectancy violation effects (not directly tested for ceiling height) and LOW confidence for individual differences.

**Median Score**: 6.5/10

#### 5. Practical Utility

- **Architectural Researcher**: 8/10 — Utility high; architects can design ceiling heights strategically to prime processing type. Actionable for hospitality (high for creativity), detail-focused work (low), etc.
- **Environmental Psychologist**: 6/10 — Utility depends on field validation. Lab priming effect may not persist in real residential contexts with high emotional stakes and customization.

**Median Score**: 7/10

### Issues Flagged

1. **Meyers-Levy effect not replicated post-2007**: No modern Registered Reports validation. Robustness unknown.
2. **No residential cross-cultural validation**: Meyers-Levy tested lab/retail; residential habituation effects may differ.
3. **Individual differences not modeled**: Height, anxiety, personality (openness) likely moderate effect. Model treats all within-culture as uniform.
4. **SD_cultural (0.25m) assumed, not measured**: Actual building code variance suggests larger SD; if true, effect sizes shrink.
5. **Non-residential generalization untested**: Offices, hospitals, schools likely differ. CH-4 generalization to all residential spaces risky.

### Recommended Adjustments

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| SD_cultural | 0.25m (assumed) | 0.30–0.35m or empirically measured | Building code ranges suggest larger variability |
| Meyers-Levy applicability | Applied to residential | Conditional: lab priming, not residential habituation tested | Generalization unvalidated |
| Individual differences | Not modeled | Modeled or flagged as constraint | Height, anxiety, personality moderate effect |

### Vote: APPROVE WITH REVISIONS

**4/5 Approve + 1/5 Revisions**

**Conditions**:
- Empirically measure SD_cultural for Japan, USA, Northern Europe building stock
- Conduct residential field study validating Meyers-Levy generalization
- Add individual difference moderators (height, trait anxiety) or flag as limitation
- Fund replication of Meyers-Levy effect via Registered Report before live deployment

---

## CH-5: Nature/Artifice Parameters

### File Metadata
- **Dimensions**: 4 core parameter groups (phenomenon spectrum, historical mechanisms, cross-cultural evidence, CVA calibration)
- **Regions**: 5 regional baselines (East Asian, Scandinavian, Western North American, Islamic, Aboriginal)
- **Evidence quality**: Mixed; strong historical scholarship, moderate empirical psychology, low on adaptation kinetics

### Evaluation by Dimension

#### 1. Empirical Grounding

- **Cross-Cultural Psychologist**: 8/10 — Nasar (1988) and Maedicke et al. (2010) provide solid empirical comparison. Gotfried & Marans (2023) 41-country nature-connectivity study is large-scale and well-designed.
- **Environmental Psychologist**: 7/10 — Historical causation (post-Romantic Western nostalgia, post-WWII Japanese urbanization) is well-documented. Empirical connection to contemporary preferences is less direct.
- **Psychometrician**: 6/10 — Cross-cultural studies exist (Nasar, Maedicke) but not systematic measurement of the same landscapes across populations. Comparison based on different stimuli (Western subjects rate Western landscapes; Japanese rate Japanese landscapes) confounds stimulus with cultural response.
- **Epistemologist**: 7/10 — Historical narrative (technological prowess → control, climate → resource management → control preference) is coherent. Causality from history to contemporary preference is inferential, not proven.

**Median Score**: 7/10

#### 2. Regional Differentiation

- **Cross-Cultural Psychologist**: 7/10 — East Asian (control), Scandinavian (wild), Western (intermediate), Islamic (bounded/water-centered), Aboriginal (spiritual integration) is nuanced and avoids stereotyping. Acknowledges within-region variation.
- **Environmental Psychologist**: 8/10 — Immigrant evidence (Kaplan & Kaplan 2002) showing East Asian immigrants maintain control preference in N. America supports cultural specificity.

**Median Score**: 7.5/10

#### 3. Parameter Calibration

- **Environmental Psychologist**: 6/10 — Preference scores (East Asia 0.15, Scandinavia 0.80, Western 0.45, Islamic 0.30) are ordinal, not measured on absolute scale. Intervals between values (0.15→0.45=0.30 interval) may not represent equal psychological distance.
- **Psychometrician**: 5/10 — **FLAG**: Immigrant adaptation rate (1% per year) is claimed but attributed to "limited studies." No citation provided. Recommends "~1% preference shift per year for first 5 years, then plateau" without source. This is a critical, testable claim; needs empirical grounding.
- **Architectural Researcher**: 6/10 — Practical guidance ("design for medium-degree wildness") is vague. What is "medium"? FD analogous to visual complexity would be useful.

**Median Score**: 5.7/10 — **CRITICAL CONCERN**: Immigrant adaptation rate (1%/year) is unjustified and central to model.

#### 4. Confidence Accuracy

- **Psychometrician**: 5/10 — **CRITICAL**: Immigrant adaptation rates assigned to MEDIUM confidence, but source is "limited studies" with no explicit citation. Should be LOW confidence or removed.
- **Epistemologist**: 6/10 — File appropriately flags "temporal plasticity unknown" and "critical periods unknown" as low-confidence. However, immigrant adaptation rate is presented as MED confidence without justification.

**Median Score**: 5.5/10

#### 5. Practical Utility

- **Architectural Researcher**: 7/10 — File acknowledges "genuine incompatibility constraint: design cannot maximize coherence for Japanese and Scandinavian occupants simultaneously." This is honest and valuable for designers. Practical utility high in identifying constraint.
- **Environmental Psychologist**: 6/10 — Utility depends on validating prediction error mechanism and landscape control operationalization.

**Median Score**: 6.5/10

### Issues Flagged

1. **Immigrant adaptation rate unjustified**: Claim "~1% preference shift per year" lacks explicit source. This is central to model; needs citation or empirical validation.
2. **Cross-stimulus confound**: Nasar (1988) and Maedicke (2010) did not measure preferences for identical stimuli across populations; comparison is indirect.
3. **Ordinal vs. cardinal scale ambiguity**: Preference scores (0.15–0.80) presented without interval-scale validation.
4. **Predictive processing mechanism untested**: Central hypothesis that prediction error drives coherence violations has no fMRI evidence in landscape contexts.
5. **Contemporary preferences vs. traditional aesthetics**: Like CH-3, conflates traditional garden design with contemporary population preferences (esp. East Asia modernization effects).

### Recommended Adjustments

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| Immigrant adaptation rate | 1%/year (MED confidence) | Removal or LOW confidence with explicit uncertainty | Lacks citation; critical to model |
| Landscape preference operationalization | Ordinal (0–1 scale) | Fractal dimension analog or interval-scale metric | Ambiguity about interval properties |
| Prediction error mechanism | Theoretical | Flag as hypothesis pending fMRI validation | No neuroimaging evidence |

### Vote: APPROVE WITH REVISIONS

**3/5 Approve + 2/5 Revisions**

**Conditions**:
- Provide explicit citation for 1%/year immigrant adaptation rate or revise to LOW confidence / remove
- Conduct cross-stimulus comparison study (Japanese, Scandinavian, Western subjects rate identical landscapes)
- Operationalize landscape control preference via measurable metric (fractal dimension analog)
- Fund fMRI study of prediction error in landscape contexts before deployment

---

## CH-6: Symmetry Parameters

### File Metadata
- **Dimensions**: 3 core parameter groups (universal symmetry detection, symmetry regime taxonomy, neural mechanisms)
- **Empirical basis**: Eglash (1999) African fractals, Redies et al. symmetry detection, Reber processing fluency
- **Evidence quality**: Strong on neural substrate (Tier 1) and historical documentation, moderate on cross-cultural preference divergence

### Evaluation by Dimension

#### 1. Empirical Grounding

- **Environmental Psychologist**: 8/10 — Eglash African Fractals (1999) is landmark; 547 citations; revolutionary documentation that traditional African architecture is deliberately fractal, not accidentally asymmetric. Groundbreaking.
- **Psychometrician**: 8/10 — Bertamini et al. (2004) and Evans et al. (2003) on bilateral symmetry detection (~30–50ms faster than asymmetry) is well-replicated, pre-attentive, automatic.
- **Architectural Researcher**: 8/10 — Western bilateral symmetry documented in classical/neoclassical architecture; Islamic tessellation patterns mathematically precise (wallpaper groups p4mm, c2mm).
- **Epistemologist**: 7/10 — Correct to distinguish Tier 1 (faster detection) from Tier 2 (preference). File appropriately notes: "faster detection ≠ aesthetic preference for symmetry." This is epistemologically rigorous.

**Median Score**: 7.75/10 — **STRONG**

#### 2. Regional Differentiation

- **Cross-Cultural Psychologist**: 8/10 — Four distinct symmetry regimes (Western bilateral, African fractal, East Asian context-dependent, Islamic geometric) are well-documented with exemplars and architectural traditions.
- **Architectural Researcher**: 9/10 — Exemplars are concrete: Kotoko compounds (Cameroon), Ashanti courtyards (Ghana), Japanese tea rooms, Islamic zellij tilework. Avoids abstraction.
- **Anthropologist**: N/A (not on panel) — (Note: If present, would assess whether fractal vs. bilateral is culturally/ecologically determined or coincidental)

**Median Score**: 8.5/10 — **EXCELLENT**

#### 3. Parameter Calibration

- **Environmental Psychologist**: 7/10 — Measured fractal dimensions for African architecture (FD≈1.8–2.0 for Kotoko; D≈1.8–2.0 for Mofou). Western bilateral FD≈1.0 (mirror symmetric). Japanese context-dependent. Calibrations defensible.
- **Psychometrician**: 7/10 — Confidence levels appropriately assigned: HIGH for Eglash documentation and Western bilateralism; MEDIUM for cross-cultural divergence; LOW for developmental onset and adult plasticity.
- **Architectural Researcher**: 8/10 — Operationalization clear: measure FD of spatial layout; compare against cultural baseline; predict whether inhabitants experience layout as organic/alive (fractal) vs. rigid/formal (bilateral).

**Median Score**: 7.3/10

#### 4. Confidence Accuracy

- **Psychometrician**: 8/10 — Confidence assessment appropriate. Eglash is foundational (HIGH); cross-cultural divergence is inferred from architectural traditions (MEDIUM); developmental plasticity is unknown (LOW).
- **Epistemologist**: 8/10 — File appropriately distinguishes level of certainty and flags research gaps (no fMRI of African vs. Western subjects viewing spatial layouts).

**Median Score**: 8/10 — **STRONG**

#### 5. Practical Utility

- **Architectural Researcher**: 9/10 — Utility high for multicultural design. Designers can measure FD of space, recognize whether it reflects Western bilateral tradition or African fractal tradition, and predict inhabitant response.
- **Environmental Psychologist**: 8/10 — Prediction error mechanism (symmetry mismatch triggers PE) is testable; allows real-time feedback.

**Median Score**: 8.5/10

### Issues Flagged

1. **Cross-cultural measurement gap critical**: File acknowledges "Gap 1: No systematic study comparing African, Western, East Asian, Islamic populations' preferences for bilateral vs. fractal vs. asymmetric layouts" in same VR or physical environments. This is major empirical gap.
2. **Developmental onset age unknown**: At what age do African children develop fractal preference? (Age 3, 5, 7, 12?) No longitudinal data.
3. **Adult plasticity unknown**: Do migrants retain childhood symmetry preference or adapt? Unknown.
4. **East Asian paradox**: Context-dependent symmetry preference (bilateral in formal, asymmetric in intimate) is interesting but mechanism unclear. Separate constraint needed?

### Recommended Adjustments

| Parameter | Current | Recommended | Rationale |
|-----------|---------|-------------|-----------|
| Cross-cultural measurement | Acknowledged gap | Mandatory field study | No direct comparison; central assumption untested |
| Developmental onset | Unknown | Empirical study (ages 3–12) | Unknown critical period |
| East Asian formula | Context-dependent | Explicit context-detection rule | Mechanism for formal vs. intimate distinction needed |

### Vote: APPROVE WITH REVISIONS

**4/5 Approve + 1/5 Revisions**

**Conditions**:
- Conduct cross-cultural study comparing African, Western, East Asian, Islamic subjects' spatial layout preferences (same environments)
- Establish developmental onset age for fractal preference in African children
- Field-test adult plasticity in migrants (do adult African immigrants to Western countries shift symmetry preference?)
- Model formal vs. intimate context detection explicitly for East Asian constraint

---

## CH-7: Color Temperature Parameters

### File Metadata
- **Dimensions**: 4 core parameter groups (CCT preference spectrum, historical causation, Kruithof curve hypothesis, CVA calibration)
- **Empirical basis**: Post-WWII Japanese fluorescent adoption, NTSC-J display standard (9300K), Kruithof (1941) original study
- **Evidence quality**: High on historical documentation, LOW on direct cross-cultural validation of Kruithof hypothesis

### Evaluation by Dimension

#### 1. Empirical Grounding

- **Cross-Cultural Psychologist**: 7/10 — Post-WWII Japanese fluorescent adoption (1950s–1960s) is well-documented historical fact. NTSC-J 9300K standard (1960–2011) is real technical standard affecting three generations of display exposure. Market evidence (East Asian LEDs offered 4000–6500K) is observable.
- **Psychometrician**: 4/10 — **CRITICAL FLAG**: File's central hypothesis—"Kruithof curve is culturally determined, not universal"—is untested. Original Kruithof (1941) study never replicated cross-culturally. File states: "Testable predictions: [1) Japanese should rate 2700K as unpleasant at low illuminance...] Research status: Untested."
- **Epistemologist**: 4/10 — File acknowledges Kruithof replication gap but proceeds to calibrate CVA parameters as if hypothesis is established. This is circular: using untested hypothesis to justify parameter settings.
- **Environmental Psychologist**: 6/10 — Color constancy mechanism (visual system learns reference white in childhood) is plausible and consistent with color science literature. Proposition that Japanese internal reference is blue-shifted due to fluorescent + 9300K displays is reasonable but not directly measured.

**Median Score**: 5.25/10 — **CRITICAL CONCERN**: Central mechanistic hypothesis untested; parameter calibration rests on speculation.

#### 2. Regional Differentiation

- **Cross-Cultural Psychologist**: 7/10 — Two main populations (East Asian, Western). Islamic and other traditions not addressed. Reasonable to focus on two largest divergence (East Asia vs. West), but geographic incompleteness noted.
- **Architectural Researcher**: 6/10 — File appropriately notes that "neutral 4000K is actually culture-specific, not truly neutral." Important design implication.

**Median Score**: 6.5/10

#### 3. Parameter Calibration

- **Psychometrician**: 3/10 — **CRITICAL**: All CVA calibrations (MultisensoryCoherence, NarrativeCoherence, PredictionError, ProcessingCost adjustments) depend on Kruithof curve cultural shift hypothesis. If hypothesis is false or partially false, all downstream parameters are miscalibrated. Example: Japanese person in Western 2700K rated as "large PE" (predicted 5000K, received 2700K). But if Kruithof was universal all along, no PE warranted.
- **Environmental Psychologist**: 4/10 — File lacks migrant adaptation data. When Japanese relocate to USA, do they: (A) shift preferences toward 2700K over time? (B) remain anchored at 5000K preference? (C) develop dual preferences? UNKNOWN. Field data at 3mo, 6mo, 12mo, 24mo post-arrival would be essential for calibration.
- **Architectural Researcher**: 5/10 — Operationalization ("Design for East Asian: 5000–6500K residential") is actionable but assumes Kruithof hypothesis is correct. If hypothesis is wrong, recommendation is misguided.

**Median Score**: 4/10 — **CRITICAL CONCERN**: Calibrations built on untested hypothesis.

#### 4. Confidence Accuracy

- **Psychometrician**: 2/10 — **SEVERE**: File assigns MEDIUM confidence to Kruithof cultural shift (theoretical coherence, limited evidence) and HIGH confidence to East Asian vs. Western CCT preference (market data, display standards). But file SIMULTANEOUSLY admits research status is "Untested" for core mechanism and "Gap 1–4: research gaps unclosed." Confidence is inflated relative to evidence.
- **Epistemologist**: 2/10 — **CRITICAL**: Confidence levels inconsistent with evidence transparency. Market data (East Asians prefer cool white) is HIGH confidence. But WHY (color constancy mechanism) is untested. File conflates "difference exists" (HIGH confidence) with "we understand mechanism" (LOW confidence) but then uses mechanism to justify CVA parameters.

**Median Score**: 2/10 — **CRITICAL OVERCONFIDENCE**

#### 5. Practical Utility

- **Architectural Researcher**: 6/10 — Utility is HIGH if Kruithof hypothesis is correct (can design culturally appropriate lighting). Utility is NEGATIVE if hypothesis is wrong (misdirects design toward uncomfortable lighting).
- **Environmental Psychologist**: 3/10 — Deployment risk is HIGH due to untested mechanism. Field trial mandatory before live use.

**Median Score**: 4.5/10

### Issues Flagged

1. **Kruithof curve hypothesis untested across cultures**: Central mechanism (visual system calibration to 9300K displays + fluorescent baseline) is plausible but has ZERO direct empirical support. File lists it as research gap.
2. **Migration adaptation data missing**: Do Japanese immigrants shift CCT preference toward Western norms over years? Unknown. Essential for field deployment.
3. **Circadian physiology untested**: Hypothesis that Japanese individuals (habituated to high-CCT) show different melatonin sensitivity. No data.
4. **Neural correlates unmeasured**: No fMRI of Japanese vs. Western subjects viewing unexpected CCT. Which brain regions active?
5. **Confidence inflation**: File assigns MEDIUM–HIGH confidence to empirically unvalidated mechanisms.

### Recommended Adjustments

| Parameter | Current Status | Recommended | Rationale |
|-----------|---|---|---|
| Kruithof cultural shift hypothesis | Untested (noted) | Flag as HYPOTHESIS pending validation | Currently used to justify calibrations |
| Migration CCT preference shift | Unknown | Mandatory field study (3mo, 6mo, 12mo, 24mo) | Essential for adaptation models |
| CVA parameter confidence | MEDIUM–HIGH on mechanism | Reduce to LOW until Kruithof validated | Mechanism untested |
| Deployment readiness | Field trial assumed | Conditional: Requires Kruithof validation first | Too much uncertainty for live use |

### Vote: REVISE AND RESUBMIT

**1/5 Approve + 3/5 Revisions + 1/5 Reject**

**Critical Conditions for Resubmission**:
1. **Before resubmission**: Conduct cross-cultural Kruithof curve replication study (Japanese, Western, other populations rate illuminance + CCT for pleasantness; validate whether pleasant region truly shifts rightward for East Asian subjects).
2. **Before resubmission**: Collect migration data (Japanese in USA at 3mo, 6mo, 12mo, 24mo post-arrival; measure CCT preference shift trajectory).
3. **Before resubmission**: Explicitly downgrade confidence levels for all untested mechanisms to LOW.
4. **Condition for deployment**: File may proceed to field trial phase ONLY after Kruithof validation study completes. Live deployment in buildings affecting real residents cannot proceed on speculative mechanism.

---

## Cross-Cutting Concerns

### 1. Systematic Confidence Overstatement

Five of seven files (CH-1, CH-3, CH-5, CH-7, and partially CH-4) assign MEDIUM or HIGH confidence to mechanisms that rest on small sample sizes, untested hypotheses, or indirect inference.

**Concern**: ψ_culture multipliers are floating-point values (e.g., 0.70, 1.05) that imply calibrated precision, but underlying confidence is often <0.65. When ψ values are plugged into CVA constraint solvers, small multiplier errors cascade.

**Recommendation**: Before deployment, standardize confidence assessment across all files. Any mechanism not directly measured in cross-cultural populations should be assigned LOW confidence (0.25–0.40), MEDIUM (0.50–0.65), or HIGH (0.70–0.95) based on:
- Sample size (n<100 = max MEDIUM; n>500 = eligible for HIGH)
- Cross-cultural replication (replicated in ≥2 independent labs = higher; unreplicated = lower)
- Mechanism testing (direct measurement > inference > theoretical plausibility)

### 2. Missing Cross-Cultural Measurement Across Multiple Domains

CH-3 (visual complexity), CH-4 (ceiling height), CH-5 (nature/artifice), CH-6 (symmetry), and CH-7 (color temperature) all acknowledge research gaps where the SAME STIMULI have NOT been rated by subjects from different cultural backgrounds.

**Concern**: Files infer cross-cultural divergence from comparisons of different stimuli (Japanese rate Japanese landscapes; Western rate Western landscapes), introducing confound between cultural response and stimulus-specific properties.

**Recommendation**: Fund a systematic cross-cultural perception study where:
- N ≈ 50–100 subjects per cultural group (Japan, Germany/Western Europe, East Africa, Middle East, Latin America)
- Same stimuli rated on: visual complexity (FD), ceiling height perception, landscape nature/artifice preference, spatial symmetry (bilateral vs. fractal), lighting CCT preference
- Controlled for SES, education, personality, and migration history
- Data used to revalidate all CH parameters simultaneously

### 3. ψ_culture Multiplier Validation Gap

All seven files propose ψ_culture multipliers (e.g., CH-1 ProcessingCost 0.70 for Tokyo), but none show held-out cross-validation. No evidence that multipliers generalize to populations outside the original calibration set.

**Concern**: If multipliers are overfitted to limited sample (e.g., Tokyo n=20), deploying them system-wide will produce poor predictions for Seoul, Hong Kong, Shanghai, or rural Japan.

**Recommendation**: Before deployment, split calibration data 70/30 (train/test). Revalidate all ψ_culture multipliers on held-out test set. Report prediction error on unseen populations.

### 4. Individual Differences Largely Unmolded

Files acknowledge that personality (openness, need for structure), SES, education, anxiety, height, and other individual traits likely moderate cultural effects. However, most files do NOT model these as constraint violations or uncertainty bands.

**Concern**: Two Japanese residents in same space may have divergent CVA profiles depending on personality and SES. File treats all within-culture as uniform.

**Recommendation**: For deployment, introduce individual difference layers. E.g., "κ_nature baseline for East Asian = 0.15 ± 0.10 (SD reflects individual variation in openness, SES)." Range-based predictions more honest.

### 5. Temporal Plasticity Largely Unknown

CH-5 claims 1%/year immigrant adaptation; CH-1, CH-4, CH-7 note "plasticity unknown." No longitudinal data on whether lived experience in new cultural context reshapes perceptual baselines.

**Concern**: System assumes preferences are fixed from childhood. If adults can shift baselines over years, model is incomplete.

**Recommendation**: Fund 3-year longitudinal study of immigrants: Japanese to USA, Western Europeans to East Asia, etc. Measure preference shifts at baseline, 3mo, 6mo, 12mo, 24mo, 36mo. Establish timescale for adult relearning.

### 6. Aboriginal Australian and Other Underrepresented Populations

CH-5 includes Aboriginal Australian tradition (spiritual integration, not aesthetic object) but no parameters for Aboriginal residents' actual built-environment preferences. CH-2, CH-3, CH-4, CH-6, CH-7 do NOT address Aboriginal, Indigenous, or African populations except as historical exemplars (CH-6 Eglash).

**Concern**: ATLAS system claims cultural relevance but has calibrations for primarily OECD nations (Japan, Korea, Western Europe, North America) + Islamic Middle East. Remaining 80% of world's populations underrepresented.

**Recommendation**: Acknowledge limited geographic scope explicitly in deployment documentation. Do not claim universal applicability to Aboriginal Australian, Sub-Saharan African, South Asian, or Oceanic populations without data.

---

## Approved Thresholds and Deployment Parameters

### Approved ψ_culture Multipliers (Conditional)

The following ψ_culture multipliers are APPROVED for field trial use, conditional on validation in held-out populations:

#### CH-1: Noise Tolerance
- **ProcessingCost**:
  - East Asia high-density: 0.70 ✓
  - East Asia mid-density: 0.85 ✓
  - Western urban: 1.00 (baseline)
  - Western suburban: 1.05 ✓
  - Rural quiet: 1.20 ✓
- **MultisensoryCoherence**:
  - East Asia high-density: 0.80 ✓
  - East Asia mid-density: 0.88 ✓
  - Western urban: 1.00 (baseline)
  - Western suburban: 0.95 ✓

**Conditions**: Validate on Seoul, Shanghai, Hong Kong populations not in original calibration set.

#### CH-2: Proxemics
- **SocialCueDensity regional thresholds**: APPROVED as presented.
  - Romania/Hungary/Estonia: 1.5–2.0 people/m²
  - UK/Austria/Ukraine: 2.5–3.5 people/m²
  - Argentina/Peru/Bulgaria: 3.5–4.5 people/m²
  - Saudi Arabia/Pakistan: 2.0–3.0 people/m²

**Conditions**: None; Sorokowska data is gold standard.

#### CH-3: Visual Complexity
- **Fractal dimension baselines**: APPROVED with MEDIUM confidence
  - Japanese: FD 1.10 (error tolerance ±0.15)
  - Scandinavian: FD 1.18 (error tolerance ±0.20)
  - Islamic: FD 1.65 (error tolerance ±0.20)
  - Baroque: FD 1.80 (error tolerance ±0.25)
  - Western average: FD 1.40 (error tolerance ±0.25)

**Conditions**: Validate LoadRate formula empirically before using to trigger fatigue warnings.

#### CH-4: Ceiling Height
- **ControlEfficacy multiplier formula**: APPROVED with MEDIUM confidence
  - ψ_CE = 1.0 + 0.15 × Z_ceil (where Z_ceil is standardized deviation from cultural baseline)

**Conditions**: Replication of Meyers-Levy effect via Registered Report before live deployment.

#### CH-5: Nature/Artifice
- **Narrative coherence baselines**: APPROVED with MEDIUM confidence
  - East Asia: 0.15 (curated preference)
  - Scandinavia: 0.80 (wild preference)
  - Western: 0.45 (intermediate)
  - Islamic: 0.30 (bounded/water-centered)

**Conditions**: Remove or validate 1%/year immigrant adaptation rate before deployment.

#### CH-6: Symmetry
- **Fractal dimension baselines for spatial layout**: APPROVED with HIGH confidence
  - African fractal: FD 1.8–2.0
  - Western bilateral: FD ≈1.0
  - Islamic geometric: FD 1.5–1.7 (tessellation-based)
  - East Asian context-dependent: bilateral in formal (FD≈1.0), asymmetric in intimate (FD≈1.5)

**Conditions**: Cross-cultural measurement study validating preference divergence.

#### CH-7: Color Temperature
- **Regional preferred CCT ranges**: APPROVED with LOW confidence (field trial only)
  - East Asia residential: 5000–6500K
  - Western residential: 2700–3000K
  - East Asia office: 5500–6500K
  - Western office: 3500–4000K

**Conditions**: MANDATORY Kruithof curve replication before any architectural recommendation based on color temperature calibration. Field trial only; cannot deploy in buildings with real occupants until Kruithof validation complete.

---

## Conditions for Deployment

### Tier 1: Pre-Deployment (Before Field Trial Phase)

**MANDATORY before any deployment in buildings with real occupants:**

1. **CH-7 (Color Temperature)**: Complete Kruithof curve cross-cultural replication study (minimum 20 subjects per cultural group × 4 cultures × 3 illuminance levels = 240 subject-sessions).
   - **Responsible party**: Lighting/perceptual psychology lab
   - **Timeline**: 6 months
   - **Deliverable**: Publication or Preregistry showing whether pleasant region truly shifts rightward for East Asian subjects

2. **CH-4 (Ceiling Height)**: Replication of Meyers-Levy & Zhu (2007) via Registered Report.
   - **Responsible party**: Cognitive/environmental psychology lab
   - **Timeline**: 6 months
   - **Deliverable**: Registered Report showing effect replicates or identifies boundary conditions

3. **CH-5 (Nature/Artifice)**: Provide explicit source for 1%/year immigrant adaptation rate OR revise to LOW confidence / remove.
   - **Responsible party**: Citation archaeology + empirical validation if rate cannot be sourced
   - **Timeline**: 2 weeks (citation check); 18 months if empirical study needed

### Tier 2: Field Trial Phase (Conditional Approval)

**If Pre-Deployment tier is met**, ATLAS may proceed to field trial in controlled setting (new building, diverse occupant population, research partnership with architects/building managers, informed consent from occupants):**

1. **Cross-cultural Perception Study** (Concurrent): Rate same visual/acoustic/spatial/lighting stimuli across n=50 per cultural group (Japan, Western Europe, E. Africa, Middle East, Latin America). Revalidate all 7 CH parameters.
   - **Timeline**: 12 months parallel with field trial
   - **Deliverable**: Empirical revalidation of CH-1 through CH-7 on cross-cultural population

2. **Held-out Validation**: Split calibration data 70/30 (train/test). Revalidate all ψ_culture multipliers on held-out populations (e.g., if trained on Tokyo n=20, test on Seoul n=10, Hong Kong n=10).
   - **Timeline**: 3 months (concurrent with field trial design)
   - **Deliverable**: Prediction error on unseen populations

3. **Migration Longitudinal Study**: Recruit 30 Japanese immigrants to USA + 30 Western immigrants to East Asia. Measure CCT, noise tolerance, proxemics, complexity, ceiling height preferences at baseline, 3mo, 6mo, 12mo, 24mo.
   - **Timeline**: 24 months parallel with field trial
   - **Deliverable**: Revalidation or revision of CH-5 immigrant adaptation rates; data for all CH files' temporal plasticity models

### Tier 3: Live Deployment (Post-Field Trial)

**Only after field trial phase demonstrates:**

1. ψ_culture multipliers predict real occupant responses with <15% mean absolute error
2. Cross-cultural study confirms parameter generalizations
3. No significant harm or user dissatisfaction from culturally mismatched design interventions
4. Expert panel reconvenes to review field trial results and recommends deployment

---

## Panelist Recommendations Summary

### Cross-Cultural Psychologist

**Overall**: Files demonstrate sophistication in avoiding stereotypes and grounding in cross-cultural psychology literature. However, geographic scope limited to primarily OECD nations.

**Key recommendation**: Before deployment, acknowledge explicitly that ATLAS cultural calibrations apply to Japan, Korea, Western Europe, North America, and Islamic Middle East. Aboriginal Australian, Sub-Saharan African, South Asian, and Oceanic populations NOT adequately represented. Market targeting should reflect this limitation.

### Environmental Psychologist

**Overall**: Person-environment interaction mappings (e.g., proxemics → SocialCueDensity, noise → ProcessingCost) are theoretically sound. However, field validation critical.

**Key recommendation**: Field trial must include real-world feedback loop. Architects/occupants rate whether ATLAS recommendations improve wellbeing. Be prepared to revise ψ_culture multipliers if field data contradicts parameter predictions.

### Psychometrician

**Overall**: Confidence assessment structure is appropriate, but confidence values themselves are inflated relative to evidence quality.

**Key recommendation**: Downgrade confidence globally by 0.1–0.2 points until cross-cultural measurement studies complete. Replace ordinal scales (nature/artifice 0–1) with interval-scale metrics or explicitly note ordinal limitation.

### Architectural Researcher

**Overall**: Files operationalize parameters into actionable design guidance. Practical utility is strong IF underlying parameters are valid.

**Key recommendation**: In deployment, architects should receive not point estimates (FD=1.40 ± 0.25) but ranges and uncertainty bands reflecting confidence levels. Design tools should flag HIGH uncertainty (e.g., CH-7 color temperature) and recommend contingent design (tunable CCT) until validation complete.

### Epistemologist

**Overall**: Files appropriately distinguish Tier 1 (universal perceptual apparatus) from Tier 2 (cultural calibration). Epistemological humility evident. However, some mechanisms presented as more certain than evidence warrants.

**Key recommendation**: Before deployment, conduct Bayesian epistemic review. For each CH file, explicitly list: (A) what is certain (e.g., Japanese prefer cool light), (B) what is plausible (e.g., visual system calibration mechanism), (C) what is speculative (e.g., 1%/year adaptation rate). Make (B) and (C) visible in UI so architects/occupants understand uncertainty.

---

## Final Vote and Disposition

### Summary Vote

| File | Recommendation | Panelist Breakdown |
|------|---|---|
| **CH-1** | APPROVE WITH REVISIONS | 3Y + 2R |
| **CH-2** | APPROVE | 5Y |
| **CH-3** | APPROVE WITH REVISIONS | 3Y + 2R |
| **CH-4** | APPROVE WITH REVISIONS | 4Y + 1R |
| **CH-5** | APPROVE WITH REVISIONS | 3Y + 2R |
| **CH-6** | APPROVE WITH REVISIONS | 4Y + 1R |
| **CH-7** | REVISE AND RESUBMIT | 1Y + 3R + 1N |

### Tally
- **APPROVE (no revisions)**: 1 file (CH-2)
- **APPROVE WITH REVISIONS**: 5 files (CH-1, CH-3, CH-4, CH-5, CH-6)
- **REVISE AND RESUBMIT**: 1 file (CH-7)
- **REJECT**: 0 files

### Panel Disposition

**CONDITIONAL APPROVAL for field trial phase**, contingent on:

1. **Immediate (Pre-field trial)**: Revise CH-1, CH-3, CH-4, CH-5, CH-6 per panelist conditions (downgrade confidence, validate formulas, remove unjustified claims).
2. **Immediate**: CH-7 requires Kruithof curve replication study before any use in architectural recommendations.
3. **Concurrent (Field trial)**: Mandatory cross-cultural perception study, held-out validation, and migration longitudinal study.
4. **Post-trial**: Expert panel reconvenes to review field trial results before live deployment decision.

---

## Research Priorities for Panel-Recommended Funding

To close critical evidence gaps before deployment, the following research priorities are recommended for funding (estimated budgets):

| Priority | Study | Reason | Duration | Budget |
|----------|-------|--------|----------|--------|
| **P1 (Critical)** | CH-7 Kruithof curve replication (cross-cultural) | Central mechanism untested; affects color temperature calibration for all occupants | 6 months | $150K |
| **P1 (Critical)** | CH-4 Meyers-Levy ceiling height replication (Registered Report) | Replication status unknown; drives control efficacy and narrative coherence | 6 months | $100K |
| **P2 (High)** | Cross-cultural perception study (n=50 per group × 5 cultures) | Validates all 7 CH parameters on diverse population; enables revalidation of ψ_culture multipliers | 12 months | $200K |
| **P2 (High)** | Migration longitudinal study (n=30 Japanese→USA, n=30 Western→E.Asia, 24mo) | Empirically grounds CH-5 immigrant adaptation rate and tests temporal plasticity across all domains | 24 months | $180K |
| **P3 (Medium)** | CH-3 visual complexity sample size increase (n=200+ per group) | Current n<100 studies vulnerable to publication bias; larger replication | 9 months | $120K |
| **P3 (Medium)** | CH-6 African symmetry preference study (n=100 African subjects rating bilateral vs. fractal layouts) | Cross-cultural measurement gap; validates Eglash fractal hypothesis against Western subjects | 12 months | $150K |
| **P4 (Lower)** | Individual differences modeling (personality, SES, anxiety effects across all CH domains) | Refine uncertainty bands; move from group-level to person-level predictions | 18 months | $200K |

**Total estimated funding**: $1.1M over 24 months

---

## Appendix: Confidence Calibration Framework

For future CH parameter development, panels should use this framework:

### Confidence Level Definitions

| Level | Definition | Evidence Standard | Allowed in Deployment |
|-------|-----------|------------------|---------------------|
| **HIGH (0.75–0.95)** | Well-replicated finding with strong empirical support across multiple independent labs, cross-cultural validation, n>500, published in peer-reviewed journals, effect sizes consistent | Multiple independent replications; n>300 per group; cross-cultural measurement; effect size d>0.5 | YES (with monitoring) |
| **MEDIUM (0.50–0.74)** | Consistent findings with limited cross-cultural replication; smaller samples or indirect evidence; mechanistic theory sound but not directly tested | At least one published study; n>100 per group; theoretical coherence strong; some cross-cultural data | YES (field trial only; flag uncertainty) |
| **LOW (0.25–0.49)** | Mechanistic inference or extrapolation without direct measurement; plausible but untested; animal studies or Western populations only | Theoretical plausibility; consistent with indirect evidence; no direct cross-cultural measurement | CONDITIONAL (field trial only; cannot drive hard architectural decisions) |
| **VERY LOW (<0.25)** | Speculative; based on limited anecdotal evidence or logical extrapolation; no published data | Opinion, case study, or logical inference | NO (document as hypothesis; recommend research) |

### Questions Panels Should Ask for Each Parameter

1. **Replication**: Has this finding been independently replicated? (Y/N → affects confidence floor)
2. **Sample size**: n per cultural group? (n<50=max MEDIUM; n 50–300=eligible MEDIUM; n>300=eligible HIGH)
3. **Cross-cultural**: Measured in ≥2 cultural groups simultaneously? (NO→cap at MEDIUM; YES→eligible HIGH)
4. **Mechanism testing**: Is the underlying mechanism directly measured or inferred? (direct→+0.1; inferred→−0.2)
5. **Publication venue**: Peer-reviewed journal? (preprint/thesis→−0.1; top-tier journal→+0.05)
6. **Effect size**: |d| or |r|? (d>1.0 or r>0.6→+0.1; d 0.3–0.8→baseline; d<0.3→−0.1)

---

## Conclusion

The seven Cultural Habituation calibration parameter files represent a rigorous, evidence-informed approach to modeling culture-specific perceptual baselines for the ATLAS system. The panel commends the authors for epistemological transparency, appropriate qualification of uncertainty, and grounding in peer-reviewed literature.

However, **systematic gaps in cross-cultural empirical validation, untested mechanistic hypotheses (especially CH-7 Kruithof curve), and confidence overstatement relative to evidence quality pose deployment risks** if mitigated before field trial.

The panel recommends **CONDITIONAL APPROVAL for field trial** with mandatory research priorities (P1–P4) and robust data collection from real occupants to validate parameters before live deployment in buildings affecting real residents' wellbeing.

**This is a system affecting human experience of the built environment. Deployment must be careful, iterative, and grounded in continuous feedback from diverse populations.**

---

**Panel Review Completed**: 2026-03-02
**Recommendation Status**: Conditional Approval (Field Trial Phase)
**Next Milestone**: Kruithof Replication Study Results (6 months) + Cross-Cultural Perception Study (12 months)

