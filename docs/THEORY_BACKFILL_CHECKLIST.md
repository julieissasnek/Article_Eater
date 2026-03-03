# Theory ID Backfill Improvement — Execution Checklist

**Date**: 2026-03-02
**Status**: Ready for execution

---

## Pre-Execution Checklist

✓ **Analysis Complete**
- [x] Identified the problem: 99.3% PP default assignment
- [x] Understood data sources: tag_assignments (91,747 tags), tier1_frameworks.json (10 theories)
- [x] Designed algorithm: highest-confidence T1 tag per belief
- [x] Validated on sample data

✓ **Script Created & Tested**
- [x] `scripts/improve_theory_backfill.py` created (206 lines)
- [x] Help text verified
- [x] Dry-run executed successfully
- [x] 1,590 changes identified and validated
- [x] Zero errors or warnings in output

✓ **Documentation Complete**
- [x] `docs/THEORY_BACKFILL_IMPROVEMENT_2026-03-02.md` (technical report)
- [x] `docs/THEORY_BACKFILL_BEFORE_AFTER.md` (visual analysis)
- [x] `THEORY_BACKFILL_SUMMARY.md` (executive summary)
- [x] `THEORY_BACKFILL_CHECKLIST.md` (this document)

✓ **Data Quality Verified**
- [x] No NULL theory_ids in current state
- [x] All 1,590 proposed changes reference valid T1 frameworks
- [x] All changes based on 0.80+ confidence tags
- [x] No orphaned references (no foreign keys to theory_id)
- [x] Reversible via belief_versions table

✓ **Risk Assessment Complete**
- [x] Data loss risk: ZERO
- [x] Foreign key conflicts: ZERO
- [x] Breaking changes: ZERO
- [x] Rollback difficulty: LOW

---

## Execution Steps

### Step 1: Pre-Flight Check (Optional but Recommended)

```bash
# Verify current state
sqlite3 data/web_persistence_v2.db "SELECT theory_id, COUNT(*) FROM beliefs GROUP BY theory_id ORDER BY COUNT DESC;"

# Expected output before changes:
# PP|3395
# CB|8
# SN|6
# NM|5
# IC|4
# MS|2
```

### Step 2: Run Dry-Run (Recommended)

```bash
# Review the analysis one final time
python3 scripts/improve_theory_backfill.py --dry-run

# Expected output:
# Database: data/web_persistence_v2.db
# Mode: DRY-RUN
# Loaded 10 T1 frameworks
# Loaded finding_template_theory_links with 4498 belief mappings
# Processing 3420 beliefs...
# === BEFORE (Current State) ===
# === AFTER (Improved State) ===
# === CHANGES SUMMARY ===
# Total beliefs: 3420
# Unchanged: 1830
# Updated from tags: 1590
# [DRY-RUN COMPLETE] No changes made to database
```

### Step 3: Apply Changes (Requires Approval)

```bash
# Run with --commit flag to apply changes
python3 scripts/improve_theory_backfill.py --commit

# Expected output:
# Database: data/web_persistence_v2.db
# Mode: COMMIT
# [... same analysis as dry-run ...]
# === COMMITTING 1590 UPDATES ===
# Updated 1590 beliefs
```

This will take ~10-30 seconds depending on disk I/O.

### Step 4: Verification (Required)

```bash
# Check the new distribution
sqlite3 data/web_persistence_v2.db "SELECT theory_id, COUNT(*) as count FROM beliefs GROUP BY theory_id ORDER BY count DESC;"

# Expected output after changes:
# PP|1805
# NM|348
# SN|269
# IC|219
# DT|160
# CB|153
# MSI|143
# DP|132
# EC|107
# MS|84
```

### Step 5: Audit (Optional)

```bash
# Check which beliefs were updated
sqlite3 data/web_persistence_v2.db \
  "SELECT COUNT(*) FROM beliefs WHERE updated_at > datetime('now', '-1 minute');"

# Should return: 1590 (or close to it, depending on timing)

# Spot-check a few changes
sqlite3 data/web_persistence_v2.db \
  "SELECT belief_id, theory_id FROM beliefs WHERE theory_id != 'PP' LIMIT 10;"

# All should show non-PP theories
```

---

