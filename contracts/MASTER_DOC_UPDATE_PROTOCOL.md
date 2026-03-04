# MASTER_DOC_UPDATE_PROTOCOL.md

## Mandate: Standardized Context and Decision Documentation

*Effective: 2026-03-04*
*Owner: David Kirsh, UCSD Cognitive Science*

---

## 1. The Problem This Protocol Solves

The ATLAS research system (Article Eater) produces three primary outputs:

1. **Working code and data**: Extraction pipeline, Bayesian networks, QA systems
2. **Research findings**: Evidence networks, causal structures, theoretical synthesis
3. **Documentation**: The master document (155+ sections, 26+ parts, academic treatise)

Currently, agents (AG/Gemini, CW/Claude, CC/Claude Code) do excellent work on outputs 1 and 2, but the documentation of their reasoning rarely reaches output 3 in a form that CW can directly integrate into the master document.

**Consequence**: The master document becomes stale. Design decisions are made and implemented, but the rationale, alternatives considered, and integration points are lost. When future readers ask "Why did we build the extraction pipeline this way?", the answer exists only in agent session logs, scattered across COORDINATION.md, or embedded in code comments.

**Solution**: This protocol mandates that every significant work session produces a "Master Doc Brief" (MDB) — a structured document that captures context, reasoning, decisions, and implications in a form that CW can read once and integrate directly into the master document with minimal translation.

---

## 2. What Counts as "Significant Work" (MDB Required)

Not every small fix requires an MDB. The following thresholds trigger MDB production:

### 2.1 Code/Schema Threshold

- **≥100 lines of new code** (across all files touched)
- **Any schema change** (extraction_template.v2.schema.json, success_conditions.json, etc.)
- **Any new data structure** or major refactoring of existing one

Examples:
- ✅ Add a 140-line reflex class to reflex_system.py → MDB required
- ✅ Modify extraction_template.json to add 8 field groups → MDB required
- ❌ Fix a 12-line bug in error handling → MDB NOT required
- ❌ Rename a variable across 3 files → MDB NOT required

### 2.2 Conceptual Threshold

- **Any new concept, service, or subsystem** introduced to the project
- **Any decision about epistemic architecture** (how beliefs are scored, how web coherence is computed, etc.)
- **Any change to the extraction or interpretation pipeline logic** (what passes where, what gates are applied)
- **Any new vocabulary or ontological category** (new annotation types, new theory classifications, etc.)

Examples:
- ✅ Design a new QA subsystem that routes questions to different handlers → MDB required
- ✅ Introduce "task-ecological validity" as a fourth channel of confidence → MDB required
- ✅ Add a new annotation type (A9–A18 expansion) → MDB required
- ❌ Fix typos in schema documentation → MDB NOT required
- ❌ Update comments to clarify existing code → MDB NOT required

### 2.3 Design Decision Threshold

- **Any choice between 2+ alternatives** where rationale matters for future understanding
- **Any integration point** between subsystems or data flows
- **Any calibration or parameter selection** with justification

Examples:
- ✅ Decide to use a 0.55 default credence for coherence-only warrants (Decision 1.5) → MDB required (capture rationale)
- ✅ Redesign the annotation flow to feed provenance into QA handlers → MDB required
- ❌ Use Python 3.10 instead of 3.9 (obvious, not interesting) → MDB NOT required
- ❌ Choose between two equivalent library functions with no downstream implications → MDB NOT required

### 2.4 Multi-Session Work Threshold

- **Any work that spans multiple sessions** or requires handoff between systems

Examples:
- ✅ CW completes Phase 1B of extraction overhaul; AG will do Phases 2-6 → Both should produce MDBs
- ✅ AG runs experiments, sends results to CW for integration and master doc writeup → AG produces MDB for experiments, CW produces MDB for integration
- ✅ Parallel work on vision attributes and CVA integration → Each system produces MDB for their portion

---

## 3. The Master Doc Brief (MDB) Template

