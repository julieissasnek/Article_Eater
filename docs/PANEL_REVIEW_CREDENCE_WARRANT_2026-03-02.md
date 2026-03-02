# Panel Review: Credence-Warrant Integration and Theory Entrenchment Assessment

**Date**: 2026-03-02
**Convened by**: CW, at direction of David Kirsh
**Sprint**: CREDENCE-WARRANT
**Documents under review**: §48.3B (Warrant Strength Assignment), §48.3C (Theory Entrenchment Assessment), EXPERT_PANEL_MECHANISM_VS_EVIDENCE_2026-03-01.md

---

## The Panel

**Deborah Mayo** — Virginia Tech. Severity principle, error statistics. [~8,200 citations]
**Nancy Cartwright** — Durham/UCSD. Capacities, external validity, evidence hierarchies. [~22,000 citations]
**Jim Woodward** — Pittsburgh (emeritus). Interventionist causation, invariance. [~18,000 citations]
**Paul Thagard** — Waterloo (emeritus). Explanatory coherence (ECHO), computational epistemology. [~14,000 citations]
**Jacob Stegenga** — Cambridge. Medical nihilism, evidence amalgamation. [~2,500 citations]
**Phyllis Illari** — UCL. Evidential pluralism, mechanistic evidence. [~1,800 citations]

---

## Three Questions for the Panel

### Question 1: Is the ω Composite Formula Correct?

**The proposal (§48.3B)**: Warrant strength ω is computed from five components:

```
ω = ω_base × ω_conf × ω_rep × ω_meta
```

where ω_base differs by edge type:
- Non-mechanism edges: ω_base = ω_sev (experimental severity alone)
- Mechanism edges: ω_base = ω_sev + ω_theory × (1 − ω_sev) (severity + diminishing-returns theory boost)

And ω_theory = T_ent × mechanism_specificity.

**Mayo**: The formula separates severity (ω_sev) from confound risk (ω_conf) as distinct multiplicative factors. I endorse this. These are logically independent: a study can be well-powered (high severity) but poorly controlled (high confound risk), or vice versa. Making them multiplicative means both must be adequate — you cannot compensate for poor control with large sample size. That is correct.

However, I have a concern about the severity scoring table. The table assigns ω_sev ranges by study *design type* (RCT, quasi-experimental, correlational). This is a category error that mirrors the evidence-hierarchy mistake. Severity depends on *how well a specific study controls error*, not on its design label. A well-executed quasi-experiment with careful matching can be more severe than a poorly executed RCT with high dropout. The table should be a starting-point heuristic, not a deterministic assignment. **Recommendation**: Add a note that the design-type ranges are defaults that should be adjusted based on the specific study's error-control characteristics. An RCT with 40% dropout and no intention-to-treat analysis might drop to ω_sev = 0.50 despite being nominally an RCT.

**Woodward**: The formula correctly treats the discount factor d(τ) and warrant strength ω as orthogonal. d is a property of the warrant *type*; ω is a property of the warrant *instance*. A weak study can have MECHANISM warrant (d = 0.80) but low ω. This independence is important and the formalization preserves it.

I want to comment on the confound risk term. The proposal says ω_conf captures "ease of imagining confounders." I would restate this in interventionist terms: ω_conf captures the degree to which the exclusion restriction is satisfied — whether there exist plausible alternative pathways from the intervention to the outcome that bypass the proposed cause. "Ease of imagining" is a psychological description; "alternative causal pathways not blocked by the study design" is the structural condition. The formula is correct; the interpretation should be sharpened. **Recommendation**: Restate confound risk in interventionist terms in the master doc text, keeping "confound-imaginability" as the informal gloss.

**Thagard**: I have a structural concern. The formula treats the five components as independent factors combined multiplicatively. But in practice, they are not independent. Replication (ω_rep) is correlated with community uptake. Meta-calibration (ω_meta) partially overlaps with confound risk. The formula may undercount evidence when components are positively correlated and overcount when they are negatively correlated.

However, I recognize that modeling the full dependency structure would require a joint probability model that is impractical to calibrate. The multiplicative independence assumption is a reasonable approximation for an operational system. **Recommendation**: Accept the formula but add a note acknowledging the independence assumption and its limitations. In future versions, a Bayesian network model of the ω components could replace the multiplicative formula.

