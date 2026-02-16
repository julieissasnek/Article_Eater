# Neuroscience Expert Panel: Part II
## New Mechanistic Templates (Fully Specified) and Extended Framework Taxonomy
## February 15, 2026

---

# PART A: FULLY SPECIFIED NEW TEMPLATES (Templates 21–30)

These templates were recommended by the neuroscience panel (Friston, Seth, Nadel, Chiba, Buzsáki, Raichle, Sterling, Bar, Clark) and are specified here in the same format as Templates 1–20 in the CMR V2.0 specification. They extend the template library from 20 to 30, covering mechanisms the original 20 missed.

---

## TEMPLATE 21: PP_ACTIVE_INFERENCE_003
**"Environmental controllability → action policy availability → free energy reduction"**
*Recommended by: Karl Friston*

**Structural pattern**: environmental_affordance → action_policy_space → regulatory_efficiency
**Higher-order principle**: Organisms don't just passively receive prediction errors — they act to reduce them. Environments that afford prediction-error-reducing actions are less stressful than those that trap occupants with unresolvable surprise.
**Transferable to**: Any domain where control over sensory input is possible (thermal, acoustic, visual, social, spatial)

**Causal chain**:
1. Environmental features affording regulatory actions (operable windows, adjustable lighting, movable furniture, accessible exits, alternative routes) → expanded action policy space
   - Level: ecological → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Gibson, 1979 for affordances; Friston et al., 2016 for active inference formalism)
   - Evidence: Affordances are perceptually specified and neurally encoded in dorsal stream (Cisek & Kalaska, 2010)
2. Expanded action policy space → lower *expected* free energy across policies → reduced uncertainty about future states
   - Level: computational
   - Bridging quality: HIGH (formal derivation)
   - Maturity: **how-plausibly** (the mathematical formalism is rigorous; empirical mapping to architectural controllability is emerging)
3. Lower expected free energy → reduced allostatic preparatory cost → lower baseline cortisol and sympathetic tone
   - Level: computational → molecular → systems
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (consistent with perceived control literature — Langer & Rodin, 1976; Glass & Singer, 1972 — but specific free energy mechanism not directly tested)
   - Parameter range: Perceived control reduces cortisol by 15-30% in lab studies (Dickerson & Kemeny, 2004)
4. Lower baseline allostatic cost → resources freed for cognition, immune function, social engagement
   - Level: systems → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly**

**Moderators**: Actual vs. perceived controllability (perceived suffices — even a button that *could* be pressed reduces stress; Glass & Singer, 1972). Learned helplessness history (organisms with history of uncontrollable environments have reduced exploration of action policies even when available). Cultural norms around personal vs. collective control.

**Scope conditions**: Requires that the organism has learned (or can rapidly learn) the contingency between action and sensory consequence. Novel affordances require exploration time. Does not apply when all action policies lead to equivalently bad outcomes (inescapable stressor).
**Known interactions**: Connects to EC_COGNITIVE_OFFLOADING_002 (environmental affordances are cognitive resources). Connects to NM_THREAT_HPA_001 (controllability moderates threat response magnitude).
**Overall maturity**: **how-plausibly** (strong formal theory + robust behavioral evidence for control effects; mechanistic bridge through free energy not directly tested)

**Key references**: Friston, K. (2010, cited ~8,000); Friston et al. (2016, cited ~800); Glass & Singer (1972, cited ~1,500); Langer & Rodin (1976, cited ~4,000); Cisek & Kalaska (2010, cited ~1,500); Dickerson & Kemeny (2004, cited ~3,000)

---

## TEMPLATE 22: PP_RAPID_GIST_004
**"Low-spatial-frequency scene structure → rapid associative prediction → contextual framing"**
*Recommended by: Moshe Bar*

**Structural pattern**: coarse_feature_extraction → top_down_prediction_cascade → interpretive_frame
**Higher-order principle**: The brain evaluates the global structure of a scene before processing details, using a fast magnocellular pathway to generate top-down predictions that frame all subsequent processing. First impressions of buildings are determined by gross proportions and light distribution, not by decorative detail.
**Transferable to**: Auditory scenes (low-frequency spectral envelope → sound source categorization), social scenes (postural configuration → social situation categorization)

**Causal chain**:
1. Scene low-spatial-frequency (LSF) content (overall light distribution, volume proportions, gross geometry, color temperature) → magnocellular pathway → rapid V1/V2 → dorsal stream → PFC (orbital and lateral prefrontal cortex)
   - Level: ecological → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Bar et al., 2006; Kveraga, Boshyan, & Bar, 2007; Mu & Li, 2013)
   - Parameter range: PFC activation from LSF onset at ~130ms; magnocellular system processes spatial frequencies below ~2 cycles/degree preferentially
   - Evidence: Direct MEG/fMRI evidence for LSF-driven PFC activation preceding detailed object recognition
2. PFC activation → associative memory retrieval → scene category prediction ("hospital," "home," "church," "prison") → affective prediction (expected valence/arousal)
   - Level: circuit → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Bar, 2007, 2009; Barrett & Bar, 2009 — affective predictions accompany perceptual ones)
   - Evidence: PFC generates predictions that facilitate temporal/parietal object recognition; prediction errors measured when scene contents mismatch category
3. Scene category prediction + affective prediction → top-down expectation cascade → modulates all subsequent detail processing in ventral stream
   - Level: circuit → circuit (PFC → temporal/parietal)
   - Bridging quality: HIGH
   - Maturity: **how-actually** (predictive coding framework; fMRI evidence for top-down modulation of scene processing — Summerfield et al., 2006)
4. Contextual frame persists and biases interpretation → detail features interpreted within frame → confirmation bias for initial gist
   - Level: computational → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (consistent with anchoring/framing literature; specific architectural application emerging but not directly tested)

**Moderators**: Viewing duration (frame established at ~130ms but can be overridden with sustained viewing >2-3s if details contradict gist). Prior expectation (knowing you're entering a "hospital" vs. a "spa" shifts frame before any visual input). Emotional state (anxious observers generate more threat-related gist categories from ambiguous LSF input — Barrett & Bar, 2009). Cultural familiarity with building type.

**Scope conditions**: Requires sufficient visual information for LSF extraction (not applicable in darkness, extreme fog, or when view is blocked). The gist-frame can be overridden by strongly contradictory details, but this takes additional processing time and cognitive effort. Most effective for first exposure to a space — repeated exposure builds detailed models that partially bypass gist-based processing.
**Known interactions**: Connects to PP_SPECTRAL_MATCH_001 (LSF content carries the 1/f information). Connects to DP_IMPLICIT_EVALUATION_001 (rapid gist is the mechanism underlying fast environmental evaluation). Connects to NM_THREAT_HPA_001 (threat-related gist triggers amygdala via magnocellular pathway).
**Overall maturity**: **how-actually** (neural pathway well-characterized; gist-based prediction well-demonstrated; specific architectural application is the least tested link)

**Architectural prediction**: Changing a building's LSF properties (lighting distribution, ceiling height, volume proportions, window-to-wall ratio) will shift the first-impression frame more effectively than changing HSF properties (material texture, decorative detail, signage fonts). A building with "welcoming" proportions and "institutional" finishes will feel more welcoming than a building with "institutional" proportions and "welcoming" finishes.

**Key references**: Bar, M. (2007, cited ~1,500); Bar, M. (2009, cited ~800); Bar, Neta, & Linz (2006, cited ~1,500); Barrett & Bar (2009, cited ~800); Kveraga, Boshyan, & Bar (2007, cited ~500); Summerfield et al. (2006, cited ~600); Mu & Li (2013, cited ~200)

---

## TEMPLATE 23: SN_CONTEXT_MEMORY_002
**"Environmental context stability → context-dependent encoding → retrieval efficiency"**
*Recommended by: Lynn Nadel*

**Structural pattern**: context_stability → encoding_coherence → retrieval_facilitation
**Higher-order principle**: The hippocampus binds experiences to their environmental context; returning to the same context reinstates the encoded experience. Architectural stability supports memory; frequent reorganization disrupts it.
**Transferable to**: Virtual environments, narrative contexts, social contexts

**Causal chain**:
1. Stable environmental context (consistent spatial layout, lighting, acoustic signature, temperature, olfactory cues) → consistent hippocampal context representation (place cell ensemble + boundary cell configuration + grid cell phase)
   - Level: ecological → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (O'Keefe & Nadel, 1978; Muller & Kubie, 1987; Anderson & Jeffery, 2003)
   - Evidence: Place cell ensembles remap when environmental context changes; stable contexts produce stable place cell maps
2. Consistent context representation → strong context-event binding during encoding → events tagged with rich contextual information
   - Level: circuit → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Nadel & Moscovitch, 1997; Smith & Vela, 2001)
   - Parameter range: Context-dependent memory advantage: 20-40% better recall in same vs. different context (Smith & Vela, 2001 meta-analysis)
3. Strong context-event binding → context reinstatement at retrieval → hippocampal pattern completion → enhanced recall
   - Level: circuit → computational → psychological
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Nadel et al., 2000; Tompary & Davachi, 2017)
4. Enhanced recall in stable contexts → cumulative learning advantages (for schools, workplaces, hospitals where learning matters)
   - Level: psychological → behavioral
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (robust behavioral evidence for context-dependent memory; specific application to architectural stability less tested)

