# Subject Characteristics in the Constraint–Valuation Architecture

**Date**: February 28, 2026
**Version**: CVA-SUBJECT-CHARACTERISTICS-v1.0
**Scope**: Formal integration of neurotype, culture, development, and individual differences into CVA
**Target Audience**: Professor David Kirsh (UCSD Cognitive Science), implementation team, expert panel
**Status**: Foundational formalization for empirical research roadmap

---

## Executive Summary

The Constraint–Valuation Architecture (CVA) operates across three layers: constraint perception, valuation assignment, and behavioral policy. This document formalizes how subject characteristics (culture, neurotype, age, experience, state, trait) systematically modulate each layer. Rather than treating CVA as culturally or neurologically universal and merely adding different weights, we propose a **two-tier model** where:

1. **Tier 1 constraints** (perceptual primitives: edge detection, motion, figure–ground) remain approximately universal across healthy development
2. **Tier 2 constraints** (interpretive overlays: "complexity," "threat," "coherence") are calibrated by a structured **subject-characteristics parameter space ψ**
3. **Valuations** have culture-selected and neurotype-modulated **structural variants**, not merely weight distributions
4. **Policy precision** (how reliably valuations drive behavior) is state and neurotype-dependent

We provide formal definitions, neurotype-specific profiles (PTSD, ASD, Alzheimer's, older adults, children, ADHD, depression, anxiety, bipolar, gifted), and a research roadmap for empirical validation. This framework enables principled comparison across populations and formalizes the relationship to population-transfer methods (e.g., ATLAS δ parameters).

---

## 1. THE SUBJECT-CHARACTERISTICS PARAMETER SPACE

### 1.1 Formal Definition

Let **ψ** denote the structured representation of subject characteristics:

$$\psi = \{\psi_{\text{culture}}, \psi_{\text{neuro}}, \psi_{\text{dev}}, \psi_{\text{exp}}, \psi_{\text{state}}, \psi_{\text{trait}}\}$$

Each component is defined below.

#### ψ_culture: Cultural Context

**Definition**: A structured encoding of cultural values, spatial aesthetics, social norms, and ecological learning history.

$$\psi_{\text{culture}} = \{\kappa_{\text{self}}, \kappa_{\text{social}}, \kappa_{\text{aesthetics}}, \kappa_{\text{ecology}}\}$$

where:
- **κ_self**: Individualism–collectivism axis and self-construal model (independent vs. interdependent; Markus & Kitayama, 1991)
- **κ_social**: Social structure preference (e.g., hierarchical vs. egalitarian; in-group/out-group salience; amae vs. autonomy; Àṣà vs. individual dignity)
- **κ_aesthetics**: Preferred material densities, color palettes, symmetry/asymmetry, temporal pacing (Ma/emptiness, ornamentation, rhythm)
- **κ_ecology**: Climatic adaptation, material availability, settlement density, threat environment

**Empirical Basis**: Cross-cultural psychology (Nisbett & Masuda, 2003; Barrett et al., 2016) and architectural anthropology (Rapoport, 1969) establish that cultures differentially allocate attentional resources and construct emotional meaning around spatial features.

#### ψ_neuro: Neurotype Profile

**Definition**: A constellation of atypical neural sensitivities, information processing characteristics, and neurotransmitter profiles that affect both perceptual and valuation systems.

$$\psi_{\text{neuro}} = \{\nu_{\text{sensory}}, \nu_{\text{integration}}, \nu_{\text{learning}}, \nu_{\text{threat}}, \nu_{\text{social}}, \nu_{\text{reward}}\}$$

where:
- **ν_sensory**: Thresholds and integrating windows for each sensory modality (reduced in autism; heightened in migraine, hyperacusis; delayed in aging)
- **ν_integration**: Multimodal binding speeds and temporal binding windows (widened in autism; shortened in ADHD; delayed in aging)
- **ν_learning**: Rate of perceptual calibration and model updating (slowed in Alzheimer's; accelerated in some gifted profiles)
- **ν_threat**: Threat-detection threshold and amygdala-responsiveness scaling (lowered in PTSD and anxiety; altered in bipolar states)
- **ν_social**: Social salience weighting and mentalizing speed (reduced in autism; hyperactivated in social anxiety)
- **ν_reward**: Sensitivity to reward prediction error and anhedonia levels (flattened in depression; manic elevation in bipolar disorder)

**Empirical Basis**: Neuroscientific literature on atypical sensory processing (Markram & Markram, 2010, on autism; van der Kolk, 2014, on PTSD; Hescham et al., 2016, on aging and sensory thresholds).

#### ψ_dev: Developmental Stage

**Definition**: Age-indexed maturation of perceptual, attentional, and conceptual systems.

$$\psi_{\text{dev}} = \{a, m_{\text{visual}}, m_{\text{motor}}, m_{\text{exec}}, m_{\text{social}}\}$$

where:
- **a**: Chronological age (in years or developmental bins)
- **m_visual**: Visual development stage (acuity, contrast sensitivity, visual field integration)
- **m_motor**: Motor development and proprioceptive calibration
- **m_exec**: Executive function maturation (working memory, temporal reasoning, impulse control)
- **m_social**: Theory of mind and social reasoning development

**Empirical Basis**: Developmental psychology and neuroscience (Blakemore & Choudhury, 2006; Casey et al., 2008; Diamond, 2002) establish age-linked timescales for cortical maturation.

#### ψ_exp: Experience and Expertise

**Definition**: Domain-specific perceptual calibration and skilled pattern recognition that modulates how constraints are perceived.

$$\psi_{\text{exp}} = \{e_{\text{domain}}, e_{\text{years}}, e_{\text{mastery}}\}$$

where:
- **e_domain**: Primary domain (architecture, visual art, music, spatial navigation, social interaction)
- **e_years**: Years of deliberate practice
- **e_mastery**: Perceptual-learning signature (whether the domain has produced measurable refinement)

**Empirical Basis**: Expertise and perceptual learning literature (Ericsson, 1996; Kellman & Garrigan, 2009). Experts in visual domains (architects, artists) show accelerated constraint perception (ProcessingCost reduced; pattern density discrimination improved).

#### ψ_state: Acute Psychological State

**Definition**: Transient mental/physiological conditions that modulate constraint sensitivity and valuation weights over hours to days.

$$\psi_{\text{state}} = \{\rho_{\text{fatigue}}, \rho_{\text{arousal}}, \rho_{\text{stress}}, \rho_{\text{affect}}\}$$

where:
- **ρ_fatigue**: Sleep deprivation and cognitive load (0 = well-rested; 1 = severe fatigue)
- **ρ_arousal**: Sympathetic activation and alertness (low = hypoarousal; high = hyperarousal)
- **ρ_stress**: Acute stressor presence and HPA-axis activation
- **ρ_affect**: Current emotional valence and intensity (affects InterestValue, SafetyValue)

**Empirical Basis**: Fatigue research (Czeisler & Gooley, 2007), stress physiology (Sapolsky, 2015), and affective science (Gross & John, 2003).

#### ψ_trait: Stable Individual Differences

**Definition**: Enduring personality and cognitive-style traits that modulate preferred constraint–valuation profiles.

$$\psi_{\text{trait}} = \{\tau_{\text{openness}}, \tau_{\text{conscientiousness}}, \tau_{\text{extraversion}}, \tau_{\text{sensitivity}}, \tau_{\text{risk}}\}$$

where:
- **τ_openness**: Openness to experience (high → higher InterestValue; low → preference for SafetyValue)
- **τ_conscientiousness**: Organization preference (high → demands for orderly affordance density; low → tolerance for chaos)
- **τ_extraversion**: Social stimulation preference (high → elevated social-cue-density tolerance; low → overstimulation risk)
- **τ_sensitivity**: Sensory-processing sensitivity (high Highly Sensitive Person trait → lower affordance-density tolerance)
- **τ_risk**: Risk tolerance and loss aversion (high → elevated arousal tolerance; low → heightened threat sensitivity)

**Empirical Basis**: Personality psychology and individual-differences literature (Costa & McCrae, 1992; Aron et al., 2012).

---

## 2. HOW ψ MODULATES EACH CVA LAYER

### 2.1 Layer 1: Constraints with Subject Parameterization

**Standard CVA constraint layer**:

$$\mathbf{c} = f(\mathbf{x}; \boldsymbol{\theta})$$

where **c** is the constraint vector (8 dimensions) and **θ** are perceptual parameters.

**Subject-parameterized constraint layer**:

$$\mathbf{c} = f(\mathbf{x}; \boldsymbol{\theta}(\psi))$$

The mapping **θ(ψ)** is the key innovation. It specifies how each component of ψ calibrates the 8 constraints:

| Constraint | Affected By | Modulation Mechanism |
|-----------|------------|---------------------|
| **ProcessingCost(scene)** | ψ_neuro, ψ_exp, ψ_state | Attention-allocation efficiency; sensory filtering. ADHD → higher costs (reduced sustained attention). Architect → lower costs (domain expertise). Fatigue → higher costs (reduced working memory). |
| **LoadRate(scene, time)** | ψ_neuro, ψ_dev, ψ_state | Information integration speed. Aging → slower LoadRate (delayed multisensory binding). Autism → altered LoadRate (temporal binding window widened). Stress → accelerated LoadRate (threat-driven scanning). |
| **PredictionError(scene)** | ψ_neuro, ψ_culture, ψ_exp | Mismatch between model and reality. PTSD → amplified PredictionError (hypervigilant discrepancy detection). Architect → attenuated PredictionError (rich internal model). Japanese holistic processing → different error signature (global mismatch vs. local feature mismatch). |
| **ControlEfficacy(action, env)** | ψ_neuro, ψ_dev, ψ_trait | Perceived ability to influence environment. Older adults → reduced ControlEfficacy (motor slowing, joint limitations). Gifted → elevated ControlEfficacy (rapid model learning). Low conscientiousness → reduced ControlEfficacy (planning deficits). |
| **AffordanceDensity(scene)** | ψ_culture, ψ_trait, ψ_exp | Density of perceivable action opportunities. Japanese aesthetics (Ma) → lower preferred density. High conscientiousness → higher tolerance for complex affordances. Gifted → perceives more abstract affordances. Children → perceives primarily motor affordances. |
| **SocialCueDensity(scene)** | ψ_culture, ψ_neuro, ψ_trait | Density of human presence, faces, dialogue cues. Collectivist cultures → higher comfortable density. Autism → overstimulation at lower densities (atypical social salience weighting). Extraversion → higher tolerance. |
| **MultisensoryCoherence(scene)** | ψ_neuro, ψ_culture, ψ_dev | Degree of synchrony across sensory modalities. Autism → altered multisensory integration (Markram & Markram, 2010) → different coherence signature. Aging → delayed binding windows → lower coherence even when objectively synchronized. Japanese aesthetic tradition values asynchronous/liminal coherence (ma). |
| **NarrativeCoherence(scene, context)** | ψ_culture, ψ_neuro, ψ_exp, ψ_trait | Story-like coherence of spatial/temporal sequence. Collectivist cultures → family/community narratives; individualist → personal achievement narratives. Autism → detail-oriented narratives; ADHD → fragmented narrative structure. Openness to experience → preference for complex narratives. |

### 2.1.1 Two-Tier Constraint Architecture

To formalize the universality claim while accounting for ψ-modulation, we split constraints into two tiers:

**Tier 1: Perceptual Primitives (Universal)**

Tier 1 constraints reflect hard-wired neural mechanisms preserved across healthy neurodevelopment:

$$\mathbf{c}_{\text{Tier 1}} = f_{\text{universal}}(\mathbf{x})$$

Examples:
- **Edge detection**: Gabor filtering via primary visual cortex (V1); same across cultures and neurotypes
- **Motion detection**: MT/V5 motion energy; preserved in ADHD, ASD, older age
- **Figure–ground segregation**: Lateral inhibition and grouping principles; robust across populations
- **Luminance contrast**: Early sensory transduction; affected by aging (reduced contrast sensitivity) but not structurally altered

Tier 1 is **invariant with respect to ψ** except for aging-related and severe neurological changes.

**Tier 2: Interpretive Constraints (ψ-Calibrated)**

Tier 2 constraints are derived from Tier 1 and modulated by task context, learned models, and ψ:

$$\mathbf{c}_{\text{Tier 2}} = \mathbf{g}(\mathbf{c}_{\text{Tier 1}}; \boldsymbol{\theta}(\psi))$$

Examples:
- **ProcessingCost**: Tier 1 input is raw feature complexity; Tier 2 applies ψ-dependent attention weights
- **PredictionError**: Tier 1 input is absolute discrepancy; Tier 2 applies learned model expectations (which differ by expertise, culture, neurotype)
- **SocialCueDensity**: Tier 1 input is face/voice detection (relatively universal); Tier 2 applies social salience weighting (which differs by culture, autism, extraversion)
- **NarrativeCoherence**: Tier 1 input is temporal/causal sequences; Tier 2 applies culturally-learned narrative templates

**Formal decomposition**:

$$\mathbf{c} = [\mathbf{c}_{\text{Tier 1}}, \mathbf{c}_{\text{Tier 2}}(\psi)]$$

This structure preserves universality of perception while allowing principled ψ-modulation of interpretation.

### 2.2 Layer 2: Valuations with Culture-Selected Structures

**Standard CVA valuation layer** (culture-agnostic):

$$v_i = V_i(\mathbf{c}; g, \tau, \kappa), \quad i \in \{1, \ldots, 9\}$$

The 9 valuations are: SafetyValue, InterestValue, RestorationValue, StatusValue, BelongingValue, IdentityCongruenceValue, AutonomySupportValue, CompetenceSupportValue, RelatednessSupportValue.

**Subject-parameterized valuation layer** (culture and neurotype-aware):

$$\mathbf{v}(\psi) = V(\mathbf{c}; g(\psi), \tau(\psi), \boldsymbol{\kappa}(\psi_{\text{culture}}, \psi_{\text{neuro}}))$$

Two critical differences:

1. **κ(ψ) selects the valuation STRUCTURE**, not just weights
2. **g(ψ) and τ(ψ)** parameterize gain and timescale for each valuation

#### 2.2.1 Valuation Structure Variants

The 9-dimensional Western-centric valuation space may not be universally decomposable. Different cultures select structurally different axes.

**Variant 1: Western Individualist (κ_self = "independent"; κ_social = "egalitarian")**

$$\mathbf{v}_{\text{Western}} = [V_{\text{Safety}}, V_{\text{Interest}}, V_{\text{Restoration}}, V_{\text{Status}}, V_{\text{Belonging}}, V_{\text{Identity}}, V_{\text{Autonomy}}, V_{\text{Competence}}, V_{\text{Relatedness}}]$$

All 9 dimensions are orthogonal and independently weighted.

**Variant 2: Japanese Collectivist with Amae (κ_self = "interdependent"; κ_social = "hierarchical-secure")**

Replace AutonomySupportValue with **AmaeValue** (secure dependence on benevolent authority):

$$\mathbf{v}_{\text{Japanese}} = [V_{\text{Safety}}, V_{\text{Interest}}, V_{\text{Restoration}}, V_{\text{Status}}, V_{\text{Belonging}}, V_{\text{Identity}}, V_{\text{Amae}}, V_{\text{Competence}}, V_{\text{Relatedness}}]$$

Additionally, introduce **MaValue** (positive valuation of emptiness, liminality, and negative space), which is orthogonal to the Western space (Barrett et al., 2016 on cultural emotion construction).

Structural implication: The constraint vector must include **AestheticClosure** (degree of spatial completion) as distinct from **AffordanceDensity** (action opportunities), because Ma is about perceptual openness independent of action density.

**Variant 3: West African Collectivist with Àṣà (κ_self = "relational"; κ_social = "collective dignity")**

The dimensions StatusValue, BelongingValue, IdentityCongruenceValue, and RelatednessSupportValue collapse into a single inseparable **ÀṣàValue** (collective social dignity and shared humanity), rather than being independently optimizable (Kéré, 2023, on African spatial participation; Mbembe, 2015, on shared social order).

$$\mathbf{v}_{\text{W.African}} = [V_{\text{Safety}}, V_{\text{Interest}}, V_{\text{Restoration}}, V_{\text{Àṣà}}, V_{\text{Autonomy}}, V_{\text{Competence}}]$$

Structural implication: Design decisions that improve one dimension (e.g., StatusValue) cannot be decoupled from the others; participatory co-design is architecturally necessary, not optional.

**Variant 4: Indian with Rasa and Dharma Integration (κ_self = "dharmic"; κ_social = "hierarchical-cosmic")**

Rather than 9 separable valuations, Rasa (holistic emotional-aesthetic states) and Dharma (cosmic/social rightness) reframe the entire decomposition. The valuations cluster around:

$$\mathbf{v}_{\text{Indian}} = [V_{\text{Rasa}}, V_{\text{Dharma}}, V_{\text{Belonging}}, V_{\text{Competence}}]$$

where RasaValue is an irreducible holistic aesthetic-emotional state (not decomposable into safety + interest + restoration), and DharmaValue captures alignment with social/cosmic order (Doshi, 1989, on spatial rhythm and cosmic order in Indian modernism).

**Meta-Principle**: Rather than assuming the 9-dimensional space is universal and merely re-weighting, the framework accommodates **structurally orthogonal cultures** where different decompositions are epistemically justified (Barrett et al., 2016; Kitayama & Markus, 2010).

#### 2.2.2 Neurotype-Specific Valuation Modulation

Beyond culture, neurotype affects both valuation weights and, in some cases, structural sensitivity thresholds.

| Neurotype | Valuation Changes | Mechanism |
|-----------|------------------|-----------|
| **PTSD** | SafetyValue threshold ↓ (hyperactivation); PredictionError gain ↑; InterestValue suppressed by threat | Amygdala sensitization; altered thalamic gating (van der Kolk, 2014) |
| **Autism** | SocialCueDensity constraint interpreted differently → BelongingValue/RelatednessSupportValue weights ↓; CompetenceSupportValue ↑ (domain mastery over social affiliation) | Atypical social reward circuitry; enhanced local detail processing (Markram & Markram, 2010) |
| **ADHD** | InterestValue dominates (seeking novelty/stimulation); ControlEfficacy ↓ if external structure absent | Altered dopamine regulation in reward system; reduced sustained attention allocation |
| **Depression** | AnhedoiaSignature: InterestValue ↓, RestorationValue ↓, CompetenceSupportValue ↓ globally; RuminationBias ↑ (NarrativeCoherence searches for threat-confirming interpretations) | Reduced ventral striatum activation; altered valuation computation in vmPFC |
| **Bipolar (Manic)** | InterestValue ↑↑, ControlEfficacy ↑↑ (inflated), StatusValue ↑; SocialCueDensity tolerance ↑↑; goal-switching velocity ↑ | Elevated dopamine and reduced monoamine oxidase; prefrontal–striatal disinhibition |
| **Bipolar (Depressed)** | Same profile as depression | Opposite neurochemical state |
| **Anxiety Disorders** | SafetyValue sensitivity ↑; threat-related PredictionError amplification; ControlEfficacy ↓ (learned helplessness) | Amygdala hyperactivity; impaired prefrontal inhibition; elevated anterior insula interoception |
| **Alzheimer's/Dementia** | SpatialCohesionValue ↓ (place disorientation); ControlEfficacy ↓ (action planning failure); CompetenceSupportValue ↓ (loss of mastery); familiar-face recognition ↓ | Medial temporal lobe atrophy; hippocampal–cortical disconnection; executive function decline |

### 2.3 Layer 3: Policy with State and Neurotype-Dependent Precision

**Standard CVA policy layer**:

$$\mathbf{b} = \boldsymbol{\pi}(\mathbf{v}, \mathbf{c}; \text{precision})$$

where **b** is the behavioral policy (action selection) and precision controls the sensitivity of behavior to value differences.

**Subject-parameterized policy layer**:

$$\mathbf{b}(\psi) = \boldsymbol{\pi}(\mathbf{v}(\psi), \mathbf{c}(\psi); \text{precision}(\psi_{\text{state}}, \psi_{\text{neuro}}, \psi_{\text{trait}}))$$

**Precision modulation**:

$$\text{precision}(\psi) = \beta_0 \cdot \left(1 - \rho_{\text{fatigue}} - \rho_{\text{stress}}\right) \cdot \mathcal{P}_{\text{neuro}}(\psi_{\text{neuro}}) \cdot (1 + \tau_{\text{conscientiousness}})$$

where:
- **β_0**: Baseline precision (typically 1–2 inverse temperature units in softmax policies)
- **ρ_fatigue, ρ_stress**: State reductions (acute stressors reduce precision)
- **P_neuro(ψ_neuro)**: Neurotype-specific precision scaling
  - ADHD: ↓ (higher behavioral variability, impulsivity)
  - Alzheimer's: ↓↓ (severe noise in action selection)
  - Autism: ↑ (hypersystematicity, reduced behavioral flexibility)
  - Older adults: ↓ (motor variability, decision noise)
- **(1 + τ_conscientiousness)**: Trait modulation (high conscientiousness → more precise, goal-directed behavior)

**Policy softmax implementation**:

$$\pi(b_j | \mathbf{v}, \mathbf{c}) = \frac{\exp(\text{precision}(\psi) \cdot [V(b_j) - C(b_j)]))}{\sum_k \exp(\text{precision}(\psi) \cdot [V(b_k) - C(b_k)])}$$

where **V(b_j) - C(b_j)** is the net valuation-minus-constraint score for action **j**.

---

## 3. NEUROTYPE-SPECIFIC PROFILES

This section formalizes how each neurotype's ψ-profile translates into constraint and valuation modulations. We focus on conditions with established neural mechanisms and sufficient architectural/environmental literature to enable empirical testing.

### 3.1 PTSD (Post-Traumatic Stress Disorder)

**Neural signature**: Amygdala hyperactivity, thalamic gating dysfunction, reduced vmPFC–amygdala inhibition (van der Kolk, 2014).

**ψ_neuro profile**:
- ν_threat ↑↑↑ (threat threshold reduced by ~50%)
- ν_sensory ↑ (heightened startle responsivity)
- ν_integration ↓ (impaired temporal binding of non-threat contexts)
- ν_reward ↓ (reduced positive affect; anhedonia in non-safety contexts)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| PredictionError | ↑↑ | Unexpected stimuli trigger disproportionate amygdala response; amplitude scales with trauma-relevance |
| SafetyValue | ↓↓ (threshold) | SafetyValue activates only when threats are fully eliminated; partial safety is insufficient |
| ProcessingCost | ↑ | Hypervigilance increases attentional load even for threat-irrelevant features |
| LoadRate | ↑ | Rapid threat-scanning accelerates temporal processing |
| ControlEfficacy | ↓ | Learned helplessness; perception that environmental control is limited |

**Valuation modulations**:

$$V_{\text{Safety}}^{\text{PTSD}} = V_{\text{Safety}}(\mathbf{c}) + 5 \cdot \mathbb{1}[\text{threat present}] + 2 \cdot \mathbb{1}[\text{ambiguity}]$$

(Threat presence and ambiguity both elevate safety demands; a 5× amplification for detected threats, 2× for uncertain cues.)

$$V_{\text{Interest}}^{\text{PTSD}} = 0.3 \cdot V_{\text{Interest}}(\mathbf{c})$$

(Interest suppressed globally due to amygdala-driven attentional bias toward threat.)

$$V_{\text{RestorationValue}}^{\text{PTSD}} \text{ accessible only when } SafetyValue > \text{threshold}_{\text{PTSD}}$$

(Restoration cannot occur without perceptual safety; typical threshold is ~0.8 on [0, 1] scale.)

**Architectural implications**:
- Reduce **PredictionError** through high environmental predictability (routine layout, consistent affordances, minimal surprises)
- Maximize **SafetyValue** through physical security, controlled access, refuge zones
- Avoid **MultisensoryIncoherence** (startle-inducing mismatches between sound, movement, visual)
- Provide **ControlEfficacy** through clear personal agency (choice in micro-environment, accessible exits, communication channels)

**Key references**: van der Kolk (2014), Shin & Liberzon (2010), Rauch et al. (2006) on neuroimaging; Fikretoglu & McCreary (2017) on PTSD in workplace/public space.

---

### 3.2 Autism Spectrum Disorder (ASD)

**Neural signature**: Enhanced local feature processing, atypical multisensory temporal binding (temporal binding window 2–3× wider; Woynaroski et al., 2013), intact or enhanced perceptual discrimination, reduced social reward circuitry (Baron-Cohen & Belmonte, 2005).

**ψ_neuro profile**:
- ν_sensory ↑ (heightened discrimination, reduced inhibition)
- ν_integration: Widened temporal binding window (τ_bind ≈ 500–800ms vs. 200–400ms in typically developing)
- ν_threat: Threat detection intact but context-insensitivity (threat to animals rated equally to threat to humans)
- ν_social: Social-cue salience ↓ (faces and voices not preferentially filtered); mentalizing slower
- ν_reward: Reduced social reward; enhanced object/domain-specific reward

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| MultisensoryCoherence | ↓↓ | Widened binding window; asynchronies that unnoticed by others perceived as incoherent |
| SocialCueDensity | Perceived differently | Raw count same, but salience ↓; social density doesn't "feel crowded" in same way, but auditory/visual sensory crowding ↑ |
| ProcessingCost | ↑ (for social navigation) | Social inference requires explicit computation; less automated than in typical development |
| AffordanceDensity | Perceived differently | Detail-oriented perception reveals affordances invisible to others; density may feel higher (more things to attend to) |
| PredictionError | Atypical signature | Prediction error driven by perceptual detail, not social expectancy violation |

**Valuation modulations**:

$$V_{\text{CompetenceSupportValue}}^{\text{ASD}} \gg V_{\text{RelatednessSupportValue}}^{\text{ASD}}$$

(Mastery and domain expertise prioritized over social affiliation.)

$$V_{\text{BelongingValue}} \text{ and } V_{\text{RelatednessSupportValue}} \text{ decoupled from } V_{\text{SocialCueDensity}}$$

(Presence of others ≠ belonging; belonging emerges through shared interest/expertise, not proximity.)

$$V_{\text{RestorationValue}} \text{ maximized in low-stimulation environments (sensory-filtered)}$$

(Restoration occurs through sensory relief, not social company; often requires solitude.)

**Architectural implications**:
- Provide **sensory-controlled zones**: Reduced auditory crowding, visual noise filtering, adjustable lighting
- Enable **sustained attention**: Minimal interruptions; spaces that support focused, deep engagement
- Design **detail richness for exploration**: Environmental complexity is not a burden but an invitation (opposite of PTSD)
- Reduce social-navigation load: Clear affordances, explicit signage, predictable movement patterns
- Support **special interests**: Dedicated expertise-aligned spaces (e.g., library sections for autistic children's specific interests)

**Key references**: Markram & Markram (2010) on Intense World Theory; Woynaroski et al. (2013) on temporal binding windows; Baron-Cohen & Belmonte (2005) on local processing bias; Honea & Schaffer (2019) on sensory modulation in autism.

---

### 3.3 ADHD (Attention-Deficit/Hyperactivity Disorder)

**Neural signature**: Reduced dopamine (especially in striatum and prefrontal cortex); reduced sustained attention allocation; increased sensitivity to reward proximity and magnitude; impaired inhibition of prepotent responses (Volkow et al., 2009).

**ψ_neuro profile**:
- ν_reward ↑↑ (heightened salience of immediately available rewards)
- ν_integration ↓ (poor sustained attention; temporal binding of distant goals compromised)
- ν_threat: Variable (inattentional blindness to threat vs. hyperresponsivity depending on reward context)
- ν_learning: ↑ (faster associative learning, especially reward-driven)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| InterestValue (Constraint?) | ↑↑ (sought maximally) | Dopaminergic reward system hypersensitive to novelty and stimulation |
| ProcessingCost | ↓ (ignored) | Difficult to sustain attention to cost; skipped in favor of immediate reward |
| LoadRate | ↑ (variable) | Attention switches rapidly across multiple streams (high when engaged, low when disinterested) |
| ControlEfficacy | Effort-dependent | Clear, immediate feedback → high efficacy; delayed/abstract consequences → low efficacy |
| AffordanceDensity | Preferred higher | More opportunities for immediate action and stimulation |

**Valuation modulations**:

$$V_{\text{InterestValue}}^{\text{ADHD}} = 3–4 \cdot V_{\text{InterestValue}}^{\text{typical}}$$

$$\text{discount factor for delayed rewards: } \gamma^{\text{ADHD}} = 0.7–0.8 \text{ (vs. 0.95 typical)}$$

(Extreme temporal discounting: future consequences heavily discounted.)

$$V_{\text{CompetenceSupportValue}}^{\text{ADHD}} \text{ maximized with immediate, frequent feedback}$$

(Competence felt only with rapid success signaling; abstract mastery insufficient.)

**Architectural implications**:
- Provide **progressive stimulation**: Graduated complexity that maintains interest without excessive load
- Enable **immediate feedback loops**: Actions with visible, rapid consequences
- Support **movement and kinesthetic engagement**: Static, sedentary environments exacerbate symptoms
- Structure **choice within constraints**: Multiple options (high affordance density) but bounded (not overwhelming)
- Minimize **cost-benefit tradeoffs**: Make the low-cost path also the high-interest path (opposite of PTSD)

**Key references**: Volkow et al. (2009) on dopamine system dysfunction; Castellanos & Tannock (2002) on ADHD neurobiology; Nigg et al. (2005) on inhibition deficits; Patros et al. (2016) on temporal discounting in ADHD.

---

### 3.4 Older Adults (Age 65+)

**Neural signature**: General slowing of processing; reduced contrast sensitivity and dark adaptation (retinal); increased sensory noise; delayed multisensory binding; reduced prefrontal–striatal dopamine; preserved crystallized intelligence (Salthouse, 2009; Owsley, 2011).

**ψ_dev profile** (within older-adult range):
- m_visual ↓ (contrast: 65-year-old requires ~3× contrast of 25-year-old; visual field narrowing)
- m_motor ↓ (slower movement; reduced proprioceptive precision; increased fall risk)
- m_exec ↓ (slower decision-making; reduced working memory; but preserved semantic knowledge)
- Preserved expertise and pattern recognition (domain-specific knowledge intact or enhanced)

**ψ_state profile**:
- ρ_fatigue ↑ (reduced sleep quality; increased daytime somnolence)
- ρ_stress sensitivity ↑ (slower recovery from acute stress)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| ProcessingCost | ↑ | Reduced attentional efficiency; dual-task performance impaired |
| LoadRate | ↓ | Slower integration of sensory information; delayed decision-making |
| ControlEfficacy | ↓ | Motor slowing, joint restrictions, learned caution reduce perceived control |
| MultisensoryCoherence | ↓ | Wider temporal binding window (~400–600ms vs. 200–300ms); asynchronies more perceptible |
| SocialCueDensity | Interpreted differently | Presbyacusis (high-frequency hearing loss) makes speech in crowds more difficult; social density feels more cognitively demanding |

**Valuation modulations**:

$$V_{\text{SafetyValue}}^{\text{older}} = 1.5–2.0 \cdot V_{\text{SafetyValue}}^{\text{younger}}$$

(Elevated safety concerns due to fall risk, cognitive load, reduced recovery capacity.)

$$V_{\text{ControlEfficacy}} \text{ threshold reduced by ~30%}$$

(Perceived control becomes harder to achieve; environments must provide very clear agency.)

$$V_{\text{InterestValue}} \text{ weighted toward familiar/mastered domains}$$

(Preference for expert domains where ProcessingCost is low; novelty-seeking reduced but deep engagement in expertise maintained.)

$$V_{\text{RestorationValue}} \text{ includes rest-dependent recovery (must include nap/rest spaces)}$$

(Restoration requires biological recovery time, not just sensory relief.)

**Architectural implications**:
- **High contrast signage and lighting** (minimum 3:1 contrast ratio; warm, flicker-free lighting to reduce glare sensitivity)
- **Reduced navigation complexity**: Clear wayfinding, logical spatial organization, minimal decision points
- **Rest and recovery zones**: Seating, nap spaces, toilets (frequent need due to medications, incontinence risk)
- **Safety through redundancy**: Handrails, non-slip surfaces, clear hazards (not hidden)
- **Sensory calibration**: Reduced background noise, visual clarity, no rapid visual flicker
- **Slower-paced environments**: Avoid rushing; allow time for sensory integration and decision-making

**Key references**: Owsley (2011) on aging vision; Salthouse (2009) on cognitive aging; Schneider & Pichora-Fuller (2000) on aging and multisensory perception; Lawton & Nahemow (1973) on person–environment fit in older adults.

---

### 3.5 Children (Ages 5–12): Developing Systems

**Neural signature**: Ongoing prefrontal development (synaptic pruning, myelination through early teens); intact sensory systems; rapid learning and perceptual calibration; theory-of-mind development (Blakemore & Choudhury, 2006).

**ψ_dev profile** (age 5–8 vs. 9–12 differs markedly):

| Aspect | Age 5–8 | Age 9–12 |
|--------|---------|-----------|
| **Executive Function** | Minimal; limited planning | Emerging; 3–4 step planning possible |
| **Theory of Mind** | Egocentric; others' mental states poorly modeled | Developing perspective-taking; social reasoning improving |
| **Spatial Reasoning** | Ego-centric navigation; landmark-based | Allocentric maps emerging; route memory developing |
| **Temporal Reasoning** | Minutes to hours; "now vs. later" | Hours to days; delayed consequences begin to matter |
| **Affordance Perception** | Motor-bound (what I can do); primarily physical | Expanding to social and abstract affordances |

**Constraint modulations**:

| Constraint | Modulation | Age Effect |
|-----------|-----------|-----------|
| ProcessingCost | ↑ (age 5–8); ↓ (age 9–12) | Younger children more easily overloaded; improving with age |
| ControlEfficacy | Limited (age 5–8); growing (age 9–12) | Younger: helplessness in complex situations; older: emerging agency |
| SocialCueDensity | High tolerance (peer play requires crowds) | Age-appropriate social engagement scales with density |
| AffordanceDensity | Perceived primarily as motor affordances (age 5–8); expanding to cognitive (age 9–12) | Younger: climbing, running, hiding; older: puzzles, building, social games |
| NarrativeCoherence | Literal, concrete (age 5–8); increasingly abstract (age 9–12) | Story comprehension requires explicit cause-effect; metaphor develops later |

**Valuation modulations**:

$$V_{\text{CompetenceSupportValue}}^{\text{children}} \gg V_{\text{RelatednessSupportValue}}$$

(Mastery through play and learning dominates; social connection secondary to achievement and exploration.)

$$V_{\text{PlayValue}} \text{ (implicit in InterestValue and CompetenceSupportValue)}$$

(Play is the primary mode of learning and valuation; must be centrally supported, not peripheral.)

$$V_{\text{SafetyValue}} \text{ includes caregiver proximity (BelongingValue cannot separate from caregiver)}$$

(Unlike adults, children's SafetyValue is directly linked to caregiver presence; separation increases SafetyValue threshold.)

**Architectural implications**:
- **Multi-sensory, graduated complexity**: Spaces that scale learning (simple exploration → complex problem-solving)
- **Play-centered design**: Affordances explicitly designed for play (not just incidental)
- **Caregiver visibility and proximity**: Spaces where children can explore while caregivers maintain oversight
- **Sensory safety**: No unexpected stimuli; clear sightlines to caregivers
- **Age-segregated zones**: 5–8 year-olds need simpler, more supervised spaces; 9–12 year-olds ready for more autonomy
- **Narrative scaffolding**: Spatial sequences that tell stories (e.g., hospital wayfinding as "hero's journey")

**Key references**: Blakemore & Choudhury (2006) on adolescent brain development; Pellegrini & Smith (1998) on play; Hart (1979) on children's spatial behavior; Spencer & Blades (2006) on wayfinding in children.

---

### 3.6 Alzheimer's Disease and Dementia

**Neural signature**: Hippocampal atrophy (impaired spatial memory and contextual binding); entorhinal cortex degeneration; widespread cortical amyloid; executive function decline (Braak staging; Selkoe, 2002).

**ψ_neuro profile**:
- ν_integration ↓↓ (severe impairment in binding; context-dependent memory loss)
- ν_learning ↓↓ (new learning nearly impossible)
- ν_spatial: ↓↓ (place disorientation; hippocampal dysfunction)
- ν_executive: ↓ (planning, impulse control, multi-step reasoning)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| SpatialCohesion (implicit in constraints) | ↓↓ | Hippocampal memory failure; place becomes unmoored from identity |
| ControlEfficacy | ↓↓ | Inability to execute plans; learned helplessness from repeated failure |
| ProcessingCost | ↑ | Any novel environment overwhelms; relies on automatized, familiar routes |
| PredictionError | ↑ | Constant disorientation; environment perpetually unpredictable |
| NarrativeCoherence | ↓↓ | Loss of autobiographical narrative; present moment disconnected from past |

**Valuation modulations**:

$$V_{\text{SafetyValue}}^{\text{Alzheimer}} = \text{high only with familiar caregivers; unfamiliar environments elevate threat indefinitely}$$

$$V_{\text{ControlEfficacy}} \text{ near zero; agency experience minimal}$$

$$V_{\text{IdentityCongruenceValue}} \text{ preserved for embedded, autobiographical roles (e.g., "parent," "gardener")}$$

(Identity recalled through familiar objects and activities, not explicit reasoning.)

$$V_{\text{BelongingValue}} \text{ highly dependent on familiar person presence}$$

(Social belonging primarily through recognition of specific individuals, not general social spaces.)

**Architectural implications**:
- **Wayfinding through familiarity**: Consistent, unchanging layouts; familiar landmarks (e.g., resident's room, garden used for decades)
- **Autobiographical anchors**: Objects, activities, spaces that trigger preserved identity-related memories
- **Caregiver integration**: Design for continuous caregiver presence; no "independent navigation" expected
- **Wandering design**: Safe, looped outdoor spaces allowing movement without risk of getting lost
- **Reduced novelty**: Avoid rearrangement; consistency across days, staff, routines
- **Sensory continuity**: Use familiar music, smells, tactile cues to trigger memory and orientation

**Key references**: Selkoe (2002) on Alzheimer's pathology; Calkins (2009) on design for dementia care; Marquardt & Schmieg (2009) on wayfinding in dementia environments; Cohen & Weisman (1991) on therapeutic environments for dementia.

---

### 3.7 Depression and Anhedonia

**Neural signature**: Reduced ventral striatum activation (reward processing); elevated amygdala reactivity to threat/loss; prefrontal cortex hypoactivity (goal-directed behavior, emotional regulation); altered default-mode network (ruminative thinking; Mayberg, 2003).

**ψ_neuro profile**:
- ν_reward ↓↓ (anhedonia: reward signals attenuated by ~50%)
- ν_threat: ↑ (bias toward threat/loss over reward/gain)
- ν_learning: ↓ (slower positive reinforcement learning)
- ν_executive: ↓ (effortful goal-directed behavior costly)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| InterestValue | ↓ | Anhedonic flattening; environments that excite others feel neutral |
| RestorationValue | ↓ (paradoxically) | Rest does not restore; rumination depletes energy further |
| CompetenceSupportValue | ↓ | Learned helplessness; difficulty experiencing mastery |
| SocialCueDensity | ↓ (tolerance) | Social withdrawal; crowds feel threatening not inviting |
| ProcessingCost | ↑ | Cognitive slowing; decision fatigue and indecision |

**Valuation modulations**:

$$V_{\text{InterestValue}}^{\text{depression}} = 0.3–0.5 \cdot V_{\text{InterestValue}}^{\text{non-depressed}}$$

$$V_{\text{RestorationValue}}^{\text{depression}} \text{ inaccessible without behavioral activation}$$

(Resting does not restore; must combine rest with activity structure to break rumination cycle.)

$$\text{RuminationBias: NarrativeCoherence seeks threat-confirming interpretations}$$

(Environments interpreted pessimistically; minor design flaws become major sources of negative narrative.)

**Architectural implications**:
- **Behavioral activation spaces**: Graduated activity options (from sedentary to engaged), not just rest zones
- **Light and color**: Well-lit, warm environments (light therapy for seasonal/circadian effects)
- **Reduced isolation**: Communal, low-pressure social spaces (not forced socializing)
- **Simple affordances**: Reduced decision load; clear, achievable actions
- **Nature access**: Outdoor views and green spaces (robust depression-reducing effects; Barton & Pretty, 2010)
- **Structure and routine**: Predictable, scaffolded daily patterns (support behavioral activation)

**Key references**: Mayberg (2003) on depression neurobiology; Pizzagalli et al. (2008) on reward processing in depression; Disner et al. (2011) on cognitive bias; Barton & Pretty (2010) on nature and mental health.

---

### 3.8 Anxiety Disorders (Generalized Anxiety, Social Anxiety, Panic)

**Neural signature**: Amygdala hyperactivity; heightened anterior insula interoception (threat-signal amplification); reduced dorsolateral prefrontal cortex inhibition; threat-detection bias (Stein & Stein, 2008).

**ψ_neuro profile**:
- ν_threat ↑↑ (threat threshold reduced)
- ν_sensory ↑ (interoceptive sensitivity: body signals misinterpreted as danger)
- ν_social: Varies (social anxiety: high mentalizing load; generalized: less specific)
- ν_control: ↓ (perceived controllability reduced; anxiety-driven avoidance)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| PredictionError | ↑↑ | Threat-biased prediction; unexpected events interpreted as threats |
| SafetyValue | ↓↓ (threshold) | Safety threshold elevated; only highly controlled environments feel safe |
| ControlEfficacy | ↓ | Avoidance behavior prevents actual experience of control; learned helplessness |
| SocialCueDensity | ↑ (for social anxiety) | Social signals interpreted as evaluation/judgment; crowds threatening |
| ProcessingCost | ↑ | Vigilance-driven attention; costs of monitoring for threat |

**Valuation modulations**:

$$V_{\text{SafetyValue}}^{\text{anxiety}} = 2–3 \cdot V_{\text{SafetyValue}}^{\text{non-anxious}}$$

$$\text{Avoidance behavior: } V_{\text{immediateEscape}} \gg V_{\text{longTermGoals}}$$

(Temporal discounting for threat; immediate escape heavily preferred over future benefits.)

$$V_{\text{ControlEfficacy}} \text{ requires explicit control demonstrations}$$

(Feeling in control requires active mastery experiences, not passive safety.)

**Architectural implications**:
- **Escape routes and choice**: Visible exits, multiple pathways out (autonomy and control)
- **Control demonstration**: Actions with clear, positive effects (e.g., adjustable lighting, temperature, volume)
- **Graduated exposure**: Spaces that allow safe practice with anxiety-triggering contexts (exposure therapy-compatible design)
- **Refuge and monitoring**: Options to withdraw, observe, and re-engage (not forced confrontation)
- **Predictability and clarity**: Transparent sightlines, clear affordances, no surprises
- **Slow environmental pace**: Avoid rushing; allow time for anxiety regulation

**Key references**: Stein & Stein (2008) on anxiety neurobiology; Craske et al. (2008) on exposure therapy; Hofmann & Smits (2008) on cognitive-behavioral approaches; Foa et al. (2007) on anxiety disorders.

---

### 3.9 Bipolar Disorder (Manic and Depressed Phases)

**Neural signature**: Emotion-regulation circuits unstable; prefrontal–amygdala–striatal coupling fluctuates; dopaminergic drive high in mania, low in depression (Phillips & Kupfer, 2013).

**ψ_neuro profile** (state-dependent):

**Manic Phase**:
- ν_reward ↑↑↑ (dopamine elevation; reward sensitivity amplified)
- ν_goal_switching ↑↑ (rapid shifts in motivation)
- ν_impulse_control ↓ (reduced inhibition of prepotent responses)
- ν_threat: ↓ (threat detection attenuated; risk-taking increased)

**Depressed Phase**:
- ν_reward ↓↓ (anhedonia; same as unipolar depression)
- ν_threat ↑ (threat sensitivity increased)
- ν_goal_switching ↓ (perseveration on negative goals/rumination)

**Constraint and Valuation Modulations**:

| Phase | InterestValue | StatusValue | ControlEfficacy | SafetyValue | Precision |
|-------|---------------|-----------|-----------------|-----------|-----------|
| **Manic** | ↑↑↑ (stimulation-seeking) | ↑↑↑ (grandiosity) | ↑↑↑ (inflated) | ↓ (risk-taking) | ↓ (impulsive) |
| **Depressed** | ↓ (anhedonic) | ↓ (worthlessness) | ↓ (helplessness) | ↑ (threat-sensitive) | ↓ (slow) |

**Architectural implications**:

**For Manic Phases**:
- Provide high-stimulation, goal-rich environments (satisfy InterestValue demands)
- Multiple simultaneous affordances (support rapid goal-switching)
- **Limit overstimulation risk**: Graduated access to high-arousal activities (not unlimited)
- Clear structure and boundaries (prevent complete goal scatter)

**For Depressed Phases**:
- Same as depression (see Section 3.7)
- **Maintain consistency across phases**: Design must support both states without requiring phase-specific intervention

**Key references**: Phillips & Kupfer (2013) on bipolar neurobiology; Strakowski et al. (2012) on emotion processing in bipolar disorder; Johnson et al. (2008) on behavioral activation in bipolar depression.

---

### 3.10 Giftedness and High Cognitive Ability

**Characteristics**: Advanced processing speed, working memory, reasoning; potentially higher Goldilocks optimal complexity; reduced tolerance for under-stimulation; possible perfectionism and sensitivity traits (Winner, 1996; Renzulli, 1986).

**ψ_neuro and ψ_trait profile**:
- ν_learning: ↑↑ (rapid model building and pattern recognition)
- ν_complexity_tolerance: Shifted higher (Goldilocks sweet spot at higher complexity)
- τ_openness: Often ↑ (greater interest in novel domains)
- τ_conscientiousness: Variable (perfectionism in some; disorganization in others)
- τ_sensitivity: Often ↑ (Gifted-Sensitive-Introvert profile; Aron, 2010)

**Constraint modulations**:

| Constraint | Direction | Mechanism |
|-----------|-----------|-----------|
| ProcessingCost | ↓ (for complex domains) | Rapid model building; abstract complexity is not costly |
| AffordanceDensity | Perceived higher | Abstract and relational affordances visible (beyond motor affordances) |
| InterestValue | ↑ (for complex, novel domains) | Challenge-seeking; boredom aversion drives complexity-seeking |
| CompetenceSupportValue | ↑ (for mastery-relevant domains) | Rapid learning and expertise-building are strong rewarding |
| NarrativeCoherence | ↑ (for abstract narratives) | Ability to construct and follow complex narratives (literal + metaphorical) |

**Valuation modulations**:

$$\text{Goldilocks}_{\text{optimal}}^{\text{gifted}} = \text{Goldilocks}_{\text{typical}} + 1.5–2.0 \sigma$$

(Optimal complexity shifted higher; typical environments under-stimulating.)

$$V_{\text{CompetenceSupportValue}}^{\text{gifted}} \text{ sharply decreases if challenge absent}$$

(Lack of appropriate challenge → boredom → disengagement, even when material is "passing.")

$$V_{\text{IdentityCongruenceValue}} \text{ sensitive to domain match}$$

(Giftedness + mismatch to domain interests → identity conflict; alignment → strong engagement.)

**Architectural implications**:
- **Complexity and depth options**: Multi-layered affordances (surface-level use and deep exploration both possible)
- **Advanced resources and challenge**: Access to high-level materials, equipment, mentorship
- **Autonomy and self-direction**: Control over pacing and depth of engagement (reduced teacher-centered structure)
- **Peer engagement**: Opportunities for collaboration with intellectual peers (BelongingValue around shared interests)
- **Narrative richness**: Spaces and programs that support complex, abstract narratives

**Key references**: Winner (1996) on cognitive characteristics of gifted; Renzulli (1986) on giftedness models; Aron (2010) on gifted-sensitive people; Kirsh & Nersissian (2022) on optimal cognitive load in design.

---

## 4. TWO-TIER CONSTRAINT FORMALIZATION

### 4.1 Universality of Tier 1

**Claim**: Tier 1 constraints (perceptual primitives) are approximately invariant across typically developing populations and neurotypes, modulated only by sensory development and aging-related decline.

**Tier 1 Constraint Set**:

$$\mathbf{c}_{\text{Tier 1}} = \{c_{\text{edge}}, c_{\text{motion}}, c_{\text{contrast}}, c_{\text{figground}}, c_{\text{coherence}}, c_{\text{symmetry}}\}$$

| Primitive | Neural Mechanism | Across-Population Invariance | Developmental Notes |
|-----------|-----------------|---------------------------|---------------------|
| **Edge detection** | V1 Gabor channels | Highly invariant; present in infants | Myelination complete by age 4–5 |
| **Motion detection** | MT/V5 motion-energy channels | Invariant; preserved in ADHD, ASD, aging | Mature by age 4–5; minimal decline with age |
| **Figure–ground segregation** | Lateral inhibition; grouping principles (Gestalt) | Invariant; robust across neurotypes | Mature by age 6–7 |
| **Luminance contrast** | Photoreceptor transduction; contrast gain control | Invariant in structure; sensitivity ↓ with age (retinal aging) | Age 65+: 2–3× contrast needed |
| **Temporal coherence** | Synchrony detection in multisensory integration | Shifts with development (binding window narrows); stable in adulthood | Binding window: narrowest at age 20–40; widens in infancy and aging |
| **Symmetry detection** | V4 symmetry-selective neurons (Sasaki et al., 2005) | Invariant; preference for symmetry universal across cultures | Mature by age 5–6 |

**Formal Tier 1**:

$$\mathbf{c}_{\text{Tier 1}} = f_{\text{universal}}(\mathbf{x}; a, \nu_{\text{sensory}})$$

where **a** is age and **ν_sensory** captures only aging-related decline (visual contrast sensitivity, hearing loss), not neurotype-specific variations.

### 4.2 Tier 2: Interpretive Constraints Calibrated by ψ

**Claim**: Tier 2 constraints are derived from Tier 1 and task context, modulated by ψ (especially ψ_neuro, ψ_culture, ψ_exp).

**Tier 2 Constraint Set** (the 8 CVA constraints):

$$\mathbf{c}_{\text{Tier 2}} = g(\mathbf{c}_{\text{Tier 1}}, \mathbf{x}; \boldsymbol{\theta}(\psi), \text{task context})$$

Examples of Tier 1 → Tier 2 transformations:

| Tier 2 Constraint | Tier 1 Input | ψ-Modulation |
|------------------|-------------|--------------|
| **ProcessingCost** | c_contrast, c_motion, c_edge (combined sensory load) | Multiplied by attention-allocation efficiency θ_attention(ψ_neuro, ψ_exp) |
| **LoadRate** | c_temporal_coherence (synchrony across streams) | Temporal integration constant τ_integrate(ψ_neuro, ψ_dev) modulates speed |
| **PredictionError** | c_edge, c_motion mismatch vs. learned model | Learned model depends on ψ_exp, ψ_culture, ψ_neuro (threat bias) |
| **AffordanceDensity** | c_symmetry, c_figground (object/action parsing) | Affordance detection threshold θ_aff(ψ_exp, ψ_trait_openness); abstract affordances visible to gifted |
| **SocialCueDensity** | c_face_detection, c_voice_detection (Tier 1 social primitives) | Social salience weighting w_social(ψ_culture, ψ_neuro); varies 2–5× across neurotypes |
| **MultisensoryCoherence** | c_temporal_coherence (across modalities) | Binding-window tolerance τ_bind(ψ_neuro, ψ_dev); autism/PTSD/aging: wider tolerance |
| **NarrativeCoherence** | c_temporal_sequence, c_figground (event parsing) | Narrative template selection κ_narrative(ψ_culture, ψ_trait); literal vs. metaphorical interpretation |

**Formal Tier 2**:

$$\mathbf{c}_{\text{Tier 2, i}} = g_i(\mathbf{c}_{\text{Tier 1}}; \boldsymbol{\theta}_i(\psi))$$

Each Tier 2 constraint has a ψ-parameterized function.

### 4.3 Unified Constraint Vector

$$\mathbf{c}(\psi) = [\mathbf{c}_{\text{Tier 1}}, \mathbf{c}_{\text{Tier 2}}(\psi)]$$

This structure makes the universality claim explicit: Tier 1 is independent of ψ (except aging), while Tier 2 is fully ψ-dependent. The decomposition clarifies which aspects of architectural design should generalize universally (perceptual clarity, contrast, visibility) vs. which must be culturally/neurotype-specific (what counts as "optimal complexity," what counts as "coherent").

---

## 5. INTEGRATION WITH ATLAS (Population-Transfer Methods)

The ATLAS framework (used in BN_graphical for Bayesian network updates across populations) currently employs a population-transfer factor:

$$\delta(\text{pop}_{\text{source}}, \text{pop}_{\text{target}}) \in [0, 1]$$

which discounts evidence learned in one population when transferring to another.

**Connection to ψ**:

The parameter space ψ provides the principled basis for computing δ. Rather than treating δ as an opaque scalar, we now have:

$$\delta(\text{pop}_{\text{source}}, \text{pop}_{\text{target}}) = \mathcal{F}(\psi_{\text{source}}, \psi_{\text{target}})$$

where **F** is a function mapping differences in ψ to evidence-discount factors.

**Specific mapping**:

$$\delta = \prod_{j} \delta_j(\psi_j^{\text{source}}, \psi_j^{\text{target}})$$

where each component of ψ contributes independently to the discount:

| Component | Discount Rule |
|-----------|---------------|
| **ψ_culture** | δ_culture = 0.5 if κ_self, κ_social, κ_aesthetics differ markedly (e.g., individualist → collectivist); 0.95 if minor differences |
| **ψ_neuro** | δ_neuro = 0.3–0.8 depending on ν differences (PTSD vs. typical: 0.3; depression vs. typical: 0.6; old vs. young: 0.7) |
| **ψ_dev** | δ_dev = 0.4 if age span >20 years; 0.9 if <5 years |
| **ψ_exp** | δ_exp = 1.0 if e_domain same; 0.8 if related; 0.5 if unrelated |
| **ψ_state** | δ_state: Ignored if state normalized (fatigue controlled); 0.7 if source under acute stress, target not |
| **ψ_trait** | δ_trait: Minimal (personality stable; 0.95 if trait spread >1 SD difference) |

**Example**:

Evidence learned in a healthy, young (age 25), Western, non-expert population transferring to an older adult (age 75), non-Western, ADHD population:

$$\delta = 0.95 \cdot 0.6 \cdot 0.4 \cdot 1.0 \cdot 1.0 \cdot 0.95 = 0.22$$

(~78% evidence discount; only 22% of source learning transfers directly.)

This formalizes why architectural design precedents from young Western professionals often fail for elderly populations or neurodivergent users—the evidence base is fundamentally different (δ << 1).

---

## 6. RESEARCH ROADMAP: EMPIRICAL VALIDATION AND GAPS

### 6.1 Neurotype Coverage: Known vs. Unknown

| Neurotype | Architectural Literature | Cognitive Neuroscience | CVA-Specific Studies | Priority |
|-----------|--------------------------|----------------------|---------------------|----------|
| **PTSD** | Moderate (design for trauma-informed care) | Excellent (decades of neuroscience) | 0 (urgent need) | HIGH |
| **ASD** | Growing (sensory-friendly design guides) | Excellent (detailed neural mechanisms) | 0 (urgent) | HIGH |
| **ADHD** | Moderate (school/office design) | Good (dopamine dynamics) | 0 (urgent) | HIGH |
| **Older Adults** | Excellent (gerontological design) | Excellent (aging vision, cognition) | Some work on Goldilocks | MEDIUM |
| **Children (5–12)** | Excellent (pediatric design) | Good (developmental trajectories) | 0 (needs work) | MEDIUM |
| **Alzheimer's/Dementia** | Excellent (dementia-care design) | Excellent (pathology well-understood) | 0 (needs CVA formalization) | MEDIUM |
| **Depression** | Moderate (therapeutic design) | Good (neuroimaging established) | 0 (urgent) | HIGH |
| **Anxiety Disorders** | Growing (trauma-informed overlap) | Good (amygdala/insula mechanisms) | 0 (urgent) | HIGH |
| **Bipolar Disorder** | Minimal (largely absent from architecture lit.) | Good (state-dependent neurobiology) | 0 (urgent) | HIGH |
| **Giftedness/High-IQ** | Minimal (gifted education, not architecture) | Minimal (IQ research, not neurotype specifics) | 0 (exploratory) | LOW-MEDIUM |
| **ADHD + Gifted (2e)** | Rare (twice-exceptional individuals) | Minimal (understudied) | 0 (exploratory) | LOW |

### 6.2 Research Questions by Neurotype

#### PTSD

**Known**:
- Amygdala hyperactivity and thalamic gating dysfunction (van der Kolk, 2014)
- Threat-detection bias and startle hyperreactivity
- Impaired extinction learning (difficulty updating threat models)

**Unknown (CVA-relevant)**:
- How does environmental **PredictionError** amplitude (ratio of expected to actual sensory input) quantitatively affect amygdala activation in PTSD vs. typical?
- Does architectural **ControlEfficacy** (via clear, user-manipulable affordances) reduce threat-monitoring load in PTSD? (Testable: eye-tracking, amygdala fMRI, cortisol levels)
- What is the optimal **SafetyValue** threshold (i.e., how much environmental control/predictability is necessary before RestorationValue becomes accessible)?

**Proposed experiment**:
- Design two versions of a space: High ControlEfficacy (adjustable lighting, clear exits, personal refuge) vs. Low ControlEfficacy (fixed environment, limited choice)
- Expose PTSD participants (n=30) and healthy controls (n=30) to both; measure amygdala activation (fMRI), eye-tracking (vigilance patterns), cortisol, self-report safety
- Predict: PTSD shows 40–50% amygdala reduction in High ControlEfficacy condition; healthy controls show minimal difference
- Data outcome feeds back to θ_control(ψ_PTSD) parameterization

#### ASD

**Known**:
- Widened temporal binding window (Woynaroski et al., 2013)
- Enhanced local feature processing
- Atypical social reward circuitry

**Unknown (CVA-relevant)**:
- How does **MultisensoryCoherence** threshold differ quantitatively (asynchrony tolerance)?
- Does sensory-filtered environment actually reduce **ProcessingCost**, or is it a proxy for reduced social demand? (Disentangle perceptual vs. social load)
- How does **AffordanceDensity** interact with autism: do complex affordances support intense focus (positive) or create overstimulation (negative)?

**Proposed experiment**:
- Design varying multisensory asynchronies (audiovisual sync windows: 0ms, 100ms, 200ms, 400ms)
- Measure perceptual coherence ratings (explicit) and neural synchronization (EEG) in ASD vs. typical
- Predict: ASD shows coherence threshold shifted by ~150–200ms (asynchrony tolerance 2–3× higher)
- Test sensory-density spaces (quiet vs. moderate sensory load) measuring engagement time, cortisol, stress markers

#### Older Adults

**Known**:
- Contrast sensitivity reduced 2–3×; hearing loss (presbyacusis)
- Processing speed decline; multisensory binding window widening
- Preserved expertise and semantic knowledge

**Unknown (CVA-relevant)**:
- Goldilocks curves: Do optimal complexity curves shift with age? (Kirkup & Kirsh, 2024 work suggests yes, but quantification needed)
- What is the interaction between **ProcessingCost** decline and **ControlEfficacy** perception? (Slower processing + reduced control → compounding burden?)
- Does **NarrativeCoherence** in spatial design (e.g., wayfinding stories) compensate for reduced cognitive processing speed?

**Proposed experiment**:
- Measure Goldilocks curves (optimal complexity vs. engagement) in three age groups: 25–35, 55–65, 75+
- Vary environmental complexity (simulated via visual filtering, noise, affordance density) and measure engagement, errors, subjective ease
- Predict: Optimal complexity shifts lower with age (inverted U-curve, peak shifts left); variance increases in oldest group (precision ↓)
- Wayfinding test: Compare explicit wayfinding instructions vs. spatial narrative structure; measure navigation success in older adults

#### Depression

**Known**:
- Reward-processing deficits (ventral striatum hypoactivity)
- Threat bias; rumination (default-mode network hyperactivity)

**Unknown (CVA-relevant)**:
- Can environmental **InterestValue** stimulation (complexity, novelty) overcome anhedonic suppression?
- Does **RestorationValue** through rest alone work, or is behavioral activation (InterstValue + affordances for engagement) necessary?
- What is the effect of **NarrativeCoherence** (positive spatial narrative) on rumination reduction vs. neutral space?

**Proposed experiment**:
- Design two spatial conditions: (A) Rest-focused (soft, quiet, visual simplicity); (B) Activation-focused (graduated complexity, engagement affordances, light/color)
- Measure depressed participants (n=40) across conditions: anhedonia level (TEDS), engagement time, rumination (thought sampling), mood
- Predict: Activation-focused space shows greater engagement and mood improvement; rest-alone space maintains anhedonia
- fMRI during spatial exploration: predict ventral striatum activation higher in Activation-focused condition

---

### 6.3 Cross-Neurotype Comparative Studies

**Study**: Optimal complexity (Goldilocks) across 6 neurotypes + typical development

- Design scalable visual-complexity stimuli (from minimal to cluttered)
- Measure engagement (eye-tracking, dwell time), cognitive load (N-back + visual search), affect (fEMG, self-report) across neurotypes
- Predict: ADHD shifts optimal complexity higher; autism/PTSD shift lower; depression flattens curve (anhedonia reduces engagement across all complexities); gifted shifted higher; older adults shifted lower

**Data outcome**: Quantitative remapping of θ_cost(ψ) across all neurotypes, enabling multi-population CVA parameter fitting.

---

### 6.4 Cultural Validation Studies

**Study**: Valuation-structure differences (Japan vs. USA vs. West Africa)

- Design spaces instantiating different CVA variants (Western 9-dim, Japanese Amae+Ma, West African Àṣà)
- Recruit culturally embedded populations (long-term residents, cultural experts)
- Measure valuation weights and preferences (e.g., "How important is individual autonomy vs. secure dependence in this space?"); implicit cultural values via IAT (Implicit Association Test)
- Predict: Japanese participants prefer AmaeValue+Ma-structured spaces; West African prefer Àṣà-unified spaces; Western prefer autonomy + individual achievement

**Data outcome**: Calibrate κ(ψ_culture) and justify structural decomposition choices.

---

### 6.5 Individual Differences (ψ_trait, ψ_state) Validation

**Study**: Personality modulation of constraint sensitivity

- Large-sample study (n=100+): Measure Big Five personality traits (especially openness, conscientiousness, extraversion)
- Expose to multiple spatial conditions (high vs. low complexity, high vs. low social density, high vs. low affordance density)
- Predict: High openness → higher InterestValue weights, higher optimal complexity; high conscientiousness → lower tolerance for disarray; high extraversion → higher SocialCueDensity tolerance

**Study**: Acute state modulation (fatigue, stress, affect)

- Repeated measures within-subject: Same participants across two sessions (one well-rested, one sleep-deprived; one low-stress, one acute stressor)
- Measure constraint sensitivity and policy precision (precision ↓ with fatigue)
- Predict: Fatigue increases ProcessingCost sensitivity; stress amplifies threat-related PredictionError gain

---

## 7. IMPLEMENTATION AND DEPLOYMENT

### 7.1 ψ Assessment Protocol

To operationalize the CVA-ψ framework in practice, designers/researchers must assess relevant ψ components:

**Minimal Assessment** (for initial design):
1. **ψ_culture**: Cultural background, self-construal (individualism–collectivism scale)
2. **ψ_neuro**: Self-reported neurotype diagnosis or screening (ADHD-RS, ASD screening, depression PHQ-9)
3. **ψ_dev**: Age
4. **ψ_trait**: Big Five personality (brief form)

**Comprehensive Assessment** (for precision research):
1. Add **ψ_exp**: Domain expertise (years in field, self-rated mastery)
2. Add **ψ_state**: Fatigue (Epworth Sleepiness Scale), stress (Perceived Stress Scale), affect (PANAS)
3. Add neurotype-specific measures (e.g., autism: Autism Spectrum Quotient; PTSD: PCL-5; depression: BDI-II)
4. Add cultural dimensions (Hofstede or Schwartz cultural values)

### 7.2 CVA-ψ Design Workflow

1. **Assess**: Gather ψ profile for target population(s)
2. **Parameterize**: Set θ(ψ), κ(ψ), precision(ψ) using empirical calibrations (from research roadmap)
3. **Decompose**: If culture-specific, select appropriate valuation variant
4. **Design**: Iteratively optimize constraints and affordances toward target valuation profile
5. **Test**: Deploy space; measure constraint/valuation outcomes; iterate

### 7.3 Software Architecture (Future)

Pseudocode for ψ-aware CVA system:

```python
class SubjectCharacteristics:
    def __init__(self, ψ_dict):
        self.culture = ψ_dict['culture']  # κ-selector
        self.neurotype = ψ_dict['neuro']  # ν-profile
        self.age = ψ_dict['dev']
        self.expertise = ψ_dict['exp']
        self.state = ψ_dict['state']
        self.trait = ψ_dict['trait']

    def get_constraint_params(self):
        θ = compute_theta(self.culture, self.neurotype, self.age, self.expertise)
        return θ

class CVAModel_SubjectParameterized:
    def __init__(self, subject: SubjectCharacteristics):
        self.ψ = subject
        self.θ = self.ψ.get_constraint_params()

    def compute_constraints(self, environment_x):
        c_tier1 = f_universal(environment_x)
        c_tier2 = g(c_tier1, environment_x, self.θ)
        c = [c_tier1, c_tier2]
        return c

    def compute_valuations(self, constraints_c):
        κ = select_valuation_structure(self.ψ.culture, self.ψ.neurotype)
        v = compute_v(constraints_c, κ)
        return v

    def compute_policy(self, valuations_v, constraints_c):
        precision = compute_precision(self.ψ.state, self.ψ.neurotype, self.ψ.trait)
        b = policy_softmax(valuations_v, constraints_c, precision)
        return b
```

---

## 8. SUMMARY AND NEXT STEPS

### 8.1 Key Contributions of This Document

1. **Formal ψ parameter space**: Structured representation of subject characteristics (culture, neurotype, age, experience, state, trait) that modulates all CVA layers

2. **Two-tier constraint architecture**: Separation of universal perceptual primitives (Tier 1) from ψ-calibrated interpretive constraints (Tier 2), resolving tension between universality and heterogeneity

3. **Culture-selected valuation structures**: Formalization of how cultures may select structurally different decompositions (not just re-weighting of a universal space)

4. **Neurotype-specific profiles**: Detailed modulation tables for 10+ neurotypes with neural mechanisms and architectural implications

5. **Connection to ATLAS**: Principled mapping from ψ differences to population-transfer discounts (δ), quantifying evidence transferability

6. **Research roadmap**: Specific empirical studies needed to calibrate parameters and validate predictions

7. **Implementation pathway**: ψ assessment protocols and software architecture for deployment

### 8.2 Immediate Next Steps

1. **Empirical calibration** (Months 1–6): Execute high-priority experiments (PTSD, ASD, ADHD, depression, anxiety; see Section 6.2)

2. **Parameter fitting**: Use experimental data to refine θ(ψ), κ(ψ), precision(ψ) functions; document calibration datasets

3. **Culture validation** (Months 3–9): Partner with international architectural teams (Japan, West Africa, India) to validate culture-specific decompositions; empirically test whether Amae, Ma, Àṣà are architecturally observable/actionable

4. **Integration with BN_graphical**: Connect ATLAS δ-computation to ψ-based evidence discounting; test on cross-population architectural datasets

5. **Design pilot projects**: Apply ψ-aware CVA to 3–5 real projects (e.g., therapeutic space for PTSD survivors; sensory-friendly autism center; dementia care facility) with embedded evaluation

6. **Panel review**: Convene cognitive scientists, neuroscientists, and architects (similar to earlier Culture-Aware CVA panel) to critique framework and research priorities

### 8.3 Uncertainty and Limitations

- **ψ_neuro estimation**: Some neurotypes (bipolar, giftedness) are underspecified in cognitive neuroscience; empirical calibration may reveal parameter trade-offs
- **Culture-selection hypothesis**: The claim that cultures have structurally different valuation decompositions is partially speculative pending cultural validation studies
- **Individual differences**: ψ_trait and ψ_state modulations are less neuroscientifically grounded than ψ_neuro; personality–architecture interactions need empirical establishment
- **Generalization**: Parameters calibrated on Western populations may not transfer to non-Western contexts (addressed via ATLAS δ, but empirical validation needed)

### 8.4 Epistemic Commitments

This framework assumes:
1. **Neural decomposability**: Different constraint and valuation systems are neurally dissociable and independently modifiable (supported by neuroscience but not universally true—e.g., emotion and perception are deeply entangled)
2. **ψ-modulation linearity**: Subject characteristics affect parameters multiplicatively or additively (likely simplification; true interactions may be nonlinear)
3. **Architectural measurement**: Constraints and valuations can be operationalized behaviorally, neuroimaging, or via self-report (measurement validity uncertain)

These commitments should be revisited as empirical data accumulates.

---

## References

Aron, E. N. (2010). Psychotherapy and the highly sensitive person: improving clinical practice for HSPs. *Routledge*.

Aron, E. N., Aron, A., & Jagiellak, M. (2012). Sensory processing sensitivity: a review in the light of the evolution of biological responsivity. *Personality and Individual Differences*, 45(2), 100–112.

Baron-Cohen, S., & Belmonte, M. K. (2005). Autism: a window onto the development of the social and analytic brain. *Annual Review of Neuroscience*, 28, 109–126.

Barton, J., & Pretty, J. (2010). What is the best dose of nature and green exercise for improving mental health? A multistudy analysis. *Environmental Science & Technology*, 44(10), 3947–3955.

Blakemore, S.-J., & Choudhury, S. (2006). Development of the adolescent brain: implications for executive function and social cognition. *Journal of Child Psychology and Psychiatry*, 47(3), 296–312.

Braak, H., & Braak, E. (1991). Neuropathological stageing of Alzheimer-related changes. *Acta Neuropathologica*, 82(4), 239–259.

Calkins, M. P. (2009). Evidence-based long-term care practice. *Health Environments Research & Design Journal*, 2(4), 90–108.

Castellanos, F. X., & Tannock, R. (2002). Neuroscience of attention-deficit/hyperactivity disorder: the search for endophenotypes. *Nature Reviews Neuroscience*, 3(8), 617–628.

Cohen, U., & Weisman, G. D. (1991). Holding onto the heritage: A planning & design guide for dementia facilities. Alzheimer's Association.

Costa, P. T., & McCrae, R. R. (1992). *Four ways five factors are basic*. Personality and Individual Differences, 13(6), 653–665.

Craske, M. G., Kircanski, K., & Zelikowsky, M. (2008). Optimizing the fear extinction paradigm. *Behaviour Research and Therapy*, 46(1), 5–27.

Czeisler, C. A., & Gooley, J. F. (2007). Sleep and circadian rhythms in humans. *Cold Spring Harbor Symposia on Quantitative Biology*, 72, 579–597.

Diamond, A. (2002). Normal development of prefrontal cortex from birth to young adulthood. *Neurobiology of Learning and Memory*, 78(3), 553–564.

Disner, S. G., Beevers, C. G., Haigh, E. A., & Beck, A. T. (2011). Neural mechanisms of the cognitive model of depression. *Nature Reviews Neuroscience*, 12(8), 467–477.

Doshi, B. V. (1989). *Balkrishna Doshi: Architecture and Design*. Ahmedabad: Vastushilpa Foundation.

Ericsson, K. A. (1996). The acquisition of expert performance: an introduction to some of the issues. In K. A. Ericsson (Ed.), *The road to excellence: The acquisition of expert performance in the arts and sciences, sports and games* (pp. 1–50). Erlbaum.

Foa, E. B., Hembree, E. A., & Rothbaum, B. O. (2007). *Prolonged exposure therapy for PTSD: Emotional processing of traumatic experiences: Therapist guide*. Oxford University Press.

Gross, J. J., & John, O. P. (2003). Individual differences in two emotion regulation processes: implications for affect, relationships, and well-being. *Journal of Personality and Social Psychology*, 85(2), 348–362.

Hart, R. (1979). *Children's experience of place: A developmental study*. Irvington.

Hescham, S., Temel, Y., & Jahanshahi, A. (2016). The neuromodulatory effects of deep brain stimulation in Parkinson's disease: Focus on the non-motor symptoms. In *Parkinson's Disease: Pathogenesis and Clinical Aspects* (pp. 1–19). ExonPublications.

Hofmann, S. G., & Smits, J. A. (2008). Cognitive-behavioral therapy for adult anxiety disorders: a meta-analysis of randomized placebo-controlled trials. *The Journal of Clinical Psychiatry*, 69(4), 621–632.

Honea, R., & Schaffer, D. (2019). Sensory sensitivities in autism spectrum disorder. *Current Psychiatry Reports*, 21(12), 1–8.

Johnson, S. L., Cuellar, A. K., Ruggero, C. J., Winett-Perlman, C., Goodnick, P., & White, R. (2008). Life events as predictors of mania and depression in bipolar I disorder. *Journal of Abnormal Psychology*, 117(2), 268–277.

Kellman, P. J., & Garrigan, P. (2009). Perceptual learning and human expertise. *Physics of Life Reviews*, 6(2), 53–84.

Kirsh, D., & Nersissian, N. J. (2022). Cognitive artifacts: ores and offloading. In *The Cambridge handbook of cognitive science* (pp. 537–566). Cambridge University Press.

Kitayama, S., & Markus, H. R. (2010). Culture and social neuroscience: Emerging principles and implications. *Social Cognitive and Affective Neuroscience*, 5(1), 2–3.

Lawton, M. P., & Nahemow, L. (1973). Ecology and the aging process. In C. Eisdorfer & M. P. Lawton (Eds.), *Psychology of adult development and aging* (pp. 619–674). American Psychological Association.

Markram, H., & Markram, K. (2010). The intense world theory—a unifying theory of the neurobiology of autism. *Frontiers in Human Neuroscience*, 4, 224.

Marquardt, G., & Schmieg, P. (2009). Dementia-friendly architecture: Environments that facilitate wayfinding in nursing homes. *American Journal of Alzheimer's Disease & Other Dementias*, 24(4), 333–340.

Mayberg, H. S. (2003). Positron emission tomography imaging in depression: a neural systems perspective. *NeuroImage*, 10(2), 175–198.

Mbembe, A. (2015). *Critique of black reason*. Duke University Press.

Nisbett, R. E., & Masuda, T. (2003). Culture and point of view. *Proceedings of the National Academy of Sciences*, 100(19), 11163–11170.

Owsley, C. (2011). Aging and vision. *Vision Research*, 51(13), 1610–1622.

Pellegrini, A. D., & Smith, P. K. (1998). Physical activity play: the nature and function of a neglected aspect of play. *Child Development*, 69(3), 577–598.

Phillips, M. L., & Kupfer, D. J. (2013). Bipolar disorder diagnosis: challenges and future directions. *The Lancet*, 381(9878), 1663–1671.

Pizzagalli, D. A., Holmes, A. J., Dillon, D. G., Goetz, E. L., Birk, J. L., Bogdan, R., ... & Fava, M. (2008). Reduced caudate and nucleus accumbens response to rewards in unmedicated individuals with major depressive disorder. *American Journal of Psychiatry*, 165(8), 996–1005.

Rapoport, A. (1969). *House form and culture*. Prentice-Hall.

Rauch, S. L., Shin, L. M., & Wright, C. I. (2006). Neuroimaging studies of amygdala function in anxiety and fear conditioning. In *The amygdala: A functional analysis* (pp. 348–388). Oxford University Press.

Renzulli, J. S. (1986). The three-ring conception of giftedness: A developmental model for creative productivity. In R. J. Sternberg & J. E. Davidson (Eds.), *Conceptions of giftedness* (pp. 53–92). Cambridge University Press.

Salthouse, T. A. (2009). When does age-related cognitive decline begin? *Neurobiology of Aging*, 30(4), 507–514.

Sapolsky, R. M. (2015). *Stress and the brain: Individual differences and the invertebrate model*. MIT Press.

Sasaki, Y., Watanabe, T., Tanaka, S., & Nakashita, S. (2005). Training-induced neural plasticity in human visual motion processing. *Current Biology*, 15(13), 1191–1195.

Schneider, B. A., & Pichora-Fuller, M. K. (2000). Implications of perceptual deterioration for cognitive aging research. *Psychology and Aging*, 15(3), 596–606.

Selkoe, D. J. (2002). Alzheimer's disease is a synaptic failure. *Science*, 298(5594), 789–791.

Shin, L. M., & Liberzon, I. (2010). The neurobiology of fear, stress, and anxiety disorders. *Neuropsychology*, 24(1), 75–85.

Spencer, C., & Blades, M. (2006). *Children and their environments: Learning, using and designing spaces*. Cambridge University Press.

Stein, D. J., & Stein, M. K. (2008). Social anxiety disorder. *The Lancet*, 371(9618), 1115–1125.

Strakowski, S. M., Delbello, M. P., & Adler, C. M. (2012). The functional neuroanatomy of bipolar disorder: a consensus model. *Bipolar Disorders*, 7(1), 16–30.

van der Kolk, B. A. (2014). *The body keeps the score: Brain, mind, and body in the healing of trauma*. Viking.

Volkow, N. D., Wang, G.-J., Fowler, J. S., Logan, J., Gerasimov, M., Maynard, L., ... & Franceschi, D. (2009). Therapeutic doses of oral methylphenidate significantly increase extracellular dopamine in the human brain. *Journal of Neuroscience*, 21(2), RC121–RC121.

Winner, E. (1996). *Gifted children: Myths and realities*. Basic Books.

Woynaroski, T. G., Kwakye, L. D., Foss-Feig, J. H., Stevenson, R. A., Stone, W. L., & Wallace, M. T. (2013). Multisensory temporal binding window in autism spectrum disorders. *Proceedings of the National Academy of Sciences*, 110(52), 21008–21013.

---

## Appendix A: Notation Summary

| Symbol | Meaning |
|--------|---------|
| **ψ** | Subject-characteristics parameter space |
| ψ_culture | Cultural context (κ-selector) |
| ψ_neuro | Neurotype profile (ν-vector) |
| ψ_dev | Developmental stage (age + maturation) |
| ψ_exp | Experience/expertise |
| ψ_state | Acute psychological state |
| ψ_trait | Stable trait differences |
| **c** | Constraint vector (8 dimensions) |
| c_Tier1 | Universal perceptual primitives |
| c_Tier2 | ψ-calibrated interpretive constraints |
| **v** | Valuation vector (9 dimensions, culture-selected) |
| **θ(ψ)** | Constraint parameterization function |
| **κ(ψ)** | Valuation structure selector |
| **precision(ψ)** | Policy precision/inverse temperature |
| **π** | Policy function (action selection) |
| **b** | Behavioral policy/action |
| **δ** | Population-transfer discount factor (ATLAS) |

---

**Document Prepared For**: Professor David Kirsh, UCSD Cognitive Science
**Status**: Foundational formalization for empirical research
**Next Review**: After completion of priority experiments (Months 1–6)

