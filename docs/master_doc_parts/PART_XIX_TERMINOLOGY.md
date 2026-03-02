# PART XIX: TERMINOLOGY AND CONCEPT REFERENCE (§140)

*This Part provides a consolidated reference guide to the ATLAS system's core concepts, mathematical framework, and notation. It distils the theoretical and technical material from Parts I–XVIII into a quick-reference format designed for practitioners, panel members, and anyone needing to navigate the system's vocabulary and visual models.*

---

## §140: Quick Reference — The ATLAS Cheat Sheet v2.0 {#140}

### 140.1 The Three-Layer Architecture

The ATLAS system separates epistemic assessment (what we know) from operational prediction (what we expect). They are connected by a projection function π that translates one into the other.

| **Aspect** | **Epistemic Network (EN)** | **Projection Bridge (π)** | **Bayesian Network (BN)** |
|---|---|---|---|
| **Core question** | How well-supported is each causal claim, by what kind of evidence, from which populations? | How should epistemic assessments translate into operational parameters for a specific context and population? | Given the operational model, what will happen if we intervene? |
| **Graph type** | Labeled directed multigraph (cycles OK, parallel edges OK) | Function: EN → BN | Directed acyclic graph (DAG)—standard Pearl SCM |
| **Numbers it carries** | Warrant strength (ω): degree of belief in the evidential bridge | Transfer reliability (d): how much survives transfer. Population factor (δ): population mismatch attenuation. | CPT entries: P(X \| parents). What actually happens in the world. |
| **What edges mean** | "Evidence of type τ supports the claim that A relates to C" | Translates each EN edge into a CPT contribution | "A causally influences C in this specific context" |
| **Is it Bayesian?** | NO. Coherentist structure (Quine). Permits cycles, parallel edges, typed edges. Does not satisfy Markov condition. | Bridges coherentist epistemology to Bayesian computation | YES. Standard Bayesian Network. do-calculus applies. |
| **Who populates it** | Article Eater + expert review (from published research) | System architecture (fixed mapping τ → d) | Computed by π from EN inputs |

### 140.2 The Four Numbers (Do Not Confuse Them)

| **Aspect** | **Warrant Strength (ω)** | **Transfer Reliability (d)** | **Population Factor (δ)** | **Conditional Probability (CPT)** |
|---|---|---|---|---|
| **Lives in** | EN (on each edge) | Bridge (set by τ) | Bridge (per context) | BN (on each edge) |
| **Measures** | How well-supported is this specific evidence? | How much of this EVIDENCE TYPE survives transfer? | How well does evidence from THIS population transfer to THAT population? | What actually happens in the world given these inputs? |
| **Uncertainty** | EPISTEMIC (reducible) | EPISTEMIC (structural) | EPISTEMIC (reducible by studying target pop.) | ALEATORY (irreducible) |
| **What 0.80 means** | "Quite confident this evidence is solid" | "This type retains 80% on transfer" | "Populations fairly similar" | "80% chance of this outcome" |
| **Can change?** | Yes—new studies | No—set by type hierarchy | Yes—studying target pop. | Yes—recomputed by π |
| **Prose name** | "Degree of belief" | "Transfer reliability" | "Population transfer factor" | "Probability of outcome" |

**Projection formula:** logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)

### 140.3 The Seven Warrant Types

