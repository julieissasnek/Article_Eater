# OPUS REVIEW — CROSSCUT-I PRE-PANEL CLEARANCE (S-08)
## Reviewer: Opus/Chat (Claude Opus 4.6)
## Date: February 23, 2026
## Input: PENDING_REVIEW_CROSSCUT_I.md (Cowork, Feb 23 2026)

---

# Verdict: CLEARED WITH FLAGS — 9 issues, 2 structural decisions required before execution

This is the final panel. It carries more accumulated weight than any panel
before it: 6 cross-panel assignments, the AX4 canonical specification, the
Aesthetic Anchoring evaluation, the differential-mode model adoption, and the
VR limitation axiom that retroactively applies to the entire template corpus.
Cowork has produced a well-structured pre-panel document that correctly
identifies the panel's dual character (meta-level axioms vs. integrative
mechanisms) and proposes a phased execution plan. The expert roster
recommendations are strong. The Crucible debates are well-chosen.

The document requires two structural decisions before execution, plus seven
additional flags of varying severity.

---

# 1. Structural Decisions

## DECISION A: Panel Split — Phase A/B Within a Single Panel or Two Separate Panels?

Cowork proposes a two-phase structure (Phase A: 8 AX axioms, Phase B: 7 CROSS
mechanisms) within a single panel. My NEUROMOD-I review (§4.2) flagged the
question of whether CROSSCUT-I should be split into two separate panels
(CROSSCUT-Ia and CROSSCUT-Ib). Having now read the pre-panel document, I can
assess this properly.

**The case for splitting**: The AX templates and the CROSS templates have
fundamentally different epistemological characters. The AX templates are
meta-analytic parameters derived from aggregate patterns across the corpus —
they are calibrated by examining what 76 prior templates collectively imply
about dose-response, habituation, individual differences, and so on. The CROSS
templates are integrative neural mechanisms (thalamic gating, salience
switching, working memory oscillations) that require traditional neuroscience
panel methods. Mixing these in a single panel means the expert roster must
serve two masters: meta-analysts for Phase A and neuroscientists for Phase B.
The Round Table statements and Crucible debates would have to context-switch
between modes.

**The case for keeping it unified**: The AX templates and CROSS templates
interact. AX_DOSE_RESPONSE_007 specifies functional forms that the CROSS
templates use. AX_HABITUATION_002 determines how quickly CROSS mechanisms
attenuate. AX_ATTENTION_MEDIATION_010 directly feeds SALIENCE_NETWORK_SWITCH_001
and CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001. Separating them into two panels
would require the second panel to inherit from the first, adding a dependency
layer. Given that CROSSCUT-I is the last panel, there is no downstream panel
to propagate errors to — the cost of a unified panel that is slightly
unwieldy is lower than the cost of inter-panel dependency management.

**Decision: Keep unified, but enforce the Phase A → Phase B structure as a
hard execution boundary.** Phase A (AX axioms 1–8) must be fully complete and
checkpointed before Phase B (CROSS mechanisms 9–15) begins. Cowork should
treat the Phase A/B boundary as equivalent to a panel handoff: full save,
internal consistency check on all 8 AX parameters, then proceed to Phase B.
This gives us the benefits of phasing without the overhead of two separate
panels.

Add constraint:

> **C-09**: Phase A (AX templates 1–8) must be fully complete and internally
> consistent before Phase B (CROSS/mechanism templates 9–15) begins.
> Phase A outputs serve as inputs to Phase B. Treat the Phase A/B boundary
> as a hard checkpoint with internal consistency verification.

## DECISION B: AX3 Awe Templates — Include or Defer?

Cowork flags this correctly. Three AX3 awe templates (HIGH_PE, SMALL_SELF,
NEED_FOR_ACCOMMODATION) are referenced as cross-template interactions in
VISUAL-I but do not exist as standalone templates. The Sprint Brief
conditionally includes them ("if in the gap registry, add them"). Adding them
expands the panel from 15 to 18 templates.

The cost-benefit is straightforward:

**Costs of including**: 18 templates is the largest panel by a wide margin.
Awe is a contested construct — Keltner & Haidt (2003) define it via perceived
vastness and need for accommodation, but the neural mechanisms are poorly
specified (Yaden et al., 2019, review identifies default mode network
suppression and interoceptive surprise but no consensus circuit model). Three
templates for awe may be premature given the thin evidence base.

**Benefits of including**: VISUAL-I's VF1, VF3, and L1 all reference AX3 as
a cross-template interaction. If AX3 remains uncalibrated, these cross-
template flags are permanently unresolved. Keltner is already on the roster.
Awe is directly relevant to the project's architectural scope — cathedrals,
monumental spaces, landscape vistas are canonical architectural experiences
that the CMR should be able to model.

**Costs of deferring**: The AX3 cross-template flags from VISUAL-I remain
permanently open. No future panel is planned to address them.

**Decision: Include 2 of the 3 awe templates, defer the third.** The three
proposed templates (HIGH_PE, SMALL_SELF, NEED_FOR_ACCOMMODATION) overlap
substantially. The "need for accommodation" construct (Keltner & Haidt, 2003)
IS the prediction-error mechanism applied to awe — it is the same as "high PE"
described in predictive processing terms. These can be consolidated:

- **AX3_AWE_MECHANISM_001** — consolidates HIGH_PE and NEED_FOR_ACCOMMODATION.
  The mechanism IS the prediction error: vast/complex stimuli that exceed the
  brain's current generative model, requiring schema revision. This is a PP
  mechanism with SN involvement (salience detection of the vastness cue).
  Anchored by Keltner + Friston.