**Moderators**: Distinctiveness of context (unique architectural spaces produce stronger context codes than generic ones). Emotional valence of encoded events (high-arousal events are bound to context more strongly — flashbulb memory effect). Number of experiences in the context (more episodes → richer context representation). Time since encoding (context-dependent advantage is strongest after delays).

**Scope conditions**: Requires that the person physically occupies the space during encoding (reading about a place doesn't create a context code). Context must be multisensory — purely visual context is weaker than multisensory (spatial + acoustic + olfactory + thermal). Applies to episodic memory; semantic memory is less context-dependent after consolidation.
**Known interactions**: Connects to SN_LAYOUT_COGNITIVE_MAP_001 (the cognitive map IS the spatial component of the context representation). Connects to NM_CORTISOL_HIPPOCAMPAL_005 (stress during encoding can produce context codes that reinstate stress upon return — traumatic context conditioning).
**Overall maturity**: **how-actually** (one of the best-established phenomena in memory research; architectural application is a straightforward extension)

**Architectural prediction**: Schools that reorganize classrooms frequently will produce weaker context-dependent memory than those maintaining stable room assignments. Hospitals where patients remain in one room will recover faster and have better medication compliance than those moved between rooms — because returning to the same room reinstates the learning context for health management routines.

**Key references**: O'Keefe & Nadel (1978, cited ~10,000); Nadel & Moscovitch (1997, cited ~2,500); Nadel et al. (2000, cited ~2,500); Smith & Vela (2001, cited ~1,500); Anderson & Jeffery (2003, cited ~200); Tompary & Davachi (2017, cited ~200)

---

## TEMPLATE 24: SN_THETA_SEQUENCE_003
**"Navigational path structure → theta sequence coherence → trajectory fluency"**
*Recommended by: György Buzsáki*

**Structural pattern**: path_continuity → sequence_coherence → navigational_comfort
**Higher-order principle**: The hippocampus represents trajectories as compressed sequences within theta cycles. Smooth, predictable paths produce coherent theta sequences; abrupt discontinuities produce sequence disruptions that are experienced as disorientation.
**Transferable to**: Temporal sequences in music (rhythmic predictability), narrative structure (plot continuity), task workflows (procedural fluency)

**Causal chain**:
1. Navigational path with continuous geometry (gradual curves, visible path ahead, predictable direction changes, long sightlines) → smooth place cell sequence activation within theta cycles
   - Level: ecological → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (O'Keefe & Recce, 1993 — theta phase precession; Dragoi & Buzsáki, 2006 — theta sequences)
   - Parameter range: Theta sequences span ~7-10 place fields within each 125ms theta cycle; represent ~50cm–2m of path ahead of current position (in rats; scaled to room-level in humans)
2. Coherent theta sequences → accurate trajectory prediction → low navigational prediction error
   - Level: circuit → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Johnson & Redish, 2007; Wikenheiser & Redish, 2015 — theta sequences predict future position)
3. Low navigational prediction error → reduced hippocampal-prefrontal conflict monitoring → reduced anxiety and cognitive load
   - Level: computational → circuit → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (conflict between predicted and actual trajectory engages ACC/mPFC; this is established for cognitive conflict generally but specific hippocampal trajectory prediction error → anxiety is inferential)
4. Conversely: Path with abrupt discontinuities (blind corners, sudden level changes, T-intersections without sightlines) → theta sequence disruption → trajectory prediction failure → hippocampal error signal → reorientation demand → anxiety + cognitive load
   - Level: ecological → circuit → computational → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (established that hippocampal theta is disrupted by environmental discontinuities; specific downstream anxiety pathway is plausible but not directly measured in humans)

**Moderators**: Familiarity (repeated exposure builds route memory that compensates for structural discontinuities). Speed of movement (faster movement compresses more trajectory into each theta cycle, making disruptions more salient). Cognitive load (divided attention impairs theta sequence formation). Age (theta rhythms decline with aging, reducing trajectory prediction range).

**Scope conditions**: Requires active locomotion (passive transport in wheelchairs or vehicles partially engages the system but with different dynamics). Theta sequences are best characterized for forward linear movement; complex 3D movement (stairs, ramps, elevators) may engage different mechanisms. Human theta is more variable in frequency (3-8 Hz) than rodent theta (6-12 Hz), which may affect sequence compression.
**Known interactions**: Connects to SN_LAYOUT_COGNITIVE_MAP_001 (theta sequences build the cognitive map during exploration). Connects to MS_RIPPLE_REPLAY_002 (theta sequences are the raw material that SPW-Rs later replay for consolidation).
**Overall maturity**: **how-plausibly** (oscillatory mechanisms are how-actually in rodents; human homologues are established but less precisely characterized; architectural predictions are derivations, not direct tests)

**Key references**: O'Keefe & Recce (1993, cited ~3,000); Dragoi & Buzsáki (2006, cited ~1,000); Johnson & Redish (2007, cited ~500); Wikenheiser & Redish (2015, cited ~400); Buzsáki & Tingley (2018, cited ~500)

---

## TEMPLATE 25: MS_RIPPLE_REPLAY_002
**"Environmental rest opportunities → sharp-wave ripple replay → spatial knowledge consolidation"**
*Recommended by: György Buzsáki*

**Structural pattern**: low_demand_pause → replay_opportunity → memory_consolidation
**Higher-order principle**: The hippocampus consolidates spatial experiences during quiet wakefulness and sleep via sharp-wave ripples (SPW-Rs) — brief high-frequency oscillations that compress and replay recent trajectories. Architectural rest opportunities are not mere comfort; they enable the neural mechanism for learning the building.
**Transferable to**: Any learning domain (skill consolidation during practice breaks, conceptual learning during rest periods in educational settings)

**Causal chain**:
1. Environmental features affording rest/pause (benches, alcoves, courtyards, window seats, waiting areas with views) → behavioral state transition from active exploration to quiet wakefulness
   - Level: ecological → behavioral
   - Bridging quality: HIGH
   - Maturity: **how-actually** (behavioral observation; environmental psychology literature on rest affordances)
2. Quiet wakefulness → hippocampal state transition from theta (exploration mode) to large irregular activity (LIA) with intermittent SPW-Rs
   - Level: behavioral → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Buzsáki, 2015; this state transition is one of the most robust findings in hippocampal physiology)
   - Parameter range: SPW-Rs occur at ~0.5-2 Hz during quiet wakefulness; each event lasts 50-120ms; replay compresses ~300ms-1s of experience into ~50ms
3. SPW-Rs replay compressed versions of recent spatial experience → reactivation of place cell sequences from recent navigation
   - Level: circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Lee & Wilson, 2002; Foster & Wilson, 2006; Huszár et al., 2024)
   - Evidence: Spike sequences during SPW-Rs match sequences during prior navigation, both forward and reverse; disrupting SPW-Rs impairs spatial learning
4. Replayed sequences → hippocampal-neocortical dialogue → consolidation of spatial knowledge in neocortex
   - Level: circuit → systems
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Girardeau, Benchenane, Wiener, Buzsáki, & Zugaro, 2009 — SPW-R disruption impairs consolidation; Khodagholy, Gelinas, & Buzsáki, 2017 — cortical ripples coordinate with hippocampal ripples)
5. Consolidated spatial knowledge → improved wayfinding on subsequent visits → reduced navigational stress and cognitive load
   - Level: systems → psychological → behavioral
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (established that consolidation improves spatial memory; specific architectural application is a derivation)

**Moderators**: Quality of rest (true quiet wakefulness > anxious waiting > task-engaged sitting — SPW-Rs are suppressed by cholinergic activation during active processing). View during rest (views that engage DMN without demanding directed attention may optimize SPW-R conditions — connects to DT_DMN_MAINTENANCE_002). Duration of rest (minimum ~2-5 min to allow meaningful replay; 15-20 min optimal for substantial consolidation).

**Scope conditions**: Applies to new or recently modified environments where spatial learning is occurring. Less relevant for highly familiar environments where spatial knowledge is already consolidated. SPW-R replay is selective — not all experiences are replayed; novel and rewarding experiences are preferentially replayed (Huszár et al., 2024). Sleep provides additional and more effective consolidation than quiet wakefulness alone.
**Known interactions**: Connects to SN_THETA_SEQUENCE_003 (theta sequences during exploration are what gets replayed during SPW-Rs). Connects to DT_ATTENTIONAL_DEMAND_001 (environments allowing DMN engagement also allow SPW-R replay — the rest function is shared). Connects to NM_CHOLINERGIC_GATING_007 (high ACh during exploration suppresses SPW-Rs; low ACh during rest permits them — the ACh state is the gating signal for replay).
**Overall maturity**: **how-actually** for the neural mechanisms (among the best-established in hippocampal physiology); **how-plausibly** for the architectural application (the derivation is tight but untested directly)

