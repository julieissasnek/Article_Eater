# Action Plan: Recover Tier2 Coverage from 23.6% to 90%

**Date**: 2026-03-01
**Objective**: Fix hard gate failure blocking AESHI at 49/100
**Timeline**: 15 minutes (total execution time)

---

## Current Status

| Metric | Value |
|--------|-------|
| Current tier2 coverage | 23.6% (807/3,420 beliefs) |
| Findings needing tier2 | 3,078 to pass 90% gate |
| Missing annotations | 2,271 beliefs |
| Hard gate status | FAIL (0.236 < 0.90) |
| AESHI score | Capped at 49/100 |
| AESHI band | RED |

---

## Root Cause

- High-quality file exists: `data/production/finding_template_theory_links_fixed.json` (85.6% coverage)
- Current production file: `data/production/finding_template_theory_links.json` (23.6% coverage)
- File divergence occurred at 2026-03-01 02:05–02:33 UTC
- 2,244 beliefs have tier2 annotations in fixed but not in current

---

## Solution: Three-Step Recovery

### Step 1: Promote Fixed File to Production (1 minute)

**Action**:
```bash
cd /absolute/path/Article_Eater_PostQuinean_v1
cp data/production/finding_template_theory_links_fixed.json \
   data/production/finding_template_theory_links.json
```

**Verification**:
```python
import json
data = json.loads(open('data/production/finding_template_theory_links.json').read())
res = data.get('resolutions', [])
with_tier2 = sum(1 for r in res if r.get('tier2_relevance'))
print(f"Coverage: {with_tier2}/{len(res)} = {with_tier2/len(res):.1%}")
# Expected: Coverage: 2929/3420 = 85.6%
```

**Impact**:
- Tier2 coverage: 23.6% → 85.6%
- Hard gate: Still FAIL (85.6% < 90%)
- AESHI: Still capped at 49, but only 4.4 points away from passing
- File size: 3.2 MB → 5.2 MB

**Commit** (if using git):
```bash
git add data/production/finding_template_theory_links.json
git commit -m "Recover tier2 coverage from fixed file (23.6% → 85.6%)"
```

---

### Step 2: Identify Gap Beliefs (2 minutes)

**Find beliefs without tier2 in fixed file**:

```python
import json

# Load fixed file
with open('data/production/finding_template_theory_links_fixed.json') as f:
    data = json.load(f)

resolutions = data.get('resolutions', [])

# Find beliefs without tier2
gap_beliefs = []
for r in resolutions:
    tier2 = r.get('tier2_relevance')
    if not tier2 or tier2 == {}:
        gap_beliefs.append({
            'belief_id': r['belief_id'],
            'tier1_relevance': r.get('tier1_relevance'),
            'top_templates': r.get('top_templates', [])
        })

print(f"Beliefs needing tier2: {len(gap_beliefs)}")
print(f"Coverage needed: {(3420 - len(gap_beliefs))/3420:.1%}")

# Save for targeting
with open('gap_beliefs_for_tier2.json', 'w') as f:
    json.dump(gap_beliefs, f, indent=2)
```

**Output**: 491 beliefs without tier2 annotations

---

### Step 3: Run Targeted Tier2 Resolution (10-12 minutes)

**Option A: Full pipeline (recommended)**

Run the finding template resolver on all beliefs:

```bash
python3 scripts/run_finding_template_relevance_streaming.py \
  --web-db data/web_persistence_v2.db \
  --templates-dir data/templates \
  --output data/production/finding_template_theory_links.json \
  --batch-size 500 \
  --min-template-score 0.25 \
  --min-tier-support-score 0.30 \
  --top-k-templates 5
```

**Expected runtime**: 8-10 minutes
**Expected result**: Tier2 coverage reaches 90%+

**Verification after completion**:
```python
import json
data = json.loads(open('data/production/finding_template_theory_links.json').read())
res = data.get('resolutions', [])
with_tier2 = sum(1 for r in res if r.get('tier2_relevance'))
coverage = with_tier2 / len(res) if res else 0
print(f"Final coverage: {with_tier2}/{len(res)} = {coverage:.1%}")
print(f"Gate passes: {coverage >= 0.90}")
```

**Option B: Minimal patch (faster, if time critical)**

If full resolution takes too long, patch only the gap beliefs:

```bash
# This requires modifying the resolver script to handle subset input
# Contact David if <90% coverage is unacceptable but time is limited
```

---

## Expected Outcomes

### After Step 1 (Fixed File Promoted)

```
Tier2 coverage: 85.6% (2,929/3,420)
Hard gate: FAIL (85.6% < 90.0%) ← Still failing
AESHI score: 49 (still capped) ← Improvement pending step 3
AESHI band: RED
Status: Closer, but incomplete
```

### After Step 3 (Full Resolution)

```
Tier2 coverage: 90%+ (3,078+/3,420)
Hard gate: PASS
AESHI score: Calculated freely, not capped
  Estimated: 65-75 (pending other subscores)
AESHI band: YELLOW or GREEN
Status: RESOLVED ✓
```

---

## Post-Recovery Validation

