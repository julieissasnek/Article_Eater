# Technical Reference: Tier2 Coverage Investigation

**Date**: 2026-03-01
**Database**: web_persistence_v2.db (3,420 beliefs)
**Measurement Script**: scripts/compute_system_health.py

---

## Database Query Results

### 1. Total Belief Count

```sql
SELECT COUNT(*) FROM beliefs;
-- Result: 3420
```

### 2. Beliefs with Annotations

```sql
SELECT COUNT(*) FROM beliefs WHERE epistemic_v2 IS NOT NULL AND epistemic_v2 != '';
-- Result: 3420 (100%)
```

### 3. Beliefs with Tier2 Data (Current File)

```sql
SELECT COUNT(*)
FROM beliefs b
WHERE b.epistemic_v2 IS NOT NULL
  AND json_extract(b.epistemic_v2, '$.template_relevance_v1.tier2_relevance') IS NOT NULL
  AND json_extract(b.epistemic_v2, '$.template_relevance_v1.tier2_relevance') != '{}';
-- Result: 3420 (but empty dicts in 2,613 beliefs)
```

### 4. Sample Beliefs with Tier2 Data

```sql
SELECT belief_id,
       json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') as tier2
FROM beliefs
WHERE epistemic_v2 IS NOT NULL
  AND json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') IS NOT NULL
  AND json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance') != '{}'
LIMIT 5;
```

---

## File Analysis

### Current Production File

**Path**: `/absolute/path/Article_Eater_PostQuinean_v1/data/production/finding_template_theory_links.json`

**Metadata**:
- Size: 3,204,749 bytes (3.2 MB)
- Modified: 2026-03-01 02:33:57 UTC
- Format: JSON with `resolutions` array

**Structure**:
```json
{
  "resolutions": [
    {
      "belief_id": "doi:10.25916/...:TBL-...:C001",
      "environment_id": "env_00133fe7",
      "outcome_id": "out_01a2b3c4",
      "tier1_relevance": {"THEORY_A": 0.75, ...},
      "tier2_relevance": {},  // Empty in 2,613 cases (current)
      "top_templates": [...]
    },
    ...
  ]
}
```

**Count Statistics**:
```python
import json
links = json.loads(open('data/production/finding_template_theory_links.json').read())
resolutions = links.get('resolutions', [])
total = len(resolutions)  # 3,420
with_tier2 = sum(1 for r in resolutions if r.get('tier2_relevance'))  # 807
coverage = with_tier2 / total  # 0.2360 (23.6%)
```

---

### Fixed Quality File

**Path**: `/absolute/path/Article_Eater_PostQuinean_v1/data/production/finding_template_theory_links_fixed.json`

**Metadata**:
- Size: 5,246,164 bytes (5.2 MB)
- Modified: 2026-03-01 02:05:00 UTC
- Format: Same JSON structure

**Count Statistics**:
```python
import json
links = json.loads(open('data/production/finding_template_theory_links_fixed.json').read())
resolutions = links.get('resolutions', [])
total = len(resolutions)  # 3,420
with_tier2 = sum(1 for r in resolutions if r.get('tier2_relevance'))  # 2,929
coverage = with_tier2 / total  # 0.8564 (85.6%)
```

**Size Difference**: 2,041,415 bytes (63.8% larger) due to tier2 content

---

## Comparison: Current vs Fixed

### Belief-Level Comparison

```python
import json

current = json.loads(open('data/production/finding_template_theory_links.json').read())
fixed = json.loads(open('data/production/finding_template_theory_links_fixed.json').read())

curr_res = {r['belief_id']: r for r in current.get('resolutions', [])}
fixed_res = {r['belief_id']: r for r in fixed.get('resolutions', [])}

# Statistics
common_ids = set(curr_res.keys()) & set(fixed_res.keys())
# Result: 3420 (100% overlap)

# Tier2 status changes
tier2_changes = 0
for bid in common_ids:
    curr_has = bool(curr_res[bid].get('tier2_relevance'))
    fixed_has = bool(fixed_res[bid].get('tier2_relevance'))
    if curr_has != fixed_has:
        tier2_changes += 1
# Result: 2,244 beliefs with different tier2 status
```

### Examples of Differences

#### Example 1: `template:ARCH_PROMENADE_TEMPORAL_PE_001`

**Current**:
```json
{
  "belief_id": "template:ARCH_PROMENADE_TEMPORAL_PE_001",
  "tier2_relevance": {}
}
```

