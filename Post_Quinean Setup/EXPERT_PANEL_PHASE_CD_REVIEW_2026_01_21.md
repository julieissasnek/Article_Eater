# Expert Panel Review: Phase C-D Implementation Decisions

**Date**: January 21, 2026
**Sprints Covered**: C1-C4 (Query & Ingestion), D1-D2 (Stopping & Reporting)
**Status**: Implementation complete, seeking retrospective review

---

## Context

During a batch implementation session, I implemented Phases C and D autonomously. The user requested I "continue in batch through all the sprints" with minimal interruption. This document identifies **12 key design decisions** that would benefit from expert panel review.

All features are working (181 tests passing), but these decisions embed significant epistemic and design assumptions that should be validated.

---

## Decision Point 1: Query Type Taxonomy (C1)

**File**: `src/services/query_parser.py:28-56`

**Decision Made**: Created 13 query types organized into 5 categories:
- Factual: WHAT_IS, DOES_X_AFFECT_Y, HOW_MUCH
- Exploratory: WHAT_DO_WE_KNOW, WHAT_EVIDENCE
- Comparative: COMPARE, WHICH_IS_BETTER
- Meta: HOW_CONFIDENT, WHY_BELIEVE, WHAT_CONTRADICTS
- Scope: WHAT_DONT_KNOW, WHEN_DOES, FOR_WHOM

**Rationale**: Covers the question types most relevant to systematic review of scientific evidence.

**Questions for Panel**:
1. Is this taxonomy complete for neuroarchitecture evidence queries?
2. Should there be a WHAT_CAUSES vs WHAT_CORRELATES distinction?
3. Are meta-queries (WHY_BELIEVE, WHAT_CONTRADICTS) appropriate for users or should they be internal?

---

## Decision Point 2: Vocabulary Bridge as Static Mapping (C1)

**File**: `src/services/query_parser.py` (VOCABULARY_BRIDGE dict)

**Decision Made**: Created static synonym mappings:
```python
VOCABULARY_BRIDGE = {
    "natural light": ["daylight", "sunlight", "daylighting", "natural lighting"],
    "productivity": ["performance", "output", "efficiency", "work output"],
    "stress": ["anxiety", "cortisol", "tension", "psychological strain"],
    # ... 20+ terms
}
```

**Rationale**: Ensures consistent vocabulary expansion without LLM dependency.

**Questions for Panel**:
1. Should vocabulary expansion be dynamic (embedding-based similarity) or static?
2. How do we handle domain drift if new terminology emerges?
3. Should users be able to add/modify mappings? (Bates: transparency concern)

---

## Decision Point 3: Causal Claim Detection via Keywords (C2)

**File**: `src/services/query_response.py:310-318`

**Decision Made**: Detect causal claims using keyword matching:
```python
causal_keywords = [
    'cause', 'effect', 'affect', 'impact', 'influence',
    'improve', 'reduce', 'increase', 'decrease', 'lead to',
    'result in', 'because', 'due to'
]
```

**Rationale**: Simple, interpretable, no false negatives for strong causal language.

**Questions for Panel**:
1. Is keyword detection sufficient or do we need semantic analysis?
2. "Improve" and "reduce" are directional but not necessarily causal—should they be included?
3. Should hedged language ("may affect", "potentially reduces") be treated differently?

---

## Decision Point 4: Confidence Level Thresholds (C2)

**File**: `src/services/query_response.py:256-266`

**Decision Made**: Three-tier confidence classification:
- **High**: avg_credence ≥ 0.70
- **Medium**: 0.40 ≤ avg_credence < 0.70
- **Low**: avg_credence < 0.40
- **Unknown**: no matching beliefs

**Rationale**: Maps to intuitive labels; 0.70 is conventional "strong evidence" threshold.

**Questions for Panel**:
1. Are these thresholds appropriate for neuroarchitecture evidence?
2. Should confidence account for uncertainty (credence ± uncertainty) rather than point estimate?
3. Should we differentiate "low confidence" from "conflicting evidence"?

---

## Decision Point 5: Five Stopping Criteria Selection (D1)

**File**: `src/services/stopping_rules.py:28-37, 150-178`

**Decision Made**: Implemented 5 stopping criteria:
1. **Saturation**: No new themes in recent N beliefs (80% threshold)
2. **Confidence**: Average credence meets threshold (default 0.70)
3. **Count**: Minimum evidence quantity (default 5)
4. **Coverage**: At least 2 of 4 epistemic levels present (50%)
5. **Contradiction Stability**: Contested rate stable between old/new halves

**Rationale**: Multi-criteria approach avoids premature stopping while catching saturation.

**Questions for Panel**:
1. Are these the right 5 criteria? Should cost-benefit or time budget be active (currently defined but not evaluated)?
2. Is the saturation algorithm (first-5-words theme hashing) too crude?
3. Should criteria be weighted differently based on query type?

---

## Decision Point 6: Stopping Decision Logic (D1)

**File**: `src/services/stopping_rules.py:280-295`

**Decision Made**: Stop when:
- Minimum evidence criterion is met, AND
- At least 60% of criteria are met

```python
has_min_evidence = any(c.reason == StoppingReason.EVIDENCE_COUNT and c.is_met for c in criteria_met)
should_stop = has_min_evidence and met_ratio >= 0.6
```

**Rationale**: Requires baseline evidence plus majority of quality indicators.

**Questions for Panel**:
1. Is 60% the right threshold, or should it be configurable per use case?
2. Should minimum evidence be a hard gate, or weighted like other criteria?
3. For systematic reviews, should we ever recommend stopping before saturation?

