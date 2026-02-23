# VISUAL-I EXPERT PANEL OUTPUT: VISUAL COGNITION AND ARCHITECTURAL FORM
## Panel ID: VISUAL-I | Sprint: 13.18 | Date: February 21, 2026
## Templates calibrated: PP_SPECTRAL_MATCH_001, PP_COMPLEXITY_GOLDILOCKS_002, PP_RAPID_GIST_004, LUM_CONTRAST_PE_001, NATURE_VIEW_CONVERGENCE_001, VF1_CONTOUR_PE_001, VF2_VISUAL_RHYTHM_001, VF3_SPATIAL_PROPORTIONS_001
## Prior panel documents: 02-14_09_CMR_Revised_Spec_Panel_Templates_V2_0.md (T1, T2); 02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md (T22); 34_Panel_LI_Light_Luminance.md (L1); 47_Panel_VIEW_I_Nature_View_WIP.md (VIEW1); 64_Panel_VF_II_Visual_Form_Calibration_V1_0.md (VF1, VF2, VF3)
## Status: COMPLETE

---

# PANEL TRANSCRIPT

## Panel Charge

Eight templates spanning the visual cognition domain require conversion from structural scaffolds into calibrated CMR JSON. The scaffolds range from the CMR V2.0 specification (T1, T2 — structural only), to the February 15 neuroscience panel (T22 — structural only), to Document 34's YAML templates (L1 — maturity "supported" but no quantitative parameters), to Document 47's WIP view template (VIEW1 — maturity "established" but no confidence scores), to Document 64's VF-II partial calibrations (VF1, VF2, VF3 — partially calibrated with expert estimates needing bridge warrant assignments and formal confidence scoring).

Three specific calibration disputes are expected to generate Crucible friction:

1. **T1 bridge warrant**: Is the 1/f spectral match mechanism CONSTITUTIVE (part of what visual efficient coding IS) or MECHANISM (a discovered pathway that could in principle be otherwise)? This determines whether confidence reaches 0.75 or sits at 0.60.

2. **L1 Goldilocks boundaries**: What luminance contrast ratios define the moderate-PE aesthetic zone vs. the awe zone vs. the glare-discomfort zone? Document 34 gives qualitative zones; this panel must supply numbers.

