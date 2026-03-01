# OPUS POST-PANEL REVIEW — NEUROMOD-I (S-07)
## Reviewer: Opus/Chat (Claude Opus 4.6)
## Date: February 23, 2026
## Inputs reviewed:
##   1. NEUROMOD_I_Panel_Output.md (2,588 lines, 11 templates)
##   2. REVIEW_NEUROMOD_I_post.md (Cowork self-review)
##   3. REVIEW_T29_VERIFICATION.md (T29 dedicated verification)

---

# VERDICT: CLEARED — Best Panel in the Pipeline

---

# 1. Executive Assessment

This is the strongest panel the CMR pipeline has produced. It surpasses MUSIC-I
— which held the previous quality benchmark — in three respects: theoretical
depth (the five-neuromodulator computational taxonomy from Dayan's framework
gives the panel a formal spine that MUSIC-I lacked), constraint discipline
(12/12 constraints satisfied with zero violations), and epistemic honesty (17
THEORETICAL_DEFAULTs explicitly flagged, each individually justified, with T29
carrying the lowest template confidence in the panel at 0.45 — a correct
reflection of compounded uncertainty rather than false precision).

The panel output, the self-review, and the T29 verification are all
well-executed. Cowork resolved all 8 pre-panel clearance flags, added the
serotonergic template per Issue 3, reframed the Crucible debates per Issues 4
and 5, and produced the T29 standalone verification that my clearance review
recommended. The crash-resilience protocol was followed with incremental saves
at five checkpoints. The output is 2,588 lines — the largest in the pipeline
— and the density is appropriate to the subject matter.

I have six items for the record, two of which require action. None are
blocking.

---

# 2. What the Panel Does Well

## 2.1 The Dayan Computational Taxonomy

The organising framework — DA encodes reward PE, NE encodes unexpected
uncertainty (volatility), ACh encodes expected uncertainty (stochasticity),
5-HT encodes aversive prediction and mood bias — comes from Yu & Dayan (2005)
and Dayan & Huys (2009). This is the right theoretical scaffold. It gives each
neuromodulator a computationally distinct role, which prevents the mechanism
chains from degenerating into vague "this neurotransmitter does stuff"
narratives. The architectural translations are clean: DA responds to reward
features, NE to environmental change, ACh to sensory complexity, 5-HT to
daylight-mediated valence. Each modulator has a different optimal design lever.

## 2.2 The Crucible Debates

All three debates produced concrete, usable deliverables rather than abstract
theoretical resolutions:

