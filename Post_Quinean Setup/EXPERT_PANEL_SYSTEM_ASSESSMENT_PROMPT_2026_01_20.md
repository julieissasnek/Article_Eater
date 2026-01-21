# Expert Panel System Assessment Prompt
## Article Eater Post-Quinean v1 — Critical Review Request
**Date**: January 20, 2026
**Prepared by**: Development Team
**Purpose**: Ruthless assessment of system robustness, gaps, and future direction

---

## EXECUTIVE SUMMARY

Article Eater V21.0.0 (Post-Quinean) is a research system that extracts evidence-backed rules from scientific articles and integrates them into a Quinean Web of Belief for CNFA (Cognitive Neuroscience of Focused Attention) neuroarchitecture research.

**Current Status**:
- Sprints 1-7: COMPLETE and TESTED (470+ tests passing)
- Sprints 8-9: PENDING (Theory integration, BN export)
- Core: 25 service modules, 20,000+ LOC
- Schemas: 11 versioned JSON contracts
- Documentation: Comprehensive

**Request to Panel**: Assess this system with maximum skepticism. Identify what is genuinely complete vs. what is cosmetically complete. Find the gaps between specification and reality. Challenge our assumptions about user needs and workflow design.

---

## PANEL COMPOSITION

### Core Advisors (Constructed from Published Work)
1. **Dr. Judea Pearl** — Bayesian networks, causal inference, counterfactual reasoning
2. **Dr. Nancy Cartwright** — Philosophy of science, bridge warrants, causal pluralism
3. **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
4. **Dr. Marcia Bates** — Information science, knowledge organization, search behavior
5. **Dr. Rachel Kaplan** — Environmental psychology (primary domain expert)

### Additional Specialists for This Review
6. **Workflow Designer** — Task analysis, user journey mapping, cognitive load
7. **GUI/UX Expert** — Interface design, visual information display, interaction patterns
8. **Systems Architect** — Integration patterns, data flow, scalability concerns
9. **Epistemologist** — Coherentist vs. foundationalist critique, Quinean implementation fidelity

---

## PART I: USER USE CASES (SCRUTINIZE THESE)

### Primary Stakeholder: Practicing Architect
The system must serve architects who want to make evidence-based design decisions.

**UC1: Image-to-Evidence Lookup**
> An architect uploads/feeds an image of a proposed design. The system analyzes tags/features, matches against the BN rule database, and returns probabilistic effects on outcomes (stress, creativity, wayfinding, etc.).

*Challenge Questions*:
- How does image tagging integrate with the extraction pipeline?
- What is the data flow from image → tags → rule lookup → BN query → probability output?
- Is any of this currently implemented? (Answer: NO - this is aspirational)
- What components are missing?

**UC2: Network Probing with Epistemic Context**
> A researcher queries the network: "What affects creativity in open-plan offices?" The system returns not just articles/answers but epistemic metadata: uncertainty levels, conflicting evidence, bridge warrant types, scope conditions.

*Challenge Questions*:
- Does the current API support this query pattern?
- Can the system return coherence-aware search results?
- How does VOI search inform the response?
- What output format does the user see?

**UC3: VOI-Driven Experiment Recommendations**
> A researcher asks: "What experiment should I run next to maximize knowledge gain?" The system identifies epistemic gaps (UNCERTAIN vs UNEXPLORED), calculates value-of-information, and recommends specific studies.

*Challenge Questions*:
- Is VOI calculation domain-weighted?
- How does the system distinguish "uncertain" (conflicting evidence) from "unexplored" (no evidence)?
- Does it recommend study designs or just topics?
- Is there a GUI for this? (Answer: NO)

### Secondary Stakeholder: Graduate Student
Students need to learn the field and understand the evidence landscape.

**UC4: Theory-Mechanism Understanding**
> A student asks: "What theories explain why natural light improves mood?" The system returns theories, their mechanisms, supporting/conflicting evidence, and how the theories relate to each other.

*Challenge Questions*:
- Is the theory system integrated with the pipeline? (Answer: SCHEMA exists, integration INCOMPLETE)
- Can the system retrieve theories by outcome construct?
- Does it show theory-theory relationships (subsumption, competition, refinement)?

