# Panel Consultation: Query Alerts and Monitoring System

**Date**: 2026-02-09
**Sprint**: 3.0.2-G
**Module**: `src/services/query_alerts.py`
**Decisions Under Review**: D1–D7

---

## Panel Composition

Given the nature of an alerting/monitoring system, we convene experts in:
- **System design and bounded rationality**: Dr. Herbert Simon
- **Naturalistic decision making**: Dr. Gary Klein
- **Cognitive psychology and attention**: Dr. Daniel Kahneman
- **Information science and search behavior**: Dr. Marcia Bates
- **Domain context (environmental psychology)**: Dr. Rachel Kaplan

---

## Decision D1: Alert Condition Types

### Context

The system must detect meaningful changes in the Web of Belief. We implemented 11 alert types:

1. **Belief-level**: CREDENCE_CHANGE, STATUS_CHANGE, NEW_EVIDENCE, ENTRENCHMENT_CHANGE
2. **Constraint-level**: CONSTRAINT_ADDED, CONSTRAINT_REMOVED
3. **Theory-level**: THEORY_SHIFT, THEORY_CONTESTED
4. **System-level**: COHERENCE_DROP, NEW_STUB
5. **Custom**: PATTERN_MATCH

### Question

Is this taxonomy of alert types appropriate? Are there missing categories? Is the granularity correct?

### Current Implementation

```python
class AlertType(Enum):
    CREDENCE_CHANGE = "credence_change"
    STATUS_CHANGE = "status_change"
    NEW_EVIDENCE = "new_evidence"
    ENTRENCHMENT_CHANGE = "entrenchment_change"
    CONSTRAINT_ADDED = "constraint_added"
    CONSTRAINT_REMOVED = "constraint_removed"
    THEORY_SHIFT = "theory_shift"
    THEORY_CONTESTED = "theory_contested"
    COHERENCE_DROP = "coherence_drop"
    NEW_STUB = "new_stub"
    PATTERN_MATCH = "pattern_match"
```

---

## Panel Responses: D1

### Dr. Herbert Simon (Bounded Rationality, System Design)

The taxonomy follows sound principles of hierarchical decomposition. I note three observations:

1. **Level-appropriate alerts**: The three-tier structure (belief, theory, system) respects the natural abstraction hierarchy. Researchers monitoring specific claims need different signals than those monitoring paradigm health.

2. **Missing: ANOMALY_DETECTED**. Your current types assume expected changes. Consider adding an alert for *statistical anomalies*—patterns that deviate from historical norms without fitting predefined categories. Satisficing agents benefit from exception-based monitoring.

3. **ENTRENCHMENT_CHANGE is redundant given V23.0.0**. Since entrenchment is now emergent (computed from connectivity + level + coherence), changes in entrenchment are always downstream of other alertable events. Consider removing it to reduce cognitive load.

### Dr. Gary Klein (Naturalistic Decision Making)

From a Recognition-Primed Decision perspective:

1. **Pattern recognition matters more than thresholds**. Expert researchers don't think "credence changed by 0.15"; they think "this finding is now less certain than that related finding." Consider adding RELATIVE_SHIFT alerts comparing beliefs within a cluster.

2. **NEW_STUB is excellent**. Stubs represent *cues* that the situation differs from the mental model—exactly what experts scan for. I'd prioritize this type.

3. **Missing: CONVERGENCE and DIVERGENCE**. When multiple independent lines of evidence converge (or diverge), that's decision-relevant. The current system alerts on individual changes but not on multi-source patterns.

### Dr. Daniel Kahneman (Cognitive Psychology, Attention)

I have concerns about alert fatigue:

1. **11 types is near the upper bound**. Miller's 7±2 applies here. Users will likely enable 3-4 types and ignore the rest. Design for the realistic case.

2. **CREDENCE_CHANGE will dominate**. In active research databases, credence changes constantly. Without careful threshold tuning, this one type will generate 90% of alerts.

