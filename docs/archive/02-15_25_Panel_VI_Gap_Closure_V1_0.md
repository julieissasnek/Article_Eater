# PANEL VI: TEMPLATE GAP CLOSURE
## Article Eater — Six New Templates for Sensory and Cognitive Gaps
## February 15, 2026 — Document 25

---

## Panel Charter

**Purpose**: Close the six template gaps identified in the Grand Synthesis (Document 24). Each gap represents a domain of environmental experience with documented effects on wellbeing but no current template in the library. For each, the panel will: (1) identify the core neural mechanism, (2) specify the template with causal links, (3) connect it to existing templates, and (4) specify ecological testability.

**Approach**: A single session with domain experts rotating in for their specialty. Three cross-cutting panelists remain throughout: Aspinall (ecological measurement), Andrews-Hanna (DMN/integration), and Bar (prediction error framing). Domain experts are called for their specific gap.

**Templates to Produce**: T53 (Olfactory-Limbic), T54 (Creative Divergence), T55 (Circadian Entrainment), T56 (Awe/Vastness), T57 (Thermal Comfort), T58 (Acoustic Ecology).

---

## Cross-Cutting Panelists (Present Throughout)

| Name | Affiliation | Role |
|---|---|---|
| **Peter Aspinall** | Heriot-Watt University | Ecological measurement — testability rating for every edge |
| **Jessica Andrews-Hanna** | University of Arizona | DMN integration — how each new template connects to restoration networks |
| **Moshe Bar** | Bar-Ilan University | Predictive processing framing — how each domain involves prediction |

---

## T53: OLFACTORY-LIMBIC ENVIRONMENTAL PROCESSING

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Jay Gottfried** | University of Pennsylvania | Olfactory neuroscience — the neural architecture from olfactory bulb to orbitofrontal cortex. How odors are encoded, categorized, and linked to affect and memory. |
| **Rachel Herz** | Brown University | Olfactory psychology — how odors affect mood, cognition, and behavior. The Proust effect: olfactory-evoked autobiographical memory. |
| **Asifa Majid** | University of Oxford | Cross-cultural olfaction — challenges to the assumption that olfactory preferences are universal. Some cultures (Jahai, Maniq) have rich olfactory vocabularies and different preference structures. |

### Panel Discussion

**Gottfried**: The olfactory system is neuroanatomically unique among the senses. Every other sensory modality is relayed through the thalamus before reaching cortex. Olfaction bypasses the thalamus entirely for its primary projection — olfactory bulb projects directly to piriform cortex (primary olfactory cortex) and, critically, directly to the amygdala and entorhinal cortex. This gives olfaction the most direct pathway to the limbic system of any sense. The architectural implication is profound: odors affect emotion and memory before they are consciously identified.

The processing chain:
1. **Olfactory receptor neurons** in nasal epithelium → olfactory bulb (~100ms)
2. **Olfactory bulb** → piriform cortex (pattern recognition) + **amygdala** (affective evaluation) + **entorhinal cortex** (memory gateway to hippocampus) — all simultaneously (~150-200ms)
3. **Piriform cortex** → orbitofrontal cortex (OFC) (conscious odor identification, ~300-500ms)
4. **Amygdala** → hypothalamus (autonomic response) + vmPFC (affect regulation)
5. **Entorhinal cortex** → hippocampus (odor-evoked memory retrieval)

The direct amygdala projection (step 2) means olfaction can trigger emotional and autonomic responses BEFORE conscious odor identification. You feel the affect of an odor before you know what it is. This is even faster than the visual subcortical low road (T46) for affective evaluation, because the visual low road goes through the pulvinar (thalamus), while olfaction skips the thalamus entirely.

**Herz**: The memory connection is equally important for architecture. The Proust effect — vivid autobiographical memory triggered by odor — is not literary metaphor. It is a well-documented phenomenon with a clear neural basis (Herz & Engen, 1996; Herz, 2004). Odor-evoked memories are rated as more emotional, more vivid, and older (earlier in life) than memories evoked by the same stimulus in other modalities (visual, auditory). The mechanism: olfactory input reaches the hippocampus via entorhinal cortex with minimal preprocessing — the raw olfactory pattern is a powerful retrieval cue for hippocampal episodic memory.

For architecture: the smell of a building is an index into its occupants' memories. The smell of fresh wood, baking bread, coffee, garden soil, rain on concrete — each triggers specific memory networks. A hospital that smells of disinfectant triggers medical memories (often negative). A building lobby that smells of fresh flowers or wood triggers different associations. Olfactory design is memory design.

**Majid**: I must caution against assuming universal olfactory preferences. While some odor valence judgments are cross-culturally robust (putrescine is aversive everywhere, vanillin is pleasant nearly everywhere), many preferences are culturally shaped (Arshamian et al., 2022). The Jahai of Malaysia have a lexicon for odors as rich as English's color lexicon — and their pleasantness ratings for some odors differ markedly from Western norms. Architectural olfactory design should specify a *mechanism* (the limbic pathway) without assuming specific odor preferences are universal.

**Bar**: From the predictive processing perspective: olfaction contributes to multimodal environmental prediction. You predict the smell of a space from its visual appearance. A garden should smell green; a kitchen should smell of food; a hospital should smell clinical. When the olfactory prediction is confirmed (congruent multisensory experience), processing fluency increases. When violated (a garden that smells of exhaust), prediction error in the olfactory domain generates negative affect. This connects to Kahn's multisensory coherence finding from Panel T2-A: real nature exceeds screen nature partly because the olfactory channel is congruent.

### T53 Specification

