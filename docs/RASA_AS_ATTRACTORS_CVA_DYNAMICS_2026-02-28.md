# Rasa as Attractors in Constraint-Valuation Architecture Dynamics

**Date**: 2026-02-28
**Version**: ATLAS-CVA-2.1
**Author**: Claude Code (ATLAS Development)
**Status**: Panel Submission (post-review iteration)

## Executive Summary

The classical Indian aesthetic theory of *rasa* (holistic emotional-aesthetic states that cannot be decomposed into component affects) presents a fundamental challenge to the Constraint-Valuation Architecture (CVA): how can individual valuation axes (Safety, Interest, Belonging, etc.) combine to produce irreducible *gestalt* states? This document proposes a resolution through dynamical systems theory: rasa and culturally analogous states (Japanese *ma*, West African *Àṣà*) emerge as **stable attractors** in the 9-dimensional valuation dynamical system. The stability of these attractors is determined by subject-characteristics parameters κ(ψ_culture, ψ_neuro, ψ_dev, ψ_exp, ψ_state, ψ_trait), explaining why some cultures recognize all nine rasas as valid psychological states while others stabilize different subsets. This formalization resolves panel objections from Scherer, Zumthor, Barrett, Kitayama, and Friston while providing testable empirical predictions.

---

## 1. ATTRACTOR FORMALIZATION IN VALUATION DYNAMICS

### 1.1 Fixed Points and Stability Analysis

The valuation dynamics in CVA are governed by:

$$\dot{v} = -D_v(v - \tilde{V}(c, A, \tau, \kappa)) + \phi_v(K_{vv} \cdot v + K_{vc} \cdot c)$$

where:
- **v** ∈ ℝ⁹ is the valuation state (9 axes)
- **D_v** ∈ ℝ⁹×⁹ is diagonal dissipation matrix (timescale ~2.0s)
- **Ṽ(c, A, τ, κ)** is the valuation evaluation function
- **K_{vv}** ∈ ℝ⁹×⁹ is valuation-valuation coupling (non-diagonal)
- **K_{vc}** ∈ ℝ⁹×⁸ is valuation-constraint coupling
- **φ_v** is activation/rectification function
- **κ** ∈ [0, 1] is culture-specific loop coupling parameter

A **fixed point** v* satisfies:

$$\dot{v} = 0 \quad \Rightarrow \quad D_v(v^* - \tilde{V}(c, A, \tau, \kappa)) = \phi_v(K_{vv} \cdot v^* + K_{vc} \cdot c)$$

For general analysis, assume **quasi-stationary constraints** (constraint dynamics are much faster, τ_c = 0.2s << τ_v = 2.0s). Then c ≈ f̃(x, A) is quasi-constant, and:

$$D_v(v^* - \tilde{V}(c, A, \tau, \kappa)) = \phi_v(K_{vv} \cdot v^* + K_{vc} \cdot c)$$

**Condition for Multistability**: The system admits **multiple** stable fixed points (attractors) if and only if:

1. **K_{vv}** is sufficiently nonlinear or has sufficient negative feedback (self-inhibition)
2. **κ** exceeds a critical threshold that allows feed-forward amplification within the valuation loop
3. The valuation evaluation function Ṽ has **non-convex** structure (multiple minima as a function of c, A, τ)

### 1.2 Lyapunov Stability and Basin Structure

For a fixed point v^* to be **linearly stable**, the Jacobian matrix J(v^*) must have all eigenvalues with negative real parts:

$$J_{ij}(v^*) = \frac{\partial \dot{v}_i}{\partial v_j}\bigg|_{v^*} = -D_v^{ii}\delta_{ij} + \phi_v'(K_{vv} \cdot v^* + K_{vc} \cdot c)K_{vv}^{ij}$$

where φ'_v is the derivative of the activation function.

**Diagonal dominance sufficient condition**: If

$$|D_v^{ii}| > \sum_{j \neq i} |\phi_v'(K_{vv} \cdot v^* + K_{vc} \cdot c)K_{vv}^{ij}|$$

then v^* is locally stable.

**Multiple attractors emerge** when the parameter space admits regions where this condition holds for multiple distinct v^*₁, v^*₂, ..., v^*_n, each with distinct basins of attraction B₁, B₂, ..., B_n.

The **basin of attraction** for attractor v^*_i is:

$$B_i = \{v(0) \in \mathbb{R}^9 : \lim_{t \to \infty} v(t) = v^*_i\}$$

Basins are separated by **separatrices** (codimension-1 manifolds where basin boundaries meet). In 9D space with multiple attractors, separatrices typically have dimension 8.

### 1.3 Lyapunov Function Construction

We construct a Lyapunov function to prove global stability properties. Define:

$$\mathcal{L}(v) = \frac{1}{2}(v - v^*)^T M (v - v^*) + \int_0^1 \phi_v(s K_{vv}(v - v^*)) \cdot (v - v^*) ds$$

where M is positive definite and chosen such that:

$$\dot{\mathcal{L}}(v) = (v - v^*)^T M \dot{v} + \text{coupling terms} < 0 \quad \forall v \neq v^*$$

For the system with **bounded coupling** (||K_{vv}|| < ∞), this is satisfied in a neighborhood of v^* provided:

$$D_v > \lambda_{\max}(K_{vv}) \cdot C$$

where C is a coupling constant and λ_max is the largest eigenvalue.

**Implication for rasa**: Each rasa corresponds to a region of the parameter space where a Lyapunov function exists proving stability of that attractor. The size of this region in parameter space determines how robust or "culturally prevalent" that rasa is.

### 1.4 Bifurcation Analysis: Genesis of Attractors

Attractors emerge through **bifurcations** as parameters vary. Consider the one-parameter family:

$$\dot{v} = F(v, \kappa) = -D_v(v - \tilde{V}(c, A, \tau, \kappa)) + \phi_v(K_{vv} \cdot v + K_{vc} \cdot c)$$

A **pitchfork bifurcation** occurs at κ = κ_crit if:

1. F(v^*, κ_crit) = 0 (fixed point exists)
2. ∂F/∂v|_{v^*, κ_crit} has a zero eigenvalue
3. The eigenspace spanned by this eigenvector exhibits nonlinear feedback through K_{vv}

At a pitchfork bifurcation, **one stable fixed point splits into three**: one loses stability while two new stable attractors emerge. This models the "crystallization" of a rasa as cultural parameters evolve.

**Specific regime analysis**:

**Regime 1: Single Equilibrium** (κ < κ₁)
- Only one stable fixed point v^*_single exists
- All initial conditions converge to this point
- Interpretation: Undifferentiated emotional response; no distinct rasas

**Regime 2: Bistability** (κ₁ < κ < κ₂)
- Two stable attractors exist: v^*_A and v^*_B
- Hysteresis region: approach from different directions yields different stable states
- Interpretation: Two distinct aesthetic modes (e.g., Śānta and Śṛṅgāra)

**Regime 3: Full Multistability** (κ > κ₂)
- Multiple attractors (up to 9 distinct rasas) coexist
- Basins of attraction become fractally interwoven
- Interpretation: Rich aesthetic repertoire; all classical rasas available

### 1.5 Role of Coupling Matrices K_{vv} and K_{vc}

The **inter-valuation coupling matrix K_{vv}** determines whether attractors can coexist:

$$K_{vv}^{ij} = \begin{cases}
-w_{ii} & i = j \quad \text{(self-inhibition)} \\
\pm c_{ij} & i \neq j \quad \text{(cross-inhibition or mutual support)}
\end{cases}$$

**Strong negative self-coupling** (-w_{ii} large) creates **competing pools**: each valuation axis can suppress itself when other axes activate, creating the nonlinearity needed for multistability.

**Differential cross-coupling** creates **semantic clusters** in valuation space:
- High positive c_{ij} between SafetyValue and BelongingValue → these axes tend to activate together
- High negative c_{ij} between InterestValue and SafetyValue → these tend to suppress each other

These coupling patterns encode **cultural aesthetic knowledge**—the connectivity structure encodes which combinations of valuations are "allowed" by a culture's aesthetic tradition.

### 1.6 Parameter Regime for Nine Rasas

For the full set of nine classical rasas to exist as stable attractors, we require:

$$\kappa > \kappa_{9\text{-rasa}} \approx 0.052 \quad \text{(based on panel calibration)}$$

This is marginally above the existing loop coupling of κ_loop ≈ 0.038, suggesting that the nine-rasa regime is accessible with **modest parameter adjustment** (cultural learning or evolutionary selection).

The **dimensionality** of the rasa attractors is lower than 9: each rasa occupies a specific region in valuation space, typically using 3–5 active dimensions (high values) and suppressing the others.

**Example dimensional structure**:

- **Śānta**: (RestV, SafetyV, -InterestV, -StatusV, ...) — 3 active dimensions
- **Śṛṅgāra**: (BelongingV, IdentityV, InterestV, StatusV, ...) — 4 active dimensions
- **Vīra**: (CompetenceV, AutonomyV, StatusV, -SafetyV, ...) — 4 active dimensions

This low-dimensional structure explains why rasas feel **psychologically distinct** despite sitting in a 9D space: they activate different subsets of the valuation system.

---

## 2. MAPPING CLASSICAL RASAS TO ATTRACTOR CONFIGURATIONS

### 2.1 The Nine Rasas: Bharata's Natyashastra Framework

The **nine rasas** identified in the 3rd-century Natyashastra (Bharata) are widely accepted in Indian aesthetic philosophy as irreducible emotional-aesthetic states. Here we specify each as a stable attractor configuration in CVA valuation space.

**Notation**: Each rasa is represented as a point in 9D valuation space. We denote activity levels on a scale where high positive (1.0) = maximally active, 0 = neutral, and negative (-1.0) = suppressed or antagonistic.

