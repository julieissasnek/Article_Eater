# Master Doc Briefs Directory

**Purpose**: Centralized repository for Master Doc Briefs (MDBs) — standardized context and decision documentation produced by every agent whenever they do significant work.

**Why This Exists**: The master document (155+ sections, 26+ parts) must stay current with system development. Without this directory, design decisions and technical context are buried in session logs. With it, CW can read one clear document and integrate it into the master doc with minimal translation.

---

## Quick Start

**For agents doing work:**
1. Read `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` (the protocol spec)
2. Determine if your work meets the "Significant Work" threshold (§2 of the protocol)
3. If YES, create an MDB using the template (§3 of the protocol)
4. Store it here with the naming convention: `MDB_{AGENT}_{DATE}_{TOPIC}.md`
5. Commit it to git along with your code changes

**For CW integrating work:**
1. Scan this directory weekly (every Monday AM)
2. Read each new MDB
3. Extract key content (design decisions, new concepts, architectural details)
4. Integrate into appropriate Part of `docs/master_doc_parts/`
5. Update the index (`_index.md` in this directory)

---

## Directory Contents

```
docs/master_doc_briefs/
├── README.md                                (this file)
├── _index.md                                (auto-generated index of all MDBs)
├── MDB_CW_2026-02-28_EXTRACTION-VALIDATOR.md
├── MDB_AG_2026-03-01_VISION-ATTRIBUTES-BATCH1.md
├── MDB_CC_2026-03-04_OVERSEER-FIXES.md
└── [more MDBs added as sessions complete significant work]
```

---

## Index (_index.md)

The `_index.md` file is a quick reference table of all MDBs in this directory:

| Date | Agent | Topic | Status | Master Doc Impact | Notes |
|---|---|---|---|---|---|
| 2026-02-28 | CW | Extraction Field Validator | FINAL | Part III.2, IV.1 | 50+ validation rules, 1,009 articles scored |
| 2026-03-01 | AG | Vision Attributes Batch 1 | FINAL | Part VI, VII | 12 new attributes across 3 files, 120 tests |
| 2026-03-04 | CC | Overseer Critical Fixes | FINAL | Part III.3 | 3 SQL bugs fixed, AESHI 65→70 |

CW regenerates this file weekly by scanning all MDB files in the directory and extracting metadata from their headers and "Master Doc Impact" sections.

---

## Naming Convention

Every MDB file follows this pattern:

```
MDB_{AGENT}_{DATE-ISO}_{TOPIC-SLUG}.md
```

**Format**:
- `{AGENT}` = CW | AG | CC | [future agents]
- `{DATE-ISO}` = YYYY-MM-DD (ISO 8601 format)
- `{TOPIC-SLUG}` = kebab-case topic name (no spaces, no special chars)

**Examples**:
- `MDB_CW_2026-02-28_EXTRACTION-VALIDATOR.md`
- `MDB_AG_2026-03-01_VISION-ATTRIBUTES-BATCH1.md`
- `MDB_CC_2026-03-04_OVERSEER-FIXES.md`
- `MDB_CW_2026-03-05_EXTRACTION-PIPELINE-PHASES-1A-1B.md`

**Why this naming**: Sorts chronologically and by agent, making it easy to scan recent work and see what each system did.

---

## MDB Template Overview

Every MDB has these sections (from `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` §3):

1. **Context & Motivation** — Problem statement, why it matters
2. **What Was Done** — Concrete deliverables, how it works, testing/validation
3. **Design Decisions** — For each significant choice: context, alternatives, rationale, risk, dependencies
4. **Epistemic Implications** — Impact on web of belief, AESHI, downstream systems, uncertainties
5. **New Concepts** — If any, fully defined
6. **Master Doc Impact** — Which Parts and sections should be updated
7. **Panel Review** — Whether expert panel feedback is needed, scope, turnaround
8. **Success Conditions** — SC-* defined or modified with test status
9. **Next Steps & Known Gaps** — Follow-up work, limitations, dependencies created
10. **References & Evidence** — Grounding in ATLAS and external literature

---

## Quality Standards

### ✅ Good MDB

- **Concrete** — Names files, reports metrics, cites decisions. No vague summaries.
- **Justified** — Each decision explains alternatives and rationale
- **Connected** — Shows how work integrates into ATLAS architecture
- **Epistemic clarity** — Explains impact on credence, coherence, AESHI, or other epistemically interesting properties
- **Usable** — CW can read once and integrate into master doc with minimal translation
- **Prompt** — Produced within 1 day of work completion

### ❌ Bad MDB

- Vague ("fixed stuff")
- Unjustified decisions ("we chose option A")
- Isolated from architecture
- Overly technical (assumes codebase knowledge)
- Incomplete sections
- Stale (written weeks later from memory)

See `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` §7 for detailed examples.

---

## Fast Track for Small Changes

Not all changes need a full MDB. **Change Notes** in COORDINATION.md are lightweight alternatives for:
- Bug fixes <50 lines
- Test additions without new infrastructure
- Documentation updates
- Minor refactors

Format: 2–3 sentence summary in COORDINATION.md Sprint Status table.

See `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` §8 for details.

---

## Integration Workflow (CW Perspective)

### Weekly (Every Monday AM)

1. **Read new MDBs** produced since last Monday
2. **Scan "Master Doc Impact" section** — know which Parts need updating
3. **Check "Panel Review" section** — flag high-risk work for David's attention
4. **Start integration** → extract content from MDB, rewrite for master doc prose style

### Per-MDB Integration (1–2 hours)

1. **Open relevant Part files** from `docs/master_doc_parts/`
2. **Extract key content** from MDB: "How It Works" section, design decisions, new concepts
3. **Rewrite** using `contracts/WRITING_STYLE_GUIDE.md` and `contracts/SCIENCE_COMMUNICATION_NORMS.md`
4. **Add references** — cite MDB and code artifacts
5. **Update word counts** in Part headers
6. **Mark dependencies** if new figures are needed (via `contracts/FIGURE_DEPENDENCIES.json`)

### Monthly (Before Release)

1. **Full audit** — verify all significant work has an MDB
2. **Update _index.md** with cumulative metadata
3. **Commit** master doc + _index.md changes
4. **Tag version** in git

---

## Key Responsibilities

### Agents (CW, AG, CC)
- Produce MDBs for significant work (see `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` §2)
- Follow template structure (§3)
- Include epistemic implications (§3 required section)
- Commit MDB to git along with code changes
- Provide Change Notes for small fixes instead of full MDBs

### CW (Cowork/Claude — Integration Steward)
- Read all new MDBs weekly
- Integrate into master doc Parts
- Maintain _index.md
- Flag panel review needs to David
- Ensure consistency across Parts (no contradictions from different MDBs)

### David Kirsh (System Owner)
- Monitor for MDB compliance
- Review panel-flagged decisions
- Approve major amendments to the protocol
- Use MDBs as evidence for what the system does/why

---

## Historical Context

In early 2026, agents built rapidly without documenting design decisions. When David asked "Why did we use a 0.90 AESHI gate?", the answer took 3 hours of session logs to reconstruct.

This protocol ensures decisions are documented in real time, with full rationale, so future readers (and future Davids) can understand the system without archaeological investigation.

---

## Questions & Feedback

If you have questions about the MDB format, protocol interpretation, or integration process:
- Check `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` first
- Ask in COORDINATION.md (post as a micro-task or handoff item)
- Suggest amendments (document proposal + implementation plan)

---

**Last updated**: 2026-03-04
**Version**: 1.0 (Initial release)
**Status**: ACTIVE
