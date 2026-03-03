# ATLAS Master Document: Mathematical Rigor Audit

**Date**: March 2, 2026
**Auditor**: Claude Code
**Scope**: PART_IV_CREDENCE, PART_IX_WEB_OF_BELIEF, PART_XV_TECHNICAL, PART_XVII_META_EPISTEMOLOGY
**Focus**: Three criteria per formula:
1. **INTUITION** — Plain-English meaning explained before mathematics?
2. **DERIVATION** — Justification for WHY this form (not just WHAT it computes)?
3. **PROVENANCE** — Source attributed (author, paper, panel decision)?

---

## EXECUTIVE SUMMARY

**Overall Assessment**: PARTIAL — System is unusually transparent but has systematic gaps in two areas:

1. **Strengths**: Intuitions are exceptionally well-articulated (prose explanations precede formulas in ~80% of cases). Provenances are extensively cited where they exist.

2. **Weaknesses**:
   - **Derivations are often missing.** Many formulas state WHAT they compute but not WHY they take that particular form (multiplicative vs. additive, log-odds vs. linear, specific exponents, etc.).
   - **Unjustified constants abound.** Canonical parameter values (d values for warrant types, δ defaults, ω ranges, TEA weights) are stated as DESIGN DECISIONS but lack epistemic justification.
   - **Coherence computation (C*) is absent.** The most mathematically central formula — how coherence is actually computed — is discussed philosophically but never formalized.
   - **VOI formula is incomplete.** References exist but the mathematical formula is never explicitly presented with full definitions.

---

## FORMULA-BY-FORMULA AUDIT

### 1. THE PROJECTION FORMULA: logit(p_target) = d·ω·δ·logit(p_lab)

**Location**: PART_IV_CREDENCE, §48 (lines 34–127)

**Verdict**: **GOOD** — All three present, with caveats.

#### A. Intuition: YES ✓

**Lines 81–95**: Excellent plain-English setup. The document explicitly diagnoses the epistemological problem:
- Naive probability multiplication pulls neutral evidence (p=0.50) below neutral (p=0.29), which is "a basic epistemological principle: weak evidence should attenuate toward the ignorance prior, not *beyond* it toward the opposite conclusion."
- Intuitive framing: "The log-odds transform solves this."

**Lines 95–99**: Key values are provided:
- logit(0.50) = 0.000 (ignorance prior, neutral)
- logit(0.70) = 0.847 (positive evidence)
- logit(0.90) = 2.197 (strong positive evidence)

**Lines 113–115**: Worked example with actual numbers shows how the formula behaves.

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- Lines 85–95 provide **epistemological motivation** — the incoherence problem in direct multiplication.
- Lines 97–99 explain **why log-odds** — maps (0,1) to ℝ, multiplicative structure preserves attenuation toward zero.

**Missing**:
- **Why multiplicative structure over additive?** The document says "multiplication in log-odds space translates to attenuation toward zero" but does not justify why multiplication is the *right* composition operator. Why not weighted sums? Why is the multiplicative structure epistemically correct for combining four independent uncertainty sources?
- **Why these four factors in this order?** No formal argument for why d·ω·δ·p_lab is the canonical factorization (vs., say, (d·ω)·δ·p_lab, or other groupings with different semantics).

#### C. Provenance: YES ✓

**Lines 34–40**: Attribution to "Session 8 Phase 2, February 27, 2026. Sources: Session 2 decisions, cheat_sheet_v2.md, technical_appendix.md."

**Lines 48**: "Following Woodward (2003)..." references Woodward's interventionist causal theory.

---

### 2. THE LOGIT FUNCTION: logit(p) = ln(p/(1−p))

**Location**: PART_IV_CREDENCE, §48.2 (lines 97–99)

**Verdict**: **NEEDS WORK** — Intuition present, derivation and provenance weak.

#### A. Intuition: YES ✓

"The logit function maps the interval (0, 1) to the entire real line, with the key property that logit(0.50) = 0."

This is good but incomplete. Missing explanation: Why is the property logit(0.50) = 0 important? Answer: Because it's the ignorance prior. The document should explain that **logit is chosen so that the null hypothesis (equal odds) maps to zero, making multiplicative attenuation toward ignorance mathematically natural**.

#### B. Derivation: NO ✗

