**ATLAS Architecture**

**Terminology & Concept Cheat Sheet v2.0**

*Epistemic Network · Bayesian Network · Projection Bridge*

February 2026 · v2.0

**1. The Three-Layer Architecture**

The ATLAS system separates epistemic assessment (what we know) from operational prediction (what we expect). They are connected by a projection function π that translates one into the other.

  ------------------------ -------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------
                           **Epistemic Network (EN)**                                                                                           **Projection Bridge (π)**                                                                                       **Bayesian Network (BN)**
  **Core question**        How well-supported is each causal claim, by what kind of evidence, from which populations?                           How should epistemic assessments translate into operational parameters for a specific context and population?   Given the operational model, what will happen if we intervene?
  **Graph type**           Labeled directed multigraph (cycles OK, parallel edges OK)                                                           Function: EN → BN                                                                                               Directed acyclic graph (DAG) --- standard Pearl SCM
  **Numbers it carries**   Warrant strength (ω): degree of belief in the evidential bridge                                                      Transfer reliability (d): how much survives transfer. Population factor (δ): population mismatch attenuation.   CPT entries: P(X \| parents). What actually happens in the world.
  **What edges mean**      "Evidence of type τ supports the claim that A relates to C"                                                          Translates each EN edge into a CPT contribution                                                                 "A causally influences C in this specific context"
  **Is it Bayesian?**      NO. Coherentist structure (Quine). Permits cycles, parallel edges, typed edges. Does not satisfy Markov condition.   Bridges coherentist epistemology to Bayesian computation                                                        YES. Standard Bayesian Network. do-calculus applies.
  **Who populates it**     Article Eater + expert review (from published research)                                                              System architecture (fixed mapping τ → d)                                                                       Computed by π from EN inputs
  ------------------------ -------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------

