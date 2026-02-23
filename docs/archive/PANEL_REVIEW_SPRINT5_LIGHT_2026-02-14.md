# Light Panel Review: Sprint 5 Integration Testing
## February 14, 2026

**Scope**: Test corpus adequacy and integration test coverage
**Focus**: Are the tests sufficient to validate Epistemic Tier 2?

---

## 1. Ulrich Test Corpus Assessment

### 1.1 Corpus Overview

| Metric | Value | Assessment |
|--------|-------|------------|
| Total claims | 20 | Adequate for unit testing; light for stress testing |
| Based on | Ulrich (1984) nature-view study | Good anchor — well-known, methodologically interesting |
| Synthetic | Yes | Appropriate for controlled testing |

### 1.2 Coverage Analysis

#### Claim Types
| Type | Count | Target | Status |
|------|-------|--------|--------|
| FUNCTIONAL_EFFECT (Type B) | 16 | — | **Heavy** |
| EVALUATIVE_RESPONSE (Type A) | 4 | — | Light |

**Finding**: Type B claims dominate (80%). This reflects CNFA literature reality but means Type A validation is thin.

#### Pathways
| Pathway | Count | Claims |
|---------|-------|--------|
| mixed | 10 | ulrich_001, ulrich_002, replicate_001, fail_001, samelab_001, samelab_003, vr_study_001, meta_001, high_quality_001 |
| personal_epistemic | 7 | mechanism_002, samelab_002, samelab_004, preference_001, photo_wayfinding_001, preference_type_a_001, spatial_legibility_001 |
| subpersonal | 3 | mechanism_001, mechanism_003, unknown_method_001 |

**Finding**: Mixed pathway dominates. Subpersonal is under-represented (15%).

#### Study Designs
| Design | Count |
|--------|-------|
| quasi_experimental | 6 |
| rct | 6 |
| correlational | 6 |
| meta_analysis | 1 |
| unknown | 1 |

**Finding**: Good balance across experimental hierarchy.

#### Presentation Modalities
| Modality | Count |
|----------|-------|
| real_building_controlled | 12 |
| photographs_2d | 4 |
| vr_cave | 1 |
| vr_hmd_room_scale | 1 |
| null (meta-analysis) | 1 |

**Finding**: Real building dominates. VR modalities under-represented (only 2/20).

### 1.3 Planted Test Cases

| Test Target | Planted Case | Count | Detection |
|-------------|--------------|-------|-----------|
| Same-lab bias | Kellert Lab cluster | 4 claims | ✓ Detected |
| High vs. low quality | high_quality_001 vs low_quality_001 | 2 claims | ✓ Detected |
| Photo-wayfinding mismatch | photo_wayfinding_001 | 1 claim | ✓ Detected |
| Unknown method | unknown_method_001 (alpha-amylase) | 1 claim | ✓ Flagged |
| Failed replication | fail_001 | 1 claim | Present |

**Finding**: Key test cases are planted and detected.

### 1.4 Corpus Gaps

| Gap | Impact | Priority |
|-----|--------|----------|
| No VR HMD stationary claims | Can't test cybersickness confound detection | Medium |
| Only 1 failed replication | Weak test of conflict detection | Medium |
| No claims with temporal misalignment explicitly marked | Relies on methods text inference | Low |
| No multi-study papers | Can't test claim aggregation | Low |

---

## 2. Integration Test Coverage Assessment

### 2.1 Test Matrix

| Sprint | Component | Test Coverage | Tests |
|--------|-----------|---------------|-------|
| 1 | Schema/Templates | Imported only | test_extraction_modules_import |
| 2 | BN Nodes/Edges | Not explicitly tested | — |
| 3 | Monitors | Not explicitly tested | — |
| 4 | Extraction Pipeline | ✓ Full | test_process_single_claim, test_process_all_claims |
| 4b | Method Registry | ✓ Full | Multiple tests |
| 4b | Task Ecology | ✓ Full | Multiple tests |
| 4b | Validity Scoring | ✓ Full | Multiple tests |

**Finding**: Sprints 2-3 (BN nodes, monitors) have no explicit integration tests in Sprint 5.

### 2.2 Coverage by Task

