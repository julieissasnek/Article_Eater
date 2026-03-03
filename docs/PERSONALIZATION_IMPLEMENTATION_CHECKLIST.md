# QA Personalization Implementation Checklist

**Status**: Ready for Phase 1
**Last Updated**: March 2, 2026
**Owner**: Implementation Team (AG)

---

## Overview

This checklist tracks implementation of real user-type personalization (ref: `QA_PERSONALIZATION_SPEC_2026-03-02.md`).

The goal: Transform the QA system from cosmetic personalization (different buttons, same answers) to structural personalization (genuinely different answers per user type).

**Timeline**: 8 weeks
**Phases**: 6 (data structures → handlers → response generation → integration → testing → evaluation)

---

## Phase 1: Data Structure Definition (Week 1)

### Subtask 1.1: Define Core Data Structures

- [ ] Create `src/services/user_personalization.py` with:
  - [ ] `UserTypeID` enum (ARCHITECT, RESEARCHER, STUDENT, REVIEWER, QUICK_LOOKUP)
  - [ ] `UserProfile` dataclass (presupposition_frame, question_modes, completeness_criteria, vocabulary_register, etc.)
  - [ ] `TypedAnswer` dataclass (all fields per Part C of spec)
  - [ ] `DesignParameter` dataclass (for architect answers)
  - [ ] `ResearcherEffectData` dataclass (for researcher answers)

**Acceptance criteria**:
- [ ] All dataclasses have docstrings explaining purpose
- [ ] `TypedAnswer` can serialize to JSON and back
- [ ] Type hints are complete (no `Any` types)
- [ ] Classes pass mypy type checking

### Subtask 1.2: Define User Profiles

- [ ] Create `src/services/user_profiles.py` with canonical profiles for all 5 types:
  - [ ] ARCHITECT: designer, pragmatic, action-focused
  - [ ] RESEARCHER: evidence-focused, heterogeneity-conscious
  - [ ] STUDENT: learning-focused, schema-building
  - [ ] REVIEWER: data-focused, reproducibility-focused
  - [ ] QUICK_LOOKUP: signal-focused, time-constrained

**Profile fields per spec Part A**:
- [ ] `type_id`: UserTypeID
- [ ] `name`: str
- [ ] `presupposition_frame`: str
- [ ] `primary_question_modes`: List[str]
- [ ] `completeness_criteria`: List[str]
- [ ] `vocabulary_register`: str (enum: plain, technical, moderate, standardized, conversational)
- [ ] `actionability_level`: float (0.0–1.0)
- [ ] `uncertainty_communication`: str
- [ ] `answer_structure`: str (what comes first)
- [ ] `evidence_depth`: str (minimal, moderate, deep, complete)
- [ ] `citation_style`: str (none, footnote, inline, full_apa)

**Acceptance criteria**:
- [ ] All 5 profiles defined
- [ ] Each profile validates against spec Part A
- [ ] Profiles can be loaded from JSON (for persistence)
- [ ] Accessing profile attributes works: `USER_PROFILES[UserTypeID.ARCHITECT].actionability_level`

### Subtask 1.3: Version and Commit

- [ ] Add both files to version control
- [ ] Write commit message: "Add user personalization data structures (Phase 1)"
- [ ] Update `TASKS.md` with Phase 1 completion and Phase 2 blockers

---

## Phase 2: Handler Architecture (Weeks 2–3)

### Subtask 2.1: Extend ArbitraryQAHandler

- [ ] Update `src/services/arbitrary_qa_handler.py`:
  - [ ] Add `user_type: Optional[UserTypeID]` parameter to `answer()` method
  - [ ] Add `_load_user_profiles()` method to load canonical profiles
  - [ ] Add `_route_to_handler()` method that selects type-specific handler based on:
    - Question type (existing classification)
    - User type (new)
  - [ ] Maintain backward compatibility: if user_type is None, use generic handler

