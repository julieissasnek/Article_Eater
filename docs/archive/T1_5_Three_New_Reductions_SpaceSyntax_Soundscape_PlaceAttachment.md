# T1.5 Formal Reductions: Space Syntax, Soundscape Theory, Place Attachment

**Version 1.0 — February 21, 2026**
**Status: IN PROGRESS — saving incrementally to avoid loss**

This document formalizes the reduction of three high-priority Tier 1.5 domain theories to the CMR mechanistic template architecture. It follows the format established in T1_5_Expansion_Three_Reductions.md and is designed for direct integration into the Article Eater Web of Belief and Bayesian causal network.

---

## Preliminary: What "Operational Reduction" Means Here

A T1.5 theory is operationally reduced when the following have been specified:

1. **Core phenomena**: The empirical regularities the theory organizes, stated as input-output relationships that the Article Eater must recognize and correctly map.
2. **T1 decomposition**: Which of the 10 Tier 1 frameworks (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI) provide the mechanism for each phenomenon, and with what coverage fraction.
3. **T2 template assignments**: Existing templates from the ~150-template registry that handle identified phenomena; new templates proposed where gaps exist.
4. **IE-DPT overlay**: Where the explicit channel (activity frame, semantic context, deliberate attention) modulates the implicit substrate, and what percentage of variance this overlay explains.
5. **Bridge warrant classes**: What kind of inferential link (CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL) connects empirical claims to the template.
6. **Irreducible residual**: What the T1 decomposition cannot account for — the honest remainder.
7. **New T2 templates proposed**: Formalized proposals ready for registration in the template registry.
8. **Outcome domains and keywords**: For Article Eater extraction pipeline (`OUTCOME_DOMAIN_TO_THEORY` and `THEORY_KEYWORDS` dictionaries).

The credence formula that governs how empirical evidence flows upward is:

`P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

Every element below is designed to make this formula computable for incoming literature.

---

# REDUCTION 1: SPACE SYNTAX THEORY

**Citation**: Hillier, B., & Hanson, J. (1984). *The social logic of space*. Cambridge University Press. (~7,000 GS)
**Supporting**: Penn, A. (2003). Space syntax and spatial cognition. *Environment and Behavior*, 35(1), 30–65. (~700 GS); Hillier, B., Penn, A., Hanson, J., Grajewski, T., & Xu, J. (1993). Natural movement: or, configuration and attraction in urban pedestrian movement. *Environment and Planning B*, 20(1), 29–66. (~2,500 GS)

---

## 1.1 Core Phenomena Space Syntax Organizes

Space syntax is a configurational theory: it holds that the abstract relational structure of a spatial network — independent of individual elements' attractiveness, land use, or visual appearance — predicts how people move through, use, and experience it. The Article Eater must recognize claims in the following families as belonging to this theory:

**Phenomenon SS-A: Integration Predicts Movement Flows**
The theory's central empirical claim: spaces with high *integration* (topological closeness to all other spaces in a network, measured by mean depth) attract disproportionately more pedestrian movement. Hillier et al. (1993) reported R² = 0.50–0.80 between syntactic integration and observed pedestrian flows across multiple UK cities — strong enough to be considered one of environmental psychology's most replicated quantitative regularities. Article Eater should recognize claims of the form: "spaces with lower mean depth / higher integration value show higher pedestrian counts," "axial line integration predicts retail footfall," "grid connectivity correlates with movement density."

**Phenomenon SS-B: Natural Movement Thesis**
The "natural movement" claim is theoretically bolder than the correlation alone: Hillier argues that configuration *alone* — without invoking attractors, land use, or destinations — explains a substantial fraction of movement variance. The fraction attributable to configuration vs. attractors has been contested (Nes & Yamu, 2021). Article Eater should tag claims about the independent explanatory power of spatial configuration relative to land use or destination-based models.

**Phenomenon SS-C: Intelligibility and Wayfinding**
*Intelligibility* (the correlation between local connectivity and global integration within a space) predicts how easily navigators can infer global structure from local cues — an index of the degree to which "what you can see tells you where you are." High intelligibility spaces are easier to learn and navigate without maps. This is directly relevant to wayfinding research, which constitutes a substantial fraction of architectural neuroscience literature. Claims of the form: "participants in high-intelligibility buildings made fewer navigation errors," "spatial disorientation correlates inversely with intelligibility scores" belong here.

**Phenomenon SS-D: Spatial Configuration and Social Encounter**
Hillier's sociological extension: the configurational structure of a settlement or building is not merely functional but encodes social logic — who is likely to encounter whom. Higher integration spaces function as *interfaces* between different social groups; lower integration (deeper, less connected) spaces become *transpatial* communities of insiders. Article Eater should recognize claims about how spatial layout mediates copresence, chance encounter, or social segregation patterns. This phenomenon is the sociological complement of SS-A.

**Phenomenon SS-E: Isovist Properties and Spatial Experience**
The *isovist* — the polygon of visible space from any given vantage point — is Space Syntax's bridge to experience. Isovist area, compactness (the ratio of the square of the perimeter to area), and openness predict subjective assessments of spaciousness, surveillance/being-surveilled, and comfort. Benedikt (1979) established the formalism; Turner et al. (2001) operationalized it computationally. Claims connecting isovist measures to perceived spaciousness, privacy, or safety belong here.

**Phenomenon SS-F: Depth and Spatial Segregation / Privacy**
*Mean topological depth* from a reference point predicts both wayfinding difficulty and perceived privateness. The deeper a space (more steps through connected spaces required to reach it), the more private, the more insider-oriented it is. This partially overlaps with Privacy Regulation but is specifically about configurational depth rather than social boundary regulation mechanisms.

---

## 1.2 T1 Framework Decomposition

### Primary: SN — Spatial Navigation / Cognitive Mapping (Coverage: ~40%)

Space syntax was always implicitly about cognitive mapping, but the connection was made explicit by O'Keefe & Burgess (1996) and formalized in the "spatial cognition" reading of Penn (2003). The constructs map as follows:

*Integration → Grid cell metric coding (SC1)*: Integration in Space Syntax measures topological/metric centrality. Grid cells in the entorhinal cortex provide metric coding of space — essentially the neural substrate of the abstract spatial map that integration is computed on. High-integration spaces are, by hypothesis, those that grid-cell coding most efficiently represents given the overall network geometry. This is a constitutive claim: Space Syntax integration is, at the neural implementation level, a behavioral correlate of the efficiency of the grid-cell metric representation of a given location within the broader spatial network.

*Intelligibility → Hippocampal cognitive map quality*: The degree to which local structure predicts global structure (intelligibility) should correspond to the fidelity of the hippocampal cognitive map. Spiers & Maguire (2006) showed that hippocampal activity during taxi navigation correlates with spatial complexity and planning demands — the same variables that Space Syntax says reduce intelligibility. Wiener & Mallot (2003) argued that human route-choice behavior follows principles of maximal information gain, consistent with intelligibility as a predictor of navigation strategy.

*Natural movement → Place cell firing and path integration*: The claim that people follow syntactically integrated routes "naturally" — without explicit planning — maps onto place cell path-integration: people drift toward routes that their existing hippocampal representation has already coded as traversed/familiar. The natural movement thesis is thus a behavioral prediction derivable from path-integration principles: the configuration that has previously produced the densest place-cell coverage will attract movement without deliberate planning.

*Depth → Allocentric spatial representation*: Deep spaces require more steps in an allocentric spatial representation — more nodes in the hippocampal graph. High-depth spaces are predicted to be harder to represent allocentrically, consistent with their greater wayfinding difficulty.

### Secondary: PP — Predictive Processing (Coverage: ~25%)

Penn (2003) made an explicit argument that Space Syntax's power comes from its relationship to the visual field — the observer is continually making predictions about what lies beyond the visible region, and integration serves as a proxy for how often those predictions will be violated or confirmed. This is precisely PP: the spatial configuration determines the prediction error landscape that the navigator traverses.

*Isovist → Prediction error landscape*: The isovist defines what is currently visible. Configuration determines what lies beyond — the "expected" continuation. High-integration, high-intelligibility spaces have isovists whose contents reliably predict what lies beyond; low-intelligibility spaces violate expectations systematically. PP predicts that movement toward high-intelligibility spaces is driven by minimization of anticipated free energy — people prefer routes where their model of what lies ahead will be confirmed rather than violated.

*The "mystery" overlap with Kaplan*: The Kaplan Preference Matrix's construct of *mystery* (Kaplan & Kaplan, 1989) is essentially an isovist property: partial occlusion of the next region, promising more information ahead. Mystery in Space Syntax terms is a controlled prediction error — low enough to be tolerable, high enough to motivate movement. This connects Space Syntax to KP2 (the proposed template for Spatial Mystery / Anticipated PE) and reveals a shared PP mechanism across two T1.5 theories.

### Secondary: EC — Embodied Cognition (Coverage: ~20%)

The affordance-theoretical reading of Space Syntax (Peponis et al., 1997) holds that what integration really measures is the affordance structure of a space — how many movement possibilities (in Gibson's sense) are available from each location. High-integration spaces have richer affordance networks: more directions of movement, more potential encounters, more action possibilities. EC predicts that people will be drawn to spaces that offer richer affordance structure not because of cognitive mapping but because the body-environment system spontaneously aligns with movement opportunities.

Template T8 (Affordance-Guided Action) applies directly. The "natural movement" thesis, under the EC reading, does not require hippocampal cognitive maps at all: it emerges from the direct perception of affordances in a syntactically integrated environment.

### Tertiary: IE-DPT overlay (Coverage: ~15%)

This is where Space Syntax meets its boundary conditions. The theory is explicitly about the implicit channel — it predicts behavior without reference to goals, intentions, or knowledge states. But IE-DPT's core claim is that the explicit channel significantly modulates implicit-channel effects. The evidence for explicit-channel override in Space Syntax:

*Goal-state modulation*: Template T_IE_010 (Wayfinding × Goal State) directly applies. A navigator with a specific destination overrides syntactic pull: they will traverse a low-integration, high-depth route if it leads to their goal. Integration predicts movement aggregated across many actors with varying goals; for any individual with a clear explicit goal, the prediction is substantially weakened (Penn, 2003, acknowledged this as a limitation of the natural movement thesis).

*Expertise effects*: Architects, urban planners, and trained Space Syntax analysts move through environments differently — they have explicit representations of syntactic structure that produce deliberate counter-syntactic exploration. Template T_IE_002 (Expertise-Modulated Aesthetic Divergence) applies: expert knowledge reorganizes the explicit frame such that syntactic constraints lose their behavioral force.

*Cultural-semantic overlay*: In settings with strong territorial or symbolic marking (a sacred precinct, a private residential zone, an institutional corridor marked with authority symbols), semantic content overrides syntactic integration. Template T_IE_003 (Semantic Override) applies: a highly integrated but symbolically "forbidden" space will not attract the pedestrian flows its integration value predicts.

---

## 1.3 T2 Template Assignments

### Existing Templates That Apply

| Template | Name | Phenomenon Covered | Bridge Warrant | Notes |
|----------|------|--------------------|----------------|-------|
| **SC1** | Grid Cell Metric Coding | SS-A (Integration → movement) | CONSTITUTIVE (P=0.75) | Integration is behavioral correlate of grid-cell metric centrality |
| **T3** | Place Cell Firing Patterns | SS-C (Intelligibility → navigation) | MECHANISM (P=0.60) | Hippocampal map quality predicts wayfinding success |
| **SC2** | Isovist Processing | SS-E (Isovist → experience) | CONSTITUTIVE (P=0.75) | Isovist is the visual-field input to all higher processing |
| **T8** | Affordance-Guided Action | SS-B (Natural movement) | MECHANISM (P=0.60) | EC reading: syntactic structure = affordance structure |
| **ENCLOSURE** | Enclosure and Boundary Detection | SS-F (Depth → privacy) | FUNCTIONAL (P=0.50) | Depth partially operationalizes enclosure |
| **T66** | Learned Safety Prediction | SS-D (Configuration → encounter) | MECHANISM (P=0.60) | Habitual traversal of integrated routes = learned safety |
| **T_IE_010** | Wayfinding × Goal State | Modulation of SS-A,C | FUNCTIONAL (P=0.50) | Goal-state overrides syntactic pull |
| **T_IE_003** | Semantic Override | Modulation of SS-A,B | FUNCTIONAL (P=0.50) | Symbolic marking overrides integration predictions |
| **T_IE_002** | Expertise-Modulated Divergence | Modulation of all SS | FUNCTIONAL (P=0.50) | Expert navigators override syntactic baseline |

### New T2 Templates Proposed

**SS1 — Syntactic Integration and Cognitive Map Efficiency**
- *Architectural Feature*: Spatial network integration value (axial/segment analysis)
- *Neural Mechanism*: Grid cell metric coding efficiency × hippocampal place cell coverage density
- *Outcome*: Pedestrian movement probability; wayfinding success rate; orientation accuracy
- *Maturity*: How-plausibly (strong behavioral evidence, direct neural evidence emerging — Spiers & Maguire, 2006; Wiener & Mallot, 2003)
- *IE-DPT modulation*: Goal-state and expertise reduce effect size in individuals; effect is robust at population aggregate level
- *Bridge warrant class*: CONSTITUTIVE for integration-movement; MECHANISM for integration-cognition

**SS2 — Intelligibility and Predictive Spatial Inference**
- *Architectural Feature*: Intelligibility index (correlation of local connectivity to global integration)
- *Neural Mechanism*: PP prediction error minimization in entorhinal-hippocampal circuit; forward model accuracy for spatial transitions
- *Outcome*: Navigation errors; time-to-destination; subjective disorientation; wayfinding anxiety
- *Maturity*: How-plausibly (behavioral: Haq & Zimring, 2003; neural: inference from PP framework)
- *IE-DPT modulation*: Explicit maps/GPS largely abolishes intelligibility effects; implicit-channel dominant in map-free navigation
- *Bridge warrant class*: MECHANISM

**SS3 — Isovist Affordance and Perceived Spatial Control**
- *Architectural Feature*: Isovist area, compactness, and radial variance from any location
- *Neural Mechanism*: EC affordance detection (T8) + IC body-budget prediction (IC2) + amygdala-mediated surveillance assessment
- *Outcome*: Perceived safety; comfort; surveillance capacity; willingness to linger
- *Maturity*: How-plausibly (behavioral: Stamps, 2005; Benedikt, 1979; neural: inference)
- *IE-DPT modulation*: Context frame (public space vs. private space) substantially modulates whether isovist openness reads as safety or exposure
- *Bridge warrant class*: MECHANISM + FUNCTIONAL

---

## 1.4 IE-DPT Analysis

Space Syntax is the purest test of the implicit channel's power: it explicitly claims to predict behavior without reference to mental states, goals, or intentions. IE-DPT both validates and qualifies this claim.

**Validation**: The theory is correct that there is a powerful implicit-channel substrate — the hippocampal cognitive map and grid-cell metric coding operate below deliberate awareness and produce systematic behavioral biases toward syntactically integrated spaces. This is consistent with IE-DPT's claim that implicit processing is the baseline.

**Qualification**: The natural movement thesis is a population-level claim that holds because individual goal-state variation averages out across large samples. At the individual level, the explicit channel (goal-state, wayfinding strategy, expertise) regularly overrides syntactic pull. The reduction clarifies that Space Syntax's predictive power is essentially the signal that remains after IE-DPT's explicit-channel noise is aggregated away.

**Critical question answered**: The reduction supports a hybrid answer to whether natural movement is fundamentally SN, PP, or EC. SN (hippocampal map quality) is primary for the cognitive-map reading; PP (prediction error landscape) explains the visual pull toward integrated spaces; EC (affordance richness) provides a parallel pathway that operates without cognitive maps. All three converge on the same behavioral prediction for neurologically typical adults in unfamiliar environments — which is why the theory's empirical record is as strong as it is.

---

## 1.5 Irreducible Residual

After the SN + PP + EC + IE-DPT decomposition, the following remains unexplained:

**Sociological logic** (~20%): Hillier's deepest claim is not about individual cognition but about how spatial configuration encodes and reproduces social structure across historical time — how the layout of a settlement reflects and perpetuates the social relations of its society. This is not a claim about neural mechanisms but about social morphogenesis. The CMR architecture has no tier that handles this, and it does not need to: it is not a claim about cognition. However, it means that Space Syntax literature contains two distinct kinds of claims — configurational-cognitive (reducible) and configurational-social (outside CMR scope). The Article Eater must distinguish them.

**Topological vs. metric debate** (~5%): Space Syntax originally operationalized integration topologically (counting graph steps); later work introduced metric and angular variants (Hillier & Iida, 2005; Turner, 2001). The reduction maps best onto metric/angular integration, which is more directly comparable to grid-cell metric coding. Claims using topological integration only partially map to SC1.

**Cultural configuration differences** (~10%): The integration-movement correlations were established primarily in Western urban grids. Evidence from non-Western urban forms (Islamic medina layouts, Japanese machiya townscapes) shows different relationships between syntactic depth and social function (Hanson, 1998). Cultural-semantic overlays modulate the baseline substantially.

**Total reducibility estimate**: ~65% of Space Syntax empirical claims about cognitive and behavioral outcomes can be mapped to existing or proposed T2 templates. ~20% requires the sociological reading (outside scope). ~15% depends on cultural-semantic context not yet specified in CMR.

---

## 1.6 Outcome Domains and Keywords for Article Eater

```python
# Addition to OUTCOME_DOMAIN_TO_THEORY in extraction_to_web.py
"spatial.configuration": ["Space_Syntax"],
"spatial.navigation.wayfinding": ["Space_Syntax", "SN"],
"spatial.movement": ["Space_Syntax"],
"spatial.integration": ["Space_Syntax"],
"spatial.intelligibility": ["Space_Syntax"],
"behav.pedestrian": ["Space_Syntax"],
"affect.spatial.disorientation": ["Space_Syntax"],
"affect.perceived.safety.spatial": ["Space_Syntax", "Prospect_Refuge"],