### 1. Verify Hard Gate Passes

```bash
python3 scripts/compute_system_health.py --skip-gates \
  --web-db data/web_persistence_v2.db \
  --finding-web-db data/web_persistence_v2.db \
  --links-json data/production/finding_template_theory_links.json \
  --templates-dir data/templates \
  --bn-json data/production/realtime_incremental_bn.json \
  --print-json 2>&1 | grep -A 5 "finding_template_contracts"
```

Expected output:
```
"finding_template_contracts": {
  "name": "finding_template_contracts",
  "ok": true,  ← GATE PASSES
  "exit_code": 0,
  "detail": "all finding-template contracts passed"
}
```

### 2. Check Overall AESHI Score

```bash
python3 scripts/compute_system_health.py --skip-gates \
  --web-db data/web_persistence_v2.db \
  --finding-web-db data/web_persistence_v2.db \
  --links-json data/production/finding_template_theory_links.json \
  --templates-dir data/templates \
  --bn-json data/production/realtime_incremental_bn.json \
  --markdown-out docs/system_health_report.md \
  --json-out data/production/system_health_report.json
```

### 3. Review Report

```bash
cat docs/system_health_report.md
```

Look for:
- `Overall score`: Should be >50 (not capped at 49)
- `Band`: Should be YELLOW or GREEN (not RED)
- `Hard gates_ok`: Should be TRUE

---

## Rollback Plan (if needed)

If the tier2 resolution causes unexpected issues:

```bash
# Restore current file
cp data/production/finding_template_theory_links_patched.json \
   data/production/finding_template_theory_links.json

# Or restore from git
git checkout data/production/finding_template_theory_links.json
```

---

## Documentation & Handoff

### Files Created This Investigation

1. **INVESTIGATION_TIER2_COVERAGE_DISCREPANCY_2026-03-01.md**
   - Full technical investigation
   - Database analysis
   - Examples and root cause

2. **TECHNICAL_REFERENCE_TIER2_INVESTIGATION.md**
   - SQL queries and code paths
   - File structure and timeline
   - Database-level details

3. **FINDINGS_SUMMARY.txt**
   - Executive summary
   - Key facts in plain text
   - Quick reference

4. **ACTION_PLAN_TIER2_RECOVERY.md** ← You are here

### Update COORDINATION.md

After successful recovery, add to handoff queue:

```markdown
| H13 | CW/AG | BOTH | **Tier2 Recovery Complete**: Fixed file promoted (85.6%), full resolution to 90%+ coverage. Hard gate now passes. AESHI score no longer capped at 49. See INVESTIGATION_TIER2_COVERAGE_DISCREPANCY_2026-03-01.md for full details. | P0 | 2026-03-01 | ✅ DONE (2026-03-01 HH:MM UTC) |
```

### Update TASKS.md

```markdown
| T-TIER2 | Recover tier2 coverage from 23.6% to 90%+ | COMPLETED | Promoted fixed file (85.6%), ran resolution to reach hard gate threshold. Score now free to calculate. |
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Fixed file is corrupted | Low | High | Verify with Python before promotion |
| Tier2 resolution hangs | Low | Medium | Monitor with timeout, revert if needed |
| Other hard gates still fail | Low | Low | Score still improves, gates documented |
| Tier2 coverage regression | Very low | Low | Backup current file before overwrite |

---

## Success Criteria

- [x] Fixed file identified and validated
- [ ] Fixed file promoted to production
- [ ] Tier2 coverage reaches 85.6%
- [ ] Full resolution runs to completion
- [ ] Tier2 coverage reaches 90%+
- [ ] Hard gate passes in AESHI script
- [ ] AESHI score calculated freely (not capped at 49)
- [ ] AESHI band improves (RED → YELLOW or GREEN)

---

## Timeline Estimate

| Step | Task | Duration | Start | End |
|------|------|----------|-------|-----|
| 1 | Promote fixed file | 1 min | T+0 | T+1 |
| 1 | Verify promotion | 1 min | T+1 | T+2 |
| 2 | Identify gap beliefs | 2 min | T+2 | T+4 |
| 3 | Run tier2 resolution | 10-12 min | T+4 | T+14-16 |
| 4 | Validate & verify | 2 min | T+14-16 | T+16-18 |
| **TOTAL** | | **16-18 minutes** | | |

---

## Contact & Questions

If issues arise during execution:

1. Check database connectivity: `python3 -c "import sqlite3; sqlite3.connect('data/web_persistence_v2.db').execute('SELECT 1')"`
2. Verify template directory exists: `ls -la data/templates/ | head -5`
3. Check BN JSON: `python3 -c "import json; print(len(json.loads(open('data/production/realtime_incremental_bn.json').read()).get('nodes', [])))"`
4. Consult investigation document if unexpected errors occur

---

## Summary

**What**: Replace current tier2 file with fixed version, then run full resolution
**Why**: Current file missing 2,244 tier2 annotations that were computed but not integrated
**When**: Now (blocking AESHI at RED/49)
**How**: 3 steps, ~15 minutes total
**Expected result**: Hard gate passes, score freed from 49-point cap

Good luck!
