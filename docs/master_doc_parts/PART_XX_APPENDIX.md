# PART XX: TECHNICAL APPENDIX — FORMULAS AND WORKED EXAMPLES (§141–§146)

*This Part provides the mathematical foundations and numerical case studies for the ATLAS system's projection mechanism. It contains the complete formulae, step-by-step worked calculations, and diagnostic comparisons that enable practitioners to understand how epistemic assessments convert into operational predictions.*

---

## §141: Core Formulas {#141}

### 141.1 The Log-Odds Transform

The log-odds (logit) function maps probabilities from the interval (0, 1) to the real line (−∞, +∞). This is necessary because we need to attenuate probabilities multiplicatively without producing values outside [0, 1].

**logit(p) = ln(p / (1 − p))**

Key values:

- logit(0.50) = 0.000 (ignorance prior = zero in log-odds)
- logit(0.60) = 0.405
- logit(0.70) = 0.847
- logit(0.72) = 0.944
- logit(0.80) = 1.386
- logit(0.90) = 2.197
- logit(0.95) = 2.944

The inverse (sigmoid) maps back:

**σ(x) = 1 / (1 + exp(−x))**

### 141.2 Single-Edge Projection

For a single EN edge with lab-derived probability p_lab, warrant type τ, warrant strength ω, and population factor δ:

**logit(p_target) = d(τ) · ω · δ · logit(p_lab)**

**p_target = σ(logit(p_target))**

This attenuates the lab finding toward the ignorance prior (p = 0.50, logit = 0). The stronger the evidence (ω), the closer the transfer reliability (d), and the better the population match (δ), the more of the lab finding survives.

### 141.3 Serial Combination (Chain)

For a serial chain of edges e₁, e₂, …, eₖ through intermediate nodes:

**d_eff = min(d(τ(e_1)), d(τ(e_2)), …, d(τ(e_k)))**

**ω_eff = ∏ ω_i (product of all warrant strengths)**

**δ_eff = min(δ_i) (weakest population match)**

The effective projection is then:

**logit(p_target) = d_eff · ω_eff · δ_eff · logit(p_lab)**

### 141.4 Parallel Combination (Convergent Evidence)

For k independent edges supporting the same claim, each with its own lab probability, type, strength, and population match:

**logit(p_target) = Σ_{i=1}^{k} d(τ_i) · ω_i · δ_i · logit(p_lab_i)**

Each evidence line contributes an independent log-odds increment. The total is converted back via sigmoid.

### 141.5 Empirical Floor

Recompute the projection using only edges where τ ∈ {CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL}. Remove THEORY_DERIVED, ANALOGICAL, and CAPACITY edges. If the chain survives, compute a lower estimate. If the chain breaks (no empirical path remains), floor = 0.50 (ignorance prior).

### 141.6 Theory Dependence Diagnostic

**ratio = (empirical_floor − 0.50) / (full_projection − 0.50)**

- ratio > 0.80 → EMPIRICALLY GROUNDED
- ratio 0.40–0.80 → THEORY-AUGMENTED
- ratio < 0.40 or chain breaks → THEORY-SCAFFOLDED [theory name]

---

## §142: Worked Example 1 — Daylight → Mood (Empirically Grounded) {#142}

### 142.1 Setup

Claim: "Increasing window-to-wall ratio improves patient mood."

Target context: A new hospital in San Diego. Western population. Demographics similar to study samples.

The EN chain has three serial links:

| **Link** | **τ** | **ω** | **d** | **p_lab** |
|---|---|---|---|---|
| 1. Window ratio → Daylight | CONSTITUTIVE | 0.95 | 0.95 | 0.98 |
| 2. Daylight → Serotonin | MECHANISM | 0.85 | 0.80 | 0.80 |
| 3. Serotonin → Mood | MECHANISM | 0.80 | 0.80 | 0.72 |

Population factor: δ = 0.90 (Western city, similar demographics to study samples).

### 142.2 Serial Combination

d_eff = min(0.95, 0.80, 0.80) = 0.80

ω_eff = 0.95 × 0.85 × 0.80 = 0.646

δ_eff = 0.90

### 142.3 Projection Computation

We need the lab-derived probability for the full chain. The final link gives p_lab = 0.72 (probability of positive mood given high serotonin). For the full chain, we propagate:

Step 1: logit(0.72) = ln(0.72/0.28) = ln(2.571) = 0.944

Step 2: Attenuated log-odds = d_eff · ω_eff · δ_eff · logit(p_lab)

= 0.80 × 0.646 × 0.90 × 0.944