3. **Consider severity-based filtering**. Rather than type-based subscription, let users say "only alert me on WARNING+ severity." The current severity calculation (based on change magnitude) is a good start.

4. **ENTRENCHMENT_CHANGE adds little signal**. Users don't have direct intuition about entrenchment. Alert on the *causes* (new constraints, coherence shifts), not the derived metric.

### Dr. Marcia Bates (Information Science)

From an information behavior perspective:

1. **The taxonomy maps well to Bates' RELATED and CANONICAL patterns**. NEW_EVIDENCE supports berry-picking; THEORY_SHIFT supports paradigm monitoring.

2. **Consider STALE_EVIDENCE**. Research moves fast. A belief that hasn't received new evidence in 2+ years might be stale—either well-established or abandoned. Both states are informative.

3. **PATTERN_MATCH is too flexible**. Without structure, users create overlapping, redundant patterns. Provide templates: "beliefs mentioning [topic]", "beliefs from [author]", etc.

### Dr. Rachel Kaplan (Environmental Psychology)

From the domain perspective:

1. **THEORY_CONTESTED is crucial**. In environmental psychology, ART vs. SRT debates are central. Alerting when theories enter contested states directly supports scholarly work.

2. **Consider REPLICATION_NEEDED**. When credence is moderate (0.4–0.6) with high uncertainty, the field needs replication. This isn't currently an alert type.

3. **NEW_STUB + topic patterns together serve "gap hunting"**. Researchers looking for dissertation topics would use these together.

---

## Synthesis: D1

| Recommendation | Source | Action |
|----------------|--------|--------|
| Remove ENTRENCHMENT_CHANGE | Simon, Kahneman | **ACCEPT** — Redundant with causative alerts |
| Add ANOMALY_DETECTED | Simon | **DEFER** — Useful but adds complexity; revisit in v2 |
| Add RELATIVE_SHIFT | Klein | **DEFER** — Requires cluster definition; future feature |
| Add CONVERGENCE/DIVERGENCE | Klein | **DEFER** — Multi-source patterns are v2 |
| Add STALE_EVIDENCE | Bates | **CONSIDER** — Simple timestamp check; low effort |
| Provide PATTERN_MATCH templates | Bates | **ACCEPT** — Add convenience functions |

**Consensus Action for D1**: Remove ENTRENCHMENT_CHANGE from AlertType enum. Add STALE_EVIDENCE as a simple time-based alert. Document PATTERN_MATCH with recommended patterns.

---

## Decision D2: Notification Delivery Mechanism

### Context

We support three notification channels:
1. **In-app queue** — Internal list for Streamlit UI polling
2. **Webhook** — HTTP POST to external endpoint
3. **Email** — Placeholder (not implemented)

### Question

Is this channel mix appropriate? Should we prioritize any channel differently?

### Current Implementation

- InAppNotificationHandler: Thread-safe list with acknowledge()
- WebhookNotificationHandler: urllib POST with 10s timeout
- EmailNotificationHandler: Placeholder returning True if email set

---

## Panel Responses: D2

### Dr. Herbert Simon

1. **Webhook is essential for integration**. Research systems don't exist in isolation. Webhook enables Slack, Discord, custom dashboards—whatever the lab uses.

2. **Email is lowest priority**. Academic email is overloaded. Researchers check email reactively, not for real-time alerts. In-app + webhook suffices.

3. **Consider batch webhooks**. Individual POSTs for every alert is expensive. Offer a "digest mode" that batches alerts before sending.

### Dr. Gary Klein

1. **In-app is the right primary channel**. Researchers are in the application when they need context. Interrupting them elsewhere loses the recognition-primed advantage.

2. **Webhook should support rich context**. Include not just the alert but the belief content, related beliefs, and recent history. Experts need surrounding context to make sense of signals.

### Dr. Daniel Kahneman

1. **Multi-channel redundancy is dangerous**. If users enable both in-app and webhook, they see every alert twice. This trains them to ignore alerts.

2. **Recommend a primary channel selection**. Each watch should have ONE primary notification method, with others as fallback.

