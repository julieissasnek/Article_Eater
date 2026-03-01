# CVA Mathematical Formalization: Critical Questions for Expert Consultation

**Date**: February 27, 2026
**Prepared for**: Chat (Claude) expert consultation on domains where formalization has gaps

---

## Overview

The mathematical formalization (CVA_MATHEMATICAL_FORMALIZATION_2026-02-27.md) provides rigorous dynamics, identifiability analysis, and beauty models. However, six critical questions remain that require deeper domain expertise in active inference, appraisal theory, and neuroscience. These questions cannot be resolved by internal analysis alone.

---

## 1. Precision-Weighting Under Active Inference: Is ActivityFrame Truly Precision Modulation?

**Problem**: In Section 3 (Active Inference Reformulation), we claim that ActivityFrame IS the precision allocation mechanism. But this assumption needs validation.

**Precise question for Chat**:

In predictive coding frameworks (Friston, Barrett & Simmons), precision weights π_j determine how much each prediction error is corrected:

```
Δx = (1/σ²) · δ_prediction_error
```

We propose that ActivityFrame modulates these precisions:

```
π_j(A) = baseline_π_j · κ_j(A)
```

where κ_j(A) ∈ [0.1, 5] is the activity-dependent modulation for valuation j.

**Specific questions**:
1. Is there empirical evidence that the *same* neural valuation signal (e.g., from orbitofrontal cortex) is *gated* differently depending on task context, OR does the neural signal itself change representation?
2. If it's gating (precision modulation), what are the neural mechanisms? Which neural systems compute and allocate these precisions?
3. If it's representation change, then ActivityFrame restructures the valuation space itself (not just weights it), which contradicts our assumption that the nine-dimensional valuation space is constant.

**Why it matters**: This determines whether CVA's "separability" is real (constant valuations, modulated precision) or illusory (valuations themselves change by activity frame). The answer affects how we model learning and transfer across contexts.

---

## 2. Can Constraint Perception Be Truly Pre-Valuation, or Is Perception Inherently Valuation-Laden?

**Problem**: Section 1.2 assumes constraints f_i(x) are *sensory estimates* prior to valuation. But constructionist psychology (Barrett) and enactive cognition (Varela) both argue perception is valuation-laden from the ground up.

**Precise question for Chat**:

Consider visual constraint perception (e.g., perceiving spatial density):

- **Interpretation 1 (CVA assumption)**: The visual system computes a proto-feature (number of objects, occlusion density), which is *then* weighted by goals to produce a valuation. Perception → Valuation is a real temporal/causal sequence.

- **Interpretation 2 (Constructionist)**: Visual perception is shaped by current goals, emotional state, and cultural context *from the start*. There is no pre-valuation "objective" density; perception is already goal-relative.

**Empirical predictions that would distinguish**:

1. **Backward masking experiment**: If perception is pre-valuation, then masked constraint information (presented for 100ms, then masked) should still influence neural activity patterns even if subjects don't consciously value it. If constructionist, masked information should have no effect because perception requires active valuation.

2. **Cross-cultural invariance**: If constraints are pre-valuation (objective), then the raw perception of density should be invariant across cultures (same eye movements, same neural activity). If perception is valuation-laden, eye movements and neural activity should differ by culture/goal.

**Specific question for Chat**:
- What is the strongest empirical evidence that supports Interpretation 1 (pre-valuation perception)?
- What are the best counterarguments from constructionist psychology, and how might CVA address them without losing its mathematical structure?
- Could CVA work if constraints and valuations are *simultaneous* (not sequential) but still separable analytically?

**Why it matters**: If perception is inherently valuation-laden, then the "constraint" layer in CVA is not truly independent of goals. This weakens the separability claim but might strengthen the unified-inference interpretation (Section 3).

---

## 3. What Neural Evidence Would Prove That BelongingValue and IdentityCongruenceValue Are Real, Separable Valuations?

**Problem**: Eisenberger (Section 2.1) raised the hardest neuro question: Do orbitofrontal and ventromedial prefrontal cortex *separately* encode belonging-specific and identity-specific value, or do they compute *general* value that is post-hoc interpreted as belonging/identity?

**Precise question for Chat**:

