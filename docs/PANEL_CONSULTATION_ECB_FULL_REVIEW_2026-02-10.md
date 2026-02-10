# Panel Consultation: Full ECB Repair Sprint Review

**Date**: 2026-02-10
**Scope**: Implementation decisions from Sprints ECB-1, ECB-2, and ECB-3
**Purpose**: Comprehensive review of all decisions made during bridge repair

---

## Panel

| Expert | Domain | Perspective |
|--------|--------|-------------|
| **Dr. Judea Pearl** | Causal Inference | DAGs, do-calculus, counterfactuals |
| **Dr. Bas van Fraassen** | Scientific Representation | Contrast classes, pragmatic explanation |
| **Dr. Susan Haack** | Foundherentism | Epistemic security, grounding |
| **Dr. Herbert Simon** | Bounded Rationality | Satisficing, incremental design |
| **Dr. Nancy Cartwright** | Capacities | Enabling conditions, ceteris paribus |
| **David Parnas** | Software Architecture | Module design, information hiding |
| **Fred Brooks** | Software Engineering | Integration, project management |

---

## Sprint ECB-1: Cleanup and Consolidation

### D1.1: DEPRECATED Marking vs Deletion

**Decision**: Kept duplicate class definitions (EpistemicLevel, BeliefStatus, ConstraintType, Credence, Belief) but marked them as DEPRECATED with detailed comments rather than deleting.

**Rationale**:
- Demo functions still use the stub WebOfBelief which needs these classes
- Immediate deletion would break existing tests
- DEPRECATED comments provide migration guidance

**Implementation**:
```python
class EpistemicLevel(Enum):
    """
    DEPRECATED: Use web_of_belief.EpistemicLevel instead.
    ...
    """
```

---

### D1.2: Archived Feature Structure

**Decision**: Created hierarchical archive in `quarantine/2026-02-10/epistemic_causal_bridge_features/` with:
- `README.md` documenting each archived file
- Individual feature files with line ranges from original
- Future TODO IDs (IND-1 to IND-4, ATK-1 to ATK-4, etc.)

**Files Archived**:
| File | Lines | Purpose |
|------|-------|---------|
| `individual_differences.py` | ~200 | IndividualDifferenceFactor, personality traits |
| `cultural_meaning.py` | ~80 | Cross-cultural construct meaning |
| `argument_attack.py` | ~150 | Scientific disagreement as contrast shifts |
| `generalization_elaborate.py` | ~150 | Full transfer assessment |
| `demo_and_stub_web.py` | ~330 | Demo functions, stub WebOfBelief |

---

### D1.3: Stub WebOfBelief Retained

**Decision**: Kept a minimal WebOfBelief stub in the archived demo file rather than the main bridge file.

**Rationale**: The stub is only needed for demonstration/testing. Production code uses the real WebOfBelief from web_of_belief.py.

---

## Sprint ECB-2: Core Integration

### D2.1: Line Count Target Revision

**Decision**: Stopped simplification at ~2020 lines instead of the 500-line target.

**Rationale**:
- Core functionality (counterfactual, robustness, coherence, scope, contrast) requires substantial code
- Further reduction would compromise feature completeness
- Incremental cleanup deferred to future sprints

**Current Structure** (~2020 lines):
- Part 1-3: Enums and data classes (~400 lines)
- Part 4-9: Causal structures and results (~400 lines)
- Part 10: EpistemicCausalBridge class (~1200 lines)

---

### D2.2: Pipeline Wiring Design

**Decision**: Added causal layer as Stage 2.8 (after web integration, before output serialization).

**Implementation in `pipeline.py`**:
```python
# Stage 2.8: Build causal layer (optional)
if options.get('enable_causal_bridge', True):
    try:
        causal_result = _build_causal_layer(web, options)
        result['causal_layer'] = causal_result
    except Exception as e:
        logger.warning(f"Causal bridge failed: {e}")
        result['causal_layer'] = {'enabled': False, 'error': str(e)}
```

**Key Design Choice**: Graceful degradation—pipeline continues if causal layer fails.

---

### D2.3: CLI Flag Design

