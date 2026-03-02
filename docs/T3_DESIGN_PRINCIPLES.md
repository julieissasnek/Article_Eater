# T3 Empirical Belief Layer — Design Principles & Key Decisions

## Principles

### P-1: Beliefs Form Bottom-Up from Evidence
T3 beliefs **emerge** from convergence of ≥3 independent findings at the same generalization level. No belief is created top-down.

### P-2: Dual-Hierarchy Generalization
IV (stimulus taxonomy) and DV (outcome taxonomy) generalize **independently**. A T3 belief is a point in the IV×DV product space.

### P-3: Mechanism Identity Required for Merging (Cartwright)
Two stimuli can only be merged if they share a **plausible mechanism** (linked to the same T2 template). Statistical similarity alone is insufficient.

### P-4: Access Level is a Don't-Merge Criterion (Barrett)
Cortisol (autonomic) and self-reported stress (conscious) are **different phenomena**. Beliefs at different access levels never merge.

### P-5: Delivery Mode is a Boundary Condition, Not a Generalization Axis
VR and real-world findings are tracked as **boundary conditions**, not separate beliefs. The question "does VR replicate real?" is empirical.

### P-6: Coverage Gaps are First-Class
Identifying what **hasn't** been tested is as important as aggregating what has. Gaps feed directly into VOI search.

### P-7: Integration by Contract, Not Coupling
T3 exposes **7 typed protocol contracts**. Existing modules interact through these contracts without importing T3 internals.

### P-8: Nascent Beliefs are Search Seeds (NEW)
Every single-article finding is preserved as a **NASCENT** belief — not discarded, not hidden. Nascent beliefs are *precisely* the claims we want to search for more articles about. They drive the article acquisition pipeline by generating high-priority search queries. A nascent belief is the EN saying "I heard one claim about X → Y; I should find out if anyone else has studied this."

---

## Key Decisions

| # | Decision | Rationale | Alternative Considered |
|---|----------|-----------|----------------------|
| D-1 | 11 root IV domains | User feedback: include person-state, cultural, olfactory, temporal | 5 roots (original plan — too narrow) |
| D-2 | ≥3 source convergence threshold | Matches scientific convention (n≥3 for pattern) | ≥2 (too generous) or ≥5 (too strict) |
| D-3 | Bayesian Beta posterior for confidence | Natural interpretation, handles sparse data | Frequentist meta-analysis (requires more data) |
| D-4 | Parametric merge → parent node | 9', 9.5', 10' → "high ceiling" when direction consistent | Keep all separate (loses generalization) |
| D-5 | Equivalence classes for DV merge | Fluency+originality = "divergent thinking tasks" | Merge by common ancestor (too aggressive) |
| D-6 | Event bus for cross-module communication | Decoupled, testable, extensible | Direct function calls (tight coupling) |
| D-7 | T3Adapter as single integration point | Parnas information hiding | Multiple adapters per contract (complex) |
| D-8 | NASCENT status for n=1 findings | Drive search acquisition; n=1 is a question, not silence | Discard n<3 (loses search signal) |

---

## Expert Panel (Expanded, 18 Panelists)

### Founding Panel (Architecture & Philosophy)
| Panelist | Domain | Key Contribution |
|----------|--------|-----------------|
| Nancy Cartwright | Philosophy of Causation | Mechanism identity for merging |
| Rachel Kaplan | Environmental Psychology | Preference matrix tagging |
| Joshua Tenenbaum | Computational Cognitive Science | Bayesian generalization from examples |
| Herbert Simon | Systems Design | Contract-based integration architecture |
| Martin Fowler | Software Architecture | Adapter pattern, event bus design |

### Subject-Matter Experts (Expanded)
| Panelist | Domain | Key Contribution |
|----------|--------|-----------------|
| Colin Ellard | Cognitive Neuroscience / CNFA | Creativity measure distinctions, VR validity |
| Lisa Feldman Barrett | Affective Neuroscience | Access level = don't-merge (cortisol ≠ self-report) |
| Jan Gehl | Urban Design / Social Space | Sufficient subtype coverage requirement |
| Upali Nanda | Healthcare Design / CNFA | Population-conditioned beliefs, clinical DVs |
| Ruth Dalton | Space Syntax / Architecture | Temporal scope as boundary condition |
| Antonio Damasio | Neuroscience (Somatic Markers) | Embodied cognition IVs, interoception as modality |
| Karl Friston | Computational Neuroscience | Active inference framing, predictive coding for IV taxonomy |
| Ed Diener | Well-Being Science | Subjective well-being scales, life satisfaction as DV |
| Carol Ryff | Eudaimonic Well-Being | Distinguishing hedonic vs eudaimonic DVs |
| Jim Russell | Core Affect Theory | Arousal × valence circumplex for affect DVs |
| Tor Wager | Affective Neuroscience / Physiology | Neuroimaging ≠ behavior (access level validation) |
| Peter Sterling | Allostasis / Physiology | Allostatic load as integrative health DV |
| Yoshua Bengio | Machine Learning / Latent Variables | Disentangled representations for IV/DV spaces |

### Panel Size Rationale
- **4 neuroscientists** (Damasio, Friston, Barrett, Wager): needed for access level rules, mechanism validation, embodied cognition dimensions
- **2 computationalists** (Tenenbaum, Bengio): needed for generalization theory, latent variable structure
- **3 affect/well-being** (Diener, Ryff, Russell): needed for DV measurement equivalence, hedonic/eudaimonic distinction
- **2 physiologists** (Wager, Sterling): needed for physiological DV boundaries, allostatic integration

---

## Reflexes

| ID | Trigger | Action |
|----|---------|--------|
| RF-1 | T3 belief contradicts T2 template | Flag for review |
| RF-2 | Coverage gap score > 0.8 | Auto-generate search suggestion |
| RF-3 | Belief with <3 sources promoted | Demote to TENTATIVE |
| RF-4 | Merge would combine different mechanisms | BLOCK and log |
| RF-5 | Delivery mode differs, all else same | Note as boundary condition |
| RF-6 | Nascent belief created | Generate search seed query |

---

## Module Map

```
stimulus_taxonomy.py ──┐
                       ├── generalization_tree.py ──> t3_belief_engine.py ──> t3_integration.py
dv_generalization.py ──┘                                                          │
                                                                                  ├── T3QueryContract
                                                                                  ├── T3UpdateContract
                                                                                  ├── T3GapContract (+ nascent seeds)
                                                                                  ├── T3ArgumentContract
                                                                                  ├── T3OverseerContract
                                                                                  ├── T3BNContract
                                                                                  └── T3TemplateContract
```

## Belief Lifecycle

```
Article extraction → EN Finding → T3 Finding
    ↓
n=1 → NASCENT (search seed, priority=0.85)
n=2 → TENTATIVE (waiting for corroboration)
n≥3 → ESTABLISHED (if direction consistent)
     → CONTESTED (if direction mixed)
     → BOUNDARY (if moderator identified)
```
