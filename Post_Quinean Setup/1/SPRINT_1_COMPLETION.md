# Sprint 1 Completion Summary
## Article Eater - Extraction to Web of Belief Integration

**Date**: 2026-01-17  
**Sprint**: 1 - Core Mapper Implementation  
**Status**: ✓ COMPLETE

---

## Deliverables

### Files Created

1. **`src/services/extraction_to_web.py`** (~700 lines)
   - Core mapper from contract pipeline to web of belief
   - Claim → Belief mapping
   - Rule → Constraint mapping
   - Theory inference engine
   - Stub management
   - Tension detection
   - Integration report generation

2. **`tests/test_extraction_to_web.py`** (~350 lines)
   - Comprehensive test suite
   - 15 tests, all passing

### Capabilities Implemented

| Feature | Status | Notes |
|---------|--------|-------|
| claim_type → EpistemicLevel | ✓ | Maps all 6 claim types |
| ae.claim.v1 → Belief | ✓ | Full field mapping |
| ae.rule.v1 → Constraint | ✓ | Handles all polarities |
| Theory inference | ✓ | Outcome taxonomy + keywords |
| Stub detection | ✓ | Threshold: 0.4 relevance score |
| Anomaly detection | ✓ | Null findings → ANOMALOUS |
| Credence computation | ✓ | Incorporates statistics |
| Population scope | ✓ | Preserved in tags |
| Integration workflow | ✓ | Batch processing with reports |
| TheoryRegistry compat | ✓ | ID format compatible |

---

## Expert Panel Decision Points

The following decisions were made during implementation and should be reviewed:

### 1. Claim Type to Epistemic Level Mapping

**Decision Made**:
```
mechanistic    → THEORETICAL    (Theory-level claims)
causal         → INTERMEDIATE   (Generalizations)
associational  → EMPIRICAL      (Single-study findings)
moderated      → EMPIRICAL      (With moderator metadata)
descriptive    → OBSERVATIONAL  (Direct measurements)
null           → EMPIRICAL      (Null findings, marked ANOMALOUS)
```

**Questions for Panel**:
- Is "mechanistic" appropriately placed at THEORETICAL? Some mechanism claims are quite specific.
- Should "causal" claims with RCT design be elevated to INTERMEDIATE, or should they be EMPIRICAL?
- Is the distinction between EMPIRICAL and OBSERVATIONAL defensible for this domain?

### 2. Theory Inference Threshold

**Decision Made**:
- Relevance score ≥ 0.4 required for theory assignment
- Below threshold → mark as STUB

**Questions for Panel**:
- Is 0.4 the right threshold? Too high = many stubs; too low = forced connections
- Should the threshold vary by theory type (e.g., higher for ART than for Biophilia)?

### 3. Null Finding Treatment

**Decision Made**:
- Null findings become ANOMALOUS beliefs
- Credence reduced by 50% (evidence AGAINST an effect)
- Still integrated into web (not discarded)

**Questions for Panel**:
- Is ANOMALOUS the right status for null findings?
- Should null findings be weighted differently in coherence calculations?
- Publication bias: Should we discount positive findings instead?

### 4. Theory Inference Strategy

**Decision Made**: Three-strategy approach:
1. Outcome taxonomy mapping (primary, score 0.5-0.8)
2. Keyword matching in statement (secondary, score 0.6)
3. Environment factor matching (tertiary, score 0.4)

**Questions for Panel**:
- Is keyword matching too noisy?
- Should theory inference consider study design (e.g., neuroimaging → brain mechanisms)?
- How to handle claims that match multiple theories equally?

### 5. Constraint Type from Polarity

**Decision Made**:
```
positive  → SUPPORTS (strength × 1.0)
negative  → CONTRADICTS (strength × 1.0)
null      → INDEPENDENT (strength × 0.3)
u_shaped  → SUPPORTS (strength × 0.7)
unknown   → SUPPORTS (strength × 0.5)
```

**Questions for Panel**:
- Should u_shaped be a distinct constraint type?
- Is INDEPENDENT the right type for null polarity?
- Are the strength modifiers appropriate?

---

## Test Results

```
TestEpistemicLevelMapping:
  ✓ mechanistic→THEORETICAL
  ✓ causal→INTERMEDIATE
  ✓ associational→EMPIRICAL
  ✓ descriptive→OBSERVATIONAL
  ✓ null→EMPIRICAL

TestTheoryInference:
  ✓ attention→ART
  ✓ stress→SRT

TestClaimToBeliefMapping:
  ✓ causal_claim_maps
  ✓ null_becomes_anomalous
  ✓ orphan_becomes_stub

TestRuleToConstraintMapping:
  ✓ rule_maps_to_constraint
  ✓ negative→CONTRADICTS

TestIntegration:
  ✓ adds_beliefs_to_web
  ✓ tracks_stubs
  ✓ tracks_anomalies

Results: 15 passed, 0 failed
```

---

## Sample Output

Integration of 3 test claims:

| Claim | Type | Theory Inferred | Status |
|-------|------|-----------------|--------|
| Park → stress | causal | SRT (0.80) | TENTATIVE |
| Plants → attention (null) | null | ART (0.80) | ANOMALOUS |
| Thermal → satisfaction | associational | None | STUB |

**Integration Report**:
- Claims processed: 3, success: 3
- Stubs: 1, Anomalies: 1
- Theory distribution: {SRT: 1, ART: 1}
- Level distribution: {intermediate: 1, empirical: 2}
- Coherence: 0.416 → 0.416 (no equilibrium run)

---

## Compatibility Notes

### TheoryRegistry Compatibility

The mapper produces belief IDs and structures compatible with eventual TheoryRegistry integration:

- `belief_id` format: `{source}:{type}:{index}` (matches `prediction_id` pattern)
- Credence decomposition ready for `theory_contribution`, `derivation_contribution`, `empirical_contribution`
- `paper_ids` maps to `extraction_source`
- Population metadata ready for `applicable_populations`

### Future Sprint Readiness

**Sprint 2 (Pipeline Integration)**: 
- `integrate_extraction()` ready to be called from `app/tasks/pipeline.py`
- Output functions (`export_stubs_jsonl`, `export_tensions_jsonl`) ready

**Sprint 3 (Bridge Warrants)**:
- `applicability` field from rules preserved
- Ready to add bridge inference logic

**Sprint 4 (Outcome Taxonomy)**:
- Uses `outcome_lookup.json` structure
- Ready for temporal class extensions

---

## Next Steps

1. **Panel Review**: Address the 5 decision points above
2. **Sprint 2**: Wire mapper into `app/tasks/pipeline.py`
3. **Testing**: Process actual papers through the integrated pipeline

---

## References

- Quine, W.V.O. (1951). Two Dogmas of Empiricism. *Philosophical Review*, 60(1), 20-43.
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press.
- Boghossian, P. (1996). Analyticity Reconsidered. *Noûs*, 30(3), 360-391.
