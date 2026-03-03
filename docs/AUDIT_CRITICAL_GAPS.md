# ATLAS Critical Gaps: Implementation Blockers & Quick Fixes

**Date**: March 2, 2026
**Urgency**: THREE ITEMS BLOCK REPRODUCIBILITY

---

## BLOCKER 1: COHERENCE COMPUTATION (C*) — NOT FORMALIZED

### Status
**Missing**: The mathematical formula for computing C* (web-of-belief coherence score).

### Where It's Discussed (But Not Defined)
- PART_IX_WEB_OF_BELIEF: Sections 84–89, ~50 pages of philosophical discussion
- PART_XVII_META_EPISTEMOLOGY: Sections on coherence, entrenchment, belief revision (~100 pages)
- PART_IV_CREDENCE: §52.5 "Full coherence computation" explicitly states it's NOT fully implemented (line 1718)

### What the Document Says (From grep results)

Line 138 (PART_IX): "The web's coherence can be scored as:" [text omitted, formula not shown]

Line 489 (PART_IX): "Equilibrium is not 'truth' but *coherence*—maximum consistency among all beliefs, observations, and principles."

Line 1718 (PART_IV): "**Full coherence computation**: Abandon the three-factor decomposition entirely and compute composite credence through a single coherence assessment of the web — the approach that the web-of-belief infrastructure already supports in principle. This is theoretically attractive but **computationally demanding and would sacrifice the formula's transparency and interpretability**."

### The Problem
The entire Quinean web-of-belief architecture depends on coherence as the central metric. Yet:

1. **No formula** to compute C* from the belief network structure
2. **No algorithm** to identify contradicting beliefs and agreement links
3. **No weights** defined for how to balance positive coherence vs. negative contradiction
4. **No normalization** — how is the score mapped to [0, 1]?
5. **No examples** showing the computation with real data

### How This Blocks Implementation

- **Belief revision** (Algorithm 4 in PART_XVII, line 908): "Iterates until convergence (credences stabilise within a tolerance ε)" — but convergence of what? How is coherence measured at each iteration?
- **Web-of-belief diagnostics**: Cannot identify when coherence is degraded without a metric
- **Validation**: Cannot test whether the system actually achieves coherence as claimed

### What Should Be There

A formal specification like:

```
C* = Σ_{(i,j): i<j} [w_ij · A_ij · similarity_scale(C_i, C_j) − λ · w_ij · cont_ij]

where:
  - w_ij = strength of connection between beliefs i and j (0 to 1)
  - A_ij = agreement indicator (1 if mutually supportive, 0 otherwise)
  - similarity_scale(C_i, C_j) = function mapping (0,1)² → ℝ
  - cont_ij = contradiction degree (0 to 1)
  - λ = parameter balancing agreement vs. contradiction (0 to 1)

Normalization:
  C*_normalized = C* / max_possible_coherence

Worked example:
  [5–10 node web with scores for each edge]
```

But **this is not in the document**.

### Recommended Action

**Priority: URGENT**

1. Write formal specification for C* (1–2 pages)
2. Provide worked example with 5–10 beliefs (1 page)
3. Define the algorithm for:
   - Computing agreement links (when do beliefs support each other?)
   - Computing contradiction links (when do beliefs contradict?)
   - Weighting edges in the web
4. Show sensitivity analysis: how much does C* change if λ parameter varies?

**Estimated effort**: 1–2 weeks

---

## BLOCKER 2: VOI (VALUE OF INFORMATION) FORMULA — INCOMPLETE

### Status
**Partial**: Conceptual framework present; mathematical formula missing.

### Where It's Discussed
- PART_XV_TECHNICAL, §121.3 "VOI for Literature Search vs. Experimental Design" (lines 236–302)
- Lines 258–259 define conceptual components
- Lines 280–302 provide worked example

### What the Document Says

Line 258–259:
> "Structural VOI: How much coherence would be gained if the gap were fully closed? (Measured as counterfactual coherence improvement on the web of belief.)"
>
> "Epistemic VOI: How much would uncertainty about this belief be reduced? (Measured as entropy reduction if we got strong evidence either way.)"

Line 302: Example output — "VOI per dollar: 0.595 / 1.25 = **0.476 information per dollar**"

### The Problem
The document states (line 254): "**VOI Scoring Formula for Literature Search**" but then provides:
1. Conceptual definitions (above)
2. Worked example with final answer (VOI = 0.8)
3. NO explicit formula with variable definitions

### How This Blocks Implementation

The system uses VOI to:
- Prioritize literature searches (line 219): "**VOI Gap Identified** → **Search Strategy Selected** → **Targeted Query Executed**"
- Decide whether to close a gap (line 302): "VOI per dollar = 0.595 / 1.25 = 0.476 — informative?"
- Rank candidate papers (§121.3)

