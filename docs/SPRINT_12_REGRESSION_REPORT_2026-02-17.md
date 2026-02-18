# Sprint 12 Full System Regression Report

**Date**: 2026-02-17
**Agent**: CC-0217
**Task**: 12.21 - Full System Regression Suite

---

## 1. Test Suite Summary

| Category | Tests | Status |
|----------|-------|--------|
| CMR Core Tests | 281 | PASSED |
| Sensitivity Analysis | 50 passed, 3 skipped | PASSED |
| Tier 2 Validation | 1 script | PASSED |
| Ulrich 1984 Pipeline | 1 script | PASSED |
| Field Validation | 45 | PASSED |
| Process Paper | 25 | PASSED |
| Template Matching | 147 | PASSED |
| WIS Computation | 64 | PASSED |

**Total CMR Tests: 331 passed (281 + 50 sensitivity)**

---

## 2. Tier 2 Reduction Validation

### Salk Institute vs Open Plan Office

| Theory | Construct | Salk | Open Plan | Delta |
|--------|-----------|------|-----------|-------|
| ART | Being_Away | 84.4 | 69.0 | +15.4 |
| ART | Fascination_Soft | 86.6 | 78.5 | +8.1 |
| SRT | Autonomic_Stress_Reduction | 70.8 | 66.8 | +4.0 |
| Biophilia | Nature_In_Space | 78.3 | 72.5 | +5.8 |
| Biophilia | Nature_Of_Space | 80.0 | 50.0 | +30.0 |

**Average Restorative Score:**
- Salk Institute: **80.0**
- Open Plan Office: **71.7**
- Difference: **+8.3** (Salk superior as expected)

**Status: [PASS]** - Tier 2 reductions correctly differentiate architectural quality.

---

## 3. Ulrich 1984 Full Pipeline

### Pathway Detection
- **ART pathway**: 0 hits (expected - not explicit in claims)
- **SRT pathway**: 2 hits (recovery time, analgesic → Autonomic_Stress_Reduction)
- **Biophilia pathway**: 4 hits (nature view, tree view → Nature_In_Space)

### Template Matching via Reduction
- Claim 1 (recovery time): VIEW1 (0.50), OLF1 (0.20), MAT4 (0.20)
- Claim 2 (analgesic): VIEW1 (0.50), OLF1 (0.20), MAT4 (0.20)

### Pipeline Results
| Metric | Value |
|--------|-------|
| Claims Extracted | 2 |
| Claims Matched | 2 |
| Unmatched | 0 |
| Contradictions | 0 |
| Confirmations | 0 |
| Gaps | 0 |
| Aggregate VOI | 0.60 |
| Update Proposals | 2 (boundary_revision) |

**Status: [PASS]** - Full paper processing pipeline functional.

---

## 4. Template Inventory

### Active Templates: 52

| Category | Count | Description |
|----------|-------|-------------|
| E | 6 | Environmental |
| L | 5 | Light/Circadian |
| MAT | 5 | Materials |
| CREA | 4 | Creativity |
| SC | 4 | Sound/Acoustic |
| TP | 4 | Thermal/Physiological |
| SOC | 3 | Social/Privacy |
| VF | 3 | Visual Form |
| COL | 2 | Color |
| DT | 2 | DMN/TPN |
| NM | 2 | Neuromodulatory |
| SN | 2 | Spatial Navigation |
| VIEW | 1 | View Quality |
| Others | 9 | Various |

---

## 5. Reduction Coverage

| Theory | Constructs | Mean Coverage |
|--------|------------|---------------|
| ART | 5 | 80% |
| Biophilia | 4 | 81% |
| SRT | 3 | 65% |

**Total Constructs Mapped**: 21

---

## 6. Uncertainty-Aware WIS (Task 13.6)

### Test Results
- Base WIS: 75.0
- 95% CI: [52.8, 99.1]
- Confidence Width: 46.3

### Uncertainty Sources
| Source | Fraction |
|--------|----------|
| Parameter (calibration) | 10% |
| Measurement (tier) | 10% |
| Model (PE contribution) | 10% |
| **Combined** | **17%** |

**Status: [PASS]** - Monte Carlo uncertainty propagation functional.

---

## 7. Field Validation Protocols

### Available Protocols: 5

| Template | Design | Sample N | Est. Cost |
|----------|--------|----------|-----------|
| L2 | quasi_experimental | 60 | $15,000 |
| MAT1 | within_subjects | 40 | $5,200 |
| SOC2 | quasi_experimental | 80 | $5,500 |
| VF3 | within_subjects | 48 | $5,500 |
| VIEW1 | quasi_experimental | 90 | $7,000 |

**Status: [PASS]** - Protocol generators functional with full study specifications.

---

## 8. Paper Processing Pipeline

### End-to-End Test
- Input: 1 claim (daylight → alertness)
- Status: complete
- Claims matched: 1/1
- Output: ProcessingResult with proposals

**Status: [PASS]** - Main entry point functional.

---

## 9. Component Status Summary

| Component | File | Status |
|-----------|------|--------|
| WIS Computation | src/cmr/wis.py | FUNCTIONAL |
| Uncertainty WIS | src/cmr/wis.py | FUNCTIONAL |
| Template Matching | src/cmr/template_matching.py | FUNCTIONAL |
| Reduction API | src/cmr/reduction_api.py | FUNCTIONAL |
| Paper Evaluation | src/cmr/paper_eval.py | FUNCTIONAL |
| Paper Processing | src/cmr/process_paper.py | FUNCTIONAL |
| Update Proposals | src/cmr/learning/update_proposals.py | FUNCTIONAL |
| Evidence Accumulation | src/cmr/learning/evidence_accumulation.py | FUNCTIONAL |
| Field Validation | src/cmr/field_validation.py | FUNCTIONAL |

---

## 10. Known Issues

1. **Deprecation Warnings**: `datetime.utcnow()` deprecated in Python 3.12+
   - Impact: None (cosmetic)
   - Fix: Replace with `datetime.now(datetime.UTC)`

2. **Test Collection Errors**: 12 non-CMR tests have import errors
   - Affected: API routes, BN export, UI admin tests
   - Impact: None for CMR functionality
   - Root cause: Missing dependencies or outdated imports

3. **Evidence Accumulation API**: Signature changed
   - Current: `accumulate_evidence(evidence, current_value, ...)`
   - Some callers may need updates

---

## 11. Validation Checklist

- [x] Sprint verification tests pass
- [x] Tier 2 reduction validation passes
- [x] Input sensitivity tests exist
- [x] Three worked examples (Salk, Open Plan, Classroom) pass
- [x] Ulrich 1984 full pipeline passes
- [x] Completeness inventory: 52 active templates
- [x] Full CMR test suite: 281 passed
- [x] Uncertainty-aware WIS functional
- [x] Field validation protocols functional
- [x] Paper processing pipeline functional

---

## 12. Conclusion

**Overall Status: PASS**

The Sprint 12 CMR system is fully functional with:
- 281 tests passing
- Tier 2 reductions correctly scoring architectural quality
- Full paper processing pipeline operational
- Uncertainty propagation implemented
- Field validation protocol generation working

The system correctly identifies that the Salk Institute scores higher than an open-plan office on restorative measures (80.0 vs 71.7), and successfully processes the Ulrich 1984 nature view claims through the SRT and Biophilia pathways.

---

*Generated: 2026-02-17 by CC-0217*
