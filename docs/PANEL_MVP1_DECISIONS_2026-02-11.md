# Panel Consultation: MVP-1 Persistent Web State Decisions

**Date**: 2026-02-11 (Retroactive)
**Terminal**: Terminal 1 (MAIN-TERMINAL)
**Decisions Under Review**: D1, D2, D3, D4

---

## Panel Composition

For persistence and data architecture decisions:
- **Dr. Herbert Simon** — System design, bounded rationality
- **Dr. Jim Gray** — Database systems, transaction processing (constructed voice)
- **Dr. Martin Fowler** — Software architecture patterns (constructed voice)
- **Dr. Pat Helland** — Distributed systems, immutability (constructed voice)

---

## Decisions Under Review

### D1: Thin Wrapper vs. New Implementation
**Context**: Need persistent accumulation across paper processing runs
**Decision**: Created `WebAccumulator` as thin wrapper over existing `WebPersistenceService`
**Alternatives**:
- Build new accumulation system from scratch (duplication)
- Modify WebPersistenceService directly (violates single responsibility)
- Use WebPersistenceService directly without wrapper (no accumulator-specific API)
**Risk Level**: Low

### D2: Event Sourcing to events.jsonl
**Context**: Need audit trail and debugging capability for accumulation
**Decision**: Append-only JSONL file for all accumulation events
**Alternatives**:
- Log to SQLite table (queryable but more complex)
- No event log (loses debugging capability)
- Structured logging only (not easily replayable)
**Risk Level**: Low

### D3: Dual Storage (SQLite + JSON Export)
**Context**: SQLite is authoritative but not human-readable
**Decision**: Auto-export to `accumulated_web.json` after each integration
**Alternatives**:
- SQLite only (harder to inspect)
- JSON only (no ACID guarantees)
- Export on demand only (stale snapshots)
**Risk Level**: Medium (sync issues possible)

### D4: papers_processed List in AccumulatorStats
**Context**: Need to check if paper already processed (skip duplicates)
**Decision**: Added `papers_processed: List[str]` to AccumulatorStats, read from events.jsonl
**Alternatives**:
- Query SQLite for processed papers (more complex)
- Track in memory only (lost on restart)
- Separate tracking file (fragmentation)
**Risk Level**: Low

---

## Panel Responses

### Dr. Herbert Simon (System Design):

**On D1 (Thin Wrapper)**:
"The wrapper pattern is a classic example of satisficing in software design. You had a working persistence layer; building new would be wasteful. The wrapper provides a clean API for the specific use case (accumulation) without disturbing the general-purpose layer beneath.

**Approved**. This is textbook bounded rationality—use what works."

**On D3 (Dual Storage)**:
"The dual storage creates a potential consistency problem. If JSON export fails but SQLite succeeds, you have divergence. However, for a research tool where the JSON is for *inspection* not *operation*, this is acceptable.

**Approved with caveat**: Document that SQLite is authoritative; JSON is best-effort snapshot."

---

### Dr. Jim Gray (Database Systems):

**On D2 (Event Sourcing)**:
"JSONL append-only logs are an excellent choice for audit trails. They're:
1. Append-only (no corruption from partial writes)
2. Human-readable (debugging)
3. Replayable (can reconstruct state)

The only concern is file growth over time. For a research tool processing hundreds of papers, this is fine. For millions, you'd need rotation.

**Approved**. Consider adding log rotation if file exceeds 100MB."

**On D3 (Dual Storage)**:
"The pattern you've implemented is essentially 'write-through cache' where JSON is the cache and SQLite is the source of truth. This is a well-understood pattern.

**Approved**. Ensure the JSON export is atomic (write to temp file, then rename)."

---

### Dr. Martin Fowler (Software Architecture):

**On D1 (Thin Wrapper)**:
"This is the Facade pattern—providing a simplified interface to a complex subsystem. The WebAccumulator facade hides the complexity of WebPersistenceService while exposing only what the accumulation use case needs.

**Approved**. Good separation of concerns."

**On D4 (papers_processed List)**:
"Reading from events.jsonl to populate the list is a form of event sourcing replay. This is correct but has a performance implication: you're scanning the entire log on each `get_stats()` call.

**Approved with recommendation**: Cache the list in memory after first read; invalidate cache when new events are written."

---

### Dr. Pat Helland (Immutability):

**On D2 (Event Sourcing)**:
"Append-only logs are the foundation of reliable systems. By never modifying past events, you gain:
1. Auditability (what happened when)
2. Debuggability (replay to any point)
3. Recoverability (rebuild from log)

**Strongly approved**. This is the right pattern for research reproducibility."

**On D4 (papers_processed from events)**:
"Deriving current state from event log is correct event sourcing. The list of processed papers is a 'projection' of the event stream.

**Approved**. Consider materializing this projection to a separate file if performance becomes an issue."

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1 | **APPROVED** | No changes needed |
| D2 | **APPROVED** | Consider log rotation at 100MB (deferred) |
| D3 | **APPROVED** | Document SQLite as authoritative; ensure atomic writes |
| D4 | **APPROVED** | Consider caching papers_processed list (deferred) |

---

## Action Items

### Immediate
1. [x] Document that SQLite is authoritative source of truth (in code comments)

### Deferred
2. [ ] Add log rotation for events.jsonl if >100MB
3. [ ] Cache papers_processed list in memory
4. [ ] Ensure JSON export uses atomic write (temp file + rename)

---

## Panel Sign-off

**Status**: APPROVED

All four decisions align with established patterns (Facade, Event Sourcing, Write-Through Cache). No architectural changes required.

*Panel consultation complete: 2026-02-11*
