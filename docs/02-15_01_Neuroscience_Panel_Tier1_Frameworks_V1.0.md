# Neuroscience Expert Panel: Tier 1 Frameworks and Mechanistic Templates
## How the Theories Actually Work — Critiques, Corrections, Expansions, and Missing Frameworks
## February 15, 2026

---

# PANEL COMPOSITION

Nine neuroscientists and cognitive scientists chosen because they *created* or *work within* the Tier 1 framework theories. Unlike the previous panel (philosophers of scientific reasoning), this panel addresses whether the mechanistic templates are neurobiologically correct, what's missing, and how their theories actually explain environmental effects on cognition, affect, and behavior. They were also explicitly asked: **Are there Tier 1 frameworks missing from the current set of eight?**

1. **Karl Friston** (Neuroscience, UCL) — Creator of the Free Energy Principle, active inference, and the computational framework for predictive processing. *Tier 1 Framework #1*.

2. **Anil Seth** (Neuroscience, University of Sussex) — Leading contributor to interoceptive inference, the "beast machine" theory of consciousness, and controlled hallucination. *Tier 1 Frameworks #1 and #6*.

3. **Lynn Nadel** (Psychology/Cognitive Science, University of Arizona) — Co-author with John O'Keefe of *The Hippocampus as a Cognitive Map* (1978). Foundational contributor to spatial cognition, context-dependent memory, and stress effects on hippocampal function. *Tier 1 Framework #2*.

4. **Andrea Chiba** (Cognitive Science/Neuroscience, UC San Diego) — Expert on basal forebrain cholinergic systems, attention, associative learning, and neural plasticity. Her work on the specificity of cholinergic projections is central to understanding precision modulation and attentional gating. *Tier 1 Framework #5, especially acetylcholine*.

5. **György Buzsáki** (Neuroscience, NYU) — Leading authority on neural oscillations, hippocampal theta rhythms, sharp-wave ripples, and the "neural syntax" hypothesis. His work bridges spatial cognition and memory consolidation. *Tier 1 Frameworks #2 and #7*.

6. **Marcus Raichle** (Neurology/Radiology, Washington University St. Louis) — Discoverer of the default mode network. His characterization of resting-state brain organization transformed understanding of how the brain allocates metabolic resources. *Tier 1 Framework #4*.

7. **Peter Sterling** (Neuroscience, University of Pennsylvania) — Originator of the allostasis concept (with Joseph Eyer). Reframes homeostasis as anticipatory regulation — the brain predicts metabolic needs rather than reactively correcting deviations. *Critical for Tier 1 Frameworks #5 and #6*.

8. **Moshe Bar** (Neuroscience, Bar-Ilan University) — Proactive brain theory — the brain generates predictions and associations continuously, not just in response to stimuli. His work on scene perception, low-spatial-frequency processing, and rapid environmental evaluation bridges predictive processing to actual environmental experience. *Bridges Tier 1 Framework #1 to environmental perception*.

9. **Andy Clark** (Philosophy/Cognitive Science, University of Sussex) — Author of *Surfing Uncertainty* and champion of the "prediction machine" view of the brain. Integrates predictive processing with embodied and extended cognition. *Bridges Tier 1 Frameworks #1 and #8*.

---

# CONTEXT PRESENTED TO PANEL

The panel was shown:
- The corrected three-tier hierarchy (8 Tier 1 frameworks, demoted Tier 2 theories)
- The 20 mechanistic templates from the CMR V2.0 specification
- The Ulrich (1984) worked example showing multi-framework prediction generation
- Three explicit questions:
  1. Are the mechanistic templates neurobiologically correct? What's wrong, missing, or overstated?
  2. How do your specific theories actually explain how built environments affect people?
  3. **Are there Tier 1 frameworks missing from the current eight?** Should any be added, split, or reconceived?

---

# SECTION 1: TEMPLATE CRITIQUE AND CORRECTION

## KARL FRISTON

Your templates represent the free energy principle with reasonable accuracy but miss several things that matter for the architectural application.

**Template 1 (PP_SPECTRAL_MATCH_001) — Mostly correct, but incomplete.** You correctly note that natural scenes have 1/f spectral statistics matching the visual generative model's expectations, producing lower prediction error. But you're treating prediction error as a single scalar quantity when it's actually a hierarchically distributed signal with different functional significance at different levels. Prediction errors at low levels of the visual hierarchy (V1, V2) index violations of local feature expectations — edge orientation, spatial frequency, contrast. Prediction errors at intermediate levels (V4, LOC) index violations of object and texture expectations. Prediction errors at high levels (PFC, scene-selective regions like PPA) index violations of scene category and spatial layout expectations.

This matters for your templates because different architectural features generate prediction errors at different levels. A building with unusual surface textures generates low-level prediction errors. A building with unexpected spatial layout generates high-level prediction errors. The *level* of the prediction error determines which neural systems are engaged in resolution, which neuromodulatory systems respond, and how metabolically costly the processing is. Low-level prediction errors are resolved locally and cheaply. High-level prediction errors recruit broad cortical networks and are metabolically expensive. Your templates should tag prediction error level.

**Template 2 (PP_COMPLEXITY_GOLDILOCKS_002) — Needs precision weighting.** The inverted-U relationship between complexity and preference isn't just about prediction error magnitude. It's about the *interaction* between prediction error and precision. Precision weighting determines how much influence prediction error has on belief updating. In a familiar, safe context (high precision on priors), moderate prediction error is resolvable and rewarding. In an unfamiliar, threatening context (low precision on priors), the same prediction error magnitude becomes aversive because the system can't resolve it — it doesn't have confident enough priors to explain away the surprise.

This means the Goldilocks curve *shifts* with context, familiarity, and emotional state. The same building produces different optimal complexity for a first-time visitor versus a regular occupant. Your template has "observer_familiarity" as a moderator, which is correct, but the mechanism needs to be specified through precision weighting, not as a vague moderating influence. The specific prediction: familiarity increases prior precision → shifts the Goldilocks peak to higher complexity levels → experts and frequent visitors should prefer more complex environments than novices. This is testable.

**Critical addition — Active inference.** Your templates treat the organism as a passive receiver of prediction errors. Active inference (Friston, 2010; Friston et al., 2016) says organisms *act* to minimize prediction error — they don't just update their model, they change the environment to match their predictions. In architectural terms: people don't just perceive buildings, they navigate them, manipulate them, seek information, avoid threats, and adjust their position to optimize their sensory intake. The organism's *action policies* are part of the mechanism.

This generates a prediction missing from your templates: environments that afford active inference — that allow the occupant to *do something* about prediction errors (open a window, adjust lighting, move to a different room, find a landmark) — should be less stressful than environments that trap occupants with unresolvable prediction errors (windowless rooms, featureless corridors, locked wards). The architectural concept of *controllability* gets a precise mechanistic interpretation through active inference: controllability = the availability of action policies that reduce expected free energy.