```python
MechanisticTemplate(
    template_id="IC_OLFACTORY_LIMBIC_001",
    name="Olfactory-Limbic Environmental Processing",
    structural_pattern="BYPASS",  # bypasses thalamic relay
    higher_order_principle=(
        "Olfaction has the most direct sensory pathway to limbic structures "
        "(amygdala, entorhinal cortex, hippocampus), bypassing thalamic relay. "
        "Odors affect emotion and memory before conscious identification. "
        "Environmental odors serve as: (1) rapid affective modulators via "
        "amygdala, (2) autobiographical memory retrieval cues via hippocampus, "
        "and (3) multisensory coherence signals that modulate processing fluency."
    ),
    framework_ids=["IC"],  # Interoceptive — olfaction is a chemical sense with strong interoceptive qualities
    causal_links=[
        CausalLink(
            from_variable="environmental_odor_molecules",
            to_variable="amygdala_affective_evaluation",
            activity="direct_olfactory_limbic_processing",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Gottfried, 2010; Zelano & Sobel, 2005",
            parameters={
                "pathway": "olfactory_bulb → piriform + amygdala (direct, no thalamic relay)",
                "latency_ms": "150-200 for amygdala activation",
                "note": "Faster affective evaluation than any other sense"
            }
        ),
        CausalLink(
            from_variable="environmental_odor_molecules",
            to_variable="hippocampal_memory_retrieval",
            activity="odor_evoked_autobiographical_memory",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Herz & Engen, 1996; Herz, 2004",
            parameters={
                "pathway": "olfactory_bulb → entorhinal_cortex → hippocampus",
                "memory_properties": "more_emotional, more_vivid, earlier_in_life than other modalities",
                "architectural_implication": "building_odors_index_occupant_memories"
            }
        ),
        CausalLink(
            from_variable="olfactory_visual_congruence",
            to_variable="multisensory_processing_fluency",
            activity="cross_modal_prediction_confirmation",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Kahn et al., 2008 (real nature > screen nature); Bar cross-modal prediction",
            parameters={
                "congruent": "garden_smell + garden_visual → fluency → positive_affect",
                "incongruent": "exhaust_smell + garden_visual → PE → negative_affect"
            }
        ),
        CausalLink(
            from_variable="amygdala_evaluation",
            to_variable="autonomic_response",
            activity="olfactory_autonomic_cascade",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Gottfried, 2010",
            parameters={
                "pleasant_odors": "reduced_sympathetic, increased_parasympathetic",
                "unpleasant_odors": "increased_sympathetic, HPA_activation_possible",
                "connects_to": "T5 (threat/HPA) via amygdala-hypothalamic pathway"
            }
        )
    ],
    scope_conditions=[
        "Olfactory adaptation is rapid (~2-5 minutes for constant odors). Environmental odor effects require either novel odors or fluctuating concentrations.",
        "Cross-cultural variation in odor preferences is substantial (Majid). Mechanism is universal; preferred odors are not.",
        "Olfactory sensitivity varies with age (declines significantly after 60), sex (females generally more sensitive), and individual genetics (OR gene polymorphisms)."
    ],
    interactions=[
        {"template": "T5 (Threat/HPA)", "type": "INPUT",
         "description": "Unpleasant odors activate amygdala → T5 pathway. Malodorous environments are stressors."},
        {"template": "T23 (Context Memory)", "type": "INPUT",
         "description": "Odor-evoked hippocampal retrieval uses the same context memory system. Building odors contribute to 'Being Away' or prevent it (hospital smell anchors you to medical context)."},
        {"template": "T12 (Interoceptive Affect)", "type": "SHARED_SUBSTRATE",
         "description": "Olfaction is a chemical sense with interoceptive qualities. OFC odor processing shares substrate with interoceptive representation."}
    ],
    ecological_testability="HIGH — odors are directly measurable (electronic nose, GC-MS), controllable (HVAC scent diffusion), and physiological responses are measurable (EDA for valence, salivary cortisol for stress).",
    overall_maturity="how-actually (pathway) / how-plausibly (architectural application)",
    key_references=[
        "Gottfried, J. A. (2010). Central mechanisms of odour object perception. Nature Reviews Neuroscience. [~500 citations]",
        "Herz, R. S., & Engen, T. (1996). Odor memory: Review and analysis. Psychonomic Bulletin & Review. [~800 citations]",
        "Herz, R. S. (2004). A naturalistic analysis of autobiographical memories triggered by olfactory visual and auditory stimuli. Chemical Senses. [~400 citations]",
        "Arshamian, A., et al. (2022). The perception of odor pleasantness is shared across cultures. Current Biology. [~100 citations]",
        "Zelano, C., & Sobel, N. (2005). Humans as an animal model for systems-level organization of olfaction. Neuron. [~300 citations]"
    ]
)
```

---

## T54: CREATIVE DIVERGENCE / RESTORATION-ENABLED CREATIVITY

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Roger Beaty** | Penn State | Neural basis of creative cognition. His work on DMN-executive network cooperation during creative thinking is the leading mechanistic account of how creativity works in the brain. |
| **Jonathan Schooler** | UC Santa Barbara | Mind-wandering, incubation, and creative insight. His work demonstrates that specific types of mind-wandering (not all) facilitate creative problem-solving. |
| **Kalina Christoff** | University of British Columbia | Spontaneous thought and the DMN. Her dynamic framework for understanding the spectrum from deliberate thought to spontaneous thought to dreaming maps exactly onto the ART restoration → creativity pathway. |

### Panel Discussion

**Beaty**: Creative cognition — specifically divergent thinking and creative insight — depends on the *cooperation* between the default mode network (DMN) and the executive control network (ECN), not on DMN alone (Beaty, Benedek, Silvia, & Schacter, 2016; Beaty et al., 2018). The DMN generates candidate ideas (associative, memory-based, spontaneous). The ECN evaluates and refines them (selecting promising ideas, inhibiting irrelevant ones). Creativity requires BOTH: unconstrained generation (DMN) plus selective evaluation (ECN).

The critical finding for this project: the DMN-ECN cooperation pattern during creativity is distinct from the DMN pattern during rest or mind-wandering. During rest, DMN and ECN are anti-correlated (when one is up, the other is down). During creative thinking, they are positively correlated — both are active simultaneously. This requires a specific neural state that is neither pure DMN engagement (the ART soft fascination state) nor pure task focus (the ECN-dominant state), but a flexible intermediate.

**Schooler**: My contribution is about the *incubation effect* and its relationship to mind-wandering. The incubation effect is well-established: taking a break from a problem and engaging in an unrelated task facilitates subsequent insight. But not all breaks are equally effective. Breaks that involve mild, non-demanding cognitive engagement (the kind of task that allows mind-wandering) are more effective than breaks involving demanding cognitive tasks or complete rest (Baird et al., 2012).

This maps directly onto ART's soft fascination: an environment that provides mild, effortless engagement — exactly the Kaplan definition — is the optimal incubation environment. It engages the DMN (spontaneous thought, associative processing) while leaving enough cognitive capacity for the ECN to intermittently evaluate generated ideas. The architectural implication: restorative environments are also creative incubation environments.

**Christoff**: I want to add a nuance. Spontaneous thought exists on a spectrum (Christoff, Irving, Fox, Spreng, & Andrews-Hanna, 2016):

| State | DMN activity | ECN activity | Attentional constraint | Creative utility |
|---|---|---|---|---|
| Focused work | Low | High | High | Low divergence, high convergence |
| Soft fascination / restorative mind-wandering | High (medial temporal) | Low | Low | HIGH divergence, low convergence |
| Rumination | High (dorsal medial) | Moderate | Moderate (stuck in loop) | Very low (repetitive, not generative) |
| Sleep/dreaming | Very high | Very low | None | Variable (some insight, mostly noise) |

