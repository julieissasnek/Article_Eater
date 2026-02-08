# PARALLEL_WORK.md

*Last updated: Saturday, February 8, 2026*

This file coordinates parallel Claude Code sessions to prevent conflicts.

---

## How This Works

1. **Before starting work**: Check this file, claim your lane
2. **Claim a lane**: Edit the "Active Claims" section with your session ID
3. **Respect file ownership**: Only edit files in your lane
4. **Release when done**: Clear your claim when finished

---

## Work Lanes

### Lane A: Sprint 2.5 Schema Design
**Scope**: Design social epistemology schema and data structures
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `src/services/social_epistemology.py` — NEW FILE
- `contracts/schemas/social_epistemology.schema.json` — NEW FILE
- `docs/SPRINT_2.5_DESIGN.md` — NEW FILE

**Files SHARED (read-only)**:
- `src/services/web_of_belief.py` — Reference existing Belief class

**Tasks**:
- 2.5.1 Design community schema
- 2.5.2 Design `EpistemicCommunity` class
- 2.5.3 Design `BeliefProvenance` class
- Answer Panel Questions SE-1 through SE-5

---

### Lane B: Sprint 2.5 Implementation
**Scope**: Implement social epistemology classes and integrate with WebOfBelief
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `src/services/social_epistemology.py` — Implementation (after Lane A designs)
- `tests/test_social_epistemology.py` — NEW FILE

**Files SHARED (coordinate changes)**:
- `src/services/web_of_belief.py` — Extend Belief class with provenance

**Tasks**:
- 2.5.4 Implement `CommunityRelativeCredence`
- 2.5.5 Implement `ContestationTracker`
- 2.5.6 Implement `MethodologicalDiversityAssessor`
- 2.5.7 Integrate with existing Belief class
- 2.5.8 Tests

**Dependencies**: Lane A must complete schema design first

---

### Lane C: Credibility Testing (TODO 1)
**Scope**: Enhance credibility testing module
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `src/services/credibility_testing.py`
- `tests/test_credibility_testing.py`
- `docs/implementation_plans/TODO1_*.md`

**Files SHARED (read-only)**:
- `src/services/web_of_belief.py`
- `src/services/extraction_to_web.py`

**Tasks**: See `docs/STRATEGIC_TODOS_2026_01_20.md` TODO 1

---

### Lane D: Interpretive Intelligence (TODO 2)
**Scope**: Enhance interpretive intelligence module
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `src/services/interpretive_intelligence.py`
- `tests/test_interpretive_intelligence.py`
- `docs/implementation_plans/TODO2_*.md`
- `contracts/vocab/vocabulary_bridge.yaml`

**Files SHARED (read-only)**:
- `src/services/web_of_belief.py`
- `src/services/bridge_warrants.py`

**Tasks**: See `docs/STRATEGIC_TODOS_2026_01_20.md` TODO 2

---

### Lane E: VOI-Driven Search (TODO 3)
**Scope**: Enhance VOI search module
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `src/services/voi_search.py`
- `tests/test_voi_search.py`
- `docs/implementation_plans/TODO3_*.md`
- `contracts/vocab/cross_field_vocabulary.yaml` — NEW FILE

**Files SHARED (read-only)**:
- `src/services/web_of_belief.py`
- `src/services/paper_fetcher.py`

**Tasks**: See `docs/STRATEGIC_TODOS_2026_01_20.md` TODO 3

---

### Lane F: Panel Convening (P-TC, P-QW)
**Scope**: Convene pending expert panels
**Owner**: UNCLAIMED
**Files OWNED (exclusive write access)**:
- `docs/PANEL_P-TC_*.md` — NEW FILES
- `docs/PANEL_P-QW_*.md` — NEW FILES

**Files SHARED (read-only)**:
- `TASKS.md` — Read decisions, update after panel
- All service files (for context)

**Tasks**:
- Convene P-TC panel (7 decisions)
- Convene P-QW panel (6 decisions)

---

## Active Claims

**IMPORTANT**: Edit this section to claim/release lanes.

| Lane | Session ID | Claimed At | Expected Duration | Notes |
|------|------------|------------|-------------------|-------|
| A | — | — | — | COMPLETED: Sprint 2.5 Schema Design (2026-02-08). P-SE panel consulted. |
| B | — | — | — | COMPLETED: Sprint 2.5 Implementation (2026-02-08). social_epistemology.py (~1300 lines), 54 tests. |
| C | — | — | — | COMPLETED: TODO 1 Credibility Testing (2026-02-08). Feedback module, semantic coherence, pipeline. |
| D | — | — | — | COMPLETED: TODO 2 Interpretive Intelligence (2026-02-08). Added MECHANISM + DISAGREEMENT patterns. |
| E | — | — | — | COMPLETED: TODO 3 VOI-Driven Search (2026-02-08). Cross-field vocabulary, 92 tests. |
| F | — | — | — | COMPLETED: P-TC and P-QW panels convened (2026-02-08) |