I'd recommend adding a template:
**PP_ACTIVE_INFERENCE_003**: Environmental controllability → availability of prediction-error-reducing actions → expected free energy reduction → reduced allostatic load. This should be how-plausibly mature — the theoretical derivation is tight, the specific architectural predictions are testable but largely untested.

---

## ANIL SETH

I want to address Template 12 (IC_INTEROCEPTIVE_AFFECT_001) and the broader treatment of interoceptive inference, because several things need correction and one thing needs fundamental expansion.

**Correction 1 — Interoceptive inference is not a downstream consequence of environmental processing.** Your template structures it as: environment → exteroceptive processing → physiological change → interoceptive prediction error → affect. This makes interoception look like a late stage in a serial pipeline. That's wrong. Interoceptive predictions are generated *simultaneously* with exteroceptive predictions, not after them. When you walk into a room, your brain is generating predictions about what you'll see AND predictions about what your body's state should be in this context, simultaneously and interactively.

The correct structure: the brain generates a *joint prediction* across exteroceptive and interoceptive domains. The prediction for a hospital room includes visual expectations (white walls, medical equipment) AND body-state expectations (elevated cortisol, increased heart rate, anxiety). If the body-state prediction is confirmed (you feel anxious as expected), interoceptive prediction error is low — you feel what you expected to feel. If it's violated (you feel calm in a hospital room), that's an interoceptive prediction error that itself requires explanation. This matters because the *predictability* of one's own emotional responses to environments contributes to wellbeing independently of the valence of those responses. Chronically unpredictable affective states are distressing even when occasionally positive.

**Correction 2 — The "beast machine" perspective.** In my recent work (Seth, 2021), I argue that the fundamental function of brains is to regulate the body's physiological condition — to keep the organism alive. All perception, all cognition, all experience serves this function. The experience of being a self, having a body, existing in an environment — these are all controlled hallucinations generated in the service of allostatic regulation.

For neuroarchitecture, this means: the deepest level at which buildings affect people is *allostatic*. Not aesthetic, not cognitive, not even emotional — allostatic. A building that supports efficient physiological regulation (stable temperature, adequate oxygen, appropriate lighting for circadian regulation, acoustic protection from startle responses, clean air for immune function) is a building that supports the organism's most fundamental computational priority. Aesthetic pleasure and cognitive performance are downstream of, and dependent on, successful allostatic regulation.

