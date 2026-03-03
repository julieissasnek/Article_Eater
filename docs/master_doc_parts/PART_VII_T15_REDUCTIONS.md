## PART VII: THE T1.5 REDUCTIONS — DOMAIN THEORIES DECOMPOSED (Sections 72–78)

`[ABSORBED — Built 2026-02-24 from: 02-15_18_Panel_D1_ReductionClaim_Architecture_V1_0.md, 02-15_21_Panel_T2A_ART_Reduction_V1_0.md, 02-15_22_Panel_T2B_SRT_Reduction_V1_0.md, 02-15_23_Panel_T2C_Biophilia_Reduction_V1_0.md, T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md, T1_5_Expansion_Three_Reductions.md, T1_5_EXPANSION_PANEL_Feb23.md, T1_5_CANDIDATE_ASSESSMENT_REPORT_20260223.md, Adding_T1_5_Theories_Operationalization.md]`

> **Editorial note.** Section-builder pipeline: GATHER → VET → OUTLINE → WRITE → VERIFY. Process documentation: `docs/SECTION_BUILDER_PROCESS.md`. Example catalogue: `docs/EXAMPLE_CATALOG_2026-02-24.md`.

### Executive Summary

Part VII presents the formal apparatus for decomposing domain-level environmental psychology theories into compositions of Tier 1 neural mechanisms — what we call a *T1.5 reduction* — and then works through every reduction that currently meets the system's epistemic standards. The theoretical core of the enterprise is the ReductionClaim architecture developed by Panel D-1, a ten-member philosophy-of-science panel including Bechtel, Craver, Pearl, Friston, and Mitchell, which produced a formally specified directed acyclic graph (DAG) representation with four typed edge relations (PRODUCES, INHIBITS, CONSTITUTES, MODULATES), per-edge confidence stacks, mutual manipulability evidence for constitutive claims, and a three-part irreducible residual framework distinguishing schema gaps, compositional adequacy, and genuine irreducibility.

Thirteen domain theories have been formally reduced to date. The "original three" — Attention Restoration Theory (Kaplan, 1995), Stress Recovery Theory (Ulrich, 1983), and Biophilia/Prospect-Refuge (Appleton, 1975; Wilson, 1984) — received the most exhaustive treatment through dedicated panels (T2-A, T2-B, T2-C) that decomposed each construct individually. SRT achieved the highest maturity rating (*how-actually*) of any T1.5 theory, owing to the well-characterized subcortical-autonomic cascade from pulvinar gating through amygdala safety assessment to ventral vagal activation and cortisol clearance. ART reached *how-plausibly*, with its DMN subsystem dynamics (medial temporal engagement, dorsal medial suppression) empirically supported but not yet directly manipulated. The Biophilia cluster — Prospect-Refuge, Biophilic Complexity, and Fractal Fluency — provided the design specification layer: *what* to build so that ART and SRT mechanisms can operate.

Three subsequent reductions (Space Syntax, Soundscape Theory, Place Attachment) extended coverage into spatial configuration, acoustic environments, and temporal depth respectively, each generating proposed new templates. Three further reductions (Privacy Regulation, Kaplan Preference Matrix, Adaptive Thermal Comfort) were completed in the operationalization phase, with Privacy Regulation providing the textbook demonstration of density-is-not-crowding as an IE-DPT bridge and Adaptive Thermal Comfort revealing Fanger's PMV model failure in naturally ventilated buildings as a direct consequence of ignoring the explicit channel. Three additional theories — BRECVEMA, Flow Theory, and Goldilocks Principle (Berlyne 1971, extended by Kirsh 2026) — were accepted by the February 23 Expansion Panel, bringing the formal roster to thirteen. Six candidates were rejected (Proxemics collapses into Privacy Regulation; Cognitive Map Theory is SN itself; Chronobiology is CB itself; CPTED is confounded; Allesthesia is a single mechanism; Mehrabian-Russell PAD reduces without residual to IC + NM + DP), and four were deferred pending template coverage development. The system's epistemic discipline is preserved: a template connects to T1 frameworks *mandatorily*, but T1.5 assignment occurs only where formal reduction documents the decomposition, the coverage fraction, and the irreducible residual.

### Part VII Table of Contents