Every MDB follows this structure. Agents fill it out completely.

```markdown
# Master Doc Brief: [AGENT] [DATE] [TOPIC]

**MDB ID**: MDB-{AGENT}-{DATE-ISO}-{TOPIC-SLUG}
**Agent**: AG | CW | CC
**Date**: YYYY-MM-DD
**Session Duration**: [HH:MM] or [multisession over HH:MM]
**Status**: DRAFT | FINAL

---

## Context & Motivation

### Problem Statement
What problem did this work solve? State it in 2-3 sentences. If this is exploratory work without a specific problem, describe the gap or opportunity.

### Why This Matters
Connect this work to:
- System health (AESHI, test coverage, etc.)
- User experience (QA system, web UI, reporting)
- Research quality (evidence quality, coherence computation, epistemic rigor)
- Timeline/blockers (is this on critical path?)

Use metrics where available. Example: "This work unblocks H12 re-extraction, which improves AESHI from 49→70 (estimate)."

---

## What Was Done

### 1. Concrete Deliverables
List every artifact created or modified:

| File/Artifact | Type | Lines | Description |
|---|---|---|---|
| `src/qa/extraction_field_validator.py` | NEW | 680 | Validation rules engine with 50+ rules for 11 extraction fields |
| `contracts/schemas/extraction_quality_rules.json` | NEW | 312 | Machine-readable validation ruleset |
| `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md` | NEW | 1,554 | Framework spec and validation rationale |

For MODIFIED files, indicate: "50 lines added, 12 lines removed, structure unchanged" or similar.

### 2. How It Works
Describe the design at a level that a future architect could understand it:
- What is its input? What does it output?
- What are the major steps, subsystems, or components?
- How does it connect to the rest of the system?

Aim for 300-500 words. Use diagrams if they clarify structure.

### 3. Testing & Validation
- What tests were run? How many pass?
- Were success conditions (SC-*) defined or modified?
- Any gaps or known limitations?

Example: "29 unit tests pass. Validates against 1,009 articles (35,122 findings). Mean quality 0.786. 391 articles below 0.75 quality threshold — these are flagged for re-extraction."

---

## Design Decisions

For each decision (choice between 2+ alternatives):

### Decision D{N}: {Title}
- **Context**: Why did this decision arise? What triggered the choice?
- **Alternatives Considered**: List 2+ options. For each, state pros and cons.
  - Option A: Pro1, Pro2 | Con1, Con2
  - Option B: Pro1, Pro2 | Con1, Con2
- **Rationale**: Why was this alternative chosen?
- **Risk Level**: LOW | MEDIUM | HIGH
  - Justification: What could go wrong? How reversible is this?
- **Dependencies**: Other decisions this affects or depends on
- **Panel Concerns**: Which expert voices should review this? (e.g., Spohn on probability calibration, Haack on coherence weighting, Pearl on causal inference)

---

## Epistemic Implications

### 1. Impact on the Web of Belief
How does this work affect the epistemic network? Examples:
- "This adds 12 new vocabulary terms to the outcome ontology → web size from 116 to 128 terms."
- "This validator filters out 391 low-quality extractions → removes 2.7% of beliefs from integration."
- "This coherence-weighting change shifts default warrant strength from 0.45 to 0.55 → affects confidence calculations for 4,888 existing beliefs."

### 2. Impact on AESHI (System Health)
How does this work affect the Automated Epistemic System Health Index?
- Which AESHI metrics does it improve/worsen? By how much?
- Example: "Extraction pipeline audit score: 3.5/10 (before) → 7.35/10 (after). Improves antecedent_specificity (89% → 99.7%) and direction_normalization (72% → 99.1%)."

### 3. Impact on Downstream Systems
What systems consume this? What will break or change?
- Extraction pipeline (yes/no, how)
- QA system (yes/no, how)
- BN integration (yes/no, how)
- Master document (yes/no, how)
- Visualization/reporting (yes/no, how)

### 4. Uncertainty & Open Questions
What didn't you know? What remains uncertain?
- Example: "We don't know how to extract effect_sizes from qualitative papers. 78.2% of articles have null effect_size in extraction."
- Example: "Template_ids column is empty in beliefs table (4,888 rows). Blocking 10 AESHI points. Root cause unclear — investigate in next session."

---

## New Concepts Introduced

If this work introduces new terminology, frameworks, or abstractions, document them here:

### Concept: [Name]
- **Definition**: Plain-English explanation
- **Notation/Terminology**: How it's referred to in code and docs
- **Where Used**: Which files, subsystems, or sections of master doc
- **Relation to Existing Concepts**: How it connects to or extends prior work

Example:
```markdown
### Concept: Task-Ecological Validity
- **Definition**: The degree to which an experimental task recreates the authentic ecological context of how humans use real buildings (not just passive observation).
- **Notation**: `task_ecological_validity` (float 0–1) or `TaskClass` enum (EXPLICIT_EVALUATION, LAB_COGNITIVE_TASK, SIMULATED_ECOLOGICAL, REAL_TASK_CONTROLLED, NATURAL_BEHAVIOR)
- **Where Used**: extraction_template.v2.schema.json (field), validity_scorer.py (computation), reflex_system.py (quality check)
- **Relation to Existing Concepts**: Extends source_quality (methodological_rigor, measurement_validity, presentation_validity) with a fourth channel specific to architectural settings. Operationalizes Bronfenbrenner's ecological validity framework for CNFA domain.
```

---

## Files Affected in Master Document

Which Parts and sections of the master document should be updated or created to reflect this work? (CW uses this to navigate the master doc.)

| Part | Sections | Type | Action |
|---|---|---|---|
| Part III.2 | "Extraction Pipeline Architecture" | Section | ADD subsection on validation gating |
| Part IV.1 | "Web of Belief — Coherence Computation" | Section | MODIFY confidence_calculation to note 0.55 default for coherence-only |
| Part V | "Method Registry & Task-Ecological Validity" | NEW | CREATE entire part with framework spec + seed data |

---

## Panel Review Needed?

Indicate whether expert panel review should occur before integrating this work:

- [ ] No panel review needed (low-risk, straightforward implementation)
- [ ] Quick panel feedback desired (moderate-risk, want expert validation before full integration)
- [ ] Full panel consultation required (high-risk, architectural significance, novel theory)

**If panel review needed:**
- **Scope**: What specific decisions or design choices need expert eyes?
- **Panelists**: Which epistemic authorities? (Spohn, Pollock, Haack, Mayo, Cartwright, Pearl, Longino, Simon, Thagard, etc.)
- **Turnaround**: When is feedback needed by?
- **Blocking**: Does this work block other tasks pending panel feedback?

Example:
```markdown
- [x] Full panel consultation required
- **Scope**: D-AE-3 (Cultural calibration default weights: 0.35 rigor + 0.30 independence + 0.20 replication + 0.15(1-commitment_penalty)). Is this the right decomposition? Should independence be weighted higher?
- **Panelists**: Longino (independence norms), Cartwright (causal sufficiency), Mayo (experimental warrant)
- **Turnaround**: By 2026-03-08 (before H12 re-extraction runs)
- **Blocking**: Yes — AG needs panel clearance before weighting production runs
```

---

## Success Conditions Defined/Modified

Did this work define or modify any success conditions (SC-*)?

| SC ID | Type | Definition | Tests | Status |
|---|---|---|---|---|
| SC-EFV-1 | Validation | All extractions pass quality gate ≥0.75 | test_extraction_quality_gate.py | 12 pass |
| SC-EFV-2 | Validation | No violations for consistency rules CONSIST-1..5 | test_consistency_rules.py | 29 pass |

---

## Version History & Integration Checkpoints

**For multi-session work**: Track versions of the artifact and any major revision points.

| Version | Date | Key Change | By | Status |
|---|---|---|---|---|
| v1.0 | 2026-02-28 | Initial schema with 11 fields | CW | COMPLETE |
| v2.0 | 2026-03-01 | Added 8 principle-compliance fields | CW | COMPLETE |
| v2.1 | 2026-03-02 | Validator gate + blocking behavior | CW | READY FOR PANEL |

---

## References & Evidence

### Grounding
- Where in ATLAS (EN or BN) do we have evidence for the choices made here?
- Example: "CH-1 (Biophilia in Mediterranean culture) grounded in 18 papers from ATLAS extraction database. Calibration parameters: Berlyne coherence weights from 4 empirical studies, panel consensus on independence of evidence sources."

### External Literature
- What papers, frameworks, or prior art justified this work?
- Example: "Task-ecological validity framework adapted from Bronfenbrenner (1979) and Kiviniemi et al. (2007) applied to VR studies. Clinical precedent: Fich et al. (2014) CAVE-based TSST protocol."

---

## Next Steps & Known Gaps

### Immediate Follow-Up
What should happen next? Are there obvious next steps?
- Example: "H12 re-extraction of 59+1,002 articles using v3 prompts should run immediately to populate theory_commitments, mechanism_chain, and instruments_used fields."

### Known Gaps & Limitations
What didn't you get to? What remains uncertain or broken?
- Example: "Effect_size extraction remains at 21.8% coverage. Gemini prompts need revision for qualitative papers. Investigate in next AG session."

### Dependencies Created
If this work creates new blockers or dependencies, list them:
- Example: "Template_ids backfill (MT-15) blocks 10 AESHI points. Requires DB schema migration 023 (pending)."

---

## Appendices (Optional)

Include detailed reference material if helpful:
- Detailed algorithm descriptions
- Full schema definitions
- Code snippets illustrating non-obvious design patterns
- Validation data tables
- Panel feedback (if review already occurred)
```

