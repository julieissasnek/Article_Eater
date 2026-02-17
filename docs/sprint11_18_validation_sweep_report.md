# Sprint 11.18 Paper Eval Validation Sweep

Generated: 2026-02-17T18:04:36.810838+00:00

## Scenario Results
### ulrich_1984_proxy
- claims extracted: 3
- claims matched: 3
- claims unmatched: 0
- matched templates (4): MAT4, SOC1, SOC2, VIEW1
- aggregate VOI: 0.6
- expected information gain: medium

### contradicting_study
- claims extracted: 2
- claims matched: 2
- claims unmatched: 0
- matched templates (4): CREA1, CREA2, CREA4, VF3
- aggregate VOI: 0.7
- expected information gain: medium

### novel_gap_study
- claims extracted: 2
- claims matched: 0
- claims unmatched: 2
- matched templates (0): none
- aggregate VOI: 0.6
- expected information gain: medium

## Coverage
- total claims: 7
- matched claims: 5 (71.4%)
- assessed claims: 7 (100.0%)
- unique matched templates: 8
- template IDs: CREA1, CREA2, CREA4, MAT4, SOC1, SOC2, VF3, VIEW1
- category counts: {"confirmation": 0, "extension": 3, "contradiction": 2, "gap": 2}

## Full Test Suite
- status: pass
- summary: 3282 passed, 14 skipped, 9 warnings

## Readiness Assessment
- Paper eval pipeline is operational for confirmation, contradiction, and gap detection.
- Coverage remains bounded by ontology breadth (unmatched claims still surface as explicit gaps).
- Current state is suitable for continued expansion with additional claim libraries (Task 11.19).