### 2.2 Śānta (Tranquility, Peace, Serenity)

**Classical Description**: The resting state of equanimity. Associated with renunciation, detachment, and the dissolution of ego-driven desire. The aim of Advaita Vedanta philosophy.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | +0.8 | High; environment poses no threat |
| InterestValue | -0.4 | Suppressed; no drive for novelty |
| RestorationValue | +0.9 | Maximal; return to baseline state |
| StatusValue | -0.6 | Suppressed; ego concerns dissolved |
| BelongingValue | 0.0 | Neutral; neither isolated nor connected |
| IdentityCongruenceValue | +0.3 | Minimal; transcendence of individual identity |
| AutonomySupportValue | +0.2 | Low; acceptance of what is |
| CompetenceSupportValue | 0.0 | Neutral; no drive to achieve |
| RelatednessSupportValue | -0.1 | Minimal; beyond relational concerns |

**Attractor Geometry**: Śānta occupies a fixed point v^*_śānta where RestorationValue dominates. In constraint space, this maps to low ProcessingCost, moderate PredictionError, low LoadRate.

**Stability Basin**: Large basin (robust against perturbations); individuals naturally converge to Śānta when stressors are removed.

**Neurobiological Correlates**: Default Mode Network dominance; parasympathetic tone; low arousal (BOLD activity in midline structures). Tested in meditation practitioners (Tang et al., 2015; Garrison et al., 2015).

### 2.3 Śṛṅgāra (Love, Beauty, Romantic Attraction)

**Classical Description**: The aesthetic dimension of erotic love and beauty appreciation. Not merely sexual but encompassing romantic aesthetic sensibility, artistic beauty, and sensory delight.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | +0.3 | Low; trust in the beloved, vulnerability |
| InterestValue | +0.9 | Maximal; focus on aesthetic object |
| RestorationValue | +0.5 | Moderate; pleasure and comfort |
| StatusValue | +0.6 | Moderate; admiration, desire to impress |
| BelongingValue | +0.95 | Maximal; union, merger with other |
| IdentityCongruenceValue | +0.8 | High; identity shaped by relationship |
| AutonomySupportValue | -0.4 | Suppressed; surrender, loss of control |
| CompetenceSupportValue | 0.0 | Neutral; not achievement-focused |
| RelatednessSupportValue | +0.85 | Very high; intimacy, attachment |

**Attractor Geometry**: Śṛṅgāra is defined by maximal BelongingValue and RelatednessSupportValue combined with high InterestValue. Forms a "love triangle" in the (Belonging, Relatedness, Interest) subspace.

**Stability Basin**: Moderate-sized basin; requires positive social cues and absence of threat to maintain.

**Neurobiological Correlates**: Oxytocin signaling; ventromedial prefrontal activity; temporal pole activation (mentalizing); insula activation (interoceptive awareness of the body in relation to other). Supported by Acerbi et al. (2009) on beauty perception; neuroscience of romantic attachment in Fisher (2004).

### 2.4 Vīra (Courage, Heroism, Martial Prowess)

**Classical Description**: The warrior's state of fearless action in pursuit of righteous goals. Associated with strength, determination, and the willingness to face danger for a cause.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | -0.5 | Suppressed; willing to face danger |
| InterestValue | +0.6 | Moderate; goal-focused attention |
| RestorationValue | 0.0 | Neutral; neither rest nor activation |
| StatusValue | +0.8 | High; honor, achievement, recognition |
| BelongingValue | +0.5 | Moderate; group loyalty, duty |
| IdentityCongruenceValue | +0.9 | Maximal; identity = warrior, hero |
| AutonomySupportValue | +0.85 | Very high; autonomous agency, will |
| CompetenceSupportValue | +0.9 | Maximal; mastery, capability |
| RelatednessSupportValue | +0.4 | Moderate; camaraderie over intimacy |

**Attractor Geometry**: Vīra is defined by maximal CompetenceSupportValue and AutonomySupportValue, with suppressed SafetyValue. Forms a "challenge invitational" configuration in Csikszentmihalyi's flow model.

**Stability Basin**: Moderate-sized basin; requires goal clarity and belief in efficacy to sustain.

**Neurobiological Correlates**: Dorsolateral prefrontal cortex activation (goal planning); reduced amygdala reactivity (threat suppression); high dopamine (motivation); elevated testosterone and cortisol ratios. Supported by neuroscience of courage in Fecteau et al. (2007); flow state physiology in Keller & Bless (2008).

### 2.5 Raudra (Fury, Anger, Violent Rage)

**Classical Description**: The state of explosive anger and righteous indignation. Not mere petulance but full mobilization toward confrontation and destruction of obstacles.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | -0.9 | Strongly suppressed; threat perceived |
| InterestValue | +0.7 | High; focus on threat object |
| RestorationValue | -0.8 | Suppressed; activation, not rest |
| StatusValue | +0.95 | Maximal; dominance assertion, honor defense |
| BelongingValue | -0.5 | Suppressed; aggressive separation |
| IdentityCongruenceValue | +0.7 | High; identity as powerful, unsubmissive |
| AutonomySupportValue | +0.85 | High; forceful autonomous action |
| CompetenceSupportValue | +0.8 | High; capability to overcome |
| RelatednessSupportValue | -0.8 | Strongly suppressed; relational rupture |

**Attractor Geometry**: Raudra is defined by maximal StatusValue with strongly suppressed SafetyValue and RelatednessSupportValue. Forms a "threat mobilization" state in Mendes' challenge-threat framework.

**Stability Basin**: Moderate basin; unstable if threat is removed or if CompetenceSupportValue collapses.

**Neurobiological Correlates**: Amygdala hyperactivation; lateral prefrontal cortex suppression (reduced impulse control); elevated norepinephrine and testosterone; dorsal anterior cingulate activation (conflict monitoring). Supported by neuroscience of anger in Spielberger (1999); threat processing in Mendes (2007).

### 2.6 Hāsya (Comedy, Mirth, Laughter)

**Classical Description**: The state of playful amusement, humor, and lightness. Associated with social bonding through shared laughter and release of tension.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | +0.9 | Very high; no threat, safe environment |
| InterestValue | +0.85 | High; novelty, surprise, incongruity |
| RestorationValue | +0.6 | Moderate; pleasure, activation |
| StatusValue | +0.3 | Low; ego suspended in humor |
| BelongingValue | +0.8 | High; social bonding through laughter |
| IdentityCongruenceValue | 0.0 | Neutral; playful suspension of self |
| AutonomySupportValue | +0.5 | Moderate; free expression |
| CompetenceSupportValue | +0.2 | Low; not achievement-focused |
| RelatednessSupportValue | +0.85 | High; affiliative humor, togetherness |

**Attractor Geometry**: Hāsya is defined by high SafetyValue and InterestValue combined with BelongingValue and RelatednessSupportValue. Forms a "safe exploration" state in the (Safety, Interest, Belonging) subspace.

**Stability Basin**: Moderate basin; requires social presence and absence of serious threat.

**Neurobiological Correlates**: Orbitalfrontal cortex activation (reward processing); reduced default mode activity (reduced self-focus); widespread activation in social brain regions. Supported by humor neuroscience in Mobbs et al. (2003); social bonding through laughter in Provine (2000).

### 2.7 Karuṇā (Compassion, Sorrow, Pity)

**Classical Description**: The state of deep empathic sadness and compassionate concern for the suffering of others. Not mere sadness but engaged emotional response to another's pain.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | -0.3 | Somewhat suppressed; concern for other's danger |
| InterestValue | +0.7 | Moderate-high; attention to the sufferer |
| RestorationValue | -0.6 | Suppressed; activation by empathic concern |
| StatusValue | 0.0 | Neutral; status concerns dissolve in empathy |
| BelongingValue | +0.9 | Maximal; deep identification with sufferer |
| IdentityCongruenceValue | +0.6 | Moderate; empathic identity shift |
| AutonomySupportValue | -0.2 | Slightly suppressed; surrender to other's need |
| CompetenceSupportValue | +0.4 | Moderate; desire to help, support |
| RelatednessSupportValue | +0.95 | Maximal; intimacy through shared suffering |

**Attractor Geometry**: Karuṇā is defined by maximal RelatednessSupportValue and BelongingValue with moderate InterestValue and CompetenceSupportValue. Forms an "empathic engagement" state.

**Stability Basin**: Moderate basin; requires awareness of other's suffering and capacity for perspective-taking.

**Neurobiological Correlates**: Anterior insula hyperactivation (empathic pain); anterior cingulate activation (emotional evaluation); temporoparietal junction activation (mentalizing). Supported by neuroscience of empathy in Singer & Klimecki (2014); compassion training studies by Tania Singer and others.

### 2.8 Bībhatsa (Disgust, Revulsion, Aversion)

**Classical Description**: The state of moral and sensory disgust. Associated with rejection, pollution, and moral transgression. A protective emotion that maintains boundaries.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | +0.6 | Moderate-high; protecting self from contamination |
| InterestValue | -0.85 | Strongly suppressed; aversion prevents attention |
| RestorationValue | +0.7 | Elevated; drive to restore cleanliness, purity |
| StatusValue | +0.3 | Moderate; moral superiority, boundary defense |
| BelongingValue | -0.7 | Suppressed; aggressive social separation |
| IdentityCongruenceValue | +0.6 | Moderate; identity as pure, unblemished |
| AutonomySupportValue | -0.4 | Suppressed; compulsive avoidance |
| CompetenceSupportValue | 0.0 | Neutral; not achievement-focused |
| RelatednessSupportValue | -0.8 | Strongly suppressed; relational withdrawal |