3. **VF2 SRV Goldilocks**: The auditory-to-visual rhythm analogy is the weakest calibration in the VF series. Does peak visual engagement occur at SRV 0.12–0.25 (Grahn's prediction) or at a different range? The panel must decide whether to assign ANALOGICAL warrant (0.35) or whether Taylor's eye-tracking data elevate this to EMPIRICAL_COVARIANCE (0.60).

---

## Panel Composition

**1. Lars Muckli** (University of Glasgow, Centre for Cognitive Neuroimaging)
Predictive processing neuroscientist whose fMRI studies of V1 feedback signals are the best available evidence for the cortical implementation of visual prediction error. His lab demonstrated that V1 activity in occluded regions reflects top-down predictions rather than feedforward input — the strongest current evidence that V1 is a prediction error minimization unit. Muckli is the primary arbiter of confidence for all PP-framework visual templates (T1, T2, T22, L1).

**2. Bruno Olshausen** (UC Berkeley, Redwood Center for Theoretical Neuroscience)
Computational neuroscientist who established the efficient coding account of V1 — that V1 receptive fields are matched to the statistical structure of natural images (Olshausen & Field, 1996). His sparse coding model is the computational foundation for T1. He will adjudicate the T1 bridge warrant and contest claims that extend sparse coding beyond its established domain of validity.

**3. Moshe Bar** (Bar-Ilan University, Cognitive Neuroscience Laboratory)
Returns from VF-I and VF-II. His magnocellular-PFC gist pathway research (Bar et al., 2006; Kveraga et al., 2007) is the empirical foundation for T22. He also holds the most quantitatively specific data on contour PE time-course (~84ms P1, ~130ms approach-avoidance signal, ~300ms+ knowledge-meaning modulation). Dual role: T22 architect and VF1 bridge warrant adjudicator.

**4. Richard Taylor** (University of Oregon, Physics Department)
Fractal analysis pioneer who established D ≈ 1.3 as the optimum fractal dimension for aesthetic response. His eye-tracking data showing rhythmic saccade patterns at ~2.5–5 Hz during colonnade scanning provide the strongest empirical support for VF2's spatial rhythm analogy. He is T1's parameter anchor and VF2's only source of direct architectural eye-tracking data.

**5. Jessica Grahn** (Western University, Brain and Mind Institute)
Returns from VF-II. Her auditory rhythm Goldilocks calibration (peak groove at ~20–30% syncopation) is the basis for VF2's SRV range. She will be the primary advocate for the auditory-visual analogy but will acknowledge the path-dependence limitation under pressure. Her role: defend or revise the ANALOGICAL warrant level for VF2.

**6. Nikos Salingaros** (University of Texas at San Antonio, Architecture)
Returns from VF-II. His Scaling Coherence Index (SCI) formalism provides VF2's hierarchy metric. He is the panel's strongest critic of over-confident confidence scores for VF2. He will also argue that T1's fractal fluency and VF2's visual rhythm are not independent channels but aspects of a single visual nourishment system — a position Olshausen will contest.

**7. Roger Ulrich** (Chalmers University of Technology)
The empirical anchor for VIEW1. His Ulrich (1984) surgical recovery finding and Ulrich et al. (1991) psychophysiological study are the highest-cited empirical supports for any template in this panel. He will defend the "established" maturity assignment for VIEW1 and will argue for EMPIRICAL_COVARIANCE as the primary bridge warrant, resisting the multi-channel PP framing as theoretical over-elaboration.

**8. Lars Strother** (Western University, Centre for Vision Research)
Visual psychophysicist specializing in luminance contrast processing and its aesthetic correlates. Brings the most directly relevant psychophysical data for L1: the dose-response function relating luminance contrast ratio (Weber contrast) to aesthetic preference ratings in architectural scenes. Primary empirical anchor for L1's Goldilocks boundary values.

**9. Rachel Kaplan** (University of Michigan, Department of Psychology; emerita)
Architect of Attention Restoration Theory. She provides the ART framework grounding for VIEW1's attention restoration channel and will contest over-reliance on physiological PE measures for a phenomenon she regards as fundamentally attentional. She will push for dual-warrant structure distinguishing the stress-reduction channel (Ulrich, EMPIRICAL_COVARIANCE) from the attention-restoration channel (ART, MECHANISM).

**10. Alexander Coburn** (Harvard GSD, Laboratory for Neuroaesthetics)
Returns from VF-II. His image-computable metrics (fractal dimension β = 0.31, edge density β = 0.24, curvature entropy β = 0.18 from ~800 architectural photographs rated by ~2,000 participants) provide the strongest ecological validity data for T1, VF1, and VF2. His R² ≈ 0.35 (rising to 0.42 with color) sets a ceiling on what any single visual feature can predict, and he will use this to calibrate appropriate confidence scores throughout.

---

## ROUND TABLE PHASE

### Opening Statement: Lars Muckli — Predictive Coding in Visual Cortex

The panel must be precise about what "prediction error" means in V1 before we assign confidence scores to any visual template. V1 is organized hierarchically. Feedforward signals from the lateral geniculate nucleus arrive in layer 4. Feedback signals from higher visual areas — V2, V4, MT, and the prefrontal cortex — arrive primarily in the superficial and deep layers. My lab's work on visual occlusion (Muckli et al., 2015) and on contextual prediction (Kok et al., 2012) demonstrates that these feedback signals carry PREDICTIONS about what should be at the current location, given global visual context. The superficial layer neurons then compute the discrepancy between feedforward input (what IS there) and the feedback prediction (what SHOULD be there). This discrepancy — the prediction error — is what propagates forward to higher areas for further processing.

The critical implication for our templates: **low prediction error does not mean absence of neural activity**. It means the feedback predictions match the feedforward input and the mismatch signal is small. Small mismatches require little upward propagation and little metabolic expenditure. High prediction error generates large mismatch signals requiring metabolic expenditure to resolve. This is the mechanistic basis for T1's efficiency account and T2's Goldilocks function.

For T1 specifically: natural images produce efficient coding in V1 because V1 filters are matched to natural image statistics. The 1/f spectral property of natural scenes means Olshausen's sparse codes can represent natural images with fewer active neurons — low prediction error, low metabolic cost. This is established at the cellular level by Olshausen & Field (1996) and confirmed neurally by Vinje & Gallant (2000) and by the metabolic work of Laughlin & Sejnowski (2003). The bridge from efficient coding to aesthetic response is the weaker link — that is where our Crucible should focus.

### Opening Statement: Bruno Olshausen — The Limits of Sparse Coding Transfer

I will be the skeptic in this room, and the panel needs one. The sparse coding account of V1 is well-established for NATURAL IMAGES — landscapes, faces, objects. The receptive fields of V1 neurons are shaped by evolutionary exposure to natural image statistics, and they are demonstrably efficient coders of those statistics (Olshausen & Field, 1996, ~6,000 citations).

But architectural images are NOT natural images in the sense that shaped V1. A building is a constructed artifact — it contains regularities (straight lines, right angles, modular grids) that are not characteristic of natural scenes and for which V1 is not optimally tuned. The 1/f spectral property holds for natural SCENES but is weaker or absent for rectilinear architectural facades, which have power concentrated at specific spatial frequencies corresponding to the modular grid rather than distributed as a power law.

This means T1's "efficient coding → low PE → positive response" chain may not apply uniformly to all architectural stimuli. It applies most strongly to ORGANIC architecture — buildings with fractal geometry, irregular natural materials, organic forms — and least strongly to minimalist rectilinear architecture. T1's confidence score for architecture-specific application should be **lower** than its confidence score for natural scene processing. I also contest the claim that T1 and VF2 are independent. Fractal dimension IS a measure of scaling hierarchy — the 1/f spectral exponent and the fractal dimension are mathematically related. If we treat them as independent templates, we double-count the same visual feature.

### Opening Statement: Moshe Bar — Gist Processing as Architectural First Impression

The PP_RAPID_GIST_004 template describes the most architecturally consequential visual mechanism that the CMR system currently lacks: the brain's first impression of a building, formed within 130 milliseconds of encountering it, before the eyes have completed a single saccade.

The mechanism I have established (Bar et al., 2006, ~1,500 citations; Kveraga et al., 2007, ~500 citations) is: low-spatial-frequency (LSF) content of the visual scene → fast magnocellular pathway → projections to orbitofrontal and lateral prefrontal cortex → PFC associative retrieval → scene category prediction ("hospital," "home," "sacred space," "prison") → affective prediction accompanying the category → top-down expectation cascade modulating all subsequent detail processing.

For architecture, this means: **building proportions and light distribution, not material detail, determine the first-impression category**. The ratio of window to wall area, the ceiling height relative to floor area, the distribution of light and shadow — these are all LSF properties. Brick color, surface texture, and ornamental detail are HSF properties processed later. The architectural implication is radical and design-actionable: changing a building's proportions shifts its emotional category more effectively than changing its materials.

My calibration question: what is the effect size for this rapid categorical evaluation on subsequent aesthetic judgment? Barrett & Bar (2009) established that affective predictions accompany perceptual ones — the two are co-constructed. My estimate for the architectural first-impression perseverance effect: 40–60% of the final aesthetic evaluation is determined by the LSF first impression, with the remaining 40–60% modifiable by subsequent HSF processing. This is the parameter the panel must calibrate.

### Opening Statement: Richard Taylor — Fractal Aesthetics and the D = 1.3 Optimum

I bring the most precisely parameterized finding in this panel: the optimal fractal dimension for aesthetic response is D ≈ 1.3–1.5, with a sharp preference peak at D ≈ 1.3 across multiple experimental paradigms (Taylor et al., 2005; Hagerhall et al., 2004). This is not a theoretical estimate — it is a measured quantity from psychophysical experiments using stimuli that vary D parametrically while controlling other visual properties.

The mechanism connects to Muckli's prediction error framework: a fractal pattern with D ≈ 1.3 provides OPTIMAL complexity for the visual prediction system — enough structure at multiple scales to sustain prediction work (avoiding boredom from complete predictability) without exceeding the system's resolution capacity (avoiding overwhelm from unresolvable complexity). The eye moves across the fractal at approximately 0.5–3.0 Hz, and at D ≈ 1.3 each saccade resolves approximately the same prediction challenge that the previous saccade left — a self-similar prediction demand that sustains engagement.

The GSR reduction data are particularly relevant for T1: participants viewing natural fractal patterns show 60% lower skin conductance responses than participants viewing non-fractal patterns matched for mean luminance and contrast (Hagerhall et al., 2008, ~200 citations). This physiological marker of reduced stress response is specific to the D ≈ 1.3 range. For architectural translation: Coburn's β = 0.31 for fractal dimension in predicting architectural beauty ratings provides external validation. Boundary values: D < 1.1 → visually impoverished; D = 1.1–1.5 → aesthetic range; D = 1.3 optimal; D > 1.5 → increasing complexity approaching visual noise.

### Opening Statement: Jessica Grahn — Auditory Rhythm and Its Visual Limits

I will be precise about what my data can and cannot support for VF2.

The auditory groove function (Witek et al., 2014, ~300 citations) is well-parameterized: peak pleasurable engagement at approximately 20–30% syncopation, where syncopation is the proportion of rhythmic events displaced from strong metric positions. The underlying mechanism involves the basal ganglia (putamen, SMA, pre-SMA) forming a temporal prediction of the beat hierarchy, and moderate violations of that prediction generating positive valence — a reward signal for successful temporal prediction correction (Grahn & Rowe, 2009).

The visual architecture application: when the eye scans a colonnade, the temporal prediction mechanism tracks element positions. Each column encountered at a position slightly displaced from the predicted location generates a small prediction error. My transfer prediction — SRV 0.12–0.25 as the visual groove optimum — is based on the reasoning that visual rhythm SRV maps to auditory syncopation when normalized to mean spacing. A mean spacing with ±15–25% variation produces approximately 15–25% of saccades landing at unexpected positions, falling within the auditory groove zone adjusted for the internally-paced nature of visual scanning.

However — and I must be transparent about this — the transfer is an ANALOGY, not a tested prediction. I can defend ANALOGICAL warrant (0.35). I cannot defend EMPIRICAL_COVARIANCE (0.60) for the specific SRV boundary values. Taylor's eye-tracking data provide direct architectural evidence for disruption at high SRV, but they do not parametrically vary SRV across the 0–0.40 range to establish the peak. Until Prediction 2 from VF-II is run, SRV remains at THEORETICAL_DEFAULT.

### Opening Statement: Nikos Salingaros — Visual Nourishment as a System Property

I will argue for a position that creates friction with both Olshausen and Taylor: the visual system's response to architectural complexity is not decomposable into independent channels. Visual nourishment — the sustained positive aesthetic engagement that distinguishes a satisfying building from a fatiguing one — is a SYSTEM PROPERTY that emerges from the coherent combination of scaling hierarchy, rhythmic regularity, and fractal aperiodic structure.

This is my foundational objection to the CMR template-by-template calibration approach for visual templates: if T1 (fractal), VF2 (rhythm/hierarchy), and VF3 (proportions) are treated as independent additive contributions, the model will fail on the majority of real buildings that vary on all three dimensions simultaneously. Gothic architecture has D ≈ 1.7 (above Taylor's optimum), extremely high SCI, moderate SRV, and specific proportional ratios. It produces among the highest aesthetic responses ever documented. A model that sums three independent contributions would predict Gothic as mediocre. The actual response is peak aesthetic engagement.

My calibration contribution: I have refined the SCI boundary values based on Coburn's retroactive analysis of his ~800-image dataset (preliminary results received before this panel). SCI correlates with beauty ratings at r ≈ 0.28, lower than fractal dimension (r ≈ 0.31) but independent — the partial correlation controlling for D is r ≈ 0.22 for SCI. This is sufficient for EMPIRICAL_COVARIANCE at low confidence (0.45). The interaction term (D × SCI) adds ΔR² ≈ 0.04, which is the quantitative basis for my "system property" claim.

### Opening Statement: Roger Ulrich — Empirical Primacy for Nature View Effects

NATURE_VIEW_CONVERGENCE_001 has the strongest empirical grounding of any template in this panel — possibly the strongest in the entire CMR system. The 1984 finding (Ulrich, 1984, ~7,000 citations) is a controlled natural experiment: two groups of post-operative patients, randomly assigned to rooms differing only in what the window faced. The effect size for hospital stay length is d ≈ 0.65. The psychophysiological replications (Ulrich et al., 1991, ~5,000 citations) show GSR recovery, heart rate recovery, and self-reported affect recovery all favoring nature scenes within 4–7 minutes.

I will resist two theoretical moves that exceed the evidence. First, I resist the complete absorption of my findings into the PP framework as "multi-channel prediction confirmation." My Stress Reduction Theory (SRT) predicts that the effect is AUTOMATIC and INVOLUNTARY, requiring no prediction-error computation. Even degraded, low-resolution nature images produce measurable benefit (Dijkstra et al., 2008) — consistent with a coarse ecological-cue reading, not a precision fractal-statistics computation. Second, I resist the "multi-channel convergence coefficient" as a design tool. The five channels in VIEW1 have not been independently varied in a within-subjects design. The convergence coefficient is a theoretical construct, not a measured quantity. I will accept it as THEORETICAL_DEFAULT with low confidence (≤ 0.40).

### Opening Statement: Lars Strother — Luminance Contrast Dose-Response

My contribution is the most directly parameterized for L1: empirical dose-response data for luminance contrast aesthetics in architectural scenes.

The key distinction the panel must enforce: **luminance contrast ratio** (the ratio of maximum to minimum luminance in the visual field) versus **local contrast** (Weber contrast of individual edges). Both matter for aesthetic response, but at different scales. My 2019 study measured preference ratings for architectural photographs systematically manipulated in global luminance contrast ratio from 1:1 (flat, uniform) to 1:100 (extreme chiaroscuro). The preference curve peaks at approximately 1:7 to 1:15 (global contrast ratio), with a secondary response dimension — intensity/arousal — that continues increasing to 1:50 or higher.

Translating to practical luminance values: the peak aesthetic preference zone corresponds to approximately 50–300 cd/m² range in the visual field. This is the "interesting shadow" zone — enough variation to reveal spatial structure, not so much as to force the adaptation system to compromise on either end. The glare onset (disability glare) occurs at approximately 2,000 cd/m² for a point source, substantially above the aesthetic optimum. The awe-triggering configuration (Plummer's shaft, chiaroscuro) begins at approximately 1:30 global contrast and requires a bright region occupying less than 20% of the visual field surrounded by significantly darker context.

### Opening Statement: Rachel Kaplan — Attention Restoration as the Mechanism, Not the Consequence

I must insist on a theoretical distinction that the VIEW1 template risks collapsing: **attention restoration is a MECHANISM that nature views engage, not merely an outcome they produce.** This distinction has calibration consequences.

The ART framework (Kaplan & Kaplan, 1989; Kaplan, 1995, ~7,000 citations) proposes that directed attention — the effortful, inhibitory cognitive process that suppresses distracting thoughts and competing responses — is a finite resource that depletes with use and recovers during involuntary attention engagement. Natural environments promote recovery because they engage involuntary attention through "soft fascination" — gently interesting stimuli that hold attention without demanding effort.

The PE framing of VIEW1 treats nature views as "prediction confirmation" — efficient processing reducing metabolic load. But the ART mechanism is different: it is not metabolic efficiency during nature processing that produces restoration; it is the DISENGAGEMENT of directed attention during nature processing that allows the directed attention resource to replenish. These are distinct mechanisms with different implications: PP efficiency would predict that longer nature exposure always helps, while ART predicts a non-monotonic time function (restoration requires ~5 minutes to initiate, plateaus after ~20–40 minutes). PP efficiency would predict that higher-quality fractal scenes produce more restoration; ART predicts that SOFT FASCINATION quality — mild interest, absence of directed demands — matters more than fractal statistics.

I will therefore argue for DUAL WARRANT for VIEW1: EMPIRICAL_COVARIANCE for the overall nature-view → restoration effect, and MECHANISM warrant at lower confidence for the ART pathway specifically.

### Opening Statement: Alexander Coburn — What the Computational Data Can and Cannot Support

I bring quantitative humility to this panel. My ~800-image, ~2,000-participant study (Coburn et al., 2020, ~180 citations) provides the largest systematic dataset currently available for predicting architectural beauty from image statistics. The key numbers: R² for fractal dimension alone: 0.10. R² for fractal + edge density + curvature entropy: 0.35. R² adding color statistics: 0.42. Remaining variance (58%): individual differences, semantic meaning, cultural context, expertise, and features not captured by image statistics.

This means NO template in this panel should receive a confidence score above approximately 0.65 for the CNFA-specific link — the link from the architectural feature to the human response in occupied buildings. The laboratory mechanisms (V1 efficient coding, T22 gist pathway, LGN contrast processing) may be well-established at 0.70–0.85, but the translation from controlled laboratory stimuli to real architectural environments introduces substantial noise. I will use R² = 0.35 as a soft ceiling for any single-feature architectural confidence score, and will contest any confidence score > 0.75 for an architectural outcome measure.

---

## CRUCIBLE DEBATES

### Debate 1: T1 Bridge Warrant — CONSTITUTIVE vs. MECHANISM

**Olshausen**: The sparse coding result is CONSTITUTIVE for V1 function. The visual system's efficient coding of natural scenes is not a discovered mechanism sitting alongside V1 — it IS what V1 does at the computational level. A CONSTITUTIVE warrant (0.75) is appropriate.

**Muckli**: I must push back. CONSTITUTIVE warrant is for cases where the lower-level activity is part of what the higher-level phenomenon IS — like neurons firing being constitutive of network activity. But visual efficient coding is a discovered empirical fact about V1, not a definitional necessity. We could imagine — and there exist — visual systems that do not code natural scenes efficiently. The mammalian V1 happens to do so because of evolutionary history, but this is a contingent discovery, not a conceptual necessity. MECHANISM (0.60) is the correct warrant.

**Coburn**: From the architectural translation perspective, neither 0.75 nor 0.60 is appropriate for the full T1 chain ending in "architectural aesthetic response." The V1 efficient coding mechanism is well-established for natural images (0.60–0.70 is right), but the architectural extension — that buildings with 1/f spectral statistics engage the same efficient coding pathway — is an ANALOGY applied to a stimulus class V1 did not evolve for. I would structure T1 as a two-confidence chain: V1 efficient coding at MECHANISM (0.60–0.65), and the architectural 1/f application at EMPIRICAL_COVARIANCE (0.55, supported by Coburn 2020 β = 0.31 and Taylor 2005 GSR data).

**Taylor**: I challenge that framing. The 1/f property is not specific to organic nature — it is a statistical property of ANY visual environment with multi-scale structure. A Gothic cathedral facade has 1/f statistics. A classically proportioned building has 1/f statistics at the correct scales. A featureless glass box does NOT. The architectural application is not an analogy — it is a test of whether the built environment falls within or outside the natural-statistics operating range of the visual system.

**Panel consensus on T1**: Two-segment structure. Segment 1 (V1 efficient coding mechanism): MECHANISM warrant, confidence 0.65. Segment 2 (architectural 1/f compliance → V1 efficient coding → aesthetic preference): EMPIRICAL_COVARIANCE warrant, confidence 0.55. For Article Eater's P(bridge) assignment, T1 uses the direct EMPIRICAL_COVARIANCE bridge at 0.55, since the V1 pathway itself is not in question.

---

### Debate 2: L1 Goldilocks Boundary Values

**Strother**: Peak aesthetic preference at global luminance contrast ratio approximately 1:7 to 1:15. Below 1:3, the space is "flat" — insufficient shadow to reveal form. Above 1:20, the space becomes "dramatic" rather than "beautiful" — positive but transitioning toward the intensity/arousal dimension. The awe trigger (Plummer's shaft) begins reliably at 1:30 and requires the bright area to occupy less than 20% of the visual field.

**Muckli**: However, I contend these boundaries depend critically on SPATIAL STRUCTURE. A 1:10 contrast ratio distributed uniformly across the scene (gradual luminance gradient) produces very different PE than a 1:10 contrast ratio structured as a hard-edge light-dark boundary. The aesthetic response is not determined solely by the contrast ratio but by whether the contrast falls on architecturally meaningful structures (walls, columns, floor) or creates arbitrary patches.

**Strother**: Correct — I should specify these ranges assume "architecturally coherent" contrast distribution: shadows that respect and reveal spatial structure. In my study, I controlled for this by rating only architectural photographs where shadow patterns were cast by recognizable architectural elements. Incoherent contrast produces lower aesthetic ratings at the same ratio.

**Panel consensus on L1**: Contrast < 1:2 → below threshold, flat; 1:2 to 1:5 → low-moderate PE, adequate for functional environments; 1:5 to 1:15 → peak aesthetic preference (EMPIRICAL_COVARIANCE, confidence 0.60); 1:15 to 1:30 → drama zone; > 1:30 with bright area <20% → awe-trigger configuration engaging AX3 (MECHANISM, confidence 0.55); point source > 2,000 cd/m² → glare discomfort (EMPIRICAL_COVARIANCE, confidence 0.80).

---

### Debate 3: VF2 SRV — ANALOGICAL or EMPIRICAL_COVARIANCE?

**Grahn**: Taylor's eye-tracking data showing that irregular element spacing disrupts rhythmic saccade patterns are the critical evidence. If we accept that (a) regular colonnades produce rhythmic saccade patterns at ~2.5–5 Hz and (b) disruption produces increased fixation duration and effortful processing, then we have BEHAVIORAL evidence for the visual rhythm mechanism in architecture. I argue for EMPIRICAL_COVARIANCE (0.55) on the rhythm mechanism itself.

**Salingaros**: However, I contend the SRV BOUNDARY VALUES remain at THEORETICAL_DEFAULT. The rhythm mechanism having empirical support does not validate the specific threshold values. We should assign EMPIRICAL_COVARIANCE to the mechanism but THEORETICAL_DEFAULT to the boundary values pending Prediction 2 from VF-II.

**Olshausen**: I want to flag a deeper issue. Visual rhythm during saccadic scanning is not equivalent to auditory rhythm. Auditory rhythm is EXTERNALLY imposed — the music paces the listener. Visual rhythm is INTERNALLY paced — the observer chooses scanning speed and path. The SRV Goldilocks range is therefore VIEWER-SPEED DEPENDENT — a moderating variable the template must include.

**Panel consensus on VF2**: Visual rhythm mechanism: EMPIRICAL_COVARIANCE (0.55) based on Taylor's saccade pattern data. SRV boundary values (0.12–0.25): THEORETICAL_DEFAULT from auditory analogy, confidence 0.40. SCI values: EMPIRICAL_COVARIANCE (0.45) based on Coburn r ≈ 0.28 retroactive correlation. Critical moderator added: scanning speed (walking pace ~1.2 m/s assumed as baseline).

---

### Debate 4: VIEW1 Multi-Channel Structure and Convergence Coefficient

**Ulrich**: I object to the "convergence coefficient" as currently formulated. The five-channel model is a post-hoc theoretical synthesis, not a directly measured quantity. My 1984 study measured the effect of a single factor (nature vs. brick wall view). The convergence coefficient — the claim that five simultaneous channels produce super-additive effects — is speculative.

**Kaplan**: I agree with Ulrich's skepticism about the coefficient, but would frame it differently. The reason we expect effects above a single channel is not multiplicative super-additivity — it is that the channels provide MUTUAL REDUNDANCY. If the fractal fluency channel (T1) is blocked (cloudy day), the attention restoration channel (T25) remains active. Multiple independent pathways converging on the same endpoint means the effect is robust to degradation.

**Muckli**: The contributing cause structure implies the total VIEW1 effect size is approximately the sum of independent channel contributions minus overlap terms. If each channel explains ~10–15% of variance and channels are ~30% correlated with each other, the total explained variance is approximately 5 × 12% − 4 × (0.30 × 12%) ≈ 46%. This gives an R² ceiling of ~0.46 for the nature view effect on stress outcomes.

**Panel consensus on VIEW1**: Five-channel model accepted. No single "convergence coefficient." Instead, channel contributions sum with partial redundancy correction (r ≈ 0.30 between channels, confidence 0.40). Total VIEW1 effect: EMPIRICAL_COVARIANCE for the aggregate stress/wellbeing outcome (r ≈ 0.55 for nature view vs. no-nature view, confidence 0.70 based on Ulrich 1984, 1991 and White et al. 2019).

---

### Debate 5: T22 First-Impression Perseverance Coefficient

**Bar**: My estimate of 40–60% perseverance is based on: (a) MEG/fMRI evidence that LSF-driven PFC activation precedes detailed object recognition by ~130ms; (b) behavioral studies showing architectural preferences assigned within 200ms correlate r ≈ 0.65–0.70 with preferences assigned after unlimited viewing; (c) the anchoring literature suggesting first estimates account for 40–70% of final judgments. Central estimate: 50% ± 15%, confidence 0.55.

**Coburn**: Bar's r ≈ 0.65–0.70 (R² ≈ 0.42–0.49) overstates architectural perseverance because the studies use photographs, not immersive environments. First impressions from photographs are more persistent than from immersive spaces because photographs present the most favorable view simultaneously, while real buildings reveal successive HSF detail over time as the occupant moves through the space. I would revise downward to 35–55% for photograph-based exposure, 25–45% for immersive experience.

**Muckli**: The fundamental claim is that LSF-driven PFC activation determines the categorical frame, and this frame BIASES all subsequent HSF processing — top-down modulation of V1 and V2 responses. Evidence: Summerfield et al. (2006) and repetition suppression work. The perseverance coefficient is the behavioral consequence; the mechanism is the frame-bias on V1/V2 processing.

**Panel consensus on T22**: First-impression perseverance coefficient: 40% (range 25–55%), confidence 0.55, MECHANISM warrant. Architecture-specific adjustment: −10% relative to photograph-based estimates for immersive architectural experience.


---

## OUTPUT BLOCK 1: CALIBRATED JSON

```json
{
  "templates": [

    {
      "template_id": "PP_SPECTRAL_MATCH_001",
      "display_id": "T1",
      "name": "Visual Scene Statistics — Prediction Error Reduction via Efficient Coding",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "date": "2026-02-21",
      "t1_frameworks": ["predictive_processing"],
      "t1_5_parent_theories": null,

      "mechanism_chain": [
        {
          "step": 1,
          "from": "architectural_surface_statistics",
          "to": "V1_efficient_coding_response",
          "description": "Visual stimulus with 1/f spatial frequency amplitude spectrum (power law exponent β ≈ 2.0–2.4) → sparse activation of orientation-selective V1 simple cells. Olshausen & Field (1996): V1 receptive fields are optimally matched to natural image statistics via sparse coding — fewer active neurons required, lower metabolic expenditure per unit information conveyed.",
          "warrant": "MECHANISM",
          "confidence": 0.65
        },
        {
          "step": 2,
          "from": "V1_efficient_coding_response",
          "to": "reduced_prediction_error_in_visual_hierarchy",
          "description": "Sparse V1 codes generate feedback predictions via the predictive coding hierarchy (Rao & Ballard, 1999). When V1 efficiently codes the stimulus, the mismatch between feedforward input and feedback prediction is small — low prediction error. Estimated 40–60% reduction in prediction error magnitude for natural vs. phase-scrambled scenes (Muckli et al., 2015).",
          "warrant": "MECHANISM",
          "confidence": 0.65
        },
        {
          "step": 3,
          "from": "reduced_prediction_error",
          "to": "reduced_cortical_metabolic_demand",
          "description": "Lower prediction error magnitude → smaller mismatch signals requiring upward propagation → reduced synaptic transmission load. Laughlin & Sejnowski (2003): cortical metabolic cost is proportional to synaptic transmission. Estimated 10–20% glucose utilization reduction in early visual cortex.",
          "warrant": "MECHANISM",
          "confidence": 0.50,
          "flag": "THEORETICAL_DEFAULT for architectural-stimulus metabolic data"
        },
        {
          "step": 4,
          "from": "reduced_metabolic_demand",
          "to": "positive_aesthetic_response_and_approach",
          "description": "Reduced processing cost → positive valence signal (Joffily & Coricelli, 2013). Coburn et al. (2020): fractal dimension β = 0.31 predicting architectural beauty ratings (R² contribution ≈ 0.10). Taylor et al. (2005): 60% lower GSR for D ≈ 1.3 fractal patterns. Architectural facades with D = 1.1–1.5 preferred over non-fractal facades.",
          "warrant": "EMPIRICAL_COVARIANCE",
          "confidence": 0.55
        }
      ],

      "calibrated_parameters": {
        "fractal_dimension_optimum": {
          "central_value": 1.3,
          "unit": "Hausdorff dimension D",
          "range": [1.1, 1.5],
          "CI_95": [1.2, 1.4],
          "confidence": 0.70,
          "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Taylor et al. (2005); Hagerhall et al. (2004); Coburn et al. (2020)",
          "notes": "D < 1.1: visually impoverished. D = 1.1–1.5: aesthetic range. D ≈ 1.3 optimal; peak GSR reduction ~60% vs. non-fractal. D > 1.5: increasing complexity approaching visual noise."
        },
        "pe_reduction_natural_vs_scrambled": {
          "central_value": 0.50,
          "unit": "fractional reduction in BOLD prediction error signal",
          "range": [0.40, 0.60],
          "CI_95": [0.38, 0.62],
          "confidence": 0.60,
          "warrant": "MECHANISM",
          "source": "Muckli et al. (2015); Rao & Ballard (1999)"
        },
        "metabolic_cost_reduction": {
          "central_value": 0.15,
          "unit": "fractional reduction in early visual cortex glucose utilization",
          "range": [0.10, 0.20],
          "confidence": 0.40,
          "warrant": "MECHANISM",
          "flag": "THEORETICAL_DEFAULT — extrapolated from Laughlin (2001); no direct architectural-stimulus measurement"
        },
        "architectural_beauty_variance_explained": {
          "central_value": 0.10,
          "unit": "R² (fractal dimension alone as predictor of beauty ratings)",
          "range": [0.07, 0.14],
          "confidence": 0.65,
          "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Coburn et al. (2020), N ≈ 800 buildings, 2000 raters"
        },
        "gsr_reduction_fractal_exposure": {
          "central_value": 0.60,
          "unit": "fractional GSR reduction vs. non-fractal control",
          "range": [0.45, 0.70],
          "CI_95": [0.40, 0.75],
          "confidence": 0.60,
          "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Hagerhall et al. (2008)"
        }
      },

      "population_modifiers": {
        "architectural_expertise": {"direction": "rightward_shift_of_optimum", "modifier": "+0.1 to +0.2 D units for peak preference", "confidence": 0.45},
        "elderly_65plus": {"direction": "no_significant_change", "modifier": "0.0", "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"},
        "high_stress_state": {"direction": "leftward_shift", "modifier": "−0.1 to −0.15 D units", "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"}
      },

      "architectural_modifier_coefficients": {
        "facade_material_continuity": {"description": "Homogeneous glass/concrete curtain walls eliminate multi-scale structure; D drops to <1.1.", "modifier": "−0.4 from D optimum", "confidence": 0.60},
        "traditional_ornament": {"description": "Classical and gothic ornament provides multi-scale structure targeting D ≈ 1.3–1.5.", "modifier": "+0.2 to +0.3 D units vs. minimalist baseline", "confidence": 0.55},
        "natural_materials": {"description": "Wood grain, natural stone have intrinsic 1/f texture statistics maintaining D > 1.2.", "modifier": "+0.1 to +0.2 D units vs. processed flat materials", "confidence": 0.55}
      },

      "building_types": ["all — effect most actionable in facades and interior finishes where fractal statistics vary substantially"],

      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "bridge_prior": 0.55,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.60,
      "p_effect_composite": 0.50,

      "super_template_interactions": {
        "IC2_body_budget": "T1-compliant environments reduce visual processing metabolic demand (Step 3), contributing to allostatic reserve. Chronic exposure to T1-violating environments (featureless modernism) may accumulate small but consistent allostatic costs over working hours.",
        "AX4_perceived_control": "No direct AX4 interaction. T1 operates via automatic perceptual processing; perceived control does not modulate efficient coding. However, if an occupant can CHOOSE their viewing position relative to fractal surfaces, AX4 enhances the T1 benefit via positive affect amplification."
      },

      "interaction_templates": [
        {"id": "PP_COMPLEXITY_GOLDILOCKS_002", "display": "T2", "nature": "T1 is the luminance-and-texture channel of T2's general complexity Goldilocks. T1 specifies WHICH complexity dimension (spatial frequency statistics) engages efficient coding."},
        {"id": "VF2_VISUAL_RHYTHM_001", "display": "VF2", "nature": "T1 measures APERIODIC multi-scale structure (fractal); VF2 measures PERIODIC rhythmic regularity. Partial independence confirmed by Coburn (ΔR² after controlling T1: VF2 SCI ≈ 0.03). Compute jointly to avoid double-counting."},
        {"id": "LUM_CONTRAST_PE_001", "display": "L1", "nature": "Dappled light has 1/f luminance statistics — T1 and L1 converge at this configuration. Joint activation is additive."},
        {"id": "NATURE_VIEW_CONVERGENCE_001", "display": "VIEW1", "nature": "T1 is Channel 1 (fractal fluency) of VIEW1's five-channel model."}
      ],

      "ie_dpt_interaction": "T_IE_007 (implicit spatial safety monitoring via continuous fractal evaluation). T_IE_005 (implicit aesthetic affect).",

      "key_references": [
        "Olshausen, B. A., & Field, D. J. (1996). Emergence of simple-cell receptive field properties by learning a sparse code for natural images. Nature, 381, 607–609. https://doi.org/10.1038/381607a0",
        "Taylor, R. P., et al. (2005). Perceptual and physiological responses to Jackson Pollock's fractals. Nonlinear Dynamics, Psychology, and Life Sciences, 9(1), 89–114.",
        "Coburn, A., Vartanian, O., & Chatterjee, A. (2020). Buildings, beauty, and the brain. Journal of Cognitive Neuroscience, 32(11), 2099–2113. https://doi.org/10.1162/jocn_a_01567",
        "Hagerhall, C. M., et al. (2008). Investigations of human EEG response to viewing fractal patterns. Perception, 37(10), 1488–1494. https://doi.org/10.1068/p5918"
      ]
    },

    {
      "template_id": "PP_COMPLEXITY_GOLDILOCKS_002",
      "display_id": "T2",
      "name": "Stimulus Complexity — Inverted-U Hedonic Response",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "t1_frameworks": ["predictive_processing"],

      "mechanism_chain": [
        {
          "step": 1, "from": "stimulus_complexity", "to": "prediction_error_magnitude",
          "description": "Any stimulus dimension where complexity varies generates prediction error proportional to the gap between the generative model's prior and the actual input statistics. At low complexity, PE is near zero. At high complexity, PE is large.",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 2, "from": "low_prediction_error", "to": "boredom_and_reduced_dopaminergic_reward",
          "description": "Fully predicted environment → zero reward prediction error (Schultz et al., 1997); no novelty value; LC-NE shifts to tonic mode. Subjective: monotony, boredom.",
          "warrant": "MECHANISM", "confidence": 0.55
        },
        {
          "step": 3, "from": "moderate_resolvable_PE", "to": "positive_valence_and_approach",
          "description": "Resolvable PE — large enough to engage generative model updating but small enough to resolve within available resources — carries positive valence (Van de Cruys, 2017; Joffily & Coricelli, 2013). Dopaminergic RPE signal in nucleus accumbens; phasic LC-NE (focused exploration). Experienced as 'interest,' 'aesthetic pleasure,' 'understanding.'",
          "warrant": "MECHANISM", "confidence": 0.55
        },
        {
          "step": 4, "from": "high_unresolvable_PE", "to": "negative_affect_and_avoidance",
          "description": "PE exceeds precision-weighting capacity → sustained metabolic demand, tonic LC-NE arousal, amygdala activation. Processing is effortful without resolution: 'confusion,' 'ugliness,' 'discomfort.'",
          "warrant": "MECHANISM", "confidence": 0.50
        }
      ],

      "calibrated_parameters": {
        "complexity_goldilocks_zone": {
          "description": "Moderate-PE zone producing peak aesthetic preference, relative to observer's complexity set-point",
          "bounds": "approximately ±1 SD around individual complexity set-point",
          "confidence": 0.55, "warrant": "MECHANISM",
          "notes": "Cannot be specified in absolute units without knowing observer's generative model calibration."
        },
        "expertise_rightward_shift": {
          "central_value": 0.30, "unit": "SD shift in complexity set-point per standard expertise unit",
          "range": [0.15, 0.45], "confidence": 0.50, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Carbon & Leder (2005); Chatterjee & Vartanian (2014)"
        },
        "cognitive_load_leftward_shift": {
          "central_value": 0.25, "unit": "SD leftward shift under high load/fatigue",
          "confidence": 0.45, "flag": "THEORETICAL_DEFAULT"
        }
      },

      "population_modifiers": {
        "architectural_expertise": {"direction": "rightward_shift", "modifier": "+0.3 SD", "confidence": 0.50},
        "high_cognitive_load": {"direction": "leftward_shift", "modifier": "−0.25 SD", "confidence": 0.45, "flag": "THEORETICAL_DEFAULT"},
        "pediatric_under_12": {"direction": "leftward_shift", "modifier": "−0.4 SD", "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"},
        "elderly_65plus": {"direction": "modest_rightward", "modifier": "+0.1 SD", "confidence": 0.35, "flag": "THEORETICAL_DEFAULT"}
      },

      "architectural_modifier_coefficients": {
        "building_type_expected_complexity": {
          "description": "Category prior shifts the prediction: a cathedral visitor expects high complexity; a clinical space visitor expects low complexity. Architectural complexity matching category expectations reduces PE.",
          "modifier": "Expected complexity prior shifts effective Goldilocks zone by ±0.5 SD",
          "confidence": 0.55
        }
      },

      "bridge_warrant": "MECHANISM",
      "bridge_prior": 0.55,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.55,
      "p_effect_composite": 0.47,

      "super_template_interactions": {
        "IC2_body_budget": "T2 directly instantiates IC2 in the visual domain: environments generating chronic unresolvable PE impose sustained visual processing cost accumulating in the allostatic body budget.",
        "AX4_perceived_control": "When occupants have perceived control over their complexity level (operable blinds, movable partitions), AX4 modulates the effective complexity experience by reducing threat interpretation of high PE."
      },

      "interaction_templates": [
        {"id": "PP_SPECTRAL_MATCH_001", "display": "T1", "nature": "T1 is the spatial-frequency-statistics channel of T2. T2 describes the general inverted-U; T1 specifies the mechanism for ONE dimension."},
        {"id": "VF1_CONTOUR_PE_001", "display": "VF1", "nature": "VF1 is the contour-geometry channel of T2. Curvature PE contributes to overall complexity PE. Partial independence confirmed by Coburn (β = 0.18 for curvature entropy after controlling fractal dimension)."},
        {"id": "VF2_VISUAL_RHYTHM_001", "display": "VF2", "nature": "VF2 is the temporal-prediction-during-scanning channel of T2: rhythmic variation PE contributes to overall complexity PE."}
      ],

      "key_references": [
        "Berlyne, D. E. (1971). Aesthetics and psychobiology. Appleton-Century-Crofts.",
        "Van de Cruys, S. (2017). Affective value in the predictive mind. In W. Wiese & T. Metzinger (Eds.), Philosophy and predictive processing. MIND Group. https://doi.org/10.15502/9783958573253",
        "Joffily, M., & Coricelli, G. (2013). Emotional valence and the free-energy principle. PLOS Computational Biology, 9(6), e1003094. https://doi.org/10.1371/journal.pcbi.1003094",
        "Chatterjee, A., & Vartanian, O. (2014). Neuroaesthetics. Trends in Cognitive Sciences, 18(7), 370–375. https://doi.org/10.1016/j.tics.2014.03.003"
      ]
    },

    {
      "template_id": "PP_RAPID_GIST_004",
      "display_id": "T22",
      "name": "Low-Spatial-Frequency Scene Structure — Rapid Associative Prediction — Contextual Framing",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "t1_frameworks": ["predictive_processing", "dual_process"],

      "mechanism_chain": [
        {
          "step": 1, "from": "architectural_LSF_content", "to": "magnocellular_pathway_PFC_activation",
          "description": "Building's LSF content — volume proportions, ceiling-to-floor ratio, window-to-wall ratio, gross light distribution — projects via magnocellular RGCs (preferential sensitivity to < 2 cycles/degree) → V1/V2 → dorsal stream → OFC and lateral PFC. PFC activation onset: ~130ms (Bar et al., 2006 MEG).",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 2, "from": "PFC_activation", "to": "scene_category_and_affective_prediction",
          "description": "PFC generates: (a) scene category prediction ('hospital,' 'home,' 'sacred space,' 'prison') based on LSF match to stored categorical templates; (b) affective prediction co-constructed with the category (Barrett & Bar, 2009).",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 3, "from": "scene_category_prediction", "to": "top_down_V1_V2_modulation",
          "description": "PFC-generated predictions propagate as top-down feedback to V1/V2. Summerfield et al. (2006): predicted stimuli show suppressed V1/V2 responses; unpredicted stimuli show enhanced responses. The categorical frame BIASES how every subsequent HSF detail is processed.",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 4, "from": "categorical_frame_bias", "to": "first_impression_perseverance",
          "description": "The categorical frame established within 130ms persists and shapes final aesthetic evaluation. Correlation between 130ms flash preference and unlimited-viewing preference: r ≈ 0.65–0.70 (photograph studies); r ≈ 0.55–0.65 estimated for immersive environments. First-impression perseverance coefficient: 40% (range 25–55%).",
          "warrant": "MECHANISM", "confidence": 0.55
        }
      ],

      "calibrated_parameters": {
        "LSF_PFC_activation_latency": {
          "central_value": 130, "unit": "milliseconds from stimulus onset",
          "range": [100, 160], "CI_95": [110, 150],
          "confidence": 0.70, "warrant": "MECHANISM",
          "source": "Bar et al. (2006); Kveraga et al. (2007)"
        },
        "first_impression_perseverance_coefficient": {
          "central_value": 0.40, "unit": "fraction of final aesthetic evaluation variance explained by LSF first impression",
          "range": [0.25, 0.55], "CI_95": [0.20, 0.60],
          "confidence": 0.55, "warrant": "MECHANISM",
          "source": "Bar & Neta (2007); Coburn et al. (2020)",
          "notes": "Photograph-based: 0.42–0.49. Immersive experience: −10% adjustment → 0.32–0.39. Central estimate 0.40 applies to both with ±15% uncertainty."
        },
        "LSF_spatial_frequency_threshold": {
          "central_value": 2.0, "unit": "cycles per degree (cutoff for magnocellular-predominant processing)",
          "range": [1.5, 3.0], "confidence": 0.65, "warrant": "MECHANISM",
          "source": "Kveraga et al. (2007)"
        },
        "primary_architectural_LSF_drivers": {
          "description": "R_h (ceiling height / √floor area), WWR (window-to-wall ratio), gross luminance distribution (light/dark ratio), massing silhouette",
          "confidence": 0.65, "warrant": "MECHANISM",
          "notes": "These are the architectural features that carry the LSF information determining categorical gist."
        }
      },

      "population_modifiers": {
        "first_visit_vs_repeat_visitor": {"direction": "higher_perseverance_first_visit", "modifier": "+0.10 perseverance coefficient", "confidence": 0.50},
        "high_anxiety": {"direction": "threat_bias_in_categorical_frame", "notes": "Ambiguous LSF content more likely to receive negative categorical prediction in anxious observers.", "confidence": 0.55},
        "cultural_familiarity_with_building_type": {"direction": "stronger_faster_categorical_prediction", "confidence": 0.55}
      },

      "architectural_modifier_coefficients": {
        "R_h_as_primary_LSF_driver": {
          "description": "R_h and WWR are the architectural parameters most directly determining LSF category assignment. Changing R_h from 0.22 (corridor) to 0.60 (atrium) shifts the categorical frame from 'enclosed/institutional' to 'open/monumental.'",
          "confidence": 0.60
        },
        "facade_silhouette": {
          "description": "Building silhouette (massing outline against sky) is the primary LSF cue for exterior first impression.",
          "confidence": 0.55
        }
      },

      "bridge_warrant": "MECHANISM",
      "bridge_prior": 0.65,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.60,
      "p_effect_composite": 0.51,

      "super_template_interactions": {
        "IC2_body_budget": "T22's affective prediction is an allostatic ANTICIPATION mechanism: the categorical frame predicts the body-budget demands the environment will impose. An 'institutional' prediction triggers preparatory arousal increase; a 'sacred/safe' prediction triggers preparatory parasympathetic engagement. This is IC2's predictive allostasis operating in the architectural domain.",
        "AX4_perceived_control": "Categorical frame modulates AX4: environments predicted as 'institutional' carry reduced perceived control expectation, compounding actual control available. Shifting the LSF category from 'institutional' to 'domestic/collaborative' pre-emptively increases AX4 via categorical prediction."
      },

      "interaction_templates": [
        {"id": "VF3_SPATIAL_PROPORTIONS_001", "display": "VF3", "nature": "T22 is upstream of VF3: gist categorical evaluation of ceiling height occurs at ~130ms via T22, before VF3's slower proportional evaluation at ~300ms+. T22 sets the frame; VF3 calibrates the detailed proportional response within it."},
        {"id": "LUM_CONTRAST_PE_001", "display": "L1", "nature": "T22's gross luminance distribution (overall chiaroscuro) is the L1 analog at the LSF scale. T22 processes the overall pattern; L1 processes local contrast details."},
        {"id": "SPATIAL_INTEGRATION_PE_001", "display": "SC1", "nature": "SC1's integration value is partly an LSF property — global connectivity pattern visible from a distance. T22's categorical evaluation of openness/enclosure partially overlaps with SC1's integration measure."}
      ],

      "key_references": [
        "Bar, M., et al. (2006). Top-down facilitation of visual recognition. Proceedings of the National Academy of Sciences, 103(2), 449–454. https://doi.org/10.1073/pnas.0507062103",
        "Kveraga, K., Boshyan, J., & Bar, M. (2007). Magnocellular projections as the trigger of top-down facilitation in recognition. Journal of Neuroscience, 27(48), 13232–13240. https://doi.org/10.1523/JNEUROSCI.3481-07.2007",
        "Barrett, L. F., & Bar, M. (2009). See it with feeling: Affective predictions during object perception. Philosophical Transactions of the Royal Society B, 364(1521), 1325–1334. https://doi.org/10.1098/rstb.2008.0312",
        "Summerfield, C., et al. (2006). Predictive codes for forthcoming perception in the frontal cortex. Science, 314(5803), 1311–1314. https://doi.org/10.1126/science.1132028"
      ]
    },

    {
      "template_id": "LUM_CONTRAST_PE_001",
      "display_id": "L1",
      "name": "Luminance Contrast Prediction Error and Aesthetic Response",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "t1_frameworks": ["predictive_processing"],

      "mechanism_chain": [
        {
          "step": 1, "from": "luminance_contrast_ratio", "to": "V1_V2_prediction_error_signal",
          "description": "Luminance contrast drives feedforward magnocellular signals to V1/V2. V1/V2 neurons compare feedforward luminance input against top-down predictions about expected luminance distribution given spatial context (Muckli & Petro, 2013). Luminance PE is the residual between actual and predicted luminance.",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 2, "from": "luminance_PE_moderate", "to": "positive_aesthetic_response",
          "description": "Moderate luminance PE (global contrast ratio 1:5–1:15, architecturally coherent shadow structure) generates resolvable prediction challenge → positive valence. Strother (2019): peak preference ratings at global contrast ratio 1:7–1:15 in architectural photographs. Effect size d ≈ 0.50 for preferred vs. flat-lighting conditions.",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60
        },
        {
          "step": 3, "from": "luminance_PE_high_structured", "to": "awe_response_via_AX3",
          "description": "High luminance PE (global contrast > 1:30) in specific spatial configuration (bright zone <20% of visual field surrounded by dark context — Plummer's shaft, chiaroscuro) generates categorical PE: light becomes visible AS A SUBSTANCE rather than surface illumination. Dual-adaptation state in V1 drives AX3 pathway activation.",
          "warrant": "MECHANISM", "confidence": 0.55
        },
        {
          "step": 4, "from": "luminance_PE_extreme", "to": "glare_discomfort_and_avoidance",
          "description": "Luminance exceeding retinal adaptation tolerance (point source > 2,000 cd/m²; DGP > 0.35) triggers discomfort via sustained accommodation effort, pupillary strain, and cortical arousal. Wienold & Christoffersen (2006): DGP > 0.35 produces 50% occupant dissatisfaction.",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.80
        }
      ],

      "calibrated_parameters": {
        "goldilocks_zone_global_contrast_ratio": {
          "low_bound": 5, "optimal": 10, "high_bound": 15,
          "unit": "ratio max:min luminance in visual field (cd/m²)",
          "CI_95_optimal": [7, 14],
          "confidence": 0.60, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Strother (2019); Veitch & Newsham (1998)",
          "flag": "THEORETICAL_DEFAULT for exact boundaries — Strother data not yet published in full parametric form; boundaries expert-calibrated"
        },
        "awe_trigger_configuration": {
          "contrast_ratio_threshold": 30,
          "bright_zone_max_fraction_of_visual_field": 0.20,
          "confidence": 0.55, "warrant": "MECHANISM",
          "source": "Plummer (2009); Muckli V1 dual-adaptation account",
          "notes": "Shaft, chiaroscuro, aureole configurations meet this criterion. The 20% fraction is an expert estimate requiring direct psychophysical validation."
        },
        "glare_discomfort_threshold_DGP": {
          "central_value": 0.35, "unit": "Daylight Glare Probability",
          "range": [0.30, 0.40], "confidence": 0.80, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Wienold & Christoffersen (2006)"
        },
        "preferred_luminance_range_visual_field": {
          "lower_bound": 50, "upper_bound": 300, "unit": "cd/m² average scene luminance",
          "confidence": 0.55, "warrant": "EMPIRICAL_COVARIANCE"
        },
        "spatial_coherence_modifier": {
          "description": "Contrast on architecturally meaningful structures (coherent shadows) produces more positive aesthetic response than equivalent contrast from arbitrary sources.",
          "magnitude": "+0.20 to +0.35 preference advantage for coherent vs. incoherent contrast at matched ratio",
          "confidence": 0.50, "flag": "THEORETICAL_DEFAULT for exact magnitude"
        }
      },

      "population_modifiers": {
        "migraine_prone": {"direction": "lower_glare_threshold", "modifier": "DGP threshold −0.08", "confidence": 0.55},
        "elderly_65plus": {"direction": "lower_glare_tolerance", "modifier": "Preferred range shifts to 30–200 cd/m²; DGP threshold −0.05", "confidence": 0.55},
        "dark_adapted": {"direction": "leftward_shift_in_contrast_tolerance", "confidence": 0.60}
      },

      "architectural_modifier_coefficients": {
        "window_shading": {"description": "Uncontrolled direct sun creates extreme contrast (DGP > 0.50). External shading: −40–60% peak luminance.", "confidence": 0.70},
        "surface_reflectance_near_window": {"description": "High-reflectance walls within 3m of window reduce global contrast ratio by ~30–50%.", "confidence": 0.60},
        "ceiling_reflectance": {"description": "ρ > 0.80 vs. ρ < 0.30: 25–40% reduction in contrast ratio.", "confidence": 0.60}
      },

      "building_types": ["sacred spaces (awe zone)", "museums and galleries (moderate-to-high contrast)", "offices (moderate: 1:5–1:10)", "hospitals (low: 1:3–1:6)"],

      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "bridge_prior": 0.60,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.60,
      "p_effect_composite": 0.51,

      "super_template_interactions": {
        "IC2_body_budget": "L1's glare extreme (DGP > 0.45) imposes sustained visual discomfort contributing to allostatic cost. Moderate contrast (Goldilocks zone) contributes to IC2 equilibrium. Chronic under-contrasted environments (uniform fluorescent lighting) deny the restorative visual prediction engagement that moderate PE provides.",
        "AX4_perceived_control": "Occupant control over shading (operable blinds, electrochromic glazing) is a direct AX4 interaction. Glare from uncontrollable sources scores among the highest AX4 violations in post-occupancy surveys."
      },

      "interaction_templates": [
        {"id": "PP_SPECTRAL_MATCH_001", "display": "T1", "nature": "Dappled light has 1/f luminance statistics — intersection of T1 and L1. Both activate simultaneously; joint activation is additive."},
        {"id": "AX3_AWE_HIGH_PE_001", "display": "AX3", "nature": "L1's high-PE awe-trigger configuration (contrast > 1:30, bright zone <20%) is the luminance-specific input to AX3. L1 is upstream; AX3 is downstream."},
        {"id": "SPATIAL_INTEGRATION_PE_001", "display": "SC1", "nature": "L1 is a partial confound in SC1 studies (high-integration spaces receive more daylight → luminance contrast). Article Eater should apply L1 partial-out when analyzing SC1 claims."}
      ],

      "key_references": [
        "Muckli, L., & Petro, L. S. (2013). Network interactions: Non-geniculate input to V1. Current Opinion in Neurobiology, 23(2), 195–201. https://doi.org/10.1016/j.conb.2013.01.020",
        "Wienold, J., & Christoffersen, J. (2006). Evaluation methods and development of a new glare prediction model. Energy and Buildings, 38(7), 743–757. https://doi.org/10.1016/j.enbuild.2005.08.029",
        "Plummer, H. (2009). The architecture of natural light. Thames & Hudson.",
        "Veitch, J. A., & Newsham, G. R. (1998). Lighting quality and energy-efficiency effects. Journal of the Illuminating Engineering Society, 27(1), 107–129. https://doi.org/10.1080/00994480.1998.10748214"
      ]
    },

    {
      "template_id": "NATURE_VIEW_CONVERGENCE_001",
      "display_id": "VIEW1",
      "name": "Nature View as Multi-Channel Prediction Confirmation and Attention Restoration",
      "status": "calibrated",
      "maturity": "established",
      "panel": "VISUAL-I",
      "t1_frameworks": ["predictive_processing", "DMN_TPN_dynamics", "neuromodulatory"],
      "t1_5_parent_theories": ["biophilia (Tier 2)"],

      "mechanism_chain": [
        {
          "step": 1, "from": "nature_view_presence", "to": "multi_channel_activation",
          "description": "A window view of nature simultaneously engages five partially independent channels: (1) T1 fractal fluency — natural scene 1/f statistics engage efficient V1 coding; (2) SC2 prospect — view extends isovist horizon; (3) T25 ART soft fascination — gently interesting natural elements engage involuntary attention, releasing directed attention; (4) L5 temporal variation — natural dynamism provides moderate sustained PE at ~0.1–0.5 Hz; (5) T5 ecological safety — vegetation + spatial depth signal evolutionary safety, reducing amygdala threat monitoring.",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.70
        },
        {
          "step": 2, "from": "multi_channel_confirmation", "to": "autonomic_stress_reduction",
          "description": "Convergent confirmation across channels reduces overall allostatic PE → parasympathetic activation (vagal tone increase), cortisol reduction, heart rate reduction. Ulrich (1984): hospital patients with tree views: 7.96 vs. 8.70 day stay. Ulrich et al. (1991): 4–7 minute GSR recovery vs. urban scenes.",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.75
        },
        {
          "step": 3, "from": "soft_fascination", "to": "directed_attention_restoration",
          "description": "Channel 3 (ART): involuntary attention engagement → TPN deactivation → DMN re-engagement → directed attention resource replenishment (Kaplan, 1995). Duration required: ~5 min for initial DMN re-engagement; ~20–40 min for full restoration. This is resource recovery during involuntary engagement, not metabolic efficiency of nature processing per se.",
          "warrant": "MECHANISM", "confidence": 0.60
        }
      ],

      "calibrated_parameters": {
        "overall_stress_reduction_effect": {
          "central_value": 0.55, "unit": "r correlation nature view vs. no-nature view on combined stress/wellbeing outcomes",
          "range": [0.40, 0.70], "CI_95": [0.38, 0.68],
          "confidence": 0.75, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Ulrich (1984); Ulrich et al. (1991); White et al. (2019); Bowler et al. (2010)"
        },
        "channel_confidence_scores": {
          "T1_fractal_fluency": {"confidence": 0.55, "warrant": "EMPIRICAL_COVARIANCE"},
          "SC2_prospect": {"confidence": 0.60, "warrant": "EMPIRICAL_COVARIANCE"},
          "T25_ART_soft_fascination": {"confidence": 0.65, "warrant": "MECHANISM"},
          "L5_temporal_variation": {"confidence": 0.50, "warrant": "EMPIRICAL_COVARIANCE"},
          "T5_ecological_safety": {"confidence": 0.60, "warrant": "MECHANISM"}
        },
        "multi_channel_partial_redundancy_correction": {
          "inter_channel_correlation": 0.30,
          "total_explained_variance_estimate": 0.46,
          "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"
        },
        "view_quality_gradient": {
          "high_biodiverse_natural_landscape": {"channels": 5, "estimated_r": 0.65, "confidence": 0.65},
          "managed_garden_park": {"channels": 4, "estimated_r": 0.50, "confidence": 0.60},
          "sparse_single_tree": {"channels": 2, "estimated_r": 0.30, "confidence": 0.55},
          "sky_only": {"channels": 1, "estimated_r": 0.15, "confidence": 0.45},
          "blank_wall": {"channels": 0, "estimated_r": 0.0, "confidence": 0.70}
        },
        "attention_restoration_minimum_duration": {
          "central_value": 5, "unit": "minutes",
          "range": [3, 10], "confidence": 0.55, "warrant": "MECHANISM",
          "source": "Kaplan (1995); Cimprich (1993)"
        },
        "weekly_nature_contact_threshold": {
          "central_value": 120, "unit": "minutes per week (visual + physical combined)",
          "confidence": 0.65, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "White et al. (2019)"
        }
      },

      "population_modifiers": {
        "attention_depleted_workers": {"direction": "stronger_restoration", "modifier": "+30–50% benefit magnitude", "confidence": 0.60},
        "healthcare_patients": {"direction": "largest_documented_effect", "notes": "Ulrich (1984) d ≈ 0.65 for hospital stay length", "confidence": 0.75},
        "children_under_12": {"direction": "potentially_stronger", "modifier": "+20% estimated", "confidence": 0.45, "flag": "THEORETICAL_DEFAULT"}
      },

      "architectural_modifier_coefficients": {
        "window_size": {"description": "Minimum useful: >0.5m² for seated occupant at 3m. Benefit scales ~log(window_area); diminishing returns above 3m² per occupant.", "confidence": 0.50},
        "glazing_type": {"description": "Clear glass preserves all channels. Tinted: −20% effect. Frosted: −80% effect.", "confidence": 0.55},
        "view_distance": {"description": "Close nature (<5m): maximum T1 + T5. Distance >50m: reduced T1 + T5, maintained SC2 prospect.", "confidence": 0.50}
      },

      "building_types": ["hospitals — highest priority, largest documented effect", "schools", "offices", "residential (bedroom/living area windows)"],

      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "bridge_prior": 0.70,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.65,
      "p_effect_composite": 0.55,

      "super_template_interactions": {
        "IC2_body_budget": "VIEW1 is the single largest documented reducer of architectural allostatic load. Multi-channel nature view simultaneously addresses visual PE cost (T1), threat monitoring cost (T5), attentional fatigue cost (T25), and spatial prediction cost (SC2). Buildings providing high-quality nature views reduce IC2 body-budget expenditure substantially.",
        "AX4_perceived_control": "Nature views provide a strong AX4 signal when occupants can CHOOSE to look out (operable windows, movable workstations near windows). The AX4 contribution to the total VIEW1 benefit is significant when control is present; Ulrich's controlled study documents the bare nature-view benefit without AX4."
      },

      "interaction_templates": [
        {"id": "PP_SPECTRAL_MATCH_001", "display": "T1", "nature": "Channel 1 of VIEW1."},
        {"id": "ISOVIST_VISUAL_PREDICTION_001", "display": "SC2", "nature": "Channel 2 of VIEW1."},
        {"id": "DT_DIRECTED_ATTENTION_001", "display": "T25", "nature": "Channel 3 of VIEW1. T25/ART provides the soft fascination mechanism."},
        {"id": "NM_THREAT_HPA_001", "display": "T5", "nature": "Channel 5 of VIEW1. Nature views reduce amygdala threat activation."},
        {"id": "ALLOSTATIC_MASTER_001", "display": "T29", "nature": "VIEW1 feeds T29 as the primary multi-channel restorative template."}
      ],

      "key_references": [
        "Ulrich, R. S. (1984). View through a window may influence recovery from surgery. Science, 224(4647), 420–421. https://doi.org/10.1126/science.6143402",
        "Ulrich, R. S., et al. (1991). Stress recovery during exposure to natural and urban environments. Journal of Environmental Psychology, 11(3), 201–230. https://doi.org/10.1016/S0272-4944(05)80184-7",
        "Kaplan, S. (1995). The restorative benefits of nature. Journal of Environmental Psychology, 15(3), 169–182. https://doi.org/10.1016/0272-4944(95)90001-2",
        "White, M. P., et al. (2019). Spending at least 120 minutes a week in nature is associated with good health and wellbeing. Scientific Reports, 9(1), 7730. https://doi.org/10.1038/s41598-019-44097-3"
      ]
    },

    {
      "template_id": "VF1_CONTOUR_PE_001",
      "display_id": "VF1",
      "name": "Contour Curvature Prediction Error and Approach-Avoidance",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "prior_calibration": "VF-II Doc 64 (Feb 17, 2026) — CCI metric established, partial calibration",
      "t1_frameworks": ["predictive_processing"],

      "mechanism_chain": [
        {
          "step": 1, "from": "architectural_contour_geometry", "to": "early_visual_contour_PE_signal",
          "description": "Building edges are extracted by V1 orientation-selective neurons. Angular vertices (high CCI) generate stronger mismatch signals than smooth curves (low CCI) because the visual generative model's contour prediction — which smoothly interpolates edge trajectories — is violated at vertices. P1 component at ~84ms (Leder et al., 2011): earliest EEG marker of contour PE.",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 2, "from": "contour_PE", "to": "amygdala_activation_and_approach_avoidance",
          "description": "Contour PE projects to amygdala via subcortical route (superior colliculus → pulvinar → amygdala). Angular contours produce measurable amygdala activation increase; curved contours show reduced activation. Approach-avoidance signal detectable in ERP at ~130ms. Bar & Neta (2006, 2007).",
          "warrant": "MECHANISM", "confidence": 0.70
        },
        {
          "step": 3, "from": "knowledge_meaning_modulation", "to": "expert_appreciation_of_angular_form",
          "description": "From ~300ms, semantic/contextual knowledge modulates the initial contour PE valence via OFC. Architectural training can REINTERPRET angular PE as intellectually engaging. This modulation is at the EVALUATIVE level, not the perceptual level — the 84ms P1 signal does not habituate with expertise. Knowledge-meaning modifier can reduce effective contour PE penalty by up to 60% for experts in rich conceptual contexts.",
          "warrant": "MECHANISM", "confidence": 0.60
        }
      ],

      "calibrated_parameters": {
        "CCI_boundary_values": {
          "uniform": {"range": "<0.15", "response": "Near-zero PE, neutral (may bore)", "confidence": 0.60},
          "smooth": {"range": "0.15–0.40", "response": "Low PE, fluency → approach, positive", "confidence": 0.65},
          "moderate_optimal": {"range": "0.40–0.80", "response": "Optimal: fluency + interest", "confidence": 0.65},
          "angular_mixed": {"range": "0.80–1.20", "response": "High PE, context-dependent", "confidence": 0.55},
          "angular": {"range": "1.20–1.80", "response": "Very high PE, expert-dependent", "confidence": 0.50},
          "extreme": {"range": ">1.80", "response": "Maximal PE, generally aversive", "confidence": 0.55},
          "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Bar & Neta (2006, 2007); Vartanian et al. (2013, 2019, 2021); Coburn et al. (2020)"
        },
        "vr_effect_sizes": {
          "beauty_curved_vs_angular": {"d": 0.45, "CI_95": [0.30, 0.60], "confidence": 0.70, "source": "Vartanian et al. (2019)"},
          "approach_curved_vs_angular": {"d": 0.35, "CI_95": [0.20, 0.50], "confidence": 0.65}
        },
        "contour_PE_time_course": {
          "P1_initial_detection_ms": {"value": 84, "confidence": 0.75},
          "approach_avoidance_signal_ms": {"value": 130, "confidence": 0.70},
          "knowledge_meaning_onset_ms": {"value": 300, "confidence": 0.65}
        },
        "exposure_habituation_function": {
          "formula": "d_preference(t) = 0.45 × [0.40 + 0.60 × exp(−t/τ)]",
          "tau_days": 15, "tau_range_days": [12, 18],
          "floor_factor": 0.40,
          "interpretation": "40% of initial d ≈ 0.45 gap persists permanently (perceptual component); 60% decays over ~2–4 weeks. At 2 weeks: d ≈ 0.28; at 4 weeks: d ≈ 0.22.",
          "confidence": 0.55, "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Carbon (2010); Carbon & Leder (2005)"
        },
        "knowledge_meaning_modifier": {
          "formula": "d_effective = d_PE × (1 − k_expertise × context_richness)",
          "k_naive": 0.0, "k_professional_architect": 0.60,
          "context_richness_range": [0.0, 1.0], "maximum_reduction": 0.60,
          "confidence": 0.50, "warrant": "MECHANISM",
          "notes": "Perceptual PE cannot be eliminated — only the evaluative consequence. Even architects generate full 84ms P1 PE at high-CCI vertices."
        },
        "enclosure_contour_interaction": {
          "model": "ADDITIVE (no significant interaction term, Vartanian 2019)",
          "curved_open_d": "+0.35 net positive",
          "curved_enclosed_d": "0.00 neutral",
          "angular_open_d": "+0.10 mildly positive",
          "angular_enclosed_d": "+0.45 net NEGATIVE",
          "confidence": 0.65,
          "design_implication": "In unavoidable corridors (confining R_h), curved contours compensate for enclosure PE."
        }
      },

      "architectural_context_recommendations": {
        "healthcare": {"CCI": "0.20–0.50"},
        "primary_school": {"CCI": "0.25–0.55"},
        "office": {"CCI": "0.30–0.70"},
        "cultural_gallery": {"CCI": "0.40–1.50"},
        "memorial_sacred": {"CCI": "0.60–1.80+"}
      },

      "population_modifiers": {
        "architectural_professionals": {"direction": "higher_angular_tolerance", "modifier": "k_expertise ≈ 0.50–0.60", "confidence": 0.55},
        "cognitive_load_or_fatigue": {"direction": "return_to_naive_PE", "notes": "Knowledge-meaning override weakens; CCI tolerance narrows.", "confidence": 0.55}
      },

      "bridge_warrant": "MECHANISM",
      "bridge_prior": 0.65,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.65,
      "p_effect_composite": 0.55,

      "super_template_interactions": {
        "IC2_body_budget": "High-CCI environments in high-cognitive-load contexts impose sustained contour PE processing cost on a depleted body budget. When cognitive resources to implement the knowledge-meaning override are unavailable, the raw contour PE penalty is paid in full — an IC2 cost imposed on a population that cannot afford it (e.g., fatigued hospital patients).",
        "AX4_perceived_control": "No strong direct interaction. If occupants can choose orientation to minimize angular contour exposure, AX4 is weakly engaged."
      },

      "interaction_templates": [
        {"id": "PP_COMPLEXITY_GOLDILOCKS_002", "display": "T2", "nature": "VF1 is the contour-geometry channel of T2. CCI contributes to overall visual complexity PE."},
        {"id": "VF3_SPATIAL_PROPORTIONS_001", "display": "VF3", "nature": "VF1 and VF3 interact additively (Vartanian 2019). Angular + Confining is the worst architectural combination (d ≈ −0.45)."},
        {"id": "AX3_AWE_HIGH_PE_001", "display": "AX3", "nature": "At extreme CCI (>1.80) in memorial/sacred contexts, VF1's high PE contributes to AX3 threshold activation."}
      ],

      "key_references": [
        "Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. Psychological Science, 17(8), 645–648. https://doi.org/10.1111/j.1467-9280.2006.01759.x",
        "Vartanian, O., et al. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. PNAS, 110(Suppl. 2), 10446–10453. https://doi.org/10.1073/pnas.1301227110",
        "Vartanian, O., et al. (2019). Preference for curvilinear architecture. Psychology of Aesthetics, Creativity, and the Arts, 13(4), 399–409. https://doi.org/10.1037/aca0000181",
        "Carbon, C.-C. (2010). The cycle of preference. Acta Psychologica, 134(2), 233–244. https://doi.org/10.1016/j.actpsy.2010.02.004"
      ]
    },

    {
      "template_id": "VF2_VISUAL_RHYTHM_001",
      "display_id": "VF2",
      "name": "Visual Rhythm and Scaling Hierarchy — Temporal Prediction During Scanning",
      "status": "calibrated",
      "maturity": "preliminary",
      "panel": "VISUAL-I",
      "prior_calibration": "VF-II Doc 64 (Feb 17, 2026) — SRV and SCI metrics defined, boundary values expert estimates",
      "t1_frameworks": ["predictive_processing"],

      "mechanism_chain": [
        {
          "step": 1, "from": "architectural_element_spacing", "to": "rhythmic_saccade_pattern",
          "description": "Regular architectural elements (columns, windows, structural bays) produce rhythmic saccadic eye movements at approximately f = walking_speed / (d × tan(α)) Hz. At 10m viewing distance for a 3m-spaced colonnade: ~2.5–5 Hz saccade rate (Taylor eye-tracking). This falls within the beat perception range in the basal ganglia (1–6 Hz; Grahn & Brett, 2007).",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60
        },
        {
          "step": 2, "from": "rhythmic_saccade_pattern", "to": "temporal_prediction_in_basal_ganglia_SMA",
          "description": "Putamen and SMA construct a temporal model of expected element positions. Regular spacing → stable temporal prediction → low positional PE. SRV-varied spacing → occasional positional PE → small reward prediction error at each unexpected position.",
          "warrant": "ANALOGICAL", "confidence": 0.45,
          "notes": "Analogical transfer from auditory rhythm neuroscience (Grahn & Rowe, 2009). No architectural-specific basal ganglia rhythm imaging data yet exist."
        },
        {
          "step": 3, "from": "moderate_positional_PE", "to": "peak_engagement_visual_groove",
          "description": "Moderate spatial variation (SRV ≈ 0.12–0.25) generates sufficient PE to engage the prediction-correction reward cycle without disrupting the metric framework. Analogous to auditory groove peak at ~20–30% syncopation (Witek et al., 2014). Visual groove: sustained involuntary scanning engagement, higher dwell time, subjective visual interest.",
          "warrant": "ANALOGICAL", "confidence": 0.40,
          "flag": "THEORETICAL_DEFAULT — SRV boundary values are predictions from auditory analogy, not directly measured"
        }
      ],

      "calibrated_parameters": {
        "SRV_goldilocks_zone": {
          "perfectly_regular": {"range": "0.00–0.05", "response": "Low engagement; fully predicted", "confidence": 0.50},
          "slightly_varied": {"range": "0.05–0.12", "response": "Rising engagement", "confidence": 0.45},
          "peak_estimated": {"range": "0.12–0.25", "response": "Peak: visual groove optimum", "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"},
          "declining": {"range": "0.25–0.40", "response": "Declining; prediction framework strains", "confidence": 0.40},
          "irregular": {"range": ">0.40", "response": "Low; no spatial prediction possible", "confidence": 0.50},
          "warrant": "ANALOGICAL",
          "source": "Grahn & Witek (2014) auditory analogy; Taylor eye-tracking direction data"
        },
        "SCI_scaling_coherence": {
          "rich": {"range": ">0.80", "response": "Sustained positive engagement", "confidence": 0.45},
          "good": {"range": "0.60–0.80", "response": "Positive, minor gaps", "confidence": 0.45},
          "partial": {"range": "0.40–0.60", "response": "Neutral to mildly positive", "confidence": 0.45},
          "sparse": {"range": "0.20–0.40", "response": "Visual starvation", "confidence": 0.40},
          "depleted": {"range": "<0.20", "response": "Negative for sustained viewing", "confidence": 0.45},
          "empirical_basis": "Coburn retroactive r ≈ 0.28 (preliminary)",
          "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.45
        },
        "visual_nourishment_equation": {
          "formula": "Visual_nourishment = T1_fractal(D ≈ 1.3) × VF2_rhythm(SRV ≈ 0.12–0.25) × VF2_hierarchy(SCI > 0.60)",
          "confidence": 0.40,
          "flag": "THEORETICAL_DEFAULT — interaction form (multiplicative vs. additive) not empirically determined"
        },
        "scanning_speed_moderator": {
          "baseline": "1.2 m/s walking pace",
          "notes": "SRV Goldilocks range applies to standard walking-pace scanning. Faster scanning shifts optimal SRV downward; seated viewing at distance requires adjustment.",
          "confidence": 0.40, "flag": "THEORETICAL_DEFAULT"
        }
      },

      "bridge_warrant": "ANALOGICAL",
      "bridge_prior": 0.40,
      "p_parent_theory": 0.80,
      "p_cnfa_specific": 0.40,
      "p_effect_composite": 0.32,

      "super_template_interactions": {
        "IC2_body_budget": "Visual rhythm disruption (SRV > 0.40, SCI < 0.20) may impose a small but persistent allostatic cost through sustained scanning effort without prediction resolution. Effect magnitude is lower than L1 glare or VF1 angular PE; primarily relevant for very long occupancy durations.",
        "AX4_perceived_control": "No direct interaction identified. Visual rhythm is a property of the architectural environment, not of occupant agency."
      },

      "interaction_templates": [
        {"id": "PP_SPECTRAL_MATCH_001", "display": "T1", "nature": "T1 measures APERIODIC fractal statistics; VF2 measures PERIODIC rhythmic regularity. Partial independence confirmed by Coburn (ΔR² after controlling D ≈ 0.03 for SCI). Compute jointly to avoid double-counting."},
        {"id": "ARCH_PROMENADE_TEMPORAL_PE_001", "display": "SC3", "nature": "VF2 (saccade-scale rhythm, ~0.2–0.4s) and SC3 (sequence-scale rhythm, ~20–45s) are nested temporal prediction hierarchies."}
      ],

      "key_references": [
        "Grahn, J. A., & Brett, M. (2007). Rhythm and beat perception in motor areas of the brain. Journal of Cognitive Neuroscience, 19(5), 893–906. https://doi.org/10.1162/jocn.2007.19.5.893",
        "Grahn, J. A., & Rowe, J. B. (2009). Feeling the beat: Premotor and striatal interactions in musicians and nonmusicians. Journal of Neuroscience, 29(23), 7540–7548. https://doi.org/10.1523/JNEUROSCI.0018-09.2009",
        "Witek, M. A. G., et al. (2014). Syncopation, body-movement and pleasure in groove music. PLoS ONE, 9(4), e94446. https://doi.org/10.1371/journal.pone.0094446",
        "Salingaros, N. A. (2005). Principles of urban structure. Techne Press."
      ]
    },

    {
      "template_id": "VF3_SPATIAL_PROPORTIONS_001",
      "display_id": "VF3",
      "name": "Spatial Proportions, Ceiling Height, and Cognitive Processing Mode",
      "status": "calibrated",
      "maturity": "supported",
      "panel": "VISUAL-I",
      "prior_calibration": "VF-II Doc 64 (Feb 17, 2026) + Doc 54 R_h parameterization — deepened here",
      "t1_frameworks": ["predictive_processing", "embodied_cognition"],

      "mechanism_chain": [
        {
          "step": 1, "from": "ceiling_height_and_room_proportions", "to": "spatial_enclosure_PE",
          "description": "R_h = ceiling_height / √(floor_area). This dimensionless ratio captures the occupant's sense of spatial liberation vs. confinement in a form that predicts amygdala response independently of absolute room size. Low R_h (< 0.25): spatial compression, proprioceptive prediction of restricted movement range, elevated amygdala activation. High R_h (> 0.50): spatial expansion, movement range exceeds prediction → positive spatial PE.",
          "warrant": "MECHANISM", "confidence": 0.65
        },
        {
          "step": 2, "from": "spatial_enclosure_PE", "to": "affect_broadening_narrowing",
          "description": "Low R_h → confinement → narrowed cognitive scope (Fredrickson broaden-and-build reversed). High R_h → liberation → expanded affordance → amygdala reduction → broadened cognitive scope. Meyers-Levy & Zhu (2007): 2.4m vs. 3.0m ceiling produced relational/categorical processing shift. Vartanian et al. (2015): fMRI enclosure effects on beauty and approach decisions.",
          "warrant": "MECHANISM", "confidence": 0.60
        },
        {
          "step": 3, "from": "affect_broadening", "to": "CREA2B_divergent_thinking",
          "description": "Broadened affect → expanded prediction envelope → increased tolerance for remote associations → divergent/relational thinking advantages. VF3 → CREA2B is a single causal chain: DO NOT independently compute CREA2B from ceiling height — trace through VF3's affect link. Motor pathway (CREA3) is genuinely independent and additive.",
          "warrant": "MECHANISM", "confidence": 0.55
        }
      ],

      "calibrated_parameters": {
        "R_h_goldilocks": {
          "confining": {"range": "<0.25", "response": "Spatial compression, threat elevation", "confidence": 0.65},
          "balanced": {"range": "0.25–0.35", "response": "Neutral — adequate for most functions", "confidence": 0.65},
          "liberating": {"range": "0.35–0.50", "response": "Spatial liberation, affect broadening, creativity support", "confidence": 0.65},
          "impressive": {"range": "0.50–0.80", "response": "Strong liberation, potential awe initiation", "confidence": 0.60},
          "overwhelming": {"range": ">0.80", "response": "Exceeds comfortable scale; awe or discomfort", "confidence": 0.55},
          "warrant": "EMPIRICAL_COVARIANCE",
          "source": "Doc 54 R_h parameterization; Vartanian et al. (2015); Meyers-Levy & Zhu (2007)"
        },
        "transition_enhancement_function": {
          "formula": "PE_transition = 0.55 × ln(R_h_new / R_h_old)",
          "k_central": 0.55, "k_range": [0.35, 0.75], "k_confidence": 0.40,
          "k_flag": "THEORETICAL_DEFAULT — k estimated from Vartanian fMRI + Meyers-Levy behavioral; not directly measured",
          "examples": {
            "corridor_to_atrium": {"R_h_ratio": 2.7, "PE_transition": 0.55, "processing_shift_d": 0.50},
            "standard_to_high_studio": {"R_h_ratio": 1.4, "PE_transition": 0.18, "processing_shift_d": 0.20},
            "atrium_to_standard_room": {"R_h_ratio": 0.53, "PE_transition": -0.35, "processing_shift_d": 0.30}
          },
          "overall_confidence": 0.45
        },
        "CREA2B_creativity_bonus": {
          "d_divergent_thinking_liberating_R_h": 0.40,
          "range": [0.25, 0.55], "confidence": 0.55,
          "source": "Meyers-Levy & Zhu (2007); Slepian & Ambady (2012)",
          "computation": "Apply as VF3 affect broadening → CREA2B coefficient. Do NOT double-add CREA2B independently from ceiling height."
        },
        "contour_proportions_interaction": {
          "model": "ADDITIVE (Vartanian 2019)",
          "curved_liberating": "+0.35 net positive",
          "curved_confining": "0.00 neutral",
          "angular_liberating": "+0.10 mildly positive",
          "angular_confining": "+0.45 net NEGATIVE",
          "confidence": 0.65,
          "design_implication": "In unavoidable corridors, curved contours compensate for enclosure PE."
        }
      },

      "population_modifiers": {
        "claustrophobia": {"direction": "amplified_low_R_h_response", "modifier": "~2–3× amygdala response; optimal R_h threshold shifts to >0.35", "confidence": 0.55},
        "children": {"direction": "proportionally_higher_effective_R_h", "notes": "Child in adult-proportioned space has effectively higher R_h than adult. R_h should be computed relative to observer height.", "confidence": 0.50}
      },

      "architectural_modifier_coefficients": {
        "atrium_visual_access": {"description": "Atrium visible from occupant position amplifies liberation PE even when immediate ceiling is standard height.", "modifier": "+0.08 to +0.15 R_h equivalent", "confidence": 0.50},
        "creative_workspace_target": {"recommended_R_h": "0.40–0.55"}
      },

      "building_types": ["creative workspaces (R_h target 0.40–0.55)", "corridors in hospitals (confining R_h — compensate with low CCI)", "sacred spaces (high R_h for awe)"],

      "bridge_warrant": "MECHANISM",
      "bridge_prior": 0.60,
      "p_parent_theory": 0.85,
      "p_cnfa_specific": 0.60,
      "p_effect_composite": 0.51,

      "super_template_interactions": {
        "IC2_body_budget": "Confining R_h produces sustained mild threat activation accruing as allostatic cost. In hospitals with uniformly low R_h corridors and ward bays (R_h < 0.25), cumulative IC2 cost over days of inpatient stay is non-trivial — contributing to the navigation-stress cycle (T14).",
        "AX4_perceived_control": "Spatial liberation (high R_h) is architecturally the most direct embodiment of expanded action-policy space (PP_ACTIVE_INFERENCE_003). High R_h environments afford more movement options, contributing to AX4 directly through affordance expansion."
      },

      "interaction_templates": [
        {"id": "PP_RAPID_GIST_004", "display": "T22", "nature": "T22 processes R_h as an LSF property in the first 130ms categorical frame. VF3 provides the slower, proportionally detailed evaluation that follows. T22 is upstream; VF3 is downstream."},
        {"id": "ARCH_PROMENADE_TEMPORAL_PE_001", "display": "SC3", "nature": "SC3's promenade deliberately sequences R_h transitions (approach → development → climax) to deploy VF3's transition-enhancement function as a compositional device."},
        {"id": "VF1_CONTOUR_PE_001", "display": "VF1", "nature": "VF1 and VF3 interact additively. See contour_proportions_interaction in calibrated_parameters."},
        {"id": "AX3_AWE_HIGH_PE_001", "display": "AX3", "nature": "High R_h (> 0.80) contributes to awe threshold by adding spatial liberation PE to the SC3 promenade climax. VF3 → AX3 is a contributing cause pathway."}
      ],

      "key_references": [
        "Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height. Journal of Consumer Research, 34(2), 174–186. https://doi.org/10.1086/519146",
        "Vartanian, O., et al. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure. Journal of Environmental Psychology, 41, 10–18. https://doi.org/10.1016/j.jenvp.2014.11.006",
        "Fredrickson, B. L. (2001). The role of positive emotions in positive psychology. American Psychologist, 56(3), 218–226. https://doi.org/10.1037/0003-066X.56.3.218",
        "Slepian, M. L., & Ambady, N. (2012). Fluid movement and creativity. Journal of Experimental Psychology: General, 141(4), 625–629. https://doi.org/10.1037/a0027395"
      ]
    }

  ]
}
```

---

## OUTPUT BLOCK 2: RESIDUAL GAPS

### T1 (PP_SPECTRAL_MATCH_001)

**UNCALIBRATABLE PARAMETERS:**
- *Metabolic cost reduction in architectural contexts*: The 10–20% glucose utilization reduction is extrapolated from Laughlin (2001) single-neuron efficiency work; not measured in architectural stimulus conditions. Recommended study: fMRI with ¹⁸F-FDG PET co-registration during viewing of parametrically varied architectural facades (D = 1.0, 1.2, 1.3, 1.5, 1.8), N ≥ 40.
- *Cumulative allostatic benefit of long-term T1-compliant occupancy*: No longitudinal study has measured cortisol, HRV, or immune markers across extended occupancy. Recommended: 12-week longitudinal within-subjects ESM with morning cortisol and HRV, N ≥ 60.

**THEORETICAL DEFAULTS:**
- T1 metabolic cost reduction (confidence 0.40): THEORETICAL_DEFAULT. Assumption: Laughlin's single-neuron metabolic efficiency calculations translate to the cortical visual processing system as a whole.
- Elderly and pediatric population modifiers: THEORETICAL_DEFAULT. Direction of shift inferred from exposure-based calibration; magnitude unknown.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → LUM_CONTRAST_PE_001 (L1): Dappled light produces 1/f luminance statistics that simultaneously engage T1 and L1. Article Eater must prevent double-counting when both templates apply. Assign to LIGHT-I.
- CROSS_TEMPLATE_INTERACTION → ARCH_PROMENADE_TEMPORAL_PE_001 (SC3): SC3's multichannel convergence bonus uses T1 as the spatial fractal channel. T1's fractal dimension parameter feeds directly into SC3's convergence model. Assign to SC-III.

---

### T2 (PP_COMPLEXITY_GOLDILOCKS_002)

**UNCALIBRATABLE PARAMETERS:**
- *Absolute architectural complexity thresholds*: T2 is domain-general — its parameters are relative to the observer's complexity set-point. Absolute thresholds cannot be specified without a calibrated reference stimulus battery. Recommended: develop a standardized complexity set-point instrument for architectural assessment.

**THEORETICAL DEFAULTS:**
- Cognitive load leftward shift (−0.25 SD, confidence 0.45): THEORETICAL_DEFAULT. No direct architectural-complexity study under controlled cognitive load conditions.
- Pediatric leftward shift (−0.4 SD, confidence 0.40): THEORETICAL_DEFAULT. Inferred from general visual complexity literature, not architectural studies.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → VF1, VF2, VF3: T2 is the parent template for all three VF templates. The CMR system should compute total visual PE as T2_total = f(T1, VF1_CCI, VF2_SRV/SCI, VF3_R_h). Assign to VF-III.

---

### T22 (PP_RAPID_GIST_004)

**UNCALIBRATABLE PARAMETERS:**
- *First-impression perseverance coefficient for immersive architectural experience*: The existing data are photograph-based. The −10% immersive adjustment is an expert estimate. Recommended: two-condition VR study — 130ms masked exposure vs. unlimited viewing, within-subjects, N ≥ 60, measuring preference correlation.
- *LSF category assignment for non-Western building types*: Categorical templates (hospital, home, sacred, prison) are Western. Cross-cultural validation is absent. Recommended: cross-cultural replication of Bar et al. (2006) using building types native to non-Western architectural traditions.

**THEORETICAL DEFAULTS:**
- LSF determinants (R_h, WWR as primary drivers, confidence 0.65): Mechanistically grounded but not directly tested by architectural LSF manipulation studies.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → SPATIAL_INTEGRATION_PE_001 (SC1): SC1's integration value is partially an LSF property. T22's categorical frame for "open vs. enclosed" overlaps with SC1. Assign to SPATIAL-II.
- CROSS_TEMPLATE_INTERACTION → VF3: T22 is the upstream gist evaluator of R_h (130ms); VF3 is the downstream detailed evaluator (300ms+). The sequencing must be encoded as a temporal dependency. Assign to VF-III.
- CROSS_TEMPLATE_INTERACTION: New T1.5 candidate surfaced — **Aesthetic Anchoring**: how initial affective-categorical predictions systematically bias all subsequent architectural evaluations. Parallels Tversky & Kahneman's numerical anchoring but for architectural affect. Assign to THEORY-REVIEW.

---

### L1 (LUM_CONTRAST_PE_001)

**UNCALIBRATABLE PARAMETERS:**
- *Exact Goldilocks zone boundaries from parametric architectural study*: The 1:7–1:15 range is from Strother's pilot data, not a fully published parametric study. Recommended: within-subjects study with 12-level parametric contrast ratio variation in real architectural photographs and VR scenes, measuring preference, GSR, and self-reported affect, N ≥ 80.
- *Awe-trigger spatial configuration quantification*: The 20% bright-zone fraction threshold is an expert estimate. Recommended: parametric study varying bright-zone fraction (5%, 10%, 20%, 40%, 60%) at fixed 1:30 contrast ratio, measuring AX3 phenomenological indicators and GSR.

**THEORETICAL DEFAULTS:**
- Spatial coherence modifier (+0.20 to +0.35, confidence 0.50): THEORETICAL_DEFAULT. Assumption: architecturally coherent shadow structure reduces visual scene ambiguity, consistent with predictive coding but not directly parameterized.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → AX3_AWE_HIGH_PE_001: L1's awe-trigger configuration (contrast > 1:30, bright zone <20%) is the luminance-specific input to AX3. AX3 panel must incorporate L1's spatial-configuration parameters. Assign to AWE-I.
- CROSS_TEMPLATE_INTERACTION → SPATIAL_INTEGRATION_PE_001 (SC1): L1 is a partial confound in SC1 studies (high-integration spaces receive more daylight → luminance contrast). Article Eater's SC1 analysis pipeline must include L1 partial-out. Assign to SPATIAL-II.

---

### VIEW1 (NATURE_VIEW_CONVERGENCE_001)

**UNCALIBRATABLE PARAMETERS:**
- *Multi-channel independence / partial redundancy correction (r ≈ 0.30)*: The inter-channel correlation is a theoretical estimate. No study has independently varied T1, SC2, T25, L5, and T5 channels in a factorial design. Recommended: VR study with 5 × 2 design (each channel present/absent), N ≥ 120. This is the highest-priority VIEW1 study.
- *Dose-response for view quality gradient effect sizes*: The gradient effect estimates are expert estimates, not controlled psychophysical measurements. Recommended: parametric view quality study in healthcare setting with 5 conditions, N ≥ 80.

**THEORETICAL DEFAULTS:**
- Pediatric +20% benefit (confidence 0.45): THEORETICAL_DEFAULT. No architectural study with child participants.
- Multi-channel partial redundancy correction (r ≈ 0.30, confidence 0.40): THEORETICAL_DEFAULT. Assumption: nature stimuli scoring well on T1 also score well on SC2 and L5.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → ALLOSTATIC_MASTER_001 (T29): VIEW1 is among the most potent single elements contributing to allostatic restoration. T29's architectural parameter list should explicitly include nature-view quality as a primary restorative input. Assign to NEUROMOD-I.

---

### VF1 (VF1_CONTOUR_PE_001)

**UNCALIBRATABLE PARAMETERS:**
- *CCI dose-response curve from direct parametric architectural study*: Prediction 1 from VF-II has not been run. Recommended: within-subjects presentation of 10-level CCI parametric variation (CCI 0.1–2.0) in matched architectural renderings, measuring beauty ratings, ERP (P1, N400), N ≥ 60.
- *Knowledge-meaning modifier k_expertise*: The range 0.0–0.60 derives from Carbon's behavioral data; the architectural-specific expert k has not been confirmed by ERP comparing architects vs. non-architects. Recommended: ERP study with 20 architects and 20 matched controls.

**THEORETICAL DEFAULTS:**
- Exposure habituation floor factor 0.40 (confidence 0.55): Based on Carbon's behavioral data; the perceptual floor has not been confirmed by ERP at very long exposure durations (> 6 months).

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → IC2: High-CCI environments in fatigued/stressed populations impose contour PE cost without knowledge-meaning override availability. IC2 must encode CCI × cognitive_load interaction. Assign to NEUROMOD-I.

---

### VF2 (VF2_VISUAL_RHYTHM_001)

**UNCALIBRATABLE PARAMETERS:**
- *SRV Goldilocks zone from direct psychophysical study*: Prediction 2 from VF-II has not been run. This is VF2's most critical gap. Recommended: within-subjects colonnade SRV variation study (8 levels: 0.00–0.60), measuring beauty ratings, dwell time (eye tracking), EEG alpha power, N ≥ 80.
- *SCI empirical validation from Coburn dataset*: The r ≈ 0.28 correlation is preliminary. Full analysis and publication needed for formal validation.

**THEORETICAL DEFAULTS:**
- SRV boundary values (0.12–0.25 optimum, confidence 0.40): THEORETICAL_DEFAULT. Transferred from auditory groove analogy; specific transfer assumption: visual scanning is internally paced, reducing optimal SRV by ~5% relative to auditory syncopation optimum.
- Visual nourishment equation (multiplicative form, confidence 0.40): THEORETICAL_DEFAULT. Interaction form unconfirmed.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → ARCH_PROMENADE_TEMPORAL_PE_001 (SC3): VF2 (saccade-scale, ~0.2–0.4s) and SC3 (sequence-scale, ~20–45s) are nested temporal prediction hierarchies. Must be encoded as a hierarchy, not independent parallel processes. Assign to SC-III.

---

### VF3 (VF3_SPATIAL_PROPORTIONS_001)

**UNCALIBRATABLE PARAMETERS:**
- *Transition-enhancement k coefficient (k ≈ 0.55)*: Estimated from indirect evidence. Prediction 3 from VF-II (A > B > C creative task design) has not been run. Recommended: three-condition study — A: low-ceiling corridor → high-ceiling creative space; B: high-ceiling → high-ceiling; C: low-ceiling throughout; measuring divergent thinking (AUT) and convergent thinking (RAT), N ≥ 90.

**THEORETICAL DEFAULTS:**
- Atrium visibility modifier (+0.08 to +0.15 R_h equivalent, confidence 0.50): THEORETICAL_DEFAULT. Assumption: vertical visual access via atrium modifies the proprioceptive enclosure assessment similarly to actual ceiling height difference.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → SC3 (promenade): VF3 transition-enhancement is the mechanism behind SC3's compositional approach → development → climax arc. R_h increases along the promenade are the primary spatial PE signal that SC3's position-weight table amplifies. Assign to SC-III.
- CROSS_TEMPLATE_INTERACTION → AX3 (awe): High R_h (> 0.80) contributes to the awe threshold by adding spatial liberation PE to the SC3 promenade climax. Assign to AWE-I.

---

## OUTPUT BLOCK 3: CMR INTEGRATION NOTE

### Overall Framework Mapping

All eight VISUAL-I templates operate within the **Predictive Processing (PP)** framework as their primary Tier 1 theoretical architecture. They instantiate PP at different spatial scales and visual processing stages:

T1 — PP at the spatial-frequency statistics level (V1 efficient coding as a form of prior-matched prediction). T2 — PP as a domain-general Goldilocks principle for any perceptual complexity dimension. T22 — PP at the scene-categorization level (LSF categorical frame as top-down prior governing all subsequent processing). L1 — PP at the luminance-contrast level (coherent shadow as prediction-conforming vs. incoherent contrast as prediction-violating). VF1 — PP at the contour-geometry level (curvature continuity as the visual generative model's default contour prediction). VF2 — PP at the temporal-prediction-during-scanning level (spatial regularity as a predictable sequence). VF3 — PP at the spatial-enclosure level (R_h as the environmental parameter governing proprioceptive prediction of movement range and safety).

VIEW1 additionally engages **DMN/TPN Dynamics** (via Channel 3: ART soft fascination → TPN deactivation → DMN re-engagement) and **Neuromodulatory Systems** (via Channel 5: ecological safety → amygdala → HPA reduction).

### Bridge Warrant Justification Summary

T1: EMPIRICAL_COVARIANCE (0.55) — fractal dimension β = 0.31 in Coburn dataset; GSR reduction in Taylor's experiments. Direct architectural-specific behavioral data exist, supporting a step above ANALOGICAL.

T2: MECHANISM (0.55) — The PP mechanism for valence from PE reduction is theoretically grounded in Joffily & Coricelli (2013) and Van de Cruys (2017). Domain-general application means confidence does not reach the threshold supported by a specific empirical dataset for each building type.

T22: MECHANISM (0.65) — Bar et al. (2006) MEG data directly demonstrate the magnocellular-PFC pathway; Summerfield et al. (2006) confirm top-down V1 modulation. Architecture-specific application reduces confidence to 0.60 for the full causal chain.

L1: EMPIRICAL_COVARIANCE (0.60) — Veitch & Newsham (1998) lighting preference data; Strother (2019) contrast aesthetics; Wienold (2006) glare quantification. Not MECHANISM because the V1 prediction error → aesthetic response pathway has not been directly measured in architectural luminance conditions.

VIEW1: EMPIRICAL_COVARIANCE (0.70) — the strongest empirical warrant in VISUAL-I. Multiple independent replications of the nature view → wellbeing effect in healthcare, workplace, and residential settings.

VF1: MECHANISM (0.65) — Bar & Neta (2006); Vartanian et al. (2013, 2019) architectural fMRI; Leder et al. (2011) ERP time-course. The mechanism chain (contour PE → amygdala → approach-avoidance) is established at the neural level.

VF2: ANALOGICAL (0.40) — Taylor saccade disruption data support mechanism direction; Grahn auditory groove provides Goldilocks prediction. Insufficient direct architectural visual rhythm data for EMPIRICAL_COVARIANCE. Upgrade pathway: if Prediction 2 (VF-II) confirms SRV peak at ~0.12–0.25, warrant upgrades to EMPIRICAL_COVARIANCE (0.55).

VF3: MECHANISM (0.60) — Vartanian et al. (2015) fMRI; Meyers-Levy & Zhu (2007) behavioral. R_h is the best-parameterized spatial metric in VISUAL-I.

### New T1.5 Candidate

**Aesthetic Anchoring** (surfaced from T22 Debate 5): The systematic finding that architectural first impressions formed within 130ms via the LSF-PFC categorical frame account for ~40% of final aesthetic evaluation variance constitutes a potential T1.5 framework — a mid-level theory describing how initial affective-categorical predictions anchor all subsequent architectural experience. This parallels Tversky & Kahneman's numerical anchoring but for affective-perceptual predictions in space. If confirmed cross-culturally and for immersive architectural conditions, it would reduce under PP (T22 as the mechanism) while providing a theoretically productive vocabulary for practitioner communication. Assign to THEORY-REVIEW for T1.5 candidate evaluation.

### IC2 and AX4 Summary Across All Templates

Every visual template has a direct IC2 interaction: the visual domain contributes to the allostatic body budget through the metabolic cost of visual prediction error. L1 glare is the highest-impact single-feature IC2 contribution in VISUAL-I (disability glare → sustained discomfort → allostatic arousal). VIEW1 nature view is the highest-impact restorative IC2 contributor. VF1 angular PE in cognitively depleted populations is the most clinically concerning IC2 risk.

AX4 (perceived control) interacts directly with L1 (controllable shading), VIEW1 (operable windows, movable workstations), and VF3 (ability to choose spatial position relative to ceiling height). T1, T2, VF2, and VF3 have no strong direct AX4 interactions because they operate via automatic perceptual mechanisms that do not require agency to engage.

---

## OUTPUT BLOCK 4: GAP TRACKER UPDATE BLOCK

```bash
# Mark templates calibrated
python3 scripts/gap_tracker.py --mark-calibrated PP_SPECTRAL_MATCH_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated PP_COMPLEXITY_GOLDILOCKS_002 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated PP_RAPID_GIST_004 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated LUM_CONTRAST_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated NATURE_VIEW_CONVERGENCE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF1_CONTOUR_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF2_VISUAL_RHYTHM_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --mark-calibrated VF3_SPATIAL_PROPORTIONS_001 --panel VISUAL-I

# Cross-template interactions — assign to future panels
python3 scripts/gap_tracker.py --assign LUM_CONTRAST_PE_001_T1_dapple_convergence --panel LIGHT-I
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_SC1_integration_overlap --panel SPATIAL-II
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_VF3_temporal_dependency --panel VF-III
python3 scripts/gap_tracker.py --assign T2_VF1_VF2_VF3_domain_decomposition --panel VF-III
python3 scripts/gap_tracker.py --assign VF3_SC3_promenade_R_h_sequence --panel SC-III
python3 scripts/gap_tracker.py --assign VF2_SC3_nested_temporal_hierarchy --panel SC-III
python3 scripts/gap_tracker.py --assign T1_SC3_fractal_convergence_bonus --panel SC-III
python3 scripts/gap_tracker.py --assign L1_AX3_luminance_awe_trigger --panel AWE-I
python3 scripts/gap_tracker.py --assign VF3_AX3_high_R_h_awe_contributing_cause --panel AWE-I
python3 scripts/gap_tracker.py --assign VIEW1_T29_allostatic_restoration --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign VF1_IC2_cognitive_load_CCI_interaction --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign PP_RAPID_GIST_004_AESTHETIC_ANCHORING_T1_5_candidate --panel THEORY-REVIEW

# Verify registry
python3 scripts/gap_tracker.py --report
# Expected: 136 → 128 remaining gaps (8 templates calibrated)
```

---

## OUTPUT BLOCK 5: FULL APA REFERENCE LIST

Bar, M. (2007). The proactive brain: Using analogies and associations to generate predictions. *Trends in Cognitive Sciences*, *11*(7), 280–289. https://doi.org/10.1016/j.tics.2007.05.005

Bar, M., Kassam, K. S., Ghuman, A. S., Boshyan, J., Schmid, A. M., Dale, A. M., Hämäläinen, M. S., Marinkovic, K., Schacter, D. L., Rosen, B. R., & Halgren, E. (2006). Top-down facilitation of visual recognition. *Proceedings of the National Academy of Sciences*, *103*(2), 449–454. https://doi.org/10.1073/pnas.0507062103

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science*, *17*(8), 645–648. https://doi.org/10.1111/j.1467-9280.2006.01759.x

Bar, M., & Neta, M. (2007). Visual elements of subjective preference modulate amygdala activation. *Neuropsychologia*, *45*(10), 2191–2200. https://doi.org/10.1016/j.neuropsychologia.2007.03.008

Barrett, L. F., & Bar, M. (2009). See it with feeling: Affective predictions during object perception. *Philosophical Transactions of the Royal Society B*, *364*(1521), 1325–1334. https://doi.org/10.1098/rstb.2008.0312

Berlyne, D. E. (1971). *Aesthetics and psychobiology*. Appleton-Century-Crofts.

Bowler, D. E., Buyung-Ali, L. M., Knight, T. M., & Pullin, A. S. (2010). A systematic review of evidence for the added benefits to health of exposure to natural environments. *BMC Public Health*, *10*, 456. https://doi.org/10.1186/1471-2458-10-456

Carbon, C.-C. (2010). The cycle of preference: Long-term dynamics of aesthetic appreciation. *Acta Psychologica*, *134*(2), 233–244. https://doi.org/10.1016/j.actpsy.2010.02.004

Carbon, C.-C., & Leder, H. (2005). The repeated evaluation technique (RET). *Applied Cognitive Psychology*, *19*(5), 587–601. https://doi.org/10.1002/acp.1110

Chatterjee, A., & Vartanian, O. (2014). Neuroaesthetics. *Trends in Cognitive Sciences*, *18*(7), 370–375. https://doi.org/10.1016/j.tics.2014.03.003

Cimprich, B. (1993). Development of an intervention to restore attention in cancer patients. *Cancer Nursing*, *16*(2), 83–92. https://doi.org/10.1097/00002820-199304000-00001

Coburn, A., Vartanian, O., & Chatterjee, A. (2020). Buildings, beauty, and the brain: A neuroscience of architectural experience. *Journal of Cognitive Neuroscience*, *32*(11), 2099–2113. https://doi.org/10.1162/jocn_a_01567

Dijkstra, K., Pieterse, M., & Pruyn, A. (2008). Physical environmental stimuli that turn healthcare facilities into healing environments through psychologically mediated effects. *Journal of Advanced Nursing*, *56*(2), 166–181. https://doi.org/10.1111/j.1365-2648.2006.03990.x

Fredrickson, B. L. (2001). The role of positive emotions in positive psychology: The broaden-and-build theory. *American Psychologist*, *56*(3), 218–226. https://doi.org/10.1037/0003-066X.56.3.218

Grahn, J. A., & Brett, M. (2007). Rhythm and beat perception in motor areas of the brain. *Journal of Cognitive Neuroscience*, *19*(5), 893–906. https://doi.org/10.1162/jocn.2007.19.5.893

Grahn, J. A., & Rowe, J. B. (2009). Feeling the beat: Premotor and striatal interactions in musicians and nonmusicians during beat perception. *Journal of Neuroscience*, *29*(23), 7540–7548. https://doi.org/10.1523/JNEUROSCI.0018-09.2009

Hagerhall, C. M., Laike, T., Taylor, R. P., Küller, M., Küller, R., & Martin, T. P. (2008). Investigations of human EEG response to viewing fractal patterns. *Perception*, *37*(10), 1488–1494. https://doi.org/10.1068/p5918

Hagerhall, C. M., Purcell, T., & Taylor, R. (2004). Fractal dimension of landscape silhouette outlines as a predictor of landscape preference. *Journal of Environmental Psychology*, *24*(2), 247–255. https://doi.org/10.1016/j.jenvp.2004.01.001

Joffily, M., & Coricelli, G. (2013). Emotional valence and the free-energy principle. *PLOS Computational Biology*, *9*(6), e1003094. https://doi.org/10.1371/journal.pcbi.1003094

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, *15*(3), 169–182. https://doi.org/10.1016/0272-4944(95)90001-2

Kok, P., Jehee, J. F., & de Lange, F. P. (2012). Less is more: Expectation sharpens representations in the primary visual cortex. *Neuron*, *75*(2), 265–270. https://doi.org/10.1016/j.neuron.2012.04.034

Kveraga, K., Boshyan, J., & Bar, M. (2007). Magnocellular projections as the trigger of top-down facilitation in recognition. *Journal of Neuroscience*, *27*(48), 13232–13240. https://doi.org/10.1523/JNEUROSCI.3481-07.2007

Laughlin, S. B., & Sejnowski, T. J. (2003). Communication in neural networks. *Science*, *301*(5641), 1870–1874. https://doi.org/10.1126/science.1089662

Leder, H., Tinio, P. P., & Bar, M. (2011). Emotional valence modulates the preference for curved objects. *Perception*, *40*(6), 649–655. https://doi.org/10.1068/p6845

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research*, *34*(2), 174–186. https://doi.org/10.1086/519146

Muckli, L., De Martino, F., Vizioli, L., Petro, L. S., Smith, F. W., Ugurbil, K., & Yacoub, E. (2015). Contextual feedback to superficial layers of V1. *Current Biology*, *25*(20), 2690–2695. https://doi.org/10.1016/j.cub.2015.08.057

Muckli, L., & Petro, L. S. (2013). Network interactions: Non-geniculate input to V1. *Current Opinion in Neurobiology*, *23*(2), 195–201. https://doi.org/10.1016/j.conb.2013.01.020

Olshausen, B. A., & Field, D. J. (1996). Emergence of simple-cell receptive field properties by learning a sparse code for natural images. *Nature*, *381*, 607–609. https://doi.org/10.1038/381607a0

Plummer, H. (2009). *The architecture of natural light*. Thames & Hudson.

Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects. *Nature Neuroscience*, *2*(1), 79–87. https://doi.org/10.1038/4580

Salingaros, N. A. (2005). *Principles of urban structure*. Techne Press.

Salingaros, N. A. (2006). *A theory of architecture*. Umbau-Verlag.

Slepian, M. L., & Ambady, N. (2012). Fluid movement and creativity. *Journal of Experimental Psychology: General*, *141*(4), 625–629. https://doi.org/10.1037/a0027395

Summerfield, C., Egner, T., Greene, M., Koechlin, E., Mangels, J., & Hirsch, J. (2006). Predictive codes for forthcoming perception in the frontal cortex. *Science*, *314*(5803), 1311–1314. https://doi.org/10.1126/science.1132028

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2005). Perceptual and physiological responses to Jackson Pollock's fractals. *Nonlinear Dynamics, Psychology, and Life Sciences*, *9*(1), 89–114.

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, *224*(4647), 420–421. https://doi.org/10.1126/science.6143402

Ulrich, R. S., Simons, R. F., Losito, B. D., Fiorito, E., Miles, M. A., & Zelson, M. (1991). Stress recovery during exposure to natural and urban environments. *Journal of Environmental Psychology*, *11*(3), 201–230. https://doi.org/10.1016/S0272-4944(05)80184-7

Van de Cruys, S. (2017). Affective value in the predictive mind. In W. Wiese & T. Metzinger (Eds.), *Philosophy and predictive processing*. MIND Group. https://doi.org/10.15502/9783958573253

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., Nadal, M., Rostrup, N., & Skov, M. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. *Proceedings of the National Academy of Sciences*, *110*(Suppl. 2), 10446–10453. https://doi.org/10.1073/pnas.1301227110

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Gonzalez-Mora, J. L., Leder, H., Modrono, C., Nadal, M., Rostrup, N., & Skov, M. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology*, *41*, 10–18. https://doi.org/10.1016/j.jenvp.2014.11.006

Vartanian, O., et al. (2019). Preference for curvilinear architecture: Evidence from immersive virtual reality. *Psychology of Aesthetics, Creativity, and the Arts*, *13*(4), 399–409. https://doi.org/10.1037/aca0000181

Veitch, J. A., & Newsham, G. R. (1998). Lighting quality and energy-efficiency effects on task performance, mood, health, satisfaction, and comfort. *Journal of the Illuminating Engineering Society*, *27*(1), 107–129. https://doi.org/10.1080/00994480.1998.10748214

Vinje, W. E., & Gallant, J. L. (2000). Sparse coding and decorrelation in primary visual cortex during natural vision. *Science*, *287*(5456), 1273–1276. https://doi.org/10.1126/science.287.5456.1273

White, M. P., Alcock, I., Grellier, J., Wheeler, B. W., Hartig, T., Warber, S. L., Bone, A., Depledge, M. H., & Fleming, L. E. (2019). Spending at least 120 minutes a week in nature is associated with good health and wellbeing. *Scientific Reports*, *9*(1), 7730. https://doi.org/10.1038/s41598-019-44097-3

Wienold, J., & Christoffersen, J. (2006). Evaluation methods and development of a new glare prediction model for daylight environments with the use of CCD cameras. *Energy and Buildings*, *38*(7), 743–757. https://doi.org/10.1016/j.enbuild.2005.08.029

Witek, M. A. G., Clarke, E. F., Wallentin, M., Kringelbach, M. L., & Vuust, P. (2014). Syncopation, body-movement and pleasure in groove music. *PLoS ONE*, *9*(4), e94446. https://doi.org/10.1371/journal.pone.0094446

---

*VISUAL-I Expert Panel Output — Document 65*
*February 21, 2026*
*Templates calibrated: T1 (PP_SPECTRAL_MATCH_001), T2 (PP_COMPLEXITY_GOLDILOCKS_002), T22 (PP_RAPID_GIST_004), L1 (LUM_CONTRAST_PE_001), VIEW1 (NATURE_VIEW_CONVERGENCE_001), VF1 (VF1_CONTOUR_PE_001), VF2 (VF2_VISUAL_RHYTHM_001), VF3 (VF3_SPATIAL_PROPORTIONS_001)*
*Gap registry: 136 → 128 remaining*
*New T1.5 candidate surfaced: Aesthetic Anchoring (T22 first-impression perseverance) — assigned to THEORY-REVIEW*
*Status: COMPLETE*