**Stegenga**: The meta-calibration term (ω_meta) is the most important contribution and the one most likely to be challenged by reviewers. The claim that entire *fields* can be discounted based on their replication track record is controversial. Psychologists will object that it penalizes their field unfairly; physicists might argue it doesn't penalize soft sciences enough. The key defense is that this is not a permanent judgment — it is a prior that updates as the field's practices improve. The formula should make this explicit.

I also note that including citation count and author track record, even with low weight, will draw fire. I would recommend dropping these from the formal formula and relegating them to an optional "soft evidence" annotation that does not enter the computation. The rest of the formula stands on strong philosophical grounds; these social indicators do not and will provide easy targets for critics. **Recommendation**: Remove citation count and author track record from ω_meta. Keep domain reliability and malleability discount as the core meta-calibration. Note social indicators as available context but not formal inputs.

**Illari**: The theory support channel (ω_theory entering through mechanism edges) is well-designed. It correctly implements the evidential pluralism principle: mechanistic evidence is a compound of direct mechanism observation plus theoretical backing. The diminishing-returns formula — ω_base = ω_sev + ω_theory × (1 − ω_sev) — correctly captures the intuition that theory has the largest effect when direct evidence is weakest.

One concern: the formula allows theory support to *increase* ω_base beyond ω_sev even when the mechanism has never been directly tested. If ω_sev = 0.05 (untested mechanism) and ω_theory = 0.90 (parent theory is circadian neuroscience), then ω_base = 0.05 + 0.90 × 0.95 = 0.905. This seems too generous — it implies that a well-confirmed theory can substitute almost entirely for direct mechanism testing. The diminishing returns work in the right direction but the ceiling is too high for untested mechanisms. **Recommendation**: Add a floor constraint: ω_base for mechanism edges should not exceed 2 × ω_sev when ω_sev < 0.20. This prevents theory from doing all the work when direct evidence is essentially absent.

**Cartwright**: I agree with Illari's concern. A theory predicts a mechanism; the mechanism has never been tested in this specific context. The theory may be well-confirmed in general, but whether it applies *here* is exactly the external validity question. Theory entrenchment tells us the mechanism *could* operate in principle; it does not tell us it *does* operate in this specific causal context. The floor constraint Illari proposes is reasonable.

More broadly, I want to flag that the entire ω formula assumes that warrant strength is a single scalar. In reality, the strength of evidence is purpose-relative: evidence that is strong for establishing existence of an effect (severe test) may be weak for predicting the effect in a new context (external validity) or for intervening on it (mechanism). The scalar ω collapses these purposes. For the current system, where ω feeds into a projection formula (which is explicitly about transfer to new contexts), this collapsing is acceptable because the projection formula handles context-transfer separately through δ. But future versions might benefit from purpose-indexed warrant strength. **Recommendation**: Accept the scalar ω for now; add a note about purpose-relative strength as a future refinement.

#### Panel Vote on Question 1

| Panelist | Vote | Conditions |
|---|---|---|
| Mayo | APPROVE WITH REVISION | Add note that design-type ω_sev ranges are defaults, not deterministic |
| Woodward | APPROVE WITH REVISION | Restate confound risk in interventionist terms |
| Thagard | APPROVE WITH NOTE | Acknowledge independence assumption |
| Stegenga | APPROVE WITH REVISION | Remove citation count / author track record from ω_meta |
| Illari | APPROVE WITH REVISION | Add floor constraint: ω_base ≤ 2 × ω_sev when ω_sev < 0.20 |
| Cartwright | APPROVE WITH NOTE | Accept scalar ω; note purpose-relativity as future refinement |

**Result: APPROVED with four revisions.** All four revisions are non-breaking (they modify edge cases and annotations, not the core formula structure).

---

### Question 2: Is the TEA Procedure Correct?

**The proposal (§48.3C)**: Theory entrenchment is computed from five dimensions:

T_ent = 0.30 × ECB + 0.25 × PN + 0.20 × TP + 0.15 × CUC + 0.10 × CAS

where ECB = empirical confirmation breadth, PN = predictive novelty, TP = theoretical precision, CUC = community uptake and contestation, CAS = coherence with adjacent science.

**Thagard**: I have the most to say here because I have spent three decades building computational models of exactly this problem (ECHO, 1989; HOT coherence, 2000).