**Crucible 1** (wanting vs. liking): The dual-parameter model with 5-HT
moderation is a genuine synthesis. Berridge's distinction between RPE-driven
wanting (which habituates) and incentive-sensitised wanting (which can
increase with repeated exposure) provides a mechanistic account of place
attachment that the CMR previously lacked. The RPE habituation curve
(Schultz's data: 50% reduction on second exposure, ~80% by fourth) gives
this a quantitative backbone. The panel correctly identifies that sustained
engagement requires either ongoing unpredictable reward or cue-reward
sensitisation — two distinct architectural strategies.

**Crucible 2** (explore vs. exploit): The task-dependent optimal novelty
framework, with NE-ACh interaction, converges with CREATIVE-I's differential-
mode model. This cross-panel convergence is significant (addressed in §4
below). The daylight-NE baseline interaction is a nice detail — morning
bright light shifts the explore/exploit balance toward exploration
independently of spatial configuration.

**Crucible 3** (T29 boundary conditions): The 75th-percentile threshold with
quantified error estimates (15–25% underestimation for single-subsystem
overload, 10–20% for 3+ simultaneous) is exactly what I asked for in the
clearance reframing. This is mature epistemic practice — the panel
acknowledges where its model fails and estimates the magnitude of failure.

## 2.3 The IE-DPT Four-Level Implementation

This is the deepest IE-DPT implementation in the pipeline. The four levels
map with striking clarity onto the neuromodulatory systems, and the
architectural actionability analysis is the most practically useful IE-DPT
output we have produced: Levels 3 and 4 (explicit modulation of implicit +
AX4 cross-cutting) are the most architecturally actionable because design can
directly support the cognitive processes at these levels (safety appraisal,
perceived control affordances). Level 1 processes can only be influenced by
modifying physical parameters. This is a design-relevant insight that
generalises beyond NEUROMOD-I.

## 2.4 The Serotonergic Addition

Cools as primary anchor for NM7 was the right choice. The 5-HT template
fills a genuine gap — without it, T29 was missing the mood-valence pathway
that connects daylight to occupant satisfaction. The "sick building syndrome"
mechanism (inadequate daylight → chronic low 5-HT → negative processing bias →
amplified complaint reporting) is speculative but plausible, and the template
correctly carries it at EMPIRICAL_COVARIANCE with confidence 0.45.

---

# 3. Items for the Record — No Action Required

## 3.1 The 17 THEORETICAL_DEFAULTs — Assessment

Cowork's self-review (Issue 3) asks whether 17 THEORETICAL_DEFAULTs is too
many and whether compounded uncertainty renders T29 practically irrelevant.
The answer is no — but it is the right question to ask.

The 17 defaults break down as follows: 7 are T29 weights (all w = 1.0,
confidence 0.40), which is an acknowledged simplification that cannot be
resolved without longitudinal biomarker studies. The remaining 10 are
distributed across the other templates and mostly reflect the long bridging
distance from laboratory neuroscience (primate single-unit, human fMRI,
pharmacological manipulation) to architectural application. Each default is
individually justified and none is avoidable given the current evidence base.

The critical question is whether T29's composite output (0.45 confidence,
additive model, equal weights) is useful for architectural practice. The
answer is a qualified yes. T29 does not produce a precise numerical allostatic
load score — and it should not claim to. What it does produce is a structured
inventory of the neuromodulatory pathways through which buildings impose
chronic demands on occupants, with explicit identification of which pathways
are most modifiable by design (Levels 3 and 4) and which are most
consequential (HPA and NE, per AX4 moderation). This structural contribution
has value independent of the precise numerical calibration. The 17 defaults
are honest markers of where the numbers need work; the architecture of the
model is sound.

## 3.2 NM4 (Incentive Sensitisation) — Weakest Template

Cowork flags NM4 at confidence 0.40, ANALOGICAL warrant, as the weakest
template. This is correct. The scaling from drug-related incentive
sensitisation (Robinson & Berridge, 2008) to moderate environmental rewards
(repeated cue-reward pairing in architectural contexts) is a genuinely long
analogical bridge. There is no direct evidence that architectural cues undergo
incentive sensitisation in the Berridge sense.

However, I do not recommend demotion to stub status. The construct fills a
necessary gap: NM1 (RPE) explains initial novelty-driven approach but predicts
habituation; NM4 (sensitisation) explains why approach can INCREASE with
familiarity — the mechanism for place attachment. Without NM4, the CMR has no
account of why people develop deep loyalty to buildings they have visited
hundreds of times. The template should remain at 0.40 ANALOGICAL with a clear
flag that this is the least empirically grounded mechanism in the panel. If
environmental sensitisation studies emerge (e.g., fMRI of cue-reward pairing
in familiar vs. novel architectural contexts), the confidence could be revised
upward substantially.

## 3.3 Lambert et al. (2002) — Single-Study Foundation for 5-HT Pathway

Cowork's self-review (Issue 6) correctly flags that the daylight → 5-HT
synthesis pathway rests heavily on Lambert et al. (2002, N = 101, post-mortem
data). This is a methodologically unusual study — post-mortem measurement of
5-HIAA in brain tissue correlated with ante-mortem sunlight exposure. The
correlation (r = 0.56) is strong, and the physiological mechanism (light →
retinal pathway → raphe → tryptophan hydroxylase activation) is plausible
based on animal studies (Lowry et al., 2009). But independent replication with
in-vivo methodology in humans remains lacking.

This is already captured in NM7's confidence (0.45, EMPIRICAL_COVARIANCE) and
the THEORETICAL_DEFAULT flag. No action needed now; flag for the next
systematic literature review.

## 3.4 The Social → Inflammation Mild Double-Count

