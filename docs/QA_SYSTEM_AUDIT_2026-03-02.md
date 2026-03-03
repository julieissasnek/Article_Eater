# ATLAS QA System Audit Report

**Date**: 2026-03-02
**Auditor**: Claude Code (Haiku 4.5)
**Status**: Completed — Comprehensive gap analysis with implementation recommendations
**Scope**: Full ATLAS QA system (specs, services, UI, user type personalization)

---

## Executive Summary

The ATLAS QA system is **architecturally sound but epistemically incomplete**. The system implements a well-designed three-level progressive disclosure structure and question classification routing that aligns with the master doc specs. However, there are **critical gaps in epistemic work** — the system does not currently demonstrate the 7 Q-norms, does not track explanatory completeness, and user-type personalization is partially implemented (schema exists; differentiation is cosmetic rather than substantive).

**Key Finding**: A researcher, practitioner, and student asking the same question receive answers with different *presentation* but identical *content*. The system's data structures support real personalization, but the routing logic doesn't activate it.

---

## Part 1: Specification Compliance Matrix

### QA System Requirements from Master Doc (§122 + INTERPRETATION_SPACE_SPEC §4.7)

| Capability | Spec Location | Implemented? | Quality | Notes |
|---|---|---|---|---|
| **A. Question Classification** | §122.4 (Query Classification) | YES | Good | 20+ question types defined; regex + fallback; confidence scores |
| **B. Question Types (Interpretation Space)** | §4.7.1-4.7.2 (7 Q-norms) | PARTIAL | Poor | Types exist but Q-norm validation absent |
| **C. Progressive Disclosure** | §122.3 (3-5 levels) | YES | Good | 5 response modes (headline/summary/detail/deep_dive) implemented |
| **D. Credence-Weighted Answers** | §4.2 (R₂ warrants) | PARTIAL | Medium | Answers show credence but not credence distributions; no explicit warrant mapping |
| **E. Contradiction Detection** | §122.2 + E1.D2 (Pearl) | YES | Good | ContestedEvidence section tracks contradictions |
| **F. Scope Conditions** | §122.3 + §4.7.1 (Q1 norm) | YES | Medium | Extracted but sparse; not always complete |
| **G. Theory-Grounded Mechanisms** | §122.2 (T1 frameworks) | PARTIAL | Medium | Framework voices exist (integrated_query_service) but rarely surfaced |
| **H. Gap Identification** | §4.7.1 (Q5 norm: Gawande) | YES | Medium | Gaps exist in data; not formatted as questions per Q5 |
| **I. User Type Differentiation** | §122.2 (Panel design) | PARTIAL | Weak | UI selector exists; response variation is minimal |
| **J. Explanatory Work (Epistemic Transparency)** | §122.2 (Lipton IBE) | PARTIAL | Weak | System explains *what*; doesn't always explain *why it believes this* |

**Overall Compliance**: 60% — Core infrastructure present, but epistemic rigor incomplete.

---

## Part 2: Gap Analysis (Detailed)

### A. Q-Norm Compliance (§4.7.1: The Seven Question-Formulation Norms)

The system does NOT currently validate generated questions against the 7 Q-norms. This is a critical gap because the spec explicitly states (§4.7): "A poorly formulated question wastes computational resources, generates vacuous answers, and creates the illusion of interrogation without actual epistemic progress."

| Q-Norm | Name | Spec Requirement | Implementation | Gap |
|--------|------|---|---|---|
| **Q1** | Warrant Presuppositions (Hintikka) | Check credence ≥ 0.5 before asking "why" | NO validation in arbitrary_qa_handler.py | MISSING: Presupposition checking; system can ask "why does X?" when X is DEFEATED |
| **Q2** | Specify Contrast Class (Bromberger/van Fraassen) | Every "why/how/comparison" has explicit contrast | Patterns exist but not enforced | PARTIAL: COMPARISON type defined but contrast not always extracted from web |
| **Q3** | Classify Problem Type (Laudan) | Label: empirical vs conceptual vs methodological vs bridging | Implicit in query_type; no explicit problem_type field | WEAK: No visible problem classification in responses |
| **Q4** | Value Before Asking (Simon VOI) | Estimate V_prior; threshold θ_VOI = 0.15 | NO VOI computation | MISSING: Questions are asked without value estimation |
| **Q5** | Name What You Don't Know (Gawande) | Non-vague targets + answer shape + falsifiable anchor | Gap registry exists; not formatted as precise questions | PARTIAL: Gaps identified but not as per Q5 specifics |
| **Q6** | Earn the Complexity (Yong Prerequisites) | L1→L2→L3→L4→L5 hierarchy enforced | No prerequisite checking | MISSING: Cross-domain questions can be asked before main effect established |
| **Q7** | Show the Seam (Sapolsky: Target Conflicts) | When conflict detected, ask about boundary not main effect | Logic exists for CONTRADICTS; not applied during question generation | WEAK: Conflicts detected but question formulation doesn't prioritize seams |