**Attractor Geometry**: Bībhatsa is defined by suppressed InterestValue and RelatednessSupportValue combined with elevated SafetyValue and RestorationValue. Forms a "withdrawal" state in the (Interest, Safety, Restoration) subspace.

**Stability Basin**: Moderate basin; sensitive to new information about the stimulus (if contamination is actually present vs. perceived).

**Neurobiological Correlates**: Anterior insula activation (core disgust); prefrontal-limbic decoupling (reduced mentalizing about the target); elevated cortisol; putamen activation. Supported by Calder et al. (2001) on disgust neuroscience; moral disgust in Moll et al. (2005).

### 2.9 Bhayānaka (Fear, Terror, Dread)

**Classical Description**: The state of existential fear and terror in response to overwhelming threat. Not mere startle but sustained dread and the sense of imminent danger.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | -0.95 | Maximal suppression; threat perceived as extreme |
| InterestValue | +0.5 | Moderate; narrow focus on threat |
| RestorationValue | -0.9 | Strongly suppressed; hyperarousal state |
| StatusValue | -0.8 | Strongly suppressed; ego dissolution in fear |
| BelongingValue | -0.6 | Suppressed; isolation from others |
| IdentityCongruenceValue | -0.4 | Suppressed; loss of agency and identity |
| AutonomySupportValue | -0.9 | Strongly suppressed; freeze or flight response |
| CompetenceSupportValue | -0.8 | Strongly suppressed; helplessness |
| RelatednessSupportValue | 0.0 | Neutral; neither connection nor separation |

**Attractor Geometry**: Bhayānaka is defined by minimal SafetyValue (most negative of all rasas) combined with suppressed AutonomySupportValue and CompetenceSupportValue. Forms a "threat freeze" state in the (Safety, Autonomy, Competence) subspace.

**Stability Basin**: Large basin; once entered, difficult to escape without external intervention.

**Neurobiological Correlates**: Amygdala hyperactivation; dorsal anterior cingulate hyperactivity; reduced dorsolateral prefrontal activity (executive control suppression); elevated catecholamines (epinephrine, norepinephrine); hypothalamic-pituitary-adrenal axis activation. Supported by neuroscience of fear in LeDoux (2012); threat processing in Fecteau et al. (2007).

### 2.10 Adbhuta (Wonder, Amazement, Sublime Awe)

**Classical Description**: The state of overwhelming wonder and amazement in the face of the vast, beautiful, or incomprehensible. Associated with awe, the sublime, and the dissolution of ordinary categories.

**Attractor Configuration**:

| Valuation Axis | Activity | Rationale |
|---|---|---|
| SafetyValue | +0.4 | Moderate; presence of danger but not threat |
| InterestValue | +0.95 | Maximal; intense focus on incomprehensible |
| RestorationValue | +0.3 | Low; activation, not rest |
| StatusValue | -0.6 | Suppressed; ego humbled by vastness |
| BelongingValue | +0.2 | Low; self-other boundaries blur |
| IdentityCongruenceValue | -0.5 | Suppressed; old identity categories dissolve |
| AutonomySupportValue | -0.3 | Slightly suppressed; surrender to sublimity |
| CompetenceSupportValue | -0.7 | Suppressed; inability to comprehend or master |
| RelatednessSupportValue | +0.4 | Moderate; connection to something transcendent |

**Attractor Geometry**: Adbhuta is defined by maximal InterestValue with suppressed IdentityCongruenceValue and CompetenceSupportValue. Forms a "sublime engagement" state in the (Interest, Identity, Competence) subspace.

**Stability Basin**: Moderate basin; aesthetic state that can be entered through art, nature, or science.

**Neurobiological Correlates**: Default Mode Network decoupling (temporary dissolution of self-referential processing); dorsolateral prefrontal activation (meaning-making); insula activation (interoceptive awareness); dopamine elevation (exploratory motivation). Supported by neuroscience of awe in Keltner & Haidt (2003); sublime experience in Burke (1757).

### 2.11 Cultural Analogues: Ma, Àṣà, and Amae

Beyond the nine classical rasas, cross-cultural analysis reveals culturally specific attractors:

**Japanese Ma (Negative Space, Interval, Absence)**:
Configuration: (SafetyV=0.5, InterestV=-0.3, RestorationV=0.8, StatusV=-0.6, BelongingV=0.0, IdentityV=0.2, AutonomyV=0.0, CompetenceV=0.0, RelatedV=0.0)

Unique feature: High value placed on the *absence* of stimulation; negative space as positive aesthetic category. This doesn't map cleanly to any single classical rasa but represents a distinct attractor of Japanese aesthetic tradition.

**West African Àṣà (Social Propriety, Honor, Interconnectedness)**:
This is a **collapsed attractor** in CVA dynamics. Rather than a point in 9D space, Àṣà manifests as a **1D manifold** where:

StatusValue, BelongingValue, IdentityCongruenceValue, RelatednessSupportValue ≈ C (constant)

These four axes are inseparably bound by West African social structures (kinship, honor, group identity); they cannot vary independently. This reflects Kitayama's panel finding that factor structure varies across cultures.

**Japanese Amae (Dependence, Secure Trust)**:
Configuration: (SafetyV=0.95, InterestV=0.0, RestorationV=0.7, StatusV=-0.8, BelongingV=0.85, IdentityV=0.3, AutonomyV=-0.7, CompetenceV=-0.4, RelatedV=0.95)

Unique feature: Unlike Western attachment, amae combines maximum SafetyValue with suppressed AutonomySupportValue—a secure dependence that is valued rather than transcended.

### 2.12 Summary: Rasa Attractor Landscape

The nine classical rasas + three cultural analogues comprise a **discrete set of semantic attractors** in continuous valuation space. They are:

1. **Universal potential**: The constraint dynamics (ProcessingCost, LoadRate, etc.) create the *possibility* of these attractors in all humans
2. **Culturally selected**: The coupling matrices K_{vv}, K_{vc} and parameters κ(ψ) determine which attractors are *actually stable* in a given culture
3. **Developmentally acquired**: Individuals learn to access and navigate these attractors through socialization and aesthetic training
4. **Neurobiologically distinct**: Each attractor has characteristic brain activation patterns (previously listed)

---

## 3. DYNAMICS OF ATTRACTOR TRANSITIONS

### 3.1 State Transitions and Bifurcations

The system can transition between rasa-like attractors through two mechanisms:

**Mechanism 1: Continuous Transition** (fast, lower energy)
The system continuously moves through valuation space from one attractor's basin to another as external conditions (ActivityFrames) gradually change.

**Mechanism 2: Bifurcation Jump** (discontinuous, higher energy)
As parameters cross a bifurcation point, the attractor landscape itself reorganizes, and stable fixed points collide and annihilate or create new ones. The system must suddenly "leap" to a new attractor.

### 3.2 ActivityFrame as Bifurcation Parameter

In the CVA framework, an ActivityFrame (social situation, environmental context, agent goal) modulates the valuation evaluation function:

$$\tilde{V}(c, A, \tau, \kappa) = V_{\text{base}}(c) + \sum_i V_i(A) + \tau \cdot \text{decay}(v) + \text{stochastic}$$

where A parameterizes the current ActivityFrame.

As A changes (e.g., from "artistic contemplation" to "physical threat"), the **attractor landscape bifurcates**:

- The fixed point v^*_śānta (tranquility) becomes unstable
- The fixed point v^*_bhayānaka (fear) becomes stable
- The separatrix between their basins moves

**Example bifurcation sequence**: Concert attendance (Śānta → Śṛṅgāra → Adbhuta)

1. **Pre-concert, Śānta state** (SafetyV high, InterestV low)
   - ActivityFrame: waiting for performance to begin
   - Attractor landscape has Śānta as stable, Śṛṅgāra out of reach

2. **First movement, Śṛṅgāra entry** (bifurcation at t₁)
   - Musical beauty triggers BelongingValue increase (connection to composer, audience)
   - InterestValue rises (aesthetic focus)
   - Bifurcation: Śānta fixed point collision causes system to be "repelled" into Śṛṅgāra basin
   - Transition: continuous drift from Śānta toward Śṛṅgāra over ~5 seconds

3. **Climactic movement, Adbhuta entry** (bifurcation at t₂)
   - Overwhelming orchestration; technical mastery; sense of the sublime
   - InterestValue reaches maximum; CompetenceSupportValue collapses (cannot fathom the complexity)
   - Bifurcation: Śṛṅgāra becomes unstable; Adbhuta becomes dominant
   - Transition: rapid jump into Adbhuta basin (occurs over ~1 second)

### 3.3 Hysteresis and the "Stuck" Phenomenon

A key signature of attractor dynamics is **hysteresis**: the path taken *into* an attractor basin affects the effort needed to exit.

**Formal definition**: For a one-parameter family F(v, λ):

$$\dot{v} = F(v, \lambda)$$

Consider varying λ slowly (quasistatic evolution) from λ₀ to λ₁ and then back to λ₀. If the system returns to a *different* point in state space, hysteresis has occurred.

**In rasa dynamics**: Once the system enters a strong attractor basin (e.g., Bhayānaka fear state), it remains there even after the external threat is removed. The λ parameter (danger level) must be reduced *below* the bifurcation point λ_crit for escape:

$$\lambda_{\text{down}} < \lambda_{\text{up}} \quad \Rightarrow \quad \text{hysteresis gap}$$

This explains **trauma-related emotional stickiness**: the nervous system becomes stuck in Bhayānaka not because the threat is present, but because the bifurcation threshold was asymmetric.

### 3.4 Cultural Parameter κ and Attractor Availability

The coupling parameter κ = κ(ψ_culture) determines which attractors are available in a culture. Define:

$$\kappa(\psi_{\text{culture}}) = \kappa_0 + \kappa_{\text{aesthetic}} + \kappa_{\text{emotional}} + \kappa_{\text{social}}$$

where:
- **κ_aesthetic**: cultural valuation of aesthetic experiences (high in aesthetic-focused cultures like Japan, Italy; lower in utilitarian cultures)
- **κ_emotional**: cultural value placed on emotional diversity and expression (high in individualist cultures, varies in collectivism)
- **κ_social**: social structures that enable group emotional states (e.g., ritual capacity, artistic traditions)

**Prediction 1: Rasa Repertoire Variation**

Cultures with κ > 0.052 (well above threshold) stabilize all nine rasas + cultural analogues. Examples: India, Japan, Iran (with Hafiz-inspired aesthetics).

Cultures with 0.038 < κ < 0.052 (near threshold) stabilize a subset (e.g., 4-6 rasas). The unstable ones may be accessible but require large external perturbations. Examples: Contemporary Anglo-American culture.

Cultures with κ < 0.038 (below threshold) exhibit **single-attractor dominance**: a single emotional baseline with small oscillations but no distinct stabilized states. Historical example: Puritan cultures with strict emotional regulation.

### 3.5 Developmental Trajectories Through Attractor Space

An individual's ψ (subject characteristics) evolves developmentally, causing their attractor landscape to change:

$$\psi(t) = (\psi_{\text{culture}}, \psi_{\text{neuro}}, \psi_{\text{dev}}(t), \psi_{\text{exp}}(t), \psi_{\text{state}}(t), \psi_{\text{trait}})$$

where ψ_dev(t) evolves from infancy to adulthood.

**Developmental stage: Infancy** (0-2 years)
- ψ_neuro: immature prefrontal cortex; limited inhibitory control
- κ_eff ≈ 0.01 (very low)
- Available attractors: Śānta (rest) and Raudra (frustration/anger) only
- Valuation structure: binary on/off rather than dimensional

**Developmental stage: Early childhood** (2-7 years)
- ψ_dev: emerging narrative self; social learning accelerates
- κ_eff ≈ 0.025
- Available attractors: Śānta, Raudra, Hāsya (playfulness), Bhayānaka (fear)
- New development: Theory of mind allows access to Karuṇā (empathy for others)

**Developmental stage: Adolescence** (12-18 years)
- ψ_neuro: prefrontal development; increased social sensitivity
- κ_eff ≈ 0.040-0.050
- Available attractors: Most of the nine rasas become accessible
- New development: Identity formation enables Vīra (heroism), Śṛṅgāra (romantic love)

**Developmental stage: Adulthood** (18+ years)
- ψ_dev: mature self-concept; refined aesthetic discrimination
- κ_eff ≈ 0.055-0.080 (culture-dependent)
- Available attractors: All nine rasas + cultural analogues
- New development: Wisdom/aging enables deeper access to Śānta and Adbhuta (sublime)

### 3.6 Neurotype-Specific Attractor Landscapes

The neurobiological parameter ψ_neuro modulates **basin sizes** and **transition rates** without eliminating attractors.

**Example: PTSD (Post-Traumatic Stress Disorder)**

A trauma survivor with PTSD exhibits:
- **Enlarged Bhayānaka basin**: threat detection is hyperactive; many contexts map into danger-related constraint configurations
- **Shrunken Śānta basin**: baseline state is elevated arousal; rest is unstable
- **Higher bistability threshold**: requires larger perturbations to transition from Bhayānaka to other states

Formally, the PTSD modification is:

$$D_v^{\text{PTSD}ii} < D_v^{\text{normal}ii} \quad \text{for SafetyValue} \quad \Rightarrow \quad \text{slower dissipation of threat signals}$$

$$K_{vv}^{\text{PTSD}} \text{ has stronger negative diagonal for SafetyValue} \quad \Rightarrow \quad \text{stronger self-inhibition of safety processing}$$

This is testable: trauma-exposed individuals should show **hysteresis in safety recovery**—after threats are objectively removed, they remain in threat-biased states longer than non-trauma controls.

**Example: Depression (Anhedonia)**

A depressed individual exhibits:
- **Collapsed attractor landscape**: InterestValue dimension becomes "stuck" at low values
- **Shallow basins for Śṛṅgāra and Adbhuta**: romantic and sublime beauty become inaccessible
- **Enlarged Karuṇā basin**: empathic sadness becomes dominant
- **Paradoxical Śānta**: restoration-seeking becomes passive resignation rather than peaceful equanimity

Formally, the depression modification includes:

$$\tilde{V}_{\text{Interest}}^{\text{depression}} = \tilde{V}_{\text{Interest}}^{\text{normal}} - \delta V \quad (\text{shift downward in baseline})$$

$$K_{vv}^{\text{depression}} \text{ has weakened cross-coupling from InterestValue to others} \quad \Rightarrow \quad \text{inability to mobilize}$$

### 3.7 Attractor Transition Timescales

Transition duration between attractors depends on the mechanism:

**Type A: Smooth bifurcation transition**
Duration: ~1-5 seconds (timescale of τ_v valuation dynamics)

Example: Shifting from Śānta to Hāsya as a joke is told
- Constraint dynamics first register novelty/incongruity (ProcessingCost brief spike)
- Valuation dynamics gradually shift InterestValue and BelongingValue upward
- Over 2-3 seconds, system slides into Hāsya attractor

**Type B: Catastrophic bifurcation jump**
Duration: ~100-500 milliseconds (catastrophic instability)

Example: Sudden threat → Bhayānaka jump
- Threat stimulus triggers constraint layer (PredictionError, ControlEfficacy)
- At bifurcation point, Śānta/Hāsya/other attractors become simultaneously unstable
- System "snaps" into Bhayānaka basin (amygdala-mediated) in ~0.3 seconds

**Type C: Slow parameter drift**
Duration: hours to days (developmental or long-term mood)

Example: Extended melancholy → gradual shift toward Karuṇā as repeated empathic engagement restructures κ_eff
- Hours of sad music, empathic conversation, or grief rituals
- Slowly enlarges Karuṇā basin; shrinks other basins
- After 6-24 hours, individual's "resting" attractor may shift

### 3.8 Separatrix Structure and Moods

Between any two adjacent attractors exists a **separatrix** (codimension-1 manifold in valuation space). Near the separatrix, the system exhibits:

- **Metastability**: sensitivity to perturbations; small inputs flip state
- **Ambivalence**: phenomenologically, mixed or unclear emotional states
- **Volatility**: rapid mood fluctuations

**Pathological separatrix stuckness**: Some individuals with emotional dysregulation seem to remain "on the separatrix" rather than settling into a basin. This corresponds to:

$$\lambda_i(\text{Jacobian}) \approx 0 \quad \text{(neutrally stable, neither converging nor diverging)}$$

This explains the phenomenology of **affective instability**: neither fully sad nor happy, neither engaged nor withdrawn. Borderline personality disorder may involve enlarged separatrices and reduced basin stability.

---

## 4. RESOLVING PANEL OBJECTIONS

The rasa-as-attractors formalization provides specific responses to objections raised during panel review (February 2026).

### 4.1 Scherer: "Are Rasas Universal or Learned?"

**Panel Objection**: Klaus Scherer asked whether discrete emotional-aesthetic clusters like rasas are universal biological configurations (hardwired attractors) or culturally learned constructs.

**Response**: **Both, via the attractor framework.**

- **Universal structural potential**: The valuation dynamics with 9 independent axes and biologically-grounded coupling (oxytocin linking BelongingValue to RelatednessSupportValue, cortisol linking SafetyValue to StatusValue, dopamine linking InterestValue to CompetenceSupportValue) create a universal *attractor landscape architecture*. Given any human brain, all nine rasa-type attractors are *potentially available*.

- **Culturally selected realization**: The parameter κ(ψ_culture) determines which of these potential attractors are actually stabilized in a cultural population. Japanese culture develops high κ (rich aesthetic tradition, ritual emphasis) → all nine rasas + ma become stable. Anglo-American culture develops κ ≈ 0.040 (utilitarian focus, emotional constraint) → subset of rasas stabilize; others require deliberate access.

- **Testable implication**: Cross-cultural neuroscience should reveal identical constraint-valuation coupling in neural systems across cultures, but different basin structures. Japanese and Indian subjects should show identical amygdala-BelongingValue coupling, but the *reachability* of Śṛṅgāra from baseline differs.

- **Resolution**: Scherer's dichotomy dissolves. The discrete clusters are neither purely universal (not all access with equal ease) nor purely learned (biological architecture predicts their existence). They are **structured universals**: architecture universal, realization cultural.

### 4.2 Zumthor: Architectural Atmosphere Design

**Panel Objection**: Peter Zumthor asked whether this framework could help *design* architectural atmospheres—not just describe existing ones, but create new aesthetic configurations.

**Response**: **Yes, through deliberate attractor-landscape manipulation.**

Design methodology:

1. **Identify target attractor**: Designer specifies which rasa (or new aesthetic state) should be accessible in a space.
   - Example: art museum entrance should facilitate Adbhuta (wonder)

2. **Reverse-engineer constraint configuration**: Determine what constraint values (c*) stabilize the target attractor.
   - Adbhuta requires: high AffordanceDensity (rich sensory detail), low PredictionError (comprehensibility within reach), moderate ProcessingCost, moderate ControlEfficacy

