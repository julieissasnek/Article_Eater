# Tier 1 Phase A Implementation Decisions
## For Expert Panel Review
**Date**: January 20, 2026
**Status**: Phase A Complete — Requesting Panel Feedback

---

## IMPLEMENTATION SUMMARY

Phase A (Backend Infrastructure) is complete. Four sprints delivered:

| Sprint | Component | Tests | Status |
|--------|-----------|-------|--------|
| A1 | Core Data Model Extensions | 27 | COMPLETE |
| A2 | Graph API Endpoints | 33 | COMPLETE |
| A3 | Ingestion API Clients | 38 | COMPLETE |
| A4 | Stability Engine | 26 | COMPLETE |

**Total**: 124 new tests, all passing.

---

## FILES CREATED

| File | Purpose | LOC |
|------|---------|-----|
| `src/services/graph_api.py` | Graph export for Evidence Explorer | ~500 |
| `src/services/paper_fetcher.py` | Unified paper ingestion | ~450 |
| `src/services/stability_engine.py` | Stability tracking & reporting | ~400 |
| `tests/test_tier1_data_model.py` | Data model tests | ~350 |
| `tests/test_graph_api.py` | Graph API tests | ~350 |
| `tests/test_paper_fetcher.py` | Paper fetcher tests | ~300 |
| `tests/test_stability_engine.py` | Stability engine tests | ~350 |

---

## DECISIONS IMPLEMENTED

### D1: SourceDepth Enum (Cartwright)

Added `SourceDepth` enum to track extraction depth:
- `FULL_TEXT` — Complete paper analyzed
- `ABSTRACT` — Only abstract available
- `METADATA` — Only title/keywords

**Rationale**: Causal claims from abstracts should have lower confidence.

**Panel Question**: Should we adjust default credence based on source depth automatically?

### D2: EnablingConditions Dataclass (Cartwright)

Added `EnablingConditions` separate from `ScopeConditions`:
```python
@dataclass
class EnablingConditions:
    minimum_exposure: Optional[str]  # ">30 minutes"
    baseline_state: Optional[str]    # "non-depressed"
    concurrent_factors: List[str]    # Must be present
    blocking_factors: List[str]      # Must be absent
    threshold: Optional[str]         # ">300 lux"
    dosage: Optional[str]            # "daily"
```

**Rationale**: Enabling conditions explain why findings fail to replicate (mechanism blocked vs. absent).

**Panel Question**: Is this structure sufficient for capacity claims?

### D3: Credence History Tracking (Simon)

Added `CredenceHistoryEntry` and history tracking to beliefs:
- Timestamps each credence change
- Records delta from previous value
- Tracks triggering paper ID
- Enables stability calculation

**Rationale**: Stability-based stopping rules need history.

**Implementation Detail**: History appended on each `record_credence_change()` call.

### D4: Oscillation Detection (Epistemologist)

Added automatic contested belief detection:
- Detects when credence crosses a threshold (0.5) multiple times
- Sets `contested=True` flag
- Reports credence range instead of point estimate

**Rationale**: Oscillation indicates genuine disagreement, not noise.

**Panel Question**: Is threshold of 0.5 appropriate? Should it be configurable?

### D5: Graph Export Format (Pearl, UX Expert)

Graph export includes:
- Nodes with: credence, status, outcome_category, contested flag, source_depth
- Edges with: type, strength, causal_direction, is_correlational flag
- Metadata: total counts, coherence score

**Key Decision**: CORRELATIONAL edges flagged separately for visualization (no arrowhead, reduced opacity).

### D6: Node Detail Progressive Disclosure (Simon)

NodeDetail includes both full and simplified views:
- Full: All metadata, constraints, scope, enabling conditions
- Simplified: Traffic-light confidence, source count, disagreement flag

**Rationale**: Novice users need simple view; experts need full access.

### D7: Identifier Auto-Detection (Systems Architect)