But without a formula, **it is impossible to**:
- Automate VOI computation
- Validate that the system is actually computing what it claims
- Compare against alternative VOI formulations
- Calibrate the decision threshold ("VOI ≥ 0.6 triggers search?")

### What Should Be There

A formal specification like:

```
VOI(gap) = P(close | search) · Coherence_gain(closed)
         + P(partial | search) · Coherence_gain(partial)
         + P(fail | search) · Coherence_gain(fail)
         − cost(search)

where:
  - P(close | search) = probability search finds definitive evidence (0 to 1)
  - P(partial | search) = probability search finds partial evidence
  - P(fail | search) = probability search finds nothing relevant
  - Coherence_gain(state) = change in C* if gap reaches state (before – after)
  - cost(search) = time/money cost in comparable units

Example computation:
  Gap: "Does daylight increase mood?" (currently contradicted by 2 studies)
  P(close) = 0.30 (likelihood search finds meta-analysis resolving contradiction)
  P(partial) = 0.60 (likelihood search finds supportive study)
  P(fail) = 0.10
  Coherence_gain(closed) = +0.25 (C* improves from 0.82 to 1.07, normalized)
  Coherence_gain(partial) = +0.08
  Coherence_gain(fail) = −0.02
  cost(search) = ~$2.00

  VOI = 0.30 · 0.25 + 0.60 · 0.08 + 0.10 · (−0.02) − 2.00
      = 0.075 + 0.048 − 0.002 − 2.00
      = −1.879 (negative VOI; search not worth it)
```

But **this level of formalization is missing**.

### Recommended Action

**Priority: URGENT**

1. State the VOI formula explicitly (2–3 lines of math)
2. Define each variable (P, Coherence_gain, cost)
3. Explain how to estimate each component (from what data?)
4. Provide 2–3 worked examples showing different gap types
5. Specify decision rule: "VOI ≥ [threshold] triggers search"

**Estimated effort**: 1 week

---

## BLOCKER 3: d (TRANSFER RELIABILITY) VALUES — UNJUSTIFIED CONSTANTS

### Status
**Asserted**: Seven d values (0.95, 0.80, 0.80, 0.65, 0.55, 0.40, 0.25) are stated as design decisions with no empirical or theoretical justification.

### Where It's Stated
PART_IV_CREDENCE, §48.1 (line 50):

| Warrant Type | d Value | Rationale (From Document) |
|---|---|---|
| CONSTITUTIVE | 0.95 | "Window area determines daylight exposure... relationship is definitional" |
| MECHANISM | 0.80 | Claims about causal pathways |
| EMPIRICAL_ASSOCIATION | 0.80 | Statistical correlations |
| FUNCTIONAL | 0.65 | "Performance under specific conditions" |
| CAPACITY | 0.55 | "Latent abilities" |
| ANALOGICAL | 0.40 | "Reasoning by analogy" |
| THEORY_DERIVED | 0.25 | "Untested theoretical framework... theory might be wrong" |

### The Problem

**Why d = 0.95 for CONSTITUTIVE and not 0.90 or 0.98?**

- No empirical data cited (e.g., meta-analysis showing CONSTITUTIVE claims replicate 95% of the time)
- No theoretical derivation (e.g., "A definitional relationship has uncertainty from [X], which compounds to 0.05 total error")
- No panel decision document referenced (though style suggests these are design decisions)

**Why the specific gap structure?**
- CONSTITUTIVE → MECHANISM: 0.15 drop (0.95 → 0.80)
- MECHANISM → FUNCTIONAL: 0.15 drop (0.80 → 0.65)
- FUNCTIONAL → CAPACITY: 0.10 drop (0.65 → 0.55)
- CAPACITY → ANALOGICAL: 0.15 drop (0.55 → 0.40)
- ANALOGICAL → THEORY_DERIVED: 0.15 drop (0.40 → 0.25)

Is this structure principled or arbitrary?

### How This Blocks Reproducibility

The d values are **parameters in every projection** (line 107):
```
logit(p_target) = d(τ) · ω · δ · logit(p_lab)
```

A 10% shift in d cascades through all predictions:

| Scenario | d(MECHANISM) = 0.80 | d(MECHANISM) = 0.72 | Difference |
|---|---|---|---|
| logit(p_lab) = 1.0, ω = 0.80, δ = 0.90 | logit(p_target) = 0.576, p_target = 0.640 | logit(p_target) = 0.518, p_target = 0.627 | −1.3% |
| logit(p_lab) = 2.0, ω = 0.80, δ = 0.90 | logit(p_target) = 1.152, p_target = 0.760 | logit(p_target) = 1.037, p_target = 0.738 | −2.2% |