---

## Lane Coordination Protocol

### Shared File: `web_of_belief.py`

This is the core engine and CANNOT be exclusively owned. Coordination rules:

1. **Read access**: All lanes can read
2. **Write access**: Must coordinate via this file
3. **Pending changes queue**:

| Requester | Change Description | Affected Lines/Methods | Status |
|-----------|-------------------|------------------------|--------|
| Lane B | Add `provenance` field to Belief | Belief class | ✓ COMPLETE |
| Lane B | Add community-relative credence support | New methods | ✓ COMPLETE |
| Lane B | Add `community_associations` field | Belief class | ✓ COMPLETE |
| Lane B | Add social_epistemology optional import | Import section | ✓ COMPLETE |

**All Lane B changes complete** — web_of_belief.py now supports Sprint 2.5 social epistemology features.

### Existing Types (Already Implemented in Sprint 1.6)

These types already exist in `web_of_belief.py`:

```python
# Already implemented - DO NOT duplicate

class InferenceType(Enum):
    INDUCTIVE = "inductive"
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class BeliefKind(Enum):
    MECHANISTIC = "mechanistic"
    EVIDENTIAL = "evidential"
    THEORETICAL = "theoretical"
    METHODOLOGICAL = "methodological"
    BRIDGE = "bridge"
```

### Proposed New Types (Sprint 2.5)

If you need to add types/enums that other lanes might use, add them here first:

```python
# Proposed for Sprint 2.5 - Lane A to design, Lane B to implement

class CommunityType(Enum):
    JOURNAL_CLUSTER = "journal_cluster"
    CITATION_NETWORK = "citation_network"
    THEORY_COMMITMENT = "theory_commitment"
    METHODOLOGICAL = "methodological"

class ContestationType(Enum):
    EMPIRICAL = "empirical"        # Different data interpretations
    METHODOLOGICAL = "methodological"  # Different methods
    THEORETICAL = "theoretical"    # Different frameworks
    SCOPE = "scope"               # Different generalization claims
```

---

## Conflict Resolution

If two sessions need the same file:

1. **Check this file first** — see who has the claim
2. **Coordinate via TASKS.md** — leave a note in Session Log
3. **Serialize if necessary** — one finishes, then the other starts
4. **Create interface files** — if extending, add a new file that imports from shared

---

## Session Handoff Protocol

When finishing a lane:

1. **Mark tasks complete** in TASKS.md
2. **Clear your claim** in Active Claims table above
3. **Document any unfinished work** in TASKS.md Pending section
4. **Note any discoveries** that affect other lanes

---

## Quick Reference: File Ownership Matrix

| File | Lane A | Lane B | Lane C | Lane D | Lane E | Lane F |
|------|--------|--------|--------|--------|--------|--------|
| `social_epistemology.py` (new) | WRITE | WRITE* | — | — | — | — |
| `web_of_belief.py` | read | coord | read | read | read | read |
| `credibility_testing.py` | — | — | WRITE | read | — | — |
| `interpretive_intelligence.py` | — | — | read | WRITE | — | — |
| `voi_search.py` | — | — | — | — | WRITE | — |
| `TASKS.md` | update | update | update | update | update | WRITE |
| Panel docs | — | — | — | — | — | WRITE |

Legend: WRITE = exclusive, WRITE* = after Lane A completes, read = read-only, coord = coordinate changes, — = no access needed

---

## Recommended Parallel Combinations

These lane pairs work well together (minimal conflicts):

- **Lane A + Lane E** — Schema Design + VOI Search (independent)
- **Lane A + Lane C** — Schema Design + Credibility (independent)
- **Lane C + Lane F** — Credibility + Panels (independent)
- **Lane D + Lane E** — Interpretive + VOI (independent)
- **Lane C + Lane D** — Credibility + Interpretive (minimal overlap)

Avoid running simultaneously:
- **Lane A + Lane B** — Lane B depends on Lane A completing first
- **Lane B + Lane C/D/E** — Lane B modifies `web_of_belief.py`

---

*Created: February 8, 2026*
