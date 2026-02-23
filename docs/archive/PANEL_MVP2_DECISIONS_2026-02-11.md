# Panel Consultation: MVP-2 Batch Processing Decisions

**Date**: 2026-02-11 (Retroactive)
**Terminal**: Terminal 1 (MAIN-TERMINAL)
**Decisions Under Review**: D1, D2, D3, D4

---

## Panel Composition

For batch processing and resilience decisions:
- **Dr. Herbert Simon** — Bounded rationality, satisficing
- **Dr. Michael Nygard** — Release It!, stability patterns (constructed voice)
- **Dr. Martin Kleppmann** — Designing Data-Intensive Applications (constructed voice)
- **Dr. Michael T. Fisher** — Distributed systems (constructed voice)

---

## Decisions Under Review

### D1: Circuit Breaker Threshold (3 Consecutive Failures)
**Context**: Batch processing should not continue indefinitely if something is broken
**Decision**: Stop after 3 consecutive failures, configurable via `max_consecutive_failures`
**Alternatives**:
- No circuit breaker (runaway failures)
- Fixed percentage threshold (e.g., stop if >50% fail)
- Exponential backoff without stopping
**Risk Level**: Medium

### D2: YAML Config Optional (Graceful Fallback)
**Context**: Users may not have PyYAML installed or may prefer CLI args
**Decision**: YAML config is optional; CLI args override config; works without YAML
**Alternatives**:
- Require YAML config (dependency burden)
- JSON config only (less readable)
- CLI args only (verbose for complex configs)
**Risk Level**: Low

### D3: Progress Tracking to JSON File
**Context**: Long batch runs need progress visibility and crash recovery
**Decision**: Write progress to `batch_progress.json` every 10 papers
**Alternatives**:
- No progress file (lost on crash)
- Progress in SQLite (overkill)
- Real-time progress to stdout only (not persistent)
**Risk Level**: Low

### D4: Skip-Already-Processed as Default
**Context**: Re-running batch should not duplicate work
**Decision**: Default `skip_already_processed=True`, check via AccumulatorStats.papers_processed
**Alternatives**:
- Always reprocess (wasteful)
- Default to reprocess, opt-in skip (surprising behavior)
- Separate "resume" command (more complex)
**Risk Level**: Low

---

## Panel Responses

### Dr. Herbert Simon (Bounded Rationality):

**On D1 (Circuit Breaker at 3)**:
"Three is a reasonable satisficing threshold. It's:
- Not so low that transient errors stop processing (1 would be too aggressive)
- Not so high that you waste resources on systematic failures (10 would be too tolerant)

The key insight is that consecutive failures indicate a *systematic* problem, not random noise.

**Approved**. Three is the right order of magnitude."

**On D4 (Skip-Already-Processed)**:
"This is correct default behavior. Users expect idempotent operations—running the same batch twice should produce the same result, not double the data.

**Approved**. The `--no-skip-processed` flag provides escape hatch for intentional reprocessing."

---

### Dr. Michael Nygard (Release It!):

**On D1 (Circuit Breaker)**:
"The circuit breaker pattern is essential for batch systems. Your implementation is a 'consecutive failure' breaker, which is simpler than time-window breakers but effective.

**Recommendations**:
1. Log clearly when circuit breaker trips (you do this ✓)
2. Consider adding a 'half-open' state for retry after cooldown
3. The threshold should be configurable (you have this ✓)

**Approved**. For MVP, the simple consecutive-failure model is sufficient."

**On D3 (Progress File)**:
"Progress checkpointing is critical for long-running batches. Writing every 10 papers is a good tradeoff between I/O overhead and data loss risk.

**Approved**. Consider adding a 'resume from progress file' feature in future."

---

### Dr. Martin Kleppmann (Data-Intensive Applications):

**On D2 (Optional YAML)**:
"Making configuration optional respects the principle of least surprise. Users can start simple (CLI args) and graduate to config files as complexity grows.

The graceful degradation when PyYAML is missing is correct—a missing optional dependency should not crash the system.

**Approved**."

**On D4 (Skip-Already-Processed)**:
"This implements idempotency at the batch level. The check via `papers_processed` list is O(n) but acceptable for hundreds of papers.

**Caveat**: If scaling to thousands of papers, consider a bloom filter or set-based lookup.

**Approved for MVP scale**."

---

### Dr. Michael T. Fisher (Distributed Systems):

**On D1 (Circuit Breaker)**:
"In distributed systems, we distinguish between:
- **Fail-fast**: Stop immediately on any error
- **Fail-safe**: Continue despite errors
- **Circuit breaker**: Stop after pattern indicates systematic failure

Your choice of circuit breaker is appropriate for batch processing where you want resilience to transient errors but protection against systematic failures.

**Approved**."

**On D3 (Progress JSON)**:
"The progress file is essentially a checkpoint. For true crash recovery, you'd need:
1. Checkpoint before processing (current paper ID)
2. Checkpoint after processing (completed paper ID)

Your current design checkpoints completed work, which is sufficient for 'resume from last good state.'

**Approved**. The 10-paper interval is reasonable."

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1 | **APPROVED** | No changes; consider half-open state in future |
| D2 | **APPROVED** | No changes needed |
| D3 | **APPROVED** | Consider 'resume from progress' feature (deferred) |
| D4 | **APPROVED** | Consider bloom filter for large scale (deferred) |

---

## Action Items

### Immediate
None required—all decisions approved as implemented.

### Deferred (Future Scaling)
1. [ ] Add 'half-open' circuit breaker state (retry after cooldown)
2. [ ] Add 'resume from progress file' feature
3. [ ] Use bloom filter or set for papers_processed at scale (>1000 papers)

---

## Panel Sign-off

**Status**: APPROVED

All four decisions follow established patterns for batch processing systems (Circuit Breaker, Checkpointing, Idempotency). The implementation is appropriate for MVP scale; scaling recommendations noted for future.

*Panel consultation complete: 2026-02-11*
