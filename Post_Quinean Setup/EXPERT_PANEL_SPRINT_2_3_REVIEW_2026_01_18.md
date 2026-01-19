# Expert Panel Review: Sprint 2 Decisions + Sprint 3 Specification

**Date**: Sunday, January 18, 2026
**Purpose**: Convene expert panel to review Sprint 2 implementation decisions and specify Sprint 3
**Context**: Claude Code implemented Sprint 2 without sufficient specification; design decisions need validation

---

## BACKGROUND FOR NEW CLAUDE INSTANCE

### Project Overview

Article Eater V21.0.0 (Post-Quinean) extracts evidence-backed rules from scientific papers about how built environments affect human cognition, emotion, and behavior. The system uses **Quinean coherentist epistemology** (Web of Belief) rather than foundationalist accumulation.

**Owner**: Professor David Kirsh, UCSD Cognitive Science

**Repo**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`

### Architecture (Four Tracks)

```
TRACK A: EXTRACTION PIPELINE (production)
PDF → Seven-Panel LLM extraction → claims.jsonl + rules.jsonl
Location: app/tasks/pipeline.py

TRACK B: WEB OF BELIEF (research)
In-memory coherentist epistemology
Location: src/services/web_of_belief.py (1300+ lines)

TRACK C: THEORY REGISTRY (database)
SQLite-backed theory/prediction storage
Location: src/services/theory_registry.py

TRACK D: DUAL EPISTEMOLOGY (analysis)
Foundationalist vs. Coherentist comparison
Location: src/services/dual_epistemology.py
```

### Sprint Status

- **Sprint 1**: COMPLETE - `src/services/extraction_to_web.py` mapper (claims→beliefs)
- **Sprint 2**: IMPLEMENTED BUT NEEDS REVIEW - Pipeline integration
- **Sprint 3**: NOT STARTED - Bridge warrants (needs specification)
- **Sprints 4-8**: Pending

### Key Quinean Concepts

1. **Nothing is foundational** - all beliefs are revisable
2. **Justification via coherence** - not accumulation of independent facts
3. **BN is derivative** - Bayesian Network generated FROM web, not primary
4. **Stubs** - findings that don't fit current ontology (held, not forced or dropped)
5. **Bridge warrants** - explicit assumptions licensing domain transfer

---

## EXPERT PANEL MEMBERS

Convene these constructed voices (from their published work):

- **Dr. Judea Pearl** — Bayesian networks, causal inference
- **Dr. Nancy Cartwright** — Philosophy of science, bridge warrants
- **Dr. Herbert Simon** — Bounded rationality, system design
- **Dr. Marcia Bates** — Information science, knowledge organization
- **Dr. Rachel Kaplan** — Environmental psychology (the domain)

---

## PART 1: SPRINT 2 DECISIONS REQUIRING REVIEW

Sprint 2 integrated the extraction_to_web.py mapper into pipeline.py. The following decisions were made without expert consultation:

### Decision 2.1: Fresh Web Per Paper vs. Cumulative

**What was implemented**: Each paper gets a fresh `WebOfBelief` instance. Beliefs do not accumulate across papers in a single pipeline run.

**Rationale assumed**: Sprint 5 is titled "Persistence & Accumulation" - so Sprint 2 intentionally does NOT accumulate.

**Questions for panel**:
- Is this correct? Should Sprint 2 produce isolated per-paper webs?
- Or should there be an option to integrate into an existing web?
- What are the epistemological implications of isolated vs. cumulative integration?

### Decision 2.2: Graceful Degradation

**What was implemented**: If web_of_belief imports fail or integration throws an exception, the pipeline continues and returns `"web_integration": "skipped"` or `"failed"`. Extraction outputs (claims.jsonl, rules.jsonl) are still produced.

**Questions for panel**:
- Should web integration failure block the entire pipeline?
- Is silent degradation appropriate, or should it be louder (warning, error)?
- What's the contract with downstream consumers?

### Decision 2.3: Schema Formalization

**What was implemented**: I invented schemas on the fly:
- `ae.web_state.v1` for web_state.json
- `ae.coherence_summary.v1` for coherence_summary.json

**The spec said**: "Update contracts per governance requirements"

**What I didn't do**: Create formal JSON schemas in `contracts/ae_af/schemas/`

**Questions for panel**:
- Should these be formal contracts with versioned schemas?
- What fields are required vs. optional?
- Who consumes these files and what do they need?

### Decision 2.4: Web State Serialization

**What was implemented** in web_state.json:
```json
{
  "schema": "ae.web_state.v1",
  "run_id": "...",
  "paper_id": "...",
  "created_at": "...",
  "n_beliefs": 10,
  "n_constraints": 5,
  "coherence_score": 0.416,
  "beliefs": {
    "belief_id": {
      "content": "first 200 chars...",
      "level": "EMPIRICAL",
      "status": "TENTATIVE",
      "credence": 0.75,
      "theory_id": "SRT",
      "entrenchment": 0.3
    }
  },
  "integration_report": { ... }
}
```

**Questions for panel**:
- Is this the right level of detail?
- Should we serialize the full belief content or truncate?
- Should constraints be serialized too?
- Is this format suitable for Sprint 5 persistence?

### Decision 2.5: Equilibrium Parameters

**What was implemented**: Hardcoded `seek_equilibrium=True` and `equilibrium_iterations=5`

**Questions for panel**:
- Should these be configurable (env vars, profile settings)?
- What's the right default number of iterations?
- Should equilibrium-seeking be optional for speed?

### Decision 2.6: Output File Conditionality

**What was implemented**: New files (web_state.json, stubs.jsonl, tensions.jsonl, coherence_summary.json) are only written if integration succeeds. On failure, they're not created.

**Questions for panel**:
- Should we write empty/error files on failure for consistency?
- What should downstream consumers expect?

---

## PART 2: SPRINT 3 SPECIFICATION NEEDED

The current specification for Sprint 3 is:

> "Sprint 3: Bridge Warrant Foundation
> - Schema extension with `bridge` field
> - Bridge types: mechanism, functional, analogical, constitutive
> - Bridge-weighted credence calculation"

This is insufficient to implement. The panel should address:

### Question 3.1: Where Does the Bridge Field Live?

Options:
- In `ae.claim.v1` schema (extraction-time annotation)
- In `ae.rule.v1` schema (rule-level annotation)
- In `Belief` class (web-of-belief internal)
- In `Constraint` class (edge-level annotation)
- New `ae.bridge.v1` schema (separate entity)

### Question 3.2: How Is Bridge Type Determined?

Options:
- LLM inference during extraction (add to 7-panel prompt)
- Manual annotation (HITL review step)
- Heuristic from claim/rule properties
- Default assignment with manual override

### Question 3.3: Bridge-Weighted Credence Formula

The handoff document mentions:
```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