**UC5: Measurement Method Education**
> A student asks: "How do researchers measure stress in architectural studies?" The system returns measurement methods, their epistemic levels (self-report vs. physiological vs. behavioral), and papers using each method.

*Challenge Questions*:
- Does outcome_taxonomy.py expose measurement method queries?
- Is there an API endpoint for this?
- What output format does the student see?

**UC6: Field Overview Generation**
> A student asks: "Give me an overview of theories about attention in built environments." The system returns a structured summary: major theories, key phenomena, open questions, methodological debates.

*Challenge Questions*:
- Can the system generate this summary automatically?
- Does interpretive_intelligence.py support overview-level explanations?
- What is the quality of auto-generated overviews vs. hand-written ones?

**UC7: Backward Reasoning (Effect → Cause)**
> A student asks: "What environmental properties affect creativity? Do they interact?" The system returns causal variables, their effect sizes, confidence levels, and interaction patterns.

*Challenge Questions*:
- Does the BN support this query pattern (effect → cause)?
- How are interactions represented? (Answer: CausalDirection enum includes MEDIATED, but interaction modeling is unclear)
- Can the system distinguish direct effects from mediated effects?

### Additional Use Cases (Generated for Completeness)

**UC8: Contradiction Detection and Resolution**
> A researcher notices two studies report opposite effects of the same variable. The system explains the contradiction: scope conditions differ, measurement methods differ, or genuine anomaly.

*Challenge Questions*:
- Does web_persistence.py categorize contradiction types? (Answer: YES - DIRECT_CONTRADICTION, SCOPE_BOUNDARY, PRECISION_BOUNDARY)
- Can the system automatically explain contradictions?
- Is there a GUI for contradiction review?

**UC9: Bridge Warrant Audit**
> A researcher is skeptical about applying lab findings to real buildings. The system shows all bridge warrants, their types (mechanism, functional, analogical, constitutive), and confidence levels.

*Challenge Questions*:
- Can users query bridges by type or confidence?
- Is there a visual representation of bridge networks?
- How do users provide feedback on bridge quality?

**UC10: Longitudinal Web Evolution Tracking**
> A researcher wants to see how beliefs have evolved over multiple paper ingestions. The system shows credence trajectories, belief additions/revisions, and coherence score history.

*Challenge Questions*:
- Does web_persistence.py support history queries? (Answer: YES - snapshots, rollback)
- Is there a visualization of web evolution?
- Can users compare web states at different timepoints?

**UC11: Publication Bias Assessment**
> A researcher asks: "Is there publication bias in studies of biophilic design?" The system uses null_result_indicators.yaml to assess whether null results are underrepresented.

*Challenge Questions*:
- Is NullResultDetector integrated into search recommendations?
- Can the system quantify publication bias risk?
- Does it recommend specific search strategies to counteract bias?

**UC12: Cross-Domain Knowledge Transfer**
> A researcher asks: "Can findings from hospital design apply to school design?" The system assesses bridge warrant applicability across domains.

*Challenge Questions*:
- Does bridge_warrants.py support domain-to-domain transfer assessment?
- What are the conditions for valid transfer?
- How does the system flag risky transfers?

**UC13: Teaching Module Generation**
> A professor wants to create a teaching module on "evidence-based design principles." The system generates structured content with citations, confidence levels, and open questions.

*Challenge Questions*:
- Can interpretive_intelligence.py generate teaching-appropriate content?
- Does it distinguish "well-established" from "emerging" findings?
- Is there an export format for course materials?

**UC14: Hypothesis Refinement Assistance**
> A PhD student has a hypothesis: "Natural views reduce stress more than nature sounds." The system returns relevant evidence, identifies gaps, and suggests refinements.

*Challenge Questions*:
- Can the system parse natural language hypotheses?
- Does it map hypotheses to existing beliefs/constraints?
- Can it suggest testable predictions?

**UC15: Systematic Review Support**
> A researcher is conducting a systematic review. The system identifies all relevant papers, extracts standardized data, flags methodological concerns, and generates PRISMA-style outputs.