**Critical Finding**: The system can generate fluent-sounding questions that violate the Q-norms. Example: If daylight→stress has credence 0.3 (TENTATIVE), the system might still ask "Why does daylight reduce stress?" (violates Q1). The question sounds good but presupposes something unwarranted.

**Success Condition Target**: SC-Q-ALL = 80% composite compliance across all 7 norms.
**Current Status**: ~15% (question classification works; norm validation absent).

**Recommended Implementation**:
1. Add Q-norm validation before question is presented to user
2. Implement presupposition checker: verify credence(presupposition) ≥ 0.5 or reformulate
3. Compute VOI for every gap (structural_impact × tractability × |generators|)
4. Add problem_type classification to every question
5. Enforce prerequisite hierarchy before asking complex questions

---

### B. Explanation Completeness (Lipton's Inference to Best Explanation)

The master doc (§122.2) endorses Lipton's model: a good explanation is "lovely" — unified, mechanistic, precise, appropriately scoped. The spec says answers should explain "why they are asking it" and "what deeper question lurks behind."

**Audit Finding**: The system explains *answers to questions* but not "why this is the right answer" or "what changed your credence."

| Dimension | Required (Spec) | Current (Implementation) | Gap |
|---|---|---|---|
| Answer the actual question first | Headline before elaboration (P1) | YES — headline provided | GOOD |
| Show reasoning (warrant chain) | Evidence items with sources, credence | Evidence items + credence shown | GOOD |
| Make depth levels explicit | 5 levels (headline/summary/detail/deep/deep_research) | YES — response_mode selectable | GOOD |
| Preserve coherence across levels | Level 1 doesn't contradict Level 3 | NO validation of coherence | WEAK: Could show conflicting mechanisms at different levels |
| Acknowledge uncertainty honestly | Confidence markers throughout | Confidence level (high/medium/low) shown | MEDIUM: Coarse-grained; not credence distributions |
| **Enable action** | Connect to what user can *do* | Design guidance exists for architects | PARTIAL: Only for practitioner persona |
| **Show epistemic work** | How did you arrive at this credence? | Belief list shown; not warrant chain | WEAK: No "here's why credence is 0.72 not 0.65" |

**Key Missing Piece**: When the system says "Plants reduce stress (credence 0.72)," it should explain **why not 0.80 or 0.60**. What evidence points up? What points down? This is the "epistemic work."

**Recommended Implementation**:
1. For each belief, show contributing evidence with direction (+/−)
2. Explain credence using warrant structure: "High credence because [3 supporting warrants]; lower than 0.85 because [2 undercutting defeaters]"
3. For contested findings, explicitly show both sides: "6 studies say plants reduce stress; 2 say no effect. Why believe 6 over 2? [explanation]"

---

### C. User Type Personalization (Schema vs. Reality)

**Key Finding: The system has elaborate persona infrastructure but minimal actual differentiation.**

#### Infrastructure Present

The system defines `UserPersona` enum with 6 types:
- ARCHITECT: design recommendations, thresholds
- RESEARCHER: evidence quality, gaps, studies
- FACILITIES: practical changes, ROI
- STUDENT: clear explanations, principles
- POLICY: population effects, standards
- CLINICIAN: patient populations, contraindications

And `PERSONA_EMPHASIS` mapping: each persona has primary/secondary priorities and different vocabulary preferences.

#### Actual Differentiation (What Users Actually See)

**Test Case**: "What reduces stress in hospitals?"

**Expected (per spec)**:
- Practitioner: "High ceilings + nature views + control features. Budget $X per bed. ROI through reduced medication use."
- Researcher: "14 studies support nature; effect size d ≈ 0.4–0.6. Strongest evidence in surgical recovery; weaker in routine hospitalization. Methodological concerns: [details]. Proposed studies needed: [list]."
- Student: "Hospitals stress patients because [mechanism]. Nature helps through [pathway]. This connects to [theory]."