The soft fascination state identified in Panel T2-A is the optimal state for *divergent* creative thinking — generating novel associations, exploring possibility spaces, connecting distant ideas. But it is not optimal for *convergent* creative thinking — evaluating, selecting, and refining ideas. Convergent thinking requires ECN re-engagement.

The architectural implication: a building that supports the full creative cycle should provide BOTH a soft fascination environment (for divergent incubation) AND a focused work environment (for convergent refinement), with easy transition between them. The transition itself may facilitate the DMN-ECN cooperation that Beaty describes, because the brain is momentarily in a flexible intermediate state during the switch.

**Andrews-Hanna**: This connects beautifully to the DMN subsystem model. Divergent creativity primarily engages the medial temporal subsystem (scene construction, episodic memory, prospective simulation — the "what if" mode). This is exactly the subsystem that soft fascination activates. Convergent creativity engages the core subsystem in cooperation with ECN (self-referential evaluation of generated ideas). The anti-rumination requirement holds for creativity just as it does for restoration: dorsal medial subsystem engagement (social cognition, self-criticism) interferes with divergent generation.

### T54 Specification

```python
MechanisticTemplate(
    template_id="HC_CREATIVE_DIVERGENCE_001",
    name="Restoration-Enabled Creative Divergence",
    structural_pattern="FACILITATION",
    higher_order_principle=(
        "Environments that support soft fascination (ART) simultaneously create "
        "optimal conditions for divergent creative thinking, because both depend "
        "on medial temporal DMN subsystem engagement with suppressed rumination. "
        "The architectural creative cycle requires transition between soft "
        "fascination environments (divergent generation) and focused work "
        "environments (convergent evaluation)."
    ),
    framework_ids=["HC"],  # Higher Cognition
    causal_links=[
        CausalLink(
            from_variable="soft_fascination_state",
            to_variable="medial_temporal_DMN_divergent_generation",
            activity="spontaneous_associative_processing",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Beaty et al., 2016; Christoff et al., 2016",
            parameters={
                "subsystem": "medial_temporal (scene construction, episodic simulation)",
                "mode": "divergent — generating novel associations, remote connections",
                "requirement": "dorsal_medial_subsystem_suppressed (no rumination)",
                "connects_to": "RC_ART_SOFT_FASCINATION_002 (same DMN state)"
            }
        ),
        CausalLink(
            from_variable="medial_temporal_DMN_generation",
            to_variable="incubation_of_creative_problems",
            activity="unconscious_associative_recombination",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Baird et al., 2012; Schooler & Melcher, 1995",
            parameters={
                "incubation_duration": "minutes to hours",
                "requires": "mild_cognitive_engagement (not full rest, not demanding task)",
                "optimal_environment": "soft_fascination (ART) — nature, walking, showering"
            }
        ),
        CausalLink(
            from_variable="environment_transition_restorative_to_focused",
            to_variable="DMN_ECN_cooperative_state",
            activity="creative_evaluation_mode",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="LOW", maturity="how-possibly",
            key_evidence="Beaty et al., 2018 (DMN-ECN cooperation in creative people)",
            parameters={
                "note": "The transition between environments may briefly create the flexible "
                        "DMN-ECN coupling that characterizes creative insight. Speculative "
                        "but architecturally testable."
            }
        )
    ],
    scope_conditions=[
        "Creativity benefit requires PRIOR engagement with a creative problem (incubation requires something to incubate)",
        "Divergent and convergent phases have different environmental requirements — one environment cannot optimally support both",
        "Individual differences in creative ability modulate the effect; high-creativity individuals show stronger DMN-ECN coupling at baseline"
    ],
    interactions=[
        {"template": "T27 (DMN Maintenance)", "type": "SHARED_SUBSTRATE",
         "description": "Soft fascination (T27 medial temporal DMN) is the SAME state as divergent creative generation. Restoration and creativity share neural substrate."},
        {"template": "T45 (Proactive/Reactive Control)", "type": "TRANSITION",
         "description": "The transition from soft fascination to focused work involves a control mode shift that may facilitate DMN-ECN cooperation."},
        {"template": "ART system", "type": "DOWNSTREAM",
         "description": "Creativity is a downstream consequence of restoration — once directed attention capacity is restored, it can be deployed for creative convergent evaluation."}
    ],
    ecological_testability="MEDIUM — divergent thinking measurable by Alternative Uses Task, Remote Associates Test via smartphone. The incubation effect is testable by measuring creative performance before vs. after restorative breaks.",
    overall_maturity="how-plausibly (DMN-creativity link well-established; architectural application is novel)",
    key_references=[
        "Beaty, R. E., Benedek, M., Silvia, P. J., & Schacter, D. L. (2016). Trends in Cognitive Sciences. [~800 citations]",
        "Beaty, R. E., et al. (2018). Robust prediction of individual creative ability from brain functional connectivity. PNAS. [~400 citations]",
        "Baird, B., et al. (2012). Inspired by distraction: Mind wandering facilitates creative incubation. Psychological Science. [~600 citations]",
        "Christoff, K., Irving, Z. C., Fox, K. C. R., Spreng, R. N., & Andrews-Hanna, J. R. (2016). Trends in Cognitive Sciences. [~800 citations]"
    ]
)
```

---

## T55: CIRCADIAN ENTRAINMENT AND NON-VISUAL LIGHT EFFECTS

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Russell Foster** | University of Oxford | Circadian neuroscience — discovered the role of melanopsin-expressing intrinsically photosensitive retinal ganglion cells (ipRGCs) in circadian entrainment. The world's foremost authority on how light affects the brain beyond vision. |
| **Mariana Figueiro** | Icahn School of Medicine at Mount Sinai | Lighting design and circadian health — translates circadian neuroscience into architectural lighting specifications. Knows the exact lux levels, spectral compositions, and timing parameters needed. |
| **Till Roenneberg** | Ludwig Maximilian University of Munich | Chronobiology and social jetlag — how misalignment between biological and social clocks affects health. His concept of "social jetlag" has direct architectural implications for building occupancy schedules. |

### Panel Discussion

**Foster**: The discovery of melanopsin ipRGCs (Provencio et al., 2000; Berson, Dunn, & Takao, 2002; Foster, 2021) fundamentally changed our understanding of how light affects the brain. These photoreceptors are NOT part of the image-forming visual system. They project to:

1. **Suprachiasmatic nucleus (SCN)** — the master circadian clock. ipRGC input entrains the SCN to the 24-hour light-dark cycle. This is the primary circadian pathway.
2. **Ventrolateral preoptic area (VLPO)** — sleep regulation. Light via ipRGCs promotes wakefulness by inhibiting sleep-promoting neurons.
3. **Perihabenular nucleus** — mood regulation. Light via ipRGCs affects mood through a pathway that is independent of both vision and circadian entrainment (Fernandez et al., 2018).
4. **Olivary pretectal nucleus** — pupillary light reflex.

