# ATLAS System Health Report — February 26, 2026

## Executive Summary

**AESHI Score: 49.0 / 100 (RED)**

The system is architecturally sound but has significant health issues that prevent it from reaching AMBER (60+) or GREEN (80+) status. The good news: the theory layer scores 85.46, the web/BN layer scores 72.00, and contract compliance is 66.31. The bad news: the pipeline subscore is 0.00 (import failures), isolated beliefs are at 49.6%, and there are 69 ceiling violations across 25 templates.

---

## Health Script Results

### 1. Ceiling Linter (`lint_bridge_ceilings.py`)

- **Templates scanned**: 208
- **Calibrated templates**: 103
- **Ceiling violations**: 69 across 25 templates

Most violations are MECHANISM chain steps at 0.65-0.70 vs ceiling 0.60. Key offenders:
- T6: CONSTITUTIVE steps at 0.80-0.85 (ceiling 0.75), EMPIRICAL_COVARIANCE at 0.70 (ceiling 0.60)
- PP_RAPID_GIST_004: 3 MECHANISM steps at 0.70 (ceiling 0.60)
- CIRCADIAN_ARCH_REGULATION_001: FUNCTIONAL steps at 0.58-0.60 (ceiling 0.50)
- VF2_VISUAL_RHYTHM_001: ANALOGICAL steps at 0.40-0.45 (ceiling 0.35)
- VIEW1 (NATURE_VIEW_CONVERGENCE_001): bridge at 0.68 (EMPIRICAL_COVARIANCE ceiling 0.60)

**Decision needed**: Clamp all to ceilings, or review per-violation with panel justification?

### 2. Web-BN Health (`check_web_bn_health.py`)

- **Web**: 4,888 beliefs, 6,899 constraints, 1,898 bridges
- **BN**: 6,340 nodes, 11,925 edges, 0 dangling, 0 cycles, 0 unresolved
- **MINIMUM VIABLE**: FAIL (2 of 12 gates failed)
  - web.constraints < 8,000 (actual: 6,899) — need ~1,100 more constraints
  - web.isolated_pct > 25% (actual: 49.6%) — nearly half of all beliefs are orphaned
- **TARGET**: FAIL (1 miss)
  - web.isolated_pct > 10% (actual: 49.6%)

The BN is healthy (no cycles, no dangling edges, 99.8% in largest component). The web has the problem: too many orphan beliefs.

### 3. Template Validation (`validate_all_templates.py`)

- **Result**: 208/208 PASSED
- All templates conform to canonical JSON schema.

### 4. Toulmin Validation (`validate_toulmin.py`)

- **Result**: 9/9 multi-I templates PASSED (33 mechanism steps)
- All justifications complete and properly formatted.

### 5. Corpus Health (`corpus_health_report.py`)

- **Templates**: 186 (with 13 molecules)
- **Papers**: 812 with 1,735 citation edges
- **Classified**: 166/186 (89%) — 20 unclassified templates
- **Sparse domains**: olfactory (2), circadian (3) — need more coverage
- **Templates with 0 references**: 42 (22.6%)
- **Templates with <3 references**: 47 (25.3%)
- **Top cited papers**: Ulrich 1984 (5,124), Kaplan 1991 (4,955)

### 6. System Health (`compute_system_health.py`)

| Area | Score | Notes |
|------|-------|-------|
| Theory | 85.46 | Strong — 18 T1 frameworks, good coverage |
| Web/BN | 72.00 | BN healthy, web has orphan problem |
| Contract | 66.31 | Mostly compliant, some gaps |
| Stability | 50.83 | Moderate — coherence acceptable |
| Pipeline | 0.00 | Import failures (environment issue, not code bug) |

Hard gate failures:
- sanity_check: FAIL (import issues in this environment)
- offline_pipeline_smoke: FAIL (missing dependencies)
- offline_pipeline_v2_smoke: FAIL (missing dependencies)
- web_bn_minimum_viable: FAIL (isolated_pct too high)
- finding_template_contracts: FAIL (persisted_ratio 0.0)
- **web_of_belief_invariants: PASS** (the core invariant checks pass)

---

## Priority Repair Actions

### P0: Critical (blocks GREEN status)

1. **Reduce isolated beliefs** — 49.6% orphaned. Target: <25% (minimum viable) or <10% (target). This requires running `scripts/safe_improve_web_health.py` or manually connecting orphaned beliefs via constraints. The most impactful single action.

2. **Clamp ceiling violations** — 69 violations across 25 templates. Use `scripts/ceiling_adjudicator.py` for panel-reviewed clamping, or `scripts/safe_improve_web_health.py` for conservative auto-clamping.

### P1: Important (blocks AMBER status)

3. **Add references to 42 zero-reference templates** — These templates lack any paper support. Either add references via the extraction pipeline, or mark as THEORETICAL_DEFAULT.

4. **Classify 20 unclassified templates** — 11% of templates lack domain classification.

5. **Increase constraint count** — Need ~1,100 more constraints to reach 8,000 minimum viable threshold.

### P2: Moderate

6. **Expand sparse domains** — olfactory (2 templates) and circadian (3) need more coverage.

7. **Fix pipeline smoke tests** — These fail due to missing runtime dependencies (not code bugs). Need proper environment setup.

---

## Recommended Execution Order for AG

```bash
# Step 1: Conservative health improvement (dry-run first)
python scripts/safe_improve_web_health.py --dry-run

# Step 2: If dry-run looks good, run for real
python scripts/safe_improve_web_health.py

# Step 3: Adjudicate ceiling violations
python scripts/ceiling_adjudicator.py

# Step 4: Re-check health
python scripts/compute_system_health.py
python scripts/check_web_bn_health.py

# Step 5: If still RED, run targeted repairs
python scripts/maintain_web.py
python scripts/maintain_bn.py
```

---

*Generated by health audit session, February 26, 2026*