**Acceptance criteria**:
- [ ] Existing code paths work unchanged (backward compatible)
- [ ] New `user_type` parameter accepted but optional
- [ ] Routing logic tested: MECHANISM question to architect handler vs researcher handler gives different path

### Subtask 2.2: Create TypeSpecificHandlers Class

- [ ] Create `src/services/type_specific_handlers.py`:
  - [ ] Class `TypeSpecificHandlers` with method `handle_typed_question()`
  - [ ] Delegate to question-type-specific handlers:
    - [ ] `handle_mechanism_question(query, user_type, evidence_base) → TypedAnswer`
    - [ ] `handle_evidence_for_question(query, user_type, evidence_base) → TypedAnswer`
    - [ ] `handle_scope_question(query, user_type, evidence_base) → TypedAnswer`
    - [ ] `handle_comparison_question(query, user_type, evidence_base) → TypedAnswer`
    - [ ] `handle_gaps_question(query, user_type, evidence_base) → TypedAnswer`
  - [ ] Each question-type handler has internal dispatch per user type:
    ```python
    def handle_mechanism_question(...):
        if user_type == ARCHITECT:
            return self._architect_mechanism(...)
        elif user_type == RESEARCHER:
            return self._researcher_mechanism(...)
        # etc.
    ```

**Acceptance criteria**:
- [ ] All 5 question types supported
- [ ] Each question type has at least 2 user-type handlers (architect, researcher minimum)
- [ ] Handlers return TypedAnswer (not string)
- [ ] Tests pass for routing logic

### Subtask 2.3: Implement Type-Specific Handler Methods

- [ ] For MECHANISM question type:
  - [ ] `_architect_mechanism(query, base_mechanism, effect_data) → TypedAnswer`
    - Output: design_parameters + brief mechanism + scope + actionability
  - [ ] `_researcher_mechanism(query, base_mechanism, effect_data) → TypedAnswer`
    - Output: full mechanism + effect_sizes + heterogeneity + competing explanations
  - [ ] `_student_mechanism(query, base_mechanism, effect_data) → TypedAnswer`
    - Output: theory_explanation + history + learning_path
  - [ ] `_reviewer_mechanism(query, base_mechanism, effect_data) → TypedAnswer`
    - Output: study_data table (exportable)
  - [ ] `_quick_mechanism(query, base_mechanism, effect_data) → TypedAnswer`
    - Output: headline + mechanism (one sentence)

**Acceptance criteria**:
- [ ] All 5 variants implemented for MECHANISM
- [ ] Each returns TypedAnswer with appropriate fields populated
- [ ] Unit tests for each handler (at least one test per handler)

### Subtask 2.4: Helper Methods for Type-Specific Formatting

- [ ] Implement `_express_credence_*` methods:
  - [ ] `_express_credence_architect(effect_data) → str`
    - Returns: "65% confident. Stronger in offices (70%), weaker in homes (55%)"
  - [ ] `_express_credence_researcher(effect_data) → str`
    - Returns: "60–70% credence. Publication bias likely inflates by 10–15%; I² = 52%"
  - [ ] `_express_credence_student(effect_data) → str`
    - Returns: "Fairly well-supported. The mechanism is contested between ART and SRT."
  - [ ] `_express_credence_reviewer(effect_data) → str`
    - Returns: "GRADE: Moderate certainty of evidence"
  - [ ] `_express_credence_quick(effect_data) → str`
    - Returns: "Moderate confidence"

- [ ] Implement `_format_citations_*` methods (per citation style):
  - [ ] `_format_citations_architect()`: Footnote style, minimal inline
  - [ ] `_format_citations_researcher()`: Full APA with DOIs, inline when relevant
  - [ ] `_format_citations_student()`: Short author-year, with context
  - [ ] `_format_citations_reviewer()`: BibTeX or exportable format
  - [ ] `_format_citations_quick()`: No citations