PaperFetcher auto-detects identifier type:
- DOI: `10.xxxx/...` or `https://doi.org/...`
- PMID: 6-9 digit number or `PMID:xxxxx`
- arXiv: `YYMM.NNNNN` or `arxiv:category/NNNNNNN`
- Semantic Scholar: 40-char hex string

**Rationale**: Users should paste any identifier without specifying type.

### D8: Duplicate Detection (Systems Architect)

Checks existing papers before fetching:
- Match on DOI, PMID, arXiv ID, or S2 ID
- Returns `FetchStatus.DUPLICATE` with existing paper ID

**Panel Question**: Should fuzzy matching on title/author be added?

### D9: Citation Suggestions (Bates)

PaperFetcher provides citation-based suggestions:
- `citing_in_web`: Papers in web that cite this one
- `cites_in_web`: Papers in web cited by this one
- `citing_suggestions`: Papers NOT in web that cite this one
- `cites_suggestions`: Papers NOT in web cited by this one

**Rationale**: Build complete evidence networks.

### D10: Publication Bias Estimation (Cartwright)

StabilityEngine estimates publication bias:
- Counts null result indicators in belief content
- Calculates null result ratio
- Risk levels: LOW (>15% null), MODERATE (5-15%), HIGH (<5%)
- Includes warning message when bias detected

**Panel Question**: Should we add funnel plot asymmetry analysis?

### D11: Stability-Based Stopping (Simon)

StabilityEngine provides stopping recommendation:
- Stable: All beliefs within threshold for N papers
- Converging: Trending toward stability
- Contested: Genuine disagreement (may stop even if not converging)
- Unstable: Continue searching

**Key Framing**: "Given current evidence" — not absolute certainty.

### D12: Gap Integration (Simon)

Stability report includes VOI gaps:
- High-uncertainty beliefs flagged as gaps
- Contested beliefs flagged as gaps
- High-VOI gaps highlighted for action

---

## DECISIONS NEEDING PANEL INPUT

### Q1: Abstract-Only Credence Adjustment

Should beliefs extracted from abstracts automatically receive lower default credence?

**Options**:
- A. Yes, multiply by 0.8 (e.g., 0.7 → 0.56)
- B. Yes, cap at 0.5 maximum
- C. No, just display warning badge
- D. Configurable per user

**Current Implementation**: Option C (warning badge only)

### Q2: Oscillation Threshold

Is 0.5 the right threshold for detecting oscillation?

**Options**:
- A. Fixed at 0.5
- B. Adaptive based on belief's credence mean
- C. User-configurable

**Current Implementation**: Option A (fixed at 0.5)

### Q3: Duplicate Matching

Should we add fuzzy matching for duplicates?

**Options**:
- A. Exact identifier match only (current)
- B. Add title + year fuzzy match (Levenshtein < 3)
- C. Add semantic similarity matching

**Current Implementation**: Option A

### Q4: Publication Bias Depth

Should we implement funnel plot asymmetry analysis?

**Options**:
- A. Simple null ratio (current)
- B. Add funnel plot when >10 studies
- C. Add Egger's test statistic
- D. Both B and C

**Current Implementation**: Option A

### Q5: API Key Strategy

For real API clients (CrossRef, PubMed, Semantic Scholar):

**Options**:
- A. Shared institutional key with rate limiting
- B. Require user keys from start
- C. Start shared, migrate to user keys at scale

**Current Implementation**: Mock clients (no real API calls yet)

---

## NEXT PHASES

| Phase | Focus | Depends On |
|-------|-------|------------|
| B | Evidence Explorer GUI (React + Cytoscape.js) | A complete |
| C | Query & Ingestion UI | A, B |
| D | Stopping & Reporting UI | A, B |

---

## PANEL ACTION REQUESTED

Please review:
1. The implementation decisions (D1-D12)
2. Answer questions Q1-Q5
3. Identify any concerns before Phase B begins

**Next step**: Once panel approves, proceed to Phase B (Evidence Explorer GUI).