*Challenge Questions*:
- Is this currently possible? (Answer: Partially - extraction exists, but no PRISMA output)
- What manual steps remain?
- How does this integrate with existing review tools (Covidence, etc.)?

---

## PART II: CRITICAL GAPS IDENTIFIED

### GAP 1: No GUI Exists
**Severity**: CRITICAL for user adoption

The entire system is CLI/API-based. No graphical interface exists for any use case.

*Questions for Panel*:
- What is the minimum viable GUI for architect users?
- Should we prioritize web-based or desktop?
- What visualizations are essential (network graph, credence trajectories, contradiction maps)?

### GAP 2: Theory System Integration Incomplete
**Severity**: HIGH

The theory database schema is complete (017_theories.sql), and TheoryRegistry class exists, but there is NO pipeline integration. Theories are not extracted from papers or linked to predictions.

*Questions for Panel*:
- Should theory extraction be automatic (LLM-based) or manual (human annotation)?
- How do we link predictions to empirical evidence?
- What is the theory confidence update rule when evidence conflicts?

### GAP 3: BN Export Semantics Undefined
**Severity**: HIGH for architect use cases

The pipeline has BN export stubs (version 0.2), but there is no specification for:
- How to calculate priors from web coherence
- How to generate CPTs from belief credences
- How to handle causal direction (FORWARD/REVERSE/BIDIRECTIONAL)

*Questions for Panel*:
- Dr. Pearl: How should Quinean coherence inform BN priors?
- Should the BN be a direct mapping, or a separate derived structure?
- What BN format should we export to (BIFXML, Hugin, etc.)?

### GAP 4: Image Integration Absent
**Severity**: HIGH for UC1

No component exists for:
- Image upload/ingestion
- Tag extraction from images
- Tag-to-rule matching

*Questions for Panel*:
- Should image tagging be internal (trained model) or external (user provides tags)?
- What tag vocabulary should we use?
- How do we handle ambiguous images?

### GAP 5: Natural Language Query Interface Absent
**Severity**: MEDIUM

Users cannot ask questions in natural language. All queries are structured API calls.

*Questions for Panel*:
- Is NL query essential, or can structured queries suffice?
- If NL, should we use LLM-based query parsing?
- What query types must be supported?

### GAP 6: Collaboration/Multi-User Support Absent
**Severity**: LOW for research, HIGH for production

The system is single-user. No support for:
- Multiple concurrent users
- Shared webs
- Permission controls
- Audit trails for multi-user edits

*Questions for Panel*:
- Is multi-user essential for initial release?
- What collaboration patterns matter (shared web vs. personal forks)?

### GAP 7: Real-Time Feedback Loop Absent
**Severity**: MEDIUM

Users cannot easily provide feedback on extraction quality, belief credences, or bridge warrant assessments. The feedback_store.py exists but is not integrated into workflows.

*Questions for Panel*:
- What feedback is most valuable?
- How should feedback update the web?
- Should there be an "expert override" mechanism?

---

## PART III: TECHNICAL ARCHITECTURE STATUS

### What IS Implemented (Verified)

| Component | Status | Evidence |
|-----------|--------|----------|
| PDF text extraction | ✓ | app/pdf_ingest.py |
| Claim/rule extraction | ✓ | LLM-based + pattern extraction |
| Claim → Belief mapping | ✓ | extraction_to_web.py, 30+ tests |
| Web of Belief state machine | ✓ | web_of_belief.py, 1606 LOC |
| Constraint validation | ✓ | validation.py, 47 tests |
| Equilibrium seeking | ✓ | configurable, converges |
| Bridge warrant detection | ✓ | bridge_warrants.py, 27 tests |
| Web persistence/merging | ✓ | web_persistence.py, 62 tests |
| Credibility testing | ✓ | credibility_testing.py, 60 tests |
| Interpretive explanations | ✓ | interpretive_intelligence.py, 65 tests |
| VOI search | ✓ | voi_search.py, 76 tests |
| Outcome taxonomy | ✓ | outcome_taxonomy.py, 26 tests |
| Environment taxonomy | ✓ | environment_taxonomy.py, 35 tests |
| Vocabulary bridge | ✓ | vocabulary_bridge.py, 28 tests |