---

## Decision Point 7: Expected Outcome Categories (D2)

**File**: `src/services/reporting.py:311-314`

**Decision Made**: Hardcoded 8 expected outcomes for gap analysis:
```python
expected_outcomes = {
    'productivity', 'cognition', 'stress', 'wellbeing',
    'health', 'creativity', 'attention', 'mood'
}
```

**Rationale**: Core neuroarchitecture outcomes per CNFA domain.

**Questions for Panel**:
1. Is this list complete? Missing: sleep, social, recovery, perception?
2. Should expected outcomes be configurable or derived from the taxonomy?
3. How do we handle outcomes that span categories (e.g., "cognitive stress")?

---

## Decision Point 8: Quality Score Formula (D2)

**File**: `src/services/reporting.py:410-415`

**Decision Made**: Composite quality score:
```python
quality_score = (
    (full_text_pct * 0.4) +           # Source depth
    (multi_source_ratio * 0.3) +      # Corroboration
    (avg_credence * 0.3)              # Confidence
)
```

**Rationale**: Weights full-text access highest (per Cartwright), with corroboration and confidence secondary.

**Questions for Panel**:
1. Are these weights appropriate? Should Cartwright's concern (source depth) dominate?
2. Should quality score penalize high uncertainty explicitly?
3. Should recency of evidence factor into quality?

---

## Decision Point 9: Gap Analysis Categories (D2)

**File**: `src/services/reporting.py:302-370`

**Decision Made**: Five gap categories:
1. Missing outcome categories
2. Abstract-only causal claims (Cartwright flag)
3. High uncertainty beliefs (≥25% uncertainty)
4. Single-source beliefs
5. Unscoped causal claims (missing population/setting)

**Rationale**: Each identifies a different type of epistemic weakness.

**Questions for Panel**:
1. Are there other gap types we should detect? (e.g., temporal gaps, methodological gaps)
2. Is 25% uncertainty the right threshold for "high uncertainty"?
3. Should gaps be prioritized/ranked by severity?

---

## Decision Point 10: Ingestion Warnings (C3)

**File**: `app/routes/ingestion.py:280-310`

**Decision Made**: Auto-generate warnings for:
- Causal claims marked `is_causal=True` from abstracts
- Causal language detected when `is_causal=False` (prompt to reconsider)
- Abstract-only sources with any causal keywords

**Rationale**: Proactive Cartwright warnings at ingestion time.

**Questions for Panel**:
1. Are these warnings helpful or will they cause warning fatigue?
2. Should warnings block ingestion or just inform?
3. Should there be a "I've verified this" override option?

---

## Decision Point 11: Follow-up Question Generation (C2)

**File**: `src/services/query_response.py:349-402`

**Decision Made**: Generate exactly 3 follow-ups per Simon's recommendation:
1. **Deeper**: "What are the mechanisms by which {subject} affects {object}?"
2. **Broader**: "What other factors also affect {object}?"
3. **Uncertainty**: Context-dependent (contested → "Why is evidence contested?", gaps → "What don't we know?", limited → "What research is needed?")

**Rationale**: Per Simon (Q2), exactly 3 provides structure without overwhelming.

**Questions for Panel**:
1. Are these the right 3 directions, or should we vary based on query type?
2. Should follow-ups be generated from actual evidence gaps rather than templates?
3. Should users be able to request more/fewer follow-ups?

---

## Decision Point 12: Evidence Limit Defaults (C4)

**File**: `app/routes/query.py:50-51`

**Decision Made**: Default limits:
- `max_evidence`: 10 items per response
- Beliefs sorted by relevance score then credence

**Rationale**: Balances comprehensiveness with cognitive load.

**Questions for Panel**:
1. Is 10 the right default? Should it vary by response type?
2. Should we show "and N more..." indicator when truncating?
3. Should highly contested beliefs be surfaced even if low relevance?

---

## Summary Table

| # | Decision | Key Values | Primary Concern |
|---|----------|------------|-----------------|
| 1 | Query taxonomy | 13 types, 5 categories | Completeness |
| 2 | Vocabulary bridge | Static mappings | Maintainability |
| 3 | Causal detection | 13 keywords | False positives |
| 4 | Confidence thresholds | 0.70/0.40 cutoffs | Calibration |
| 5 | Stopping criteria | 5 criteria | Completeness |
| 6 | Stopping logic | 60% + min evidence | Threshold choice |
| 7 | Expected outcomes | 8 categories | Domain coverage |
| 8 | Quality formula | 40/30/30 weights | Weighting |
| 9 | Gap categories | 5 types, 25% uncertainty | Completeness |
| 10 | Ingestion warnings | 3 auto-warnings | Warning fatigue |
| 11 | Follow-up generation | 3 template types | Flexibility |
| 12 | Evidence limits | 10 default | Cognitive load |

---

## Requested Panel Response Format

For each decision point, please provide:
1. **Assessment**: Approve / Modify / Rethink
2. **Specific Concerns**: Any issues with the current implementation
3. **Recommended Changes**: If "Modify" or "Rethink", what specifically should change
4. **Priority**: High / Medium / Low (for any recommended changes)

---

## Panel Members

- **Dr. Judea Pearl** — Causal inference, Bayesian networks
- **Dr. Nancy Cartwright** — Philosophy of science, evidence quality
- **Dr. Herbert Simon** — Bounded rationality, satisficing
- **Dr. Marcia Bates** — Information science, vocabulary/retrieval
- **Dr. Rachel Kaplan** — Environmental psychology (domain expert)
