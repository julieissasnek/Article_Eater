# CMR ARCHITECTURE EXPLANATION
## A Complete Account of the Compositional Mechanistic Reasoning System
## Living Document — Started February 22, 2026
## Status: DRAFT — CC verification pass in progress

---

# HOW TO USE THIS DOCUMENT

**This document is being verified and expanded by CC against the actual project files
as specified in CC_PROMPT_CMR_EXPLANATION.md. Sections are marked as follows:**

- `[DRAFT — VERIFIED]` = Content has been checked by CC against source files
- `[TODO]` = No content yet; CC must write from source files
- `[COMPLETE]` = Verified and finalized

**See CC_PROMPT_CMR_EXPLANATION.md for the full list of source files CC must read
and the verification protocol CC must follow.**

---

# TABLE OF CONTENTS

1. Introduction: The Problem CMR Solves
2. The Core Credence Formula
   2.1 P(parent theory)
   2.2 P(bridge)
   2.3 P(CNFA-specific)
   2.4 The Multiplicative Structure and Its Justification
   2.5 Quinean Webs and Bayesian Networks: Why the CMR Is Neither and Both
   2.6 Worked Example: VF2 (Visual Rhythm)
   2.7 Worked Example: VIEW1 (Nature View Convergence)
3. The Tiered Theoretical Architecture
   3.1 Tier 1: Neurally Grounded Framework Theories
   3.2 Tier 1.5: Domain Theories Formally Reduced to T1
   3.3 Tier 2 and Below
4. Bridge Warrants: Quantifying the Transfer Problem
   4.1 The Warrant Hierarchy in Detail
   4.2 The Constitutive/Mechanism Boundary
   4.3 The Analogical Warrant and Its Limits
5. The Template System
   5.1 Template Structure
   5.2 The 151-Template Landscape
6. Calibration: The Expert Panel Method
   6.1 Panel Composition Principles
   6.2 The Crucible Debate Method
   6.3 From Debate to Calibrated JSON
   6.4 The Review Protocol
7. Confidence Discipline and the Review Protocol
   7.1 Confidence Score Ranges
   7.2 The Coburn R-squared Ceiling (Generalized)
   7.3 The Red Flag Scan
8. The Panel Sequence and Its Rationale
9. Cross-Template Interactions and the Integration Problem
10. The Allostatic Meta-Principle
    10.1 Sterling's Allostasis and Its Architectural Implications
    10.2 ALLOSTATIC_MASTER_001 (T29): The Master Template
11. IE-DPT: The Implicit-Explicit Dual-Process Elevation
    11.1 What IE-DPT Claims
    11.2 The Kirsh Connection
    11.3 Known Errors in the IE-DPT Specification
12. Computational Implementation: The Article Eater
    12.1 System Architecture
    12.2 The Gap Tracker
    12.3 The Cowork Autonomous Execution Pipeline
13. What the System Cannot Do: Limitations and Residual Gaps
    13.1 The Independence Assumption
    13.2 The Expert Judgment Bottleneck
    13.3 Cultural and Individual Variation
    13.4 The Design-Actionability Gap
14. References
15. Session Log

---

# 1. Introduction: The Problem CMR Solves

`[DRAFT — VERIFIED against Transfer doc §1, CMR Spec Part I, Theory Tier Architecture §1]`

Cognitive Neuroscience for Architecture (CNFA) is a field that aspires to ground architectural design decisions in evidence about how the brain processes built environments. The aspiration is legitimate. There is no serious doubt that buildings affect cognition, affect, stress physiology, sleep architecture, social behavior, and creative performance — the empirical literature documenting such effects spans decades and includes well-controlled studies with substantial effect sizes (Ulrich, 1984; Kaplan, 1995; Vartanian et al., 2013). The difficulty is not whether architectural environments affect the brain, but how to evaluate the *strength, specificity, and transferability* of any particular claim about any particular architectural feature's effect on any particular neural or psychological outcome.

The field's current epistemic practice is inadequate to this task. A typical CNFA research claim takes the form: "Architectural feature X activates neural mechanism Y, producing behavioral outcome Z." Such claims typically rest on three inferential steps, each of which introduces uncertainty: the neuroscience establishing mechanism Y, the bridge reasoning connecting Y to the architectural context, and the architectural-specific evidence that feature X actually engages Y in a real building. The field has no systematic method for tracking, combining, or calibrating these uncertainties. The result is a literature in which well-established neuroscience (e.g., the predictive processing account of visual cortex) is yoked to weakly supported architectural transfer claims (e.g., that a specific fractal dimension optimizes aesthetic response in buildings) without any explicit accounting for the inferential gap between the two.

CMR — Compositional Mechanistic Reasoning — is a computational system designed to impose epistemic discipline on exactly this problem. It decomposes every CNFA claim into its constituent inferential steps, assigns calibrated credence values to each step, and computes the overall credence for the claim as a product of its components. The system is compositional because it builds complex claims from simpler, independently evaluable pieces. It is mechanistic because it requires explicit specification of the neural or physiological causal pathway connecting the architectural feature to the outcome. And it is a reasoning system because it embodies a normative epistemology — a set of rules about how evidence should be combined and when claims should be trusted — rather than merely cataloging findings.

The intellectual ancestry of this approach draws on several traditions. The Bayesian epistemology that underlies the credence calculus has roots in de Finetti (1937), Savage (1954), and more recently Howson and Urbach (2006). The compositional decomposition of complex claims into mechanistic steps reflects the interventionist account of causal explanation developed by Woodward (2003). The specific problem of transferring causal findings across contexts — from laboratory to building — connects to the transportability framework of Pearl and Bareinboim (2014). And the tiered theory structure, in which domain-specific claims inherit credence from more general parent theories, draws on the structural realism tradition in philosophy of science (Worrall, 1989) and on the Lakatosian distinction between a research programme's hard core and its protective belt (Lakatos, 1970). But the CMR is not simply a Bayesian Network — it is, as described in its founding specification (per CMR Spec V1.0 §1.1), a "Web of Belief with Bayesian causal network properties," a formulation whose significance is developed in Section 2.5.

What distinguishes CMR from a purely philosophical framework is that it is implemented as a computational system — the "Article Eater" — that ingests research papers, extracts mechanism claims, assigns them to templates within the tiered architecture, and computes calibrated credence scores that can be updated as new evidence arrives. The system currently tracks 151 templates organized across 12 expert panels, of which 23 have been fully calibrated as of February 2026 (per Transfer doc §5: STRESS-I 3, LIGHT-I 8, SPATIAL-I 4, VISUAL-I 8).

Why architecture specifically? The CMR addresses a problem that is acute in architecture but general in applied science: the translation gap between laboratory findings and real-world design decisions. Architecture needs *actionable* credence estimates — not merely "nature views are beneficial" but "a window view of biodiverse natural landscape (5 channels engaged) produces r ≈ 0.65 stress reduction, while a sparse single tree (2 channels) produces r ≈ 0.30, and sky-only (1 channel) produces r ≈ 0.15" (per VISUAL-I VIEW1 calibrated JSON). The CMR's template system produces exactly calibrated parameters, grounded in mechanism chains with explicit bridge warrant assignments, that an architect can use to compare design alternatives quantitatively.

The project originated in a collaboration between the Cognitive Science department at UCSD and the Article Eater software system, beginning in early 2026. The founding specification (02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md) defined the six-step reasoning pipeline — causal decomposition, framework matching, mechanism tracing, prediction generation, cross-framework convergence, and prediction prioritization — that structures all subsequent template calibration work.

---

# 2. The Core Credence Formula

`[DRAFT — VERIFIED against Transfer doc §1, OPUS_REVIEW_GUIDE §6]`

The formula at the heart of CMR is:

```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

Every calibrated parameter in the system is ultimately a component of this product. The formula encodes a conjunctive epistemology: a CNFA effect claim is credible only to the extent that all three of its constituent conditions are met. If the parent neuroscience is strong but the bridge to architecture is weak, the product is low. If the bridge is strong but the architectural evidence is uncertain, the product is still moderated. There is no compensation — weakness anywhere cascades multiplicatively through the system.

## 2.1 P(parent theory): Credence in the Grounding Neuroscience

`[DRAFT — VERIFIED against Transfer doc §2.1, Theory Tier Architecture §2]`

The first factor represents the credence assigned to the Tier 1 framework theory that grounds the architectural claim. The current T1 roster comprises ten neurally grounded frameworks (per Transfer doc §2.1):

| # | Code | Framework | Core Reference |
|---|------|-----------|----------------|
| 1 | PP | Predictive Processing / Active Inference | Friston (2010) |
| 2 | SN | Spatial Navigation / Cognitive Mapping | O'Keefe & Nadel (1978) |
| 3 | DP | Dual-Process Evaluation | Evans & Stanovich (2013) |
| 4 | DT | DMN/TPN Dynamics | Raichle et al. (2001) |
| 5 | NM | Neuromodulatory Systems | Schultz et al. (1997) |
| 6 | IC | Interoceptive / Constructionist Affect | Barrett (2017); Seth (2013) |
| 7 | MS | Memory Systems | McClelland et al. (1995) |
| 8 | EC | Embodied Cognition | Gibson (1979); Varela et al. (1991) |
| 9 | CB | Chronobiological Regulation | Feb 15 neuroscience panel |
| 10 | MSI | Multisensory Integration | Feb 15 neuroscience panel |

Three criteria govern admission to Tier 1 (per Theory Tier Architecture §1): (1) **mechanistic specificity** — the theory specifies mechanisms at a level connecting to neural implementation; (2) **cross-domain generativity** — it generates predictions across sensory and behavioral domains, not within one domain only; and (3) **convergent multi-method support** — it is supported by evidence from multiple methodologies (single-cell recording, fMRI, lesion studies, computational modeling, behavioral experiments).

Each framework has a prior credence based on converging evidence from multiple independent experimental paradigms, the quality of neural mechanism specification, and confirmed testable predictions. PP, for instance, rests on single-neuron recording in V1 (Rao & Ballard, 1999), fMRI expectation suppression (Summerfield et al., 2006), EEG mismatch negativity (Garrido et al., 2009), and computational models (Friston, 2010). Its P(parent theory) is correspondingly high — in the range 0.80–0.85. PP is not beyond dispute: some argue the framework is unfalsifiable (Kogo & Trengove, 2015 [VERIFY]); others argue it over-extends when applied to affect (Colombo & Wright, 2017 [VERIFY]). The CMR does not require resolving these disputes; it requires assigning a credence reflecting the current balance of evidence.

**Critical errors to avoid** (per Transfer doc §2.1): ART and SRT are NOT T1 — they are T1.5 domain theories formally reduced to T1 frameworks. IE-DPT is NOT T1 #11 — it is an elevation of T1 #3 (DP); the T1 count remains 10.

The P(parent theory) term is where the Web of Belief structure does its most important work. When multiple T1 frameworks make overlapping predictions for a given architectural effect, the convergence raises the credence of the shared prediction — the Bayesian analogue of Whewell's (1840/1858) "consilience of inductions." The CMR Spec V1.0 formalizes this through the Framework Independence Matrix (§3.3), an 8×8 matrix encoding shared theoretical commitments between T1 frameworks, which allows computation of "effective independence" scores for multi-framework predictions.

How P(parent theory) is assigned in practice: The Theory Tier Architecture document (02-14_07) provides the detailed mechanistic specification for each T1 framework, including its neural implementation, cross-domain scope, known problems, and contested aspects. Panel experts consult this specification when assigning confidence to the parent theory component. The assignment is not a free parameter — it reflects published, quantifiable evidence bases, with citation counts serving as a rough proxy for community acceptance and replication breadth.

## 2.2 P(bridge): Credence in the Laboratory-to-Architecture Transfer

`[DRAFT — VERIFIED against OPUS_REVIEW_GUIDE §1, Transfer doc §2.3]`

The second factor is the CMR's most distinctive contribution: an explicit, calibrated estimate of the probability that a laboratory mechanism operates in the architectural context.

The transfer problem is a version of external validity (Campbell & Stanley, 1963). Brunswik (1956) called it ecological representativeness. It takes particularly acute form in CNFA because the gap between laboratory stimuli and architectural experience is exceptionally large. A laboratory study of visual preference might use photographs displayed on monitors for 500ms; an architectural experience involves full-body immersion in a multisensory environment over hours or years. The bridge warrant quantifies how much confidence transfers across this gap.

The CMR defines six warrant types, each with a Bayesian prior (per Transfer doc §2.3 and OPUS_REVIEW_GUIDE §1):

| Warrant Type | Prior P | Assigned When |
|--------------|---------|---------------|
| CONSTITUTIVE | 0.75 | The architectural feature IS the mechanism (e.g., window area IS daylight exposure) |
| MECHANISM | 0.60 | Complete causal pathway traced and experimentally tested |
| EMPIRICAL_COVARIANCE | 0.60 | Strong correlation (r > 0.40, replicated); mechanism inferred |
| FUNCTIONAL | 0.50 | Same function, different mechanism |
| CAPACITY | 0.45 | System has capacity, mechanism unspecified |
| ANALOGICAL | 0.35 | Structural analogy only — no direct empirical evidence in CNFA domain |

**Strict enforcement rule** (per OPUS_REVIEW_GUIDE §1): A parameter's confidence score can never exceed the ceiling implied by its bridge warrant. An ANALOGICAL warrant with confidence 0.65 is a contradiction — it must be flagged. This rule prevents the common epistemic error of allowing theoretical enthusiasm to override evidential caution.

Intellectual antecedents include Pearl and Bareinboim's (2014) transportability calculus and Steel's (2008) extrapolation analysis [VERIFY].

## 2.3 P(CNFA-specific): Credence in the Specific Architectural Parameter

`[DRAFT — VERIFIED against OPUS_REVIEW_GUIDE §3, VISUAL-I Output]`

The third factor captures credence in the specific architectural parameter — the empirical evidence that a given architectural feature produces the claimed effect in actual (or near-actual) building conditions.

This factor is disciplined by the Coburn R-squared ceiling: in the VISUAL-I panel, the Salingaros interaction analysis (D × SCI) yielded ΔR² ≈ 0.04 (per Transfer doc §6 Finding 6 and OPUS_REVIEW_GUIDE §3). This means no single visual parameter explains more than approximately 25–30% of aesthetic variance in isolation, and interaction terms between visual parameters are small (4% additional variance). The implication generalizes beyond the visual domain: be suspicious of any calibration implying a single architectural feature explains more than 30% of the target outcome. If a panel assigns d > 0.80 to any single architectural manipulation, it should be challenged — the empirical literature does not support single-feature dominance at that level for subjective outcomes.

Calibration of P(CNFA-specific) occurs during the expert panel process (Section 6). Each panel assigns confidence scores to individual architectural parameters after Crucible debate, with scores constrained by the bridge warrant ceiling (Section 2.2), the Coburn R² ceiling, and the THEORETICAL_DEFAULT rule: any parameter set below 0.50 confidence must carry the THEORETICAL_DEFAULT flag and state the assumption explicitly (per OPUS_REVIEW_GUIDE §2).

## 2.4 The Multiplicative Structure and Its Justification

`[DRAFT — VERIFIED against CMR Spec §5.1, Transfer doc §1]`

The formula multiplies rather than adds. This reflects a conjunctive epistemology: the CNFA claim is only as strong as the conjunction of all three conditions. Weakness anywhere cascades multiplicatively. This is more conservative than frameworks allowing compensation across levels (cf. Russo & Williamson, 2007 [VERIFY]). A template with P(parent) = 0.85, P(bridge) = 0.60, and P(CNFA) = 0.65 yields a composite credence of only 0.33. This is deliberate: it prevents over-confident claims from passing through the system when one or more inferential links are weak.

A counter-argument must be acknowledged: the three terms are not fully independent. Strong CNFA-specific evidence (direct architectural RCT) is simultaneously bridge evidence — it demonstrates that the mechanism does transfer to architectural conditions, which should update P(bridge) upward. Conversely, weak parent theory should reduce the interpretive value of strong CNFA-specific correlations. A future iteration might introduce conditional updating to model these dependencies. This limitation is developed in Section 13.1; the theoretical significance — why the CMR is not simply a Bayesian Network despite having BN-like features — is the subject of Section 2.5.

---

## 2.5 Quinean Webs and Bayesian Networks: Why the CMR Is Neither and Both

`[DRAFT — VERIFIED against PANEL_RUTHLESS_REVIEW_2026-02-12, DESIGN_RATIONALE.md, web_of_belief.py]`

This section addresses a question that is philosophically central and practically important: what kind of thing IS the CMR system? The project carries "PostQuinean" in its name, implements a `WebOfBelief` class with explicit references to Quine (1951), and yet computes multiplicative credence scores in a manner that looks strikingly Bayesian. A simulated ruthless review panel (Panel P-RUTHLESS, 2026-02-12) surfaced the tension sharply.

### 2.5.1 The Quinean Heritage

Quine's web of belief (Quine & Ullian, 1978) holds five commitments that the CMR system explicitly adopts:

1. **No belief is unrevisable.** Every node in the web — theoretical frameworks (T1), bridge warrants, empirical findings, even the credence formula itself — is subject to revision if the total web achieves better coherence without it. The `Belief` class defines no epistemic floor; `BeliefStatus` ranges from `STUB` through `TENTATIVE`, `ESTABLISHED`, `ENTRENCHED`, to `ANOMALOUS`, but even an `ENTRENCHED` belief can be demoted.

2. **Justification is holistic.** A belief is justified not by its foundational pedigree but by its place in the web's overall coherence. The system computes entrenchment as an emergent property — 40% connectivity, 30% level contribution, 30% coherence contribution (Thagard's formula) — rather than storing it as a fixed property. This was a deliberate architectural decision (V23.0.0 BREAKING CHANGE in `web_of_belief.py`): settable entrenchment was removed because it constituted hidden foundationalism.

3. **Revision is conservative.** When new evidence conflicts with the web, the system seeks minimal revision — preferring to revise peripheral beliefs (low entrenchment) over central ones (high connectivity and coherence). This implements Quine's principle that beliefs near the web's center resist revision more strongly than those at the periphery.

4. **Observation is theory-laden.** Empirical beliefs in the web are uncertain and interpretive. An EEG study reporting "alpha power increased" is already theory-laden (it presupposes that alpha power indexes relaxation). The system tracks source depth (`FULL_TEXT`, `ABSTRACT`, `METADATA`) not as a reliability ranking but as an index of how much interpretive context is available.

5. **Stubs are held, not forced.** Findings that do not fit the current theoretical structure are preserved as `STUB` beliefs — unintegrated nodes awaiting future theoretical integration. This prevents the foundationalist error of either forcing recalcitrant data into existing categories or discarding it.

### 2.5.2 The Bayesian Features

Despite this Quinean foundation, the CMR's credence formula looks unmistakably Bayesian:

```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

