# PART XXIV: Functional Circuits and T1 Atoms

**Last updated:** 4 March 2026
**Section numbers:** §160–§167
**Word count:** ~7,660

---

## §160 Introduction: Organizing Principles and Causal Claims

The ATLAS framework has so far addressed three levels of representation:

- **T1 (Atomic Computations):** Computational primitives—lateral inhibition, evidence accumulation, prediction error—that appear across cognitive domains.
- **T1.5 (Theories):** Coherent accounts of specific phenomena (e.g., arousal regulation, affect formation) that compose T1 primitives into mechanistic explanations.
- **T2 (Templates):** Recurring archetypal structures (PREDICTIVE_CODING, HOMEOSTATIC_REGULATION) that instantiate computational motifs in specific domains.

This section introduces two novel organizational structures that sit between T1 and T2: **functional circuits** and a formal stratification of **T1 atoms** into canonical, established, and hypothetical classes.

The central challenge addressed here is epistemic: we must distinguish between the *descriptive power* of circuits (they are powerful organizing tools) and their *metaphysical status* (they do not necessarily correspond to discrete neural modules). As Barrett (2017) has shown, the brain does not contain discrete emotion circuits; the logic extends to computational circuits generally. Yet circuits remain explanatorily indispensable because they capture genuine regularities in how computations compose and recur across domains.

This section develops a careful account of what functional circuits *are* and *are not*, formulates the hierarchy of T1 atoms, and explains how circuits guide evidence collection and theory evaluation in the QA system.

---

## §161 Functional Circuits: Definition and Epistemic Status

### §161.1 Definition

A **functional circuit** is a stereotyped subnetwork of T2 templates that recurs across different T1.5 theories and cognitive domains. It instantiates a T2 computational archetype in a specific phenomenological context, but the archetype itself is domain-general.

For example:
- The **Arousal-Attention Gating Circuit** combines PREDICTIVE_CODING (generating expectations about task relevance) with GATED_PROPAGATION (blocking sensory input during high intrinsic uncertainty) and ACCUMULATION_TO_BOUND (deciding whether to engage attention).
- This same pattern appears in visual attention (Desimone & Duncan, 1995), emotional salience detection (LeDoux, 1996), and metacognitive monitoring (Fleming & Dolan, 2012).
- Each instantiation differs in substrate (visual cortex vs. amygdala vs. anterior insula) and timescale (milliseconds vs. seconds vs. introspective awareness), but the computational *structure* is invariant.

Circuits are thus functionally defined—they describe *what computations do together*, not *where they live in the brain*.

### §161.2 What Circuits Are NOT: The Psychological Reality Fallacy

The most important epistemic clarification: **circuits are not discrete neural modules**, and asserting that they are commits the **psychological reality fallacy**.

Barrett's argument is decisive. She shows that cognitive neuroscience has long assumed that psychological categories (emotion, decision, perception) map onto anatomically distinct neural circuits. Yet the evidence contradicts this. The same neural populations participate in multiple psychological functions; circuits reconfigure dynamically; the same anatomical pathway supports different computations depending on context.

The same logic applies to functional circuits in ATLAS:

1. **Anatomical discreteness is not implied.** The HOMEOSTATIC_REGULATION circuit might involve hypothalamus, insula, ventromedial prefrontal cortex, and diffuse autonomic output. These are not a "circuit" in any anatomical sense; they are anatomically dispersed.

2. **Functional boundaries are pragmatic.** We group templates into circuits because they tend to co-activate and interact. But there is no commitment that the brain maintains this grouping; the grouping is an analytical convenience for us.

3. **Substrate independence is expected.** The same circuit may be realized in silicon, biological neural tissue, or population dynamics in a connectionist network. The circuit describes a computational pattern, not a neural structure.

The correct analogy is to **design patterns in software engineering** (Gamma et al., 1994). The Observer pattern—"notify all listeners when state changes"—recurs everywhere in large software systems. But there is no single Observer object in any program; it is a structural motif, a way of organizing thinking. Circuits function identically.

### §161.3 The Latent Variable Interpretation

The most productive way to think about functional circuits is as **latent variables**: hidden dimensions of structured covariance in the neural-behavioral data. Consider an analogy. Imagine recording the sound of an orchestra. You cannot see the instruments, but by analyzing the statistical structure of the recording—which frequencies co-vary, which timbres cluster, which onsets synchronize—you can recover the major voices. You discover "something like a string section" and "something like a brass section." These voices are not physical objects in the recording; they are patterns of structured covariance that carve the signal at its joints. A functional circuit is exactly this kind of recovered pattern.

When we say "the Sensory Prediction Error Circuit," we are saying that a set of component processes—generating expectations, comparing them with sensory input, computing a mismatch signal, and updating the generative model—tend to co-vary across tasks and studies. Experiments that engage prediction tend to engage error detection; error detection tends to engage model updating; model updating tends to be metabolically coupled with the initial prediction. This co-variance structure is what the circuit captures. It does not live at a single address in the brain; it is a statistical regularity, not an anatomical structure. But the regularity is real, and when it is well-documented, it has genuine explanatory force.

This interpretation draws on the latent variable tradition in psychometrics (Borsboom, Mellenbergh, & van Heerden, 2003) and computational neuroscience (Cunningham & Yu, 2014). The key insight is that latent variables need not correspond to discrete entities to be scientifically meaningful. General intelligence (*g*) is a latent variable; no one claims there is a single "intelligence neuron." Yet *g* predicts performance across dozens of cognitive tasks, and individual differences in *g* have known neural correlates in white matter integrity and cortical thickness. The construct is real without being localized. The same logic applies to functional circuits.

**What this means for ATLAS.** The circuits in the ATLAS registry are hypothesized latent dimensions. For well-evidenced circuits (STRONG status), the covariance pattern has been recovered across multiple paradigms—different labs, different tasks, sometimes different species—and there is converging evidence from perturbation studies (brain stimulation, pharmacological intervention, lesion analysis) that disturbing one component affects others. For moderately evidenced circuits (MODERATE status), the components co-vary as the circuit predicts, but the full factor structure has not been confirmed by independent dimensional analysis. For hypothetical circuits (HYPOTHETICAL status), the circuit is a prediction derived from theoretical considerations—Barrett's (2017) constructionist framework, for example—and the covariance structure remains to be extracted from data.

The latent variable interpretation subsumes three earlier characterizations of what circuits "are":

**Computational universality** (Batterman, 2002): the circuit describes a universality class—a family of systems with different microscopic details but identical macroscopic covariance structure. Accumulation-to-bound, for example, shows the same ramping dynamics in perceptual decision making, belief formation, and aesthetic preference. The circuit is the universal law; different domains are different samples drawn from the same latent factor.