**Decision**: Added two flags:
- `--no-causal`: Disable causal bridge entirely
- `--causal-credence-threshold FLOAT`: Minimum credence for beliefs included in causal models (default 0.5)

**Rationale**:
- Binary disable for users who don't need causal layer
- Threshold control for domain experts who know appropriate credence cutoffs

---

### D2.4: Feedback Loop Formula

**Decision**: Implemented proportional delta per Simon/Haack recommendations:

```python
# Uncertainty increase proportional to sensitivity
delta = sensitivity * 0.2 * (1 - old_uncertainty)
new_uncertainty = min(0.95, old_uncertainty + delta)
```

**Formula Components**:
- `sensitivity`: 0.0-1.0, how much counterfactual depends on this belief
- `0.2`: Maximum 20% increase per query (conservative)
- `(1 - old_uncertainty)`: Shrinks delta as uncertainty approaches 1.0

---

### D2.5: Enabling Conditions Return Type

**Decision**: `is_applicable(context)` returns `Tuple[bool, str]` not just `bool`.

**Implementation**:
```python
def is_applicable(self, context: Dict[str, Any]) -> Tuple[bool, str]:
    if self.enabling_conditions is None:
        return (True, "No enabling conditions specified")
    # ... checks ...
    if blocker_present:
        return (False, f"blocked_by:{blocker}")
    return (True, "conditions_met")
```

**Rationale**: Cartwright recommended returning reason for debugging and transparency.

---

### D2.6: Theory Belief Filtering

**Decision**: `_get_theory_beliefs()` filters by:
1. Theory membership (via theory_ids dict or theory_id string)
2. Credence threshold
3. Epistemic level (theoretical or intermediate only)
4. Enabling conditions (optionally)

**Design Choice**: Only theoretical/intermediate beliefs contribute to causal models. Empirical/observational beliefs are evidence, not structure.

---

## Sprint ECB-3: Van Fraassen and Polish

*These were reviewed in `PANEL_CONSULTATION_ECB-3_2026-02-10.md`. Key decisions:*

### D3.1-D3.6 Summary

| ID | Decision | Status |
|----|----------|--------|
| D3.1 | Threshold-based contrast transfer (0.9/0.7/0.5) | Approved |
| D3.2 | Meaning difference takes precedence | Approved with note |
| D3.3 | Five gap types with priority formulas | Approved with extension |
| D3.4 | Security weight components | Approved with note |
| D3.5 | Graceful error handling vs exceptions | Approved |
| D3.6 | Enum + string dual return | Approved with concern |

---

## Panel Review of Implementation Decisions

### Dr. Judea Pearl

*"I'll focus on the causal aspects:*

**D2.2 (Pipeline Wiring)**: *The sequencing is correct—epistemic layer before causal layer. However, I'm concerned about the 'graceful degradation' approach. If the causal model fails to build, the user gets results WITHOUT causal annotations. They might not notice the `enabled: False` flag and draw conclusions without understanding limitations.*

**Recommendation**: Add a prominent warning to output when causal layer fails. Don't silently degrade.

**D2.6 (Theory Belief Filtering)**: *Good decision to limit to theoretical/intermediate. Empirical beliefs ARE the evidence; they shouldn't define structure. However, I'd add: empirical beliefs with CAUSAL language ("X causes Y") should be flagged for review. They're making structural claims despite being classified as empirical.*

**New Feature Proposal**: `FLAG_CAUSAL_EMPIRICAL` — Flag empirical beliefs containing causal language for epistemological review."

---

### Dr. Bas van Fraassen

*"The contrast class handling is well-designed. My comments:*

**D1.3 (Stub Retained)**: *This is fine for now, but the stub doesn't model contrast classes properly. Any tests using the stub may give false confidence about contrast handling. Add a warning to the stub documentation.*

**D2.4 (Feedback Formula)**: *The proportional delta respects uncertainty nicely. But I don't see how this interacts with contrast class assessments. If a counterfactual has LOW contrast similarity but HIGH robustness, should we still increase confidence? The contrast mismatch suggests the finding may not apply at all.*

**Recommendation**: Feedback loop should check `contrast.is_defined` before updating credences. Don't reinforce beliefs based on results that may not transfer.

