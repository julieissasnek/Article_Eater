# QA System Personalization: Complete Documentation

**Date**: March 2, 2026
**Status**: Expert panel deliberation complete; specification ready for implementation
**Owner**: David Kirsh, UCSD Cognitive Science

---

## Quick Overview

The ATLAS QA system currently supports 5 user personas (architect, researcher, student, systematic reviewer, quick lookup) but provides only **cosmetic personalization** — all users get essentially identical answers with different buttons and question suggestions.

This documentation package defines **real personalization**: genuinely different answers per user type, structured according to each type's cognitive mode, information needs, and decision context.

---

## What's Included

### 1. Core Specification
**File**: `QA_PERSONALIZATION_SPEC_2026-03-02.md` (8,500+ words)

The complete technical specification including:
- **Part A**: User Type Profiles for all 5 personas (presupposition frame, completeness criteria, vocabulary register, actionability needs, uncertainty communication)
- **Part B**: Personalization Dimensions (answer structure, evidence presentation, vocabulary, uncertainty, actionability)
- **Part C**: Implementation Architecture (high-level design, data structures, code snippets, integration points)
- **Part D**: Epistemic Guardrails (7 rules ensuring personalization doesn't distort evidence)
- **Part E**: Test Criteria (concrete test cases for each user type; success metrics)
- **Part F**: Implementation Roadmap (6-phase plan, 8 weeks)

**Use this document for**:
- Technical architecture decisions
- Data structure definitions
- Integration points with existing code
- Test case validation

---

### 2. Panel Deliberation Notes
**File**: `PANEL_DELIBERATION_NOTES_2026-03-02.md` (5,000+ words)

Expert panel discussion (8 researchers) addressing key questions:

**Q1: What should ACTUALLY differ between user types?**
- Answer: Five genuinely different cognitive modes, not just reading levels
- Discussion: Architect (goal-directed), Researcher (epistemic critique), Student (schema construction), Reviewer (systematic reproducibility), Quick (rapid signal extraction)

**Q2: What is completeness for each user type?**
- Answer: Completeness means different things per type (parameters vs. heterogeneity vs. theory vs. data vs. headline)
- Table: Completeness criteria per type

**Q3: How do we avoid epistemic compromise?**
- Answer: 7 guardrails ensuring simplification ≠ distortion
- Rules: Required caveats per credence level, evidence quality disclosure, no threshold inflation, mechanism honesty, scope conditions mandatory, individual differences disclosed, competing explanations acknowledged

**Q4: What's minimum viable personalization?**
- Answer: 4 key dimensions cover 80% of the difference
- Dimensions: Answer structure, evidence depth, vocabulary register, uncertainty communication
- Estimate: 8 weeks, manageable implementation cost

**Q5: Where should personalization happen (generation vs presentation)?**
- Answer: Generation time, not presentation
- Rationale: Different user types ask different questions, need different content structures, different information

**Consensus summary and takeaways**

**Use this document for**:
- Understanding the rationale behind the specification
- Resolving design questions during implementation
- Panel review and feedback
- Communicating with non-technical stakeholders

---

### 3. Implementation Checklist
**File**: `PERSONALIZATION_IMPLEMENTATION_CHECKLIST.md` (2,500+ words)

Detailed, phase-by-phase checklist for engineering team:

**6 Phases**:
1. **Phase 1 (Week 1)**: Data structure definition (UserTypeID, UserProfile, TypedAnswer, DesignParameter, etc.)
2. **Phase 2 (Weeks 2–3)**: Handler architecture (extend ArbitraryQAHandler, create TypeSpecificHandlers)
3. **Phase 3 (Weeks 4–5)**: Response generation (implement all handlers for MECHANISM, EVIDENCE_FOR, SCOPE)
4. **Phase 4 (Week 6)**: Integration (update API, Streamlit, end-to-end testing)
5. **Phase 5 (Week 7)**: Testing & validation (test cases, epistemic audit, differentiation, completeness scoring)
6. **Phase 6 (Week 8+)**: Evaluation (A/B testing, user feedback, iteration)

**Per phase**:
- Subtasks with checkboxes
- Acceptance criteria for each subtask
- Helper methods to implement
- Code snippets where applicable
- Estimated effort

**Cross-phase requirements**: Code quality, testing, documentation, performance, risk mitigation

**Success metrics**:
- 3+ question types with full personalization
- 5 user types fully supported
- 100% epistemic integrity audit pass rate
- >0.30 differentiation score (answers are genuinely different)
- +15–25% user satisfaction improvement (A/B test)

**Use this document for**:
- Day-to-day implementation tracking
- Code review checklist
- Phase completion criteria
- Risk management

---

### 4. Quick Reference
This README (you are here)

---

## How to Use These Documents

### For Design Decisions
1. Start with **Panel Deliberation Notes** (Part A–C) to understand the rationale
2. Check **Specification** (Part B–C) for technical details and examples
3. Reference **Checklist** if you encounter a scope/precedent question

### For Implementation
1. **Week 1**: Read Specification Part C + Checklist Phase 1 → start coding
2. **Weeks 2–3**: Reference Specification code snippets, use Checklist Phase 2–3
3. **Week 4+**: Use Checklist for testing, integration, evaluation

### For Testing
1. **Unit tests**: Reference Specification Part E test cases
2. **Integration tests**: Checklist Phase 4–5 sections
3. **Success metrics**: Checklist bottom section + Specification Part E

### For Questions
1. **"Why personalize this way?"** → Panel Deliberation
2. **"How should this be coded?"** → Specification Part C (code snippets)
3. **"What's next after I finish X?"** → Checklist (next phase)
4. **"How do I know it's done?"** → Checklist (success criteria)

---

## Key Concepts

### The Five User Types

| Type | Cognitive Mode | Key Difference |
|------|---|---|
| **Architect** | Goal-directed pragmatism | Wants actionable design parameters & thresholds |
| **Researcher** | Epistemic critique | Wants effect sizes, heterogeneity, competing mechanisms |
| **Student** | Schema construction | Wants foundational theory & learning path |
| **Reviewer** | Systematic reproducibility | Wants structured, machine-readable data |
| **Quick Lookup** | Rapid signal extraction | Wants headline + credence + one caveat |

### Four Key Dimensions of Personalization

1. **Answer Structure**: What comes first? (parameter vs. effect size vs. theory vs. data vs. headline)
2. **Evidence Depth**: How much detail? (minimal → moderate → deep → complete)
3. **Vocabulary Register**: What words? (plain → technical → conversational)
4. **Uncertainty Communication**: How do we say "we're unsure"? (percentage, interval, verbal, GRADE, label)

### Seven Epistemic Guardrails

1. No misrepresentation via oversimplification
2. Evidence quality must always be disclosed
3. No threshold inflation (false precision)
4. Mechanism must be stated honestly (including unknowns)
5. Scope conditions are non-negotiable
6. Individual differences must be disclosed
7. Competing explanations must be acknowledged

---

## Expected Outcomes

### During Implementation
- Clearer code architecture (type-specific handlers)
- Better test coverage (each handler separately tested)
- Documented decision rationale (panel notes explain why)

### After Completion
- Architects receive answers with design parameters + trade-offs first
- Researchers receive answers with effect sizes + heterogeneity first
- Students receive answers with theory + learning path first
- Reviewers receive exportable study-level data tables
- Quick-lookup users receive 50-word headlines with credence

### Long-Term Impact
- User satisfaction increases 15–25% (A/B test target)
- System matches cognitive modes, not just reading levels
- Personalization is genuinely useful, not cosmetic
- Epistemic integrity is maintained across all variations
- Foundation for extending to additional question types

---

## Timeline

```
Week 1:    Data structures defined + committed
Weeks 2–3: Handler architecture + Phase 2 handlers
Weeks 4–5: All response generators implemented
Week 6:    Integration + end-to-end tests
Week 7:    Testing suite passes; epistemic audit 100%
Week 8+:   A/B testing, feedback, iteration
```

**Critical path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 (no parallelization possible)

---

## FAQ

### Q: Why not just present answers differently?
**A**: Different user types ask different questions and need fundamentally different content. Reformatting one answer doesn't work. See **Specification Part C** (generation vs. presentation).

### Q: How do we ensure architects don't get oversimplified?
**A**: Seven epistemic guardrails (see **Guardrails** section above). Every answer passes an integrity audit. See **Specification Part D**.

### Q: What if a user type doesn't like their personalized answer?
**A**: Frontend offers to switch types and re-run query. See **Specification Part C (Integration)**.

### Q: How much does this slow down queries?
**A**: Target <100ms overhead. Handlers are deterministic (no new LLM calls). See **Checklist (Performance)**.

### Q: Is this backward compatible?
**A**: Yes. Without user_type specified, system behaves as it does now. See **Checklist Phase 1 (Backward Compatibility)**.

### Q: What if the panel was wrong about what users need?
**A**: Validate in Phase 6 (A/B testing + user feedback). If satisfaction doesn't improve 15–25%, iterate. See **Checklist Phase 6 (Feedback Loop)**.

---

## Next Steps

### For David (Researcher/Owner)
1. Review **Panel Deliberation Notes** (especially Q1–Q5) for expert consensus
2. Review **Specification Part D (Epistemic Guardrails)** for concerns about truth preservation
3. Approve or iterate on the 5 user type profiles (Specification Part A)
4. Assign implementation team

### For Implementation Team (AG)
1. Read **Specification Part C (Implementation Architecture)** for overview
2. Start **Checklist Phase 1**: Create data structures
3. Use **Specification code snippets** as reference during coding
4. After each phase, verify against **Checklist** acceptance criteria

### For QA/Testing
1. Familiarize with **Specification Part E (Test Criteria)** now
2. Prepare test infrastructure in Week 6
3. Run test cases + epistemic audit in Phase 5
4. Execute A/B testing in Phase 6

---

## Document Relationships

```
Panel Deliberation Notes  ←→  Specification  ←→  Implementation Checklist
   (Why?)                     (What? How?)         (When? Who? What's next?)
```

All three documents are designed to be readable independently, but linked conceptually. When you need to understand the rationale (Why), go to Panel Notes. When you need technical details (What/How), go to Specification. When you need task tracking (When/What's next), go to Checklist.

---

## Versioning & Updates

- **Specification**: V1 (2026-03-02) — Locked for Phase 1–3 implementation. Updated only if panel reconvenes.
- **Panel Notes**: V1 (2026-03-02) — Locked. Only updated if major panel decision changes.
- **Checklist**: Living document. Updated weekly as phases complete. See TASKS.md for real-time status.
- **README**: This file. Updated quarterly or when major changes occur.

---

## Contact & Questions

- **Specification Questions**: David Kirsh (researcher)
- **Implementation Questions**: AG lead engineer
- **Panel Questions**: Consult **Panel Deliberation Notes**; escalate to David if unresolved
- **Blockers**: Escalate with specific issue + proposed solution

---

**Status**: Ready for Phase 1 execution. All documentation complete. Awaiting go-ahead to begin implementation.

