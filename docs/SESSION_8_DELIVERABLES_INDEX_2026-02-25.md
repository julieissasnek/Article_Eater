# Session 8 Deliverables Index
**Date**: February 25, 2026
**For**: Professor David Kirsh
**From**: Claude Code (Session 8)
**Status**: COMPLETE & READY FOR REVIEW

---

## Overview

Session 8 produced a comprehensive sprint plan translating the 18-person expert panel's OVERSEER design recommendations into actionable engineering work. Three documents were created, organized for different audiences and use cases.

---

## Three Documents (Read in This Order)

### 1. SPRINT_PLAN_SUMMARY_2026-02-25.md (Quick Read — 10 min)
**Purpose**: High-level overview for decision-making
**Audience**: Professor Kirsh, executive summary
**Length**: 238 lines, ~1,500 words

**Contents**:
- What was delivered (one-paragraph summary per sprint)
- System architecture diagram
- Key technical decisions (decision table + panelist rationale)
- Dijkstra invariant explanation
- Expected outcomes by March 3
- Three options for implementation (Option A: all sprints; Option B: minimal; recommendation)
- Questions for David

**Best for**: Getting approval to proceed with engineering

**Read this first if**: Time-constrained or need executive summary

---

### 2. SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md (Comprehensive Reference — 45 min)
**Purpose**: Complete engineering specification with code examples and test coverage
**Audience**: Claude Code (implementer), David (technical review), panel members (optional)
**Length**: 1,740 lines, ~18 KB

**Contents**:
- Executive summary (3 paragraphs)
- System state diagram (Dijkstra invariant INV-0)
- Six sprints in full detail:
  - **Sprint 0**: Metadata enrichment (citation graph)
  - **Sprint 1**: 12-phase setup function (most complex; 300 LOC each phase)
  - **Sprint 2**: OVERSEER core (6 sub-components, database schemas)
  - **Sprint 3**: Coherence dashboard (Streamlit page, metrics)
  - **Sprint 4**: Argumentation graph (citation polarity, supersession)
  - **Sprint 5**: Nightly batch infrastructure (automated maintenance)
  - **Sprint 6**: Expert calibration prep (panel inputs)
- For each sprint: tasks, dependencies, testing approach, key decisions
- Risk register (5 major risks, probabilities, mitigation)
- Delivery timeline (Gantt-style table)
- Key decisions embedded (O-1 through O-8 with full rationale)
- Success criteria (functional, non-functional, epistemic)
- References (7 key papers: Quine, Haack, Spohn, Pearl, Cartwright, Dijkstra, DerSimonian)

**Best for**: Engineering implementation, detailed understanding, problem-solving

**Read this if**: Need to understand technical decisions, implement sprints, or brief panel members

---

### 3. SESSION_8_DELIVERABLES_INDEX_2026-02-25.md (This Document)
**Purpose**: Navigation guide and metadata
**Audience**: Everyone (orientational)
**Length**: 260 lines, ~1,200 words

**Contents**:
- Document descriptions
- Reading guide (how to navigate by use case)
- Key metrics & context
- Updated project files
- Next steps & approval path

**Best for**: Understanding how to use the other two documents

---

## Reading Guide by Use Case

### "I need to approve this plan in 10 minutes"
→ **Read**: SPRINT_PLAN_SUMMARY (10 min)
→ **Focus**: Sections "The Six Sprints", "Dijkstra Invariant", "What This Enables Next"
→ **Decide**: Approve for Sprint 0 start? Request modifications? Escalate to panel?

### "I want to understand the engineering work"
→ **Read**: SPRINT_PLAN_SETUP_AND_OVERSEER (45 min, or longer if diving into code)
→ **Focus**: Sprint 0–6 full details, code examples, database schemas
→ **Outcome**: Can implement or brief an implementer

### "I need to present this to the panel"
→ **Read**: Both summary (10 min) + relevant sections of main plan (30 min)
→ **Focus**: "Key Decisions Embedded", "Panel Theoretical Commitments" (end of main document)
→ **Outcome**: Can present rationale behind every engineering choice

### "I'm implementing Sprint N"
→ **Read**: Main plan, Sprint N section + adjacent sections (for dependencies)
→ **Focus**: Tasks table, dependencies, testing, code examples, files to create
→ **Tools**: Use this as pseudo-code specification