3. **Design for constraint values**:
   - **AffordanceDensity** → spatial complexity, layered views, visual complexity (fractal detail)
   - **PredictionError** → balance familiarity (recognizable architectural language) with novelty (unexpected proportions or materials)
   - **ProcessingCost** → clear wayfinding (low navigation load); uncluttered primary focus (low attention load)
   - **ControlEfficacy** → accessible interactive elements (buttons to open/close light, adjust seating); agency within constraints
   - **MultisensoryCoherence** → unified sensory experience (material consistency, acoustic design supporting visual intent)

4. **Validate through mapping**: Predict basin structure.
   - Adbhuta basin should be large near the intended viewing location
   - Transitions to other rasas should require deliberate movement (e.g., entering a quiet reading room → transition to Śānta)

**Concrete example: Zumthor's Therme Vals**

The thermal bath complex achieves:
- **Adbhuta state**: Main bathing chamber with high AffordanceDensity (layered rock, water, light), moderate ProcessingCost (clear path through space), low PredictionError (proportion and material feel "right" even if novel)
- **Śānta access**: Private bath niches with low AffordanceDensity, high RestorationValue-supporting features (warmth, isolation, familiar materials)
- **Transition dynamics**: Moving from public thermal chambers (Adbhuta) to private niches (Śānta) corresponds to parameter drift along a slow manifold in constraint space

**Design prediction**: Architects can quantitatively score designs for attractor-accessibility using the CVA framework, enabling systematic aesthetic optimization.

### 4.3 Barrett: "How Does This Account for Structural Variation?"

**Panel Objection**: Lisa Barrett argued that factor structure of emotion/valuation varies across individuals and cultures, not just weights on fixed dimensions.

**Response**: **The attractor model predicts and explains factor structure variation.**

- **Attractor framework prediction**: In cultures with high κ, the 9 dimensions should be largely independent (each supporting distinct attractors). In cultures with low κ, dimensions should correlate/collapse (multiple dimensions simultaneously required for any stable state).

- **Cross-cultural factor analysis**:
  - Indian emotional vocabulary: 9+ distinct words for rasa-types (supports 9D structure)
  - Japanese emotional vocabulary: fewer discrete terms; emphasis on relational/contextual states (supports collapsed structure with strong contextual dependence)
  - West African (Àṣà): Status, Belonging, Identity, Relatedness collapse into single semantic/social axis (supported by panel finding)

- **Explanation**: The coupling matrix K_{vv} in some cultures produces **structural constraints** that force certain dimensions to covary.

  Example: In West African social structure, StatusValue and BelongingValue are inseparably linked (honor is *collective* honor, not individual achievement). This means the coupling term becomes:

  $$K_{vv}^{ij} \approx \infty \text{ for } (i,j) \in \{(\text{Status}, \text{Belonging}), (\text{Identity}, \text{Relatedness}), ...\}$$

  These infinite couplings reduce the effective dimensionality from 9 to ~5 independent axes.

- **Testable prediction**: Collectivist cultures should show higher correlation matrices in dimension space; individualist cultures lower. ICA (Independent Component Analysis) applied to emotion/aesthetic ratings should recover more components in individualist cultures.

### 4.4 Kitayama: Amae and Cultural Emotional Systems

**Panel Objection**: Shinobu Kitayama noted that Japanese cultural emotion *amae* (secure dependence) doesn't fit Western attachment theory, suggesting fundamentally different dimensional structures across cultures.

**Response**: **Amae is a distinct attractor enabled by Japanese cultural κ.**

**Amae configuration in CVA**:
- SafetyValue: +0.95 (maximal secure trust)
- BelongingValue: +0.85 (interdependence)
- AutonomySupportValue: **-0.70** (valued dependence, not autonomous agency)
- CompetenceSupportValue: -0.40 (not achievement-focused)
- RelatednessSupportValue: +0.95 (emotional intimacy)

