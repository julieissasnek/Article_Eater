# Expert Panel III: Multimodal Integration, Neglected Senses, and Higher Cognition
## New Templates with Parameters and Boundary Conditions
## February 15, 2026

---

# PANEL COMPOSITION

This third panel addresses specific gaps identified in the first two panels: the near-total absence of auditory, haptic, and olfactory mechanisms; the missing treatment of crossmodal/multisensory integration; the lack of higher cognitive function (task constraints, working memory, cognitive control); and — critically — the need for *quantitative parameters and explicit boundary conditions* that would make the templates computable rather than merely narrative.

1. **Charles Spence** (Experimental Psychology, University of Oxford) — Head of the Crossmodal Research Laboratory. World's leading authority on crossmodal correspondences and multisensory integration. Has written specifically on architectural design for the multisensory mind. *The multimodal question*.

2. **Mark Wallace** (Neuroscience, Vanderbilt University) — Neural mechanisms of multisensory integration. Studies how sensory signals are combined at the single-neuron and circuit level, including spatial and temporal rules governing integration. *Neural basis for Spence's behavioral findings*.

3. **Josh McDermott** (Brain & Cognitive Sciences, MIT) — Computational auditory perception. Studies how the auditory system parses complex acoustic environments (the "cocktail party problem"), auditory texture perception, and the statistics of natural sounds. *Auditory processing in environments*.

4. **Nina Kraus** (Communication Sciences, Northwestern University) — Auditory neuroscience, subcortical auditory processing, the Biological Processing of Sound lab. Studies how sound exposure shapes brain function and health, particularly in noisy environments and across the lifespan. *Sound-brain-health connection*.

5. **Roberta Klatzky** (Psychology/Human-Computer Interaction, Carnegie Mellon) — Leading authority on haptic perception, spatial cognition through touch, and the role of tactile information in object recognition and environmental understanding. *The missing sense in architecture*.

6. **Earl Miller** (Picower Institute, MIT) — Prefrontal cortex function, working memory, cognitive control, brain oscillations. His integrative theory of PFC function (Miller & Cohen, 2001) is the 5th most-cited paper in the history of neuroscience. *Neural basis of higher cognition*.

7. **Gerd Gigerenzer** (Max Planck Institute for Human Development / Harding Center) — Ecological rationality, bounded rationality, heuristic decision-making. Intellectual heir to Herbert Simon. Studies how cognitive limitations interact with environmental structure. *Task constraints and ecological rationality*.

8. **David Badre** (Cognitive, Linguistic & Psychological Sciences, Brown University) — Hierarchical cognitive control, frontal lobe organization of complex behavior, the "hierarchy of abstraction" in prefrontal cortex. *How the brain organizes goal-directed behavior in complex environments*.

9. **Rachel Herz** (Psychology, Brown University) — Olfactory cognition, olfactory-memory-emotion connections. Author of *The Scent of Desire*. Studies how odors affect emotion, memory, and behavior. *The most architecturally neglected sense*.

---

# QUESTIONS POSED TO PANEL

1. What mechanistic templates are missing from the current library for your domain?
2. What are the *quantitative parameters* — the actual numbers, ranges, and units — that each template needs?
3. What are the *boundary conditions* — the circumstances under which each mechanism breaks down, reverses, or doesn't apply?
4. **For Spence and Wallace specifically**: Is multisensory integration a Tier 1 framework? Does the brain have dedicated multisensory machinery, or does integration emerge from the interaction of unisensory systems?
5. **For Miller, Gigerenzer, and Badre**: How do task goals, cognitive control, and working memory constraints interact with environmental processing? Is there a "higher cognition" framework missing from Tier 1?

---

# SECTION 1: THE MULTIMODAL QUESTION

## CHARLES SPENCE

Your entire template library has a fundamental problem: it's organized by sensory modality and neural system as if the brain processes architectural environments one sense at a time. It doesn't. The experience of being in a building is irreducibly multisensory — you simultaneously see the space, hear its acoustic character, feel the temperature and surface textures, smell the air, and sense your own body in relation to the spatial volume. These sensory streams are not processed independently and then "combined" at some late stage. They interact early, pervasively, and in ways that your modality-specific templates cannot predict.

Let me give you three examples of crossmodal effects that matter for architecture and that none of your 30 templates can generate.

**Example 1 — Sound changes what you see.** The perceived visual size of a room is modulated by its acoustic properties. A room with long reverberation time (>1.5s) is perceived as larger than an acoustically identical room with short reverberation (0.3s), even when the visual information is identical (Yadav, Cabrera, & Martens, 2012). The acoustic environment modulates spatial perception. Your SN_LAYOUT_COGNITIVE_MAP_001 template has no mechanism for this because it treats spatial cognition as visual-proprioceptive.

**Example 2 — What you see changes what you feel.** Thermal comfort ratings are significantly affected by the colour temperature of lighting. Cool-white lighting (6500K) makes the same room feel 1-2°C cooler than warm-white lighting (2700K), with no change in actual temperature (Laurentin, Bermtto, & Fontoynont, 2000). People in warm-lit rooms set their preferred thermostat higher than people in cool-lit rooms. This is a crossmodal correspondence between colour temperature and thermal perception that your templates have no mechanism for.

**Example 3 — Congruency amplifies, incongruency attenuates.** When multisensory signals are congruent — when the visual, auditory, haptic, and olfactory properties of a space tell a consistent story — the overall experience is enhanced supralinearly (the whole is greater than the sum of the parts). When they're incongruent — a "luxury" visual environment with "institutional" acoustic properties — the overall experience is degraded. This is the principle of *multisensory congruency*, and it's arguably the most important design principle for architecture that your template library completely misses.

I've argued in my own work on architectural design (Spence, 2020a, 2020b) that the notion of "synaesthetic design" should be replaced by a rigorous approach based on crossmodal correspondences. Crossmodal correspondences are reliable, consensual associations between stimulus features in different sensory modalities: pitch ↔ spatial height, brightness ↔ loudness, angular shapes ↔ bitter taste, warm colours ↔ warmth, smooth textures ↔ tonal sounds, rough textures ↔ noisy sounds. These correspondences are not arbitrary — many have developmental origins and neural bases.

**My recommendation**: Multisensory Integration should be, at minimum, a strong Tier 1.5 framework, and I'd argue for Tier 1. It has well-characterized neural mechanisms (Wallace will say more), generates cross-domain predictions that no single-modality framework can make, and is directly relevant to architectural experience. The key computational principles — the spatial rule, the temporal rule, the inverse effectiveness rule, and the congruency principle — are well-established and architecturally applicable.

---

## MARK WALLACE

Spence has laid out the behavioral case. Let me add the neural mechanisms.

**The brain has dedicated multisensory circuitry.** Multisensory integration is not just "late convergence" where fully processed unisensory signals come together in association cortex. There is multisensory interaction at every level of the neural hierarchy:

- In the **superior colliculus** (SC), single neurons respond to visual, auditory, and somatosensory stimuli. These neurons obey three well-characterized rules (Stein & Meredith, 1993):
  - **The spatial rule**: Signals from the same spatial location are enhanced; signals from different locations are depressed
  - **The temporal rule**: Signals within a temporal window (~100-200ms for audiovisual, ~300-500ms for visuotactile) are integrated; signals outside this window are segregated
  - **The inverse effectiveness rule**: The enhancement from multisensory integration is *greatest* when unisensory signals are weak. A faint sound and dim light together produce a much bigger neural response than predicted by their sum. Strong unisensory signals gain less from integration.

- In **cortex**, classically "unisensory" areas (V1, A1, S1) show crossmodal modulation — auditory input modulates visual cortex activity, tactile input modulates auditory cortex activity (Ghazanfar & Schroeder, 2006). This is not late feedback; it occurs within 50-100ms of stimulus onset.

- In **association cortex** (STS, IPS, PFC), neurons encode multisensory objects and events, not unisensory features. The brain's representation of "this room" is inherently multisensory from early processing stages.

**For your templates, the inverse effectiveness rule is the most architecturally important.** It means that multisensory design interventions are *most effective* in degraded sensory conditions. A hospital patient in a windowless room with poor lighting (weak visual signal) will benefit *disproportionately* from congruent auditory enrichment (nature sounds), compared to a patient with excellent visual conditions. The worse one sense is served, the more the other senses can compensate. This generates predictions that purely unisensory templates cannot.

