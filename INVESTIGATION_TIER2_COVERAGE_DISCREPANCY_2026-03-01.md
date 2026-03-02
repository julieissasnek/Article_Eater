# INVESTIGATION: Tier2 Coverage Discrepancy (23.6% vs 86.9%)

**Date**: 2026-03-01
**Investigator**: Claude Code
**Status**: CRITICAL FINDING IDENTIFIED

---

## Executive Summary

The AESHI system reports **Tier2 coverage at 23.6% (807/3,420 findings)**, capping the overall score at 49/100. However, AG reported achieving **86.9% Tier2 coverage (22,031/25,355 findings)** in recent work. Investigation reveals:

1. **Root cause**: A high-quality tier2 annotation file (`finding_template_theory_links_fixed.json`) exists but is not being used by AESHI measurement.
2. **The fixed file**: Contains 86.4% tier2 coverage (2,929/3,420 beliefs), matching AG's reported quality.
3. **Data gap**: 2,244 beliefs have tier2 annotations in the fixed file but NOT in the current file being measured.
4. **Status**: The fixed file was generated as part of AG's recent work but has not been integrated into the production measurement pipeline.

---

## Detailed Findings

### 1. Database Inventory

All web_persistence databases in the system:

| Database | Beliefs | With epistemic_v2 | Notes |
|----------|---------|-------------------|-------|
| web_persistence.db | 4,888 | 0 | Legacy, no annotations |
| web_persistence_v2.db | 3,420 | 3,420 | **Active**, fully annotated |
| web_persistence_LOCKED.db | 4,888 | 4,888 | Full but different schema |
| web_persistence_v2.codex_*.db | 382 each | 0 | Variant experimental DBs |

**Current system DB**: `data/web_persistence_v2.db` (3,420 beliefs, all with template_relevance_v1 annotations)

### 2. Tier2 Coverage in Different Link Files

| File | Total Findings | With tier2_relevance | Coverage | File Size | Modified |
|------|----------------|----------------------|----------|-----------|----------|
| **finding_template_theory_links.json** (CURRENT) | 3,420 | 807 | **23.6%** | 3.2 MB | 2026-03-01 02:33 |
| **finding_template_theory_links_fixed.json** (HIGH-QUALITY) | 3,420 | 2,929 | **85.6%** | 5.2 MB | 2026-03-01 02:05 |
| finding_template_theory_links_patched.json | 4,888 | 768 | 15.7% | 2.7 MB | 2026-03-01 02:08 |
| finding_template_theory_links_persisted.json | 4,888 | 768 | 15.7% | 2.7 MB | 2026-03-01 06:28 |

**Key observation**: The `_fixed` file has **2.6× higher coverage** (85.6% vs 23.6%) despite containing the same 3,420 beliefs.

### 3. Content Comparison: Current vs Fixed

Comparing belief-by-belief (all 3,420 are common):

- **Beliefs with different tier2 status**: 2,244 (65.6% of the dataset)
- **Current has tier2, fixed doesn't**: ~14 (negligible)
- **Fixed has tier2, current doesn't**: ~2,230 (massive gap)

### 4. Evidence: Concrete Examples

#### Example 1: `template:ARCH_PROMENADE_TEMPORAL_PE_001`

**Current file**:
- tier2_relevance: `{}` (empty)

**Fixed file**:
- tier2_relevance:
  ```json
  {
    "PREDICTIVE_PROCESSING": 0.7774,
    "ADAPTIVE_THERMAL_COMFORT": 0.3955,
    "ALLOSTATIC_REGULATION": 0.3955,
    "IC": 0.3955,
    "INTEROCEPTION": 0.3955,
    "METABOLIC_HEALTH": 0.3955,
    "CHRONOBIOLOGICAL": 0.2855,
    "NEUROMODULATORY": 0.2855
  }
  ```
- top_templates: `[{THERMAL_ADAPTIVE_PE_001: 0.7909}, {IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001: 0.7909}]`

#### Example 2: `template:ED_RECONSOLIDATION_001`

**Current file**:
- tier2_relevance: `{}` (empty)

**Fixed file**:
- tier2_relevance: Multiple frameworks with scores (SPATIAL_NAVIGATION: 0.6388, etc.)
- top_templates: COLLABORATIVE_CREATIVITY_ARCHITECTURE_001 (0.83), OLFACTORY_PE_TRANSITION_001 (0.83)

### 5. File Generation Timeline

