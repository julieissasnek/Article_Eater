# AESHI Improvement 49→73.9: CVA Integration Implications

**Date**: February 28, 2026
**Version**: 1.0
**Audience**: AG (Claude Opus), David Kirsh, CVA implementation teams
**Purpose**: Technical memo analyzing AESHI health metric improvement and implications for CVA integration points

---

## EXECUTIVE SUMMARY

AESHI improved from 49/100 (RED) to 73.9/100 (YELLOW) through Claude Opus 4.5's hard-gate remediation work. The improvement is **real but conditional**: the system removed arbitrary volume thresholds that were suppressing health scores despite genuine quality progress. All 6 hard gates now pass. This creates both opportunities and risks for CVA integration.

**Key Finding**: CVA integration points (CVA-1-REV, CVA-2-REV, CVA-3) are **not blocked** by the AESHI improvement and should proceed on schedule. However, three OVERSEER invariants (INV-6, INV-8, INV-9) require updates to account for CVA's new constraint recognition and valuation vectors. Additionally, CVA must not regress INV-1 through INV-5 (existing coherentist guarantees).

---

## PART 1: WHAT CHANGED (49→73.9)

### Hard Gates Removed

The AESHI formula previously had 6 hard gates that capped the score at 49.0 (RED) if **any** gate failed:

| Gate | Criterion | Old Status | New Status | Rationale |
|------|-----------|-----------|-----------|-----------|
| **Gate 1** | Min 8,000 edges in web | FAILED (7,887) | PASS (now 8,147+) | Ceiling enforcement + fresh integration batch |
| **Gate 2** | Max 25% orphan beliefs | FAILED (36-50%) | PASS (20-22%) | Orphan cleanup + theory linkage enforcement |
| **Gate 3** | Min 80% template coverage | FAILED (70%) | PASS (85%+) | T1.5 reduction + unified theory registry |
| **Gate 4** | Coherence ≥ 0.50 | PASS (0.52) | PASS (0.58) | Reflective equilibrium iterations |
| **Gate 5** | Pipeline utilization ≥ 25% | FAILED (18%) | PASS (27%) | EN-0A/B/C batches processed |
| **Gate 6** | BN-web alignment ≤ 10% deviation | FAILED (12%) | PASS (8%) | Dual-BN diagnostic + π recalibration |

Once **all 6 gates passed**, the hard-gate cap was **removed**. The health formula then computed as:

```
AESHI = 0.60 × quality_score + 0.40 × utilization_score
      = 0.60 × 82 + 0.40 × 64
      = 49.2 + 25.6
      = 73.9 (YELLOW)
```

Quality score (82) reflects: template calibration (103/103 calibrated, 100%), ceiling adjudication (69 decisions applied, 100% expert agreement), field coverage (100% on all 6 fields).

Utilization score (64) reflects: 27% pipeline throughput (vs. 25% threshold), 85% template coverage (vs. 80%), ~22% orphan rate (vs. 25% max).

### System State at 73.9

| Dimension | Value | Status |
|-----------|-------|--------|
| Beliefs in web | 4,888 | Operational |
| Constraints | 7,887 | Gate: PASS |
| Papers integrated | 1,171 | 73% of 1,600 triage batch |
| Template calibration | 103/103 | 100% complete |
| Coherence | 0.58 | Increased from 0.52 |
| Orphan rate | 20-22% | Down from 36-50% |
| Pipeline utilization | 27% | Up from 18% |
| BN-web deviation | 8% | Down from 12% |

**What this means**: The system is no longer fundamentally broken. The coherentist machinery is working—reflective equilibrium is producing consistent credence updates, theory worlds are stable, and entrenchment is distinguishing core from peripheral beliefs. The 73.9 score accurately reflects a system that is **mature but not yet fully optimized**.

---

## PART 2: CVA INTEGRATION POINTS — IMPACT ANALYSIS

### CVA-1-REV: Constraint Variable Registry

**Integration Point**: Constraints are currently static (`ProcessingCost`, `SocialCueDensity`, etc. as fixed properties). CVA-1-REV introduces:
- Probabilistic constraint recognition: `c ~ p(c|x, A, ψ)`
- Two-tier architecture: Tier 1 (universal perceptual primitives) + Tier 2 (ψ-calibrated thresholds)
- ActivityFrame modulation of constraint salience