3. **The current 10s webhook timeout is generous**. Most webhooks respond in <1s. Long timeouts block the alert loop.

### Dr. Marcia Bates

1. **In-app queue matches monitoring behavior**. Researchers check dashboards periodically—exactly the pattern in-app supports.

2. **Webhook enables SDI (Selective Dissemination of Information)**. This is a classic information science service. The implementation aligns with established practice.

---

## Synthesis: D2

| Recommendation | Source | Action |
|----------------|--------|--------|
| Keep email as low priority | Simon | **ACCEPT** — Already placeholder |
| Add digest mode for webhooks | Simon | **DEFER** — Future enhancement |
| Include rich context in webhooks | Klein | **ACCEPT** — Already sending alert + watch info |
| Recommend primary channel | Kahneman | **CONSIDER** — Add to documentation |
| Reduce webhook timeout | Kahneman | **ACCEPT** — Change 10s → 5s |

**Consensus Action for D2**: Reduce webhook timeout to 5s. Document recommendation for single primary channel per watch. Current architecture is sound.

---

## Decision D3: Alert Persistence (SQLite + Cache)

### Context

We use SQLite for durable storage with an in-memory cache for frequently accessed watches.

### Question

Is SQLite appropriate, or should we use the main application database? Is the caching strategy correct?

### Current Implementation

- Separate SQLite database (alerts.db)
- In-memory dict cache for watches
- Cache populated on read, updated on write

---

## Panel Responses: D3

### Dr. Herbert Simon

1. **Separate database is correct**. Alerts are operational data with different lifecycle than research content. Separation enables independent backup/purge policies.

2. **The cache invalidation strategy is simple but correct**. For a single-user research tool, write-through cache is adequate.

3. **Consider sqlite WAL mode**. For concurrent access (multiple Streamlit sessions), WAL provides better isolation.

### Dr. Daniel Kahneman

1. **Separation reduces cognitive load**. Researchers don't want alert history mixed with their research database. Clear separation is intuitive.

### Dr. Marcia Bates

1. **30-day retention default is appropriate**. This matches typical research cycle length. Important alerts can be starred/saved separately.

---

## Synthesis: D3

| Recommendation | Source | Action |
|----------------|--------|--------|
| Keep separate database | Simon, Kahneman | **ACCEPT** — Already implemented |
| Enable WAL mode | Simon | **ACCEPT** — Simple pragma change |
| Keep 30-day default | Bates | **ACCEPT** — Already implemented |

**Consensus Action for D3**: Enable WAL mode in SQLite initialization. Current architecture is validated.

---

## Decision D4: Watch Granularity

### Context

Watches can target five entity types:
1. BELIEF — Specific belief_id
2. THEORY — Theory_id (all beliefs in theory)
3. TOPIC — Regex pattern on content
4. LEVEL — Epistemic level (THEORETICAL, EMPIRICAL, etc.)
5. SYSTEM — Global metrics

### Question

Is this granularity sufficient? Too much? Should CREDENCE_RANGE be a separate target type or a condition modifier?

### Current Implementation

WatchTarget enum with matches_belief() method checking each type.

---

## Panel Responses: D4

### Dr. Herbert Simon

1. **Five levels is at the edge of complexity**. Each level adds cognitive overhead. I'd argue LEVEL is the weakest—users rarely think "alert me on all EMPIRICAL beliefs."

2. **CREDENCE_RANGE should be a condition modifier, not a target**. "Watch beliefs with credence 0.4–0.6" is a filter, not a target. Current implementation as a condition (min_credence/max_credence) is correct.

### Dr. Gary Klein

1. **TOPIC pattern is the most naturalistic**. Experts think in topics: "anything about stress and nature," "anything about circadian rhythms." This should be the most prominent option.

2. **Consider adding SOURCE (author/journal)**. Experts track trusted authors and suspect journals. "Alert me when a Kaplan paper is processed" is a natural request.

### Dr. Rachel Kaplan