### What is PARTIALLY Implemented

| Component | Status | Gap |
|-----------|--------|-----|
| Theory system | Schema only | No pipeline integration |
| BN export | Stubs only | No semantics |
| API routes | Minimal | No query endpoints |

### What is NOT Implemented

| Component | Notes |
|-----------|-------|
| GUI | None |
| Image processing | None |
| NL query parsing | None |
| Multi-user support | None |
| Real-time feedback | Partial |

---

## PART IV: QUINEAN FIDELITY ASSESSMENT

### Philosophical Commitments (Claimed)

1. **No foundational beliefs** — All beliefs revisable
2. **Coherence as criterion** — Justification from fit, not accumulation
3. **Mutual constraint** — Beliefs constrain each other bidirectionally
4. **Stubs as liminal** — Findings that don't fit are held, not forced
5. **Bridge warrants explicit** — Cross-domain transfer licensed explicitly

### Implementation Fidelity (Assess Critically)

*Questions for Epistemologist*:
- Does the equilibrium-seeking algorithm truly implement reflective equilibrium, or is it just optimization?
- When the system revises a belief, does it consider ALL affected beliefs (Quinean holism), or just local neighbors?
- How does the system avoid collapsing into a form of foundationalism through "central" beliefs that never get revised?
- Are stubs genuinely held in liminal status, or does the system pressure toward integration?
- Does the coherence score capture genuine coherence, or just consistency?

---

## PART V: WORKFLOW DESIGN QUESTIONS

*Questions for Workflow Designer*:

1. **Primary Task Analysis**: For each use case, what is the user's primary task? What decisions do they need to make? What information supports those decisions?

2. **Cognitive Load**: The system exposes many dimensions (credence, coherence, bridge type, scope conditions, etc.). How do we present this without overwhelming users?

3. **Error Recovery**: When the system makes a mistake (wrong extraction, bad bridge), how does the user notice and correct it?

4. **Learning Curve**: How steep is the learning curve for each user type (architect, researcher, student)? What training is needed?

5. **Trust Calibration**: How do users learn to trust the system appropriately — neither over-trusting nor dismissing it?

---

## PART VI: GUI/UX DESIGN QUESTIONS

*Questions for GUI/UX Expert*:

1. **Visual Vocabulary**: How do we visually represent:
   - Credence levels (0.0 to 1.0)
   - Coherence scores
   - Bridge warrant types
   - Contradiction categories
   - Scope conditions

2. **Network Visualization**: The web of belief is a graph. How do we visualize it usefully? What are the interaction patterns (zoom, filter, focus)?

3. **Query Interface**: Natural language? Structured forms? Faceted search? What combination serves each user type?

4. **Explanation Display**: interpretive_intelligence.py generates explanations. How do we display them? Expandable sections? Tooltips? Separate panel?

5. **Feedback Mechanisms**: How do users provide feedback (thumbs up/down, text, structured correction)?

---

## PART VII: SYSTEMS ARCHITECTURE QUESTIONS

*Questions for Systems Architect*:

1. **Scalability**: The current system is SQLite-based. At what scale does this become a bottleneck? What is the migration path?

2. **Integration Points**: How does this system integrate with:
   - Reference managers (Zotero, Mendeley)
   - BN tools (GeNIe, Netica)
   - Design tools (Revit, SketchUp)
   - LMS systems (Canvas, Moodle)

3. **API Design**: What API patterns best serve the use cases? REST? GraphQL? WebSocket for real-time?

4. **Deployment**: On-premises vs. cloud? Single-tenant vs. multi-tenant?

5. **Data Portability**: How do users export their webs? What formats?

---

## PART VIII: SPECIFIC EXPERT QUESTIONS

### For Dr. Pearl:
1. Given that the Quinean web has no foundational beliefs, how should we calculate BN priors? Is there a coherence-based prior?
2. The system tracks CausalDirection (FORWARD, REVERSE, BIDIRECTIONAL, COMMON_CAUSE, MEDIATED). How should these map to BN edge semantics?
3. When evidence conflicts, the system revises beliefs via equilibrium seeking. Should the BN automatically update, or should it be regenerated?