The TEA procedure is a reasonable operationalization, but I want to flag two issues. First, the dimensions are not cleanly independent. ECB and CAS overlap: a theory that coheres with adjacent science is more likely to have been tested using methods from those adjacent fields. PN and TP overlap: precise theories are more likely to generate genuinely novel predictions because they make specific enough claims to be surprised by. The weighted sum treats them as independent, which inflates the composite for theories that score uniformly high and deflates it for theories with compensating strengths and weaknesses.

Second, my ECHO model would handle this differently. In ECHO, theory evaluation is a constraint-satisfaction problem: propositions (including theoretical claims and data) are connected by explanatory and contradictory relations, and activation spreads through the network until a stable state is reached. The activation of a theory is not a weighted sum of independent dimensions but an emergent property of the theory's place in the explanatory network. I recognize that implementing ECHO for every theory in the ATLAS system is impractical, but the weighted-sum approach should be understood as an approximation of what a full coherence computation would yield.

That said, the dimensions chosen are defensible and the worked examples produce plausible orderings. Circadian > PP > ART > SRT > biophilia is a ranking most philosophers of science would accept. **Recommendation**: Accept the procedure. Add a note that it approximates a full explanatory coherence computation. Future versions could use ECHO-style constraint satisfaction.

**Mayo**: I am supportive of the high weight on ECB (0.30) and PN (0.25). These are the strongest indicators of a theory's track record. I would go further: PN should be weighted higher than ECB. A theory that has been confirmed many times but only by testing its motivating observations is not as impressive as one that has generated genuinely surprising predictions. The current weights (ECB 0.30 > PN 0.25) slightly favor breadth over novelty. I would prefer PN 0.30, ECB 0.25. But this is a matter of degree, not principle. The current weights are acceptable.

The TP dimension (precision, weight 0.20) is correctly motivated by Meehl (1978). Vague theories that can accommodate any result are effectively unfalsifiable. Rewarding precision is essential. I endorse this.

I am less comfortable with CUC (community uptake, 0.15). Popularity is not evidence. A theory can be widely accepted and wrong, or widely ignored and correct. The argument that community uptake serves as a proxy for adversarial scrutiny (Longino) is valid but weak — it assumes the community actually engages critically, which is not always the case (groupthink, paradigm entrenchment). I would reduce CUC to 0.10 and redistribute the weight to PN. **Recommendation**: Consider PN 0.30, CUC 0.10, redistributing 0.05 from CUC to PN.

**Cartwright**: The procedure makes a philosophically important distinction that should be highlighted: it distinguishes between a theory's general confirmedness (TEA) and the specificity with which the theory predicts a particular mechanism (the "specificity" term in ω_theory = T_ent × specificity). This is exactly right. A theory can be well-confirmed in general but say nothing specific about the case at hand. The TEA score should not be conflated with the mechanism-specific relevance.

I want to add one dimension that is missing: **scope-limitation awareness**. A good theory knows its own boundaries — it specifies where it applies and where it doesn't. Circadian theory is clear: it applies to organisms with SCN-like structures, to visible light wavelengths, to entrainment timescales. Biophilia is vague about its scope: does it apply to all humans? Only those raised in environments with nature exposure? Only to visual stimuli? A theory that explicitly acknowledges its scope limitations is more trustworthy than one that claims universality by default.

However, scope awareness could be captured within TP (theoretical precision) rather than as a sixth dimension. A theory that specifies its boundary conditions is more precise than one that doesn't. **Recommendation**: Add scope-limitation awareness to the TP scoring rubric rather than as a separate dimension.

**Stegenga**: The procedure is sound. I particularly endorse the reproducibility requirements: anchor examples, cited justifications, panel review for contested theories, version-tracked updates. These are exactly the safeguards needed to prevent TEA scores from degenerating into arbitrary numbers.

One addition: the procedure should specify how to handle **theory revisions and splits**. Attention Restoration Theory as proposed by Kaplan (1995) is different from the version refined by Hartig et al. (2014). Predictive processing as proposed by Friston (2010) is different from the embodied/enactive versions (Bruineberg et al., 2018). Which version gets the TEA score? **Recommendation**: TEA scores should be indexed to specific formulations with citations. When a theory has diverged into significantly different versions, each version gets its own TEA score.