**Key references**: Buzsáki (2015, cited ~2,000); Lee & Wilson (2002, cited ~2,000); Foster & Wilson (2006, cited ~1,500); Girardeau et al. (2009, cited ~1,000); Khodagholy, Gelinas, & Buzsáki (2017, cited ~500); Huszár et al. (2024)

---

## TEMPLATE 26: NM_CHOLINERGIC_GATING_007
**"Environmental salience → basal forebrain ACh → selective cortical precision enhancement"**
*Recommended by: Andrea Chiba*

**Structural pattern**: salient_feature_detection → neuromodulatory_gating → selective_processing_enhancement
**Higher-order principle**: The basal forebrain cholinergic system selectively boosts processing of salient environmental features by increasing the gain on specific cortical circuits. Not all features are processed equally — the cholinergic system determines which aspects of the environment get high-precision processing.
**Transferable to**: Any sensory modality (visual, auditory, olfactory, somatosensory salience all engage cholinergic gating)

**Causal chain**:
1. Environmentally salient feature (novel object, movement, change in lighting, sudden sound, reward-predictive cue) → detection by amygdala (affective salience) or prefrontal cortex (task-relevant salience) → projection to basal forebrain (nucleus basalis of Meynert, medial septum, diagonal band)
   - Level: ecological → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Zaborszky et al., 2018; Sarter, Parikh, & Howe, 2009)
   - Parameter range: Phasic ACh transients with onset ~200-500ms post-stimulus; duration ~1-5s
2. Basal forebrain activation → *specific* cholinergic projections to cortical regions processing the salient feature (not diffuse — circuit-specific)
   - Level: circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Zaborszky et al., 2018 — modular BF-cortical projection architecture; Chiba et al., 1995, 1999 — selective attentional effects of cholinergic lesions)
   - Evidence: Different BF cell groups project to different cortical regions; ACh release can be selective and coordinated
3. Regional ACh release → increased cortical signal-to-noise ratio → enhanced processing precision for salient feature → suppressed processing of non-salient features
   - Level: circuit → cellular → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Minces, Pinto, Dan, & Chiba, 2017 — cholinergic shaping of neural correlations; Hasselmo & Sarter, 2011)
4. Enhanced precision for salient features → those features disproportionately influence perception, memory encoding, and behavioral response
   - Level: computational → psychological
   - Bridging quality: HIGH
   - Maturity: **how-plausibly** (the computational consequence is straightforward; measuring which architectural features are "selected" by the cholinergic system in naturalistic settings is difficult)

**Two modes** (following Yu & Dayan, 2005):
- **Expected uncertainty mode** (tonic ACh): Occupant enters known-complex environment (hospital, airport, market) → sustained tonic ACh elevation → enhanced sensory processing across modalities → "scanning" mode → facilitates learning of environmental structure
- **Unexpected uncertainty mode** (phasic NE, not ACh): Occupant encounters surprise in a supposedly simple environment → phasic noradrenergic response → global arousal and exploration → "orienting" mode → drives search for explanation

**Moderators**: Attentional state (fatigued occupants have depleted cholinergic tone → reduced salience detection → critical environmental features may be missed). Sleep deprivation (Chiba's work on sleep deprivation → attentional impairment via cholinergic depletion). Alzheimer's disease / cholinergic degeneration (BF cholinergic loss → environmental salience detection fails → environments become confusing and threatening).

**Scope conditions**: Requires intact basal forebrain cholinergic system. Cholinergic function declines with age and is severely compromised in Alzheimer's disease — architectural design for aging populations must account for reduced cholinergic gating (make salient features MORE salient to compensate). Cholinergic gating is suppressed during SPW-R replay (connects to MS_RIPPLE_REPLAY_002) — the two systems are mutually exclusive.
**Known interactions**: Critical gating relationship with MS_RIPPLE_REPLAY_002 (ACh ON = exploration/learning; ACh OFF = replay/consolidation). Connects to PP_RAPID_GIST_004 (cholinergic system modulates which subsequent details get high-precision processing after gist established). Connects to DT_ATTENTIONAL_DEMAND_001 (chronic cholinergic engagement without rest = directed attention fatigue at the cholinergic level).
**Overall maturity**: **how-actually** for BF circuitry and selectivity; **how-plausibly** for architectural application

**Key references**: Zaborszky et al. (2018, cited ~200); Sarter, Parikh, & Howe (2009, cited ~1,000); Yu & Dayan (2005, cited ~3,500); Hasselmo & Sarter (2011, cited ~500); Minces et al. (2017, cited ~100); Chiba et al. (1995, cited ~300); Chiba et al. (1999, cited ~100); Tingley et al. (2018, cited ~50)

---

## TEMPLATE 27: DT_DMN_MAINTENANCE_002
**"Low-demand periods → DMN subsystem re-engagement → model maintenance and restoration"**
*Recommended by: Marcus Raichle*

**Structural pattern**: demand_reduction → maintenance_opportunity → model_integrity_preservation
**Higher-order principle**: The DMN performs essential model maintenance operations (self-referential processing, social cognition, memory consolidation, prospective simulation) that are suppressed by sustained environmental demands. Environments must provide periods of low demand for these operations to occur. DMN suppression is not merely fatiguing — it prevents necessary cognitive maintenance.
**Transferable to**: Work scheduling (break structure), educational design (interleaving instruction with rest), clinical design (recovery environments)

**Causal chain**:
1. Environmental period of low directed-attention demand (nature view, quiet waiting area, familiar and safe resting space, low-stimulus transition zone) → task-positive network deactivation
   - Level: ecological → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Raichle et al., 2001; Fox et al., 2005)
2. TPN deactivation → DMN re-engagement (anticorrelation release)
   - Level: circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (robust fMRI finding; onset within seconds of task cessation)
3. DMN re-engagement activates *two dissociable subsystems*:
   a. **MTL subsystem** (hippocampus, parahippocampal cortex, retrosplenial cortex, ventromedial PFC) → scene construction, spatial model updating, episodic memory retrieval, future simulation
   b. **dmPFC subsystem** (dorsomedial PFC, TPJ, lateral temporal cortex, temporal pole) → social cognition, theory of mind, self-referential processing, narrative understanding
   - Level: circuit → computational
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Andrews-Hanna et al., 2010; Buckner & DiNicola, 2019)
4. DMN maintenance operations → {MTL: updated spatial models, consolidated memories, prospective plans; dmPFC: maintained social models, intact self-concept, emotional regulation capacity}
   - Level: computational → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (individual operations well-documented; cumulative maintenance function is an interpretive framework)
5. Chronically insufficient DMN engagement → degraded model quality → impaired creativity, social cognition deficits, reduced emotional regulation, burnout symptomatology
   - Level: psychological → clinical
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (Hamilton et al., 2015; Buckner et al., 2008; correlational evidence for DMN disruption in depression and burnout)

**Subsystem-specific architectural predictions**:
- **MTL subsystem engagement**: Environments with spatial depth, natural vistas, panoramic views → engage scene construction machinery → supports spatial model updating. Prediction: offices with window views should show better spatial memory and more creative problem-solving than windowless offices, mediated by MTL DMN subsystem engagement.
- **dmPFC subsystem engagement**: Social environments during low-demand periods (café, garden with other people present) → engage social cognition machinery → supports social model maintenance. Prediction: communal rest areas should improve social cohesion and team function compared to isolated rest areas, mediated by dmPFC DMN subsystem engagement.

**Moderators**: Anxiety (anxious rumination hijacks DMN for repetitive self-focused processing, preventing healthy maintenance — Hamilton et al., 2015). Quality of rest environment (a "rest" area with persistent noise or visual clutter may not actually reduce TPN engagement). Duration needed: MTL maintenance detectable after ~5 min; full DMN cycling requires ~15-20 min.

**Scope conditions**: DMN engagement requires subjective safety — threatening or uncertain environments maintain TPN engagement even without explicit tasks. Individual differences in DMN dynamics (some people show more rapid DMN engagement; meditation practice may enhance this). Applies to neurotypical adult brains — DMN dynamics differ in ASD, schizophrenia, and ADHD.
**Known interactions**: Connects to MS_RIPPLE_REPLAY_002 (MTL subsystem engagement overlaps with SPW-R replay conditions). Connects to DT_ATTENTIONAL_DEMAND_001 (this template is the recovery mechanism for the fatigue produced by that template). Connects to NM_CHOLINERGIC_GATING_007 (low ACh → DMN engagement + SPW-R replay; high ACh → TPN engagement + active processing).
**Overall maturity**: **how-plausibly** (neural subsystem architecture is how-actually; functional significance of DMN maintenance is how-plausibly; architectural derivations are emerging)