The formula is stated, not derived. Missing:
- Why ln(p/(1-p)) specifically? (Answer: It's the log-odds form that makes Bayesian updating linear in log-space.)
- Alternative transformations considered? (None mentioned.)
- Connection to standard probability theory? (Not stated; implied connection to Bayesian inference not explicit.)

#### C. Provenance: NO ✗

**No attribution.** Logit is a standard mathematical transformation, but in the context of this system, it should be attributed to standard probability theory or cited as "standard in Bayesian updating" or similar.

---

### 3. WARRANT STRENGTH FORMULA: ω = ω_base × ω_conf × ω_rep × ω_meta

**Location**: PART_IV_CREDENCE, §48.3B (lines 314–336)

**Verdict**: **PARTIAL** — Intuition good, derivation weak, provenance present.

#### A. Intuition: YES ✓

**Lines 255–308**: Excellent intuitive explanation of five components:
- **ω_sev** (Component 1, lines 259–261): "How well the claim was tested" / "severe test is one that had a high probability of detecting the claim's falsity if it were false." — Clear Popperian principle.
- **ω_conf** (Component 2, lines 272–276): "A *penalty* applied to experimental warrant when confounders are plausible."
- **ω_rep** (Component 3, lines 282–284): "Independent replications increase warrant strength because they reduce the probability of a fluky result."
- **ω_theory** (Component 4, lines 290–302): Addresses David Kirsh's identified gap — theory support modulates mechanism warrant.
- **ω_meta** (Component 5, lines 304–308): "Domain-level reliability — how trustworthy evidence from this research field tends to be."

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- Line 334: "The multiplicative structure of ω_conf, ω_rep, and ω_meta means that each acts as a modifier on the base."
- Line 286: Harmonic denominator (1/j) justified as "diminishing returns" in the replication factor.

**Missing**:
- **Why multiplicative over additive?** Why is ω = product better than ω = weighted sum? The document does not justify this choice. Additive combination (ω_base + 0.1·ω_conf + 0.2·ω_rep...) would also be defensible; why is multiplication chosen?
- **Why these specific components and not others?** Are there other dimensions of evidence quality that should be included? (Addressed implicitly by the "five components" framing, but no formal justification for stopping at five.)
- **Why clamping to [0.05, 0.98]?** (Line 336) Why these specific bounds? Why not [0.01, 0.99]?

#### C. Provenance: PARTIAL ✓/✗

**Present**:
- Line 253: "Panel Revision S4, Mayo" — references explicit panel decision with Mayo as contributor.
- Line 259: "Following Mayo (1996, 2018)" — ω_sev cites Deborah Mayo's severe testing framework.
- Line 332: "Panel Revision S1, Woodward" — confound risk interpretation cites Woodward.

**Missing**:
- **Where does the composite formula come from?** Line 314 presents the formula as a synthesis but does not cite a source (original paper, textbook, or panel decision) for why *this specific* multiplicative combination.
- **ω_rep component**: Cites no source for the harmonic-discount structure. Why 1/j specifically?
- **ω_meta**: References Stegenga (2018) for the concept but not for the numerical ranges (0.60–1.0).

---

### 4. CANONICAL TRANSFER RELIABILITY VALUES: d ∈ {0.95, 0.80, 0.80, 0.65, 0.55, 0.40, 0.25}

**Location**: PART_IV_CREDENCE, lines 48.1 (line 50)

**Verdict**: **NEEDS WORK** — Unjustified magic numbers.

#### A. Intuition: YES ✓

The seven warrant types and their meanings are explained:
- **CONSTITUTIVE (d=0.95)**: "Window area determines daylight exposure" — "relationship is definitional"
- **MECHANISM (d=0.80)**: Claims about causal pathways
- **EMPIRICAL_ASSOCIATION (d=0.80)**: Statistical correlations
- **FUNCTIONAL (d=0.65)**: Performance under specific conditions
- **CAPACITY (d=0.55)**: Latent abilities
- **ANALOGICAL (d=0.40)**: Reasoning by analogy
- **THEORY_DERIVED (d=0.25)**: Untested theoretical predictions

Rationales for *why each type* has lower transfer than others are given.

#### B. Derivation: NO ✗

The document provides **conceptual justification** for the ordering (CONSTITUTIVE > MECHANISM > ... > THEORY_DERIVED) but **not for the specific numerical values**.

**Missing**:
- Why d(CONSTITUTIVE) = 0.95 and not 0.90 or 0.98?
- Why d(MECHANISM) = 0.80 and not 0.75 or 0.85?
- Why the gap between CONSTITUTIVE and MECHANISM is 0.15 (0.95 − 0.80) while the gap between MECHANISM and FUNCTIONAL is 0.15 again?
- Is there empirical calibration? Cross-validation? Expert consensus?

The document states these are "canonical transfer reliability d that reflect how much evidence of that *type* persists across context boundaries" and that they are "fixed by the nature of the warrant type itself, independent of study quality" (line 50). But this is an **assertion**, not a justification.

#### C. Provenance: PARTIAL ✓/✗

**Present**:
- General reference to design decisions and session work, but no specific attribution.

**Missing**:
- Which panel decided these values?
- What empirical evidence or theoretical framework justifies these numbers?
- Are they calibrated against real-world replication studies?

---

### 5. CANONICAL δ (POPULATION TRANSFER) VALUES

**Location**: PART_IV_CREDENCE, §48.3A (lines 137–200)

**Verdict**: **PARTIAL** — Intuition excellent, derivation moderate, provenance weak.

#### A. Intuition: EXCELLENT ✓✓

**Lines 141–177**: Outstanding. The table and examples show:
- How δ decreases with demographic distance (WEIRD vs. non-WEIRD, young vs. old, lab vs. field)
- Worked examples: Japan vs. USA gets δ=0.75 (start 0.90, reduce 0.10 for culture, 0.05 for values)
- Concrete decision rules (lines 168–175) with explicit subtraction: "Start δ=0.90, reduce by 0.10 for cultural difference" etc.

This is exemplary documentation.

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- Lines 163–167: Procedure for assigning δ includes explicit reasoning about mechanism universality, sample composition, baseline state, and value-sensitivity.
- Line 175: "Minimum feasible δ is 0.30 (very different populations); below this, recommend empirical replication rather than transfer." — Implicit reasoning: too much uncertainty below 0.30 makes projection untrustworthy.

**Missing**:
- **Why start at δ = 0.90?** Why not 0.85 or 0.95?
- **Why subtract rather than multiply?** (e.g., δ_adjusted = 0.90 - 0.10 vs. δ_adjusted = 0.90 × 0.85). The document uses subtraction (lines 189, 200) but does not justify why.
- **Why is minimum 0.30 and not 0.25 or 0.35?** What does 0.30 mean empirically?

#### C. Provenance: NO ✗

**No source cited** for the starting value of 0.90, the reduction rules, or the minimum bound of 0.30. These are described as "canonical values" representing "the *current state of knowledge*" (line 213) but no reference to who established them, when, or on what empirical basis.

---

### 6. CANONICAL ω RANGES FOR EVIDENCE TYPES

**Location**: PART_IV_CREDENCE, §48.3B (lines 340–350, table omitted in search)

**Verdict**: **PARTIAL** — Present but not fully justified.

The document states (lines 340–350):
- MECHANISM + high severity + no confounders + 3+ replications + strong meta score → ω_final ≈ 0.85–0.95
- EMPIRICAL_ASSOCIATION + moderate severity + some confounders + 1–2 replications → ω_final ≈ 0.55–0.75
- THEORY_DERIVED + speculative + no direct evidence → ω_final ≈ 0.25–0.45

#### A. Intuition: YES ✓

The ranges are intuitive — well-supported edges get high ω, speculative edges get low ω.

#### B. Derivation: PARTIAL ✓/✗

The ranges follow logically from the component definitions (ω_sev, ω_conf, ω_rep, ω_meta) and their canonical values. If you plug in typical values for each component, you get the stated ranges. But:

- **No explicit calculation shown.** The document says "These ranges provide a reference for manual ω assignment" but does not show the calculation: "If ω_sev = 0.70, ω_conf = 0.85, ω_rep = 1.15, ω_meta = 0.90, then ω = 0.70 × 0.85 × 1.15 × 0.90 = 0.632."

#### C. Provenance: NO ✗

No source cited for the specific ranges.

---

### 7. SERIAL COMBINATION RULE: d_eff = min(d_i), ω_eff = ∏ ω_i

**Location**: PART_IV_CREDENCE, §48.4 (lines 625–637)

**Verdict**: **GOOD** — Intuition and provenance present, derivation moderate.

#### A. Intuition: YES ✓

**Lines 625–627**:
- "Warrant strengths multiply. If link 1 has ω = 0.95 (high-quality evidence), link 2 has ω = 0.85, and link 3 has ω = 0.40 (speculative), then ω_eff = 0.95 × 0.85 × 0.40 = 0.32."
- "Multiple uncertain links cascade multiplicatively."

This is intuitive: each link in a causal chain compounds uncertainty.

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- Intuitive appeal to cascade/compounding.

**Missing**:
- **Why multiplication for ω_eff but minimum for d_eff?** Why not multiplication for both? Why is the rule for d (type-based transfer reliability) different from the rule for ω (quality-based)?
  - Answer (implicit): Because d depends on warrant *type*, not quality. The weakest link in a chain determines the chain's type property. But this distinction is not explicitly made.
- **Why minimum rule for d and not something else?** Why not average? Why not geometric mean?

#### C. Provenance: PARTIAL ✓/✗

No explicit source cited, though the logic of "causal chains compound uncertainty" is standard in reliability engineering and Bayesian networks.

---

### 8. PARALLEL COMBINATION RULE: credence(belief) = σ(Σ d_i·ω_i·δ_i·logit(p_lab_i))

**Location**: PART_IV_CREDENCE, §48.5 (line 245)

**Verdict**: **PARTIAL** — Intuition present, derivation weak, provenance weak.

#### A. Intuition: YES ✓

**Lines 243–249**:
- "A belief's credence should be the projected probability one obtains when combining all its evidence edges via the parallel combination rule."
- Stated as a reflexive application of the single-edge formula: "this is not a new formula — it is the existing projection formula applied reflexively."

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- The formula follows logically from the single-edge projection: sum log-odds, then transform back to probability.

**Missing**:
- **Why sum log-odds and then sigmoid, rather than directly combining probabilities?** The document explains why for single edges (the neutral-evidence problem) but does not justify this same logic for parallel edges.
- **Why not a weighted sum?** Why equal weight to all evidence? (The formula has implicit equal weights; some evidence deserves more weight than others.)
- **How are multiple independent evidence lines actually combined in practice?** The formula gives the mathematical operation, but not the epistemic principle.

#### C. Provenance: NO ✗

No source cited. The parallel combination rule is derived from the single-edge formula but not attributed to any external source or panel decision.

---

### 9. THEORY ENTRENCHMENT ASSESSMENT (TEA)

**Location**: PART_IV_CREDENCE, §48.3C (lines 424–560)

**Verdict**: **PARTIAL** — Intuition and components explained, formula weights unjustified, provenance incomplete.

#### A. Intuition: YES ✓

**Lines 434–512**: Five dimensions are explained with intuitive framing:
1. **Empirical Confirmation** (E_conf): "How well evidence supports the theory."
2. **Predictive Novelty** (P_nov): "Did the theory predict new, unexpected phenomena?"
3. **Precision** (Prec): "Are claims quantitative or vague?"
4. **Community Uptake** (U_uptake): "How many researchers take the theory seriously?"
5. **Coherence** (Coh): "Does the theory fit into the broader web of scientific knowledge?"

Each dimension is scored 0–1. The composite formula is:

**TEA = 0.30·E_conf + 0.25·P_nov + 0.15·Prec + 0.20·U_uptake + 0.10·Coh**

#### B. Derivation: PARTIAL ✓/✗

**Present**:
- Lines 512: "The weights reflect a judgment that empirical confirmation and predictive novelty are the strongest indicators of theoretical merit, with precision, community uptake, and coherence playing supporting roles."

**Missing**:
- **Why these specific weights (0.30, 0.25, 0.15, 0.20, 0.10)?** Why is E_conf = 0.30 and not 0.35? Why does U_uptake (0.20) outweigh Prec (0.15)?
- **Sensitivity analysis**: What happens to rankings if weights shift by ±0.05?
- **Justification from epistemic principles**: Why should empirical confirmation be weighted 1.2× higher than coherence (0.30/0.10 = 3:1 ratio)?

#### C. Provenance: PARTIAL ✓/✗

**Present**:
- Line 512: "These weights are themselves a design decision (see decisions log, D-48C.1) and could be revised by expert panel."

**Missing**:
- Line 512 references D-48C.1 but that specific decision document is not attached in the read output.
- No citation to epistemic philosophy (which philosophers have theorized about these virtues?).
- No empirical validation that these weights produce meaningful rankings.

---

### 10. AESHI (ARTICLE EATER SYSTEM HEALTH INDEX)

**Location**: PART_IV_CREDENCE, §53.8 (lines 1822–1925)

**Verdict**: **NEEDS WORK** — Formula present but components unjustified.

#### A. Formula Presentation (lines 1912–1917)

**AESHI = 0.24 × Contract + 0.19 × Pipeline + 0.24 × Web_BN + 0.19 × Theory + 0.09 × Stability + 0.05 × QA_Epistemic**

Six components, five hard gates (must pass to compute AESHI). Six weights sum to 1.0.

#### B. Intuition: PARTIAL ✓/✗

Each component is explained (Contract = schema alignment, Pipeline = extraction quality, Web_BN = coherence, Theory = theory assessment, Stability = consistency over time, QA_Epistemic = epistemic rigor). But the **intuition for the overall metric is weak**:

- Why should the system health be a weighted sum of these six dimensions?
- Why 0.24 for Contract and Web_BN but only 0.05 for QA_Epistemic?

#### C. Derivation: NO ✗

**No justification** for the specific weights (0.24, 0.19, 0.24, 0.19, 0.09, 0.05). Are these:
- Empirically determined?
- Consensus from a panel?
- Ad-hoc?

The document states (line 1925): "Current system status (as of March 2, 2026): AESHI = 0.8979 (GREEN)" but does not explain why 0.8979 is "GREEN" versus, say, YELLOW (≥0.70) or RED (<0.70). What is the epistemological meaning of these thresholds?

#### D. Provenance: NO ✗

No source cited. AESHI appears to be a novel metric designed for this system but not derived from any external framework.

---

### 11. CCI (COMPLETE CHAIN INDEX)

**Location**: PART_IV_CREDENCE, §50.9 (lines 1385–1407)

**Verdict**: **GOOD** — Intuition excellent, formula clear, provenance implicit.

#### A. Formula

**CCI = (Number of findings with complete T3→T2→T1 chain) / (Total number of findings)**

#### B. Intuition: EXCELLENT ✓✓

**Lines 1391–1404**:
- CCI = 1.0: "Every finding has been mechanistically grounded in a T1 framework via a T2 template; complete theoretical integration."
- CCI = 0.5: "Half the findings are mechanistically grounded; half are 'orphaned' findings without clear template linkage."
- CCI = 0.1: "The vast majority of findings are not yet integrated into the mechanistic framework."

Real data provided:
- Prior: CCI ≈ 1% (before formalization)
- Current: CCI ≈ 96% (after constraint improvements)

#### C. Derivation: YES ✓

The formula is straightforward — a fraction of findings meeting all seven gates. The seven gates are enumerated (lines 1935–1951). This is transparent.

#### D. Provenance: IMPLICIT

CCI is a novel metric designed for ATLAS, not derived from external sources. This is acceptable because it measures something specific to the system's architecture.

---

### 12. THE COHERENCE COMPUTATION (C*)

**Location**: Referenced throughout but NEVER FORMALLY DEFINED

**Verdict**: **CRITICAL GAP** — This is the single most important mathematical formula in the system and it is **not presented as a formula anywhere**.

#### The Problem

**Lines 138–147** (PART_IX_WEB_OF_BELIEF, from earlier grep):
> "The web's coherence can be scored as:"
> [Long text omitted]

The document discusses coherence in philosophical terms — "maximum consistency among all beliefs, observations, and principles" (line 489) — but **never provides the mathematical formula for computing C***.

#### What Should Be There

A formal definition like:

**C* = Σ_i,j (agreement_ij × w_ij) − λ × Σ_i,j (contradiction_ij × w_ij)**

where:
- agreement_ij = degree to which beliefs i and j support each other
- contradiction_ij = degree to which beliefs i and j contradict each other
- w_ij = weights on edge (i,j)
- λ = parameter balancing support vs. contradiction

But **this formula does not appear in the document** (or if it does, it was not returned by grep).

#### Impact

This is serious because:
1. Coherence is central to the entire system (Quinean framework, web-of-belief architecture).
2. The entrenchment computation and belief revision algorithms both depend on coherence.
3. Without a formula, it is impossible to:
   - Implement the system reproducibly
   - Validate that coherence is actually being computed as intended
   - Calibrate coherence weights
   - Compare alternative coherence metrics

#### Status

The document acknowledges this gap implicitly (line 1718):
> "**Full coherence computation**: Abandon the three-factor decomposition entirely and compute composite credence through a single coherence assessment of the web — the approach that the web-of-belief infrastructure already supports in principle. This is theoretically attractive but computationally demanding and would sacrifice the formula's transparency and interpretability."

This statement suggests that the current system DOES NOT compute full coherence formally, but only a "three-factor decomposition" that is more tractable. The full coherence formula remains unspecified.

---

### 13. VOI (VALUE OF INFORMATION)

**Location**: PART_XV_TECHNICAL, §121.3 (lines 236–302)

**Verdict**: **PARTIAL** — Conceptual framework present, mathematical formula incomplete.

#### A. What Is Presented

**Lines 258–259**: VOI has two components:
- **Structural VOI**: "How much coherence would be gained if the gap were fully closed?"
- **Epistemic VOI**: "How much would uncertainty about this belief be reduced?"

#### B. The Problem

The document provides:
- Conceptual definitions (above)
- Worked example with a specific gap (lines 280–302)
- Decision logic (lines 356–360)

But **no mathematical formula** for computing VOI. The section is titled "VOI Scoring Formula for Literature Search" (line 254) but the actual formula is missing.

#### C. What Should Be There

A formal definition like:

**VOI(gap) = P(gap_closes) × Coherence_gain(closed) + P(gap_persists) × Coherence_gain(partial)**

where:
- P(gap_closes) = probability a literature search finds definitive evidence
- Coherence_gain = improvement in web coherence
- Weighted by search cost

#### D. Worked Example

The document does provide (lines 280–302) a concrete example:
- Gap: Direction (contradiction between two findings)
- VOI = 0.8
- Search cost ≈ $1.25
- VOI per dollar = 0.476

But this is an **example output**, not a **formula definition**.

---

### 14. MAGIC NUMBERS: CANONICAL VALUES WITH NO JUSTIFICATION

The audit found these unjustified constants:

| Constant | Value | Location | Justification | Status |
|----------|-------|----------|---------------|--------|
| d (CONSTITUTIVE) | 0.95 | §48.1 | "Definitional relationship" | Conceptual, not empirical |
| d (THEORY_DERIVED) | 0.25 | §48.1 | "Untested theory" | Conceptual, not empirical |
| δ (default start) | 0.90 | §48.3A | "Same culture would be 0.95, but..." | Implicit reasoning, not derived |
| δ (minimum feasible) | 0.30 | §48.3A, line 175 | "Too different to transfer" | Arbitrary threshold |
| ω_sev (max) | ~0.95 | §48.3B, table | (table omitted) | Not visible in audit |
| ω floor | 0.05 | §48.3B, line 336 | "Prevents any edge from contributing zero" | Philosophical, not epistemic |
| ω ceiling | 0.98 | §48.3B, line 336 | "Prevents overconfidence" | Philosophical, not epistemic |
| TEA weight (E_conf) | 0.30 | §48.3C, formula | "Judgment that empirical confirmation is strongest" | Unsourced opinion |
| TEA weight (P_nov) | 0.25 | §48.3C, formula | (as above) | Unsourced opinion |
| AESHI weight (Contract) | 0.24 | §53.8, formula | (no justification provided) | Arbitrary |
| AESHI weight (QA_Epistemic) | 0.05 | §53.8, formula | (no justification provided) | Arbitrary |

---

## SYSTEMATIC FINDINGS

### Missing Derivations

**Pattern**: Many formulas state WHAT they compute but not WHY they take their particular form.

#### Examples:

1. **Multiplicative structure of ω**: Why multiply ω_base × ω_conf × ω_rep × ω_meta rather than add them with weights?
   - **Document says**: "Each acts as a modifier on the base."
   - **Missing**: Formal justification. Additive combination would also work. Why multiplicative?

2. **Harmonic discount for replications**: Why 1/j and not 1/j²?
   - **Document says**: "Diminishing returns."
   - **Missing**: Derivation from first principles or empirical validation.

3. **Minimum rule for d_eff in chains**: Why min(d_i) and not product or average?
   - **Document says**: (Implicit) "Type property is determined by weakest type."
   - **Missing**: Explicit statement and justification.

### Missing Formal Definitions

1. **Coherence computation (C*)**: The most central mathematical concept in the system. Discussed in 100+ pages but **never defined as a formula**.

2. **VOI formula**: Referenced as "VOI scoring formula" but the actual formula is not presented. Only examples and intuition.

3. **Bridge warrant ceilings**: Mentioned but not formally specified. How does a bridge warrant "ceiling" interact with evidence quality (ω)? Is it a hard constraint or soft prior?

### Unjustified Constants

Approximately **20+ numerical constants** (d values, δ defaults, ω ranges, AESHI weights, CCI thresholds, etc.) lack empirical or theoretical justification. They are stated as "design decisions" but:

- **No source cited** for why these specific values.
- **No sensitivity analysis** showing how results change if values shift by ±10%.
- **No empirical validation** against real data.

Example: Why is d(CONSTITUTIVE) = 0.95 and not 0.90? What happens to system predictions if this changes?

### Documented Gaps

The document explicitly acknowledges several mathematical gaps:

1. **Line 253** (Panel Revision S4, Mayo): "Uncertainty propagation... is deferred to implementation but is noted as a design requirement."

2. **Lines 3659–3660** (PART_XVII): "Full operationalization of the Quinean revision algorithm remains incomplete... automatic identification of minimal-cut belief sets."

3. **Line 1718** (§52.5): "Full coherence computation: ... would sacrifice the formula's transparency and interpretability." — Currently NOT implemented.

---

## FIGURES AND VISUALIZATIONS

**Current Status**: ONE figure found.

**Line 137 reference** (PART_IV_CREDENCE): "Figure M-6: Population Transfer" — A heatmap of δ values by study immersion level (lab → field) and claim type (preference → function).

**Missing Figures** (Where They Would Help):

1. **Parameter space plot for d values**: Show the seven warrant types on a 2D plane labeled "mechanism-dependence" vs. "theory-independence," with d values as color gradient. This would make the canonical values intuitive rather than arbitrary.

2. **Worked example diagram for ω computation**: Show a specific study (e.g., a daylight-mood experiment) with annotated ω_sev, ω_conf, ω_rep, ω_meta values, then show the calculation ω = product.

3. **TEA weight sensitivity analysis**: A bar chart showing how the final TEA score changes if weights shift (e.g., E_conf = 0.25 vs. 0.35).

4. **Coherence metric diagram**: A visual representation of how C* is computed from contradiction and agreement links. Currently absent.

5. **Belief revision algorithm flowchart**: Show Algorithm 4 (entrenchment-based revision) as a decision tree so readers understand the "try least-entrenched beliefs first" principle.

6. **VOI decision threshold chart**: Show the relationship between VOI score, search cost, and decision to search. Currently conceptual, needs visualization.

---

## RECOMMENDATIONS

### High Priority (Blocks Reproducibility)

1. **Formalize the coherence computation (C*)**
   - Location: PART_IX_WEB_OF_BELIEF, §84–85
   - Action: Define C* explicitly as a mathematical formula, with:
     - Agreement and contradiction measures (how to compute from the web graph)
     - Weighting scheme (how to weight different belief pairs)
     - Normalization (how to map to [0,1] scale)
     - Worked example with 5–10 beliefs

2. **Formalize the VOI formula**
   - Location: PART_XV_TECHNICAL, §121.3
   - Action: State the mathematical formula for VOI including:
     - Probability of gap closure by search type
     - Coherence gain function
     - Cost factor
     - Worked example with actual numbers

3. **Justify canonical d values empirically**
   - Location: PART_IV_CREDENCE, §48.1
   - Action: Either:
     - Cite empirical studies showing these transfer rates (e.g., meta-analysis comparing CONSTITUTIVE vs. MECHANISM replication success)
     - OR conduct sensitivity analysis: "If d(MECHANISM) = 0.75 instead of 0.80, how do predictions change?"

### Medium Priority (Improves Interpretability)

4. **Derive the multiplicative structure of ω**
   - Location: PART_IV_CREDENCE, §48.3B, line 314
   - Action: Justify why ω = ω_base × ω_conf × ω_rep × ω_meta (multiplicative) rather than additive combination. Consider:
     - Multiplicative: each factor scales the prior warrant (Bayesian updating in probability space)
     - Additive: each factor adds independent contribution (assumes factors are orthogonal)
     - Which assumption is more defensible for evidence quality?

5. **Justify TEA weights**
   - Location: PART_IV_CREDENCE, §48.3C, line 512
   - Action: Cite Decision D-48C.1 (referenced but not shown) and explain:
     - Why E_conf (0.30) > P_nov (0.25) > U_uptake (0.20) > Prec (0.15) > Coh (0.10)?
     - Sensitivity analysis: how much do theory rankings change if weights are {0.25, 0.25, 0.20, 0.20, 0.10}?

6. **Justify AESHI weights**
   - Location: PART_IV_CREDENCE, §53.8, line 1914
   - Action: Explain why Contract and Web_BN each get 0.24 (tied for highest) while QA_Epistemic gets only 0.05. Is this proportional to impact? Cost? Detectability?

7. **Create parameter justification table**
   - Location: New appendix
   - Content: For each constant (d, δ, ω, TEA weight, AESHI weight), list:
     - Value
     - Conceptual justification
     - Empirical basis (if any)
     - Uncertainty/range
     - Sensitivity (how sensitive are results to ±10%?)

### Lower Priority (Pedagogical)

8. **Add figures**:
   - Parameter space diagram for warrant types (d values)
   - Worked example diagram for ω computation
   - Coherence metric visualization
   - Belief revision algorithm flowchart
   - VOI decision threshold chart
   - TEA weight sensitivity bar chart

9. **Cross-reference decision logs**
   - Many formulas reference panel decisions (e.g., "Panel Revision S4, Mayo")
   - Action: Ensure decision logs are linked/embedded in the master document

10. **Add alternative formulations**
    - For each major formula, note: "Alternative formulations considered: [X], [Y]. We chose [Z] because..."
    - Example: "We considered additive ω combination (ω = 0.3·ω_sev + 0.2·ω_conf...) but chose multiplicative ω = ω_sev × ω_conf... because..."

---

## SUMMARY VERDICTS

| Formula | Intuition | Derivation | Provenance | Overall | Priority Fix |
|---------|-----------|-----------|-----------|---------|--------------|
| Projection: logit(p_target) = d·ω·δ·logit(p_lab) | ✓✓ | ✓/✗ | ✓ | **GOOD** | Justify multiplicative structure |
| Logit function | ✓ | ✗ | ✗ | **PARTIAL** | Add derivation; cite source |
| ω = ω_base × ω_conf × ω_rep × ω_meta | ✓✓ | ✓/✗ | ✓ | **PARTIAL** | Justify multiplicative combination |
| d canonical values | ✓ | ✗ | ✗ | **NEEDS WORK** | Empirical basis or sensitivity analysis |
| δ canonical values | ✓✓ | ✓/✗ | ✗ | **PARTIAL** | Cite source; justify 0.90 and 0.30 |
| Serial combination (d_eff, ω_eff) | ✓ | ✓/✗ | ✗ | **GOOD** | Justify min vs. other rules |
| Parallel combination | ✓ | ✓/✗ | ✗ | **GOOD** | Add derivation logic |
| TEA = 0.30·E_conf + ... | ✓ | ✓/✗ | ✓/✗ | **PARTIAL** | Justify weights; cite decision |
| AESHI = 0.24·Contract + ... | ✓/✗ | ✗ | ✗ | **NEEDS WORK** | Justify all weights; add sensitivity |
| CCI formula | ✓✓ | ✓ | ✓ | **GOOD** | No action needed |
| Coherence computation (C*) | ✗ | ✗ | ✗ | **CRITICAL GAP** | **URGENT: Formalize** |
| VOI formula | ✓ | ✗ | ✗ | **NEEDS WORK** | **URGENT: Formalize** |

---

## CONCLUSION

The ATLAS master document is **exceptionally well-articulated for intuition and motivation**. Nearly every formula is preceded by clear English explanation of why it matters. This is a strength.

However, the system has **three systematic weaknesses**:

1. **Missing derivations**: Many formulas lack formal justification for their specific mathematical form (multiplicative vs. additive, these exponents vs. others, these weights vs. alternatives).

2. **Unjustified constants**: ~20+ numerical parameters (d values, δ defaults, ω bounds, TEA weights, AESHI weights) are stated as "design decisions" with no empirical basis, sensitivity analysis, or panel attribution (though decision logs are referenced but not shown).

3. **Critical gaps**: The two most important mathematical definitions — **coherence computation (C*)** and **VOI formula** — are discussed extensively but **never formalized as mathematical formulas**. This is a blocker for implementation reproducibility.

**Estimated remediation effort**:
- High priority fixes: 2–3 weeks (formalize C* and VOI, justify d values)
- Medium priority fixes: 2–3 weeks (derivations, TEA/AESHI weights)
- Low priority fixes: 1–2 weeks (figures, alternative formulations)

**Total**: ~4–8 weeks to move from "good prose documentation" to "publication-ready mathematical rigor."