**Actual (per code inspection)**:
1. **Query page** (1_query.py): Shows different common questions per persona. Different *button labels*, same underlying QA system.
2. **Response rendering**: Calls enrich_response() which returns persona-specific data (thresholds for architects, GRADE ratings for clinicians, glossary for students).
3. **BUT**: The underlying answer (headline/summary/detail) is identical across personas. Enrichment is *supplementary*, not *differentiating*.

**Example from code** (template_query_service.py, enrich_response):
```python
if persona == UserPersona.ARCHITECT:
    enrichment['thresholds'] = thresholds  # Add design parameters
elif persona == UserPersona.CLINICIAN:
    enrichment['grade_ratings'] = [...]     # Add GRADE ratings
elif persona == UserPersona.STUDENT:
    enrichment['glossary'] = glossary        # Add term definitions
```

This adds *supplementary data*, not *different answers*. If a practitioner asks "Why do plants reduce stress?" they get the same mechanism explanation as a researcher — just with fewer options to drill deeper.

#### Real Personalization (Not Currently Implemented)

**Researcher would want**:
- Effect size confidence interval, not just point estimate
- Between-study heterogeneity (I²), not just "multiple studies"
- Risk of bias assessment per study
- Which findings are most contested
- Replication status of key claims

**Practitioner would want**:
- Translated to design parameters: "30% more green view," "2.5m² per person nature access"
- ROI: "Natural daylighting costs $500/window; reduces stress medication by X%, saving $Y"
- Implementation timeline: "Can be added in 6 weeks, phased in 3 zones"
- Contraindications: "Nature views don't help patients with [condition]"

**Student would want**:
- Theory first: "ART says natural settings reduce stress via fascination, freeing directed attention. Here's an analogy: [example]"
- Key papers to read: "Start with Kaplan 1989; then move to Ulrich 1983"
- How this connects: "Connects to memory systems theory — nature builds stronger episodic memories"

**Current system provides**: Same headline, same evidence list, different *buttons* to click for supplementary info.

**Honest Assessment**: Personalization is **cosmetic, not substantive**. The Potemkin village analogy is accurate.

**Recommended Implementation** (real personalization):
1. **Researcher path**:
   - Query template_query_service with persona=RESEARCHER
   - Return effect_size (point + CI), not just headline
   - Include between-study heterogeneity
   - Show study designs (RCT vs observational)

2. **Practitioner path**:
   - Translate all findings to design parameters
   - Add cost-benefit analysis
   - Include implementation timeline

3. **Student path**:
   - Start with theory, then evidence
   - Link to key papers
   - Provide learning pathway

---

### D. Theory-Grounded Mechanisms (T1 Framework Voices)

**Spec Requirement** (§122.2): The system should surface expert panel comments from 10 T1 frameworks (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI), each offering a distinct perspective.

**Current Implementation**: Excellent infrastructure exists in `integrated_query_service.py`:
- All 10 frameworks defined with characteristic questions
- `FRAMEWORK_VOICES` dict with typical complications and speculation
- `PanelComment` dataclass for framework perspectives
- Method to generate panel comments from template response

**Integration Status**: Infrastructure exists but **is NOT surfaced in the UI**. The query page (1_query.py) doesn't call integrated_query_service; it calls arbitrary_qa_handler or template_query_service directly. The panel discussion data structure is prepared but never rendered.

**Finding**: The system *has* the panel expertise; it's not *used*.

**Recommended Integration**:
1. In query page, after showing headline + summary, offer expandable "Expert Panel Discussion" section
2. Show each framework's voice: "Predictive Processing says [perspective]; complication: [detail]"
3. Highlight framework disagreements: "Embodied Cognition emphasizes [X]; Dual Process emphasizes [Y]; tension: [explanation]"

---

### E. Contradiction Detection & Representation (Pearl's Causal Levels)

**Spec Requirement** (§122.2 + E1.D2): Show directional opposition, not just credence thresholds. Distinguish between "higher credence" and "directional disagreement."

**Current Implementation** (query_response.py):
- YES: `ContestedEvidence` section groups supporting vs. contradicting evidence
- YES: Explicit contested flag on beliefs
- YES: Directional opposition detection ("X increases Y" vs. "X decreases Y")
- YES: Shows count of supporting vs. contradicting items

