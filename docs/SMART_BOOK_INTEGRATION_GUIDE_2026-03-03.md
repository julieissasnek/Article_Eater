# Smart Book Integration Guide

**Date**: March 3, 2026
**Version**: 1.0
**Purpose**: Instructions for integrating Smart Book into ATLAS development workflow

---

## What You've Received

Three deliverables implement the Smart Book system:

| File | Size | Purpose |
|------|------|---------|
| `docs/SMART_BOOK_DESIGN_2026-03-03.md` | 21 KB | Design document explaining precedents, architecture, motivation |
| `docs/SMART_BOOK_README.md` | 13 KB | User guide for running validator, understanding reports, maintaining manifest |
| `docs/master_doc_parts/DEPENDENCY_MANIFEST.json` | 29 KB | Machine-readable specification of all concepts and dependencies |
| `scripts/validate_master_doc.py` | 21 KB | Python validator script (executable, no dependencies) |

---

## Immediate Actions (This Week)

### 1. Review Design & Architecture

Read `SMART_BOOK_DESIGN_2026-03-03.md` to understand:
- Why the system matters (epistemically responsible documentation)
- Precedents (literate programming, Sphinx, knowledge graphs)
- How the system works (concepts, dependencies, validation)
- Future extensions

**Estimated time**: 30 minutes

### 2. Run a Validation Report

```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/validate_master_doc.py --mode=report --output=docs/VALIDATION_REPORT_2026-03-03.md
```

This generates a markdown report of current inconsistencies. Current findings:

**CRITICAL Issues** (must fix):
- PART_VII_T15_REDUCTIONS contains "1 T1.5 theory" instead of canonical value 13
- PART_VII_T15_REDUCTIONS contains "22 T1.5 theories" instead of canonical value 13

**MEDIUM Issues** (review sections for potential updates):
- T1_5_COUNT updated 2026-02-27 → review §35, §40, §54, §78, §100, §115, §142, §147
- CREDENCE_FORMULA_LOGODDS updated 2026-02-27 → review §48A, §49, §50, §51, §52, §53, §54

**Estimated time**: 10 minutes for report generation + 30 minutes to review findings

### 3. Understand the Manifest

Read `SMART_BOOK_README.md` sections on:
- "Dependency Manifest Structure" — how to read the JSON
- "Dependency Types" — what DEFINES, USES, EXTENDS, SUPERSEDES mean
- "Existing Issues Found" — what violations the validator detected

**Estimated time**: 20 minutes

---

## Short-Term Setup (This Month)

### Option A: Pre-Commit Hook (Recommended for Developers)

Prevent commits that violate consistency:

```bash
#!/bin/bash
# Copy to .git/hooks/pre-commit and chmod +x

python scripts/validate_master_doc.py --mode=validate
if [ $? -ne 0 ]; then
  echo "❌ Commit blocked by Smart Book validator"
  echo "Violations found. Run:"
  echo "  python scripts/validate_master_doc.py --mode=report"
  exit 1
fi
```

**Setup time**: 5 minutes
**Benefit**: Impossible to commit consistency violations

### Option B: CI/CD Integration (Recommended for Shared Repos)

Add GitHub Actions or similar to run validator on every push:

```yaml
# .github/workflows/validate-docs.yml
name: Validate ATLAS Documentation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: python scripts/validate_master_doc.py --mode=validate
```

**Setup time**: 10 minutes
**Benefit**: Automatic validation on every PR

### Option C: Manual Check (Minimum Viable)

Run manually before committing:

```bash
python scripts/validate_master_doc.py --mode=suggest
```

Review the suggestions and fix violations.

**Setup time**: 0 minutes
**Benefit**: Establishes validation habit; can evolve to hooks/CI

---

## Medium-Term Maintenance (Ongoing)

### When You Update a Concept

If you change something like the T1.5 count or credence formula:

1. **Make the change** in the PART_*.md file
2. **Update the manifest**:
   ```bash
   # Edit docs/master_doc_parts/DEPENDENCY_MANIFEST.json
   # Update: canonical_value, last_updated, add to update_history
   ```
