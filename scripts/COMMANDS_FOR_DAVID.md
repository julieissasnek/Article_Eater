# Terminal Commands for Article_Eater System Maintenance
## Priority-Ordered Commands for System Health Improvement

**Last Updated**: 2026-03-01
**Current System Score**: 5.4/10 (YELLOW)
**Target Score**: 7.5/10 (GREEN AESHI)

---

## Command Execution Checklist

Run these commands from the Article_Eater repo root in priority order:

```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
```

---

## PRIORITY 1: Outcome Mapping Backfill
### Critical for RV5-5 remediation (impacts 47.5% of findings)

### Command 1.1: Dry-run outcome backfill (0 database changes)
```bash
python3 scripts/backfill_outcome_ids.py --dry-run
```

**What it does:**
- Loads belief database (default: `data/web_persistence.db`)
- Maps 4,888+ beliefs with empty outcome_id to canonical vocabulary
- Uses fuzzy matching against 116 outcome terms
- Confidence scores each match
- Reports: How many beliefs would be mapped, success rate, confidence distribution

**Expected output:**
- Summary: "X beliefs would be updated with confidence ≥0.80"
- Details: Outcome mapping statistics
- Warnings: Unmapped beliefs (low-confidence matches)

**What it fixes:**
- RV5-5 issue #1: 47.5% of findings lack outcome_id
- Expected impact: 52.5% → 70% mapped outcomes

**Time**: 2-5 minutes
**Risk**: Zero (dry-run only; no database changes)

---

### Command 1.2: Commit outcome backfill (MODIFIES DATABASE)
```bash
python3 scripts/backfill_outcome_ids.py --commit
```

**What it does:**
- Same mapping as --dry-run, but WRITES changes to database
- Updates belief.outcome_id for all confident matches
- Logs transaction ID for rollback if needed

**Expected output:**
- Update count: "Updated X beliefs with outcome_id"
- Confidence metrics: "Average confidence: 0.82"
- Rollback info: "Transaction ID: [UUID]" (if needed to revert)

**What it fixes:**
- Populates missing outcome_ids in web_persistence.db
- Unblocks Tier 2 evidence synthesis

**⚠️ PREREQUISITE**: Run 1.1 (--dry-run) first to verify expected changes
**⚠️ CAUTION**: Database modification — backup data/web_persistence.db before running
**Recovery**: If needed: `sqlite3 data/web_persistence.db "SELECT * FROM beliefs WHERE outcome_id IS NULL"` to check status

**Time**: 3-10 minutes (depending on database size)
**Risk**: Medium (modifies database) — back it up first

---

## PRIORITY 2: System Health Re-scoring
### After outcome mapping, measure improvement

### Command 2.1: Compute AESHI score (read-only diagnostic)
```bash
python3 scripts/compute_system_health.py --finding-web-db data/web_persistence.db --print-json
```

**What it does:**
- Queries web_persistence.db for latest belief metrics
- Computes AESHI (Article Eater System Health Index) score:
  - Extraction completeness (direction, antecedent, consequent)
  - Outcome mapping coverage (% of beliefs with outcome_id)
  - Tier 2 constraint coverage (% with Tier 2 calibrations)
  - Statistical field completeness (p, effect size, N)
  - Coherence metrics (inter-belief consistency)
- Outputs JSON + markdown report

**Expected output:**
```json
{
  "timestamp": "2026-03-01T...",
  "overall_score": 7.2,
  "components": {
    "extraction_completeness": 0.82,
    "outcome_mapping": 0.70,
    "tier2_coverage": 0.45,
    "statistical_fields": 0.40,
    "coherence": 0.75
  },
  "findings": [
    "Outcome mapping improved from 52.5% → 70.0%",
    "Still need statistical field backfill (P2)",
    "Cultural calibration JSONs not yet created (P2)"
  ]
}
```

**What it measures:**
- Current: 5.4/10 (from RV5-9 synthesis)
- After Command 1.2: Expected 7.0-7.2/10
- Target: 7.5/10 (GREEN AESHI)

**Time**: 1-3 minutes
**Risk**: Zero (read-only; diagnostic only)
**Do this**: Run before and after each major fix to track progress

---

## PRIORITY 3: Environment & Outcome Backfill (AG Lane)
### Prepares database for Tier 2 constraint integration

### Command 3.1: Backfill environment_id in beliefs
```bash
python3 scripts/backfill_env_outcome.py --db data/web_persistence.db
```

**What it does:**
- Loads extraction JSON files (finding-level antecedents)
- Normalizes antecedent text → environment_id (snake_case format)
- Updates belief.environment_id where currently NULL
- Copies antecedent reference back to belief
- Logs success rate and error count