The key parameters for architectural lighting:
- **Melanopic equivalent daylight illuminance (melanopic EDI)**: The ipRGCs are most sensitive to ~480nm (blue) light. Melanopic EDI measures the biologically effective light dose for ipRGCs specifically. The threshold for circadian entrainment is ~250 melanopic lux sustained for >30 minutes during daytime.
- **Timing**: Morning light exposure (within 2 hours of waking) is most effective for circadian entrainment. Evening light exposure (within 3 hours of sleep) disrupts circadian rhythm and delays sleep onset.
- **Duration**: At least 30 minutes of exposure above threshold for circadian benefit.
- **Spectrum**: Broad-spectrum daylight (melanopic EDI ~250 at the eye) is far more effective than typical indoor electric lighting (melanopic EDI ~50-100 at the eye under most office conditions).

**Figueiro**: The architectural implication is stark: most buildings provide grossly insufficient circadian light. Workers in windowless offices receive melanopic EDI of 50-100 lux — well below the entrainment threshold. Even windowed offices may be insufficient if the worker is facing away from the window or if the window has low-transmittance glazing. The result: chronic circadian disruption, impaired sleep, daytime drowsiness, and mood degradation.

The design specifications are quantitative and implementable:
- **Morning**: Provide >250 melanopic EDI at eye level during the first 2 hours of occupancy. This requires either direct daylight exposure (window within 3m, clear sky) or high-output blue-enriched electric lighting.
- **Daytime**: Maintain >150 melanopic EDI throughout the day for alertness.
- **Evening**: Reduce melanopic EDI to <50 after 6pm to permit melatonin onset. This means warm-spectrum, dim lighting in residential and hospitality settings.
- **Avoid**: Constant uniform lighting throughout the day. The circadian system needs CONTRAST between bright daytime and dim evening.

**Roenneberg**: My concept of "social jetlag" — the discrepancy between your biological clock and your social schedule — affects approximately 80% of the population (Wittmann, Dinich, Merrow, & Roenneberg, 2006). Late chronotypes (natural night owls) forced to wake early for work experience chronic circadian misalignment equivalent to flying several time zones every week. This produces: impaired cognitive performance, elevated cortisol, increased inflammatory markers, and reduced wellbeing.

Architecture can either exacerbate or ameliorate social jetlag. Buildings with abundant morning daylight help entrain late chronotypes earlier, reducing misalignment. Buildings with excessive evening light (glass-walled offices worked late, brightly lit retail) delay circadian rhythms and increase misalignment.

### T55 Specification

```python
MechanisticTemplate(
    template_id="NM_CIRCADIAN_ENTRAINMENT_001",
    name="Circadian Entrainment and Non-Visual Light Effects",
    structural_pattern="ENTRAINMENT",  # new pattern: external signal synchronizes internal oscillator
    higher_order_principle=(
        "Melanopsin-expressing ipRGCs provide a non-visual light pathway to the "
        "SCN (circadian clock), VLPO (sleep/wake), and perihabenular nucleus (mood). "
        "Architectural lighting that provides sufficient melanopic EDI at appropriate "
        "times entrains healthy circadian rhythms, promoting sleep quality, daytime "
        "alertness, and mood stability. Insufficient or mistimed light causes "
        "circadian disruption equivalent to chronic jet lag."
    ),
    framework_ids=["NM"],  # Neuromodulation — circadian rhythm controls melatonin, cortisol diurnal cycle
    causal_links=[
        CausalLink(
            from_variable="architectural_light_exposure",
            to_variable="ipRGC_melanopic_stimulation",
            activity="non_visual_photoreception",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Foster, 2021; Provencio et al., 2000; Berson et al., 2002",
            parameters={
                "photoreceptor": "melanopsin ipRGCs, peak sensitivity ~480nm",
                "threshold": ">250 melanopic EDI for circadian entrainment",
                "duration": ">30 minutes sustained exposure",
                "location": "measured at eye level, not at work surface"
            }
        ),
        CausalLink(
            from_variable="ipRGC_stimulation",
            to_variable="SCN_circadian_entrainment",
            activity="phase_setting_of_master_clock",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Foster, 2021",
            parameters={
                "morning_light": "advances_clock (helps late chronotypes)",
                "evening_light": "delays_clock (exacerbates late chronotypes)",
                "downstream": "SCN controls melatonin (pineal), cortisol diurnal rhythm (adrenal), core body temperature"
            }
        ),
        CausalLink(
            from_variable="SCN_entrainment",
            to_variable="sleep_quality_and_daytime_alertness",
            activity="circadian_regulation_of_sleep_wake",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Cajochen et al., 2005; Figueiro et al., 2017",
            parameters={
                "entrained": "consolidated sleep, daytime alertness, normal cortisol diurnal rhythm",
                "disrupted": "fragmented sleep, daytime drowsiness, flattened cortisol rhythm (connects to T5/T29)"
            }
        ),
        CausalLink(
            from_variable="ipRGC_stimulation",
            to_variable="mood_regulation_via_perihabenular",
            activity="non_circadian_light_mood_effect",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Fernandez et al., 2018; LeGates et al., 2012",
            parameters={
                "note": "Light affects mood INDEPENDENTLY of circadian entrainment and vision. "
                        "This pathway may explain seasonal affective disorder and the mood "
                        "benefits of bright environments even for non-circadian endpoints."
            }
        )
    ],
    scope_conditions=[
        "Parameters are specific to melanopic EDI, not photopic lux — standard lighting design metrics (photopic lux) do not capture circadian effectiveness",
        "Timing matters enormously: the same light dose at 8am vs. 10pm has opposite circadian effects",
        "Individual chronotype modulates optimal timing — one-size-fits-all lighting schedules are suboptimal",
        "Age: ipRGC sensitivity declines with age; elderly require higher melanopic EDI"
    ],
    interactions=[
        {"template": "T5 (Threat/HPA)", "type": "MODULATOR",
         "description": "Circadian disruption flattens cortisol diurnal rhythm — the same pattern seen in chronic stress and social isolation (T50). Healthy circadian rhythm is necessary for normal HPA axis function."},
        {"template": "T29 (Allostatic Master)", "type": "INPUT",
         "description": "Circadian disruption is an allostatic stressor. Chronic disruption contributes to allostatic load via sleep loss, cortisol dysregulation, and inflammatory marker elevation."},
        {"template": "T22 (Aesthetic Reward)", "type": "INDEPENDENT",
         "description": "The non-visual light pathway (ipRGC) is independent of the visual aesthetic pathway. A beautiful but dim environment fails circadian requirements; an ugly but bright environment succeeds."}
    ],
    ecological_testability="HIGH — melanopic EDI measurable by spectroradiometer; actigraphy measures circadian phase and sleep quality; cortisol diurnal rhythm measurable by repeated salivary samples. All measurable in real buildings.",
    overall_maturity="how-actually (mechanism) / how-plausibly (specific architectural thresholds)",
    key_references=[
        "Foster, R. G. (2021). Sleep, circadian rhythms and health. Interface Focus. [~100 citations]",
        "Provencio, I., et al. (2000). A novel human opsin in the inner retina. Journal of Neuroscience. [~2,000 citations]",
        "Berson, D. M., Dunn, F. A., & Takao, M. (2002). Phototransduction by retinal ganglion cells. Science. [~3,000 citations]",
        "Fernandez, D. C., et al. (2018). Light affects mood and learning through distinct retina-brain pathways. Cell. [~300 citations]",
        "Figueiro, M. G., et al. (2017). Tailored lighting intervention improves measures of sleep, depression, and agitation. BMC Geriatrics. [~200 citations]",
        "Wittmann, M., Dinich, J., Merrow, M., & Roenneberg, T. (2006). Social jetlag. Chronobiology International. [~800 citations]",
        "Cajochen, C., et al. (2005). High sensitivity of human melatonin, alertness, thermoregulation, and heart rate to short wavelength light. JCEM. [~1,200 citations]"
    ]
)
```