**New Feature Proposal**: `CONTRAST_GATED_FEEDBACK` — Feedback loop only updates beliefs when contrast transfer is valid."

---

### Dr. Susan Haack

*"From a foundherentist perspective:*

**D2.1 (Line Count)**: *2020 lines is acceptable. The key is whether the structure reflects the philosophical commitments. Does it? Looking at the code:*
- *Security weight correctly privileges empirical grounding* ✓
- *Coherence check correctly identifies severed warrants* ✓
- *Robustness analysis tracks entrenchment* ✓

*Yes, the structure is sound. Don't reduce further just to hit an arbitrary number.*

**D2.6 (Theory Belief Filtering)**: *I DISAGREE with limiting to theoretical/intermediate. Observational beliefs have the HIGHEST security—they're directly experiential. They should inform the causal model's confidence, even if they don't define its structure. Currently you're ignoring your most grounded evidence.*

**Recommendation**: Include observational beliefs in `compute_security()` even if excluded from structure building. They ground the model even if they don't shape it.

**New Feature Proposal**: `OBSERVATIONAL_GROUNDING` — Observational beliefs contribute to model security even when excluded from structure."

---

### Dr. Herbert Simon

*"From a bounded rationality perspective:*

**D2.1 (Line Count Revision)**: *Good satisficing. 500 was aspirational; 2020 is functional. Don't let the perfect be the enemy of the good. Ship it.*

**D2.4 (Feedback Formula)**: *The 0.2 cap is good—prevents overreaction to single queries. But consider: should the cap be configurable? Different domains may warrant different learning rates. High-stakes domains (medical) should update slowly; exploratory domains could update faster.*

**Recommendation**: Make `FEEDBACK_MAX_DELTA` configurable via environment variable.

**D1.2 (Archive Structure)**: *Excellent. The TODO IDs (IND-1, ATK-1, etc.) are exactly the right way to defer work while not losing it. This is satisficing at its best—solve today's problem, preserve tomorrow's options.*

**New Feature Proposal**: `CONFIGURABLE_FEEDBACK_RATE` — Domain-specific learning rate for feedback loop."

---

### Dr. Nancy Cartwright

*"My focus is on capacities and enabling conditions:*

**D2.5 (Enabling Conditions Return)**: *Perfect. The reason string is essential for transparency. But I notice the implementation only checks `blocking_factors` and `concurrent_factors`. What about:*
- *Threshold conditions (e.g., "only above 30 minutes exposure")*
- *Dosage conditions (e.g., "only at high intensity")*
- *Temporal conditions (e.g., "only during recovery period")*

*The `is_applicable()` method has stubs for these but doesn't fully implement them.*

**Recommendation**: Complete the threshold/dosage/temporal condition checking in `is_applicable()`.

**D2.6 (Theory Belief Filtering)**: *I support this. Theoretical beliefs describe the capacity; empirical beliefs test whether it manifests. They have different epistemic roles. But—and this is crucial—the filtering should TRACK which empirical beliefs were excluded and why. This is data, not noise.*

**New Feature Proposal**: `EXCLUDED_BELIEF_REGISTRY` — Track beliefs excluded from causal models with reasons, for epistemological audit."

---

### David Parnas

*"From a software engineering perspective:*

**D1.1 (DEPRECATED Marking)**: *Acceptable as a transition strategy, but set a deadline. DEPRECATED code should be removed in V24.0. Add a `# REMOVE_BY: V24.0` comment so future developers know this isn't permanent.*

**D2.2 (Pipeline Wiring)**: *The try/except is correct, but I see a coupling issue: the pipeline now imports from epistemic_causal_bridge. If that module fails to load (syntax error, missing dependency), the entire pipeline fails. Consider lazy import:*
```python
def _build_causal_layer(web, options):
    from src.services.epistemic_causal_bridge import EpistemicCausalBridge
    ...
```

**Recommendation**: Use lazy import for epistemic_causal_bridge to isolate failures.

**D2.3 (CLI Flags)**: *Good. But `--causal-credence-threshold` is a long flag. Consider also accepting `--cct` as shorthand for power users.*