**Fixed**:
```json
{
  "belief_id": "template:ARCH_PROMENADE_TEMPORAL_PE_001",
  "tier2_relevance": {
    "PREDICTIVE_PROCESSING": 0.7774,
    "ADAPTIVE_THERMAL_COMFORT": 0.3955,
    "ALLOSTATIC_REGULATION": 0.3955,
    "IC": 0.3955,
    "INTEROCEPTION": 0.3955,
    "METABOLIC_HEALTH": 0.3955,
    "CHRONOBIOLOGICAL": 0.2855,
    "NEUROMODULATORY": 0.2855
  },
  "top_templates": [
    {
      "template_id": "THERMAL_ADAPTIVE_PE_001",
      "display_id": "MAT2",
      "score": 0.7909,
      "reasons": ["environmental endpoint alignment", ...]
    }
  ]
}
```

---

## AESHI Hard Gate Code Path

### Source File
`scripts/compute_system_health.py`, lines 366-421

### Key Function
```python
def compute_finding_contract(
    links_json: Path,
    templates_dir: Path,
    web_db: Path,
    annotation_key: str = "template_relevance_v1",
    min_unique_tier1: int = 10,
    min_tier2_coverage: float = 0.90,  # ← HARD GATE THRESHOLD
    max_non_music_music_top: int = 0,
    min_persisted_ratio: float = 1.0,
) -> tuple[dict[str, Any], GateResult]:

    # Load resolutions
    links = load_json(links_json)
    resolutions = links.get("resolutions", [])
    findings_total = len(resolutions)

    # Count tier2
    findings_with_tier2 = sum(1 for r in resolutions if r.get("tier2_relevance"))
    tier2_coverage = (findings_with_tier2 / findings_total) if findings_total else 0.0

    # Check hard gate
    failures: list[str] = []
    if tier2_coverage < min_tier2_coverage:
        failures.append(f"tier2_coverage {tier2_coverage:.3f} < {min_tier2_coverage:.3f}")

    # Create gate result
    gate = GateResult(
        name="finding_template_contracts",
        ok=(len(failures) == 0),
        exit_code=0 if not failures else 1,
        detail="; ".join(failures) if failures else "all contracts passed",
    )
    return metrics, gate
```

### Hard Gate Output (Current System)

```
finding_template_contracts gate:
  name: "finding_template_contracts"
  ok: False  # ← GATE FAILS
  exit_code: 1
  detail: "tier2_coverage 0.236 < 0.90"
```

### Hard Gate Output (With Fixed File)

```
finding_template_contracts gate:
  name: "finding_template_contracts"
  ok: False  # ← Still fails, but close
  exit_code: 1
  detail: "tier2_coverage 0.856 < 0.90"
```

### Score Cap Code (lines 580-582)

```python
hard_gates_ok = all(gate.ok for gate in gates.values()) if gates else True
if not hard_gates_ok:
    weighted = min(weighted, 49.0)  # ← CAP AT 49 IF ANY GATE FAILS
```

**Implication**:
- Current: 0.236 < 0.90 → gates fail → score capped at 49
- With fixed: 0.856 < 0.90 → gates fail → score capped at 49 (still)
- At 90%+: All gates pass → score calculated freely

---

## File Timeline

```
Timestamp            File Name                        Coverage    Size
──────────────────── ─────────────────────────────── ────────── ──────────
2026-03-01 02:05:00  finding_template_theory_links_fixed.json      85.6%    5.2 MB
2026-03-01 02:08:00  finding_template_theory_links_patched.json     15.7%    2.7 MB
2026-03-01 02:33:57  finding_template_theory_links.json    23.6%    3.2 MB  ← CURRENT
2026-03-01 06:28:00  finding_template_theory_links_persisted.json   15.7%    2.7 MB
```

**Pattern**: Fixed file (high quality) → subsequent files show regression

---

## Database Variants

All databases on system:

| Path | Beliefs | Annotated | epistemic_v2 | Notes |
|------|---------|-----------|--------------|-------|
| data/web_persistence.db | 4,888 | 0 | NULL | Legacy, no annotations |
| data/web_persistence_v2.db | **3,420** | 3,420 | Populated | **Active system** |
| data/web_persistence_LOCKED.db | 4,888 | 4,888 | Populated | Full but locked |
| data/web_persistence_v2.codex_direction_safe.db | 382 | 0 | NULL | Variant experiment |
| data/web_persistence_v2.codex_hard_direction.db | 382 | 0 | NULL | Variant experiment |
| data/web_persistence_v2.codex_release_candidate.db | 382 | 0 | NULL | Variant experiment |

---