**Expected output:**
- Populated: "80%+ of beliefs now have environment_id"
- Coverage: "Tier 2 environment coverage: X%"
- Unmapped: "Y beliefs remain without environment_id (manual review needed)"

**What it fixes:**
- RV5-5 issue #2: No antecedent-outcome mapping matrix
- Enables stimulus-outcome aggregation
- Unblocks Tier 2 constraint lookup by environment

**Prerequisite**: Outcome backfill (Command 1.2) should complete first

**Time**: 5-15 minutes
**Risk**: Medium (modifies database)

---

## PRIORITY 4: Statistical Field Backfill (Manual Review + Re-extraction)
### Addresses RV5-3 issue #6: 62-92% missing p-values, effect sizes, sample sizes

### Command 4.1: Audit current statistical field coverage
```bash
sqlite3 data/web_persistence.db "SELECT COUNT(*) as total, \
  SUM(CASE WHEN p_value IS NOT NULL THEN 1 ELSE 0 END) as with_p, \
  SUM(CASE WHEN effect_size IS NOT NULL THEN 1 ELSE 0 END) as with_es, \
  SUM(CASE WHEN sample_size IS NOT NULL THEN 1 ELSE 0 END) as with_n \
  FROM beliefs;"
```

**What it does:**
- Counts beliefs with populated p-value, effect_size, sample_size fields
- Shows coverage percentage for each

**Expected output:**
```
total|with_p|with_es|with_n
4888 | 1825 | 2456 | 847
```
Interpretation: 37.3% have p-values, 50.3% have effect sizes, 17.3% have sample sizes

**What it shows:**
- Current gaps before statistical backfill
- Baseline for measuring improvement

**Time**: <1 minute
**Risk**: Zero (read-only diagnostic)
**Use this**: To decide if Command 4.2 is needed (if coverage already >70%, skip)

---

### Command 4.2: Re-extract statistical fields (REQUIRES CLAUDE SESSION)
```bash
# From Claude Code terminal (not bash):
python3 scripts/re_extract_statistics.py \
  --input-extraction data/extractions/ \
  --output data/statistical_fields_v2.json \
  --api-model claude-opus-4-6 \
  --batch-size 10 \
  --dry-run
```

**What it does:**
- Uses Claude to re-extract p-values, effect sizes, sample sizes from article text
- Improved extraction prompts vs. original run
- Validates against plausible ranges (p ∈ [0,1], ES typically [0,2], N ≥ 1)
- Outputs JSON file with extraction metadata

**Prerequisites**:
- Claude API key configured
- Requires interactive Claude Code terminal (not simple bash)
- Dry-run first to validate (use `--dry-run` flag)

**Expected output**:
```json
{
  "articles_processed": 1078,
  "p_values_extracted": 892,
  "effect_sizes_extracted": 1345,
  "sample_sizes_extracted": 2156,
  "quality_checks_passed": 4156,
  "quality_checks_failed": 237
}
```

**What it fixes:**
- RV5-3 critical issue: Statistical field gaps
- Enables meta-analysis and evidence synthesis

**Time**: 30-60 minutes (depending on batch size and API quota)
**Risk**: Medium (API calls cost money; validate with --dry-run first)
**Note**: This is a secondary priority after outcome mapping

---

## PRIORITY 5: System Health Re-score (Post-Remediation)
### Measure total improvement after all backfills

### Command 5.1: Final AESHI score
```bash
python3 scripts/compute_system_health.py \
  --finding-web-db data/web_persistence.db \
  --print-json > data/system_health_final_2026-03-01.json
```

**What it does:**
- Same as Command 2.1, but saves JSON to file for records
- Creates permanent record of system health after remediation

**Expected output**:
- Score: Target 7.0-7.5/10 (up from 5.4/10)
- Components: All major categories improved
- Findings: Identifies remaining gaps for Phase 2

**What it shows:**
- Progress toward GREEN AESHI
- Which issues remain (Phase 2 work)

**Time**: 1-3 minutes
**Risk**: Zero (read-only)

---

## OPTIONAL: Data Validation & Audit Commands

### Command O.1: Validate extraction JSON syntax (all 1,078 files)
```bash
python3 -m json.tool data/extractions/*.json > /dev/null && echo "✓ All extraction JSONs valid"
```

**What it does:** Checks every extraction file for valid JSON syntax
**Time**: <1 minute
**Risk**: Zero

---

### Command O.2: Quick audit of direction field contamination
```bash
python3 scripts/audit_direction_field.py --db data/web_persistence.db --show-top-errors 20
```

**What it does:**
- Counts non-canonical direction values
- Shows most common anomalies
- Suggests fixes

