# CVA Mathematical Formalization: Document Index

**Date**: February 27, 2026
**Status**: Complete, ready for panel review
**Total content**: 1,215 lines (formalization) + 227 lines (critical questions) = 1,442 lines

---

## Two Main Deliverables

### 1. CVA_MATHEMATICAL_FORMALIZATION_2026-02-27.md (48 KB, 1,215 lines)

**Purpose**: Rigorous mathematical response to expert panel critique. Directly addresses all panelist demands.

**Structure**:

| Section | Responds to | Length | Key Content |
|---------|------------|--------|------------|
| 1. Explicit Dynamics | Strogatz | ~200 lines | F(c,v,x,A), G(v,c,A) fully specified; Jacobian analysis; loop-gain criterion κ < 1; numerical verification |
| 2. Identifiability | Jordan | ~150 lines | Formal identifiability theorem; experimental designs (constraint manip., activity manip., cross-context); Fisher Information analysis; minimum sample requirements |
| 3. Active Inference | Friston | ~100 lines | Hierarchical generative model; free energy formulation; precision-weighting = ActivityFrame; message-passing architecture; unifies CVA with predictive coding |
| 4. Beauty Models | Barrett, Scherer | ~200 lines | Model 1 (linear), Model 2 (categorical), Model 3 (KL-divergence/cultural), Model 4 (residual-holistic); cross-cultural validation design |
| 5. ATLAS Integration | Ulrich, Dalton | ~150 lines | Two-stage projection (Feature → Constraint → Valuation → Outcome); concrete hospital example; why CVA improves prediction |
| 6. Panelist Verdicts | All | ~150 lines | What specific results would shift each panelist from DEFER → ADOPT; empirical milestones and success criteria |
| 7. Implementation | Engineering | ~100 lines | Mathematical reference, priority checklist, validation milestones |

**How to read**:
- **For Strogatz**: Start at Section 1 (subsections 1.2–1.7)
- **For Jordan**: Go to Section 2 (subsections 2.1–2.6)
- **For Friston**: See Section 3 (subsections 3.1–3.5)
- **For Barrett/Constructionism**: Read Section 4 (subsections 4.1–4.6)
- **For implementation team**: Review Section 7 and the Implementation Checklist

---

### 2. CVA_QUESTIONS_FOR_CHAT_2026-02-27.md (15 KB, 227 lines)

**Purpose**: Seven precisely formulated critical questions that require deeper domain expertise. These are the hardest remaining problems that internal analysis cannot resolve.

**Questions**:

| # | Title | Domain | Why It's Critical |
|----|-------|--------|------------------|
| 1 | Precision Weighting Under Active Inference | Predictive coding | Determines if ActivityFrame modulates precision (unified inference) or if valuations themselves change (separate valuations) |
| 2 | Pre-Valuation Perception | Constructionist psychology | Determines if constraints are truly pre-valuation (separability valid) or if perception is valuation-laden from the ground up |
| 3 | Neural Separability of BelongingValue/IdentityValue | Neuroscience | Determines if the 9 valuations are neurally real (distinct OFC subregions) or post-hoc interpretations of general value |
| 4 | Irreducible Gestalt Properties in Beauty | Aesthetic theory | Determines if beauty is decomposable into dimensions (supports CVA) or irreducibly holistic (contradicts CVA) |
| 5 | Cultural Variation in Valuation Structure | Cultural psychology | Determines if culture modulates weights (universal dimensions) or restructures the space itself (culture-specific dimensions) |
| 6 | Feedback Mechanism for Constraint Perception | Neuroscience | Determines which mechanism (precision, prior, attention) explains how goals bias perception, and its empirical effect size |
| 7 | Temporal/Embodied Aspects | Phenomenology, embodied cognition | Determines if CVA's static model captures architecture's temporal unfolding and embodied experience, or if these are irreducibly left out |

**How to use**:
- Pass these to Chat or specialized consultants before implementation begins
- Use answers to refine CVA model assumptions
- Identify where empirical work needs to validate theoretical claims

---

## How These Documents Relate to the Expert Panel

**Panel Feedback** (from EXPERT_PANEL_CVA_FULL_2026-02-27.md):
- 0 votes for FULL ADOPTION
- 10 votes for PARTIAL ADOPTION (with conditions)
- 2 votes for DEFER (Strogatz, Jordan)

**This formalization addresses the conditions**:

1. **Strogatz's DEFER condition**: "Specify the dynamics fully. Show me F and G."
   - ✓ Section 1 provides full F and G with numerical verification

2. **Jordan's DEFER condition**: "Run identifiability experiments."
   - ✓ Section 2 provides formal experiment designs and feasibility

3. **Barrett's PARTIAL condition**: "Build in cultural contingency from the start."
   - ✓ Section 4 provides KL-divergence (cultural) model of beauty

4. **Friston's PARTIAL condition**: "Interpret as abstractions of unified inference."
   - ✓ Section 3 reformulates CVA as hierarchical generative model with active inference

5. **Ulrich's PARTIAL condition**: "Validate empirically."
   - ✓ Section 6 specifies what empirical results would move verdicts

---

## Implementation Timeline

**If panel approves this formalization**:

| Phase | Duration | Deliverable | Success Metric |
|-------|----------|-------------|-----------------|
| 1: Math verification | 2–4 weeks | Formal proof document, code for F/G/Jacobian | κ < 0.5 for realistic parameters |
| 2: Identifiability | 4–8 weeks | Pilot constraint-manipulation experiment | Constraint recovery r ≥ 0.75 |
| 3: Beauty models | 8–16 weeks | Cross-cultural beauty study (USA, Japan) | Model 3 or 2 outperforms Model 1 |
| 4: Template reclassification | 12–16 weeks | 20-template pilot reclassification | ≥90% feature retention, outcome prediction maintained |
| 5: Panel reappraisal | Week 18 | Panel votes on partial adoption | Move from DEFER → ADOPT PARTIALLY |

---

## Key Assumptions Documented

**This formalization makes explicit**:

1. **Timescale assumption**: τ_c = 100–500 ms, τ_v = 1–5 s (standard in predictive processing)
2. **Feedback assumption**: ε_fb = 0.08–0.25 (weak feedback, supporting separability)
3. **Coherence assumption**: γ = 0.15 (moderate cultural/group influence)
4. **Nine-dimension assumption**: Universal valuation structure (refutable by Kitayama's cross-cultural work)
5. **Linear-in-V beauty assumption**: B ≈ β^T v, but presented alongside categorical and KL-divergence alternatives

**Each can be validated or refuted empirically** (see Section 6).

---

## For David's Decision-Making

**This formalization:**
- ✓ Answers Strogatz's "show me F and G" directly
- ✓ Proposes explicit identifiability experiment that Jordan can evaluate
- ✓ Incorporates Friston's active inference framework
- ✓ Includes Barrett's cultural constructionism via KL-divergence model
- ✓ Provides integration path with current ATLAS (Section 5)
- ✓ Identifies remaining unknowns clearly (7 critical questions)

**Recommendation**: Circulate this formalization to the panel with a note: *"Based on your feedback, here is the full mathematical specification CVA requires for empirical validation. These documents (1) answer your immediate technical demands and (2) identify what empirical work comes next."*

---

**Status**: READY FOR PANEL CIRCULATION
**Next action**: Share with panel; gather feedback on formalization completeness before proceeding to Phase 1 (mathematical verification)