1. **THEORY is essential for paradigm monitoring**. I'd keep all five.

2. **LEVEL might serve methodology tracking**. If a theory is moving from theoretical to empirical grounding (more EMPIRICAL beliefs), that's progress. LEVEL watches could detect this.

### Dr. Marcia Bates

1. **The granularity mirrors faceted classification**. Topic, level, theory, and system are orthogonal facets. This supports combination queries naturally.

---

## Synthesis: D4

| Recommendation | Source | Action |
|----------------|--------|--------|
| CREDENCE_RANGE as condition is correct | Simon | **VALIDATED** |
| Consider removing LEVEL | Simon | **REJECT** — Kaplan/Bates justify keeping it |
| Add SOURCE target | Klein | **DEFER** — Useful but requires paper provenance tracking |
| Keep TOPIC prominent | Klein | **ACCEPT** — Document as primary use case |

**Consensus Action for D4**: Current five-level granularity is validated. Document TOPIC as the primary discovery mechanism.

---

## Decision D5: Threshold Semantics

### Context

AlertCondition supports both:
- threshold_absolute: e.g., 0.1 (10% credence change)
- threshold_percentage: e.g., 20.0 (20% relative change)

These use OR logic—meeting either triggers the alert.

### Question

Should thresholds use AND or OR logic? Is supporting both types necessary?

### Current Implementation

```python
if self.threshold_absolute is not None:
    if abs(absolute_change) >= self.threshold_absolute:
        triggered = True

if self.threshold_percentage is not None:
    if abs(percentage_change) >= self.threshold_percentage:
        triggered = True
```

---

## Panel Responses: D5

### Dr. Herbert Simon

1. **OR logic is correct for alerting**. Users want to catch any significant change. AND logic would create false negatives.

2. **Both threshold types are necessary**. Absolute: "alert if credence changes by 0.15 regardless of starting point." Percentage: "alert if credence drops by 50%." Different use cases.

### Dr. Daniel Kahneman

1. **Beware threshold tuning paralysis**. Users will spend inordinate time choosing between 0.1 and 0.15. Provide sensible defaults and hide the complexity.

2. **Consider preset "sensitivity levels"**. Low (0.2/40%), Medium (0.1/20%), High (0.05/10%) rather than raw numbers.

### Dr. Marcia Bates

1. **OR logic supports exploratory monitoring**. Users in exploration phase want to see more, not less. They can tighten thresholds after understanding the data.

---

## Synthesis: D5

| Recommendation | Source | Action |
|----------------|--------|--------|
| Keep OR logic | Simon, Bates | **VALIDATED** |
| Keep both threshold types | Simon | **VALIDATED** |
| Add preset sensitivity levels | Kahneman | **ACCEPT** — Add convenience functions |

**Consensus Action for D5**: Current implementation validated. Add convenience functions for LOW/MEDIUM/HIGH sensitivity presets.

---

## Decision D6: Deduplication (5-Minute Cooldown)

### Context

Each watch has a cooldown_minutes parameter (default 5). After triggering, the watch won't re-trigger for that duration.

### Question

Is 5 minutes an appropriate default? Should cooldown be per-watch or per-belief?

### Current Implementation

- cooldown_minutes per watch
- last_triggered stored in Watch
- can_trigger() checks cooldown before matching

---

## Panel Responses: D6

### Dr. Daniel Kahneman

1. **5 minutes is reasonable for interactive use**. Too short (< 1 min) causes alert storms; too long (> 30 min) misses rapid changes.

2. **Per-watch is correct**. A watch on "theory ART" shouldn't fire for every belief change within ART during a bulk update. The watch-level cooldown aggregates appropriately.

3. **Consider event-based cooldown reset**. If the user acknowledges an alert, reset the cooldown immediately—they're paying attention.

### Dr. Gary Klein

1. **Cooldown matches expert attention patterns**. Researchers check alerts periodically, not continuously. 5 minutes aligns with natural break points.

2. **Allow cooldown=0 for live monitoring**. During active data entry, researchers may want immediate feedback. Zero cooldown enables this.