```
2026-03-01 02:05 → finding_template_theory_links_fixed.json (5.2 MB, 86.4% tier2)
2026-03-01 02:08 → finding_template_theory_links_patched.json (2.7 MB, 15.7% tier2)
2026-03-01 02:33 → finding_template_theory_links.json (3.2 MB, 23.6% tier2) ← CURRENT
2026-03-01 06:28 → finding_template_theory_links_persisted.json (2.7 MB, 15.7% tier2)
```

The `_fixed` file was created **28 minutes BEFORE** the current file but contains significantly better annotations.

### 6. AESHI Measurement Code Path

From `scripts/compute_system_health.py` (lines 366-421):

```python
def compute_finding_contract(...):
    links = load_json(links_json)  # ← loads finding_template_theory_links.json
    resolutions = links.get("resolutions", [])
    findings_with_tier2 = sum(1 for r in resolutions if r.get("tier2_relevance"))
    tier2_coverage = (findings_with_tier2 / findings_total) if findings_total else 0.0

    failures: list[str] = []
    if tier2_coverage < min_tier2_coverage:  # default: 0.90
        failures.append(f"tier2_coverage {tier2_coverage:.3f} < {min_tier2_coverage:.3f}")

    gate = GateResult(
        name="finding_template_contracts",
        ok=(len(failures) == 0),
        ...
    )
```

**Line 395**: The hard gate fails if `tier2_coverage < 0.90` (minimum required)

**Current system**: 0.236 < 0.90 → FAIL
**With fixed file**: 0.854 < 0.90 → Still FAIL (but close: 0.854 vs 0.90)

### 7. The 49-Point Hard Gate Cap

From `scripts/compute_system_health.py` (lines 580-582):

```python
hard_gates_ok = all(gate.ok for gate in gates.values()) if gates else True
if not hard_gates_ok:
    weighted = min(weighted, 49.0)  # ← Cap at 49 if any hard gate fails
```

**Current state**:
- Hard gate FAILS (0.236 < 0.90)
- Score capped at 49.0/100
- Band: RED
- Status: FAIL

**With fixed file**:
- Hard gate FAILS (0.854 < 0.90)
- Score capped at 49.0/100 (still)
- But only 3.6 percentage points away from passing

### 8. AG's Reported 86.9% Coverage

From `COORDINATION.md` (dated 2026-03-01):

```markdown
| SC-T2-3 | Tier2 coverage ≥50% | ✅ **86.9%** (22,031/25,355) |
```

**Analysis**:
- AG processed 25,355 findings (not the 3,420 in current system)
- Reported 86.9% tier2 coverage
- The `finding_template_theory_links_fixed.json` has 86.4% coverage
- **Difference likely due**:
  - AG was processing extraction findings from the integration pipeline
  - The fixed file represents a subset of those (3,420 integrated beliefs)
  - Coverage rates are nearly identical (86.9% vs 86.4%)

### 9. Why Current File (23.6%) Instead of Fixed (85.6%)?

Hypothesis: After AG's tier2 resolution processing produced the _fixed file, subsequent operations (patching, persisting, or re-running) regenerated the current file with incomplete tier2 data.

Timeline reconstruction:
1. AG ran tier2 resolution → `finding_template_theory_links_fixed.json` (86.4% coverage)
2. Some patching operation → `finding_template_theory_links_patched.json` (15.7% coverage)
3. Final output or persistence → `finding_template_theory_links.json` (23.6% coverage) ← **CURRENT**

The exact operations between steps 1-3 are unclear, but they resulted in tier2 annotations being lost.

---

## Data Mapping

### Finding IDs Structure

All findings use this pattern:
```
belief_id: "doi:10.1234/....:TBL-20260216...:C001"
environment_id: "env_00133fe7"
outcome_id: "out_01a2b3c4"
```

These map to:
- Source paper DOI
- Extracted table/section identifier
- Column/cell reference
- Environment and outcome variable IDs

### Tier2 Annotation Structure

In `epistemic_v2` JSON column:

```json
{
  "template_relevance_v1": {
    "tier1_relevance": {
      "THEORY_NAME": 0.75
    },
    "tier2_relevance": {
      "DOMAIN_FRAMEWORK": 0.85,
      "ANOTHER_FRAMEWORK": 0.42
    }
  }
}
```

**Key field**: `template_relevance_v1.tier2_relevance` — must be non-empty dict

---

## Critical Path to Resolution

### Option A: Use the Fixed File (RECOMMENDED - Immediate)

**Action**: Replace current file with fixed file

