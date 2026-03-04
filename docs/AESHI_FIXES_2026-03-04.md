# AESHI Fixes and Comprehensiveness Audit — 2026-03-04

**Session**: Pipeline execution + AESHI investigation + fixes
**AESHI Before**: 50 (capped due to wrong DB) → 65 (correct DB) → **70 (after fixes)**

---

## Problem Diagnosis

### Root Cause 1: Wrong Database Reference
The initial AESHI check pointed at `web_of_belief.db` (20 KB, empty) instead of `web_persistence.db` (89 MB, 4,888 beliefs). This caused:
- Pipeline utilization: 0% (triggering hard cap at 50)
- All belief-dependent metrics: 0

### Root Cause 2: Schema Mismatch in SQL Queries
Two methods queried `belief_versions` table (0 rows) instead of `beliefs` table (4,888 rows):
- `_count_total_beliefs()` → returned 0
- `_count_orphan_beliefs()` → returned 0

### Root Cause 3: Template Coverage Logic
The metric looked for `belief_id LIKE 'template:%'` but actual belief IDs use format `disc:doi:...`. The `template_ids` column exists but is unpopulated.

---

## Fixes Applied

### Fix 1: `_count_total_beliefs()` (overseer.py:1653-1662)
```python
# BEFORE: queried empty table
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM belief_versions")

# AFTER: queries actual beliefs table
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM beliefs")
```

### Fix 2: `_count_orphan_beliefs()` (overseer.py:1664-1676)
```python
# BEFORE: queried empty table
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM belief_versions WHERE theory_id IS NULL")

# AFTER: queries actual beliefs table
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM beliefs WHERE theory_id IS NULL")
```

### Fix 3: `_check_template_belief_coverage()` (overseer.py:945-964)
```python
# BEFORE: looked for belief_id prefix
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM beliefs WHERE belief_id LIKE 'template:%'")

# AFTER: checks template_ids column
cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM beliefs WHERE template_ids IS NOT NULL AND template_ids != ''")
```

### Fix 4: Added AESHI Comprehensiveness Meta-Check
New methods added to `overseer.py`:
- `_check_test_pass_rate()` — INV-11: reads test results
- `audit_aeshi_comprehensiveness()` — reports measured vs recommended metrics

---

## AESHI Comprehensiveness Audit

**Currently Measured (9 metrics):**
1. provenance_coverage — Quality: source tracking
2. global_coherence — Quality: belief consistency
3. conflict_rate — Quality: contradiction detection
4. schema_compliance — Quality: data validation
5. credence_bounds — Quality: probability bounds
6. pipeline_utilization — Coverage: extraction→integration
7. template_coverage — Coverage: template→belief linkage
8. theory_linkage — Coverage: theory→belief linkage
9. evidence_diversity — Coverage: paper vs template sources

**Recommended Additions (8 metrics):**
1. test_pass_rate — Quality: automated test health (6,500+ tests)
2. subsystem_health — Quality: per-subsystem operational status
3. success_condition_coverage — Quality: SC test coverage (389 SC tests)
4. extraction_quality — Quality: field-level extraction accuracy
5. bn_calibration — Quality: Bayesian network correctness
6. reflex_health — Quality: reflexive monitoring operational
7. annotation_integration — Coverage: user annotations→beliefs
8. interpretation_space — Coverage: R₁-R₄ closure operators

**Comprehensiveness**: 52.9% (9/17 recommended metrics)

---

## Current AESHI Breakdown

| Metric | Value | Points | Status |
|--------|-------|--------|--------|
| Pipeline Utilization | 4.60 (460%) | 15/15 | ✅ |
| Evidence Diversity | 1.00 (100%) | 5/5 | ✅ |
| Theory Linkage | 0.48 (52% linked) | 5.2/10 | ⚠️ |
| Template Coverage | 0.00 | 0/10 | ❌ Needs data |
| Provenance | 1.00 | 15/15 | ✅ |
| Conflict Rate | 0.00 | 10/10 | ✅ |
| **TOTAL** | | **70/100** | |

---

## Remaining Work

1. **Populate template_ids column** — Link 4,888 beliefs to their corresponding templates
2. **Improve theory linkage** — 2,583 orphan beliefs need theory_id assignment
3. **Integrate test pass rate** — Wire pytest results into AESHI formula
4. **Add subsystem health checks** — Per-service operational monitoring

---

## Justification

The AESHI fixes were necessary because:

1. **Data visibility**: OVERSEER was blind to 89 MB of actual system state
2. **Metric accuracy**: Three core metrics returned incorrect values
3. **Comprehensiveness**: AESHI measured only 52.9% of recommended health indicators
4. **Actionability**: False zeros masked real issues (template linkage, theory orphans)

The meta-check (`audit_aeshi_comprehensiveness()`) ensures future development doesn't expand the system without corresponding health monitoring.