The T29 verification document honestly identifies a mild overlap: social
isolation contributes to inflammation (Cacioppo pathway), but social isolation
and inflammation enter T29 as separate additive terms. Under strict
independence, this produces a small double-count. The verification correctly
assesses this as a known limitation of the additive model, with small
practical impact because the social → inflammation cascade operates on a
weeks-to-months timescale while the acute psychosocial component is faster.
Accepted; no action.

---

# 4. Items Requiring Action

## 4.1 Differential-Mode Model — Cross-Panel Adoption Decision

Cowork's self-review (Issue 2) recommends formal adoption of the differential-
mode model as a CMR working model alongside Barrett-Craig. The evidence is now
compelling:

- CREATIVE-I established the model: low stimulation → divergent/implicit
  processing; moderate stimulation → convergent/explicit processing.
- NEUROMOD-I provides the neural mechanism: the LC-NE explore/exploit
  framework maps directly onto the differential-mode model (low NE → exploit/
  focused → convergent work; moderate NE → explore/flexible → creative work).
- The NE-ACh interaction adds precision: ACh provides expected-uncertainty
  weighting that modulates the NE-driven mode switch.

Two independent panels converging on the same framework from different
starting points (cognitive psychology in CREATIVE-I, computational
neuromodulation in NEUROMOD-I) is strong evidence for the model's validity.

**Decision: ADOPT the differential-mode model as a CMR working model.**
Same conditions as Barrett-Craig: working-model label, revision clause,
brief position statement. Each future panel should specify where its primary
mechanism falls on the stimulation-mode axis and what NE level optimises that
process.

**Action**: Produce a one-page cross-panel position statement for the
differential-mode model, analogous to the Barrett-Craig position statement.
Assign to Cowork or next Opus/Chat session. Update the Architecture
Explanation document.

## 4.2 CROSSCUT-I Scope Review

Cowork's self-review (Issue 4) notes that CROSSCUT-I has accumulated
substantial scope from prior panels. By my count:

- Original GAP_PANEL_MASTER_PLAN allocation: 15 templates
- MUSIC-I cross-template assignments: 2 (cultural conditioning moderator,
  plus at least 1 other)
- THERMAL-I cross-template assignments: 2 (thermal-acoustic interaction,
  plus 1 other)
- CREATIVE-I assignments: 2 (Aesthetic Anchoring evaluation, plus at least
  1 other)
- NEUROMOD-I assignments: 1 (restoration input cross-panel verification)

CROSSCUT-I is explicitly the meta-analytic reconciliation panel, so absorbing
cross-panel flags is its intended function. But 15 templates plus 7+
accumulated cross-panel tasks is a very large scope. The panel may need to be
partitioned or prioritised.

**Action**: Before CROSSCUT-I pre-panel clearance, produce a scope inventory
that lists all accumulated cross-panel assignments alongside the 15 planned
templates. Decide whether CROSSCUT-I can absorb everything in a single panel
or whether it should be split into CROSSCUT-Ia (meta-analytic templates) and
CROSSCUT-Ib (cross-panel reconciliation tasks). This is a pre-panel planning
task, not a NEUROMOD-I issue — but it should be flagged now so the next
session addresses it immediately.

---

# 5. T29 Verification — Opus Confirmation

The REVIEW_T29_VERIFICATION.md document is well-executed. Key findings:

- **Traceability**: All 12 input terms traced to source panels. No orphan
  terms. No terms without panel provenance. Verified.
- **Double-counting**: One mild overlap identified (social → inflammation),
  appropriately assessed as an accepted limitation. The daylight triple-pathway
  (NE alerting, 5-HT mood, chronic restoration) is verified as three distinct
  physiological mechanisms, not a true double-count. This was the most
  important check in the verification and it passes.
- **Constraint compliance**: 12/12 satisfied. Zero violations.
- **Confidence**: 0.45 — appropriate for a template that integrates 6+ uncertain
  inputs through a simplified additive model with equal weights.
- **Residual gaps**: Five gaps identified (T29_GAP1–5), all correctly assessed
  for severity and resolution path. T29_GAP3 (building-attributable AL never
  empirically isolated) is identified as a field-level gap rather than a model
  error — this is the right framing.

