# Expert Panel Review Request: Sprint 5 - Persistence & Accumulation

**Date**: 2026-01-18
**Sprint**: 5 (Persistence & Accumulation)
**Status**: Implementation Complete, Awaiting Expert Review
**Author**: Claude Code Implementation

---

## Executive Summary

Sprint 5 implements persistent storage and cross-paper accumulation for the Quinean Web of Belief. The implementation provides:

1. **SQLite Persistence**: Normalized relational storage for beliefs, constraints, and bridges
2. **Master Web Accumulation**: Integration of multiple paper extractions into a unified web
3. **Belief Merging Strategy**: New/update/conflict resolution when beliefs collide
4. **Version Tracking**: Full audit trail for belief evolution
5. **Coherence History**: Tracking web coherence as evidence accumulates

**All 31 tests pass.**

---

## Background for Expert Panel

### Current System Context

Article Eater extracts evidence-backed rules from scientific articles. Sprints 1-4 established:

- **Sprint 1**: Quinean Web of Belief architecture (coherentist epistemology)
- **Sprint 2**: Extraction-to-web pipeline (converting article extractions to beliefs)
- **Sprint 3**: Bridge warrants (cross-domain evidence transfer)
- **Sprint 4**: Extended outcome taxonomy (theory-outcome mappings)

**Sprint 5 Problem**: Each paper extraction creates an isolated web. We need to:
1. Persist web state across sessions
2. Accumulate beliefs from multiple papers into a master web
3. Handle conflicts when different papers make different claims
4. Track how the web evolves over time

### Key Files

| File | Purpose |
|------|---------|
| `src/services/web_persistence.py` | SQLite persistence and accumulation service |
| `tests/test_web_persistence.py` | 31 comprehensive tests |

---

## Decisions Requiring Expert Review

### Decision 5.1: Normalized Relational Storage (vs. Document/Blob)

**Implementation**: Separate tables for beliefs, constraints, bridges.

```sql
-- Beliefs table (normalized)
CREATE TABLE beliefs (
    belief_id TEXT PRIMARY KEY,
    web_id TEXT NOT NULL,
    content TEXT NOT NULL,
    level TEXT NOT NULL,
    status TEXT NOT NULL,
    credence_value REAL NOT NULL,
    credence_uncertainty REAL,
    ...
);

-- Constraints table
CREATE TABLE constraints (
    constraint_id TEXT PRIMARY KEY,
    web_id TEXT NOT NULL,
    source_id TEXT REFERENCES beliefs(belief_id),
    target_id TEXT REFERENCES beliefs(belief_id),
    constraint_type TEXT NOT NULL,
    strength REAL,
    ...
);
```

**Alternative Considered**: Store entire web as JSON blob.

**Rationale for Normalized**:
- Enables SQL queries across beliefs (e.g., "all beliefs from theory X")
- Supports incremental updates without rewriting entire web
- Foreign keys ensure referential integrity
- Better for concurrent access (future multi-user)

**Questions for Expert Panel**:
1. Is relational normalization appropriate for a coherentist structure?
2. Should constraint strengths be stored or computed dynamically?
3. What indexing strategy optimizes coherence calculations?

---

### Decision 5.2: Conservative Merge Strategy

**Implementation**: Three-way merge for beliefs with same ID.

```python
def merge_belief_into_master(self, master_web_id, belief, source_paper_id):
    existing = self.load_belief(belief.belief_id, master_web_id)

    if existing is None:
        # NEW: Add belief directly
        return MergeResult(merge_type="new")

    if self._beliefs_same_content(existing, belief):
        # UPDATE: Merge credences (weighted by observations)
        merged_credence = self._merge_credences(existing.credence, belief.credence)
        return MergeResult(merge_type="update", new_credence=merged_credence)

    else:
        # CONFLICT: Keep both, flag for review
        conflict_id = f"{belief.belief_id}:conflict:{source_paper_id}"
        return MergeResult(merge_type="conflict")
```

**Content Similarity**: Uses SequenceMatcher with 0.9 threshold.

**Questions for Expert Panel**:
1. Is content similarity (string matching) the right criterion for "same belief"?
2. Should conflicts be auto-resolved using credence, or always flagged?
3. How should contradicting beliefs (same ID, opposite claims) be handled?

---

### Decision 5.3: Credence Merge Formula

**Implementation**: Weighted average by observation count.

```python
def _merge_credences(self, c1: Credence, c2: Credence) -> Credence:
    n1 = max(1, c1.n_observations)
    n2 = max(1, c2.n_observations)

    total = n1 + n2
    merged_value = (c1.value * n1 + c2.value * n2) / total

    # Uncertainty decreases with more observations
    merged_uncertainty = c1.uncertainty / math.sqrt(total)

    return Credence(value=merged_value, uncertainty=merged_uncertainty, ...)
```

**Rationale**:
- More observations = more weight (replication valued)
- Uncertainty decreases as 1/sqrt(n) (following frequentist intuition)
- Preserves evidence counts for transparency

**Questions for Expert Panel**:
1. Is weighted averaging appropriate for combining credences?
2. Should we use Bayesian pooling of beta distributions instead?
3. How should conflicting evidence (high n_contradicting) affect merge?
4. Is the 1/sqrt(n) uncertainty reduction formula justified?

---

### Decision 5.4: Master Web vs. Per-Paper Webs

**Implementation**: Maintain both master (accumulated) and per-paper webs.

```python
# Each paper creates its own web
paper_web = extraction_to_web(paper_extraction)
service.save_web(paper_web, f"paper:{paper_id}")

# Papers integrate into master
report = service.integrate_paper_web(paper_web, paper_id)
# Master is at "master:web:accumulated"
```