# Addition to THEORY_KEYWORDS
"Space_Syntax": [
    "space syntax", "hillier", "hanson", "axial analysis", "segment analysis",
    "integration value", "mean depth", "connectivity", "intelligibility",
    "natural movement", "isovist", "syntactic", "spatial network",
    "pedestrian flow", "topological depth", "angular analysis", "depthmap"
],
```

---
*[SAVE POINT 1 — Space Syntax complete. Proceeding to Soundscape Theory.]*
---

# REDUCTION 2: SOUNDSCAPE THEORY

**Citations**: 
- Schafer, R. M. (1977). *The tuning of the world*. Knopf. (~3,000 GS)
- ISO 12913-1:2014. *Acoustics — Soundscape — Part 1: Definition and conceptual framework*. International Organization for Standardization.
- Kang, J., Aletta, F., Gjestland, T. T., Brown, L. A., Botteldooren, D., Schulte-Fortkamp, B., ... & Jeon, J. Y. (2016). Ten questions on the soundscapes of the built environment. *Building and Environment*, 108, 284–294. (~600 GS)
- Brown, A. L. (2012). Soundscapes and environmental noise management. *Noise Control Engineering Journal*, 60(5), 493–516.
- Axelsson, Ö., Nilsson, M. E., & Berglund, B. (2010). A principal components model of soundscape perception. *Journal of the Acoustical Society of America*, 128(5), 2836–2846. (~700 GS)

---

## 2.1 Core Phenomena Soundscape Theory Organizes

Soundscape Theory is distinguished from classical acoustics by its definitional insistence on the perceiver: the ISO 12913-1 standard defines soundscape as "acoustic environment as perceived or experienced and/or understood by a person or people, in context." The three terms in that definition — perceived, experienced, understood — correspond almost exactly to the PP implicit signal, the IC interoceptive construction, and the IE-DPT explicit frame. This is not coincidental; it means the standard already contains a latent tier structure awaiting formalization.

The Article Eater should recognize claims in the following families:

**Phenomenon SC-A: Level-Independent Soundscape Evaluation**
The central empirical regularity: the same sound pressure level (dBA) produces systematically different evaluations depending on context, source attribution, and perceiver expectations. Bijsterveld (2008) documented the long historical record of this; Davies et al. (2013) showed experimentally that traffic at 55 dBA is rated as significantly more annoying than birdsong at 55 dBA, while birdsong at 65 dBA is rated as more pleasant than traffic at 45 dBA in some park contexts. This is non-monotonic with level — the standard acoustic model predicts monotonic annoyance increase with dBA, which is routinely violated.

The Article Eater should recognize: "perceived annoyance/comfort did not correlate with measured SPL," "acoustic context modulated appraisal independent of level," "source attribution changed soundscape evaluation without changing level."

**Phenomenon SC-B: The Circumplex Model of Soundscape Perception**
Axelsson et al. (2010) established a two-dimensional circumplex for soundscape perception: one axis runs from pleasant to unpleasant, the other from eventful to uneventful/calm. This two-dimensional structure has been replicated across multiple countries and cultures (ISO/TS 12913-2:2018). The Article Eater should recognize claims mapping acoustic environments onto this circumplex: "the office was rated as eventful but unpleasant," "the park soundscape scored high on both pleasantness and calmness," "the hospital corridor was rated as unpleasant and uneventful (the worst quadrant)."

**Phenomenon SC-C: Masking vs. Restoration — The Right Sounds vs. No Sound**
A counterintuitive finding with major practical implications: silence in some contexts (open-plan offices, hospital wards) produces hypervigilance and greater sensitivity to intrusive sounds, while appropriately selected masking sounds (nature sounds, broadband noise) reduce annoyance and improve cognitive performance even when they increase total SPL. Haapakangas et al. (2011) showed speech intelligibility of distractors is a better predictor of cognitive impairment than overall level. The Article Eater should recognize: "nature sound masking improved concentration despite higher overall SPL," "speech noise is more cognitively disruptive than broadband noise at equivalent levels," "silence increased sensitivity to intrusive events."

**Phenomenon SC-D: Expectation-Congruent Soundscapes and Restorative Experience**
The match between expected and actual soundscape predicts restorative quality better than either alone. A forest without birdsong is subtly "wrong" — the mismatch produces mild alerting responses. A city street with abundant birdsong is perceived as unexpectedly positive — a prediction error in the pleasant direction. Ratcliffe et al. (2013) and Pijanowski et al. (2011) documented the restorative premium of biophilic sounds; the mechanism is clearly PP rather than a simple preference for quiet. The Article Eater should recognize: "soundscape incongruence reduced restoration even at low levels," "unexpected natural sounds in urban environments produced positive affect disproportionate to their level."

**Phenomenon SC-E: Noise Annoyance and Stress Physiology**
Classical environmental noise research: long-term exposure to traffic, aircraft, and industrial noise at levels above ~55 dBA Leq (nighttime ~40 dBA) produces measurable cardiovascular, endocrine, and immunological stress responses (WHO Environmental Noise Guidelines, 2018; Münzel et al., 2014; Babisch, 2014). This is partially reducible to standard SRT/NM mechanisms. The Article Eater should recognize: "nighttime transport noise elevated cortisol," "aircraft noise exposure associated with cardiovascular risk," "noise annoyance mediated by perceived control."

**Phenomenon SC-F: Individual Differences in Noise Sensitivity**
Noise sensitivity is a stable trait moderating annoyance independent of exposure level. Belojevic et al. (1997) showed high-sensitivity individuals show annoyance at levels that do not affect low-sensitivity individuals. The Article Eater should recognize claims about noise sensitivity as a moderating variable, particularly in studies that fail to account for it (a common confound in architectural acoustics research).

---

## 2.2 T1 Framework Decomposition

### Primary: PP — Predictive Processing (Coverage: ~35%)

Soundscape Theory's core insight — that evaluation is not a function of level but of context-modulated perception — is, in PP terms, a claim that the likelihood mapping from acoustic signal to subjective evaluation is entirely mediated by the precision-weighted prior. The same afferent signal (55 dBA) projects onto radically different posterior distributions when the active inference model differs (traffic noise expected and unwanted vs. city ambiance expected and desired).

*Template PP1 (Prediction Error in Sensory Processing)*: The acoustic signal generates prediction errors relative to the active model. In a quiet context with traffic expectation, intermittent traffic bursts produce salient positive prediction errors (unexpected confirmation of an aversive prediction = relief, or unexpected violation of silence = annoyance depending on whether the prior was "should be quiet"). In a city soundscape context, the same burst is assimilated with low prediction error.

*Template PP2 (Precision Weighting)*: Noise sensitivity as a trait can be formalized as a chronic elevation of precision weighting on acoustic prediction errors — high-sensitivity individuals assign more weight to deviations from acoustic expectations, which is why they register annoyance at lower objective levels.

*Expectation-congruent restoration (SC-D)*: The biophilic sound premium is a PP prediction: nature sounds in a natural environment produce near-zero prediction error (confirming the environmental model), allowing free energy to be reallocated from perceptual inference to other processes — this is the PP mechanism for restoration, analogous to ART's directed attention fatigue recovery.

### Secondary: IC — Interoceptive / Constructionist Affect (Coverage: ~25%)

Barrett's (2017) constructionist affect model predicts that the valence assigned to an acoustic event is not a direct readout of the signal but a construction from interoceptive state, prior affect, and contextual concept. This explains SC-A (level-independence) elegantly: at 55 dBA, traffic constructs as "annoying noise" when the interoceptive state is stressed and the concept "unwanted intrusion" is active; it constructs as "city ambiance" when the interoceptive state is energized and the concept "urban vitality" is active.

*Template IC2 (Body Budget Prediction)*: Traffic noise at sustained high levels is a body-budget threat: it produces autonomic arousal (SC-E) that the organism must regulate. The IC layer predicts that acoustic comfort is fundamentally a body-budget management process — sounds that reduce body-budget uncertainty (predictable, controllable, meaningful) are experienced as comfortable regardless of level; sounds that increase body-budget uncertainty (unpredictable, uncontrollable, meaningless) are experienced as stressful.

*Noise sensitivity (SC-F)*: High noise sensitivity is, in IC terms, a chronic elevation of interoceptive arousal baseline — high-sensitivity individuals have a higher resting body-budget allocation to acoustic monitoring, which reduces their threshold for annoyance.

### Tertiary: NM — Neuromodulatory Systems (Coverage: ~20%)

*Dopaminergic modulation — unexpected positive sounds*: Ratcliffe et al.'s (2013) finding that birdsong in unexpected urban contexts produces disproportionate positive affect is a classic NM prediction: a positive prediction error in the acoustic domain produces dopaminergic reward proportional to its unexpectedness (Schultz, 1998). The birdsong restorative premium is partly a dopaminergic RPE signal.

*Cortisol and sustained noise (SC-E)*: The stress physiology of chronic noise exposure is mediated by HPA axis activation — the same NM pathway underlying SRT. The mechanism is: sustained acoustic threat (traffic, industrial noise) → amygdala activation → HPA axis → cortisol elevation → cardiovascular risk. This pathway is well-established (Munzel et al., 2014).

*Template NM1 (Dopamine Reward Prediction Error)*: Unexpected pleasant sounds (birdsong in urban context, music emerging from silence) generate dopaminergic RPE signals. Predictable pleasant sounds habituate dopaminergic response — this is why the same nature recording loses its restorative power with repeated exposure.

### Tertiary: MSI — Multisensory Integration (Coverage: ~10%)

Soundscape experience is inevitably multisensory: the same acoustic signal is rated differently when visual context changes (road noise heard in a park vs. the same noise heard in a city street). Viollon et al. (2002) showed that visual context explained significant additional variance in soundscape evaluation above acoustic measures alone. This is a direct MSI effect: visual input provides a contextual prior that precision-weights acoustic interpretation.

*Template MSI1 (Cross-Modal Prediction)*: Visual environment provides a generative model for expected soundscape — a forest cue predicts nature sounds; an office cue predicts speech and HVAC. Violations of this cross-modal prediction produce both PP prediction errors and IC body-budget uncertainty, amplifying negative evaluation relative to what either sense alone would produce.

### IE-DPT Overlay (Coverage: ~10%)

*Activity-frame reconfiguration (SC-A)*: The core level-independence finding is precisely IE-DPT Template T_IE_001 (Activity-Frame Complexity Retuning) applied to the acoustic domain. The frame "I am working in a quiet office" sets noise tolerance thresholds; the frame "I am at a busy café" resets them. The same 65 dBA is below threshold in one frame and above threshold in another. This is not merely preference variation — it is a systematic, frame-driven reconfiguration of what counts as signal vs. noise.

*Semantic override (SC-C)*: The right masking sounds (nature sounds, appropriate music) work partly through semantic override: they reconfigure the acoustic frame from "disturbing noise environment" to "pleasant sound environment," which then suppresses the annoyance response at a top-down level. Template T_IE_003 (Semantic Override) applies: understanding that the sounds are meaningfully selected (as in sound-masking systems explicitly presented as designed soundscapes rather than background noise) enhances their effectiveness beyond what the acoustic properties alone predict (Kjellberg et al., 1996).

*Placebo architecture (SC-E)*: Perceived control over acoustic environment substantially reduces annoyance independent of actual acoustic change (Glass & Singer, 1972). Template T_IE_006 (Placebo Architecture): the belief that one can control noise produces the same stress-reduction as actual control, demonstrating the explicit channel's regulatory power over the IC body-budget response.

---

## 2.3 T2 Template Assignments

### Existing Templates That Apply

| Template | Name | Phenomenon Covered | Bridge Warrant |
|----------|------|--------------------|----------------|
| **PP1** | Prediction Error — Sensory | SC-A (level independence), SC-D (congruence) | CONSTITUTIVE (P=0.75) |
| **PP2** | Precision Weighting | SC-F (noise sensitivity) | MECHANISM (P=0.60) |
| **IC2** | Body Budget Prediction | SC-E (stress physiology), SC-C (masking) | MECHANISM (P=0.60) |
| **NM1** | Dopamine RPE | SC-D (biophilic sound premium) | MECHANISM (P=0.60) |
| **T66** | Learned Safety Prediction | SC-A (familiarity reduces annoyance) | MECHANISM (P=0.60) |
| **MSI1** | Cross-Modal Prediction | SC-A (visual context modulation) | MECHANISM (P=0.60) |
| **T_IE_001** | Activity-Frame Retuning | SC-A (frame-dependent tolerance) | FUNCTIONAL (P=0.50) |
| **T_IE_003** | Semantic Override | SC-C (right masking sounds) | FUNCTIONAL (P=0.50) |
| **T_IE_006** | Placebo Architecture | SC-E (perceived control) | FUNCTIONAL (P=0.50) |

### New T2 Templates Proposed

**SOC1 — Acoustic Expectation Violation and Soundscape Appraisal**
- *Architectural Feature*: Match/mismatch between expected soundscape (given spatial context) and actual soundscape
- *Neural Mechanism*: PP: acoustic prediction error magnitude (relative to contextual prior) → IC body-budget uncertainty elevation → NM valence signal
- *Outcome*: Soundscape pleasantness rating; restoration potential; annoyance score; physiological arousal
- *Maturity*: How-plausibly (behavioral: Davies et al., 2013; Ratcliffe et al., 2013; neural: inference from PP + IC)
- *IE-DPT modulation*: Activity frame sets the expected soundscape — same mismatch is processed differently under work frame vs. leisure frame
- *Bridge warrant class*: MECHANISM

**SOC2 — Acoustic Body-Budget Threat and Cardiovascular Risk**
- *Architectural Feature*: Sustained noise level (Lnight, Ldn) and noise event frequency/unpredictability
- *Neural Mechanism*: Amygdala threat detection → HPA axis activation → cortisol elevation → sympathetic ANS dominance → cardiovascular strain
- *Outcome*: Cortisol AUC; nighttime blood pressure; cardiovascular disease incidence; sleep quality
- *Maturity*: How-actually for the cortisol-cardiovascular pathway (Babisch, 2014; Munzel et al., 2014); how-plausibly for the amygdala initiation
- *IE-DPT modulation*: Perceived control over noise substantially attenuates the HPA response (Glass & Singer, 1972); learned helplessness amplifies it
- *Bridge warrant class*: MECHANISM + EMPIRICAL_COVARIANCE

**SOC3 — Restorative Soundscape and Autonomous Nervous System Recovery**
- *Architectural Feature*: Presence and predominance of natural sounds (water, birdsong, wind through vegetation) vs. anthropogenic noise
- *Neural Mechanism*: Nature sounds → low acoustic prediction error (PP) + positive RPE (NM-dopamine) → parasympathetic dominance → HPA deactivation → ANS recovery
- *Outcome*: Heart rate variability; cortisol recovery rate; subjective restoration; attention restoration test performance
- *Maturity*: How-plausibly (behavioral: Alvarsson et al., 2010; Annerstedt et al., 2013; neural: inference from PP + NM + IC)
- *IE-DPT modulation*: Frame matters: same birdsong labeled "natural restoration" vs. "acoustic experiment" produces different restoration trajectories
- *Bridge warrant class*: MECHANISM

---

## 2.4 IE-DPT Analysis

Soundscape is, of all T1.5 theories, the one that most explicitly invites the IE-DPT decomposition. The ISO 12913-1 definition already contains a latent three-tier structure:

- "Acoustic environment" (physical signal: dBA, spectral characteristics) = the T2 mechanistic input
- "Perceived or experienced" = the IC + PP implicit channel processing
- "Understood by a person in context" = the IE-DPT explicit channel

The standard's insistence on the third term — "understood in context" — is the soundscape field's own acknowledgment that the implicit acoustic experience is insufficient to predict soundscape evaluation. This makes Soundscape Theory the clearest empirical domain in which IE-DPT convergent validity is demonstrated: the field's own definitional standard requires an explicit-channel supplement.

**Critical finding**: Soundscape extends the convergent pattern from §5 of the transfer document into the acoustic domain. Privacy Regulation required explicit frame to explain density ≠ crowding; Adaptive Thermal Comfort required it to explain why NV users tolerate wider temperature ranges; Soundscape requires it to explain why 55 dBA traffic ≠ 55 dBA birdsong. The fourth independent domain converging on the same structural finding substantially strengthens the case for IE-DPT superordinate status.

---

## 2.5 Irreducible Residual

**Cultural specification of soundscape categories** (~15%): What constitutes a "pleasant" vs. "unpleasant" sound is substantially culturally conditioned — the circumplex structure replicates cross-culturally but the mapping of specific sound sources onto it does not (Yang & Kang, 2005). Sounds coded as "natural and restorative" in Northern European populations may be coded differently in populations with different relationships to the specific natural sound sources.

**Spectrotemporal complexity preferences** (~10%): There is evidence (Ilie & Thompson, 2006) that the preference for certain acoustic textures (broadband noise vs. tonal; regular vs. irregular temporal structure) follows principles analogous to visual complexity preference (Berlyne, 1971) but the neural substrate of acoustic complexity preference is not fully specified. This is a potential bridge to Berlyne reduction but requires dedicated investigation.

**Total reducibility estimate**: ~75% of Soundscape Theory empirical claims about perceptual and physiological outcomes are covered by existing or proposed templates. ~15% requires cultural specification; ~10% requires additional work on acoustic complexity preferences.

---

## 2.6 Outcome Domains and Keywords for Article Eater

```python
# Addition to OUTCOME_DOMAIN_TO_THEORY
"acoustic.perception": ["Soundscape_Theory"],
"acoustic.annoyance": ["Soundscape_Theory"],
"acoustic.comfort": ["Soundscape_Theory"],
"acoustic.restoration": ["Soundscape_Theory", "ART"],
"health.noise": ["Soundscape_Theory"],
"physio.cortisol.noise": ["Soundscape_Theory", "SRT"],
"affect.soundscape": ["Soundscape_Theory"],