**2. The Four Numbers (Don't Confuse Them)**

  --------------------- ----------------------------------------------- --------------------------------------------------- -------------------------------------------------------------------------- --------------------------------------------------------
                        **Warrant Strength (ω)**                        **Transfer Reliability (d)**                        **Population Factor (δ)**                                                  **Conditional Probability (CPT)**
  **Lives in**          EN (on each edge)                               Bridge (set by τ)                                   Bridge (per context)                                                       BN (on each edge)
  **Measures**          How well-supported is this specific evidence?   How much of this EVIDENCE TYPE survives transfer?   How well does evidence from THIS population transfer to THAT population?   What actually happens in the world given these inputs?
  **Uncertainty**       EPISTEMIC (reducible)                           EPISTEMIC (structural)                              EPISTEMIC (reducible by studying target pop.)                              ALEATORY (irreducible)
  **What 0.80 means**   "Quite confident this evidence is solid"        "This type retains 80% on transfer"                 "Populations fairly similar"                                               "80% chance of this outcome"
  **Can change?**       Yes --- new studies                             No --- set by type hierarchy                        Yes --- studying target pop.                                               Yes --- recomputed by π
  **Prose name**        \"Degree of belief\"                            \"Transfer reliability\"                            \"Population transfer factor\"                                             \"Probability of outcome\"
  --------------------- ----------------------------------------------- --------------------------------------------------- -------------------------------------------------------------------------- --------------------------------------------------------

**Projection formula: logit(p\_target) = d(τ) · ω · δ(pop, pop\_target) · logit(p\_lab)**

**3. The Seven Warrant Types**

Ordered by transfer reliability (Woodward's invariance range). Fifth column shows where each type makes a real difference.

  ------------------------------------- ------- ------------------------------------------------------------------- ---------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Warrant Type**                      **d**   **What It Means**                                                   **Plain English**                                                **Working Example (Where It Bites)**
  **CONSTITUTIVE**                      0.95    Identity / definitional. Not a causal claim.                        Lab variable IS the architectural variable by definition.        Window-to-wall ratio = glazed area ÷ wall area. Architect changes window size, asks "Will daylight increase?" EN answers with near-certainty (ω=0.95). No study needed. No population matters. d=0.95 because even definitions have edge cases (does a translucent panel count?).
  **MECHANISM**                         0.80    Known causal pathway with identified entities & activities.         We know WHY and HOW A causes C through specific intermediates.   Lambert et al. (2002): daylight → retinal ganglion cells → raphe nuclei → serotonin. Architect asks "Will this work in Mumbai?" Mechanism is biological, conserved across humans, d=0.80. WHERE IT BITES: if hospital uses UV-filtered glass blocking melanopsin-activating wavelengths, mechanism breaks at link 1. EN knows EXACTLY where to check.
  **EMPIRICAL\_ASSOCIATION**            0.80    Replicated statistical association, mechanism unknown.              We know THAT A and C covary but not WHY.                         Beauchemin & Hays (1996): sunny rooms → shorter stays. Replicated. Architect asks "Will this work in my facility?" Problem: is it the light, the view, the warmth, or staff behavior? WHERE IT BITES: correlation might vanish in a windowless facility with excellent artificial light --- revealing it was the view, not the light. Without mechanism, can't predict which factor matters.
  **FUNCTIONAL**                        0.65    Known functional role, mechanism unknown.                           We know WHAT it does but not HOW.                                Nature exposure "serves as stress reducer" (Kaplan, 1995). But: attention restoration? Autonomic? Evolutionary? Architect puts green wall in underground car park. WHERE IT BITES: if mechanism is attention restoration (needs sustained engagement), a glimpsed wall won't work. If autonomic (reflexive), even a glimpse might suffice. Can't predict without mechanism.
  **CAPACITY**                          0.55    System CAN produce the effect; hasn't been shown in this context.   Possibility, not actuality.                                      Lab: humans discriminate 0.2s reverberation differences. Therefore acoustics COULD affect spaciousness. WHERE IT BITES: lab used headphones, pure tones, focused attention. Real lobby has background noise, visual distractions, social chatter. The capacity may never be exercised in situ. CAN ≠ DOES.
  **ANALOGICAL**                        0.40    Cross-domain transfer via structural similarity.                    Evidence from domain X applied to Y by analogy.                  Fractals reduce stress in natural landscapes (Hägerhäll, 2004). Analogy: fractals in building facades should too. WHERE IT BITES: if calming is about nature-signaling (safe environment), not geometry per se, then fractal concrete facades won't trigger it. Surface features differ even if deep structure matches.
  **THEORY\_DERIVED \[theory name\]**   0.25    Prediction from named theory. No direct test.                       Theory says this should happen. Nobody has checked.              Predictive processing predicts moderate facade complexity minimizes prediction error → preference. Tag: \[Predictive Processing\]. WHERE IT BITES: same EEG data = "low prediction error" (PP theory) OR "soft fascination" (Attention Restoration). Different theories → different design recommendations. EN tracks WHICH theory, so all dependent edges update when theories are tested.
  ------------------------------------- ------- ------------------------------------------------------------------- ---------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**4. How Evidence Combines**

  --------------------------- ------------------------------------------------- ------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Rule**                    **When It Applies**                               **Formula**                                                               **Working Example**
  **Serial (Chain)**          Inferring through intermediates: A → B → C → D.   d\_eff = min(d\_i). Weakest link dominates.                               Fractal → cortical response (MECH, d=0.80) → prediction error (THEORY, d=0.25) → stress (THEORY, d=0.25) → wellbeing (EMPIRICAL, d=0.80). Effective d = 0.25. Theory links are the bottleneck.
  **Parallel (Convergent)**   Multiple independent lines for same claim.        Additive in log-odds: Σ d\_i · ω\_i · logit(p\_i)                         Daylight → mood: (1) MECHANISM via serotonin (ω=0.85) + (2) EMPIRICAL\_ASSOC from hospital studies (ω=0.70). Two lines sum in log-odds → stronger than either.
  **Explanatory Boost**       Mechanism explains existing association.          \(a\) Add mechanism as parallel path. (b) Increase ω on empirical edge.   Car mechanic: 20 successful repairs = EMPIRICAL\_ASSOC (ω=0.70). Learns WHY (gas/oxygen ratio) = new MECHANISM path. Also: ω on empirical edge rises to 0.82 (confounding less likely). Theory/mechanism NEVER decreases confidence.
  --------------------------- ------------------------------------------------- ------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**5. The Dual-BN Diagnostic**

For every BN edge, the system computes three diagnostics to separate empirical evidence from theoretical scaffolding.

  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Diagnostic**          **Definition**                                                                                                                                                                                                          **Working Example**
  **Full Projection**     Standard computation using ALL links including THEORY\_DERIVED. Best estimate. Goes into BN's CPT.                                                                                                                      Fractal → wellbeing: d\_eff=0.25, P≈0.58. Daylight → mood: d\_eff=0.80, P≈0.74.
  **Empirical Floor**     Projection using ONLY empirically grounded links (CONSTITUTIVE, MECHANISM, EMPIRICAL\_ASSOC, FUNCTIONAL). Remove THEORY\_DERIVED, ANALOGICAL, CAPACITY. Chain survives → lower estimate. Chain breaks → floor = 0.50.   Fractal: chain BREAKS (no empirical path from cortical response to stress). Floor = 0.50. Daylight: all links grounded. Floor = 0.74 = full projection.
  **Theory Dependence**   EMPIRICALLY GROUNDED (floor/full \> 0.80). THEORY-AUGMENTED (0.40--0.80). THEORY-SCAFFOLDED \[name\] (floor ≈ 0.50 / chain breaks).                                                                                     Daylight: EMPIRICALLY GROUNDED. Fractal: THEORY-SCAFFOLDED \[Predictive Processing\]. Dual-BN comparison: theory-inclusive model recommends windows + fractals. Empirical-only model recommends windows, is silent on fractals.
  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**6. Population Transfer Factors (δ)**

Most evidence comes from WEIRD populations (Henrich et al., 2010). δ formalizes the population mismatch.

  -------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Dimension**              **What It Captures**                                                            **How It Affects δ**                                                       **Working Example**
  **Cultural distance**      Individualist vs. collectivist, aesthetic traditions, built-environment norms   High distance → low δ                                                      Optimal fractal D≈1.3 from Scandinavian subjects. India fieldwork suggests different preferences. δ≈0.45 (WEIRD-only). After India study: δ≈0.85.
  **Demographic distance**   Age, SES, education                                                             Large mismatch → low δ                                                     Thermal comfort from 20-year-olds. Target: elderly care (mean age 78). Thermoregulation changes with age. δ≈0.40. One elderly study raises to ≈0.80.
  **Neurodiversity scope**   Whether study included neurodiverse participants                                Neurotypical-only + neurodiverse target → δ drops. May involve REVERSAL.   Open-plan offices: positive for neurotypical extraverts, REVERSES for ADHD/autism (sensory overload). δ can't handle reversal --- need explicit moderator node.
  **Ecological validity**    Lab vs. field, acute vs. chronic                                                Lab-only → lower δ                                                         Color preference: 30-sec lab exposure to swatches. Target: hospital rooms, years of exposure. Chronic adaptation differs. "Blue is calming" may not hold. δ≈0.50.
  -------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------

**7. What the EN Has That the BN Doesn't**

  ---------------------------------------------------- ----------------------------------------------- ------------------------------------------------------------------ ---------------------------------------------------------
  **EN Feature**                                       **Why It's in the EN**                          **Why Not in the BN**                                              **Where Info Goes**
  **Latent states (raphe nuclei, prediction error)**   Real intermediate processes in causal chains.   Architect can't measure/manipulate. BN nodes must be actionable.   Collapsed into CPTs. 5-step neural chain → one BN edge.
  **Theoretical claims**                               Organizing principles generating predictions.   Too abstract for probability distributions.                        Contributes to ω of lower-level claims.
  **Parallel edges**                                   Multiple evidence types for same claim.         BN has exactly ONE edge between any pair.                          Aggregated by π via log-odds summation.
  **Warrant type / strength**                          WHAT KIND of evidence and HOW GOOD.             BN edges are untyped (Pearl).                                      Consumed by π to compute CPTs.
  **Population metadata**                              Records who was studied.                        BN is context-specific already.                                    Consumed by π to compute δ.
  **Cycles**                                           Mutual epistemic support.                       BN must be DAG (do-calculus requires it).                          Resolved during projection.
  ---------------------------------------------------- ----------------------------------------------- ------------------------------------------------------------------ ---------------------------------------------------------

The BN has: CPTs (object-level probabilities), do-calculus (intervention computation), Markov condition (conditional independence). These are computational tools the EN lacks. Division of labor: EN for epistemology, BN for computation, π for translation.

**8. Key Structural Principles**

  ------------------------------------- ----------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------
  **Principle**                         **Statement**                                                                                                                 **Why It Matters**
  **Accordion (Mechanisms)**            Mechanisms at multiple granularity. Type stays MECHANISM. Strength ω increases with elaboration (coarse: 0.60; fine: 0.90).   Elaboration raises confidence, not type. You don't need the full molecular chain to call it MECHANISM.
  **Theory vs. Mechanism**              THEORY explains WHY mechanisms exist (d=0.25). MECHANISM is a specific worldly process (d=0.80). Different strata in EN.      Predictive processing PREDICTS cortical coding should reduce stress. Serotonergic pathway IS a mechanism doing it.
  **Measurement ≠ Mechanism**           EEG, fMRI, skin conductance are measurement instruments, not part of mechanisms.                                              "Fractals produce EEG patterns" = MECHANISM. "EEG patterns reflect prediction error" = THEORY\_DERIVED. Different types.
  **Interactions = Edge Annotations**   Most interactions annotate existing edges. Well-established ones can be promoted to moderator nodes.                          Avoids O(N²) edge explosion while preserving information.
  **S-Node Guidance**                   EN types inform S-node placement: MECHANISM → precise; EMPIRICAL\_ASSOC → everywhere; CONSTITUTIVE → none.                    Fills the gap Pearl left open in transportability analysis.
  ------------------------------------- ----------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------

**9. Quick Reference: All Symbols**

  ------------ ---------------------------- -----------------------------------------------------------------------------------------------------------------
  **Symbol**   **Name**                     **Definition**
  EN           Epistemic Network            W = (N, E, τ, ω, pop). Coherentist structure. The body of evidence.
  BN           Bayesian Network             DAG + CPTs. Pearl SCM. Causal inference engine.
  π            Projection Function          EN → BN. Translates epistemology into operational parameters.
  τ            Warrant Type                 ∈ {CONSTITUTIVE, MECHANISM, EMPIRICAL\_ASSOCIATION, FUNCTIONAL, CAPACITY, ANALOGICAL, THEORY\_DERIVED \[name\]}
  ω            Warrant Strength             Degree of belief in evidential bridge. ∈ (0,1). Meta-level: evidence quality.
  d            Transfer Reliability         How much evidence of type τ survives transfer. ∈ (0,1). Fixed by τ.
  δ            Population Transfer Factor   Attenuation for population mismatch. ∈ (0,1).
  pop          Population Metadata          On each EN edge: culture, age, neurodiversity, SES, sample size.
  CPT          Conditional Prob. Table      P(X \| Pa(X)). Object-level BN content. Columns sum to 1.
  do(X=x)      Intervention                 Pearl's operator: set X to x, sever incoming edges.
  logit(p)     Log-odds                     log(p/(1−p)). Maps (0,1) to real line for projection.
  SCM          Structural Causal Model      Structural equations X = f(Pa(X), U) + DAG.
  S-node       Selection Node               Pearl & Bareinboim: marks context-varying variables in transportability.
  ------------ ---------------------------- -----------------------------------------------------------------------------------------------------------------