**Quality Assessment**: GOOD. The system properly detects and flags contradictions. However:

1. **Presupposition of Pearl's Ladder** (§122.3): System distinguishes query causal level (associational/interventional/counterfactual) but doesn't always surface it. A user asking "Does nature reduce stress?" at ASSOCIATIONAL level might be shown intervention-level evidence, creating confusion.

2. **Scope Condition Clarity**: When contradictions exist, the system should highlight the scope boundary: "In surgical recovery, plants reduce stress (supporting n=6); in routine hospitalization, no effect (contradicting n=2). Why? Surgical patients have more control over their environment..."

**Current Gap**: Contradictions are flagged but not fully explained.

**Recommended Implementation**:
1. Always show causal level of query in headline: "(Associational: correlation evidence)"
2. When contradictions exist, add "Scope Analysis" section explaining the boundary
3. Use Cartwright's conflict typology (incompatibility vs. boundary violation) to distinguish types

---

### F. Gaps as Precise Questions (Q5: Gawande Principle)

**Spec Requirement** (§4.7.1, Q5): Gaps should have (a) non-vague target, (b) specified answer shape, (c) falsifiable anchor.

**Example** (Good):
- Gap: "We don't know if circadian disruption + noise together cause greater stress than noise alone"
- Target: Interaction effect (circadian × noise)
- Answer shape: RCT with 2×2 design; measure cortisol
- Falsifiable anchor: "Current hypothesis: main effects combine additively (no interaction)"

**Example** (Bad):
- Gap: "We don't understand the mechanism of biophilia"
- ← Vague target, no specified answer shape, no falsifiable anchor

**Current Implementation**: Gap identification exists; formatting is sparse. The system logs gaps but doesn't format them as precise questions.

**Recommended Implementation**:
1. Create `PreciseGap` data class with: target, answer_shape, falsifiable_anchor, difficulty_estimate
2. Apply Q5 logic when gap is surfaced: "To resolve this gap, we'd need: [study design]. The hypothesis would be falsified if: [condition]."
3. Compute difficulty_estimate (1 study? 5 studies? New methodology needed?) to help with prioritization

---

## Part 3: Epistemic Work Transparency

**Critical Finding**: The system does not show its epistemic work.

### What "Epistemic Work" Means

When the system says "Plants reduce stress (credence 0.72)," a user who understands epistemic rigor asks: "Why 0.72? What evidence points to 0.72, not 0.80 or 0.60?"

The answer should be:
1. **Supporting evidence**: 8 studies show effect; median d=0.45; mostly in hospital/recovery settings
2. **Undercutting defeaters**: 3 studies show no effect; confound: all used potted plants, not living walls
3. **Warrant ceiling**: "Can't exceed 0.85 because mechanism not fully resolved" (warrant constraint)
4. **Coherence constraints**: "Slightly lower because conflicts with [belief X] under [principle Y]"

### Current Status

| Aspect | Current | Spec Requirement | Gap |
|--------|---------|---|---|
| Show supporting vs contradicting evidence | YES | Required (P1) | GOOD |
| Show credence number | YES | Required (P1) | GOOD |
| Explain *why* that credence | NO | Required (Lipton IBE) | CRITICAL GAP |
| Show confidence interval | NO | Recommended for researchers | MISSING |
| Explain warrant ceiling | NO | Required (§122.1) | CRITICAL GAP |
| Show coherence constraints | NO | Implied (§122.2) | MISSING |

### Recommended Implementation

When rendering an answer with credence, add an "Epistemic Transparency" section:

```
Claim: Plants reduce stress in hospital patients
Credence: 0.72 (medium-high confidence)

Why 0.72?
  Supporting evidence:
    - 8 studies show effect (median Cohen's d = 0.45)
    - Strongest in ICU recovery (d = 0.62 ± 0.15)
    - Weaker in psychiatric wards (d = 0.18)

  Undercutting defeaters:
    - 3 studies show null result
    - All used potted plants; unclear if effect size scales with installation type

  Warrant ceiling: Can't exceed 0.85 because
    - Mechanism partially unresolved (ART vs. biophilia vs. stress recovery)
    - Population heterogeneity (surgical vs psychiatric vs medical)

  Coherence constraints:
    - Slightly reduced from 0.75 due to tension with [belief about lighting color]
      (both can't both be true under current constraint network)
```

