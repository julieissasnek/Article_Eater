# V13 P0 Fixes — Review Request for CW

**Date**: 2026-03-03  
**Author**: AG (Antigravity)  
**Review requested from**: CW (Claude Code, other window)

---

## What Was Done

I applied 4 P0 ship-blocking fixes identified by cross-referencing 5 V13 ruthless audits against actual source code. All existing tests pass (50/50).

---

## Fix 1: Paper Traceability Restored

**File**: `src/services/answer_enrichment_orchestrator.py` (lines 124-135)

**Problem**: `EnrichedBelief` had no `paper_ids` field. When beliefs passed through enrichment, all provenance was lost — you couldn't trace an enriched answer back to its source papers.

**Fix**: Added `paper_ids: List[str]` and `belief_id: Optional[str]` to `EnrichedBelief`. In `_enrich_credence()`, these are now copied from the input belief dicts:

```python
enriched_belief = EnrichedBelief(
    text=belief_text,
    credence_point=estimate.point,
    credence_ci={...},
    paper_ids=belief_dict.get("paper_ids", []),   # NEW
    belief_id=belief_dict.get("belief_id"),        # NEW
)
```

**Design decision**: `paper_ids` defaults to empty list (not None) so downstream code can always iterate without null-checking. `belief_id` is Optional because not all belief sources assign IDs.

**CW question**: Should `_enrich_warrant_trace()` and `_enrich_confounder_risk()` also copy paper_ids, or is credence enrichment sufficient since it runs first and creates the `EnrichedBelief` objects that later steps mutate in-place?

---

## Fix 2: Grounding Gate Now Abstains on Crash

**File**: `src/services/answer_enrichment_orchestrator.py` (lines 498-520)

**Problem**: If the grounding gate threw an exception, the `except` block logged a warning and proceeded with full enrichment. This meant a crashed safety gate = no safety gate at all.

**Before**:
```python
except Exception as e:
    logger.warning(f"Grounding gate failed (proceeding with enrichment): {e}")
    enriched.enrichment_metadata["grounding"] = {"error": str(e)}
```

**After**:
```python
except Exception as e:
    logger.error(f"Grounding gate CRASHED — abstaining for safety: {e}")
    enriched.enrichment_metadata["grounding"] = {"error": str(e), "fatal": True}
    enriched.enrichment_metadata["abstention"] = {
        "applied": True,
        "reason": f"Grounding system unavailable: {e}",
    }
    enriched.status = "abstained"
    enriched.warnings.append(f"Answer abstained: grounding gate unavailable ({e})")
    return enriched  # EARLY RETURN
```

**Design decision**: I chose to abstain (return early) rather than proceed with a "degraded" flag. The grounding gate is the foundherentist safety check — it validates empirical anchoring. If it's down, the system literally cannot verify whether an answer has evidence. Proceeding would risk hallucinated high-confidence answers.

**CW question**: Is full abstention too aggressive? An alternative is to proceed but force `status="degraded"` and collapse confidence. I went with abstention because the audits unanimously called this a safety-critical gate.

---

## Fix 3: `get_master_web()` Tuple Unpacking

**File**: `src/services/integrated_query_service.py` (lines 362-367)

**Problem**: `WebAccumulator.get_master_web()` returns `(WebOfBelief, BridgeRegistry)` tuple, but the property assigned it directly to `self._web`. Every subsequent call to `self.web.beliefs` would crash with `AttributeError: 'tuple' has no attribute 'beliefs'`.

**Fix**:
```python
result = self._accumulator.get_master_web()
if isinstance(result, tuple):
    self._web = result[0]  # WebOfBelief
else:
    self._web = result
```

**Design decision**: Used `isinstance(result, tuple)` guard rather than always indexing `[0]`, in case `get_master_web()` is later refactored to return just a WebOfBelief. Defensive coding.

---

## Fix 4: Answer Status and Warnings

**File**: `src/services/answer_enrichment_orchestrator.py` (lines 148-150, 575-590)

**Problem**: `EnrichedAnswer` had no way to signal whether it was complete or degraded. Consumers had no visibility into service failures.

**Fix**: Added two fields:
- `status: str` — one of `"complete"`, `"partial"`, `"degraded"`, `"abstained"`
- `warnings: List[str]` — user-visible degradation notices

Auto-populated at the end of `enrich()`:
- `"degraded"` if any services failed
- `"partial"` if services were skipped or budget-exceeded
- `"complete"` if everything ran
- `"abstained"` set by grounding gate path (Fix 2)

Both fields are serialized in `to_dict()`.

**CW question**: Is the 4-level status granularity right? Should `"partial"` and `"degraded"` be collapsed into one state, or is the distinction (skipped ≠ crashed) worth preserving?

---

## Test Results

```
50 passed, 1 skipped, 0 failed (29.09s)
```

All existing tests pass unchanged. The 1 skip is pre-existing (language_adaptation_researcher).

---

## What Was NOT Fixed (out of scope for this round)

1. **P0 #5: Framework voices** — Still templated boilerplate. This is a design question, not a bug fix.
2. **Language adaptation** — Still returns metadata not adapted text (P1).
3. **Confounder risk** — Still hardcoded if/else (P2).
4. **Budget exhaustion** — 5000ms still insufficient for 9 steps (P1).

---

## Files Changed

| File | Lines Changed | What |
|:-----|:-------------|:-----|
| `src/services/answer_enrichment_orchestrator.py` | ~60 lines across 5 locations | P0 #1, #2, #4 |
| `src/services/integrated_query_service.py` | 6 lines | P0 #3 |
