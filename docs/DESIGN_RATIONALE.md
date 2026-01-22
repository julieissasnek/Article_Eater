# Design Rationale: Theory of the System

**Date**: January 22, 2026
**Version**: V21.0.0 (Post-Quinean)
**Purpose**: Document the epistemological commitments and design decisions (per Naur, ruthless review 2026-01-22)

---

## 1. Quinean Commitment: Why Coherentist, Not Foundationalist

### The Core Decision
Article Eater uses **coherentist epistemology** (Quine's Web of Belief) rather than foundationalist epistemology.

### Why This Matters
In foundationalist systems (like classical Bayesian networks), some beliefs are "basic" - they're accepted without justification and serve as foundations for derived beliefs. This creates problems:

1. **Anchoring bias**: Foundational beliefs resist revision even when they should change
2. **One-way inference**: Information flows from foundations upward, not from derived beliefs back
3. **False certainty**: Treating some evidence as "given" masks its actual uncertainty

### The Quinean Alternative
In the Web of Belief:
- **Nothing is foundational** - all beliefs are revisable
- **Justification comes from coherence** - a belief is justified by how well it fits with other beliefs
- **Any node can be revised** - when evidence conflicts, theory, auxiliary assumptions, or measurement can change
- **Stubs are held, not forced** - findings that don't fit current ontology are preserved without forcing interpretation

### Implications for Implementation
- The BN (Bayesian Network) is **derivative** of the web, not primary
- Credence represents **coherence-weighted confidence**, not raw probability
- Contested evidence is handled through **directional opposition**, not credence thresholds
- Revisions propagate through **coherence constraints**, not Bayesian conditioning

### References
- Quine, W.V.O. & Ullian, J.S. (1978). *The Web of Belief* (2nd ed.). Random House.
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press.

---

## 2. Three-Tier Classification: Why Not Four Tiers

### The Decision
Causal claims are classified into three tiers:
1. **CAUSAL**: Clear causal claim with mechanism or experimental evidence
2. **SUGGESTIVE**: Hints at causation but not definitive
3. **ASSOCIATIONAL**: Purely correlational language

### Why Three, Not Four or More
Per Simon (bounded rationality review), adding a fourth tier would:
1. **Exceed cognitive capacity** - users can hold ~3-4 categories in working memory
2. **Create false precision** - distinguishing "weakly causal" from "suggestive" is unreliable
3. **Increase maintenance burden** - more categories means more classification rules

### The Alternative Considered
A four-tier system with "CAUSAL-INSUFFICIENT" (causal language without mechanism/confounder) was proposed by Pearl. However:
- This is captured by **warnings** in the three-tier system
- Users get the nuance without learning another category
- The warning system is more flexible than a fixed tier

### Implementation Note
Per Pearl's design-first approach:
- Experimental design takes precedence over language
- Quasi-experimental designs can yield CAUSAL tier with causal language
- Causal language alone (observational) requires mechanism OR confounder control for CAUSAL

---

## 3. Directional Opposition: Why Not Credence Threshold

### The Decision
Contested evidence is detected via **directional opposition** (X increases Y vs X decreases Y), not credence threshold (credence < 0.5).

### Why This Matters
Per Pearl (ruthless review 2026-01-22):
> "Credence represents belief strength, not direction. Two studies can both be highly credible (high credence) while reaching opposite conclusions."

### The Failed Alternative
Earlier implementations used credence thresholds:
```python
# WRONG: Low credence means contested
if belief.credence.value < 0.5:
    belief.contested = True
```

This conflates **uncertainty** with **disagreement**:
- A belief with credence 0.3 might simply have weak evidence (uncertain)
- A belief with credence 0.8 might be contradicted by another belief with credence 0.8 (contested)

### The Correct Approach
```python
# RIGHT: Directional opposition means contested
def _has_directional_opposition(positive: List[Belief], negative: List[Belief]) -> bool:
    """Contested = high-credence evidence on both sides."""
    return (
        any(b.credence.value > 0.6 for b in positive) and
        any(b.credence.value > 0.6 for b in negative)
    )
```

---

## 4. Pattern Selection: Why These Specific Patterns

### Causal Language Patterns
The causal patterns were selected based on:
1. **Corpus analysis** of neuroarchitecture literature
2. **Linguistic markers** from causation studies (Pearl, 2009; Beebee et al., 2009)
3. **Domain expertise** from Kaplan (environmental psychology)

### Neuroarchitecture-Specific Patterns (F1.1)
Per Kaplan (ruthless review 2026-01-22), domain patterns include:
- Building certification: `green building`, `WELL`, `LEED`, `biophilic design`
- Lighting interventions: `daylighting`, `glare control`, `circadian lighting`
- Environmental quality: `thermal comfort`, `acoustic comfort`, `IAQ`

### Theoretical Framework Patterns (F1.2)
Detection of established theories:
- **ART** (Attention Restoration Theory): `being away`, `fascination`, `extent`, `compatibility`
- **Prospect-Refuge**: `prospect`, `refuge`, `mystery`, `complexity`
- **SRT** (Stress Recovery Theory): `stress recovery theory`, `Ulrich`, `affective response`
- **Biophilia**: `biophilia`, `biophilic`, `nature connection`

### Why Pattern Matching (Not ML)
1. **Interpretability**: Patterns are human-readable and auditable
2. **Maintainability**: Domain experts can add patterns without ML expertise
3. **Appropriate complexity**: For pattern detection, regex is sufficient; ML would be over-engineering

---

## 5. Bridge Warrant Theory: Evidence Portability

### The Concept
Bridge warrants (Cartwright & Hardie, 2012) are explicit assumptions that license knowledge transfer across domains.

### Bridge Types (Extended per F2.1)
| Type | P(bridge) | Description |
|------|-----------|-------------|
| CONSTITUTIVE | 0.75 | Target literally contains source |
| MECHANISM | 0.60 | Same causal pathway in both domains |
| CAPACITY | 0.55 | Entity has stable capacity (NEW) |
| FUNCTIONAL | 0.50 | Same outcome, different mechanisms |
| ANALOGICAL | 0.35 | Structural similarity |

### Capacity Bridges (F2.1)
Per Cartwright (ruthless review 2026-01-22):
> "Some bridges work because an entity has a stable capacity, not because of mechanism. 'Plants have the capacity to reduce stress' doesn't specify mechanism but references stable capacity."

Detection patterns: `has the capacity`, `capable of`, `tends to`, `propensity to`, `disposition`

### Bridge-Weighted Credence
```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

This formula assumes independence (a simplification), but has the right qualitative properties.

---

## 6. Satisficing Principles: Bounded Rationality Throughout

### The Philosophy
Per Simon (ruthless review 2026-01-22), the system follows satisficing principles:

1. **Three tiers, not optimal classification** - good enough beats perfect
2. **Pattern matching, not probabilistic parsing** - fast and interpretable
3. **Stopping rules based on saturation** - not exhaustive search
4. **Three follow-ups per response** - matches cognitive capacity

### Implementation Examples
- **Confidence levels**: Four levels (High/Medium/Low/Unknown), not continuous probabilities
- **Evidence limit**: Top 10 items per response, not complete corpus
- **Follow-up structure**: Exactly 3 follow-ups (deeper, scope, uncertainty)

### Why Satisficing Works Here
Neuroarchitecture research is:
1. **Exploratory** - users don't know exactly what they're looking for
2. **Uncertain** - evidence is often indirect or contested
3. **Practical** - decisions must be made with incomplete information

Optimal inference would be computationally intractable and practically unnecessary.

---

## 7. Measurement Method Differences (F2.2)

### Why This Matters
Per Cartwright (ruthless review 2026-01-22), measurement method is critical for explaining disagreement:

| Method Type | Examples | Issue |
|-------------|----------|-------|
| Self-report vs Physiological | Survey vs cortisol | What people say vs what bodies do |
| Behavioral vs Self-report | Task performance vs questionnaire | What people do vs what they say |
| Objective vs Subjective | Lux levels vs perceived brightness | Physical vs experiential |
| Short-term vs Long-term | Acute vs chronic | Temporal scope |

### Implementation
Disagreement detection checks for measurement method differences and reports them as reasons for contested evidence.

---

## 8. Confounder Gap Detection (E1.D4)

### Severity Levels
Per Cartwright (E1.D4):
- **CRITICAL**: Abstract-only causal claim, no confounder mention
- **WARNING**: Full-text causal claim, no confounder mention
- **INFO**: Associational claim or has confounder mention

### Expanded Keywords (F1.4)
Per Pearl and Kaplan:
- Statistical control: `controlled for`, `adjusted for`, `covariate`
- Causal identification: `propensity score`, `instrumental variable`, `RDD`
- Domain-specific: `occupant density`, `habituation`, `prior exposure`
- Implicit control: `adjusted model`, `full model`, `multivariate`

---

## References

- Beebee, H., Hitchcock, C., & Menzies, P. (Eds.). (2009). *The Oxford Handbook of Causation*. Oxford University Press.
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press.
- Cartwright, N. (1999). *The Dappled World*. Cambridge University Press.
- Cartwright, N., & Hardie, J. (2012). *Evidence-Based Policy*. Oxford University Press.
- Kaplan, R. & Kaplan, S. (1989). *The Experience of Nature*. Cambridge University Press.
- Pearl, J. (2009). *Causality* (2nd ed.). Cambridge University Press.
- Quine, W.V.O. & Ullian, J.S. (1978). *The Web of Belief* (2nd ed.). Random House.
- Simon, H. (1996). *The Sciences of the Artificial* (3rd ed.). MIT Press.
- Ulrich, R.S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420-421.

---

## Appendix: Decision Log

| Date | Decision | Rationale | Expert |
|------|----------|-----------|--------|
| 2026-01-18 | Three tiers, not four | Cognitive load (Simon) | Simon |
| 2026-01-18 | Directional opposition | Credence ≠ direction (Pearl) | Pearl |
| 2026-01-18 | Bridge warrant types | Evidence portability (Cartwright) | Cartwright |
| 2026-01-22 | Add CAPACITY bridge type | Stable capacities ≠ mechanisms | Cartwright |
| 2026-01-22 | Expand neuroarch patterns | Domain coverage incomplete | Kaplan |
| 2026-01-22 | Reduce CONSTITUTIVE to 0.75 | Definitional bridges can be contested | Cartwright |
| 2026-01-22 | Add theoretical frameworks | ART, prospect-refuge, SRT detection | Kaplan |