3. **Run validation** to find affected sections:
   ```bash
   python scripts/validate_master_doc.py --mode=report
   ```
4. **Review and update** dependent sections (validator will tell you which ones)
5. **Commit** with message noting all affected sections:
   ```bash
   git commit -m "§34: T1.5 count 12→13; review §35, §40, §54, §78, §100, §115, §142, §147"
   ```

### When You Add a New Concept

1. **Write the section** in PART_*.md
2. **Add to manifest** under `concepts`:
   - Set `defined_in` to your section number
   - Set `canonical_value` to the actual value
   - Add entry to `update_history`
   - Leave `used_in` empty initially
3. **Run validation** to verify no errors:
   ```bash
   python scripts/validate_master_doc.py --mode=validate
   ```
4. **Commit both markdown and manifest**

### When You Use an Existing Concept

The validator will track it automatically. Just make sure you match the canonical value.

**Example**: If you write about T1.5 theories, say "13 T1.5 theories" (not 10, 12, or any other number).

---

## Long-Term Vision (This Year)

### Phase 2: Concept Genealogy
Extend manifest to show concept evolution over time:

```json
"T1_5_COUNT": {
  "genealogy": "T1.5 taxonomy: 4 (initial, 2025-08) → 10 (first refinement, 2025-11) → 12 (consolidation, 2026-01) → 13 (final, 2026-02). Settled as of 2026-02-27."
}
```

### Phase 3: Cross-Repo Dependencies
Track dependencies between ATLAS master doc and implementation code:

```json
"CREDENCE_FORMULA_LOGODDS": {
  "implementation": "web_of_belief.py:compute_credence()",
  "tests": "tests/test_credence_projection.py"
}
```

Validator would check that code matches documentation.

### Phase 4: Panelist Integration
Link decisions to expert panel sessions:

```json
"WARRANT_TYPES": {
  "calibrated_by": ["Mayo", "Illari", "Woodward", "Cartwright", "Stegenga"],
  "panel_session": "EXPERT_PANEL_MECHANISM_VS_EVIDENCE_2026-03-01.md"
}
```

### Phase 5: Interactive Queries
Build a query interface:
```bash
# Show me all sections using warrant types
python scripts/smart_book_query.py --concept=WARRANT_TYPES --mode=uses

# List all changes in the last 30 days
python scripts/smart_book_query.py --since=2026-02-01 --sort=date

# Generate a consistency audit for panel review
python scripts/smart_book_audit.py --panel=philosophy --format=pdf
```

---

## Common Scenarios

### Scenario 1: "I Updated T1.5 Count from 12 to 13"

```bash
# 1. Edit docs/master_doc_parts/PART_II_THEORETICAL.md (§34)
#    Change "12 T1.5 theories" to "13 T1.5 theories"

# 2. Edit docs/master_doc_parts/DEPENDENCY_MANIFEST.json
#    In concepts.T1_5_COUNT:
#    - canonical_value: 13 (was 12)
#    - last_updated: "2026-03-03"
#    - add to update_history: {"value": 13, "date": "2026-03-03", "context": "..."}

# 3. Run validator
python scripts/validate_master_doc.py --mode=report

# 4. Manually check flagged sections: §35, §40, §54, §78, §100, §115, §142, §147
#    (Validator will list them)

# 5. Update any sections that mention the count with the new value

# 6. Commit
git add docs/master_doc_parts/PART_II_THEORETICAL.md
git add docs/master_doc_parts/DEPENDENCY_MANIFEST.json
git add [any other sections updated]
git commit -m "§34: T1.5 count 12→13; updated §35, §40, §54, §78, §100, §115, §142, §147"
```

### Scenario 2: "I Found a New Warrant Type"