**Illari**: The procedure correctly handles the relationship between theories, mechanisms, and molecules (the inheritance structure at the end of §48.3C). Mechanisms inherit standing from their parent theory's TEA plus their own direct evidence; molecules aggregate their constituent beliefs' credences. This is clean and avoids double-counting.

**Woodward**: The five dimensions map reasonably well onto the structural features I consider most important for causal theories: invariance (captured by ECB and PN — a theory that generates confirmed novel predictions has demonstrated invariance across test conditions), precision (TP), and modularity (not explicitly captured but partially reflected in CAS — a theory that coheres with adjacent science likely has modular components that can be tested independently).

I endorse the procedure. No revisions needed.

#### Panel Vote on Question 2

| Panelist | Vote | Conditions |
|---|---|---|
| Thagard | APPROVE WITH NOTE | Acknowledge approximation of full coherence computation |
| Mayo | APPROVE WITH SUGGESTION | Consider increasing PN weight at expense of CUC |
| Cartwright | APPROVE WITH REVISION | Add scope-limitation awareness to TP rubric |
| Stegenga | APPROVE WITH REVISION | Index TEA scores to specific theory formulations |
| Illari | APPROVE | No changes |
| Woodward | APPROVE | No changes |

**Result: APPROVED with two revisions and one suggestion.** The suggestion (PN weight adjustment) is a preference, not a structural issue, and can be deferred to the next review cycle.

---

### Question 3: Should Credence Be Derived from Warrant Structure?

**The proposal (§48.3B)**: A belief's credence should be computed as:

credence(belief) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))

This is the existing parallel-combination projection formula (§48.5) applied reflexively. Credence IS the projected probability when all evidence lines are combined. The separate `compute_credence_from_statistics()` function should be treated as a provisional estimate superseded once full warrant structure is assembled.

**Thagard**: This is the most consequential proposal. It unifies the credence system and the warrant system, which I support in principle — coherentist epistemology (Quine, BonJour, my own ECHO work) requires that the standing of a belief be determined by its place in the network, not by an independent computation.

However, I have a concern about bootstrapping. When a belief first enters the system (from extraction), it has no warrant structure yet. The provisional credence from `compute_credence_from_statistics()` is needed as a starting point. The proposal says this is "explicitly superseded" once the warrant structure is assembled. But in practice, the warrant structure itself depends on other beliefs' credences (theory entrenchment depends on the credences of the theory's constituent beliefs, which depend on their warrant structures, which depend on...). This is a circularity that coherentist systems must handle.

The standard approach is iterative stabilization: start with provisional credences, compute warrant structures, re-derive credences from warrants, repeat until convergence. The system already has this pattern in reflective equilibrium (seek_equilibrium). The proposal should explicitly state that the warrant-derived credence is computed iteratively, starting from provisional values. **Recommendation**: Add explicit discussion of iterative convergence from provisional credences.

**Mayo**: I am ambivalent. The formula correctly combines evidence lines using the projection calculus. But credence, in my framework, is not a probability to be computed from a formula — it is the *result of assessing whether claims have survived severe tests*. The formula captures study quality (through ω_sev) and evidence combination (through parallel log-odds), which are necessary components of severity assessment. So the formula is not wrong; it's an approximation of what a full severity assessment would yield.

My concern is that the formula makes credence look more precise than it is. A number like "credence = 0.617" implies three significant digits of epistemic precision that we do not have. The uncertainty field on the Credence class is supposed to capture this, but if credence is now derived from the warrant formula, the uncertainty should also be derived (from the uncertainties in ω, d, δ, and p_lab). **Recommendation**: Propagate uncertainty through the formula. Do not report credence to more than two significant digits.

**Cartwright**: I support the unification. The separate credence computation was a source of inconsistency — a belief could have high credence but fragile warrants. Making credence depend on warrants forces the system to be internally coherent.

But I want to flag a practical issue. The current system has ~3,000+ beliefs. Many have credence values but minimal warrant structure (they have a p-value and an extraction confidence, but no typed warrant edges). The transition from the old system to the new one will produce a discontinuity: beliefs that currently have credence 0.70 (from strong p-values) might drop to 0.50 (because they lack typed warrant edges). This transition needs to be managed carefully. **Recommendation**: Implement a transition period where both old and new credence are computed and compared. Flag large discrepancies for manual review.

