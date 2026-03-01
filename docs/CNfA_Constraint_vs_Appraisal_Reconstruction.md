
# CNfA Aesthetics Appraisal Framework
## Constraint vs Appraisal: A Cleaner Conceptual Reconstruction

Version: 1.0  
Goal: Replace ambiguous “appraisal hub” talk with a conceptually tighter account that still supports BN modeling and paper-ingestion.

---

# 1. Why the Term “Appraisal” Is a Problem

You raised the key objection:

> A system affected by clutter or noise is not necessarily “appraising” anything. It may just be a cascade of perceptual/neural events.

This objection bites because “appraisal” has a strong historical meaning in psychology:

- **Classical appraisal theory** treats appraisal as an evaluation of significance relative to goals/needs (often formulated as questions like “Is this harmful?”).
- Many of the phenomena we want to model (fluency, grouping, load, prediction error) look like **constraints on inference** rather than evaluations.

If we keep the word “appraisal” without tightening it, we risk two failures:

1. **Category mistake:** treating computational constraints as value judgments.  
2. **False modularity:** implying there are separable “appraisal systems” when there may be coupled dynamical constraints.

So the reconstruction must do two things simultaneously:

- Provide a non-misleading ontology for fluency/complexity/prediction etc.
- Preserve a route from those variables to behavior (approach/avoid, choice, report).

---

# 2. Three Notions to Separate (and Keep Separate)

## 2.1 Constraint (C)

A **constraint** is a limitation, regularity, or cost function imposed on processing.

Examples:
- Limited attentional capacity
- Grouping principles
- Coding efficiency pressures
- Prediction-error minimization pressures

Constraints do not, by themselves, contain value. They shape what the system can do and at what cost.

## 2.2 Control Signal (U)

A **control signal** is an output that changes allocation of resources, action selection, or physiological state.

Examples:
- Shifts in attention
- Arousal modulation
- Avoidance/approach tendencies
- Exploration vs exploitation

Control signals are direction-sensitive, but not necessarily “evaluations.”

## 2.3 Evaluation (E)

An **evaluation** (in the strong sense) is a mapping that assigns *valence* or *goal relevance*—a “good/bad for me” signal.

Examples:
- Threat value (bad)
- Restorative value (good)
- Status value (good/bad depending on identity)

Evaluation is what motivates calling something appraisal.

**Core idea:** appraisal is not identical to constraint. Appraisal is better treated as a *valuation functional applied to constrained inference outputs*.

---

# 3. A Cleaner Architecture: Constrained Inference → Valuation → Action

Instead of “Appraisal Hubs,” use a two-stage mechanism.

## Stage 1: Constrained Inference Layer (CIL)

This layer computes *representations* under constraints:

- Perceptual organization (grouping, segmentation)
- Scene understanding (layout, affordances)
- Predictive model fit (prediction error)
- Load and uncertainty estimates

Outputs are *descriptive* and *cost-related* quantities:

- Processing cost
- Uncertainty
- Information gain
- Control efficacy estimates
- Feasibility of action plans

Call these **Organizing Variables** or **Constraint Variables**.

## Stage 2: Valuation Layer (VL)

This layer converts descriptive/cost variables into evaluative signals by applying goal-dependent value functions.

Examples:
- If goal is safety, uncertainty in escape routes has negative value.
- If goal is exploration, moderate prediction error has positive value.
- If goal is recovery, low load + soft fascination has positive value.

This is where “Is this safe?” properly belongs.

## Stage 3: Policy/Action Layer (PL)

Evaluative signals influence:

- approach/avoid
- attention allocation
- dwell time
- choices and reports

This is the policy computation layer (decision making).

---

# 4. Re-mapping the Eight Hubs Under the Cleaner Account

We can keep the *same variables* but reclassify them.

## 4.1 Variables that are primarily CONSTRAINT / ORGANIZATION (CIL)

### Fluency (F)
- Best seen as *estimated processing cost* or *coding efficiency*.
- Not inherently evaluative: it becomes evaluative when low cost is valued.

### Complexity regulation (C)
- Best seen as *load/arousal pressure* and *information rate*.
- Again, the evaluation depends on task and trait (sensation seeking).

### Predictability / Surprise (S)
- Best seen as *prediction error / information gain*.
- Not evaluative by itself; interest vs threat depends on value function.

### Affordance fit (A) — mixed
- Includes descriptive feasibility estimates (CIL) plus goal relevance (VL).

**Conclusion:** Fluency, complexity, and surprise belong primarily to *constrained inference*, not appraisal.

## 4.2 Variables that are more directly EVALUATIVE (VL)

### Threat/Safety (T)
- This is a valuation of inferred risk—closer to genuine appraisal.

### Restorativeness (R)
- Valuation of recovery potential; evaluative because it implies “good for regulation.”

### Social signaling (G)
- Valuation depends strongly on cultural identity; still evaluative because it assigns social meaning.

### Prospect/Refuge/Control (P) — mixed
- Control efficacy estimate (CIL) plus safety valuation (VL).

**Conclusion:** Threat, restoration, and social meaning are more naturally “appraisals.”

---

# 5. The Key Payoff: Why This Fix Matters