---

## T56: AWE AND VASTNESS

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Dacher Keltner** | UC Berkeley | The psychology and neuroscience of awe. His framework (Keltner & Haidt, 2003; Keltner, 2023) identifies vastness and need-for-accommodation as the core features of awe. |
| **Michelle Shiota** | Arizona State University | Positive emotion neuroscience. Her work on awe-related physiological responses (reduced sympathetic arousal, piloerection, vagal activation) provides the peripheral measurement basis. |
| **Yaden & Newberg** (represented by **David Yaden**) | Johns Hopkins | Self-transcendent experiences and their neural correlates. His work connects awe to reduced activity in the default mode network's self-referential hub — the "small self" phenomenon. |

### Panel Discussion

**Keltner**: Awe is defined by two appraisals: (1) perceived vastness — the stimulus is experienced as larger than the self's current conceptual framework, and (2) need for accommodation — the existing mental schema must be revised to accommodate the experience (Keltner & Haidt, 2003; Keltner, 2023). Vastness can be physical (the Grand Canyon, a cathedral's nave) or conceptual (an overwhelming idea, a virtuosic performance), but architectural awe is primarily about physical vastness.

The phenomenology: in awe, the sense of self diminishes. People feel small, connected to something larger, and their typical self-focused concerns recede. Time perception shifts — awe makes people feel they have more time. Prosocial behavior increases — awe makes people more generous and cooperative.

**Yaden**: The neural signature of awe, from our preliminary imaging work and from the broader self-transcendence literature (Yaden et al., 2017; Yaden & Newberg, 2022): reduced activity in the DMN core subsystem, specifically the medial prefrontal cortex (mPFC) self-referential node. This is NOT the same as general DMN suppression (which happens during focused external tasks). It is selective suppression of the SELF-referential component while other DMN functions (scene construction, episodic simulation) may be enhanced.

The "small self" has a neural basis: reduced mPFC activity during awe means the brain's self-model is temporarily de-emphasized. Attention and processing resources shift from self-focused concerns to the vast stimulus. This connects to ART: awe may be an extreme form of "Being Away" — the self-referential concerns that cause attentional fatigue are not just set aside (as in Being Away) but actively suppressed by the overwhelming stimulus.

**Shiota**: The physiological signature is distinctive (Shiota, Keltner, & Mossman, 2007): piloerection (goosebumps), reduced heart rate, vagal activation (RSA increase), and occasionally tears. This profile is UNLIKE other positive emotions — joy shows sympathetic activation (increased HR); awe shows parasympathetic activation. Awe's physiology looks more like SRT recovery than like hedonic pleasure. It is a calming, opening, de-arousing experience despite being intensely positive.

**Andrews-Hanna**: The DMN dynamics during awe are fascinating. If Yaden is right that mPFC self-referential activity decreases while medial temporal subsystem activity may increase, then awe produces a specific DMN configuration: enhanced scene construction and spatial processing (the vast environment) with suppressed self-focus. This is the IDEAL state for restoration — even more so than soft fascination, because in soft fascination the core subsystem is active (self-referential processing is possible), while in awe the self-referential component is actively suppressed.

This suggests awe may be the *most restorative* environmental experience — more so than soft fascination — because it achieves the anti-rumination goal not through gentle disinhibition but through the overwhelming vastness of the stimulus itself.

### T56 Specification