**Illari**: Endorsed. The unification correctly implements the principle that epistemic standing should reflect the *structure* of evidence, not just its quantity.

**Woodward**: Endorsed. The formula is the projection calculus applied reflexively, which is mathematically elegant and epistemically sound.

**Stegenga**: Endorsed with one note: the formula makes an implicit assumption that all evidence lines are independent. When two studies share the same methodology, population, or research group, their contributions should not be simply additive in log-odds space. The parallel combination formula (§48.5) should include a correction for correlated evidence. This is not a new issue — it affects the existing projection calculus equally — but it becomes more visible when credence is computed this way. **Recommendation**: Add a note about the independence assumption. In future, implement a correlation discount for non-independent evidence lines.

#### Panel Vote on Question 3

| Panelist | Vote | Conditions |
|---|---|---|
| Thagard | APPROVE WITH REVISION | Add iterative convergence from provisional credences |
| Mayo | APPROVE WITH REVISION | Propagate uncertainty; limit significant digits |
| Cartwright | APPROVE WITH REVISION | Implement transition period with dual credence comparison |
| Illari | APPROVE | No changes |
| Woodward | APPROVE | No changes |
| Stegenga | APPROVE WITH NOTE | Acknowledge independence assumption for correlated evidence |

**Result: APPROVED with three revisions.** The Thagard and Mayo revisions affect implementation; the Cartwright revision affects rollout strategy.

---

## Summary of All Panel Revisions

### Must-Do (before implementation)

| ID | Revision | Source | Affects |
|---|---|---|---|
| R1 | Floor constraint on theory boost: ω_base ≤ 2 × ω_sev when ω_sev < 0.20 | Illari + Cartwright | §48.3B formula |
| R2 | Remove citation count and author track record from ω_meta formal computation | Stegenga | §48.3B meta-calibration |
| R3 | Add scope-limitation awareness to TP scoring rubric | Cartwright | §48.3C TEA dimension 3 |
| R4 | Index TEA scores to specific theory formulations with citations | Stegenga | §48.3C procedure |
| R5 | Add iterative convergence discussion (provisional → warrant-derived credence) | Thagard | §48.3B architecture |
| R6 | Implement transition period with dual credence (old vs. new) comparison | Cartwright | Implementation plan |

### Should-Do (quality improvements, can be deferred)

| ID | Revision | Source | Affects |
|---|---|---|---|
| S1 | Restate confound risk in interventionist terms | Woodward | §48.3B text |
| S2 | Add note that design-type ω_sev ranges are defaults, adjustable per study | Mayo | §48.3B table |
| S3 | Acknowledge independence assumption in ω formula | Thagard | §48.3B text |
| S4 | Propagate uncertainty through the formula; limit significant digits | Mayo | Implementation |
| S5 | Note purpose-relative warrant strength as future refinement | Cartwright | §48.3B text |
| S6 | Note TEA approximates full explanatory coherence computation | Thagard | §48.3C text |
| S7 | Consider increasing PN weight at expense of CUC | Mayo | §48.3C weights |
| S8 | Acknowledge correlated evidence in parallel combination | Stegenga | §48.5 text |

---

## Sprint Plan (Revised Post-Panel)

| Phase | What | Effort | Status |
|---|---|---|---|
| 1. Panel Review | ✅ DONE — 6 Must-Do revisions, 8 Should-Do notes | 1 hr | **COMPLETE** |
| 2A. Apply R1–R6 to master doc | Update §48.3B and §48.3C with panel revisions | 30 min | **NEXT** |
| 2B. Apply S1–S6 to master doc | Annotation updates (non-structural) | 20 min | Can parallel with 2A |
| 3. TEA Scoring | Apply TEA to remaining ~9 T1.5 theories + store in data/theories/ | 1 hr | After 2A |
| 4. Implementation | Compute ω from extraction metadata; replace credence function; add TEA lookup; implement R5 (iterative convergence) and R6 (dual credence transition) | 3–4 hrs | After 3 |
| 5. Validation | Run revised credence on 50 pilot beliefs; compare old vs. new; flag discrepancies per R6 | 1 hr | After 4 |
| 6. Doc Finalization | Update worked examples (§48.7–48.11); sprint completion report | 30 min | After 5 |

Total: ~7–8 hours across 2–3 sessions.
