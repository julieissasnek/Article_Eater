# ATLAS EN/BN Architecture — Session Exchange Summary
## Session Date: February 27, 2026 (post-compaction continuation)
## Participants: David Kirsh + Claude (Opus)

---

## Context
This session continues from a prior session (transcript: `/mnt/transcripts/2026-02-27-03-16-51-ewg-warrant-analysis-doc.txt`) in which we produced:
- `02-26_01_EWG_Warrant_Analysis_V1.0.docx` — 30-page formal analysis of seven warrant types
- `02-26_02_Addressing_Pearl_Typed_Edges_V2.0.docx` — 40-page response to Pearl's likely objections
- `02-27_03_ATLAS_Terminology_Cheat_Sheet_V1.0.docx` — Landscape cheat sheet (first version)

The current session made several major conceptual advances that are NOT yet captured in any document.

---

## Major Decisions & Conceptual Advances

### 1. RENAMING: EWG → Epistemic Network (EN)
**Decision**: Rename "Epistemic Warrant Graph" (EWG) to **Epistemic Network** (EN).
**Rationale**: EN vs BN is immediately intuitive — one is about what we *know* (epistemic), the other is about what we *predict* (Bayesian). "Warrant" now lives inside the EN as the name for edge annotations rather than the whole graph.
**Status**: DECIDED. All future documents should use EN.

### 2. RENAMING: Confidence weight → Warrant Strength (ω)
**Decision**: The number ω on each EN edge is called **warrant strength** in the formal system and **degree of belief** in prose exposition.
**Rationale**: "Confidence weight" risked confusion with statistical confidence intervals. "Warrant strength" pairs naturally with "warrant type" (τ), making the two annotations a matched pair: the *type* tells you what kind of evidence, the *strength* tells you how good that evidence is.
**Status**: DECIDED.

### 3. NAMING: Transfer Reliability for discount factor (d)
**Decision**: The discount factor d is called **transfer reliability** in prose.
**Rationale**: It answers: "how much of this type of evidence survives transfer to a new context?" Transfer reliability is self-documenting.
**Status**: DECIDED.

### 4. DEFINITION: CPT = Conditional Probability Table
**Decision**: Always spell out "Conditional Probability Table" on first use. CPT is P(X | Pa(X)) — for each configuration of parent values, a probability distribution over X's values. Columns sum to 1.
**Key distinction**: CPT is the *object-level* content (what happens in the world). Warrant strength ω is the *meta-level* content (how well-supported is the evidence). Discount factor d is the *transfer-level* content (how much survives context change).
**Status**: DECIDED.

### 5. RENAMING: EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION
**Decision**: Rename to **EMPIRICAL_ASSOCIATION**.
**Rationale**: "Covariance" is technically precise but less intuitive. "Correlation" has baggage ("correlation is not causation"). "Association" is the epidemiological term of art — what you report when you have evidence of a relationship but aren't claiming causation. Rejected alternatives: "Confound Risk" (names the vulnerability, not the evidence), "Raw Correlation" (implies unprocessed data).
**Status**: DECIDED.

### 6. RENAMING: THEORETICAL_DEFAULT → THEORY_DERIVED [theory name]
**Decision**: Rename to **THEORY_DERIVED** and require each edge of this type carry an explicit **theory tag** naming the framework.
**Example**: τ = THEORY_DERIVED [Predictive Processing] instead of τ = THEORETICAL_DEFAULT.
**Rationale**: Three advantages — (a) auditability (traces claims to named theories), (b) update propagation (if a theory is challenged, query all edges presupposing it), (c) theory comparison (competing theories show as parallel THEORY_DERIVED edges with different tags).
**Status**: DECIDED.

### 7. REVISED WARRANT TYPE SET
The full type set is now:
1. CONSTITUTIVE (d = 0.95)
2. MECHANISM (d = 0.80)
3. EMPIRICAL_ASSOCIATION (d = 0.80)
4. FUNCTIONAL (d = 0.65)
5. CAPACITY (d = 0.55)
6. ANALOGICAL (d = 0.40)
7. THEORY_DERIVED [theory name] (d = 0.25)