= 0.439

Step 3: p_target = σ(0.439) = 1/(1 + exp(−0.439)) = 1/(1 + 0.645) = 0.608

**Result: P(mood = positive | windows = large) ≈ 0.61 in the target hospital.**

Note: This is pulled from the lab value of 0.72 toward the ignorance prior of 0.50 by the combined attenuation. But it remains substantially above 0.50, reflecting real evidence.

### 142.4 Parallel Evidence Boost

Now suppose we also have a direct EMPIRICAL_ASSOCIATION edge: hospital outcome studies showing p_lab = 0.68 for the direct association between daylight and mood improvement (Beauchemin & Hays, 1996), with ω = 0.70, d = 0.80, δ = 0.90.

Additional log-odds contribution:

logit(0.68) = ln(0.68/0.32) = ln(2.125) = 0.754

Contribution = 0.80 × 0.70 × 0.90 × 0.754 = 0.380

Total log-odds = 0.439 (mechanism path) + 0.380 (empirical association) = 0.819

p_target = σ(0.819) = 1/(1 + exp(−0.819)) = 1/(1 + 0.441) = 0.694

**Result with parallel evidence: P(mood = positive | windows = large) ≈ 0.69**

The two independent lines of evidence produce substantially higher confidence (0.69) than either alone (0.61 or ~0.59). This is the parallel combination boost in action.

### 142.5 Empirical Floor

All links are empirically grounded (CONSTITUTIVE + MECHANISM + EMPIRICAL_ASSOCIATION). Removing THEORY_DERIVED links removes nothing. Empirical floor = 0.69. Identical to full projection.

**Theory dependence: EMPIRICALLY GROUNDED.**

---

## §143: Worked Example 2 — Fractal → Wellbeing (Theory-Scaffolded) {#143}

### 143.1 Setup

Claim: "Fractal facades improve occupant wellbeing." Target: same San Diego hospital.

| **Link** | **τ** | **ω** | **d** | **p_lab** |
|---|---|---|---|---|
| 1. Fractals → Cortical response | MECHANISM | 0.75 | 0.80 | 0.78 (EEG established) |
| 2. Cortical → Prediction error | THEORY_DERIVED [PP] | 0.45 | 0.25 | 0.70 (theory predicts) |
| 3. Pred. error → Stress | THEORY_DERIVED [PP] | 0.40 | 0.25 | 0.65 (theory predicts) |
| 4. Stress → Wellbeing | EMPIRICAL_ASSOC | 0.70 | 0.80 | 0.75 (replicated) |

### 143.2 Serial Combination

d_eff = min(0.80, 0.25, 0.25, 0.80) = 0.25

ω_eff = 0.75 × 0.45 × 0.40 × 0.70 = 0.0945

δ_eff = 0.90

### 143.3 Projection Computation

Using the final link's lab probability (p_lab = 0.75 for the full chain effect):

Step 1: logit(0.75) = ln(0.75/0.25) = ln(3.0) = 1.099

Step 2: Attenuated = 0.25 × 0.0945 × 0.90 × 1.099 = 0.0234

Step 3: p_target = σ(0.0234) = 1/(1 + exp(−0.0234)) = 0.506

**Result: P(wellbeing = high | fractal_D = 1.3) ≈ 0.506**

This is barely above the ignorance prior of 0.50. The chain of four links with two THEORY_DERIVED bottlenecks and low ω values produces almost no usable signal. The product of four ω values (0.0945) combined with the minimum discount (0.25) reduces the lab finding to near-zero in log-odds space.

### 143.4 Empirical Floor

Remove links 2 and 3 (THEORY_DERIVED [Predictive Processing]).

The chain breaks: there is no path from "cortical response" to "stress reduction" using only empirically grounded links. We have two disconnected empirical fragments:

- Fragment A: Fractals → Cortical response (MECHANISM, strong)
- Fragment B: Stress → Wellbeing (EMPIRICAL_ASSOCIATION, strong)

But nothing empirically connects them.

**Empirical floor = 0.50 (ignorance prior).**

**Theory dependence: THEORY-SCAFFOLDED [Predictive Processing].**

### 143.5 What the Numbers Tell the Architect

The full projection (0.506) and empirical floor (0.500) are nearly identical. The gap is 0.006—meaning predictive processing theory contributes almost nothing quantitatively in this chain. This is because the ω values on the theoretical links are low (0.45, 0.40), reflecting that these predictions haven't been tested.