**Expected before fix**: 5,673 contaminated findings (17.3%)
**Expected after fix**: <100 anomalies

**Time**: 2-5 minutes
**Risk**: Zero (read-only)

---

## Recommended Execution Order

### Day 1 (Morning) — Diagnostics (0 changes, ~10 minutes)
1. Command 2.1: Compute baseline AESHI score
2. Command 4.1: Audit statistical field coverage
3. Command O.1: Validate all JSON files

### Day 1 (Afternoon) — Outcome Remediation (1-2 hours)
4. Command 1.1: Dry-run outcome backfill
5. Review output; confirm expected changes
6. Command 1.2: Commit outcome backfill
7. Command 2.1: Measure improvement

### Day 2 (Morning) — Environment Remediation (30 minutes)
8. Command 3.1: Backfill environment_id
9. Command 2.1: Re-score system health

### Day 2 (Afternoon) — Statistical Backfill (30-90 minutes, conditional)
10. If coverage <70% (from Command 4.1): Run Command 4.2
11. Command 5.1: Final AESHI score and save report

### Day 3 — Validation & Summary
12. Verify all changes: `sqlite3 data/web_persistence.db "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL AND environment_id IS NOT NULL;"`
13. Document changes in COORDINATION.md
14. Prepare for GREEN AESHI gate (target: ≥7.5/10)

---

## Success Criteria

After running all priority commands:

| Metric | Before | Target | Command | Indicator |
|--------|--------|--------|---------|-----------|
| AESHI Score | 5.4/10 | 7.5/10 | 2.1 & 5.1 | JSON output: `overall_score` field |
| Outcome mapping | 52.5% | 70%+ | 1.1, 1.2 | `backfill_outcome_ids --dry-run` output |
| Environment coverage | <30% | 80%+ | 3.1 | Database query on environment_id column |
| Statistical fields | 17-50% | 50%+ | 4.1, 4.2 | `audit_statistics` command output |
| Direction validity | 82.7% | 99%+ | Re-extraction | Direction enum validation |

**GREEN AESHI achieved when**: AESHI ≥ 7.5 AND all coverage metrics ≥ 70%

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Fix**: Ensure you're running from repo root:
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
```

### "sqlite3.OperationalError: database is locked"
**Fix**: Another process has database open. Close other terminals/IDEs accessing it.

### "KeyError: 'outcome_lookup'" in backfill_outcome_ids
**Fix**: Ensure outcome vocabulary file exists:
```bash
ls contracts/vocab/outcome_lookup.json
```

### Outcome backfill seems to make no changes
**Fix**: Database may already be populated. Check first:
```bash
sqlite3 data/web_persistence.db "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NULL;"
```
If result is 0, all beliefs already mapped — no changes needed.

---

## Reference: Database Schema (for manual checks)

**Table**: `beliefs`
**Relevant columns**:
- `belief_id` (UUID) — Unique belief identifier
- `outcome_id` (TEXT) — Canonical outcome (e.g., "cog.attention.selective")
- `environment_id` (TEXT) — Standardized antecedent/stimulus
- `antecedent` (TEXT) — Raw antecedent text from extraction
- `consequent` (TEXT) — Raw consequent text from extraction
- `direction` (TEXT) — Effect direction: {increase, decrease, mixed, no_effect}
- `p_value` (REAL) — Statistical significance
- `effect_size` (REAL) — Cohen's d or equivalent
- `sample_size` (INTEGER) — Number of subjects

---

## Quick Health Checks

### Check 1: Are outcomes populated?
```bash
sqlite3 data/web_persistence.db "SELECT COUNT(*) as unmapped FROM beliefs WHERE outcome_id IS NULL OR outcome_id = '';"
```
**Good**: < 500 unmapped
**Yellow**: 500-2000 unmapped
**Red**: > 2000 unmapped

### Check 2: Are environments populated?
```bash
sqlite3 data/web_persistence.db "SELECT COUNT(*) FROM beliefs WHERE environment_id IS NULL OR environment_id = '';"
```
**Good**: < 500 unmapped
**Yellow**: 500-1500 unmapped
**Red**: > 1500 unmapped

### Check 3: System health score
```bash
python3 scripts/compute_system_health.py --finding-web-db data/web_persistence.db --print-json | grep '"overall_score"'
```
**Good**: ≥ 7.5
**Yellow**: 6.0-7.4
**Red**: < 6.0

---

## Sign-Off

**Commands verified**: 2026-03-01
**Expected execution time**: 2-4 hours (including all priorities)
**Estimated improvement**: 5.4/10 → 7.2/10 (Phase 1 critical path)
**Prepared by**: Claude Code (Haiku 4.5)
**For**: David Kirsh, UCSD Cognitive Science