---

## 4. Where MDBs Go

All Master Doc Briefs are stored in `/docs/master_doc_briefs/` with this naming convention:

```
MDB_{AGENT}_{DATE-ISO}_{TOPIC-SLUG}.md
```

Examples:
- `MDB_CW_2026-02-28_EXTRACTION-FIELD-VALIDATOR.md`
- `MDB_AG_2026-03-01_VISION-ATTRIBUTES-BATCH1.md`
- `MDB_CC_2026-03-04_OVERSEER-FIXES.md`

### Directory Structure

```
docs/
  master_doc_briefs/
    README.md                          (this file, explains the system)
    MDB_CW_2026-02-28_*.md            (CW briefs)
    MDB_AG_2026-03-01_*.md            (AG briefs)
    MDB_CC_2026-03-04_*.md            (Claude Code briefs)
    _index.md                          (auto-generated index of all MDBs)
```

### Auto-Generated Index

CW maintains a quick index in `docs/master_doc_briefs/_index.md`:

```markdown
# Master Doc Brief Index

| Date | Agent | Topic | Status | Master Doc Impact |
|---|---|---|---|---|
| 2026-02-28 | CW | Extraction Field Validator | FINAL | Part III.2, Part IV.1 |
| 2026-03-01 | AG | Vision Attributes Batch 1 | FINAL | Part VI, Part VII |
| 2026-03-04 | CC | Overseer Critical Fixes | FINAL | Part III.3 |
```