### "I need to understand risk"
→ **Read**: Main plan, "Risk Register" section + Sprint-specific risk subsections
→ **Focus**: Probability, impact, mitigation for each risk
→ **Decision**: Adjust sprints based on risk tolerance

---

## Key Metrics & Context

### System State Before Plan
- **Papers extracted**: ~850 (via Gemini pipeline)
- **Extraction JSONs**: ~100 in data/extractions/
- **Templates**: 208 total (103 calibrated, 79 scaffold)
- **T1.5 theories**: 14 formally reduced
- **Integration pipeline tests**: 27/27 passing
- **System status**: Eagerly wired (all Steps 2–13 functional)

### System State After Plan (Target: March 3)
- **Papers integrated**: 850 (into web of belief)
- **Beliefs created**: ~2,000+
- **BN nodes**: 850+
- **BN edges**: Constraint-learned DAG
- **OVERSEER**: Actively monitoring 5 invariants
- **Dashboard**: Live, real-time metrics
- **System status**: OPERATIONAL (Dijkstra invariant verified)

### Engineering Investment
- **Total engineering hours**: ~20.5 hours
- **Code to write**: ~3,500 lines (6 sprints combined)
- **Tests to write**: ~2,000 lines (comprehensive coverage)
- **Expert panel input**: ~6 hours (calibration review)
- **Total project duration**: Feb 25 – Mar 3 (6 calendar days)

---

## Updated Project Files

The following files were created or modified in support of this plan:

### New Documents Created
1. **docs/SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md** (main plan, 1,740 lines)
2. **docs/SPRINT_PLAN_SUMMARY_2026-02-25.md** (executive summary, 238 lines)
3. **docs/SESSION_8_DELIVERABLES_INDEX_2026-02-25.md** (this file, 260 lines)

### Files Updated
1. **TASKS.md** (P0 section updated with 8 new sprint tasks + panel calibration task)
2. **ACTIVE_TASKS.md** (new rows: SPRINT-PLAN-DELIVERY, SPRINT-0-READY)

### Related Existing Documents (Not Modified)
- `docs/PANEL_OVERSEER_DESIGN_2026-02-25.md` (expert panel recommendations, created Session 6–7)
- `docs/PANEL_SESSION_DELIVERABLES_2026-02-25.md` (panel summary, created Session 7)

---

## Decision Records

All 8 design questions (O-1 through O-8) from the expert panel are embedded in the main plan with full context and panelist rationale:

| O-ID | Topic | Decision | Panelist(s) |
|------|-------|----------|-----------|
| **O-1** | Web credence computation | Full pipeline (theory inference + reflective equilibrium) | Quine, Haack, Spohn, DerSimonian |
| **O-2** | Coherence alert threshold | Statistical baseline (mean ± 1σ per theory) | Cartwright |
| **O-3** | Violation handling | Quarantine (7-day review), not auto-retire | Haack |
| **O-4** | BN coupling | Hierarchical one-directional (web → BN priors) | Pearl, Cartwright, Good |
| **O-5** | Provenance computation | Synchronous (Step 5), not deferred | Haack |
| **O-6** | QA cache strategy | Batched nightly (Option C) | Good |
| **O-7** | OVERSEER database | Separate (overseer.db), not shared | Parnas |
| **O-8** | Maintenance work lanes | Parallel OVERSEER-MAINT lanes in ACTIVE_TASKS.md | Simon |

Each decision is justified with:
- **Context**: Why this question arose
- **Options considered**: What alternatives existed
- **Rationale**: Why this choice was made
- **Panelist concerns**: Which expert voices endorsed it
- **Risk assessment**: What could go wrong

---

## Approval Path & Next Steps

### For David Kirsh

**Decision Required**: Approve plan as written, request modifications, or defer to panel review?

**Options**:
1. **Approve immediately** → Authorize Sprint 0 start (today, 30 min)
2. **Request modifications** → Specify what changes are needed
3. **Defer to panel** → Convene panel for review before implementation (optional; O-1..O-8 already approved)

**Expected Response Time**: Recommend within 24 hours (Sprint 0–1 are on critical path for March 3 OPERATIONAL target)

### For Implementation (Claude Code)

**If approved**:
1. Start Sprint 0 immediately (semantic_scholar_enrichment.py --repair)
2. Follow Sprint 1 coding tasks (12 phases, most complex)
3. Implement Sprints 2–5 in sequence
4. Generate calibration report (Sprint 6)
5. Await panel calibration review (Mar 2–3)

