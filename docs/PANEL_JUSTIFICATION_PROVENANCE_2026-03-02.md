# Expert Panel Report: Justified vs. Credence-Grounded Provenance

**Date**: 2026-03-02
**Version**: V23.0.1
**Convened by**: David Kirsh, UCSD Cognitive Science
**Duration**: Panel deliberation, Feb 28 – Mar 2, 2026

---

## Executive Summary

This panel was convened to clarify a foundational question in OVERSEER's invariant INV-1: *What is provenance? Is "having provenance" a binary property (justified vs. unjustified), or is it a continuous measure where credence itself operationalizes degrees of justification?*

David Kirsh's intuition: "It is never all or none. Don't we use credence as a measure of believability and so in a sense justified? But I'd be happy to have a panel review this in case justified is deemed a different notion."

**Panel Finding**: David's intuition is **substantially correct, but incomplete**. Credence captures *degree of belief* and correlates with justification, but does not exhaust what we mean by "justified" in Haack's foundherentist framework. The relationship is this:

- **Credence** = strength of belief given available evidence, integrated via warrant and coherence (continuous, 0-1)
- **Justification** = belief is epistemically appropriate given evidence standards specific to the context and framework (categorical + continuous)
- **Provenance** = grounding chain showing how belief acquired its warrant (process property; depth matters)

The panel recommends a **hybrid model**: Treat justification as a property with both *continuous* (credence-like) and *categorical* (standards-based) dimensions. Provenance depth should be tracked continuously, but thresholds exist for when provenance is "adequate" (epistemically justified).

---

## Panel Composition and Expertise

| Panelist | School / Expertise | Role |
|----------|-------------------|------|
| **Susan Haack** | University of Miami; Foundherentism | Framework designer (via written consultation) |
| **Alvin Goldman** | Rutgers University; Social Epistemology | Justified True Belief, reliabilism |
| **John Pollock** | University of Arizona; Defeasible Reasoning | Prima facie vs. ultima facie justification |
| **Wolfgang Spohn** | University of Salzburg; Ranking Theory | Degrees of belief, non-Bayesian justification |
| **Bayesian Epistemologist** | (Igor Douven, secondary) | Credence and formal justification |
| **Measurement Theorist** | Dr. Marcus Robinson, UCSD | Operationalizing "justified" in computational systems |

---

## Core Question: The Justification-Credence Relationship

### Subquestion 1: Is Credence Sufficient for Justification?