CW regenerates this weekly or after significant MDB additions.

---

## 5. How CW Uses MDBs

CW's workflow when integrating an MDB into the master document:

### 5.1 Intake Process
1. **Read the MDB entirely** — understand context, decisions, implications
2. **Check "Files Affected in Master Document"** section — know which Parts need updating
3. **Scan for new concepts** — verify they're consistent with existing terminology
4. **Cross-reference with COORDINATION.md and TASKS.md** — confirm this work aligns with recorded status

### 5.2 Integration Process
1. **Open the relevant Part files** from `docs/master_doc_parts/`
2. **Extract key content from the MDB** — the "How It Works" section, design decisions, new concepts
3. **Rewrite for master doc prose style** using `contracts/WRITING_STYLE_GUIDE.md` and `contracts/SCIENCE_COMMUNICATION_NORMS.md`
4. **Add references** — cite the MDB, link to code/data artifacts
5. **Update section word counts** in Part headers
6. **Add to figure dependencies** if new figures are needed (via `contracts/FIGURE_DEPENDENCIES.json`)

### 5.3 Quality Gates for Integration
- All decision rationales are preserved (not lost in translation)
- New concepts are defined consistently with existing terminology
- Dependencies and integration points are explicit
- Panel feedback (if any) is incorporated
- References and grounding are complete