### Dr. Herbert Simon

1. **The default should be conservative (longer)**. Alert fatigue is worse than missed alerts. Consider 15 minutes as default.

---

## Synthesis: D6

| Recommendation | Source | Action |
|----------------|--------|--------|
| Per-watch cooldown is correct | Kahneman | **VALIDATED** |
| 5 min default is reasonable | Kahneman, Klein | **VALIDATED** — Consider documenting 15 min for busy databases |
| Allow cooldown=0 | Klein | **VALIDATED** — Already supported |
| Acknowledgment resets cooldown | Kahneman | **CONSIDER** — Nice enhancement |

**Consensus Action for D6**: Current implementation validated. Document that cooldown=0 enables live monitoring and suggest 10-15 min for busy databases.

---

## Decision D7: Historical Retention (30 Days)

### Context

retention_days (default 30) determines how long alerts are kept before cleanup.

### Question

Is 30 days appropriate? Should retention be per-watch or global?

### Current Implementation

- retention_days per watch
- cleanup_old_alerts() uses default if not specified
- No automatic cleanup (must be called explicitly)

---

## Panel Responses: D7

### Dr. Marcia Bates

1. **30 days matches typical research sprints**. Most literature reviews operate on 1-4 week cycles. 30 days captures the full cycle.

2. **Consider "starred" alerts that never expire**. Important alerts (e.g., "paradigm shift detected") should be preservable.

### Dr. Herbert Simon

1. **Per-watch retention is unnecessary complexity**. Global retention with manual archiving is simpler. Researchers won't customize retention per-watch.

2. **Add automatic cleanup**. The current manual approach will lead to unbounded growth. Run cleanup on application start.

### Dr. Daniel Kahneman

1. **Alert history enables trend analysis**. Don't delete—archive. "How often has theory X been contested in the past year?" is a valid question.

---

## Synthesis: D7

| Recommendation | Source | Action |
|----------------|--------|--------|
| 30 days is appropriate | Bates | **VALIDATED** |
| Add starred alerts | Bates | **DEFER** — Future enhancement |
| Simplify to global retention | Simon | **ACCEPT** — Make per-watch retention optional |
| Add automatic cleanup on start | Simon | **ACCEPT** — Simple improvement |
| Archive don't delete | Kahneman | **CONSIDER** — Keep alerts table, add archived flag |

**Consensus Action for D7**: Add automatic cleanup on AlertManager initialization. Consider archived flag instead of delete in future version.

---

## Implementation Summary

### Immediate Changes (This Sprint)

1. **D1**: Remove ENTRENCHMENT_CHANGE from AlertType enum (redundant with emergent entrenchment)
2. **D2**: Reduce webhook timeout from 10s to 5s
3. **D3**: Enable SQLite WAL mode
4. **D5**: Add convenience functions for sensitivity presets (LOW/MEDIUM/HIGH)
5. **D7**: Add automatic cleanup on AlertManager init

### Documentation Additions

1. Document TOPIC pattern as primary discovery mechanism (D4)
2. Document single primary channel recommendation (D2)
3. Document cooldown=0 for live monitoring, suggest 10-15 min for busy DBs (D6)

### Deferred to Future Version

1. ANOMALY_DETECTED, RELATIVE_SHIFT, CONVERGENCE/DIVERGENCE alert types
2. Digest mode for webhooks
3. SOURCE target type for author/journal tracking
4. Starred alerts that never expire
5. Archived flag instead of delete

---

## Panel Endorsement

The panel reaches **consensus** that the query_alerts.py implementation is architecturally sound. The recommended immediate changes are refinements, not corrections. The system appropriately balances:

- **Flexibility** (multiple watch granularities, condition types)
- **Simplicity** (sensible defaults, clear abstractions)
- **Integration** (webhook for external systems)
- **Performance** (SQLite + cache hybrid)

**Approved for release with noted modifications.**

---

*Panel consultation completed: 2026-02-09*