### For Dr. Cartwright:
1. Bridge warrants can fail. When they do, should failure evidence revise the source theory (Quinean approach) or just flag the bridge as unreliable?
2. Scope boundary conflicts occur when the same variable behaves differently in different contexts. Should we create context-specific beliefs, or keep one belief with scope conditions?
3. How do we handle "capacity" claims that require enabling conditions to manifest?

### For Dr. Simon:
1. The VOI search uses epsilon-greedy with decay. Is this the right satisficing strategy, or should we use Thompson sampling?
2. Users face many choices (which papers to trust, which bridges to accept). How do we design for bounded rationality without patronizing experts?
3. When should the system stop searching (stopping rules)? Current implementation uses budget-based limits.

### For Dr. Bates:
1. The vocabulary bridge translates between expertise levels (academic, practitioner, common). Are these the right levels? Missing any?
2. How should we handle terminological drift as fields evolve?
3. What search interaction patterns best serve exploratory information seeking?

### For Dr. Kaplan:
1. The outcome taxonomy covers CNFA constructs. Are there important constructs missing?
2. How should we handle constructs that don't fit the current ontology (stubs)?
3. What domain-specific validation would you recommend?

---

## PART IX: DELIVERABLE REQUEST

Please provide:

1. **Gap Analysis**: For each use case (UC1-UC15), assess:
   - Feasibility with current system
   - Components needed to enable
   - Priority (critical/high/medium/low)

2. **Architecture Recommendations**: What structural changes are needed?

3. **Workflow Designs**: For the top 3 use cases, sketch the user workflow

4. **GUI Mockup Concepts**: What are the essential screens?

5. **Priority Roadmap**: What should we build next, and in what order?

6. **Risk Assessment**: What could go wrong? What are we missing?

7. **Quinean Fidelity Report**: Does the implementation honor the philosophical commitments?

---

## APPENDIX A: REPOSITORY STRUCTURE

```
Article_Eater_PostQuinean_v1/
├── src/services/           # Core Python services (25 modules, 20K+ LOC)
│   ├── web_of_belief.py    # Core epistemic engine (1606 LOC)
│   ├── extraction_to_web.py # Claim → Belief mapper (1073 LOC)
│   ├── bridge_warrants.py  # Cross-domain transfer (1014 LOC)
│   ├── web_persistence.py  # Storage & merging (2385 LOC)
│   ├── credibility_testing.py # Update decisions (1054 LOC)
│   ├── interpretive_intelligence.py # Human explanations (1621 LOC)
│   ├── voi_search.py       # Search recommendations (1218 LOC)
│   └── ... (18 more services)
├── app/
│   ├── tasks/pipeline.py   # Main extraction pipeline (1400+ LOC)
│   ├── main.py             # FastAPI server
│   └── cli/                # CLI entry points
├── contracts/ae_af/schemas/ # 11 JSON schemas
├── contracts/vocab/        # Vocabulary files
├── db/sql/                 # Database schemas
├── tests/                  # 470+ tests
└── docs/                   # Architecture & planning
```

---

## APPENDIX B: SPRINT COMPLETION STATUS

| Sprint | Component | Status | Tests |
|--------|-----------|--------|-------|
| 1 | extraction_to_web.py | COMPLETE | ~30 |
| 2 | Pipeline integration | COMPLETE | ~35 |
| 3 | Bridge warrants | COMPLETE | 27 |
| 4 | Outcome taxonomy | COMPLETE | 26 |
| 5 | Web persistence | COMPLETE | 62 |
| 6 | Causal direction, scope | COMPLETE | 31 |
| 7 | Environment taxonomy | COMPLETE | 35 |
| 8 | Theory integration | PENDING | - |
| 9 | BN export, docs | PENDING | - |

---

## APPENDIX C: TEST COMMANDS

```bash
# Run all tests
pytest -q

# Run specific test file
pytest tests/test_web_of_belief.py -v

# Run with coverage
pytest --cov=src/services tests/
```

---

*End of Assessment Request*

**Please be ruthless. Identify what doesn't work, what's missing, and what we're fooling ourselves about.**