Current fMRI evidence shows that OFC/vmPFC respond to various types of value (food, money, social approval, moral judgment). But this doesn't prove *separate channels* for belonging vs. identity.

**What would constitute proof**:

1. **Connectivity evidence**: Do distinct OFC subregions (e.g., medial vs. lateral) have *different* inputs from social-affective systems (anterior insula, ventral ACC, amygdala) and different outputs to motor/action systems?

2. **Lesion/inactivation evidence**: If you selectively inactivate one OFC subregion, does belonging-specific preference disappear while identity-specific preference remains?

3. **Single-unit recording evidence** (in animals): Do distinct neural populations in OFC/vmPFC encode belonging-value vs. autonomy-value vs. competence-value, with different response profiles to constraint manipulations?

**Specific question for Chat**:

- Is there *any* published evidence showing that a specific brain region encodes "belonging value" separately from "identity value"?
- If not, what would be the minimal neuroimaging experiment to provide such evidence?
- Alternatively, is it possible that "belonging" and "identity" are not separable neural values but rather *behavioral interpretations* of a more general "social value" signal?

**Why it matters**: If BelongingValue is not neurally separable, then Deci and Eisenberger are right that it's conceptually useful but neurally unified. This doesn't invalidate CVA, but it affects claims about neural realism.

---

## 4. How Do We Handle Irreducible Complexity and Gestalt Properties in Beauty?

**Problem**: Section 4.4 (Residual-Holistic Model) proposes that formal properties (symmetry, proportion, fractal dimension) contribute independently to beauty. But this raises a hard question: how do we distinguish between "formal properties are independent" vs. "formal properties are *compressed into* the valuation vector"?

**Precise question for Chat**:

Consider ceiling height—a key architectural variable:

- Does ceiling height map to a constraint (SpatialScale, Enclosure, etc.), which then maps to valuations (SafetyValue, RestorativeValue)?
- OR is ceiling height *immediately* perceived as an aesthetic quality (bigness, grandeur, suffocation) without an intermediate constraint layer?

**Operationally, these might be equivalent** (both predict behavior), but they're conceptually different.

**Specific question for Chat**:

1. In the literature on *aesthetic realism* (philosophical aesthetics), what is the strongest argument that beauty is NOT decomposable into separable dimensions, but is instead an irreducible *Gestalt*?

2. In the empirical literature on *perceptual organization* (Pomerantz, Treisman, Feldman), are there properties that are perceived as unified wholes (not as sums of parts)? Can we use these as a model for potentially irreducible aspects of architectural beauty?

3. How would we design an experiment to test whether ceiling height is decomposable into constraints+valuations vs. irreducibly perceived as a unified aesthetic property?