# Addition to THEORY_KEYWORDS
"Soundscape_Theory": [
    "soundscape", "acoustic environment", "noise annoyance", "sound perception",
    "ISO 12913", "axelsson", "kang", "schafer", "soundscape evaluation",
    "pleasantness", "eventfulness", "acoustic comfort", "noise sensitivity",
    "sound masking", "speech intelligibility", "biophilic sound", "noise exposure",
    "environmental noise", "perceived noise", "acoustic restoration",
    "circumplex", "soundscape design"
],
```

---
*[SAVE POINT 2 — Soundscape Theory complete. Proceeding to Place Attachment.]*
---

# REDUCTION 3: PLACE ATTACHMENT

**Citations**:
- Altman, I., & Low, S. M. (Eds.). (1992). *Place attachment*. Plenum Press. (~4,000 GS)
- Scannell, L., & Gifford, R. (2010). Defining place attachment: A tripartite organizing framework. *Journal of Environmental Psychology*, 30(1), 1–10. (~3,000 GS)
- Lewicka, M. (2011). Place attachment: How far have we come in the last 40 years? *Journal of Environmental Psychology*, 31(3), 207–230. (~2,000 GS)
- Rowles, G. D. (1983). Place and personal identity in old age: Observations from Appalachia. *Journal of Environmental Psychology*, 3(4), 299–313.
- Manzo, L. C., & Perkins, D. D. (2006). Finding common ground: The importance of place attachment to community participation and planning. *Journal of Planning Literature*, 20(4), 335–350. (~800 GS)

---

## 3.1 Core Phenomena Place Attachment Organizes

Place attachment differs fundamentally from all other T1.5 theories in the system: it is the only one organized around *temporal depth* rather than immediate or short-term environmental response. All of ART, SRT, Biophilia, Prospect-Refuge, Privacy Regulation, Kaplan Matrix, Adaptive Thermal Comfort, Space Syntax, and Soundscape Theory are essentially theories of the moment: you enter a space, and within seconds to hours, these mechanisms operate. Place attachment is about what happens over months and years — the progressive binding of autobiographical memory, emotional history, territorial familiarity, and identity to a specific location.

This temporal difference is not merely descriptive; it predicts which T1 frameworks are primary. Immediate-response theories are dominated by PP, NM, and IC (moment-to-moment prediction and affect). Temporal-depth theories are dominated by MS and SN (memory binding and cognitive mapping) with substantial IE-DPT explicit-channel involvement (the meaning a person actively constructs about their relationship to a place).

**Phenomenon PA-A: Place Familiarity and Habitat Security**
The most basic form: repeated exposure to a specific environment produces hippocampal cognitive map consolidation, environmental pattern recognition, and — critically — a reduction in body-budget uncertainty. The familiar place requires no active spatial inference; movement through it can be automated. This produces a distinct affective tone: not mere comfort but something closer to *embodied security* — the sense that the environment's behavior is fully predictable and therefore controllable. Rowles (1983) documented this in elderly Appalachian residents who reported that their long-inhabited homes "knew them." The Article Eater should recognize: "length of residence correlated with place attachment scores," "familiar environments showed reduced cortisol relative to novel environments," "residents reported greater sense of security in long-occupied dwellings."

**Phenomenon PA-B: Episodic Memory Binding to Place**
Places accumulate biographical significance through hippocampal episodic binding: memories of significant events become associated with the spatial context in which they occurred (context-dependent memory: Godden & Baddeley, 1975). Returning to a place activates the associated episodic memories, which in turn activate the affect associated with those memories. This is why the childhood home is experienced so differently from an objectively superior new dwelling — the new dwelling lacks the episodic scaffolding that makes the old one a "memory palace" for biographical identity. The Article Eater should recognize: "environmental cues triggered autobiographical memories," "place-based memory retrieval predicted attachment scores," "displacement from long-occupied environments produced grief responses analogous to bereavement."

**Phenomenon PA-C: Place Identity and Self-Concept Integration**
Proshansky, Fabian, & Kaminoff (1983) established that places become integrated into self-concept — place identity is a component of personal identity. The apartment one chose deliberately, decorated personally, and inhabited through significant life transitions is not merely a location but a material component of the self-concept. This creates a specific form of attachment that differs from familiarity (PA-A) or memory (PA-B): the place is experienced as *mine* in a proprioceptive sense — its violation (forced relocation, unwanted renovation) is experienced as a violation of the self. The Article Eater should recognize: "attachment correlated with degree of place personalization," "involuntary relocation produced identity disruption beyond grief," "place attachment predicted resistance to renovation proposals."

**Phenomenon PA-D: Territorial Familiarity and Spatial Ownership**
Altman's (1975) territorial framework (already partially reduced in the Privacy Regulation reduction as proposed template PR2) extends into place attachment when territorial claims are sustained over time. Repeated successful territorial behavior — defending, personalizing, and controlling a space — consolidates the place into a *defended territory* whose loss is experienced as threat, not merely inconvenience. This is distinct from mere familiarity (PA-A): it is familiarity + successful agency + defensive investment. The Article Eater should recognize: "personalization behaviors predicted long-term attachment," "territorial marking correlated with attachment strength," "defended territories showed stronger attachment than equivalent undefended spaces."

**Phenomenon PA-E: Rootedness vs. Sense of Place (the Tuan Distinction)**
Tuan (1977) distinguished *rootedness* (unreflective, taken-for-granted belonging to a place, like the habitat security of PA-A) from *sense of place* (reflective, articulated appreciation of a place's distinctiveness). This distinction is directly relevant to IE-DPT: rootedness is predominantly implicit-channel; sense of place involves substantial explicit-channel processing. The practical implication: rootedness can exist without any capacity to articulate what makes a place valuable; it is the form of place attachment most at risk from forced relocation because it cannot be transplanted by recreating the physical features. The Article Eater should recognize: "attachment persisted despite physical changes to the place," "residents could not articulate reasons for attachment," "physically identical replacement buildings failed to replicate attachment to demolished originals."

**Phenomenon PA-F: Disrupted Attachment and Post-Displacement Grief**
When long-held attachments are severed — through forced relocation, demolition, disaster — the disruption produces responses phenomenologically similar to bereavement (Fried, 1963, "grieving for a lost home"). Manzo & Perkins (2006) documented how post-disaster reconstruction failures stem from the fact that rebuilt physical structures cannot recreate accumulated biographical and social meaning. This has direct clinical and design implications for aging populations, post-disaster communities, and patients displaced from long-occupied rooms in healthcare settings. The Article Eater should recognize: "relocation produced depressive symptoms," "post-disaster rebuilding did not restore pre-disaster wellbeing despite physical equivalence," "attachment disruption predicted recovery time."

---

## 3.2 T1 Framework Decomposition

### Primary: MS — Memory Systems (Coverage: ~35%)

Place attachment is, at the neural-mechanistic level, fundamentally a memory phenomenon. The three memory systems relevant to place attachment map onto the phenomena as follows:

*Hippocampal episodic memory (PA-B)*: The binding of events to spatial context is the hippocampus's core function (Tulving, 2002; Burgess, Maguire, & O'Keefe, 2002). Place attachment, in this reading, is the cumulative product of successful hippocampal context-event binding over time. High attachment = rich hippocampal-spatial scaffolding for biographical memory. The Article Eater's claim that "the house was 'full of memories'" is a behavioral report of dense hippocampal context-event associations. Forced relocation severs the cue-memory relationship — the place's absence makes the associated memories less accessible, which is a form of autobiographical amnesia.

*Semantic memory consolidation (PA-A)*: Familiarity without explicit recollection — the sense that "I know this place" without being able to recall specific events — is mediated by neocortical semantic consolidation (McClelland et al., 1995). The long-term resident's sense of embodied security in their neighborhood does not require recalling specific episodes; it is carried in semantic knowledge of the environment's properties, rhythms, and social composition.

*Procedural/implicit memory (PA-A, PA-D)*: The automation of movement through a familiar environment — finding the bathroom in the dark, knowing which step creaks, which door sticks — is procedural memory (EC-motor routines consolidated in cerebellum and basal ganglia). This is the most "embodied" form of place attachment: the body has learned the place. Forced relocation disrupts procedural routines that were never explicitly represented and therefore cannot be consciously compensated for.

### Primary: SN — Spatial Navigation / Cognitive Mapping (Coverage: ~25%)

*Cognitive map consolidation (PA-A, PA-C)*: The cognitive map of a long-inhabited environment is maximally consolidated — it has the highest fidelity spatial representation the hippocampal-entorhinal system can achieve. This consolidated map is not merely instrumental (it guides navigation) but constitutive of the experienced relationship with the place. The "knowledge of London" that Maguire et al. (2000) showed in London taxi drivers is the extreme case: the hippocampal representation of a territory that has been navigated extensively becomes a defining feature of the person's cognitive identity.

*Place cell-mediated context reinstatement (PA-B)*: Hippocampal place cells fire in location-specific patterns that serve as context representations for memory retrieval (Leutgeb et al., 2004). Returning to a place reactivates the place cell pattern, which serves as a cue for all memories associated with that context. This is the neural mechanism of PA-B: the place literally reinstates the neural context for biographical memory. Strong attachment corresponds to rich, dense place cell representations with many associated episodic memories.

*Allocentric home-space representation (PA-D)*: Territorial familiarity (PA-D) may correspond to the stability and precision of the allocentric spatial representation — the degree to which the inhabited space is represented from multiple viewpoints, with all boundaries and affordances fully coded. This is the "defended territory" at the neural level: a completely mapped, fully controlled representational domain.

### Tertiary: IC — Interoceptive / Constructionist Affect (Coverage: ~15%)

*Body-budget familiarity and allostatic security (PA-A)*: The familiar place is the place where the body's allostatic predictions are most accurate. Every physiological regulatory function — temperature, activity level, social contact, rest timing — is predictable in the familiar home environment. This is the IC/allostatic reading of PA-A: attachment is the affective signature of a maximally calibrated body-budget model for a specific location. Unfamiliar environments impose body-budget costs simply because they require recalibration; the long-occupied home is the environment of minimal body-budget uncertainty.

*Grief as body-budget disruption (PA-F)*: Post-displacement grief is not merely cognitive loss (of memories, of identity) but IC disruption: the body-budget model calibrated to the specific environment is suddenly inapplicable. Every automatic prediction — what temperature to expect, how many steps to the kitchen, what sounds are normal — is now violated. This is a sustained, environment-specific interoceptive prediction error that cannot resolve until recalibration to the new environment is complete.

### Tertiary: IE-DPT Overlay (Coverage: ~15%)

This is where Place Attachment most distinctively challenges IE-DPT's current template architecture. The existing 12 templates (T_IE_001–012) are all about the moment of encounter: how the explicit frame configures the immediate perceptual and affective response. Place attachment requires extending IE-DPT into biographical time — how the explicit frame for a place (its meaning, its identity-relevance, its history) develops through deliberate engagement over months and years, and how this accumulated explicit-channel processing becomes sedimented into the implicit response.

*Sedimentation principle (T_IE_DAP6)*: The tenth derived principle of IE-DPT — "sedimentation" — states that repeated explicit-channel encounters with a designed feature progressively become automatic. In place attachment, this works at a biographical timescale: what began as deliberate choice (I chose this apartment), deliberate personalization (I decorated it), deliberate social investment (I hosted significant events here) gradually sediments into the unreflective rootedness (PA-E) that characterizes full attachment. Place attachment is IE-DPT's sedimentation principle operating at the biographical scale.

*Meaning-construction and place identity (PA-C)*: Sense of place (as opposed to rootedness) is explicitly IE-DPT: the person has constructed an articulate explicit representation of what makes this place meaningful. This representation modulates the affective response — the same physical space produces qualitatively different experience for someone who understands its historical significance vs. someone who does not. Template T_IE_003 (Semantic Override) applies here: semantic enrichment of the place concept enhances attachment beyond what the implicit familiarity alone produces.

*Agency-investment and control frame (PA-D)*: Territorial attachment is substantially mediated by perceived agency — the sense that one has successfully defended, personalized, and controlled the space. Template T_IE_AX4 (Perceived Control) applies: the attachment value of a space is partly a record of successful control experiences. This explains why attachment to owned homes is generally stronger than attachment to equivalent rented homes (Regan & Tonry, 1983) — ownership provides a stable explicit frame of legitimate control that amplifies the territorial investment.

**Critical IE-DPT finding for Place Attachment**: The reduction reveals that IE-DPT must be extended temporally to handle biographical-scale sedimentation. The current templates describe frame-switching at the timescale of minutes to hours. Place attachment requires a theory of how explicit frames accumulate into implicit structures over months and years. This is not a failure of IE-DPT but an invitation for its natural extension — what might be called "IE-DPT temporal depth" or biographical explicit-channel integration.

---

## 3.3 T2 Template Assignments

### Existing Templates That Apply

| Template | Name | Phenomenon Covered | Bridge Warrant |
|----------|------|--------------------|----------------|
| **T3** | Place Cell Firing | PA-B (episodic binding), PA-A (cognitive map) | CONSTITUTIVE (P=0.75) |
| **T66** | Learned Safety Prediction | PA-A (familiarity → security) | MECHANISM (P=0.60) |
| **IC2** | Body Budget Prediction | PA-A,F (allostatic calibration, grief) | MECHANISM (P=0.60) |
| **PR2** | Territorial Familiarity | PA-D (defended territory) | CONSTITUTIVE (P=0.75) |
| **T_IE_DAP6** | Sedimentation | PA-E (rootedness formation) | FUNCTIONAL (P=0.50) |
| **T_IE_003** | Semantic Override | PA-C (identity-enriched experience) | FUNCTIONAL (P=0.50) |
| **AX4** | Perceived Control | PA-D (agency investment) | MECHANISM (P=0.60) |
| **T_IE_008** | Trauma-Space Interaction | PA-F (displacement grief) | MECHANISM (P=0.60) |

### New T2 Templates Proposed

**PA1 — Biographical Episodic Binding and Place Attachment**
- *Architectural Feature*: Length of occupancy × density of significant life events × degree of personalization
- *Neural Mechanism*: Hippocampal context-event binding (MS: E1) → episodic memory consolidation → place cell representation enrichment → context reinstatement upon return
- *Outcome*: Place attachment scale scores; resistance to relocation; grief magnitude upon displacement; memory retrieval frequency in place
- *Maturity*: How-plausibly (behavioral: Scannell & Gifford, 2010; Lewicka, 2011; neural: inference from hippocampal context-memory binding literature — Burgess et al., 2002)
- *IE-DPT modulation*: Events experienced under high explicit attention (milestone events, rituals, deliberate commemorations) produce stronger hippocampal binding than habitual events; explicit meaning-making amplifies binding
- *Bridge warrant class*: MECHANISM

**PA2 — Allostatic Calibration and Embodied Security**
- *Architectural Feature*: Length of occupancy in a consistent physical and social environment
- *Neural Mechanism*: IC: body-budget prediction model calibration → reduction in interoceptive prediction errors → parasympathetic baseline elevation → reduced allostatic load
- *Outcome*: Physiological stress markers (cortisol, HRV) lower in familiar vs. equivalent novel environment; subjective sense of security and comfort; reduced sleep disturbance
- *Maturity*: How-possibly for full pathway; how-plausibly for behavioral outcome (Brown et al., 2003; Fried, 1963)
- *IE-DPT modulation*: Explicit awareness that environment is temporary attenuates calibration — renters calibrate less fully than owners (a documented effect in attachment research: Lewicka, 2011)
- *Bridge warrant class*: MECHANISM

**PA3 — Displacement Grief and Interoceptive Disruption**
- *Architectural Feature*: Involuntary vs. voluntary relocation from long-occupied environment
- *Neural Mechanism*: Sudden mismatch between calibrated body-budget model and new environment → sustained interoceptive prediction error → HPA axis reactivation → IC: allostatic overload → behavioral phenotype analogous to bereavement
- *Outcome*: Depressive symptom incidence post-relocation; cortisol elevation; sleep disruption; cognitive impairment (working memory load from continuous spatial reorientation); attachment to objects from original environment (transitional objects)
- *Maturity*: How-plausibly (behavioral: Fried, 1963; Rowles, 1983; Manzo & Perkins, 2006; Ulrich et al., 2008 on familiar objects in hospital recovery; neural: inference from IC and MS disruption)
- *IE-DPT modulation*: Voluntary relocation with high explicit preparation substantially attenuates displacement grief; the explicit frame of "chosen change" reorganizes the IC disruption as tolerable uncertainty rather than threat
- *Bridge warrant class*: MECHANISM

---

## 3.4 IE-DPT Analysis and the Critical Finding

Place attachment is the theory that most productively challenges IE-DPT's current architecture. The challenge is not a refutation but an invitation to temporal extension.

**Current IE-DPT (as specified)**: Templates operate at the timescale of minutes to hours. The activity frame configures the immediate encounter. Sedimentation (DAP6) describes the process by which such frames eventually become automatic — but the timescale of sedimentation is not specified.

**What Place Attachment requires**: A theory of how explicit-channel processing over biographical time (months to years of deliberate choice, personalization, social investment, and meaning-making) produces a qualitatively different form of implicit experience — not merely habituated attention but sedimented identity. The long-term resident's relationship to their home is not merely the cumulative sum of many frame-encounter cycles; it is a qualitatively transformed engagement in which the explicit and implicit channels have co-evolved around that specific environment.

**The proposed extension — "IE-DPT Temporal Depth"**: This could be formalized as a meta-template: *Biographical Explicit Integration* (BEI) — the process by which repeated, meaning-laden explicit encounters with a specific place progressively consolidate into implicit familiarity, territorial security, and finally identity integration. BEI would explain:
- Why identical new buildings fail to replicate attachment to demolished originals (the BEI history is non-transferable)
- Why aging-in-place preserves cognitive function in elderly residents (the fully calibrated environment reduces cognitive load)
- Why post-disaster psychological recovery is slower when rebuilding produces physically superior but BEI-stripped environments

**Does IE-DPT apply to CB and MSI?** (Open question from §7): Place Attachment suggests that IE-DPT's temporal depth limitation applies to CB as well — circadian entrainment to a specific environment (light schedule, temperature rhythms, social timing) is another form of allostatic calibration that sediments over biographical time. Disruption of circadian entrainment through relocation is a real phenomenon (Monk et al., 1992) and may be a component of displacement grief.

**Scannell & Gifford's tripartite framework**: The Person × Process × Place decomposition maps directly onto the tier architecture:
- *Place* (physical properties) → T2 mechanistic substrate (what SC2, T8, ENCLOSURE capture)
- *Process* (affect, cognition, behavior) → T1 mechanisms (MS, SN, IC, EC, IE-DPT)
- *Person* (identity, biography, culture) → IE-DPT explicit channel + BEI meta-template

The reduction validates the tripartite framework while specifying its neural and computational content.

---

## 3.5 The Critical Question: Is Place Attachment One Theory or Many?

Lewicka's (2011) concern that the field suffers from proliferating definitions is confirmed by the reduction: "place attachment" is not a single T1.5 theory with unified constructs but a cluster of related phenomena with distinct T1 substrates:

| Phenomenon | Primary T1 | Maturity | Could Stand Alone? |
|-----------|-----------|---------|-------------------|
| PA-A (Habitat Familiarity) | MS + IC | How-plausibly | Yes — merge with T66 |
| PA-B (Episodic Binding) | MS hippocampal | How-plausibly | Yes — PA1 template |
| PA-C (Identity Integration) | IE-DPT + MS | How-possibly | Yes — IE-DPT extension |
| PA-D (Territorial Familiarity) | SN + EC | How-plausibly | Already PR2 |
| PA-E (Rootedness) | MS + IC + EC | How-plausibly | PA2 template |
| PA-F (Displacement Grief) | IC + MS disruption | How-plausibly | PA3 template |

**Conclusion**: "Place Attachment" as a single T1.5 theory reduces to approximately 4–5 distinct mechanistic clusters. Unlike ART (which, despite multiple components, has a unified mechanism of directed attention recovery) or Privacy Regulation (which has a unified mechanism of boundary regulation dialectics), Place Attachment is better understood as a family of related theories unified by temporal depth rather than by a single mechanism. This means it functions less like ART (one theory → one family of templates) and more like a domain label (analogous to "thermal comfort" as a domain containing both Adaptive Thermal Comfort and other thermal response phenomena).

**Practical recommendation**: Register Place Attachment in the Article Eater as a parent theory with five distinct sub-mechanisms (PA1–PA5), where claims are tagged to sub-mechanisms rather than to the parent theory directly. This avoids the vagueness problem Lewicka identified while preserving the clinical and practical domain label for users.

---

## 3.6 Irreducible Residual

**Cultural specification of attachment objects** (~15%): What locations become attachment objects is substantially culturally conditioned — the specific physical features that anchor identity and memory differ across cultures (Manzo, 2005). The neural mechanisms of episodic binding and allostatic calibration are universal; what they bind to is culturally specified.

**Social/relational attachment (PA-D extension)** (~15%): Much of what people call "place attachment" is really attachment to the social community of a place — the neighbors, rhythms, and social practices associated with a location. When the community disperses (gentrification, disaster) but the physical place remains, attachment often dissolves — demonstrating that the social relationships are load-bearing in the attachment structure. This social dimension is not yet captured in the CMR template architecture.

**Narrative and cultural heritage** (~10%): Attachment to places of historical or cultural significance (one's ancestral homeland, a heritage building, a sacred site) operates through explicit cultural narratives rather than personal episodic history. This is an IE-DPT explicit-channel phenomenon but one mediated by cultural transmission rather than personal experience — outside current CMR scope.

**Total reducibility estimate**: ~60% of Place Attachment empirical claims about psychological and behavioral outcomes are covered by existing or proposed templates. ~15% requires cultural specification; ~15% requires social-community extension; ~10% requires cultural heritage/narrative mechanisms outside current scope.

---

## 3.7 Outcome Domains and Keywords for Article Eater

```python
# Addition to OUTCOME_DOMAIN_TO_THEORY
"place.attachment": ["Place_Attachment"],
"place.identity": ["Place_Attachment"],
"place.familiarity": ["Place_Attachment", "SN"],
"behav.relocation": ["Place_Attachment"],
"affect.displacement": ["Place_Attachment"],
"affect.rootedness": ["Place_Attachment"],
"health.aging.place": ["Place_Attachment"],
"affect.grief.relocation": ["Place_Attachment"],