---

## Part 4: Missing Mechanisms (How the System Works)

The system does NOT implement the following mechanisms from the spec:

| Mechanism | Spec Location | Required By | Implementation |
|---|---|---|---|
| **Presupposition Checking** | Q1 norm (§4.7.1) | Every question | MISSING |
| **Contrast Class Generation** | Q2 norm (§4.7.1) | Comparison/Mechanism questions | PARTIAL |
| **Problem Type Classification** | Q3 norm (§4.7.1) | Every generated gap | MISSING |
| **Value of Information (VOI)** | Q4 norm + §3.3 | Question prioritization | MISSING |
| **VOI Threshold Filtering** | §4.7.1 (θ_VOI = 0.15) | Question acceptance | MISSING |
| **Prerequisite Hierarchy** | Q6 norm (§4.7.1) | Complex questions | MISSING |
| **Seam-Targeting** | Q7 norm (§4.7.1) | Conflict detection | WEAK |
| **Science Writer Norms** | §7 (P11–P17) + §4.7.2 | Answer composition | PARTIAL |
| **Warrant Tracing** | §2 (warrant structure) | Confidence explanation | WEAK |
| **Causal Level Pearl's Ladder** | §122.3, Pearl intro | Query interpretation | PARTIAL |

---

## Part 5: Assessment by User Type

### Practitioner / Designer

**Spec Promise** (§122.2): "Evidence-based design decisions for real-world projects"

| Information Need | Spec Says | System Provides | Quality |
|---|---|---|---|
| Specific design parameters (dimensions, materials, quantities) | D₁, D₂, ... thresholds | YES — from extract_calibrated_thresholds() | GOOD |
| Cost-benefit analysis | ROI calculations | NO | MISSING |
| Implementation timeline | When to apply, how to phase | NO | MISSING |
| Risk / contraindications | When NOT to apply | NO, just general caveats | MISSING |
| Precedent / case studies | "How was this done elsewhere?" | Implicitly in evidence base; not surfaced | WEAK |

**Honest Assessment**: System provides *what* to design (parameters); doesn't always provide *why* (mechanism) or *when* (implementation timeline) or *risks* (contraindications).

### Senior Researcher

**Spec Promise**: "Comprehensive literature reviews and evidence synthesis"

| Information Need | Spec Says | System Provides | Quality |
|---|---|---|---|
| Effect size + CI | Required for research questions | Credence shown; no formal CI | WEAK |
| Between-study heterogeneity (I²) | Required for meta-analytic interpretation | NO | MISSING |
| Risk of bias assessment | GRADE / Cochrane criteria | NO | MISSING |
| Study designs (RCT vs observational) | Evidence strength depends on design | Metadata exists; not surfaced | WEAK |
| Replication status | Key papers replicated or contested? | Contradictions shown; replication status implicit | WEAK |
| Research gaps with feasibility | "What should we study next?" | Gaps identified; not prioritized by VOI | WEAK |

**Honest Assessment**: System can show evidence base; doesn't provide *research-grade* synthesis. A researcher would need to export the data and do their own meta-analysis.

### Graduate Student

**Spec Promise**: "Learning the field and finding thesis direction"

| Information Need | Spec Says | System Provides | Quality |
|---|---|---|---|
| Clear theory explanations | Theory guides available | YES — TheoryGuideService exists | GOOD |
| Key papers to read | Canonical references | YES — key_references in templates | GOOD |
| Thesis direction options | Research gaps → thesis ideas | Gaps exist; not packaged as thesis opportunities | WEAK |
| How this connects to other fields | Cross-domain integration | Panel discussion could help; not surfaced | WEAK |
| Learning pathway | "What should I learn first?" | Q6 prerequisite hierarchy not implemented | MISSING |

**Honest Assessment**: Student gets good introduction; doesn't get structured learning pathway or thesis direction guidance.

---

## Part 6: Response Depth Implementation

**Good news**: Progressive disclosure is well-implemented.

| Mode | Name | Purpose | Implementation | Quality |
|---|---|---|---|---|
| L1 | HEADLINE | One-sentence answer | Explicit | GOOD |
| L2 | SUMMARY | Key evidence + confidence | Evidence list shown | GOOD |
| L3 | DETAIL | Full trace with citations | Detail level includes all evidence + scope | GOOD |
| L4 | DEEP_DIVE | Complete epistemology | Includes deep_dive field (research gaps, theory debate) | MEDIUM |
| Bonus | Persona enrichment | Persona-specific supplementary data | Architect thresholds, clinician GRADE, student glossary | MEDIUM |