### 8. IS THE EN BAYESIAN?
**Answer**: No, not in Pearl's technical sense.
- The EN is NOT a Bayesian Network: it permits cycles, parallel edges, and typed edges.
- The EN does NOT satisfy the Markov condition: edges represent evidential support, not probabilistic dependence.
- Update rules for ω are not necessarily Bayesian conditionalization — they may involve qualitative evidence quality judgments.
- The EN IS Bayesian in one narrow sense: ω can be interpreted as a subjective probability (degree of belief), following de Finetti/Ramsey.
- Best description: the EN is a **coherentist** epistemic structure (Quinean web of belief) that *interfaces with* a Bayesian computational structure (the BN) through π.
**Status**: DECIDED. Needs explicit statement in all documents.

### 9. THE THREE DIFFERENT NUMBERS (Critical Distinction)
| Number | Name | Lives in | Measures | Kind of uncertainty |
|--------|------|----------|----------|-------------------|
| ω | Warrant Strength | EN (on each edge) | How well-supported is this evidence? | EPISTEMIC (reducible) |
| d | Discount Factor / Transfer Reliability | Bridge (set by τ) | How much of this evidence type survives transfer? | EPISTEMIC (structural) |
| CPT | Conditional Probability Table | BN (on each edge) | What actually happens given inputs? | ALEATORY (irreducible) |

### 10. EN HAS MORE EDGES THAN BN — WHY
The EN is comprehensive; the BN is operational. Classes of EN content absent from BN:
- **Latent/unobservable states** (raphe nuclei activity, prediction error signals) → collapsed into CPTs
- **Theoretical claims** (predictive coding governs aesthetic response) → contributes to ω of lower-level claims
- **Parallel edges** (multiple evidence types for same relationship) → aggregated by π into single CPT
- **Cycles** (mutual epistemic support) → resolved during projection
- **Warrant type/strength annotations** → consumed by π, "baked into" CPTs
**Status**: DECIDED. This is a key architectural feature, not a side effect.

### 11. SERIAL vs. PARALLEL COMBINATION RULES
**Serial combination** (chain through intermediate nodes): Minimum-discount rule. d_eff = min(d_i). Weakest link dominates. Used when inferring through unverified intermediate steps.

**Parallel combination** (multiple evidence lines for same claim): Additive in log-odds. Total = Σ d_i · ω_i · logit(p_i). More evidence = higher confidence. Used when independent sources converge.

**Explanatory boost**: When a mechanism explains an existing empirical association:
(a) Add mechanism as parallel path (additive)
(b) Increase ω on empirical edge (reduced confounding risk)
(c) Both effects increase confidence — theory/mechanism NEVER decreases confidence relative to the same evidence without theory

**The car mechanic principle**: A mechanic who has fixed 20 carburetors (EMPIRICAL_ASSOCIATION, d=0.80) is more confident than a theorist who only knows combustion chemistry (THEORY_DERIVED, d=0.25). But a mechanic who ALSO understands the theory outperforms both (parallel combination). Explanation adds to empirical evidence; it never subtracts.

**Status**: DECIDED. Major conceptual advance of this session.

### 12. DUAL BN RUNS: Full Projection vs. Empirical Floor
**Architecture**: For each BN edge produced by collapsing an EN path, compute:

**Full projection** (goes into BN's CPT): Standard computation using all links including THEORY_DERIVED. Best estimate for decision-making.

**Empirical floor**: Projection using ONLY empirically grounded links (CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL). CAPACITY, ANALOGICAL, and THEORY_DERIVED removed. Either the chain survives (giving a lower-confidence estimate) or breaks (empirical floor = 0.50, the ignorance prior).

**Theory dependence diagnostic** (categorical):
- **Empirically grounded**: empirical floor ≈ full projection (ratio > 0.80)
- **Theory-augmented**: empirical floor exists but substantially lower (ratio 0.40–0.80)
- **Theory-scaffolded**: empirical floor ≈ 0.50 or chain breaks. Claim DEPENDS on named theory.

**Dual BN option**: Run BN twice — theory-inclusive model and empirical-only model. Compare outputs. "The theory-inclusive model recommends larger windows AND fractal facades. The empirical-only model recommends larger windows but is silent on fractal facades."

**Status**: DECIDED. Novel contribution of this session.

### 13. THEORY vs. MECHANISM DISTINCTION
**Mechanism** (Machamer, Darden, Craver 2000): Specific organized system of entities and activities producing a specific phenomenon. Spatiotemporally located. Can be intervened on. Can break. Lives at implementational level (Marr).

**Theory**: Higher-level explanatory framework explaining WHY mechanisms exist and predicting their form. Not spatiotemporally located. Cannot be directly intervened on. Lives at computational level (Marr). Generates instances rather than being caused by them.

**In the EN**: Theories → THEORY_DERIVED edges (d = 0.25) at top of graph. Mechanisms → MECHANISM edges (d = 0.80) in middle. Observations → EMPIRICAL_ASSOCIATION edges (d = 0.80) at bottom. Stratified structure.

**In the BN**: Theories do NOT appear (too abstract). Mechanisms may appear if intermediate states are measurable; otherwise collapsed into CPTs.

### 14. ACCORDION NATURE OF MECHANISMS
Mechanisms can be described at multiple granularity levels. Early research may establish a coarse mechanism ("light increases serotonin"). Later work elaborates intermediate steps (retinal ganglion cells → retinohypothalamic tract → raphe nuclei → tryptophan hydroxylase).

**Key principle**: Warrant type stays MECHANISM at every granularity level, but warrant strength ω increases as the mechanism is elaborated. The accordion doesn't change type; it changes weight. A coarsely described mechanism (ω = 0.60) vs. a finely described mechanism (ω = 0.90). Both get d = 0.80 for MECHANISM.

**EEG clarification**: EEG is a measurement instrument, not part of the mechanism. "Fractals produce specific EEG patterns" is an empirically established measurement link. "Those EEG patterns reflect prediction error" is a THEORY_DERIVED interpretive link. The mechanism is the neural process; the EEG is how we observe it.

### 15. INTERACTIONS AS EDGE ANNOTATIONS
**Decision**: Most interactions are **annotations on existing edges**, not separate edges.
- An edge A → C gets an optional interaction qualifier: "Evidence gathered at level B = b₀; relationship may not hold at other levels of B."
- Interaction qualifier affects projection: when π encounters annotated edge and target context has B ≠ b₀, further attenuation.
- **Exception**: Well-established, important interactions can be promoted to full edges (e.g., "latitude moderates daylight→mood" as a MECHANISM edge if the mechanism is understood).
**Rationale**: Keeps graph manageable. For N variables, pairwise interactions = O(N²) — would triple edge count as separate edges.

### 16. POPULATION TRANSFER FACTORS (δ) — Major New Component
**The gap identified**: Population transferability (culture, WEIRD bias, neurodiversity, age, SES) has been discussed but never formalized in the architecture.

**Proposed architecture** (hybrid of three options):

**Default**: Every EN edge carries **population metadata** (pop) recording who was studied. π computes **population transfer factor** δ(pop_source, pop_target) ∈ (0,1).

**Full projection formula**:
```
logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)
```

Three multiplicative factors, each doing different work:
- d: how well does this TYPE of evidence transfer?
- ω: how good is this SPECIFIC piece of evidence?
- δ: how well does evidence from THIS population transfer to THAT population?

**Population distance dimensions**:
- Cultural distance (Hofstede dimensions, WEIRD index)
- Demographic distance (age, SES, education)
- Neurodiversity scope (was study neurotypical-only?)
- Ecological validity (lab vs. field, acute vs. chronic)

**Explicit moderator nodes**: When direct evidence of population moderation exists, represent as explicit edges in EN with own warrant types.

**Neurodiversity special case**: Not just attenuation — may involve *reversal* of effects (fluorescent lighting: neutral for neurotypical, aversive for many autistic individuals). Population factor δ handles attenuation but not reversal. Need explicit moderator nodes for neurodiversity effects.

**Sobering implication**: For non-WEIRD populations, δ will be painfully low for most edges. System honestly reports that evidence base is predominantly WEIRD. Creates research prioritization signal.

**David's India fieldwork**: Each study with Indian populations adds new edges (pop = Indian urban adults) or raises δ for existing edges applied to Indian contexts.

**Status**: PROPOSED. Needs formalization and integration into all documents.

### 17. TRANSPORTABILITY ANALYSIS (Pearl & Bareinboim)
Pearl's formal framework for transferring causal effects across contexts:
- Draw causal graph for source context
- Mark S-nodes on every variable where target context might differ
- Derive formal conditions for valid transport

**Limitation**: Assumes you know where to place S-nodes. EN warrant types inform S-node placement:
- MECHANISM warrants → know exactly which variables to check → precise S-node placement
- EMPIRICAL_ASSOCIATION warrants → unknown mediating pathway → S-nodes everywhere → often makes transport formally unidentifiable
- EN warrant types are effectively a guide to S-node placement

---

## Worked Examples Developed This Session

### Example 1: Daylight → Mood Chain (Empirically Grounded)
W→D: CONSTITUTIVE, ω=0.95, d=0.95 (windows admit light by definition)
D→S: MECHANISM, ω=0.85, d=0.80 (Lambert et al., retinal-raphe pathway)
S→M: MECHANISM, ω=0.80, d=0.80 (serotonergic mood regulation, SSRI evidence)
Full projection: d_eff = 0.80, P(mood=positive|windows=large) ≈ 0.74
Empirical floor: 0.74 (identical — all links empirically grounded)
Diagnostic: **Empirically grounded**

### Example 2: Fractal → Wellbeing Chain (Theory-Scaffolded)
Fractals → cortical response: MECHANISM, ω=0.75, d=0.80
Cortical response → prediction error: THEORY_DERIVED [Predictive Processing], ω=0.45, d=0.25
Prediction error → stress reduction: THEORY_DERIVED [Predictive Processing], ω=0.40, d=0.25
Stress reduction → wellbeing: EMPIRICAL_ASSOCIATION, ω=0.70, d=0.80
Full projection: d_eff = 0.25, P(wellbeing=high|fractal_D=1.3) ≈ 0.58
Empirical floor: Chain BREAKS (no empirical path from cortical response to stress). Floor = 0.50
Diagnostic: **Theory-scaffolded [Predictive Processing]**
Research recommendation: Test whether EEG response to architectural fractals reflects prediction error

### Example 3: Car Mechanic (Serial vs. Parallel)
Mechanic with 20 repairs, no theory: EMPIRICAL_ASSOCIATION, d=0.80, ω=0.70
Theorist with combustion chemistry, no repairs: THEORY_DERIVED [Thermodynamics], d=0.25, ω=0.80
Mechanic who also understands theory: Both edges in parallel, additive in log-odds → highest confidence
Demonstrates: explanation ADDS to empirical evidence, never subtracts

---

## Documents To Produce
1. **Master Report**: "The ATLAS Epistemic Network: Architecture, Terminology, and Formal Properties" — comprehensive integration of all material
2. **Updated Cheat Sheet v2**: incorporating all naming changes, population transfer, combination rules, dual BN runs
3. **Technical Appendix**: formulas, worked numerical examples with actual numbers
4. **This Exchange Summary**: (completed)

---

## Updated Terminology Quick Reference
| Old Term | New Term | Symbol |
|----------|----------|--------|
| Epistemic Warrant Graph (EWG) | **Epistemic Network (EN)** | W = (N, E, τ, ω) |
| Confidence weight | **Warrant strength** | ω |
| Discount factor (in prose) | **Transfer reliability** | d |
| EMPIRICAL_COVARIANCE | **EMPIRICAL_ASSOCIATION** | — |
| THEORETICAL_DEFAULT | **THEORY_DERIVED [theory name]** | — |
| (new) | **Population transfer factor** | δ |
| (new) | **Empirical floor** | (diagnostic) |
| (new) | **Theory dependence diagnostic** | Empirically grounded / Theory-augmented / Theory-scaffolded |