**Rationale**:
- Per-paper webs preserve provenance (which paper said what)
- Master web enables cross-paper queries
- Allows re-extraction without losing history
- Supports "undo" by removing a paper's contributions

**Questions for Expert Panel**:
1. Should per-paper webs share constraints with master, or be independent?
2. How should paper retraction affect the master web?
3. Should papers have quality weights affecting merge?

---

### Decision 5.5: Coherence History Logging

**Implementation**: Record coherence score after each significant change.

```python
CREATE TABLE coherence_history (
    history_id INTEGER PRIMARY KEY,
    web_id TEXT NOT NULL,
    coherence_score REAL NOT NULL,
    n_beliefs INTEGER NOT NULL,
    n_constraints INTEGER NOT NULL,
    recorded_at TEXT NOT NULL,
    triggered_by TEXT  -- "save", "merge", "equilibrium", paper_id
);
```

**Usage**: Track how coherence evolves as evidence accumulates.

**Questions for Expert Panel**:
1. Is coherence the right metric for tracking web health?
2. Should we log local coherence (per-theory) or just global?
3. What coherence decline should trigger alerts?

---

## Implementation Details

### Database Schema Summary

| Table | Purpose |
|-------|---------|
| `web_metadata` | Web identity, version, statistics |
| `beliefs` | All beliefs with full credence data |
| `constraints` | Inter-belief constraints |
| `bridges` | Bridge warrants (Sprint 3) |
| `paper_integrations` | Integration history per paper |
| `coherence_history` | Coherence evolution log |
| `belief_merge_log` | Detailed merge decisions |

### Key Functions

| Function | Purpose |
|----------|---------|
| `save_web(web, web_id)` | Persist complete web state |
| `load_web(web_id)` | Reconstruct web from database |
| `integrate_paper_web(paper_web, paper_id)` | Merge paper into master |
| `merge_belief_into_master(master_id, belief, paper_id)` | Single belief merge |
| `get_integration_history(web_id)` | Paper integration log |
| `get_coherence_history(web_id)` | Coherence evolution |
| `get_statistics(web_id)` | Summary metrics |

### IntegrationReport Structure

```python
@dataclass
class IntegrationReport:
    paper_id: str
    n_beliefs_added: int = 0
    n_beliefs_updated: int = 0
    n_beliefs_conflicted: int = 0
    n_constraints_added: int = 0
    n_bridges_added: int = 0
    coherence_before: Optional[float] = None
    coherence_after: Optional[float] = None
    merge_results: List[MergeResult] = []
```

---

## Test Coverage

All 31 tests pass:

- **Basic Persistence**: 4 tests (service creation, schema, save/load)
- **Belief Operations**: 4 tests (CRUD, tags, updates)
- **Constraint Operations**: 2 tests (save, bidirectional)
- **Bridge Operations**: 2 tests (save/load, evidence tracking)
- **Master Web Accumulation**: 3 tests (creation, integration, multi-paper)
- **Belief Merging**: 4 tests (new, update, conflict, formula)
- **History Tracking**: 3 tests (coherence, merge log, integration)
- **Statistics**: 2 tests (summary, conflict count)
- **Integration Report**: 2 tests (fields, merge results)
- **Edge Cases**: 4 tests (nonexistent, empty, similarity)
- **Round Trip**: 1 test (full serialization)

---

## Integration Points

### With Sprint 2 (extraction_to_web.py)

```python
from src.services.web_persistence import WebPersistenceService

service = WebPersistenceService("ae_beliefs.db")

# After extraction
paper_web = extraction_to_web(paper_extraction)
report = service.integrate_paper_web(paper_web, paper_id)

print(f"Added {report.n_beliefs_added} beliefs, coherence: {report.coherence_after:.3f}")
```

### With Sprint 3 (bridge_warrants.py)

```python
# Bridges are persisted with the web
service.save_web(web, web_id, bridge_registry=bridge_registry)

# And loaded back
web, bridge_registry = service.load_web(web_id)
```

---

## Requested Expert Panel Composition

For Sprint 5, we request input from:

1. **Dr. Judea Pearl** — Credence aggregation, causal inference across papers
2. **Dr. Nancy Cartwright** — Evidence accumulation, replication weighting
3. **Dr. Larry Wasserman** — Statistical pooling of uncertain quantities
4. **Dr. Peter Norvig** — Database design for knowledge representation
5. **Dr. Herbert Simon** — Bounded rationality in merge decisions

---

## Questions Summary

1. Is normalized relational storage appropriate for coherentist webs?
2. Is content similarity the right criterion for belief identity?
3. Should credence conflicts be auto-resolved or flagged for review?
4. Is weighted averaging appropriate for credence pooling?
5. Should the 1/sqrt(n) uncertainty reduction formula be used?
6. How should paper retraction affect the accumulated web?
7. Is global coherence the right metric for web health?

---

## Philosophical Considerations

### The Problem of Accumulation

In coherentist epistemology, beliefs are justified by their coherence with other beliefs. When we accumulate evidence across papers, we face a fundamental question:

**Is the accumulated web more reliable than any single paper's web?**

Arguments for YES:
- More observations reduce uncertainty
- Replication is epistemically valuable
- Conflicting evidence gets identified and flagged

Arguments for CAUTION:
- Systematic biases may accumulate
- Publication bias affects what gets merged
- Different papers may use different operationalizations

### Connection to Quinean "Web"

Quine's original metaphor suggests that our total field of beliefs faces experience as a "corporate body." Sprint 5 literalizes this metaphor:

- Each paper contributes to the corporate body
- The master web is the "corporate" belief state
- Coherence is the criterion of acceptance
- Even well-supported beliefs can be revised if new evidence conflicts

---

**End of Sprint 5 Expert Panel Request**
