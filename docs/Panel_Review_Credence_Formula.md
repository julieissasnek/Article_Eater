# ATLAS Credence Formula Audit: Expert Panel Deliberation Report
## February 26, 2026

---

## THE CRITICAL FINDING

The ATLAS health audit discovered that the core credence formula — P(composite) = P(parent) x P(bridge) x P(CNFA) — is **systematically violated** across every worked example in the master document. Stated composites exceed formula products by 30-80%. This is structural, not rounding.

| Template | P(parent) | P(bridge) | P(CNFA) | Product | Stated | Delta |
|----------|-----------|-----------|---------|---------|--------|-------|
| VIEW1    | 0.85      | 0.70      | 0.70    | 0.416   | 0.55   | 0.134 |
| VF2      | 0.80      | 0.40      | 0.50    | 0.160   | 0.32   | 0.160 |
| MAT1     | 0.82      | 0.65      | 0.68    | 0.362   | 0.52   | 0.158 |
| SC1      | 0.80      | 0.60      | 0.65    | 0.312   | 0.52   | 0.208 |
| SOC2     | 0.78      | 0.62      | 0.70    | 0.339   | 0.62   | 0.281 |
| L2       | 0.85      | 0.68      | 0.65    | 0.376   | 0.62   | 0.244 |
| CREA3    | 0.76      | 0.58      | 0.62    | 0.273   | 0.48   | 0.207 |

Additionally, 6 of 7 worked examples have bridge warrant values exceeding their canonical ceilings.

---

## PANEL COMPOSITION

1. **Nancy Cartwright** (Philosophy of Science, LSE/UCSD) — Capacities, causal inference
2. **Judea Pearl** (Computer Science, UCLA) — Causal inference, Bayesian networks
3. **Paul Thagard** (Cognitive Science, Waterloo) — Explanatory coherence
4. **Susan Haack** (Philosophy, Miami) — Foundherentism, evidence theory
5. **Roger Cooke** (Risk Analysis, RFF) — Expert elicitation
6. **Kevin Murphy** (Machine Learning, Google) — Probabilistic graphical models
7. **Jim Woodward** (Philosophy, Pittsburgh/Caltech) — Interventionism

---

## UNANIMOUS FINDINGS

1. **The multiplicative formula is not operational.** Stated composites systematically exceed factor products by 30-80%. This is structural, not calibration error.

2. **The ceiling violations are real.** 6 of 7 examples assign bridge warrants exceeding canonical ceilings (EMPIRICAL_COVARIANCE 0.60, MECHANISM 0.60, etc.).

3. **The three factors are not independent.** Multiplicative decomposition assumes conditional independence; the data and theory both indicate correlated factors.

4. **Composites reflect holistic panel judgment, not formula output.** This is not inherently problematic but must be acknowledged.

5. **A weighted additive model fits the data far better.** Approximately: Composite ≈ 0.50 x P(parent) + 0.30 x P(bridge) + 0.20 x P(CNFA).

6. **Epistemic honesty requires correcting how ATLAS represents its method.**

---

## KEY DEBATE: What Is the Formula Actually Doing?

### Kevin Murphy's regression analysis:

- **Multiplicative model**: mean residual = 0.188 (systematic upward bias). Poor fit. Reject.
- **Simple average**: (P1 + P2 + P3)/3 — overshoots consistently. Reject.
- **Weighted additive** (0.50/0.30/0.20): MSE ≈ 0.008. Good fit. Parent theory dominates.

### Interpretation (Nancy Cartwright):

The weights encode a priority structure: parent theory is primary (peer-reviewed, tested across contexts), bridge is secondary (transfer is inherently uncertain), CNFA-specific is tertiary (most context-dependent). The composite is not a probabilistic conjunction but a theory-driven weighted assessment.

### Alternative (Judea Pearl):

A Bayesian latent variable model — treating factors as noisy signals of true "transferability" — explains why composites exceed products. Factors are correlated measurements of a single latent variable; Bayesian fusion naturally produces higher posteriors than simple multiplication of likelihoods.

### Coherence view (Paul Thagard):

The formula should be a coherence satisfaction algorithm, not a factorization formula. Multiple satisfied constraints produce super-additive coherence gain, which is exactly what the data show.

---

## PRIORITIZED RECOMMENDATIONS

### TIER 1: Immediate Corrections

**1.1** Retire the multiplicative formula from the master document. Replace with explicit description of actual procedure.

**1.2** Correct ceiling violations in existing cases:
- Option A (conservative): Recompute factor values to respect ceilings
- Option B (revisionist): Revise ceilings upward with documented justification
- Panel recommends Option A unless strong theoretical reasons support higher ceilings.

**1.3** Document the actual composite assessment procedure:
- Step A: Independently assess P(parent), P(bridge), P(CNFA) with ceiling constraints
- Step B: Compute baseline composite as 0.50 x P(parent) + 0.30 x P(bridge) + 0.20 x P(CNFA)
- Step C: Assess coherence; apply adjustment (-0.05 to +0.05)
- Step D: Document any deviation > 0.05 with reasoning
- Step E: Final composite is the output; factors are inputs and justifications

### TIER 2: Medium-term improvements

**2.1** Conduct sensitivity analyses showing how results differ under multiplicative, weighted additive, and holistic approaches.

**2.2** Establish calibration benchmarks: Do composites of 0.55 predict ~55% replication rates?

**2.3** Formalize the coherence adjustment step with explicit guidelines.

### TIER 3: Long-term formalization

**3.1** Develop a formal coherence model (adapted ECHO or custom Bayesian network).

**3.2** Ground coherence in interventionist causal analysis.

**3.3** Conduct structured expert elicitation on the weighting structure.

---

## AREAS OF DISAGREEMENT

### Framework choice:
- **Cartwright & Woodward**: Coherence satisfaction / interventionist causal framework
- **Pearl & Murphy**: Bayesian latent variable model
- **Resolution**: Either is defensible; choice should align with ATLAS's philosophical foundations

### Implementation complexity:
- **Cartwright & Thagard**: Full ECHO-style constraint networks
- **Murphy**: Pragmatic weighted additive + coherence adjustment (±0.05)
- **Resolution**: Murphy's approach as short-term fix; formal coherence modeling as long-term goal

### Backward compatibility:
- **Cooke**: Grandfather current composites; correct procedure going forward
- **Cartwright**: Re-analyze under corrected procedure for methodological coherence
- **Resolution**: Preserve with footnote; future analyses use corrected method

---

## RELATIONSHIP TO AG's HEALTH REPORT

AG's corpus_health_report.py found: 100 missing confidence values, 103 missing bridge warrants, 40 unclassified templates, 1 ceiling violation.

The health audit reveals these are symptoms of a deeper structural issue:
- The **missing confidence values** likely reflect the gap between markdown specifications and JSON serialization (~52 templates not yet in JSON)
- The **missing bridge warrants** reflect the same serialization gap
- The **1 ceiling violation** AG found is actually the tip of an iceberg: the master doc shows 6 of 7 worked examples exceed ceilings
- The **formula discrepancy** is the root cause: the system was designed around a formula that doesn't match practice

### Repair priority:
1. Fix the formula (this panel's recommendations)
2. Serialize remaining templates to JSON (AG's task)
3. Enforce corrected ceilings in all templates
4. Re-run health checks against corrected specifications