**T29 verification: CONFIRMED. No revisions needed.**

---

# 6. Notes for AG Extraction

David, you mentioned feeding this to AG for extraction using the general
method documented in PANEL_INTEGRATION_PROMPT.md. A few specific notes for
whoever runs that extraction:

1. **11 templates to extract** — the largest single extraction batch.
   Recommend extracting in the same order as calibration (NM1–NM10, then T29
   last) to preserve dependency structure.

2. **T29 requires special handling.** It has the most complex
   super_template_interactions of any template (receives from 6 prior panels
   + all 10 NEUROMOD-I templates). The extraction should verify that every
   cross-panel input reference resolves to a template that actually exists in
   the web of belief.

3. **The 17 THEORETICAL_DEFAULTs should all carry provenance**: panel_source =
   "NEUROMOD-I", calibration_method = "panel_calibrated", with the specific
   THEORETICAL_DEFAULT flag preserved. These are not stubs — they are
   calibrated values that happen to rely on defaults rather than direct
   empirical measurement.

4. **AX4 entries**: NM5 and NM8 both reference AX4_mod (C-12). The extraction
   should ensure that AX4 is represented in the schema per the elevation
   decision (REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md, Decision 2).
   If CC has not yet completed the AX4 schema entry (Wave 3 task, now
   triggered), the extraction should create placeholder AX4 references that
   can be linked once the schema entry exists.

5. **Constraint references**: Several templates reference specific constraints
   (C-01, C-04, C-07, C-12) in their calibration_constraint fields. These
   should be preserved in the extracted schema as provenance metadata, not
   stripped out.

---

# 7. Consolidated Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | **Adopt differential-mode model as CMR working model** — produce position statement | Cowork or Opus/Chat | HIGH |
| 2 | **CROSSCUT-I scope inventory** — list all accumulated cross-panel tasks + 15 templates; decide single panel or split | Opus/Chat (pre-panel) | HIGH |
| 3 | AG extraction of 11 NEUROMOD-I templates per PANEL_INTEGRATION_PROMPT.md (see §6 notes) | AG | MEDIUM |
| 4 | Update TRANSFER document: record NEUROMOD-I completion (11 templates, pipeline total now 76 calibrated) | Opus/Chat | MEDIUM |
| 5 | Barrett-Craig position statement (from CREATIVE-I review, still pending) | Cowork or Opus/Chat | MEDIUM |

---

# 8. Pipeline Status Update

| Panel | Templates | Status |
|-------|-----------|--------|
| STRESS-I | 3 | COMPLETE |
| SOCIAL-I | 6 | COMPLETE |
| MEMORY-I | 6 | COMPLETE |
| MULTI-I | 6 | COMPLETE |
| MUSIC-I | 13 | COMPLETE |
| THERMAL-I | 3 | COMPLETE |
| CREATIVE-I | 7 | COMPLETE |
| NEUROMOD-I | 11 | **COMPLETE — CLEARED** |
| VISUAL-I | 7 | COMPLETE (pre-pipeline) |
| LIGHT-I | 8 | COMPLETE (pre-pipeline) |
| SPATIAL-I | 6 | COMPLETE (pre-pipeline) |
| **CROSSCUT-I** | **15** | **NEXT (S-08, final panel)** |

**Pipeline calibrated**: 55 (pipeline) + 21 (pre-pipeline) = **76 templates**
**Remaining**: CROSSCUT-I (15 templates) + accumulated cross-panel tasks
**Working models adopted**: Barrett-Craig two-stage (THERMAL-I), Differential-
mode (CREATIVE-I + NEUROMOD-I convergence)
**Cross-cutting moderators elevated**: AX4 Perceived Control (structural
implementation triggered)

---

*OPUS_REVIEW_NEUROMOD_I_FINAL.md — CMR Project*
*Reviewer: Opus/Chat (Claude Opus 4.6), February 23, 2026*
*Status: CLEARED — Best panel in the pipeline*
*T29 Verification: CONFIRMED*