**Key references**: Raichle et al. (2001, cited ~15,000); Fox et al. (2005, cited ~10,000); Andrews-Hanna et al. (2010, cited ~3,500); Buckner & DiNicola (2019, cited ~1,500); Hamilton et al. (2015, cited ~600)

---

## TEMPLATE 28: EC_COGNITIVE_OFFLOADING_002
**"Environmental legibility → information available in environment → reduced internal processing"**
*Recommended by: Andy Clark*

**Structural pattern**: external_information_structure → cognitive_load_distribution → internal_resource_liberation
**Higher-order principle**: Well-designed environments do cognitive work that the brain would otherwise do internally. Clear wayfinding extends spatial memory into the environment. Logical spatial organization extends working memory into the layout. The "intelligence" of a building can be measured by how much cognitive work it does for its occupants.
**Transferable to**: Tool design (good tools offload cognition), interface design (good UIs reduce cognitive load), urban design (legible cities vs. confusing ones)

**Causal chain**:
1. Environmental information structure (clear signage, logical spatial organization, visible landmarks, consistent design language, affordance-rich surfaces) → information available through perception rather than memory
   - Level: ecological
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Gibson, 1979; Norman, 1988; Lynch, 1960 — environmental legibility)
2. Perceptually available information → reduced demand on hippocampal spatial memory, prefrontal working memory, and executive function
   - Level: ecological → circuit
   - Bridging quality: MEDIUM-HIGH
   - Maturity: **how-plausibly** (consistent with cognitive load theory — Sweller, 1988; Risko & Gilbert, 2016 for cognitive offloading; specific neural mechanisms for architectural offloading not directly measured)
3. Reduced internal processing demands → freed prefrontal and hippocampal resources → available for other tasks (social engagement, creative thinking, learning, emotional regulation)
   - Level: circuit → computational → psychological
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (the logic is sound and consistent with dual-task paradigms; specific architectural offloading-to-performance benefits not isolated)
4. Over time: environments that offload cognition → reduced allostatic cost → reduced cumulative cognitive fatigue → healthier and more productive occupants
   - Level: psychological → clinical/behavioral
   - Bridging quality: MEDIUM
   - Maturity: **how-possibly** (this is a long-term cumulative prediction that would be difficult to test directly)

**Moderators**: Cognitive capacity of occupant (offloading is more valuable for occupants with reduced capacity — elderly, stressed, cognitively impaired, children). Familiarity (familiar occupants have internalized spatial knowledge that makes environmental offloading less critical). Task demands (offloading is most valuable when occupants need cognitive resources for non-navigational tasks — surgeons in hospitals, students in schools).

**Scope conditions**: Requires that environmental information is *perceivable* — signage must be legible, landmarks must be visible, affordances must be detectable. Poor environmental conditions (bad lighting, visual clutter, noise masking auditory cues) can negate offloading affordances. Applies most strongly during first few exposures; decreases as spatial knowledge is internalized. Cultural and linguistic variation in signage interpretation.
**Known interactions**: Connects to PP_ACTIVE_INFERENCE_003 (environmental information structures are what make action policies available). Connects to SN_LAYOUT_COGNITIVE_MAP_001 (legible environments produce better cognitive maps faster → less need for offloading on subsequent visits). Connects to PP_RAPID_GIST_004 (gist-consistent signage is processed faster — signs that match the building's category frame are more effective than incongruent ones).
**Overall maturity**: **how-plausibly** (theoretical framework is robust; individual mechanisms are well-established; the specific "offloading" framing as applied to architecture is emerging)

**Key references**: Clark & Chalmers (1998, cited ~8,000); Gibson (1979, cited ~35,000); Norman (1988, cited ~15,000); Lynch (1960, cited ~12,000); Sweller (1988, cited ~10,000); Risko & Gilbert (2016, cited ~300)

---

## TEMPLATE 29: ALLOSTATIC_MASTER_001
**"Cumulative environmental demands → total allostatic cost → resource allocation for function"**
*Recommended by: Peter Sterling and Anil Seth*

**Structural pattern**: demand_summation → metabolic_budget_allocation → functional_capacity
**Higher-order principle**: The brain manages a *metabolic budget* for physiological regulation. Every environmental demand (thermal compensation, noise filtering, navigational computation, threat monitoring, social processing, circadian adjustment) draws from this budget. A building's total impact on wellbeing is determined by the *sum* of its allostatic demands relative to the organism's metabolic capacity. This is the master template — the integrating framework within which all other templates' effects ultimately cash out.
**Transferable to**: Urban environment assessment, workplace design evaluation, hospital design evaluation, school design evaluation — any context where cumulative environmental impact on health matters

**Causal chain**:
1. Multiple concurrent environmental features each imposing regulatory demands:
   - Thermal deviation from comfort → thermoregulatory cost (autonomic, metabolic)
   - Acoustic deviation from optimal → auditory filtering cost + startle response cost
   - Visual complexity beyond resolvable range → visual processing cost
   - Navigational uncertainty → spatial computation cost + anxiety cost
   - Social demand (crowding, surveillance, or isolation) → social regulation cost
   - Air quality deviation → respiratory and immune regulation cost
   - Circadian-misaligned lighting → chronobiological regulation cost
   - Level: ecological → systems
   - Bridging quality: MEDIUM-HIGH (each individual demand is well-characterized; the summation logic is the novel claim)
   - Maturity: **how-plausibly** (each demand pathway is independently supported; the additive/interactive summation model is a hypothesis)
2. Sum of regulatory demands → total allostatic cost → draw on metabolic budget
   - Level: systems
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (Sterling, 2012; McEwen, 2007 — allostatic load concept; specific summation model is an architectural extension)
   - Key assumption: Demands are *approximately additive* with some interactions (Sterling's model; but see Darden's recommendation R3 from Panel 1 — biological composition may not be additive)
3. **If total cost < available budget**: Surplus resources allocated to:
   - Cognitive function (prefrontal engagement, creative processing, learning)
   - Immune function (surveillance, repair, inflammation control)
   - Social engagement (theory of mind, empathy, prosocial behavior)
   - Growth and repair (tissue maintenance, wound healing, neurogenesis)
   - Level: systems → psychological/clinical
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly**
4. **If total cost > available budget**: Triage — some regulatory demands go unmet:
   - First to be sacrificed: immune function, growth/repair (Sapolsky, 2004)
   - Then: social cognition, creative capacity (Hamilton et al., 2015)
   - Last to be sacrificed: thermoregulation, cardiovascular function (core survival)
   - Level: systems → clinical
   - Bridging quality: MEDIUM
   - Maturity: **how-plausibly** (the triage hierarchy is consistent with evolutionary medicine; specific ordering is approximate)
5. Chronic allostatic overload → allostatic load accumulation → measurable health consequences (cardiovascular disease, metabolic syndrome, immune suppression, cognitive decline, mood disorders)
   - Level: clinical
   - Bridging quality: HIGH
   - Maturity: **how-actually** (McEwen, 2007; Juster, McEwen, & Lupien, 2010; robust epidemiological evidence)

**Moderators**: Individual metabolic capacity (age, health status, genetic factors, fitness level, sleep quality — all affect available budget). Current load from non-architectural sources (work stress, relationship problems, financial anxiety — reduce remaining budget for environmental coping). Adaptive capacity (regular exposure to moderate demands increases capacity — hormesis). Recovery quality (good sleep, exercise, social support replenish metabolic budget).

**Scope conditions**: This is a *population-level* template — individual responses will vary significantly based on metabolic capacity and concurrent stressors. The summation model is an approximation — some demand combinations may interact synergistically (noise × thermal discomfort > noise + thermal discomfort). Requires long-duration exposure (hours to days) for allostatic costs to accumulate meaningfully; brief exposures to demanding environments may be stimulating rather than depleting (connects to hormesis).
**Known interactions**: This is the MASTER TEMPLATE — all other templates' effects feed into this one. Specifically: PP_SPECTRAL_MATCH_001 (visual processing cost), SN_LAYOUT_COGNITIVE_MAP_001 (navigational cost), DT_ATTENTIONAL_DEMAND_001 (attentional cost), NM_THREAT_HPA_001 (threat cost), IC_ALLOSTATIC_ANTICIPATION_001 (predictability reduces anticipatory cost), PP_ACTIVE_INFERENCE_003 (controllability reduces expected cost), EC_COGNITIVE_OFFLOADING_002 (legibility reduces cognitive cost). Every template in the library has an allostatic consequence that feeds into this integrating template.
**Overall maturity**: **how-plausibly** (allostatic load concept is well-established; summation model for architectural application is a theoretical extension; the master-template integrating function is the key novel contribution)

**Measurement implications**: A building's allostatic cost can be estimated by: HRV profile of occupants (higher HRV = lower allostatic cost → more efficient regulation), diurnal cortisol variability (flatter slope = higher allostatic load), inflammatory markers (CRP, IL-6), and subjective wellbeing measures (as downstream consequences).

**Key references**: Sterling (2012, cited ~800); Sterling & Eyer (1988, cited ~2,000); McEwen (2007, cited ~5,500); Juster, McEwen, & Lupien (2010, cited ~1,000); Sapolsky (2004, cited ~5,000)

---

## TEMPLATE 30: CHRONO_LIGHT_ENTRAINMENT_001
**"Architectural light exposure → circadian entrainment quality → physiological coordination"**
*Recommended by: Peter Sterling; endorsed by panel consensus as first template for new Tier 1 Framework #9*

**Structural pattern**: light_input → clock_synchronization → systemic_coordination
**Higher-order principle**: The suprachiasmatic nucleus (SCN) coordinates virtually all physiological rhythms (cortisol, melatonin, body temperature, immune function, metabolism, cognitive performance) to a 24-hour cycle. Light is the primary synchronizing signal. Buildings mediate most of an urban population's light exposure. Therefore, building design is the primary determinant of circadian health for the majority of people who spend 80-90% of their time indoors.
**Transferable to**: Workspace scheduling (shift work design), hospital ward design (patient circadian support), school design (student alertness optimization), urban planning (outdoor light access)

**Causal chain**:
1. Architectural light environment (window size, orientation, glazing properties, electric light spectrum, light level, temporal pattern of exposure) → retinal light input with specific spectral composition, intensity, timing, and duration
   - Level: ecological → cellular
   - Bridging quality: HIGH
   - Maturity: **how-actually** (well-characterized relationship between building design and light exposure; Heschong Mahone Group, 2003; Boubekri et al., 2014)
2. Retinal light input → intrinsically photosensitive retinal ganglion cells (ipRGCs, melanopsin-expressing) → retinohypothalamic tract → SCN
   - Level: cellular → circuit
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Berson, Dunn, & Takao, 2002; Hattar et al., 2002; LeGates, Fernandez, & Hattar, 2014)
   - Parameter range: ipRGCs are maximally sensitive to ~480nm (blue) light; threshold for circadian entrainment ~100-200 lux at cornea; bright light exposure (>1000 lux) most effective for phase shifting