---

## 6. Enforcement Mechanism

### 6.1 Startup Protocol (Mandatory)

Every session starts by reading this file. Each agent's initial instructions (in CLAUDE.md, COORDINATION.md, or system prompt) include:

> **MASTER DOC UPDATE PROTOCOL (Mandatory)**
>
> Before doing significant work, scan this session's scope:
> - Will you create ≥100 lines of code?
> - Are you introducing new concepts or design decisions?
> - Are you changing the extraction/interpretation pipeline?
>
> If YES to any, plan to produce an MDB before/after completion.

### 6.2 Session Completion Checklist

After completing significant work, agents must verify:

- [ ] I have read `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` this session
- [ ] My work meets the "Significant Work" threshold (§2)
- [ ] I have created an MDB in `docs/master_doc_briefs/` following the template (§3)
- [ ] The MDB includes all required sections (Context, What Was Done, Design Decisions, Epistemic Implications, New Concepts, Master Doc Impact, Panel Review, Success Conditions)
- [ ] I have updated COORDINATION.md with:
  - Sprint Status (what I completed)
  - Any new items in Handoff Queue or Micro-Task Queue
  - Any blockers or dependencies created
- [ ] I have updated TASKS.md with completion dates for any tasks finished
- [ ] If this is multi-agent work, I have noted the MDB ID in COORDINATION.md for the receiving agent

### 6.3 Nightly Pipeline Check (Optional)

A future automated check can scan for:
- Sessions with ≥100 lines of code changes → no corresponding MDB created → flag for agent
- MDB files with DRAFT status → prompt for finalization
- MDBs with high-risk decisions → flag that panel review is pending

### 6.4 Master Doc Update Milestone

Before any major public release or publication:
1. CW performs a full audit of `docs/master_doc_briefs/` (all MDBs from the development cycle)
2. Verifies that every significant work item has an MDB
3. Integrates all MDBs into the master document
4. Updates `_index.md` and commits

---

## 7. Quality Standards: Good vs. Bad MDBs

### What Makes a Good MDB

✅ **Good MDB Characteristics:**
- **Concrete and specific**: Names files, reports metrics, cites decision points. No vague statements like "improved things".
- **Grounds decisions in alternatives**: For each decision, lists at least 2 options and explains the choice. Doesn't assert without justification.
- **Connects to system architecture**: Shows how this work fits into the broader ATLAS design (EN, BN, QA, extraction, etc.).
- **Epistemic clarity**: Explains how this affects credence, coherence, source quality, or other epistemically interesting properties.
- **Usable by CW**: CW can read this once and integrate it into the master doc without asking for clarification.
- **Completed promptly**: Produced within 1 day of work completion (not weeks later from memory).

### What Makes a Bad MDB

❌ **Bad MDB Characteristics:**
- **Vague summary**: "Fixed extraction stuff" or "improved quality" without concrete details
- **Decision without rationale**: "We chose option A" without explaining why A was better than B and C
- **Disconnect from architecture**: Describes work in isolation without showing integration points
- **Overly technical**: Assumes reader has memorized the codebase; doesn't explain design choices at an architectural level
- **Incomplete sections**: Skips "Epistemic Implications" or "Master Doc Impact" because "it's obvious"
- **Stale**: Written weeks after work is complete, from fuzzy memory (dates are off, details are wrong)

