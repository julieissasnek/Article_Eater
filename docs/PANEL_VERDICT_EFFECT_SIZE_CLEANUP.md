# Expert Panel Verdict: Effect Size Cleanup (--commit)

**Date**: March 2, 2026
**Panel Decision**: APPROVE WITH CONDITIONS
**Risk Level**: Medium
**Confidence**: High (65-85% across panelists)

---

## Executive Summary

The panel unanimously supports executing `python scripts/clean_effect_sizes.py --commit` to clean 536 problematic effect sizes in 124 extraction files. However, we impose **three binding conditions** on execution to preserve data integrity and enable oversight.

**Key Finding**: The problems are real, well-classified, and the data is currently contaminating downstream credence computations. The cleanup is justified. But the execution must include safeguards and a post-commit audit.

---

## Problem Statement (Consensus)

**Scope**: 536 problems across 124 extraction JSON files

| Problem Type | Count | Severity |
|--------------|-------|----------|
| P-values in effect_size field | 288 | CRITICAL |
| Non-numeric values | 217 | MODERATE |
| Out-of-range values | 19 | CRITICAL |
| Extreme outliers | 12 | MODERATE |
| **TOTAL** | **536** | — |

**Impact on System**: Effect sizes feed directly into credence computation (logit projection in GraphConfidenceService). Contaminated effect sizes produce invalid credences, which propagate through query responses.

---

## Panelist Positions

### 1. Data Steward

**Concern**: Provenance, auditability, reversibility

**Assessment**:
- **Strength**: The script quarantines (not deletes) bad values:
  - Original value moves to `_original_effect_size`
  - Quarantine reason saved in `_quarantine_reason`
  - This enables full audit trail and potential recovery
  - Files are modified in-place with no backup mechanism external to version control

- **Weakness**:
  - 124 files will be silently modified in git history
  - No separate quarantine directory or archive file
  - Future investigators must read JSON to reconstruct what changed
  - Git commit message alone won't capture the 536 individual problems

- **Risk**: Medium. The quarantine mechanism is good, but there's no central record of what was removed.

**Questions Answered**:
- Q: Does the script have a backup? A: Implicit via git. Explicit backup: NO.
- Q: Can we reverse it? A: Yes, via git revert or reading `_original_effect_size` fields.

**Vote**: **APPROVE WITH CONDITIONS**

**Conditions**:
1. Create a pre-commit summary file: `docs/EFFECT_SIZE_CLEANUP_DETAIL_2026-03-02.json` containing all 536 problems with file, index, original value, reason (for audit trail)
2. Git commit message must include: `Cleaned 536 effect size problems across 124 files (see docs/EFFECT_SIZE_CLEANUP_DETAIL_*)`
3. Post-commit: run a verification script to confirm all _original_effect_size fields are readable and contain the right values

---

### 2. Statistician

**Concern**: Are the classification rules correct? Is 0.001 really a p-value, not a tiny effect size?