**Actionable insight:** Do not invest in fractal facades based on this evidence. The expected improvement over random (0.006 probability points) does not justify the cost. Instead, invest in research: a single well-designed study testing the prediction-error interpretation of the EEG response could upgrade links 2 and 3 from THEORY_DERIVED (d = 0.25) to EMPIRICAL_ASSOCIATION (d = 0.80) or even MECHANISM (d = 0.80), dramatically changing the projection.

---

## §144: Worked Example 3 — Population Transfer Effects {#144}

### 144.1 Same Evidence, Different Populations

Take the daylight → mood mechanism path (from Example 1). The evidence is from Western populations (Lambert et al., 2002—Australian subjects; Beauchemin & Hays, 1996—Canadian subjects).

Now project to three different target contexts:

| **Target Context** | **δ** | **Log-odds (0.944 × 0.80 × 0.646 × δ)** | **p_target** | **Interpretation** |
|---|---|---|---|---|
| Hospital in San Diego | 0.90 | 0.439 | 0.608 | Good evidence, modest attenuation |
| Hospital in Ahmedabad | 0.50 | 0.244 | 0.561 | Large cultural distance. Effect attenuated. |
| Elderly care, rural India | 0.30 | 0.146 | 0.537 | Cultural + demographic distance. Near ignorance. |

The mechanism is biological (serotonin pathway is conserved across humans), so the warrant type and strength remain the same. But the population factor δ pulls the projection toward 0.50 for populations that were not studied. The system is honest: we simply do not know how much of the lab finding holds for elderly rural Indian populations.

### 144.2 Research Prioritization

A single well-designed study of daylight exposure and mood in Indian urban populations would raise δ from 0.50 to approximately 0.85 for that context. The projected probability would jump from 0.561 to approximately 0.596. For the elderly rural Indian context, a study with that specific population would raise δ from 0.30 to 0.80, changing the projection from 0.537 to 0.590. Each study has maximal impact where δ is lowest—the system automatically identifies the highest-priority populations to study.

---

## §145: Worked Example 4 — Dual-BN Comparison for Design Decisions {#145}

An architect is designing a hospital in San Diego and wants recommendations for three design features. The EN projects the following:

| **Design Feature** | **Full Projection** | **Empirical Floor** | **Diagnostic** | **Recommendation** |
|---|---|---|---|---|
| Larger windows | P = 0.69 | P = 0.69 | EMPIRICALLY GROUNDED | PROCEED. Evidence is strong and empirically established. |
| Fractal facades | P = 0.506 | P = 0.50 (breaks) | THEORY-SCAFFOLDED [PP] | DO NOT INVEST. Theory-only. Fund research first. |
| Biophilic elements | P = 0.62 | P = 0.58 | THEORY-AUGMENTED | CAUTIOUS PROCEED. Mostly empirical but theory adds some confidence. |

The dual-BN comparison makes the decision landscape transparent. The theory-inclusive model recommends all three. The empirical-only model recommends larger windows confidently, biophilic elements cautiously, and is silent on fractal facades. The architect can make informed decisions about where to invest and where to wait for better evidence.

---

## §146: Complete Formula Reference {#146}

### 146.1 Log-odds transform

**logit(p) = ln(p / (1 - p))**

**σ(x) = 1 / (1 + exp(-x))**

### 146.2 Single-edge projection

**logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)**

### 146.3 Serial chain (through intermediate nodes)

**d_eff = min(d_i) ω_eff = ∏ ω_i δ_eff = min(δ_i)**

### 146.4 Parallel combination (convergent evidence)

**logit(p_target) = Σ_i d_i · ω_i · δ_i · logit(p_lab_i)**

### 146.5 Empirical floor

Recompute (146.3) or (146.4) using only edges where τ ∈ {CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL}.

### 146.6 Theory dependence diagnostic

**ratio = (empirical_floor - 0.50) / (full_projection - 0.50)**

- ratio > 0.80 → EMPIRICALLY GROUNDED
- ratio 0.40–0.80 → THEORY-AUGMENTED
- ratio < 0.40 or chain breaks → THEORY-SCAFFOLDED [theory name]

### 146.7 References for §141–§146

Beauchemin, K. M., & Hays, P. (1996). Sunny hospital rooms expedite recovery from severe and refractory depression. *Journal of Affective Disorders*, 40(1), 49-51.

Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D. (2002). Effect of sunlight and season on serotonin turnover in the brain. *The Lancet*, 360(9348), 1840-1842.

Hägerhäll, C. M. (2004). Referral frequency and design dimensions in natural and built environments. *Journal of Environmental Psychology*, 24(1), 63-81.

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, 15(3), 169-182.

---

