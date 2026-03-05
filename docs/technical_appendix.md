**ATLAS Technical Appendix**

**Formulas, Numerical Worked Examples, and Projection Mechanics**

February 2026 --- v1.0

**A.1 Core Formulas**

**A.1.1 The Log-Odds Transform**

The log-odds (logit) function maps probabilities from the interval (0, 1) to the real line (−∞, +∞). This is necessary because we need to attenuate probabilities multiplicatively without producing values outside \[0, 1\].

**logit(p) = ln(p / (1 − p))**

Key values:

logit(0.50) = 0.000 (ignorance prior = zero in log-odds)

logit(0.60) = 0.405

logit(0.70) = 0.847

logit(0.72) = 0.944

logit(0.80) = 1.386

logit(0.90) = 2.197

logit(0.95) = 2.944

The inverse (sigmoid) maps back:

**σ(x) = 1 / (1 + exp(−x))**

**A.1.2 Single-Edge Projection**

For a single EN edge with lab-derived probability p\_lab, warrant type τ, warrant strength ω, and population factor δ:

**logit(p\_target) = d(τ) · ω · δ · logit(p\_lab)**

**p\_target = σ(logit(p\_target))**

This attenuates the lab finding toward the ignorance prior (p = 0.50, logit = 0). The stronger the evidence (ω), the closer the transfer reliability (d), and the better the population match (δ), the more of the lab finding survives.

**A.1.3 Serial Combination (Chain)**

For a serial chain of edges e₁, e₂, \..., eₖ through intermediate nodes:

**d\_eff = min(d(τ(e\_1)), d(τ(e\_2)), \..., d(τ(e\_k)))**

**ω\_eff = ∏ ω\_i (product of all warrant strengths)**

**δ\_eff = min(δ\_i) (weakest population match)**

The effective projection is then:

**logit(p\_target) = d\_eff · ω\_eff · δ\_eff · logit(p\_lab)**

**A.1.4 Parallel Combination (Convergent Evidence)**

For k independent edges supporting the same claim, each with its own lab probability, type, strength, and population match:

**logit(p\_target) = Σ\_{i=1}\^{k} d(τ\_i) · ω\_i · δ\_i · logit(p\_lab\_i)**

Each evidence line contributes an independent log-odds increment. The total is converted back via sigmoid.

**A.2 Worked Example 1: Daylight → Mood (Empirically Grounded)**

**A.2.1 Setup**

Claim: "Increasing window-to-wall ratio improves patient mood."

Target context: A new hospital in San Diego. Western population. Demographics similar to study samples.

The EN chain has three serial links:

  ----------------------------- -------------- ------- ------- ------------
  **Link**                      **τ**          **ω**   **d**   **p\_lab**
  1\. Window ratio → Daylight   CONSTITUTIVE   0.95    0.95    0.98
  2\. Daylight → Serotonin      MECHANISM      0.85    0.80    0.80
  3\. Serotonin → Mood          MECHANISM      0.80    0.80    0.72
  ----------------------------- -------------- ------- ------- ------------

Population factor: δ = 0.90 (Western city, similar demographics to study samples).

**A.2.2 Serial Combination**

d\_eff = min(0.95, 0.80, 0.80) = 0.80

ω\_eff = 0.95 × 0.85 × 0.80 = 0.646

δ\_eff = 0.90

**A.2.3 Projection Computation**

We need the lab-derived probability for the full chain. The final link gives p\_lab = 0.72 (probability of positive mood given high serotonin). For the full chain, we propagate:

Step 1: logit(0.72) = ln(0.72/0.28) = ln(2.571) = 0.944

Step 2: Attenuated log-odds = d\_eff · ω\_eff · δ\_eff · logit(p\_lab)

= 0.80 × 0.646 × 0.90 × 0.944

= 0.439

Step 3: p\_target = σ(0.439) = 1/(1 + exp(−0.439)) = 1/(1 + 0.645) = 0.608

**Result: P(mood = positive \| windows = large) ≈ 0.61 in the target hospital.**

Note: This is pulled from the lab value of 0.72 toward the ignorance prior of 0.50 by the combined attenuation. But it remains substantially above 0.50, reflecting real evidence.

**A.2.4 Parallel Evidence Boost**