**Acceptance criteria**:
- [ ] All credence expression methods return strings matching examples in spec
- [ ] All citation methods tested and produce correct output
- [ ] Methods are reusable across handler types

### Subtask 2.5: Version and Commit

- [ ] Add `type_specific_handlers.py` to version control
- [ ] Update `arbitrary_qa_handler.py` integration
- [ ] Commit: "Add type-specific handler architecture (Phase 2)"
- [ ] Update `TASKS.md`

---

## Phase 3: Response Generation (Weeks 4–5)

### Subtask 3.1: Implement Full Handler for MECHANISM Questions

- [ ] Complete implementation of all 5 handlers for MECHANISM:
  - [ ] `_architect_mechanism()`: Full implementation with design parameter extraction
  - [ ] `_researcher_mechanism()`: Full implementation with effect size + heterogeneity
  - [ ] `_student_mechanism()`: Full implementation with theory + history + learning
  - [ ] `_reviewer_mechanism()`: Full implementation with study-level data export
  - [ ] `_quick_mechanism()`: Full implementation with headline + one sentence

**Helper methods needed**:
- [ ] `_extract_design_parameters(mechanism, effect_data) → List[DesignParameter]`
  - Scans mechanism and effect data to identify actionable parameters
  - Returns: [DesignParameter(name="Ceiling height", range=(9.8, 12), unit="feet", ...), ...]

- [ ] `_extract_effect_sizes(effect_data) → Dict`
  - Formats effect sizes with CI, heterogeneity, publication bias
  - Returns: {"estimate": d, "ci": (0.32, 0.64), "i2": 0.52, "egger_p": 0.08, ...}

- [ ] `_get_scope_conditions(effect_data, default_population) → List[str]`
  - Extracts scope from effect data, customized by population
  - Returns: ["Works in office workers (r=0.38)", "Weaker in hospitals (r=0.28)", ...]

- [ ] `_make_actionable(design_params, scope) → str`
  - Translates parameters and scope into actionable guidance
  - Returns: "Use living plants visible from >50% of workstations, <3m distance, with maintenance plan"

- [ ] `_explain_theories(theories: List[str]) → str`
  - Explains each theory from first principles
  - Returns: "Attention Restoration Theory (Kaplan & Kaplan 1989) proposes that..."

- [ ] `_create_learning_path(key_papers: List[str]) -> str`
  - Orders papers by pedagogy
  - Returns: "Start with Ulrich 1984 (foundational); then Kaplan & Kaplan 1989 (theory); then..."

**Acceptance criteria**:
- [ ] All helper methods implemented
- [ ] Unit tests for each helper (at least one test per)
- [ ] Integration tests: MECHANISM question → each user type produces TypedAnswer with correct fields
- [ ] Example test case from spec Part E passes (Architects get parameters first, etc.)

### Subtask 3.2: Implement Handlers for EVIDENCE_FOR Questions

- [ ] Repeat Subtask 3.1 for EVIDENCE_FOR question type
  - [ ] `_architect_evidence_for()`: Focus on practical implications
  - [ ] `_researcher_evidence_for()`: Full evidence synthesis with quality assessment
  - [ ] `_student_evidence_for()`: Key papers + methodology overview
  - [ ] `_reviewer_evidence_for()`: All studies matching criteria (exportable)
  - [ ] `_quick_evidence_for()`: Study count + headline finding

**Acceptance criteria**:
- [ ] All 5 handlers implemented
- [ ] Tests pass for EVIDENCE_FOR routing and rendering

### Subtask 3.3: Implement Handlers for SCOPE Questions

- [ ] Repeat Subtask 3.1 for SCOPE question type
  - [ ] `_architect_scope()`: Population-specific parameters and contraindications
  - [ ] `_researcher_scope()`: Subgroup analyses with heterogeneity breakdown
  - [ ] `_student_scope()`: Populations studied and gaps
  - [ ] `_reviewer_scope()`: Study-level population metadata (exportable)
  - [ ] `_quick_scope()`: One-sentence scope summary