**Assessment**: Structure is good. Content is moderate. The system can show more at deeper levels but often doesn't.

---

## Part 7: Specification Success Conditions (Did We Meet Them?)

From INTERPRETATION_SPACE_SPEC §4.7.3:

| Success Condition | Target | Current Status | Pass/Fail |
|---|---|---|---|
| SC-Q1: ≥95% presuppositions verified | 95% | ~10% | FAIL |
| SC-Q2: ≥80% MECHANISM/COMPARISON have explicit contrast | 80% | ~30% | FAIL |
| SC-Q3: 100% questions carry problem_type label | 100% | ~0% | FAIL |
| SC-Q4: All questions carry VOI estimate | 100% | ~0% | FAIL |
| SC-Q5: ≥90% questions non-vague + answer-shape + falsifiable | 90% | ~20% | FAIL |
| SC-Q6: ≥90% questions satisfy prerequisites | 90% | ~0% | FAIL |
| SC-Q7: ≥80% conflict questions target seam | 80% | ~40% | FAIL |
| SC-R4-OPEN: Questions pass 80% composite Q-norm | 80% | ~15% | FAIL |
| SC-R4-CLOSE: Answers ≥0.6 on 5 rubric dimensions | 0.6 | ~0.55 | FAIL (borderline) |

**Overall**: 0 of 9 success conditions met. The system architecture supports the specs; the implementation doesn't activate most of the epistemic machinery.

---

## Part 8: Critical Gaps Summary

### Tier 1 (Must Fix for Epistemic Integrity)

1. **Presupposition Validation (Q1)**
   - Implement: Before asking "Why does X?" check credence(X) ≥ 0.5
   - Impact: Prevents vacuous questions
   - Effort: Medium (requires credence lookup in web_of_belief)

2. **Epistemic Work Transparency**
   - Implement: Show *why* credence is X not Y (supporting + undercutting evidence + warrant ceiling)
   - Impact: Builds user trust; explains reasoning
   - Effort: Medium (template already structured)

3. **Real User Type Personalization**
   - Implement: Different *answers*, not just different *buttons*
   - Researcher: Effect size + CI + heterogeneity
   - Practitioner: Design parameters + ROI + timeline
   - Student: Theory-first + reading path
   - Impact: System becomes 3× more useful for each user type
   - Effort: High (requires reimplementation of query routing)

### Tier 2 (Should Fix for Completeness)

4. **Value of Information (VOI) Computation**
   - Implement: Estimate structural_impact × tractability × |generators| for each gap
   - Impact: Priorities questions; prevents time-wasting interrogation
   - Effort: Medium

5. **Theory-Grounded Mechanism Surfacing**
   - Implement: Activate integrated_query_service panel discussion in UI
   - Impact: Provides multiple expert perspectives
   - Effort: Low (code exists; needs UI rendering)

6. **Problem Type Classification (Laudan)**
   - Implement: Label each gap as empirical / conceptual / methodological / bridging
   - Impact: Routes questions to appropriate evidence type
   - Effort: Medium

### Tier 3 (Nice to Have)

7. **Contrast Class Validation (Q2)**
   - Implement: For COMPARISON/MECHANISM questions, verify contrast class specified
   - Impact: Prevents ambiguous questions
   - Effort: Low–Medium

8. **Prerequisite Hierarchy Enforcement (Q6)**
   - Implement: Only ask cross-domain questions after main effects established
   - Impact: Prevents premature complex questions
   - Effort: Medium

---

## Part 9: Recommendations

### Immediate (Next 2 Weeks)

1. **Add Q-norm Validation Service**
   ```python
   class QNormValidator:
       def validate_presupposition(question, web_of_belief) -> Tuple[bool, str]
       def validate_contrast_class(question) -> Tuple[bool, List[str]]
       def validate_problem_type(gap) -> problem_type
       def compute_voi(gap) -> float
       def validate_composite(question) -> float  # 0-1 compliance
   ```

2. **Implement Epistemic Work Display**
   - In QueryResponse, add `epistemic_analysis` field showing:
     - Supporting evidence items with direction
     - Undercutting defeaters
     - Warrant ceiling reason
     - Coherence constraints