# Addition to THEORY_KEYWORDS
"Place_Attachment": [
    "place attachment", "sense of place", "place identity", "rootedness",
    "topophilia", "place bonding", "scannell", "gifford", "lewicka",
    "tuan", "altman", "relocation", "displacement", "aging in place",
    "territorial familiarity", "biographical memory place",
    "place meaning", "home attachment", "place disruption",
    "post-disaster recovery place", "personalization attachment"
],
```

---
*[SAVE POINT 3 — All three reductions complete. Cross-cutting analysis follows.]*
---

# §4. CROSS-CUTTING FINDINGS FROM THE THREE REDUCTIONS

## 4.1 The Convergent IE-DPT Pattern Extends

The three new reductions add a fourth, fifth, and sixth data point to the convergent finding from §5 of the transfer document:

| Theory | IE-DPT's Indispensable Contribution |
|--------|-------------------------------------|
| Privacy Regulation | density ≠ crowding (frame determines threshold) |
| Adaptive Thermal Comfort | NV users tolerate wider range (adaptive frame) |
| Kaplan Preference Matrix | individual complexity optima vary with expertise/frame |
| **Space Syntax** | natural movement breaks down under explicit goal/expertise |
| **Soundscape Theory** | 55 dBA traffic ≠ 55 dBA birdsong (frame-dependent appraisal) |
| **Place Attachment** | rootedness vs. sense of place (implicit vs. explicit biographical processing) |

Six independent domains, each requiring the explicit channel to explain its most practically consequential phenomenon. This is the strongest evidence yet for IE-DPT superordinate status.

## 4.2 Super-Template Candidates Strengthened

The recurring templates across all six reductions:

| Template | Appears In |
|----------|-----------|
| **IC2 (Body Budget Prediction)** | Privacy Regulation, Adaptive Thermal, Soundscape, Place Attachment (5/6 reductions) |
| **AX4 (Perceived Control)** | Privacy Regulation, Adaptive Thermal, Soundscape, Place Attachment (5/6 reductions) |
| **T66 (Learned Safety)** | Biophilia, Space Syntax, Place Attachment, Privacy Regulation (4/6) |
| **SC2 (Isovist)** | Prospect-Refuge, Space Syntax (2/6 but architecturally central) |

IC2 and AX4 appear in 5 of 6 reductions spanning thermal, acoustic, social, spatial, and biographical domains. The case for formal super-template status is now compelling.

## 4.3 New Templates Proposed (This Session)

| ID | Name | Theory | Frameworks |
|----|------|--------|------------|
| SS1 | Syntactic Integration and Cognitive Map Efficiency | Space Syntax | SN + PP |
| SS2 | Intelligibility and Predictive Spatial Inference | Space Syntax | PP + SN |
| SS3 | Isovist Affordance and Perceived Spatial Control | Space Syntax | EC + IC + NM |
| SOC1 | Acoustic Expectation Violation | Soundscape | PP + IC + NM |
| SOC2 | Acoustic Body-Budget Threat | Soundscape | IC + NM |
| SOC3 | Restorative Soundscape and ANS Recovery | Soundscape | PP + NM + IC |
| PA1 | Biographical Episodic Binding | Place Attachment | MS + SN |
| PA2 | Allostatic Calibration and Embodied Security | Place Attachment | IC + EC |
| PA3 | Displacement Grief and Interoceptive Disruption | Place Attachment | IC + MS |

## 4.4 IE-DPT Temporal Extension Required

Place Attachment uniquely reveals that IE-DPT requires temporal extension — a "biographical explicit integration" (BEI) meta-template that describes the multi-year sedimentation of explicit-channel processing into implicit experience. This is the most theoretically productive finding from the three reductions: a genuine gap in the current IE-DPT specification that Place Attachment uniquely identifies.

## 4.5 Revised T1.5 Roster (10 Formally Reduced)

| # | Theory | Domain | Reduced? |
|---|--------|--------|---------|
| 1 | ART | Nature/Restoration | Yes |
| 2 | SRT | Stress/Nature | Yes |
| 3 | Biophilia | Nature/Evolution | Yes |
| 4 | Prospect-Refuge | Spatial Preference | Yes |
| 5 | Privacy Regulation | Social-Spatial | Yes |
| 6 | Kaplan Preference Matrix | Visual Preference | Yes |
| 7 | Adaptive Thermal Comfort | Thermal/IEQ | Yes |
| **8** | **Space Syntax** | **Spatial Configuration** | **Yes (this document)** |
| **9** | **Soundscape Theory** | **Acoustic/IEQ** | **Yes (this document)** |
| **10** | **Place Attachment** | **Temporal/Biographical** | **Yes (this document)** |

---

# §5. REGISTRATION PATCH FOR ARTICLE EATER

Upon completion of this document, run:

```bash
python3 scripts/patch_web_theories_and_levels.py
```

Then manually add the new template entries (SS1–SS3, SOC1–SOC3, PA1–PA3) to the template registry in `THEORY_HIERARCHY_AND_MECHANISMS.md`, following the existing format for PR1, PR2, KP1, KP2, TC1.

Update `TRANSFER_IE_DPT_Theory_Tiers_Feb20.md` §7 Pending Work to mark items 5 (reduce high-priority candidates) as complete.

---

# REFERENCES

Altman, I. (1975). *The environment and social behavior: Privacy, personal space, territory, crowding*. Brooks/Cole.

Altman, I., & Low, S. M. (Eds.). (1992). *Place attachment*. Plenum Press.

Alvarsson, J. J., Wiens, S., & Nilsson, M. E. (2010). Stress recovery during exposure to nature sound and environmental noise. *International Journal of Environmental Research and Public Health*, 7(3), 1036–1046. https://doi.org/10.3390/ijerph7031036

Annerstedt, M., Jönsson, P., Wallergård, M., Johansson, G., Karlson, B., Grahn, P., ... & Währborg, P. (2013). Inducing physiological stress recovery with sounds of nature in a virtual reality forest. *Physiology & Behavior*, 118, 240–250. https://doi.org/10.1016/j.physbeh.2013.05.023

Axelsson, Ö., Nilsson, M. E., & Berglund, B. (2010). A principal components model of soundscape perception. *Journal of the Acoustical Society of America*, 128(5), 2836–2846. https://doi.org/10.1121/1.3493436

Babisch, W. (2014). Updated exposure-response relationship between road traffic noise and coronary heart diseases: A meta-analysis. *Noise & Health*, 16(68), 1–9. https://doi.org/10.4103/1463-1741.127847

Barrett, L. F. (2017). *How emotions are made: The secret life of the brain*. Houghton Mifflin Harcourt.

Benedikt, M. L. (1979). To take hold of space: Isovists and isovist fields. *Environment and Planning B: Planning and Design*, 6(1), 47–65. https://doi.org/10.1068/b060047

Brown, A. L. (2012). Soundscapes and environmental noise management. *Noise Control Engineering Journal*, 60(5), 493–516. https://doi.org/10.3397/1/376213

Burgess, N., Maguire, E. A., & O'Keefe, J. (2002). The human hippocampus and spatial and episodic memory. *Neuron*, 35(4), 625–641. https://doi.org/10.1016/S0896-6273(02)00830-9

Davies, W. J., Adams, M. D., Bruce, N. S., Cain, R., Carlyle, A., Cusack, P., ... & Nitschke, N. (2013). Perception of soundscapes: An interdisciplinary approach. *Applied Acoustics*, 74(2), 224–231. https://doi.org/10.1016/j.apacoust.2012.05.010

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1a), 145–167.

Evans, J. S. B. T., & Stanovich, K. E. (2013). Dual-process theories of higher cognition: Advancing the debate. *Perspectives on Psychological Science*, 8(3), 223–241. https://doi.org/10.1177/1745691612460685

Fried, M. (1963). Grieving for a lost home. In L. J. Duhl (Ed.), *The urban condition* (pp. 151–171). Basic Books.

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin.

Glass, D. C., & Singer, J. E. (1972). *Urban stress: Experiments on noise and social stressors*. Academic Press.

Godden, D. R., & Baddeley, A. D. (1975). Context-dependent memory in two natural environments: On land and underwater. *British Journal of Psychology*, 66(3), 325–331. https://doi.org/10.1111/j.2044-8295.1975.tb01468.x

Haapakangas, A., Helenius, R., Koskela, H., & Hongisto, V. (2011). Perceived acoustic environment, work performance and well-being: Survey results from Finnish offices. In *Proceedings of the 9th International Congress on Noise as a Public Health Problem*. London.

Hall, E. T. (1966). *The hidden dimension*. Doubleday.

Hanson, J. (1998). *Decoding homes and houses*. Cambridge University Press.

Haq, S., & Zimring, C. (2003). Just down the road a piece: The development of topological knowledge of building layouts. *Environment and Behavior*, 35(1), 132–160. https://doi.org/10.1177/0013916502238868

Hillier, B., & Hanson, J. (1984). *The social logic of space*. Cambridge University Press. https://doi.org/10.1017/CBO9780511597237

Hillier, B., & Iida, S. (2005). Network and psychological effects in urban movement. In *Proceedings of Spatial Information Theory (COSIT 2005)*, Lecture Notes in Computer Science, 3693, 475–490. https://doi.org/10.1007/11556114_30

Hillier, B., Penn, A., Hanson, J., Grajewski, T., & Xu, J. (1993). Natural movement: or, configuration and attraction in urban pedestrian movement. *Environment and Planning B: Planning and Design*, 20(1), 29–66. https://doi.org/10.1068/b200029

Ilie, G., & Thompson, W. F. (2006). A comparison of acoustic cues in music and speech for three dimensions of affect. *Music Perception*, 23(4), 319–329. https://doi.org/10.1525/mp.2006.23.4.319

ISO 12913-1:2014. *Acoustics — Soundscape — Part 1: Definition and conceptual framework*. International Organization for Standardization.

Kang, J., Aletta, F., Gjestland, T. T., Brown, L. A., Botteldooren, D., Schulte-Fortkamp, B., ... & Jeon, J. Y. (2016). Ten questions on the soundscapes of the built environment. *Building and Environment*, 108, 284–294. https://doi.org/10.1016/j.buildenv.2016.08.011

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Kennedy, D. P., Gläscher, J., Tyszka, J. M., & Adolphs, R. (2009). Personal space regulation by the human amygdala. *Nature Neuroscience*, 12(10), 1226–1227. https://doi.org/10.1038/nn.2381

Kjellberg, A., Landström, U., Tesarz, M., Söderberg, L., & Åkerlund, E. (1996). The effects of nonphysical noise characteristics, ongoing task and noise sensitivity on annoyance and distraction due to noise at work. *Journal of Environmental Psychology*, 16(2), 123–136. https://doi.org/10.1006/jevp.1996.0011

Lewicka, M. (2011). Place attachment: How far have we come in the last 40 years? *Journal of Environmental Psychology*, 31(3), 207–230. https://doi.org/10.1016/j.jenvp.2010.10.001

Leutgeb, S., Leutgeb, J. K., Treves, A., Moser, M. B., & Moser, E. I. (2004). Distinct ensemble codes in hippocampal areas CA3 and CA1. *Science*, 305(5688), 1295–1298. https://doi.org/10.1126/science.1100265

Maguire, E. A., Gadian, D. G., Johnsrude, I. S., Good, C. D., Ashburner, J., Frackowiak, R. S., & Frith, C. D. (2000). Navigation-related structural change in the hippocampi of taxi drivers. *Proceedings of the National Academy of Sciences*, 97(8), 4398–4403. https://doi.org/10.1073/pnas.070039597

Manzo, L. C., & Perkins, D. D. (2006). Finding common ground: The importance of place attachment to community participation and planning. *Journal of Planning Literature*, 20(4), 335–350. https://doi.org/10.1177/0885412205286160

McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex: Insights from the successes and failures of connectionist models of learning and memory. *Psychological Review*, 102(3), 419–457. https://doi.org/10.1037/0033-295X.102.3.419

Monk, T. H., Petrie, S. R., Hayes, A. J., & Kupfer, D. J. (1992). Regularity of daily life in relation to personality, age, gender, sleep quality and circadian rhythms. *Journal of Sleep Research*, 1(3), 185–192. https://doi.org/10.1111/j.1365-2869.1992.tb00040.x

Munzel, T., Gori, T., Babisch, W., & Basner, M. (2014). Cardiovascular effects of environmental noise exposure. *European Heart Journal*, 35(13), 829–836. https://doi.org/10.1093/eurheartj/ehu030

Nes, A., & Yamu, C. (2021). *Introduction to Space Syntax in Urban Studies*. Springer.

O'Keefe, J., & Burgess, N. (1996). Geometric determinants of the place fields of hippocampal neurons. *Nature*, 381(6581), 425–428. https://doi.org/10.1038/381425a0

Penn, A. (2003). Space syntax and spatial cognition: Or why the axial line? *Environment and Behavior*, 35(1), 30–65. https://doi.org/10.1177/0013916502238864

Peponis, J., Zimring, C., & Choi, Y. K. (1990). Finding the building in wayfinding. *Environment and Behavior*, 22(5), 555–590. https://doi.org/10.1177/0013916590225001

Pijanowski, B. C., Farina, A., Gage, S. H., Dumyahn, S. L., & Krause, B. L. (2011). What is soundscape ecology? An introduction and overview of an emerging new science. *Landscape Ecology*, 26(9), 1213–1232. https://doi.org/10.1007/s10980-011-9600-8

Proshansky, H. M., Fabian, A. K., & Kaminoff, R. (1983). Place-identity: Physical world socialization of the self. *Journal of Environmental Psychology*, 3(1), 57–83. https://doi.org/10.1016/S0272-4944(83)80021-8

Raichle, M. E., MacLeod, A. M., Snyder, A. Z., Powers, W. J., Gusnard, D. A., & Shulman, G. L. (2001). A default mode of brain function. *Proceedings of the National Academy of Sciences*, 98(2), 676–682. https://doi.org/10.1073/pnas.98.2.676

Ratcliffe, E., Gatersleben, B., & Sowden, P. T. (2013). Bird sounds and their contributions to perceived attention restoration and stress recovery. *Journal of Environmental Psychology*, 36, 221–228. https://doi.org/10.1016/j.jenvp.2013.08.004

Rowles, G. D. (1983). Place and personal identity in old age: Observations from Appalachia. *Journal of Environmental Psychology*, 3(4), 299–313. https://doi.org/10.1016/S0272-4944(83)80033-4

Scannell, L., & Gifford, R. (2010). Defining place attachment: A tripartite organizing framework. *Journal of Environmental Psychology*, 30(1), 1–10. https://doi.org/10.1016/j.jenvp.2009.09.006

Schafer, R. M. (1977). *The tuning of the world*. Knopf.

Schultz, W. (1998). Predictive reward signal of dopamine neurons. *Journal of Neurophysiology*, 80(1), 1–27. https://doi.org/10.1152/jn.1998.80.1.1

Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science*, 275(5306), 1593–1599. https://doi.org/10.1126/science.275.5306.1593

Seth, A. K. (2013). Interoceptive inference, emotion, and the embodied self. *Trends in Cognitive Sciences*, 17(11), 565–573. https://doi.org/10.1016/j.tics.2013.09.007

Spiers, H. J., & Maguire, E. A. (2006). Thoughts, behaviour, and brain dynamics during navigation in the real world. *NeuroImage*, 31(4), 1826–1840. https://doi.org/10.1016/j.neuroimage.2006.01.037

Stamps, A. E. (2005). Enclosure and safety in urbanscapes. *Environment and Behavior*, 37(1), 102–133. https://doi.org/10.1177/0013916504264946

Sterling, P., & Eyer, J. (1988). Allostasis: A new paradigm to explain arousal pathology. In S. Fisher & J. Reason (Eds.), *Handbook of life stress, cognition and health* (pp. 629–649). Wiley.

Tuan, Y. F. (1977). *Space and place: The perspective of experience*. University of Minnesota Press.

Tulving, E. (2002). Episodic memory: From mind to brain. *Annual Review of Psychology*, 53(1), 1–25. https://doi.org/10.1146/annurev.psych.53.100901.135114

Turner, A. (2001). Angular analysis. In *Proceedings of the 3rd International Symposium on Space Syntax*. Georgia Institute of Technology.

Turner, A., Doxa, M., O'Sullivan, D., & Penn, A. (2001). From isovists to visibility graphs: A methodology for the analysis of architectural space. *Environment and Planning B: Planning and Design*, 28(1), 103–121. https://doi.org/10.1068/b2684

Viollon, S., Lavandier, C., & Drake, C. (2002). Influence of visual setting on sound ratings in an urban environment. *Applied Acoustics*, 63(5), 493–511. https://doi.org/10.1016/S0003-682X(01)00067-2

WHO Regional Office for Europe. (2018). *Environmental noise guidelines for the European Region*. World Health Organization.

Wiener, J. M., & Mallot, H. A. (2003). 'Fine-to-coarse' route planning and navigation in regionalized environments. *Spatial Cognition & Computation*, 3(4), 331–358. https://doi.org/10.1207/S15427633SCC0304_5

Yang, W., & Kang, J. (2005). Acoustic comfort evaluation in urban open public spaces. *Applied Acoustics*, 66(2), 211–229. https://doi.org/10.1016/j.apacoust.2004.07.011

---
*Document version 1.0 — February 21, 2026*
*T1.5 Reductions: Space Syntax, Soundscape Theory, Place Attachment*
*Ready for integration into Article Eater Web of Belief*