**Organizing principles**: circuits allow us to recognize that arousal regulation, cognitive load regulation, and thermoregulatory affect instantiate the same HOMEOSTATIC_REGULATION archetype. This is the latent variable in action—we see the common factor behind superficially different observations. The gain is predictive: knowing that two phenomena share a latent circuit licenses predictions about one based on manipulations of the other.

**Testable hypotheses**: the latent variable interpretation generates specific, falsifiable predictions. If a circuit is real, then (a) the component processes should load on a common latent factor in behavioral covariance data; (b) perturbation studies (TMS, pharmacological intervention, lesion analysis) should show that disrupting one component affects the others; (c) the factor structure should replicate across independent samples and paradigms; (d) the circuit should be recoverable from neural population recordings via dimensionality reduction techniques (GPFA, demixed PCA, LFADS). These predictions can be tested without any commitment to anatomical localization.

### §161.4 Testing the Latent Variable Interpretation

The claim that circuits are latent variables is itself empirical—it can be confirmed or disconfirmed by data. The primary methods for testing it are:

**Confirmatory factor analysis on behavioral data.** If a circuit is a real latent variable, then behavioral measures of its component processes should load on a common factor. For the Sensory Prediction Error Circuit, tasks measuring prediction accuracy, error detection sensitivity, and model updating speed should covary more with each other than with tasks from other circuits. The factor structure should replicate across samples.

**Dimensionality reduction on neural population data.** Gaussian Process Factor Analysis (GPFA; Yu et al., 2009), demixed PCA (Kobak et al., 2016), and Latent Factor Analysis via Dynamical Systems (LFADS; Pandarinath et al., 2018) are methods for discovering latent dimensions in neural data. If circuits are real latent variables, these methods should recover circuit-like dimensions from population recordings during tasks that engage the relevant computations.

**Cross-paradigm generalization.** A strong test of the latent variable interpretation is whether the factor structure discovered in one experimental paradigm generalizes to a different paradigm that engages the same circuit. If the Homeostatic Regulation Circuit is a real latent variable, its factor structure should generalize from thermoregulation studies to arousal regulation studies.

**Perturbation studies.** If circuit components share a latent cause, then perturbing one component should affect the others. TMS over prediction-related cortex should affect error detection; pharmacological modulation of arousal should affect cognitive load regulation. The prediction is that effects propagate within circuits more than across circuits—a testable claim about the covariance structure under intervention.

These tests require data that ATLAS does not yet have in most cases. The QA system therefore generates targeted article search queries for each circuit, focusing on studies that could provide the relevant evidence. For HYPOTHETICAL circuits, these searches are especially important: they represent the system's active attempt to convert theoretical predictions into empirical knowledge.

---

## §162 The Six T2 Computational Archetypes

Functional circuits instantiate six core computational archetypes. These are cross-domain abstract structures; the circuits that follow are their domain-specific instantiations.

### §162.1 PREDICTIVE_CODING

**Definition:** Generate predictions about sensory or cognitive input; detect deviations (prediction error); update the generative model to reduce error.

**Core dynamics:** The system maintains a forward model (state → expected outcome). When actual outcomes diverge from predictions, the mismatch signal drives model updating. This is Bayesian filtering in its essence: the system continuously revises beliefs about the world based on prediction error.

**Key references:** Rao & Ballard (1999) for visual cortex; Friston (2010) for the free energy principle as unifying framework.

**Neural plausibility:** Excellent. Direct evidence for prediction error signals in dopamine neurons, cerebellar Purkinje cells, and cortical circuits. Canonical implementation via divisive normalization (Carandini & Heeger, 2012).

**Example instantiation:** Visual perceptual learning (Mazzoni et al., 1991); emotional appraisal updating (Schachter & Singer, 1962); theory-of-mind predictions (Saxe & Kanwisher, 2003).

### §162.2 HOMEOSTATIC_REGULATION

**Definition:** Sense a physiological or cognitive variable; detect deviation from a setpoint; apply corrective action to restore equilibrium.

**Core dynamics:** The system monitors a state variable (temperature, arousal, task difficulty) against an internal reference value (setpoint). Discrepancies trigger corrective mechanisms. Critically, homeostasis is not absolute equilibrium; it is dynamic maintenance of functional parameters within bounds that permit continued operation.

**Key references:** Cannon (1929) for physiological homeostasis; Sterling (2012) for allostasis (predictive homeostasis, which updates setpoints based on predicted demands).