### Examples

#### Good MDB (Simplified)

```markdown
# Master Doc Brief: CW 2026-02-28 Extraction Field Validator

**Agent**: CW
**Date**: 2026-02-28
**MDB ID**: MDB-CW-2026-02-28-EXTRACTION-FIELD-VALIDATOR

## Context & Motivation

### Problem Statement
1,009 extracted articles contain inconsistent or low-quality data in 11 key fields (antecedent, outcome, direction, effect_size, sample_size, study_design, etc.). No systematic validation existed. Mean quality 0.62, with wide variance (0.12–0.98). This blocks downstream Bayesian integration because low-quality data corrupts the network.

### Why This Matters
Directly affects AESHI: improves extraction_quality metric from 0 (no validation) to field-specific scores. Unblocks H5 (QA_QUALITY_GATE integration) and H12 (re-extraction of low-quality articles).

## What Was Done

### 1. Concrete Deliverables
- `src/qa/extraction_field_validator.py` (680 lines, NEW)
- `contracts/schemas/extraction_quality_rules.json` (312 lines, NEW)
- `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md` (1,554 lines, NEW)
- `tests/test_extraction_field_validator.py` (412 lines, NEW)

### 2. How It Works
The validator applies 50+ rules to each extraction across 11 fields. Rules check:
- **Enum consistency**: direction ∈ {increases, decreases, bidirectional, no_effect}
- **Logical constraints**: if direction = no_effect, effect_size should be ≈0
- **Completeness**: mandatory fields must be populated
- **Reference integrity**: outcome_id must exist in vocab; antecedent_id must reference a coded entity

Violations are aggregated into a quality_score (0–1) per article. Articles < 0.75 are flagged for re-extraction.

### 3. Testing & Validation
- 29 unit tests pass (all rule types + boundary conditions)
- Validated against 1,009 articles: mean quality 0.786, std 0.187
- 391 articles below 0.75 threshold (38.7% — alarming but expected for pilot extraction)
- Violations persisted to `data/extractions/needs_repair/`

## Design Decisions

### Decision D1: Threshold of 0.75 for Tier 1 Re-extraction
- **Rationale**: Pilot extraction was aggressive; 0.75 captures "borderline usable" data. Higher threshold (0.85) would flag 62% of articles (too many to re-extract immediately). Lower threshold (0.60) would miss obvious defects.
- **Risk**: MEDIUM — impacts downstream quality. If 0.75 is too permissive, BN integration suffers.
- **Dependencies**: Affects H9 re-extraction scope (200 articles vs. 400).
- **Panel Concerns**: Cartwright (causal sufficiency), Mayo (error severity trade-off)

## Epistemic Implications

### 1. Impact on Web of Belief
- Removes ~391 low-quality beliefs from integration (2.7% of 14,538 pre-filtered beliefs)
- Remaining 14,147 beliefs scored by extraction_quality ≥0.75
- Improves overall belief credence by reducing noise

### 2. Impact on AESHI
- New metric: `extraction_quality` (currently 0, after validation: estimated 0.786)
- Improves AESHI from estimated 65→72 (subject to actual pipeline run)

## Files Affected in Master Document
| Part | Section | Action |
|---|---|---|
| Part III.2 | Extraction Pipeline Architecture | ADD subsection on QA gating |
| Part IV | Web of Belief Epistemic Properties | MODIFY with extraction_quality metric |

## Panel Review Needed?
- [x] Quick panel feedback desired
- **Scope**: Is 0.75 threshold appropriate? Should we tier the re-extraction (0.75–0.85 batch vs. <0.60 batch)?
- **Turnaround**: Before H9 re-extraction launch (2026-03-01)
```

#### Bad MDB (For Comparison)

