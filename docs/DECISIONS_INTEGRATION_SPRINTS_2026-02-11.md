# Integration Sprint Decisions Log

**Date Started**: 2026-02-11
**Sprints**: INT-1 through INT-6
**Status**: ACTIVE — Decisions accumulate here for panel review

---

## Decision Tracking Protocol

All implementation decisions during integration sprints are logged here for panel review.

**Decision Format**:
```
### D[sprint]-[number]: [Title]
**Context**: Why this decision arose
**Decision**: What was decided
**Alternatives**: Other options considered
**Risk Level**: Low/Medium/High
**Status**: PENDING_REVIEW | PANEL_APPROVED | REVISED
```

---

## Sprint INT-1: Edge Justification Foundation

### D1-1: Variable Name Matching Strategy
**Context**: BN variables (e.g., `daylight`) must match belief content (e.g., "natural light")
**Decision**: Taxonomy-based matching via environment_taxonomy.py + vocabulary_bridge.py. These existing services already handle synonym resolution.
**Alternatives**:
- Exact string match (brittle) — REJECTED
- Taxonomy-based matching via environment_taxonomy.py — SELECTED
- Fuzzy matching with threshold — Could supplement taxonomy
- Manual mapping table — Fallback for edge cases
**Risk Level**: Medium
**Status**: PENDING_REVIEW

### D1-2: Credence Aggregation Method
**Context**: Multiple beliefs support same edge; how to combine credences?
**Decision**: Inverse-variance weighted average (DerSimonian-Laird style). Weight = 1/variance, where variance = uncertainty². This gives more weight to beliefs with lower uncertainty.
**Alternatives**:
- Simple average — REJECTED (ignores uncertainty)
- Inverse-variance weighted average (DerSimonian-Laird) — SELECTED
- Maximum credence — Too optimistic
- Minimum credence (conservative) — Too pessimistic
**Risk Level**: Medium
**Status**: PENDING_REVIEW

### D1-3: Conflict Detection Threshold
**Context**: When do beliefs "conflict" vs. "slightly disagree"?
**Decision**: Constraint weight < -0.3 triggers conflict classification. This threshold avoids flagging minor tensions while catching genuine conflicts.
**Alternatives**:
- Any negative constraint = conflict — Too sensitive
- Constraint weight < -0.3 = conflict — SELECTED
- Opposite polarity claims = conflict — Requires parsing
- Manual review required — Not scalable
**Risk Level**: Low
**Status**: PENDING_REVIEW

---

## Sprint INT-2: Gap Prediction Engine

### D2-1: VOI Calculation Formula
**Context**: How to compute Value of Information for gap prioritization?
**Decision**: Simple heuristic (coverage × uncertainty). For mechanism gaps: 0.5 + 0.1 × n_empirical_beliefs. For boundary gaps: 0.4 + 0.4 × (1 - coverage_ratio). Full Bayesian VOI deferred to future sprint.
**Alternatives**:
- Entropy reduction — Too complex for MVP
- Decision impact (downstream beliefs affected) — Requires full graph analysis
- Simple heuristic (coverage × uncertainty) — SELECTED
- Full Bayesian VOI — Deferred
**Risk Level**: Medium
**Status**: PENDING_REVIEW

### D2-2: Path Length for Mediation Gaps
**Context**: How long a path A→...→Y triggers a mediation gap check?
**Decision**: 2-hop only (A→X→Y). Longer paths would create combinatorial explosion and less actionable gaps.
**Alternatives**:
- 2-hop only (A→X→Y) — SELECTED
- Up to 3-hop — Too many false positives
- Any path length — Computationally expensive
**Risk Level**: Low
**Status**: PENDING_REVIEW

