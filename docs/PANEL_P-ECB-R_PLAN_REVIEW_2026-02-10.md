# Panel P-ECB-R: Implementation Plan Review

**Date**: 2026-02-10
**Document**: Review of `IMPLEMENTATION_PLAN_BRIDGE_REPAIR_2026-02-10.md`
**Reviewers**: Original panel + system developers

---

## Additional Reviewers

| Expert | Domain | Role |
|--------|--------|------|
| **David Parnas** | Software Architecture | Module design, information hiding |
| **Fred Brooks** | Software Engineering | System integration, project management |

---

## Panel Review: Sprint ECB-1 (Cleanup)

### Task ECB-1.1: Archive Features to Quarantine

**Simon**: *"Good. You're removing 600+ lines of unused code while preserving it for future use. This is exactly the satisficing approach—solve today's problem, don't lose tomorrow's options."*

**Parnas**: *"The archive documentation is thorough. I approve of moving code to quarantine rather than deleting. One addition: each archived file should have a header comment indicating:
1. Date archived
2. Why archived (not 'bad', but 'premature')
3. Dependencies it would need if reintegrated

This prevents future developers from re-implementing without checking quarantine."*

**Recommendation**: Add header comments to archived files.

### Task ECB-1.2: Delete Duplicate Class Definitions

**Parnas**: *"This is a textbook information hiding violation. The bridge should not define its own `Belief` class when it operates on `web_of_belief.Belief` objects. The plan correctly identifies this.*

*However, I see a risk: the bridge's `Belief` class (lines 150-192) has a field `contrast_class: Optional[ContrastClass]` that `web_of_belief.Belief` does not have. You need to verify this isn't breaking functionality."*

**Action Required**: Check if any code depends on `bridge.Belief.contrast_class`. If so, add to `web_of_belief.Belief` or handle differently.

**Brooks**: *"The import list is getting long. Consider whether you need ALL of these imports or if a facade pattern would help. But for now, explicit imports are fine—clarity over brevity."*

### Task ECB-1.3: Consolidate Implementations

**Brooks**: *"Two implementations is exactly the 'second system effect' in reverse—someone built something new without retiring the old. Consolidation is overdue.*

*I recommend: Don't try to merge. Pick one (the repo file), update it, and archive the other. Merging risks introducing bugs from the less-tested version."*

**Parnas**: *"Agreed. The external file is 84KB—larger than the repo file. This suggests it has features the repo file lacks. Inventory those features before archiving. If any are needed, add them to the repo file explicitly, not by blind merge."*

**Action Required**: Before consolidating, diff the two files and document differences.

---

## Panel Review: Sprint ECB-2 (Core Integration)

### Task ECB-2.1: Simplify EpistemicCausalBridge Class

**Simon**: *"Target of 500 lines is good. Current 2400 lines suggests 80% is scaffolding. Your class outline looks right.*

*One concern: `update_web_from_result()` is new functionality, not simplification. Be careful not to add features while claiming to simplify. Do ECB-2.1 (simplify) BEFORE ECB-2.2 (add feedback loop)."*

**Pearl**: *"The method list is correct. I particularly approve of keeping `build_causal_models()` and `counterfactual()` as the primary interface. These map directly to the two fundamental causal operations:
1. Model construction (structure + parameters)
2. Query answering (intervention effects)

All other methods should be internal."*

**van Fraassen**: *"I see `_assess_contrast_transfer()` in the list. Good. This is essential. Make sure it's not cut in simplification."*

**Parnas**: *"The 'Classes to keep' list is reasonable. I would add: create a clear separation between **public API** (3-4 methods) and **private implementation** (everything else). Python's convention of `_method()` for private is sufficient, but document it."*

### Task ECB-2.2: Add Feedback Loop Method