**Assessment**:
- **Strength**:
  - P-value detection rule is sound: standard p-values (0.05, 0.01, 0.001, 0.0001, 0.005, etc.) are registered as TYPICAL_P_VALUES
  - The heuristic `_looks_like_pvalue()` also flags values < 0.001 as p-values (good catch)
  - For correlations, only exact p-value matches trigger wrong_field (doesn't flag legitimate small r values like r=0.08)
  - The confidence level (0.9) on wrong_field classification is appropriate — not overconfident

- **Weakness**:
  - Some p-values (e.g., 0.15, 0.25) are NOT in TYPICAL_P_VALUES and might slip through if stored in effect_size field
  - Cohen's d < 0.2 is sometimes legitimate (very small effect), but the rule doesn't special-case it
  - The rule flags "0.0001" as p-value, but it *could* be a legitimate odds ratio or raw count
  - Non-numeric "0.5-1.0" (a range) loses information — the underlying data was 0.5 to 1.0, now just null

- **Risk**: Low-to-Medium. Most problems are clearly wrong; some edge cases could be legitimate but rare.

**Validation Evidence**:
- 81 tests in `test_effect_size_validator.py` all PASS
- Tests cover: boundary cases, correlations with p-values, non-numeric, outliers, normalization
- Test for "Real-world mixed data" passes

**Vote**: **APPROVE**

**Rationale**: The classification rules are statistically sound for 95%+ of cases. The 5% edge cases (e.g., legitimate very small Cohen's d) are outweighed by the 288 clear p-value misplacements.

---

### 3. Research Methodologist

**Concern**: Are we losing legitimate effect sizes? When is d > 3.0 actually real?

**Assessment**:
- **Strength**:
  - Out-of-range validation is appropriate: partial_eta² > 1 is impossible (it's a squared correlation)
  - Negative odds ratios are impossible — flagging them is correct
  - Non-numeric values like "large", "small", "ns" (not significant) cannot be used in quantitative computation and must be marked null
  - Ranges like "0.5-1.0" are unprocessable — requires expert manual extraction

- **Weakness**:
  - 12 "outlier" cases flagged for Cohen's d > 5.0 or < -5.0
  - Cohen's d = 6.0 is rare but not impossible: e.g., drug vs. placebo in pain studies, highly controlled experiments
  - The outlier threshold (d > ±5) is reasonable as a flag, but setting effect_size=NULL loses the information
  - Non-numeric values: some (like "medium effect") might have been extractable to numeric (e.g., 0.5 for Cohen's d)

- **Risk**: Medium. We're losing 12 outlier values that might be legitimate. But the harm of including them (credence distortion) may exceed harm of losing them (reduced coverage).

**Vote**: **APPROVE WITH CONDITIONS**

**Conditions**:
1. Manually review the 12 "outlier" flagged values before commit
   - Check if they're actually in the original paper and legitimate
   - If > 50% are real, adjust OUTLIER_THRESHOLDS before commit
2. For non-numeric "large/moderate/small" values: document that these are not quantifiable and note count in cleanup report
3. Track coverage impact: How many findings lose effect_size? Report as % of total findings

---

### 4. Software Engineer

**Concern**: File I/O safety, atomicity, data corruption risk

**Assessment**:
- **Strength**:
  - Script reads file, modifies in-memory dict, writes back
  - JSON serialization is standard and safe
  - `indent=2` preserves human-readable format
  - Dry-run mode allows preview without risk
  - Error handling: try/except on read and write

- **Weakness**:
  - Not atomic: if process crashes during write, file is corrupted
  - No file locking or temporary files: write directly to target file
  - If 124 files are being written and power fails on file #50, you have 50 corrupted files
  - No disk space check: if /data fills up mid-write, silent failure
  - File permission issues: what if a file is read-only? Script logs error but continues

- **Risk**: Low-to-Medium. In normal conditions, safe. In failure conditions, risky.

**Vote**: **APPROVE WITH CONDITIONS**

**Conditions**:
1. Before commit: verify that all 124 JSON files are writable
   - Run a quick check: `for f in data/extractions/*.json; do touch "$f" || echo "Cannot write: $f"; done`
2. During commit: redirect stderr to a log file to catch any write errors
   - `python scripts/clean_effect_sizes.py --commit 2>&1 | tee effect_size_cleanup_2026-03-02.log`
3. Post-commit: verify all 124 files were successfully updated
   - Check that all 124 files are newer than pre-commit timestamp
   - Spot-check 5 random files to verify _original_effect_size fields exist

---

### 5. Epistemologist

**Concern**: Downstream impact on credence computation. Are we improving or degrading evidence quality?

**Assessment**:
- **Strength**:
  - The GraphConfidenceService uses effect_size as a direct input to credence bounds
  - A p-value (0.05) in the effect_size field produces a credence interval of [0.05, max] — nonsensical
  - A string "large" in the field causes numeric computation to fail or be skipped
  - Setting effect_size=NULL is semantically correct: "we don't know the effect size for this finding"
  - NULL values are handled gracefully by downstream code (the `base_effect_size=0.0` default applies)

- **Weakness**:
  - Nullifying effect_size reduces the coverage of findings
  - A finding with effect_size=NULL contributes no evidence of magnitude, only direction
  - If a researcher extracted "Cohen's d = 1.2" but typed it as "1.2x" (non-numeric), we lose it
  - The Quinean coherence system does NOT penalize missing effect sizes — it just ignores them
  - Impact: credence bounds widen, but don't improve

- **Risk**: Low. Setting to NULL is epistemically safer than keeping garbage, even if less informative.

**Vote**: **APPROVE**

**Rationale**:
- Current effect_size contamination is actively *harmful* to credence computation
- NULL is epistemically neutral (doesn't assert false information)
- Coverage loss is acceptable cost for removing false information
- The 288 p-values and 217 non-numeric values are not salvageable without human re-review

---

## Synthesis: Panel Verdict

**APPROVED WITH CONDITIONS**

### The Binding Conditions

**1. Pre-Commit Audit Record** (Data Steward)
```bash
# Before running --commit, save a detailed record:
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/clean_effect_sizes.py --verbose > /tmp/cleanup_dry_run.txt 2>&1
# Create docs/EFFECT_SIZE_CLEANUP_DETAIL_2026-03-02.json containing all 536 problems
```

**2. Manual Review of 12 Outliers** (Research Methodologist)
- List all 12 outlier cases (d or similar > ±5)
- For each, check original paper to verify legitimacy
- If ≥ 50% are real, increase OUTLIER_THRESHOLDS before commit
- Document decision in docs/EFFECT_SIZE_CLEANUP_DECISIONS_2026-03-02.md

**3. File Writeability Verification** (Software Engineer)
```bash
# Before commit:
for f in data/extractions/*.json; do
  if ! touch "$f"; then
    echo "Cannot write: $f"
  fi
done
```

**4. Commit Procedure**
```bash
python scripts/clean_effect_sizes.py --commit 2>&1 | tee docs/effect_size_cleanup_2026-03-02.log
# Verify all 124 files have _original_effect_size fields
git diff --stat | wc -l  # Should be ~124 files modified
```

**5. Post-Commit Verification**
- Spot-check 5 random modified files to confirm structure
- Verify no file corruption (valid JSON)
- Commit log to git: `git add docs/effect_size_cleanup_*.* && git commit -m "..."`

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| File corruption | Low (1%) | High (data loss) | Atomic writes, writeability check |
| Loss of legitimate values | Medium (10%) | Medium (reduced coverage) | Manual outlier review |
| Downstream code fails on NULL | Low (2%) | Medium (computation errors) | Already handles NULL gracefully |
| Audit trail lost | Low (1%) | Medium (forensics hard) | Pre-commit audit file |
| **Overall Risk** | **Low** | **Medium** | **All mitigated** |

---

## Confidence Levels

| Panelist | Recommendation | Confidence |
|----------|-----------------|------------|
| Data Steward | APPROVE w/ conditions | 80% |
| Statistician | APPROVE | 85% |
| Research Methodologist | APPROVE w/ conditions | 65% |
| Software Engineer | APPROVE w/ conditions | 75% |
| Epistemologist | APPROVE | 80% |
| **Panel Consensus** | **APPROVE w/ CONDITIONS** | **77% avg** |

---

## Decision Rationale

1. **The problems are real**: 288 p-values in an effect_size field is not a borderline case. These are clearly extraction errors.

2. **The cost of NOT cleaning is higher**: Garbage data contaminates credence computation. A finding with effect_size=0.05 (a p-value) produces a nonsensical credence bound.

3. **The cleanup is reversible**: Original values are preserved in `_original_effect_size`. Git history is permanent. We can audit or revert.

4. **The conditions are achievable**: Conditions require pre-commit auditing, manual outlier review, and post-commit verification—all low-overhead.

5. **The system can handle NULL**: Downstream code treats NULL effect_size as "unknown magnitude, use default bounds." This is safe.

---

## Action Items (for Execution)

Priority: **CRITICAL** — Execute in this order:

1. **Pre-commit** (30 min)
   - [ ] Run dry-run with --verbose and save output
   - [ ] Generate audit file: `docs/EFFECT_SIZE_CLEANUP_DETAIL_2026-03-02.json`
   - [ ] List 12 outliers and manually verify in source papers

2. **Execution** (5 min)
   - [ ] Verify file writeability
   - [ ] Run: `python scripts/clean_effect_sizes.py --commit 2>&1 | tee docs/effect_size_cleanup_2026-03-02.log`
   - [ ] Monitor for errors in log

3. **Post-commit** (15 min)
   - [ ] Verify all 124 files updated
   - [ ] Spot-check 5 random files for valid JSON
   - [ ] Commit audit files and log to git

---

## Panel Sign-Off

- **Data Steward**: Approve with conditions 1, 3, 4
- **Statistician**: Approve unconditionally
- **Research Methodologist**: Approve with condition 2
- **Software Engineer**: Approve with conditions 3, 4
- **Epistemologist**: Approve unconditionally

**Consensus**: PROCEED with conditions 1-5 above.

---

**Date Approved**: March 2, 2026
**Authority**: Expert Panel (Epistemology, Statistics, Methods, Data, Engineering)
**Next Review**: Post-commit verification (same date)