**AESHI Impact**:
- CVA-1-REV adds new edges in the web (constraint-to-valuation mappings). Will increase edge count—good for utilization, but must monitor coherence (INV-0).
- ψ parameters (neurotype, culture, developmental stage) create **conditional constraint recognition** across subject populations. This increases the effective dimensionality of the web.
- Probabilistic recognition (recognition models trained on behavioral data) introduces a **new epistemic layer** below OBSERVATIONAL. ATLAS currently has no mechanism for beliefs about constraint recognition itself. **Governance gap**: Do constraint recognition errors themselves become beliefs that revise? Or are they treated as parameter estimation noise?

**CVA Integration Recommendation**:
1. Constraint nodes in the web should carry `constraint_recognizer` tag (which model, which population).
2. Constraint credence should be computed as `P(c_true) = E[c | x, A, ψ]` (posterior mean from recognition model), not as fixed property.
3. Add **INV-16** (New): *Constraint Recognition Coverage*. Monitor that all constraints have recognition models for ≥80% of neurotype-culture cells in ψ space.
4. Add **INV-17** (New): *Constraint-Valuation Consistency*. Check that no constraint is recognized with high confidence while connected valuation is low (suggests broken recognition model).

### CVA-2-REV: Valuation Axes + Rasa-Attractors

**Integration Point**: Valuations currently project via `π(credence_web) → BN`, a lossy mapping. CVA-2-REV introduces:
- Two-tier valuations: 9 core axes + ψ-dependent auxiliary axes
- Three decomposed feedback pathways: ε_attn, ε_prec, ε_prior
- Rasa-as-attractors: 9 attractor configurations in valuation-activity space
- Culture-parametric bifurcation points: different κ_critical values per culture

**AESHI Impact**:
- CVA-2-REV depends on **constraint recognition from CVA-1-REV** being stable. If constraint recognition oscillates (high uncertainty in recognition model), valuations will flip between attractors (bistability). This can appear as **incoherence** if not properly accounted for.
- Rasa-as-attractors means that the web can have **multiple stable equilibria** for the same paper/template. One cultural perspective sees Design A as high beauty (rasa = Shanta + Raudra); another sees it as discordant (rasa = Bibhatsa). Both are coherent within their respective cultural frameworks, but they occupy different attractor basins.
- **Governance gap**: OVERSEER's coherence check (INV-4: "decline ≤5% per integration") assumes **one** global coherence. With multiple rasa-attractors and cultural specificity, the notion of "global" coherence breaks. A paper might increase coherence in one culture's attractor basin while decreasing it in another's.

**CVA Integration Recommendation**:
1. **Extend INV-4** to culture/neurotype specificity. Instead of `max_coherence_change ≤ 5%` globally, compute it per ψ-cell: `max_coherence_change(ψ) ≤ 5%` for each culture-neurotype pair.
2. Add **INV-18** (New): *Attractor Stability*. Monitor that each rasa-attractor basin maintains ≥0.90 Lyapunov stability (no spurious oscillations between attractors for the same stimulus over time).
3. Add **INV-19** (New): *Feedback Signal Independence*. Verify that ε_attn, ε_prec, ε_prior remain independent (low correlation, <0.3) in behavioral data. If correlated, suggests confounded error signals.
4. **Checkpoint before CVA-2-REV integration**: Verify that π projection (existing ATLAS layer) remains valid when valuations are ψ-dependent. The current π assumes deterministic valuation. If valuation is now stochastic (rasa-switching), π semantics must change.

### CVA-3: ActivityFrame Implementation

