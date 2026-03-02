# RV5-8 Audit: Action Items & Fixes

**Generated**: 2026-03-01
**Based on**: RV5_8_CONTRACTS_SCHEMAS_AUDIT_2026-03-01.md

---

## Priority 1: CRITICAL FIXES (Do today)

### Issue 1: Missing Error/Warning Messages in extraction_quality_rules.json

**File**: `/contracts/schemas/extraction_quality_rules.json`
**Severity**: HIGH
**Impact**: Validation failures produce no user feedback

**Rules requiring fixes** (8 total):

1. **SS3_N_IN_NARRATIVE** (Field: sample_size)
   - Location: Line ~100-120
   - Add field: `"warning_message"` or `"error_message"`
   - Suggested message: "Sample size inferred from narrative text; verify accuracy."

2. **SSS2_SOURCE_WITH_N** (Field: sample_size_source)
   - Add messaging for when source matches reported N value
   - Suggested message: "Verify that reported N value matches the identified source."

3. **SSS3_ESTIMATED_CONFIDENCE** (Field: sample_size_source)
   - Add messaging for confidence in estimated sample size
   - Suggested message: "Sample size is estimated; confidence level not high."

4. **SI2_FIGURE_REFERENCE** (Field: stimulus_images)
   - Add messaging for figure reference validation
   - Suggested message: "Figure reference format invalid or missing. Use format like 'Figure 2A' or 'Supplementary Figure S1'."

5. **MID1_VALID_FORMAT** (Field: molecule_ids)
   - Add messaging for format validation
   - Suggested message: "Molecule ID format invalid. Expected format: [A-Z0-9_]+"

6. **MID2_REGISTRY_CHECK** (Field: molecule_ids)
   - Add messaging for registry validation
   - Suggested message: "Molecule ID not found in rasa_attractors registry. Verify ID exists."

7. **IU4_RELIABILITY_REPORTED** (Field: instruments_used)
   - Add messaging for reliability metrics
   - Suggested message: "Instrument reliability (Cronbach's alpha, test-retest) should be reported for this instrument."

8. **TS4_NULL_WITH_DATA** (Field: test_statistic)
   - Add messaging for missing test statistics
   - Suggested message: "Test statistic expected but null. Provide t, F, χ², or other statistic value."

**Action**:
```bash
# Edit /contracts/schemas/extraction_quality_rules.json
# For each rule listed above, add:
"error_message": "Your message here"
# or
"warning_message": "Your message here"
# (depending on severity level)
```

**Estimated time**: 10 minutes
**Complexity**: LOW (search & add text)

---

### Issue 2: InstrumentUsed.construct_measured should be required

**File**: `/contracts/schemas/extraction_template.v2.schema.json`
**Severity**: MEDIUM
**Impact**: Semantic correctness; allows null construct_measured

**Current state** (line ~716-732):
```json
"InstrumentUsed": {
  "type": "object",
  "required": ["name"],
  "properties": {
    ...
    "construct_measured": {
      "type": "string",
      "description": "What psychological/physiological construct..."
    },
    ...
  }
}
```

**Fix**: Add "construct_measured" to required array

```json
"InstrumentUsed": {
  "type": "object",
  "required": ["name", "construct_measured"],
  "properties": {
    ...
  }
}
```

**Rationale**: Every measurement instrument measures some construct; this should never be null.

**Estimated time**: 2 minutes
**Complexity**: LOW (one-line change)

---

## Priority 2: DATA CLEANUP (Do this week)

### Issue 3: Instrument year anomalies

**File**: `/contracts/instruments/instruments_registry.json`
**Severity**: LOW
**Impact**: Data integrity; metadata accuracy

**Problems**:
1. GONOGO: year = 1868 (instrument not invented until ~1960s)
2. EMG: year = 1850 (electrodes/EMG methodology not developed until ~1950s)

**Action**:
1. Look up accurate development/publication year for each
2. Update the year field with correct value
3. Add inline comment if historical context is important

**Example**:
```json
{
  "instrument_id": "GONOGO",
  ...
  "year": 1966,  // Updated from 1868 (Donders & Kessen original work)
  ...
}
```

**Estimated time**: 15 minutes (research + update)
**Complexity**: LOW (requires external source verification)

---

## Priority 3: TESTING & VALIDATION (This sprint)

### Issue 4: Test extraction_quality_rules coverage

**Action**: Verify all 68 rules execute without error when applied to test data
- Run validation pipeline with sample findings
- Ensure all error/warning messages appear correctly in logs
- Test edge cases for each rule type

**Estimated time**: 30 minutes
**Complexity**: MEDIUM

---

## Priority 4: DOCUMENTATION (Optional but recommended)

### Issue 5: Document ID naming conventions

**Current inconsistency**:
- instruments use `instrument_id`
- outcomes use `term_id`
- template schema uses `id`
- rules use `rule_id`

**Recommendation**: Add note to `CLAUDE.md` or create ID_NAMING_CONVENTIONS.md documenting why different fields use different key names.

**Estimated time**: 10 minutes
**Complexity**: LOW

---

## Checklist for Completion

```
Priority 1 Fixes:
[ ] Add error/warning messages to 8 quality rules in extraction_quality_rules.json
[ ] Make construct_measured required in extraction_template.v2.schema.json
[ ] Commit changes with message "RV5-8: Fix quality rule messages and InstrumentUsed schema"

Priority 2 Cleanup:
[ ] Review and correct GONOGO year
[ ] Review and correct EMG year
[ ] Commit with message "RV5-8: Correct instrument development years"

Priority 3 Testing:
[ ] Run validation on sample extraction with all 68 rules
[ ] Verify no null error messages appear
[ ] Log results to test_results.md

Priority 4 Documentation:
[ ] Add section to docs about ID naming conventions
```

---

## File Locations for Quick Reference

| Task | File | Line(s) |
|------|------|---------|
| Fix quality rule messages | `/contracts/schemas/extraction_quality_rules.json` | ~100-1000+ |
| Fix InstrumentUsed schema | `/contracts/schemas/extraction_template.v2.schema.json` | ~716-732 |
| Fix GONOGO year | `/contracts/instruments/instruments_registry.json` | Search "GONOGO" |
| Fix EMG year | `/contracts/instruments/instruments_registry.json` | Search "EMG" |

---

## Overall Impact Assessment

**Total issues**: 11
- Critical: 0 (system works fine)
- High: 8 (quick fix)
- Medium: 1 (quick fix)
- Low: 2 (data cleanup)

**Time to fix all**: ~60 minutes total
**Breaking changes after fix**: NONE
**System remains operational**: YES

---

## Sign-Off

Audit completed: 2026-03-01
Auditor: Claude Code (Haiku 4.5)
Status: READY FOR FIXES
