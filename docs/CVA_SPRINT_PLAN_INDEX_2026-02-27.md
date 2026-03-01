# CVA Sprint Plan: Quick Index

**Full Document**: `CVA_SPRINT_PLAN_2026-02-27.md` (1,121 lines)

---

## Executive Summary (Quick View)

**Panel Verdict**: 10 ADOPT PARTIALLY, 2 DEFER, 0 FULL, 0 REJECT

**Seven Mandatory Conditions**:
1. Analytical, not causal separation
2. Explicit dynamics (F and G functions)
3. Identifiability validated empirically
4. Cultural contingency from start
5. Incremental adoption (20-template pilot)
6. Design-thinking grounded (not just prediction)
7. Track minority concerns (Strogatz, Barrett, Zumthor)

---

## The Plan at a Glance

### Phase A: Foundation (Weeks 1–6)
| Sprint | Duration | Goal | Key Deliverable |
|--------|----------|------|-----------------|
| CVA-1 | 2 weeks | Operationalize 8 constraint variables | `constraint_variables.py` + Registry doc |
| CVA-2 | 2 weeks | Define 9 valuation axes with interactions | `valuation_axes.py` + Specification doc |
| CVA-3 | 2 weeks | Build ActivityFrame module | `activity_frame.py` + 5 worked examples |

**Phase A Effort**: 31 person-days | **Code**: ~250 lines × 3 modules | **Docs**: ~2,000 lines

---

### Phase B: Pilot Validation (Weeks 7–14)
| Sprint | Duration | Goal | Key Deliverable |
|--------|----------|------|-----------------|
| CVA-4 | 3 weeks | Classify 20 templates under CVA | 20 annotations + gap report |
| CVA-5 | 2 weeks | Extend projection with goal modulation | `epistemic_projection_cva.py` + test results |
| CVA-6 | 2 weeks | Test beauty compression (3 models) | Model comparison + residual analysis |

**Phase B Effort**: 34 person-days | **Code**: ~400 lines × 2 modules | **Docs**: ~1,500 lines | **Tests**: Pass/fail on 20 templates

---

### Phase C: Empirical Design (Weeks 15–18)
| Sprint | Duration | Goal | Key Deliverable |
|--------|----------|------|-----------------|
| CVA-7 | 2 weeks | Design 3 identifiability experiments (pre-registered) | Experiment protocols + power analyses |
| CVA-8 | 2 weeks | Design cross-cultural validation study | Study protocol + cultural adaptation guidelines |

**Phase C Effort**: 22.5 person-days | **Output**: Pre-registered protocols ready for external execution | **No code changes**

---

### Phase D: Integration Decision (Weeks 19–22)
| Sprint | Duration | Goal | Key Deliverable |
|--------|----------|------|-----------------|
| CVA-9 | 4 weeks | Master Doc update + Expert Panel 2 + GO/NO-GO decision | Updated Master Doc (Part XXII) + panel vote + decision report |

**Phase D Effort**: 20 person-days | **Outcome**: GO → Sprint CVA-10 (full 208 templates) | DEFER → empirical studies | PARTIAL → selective integration | NO-GO → archive

---

## Total Effort and Timeline

**Person-Days**: 31 + 34 + 22.5 + 20 = **107.5 person-days**
- David: 13.5 days (guidance, review, panel liaison)
- Claude: 87 days (code, docs, analysis)
- Panelists: 18 days (async review)

**Calendar**: ~20–24 weeks (March–October 2026, with parallelization)

**Cost**: ~$27K–35K (assuming $250–350/person-day blended rate for professional hours)

---

## Key Design Decisions

| Decision | Rationale | Panelist Concern |
|----------|-----------|-----------------|
| Analytical, not causal | Allows feedback loops; prevents false ontological claims | Friston on coupled dynamics |
| Explicit dynamics required | Prevents hand-waving; makes separability testable | Strogatz on technical rigor |
| Identifiability pre-registration | Prevents p-hacking; ensures real evidence | Jordan on inverse problem |
| Cultural variation in structure | Not just parameter weights; real structural difference | Barrett on WEIRD bias |
| 20-template pilot gate | Validates framework before full 208 commitment | Panel consensus (incremental) |
| Two-panel structure | First panel endorsement, second panel validates pilot results | Risk management |

---

## Files Referenced

**Core Panel Documents**:
- `EXPERT_PANEL_CVA_FULL_2026-02-27.md` — Full transcripts, panelist statements, votes

**Proposed Deliverables** (to be created during sprints):