**Implication**: Published predictions depend on unjustified constants. Peer review cannot validate whether the values are correct.

### Recommended Action

**Priority: HIGH** (not urgent, but foundational)

Choose ONE of:

**Option A: Empirical Justification**
- Conduct meta-analysis of replication studies, stratified by warrant type
- Example: "Of 100 MECHANISM claims in the literature, what fraction are successfully replicated by independent teams? That frequency is d(MECHANISM)."
- Effort: 2–3 months of literature work

**Option B: Sensitivity Analysis**
- Show how ATLAS predictions change if d values shift by ±10%
- Document which template conclusions are robust (still hold even if d changes) vs. sensitive (collapse if d shifts)
- Provide confidence intervals on d values: "d(MECHANISM) = 0.80 ± 0.15" (implies true value could be 0.65–0.95)
- Effort: 2–3 weeks of simulation

**Option C: Panel Review & Attribution**
- Reference the panel decision that established these values (e.g., "Decision D-48.1A: Panel consensus...")
- Document panelist disagreement (if any) on the values
- Provide the panel's justification (conceptual, empirical, or pragmatic)
- Effort: 1–2 weeks (if decision log exists)

**We recommend Option B (sensitivity analysis) + Option C (panel attribution) as fast path.**

**Estimated effort**: 2–3 weeks

---

## NON-BLOCKER GAPS (But Important for Rigor)

### Gap 4: δ (POPULATION TRANSFER) DEFAULT VALUE = 0.90

**Location**: PART_IV_CREDENCE, §48.3A, line 169

**Problem**: Why start at 0.90 and not 0.85 or 0.95?

**Recommendation**: Add one sentence: "This default reflects [empirical basis], calibrated against [data source]. Sensitivity analysis shows predictions are robust to δ ∈ [0.80, 0.95]."

**Effort**: 1 hour

---

### Gap 5: δ (MINIMUM FEASIBLE) = 0.30

**Location**: PART_IV_CREDENCE, §48.3A, line 175

**Problem**: Why 0.30 and not 0.25 or 0.35? What is the epistemological meaning?

**Recommendation**: Add explanation: "Below δ = 0.30, uncertainty from population differences exceeds [threshold], making projection unreliable. We recommend empirical replication instead."

**Effort**: 30 minutes

---

### Gap 6: ω FLOOR = 0.05, CEILING = 0.98

**Location**: PART_IV_CREDENCE, §48.3B, line 336

**Problem**: Why these specific bounds?

**Current Text**: "Final clamping: ω ∈ [0.05, 0.98]. The floor prevents any edge from contributing zero (we always have *some* evidence), and the ceiling prevents overconfidence (we never claim certainty about a transfer)."

**Recommendation**: Add: "These bounds implement the principles [X] and [Y]. Sensitivity: if bounds were [0.01, 0.99], predictions would shift by [±Z%]."

**Effort**: 2–3 hours

---

### Gap 7: TEA WEIGHTS — LACK SENSITIVITY ANALYSIS

**Location**: PART_IV_CREDENCE, §48.3C, line 512

**Current Formula**:
```
TEA = 0.30·E_conf + 0.25·P_nov + 0.15·Prec + 0.20·U_uptake + 0.10·Coh
```

**Problem**: Why 0.30 vs. 0.25 for top two weights? How much do theory rankings change if weights become {0.25, 0.25, 0.20, 0.20, 0.10}?

**Recommendation**: Add table showing:
| Theory | Current TEA | TEA (Alt. weights) | Rank Change |
|---|---|---|---|
| Biophilia | 0.65 | 0.63 | (small) |
| Circadian neuroscience | 0.88 | 0.87 | (small) |
| Fractal architecture | 0.42 | 0.41 | (small) |

**Effort**: 3–4 hours

---

### Gap 8: AESHI WEIGHTS — LACK JUSTIFICATION

**Location**: PART_IV_CREDENCE, §53.8, line 1914

**Current Formula**:
```
AESHI = 0.24·Contract + 0.19·Pipeline + 0.24·Web_BN + 0.19·Theory + 0.09·Stability + 0.05·QA_Epistemic
```

**Problem**: Why is QA_Epistemic (0.05) the lowest weight? It sounds important but is downweighted. Why?

**Recommendation**: Add explanation for the weight hierarchy. Is it:
- Based on impact (how much does each component affect overall system integrity)?
- Based on tractability (how easy is it to improve)?
- Based on historical data (which components have been most problematic)?

Then show: "If weights were equal (0.167 each), AESHI would be [value]."

**Effort**: 2–3 hours

---

