# Implicit vs. Explicit Processing in Predictive Processing: A Gap in the Theory and Its Architectural Consequences

## David Kirsh & Claude | Cognitive Science, UC San Diego | February 2026

---

## WORKING DOCUMENT — Sections 1-4, Appendix A, and Expert Panel EC-I Complete (Session 6)

This document captures a critical theoretical discussion that emerged during Session 5 of the Goldilocks Principle / CNfA development. It identifies a structural limitation in Predictive Processing as a theory of cognition and proposes an architectural framework that distinguishes two computational regimes with different environmental requirements. **Status**: Sections 1-4, Appendix A, and Expert Panel EC-I are complete. Templates EC-1 through EC-12 generated. **Remaining task**: (4) Add slides to Goldilocks presentation.

---

## 1. THE PROBLEM: DIFFERENT KINDS OF LEARNING REQUIRE DIFFERENT KINDS OF ENVIRONMENTAL SUPPORT

### 1.1 The Kidd Framework Is Single-Level Parameter Estimation

The Kidd Goldilocks data (Kidd, Piantadosi, & Aslin, 2012 [GS: ~700]) demonstrates that 7-8 month old infants preferentially attend to visual and auditory events of intermediate complexity (~1.25 bits), as measured by negative log probability under an ideal Bayesian learner. This is a clean inverted-U: too predictable (nothing to learn) and too surprising (unlearnable) both produce look-away; intermediate surprise sustains attention.

But what the ideal learner computes is **single-level parameter estimation within a known model structure**: the infant maintains a Dirichlet-multinomial distribution over event types, and surprise is computed relative to that posterior. The Goldilocks zone is where the next event maximally updates the parameters of that single distribution.

### 1.2 Real Cognition Involves Multiple Simultaneous Inference Problems at Different Hierarchical Levels

An agent engaged in serious cognitive work—a researcher reading a paper, an architect evaluating a space, a surgeon planning an approach—maintains multiple simultaneous inference streams:

- **(a) First-order prediction**: Predicting the next item in a sequence (what word comes next, what's around the corner)
- **(b) Model selection**: Inferring *what kind of thing this is*—what generative model is producing the data (is this a Markov chain or a hidden Markov model? Is this building organized radially or on a grid?)
- **(c) Ecological inference**: Inferring something about the *class of situations* in which this kind of pattern appears (what does this tell me about how this kind of building typically works?)
- **(d) Cross-domain theory building**: Connecting what you're seeing to a broader theoretical question that uses this as evidence but concerns an entirely different domain (does the way people learn sequences tell me something about how they learn spatial layouts?)

Each level has its own distribution over hypotheses, its own PE, and its own informativeness measure—and **these levels don't agree about what stimulus is maximally informative**.

An event completely predictable at level (a)—you knew the next box would be red—might be massively informative at level (b)—because the fact that it was red *again* discriminates between competing generative models. And it might be transformative at level (d)—because the confirmed pattern maps onto a theoretical conjecture about an entirely different domain.

### 1.3 Three Computational Problems the Kidd Framework Doesn't Capture

**Problem 1: Structure learning vs. parameter learning.** Model selection—figuring out which generative model best explains the data—is computationally much harder than parameter estimation. The informativeness of a datum for model selection depends on how much it discriminates between competing models, not on how surprising it is under the current best model. A datum with low first-order PE can have enormous model-selection value (Tenenbaum, Kemp, Griffiths, & Goodman, 2011 [GS: ~3,500]).

**Problem 2: Multiple active conjectures running in parallel.** Unlike the Kidd infant with one learning problem and one posterior, an expert maintains multiple active inference streams simultaneously. Each has its own precision-weighted PE, and the "optimal" environment is not the one that maximizes information gain for any single stream but the one that **allocates precision appropriately across streams**.

**Problem 3: Model construction (not just model selection).** When a thinker proposes a new model that wasn't in the candidate set—composing elements from different domains into a novel explanatory structure—this goes beyond what standard hierarchical Bayesian inference provides. It arguably requires something like a symbolic compositional system operating *on top of* the probabilistic inference machinery (Lake, Ullman, Tenenbaum, & Gershman, 2017 [GS: ~3,500]).

---

## 2. THE IMPLICIT/EXPLICIT DIVIDE: TWO COMPUTATIONAL REGIMES

### 2.1 PP Is Fundamentally a Theory of Subpersonal, Automatic Processing

The standard PP story (Friston, 2010; Clark, 2013, 2016) describes subpersonal, automatic, inference-like processes. Prediction errors propagate upward, precision is allocated, priors are updated, active inference unfolds—and all of this happens without anyone deciding to do any of it. The system is self-organizing.

- **Attention** in PP = precision-weighting (gain control, not deliberate act)
- **Learning** in PP = automatic Bayesian updating
- **Action** in PP = motor system resolving proprioceptive PE

The whole architecture is designed to explain intelligent behavior **without a homunculus**—without anyone inside the system choosing what to attend to, what to learn, or what conjecture to pursue.

For a vast amount of cognition, this is probably right. The Kidd infant data is entirely about implicit processing. Environmental influence on explore/exploit is unconscious. The Goldilocks principle at this level is an automatic optimization.

### 2.2 Deliberate Cognition Is Not Well Described as Automatic PE Propagation

When a researcher deliberately entertains a conjecture, holds it in mind, evaluates evidence for and against it, decides to push on it rather than some other conjecture, and chooses to focus attention on a specific aspect of a theoretical landscape—this is executive, strategic, volitional cognition:

- **Controlled processing** (Shiffrin & Schneider, 1977 [GS: ~7,000])
- **System 2** (Kahneman, 2011 [GS: ~60,000+])
- **Cognitive control** (Botvinick et al., 2001 [GS: ~6,000]; Miller & Cohen, 2001 [GS: ~10,000])

### 2.3 Three Layers of the Problem

**Layer 1: The attention-as-precision story is incomplete for deliberate attention.** PP handles involuntary attention well (loud noise → phasic precision increase on auditory channel). But deliberately choosing to attend to the logical structure of an argument rather than the font it's printed in is not stimulus-driven precision adjustment. It's top-down, goal-directed allocation. Clark (2017, "Predictions, Precision, and Agentive Attention") acknowledges this but offers the same mechanism (precision-weighting from "higher-level predictions"), which pushes the explanatory burden upward without resolving it. This is a **version of the homunculus problem** that PP was supposed to dissolve but hasn't fully dissolved for explicit cognition.

**Layer 2: The computational difference between implicit and explicit processing is real, not just phenomenological.** Implicit processing is fast, parallel, high-capacity, inflexible (operates within existing models). Explicit processing is slow, serial, low-capacity, flexible (constructs novel model structures, composes unprecedented representations, reasons about hypotheticals). PP handles the implicit side well. The explicit side—deliberate compositional reasoning—is not well captured by PE propagation in a fixed hierarchy.

**Layer 3: Architectural implications are significant.** If deliberate cognition is a genuinely different computational regime—not just a higher level of the same hierarchy—then environmental requirements may be qualitatively different, not just quantitatively more demanding.

---

## 3. TWO-REGIME ENVIRONMENTAL REQUIREMENTS

### 3.1 Implicit Regime: Goldilocks-Sensitive, PE-Magnitude-Driven

- Moderate PE optimal (Kidd's inverted-U)
- Unconsciously modulated by environmental statistics
- Environment sets the explore/exploit dial automatically
- Well-captured by the Goldilocks framework
- **Critical variable**: Information rate (PE per unit time)

### 3.2 Explicit Regime: Interruption-Sensitive, PE-Variance-Driven

- Not about PE magnitude but about **protected workspace**
- Temporal stability and interruption protection are primary requirements
- Every phasic LC burst doesn't just steal precision momentarily—it can **collapse the fragile structure of an extended deliberative inference** that has been building over minutes
- Cognitive cost of interruption is proportional to complexity of the mental structure that must be rebuilt, not to the duration of the interruption
- **Critical variable**: Uninterrupted duration of protected low-PE conditions; PE variance over time

### 3.3 The Mean vs. Variance Distinction

- **Implicit processing** is sensitive to the **mean** of the PE distribution (average surprise level → Goldilocks zone)
- **Explicit processing** is sensitive to the **variance** of the PE distribution (how predictable the prediction errors themselves are)

A room averaging 45 dB with occasional 70 dB spikes (alarms, speech intrusions, HVAC cycling) is far worse for deep processing than a room averaging 50 dB continuously. The spikes kill explicit processing because each triggers a phasic response that collapses the deliberative structure.

More precisely: explicit processing optimizes on the **precision of the PE signal itself**—how predictable the prediction errors are. If PE is steady and predictable, the system can commit stable precision to high-level inference. If PE is volatile, the system must hold precision in reserve for environmental monitoring, reducing what's available for deliberation.

### 3.4 The Goldilocks Zone Is Not a Single Zone

The Goldilocks zone is different for each level of the inferential hierarchy, and the zones can conflict:

| Inferential Level | What's Optimal | Why |
|---|---|---|
| Sequence prediction (Kidd level) | Moderate PE | Maximizes single-level information gain |
| Model selection | Discriminating evidence | May be low first-order PE but high model-diagnostic value |
| Theory building | Protected quiet + slow integration | Needs uninterrupted temporal stability, not moderate surprise |
| Environmental monitoring | Near-zero PE | Should be running on autopilot, not capturing attention |

The best environments for serious cognitive work support **both regimes simultaneously**: moderate complexity for implicit processing (keeps system alert, mildly exploratory), combined with high temporal stability for explicit processing (protects deliberative workspace).

---

## 4. IMPLICATIONS FOR ARCHITECTURAL DESIGN

The two-regime framework transforms the design question. Under the standard Goldilocks account, the architect's task is to drive environmental complexity toward an optimal mean — moderate PE across sensory channels. Under the two-regime account, the architect faces a more complex optimization: simultaneously providing moderate-complexity stimulation to keep the implicit system alert and exploratory, while ensuring temporal stability and interruption protection for the explicit system's fragile deliberative workspace. These are not the same thing, and in many conventional environments they are actively in conflict.

What follows is an attempt to spell out the architectural consequences of this dual requirement across five building types, followed by a treatment of temporal design and the special role of personal environmental control. The examples are drawn from the empirical literature on environmental psychology, post-occupancy evaluation, and neuroarchitectural research, though the two-regime theoretical framing is new and generates predictions that have not yet been directly tested.

### 4.1 The General Principle: Mean-Optimization vs. Variance-Minimization

The implicit regime optimizes the *mean* of the non-task PE distribution. If background sensory channels deliver moderate complexity — a view of moving foliage, variable natural light, moderate acoustic texture — the system remains in the Goldilocks zone: alert, mildly exploratory, with well-calibrated arousal via the LC-NE system (Aston-Jones & Cohen, 2005). Too little complexity produces hypo-arousal and mind-wandering; too much produces hypervigilance and attentional capture. This is the standard Goldilocks story, well supported by decades of environmental preference research (Kaplan & Kaplan, 1989 [GS: ~7,500]; Berlyne, 1971 [GS: ~5,000]).

The explicit regime optimizes the *variance* of the non-task PE distribution over time. What matters is not the average level of background stimulation but the *predictability* of that level. A room at a steady 50 dB is better for sustained deliberation than a room averaging 45 dB with irregular spikes to 70 dB, because each spike triggers a phasic LC-NE burst that resets precision allocation across the cortical hierarchy (Bouret & Sara, 2005 [GS: ~1,200]). The explicit processing stream does not merely pause during such an interruption — the fragile extended structure of a multi-step inference may collapse entirely, requiring costly reconstruction (Monk, Trafton, & Boehm-Davis, 2008 [GS: ~300]; Altmann & Trafton, 2002 [GS: ~800]).

The design principle that follows is: **moderate complexity plus temporal stability**. The best environments for serious cognitive work provide rich but steady background stimulation — enough to keep the implicit system engaged without boring it, delivered in patterns predictable enough that the explicit system can safely ignore them.

### 4.2 Offices: Focus Pods, Collaboration Zones, and the Open-Plan Catastrophe

The open-plan office is the single most instructive case for the two-regime framework, because it represents a near-perfect optimization for the implicit regime at the expense of a near-total destruction of the explicit regime.

**Why open plans feel stimulating.** Open offices provide moderate visual complexity (people moving, varied spatial depth, changing configurations), moderate acoustic texture (conversation fragments, movement sounds, typing), and high social information (facial expressions, postures, approach trajectories). For the implicit system, this is close to ideal: the sensory environment is rich enough to sustain alertness without being overwhelming, and the social information stream provides precisely the kind of moderately predictable, moderately surprising event sequence that the Goldilocks zone favors. This is why post-occupancy surveys often find that employees in open offices report feeling more "energized" and "connected" (Kim & de Dear, 2013 [GS: ~1,200]) — their implicit systems are, in fact, well-served.

**Why open plans destroy deep work.** The same features that optimize the implicit regime are catastrophic for the explicit regime. Conversation fragments are not merely loud — they are *semantically salient*, meaning the language processing system cannot suppress them (Colle & Welsh, 1976 [GS: ~600]; Jones & Macken, 1993 [GS: ~400]). The irrelevant speech effect is not an attention failure; it is an architectural consequence of the fact that auditory language processing is largely obligatory in the early stages (Bregman, 1990 [GS: ~5,500]). Each semantically parsed speech fragment generates PE at multiple levels of the predictive hierarchy, and importantly, speech fragments from overheard conversations are *maximally unpredictable* in content and timing — they maximize PE variance on exactly the channel that is hardest to suppress.

Movement in the visual periphery is similarly obligatory in its early processing. Each new person entering the visual field triggers an orienting response — a PE-driven phasic reallocation of precision toward the moving stimulus (Corbetta & Shulman, 2002 [GS: ~10,000]). In evolutionary terms, this makes perfect sense: moving objects in the periphery were potential threats or opportunities, and the cost of missing them was lethal. In an open office, this means the explicit system is subjected to unpredictable interruptions every few minutes as colleagues walk past, stand up, or enter the space.

The empirical evidence bears this out decisively. Bernstein and Turban (2018 [GS: ~400]) found that the transition from cubicles to open offices *reduced* face-to-face interaction by approximately 70% while increasing electronic messaging by roughly 50% — the opposite of the intended effect. Employees, deprived of environmental support for the explicit regime, constructed substitute privacy through behavioral withdrawal (headphones, averted gaze, electronic communication). This is active inference in the service of variance minimization: when the environment fails to protect the deliberative workspace, agents restructure their social behavior to achieve what the architecture did not provide.

**The focus pod as explicit-regime shelter.** The proliferation of small enclosed rooms in contemporary office design — phone booths, focus pods, one-person quiet rooms — represents an implicit architectural recognition of the two-regime problem, though it is rarely articulated in these terms. The typical focus pod provides low PE variance (solid walls, acoustic isolation, minimal visual distractions) at the cost of very low PE mean (blank walls, no view, poor air quality from undersized HVAC). It protects the explicit regime by starving the implicit regime. Users report that such pods are useful for short bursts of focused work but become oppressive over longer periods (Waber et al., 2014) — precisely the phenomenology predicted by a framework in which the implicit system, deprived of its Goldilocks zone, generates the aversive signal of boredom.

**The two-regime office.** The design implication is that the best office environment for knowledge work provides: (a) moderate spatial and visual complexity (prospect views, natural materials, biophilic elements) delivered with high temporal stability (no sudden changes, predictable patterns of movement), (b) acoustic masking that reduces PE variance rather than PE mean (steady-state natural sounds or calibrated pink noise rather than silence punctuated by speech), and (c) spatial boundaries that allow occupants to select their position along the implicit-explicit continuum (from socially embedded collaboration zones to acoustically isolated deep-work rooms, with intermediate zones of partial enclosure).

The research of Mehta, Zhu, and Cheema (2012 [GS: ~1,200]) on ambient noise and creativity provides indirect support: they found that moderate ambient noise (~70 dB) enhanced creative performance relative to both low (~50 dB) and high (~85 dB) noise — an inverted-U consistent with the implicit Goldilocks — but crucially, the noise in their experiment was *steady-state* (constant café ambiance), not variable. The two-regime framework predicts that the same *average* noise level would impair creativity if delivered with high temporal variance (intermittent speech, door slams, HVAC cycling).

### 4.3 Hospitals: Surgical Suites, Recovery Wards, and the ICU Problem

Hospitals present the two-regime problem in perhaps its most consequential form, because the stakes of cognitive failure are measured in morbidity and mortality.

**Surgical suites: explicit-regime environments par excellence.** The operating theater is the paradigm case of an environment that must protect the explicit regime. A surgeon performing a complex procedure maintains multiple simultaneous inference streams (anatomical prediction, complication monitoring, team coordination, procedural sequencing) over extended periods, and each stream involves the kind of deliberate, compositional reasoning that the explicit regime supports. Interruptions during surgery have been directly linked to technical errors: Healey, Sevdalis, and Vincent (2006 [GS: ~200]) found that irrelevant conversation and equipment problems were the most common sources of flow disruption, and Weigl et al. (2012 [GS: ~150]) found that surgical workflow disruptions were associated with compensatory behaviors that increased overall procedure time and complication risk.

The two-regime framework generates a specific prediction: it is not the *number* of stimuli in the OR that matters, but the *temporal unpredictability* of non-task stimulation. A steady, predictable auditory environment (even one at moderate volume) should be less disruptive than a quiet environment with unpredictable intrusions. There is suggestive evidence for this in the music-in-surgery literature: Ullmann et al. (2008 [GS: ~150]) found that surgeon-selected background music did not impair performance and may have improved it, consistent with the idea that steady-state moderate stimulation serves the implicit regime (keeping arousal calibrated) without disturbing the explicit regime (because its temporal signature is predictable). The key variable is whether the auditory environment is self-selected and predictable or externally imposed and variable.

**Recovery wards: implicit-regime environments for healing.** The patient recovering from surgery or acute illness is in a fundamentally different cognitive state. The explicit processing demands are typically low (no complex deliberation required), while the implicit system is engaged in the critical work of physiological recovery — a process that unfolds through interoceptive prediction and allostatic regulation (Sterling, 2012 [GS: ~1,500]; Barrett & Simmons, 2015 [GS: ~700]). Ulrich's foundational finding that patients with window views of nature recovered faster than those facing a brick wall (Ulrich, 1984 [GS: ~6,000]) is, in the two-regime framework, an implicit-regime phenomenon: the natural view provides moderate, temporally smooth visual complexity (moving foliage, variable light, depth gradients) that keeps the implicit system in its Goldilocks zone, supporting parasympathetic tone and recovery.

The critical design variable for recovery environments is the *quality* of the sensory environment at the Goldilocks optimum, not the *protection* of a deliberative workspace. Daylight that tracks circadian rhythms (Beauchemin & Hays, 1998 [GS: ~600]), views of nature (Ulrich et al., 2008 [GS: ~500]), moderate acoustic environments without speech intrusions (Busch-Vishniac et al., 2005 [GS: ~500]), comfortable thermal conditions (Hwang & Jeon, 2020) — all of these are implicit-regime optimizations that support the body's prediction-driven healing processes.

**The ICU problem: both regimes fail simultaneously.** Intensive care units are among the worst environments in the built world for both regimes. For patients, the implicit regime is assaulted by a sensory environment that is simultaneously understimulating (no nature, no daylight, no spatial depth, identical ceiling tiles in every direction) and overstimulating in the worst possible way (unpredictable alarm sounds, sudden bright lights, irregular intrusions by unfamiliar personnel). The PE variance is extreme — long stretches of sensory monotony punctuated by jarring, unpredictable events — which is the precise opposite of what either regime requires. The clinical consequence is ICU delirium, now understood as affecting 60-80% of mechanically ventilated patients (Ely et al., 2001 [GS: ~3,000]), and reframed in the two-regime framework as a predictive processing catastrophe: the brain's generative models degrade under conditions that provide neither the stable moderate complexity the implicit system needs nor the temporal predictability the explicit system requires for coherent reality monitoring.

For clinical staff, the ICU presents the complementary problem: nurses and physicians must perform sustained deliberative reasoning (medication calculations, multi-system monitoring, procedure planning) in an environment engineered to maximize PE variance through constant alarms, many of which are false positives. Cvach (2012 [GS: ~500]) documented "alarm fatigue" — the progressive desensitization to clinical alarms — which in the two-regime framework represents the explicit system's defensive strategy when PE variance is uncontrollable: the system down-weights precision on the alarm channel globally, because it cannot selectively suppress only false alarms. The tragic consequence is that true alarms are missed because the environment made it impossible to maintain appropriate precision allocation.

### 4.4 Schools: Lecture, Seminar, Study, and the Developmental Dimension

Educational environments are particularly interesting for the two-regime framework because different pedagogical modes place radically different demands on the implicit and explicit systems, and because developing brains may have different regime parameters than adult brains.

**Lecture halls: the implicit regime carries the cognitive load.** In a well-delivered lecture, the student's explicit processing is relatively disengaged — the student is *receiving* a structured information stream, not *constructing* one. The Goldilocks principle applies straightforwardly: the lecturer's task is to deliver material at a rate that provides moderate PE (not so familiar as to be boring, not so novel as to be incomprehensible), and the environment should support sustained implicit engagement. The empirical literature on classroom design confirms this: daylight improves academic performance (Heschong, 1999 [GS: ~400]; Nicklas & Bailey, 1996), thermal comfort reduces cognitive load (Wargocki & Wyon, 2007 [GS: ~300]), and moderate visual complexity in the classroom supports attention without distraction (Barrett, Zhang, Moffat, & Kobbacy, 2013 [GS: ~400]).

However, the two-regime framework adds an important nuance: even in lectures, the *best* students are engaged in explicit processing — they are evaluating the argument, comparing it to prior knowledge, generating questions, constructing novel connections. For these students, PE variance matters: a lecture hall with unpredictable acoustic intrusions (corridor noise, HVAC cycling, phones) selectively impairs the most valuable cognitive activity. The design implication is that lecture halls need not be sensorily impoverished (moderate visual richness is beneficial) but must be *acoustically predictable* — well-isolated from variable external noise, with uniform sound distribution and minimal reverberation that could distort the speech signal.

**Seminar rooms: the explicit regime is primary.** In a seminar, students are expected to construct and evaluate arguments in real time — quintessentially explicit processing. The environmental requirements shift accordingly. The critical variable is no longer mean PE across sensory channels but the protection of the deliberative workspace. Small group size reduces unpredictable social stimulation; circular or U-shaped seating provides stable visual access to all participants (reducing orienting responses to speakers at unexpected locations); acoustic isolation prevents the kind of variable intrusions that would collapse a developing line of argument.

The two-regime framework predicts that seminar rooms should have *more* visual richness than conventional design assumes (to keep the implicit system in its Goldilocks zone during the inevitable pauses and transitions in discussion) but *less* acoustic and social unpredictability than open-plan classrooms. The increasing trend toward "flexible" learning spaces with moveable walls and open boundaries may inadvertently optimize the implicit regime (spatial variety, social visibility) at the expense of the explicit regime (acoustic bleeding, visual interruptions from adjacent groups).

**Individual study: the variance problem is paramount.** The library reading room is perhaps the oldest architectural solution to the explicit-regime problem. Its design features — acoustic isolation, visual monotony at the periphery combined with the richly structured text at the fovea, prohibition against conversation, social norms against disruption — constitute a systematic minimization of PE variance on all non-task channels. The two-regime framework explains why libraries *work* for deep study: the implicit system receives enough stimulation to avoid boredom (spatial grandeur, natural light, the presence of other people engaged in similar activity) while the explicit system receives maximal protection (predictable silence, no sudden changes, strong social norms against interruption).

The contemporary displacement of library study by café study is an interesting test case. Students report that cafés are "better for studying" than libraries, which superficially contradicts the explicit-regime analysis. But the two-regime framework resolves this: café noise, when it consists of steady-state conversation babble (unintelligible, therefore not semantically processed), functions as acoustic masking — it *reduces* PE variance by covering up the discrete, unpredictable sounds (door closings, footsteps, coughs) that would trigger phasic orienting responses. The café is better than a quiet library that is punctuated by coughs and whispers precisely because steady-state babble has lower PE variance than intermittent quiet-puncturing sounds. This is consistent with Mehta et al.'s (2012) finding and with the commercial success of "café noise" applications among knowledge workers.

**The developmental dimension.** Children's brains are calibrated differently from adult brains in ways that may shift the implicit/explicit balance. Younger children have less developed prefrontal cortex and weaker cognitive control (Diamond, 2013 [GS: ~4,500]), which suggests that their explicit regime is less robust and more vulnerable to interruption. At the same time, children's implicit systems may have wider Goldilocks zones — they tolerate (and indeed seek) higher levels of environmental complexity than adults, consistent with the idea that developing brains are in a higher-exploration mode with different LC-NE gain parameters (Gopnik, 2020 [GS: ~200]).

The design implication is that environments for younger children should provide *more* sensory richness (wider Goldilocks zone, more implicit exploration) with *more* interruption protection for explicit tasks (because the explicit system is more fragile). This is the opposite of what many schools provide: visually overwhelming classrooms covered in competing displays (Fisher, Godwin, & Seltman, 2014 [GS: ~300], showed that heavily decorated classrooms reduced learning by increasing off-task behavior) combined with constant acoustic interruptions from adjacent classrooms, PA systems, and corridor traffic. The decorated classroom problem is specifically an implicit-regime failure: the decorations push visual complexity beyond the Goldilocks zone, and the developmental literature confirms that children's implicit systems are more easily captured by high-complexity environmental stimulation than adults' (Hanley et al., 2017).

### 4.5 Research Environments: The Study, the Library, the Lab, and the Hallway

The academic research environment is the setting in which the two-regime problem is most acute, because the core activity — generating novel theoretical understanding — involves the most demanding forms of explicit cognition (model construction, cross-domain analogy, compositional hypothesis generation) sustained over the longest timescales.

**The private study.** Virginia Woolf's "room of one's own" is, in the two-regime framework, a room that protects the explicit regime. The private study provides maximal PE variance control: a closed door, acoustic isolation, a stable visual environment arranged by the occupant, no uncontrolled social intrusions. Importantly, the best studies also serve the implicit regime: a window view (moderate visual complexity, temporal smoothness of natural light and vegetation), bookshelves (high visual complexity but completely stable and under the occupant's control), and personal artifacts (familiar objects that generate near-zero PE while providing a rich predictive context). The private study is the architectural solution to the two-regime problem for individual deep work, and its progressive elimination from academic buildings in favor of open-plan offices represents, in theoretical terms, the systematic destruction of the explicit-regime support infrastructure for knowledge production.

**The laboratory.** Research laboratories present a different two-regime profile. Experimental work involves extended sequences of procedural execution (explicit regime: following protocols, monitoring for deviations, making real-time decisions about parameter adjustments) embedded in an environment that must also support opportunistic observation (implicit regime: noticing unexpected patterns, registering anomalous results that don't match predictions). The best-designed labs provide visual access to ongoing experiments (implicit Goldilocks: moderate complexity, mildly surprising outcomes) with acoustic and social predictability (explicit protection: steady-state equipment noise, controlled access, clear protocols for when interruption is acceptable).

**The hallway and the "creative collision."** The contemporary architectural emphasis on "creative collisions" — chance encounters in hallways, stairwells, and open spaces that spark new ideas — is, in the two-regime framework, an optimization of the implicit regime for social information processing. Chance encounters provide moderately surprising social stimulation (unexpected juxtaposition of people from different domains), and the Goldilocks principle predicts that such encounters will be maximally informative when they are neither too predictable (same people every day) nor too surprising (strangers with no shared context).

But the two-regime framework adds a crucial caveat: creative collisions are only valuable if participants have *already* done the explicit-regime work of developing theoretical structures that can be juxtaposed and recombined. An encounter between two researchers who have each spent the morning in deep thought about their respective problems may produce genuine insight through novel combination. An encounter between two researchers who have spent the morning in an open-plan office fielding emails and attending to peripheral social stimulation is unlikely to produce anything beyond pleasantries, because neither has built the deliberative structures that make creative combination possible. **The creative collision literature mistakes the recombination event for the entire creative process.** The two-regime framework predicts that buildings optimized for creative collisions at the expense of deep-work spaces will produce *less* creative output than buildings that provide both, because the explicit-regime work is the rate-limiting step.

Allen's (1977 [GS: ~4,000]) classic finding that communication probability drops off sharply with physical distance is often cited in support of open-plan and "collision-optimizing" design. But Allen was studying information *transfer*, not idea *generation*. The two-regime framework distinguishes these: information transfer is primarily an implicit-regime process (recognizing relevant patterns in others' communications), while idea generation requires explicit-regime model construction. Optimizing the building for information transfer without protecting spaces for idea generation is like optimizing a kitchen for ingredient delivery while eliminating the stove.

### 4.6 Temporal Design: Supporting Regime-Switching Across the Workday

The two-regime framework has implications not just for the *spatial* organization of buildings but for their *temporal* behavior. Most cognitive work involves alternation between implicit and explicit modes — periods of exploration, conversation, and intake (implicit) punctuated by periods of focused analysis, writing, and deliberation (explicit). The building that supports this alternation is one whose environmental characteristics can shift in ways that support the active regime.

**Circadian alignment.** Natural light varies systematically across the day in ways that may align with regime-switching. Morning light (high color temperature, strong blue content) promotes alertness and cortical arousal through melanopsin-mediated pathways (Berson, Dunn, & Takao, 2002 [GS: ~2,500]), supporting the implicit regime's need for well-calibrated arousal. The post-lunch circadian dip (typically 13:00-15:00) is the period when explicit processing is most vulnerable, and environmental design that compensates — higher-intensity lighting, cooler temperatures, reduced acoustic intrusion during this window — may protect the explicit regime during its period of greatest fragility. Late-afternoon light (warmer color temperature, longer shadows, increased visual complexity from low sun angles) naturally supports a return to implicit-mode exploration and social engagement.

**Acoustic temporal design.** The most sophisticated acoustic environments are those that provide different profiles at different times. Research libraries have long practiced informal temporal design through social norms (quiet periods, group-study periods). The two-regime framework suggests that these norms reflect a genuine computational requirement and could be supported architecturally through adaptive acoustic systems — masking noise that varies in character across the day, operable acoustic boundaries that can reconfigure spaces from open to enclosed, and scheduling systems that coordinate quiet periods across adjacent spaces to prevent acoustic bleeding during protected explicit-regime periods.

**The problem of the workday transition.** The transition from explicit to implicit mode is relatively easy — the explicit system simply releases its precision allocation, and the implicit system resumes its default Goldilocks-seeking behavior. The transition from implicit to explicit mode is much harder: the explicit system must recruit prefrontal resources, establish working memory representations, build the initial structure of a deliberative inference, and suppress competing implicit-mode processes. This transition takes 10-23 minutes (Mark, Gudith, & Klocke, 2008 [GS: ~500]; Mark, Gonzalez, & Harris, 2005 [GS: ~1,500]), during which the system is maximally vulnerable to interruption because the deliberative structure is still fragile and incompletely established.

The architectural implication is that the *transition* between collaborative and focused spaces should be designed as a *gradient* rather than a threshold — a spatial sequence that progressively reduces PE variance over several minutes, allowing the explicit system to build up gradually rather than switching abruptly from high-stimulation to low-stimulation environments. Some traditional architectural sequences do this inadvertently: the progression from a building's public lobby through increasingly private corridors to a private office provides exactly this gradient of decreasing social and sensory PE variance.

### 4.7 The Role of Personal Control: Agency as Dual-Regime Support

Personal environmental control — the ability to open a window, adjust lighting, control temperature, close a door, rearrange furniture — has a unique status in the two-regime framework because it serves both regimes simultaneously through different mechanisms.

**For the implicit regime, control enables active inference.** In the PP framework, active inference is the mechanism by which the agent changes the world to match its predictions rather than changing its predictions to match the world (Friston, 2010). Operable environmental controls extend active inference into the built environment: the occupant can adjust sensory channels to maintain their individual Goldilocks optimum. Since Goldilocks zones vary across individuals (neuroticism, sensory processing sensitivity, cultural calibration — see the India fieldwork discussion in the Goldilocks article), personal control is the architectural mechanism that accommodates individual variation without requiring the architect to know each occupant's parameters.

**For the explicit regime, control minimizes PE variance by making the environment predictable.** When an occupant controls their own lighting, temperature, and acoustic environment, the environmental statistics become *self-generated predictions*. A noise that you caused is maximally predictable; a noise imposed by the building or a neighbor is maximally unpredictable. The PE variance associated with self-generated environmental changes approaches zero, while the PE variance associated with externally imposed changes is maximal. This is why the sense of control matters even when the actual environmental conditions are identical: Langer and Rodin's (1976 [GS: ~3,500]) classic finding that perceived control improves health outcomes in nursing homes is, in the two-regime framework, partly an explicit-regime effect — the residents whose environment was predictable (because they controlled it) could allocate more precision to deliberative processing and reality monitoring, while those whose environment was externally determined had to maintain higher precision reserves for environmental monitoring.

The empirical literature on environmental control and productivity is extensive and consistent: perceived control over temperature (Wyon, 1996), lighting (Newsham et al., 2009 [GS: ~200]), ventilation (Brager & de Dear, 1998 [GS: ~1,000]), and acoustic conditions (Leather, Pyrgas, Beale, & Lawrence, 1998 [GS: ~300]) all predict higher satisfaction and productivity, often independently of the actual environmental conditions. The two-regime framework provides a unified explanation: control simultaneously optimizes the implicit regime (individual Goldilocks calibration) and protects the explicit regime (self-generated environmental changes have near-zero PE variance).

**The open-plan control catastrophe.** Open-plan offices eliminate personal environmental control almost entirely. Temperature, lighting, and acoustic conditions are determined by building systems and by the collective behavior of co-occupants, neither of which is under individual control. The occupant cannot close a door, adjust airflow, or modulate lighting without affecting neighbors. In the two-regime framework, this represents a simultaneous failure of both implicit-regime optimization (one-size-fits-all conditions miss every individual's Goldilocks zone) and explicit-regime protection (environmental changes are externally imposed and therefore maximally unpredictable). The resulting behavioral adaptations — headphones, screen barriers, "do not disturb" signals — are occupant-improvised control mechanisms that partially restore what the architecture removed.

### 4.8 Summary: The Two-Regime Design Matrix

The two-regime framework generates a structured approach to environmental design evaluation. For any given space, the designer can assess:

**Implicit-regime support**: Does the environment provide moderate PE across sensory channels? Is the mean complexity level in the Goldilocks zone for the intended occupants and activities? Are there sufficient biophilic elements, spatial variety, and natural light to sustain implicit-system engagement? Is the multi-channel balance appropriate (cross-modal compensation: quieter spaces need more visual complexity; visually stimulating spaces need less acoustic input)?

**Explicit-regime protection**: Is PE variance minimized on non-task channels? Are acoustic intrusions predictable or suppressible? Is the space protected from unpredictable social interruptions? Can the occupant sustain a deliberative line of reasoning for 20+ minutes without forced attentional reallocation? Does the temporal profile of environmental change support rather than disrupt extended cognitive work?

**Regime-switching support**: Does the building provide a gradient of spaces supporting different positions on the implicit-explicit continuum? Can occupants move between collaborative and focused modes with appropriate environmental transitions? Do spatial sequences provide progressive PE-variance reduction for the implicit-to-explicit transition? Are temporal patterns (circadian, workday, weekly) aligned with expected regime-switching patterns?

**Personal control**: Can occupants adjust their individual environment to calibrate both the PE mean (implicit Goldilocks optimization) and PE variance (explicit interruption protection)? Are control mechanisms intuitive and low-cost (not requiring complex interfaces or social negotiation)?

This matrix constitutes a practical design evaluation tool derived from the theoretical framework. Its predictions are specific and testable: for instance, that a room with moderate mean PE and low PE variance will outperform a room with optimal mean PE and high variance for any task requiring sustained deliberation, and that the magnitude of this effect will increase with task complexity and the duration of required sustained attention.

---

## APPENDIX A: TOWARD A THEORY OF EXPLICIT COGNITION DISTINCT FROM PP

### A.1 PP as a Theory of Implicit Attention Control

The first step in diagnosing the gap in PP is to state precisely what "attention" means in the PP framework and to recognize that it covers only one of two fundamentally different attentional operations.

**What PP means by attention.** In the PP framework, attention is precision-weighting: the gain modulation of prediction error signals at various levels of the cortical hierarchy (Feldman & Friston, 2010 [GS: ~1,200]; Hohwy, 2012 [GS: ~1,000]). When precision is increased on a particular channel, PE signals on that channel have greater influence on the inferential process — they carry more evidential weight for updating generative models. When precision is decreased, PE signals are attenuated — treated as noise rather than signal. This is computationally elegant. It unifies attention (which errors matter), learning (how models update), and sensory attenuation (why self-generated signals are muted) under a single formalism.

Crucially, this precision-weighting is computed, not chosen. The system adjusts precision based on the estimated reliability of different sensory channels given the current context, following the mathematical logic of Bayesian inference under heteroscedastic noise (i.e., noise whose variance changes across observations). A loud noise in a quiet room receives high precision because the auditory channel has been operating with low variance — any sudden PE is treated as signal. The same acoustic event in a noisy environment receives lower precision because the channel's baseline variance is high. None of this requires anyone to *decide* to attend to the noise; the precision adjustment is a consequence of the system's ongoing inference about channel reliability.

This is implicit attention control: the system automatically adjusts what it "cares about" based on the statistical structure of the incoming signal, without any representation of goals, strategies, or deliberate choices about what to attend to. It handles a remarkably wide range of attentional phenomena — involuntary capture, contextual modulation, sensory attenuation during action, even some forms of selective attention in predictable environments.

**What implicit attention control means computationally.** In formal terms, implicit attention is the optimization of a diagonal precision matrix Π in the generative model's likelihood function: p(data | causes) = N(g(causes), Π⁻¹), where Π is updated as a function of the recent prediction error history on each channel. The system adjusts Π to maximize model evidence (minimize free energy). This is a second-order inference problem — inferring the reliability of one's own sensory channels — but it remains an automatic optimization, not a deliberate act. The precision adjustments are continuous, preconscious, and driven by the statistical properties of the PE signal rather than by any representation of "what I want to attend to."

### A.2 PP as a Theory of Implicit PE Measurement

The same automatic, subpersonal character applies to how PE is *measured* in the PP framework. Prediction error in the standard formulation is the discrepancy between top-down predictions and bottom-up sensory signals at each level of the hierarchy: ε = x − g(v), where x is the sensory input, g(·) is the generative model's predicted input, and v is the vector of hidden causes. This measurement is continuous, automatic, and distributed across the entire cortical hierarchy. Nobody decides to compute PE; it emerges as a consequence of the architecture.

**What implicit PE measurement means computationally.** The system registers mismatches at every level simultaneously — from retinal ganglion cells computing contrast deviations to prefrontal regions computing violations of abstract expectations. At each level, PE is the *residual* that the current model fails to explain, and it propagates upward to drive model revision. This is implicit in three senses: (a) it is not represented as "I notice a discrepancy" but computed as a numerical residual in a hierarchical inference, (b) it occurs in parallel across all sensory channels without any selection of which mismatches to care about (selection happens downstream via precision-weighting), and (c) it is not available to consciousness in its raw form — what reaches awareness, to the extent that anything does, is the *result* of PE-driven inference (the updated percept), not the PE signal itself.

The distinction between implicit PE measurement and explicit PE measurement is critical for what follows. In implicit mode, PE is a signal *used by* the system; in explicit mode, PE becomes something *known to* the system — a representational content that can be reflected upon, compared, discussed, and strategically deployed.

### A.3 Why PP Cannot Currently Account for Explicit Attention and Explicit PE

The problem emerges when we consider what happens during deliberate cognitive activity — the kind of processing that characterizes sustained analytical thought, creative problem-solving, or any situation in which the thinker is consciously aware of entertaining hypotheses and evaluating evidence.

**The explicit attention problem.** When a researcher deliberately chooses to attend to the logical structure of an argument rather than its rhetorical force, or when a clinician deliberately focuses on differential diagnosis rather than the patient's emotional presentation, something happens that is qualitatively different from precision-weighting. The agent forms a *representation of what to attend to* — a goal-directed specification of which aspects of the stimulus to privilege — and then implements that specification through top-down control. Clark (2017) acknowledges this and proposes that deliberate attention is just precision-weighting from very high-level predictions. But this merely relocates the problem: where do those high-level predictions come from? If the answer is "from even higher-level predictions," we have an infinite regress. If the answer is "from goals and intentions," we have left the PP framework for something that requires a theory of goal representation, maintenance, and strategic deployment — which PP does not provide.

The computational difference is stark. Implicit attention adjusts gain on channels based on estimated channel reliability (a function of recent PE statistics). Explicit attention selects channels based on task-relevant criteria (a function of goals, plans, and strategic considerations that are *represented* at a personal level). The first is an optimization over a well-defined cost function; the second is an implementation of a *selected* cost function, where the selection itself requires explanation.

**The explicit PE problem.** In deliberate cognition, the thinker is aware of prediction errors — not as raw residuals but as propositional content: "this result contradicts my hypothesis," "this argument doesn't follow from the premises," "this building feels wrong for what it's supposed to do." The thinker can represent the PE, reflect on it, compare it to PEs from other domains, and decide how much weight to give it. This is explicit PE measurement: PE becomes a cognitive object rather than a computational signal.

PP has no account of how this happens. The formal machinery produces PE as a vector of residuals at each hierarchical level, but the transition from "residual in a computational architecture" to "propositional content available for deliberate evaluation" is precisely the hard problem that PP shares with every other computational theory of mind. The problem is not merely phenomenological (though it is that); it is functional. Explicit PE measurement changes what the system can *do*: it can compare PEs across domains, reason about the significance of a mismatch, decide whether to revise the model or reject the data, and communicate the PE to other agents through language. None of these operations is available at the implicit level.

**The homunculus returns.** PP was designed to eliminate the homunculus — to explain intelligent behavior without appealing to a little person inside the head making decisions. For implicit processing, it succeeds brilliantly. But for explicit processing, the homunculus returns in a more sophisticated guise. When Clark proposes that deliberate attention is "precision-weighting from high-level predictions," the high-level predictions must include representations of goals ("I want to understand the causal structure"), strategies ("I should look at the control condition first"), and metacognitive assessments ("my current model doesn't fit the data well enough"). These representations are not explained by PP — they are the inputs to PP from a system that PP doesn't describe. Either PP is incomplete (it handles the implicit but not the explicit), or PP is the whole story and explicit cognition is an illusion (a position that no serious cognitive scientist endorses, and that is empirically untenable given the massive neuroimaging, neuropsychological, and behavioral evidence for qualitatively distinct controlled processing).

### A.4 A Positive Theory of Explicit Cognition as a Distinct Computational Regime

What follows is an attempt to characterize explicit cognition as a distinct computational regime that operates *in coordination with* but *not reducible to* the implicit PP machinery. This draws on Global Workspace Theory (Baars, 1988; Dehaene & Naccache, 2001), Adaptive Gain Theory (Aston-Jones & Cohen, 2005), prefrontal cognitive control theory (Miller & Cohen, 2001), and the emerging literature on prefrontal-basal ganglia gating (Frank & Badre, 2012).

**A.4.1 The Workspace Architecture.** The core proposal is that explicit cognition operates through a *workspace* — a capacity-limited, serially organized representational medium that makes selected information globally available to multiple processing systems simultaneously. This is Baars' (1988) global workspace, formalized by Dehaene and colleagues as the "global neuronal workspace" (Dehaene, Kerszberg, & Changeux, 1998 [GS: ~2,000]; Dehaene & Naccache, 2001), and implemented primarily through long-range frontoparietal connectivity with prefrontal cortex as the critical hub.

The workspace has several properties that distinguish it from implicit PP:

*Serial bottleneck.* The workspace processes one coherent representation at a time (or at most a small number). This is the source of the capacity limitation of conscious cognition and the seriality of deliberate thought. It is not a design flaw but a feature: global availability to all processing systems requires a single coherent state, and maintaining multiple globally-broadcast states simultaneously would create interference (Baars, 1988; Dehaene & Naccache, 2001).

*Compositional structure.* Workspace representations are not fixed patterns but compositionally assembled structures — novel combinations of elements bound by variable-binding operations (Fodor & Pylyshyn, 1988 [GS: ~6,000]; Marcus, 2001 [GS: ~2,000]). "The temperature in this room is causing my concentration to deteriorate" is not a stored pattern but a composed representation that combines perceptual content (temperature), self-referential content (concentration), causal structure (causing), and temporal dynamics (deteriorating). PP can handle pattern matching; it does not provide a natural account of novel compositional binding.

*Goal-directed control.* The workspace is controlled by a goal-maintenance system, primarily instantiated in dorsolateral prefrontal cortex (Miller & Cohen, 2001), which determines what information enters the workspace, how long it persists, and when it is updated. This system operates through *gating* — selectively opening and closing the workspace to new information (Frank & Badre, 2012; O'Reilly & Frank, 2006 [GS: ~1,500]). Gating is the computational operation that implements deliberate attention: the decision to attend to logical structure rather than rhetorical force is a gating operation that admits the former and excludes the latter from the workspace.

*Metacognitive access.* The workspace provides a level of representation at which the system's own processing states become available as cognitive objects. This is what makes explicit PE possible: when a prediction error at any level of the PP hierarchy is "broadcast" into the workspace, it ceases to be merely a computational residual and becomes a representable, reflectable-upon content — "I notice that my prediction was wrong." This is not a mysterious emergence; it is a consequence of the workspace architecture's function of making local processing states globally available.

**A.4.2 The Two-Regime Computational Architecture.** The relationship between implicit PP and explicit workspace cognition is not sequential (first implicit, then explicit) but concurrent and interactive:

*Implicit PP operates continuously* — generating predictions, computing PE, adjusting precision, driving active inference. It never stops, even during explicit cognition. The implicit system provides the perceptual world within which explicit cognition operates.

*The workspace samples selectively from PP* — selecting which PE signals to promote to workspace representation, which models to hold up for explicit evaluation, which precision assignments to override with deliberate attention. The workspace is a consumer and controller of PP, not a replacement for it.

*Workspace operations feed back into PP* — when the workspace generates a novel hypothesis (through compositional binding), this hypothesis is "installed" in the PP hierarchy as a new prior, which then generates new predictions and produces new PE. The explicit system proposes; the implicit system tests. This is the cycle that constitutes deliberate inquiry.

*The two regimes have different resource requirements.* Implicit PP is parallel, high-capacity, energy-efficient, and tolerant of moderate environmental perturbation. Workspace cognition is serial, capacity-limited, energy-expensive (the prefrontal cortex is metabolically among the most costly brain regions — Lennie, 2003 [GS: ~1,500]), and exquisitely vulnerable to interruption because its representations must be actively maintained against decay and interference.

**A.4.3 The LC-NE System as Regime Switch.** The locus coeruleus-norepinephrine system provides the neurochemical mechanism for switching between regimes (Aston-Jones & Cohen, 2005). In tonic mode (moderate, steady NE release), the LC-NE system supports focused, exploitation-oriented processing — the explicit regime's operating conditions. In phasic mode (burst firing to salient events), the system resets precision allocation across the cortex, interrupting ongoing processing and promoting exploratory, implicit-mode engagement with the environment.

The architectural implication is direct: environmental events that trigger phasic LC-NE bursts (sudden sounds, unexpected movements, social intrusions) don't merely distract — they *switch the computational regime* from explicit to implicit. This is why PE variance, not PE mean, is the critical variable for explicit processing. Each high-variance PE event triggers a phasic burst that collapses the workspace's maintained representations and forces a regime switch. The cost is not the duration of the distraction but the time required to *rebuild* the workspace state after the regime switch — to re-enter the explicit mode, reconstruct the compositional representation, and resume the deliberative inference.

### A.5 A Theory of Interruption of Explicit Cognition

The two-regime framework yields a detailed account of interruption that goes beyond the general observation that "interruptions hurt concentration." Different types of interruption have different costs because they disrupt different components of the workspace architecture.

**A.5.1 Taxonomy of Interruption Types**

*Type 1: Phasic environmental intrusion.* A sudden loud sound, an unexpected movement in the visual periphery, a door opening. These trigger phasic LC-NE bursts that reset cortical precision allocation. The workspace does not merely pause — it is actively dismantled by the phasic norepinephrine surge, which promotes a global state of exploratory, implicit-mode processing incompatible with the focused state required for workspace maintenance.

Computational mechanism: Phasic NE release increases the gain on bottom-up sensory signals globally (Berridge & Waterhouse, 2003 [GS: ~1,500]), overwhelming the top-down precision assignments that were maintaining the workspace state. The maintained representation literally loses its competitive advantage over incoming sensory information.

Recovery dynamics: 10-23 minutes to full resumption of pre-interruption explicit processing (Mark et al., 2008; Mark et al., 2005), but the duration varies as a function of the complexity of the workspace representation that was disrupted. Rebuilding a simple working memory representation (e.g., "where was I in this paragraph") takes seconds; rebuilding a complex compositional structure (e.g., "I was evaluating whether the third assumption in Smith's argument entails the conclusion given the counterexample I generated from the Jones data") may take many minutes or may fail entirely if the intermediate inferential steps cannot be reconstructed.

*Type 2: Semantic intrusion.* Overheard speech, especially unpredictable content-bearing speech, is a distinct and particularly destructive type of interruption. It does not merely trigger a phasic orienting response; it actively inserts *competing compositional content* into the workspace. Because language processing is obligatory through at least the level of semantic access (Bregman, 1990), overheard speech creates workspace representations that compete directly with the maintained deliberative content for the same serial-processing bottleneck.

Computational mechanism: Obligatory semantic processing of speech activates workspace-compatible representations (Dehaene et al., 2006 [GS: ~1,000]) that compete with the goal-maintained representations. The workspace cannot maintain two unrelated compositional structures simultaneously, so the intruding content either displaces the maintained content or creates interference that degrades both.

Recovery dynamics: Worse than Type 1 because the intruding content is compositionally structured and may create associative interference with the maintained content. The classic finding that irrelevant speech impairs serial recall even when participants know to ignore it (Jones & Macken, 1993; Colle & Welsh, 1976) reflects this workspace-level competition.

*Type 3: Social interruption.* A colleague approaching, a question, a request for attention. This is the most complex type because it engages not just the perceptual systems (Type 1) and language system (Type 2) but also the social-cognitive system — theory of mind, pragmatic inference, social obligation assessment. The processing demand is enormous: the system must simultaneously (a) parse the social meaning of the approach, (b) assess the urgency and social cost of ignoring it, (c) maintain the current workspace content, and (d) generate an appropriate response. This is a four-way demand on a serial bottleneck that can handle one or two.

Computational mechanism: Social stimuli receive mandatory high precision-weighting because the social-cognitive system treats conspecific behavior as inherently unpredictable and consequential (Frith & Frith, 2006 [GS: ~4,000]). The precision assignment cannot be voluntarily reduced without social cost, creating a forced workspace switch.

Recovery dynamics: Worst of all three types, because the social interaction often generates new workspace content (a request, a piece of information, an emotional response) that persists after the interruption ends, competing with the original deliberative content for workspace access. Gonzalez and Mark (2004 [GS: ~300]) found that people do not return to an interrupted task for an average of 25 minutes after a social interruption, in part because the social content generates its own follow-on processing demands.

**A.5.2 The Interruption-Complexity Function**

The central prediction of this theory is that the *cost* of an interruption is a function of the *complexity* of the workspace representation that is disrupted, not a function of the duration or intensity of the interrupting event. A three-second door slam that collapses a complex inferential structure is more costly than a thirty-second conversation that interrupts routine email processing, because the workspace representation in the first case is compositionally complex and difficult to reconstruct, while in the second case it is simple and easily resumed.

This predicts an interaction between task type and interruption sensitivity that has been confirmed empirically: Speier, Valacich, and Vessey (1999 [GS: ~700]) found that interruptions impaired complex task performance more than simple task performance, and Monk et al. (2008) found that interruption cost increased with the complexity of the interrupted task. In the two-regime framework, this is because complex tasks are those that build the most elaborate workspace representations, and it is the workspace representation — not the attention or the arousal — that is the casualty of interruption.

**A.5.3 The Fragility Curve**

Workspace representations are not uniformly fragile throughout their construction. There is a characteristic fragility curve:

*Phase 1: Construction (0-5 minutes).* The workspace is being populated. Relevant information is being retrieved from long-term memory, organized into a compositional structure, and evaluated for coherence. The representation is maximally fragile because it is incomplete — an interruption at this phase means the entire construction process must restart.

*Phase 2: Elaboration (5-15 minutes).* The core structure is established and is being refined, extended, and evaluated. The representation is moderately fragile — an interruption may damage peripheral elements while leaving the core intact, allowing partial recovery.

*Phase 3: Consolidation (15+ minutes).* The representation has stabilized and may begin to be encoded into long-term memory formats. Fragility decreases because the representation has redundant support from multiple memory systems. An interruption at this phase may cause a pause without total collapse.

*Phase 4: Fluent operation (variable onset).* For highly practiced explicit tasks, the workspace operation becomes partially automatized — the implicit system takes over some of the maintenance burden. This is the "flow" state (Csikszentmihalyi, 1990 [GS: ~25,000]), and it represents a partial convergence of the two regimes: explicit-level processing with implicit-level stability. Interruption sensitivity decreases further because the representation has deep support from automated subroutines.

The architectural implication is that *uninterrupted time* is a non-linear resource: the first 5 minutes of uninterrupted work are disproportionately valuable (they determine whether the workspace gets populated at all), and the value of additional uninterrupted time follows a roughly logarithmic function — each additional minute is valuable but less so than the previous one, until the consolidation phase is reached and the representation becomes self-sustaining.

### A.6 Templates and Architectural Consequences

The theory of explicit cognition generates a set of mechanistic templates in the Article Eater format — testable claims about how specific architectural features affect specific cognitive processes through identified mechanisms.

**Template EC-1: Acoustic Predictability and Workspace Maintenance**

*Mechanism*: Unpredictable acoustic events trigger phasic LC-NE bursts → global precision reset → workspace collapse → forced regime switch from explicit to implicit.

*Prediction*: Environments with lower acoustic PE variance support longer continuous bouts of explicit processing, even if their mean acoustic level is higher than quieter but more variable environments.

*Architectural consequence*: Design for steady-state acoustic environments. Continuous masking sound (natural soundscapes, calibrated noise) is preferable to intermittent quiet. If quiet is achievable, it must be *reliably* quiet — a quiet room with occasional acoustic intrusions is worse than a moderately noisy room with consistent sound.

*Supporting evidence*: Mehta et al. (2012); Roper & Juneja (2018 [GS: ~50]); Haapakangas et al. (2011 [GS: ~200]).

**Template EC-2: Visual Periphery Stability and Explicit Processing Duration**

*Mechanism*: Movement in the visual periphery triggers involuntary saccades via superior colliculus → orienting response → phasic precision reallocation → workspace disruption.

*Prediction*: Environments where the visual periphery is stable (no unpredictable movement) support longer explicit processing bouts than environments with peripheral visual change, independent of central visual complexity.

*Architectural consequence*: For deep-work spaces, control peripheral visual change. Solid walls or translucent (not transparent) partitions. Position workstations so that circulation paths are not in peripheral vision. If windows are present, ensure the view provides smooth temporal change (foliage, clouds) rather than discrete events (pedestrians, vehicles).

*Supporting evidence*: Fisher et al. (2014); Theeuwes (1991 [GS: ~2,500]); Bernstein & Turban (2018).

**Template EC-3: Social Predictability and Workspace Protection**

*Mechanism*: Unpredictable social approach triggers high-precision social-cognitive processing → mandatory workspace engagement → displacement of maintained deliberative content.

*Prediction*: Environments where social interruption is either physically prevented or socially regulated support longer explicit processing bouts. The critical variable is not social *density* but social *predictability* — a space with many people following predictable patterns (a library) may be less disruptive than a space with few people following unpredictable patterns (a shared office with irregular colleagues).

*Architectural consequence*: Provide legible social protocols through spatial design. Thresholds, doors, and gradients of publicness communicate interruptibility. Spaces without such signals (open plans, benching) force occupants to improvise social protocols (headphones as "do not disturb" signals), which are less reliable and require ongoing cognitive maintenance — itself a tax on the explicit regime.

**Template EC-4: The Construction Phase Protection Principle**

*Mechanism*: Workspace representations are maximally fragile during the first 5 minutes of construction. Any interruption during this phase forces complete restart. Each restart has a compounding cost because failed construction attempts may generate interference.

*Prediction*: The first 5 minutes after a person begins focused work are disproportionately critical. An environment that provides even brief reliable protection during this phase will support more total explicit processing than an environment that provides longer but unreliable protection.

*Architectural consequence*: Explicit-regime spaces should provide *guaranteed* minimum uninterrupted periods. This requires not just acoustic and visual isolation but social-protocol support: doors that signal "do not disturb," scheduling systems that reserve spaces for minimum 30-minute blocks, and cultural norms that respect the construction phase. The transition sequence from collaborative to focused space (discussed in Section 4.6) should be designed to support the construction phase by providing a gradient of decreasing PE variance.

**Template EC-5: The Regime-Switch Gradient**

*Mechanism*: Transition from implicit to explicit mode requires recruitment of prefrontal resources, suppression of competing implicit-mode processes, and construction of an initial workspace representation. This transition is effortful, takes 10-23 minutes, and is itself vulnerable to interruption.

*Prediction*: Environments that support a gradual transition — progressively decreasing PE variance over space or time — will produce faster and more successful explicit-mode entry than environments that require abrupt transitions.

*Architectural consequence*: Design spatial sequences from collaborative zones to focused zones as gradients, not thresholds. A progression from open collaboration space → semi-enclosed transition space (library tables, study carrels) → fully enclosed private space mirrors the temporal dynamics of regime switching and allows the workspace construction phase to begin during the spatial transition.

**Template EC-6: Personal Control as Variance Reduction**

*Mechanism*: Self-generated environmental changes produce near-zero PE (because they are predicted by the motor command that produced them — the standard sensory attenuation account in PP). Externally imposed changes produce high PE. Therefore, occupant-controlled environments have lower effective PE variance than identical environments under external control.

*Prediction*: Two physically identical environments will support different amounts of explicit processing depending on who controls the environmental parameters. Occupant control reduces effective PE variance → protects workspace → supports longer explicit processing bouts.

*Architectural consequence*: Provide intuitive, low-cost personal environmental controls in all explicit-regime spaces. The controls must be low-cost not just financially but *cognitively* — they should not themselves require workspace resources to operate. A simple operable window is better than a complex climate control interface, because the window can be operated through implicit-mode sensorimotor control while the interface demands explicit-mode engagement.

---

### Expert Panel EC-I: Explicit Cognition and Architectural Consequences

**Panel convened**: Andy Clark, Karl Friston, Earl Miller, Michael Botvinick, Stanislas Dehaene, Jonathan Cohen, David Kirsh, Lisa Feldman Barrett

**Charge**: The panel reviewed the two-regime framework (Sections 1-4) and the theory of explicit cognition (Appendix A, Sections A.1-A.6). Panelists were asked to: (1) evaluate, refine, and dispute the Tier 1 theories of explicit cognition; (2) generate Tier 2 mechanistic templates with architectural predictions; (3) identify convergences and unresolved disputes.

---

### TIER 1: THEORIES OF EXPLICIT COGNITION -- POSITIONS, DISPUTES, AND CONVERGENCES

#### T1-EC.1: Global Neuronal Workspace Theory

**Core claim**: Conscious, explicit cognition requires the "ignition" of a distributed frontoparietal network that makes local processing results globally available to multiple specialized processors simultaneously (Baars, 1988 [GS: ~4,000]; Dehaene & Naccache, 2001 [GS: ~4,500]; Dehaene et al., 1998 [GS: ~2,000]).

**Dehaene's formulation for the panel**: Explicit cognition is workspace ignition. The transition from implicit to explicit processing is not gradual but a *phase transition* -- a nonlinear jump from local, modular processing to global broadcast. The all-or-none character of ignition (Sergent & Dehaene, 2004 [GS: ~500]) explains why explicit processing is serial and capacity-limited: only one coherent pattern can occupy the global workspace at a time, because ignition is a self-reinforcing winner-take-all dynamic. The workspace is the mechanism by which PE at any level of the PP hierarchy becomes a cognitive object -- a content available for report, reasoning, and deliberate action.

**Environmental implication**: Ignition has a *threshold*. A prediction error must reach a critical magnitude (or be precision-boosted above threshold by top-down attention) to trigger workspace access. Sub-threshold PEs are processed implicitly. This means that environmental stimuli have a binary effect on explicit cognition: they either fail to trigger ignition (and are processed implicitly, in the Goldilocks framework) or they succeed in triggering ignition (and commandeer the workspace, displacing whatever was there). The architectural goal is to keep non-task environmental PE below the ignition threshold while keeping it above the boredom threshold for implicit processing.

**Clark's response**: The phase-transition model is too sharp. There are intermediate states -- partial awareness, fringe consciousness, the "tip of the tongue" -- that don't fit a binary ignition account. Moreover, the workspace model treats the environment as a source of inputs to a central processor, which is precisely the neo-Cartesian architecture that radical PP was supposed to dissolve. The environment isn't just sending signals that may or may not cross a threshold; the agent is actively sampling the environment as part of an extended predictive loop. Workspace ignition, if it exists, is better understood as a phase transition in the *whole brain-body-environment system*, not just in a cortical network.

**Panel assessment**: Strong empirical support for the basic ignition phenomenon (Dehaene et al., 2006 [GS: ~1,000]; Sergent & Dehaene, 2004 [GS: ~500]; Quiroga, Mukamel, Isham, Malach, & Fried, 2008 [GS: ~800]). The binary ignition model may be too strict for graded conscious access, but the core architectural claim -- that explicit cognition requires global broadcast through a capacity-limited frontoparietal network -- is well-supported and generates specific architectural predictions. **Confidence: HIGH** for the basic mechanism; **MODERATE** for the strict phase-transition characterization.

#### T1-EC.2: Adaptive Gain Theory (LC-NE System as Regime Switch)

**Core claim**: The locus coeruleus-norepinephrine system operates in two modes -- tonic (steady, moderate NE, supporting exploitation/focus) and phasic (burst, high NE, supporting exploration/reset) -- and the balance between these modes determines the computational regime (Aston-Jones & Cohen, 2005 [GS: ~5,000]).

**Cohen's formulation for the panel**: The LC-NE system is the mechanism that implements the implicit/explicit regime distinction at the neurochemical level. Tonic mode corresponds to the explicit regime: moderate, steady NE maintains stable gain in prefrontal cortex, supporting sustained workspace representations. Phasic mode corresponds to the implicit regime switch: bursts of NE reset cortical gain globally, collapsing maintained representations and promoting broad, exploratory processing. The critical insight for architecture is that phasic bursts are *triggered by salient environmental events* -- they are the mechanism by which the environment forces regime switching. Every unpredictable salient event is a potential regime-switch trigger.

**Miller's refinement**: The LC-NE story is correct but incomplete. Prefrontal cortex doesn't just receive NE modulation passively -- it actively regulates LC firing through descending projections (Arnsten, 2009 [GS: ~1,500]; Sara, 2009 [GS: ~800]). This means the explicit regime can *resist* phasic triggering to some degree -- the PFC can maintain its own tonic state by suppressing LC phasic responses. But this resistance is effortful, metabolically costly, and degrades over time. The environmental design question becomes: how much resistance capacity must the PFC expend on environmental suppression, and how much is left for actual cognitive work? An environment with frequent phasic triggers drains PFC resistance capacity even when the triggers are successfully suppressed.

**Barrett's addition**: Don't forget that the LC-NE system is deeply integrated with interoceptive processing and allostatic regulation (Barrett & Simmons, 2015 [GS: ~700]). Thermal discomfort, hunger, sleep pressure, and other bodily states modulate LC-NE gain, which means the regime-switch threshold is not a fixed property of the environment but varies with the occupant's physiological state. The same acoustic event that is easily suppressed at 10 AM (when allostatic resources are high) may trigger a full regime switch at 3 PM (when circadian dip reduces PFC resistance). Architecture needs to account for *temporal variation in regime-switch threshold* -- the same environment may be adequate for explicit-regime protection in the morning and inadequate in the afternoon.

**Panel assessment**: Very strong empirical foundation for the basic two-mode model. Miller's refinement about PFC resistance and its depletion is critical for architectural applications. Barrett's point about allostatic modulation is important and underexplored. **Confidence: HIGH**.

#### T1-EC.3: Prefrontal-Basal Ganglia Gating

**Core claim**: The prefrontal cortex maintains workspace representations through persistent neural activity, and the basal ganglia implement a *gating* mechanism that controls what information enters and exits the workspace (Frank & Badre, 2012 [GS: ~500]; O'Reilly & Frank, 2006 [GS: ~1,500]; Hazy, Frank, & O'Reilly, 2007 [GS: ~600]).

**Botvinick's formulation for the panel**: Gating is what makes explicit cognition *controlled* rather than merely *conscious*. The workspace doesn't just broadcast whatever is loudest -- the basal ganglia learn to selectively admit task-relevant information and exclude task-irrelevant information, based on reinforcement history. The dopaminergic system trains the gate: successful workspace updates (ones that led to good outcomes) strengthen the gating policy; unsuccessful ones weaken it. This means gating is an acquired skill, not a fixed architectural property. Expert thinkers have better-trained gates -- they are better at keeping irrelevant environmental information out of the workspace.

**Environmental implication**: Gating has an *error rate* that depends on the discriminability of task-relevant and task-irrelevant information. When the environment contains stimuli that are semantically similar to the workspace content (e.g., overheard conversation about a topic related to one's work), gating accuracy drops because the gating system cannot easily distinguish relevant from irrelevant input. This predicts that *semantic similarity* between environmental intrusions and workspace content is a critical variable -- more so than raw intensity. A quiet conversation about one's own research topic is more disruptive than a louder conversation about an unrelated topic, because the gating system is less able to exclude semantically similar content.

**Friston's integration with PP**: Gating can be formalized as precision-weighting on the *temporal* dimension -- the gate is open when precision on the updating signal exceeds a threshold (learned through dopaminergic reinforcement), and closed otherwise. This connects the gating literature to PP: the workspace is maintained by high precision on top-down predictions, and updated when bottom-up PE achieves sufficient precision to overcome the top-down prior. The environment modulates this by changing the baseline precision of bottom-up signals -- a noisy environment with high PE variance increases baseline bottom-up precision, making the gate harder to keep closed.

**Panel assessment**: Strong computational and neurobiological support. The gating framework adds specificity beyond the general workspace story -- it explains *why* some environmental intrusions are more disruptive than others (semantic similarity) and *how* expertise modulates environmental sensitivity (learned gating policies). **Confidence: HIGH** for the basic mechanism; **MODERATE** for the specific dopaminergic training account.

#### T1-EC.4: Conflict Monitoring and Cognitive Control

**Core claim**: The anterior cingulate cortex (specifically dACC) monitors for conflict between competing processing streams and signals the need for increased cognitive control, which is then implemented by dorsolateral PFC (Botvinick et al., 2001 [GS: ~6,000]; Shenhav, Botvinick, & Cohen, 2013 [GS: ~1,500]).

**Botvinick's formulation for the panel**: Conflict monitoring provides the *error signal* that drives cognitive control allocation. When multiple incompatible representations compete for the workspace -- the maintained deliberative content vs. an environmental intrusion -- dACC detects the conflict and signals for increased control (increased PFC engagement, stronger gating, more precision on the maintained content). This is the mechanism behind the subjective experience of *effort* in maintaining concentration against distraction: the conflict monitor is firing continuously, driving costly control recruitment.

**Environmental implication**: Conflict monitoring has a metabolic cost (Shenhav, Musslick, Lieder, Kool, Griffiths, Cohen, & Botvinick, 2017 [GS: ~800]). Every environmental intrusion that creates workspace conflict -- even if successfully resolved by increased control -- depletes the resources available for cognitive control. The environment doesn't need to *succeed* in disrupting explicit processing to impose a cost; it merely needs to *threaten* disruption, triggering conflict monitoring and control recruitment. This means that the effective cost of an environment is not measured by the number of actual interruptions but by the number of *conflict events* -- detected threats that required control mobilization. An environment with frequent near-misses (events that triggered conflict monitoring but were successfully excluded by gating) is more fatiguing than an environment with no such events, even if the actual interruption count is identical.

**Cohen's connection to LC-NE**: The conflict signal from dACC is one of the inputs that can trigger phasic LC-NE bursts (Aston-Jones & Cohen, 2005). When conflict accumulates beyond a threshold, the system switches from the exploitation/explicit mode to the exploration/implicit mode -- this is the neurochemical implementation of "giving up" on a difficult cognitive task in a distracting environment. The person doesn't decide to stop concentrating; the accumulated conflict signal triggers a regime switch that makes sustained concentration neurochemically impossible until the LC-NE system returns to tonic mode.

**Panel assessment**: Very strong empirical support. The metabolic cost of conflict monitoring is the key addition to the architectural analysis -- it predicts that "almost-distracting" environments are more fatiguing than typically recognized. **Confidence: HIGH**.

#### T1-EC.5: Constructed Workspace -- Barrett's Allostatic-Predictive Account

**Core claim**: The workspace is not a passive stage on which representations appear; it is actively *constructed* through allostatic predictions that integrate interoceptive, exteroceptive, and conceptual information into a coherent situated experience (Barrett, 2017 [GS: ~3,000]; Kleckner et al., 2017 [GS: ~500]).

**Barrett's formulation for the panel**: The other panelists treat the workspace as if it operates on purely cognitive content -- representations, inferences, hypotheses. But every workspace state has an affective dimension because every prediction includes interoceptive predictions about the body's energy budget. When the workspace maintains a complex deliberative inference, this requires metabolic resources, and the brain is continuously predicting whether those resources are available. If the allostatic prediction says "we are running low" (due to poor sleep, inadequate nutrition, thermal stress, accumulated fatigue), the workspace's capacity *shrinks* -- not because of a cognitive limitation but because the brain's resource-allocation system withdraws metabolic support from the prefrontal network. This is the mechanism behind the common experience that concentration is harder when one is hungry, cold, sleep-deprived, or in physical discomfort.

**Environmental implication**: Architecture affects explicit cognition through two routes: (1) the cognitive route (PE variance, interruptions, conflict -- the focus of the other theories), and (2) the allostatic route (thermal comfort, air quality, ergonomics, circadian alignment -- the bodily conditions that determine the metabolic budget available for workspace maintenance). These routes are independent in mechanism but additive in effect. A thermally uncomfortable room with low PE variance may support less explicit processing than a thermally comfortable room with moderate PE variance, because the allostatic cost of thermal regulation drains the same metabolic budget that workspace maintenance requires.

**Kirsh's extension**: This connects to the embodied cognition literature on cognitive offloading (Kirsh & Maglio, 1994 [GS: ~2,500]; Risko & Gilbert, 2016 [GS: ~500]). The workspace is capacity-limited, but the capacity limit is partially set by the body's metabolic state, which is partially set by the environment. Architecture that supports the body (comfortable temperature, good air quality, appropriate lighting, ergonomic furniture) indirectly supports the mind by maintaining the metabolic budget from which workspace capacity is drawn. This is not metaphorical -- it is a direct physiological connection through allostatic regulation.

**Panel assessment**: Theoretically compelling and consistent with the empirical literature on environmental comfort and cognitive performance. Adds a critical dimension to the two-regime framework: implicit/explicit regime requirements are not only about PE statistics but about the bodily conditions that determine the metabolic budget for explicit processing. **Confidence: MODERATE-HIGH** (theoretical framework strong; specific quantitative predictions still emerging).

#### T1-EC.6: Extended Cognitive Niche -- Kirsh's Environmental Scaffolding Account

**Core claim**: Explicit cognition is not solely a brain-internal process; it routinely depends on external representational structures -- notes, diagrams, spatial arrangements of objects, architectural features -- that serve as persistent scaffolds for workspace operations (Clark & Chalmers, 1998 [GS: ~12,000]; Kirsh, 1995 [GS: ~1,200]; Kirsh, 2010 [GS: ~400]).

**Kirsh's formulation for the panel**: The workspace has a severe capacity limitation, but humans compensate by externalizing workspace contents into the environment. A researcher's desk covered with organized papers is not a mess -- it is an externalized workspace. The spatial arrangement encodes relationships (related papers nearby, contrasting positions facing each other), and the visual presence of each document serves as a persistent activation source for its associated workspace content, reducing the internal maintenance burden. When the researcher looks at a particular stack, its content is reactivated in the workspace without costly retrieval from long-term memory.

This means that the *architectural affordance for externalization* is a critical design variable for explicit-regime support. Can the occupant arrange physical objects? Is there display space for in-progress work? Can documents, diagrams, and notes remain visible and spatially organized? The trend toward "clean desk" policies and minimal workstations directly attacks the externalized workspace, forcing all maintenance into the capacity-limited internal workspace.

**Clark's strong endorsement**: This is the extended mind thesis applied to cognitive control. The workspace isn't inside the head -- it's a *coupled system* that includes the brain, the body, and the structured environment. Architecture that supports externalization *literally increases workspace capacity* by providing stable, persistent, spatially organized external storage that the internal workspace can use as an extension of itself. This is not a metaphor; it is a functional claim about the computational architecture of extended cognitive systems.

**Environmental implication**: Explicit-regime environments need *manipulable surfaces* -- whiteboards, corkboards, desk space for spreading documents, wall space for posting diagrams. The surfaces must be persistent (not cleared at end of day), personal (organized by the user, not by policy), and visually accessible from the work position (so that peripheral vision can maintain activation of externalized content without requiring deliberate visual search). Digital-only environments eliminate the spatial-organizational affordances that physical externalization provides, forcing all workspace management into the internal, capacity-limited system.

**Panel assessment**: Well-supported by the situated cognition literature and consistent with workplace productivity research. Provides a specific and actionable architectural design variable (externalization affordances) that is often overlooked in contemporary workspace design. **Confidence: HIGH** for the basic cognitive mechanism; **MODERATE** for the specific architectural predictions (needs more controlled workplace studies).

---

### TIER 1: CONVERGENCES AND DISPUTES

**Point of convergence 1: The workspace is real and capacity-limited.** All panelists agree that explicit cognition operates through a capacity-limited, serially organized representational system, whether this is characterized as global workspace ignition (Dehaene), precision-weighted gating (Friston), or extended cognitive scaffolding (Clark, Kirsh). The computational bottleneck is not an artifact of experimental paradigms but a genuine architectural constraint.

**Point of convergence 2: The environment modulates workspace capacity through multiple routes.** The panel identifies at least four routes: (a) PE-variance-driven interruption (the main focus of the two-regime framework), (b) conflict-driven depletion (Botvinick -- even suppressed interruptions cost resources), (c) allostatic modulation (Barrett -- bodily comfort determines metabolic budget), and (d) externalization support (Kirsh -- architecture can extend effective workspace capacity). A complete architectural account must address all four.

**Point of convergence 3: The LC-NE system is the regime-switching mechanism.** There is broad agreement that the transition between implicit (exploratory, Goldilocks-sensitive) and explicit (focused, interruption-sensitive) modes is mediated by the tonic/phasic balance of the LC-NE system, and that environmental events can trigger regime switches through phasic NE bursts.

**Dispute 1: Is the implicit/explicit distinction a continuum or a phase transition?** Dehaene argues for a sharp phase transition (ignition is all-or-none). Clark argues for a continuum with intermediate states. Barrett argues that the threshold varies with allostatic state, so the same stimulus may produce implicit processing in one metabolic state and explicit processing in another. Cohen notes that the LC-NE system operates on a continuum of tonic firing rates, suggesting the regime distinction is more graded than binary. **Resolution**: The panel agrees that for *architectural* purposes, treating the regimes as qualitatively distinct is productive even if the underlying neuronal mechanisms are continuous, because the environmental requirements are qualitatively different (mean PE vs. PE variance optimization).

**Dispute 2: Does PP need to be supplemented or replaced for explicit cognition?** Friston maintains that PP, properly formulated with hierarchical precision optimization and active inference, can account for explicit cognition without supplementation. Clark is sympathetic but acknowledges the homunculus problem is not fully resolved. Dehaene argues that the workspace is a distinct architectural feature that PP must be supplemented with. Miller and Botvinick argue that the prefrontal control system is computationally distinct from PP's automatic inference and requires its own theoretical treatment. **Resolution**: No consensus. The working document's position -- that PP handles implicit processing well and must be supplemented by a workspace/control account for explicit processing -- is endorsed by the majority (Dehaene, Miller, Botvinick, Cohen, Kirsh, Barrett) but contested by the minority (Friston, with Clark partially sympathetic).

**Dispute 3: How much does expertise change the picture?** Botvinick's gating account predicts that expert thinkers have better-trained gates and are therefore less susceptible to environmental disruption. This would mean that architectural requirements for explicit-regime protection vary with expertise level. Miller agrees: experts automate more of the explicit-regime processing, reducing workspace load. Barrett notes that experts may also have better allostatic regulation (less autonomic reactivity to mild stressors). Clark suggests that experts make more extensive use of environmental scaffolding, so their workspace is more extended and potentially more environmentally dependent, not less. **Resolution**: Expertise likely modulates sensitivity to environmental disruption, but the direction of the effect is complex and may differ across the four routes identified above.

---

### TIER 2: MECHANISTIC TEMPLATES -- PANEL-GENERATED

The panel reviewed templates EC-1 through EC-6 from Appendix A and endorsed all six with minor modifications. The following additional templates were generated through panel discussion.

#### Template EC-7: Conflict Accumulation and Regime Collapse (Botvinick/Cohen)

*Mechanism*: Environmental events that trigger conflict monitoring (dACC activation) impose a metabolic cost even when successfully excluded from the workspace. Conflict monitoring costs accumulate over time. When accumulated cost exceeds the PFC's sustainable control budget, the conflict signal triggers a phasic LC-NE burst, producing regime switch to implicit mode and explicit processing collapse.

*Prediction*: The duration of sustainable explicit processing in a given environment is a function not of the number of *successful* interruptions but of the number of *conflict events* (detected environmental threats that required control mobilization). An environment with 20 near-miss intrusions per hour (all successfully suppressed) will produce regime collapse faster than an environment with 5 actual interruptions per hour, because the cumulative conflict-monitoring cost of 20 near-misses exceeds the recovery cost of 5 interruptions with rebuild time.

*Architectural consequence*: Design for *zero* conflict events, not merely for *zero* actual interruptions. This means the environment should not contain stimuli that *could* trigger conflict monitoring -- not stimuli that *won't quite* penetrate the workspace. Acoustic masking should render speech *unintelligible* (not merely quiet), because intelligible speech at low volume still triggers conflict monitoring. Visual barriers should be *opaque* (not translucent), because visible movement through translucent barriers still triggers orienting. The design target is the *absence of subthreshold threats*, not just the absence of suprathreshold interruptions.

*Supporting evidence*: Botvinick et al. (2001); Shenhav et al. (2013 [GS: ~1,500]); Shenhav et al. (2017 [GS: ~800]); Kool, McGuire, Rosen, & Botvinick (2010 [GS: ~800]).

*Calibration parameters*: Conflict-monitoring metabolic cost per event (~0.5-1% of available control budget, estimated from Kool et al., 2010, cognitive effort avoidance data); sustainable control budget duration (~90-120 min before mandatory regime-switch rest; Helton & Russell, 2015 [GS: ~300]).

#### Template EC-8: Allostatic Load and Workspace Capacity (Barrett/Cohen)

*Mechanism*: Workspace maintenance requires metabolic resources allocated through allostatic prediction. Interoceptive predictions about resource availability modulate the precision allocated to prefrontal workspace representations. Environmental stressors that increase allostatic load (thermal discomfort, poor air quality, noise stress, ergonomic strain) reduce the metabolic budget available for workspace maintenance, leading to reduced effective workspace capacity and shorter sustainable explicit processing duration.

*Prediction*: Workspace capacity (measured as working memory span, sustained attention duration, or complexity of maintainable deliberative structures) will covary with environmental comfort variables independently of PE variance. A comfortable room with moderate PE variance will support more explicit processing than an uncomfortable room with low PE variance.

*Architectural consequence*: Allostatic support (thermal comfort, air quality, ergonomic design, circadian-aligned lighting) is not a luxury or a satisfaction variable -- it is a *cognitive performance* variable that directly modulates explicit-regime capacity. Design standards that treat comfort and cognition as independent are wrong: they are coupled through the allostatic budget. The ASHRAE thermal comfort standards (ASHRAE Standard 55), for example, define comfort ranges based on occupant satisfaction surveys, but the cognitive performance implications may call for *tighter* ranges than satisfaction alone would require (Seppanen, Fisk, & Lei, 2006 [GS: ~800]).

*Supporting evidence*: Barrett & Simmons (2015 [GS: ~700]); Kleckner et al. (2017 [GS: ~500]); Seppanen et al. (2006 [GS: ~800]); Wargocki & Wyon (2007 [GS: ~300]); Allen et al. (2016 [GS: ~600]).

*Calibration parameters*: Temperature performance optimum: ~21-22 degrees C (Seppanen et al., 2006), with ~1% cognitive performance decrement per degree deviation. CO2 performance threshold: significant decrement above ~1000 ppm (Allen et al., 2016). Light intensity for sustained attention: 300-500 lux (Boyce, 2014 [GS: ~1,000]).

#### Template EC-9: Semantic Gating Load and Content-Specific Vulnerability (Botvinick/Dehaene)

*Mechanism*: The basal ganglia gating system excludes environmental content from the workspace based on learned relevance discrimination. Gating error rate increases when environmental content is semantically similar to workspace content, because the gating system cannot easily discriminate relevant from irrelevant input on the basis of semantic features alone. Semantically similar environmental content produces more frequent gate "leaks," more workspace contamination, more conflict monitoring, and faster depletion.

*Prediction*: The disruptive effect of environmental speech varies with its semantic relationship to the occupant's current task. Overheard conversation about one's own research topic is more disruptive than equally loud conversation about an unrelated topic. Background music with lyrics in the occupant's native language is more disruptive during language-based tasks than during spatial tasks. The critical variable is the *semantic overlap* between environmental content and workspace content.

*Architectural consequence*: Acoustic design for explicit-regime environments should prioritize semantic masking over simple volume reduction. Rendering speech unintelligible (through noise masking, absorption, or spatial separation that degrades phonemic cues) is more important than reducing its volume. Multi-language offices may have different masking requirements -- speech in a non-native language is less disruptive because it generates less semantic activation. Implications for office layout: people working on similar projects should not be placed within each other's speech range, because the semantic similarity of their conversations maximizes cross-disruption.

*Supporting evidence*: Colle & Welsh (1976 [GS: ~600]); Jones & Macken (1993 [GS: ~400]); Marsh, Hughes, & Jones (2008 [GS: ~200]); Haka et al. (2009 [GS: ~200]).

*Calibration parameters*: Irrelevant speech effect magnitude: ~30% performance decrement on serial recall tasks (Jones & Macken, 1993). Speech intelligibility threshold for significant disruption: STI > 0.20 (Haapakangas et al., 2011 [GS: ~200]). Semantic relatedness multiplier: ~1.5x-2x base disruption for content-related speech (estimated from Marsh et al., 2008).

#### Template EC-10: Externalization Affordance and Effective Workspace Size (Kirsh/Clark)

*Mechanism*: The internal workspace is capacity-limited (~4 items/chunks, Cowan, 2001 [GS: ~4,500]). However, this limit applies to *internally maintained* representations. When workspace contents are externalized -- written on paper, arranged on a desk, displayed on a wall -- they are maintained by the environment rather than by prefrontal persistent activity, and can be reactivated through a brief visual fixation rather than costly internal retrieval. The effective workspace capacity is therefore: internal capacity + externalized capacity, where externalized capacity is determined by the number of stable, spatially organized, visually accessible external representations.

*Prediction*: Explicit processing performance on tasks that exceed internal workspace capacity (complex multi-step reasoning, theory comparison, synthesis across sources) will be better in environments that support externalization than in environments that do not, holding all other variables constant. The benefit will be proportional to the degree by which the task exceeds internal workspace capacity -- no benefit for simple tasks, large benefits for complex tasks.

*Architectural consequence*: Explicit-regime workspaces need: (a) display surfaces -- whiteboards, corkboards, wall space for posting, desk space for spreading -- that are within the visual field from the primary work position; (b) persistence -- externalized content must remain undisturbed across work sessions (clean-desk policies destroy externalized workspaces); (c) manipulability -- the occupant must be able to rearrange externalized content to reflect evolving conceptual structure (fixed displays are less useful than moveable ones); (d) appropriate granularity -- the display resolution must support the type of externalization required (fine text requires close surfaces; conceptual maps require large surfaces visible from a distance).

*Supporting evidence*: Cowan (2001 [GS: ~4,500]); Kirsh (1995 [GS: ~1,200]); Kirsh (2010 [GS: ~400]); Risko & Gilbert (2016 [GS: ~500]); Clark & Chalmers (1998 [GS: ~12,000]).

*Calibration parameters*: Internal workspace capacity: ~4 chunks (Cowan, 2001). Externalization reactivation time: ~200-500ms per visual fixation on externalized content (estimate from visual search literature). Maximum useful externalized items: ~20-30 (beyond which the spatial organization itself becomes a search problem; estimate from Kirsh, 1995).

#### Template EC-11: Regime-Transition Circadian Modulation (Barrett/Cohen)

*Mechanism*: The regime-switch threshold (the magnitude of environmental PE required to trigger phasic LC-NE burst and force implicit-mode transition) varies with circadian phase. During circadian peaks (typically 09:00-12:00 and 16:00-18:00), PFC resistance to phasic triggering is high and the regime-switch threshold is elevated -- the explicit regime is robust. During the circadian trough (typically 13:00-15:00), PFC resistance is reduced, the regime-switch threshold drops, and environmental events that would be easily suppressed at peak hours can trigger regime collapse.

*Prediction*: The same environment will support different amounts of explicit processing at different times of day. Environments that are adequate for explicit-regime protection during circadian peaks may be inadequate during the post-lunch trough. The interaction is multiplicative: circadian trough x high PE variance = regime collapse even in moderately well-designed environments.

*Architectural consequence*: Explicit-regime protection should be *temporally modulated* -- strongest during vulnerable circadian periods. Practical implementations: (a) scheduling policies that reserve deepest-work spaces for afternoon use; (b) adaptive acoustic masking that increases during 13:00-15:00; (c) lighting that provides higher-intensity, cooler-temperature illumination during the circadian trough to compensate for reduced cortical arousal; (d) thermal design that maintains tighter comfort bands during vulnerable periods. The circadian alignment of lighting through melanopsin-activating blue-enriched illumination (Berson et al., 2002 [GS: ~2,500]) provides a direct environmental intervention for regime-switch threshold maintenance.

*Supporting evidence*: Aston-Jones & Cohen (2005 [GS: ~5,000]); Van Dongen, Baynard, Maislin, & Dinges (2004 [GS: ~1,000]); Cajochen, Munch, Kobialka, Krauchi, Steiner, Oelhafen, ... & Wirz-Justice (2005 [GS: ~400]); Berson et al. (2002 [GS: ~2,500]).

*Calibration parameters*: Circadian trough performance decrement: ~10-20% on sustained attention tasks (Van Dongen et al., 2004). Blue-enriched light compensation: 6500K illumination at 500+ lux partially offsets circadian dip (Cajochen et al., 2005).

#### Template EC-12: Task-Switching Costs and Spatial Encoding of Mode (Botvinick/Kirsh)

*Mechanism*: Switching between implicit and explicit regimes incurs a reconfiguration cost: the gating policy must be updated, precision must be reallocated, and workspace contents must be rebuilt. This cost is reduced when the switch is *spatially encoded* -- when different physical locations are associated with different computational regimes through learning. Place-cells and spatial context signals prime the appropriate gating policy before the regime switch is needed, reducing transition time.

*Prediction*: Regime switching will be faster when the implicit and explicit environments are spatially distinct (different rooms, different locations within a room) than when they occupy the same space (same desk, same chair). The benefit of spatial encoding increases with the number of transitions per day -- habitual switchers develop stronger place-mode associations.

*Architectural consequence*: Separate implicit-mode and explicit-mode activities into *distinct spatial zones* rather than accommodating both in a single "flexible" space. The spatial separation provides contextual priming that accelerates regime switching. The "activity-based working" model (no assigned desks; choose a workspace based on current task) is compatible with this prediction *if* the spatial zones are perceptually distinct and consistently associated with specific modes. The critical failure mode is the undifferentiated open plan, where no spatial region has a consistent mode association and contextual priming cannot develop.

*Supporting evidence*: Monsell (2003 [GS: ~3,500]); Godden & Baddeley (1975 [GS: ~2,500]); Smith & Vela (2001 [GS: ~1,500]).

*Calibration parameters*: Baseline task-switch cost: ~200-500ms for simple switches (Monsell, 2003); 10-23 minutes for full regime transition (Mark et al., 2005, 2008). Context-dependent memory benefit: ~10-20% recall improvement in matching vs. mismatching environments (Smith & Vela, 2001).

---

### PANEL SUMMARY: SCOPE EXCLUSIONS AND OPEN QUESTIONS

**Scope exclusions**: The panel did not address: (a) age-related changes in explicit-regime capacity (though the developmental dimension in Section 4.4 was endorsed as important); (b) clinical populations with impaired explicit processing (ADHD, schizophrenia, TBI) and their architectural requirements; (c) pharmacological modulation of regime-switch threshold (caffeine, methylphenidate); (d) the role of sleep architecture in next-day explicit-regime capacity.

**Open questions for future panels**:

1. *Quantitative regime-switch model*: Can we specify the precise mathematical relationship between PE variance, conflict accumulation, allostatic load, and circadian phase in predicting regime-switch probability? This would allow quantitative architectural specification rather than qualitative design principles.

2. *Digital vs. physical externalization*: Does digital externalization (multiple screens, tabs, documents) provide the same workspace extension as physical externalization (papers, whiteboards)? Preliminary evidence suggests not (Mangen, Walgermo, & Bronnick, 2013 [GS: ~400]), but the mechanism is unclear.

3. *Social-cognitive regime*: Is there a third regime -- a *social-cognitive* mode distinct from both implicit processing and individual explicit processing -- that operates during collaborative deliberation? If so, it would have its own environmental requirements distinct from both the Goldilocks zone and the variance-minimization principle.

4. *Expertise x environment interaction*: How does expertise modulate the four routes of environmental influence (PE variance, conflict accumulation, allostatic load, externalization)? Does expertise reduce sensitivity on all routes equally, or are some routes more resilient to expertise effects?


## APPENDIX B: SLIDES TO ADD TO GOLDILOCKS PRESENTATION

### [TO BE DEVELOPED IN NEXT SESSION — after Appendix A is complete]

Proposed new slides:
- Implicit vs. explicit: two computational regimes, two environmental profiles
- The Kidd data as "simplest case" — single-level parameter estimation
- Real-world cognition: multiple hierarchical levels, conflicting optima
- PE mean vs. PE variance: the critical design variable for deep work
- Interruption cost: why spikes matter more than means
- Architectural examples for each regime
- The two-regime design principle: moderate complexity + temporal stability
- Tier 1 theories and their architectural consequences
- Tier 2 mechanistic templates with design implications

---

## REFERENCES

Allen, J. G., MacNaughton, P., Satish, U., Santanam, S., Vallarino, J., & Spengler, J. D. (2016). Associations of cognitive function scores with carbon dioxide, ventilation, and volatile organic compound exposures in office workers. *Environmental Health Perspectives*, 124(6), 805–812. [GS: ~600]

Allen, T. J. (1977). *Managing the Flow of Technology*. MIT Press. [GS: ~4,000]

Altmann, E. M., & Trafton, J. G. (2002). Memory for goals: An activation-based model. *Cognitive Science*, 26(1), 39–83. [GS: ~800]

Arnsten, A. F. T. (2009). Stress signalling pathways that impair prefrontal cortex structure and function. *Nature Reviews Neuroscience*, 10(6), 410–422. [GS: ~1,500]

Aston-Jones, G., & Cohen, J. D. (2005). An integrative theory of locus coeruleus-norepinephrine function. *Annual Review of Neuroscience*, 28, 403–450. [GS: ~5,000]

Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press. [GS: ~4,000]

Barrett, L. F. (2017). *How Emotions Are Made: The Secret Life of the Brain*. Houghton Mifflin Harcourt. [GS: ~3,000]

Barrett, L. F., & Simmons, W. K. (2015). Interoceptive predictions in the brain. *Nature Reviews Neuroscience*, 16(7), 419–429. [GS: ~700]

Barrett, P., Zhang, Y., Moffat, J., & Kobbacy, K. (2013). A holistic, multi-level analysis identifying the impact of classroom design on pupils' learning. *Building and Environment*, 59, 678–689. [GS: ~400]

Beauchemin, K. M., & Hays, P. (1998). Dying in the dark: Sunshine, gender and outcomes in myocardial infarction. *Journal of the Royal Society of Medicine*, 91(7), 352–354. [GS: ~600]

Berlyne, D. E. (1971). *Aesthetics and Psychobiology*. Appleton-Century-Crofts. [GS: ~5,000]

Bernstein, E. S., & Turban, S. (2018). The impact of the 'open' workspace on human collaboration. *Philosophical Transactions of the Royal Society B*, 373(1753), 20170239. [GS: ~400]

Berridge, C. W., & Waterhouse, B. D. (2003). The locus coeruleus–noradrenergic system: Modulation of behavioral state and state-dependent cognitive processes. *Brain Research Reviews*, 42(1), 33–84. [GS: ~1,500]

Berson, D. M., Dunn, F. A., & Takao, M. (2002). Phototransduction by retinal ganglion cells that set the circadian clock. *Science*, 295(5557), 1070–1073. [GS: ~2,500]

Botvinick, M. M., Braver, T. S., Barch, D. M., Carter, C. S., & Cohen, J. D. (2001). Conflict monitoring and cognitive control. *Psychological Review*, 108(3), 624–652. [GS: ~6,000]

Bouret, S., & Sara, S. J. (2005). Network reset: A simplified overarching theory of locus coeruleus noradrenaline function. *Trends in Neurosciences*, 28(11), 574–582. [GS: ~1,200]

Boyce, P. R. (2014). *Human Factors in Lighting* (3rd ed.). CRC Press. [GS: ~1,000]

Brager, G. S., & de Dear, R. J. (1998). Thermal adaptation in the built environment: A literature review. *Energy and Buildings*, 27(1), 83–96. [GS: ~1,000]

Bregman, A. S. (1990). *Auditory Scene Analysis*. MIT Press. [GS: ~5,500]

Busch-Vishniac, I. J., West, J. E., Barnhill, C., Hunter, T., Orber, D., & Ney, R. (2005). Noise levels in Johns Hopkins Hospital. *Journal of the Acoustical Society of America*, 118(6), 3629–3645. [GS: ~500]

Cajochen, C., Munch, M., Kobialka, S., Krauchi, K., Steiner, R., Oelhafen, P., ... & Wirz-Justice, A. (2005). High sensitivity of human melatonin, alertness, thermoregulation, and heart rate to short wavelength light. *Journal of Clinical Endocrinology & Metabolism*, 90(3), 1311-1316. [GS: ~400]

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *BBS*, 36(3), 181–204. [GS: ~5,800]

Clark, A. (2016). *Surfing Uncertainty*. Oxford University Press. [GS: ~3,200]

Clark, A. (2017). Predictions, precision, and agentive attention. *Consciousness and Cognition*, 56, 115–119.

Clark, A. (2018). A nice surprise? Predictive processing and the active pursuit of novelty. *Phenomenology and the Cognitive Sciences*, 17(3), 521–534. [GS: ~85]

Colle, H. A., & Welsh, A. (1976). Acoustic masking in primary memory. *Journal of Verbal Learning and Verbal Behavior*, 15(1), 17–31. [GS: ~600]

Corbetta, M., & Shulman, G. L. (2002). Control of goal-directed and stimulus-driven attention in the brain. *Nature Reviews Neuroscience*, 3(3), 201–215. [GS: ~10,000]

Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. *Behavioral and Brain Sciences*, 24(1), 87-114. [GS: ~4,500]

Craik, F. I. M., & Lockhart, R. S. (1972). Levels of processing: A framework for memory research. *Journal of Verbal Learning and Verbal Behavior*, 11(6), 671–684. [GS: ~12,000]

Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row. [GS: ~25,000]

Cvach, M. (2012). Monitor alarm fatigue: An integrative review. *Biomedical Instrumentation & Technology*, 46(4), 268–277. [GS: ~500]

Dehaene, S., & Naccache, L. (2001). Towards a cognitive neuroscience of consciousness. *Cognition*, 79(1–2), 1–37. [GS: ~4,500]

Dehaene, S., Changeux, J.-P., Naccache, L., Sackur, J., & Sergent, C. (2006). Conscious, preconscious, and subliminal processing: A testable taxonomy. *Trends in Cognitive Sciences*, 10(5), 204–211. [GS: ~1,000]

Dehaene, S., Kerszberg, M., & Changeux, J.-P. (1998). A neuronal model of a global workspace in effortful cognitive tasks. *Proceedings of the National Academy of Sciences*, 95(24), 14529–14534. [GS: ~2,000]

Diamond, A. (2013). Executive functions. *Annual Review of Psychology*, 64, 135–168. [GS: ~4,500]

Ely, E. W., Inouye, S. K., Bernard, G. R., Gordon, S., Francis, J., May, L., ... & Dittus, R. (2001). Delirium in mechanically ventilated patients. *JAMA*, 286(21), 2703–2710. [GS: ~3,000]

Feldman, H., & Friston, K. (2010). Attention, uncertainty, and free-energy. *Frontiers in Human Neuroscience*, 4, 215. [GS: ~1,200]

Fisher, A. V., Godwin, K. E., & Seltman, H. (2014). Visual environment, attention allocation, and learning in young children: When too much of a good thing may be bad. *Psychological Science*, 25(7), 1362–1370. [GS: ~300]

Fodor, J. A., & Pylyshyn, Z. W. (1988). Connectionism and cognitive architecture: A critical analysis. *Cognition*, 28(1–2), 3–71. [GS: ~6,000]

Frank, M. J., & Badre, D. (2012). Mechanisms of hierarchical reinforcement learning in corticostriatal circuits 1: Computational analysis. *Cerebral Cortex*, 22(3), 509–526. [GS: ~500]

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138. [GS: ~8,500]

Frith, C. D., & Frith, U. (2006). The neural basis of mentalizing. *Neuron*, 50(4), 531–534. [GS: ~4,000]

Godden, D. R., & Baddeley, A. D. (1975). Context-dependent memory in two natural environments: On land and underwater. *British Journal of Psychology*, 66(3), 325-331. [GS: ~2,500]

Gonzalez, V. M., & Mark, G. (2004). "Constant, constant, multi-tasking craziness": Managing multiple working spheres. *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, 113–120. [GS: ~300]

Gopnik, A. (2020). Childhood as a solution to explore-exploit tensions. *Philosophical Transactions of the Royal Society B*, 375(1803), 20190502. [GS: ~200]

Haapakangas, A., Kankkunen, E., Hongisto, V., Virjonen, P., Oliva, D., & Keskinen, E. (2011). Effects of five speech masking sounds on performance and acoustic satisfaction. *Acta Acustica United with Acustica*, 97(4), 641–655. [GS: ~200]

Haka, M., Haapakangas, A., Keranen, J., Hakala, J., Keskinen, E., & Hongisto, V. (2009). Performance effects and subjective disturbance of speech in acoustically different office types. *Indoor Air*, 19(3), 241-251. [GS: ~200]

Hanley, M., Khairat, M., Taylor, K., Wilson, R., Cole-Fletcher, R., & Riby, D. M. (2017). Classroom displays — attraction or distraction? Evidence of impact on attention and learning from children with and without autism. *Developmental Psychology*, 53(7), 1265–1275.

Hazy, T. E., Frank, M. J., & O'Reilly, R. C. (2007). Towards an executive without a homunculus: Computational models of the prefrontal cortex/basal ganglia system. *Philosophical Transactions of the Royal Society B*, 362(1485), 1601-1613. [GS: ~600]

Healey, A. N., Sevdalis, N., & Vincent, C. A. (2006). Measuring intra-operative interference from distraction and interruption observed in the operating theatre. *Ergonomics*, 49(5–6), 589–604. [GS: ~200]

Helton, W. S., & Russell, P. N. (2015). Rest is best: The role of rest and task interruptions on vigilance. *Cognition*, 134, 165-173. [GS: ~300]

Heschong, L. (1999). *Daylighting in Schools: An Investigation into the Relationship Between Daylighting and Human Performance*. Heschong Mahone Group. [GS: ~400]

Hohwy, J. (2012). Attention and conscious perception in the hypothesis testing brain. *Frontiers in Psychology*, 3, 96. [GS: ~1,000]

Hwang, R. L., & Jeon, M. J. (2020). Effects of thermal environment on patient recovery in hospital. *Building and Environment*, 169, 106556.

Jones, D. M., & Macken, W. J. (1993). Irrelevant tones produce an irrelevant speech effect: Implications for phonological coding in working memory. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 19(2), 369–381. [GS: ~400]

Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux. [GS: ~60,000+]

Kaplan, R., & Kaplan, S. (1989). *The Experience of Nature: A Psychological Perspective*. Cambridge University Press. [GS: ~7,500]

Kidd, C., & Hayden, B. Y. (2015). The psychology and neuroscience of curiosity. *Neuron*, 88(3), 449–460. [GS: ~700]

Kidd, C., Piantadosi, S. T., & Aslin, R. N. (2012). The Goldilocks effect: Human infants allocate attention to visual sequences that are neither too simple nor too complex. *PLoS ONE*, 7(5), e36399. [GS: ~700]

Kidd, C., Piantadosi, S. T., & Aslin, R. N. (2014). The Goldilocks effect in infant auditory attention. *Child Development*, 85(5), 1795–1804. [GS: ~200]

Kim, J., & de Dear, R. (2013). Workspace satisfaction: The privacy-communication trade-off in open-plan offices. *Journal of Environmental Psychology*, 36, 18–26. [GS: ~1,200]

Kirsh, D. (1995). The intelligent use of space. *Artificial Intelligence*, 73(1-2), 31-68. [GS: ~1,200]

Kleckner, I. R., Zhang, J., Touroutoglou, A., Makris, N., Dickerson, B. C., & Barrett, L. F. (2017). Evidence for a large-scale brain system supporting allostasis and interoception in humans. *Nature Human Behaviour*, 1(5), 0069. [GS: ~500]

Kool, W., McGuire, J. T., Rosen, Z. B., & Botvinick, M. M. (2010). Decision making and the avoidance of cognitive demand. *Journal of Experimental Psychology: General*, 139(4), 665-682. [GS: ~800]

Lake, B. M., Ullman, T. D., Tenenbaum, J. B., & Gershman, S. J. (2017). Building machines that learn and think like people. *BBS*, 40, e253. [GS: ~3,500]

Langer, E. J., & Rodin, J. (1976). The effects of choice and enhanced personal responsibility for the aged. *Journal of Personality and Social Psychology*, 34(2), 191–198. [GS: ~3,500]

Lau, H., & Rosenthal, D. (2011). Empirical support for higher-order theories of conscious awareness. *Trends in Cognitive Sciences*, 15(8), 365–373. [GS: ~600]

Leather, P., Pyrgas, M., Beale, D., & Lawrence, C. (1998). Windows in the workplace: Sunlight, view, and occupational stress. *Environment and Behavior*, 30(6), 739–762. [GS: ~300]

Lennie, P. (2003). The cost of cortical computation. *Current Biology*, 13(6), 493–497. [GS: ~1,500]

Mangen, A., Walgermo, B. R., & Bronnick, K. (2013). Reading linear texts on paper versus computer screen: Effects on reading comprehension. *International Journal of Educational Research*, 58, 61-68. [GS: ~400]

Marcus, G. F. (2001). *The Algebraic Mind: Integrating Connectionism and Cognitive Science*. MIT Press. [GS: ~2,000]

Mark, G., Gonzalez, V. M., & Harris, J. (2005). No task left behind? Examining the nature of fragmented work. *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, 321–330. [GS: ~1,500]

Mark, G., Gudith, D., & Klocke, U. (2008). The cost of interrupted work: More speed and stress. *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, 107–110. [GS: ~500]

Marsh, J. E., Hughes, R. W., & Jones, D. M. (2008). Auditory distraction in semantic memory: A process-based approach. *Journal of Memory and Language*, 58(3), 682-700. [GS: ~200]

Mehta, R., Zhu, R., & Cheema, A. (2012). Is noise always bad? Exploring the effects of ambient noise on creative cognition. *Journal of Consumer Research*, 39(4), 784–799. [GS: ~1,200]

Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annual Review of Neuroscience*, 24, 167–202. [GS: ~10,000]

Miller, M., & Clark, A. (2018). Happily entangled: Prediction, emotion, and the embodied mind. *Synthese*, 195(6), 2559–2575. [GS: ~250]

Monk, C. A., Trafton, J. G., & Boehm-Davis, D. A. (2008). The effect of interruption duration and demand on resuming suspended goals. *Journal of Experimental Psychology: Applied*, 14(4), 299–313. [GS: ~300]

Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences*, 7(3), 134-140. [GS: ~3,500]

Newsham, G. R., Aries, M. B. C., Mancini, S., & Faye, G. (2009). Individual control of electric lighting in a daylit space. *Lighting Research and Technology*, 40(1), 25–41. [GS: ~200]

Nicklas, M. H., & Bailey, G. B. (1996). *Student Performance in Daylit Schools*. Innovative Design. [GS: ~200]

O'Reilly, R. C., & Frank, M. J. (2006). Making working memory work: A computational model of learning in the prefrontal cortex and basal ganglia. *Neural Computation*, 18(2), 283–328. [GS: ~1,500]

Piantadosi, S. T., Kidd, C., & Aslin, R. N. (2014). Rich analysis and rational models: Inferring individual behavior from infant looking data. *Developmental Science*, 17(3), 321–337. [GS: ~150]

Quiroga, R. Q., Mukamel, R., Isham, E. A., Malach, R., & Fried, I. (2008). Human single-neuron responses at the threshold of conscious recognition. *Proceedings of the National Academy of Sciences*, 105(9), 3599-3604. [GS: ~800]

Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences*, 20(9), 676-688. [GS: ~500]

Roper, K. O., & Juneja, P. (2018). Distractions in the workplace revisited. *Journal of Facilities Management*, 16(3), 347–361. [GS: ~50]

Seppanen, O., Fisk, W. J., & Lei, Q. H. (2006). Effect of temperature on task performance in office environment. *Lawrence Berkeley National Laboratory Report*. [GS: ~800]

Shenhav, A., Botvinick, M. M., & Cohen, J. D. (2013). The expected value of control: An integrative theory of anterior cingulate cortex function. *Neuron*, 79(2), 217-240. [GS: ~1,500]

Shiffrin, R. M., & Schneider, W. (1977). Controlled and automatic human information processing: II. Perceptual learning, automatic attending, and a general theory. *Psychological Review*, 84(2), 127–190. [GS: ~7,000]

Smith, S. M., & Vela, E. (2001). Environmental context-dependent memory: A review and meta-analysis. *Psychonomic Bulletin & Review*, 8(2), 203-220. [GS: ~1,500]

Speier, C., Valacich, J. S., & Vessey, I. (1999). The influence of task interruption on individual decision making: An information overload perspective. *Decision Sciences*, 30(2), 337–360. [GS: ~700]

Sterling, P. (2012). Allostasis: A model of predictive regulation. *Physiology & Behavior*, 106(1), 5–15. [GS: ~1,500]

Tenenbaum, J. B., Kemp, C., Griffiths, T. L., & Goodman, N. D. (2011). How to grow a mind: Statistics, structure, and abstraction. *Science*, 331(6022), 1279–1285. [GS: ~3,500]

Theeuwes, J. (1991). Exogenous and endogenous control of attention: The effect of visual onsets and offsets. *Perception & Psychophysics*, 49(1), 83–90. [GS: ~2,500]

Ullmann, Y., Fodor, L., Schwarzberg, I., Carmi, N., Ullmann, A., & Ramon, Y. (2008). The sounds of music in the operating room. *Injury*, 39(5), 592–597. [GS: ~150]

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420–421. [GS: ~6,000]

Ulrich, R. S., Zimring, C., Zhu, X., DuBose, J., Seo, H. B., Choi, Y. S., ... & Joseph, A. (2008). A review of the research literature on evidence-based healthcare design. *Health Environments Research & Design Journal*, 1(3), 61–125. [GS: ~500]

Van Dongen, H. P. A., Baynard, M. D., Maislin, G., & Dinges, D. F. (2004). Systematic interindividual differences in neurobehavioral impairment from sleep loss: Evidence of trait-like differential vulnerability. *Sleep*, 27(3), 423-433. [GS: ~1,000]

Wargocki, P., & Wyon, D. P. (2007). The effects of moderately raised classroom temperatures and classroom ventilation rate on the performance of schoolwork by children. *HVAC&R Research*, 13(2), 193–220. [GS: ~300]

Weigl, M., Antoniadis, S., Chiapponi, C., Bruns, C., & Sevdalis, N. (2012). The impact of intra-operative interruptions on surgeons' perceived workload: An observational study. *Surgical Endoscopy*, 29(1), 145–153. [GS: ~150]

Wu, S., Blanchard, T. C., Meschke, E., Aslin, R. N., Hayden, B. Y., & Kidd, C. (in prep). Information-seeking behavior in human-infant and macaque learners.

Wyon, D. P. (1996). Indoor environmental effects on productivity. *Proceedings of IAQ '96: Paths to Better Building Environments*, 5–15.