Ordered by transfer reliability (Woodward's invariance range).

| **Warrant Type** | **d** | **What It Means** | **Plain English** |
|---|---|---|---|
| **CONSTITUTIVE** | 0.95 | Identity / definitional. Not a causal claim. | Lab variable IS the architectural variable by definition. |
| **MECHANISM** | 0.80 | Known causal pathway with identified entities & activities. | We know WHY and HOW A causes C through specific intermediates. |
| **EMPIRICAL_ASSOCIATION** | 0.80 | Replicated statistical association, mechanism unknown. | We know THAT A and C covary but not WHY. |
| **FUNCTIONAL** | 0.65 | Known functional role, mechanism unknown. | We know WHAT it does but not HOW. |
| **CAPACITY** | 0.55 | System CAN produce the effect; hasn't been shown in this context. | Possibility, not actuality. |
| **ANALOGICAL** | 0.40 | Cross-domain transfer via structural similarity. | Evidence from domain X applied to Y by analogy. |
| **THEORY_DERIVED [theory name]** | 0.25 | Prediction from named theory. No direct test. | Theory says this should happen. Nobody has checked. |

### 140.4 How Evidence Combines

| **Rule** | **When It Applies** | **Formula** |
|---|---|---|
| **Serial (Chain)** | Inferring through intermediates: A → B → C → D. | d_eff = min(d_i). Weakest link dominates. |
| **Parallel (Convergent)** | Multiple independent lines for same claim. | Additive in log-odds: Σ d_i · ω_i · logit(p_i) |
| **Explanatory Boost** | Mechanism explains existing association. | (a) Add mechanism as parallel path. (b) Increase ω on empirical edge. |

### 140.5 The Dual-BN Diagnostic

For every BN edge, the system computes three diagnostics to separate empirical evidence from theoretical scaffolding.

| **Diagnostic** | **Definition** |
|---|---|
| **Full Projection** | Standard computation using ALL links including THEORY_DERIVED. Best estimate. Goes into BN's CPT. |
| **Empirical Floor** | Projection using ONLY empirically grounded links (CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOC, FUNCTIONAL). Chain survives → lower estimate. Chain breaks → floor = 0.50. |
| **Theory Dependence** | EMPIRICALLY GROUNDED (floor/full > 0.80). THEORY-AUGMENTED (0.40–0.80). THEORY-SCAFFOLDED [name] (floor ≈ 0.50). |

### 140.6 Population Transfer Factors (δ)

Most evidence comes from WEIRD populations (Henrich et al., 2010). δ formalizes the population mismatch.

| **Dimension** | **What It Captures** | **How It Affects δ** |
|---|---|---|
| **Cultural distance** | Individualist vs. collectivist, aesthetic traditions, built-environment norms | High distance → low δ |
| **Demographic distance** | Age, SES, education | Large mismatch → low δ |
| **Neurodiversity scope** | Whether study included neurodiverse participants | Neurotypical-only + neurodiverse target → δ drops. May involve REVERSAL. |
| **Ecological validity** | Lab vs. field, acute vs. chronic | Lab-only → lower δ |

### 140.7 Key Structural Principles

| **Principle** | **Statement** | **Why It Matters** |
|---|---|---|
| **Accordion (Mechanisms)** | Mechanisms at multiple granularity. Type stays MECHANISM. Strength ω increases with elaboration (coarse: 0.60; fine: 0.90). | Elaboration raises confidence, not type. You don't need the full molecular chain. |
| **Theory vs. Mechanism** | THEORY explains WHY mechanisms exist (d=0.25). MECHANISM is specific worldly process (d=0.80). | Predictive processing PREDICTS stress reduction. Serotonergic pathway IS a mechanism. |
| **Measurement ≠ Mechanism** | EEG, fMRI, skin conductance are measurement instruments, not mechanisms. | "Fractals produce EEG patterns" = MECHANISM. "EEG patterns reflect prediction error" = THEORY_DERIVED. |
| **Interactions = Edge Annotations** | Most interactions annotate existing edges. Well-established ones promoted to moderator nodes. | Avoids O(N²) edge explosion while preserving information. |
| **S-Node Guidance** | EN types inform S-node placement: MECHANISM → precise; EMPIRICAL_ASSOC → everywhere; CONSTITUTIVE → none. | Fills the gap Pearl left open in transportability analysis. |

### 140.8 Quick Reference — All Symbols

| **Symbol** | **Name** | **Definition** |
|---|---|---|
| **EN** | Epistemic Network | W = (N, E, τ, ω, pop). Coherentist structure. The body of evidence. |
| **BN** | Bayesian Network | DAG + CPTs. Pearl SCM. Causal inference engine. |
| **π** | Projection Function | EN → BN. Translates epistemology into operational parameters. |
| **τ** | Warrant Type | ∈ {CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL, CAPACITY, ANALOGICAL, THEORY_DERIVED [name]} |
| **ω** | Warrant Strength | Degree of belief in evidential bridge. ∈ (0,1). |
| **d** | Transfer Reliability | How much evidence of type τ survives transfer. ∈ (0,1). Fixed by τ. |
| **δ** | Population Transfer Factor | Attenuation for population mismatch. ∈ (0,1). |
| **CPT** | Conditional Prob. Table | P(X \| Pa(X)). Object-level BN content. Columns sum to 1. |
| **logit(p)** | Log-odds | log(p/(1−p)). Maps (0,1) to real line for projection. |
| **SCM** | Structural Causal Model | Structural equations X = f(Pa(X), U) + DAG. |
| **S-node** | Selection Node | Pearl & Bareinboim: marks context-varying variables in transportability. |

### 140.9 References for §140

Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? *Behavioral and Brain Sciences*, 33(2-3), 61-83. [Google Scholar citations: ~15,000]

Woodward, J. (2003). *Making Things Happen: A Theory of Causal Explanation*. Oxford University Press. [Google Scholar citations: ~3,500]

---