```bash
# 1. Write the new section (e.g., §48B: "New Warrant Type: COMPOSITIONAL")

# 2. Update manifest
#    In concepts.WARRANT_TYPES:
#    - count: 8 (was 7)
#    - values: add new entry with name and transfer_reliability
#    - last_updated: "2026-03-03"
#    - add to update_history

# 3. Run validator
python scripts/validate_master_doc.py --mode=validate

# 4. Check if other sections need updating
python scripts/validate_master_doc.py --mode=report

# 5. Commit
git add docs/master_doc_parts/PART_IV_CREDENCE.md
git add docs/master_doc_parts/DEPENDENCY_MANIFEST.json
git commit -m "§48: Added COMPOSITIONAL warrant type (d=0.70); updated §48.1"
```

### Scenario 3: "Legacy Formula Still Appears in Sections 54–78"

This is expected and documented. The sections predate the transition to log-odds formalism. See SMART_BOOK_README.md section "When Superseding a Concept."

If you want to update these sections:

```bash
# 1. For each section using legacy formula:
#    - Option A: Update to use new log-odds formula
#    - Option B: Add explicit note: "This section uses the legacy three-factor formula (see §48 for transition notes)"

# 2. Update manifest to confirm which sections you've updated
#    In concepts.CREDENCE_FORMULA_LEGACY.used_in: remove sections you've updated

# 3. Run validator to confirm no violations
python scripts/validate_master_doc.py --mode=validate

# 4. Commit with clear message:
git commit -m "§54–§78: Updated to reference new log-odds credence formula (§48)"
```

---

## Troubleshooting

### "Validator says I have a violation but I don't"

Check the regex pattern in `DEPENDENCY_MANIFEST.json`. It might be matching something you didn't intend.

**Fix**: Update the pattern or adjust your wording to avoid false matches.

**Example**: If validator flags "121 T1.5 theories" as a mismatch, the pattern needs a word boundary: `\b(\d+)\s+T1\.5\s+theor` instead of `(\d+)\s+T1\.5\s+theor`

### "Validator can't find a concept I know exists"

The concept might not be in the manifest yet.

**Fix**: Add it to `DEPENDENCY_MANIFEST.json` under `concepts`.

### "I want to update the manifest but don't know the section numbers"

Run a quick search:

```bash
grep -n "T1\.5" docs/master_doc_parts/PART_*.md | head -20
```

This shows all mentions of "T1.5" with line numbers and filenames.

### "Pre-commit hook is blocking my commit"

Run the validator to see what's wrong:

```bash
python scripts/validate_master_doc.py --mode=report
```

Fix the violations, then try committing again.

---

## Files Changed & Locations

### Design & Documentation

```
docs/
├── SMART_BOOK_DESIGN_2026-03-03.md          ← Design document (precedents, architecture)
├── SMART_BOOK_README.md                     ← User guide
└── SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md  ← This file
```

### Machine-Readable Manifest

```
docs/master_doc_parts/
└── DEPENDENCY_MANIFEST.json                 ← Core dependency specification
```

### Validator Script

```
scripts/
└── validate_master_doc.py                   ← Executable Python validator
```

---

## Success Metrics

After integrating Smart Book, you should see:

✓ **Immediate (week 1)**:
- Validator runs without errors
- All CRITICAL violations identified and reviewed
- Team understands concept dependencies

✓ **Short-term (month 1)**:
- Pre-commit hook or CI/CD integration active
- No commits with consistency violations
- Developers know to run validator before committing

✓ **Medium-term (quarter 1)**:
- Zero consistency violations in validation reports
- Concept update workflow well-established
- Manifest evolves with document (updated on each relevant change)

✓ **Long-term (ongoing)**:
- Documentation is self-consistent and trustworthy
- Changes to foundational concepts automatically propagate
- Expert panels can review decision history through manifest genealogy

---

## Questions?

Refer to:
- **Design rationale**: SMART_BOOK_DESIGN_2026-03-03.md
- **How to use**: SMART_BOOK_README.md
- **Integration setup**: This file (SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md)

---

**Status**: Ready for Implementation
**Next Step**: Choose integration path (pre-commit hook, CI/CD, or manual) and begin using validator
**Maintenance**: Update manifest whenever you change a concept; run validator before each commit