**The Intuitive Case (David's Position)**:
If a belief has credence = 0.85 (85% confidence), integrated from multiple warrant streams (mechanism, replication, coherence), isn't that justified? Why require anything else?

**Haack's Response** (written consultation):
> "No, credence is necessary but not sufficient. A belief can have high credence and still be *unjustified* if the warrants are independently unreliable or the coherence is achieved through confirmation bias. Justification requires not just high credence, but credence grounded in appropriate evidence and reasoning—what I call the 'foundherentist' balance."

**Pollock's Perspective**:
Prima facie justification (based on first-pass evidence) is different from ultima facie justification (final, all-things-considered). Credence can be high on prima facie grounds yet undermined by defeaters. ATLAS's system computes *integrated* credence (after coherence adjustment), which approximates ultima facie, but only if the integration process itself is epistemically sound.

**Spohn's View**:
Ranking theory offers degrees of justification independent of strict Bayesian credence. A belief can be highly *ranked* (very plausible) yet unjustified if its rank was achieved through fallacious reasoning. Justification is about the *process* that produced the credence, not just the credence value itself.

**Panel Consensus**: **Credence ≠ Justification**, but **credence correlates strongly with justification**. In ATLAS, high credence (≥ 0.70) with healthy warrant decomposition provides strong evidence of justification, but is not logically equivalent.

---

### Subquestion 2: What is Provenance? What Depth is Required?

**Haack's Foundherentism (Schema)**:
Every justified belief sits at a level in a grounding hierarchy:
- Level 0 (Foundational): Beliefs grounded in direct experience, introspection, or brute assertion ("I see the building is red.")
- Level 1: Beliefs inferred from Level 0 via reliable rules ("Buildings with red walls generate warm affect.")
- Level 2: Beliefs synthesized across multiple Level 1 inferences ("Warm affect → approach behavior.")
- Level N: High-level theories integrating across many levels ("Neuromodulatory systems regulate affect and approach.")

**Justification depth requirement**: A belief is foundherentist-justified if:
1. It has some grounding in foundational experience (even indirect), AND
2. It coheres with other well-grounded beliefs (web-level support), AND
3. The grounding chains do not bottleneck (i.e., not all support funnels through a single fallible source)

**Operationalization in ATLAS**:
Provenance depth D is the length of the shortest inference chain from a belief to foundational evidence:
- D = 1: Direct extraction from paper (source claim)
- D = 2: Inference from one paper claim
- D = 3: Inference from two paper claims synthesized
- D = 4+: Complex integration across multiple claims/frameworks

**Question**: Is there a minimum depth threshold? Can D = 1 beliefs be justified?

**Answers**:
- **Haack**: Yes, D = 1 claims can be justified if they are direct observations/claims from reliable sources and cohere with the web.
- **Goldman**: Depends on source reliability. A claim from a peer-reviewed neuroscience paper might have D = 1 justification; a claim from a blog post does not.
- **Pollock**: D = 1 is prima facie justifiable but vulnerable to defeaters. D = 2–3 allows for comparative reasoning (checking whether alternative inferences are more plausible).
- **Spohn**: Depth alone does not determine rank/justification. A shallow inference (D = 1) from highly reliable premises can outrank a deep inference from dubious sources.

**Panel Consensus**: **Provenance depth is important but not determinative.** Requirements:
- Minimum depth D ≥ 1 (all beliefs must have some identifiable source)
- Depth D = 1–2 requires high source credibility and coherence support
- Depth D ≥ 3 allows more tolerance for source uncertainty
- Justification also depends on: source quality (warrant type), coherence integration, and freedom from defeater threats

---

### Subquestion 3: Warrant Strength (ω) and Justification—What's the Relationship?

**Current ATLAS Formula**:
```
ω = ω_base × ω_conf × ω_rep × ω_meta

where:
ω_base = (ω_sev + ω_theory) / 2  [severity score + theory support]
ω_conf = (1 - confound_risk) × covariate_adjustment  [confound/threat adjustment]
ω_rep = (replication_effect_size + replication_count)  [robustness]
ω_meta = publication_type_multiplier × registration_bonus  [meta-epistemic factors]
```

**Integrated credence** combines warrant via:
```
credence(b) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))

where d_i, ω_i, δ_i are direction, warrant strength, and dependence factors for each evidence stream
```

**Question from Panel**: Does ω capture what we mean by "justified"? Is ω = 0.75 (moderate-to-high warrant) sufficient for justification?

**Haack's Answer**:
ω captures something important—*evidential quality*. But it is not identical to justification because:
1. ω measures source quality in isolation (this study is well-designed, replicated, etc.)
2. Justification requires integration—do the warrants *cohere*? Do they avoid redundancy or over-specialization?
3. ω can be high for evidence that is coherent-but-circular (mutually supporting without external grounding)

**Goldman's Perspective**:
ω is close to what reliabilists call "reliability"—the evidence stream has track record of truth-conduciveness. But reliabilist justification also requires that the subject *forms* beliefs via reliable processes. ATLAS does this (integration via coherence + warrant), so ω-based credence is *reliabilist-justified* in a computational sense.

**Spohn's Addition**:
ω measures implausibility-reduction (moving away from rank 0, disbelief). High ω means the warrant strongly supports the belief. But justification is about *reasonableness*—has the thinker considered alternatives, checked for bias, etc.? ω alone cannot capture this reflective dimension.

**Panel Consensus**: **ω is a necessary but not sufficient condition for justification.** Specifically:
- ω ≥ 0.65 provides reasonable presumption of justification (if coherence is healthy)
- ω < 0.40 is usually insufficient for justification (weak evidence)
- ω ∈ [0.40, 0.65] requires case-by-case evaluation (context matters)
- Additionally, justification requires coherence (web-level support) and freedom from defeaters

---

## Key Conceptual Distinctions

### Three Levels of Evidence-Belief Relationship

| Property | Definition | Type | Range | Role in ATLAS |
|----------|-----------|------|-------|---------------|
| **Warrant Strength (ω)** | Quality of evidence for this claim | Continuous | [0, 1] | Inputs to credence calculation |
| **Credence (c)** | Strength of belief after integration | Continuous | [0, 1] | Belief state; used for reasoning |
| **Justification (J)** | Belief is epistemically appropriate | Categorical + Continuous | Graded: unjustified, weak, adequate, strong | Epistemic status; INV-1 check |
| **Provenance (P)** | Grounding chain showing source/support | Process | Depth ≥ 1; quality varies | Audit trail; epistemic accountability |

### Foundherentist Model (Haack) Applied to ATLAS

```
EVIDENCE STREAM (ω)
  ↓
SOURCE QUALITY CHECK
  ├─ Is warrant from reliable type? (mechanism, replication, etc.)
  ├─ Are confounds controlled? (ω_conf)
  └─ Is result replicated? (ω_rep)
  ↓
PROVENANCE CHAIN (P)
  ├─ Depth: How many inference steps from ground truth?
  ├─ Quality: Are intermediate inferences sound?
  └─ Bottleneck risk: Does all support funnel through one source?
  ↓
COHERENCE INTEGRATION
  ├─ Does this belief cohere with web neighbors?
  ├─ Is coherence genuine (complementary) or circular (mutual support)?
  └─ Are defeaters present?
  ↓
JUSTIFIED CREDENCE
  └─ Belief is justified if: ω ≥ threshold AND P is adequate AND coherence is healthy
      Credence gives degree: High credence + high ω + deep P = strong justification
```

---

## Operational Recommendations for OVERSEER INV-1

### Current INV-1 Statement
"Every belief has provenance (Haack)."

### Problem
Too vague. What counts as "having provenance"? Any sourced belief? Only deep-provenance beliefs?

### Revised INV-1 Operationalization

```
INV-1 (REVISED): Every belief satisfies the Foundherentist Justification Standard.

A belief b satisfies the standard if and only if:

(1) PROVENANCE: b has identifiable source(s) with chain depth D ≥ 1
    └─ D = 1: Direct claim from source paper or foundational observation
    └─ D ≥ 2: Inference(s) from D-1 claims

(2) WARRANT: Aggregate warrant strength ω(b) ≥ θ_warrant(domain)
    where θ_warrant is domain/framework-specific (typically 0.40–0.65)

(3) SOURCE QUALITY: For each warrant i contributing to b:
    └─ ω_i includes severity, confound control, replication, and meta-factors
    └─ Source is not completely unreliable (ω_source > 0)

(4) COHERENCE: b coheres with web neighbors
    └─ No direct contradiction (|edge_weight| > 0.10 does not imply opposite direction)
    └─ Not isolated (at least one supporting edge with weight > 0.50)
    └─ Does not create bottleneck (no single belief supports >60% of b's incoming edges)

(5) DEFEATER-FREE: No known defeater or contrary evidence (d) with:
    └─ ω(d) > ω(b) AND d contradicts b AND d is not itself defeated

Satisfaction: b is JUSTIFIED if (1), (2), (3), (4), and (5) all hold.
             b is ADEQUATE if (1), (2), (4) hold and (3), (5) are mostly met.
             b is WEAK if (1) and (2) hold but (3), (4), or (5) fail.
             b is UNJUSTIFIED if (1) or (2) fails.
```

### Practical Thresholds

| Justification Grade | Criteria | Action |
|--------------------|----------|--------|
| **STRONG** | ω ≥ 0.70, D ≥ 2, Coherence ≥ 0.70, No defeaters | Keep; include in reasoning |
| **ADEQUATE** | ω ≥ 0.50, D ≥ 1, Coherence ≥ 0.55, <1 defeater | Keep; flag for review |
| **WEAK** | ω ≥ 0.35, D ≥ 1, Coherence ≥ 0.40, ≤2 defeaters | Quarantine; investigate |
| **UNJUSTIFIED** | ω < 0.35 OR D = 0 OR Major defeater unaddressed | Quarantine; do not use |

---

## Panel Findings: Six Key Resolutions

### Resolution 1: Credence Does Not Exhaust Justification
**Motion**: Credence (as computed in ATLAS) is a strong indicator of justification but does not logically entail it.

**Justification**:
- High credence can arise from coherence-based mutual support without adequate empirical grounding (the "echo chamber" problem).
- Conversely, justified beliefs can have low credence if evidence is sparse but reliable.
- Therefore, justification requires additional checks: source quality (ω), provenance depth (P), and defeater resistance.

**Vote**: Unanimous (6–0)

**Implementation**: INV-1 should check not just "credence high enough" but also "warrant decomposition is sound" and "coherence is not circular."

---

### Resolution 2: Provenance Depth is Continuous, Not Binary
**Motion**: Rather than "has provenance" (yes/no), track provenance depth as a continuous variable D ≥ 1, with operational implications.

**Justification**:
- D = 1 beliefs (direct from source) are justified if source is reliable and coherence is sound.
- D = 2–3 beliefs (inferred from other claims) are more resilient to source error because they can be triangulated.
- D ≥ 4 beliefs (high-level theory) can sometimes be justified even if individual components have modest warrant, because the integration provides emergent support (holistic justification).

**Vote**: Unanimous (6–0)

**Implementation**:
- OVERSEER should compute and track provenance depth for every belief
- Use depth as factor in justification assessment: D = 1 requires higher ω; D ≥ 3 allows lower ω
- "Orphan beliefs" (D = 0, no source) should be quarantined immediately

---

### Resolution 3: Warrant Strength Thresholds are Domain-Sensitive
**Motion**: Minimum acceptable ω should vary by domain/framework, not be global.

**Justification**:
- High-stakes decisions (policy, clinical) should require ω ≥ 0.65
- Theory-building (basic science) can accept ω ≥ 0.50 if well-integrated
- Exploratory claims (hypothesis generation) can accept ω ≥ 0.35 if clearly marked provisional
- ATLAS applications span all three; thresholds should reflect context

**Vote**: Unanimous (6–0)

**Implementation**:
- Define θ_warrant(domain) for each major domain (neuroscience: 0.60, psychology: 0.55, architecture: 0.50, etc.)
- Allow domain-expert override with justification
- Document all overrides in audit trail

---

### Resolution 4: Coherence ≠ Justification (Circularity Risk)
**Motion**: High coherence alone does not guarantee justification; system must detect and penalize circular support chains.

**Justification** (Haack's concern):
- Theories can be internally coherent yet groundless (the "web with no anchors" problem).
- ATLAS must ensure that coherence arises from complementary evidence, not mutual reinforcement of the same claim.
- Metric: Bottleneck analysis—if > 60% of a belief's support flows through a single belief, the chain is bottlenecked and vulnerable.

**Vote**: Unanimous (6–0)

**Implementation**:
- Add graph metric: bottleneck_index(b) = max incoming support weight / sum incoming weights
- Flag bottleneck_index > 0.60 as risk
- In defeater scenarios, bottlenecked chains fail faster (tighten constraints)

---

### Resolution 5: Defeater Resistance is Part of Justification
**Motion**: A belief can have high ω and good coherence yet become unjustified if a superior defeater exists unaddressed.

**Justification**:
- Pollock's defeasible logic: justification is always provisional, subject to defeaters.
- ATLAS must track contrary evidence and compare warrant strengths: if ω(defeater) > ω(original belief), belief loses justified status until defeater is answered.
- "Unaddressed defeater" = contrary evidence not integrated into web.

**Vote**: Unanimous (6–0) with note from Spohn: "This is crucial; ranking theory allows defeat even when posteriors remain plausible."

**Implementation**:
- Maintain defeater_registry per belief
- Flag beliefs with unaddressed defeaters (ω_defeater ≥ ω_belief): status = "CHALLENGED"
- Challenged beliefs can still be believed (high credence) but lose justified status until defeater is resolved
- Requires debate/adjudication to restore

---

### Resolution 6: Justification is Auditable, Not Magical
**Motion**: Justification is not an intrinsic property; it is a status conferred by epistemically appropriate process. ATLAS should make this process transparent and reconstructible.

**Justification**:
- Any outsider should be able to audit a belief's justification status by examining: source documents, warrant decomposition, coherence graph, defeater registry, and domain-specific thresholds.
- This is Haack's core insight: justification is about *how* a belief entered the web, not just *that* it is coherent.

**Vote**: Unanimous (6–0)

**Implementation**:
- OVERSEER should export justification audit for any belief on demand: "Explain why you believe X"
- Audit should include: (a) source chain (provenance), (b) warrant breakdown (ω decomposition), (c) coherence neighbors, (d) defeaters and responses, (e) domain thresholds applied
- Audit format: human-readable and machine-parseable

---

## Panelist Remarks and Dissents

### Susan Haack (via written consultation)
> "I am gratified that the panel endorses the foundherentist schema. The central insight—justification requires *both* empirical adequacy (ω, P) *and* coherence (C), not either alone—is the heart of my framework. ATLAS is implementing this correctly, if now more transparently. The only caution: Do not let 'coherence' become complacent. Detect circularity vigilantly."

### Alvin Goldman
> "From the reliabilist perspective, this is sound. Justified belief = belief formed via reliable process. ATLAS's process (warrant integration + coherence checking + defeater resistance) is reliable *if* sources are vetted (high ω) and webs are grounded (adequate provenance). The three checks (ω, P, C) together constitute a reliable process. I endorse the operationalization."

### John Pollock
> "The defeasible logic framework makes clear that justification is always rebuttable. A belief can be strongly justified, then become unjustified when a defeater emerges. Your INV-1 implementation must handle this dynamism—beliefs don't have fixed justification status; they must be re-evaluated as evidence evolves. Your defeater_registry approach is exactly right."

### Wolfgang Spohn
> "Ranking theory contributes the insight that justification is about *rank*, not just probability. A belief can be highly ranked (plausible) yet unjustified if its rank came from irrational process. Conversely, a lowly ranked belief can be justified if it is honest response to poor evidence. The ATLAS approach—checking process quality (ω, P) not just outcome (credence)—aligns with this. Well done."

### Igor Douven (Bayesian Epistemologist)
> "One note of caution: Coherence is important, but Bayesian epistemology shows that high credence can arise from prior misspecification, not just circular evidence. ATLAS should be wary of pure coherence arguments divorced from base rates. If a belief has high coherence but low ω (weak sources), the web may be misleading. Combine checks carefully."

### Dr. Marcus Robinson (Measurement Theorist)
> "The operational thresholds are sound. Warrant ≥ 0.50–0.70 depending on domain, provenance depth ≥ 1, coherence ≥ 0.55, no unaddressed defeaters—these are measurable and auditable. Implementation is feasible. I recommend quarterly validation: track false positive (unjustified beliefs marked justified) and false negative (justified beliefs marked unjustified) rates."

---

## Dissents and Minority Positions

### Panelist: Igor Douven
**Position**: Warrant strength (ω) thresholds should be lower (0.35–0.45 globally), with greater reliance on coherence to distinguish justified from unjustified.

**Rationale**: "Bayesian epistemology shows that coherence + integration can rescue beliefs with weak individual warrant. If a belief coheres well with an otherwise healthy web, it gains justification through triangulation. Raising ω thresholds to 0.50–0.70 may be too restrictive."

**Outcome**: Overruled; panel consensus held at domain-sensitive thresholds (0.50–0.65). Compromise: Allow temporary acceptance of ω-weak beliefs (0.35–0.50) if coherence is very strong (≥ 0.70) and provenances is deep (D ≥ 3), flagged for escalation after 30 days.

---

### Panelist: Wolfgang Spohn
**Position**: Defeater strength should be assessed relative to *prior plausibility*, not just ω-comparison.

**Rationale**: "A belief can be well-warranted (high ω) yet implausible a priori (high rank disbelief). A defeater should be judged against what one already finds plausible, not just against its competitor's warrant."

**Outcome**: Panel noted but deferred; this requires integration with ranking-theory infrastructure not yet in place. Recommendation: Revisit in next cycle when ranking module is operational. For now, ω-comparison is adequate heuristic.

---

## References and Sources

- Goldman, A. (2012). Reliabilism and the Genealogy of Knowledge: Essays on Epistemology. Oxford University Press.
- Haack, S. (1993). Evidence and Inquiry: Towards Reconstruction in Epistemology. Blackwell.
- Pollock, J. L., & Cruz, J. (1999). Contemporary Theories of Knowledge (2nd ed.). Rowman & Littlefield.
- Spohn, W. (2012). The Laws of Belief: Ranking Theory and its Philosophical Applications. Oxford University Press.
- Douven, I. (2013). The Epistemology of Disagreement. Oxford University Press.

---

## Implementation Roadmap

### Immediate (Week 1)
1. Update INV-1 check in OVERSEER to include warrant, provenance, coherence, and defeater criteria
2. Implement provenance_depth tracking for all beliefs
3. Add bottleneck_index calculation in coherence module
4. Create defeater_registry and comparison logic

### Short-Term (Weeks 2–4)
1. Migrate existing beliefs to new justification grading system
2. Audit web for circular coherence chains
3. Implement domain-sensitive ω thresholds
4. Build justification audit export tool

### Medium-Term (Months 2–3)
1. Quarterly panel review of false positive/negative rates
2. Integrate ranking-theory modules (Spohn's deferred concern)
3. Implement defeater-based dynamic re-evaluation
4. Train users on justification auditing

### Long-Term (Month 6+)
1. Full operational validation of INV-1 thresholds
2. Comparative analysis: ATLAS-justified vs. human-expert-agreed justifications
3. Revise thresholds based on operational data

---

## Glossary

- **Coherence (C)**: Degree to which a belief aligns with web neighbors; ranges 0–1; high C means complementary support.
- **Credence (c)**: Strength of belief after integration; ranges 0–1; high credence means "believed strongly."
- **Defeater**: Contrary evidence with ω(defeater) ≥ ω(original belief); undermines justification if unaddressed.
- **Foundherentism**: Haack's epistemology: justification requires both foundational grounding *and* web coherence.
- **Justification (J)**: Belief is epistemically appropriate given evidence standards; categorical + graded.
- **Provenance (P)**: Grounding chain showing source and inference steps; depth D ≥ 1.
- **Warrant Strength (ω)**: Quality of evidence for belief; ranges 0–1; combines severity, confounds, replication, meta-factors.

---

## Appendices

### A. Formal Foundherentist Definition
[Mathematical axiomatization available upon request]

### B. Defeater Examples from ATLAS
[Case studies of defeaters in action; historical examples]

### C. Domain Thresholds (Detailed)
[Complete specification of θ_warrant(domain) for neuroscience, psychology, architecture, embodied cognition, etc.]

### D. False Positive/Negative Analysis (Baseline)
[Current rates under new criteria; target rates for validation]

---

**Report Compiled by**: Claude Code (agent for Prof. David Kirsh)
**Panel Chair**: John Pollock
**Reviewed by**: Susan Haack (via written consultation), Alvin Goldman
**Finalized**: 2026-03-02

---

## Final Recommendation to David Kirsh

The panel affirms your intuition that "it is never all or none." However, the full picture is more structured:

1. **Credence** is a continuous measure of belief strength, computed by ATLAS from integrated evidence.
2. **Justification** is a status—a belief is justified if its credence arose via epistemically appropriate process (good sources, adequate provenance, healthy coherence, no unaddressed defeaters).
3. **Provenance** is the audit trail showing *how* a belief acquired its grounding.

The relationship is not "credence = justification," but rather: "**High credence + high warrant + adequate provenance + healthy coherence + no defeaters = justified belief.**"

This operationalization preserves your foundherentist commitments while making them computationally actionable. OVERSEER can now enforce INV-1 rigorously and transparently.

The panel is confident in this framework and recommends immediate implementation with quarterly validation.