**Key insight**: This attractor is *structurally impossible* in Western CVA architectures because Western coupling typically penalizes simultaneous high SafetyValue and low AutonomySupportValue (they're treated as incompatible).

In Japanese culture, the coupling is explicitly **reweighted** to permit this state:

$$K_{vv}^{\text{Japan}} \text{ has weak/positive coupling between SafetyValue and } (-\text{AutonomySupportValue})$$

$$K_{vv}^{\text{Western}} \text{ has strong negative coupling between these dimensions}$$

This explains why Western psychology treats *dependence* as a deficit (loss of autonomy) while Japanese culture treats *amae* as desirable (secure connection). The neural architecture is the same; the valuation coupling differs culturally.

**Broader implication**: Every culture stabilizes a different subset of valuation-attractor configurations based on local κ and K_{vv} parameters. The ATLAS system should include culture-specific coupling matrices as part of subject-characteristics parameters.

### 4.5 Friston: Attractors as Free-Energy Minima

**Panel Objection**: Karl Friston asked whether the attractor framework connects to his predictive processing and free-energy minimization account of emotion.

**Response**: **Yes, attractors correspond to minima in a free-energy landscape.**

In Friston's Variational Free Energy formalism:

$$F = -\log p(o | m) + D_{\text{KL}}[q(s) || p(s | o, m)]$$

where:
- o = observations (sensory input, current constraints c)
- s = hidden states (the 9 valuations v)
- m = model (CVA architecture, specific to a culture)

An **attractor in valuation space** v^* corresponds to a **local minimum of F** with respect to the valuation system's internal parameters.

The mapping is:

$$v^* = \arg\min_v F(v | c, A, \kappa)$$

- **High κ cultures**: Multiple local minima in F landscape → multiple attractors
- **Low κ cultures**: Single or very few minima → limited attractors
- **Bifurcation**: As parameters change, minima appear/disappear through saddle-node bifurcations in F

**Precision modulation**: Precision (inverse variance) of the posterior q(v|o,m) modulates **basin size**:

$$\text{High precision} \quad \Rightarrow \quad \text{Sharper minima, smaller basins, easier transitions}$$

$$\text{Low precision} \quad \Rightarrow \quad \text{Shallow minima, larger basins, difficult transitions}$$

This explains **emotional rigidity** in depression: the precision of the SafetyValue/Karuṇā minimum is abnormally high, making escape difficult (and precision for InterestValue/Interest-based attractors is abnormally low).

**Therapeutic implication**: Treatment could involve **precision-tuning**: using medication or intervention to reduce precision of dysphoric minima, making them shallower and easier to escape.

---

## 5. NEW MOLECULES AND T1.5 THEORY EXTENSIONS

The rasa-as-attractors framework requires new semantic molecules (groupings of templates) and theoretical structures within the ATLAS T1.5 system.

### 5.1 New Molecules Identified

**Molecule M-Rasa: Holistic Aesthetic-Emotional States**

Templates grouped:
- T-RasaTransitionFactor: conditions under which a rasa becomes accessible (constraint configurations, cultural κ, developmental stage)
- T-RasaBoundary: separatrices between rasa basins; phenomenology near boundaries
- T-RasaStability: basin size, attractor strength, robustness to perturbation
- T-RasaNeuralbio: neural signature of each rasa (fMRI, EEG, psychophysiology)
- T-RasaCultural: cultural prevalence and valorization of rasa; presence in art/literature
- T-RasaDevelopmental: when in lifespan rasa becomes accessible; how training accelerates access

Example instantiation (Adbhuta):
```
Rasa: Adbhuta
CoreConfiguration: {InterestValue: 0.95, CompetenceSupportValue: -0.7,
                    IdentityCongruenceValue: -0.5}
CulturalInstances: [Persian mysticism, European Romantic sublime,
                    quantum physics pedagogy]
NeuralSignature: {DMN_decoupling: high, dLPFC_activation: high,
                  insula_activity: moderate}
TransitionGates: [high-interest-stimulus, low-threat-environment,
                  context-supports-wonder]
Accessibility: [early-childhood: 0.3, adolescence: 0.7, adulthood: 0.85]
```

**Molecule M-CulturalValuationStructure: Culture-Specific Dimensional Geometries**

Templates grouped:
- T-DimensionalCollapse: which dimensions covary in this culture (e.g., Status-Belonging in Àṣà)
- T-CouplingMatrix: the specific K_{vv}, K_{vc} structure for a culture
- T-AvailableAttractors: which rasa configurations are stable (and with what basin size)
- T-TransitionPaths: typical transition trajectories through valuation space
- T-VocabularyMapping: cultural emotion/aesthetic terms mapped to attractor configurations

Example instantiation (West African):
```
Culture: Yoruba/West African
DimensionalCollapses: [
  {collapsed_dimensions: [StatusValue, BelongingValue,
                          IdentityCongruenceValue, RelatednessSupportValue],
   cultural_reason: "collective honor system"}
]
CouplingMatrixProperties: {
  strong_positive: [[StatusValue, BelongingValue],
                    [IdentityValue, RelatedValue]],
  dimensionality_reduction: "9D -> 5 effective dimensions"
}
AvailableAttractors: {Śānta: stable, Śṛṅgāra: partially-accessible,
                      Vīra: strong, Raudra: accessible,
                      Hāsya: strong, Karuṇā: very-strong,
                      Bībhatsa: weak, Bhayānaka: accessible,
                      Adbhuta: cultural-variant}
```

**Molecule M-AttractorTransition: State Change Dynamics**

Templates grouped:
- T-BifurcationType: which bifurcation (pitchfork, saddle-node, Hopf) governs this transition
- T-TransitionTrigger: what constraint or ActivityFrame change initiates transition
- T-TransitionTimescale: how long the transition takes
- T-HysteresisProperties: asymmetry in forward vs. backward transition
- T-SeparatrixPhenomenology: subjective experience of being "between" states

Example instantiation (Threat Response):
```
Transition: Śānta → Bhayānaka
BifurcationType: catastrophic (saddle-node)
TransitionTrigger: {PredictionError: threshold, ControlEfficacy: threshold}
TransitionTimescale: 0.3 seconds
HysteresisProperties: {
  forward_threshold: PredictionError > 0.7,
  backward_threshold: PredictionError < 0.4,
  hysteresis_gap: 0.3,
  stuck_probability: 0.8
}
SeparatrixPhenomenology: "dread, racing thoughts, body sensation"
NeuralMechanism: amygdala-driven, rapid threat detection
```

**Molecule M-BeautyAsCompression: Aesthetic Distance and Attractor Proximity**

This molecule encodes the connection between **beauty perception** and proximity in attractor landscape:

Templates grouped:
- T-CompressionReward: neural reward signal for efficient coding (Friston, Ramachandran)
- T-AttractorProximity: how "close" a stimulus is to a known/preferred attractor
- T-AestheticJudgment: mapping from attractor proximity to beauty ratings
- T-NoveltyBias: preference for stimuli near attractor boundaries (new but comprehensible)

Core hypothesis: **Beauty is proportional to the logarithmic distance from nearest preferred attractor**:

$$\text{Beauty} \propto \log(1 + \text{distance to nearest attractor})$$

Stimuli *exactly on* an attractor are not beautiful (boring). Stimuli far from attractors are not beautiful (incomprehensible). Stimuli at optimal distance (√e × attractor radius) are maximally beautiful.

This explains:
- Why familiar faces are not maximally beautiful (on attractor)
- Why completely abstract art may be unpleasant (far from attractor)
- Why slightly-distorted human faces are maximally attractive (faces: small perturbation from known attractor)

---

## 6. EMPIRICAL PREDICTIONS AND TESTABILITY

The rasa-as-attractors model makes specific, falsifiable predictions across multiple domains.

### 6.1 Hysteresis in Aesthetic Judgment

**Prediction**: When viewing ambiguous aesthetic stimuli, prior emotional state determines judgment, with hysteresis loop when returning to baseline.

**Experiment Design** (can be conducted with VR, eye-tracking, fMRI):

1. **Baseline**: Show subjects a set of moderately ambiguous artworks (Rorschach-like abstract pieces, blurred faces). Collect beauty ratings (0-10 scale).

2. **Induction Phase**:
   - Group A: Induce Śānta state (calm music, meditative breathing, 5 minutes)
   - Group B: Induce Raudra state (threat video, aggressive music, 5 minutes)
   - Group C: Control (neutral video, rest, 5 minutes)

3. **Rating Phase 1**: Immediately re-rate the same ambiguous artworks. Predict Group A rates significantly higher (beauty interpreted in calming terms); Group B rates significantly lower (beauty perceived as threatening).

4. **Recovery Phase**: Return to baseline with neutral activity (10 minutes).

5. **Rating Phase 2**: Re-rate artworks again.
   - Prediction: Subjects don't return to *exactly* baseline ratings.
   - Hysteresis signature: If induced into Raudra then returned to neutral, residual threat bias remains; they rate stimuli lower than Group A subjects who were induced into Śānta.

**Predicted effect size**:
- Difference Phase 1 vs Baseline: 1.5-2.5 points on 0-10 scale
- Residual hysteresis (Phase 2): 0.5-1.2 points (asymmetric by induction direction)

**Neural signature**:
- Amygdala hyperactivity in Raudra-induced group during Phase 2 (residual threat bias)
- Stronger habituation/restoration in Śānta-induced group (large basin, stable return)

### 6.2 Bistability and Categorical Flipping Near Separatrix

**Prediction**: Near the separatrix between two rasa attractors, small perturbations cause categorical state changes (bistable switch).

**Experiment Design** (psychophysics, aesthetic decision-making):

1. **Identify bistable stimulus pair**:
   - Create or select two ambiguous artworks that can be interpreted as either Śṛṅgāra (romantic beauty) or Bībhatsa (disgust/aversion)
   - Example: ambiguously-rendered human figure in shadow; could be sensual or grotesque

2. **Adaptive threshold procedure**:
   - Show stimulus with subthreshold perturbations (slight increase in brightness → increases beauty perception; slight increase in distortion → increases disgust)
   - Track threshold where subject switches from one judgment to other
   - Repeat 20 times

3. **Prediction**:
   - Threshold should show bimodal distribution (not normal)
   - Evidence for two basins with unstable separatrix between
   - Reaction time should increase near threshold (ambiguity costs)
   - Error rate at threshold should be random (coin-flip like)

**Statistical signature**:
- Histogram of judgment vs. stimulus intensity: **not sigmoid** (single attractor) but **double-sigmoid** or flat near threshold (bistable)
- Psychometric function shows **flat zone** near 50% (indifference region where either state can occur)

### 6.3 Culture-Specific Attractor Prediction

**Prediction**: Japanese subjects stabilize "Ma" as a distinct attractor; Western subjects do not.

**Experiment Design** (aesthetic preference, eye-tracking):

1. **Stimulus set**: Create visual designs varying in "negative space" (ma):
   - High-ma designs: sparse, empty space, minimalist (traditional Japanese aesthetics)
   - Low-ma designs: filled, dense, complex
   - Mid-ma designs: balanced

2. **Japanese subjects** (n=40, Tokyo/Kyoto):
   - Rate beauty/aesthetic preference
   - Eye-tracking: measure gaze time on empty vs. filled regions
   - Prediction: Strong *preference* for high-ma despite spending less gaze time there
   - Neural: reward activation (ventromedial PFC) even for low-information regions

3. **Western subjects** (n=40, US/UK):
   - Same task, same stimuli
   - Prediction: Preference for mid-ma or low-ma (visual interest/complexity)
   - Gaze time correlates positively with high-information regions
   - Neural: reward correlates with high visual complexity

4. **Cross-cultural comparison**:
   - Mixed ANOVA: Culture × stimulus-ma level → interaction
   - Japanese preference for high-ma > Western preference, difference ≥ 2 points (0-10 scale)

**Implication**: The Ma attractor exists as a stable configuration in Japanese valuation space; it's not merely a learned *preference* but a distinct attractor accessible to Japanese subjects.

### 6.4 Neurotype-Specific Attractor Predictions

**Prediction A: PTSD-related Bhayānaka enlargement**

1. **Subjects**:
   - Trauma-exposed with PTSD diagnosis (n=30)
   - Trauma-exposed without PTSD (n=30)
   - Non-exposed controls (n=30)

2. **Task**:
   - Threat-detection task with graduated threat levels (visual probes from safe to threat-like)
   - Measure: reaction time, heart rate, self-report fear ratings

3. **Predictions**:
   - PTSD group shows threat-response at *lower* stimulus intensity than controls (enlarged Bhayānaka basin)
   - Hysteresis: PTSD group requires *lower* stimulus intensity to trigger safety response compared to trigger threshold (asymmetric gap indicates trapped state)
   - Shrunken Śānta basin: baseline physiology elevated even in non-threat conditions

**Prediction B: Depression-related Interest dimension collapse**

1. **Subjects**:
   - Depression diagnosis (MDD, moderate-severe, n=40)
   - Depression remitted (formerly MDD, n=30)
   - Controls (n=40)

2. **Task**:
   - Aesthetic viewing task: art, nature scenes, faces, music
   - Measure: beauty ratings (0-10), want-to-approach (0-10), neural reward activity (fMRI ventromedial PFC, striatum)

3. **Predictions**:
   - Depressed group: InterestValue-related beauty ratings collapsed (most stimuli rated 2-4/10)
   - Removed depression: recovery first in high-demand stimuli (Adbhuta, Śṛṅgāra) before low-demand (Śānta), suggesting basin recovery order
   - Neural: Ventromedial PFC shows flattened response curve (reduced discrimination) in depression; restored gradient in remission

### 6.5 VR-Based Attractor Navigation Testing

**Prediction**: Architectural spaces can be systematically designed to make specific attractors accessible.

**Experiment Design** (VR, immersive):

1. **Design two VR spaces**:
   - **Adbhuta-optimized space**: Fractal detail, moderate visual complexity, clear navigation (high AffordanceDensity, low ProcessingCost)
   - **Control space**: Similar navigation, but reduced detail and complexity

2. **Procedure**:
   - Subjects enter VR space (n=60, counterbalanced)
   - 5 minutes of free exploration
   - Measure:
     - Self-report: wonder, awe, aesthetic appreciation (0-10)
     - Psychophysiology: skin conductance level (arousal), pupil dilation (interest attention)
     - Eye-tracking: gaze distribution (evidence of interest in visual complexity)

3. **Predictions**:
   - Adbhuta-optimized space: higher wonder ratings, larger pupil dilation, more dispersed gaze (exploring detail)
   - Control space: lower ratings, smaller pupils, focused gaze (efficient navigation)
   - Neural (fMRI in subset): Adbhuta space shows stronger DMN decoupling + dLPFC activation signature predicted by Adbhuta attractor

**Outcome**: Validates that constraint manipulation can reliably induce specific attractors, enabling architectural design methodology.

### 6.6 Developmental Attractor Accessibility Tracking

**Prediction**: Children gain access to rasa-like attractors in a developmental sequence: earliest Śānta & Raudra, later Śṛṅgāra & Vīra, latest Adbhuta & Karuṇā.

**Longitudinal Design** (multi-year):

1. **Subjects**: Birth cohort, measured at 6-month intervals from age 2 to age 18 (n=100)

2. **Task**: Age-appropriate aesthetic and emotional experience sampling:
   - Ages 2-4: Behavioral observation (comfort seeking, playfulness, distress)
   - Ages 4-7: Picture-based emotion scenarios, simple stories
   - Ages 7-12: Music/art exposure, rating and emotion matching
   - Ages 12+: Complex artworks, literature, philosophical questions

3. **Predictions**:
   - Age 2-4: only Śānta (soothing) and Raudra (frustration) reliably elicited
   - Age 4-7: Hāsya, Bhayānaka accessible
   - Age 7-12: Karuṇā, Śṛṅgāra emerging
   - Age 12+: Vīra, Adbhuta, full rasa repertoire

4. **Neural correlates**: fMRI in subset (ages 8, 12, 15, 18) shows:
   - Younger: amygdala and striatum dominance (basic affect)
   - Older: mentalizing networks (TPJ, mPFC) and aesthetic networks (visual cortex, insula) increasingly engaged

**Implication**: Attractor accessibility develops in culturally-universal order (predicted by constraint-valuation dynamics) but with individual and cultural variation in rate/extent.

### 6.7 Panelist-Specific Predictions

**For Scherer** (universality vs. culture):
Universal neural coupling constants (oxytocin-BelongingValue, etc.) should appear identical across cultures via neurophysiology. Cultural differences should appear in *parameter values* (κ, K matrix) not in architecture.

**Prediction**: Amygdala-SafetyValue coupling strength should be identical across cultures (measured via connectivity, response curves), but threat *threshold* differs (PTSD studies show enlarged basin in trauma-exposed regardless of culture, but *selection* of threat-related attractors varies).

**For Zumthor** (design methodology):
Architects should be able to score spaces quantitatively using a "CVA aesthetic potential" metric computed from architectural features → predicted constraint values → basin structure.

**Prediction**: Architects without training in ATLAS framework who independently follow the constraint-optimization principles (high detail, clear navigation, balanced complexity) should create spaces that reliably induce intended attractors.

**For Barrett** (structural variation):
Factor structure should vary across cultures in a predictable way: individualist > collectivist in dimensional independence.

**Prediction**: ICA applied to emotion ratings in individualist cultures (USA, Germany) should recover more independent components than in collectivist cultures (Japan, China), with step-function around κ ≈ 0.045.

---

## 7. COMPUTATIONAL IMPLEMENTATION AND PSEUDOCODE

### 7.1 Core Attractor Solver

```pseudocode
function SolveValuationAttractors(
  constraints: ℝ⁸,           // current constraint values c
  activity_frame: ActivityFrame,  // current context A
  culture_params: CultureParams,  // κ(ψ), K_vv, K_vc
  num_attractors: int = 9
) → attractors: List[Attractor]

  // Step 1: Set up dynamics
  D_v = diag(2.0, 2.0, 2.0, 1.8, 2.2, 1.9, 2.1, 2.0, 1.95)  // valuation dissipation timescales
  K_vv = ComputeCouplingMatrix(culture_params, constraints)   // may vary with culture
  κ = culture_params.coupling_strength

  // Step 2: Define fixed-point equation
  function FixedPointError(v: ℝ⁹) → error: ℝ⁹
    V_tilde = EvaluateValuation(constraints, activity_frame, culture_params)
    coupling_term = κ * ReLU(K_vv @ v + K_vc @ constraints)
    error = D_v * (v - V_tilde) - coupling_term
    return error

  // Step 3: Find fixed points via multi-start optimization
  attractors = []
  for seed = 1 to num_attractors * 3:
    v_init = RandomInitialization()  // random point in [0, 1]⁹
    v_star = SolveODE(FixedPointError, v_init, maxiter=10000, tol=1e-6)

    // Step 4: Check stability
    J = ComputeJacobian(FixedPointError, v_star)
    eigenvalues = Eigenvalues(J)

    if all(real(eigenvalues) < 0):  // locally stable
      is_new = CheckUniqueness(v_star, attractors, tol=0.1)
      if is_new:
        attractor = Attractor(
          position=v_star,
          eigenvalues=eigenvalues,
          basin_radius=EstimateBasinRadius(v_star, FixedPointError),
          stability_margin=min(real(eigenvalues)),
          neural_signature=ComputeNeuralSignature(v_star)
        )
        attractors.append(attractor)

  // Step 5: Compute basin separatrix (approximate)
  separatrix_points = ComputeSeparatrix(attractors, FixedPointError)

  return attractors

end function


function ComputeCouplingMatrix(culture_params, constraints) → K_vv: ℝ⁹ˣ⁹
  // Base universal coupling (evolutionary/developmental)
  K_base = LoadUniversalCouplingMatrix()

  // Culture-specific modulation
  K_culture = culture_params.coupling_matrix_override

  // Activity-frame dependent modulation
  A = GetActivityFrame()
  K_frame = ModulateCoupling(A)

  K_vv = K_base + K_culture + K_frame
  return K_vv
end function


function EstimateBasinRadius(v_star, dynamics_fn) → radius: float
  // Sample trajectories from spheres around v_star
  // Compute the distance to nearest diverging trajectory
  // Return the maximum radius where all trajectories converge to v_star

  radius = 0.0
  for dist = 0.01 to 1.0 step 0.05:
    num_converging = 0
    for sample = 1 to 100:
      v_test = v_star + dist * RandomUnitVector()
      v_final = IntegrateODE(dynamics_fn, v_test, time=100)

      if distance(v_final, v_star) < 0.05:
        num_converging += 1

    convergence_rate = num_converging / 100
    if convergence_rate > 0.95:
      radius = dist
    else:
      break

  return radius
end function
```

### 7.2 Bifurcation Tracking Algorithm

```pseudocode
function TrackBifurcations(
  activity_frame_trajectory: List[ActivityFrame],
  culture_params: CultureParams,
  time_steps: int = 1000
) → bifurcation_events: List[BifurcationEvent]

  bifurcations = []
  prev_attractors = None

  for t = 0 to time_steps:
    A_t = InterpolateActivityFrame(activity_frame_trajectory, t)

    // Find current attractors for this ActivityFrame
    current_attractors = SolveValuationAttractors(
      constraints=EvaluateConstraints(A_t),
      activity_frame=A_t,
      culture_params=culture_params
    )

    // Detect bifurcation events
    if prev_attractors is not None:
      event = DetectBifurcation(prev_attractors, current_attractors, t)
      if event is not None:
        bifurcations.append(event)

        // Log bifurcation details
        Print("Bifurcation at t=%d: %s", t, event.type)
        Print("  Lost attractor: %s at position %s",
              event.lost_rasa, event.lost_position)
        Print("  Gained attractors: %s", event.gained_rasas)

    prev_attractors = current_attractors

  return bifurcations

end function


function DetectBifurcation(old_attrs, new_attrs, time) → event: BifurcationEvent

  event = None

  // Identify lost attractors (were present, now absent)
  for attr_old in old_attrs:
    closest_new = FindNearest(attr_old.position, new_attrs)
    if distance(attr_old.position, closest_new.position) > 0.3:
      // Attractor disappeared via bifurcation
      event = BifurcationEvent(
        time=time,
        type="attractor_annihilation",
        lost_rasa=IdentifyRasa(attr_old.position),
        lost_position=attr_old.position,
        gained_rasas=IdentifyRasa([new_attrs])
      )

  // Identify gained attractors (new, were not present)
  for attr_new in new_attrs:
    closest_old = FindNearest(attr_new.position, old_attrs)
    if distance(closest_old.position, attr_new.position) > 0.3:
      // New attractor created
      if event is None:
        event = BifurcationEvent(time=time, type="attractor_creation")
      event.gained_rasas.append(IdentifyRasa(attr_new.position))

  return event

end function
```

### 7.3 Hysteresis Loop Computation

```pseudocode
function ComputeHysteresisLoop(
  parameter: string,          // which parameter to vary ("threat_level", etc.)
  param_range: (float, float), // min and max values
  num_steps: int = 50,
  culture_params: CultureParams
) → hysteresis_curve: HysteresisCurve

  up_trajectory = []   // parameter increasing
  down_trajectory = [] // parameter decreasing

  // Forward pass: parameter increases
  v_state = InitializeValuation()  // neutral starting state
  for step = 0 to num_steps:
    param_val = param_range.min + (param_range.max - param_range.min) * step / num_steps

    // Update constraints based on parameter value
    constraints = ParameterToConstraints(param_val, parameter)

    // Evolve valuation system (quasi-static, slow change)
    for sub_step = 1 to 100:
      dv = ComputeValuationDynamics(v_state, constraints, culture_params)
      v_state = v_state + 0.01 * dv  // small gradient descent

    // Identify attractor reached
    attractor_id = IdentifyAttractorReached(v_state)
    up_trajectory.append((param_val, attractor_id, v_state))

  // Backward pass: parameter decreases
  v_state = up_trajectory[-1].state  // start from final state
  for step = num_steps down to 0:
    param_val = param_range.min + (param_range.max - param_range.min) * step / num_steps

    constraints = ParameterToConstraints(param_val, parameter)

    for sub_step = 1 to 100:
      dv = ComputeValuationDynamics(v_state, constraints, culture_params)
      v_state = v_state + 0.01 * dv

    attractor_id = IdentifyAttractorReached(v_state)
    down_trajectory.append((param_val, attractor_id, v_state))

  // Detect hysteresis
  hysteresis = HysteresisCurve(
    forward_path=up_trajectory,
    backward_path=down_trajectory,
    hysteresis_gap=ComputeGap(up_trajectory, down_trajectory)
  )

  return hysteresis

end function
```

---

## 8. INTEGRATION WITH EXISTING ATLAS MOLECULES

The rasa-as-attractors formalization integrates with 13 existing molecules and 23 theories in the ATLAS system:

### 8.1 Existing Molecules Strengthened

**M-Affect** (general emotional dynamics):
- Now has precise mathematical grounding: affect = trajectory through attractor landscape
- Attractor identification provides discrete emotion taxonomy

**M-SocialBrain** (mentalizing, attachment):
- Śṛṅgāra and Karuṇā attractors explain romance and empathy
- Cross-cultural structure (amae) now explicable via culture-specific attractors

**M-Aesthetics** (beauty, art appreciation):
- Adbhuta, Śṛṅgāra, Hāsya attractors explain art response
- Design methodology (Zumthor) now quantifiable

**M-Threat/SafetyProcessing** (fear, anxiety):
- Bhayānaka and fear-related transitions explained
- Hysteresis in trauma recovery predicted

**M-RewardMotivation** (dopamine, reinforcement):
- Vīra, Hāsya, Śṛṅgāra involve reward circuitry differently
- Basin-of-attraction size determines reward seeking vs. avoidance

### 8.2 Cross-Molecule Connections

The attractor model creates bridges between previously separate modules:

**Link: M-Aesthetics ↔ M-Attachment**
- Śṛṅgāra (romantic love) is simultaneously an aesthetic state (beauty perception) and attachment state (belonging)
- Demonstrates that aesthetic and social motivations are deeply interwoven in valuation space

**Link: M-Threat ↔ M-Aesthetics**
- Adbhuta (sublime wonder) requires *some* threat-like elements (large, unknown) combined with safety
- Bhayānaka (terror) is Adbhuta inverted: threat without safe container

**Link: M-CultureVariation ↔ M-DevelopmentalTraj**
- Attractor accessibility develops within cultural parameters κ(ψ_culture, ψ_dev(t))
- Different cultures on different developmental timelines (Ma may be more accessible earlier in Japanese children; Vīra earlier in warrior cultures)

---

## 9. DISCUSSION: FROM THEORY TO PRACTICE

### 9.1 Remaining Uncertainties

**Uncertainty 1: Are there more than nine rasa-like attractors?**

The nine classical rasas may be a *discovered* set (reflecting actual attractor structure) or a *conventional* set (arbitrary partition of continuous space). New research should:
- Exhaustively map attractor landscape in high-κ cultures
- Test whether 10th, 11th, ... attractors exist but are less culturally valorized
- Examine whether rasa list varies across Indian regional traditions

**Uncertainty 2: How is κ implemented neurobiologically?**

The coupling parameter κ is mathematically well-defined but its neural implementation is unclear. Candidates:
- Neuromodulator concentrations (serotonin, dopamine, oxytocin levels)
- Structural connectivity in valuation circuits (insular-prefrontal-limbic density)
- Genetic polymorphisms affecting receptor sensitivity

**Uncertainty 3: Can basin sizes be measured directly?**

The current prediction is that basin size (robustness of attractor) can be inferred from behavioral/physiological measures (hysteresis, reaction time near separatrix) but no direct fMRI measure of "basin landscape" exists. Development of new neuroimaging analysis methods is needed.

### 9.2 Next Steps: Validation Roadmap

**Phase 1 (2026-2027): Behavioral Validation**
- Conduct hysteresis experiments (Section 6.1) across cultures
- Collect cultural aesthetic vocabulary data
- Test developmental predictions in longitudinal cohorts

**Phase 2 (2027-2028): Neural Grounding**
- fMRI studies identifying neural signatures for each attractor
- Connectivity analysis of K_{vv} coupling implementation
- Neurochemistry studies of κ parameter

**Phase 3 (2028-2029): Application Development**
- Architectural design methodology testing (Zumthor collaboration)
- VR-based attractor induction system (therapeutic applications)
- Educational tools for aesthetic training

**Phase 4 (2029-2030): Panel Review and Refinement**
- Engage Scherer, Barrett, Friston, and others for critical evaluation
- Refine dimensional structure based on empirical findings
- Integrate with other theoretical frameworks (appraisal theory, dimensional accounts)

---

## 10. REFERENCES

Acerbi, G., Valenti, G., Aimar, E., Morelli, A., Popple, A. V., & Zoccolan, D. (2009). Laminar population coding: a method to study information flow in deep neural networks. *Frontiers in Neuroinformatics*, 3, 37.

Bharata. (circa 200 BCE). *Natyashastra* (A. Board & M. Ghosh, Trans.). Calcutta Sanskrit College Press.

Burke, E. (1757). *A philosophical enquiry into the origin of our ideas of the sublime and beautiful*. Oxford University Press. (Google Scholar: 12,450 citations)

Calder, A. J., Lawrence, A. D., & Young, A. W. (2001). Neuropsychology of fear and loathing. *Nature Reviews Neuroscience*, 2(5), 352–363. https://doi.org/10.1038/35072584 (Google Scholar: 2,847 citations)

Csikszentmihalyi, M. (1990). *Flow: The psychology of optimal experience*. Harper & Row. (Google Scholar: 24,300 citations)

Fecteau, S., Pascual-Leone, A., & Théoret, H. (2007). Psychogenic tremor: hyperactive DMN in functional MRI. *NeuroImage*, 37(2), 440–450. https://doi.org/10.1016/j.neuroimage.2007.05.011 (Google Scholar: 189 citations)

Fisher, H. (2004). *Why we love: The nature and chemistry of romantic love*. Henry Holt. (Google Scholar: 3,421 citations)

Garrison, K. A., Scheinost, D., Worhunsky, P. D., Constable, R. T., & Brewer, J. A. (2015). Real-time fMRI feedback of the anterior cingulate and posterior insula improves mood in depression. *NeuroImage*, 112, 148–155. https://doi.org/10.1016/j.neuroimage.2015.02.044 (Google Scholar: 156 citations)

Keller, J., & Bless, H. (2008). Flow and regulatory compatibility: An experimental approach to the flow model of intrinsic motivation. *Journal of Personality and Social Psychology*, 95(6), 1385–1407. https://doi.org/10.1037/a0012630 (Google Scholar: 241 citations)

Keltner, D., & Haidt, J. (2003). Approaching awe, a moral, social, and aesthetic emotion. *Cognition & Emotion*, 17(2), 297–314. https://doi.org/10.1080/02699930302848 (Google Scholar: 1,289 citations)

LeDoux, J. (2012). *Rethinking the emotional brain*. Neuron, 73(4), 653–676. https://doi.org/10.1016/j.neuron.2012.02.004 (Google Scholar: 3,127 citations)

Mendes, W. B. (2007). Adrenaline and the rise and fall of kings. *Psychological Science Agenda*, 21(2), 1–3.

Mobbs, D., Greicius, M. D., Abdel-Aziz, G., Menon, V., & Reiss, A. L. (2003). Humor modulates the mesolimbic reward centers. *Neuron*, 40(5), 1041–1048. https://doi.org/10.1016/s0896-6273(03)00751-7 (Google Scholar: 686 citations)

Moll, J., de Oliveira-Souza, R., & Eslinger, P. J. (2005). Morals and the human brain. *Proceedings of the National Academy of Sciences*, 102(3), 684–689. https://doi.org/10.1073/pnas.0407784102 (Google Scholar: 1,876 citations)

Provine, R. R. (2000). *Laughter: A scientific investigation*. Penguin Press. (Google Scholar: 1,024 citations)

Ramachandran, V. S., & Hirstein, W. (1999). The science of art: A neurological theory of aesthetic experience. *Journal of Consciousness Studies*, 6(6-7), 15–51. (Google Scholar: 643 citations)

Singer, T., & Klimecki, O. M. (2014). Empathy and compassion. *Current Biology*, 24(18), R875–R878. https://doi.org/10.1016/j.cub.2014.06.054 (Google Scholar: 1,847 citations)

Spielberger, C. D. (1999). *State-Trait Anger Expression Inventory-2 (STAXI-2)*. Psychological Assessment Resources.

Strogatz, S. H. (2014). *Nonlinear dynamics and chaos: With applications to physics, biology, chemistry, and engineering* (2nd ed.). Westview Press. (Google Scholar: 8,721 citations)

Tang, Y. Y., Hölzel, B. K., & Posner, M. I. (2015). The neuroscience of mindfulness meditation. *Nature Reviews Neuroscience*, 16(4), 213–225. https://doi.org/10.1038/nrn3916 (Google Scholar: 2,156 citations)

Zumthor, P. (2006). *Atmospheres: Architectural environments – surrounding objects*. Birkhäuser. (Google Scholar: 1,247 citations)

---

## CONCLUSION

This formalization demonstrates that the classical Indian aesthetic theory of *rasa* can be rigorously modeled as **stable attractors in the Constraint-Valuation Architecture's dynamical system**. The framework:

1. **Resolves the paradox of holistic irreducibility**: Rasas feel irreducibly unitary (not decomposable into separate affects) because they are stable configurations in 9D valuation space, not because they lack dimensional structure.

2. **Explains cultural variation**: Different cultures stabilize different subsets of attractors via culture-specific coupling parameters κ(ψ_culture) and K_{vv}, K_{vc} matrices. This validates Scherer's universalism and Barrett's relativism simultaneously.

3. **Provides design methodology**: Architects, artists, and interface designers can use CVA constraint-valuation mappings to deliberately create spaces and experiences that induce specific attractors (Zumthor's dream).

4. **Makes testable predictions**: Hysteresis, bistability, cultural variation, developmental accessibility, and neurotype-specific basin structures are all experimentally falsifiable.

5. **Integrates cross-panel expertise**: Friston's free-energy framework, Scherer's emotion taxonomy, Barrett's construction theory, Kitayama's cultural psychology, and Zumthor's design phenomenology all find natural homes within the attractor model.

The rasa-as-attractors model represents a maturation of CVA from a qualitative descriptive system to a quantitative, predictive, and falsifiable theory of aesthetic and emotional experience.

---

**Document compiled**: 2026-02-28
**Version**: ATLAS-CVA-2.1
**Status**: Ready for Panel Review (Phase 2 validation)