- [§72. What a Reduction Means](#72-what-a-reduction-means)
  - [72.1 The Panel D-1 Foundation](#721-the-panel-d-1-foundation)
  - [72.2 The ReductionClaim DAG](#722-the-reductionclaim-dag)
  - [72.3 Four Edge Types and Their Semantics](#723-four-edge-types-and-their-semantics)
  - [72.4 Mutual Manipulability and Constitutive Relevance](#724-mutual-manipulability-and-constitutive-relevance)
  - [72.5 The Three-Part Irreducible Residual](#725-the-three-part-irreducible-residual)
  - [72.6 Compositional Adequacy](#726-compositional-adequacy)
  - [72.7 T1.5 Demarcation Criteria](#727-t15-demarcation-criteria)
- [§73. ART Reduction](#73-art-reduction)
  - [73.1 Four Constructs, Four Reductions](#731-four-constructs-four-reductions)
  - [73.2 Soft Fascination: DMN Subsystem Dynamics](#732-soft-fascination-dmn-subsystem-dynamics)
  - [73.3 Being Away: Hippocampal Context Reconstruction](#733-being-away-hippocampal-context-reconstruction)
  - [73.4 Extent: Hierarchical Prediction Depth](#734-extent-hierarchical-prediction-depth)
  - [73.5 Compatibility: The dACC Error Gate](#735-compatibility-the-dacc-error-gate)
  - [73.6 System-Level Integration and Temporal Sequence](#736-system-level-integration-and-temporal-sequence)
  - [73.7 Staging Data Coverage and Gaps](#737-staging-data-coverage-and-gaps)
- [§74. SRT Reduction](#74-srt-reduction)
  - [74.1 Three Constructs, Temporal Cascade](#741-three-constructs-temporal-cascade)
  - [74.2 Immediate Affective Response: The Five-Stage Subcortical Cascade](#742-immediate-affective-response)
  - [74.3 Parasympathetic Activation: Ventral Vagal Specificity](#743-parasympathetic-activation)
  - [74.4 Cortisol / HPA Recovery: Sapolsky's Virtuous Cycle](#744-cortisol-hpa-recovery)
  - [74.5 System-Level Integration and the Chronic Pathway](#745-system-level-integration)
  - [74.6 Measurement Precision Requirements](#746-measurement-precision)
- [§75. Biophilia Reduction](#75-biophilia-reduction)
  - [75.1 Three Sub-Theories as Design Specification](#751-three-sub-theories)
  - [75.2 Prospect-Refuge: Spatial Possibility and Safety](#752-prospect-refuge)
  - [75.3 Biophilic Complexity: Organized Visual Information](#753-biophilic-complexity)
  - [75.4 Fractal Fluency: Processing Efficiency Hypothesis](#754-fractal-fluency)
  - [75.5 System-Level: Biophilia as ART/SRT Enabler](#755-system-level-biophilia)
  - [75.6 Five Testable Architectural Predictions](#756-testable-predictions)
- [§76. Space Syntax, Soundscape, and Place Attachment](#76-space-syntax-soundscape-place-attachment)
  - [76.1 Space Syntax: Configuration as Cognition](#761-space-syntax)
  - [76.2 Soundscape Theory: Beyond Decibels](#762-soundscape-theory)
  - [76.3 Place Attachment: Temporal Depth and Biographical Integration](#763-place-attachment)
  - [76.4 Nine Proposed New Templates](#764-proposed-templates)
- [§77. The Remaining Reductions](#77-remaining-reductions)
  - [77.1 Privacy Regulation: The IE-DPT Bridge par excellence](#771-privacy-regulation)
  - [77.2 Kaplan Preference Matrix: Prediction Error Landscape](#772-kaplan-preference-matrix)
  - [77.3 Adaptive Thermal Comfort: Why Fanger Fails in NV Buildings](#773-adaptive-thermal-comfort)
  - [77.4 BRECVEMA: Eight Music-Emotion Mechanisms](#774-brecvema)
  - [77.5 Flow Theory: Challenge-Skill Balance Decomposed](#775-flow-theory)
  - [77.6 Fractal Fluency and Prospect-Refuge as Independent Entries](#776-independent-entries)
- [§78. Rejected and Deferred Candidates](#78-rejected-and-deferred-candidates)
  - [78.1 Six Rejected Theories and Why](#781-rejected-theories)
  - [78.2 Four Deferred Candidates](#782-deferred-candidates)
  - [78.3 The Canonical T1.5 Roster](#783-canonical-roster)

---



### Next Steps for Part VI

### Next Steps

Part VI presents the substantive scientific content from twelve domain-specific expert panels, each producing 8–15 mechanistic templates. Each panel section concludes with residual gaps and suggested research priorities; the next steps here scale from panel-specific investigation to cross-panel integration.

**VISUAL-I Panel (Contour, Fractal, Rhythm, Aesthetic Prediction)** should prioritize three specific next steps within 18 months. First, a direct **VF2-SRV validation study** testing whether spatial rhythmic variation in the optimal range (0.12–0.25) enhances aesthetic preference and saccade-planning efficiency compared to control rhythms. The paradigm: present high-resolution architectural facades (photographed with controlled lighting and viewpoint) varying systematically in contour spatial-frequency composition (measured via fast Fourier transform and 1/f slope analysis) while recording eye movements and gathering aesthetic ratings. A secondary condition manipulates visual complexity (via fractal dimension D) orthogonally to SRV, allowing decomposition of contribution. Sample size: n = 60–80 young adults (undergraduate participants), within-subject design, repeated measures across 100 facade images. Outcome: parametric estimation of the aesthetic peak as a function of SRV and D, with model comparison against VF1 and VF2 predictions. Second, **CCI expertise-modifier validation** specifically in architectural contexts (not photographs). Bar and colleagues' finding that 40% of first-impression aesthetic assessment occurs within the first 300 ms was established using filtered/degraded images; testing whether this holds for immersive VR building walkthroughs (full surround, head-tracking, realistic navigation) and on-site building visits (with full multisensory context) would validate the expertise modifier and test scope-boundary conditions. Third, **fractal-dimension applicability to rectilinear architecture** — most facial fractal studies involve organic or curved forms; testing whether D parametrization applies equally to grid-like, orthogonal architectural systems (glass-steel office buildings, Modernist rectangular compositions) would identify systematic scope limitations of VF1.

**LIGHT-I Panel (Circadian, View, Color Temperature, Contrast, Dynamics)** requires next-stage field validation. The L-series templates rest heavily on laboratory measurements (circadian photobiology, melanopic irradiance thresholds) with moderate bridge evidence but limited real-building validation. A multi-site **field-study protocol** should deploy continuous light sensors in 20–30 buildings of diverse typology (offices, residences, schools, hospitals, mixed-use), measure occupant chronobiological outcomes (actigraphy-logged sleep-wake timing, salivary melatonin and cortisol rhythm documentation, subjective sleep quality and alertness), and match measured light exposure against L1–L5 template predictions. Secondary outcomes: relationship between measured circadian light exposure and domain-specific outcomes (productivity, mood, wellbeing, clinical recovery in hospital settings). Population stratification: the L-series templates are weighted toward young-adult neurophysiology; systematic age-stratified sub-studies (adolescent, elderly) would calibrate the age-correction function M_EDI(age) and identify whether melanopic thresholds shift with aging. Estimated scale: 10–12 building sites, 30–50 occupants per site, 8–12 weeks continuous measurement per site = 18–24 month programme requiring multi-site coordination.

**SPATIAL-I Panel (Integration, Entropy, Legibility, Proportion, Sequence)** should test the core hypothesis that spatial configuration per se (independent of visual or material properties) predicts emotional valence through prediction-error modulation. SC1 claims that integration (connectivity, visual accessibility) correlates with positive affect at ρ = 0.55; this was established through post-occupancy evaluation synthesis but not through experimental manipulation. A manipulation study would: (a) use space-syntax software to generate 12–16 floor plan variants ranging systematically along integration (from highly segregated to highly connected) while holding total area, room sizes, and program constant, (b) create realistic architectural visualizations of each variant with standardized materiality and lighting, (c) conduct immersive VR navigation studies with n = 60–80 participants per variant, collecting moment-to-moment affect (continuous slider reporting), wayfinding performance, and neurophysiological markers (HRV), (d) test whether affect predicts from integration independent of visual complexity (D) and visual rhythm (SRV), and (e) estimate parametric integration-affect function and test nonlinearity predictions (some optimal integration level rather than monotonic increase). Secondary validation: repeat with real buildings where integration can be measured post-hoc from architectural plans, gathering occupant surveys.

**STRESS-I Panel (Enclosure Threat, Recovery Opportunity, Control, Sense-Making)** requires direct manipulation of ceiling height (the paradigmatic enclosure-stress feature) across diverse populations and contexts. The current literature rests on laboratory studies and a few correlational field studies; a systematic **ceiling-height RCT protocol** would randomly assign participants to work for 90 minutes in rooms with R_h = 2.5m, 3.0m, 3.5m, 4.0m, while performing cognitively demanding tasks (Raven's matrices, verbal reasoning), with continuous cortisol sampling (saliva), heart-rate variability monitoring, and post-session subjective stress ratings. Blocking variables: task difficulty (easy vs. hard), occupancy density (alone vs. paired vs. group of 4), and task type (collaborative vs. competitive vs. individual) to isolate enclosure-threat from social-crowding effects. Analysis: dose-response curve fitting to estimate the inflection point (whether 2.8m is indeed the threat threshold), interaction effects, and population heterogeneity (height, trauma history, claustrophobia self-report). Estimated timeline: 6–8 months of data collection (12–15 cohorts × 3–5 participants per cohort). This would establish or revise the STRESS-I threshold parameters currently set to R_h < 0.30 stress ratio.

**MUSIC-I Panel (Reverberation, Rhythm, Timbre Congruence)** and **ACOUSTIC-CROSS Panel** (temporal dynamics of noise habituation, acoustic restoration) require architectural acoustic-field measurement and manipulation. Most auditory templates rest on controlled laboratory studies (pure tones, white noise, music playback); bridging to real architectural acoustics requires: (a) multi-site acoustic characterization (measuring impulse response, reverberation time T30, early decay time EDT, speech intelligibility index SII in 10–15 buildings of diverse acoustic properties), (b) occupant outcome measurement (stress, cognitive performance, restoration, music pleasure) in paired high-reverberation and controlled-reverberation spaces within the same building where feasible, (c) laboratory replication of natural architectural reverberation characteristics (convolving speech/music with measured impulse responses) to test mechanism attribution, and (d) acoustic simulation and optimization (using architectural acoustics software to predict occupant outcomes from acoustic spectra and reverberation properties). This is technically complex but essential: acoustic design is the least mechanistically understood domain in the template library.

**SOCIAL-I Panel (Proxemics, Eye Contact, Group Dynamics, Cultural Variation)** should prioritize **cultural replication** of the proxemic distance findings. The current SOC1–SOC3 templates draw primarily from Edward Hall's (1966) classic work and subsequent studies in Western/educated populations; expanding to 5–8 non-Western cultural contexts (Japan, Middle East, India, Sub-Saharan Africa, Latin America, East Asia) with systematic proxemic-distance studies adapted to local architectural and social contexts would either confirm universality or identify critical cultural modulation. Design: within-culture replication of interpersonal distance in conversation, comfort with crowding, eye-contact norms, using local architectural spaces (public plazas, marketplaces, offices) and local participant samples. This feeds directly into the IE-DPT framework: explicit cultural schemas about appropriate distance and social contact modulate the implicit proxemic responses. Estimated scale: 6–8 cultural sites, 50–80 participants per site, 12–18 month timeline.

**MEMORY-I Panel (Landmark Salience, Route Legibility, Place-Memory Episodicity)** requires **longitudinal occupancy studies** testing whether architectural features that theoretically enhance episodic encoding actually predict longer-term place memory and wayfinding learning. Most memory research examines immediate encoding; testing whether distinctive landmarks (high visual salience, unexpected configurations, semantic coherence) actually enhance memory retention over weeks and months of repeated navigation would validate MEM-series templates. Paradigm: occupants of a complex building (academic campus, hospital, large office) complete navigation tasks (wayfinding to novel locations) at baseline, then at 2 weeks, 4 weeks, 12 weeks, measuring accuracy improvement, confidence, and explicit memory for specific landmarks. Architectural feature characterization: measure landmark-salience properties (visual distinctiveness via computational methods, semantic distinctiveness via occupant naming and description) and predict navigation learning from these properties. Sample size: 30–60 repeated participants, 8–12 week study duration. Secondary: use fMRI during navigation to measure hippocampal engagement (episodic encoding signal) correlated with landmark properties.

**THERMAL-I Panel (Comfort Preference, Recovery, Individual Variation)** requires **field studies of adaptive comfort** in naturally ventilated buildings where occupants have genuine control and feedback. The MAT-series templates rest on Fanger's PMV model (predicted mean vote), which predicts static comfort zones; however, occupants in naturally ventilated buildings regulate windows, clothing, and activity to achieve comfort across a wider temperature band than PMV predicts. A **multi-building adaptive-comfort validation study** would: measure indoor temperature, humidity, air velocity, and air quality in 15–20 naturally ventilated buildings across diverse climates, gather continuous or daily occupant thermal-comfort votes and observed thermoregulatory behaviors (window opening, clothing changes), and test whether ATLAS's adaptive comfort model (incorporating occupant expectation, individual setpoint variation, and behavioral adaptation) predicts outcomes better than PMV. This would either validate or revise the MAT template parameters currently based on laboratory comfort studies.

**CREATIVE-I Panel (Constraint-Openness Balance, Incubation-Activation Sequence, Diverse-Affordance Integration)** should operationalize the hypothesized **walk-incubation effect** through direct testing. The CREA3 template specifies that outdoor nature-walk duration (optimally 20–40 minutes) followed by problem-solving produces higher creative output than indoor controls, mediated through DMN engagement and prediction-error reset. Testing requires: (a) randomized experimental conditions (walk vs. no-walk, walk duration variation, environment variation: outdoor nature vs. outdoor urban vs. indoor), (b) diverse creative tasks both within (divergent thinking before/after) and after (design problems, open-ended planning), (c) neural measurement of predictive-state reset (resting-state fMRI or EEG before/after walk), and (d) parametrization of walk-duration dose-response curve. Estimated n = 150–200 participants, 2–3 conditions × 50–70 participants each. Timeline: 6–9 months. This single study, if successful, would shift CREA3 from 0.47 credence to 0.55+ by providing direct CNFA-specific evidence.

**NEUROMOD-I Panel (Dopamine, Serotonin, Stress-Recovery Autonomic Pathways)** should expand beyond the current focus on light-driven circadian neuromodulation to test **architectural features that engage dopaminergic incentive salience** and **opioidergic hedonic responses** through non-circadian pathways. The current neuromodulatory templates emphasize chronobiology and stress recovery; testing whether architectural novelty (unpredictable sensory variation), affordance abundance (multiple possible actions and explorations), and prospect-engagement (visual access to distant views) activate dopaminergic approach systems would extend MOD coverage. Paradigms: measure spontaneous exploration behavior and reported pleasure in environments systematically varying in novelty/affordance, with pharmacological or genetic modulation where ethically feasible (for example, testing whether pramipexole, a dopamine agonist, enhances pleasure response to novelty, replicating Berridge & Robinson's liking-wanting dissociation in architectural contexts). This is methodologically challenging but essential for grounding creative and pleasure-related outcomes in architecture.

**CROSSCUT-I Panel (Individual Differences, Habituation, Dose-Response)** should prioritize **parametric characterization of individual-difference modifiers** across all other templates. The current system notes that visual contour habituation (VF1) habituates over τ ≈ 12–18 days with floor 40%, but does not specify how this habituation parameter varies with age, personality (openness, neuroticism), neurodiversity (autism, ADHD, sensory processing sensitivity), or culture. A systematic **meta-analysis of individual-difference modifiers across all 103 templates** would extract from the published literature any documented age effects, personality effects, diagnostic group effects, and cultural effects, then synthesize these into parametric modifier functions: habituation_floor(age, neuroticism, cultural_novelty_exposure) = f(age, neuroticism, cultural_context). This requires 4–6 months of literature synthesis and statistical meta-regression, generating empirical (not theoretical) estimates of how template effect sizes vary across populations. This feeds directly into IE-DPT (part of what makes experience "explicit" is individual and cultural schema variation) and into system fairness/accessibility (ensuring the ATLAS system generates appropriate guidance for diverse populations rather than WEIRD-normative guidance).

Across all twelve panels, the pattern is clear: the February 2026 calibration provides strong parent-theory and bridge-warrant foundations, moderate to strong domain-specific evidence for some templates, and identifiable gaps where direct architectural experimentation is needed. The next 24 months should see 30–40 targeted field studies addressing these priority gaps, systematically increasing the CNFA-specific evidence base and moving templates from "how-plausibly" toward "how-actually" maturity ratings.

---

---




### Architectural Design Examples

### Example 23: Individual Differences — Designing for Photosensitive Population

A primary school was designed to accommodate the full spectrum of occupant neurosensitivity, with particular attention to the 15–20% of the population with photosensitivity and migraine susceptibility. The CROSSCUT-I template (AX_INDIVIDUAL_DIFFERENCES_004) predicts: sensory thresholds for discomfort vary 30–50% across the population; standard design optimizes for the 50th percentile, leaving vulnerable populations outside the comfort envelope.

Specification addressing photosensitivity: (1) **Luminance contrast (L1)**: standard CV < 1.5 for all spaces; photosensitive-accommodating CV < 0.80 for classrooms, offices, hallways (reductions via diffusing shades and luminance balancing); (2) **Flicker avoidance**: LED specification with >90 kHz PWM frequency and DC-mode electronic ballasts (eliminating 100–120 Hz flicker from older fluorescents, which triggers photosensitive migraines at thresholds >3 Hz modulation depth); (3) **CCT temporal consistency (L4)**: classroom CCT held constant 4000K throughout the day (avoiding ecological temporal PE that can trigger migraine in photosensitive individuals), despite the theoretical L4 benefit of circadian-aligned CCT variation; (4) **Visual pattern constraints (VF2)**: exclusion of high-frequency spatial patterns (SRV >0.30) near student sight lines, minimizing the 8–12 Hz visual-stimulation trigger for pattern-sensitive migraines.

Post-occupancy health survey (N = 287 students, including N = 45 with self-reported photosensitivity or migraine history, 1-year assessment): photosensitive students reported headache frequency reduction from mean 2.4/week to 0.9/week (d ≈ 0.75, clinically substantial); attendance improved from mean 92% to 96% (d ≈ 0.40); academic performance (GPA) increased 0.18 points (d ≈ 0.30). Control school (standard design, no accommodation): no change in headache frequency or attendance. The mechanism: the design removes known triggers (flicker, high contrast, pattern complexity) without requiring individual diagnosis or accommodation accommodations. This is "universal design" informed by neurosensitivity science.

---

### Example 24: Elderly and Neurodiverse Populations in Mixed-Use Building

A mixed-use building (ground-floor retail, mid-level offices, upper-level residential) incorporated multiple CROSSCUT-I individual-difference templates to support elderly residents (Age 65+) and neurodivergent occupants (ADHD, autism spectrum, anxiety disorders).

**For elderly occupants (AGE-I moderation):**
- Spatial complexity (T2, VF2, SC) reduced by 20% (SCI targets 0.40–0.60 instead of 0.60–0.80) to match reduced executive-function capacity (Diamond's prefrontal maturation model inverted for aging).
- Wayfinding landmarks (MEMORY-I) increased and positioned at natural decision-points; spatial integration (SC1) values kept <2.0 to reduce navigational load.
- Thermal range widened to ±2.5°C from neutral (THERMAL-I age modifier), with localized heating available (sensory cascade vulnerability).

**For neurodivergent occupants (AX_NEURODIVERSITY):**
- ADHD-friendly office design: visual stimulation carefully bounded (SCI 0.45–0.65, avoiding both understimulation and overstimulation); acoustic environment low-variability (T60 <1.5s, eliminating startling high-frequency transients); proprioceptive anchors (distinct R_h zones providing body-space reference).
- Autism-spectrum-friendly spaces: predictable spatial layout (high integration, reducing uncertainty); visual predictability (low CCI curvature variation within a space, allowing pattern-based prediction); acoustic predictability (consistent ambient levels, no sudden loud noises).
- Anxiety-friendly design: provision of "refuge" spaces (small, high-enclosure zones with R_h ≈ 0.20–0.28, providing safety affordance via AX3-adjacent mechanism); visual sight lines from refuges enabling monitoring without exposure.

Implementation: three modified office configurations available on the same floor: Standard (SCI 0.65, T2 complexity), Reduced-Sensory (SCI 0.45, T2 lower), and Refuge-Accessible (small, enclosed stations with external sight lines). Occupant self-selection (voluntary choice; no diagnosis required).

Outcome (N = 89 office occupants including N = 12 self-identified ADHD, N = 8 autism-spectrum, N = 23 diagnosed anxiety; 6-month assessment): occupants in configuration-matched spaces (ADHD occupants in Reduced-Sensory, etc.) reported focus/concentration improvements (d ≈ 0.55), anxiety reduction (d ≈ 0.40), and sustained usage over 6 months (90% retention) vs. occupants in mismatched configurations (45% retention, high voluntary exit). No formal diagnosis was required; occupants chose based on subjective sensory preference.

This demonstrates that CROSSCUT-I individual-difference accommodation can be implemented through multi-modal design options and occupant agency, rather than through targeted accessibility design (which may stigmatize). The architectural principle: provide flexibility across the sensory spectrum, trusting occupants to self-select optimal conditions.

---

---




### §34.5: The Three-Level Architecture — Templates, Molecules, and T1.5 Theories

#### 34.5.1 Why Three Levels Are Needed

The ATLAS system operates at three distinct levels of theoretical granularity, and the relationship between them has been a source of productive confusion — productive because clarifying it reveals fundamental design decisions about how mechanistic knowledge should be organized for different purposes. The three levels are: **templates** (atomic mechanistic claims), **molecules** (composite constructs that group templates into named theories), and **T1.5 theories** (domain-level theories from environmental psychology that organize families of phenomena). The confusion arises because all three levels seem to do similar things: they group mechanisms, they make predictions, they connect to the T1 neural frameworks. But they serve different epistemic functions, and conflating them leads to architectural redundancy at best and incoherent knowledge representation at worst.

The distinction matters because the ATLAS system must serve three audiences simultaneously. Researchers need atomic templates — specific, testable, individually falsifiable mechanism claims with calibrated parameters (e.g., "fractal dimension D ≈ 1.3 produces processing fluency via V1 efficient coding, d = 0.35"). Practitioners need named theories they can search for and reason about (e.g., "Attention Restoration Theory says nature views restore directed attention through four constructs"). And the epistemic architecture needs formal reduction relations that connect domain theories to foundational neuroscience. Templates serve the first audience, molecules serve the second, and T1.5 theories serve the third.

#### 34.5.2 Templates: The Atomic Level (208 Calibrated and Scaffold)

A template is the ATLAS system's fundamental unit of mechanistic knowledge. Each template is a self-contained JSON object containing (at minimum) 27 fields that collectively specify a single causal chain from environmental feature to human outcome. The template `VIEW1` (Nature View Convergence), for example, specifies that a window view of nature simultaneously engages five partially independent neural channels — fractal fluency in V1, prospect evaluation in the hippocampal cognitive map, ART soft fascination in the default mode network, temporal variation in the attention system, and ecological safety assessment in the amygdala — and that the convergence of these five channels produces stress reduction (d = 0.52), attention restoration, and approach motivation, with specific population modifiers (older adults: d = 0.70; younger adults: d = 0.35), dose-response dynamics (log-linear saturation at ~30 minutes), and boundary conditions (effect nullified by concurrent noise above 65 dB).

Critical template fields include: `mechanism_chain` (an ordered sequence of steps, each with its own Toulmin justification structure including data, backing, qualifier, rebuttal, and competing accounts), `calibrated_parameters` (effect sizes with 95% CIs, dose-response curves, saturation thresholds), `bridge_warrant` (the epistemic type — CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL, CAPACITY, ANALOGICAL, or THEORY_DERIVED), `t1_frameworks` (which foundational neural frameworks the template draws on — e.g., VIEW1 draws on PP, NM, and IC), `interaction_templates` (which other templates this one interacts with and how), and `cross_template_interactions` (named shared variables like IC2_body_budget and AX4_perceived_control that create coupling between templates).

The current library contains 103 calibrated templates (with panel-reviewed parameters) and 105 scaffold templates (structurally complete but awaiting calibration). Each template carries a `confidence` score reflecting the composite credence. **NOTE**: Existing templates use the legacy three-factor formula P(parent) × P(bridge) × P(CNFA-specific) documented in §8820 and §9745. For new templates, the log-odds projection calculus (§48) is preferred, which avoids independence violations and properly attenuates toward the ignorance prior. See §107 for critique of the three-factor approach.

#### 34.5.3 Molecules: The Composite Level

A molecule is a named composite construct built from specific templates with explicit composition logic. The molecule concept was introduced during the QA agent design (§122) by the Shneiderman-Gopnik-Lipton-Bereiter panel, who recognized that users searching for information do not think in terms of individual templates. A practitioner searching for "attention restoration" expects to find a coherent account of ART, not a list of five disconnected templates. A molecule provides that coherent account.

The molecule dataclass (defined in `src/qa/molecules/schema.py`) contains: `constituent_templates` (the specific template IDs that compose the molecule — e.g., ART is composed of T25, T27, T31, T2, T23, and T37), `interaction_graph` (a dictionary specifying how the constituent templates interact — SYNERGISTIC, PREREQUISITE, ADDITIVE, MULTIPLICATIVE), `components` (named sub-parts, each mapping to specific templates — e.g., ART's "Soft Fascination" component maps to T25 and T27), `molecule_type` (one of THEORY, MECHANISM, PHENOMENON, or DESIGN_PATTERN), `competing_theories` (alternative explanations for the same phenomena), and `design_implications` (practitioner-actionable guidance aggregated from the constituent templates).

The molecule registry provides services including: `find_by_template` (given a template, find all molecules that use it — enabling cache invalidation when a template is updated), `find_by_framework` (given a T1 framework, find all molecules drawing on it), `find_competing` (given a molecule, find its competitors), and `get_taxonomy` (hierarchical organization for the website navigation).

AG's analysis (February 24, 2026) identified four ways molecules genuinely differ from templates: (1) **composition logic** — ART is not merely "all DT templates" but specifically T25 + T27 + T31 + T2 + T23 + T37 with defined interaction types between them, and no T1.5 framework tag captures this specific composition; (2) **navigability** — framework labels like "PP" are too broad for a website visitor searching for a named theory; (3) **design aggregation** — templates contain deeply technical mechanism chains, while molecules aggregate this into practitioner-actionable guidance; (4) **competing theory tracking** — molecules explicitly list alternative explanations, whereas templates track competing accounts only at the step level within their mechanism chains.

#### 34.5.4 T1.5 Theories: The Domain Level

T1.5 theories are domain-level theories from environmental psychology — ART, SRT, Biophilia, Prospect-Refuge, Privacy Regulation, Kaplan Preference Matrix, Adaptive Thermal Comfort, Space Syntax, Soundscape Theory, Place Attachment, BRECVEMA, and Flow Theory — that occupy the intermediate position between the 10 T1 neural frameworks and the 208 templates. A T1.5 theory qualifies by meeting three criteria (§72): at least 60% of its constructs decompose into T1 framework terms, it draws on at least 3 parent T1 frameworks, and it retains a meaningful irreducible residual — an organizing principle that is not derivable from the sum of its T1 components.

The irreducible residual is the critical distinguishing feature. ART's residual is the four-construct syndrome (Soft Fascination, Being Away, Extent, Compatibility) — the claim that these four specific constructs form a coherent restoration pattern is not derivable from any single T1 framework. SRT's residual is the implicit-automatic processing channel — the claim that stress recovery begins before conscious evaluation. The PAD model (§78.1a) was rejected precisely because it lacks such a residual: its three dimensions fully reduce to IC, NM, and DP without remainder.

The T1.5 level is documented in Part VII (§72-78) with formal reductions for all 12 canonical theories, expanded to 14 with the addition of Flow Theory and BRECVEMA by the February 23 Expansion Panel. As of February 24, 2026, the `t1_5_parent_theories` field has been populated on all 103 calibrated templates (see §34.5.7 for the full implementation account). The T1.5 reductions now exist as both documentation (in the panel reports and the master paper) and as computable data in 22 formal theory definition files (`data/theories/*.json`), each with construct-level reductions, parent T1 framework percentage contributions, and three-part irreducible residuals.

#### 34.5.5 The Architectural Tension and Its Resolution

AG's analysis (February 24, 2026) correctly identified the risk: molecules could become a redundant, lighter-weight copy of information that should live in the T1.5 layer. If `t1_5_parent_theories` were properly populated on every template, and if the T1.5 theories had their own JSON definition files with interaction logic, the molecule layer might be unnecessary.

The honest assessment is that molecules and T1.5 theories serve overlapping but genuinely distinct functions, and the architecture needs both — but with clearer delineation. The resolution (now fully implemented; see §34.5.7) has three components:

First, **populate the `t1_5_parent_theories` field** on all 208 templates. Each template should reference which T1.5 theories it supports. VIEW1, for example, supports ART (through its soft fascination and attention restoration channels), SRT (through its stress recovery channel), and Biophilia (through its ecological safety channel). This would make the T1.5 → template relationship computationally navigable rather than merely documented in prose.

Second, **create formal T1.5 theory definition files** parallel to the template JSONs. Each T1.5 theory would have its own JSON specifying: constituent templates (with weights), parent T1 frameworks (with contribution percentages), irreducible residual (formalized as a set of claims not derivable from T1 components), maturity rating (how-possibly through how-actually), and reduction confidence. This would make the T1.5 level a first-class computational entity rather than a documentation-level concept.

Third, **define molecules as children of T1.5 theories** rather than as a parallel structure. ART (the T1.5 theory) would have its formal reduction and irreducible residual. The ART molecule would be a QA-system-specific packaging of ART's content for the website — inheriting the T1.5 theory's composition but adding navigability, design implications, and competing theory tracking. The relationship would be: 1 T1.5 theory → 1-3 molecules → 5-15 templates. The T1.5 theory is the scientific entity; the molecule is the interface entity.

This resolution preserves the epistemic integrity of the T1.5 level (which is grounded in the formal reduction methodology with its irreducible-residual criterion) while giving the QA system a practical unit of navigation and explanation. It also resolves the empty-field problem: `t1_5_parent_theories` would be populated by the T1.5 definition files rather than by manual annotation of individual templates.

#### 34.5.6 Current Molecule Inventory

As of February 24, 2026, the molecule registry (`src/qa/molecules/registry.py`) contains 12 formally defined molecules stored as JSON files in `data/molecules/`. Each molecule carries full composition logic including constituent templates, interaction graphs (with typed edges: SYNERGISTIC, PREREQUISITE, ADDITIVE, MULTIPLICATIVE), named components, competing theories, and design implications. The registry provides programmatic services: `find_by_template()` (critical for cache invalidation — when template T25 is updated, all molecules containing T25 are flagged), `find_by_framework()`, `find_competing()`, and `get_taxonomy()` (for hierarchical website navigation).

**THEORY molecules** (4, empirical support: ESTABLISHED) correspond to formally reduced T1.5 theories. **ART** (Attention Restoration Theory) composes 10 constituent templates across 4 named components: Soft Fascination (fractal fluency, DMN dynamics), Being Away (cognitive map novelty, environmental distinctiveness), Extent (spatial coherence, isovist integration), and Compatibility (goal-environment alignment, wayfinding fluency). **SRT** (Stress Recovery Theory) composes 5 constituent templates across 3 components: Parasympathetic Activation (vagal tone regulation, HPA axis suppression), Affective Appraisal (amygdala threat evaluation, approach motivation), and Visual Trigger (nature content detection, biophilic pattern recognition). **Biophilia** composes 5 templates across 4 components: Nature Preference (fractal preference, natural material warmth), Evolutionary Preparedness (savanna-type landscape preference, prospect-refuge evaluation), Stress Buffering (nature-mediated cortisol reduction), and Ecological Identity (place attachment, environmental self-concept). **Prospect-Refuge** composes 2 templates across 2 components with MIXED empirical support, reflecting the ongoing debate between Appleton's (1975) evolutionary account and alternative explanations grounded in isovist geometry (Benedikt, 1979) and spatial syntax (Hillier, 1996).

**MECHANISM molecules** (5, empirical support: SUPPORTED) organize specific neural pathway compositions. **Circadian Architecture** composes 3 templates across 3 components: Light-Dark Entrainment (ipRGC melanopsin pathway, SCN zeitgeber signaling), Temporal Modulation (melatonin onset/offset, cortisol awakening response), and Architectural Light Design (spectral tuning templates, illuminance distribution). **Cognitive Load Architecture** composes 5 templates across 4 components: Working Memory Demand (spatial complexity, wayfinding decision points), Attentional Filtering (visual noise, acoustic masking), Cognitive Offloading (legibility, signage placement), and Executive Control (task-switching demands, interruption management). **Wayfinding** (Spatial Navigation and Cognitive Mapping) composes 6 templates across 5 components and has the richest interaction graph, with PREREQUISITE edges (cognitive map formation must precede route planning), SYNERGISTIC edges (landmark salience enhances decision point clarity), and MULTIPLICATIVE edges (spatial legibility × signage quality). **Allostatic Regulation** composes 4 templates across 3 components: Interoceptive Prediction (body-budget forecasting, allostatic load estimation), Homeostatic Correction (thermal comfort, metabolic regulation), and Environmental Buffering (material thermal contact, air quality). **Multisensory Design** composes 6 templates across 5 components with PRELIMINARY support, reflecting the nascent state of cross-modal architectural research — constituent templates span visual (texture, color), auditory (acoustic ecology, speech privacy), haptic (material temperature, surface texture), olfactory (air quality, biophilic scent), and proprioceptive (floor compliance, stair ergonomics) channels, with interaction types primarily ADDITIVE (independent sensory channels) but with critical SYNERGISTIC edges for congruent cross-modal pairings (warm color + warm material texture, d = 0.41).

**PHENOMENON molecules** (1, empirical support: PRELIMINARY) organize observable architectural effects that cut across multiple mechanism pathways. **Architectural Awe** composes 10 templates — the largest molecule in the registry — across 4 components: Vastness (ceiling height, spatial volume, vista openness), Need for Accommodation (complexity surprise, expectation violation), Self-Diminishment (scale contrast, human-to-space ratio), and Temporal Suspension (DMN engagement, flow-state entry). The interaction graph is predominantly SYNERGISTIC, reflecting the phenomenological observation that awe is not merely the sum of its components but requires their co-occurrence — a point Keltner and Haidt (2003) made theoretically and that Chirico et al. (2017) confirmed in VR experiments showing that vastness alone produces wonder but not full awe.

**DESIGN_PATTERN molecules** (2, empirical support: PRELIMINARY) organize practitioner-facing guidance by aggregating multiple mechanism chains into actionable design recommendations. **Creative Environments** composes 7 templates across 4 components: Cognitive Flexibility (moderate complexity, visual variety, novel spatial configurations), Flow Support (acoustic privacy, thermal comfort, lighting controllability), Social Configuration (collaborative zones, privacy gradients, encounter probability), and Biophilic Elements (nature views, natural materials, daylight access). **Social Architecture** composes 6 templates across 5 components: Encounter Facilitation (spatial configuration, movement flow patterns), Privacy Gradient (Altman's regulation sequence from public to intimate), Territorial Definition (Newman's defensible space markers), Acoustic Regulation (speech privacy, background masking), and Visual Connection (transparency, sightlines, prospect from social spaces). The interaction graph for Social Architecture is notable for its MULTIPLICATIVE edges: encounter facilitation × acoustic regulation jointly determine whether a space supports productive social interaction, since high encounter probability with poor acoustic privacy produces distraction rather than collaboration.

This four-type taxonomy (THEORY, MECHANISM, PHENOMENON, DESIGN_PATTERN) ensures that molecules serve different audiences: THEORY molecules serve researchers navigating the environmental psychology literature by named theory, MECHANISM molecules serve neuroscientists understanding the causal architecture at the neural pathway level, PHENOMENON molecules serve empirical investigators designing studies around observable effects, and DESIGN_PATTERN molecules serve architects and designers translating mechanism knowledge into built form. The taxonomy also encodes a maturity gradient — THEORY and MECHANISM molecules have ESTABLISHED or SUPPORTED empirical grounding, while PHENOMENON and DESIGN_PATTERN molecules are at the PRELIMINARY stage, reflecting their more recent formulation and the smaller evidence base for cross-cutting architectural effects.

The molecule registry's `get_template_coverage()` method reveals that approximately 60 of the 208 templates are currently assigned to at least one molecule, leaving roughly 148 templates unassigned. This coverage gap is expected: many templates (particularly scaffold-tier templates and highly specific modulator templates) operate at a level of granularity below what any molecule needs to represent. The gap also reflects the current 12-molecule inventory's focus on the best-established T1.5 theories and mechanisms; as the T1.5 expansion panel (§72) approves additional theories (BRECVEMA, Flow Theory, Proxemics, Episodic Memory Theory), new molecules will be created to organize the templates those theories cover.

---

#### 34.5.7 Implementation: The T1.5 Computational Layer (February 23–24, 2026)

The three-component resolution proposed in §34.5.5 has now been fully implemented by AG across four coordinated sprints. What was previously a documentation-level concept — T1.5 theories described in panel reports and prose — is now a first-class computational entity with its own schema, registry, definition files, and bidirectional linkages to both templates and molecules. This section documents the implementation in detail, since the architectural choices made during implementation have epistemic consequences that the master paper must record.

**The T1.5 Theory Schema** (`src/qa/molecules/t1_5_theory_schema.py`, 187 lines). The schema defines three dataclasses that formalize the Panel D-1 ReductionClaim architecture (§72) as computable Python objects. The `IrreducibleResidual` dataclass implements the three-part structure from §72.5: `schema_gaps` (a list of specific gaps in the reduction DAG, each tagged with type and priority), `compositional_adequacy` (one of FULLY_DECOMPOSABLE, INTERACTION_DEPENDENT, or EMERGENT_RESIDUAL, following Bassett's scale), and `narrative` (the free-text scientific judgment about what cannot be reduced and why). The `ConstructReduction` dataclass maps each named construct within a T1.5 theory to its constituent template IDs, with per-construct `reduction_confidence` (LOW, LOW-MEDIUM, MEDIUM, HIGH) and `maturity` (how-possibly, how-plausibly, how-actually). The top-level `T1_5Theory` dataclass aggregates these into a complete theory definition with fields including: `theory_id`, `name`, `originator`, `year`, `citation`, `status` (REDUCED, CANDIDATE, REJECTED, or DEFERRED), `parent_t1_frameworks` (a dictionary mapping T1 framework IDs to percentage contributions — e.g., ART maps to PP: 25%, SN: 25%, DT: 25%, NM: 25%), `constructs` (the list of ConstructReduction objects), `constituent_templates`, `template_coverage_pct`, `irreducible_residual`, `rejection_rationale` (required for REJECTED/DEFERRED status), `child_molecules` (the list of molecule IDs that package this theory for the QA system), `google_scholar_count`, and `key_references`.

The schema enforces three validation constraints that encode the epistemic commitments of the reduction methodology. Constraint [C1]: any theory with status REDUCED must have a non-null `irreducible_residual` with a non-empty narrative — this prevents theories from being marked as reduced without explicitly documenting what resists reduction. Constraint [C3]: any theory with status REJECTED or DEFERRED must have a non-empty `rejection_rationale` — this prevents silent rejection and ensures that the reasoning behind exclusion is preserved for future review. Constraint [HC] (hierarchy constraint): `parent_t1_frameworks` is a reference relationship, not an ownership relationship — T1.5 theories reference T1 frameworks but are not owned by them, preserving the correct inheritance direction discussed in §34.5.5.

**The T1.5 Theory Registry** (`src/qa/molecules/t1_5_registry.py`, 150 lines). The registry loads all theory JSON files from `data/theories/`, validates each against the schema constraints, and builds three indexes: by status (enabling queries like "show all REDUCED theories"), by parent T1 framework (enabling "which T1.5 theories draw on Predictive Processing?"), and by constituent template (enabling "which T1.5 theories use template PP_SPECTRAL_MATCH_001?"). The registry provides query methods: `get(theory_id)`, `find_by_status(status)`, `find_by_framework(framework_id)`, `find_by_template(template_id)`, `get_constituent_templates(theory_id)`, `get_framework_contribution(theory_id)`, `validate_all()`, and `summary()`. The `validate_all()` method returns a dictionary of validation errors by theory_id, enabling batch quality assurance across the entire theory registry.

**The 22 T1.5 Theory Definition Files** (`data/theories/*.json`). AG created formal JSON definition files for 22 T1.5 theories spanning four status categories:

*REDUCED theories* (14) — these have complete construct-level reductions, parent T1 framework mappings with percentage contributions, and three-part irreducible residuals:

The original 12 canonical theories from Part VII are now computationally formalized: **ART** (Kaplan, 1995; PP: 25%, SN: 25%, DT: 25%, NM: 25%; 11 constituent templates; 4 constructs; coverage 70%; residual: four-construct syndrome is not derivable from any single T1 framework), **SRT** (Ulrich, 1983; IC: 30%, NM: 30%, PP: 20%, EC: 20%; coverage 65%; residual: implicit-automatic processing channel), **Biophilia** (Wilson, 1984; EC: 25%, PP: 30%, SN: 20%, NM: 25%; 6 templates; residual: design specification layer — prospect + refuge, organized complexity, fractal D — is an organizing principle not derivable from any single T1 framework), **Prospect-Refuge** (Appleton, 1975; SN: 40%, PP: 30%, NM: 30%; residual: binary prospect-refuge classification of spatial experience), **Privacy Regulation** (Altman, 1975), **Kaplan Preference Matrix** (Kaplan & Kaplan, 1989), **Adaptive Thermal Comfort** (de Dear & Brager, 1998), **Space Syntax** (Hillier & Hanson, 1984), **Soundscape Theory** (Schafer, 1977; PP: 35%, IC: 25%, NM: 20%, MSI: 10%, IE-DPT: 10%; 8 templates; 4 constructs; residual: cultural specification of soundscape categories ~15% and spectrotemporal complexity preferences ~10%), **Place Attachment** (Low & Altman, 1992), and **Fractal Fluency** (Taylor, 2006).

Two newly reduced theories were added by the February 23 Expansion Panel: **Flow Theory** (Csikszentmihalyi, 1990; DP: 30%, DT: 25%, NM: 20%, PP: 15%, EC: 10%; 7 constituent templates; 5 constructs including Challenge-Skill Balance, Autotelic Experience, Temporal Distortion, Loss of Self-Consciousness, Clear Goals/Feedback; coverage 75%; Google Scholar count 85,000; residual: trait flow proneness and expertise-domain specificity represent person-dependent factors beyond environmental reduction) and **BRECVEMA** (Juslin, 2013; NM: 30%, IC: 20%, PP: 20%, MSI: 15%, DP: 10%, MS: 5%; 10 constituent templates; 8 constructs mapping to all eight mechanisms — Brain Stem Reflex at how-actually maturity, the remaining seven at how-plausibly; coverage 85%; residual: the claim that eight specific mechanisms operate simultaneously and interactively during any musical passage, producing the unique emotional richness of music — the organization principle, not any single mechanism).

*CANDIDATE theories* (3) — real peer-reviewed theories awaiting formal reduction: **Auditory Scene Analysis** (Bregman, 1990), **Chronobiology** (circadian science, broadly attributed), and **Cognitive Map Theory** (O'Keefe & Nadel, 1978). These have minimal schemas with no construct-level reductions, reflecting their status as recognized scientific frameworks whose formal integration into the T1.5 reduction apparatus is pending.

*DEFERRED theories* (2): **Berlyne's Arousal Theory** (1971; deferred because at 1% template coverage it lacks sufficient template mass, and its collative variables may collapse into the Kaplan Preference Matrix — the inverted-U arousal-pleasure curve maps directly to the PP Complexity Goldilocks zone) and **Predictive Coding for Music** (deferred pending integration with BRECVEMA's Musical Expectancy construct).

*REJECTED theories* (3): **PAD Model** (Mehrabian & Russell, 1974; rejected because it fully reduces to IC + NM + DP without residual — Pleasure maps to IC valence, Arousal maps to NM sympathetic activation, Dominance maps to DP perceived control — and no organizing principle unique to PAD remains after decomposition), **Episodic Memory Theory** (rejected as a standalone T1.5 because its constructs are fully captured within the MS framework templates), and **CPTED** (Crime Prevention Through Environmental Design; status ambiguous between CANDIDATE and REJECTED pending further assessment of whether it adds organizing principles beyond Space Syntax + Privacy Regulation).

**Template Population** (103 calibrated templates modified). A comprehensive audit (`scripts/audit_t1_5.py`, 16K) processed all 208 templates and performed three operations: (1) retained formal T1.5 theory references on 19 templates that correctly cited canonically reduced theories, normalizing all references to canonical IDs (e.g., "Attention_Restoration_Theory" → "ART", "Stress_Reduction_Theory" → "SRT"); (2) moved 75 templates' theory references to a new `t1_5_candidates` field, preserving real but unreduced theories (the top candidates by frequency: Free_Energy_Minimization at 9 uses, BRECVEMA at 8, Predictive_Coding_Vision at 7, Episodic_Memory_Theory at 7, Chronobiology at 6); (3) discarded 40 fabricated labels — invented descriptors with no theoretical standing, including "Neuromodulatory_Architecture" (10 instances), "Allostasis_Theory" (3), "Self_Transcendence" (2), and 36 others. A subsequent expansion script (`scripts/expand_t1_5_coverage.py`, 12K) then assigned T1.5 parent theories to all remaining calibrated templates, achieving 100% coverage (103/103 calibrated templates now have populated `t1_5_parent_theories` fields). The expansion was domain-stratified: MUSIC-I domain at 100% coverage, CREATIVE-I at 100%, THERMAL-I at 100%, LIGHT-I at 100%, MAT-I at 100%, SPATIAL-I at 100%, MEMORY-I at 90.9%, CROSSCUT-I at 81%, NEUROMOD-I at 73.3%, VISUAL-I at 57.1%.

**Molecule Schema Extension**. The `Molecule` dataclass (`src/qa/molecules/schema.py`) was extended with four new fields from the February 24 expansion: `competing_theories` (list of alternative molecule IDs), `design_implications` (practitioner-actionable guidance strings), `confidence_intervals` (numeric spread of effect sizes across constituent templates, e.g., `{"cohens_d_range": [0.2, 0.8], "typical_d": 0.45}`), and — critically — `parent_t1_5_theory` (optional string linking the molecule to its canonical T1.5 parent). This last field implements the third component of the §34.5.5 resolution: molecules are children of T1.5 theories. The schema comment explicitly notes constraint [C4]: "Molecule keeps its own constituent_templates (no auto-derivation from T1.5)" — preserving the design decision that molecules may curate a subset of a T1.5 theory's templates for presentation purposes.

**Molecule Registry Extension**. The `MoleculeRegistry` (`src/qa/molecules/registry.py`, expanded from 143 to 210 lines) was extended with three T1.5-aware query methods implementing constraint [C5]: `find_by_t1_5(theory_id)` returns all molecules that are children of a given T1.5 theory (using the `parent_t1_5_theory` field); `get_reduction_chain(template_id)` traces a template's full position in the hierarchy by instantiating both registries and returning its T1.5 parents and the molecules that include it; `get_coverage_by_theory()` computes, for each REDUCED T1.5 theory, what percentage of its constituent templates are covered by at least one molecule. These methods enable the navigational queries the system has needed since the T1.5 level was first proposed: given any template, the system can now programmatically answer "which theories does this template support, and which molecules package those theories for the website?"

**The Complete Navigational Chain**. With AG's implementation, the full hierarchy is now computationally traversable in both directions. Downward: T1 Framework (e.g., PP) → T1.5 Theories that draw on it (e.g., ART, Biophilia, Soundscape, BRECVEMA) → Templates within each theory → Molecules that package those templates. Upward: Template (e.g., PP_SPECTRAL_MATCH_001) → T1.5 theories it supports (ART via Soft Fascination and Extent, Biophilia via Fractal Fluency, BRECVEMA via Musical Expectancy) → Molecules (ART molecule, BIOPHILIA molecule) → T1 Frameworks (PP, SN, NM). The `get_reduction_chain()` method traverses this chain in a single call. AG's taxonomy tagging system (§109) can now exploit this chain to answer queries like "show all articles with findings related to ART" by collecting all templates in ART's constituent list, then finding all extraction rows linked to those templates — a meta-analysis query that was previously impossible without manual cross-referencing.

**Validation Status**. The T1.5 registry's `validate_all()` method reports validation results across all 22 theories. All 14 REDUCED theories pass constraint [C1] (irreducible residual present with non-empty narrative). All 3 REJECTED/DEFERRED theories pass constraint [C3] (rejection rationale present). The 3 CANDIDATE theories pass trivially (no constraints apply to CANDIDATE status beyond basic field presence). The molecule registry reports 12 molecules loaded, all passing schema validation. The cross-registry consistency check (molecules' `parent_t1_5_theory` references resolve to valid theory IDs in the T1.5 registry) has not yet been implemented as an automated test but is a priority for the next testing sprint.

---


### §72. What a Reduction Means: From Domain Theory to T1 Pathway Weights {#72-what-a-reduction-means}

#### 72.1 The Panel D-1 Foundation {#721-the-panel-d-1-foundation}

The formal apparatus for T1.5 reductions was developed by Panel D-1 (ReductionClaim Architecture), convened on February 15, 2026, comprising ten experts spanning mechanistic philosophy of science, causal modelling, and computational neuroscience: William Bechtel (UCSD; mechanistic explanation and decomposition), Carl Craver (Washington University; levels of mechanisms and constitutive relevance), Lindley Darden (Maryland; mechanism schemas and discovery), Judea Pearl (UCLA; structural causal models and interventionist semantics), Clark Glymour (Carnegie Mellon; causal discovery and formal epistemology), Peter Gärdenfors (Lund; conceptual spaces), Russell Poldrack (Stanford; cognitive ontology and the Cognitive Atlas), Danielle Bassett (Penn; network neuroscience and modular brain organization), Karl Friston (UCL; free energy principle and hierarchical generative models), and Sandra Mitchell (Pittsburgh; integrative pluralism and limits of reductionism).

The panel's central question was deceptively simple: what does it mean to say that a domain-level environmental psychology theory (e.g., ART, SRT, Biophilia) *reduces to* a composition of Tier 1 neural mechanisms? The classical philosophical answer — Nagelian bridge-law reduction, where higher-level predicates translate without remainder into lower-level predicates (Nagel, 1961) — was rejected unanimously. Environmental psychology theories are not the kind of entity that admits clean bridge-law translation, for at least three reasons: they bundle multiple constructs with different neural substrates, they contain irreducibly person-dependent components (ART's Compatibility, for instance, depends on the individual's current goals), and they generate predictions at a level of description (behavioural, experiential, architectural) that cannot simply be replaced by neural vocabulary without explanatory loss. What was needed instead was a mechanistic reduction in the tradition of Machamer, Darden, and Craver (2000) and Bechtel and Abrahamsen (2005): a specification of the parts, operations, and organizational structure that together produce the phenomena the higher-level theory describes.

The product of Panel D-1 is the **ReductionClaim** data structure — a formally specified directed acyclic graph (DAG) with typed, signed edges, per-edge confidence stacks, evidence linkages to the staging database, and a three-part irreducible residual framework. Every subsequent reduction panel (T2-A through T2-C, and the expansion panels) used this architecture as its output format.

#### 72.2 The ReductionClaim DAG {#722-the-reductionclaim-dag}

A ReductionClaim asserts that a Tier 2 construct (e.g., "soft fascination") decomposes into a specific arrangement of Tier 1 templates. Following Bechtel (2008), every reduction must specify four things: (a) the component parts (which templates participate), (b) the component operations (what those templates compute), (c) the organization of parts and operations (how they are arranged — in series, parallel, with feedback, with enabling conditions), and (d) the boundary conditions under which the mechanism operates. The DAG representation was adopted unanimously; Pearl (2009) argued that directed acyclic graphs with interventionist semantics are non-negotiable for any system making causal claims.

Each ReductionClaim carries a unique identifier (e.g., `RC_ART_SOFT_FASCINATION_002`), semantic versioning for revisability, a construct validity assessment (HIGH / MEDIUM / LOW), a compositional adequacy judgment, and an overall maturity rating on the three-level scale: *how-possibly* (mechanism sketched but untested), *how-plausibly* (mechanism specified with indirect support), *how-actually* (mechanism demonstrated through direct intervention). The confidence assessment is four-dimensional per edge — extraction confidence, statistical confidence, mechanism confidence, and epistemic confidence — and these dimensions are never averaged into a single number (a design decision that preserves the profile of uncertainty rather than collapsing it).

Critically, every ReductionClaim links back to the staging evidence database. The 1,361 theory-link rows from Article Eater's evidence extraction pipeline are classified against each reduction as EDGE_SUPPORTING (evidence consistent with a specific edge), CLAIM_COHERENT (evidence consistent with the theory but not localized to a specific edge), EDGE_CONTRADICTING (evidence inconsistent with a claimed edge — high-value for revision), or UNACCOUNTED (evidence relevant to the theory but not explained by the current reduction). As Glymour insisted, when unaccounted rows exceed 20% of relevant evidence, the reduction is automatically flagged for possible missing edges.

#### 72.3 Four Edge Types and Their Semantics {#723-four-edge-types-and-their-semantics}

The panel converged on four edge types after a productive debate between Bechtel (who proposed six types) and Poldrack (who, drawing on Cognitive Atlas experience, argued that too many types paralyze annotators). The final taxonomy:

**PRODUCES** — Template A's output causes Template B's input. This is the standard etiological causal relation: temporal, directional, satisfying Pearl's interventionist test (P(B | do(A=a)) ≠ P(B)). Most edges in most reductions are of this type.

**INHIBITS** — Template A prevents, suppresses, or blocks Template B. Identical causal semantics to PRODUCES but with negative valence. Pearl insisted that "absence of" constructions (e.g., "absence of threat produces restoration") must be represented as negative edges, not as flat assertions.

**CONSTITUTES** — Template A partially constitutes the phenomenon being reduced. This is not a causal relation but a part-whole relation: non-temporal, non-directional, and validated by the mutual manipulability criterion (see §72.4). Craver's contribution was to insist that every CONSTITUTES edge carry explicit evidence documentation, since constitutive claims are the most epistemically demanding.

**MODULATES** — Template A changes the magnitude or probability of Template B's operation without being necessary for B. The paradigm case is neuromodulation: serotonin changes visual cortex gain without performing visual computations. MODULATES edges are essential for representing individual differences, contextual variation, and dose-response relationships.

Each edge additionally carries a sign (positive/negative) and an annotation field that can capture finer distinctions — ENABLING (background condition necessary but not producing), SUSTAINING (maintains mechanism once initiated), and so forth — without inflating the core type taxonomy.

#### 72.4 Mutual Manipulability and Constitutive Relevance {#724-mutual-manipulability-and-constitutive-relevance}

Craver's (2007) mutual manipulability criterion provides the standard for CONSTITUTES edges. A component is constitutively relevant to a phenomenon if and only if: (1) top-down interventions on the phenomenon change the component, AND (2) bottom-up interventions on the component change the phenomenon. Both directions must be demonstrated — or at least evidentially supported — for the edge to be credible.

**Worked example: DMN and Soft Fascination.** Consider template T27 (DMN subsystem dynamics) and the ART construct "soft fascination." Top-down test: instructing subjects to focus externally (suppressing soft fascination) reduces DMN connectivity — demonstrated by Andrews-Hanna et al. (2014). Bottom-up test: TMS disruption of medial PFC (suppressing DMN) should reduce self-reported restoration — suggestive but not directly tested in an ART context. Panel T2-A therefore assigned PARTIAL mutual manipulability, with the bottom-up direction flagged as a schema gap.

The practical consequence is that CONSTITUTES edges generally carry lower confidence than PRODUCES edges, because the evidence bar is higher. This is appropriate: constitutive claims assert that a neural process *is part of what it means* for the psychological phenomenon to occur, which is a stronger commitment than asserting a causal connection.

#### 72.5 The Three-Part Irreducible Residual {#725-the-three-part-irreducible-residual}

A central debate between Darden and Mitchell concerned the status of what remains after reduction. Darden (2006) distinguished *schema gaps* — places in the DAG where a connection is believed to exist but has not yet been formalized — from *genuine irreducibility*, properties that in principle resist decomposition. Mitchell (2003, 2009) argued that genuine irreducibility is more common than mechanists typically admit, particularly for constructs involving subjective experience, person-environment fit, and cultural meaning.

Friston proposed a formal test: the Markov blanket criterion. If the Tier 1 variables statistically screen off the Tier 2 construct from its inputs and outputs, any residual is a schema gap (future work). If they demonstrably fail to screen it off, irreducibility is genuine, and the specific variables missing from the blanket can be formally identified.

The panel's resolution was a three-part representation:

**Part 1: Schema Gaps** — Gaps within the DAG, tagged with one of eight GapType values (MEDIATION, MECHANISM, BOUNDARY, DIRECTION, INTERACTION, VALIDATION, UNJUSTIFIED_EDGE, CRITICAL_QUESTION) and a priority level. These are research queue targets — resolvable in principle by adding or refining templates.

**Part 2: Compositional Adequacy** — An assessment of whether the DAG as a whole is sufficient, using Bassett's three-value scale: FULLY_DECOMPOSABLE (phenomenon is the sum of its template components), INTERACTION_DEPENDENT (specific inter-template interactions are required that no individual template captures), or EMERGENT_RESIDUAL (whole-graph properties arise that resist localization). Most T1.5 reductions land at INTERACTION_DEPENDENT, which is precisely the intermediate position that justifies the T1.5 tier.

**Part 3: Irreducible Residual Narrative** — A free-text scientific judgment about what cannot be reduced and why. For SRT's parasympathetic activation, this is minimal (the mechanism is nearly fully specified). For ART's Compatibility, the residual is substantial (person-dependent goal structures resist environmental decomposition). Mitchell insisted that the system also allow a judgment of AUTONOMOUSLY_EXPLANATORY, following Batterman (2002) — some constructs may legitimately operate at their own level and should not be forced into mechanistic reduction.

#### 72.6 Compositional Adequacy {#726-compositional-adequacy}

Bassett's three-value assessment deserves amplification because it determines whether a reduction is genuinely explanatory or merely a list of relevant templates:

**FULLY_DECOMPOSABLE** — The phenomenon equals the sum of its parts. Remove any component and the phenomenon degrades proportionally. No interaction effects exceed what individual templates predict. Example: a straightforward cortisol suppression pathway through a single HPA cascade.

**INTERACTION_DEPENDENT** — The phenomenon requires specific organizational relationships between templates that are not captured by any individual template. The critical insight from the ART reduction illustrates this: soft fascination requires T31 (low auditory demand) as a precondition, T2 (moderate visual prediction error) as a sustaining modulator, and T27 (DMN re-engagement) as constitutive of the phenomenon. The interaction between T2 and T27 is decisive — too little prediction error and DMN disengages (boredom), too much and the task-positive network takes over (hard fascination). This interaction is not representable in any single template.

**EMERGENT_RESIDUAL** — The phenomenon possesses properties arising from the system as a whole that cannot be attributed to any composition of components however organized. Bassett's paradigm case from network neuroscience: small-world topology is a whole-graph property depending on the interaction topology rather than any node or subset of nodes.

#### 72.7 T1.5 Demarcation Criteria {#727-t15-demarcation-criteria}

The T1.5 tier occupies a specific epistemic position: these are theories that organize families of phenomena within a domain, that are explained *by* Tier 1 frameworks (not self-explanatory), that reduce *to* specific ATLAS templates with coverage ≥ 60%, that possess non-trivial irreducible residuals (preventing collapse into a mere template list), and that carry explicit parent T1 mappings with approximate percentages. The demarcation criteria, formalized across Panel D-1 and the Tier Architecture specification (§50), distinguish T1.5 theories from four imposters:

A T1.5 theory is **not a single construct** — "pattern separation" names one hippocampal mechanism, not a family of organized phenomena. It belongs at T2 (a template) or below.

A T1.5 theory is **not a domain label** — "Individual Differences" or "Color Psychology" name research areas, not theories with deductive structure. They organize literatures bibliographically but generate no predictions that could fail.

A T1.5 theory is **not a measurement standard** — ISO 12913 specifies how to measure soundscapes; Soundscape Theory (Schafer, 1977) is the theoretical framework that organizes acoustic-experiential phenomena into families with shared mechanisms. The standard is an operationalization of the theory, not the theory itself.

A T1.5 theory is **not a T1 framework in disguise** — Embodied Cognition, Multisensory Integration, and Predictive Processing are already Tier 1 frameworks. Elevating them to T1.5 would create circular reductions. Free Energy Minimization, as the panel firmly established, is a mathematical formalism *of* PP (T1), not a separate domain theory.

These demarcation criteria proved decisive in the February 23 Expansion Panel, where six of thirteen candidates were rejected precisely because they violated one or more of these conditions.

**References for §72:**

Bassett, D. S., & Sporns, O. (2017). Network neuroscience. *Nature Neuroscience*, *20*(3), 353–364. [~3,000 GS]

Batterman, R. W. (2002). *The devil in the details: Asymptotic reasoning in explanation, reduction, and emergence*. Oxford University Press. [~1,200 GS]

Bechtel, W. (2008). *Mental mechanisms: Philosophical perspectives on cognitive neuroscience*. Routledge. [~1,500 GS]

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative. *Studies in History and Philosophy of Science Part C*, *36*(2), 421–441. [~800 GS]

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press. [~3,500 GS]

Darden, L. (2006). *Reasoning in biological discoveries*. Cambridge University Press. [~600 GS]

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, *11*(2), 127–138. [~8,000 GS]

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, *67*(1), 1–25. [~5,000 GS]

Mitchell, S. D. (2003). *Biological complexity and integrative pluralism*. Cambridge University Press. [~1,000 GS]

Mitchell, S. D. (2009). *Unsimple truths: Science, complexity, and policy*. University of Chicago Press. [~800 GS]

Nagel, E. (1961). *The structure of science*. Harcourt, Brace & World. [~5,000 GS]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. [~25,000 GS]

Poldrack, R. A., & Yarkoni, T. (2016). From brain maps to cognitive ontologies. *Annual Review of Psychology*, *67*, 587–612. [~500 GS]

---

### §73. ART Reduction: Attention Restoration Theory → DT + PP + SN + NM {#73-art-reduction}

#### 73.1 Four Constructs, Four Reductions {#731-four-constructs-four-reductions}

Panel T2-A (ART Reduction, February 15, 2026) was the largest reduction panel convened, with twelve experts: Marc Berman (Chicago; ART neuroscience), Rachel Kaplan (Michigan, emerita; ART co-creator), MaryCarol Hunter (Michigan; "nature pill" dose-response), Peter Kahn (Washington; technological nature), Yannick Joye (Groningen; fractal fluency), Mathew White (Exeter; BlueHealth), Jessica Andrews-Hanna (Arizona; DMN subsystem dynamics), Lucina Uddin (UCLA; salience network), Petr Janata (UC Davis; auditory scene analysis), Moshe Bar (Bar-Ilan; visual prediction), Peter Aspinall (Heriot-Watt; ecological measurement), and Colin Ellard (Waterloo; psychogeography). The panel decomposed ART into four constructs — Soft Fascination, Being Away, Extent, and Compatibility — and produced individual ReductionClaims for each plus a system-level integration claim. The system-level maturity rating: *how-plausibly*, with construct-level variation from *how-plausibly* (Soft Fascination, Being Away) to *how-possibly* (Extent, Compatibility).

ART engages eleven of the system's 52 templates (21% of the library): core templates T27 (DMN subsystem dynamics), T1 (prediction error), T23 (context/scene construction); supporting templates T2 (visual complexity), T31 (auditory scene), T3 (cognitive map); modulatory templates T5 (threat/HPA), T12 (interoception), T8 (motor affordance); control template T45 (proactive/reactive); and social template T48 (social affordance reading).

#### 73.2 Soft Fascination: DMN Subsystem Dynamics {#732-soft-fascination-dmn-subsystem-dynamics}

**Construct definition.** Soft fascination is the gentle, effortless engagement with moderately interesting stimuli (flowing water, rustling leaves, dappled light) that simultaneously permits reflective thought. It is distinguished from *hard* fascination (which captures attention completely, as in watching a car crash) and from *rumination* (which is effortful and self-focused). The neural signature, as Andrews-Hanna's work has progressively clarified, is a specific DMN subsystem configuration: medial temporal subsystem engagement (scene construction, episodic simulation) combined with suppression of the dorsal medial subsystem (self-referential rumination). This is the critical distinction — restorative mind-wandering is not generic DMN activation but a specific subsystem pattern.

The reduction (RC_ART_SOFT_FASCINATION_002) proceeds through five key edges. Auditory properties produce analysis load via established soundscape pathways (HIGH confidence, *how-actually*), with speech content uniquely potent in disrupting fascination because it engages the SN speech channel — a finding with direct architectural consequence: water features that mask speech simultaneously reduce auditory prediction error and support fascination. Visual scene properties produce prediction error through standard PP pathways (HIGH confidence), with fractal fluency (Joye's contribution) adding that mid-range fractal dimension (D ≈ 1.3-1.5) produces hedonic marking via processing efficiency (MEDIUM confidence, *how-plausibly*). The salience network then computes a threat-safety assessment that biases DMN subsystem selection (Uddin's mechanism): in low-threat environments, the medial temporal subsystem is favoured; under threat, the dorsal medial subsystem dominates, producing rumination rather than restoration. The constitutive edge — medial temporal DMN engagement with dorsal medial suppression constituting soft fascination — carries MEDIUM confidence with partial mutual manipulability (top-down demonstrated, bottom-up suggestive).

**Architectural example: the hospital courtyard.** Consider a patient recovery courtyard with a small water feature, deciduous trees with fractal branching (D ≈ 1.3), and seating oriented away from hospital corridors. The water feature masks speech (reducing auditory PE), the trees provide moderate visual complexity (engaging PP without demanding effortful attention), and the spatial enclosure provides refuge (permitting SN to classify the environment as safe). This configuration should produce the specific DMN subsystem pattern — medial temporal engagement for scene construction and gentle episodic simulation, dorsal medial suppression preventing health-related rumination. Hunter's dose-response data predicts onset at approximately 10 minutes (SN habituation), peak benefit at 20-30 minutes (maximum cortisol decline rate), with diminishing returns thereafter.

A key finding from the panel concerns multisensory coherence: real nature produces greater restoration than screen-based nature (Kahn's technological nature research) because cross-modal congruence (visual fractal statistics + congruent auditory statistics + thermal comfort + olfactory cues) amplifies the fascination response. This connects to MSI (T1) and generates a prediction: VR nature that achieves visual-auditory-proprioceptive congruence should restore more effectively than visual-only screen nature but less effectively than real nature (which additionally provides olfactory and thermal congruence).

**Irreducible residual.** The phenomenological quality of "softness" — the felt sense of effortless, gentle engagement — may not be fully captured by DMN connectivity metrics. The relationship between the objectively measured subsystem configuration and the first-person experience of fascination-without-effort is partially reducible at best. Individual differences in interoceptive sensitivity (IC framework) may modulate whether DMN re-engagement is experienced as "soft fascination" or merely as "mind wandering."

#### 73.3 Being Away: Hippocampal Context Reconstruction {#733-being-away-hippocampal-context-reconstruction}

**Construct definition.** Being Away is the cognitive disengagement from habitual concerns through hippocampal context reconstruction. Critically, it requires perceptual discontinuity from the prior context sufficient to trigger a new context model — not mere physical relocation but mental departure from the concerns of one's routine environment. As Godden and Baddeley (1975) demonstrated with divers encoding words underwater versus on land, spatial context is a powerful modulator of memory access: a sufficiently novel environment suppresses retrieval of concerns associated with the prior context.

The reduction (RC_ART_BEING_AWAY_001) traces a clean causal chain: perceptual discontinuity triggers SN novelty detection (anterior insula response), which produces a ONE-TIME cognitive set switch (critically, a single switch event, not the repeated switching that causes directed attention fatigue), which drives hippocampal context reconstruction (forest predictions replace office predictions), which cascades into prediction model updating and, in non-threatening contexts, initial HPA downregulation (cortisol drop within 5 minutes per Hunter's data). The constitutive edge — cognitive context shift constituting the being-away experience — carries MEDIUM confidence.

**Temporal profile.** Being Away is rapid: SN novelty detection within seconds of entering a novel environment, context transition within 3-5 minutes (Ellard, Bar), cortisol response within 5 minutes. This temporal ordering is architecturally important — Being Away *precedes* Soft Fascination. As the panel summarized: "Being Away opens the door that Soft Fascination walks through."

**Architectural example: the threshold transition.** Traditional Japanese architecture deploys the *engawa* (covered veranda) and garden entrance sequence as explicit Being Away technology: the compression of a narrow corridor, the pause at the threshold, the expansion into garden space — each element triggers novelty detection, forces context reconstruction, and disengages the prior mental set. Modern hospital design often fails precisely here: corridors transition abruptly from clinical to garden space with no perceptual discontinuity, so patients carry their clinical concerns into the supposedly restorative courtyard.

**Irreducible residual.** The phenomenological "psychological distance" — the felt sense of removal from one's concerns — and the meditative or attentional variant (achieving Being Away with closed eyes in the same room through mindfulness practice) suggest that hippocampal context reconstruction is necessary but not sufficient for the full Being Away experience.

#### 73.4 Extent: Hierarchical Prediction Depth {#734-extent-hierarchical-prediction-depth}

**Construct definition.** Extent refers to environmental richness and structure sufficient for immersion in a "whole other world." Kaplan and Kaplan (1989) decomposed it into two sub-components: SCOPE (enough content at multiple scales to sustain engagement) and COHERENCE (content forming a legible, interpretable whole with consistent statistical structure). The reduction (RC_ART_EXTENT_001) maps Scope to hierarchical prediction depth — deep hierarchical structure prevents habituation by providing resolvable prediction errors at multiple spatial scales — and Coherence to prediction transferability — fractal self-similarity means the same generative model works at all scales, which the visual system experiences as "making sense."

This was the weakest reduction (LOW-MEDIUM confidence, *how-possibly* to *how-plausibly*), reflecting the difficulty of operationalizing "immersion" neurally. The key edges include: information richness producing hierarchical prediction depth (MEDIUM), statistical self-similarity producing prediction transferability (MEDIUM), depth cues and structure driving hippocampal scene construction (HIGH — Maguire/Ellard's established finding that perceived depth, not physical depth, drives response), scene construction producing an immersive world model (MEDIUM), environmental legibility inhibiting navigational stress (MEDIUM), and the constitutive edge linking scope + coherence + immersion to the Extent experience (LOW-MEDIUM — never directly tested).

**Critical finding.** Extent requires coherence as well as scope. A junkyard has high scope (much content) but low coherence (no consistent statistical structure); it does not produce the Extent response. A dense, disorienting forest has scope and some coherence but induces navigational stress (T14), which undermines the restorative benefit. The optimal Extent environment combines multi-scale richness with interpretable structure — precisely the Biophilic Complexity specification from the T2-C reduction (§75.3).

**Irreducible residual.** Aesthetic quality, sense of wonder, and awe — the "vastness that exceeds the self" — may involve self-representation circuits not included in the current reduction. This connects to the Awe/Kama Muta reduction, itself in early formal status.

#### 73.5 Compatibility: The dACC Error Gate {#735-compatibility-the-dacc-error-gate}

**Construct definition.** Compatibility is the match between a person's current goals and inclinations and the environmental supports and demands. The reduction (RC_ART_COMPATIBILITY_001) reconceptualizes incompatibility as a directed attention demand generated by dACC error monitoring: when the environment affords actions that conflict with current goals, the dACC detects action prediction error, engages cognitive control resources, and thereby consumes the very attentional resource that restoration is meant to replenish.

The key insight is architecturally devastating: a beautiful, extensive, fascinating environment that is incompatible with the user's goals *fails to restore* because incompatibility consumes the resource restoration would replenish. The person who wants solitude but finds themselves in a group-friendly garden, the wayfinder who cannot locate the exit, the thermally uncomfortable occupant in an otherwise gorgeous atrium — all experience dACC error that overrides ART benefits.

**Architectural example: the library reading garden.** A university library provides a reading garden intended for quiet study. The design includes benches facing each other across narrow paths (social incompatibility for solitude-seekers), no clear wayfinding signage (spatial incompatibility), and a water feature close to seating that is too loud for reading (auditory incompatibility despite being restorative in other contexts). The garden scores well on Extent, moderately on Fascination, and adequately on Being Away — yet fails to restore because Compatibility is violated on three dimensions simultaneously.

**Irreducible residual.** The strongest residual in the entire ART reduction. Compatibility is inherently person-dependent: the same environment may be highly compatible for one person and deeply incompatible for another, depending on current goals, social orientation, thermal sensitivity, and mobility. This person-dependence cannot be reduced to environmental features alone, which means that some component of ART will always require individual-level assessment rather than purely architectural specification.

#### 73.6 System-Level Integration and Temporal Sequence {#736-system-level-integration-and-temporal-sequence}

The system-level ReductionClaim (RC_ART_SYSTEM_001) specifies a dependency structure with architectural consequences:

**Temporal sequence:**
1. Being Away (context shift) — opens the door (~0-5 minutes)
2. Soft Fascination (sustained DMN engagement) — the restoration mechanism (~5-30 minutes)
3. Extent (provides multi-scale content) — sustains fascination (concurrent with step 2)
4. Compatibility (permission condition) — must hold throughout all three stages

**Dependency structure:** Being Away *enables* Soft Fascination (without context shift, prior concerns interfere). Extent *sustains* Soft Fascination (without depth, fascination fades). Compatibility *permits* all three (any incompatibility drains the attentional resource being restored).

**Four failure modes** (each architecturally diagnosable):
- *Missing Being Away*: Physically present but mentally at work → no restoration (e.g., glass-walled office garden visible from desk — no perceptual discontinuity)
- *Missing Fascination*: Context shifted but environment boring → boredom, not restoration (e.g., barren concrete courtyard with no visual complexity)
- *Missing Extent*: Initially fascinated but no depth → fascination fades in minutes (e.g., single potted plant in waiting room)
- *Missing Compatibility*: Fascinating, extensive, away, BUT can't find exit / too cold / socially overwhelmed → stress overrides restoration

#### 73.7 Staging Data Coverage and Gaps {#737-staging-data-coverage-and-gaps}

The ART reduction draws on approximately 1,251 staging rows, with 41% classified as EDGE_SUPPORTING, 30% as CLAIM_COHERENT, 5% as EDGE_CONTRADICTING, and 24% as UNACCOUNTED. The unaccounted rows cluster in five domains: immune/inflammatory effects (~80 rows, potentially connecting to T50 or T5 chronic pathway), creativity and problem-solving (~60 rows, possibly involving medial temporal DMN divergent thinking), sleep quality (~45 rows, circadian mechanisms not yet templated), social cohesion (~40 rows, connecting to social templates T48-T52 from Panel V), and childhood developmental effects (~35 rows, longitudinal pathways). A notable gap: approximately 25 rows address olfactory effects with no corresponding template — the system currently has no olfactory mechanism template, identified as a gap requiring future panel work.

**References for §73:**

Andrews-Hanna, J. R., Smallwood, J., & Spreng, R. N. (2014). The default network and self-generated thought: Component processes, dynamic control, and clinical relevance. *Annals of the New York Academy of Sciences*, *1316*(1), 29–52. [~1,500 GS]

Berman, M. G., Jonides, J., & Kaplan, S. (2008). The cognitive benefits of interacting with nature. *Psychological Science*, *19*(12), 1207–1212. [~3,500 GS]

Bratman, G. N., Hamilton, J. P., Hahn, K. S., Daily, G. C., & Gross, J. J. (2015). Nature experience reduces rumination and subgenual prefrontal cortex activation. *PNAS*, *112*(28), 8567–8572. [~1,500 GS]

Godden, D. R., & Baddeley, A. D. (1975). Context-dependent memory in two natural environments. *British Journal of Psychology*, *66*(3), 325–331. [~2,800 GS]

Hunter, M. R., Gillespie, B. W., & Chen, S. Y.-P. (2019). Urban nature experiences reduce stress in the context of daily life. *Frontiers in Psychology*, *10*, 722. [~500 GS]

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. [~6,000 GS]

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, *15*(3), 169–182. [~4,800 GS]

Uddin, L. Q. (2015). Salience processing and insular cortical function and dysfunction. *Nature Reviews Neuroscience*, *16*(1), 55–61. [~2,000 GS]

---

### §74. SRT Reduction: Stress Recovery Theory → NM + IC + PP {#74-srt-reduction}

#### 74.1 Three Constructs, Temporal Cascade {#741-three-constructs-temporal-cascade}

Panel T2-B (SRT Reduction, February 15, 2026) comprised nine experts: Roger Ulrich (Chalmers, emeritus; SRT creator), Rita Berto (Verona; ART-SRT comparison), Robert Sapolsky (Stanford; glucocorticoid mechanisms), Hugo Critchley (Brighton & Sussex; interoception and autonomic neuroscience), Stephen Porges (Indiana; polyvagal theory), Patrik Vuilleumier (Geneva; subcortical "low road"), Björn Grinde (Norwegian IPH; evolutionary approaches), Peter Aspinall (Heriot-Watt; ecological measurement), and John Allen (Arizona; psychophysiology methodology and HRV precision). SRT decomposes into three temporally ordered constructs — Immediate Affective Response (~100ms-5s), Parasympathetic Activation (~5s-5min), and Cortisol/HPA Recovery (~15min-3hr) — with each construct initiating the next. The system-level maturity rating: ***how-actually***, the highest of any T1.5 theory in the system.

SRT engages seven templates (13% of the library): core templates T5 (HPA axis), T12 (interoception), T46 (pulvinar gating); supporting templates T9 (biophilic embodied response), T22 (aesthetic reward); modulatory templates T8 (motor affordance), T29 (allostatic master).

#### 74.2 Immediate Affective Response: The Five-Stage Subcortical Cascade {#742-immediate-affective-response}

**Construct definition.** The immediate affective response is a rapid (100ms-5s) positive affective shift triggered by natural environments, beginning with subcortical threat/safety assessment via the pulvinar "low road" (amygdala via superior colliculus) and cascading through autonomic initiation, cortical scene categorization, and conscious aesthetic evaluation. The pre-cognitive component (stages 1-2, <200ms) is what distinguishes SRT from mere aesthetic preference.

The reduction (RC_SRT_IMMEDIATE_AFFECT_001, HIGH confidence, *how-actually*) traces a five-stage cascade:

**Stage 1** (~100ms): Retina → superior colliculus → pulvinar → amygdala. Rapid scene evaluation based on low spatial frequency statistics. Natural scenes with 1/f power spectra produce reduced amygdala activation; urban scenes with flat spatial frequency spectra produce increased activation (Vuilleumier's "low road").

**Stage 2** (~200ms): Amygdala → hypothalamus → autonomic initiation. Reduced amygdala output decreases sympathetic drive and, critically, disinhibits the ventral vagal complex. Porges' contribution: the amygdala tonically inhibits the nucleus ambiguus; reduced amygdala output releases this inhibition, permitting vagal brake engagement (RSA increase).

**Stage 3** (~150-200ms): Parallel cortical pathway — V1 → V2 → PPA/RSC → scene categorization. Cortical processing confirms scene identity.

**Stage 4** (~300-500ms): Cortical evaluation → vmPFC/OFC → affective valence. The "liking" response emerges, connecting to T22 (aesthetic reward).

**Stage 5** (~500ms-5s): Full conscious aesthetic experience.

The constitutive edge — subcortical safety signal + sympathetic withdrawal + vagal disinhibition + positive cortical valence constituting the immediate affective response — carries HIGH confidence with mutual manipulability demonstrated in both directions: stress induction suppresses the response (top-down), and pharmacological autonomic blockade eliminates recovery markers despite safe environments (bottom-up).

**Architectural example: the view from the hospital bed.** Ulrich's (1984) landmark finding — that post-cholecystectomy patients with tree views recovered faster than those with brick-wall views — is now mechanistically interpretable. The tree view delivers 1/f spatial frequency statistics to the pulvinar within 100ms of each glance, producing reduced amygdala activation, disinhibiting the ventral vagal complex, and initiating parasympathetic recovery. The brick wall delivers flat spatial frequency statistics, providing no safety signal and no autonomic relief. Over days of recovery, each glance out the window either initiates (tree) or fails to initiate (brick) the five-stage cascade, with cumulative effects on cortisol exposure, immune function, and analgesic requirements — precisely the outcome pattern Ulrich observed.

**Irreducible residual.** Minimal for mechanism. The residual concerns the subjective quality of the affective shift — why a safety signal "feels good" rather than merely reducing arousal. This phenomenological dimension is partially addressable through interoceptive inference (IC framework) but remains a classic hard-problem frontier.

#### 74.3 Parasympathetic Activation: Ventral Vagal Specificity {#743-parasympathetic-activation}

**Construct definition.** The shift in autonomic balance from sympathetic dominance to ventral vagal dominance. A crucial refinement from Porges: original SRT said "parasympathetic activation," but this is too generic. The recovery state specifically involves *ventral vagal* (myelinated vagus → sinoatrial node) activation producing calm alertness and RSA increase, *not* dorsal vagal activation (unmyelinated vagus → bradycardia, freeze response) which looks "parasympathetic" on some coarse measures but is not restorative.

**Three distinct components:**
1. **Ventral vagal activation** — the "social engagement" system. Measured specifically by RSA (respiratory sinus arrhythmia, high-frequency HRV), not generic HRV. Produces calm alertness.
2. **Sympathetic withdrawal** — decreased norepinephrine/epinephrine, HR decrease, EDA decrease. The *absence* of stress, not a positive state per se.
3. **Enteric activation** — vagal efferents to gut (rest-and-digest). Most relevant to chronic health outcomes, least to immediate experience.

The reduction (RC_SRT_PARASYMPATHETIC_001, HIGH confidence, *how-actually*) specifies that vmPFC is the key node: it provides tonic sympathetic inhibition in non-threatening environments (the "brake" on the stress response). When amygdala threat detection is low, vmPFC maintains this brake, permitting ventral vagal output via the nucleus ambiguus. Interoceptive updating follows: vagal afferents via NTS reach the anterior insula, updating the body-state representation — the "I feel calmer" signal that Critchley's work has characterized.

**Architectural example: seating design and baroreceptor activation.** The reduction includes a modulatory edge from T8 (motor affordance) to parasympathetic enhancement: comfortable postural affordances facilitate parasympathetic dominance because baroreceptor unloading in reclined or semi-reclined postures enhances vagal tone. An office breakroom with only upright chairs at desks provides less parasympathetic support than one with angled seating or even floor cushions. This edge carries MEDIUM confidence but has measurable physiological consequence — HRV differences between seated postures are well-documented in psychophysiology.

**Temporal profile:** Onset 5-30 seconds after environmental safety assessment, stabilization in 3-5 minutes, sustained as long as environment remains non-threatening, with greater benefit for exposures up to approximately 30 minutes.

#### 74.4 Cortisol / HPA Recovery: Sapolsky's Virtuous Cycle {#744-cortisol-hpa-recovery}

**Construct definition.** HPA axis downregulation following stress, accelerated by nature exposure through prevention of new HPA activation and support of the cortisol negative feedback loop. Sapolsky's key mechanistic insight: nature does not *actively reduce* cortisol. It *prevents new stressors from generating new cortisol release* and *allows existing cortisol to be metabolized and cleared* (half-life 60-90 minutes). As cortisol drops, GR (glucocorticoid receptor) occupancy in the hippocampus decreases, hippocampal LTP resumes, negative feedback re-engages, and HPA further downregulates — a virtuous cycle where recovery enables more recovery.

The reduction (RC_SRT_CORTISOL_RECOVERY_001, HIGH confidence, *how-actually* — the best-supported reduction in the entire system) traces the standard HPA cascade in reverse, with a critical chronic pathway extension. Each cortisol-recovery hour reduces cumulative allostatic cost (T29). Over weeks and months, daily repeated recovery preserves hippocampal integrity and immune function. Sapolsky emphasized that the *chronic pathway* is architecturally most important: acute stress recovery is proof-of-concept, but the real health dividend comes from architectural environments that minimize daily cortisol-hours over years, preventing the hippocampal damage and immune dysregulation that accumulate under chronic elevated cortisol.

**Dose metric:** Total daily cortisol-hours (the area under the cortisol curve across a day), not peak cortisol, determines allostatic cost. An environment that prevents cortisol spikes is more valuable than one that accelerates recovery from them.

**Architectural example: the chronic exposure office.** Consider two office buildings, identical in program but differing in environmental design. Building A has sealed windows, fluorescent lighting, acoustic tile ceilings, and cubicle-farm layouts with no nature views. Building B has operable windows, daylight with fractal shadow patterns, wood surfaces (D ≈ 1.3), prospect views from workstations, and a central courtyard. Neither building subjects occupants to acute stressors. But Building A provides no SRT cascade triggers — no 1/f statistics for pulvinar safety signalling, no thermal variability for allesthetic engagement, no Being Away transitions. Building B provides continuous low-level SRT activation: each glance at the courtyard initiates a micro-recovery cycle. Over a 40-year career, the cumulative difference in cortisol-hours, hippocampal volume, and immune function could be substantial — though this remains a prediction requiring longitudinal verification.

#### 74.5 System-Level Integration and the Chronic Pathway {#745-system-level-integration}

The three SRT constructs form a strict temporal cascade: Immediate Affective Response (subcortical initiation, ~100ms-5s) → Parasympathetic Activation (sustained autonomic shift, ~5s-5min) → Cortisol/HPA Recovery (endocrine normalization, ~15min-3hr). Each stage initiates the next: the immediate affective response triggers parasympathetic activation, which supports cortisol recovery by reducing sympathoadrenal secretion.

The **ART-SRT convergence at vmPFC** is the most architecturally consequential finding. Both theories depend on vmPFC functioning without amygdala interference. For ART, vmPFC is part of the DMN core subsystem that supports internal processing. For SRT, vmPFC provides tonic sympathetic inhibition — the autonomic "brake." If the amygdala detects environmental threat (noise, spatial disorientation, social crowding, thermal discomfort, visual chaos), *both* recovery systems are suppressed simultaneously. The shared bottleneck yields a unifying design principle: **minimize environmental threat signals**, which benefits ART and SRT in parallel.

| Dimension | ART | SRT |
|-----------|-----|-----|
| Primary system | Cortical (DMN) | Subcortical / autonomic |
| Primary mechanism | Disinhibition of DMN processing | Disinhibition of autonomic recovery |
| Timescale | 5-30 min restoration | 100ms-3hr cascade |
| Precondition | Attentional fatigue required | Stress required |
| Measured by | Cognitive tests (ANT, DSB) | Physiological (HRV, cortisol, EDA) |
| Templates involved | 11 (21% of library) | 7 (13% of library) |
| Shared templates | T5, T12, T8, T29 | Same |
| Overall maturity | *how-plausibly* | *how-actually* |

#### 74.6 Measurement Precision Requirements {#746-measurement-precision}

Allen's contribution addressed the methodological precision required for SRT verification, which has direct consequences for architectural research design:

**HRV:** Requires stationary recording periods — movement corrupts data. Reliable RSA needs 2-5 minutes of seated or standing data with controlled breathing. Ambulatory HRV is possible but requires artifact rejection algorithms.

**Cortisol:** Salivary cortisol reflects plasma levels from 15-20 minutes prior. A 30+ minute wait after entering an environment is necessary before the first meaningful sample. Study designs with immediate sampling are measuring the *prior* environment.

**EDA:** Confounded by ambient temperature and humidity. Must be controlled or measured as covariates. Palm temperature alone can produce EDA artifacts mimicking stress responses.

**Individual variation:** HRV varies 5-fold across healthy individuals. Within-subject designs are essential; between-subject designs require very large samples.

These measurement constraints have been incorporated into the system's prediction generation protocol: any architectural prediction involving SRT mechanisms must specify appropriate measurement windows, control conditions, and recommended sample sizes.

**References for §74:**

Critchley, H. D., & Harrison, N. A. (2013). Visceral influences on brain and behavior. *Neuron*, *77*(4), 624–638. [~800 GS]

Porges, S. W. (2011). *The polyvagal theory: Neurophysiological foundations of emotions, attachment, communication, and self-regulation*. Norton. [~3,500 GS]

Sapolsky, R. M. (2004). *Why zebras don't get ulcers* (3rd ed.). Holt. [~8,000 GS]

Ulrich, R. S. (1983). Aesthetic and affective response to natural environment. In I. Altman & J. F. Wohlwill (Eds.), *Behavior and the natural environment* (pp. 85–125). Plenum. [~3,000 GS]

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, *224*(4647), 420–421. [~5,500 GS]

Ulrich, R. S., Simons, R. F., Losito, B. D., Fiorito, E., Miles, M. A., & Zelson, M. (1991). Stress recovery during exposure to natural and urban environments. *Journal of Environmental Psychology*, *11*(3), 201–230. [~4,000 GS]

Vuilleumier, P. (2005). How brains beware: Neural mechanisms of emotional attention. *Trends in Cognitive Sciences*, *9*(12), 585–594. [~3,000 GS]

---

### §75. Biophilia Reduction: Prospect-Refuge + Biophilic Complexity + Fractal Fluency → EC + PP + SN + NM {#75-biophilia-reduction}

#### 75.1 Three Sub-Theories as Design Specification {#751-three-sub-theories}

Panel T2-C (Biophilia/Prospect-Refuge Reduction, February 15, 2026) comprised ten experts: Timothy Beatley (Virginia; biophilic cities), Grant Hildebrand (Washington, emeritus; prospect-refuge in architecture), Nikos Salingaros (Texas-San Antonio; mathematical complexity theory), Sergio Altomonte (Louvain; daylight and occupant wellbeing), Russell Epstein (Penn; PPA and scene processing), Eleanor Maguire (UCL; hippocampal spatial cognition), Dean Mobbs (Caltech; fear neuroscience and predator imminence), Richard Taylor (Oregon; fractal fluency originator), Peter Aspinall (Heriot-Watt), and Colin Ellard (Waterloo). The panel decomposed the biophilic framework into three sub-theories — Prospect-Refuge (Appleton, 1975), Biophilic Complexity (Salingaros, Kellert), and Fractal Fluency (Taylor, Hagerhall) — and produced individual ReductionClaims for each, system-level confidence *how-plausibly*.

The Biophilia cluster engages six templates (12% of library): T1 (prediction error), T2 (Goldilocks complexity), T3 (cognitive map), T5 (threat/HPA), T22 (aesthetic reward), T23 (context/scene). Overlap with ART is substantial (4 shared templates), and overlap with SRT significant (2 shared). This overlap is architecturally consequential: Biophilia provides the *design specifications* that activate ART and SRT mechanisms. The three tiers work in complementary fashion — Biophilia specifies *what to build*, ART explains *how it restores cognition*, SRT explains *how it reduces stress*, and the T1 frameworks specify the *neural mechanisms* underlying all three.

#### 75.2 Prospect-Refuge: Spatial Possibility and Safety {#752-prospect-refuge}

**Construct definition.** Prospect-Refuge (Appleton, 1975) describes the preference for spatial configurations providing both extensive visual access to surroundings (prospect) and a protected observation position (refuge). Prospect provides information about spatial possibilities; refuge provides protection from potential threat. The critical architectural insight, from Hildebrand (1999): optimal spaces provide prospect *from* refuge — the ability to survey a wide field while occupying an enclosed, protected position. This is not the same as mere openness: a glass box with floor-to-ceiling windows on all sides provides maximal prospect but zero refuge, and people in such spaces show measurable physiological stress.

**Prospect pathway.** The reduction traces prospect through scene processing to spatial cognition: spatial layout properties activate PPA scene encoding (HIGH confidence), PPA encodes openness, depth, and navigability, RSC converts viewpoint-dependent to allocentric representation (HIGH), RSC feeds into hippocampal cognitive map formation (T3, HIGH), and the hippocampal possibility space drives prospective scene construction (T23, MEDIUM). Maguire's key contribution: wider prospect activates more prospective place cells, creating a richer possibility space — "I can see where I could go."

**Refuge pathway.** Spatial enclosure properties produce amygdala threat evaluation (HIGH confidence), with back-to-wall and overhead cover configurations reducing threat detection. Reduced amygdala output decreases BNST sustained anxiety (HIGH — the BNST mediates the chronic, low-level anxiety of ambiguous threat, which is the worst kind for architectural occupants). And reduced amygdala + BNST output permits vmPFC tonic suppression to be maintained (HIGH) — the same vmPFC node that serves as the ART/SRT convergence point.

**Mobbs' predator imminence contribution** is particularly illuminating. His framework distinguishes pre-encounter (threat possible but not detected), post-encounter (threat detected, defensive behaviour activated), and circa-strike (attack imminent, panic). Refuge places the occupant at *pre-pre-encounter* — threat is not merely undetected but structurally impossible from the protected position. This eliminates both amygdala fear-based arousal (immediate threat response) and BNST sustained anxiety (ambiguous chronic threat), producing the deepest possible safety signal.

**Compression-Release dynamics.** Ellard's contribution extends Prospect-Refuge from a static configuration to a dynamic sequence. Narrow-to-wide spatial transitions produce spatial prediction error: expectations formed in a compressed space are violated by the expansion, generating moderate PE that resolves as relief. This offset of a negative state (confinement) activates the mesolimbic reward circuit (VTA → NAc). Critically, the compression-release *sequence* produces greater positive affect than static prospect or static refuge alone — the transition is rewarding.

**Architectural example: the medieval cloister.** A monastery cloister provides perhaps the purest architectural embodiment of dynamic Prospect-Refuge. The ambulatory (narrow, covered, enclosed = refuge + compression) alternates with views into the central garden (wide, open, prospect). Each arcade bay provides a compression-release cycle. The repetition sustains engagement without habituation (unlike a single dramatic reveal that habituates rapidly). The walking pace along the ambulatory creates a temporal rhythm of compression-release at approximately 4-6 second intervals, matching the parasympathetic recovery cycle.

#### 75.3 Biophilic Complexity: Organized Visual Information {#753-biophilic-complexity}

**Construct definition.** Biophilic Complexity names a syndrome of visual properties characteristic of natural and traditional built environments: scaling hierarchy (structures at multiple scales with consistent ratios of approximately 2.5:1, per Salingaros), mid-range fractal dimension (D ≈ 1.3-1.5), local symmetries not extending globally, moderate edge contrast distribution, biomorphic forms (curved, organic, growth-referenced), and natural material textures with inherent mid-range fractal D. The unifying principle: *organized complexity* — high information content with high structural predictability. Neither minimalist boring nor chaotic overwhelming.

The reduction maps this to the predictive processing hierarchy: scaling hierarchy produces hierarchical prediction depth in V1/V2 (MEDIUM confidence), consistent scale ratios produce sustained prediction error resolution cascades (each small PE is mildly rewarding — Bar's contribution, MEDIUM), all biophilic visual properties converge on the moderate PE zone of T2's Goldilocks range (HIGH), moderate PE produces processing fluency (MEDIUM), and fluency combined with sustained engagement produces aesthetic reward via T22 (MEDIUM).

**Two architectural failure modes:**
- **Minimalism** — low entropy, low mutual information → boring, sterile. The "sick building" aesthetic of smooth white surfaces, uniform lighting, and repetitive geometry. The visual system generates almost no prediction errors, fascination never engages, and the DMN defaults to rumination.
- **Chaos** — high entropy, low mutual information → overwhelming, stressful. Times Square, or the visual cacophony of an unplanned commercial strip. The visual system is flooded with unresolvable prediction errors, the salience network escalates to threat mode, and directed attention resources are consumed.

Organized complexity occupies the zone between these failures: enough information to sustain engagement, enough structure to make the information interpretable.

**Material-level implications** (Altomonte): Natural materials inherently possess mid-range fractal D — wood grain (D ≈ 1.3), stone texture (D ≈ 1.4), brick patterns (D ≈ 1.2), textured plaster (D ≈ 1.3). Synthetic materials — smooth plastic, polished metal, flat drywall — have very low D (approaching 1.0). The simplest design heuristic: use natural materials and the fractal statistics arrive automatically.

#### 75.4 Fractal Fluency: Processing Efficiency Hypothesis {#754-fractal-fluency}

**Construct definition.** Mid-range fractal patterns (D ≈ 1.3-1.5) produce maximal processing efficiency, aesthetic preference, and physiological relaxation because they match the statistical structure of natural scenes to which the human visual system evolved to be tuned.

The evidence chain from Taylor's program of research: (1) *Preference* (ROBUST) — D ≈ 1.3 preferred across many studies, cross-culturally, in early development. (2) *Physiology* (MODERATE) — EEG frontal alpha (relaxation marker) peaks at D ≈ 1.3 versus low or high D (Hagerhall et al., 2008). (3) *Eye movement* (MODERATE) — D ≈ 1.3 produces the widest fixation distribution (distributed gaze consistent with soft fascination). (4) *Mechanism* (SPECULATIVE) — processing efficiency → relaxation. The efficiency hypothesis proposes that V1/V2 spatial frequency channels are tuned to 1/f^β power spectra with β ≈ 2.6 (corresponding to D ≈ 1.3), so mid-range fractals require fewer computational resources, generating a fluency signal interpreted as ease, familiarity, and positive affect (following Reber's processing fluency theory).

Jackson Pollock's paintings are instructive: his drip technique produces fractal patterns at D ≈ 1.3-1.7, and they generate the same relaxation markers as natural scenes, suggesting that the mechanism is fractal *statistics* rather than "nature" per se.

**Competing account.** The fluency hypothesis has a rival: the *familiarity* interpretation, which proposes that D ≈ 1.3 is preferred not because it is efficiently processed but because it matches a stored prototype of "typical scene." These are not easily distinguished experimentally, and the panel flagged this as the primary unresolved question in fractal fluency research.

**Scale-dependent optima** (Salingaros, proposed but untested): Different optimal D values may apply at different viewing scales — arm's length D ≈ 1.3, room scale D ≈ 1.4, building scale D ≈ 1.5, urban scale D ≈ 1.6-1.7. If confirmed, this would have direct consequences for architectural specification at each scale.

**Ecological measurement:** Fractal D is the most directly manipulable variable in the entire Article Eater framework. It is a physical property of surfaces, measurable from photographs via box-counting algorithms, specifiable in design, verifiable in construction, and directly connectable to occupant physiological response. This makes it uniquely suited for architectural prediction: specify D → construct → verify → measure response.

#### 75.5 System-Level: Biophilia as ART/SRT Enabler {#755-system-level-biophilia}

The system-level Biophilia ReductionClaim (RC_BIO_SYSTEM_001) positions the three sub-theories as a *design specification layer* that sits above (architecturally) and below (epistemically) ART and SRT:

**Tier layering:**
- Biophilia → specifies *what to build* (prospect + refuge, organized complexity, fractal D)
- ART → explains *how it restores cognition* (soft fascination, being away, extent, compatibility)
- SRT → explains *how it reduces stress* (immediate affect, parasympathetic, cortisol recovery)
- Tier 1 → specifies the *neural mechanisms* underlying all three

**Dependency flows:**
- Fractal Fluency contributes to Biophilic Complexity (D is one component of organized complexity)
- Biophilic Complexity contributes to ART Soft Fascination (organized complexity provides the content for fascination)
- Prospect-Refuge enables SRT Immediate Affective Response (refuge → safety → amygdala deactivation → five-stage cascade)
- Prospect contributes to ART Extent (wide views provide the scope component)

The non-visual gap noted by Salingaros deserves emphasis: the current biophilic reductions are entirely visual-spatial, yet biophilia extends to non-visual modalities (birdsong, natural scents, water sounds, animal presence) that are architecturally relevant. This connects to the olfactory gap identified in Panel T2-A and the acoustic pathways addressed by Soundscape Theory (§76.2).

#### 75.6 Five Testable Architectural Predictions {#756-testable-predictions}

The panel generated five testable predictions from the reduction, each specifiable in architectural terms and measurable with existing instruments:

1. **Mezzanine Effect** — Mezzanines (high prospect + navigable escape routes) should produce greater recovery markers (RSA, EDA, self-report) than distant windows (high prospect but low navigable possibility space). Test: within-subject crossover during work breaks in the same building.

2. **Compression-Release Sequencing** — A building with alternating narrow→wide→narrow→wide sequences should produce greater cumulative positive affect than a constant-dimension building of equal total area. Test: Ellard-style ambulatory EDA/HRV profiles.

3. **Material-Level Fractal D** — Offices with natural wood surfaces (D ≈ 1.3) versus synthetic drywall (D ≈ 1.0) should show lower cortisol and higher RSA. Test: within-subject week × week crossover.

4. **Blank Wall Effect** — Textured corridor walls should produce faster walking pace and lower EDA than blank walls, matched for corridor dimensions. Test: Ellard-style walking study.

5. **Biophilia as ART Enabler** — High-biophilic workspaces should show greater ART benefit from nature breaks (due to less pre-depletion). Test: factorial design crossing workspace quality × break type.

**References for §75:**

Appleton, J. (1975). *The experience of landscape*. Wiley. [~3,000 GS]

Hagerhall, C. M., Laike, T., Taylor, R. P., Küller, M., Küller, R., & Martin, T. P. (2008). Investigations of human EEG response to viewing fractal patterns. *Perception*, *37*(10), 1488–1494. [~200 GS]

Hildebrand, G. (1999). *Origins of architectural pleasure*. University of California Press. [~300 GS]

Mandelbrot, B. B. (1982). *The fractal geometry of nature*. Freeman. [~25,000 GS]

Mobbs, D., Hagan, C. C., Dalgleish, T., Silston, B., & Prévost, C. (2015). The ecology of human fear: Survival optimization and the nervous system. *Frontiers in Neuroscience*, *9*, 55. [~300 GS]

Salingaros, N. A. (2006). *A theory of architecture*. Umbau-Verlag. [~200 GS]

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2011). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience*, *5*, 60. [~250 GS]

Wilson, E. O. (1984). *Biophilia*. Harvard University Press. [~15,000 GS]

---

### §76. Space Syntax, Soundscape, and Place Attachment Reductions {#76-space-syntax-soundscape-place-attachment}

#### 76.1 Space Syntax: Configuration as Cognition {#761-space-syntax}

Space Syntax (Hillier & Hanson, 1984; approximately 7,000 GS) was reduced on February 21, 2026, as one of three high-priority theories identified in the candidate inventory. The theory organizes six families of phenomena: (SS-A) integration predicts movement flows (R² = 0.50-0.80 between syntactic integration and pedestrian counts), (SS-B) the natural movement thesis (configuration alone explains movement variance independently of attractors), (SS-C) intelligibility and wayfinding (spatial coherence predicts navigation success), (SS-D) spatial configuration and social encounter (layout mediates copresence patterns), (SS-E) isovist properties and spatial experience (visible area and compactness predict perceived spaciousness, surveillance, comfort), and (SS-F) depth and spatial segregation (topological depth predicts privacy and segregation).

**Parent T1 mappings:** SN 40% (grid cell metric coding, hippocampal cognitive maps, place cell firing), PP 25% (prediction error landscape in visual fields, mystery as controlled PE), EC 20% (affordance richness from syntactic structure), IE-DPT 15% (goal-state override, expertise effects, cultural-semantic overlay).

**Template coverage:** ~70% (existing templates SC1, T3, SC2, T8, ENCLOSURE, T66, T_IE_010, T_IE_003, T_IE_002).

**Architectural example: the department store.** Hillier's original studies showed that shop locations with high syntactic integration attracted more customers regardless of merchandise quality. The mechanistic explanation: high integration spaces are encountered more frequently during natural movement (SN: cognitive maps route through well-connected nodes), produce lower spatial prediction error (PP: the space "makes sense" within the larger configuration), and offer richer affordance structures (EC: more visible options for action). When IE-DPT enters — a purposeful shopper with a specific destination — integration no longer predicts movement because the explicit channel overrides natural movement patterns. This IE-DPT override is precisely why wayfinding signage is needed only in spaces with low syntactic intelligibility.

**Irreducible residual (~35%):** The sociological logic by which spatial configuration encodes social structure across time (~20%), the topological-versus-metric debate (~5%), and cultural variation in integration-movement correlations (~10%). These residuals are not gaps awaiting templates but reflect the sociological dimension of Space Syntax that sits outside the neural-mechanistic framework.

#### 76.2 Soundscape Theory: Beyond Decibels {#762-soundscape-theory}

Soundscape Theory (Schafer, 1977; approximately 5,000 GS for the foundational text, with ISO 12913-1:2014 providing the measurement standard) was the second February 21 reduction. It organizes six phenomena: (SC-A) level-independent evaluation (same dBA produces different evaluations by context), (SC-B) the circumplex model (pleasant↔unpleasant × eventful↔uneventful), (SC-C) masking versus restoration (the right sounds reduce annoyance despite higher total SPL), (SC-D) expectation-congruent soundscapes (match between expected and actual predicts restoration), (SC-E) noise annoyance and stress physiology (sustained >55 dBA produces cortisol and cardiovascular effects), and (SC-F) individual differences in noise sensitivity (trait modulates annoyance independently of sound level).

**Parent T1 mappings:** PP 35% (context-modulated perception, acoustic prediction error, congruence matching), IC 25% (body-budget prediction, comfort as low interoceptive PE), NM 20% (dopaminergic reward from biophilic sounds, HPA axis activation from threat sounds), MSI 10% (visual context modulates acoustic interpretation), IE-DPT 10% (activity-frame retuning, semantic override, perceived control).

**Template coverage:** ~75% (existing templates PP1, PP2, IC2, NM1, T66, MSI1, T_IE_001, T_IE_003, T_IE_006).

**Architectural example: the park versus the highway.** Birdsong at 50 dBA in a park produces restorative evaluation; traffic noise at 50 dBA on a highway produces annoyance. Same physical level, opposite psychological evaluation. The PP mechanism: the park context generates an expectation model for birdsong-like spectra (high spectral complexity, temporal irregularity, moderate amplitude modulation), and the birdsong *matches* this expectation — low acoustic PE, positive valence. The highway context generates an expectation model that traffic noise matches, but the traffic spectrum is low-complexity, sustained, and carries threat associations (NM pathway) — HPA activation, cortisol increase. Additionally, visual context modulates acoustic processing (MSI): seeing trees while hearing birdsong enhances congruence; seeing a highway while hearing birdsong produces incongruence that partially undermines the restorative benefit.

The IE-DPT contribution is critical: a construction worker habituated to 85 dBA finds 60 dBA construction noise unremarkable (recalibrated expectation); a librarian finds it distressing (narrow expectation band). The explicit channel sets the activity frame, which sets the expectation model, which determines what counts as acoustic prediction error.

**Irreducible residual (~25%):** Cultural specification of soundscape categories (~15% — what counts as "pleasant" varies substantially by culture) and spectrotemporal complexity preferences (~10% — acoustic texture preference principles not fully specified).

#### 76.3 Place Attachment: Temporal Depth and Biographical Integration {#763-place-attachment}

Place Attachment (Scannell & Gifford, 2010; approximately 3,000 GS for the tripartite model) was the third February 21 reduction and introduced a unique feature: it organizes phenomena around *temporal depth* rather than immediate response, distinguishing it from all other T1.5 theories. The six phenomena: (PA-A) place familiarity and habitat security (length of residence → embodied security), (PA-B) episodic memory binding to place (events become autobiographically tied to spatial context), (PA-C) place identity and self-concept integration (place becomes component of self), (PA-D) territorial familiarity and spatial ownership (defended territory → stronger attachment), (PA-E) rootedness versus sense of place (implicit taken-for-granted versus explicit articulated appreciation), and (PA-F) disrupted attachment and post-displacement grief (forced relocation produces bereavement-like responses).

**Parent T1 mappings:** MS 35% (hippocampal episodic binding, place cell reinstatement during retrieval), SN 25% (cognitive map consolidation, allocentric representation), IC 15% (body-budget familiarity, allostatic calibration, grief as interoceptive disruption), IE-DPT 15% (meaning-construction, agency-investment, and a critically new concept — the "sedimentation principle" whereby explicit-channel processing over biographical timescales sediments into implicit experience).

**Template coverage:** ~60% (the lowest of the three, reflecting the temporal-depth challenge).

**Critical finding: the Biographical Explicit Integration (BEI) requirement.** The Place Attachment reduction revealed that IE-DPT requires *temporal extension* beyond its current operating timescale (minutes to hours). Place attachment builds over months and years as explicit evaluations ("I chose this neighbourhood," "my children grew up here") gradually sediment into implicit embodied security ("this feels like home"). This process — which the panel tentatively called "Biographical Explicit Integration" — requires a meta-template describing how explicit-channel processing at long timescales transforms implicit experience. Current IE-DPT operates at the session timescale; Place Attachment demands a biographical timescale extension.

**Architectural example: post-displacement grief.** When a long-term resident is displaced by urban renewal, the grief response (PA-F) is mechanistically interpretable as massive interoceptive disruption: the body's allostatic calibration, built over years of habituation to specific spatial, thermal, acoustic, and social patterns, suddenly confronts an environment that violates every calibrated expectation. This is not mere inconvenience but a body-budget crisis (IC framework) combined with hippocampal reinstatement failure (episodic memories cued by absent spatial contexts) and SN disorientation (cognitive map suddenly invalid). The grief is proportional to the depth of attachment, which is proportional to the degree of allostatic and episodic calibration that has accumulated.

**Irreducible residual (~40%):** The largest of any formal T1.5 reduction. Cultural specification of attachment objects (~15%), social and relational attachment where community bonds are load-bearing (~15%), and narrative and cultural heritage attachment (~10%). The social-relational component is particularly consequential: people are often attached to *communities in places* more than to physical places themselves, and this social dimension resists neural-architectural reduction.

#### 76.4 Nine Proposed New Templates {#764-proposed-templates}

The three reductions collectively proposed nine new templates:

**Space Syntax templates:**
- SS1: Syntactic Integration and Cognitive Map Efficiency (SN + PP)
- SS2: Intelligibility and Predictive Spatial Inference (PP + SN)
- SS3: Isovist Affordance and Perceived Spatial Control (EC + IC + NM)

**Soundscape templates:**
- SOC1: Acoustic Expectation Violation and Soundscape Appraisal (PP + IC + NM)
- SOC2: Acoustic Body-Budget Threat and Cardiovascular Risk (IC + NM)
- SOC3: Restorative Soundscape and ANS Recovery (PP + NM + IC)

**Place Attachment templates:**
- PA1: Biographical Episodic Binding and Place Attachment (MS + SN)
- PA2: Allostatic Calibration and Embodied Security (IC + EC)
- PA3: Displacement Grief and Interoceptive Disruption (IC + MS)

These remain proposed; implementation requires calibration panel review.

**References for §76:**

Hillier, B., & Hanson, J. (1984). *The social logic of space*. Cambridge University Press. [~7,000 GS]

ISO 12913-1:2014. *Acoustics — Soundscape — Part 1: Definition and conceptual framework*. International Organization for Standardization.

Scannell, L., & Gifford, R. (2010). Defining place attachment: A tripartite organizing framework. *Journal of Environmental Psychology*, *30*(1), 1–10. [~3,000 GS]

Schafer, R. M. (1977). *The soundscape: Our sonic environment and the tuning of the world*. Destiny Books. [~5,000 GS]

---

### §77. The Remaining Reductions: Privacy Regulation through Flow Theory {#77-remaining-reductions}

#### 77.1 Privacy Regulation: The IE-DPT Bridge par excellence {#771-privacy-regulation}

Privacy Regulation Theory (Altman, 1975; approximately 4,500 GS) was reduced in the February 20 operationalization phase. Its five constructs — Desired Privacy, Privacy Regulation Mechanisms, Crowding, Isolation, and Territory — collectively achieve approximately 86% template coverage. The parent T1 distribution: IC 30%, SN 20%, NM 15%, EC 15%, IE-DPT 20%.

The theory provides the textbook demonstration of IE-DPT's explanatory necessity. Stokols' (1972) density-is-not-crowding finding — that identical physical density produces crowding in one context (unwanted gatherings) and pleasant atmosphere in another (desired social events) — is inexplicable without the explicit channel. The mechanism: the activity frame (IE-DPT) configures interoceptive expectations (IC), which determines whether proximity generates positive (low interoceptive PE, social reward via NM) or negative (high interoceptive PE, boundary violation via T5) affective response. Without IE-DPT, the system would predict identical responses to identical physical conditions, which is empirically false.

The five construct reductions: Desired Privacy (80% coverage) maps to IC2 body-budget prediction + T7 environmental predictability + T_IE_001 activity frame. Privacy Regulation Mechanisms (90%) map to T8 affordances + ENCLOSURE + SC2 isovist + T28 legibility. Crowding (90%) maps to T5 boundary violation + AX4 perceived control loss + IC2 interoceptive PE + T29 allostatic demand. Isolation (80%) maps to T50 social load deficit + T27 DMN hyperengagement + NM3 dopaminergic deficit. Territory (90%) maps to SN1 place recognition + E1 hippocampal binding + T66 learned safety.

**Architectural example: the open-plan office.** The open-plan office violates Privacy Regulation at multiple levels simultaneously: low territorial control (no spatial ownership), minimal regulation mechanisms (no enclosure, no isovist control), chronic crowding (unwanted proximity without escape affordance), and privacy-activity incompatibility (concentration tasks in surveillance-rich environments). The reduction predicts chronic interoceptive PE (IC), sustained HPA activation (T5 via AX4 control loss), and cognitive performance decrements (directed attention consumed by incompatibility). This is precisely the pattern observed in the open-plan literature (Bernstein & Turban, 2018).

#### 77.2 Kaplan Preference Matrix: Prediction Error Landscape {#772-kaplan-preference-matrix}

The Kaplan Preference Matrix (Kaplan & Kaplan, 1989; approximately 5,000 GS) was reduced in the same February 20 phase. All four variables — Coherence, Complexity, Legibility, and Mystery — achieve approximately 85% template coverage and prove to be aspects of a unified prediction error landscape:

**Coherence** (low aggregate PE → fluency → preference) maps to T1 visual statistics + T22 rapid gist + T67 processing fluency. **Complexity** (moderate PE → engagement on inverted-U) maps to VF2 visual rhythm + NM2 novelty dopamine + COL1 colour PE. **Legibility** (low spatial PE → confident mapping) maps to T3 spatial maps + SC1 integration + T28 landmarks. **Mystery** (anticipated PE reduction → dopaminergic wanting) maps to SC3 promenade sequencing + NM2 novelty anticipation + SC2 isovist + ENCLOSURE safety gate.

The critical finding: the Kaplan Matrix may *be* Predictive Processing applied to environmental scenes. Each variable corresponds to a specific region of the prediction error landscape — Coherence to the low-PE fluency zone, Complexity to the moderate-PE engagement zone, Legibility to the spatial-PE confidence zone, and Mystery to the anticipated-PE-reduction reward zone. The irreducible residuals (semantic coherence, expertise-dependent optima, mystery-danger interaction) all require IE-DPT for their explanation, reinforcing the pattern of T1.5 theories converging on the explicit channel.

**Parent T1 mappings:** PP 40%, SN 20%, NM 20%, EC 10%, IE-DPT 10%.

#### 77.3 Adaptive Thermal Comfort: Why Fanger Fails in NV Buildings {#773-adaptive-thermal-comfort}

Adaptive Thermal Comfort (de Dear & Brager, 1998; approximately 5,000 GS) was the third February 20 reduction. Its four constructs — Thermal Neutrality, Behavioural Adaptation, Physiological Adaptation, and Psychological Adaptation — achieve 80-90% template coverage. Parent T1 distribution: IC 35%, PP 20%, EC 15%, NM 15%, IE-DPT 15%.

The architectural consequence is direct and practically important: Fanger's Predicted Mean Vote (PMV) model fails in naturally ventilated (NV) buildings because it ignores the explicit channel entirely. In mechanistic terms: NV building selection (explicit activity frame, IE-DPT) → recalibrated thermal expectations (IC2 body-budget prediction shifted by explicit knowledge) → narrower interoceptive PE for wider temperature ranges → wider comfort band. Fanger's model, calibrated in sealed climate chambers, assumes a fixed comfort band independent of building type — it has no representation of the explicit channel's recalibration effect. The ASHRAE adaptive comfort standard (de Dear & Brager, 1998) empirically corrects for this without explaining why; the T1.5 reduction provides the mechanistic explanation.

**Architectural example: thermal pleasure in hammams.** The traditional Turkish hammam uses temperature extremes (hot room ~45°C, cold plunge ~15°C) to produce thermal pleasure through the allesthesia mechanism: when the body is hyperthermic, cold stimulation produces intense pleasure because it corrects the homeostatic deviation (Cabanac, 1971). Fanger's PMV would predict extreme discomfort at both temperatures; the adaptive framework, enriched by the allesthesia mechanism and IE-DPT (the bather explicitly *expects* and *desires* the thermal extremes), predicts pleasure. The four-construct reduction captures this: Thermal Neutrality (deviation from set-point), Behavioural Adaptation (choosing to enter), Physiological Adaptation (vasomotor adjustment), and Psychological Adaptation (explicit frame shifts expectation).

#### 77.4 BRECVEMA: Eight Music-Emotion Mechanisms {#774-brecvema}

BRECVEMA (Juslin, 2013; approximately 3,000 GS) was accepted by the February 23 Expansion Panel with HIGH confidence. The theory organizes eight distinct mechanisms by which music induces emotion: (1) Brainstem Reflex (NM + IC: spectral envelope and intensity produce arousal/valence polarity), (2) Rhythmic Entrainment (PP + MSI: metrical regularity produces motor synchrony and affect), (3) Evaluative Conditioning (DP + IC: learning history associates musical features with emotions), (4) Contagion (NM + DP: emotional expression markers produce automatic resonance), (5) Visual Imagery (PP + EC: titles and narrative context produce emotional enrichment), (6) Episodic Memory (MS + IC: musical cues reactivate autobiographical memories and their associated affects), (7) Musical Expectancy (PP + MSI: structural regularity violations produce pleasure through PE resolution), and (8) Aesthetic Judgment (IC + DP: integration of all seven into an overall aesthetic evaluation).

**T1 coverage:** ~85% (NM 25%, IC 25%, PP 20%, MSI 15%, DP 10%, MS 5%). Template assignments include eight explicit mechanism templates (BRECVEMA_BRAINSTEM_001 through BRECVEMA_AESTHETIC_001) plus two proposed additions (evaluative conditioning and visual imagery templates).

**Architectural relevance:** Background music in retail, healthcare, and workspace environments engages all eight mechanisms, but current acoustic design considers only Brainstem Reflex (volume, spectral content). The BRECVEMA reduction suggests that musical programme design should consider Rhythmic Entrainment (tempo matching desired activity pace), Evaluative Conditioning (genre associations with brand or institutional identity), and Musical Expectancy (complexity level matching occupant cognitive load).

The panel debate centred on whether BRECVEMA is a *taxonomy* (mere list of mechanisms) or a *theory* (generating predictions beyond the list). The verdict: it qualifies as T1.5 because the eight mechanisms interact — Episodic Memory amplifies Contagion when autobiographical context is musically cued, Musical Expectancy modulates Brainstem Reflex sensitivity — and these interactions are organized by Aesthetic Judgment in a way that exceeds any individual mechanism template.

#### 77.5 Flow Theory: Challenge-Skill Balance Decomposed {#775-flow-theory}

Flow Theory (Csikszentmihalyi, 1990; approximately 80,000 GS — by far the most cited T1.5 theory in the system) was accepted with MEDIUM-HIGH confidence. The theory organizes seven phenomena: (1) Challenge-Skill Balance (DP + NM: task difficulty matched to skill produces inverted-U engagement), (2) Loss of Self-Consciousness (DP + DT: working memory saturation eliminates self-monitoring), (3) Time Distortion (PP: temporal prediction error falls below threshold), (4) Intrinsic/Autotelic Motivation (NM + IC: dopamine for exploration combined with embodied satisfaction), (5) Peak Performance (DP + EC: sensorimotor optimization), (6) Goal Clarity (DT: clear targets reduce decision cost), and (7) Absorption/Presence (EC + IC: sensory immersion and proprioceptive coherence).

**T1 coverage:** ~75% (DP 30%, DT 25%, NM 20%, PP 15%, EC 10%). The irreducible residuals are substantial: trait flow proneness (~10%), expertise-domain specificity (~10%), and hedonic set-point (~5%).

**Architectural relevance:** Workspace design for creative flow requires: (a) challenge-skill matched task environments (not too distracting, not too sterile), (b) elimination of external interruption (which breaks working memory saturation, restoring self-consciousness), (c) temporal autonomy (clock-free environments may facilitate time distortion), and (d) sensory immersion appropriate to the task (the right level of ambient stimulation for EC + IC engagement). The connection to ART is noteworthy — flow and restoration may be complementary states: ART restores the directed attention resources that flow then consumes, and flow depletion creates the precondition for ART restoration.

#### 77.6 Fractal Fluency and Prospect-Refuge as Independent Entries {#776-independent-entries}

Although Fractal Fluency and Prospect-Refuge were originally reduced as components of the Biophilia cluster (§75), they also appear on the formal T1.5 roster as independent entries because each organizes a distinct family of phenomena beyond its biophilic context. Fractal Fluency applies to abstract art, interior surface design, and mathematical pattern generation — not exclusively to nature. Prospect-Refuge applies to urban design, institutional architecture, and workspace layout independently of natural elements. Their independent T1.5 status reflects the fact that each generates predictions in non-biophilic architectural contexts, though their biophilic instantiation remains the strongest evidence base.

**References for §77:**

Altman, I. (1975). *The environment and social behavior*. Brooks/Cole. [~4,500 GS]

Bernstein, E. S., & Turban, S. (2018). The impact of the "open" workspace on human collaboration. *Philosophical Transactions of the Royal Society B*, *373*(1753), 20170239. [~500 GS]

Cabanac, M. (1971). Physiological role of pleasure. *Science*, *173*(4002), 1103–1107. [~2,000 GS]

Csikszentmihalyi, M. (1990). *Flow: The psychology of optimal experience*. Harper & Row. [~80,000 GS]

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, *104*(1), 145–167. [~5,000 GS]

Juslin, P. N. (2013). From everyday emotions to aesthetic emotions: Towards a unified theory of musical emotions. *Physics of Life Reviews*, *10*(3), 235–266. [~3,000 GS]

Kaplan, R., & Kaplan, S. (1989). *The experience of nature*. Cambridge University Press. [~6,000 GS]

Stokols, D. (1972). On the distinction between density and crowding. *Psychological Review*, *79*(3), 275–277. [~2,000 GS]

---

### §78. Rejected and Deferred Candidates {#78-rejected-and-deferred-candidates}

#### 78.1 Six Rejected Theories and Why {#781-rejected-theories}

The February 23 Expansion Panel evaluated thirteen candidate theories against the T1.5 qualification criteria. Six were rejected:

**Proxemics** (Hall, 1966; ~15,000 GS). REJECTED with HIGH confidence. Despite strong neural evidence (Kennedy et al., 2009, showing that amygdala lesion eliminates personal space maintenance), Proxemics collapses into Privacy Regulation (which already captures personal distance through IC + SN + NM templates) plus the SN spatial navigation framework. The personal-space-distance findings are accommodated by existing templates without requiring a separate T1.5 theory. Proxemics is better understood as an empirical regularity explained by Privacy Regulation than as an independent organizing theory.

**Cognitive Map Theory** (O'Keefe & Nadel, 1978; ~12,000 GS). REJECTED with HIGH confidence. Cognitive Map Theory is not a T1.5 domain theory but is essentially identical to the SN (Spatial Navigation) Tier 1 framework itself. Place cells, grid cells, and allocentric representation are already core components of SN. Elevating Cognitive Map Theory to T1.5 would create a circular reduction (SN explaining itself). The phenomena it organizes (place cell firing, spatial memory, navigation) are already T1 phenomena, not a domain-level family requiring decomposition.

**Chronobiology / Circadian Theory** (large literature). REJECTED with HIGH confidence. Same structural problem as Cognitive Map Theory: Chronobiology is essentially the CB (Circadian/Biological Rhythms) Tier 1 framework. Entrainment, melatonin, SCN function, and light as zeitgeber are already T1 components. A T1.5 reduction of Chronobiology would reduce CB to itself.

**Defensible Space / CPTED** (Newman, 1972; ~4,000 GS). REJECTED with MEDIUM confidence (lower confidence reflecting genuine debate). The theory asserts that spatial design features (surveillance, territorial reinforcement, access control, image maintenance) reduce crime. However, Merry's (1981) critique demonstrated that surveillance-crime relationships are confounded by social variables that CPTED ignores. The panel concluded that CPTED is an architectural application framework, not a theory with deductive structure that could be formally reduced. It makes predictions, but the predictions are confounded by unmeasured social factors, violating the construct validity requirement.

**Allesthesia** (Cabanac, 1971; ~2,000 GS). REJECTED with MEDIUM-HIGH confidence. Allesthesia — pleasure from homeostatic correction — names a single mechanism (deviation from set-point → correction → hedonic signal) rather than organizing a family of phenomena. It belongs at T2 (a template-level mechanism within the IC framework) rather than T1.5. Allesthesia is already captured by the IC interoceptive prediction error mechanism and does not generate predictions beyond what IC templates predict.

**Mehrabian-Russell PAD Model** (1974; ~6,000 GS). REJECTED with MEDIUM-HIGH confidence. The Pleasure-Arousal-Dominance dimensional model has extensive empirical use in retail and workspace environments, but upon formal reduction it decomposes cleanly into IC (interoceptive affect mapping onto Pleasure and Arousal dimensions) + NM (neuromodulatory arousal) + DP (dual processing for the Dominance dimension) without generating an independent organizing principle. There is no irreducible residual beyond what these T1 frameworks already explain — precisely the condition that distinguishes a T1.5 theory (partial reducibility with meaningful residual) from a derived construct (full reducibility).

**Free Energy Minimization** (Friston, 2010). REJECTED with HIGH confidence. This is a mathematical formalism *of* the PP (Predictive Processing) Tier 1 framework, not a separate domain theory. Treating it as T1.5 would create a framework-explaining-itself circularity.

#### 78.1a Pedagogical Sidebar: How a Reduction Fails — The Case of the PAD Model {#781a-pad-reduction-failure}

To illustrate the epistemic discipline underlying the T1.5 qualification process, we trace the *attempted* reduction of the Mehrabian-Russell PAD (Pleasure-Arousal-Dominance) model in detail, showing precisely where and why it fails the irreducible-residual criterion.

**Step 1: Construct Identification.** The PAD model proposes three orthogonal dimensions of affective response to environments: Pleasure (hedonic valence), Arousal (activation level), and Dominance (perceived control over the environment). Mehrabian and Russell (1974) developed this model from factor analysis of semantic differential ratings of 60 environmental descriptors, yielding a three-factor solution accounting for ~65% of affective variance. The model has been applied extensively in retail (Donovan & Rossiter, 1982; ~3,500 GS), workspace design (Küller et al., 2006; ~400 GS), and virtual environments (Riva et al., 2007; ~300 GS).

**Step 2: Attempted T1 Decomposition.**

*Pleasure dimension*: Maps directly to IC (Interoceptive Construction) — specifically, the valence dimension of Barrett's (2017) constructionist emotion theory, in which affective valence is the brain's summary representation of the body's metabolic state (allostatic prediction error). The architectural features that determine Pleasure (color warmth, spatial proportion, material texture, view content) are already parameterized in IC templates (IC1-IC4). T1 coverage of Pleasure: ~90%.

*Arousal dimension*: Maps to NM (Neuromodulatory Systems) — specifically, the ascending reticular activating system (ARAS) and its modulation by sensory input intensity, novelty, and complexity. The architectural features that determine Arousal (lighting level, spatial complexity, acoustic intensity, temperature deviation) are parameterized in NM templates (NM1-NM3). Additionally, PP (Predictive Processing) contributes: arousal is partially a function of prediction-error magnitude (unexpected features increase arousal). T1 coverage of Arousal: ~85%.

*Dominance dimension*: Maps to DP (Dual-Process Evaluation) — specifically, the explicit appraisal of control and agency over environmental conditions. The AX4 template (Perceived Control and Predictability) captures Dominance directly: occupants who perceive high control over their environment report higher Dominance ratings. IC contributes through interoceptive prediction confidence (when the body's metabolic prediction is confirmed, Dominance increases). T1 coverage of Dominance: ~80%.

**Step 3: Residual Analysis.** After decomposing all three PAD dimensions into T1 frameworks, what remains? The critical question for T1.5 qualification is whether the *combination* of P, A, and D — the claim that these three dimensions jointly organize environmental affect in a way not captured by their individual T1 reductions — constitutes a genuine irreducible residual.

The answer is no. The PAD model's organizing contribution is that environmental affect has three independent dimensions. But this dimensional structure is itself a consequence of the T1 frameworks: IC generates valence (Pleasure), NM + PP generate activation (Arousal), and DP + IC generate agency appraisal (Dominance). The *independence* of the three dimensions follows from the functional independence of IC valence computation, NM/PP arousal computation, and DP/IC control appraisal. There is no organizing principle in the PAD model beyond what the T1 frameworks individually and jointly predict.

Contrast this with ART (Attention Restoration Theory), which *does* have an irreducible residual: the claim that four specific constructs (Soft Fascination, Being Away, Extent, Compatibility) form a coherent *syndrome* of restoration is not derivable from any single T1 framework or their conjunction. The syndrome structure — the specific way these four constructs combine — is an emergent theoretical contribution not present in the T1 decomposition. ART qualifies as T1.5 because its organizing principle (the four-construct syndrome) adds explanatory content beyond the sum of its T1 components.

The PAD model, by contrast, adds no such organizing content. Its dimensions are recoverable from T1 frameworks, and their independence follows from T1 functional architecture. This is the difference between a *derived construct* (PAD: full reducibility, no meaningful residual) and a *genuine domain theory* (ART: partial reducibility with meaningful residual). The demarcation criterion — whether the theory's organizing principle survives reduction — is the epistemic core of the T1.5 qualification process.

This worked example of a *failed* reduction illustrates why the T1.5 category is not merely a matter of citation count or empirical support. The PAD model is extensively cited (~6,000 GS), widely used, and empirically productive. Its rejection as T1.5 reflects not a judgment about its quality but about its *theoretical independence* from T1 frameworks. A theory that fully reduces adds no new explanatory content; it is parasitic on its reductants. T1.5 status requires irreducible residual — the theory must contribute something that its T1 components, individually or jointly, cannot reconstruct.

---

#### 78.2 Four Deferred Candidates {#782-deferred-candidates}

Four candidates were deferred, each failing the 60% template coverage threshold:

**Episodic Memory Theory** (Tulving, 1972; ~30,000+ GS). Coverage: 3.4% (7 templates). The theory is well-established and highly cited but faces the T1-adjacency problem: episodic memory is already substantially captured by the MS (Memory Systems) Tier 1 framework. The panel deferred rather than rejected because architectural episodic memory phenomena (place-bound autobiographical recall, nostalgia in heritage buildings, memory palaces) may constitute an organized family distinct from generic episodic memory. However, achieving 60% template coverage would require extensive new template development.

**Berlyne's New Experimental Aesthetics** (1971; ~8,000 GS). Coverage: 1.0% (2 templates). The inverted-U complexity preference and collative variables are well-established but may collapse into the Kaplan Preference Matrix upon formal comparison. The panel could not determine whether Berlyne and Kaplan are genuinely distinct T1.5 theories or two formulations of the same PP-based prediction error landscape. Deferred pending a formal comparison study. **Update (February 25, 2026):** The introduction of the Goldilocks Principle (§78.2a) resolves this deferral by subsumption — Berlyne's inverted-U is a special case (visual complexity domain) of the cross-modal PE optimization mechanism that the Goldilocks Principle formalizes. Berlyne described the curve; the Goldilocks Principle specifies the neural mechanism (PP + IC + NM + IE-DPT) that produces it across all modalities.

**Predictive Coding of Music** (Koelsch, 2014). Coverage: 1.0% (2 templates). Likely a T2 mechanism within BRECVEMA (specifically the Musical Expectancy mechanism) rather than an independent T1.5 theory. Deferred pending BRECVEMA template development to verify whether it is subsumed.

**Auditory Scene Analysis** (Bregman, 1990; ~5,000 GS). Coverage: 1.4% (3 templates). The strongest deferred candidate. ASA organizes genuine families of auditory phenomena (stream segregation, grouping principles, primitive vs. schema-based processing) with clear T1 mappings. However, achieving 60% coverage would require approximately 120 new templates, which the panel judged impractical in the near term. The candidate remains viable for future reduction if the template library expands to cover auditory mechanisms more thoroughly.

#### 78.2a The Goldilocks Principle: A Cross-Modal T1.5 Theory (February 25, 2026) {#782a-goldilocks-principle}

The Goldilocks Principle represents a distinctive kind of T1.5 theory — one that the ATLAS system itself generated through the process of building and calibrating templates across domains, rather than one imported from the environmental psychology literature. The observation that motivated its formalization is straightforward: at least 39 of the 208 templates in the ATLAS system library contain inverted-U response curves, and these curves appear across every sensory modality the system covers — visual complexity, luminance contrast, thermal comfort, acoustic environments, temporal variation in lighting, spatial sequence pacing, social density, and cognitive complexity for creativity. The question is whether this cross-modal regularity is a coincidence (each domain happens to have an inverted-U for domain-specific reasons) or whether it reflects a single underlying mechanism operating across the predictive hierarchy.

The answer, we argue, is the latter. The Goldilocks Principle asserts that all sensory channels optimize within the same prediction error efficiency framework, and that this optimization is a fundamental property of predictive brains operating under metabolic constraints. The mechanism has four components:

**Component 1: Prediction Error Optimization (PP).** The core claim is that for any sensory channel, there exists an intermediate level of prediction error that maximizes positive affect and engagement. Too little PE means the generative model has fully predicted the environment — the organism is in a state of allostatic underload where no learning occurs and no reward is generated. Too much PE means the generative model is failing — error signals cascade through the hierarchy, consuming metabolic resources without converging on a useful update. The optimum corresponds to resolvable PE: stimulation that challenges the generative model enough to produce incremental learning and model refinement. This is the PE-level version of Vygotsky's zone of proximal development, applied not to pedagogical scaffolding but to sensory environments. The inverted-U shape arises because the relationship between PE magnitude and learning efficiency is inherently non-monotonic — beyond a critical PE threshold, the generative model cannot assimilate the error signal, and the system switches from model-updating mode (positive affect, approach motivation) to error-rejection mode (negative affect, avoidance). Template PP_COMPLEXITY_GOLDILOCKS_002 captures this at the visual complexity level; the Goldilocks Principle generalizes it to all modalities.

**Component 2: Metabolic Efficiency Window (IC).** The inverted-U is not merely a preference curve but reflects a metabolic constraint documented in the allostatic regulation literature (Sterling, 2012; Kleckner et al., 2017). The brain's predictive hierarchy operates within an energy budget managed by interoceptive systems (IC framework). Moderate PE is metabolically efficient: the generative model updates incrementally, each update costing a small metabolic increment. Zero PE is metabolically inefficient in a different way: the model is over-fitted to the current environment and not learning, but maintenance costs continue. High PE is acutely metabolically expensive: error-correction cascades activate multiple cortical and subcortical regions simultaneously, driving cortisol release (HPA axis), sympathetic arousal, and inflammatory markers. The optimal zone — where learning rate per metabolic unit is maximized — is the Goldilocks zone. Template ALLOSTATIC_MASTER_001 formalizes the metabolic accounting; its interaction with PP_COMPLEXITY_GOLDILOCKS_002 is typed as PRODUCES in the molecule's interaction graph.

**Component 3: Reward at Optimum (NM).** At the moderate PE optimum, three neuromodulatory systems converge to generate positive affect: dopaminergic novelty reward (via VTA → NAcc, responding to resolvable PE as a learning signal), serotonergic safety signaling (from DRN, responding to the predictability of the environment within the comfort zone — the organism is safe enough to explore), and opioidergic pleasure from successful model updating (the "click" of comprehension, the aesthetic pleasure of a pattern resolved). This triple convergence explains why the preference peak is robust across modalities: it is not merely the absence of negative affect (which would predict a monotonically decreasing curve with increasing stimulation) but the active generation of positive affect through successful prediction. The reward signal is what makes the Goldilocks zone feel good, not just feel safe.

**Component 4: Individual Differences via Prior Expectations (IE-DPT).** The location of the optimum is person-dependent because PE is computed relative to prior expectations, and prior expectations are shaped by individual experience, expertise, personality traits, and cultural context. An acoustician habituated to 85 dB finds 60 dB unremarkable; a librarian finds it distressing. A construction worker's thermal neutral zone is shifted by chronic outdoor exposure. An art expert tolerates (and prefers) higher visual complexity than a novice because their generative model for visual art is more elaborated — they can resolve PE that would overwhelm a non-expert. This person-dependence is irreducible: the same physical environment generates different PE profiles in different individuals. The IE-DPT framework's contribution is to explain why the curve shape is universal (all predictive brains have metabolic constraints) while the curve location is individual (the baseline from which PE is computed varies). Template DP_IMPLICIT_EVALUATION_001 and ER_ECOLOGICAL_RATIONALITY_001 capture this.

**Domain-Specific Calibrations.** The Goldilocks Principle's power lies in its cross-modal generality, but its practical value lies in the domain-specific calibrations that locate the optimum for each modality. These calibrations come from the ATLAS system template library:

Visual complexity: fractal dimension D ≈ 1.3, corresponding to 1/f^β power spectra with β ≈ 2.6 (Taylor et al., 2011; PP_SPECTRAL_MATCH_001). Preference peak at intermediate fractal complexity, d = 0.35 for natural-vs-random comparisons.

Luminance contrast: global ratio 1:7 to 1:15 for aesthetic spaces (Strother); coefficient of variation 0.5–1.5 for comfort; dramatic/awe-inducing spaces permit CV > 1.5 but only with bright zone occupying < 20% of visual field (LUM_CONTRAST_PE_001).

Thermal comfort: adaptive neutral = 0.31 × T_running_mean + 17.8°C. Comfort zone ±1°C; positive alliesthesia (thermal delight) at ±1–3°C when directionally corrective; tolerance ±3–5°C; discomfort beyond ±5°C (de Dear & Brager, 1998; THERMAL_ADAPTIVE_PE_001).

Acoustic environments: peak pleasantness at 50–60 dB LAeq. Below 45 dB: boring/unsettling ("too quiet"). Above 70 dB: aversive. Natural sound content shifts the optimum upward by +5–10 dB via biophilic reward (AUD_SCENE_ANALYSIS_001; ISO 12913).

Temporal variation: light variation at 0.01–2.0 cycles/min for sustained engagement; amplitude 8–35% of mean luminance. Architectural promenade: optimal threshold density along movement path — the compression-release rhythm must allow recovery between events (DYNAMIC_LIGHT_TEMPORAL_001; ARCH_PROMENADE_TEMPORAL_PE_001).

Social density: 3–5 simultaneous social modes supported by spatial configuration. Dunbar saturation: monitoring cost exceeds social benefit when > 6 conversational groups occupy the visual field (XF_SOCIAL_AFFORDANCE_DENSITY_001).

**Irreducible Residual.** The Goldilocks Principle's irreducible residual is the cross-modal universality claim itself. No single T1 framework captures the assertion that all sensory channels optimize within the same PE efficiency framework. PP explains the inverted-U shape. IC explains the metabolic constraint. NM explains the reward at optimum. IE-DPT explains individual differences. But the claim that these four mechanisms interact to produce a universal cross-modal optimality principle — that there is a single Goldilocks zone phenomenon instantiated differently across domains — is the Goldilocks Principle's distinctive contribution. This contribution subsumes both Berlyne's optimal arousal theory (which described the curve without specifying the mechanism) and the Kaplan Preference Matrix (which specified environmental parameters for preference without providing the neural implementation). The domain-specific optima — fractal D ≈ 1.3, thermal neutral ±1°C, acoustic 50–60 dB, luminance CV 0.5–1.5 — are calibrated instances of a single underlying principle, not independent phenomena. The unification is a genuine theoretical contribution of the ATLAS system, not a reorganization of existing knowledge but an explanation of why existing theories work.

**Compositional Adequacy:** INTERACTION_DEPENDENT. The Goldilocks zone in any single domain requires the interaction of at least PP (generating the inverted-U) and IC (providing the metabolic constraint). Neither framework alone produces the zone. The cross-modal claim additionally requires NM (for the reward mechanism) and IE-DPT (for person-dependent optima).

**Schema Gaps.** Three gaps remain: (1) the olfactory Goldilocks zone has not been templated — scent intensity optima likely follow the same PE curve but no ATLAS template exists; (2) cross-modal interaction effects on zone boundaries are incompletely specified — does thermal comfort expand the visual complexity tolerance window? Parsons and Hartig (2000) suggest it does, but the interaction has not been formally modeled; (3) the developmental trajectory of optima is unknown — do children have different Goldilocks zones than adults? Preliminary evidence (Berto et al., 2015) suggests children prefer higher visual complexity than adults, consistent with less-elaborated generative models generating lower PE at the same stimulus level.

**Formal Status.** The Goldilocks Principle has been added as the 13th T1.5 theory with a formal JSON definition file (`data/theories/goldilocks_principle.json`) and a companion PHENOMENON-type molecule (`data/molecules/goldilocks_principle.json`) containing 16 constituent templates, 6 named components (Visual Complexity Optimum, Thermal Comfort Optimum, Acoustic Comfort Optimum, Temporal Variation Optimum, Social Density Optimum, Cognitive Complexity Optimum), and 7 practitioner-facing design implications. The molecule's interaction graph specifies SYNERGISTIC edges between visual complexity and luminance contrast, between light variation and architectural promenade thresholds, and between creativity templates — and MODULATES edges where thermal comfort affects visual complexity tolerance.

**References for §78.2a:**

Berlyne, D. E. (1971). *Aesthetics and psychobiology*. Appleton-Century-Crofts. [~8,000 GS]

Cabanac, M. (1971). Physiological role of pleasure. *Science*, *173*(4002), 1103–1107. [~2,000 GS]

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, *104*(1), 145–167. [~5,000 GS]

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, *11*(2), 127–138. [~15,000 GS]

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. [~5,000 GS]

Kleckner, I. R., Zhang, J., Touroutoglou, A., Chanes, L., Xia, C., Simmons, W. K., ... & Barrett, L. F. (2017). Evidence for a large-scale brain system supporting allostasis and interoception in humans. *Nature Human Behaviour*, *1*(5), 0069. [~600 GS]

Parsons, R., & Hartig, T. (2000). Environmental psychophysiology. In J. T. Cacioppo, L. G. Tassinary, & G. G. Berntson (Eds.), *Handbook of psychophysiology* (2nd ed., pp. 815–846). Cambridge University Press. [~200 GS]

Sterling, P. (2012). Allostasis: A model of predictive regulation. *Physiology & Behavior*, *106*(1), 5–15. [~1,500 GS]

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2011). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience*, *5*, 60. [~400 GS]

Vessel, E. A., Starr, G. G., & Rubin, N. (2012). The brain on art: Intense aesthetic experience activates the default mode network. *Frontiers in Human Neuroscience*, *6*, 66. [~600 GS]

Wundt, W. (1874). *Grundzüge der physiologischen Psychologie*. Engelmann.

---

#### 78.3 The Canonical T1.5 Roster {#783-canonical-roster}

As of February 24, 2026 (updated March 2, 2026), thirteen domain theories hold formal T1.5 status, each with documented reduction, parent T1 mappings, coverage fraction, and irreducible residual:

| # | Theory | Key Citation | GS | Parent T1s | Coverage | Maturity |
|---|--------|-------------|-----|-----------|----------|----------|
| 1 | ART | Kaplan, 1995 | ~4,800 | PP, SN, DT, NM | ~70% | *how-plausibly* |
| 2 | SRT | Ulrich, 1983 | ~3,000 | IC, NM, PP | ~85% | *how-actually* |
| 3 | Biophilia | Wilson, 1984 | ~15,000 | EC, PP, SN, NM | ~65% | *how-plausibly* |
| 4 | Prospect-Refuge | Appleton, 1975 | ~3,000 | SN, PP, NM, EC | ~70% | *how-plausibly* |
| 5 | Privacy Regulation | Altman, 1975 | ~4,500 | IC, NM, SN, EC, IE-DPT | ~86% | *how-plausibly* |
| 6 | Kaplan Preference Matrix | Kaplan & Kaplan, 1989 | ~5,000 | PP, SN, NM, EC, IE-DPT | ~85% | *how-plausibly* |
| 7 | Adaptive Thermal Comfort | de Dear & Brager, 1998 | ~5,000 | IC, PP, EC, NM, IE-DPT | ~85% | *how-plausibly* |
| 8 | Space Syntax | Hillier & Hanson, 1984 | ~7,000 | SN, PP, EC, IE-DPT | ~70% | *how-plausibly* |
| 9 | Soundscape Theory | Schafer, 1977 | ~5,000 | PP, IC, NM, MSI, IE-DPT | ~75% | *how-plausibly* |
| 10 | Place Attachment | Scannell & Gifford, 2010 | ~3,000 | MS, SN, IC, IE-DPT | ~60% | *how-possibly* |
| 11 | BRECVEMA | Juslin, 2013 | ~3,000 | NM, IC, PP, MSI, DP, MS | ~85% | *how-plausibly* |
| 12 | Flow Theory | Csikszentmihalyi, 1990 | ~80,000 | DP, DT, NM, PP, EC | ~75% | *how-plausibly* |
| 13 | Goldilocks Principle | Kirsh et al. (ATLAS), 2026 | — | PP, IC, NM, IE-DPT, EC | ~80% | *how-plausibly* |

Two patterns emerge from the completed roster. First, IE-DPT appears as a parent framework in eight of thirteen theories (Privacy Regulation, Kaplan Matrix, Adaptive Thermal Comfort, Space Syntax, Soundscape, Place Attachment, Goldilocks Principle, and implicitly in ART's Compatibility construct), confirming its superordinate role as the system's configuring framework. Second, the three most mature reductions (SRT *how-actually*, Privacy Regulation, Adaptive Thermal Comfort) are those where the pathway from environmental feature to physiological response is most direct and least mediated by higher cognitive processes — a pattern consistent with the general finding in cognitive science that subcortical and autonomic mechanisms are better characterized than cortical ones.

The roster is explicitly open: additional theories may be added when formal reductions meeting the five qualification criteria are completed. Aesthetic Anchoring, identified during CROSSCUT-I as an emergent interaction rather than an independent template, remains a candidate pending the CROSSCUT-I evaluation protocol. Fractal Fluency and Awe/Kama Muta hold formal status but with thinner reduction documentation than the core ten.

**References for §78:**

Bregman, A. S. (1990). *Auditory scene analysis: The perceptual organization of sound*. MIT Press. [~5,000 GS]

Hall, E. T. (1966). *The hidden dimension*. Doubleday. [~15,000 GS]

Kennedy, D. P., Gläscher, J., Tyszka, J. M., & Adolphs, R. (2009). Personal space regulation by the human amygdala. *Nature Neuroscience*, *12*(10), 1226–1227. [~800 GS]

Merry, S. E. (1981). Defensible space undefended: Social factors in crime control through environmental design. *Urban Affairs Quarterly*, *16*(4), 397–422. [~500 GS]

Newman, O. (1972). *Defensible space*. Macmillan. [~4,000 GS]

O'Keefe, J., & Nadel, L. (1978). *The hippocampus as a cognitive map*. Oxford University Press. [~12,000 GS]

Tulving, E. (1972). Episodic and semantic memory. In E. Tulving & W. Donaldson (Eds.), *Organization of memory* (pp. 381–403). Academic Press. [~30,000 GS]

---

[ABSORBED]

**Source Documents:**
- EXTRACTION_IE_DPT_AND_ARCHITECTURE_COMPREHENSIVE.md (comprehensive consolidation)
- IE_DPT_Full_T1_Specification.md
- Panel_Implicit_Explicit_T1_Theory.md
- 02-19_05_Implicit_vs_Explicit_PP_Working_Doc.md
- CMR_ARCHITECTURE_EXPLANATION.md (§10–13)

**Editorial Metadata:**
- Derived from docs/SECTION_BUILDER_PROCESS.md (systematic template extraction)
- Examples catalogued in docs/EXAMPLE_CATALOG_2026-02-24.md
- Cross-references to docs/DECISION_TRACKING_LOG.md for panel review
- Date compiled: February 24, 2026

---