### D2-3: Scope Condition Comparison
**Context**: How to detect "narrow" scope conditions for boundary gaps?
**Decision**: Compare against hardcoded KNOWN_SETTINGS and KNOWN_POPULATIONS sets. Simple but effective for MVP. Sets include: office, healthcare, educational, residential, retail, industrial, hospitality, outdoor, transportation; adults, children, elderly, workers, patients, students.
**Alternatives**:
- Compare against known universe of settings/populations — SELECTED
- Compare against beliefs in same domain — More dynamic but complex
- Hardcoded list of expected coverage — Same as selected
**Risk Level**: Low
**Status**: PENDING_REVIEW

---

## Sprint INT-3: BN Frontend — Evidence Panel

### D3-1: Edge Opacity Mapping
**Context**: How to map credence (0-1) to visual opacity?
**Decision**: [PENDING]
**Alternatives**:
- Linear: opacity = credence
- Threshold: <0.5 = 30%, >=0.5 = 100%
- Logarithmic scale
- Three-tier: low/medium/high
**Risk Level**: Low

### D3-2: Evidence Panel Trigger
**Context**: How does user open evidence panel?
**Decision**: [PENDING]
**Alternatives**:
- Click on edge
- Hover for 500ms
- Right-click context menu
- Dedicated "inspect" mode
**Risk Level**: Low

### D3-3: Belief Display Limit
**Context**: How many beliefs to show in evidence panel before "show more"?
**Decision**: [PENDING]
**Alternatives**:
- Top 3 by credence
- Top 5 by credence
- All with scrolling
- Grouped by theory
**Risk Level**: Low

---

## Sprint INT-4: Epistemic Web Component

### D4-1: Layout Algorithm
**Context**: How to position nodes in the web visualization?
**Decision**: [PENDING]
**Alternatives**:
- Force-directed (organic, can be messy)
- Hierarchical by epistemic level
- Clustered by theory
- Manual positioning
**Risk Level**: Medium

### D4-2: Clustering Strategy
**Context**: Per Tufte, should cluster by theory. How?
**Decision**: [PENDING]
**Alternatives**:
- Visual grouping (colored backgrounds)
- Physical clustering (nodes closer together)
- Collapsible groups
- Tabs for different theories
**Risk Level**: Low

### D4-3: Node Size Encoding
**Context**: What should node size represent?
**Decision**: [PENDING]
**Alternatives**:
- Credence (higher = larger)
- Entrenchment (more connected = larger)
- Fixed size
- Number of supporting papers
**Risk Level**: Low

---

## Sprint INT-5: Cross-Layer Query API

### D5-1: API Response Format
**Context**: Should responses be flat JSON or nested?
**Decision**: [PENDING]
**Alternatives**:
- Flat with references (IDs)
- Fully nested (embedded objects)
- Hybrid (summary embedded, details by reference)
**Risk Level**: Low

### D5-2: Pagination Strategy
**Context**: Large result sets need pagination
**Decision**: [PENDING]
**Alternatives**:
- Offset-based (page=2, limit=10)
- Cursor-based (after=belief_id)
- No pagination (limit results)
**Risk Level**: Low

---

## Sprint INT-6: User Modes

### D6-1: Default Mode
**Context**: Which mode should users see first?
**Decision**: [PENDING]
**Alternatives**:
- Knowledge Mode (per Simon: satisficing)
- Prediction Mode (actionable)
- Last-used mode (cookie/localStorage)
**Risk Level**: Low

### D6-2: Mode Switching Persistence
**Context**: Should mode choice persist across sessions?
**Decision**: [PENDING]
**Alternatives**:
- localStorage
- URL parameter
- User account setting
- Always reset to default
**Risk Level**: Low

---

## Panel Review Schedule

Decisions will be reviewed by panel:
- After INT-1 completes: D1-* decisions
- After INT-2 completes: D2-* decisions
- After INT-3,4 complete: D3-*, D4-* decisions
- After INT-5,6 complete: D5-*, D6-* decisions

Or panel can review all at end if preferred.

---

## Revision Log

| Decision | Original | Revised To | Reason | Date |
|----------|----------|------------|--------|------|
| (none yet) | | | | |

---

*Log started: 2026-02-11*
*Actively updated during implementation*