## Tier2 Data Structure (Database Level)

### JSON Schema in epistemic_v2 Column

```json
{
  "template_relevance_v1": {
    "tier1_relevance": {
      "THEORY_NAME": 0.75,
      "ANOTHER_THEORY": 0.60
    },
    "tier2_relevance": {
      "DOMAIN_FRAMEWORK_1": 0.85,
      "DOMAIN_FRAMEWORK_2": 0.42,
      "DOMAIN_FRAMEWORK_3": 0.38
    }
  }
}
```

### Key Paths

- `epistemic_v2`: Top-level JSON string column
- `json_extract(epistemic_v2, '$.template_relevance_v1')`: Annotation object
- `json_extract(epistemic_v2, '$.template_relevance_v1.tier2_relevance')`: Tier2 data
- **Check**: `tier2_relevance != '{}'` (empty dict is falsy)

### Population Status (Current DB)

```sql
-- Beliefs with non-empty tier2 data
SELECT COUNT(*)
FROM beliefs b
WHERE b.epistemic_v2 IS NOT NULL
  AND json_type(json_extract(b.epistemic_v2, '$.template_relevance_v1.tier2_relevance')) = 'object'
  AND json_extract(b.epistemic_v2, '$.template_relevance_v1.tier2_relevance') != '{}';
-- Result: 807 (23.6%)
```

---

## Recovery Instructions

### Immediate Fix (1 minute)

```bash
cd /absolute/path/Article_Eater_PostQuinean_v1
cp data/production/finding_template_theory_links_fixed.json \
   data/production/finding_template_theory_links.json
```

Verify:
```bash
python3 -c "
import json
data = json.loads(open('data/production/finding_template_theory_links.json').read())
res = data.get('resolutions', [])
with_tier2 = sum(1 for r in res if r.get('tier2_relevance'))
print(f'Coverage: {with_tier2}/{len(res)} = {with_tier2/len(res):.1%}')
"
# Expected: Coverage: 2929/3420 = 85.6%
```

### Medium-Term Fix (5-10 minutes)

Reach 90% coverage target by filling remaining 149 beliefs:

```bash
python3 scripts/run_finding_template_relevance.py \
  --web-db data/web_persistence_v2.db \
  --templates-dir data/templates \
  --output data/production/finding_template_theory_links.json \
  --min-template-score 0.25 \
  --min-tier-support-score 0.30
```

---

## Verification Commands

### Python

```python
import json
import sqlite3

# Check current file
links = json.loads(open('data/production/finding_template_theory_links.json').read())
res = links.get('resolutions', [])
with_tier2 = sum(1 for r in res if r.get('tier2_relevance'))
print(f"File coverage: {with_tier2}/{len(res)} = {with_tier2/len(res):.4f}")

# Check database
conn = sqlite3.connect('data/web_persistence_v2.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM beliefs")
total = cur.fetchone()[0]
print(f"DB beliefs: {total}")
conn.close()
```

### Shell (with sqlite3 installed)

```bash
sqlite3 data/web_persistence_v2.db "
SELECT COUNT(*) as total,
       COUNT(CASE WHEN epistemic_v2 IS NOT NULL THEN 1 END) as annotated
FROM beliefs;
"
```

---

## References

### Related Files

1. **Investigation Report**: `INVESTIGATION_TIER2_COVERAGE_DISCREPANCY_2026-03-01.md`
2. **Findings Summary**: `FINDINGS_SUMMARY.txt`
3. **AESHI Script**: `scripts/compute_system_health.py`
4. **Finding Resolver**: `src/services/finding_template_relevance.py`
5. **Coordination Log**: `COORDINATION.md`

### Key Code Locations

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| Hard gate check | compute_system_health.py | 395-396 | Compare tier2 to 0.90 |
| Hard gate failure | compute_system_health.py | 580-582 | Cap score at 49 if gates fail |
| File loading | compute_system_health.py | 366-421 | Load and process findings |
| Tier2 count | compute_system_health.py | 379 | Count findings with tier2_relevance |

---

## Summary

| Metric | Current | Fixed | Target |
|--------|---------|-------|--------|
| Tier2 coverage | 23.6% | 85.6% | 90.0% |
| Findings with tier2 | 807 | 2,929 | 3,078 |
| Gap to target | 2,271 | 149 | 0 |
| Hard gate | FAIL | FAIL | PASS |
| AESHI score cap | 49 | 49 | Free |
| Band | RED | RED | TBD |

**Path to Green**: Fixed file + 149 additional beliefs = Hard gate passes = Score calculated freely