Now suppose we also have a direct EMPIRICAL\_ASSOCIATION edge: hospital outcome studies showing p\_lab = 0.68 for the direct association between daylight and mood improvement (Beauchemin & Hays, 1996), with ω = 0.70, d = 0.80, δ = 0.90.

Additional log-odds contribution:

logit(0.68) = ln(0.68/0.32) = ln(2.125) = 0.754

Contribution = 0.80 × 0.70 × 0.90 × 0.754 = 0.380

Total log-odds = 0.439 (mechanism path) + 0.380 (empirical association) = 0.819

p\_target = σ(0.819) = 1/(1 + exp(−0.819)) = 1/(1 + 0.441) = 0.694

**Result with parallel evidence: P(mood = positive \| windows = large) ≈ 0.69**

The two independent lines of evidence produce substantially higher confidence (0.69) than either alone (0.61 or \~0.59). This is the parallel combination boost in action.

**A.2.5 Empirical Floor**

All links are empirically grounded (CONSTITUTIVE + MECHANISM + EMPIRICAL\_ASSOCIATION). Removing THEORY\_DERIVED links removes nothing. Empirical floor = 0.69. Identical to full projection.

**Theory dependence: EMPIRICALLY GROUNDED.**

**A.3 Worked Example 2: Fractal → Wellbeing (Theory-Scaffolded)**

**A.3.1 Setup**

Claim: "Fractal facades improve occupant wellbeing." Target: same San Diego hospital.

  ---------------------------------- ------------------------ ------- ------- ------------------------
  **Link**                           **τ**                    **ω**   **d**   **p\_lab**
  1\. Fractals → Cortical response   MECHANISM                0.75    0.80    0.78 (EEG established)
  2\. Cortical → Prediction error    THEORY\_DERIVED \[PP\]   0.45    0.25    0.70 (theory predicts)
  3\. Pred. error → Stress           THEORY\_DERIVED \[PP\]   0.40    0.25    0.65 (theory predicts)
  4\. Stress → Wellbeing             EMPIRICAL\_ASSOC         0.70    0.80    0.75 (replicated)
  ---------------------------------- ------------------------ ------- ------- ------------------------

**A.3.2 Serial Combination**

d\_eff = min(0.80, 0.25, 0.25, 0.80) = 0.25

ω\_eff = 0.75 × 0.45 × 0.40 × 0.70 = 0.0945

δ\_eff = 0.90

**A.3.3 Projection Computation**

Using the final link's lab probability (p\_lab = 0.75 for the full chain effect):

Step 1: logit(0.75) = ln(0.75/0.25) = ln(3.0) = 1.099

Step 2: Attenuated = 0.25 × 0.0945 × 0.90 × 1.099 = 0.0234

Step 3: p\_target = σ(0.0234) = 1/(1 + exp(−0.0234)) = 0.506

**Result: P(wellbeing = high \| fractal\_D = 1.3) ≈ 0.506**

This is barely above the ignorance prior of 0.50. The chain of four links with two THEORY\_DERIVED bottlenecks and low ω values produces almost no usable signal. The product of four ω values (0.0945) combined with the minimum discount (0.25) reduces the lab finding to near-zero in log-odds space.

**A.3.4 Empirical Floor**

Remove links 2 and 3 (THEORY\_DERIVED \[Predictive Processing\]).

The chain breaks: there is no path from "cortical response" to "stress reduction" using only empirically grounded links. We have two disconnected empirical fragments:

Fragment A: Fractals → Cortical response (MECHANISM, strong)

Fragment B: Stress → Wellbeing (EMPIRICAL\_ASSOCIATION, strong)

But nothing empirically connects them.

**Empirical floor = 0.50 (ignorance prior).**

**Theory dependence: THEORY-SCAFFOLDED \[Predictive Processing\].**

**A.3.5 What the Numbers Tell the Architect**

The full projection (0.506) and empirical floor (0.500) are nearly identical. The gap is 0.006 --- meaning predictive processing theory contributes almost nothing quantitatively in this chain. This is because the ω values on the theoretical links are low (0.45, 0.40), reflecting that these predictions haven't been tested.

Actionable insight: Do not invest in fractal facades based on this evidence. The expected improvement over random (0.006 probability points) does not justify the cost. Instead, invest in research: a single well-designed study testing the prediction-error interpretation of the EEG response could upgrade links 2 and 3 from THEORY\_DERIVED (d = 0.25) to EMPIRICAL\_ASSOCIATION (d = 0.80) or even MECHANISM (d = 0.80), dramatically changing the projection.