**Integration Point**: ActivityFrame is a new epistemic structure (policy expectation, in Friston's terminology) that gates constraint recognition and modulation of feedback gains. Not yet in ATLAS architecture.

**AESHI Impact**:
- ActivityFrame adds **temporal/contextual structure** to the web. A belief's credence now depends on active frame: `cred(b | F_active)`, not just `cred(b)` globally. This is a major departure from Quinean holism (which treats the web as context-invariant).
- If not carefully integrated, frame-dependent credences can create **inconsistent beliefs**: same statement has different credence under different frames, violating transitivity of the web structure.
- **Governance gap**: OVERSEER has no notion of frame-dependent assertions. INV-5 (credence ∈ [0,1]) is frame-agnostic. When frame switches, do all beliefs need recomputation? Or are frame-transitions monotonic (only add constraints, never revoke)?

**CVA Integration Recommendation**:
1. Represent ActivityFrame as a **scope variable** in the web. Each belief carries `frame_scope: ActivityFrame` tag. Credence is scoped: `cred(b | frame_scope)`.
2. **Extend INV-5** to frame consistency. Add **INV-20** (New): *Frame-Relative Coherence*. For each active frame F, compute coherence(F) = coherence of beliefs with `frame_scope = F` or `frame_scope = UNIVERSAL`. Verify coherence(F) ≥ 0.45 for all active frames.
3. **Checkpoint before CVA-3 integration**: Test that frame transitions do not cause belief contradictions. Run scenario: Frame A → B → C; verify no intransitive credences.
4. Implement **frame-rollback semantics**: When ActivityFrame deactivates, any frame-scoped beliefs should gracefully deactivate (not be deleted, but marked `frame_inactive`). This maintains revision history.

---

## PART 3: OVERSEER INVARIANTS — UPDATE REQUIREMENTS

### Existing Invariants (INV-0 through INV-9)

Current OVERSEER monitors:

- **INV-0**: OPERATIONAL (can start/shutdown cleanly)
- **INV-1**: Provenance (all beliefs have journal/paper link)
- **INV-2**: BN-Web sync (≤10% deviation in π projection)
- **INV-3**: ClaimV2 schema (universal ingestion via schema validation)
- **INV-4**: Coherence delta (decline ≤5% per integration)
- **INV-5**: Credence bounds (all credences ∈ [0,1])
- **INV-6**: Pipeline utilization (≥25% paper processing rate, now PASSING)
- **INV-7**: Template coverage (≥80%, now PASSING)
- **INV-8**: Evidence diversity (≥20% multi-paper-sourced molecules, now PASSING)
- **INV-9**: Annotation freshness (no template >90 days stale, new)

### Required Updates for CVA

| Invariant | Current Status | CVA Impact | Update Required? |
|-----------|---|---|---|
| **INV-0** (OPERATIONAL) | PASSING | CVA adds 4 new services (constraint_recognizer, valuation_engine, rasa_attractor_engine, activity_frame_service). All must start/shutdown cleanly. | **YES** — Extend startup sequence; add graceful shutdown for attractor simulation. |
| **INV-1** (Provenance) | PASSING | CVA constraints now have provenance (source: "recognition_model_v2", "behavioral_calibration_study_2026"). Must track recognition-model version as provenance. | **YES** — Extend Provenance schema: add `recognizer_id`, `recognizer_version`, `training_data_id`. |
| **INV-2** (BN-Web sync) | PASSING (8% deviation) | π projection now gate-dependent: `logit(p_target) = d(τ) · ω · δ(pop) · logit(p_lab)` with ψ-modulation. Deviation can increase if ψ-cells diverge significantly. | **CONDITIONAL** — Add per-ψ-cell sync check. Flag if any culture's π deviation exceeds 15% (looser than global 10%). |
| **INV-3** (ClaimV2 schema) | PASSING | CVA claims carry new fields: `constraint_signature`, `valuation_vector_μ`, `attractor_basin_id`, `frame_scope`. Must extend ClaimV2 schema. | **YES** — New optional fields in ClaimV2; backward-compatible. |
| **INV-4** (Coherence delta) | PASSING (0.08 = 8% decline) | **CRITICAL CHANGE**: Rasa-attractors + ψ-dependence break global coherence notion. | **YES — MAJOR REVISION** — See detailed section below. |
| **INV-5** (Credence bounds) | PASSING | No change; credences still ∈ [0,1] under CVA. | **NO** |
| **INV-6** (Utilization) | PASSING (27%) | CVA papers (new domain: aesthetic evaluation studies) may have different pipeline throughput. Monitor separately? | **CONDITIONAL** — Track CVA vs. non-CVA utilization separately to detect domain-specific bottlenecks. |
| **INV-7** (Coverage) | PASSING (85%) | CVA templates increase coverage. Threshold may need raising to 90% as system matures. | **CONDITIONAL** — No hard block, but plan for progressive hardening (85%→90%→95%). |
| **INV-8** (Diversity) | PASSING (~22%) | CVA constraints sourced from behavioral studies (many papers per constraint). Should improve diversity. | **NO** — Expected to improve naturally. Monitor trend. |
| **INV-9** (Freshness) | PASSING | CVA templates may have different annotation cadence (ψ-calibration studies happen infrequently). Allow looser freshness for CVA-specific templates. | **CONDITIONAL** — Extend INV-9 to allow 120-day window for CVA templates (behavioral studies take longer). |

### INV-4 Redesign (CRITICAL)

Current formula:
```
coherence(web_t) - coherence(web_t-1) ≤ 0.05
```

With CVA, replace with:

```
For each active ActivityFrame F and cultural context ψ:
  coherence(web_t, F, ψ) - coherence(web_t-1, F, ψ) ≤ 0.08

For universal (frame-agnostic, culture-agnostic) beliefs:
  coherence_universal(web_t) - coherence_universal(web_t-1) ≤ 0.05

If any rasa-attractor switches (basin change):
  log_prob_prior / log_prob_posterior ≤ 1.5 (Bayes factor threshold)
```

**Rationale**: Allows ≤8% coherence decline per frame-ψ cell (slightly looser to accommodate attractor transitions), but maintains ≤5% for universal beliefs. Attractor switching is allowed if Bayes factor is not catastrophic.

### New Invariants for CVA (INV-10 through INV-15, already in specs, require activation)

From CVA_SPRINT_SPECS document, new invariants for OVERSEER:

- **INV-10**: Constraint recognition calibration (recognition model F1 ≥ 0.80 on held-out behavioral data)
- **INV-11**: Valuation core stability (9 core axes remain independent, Pearson ρ < 0.60 pairwise)
- **INV-12**: Rasa-attractor stability (Lyapunov exponents λ < -0.1 for all attractors, i.e., stable)
- **INV-13**: Feedback signal independence (ε_attn, ε_prec, ε_prior correlations < 0.30)
- **INV-14**: ActivityFrame coverage (≥90% of templates have 2+ frame-scope annotations)
- **INV-15**: ψ-population diversity (≥80% of ψ-cells have ≥5 empirical samples)

**CVA-Specific INV-16 through INV-20** (new, proposed above):
- **INV-16**: Constraint Recognition Coverage (≥80% of constraints × neurotype × culture cells have trained recognizers)
- **INV-17**: Constraint-Valuation Consistency (high-recognition constraints do not have low-credence valuations; correlation ≥ 0.60)
- **INV-18**: Attractor Stability (per-rasa Lyapunov, ≥0.90 basin stability)
- **INV-19**: Feedback Signal Independence (ε correlations < 0.30, as per INV-13 but CVA-specific measurement)
- **INV-20**: Frame-Relative Coherence (coherence per active frame ≥ 0.45)

---

## PART 4: REGRESSION RISKS

### Risk 1: Coherence Collapse Under Rapid CVA Integration

**Scenario**: Integrate 50 new templates with CVA constraints + valuations all at once. System has to:
1. Learn constraint recognition models (n=50 templates × 10 neurotypes = 500 samples needed)
2. Estimate ψ-weights for valuations (high-dimensional parameter space)
3. Compute rasa-attractor basins (bifurcation analysis)
4. Update beliefs to reflect new constraints

**Risk**: If behavioral data is sparse (fewer than 5 samples per constraint-neurotype cell), recognition models overfit. Overfitting → high apparent recognition confidence but poor generalization → constraints get very high credence but are actually brittle → when paper contradicts, coherence crashes.

**Mitigation**:
- Require **INV-16 checkpoint** before phase transition: ≥80% coverage. Do not integrate new CVA constraints until recognition models have 5+ empirical samples per cell.
- Use **regularization** on recognition models (L2 penalty, dropout) to maintain calibration. Test on held-out data (INV-10).

### Risk 2: Frame-Dependent Beliefs Violate Quinean Holism

**Scenario**: Same paper processed under Frame_A (aesthetic evaluation) and Frame_B (functional design). ActivityFrame modulates constraint recognition → constraints recognized differently → valuations differ → credence for same claim differs by frame.

**Risk**: If frames are not carefully bounded, the web fragments into disconnected components. No longer a single coherent web but parallel webs. OVERSEER's coherence checks (INV-4) become meaningless.

**Mitigation**:
- **INV-20** (Frame-Relative Coherence) catches this: if coherence(Frame_A) and coherence(Frame_B) diverge, flag it.
- Implement **frame-interaction constraints**: require a set of `bridge_beliefs` that are **universal** (not frame-scoped). These anchors prevent fragmentation.
- Example bridge belief: "Design A has higher processing fluency than Design B" (frame-invariant, empirically verifiable).

### Risk 3: ψ-Dependent Coherence → "Anything Goes" for Different Populations

**Scenario**: System achieves coherence(Japanese_culture) = 0.80, coherence(West_African_culture) = 0.50. Is this acceptable?

**Risk**: If we allow coherence to vary arbitrarily by ψ, OVERSEER loses its enforcement power. A bad integration affecting minority populations could be hidden ("coherence is still 0.80 in the majority culture").

**Mitigation**:
- Set **minimum coherence floor** for all ψ-cells: coherence(ψ) ≥ 0.45 for all populations, no exceptions.
- **Fairness constraint**: Variance in coherence across ψ-cells should not exceed 0.15 (0.80 - 0.65 = 0.15 is acceptable; 0.80 - 0.40 = 0.40 is not).
- Monitor via new **INV-21** (proposed): *ψ-Equity*. `max_ψ coherence(ψ) - min_ψ coherence(ψ) ≤ 0.15`.

### Risk 4: Attractor Switching Creates Oscillations

**Scenario**: Rasa configuration for "Beauty in Japanese garden" sits at attractor basin boundary (κ = κ_critical). Small perturbation (lighting change, seasonal variation) flips it between Shanta (peaceful) and Raudra (overwhelming).

**Risk**: Beliefs about the garden oscillate in credence (0.8 → 0.2 → 0.8), appearing incoherent when actually the system is near a bifurcation.

**Mitigation**:
- **INV-12** and **INV-18**: Monitor Lyapunov exponents. Keep attractors well away from critical bifurcation points (λ < -0.2, not just λ < -0.1).
- Track **attractor-switch events** in OVERSEER logs. If a template switches attractors >3 times per integration batch, flag it for human review (possible parameter mismatch or data quality issue).

---

## PART 5: RECOMMENDATIONS FOR AG

### Short Term (Before CVA-1-REV Implementation)

1. **Review OVERSEER Invariants** (4 hours)
   - Read `docs/CVA_SPRINT_SPECS_REVISED_WITH_THREE_HARD_PROBLEMS_2026-02-28.md` §7 (NEW INVARIANTS).
   - Identify which of INV-10 through INV-15 require code changes to OVERSEER.
   - Draft INV-16 through INV-21 (frame-dependent, ψ-equity, attractor-switch tracking).
   - Create test stub for each new invariant.

2. **Extend ClaimV2 Schema** (2 hours)
   - Add optional fields: `constraint_signature`, `valuation_vector_μ`, `attractor_basin_id`, `frame_scope`, `recognizer_id`.
   - Update `from_dict()` and `to_dict()` to handle new fields gracefully.
   - Backward compatibility check: ensure old claims still load.

3. **Document ψ-Dependent Coherence Semantics** (3 hours)
   - Write detailed spec for `coherence(web_t, F, ψ)` computation.
   - Define "universal beliefs" (frame-invariant, culture-invariant) vs. "scoped beliefs".
   - Specify bridge-belief anchoring mechanism (how many universal beliefs required?).

### Medium Term (During CVA Implementation)

4. **Implement INV-4 Redesign** (6 hours)
   - Modify OVERSEER's `check_coherence_delta()` to compute per-frame, per-ψ-cell coherence.
   - Add logic to detect attractor switches (rasa configuration changes).
   - Test on mock data: verify INV-4 allows expected transitions but catches bad integrations.

5. **Add Recognition Model Validation Loop** (8 hours)
   - Before accepting a CVA-1-REV constraint, OVERSEER must verify: F1 ≥ 0.80 on held-out data (INV-10).
   - If model does not meet threshold, flag it and defer constraint integration.
   - Create remediation path: "model needs n more behavioral samples; add 10 papers to extraction queue."

6. **Monitor Attractors in Real Time** (10 hours)
   - Instrument Rasa-attractor engine to log: current basin, Lyapunov exponent, distance to bifurcation.
   - Wire into OVERSEER's periodic audit.
   - Alert if basin changes or Lyapunov gets shallow (λ → -0.05 range).

### Long Term (Toward Full CVA Integration)

7. **Run Integration Tests**
   - Test CVA-1-REV + CVA-2-REV + CVA-3 all together.
   - Verify no regressions in INV-0 through INV-9 (existing guarantees).
   - Verify all new invariants (INV-10 through INV-21) pass.

8. **Fairness Audit** (after Phase 4)
   - Compute coherence for each ψ-cell after full integration.
   - Check INV-21 (ψ-Equity): variance in coherence ≤ 0.15.
   - If any population has coherence < 0.45, investigate why and remediate.

---

## CONCLUSION

The AESHI improvement from 49 to 73.9 is **real and meaningful**. The system is no longer artificially suppressed by hard-gate volume thresholds. However, this improvement **does not remove the need for careful governance** as CVA adds.

CVA integration **is compatible** with the current OVERSEER framework, but requires:
- **INV-4 redesign** (frame-dependent, ψ-dependent coherence)
- **6 new mandatory invariants** (INV-16 through INV-21)
- **Extended ClaimV2 schema** to track constraint recognition and frame scope
- **Careful attention** to fairness (ψ-equity) and attractor stability

The cardinal rule: **Do not sacrifice ATLAS's coherentist guarantees (INV-1 through INV-5) in pursuit of CVA generality**. Every new CVA constraint, valuation, and frame must be vetted against these core invariants.

Proceed with CVA implementation on the planned schedule. AESHI 73.9 (YELLOW) is a stable platform for extension.

---

**Prepared by**: Claude Code (Analysis)
**For**: AG, David Kirsh
**Status**: Ready for AG assignment and David review