3. **Add Researcher Personalization Path**
   - Create `researcher_response()` method in template_query_service
   - Return effect_size (point + CI), between-study heterogeneity, study designs
   - Include GRADE quality assessment

### Short-term (Next 4 Weeks)

4. **Activate Panel Discussion in UI**
   - Modify query page (1_query.py) to show T1 framework panel comments
   - Use integrated_query_service for deep_dive mode

5. **Implement VOI Filtering**
   - Add `value_of_information.py` service
   - Filter gaps: only surface VOI ≥ threshold
   - Explain: "We identified this gap but it's low-priority because..."

6. **Add Practitioner Design Parameter Translation**
   - Create `design_translator.py` service
   - Map template claims to design parameters (dimensions, materials, quantities)
   - Include ROI calculations and implementation timeline

### Medium-term (Next 8 Weeks)

7. **Fully Implement Q-Norms**
   - Integrate QNormValidator into arbitrary_qa_handler question generation
   - Track compliance metrics (target 80% composite)
   - Add expert review loop for high-compliance audit

8. **Implement Real Problem Type Classification (Laudan)**
   - Classify every gap: empirical vs conceptual vs methodological vs bridging
   - Route to appropriate evidence source
   - Show user: "This requires [type of evidence]"

9. **Overhaul User Type Personalization**
   - Eliminate cosmetic differences (same button labels)
   - Implement substantive path differences
   - Test with personas: same question → 3 genuinely different answers

---

## Part 10: Technical Debt & Architectural Notes

### Clean Debt (Easy to Fix)

1. `arbitrary_qa_handler.py` is 1,798 lines; should be split into:
   - QuestionClassifier
   - QuestionRouter
   - CatalogAnswerer
   - AIAnswerer

2. `template_query_service.py` format_for_persona() method is 500+ lines; extract per-persona formatters

3. `query_response.py` ProgressiveResponse class is good; but response building logic is scattered

### Structural Debt (Requires Thought)

1. **Persona handling**
   - Currently: persona is a parameter that adds supplementary data
   - Should be: persona determines *everything* (query path, evidence selection, answer composition)
   - Refactor: Create PersonaStrategy pattern; each persona is a separate strategy class

2. **QA Agent Architecture** (§122.2)
   - Spec describes panel-based design (Lipton, Gopnik, Bereiter, Shneiderman, Simon)
   - Implementation: Uses panels only for infrastructure
   - Missing: Actual panel reasoning (multiple experts considering same answer)

3. **Epistemic Network Integration**
   - Web of Belief exists and is rich
   - QA system doesn't fully leverage credence, warrants, defeaters
   - Recommendation: Create `warrant_tracer.py` service to explain credence via web structure

---

## Conclusion

The ATLAS QA system has **excellent infrastructure but incomplete implementation**. The master doc specifications are clear and sophisticated; the code demonstrates good architecture and understanding. The gaps are not in design but in *activation* — the epistemic machinery is built but not engaged.

**Key Takeaway**: A user interacting with the system will find it helpful and accurate, but will not see the epistemic rigor promised by §122. The system explains *what* the evidence says; it rarely explains *how confident to be and why*.

**Estimate for Full Compliance**: 12–16 weeks with a focused team of 2–3 engineers.

**Priority**: Fix Tier 1 gaps first (presupposition validation, epistemic transparency, real personalization). These enable the system to live up to its design specifications.

---

## Appendix A: Files Audited

- `/src/services/arbitrary_qa_handler.py` (1,798 lines)
- `/src/services/template_query_service.py` (2,400+ lines)
- `/src/services/integrated_query_service.py` (600+ lines)
- `/src/services/knowledge_catalog.py` (500+ lines)
- `/src/services/query_parser.py` (500+ lines)
- `/src/services/query_response.py` (400+ lines)
- `/streamlit_app/pages/1_query.py` (400+ lines)
- `/streamlit_app/pages/9_knowledge_base.py` (200+ lines)
- `/streamlit_app/config.py` (250+ lines)
- `docs/master_doc_parts/PART_XV_TECHNICAL.md` (§122)
- `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md` (§4.7)
- `contracts/MATH_EXPLANATION_NORMS.md`

---

**Report Status**: FINAL
**Next Review Date**: 2026-03-16 (post Tier 1 implementation)

---

*Generated by Claude Code (Haiku 4.5) for David Kirsh, UCSD Cognitive Science*
*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