Questions:
- Is this the target formula?
- What's the default P(bridge) for each bridge type?
- How does this interact with existing credence computation in extraction_to_web.py?
- Should bridge strength be continuous (0-1) or categorical?

### Question 3.4: Bridge Failure Handling

The Bar & Neta → Vartanian example:
- Bar & Neta found amygdala activation for angular objects
- Vartanian found ACC (not amygdala) activation for angular rooms
- The mechanism bridge FAILED

Questions:
- How do we represent bridge failure in the web?
- Does failed bridge create a tension? An anomaly?
- How does this inform VOI (value of information)?

### Question 3.5: Bridge Warrant Schema

If we create `ae.bridge.v1`, what fields?

Proposed structure (for panel review):
```json
{
  "schema": "ae.bridge.v1",
  "bridge_id": "bridge:001",
  "source_domain": "object_perception",
  "target_domain": "architectural_perception",
  "bridge_type": "mechanism|functional|analogical|constitutive",
  "warrant_statement": "Angular objects and angular rooms share threat-detection pathway",
  "assumed_mechanism": "amygdala activation",
  "confidence": 0.6,
  "evidence_for": ["claim:001", "claim:002"],
  "evidence_against": ["claim:003"],
  "status": "hypothesized|supported|failed|revised"
}
```

### Question 3.6: Integration Points

Where does bridge warrant logic go?
- New file `src/services/bridge_warrants.py`?
- Extension to `extraction_to_web.py`?
- Extension to `web_of_belief.py`?

---

## PART 3: DELIVERABLES REQUESTED

After panel deliberation, please provide:

1. **Sprint 2 Validation**: Approve/revise the 6 decisions above
2. **Sprint 3 Specification**: Detailed enough to implement, including:
   - Schema definitions
   - Algorithm/formula specifications
   - Integration points
   - Test cases or examples
3. **Any Schema Updates**: If formal contracts needed, specify fields

---

## CONTEXT FILES TO READ

If the new Claude instance needs more context:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project guidance, governance rules |
| `docs/SYSTEM_OVERVIEW.md` | Architecture summary |
| `src/services/extraction_to_web.py` | Sprint 1 mapper (just updated) |
| `src/services/web_of_belief.py` | Core Quinean engine |
| `app/tasks/pipeline.py` | Sprint 2 integration point |
| `Post_Quinean Setup/1/CNFA_STATE_HANDOFF_2026_01_18.md` | Full project handoff |

---

## COMMUNICATION STYLE

David prefers:
- Clean academic writing (Bertrand Russell style)
- Thorough explanations over brevity
- Clear timestamps on everything
- Explicit about what's certain vs. uncertain
- APA citations with DOIs where relevant

---

*Document created: Sunday, January 18, 2026*
*For use in Claude.ai Project "Post_Quinean AE" to convene expert panel*