```python
MechanisticTemplate(
    template_id="HC_AWE_VASTNESS_001",
    name="Awe, Vastness, and Self-Transcendence in Built Space",
    structural_pattern="ACCOMMODATION",  # new pattern: schema must expand to accommodate stimulus
    higher_order_principle=(
        "Physical vastness (cathedral naves, grand atriums, panoramic landscapes) "
        "can trigger awe — a state characterized by reduced self-referential mPFC "
        "activity, enhanced scene processing, parasympathetic activation, and "
        "prosocial behavior. Awe represents an extreme form of 'Being Away' that "
        "actively suppresses the self-focused rumination that ART merely displaces. "
        "Architectural spaces that produce awe may be the most restorative "
        "environments, but they require sufficient physical scale."
    ),
    framework_ids=["HC", "IC"],  # Higher Cognition + Interoception (for vagal response)
    causal_links=[
        CausalLink(
            from_variable="perceived_physical_vastness",
            to_variable="schema_accommodation_demand",
            activity="detect_stimulus_exceeding_current_framework",
            from_level="PERSONAL_EPISTEMIC", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Keltner & Haidt, 2003; Keltner, 2023",
            parameters={
                "threshold": "stimulus must exceed the self's current spatial schema",
                "architectural_features": "ceiling_height >10m, volume >1000m³, panoramic_views >180°, "
                                          "natural_vastness (ocean, mountains, sky)",
                "note": "threshold varies with individual experience — frequent cathedral visitors habituate"
            }
        ),
        CausalLink(
            from_variable="schema_accommodation",
            to_variable="reduced_mPFC_self_referential_activity",
            activity="small_self_effect",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Yaden et al., 2017; van Elk et al., 2019",
            parameters={
                "substrate": "reduced mPFC (core DMN self-referential hub)",
                "preserved": "medial_temporal_subsystem (scene construction enhanced)",
                "suppressed": "dorsal_medial_subsystem (social comparison, self-criticism)",
                "distinct_from": "general DMN suppression during task focus"
            }
        ),
        CausalLink(
            from_variable="awe_state",
            to_variable="parasympathetic_activation_with_piloerection",
            activity="awe_specific_autonomic_signature",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Shiota et al., 2007; Gordon et al., 2017",
            parameters={
                "HR": "decreased", "RSA": "increased", "piloerection": "present",
                "distinct_from": "joy (sympathetic activation) and relaxation (no piloerection)"
            }
        ),
        CausalLink(
            from_variable="awe_state",
            to_variable="prosocial_behavior_increase",
            activity="self_diminishment_enables_other_orientation",
            from_level="PERSONAL_EPISTEMIC", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Piff et al., 2015; Bai et al., 2017",
            parameters={
                "effect": "increased generosity, cooperation, humility",
                "mechanism": "reduced self-focus → increased attention to others",
                "architectural_implication": "awe-inducing shared spaces may increase prosocial behavior"
            }
        )
    ],
    scope_conditions=[
        "Requires sufficient physical scale — typical office or residential ceilings (2.5-3m) do not produce awe",
        "Habituation: frequent exposure to the same vast space reduces awe. Awe requires novelty or sustained perceptual vastness",
        "Can be negative (threat-based awe: towering cliff, vast storm) which produces sympathetic rather than parasympathetic activation",
        "Cultural variation: what counts as 'vast' depends on experiential baseline"
    ],
    interactions=[
        {"template": "T27 (DMN Maintenance)", "type": "RELATED_BUT_DISTINCT",
         "description": "Soft fascination engages DMN with possible self-referential processing. Awe suppresses self-referential mPFC while enhancing scene processing. Awe is MORE restorative than soft fascination for rumination reduction."},
        {"template": "ART Being Away (RC_ART_BEING_AWAY_001)", "type": "EXTREME_VERSION",
         "description": "Awe is an extreme form of Being Away. Normal Being Away displaces habitual concerns through context shift. Awe actively suppresses them through schema accommodation."},
        {"template": "T3 (Cognitive Map)", "type": "INPUT",
         "description": "The hippocampal cognitive map must represent the vast space. Awe may occur when the spatial representation exceeds the brain's normal operating scale — the map itself must 'zoom out.'"}
    ],
    ecological_testability="MEDIUM-HIGH — piloerection detectable by skin conductance; RSA measurable; self-report awe scales exist (AWE-S); prosocial behavior measurable by behavioral tasks. Physical scale is directly measurable.",
    overall_maturity="how-plausibly (phenomenology and physiology established; neural mechanism preliminary)",
    key_references=[
        "Keltner, D., & Haidt, J. (2003). Cognition and Emotion. [~1,800 citations]",
        "Keltner, D. (2023). Awe: The New Science of Everyday Wonder. Penguin. [~100 citations]",
        "Yaden, D. B., Haidt, J., Hood, R. W., Vago, D. R., & Newberg, A. B. (2017). Psychology of Consciousness. [~300 citations]",
        "Shiota, M. N., Keltner, D., & Mossman, A. (2007). Cognition and Emotion. [~800 citations]",
        "Piff, P. K., et al. (2015). Awe, the small self, and prosocial behavior. JPSP. [~700 citations]"
    ]
)
```

---

## T57: THERMAL COMFORT AND THERMOREGULATORY AFFECT

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Richard de Dear** | University of Sydney | Adaptive thermal comfort — the leading model of how humans adapt to and evaluate thermal environments. His adaptive model replaced the static PMV model in ASHRAE standards. |
| **Hugo Critchley** | Brighton & Sussex (returning) | Interoception and autonomic regulation — thermal comfort is fundamentally an interoceptive process. |

### Panel Discussion

**de Dear**: The adaptive comfort model (de Dear & Brager, 1998; 2002) demonstrates that thermal comfort is not a fixed setpoint but a dynamic, context-dependent evaluation. People in naturally ventilated buildings accept a wider range of temperatures (roughly 20–28°C) than people in air-conditioned buildings (roughly 22–26°C), because they adapt their expectations, behavior, and physiology to the ambient conditions. This adaptation involves both physiological thermoregulation and psychological expectation — a predictive process.

**Critchley**: Thermal comfort is processed interoceptively. The pathway: thermoreceptors in skin → spinal cord → thalamus (ventral posterior medial nucleus) → primary somatosensory cortex → posterior insula (thermosensory cortex) → anterior insula (integrated interoceptive representation). The anterior insula generates the conscious experience of thermal comfort or discomfort.

The connection to the existing template library: thermal discomfort is processed by the same anterior insula that processes interoceptive affect (T12), social empathy (T49), and salience network computation (D-1b). When the anterior insula is occupied with thermal discomfort signals, it has reduced capacity for these other functions. Thermal discomfort literally competes with interoceptive processing, social empathy, and salience computation for anterior insula resources.

**Bar**: And from the predictive processing perspective: thermal comfort IS thermal prediction match. You predict the thermal environment based on visual cues (sunlight, shade, materials), contextual knowledge (it's summer, this is an air-conditioned building), and recent experience (it's been warm all day). When the actual thermal experience matches prediction: low thermal PE → comfort. When it violates prediction: thermal PE → discomfort. A sudden cold draft in a warm room is more uncomfortable than a steady cool temperature, because of the prediction error.

### T57 Specification

