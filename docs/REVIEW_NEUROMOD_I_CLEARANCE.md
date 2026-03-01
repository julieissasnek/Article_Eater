# OPUS REVIEW — NEUROMOD-I PRE-PANEL CLEARANCE (S-07)
## Reviewer: Opus/Chat (Claude Opus 4.6)
## Date: February 23, 2026
## Input: PENDING_REVIEW_NEUROMOD_I.md (Cowork, Feb 23 2026)

---

# Verdict: CLEARED WITH FLAGS — 8 issues, 3 of them serious

---

# 1. Overall Assessment

This is the most ambitious pre-panel clearance Cowork has produced — and
appropriately so, since NEUROMOD-I is the most consequential panel remaining.
T29 (ALLOSTATIC_MASTER_001) is the integration template that receives input
from every prior panel, which means errors here propagate everywhere. Cowork
clearly understands this: the dependency analysis (§3.3) is the most thorough
we have seen, correctly identifying seven dependency chains across six prior
panels. The constraint set (C-01 through C-10) is comprehensive. The addition
of Crucible debate pairings — absent from the CREATIVE-I pre-panel and flagged
in my review there — is a welcome correction.

The document has three serious issues, three moderate issues, and two minor
ones.

---

# 2. Serious Issues

## ISSUE 1: The Restoration Term in T29 — Cowork Is Right, But the Implications Are Large

Cowork added a restoration term (−w_restoration × restoration_benefit) to the
T29 formula and explicitly flagged it for Opus review, noting that the original
Sprint Brief specification did not include it. This is the kind of principled
deviation that Cowork should be commended for — the reasoning is correct.
Without a restoration term, T29 is a monotonically increasing cost accumulator
that cannot model recovery, which contradicts decades of evidence on restorative
environments (Ulrich, 1984; Kaplan, 1995; Berman, Jonides, & Kaplan, 2008).
A model of allostatic load that can never decrease is empirically indefensible.

However, the implications of adding this term are substantial and need to be
worked through before the panel executes:

**(a) What enters the restoration term?** Cowork lists VIEW1 and
HC_CREATIVE_DIVERGENCE, but the full set of restorative inputs across the
calibrated template corpus is larger. STRESS-I T7 (body-budget restoration),
MEMORY-I MS_CONSOLIDATION_RESTORATION_001 (DMN re-engagement conditions),
LIGHT-I daylight effects (d = 0.38), and THERMAL-I thermal comfort (which
reduces HPA load when conditions are within the adaptive comfort band) all have
restorative components. The restoration term risks becoming a catch-all that
absorbs restorative effects from every other panel, which would make it
extremely difficult to calibrate.

**(b) Temporal dynamics.** The cost terms in T29 operate on chronic timescales
(weeks to months of cumulative load). Does the restoration term operate on the
same timescale? Nature exposure has acute cortisol reduction effects (Park
et al., 2010, show salivary cortisol reduction within 15–20 minutes of forest
exposure) as well as chronic effects (Astell-Burt & Feng, 2019, on
residential greenness and long-term cortisol trajectories). The restoration
term must specify its timescale or it will be incommensurable with the cost
terms.

**(c) Linearity assumption.** Adding a negative linear term to a positive
linear sum assumes that restoration simply subtracts from load. The empirical
evidence suggests that restoration may be nonlinear — there may be a floor
effect (you cannot restore below baseline) and possibly a ceiling effect
(restoration saturates after a certain dose). This interacts with Crucible
Debate 3 (additive vs. nonlinear).

**Decision**: Accept the restoration term. It is necessary. But add the
following constraint:

> **C-11**: The restoration term in T29 is limited to CHRONIC restorative
> inputs that operate on timescales commensurate with the cost terms (weeks
> to months). Acute restoration effects (e.g., 15-minute cortisol reduction
> from nature exposure) are modelled within individual templates, not in T29.
> The restoration term has a floor at zero (load cannot go below baseline).
> Restorative inputs are: VIEW1 (nature view, VISUAL-I), daylight (LIGHT-I,
> d = 0.38), thermal comfort within adaptive band (THERMAL-I), and
> HC_CREATIVE_DIVERGENCE (CREATIVE-I) — exhaustive list, no others without
> explicit justification. Each enters with THEORETICAL_DEFAULT weight (1.0)
> pending empirical calibration.