```bash
cp data/production/finding_template_theory_links_fixed.json \
   data/production/finding_template_theory_links.json
```

**Expected outcome**:
- Tier2 coverage: 23.6% → 85.6%
- Hard gate: Still FAILS (85.6% < 90%)
- AESHI score: Still capped at 49/100 (need 90% to pass)
- **But**: Only 4.4 percentage points away from passing (vs 66.4 currently)

### Option B: Reach 90% Tier2 Coverage Target

**Gap**: 90% of 3,420 = 3,078 beliefs need tier2 annotations
**Current in fixed**: 2,929 have tier2
**Additional needed**: 149 beliefs

**Approach**:
1. Identify the 491 beliefs without tier2 in fixed file
2. Run targeted tier2 resolution on those 491
3. Should be feasible in 5-10 minutes

**Expected outcome**:
- Tier2 coverage: 90%+
- Hard gate: PASS
- AESHI score: Calculated from all components
- Band: Likely YELLOW or GREEN (depending on other metrics)

### Option C: Understand the Lost Data

**Investigation**:
- Check git history (if available) to see what changed between _fixed and current
- Review any scripts that regenerated the current file
- Determine if the tier2 data can be recovered from intermediate files

---

## SQL Verification Queries

To verify findings in the database:

```sql
-- Count total beliefs with any annotation
SELECT COUNT(*) FROM beliefs WHERE epistemic_v2 IS NOT NULL AND epistemic_v2 != '';

-- Count with tier2 data
SELECT COUNT(*)
FROM beliefs
WHERE epistemic_v2 IS NOT NULL
  AND json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') IS NOT NULL
  AND json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') != '{}';

-- Sample beliefs with tier2
SELECT belief_id,
       json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') as tier2
FROM beliefs
WHERE epistemic_v2 IS NOT NULL
LIMIT 5;
```

---

## Files and Line References

| File | Key Lines | Purpose |
|------|-----------|---------|
| `scripts/compute_system_health.py` | 366-421 | Compute tier2 coverage & hard gate |
| `scripts/compute_system_health.py` | 580-582 | Apply 49-point cap if hard gates fail |
| `data/production/finding_template_theory_links.json` | - | CURRENT, 23.6% coverage |
| `data/production/finding_template_theory_links_fixed.json` | - | HIGH-QUALITY, 85.6% coverage |
| `COORDINATION.md` | Line ~49 | AG reported 86.9% coverage (SC-T2-3) |

---

## Blockers & Next Steps

### Current Blockers

1. **Hard gate not passing** (0.236 < 0.90)
   - Prevents AESHI from scoring above 49
   - Needs tier2 coverage to reach 90%

2. **Data loss/divergence**
   - Fixed file exists but not integrated
   - Current file has incomplete annotations
   - Gap of 2,244 beliefs with lost tier2 data

### Recommended Actions (Priority Order)

1. **IMMEDIATE**: Replace current links file with fixed
   - `cp finding_template_theory_links_fixed.json finding_template_theory_links.json`
   - Re-run AESHI to verify coverage improves to 85.6%

2. **NEXT**: Run targeted tier2 resolution on missing 491 beliefs
   - Identify beliefs in fixed file without tier2
   - Run through tier2 relevance resolver
   - Update links file to 90%+ coverage

3. **FOLLOWUP**: Understand what regenerated current file
   - Check git history or script logs
   - Prevent similar data loss in future runs
   - Document the correct pipeline

---

## Appendix: Numeric Summary

```
Beliefs in current system: 3,420
Beliefs in fixed file: 3,420 (identical set)

Current file tier2 coverage: 23.6% (807 with tier2)
Fixed file tier2 coverage: 85.6% (2,929 with tier2)
Difference: 2,122 additional beliefs with annotations

Target for hard gate: 90% (3,078 beliefs)
Fixed file gap to target: 149 beliefs (4.4%)

AESHI score current: 49.0 (capped by hard gate)
AESHI band current: RED
AESHI status current: FAIL

Potential score with fixed: 49.0 (still capped, but close to passing)
Potential score at 90%: TBD (depends on other subscores, but no cap)
```

---

## Conclusion

The Tier2 coverage discrepancy is not due to a measurement error, but rather a **data integration issue**. The high-quality annotations (86.4% coverage) exist in the `_fixed` file but have not been made the current production file. The hard gate is correctly failing because the current file truly has only 23.6% coverage, but this is not representative of the actual work completed.

**The solution is straightforward**: integrate the fixed file into production and close the remaining 4.4% gap to reach 90% coverage.