| Task | Tests | Status |
|------|-------|--------|
| 5.1 Corpus validation | 4 tests | ✓ Complete |
| 5.2 E2E pipeline | 4 tests | ✓ Complete |
| 5.3 Three-pathway | 4 tests | ✓ Complete |
| 5.4 Bias detection | 2 tests | ✓ Complete |
| 5.5 Source quality ordering | 2 tests | ✓ Complete |
| 5.6 Full integration | 2 tests | ✓ Complete |
| 5.6b Claim bifurcation | 4 tests | ✓ Complete |
| 5.7 Auto-challenges | 3 tests | ✓ Complete |
| 5.8 Method flagging | 2 tests | ✓ Complete |

**Total**: 27 integration tests (28 including fixture).

### 2.3 Coverage Gaps

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| BN coherence computation not tested in Sprint 5 | Medium | Add test using bn_coherence_client |
| Monitor algorithms (concentration, unfalsifiability) not integrated | Medium | Deferred — monitors are Sprint 3 unit-tested |
| Bridge warrant generation not tested | Low | Part of extraction, implicitly covered |
| Web persistence not tested | Low | Infrastructure, not epistemic |
| VR cybersickness confound detection weak | Low | Add VR-specific claim to corpus |

---

## 3. Panel Decisions

### D-S5.1: Corpus Size Adequacy

**Question**: Is 20 claims sufficient?

**Decision**: **ADEQUATE FOR VALIDATION, INSUFFICIENT FOR STRESS TESTING**

Rationale:
- 20 claims test all major code paths
- Planted cases exercise specific detection logic
- For production stress testing, would need 100+ claims with realistic noise

**Action**: None required. Note limitation in documentation.

---

### D-S5.2: Type A Claim Under-representation

**Question**: Only 4 evaluative_response claims (20%). Is this a gap?

**Decision**: **ACCEPTABLE**

Rationale:
- Reflects actual CNFA literature distribution
- Type A claims have simpler validity requirements (photos ARE valid for preference)
- Key bifurcation test exists: test_claim_type_classifier, test_generalizability_weight_by_modality

**Action**: None required.

---

### D-S5.3: VR Modality Under-representation

**Question**: Only 2 VR claims (10%). Missing cybersickness confound testing?

**Decision**: **MINOR GAP — DEFER**

Rationale:
- VR confound detection is implemented in method_identifier.py
- Unit tests cover the detection logic
- Integration test gap is real but low priority

**Action**: Add note to TASKS.md for future corpus expansion.

---

### D-S5.4: Sprint 2-3 Integration Gap

**Question**: BN nodes/edges and monitors not explicitly tested in Sprint 5.

**Decision**: **ACCEPTABLE**

Rationale:
- Sprint 2-3 have comprehensive unit tests (test_sprint2.py, test_sprint3.py)
- BN coherence client exists but depends on external service
- Integration would require mock BN or live BN server
- Risk is low given unit test coverage

**Action**: None required. Document as future enhancement if BN integration becomes critical path.

---

### D-S5.5: Subpersonal Pathway Under-representation

**Question**: Only 3 subpersonal claims (15%). Adequate?

**Decision**: **ACCEPTABLE**

Rationale:
- Subpersonal is inherently less common in CNFA (most effects are mixed or personal)
- Three claims test the classification logic
- Keywords for subpersonal (circadian, cortisol, physiological) are well-covered

**Action**: None required.

---

## 4. Summary

### Strengths
1. All Sprint 5 tasks have dedicated tests (27 total)
2. Planted test cases exercise bias detection, quality ordering, challenge generation
3. Corpus covers all major study designs and claim types
4. Pipeline tests verify end-to-end processing without errors

### Acceptable Gaps
1. Corpus size (20) is validation-grade, not stress-grade
2. Type A claims light but sufficient
3. VR modalities light but unit-tested elsewhere
4. Sprint 2-3 integration implicit via unit tests

### No Critical Gaps Identified

**Panel Verdict**: Sprint 5 integration testing is **ADEQUATE** for validating Epistemic Tier 2 implementation.

---

## 5. Appendix: Test Corpus Claim Distribution

```
Claim Types:
  functional_effect:    ████████████████ 16
  evaluative_response:  ████ 4

Pathways:
  mixed:                ██████████ 10
  personal_epistemic:   ███████ 7
  subpersonal:          ███ 3

Study Designs:
  rct:                  ██████ 6
  quasi_experimental:   ██████ 6
  correlational:        ██████ 6
  meta_analysis:        █ 1

Modalities:
  real_building:        ████████████ 12
  photographs_2d:       ████ 4
  vr_cave:              █ 1
  vr_hmd_room_scale:    █ 1
```

---

*Panel review completed February 14, 2026*
