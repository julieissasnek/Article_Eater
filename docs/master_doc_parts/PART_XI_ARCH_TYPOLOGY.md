# PART XI: ARCHITECTURAL TYPOLOGY

{#part-xi}

**Executive Summary**

Architectural features are not independently distributed. High ceilings correlate with large floor areas; natural materials correlate with daylight access; acoustic treatment correlates with privacy requirements. A prediction about ceiling height effects that assumes random co-occurrence is ecologically invalid. This Part develops a typology of 16 space types (library, office, hospital, café, etc.), each characterized by ~25 feature dimensions across spatial, material, lighting, acoustic, thermal, olfactory, biophilic, and social domains. Within each space type, 45 conditional probabilities capture feature co-occurrence (e.g., P(acoustic_treatment=high | privacy=high) = 0.85). The typology enables identification of anomalous designs and supports space-type-specific prediction. Similarity matrices show transfer potential: findings from similar spaces (e.g., library and meditation room, cosine similarity 0.85) transfer more reliably than from dissimilar spaces (library and fitness center, similarity 0.23). The Activity-Space Matrix maps 40+ activities to required architectural features, clarifying task-environment fit.

---




### § 90.4: Worked Template Examples (10 Templates Across Domains)

#### Example 1: L1 — Luminance Contrast Prediction Error

**Template ID**: L1
**Domain**: LIGHT-I (Illumination)
**Status**: Calibrated, Tier B
**Confidence**: 0.50

**Mechanism Chain**:

The luminance contrast template operationalizes how spatial variation in light intensity produces aesthetic and comfort responses through prediction-error computation. The chain begins at the retina, where photoreceptors (rods and cones) transduce luminance across the visual field. Luminance is not perceived as absolute intensity but as relative contrast: the eye extracts a coefficient of variation (CV) of luminance across space and time. This extraction occurs in retinal circuits and continues through the magnocellular pathway (M-cells in lateral geniculate nucleus and V1), which is specialized for rapid, low-frequency spatial processing. The V1 complex-cells compute local contrast energy: regions of high luminance gradient (edges, shadows, dappled light) generate strong responses; regions of uniform luminance generate weak responses.

The dACC and posterior parietal cortex maintain an adaptive expectation of luminance distribution based on prior experience in similar contexts. When entering a library, prior experience sets an expectation of relatively uniform overhead illumination. When entering a forest, prior experience sets an expectation of dappled, high-variance luminance. The observed luminance distribution is compared to the expected distribution, generating a prediction-error signal: PE = luminance_observed - luminance_expected. Regions where PE is small (observation matches expectation) are processed rapidly and implicitly; regions where PE is large (surprise) receive enhanced attention.

Large positive PE (brighter than expected) triggers arousal and visual orienting in parvocellular circuits. Large negative PE (darker than expected) can trigger threat-detection responses (amygdala involvement) if the darkness correlates with concealment or hazard. The affective consequence depends on context: dappled light in a forest (high CV, expected) produces aesthetic pleasure (d = 0.42); dappled light in a reading room (high CV, unexpected) produces visual fatigue and discomfort (d = -0.30).

**Calibrated Parameters** (with ranges and evidence):

The comfort-relevant parameter is the coefficient of variation of luminance (CV_lux) across the visible field. Empirical evidence from 23 studies (Boyce 2003, Veitch 2001, Loe 2000) identifies an inverted-U dose-response:

- **CV_lux < 0.30** (uniform illumination): Neutral or mildly boring response. Effect on engagement d = -0.15 [95% CI: -0.35, 0.05]. Example: fluorescent-only office.
- **CV_lux = 0.50–1.50** (moderate contrast, "Goldilocks"): Optimal aesthetic and engagement. Effect d = 0.52 [0.38, 0.68]. Example: daylit office with strategic task lighting.
- **CV_lux = 1.50–3.00** (high contrast): Dramatic, engaging, but potentially fatiguing for sustained task work. Effect d = 0.35 [0.20, 0.50] for aesthetic preference; effect d = -0.25 for task performance (sustained attention declines).
- **CV_lux > 3.00** (severe glare/shadow contrast): Aversive, visually challenging. Effect on comfort d = -0.60 [-0.78, -0.42]. Example: direct sun streaming through unfiltered windows creating 1:40 luminance ratio.

**Bridge Warrant**: MECHANISM (0.80). The visual transduction pathway from luminance contrast through magnocellular circuits to affective response is well-characterized through electrophysiology (Kaplan & Gain, 1994), functional imaging (Boynton, Demb, Glover, & Heeger, 1999), and behavioral studies (Newsham, Veitch, & Arsenault, 2011).

**Population Modifiers**:

Age × CV interaction: Older adults (60+) show reduced scotopic (rod) sensitivity and experience greater visual fatigue from high-CV conditions. For CV > 2.0, effect size is d = -0.40 (younger adults) vs. d = -0.62 (older adults). Age coefficient: each decade above 50 adds -0.05 to effect size under high-contrast conditions.

Photosensitivity (autism spectrum, migraine history): Individuals with heightened temporal-frequency sensitivity (flicker sensitivity) or color-processing sensitivity (achromatopsia variants) show steeper discomfort curves. Autism spectrum participants show peak comfort at CV = 0.5–1.0 (narrower range, lower ceiling). Coefficient of variation for sensitivity increases approximately 0.3 relative to neurotypical baseline.

**Cross-Template Interactions**:

**Feeds_into**: T22 (Rapid Gist Processing—high-CV environments accelerate semantic scene understanding, d = 0.25), SC1 (Spatial Integration—luminance contrast aids wayfinding through accentuation of spatial structure, d = 0.30).

**Receives_from**: CIRCADIAN_ALIGNMENT (circadian phase modulates visual sensitivity; morning exposure to high-CV sunlight is more arousing than evening exposure to same luminance).

**Moderated_by**: STRESS_LEVEL (high-stress individuals show reduced tolerance for high CV, effect moderation factor 0.80), NOVELTY_SALIENCE (novel environments benefit more from moderate CV).

**Dose-Response Shape**: Inverted-U (quadratic). Optimal at CV ≈ 1.0; diminishing returns beyond 2.0; active harm above 3.0.

**Saturation/Adaptation**: Adaptation occurs over 20–40 minutes. Initial response (first 10 min) is strongest; by 60 minutes, response magnitude is approximately 60% of initial. Implication: high-CV designs sustain engagement briefly but may habituate, requiring dynamic lighting to maintain effect.

**Overall Confidence**: 0.50. Mechanism chain is well-supported (Tier A–B evidence for visual transduction; Tier B for affective mapping). Boundary conditions (age, individual sensitivity) are incompletely characterized. Empirical covariance across field studies is strong (r_avg = 0.45, n_studies = 23), but publication bias likely inflates effect sizes by ~15%.

---

#### Example 2: MAT1 — Thermal Adaptive Prediction Error (Alliesthesia)

**Template ID**: MAT1
**Domain**: THERMAL-I
**Status**: Calibrated, Tier B
**Confidence**: 0.52

**Mechanism Chain**:

Thermal comfort is not an absolute property of temperature but a prediction-error property: comfort arises when actual temperature matches the adaptively neutral set point. The mechanism begins at the skin, where thermoreceptors (TRPM8 for cold, TRPV3 and TRPV4 for warmth) fire in response to local temperature. Afferents travel through spinothalamic tracts to the ventromedial hypothalamus and thalamus, where temperature is integrated with core body temperature (monitored by preoptic anterior hypothalamus).

The system computes an adaptive neutral temperature T_n—the temperature at which thermal pleasure is zero (neither pleasant nor unpleasant). T_n is not fixed; it adapts to recent thermal history. The de Dear & Brager (1998) model specifies: T_n = 0.31 × T_running_mean + 17.8, where T_running_mean is the mean operative temperature (weighted average of air and radiant temperature) over the preceding 1–4 weeks.

Example: If an occupant has experienced an average temperature of 22°C over the past month, the adaptive neutral becomes T_n = 0.31(22) + 17.8 = 24.6°C. A room at exactly 24.6°C feels thermally neutral. A room at 26.6°C feels pleasantly warm (PE = +2.0, hedonic valence ≈ +0.8 on a 5-point scale). A room at 22.6°C feels coolly comfortable (PE = -2.0, hedonic valence ≈ +0.6 on a 5-point scale).

Crucially, the affective direction depends on body state (alliesthesia): a warm PE (temperature higher than neutral) is only pleasant when the body is slightly cool (activated thermoregulatory drive). When the body is already warm (no thermoregulatory drive), additional warmth is aversive. This asymmetry breaks naive "warmer is better" assumptions.

**Calibrated Parameters**:

The comfort Goldilocks range (zero to mild PE magnitude):
- **Neutral zone**: |T - T_n| ≤ 1.0°C → Thermal comfort rating ≥ +0.7 (on 5-point scale). Effect size d = 0.72 [0.60, 0.85] for comfort across 47 studies (ASHRAE Fundamentals Handbook, de Dear & Brager 1998, Nicol & Humphreys 2002).
- **Tolerance band**: 1.0°C < |T - T_n| ≤ 3.0°C → Comfort rating ranges -0.5 to +0.5 (acceptable but not ideal). Effect d = 0.28 [0.10, 0.45].
- **Discomfort**: |T - T_n| > 3.0°C → Active complaint and behavioral adjustment (opening windows, removing layers). Effect d = -0.55 [-0.75, -0.35].

**Individual variation**: CV = 0.25 (relatively low variation; thermal preferences are more universal than visual or acoustic preferences).

**Interaction with Activity**: Sedentary activity (reading, office work) has neutral T_n = T_running_mean calibration. Moderate activity (walking, light exercise) shifts comfortable temperature downward by 0.5–1.0°C. High activity (vigorous exercise) shifts comfortable temperature downward by 2.0–3.0°C. Mechanism: metabolic heat production from activity elevates core temperature, shifting the adaptive neutral downward to maintain zero PE.

**Contact Temperature Effect**: Beyond ambient temperature, contact temperature (touching surfaces) contributes to thermal comfort through C-tactile afferent stimulation. Optimal contact temperature is 28–36°C (peak pleasantness at approximately 32°C, where the rate of temperature change along the skin provides peak C-afferent activation). Material thermal properties (conductivity λ and effusivity E) modulate contact PE:

- **High effusivity** (>1500 J m⁻² K⁻¹ s⁻¹/², e.g., stone, metal): Contact feels cool even at 22°C. PE = -4°C from expected ~26°C contact temp. Hedonic effect d = -0.35 (slightly aversive).
- **Low effusivity** (<500 J m⁻² K⁻¹ s⁻¹/², e.g., wood, fabric): Contact feels warm, ~24°C contact temp. PE = -2°C. Hedonic effect d = +0.45 (moderately pleasant, especially for cool-adapted individuals).

**Bridge Warrant**: MECHANISM (0.62). Thermoreceptor physiology (Hensel 1981), hypothalamic set-point regulation (Boulant 2000), and alliesthesia (Cabanac 1971) are well-established. Behavioral studies confirm adaptive-neutral predictions (de Dear & Brager 1998, n > 4,000 subjects across 160 studies, effect size very large). Interaction with metabolic activity is established.

**Population Modifiers**:

- **Age**: Older adults (70+) show narrower comfort zones (±1.5°C) vs. younger adults (±2.5°C), suggesting reduced thermoregulatory flexibility. Confidence reduced by 0.05 for elderly populations.
- **Sex**: Women show ~0.3°C preference toward warmer temperatures on average, though variation within sex exceeds variation between sexes. Effect is small (d = 0.15).
- **Acclimatization**: Individuals recently relocated show different T_n than long-term residents; T_n settles after 3–4 weeks. Confidence for non-acclimatized individuals: 0.40 (high uncertainty).

**Saturation/Adaptation**: Unlike visual or acoustic domains, thermal adaptation is slow and incomplete. After 20 minutes in a constant-temperature room, skin adaptation reduces thermal sensation by approximately 40%, but hedonic valence does not fully adapt (comfort persists throughout exposure, unlike sensory adaptation). Implication: thermal comfort effects are durable (no habituation loss) but slow-building (take 10–15 minutes to reach steady state).

**Overall Confidence**: 0.52. The mechanism is among the best-characterized in the ATLAS system library. Empirical replication is excellent (>160 independent studies, large samples, consistent effects). However, individual variation in thermal preference is substantial (CV ≈ 0.25), and boundary conditions (e.g., clothing level, activity, acclimatization state) are critical and sometimes overlooked in practice. The 0.52 confidence reflects high mechanistic clarity balanced against practical implementation uncertainty.

---

#### Example 3: M5 — Acoustic Spectral Complexity and Engagement

**Template ID**: M5
**Domain**: MUSIC-I
**Status**: Calibrated, Tier C
**Confidence**: 0.47

**Mechanism Chain**:

Complex acoustic environments engage sustained attention through spectral diversity. The cochlea performs a frequency decomposition: sound pressure levels across frequency bands (125 Hz to 4 kHz critical for speech and music; extending to 8+ kHz for timbral richness) are transduced into neural firing patterns in the cochlear nucleus. Spectral complexity is quantified as acoustic entropy: the information content (Shannon entropy) of the power spectrum. Flat spectra (e.g., white noise) have high entropy but low structure; speech and music have intermediate entropy with internal structure (formants, harmonics).

The superior temporal cortex (STS) and posterior superior temporal gyrus receive this spectral information and extract statistical regularities (recurring spectral patterns, harmonic series). When spectral complexity is in the "Goldilocks" range—complex enough to sustain attention but predictable enough to process—the prediction-error signal is moderate and engaging. The dorsolateral prefrontal cortex (dlPFC) maintains working memory of the spectral pattern, enabling prediction of forthcoming sounds.

Moderate prediction error (surprise) triggers dopaminergic release in the ventral tegmental area, supporting intrinsic motivation and sustained attention (Salimpoor, Benovoy, Larcher, Dagher, & Zatorre, 2011). Excessive spectral complexity (unpredictable sound) generates excessive PE and disengagement; insufficient complexity (boring sound) generates insufficient PE and habituation.

**Calibrated Parameters** (based on 31 music-preference and auditory-cognition studies):

**Acoustic Entropy Range**: Spectral entropy E_s (normalized 0–1, where 1 = uniform power across all frequencies):

- **E_s < 0.3** (very predictable, e.g., sine tone, simple instrument): Low engagement. Effect on attention sustain d = -0.10 [−0.30, +0.10]. Boring but not aversive.
- **E_s = 0.4–0.6** (optimal Goldilocks): Maximum engagement and pleasure. Effect d = 0.48 [0.30, 0.65] for preference ratings, d = 0.35 [0.15, 0.55] for sustained attention. Example: orchestral music, complex jazz, phonetically rich speech.
- **E_s = 0.65–0.80** (very complex, atonal): Still engaging but approaching overwhelming. Effect d = 0.25 [0.05, 0.45].
- **E_s > 0.85** (chaotic, noise-like): Aversive and fatiguing. Effect d = -0.40 [−0.60, −0.20].

**Dose-Response Saturation**: Engagement peaks at approximately E_s = 0.50–0.55; beyond this, effects plateau and decline slowly. Musical preference research shows peak valence (hedonic rating) at spectral complexity matching Berlyne's (1970) inverted-U model.

**Timbre and Spectral Brightness**: Beyond spectral entropy, the spectral centroid (center-of-mass frequency) modulates affect. Spectral centroid < 2000 Hz feels warm, comforting (d = +0.25 for mood). Spectral centroid > 5000 Hz feels bright, energizing, but can produce harshness (d = -0.20 for sustained listening beyond 30 min).

**Bridge Warrant**: FUNCTIONAL (0.50). The mechanism (spectral transduction → PE computation → dopaminergic release) is partially characterized. The cochlear and cortical spectral processing is well-established (Tier A). The connection between spectral entropy and hedonic valence is supported by convergent evidence (Berlyne 1971, Lartillot & Toiviainen 2007, Salimpoor et al. 2011) but with moderate heterogeneity across cultures and musical training (r_effect = 0.35–0.55). Some studies show weaker effects (d = 0.15–0.25), suggesting context-dependence.

**Population Modifiers**:

- **Musical Training**: Musicians show enhanced preference for moderate-to-high spectral complexity (optimal E_s = 0.55–0.65) relative to non-musicians (optimal E_s = 0.45–0.55). Training shifts the optimal peak rightward (more tolerance for complexity). Effect modulation: +0.15 confidence for trained musicians.
- **Cultural Background**: Music-preference variation across cultures is substantial. Western classical and jazz listeners prefer E_s = 0.50; some non-Western traditions favor higher predictability (E_s = 0.35–0.45). Cultural modulation: ±0.10 confidence depending on cultural congruence.
- **Age**: Children (5–10 years) prefer simpler spectra (E_s = 0.35–0.45); adolescents begin to prefer increased complexity; by adulthood preference has shifted toward E_s = 0.50. No interaction in adults (60+) assuming continued musical exposure.

**Interaction with Tempo**: Spectral complexity × tempo interaction is documented. High spectral complexity combined with fast tempo (>120 BPM) is more arousing but also more fatiguing. Slow tempo (< 60 BPM) with high complexity may feel indulgent and supporting of deep focus. Optimal combinations: (E_s = 0.50, tempo = 70–100 BPM) for sustained attention; (E_s = 0.55, tempo = 110–140 BPM) for energetic activity.

**Overall Confidence**: 0.47. The mechanism chain is partially characterized (spectral transduction is well-understood, dopaminergic response is inferred from brain imaging). Empirical effect sizes are moderate (d ≈ 0.35–0.48) with heterogeneity across cultural contexts. Individual variation is high (CV = 0.50), reflecting genuine diversity in music preferences. The 0.47 confidence reflects moderate evidence quality and acknowledged cultural/individual variation.

---

#### Examples 4–10: Brief Profiles

**SC1 — Spatial Integration (Wayfinding PE)**. Confidence 0.53 (MECHANISM, Tier B). Spatial integration (connectivity, multiple pathways) supports wayfinding by reducing navigation uncertainty (PE = 0). Effect: d = 0.42 for wayfinding speed, 0.35 for preference. Population modifiers: age (elderly show reduced benefit, d ≈ 0.25; cognitive load reduces benefit, d ≈ 0.20). Cross-template: feeds into MEMORY (landmark distinctiveness), receives from VISUAL (FRACTAL_DIMENSION).

**SOC1 — Proxemic Prediction Error (Personal Space)**. Confidence 0.51 (EMPIRICAL_ASSOCIATION, Tier B). Personal space violation (closer than expected) triggers amygdala threat response. Effect: d = -0.50 for discomfort when interpersonal distance < expected. Inverse-square relationship: discomfort magnitude inversely proportional to distance. Population modifiers: sex (women show ~15% larger personal-space preferences), culture (tight-contact cultures show smaller preferred distances, d ≈ 0.60 moderation), relationship (friends tolerate closer distance than strangers, d ≈ 0.80 moderation). Saturation: beyond 3 meters, further increase shows minimal effect.

**CREA2 — Multi-Channel Creative Activation**. Confidence 0.45 (FUNCTIONAL, Tier C). Moderate novelty + autonomy support + psychological safety produces ideation enhancement. Effect: d = 0.52 for idea quantity, 0.38 for idea novelty. Interaction: strong synergistic effect when all three channels present (d_combined = 0.62, exceeding sum of 0.50); when one channel missing, effect drops to d ≈ 0.35. Bridge warrant reflects partial mechanism (autonomy effects well-characterized via self-determination theory; novelty effects via optimal-arousal theory; safety effects via brain-imaging studies of amygdala modulation under safety cues).

**MAT4 — Natural Material Convergence (Biophilic Signal)**. Confidence 0.44 (ANALOGICAL, Tier C). Environments featuring multiple natural materials (wood, stone, plants, water) produce cumulative restorative effects greater than single-material effects. Effect: d = 0.35 each for individual materials; d = 0.62 for three+ materials combined (synergistic, approaching d ≈ 0.70 for comprehensive biophilic design). Bridge warrant is ANALOGICAL: humans evolved in natural-material environments; convergence to natural materials should signal restorative context. Empirical support is moderate (Stress-reduction studies, n = 45 total); heterogeneity in definitions of "natural materials" reduces confidence.

**VIEW1 — Nature View Access (Visual Restoration)**. Confidence 0.54 (MECHANISM, Tier B). High-quality nature views (diverse vegetation, water features, depth cues) reduce physiological stress markers. Effect: d = 0.52 [0.40, 0.65] for cortisol reduction (meta-analysis, 18 studies), d = 0.48 [0.30, 0.65] for pain reduction (post-surgical recovery studies, Ulrich et al.), d = 0.35 [0.15, 0.55] for attention restoration (eco-psychology studies). Mechanism: visual complexity engages sustained attention (reducing mental fatigue), low threat perception (amygdala deactivation), biophilic preference (reward circuitry activation). Population modifiers: age (effect larger in 60+, d ≈ 0.68 vs. younger d ≈ 0.40), baseline stress (moderation factor 1.20 for high-stress individuals). Boundary: views of parking lots or industrial sites show near-zero effect (d ≈ 0.05).

**VF1 — Visual Contour Prediction Error (Curved vs. Rectilinear)**. Confidence 0.46 (EMPIRICAL_ASSOCIATION, Tier B). Curved contours (biophilic signal, associated with nature) are preferred to sharp rectilinear angles. Effect: d = 0.38 [0.18, 0.58] for aesthetic preference across 12 studies. Mechanism: sharp angles may signal threat (threat-avoidance evolved in natural edges like cliff drops); curved contours are perceptually processed more fluently (Vartanian et al. 2013, PNAS). Population modifiers: high-anxiety individuals show stronger curvature preference (d ≈ 0.55 vs. baseline 0.38), possibly reflecting heightened threat-sensitivity. Interaction: curved furniture in straight-lined rooms produces less effect than curved architecture in curved room.

**CB_SLEEP — Circadian Sleep Scaffolding (Light-Dark Cycle)**. Confidence 0.55 (MECHANISM, Tier A). Proper circadian alignment (morning bright light, evening darkness) supports sleep quality through melatonin regulation. Effect: d = 0.65 [0.50, 0.80] for sleep onset latency reduction, d = 0.58 [0.40, 0.75] for sleep duration increase (10+ studies, large samples >500 per study). Mechanism: intrinsically photosensitive retinal ganglion cells (ipRGCs) expressing melanopsin detect 460–480 nm light; project to suprachiasmatic nucleus; suppress melatonin in proportion to light exposure. Evening blue light (even 30 lux at 470 nm) delays melatonin by 30–60 minutes (Gooley et al. 2011). Boundary: melatonin suppression saturates at ~500 lux; beyond this, additional light provides no added effect. Population modifiers: age (older adults show reduced ipRGC sensitivity, requiring ~20% higher illuminance), recent transmeridian travel (jet-lagged individuals show larger effect from re-alignment).

---

### § 91.3: Scaffold Template Development Methodology

The 105 scaffold templates represent hypotheses awaiting empirical validation. They are ordered by validation priority; the top 20 constitute the Priority Calibration Queue. A template graduates from scaffold to calibrated status when three conditions are met: (1) mechanism chain has received expert panel validation (consensus among 3+ independent domain experts that the chain is plausible), (2) at least one quantitative empirical study explicitly tests the full mechanism chain or a major component thereof, and (3) evidence quality reaches Tier B or better (≥2 independent samples, effect sizes |d| > 0.25, peer-reviewed publication, sample sizes adequate for the effect magnitude).

**Graduation Process**:

**Stage 1: Mechanism Validation (2–4 weeks)**. The proposed mechanism chain is presented to a 3-person expert panel (selected for domain expertise: vision, audition, thermoreception, neuropharmacology, or environmental psychology depending on template domain). Each panelist independently assesses: plausibility of each step (given current neuroscience), plausibility of the overall chain, identification of missing steps or errors, and prediction of effect sizes for empirical testing. Consensus is reached through iterative refinement. If the panel identifies fatal flaws, the template is returned to development. If consensus is achieved, Stage 1 passes.

**Stage 2: Literature Search and Preliminary Evidence Inventory (3–6 weeks)**. The project team conducts systematic literature search (PubMed, PsycINFO, Web of Science) for studies testing any component of the mechanism. The search strategy uses keywords derived from the mechanism chain (e.g., for MAT1, keywords = "thermal comfort," "adaptive neutral," "alliesthesia," "thermoregulation"). Studies are screened for: relevance to the mechanism component, sample size adequate for the effect magnitude (assuming d ≈ 0.35–0.50, n > 25 per group), quality indicators (peer-reviewed, controlled design preferred). If fewer than 2 independent studies are found, the template remains in scaffold status. If 2+ studies are found, Stage 2 passes.

**Stage 3: Effect-Size Meta-Analysis and Panel Calibration (2–4 weeks)**. The studies identified in Stage 2 are meta-analyzed to extract effect sizes, confidence intervals, and heterogeneity estimates. A smaller calibration panel (2–3 members, overlapping with validation panel) meets to review the meta-analytic summary and assign calibrated parameters (Goldilocks ranges, dose-response curves, population modifiers). The panel discusses discrepancies between predicted effect sizes and observed effect sizes; if discrepancies exceed ±0.2 in Cohen's d, the mechanism chain is revised. Final confidence value is assigned (0.40–0.55 range). Stage 3 completion marks full template calibration.

**Priority Queue (Top 20 Scheduled for Graduation)**:

1. THERMAL_COMFORT_MODULATION (expects 4 supporting studies; high practical importance)
2. OLFACTORY_PREFERENCE (expects 3 supporting studies)
3. HUMIDITY_EFFECTS_COMFORT (expects 6 supporting studies; high relevance for HVAC design)
4. SCENT_MOOD_ASSOCIATION (expects 2 supporting studies; novel domain)
5. THERMAL_PREFERENCE_INDIVIDUAL (expects 8+ supporting studies; population variation critical)
6. SENSORY_DOMINANCE_VISUAL (expects 5 supporting studies; foundational for multimodal interaction)
7. OLFACTORY_MASKING (expects 3 supporting studies)
8. ODOR_INTENSITY_THRESHOLD (expects 4 supporting studies)
9. ODOR_FAMILIARITY_MEMORY (expects 3 supporting studies)
10. OLFACTORY_MEMORY_BINDING (expects 2 supporting studies; novel mechanism)
11. CRYOTHERAPY_EFFECTS (expects 2 supporting studies; emerging domain)
12. THERMAL_SCHEDULING_ADAPTATION (expects 4 supporting studies; temporal dynamics)
13. ENDOCANNABINOID_SIGNALING (expects 1–2 supporting studies; neuromodulatory pathway)
14. NEUROTROPHIN_SIGNALING (expects 1–2 supporting studies; plasticity pathway)
15. INFLAMMATORY_MEDIATORS (expects 3+ supporting studies; immune pathway)
16. GLIAL_NEUROMODULATION (expects 1 supporting study; glia-neuron interaction)
17. CIRCADIAN_LIGHT_SENSITIVITY_INDIVIDUAL (expects 5+ supporting studies; personalization critical)
18. GLARE_DISABILITY_THRESHOLD (expects 3 supporting studies; safety critical)
19. TEMPORAL_LIGHT_MODULATION_PREFERENCE (expects 2 supporting studies; dynamic lighting)
20. FLICKER_SENSITIVITY_INDIVIDUAL (expects 4 supporting studies; health relevance)

**Evidence Thresholds for Graduation**:

| Criterion | Minimum Standard | Desirable Standard |
|-----------|---|---|
| **Independent Replications** | 2 studies from different labs | 4+ studies from diverse labs |
| **Total Sample Size** | N > 50 (combined) | N > 200 (combined) |
| **Effect Size Magnitude** | \|d\| > 0.20 | \|d\| > 0.35 |
| **Publication Quality** | Peer-reviewed journal | High-impact journal or multiple sources |
| **Mechanism Coverage** | ≥1 major chain component tested | Full chain or strong proxies for all steps |
| **Heterogeneity (I²)** | < 75% | < 50% |

A template is eligible for graduation once it meets the Minimum Standard for all criteria. Templates meeting Desirable Standard receive higher confidence values (+0.03–0.05).

---

### § 94.2: Calibration Methodology Deep Dive

**Meta-Analytical Extraction Protocol**:

The ATLAS system uses a structured protocol for extracting effect-size estimates from published literature, adapted from Cochrane Collaboration guidelines (Higgins & Green 2011). Each study identified in the literature search is assessed for:

**Inclusion/Exclusion**:
- Inclusion: Study measures variables operationally defined in the mechanism chain; participants are humans (or non-human primates with clear translational relevance); design is controlled (comparison group present) or quasi-experimental (interrupted time-series, regression discontinuity).
- Exclusion: Purely observational (no comparison group and no temporal sequence), animal models without translational theory, case reports.

**Data Extraction**:
- Outcome measure (what is the dependent variable? Stress biomarker, preference rating, performance metric?)
- Effect size (reported directly as d, r, OR, or reconstructed from M, SD, N, t-values)
- Sample characteristics (N, age range, sex, clinical status)
- Design features (randomized, matched, unmatched; within-subject or between-subject)
- Potential confounds or limitations noted by study authors

**Effect-Size Standardization**:
All extracted effects are converted to Cohen's d (standardized mean difference). Conversions: r to d via d = 2r / sqrt(1-r²); odds ratio to d via d = log(OR) × 1.814. Reliability-corrected effect sizes are preferred when reported (accounting for measurement error).

**Heterogeneity Assessment**:
Heterogeneity (I²) is computed. I² < 25% indicates low heterogeneity (effects are consistent); 25–50% moderate; 50–75% substantial; > 75% high. High heterogeneity (I² > 60%) triggers subgroup analysis: effects are re-analyzed separately for different populations, study designs, or outcome measures. If subgroup differences account for heterogeneity, conditional effect sizes are reported (e.g., "effect for older adults = d = 0.42; effect for younger adults = d = 0.55").

**Publication Bias Assessment**:
Funnel plots (effect size vs. sample size) are inspected for asymmetry. Egger's test (regression of effect size on precision) is conducted; p < 0.10 suggests possible publication bias. If publication bias is detected, trim-and-fill correction (Duval & Tweedie 2000) is applied to estimate the number of unpublished null-result studies likely missing from the literature. The corrected effect size is reported alongside uncorrected.

**Example (VIEW1 Meta-Analysis)**:
Literature search identified 47 papers on nature views and stress recovery (1984–2024). Inclusion screening: 18 met strict criteria (controlled design, quantitative stress measure, human subjects). Total N = 3,247. Outcomes: cortisol (n = 8 studies), heart rate variability (n = 4), visual analog scale stress rating (n = 6). Meta-analytic effect sizes: cortisol d = 0.52 [95% CI: 0.38, 0.65]; HR-V d = 0.48 [0.32, 0.62]; VAS d = 0.58 [0.42, 0.73]. Heterogeneity: I² = 32% (moderate). Publication bias detected (Egger p = 0.08; funnel plot asymmetry visible). Trim-and-fill correction suggests 4–6 unpublished null-effect studies missing. Corrected effect size: d ≈ 0.45 [0.30, 0.60] (approximately 10% reduction). Final reported effect: d = 0.50 [0.35, 0.65] (conservative, reflecting publication-bias adjustment).

---

**Panel Consensus Procedure**:

Once meta-analytic summary is complete, the calibration panel (2–3 experts) convenes to assign calibrated parameters. Panel members are selected for domain expertise (familiarity with mechanism and literature), independence (no conflict of interest in the template's success), and methodological rigor (experience with meta-analysis or quantitative evidence synthesis).

**Panel Meeting Structure (typically 2–3 hours)**:

1. **Presentation of Meta-Analysis** (30 min): Project lead presents effect sizes, heterogeneity findings, publication bias assessment, and identified moderation variables (population subgroups, study design differences).

2. **Individual Expert Calibration** (45 min): Each panelist independently assigns: (a) core effect size (point estimate for "standard" population and context, typically d = 0.40–0.55), (b) Goldilocks parameter ranges (where applicable: dose-response ranges, optimal parameter ranges), (c) population modifiers (how effect changes for age, sex, clinical status, cultural background), (d) cross-template interactions (which other templates amplify or diminish this effect?), (e) overall bridge warrant (which of the 7 warrant types applies best?).

3. **Consensus Discussion** (45 min): Panelists share their independent assessments. Disagreements are discussed: when estimates differ by > 0.05 in d or > 0.1 in confidence, the panelists discuss reasons. Often disagreements reflect different emphasis on certain studies (e.g., one panelist weights recent replications heavily; another weights foundational studies heavily). Consensus is negotiated; if agreement cannot be reached, the more conservative estimate (lower effect, higher uncertainty) is adopted.

4. **Confidence Assignment** (15 min): The panel jointly assigns overall confidence (0.40–0.55 range) using a legacy three-factor decomposition (see §48 for the modern log-odds approach and §107 for critique of independence assumptions):
   - P(mechanism chain) = 0.60–0.90 (assigned based on clarity of mechanism, evidence quality for each step)
   - P(bridge warrant) = 0.25–0.95 (assigned based on warrant type: CONSTITUTIVE 0.95, MECHANISM 0.80, EMPIRICAL_ASSOCIATION 0.80, etc.)
   - P(parameters_correct) = 0.60–0.90 (assigned based on heterogeneity, population variation, generalizability)
   - prior_coherence boost = +0.05 to +0.15 (assigned based on consistency with other templates, lack of logical contradiction)

   Confidence = max(0.40, min(0.55, P(mechanism) × P(bridge) × P(parameters) + prior_coherence))

   **Note**: This three-factor approach is retained for backward compatibility with existing template library (built 2024–2026). New templates should use the projection calculus in §48, which properly avoids independence violations through log-odds attenuation toward the ignorance prior.

5. **Written Justification** (30 min): The panel writes 1–2 page justification of their assignments, noting key evidence, disagreements, and limitations. This justification becomes part of the template's metadata.

---

**Disagreement Resolution**:

When panelists disagree substantially (>0.05 difference in effect size, >0.10 difference in confidence), the project uses a structured resolution process:

1. **Identify Source of Disagreement**: Is the disagreement about: (a) how much weight to assign certain studies? (b) interpretation of heterogeneity? (c) applicability of evidence to the template's intended use case? (d) underlying causal mechanism?

2. **Check for Expertise Specialization**: Sometimes one panelist has deeper expertise in a relevant sub-domain (e.g., one panelist is a vision neuroscientist reviewing a vision-based template). Their estimate is given slightly higher weight if the disagreement is within their specialty.

3. **Apply Conservative Bias**: When unresolved, adopt the more conservative estimate (lower effect, higher uncertainty). This prevents overconfidence.

4. **Flag for Panel Consultation**: If disagreement reflects genuine scientific debate (e.g., disagreement about mechanism directionality, not just effect magnitude), the disagreement is noted in the template's gap documentation. The template is flagged for future expert panel review (Part V consultation pathway).

---

**The 3-Star Audit Score and System Health**:

The February 2026 comprehensive audit (conducted by external auditors blind to template developers) assigned each template a 3-star quality score based on:

**Star Dimension 1: Evidence Quality** (0–1 stars)
- 1 star: Tier A–B evidence, ≥3 independent replications, effect size robust
- 0.5 stars: Tier B–C evidence, 2 independent replications, some heterogeneity
- 0 stars: Tier C–D evidence, ≤1 replication, high uncertainty

**Star Dimension 2: Mechanism Clarity** (0–1 stars)
- 1 star: Mechanism chain fully characterized, all steps have direct evidence
- 0.5 stars: Mechanism plausible, some steps inferred from adjacent evidence
- 0 stars: Mechanism is theoretical construct, not directly tested

**Star Dimension 3: Boundary Conditions Specification** (0–1 stars)
- 1 star: Population modifiers, interaction effects, and scope boundaries clearly specified
- 0.5 stars: Some modifiers identified, incomplete specification
- 0 stars: Treated as universal, no boundary conditions identified

**Star Distribution**:
- 3.0 stars (perfect): 12 templates (CIRCADIAN_ALIGNMENT, SPEECH_INTELLIGIBILITY, PROXIMITY, etc.)
- 2.5 stars: 28 templates
- 2.0 stars: 38 templates
- 1.5 stars: 18 templates
- 1.0 stars or lower: 7 templates (flagged for revision or demotion to scaffold status)

**System-Wide Mean Star Score**: 2.1 stars out of 3.0 (70% score). Audit rating: ACCEPTABLE but with significant limitations noted. Comments: "The system is defensible for design guidance under conservative assumptions, but would not withstand aggressive peer review. Calibration is methodical and transparent, but evidence base is uneven across domains."

---

## PART XI: ARCHITECTURAL TYPOLOGY (Expanded Sections)



**SECTION C: Provenance Research System**
- §95.2: Evidence Provenance Architecture
- §95.3: Social Epistemology Implementation
- §95.4: Provenance-Aware Explanation Generation

---

# SECTION C: PROVENANCE RESEARCH SYSTEM

## §95.2: Evidence Provenance Architecture

### BeliefProvenance Dataclass

Every belief in the Web carries provenance metadata through the `BeliefProvenance` dataclass:

```python
@dataclass
class BeliefProvenance:
    belief_id: str

    # Production context
    producing_communities: List[str]      # Which communities made this claim
    producing_labs: List[str]             # Which labs
    producing_authors: List[str]          # Primary authors

    # Methodological context
    methods_used: List[str]               # e.g., "lab_experiment", "field_study"
    instruments_used: List[str]           # e.g., "cortisol_assay", "POMS"

    # Community reception
    community_credences: Dict[str, float] # community_id → credence (per SE-2)
    endorsing_communities: List[str]      # Who accepts this
    contesting_communities: List[str]     # Who disputes this

    # Contestation details
    contestation_type: Optional[ContestationType]  # EMPIRICAL, METHODOLOGICAL, THEORETICAL, etc.
    contestation_details: Optional[str]

    # Aggregation decision
    aggregation_approach: DisagreementResolution   # AVERAGE, REPORT_SEPARATELY, FLAG_INCOMMENSURABLE
    aggregated_credence: Optional[float]
```

This structure answers: **Who said this? How? Why might they disagree?**

### CommunityRelativeCredence

Rather than a single credence for a belief, the system maintains credences *per community*. Example:

**Belief: "High ceilings facilitate divergent thinking through conceptual metaphor priming"**

```
Global credence: 0.55 (low consensus—genuine disagreement)

Community credences:
  - cognitive_psychology_community: 0.72 (conceptual metaphor researchers)
  - neuroscience_community: 0.45 (skeptical of metaphor mechanism)
  - architecture_community: 0.58 (accept effect, mechanism uncertain)
  - environmental_psych_community: 0.61 (accept effect)

Aggregation: REPORT_SEPARATELY
Reason: Communities use different frameworks (metaphor vs. neural prediction vs. architectural intuition);
        no shared method to arbitrate
```

This honesty is crucial. If we averaged to 0.55 (the global credence), we would hide that cognitive psychologists are confident (0.72) and neuroscientists are skeptical (0.45). Averaging would suggest false consensus.

The system defaults to REPORT_SEPARATELY for theoretical disagreements (different frameworks) and AVERAGE only for empirical disagreements within the same framework.

### Evidence Chain Construction

When the system builds an explanation, it traces the evidence chain:

**Example chain for "Nature views reduce stress"**:

```
Layer 1 (Direct observation):
  ├─ exp:ulrich_1984 → "Cardiac patients with nature views
  │  have lower stress markers than patients with blank walls"
  └─ credence_grounding: 0.95 (directly observed, large effect)

Layer 2 (One-hop inference):
  ├─ gen:nature_stress_reduction → "Exposure to natural scenes
  │  reliably reduces physiological stress"
  ├─ supported_by: [ulrich_1984, kaplan_1989, ...] (n=12 studies)
  └─ credence_grounding: 0.85 (empirical generalization)

Layer 3 (Multi-hop/abstracted):
  ├─ mec:soft_fascination → "Nature's soft fascination
  │  mechanism (ART explanation)"
  ├─ supported_by: [gen:nature_stress_reduction]
  │  (one-hop above)
  └─ credence_grounding: 0.60 (mechanistic inference)

Layer 4 (Theoretical):
  ├─ theory:art → "Attention Restoration Theory explains
  │  nature effects via directed attention recovery"
  ├─ supported_by: [mec:soft_fascination, mec:being_away, ...]
  ├─ alternative: theory:srt (stress recovery via affect)
  └─ credence_grounding: 0.45 (weak, theory-dependent)
```

The system can trace backward: Why do we believe Layer 4? Because Layer 3 supports it. Why Layer 3? Because Layer 2. Why Layer 2? Because Layer 1 (direct observation).

A user asking "Why should I believe this?" can follow the chain down to the bedrock observation.

### Audit Trails for Belief Modification History

Every time a belief's credence changes, the system records:

```python
CredenceHistoryEntry(
    timestamp: datetime,
    credence_value: float,
    delta: float,                    # Change from previous
    triggered_by: Optional[str],     # Paper ID that caused change
    update_reason: str              # Explanation (e.g., "new replication", "conflicting finding")
)
```

Example history:

```
Belief: "High ceilings facilitate divergent thinking"

Timeline:
  2024-02-15: 0.50 (CREATED) — Initial belief from Meyers-Levy & Zhu 2007
  2024-05-22: 0.62 (+0.12) — Replication study published (Szpaderski & Estes 2015)
  2024-08-10: 0.58 (-0.04) — Null result (Smith et al. 2024 VR study); credence dips
  2024-10-03: 0.65 (+0.07) — Null result critiqued (methodology issues); credence recovers
  2024-12-15: 0.68 (+0.03) — Meta-analysis (Thompson 2024) shows moderate effect
  2026-02-15: 0.72 (+0.04) — Current; stable over last 2 months
```

This audit trail makes visible what the simple number 0.72 hides: the belief was contested, then gradually strengthened. A user seeing this timeline understands the journey of the claim.

---

## §95.3: Social Epistemology Implementation

### EpistemicCommunity and Track Records

Each community is defined not by institutional power but by epistemic practice. The system tracks:

**Core commitments**:
- **Theoretical commitments**: Which T1 and T1.5 frameworks the community accepts
- **Methodological preferences**: Lab vs. field; self-report vs. physiological; cross-sectional vs. longitudinal
- **Characteristic vocabulary**: Terms that define the community (soft fascination for ART; parasympathetic for SRT)
- **Exemplary papers**: Foundational works that define the paradigm (Kuhn)

**Track records** (per domain):
- **Prediction accuracy**: When the community made a prediction (e.g., "nature views will reduce stress"), was it borne out?
- **Replication robustness**: When findings from this community are replicated, do they hold?
- **Evidence quality**: Does the community publish rigorous studies or sloppier ones?

Example track record (hypothetical):
```
Environmental Psychology field:
  domain: architectural_outcomes
  prediction_accuracy: 0.82  (82% of predictions borne out)
  replication_rate: 0.75    (75% of studies that attempted replication succeeded)
  publication_quality: 0.68 (on scale 0-1; based on methodology rigor)

ART community (within field):
  prediction_accuracy: 0.88 (ART predictions especially accurate)
  replication_rate: 0.72
  publication_quality: 0.71 (good, slightly better than field average)

SRT community (within field):
  prediction_accuracy: 0.76 (less accurate; often invokes alternative mechanisms)
  replication_rate: 0.78
  publication_quality: 0.65 (weaker methodology on average)
```

These track records are *not* used to weight consensus (per panel decision SE-3: "Do not use institutional power for credence weighting"). Instead, they are used to:
1. Flag if a community is making wildly inaccurate predictions (possible sign of paradigm drift)
2. Weight credences *only when there is genuine disagreement* and communities use the same method (per SE-2)
3. Identify which communities have highest-quality evidence (for meta-analysis purposes)

### Contestation and Disagreement Tracking

The `ContestationTracker` class explicitly records disagreements:

```python
@dataclass
class Contestation:
    contestation_id: str
    belief_id: str
    contesting_community_id: str      # Who disagrees
    target_community_id: str          # With whom
    contestation_type: ContestationType  # EMPIRICAL, METHODOLOGICAL, THEORETICAL, SCOPE, VALUE, INCOMMENSURABLE
    description: str

    contesting_papers: List[str]      # Papers supporting the contestation
    target_papers: List[str]          # Papers being challenged

    is_resolved: bool
    agreed_resolution_criteria: Optional[str]  # What would settle this?
    experimenter_regress: bool        # True if no agreed criteria (Collins)
```

Types of contestation:

**EMPIRICAL**: Different data interpretation
- Contesting: "Nature views reduce stress"
- Target: "The null result shows no effect"
- Resolution: Replication in well-controlled conditions
- Experimenter regress risk: Low (both sides agree experimental design matters)

**METHODOLOGICAL**: Different methods, same prediction
- Contesting: "Lab studies show X"
- Target: "Field studies show X doesn't apply"
- Resolution: Understanding why method matters; ecological validity studies
- Experimenter regress risk: Medium (disagreement about what counts as valid evidence)

**THEORETICAL**: Different explanatory frameworks
- Contesting: "ART explains nature effects via attention"
- Target: "SRT explains nature effects via affect"
- Resolution: Direct mechanism tests; could take years
- Experimenter regress risk: High (communities may not agree on what evidence counts)

**SCOPE**: Different generalization claims
- Contesting: "This applies to all populations"
- Target: "This only applies to some populations"
- Resolution: Boundary condition studies; population-stratified analysis
- Experimenter regress risk: Low (factual question: does the effect appear in group X?)

**VALUE**: Implicit value disagreements
- Contesting: "We should prioritize nature exposure in hospitals"
- Target: "Cost-benefit analysis shows this is too expensive"
- Resolution: Value conflict, not empirical; may be unresolvable
- Experimenter regress risk: Very high (not actually empirical disagreement)

**INCOMMENSURABLE** (Kuhnian): Paradigms cannot be compared
- Example: Does biophilia exist? Evolutionary psychology says yes; behaviorists say it's anthropomorphic
- Resolution: Paradigm shift; may take decades
- Experimenter regress risk: Highest (different research programs, no shared standards)

### MethodologicalDiversityAssessor

For each belief, the system computes a methodological diversity index using entropy:

```
Diversity = 0.4 × entropy(methods) + 0.3 × entropy(settings) + 0.3 × entropy(populations)
```

where entropy is normalized to 0-1.

High diversity (e.g., 0.75) means findings come from multiple methods, settings, populations. Low diversity (e.g., 0.25) means evidence is concentrated (e.g., only lab studies of college students).

**Identifying vulnerabilities**:

```
Belief: "Green walls improve cognitive performance"

Methods: Lab experiment (85%), Simulation (10%), Field (5%)
→ Vulnerability: Overwhelmingly lab-based

Settings: Office (100%)
→ Vulnerability: Only tested in one setting type

Populations: College students (75%), Adults (20%), Other (5%)
→ Vulnerability: Heavily skewed to convenience sample

Overall diversity: 0.35 (LOW)

Diversification suggestions:
  ├─ Add field experiments in real offices (not just labs)
  ├─ Test in diverse populations (children, elderly, diverse SES)
  ├─ Long-term studies (not just acute exposure)
  └─ Cross-cultural replication (US-only so far)
```

This assessment helps users understand: Is this finding robust to methodology variation, or is it an artifact of how it was studied?

---

## §95.4: Provenance-Aware Explanation Generation

### How Explanations Cite Their Evidence Chains

When the QA agent generates an explanation, it traces the provenance chain and explicitly cites it. Example:

**User Question**: "Does high ceiling height facilitate creative thinking?"

**System Response (L3)**:

> Yes, high ceilings facilitate divergent creative thinking with a moderate effect size (d ≈ 0.40), though the effect reverses for detail-focused tasks.
>
> **Evidence**: The original finding comes from Meyers-Levy & Zhu (2007), which showed that ceiling height primes conceptual associations related to "freedom" and "openness," leading to broader associative processing. This has been replicated in follow-up studies (Szpaderski & Estes 2015; Thompson 2024 meta-analysis).
>
> **Mechanism**: The proposed mechanism is conceptual metaphor priming: spatial height → metaphorical "freedom" → broadened cognition. This is grounded in embodied cognition theories (Lakoff & Johnson) but is *not directly observed*. What we observe is the effect (higher ceiling = more creative responses); the metaphor mechanism is inferred.
>
> **Contested**: Whether the mechanism is metaphor-based (cognitive level) or operates through other pathways (e.g., increased prediction error from larger spatial volume, per predictive processing) remains unclear. Different theoretical communities favor different mechanistic accounts.
>
> **Boundary Conditions**: The effect is specific to *divergent* thinking (generating multiple ideas). For *convergent* thinking (focusing on one solution), the effect reverses: lower ceilings improve performance.
>
> **Confidence**: High confidence in the empirical effect (credence 0.72 ± 0.08). Medium confidence in the proposed mechanism (credence 0.45 for metaphor account; 0.35 for predictive processing account).

Notice what this explanation does:

1. **Grounds in observation** (level 1): Ceiling height → divergent thinking (the empirical finding)
2. **Extends to generalization** (level 2): Consistent across multiple studies
3. **Infers mechanism** (level 3): Metaphor priming (theoretical inference)
4. **Marks confidence**: High for empirical, medium for mechanism
5. **Notes alternatives**: Other communities favor other mechanisms
6. **Specifies boundary conditions**: Effect type-specific

### Grounding Scores and Justification Status

Every claim in the Web carries a `grounding_score` indicating how directly it is evidence-grounded:

```python
class GroundingLevel(Enum):
    DIRECT = 1.0          # Directly observed measurement
    ONE_HOP = 0.8         # Immediate generalization from observation
    MULTI_HOP = 0.5       # Abstracted claim; intermediate inference
    THEORETICAL = 0.25    # Purely theoretical; cannot be directly observed
    SPECULATIVE = 0.1     # Speculation; awaits grounding
```

Examples:

**DIRECT (grounding 1.0)**:
"Participants viewing a 30-minute nature video showed mean HR decrease of 4.2 bpm (SD=2.1) vs. baseline."
- This is a measurement. It is grounded in the data.

**ONE_HOP (grounding 0.8)**:
"Nature exposure reliably reduces heart rate across multiple studies (mean d = 0.35)."
- This generalizes from DIRECT observations across studies. It is grounded but abstracted.

**MULTI_HOP (grounding 0.5)**:
"Biophilic design elements in healthcare settings promote parasympathetic nervous system dominance."
- This abstracts across different elements (plants, light, views), settings (hospitals, offices), and measures (HR, cortisol, self-report). The connection is more inferential.

**THEORETICAL (grounding 0.25)**:
"Human visual systems evolved to process fractal dimensions efficiently, reducing cognitive load."
- This explains *why* nature effects exist, but it appeals to evolutionary history we cannot directly observe.

**SPECULATIVE (grounding 0.1)**:
"Biomorphic design may activate ancestral memory systems."
- This is a conjecture; no direct evidence.

The system flags claims by grounding level. A user seeing a Theoretical claim knows it is inference from lower levels. A user seeing a Speculative claim knows it is not yet well-grounded.

### Justification Status

Beyond grounding, each claim carries a `justification_status`:

```python
class JustificationStatus(Enum):
    WELL_JUSTIFIED = "well_justified"         # Multiple lines of evidence converge
    COHERENT_ONLY = "coherent_only"          # Fits well with other beliefs but weakly grounded
    CONTESTED = "contested"                  # Genuine disagreement in the literature
    ISOLATED = "isolated"                    # Single study; not replicated
    CONTRADICTED = "contradicted"            # Evidence argues against it
```

Examples:

**WELL_JUSTIFIED**: "Nature views reduce stress"
- Grounding: ONE_HOP (generalizes across many studies)
- Convergence: Multiple mechanisms (ART, SRT, biophilia) predict this
- Replication: Strong (>15 studies)
- Status: WELL_JUSTIFIED

**COHERENT_ONLY**: "Fractals in architecture enhance aesthetic experience through fluency"
- Grounding: MULTI_HOP (abstracted from perception studies)
- Convergence: Fits with fluency heuristics, but few direct tests
- Replication: Weak (2-3 studies)
- Status: COHERENT_ONLY (makes sense theoretically; needs empirical support)

**CONTESTED**: "High ceilings facilitate creativity"
- Grounding: ONE_HOP (empirically replicated)
- Convergence: Different mechanisms invoked (metaphor, prediction error, etc.)
- Replication: Moderate (5+ studies of core effect; mechanism unclear)
- Status: CONTESTED (effect replicated but mechanism disputed)

### Export with Provenance Metadata

When a user exports beliefs (via the Export page), they can include full provenance:

```json
{
  "belief_id": "belief:ceiling_creativity",
  "content": "High ceilings facilitate divergent thinking",
  "credence": {
    "value": 0.72,
    "uncertainty": 0.08,
    "ci_95": [0.64, 0.80]
  },
  "grounding_score": 0.8,
  "justification_status": "WELL_JUSTIFIED",

  "provenance": {
    "producing_communities": ["cognitive_psychology", "environmental_psychology"],
    "producing_labs": ["Meyers-Levy Lab", "Thompson Lab"],
    "primary_authors": ["Meyers-Levy, J.", "Zhu, R."],
    "methods_used": ["lab_experiment", "field_study"],
    "evidence_chain": [
      {
        "level": "DIRECT",
        "description": "Meyers-Levy & Zhu (2007) lab study: ceiling height × creative task interaction",
        "reference": "10.1086/518698",
        "effect_size": {"d": 0.47, "ci": [0.15, 0.79]}
      },
      {
        "level": "ONE_HOP",
        "description": "Generalization: ceiling height effect replicates across studies",
        "supporting_papers": 5,
        "effect_size": {"d": 0.35, "ci": [0.18, 0.52]}
      },
      {
        "level": "THEORETICAL",
        "description": "Mechanism: conceptual metaphor priming (spatial height → freedom)",
        "competing_mechanisms": ["predictive_processing", "arousal_modulation"],
        "support_level": "COHERENT_ONLY"
      }
    ],

    "contestations": [
      {
        "type": "THEORETICAL",
        "description": "Is the mechanism metaphor-based or prediction-error-based?",
        "communities": ["cognitive_psychology_metaphor", "neuroscience_predictive_processing"],
        "resolution": "UNRESOLVED"
      }
    ],

    "methodological_diversity": {
      "index": 0.58,
      "methods": ["lab_experiment", "field_study", "simulation"],
      "vulnerabilities": ["lab-heavy (70% of evidence)", "mostly college students"]
    }
  }
}
```

This exported format preserves the full evidentiary journey. A user importing this into their own system gets not just the claim (credence 0.72) but the *reasons* for that credence: the evidence chain, the competing mechanisms, the limitations.

---

## Conclusion: Coherence Across the System

The three systems—QA Agent, Evidence Explorer, Provenance Research—form an integrated whole:

1. **QA Agent** delivers answers at the right depth for the user, grounded in claims from the Web of Belief
2. **Evidence Explorer** visualizes the Web, making structure and uncertainty visible
3. **Provenance Research** system ensures that credences reflect actual evidence chains, not hidden assumptions

Each system respects the principles of the others:
- The QA Agent uses the Web of Belief as its knowledge base and the Provenance system's evidence chains for explanations
- The Evidence Explorer visualizes both the Web's structure and the Provenance system's credences and contestations
- The Provenance system grounds all credences in evidence chains that the QA Agent can cite

Together, they operationalize a Quinean, coherentist epistemology: knowledge is a web, credences flow from evidence chains, alternative explanations are tracked, genuine disagreements are recorded, and explanations are honest about what we know and don't know.

---

**End of Documentation**

*Prepared by Article Eater Documentation Team*
*February 24, 2026*
*For inclusion in the ATLAS system Master Paper (Chapters 122, 124, 95)*


### Next Steps for Part X

### Next Steps

Part X catalogs the ~103 calibrated mechanistic templates and their organizational structure. Five research directions enhance the library's scope, precision, and utility.

First, **expand coverage in underrepresented domains** identified in the Part I coverage-gap analysis. Currently, templates are weighted toward visual, circadian, and stress-recovery mechanisms; acoustic, thermal, olfactory, and social-modulation mechanisms have sparse coverage. We should prioritize development of 20–30 new templates in: (a) **acoustic domain**: reverberant-space focus enhancement (AX1), acoustic openness relaxation (AX2), rhythmic-sound expectancy (AX3), background-noise stress (AX4), temporal-sound-pattern engagement (AX5); (b) **thermal domain**: draft-sensation threat (TH1), thermal-setpoint adaptation (TH2), surface-temperature pleasantness (TH3), radiant-temperature asymmetry (TH4), evaporative-cooling engagement (TH5); (c) **olfactory domain**: scent-memory episodic-binding (OL1), scent-space identity (OL2), scent-congruence comfort (OL3), natural-odor restoration (OL4); (d) **material domain**: texture-exploration engagement (MAT-EXTENDED series), patina-authenticity meaning (MAT-B1), material-origin story coherence (MAT-B2); (e) **temporal domain**: circadian-phase misalignment stress (TP-EXT1), seasonal-affective modulation via architecture (TP-EXT2), occupancy-duration habituation dynamics (TP-EXT3). Each template development requires 4–6 weeks of mechanism-chain specification, literature review, and expert consensus validation. Estimated timeline for 25–30 new templates: 6–8 months of focused work.

Second, **parameterize template interactions systematically** through the dedicated Interaction Panel (Panel XI-A, discussed in Part V). Once high-priority cross-template interactions are identified and quantified, integrate them into template JSON specifications through **interaction matrices and conditional-effect specifications**. Where template A and template B produce superadditive effects (synergistic interaction), the template library should document this explicitly: interaction_type: SYNERGISTIC, interaction_magnitude: 1.25 (meaning combined effect is 125% of additive prediction), interaction_boundary_conditions (under what conditions does synergy occur?), and interaction_evidence_support (citation to studies documenting interaction). This transforms the library from independent templates into an interconnected network representation.

Third, **develop template-specialization variants** for different architectural typologies and populations. The current templates are generic across building types and occupant demographics; however, mechanism strength and parameter values may vary substantially. For instance, the L3 circadian-convergence template optimized for office workers may differ in parameter values (melanopic thresholds, acceptable circadian phase shift) for hospital patients, school children, or shift workers. We should: (a) create specialized template variants with "_VARIANT" suffixes (e.g., L3_OFFICE, L3_HOSPITAL, L3_SCHOOL, L3_SHIFT_WORK), each with re-parameterized confidence values and population-specific bridge warrants, (b) document the evidence basis for each variant's parameter differences, and (c) allow practitioners to select appropriate variants based on their occupancy context. This moves the system from WEIRD-normative toward more equitable, context-responsive guidance. Estimated expansion: 30–50 variant templates (2–3 variants per high-impact template).

Fourth, **implement a template-versioning and revision-history system** enabling transparent iteration. Currently, templates are dated but their revision history is not formally tracked. We should: (a) adopt semantic versioning (MAJOR.MINOR.PATCH) for each template, (b) maintain a revision log documenting changes, rationale, and triggering evidence, (c) allow practitioners to select whether they want to use latest versions or stable/validated versions (analogous to software development's stable vs. development branches), and (d) periodically release "certified" template versions that have accumulated sufficient use and validation evidence. This professionalization of the template library aligns it with clinical-guideline governance and evidence-based medicine's approach to living guidance documents.

Fifth, **create template-effectiveness scorecards** for practitioners showing per-template research evidence quality. For each template, generate a one-page summary card showing: (a) mechanism chain diagram, (b) key parametric values with confidence ranges, (c) evidence sources (number of studies, cumulative sample size, study designs represented), (d) maturity rating (how-actually / how-plausibly / how-possibly), (e) known limitations and scope boundaries, (f) prior conditional-probability estimates for diverse populations, and (g) template interactions with other templates. These scorecards serve both as evidence-quality transparency tools and as practitioner-education materials, enabling architects to make informed decisions about which templates to prioritize in design.

---

---


## § 96: Why Typology Matters {#§96}

Consider two superficially similar predictions:

*Prediction 1: High ceiling height (>3.5m) increases creative ideation in open-plan offices.*

*Prediction 2: High ceiling height (>3.5m) increases creative ideation in private offices.*

These predictions have opposite empirical support. In open-plan offices, high ceilings are typically associated with large floor areas and sparse partitioning—both of which increase noise and distraction. The ceiling height effect is confounded with open-plan noise. In private offices, high ceilings occur without noise confound and show robust beneficial effects on creativity.

The confound is not incidental; it reflects real-world architectural constraints. High ceilings in open-plan spaces are a design tradeoff: you get visual openness but accept acoustic challenges. Ignoring this confound produces false generalizations.

This is the typology problem: features do not occur at random. They co-vary in ecologically valid bundles. A prediction system that treats features as independent is systematically wrong.

---

## § 97: The 16 Space Types {#§97}

Each space type is characterized by ~25 feature dimensions across eight domains. Representative profiles:

**1. Library Reading Room**: Ceiling 3.5–5.0m, 300–500 lux (soft diffuse), RT60 0.5–0.8s (absorptive), 25–35 dB (quiet), wood/upholstery, PAD [P=0.6, A=0.2, D=0.6], high biophilic elements, social isolation norm.

**2. Open-Plan Office**: Ceiling 2.7–3.3m, 300–500 lux (mixed), RT60 0.5–0.7s (weak absorption), 45–55 dB (noisy), glass/drywall, PAD [P=0.4, A=0.6, D=0.3], minimal biophilic, high social openness.

**3. Private Office**: Ceiling 2.7–3.0m, 400–500 lux (directional task), RT60 0.4–0.6s, 30–40 dB (moderate), mixed materials, PAD [P=0.5, A=0.4, D=0.5], moderate biophilic, optional social.

**4. Hospital Patient Room**: Ceiling 2.5–3.0m, 200–400 lux (dimmable), RT60 0.4–0.8s, 35–45 dB, plastic/vinyl, PAD [P=0.2, A=0.1, D=0.7] (low arousal), minimal biophilic, high control.

**5. Café**: Ceiling 2.8–3.5m, 300–600 lux (warm), RT60 0.6–1.0s (reverberant), 50–65 dB (moderate noise), mixed (wood, concrete), PAD [P=0.7, A=0.5, D=0.4], moderate biophilic, high social.

**6. Art Studio**: Ceiling 3.5–4.5m, 500–1000 lux (strong task lighting), RT60 0.5–0.8s, 40–50 dB, concrete/wood, PAD [P=0.7, A=0.6, D=0.5], minimal biophilic, variable social.

**7. Classroom**: Ceiling 2.8–3.3m, 400–500 lux (uniform), RT60 0.6–0.9s, 40–50 dB (speech intelligibility critical), mixed, PAD [P=0.5, A=0.6, D=0.4], minimal biophilic, high social structure.

**8. Museum Gallery**: Ceiling 3.0–5.0m (variable), 150–300 lux (dramatic), RT60 0.7–1.2s, 30–40 dB, mixed, PAD [P=0.4, A=0.3, D=0.6], variable biophilic, guided social.

**9. Waiting Room**: Ceiling 2.7–3.0m, 300–400 lux, RT60 0.5–0.7s, 40–50 dB, mixed, PAD [P=0.2, A=0.2, D=0.5] (anxious), minimal-to-moderate biophilic, forced social proximity.

**10. Meditation Space**: Ceiling 2.8–3.5m, 100–200 lux (dim, warm), RT60 0.8–1.2s (very absorptive), <25 dB (silent), natural materials, PAD [P=0.1, A=0.1, D=0.9] (deeply calm), high biophilic, solitude norm.

**11. Retail**: Ceiling 2.5–3.0m, 500–1000 lux (bright), RT60 0.3–0.6s (hard), 50–65 dB (lively), mixed (glass, tile), PAD [P=0.8, A=0.6, D=0.3], minimal biophilic, high social exposure.

**12. Fitness Center**: Ceiling 3.5–4.5m, 400–800 lux (bright), RT60 0.6–0.8s, 70–85 dB (loud music), concrete/rubber, PAD [P=0.8, A=0.8, D=0.2], minimal biophilic, high social visibility.

**13. Laboratory**: Ceiling 2.7–3.0m, 500–800 lux (task-focused), RT60 0.4–0.6s, 40–50 dB, plastic/stainless steel, PAD [P=0.5, A=0.5, D=0.2], minimal biophilic, moderate social (focused collaboration).

**14. Conference Room**: Ceiling 2.7–3.0m, 400–500 lux, RT60 0.5–0.8s (moderate absorption), 35–45 dB (speech critical), mixed, PAD [P=0.6, A=0.6, D=0.4], minimal-to-moderate biophilic, structured social.

**15. Hotel Lobby**: Ceiling 3.5–5.0m, 400–600 lux (warm), RT60 0.7–1.0s, 45–55 dB, mixed (marble, wood), PAD [P=0.7, A=0.4, D=0.5], moderate biophilic, public social.

**16. Residential Bedroom**: Ceiling 2.5–2.7m, 50–150 lux (dimmable, warm), RT60 0.5–0.8s, 25–35 dB, soft materials, PAD [P=0.1, A=0.1, D=0.8], moderate biophilic, private intimacy.

---

## § 98: Cross-Domain Conditionals {#§98}

The 16 space types define 45 conditional probability relationships capturing feature co-occurrence within and across types. Examples:

- **P(acoustic_treatment=high | privacy=high)** = 0.85. High privacy (soundproofing, partitions) nearly always requires acoustic treatment.

- **P(natural_materials | daylight_fraction > 0.4)** = 0.70. Spaces with high daylight (windows, skylights) tend to feature natural materials (wood, stone, natural fabrics) more often.

- **P(biophilic_elements | ceiling_height > 3.5m)** = 0.65. Tall spaces more often include plants, views, and other biophilic features.

- **P(high_luminance_variation | museum_gallery)** = 0.90. Museum galleries use directional lighting creating luminance contrast to guide attention.

- **P(speech_intelligibility_prioritized | classroom OR conference_room)** = 0.95. Educational and collaborative spaces design for speech clarity.

- **P(thermal_stratification_present | ceiling_height > 4.0m)** = 0.75. Very tall spaces develop thermal gradients (warm ceiling, cool floor).

- **P(color_temperature > 4000K | task_intensity=high)** = 0.80. Task-heavy spaces (studios, labs) use cooler, bluer light for alertness.

- **P(material_softness_high | PAD_dominance=calm)** = 0.85. Calm spaces (meditation, bedrooms) use soft, absorptive materials.

These conditionals enable prediction of ecologically valid feature combinations and identification of anomalous designs (e.g., a retail space claiming minimal biophilic elements but high ceiling, which violates typical co-occurrence patterns).

---

## § 99: Space Similarity Matrix {#§99}

A cosine-similarity matrix across 25 feature dimensions (spatial: ceiling height, floor area, boundary definition; material: softness, warmth, naturalness; lighting: illuminance, CCT, diffuseness; acoustic: RT60, dB, speech_intelligibility; thermal: temperature, gradient, radiance; olfactory: indoor_air_quality, scent_presence; biophilic: plant_coverage, views, living_materials; social: privacy_level, group_size, hierarchy) yields similarity scores between all 16 space types:

Most similar pairs: Library-Meditation (0.85), Café-Hotel Lobby (0.82), Office-Conference Room (0.78), Hospital-Waiting Room (0.72).

Most dissimilar pairs: Fitness Center-Meditation (0.23), Retail-Library (0.28), Lab-Café (0.31).

Similarity predicts transferability: findings from library reading rooms are more likely to replicate in meditation spaces than in fitness centers, because the environmental parameters are more similar.

---

## § 100: Activity-Space Matrix {#§100}

The system maps 40+ activities to required architectural features. Activities include: deep reading, collaborative brainstorming, medical consultation, quiet contemplation, physical exercise, creative making, social dining, presentation giving, focused problem-solving, casual socializing, sleep/rest, emotional support, learning/instruction, negotiation, healing/recovery, celebration, mourning, ritual, scientific discovery, artistic creation.

For each activity, the matrix specifies required parameter ranges. Example:

**Activity: Deep Reading**
- Preferred ceiling height: 3.0–4.5m (moderate to high, supports focus)
- Illuminance: 300–500 lux (task-focused but not harsh)
- Color temperature: 3500–4500K (warm to neutral, not blue)
- Reverberation time (RT60): 0.4–0.8s (absorptive, not reverberant)
- Ambient noise: <35 dB (quiet)
- Temperature: 20–22°C (cool supports alertness)
- Thermal comfort: Important for sustained concentration
- Biophilic elements: Beneficial (soft, indirect nature views or plants)
- Privacy: Essential (no open space, low social density)
- Seating: Comfortable for >2 hours continuous use
- Material warmth: Moderate (not cold, not overheated)

**Activity: Collaborative Brainstorming**
- Ceiling height: 2.8–3.5m (moderate, not isolating)
- Illuminance: 400–600 lux (bright, supports visibility and idea capture)
- Color temperature: 4500–6500K (cooler, supports alertness and ideation)
- RT60: 0.6–0.9s (moderate reverberation supports speech but not extreme)
- Ambient noise: 40–55 dB (moderate, background activity supports energy)
- Temperature: 20–23°C (slightly cool supports active thinking)
- Biophilic elements: Moderate (somewhat less critical than for deep focus)
- Privacy: Moderate (semi-public, group aware but not exposed)
- Seating: Flexible, supports movement and reconfiguration
- Material warmth: Warm and inviting (encourages openness)
- Visual variety: High (stimulating, supports idea association)

**Mismatch scenarios** (activity-space misfit) are informationally rich. Focused deep reading in a high-energy café is more challenging than prototypical library-reading, but the prediction is more informative (contrast effect more pronounced). The Activity-Space Matrix enables prediction of performance degradation when activity and space are mismatched.

---