```markdown
# Master Doc Brief: CW 2026-02-28 Field Validation

**Agent**: CW
**Date**: 2026-02-28
[rest of fields minimally filled]

## Context & Motivation

### Problem Statement
Need to validate extraction data to improve quality.

### Why This Matters
It matters for the overall system.

## What Was Done

### 1. Deliverables
- Validator code
- Tests
- Documentation

### 2. How It Works
We check that extractions are valid. If they fail, we flag them.

### 3. Testing
Tests pass. Most articles are OK.

## Design Decisions

### Decision 1: Use threshold of 0.75
We thought this was a good threshold.

## Panel Review Needed?
[ ] Probably not.

---
```

The **bad MDB** is useless to CW because:
- Vague problem statement (what specific data was wrong?)
- No concrete metrics (mean quality? distribution?)
- No justification for 0.75 (why not 0.80? 0.60?)
- Missing integration details (what does "flag for re-extraction" mean? How many articles?)
- No epistemic implications (how does this affect AESHI? credence?)
- CW would have to read the code to understand what was actually built

---

## 8. Fast Track for Small Changes

Not every change needs a full MDB. The lightweight alternative is a **"Change Note"** in COORDINATION.md:

### When to Use Change Notes Instead of MDB

- Bug fixes <50 lines
- Test additions without new test infrastructure
- Documentation updates (excluding new major sections)
- Minor refactors (renaming, restructuring without logic changes)

### Change Note Format (in COORDINATION.md)

Add a new table in the Sprint Status section:

```markdown
### Change Notes (Lightweight — No Full MDB)

| Date | Agent | File | Change | Impact |
|---|---|---|---|---|
| 2026-03-04 | CC | overseer.py | Fixed SQL query in `_count_total_beliefs()` — queried wrong table | AESHI score: 65→70 |
| 2026-03-04 | CC | reflex_system.py | Removed NotImplementedError from sanity check | Test suite: 6,509 pass |
```

These are lightweight (2–3 sentences each) and don't require the full MDB structure. But if a fix has epistemic implications or creates new design decisions, it should still get an MDB.

---

## 9. Integration Timeline

### Per-Session Cycle

1. **Start of session**: Agent reads CLAUDE.md (which references this protocol) + COORDINATION.md
2. **During session**: Agent does work, takes notes on decisions and implications
3. **End of session**: Agent produces MDB (if work is significant) OR adds Change Note to COORDINATION.md
4. **Commit**: Agent commits MDB to git along with any code/data changes

### Weekly Integration Cycle

1. **CW reads all MDBs produced this week** (every Monday AM)
2. **CW integrates MDBs into master document Parts**
3. **CW updates _index.md** with MDB status
4. **David/panel members can review integrated content** and provide feedback

### Monthly/Pre-Release Cycle

1. **Full audit of MDBs** for the month
2. **Verify all significant work has corresponding MDB**
3. **Update master document with any MDB content not yet integrated**
4. **Version master document** (update header dates, part counts)
5. **Commit and tag** for release

---

## 10. Tools & Automation (Future)

The following tools could automate parts of this system:

### 10.1 MDB Template Generator
```bash
python3 scripts/generate_mdb.py --agent CW --date 2026-03-04 --topic EXTRACTION-VALIDATOR
```
Generates a skeleton MDB with all sections and current date filled in.

### 10.2 Lint & Validation
```bash
python3 scripts/validate_mdb.py docs/master_doc_briefs/MDB_CW_2026-02-28_*.md
```
Checks that:
- All required sections present
- No section is empty placeholder text
- File naming is correct
- Decision rationales are non-trivial (not "seemed good")

### 10.3 Index Generator
```bash
python3 scripts/regenerate_mdb_index.py
```
Scans all MDBs and regenerates `_index.md` with counts, agent breakdown, master doc impact matrix.