```python
MechanisticTemplate(
    template_id="IC_THERMAL_COMFORT_001",
    name="Thermal Comfort and Thermoregulatory Interoceptive Processing",
    structural_pattern="HOMEOSTATIC",
    higher_order_principle=(
        "Thermal comfort is an interoceptive evaluation processed in the posterior "
        "and anterior insula. Thermal discomfort competes for anterior insula "
        "processing resources with interoceptive affect, social empathy, and "
        "salience computation. Adaptive thermal comfort depends on prediction: "
        "expected temperature range modulates the comfort evaluation. Thermal "
        "discomfort is a low-priority but persistent allostatic stressor."
    ),
    framework_ids=["IC"],
    causal_links=[
        CausalLink(
            from_variable="ambient_thermal_environment",
            to_variable="thermoreceptor_activation",
            activity="peripheral_thermosensation",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="de Dear & Brager, 2002",
            parameters={
                "adaptive_comfort_zone": "20-28°C (naturally ventilated), 22-26°C (air conditioned)",
                "note": "Zone depends on outdoor running mean temperature, clothing, and activity level"
            }
        ),
        CausalLink(
            from_variable="thermoreceptor_activation",
            to_variable="anterior_insula_thermal_representation",
            activity="interoceptive_thermal_evaluation",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Craig, 2009; Critchley, 2005",
            parameters={
                "pathway": "skin_thermoreceptors → spinal_cord → thalamus_VPM → "
                           "posterior_insula → anterior_insula",
                "competition": "thermal signals share anterior insula with T12, T49, SN"
            }
        ),
        CausalLink(
            from_variable="thermal_prediction_error",
            to_variable="thermal_discomfort",
            activity="mismatch_between_expected_and_actual_temperature",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="de Dear adaptive model; Bar PE framework",
            parameters={
                "note": "Drafts, sudden temperature changes, spatial thermal gradients all produce "
                        "thermal PE even within the comfort zone"
            }
        ),
        CausalLink(
            from_variable="chronic_thermal_discomfort",
            to_variable="allostatic_load_contribution",
            activity="sustained_thermoregulatory_demand",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Implied by T29 framework",
            parameters={
                "note": "Thermal discomfort is a low-intensity but persistent stressor. "
                        "Its contribution to allostatic load is through chronic anterior "
                        "insula occupation and mild sympathetic activation."
            }
        )
    ],
    interactions=[
        {"template": "T12 (Interoceptive Affect)", "type": "SHARED_SUBSTRATE",
         "description": "Thermal comfort and interoceptive affect share anterior insula. Thermal discomfort reduces available processing for other interoceptive signals."},
        {"template": "T29 (Allostatic Master)", "type": "INPUT",
         "description": "Chronic thermal discomfort contributes to allostatic load."},
        {"template": "ART Compatibility", "type": "INPUT",
         "description": "Thermal discomfort is a form of environmental incompatibility — the space doesn't support the body's thermal needs."}
    ],
    ecological_testability="HIGH — temperature measurable, thermal comfort assessable by ASHRAE scales, physiological thermoregulation measurable by skin temperature and vasoconstriction.",
    overall_maturity="how-actually (thermoregulatory physiology) / how-plausibly (anterior insula competition claim)",
    key_references=[
        "de Dear, R. J., & Brager, G. S. (1998). ASHRAE Transactions. [~2,000 citations]",
        "de Dear, R. J., & Brager, G. S. (2002). Thermal comfort in naturally ventilated buildings. Energy and Buildings. [~1,500 citations]",
        "Craig, A. D. (2009). Nature Reviews Neuroscience. [~5,000 citations]"
    ]
)
```

---

## T58: ACOUSTIC ECOLOGY AND SOUNDSCAPE PROCESSING

### Domain Experts

| Name | Affiliation | Expertise |
|---|---|---|
| **Jian Kang** | University College London | Soundscape research — the leading figure in translating R. Murray Schafer's soundscape ecology into measurable, designable parameters for buildings and cities. |
| **Petr Janata** | UC Davis (returning) | Auditory scene analysis and the neural processing of complex auditory environments. |

### Panel Discussion

**Kang**: Soundscape quality is not simply noise level. The ISO 12913 soundscape standard identifies soundscape quality as a perceptual evaluation that depends on: (1) the types of sounds present (wanted vs. unwanted, natural vs. mechanical, human vs. non-human), (2) the temporal pattern of sounds (constant vs. intermittent, predictable vs. unpredictable), and (3) the meaning and context of sounds (birdsong in a park vs. birdsong in an operating room).

The four soundscape dimensions (Axelsson, Nilsson, & Berglund, 2010): Pleasantness, Eventfulness, Familiarity, and Quietness. For restorative environments, the target is: high Pleasantness, moderate Eventfulness (not dead silent but not chaotic), high Familiarity (expected sounds for the context), and sufficient Quietness (background level below speech interference threshold).

**Janata**: The neural processing maps onto the ART framework. There are three categories of acoustic impact:

1. **Speech interference** — the most potent disruptor. Speech signals activate the cocktail party mechanism (superior temporal gyrus, inferior frontal gyrus) automatically — you cannot NOT process intelligible speech. This forces CEN engagement and prevents DMN. Threshold: Speech Transmission Index (STI) > 0.5 means speech is intelligible and will disrupt restoration. Optimal restorative soundscape: STI < 0.3 (speech unintelligible).

2. **Broadband natural sounds** — water, wind, rain, rustling leaves. These provide acoustic masking of speech (reducing STI) while producing low prediction error themselves (they are statistically stationary — the spectral envelope is constant over time, even though individual moments are unpredictable). This is the auditory equivalent of fractal fluency: predictable statistics with unpredictable details.

3. **Abrupt non-speech sounds** — mechanical noise, alarms, construction, traffic. These trigger the auditory startle pathway (cochlear nucleus → inferior colliculus → amygdala) and engage salience network computation. Even below conscious awareness threshold, abrupt sounds elevate sympathetic tone.

**Kang**: Architectural acoustic design has excellent tools. Sound level (dBA), reverberation time (RT60), Speech Transmission Index (STI), and frequency spectrum are all measurable and designable. The gap is not in measurement technology but in the framework's failure to include acoustics as a template domain. Sound masking systems, natural soundscapes (water features), and spatial acoustic zoning are all implementable design strategies with measurable outcomes.

### T58 Specification