## 5.1 It resolves the category mistake

You no longer have to pretend that edge density “evaluates.”  
Edge density influences processing cost; valuation then interprets that cost as pleasant/unpleasant depending on context.

## 5.2 It clarifies moderators

Moderators act primarily on valuation functions, not on constraint computations.

Examples:
- Expertise changes the mapping from complexity → cost (CIL), and also the mapping from social signals → value (VL).
- Sensation seeking changes the mapping from prediction error → interest (VL).
- Goal context changes which costs matter (VL).

## 5.3 It improves BN design

In BN terms, you can implement the reconstruction by splitting nodes:

**Constraint Nodes (CIL):**  
ProcessingCost, Uncertainty, InformationGain, ControlEfficacy, Load

**Valuation Nodes (VL):**  
SafetyValue, InterestValue, RestorationValue, StatusValue

Then reports and behavior are children of valuation nodes.

This makes the network more causal and less semantically confused.

---

# 6. A Minimal Formalization

Let x be measurable features.

## 6.1 Constrained inference

Compute constraint variables c:

c = f(x; θ_infer)

Examples:
- ProcessingCost = f_cost(symmetry, clutter, coherence)
- InformationGain = f_IG(prediction error proxy)
- ControlEfficacy = f_control(visibility graph, enclosure)

## 6.2 Valuation

Compute values v given goals g and traits τ:

v = V(c; g, τ)

Examples:
- SafetyValue = V_safe(ControlEfficacy, Darkness, Occlusion; safety_sensitivity)
- InterestValue = V_int(InformationGain, Load; sensation_seeking)
- RestorationValue = V_rest(Load, SoftFascination, NaturalRatio; fatigue_level)

## 6.3 Policy/action

Behavior b:

b ~ π(v; constraints)

Beauty_report is then a language mapping L over v (and social context):

Beauty_report = L(v, culture, instruction)

---

# 7. How the Classic Questions Fit Now

Your list:

- Is this safe?
- Is this coherent?
- Is this overwhelming?
- Is this predictable?
- Does this support my goals?
- Does this signal status?

Under the reconstruction:

- “Is this coherent?” → constraint/inference (low processing cost; high grouping stability)  
- “Is this overwhelming?” → constraint/inference (load rate exceeds capacity)  
- “Is this predictable?” → constraint/inference (low prediction error)  
- “Is this safe?” → valuation (risk evaluation over inferred control/visibility)  
- “Does this support my goals?” → valuation/policy (goal-fit value)  
- “Does this signal status?” → valuation (social meaning/value assignment)

So only some are appraisals in the strong sense.

---

# 8. Practical Recommendations for Your Repo

## 8.1 Rename for conceptual clarity

Replace “Appraisal Hubs” with:

**Constraint–Valuation Architecture**

And split into two namespaces:

- CIL.* (Constraint / Inference variables)
- VL.* (Valuation variables)

Keep your eight hubs as a *crosswalk* category for backward compatibility.

## 8.2 Elevate “valuation nodes” as causal parents

In the BN, make valuation nodes parent behavior and reports, not constraint nodes directly.

Constraints feed valuations; valuations feed outcomes.

## 8.3 Paper ingestion benefits

When you read a paper, ask:

1. Is it reporting a constraint effect (cost, uncertainty, load)?
2. Or a valuation effect (fear, liking, safety preference)?
3. Or a policy outcome (approach, choice)?

This is a powerful sorting principle across the literature.

---

# 9. How This Affects the Beauty Eliminability Claim

Beauty becomes even more clearly eliminable:

Beauty_report is a linguistic mapping over valuation states.

You explain more with fewer metaphysical commitments.

---

# 10. What This Reconstruction Still Needs

A tough point remains:

Some phenomena blur constraint and value (e.g., fluency often correlates with liking).

Empirically, you disambiguate by:

- Manipulating goals (exploration vs safety) while holding features fixed.
- Manipulating cognitive load (fatigue) while holding features fixed.
- Looking for dissociations: same fluency, different liking under different goals.

If dissociations occur, valuation is separate from constraint. If not, you might treat fluency as directly valenced.

---

# Appendix — Crosswalk Table (Old → New)

| Old “Hub” | Primary Role | New Node Family |
|---|---|---|
| ProcessingFluency | Constraint | CIL.ProcessingCost |
| ComplexityRegulation | Constraint | CIL.LoadRate |
| PredictabilitySurprise | Constraint | CIL.PredictionError / CIL.InformationGain |
| ThreatSafety | Valuation | VL.SafetyValue |
| ProspectRefugeControl | Mixed | CIL.ControlEfficacy + VL.SafetyValue |
| Restorativeness | Valuation | VL.RestorationValue |
| AffordanceFit | Mixed | CIL.ActionFeasibility + VL.GoalFitValue |
| SocialSignaling | Valuation | VL.StatusValue / VL.IdentityValue |

---

# Bottom line

If you want conceptual cleanliness:

- Treat fluency/complexity/surprise as **constraints on inference**.
- Treat safety/restoration/status as **valuations** applied to inferred states.
- Treat approach/choice/report as **policy outputs**.

You can still keep the 8 hubs as a practical spine, but the internal semantics become much tighter.