- **AX3_SMALL_SELF_001** — the downstream experiential and prosocial
  consequence of awe. This is the IC/EC component: interoceptive shift
  (Barrett's body-budget recalibration in the face of vastness) + embodied
  self-diminishment. This has distinct architectural implications (ceiling
  height, spatial volume, vertical emphasis).

- **DEFER**: AX3_NEED_FOR_ACCOMMODATION_001 as a standalone — it is absorbed
  into AX3_AWE_MECHANISM_001.

This gives 17 templates total: 8 AX axioms + 7 CROSS mechanisms + 2 AX3 awe
templates. Still large but more manageable than 18, and it resolves the
VISUAL-I cross-template flags.

Add the 2 awe templates to Phase B (after template 15), since they are
mechanism templates, not meta-level axioms. Revised total calibration order
is 8 + 9 = 17.

---

# 2. Substantive Issues

## ISSUE 1: The Differential-Mode Model Is Not in the Document

My NEUROMOD-I review (§4.1) formally adopted the differential-mode model as a
CMR working model. Cowork's §10.5 mentions it ("CROSSCUT-I should formally
evaluate this for cross-panel adoption") but the pre-panel document does not
include it in the constraint set, the Crucible debates, or the calibration
plan. This is a gap.

The differential-mode model is already adopted — the NEUROMOD-I review
confirmed it. CROSSCUT-I does not need to re-evaluate it. What CROSSCUT-I
needs to do is operationalise it: for each of the 76 calibrated templates,
specify where the primary mechanism falls on the differential-mode spectrum
(low stimulation / divergent-implicit vs. moderate stimulation / convergent-
explicit). This is a meta-analytic task that belongs in Phase A — probably as
a component of AX_DOSE_RESPONSE_007 or AX_ATTENTION_MEDIATION_010.

**Action**: Add constraint:

> **C-10**: The differential-mode model (low stimulation → divergent/implicit;
> moderate stimulation → convergent/explicit; converged from CREATIVE-I +
> NEUROMOD-I LC-NE framework) is a CMR working model. CROSSCUT-I must
> operationalise it by specifying the optimal stimulation level for each
> major mechanism class across the template corpus. This is a Phase A task
> (AX_DOSE_RESPONSE_007 or AX_ATTENTION_MEDIATION_010).

## ISSUE 2: AX4 Canonical Specification — Must Formally Integrate the Elevation Decision

AX_CONTROL_STRESS_004 is described as formalising C-12 from NEUROMOD-I
(AX4_mod 0.6–1.4 on HPA and NE). But this template must do more than repeat
C-12. The AX4 elevation decision (REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md,
Decision 2) established AX4 as a formally recognised cross-cutting moderator
with domain-specific effect sizes. The canonical specification must include:

- The default prior (d ≈ 0.45 from Schweiker & Wagner, 2015)
- The domain-specific calibration protocol (each panel calibrates its own
  AX4 magnitude)
- The T29 integration (AX4_mod on HPA and NE, range 0.6–1.4, per C-12)
- The interaction with IE-DPT Level 4 (AX4 as the canonical
  explicit-moderates-implicit variable)
- A survey of every prior panel's AX4 references (there are 17+ instances)
  to verify consistency

This is the template where the elevation decision becomes operational. It
deserves Tier A status.

**Action**: Upgrade AX_CONTROL_STRESS_004 from the current implicit Tier B
to Tier A. Add a sub-task: survey all 17+ AX4 instances across the calibrated
corpus for consistency.

## ISSUE 3: No Expert Roster for Awe (If AX3 Included)

If the AX3 awe templates are included per Decision B, Keltner is the right
primary anchor. But the roster currently has Keltner listed with no secondary
or complement. For two awe templates, the panel needs at least one additional
perspective. The predictive-processing account of awe (vast stimuli exceeding
the generative model) should be anchored by someone from the PP tradition.

**Recommendation**: Friston (already on the roster as computational
neuroscientist) can serve as the PP complement for AX3_AWE_MECHANISM_001.
For AX3_SMALL_SELF_001, the interoceptive/embodied component could be
anchored by Paul Piff (UC Irvine), who has published on awe-induced small-
self effects and prosocial behaviour (Piff et al., 2015, N = 1,500 across
5 studies, d ≈ 0.35 for awe → small-self → prosociality). Alternatively,
the existing roster can cover it if Keltner takes primary on both awe
templates with Friston as complement.

## ISSUE 4: IE-DPT Constraint Is Present But Incomplete

C-05 requires IE-DPT four-level gradient position for each template. Good.
But CROSSCUT-I has a unique IE-DPT obligation: the AX templates are not
themselves mechanisms at a single IE-DPT level — they are meta-parameters
that MODIFY mechanisms at all four levels. AX_DOSE_RESPONSE_007, for example,
specifies how the dose-response curve differs for Level 1 (implicit, steep
habituation) vs. Level 3 (explicit, slower habituation) processes. The IE-DPT
specification for AX templates should indicate which IE-DPT levels the axiom
modifies and whether the axiom's parameters vary by level.

**Action**: Expand C-05 to include:

> For AX-series templates: specify which IE-DPT levels the axiom modifies
> and whether parameter values are level-dependent (e.g., habituation rate
> may differ for Level 1 implicit processes vs. Level 3 explicit processes).

---

# 3. Moderate Issues

## ISSUE 5: Crucible Debate 2 (Individual Differences) — Missing the Most Important Dimension

The debate as framed (trait-based vs. context-dependent individual differences)
is reasonable but misses the most consequential individual-difference
dimension for architectural application: **neurodiversity**. Autism spectrum,
ADHD, sensory processing sensitivity (Aron & Aron, 1997), and misophonia all
produce dramatically different environmental responses that are not captured
by Big Five trait moderators. A person with sensory processing sensitivity
may experience moderate environmental stimulation as overwhelming; a person
with ADHD may require higher stimulation to achieve the same NE-driven focus.

These are not edge cases — sensory processing sensitivity alone affects an
estimated 15–20% of the population (Aron et al., 2012). Universal design
principles require that CMR templates at least acknowledge this variance.

**Action**: Add neurodiversity as an explicit dimension in
AX_INDIVIDUAL_DIFFERENCES_008 alongside Big Five traits. The template should
specify at minimum: sensory processing sensitivity (Aron & Aron, 1997),
attentional profile (ADHD-related variance in optimal NE levels), and
interoceptive sensitivity (Barrett's individual differences in interoceptive
accuracy). These do not need to be fully calibrated — THEORETICAL_DEFAULT
with a flag for future research is appropriate — but they must be structurally
present.

## ISSUE 6: Ecological Rationality Template — Uncertain Value

ER_ECOLOGICAL_RATIONALITY_001 is the template I am least confident about. The
Gigerenzer adaptive-heuristics framework is intellectually important, but its
application to architectural decision-making is genuinely unexplored (as
Cowork's Flag B acknowledges). The template risks producing a set of
speculative heuristics (e.g., "occupants use a take-the-best heuristic for
wayfinding") that sound plausible but have no empirical grounding in
architectural contexts.

The template is placed last in the calibration order (position 15), which is
appropriate — it can be trimmed if the panel runs long. But I want to be
explicit: if the Crucible cannot produce at least one mechanism step with
EMPIRICAL_COVARIANCE or better, the template should be downgraded to stub
status (Tier C) rather than receiving a speculative THEORETICAL_DEFAULT
calibration. A honest stub is better than a calibrated template built on sand.

**Action**: Add a conditional constraint:

> **C-11**: ER_ECOLOGICAL_RATIONALITY_001 must achieve at least one mechanism
> step with EMPIRICAL_COVARIANCE or higher. If the panel cannot produce this,
> downgrade to stub status (Tier C) rather than calibrating with
> THEORETICAL_DEFAULT throughout.

## ISSUE 7: VR Limitation Axiom — Needs Temporal Dimension

AX_VR_LIMITATION_012 proposes a general discount factor for VR-based evidence.
Cowork's Flag E notes that VR fidelity varies enormously and has improved
dramatically. This is correct, and it means a single discount factor is
inadequate. A VR study from 2005 (low-polygon, no haptic feedback, limited
FOV) has a very different ecological validity than a 2024 study with
photorealistic rendering, spatial audio, and thermal simulation.

**Action**: The VR limitation axiom should specify a temporal discount curve,
not a single discount factor. Something like:

- Pre-2015 VR studies: discount factor 0.5–0.6 (low ecological validity)
- 2015–2020: discount factor 0.6–0.75
- 2020–2025: discount factor 0.75–0.85
- 2025+: discount factor 0.85–0.95

These are THEORETICAL_DEFAULT ranges, but they capture the reality that VR
evidence quality is a moving target. The axiom should also specify that the
discount applies to the ARCHITECTURAL BRIDGE component of confidence, not to
the underlying neuroscience (a VR study showing amygdala activation to
threatening spaces has good neuroscience even if the architectural
generalisation is limited).

---

# 4. Minor Issues

## ISSUE 8: Template Count — 15 Becomes 17

With the AX3 awe consolidation (Decision B), the template count rises from
15 to 17. This needs to be reconciled with the GAP_PANEL_MASTER_PLAN, which
specifies 15. Cowork should add explicit justification for the two additions,
as was done for CREATIVE-I (7 vs. 5) and NEUROMOD-I (11 vs. 7).

## ISSUE 9: Friston as Expert — Potential Overreach

Karl Friston is recommended as the computational neuroscientist for cross-
domain work. His free-energy / active-inference framework is influential and
relevant, particularly for the predictive-processing templates. However,
Friston has a documented tendency toward theoretical imperialism — the free-
energy principle is presented as a unified theory of brain function, which
can overwhelm domain-specific nuances in a panel setting. The panel must be
structured so that Friston provides the computational framework without
subsuming every template into active inference.

**Action**: Add a panel-management note:

> Friston provides the computational/PP framework for CROSS templates and
> serves as complement for AX3_AWE_MECHANISM_001. The free-energy principle
> is ONE theoretical account, not the panel's organising framework. Domain-
> specific experts retain authority over their templates. The Crucible should
> test Friston's precision-weighting account against empirical dose-response
> data (Crucible 1), not default to the PP account.

---

# 5. Summary of Required Actions Before Panel Execution

| # | Issue | Action | Priority |
|---|-------|--------|----------|
| A | Panel structure | Keep unified; enforce Phase A/B hard checkpoint (C-09) | STRUCTURAL |
| B | AX3 awe templates | Include 2 (consolidate HIGH_PE + NEED_FOR_ACCOMMODATION → AWE_MECHANISM; keep SMALL_SELF). Total: 17 templates | STRUCTURAL |
| 1 | Differential-mode model | Add C-10 (operationalise across corpus; Phase A task) | REQUIRED |
| 2 | AX4 canonical specification | Upgrade to Tier A; add 17+ instance survey | REQUIRED |
| 3 | Awe expert roster | Friston as PP complement; consider Piff for SMALL_SELF | REQUIRED (if AX3 included) |
| 4 | IE-DPT for AX templates | Expand C-05: specify which IE-DPT levels each axiom modifies | REQUIRED |
| 5 | Neurodiversity in individual differences | Add SPS, ADHD, interoceptive sensitivity to AX_INDIVIDUAL_DIFFERENCES_008 | MODERATE |
| 6 | Ecological rationality conditional | Add C-11: EMPIRICAL_COVARIANCE minimum or downgrade to stub | MODERATE |
| 7 | VR limitation temporal curve | Specify era-dependent discount factors, not single value | MODERATE |
| 8 | Template count justification | Justify 17 vs. 15 from GAP_PANEL_MASTER_PLAN | MINOR |
| 9 | Friston panel management | Add note constraining free-energy-principle scope | MINOR |

---

# 6. Updated Constraint Set (C-01 through C-11)

- **C-01**: AX parameters: canonical range + domain-specific override protocol
- **C-02**: Each AX template references ≥3 prior panel implementations
- **C-03**: No AX parameter contradicts prior calibrated values without reconciliation
- **C-04**: CROSS templates specify partial-out rules with prior panel mechanisms
- **C-05**: IE-DPT four-level gradient for each template; AX templates specify which levels they modify and whether parameters are level-dependent
- **C-06**: Barrett-Craig two-stage model referenced for IC components
- **C-07**: Coburn ceiling (no single d > 0.80)
- **C-08**: AX4 canonical specification consistent with NEUROMOD-I C-12
- **C-09** (NEW): Phase A/B hard checkpoint — all 8 AX templates complete and internally consistent before Phase B begins
- **C-10** (NEW): Differential-mode model operationalised — specify optimal stimulation level for each major mechanism class
- **C-11** (NEW): ER_ECOLOGICAL_RATIONALITY_001 must achieve ≥1 EMPIRICAL_COVARIANCE step or downgrade to stub

---

# 7. A Final Note on What This Panel Must Accomplish

CROSSCUT-I is the last panel. After it completes, the CMR pipeline will have
calibrated approximately 93 templates (76 current + 17 CROSSCUT-I) covering
the full scope of the Cognitive Neuroscience for Architecture research domain.
This panel's unique obligation is not just to calibrate its own templates but
to impose coherence on the entire corpus. The AX axioms are the mechanism for
this: they define the cross-cutting parameters (dose-response, habituation,
individual differences, cultural modulation, perceived control, temporal
dynamics) that every other template uses but that no prior panel was positioned
to specify.

The risk is that the AX axioms become vague meta-commentary ("individual
differences exist and matter") rather than operationally useful parameters
("neuroticism moderates noise sensitivity with d = 0.35 ± 0.15, applicable
to all templates with acoustic mechanism steps"). Constraint C-02 (reference
≥3 prior panel implementations) is designed to prevent this, but the panel
execution must enforce specificity ruthlessly. Every AX template should
produce at least one numerical parameter range that can be retroactively
applied to the calibrated corpus.

If this panel succeeds, the CMR will be not just a collection of calibrated
templates but a coherent, cross-referenced system with explicit axioms
governing its behaviour. That is a substantial intellectual achievement.

---

*REVIEW_CROSSCUT_I_CLEARANCE.md — CMR Project*
*Reviewer: Opus/Chat (Claude Opus 4.6), February 23, 2026*
*Status: CLEARED WITH FLAGS (2 structural decisions + 7 issues, see §5)*
*Awaiting human confirmation on Decisions A and B before panel execution*