**Why it matters**: If beauty has irreducible Gestalt properties (Zumthor's phenomenology), then CVA's claim that B ≈ L(v) is fundamentally wrong, not just incomplete. This affects the entire compression model.

---

## 5. How Do Cultural and Linguistic Categories Shape the Valuation Space Itself, Not Just Weights?

**Problem**: Section 4.3 (KL-Divergence Model) assumes nine valuation dimensions exist universally, with *culture-dependent weights*. But Kitayama and Barrett both suggest the *structure of the valuation space itself* is culturally constructed.

**Precise question for Chat**:

**Example**: In English, we have separate words/concepts: "autonomy" (independence), "belonging" (group membership), "status" (rank in hierarchy). These suggest three independent dimensions.

But in collectivist cultures, these may not be independent:
- Autonomy is only valued *for the group* (not against it)
- Belonging is *intrinsically tied to* status (you belong in your hierarchical position)
- Status is evaluated relative to the group, not absolutely

**Question**: Are these linguistic/conceptual differences *mere labels* for the same underlying 9D space (universal dimensions with culture-dependent language)? Or do they reflect *actual structural differences* in how valuations are organized?

**Operationally**:

If we perform factor analysis on the 9 CVA valuations separately for individualist and collectivist cultures:
- **Hypothesis 1 (universal structure)**: Same 9 dimensions, different weights
- **Hypothesis 2 (cultural variation)**: Different number of factors, different factor structure

**Specific question for Chat**:

1. In the cross-cultural psychology literature, what is the clearest evidence that the *structure* of psychological needs/values differs across cultures (not just their weights)?

2. If the structure differs, how would we modify the CVA mathematical model to allow the dimensionality of the valuation space to vary by culture?

3. Is it possible to do this while maintaining the mathematical coherence of the model (e.g., the differential equations would need to be re-parameterized for each culture)?

**Why it matters**: If the valuation structure itself is culturally variable, then there is no single "CVA" for all humans—there are culture-specific variants. This changes the model's scope and generalizability claims.

---

## 6. What Is the Mechanism by Which Valuations Feed Back to Reshape Constraint Perception?

**Problem**: Section 1.2 includes a feedback term (ε_fb · ∂V/∂c_i) allowing valuations to bias constraint perception. But the mechanism is underspecified—is this *attention* (selective perception), *predictive coding* (prior adjustment), or something else?

**Precise question for Chat**:

In predictive processing (Friston, Barrett), top-down effects on perception typically work through:

1. **Precision modulation**: Goals make task-relevant signals more precise (easier to detect)
2. **Prior adjustment**: Goals shift Bayesian priors (we expect to see valued things)
3. **Attention**: Goals redirect visual attention (we look harder for valued things)

The CVA model treats this as a simple gain term (ε_fb), but the actual mechanism matters for:
- Predicting which perception errors are corrected
- Designing interventions (e.g., can you reduce false perceptions by rewarding accuracy?)
- Understanding individual differences (high ε_fb = strongly goal-biased perception)

**Specific question for Chat**:

1. Which of the above mechanisms (precision, prior, attention) has the strongest empirical support for goal-dependent perception of *spatial* properties (density, prospect, enclosure)?

2. In architectural perception specifically, do we have evidence that perceiving high spatial density differs by whether you *value* social density (wanting community vs. solitude)?

3. If such evidence exists, what are its effect sizes? Is ε_fb ≈ 0.05–0.15 (as assumed in CVA) empirically plausible?

**Why it matters**: This determines how strongly we should expect constraints to be biased by goals, and therefore how much "causal separation" is actually present in real perception.

---

## 7. Can CVA Handle Irreducibly Temporal and Embodied Aspects of Architectural Experience?

**Problem**: CVA's mathematical formalization treats aesthetic judgment as a static function of constraint values and activity frames. But architectural experience unfolds *over time* and involves *embodied interaction* (movement, proprioception, visceral response).

**Precise question for Chat**:

Consider the experience of entering a tall cathedral:

- First 2 seconds: visual surprise (sudden spatial scale), physiological response (increased arousal, slow deep breathing)
- 10 seconds: cognitive appraisal (recognizing the design intent, relating to scale)
- 1 minute: emotional response (awe, humility, spiritual elevation)

A single valuation vector computed at time t=0 cannot capture this temporal unfolding.

**Specific question for Chat**:

1. In the embodied cognition and architectural phenomenology literature, what are examples of aesthetic experiences that are *irreducibly temporal*—where the experience cannot be captured by a single moment's measurement of constraints and valuations?

2. Is there evidence that embodied properties (how the body *moves* through a space, proprioceptive feedback) substantially affect aesthetic judgment, independent of visual/cognitive appraisal?

3. If so, how would we extend the CVA mathematical model to include temporal dynamics and embodied variables? Would we need:
   - A temporal extension: v(t) not just v?
   - An embodied extension: proprioceptive and movement-related variables added to constraints?
   - A phenomenological extension: first-person narrative description alongside quantitative valuations?

**Why it matters**: If architecture's aesthetic power is fundamentally temporal and embodied (Zumthor's concern), then CVA's static mathematical formulation misses something essential. We'd need to either extend the model substantially or acknowledge its scope limitations.

---

## Summary: Critical Path for Expert Consultation

**Priority 1 (Foundation)**: Questions 1–2 (precision weighting, pre-valuation perception)
- These determine whether the basic CVA architecture is sound

**Priority 2 (Empirical grounding)**: Questions 3–5 (neural separability, cultural variation, beauty decomposition)
- These determine whether the model is empirically realistic

**Priority 3 (Scope)**: Question 6 (temporal/embodied aspects)
- This determines where the model's limitations lie

---

**Document prepared for**: Expert consultation with Chat or specialized consultants
**Expected expert domains**: Active inference, appraisal psychology, cultural neuroscience, phenomenology, aesthetic theory