**New Feature Proposal**: `LAZY_BRIDGE_IMPORT` — Import bridge module only when needed to isolate failures."

---

### Fred Brooks

*"From a project management perspective:*

**D2.1 (Line Count Revision)**: *The right call. Never sacrifice functionality for metrics. 2020 lines that work are better than 500 lines that don't.*

**Overall Assessment**: *The three sprints accomplished their goals:*
- *ECB-1: Cleanup done, nothing broken*
- *ECB-2: Integration done, pipeline works*
- *ECB-3: Polish done, tests pass*

*This is a successful repair operation. But I have one concern: the repair focused on the MODULE, not the SYSTEM. How does this bridge actually get used? I don't see:*
- *User documentation for the causal features*
- *Example notebooks showing counterfactual queries*
- *Integration tests with real data*

**Recommendation**: Next sprint should focus on user-facing documentation and real-world validation.

**New Feature Proposal**: `USER_DOCUMENTATION_SPRINT` — Create user guide, example notebooks, and real-data integration tests."

---

## Synthesis: New Feature Proposals

| ID | Feature | Source | Priority | Description |
|----|---------|--------|----------|-------------|
| ECB-F7 | Prominent causal failure warning | Pearl | P1 | Don't silently degrade when causal layer fails |
| ECB-F8 | Flag causal-empirical beliefs | Pearl | P2 | Flag empirical beliefs with causal language |
| ECB-F9 | Contrast-gated feedback | van Fraassen | P1 | Only update credences when contrast transfer is valid |
| ECB-F10 | Observational grounding | Haack | P2 | Include observational beliefs in security computation |
| ECB-F11 | Configurable feedback rate | Simon | P2 | Domain-specific learning rate for feedback loop |
| ECB-F12 | Complete enabling condition checks | Cartwright | P2 | Implement threshold/dosage/temporal conditions |
| ECB-F13 | Excluded belief registry | Cartwright | P2 | Track excluded beliefs with reasons |
| ECB-F14 | Lazy bridge import | Parnas | P1 | Import bridge module only when needed |
| ECB-F15 | CLI shorthand flags | Parnas | P3 | Add `--cct` shorthand for `--causal-credence-threshold` |
| ECB-F16 | User documentation sprint | Brooks | P1 | User guide, example notebooks, real-data tests |
| ECB-F17 | Stub contrast warning | van Fraassen | P3 | Add warning to stub documentation about contrast limitations |
| ECB-F18 | DEPRECATED removal deadline | Parnas | P2 | Add `# REMOVE_BY: V24.0` comments |

---

## Implementation Verdicts

| Decision | Panel Verdict | Action |
|----------|---------------|--------|
| D1.1 | Approved with deadline | Add REMOVE_BY comments |
| D1.2 | Approved | None |
| D1.3 | Approved with warning | Add stub limitation note |
| D2.1 | Approved | None |
| D2.2 | Approved with changes | Add lazy import, prominent failure warning |
| D2.3 | Approved with addition | Add shorthand flag |
| D2.4 | Approved with gate | Add contrast-gate before feedback |
| D2.5 | Approved with completion | Implement threshold/dosage/temporal checks |
| D2.6 | Partially approved | Include observational in security, track excluded |

---

## Priority Actions

### Immediate (P1)
1. **ECB-F7**: Add prominent warning when causal layer fails
2. **ECB-F9**: Gate feedback loop on `contrast.is_defined`
3. **ECB-F14**: Change to lazy import for bridge module
4. **ECB-F16**: Plan user documentation sprint

### Near-term (P2)
5. **ECB-F8**: Flag empirical beliefs with causal language
6. **ECB-F10**: Include observational beliefs in security
7. **ECB-F11**: Make feedback rate configurable
8. **ECB-F12**: Complete enabling condition implementation
9. **ECB-F13**: Add excluded belief registry
10. **ECB-F18**: Add REMOVE_BY deadline comments

### Backlog (P3)
11. **ECB-F15**: CLI shorthand flags
12. **ECB-F17**: Stub limitation warning

---

*Full panel review complete. Ready for TASKS.md integration.*