The multiplication implies conditional independence. The credence values are probabilities on [0, 1]. Individual beliefs carry `Credence` objects with `.update()` methods that apply likelihood ratios. Templates produce composite credence scores. A Bayesian would recognize this structure immediately.

Furthermore, the system assembles a Bayesian Network (via `epistemic_causal_bridge.py`) with nodes derived from the web and edges justified by constraints. The BN enables interventionist reasoning that the web alone cannot support: "What would happen if we changed the lighting?" is a do-calculus question, not a coherence question.

### 2.5.3 The Tension: Three Critiques

The Panel Ruthless Review (2026-02-12) surfaced the philosophical tension through three critiques that the CMR must answer honestly:

**Quine's critique** (simulated): "Credence values are un-Quinean. I never assigned numbers to beliefs. The web adjusts holistically to experience. Your point estimates (credence=0.75) suggest beliefs have intrinsic evidential weight independent of their web position. Wrong." And further: "You've discretized the web. My web of belief is a continuous fabric where revision ripples outward. Your discrete 'beliefs' with IDs create artificial boundaries."

**Pearl's critique** (simulated): "No do-operator implementation. Your epistemic_causal_bridge.py claims to bridge Quinean to Pearlian, but I see no actual do-calculus. Where is do(X=x)? Where are the truncated factorizations? You have causal VOCABULARY without causal SEMANTICS."

**Haack's critique** (simulated): "Coherence is underspecified. You compute 'coherence contribution' but what IS coherence in your system? Is it explanatory? Logical? Probabilistic? You've operationalized it without defining it."

### 2.5.4 The Resolution: Foundherentist Architecture

The system's answer is not to choose between Quine and Bayes but to recognize that they operate at different levels of the architecture:

**The web is primary; the BN is derivative.** This is the central architectural decision documented in `DESIGN_RATIONALE.md` §1. The `WebOfBelief` defines the epistemic landscape — what we believe, how confidently, and how beliefs cohere with each other. The Bayesian Network is derived FROM the web by extracting supported causal edges and their credence-based strengths. If the BN has an edge that the web does not support, the edge is epistemically unjustified and should be flagged — not the other way around.

This makes the system **foundherentist** in Haack's (1993) sense: it combines experiential grounding (empirical beliefs anchor the web to reality, like the clues in Haack's crossword puzzle) with mutual coherence support (beliefs support each other, like the interlocking entries in the crossword). Neither element alone is sufficient:

- Pure coherentism (no experiential anchoring) allows internally consistent but empirically disconnected webs — "science fiction epistemology."
- Pure foundationalism (no mutual support) cannot handle the multi-level evidential structure of CNFA, where laboratory findings, bridge warrants, and architectural observations must all cohere.

**Credence values are coherence-weighted, not prior probabilities.** Quine is correct that pure probability assignments are un-Quinean. The CMR's credence values are not raw probabilities but coherence-weighted confidence scores — they reflect both the direct evidence for a belief AND its position in the web. A belief with strong direct support but poor coherence with the rest of the web receives a lower effective credence than its evidence alone would suggest. This is implemented through the coherence-adjustment mechanism in `web_of_belief.py`, where credence updates propagate through support and contradiction constraints.

**The multiplicative formula is a local approximation, not a global model.** The CMR does not claim that the entire web is a Bayesian network. The three-factor formula is a local decomposition for computing CNFA-specific credence — it captures the conjunctive structure of the inference chain from laboratory to architecture. Within this local scope, the multiplicative structure is appropriate and useful. Globally, the web operates by coherence, not by probability propagation.

**The BN serves interventionist questions; the web serves epistemic questions.** "How well justified is the claim that daylight improves mood?" is an epistemic question answered by web traversal. "What would happen if we installed full-spectrum lighting?" is an interventionist question that requires causal reasoning. Pearl is correct that the BN needs do-calculus for the second class of questions; the current implementation acknowledges this as a gap (see Section 13). But the first class of questions — the CMR's primary use case — is properly addressed by the coherentist web.

### 2.5.5 What This Means in Practice

The dual architecture produces concrete benefits:

1. **Conservative credence.** The multiplicative formula prevents overconfident claims. A template with P(theory) = 0.85 but P(bridge) = 0.35 (analogical) yields composite credence of only 0.19. No amount of theoretical enthusiasm can compensate for a weak bridge — this is the conjunctive property at work.

2. **Transparent disagreement.** When two experts disagree, the web represents both positions with their respective credence values and marks the topic as `contested`. The BN does not resolve the disagreement — it propagates both scenarios. This avoids the Bayesian temptation to prematurely average over disagreements.