## What Gets Changed

### Database: `data/web_persistence_v2.db`

**Table**: `beliefs`
**Rows affected**: 1,590 of 3,420 (46.5%)
**Columns modified**:
- `theory_id`: Updated to new value (e.g., PP → NM, IC, SN, etc.)
- `updated_at`: Set to current timestamp (audit trail)

**Rows unchanged**: 1,830 (either no better mapping found, or already correct)

### Example Changes

| belief_id | Before | After | Source | Confidence |
|-----------|--------|-------|--------|-----------|
| 10.1002/ad.2031__f1 | PP | IC | tags | 0.85 |
| 10.1002/ad.2031__f10 | PP | EC | tags | 0.85 |
| 10.1002/ad.2031__f11 | PP | IC | tags | 0.85 |
| (1,587 more...) | | | | |

---

## Post-Execution Steps

### Commit to Git (If Using Version Control)

```bash
# Add the script to version control
git add scripts/improve_theory_backfill.py
git add docs/THEORY_BACKFILL_IMPROVEMENT_2026-03-02.md
git add docs/THEORY_BACKFILL_BEFORE_AFTER.md
git add THEORY_BACKFILL_SUMMARY.md
git add THEORY_BACKFILL_CHECKLIST.md

# Commit with message
git commit -m "Improve theory_id backfill: 1,590 beliefs remapped based on tag evidence

- Updated from 99.27% PP to balanced 52.78% PP (+ all 10 T1 frameworks)
- All changes based on tag_assignments with 0.80+ confidence
- Zero data loss, fully reversible via belief_versions table
- See docs/THEORY_BACKFILL_IMPROVEMENT_2026-03-02.md for full analysis"
```

### Update TASKS.md (If Using Task Tracking)

Mark task complete:
```
| T_THEORY_BACKFILL | Improve theory_id backfill in beliefs | Completed | 1,590 beliefs remapped, all 10 T1 frameworks now represented |
```

---

## Rollback Instructions (If Needed)

If any issues arise, the changes are fully reversible:

### Option 1: Database Restore

The original `theory_id` values are preserved in the `belief_versions` table:

```sql
UPDATE beliefs
SET theory_id = (
    SELECT theory_id FROM belief_versions
    WHERE belief_versions.belief_id = beliefs.belief_id
    ORDER BY created_at DESC
    LIMIT 1
)
WHERE updated_at > datetime('now', '-1 hour');
```

### Option 2: Full Database Restore

If you have a backup from before the change:
```bash
cp data/web_persistence_v2.db.backup data/web_persistence_v2.db
```

---

## Decision Matrix

**IF you want to:**

| Action | Command |
|--------|---------|
| Review analysis only | `python3 scripts/improve_theory_backfill.py --dry-run` |
| Apply changes | `python3 scripts/improve_theory_backfill.py --commit` |
| Use custom database path | `python3 scripts/improve_theory_backfill.py --commit --database /path/to/db` |
| Get help | `python3 scripts/improve_theory_backfill.py --help` |

---

## Timeline

| Step | Est. Time | Status |
|------|-----------|--------|
| Pre-flight check | 1-2 min | Ready |
| Dry-run analysis | 2-3 min | Ready |
| Apply changes (--commit) | 10-30 sec | Ready |
| Verification queries | 1-2 min | Ready |
| Total | ~15-40 min | Ready |

---

## Approval Sign-Off

**Prepared by**: Claude Code
**Date**: 2026-03-02
**Analysis Status**: ✓ Complete
**Dry-Run Status**: ✓ Passed (1,590 changes identified)
**Documentation**: ✓ Complete (3 detailed reports)
**Script Status**: ✓ Tested and ready

**Awaiting**: David's approval to execute Step 3 (--commit mode)

---

## Contact / Questions

If any questions arise during execution:

1. Check `docs/THEORY_BACKFILL_IMPROVEMENT_2026-03-02.md` for technical details
2. Check `docs/THEORY_BACKFILL_BEFORE_AFTER.md` for data analysis
3. Check `THEORY_BACKFILL_SUMMARY.md` for Q&A section
4. Review script source: `scripts/improve_theory_backfill.py` (well-commented)

---

**Ready to execute. Awaiting approval.**