**Haack**: *"The feedback logic captures my recommendations:
- High robustness → credence increase (coherentist move)
- Low robustness → flag for review (don't auto-revise)
- Coherence violation → revise less entrenched (Quinean principle)

One addition: the `delta` of 0.02 for credence increase seems arbitrary. Consider making it proportional to robustness score: `delta = 0.05 * robustness_score`. This respects the degree of support."*

**Cartwright**: *"I don't see enabling conditions in the feedback loop. If a counterfactual was computed despite potential enabling condition issues, the feedback should note this. Add:*
```python
if any(belief has enabling_conditions for belief in supporting):
    changes.append({
        'type': 'conditional_support',
        'belief_ids': [...],
        'note': 'Result conditional on enabling conditions being met'
    })
```
*"*

**Action Required**: Add conditional support tracking to feedback loop.

### Task ECB-2.3: Wire Bridge into Pipeline

**Brooks**: *"This is the critical integration point. Your plan adds a `_build_causal_layer()` function that's called after web integration. Good sequencing.*

*Missing: What happens if `build_causal_models()` fails? Add try/except with graceful degradation:*
```python
try:
    causal_result = _build_causal_layer(web, options)
except Exception as e:
    logger.warning(f'Causal bridge failed: {e}. Continuing without causal layer.')
    causal_result = {'causal_bridge_enabled': False, 'error': str(e)}
```
*The pipeline should never fail because an optional layer fails."*

**Parnas**: *"The `enable_causal_bridge` option is good. Default should be `True` for new behavior, but document it clearly. Also: add a `--no-causal` CLI flag for users who want to skip it."*

### Task ECB-2.4: Add Enabling Conditions to StructuralEquation

**Cartwright**: *"This is exactly what I requested. The `is_applicable()` method is the right abstraction.*

*Refinement: Instead of just returning `True/False`, return a tuple `(applicable: bool, reason: str)`. This helps debugging:*
```python
def is_applicable(self, context: Dict[str, Any]) -> Tuple[bool, str]:
    if self.enabling_conditions is None:
        return (True, 'no_conditions')
    # ... checks ...
    if blocker_present:
        return (False, f'blocked_by:{blocker}')
    return (True, 'conditions_met')
```
*"*

**Action Required**: Return reason from `is_applicable()`.

---

## Panel Review: Sprint ECB-3 (Van Fraassen + Feedback)

### Task ECB-3.1: Implement Contrast Transfer Rules

**van Fraassen**: *"The four transfer types are correct:
- DIRECT: Ideal case
- BASELINE_SHIFT: Common in cross-population comparison
- POPULATION_SHIFT: Different group, similar construct
- MEANING_SHIFT: Different construct—MUST NOT TRANSFER

The thresholds (0.9, 0.7, 0.5) seem reasonable as defaults but should be configurable. What seems like 0.7 similarity today may need adjustment after seeing real data."*

**Simon**: *"Make thresholds configurable via a config file or environment variables. Hardcoded thresholds are technical debt."*

**Action Required**: Add contrast transfer thresholds to configuration.

### Task ECB-3.2: Return Undefined for Non-Transferable Contrasts

**van Fraassen**: *"YES. This is essential. A computed but meaningless answer is worse than 'I don't know.'*

*The `is_defined=False` field is good. Also consider adding `reason_undefined: str` for clarity:*
```python
QuineanCounterfactualResult(
    ...
    is_defined=False,
    reason_undefined='contrast_mismatch:source_X_target_Y'
)
```
*"*

**Pearl**: *"From a causal inference perspective, this is correct. You cannot compute do(X) effects if the meaning of X differs between source and target. The plan handles this properly."*

### Task ECB-3.3: Route Gaps to VOI Search

**Simon**: *"Good integration. But I'm concerned about coupling. The bridge shouldn't directly depend on VOI search. Instead:
1. Bridge returns gaps in a standard format
2. Pipeline routes gaps to VOI (or anywhere else)

This keeps the bridge focused."*

**Action Required**: Bridge returns gaps; pipeline routes them. Don't import VOI in bridge.

### Task ECB-3.4: Add Haack's Security Weight

**Haack**: *"The `compute_security()` method correctly weights empirical beliefs higher than theoretical ones. This captures the foundational aspect of foundherentism—direct experience provides independent security.*

*One refinement: explicit contrast classes (from paper methods) should increase security. Add:*
```python
# Contrast class bonus
explicit_contrast_bonus = sum(
    0.1 for b in beliefs
    if hasattr(b, 'contrast_class') and b.contrast_class and b.contrast_class.explicit
)
return base_security + min(0.2, explicit_contrast_bonus)
```
*"*

---

## System Developer Review: Overall Architecture

### David Parnas

*"The plan is well-structured. Three sprints is appropriate—you're not trying to do everything at once.*

**Concerns**:

1. **Testing strategy is underspecified**. The test file outline is good, but you need:
   - Unit tests for each public method
   - Integration tests for pipeline flow
   - Contract tests for data structures

2. **Error handling is implicit**. Add explicit error handling for:
   - Empty web
   - Missing theory
   - Malformed belief
   - Null contrast class

3. **Versioning**: You're targeting V23.1.0. Make sure the version is incremented in all relevant files (`__init__.py`, `CLAUDE.md`, etc.) BEFORE merging.

**Approval**: CONDITIONAL on addressing error handling."*

### Fred Brooks

*"This is a reasonable plan for a repair operation. You're not trying to redesign the whole system—just fix the integration.*

**Concerns**:

1. **Schedule risk**: 3 sprints across 6-8 days is aggressive. Each sprint should have a checkpoint where you can stop if needed. Don't let 'progress' on ECB-2 block shipping ECB-1.

2. **The 'second system' warning**: The temptation will be to add features while refactoring. Resist this. Simplification is the goal. Features come later.

3. **Documentation debt**: You have good planning docs, but what about user-facing docs? Add a task: update `docs/ARCHITECTURE.md` after each sprint.

**Approval**: APPROVED with schedule flexibility."*

---

## Synthesis: Required Plan Updates

Based on panel + developer review, update the plan as follows:

| # | Update | Source | Priority |
|---|--------|--------|----------|
| 1 | Add header comments to archived files | Parnas | P1 |
| 2 | Check if bridge.Belief.contrast_class is used anywhere | Parnas | P1 |
| 3 | Diff external vs repo file before consolidating | Brooks, Parnas | P1 |
| 4 | Do ECB-2.1 (simplify) before ECB-2.2 (add feedback) | Simon | P1 |
| 5 | Make credence delta proportional to robustness | Haack | P2 |
| 6 | Add conditional support tracking to feedback | Cartwright | P2 |
| 7 | Add try/except to pipeline integration | Brooks | P1 |
| 8 | Add `--no-causal` CLI flag | Parnas | P2 |
| 9 | Return reason from `is_applicable()` | Cartwright | P2 |
| 10 | Make contrast thresholds configurable | Simon, van Fraassen | P2 |
| 11 | Add `reason_undefined` to undefined results | van Fraassen | P2 |
| 12 | Route gaps via pipeline, not bridge directly | Simon | P2 |
| 13 | Add explicit contrast bonus to security weight | Haack | P3 |
| 14 | Add explicit error handling | Parnas | P1 |
| 15 | Update ARCHITECTURE.md after each sprint | Brooks | P2 |

---

## Updated Sprint Structure

Based on review, revise sprint structure:

### Sprint ECB-1: Cleanup and Consolidation
- ECB-1.0: **NEW** Diff external vs repo file, document differences
- ECB-1.1: Archive features (with header comments)
- ECB-1.2: Delete duplicates (check contrast_class usage first)
- ECB-1.3: Consolidate (pick repo file, don't merge)
- ECB-1.4: Create quarantine structure
- **Checkpoint**: All tests pass, file compiles, pipeline unchanged

### Sprint ECB-2: Core Integration
- ECB-2.1: Simplify class (target <600 lines, NO new features)
- ECB-2.2: Add enabling conditions to StructuralEquation (with reason return)
- ECB-2.3: Wire into pipeline (with try/except, add CLI flag)
- ECB-2.4: Add feedback loop (with conditional tracking, proportional delta)
- **Checkpoint**: Pipeline runs with bridge, basic counterfactual works

### Sprint ECB-3: Van Fraassen and Polish
- ECB-3.1: Contrast transfer rules (configurable thresholds)
- ECB-3.2: Return undefined for non-transferable (with reason)
- ECB-3.3: Gap identification (bridge returns, pipeline routes)
- ECB-3.4: Security weight (with contrast bonus)
- ECB-3.5: **NEW** Update ARCHITECTURE.md
- ECB-3.6: **NEW** Error handling pass
- **Checkpoint**: Full test suite passes, docs updated

---

## Final Approval

| Reviewer | Verdict |
|----------|---------|
| Haack | APPROVED with refinements |
| Pearl | APPROVED |
| van Fraassen | APPROVED with refinements |
| Simon | APPROVED |
| Cartwright | APPROVED with refinements |
| Parnas | CONDITIONAL on error handling |
| Brooks | APPROVED with schedule flexibility |

**Overall**: APPROVED with 15 updates incorporated

---

*Plan review complete. Ready for TASKS.md sprint documentation.*