## ISSUE 2: Template Count — 10 vs. 7 in GAP_PANEL_MASTER_PLAN

The transfer document (§5.3) lists NEUROMOD-I as having 7 templates. The
Sprint Brief apparently expanded this to 9 or 10. This pre-panel lists 10.
The discrepancy is larger than in CREATIVE-I (where 5 became 7). Cowork
addresses one addition explicitly (NM_SAFETY_SIGNALING_001, Ambiguity 3) and
justifies it well — safety signaling is the mechanistic complement of threat
detection. But the other two additions are not identified or justified.

Comparing the GAP_PANEL_MASTER_PLAN expected topics (7: dopaminergic
novelty/reward, serotonergic mood/wellbeing, HPA stress cascade, allostatic
master integration T29, plus 3 others) against the 10 listed templates, the
additions appear to be:

- NM_SAFETY_SIGNALING_001 (justified by Cowork — accepted)
- NM_CHOLINERGIC_GATING_007 (cholinergic attention — not explicitly justified)
- MULTIMODAL_PE_INTEGRATION_001 (PE convergence — not explicitly justified)

Both additions are defensible — cholinergic gating is a core neuromodulatory
system that would be a conspicuous omission, and PE integration is essential
for T29 — but they should be explicitly noted.

**Decision**: Accept 10 templates. Add explicit justification for all three
additions. The panel is large but the dependency structure requires it.

## ISSUE 3: Missing Serotonergic Template

The GAP_PANEL_MASTER_PLAN lists "serotonergic mood/wellbeing" as an expected
NEUROMOD-I topic. There is no serotonergic template in this pre-panel
document. This is a significant omission. The serotonergic system is one of
the four major neuromodulatory systems (DA, NE, 5-HT, ACh). Cholinergic
gating is included (NM_CHOLINERGIC_GATING_007) but serotonin is absent.

Serotonergic modulation is directly relevant to architectural experience:

- 5-HT modulates mood valence and emotional reactivity to environmental
  stimuli (Cools et al., 2008; Dayan & Huys, 2009)
- Light exposure drives serotonin synthesis via tryptophan hydroxylase
  (Lambert et al., 2002) — this is the neurochemical substrate underlying the
  LIGHT-I melanopic pathway and seasonal affective dynamics
- The 5-HT system interacts with the HPA axis in stress responses (Lowry
  et al., 2009) — relevant to T29 integration

Without a serotonergic template, T29 is missing a major input channel. The
allostatic load formula lists w_HPA, w_NE, w_DA, w_ACh, and
w_inflammation — but no w_5HT. This is an incomplete model of neuromodulatory
allostatic load.

**Decision**: This must be addressed before panel execution. Two options:

**(a) Add an 11th template** (NM_SEROTONERGIC_MOOD_001 or similar). This
increases panel size but completes the neuromodulatory roster. The expert for
this template would be Peter Dayan (already recommended for the unnamed
computational modeller slot) or Trevor Robbins (who has extensive work on
monoamine systems including 5-HT; Robbins & Arnsten, 2009, covers both ACh
and monoamines). Alternative: Roshan Cools (Donders Institute), who has
specific expertise on serotonergic modulation of cognition (Cools et al.,
2008).

**(b) Fold serotonergic modulation into the MULTIMODAL_PE_INTEGRATION_001
template** as a serotonergic precision-weighting mechanism. This preserves the
10-template count but overloads an already complex integration template.

Option (a) is strongly preferred. Eleven templates is large but manageable,
and the serotonergic system deserves its own mechanism chain. Add w_5HT to the
T29 formula.

---

# 3. Moderate Issues

## ISSUE 4: The "Addictive Building" Framing in Crucible Debate 1