3. **Revision under pressure.** When new evidence conflicts with the web — for example, a high-powered replication failure — the system identifies the least entrenched belief that, if revised, would restore coherence. This implements Quinean holistic revision through computational mechanism rather than through philosophical hand-waving.

4. **Mechanism chains as epistemic commitments.** The seeded mechanism chains (Section 12) are not simply BN edges. Each `mechanism:` belief is a substantive theoretical commitment — "the visual system performs a rapid, sub-cortical ecological appraisal of the scene" — that can be challenged, revised, or replaced. The causal structure of the BN does not precede the epistemic commitments; it is derived from them.

### 2.5.6 Acknowledged Limitations

The resolution is imperfect, and the system inherits weaknesses from both traditions:

- **From Quine**: Coherence remains operationally underspecified. The current implementation uses constraint-weighted sum as a proxy for coherence, but this is not the explanatory coherence of Thagard (1989) or the probabilistic coherence of Bovens & Hartmann (2004). A formal definition of coherence for the system remains needed (per Haack's critique).

- **From Bayes**: The three-factor decomposition assumes conditional independence that does not hold (Section 2.4). Conditional updating between the factors would improve accuracy but introduce circular reasoning risks.

- **From both**: The system cannot currently distinguish between beliefs that are well-entrenched because they are well-supported and beliefs that are well-entrenched because they are well-connected to OTHER poorly-supported beliefs. This is the "mutual admiration society" problem in coherentism (BonJour, 1985) and the "prior sensitivity" problem in Bayesianism — the CMR inherits both.

---

## 2.6 Worked Example: VF2 (Visual Rhythm)

`[DRAFT — VERIFIED against VISUAL_I_Panel_Output_Feb21.md, VF2 JSON block]`

VF2 (`VF2_VISUAL_RHYTHM_001`) illustrates how the CMR formula disciplines calibration when the bridge between laboratory and architecture is weak. The template claims that architectural surfaces exhibiting "spatial rhythmic variation" (SRV) at specific frequencies engage rhythmic prediction in the visual system, producing a mild positive affect analogous to musical groove.

### The three factors for VF2:

**P(parent theory).** VF2 derives from Predictive Processing (PP) — a Tier 1 framework with strong neural evidence for hierarchical prediction and prediction-error signalling. PP is one of the system's most entrenched T1 frameworks. P(parent) is high: approximately 0.80.

**P(bridge).** The VISUAL-I panel debated this extensively (Debate 3, VISUAL_I_Panel_Output_Feb21.md). The core question: does the laboratory finding — that auditory rhythms at ~20–30% syncopation produce peak groove (Witek et al., 2014) — transfer to visual-architectural scanning? The panel consensus:

- The visual rhythm mechanism (eye-tracking saccade patterns at ~2.5–5 Hz during colonnade scanning, Taylor's data) merits EMPIRICAL_COVARIANCE warrant: 0.55.
- The specific SRV boundary values (0.12–0.25) are derived from auditory analogy only and receive ANALOGICAL warrant and THEORETICAL_DEFAULT status, confidence 0.40.
- The Scaling Coherence Index (SCI) has a retroactive correlation with Coburn's data (r ≈ 0.28), meriting EMPIRICAL_COVARIANCE at 0.45.

The effective bridge is the weakest link in the chain — the SRV boundary values at 0.40. This is because the SRV range is the specific architectural parameter; the mechanism and the SCI metric are supporting evidence but do not determine the architectural prescription.

**P(CNFA-specific).** The CNFA-specific evidence for VF2 is limited. No study has directly manipulated SRV in real buildings and measured affect. Taylor's eye-tracking data is architectural but observational, not interventional. The panel assigned P(CNFA-specific) ≈ 0.50, reflecting the scanning-speed moderator uncertainty (walking pace ~1.2 m/s assumed as baseline, but unvalidated).

### Composite credence:

```
P(CNFA) = P(parent) × P(bridge) × P(CNFA-specific)
        = 0.80 × 0.40 × 0.50
        ≈ 0.16
```

The actual `p_effect_composite` in the calibrated JSON is 0.32, somewhat higher than this pure multiplication because the panel chose the EMPIRICAL_COVARIANCE bridge (0.55) for the visual rhythm mechanism itself, reserving the ANALOGICAL bridge (0.40) only for the specific SRV boundary values. The composite of 0.32 is the weighted result across multiple sub-parameters.

**What this teaches:** A composite credence of 0.32 means the system treats visual rhythm as a real but weakly evidenced effect — appropriate for theoretical discussion but not for design prescription. The multiplicative formula prevented the common error of allowing theoretical enthusiasm (PP is well-supported!) to override the weak bridge from auditory to visual rhythm.

---

## 2.7 Worked Example: VIEW1 (Nature View Convergence)

`[DRAFT — VERIFIED against VISUAL_I_Panel_Output_Feb21.md, VIEW1 JSON block]`

VIEW1 (`NATURE_VIEW_CONVERGENCE_001`) illustrates the upper end of the credence range — a template with strong empirical grounding and a well-characterized multi-channel mechanism.

### The three factors for VIEW1:

**P(parent theory).** VIEW1 draws on multiple T1 frameworks simultaneously — this is its defining feature:

| Channel | T1 Framework | Mechanism |
|---------|-------------|-----------|
| 1 (Fractal fluency) | Predictive Processing (T1) | Low prediction error from natural fractal statistics |
| 2 (Spatial prediction) | Spatial Navigation (SC2) | Isovist-based spatial prediction confirmation |
| 3 (Attention restoration) | ART (T25) | Soft fascination → directed attention recovery |
| 4 (Photic modulation) | Neuromodulatory (L5) | Daylight spectral content → serotonin synthesis |
| 5 (Threat suppression) | Neuromodulatory (T5) | Nature scenes → amygdala low-threat signal |

Because VIEW1 converges across multiple T1 frameworks, P(parent) is effectively the conjunction of multiple well-supported theories — but since any single channel suffices for some effect, P(parent) is high: approximately 0.85.

**P(bridge).** The VISUAL-I panel assigned EMPIRICAL_COVARIANCE as the primary bridge warrant, based on:

- Ulrich (1984): surgical recovery study — direct architectural observation (hospital windows)
- Ulrich et al. (1991): psychophysiological study — controlled laboratory
- White et al. (2019): large-sample correlational — survey of 20,000+ UK adults

This gives P(bridge) ≈ 0.70. Critically, Ulrich's 1984 study used actual windows in actual hospitals — the bridge from laboratory to architecture is unusually short for this template.

Kaplan (panel member) argued for dual warrant: EMPIRICAL_COVARIANCE for the overall effect, MECHANISM warrant at lower confidence for the ART pathway specifically. This nuance is preserved in the calibrated JSON.

**P(CNFA-specific).** The CNFA-specific evidence is among the strongest in the entire template set. The aggregate nature-view effect on stress/wellbeing outcomes yields r ≈ 0.55 (meta-analytic estimate from Ulrich and subsequent replications), confidence 0.70. The five channels have not been independently varied in a factorial design — this is the primary gap — but the aggregate effect is well-replicated.

### Composite credence:

```
P(CNFA) = P(parent) × P(bridge) × P(CNFA-specific)
        = 0.85 × 0.70 × 0.70
        ≈ 0.42
```

The actual `p_effect_composite` in the calibrated JSON is 0.55. The difference from the pure multiplication reflects the panel's judgment that VIEW1's multi-channel convergence warrants a modest boost — the probability that ALL five channels are wrong is very low, even if individual channel strengths are uncertain.

**What this teaches:** Even for the strongest template, the CMR formula keeps the composite credence at 0.55, well below 1.0. This reflects genuine uncertainty: we do not know the relative contribution of each channel, we have no factorial study, and the R² ceiling from Coburn's interaction analysis (ΔR² ≈ 0.04 for individual visual parameters) implies that no single visual feature dominates the outcome.

### VF2 vs. VIEW1: The CMR in action

The contrast between VF2 (0.32) and VIEW1 (0.55) demonstrates the formula's intended behavior:

| Feature | VF2 | VIEW1 |
|---------|-----|-------|
| P(parent) | 0.80 (one T1) | 0.85 (five T1) |
| P(bridge) | 0.40 (analogical) | 0.70 (empirical) |
| P(CNFA-specific) | 0.50 (observational) | 0.70 (replicated) |
| Composite | 0.32 | 0.55 |

VF2's weakness is the bridge: auditory-to-visual analogy without direct architectural evidence. VIEW1's strength is the bridge: actual hospital window data. The CMR formula correctly identifies the bridge warrant as the discriminating factor.

---

# 3. The Tiered Theoretical Architecture

`[DRAFT — VERIFIED against TRANSFER_IE_DPT_Theory_Tiers_Feb21.md §2, 02-14_07_Theory_Tier_Architecture_V1_0.md]`

The CMR's credence formula requires P(parent theory). But which theories qualify as "parents"? Not all theories are equal — some have deep neural grounding and cross-domain generativity; others are phenomenological labels that summarize patterns without specifying mechanisms. The tiered theoretical architecture makes this distinction explicit and computationally consequential.

## 3.1 Tier 1: Ten Neurally Grounded Framework Theories

A theory qualifies as Tier 1 if it satisfies three criteria: (1) mechanistic specificity connecting to neural implementation, (2) cross-domain generativity — the theory makes predictions outside its original domain, and (3) convergent multi-method support from independent laboratories and paradigms.

The current T1 roster, finalized Feb 14 and refined Feb 15 with the addition of CB and MSI:

| # | Code | Framework | Core Reference |
|---|------|-----------|----------------|
| 1 | **PP** | Predictive Processing / Active Inference | Friston (2010, ~8,000 GS) |
| 2 | **SN** | Spatial Navigation / Cognitive Mapping | O'Keefe & Nadel (1978, ~10,000 GS) |
| 3 | **DP** | Dual-Process Evaluation | Evans & Stanovich (2013, ~4,000 GS) |
| 4 | **DT** | DMN/TPN Dynamics | Raichle et al. (2001, ~15,000 GS) |
| 5 | **NM** | Neuromodulatory Systems | Schultz, Dayan & Montague (1997, ~12,000 GS) |
| 6 | **IC** | Interoceptive / Constructionist Affect | Barrett (2017, ~4,000 GS) |
| 7 | **MS** | Memory Systems | McClelland, McNaughton & O'Reilly (1995, ~5,000 GS) |
| 8 | **EC** | Embodied Cognition | Gibson (1979, ~35,000 GS) |
| 9 | **CB** | Chronobiological Regulation | Added Feb 15 by neuroscience panel |
| 10 | **MSI** | Multisensory Integration | Added Feb 15 by neuroscience panel |

Above these ten, the meta-principle of **Allostasis** (Sterling & Eyer, 1988) serves as the ultimate explanandum — the goal all frameworks serve. Allostasis is not a T1 framework itself but the organizing principle: architectural environments are evaluated by how efficiently they support the brain's predictive regulation of physiological resources. This is formalized in Section 10 (ALLOSTATIC_MASTER_001).

**Critical historical note**: Attention Restoration Theory (ART, Kaplan 1995) and Stress Recovery Theory (SRT, Ulrich 1983) were initially listed as T1 frameworks. They were demoted to T1.5 on Feb 14 because, while empirically well-supported, they do not meet the neural mechanistic specificity criterion — ART describes functional phenomena (directed attention fatigue, soft fascination) without specifying neural mechanisms, and SRT describes autonomic recovery patterns without specifying the predictive or interoceptive mechanisms that produce them. Both are now formally reduced to T2 templates with explicit links to PP, DT, NM, and IC.

## 3.2 Tier 1.5: Domain Theories Formally Reduced to T1

Tier 1.5 theories are phenomenological organizing schemas — useful labels for patterns that practitioners recognize but that do not specify neural mechanisms independently. The CMR system performs a formal **reduction** of each T1.5 theory: decomposing its claims into T2 mechanistic templates grounded in T1 frameworks, while identifying the **irreducible residual** — the portion of the theory's explanatory scope that no current T1 framework captures.

As of February 21, ten T1.5 theories have been formally reduced:

| # | Theory | Domain | Primary T1 Frameworks |
|---|--------|--------|----------------------|
| 1 | ART (Kaplan, 1995) | Nature/Attention Restoration | PP, DT, SN |
| 2 | SRT (Ulrich, 1983) | Nature/Stress Reduction | NM, IC, PP |
| 3 | Biophilia (Wilson, 1984) | Innate Nature Affiliation | PP, EC, NM, MSI |
| 4 | Prospect-Refuge (Appleton, 1975) | View + Shelter Preference | SN, NM |
| 5 | Privacy Regulation (Altman, 1975) | Social-Spatial Boundary | IC, NM, SN, EC, PP, MS |
| 6 | Kaplan Preference Matrix (1989) | Scene Preference | PP, SN, NM, EC, DT |
| 7 | Adaptive Thermal Comfort (de Dear, 1998) | Thermal Tolerance | IC, PP, NM, EC, MS |
| 8 | Space Syntax (Hillier & Hanson, 1984) | Spatial Configuration | SN, PP, EC |
| 9 | Soundscape Theory (ISO 12913) | Acoustic Perception | PP, IC, NM, MSI |
| 10 | Place Attachment (Scannell & Gifford, 2010) | Biographical Place Experience | MS, SN, IC, EC |

The reduction process revealed several cross-cutting structural findings:

1. **Two super-templates** — IC2 (Body Budget Prediction) and AX4 (Perceived Control) — recur in 5 of 6 reductions. These templates span thermal, acoustic, social, spatial, and biographical domains. They may warrant formal elevation to a cross-reference index.

2. **IE-DPT superordinate status** is confirmed across six independent domains. Every T1.5 reduction independently requires the explicit channel (activity frame, semantic context, expertise) to explain its most practically consequential phenomenon. See Section 11 for the full IE-DPT account.

3. **Irreducible residuals cluster** in five categories: (a) explicit-channel effects (captured by IE-DPT), (b) cultural/social norms (not yet formalized), (c) individual physiological variation (below cognitive level), (d) temporal/biographical dynamics, and (e) social/community relational structure.

## 3.3 Tier 2 and Below: Mechanistic Templates and Empirical Claims

Tier 2 consists of ~150+ mechanistic templates, each specifying a concrete causal pathway: Architectural Feature → Neural Mechanism → Human Outcome. Each template carries a maturity classification:

- **How-actually**: Complete mechanism traced and experimentally tested (e.g., T1 fractal fluency, VIEW1 aggregate nature-view effect)
- **How-plausibly**: Mechanism proposed with partial support, specific neural pathway identified (e.g., VF2 visual rhythm)
- **How-possibly**: Mechanism conceivable, neural substrate proposed but not tested (e.g., PA2 allostatic calibration in place attachment)

Tier 3 comprises extracted empirical claims from the scientific literature (12,628 in the database as of Feb 20). These are linked to T2 templates via bridge warrants.

### The Tier Cascade

The relationship between tiers is not merely hierarchical — it is reductive. T1.5 theories do not sit "above" T2 templates; they are **decomposed into** T2 templates. The cascade flows as follows:

```
  IE-DPT (DP elevated to superordinate configuring role)
              │
    configures boundary conditions for
              │
              ▼
  PP · SN · DT · NM · IC · MS · EC · CB · MSI    [T1]
              │
    provide neural mechanisms for
              │
              ▼
       ~150+ MECHANISTIC TEMPLATES                 [T2]
              │
    aggregate into / reduce
              │
              ▼
     ART · SRT · Biophilia · Prospect-Refuge       [T1.5]
     Privacy Reg · Kaplan Matrix · Thermal Comfort
     Space Syntax · Soundscape · Place Attachment
              │
    predict / explain
              │
              ▼
       EMPIRICAL CLAIMS (12,628)                   [T3]
```

The cascade means that P(parent theory) in the CMR formula is not a single number but a structured computation: the credence in the T1 framework(s) that ground a particular T2 template's mechanism. A template grounded in PP (high entrenchment, ~8,000 citations) receives higher P(parent) than one grounded in a less-established framework. This is how the theoretical architecture feeds into the credence formula.

---

# 4. Bridge Warrants: Quantifying the Transfer Problem

`[DRAFT — VERIFIED against OPUS_REVIEW_GUIDE §1, Transfer doc §2.3, DESIGN_RATIONALE.md §5]`

The bridge warrant is the CMR's most distinctive contribution to the credence formula. It explicitly quantifies the probability that a laboratory mechanism operates in the architectural context — the transfer problem that plagues all applied cognitive science.

## 4.1 The Warrant Hierarchy in Detail

The CMR defines six bridge warrant types, ordered by strength:

| Warrant | P(bridge) | Criterion | Example |
|---------|-----------|-----------|---------|
| CONSTITUTIVE | 0.75 | The architectural feature IS the mechanism | Window area IS daylight exposure; isovist IS the visual field |
| MECHANISM | 0.60 | Complete causal pathway traced end-to-end | PP prediction error → amygdala → HPA → cortisol |
| EMPIRICAL_COVARIANCE | 0.60 | Strong replicated correlation (r > 0.40) | Nature view → surgical recovery (Ulrich 1984) |
| FUNCTIONAL | 0.50 | Same functional role, mechanism unspecified | Plants reduce stress in offices (mechanism unknown) |
| CAPACITY | 0.45 | System has the capacity, mechanism unspecified | "Plants have the capacity to reduce stress" |
| ANALOGICAL | 0.35 | Structural analogy only | Auditory groove → visual rhythm (VF2) |

The prior probabilities were set by expert judgment during the CMR specification process and represent default starting points. Individual panels can adjust these within ±0.10 if they provide explicit justification — but the strict enforcement rule applies: **a parameter's confidence score can never exceed the ceiling implied by its bridge warrant.** An ANALOGICAL warrant with confidence 0.65 is a logical contradiction and must be flagged.

## 4.2 The Constitutive/Mechanism Boundary

The system's highest warrant (CONSTITUTIVE, 0.75) is assigned when the architectural feature literally IS the mechanism under study. This occurs less often than intuition suggests. "Window area determines daylight exposure" qualifies — the architectural element (window) constitutively determines the independent variable (daylight). But "window view determines stress recovery" does not — the view is the stimulus, not the mechanism; the mechanism involves ecological appraisal, amygdala response, and autonomic recovery.

The distinction matters computationally: CONSTITUTIVE warrants bypass the transfer problem almost entirely (the gap between laboratory and architecture barely exists), while MECHANISM warrants still require demonstrating that the complete causal chain operates in situ.

## 4.3 The Analogical Warrant and Its Limits

ANALOGICAL (0.35) is the system's weakest bridge — and the most important to get right, because it is the most common. When a theory developed in one sensory domain (auditory rhythm) is applied to another (visual scanning), the only available justification is structural analogy. VF2 (Section 2.6) illustrates the consequences: the analogical bridge reduces composite credence from what would otherwise be a strong score to 0.32.

The ANALOGICAL warrant serves as a disciplinary device. It says: "This is worth investigating, but the evidence does not yet justify confidence in the specific architectural parameter." Templates with ANALOGICAL warrants should carry THEORETICAL_DEFAULT flags on their quantitative parameters and should be prioritized for empirical study.

Intellectual antecedents for the warrant hierarchy include Pearl and Bareinboim's (2014) transportability calculus and Steel's (2008) extrapolation analysis, though the CMR operationalizes these through expert calibration rather than formal do-calculus.

---

# 5. The Template System

`[DRAFT — VERIFIED against data/templates/*.json, audit_provenance.py output]`

Templates are the CMR's primary unit of knowledge organization. Each template represents a single mechanistic claim: a specific architectural feature produces a specific human outcome via a specified mechanism. Templates are stored as JSON files in `data/templates/` and carry calibrated parameters from expert panels.

## 5.1 Template Structure

A calibrated template contains the following core fields:

```json
{
  "template_id": "VF2_VISUAL_RHYTHM_001",
  "display_id": "VF2",
  "name": "Visual Rhythm Goldilocks",
  "t1_frameworks": ["PP"],
  "t1_5_theories": ["SRT"],
  "bridge_warrant_type": "ANALOGICAL",
  "maturity": "how-plausibly",
  "p_effect_composite": 0.32,
  "calibrated_parameters": {
    "SRV_range": {"value": [0.12, 0.25], "source": "auditory_analogy"},
    "SCI_threshold": {"value": 0.60, "source": "coburn_retroactive"}
  },
  "panel_source": "VISUAL-I",
  "panel_docs": ["docs/VISUAL_I_Panel_Output_Feb21.md"],
  "key_references": ["Taylor et al. (2005)", "Witek et al. (2014)"],
  "cross_template_interactions": [
    {"id": "PP_SPECTRAL_MATCH_001", "display": "T1", "nature": "..."}
  ]
}
```

Key fields — all contributing to the credence formula — include:
- **t1_frameworks**: Which T1 theories ground the mechanism (feeds P(parent))
- **bridge_warrant_type**: The transfer justification (feeds P(bridge))
- **p_effect_composite**: The final composite credence from the panell
- **maturity**: The mechanism's epistemic maturity (how-actually / how-plausibly / how-possibly)
- **cross_template_interactions**: Other templates that must be jointly computed

## 5.2 The 163-Template Landscape

As of February 22, 2026, the system contains 163 templates. A provenance audit (`scripts/audit_provenance.py`) reveals the following coverage:

| Criterion | Templates Passing | Coverage |
|-----------|-------------------|----------|
| References (≥1 APA citation) | 150/163 | 92% |
| T1 Framework linked | 147/163 | 90% |
| Panel source identified | 125/163 | 77% |
| Mechanism chain seeded | 23/163 | 14% |
| Confidence score assigned | 25/163 | 15% |
| Bridge warrant assigned | 19/163 | 12% |
| Calibrated parameters | 16/163 | 10% |
| T1.5 theory linked | 10/163 | 6% |

The **Skeptic Readiness Score** — the aggregate measure of how well the template set would withstand a skeptical review — is **33%**. The primary gaps are in bridge warrants, confidence scoring, and T1.5 linkage — all of which require expert panel calibration rather than automated extraction. The 8 templates with perfect 8/8 scores (including CIRCADIAN_ARCH_REG_001, DAYLIGHT_MULTICHANNEL_001, T6, T7, T14) have all been through expert panel review.

---

# 6. Calibration: The Expert Panel Method

`[DRAFT — VERIFIED against VISUAL_I_Panel_Output_Feb21.md, OPUS_REVIEW_GUIDE §2]`

Templates move from structural scaffolds to calibrated knowledge through expert panel review. This section describes the method using VISUAL-I (the first full visual cognition panel) as the case study.

## 6.1 Panel Composition Principles

Each panel includes: (a) domain experts who have published the primary research (e.g., Taylor for fractal fluency, Ulrich for SRT), (b) methodological critics who challenge overconfident calibrations (e.g., Coburn for R² ceiling enforcement), (c) a computational modeler who ensures parameterizations are implementable, and (d) an architect who provides the application perspective.

The VISUAL-I panel comprised eight members: Taylor (fractal fluency), Grahn (auditory rhythm), Salingaros (scaling hierarchy), Ulrich (stress recovery), Kaplan (attention restoration), Olshausen (neural coding), Muckli (cortical feedback), and Coburn (computational aesthetics). The diversity ensures that no single perspective dominates calibration.

## 6.2 The Crucible Debate Method

Panel calibration uses structured debate rather than averaging. Each template undergoes "crucible debate" — a process in which:

1. **The advocate** presents the template's theoretical case and proposed calibration
2. **The critic** identifies weaknesses, measurement limitations, and alternative explanations
3. **The bridge adjudicator** evaluates which bridge warrant type is appropriate
4. **Consensus formation** occurs through rounds of argument, with explicit recording of minority positions

The VISUAL-I panel produced four major debates: (1) T1 fractal fluency — whether D ≈ 1.3 optimum is architecture-specific or universal, (2) T2 visual complexity Goldilocks — how to set the PE sweet spot, (3) VF2 SRV boundaries — whether ANALOGICAL or EMPIRICAL_COVARIANCE warrant applies, and (4) VIEW1 multi-channel structure — how to handle partial redundancy across five channels.

## 6.3 From Debate to Calibrated JSON

After debate, the panel produces a calibrated JSON block for each template. This includes specific parameter values, confidence scores, bridge warrant assignments, and cross-template interaction flags. The VISUAL-I panel calibrated 8 templates, producing 12 cross-template interaction flags and identifying 6 THEORETICAL_DEFAULT parameters that require future empirical validation.

Key properties of the output:
- **All quantitative parameters** carry source attribution (who proposed, what evidence)
- **THEORETICAL_DEFAULT flags** mark any parameter set below 0.50 confidence
- **Cross-template interactions** are explicitly documented to prevent double-counting

## 6.4 The Review Protocol

Post-panel output undergoes review per the OPUS_REVIEW_GUIDE. The review checks:
- Bridge warrant consistency (no confidence above the warrant ceiling)
- Parameter range plausibility (no single feature d > 0.80)
- THEORETICAL_DEFAULT compliance (all low-confidence parameters flagged)
- Cross-template interaction documentation (no undocumented dependencies)

---

# 7. Confidence Discipline and the Review Protocol

`[DRAFT — VERIFIED against OPUS_REVIEW_GUIDE §2–3, VISUAL_I_Panel_Output_Feb21.md]`

## 7.1 Confidence Score Ranges

The CMR system enforces the following confidence score interpretation:

| Range | Interpretation | Typical Source |
|-------|---------------|----------------|
| 0.70–0.85 | High confidence — well-replicated, multi-method | Direct architectural RCTs, large meta-analyses |
| 0.50–0.70 | Moderate confidence — supported but gaps remain | Lab studies with bridge; partial in-situ evidence |
| 0.35–0.50 | Low confidence — theoretical or analogical only | Extrapolated from other domains; THEORETICAL_DEFAULT |
| < 0.35 | Very low — speculative | Structural analogy; no direct evidence |

No template should exceed 0.85 composite credence. The system is designed for a domain where uncertainty is genuine and irreducible.

## 7.2 The Coburn R-squared Ceiling (Generalized)

In the VISUAL-I panel, Coburn's computational analysis revealed that the Salingaros interaction analysis (D × SCI) yielded ΔR² ≈ 0.04. This has a general implication: **no single visual parameter explains more than approximately 25–30% of aesthetic variance in isolation**, and interaction terms between visual parameters are small (4% additional variance).

The Coburn ceiling generalizes: if a panel assigns d > 0.80 to any single architectural manipulation for a subjective outcome, it should be challenged. The empirical literature does not support single-feature dominance at that level. This rule constrains the system's calibrations across all panels, not only the visual domain.

## 7.3 The Red Flag Scan

The review protocol's red flag scan looks for:

1. **Confidence exceeds bridge warrant ceiling** — e.g., ANALOGICAL warrant with confidence 0.65
2. **Single-feature effect size exceeds Coburn ceiling** — d > 0.80 for any one architectural variable
3. **Missing THEORETICAL_DEFAULT flag** — parameter below 0.50 without explicit flag
4. **Undocumented cross-template interaction** — templates that share mechanisms but no interaction flag
5. **Missing panel source** — calibrated parameters without traceable panel provenance

The gap tracker (`scripts/gap_tracker.py`) automates several of these checks, identifying 153 gaps across the template set with severity-based triage (116 high, 14 medium).

---

# 8. The Panel Sequence and Its Rationale

`[DRAFT — VERIFIED against VISUAL_I_Panel_Output_Feb21.md, Transfer docs]`

Panels are sequenced to build dependencies correctly. The general principle: calibrate mechanisms before calibrating templates that depend on those mechanisms.

The planned panel sequence (with completion status):

| Panel | Domain | Templates | Status |
|-------|--------|-----------|--------|
| VISUAL-I | Visual cognition (T1, T2, VF1–3, VIEW1, L1, T22) | 8 calibrated | ✅ Complete |
| STRESS-I | Stress/restoration (SRT, ART derivatives) | ~6 targets | Planned |
| MAT-I | Materials/haptics | ~4 targets | Planned |
| NEUROMOD-I | Neuromodulatory systems | ~5 targets | Planned |
| SC-II | Spatial configuration (Space Syntax derivatives) | ~4 targets | Planned |
| SOC-I | Social configuration | ~3 targets | Planned |
| ACOUSTIC-I | Soundscape (ISO 12913 derivatives) | ~4 targets | Planned |

VISUAL-I was first because the visual domain has the most mature empirical base (fractal fluency, nature view, visual complexity). Each subsequent panel builds on calibrations from earlier panels — for example, STRESS-I will use VIEW1's calibrated nature-view parameters from VISUAL-I.

---

# 9. Cross-Template Interactions and the Integration Problem

`[DRAFT — VERIFIED against VISUAL_I_Panel_Output_Feb21.md cross-template flags]`

Templates are not independent. The VISUAL-I panel identified 12 cross-template interaction flags — cases where two or more templates share mechanistic substrates or have partially overlapping effects. These interactions present an integration problem: if T1 (fractal fluency) and VF2 (visual rhythm) both predict positive affect from the same facade, summing their effects would double-count the shared visual processing pathway.

The VISUAL-I panel's approach was explicit interaction documentation rather than mathematical integration:

- **T1 × VF2**: "T1 measures APERIODIC multi-scale structure (fractal); VF2 measures PERIODIC rhythmic regularity. Partial independence confirmed by Coburn (ΔR² after controlling T1: VF2 SCI ≈ 0.03). Compute jointly to avoid double-counting."
- **T1 × VIEW1**: "T1 is Channel 1 (fractal fluency) of VIEW1's five-channel model."
- **VF2 × SC3**: "VF2 (saccade-scale rhythm, ~0.2–0.4s) and SC3 (sequence-scale rhythm, ~20–45s) are nested temporal prediction hierarchies."

The general rule: when two templates share neural mechanisms, they should be computed jointly rather than independently summed. The specific method for joint computation has not been formalized — it is acknowledged as one of the system's principal open problems (Section 13).

---

# 10. The Allostatic Meta-Principle

`[DRAFT — VERIFIED against TRANSFER_IE_DPT_Theory_Tiers_Feb21.md §2.1, ALLOSTATIC_MASTER_001 template]`

## 10.1 Sterling's Allostasis and Its Architectural Implications

Allostasis (Sterling & Eyer, 1988) holds that the brain continuously modulates internal physiological parameters to meet anticipated environmental demands — not maintaining a fixed homeostatic set point but predictively adjusting to expected conditions. This is the CMR system's ultimate explanandum: all ten T1 frameworks describe mechanisms by which architecture modulates the brain's allostatic load.

A building that requires constant low-level effort (navigational uncertainty via SN, prediction error via PP, thermoregulatory adjustment via IC, circadian disruption via CB) imposes high allostatic load. A building that reduces these demands through design coherence, appropriate complexity, thermal stability, adequate daylight, and clear wayfinding reduces allostatic load and thereby supports long-term occupant wellbeing.

## 10.2 ALLOSTATIC_MASTER_001 (T29): The Master Template

Template T29 (`ALLOSTATIC_MASTER_001`) aggregates inputs from across the template landscape. VIEW1 is the single largest documented reducer of architectural allostatic load — multi-channel nature view simultaneously addresses visual PE cost (T1), threat monitoring cost (T5), attentional fatigue cost (T25), and spatial prediction cost (SC2).

T29 is not a template in the usual sense — it does not specify a single architectural feature → outcome pathway. Instead, it is an integrative framework that connects all other templates to the physiological bottom line. Its P(parent) is effectively the conjunction of IC (interoceptive) and NM (neuromodulatory) frameworks.

---

# 11. IE-DPT: The Implicit-Explicit Dual-Process Elevation

`[DRAFT — VERIFIED against TRANSFER_IE_DPT_Theory_Tiers_Feb21.md §3]`

## 11.1 What IE-DPT Claims

IE-DPT (Implicit-Explicit Dual Process Theory of architectural experience) is the system's superordinate modulating framework. It is NOT a new 11th T1 framework — it is an elevation and expansion of DP (T1 #3, Dual-Process Evaluation) to superordinate status.

**Core claim**: The explicit channel — activity frame, semantic context, deliberate attention, goal state, expertise, cultural meaning, biographical history — systematically modulates implicit-channel environmental effects. This modulation is not noise but structured, predictable, and architecturally consequential. The nine other T1 frameworks describe what the implicit channel processes; IE-DPT describes how the explicit channel configures the processing.

**Two channels:**
- *Implicit*: Fast, automatic, below deliberate awareness. Substrate: PP prediction errors, IC body-budget signals, NM valence, SN cognitive maps, EC affordances.
- *Explicit*: Slow, deliberate, context-sensitive. Mediated by prefrontal systems (DLPFC, vmPFC), semantic memory, working memory. Sets precision weights, configures category expectations, regulates implicit outputs.

## 11.2 The Kirsh Connection

IE-DPT makes a critical distinction: explicit ≠ Kahneman Type 2. In Kirsh's (2004) sense, "explicit" means information that has been externalized or made available to deliberate manipulation — whether processing is fast or slow. A professional architect's immediate aesthetic judgment is Kahneman Type 1 (automatic) but Kirsh-explicit (the result of deeply internalized explicit knowledge).

This produces a 2×2 matrix:

|  | Kahneman Type 1 | Kahneman Type 2 |
|--|-----------------|-----------------|
| **Kirsh-Explicit** | Design ideal: organized space, skilled automatic performance | Evaluative: deliberate analysis of organized space |
| **Kirsh-Implicit** | Habituation-masked: automatic processing in poor space | Cognitive overload: effortful processing in challenging space |

Good architectural design moves occupants from Cell D (cognitive overload) to Cell A (design ideal). This transition is IE-DPT's primary architectural prediction.

## 11.3 IE-DPT Superordinate Evidence

The superordinate claim is supported by convergent evidence from six independent T1.5 reductions, each of which independently required the explicit channel to explain its most consequential phenomenon:

| Domain | Phenomenon | Explicit-Channel Role |
|--------|-----------|----------------------|
| Social-spatial | density ≠ crowding | Crowding is an explicit-frame evaluation of density |
| Thermal | NV building occupants tolerate wider temperatures | Adaptive frame shifts acceptable band |
| Visual preference | individual complexity optima vary | Expertise and activity frame shift preference |
| Spatial configuration | natural movement thesis is a population aggregate | Individual goals override syntactic pull |
| Acoustic | 55 dBA traffic ≠ 55 dBA birdsong | Same level, opposite evaluation; frame-dependent |
| Biographical | rootedness vs. sense of place | Unreflective vs. explicitly constructed meaning |

---

# 12. Computational Implementation

`[DRAFT — VERIFIED against src/services/web_of_belief.py, scripts/seed_mechanism_beliefs.py, tests/test_mechanism_chain_validation.py]`

The theoretical architecture described in Sections 1–11 is implemented in code. The key components:

- **Web of Belief** (`src/services/web_of_belief.py`): Core epistemic engine. `Belief` and `Constraint` dataclasses. `WebOfBelief` manages beliefs, constraints, and coherence computation. 5 status levels (`STUB`, `TENTATIVE`, `ESTABLISHED`, `ENTRENCHED`, `ANOMALOUS`), 5 epistemic levels, 7 causal directions.

- **Mechanism Chains** (`scripts/seed_mechanism_beliefs.py`): 21 mechanism beliefs across 6 chain families (ART, SRT, OLF_SRT, MAT4, L3, DT1). Each belief is a substantive theoretical commitment (`mechanism:` nodes) linked by `EPISTEMIC_MEDIATION` and `SUPPORTS` constraints with `COHERENCE_SUPPORT` cross-chain bridges.

- **Traversal** (`src/services/interpretive_intelligence.py`): `MechanismExplanationPattern.traverse()` performs BFS walk along mechanism chains from entry points, collecting parallel routes. The traversal is validated by 21 unit tests that assert correct chain lengths, endpoints, and cross-chain coherence constraints.

- **Template Persistence** (`data/templates/*.json`): 163 template JSON files with provenance-tracked calibrations. Audited by `scripts/audit_provenance.py` (Skeptic Readiness: 33%). Gaps tracked by `scripts/gap_tracker.py` (153 gaps, 116 high severity).

- **Epistemic-Causal Bridge** (`src/services/epistemic_causal_bridge.py`): Derives BN structure from web constraints. This is the web-to-BN conversion described in Section 2.5 — the BN is derivative of the epistemic web.

---

# 13. Limitations

`[DRAFT — VERIFIED against PANEL_RUTHLESS_REVIEW_2026-02-12.md]`

The CMR system has significant acknowledged limitations, many identified by the Panel Ruthless Review (2026-02-12):

## 13.1 Conditional Independence Assumption

The three factors in P(parent) × P(bridge) × P(CNFA) are not independent (Section 2.4). Strong CNFA-specific evidence is simultaneously bridge evidence. This creates a known conservatism in the formula: the multiplicative structure can understate confidence when the three factors are positively correlated. Conditional updating would improve accuracy but risks circular reasoning.

## 13.2 No Do-Calculus Implementation

Pearl's critique is valid: the system has causal vocabulary without full causal semantics. The `epistemic_causal_bridge.py` assembles BN structure but does not implement truncated factorizations, do-operator, or formal transportability calculus. Interventionist questions ("what would happen if...") are answered by qualitative mechanism traversal, not by formal causal inference.

## 13.3 Coherence Remains Underspecified

Haack's critique is valid: the system computes "coherence contribution" using constraint-weighted sums but does not formally define coherence. This is neither Thagard's explanatory coherence nor Bovens & Hartmann's probabilistic coherence — it is an operational proxy that may miss theoretically important coherence properties.

## 13.4 Overconfidence in Credence Values

Kahneman's critique (Panel Ruthless Review) is partially addressed by the Coburn ceiling and bridge warrant enforcement, but the fundamental concern remains: credence values are point estimates with narrow uncertainty bounds (typically ±0.15). Real epistemic uncertainty in this domain is likely larger. The system would benefit from wider intervals and explicit treatment of unknown unknowns.

## 13.5 No Severe Testing or Defeater Search

Mayo's critique: the system accumulates supporting evidence but does not actively seek defeaters. A belief that is "consistent with 10 studies" may not have been severely tested by any of them. The system needs mechanisms for actively searching for evidence AGAINST beliefs, not just evidence FOR them.

## 13.6 Replication and Publication Bias

Meehl's critique: the system does not track independent replication (same finding from same lab twice is not independent evidence) or adjust for publication bias (the file drawer problem). The `ReplicationStatus` enum exists in the codebase but is not consistently populated or used in credence computation.

---