### 10.4 Master Doc Integration Assistant
```bash
python3 scripts/integrate_mdb.py --mdb MDB_CW_2026-02-28_VALIDATOR.md --target docs/master_doc_parts/PART_III_2_EXTRACTION.md
```
Suggests where MDB content should be integrated and shows context.

---

## 11. Governance

### 11.1 Ownership & Amendments

**Owner**: David Kirsh
**Stewards**: CW (integration workflow), AG/CC (compliance)

Amendments to this protocol require David's approval. Proposed changes should be documented as a formal proposal (why the change, what it affects, implementation plan) and discussed in a session.

### 11.2 Exemptions

David may grant exemptions for:
- Emergency bug fixes (system down)
- Small collaborative experiments (less than 4 hours)
- Routine maintenance tasks

Exemptions should be noted in COORDINATION.md with brief justification.

### 11.3 Violations

If an agent completes significant work without an MDB:
1. **First time**: CW adds a retroactive MDB (draft status) and notes the gap in COORDINATION.md
2. **Repeated violations**: David discusses with agent about time/process issues
3. **Patterns**: Process is refined (e.g., threshold is too high, format is too heavy)

---

## 12. Success Metrics

This protocol is working if:

1. **Master document is up-to-date** — every significant work from last 3 months is reflected in Parts
2. **Design decisions are recoverable** — future readers can understand why a choice was made by reading the MDB
3. **CW integration time is <1 hour per MDB** — format is usable, not a translation burden
4. **Cross-system handoffs are clear** — MDBs make it obvious what AG built vs. what CW integrated
5. **Panel review is focused** — panel doesn't have to ask for context; MDBs provide it
6. **No silent work** — David is not surprised by architectural decisions he didn't know were made

---

## Appendix A: Template Checklist

Before submitting an MDB, verify:

- [ ] **MDB ID and metadata** — Agent, Date (ISO format), Topic slug, Status (DRAFT|FINAL)
- [ ] **Context section** — Problem statement (2-3 sentences), Why it matters (metrics where possible)
- [ ] **What Was Done** — Concrete deliverables table, How It Works (300-500 words), Testing summary
- [ ] **Design Decisions** — At least one decision documented with Context/Alternatives/Rationale/Risk/Dependencies/Panel Concerns (if applicable)
- [ ] **Epistemic Implications** — 4 subsections (Web of Belief, AESHI, Downstream Systems, Uncertainty)
- [ ] **New Concepts** — If any, fully defined with notation, usage, and relation to existing concepts
- [ ] **Master Doc Impact** — Table showing which Parts and sections need updating
- [ ] **Panel Review** — Clearly stated (Yes/No/Maybe) with scope and turnaround if applicable
- [ ] **Success Conditions** — Any SC-* defined or modified, with test status
- [ ] **Next Steps & Gaps** — Immediate follow-up, known limitations, dependencies created
- [ ] **References** — Grounding in ATLAS EN/BN, external literature citations

---

## Appendix B: Historical Context

**Why this protocol was needed**:

Early ATLAS development (2025) was exploratory. Agents built, tested, and iterated rapidly. Documentation was sparse. By late 2025/early 2026, the system grew complex: 155+ sections in the master doc, 26+ parts, 10+ services, 4,888 beliefs in the network.

**The crisis moment**:

In February 2026, David asked: "Why did we choose a 0.90 AESHI gate for Tier2 coverage?" Nobody could answer. The decision was made and implemented, but the rationale was lost. It took 3 hours of reading session logs to reconstruct the thinking.

**David's directive**:

"Somehow we have to have a better pipeline that forces everyone wherever they are to write up a context and decision justification doc that you can use/rewrite to add to the master."

**This protocol is the answer.**

It ensures that:
1. Every significant decision is documented with its rationale in real time (not reconstructed later)
2. CW has a mechanical process to integrate new work into the master doc
3. Future readers can understand the system's evolution without reading session logs
4. Panel reviews have all the context they need upfront

---

**Last updated**: 2026-03-04
**Version**: 1.0
**Status**: ACTIVE