Your framework currently treats allostasis (via Sterling's work in your neuromodulatory framework) as one system among many. I'd argue it's more fundamental than that — it's the *purpose* that all the other systems serve. The DMN isn't just "resting" — it's performing allostatic maintenance. Prediction error isn't just "surprising" — it signals a potential threat to allostatic efficiency. Spatial navigation isn't just "wayfinding" — it's part of how the organism ensures it can reach resources and avoid threats.

This doesn't necessarily require a separate Tier 1 framework — but it requires restructuring the existing ones to acknowledge that allostatic regulation is the ultimate explanandum, not a parallel concern.

**Specific template addition**: I'd recommend modifying Template 7 (IC_ALLOSTATIC_ANTICIPATION_001) to be much more central than it currently is. Rename it to something like **ALLOSTATIC_EFFICIENCY_001** and position it as the highest-level organizing template — the one that other templates serve. Environments that allow efficient allostatic anticipation → reduced metabolic cost of physiological regulation → freed resources for cognition, affect, social engagement → improved wellbeing across all measures.

---

## LYNN NADEL

I have concerns about how spatial navigation is represented in your templates, particularly Template 3 (SN_LAYOUT_COGNITIVE_MAP_001).

**Concern 1 — The cognitive map is not just a spatial representation.** When John O'Keefe and I wrote *The Hippocampus as a Cognitive Map* in 1978, we were already arguing that the hippocampal system creates a framework for *organizing experience in general*, not just for navigation. The subsequent decades have confirmed this — the hippocampus uses spatial coding as a scaffold for episodic memory, relational reasoning, imagination, and future planning (Eichenbaum, 2017; Bellmund et al., 2018). Place cells don't just encode "where am I" — they encode "what's happening to me here and now," creating conjunctive representations that bind space, time, objects, and events.

For your template, this means: when someone enters a building and their hippocampus creates a cognitive map, that map isn't just a floor plan. It's an experiential record — "in this corridor I felt anxious, at this intersection I was confused, in this room I felt calm." The cognitive map is an *affective-spatial* representation. Architecture that produces coherent, well-organized cognitive maps is simultaneously producing well-organized *experiential* records. Architecture that produces fragmented, unstable maps is producing fragmented experience — and this fragmentation may be a direct mechanism for the disorientation, anxiety, and cognitive impairment documented in wayfinding literature.

**Concern 2 — Context-dependent memory and the architecture of recall.** My subsequent work on context-dependent memory (Nadel & Moscovitch, 1997; Nadel, Samsonovich, Ryan, & Moscovitch, 2000) is relevant but missing from your templates. Memory retrieval is powerfully affected by environmental context — returning to the context in which something was learned dramatically improves recall. This means architectural design shapes not just immediate experience but the *retrievability of past experiences*. Hospitals, schools, offices that maintain consistent spatial contexts support better memory for what happened in those spaces. Frequent renovation or reorganization disrupts context-dependent retrieval.

**Concern 3 — Stress effects on hippocampal function.** Template 6 (NM_CORTISOL_HIPPOCAMPAL_005) correctly identifies that chronic cortisol suppresses hippocampal function. But the specific mechanism matters and your template is vague. Acute stress (minutes) actually *enhances* hippocampal encoding via noradrenergic and glucocorticoid receptor activation — this is why traumatic memories are so vivid. Chronic stress (weeks to months) suppresses hippocampal neurogenesis, dendritic remodeling, and LTP — this is why chronically stressed individuals have poor spatial memory and spatial learning difficulties (Lupien et al., 2009).

The temporal dynamics create an important architectural prediction: a building that produces *intermittent acute stress* (startle responses to unexpected noises, brief disorientation at decision points) may actually enhance memory for the experience. A building that produces *chronic background stress* (persistent noise, constant navigational difficulty, lack of control over environment) will impair both spatial cognition and general memory. The distinction between acute and chronic stress effects on the hippocampus needs to be an explicit temporal parameter in your template, not collapsed into a single "cortisol → hippocampal damage" pathway.

**Missing template**: I'd add **SN_CONTEXT_MEMORY_002**: Environmental context stability → hippocampal context-dependent encoding → memory retrieval efficiency. Maturity: how-actually (robust behavioral and neural evidence for context-dependent memory, strong hippocampal basis).

---

## ANDREA CHIBA

Your treatment of acetylcholine in Template 5 and the neuromodulatory framework generally is correct but seriously undersells the specificity and dynamism of cholinergic function.

**Correction 1 — Cholinergic projections are not diffuse.** The older textbook view was that the basal forebrain cholinergic system is a "diffuse" modulatory system that bathes the cortex in acetylcholine when you need to pay attention. Our work (Zaborszky et al., 2018; Chiba et al., 1995, 1999) has shown this is wrong. Basal forebrain cholinergic projections are remarkably specific in their connectivity — different cholinergic cell groups project to different cortical regions, and acetylcholine release can be coordinated selectively in functionally related cortical areas. This means the cholinergic system doesn't just say "pay attention" — it says "pay attention to *this specific aspect* of the environment using *these specific cortical circuits*."

For your templates, this specificity matters. When an environmental feature captures attention (a novel sound, a moving object in peripheral vision, a change in lighting), the cholinergic system selectively boosts processing in the relevant cortical areas while leaving others relatively unmodulated. This creates a mechanism for *selective environmental influence* — not all features of an environment affect cognition equally at any given moment. The cholinergic system acts as a gating mechanism that determines *which* environmental features get processed with high precision and which are background.

**Correction 2 — Cholinergic timing operates on the scale of seconds.** Our work on basal forebrain dynamics (Tingley, Alexander, Quinn, Chiba, & Nitz, 2014; Tingley et al., 2018) has shown that cholinergic modulation operates on a fast timescale — transient bursts of ACh release lasting seconds, triggered by salient stimuli, modulating cortical processing in real time. This is not a slow, tonic system. Environmental features that trigger rapid cholinergic transients (novelty, salience, reward-predictive cues) have disproportionate influence on cortical processing compared to stable background features.

**Correction 3 — ACh and prediction error have a specific relationship.** Angela Yu and Peter Dayan (2005) proposed that ACh signals *expected uncertainty* — uncertainty that the system expects based on its model of the environment. This is distinct from norepinephrine, which signals *unexpected uncertainty* — surprise. In an architectural context: a building you know is complex (a hospital, an airport) triggers high expected uncertainty → tonic cholinergic elevation → enhanced learning and sensory processing → you process the environment more thoroughly. A building that is *unexpectedly* complex (you thought it was simple and it's not) triggers unexpected uncertainty → phasic noradrenergic response → exploration and arousal.

This ACh/NE distinction generates an important prediction: signage and wayfinding information *before* entering a complex building should shift the balance from unexpected uncertainty (NE-mediated stress) to expected uncertainty (ACh-mediated enhanced learning). The act of *preparing* someone for environmental complexity changes which neuromodulatory system dominates the response. This is testable and practically relevant.

**Template revision**: Template 5 (NM_THREAT_HPA_001) should be split. The "threat → HPA → cortisol" pathway is correct for threat processing, but the attentional/learning pathway (environmental salience → BF-ACh → selective cortical modulation → enhanced processing) is a separate mechanism with different temporal dynamics, different downstream effects, and different architectural implications. I'd add:

**NM_CHOLINERGIC_GATING_007**: Environmental salience/novelty → basal forebrain cholinergic activation → selective cortical precision enhancement → enhanced processing of salient features. Moderators: expected uncertainty (tonic ACh for known-complex environments) vs. unexpected uncertainty (phasic NE for surprising environments). Maturity: how-actually for the basic circuitry, how-plausibly for the architectural predictions.

---

## GYÖRGY BUZSÁKI

I have a fundamental concern with how your templates treat hippocampal function. The templates represent the hippocampus as creating a "cognitive map" — a static spatial representation. This is a legacy of how people read O'Keefe and Nadel, but it's not how the hippocampus actually works.

**The hippocampus is a sequence generator, not a map.** In my recent work (Buzsáki & Tingley, 2018; Buzsáki, 2019), I've argued that the hippocampal system's fundamental computation is generating temporal sequences of neural assembly activations. Place cells fire in sequences as the animal moves through space, but the sequential organization is the computation — the spatial correlate is a consequence of the animal moving while the sequences run. The same sequential machinery is used for episodic memory replay (during sharp-wave ripples), future trajectory planning (during theta), and imagination of never-experienced routes.

For your templates, this matters in two ways.

**First**, the quality of spatial experience in a building depends not just on the "map" but on the **theta sequences** generated during navigation. As an animal (or person) navigates, place cell sequences within each theta cycle represent a compressed trajectory — where you just were, where you are, and where you're about to go (Dragoi & Buzsáki, 2006). These theta sequences are the brain's real-time trajectory planning mechanism. Architecture that allows smooth, predictable theta sequences (long sightlines, gradual turns, clear path structure) should feel navigable and comfortable. Architecture that forces abrupt sequence discontinuities (blind corners, sudden level changes, disorienting turns) should feel jarring and anxiety-producing — because the theta sequences literally can't represent the trajectory smoothly.

**Second**, memory consolidation for architectural experience depends on **sharp-wave ripples** (SPW-Rs) — brief (50-100ms) high-frequency oscillations in the hippocampus during quiet wakefulness and sleep, during which the hippocampus replays compressed versions of recent experience to the neocortex (Buzsáki, 2015; Huszár et al., 2024). SPW-Rs are how experiences get selected for long-term storage. Experiences that are replayed in SPW-Rs are consolidated; experiences that aren't are forgotten.

This generates a specific architectural prediction: moments of pause and quiet reflection *within* the building experience — sitting on a bench after navigating a complex wing, resting in a courtyard, pausing at a window — may be essential for memory consolidation of the spatial experience. Buildings that allow no pauses (constant movement through corridors, no resting places, no views to stop and contemplate) may prevent SPW-R replay and impair spatial learning. The architectural practice of providing rest nodes and contemplation spaces has a neural mechanism: it enables hippocampal replay.

**Missing template**: I'd add **SN_THETA_SEQUENCE_003**: Navigational path structure → theta sequence coherence → trajectory prediction quality → navigational fluency and comfort. Discontinuous paths → theta sequence disruption → prediction failure → disorientation and stress. And **MS_RIPPLE_REPLAY_002**: Environmental pauses/rest opportunities → quiet wakefulness → SPW-R replay of recent spatial experience → consolidation of spatial knowledge. Maturity: how-actually for the oscillatory mechanisms; how-plausibly for the specific architectural predictions.

---

## MARCUS RAICHLE

Template 4 (DT_ATTENTIONAL_DEMAND_001) correctly captures the anti-correlation between DMN and task-positive networks, but it misrepresents the DMN's function and importance.

**Correction 1 — The DMN is not "rest."** When I first characterized the default mode (Raichle et al., 2001), it was defined by *consistent metabolic activity during passive states* — the brain areas that are most active when you're not doing any particular task. The field immediately and unfortunately interpreted this as "the resting network." It's not. The DMN is metabolically expensive — it accounts for a disproportionate share of the brain's glucose consumption. It's doing something important; we just don't externally observe what it's doing because the computation is internal.

Current evidence suggests the DMN performs internal model maintenance: self-referential processing, autobiographical memory retrieval, social cognition (modeling other minds), future simulation, and — critically for your framework — *generative model updating* (Andrews-Hanna, Smallwood, & Spreng, 2014; Buckner & DiNicola, 2019). When the DMN is active, the brain is maintaining, revising, and running its model of the world and the self.

**Correction 2 — Chronic DMN suppression is genuinely pathological.** Your template correctly notes that sustained task-positive engagement suppresses the DMN. What it doesn't sufficiently emphasize is the downstream consequences. Chronic DMN suppression is associated with depressive symptomatology, burnout, impaired social cognition, and reduced creative capacity (Hamilton, Farmer, Fogelman, & Bhatt, 2015). The brain *needs* DMN time the way the body needs sleep — it's when maintenance operations occur.

For architecture, this means the distinction between buildings that *allow* DMN engagement and buildings that *demand* constant task-positive engagement is not a preference issue — it's a health issue. A hospital that demands constant navigational vigilance from patients is not just annoying; it's actively interfering with the brain's maintenance operations at a time when maintenance is critical for recovery. An office that provides no periods of low-demand processing is degrading its occupants' social cognition and creative capacity over time.

**Correction 3 — The DMN has subsystems, not a single function.** The DMN is not monolithic. It has at least two subsystems: a medial temporal lobe subsystem (hippocampus, parahippocampal cortex, retrosplenial cortex) involved in memory and scene construction, and a dorsomedial prefrontal subsystem (dmPFC, TPJ, lateral temporal cortex) involved in social cognition and theory of mind (Andrews-Hanna et al., 2010). Environments might differentially engage these subsystems. Natural environments with spatial depth may engage the MTL subsystem (scene construction, spatial memory). Social environments (cafés, gathering spaces) may engage the dmPFC subsystem (social cognition).

**Template revision**: Template 4 should specify which DMN subsystem is engaged. And add: **DT_DMN_MAINTENANCE_002**: Periods of low environmental demand → DMN re-engagement → {MTL subsystem: spatial model consolidation, scene construction; dmPFC subsystem: social model maintenance, self-referential processing} → long-term cognitive and social health.

---

## PETER STERLING

I want to challenge a fundamental assumption running through all your templates: the assumption that the brain's goal is to minimize prediction error or minimize stress. It isn't. The brain's goal is to achieve **allostatic efficiency** — to regulate the body's internal milieu at minimum metabolic cost.

**The allostasis correction.** Homeostasis (Cannon, 1932) assumes the body maintains fixed set-points and corrects deviations. Allostasis (Sterling & Eyer, 1988; Sterling, 2012) assumes the brain *anticipates* needs and adjusts parameters *before* deviation occurs. The thermostat analogy for homeostasis is wrong — the brain doesn't wait for temperature to drop and then turn on the heater. It checks the weather forecast, knows what time of day it is, remembers what this room is usually like, and pre-adjusts.

For your templates, this has major consequences:

**Consequence 1 — Predictable environments are allostattically efficient.** The single most important environmental property for wellbeing, from an allostatic perspective, is *predictability*. Not novelty, not complexity, not beauty — predictability. A predictable environment allows the brain to anticipate and pre-regulate. An unpredictable environment forces reactive regulation, which is metabolically expensive and produces wear and tear (allostatic load; McEwen, 2007). This doesn't mean environments should be monotonous — the *pattern* of change should be predictable even if specific moments vary. Seasonal rhythms, daily routines, regular traffic patterns are all predictable frameworks within which variation occurs.

**Consequence 2 — Allostatic load is cumulative and architectural.** Your Template 5 (NM_THREAT_HPA_001) treats cortisol as a response to acute threats. But allostatic load accumulates from chronic low-level demands — persistent noise, poor air quality, suboptimal lighting, chronic mild thermal discomfort, constant low-level navigational uncertainty. None of these is acutely stressful, but the metabolic cost of continuously compensating adds up. Buildings generate allostatic load through the *sum* of their suboptimal features, not through any single salient stressor.

**Consequence 3 — The "efficiency" of a building is measurable.** If allostatic efficiency is the right framework, then the measurable impact of a building on occupants is the *total metabolic cost of physiological regulation while in that building*. This can be approximated by: heart rate variability (higher HRV = more efficient regulation), cortisol variability (lower diurnal cortisol variability = more efficient regulation), skin conductance stability, and respiratory pattern regularity. A "good" building, in allostatic terms, is one that *minimizes the total metabolic cost of being a body in that space*.

**Missing template — make it central**: **ALLOSTATIC_EFFICIENCY_MASTER_001**: Sum of environmental demands (thermal, acoustic, visual, navigational, social, air quality) → total allostatic regulatory cost → {if low: metabolic resources available for cognition, social engagement, immune function, growth; if high: metabolic resources diverted to regulation, depleting cognitive, social, immune function}. This should be a *master template* — the one that integrates across all the others and represents the ultimate outcome variable.

---

## MOSHE BAR

I want to focus on something your templates treat too casually — the *speed* of environmental evaluation and the neural mechanisms that support it.

**The proactive brain generates associations before you "see" the scene.** In my work (Bar, 2007, 2009; Bar et al., 2006), I've shown that the brain begins processing environmental information through a fast, low-spatial-frequency pathway that extracts the *gist* of a scene within approximately 130 milliseconds — before detailed object recognition occurs. This fast pathway goes from V1 to prefrontal cortex (via the magnocellular system), where it triggers associative predictions: "This looks like a hospital" → activate hospital-related expectations. These top-down predictions then modulate the slower, detailed processing of the scene in temporal and parietal cortex.

For architecture, this means the *first impression* of a space is determined by its low-spatial-frequency structure — the gross distribution of light and dark, the overall shape of the volume, the proportion of openings to surfaces, the color temperature. Fine details (material textures, decorative elements, signage content) are processed later and interpreted *within the context* of the initial gist-based prediction. If the gist prediction is "institutional" (flat lighting, rectangular proportions, uniform surfaces), then all subsequent detail processing is colored by institutional expectations. If the gist prediction is "welcoming" (warm lighting, varied proportions, natural materials), subsequent processing is colored by those expectations.

**This generates a specific prediction your templates miss**: You can change the *entire experience* of a building more effectively by changing its low-spatial-frequency properties (lighting distribution, volume proportions, opening sizes) than by changing its high-spatial-frequency properties (decorative details, signage design, material texture). This is because the low-spatial-frequency gist frames the interpretation of everything else. A billion dollars of fine finishing in a building with bad proportions and flat lighting won't overcome the initial gist-based prediction of "institutional."

**Missing template**: **PP_RAPID_GIST_004**: Scene low-spatial-frequency structure → magnocellular → PFC associative activation (130ms) → top-down prediction cascade → contextual frame for subsequent detailed processing. Maturity: how-actually for the neural pathway (Bar et al., 2006; Kveraga, Boshyan, & Bar, 2007); how-plausibly for the architectural application.

---

## ANDY CLARK

I want to address two issues: the treatment of embodied cognition in your templates, and a broader architectural concern about the extended mind.

**Template 8 (EC_AFFORDANCE_POSTURAL_001) is too narrow.** You've focused on affordances → postural adjustment → autonomic consequences, which is one valid pathway. But embodied cognition is broader than posture. The key insight from ecological psychology and the embodied cognition tradition (Gibson, 1979; Varela, Thompson, & Rosch, 1991; Clark, 1997) is that cognition is *constitutively shaped* by sensorimotor interaction with the environment — not just modulated by it.

In architectural terms: the act of *moving through* a building is part of the cognitive processing of that building. You don't first perceive the building and then decide to move — perception and action are coupled in a continuous sensorimotor loop. The *trajectory* of movement through a space shapes what is perceived and how it's understood. The same room experienced by walking through it, standing still in it, or sitting in it is three different cognitive objects — because the sensorimotor contingencies are different in each case (O'Regan & Noë, 2001).

Your templates treat movement as a consequence of spatial cognition (navigate → form map → evaluate). The embodied cognition perspective reverses this: movement *is* a form of cognition. The kinesthetic experience of ascending a staircase, the proprioceptive sense of a floor's resistance, the vestibular consequences of looking up in a tall atrium — these are not inputs to cognition, they are *constitutive of* the cognitive experience of the building.

**The extended mind issue.** In my work with David Chalmers (Clark & Chalmers, 1998), we argued that cognitive processes can extend beyond the brain into the environment. For architecture, this is profoundly relevant: a well-designed building is literally *part of the occupant's cognitive system*. A clear wayfinding system extends spatial memory into the environment (reducing hippocampal load). A well-organized office extends working memory into the spatial layout (important documents in accessible locations). A legible façade extends scene understanding into the architectural structure itself.

This means "cognitive load" in buildings is not just about processing demands *on the brain* — it's about the distribution of cognitive work between brain and environment. Good architecture *offloads* cognition into the environment. Bad architecture forces the brain to do all the cognitive work internally. The measurement of architectural quality should include an assessment of *how much cognitive work the building does for the occupant* versus how much the occupant must do themselves.

**Template addition**: **EC_COGNITIVE_OFFLOADING_002**: Environmental legibility and structure → information availability in environment → reduced internal cognitive processing demands → freed cortical resources. This is the extended mind applied to architecture. Maturity: how-plausibly (theoretical framework is well-developed; specific architectural predictions are emerging but largely untested).

---

# SECTION 2: ARE THERE MISSING TIER 1 FRAMEWORKS?

*The panel was explicitly asked whether the current eight Tier 1 frameworks are complete, or whether additional frameworks should be added.*

## CONSENSUS: Three candidates for addition, one for reconceptualization

### Candidate 9: Attention Network Theory

**CHIBA**: I think you need an explicit attention framework at Tier 1. You currently distribute attention across several frameworks — precision weighting in predictive processing, cholinergic gating in neuromodulatory systems, task-positive networks in DMN/TPN dynamics. But attention is its own extensively characterized system with distinct neural architectures.

**Posner and Petersen's (1990; Petersen & Posner, 2012) three attention networks** — alerting (NE-mediated, right hemisphere), orienting (ACh-mediated, parietal), executive/conflict (dopamine-mediated, anterior cingulate/PFC) — are neurally distinct, pharmacologically separable, and differentially affected by environmental features. A sudden noise alerts (NE). A movement in peripheral vision orients (ACh). A confusing sign demands executive attention (DA).

The architectural implications are different for each network. A building that chronically demands alerting attention (unpredictable noise, unsafe areas) is draining the noradrenergic system. A building that chronically demands orienting attention (cluttered visual environment, competing signage) is draining the cholinergic system. A building that chronically demands executive attention (conflicting wayfinding information, ambiguous affordances) is draining the dopaminergic system. These are *different* forms of attentional fatigue with *different* neural and experiential consequences, and they require *different* architectural remedies.

**FRISTON**: I'd push back slightly. Attention is beautifully explained *within* predictive processing as precision optimization — attending to something is increasing the gain on its prediction errors. The three attention networks are implementations of precision optimization in different neural circuits for different signal types. I don't think attention needs to be a separate Tier 1 framework — but I accept that the *implementation details* (which networks, which neuromodulators, which cortical areas) matter for architectural applications and need to be explicitly represented.

**PANEL CONSENSUS ON ATTENTION**: Not a separate Tier 1 framework, but the existing framework coverage needs **explicit attention network templates** that specify how the three attention networks are differentially engaged by environmental features. Add 2-3 templates: alerting-attention, orienting-attention, executive-attention, each with distinct neural substrates, neuromodulatory bases, environmental triggers, and fatigue signatures. Chiba's ACh/NE distinction (expected vs. unexpected uncertainty) should be integrated into these templates.

---

### Candidate 10: Reward and Valuation Systems

**FRISTON**: Your neuromodulatory framework includes dopamine, but treats it as one system among six. Reward and valuation is arguably a separate computational framework with its own extensive theory — Wolfram Schultz's reward prediction error, Kent Berridge's wanting/liking distinction, the orbitofrontal cortex as a "common currency" for valuation, Kable and Glimcher's neuroeconomics framework. These aren't just neurochemistry — they're a computational theory of how the brain assigns value to states, actions, and environments.

**SETH**: I agree this matters. People don't just *perceive* buildings — they *value* them. The valuation process has specific neural circuitry (OFC, ventromedial PFC, ventral striatum) and computational principles (comparison of expected and received value, reference-dependent evaluation, loss aversion). An office that was recently renovated to be worse than expected produces a negative reward prediction error — measured neural and behavioral disappointment — even if the office is objectively fine. The *reference point* matters for valuation, and reference points are set by expectations, past experience, and social comparison.

**BAR**: And the valuation system interacts with my rapid gist processing. The initial low-spatial-frequency gist of a scene triggers not just perceptual predictions but *value predictions* — "This looks like a hospital → I expect this to be unpleasant." These affective predictions modulate all subsequent processing. If the actual experience exceeds the value prediction (the hospital is surprisingly pleasant), positive reward prediction error drives approach behavior and positive affect. If it falls short, negative prediction error drives avoidance.

**PANEL CONSENSUS ON REWARD**: Borderline Tier 1. The computational theory is well-developed and the neural implementation is well-characterized. Currently distributed across neuromodulatory systems (dopamine), predictive processing (prediction error), and interoceptive inference (affect construction). Could remain distributed OR be elevated to Tier 1 as a **Reward/Valuation framework**. The panel recommends adding it as a **Tier 1.5 candidate** — meaning: create templates for the reward/valuation pathways, track its explanatory performance, and decide based on whether it generates predictions that the existing 8 frameworks can't. If it does, promote it. Key references: Schultz, Dayan, & Montague (1997); Berridge & Robinson (2016); Levy & Glimcher (2012).

---

### Candidate 11: Circadian/Chronobiological Regulation

**STERLING**: This is my strongest recommendation. The brain has a master clock (suprachiasmatic nucleus, SCN) that coordinates physiological processes across a 24-hour cycle. Light exposure is the primary zeitgeber (time-giver) that synchronizes the clock to the external world. Buildings mediate virtually all of an urban population's light exposure — the spectral composition, intensity, timing, and duration of light experienced during waking hours is determined by architectural design (window size and orientation, glazing properties, electric lighting spectrum and controls).

Circadian disruption — which buildings can cause through insufficient daylight, blue-enriched evening lighting, irregular light exposure patterns — produces metabolic syndrome, mood disorders, cognitive impairment, immune suppression, and increased cancer risk (Roenneberg & Merrow, 2016; Walker, 2017). This is not speculative — circadian disruption is an established clinical entity with well-characterized mechanisms.

**RAICHLE**: I'll add that circadian rhythms profoundly affect DMN function. The DMN has a circadian profile — its activation patterns change across the day in ways that track alertness, cognitive capacity, and emotional regulation. Disrupted circadian regulation means disrupted DMN cycling, which means disrupted cognitive maintenance.

**SETH**: And circadian regulation is fundamentally allostatic — the SCN is coordinating anticipatory physiological regulation across the 24-hour cycle. Disrupting it doesn't just affect sleep; it disrupts the entire allostatic anticipation machinery.

**PANEL CONSENSUS ON CIRCADIAN**: **Strong candidate for Tier 1 addition.** The neural mechanisms are well-characterized (SCN, retinal melanopsin ganglion cells, melatonin pathway, cortisol circadian rhythm). The environmental mediation is architectural (buildings control light exposure). The health consequences are clinically established. The panel recommends adding **Chronobiological Regulation** as the 9th Tier 1 framework, with specific templates for: (a) architectural light exposure → circadian entrainment quality, (b) circadian disruption → downstream neuromodulatory, cognitive, and immune consequences, (c) time-of-day modulation of all other framework effects. Key references: Czeisler et al. (1999); Roenneberg & Merrow (2016); LeGates, Fernandez, & Hattar (2014).

---

### Reconceptualization: Allostasis as Meta-Framework

**STERLING**: I want to return to Seth's earlier point. Allostasis isn't just one framework among nine. It's the *reason all the other frameworks exist*. Predictive processing serves allostatic efficiency. Spatial navigation serves allostatic efficiency (find resources, avoid threats). Memory serves allostatic efficiency (remember what worked). The DMN serves allostatic efficiency (maintain the models that enable anticipation). Emotion serves allostatic efficiency (motivational states that drive adaptive behavior).

**SETH**: I agree. The question is whether this means allostasis should be *above* the other frameworks (a meta-framework) or *alongside* them (the 10th Tier 1 framework).

**FRISTON**: From the free energy perspective, allostasis IS the free energy principle applied to physiological regulation. The free energy principle already subsumes allostasis — both say the organism minimizes surprise by anticipatory regulation. But I accept that Sterling's formulation makes different predictions than mine in some cases, because allostasis emphasizes metabolic cost in a way the abstract free energy principle does not.

**PANEL CONSENSUS ON ALLOSTASIS**: Not a 10th parallel framework but a **meta-organizing principle** that connects and prioritizes the existing frameworks. All framework effects on wellbeing ultimately cash out as allostatic consequences — metabolic efficiency or inefficiency of physiological regulation. The recommendation: create a **master allostatic template** that represents the final common pathway through which all environmental effects produce health outcomes. Environmental feature → [framework-specific mechanism] → allostatic cost or efficiency → health outcome. This master template integrates across all other templates and provides the ultimate criterion for evaluating architectural quality.

---

# SECTION 3: SPECIFIC TEMPLATE CORRECTIONS AND ADDITIONS

## Summary of Panel-Recommended Template Revisions

| Template | Revision | Source |
|---|---|---|
| T1 (PP_SPECTRAL_MATCH) | Add prediction error LEVEL tag (low/intermediate/high hierarchy) | Friston |
| T2 (PP_COMPLEXITY_GOLDILOCKS) | Mechanism via precision × prediction error interaction, not PE alone; curve shifts with familiarity via prior precision | Friston |
| T3 (SN_LAYOUT_COGNITIVE_MAP) | Map is affective-spatial, not purely spatial; includes experiential binding | Nadel |
| T4 (DT_ATTENTIONAL_DEMAND) | Specify DMN subsystems (MTL vs. dmPFC); DMN is not "rest" but active model maintenance | Raichle |
| T5 (NM_THREAT_HPA) | Split ACh pathway from general threat; add cholinergic specificity and temporal dynamics | Chiba |
| T6 (NM_CORTISOL_HIPPOCAMPAL) | Add temporal distinction: acute (enhances) vs. chronic (impairs) hippocampal function | Nadel |
| T7 (IC_ALLOSTATIC_ANTICIPATION) | Elevate to master-template status; rename to ALLOSTATIC_EFFICIENCY | Seth, Sterling |
| T8 (EC_AFFORDANCE_POSTURAL) | Broaden from postural to full sensorimotor; movement IS cognition, not input to it | Clark |
| T12 (IC_INTEROCEPTIVE_AFFECT) | Fix serial pipeline error: interoceptive predictions are simultaneous with exteroceptive, not downstream | Seth |

## Summary of Panel-Recommended New Templates

| New Template | Content | Source | Maturity |
|---|---|---|---|
| PP_ACTIVE_INFERENCE_003 | Environmental controllability → action policy availability → expected free energy reduction | Friston | how-plausibly |
| PP_RAPID_GIST_004 | Low-spatial-frequency scene structure → fast PFC associative activation → contextual frame | Bar | how-actually |
| SN_CONTEXT_MEMORY_002 | Environmental context stability → context-dependent encoding → retrieval efficiency | Nadel | how-actually |
| SN_THETA_SEQUENCE_003 | Path structure → theta sequence coherence → navigational fluency | Buzsáki | how-actually |
| MS_RIPPLE_REPLAY_002 | Environmental rest opportunities → SPW-R replay → spatial knowledge consolidation | Buzsáki | how-actually/plausibly |
| NM_CHOLINERGIC_GATING_007 | Environmental salience → BF-ACh → selective cortical precision enhancement | Chiba | how-actually |
| DT_DMN_MAINTENANCE_002 | Low-demand periods → DMN subsystem re-engagement → model maintenance | Raichle | how-plausibly |
| EC_COGNITIVE_OFFLOADING_002 | Environmental legibility → information in environment → reduced internal processing | Clark | how-plausibly |
| ALLOSTATIC_MASTER_001 | Sum of environmental demands → total allostatic cost → available resources for function | Sterling, Seth | how-plausibly |
| CHRONO_LIGHT_ENTRAINMENT_001 | Architectural light exposure → SCN entrainment → circadian regulation quality | Sterling, panel consensus | how-actually |

## Panel-Recommended Framework Revisions

| Change | Status |
|---|---|
| Add Chronobiological Regulation as Tier 1 Framework #9 | **Recommended** |
| Add explicit Attention Network Templates within existing frameworks | **Recommended** |
| Create Reward/Valuation as Tier 1.5 candidate with evaluation criteria | **Recommended** |
| Create Allostatic Efficiency as meta-organizing principle | **Recommended** |
| Don't hard-code framework count — design for dynamic framework layer | **Reiterated** (from Panel 1, Gopnik) |

---

# SECTION 4: HOW THE THEORIES ACTUALLY EXPLAIN ENVIRONMENTAL EFFECTS

## Worked Example: A Patient Enters a Hospital Room

*The panel was asked to trace what actually happens, neurobiologically, when a patient enters a hospital room with a view of a garden. Each panelist contributes their framework's perspective.*

**BAR (t = 0-150ms)**: Before the patient consciously "sees" the room, the magnocellular pathway extracts low-spatial-frequency gist. Two competing gists: "hospital room" (rectangular, fluorescent, institutional) and "garden view" (green, varied, natural). The PFC generates rapid associative predictions from both gists. The hospital frame generates expectations of discomfort, medicalization, loss of control. The garden frame generates expectations of calm, safety, organic pattern. These competing predictions begin to modulate subsequent processing within the first 150 milliseconds.

**FRISTON (t = 150ms-1s)**: The prediction errors begin arriving. Hospital-consistent features (bed, IV pole, monitors) generate low prediction error against the hospital frame — expected. The garden view generates low prediction error against the nature frame — expected *given* that frame, but producing a *precision conflict* between the two active generative models. The brain must resolve which frame dominates. The garden view, producing lower overall prediction error (natural scene statistics match the visual generative model more efficiently), begins to win the competition. Precision weighting shifts toward the nature frame.

**CHIBA (t = 1-5s)**: The novel combination (hospital + garden) triggers a phasic ACh release from basal forebrain to visual cortex, boosting processing of the unexpected element (the garden view in a hospital context). The cholinergic system says: "This is worth processing carefully." Simultaneously, the *expected* uncertainty of being in a hospital maintains tonic cholinergic elevation — the patient is in a known-complex environment and the cholinergic system supports enhanced environmental monitoring.

**NADEL (t = 5-30s)**: The hippocampus begins constructing a cognitive map of the room. Place cells activate for the current location. But critically, this map is *affective-spatial* — the hippocampal representation binds the location with the current emotional state (anxiety from hospitalization, partial calm from garden view). The conjunctive representation means that *remembering this room later* will reinstate the affective state, not just the spatial layout. If the garden view produces net positive affect, the room will be remembered more positively than a viewless room, and returning to it will reinstate that positive affect — a therapeutic context effect.

**BUZSÁKI (t = 30s-minutes)**: As the patient settles and stops active exploration, the hippocampal state transitions from theta (active navigation) to quiet wakefulness with intermittent SPW-Rs. The sharp-wave ripples begin replaying the recent experience — entering the room, seeing the garden, the moment of surprise and relief. This replay is the beginning of memory consolidation. If the patient rests quietly (rather than being immediately subjected to medical procedures), the SPW-Rs have time to transfer the spatial-affective experience to neocortex. The garden view becomes part of the patient's consolidated model of "what this hospital is like."

**RAICHLE (t = minutes-hours)**: During rest periods, the DMN re-engages. The MTL subsystem consolidates the spatial experience and runs prospective simulations ("Tomorrow I'll sit by that window"). The dmPFC subsystem processes the social aspects of the hospital experience ("That nurse was kind; the doctor seemed rushed"). Critically, DMN engagement requires that the environment not demand constant task-positive engagement. If monitors are beeping, staff are coming and going unpredictably, and the lighting is harsh, DMN engagement is suppressed and these maintenance operations don't occur.

**SETH (t = hours-days)**: Over time, the interoceptive consequences accumulate. The garden view contributes to lower cortisol through the spectral-match pathway, better circadian regulation through natural light exposure, and more efficient allostatic anticipation (the predictable natural light cycle helps the brain anticipate the day's physiological demands). The patient constructs a positive affective experience not because the garden "causes" good feelings, but because the cumulative interoceptive prediction errors are lower — the body is more predictable to itself, and that predictability is experienced as comfort.

**STERLING (t = days-weeks)**: The allostatic consequences compound. Lower daily cortisol → preserved hippocampal neurogenesis → better spatial learning and memory. Intact circadian rhythm → better sleep → better immune function → faster wound healing. Reduced total allostatic load → more metabolic resources available for tissue repair, immune surveillance, and cognitive function. The Ulrich (1984) finding — shorter hospital stays with nature views — is the macro-level consequence of hundreds of micro-level allostatic efficiencies accumulating over days.

**CLARK (throughout)**: Throughout this entire process, the garden view is not just a stimulus — it's a *cognitive resource*. The patient uses it actively: looking at the garden to self-regulate when anxious (active inference — selecting sensory input to reduce prediction error), using the garden's seasonal changes to track time (cognitive offloading — the environment does temporal orientation work that the patient's brain would otherwise have to do internally), using the garden as a topic of social conversation with visitors (extended cognition — the environment provides shared cognitive content that facilitates social connection).

---

# REFERENCES

Andrews-Hanna, J. R., Reidler, J. S., Sepulcre, J., Poulin, R., & Buckner, R. L. (2010). Functional-anatomic fractionation of the brain's default network. *Neuron*, *65*(4), 550–562. (Cited by ~3,500)

Andrews-Hanna, J. R., Smallwood, J., & Spreng, R. N. (2014). The default network and self-generated thought. *Annals of the New York Academy of Sciences*, *1316*(1), 29–52. (Cited by ~2,000)

Bar, M. (2007). The proactive brain: Using analogies and associations to generate predictions. *Trends in Cognitive Sciences*, *11*(7), 280–289. (Cited by ~1,500)

Bar, M. (2009). The proactive brain: Memory for predictions. *Philosophical Transactions of the Royal Society B*, *364*(1521), 1235–1243. (Cited by ~800)

Bar, M., Neta, M., & Linz, H. (2006). Very first impressions. *Emotion*, *6*(2), 269–278. (Cited by ~1,500)

Bellmund, J. L. S., Gärdenfors, P., Moser, E. I., & Doeller, C. F. (2018). Navigating cognition: Spatial codes for human thinking. *Science*, *362*(6415), eaat6766. (Cited by ~800)

Berridge, K. C., & Robinson, T. E. (2016). Liking, wanting, and the incentive-sensitization theory. *American Psychologist*, *71*(8), 670–679. (Cited by ~1,500)

Buckner, R. L., & DiNicola, L. M. (2019). The brain's default network: Updated anatomy, physiology and evolving insights. *Nature Reviews Neuroscience*, *20*(10), 593–608. (Cited by ~1,500)

Buzsáki, G. (2015). Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning. *Hippocampus*, *25*(10), 1073–1188. (Cited by ~2,000)

Buzsáki, G. (2019). *The Brain from Inside Out*. Oxford University Press. (Cited by ~500)

Buzsáki, G., & Tingley, D. (2018). Space and time: The hippocampus as a sequence generator. *Trends in Cognitive Sciences*, *22*(10), 853–869. (Cited by ~500)

Cannon, W. B. (1932). *The Wisdom of the Body*. Norton. (Cited by ~12,000)

Chiba, A. A., Bucci, D. J., Holland, P. C., & Gallagher, M. (1995). Basal forebrain cholinergic lesions disrupt increments but not decrements in conditioned stimulus processing. *Journal of Neuroscience*, *15*(11), 7315–7322. (Cited by ~300)

Clark, A. (1997). *Being There: Putting Brain, Body, and World Together Again*. MIT Press. (Cited by ~5,000)

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis*, *58*(1), 7–19. (Cited by ~8,000)

Czeisler, C. A., et al. (1999). Stability, precision, and near-24-hour period of the human circadian pacemaker. *Science*, *284*(5423), 2177–2181. (Cited by ~2,500)

Dragoi, G., & Buzsáki, G. (2006). Temporal encoding of place sequences by hippocampal cell assemblies. *Neuron*, *50*(1), 145–157. (Cited by ~1,000)

Eichenbaum, H. (2017). On the integration of space, time, and memory. *Neuron*, *95*(5), 1007–1018. (Cited by ~1,000)

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, *11*(2), 127–138. (Cited by ~8,000)

Friston, K., FitzGerald, T., Rigoli, F., Schwartenbeck, P., O'Doherty, J., & Pezzulo, G. (2016). Active inference and learning. *Neuroscience & Biobehavioral Reviews*, *68*, 862–879. (Cited by ~800)

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin. (Cited by ~35,000)

Hamilton, J. P., Farmer, M., Fogelman, P., & Bhatt, P. (2015). Depressive rumination, the default-mode network, and the dark matter of clinical neuroscience. *Biological Psychiatry*, *78*(4), 224–230. (Cited by ~600)

Huszár, R., et al. (2024). Selection of experience for memory by hippocampal sharp wave ripples. *Science*, *383*(6690), 1478–1483.

Kveraga, K., Boshyan, J., & Bar, M. (2007). Magnocellular projections as the trigger of top-down facilitation in recognition. *Journal of Neuroscience*, *27*(48), 13232–13240. (Cited by ~500)

LeGates, T. A., Fernandez, D. C., & Hattar, S. (2014). Light as a central modulator of circadian rhythms, sleep and affect. *Nature Reviews Neuroscience*, *15*(7), 443–454. (Cited by ~1,500)

Levy, D. J., & Glimcher, P. W. (2012). The root of all value: A neural common currency for choice. *Current Opinion in Neurobiology*, *22*(6), 1027–1038. (Cited by ~600)

Lupien, S. J., McEwen, B. S., Gunnar, M. R., & Heim, C. (2009). Effects of stress throughout the lifespan on the brain, behaviour and cognition. *Nature Reviews Neuroscience*, *10*(6), 434–445. (Cited by ~5,000)

McEwen, B. S. (2007). Physiology and neurobiology of stress and adaptation. *Physiological Reviews*, *87*(3), 873–904. (Cited by ~5,500)

Nadel, L., & Moscovitch, M. (1997). Memory consolidation, retrograde amnesia and the hippocampal complex. *Current Opinion in Neurobiology*, *7*(2), 217–227. (Cited by ~2,500)

Nadel, L., Samsonovich, A., Ryan, L., & Moscovitch, M. (2000). Multiple trace theory of human memory. *Psychological Review*, *107*(2), 225–257. (Cited by ~2,500)

O'Keefe, J., & Nadel, L. (1978). *The Hippocampus as a Cognitive Map*. Oxford University Press. (Cited by ~10,000)

O'Regan, J. K., & Noë, A. (2001). A sensorimotor account of vision and visual consciousness. *Behavioral and Brain Sciences*, *24*(5), 939–973. (Cited by ~3,000)

Petersen, S. E., & Posner, M. I. (2012). The attention system of the human brain: 20 years after. *Annual Review of Neuroscience*, *35*, 73–89. (Cited by ~3,000)

Posner, M. I., & Petersen, S. E. (1990). The attention system of the human brain. *Annual Review of Neuroscience*, *13*, 25–42. (Cited by ~10,000)

Raichle, M. E., et al. (2001). A default mode of brain function. *PNAS*, *98*(2), 676–682. (Cited by ~15,000)

Roenneberg, T., & Merrow, M. (2016). The circadian clock and human health. *Current Biology*, *26*(10), R432–R443. (Cited by ~1,000)

Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science*, *275*(5306), 1593–1599. (Cited by ~12,000)

Seth, A. K. (2021). *Being You: A New Science of Consciousness*. Dutton/Penguin. (Cited by ~500)

Sterling, P. (2012). Allostasis: A model of predictive regulation. *Physiology & Behavior*, *106*(1), 5–15. (Cited by ~800)

Sterling, P., & Eyer, J. (1988). Allostasis: A new paradigm to explain arousal pathology. In S. Fisher & J. Reason (Eds.), *Handbook of Life Stress, Cognition and Health* (pp. 629–649). Wiley. (Cited by ~2,000)

Tingley, D., Alexander, A. S., Kolbu, S., de Sa, V. R., Chiba, A. A., & Nitz, D. A. (2014). Task-phase-specific dynamics of basal forebrain neuronal ensembles. *Frontiers in Systems Neuroscience*, *8*, 174. (Cited by ~50)

Tingley, D., Alexander, A. S., Quinn, L. K., Chiba, A. A., & Nitz, D. (2018). Multiplexed oscillations and phase rate coding in the basal forebrain. *Science Advances*, *4*(8), eaar3230. (Cited by ~50)

Varela, F. J., Thompson, E., & Rosch, E. (1991). *The embodied mind*. MIT Press. (Cited by ~15,000)

Walker, M. P. (2017). *Why We Sleep*. Scribner. (Cited by ~2,000)

Yu, A. J., & Dayan, P. (2005). Uncertainty, neuromodulation, and attention. *Neuron*, *46*(4), 681–692. (Cited by ~3,500)

Zaborszky, L., et al. (2018). Specific basal forebrain-cortical cholinergic circuits coordinate cognitive operations. *Journal of Neuroscience*, *38*(44), 9446–9458. (Cited by ~200)

---

*Google Scholar citation counts approximate as of early 2025.*

**Source conversation**: Article Eater session, February 15, 2026

**END OF DOCUMENT**