**If modifications requested**:
1. Update main plan document
2. Revise affected sprint(s)
3. Re-submit for approval

---

## Success Criteria

### By Sprint Completion (March 2)
- [ ] All 850 papers integrated
- [ ] ~2,000+ beliefs in web of belief
- [ ] Global coherence baseline established (≥ 0.65 target)
- [ ] OVERSEER detects invariant violations correctly
- [ ] Dashboard live and updating
- [ ] Nightly pipeline operational
- [ ] Calibration report generated + ready for panel

### By Panel Calibration (March 3)
- [ ] Panel reviews per-theory baselines
- [ ] Alert thresholds finalized + coded
- [ ] VOI gaps ranked + approved
- [ ] Manual overrides applied (if needed)
- [ ] System declared OPERATIONAL (INV-0 verified)

---

## Technical Highlights

### Phase 5: Reflective Equilibrium (Key Innovation)
- **Convergence criterion**: Delta coherence < 0.001 (not fixed 5 iterations)
- **Safety bound**: Max 20 iterations (prevents infinite loops)
- **Acceptance**: Partial (< 0.05 delta) if full convergence not achieved
- **Panel rationale** (Quine, Haack): Holistic belief revision requires true equilibrium, not arbitrary iteration count

### OVERSEER Invariants (Dijkstra)
```
INV-0: System only OPERATIONAL if all below satisfied:
  INV-1: All beliefs have provenance (grounding chain)
  INV-2: BN structure = web constraints (causality + acyclicity)
  INV-3: Coherence ≥ baseline - 0.05 (max 5% decline)
  INV-4: No circular defeater chains (no A defeats B defeats C defeats A)
  INV-5: Extraction→Integration contract satisfied (ClaimV2 schema)
```

### Citation Polarity Detection (New Capability)
- Heuristic 1: Citation context markers ("contradicts", "disagrees")
- Heuristic 2: Belief alignment (low alignment → critical; high → supportive)
- Output: CitationPolarity (SUPPORTIVE/CRITICAL/NEUTRAL) with confidence scores

---

## FAQ

**Q: Can we start with just Sprints 0–2?**
A: Yes. Sprints 0–2 give you a working OPERATIONAL system by Feb 27. Sprints 3–6 add monitoring, discovery, and calibration (9 additional hours). Both are valid; recommendation is full path.

**Q: What if Phase 5 (Reflective Equilibrium) doesn't converge?**
A: Safety bound (20 iterations) prevents infinite loops. Partial acceptance (delta < 0.05) allows progress. System continues with warning logged. Panel can review + adjust if needed.

**Q: Do we need the panel to start implementation?**
A: No. O-1..O-8 are already approved (Session 6–7 expert review). Plan is ready for engineering now. Panel calibration happens Mar 2–3 (after implementation).

**Q: How does this relate to BN_graphical integration?**
A: Independent deployment path. BN_graphical can integrate later; Article Eater is OPERATIONAL without it (BN structure learned from constraints).

**Q: Can Sprint 6 happen before engineering (to get earlier panel feedback)?**
A: Yes. Could run Phase 8 of Sprint 1 in isolation, generate early coherence baseline, brief panel. Then continue other sprints.

---

## Documents at a Glance

| Document | Size | Read Time | Audience | Purpose |
|----------|------|-----------|----------|---------|
| SPRINT_PLAN_SUMMARY_2026-02-25.md | 238 lines | 10 min | David, execs | Approval decision |
| SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md | 1,740 lines | 45 min | Implementers, panel | Full spec |
| SESSION_8_DELIVERABLES_INDEX_2026-02-25.md | 260 lines | 15 min | Everyone | Navigation guide |

---

## Contact & Support

**Questions about the plan?**
- Review relevant sprint section in main document (SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md)
- Check "Risk Register" for common issues
- Consult panelist rationale (at end of main document) for decision context

**Ready to implement?**
- Approve plan (email David)
- Start Sprint 0 (30 min)
- Follow Sprint 1–6 in sequence
- Brief David on progress daily

**Need modifications?**
- Specify changes
- Update main plan document
- Revise affected sprints
- Re-submit for approval

---

**Document Version**: V1.0 (Index)
**Created**: 2026-02-25
**Last Updated**: 2026-02-25 11:00 UTC
**Status**: READY FOR DAVID'S APPROVAL