3. SCN activation pattern → circadian coordination of:
   a. Pineal melatonin secretion (evening onset → sleep promotion; morning suppression → wake promotion)
   b. Adrenal cortisol rhythm (morning peak → metabolic mobilization; evening trough → recovery)
   c. Core body temperature rhythm (afternoon peak → optimal cognitive performance; nighttime trough → sleep depth)
   d. Immune function cycling (nighttime immune surveillance enhancement; daytime inflammatory suppression)
   - Level: circuit → molecular → systems
   - Bridging quality: HIGH
   - Maturity: **how-actually** (Czeisler et al., 1999; Roenneberg & Merrow, 2016)
4. Well-synchronized circadian coordination → optimal timing of cognitive performance, immune function, metabolic regulation, mood regulation
   - Level: systems → psychological/clinical
   - Bridging quality: HIGH
   - Maturity: **how-actually** (disrupted circadian rhythms → established clinical consequences: metabolic syndrome, mood disorders, cognitive impairment, cancer risk — Roenneberg & Merrow, 2016; Walker, 2017)
5. Circadian disruption (insufficient daytime light, excessive evening blue light, irregular light schedules) → desynchronized physiological rhythms → misaligned cortisol, fragmented sleep, impaired immune function, metabolic dysregulation
   - Level: systems → clinical
   - Bridging quality: HIGH
   - Maturity: **how-actually** (shift work epidemiology; seasonal affective disorder; ICU delirium studies)

**Moderators**: Season and latitude (natural light availability varies; buildings must compensate in winter/high latitudes). Age (lens yellowing reduces blue light transmission → elderly need higher light levels for circadian entrainment). Chronotype (morning vs. evening types differ in optimal light timing). Iris pigmentation (lighter irides may transmit more light). Prior light history (recent bright light exposure shifts sensitivity).

**Scope conditions**: The ipRGC pathway is specifically sensitive to ~480nm blue-enriched light; warm (2700K) incandescent lighting provides minimal circadian input. Timing matters as much as intensity — blue-enriched light in morning entrains well; the same light in evening suppresses melatonin and delays sleep. Duration of exposure matters — brief bright light exposures have different phase-shifting effects than sustained exposure. This template applies to sustained building occupancy (>4 hours); brief visits don't meaningfully affect circadian regulation.
**Known interactions**: Connects to ALLOSTATIC_MASTER_001 (circadian disruption is a major contributor to allostatic load). Connects to DT_DMN_MAINTENANCE_002 (circadian-aligned sleep is the primary DMN recovery mechanism). Connects to NM_CORTISOL_HIPPOCAMPAL_005 (circadian cortisol rhythm → hippocampal function). Connects to MS_RIPPLE_REPLAY_002 (sleep quality affects overnight consolidation → circadian disruption → impaired memory consolidation). This template is connected to virtually every other template because circadian regulation affects all neural and physiological systems.
**Overall maturity**: **how-actually** (the most mechanistically complete of the new templates — every link is well-established; the architectural application is specifically studied in daylighting research, hospital design, and office design)

**Key references**: Czeisler et al. (1999, cited ~2,500); LeGates, Fernandez, & Hattar (2014, cited ~1,500); Roenneberg & Merrow (2016, cited ~1,000); Berson, Dunn, & Takao (2002, cited ~2,500); Hattar et al. (2002, cited ~2,000); Boubekri et al. (2014, cited ~200); Walker (2017, cited ~2,000)

---

# PART B: EXTENDED FRAMEWORK TAXONOMY — TIER 1.5 AND TIER 2

*The panel was reconvened and asked: "Beyond the three candidates already discussed (Attention Networks, Reward/Valuation, Circadian Regulation), what other theoretical frameworks should be in the system? Where should they sit in the tier hierarchy? What distinguishes a Tier 1.5 from a Tier 2?"*

## B.1 Tier Definitions — Refined by Panel

**FRISTON**: Let's be precise about what makes a framework Tier 1 versus lower. I'd propose three criteria:

1. **Mechanistic generativity**: Does the framework generate novel predictions about environmental effects that *cannot* be derived from other frameworks? If all its predictions can be derived as special cases of another framework, it's not independent enough for Tier 1.
2. **Neural implementation specificity**: Does it identify specific neural circuits, neuromodulatory systems, or computational architectures? A framework that only describes behavioral regularities without specifying mechanism is Tier 2 at best.
3. **Cross-domain applicability**: Does it explain environmental effects across multiple outcome domains (cognitive, affective, behavioral, physiological, social), or only within one domain?

**CLARK**: I'd add a fourth: **Theoretical maturity**. Has the framework produced a body of work with well-characterized boundary conditions, known failures, and progressive refinement? Immature frameworks that are promising but not yet battle-tested should be Tier 1.5 — monitored for promotion.

**PANEL CONSENSUS on tier definitions**:

| Tier | Criteria | Examples |
|---|---|---|
| **Tier 1** | Mechanistically generative + neurally specified + cross-domain + mature | Predictive Processing, Spatial Navigation, DMN/TPN, Neuromodulatory, Memory Systems, Interoceptive/Constructionist, Embodied Cognition, Dual-Process, (new) Chronobiological |
| **Tier 1.5** | Meets 2-3 of Tier 1 criteria; promising but not fully independent or mature; monitored for promotion | Reward/Valuation, Social Brain, Immune-Neural |
| **Tier 2** | Domain-specific, derivative of Tier 1 frameworks, OR describes regularities without mechanism | ART, SRT, Biophilia, Prospect-Refuge, Fractal Aesthetics, Thermal Comfort |
| **Tier 3** | Empirical regularities lacking any specified mechanism | Feng Shui-type claims, color psychology folk theories, unvalidated design heuristics |

---

## B.2 Tier 1.5 Candidates — Full Discussion

### Tier 1.5 Candidate A: Reward and Valuation Systems
*(Already identified in Part I of the panel document; expanded here)*

**FRISTON**: The reward and valuation system has well-characterized neural circuitry — the mesolimbic dopamine system (VTA → NAc), the OFC as a "common currency" valuation system, the anterior insula for negative valuation, and the vmPFC for integrative value computation. Wolfram Schultz's reward prediction error framework is computationally precise. The wanting/liking distinction (Berridge & Robinson, 2016) maps onto separable neural systems (dopaminergic incentive salience vs. opioidergic/endocannabinoid hedonic impact).