**Acceptance criteria**:
- [ ] All 5 handlers implemented
- [ ] Handles questions like "When does X apply? For whom?"

### Subtask 3.4: Implement Handlers for Additional Question Types

- [ ] COMPARISON questions (X vs Y)
  - [ ] Architect: which is more cost-effective; parameters for each
  - [ ] Researcher: effect sizes compared, heterogeneity per option
  - [ ] Student: theories compared, tradeoffs
  - [ ] Reviewer: subgroup data filtered by each option
  - [ ] Quick: which is better (headline)

- [ ] GAPS questions (what don't we know)
  - [ ] Architect: what parameters are unmeasured
  - [ ] Researcher: research opportunities, methodological gaps
  - [ ] Student: thesis directions, field boundaries
  - [ ] Reviewer: populations/settings not yet studied
  - [ ] Quick: is evidence complete (yes/no)

**Acceptance criteria**:
- [ ] COMPARISON and GAPS handlers implemented for all 5 user types
- [ ] Tests pass

### Subtask 3.5: Version and Commit

- [ ] Commit: "Implement response generation for MECHANISM, EVIDENCE_FOR, SCOPE (Phase 3)"
- [ ] Update `TASKS.md`: Phase 3 complete, Phase 4 ready

---

## Phase 4: Integration (Week 6)

### Subtask 4.1: Update Query Request/Response Classes

- [ ] Update `streamlit_app/api_client.py`:
  - [ ] Add `user_type: Optional[str]` to `QueryRequest` dataclass
  - [ ] Add `user_type: Optional[str]` to `QueryResult` dataclass
  - [ ] Add `is_personalized: bool` to `QueryResult`
  - [ ] Add `personalization_notes: str` to `QueryResult`

**Acceptance criteria**:
- [ ] `QueryRequest` can be serialized to JSON with user_type
- [ ] `QueryResult` can be deserialized from API response with personalization fields

### Subtask 4.2: Update Streamlit Query Page

- [ ] Update `streamlit_app/pages/1_query.py`:
  - [ ] `execute_query()` passes `user_type` to API
  - [ ] Display personalization indicator: "Answer customized for Architect"
  - [ ] Offer to switch user type and re-run query

**Acceptance criteria**:
- [ ] Query page still works for non-personalized queries (backward compatible)
- [ ] When user_type selected, query passes it through
- [ ] Personalization indicator displays correctly

### Subtask 4.3: Update API Backend

- [ ] Update `src/api/endpoints/query.py` (or equivalent):
  - [ ] Accept `user_type` from request
  - [ ] Pass to `ArbitraryQAHandler.answer(query, user_type=...)`
  - [ ] Convert `TypedAnswer` to JSON for response
  - [ ] Include `is_personalized` flag in response

**Acceptance criteria**:
- [ ] API endpoint accepts user_type parameter
- [ ] Returns personalized response structure
- [ ] Tests pass for endpoint

### Subtask 4.4: End-to-End Integration Test

- [ ] Test full flow:
  - [ ] User selects "Architect" in Streamlit
  - [ ] Enters query "Do plants reduce stress?"
  - [ ] Query sent to API with user_type="architect"
  - [ ] API routes to TypeSpecificHandlers.handle_*_question(user_type=ARCHITECT)
  - [ ] TypedAnswer with design_parameters returned
  - [ ] Rendered on Streamlit with parameters highlighted
  - [ ] Personalization indicator shows "Answer customized for Architect"

**Acceptance criteria**:
- [ ] E2E test passes for at least 2 user types
- [ ] Answer structure differs per type (architect parameters first vs researcher effect sizes first)

### Subtask 4.5: Version and Commit

- [ ] Commit: "Integrate personalization with API and Streamlit (Phase 4)"
- [ ] Update `TASKS.md`: Phase 4 complete, Phase 5 ready

---

## Phase 5: Testing & Validation (Week 7)

### Subtask 5.1: Test Case Execution (from Spec Part E)

For each test case, verify expected characteristics:

#### Test Case 1: "Do plants reduce stress?"

- [ ] **Architect answer**:
  - [ ] Includes design parameters (plant density, placement, etc.)
  - [ ] 300–500 words
  - [ ] Credence expressed as percentage (e.g., "65% confident")
  - [ ] Scope conditions stated ("Works in offices with natural light")
  - [ ] No statistical notation (no I², p-values)

- [ ] **Researcher answer**:
  - [ ] Starts with effect size (d or r with 95% CI)
  - [ ] Includes heterogeneity (I²)
  - [ ] Publication bias assessment
  - [ ] 800–1200 words
  - [ ] Cites studies with DOIs

- [ ] **Student answer**:
  - [ ] Foundational theory explanation first
  - [ ] Historical context (Ulrich → Kaplan → modern)
  - [ ] Learning path suggested
  - [ ] 600–900 words

- [ ] **Reviewer answer**:
  - [ ] Study-level data in table format
  - [ ] 17 studies listed with design, N, effect size, CI
  - [ ] GRADE certainty ratings
  - [ ] Exportable (CSV or JSON)

- [ ] **Quick Lookup answer**:
  - [ ] Headline: "Yes" or "Probably" with credence
  - [ ] One-sentence mechanism
  - [ ] One-sentence scope
  - [ ] One-sentence caveat
  - [ ] <100 words total

**Acceptance criteria**:
- [ ] All 5 answers pass their respective checks
- [ ] Differences between answers are substantial (not just reformatted)

#### Test Case 2: "What are scope conditions for nature views in hospitals?"

- [ ] Repeat test case 1 checks for scope-specific variants

**Acceptance criteria**:
- [ ] All 5 answers address scope conditions appropriately

### Subtask 5.2: Epistemic Integrity Audit

- [ ] Implement `audit_epistemic_integrity(answer: TypedAnswer, user_type: UserTypeID) → Dict[str, bool]`:
  - [ ] Check: No misrepresentation (credence ≤ 1.0, caveats present for credence < 0.70)
  - [ ] Check: Evidence quality disclosed (EBD level, RCT count, etc.)
  - [ ] Check: Scope conditions present (≥1 scope condition)
  - [ ] Check: Individual differences noted (if heterogeneity >0.30)
  - [ ] Check: Competing explanations named (if >1 mechanism)

- [ ] Run audit on 10 sample answers per user type (50 total)
- [ ] All checks must pass; no answer can fail integrity audit

**Acceptance criteria**:
- [ ] All 50 answers pass epistemic audit
- [ ] Failed answers are fixed before moving to next phase

### Subtask 5.3: Differentiation Score

- [ ] Generate answers to same query for all 5 user types
- [ ] Compute embedding similarity between answers
- [ ] Measure cosine distance (should be >0.3 for distinct answers)
- [ ] Repeat for 10 diverse queries

**Acceptance criteria**:
- [ ] Average cosine distance >0.3 across query set
- [ ] Answers are genuinely different (not just reformatted)

### Subtask 5.4: Answer Completeness Scoring

- [ ] Implement `score_answer_appropriateness(answer, user_type) → float`:
  - [ ] Architect: design parameters (20%), actionability (15%), scope (15%), mechanism brief (10%), measurement (20%), credence expression (20%)
  - [ ] Researcher: effect sizes (20%), heterogeneity (20%), mechanisms (15%), gaps (15%), caveats (15%), citations (15%)
  - [ ] Student: theory (20%), history (15%), learning path (20%), field politics (15%), open questions (15%), tone (15%)
  - [ ] Reviewer: study data (40%), GRADE (20%), search reproducibility (20%), no narrative (20%)
  - [ ] Quick: headline (20%), credence (30%), scope (20%), caveat (20%), length <100 words (10%)

- [ ] Score 10 answers per type
- [ ] All must score ≥0.80 appropriateness

**Acceptance criteria**:
- [ ] All 50 answers score ≥0.80
- [ ] Low-scoring answers are reworked

### Subtask 5.5: Version and Commit

- [ ] Commit: "Complete testing & validation (Phase 5)"
- [ ] Create test report: `docs/TESTING_REPORT_2026-03-02.md`
  - Summarize test cases passed
  - Epistemic audit results
  - Differentiation scores
  - Completeness scores
- [ ] Update `TASKS.md`: Phase 5 complete, Phase 6 ready

---

## Phase 6: Evaluation (Weeks 8+)

### Subtask 6.1: A/B Testing Setup

- [ ] Design A/B test:
  - [ ] Group A: Personalized answers (new)
  - [ ] Group B: Generic answers (current)
  - [ ] Metric: User satisfaction ("How well did this answer match your needs?")
  - [ ] Sample size: 30 users per group
  - [ ] Duration: 2 weeks

- [ ] Implement user satisfaction survey in Streamlit
  - [ ] After displaying answer: "Rate how well this answer matched your needs: 1–5"
  - [ ] Collect: user_type, question, answer_type (personalized/generic), rating

**Acceptance criteria**:
- [ ] Survey integrated into Streamlit
- [ ] Data logging works
- [ ] Can slice results by user type

### Subtask 6.2: User Feedback Loop

- [ ] Option after survey: "Tell us what you'd change"
- [ ] Collect qualitative feedback
- [ ] Analyze patterns: e.g., "Architects want more trade-off details" → update handlers

**Acceptance criteria**:
- [ ] Feedback collection works
- [ ] Can generate report of common feedback themes

### Subtask 6.3: Iterate Based on Feedback

- [ ] After 2 weeks of A/B testing:
  - [ ] Analyze satisfaction scores: Target personalized > generic by 15–25%
  - [ ] Extract feedback themes
  - [ ] Update handler logic / user profiles as needed
  - [ ] Retest

**Acceptance criteria**:
- [ ] Personalized answers score 15–25% higher on satisfaction
- [ ] If not, iterate handlers until target achieved

### Subtask 6.4: Document Learnings

- [ ] Create `docs/PERSONALIZATION_LEARNINGS_2026-03.md`:
  - [ ] A/B test results
  - [ ] User feedback themes
  - [ ] Handler improvements made
  - [ ] Profile adjustments made
  - [ ] Recommendations for Phase 2 (other question types)

**Acceptance criteria**:
- [ ] Document captures key insights
- [ ] Includes data + qualitative feedback

### Subtask 6.5: Final Commit and Close

- [ ] Commit: "Complete evaluation & learnings documentation (Phase 6)"
- [ ] Update `TASKS.md`: Mark all tasks complete
- [ ] Create sprint completion report: `docs/SPRINT_PERSONALIZATION_COMPLETION_2026-03-02.md`

---

## Cross-Phase Tasks

### Code Quality

- [ ] All code passes `ruff check` (no linting errors)
- [ ] All code passes `mypy --strict` (full type checking)
- [ ] Code follows project style (4-space indents, docstrings, etc.)
- [ ] New files added to `.gitignore` if needed

### Testing

- [ ] Unit tests written for all handlers (minimum 1 per handler)
- [ ] Integration tests for end-to-end flow (Phase 4)
- [ ] All tests pass before each commit
- [ ] Test coverage >85% for new code

### Documentation

- [ ] Docstrings on all classes and methods
- [ ] README updated with personalization feature (high-level overview)
- [ ] Inline comments for complex logic
- [ ] Update TASKS.md after each phase

### Performance

- [ ] Handler routing adds <100ms latency to existing query
- [ ] TypedAnswer serialization/deserialization <10ms
- [ ] No memory leaks (profile loading is lazy-loaded once)

---

## Risk Mitigation

### Risk: Handlers are expensive (slow down queries)

**Mitigation**:
- [ ] Measure latency for each handler (Phase 4)
- [ ] If >200ms per query, optimize:
  - [ ] Cache effect size calculations
  - [ ] Lazy-load complex helpers
  - [ ] Profile and identify bottlenecks

### Risk: Backward compatibility breaks

**Mitigation**:
- [ ] All changes to ArbitraryQAHandler maintain optional user_type parameter
- [ ] Test: Old code calling without user_type still works
- [ ] Generic handler (default if user_type=None) produces current behavior

### Risk: Epistemic integrity audit fails

**Mitigation**:
- [ ] Implement audit early (Phase 3)
- [ ] Fix failed answers before proceeding
- [ ] Add guardrail rules to handler code (e.g., "If credence <0.70, add caveat")

### Risk: Differentiation is cosmetic (not substantial)

**Mitigation**:
- [ ] Compute differentiation score weekly (Phase 3 onward)
- [ ] If cosine distance <0.25 for any pair, rework handlers
- [ ] Example: Researcher handlers may be too similar; ensure heterogeneity + publication bias always included

---

## Blockers & Dependencies

- [ ] Phase 1 must complete before Phase 2 (data structures needed)
- [ ] Phase 2 must complete before Phase 3 (handler architecture needed)
- [ ] Phase 3 must complete before Phase 4 (response generation needed)
- [ ] Phase 4 must complete before Phase 5 (integration needed)
- [ ] Phase 5 must complete before Phase 6 (need working system to evaluate)

No phases can be parallelized due to dependencies.

---

## Definition of Done

The personalization feature is complete when:

1. ✓ All 5 user types have type-specific handlers for ≥3 question types (MECHANISM, EVIDENCE_FOR, SCOPE)
2. ✓ All test cases from spec Part E pass (examples: architects get parameters first, researchers get effect sizes, etc.)
3. ✓ Epistemic integrity audit: 100% of answers pass all integrity checks
4. ✓ Differentiation score: >0.3 cosine distance between user type answers (genuinely different)
5. ✓ End-to-end integration: Streamlit → API → handlers → TypedAnswer rendering works
6. ✓ A/B testing: Personalized answers score 15–25% higher on user satisfaction than generic
7. ✓ Code quality: All code passes linting, type checking, unit tests
8. ✓ Documentation: Spec, panel notes, learnings, code comments all in place

---

## Estimated Effort per Phase

| Phase | Duration | Effort | Owner |
|-------|----------|--------|-------|
| 1: Data Structures | 1 week | 20 hours | AG (any) |
| 2: Handler Architecture | 2 weeks | 40 hours | AG (senior) |
| 3: Response Generation | 2 weeks | 50 hours | AG (senior) |
| 4: Integration | 1 week | 30 hours | AG (any) |
| 5: Testing | 1 week | 25 hours | AG (QA) |
| 6: Evaluation | 1+ week | 15 hours | AG (any) |
| **Total** | **8 weeks** | **180 hours** | |

Assumes 1 full-time engineer; can parallelize subtasks 3.1–3.3 if 2+ engineers available.

---

## Success Criteria (Quantitative)

| Metric | Target |
|--------|--------|
| # of question types with full personalization | ≥3 |
| # of user types fully supported | 5 |
| Epistemic integrity audit pass rate | 100% |
| Differentiation score (avg cosine distance) | >0.30 |
| Answer completeness score (all types) | >0.80 |
| User satisfaction (personalized vs generic) | +15–25% |
| Code test coverage | >85% |
| Latency overhead per query | <100ms |
| Zero critical bugs in Phase 5 | Yes |

---

## Contact & Escalation

- **Implementation Owner**: AG (engineering team)
- **Specification Owner**: David Kirsh
- **Panel Review**: Use panel deliberation notes for questions
- **Blockers**: Escalate to David with specific issue + proposed solution

---

**Document Status**: Ready for Phase 1 execution
**Next Action**: Create `src/services/user_personalization.py` and begin Subtask 1.1