The wanting/liking debate (Crucible Debate 1) introduces the "addictive
building" hypothesis — the idea that some commercial spaces exploit
wanting-liking dissociation. This is a provocative framing that could derail
the Crucible into normative territory (is it ethical to design wanting-
maximising spaces?) rather than keeping it on mechanistic ground (what is the
neural pathway from spatial feature to wanting vs. liking?).

The Berridge wanting/liking dissociation is well-established in animal models
(Berridge & Robinson, 1998; Berridge, 2003) and has been replicated in human
studies using implicit measures (Pool et al., 2016). Its application to
architecture is legitimate. But the "addictive building" label invites
confusion between the scientific construct (mesolimbic DA mediates incentive
salience independently of hedonic pleasure) and a normative claim (designers
are manipulating people).

**Decision**: Reframe Crucible Debate 1. The debate should be: "Does
architectural novelty preferentially engage incentive salience (wanting /
mesolimbic DA) or hedonic evaluation (liking / opioid hotspots), and are these
dissociable in the built environment?" Drop the "addictive building" framing.
If the panel produces evidence of dissociation, note it as an ethical
implication in Output Block 5 (residual gaps / future work), not as a Crucible
finding.

## ISSUE 5: Crucible Debate 3 — Additive vs. Nonlinear — Is Underspecified

The third Crucible debate (additive vs. nonlinear allostatic load) is the
right question but as framed it lacks the specificity needed for a productive
debate. "Nonlinear" covers many possibilities: threshold effects, exponential
acceleration, logarithmic saturation, hysteresis, bifurcation. Sterling's
(2012) allostasis model is cited but not specified in terms of functional
form.

More importantly, the Sprint Brief apparently mandates additive (Audit Finding
A-03). If the panel is constrained to produce an additive model, debating
whether additive is adequate seems like a purely academic exercise — the
outcome is predetermined.

**Decision**: Reframe as follows. The panel IS constrained to produce an
additive model for T29 (per A-03). The Crucible debate should focus on:
"Under what conditions does the additive model fail, and what is the magnitude
of the error?" This produces a concrete deliverable — a boundary-conditions
analysis — rather than an open-ended theoretical debate. The output should be
a qualifier/rebuttal pair in T29's Toulmin justification: qualifier = "additive
model adequate when individual subsystem loads are below [threshold]"; rebuttal
= "model breaks down under [conditions], estimated error magnitude [X]."

## ISSUE 6: Peter Dayan Affiliation

Cowork lists Peter Dayan as "Max Planck Tübingen → UCL." The arrow is
ambiguous — it could mean he moved from one to the other, or that both are
current. Dayan directed the Gatsby Computational Neuroscience Unit at UCL for
many years before moving to the Max Planck Institute for Biological
Cybernetics in Tübingen as a director. His current primary affiliation is
Max Planck Tübingen, not UCL. This should be corrected for roster accuracy.

**Decision**: Correct to "Max Planck Institute for Biological Cybernetics,
Tübingen (formerly UCL Gatsby Unit)."

---

# 4. Minor Issues

## ISSUE 7: IE-DPT Mapping Could Be Deeper