**BAR**: For architecture, the reward system explains *approach and avoidance* — why people seek out some environments and avoid others. It also explains *adaptation* — why a beautiful new building is thrilling initially but becomes affectively neutral within weeks (hedonic adaptation = declining reward prediction error as the new environment becomes the expected baseline). And it explains *disappointment* — why a building that fails to meet expectations is more aversive than an equivalently mediocre building with no expectations (negative reward prediction error scaled by expectation magnitude).

**SETH**: Where I see it earning Tier 1 status eventually is in explaining the *economic* dimension of environmental experience. People make decisions about where to live, work, eat, and socialize based on valuations of environmental alternatives. These valuations have specific neural mechanisms (OFC comparison, ventral striatal anticipation) that are not fully captured by prediction error alone. Prediction error tells you about surprise; valuation tells you about *worth*.

**PANEL STATUS**: Tier 1.5 — Monitoring for promotion. Key promotion criterion: demonstrate predictions about architectural experience that cannot be derived from the existing 9 Tier 1 frameworks. Top candidate prediction: hedonic adaptation rates for different environmental features should follow reward prediction error dynamics, not perceptual adaptation dynamics. If this is confirmed, the framework explains something the others can't.

**Initial templates if promoted**:
- RV_HEDONIC_ADAPTATION_001: Novel environmental feature → reward prediction error → hedonic response → adaptation over time as prediction error declines
- RV_EXPECTATION_VIOLATION_002: Building expectation (from marketing, reputation, prior experience) → actual experience → value discrepancy → satisfaction/disappointment scaled by expectation magnitude
- RV_APPROACH_AVOIDANCE_003: Environmental valuation → dopaminergic incentive salience → approach/avoidance behavior → spatial usage patterns

---

### Tier 1.5 Candidate B: Social Brain / Social Cognition

**RAICHLE**: The dmPFC subsystem of the DMN that I mentioned earlier is really part of a larger *social brain network* that deserves serious consideration. Dunbar's social brain hypothesis (Dunbar, 1998), the mirror neuron system (Rizzolatti & Craighero, 2004), and the theory of mind network (Saxe & Kanwisher, 2003) collectively describe a set of neural systems specifically evolved for social cognition. Architecture mediates social interaction in profound ways — it determines who you see, who you can talk to, who you can avoid, how intimate or public your interactions are, and what social scripts are afforded.

**CLARK**: The social dimension is where embodied cognition becomes *social* cognition. Shared spaces create shared experiences. The concept of "joint attention" — two people attending to the same thing — has specific neural signatures (Redcay et al., 2010) and is architecturally afforded or prevented. A lecture hall affords joint attention to the speaker. An open office affords surveillance but prevents concentrated joint attention. A coffee shop affords dyadic conversation but not group coordination.

**CHIBA**: From the neuromodulatory perspective, social interaction engages oxytocin systems (bonding, trust), serotonergic systems (mood, social hierarchy), and cholinergic systems (joint attention, shared salience detection). These are neurochemically distinct from solitary environmental processing.