**A.4 Worked Example 3: Population Transfer Effect**

**A.4.1 Same Evidence, Different Populations**

Take the daylight → mood mechanism path (from Example 1). The evidence is from Western populations (Lambert et al., 2002 --- Australian subjects; Beauchemin & Hays, 1996 --- Canadian subjects).

Now project to three different target contexts:

  --------------------------- ------- ----------------------------------------- --------------- --------------------------------------------------
  **Target Context**          **δ**   **Log-odds (0.944 × 0.80 × 0.646 × δ)**   **p\_target**   **Interpretation**
  Hospital in San Diego       0.90    0.439                                     0.608           Good evidence, modest attenuation
  Hospital in Ahmedabad       0.50    0.244                                     0.561           Large cultural distance. Effect attenuated.
  Elderly care, rural India   0.30    0.146                                     0.537           Cultural + demographic distance. Near ignorance.
  --------------------------- ------- ----------------------------------------- --------------- --------------------------------------------------

The mechanism is biological (serotonin pathway is conserved across humans), so the warrant type and strength remain the same. But the population factor δ pulls the projection toward 0.50 for populations that were not studied. The system is honest: we simply do not know how much of the lab finding holds for elderly rural Indian populations.

**A.4.2 Research Prioritization**

A single well-designed study of daylight exposure and mood in Indian urban populations would raise δ from 0.50 to approximately 0.85 for that context. The projected probability would jump from 0.561 to approximately 0.596. For the elderly rural Indian context, a study with that specific population would raise δ from 0.30 to 0.80, changing the projection from 0.537 to 0.590. Each study has maximal impact where δ is lowest --- the system automatically identifies the highest-priority populations to study.

**A.5 Worked Example 4: Dual-BN Comparison**

An architect is designing a hospital in San Diego and wants recommendations for three design features. The EN projects the following:

  -------------------- --------------------- --------------------- -------------------------- ---------------------------------------------------------------------
  **Design Feature**   **Full Projection**   **Empirical Floor**   **Diagnostic**             **Recommendation**
  Larger windows       P = 0.69              P = 0.69              EMPIRICALLY GROUNDED       PROCEED. Evidence is strong and empirically established.
  Fractal facades      P = 0.506             P = 0.50 (breaks)     THEORY-SCAFFOLDED \[PP\]   DO NOT INVEST. Theory-only. Fund research first.
  Biophilic elements   P = 0.62              P = 0.58              THEORY-AUGMENTED           CAUTIOUS PROCEED. Mostly empirical but theory adds some confidence.
  -------------------- --------------------- --------------------- -------------------------- ---------------------------------------------------------------------

The dual-BN comparison makes the decision landscape transparent. The theory-inclusive model recommends all three. The empirical-only model recommends larger windows confidently, biophilic elements cautiously, and is silent on fractal facades. The architect can make informed decisions about where to invest and where to wait for better evidence.

**A.6 Complete Formula Reference**

**1. Log-odds transform:**

**logit(p) = ln(p / (1 - p))**

**σ(x) = 1 / (1 + exp(-x))**

**2. Single-edge projection:**

**logit(p\_target) = d(τ) · ω · δ(pop, pop\_target) · logit(p\_lab)**

**3. Serial chain (through intermediate nodes):**

**d\_eff = min(d\_i) ω\_eff = ∏ ω\_i δ\_eff = min(δ\_i)**

**4. Parallel combination (convergent evidence):**

**logit(p\_target) = Σ\_i d\_i · ω\_i · δ\_i · logit(p\_lab\_i)**

**5. Empirical floor:**

Recompute (3) or (4) using only edges where τ ∈ {CONSTITUTIVE, MECHANISM, EMPIRICAL\_ASSOCIATION, FUNCTIONAL}.

**6. Theory dependence diagnostic:**

ratio = (empirical\_floor - 0.50) / (full\_projection - 0.50)

ratio \> 0.80 → EMPIRICALLY GROUNDED

ratio 0.40--0.80 → THEORY-AUGMENTED

ratio \< 0.40 or chain breaks → THEORY-SCAFFOLDED \[theory name\]