**Neural plausibility:** Excellent for classical homeostasis (thermoregulation, osmotic balance); good for arousal and affect (Sterling's allostatic framework).

**Example instantiation:** Arousal regulation via brainstem (Aston-Jones & Cohen, 2005); cognitive load regulation via dynamic task switching (Kool & Botvinick, 2014); emotional affect calibration (Russell, 2003).

### §162.3 ACCUMULATION_TO_BOUND

**Definition:** Integrate evidence over time; when accumulated evidence reaches a threshold, commit to a decision or action.

**Core dynamics:** Evidence streams into an integrator; the integrator sums (or averages) the signal. When the sum reaches a bound, the system commits. The bound may be fixed or adaptive; the timescale may be milliseconds (perceptual decision) or seconds (deliberative choice).

**Key references:** Usher & McClelland (2001) for the Linear Ballistic Accumulator; Gold & Shadlen (2007) for neural bases in decision making; Bogacz et al. (2006) for optimality proofs.

**Neural plausibility:** Excellent. Direct evidence in lateral intraparietal area (LIP), dorsal frontal cortex, and accumbens for decision-related accumulation. Parietal neurons show ramping activity proportional to accumulated evidence.

**Example instantiation:** Perceptual discrimination (motion discrimination in dots task); value-based choice (gambling tasks); belief formation (Bayesian updating, Oaksford & Chater, 2007).

### §162.4 COMPETITIVE_SELECTION

**Definition:** Multiple options or representations compete through mutual inhibition or normalization; winning option is amplified; losing options are suppressed.

**Core dynamics:** Lateral inhibition (winner-take-all) or divisive normalization (softmax competition) ensures that activity in one population suppresses others. Critically, competition is *dynamic*—the winning option depends on input strength and gain modulation.

**Key references:** Desimone & Duncan (1995) for biased competition in attention; Carandini & Heeger (2012) for normalization as canonical neural computation; Miller & Cohen (2001) for prefrontal control.

**Neural plausibility:** Excellent. Ubiquitous in sensory systems and frontal cortex. Normalization is the default computation in cortical circuits.

**Example instantiation:** Visual attention (suppression of unattended stimuli); action selection (motor cortex competition between reach directions); goal representation (prefrontal cortex encoding of task rules in competition).

### §162.5 GATED_PROPAGATION

**Definition:** A signal is blocked or transmitted depending on a gating variable. The gate acts as a context-dependent switch.

**Core dynamics:** Information flows from source A to destination B only when gating signal G is active. The gate can implement attentional filtering (Luck & Vogel, 2013), thalamic relay gating (Sherman & Guillery, 2006), or context-dependent routing in prefrontal networks (Miller & Cohen, 2001).

**Key references:** Sherman & Guillery (2006) for thalamic gating; Luck & Vogel (2013) for attentional gating in sensory systems.

**Neural plausibility:** Excellent. Thalamic reticular nucleus acts as an explicit gate; cortical attention modulates sensory relay; dopamine gates prefrontal output to motor systems.

**Example instantiation:** Selective attention (blocking irrelevant sensory input); working memory gating (preventing distracting information from accessing working memory); motor control (preventing motor output during deliberation).

### §162.6 CONVERGENT_STATE_MONITORING

**Definition:** Distributed signals from multiple sources converge on a common representation of a unified state. The convergence itself constitutes detection of that state.

**Core dynamics:** When many independent sources of evidence agree (or correlate), their convergence allows detection of a unified state that no single source could detect alone. For example, the perception of "fluency" (Reber et al., 2004) emerges from convergence of processing speed, predictability, and semantic coherence. No single signal is fluency; fluency is the detected convergence.

**Key references:** Reber et al. (2004) for fluency as convergent detection; Barrett (2017) for emotion as constructed from convergent interoceptive, contextual, and cognitive signals.

**Neural plausibility:** Moderate. The computational principle is clear; specific neural implementation is less well understood than other archetypes. Likely implemented via synchrony (multi-source signals coordinate in time) or population correlation.

**Example instantiation:** Emotion detection (convergence of arousal, facial expression, context, autobiographical memory—Barrett, 2017); fluency judgments (convergence of processing speed, semantic fit, visual clarity—Reber et al., 2004); metacognitive confidence (convergence of evidence strength, task difficulty, performance history—Fleming & Dolan, 2012).

---

## §163 The Twenty Functional Circuits

Functional circuits are defined by their archetypal structure and their domain of instantiation. Below are the twenty primary circuits identified in the ATLAS framework.

### Circuit Organization

Circuits are organized by archetype and domain. For each circuit, we specify:
- **What it does:** Functional description in 1–2 sentences.
- **Input/output variables:** The signals entering and leaving the circuit.
- **Instantiated in T1.5 theories:** Which major theories rely on this circuit.
- **Empirical status:** Strong (multiple confirmatory studies), Moderate (consistent evidence with some gaps), or Hypothetical (theoretically motivated, limited direct evidence).
- **Neural plausibility:** Assessment based on current neuroscience.

#### PREDICTIVE_CODING Archetype

**1. Sensory Prediction & Error Correction (Visual)**
- Generates predictions about upcoming visual input; updates visual models based on prediction error.
- Inputs: Sensory signal, prior expectation; Outputs: Prediction error, updated model.
- T1.5 theories: Perceptual learning (Mazzoni et al., 1991); visual attention (Corbetta & Shulman, 2002).
- Empirical status: **Strong.**
- Neural plausibility: Direct evidence in visual cortex (Rao & Ballard, 1999).

**2. Action-Outcome Prediction & Feedback Control**
- Predicts sensory consequences of actions; uses feedback error to refine motor commands.
- Inputs: Motor command, actual sensory outcome; Outputs: Feedback error, corrected command.
- T1.5 theories: Motor learning (Shadmehr & Mussa-Ivaldi, 1994); cerebellar models.
- Empirical status: **Strong.**
- Neural plausibility: Cerebellar circuits provide canonical implementation.

**3. Theory-of-Mind Prediction (Mentalizing)**
- Generates predictions about others' mental states; updates model when predictions fail.
- Inputs: Observed behavior, contextual cues; Outputs: Mental state attribution, confidence.
- T1.5 theories: Theory of mind (Saxe & Kanwisher, 2003); social prediction (Schaafsma et al., 2015).
- Empirical status: **Moderate.** Good evidence for mentalizing network; less direct evidence for prediction-error mechanism.
- Neural plausibility: Temporal-parietal junction and medial prefrontal cortex support mentalizing; prediction error signals less well characterized.

**4. Emotional Appraisal & Updating**
- Appraises events for personal relevance; updates emotional response based on new information.
- Inputs: Event features, appraisal dimensions (novelty, relevance, coping potential); Outputs: Emotional response, updated appraisal.
- T1.5 theories: Appraisal theories of emotion (Ellsworth & Scherer, 2003); cognitive control (Ochsner & Gross, 2005).
- Empirical status: **Moderate.** Strong evidence for appraisal dimensions; prediction error aspect less well tested.
- Neural plausibility: Prefrontal-amygdala circuits support appraisal; prediction error signals in amygdala to ventromedial prefrontal cortex.

#### HOMEOSTATIC_REGULATION Archetype

**5. Arousal Regulation (Brainstem & Insula)**
- Monitors arousal state; applies corrective mechanisms to maintain arousal within functional range.
- Inputs: Interoceptive signals (heart rate, pupil dilation), task demands; Outputs: Autonomic adjustments, noradrenergic modulation.
- T1.5 theories: Arousal regulation (Aston-Jones & Cohen, 2005); stress response (Selye, 1936).
- Empirical status: **Strong.**
- Neural plausibility: Locus coeruleus provides direct implementation; brainstem nuclei and insula integrate interoceptive signals.

**6. Cognitive Load Regulation**
- Monitors task difficulty relative to capacity; adjusts task engagement or strategy to maintain optimal load.
- Inputs: Task difficulty, performance error, working memory load; Outputs: Task switching, strategy change, effort adjustment.
- T1.5 theories: Cognitive control (Kool & Botvinick, 2014); task switching (Monsell, 2003).
- Empirical status: **Moderate.** Good evidence for monitoring; mechanism of corrective adjustment less clear.
- Neural plausibility: Anterior cingulate and anterior insula monitor load; prefrontal cortex implements strategy adjustment.

**7. Emotional Thermostat (Barrett's Allostasis Model)**
- Predicts affective demands and preemptively adjusts arousal setpoint; continuously recalibrates emotional baseline.
- Inputs: Predicted emotional demands, situational cues, autonomic state; Outputs: Preemptive arousal adjustment, affect color.
- T1.5 theories: Affect as constructed state (Barrett, 2017); allostasis (Sterling, 2012).
- Empirical status: **Moderate.** Emerging evidence; most directly tested in Barrett's work on emotion construction.
- Neural plausibility: Requires predictive homeostasis; supported by integrator networks linking insula, ventromedial prefrontal, and amygdala.

**8. Metabolic & Autonomic Regulation**
- Senses physiological state (blood glucose, osmolarity, temperature); applies homeostatic corrections via hypothalamic-autonomic axis.
- Inputs: Interoceptive signals; Outputs: Autonomic adjustments, endocrine signaling.
- T1.5 theories: Classical homeostasis (Cannon, 1929); allostasis (Sterling, 2012).
- Empirical status: **Strong.**
- Neural plausibility: Hypothalamus provides canonical implementation.

#### ACCUMULATION_TO_BOUND Archetype

**9. Perceptual Decision Making**
- Integrates sensory evidence over time; commits to decision when evidence reaches threshold.
- Inputs: Sensory signal, threshold setting; Outputs: Decision commitment, reaction time.
- T1.5 theories: Signal detection theory (Green & Swets, 1966); decision field theory (Busemeyer & Townsend, 1993).
- Empirical status: **Strong.**
- Neural plausibility: Direct evidence in lateral intraparietal area and dorsal frontal cortex (Gold & Shadlen, 2007).

**10. Value Accumulation for Choice**
- Integrates value signals over time; commits to action when accumulated value exceeds threshold.
- Inputs: Value estimate for each option, cost of deliberation; Outputs: Action selection, decisiveness.
- T1.5 theories: Reinforcement learning (Sutton & Barto, 1998); value-based decision making (Rangel et al., 2008).
- Empirical status: **Strong.**
- Neural plausibility: Accumbens and ventromedial prefrontal cortex.

**11. Belief Revision via Bayesian Accumulation**
- Accumulates evidence for competing hypotheses; revises belief when evidence for one hypothesis reaches threshold.
- Inputs: Evidence observations, prior beliefs; Outputs: Belief revision, confidence.
- T1.5 theories: Bayesian cognitive models (Oaksford & Chater, 2007); Dretske on evidence accumulation (Dretske, 1981).
- Empirical status: **Moderate.** Behavioral evidence strong; neural evidence for threshold-crossing less direct.
- Neural plausibility: Prefrontal-parietal networks; accumulation dynamics in dorsolateral prefrontal cortex.

**12. Confidence & Metacognitive Judgment**
- Integrates evidence about one's own accuracy; when confidence reaches threshold, commits to metacognitive judgment.
- Inputs: Task performance, task difficulty, prediction error; Outputs: Confidence rating, willingness to act.
- T1.5 theories: Metacognition (Fleming & Dolan, 2012); confidence models (Insabato et al., 2010).
- Empirical status: **Moderate.** Strong evidence for confidence effects; threshold mechanisms less clear.
- Neural plausibility: Anterior prefrontal and posterior cingulate cortex integrate confidence signals.

#### COMPETITIVE_SELECTION Archetype

**13. Visual Attention via Biased Competition**
- Multiple visual representations compete; attended stimulus is amplified; unattended are suppressed.
- Inputs: Stimulus strength, attention weight, top-down goal signal; Outputs: Attended representation, suppressed distractors.
- T1.5 theories: Biased competition (Desimone & Duncan, 1995); selective attention (Corbetta & Shulman, 2002).
- Empirical status: **Strong.**
- Neural plausibility: Visual cortex exhibits competition; attention modulates competition via gain modulation.

**14. Action Selection via Motor Cortex Competition**
- Multiple reach directions and action plans compete; winning action is amplified; losing actions suppressed.
- Inputs: Value of each action, movement-related costs, goal salience; Outputs: Selected action, suppressed alternatives.
- T1.5 theories: Action selection (Cisek & Kalaska, 2010); motor preparation.
- Empirical status: **Strong.**
- Neural plausibility: Lateral intraparietal area (LIP) and dorsal premotor cortex (PMd) show action competition.

**15. Goal Representation via Prefrontal Competition**
- Multiple candidate goals compete for cognitive resources; selected goal is amplified and maintained in working memory.
- Inputs: Goal values, contextual cues, task structure; Outputs: Active goal, suppressed alternatives.
- T1.5 theories: Cognitive control (Miller & Cohen, 2001); working memory (Goldman-Rakic, 1995).
- Empirical status: **Moderate.** Strong behavioral evidence; neural mechanisms of competition less explicitly characterized.
- Neural plausibility: Lateral prefrontal cortex maintains goal representations; competition likely via divisive normalization.

**16. Emotional Response Selection via Amygdala Competition**
- Multiple emotional responses (fear, anger, sadness) compete; dominant response is amplified.
- Inputs: Threat level, context, arousal; Outputs: Dominant emotional tone, suppressed alternatives.
- T1.5 theories: Affect construction (Barrett, 2017); emotion regulation (Gross & John, 2003).
- Empirical status: **Hypothetical.** Amygdala is known to support affective responses; competitive dynamics not directly demonstrated.
- Neural plausibility: Amygdala neurons show opponent coding; lateral inhibition is plausible but not directly confirmed.

#### GATED_PROPAGATION Archetype

**17. Sensory Gating via Thalamic Relay**
- Sensory information is gated at thalamus; relevant inputs pass through; irrelevant inputs are blocked.
- Inputs: Sensory signal, attentional gate signal; Outputs: Gated sensory relay to cortex.
- T1.5 theories: Selective attention (Sherman & Guillery, 2006); thalamic filtering.
- Empirical status: **Strong.**
- Neural plausibility: Thalamic reticular nucleus provides explicit gating.

**18. Working Memory Gating (Context-Dependent Updating)**
- Information is gated into working memory based on context; irrelevant information is blocked.
- Inputs: Candidate information, task context, working memory status; Outputs: Updated working memory, blocked information.
- T1.5 theories: Working memory (Goldman-Rakic, 1995); context-dependent gating (Braver et al., 1997).
- Empirical status: **Moderate.** Good behavioral evidence; neural gating mechanisms less explicit.
- Neural plausibility: Prefrontal dopamine gates striatal input to prefrontal cortex (Durstewitz & Seamans, 2002).

**19. Motor Gating via Dopamine (Action Disinhibition)**
- Motor outputs are gated by dopaminergic disinhibition of striatum; actions are released only when gate is active.
- Inputs: Action plan, readiness signal, dopaminergic tone; Outputs: Released action, gated inhibition.
- T1.5 theories: Motor control (Redgrave et al., 1999); decision-making (Frank et al., 2004).
- Empirical status: **Strong.**
- Neural plausibility: Direct evidence; striatal gating is well characterized.

**20. Affective Gating (Emotion Suppression & Expression)**
- Emotional signals are gated into consciousness/behavior based on social context and self-regulation capacity.
- Inputs: Emotional impulse, social cues, regulatory capacity; Outputs: Expressed emotion, suppressed emotion.
- T1.5 theories: Emotion regulation (Ochsner & Gross, 2005); social emotion (Gazzaniga, 2000).
- Empirical status: **Moderate.** Strong evidence for emotion regulation; gating mechanism less mechanistically specified.
- Neural plausibility: Prefrontal-amygdala interactions; top-down gating of amygdala via anterior cingulate and ventrolateral prefrontal cortex.

---

## §164 T1 Atoms: Canonical, Established, Hypothetical

The T1 level consists of 30 computational primitives. These atoms are the building blocks of circuits and templates. They vary in empirical support and neural plausibility.

### §164.1 Rationale for Stratification

A critical question: why distinguish CANONICAL, ESTABLISHED, and HYPOTHETICAL atoms?

The reason is **epistemic hygiene**. When we construct a circuit or T1.5 theory, we are composing atoms into larger structures. If some atoms are well-established (lateral inhibition, Bayesian updating) and others are speculative (empathic resonance, implicit mentalizing), we must distinguish them. Otherwise, we risk a **compositional fallacy**: assuming that a composite structure is well-supported simply because it *contains* some well-supported components alongside speculative ones.

The stratification forces transparency: When we claim that a circuit instantiates certain computations, we must specify which computations are canonical, which are established but domain-limited, and which are hypothetical. This allows readers (and expert panels) to assess the overall credibility of the circuit.

### §164.2 The Ten CANONICAL Atoms

CANONICAL atoms are neurally grounded, cross-domain confirmed, and fundamental to neural computation.

1. **Lateral Inhibition** — Neurons inhibit neighbors; creates winner-take-all or normalized competition. Core reference: Eccles (1969). Ubiquitous in sensory systems and everywhere from retina to motor cortex.

2. **Divisive Normalization** — Response of neuron A is divided by the sum of responses in its local population. Core reference: Carandini & Heeger (2012). Canonical computation; appears in visual cortex, auditory cortex, motor cortex, and prefrontal cortex.

3. **Synaptic Integration (Summing Inputs)** — Neuron sums (or linearly weights) inputs before firing. Core reference: Hodgkin & Huxley (1952). Fundamental.

4. **Threshold-Crossing** — When integrated input exceeds a threshold, neuron fires. Core reference: Hodgkin & Huxley (1952). Fundamental.

5. **Temporal Integration / Low-Pass Filtering** — Neuron's membrane acts as a capacitor; rapid input fluctuations are smoothed; slow trends are preserved. Core reference: Hodgkin & Huxley (1952). Fundamental.

6. **Spike-Frequency Coding** — Information is encoded in the rate of spikes (not timing). Core reference: Adrian (1928). Ubiquitous.

7. **Predictive Error Computation** — Expected minus actual (or observed minus expected). Core reference: Widrow & Hoff (1960) for delta rule; Rao & Ballard (1999) for neural implementation. Canonical in cerebellum, dopamine neurons, and cortical learning.

8. **Gain Modulation** — Multiplicative amplification of signals based on context. Core reference: Salinas & Sejnowski (2001). Ubiquitous in attention and motor systems.

9. **Recurrent Inhibition / Feedback Inhibition** — Neuron inhibits itself or its input source via recurrent connections. Creates stability and normalization. Core reference: Eccles (1969). Canonical.

10. **Hopfield-Style Associative Attraction** — Neurons with correlated firing potentials have strengthened synapses; activity drifts toward attractor states. Core reference: Hopfield (1982). Canonical in working memory and episodic memory.

### §164.3 The Ten ESTABLISHED Atoms

ESTABLISHED atoms have strong evidence within specific domains but are not universal to all neural systems. They represent important computational motifs that are confirmed but domain-limited.

1. **Dopamine Reward Prediction Error** — Dopamine neurons encode reward minus expected reward; widely confirmed in reward-based learning. Core reference: Schultz et al. (1997). Highly specific to reward system; not universal.

2. **Synchrony Detection** — Neurons preferentially respond to synchronized inputs from multiple sources. Core reference: Singer & Gray (1995). Important in binding and attention; not universal.

3. **Oscillatory Gating** — Rhythmic oscillations (alpha, theta, gamma bands) gate information flow. Core reference: Buzsáki & Draguhn (2004). Well established; function not fully understood.

4. **Sparse Coding** — Information is represented by small subset of highly active neurons; most neurons are quiet. Core reference: Olshausen & Field (1996). Strong evidence in sensory cortex; less clear elsewhere.

5. **Population Vector Averaging** — Direction of movement encoded by population of neurons whose preferred directions "vote" on movement direction. Core reference: Georgopoulos et al. (1986). Strong evidence in motor systems; specificity to movement representation unclear.

6. **Decorrelation / Whitening** — Neural circuits remove correlations from input; information is distributed across neurons. Core reference: Laughlin (1981) for early vision. Well confirmed; scope limited.

7. **Biased Competition (Attention Weighting)** — Attended stimulus is amplified; unattended is suppressed via multiplicative modulation. Core reference: Desimone & Duncan (1995). Strong evidence in visual and attention systems; generality beyond sensory systems unclear.

8. **Working Memory Persistent Activity** — Neurons maintain elevated firing rates during working memory delay; activity encodes maintained information. Core reference: Goldman-Rakic (1995). Strong evidence in prefrontal cortex; mechanism still debated.

9. **Dendritic Computation** — Dendrites perform local computations (nonlinear integration, gating); cell body integrates results. Core reference: Häusser et al. (2000). Increasingly accepted; functional significance for systems-level computation still unclear.

10. **Homeostatic Plasticity** — Synapses scale up or down to maintain firing rate in target range despite changing inputs. Core reference: Turrigiano & Nelson (2004). Well established; timescales and functional roles still being clarified.

### §164.4 The Ten HYPOTHETICAL Atoms

HYPOTHETICAL atoms are theoretically motivated and appear in models and theories, but direct empirical evidence is limited. They are not excluded; they are flagged for closer investigation.

1. **Empathic Resonance** — Observer's neural state automatically converges to actor's state via mirror mechanisms. Popular in theory; neural evidence limited; causal role unclear.

2. **Implicit Mentalizing** — Automatic, unconscious attribution of mental states to others. Theoretically coherent; direct evidence sparse.

3. **Metacognitive Feedback Loop** — Signals from prefrontal cortex provide feedback about one's own cognitive confidence; drives metacognitive judgment. Theoretically sound; direct neural evidence limited.

4. **Interoceptive Precision Weighting** — Brain assigns differential weight to different interoceptive signals based on their reliability. Core to predictive processing; direct evidence for weighting mechanism sparse.

5. **Counterfactual Simulation** — Brain generates hypothetical alternative states (what-if scenarios) by suppressing actual state and simulating counterfactuals. Theoretically central to reasoning; neural implementation unclear.

6. **Theory-of-Mind Prediction Error** — Mismatch between predicted and actual mental state of other person drives mentalizing learning. Analogous to sensory prediction error; direct evidence limited.

7. **Temporal Discounting via Hyperbolic Function** — Value of delayed reward decreases as hyperbolic function of delay. Behavioral fit good; neural mechanism of hyperbolicity unclear.

8. **Intrinsic Motivation Signal** — Separate neural signal drives exploration independent of external reward. Theoretically coherent; neural basis (curiosity signal) not well characterized.

9. **Belief-Desire Attribution via Two-Stream Processing** — Separate neural pathways encode others' beliefs vs. desires. Hypothesized; direct evidence sparse.

10. **Computational Confidence (Precision on Uncertainty)** — Separate meta-level computation estimates confidence in own computations; low confidence triggers recomputation or exploration. Theoretically elegant; neural implementation unclear.

---

## §165 The Hierarchy: Explanatory, Evidential, Compositional

The ATLAS framework maintains three distinct hierarchies. Distinguishing them prevents confusion.

### §165.1 Explanatory Hierarchy (T1 → T1.5 → T2)

The explanatory hierarchy runs top-down from abstract computational principles to domain-specific applications:

$$\text{T2 (Archetype)} \rightarrow \text{T1.5 (Theory)} \rightarrow \text{T1 (Atoms)}$$

Example: PREDICTIVE_CODING (T2 archetype) instantiates in Visual Perceptual Learning (T1.5 theory) via prediction error computation, model updating, and feedback correction (T1 atoms).

**Why this matters:** This hierarchy answers the question "How does this abstract principle realize in a specific domain?"

### §165.2 Evidential Hierarchy (T3 → T2 → T1.5 → T1)

The evidential hierarchy runs bottom-up from empirical data to abstract principles:

$$\text{T3 (Phenomena)} \rightarrow \text{T2 (Template)} \rightarrow \text{T1.5 (Theory)} \rightarrow \text{T1 (Atom)}$$

Example: A study shows that visual perceptual learning involves prediction error signals in visual cortex (T3: empirical phenomena) → instantiates PREDICTIVE_CODING (T2 template) → supports Visual Perceptual Learning Theory (T1.5) → confirms prediction error computation (T1 atom).

**Why this matters:** This hierarchy answers "What evidence supports this atom?" and prevents unsupported inferences.

### §165.3 Compositional Hierarchy

The compositional hierarchy describes how atoms compose into circuits and circuits into theories:

$$\text{T1 Atoms} \rightarrow \text{Circuits} \rightarrow \text{T1.5 Theories}$$

Example: Lateral inhibition + divisive normalization + biased competition (T1 atoms) compose the Visual Attention via Biased Competition circuit (circuit) → instantiates Selective Attention Theory (T1.5).

**Why this matters:** This hierarchy prevents the compositional fallacy. A theory is credible only if its component atoms are established.

### §165.4 Keeping the Hierarchies Separate

A common error: collapsing these hierarchies. For instance:
- Claiming that because PREDICTIVE_CODING (T2) is well-supported, all T1.5 theories instantiating it are well-supported. (Fallacy: different theories may instantiate the archetype differently, with varying empirical support.)
- Claiming that because a circuit is theoretically coherent, its component atoms are empirically confirmed. (Fallacy: atoms may be canonical, established, or hypothetical.)
- Claiming that because a phenomenon (T3) exists, the proposed T1 mechanism is correct. (Fallacy: multiple mechanisms may generate the same phenomenon.)

ATLAS requires explicit mapping: For any theory, specify which atoms compose it, which hierarchies are involved, and what evidence supports each level.

---

## §166 Functional Circuits in the QA System

How should the QA system present functional circuits and their component atoms when answering user questions?

### §166.1 Principle: Epistemic Transparency

The system must be transparent about what circuits *are* (organizing principles and testable hypotheses) and what they *are not* (discrete neural modules, unquestionable realities).

**Standard response format when a circuit is invoked:**

1. **State the circuit's archetype:** "This involves a [ARCHETYPE] structure—[definition]."
2. **List component atoms:** "It requires these computations: [atom names and stratification: CANONICAL/ESTABLISHED/HYPOTHETICAL]."
3. **Note the evidential status:** "Direct support is [strong/moderate/hypothetical]. Key studies: [references]."
4. **Acknowledge limits:** "This is an *organizing principle*, not a claim about discrete neural modules. Different neural implementations may realize this logic."
5. **Offer mechanistic detail:** "Here are the specific T1.5 theories proposing this circuit: [theory names and their contributions]."

### §166.2 Handling Compositional Uncertainty

When a circuit contains atoms of mixed stratification (e.g., CANONICAL + ESTABLISHED + HYPOTHETICAL), the system must surface this uncertainty:

- Present canonical and established atoms with confidence.
- Flag hypothetical atoms and note their speculative status.
- Suggest follow-up empirical work: "To test whether [HYPOTHETICAL atom] operates in this circuit, we would look for [specific evidence]."

### §166.3 Suggesting Competing Accounts

Circuits are not the only way to organize phenomena. The system should note alternatives:

Example: When discussing emotional affect via convergent state monitoring, acknowledge that Barrett's construction theory competes with classical discrete emotion theory (Ekman, 1992) and dimensional emotion theory (Russell, 2003). Each proposes different circuits and mechanisms.

### §166.4 Active Evidence Acquisition: The QA–Search Loop

*Added 2026-03-04.*

One of the most significant architectural decisions in the circuit QA system is that **answering a question about a circuit can trigger the system to search for evidence it does not yet have**. This is not a side effect; it is the primary engineering mechanism for converting epistemic gaps into targeted evidence acquisition.

The architecture works as follows. When a user asks about a functional circuit—say, "Tell me about the dread accumulation circuit"—the circuit QA service does three things. First, it constructs an answer that explains the circuit as a latent variable, situates it in its archetype, and reports its evidential status. Second, it generates a testability section: a set of concrete, accessible descriptions of how the circuit's latent variable interpretation could be tested, along with the data that would be required. Third—and this is the engineering innovation—it emits a set of **search targets**: specific article queries designed to find the evidence that the system currently lacks.

These search targets flow through a three-stage pipeline. The QA handler (`arbitrary_qa_handler.py`) receives the formatted circuit answer and, if search targets are present, inserts them into the `interpretation_space_suggestions` table with source type `circuit_qa` and a priority score of 0.65 (moderate-high, reflecting the importance of evidence gaps for under-evidenced circuits). The recommendation loop service (`recommendation_loop.py`) harvests these suggestions in Step 2b of its cycle, alongside interpretation space gaps (Step 1) and QA follow-up backlog (Step 2). Finally, the top-N suggestions are dispatched to the automated searcher for execution.

The design decision to set priority at 0.65 rather than higher reflects a judgment about the relative urgency of different evidence sources. Interpretation space gaps—where the system's own epistemic operators have identified structural weaknesses—typically score higher (0.6–0.9 based on VOI). Circuit QA targets represent a different kind of gap: the user asked a question, the system answered honestly about what it does not know, and now the system seeks to learn it. This is important but not maximally urgent; it enters the queue at moderate-high priority and competes with other suggestions on merit.

The rationale for this architecture—rather than, say, triggering searches immediately when a circuit answer is generated—is threefold. First, deferred execution via the suggestion pipeline allows the recommendation loop to deduplicate and prioritize across all evidence sources. If two different users ask about circuits in the same archetype, the system generates overlapping search targets that are naturally merged. Second, the pipeline architecture is auditable: every suggestion has a source, timestamp, and priority, and the overseer can monitor the flow. Third, the recommendation loop already handles dispatch, health monitoring, and cycle reporting; adding a new source type to an existing pipeline is more robust than building a parallel dispatch mechanism.

For HYPOTHETICAL circuits, the search targets are especially consequential. These circuits exist as theoretical predictions—Barrett's constructionist framework predicts certain convergent state circuits, for example—but the covariance structure that would confirm them has not been extracted from data. The search targets for HYPOTHETICAL circuits are therefore evidence-seeking in the strongest sense: they represent the system's attempt to find evidence for or against a theoretical prediction. If the evidence is found, the circuit's status upgrades; if the evidence consistently fails to materialize, the circuit should be downgraded or retired.

This pattern—QA responses generating evidence-seeking behavior—instantiates a broader principle that the ATLAS system should be **epistemically active**, not merely a passive repository. When the system encounters the boundary of its own knowledge, it should not simply report the gap; it should act to close it. The circuit QA search target pipeline is the first concrete implementation of this principle in the QA layer.

---

## §167 Conclusion: Circuits as Latent Variables and Epistemic Agents

Functional circuits in ATLAS are not claims about neural anatomy or psychological reality. They are **latent variables**—hidden dimensions of structured covariance in the neural-behavioral data—and their primary function is epistemic: they organize knowledge, generate testable predictions, and actively seek evidence.

The latent variable interpretation (§161.3) resolves a long-standing tension in cognitive neuroscience between the explanatory power of circuits and the lack of evidence for anatomically discrete modules. The resolution is that circuits do not need to be anatomically discrete to be scientifically meaningful. Like general intelligence in psychometrics, circuits capture real patterns of covariation without requiring localized substrates. The evidence for a circuit is the covariance structure itself—recoverable through factor analysis, dimensionality reduction, cross-paradigm generalization, and perturbation studies (§161.4).

The framework avoids the pitfall that has repeatedly caught cognitive neuroscience: assuming that a psychologically meaningful category (emotion, decision, attention) automatically corresponds to a discrete neural system. Instead, circuits describe invariant computational patterns that may be realized across multiple neural substrates, scales, and contexts. The analogy to design patterns in software engineering remains apt: the Observer pattern recurs everywhere in large systems, but there is no single Observer object. The pattern works because it captures a genuine structural regularity. The same is true of functional circuits.

What distinguishes the ATLAS implementation from a static taxonomy is the active evidence acquisition loop (§166.4). When the QA system answers a question about an under-evidenced circuit, it does not simply report the gap; it generates targeted search queries that feed into the recommendation loop for automated evidence acquisition. The system is epistemically active: it seeks to close the gaps in its own knowledge. For HYPOTHETICAL circuits especially, this loop is the mechanism by which theoretical predictions are converted—or fail to be converted—into empirical findings. The circuit registry is not a finished catalogue; it is a living research agenda.

---

## References

Adrian, E. D. (1928). *The basis of sensation: The action of the sense organs*. W. W. Norton.

Aston-Jones, G., & Cohen, J. D. (2005). An integrative theory of locus coeruleus-norepinephrine function. *Annual Review of Neuroscience*, 28, 403–450.

Batterman, R. W. (2002). *The devil in the details: Asymptotic reasoning in explanation, reduction, and emergence*. Oxford University Press.

Braver, T. S., Cohen, J. D., Nystrom, L. E., Jonides, J., Smith, E. E., & Noll, D. C. (1997). A parametric study of prefrontal cortex involvement in human working memory. *NeuroImage*, 5(1), 49–62.

Buzsáki, G., & Draguhn, A. (2004). Neuronal oscillations in cortical networks. *Science*, 304(5679), 1926–1929.

Busemeyer, J. R., & Townsend, J. T. (1993). Decision field theory. *Psychological Review*, 100(3), 432–459.

Carandini, M., & Heeger, D. J. (2012). Normalization as a canonical neural computation. *Nature Reviews Neuroscience*, 13(1), 51–62.

Cannon, W. B. (1929). *Bodily changes in pain, hunger, fear and rage: An account of recent researches into the function of emotional excitement*. D. Appleton.

Cisek, P., & Kalaska, J. F. (2010). Neural mechanisms for interacting with a world full of action choices. *Annual Review of Neuroscience*, 33, 269–298.

Corbetta, M., & Shulman, G. L. (2002). Control of goal-directed and stimulus-driven attention in the brain. *Nature Reviews Neuroscience*, 3(3), 201–215.

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press.

Desimone, R., & Duncan, J. (1995). Neural mechanisms of selective visual attention. *Annual Review of Neuroscience*, 18, 193–222.

Dretske, F. I. (1981). *Knowledge and the flow of information*. MIT Press.

Durstewitz, D., & Seamans, J. K. (2002). The computational role of dopamine D1 receptors in working memory. *Neural Networks*, 15(4–6), 561–572.

Eccles, J. C. (1969). *The inhibitory pathways of the central nervous system*. Charles C. Thomas.

Ekman, P. (1992). An argument for basic emotions. *Cognition & Emotion*, 6(3–4), 169–200.

Ellsworth, P. C., & Scherer, K. R. (2003). Appraisal processes in emotion. In R. J. Davidson, K. R. Scherer, & H. H. Goldsmith (Eds.), *Handbook of affective sciences* (pp. 572–595). Oxford University Press.

Fleming, S. M., & Dolan, R. J. (2012). The neural basis of metacognitive ability. *Philosophical Transactions of the Royal Society B*, 367(1594), 1338–1349.

Frank, M. J., Samanta, J. E., Moustafa, A. A., & Sherman, S. J. (2004). Hold your horses: Impulsivity, deep brain stimulation, and medication in Parkinsonism. *Science*, 318(5854), 1309–1312.

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns: Elements of reusable object-oriented software*. Addison-Wesley.

Gazzaniga, M. S. (2000). *The new cognitive neuroscience* (2nd ed.). MIT Press.

Georgopoulos, A. P., Schwartz, A. B., & Kettner, R. E. (1986). Neuronal population coding of movement direction. *Science*, 233(4771), 1416–1419.

Goldman-Rakic, P. S. (1995). Cellular basis of working memory. *Neuron*, 14(3), 477–485.

Gold, J. I., & Shadlen, M. N. (2007). The neural basis of decision making. *Annual Review of Neuroscience*, 30, 535–574.

Green, D. M., & Swets, J. A. (1966). *Signal detection theory and psychophysics*. John Wiley & Sons.

Gross, J. J., & John, O. P. (2003). Individual differences in two emotion regulation processes. *Journal of Personality and Social Psychology*, 85(2), 348–362.

Häusser, M., Spruston, N., & Stuart, G. J. (2000). Diversity and dynamics of dendritic signaling. *Science*, 290(5492), 739–744.

Hodgkin, A. L., & Huxley, A. F. (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. *The Journal of Physiology*, 117(4), 500–544.

Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational abilities. *Proceedings of the National Academy of Sciences*, 79(8), 2554–2558.

Insabato, A., Pannacciulli, B., & Summerell, G. (2010). Confidence-corrected neural signals. *PLoS Computational Biology*, 6(9), e1000930.

Kool, W., & Botvinick, M. (2014). A labor/leisure tradeoff in cognitive control. *Journal of Experimental Psychology: General*, 143(1), 131–141.

Laughlin, S. B. (1981). A simple coding procedure enhances a neuron's information capacity. *Zeitschrift für Naturforschung C*, 36(9–10), 910–912.

LeDoux, J. E. (1996). *The emotional brain: The mysterious underpinnings of emotional life*. Simon & Schuster.

Luck, S. J., & Vogel, E. K. (2013). Visual attention and the bundling of object features. *Trends in Cognitive Sciences*, 17(12), 655–666.

Marder, E., & Goaillard, J. M. (2006). Variability, compensation and homeostasis in neuron and network function. *Nature Reviews Neuroscience*, 7(7), 563–574.

Mazzoni, P., Andersen, R. A., & Jordan, M. I. (1991). Analysis of the role of visual temporal tuning in the flashlag illusion. *Journal of Neuroscience*, 11(7), 1971–1983.

Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annual Review of Neuroscience*, 24, 167–202.

Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences*, 7(3), 134–140.

Oaksford, M., & Chater, N. (2007). Bayesian rationality: The probabilistic approach to human reasoning. Oxford University Press.

Ochsner, K. N., & Gross, J. J. (2005). The cognitive control of emotion. *Trends in Cognitive Science*, 9(5), 242–249.

Olshausen, B. A., & Field, D. J. (1996). Emergence of simple-cell receptive field properties by learning a sparse code for natural images. *Nature*, 381(6583), 607–609.

Rao, R. P., & Ballard, D. H. (1999). Predictive coding in the visual cortex. *Nature Neuroscience*, 2(1), 79–87.

Rangel, A., Camerer, C., & Montague, P. R. (2008). A framework for studying the neurobiology of value-based decision making. *Nature Reviews Neuroscience*, 9(7), 545–556.

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure. *Personality and Social Psychology Review*, 8(4), 364–382.

Redgrave, P., Prescott, T. J., & Gurney, K. (1999). Is the short-latency dopamine response too short to signal reward error? *Trends in Neurosciences*, 22(4), 146–151.

Russell, J. A. (2003). Core affect and the psychological construction of emotion. *Psychological Review*, 110(1), 145–172.

Salinas, E., & Sejnowski, T. J. (2001). Gain modulation in the central nervous system. *Journal of Neuroscience*, 21(3), 627–635.

Saxe, R., & Kanwisher, N. (2003). People thinking about thinking people: The role of the temporo-parietal junction in "theory of mind." *NeuroImage*, 19(4), 1835–1842.

Schachter, S., & Singer, J. E. (1962). Cognitive, social, and physiological determinants of emotional state. *Psychological Review*, 69(5), 379–399.

Schaafsma, S. M., Pfaff, D. W., Spunt, R. P., & Adolphs, R. (2015). Deconstructing and reconstructing theory of mind. *Trends in Cognitive Sciences*, 19(2), 65–72.

Selye, H. (1936). A syndrome produced by diverse nocuous agents. *Nature*, 138(3479), 32.

Shadmehr, R., & Mussa-Ivaldi, F. A. (1994). Adaptive representation of dynamics during learning of a motor task. *The Journal of Neuroscience*, 14(5), 3208–3224.

Sherman, S. M., & Guillery, R. W. (2006). *Exploring the thalamus and its role in cortical function* (2nd ed.). MIT Press.

Singer, W., & Gray, C. M. (1995). Visual feature integration and the temporal correlation hypothesis. *Annual Review of Neuroscience*, 18, 555–586.

Sutton, R. S., & Barto, A. G. (1998). *Reinforcement learning: An introduction*. MIT Press.

Turrigiano, G. G., & Nelson, S. B. (2004). Homeostatic plasticity in the developing nervous system. *Nature Reviews Neuroscience*, 5(2), 97–107.

Usher, M., & McClelland, J. L. (2001). The time course of perceptual choice. *Psychological Review*, 108(3), 550–592.

Widrow, B., & Hoff, M. E. (1960). Adaptive switching circuits. In *IRE WESCON Convention Record* (Vol. 4, pp. 96–104).

---

**End of PART XXIV**