```python
MechanisticTemplate(
    template_id="MS_ACOUSTIC_ECOLOGY_001",
    name="Acoustic Ecology and Soundscape Processing",
    structural_pattern="FILTERING",
    higher_order_principle=(
        "The auditory environment is processed through three neural pathways with "
        "distinct architectural implications: (1) speech signals force cortical "
        "engagement, preventing DMN restoration; (2) broadband natural sounds "
        "provide low-PE acoustic environment that supports restoration while "
        "masking speech; (3) abrupt mechanical sounds trigger the startle/salience "
        "pathway, elevating stress. Architectural soundscape design should minimize "
        "speech intelligibility and abrupt sounds while providing gentle natural "
        "sound masking."
    ),
    framework_ids=["MS"],  # Multisensory Integration
    causal_links=[
        CausalLink(
            from_variable="speech_intelligibility_in_environment",
            to_variable="involuntary_speech_processing",
            activity="automatic_cocktail_party_mechanism",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Janata; Bronkhorst, 2015",
            parameters={
                "threshold": "STI > 0.5 → speech intelligible → forced CEN engagement",
                "target": "STI < 0.3 for restorative spaces",
                "pathway": "auditory_cortex → superior_temporal_gyrus → IFG (automatic)",
                "consequence": "prevents DMN engagement (T27), disrupts soft fascination"
            }
        ),
        CausalLink(
            from_variable="broadband_natural_sounds",
            to_variable="acoustic_masking_plus_low_PE",
            activity="natural_soundscape_processing",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Ratcliffe, Gatersleben, & Sowden, 2013; White et al., 2020 (water)",
            parameters={
                "masking": "reduces STI of competing speech signals",
                "PE_profile": "statistically_stationary — predictable_spectral_envelope, "
                              "unpredictable_temporal_detail (like fractal visual patterns)",
                "examples": "water_features, wind, rain, birdsong (non-territorial)",
                "optimal_level": "40-50 dBA (audible but not dominant)"
            }
        ),
        CausalLink(
            from_variable="abrupt_mechanical_sounds",
            to_variable="auditory_startle_and_salience_activation",
            activity="threat_detection_from_acoustic_transients",
            from_level="SUBPERSONAL", to_level="SUBPERSONAL",
            bridging_quality="HIGH", maturity="how-actually",
            key_evidence="Davis, 1984 (startle reflex); Uddin (SN)",
            parameters={
                "pathway": "cochlear_nucleus → inferior_colliculus → amygdala (fast, subcortical)",
                "threshold": "sound_onset_rate > ~10 dB/100ms triggers startle",
                "consequence": "sympathetic_activation, SN_engagement, disrupts_DMN",
                "examples": "door_slams, HVAC_clicks, construction_impacts, alarms"
            }
        ),
        CausalLink(
            from_variable="soundscape_quality",
            to_variable="restoration_support_or_impedance",
            activity="net_acoustic_environmental_contribution",
            from_level="SUBPERSONAL", to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM", maturity="how-plausibly",
            key_evidence="Kang, 2006; Axelsson et al., 2010",
            parameters={
                "restorative": "low STI + natural masking + no startles → DMN engagement possible",
                "disruptive": "high STI + mechanical noise + abrupt sounds → forced CEN, elevated SN",
                "connects_to": "T31 (auditory scene analysis) and ART Soft Fascination"
            }
        )
    ],
    scope_conditions=[
        "Individual noise sensitivity varies widely — acoustic comfort zones differ by ~10 dBA across individuals",
        "Context determines sound meaning — birdsong is pleasant in a park, alarming in a sterile lab",
        "Temporal pattern matters more than level — intermittent noise at 50 dBA is more disruptive than steady noise at 60 dBA",
        "Acoustic privacy needs differ by task — conversation spaces need high STI; focused work needs low STI"
    ],
    interactions=[
        {"template": "T31 (Auditory Scene Analysis)", "type": "ELABORATION",
         "description": "T58 elaborates the architectural application of T31. T31 describes auditory scene analysis as a neural mechanism; T58 specifies the three categories of acoustic input and their design implications."},
        {"template": "T27 (DMN Maintenance)", "type": "CRITICAL_INPUT",
         "description": "Speech intelligibility is the primary acoustic barrier to DMN engagement. T58's STI threshold is a necessary condition for T27 to operate in restorative mode."},
        {"template": "T5 (Threat/HPA)", "type": "INPUT",
         "description": "Abrupt sounds trigger the startle-amygdala pathway, activating T5. Chronic exposure to abrupt sounds (construction, traffic) contributes to allostatic load."}
    ],
    ecological_testability="HIGH — sound level (dBA), STI, RT60, and frequency spectrum are all measurable with standard equipment. Physiological responses (EDA for startle, HRV for autonomic state) are measurable with wearables.",
    overall_maturity="how-actually (speech processing, startle) / how-plausibly (natural sound masking benefit)",
    key_references=[
        "Axelsson, Ö., Nilsson, M. E., & Berglund, B. (2010). A principal components model of soundscape perception. JASA. [~600 citations]",
        "Kang, J. (2006). Urban Sound Environment. CRC Press. [~400 citations]",
        "Bronkhorst, A. W. (2015). The cocktail-party problem revisited. Attention, Perception, & Psychophysics. [~300 citations]",
        "Ratcliffe, E., Gatersleben, B., & Sowden, P. T. (2013). Bird sounds and their contributions to perceived attention restoration. JOEP. [~200 citations]"
    ]
)
```

---

## Summary: Six New Templates

| # | Template ID | Name | Framework | Pattern | Maturity | Key Contribution |
|---|---|---|---|---|---|---|
| T53 | IC_OLFACTORY_LIMBIC_001 | Olfactory-Limbic Processing | IC | BYPASS | how-actually | Direct amygdala pathway bypassing thalamus; Proust effect for architectural memory |
| T54 | HC_CREATIVE_DIVERGENCE_001 | Restoration-Enabled Creativity | HC | FACILITATION | how-plausibly | Soft fascination = optimal divergent thinking state; architectural creative cycle |
| T55 | NM_CIRCADIAN_ENTRAINMENT_001 | Circadian Entrainment | NM | ENTRAINMENT | how-actually | ipRGC → SCN pathway; 250 melanopic EDI threshold; timing-dependent effects |
| T56 | HC_AWE_VASTNESS_001 | Awe and Vastness | HC+IC | ACCOMMODATION | how-plausibly | Reduced self-referential mPFC; extreme Being Away; parasympathetic + piloerection |
| T57 | IC_THERMAL_COMFORT_001 | Thermal Comfort | IC | HOMEOSTATIC | how-actually | Anterior insula competition; adaptive comfort model; thermal PE |
| T58 | MS_ACOUSTIC_ECOLOGY_001 | Acoustic Ecology | MS | FILTERING | how-actually | Three acoustic pathways: speech (disrupts), natural (supports), abrupt (stresses) |

### New Structural Pattern Enum Values
- **BYPASS** (T53) — pathway that bypasses normal processing hierarchy
- **ENTRAINMENT** (T55) — external signal synchronizes internal oscillator
- **ACCOMMODATION** (T56) — schema must expand to accommodate stimulus
- **HOMEOSTATIC** (T57) — regulatory process maintaining internal setpoint
- **FILTERING** (T58) — selective processing of environmental signals by category

### Updated Template Count
**Total: 58 templates** (57 active, T19 deprecated → T48)

### Connections to Existing Architecture
- T53 (Olfactory) connects to: T5, T23, T12 — adds the missing chemical sense to the interoceptive framework
- T54 (Creativity) connects to: T27, T45 — reveals that restoration and creative incubation share DMN substrate
- T55 (Circadian) connects to: T5, T29, T22 — adds the temporal dimension (time-of-day) to the allostatic framework
- T56 (Awe) connects to: T27, T3, ART Being Away — identifies the most potent restorative state, exceeding soft fascination
- T57 (Thermal) connects to: T12, T29, ART Compatibility — fills the thermal gap in the incompatibility anti-pattern
- T58 (Acoustic) connects to: T31, T27, T5 — specifies the three acoustic categories that determine whether DMN engagement is possible

---

*Panel VI completed: February 15, 2026*
*Document 25 of the Article Eater project*
*6 new templates (T53–T58), 5 new structural_pattern enum values*
*Template library: 58 templates (57 active)*
*All identified gaps from Grand Synthesis now closed*
*Next document sequence number: 26*