**Phase A**:
- `src/services/cva/constraint_variables.py` (Registry)
- `src/services/cva/valuation_axes.py` (Axis definitions + interactions)
- `src/services/cva/activity_frame.py` (Frame module)
- `docs/CVA_CONSTRAINT_VARIABLE_REGISTRY.md` (Specifications)
- `docs/CVA_VALUATION_AXES_SPECIFICATION.md`
- `docs/CVA_ACTIVITY_FRAME_SPECIFICATION.md`

**Phase B**:
- `data/templates/cva_annotations/` (20 annotated templates)
- `src/services/cva/epistemic_projection_cva.py` (Goal-modulated projection)
- `src/services/cva/beauty_compression.py` (Three compression models)
- `docs/CVA_PILOT_GAP_REPORT.md`
- `docs/CVA_PROJECTION_EXTENSION_SPECIFICATION.md`
- `docs/CVA_BEAUTY_COMPRESSION_ANALYSIS.md`

**Phase C**:
- `docs/CVA_EXPERIMENT_1_GOAL_MANIPULATION_PROTOCOL.md`
- `docs/CVA_EXPERIMENT_2_CONSTRAINT_MANIPULATION_PROTOCOL.md`
- `docs/CVA_EXPERIMENT_3_CROSS_CONTEXT_TRANSFER_PROTOCOL.md`
- `docs/CVA_CROSS_CULTURAL_STUDY_PROTOCOL.md`
- OSF pre-registration links

**Phase D**:
- Master Document Part XXII (3,000+ lines, integrated with Parts V–XXI)
- `docs/CVA_INTEGRATION_DECISION_REPORT.md`
- `docs/CVA_DECISIONS_LOG.md` (Parallel to `TIER2_DECISIONS_LOG.md`)

---

## Decision Framework (Phase D)

**Four Possible Outcomes**:

### 1. GO (Proceed to Sprint CVA-10)
**Condition**: Pilot shows no contradictions, projections improve accuracy, panel 2/3+ consensus.
**Next**: Full 208-template reclassification (8–10 weeks), CVA-integrated ATLAS system.

### 2. DEFER (Empirical Studies, Then Revisit)
**Condition**: Pilot promising but questions remain; identifiability studies needed.
**Next**: CVA tagged as experimental; studies launched with external collaborators (6–12 months); revisit after Phase C data.

### 3. PARTIAL (Selective Integration)
**Condition**: Some CVA components valuable, but full causal claim not warranted.
**Next**: Integrate constraint layer + optional valuations; version as ATLAS v2.5; revisit after empirical validation.

### 4. NO-GO (Archive, Lessons Learned)
**Condition**: Fundamental problems revealed.
**Next**: Archive CVA codebase; document why (post-mortem); salvage individual ideas for future work.

---

## Minority Concerns Tracking

**Strogatz's Concern**: Half-measures create technical debt.
- **Mitigation**: Phase D audit for orphaned components; strict decision gate; no partial integration without plan.

**Barrett's Concern**: Cultural variation must be structural, not parametric.
- **Mitigation**: Sprint CVA-2 builds structural variation; Sprint CVA-8 tests structure empirically; Master Doc disclaimer on contingency.

**Zumthor's Concern**: Use as design-thinking tool, not prediction engine.
- **Mitigation**: Master Doc section on design thinking; separate "predictive power" (experimental) from "design utility" (qualitative).

---

## Checkpoints and Success Criteria

### Phase A Checkpoint (March 15)
- Registries + Activity Frame code complete
- >80% test coverage
- No blocking issues
- **Success metric**: Specs >500 lines each; tests pass

### Phase B Checkpoint (May 1)
- 20 templates annotated
- CVA projection ≥ baseline ATLAS accuracy
- Beauty models R² > 0.4
- **Success metric**: <5 major gaps; no contradictions

### Phase C Checkpoint (May 15)
- Experiments pre-registered
- No fatal design flaws
- **Success metric**: OSF registration complete; protocols peer-reviewed

### Phase D Checkpoint (June 15)
- Master Doc updated
- Panel 2 convened
- GO/NO-GO decision documented
- **Success metric**: Panel vote ≥2/3 for GO/PARTIAL

---

## Key Questions for David

1. **Timeline**: Can we start Phase A by March 1? Phase D decision by June 15?
2. **Panel availability**: Can 6–8 panelists commit to async pre-reads for Phase 2 panel?
3. **Pilot scope**: Is 20 templates the right size, or should we pilot on 5–10 for speed?
4. **Empirical commitment**: If Phase C shows identifiability is hard, do we abandon CVA or continue PARTIAL?
5. **Integration depth**: If GO, how deeply do we integrate CVA into ATLAS? Replace projection, or parallel layer?

---

**Document Status**: DRAFT INDEX
**Prepared**: February 27, 2026
**See Also**: `CVA_SPRINT_PLAN_2026-02-27.md` (full 1,121-line document)