**Parameters for multisensory integration**:
- Audiovisual temporal binding window: ~100-200ms (Meredith, Nemitz, & Stein, 1987)
- Visuotactile temporal binding window: ~200-500ms
- Spatial congruence window: ~10° visual angle for audiovisual; larger for less spatially precise modalities
- Inverse effectiveness threshold: Enhancement peaks when unisensory signals are 1-2 standard deviations below detection threshold; diminishes for signals >3 SD above threshold
- Multisensory enhancement magnitude: 50-200% above best unisensory response in SC neurons; typically 10-30% in behavioural measures
- Congruency benefit for architectural perception: Estimated 15-25% improvement in comfort/satisfaction ratings when multisensory signals are congruent vs. incongruent (derived from Spence's crossmodal correspondence literature)

**PANEL CONSENSUS ON MULTISENSORY TIER STATUS**: **Tier 1 recommended.** Meets all criteria: mechanistically generative (generates predictions no single-modality framework can), neurally specified (SC integration rules, cortical crossmodal modulation, association area multisensory coding), cross-domain (applies to every environmental feature), and mature (40+ years of well-characterized mechanisms). Recommend adding as **Tier 1 Framework #10: Multisensory Integration**.

---

# SECTION 2: THE NEGLECTED SENSES — AUDITORY TEMPLATES

## JOSH McDERMOTT

Your template library's treatment of sound is confined to two things: noise as a stressor (NM_THREAT_HPA_001) and acoustic interference with attention (DT_ATTENTIONAL_DEMAND_001). This misses nearly everything about how the auditory system processes architectural environments.

**The auditory system performs scene analysis, not just "hearing."** Every moment you're in a building, your auditory system is parsing the acoustic environment into distinct sources, segregating speech from background noise, estimating room geometry from reverberation, detecting events from their acoustic signatures, and monitoring for unexpected sounds. This is computationally demanding and architecturally shaped.

**Template 31: AUD_SCENE_ANALYSIS_001**
**"Acoustic environment complexity → auditory scene analysis demand → cognitive resource allocation"**

**Causal chain**:
1. Acoustic environment with multiple concurrent sources (speech, HVAC, foot traffic, equipment, music, nature sounds) → auditory scene analysis (ASA) parsing demand
   - Level: ecological → computational
   - Maturity: **how-actually** (Bregman, 1990; McDermott, 2009)
   - **Parameters**: ASA can segregate ~3-5 concurrent sources before performance degrades. Source segregation relies on: onset synchrony (<30ms for grouping), fundamental frequency difference (>1 semitone for reliable segregation), spatial separation (>15° azimuth for spatial release from masking), spectrotemporal continuity.
   - **Boundary conditions**: ASA fails when sources share similar spectrotemporal properties (multiple simultaneous talkers at similar pitch). Fails when reverberation time >2s (smears temporal cues for segregation). Degraded in hearing-impaired listeners (reduced frequency selectivity). Develops gradually in children (<8 years show reduced ASA). Declines with age (>60 years).

2. ASA demand → cortical processing load (bilateral superior temporal gyrus, planum temporale, intraparietal sulcus for spatial separation)
   - Level: computational → circuit
   - Maturity: **how-actually**
   - **Parameters**: fMRI BOLD increase in auditory cortex scales with number of sources: ~5% per additional source up to 3-4; then plateau/decline as segregation fails.

3. High ASA demand → diverted attentional resources → reduced capacity for concurrent cognitive tasks (speech comprehension, reading, creative thinking, social interaction)
   - Level: circuit → psychological
   - Maturity: **how-actually** (robust literature on noise effects on cognition; Szalma & Hancock, 2011)
   - **Parameters**: Speech-in-noise comprehension: drops from >95% correct at +15 dB SNR to ~50% at 0 dB SNR. Working memory performance: decreases ~10-20% in 60 dB(A) broadband noise vs. 35 dB(A) quiet. Complex task performance: ~5-15% degradation per 10 dB increase in irrelevant speech noise.
   - **Boundary conditions**: Steady-state noise (HVAC hum) is less disruptive than fluctuating noise (speech) at the same level, because it doesn't demand ongoing segregation. *Meaningful* irrelevant speech is maximally disruptive (the "irrelevant speech effect" — Jones & Macken, 1993). Familiar and predictable noise patterns are less disruptive than novel patterns (connects to PP framework — auditory prediction error). Individual differences are enormous — introverts, high-sensitivity individuals, and those with auditory processing disorders are ~2x more affected.

---

## NINA KRAUS

I want to add something Josh's template misses — the *subcortical* auditory processing that happens before cortical scene analysis, and its long-term health consequences.

**Template 32: AUD_SUBCORTICAL_ENCODING_002**
**"Chronic acoustic environment → subcortical auditory plasticity → speech processing and cognitive health"**

My lab has shown that the auditory brainstem — the inferior colliculus and its connections — is not a passive relay. It's plastic, shaped by acoustic experience throughout life (Kraus & Chandrasekaran, 2010). Chronic exposure to degraded acoustic environments (excessive noise, poor speech-to-noise ratios, acoustically reverberant spaces) degrades subcortical encoding precision. Chronic exposure to rich acoustic environments (music, clear speech, naturalistic sound textures) enhances it.

**Causal chain**:
1. Architectural acoustic environment → chronic sound exposure profile (spectral richness, SNR, reverberation, speech clarity)
   - Level: ecological
   - **Parameters**: "Good" acoustic environment for subcortical health: background noise <40 dB(A), RT60 0.4-0.8s for speech spaces, speech-to-noise ratio >+15 dB. "Degraded" environment: background noise >55 dB(A), RT60 >1.5s, SNR <+5 dB.
   - **Boundary conditions**: Effects require *chronic* exposure — weeks to months, not minutes. Brief noise exposure produces temporary threshold shift, not subcortical plasticity.

2. Chronic degraded acoustic exposure → reduced temporal precision of subcortical auditory encoding (measured by auditory brainstem response — ABR — to speech)
   - Level: ecological → circuit (brainstem)
   - Maturity: **how-actually** (Kraus & Chandrasekaran, 2010; Skoe & Kraus, 2010)
   - **Parameters**: Children in noisy schools show ~0.5-1ms delays in subcortical encoding of speech temporal fine structure. These delays are functionally significant — they impair speech-in-noise comprehension.

3. Reduced subcortical encoding precision → impaired speech-in-noise perception → cascading effects on academic performance (children), social engagement (elderly), cognitive load (workers)
   - Level: circuit → psychological → behavioral
   - Maturity: **how-actually** for the encoding-perception link; **how-plausibly** for the downstream behavioral cascade
   - **Boundary conditions**: Effects are most pronounced at developmental extremes — children (whose subcortical system is still maturing) and elderly (whose system is declining). Healthy young adults are more resilient but not immune. Musical training provides a protective buffer (~2x improvement in subcortical encoding precision — Kraus & Chandrasekaran, 2010).

**Architectural prediction**: Schools, elder care facilities, and open-plan offices with poor acoustics are not just annoying — they're producing measurable degradation of subcortical auditory processing that impairs speech comprehension, social engagement, and cognitive function. Acoustic design is a neural health intervention, not merely a comfort feature.

---

## JOSH McDERMOTT (additional)

**Template 33: AUD_REVERBERATION_SPACE_003**
**"Room acoustic properties → auditory spatial perception → sense of enclosure and safety"**

The auditory system extracts information about room geometry from reverberation and early reflections — even without visual input, you can estimate room size, surface materials, and your position within the space from sound alone (Traer & McDermott, 2016).

**Causal chain**:
1. Room geometry + surface materials → impulse response (pattern of early reflections + late reverberation)
   - Level: ecological (physics)
   - **Parameters**: Early reflections (<50ms after direct sound) → carry spatial information about room boundaries. Late reverberation (>80ms) → carries information about room volume and surface absorption. RT60 (time for reverb to decay 60 dB) correlates with room volume: ~0.3s for small rooms, ~1.5s for large halls, >3s for cathedrals.
   - **Boundary conditions**: This system requires at least *some* sound source in the room (footsteps, speech, HVAC are sufficient). Complete silence eliminates acoustic spatial information. Anechoic spaces (RT60 <0.1s) feel disorienting because the auditory system gets no spatial information — you lose auditory sense of enclosure.

2. Auditory spatial processing → implicit room model (supplementary to visual/proprioceptive spatial model)
   - Level: ecological → computational
   - Maturity: **how-actually** (Traer & McDermott, 2016; Kolarik et al., 2016)

3. Congruent audiovisual spatial model (room sounds match room appearance) → enhanced spatial certainty → comfort
   Incongruent audiovisual spatial model (room sounds DON'T match appearance) → spatial uncertainty → unease
   - Level: computational → psychological
   - **Parameters**: Mismatch threshold: listeners detect audiovisual room incongruence when RT60 differs by >0.3s from visually expected value, or when early reflection patterns are inconsistent with visible geometry.
   - **Boundary conditions**: Acoustic spatial processing is less precise than visual, so moderate mismatches may go undetected. But large mismatches (visually small room with cathedral reverberation, or visually large space that sounds "dead") produce discomfort and sense of wrongness.

---

# SECTION 3: HAPTIC AND OLFACTORY TEMPLATES

## ROBERTA KLATZKY

Architecture is experienced through the body. Your template library treats haptic experience as a footnote within embodied cognition (Template 8, EC_AFFORDANCE_POSTURAL_001). But haptic perception is a distinct sensory system with its own neural pathways, its own computational principles, and its own environmental significance.

**Template 34: HAP_SURFACE_MATERIAL_001**
**"Surface material properties → haptic exploration → material perception → affective response"**

**Causal chain**:
1. Architectural surface (wall, handrail, floor, door handle, countertop) with specific material properties → haptic contact during use
   - Level: ecological
   - **Parameters**: Four primary haptic dimensions (Hollins et al., 1993; Klatzky & Lederman, 2010): **roughness** (spatial period of texture elements, 0.01-10mm range relevant for architectural surfaces), **hardness** (compliance under force), **thermal quality** (thermal effusivity — how fast heat transfers from hand to surface), **stickiness** (resistance to lateral sliding). These four dimensions account for >80% of variance in haptic material perception.
   - **Boundary conditions**: Requires direct skin contact — gloved hands lose thermal and fine texture information. Contact duration matters: material identification requires ~200ms minimum; full affective evaluation requires ~500ms-2s. Temperature of the person's hand affects thermal perception of surfaces.

2. Haptic material properties → somatosensory cortex (S1, S2) + insula (thermal/affective) → material categorization + affective evaluation
   - Level: ecological → circuit
   - Maturity: **how-actually** (Lederman & Klatzky, 2009)
   - **Parameters**: Natural materials (wood, stone, cotton) are rated as more pleasant than synthetic materials (plastic, metal, vinyl) across cultures, with effect sizes of d=0.3-0.7 (Sakamoto & Watanabe, 2017). Thermal quality is the strongest predictor of pleasantness for hand-contact surfaces: materials with moderate thermal effusivity (wood: ~500-600 W·s^(1/2)/(m²·K)) are preferred over high-effusivity materials (metal: ~10,000-20,000) or very low (foam: ~50).
   - **Boundary conditions**: Affective responses to materials are modulated by context (metal feels "premium" on a watch, "cold" on a hospital bed rail). Visual expectations set a reference — if the surface looks like wood but feels like plastic, negative violation response occurs (crossmodal incongruence — connects to multisensory integration framework).

3. Aggregate haptic experience across all contacted surfaces → ambient haptic quality of building → contribution to overall environmental evaluation
   - Level: psychological
   - Maturity: **how-plausibly** (individual material preferences well-established; aggregate architectural haptic quality less studied)
   - **Boundary condition**: Haptic experience is episodic, not continuous (unlike visual or auditory). You touch surfaces intermittently. The haptic "impression" of a building is built from a series of discrete contact episodes, not a continuous stream. High-contact surfaces (door handles, handrails, desk surfaces) disproportionately determine haptic impression.

---

## RACHEL HERZ

Nadel identified olfaction as embarrassingly underrepresented in the previous panel, and he was right. Olfaction is the most architecturally neglected sense despite being the most powerful for affect and memory. Let me explain why.

**Template 35: OLF_CONTEXT_AFFECT_001**
**"Ambient olfactory environment → hedonic evaluation + context-memory binding"**

**Causal chain**:
1. Building air carries odorant molecules from materials, ventilation, occupants, cleaning products, outdoor air, food preparation, and accumulated molecular signatures
   - Level: ecological
   - **Parameters**: Human olfactory detection thresholds vary enormously by compound: hydrogen sulfide detectable at ~0.5 ppb; vanillin at ~20 ppb; many building materials emit VOCs at 1-100 ppb range. Olfactory adaptation: sensitivity to a constant odor decreases by ~50% within 1-2 minutes, ~90% within 10-15 minutes. This means building occupants rapidly *stop consciously noticing* their building's smell — but the olfactory system continues to process it subconsciously.
   - **Boundary conditions**: Complete anosmia (5-15% of population over age 65) eliminates this pathway entirely. Partial hyposmia (much more common) reduces it. COVID-19-related olfactory dysfunction has affected millions and may permanently alter olfactory processing for a subset.

2. Odorant molecules → olfactory epithelium → olfactory bulb → DIRECT projections to (a) amygdala and (b) hippocampus/entorhinal cortex. **No thalamic relay** — unique among senses.
   - Level: ecological → circuit
   - Maturity: **how-actually** (Gottfried, 2010; Herz, 2016)
   - **Parameters**: Olfactory-amygdala pathway: response onset ~100-200ms. Olfactory-hippocampal pathway: onset ~200-400ms. This direct connectivity explains why odors trigger emotional memories more powerfully than any other sense — the "Proust effect" is a neural fact, not literary metaphor.
   - **Boundary conditions**: The directness of this pathway means olfactory processing *cannot be cognitively suppressed* as effectively as visual or auditory processing. You can close your eyes or cover your ears; you cannot stop smelling (except by holding your breath, which has obvious limits). This makes olfactory environmental quality a form of involuntary exposure.

3. Olfactory-amygdala pathway → rapid hedonic evaluation (pleasant/unpleasant) → affective state modulation
   - Level: circuit → psychological
   - Maturity: **how-actually** (Anderson et al., 2003; Herz, 2016)
   - **Parameters**: Olfactory hedonic response is the *fastest* of any sensory modality — valence evaluation within 200ms, faster than visual (300ms) or auditory (250ms). Effect sizes for odor on mood: pleasant ambient odors (e.g., orange, lavender) improve mood by d=0.3-0.5 vs. odorless conditions; unpleasant odors (e.g., institutional cleaning chemicals, stale air) worsen mood by d=0.2-0.4 (Herz, 2009).

4. Olfactory-hippocampal pathway → powerful context-memory binding → odor-triggered memory retrieval
   - Level: circuit → computational
   - Maturity: **how-actually** (Herz & Engen, 1996; Arshamian et al., 2013)
   - **Parameters**: Odor-evoked memories are: more emotionally intense than memories evoked by the same item's name or image (d=0.6); experienced as more vivid and "real" (d=0.5); older — odor-cued memories come from earlier in life (mean ~6 years old vs. ~11 for visual) (Herz & Schooler, 2002). Odor-context reinstatement improves recall by 15-30% for events encoded in the presence of that odor (connects to Nadel's SN_CONTEXT_MEMORY_002).
   - **Boundary conditions**: Odor-memory binding is strongest for *first associations* — the first emotional experience paired with an odor becomes the dominant association, and later associations have difficulty overwriting it (Herz, 2016). This has profound architectural implications: if your first experience of a hospital includes the smell of antiseptic paired with fear and pain, that smell-emotion association is extremely resistant to change. Hospital design that eliminates institutional olfactory signatures is not a luxury — it's preventing negative olfactory conditioning that will persist for decades.

**Architectural prediction**: The olfactory signature of a building is arguably the *most persistent* component of environmental memory, and the most resistant to cognitive override. Buildings should be designed with olfactory intentionality — not perfuming (which often backfires), but material selection, ventilation design, and source control that produce an ambient olfactory environment that either supports positive affect or, at minimum, avoids negative olfactory conditioning.

---

# SECTION 4: HIGHER COGNITION AND TASK CONSTRAINTS

## EARL MILLER

Your templates treat the brain as if it's passively receiving environmental stimulation. But the people *in* buildings have goals, tasks, plans, and working memory limitations that fundamentally shape how they process the environment.

**Template 36: HC_WORKING_MEMORY_LOAD_001**
**"Environmental information demands → working memory load → capacity overflow → performance degradation"**

Working memory is severely capacity-limited. My work with Buschman (Buschman & Miller, 2010; Lundqvist et al., 2018) has shown that WM capacity is limited to roughly 3-4 items, maintained by gamma-frequency bursts riding on beta oscillations in prefrontal cortex. Each item in WM occupies a different phase of the beta cycle. When capacity is exceeded, top-down feedback coupling breaks down (Pinotsis, Buschman, & Miller, 2020).

**Causal chain**:
1. Environmental features requiring active maintenance in WM (navigational decisions to remember, task instructions, safety information, social obligations, environmental monitoring tasks) → WM loading
   - Level: ecological → computational
   - **Parameters**: WM capacity: 3-4 items (±1, individual differences; Cowan, 2001). Each navigational decision point adds ~1 item if not externally supported. Operating a unfamiliar door mechanism: ~1 item. Remembering a room number while navigating: 1 item. Monitoring an unpredictable environment for threat: ~1-2 items (ongoing). In a complex unfamiliar building, WM can be fully loaded just by the *navigation task*, leaving zero capacity for the occupant's actual purpose.
   - **Boundary conditions**: WM capacity is further reduced by: stress/anxiety (~25% reduction under cortisol elevation — Lupien et al., 1999), age (progressive decline from ~4 items at age 25 to ~2.5 items at age 70), divided attention, sleep deprivation (~30% reduction after 24h — Chee & Chuah, 2007), and concurrent auditory distraction (~15-20% reduction from irrelevant speech).

2. WM load approaching capacity → prefrontal cortex gamma-burst overload → top-down control breakdown → reduced ability to suppress distractors and maintain goal representations
   - Level: computational → circuit
   - Maturity: **how-actually** (Buschman & Miller, 2010; Lundqvist et al., 2018)

3. WM overflow → errors, confusion, goal forgetting, frustration, anxiety
   - Level: circuit → psychological
   - Maturity: **how-actually**
   - **Parameters**: At-capacity WM performance degrades gradually from 1 to 3 items (~5% error rate increase per item), then catastrophically from 3 to 5 items (~20-40% error rate increase; Luck & Vogel, 2013). The subjective experience of WM overflow is confusion and frustration — the "I can't think" feeling that complex environments produce.

**Architectural implication**: Every environmental demand that consumes WM capacity subtracts from the occupant's ability to perform their actual task. A surgeon navigating a confusing hospital corridor to reach an operating room is arriving with depleted WM capacity — the navigational demands consumed resources that should be available for surgical planning. Clark's cognitive offloading template (EC_COGNITIVE_OFFLOADING_002) is the architectural remedy — offload navigational WM into the environment through clear signage, logical layout, and visible landmarks, preserving WM capacity for the occupant's primary task.

---

## GERD GIGERENZER

I want to reframe the entire discussion of "complexity" in your templates. Herbert Simon's key insight was that you cannot understand cognition without understanding the structure of the *environment* in which cognition operates (Simon, 1956, 1990). Rationality is ecological — it depends on the fit between the cognitive system's capabilities and the environment's information structure.

**Template 37: ER_ECOLOGICAL_RATIONALITY_001**
**"Environmental information structure → heuristic fit → decision quality"**

**Causal chain**:
1. Built environment presents decision situations with specific information structure: number of options (doors, corridors, destinations), cue validity (how reliably do environmental cues predict the right choice?), time pressure, and redundancy
   - Level: ecological
   - **Parameters**: Human decision-making operates in three regimes depending on environmental structure (Gigerenzer & Gaissmaier, 2011):
     - **High cue validity, few options** (clear signage, one obvious path) → recognition heuristic or "take the best" → fast, accurate decisions
     - **Moderate cue validity, moderate options** (multiple corridors, some signage, partial visibility) → weighted cue integration → slower but adequate decisions
     - **Low cue validity, many options** (featureless corridors, no signage, no landmarks) → decision paralysis or random search → errors, anxiety, time waste
   - **Boundary conditions**: The crucial insight is that *more information is not always better*. Adding more signs in an already-complex environment can *worsen* decision-making by increasing the number of cues that must be evaluated. There is an optimal level of environmental information that depends on the decision's complexity and the occupant's cognitive capacity.

2. Environment-heuristic fit → decision efficiency → navigational success → confidence and control
   - Level: ecological → computational → psychological
   - Maturity: **how-plausibly** (ecological rationality framework well-established for abstract decisions; application to architectural navigation is a derivation)
   - **Parameters**: The "less-is-more" effect: in high-redundancy environments (where many cues predict the same option), the simplest heuristic outperforms complex strategies. In low-redundancy environments (where cues conflict), more complex strategies are needed. The architect's job is to design environments where simple heuristics work — this means *high cue redundancy* (multiple consistent environmental features all pointing toward the correct wayfinding decision).

**Architectural principle**: Don't design buildings that require optimizing behaviour to navigate. Design buildings that *reward satisficing* — Simon's term for "good enough" decision-making. A satisficing-friendly building has: high cue redundancy (spatial layout, landmarks, signage, and sensory gradients all pointing the same way), few irreversible decisions (you can always backtrack without major cost), and clear "good enough" options at each choice point.

---

## DAVID BADRE

I want to add the *hierarchical structure* of cognitive control, which is missing from your templates. Miller's WM template captures capacity limitations, but cognitive control is not just about how many things you can hold in mind — it's about how you organize them.

**Template 38: HC_HIERARCHICAL_CONTROL_002**
**"Environmental task structure → cognitive control hierarchy → performance and error patterns"**

My work (Badre, 2008; Badre & Nee, 2018) has shown that the prefrontal cortex is organized hierarchically along a rostro-caudal gradient. Posterior PFC (premotor, area 6) handles simple stimulus-response mappings. Mid-lateral PFC (areas 44, 45, 46) handles context-dependent rules. Anterior PFC (area 10) handles abstract policies and long-term goals. The more abstract the cognitive control demand, the more anterior the PFC region recruited.

**Causal chain**:
1. Environmental task complexity → level of abstraction required for cognitive control:
   - **Simple**: Door handle → push/pull (stimulus-response, posterior PFC)
   - **Contextual**: Elevator button → press correct floor, which depends on your current goal (context-dependent rule, mid-lateral PFC)
   - **Abstract**: Navigate hospital to find radiology → requires maintaining abstract goal across multiple subgoals, each with their own context-dependent decisions (abstract policy, anterior PFC)
   - Level: ecological → circuit
   - Maturity: **how-actually** (Badre, 2008; Koechlin, Ody, & Kouneiher, 2003)
   - **Parameters**: Each level of abstraction adds ~150-300ms to response time and recruits an additional PFC region. Error rates increase ~5-15% per level of hierarchical nesting.
   - **Boundary conditions**: The hierarchy has depth limits — beyond ~3-4 levels of nesting, humans lose track of where they are in the hierarchy. This manifests as "goal forgetting" — arriving at a location and not remembering why you went there. Elderly adults and patients with PFC damage show reduced hierarchical depth (maximum ~2 levels).

2. Deep hierarchical task structure in building → anterior PFC recruitment → metabolically expensive → fatigue and goal forgetting over time
   - Level: circuit → psychological
   - **Parameters**: Anterior PFC is the most metabolically expensive cortical region. Sustained engagement (>30-45 min) produces measurable fatigue effects.

**Architectural prediction**: Buildings with deep navigational hierarchies (find building → find wing → find floor → find corridor → find room → find person) impose deep hierarchical cognitive control demands. Each nesting level taxes a progressively more anterior (and metabolically expensive) PFC region. Flattening the hierarchy — making the destination reachable through fewer levels of nesting — directly reduces PFC load. This is why "open" designs with visible destinations feel effortless: they collapse the control hierarchy from 4-5 levels to 1-2.

---

# SECTION 5: CROSSMODAL TEMPLATES AND PARAMETERS

## SPENCE and WALLACE jointly

The following templates capture the core multisensory mechanisms missing from the library.

**Template 39: MSI_CONGRUENCY_PRINCIPLE_001**
**"Multisensory congruency → enhancement or degradation of environmental experience"**

**Causal chain**:
1. Multiple sensory channels simultaneously convey information about architectural environment (visual appearance, acoustic character, thermal quality, haptic surfaces, olfactory signature)
   - Level: ecological
2. Brain evaluates congruency: Do the multisensory signals "tell the same story"?
   - **Congruent** (warm visual appearance + warm lighting + warm acoustic properties [moderate reverberation, low-frequency emphasis] + warm haptic surfaces [wood, fabric] + warm olfactory environment [vanilla, cinnamon notes]) → multisensory enhancement
   - **Incongruent** (luxury visual finishes + harsh acoustic environment + cold haptic surfaces + institutional smell) → multisensory degradation
   - Level: ecological → computational → circuit (SC, STS, IPS)
   - **Parameters**: Congruency benefit: ~15-25% improvement in comfort, satisfaction, and wellbeing ratings (estimated from laboratory studies; architectural field studies are sparse). Incongruency penalty: ~10-20% degradation, *asymmetric* — the worst-performing sense drags overall experience down more than the best-performing sense pulls it up (negativity bias in multisensory evaluation).
   - **Boundary conditions**: Congruency evaluation operates on *abstract* feature mappings (Spence's crossmodal correspondences), not literal similarity. "Warm" visual warmth and "warm" thermal warmth are congruent not because they share physical properties but because the brain has learned their co-occurrence. Some correspondences are innate (pitch ↔ spatial height); others are learned (colour temperature ↔ thermal comfort). Culturally learned correspondences may vary — this is empirically testable and relevant to your cross-cultural Goldilocks work.

3. Multisensory congruency → unified environmental percept → enhanced processing fluency → positive affect
   Multisensory incongruency → fragmented environmental percept → processing disfluency → negative affect or unease
   - Level: computational → psychological
   - Maturity: **how-plausibly** (the component mechanisms are how-actually; the specific architectural application is emerging)

---

**Template 40: MSI_INVERSE_EFFECTIVENESS_002**
**"Degraded unisensory channel → enhanced multisensory compensation"**

**Causal chain**:
1. One sensory channel degraded by architectural conditions (dim lighting → weak visual signal; noise → degraded auditory signal; gloved hands → reduced haptic signal)
   - Level: ecological
   - **Parameters**: Inverse effectiveness is strongest when unisensory signal is 1-2 SD below reliable detection. At 0 SD (fully reliable), multisensory enhancement is minimal (~5%). At -1 SD, enhancement rises to ~20-50%. At -2 SD, enhancement can reach ~100-200% (Stein & Meredith, 1993; Holmes & Spence, 2005).
   - **Boundary conditions**: If the unisensory signal is completely absent (total darkness, silence), the "integration" becomes pure substitution by the remaining sense, which follows different rules. If *all* sensory channels are degraded simultaneously, the system is overwhelmed and enhancement fails.

2. Degraded primary channel → increased weight assigned to secondary channels → multisensory reweighting (Ernst & Banks, 2002)
   - Level: computational
   - Maturity: **how-actually** (Bayesian cue combination framework; extensive psychophysical evidence)
   - **Parameters**: The brain combines multisensory estimates using reliability-weighted averaging (Maximum Likelihood Estimation). Each sense contributes proportional to its reliability (inversely proportional to its variance). Vision is typically weighted ~70% in spatial tasks, but drops to ~30% in low-light conditions, with proprioception and audition taking up the remainder.

**Architectural prediction**: Designing for *all* senses is most critical in environments where *some* senses are compromised. A hospital ward with dim nighttime lighting needs excellent acoustic design (spatial cues from sound substitute for reduced visual spatial information) and good haptic wayfinding (textured handrails, material transitions at thresholds). An office with high noise levels needs enhanced visual clarity (high contrast, good lighting) to compensate for degraded auditory communication. The optimal multisensory design strategy is to ensure that no single sense is critically degraded, and that when one is, others compensate.

---

# SECTION 6: BOUNDARY CONDITIONS AND PARAMETERS — CROSS-CUTTING SUMMARY

*The panel was asked to aggregate the quantitative parameters and boundary conditions that the template library needs to become computable.*

## 6.1 Universal Boundary Conditions (Apply to Most Templates)

| Boundary Condition | Effect | Source |
|---|---|---|
| **Age** | Children (<8): reduced ASA, immature PFC hierarchy, developing multisensory binding. Elderly (>65): reduced WM capacity (~2.5 items), degraded subcortical auditory encoding, lens yellowing reducing circadian input, declining theta oscillation power, anosmia prevalence 5-15% | Multiple panelists |
| **Cognitive load** | Every template's effects are modulated by concurrent cognitive demands. High load → reduced processing of environmental features, reduced benefit from positive features, increased vulnerability to negative features | Miller, Badre |
| **Individual differences** | Introversion/extraversion shifts optimal stimulation (Goldilocks curve). Sensory processing sensitivity (HSP, ~20% of population) amplifies all environmental effects by ~1.5-2x. ASD individuals show altered multisensory binding. ADHD individuals show reduced PFC hierarchical control | Multiple panelists |
| **Familiarity / Exposure duration** | First exposure engages exploration, gist processing, WM-heavy navigation. Repeated exposure → internalized models, reduced WM load, reduced cholinergic engagement. Environmental effects are strongest in first 1-5 exposures, then attenuate | Spence, Gigerenzer |
| **Cultural calibration** | Crossmodal correspondences, olfactory preferences, spatial density tolerance, acoustic preferences, and optimal complexity all vary by culture. No universal parameter values exist for hedonic outcomes | Spence, Herz |
| **Health status** | Illness, pain, medication, sleep deprivation, and mental health conditions all reduce cognitive capacity and shift allostatic budget, amplifying environmental stressor effects | Sterling (from Panel 2) |

## 6.2 Temporal Parameters (When Do Effects Emerge?)

| Timescale | Mechanisms Operating | Templates |
|---|---|---|
| **<200ms** | Gist extraction, olfactory hedonic evaluation, subcortical threat detection | T22, T35, T5 |
| **200ms–1s** | Prediction error computation, cholinergic gating, multisensory binding, WM encoding | T1, T2, T26, T39, T36 |
| **1–30s** | Cognitive map formation, theta sequence generation, ASA source segregation, haptic evaluation | T3, T24, T31, T34 |
| **1–20 min** | DMN re-engagement, SPW-R replay, olfactory adaptation, WM fatigue accumulation | T27, T25, T35, T36 |
| **20 min–hours** | Directed attention fatigue, circadian phase effects, allostatic cost accumulation | T4, T30, T29 |
| **Days–weeks** | Subcortical auditory plasticity, context-memory consolidation, allostatic load accumulation, circadian entrainment/disruption | T32, T23, T29, T30 |
| **Months–years** | Hippocampal volume changes from chronic stress, subcortical encoding precision shifts, olfactory conditioning persistence, spatial expertise development | T6, T32, T35 |

## 6.3 The "Computable Template" Standard

**MILLER**: For a template to be truly computable — meaning the CMR system can use it for quantitative prediction rather than qualitative hand-waving — it needs:

1. **Input parameters with units and ranges** (not "environmental complexity is high" but "spatial frequency spectrum slope = -1.2, visual angle of view = 45°, ambient noise = 52 dB(A), RT60 = 0.8s")
2. **Transfer function with known shape** (not "complexity produces an inverted-U" but "preference = f(PE) where f is Gaussian with μ calibrated by familiarity and σ calibrated by precision")
3. **Output variables with measurement procedures** (not "wellbeing improves" but "cortisol AUC decreases by X ng/mL·h, HRV RMSSD increases by Y ms, subjective comfort rating increases by Z points on 7-point scale")
4. **Confidence intervals on all parameter estimates**
5. **Documented failure modes** (specific conditions where the template makes wrong predictions)

**GIGERENZER**: I'd add: the system should distinguish between templates where we have the transfer function empirically (dose-response curves for noise, thermal comfort models, RT60 optimization curves) and templates where we have only the qualitative shape and approximate parameters. The former can be computed directly; the latter can only be used for ordinal predictions ("A is better than B") rather than cardinal ones ("A is 23% better than B").

**PANEL CONSENSUS**: Of the 40 templates now in the library:
- **~8 templates** are near-computable with current evidence (T5 threat-HPA, T30 circadian, T31 auditory scene analysis, T32 subcortical auditory, T34 haptic materials, T35 olfactory, plus the Tier 2 engineering models for thermal/acoustic/lighting comfort)
- **~15 templates** have known qualitative shape and approximate parameters (most PP and SN templates; can make ordinal predictions)
- **~17 templates** are mechanistically specified but lack quantitative parameterization (most of the newer integrative and cross-framework templates; can make directional predictions only)

This is not a failure — it's an honest assessment of where the science is. The CMR system should track confidence level per template and propagate uncertainty through derivation chains.

---

# SECTION 7: REVISED FRAMEWORK TAXONOMY

## Updated Tier Assignments After Panel III

| Tier | Framework | Status After Panel III |
|---|---|---|
| **Tier 1** | 1. Predictive Processing | Confirmed |
| | 2. Spatial Navigation / Cognitive Mapping | Confirmed |
| | 3. Dual-Process Evaluation | Confirmed |
| | 4. DMN/TPN Dynamics | Confirmed |
| | 5. Neuromodulatory Systems | Confirmed |
| | 6. Interoceptive / Constructionist Affect | Confirmed |
| | 7. Memory Systems | Confirmed |
| | 8. Embodied Cognition | Confirmed |
| | 9. Chronobiological Regulation | **Added by Panel II** |
| | 10. Multisensory Integration | **Added by Panel III** (Spence, Wallace) |
| **Tier 1.5** | Reward / Valuation | Monitoring for promotion |
| | Social Brain / Social Cognition | Monitoring for promotion |
| | Immune-Neural Signaling | Monitoring for promotion |
| | Autonomic Regulation | Implementation layer, may not need promotion |
| | **Cognitive Control / Executive Function** | **New candidate from Panel III** (Miller, Badre) — the "higher cognition" framework. Well-specified neural circuitry (PFC hierarchy), capacity parameters, generates unique predictions about task-environment interaction. Strong case for Tier 1 promotion. |
| | **Ecological Rationality** | **New candidate from Panel III** (Gigerenzer) — describes how environmental information structure determines which cognitive strategies work. May be a design principle that cuts across frameworks rather than a separate framework. |
| **Tier 2A** | ART, SRT, Biophilia, Prospect-Refuge, Fractal Aesthetics, Environmental Preference | Unchanged |
| **Tier 2B** | Thermal Comfort, Acoustic Comfort, Visual Comfort, IAQ | Unchanged |
| **Tier 2C** | Restorative Environments, Place Attachment, Wayfinding Theory, Salutogenic Design, Neuroaesthetics | Unchanged |

---

# SECTION 8: TEMPLATE LIBRARY SUMMARY (Templates 31-40)

| # | Template ID | Framework(s) | Maturity | Key Content |
|---|---|---|---|---|
| 31 | AUD_SCENE_ANALYSIS_001 | PP, MSI | how-actually | Acoustic complexity → ASA demand → cognitive resource depletion |
| 32 | AUD_SUBCORTICAL_ENCODING_002 | NM, Chrono | how-actually | Chronic acoustics → brainstem plasticity → speech/cognitive health |
| 33 | AUD_REVERBERATION_SPACE_003 | SN, MSI | how-actually/plausibly | Room acoustics → auditory spatial model → sense of enclosure |
| 34 | HAP_SURFACE_MATERIAL_001 | EC, MSI | how-actually | Surface properties → haptic evaluation → material affect |
| 35 | OLF_CONTEXT_AFFECT_001 | IC, MS | how-actually | Ambient olfactory → direct amygdala/hippocampus → affect + memory |
| 36 | HC_WORKING_MEMORY_LOAD_001 | HC/EF | how-actually | Environmental WM demands → PFC capacity overflow → errors |
| 37 | ER_ECOLOGICAL_RATIONALITY_001 | HC/EF, PP | how-plausibly | Environmental info structure → heuristic fit → decision quality |
| 38 | HC_HIERARCHICAL_CONTROL_002 | HC/EF | how-actually | Task hierarchy depth → PFC recruitment gradient → fatigue |
| 39 | MSI_CONGRUENCY_PRINCIPLE_001 | MSI | how-plausibly | Crossmodal congruency → enhancement/degradation of experience |
| 40 | MSI_INVERSE_EFFECTIVENESS_002 | MSI | how-actually | Degraded sense → enhanced multisensory compensation |

**Cumulative library**: 40 templates. Covering: 10 Tier 1 frameworks + 2 Tier 1.5 candidates. All major sensory modalities now represented (visual, auditory, haptic, olfactory, thermal, vestibular). Higher cognition now represented (working memory, hierarchical control, ecological rationality). Cross-modal integration now represented.

---

# REFERENCES (Panel III additions)

Anderson, A. K., Christoff, K., Stappen, I., Panitz, D., Ghahremani, D. G., Glover, G., et al. (2003). Dissociated neural representations of intensity and valence in human olfaction. *Nature Neuroscience*, *6*(2), 196–202. (Cited by ~1,500)

Arshamian, A., Iannilli, E., Gerber, J. C., Willander, J., Persson, J., Seo, H. S., Hummel, T., & Larsson, M. (2013). The functional neuroanatomy of odor evoked autobiographical memories cued by odors and words. *Neuropsychologia*, *51*(1), 123–131. (Cited by ~200)

Badre, D. (2008). Cognitive control, hierarchy, and the rostro-caudal organization of the frontal lobes. *Trends in Cognitive Sciences*, *12*(5), 193–200. (Cited by ~1,500)

Badre, D., & Nee, D. E. (2018). Frontal cortex and the hierarchical control of behavior. *Trends in Cognitive Sciences*, *22*(2), 170–188. (Cited by ~500)

Bregman, A. S. (1990). *Auditory scene analysis*. MIT Press. (Cited by ~8,000)

Buschman, T. J., & Miller, E. K. (2010). Shifting the spotlight of attention: Evidence for discrete computations in cognition. *Frontiers in Human Neuroscience*, *4*, 194. (Cited by ~300)

Chee, M. W. L., & Chuah, L. Y. M. (2007). Functional neuroimaging and behavioral correlates of capacity decline in visual short-term memory after sleep deprivation. *PNAS*, *104*(22), 9487–9492. (Cited by ~400)

Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. *Behavioral and Brain Sciences*, *24*(1), 87–114. (Cited by ~5,000)

Ernst, M. O., & Banks, M. S. (2002). Humans integrate visual and haptic information in a statistically optimal fashion. *Nature*, *415*, 429–433. (Cited by ~4,000)

Ghazanfar, A. A., & Schroeder, C. E. (2006). Is neocortex essentially multisensory? *Trends in Cognitive Sciences*, *10*(6), 278–285. (Cited by ~1,500)

Gigerenzer, G., & Gaissmaier, W. (2011). Heuristic decision making. *Annual Review of Psychology*, *62*, 451–482. (Cited by ~3,000)

Gottfried, J. A. (2010). Central mechanisms of odour object perception. *Nature Reviews Neuroscience*, *11*(9), 628–641. (Cited by ~800)

Herz, R. S. (2009). Aromatherapy facts and fictions. *International Journal of Neuroscience*, *119*(2), 263–290. (Cited by ~300)

Herz, R. S. (2016). The role of odor-evoked memory in psychological and physiological health. *Brain Sciences*, *6*(3), 22. (Cited by ~200)

Herz, R. S., & Engen, T. (1996). Odor memory: Review and analysis. *Psychonomic Bulletin & Review*, *3*(3), 300–313. (Cited by ~600)

Herz, R. S., & Schooler, J. W. (2002). A naturalistic study of autobiographical memories evoked by olfactory and visual cues. *American Journal of Psychology*, *115*(1), 21–32. (Cited by ~400)

Hollins, M., Faldowski, R., Rao, S., & Young, F. (1993). Perceptual dimensions of tactile surface texture. *Perception & Psychophysics*, *54*(6), 697–705. (Cited by ~500)

Holmes, N. P., & Spence, C. (2005). Multisensory integration: Space, time, and superadditivity. *Current Biology*, *15*(18), R762–R764. (Cited by ~500)

Jones, D. M., & Macken, W. J. (1993). Irrelevant tones produce an irrelevant speech effect. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, *19*(3), 699–707. (Cited by ~300)

Klatzky, R. L., & Lederman, S. J. (2010). Multisensory texture perception. In M. J. Naumer & J. Kaiser (Eds.), *Multisensory object perception in the primate brain* (pp. 211–230). Springer. (Cited by ~200)

Koechlin, E., Ody, C., & Kouneiher, F. (2003). The architecture of cognitive control in the human prefrontal cortex. *Science*, *302*(5648), 1181–1185. (Cited by ~2,000)

Kolarik, A. J., Moore, B. C. J., Zahorik, P., Cirstea, S., & Pardhan, S. (2016). Auditory distance perception in humans: A review of cues, development, neuronal bases, and effects of sensory loss. *Attention, Perception, & Psychophysics*, *78*(2), 373–395. (Cited by ~200)

Kraus, N., & Chandrasekaran, B. (2010). Music training for the development of auditory skills. *Nature Reviews Neuroscience*, *11*(8), 599–605. (Cited by ~1,500)

Laurentin, C., Bermtto, V., & Fontoynont, M. (2000). Effect of thermal conditions and light source type on visual comfort appraisal. *Lighting Research & Technology*, *32*(4), 223–233. (Cited by ~100)

Lederman, S. J., & Klatzky, R. L. (2009). Haptic perception: A tutorial. *Attention, Perception, & Psychophysics*, *71*(7), 1439–1459. (Cited by ~1,000)

Luck, S. J., & Vogel, E. K. (2013). Visual working memory capacity. *Trends in Cognitive Sciences*, *17*(8), 391–400. (Cited by ~1,500)

Lundqvist, M., Herman, P., Warden, M. R., Brincat, S. L., & Miller, E. K. (2018). Gamma and beta bursts during working memory readout suggest roles in its volitional control. *Nature Communications*, *9*(1), 394. (Cited by ~300)

Lupien, S. J., Gillin, C. J., & Hauger, R. L. (1999). Working memory is more sensitive than declarative memory to the acute effects of corticosteroids. *Behavioral Neuroscience*, *113*(3), 420–430. (Cited by ~600)

McDermott, J. H. (2009). The cocktail party problem. *Current Biology*, *19*(22), R1024–R1027. (Cited by ~200)

Meredith, M. A., Nemitz, J. W., & Stein, B. E. (1987). Determinants of multisensory integration in superior colliculus neurons. *Journal of Neuroscience*, *7*(10), 3215–3229. (Cited by ~1,500)

Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annual Review of Neuroscience*, *24*, 167–202. (Cited by ~18,000)

Pinotsis, D. A., Buschman, T. J., & Miller, E. K. (2020). Working memory load modulates neuronal coupling. *Cerebral Cortex*, *29*(4), 1670–1681. (Cited by ~100)

Sakamoto, M., & Watanabe, J. (2017). Exploring tactile perceptual dimensions using materials associated with sensory vocabulary. *Frontiers in Psychology*, *8*, 569. (Cited by ~100)

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review*, *63*(2), 129–138. (Cited by ~5,000)

Simon, H. A. (1990). Invariants of human behavior. *Annual Review of Psychology*, *41*, 1–19. (Cited by ~2,000)

Skoe, E., & Kraus, N. (2010). Auditory brainstem response to complex sounds: A tutorial. *Ear and Hearing*, *31*(3), 302–324. (Cited by ~500)

Spence, C. (2011). Crossmodal correspondences: A tutorial review. *Attention, Perception, & Psychophysics*, *73*, 971–995. (Cited by ~1,000)

Spence, C. (2020a). Senses of place: Architectural design for the multisensory mind. *Cognitive Research: Principles and Implications*, *5*, 46. (Cited by ~200)

Spence, C. (2020b). Using ambient scent to enhance well-being in the multisensory built environment. *Frontiers in Psychology*, *11*, 598859. (Cited by ~100)

Stein, B. E., & Meredith, M. A. (1993). *The merging of the senses*. MIT Press. (Cited by ~3,000)

Szalma, J. L., & Hancock, P. A. (2011). Noise effects on human performance: A meta-analytic synthesis. *Psychological Bulletin*, *137*(4), 682–707. (Cited by ~500)

Traer, J., & McDermott, J. H. (2016). Statistics of natural reverberation enable perceptual separation of sound and space. *PNAS*, *113*(48), E7856–E7865. (Cited by ~100)

Yadav, M., Cabrera, D., & Martens, W. (2012). Auditory room size perception for real rooms. *Proceedings of Acoustics 2012*. (Cited by ~50)

---

*Google Scholar citation counts approximate as of early 2025.*

**Source conversation**: Article Eater session, February 15, 2026

**END OF DOCUMENT**