### Gap 9: DECISION LOG REFERENCES NOT EMBEDDED

**Pattern**: Throughout the document, formulas reference decision logs:
- Line 253: "Panel Revision S4, Mayo"
- Line 512: "Decision D-48C.1"
- Line 332: "Panel Revision S1, Woodward"

**Problem**: The decision documents are **not shown in the master document** and **not cited in PART_XXI_SOURCE_INDEX** (as far as the audit can tell).

**Recommendation**: Either:
- Embed decision summaries inline (2–3 paragraphs) where referenced, OR
- Create "PART_XXII_DECISION_LOG.md" with all referenced decisions

**Effort**: 2–3 hours (if decisions exist); 4–6 weeks (if they need to be written)

---

## SUMMARY TABLE: REMEDIATION ROADMAP

| Gap | Severity | Type | Est. Effort | Recommended Action |
|---|---|---|---|---|
| 1. Coherence (C*) formula | **BLOCKER** | Missing formula | 1–2 weeks | Formalize; add examples |
| 2. VOI formula | **BLOCKER** | Incomplete | 1 week | State math; define variables |
| 3. d values (0.95, 0.80, etc.) | **HIGH** | Unjustified constants | 2–3 weeks | Sensitivity analysis + panel attribution |
| 4. δ default (0.90) | Medium | Unjustified constant | 1 hour | Add one sentence |
| 5. δ minimum (0.30) | Medium | Unjustified constant | 30 minutes | Add explanation |
| 6. ω bounds [0.05, 0.98] | Medium | Unjustified constants | 2–3 hours | Add sensitivity |
| 7. TEA weights | Medium | Unjustified constants | 3–4 hours | Add sensitivity table |
| 8. AESHI weights | Medium | Unjustified constants | 2–3 hours | Add weight justification |
| 9. Decision log embedment | Low | Documentation | 2–3 hours | Link or embed |
| 10. Figures (6 proposed) | Low | Pedagogy | 2–3 days | Add diagrams |

**Total High-Priority Effort**: ~4–6 weeks
**Total Medium-Priority Effort**: ~2–3 weeks
**Total Low-Priority Effort**: ~1–2 weeks

---

## QUICK WINS (< 1 hour each)

These can be done immediately to improve rigor:

1. **Add "Sensitivity Analysis" subsection** to each of §48.3B (ω), §48.3A (δ), §48.3C (TEA), §53.8 (AESHI)
   - Show a 2×2 table: "If [parameter] ± 10%, predicted [outcome] changes by ±[%]"
   - Effort: 10 minutes per subsection (40 minutes total)

2. **Replace "design decision" language with explicit attribution**
   - Instead of: "The canonical δ values in this section represent the *current state of knowledge*"
   - Rewrite: "The canonical δ values were established by [panel name] on [date] using [method]. See Decision D-X.Y."
   - Effort: 30 minutes

3. **Add margin notes** identifying each unjustified constant
   - Markdown: `[NEEDS JUSTIFICATION: why d = 0.95 and not 0.90?]`
   - This flags gaps for readers and helps David prioritize fixes
   - Effort: 20 minutes

4. **Cross-reference PART_XV_TECHNICAL §121.3** to show where VOI is used
   - Add sentence: "VOI is computed using [formula — see §121.3] and used to prioritize [gap type] searches."
   - Effort: 5 minutes

**Total "quick wins": ~1.5 hours**

---

## NEXT STEPS FOR DAVID

1. **Decide**: Which gaps are blockers? (Recommend: C* and VOI, yes; d values, yes — all three should be fixed before publication)

2. **Assign**: Who will fix each gap? (David? Panel members? Claude?)

3. **Timeline**: When should remediation be complete? (Recommend: 4–6 weeks for all high-priority items)

4. **Validation**: How will fixes be reviewed? (Recommend: David + 2 panel members for each formula)

---

## APPENDIX: LINE NUMBER REFERENCE

All line numbers are from ATLAS master document as read on March 2, 2026. These may shift if sections are edited.

| Gap | File | Section | Lines |
|---|---|---|---|
| Coherence (C*) | PART_IX | §84–89 | 13–500+ |
| Coherence (C*) comment | PART_IV | §52.5 | 1718 |
| VOI formula | PART_XV | §121.3 | 236–302 |
| d values | PART_IV | §48.1 | 48–52 |
| δ defaults | PART_IV | §48.3A | 137–200 |
| ω formula | PART_IV | §48.3B | 314–336 |
| ω range table | PART_IV | §48.3B | 340–350 |
| TEA formula | PART_IV | §48.3C | 512 (weights) |
| AESHI formula | PART_IV | §53.8 | 1914 |
| CCI formula | PART_IV | §50.9 | 1391 |