**PANEL DISCUSSION**: Social cognition has well-specified neural circuitry (TPJ, mPFC, STS, mirror system), is cross-domain (affects learning, health, productivity, emotional wellbeing), and generates predictions about architecture that differ from other frameworks (e.g., social density effects can't be derived from spatial navigation or predictive processing alone — they require models of social information processing). The limitation is mechanistic maturity for *architectural* application — we know a lot about social cognition in lab settings, less about how architectural features modulate social brain function.

**PANEL STATUS**: Tier 1.5 — Strong candidate for promotion. Key promotion criterion: demonstrate that architectural effects on social behavior are mediated by identified social brain circuits (TPJ, mPFC, mirror system), not merely by proximity and affordance.

**Initial templates if promoted**:
- SOC_COPRESENCE_001: Architectural layout → visual/auditory access to others → social brain network activation → prosocial behavior and wellbeing (vs. isolation → social brain deprivation → loneliness effects)
- SOC_PRIVACY_REGULATION_001: Architectural features (barriers, visual screens, acoustic separation) → control over social exposure → optimal social stimulation level (inverted-U; connects to Goldilocks template)
- SOC_JOINT_ATTENTION_001: Architectural focal points (hearths, stages, water features, views) → convergent gaze → joint attention → shared experience → social bonding

---

### Tier 1.5 Candidate C: Immune-Neural Signaling (Neuroimmunology)

**SETH**: This is the one I think people underestimate. The immune system and the nervous system are in constant bidirectional communication. Peripheral inflammation affects brain function — proinflammatory cytokines (IL-1β, IL-6, TNF-α) cross the blood-brain barrier and activate microglia, producing "sickness behavior" (fatigue, social withdrawal, reduced motivation, cognitive impairment — Dantzer et al., 2008). Chronic low-grade inflammation — which can be produced by poor air quality, mold, chronic stress, sleep disruption, and circadian misalignment — produces chronic low-grade sickness behavior that may be experienced as "building malaise" or "sick building syndrome."

**STERLING**: And this connects directly to allostasis. Immune function is one of the first things sacrificed when the allostatic budget is tight. A building that generates high allostatic load → diverted immune resources → increased susceptibility to infection AND reduced immune surveillance for cancer → measurable health consequences.

**CHIBA**: The cholinergic anti-inflammatory pathway (Tracey, 2002) is relevant here. The vagus nerve provides tonic cholinergic suppression of peripheral inflammation. When the brain is under allostatic stress, vagal tone decreases, disinhibiting peripheral inflammation. This means that the stress a building produces → reduced vagal tone → increased peripheral inflammation → altered brain function. The building is literally making people inflamed.

**PANEL STATUS**: Tier 1.5 — Mechanistically well-specified and increasingly recognized as important. Key promotion criterion: demonstrate that architectural features modulate inflammatory biomarkers through identified immune-neural pathways, not merely through stress-mediated cortisol effects. If the building's air quality, mold, or volatile organic compounds directly activate immune pathways (not just stress pathways), that's a distinct mechanism. Key references: Dantzer et al. (2008); Tracey (2002); Miller & Raison (2016).

---

### Tier 1.5 Candidate D: Autonomic Regulation / Polyvagal Theory

**STERLING**: The autonomic nervous system (ANS) — sympathetic and parasympathetic branches — is the primary effector for allostatic regulation. Stephen Porges's polyvagal theory (Porges, 2011) proposes a hierarchy: the myelinated vagal system (social engagement, calm), the sympathetic system (mobilization, fight-or-flight), and the unmyelinated vagal system (immobilization, freeze). Environmental features trigger different autonomic states: safe, familiar environments → ventral vagal → social engagement mode. Ambiguous environments → sympathetic → vigilance mode. Inescapably threatening environments → dorsal vagal → freeze/dissociation.

**SETH**: I have reservations about polyvagal theory specifically — the evolutionary phylogeny it proposes is contested (Grossman & Taylor, 2007), and the three-hierarchy model is oversimplified relative to actual ANS complexity. But the broader point that autonomic state mediates the experience of environments is important and well-established.

**FRISTON**: The autonomic nervous system is the *effector* system for the allostatic and interoceptive frameworks already in Tier 1. It's how the brain implements physiological regulation. I'd argue this is implementation detail rather than a separate computational framework — it doesn't have its own computational theory in the way predictive processing or spatial navigation does.

**PANEL STATUS**: Tier 1.5 with caveats — ANS regulation is important but may be an implementation layer for existing frameworks (interoceptive inference, allostasis, neuromodulatory systems) rather than an independent computational framework. Tier 1.5 status warranted because the specific measurement tools (HRV, skin conductance, respiratory sinus arrhythmia) are directly applicable to architectural assessment — even if the computational theory reduces to other frameworks, the measurement framework is irreplaceable. Polyvagal theory specifically should be represented cautiously given ongoing controversy.

---

## B.3 Tier 2 Frameworks — Systematized

*The panel was asked to organize the Tier 2 frameworks that Article Eater already encounters in the environmental psychology literature. These are theories that appear frequently in papers the system ingests but that derive their explanatory power from Tier 1 mechanisms.*

### Tier 2A: Established Environmental Psychology Theories (Derivable from Tier 1)

**FRISTON and CLARK jointly**:

| Tier 2 Theory | Derives From (Tier 1) | What It Adds | Status |
|---|---|---|---|
| **Attention Restoration Theory** (Kaplan, 1995) | DMN/TPN dynamics + PP (prediction error reduction in nature) | Phenomenological description of restoration process; "fascination" = DMN-compatible processing | Well-validated behaviorally; mechanism now explained by Tier 1 |
| **Stress Reduction Theory** (Ulrich, 1983) | Neuromodulatory (HPA) + PP (spectral match) + Interoceptive (allostatic efficiency) | Rapid affective response to nature; evolutionary preparedness for natural environments | Well-validated; multi-mechanism explanation from Tier 1 |
| **Biophilia Hypothesis** (Wilson, 1984) | PP (evolved visual generative model) + NM (threat/safety detection) + EC (evolved affordance sensitivity) | The claim that humans have innate affiliative tendency toward nature | Descriptive; mechanism distributed across Tier 1 frameworks |
| **Prospect-Refuge Theory** (Appleton, 1975) | SN (spatial navigation affordances) + NM (threat detection) + DP (rapid environmental evaluation) + EC (affordances for escape/shelter) | Preference for environments affording visual access + physical refuge | Descriptive; mechanism is multi-framework threat-safety evaluation |
| **Fractal Aesthetics** (Taylor et al., 2005) | PP (spectral match → 1/f statistics are fractal) + NM (arousal optimization) | Preference for mid-range fractal dimension (D ≈ 1.3-1.5) | Directly derivable from PP_SPECTRAL_MATCH_001 + PP_COMPLEXITY_GOLDILOCKS_002 |
| **Environmental Preference** (Kaplan & Kaplan, 1989) | PP (complexity → prediction error) + SN (coherence → cognitive map quality) + DP (legibility → fast evaluation) + EC (mystery → exploration affordance) | Four-factor model: complexity, coherence, legibility, mystery | Elegant taxonomy; each factor maps to specific Tier 1 mechanisms |

**NADEL**: Each of these Tier 2 theories captures something real, but they describe *regularities* without specifying *mechanisms*. The CMR system's value is that it can explain *why* these regularities hold by tracing them to Tier 1 mechanisms — and more importantly, it can predict where they'll fail. ART predicts nature is always restorative, but Tier 1 mechanisms predict it won't be if the nature is threatening (poisonous plants, dangerous animals), circadianly misaligned (bright natural light at night), or navigationally confusing (dense forest with no landmarks).

### Tier 2B: Building Science / Engineering Theories

**STERLING**:

| Tier 2 Theory | Derives From (Tier 1) | What It Adds | Status |
|---|---|---|---|
| **Thermal Comfort Models** (Fanger, 1970; de Dear & Brager, 2002) | Interoceptive (thermal prediction error) + Allostatic (thermoregulatory cost) + PP (adaptive model of thermal expectations) | Specific quantitative models of comfort zones; PMV/PPD indices | Well-validated engineering models; mechanism is allostatic thermoregulation |
| **Acoustic Comfort** (various) | NM (startle/alerting) + DT (auditory attentional demand) + PP (auditory prediction error) | Specific quantitative models of acceptable noise levels | Engineering models; mechanism is attentional and stress pathways |
| **Visual Comfort / Lighting Quality** (CIE, IESNA standards) | PP (visual prediction error) + Chrono (circadian entrainment) + NM (arousal from light level) | Specific quantitative illuminance/glare/color standards | Engineering models; mechanism is visual processing + circadian |
| **Indoor Air Quality** (ASHRAE standards) | Immune-Neural (direct inflammatory pathway) + Allostatic (respiratory regulatory cost) + NM (chemical sensitivity/stress) | Specific quantitative models of acceptable pollutant levels | Engineering models; mechanism is neuroimmune + allostatic |

**SETH**: These building science frameworks are Tier 2 not because they're less important — they may be MORE important for practical design — but because they're domain-specific quantitative models whose explanatory mechanism comes from Tier 1 frameworks. They're essentially *calibrated instantiations* of general Tier 1 mechanisms for specific sensory domains.

### Tier 2C: Emerging / Under-Specified Theories

**BAR and CLARK jointly**:

| Theory | Status | Path to Promotion |
|---|---|---|
| **Restorative Environment Theory** (Hartig, 2004) | Tier 2 — integrative framework combining ART + SRT + other mechanisms | Could become Tier 1.5 if it specifies unique mechanisms beyond its component theories |
| **Place Attachment Theory** (Scannell & Gifford, 2010) | Tier 2 — describes emotional bonds to environments; mechanism likely involves hippocampal context codes (Nadel) + reward system + social identity | Could become Tier 1.5 with neural specification |
| **Affordance Theory** (Gibson, 1979) | Currently embedded in Tier 1 (Embodied Cognition); could be argued as Tier 1 in its own right | Already represented; doesn't need promotion as a separate framework |
| **Wayfinding Theory** (Arthur & Passini, 1992) | Tier 2 — describes navigational strategies; mechanism is Tier 1 Spatial Navigation + working memory + decision-making | Domain-specific application of SN framework |
| **Salutogenic Design** (Dilani, 2006) | Tier 2C — describes health-promoting design features but lacks mechanistic specificity | Needs Tier 1 mechanistic grounding to move up |
| **Neuroaesthetics of Architecture** (Chatterjee & Vartanian, 2014) | Tier 2 — describes aesthetic evaluation of buildings; mechanism is PP + Reward + DP | Active research area; could consolidate into Tier 1.5 as aesthetic/reward pathway matures |

---

## B.4 Framework Coverage Map

*The panel generated a matrix showing which environmental features are explained by which frameworks, to identify coverage gaps.*

| Environmental Feature | Tier 1 Frameworks Explaining It | Coverage Quality |
|---|---|---|
| Visual complexity | PP, DP | ✓ Strong |
| Spatial layout | SN, EC | ✓ Strong |
| Natural elements | PP (spectral match), NM (HPA reduction), IC (allostatic), DT (DMN engagement) | ✓ Strong (multi-framework) |
| Lighting | Chrono (circadian), PP (visual processing), NM (arousal) | ✓ Strong with Chrono addition |
| Noise / acoustics | NM (startle, HPA), DT (attentional demand), PP (auditory PE) | ✓ Moderate |
| Thermal conditions | IC (interoceptive PE), Allostatic (thermoregulatory cost) | ✓ Moderate |
| Air quality | Immune-Neural (T1.5), Allostatic | ○ Gap — needs Tier 1.5 immune pathway |
| Social density / privacy | Social Brain (T1.5), EC (affordances), NM (threat/safety) | ○ Partial — Social Brain would fill gap |
| Color | PP (chromatic prediction), NM (arousal), DP (implicit evaluation) | △ Moderate — less mechanistically specified than other features |
| Material texture / haptics | EC (tactile affordances), PP (haptic prediction) | △ Moderate — understudied neurally |
| Ceiling height / volume | EC (vestibular), PP (spatial frequency), SN (boundary cells) | ✓ Moderate |
| Symmetry / order | PP (regularity → low PE), DP (implicit evaluation) | ✓ Moderate |
| Olfaction | PP (olfactory prediction), IC (interoceptive), MS (olfactory-hippocampal memory) | △ Weak — olfactory processing is poorly integrated into templates |
| Building age / patina | PP (familiarity), Reward (valuation), DP (implicit evaluation) | △ Weak — understudied |
| Views / windows | Chrono (light), PP (depth/spectral), DT (DMN re-engagement), SN (distant landmark coding) | ✓ Strong (multi-framework) |
| Crowding / personal space | Social Brain (T1.5), NM (stress), EC (affordances), IC (autonomic) | ○ Partial — needs Social Brain |

**CHIBA**: The gaps cluster around *social* and *immune/chemical* pathways — exactly the Tier 1.5 candidates we identified. Promoting Social Brain and Immune-Neural to Tier 1 would close the two largest coverage gaps.

**NADEL**: And olfaction is embarrassingly underrepresented given how powerful olfactory-hippocampal connections are for context-dependent memory. The olfactory bulb projects directly to hippocampus and amygdala without thalamic relay — it's the fastest route from environment to memory system. A hospital that smells like antiseptic is creating a powerful contextual code that reinstates anxiety every time the patient encounters that smell, even years later.

**BAR**: We should add an olfactory template. I'd suggest:

**TEMPLATE CANDIDATE — SN_OLFACTORY_CONTEXT_004**: Environmental olfactory signature → direct olfactory bulb → piriform cortex → hippocampal/amygdalar activation → context-memory binding + affective tagging. Maturity: how-actually for the neural pathway (unique direct hippocampal access); how-plausibly for architectural application. This would be Template 31 when formalized.

---

## B.5 Panel Final Recommendations on Framework Taxonomy

1. **Confirm 9 Tier 1 frameworks** (original 8 + Chronobiological Regulation)
2. **Establish 4 Tier 1.5 candidates** (Reward/Valuation, Social Brain, Immune-Neural, Autonomic Regulation) with specific promotion criteria for each
3. **Catalog Tier 2 systematically** (3 subtiers: 2A established environmental psychology, 2B building science/engineering, 2C emerging/underspecified) with explicit derivation mappings to Tier 1
4. **Establish Tier 3** for empirical claims without mechanistic support (not censored from the database but flagged as unsupported by mechanism)
5. **Build allostatic meta-template** as the integrating framework across all tiers
6. **Add olfactory template** as high-priority gap-filler (Template 31)
7. **Target 35-40 templates** for the initial library (original 20 + 10 new from this panel + 5 from Tier 1.5 candidates if promoted)
8. **Design framework layer for dynamic membership** — Tier 1.5 candidates can be promoted or demoted based on track record (reiteration of Gopnik's recommendation from Panel 1)

---

# ADDITIONAL REFERENCES (not in Part I)

Anderson, M. I., & Jeffery, K. J. (2003). Heterogeneous modulation of place cell firing by changes in context. *Journal of Neuroscience*, *23*(26), 8827–8835. (Cited by ~200)

Appleton, J. (1975). *The experience of landscape*. Wiley. (Cited by ~2,000)

Arthur, P., & Passini, R. (1992). *Wayfinding: People, signs, and architecture*. McGraw-Hill. (Cited by ~1,500)

Barrett, L. F., & Bar, M. (2009). See it with feeling: Affective predictions during object perception. *Philosophical Transactions of the Royal Society B*, *364*(1521), 1325–1334. (Cited by ~800)

Berson, D. M., Dunn, F. A., & Takao, M. (2002). Phototransduction by retinal ganglion cells that set the circadian clock. *Science*, *295*(5557), 1070–1073. (Cited by ~2,500)

Boubekri, M., Cheung, I. N., Reid, K. J., Wang, C. H., & Zee, P. C. (2014). Impact of windows and daylight exposure on overall health and sleep quality of office workers. *Journal of Clinical Sleep Medicine*, *10*(6), 603–611. (Cited by ~200)

Chatterjee, A., & Vartanian, O. (2014). Neuroaesthetics. *Trends in Cognitive Sciences*, *18*(7), 370–375. (Cited by ~600)

Cisek, P., & Kalaska, J. F. (2010). Neural mechanisms for interacting with a world full of action choices. *Annual Review of Neuroscience*, *33*, 269–298. (Cited by ~1,500)

Dantzer, R., O'Connor, J. C., Freund, G. G., Johnson, R. W., & Kelley, K. W. (2008). From inflammation to sickness and depression. *Nature Reviews Neuroscience*, *9*(1), 46–56. (Cited by ~5,000)

de Dear, R. J., & Brager, G. S. (2002). Thermal comfort in naturally ventilated buildings. *Energy and Buildings*, *34*(6), 549–561. (Cited by ~3,000)

Dilani, A. (2006). A new paradigm of design and health in hospital planning. *World Hospitals and Health Services*, *42*(2), 11–15. (Cited by ~100)

Dunbar, R. I. M. (1998). The social brain hypothesis. *Evolutionary Anthropology*, *6*(5), 178–190. (Cited by ~5,000)

Fanger, P. O. (1970). *Thermal comfort*. Danish Technical Press. (Cited by ~8,000)

Foster, D. J., & Wilson, M. A. (2006). Reverse replay of behavioural sequences in hippocampal place cells during the awake state. *Nature*, *440*, 680–683. (Cited by ~1,500)

Girardeau, G., Benchenane, K., Wiener, S. I., Buzsáki, G., & Zugaro, M. B. (2009). Selective suppression of hippocampal ripples impairs spatial memory. *Nature Neuroscience*, *12*(10), 1222–1223. (Cited by ~1,000)

Glass, D. C., & Singer, J. E. (1972). *Urban stress: Experiments on noise and social stressors*. Academic Press. (Cited by ~1,500)

Grossman, P., & Taylor, E. W. (2007). Toward understanding respiratory sinus arrhythmia: Relations to cardiac vagal tone, evolution and biobehavioral functions. *Biological Psychology*, *74*(2), 263–285. (Cited by ~800)

Hartig, T. (2004). Restorative environments. In C. Spielberger (Ed.), *Encyclopedia of Applied Psychology* (Vol. 3, pp. 273–279). Academic Press. (Cited by ~500)

Hasselmo, M. E., & Sarter, M. (2011). Modes and models of forebrain cholinergic neuromodulation of cognition. *Neuropsychopharmacology*, *36*(1), 52–73. (Cited by ~500)

Hattar, S., Liao, H. W., Takao, M., Berson, D. M., & Yau, K. W. (2002). Melanopsin-containing retinal ganglion cells: Architecture, projections, and intrinsic photosensitivity. *Science*, *295*(5557), 1065–1070. (Cited by ~2,000)

Heschong Mahone Group. (2003). *Windows and offices: A study of office worker performance and the indoor environment*. California Energy Commission. (Cited by ~500)

Johnson, A., & Redish, A. D. (2007). Neural ensembles in CA3 transiently encode paths forward of the animal at a decision point. *Journal of Neuroscience*, *27*(45), 12176–12189. (Cited by ~500)

Juster, R. P., McEwen, B. S., & Lupien, S. J. (2010). Allostatic load biomarkers of chronic stress and impact on health and cognition. *Neuroscience & Biobehavioral Reviews*, *35*(1), 2–16. (Cited by ~1,000)

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. (Cited by ~5,000)

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, *15*(3), 169–182. (Cited by ~7,000)

Khodagholy, D., Gelinas, J. N., & Buzsáki, G. (2017). Learning-enhanced coupling between ripple oscillations in association cortices and hippocampus. *Science*, *358*(6361), 369–372. (Cited by ~500)

Lee, A. K., & Wilson, M. A. (2002). Memory of sequential experience in the hippocampus during slow wave sleep. *Neuron*, *36*(6), 1183–1194. (Cited by ~2,000)

Lynch, K. (1960). *The image of the city*. MIT Press. (Cited by ~12,000)

Miller, A. H., & Raison, C. L. (2016). The role of inflammation in depression. *Nature Reviews Immunology*, *16*(1), 22–34. (Cited by ~3,000)

Mu, T., & Li, S. (2013). The neural signature of spatial frequency-based information integration in scene perception. *Experimental Brain Research*, *227*(3), 367–377. (Cited by ~200)

Muller, R. U., & Kubie, J. L. (1987). The effects of changes in the environment on the spatial firing of hippocampal complex-spike cells. *Journal of Neuroscience*, *7*(7), 1951–1968. (Cited by ~1,500)

Norman, D. A. (1988). *The design of everyday things*. Basic Books. (Cited by ~15,000)

O'Keefe, J., & Recce, M. L. (1993). Phase relationship between hippocampal place units and the EEG theta rhythm. *Hippocampus*, *3*(3), 317–330. (Cited by ~3,000)

Porges, S. W. (2011). *The polyvagal theory*. Norton. (Cited by ~3,000)

Redcay, E., Dodell-Feder, D., Pearrow, M. J., Mavros, P. L., Kleiner, M., Gabrieli, J. D. E., & Saxe, R. (2010). Live face-to-face interaction during fMRI. *NeuroImage*, *50*(4), 1639–1647. (Cited by ~500)

Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences*, *20*(9), 676–688. (Cited by ~300)

Rizzolatti, G., & Craighero, L. (2004). The mirror-neuron system. *Annual Review of Neuroscience*, *27*, 169–192. (Cited by ~8,000)

Sapolsky, R. M. (2004). *Why zebras don't get ulcers* (3rd ed.). Holt. (Cited by ~5,000)

Sarter, M., Parikh, V., & Howe, W. M. (2009). Phasic acetylcholine release and the volume transmission hypothesis. *Nature Reviews Neuroscience*, *10*(5), 383–390. (Cited by ~1,000)

Saxe, R., & Kanwisher, N. (2003). People thinking about thinking people: The role of the temporo-parietal junction in "theory of mind." *NeuroImage*, *19*(4), 1835–1842. (Cited by ~3,000)

Scannell, L., & Gifford, R. (2010). Defining place attachment. *Journal of Environmental Psychology*, *30*(1), 1–10. (Cited by ~1,500)

Smith, S. M., & Vela, E. (2001). Environmental context-dependent memory. *Psychonomic Bulletin & Review*, *8*(2), 203–220. (Cited by ~1,500)

Summerfield, C., et al. (2006). Predictive codes for forthcoming perception in the frontal cortex. *Science*, *314*(5803), 1311–1314. (Cited by ~600)

Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, *12*(2), 257–285. (Cited by ~10,000)

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2005). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience*, *5*, 60. (Cited by ~300)

Tompary, A., & Davachi, L. (2017). Consolidation promotes the emergence of representational overlap in the hippocampus and medial prefrontal cortex. *Neuron*, *96*(1), 228–241. (Cited by ~200)

Tracey, K. J. (2002). The inflammatory reflex. *Nature*, *420*, 853–859. (Cited by ~5,000)

Ulrich, R. S. (1983). Aesthetic and affective response to natural environment. In I. Altman & J. F. Wohlwill (Eds.), *Behavior and the natural environment* (pp. 85–125). Plenum. (Cited by ~3,000)

Wikenheiser, A. M., & Redish, A. D. (2015). Hippocampal theta sequences reflect current goals. *Nature Neuroscience*, *18*(2), 289–294. (Cited by ~400)

Wilson, E. O. (1984). *Biophilia*. Harvard University Press. (Cited by ~6,000)

---

*Google Scholar citation counts approximate as of early 2025.*

**Source conversation**: Article Eater session, February 15, 2026

**END OF DOCUMENT**
