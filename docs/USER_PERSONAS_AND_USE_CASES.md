# ATLAS User Personas & Use Cases

**Date:** 2026-03-01  
**Purpose:** Defines who uses the system and how — addresses V8 audit UX gap  

---

## User Personas

### P1: Research Faculty (Primary)
- **Example:** Professor of Cognitive Science / Environmental Psychology
- **Expertise:** Deep domain knowledge, limited coding
- **Goals:** Query evidence, generate design recommendations, publish findings
- **Tolerance:** Low for technical errors, high for conceptual complexity
- **Key need:** "What does the evidence say about X?" → actionable answer with citations

### P2: Graduate Researcher
- **Expertise:** Moderate coding, learning the domain
- **Goals:** Add papers to the system, explore theory connections, write literature reviews
- **Tolerance:** Medium for both technical and conceptual complexity
- **Key need:** Systematic literature exploration with cross-referencing

### P3: Design Practitioner
- **Expertise:** Architecture/interior design, no coding, limited research literacy
- **Goals:** Evidence-based design recommendations for real projects
- **Tolerance:** Zero for jargon; needs plain language
- **Key need:** "For a building with properties X, Y, Z → what does evidence predict?"

### P4: System Maintainer
- **Expertise:** Python developer, moderate domain knowledge
- **Goals:** Keep pipelines running, fix failures, improve coverage
- **Tolerance:** Expects good error messages and logs
- **Key need:** AESHI dashboard, reflex reports, pipeline status

---

## Core Use Cases

### UC1: Evidence Query
**Actor:** P1 (Faculty), P2 (Researcher)  
**Trigger:** "What does evidence say about ceiling height and creativity?"  
**Flow:**
1. User enters query in Grounded Expert Agent interface
2. System searches beliefs by template relevance
3. System returns layered response (Level 0: summary → Level 5: theory)
4. Each claim links to source paper, finding, and warrant strength
5. User can drill down into any claim's provenance chain

**Success:** User gets a source-cited, multi-level answer in <10 seconds  
**Current status:** ✅ Backend works (grounded_expert_agent.py). ⚠️ UI integration partial.

### UC2: Add New Paper
**Actor:** P2 (Researcher), P4 (Maintainer)  
**Trigger:** New paper acquired, PDF available  
**Flow:**
1. Paper enters extraction queue (manual or via acquisition pipeline)
2. Gemini extracts structured findings (2-run verification)
3. QA validates extraction quality (field validator)
4. Integration cascade maps findings to beliefs, creates constraints
5. AESHI recalculates; reflexes check for problems

**Success:** Paper's findings are integrated as beliefs with provenance  
**Current status:** ✅ Pipeline works E2E. ⚠️ Requires API key and manual trigger.

### UC3: Challenge a Belief
**Actor:** P1 (Faculty)  
**Trigger:** "I disagree with belief X based on new evidence"  
**Flow:**
1. User identifies belief in the web
2. User supplies contradicting evidence (paper, finding)
3. System creates a CONTRADICTS constraint
4. Coherence recalculation adjusts credence
5. If credence drops below threshold, belief is flagged for review

**Success:** Belief credence adjusts based on new counter-evidence  
**Current status:** ⚠️ Backend supports it (constraint creation). ❌ No UI for this workflow.

### UC4: Design Recommendation
**Actor:** P3 (Practitioner)  
**Trigger:** "I'm designing a university library — what should I consider?"  
**Flow:**
1. User describes building type and constraints
2. System identifies relevant templates (lighting, acoustics, wayfinding, etc.)
3. System retrieves grounded beliefs for each template
4. System generates ranked recommendations with confidence levels
5. Each recommendation links to supporting evidence

**Success:** Actionable, evidence-based design checklist  
**Current status:** ❌ Not implemented as a workflow. Backend data exists.

### UC5: Provenance Trace
**Actor:** P1 (Faculty), P4 (Maintainer)  
**Trigger:** "Why does the system believe X?"  
**Flow:**
1. User selects a belief
2. System shows: source paper → extraction finding → template match → warrant type → ω score
3. User can inspect each link in the chain
4. System shows supporting and contradicting constraints

**Success:** Complete audit trail from belief back to PDF  
**Current status:** ✅ Data exists in epistemic_v2. ⚠️ No unified UI for traversal.