C-08 includes IE-DPT framing, which is good — Cowork learned from the
CREATIVE-I review. But the mapping given ("neuromodulatory systems operate
primarily at the IMPLICIT level; threat and safety signaling have both implicit
and explicit components") is too coarse for a panel whose entire subject matter
is the implicit/explicit boundary.

The neuromodulatory systems actually provide a textbook case for IE-DPT
gradation:

- **Fully implicit**: Phasic DA novelty response, amygdala threat detection,
  LC-NE tonic mode setting — these operate below conscious awareness
- **Implicit-to-explicit transition**: Wanting (implicit incentive salience)
  vs. liking (can be explicit hedonic evaluation) — Berridge's core dissociation
  IS an implicit/explicit dissociation
- **Explicit modulation of implicit systems**: Safety signaling via vmPFC →
  amygdala inhibition — this is an explicit cognitive appraisal ("this space is
  safe") that downregulates an implicit threat response
- **AX4 interaction**: Perceived control (AX4, now formally elevated) operates
  as an explicit cognitive moderator of implicit neuromodulatory stress
  responses — this is precisely the kind of cross-cutting implicit/explicit
  interaction that IE-DPT was designed to capture

**Decision**: Expand C-08 to include these four IE-DPT gradations. Each
template should specify where its primary mechanism sits on this gradient. T29
should include an IE-DPT integration note indicating which subsystem inputs
are implicit (and therefore not amenable to cognitive intervention) vs. which
have explicit modulators (and therefore can be influenced by design that
supports conscious appraisal — prospect-refuge legibility, wayfinding clarity,
perceived control affordances).

## ISSUE 8: AX4 Not Referenced in T29 Specification

The transfer document records AX4 (Perceived Control) as a formally elevated
cross-cutting moderator with 17+ validation instances (d ≈ 0.45). The
CREATIVE-I review confirmed elevation and triggered structural implementation.
Yet T29's mathematical specification does not include AX4.

Perceived control is one of the most potent moderators of allostatic load. The
Whitehall II studies (Marmot et al., 1991; Steptoe & Marmot, 2002) showed
that low perceived control over work demands was a stronger predictor of
cardiovascular morbidity than the demands themselves — a finding that has been
replicated across multiple occupational cohorts. Schweiker & Wagner (2015)
demonstrated the same effect in thermal comfort. If T29 is the master
allostatic integration template, AX4 must appear in it.

The question is how AX4 enters the formula. Two options:

**(a) As a multiplicative moderator** on all cost terms:
```
AL_total = AX4_mod × (w_HPA × HPA + w_NE × NE + ... ) − w_rest × restoration
```
where AX4_mod = f(perceived_control), ranging from ~0.6 (high control, load
reduced) to ~1.4 (low control, load amplified).

**(b) As a moderator on specific subsystems only** — particularly HPA (stress)
and NE (arousal), which are the subsystems most clearly moderated by perceived
control in the empirical literature.

Option (b) is more empirically defensible. The evidence that perceived control
moderates dopaminergic novelty responses or cholinergic precision gating is
much thinner than the evidence for HPA and NE moderation.

**Decision**: Add AX4 to T29 as a subsystem-specific moderator on HPA and NE
terms. Add a constraint:

> **C-12**: AX4 (Perceived Control) enters T29 as a moderator on w_HPA and
> w_NE terms specifically. AX4_mod = f(perceived_control), calibrated per
> domain. Default AX4_mod range: 0.6 (high control) to 1.4 (low control),
> with THEORETICAL_DEFAULT until panel-specific calibration. AX4 does NOT
> moderate the restoration term (restoration operates independently of
> perceived control over stressors).

---

# 5. Items That Are Correct and Need No Revision

- **Expert roster** (with Dayan affiliation correction and serotonin expert
  addition): Schultz, Berridge, Aston-Jones, Robbins, LeDoux, Milad/Quirk are
  all first-choice authorities. The McEwen legacy / Seeman living-anchor
  protocol is well-handled. Dayan recommendation for the computational
  modeller slot is excellent.

- **Dependency analysis** (§3.3): Seven dependencies across six panels,
  correctly identified with appropriate constraints. The PE encoding partial-
  out (MEMORY-I / NEUROMOD-I) is particularly well-specified.

- **Scope partition for DA templates** (Ambiguity 1): Phasic novelty vs.
  sustained incentive salience vs. computational RPE mechanism. Clean and
  defensible.

- **T29 mathematical specification** (§4): The additive weighted-sum formula
  is correctly structured (with the restoration-term addition reviewed above).
  The constraint that T29 is calibrated LAST (C-10) is essential.

- **Evidence quality flags A–E**: All five are well-identified. Flag B
  (RPE architectural extrapolation) and Flag C (wanting/liking measurement)
  correctly identify the long bridges from laboratory neuroscience to
  architectural application.

- **Calibration order** (§8): DA cluster → NE/ACh → threat/safety → PE
  convergence → T29 last. Sound rationale.

- **Constraints C-01 through C-10**: Comprehensive and well-specified. C-04
  (PE encoding partial-out) is particularly important.

- **Barrett-Craig integration** (C-09): Correctly applies the newly adopted
  working model.

---

# 6. Summary of Required Actions Before Panel Execution

| # | Issue | Action | Priority |
|---|-------|--------|----------|
| 1 | Restoration term in T29 | Accept; add C-11 (chronic timescale, floor at zero, exhaustive input list) | SERIOUS |
| 2 | Template count 10 vs. 7 | Accept 10; add explicit justification for 3 additions | SERIOUS |
| 3 | Missing serotonergic template | Add 11th template (NM_SEROTONERGIC_MOOD_001) + w_5HT to T29 formula; add Roshan Cools or expand Robbins role | SERIOUS |
| 4 | "Addictive building" framing | Reframe Crucible Debate 1 — mechanistic dissociation, not normative | MODERATE |
| 5 | Crucible Debate 3 underspecified | Reframe as boundary-conditions analysis within additive constraint | MODERATE |
| 6 | Dayan affiliation | Correct to Max Planck Tübingen (formerly UCL Gatsby) | MINOR |
| 7 | IE-DPT mapping too coarse | Expand C-08 with four-level implicit/explicit gradient | MODERATE |
| 8 | AX4 missing from T29 | Add C-12 (AX4 moderates HPA and NE terms specifically) | MODERATE |

---

# 7. Updated Constraint Set (C-01 through C-12)

For clarity, the full constraint set after this review is:

- **C-01**: Inherit STRESS-I HPA parameters. Do not re-derive.
- **C-02**: Social isolation additive in T29 (from SOCIAL-I). Not multiplicative.
- **C-03**: T29 additive weighted-sum. Equal weights (1.0) THEORETICAL_DEFAULT.
- **C-04**: PE encoding partial-out: NEUROMOD-I owns DA mechanism; MEMORY-I owns encoding.
- **C-05**: Inherit VIEW1 (negative/restorative) and LIGHT-I daylight (d = 0.38) into T29.
- **C-06**: No single d > 0.80 (Coburn ceiling).
- **C-07**: Scope partition: NOVELTY_002 = phasic; NOVELTY_REWARD_001 = sustained.
- **C-08**: IE-DPT framing with four-level gradient (fully implicit → implicit-to-explicit transition → explicit modulation of implicit → AX4 cross-cutting). Each template specifies its position.
- **C-09**: Barrett-Craig two-stage insular model (CMR working model) for IC components.
- **C-10**: T29 calibrated LAST.
- **C-11** (NEW): Restoration term chronic-only, floor at zero, exhaustive input list (VIEW1, daylight, thermal comfort, HC_CREATIVE_DIVERGENCE). THEORETICAL_DEFAULT weights.
- **C-12** (NEW): AX4 moderates w_HPA and w_NE in T29. AX4_mod range 0.6–1.4. THEORETICAL_DEFAULT. Does not moderate restoration.

---

# 8. A Note on Panel Size and Execution Risk

Eleven templates is the largest panel in the CMR pipeline (MUSIC-I had 13, but
NEUROMOD-I's templates are more heavily interdependent). The dependency load —
seven chains across six prior panels, plus the T29 master integration — makes
this panel uniquely vulnerable to error propagation. The crash-resilience
protocol is essential here: Cowork should save after EVERY template, not every
two. T29 in particular should be treated as a separate execution phase with
its own checkpoint.

I would also recommend that T29 receive a dedicated post-panel review — not
just as part of the NEUROMOD-I panel review, but as a standalone document that
verifies every input term against its source panel, confirms the additive
structure, and checks for double-counting. This is the template that holds the
entire allostatic integration together; it deserves proportional scrutiny.

---

*REVIEW_NEUROMOD_I_CLEARANCE.md — CMR Project*
*Reviewer: Opus/Chat (Claude Opus 4.6), February 23, 2026*
*Status: CLEARED WITH FLAGS (8 items, see §6)*
*Awaiting Cowork revision on Issues 1–3 (SERIOUS) before panel execution*
