# Task Completion Report: Reflex Fixes + Extraction Tiers

**Date**: 2026-03-01
**Session**: Parallel execution of two independent quality assurance tasks
**Status**: COMPLETE

---

## Summary

Two task groups executed in parallel with real extraction data:

1. **Task 1 (Reflex Fixes)**: Applied auto-fixable reflexes across all 1,065 extraction files
   - Scanned all files for direction normalization, empty findings, malformed JSON
   - Result: 0 modifications needed (extraction data already clean)
   - 59 files flagged with empty findings (automatic Tier 1 candidates)

2. **Task 2 (Extraction Scoring + Tiering)**: Scored 1,061 articles using practical quality metrics
   - Generated three tier files for strategic re-extraction decisions
   - Tier 1: 59 articles (5.6%) — empty extractions, need full re-extraction
   - Tier 2: 2 articles (0.2%) — vague antecedents, need surgical LLM fixes
   - Tier 3: 1,000 articles (94.3%) — solid quality, just add new fields

---

## Task 1: Apply Reflex Fixes

### Implementation

Created `/scripts/apply_reflex_fixes.py`:
- Loads all extraction files from `data/extractions/*.json`
- Runs DirectionNormalizationReflex: checks for non-canonical direction values
- Checks for empty findings arrays (flags for re-extraction)
- Detects null antecedents (flags for re-extraction)
- Identifies malformed JSON (quarantines to `data/extractions/quarantine/`)

### Results

```
REFLEX FIX REPORT
======================================================================
Total files scanned:           1,065
Total files modified:          0
Total files quarantined:       0

Fixes applied:
  - Direction values normalized: 0
  - Empty findings flagged:      59
  - Null antecedents flagged:    0
  - Malformed JSON quarantined:  0

Flagged issues (59):
  - empty_findings: 59
======================================================================
```

**Finding**: Extraction data is clean — no malformed JSON, no non-canonical directions, no null antecedents. All 59 files flagged have legitimately zero findings extracted (true data quality signal, not corruption).

---

## Task 2: Score Extractions + Identify Re-extraction Tiers

### Implementation

Created `/scripts/identify_reextraction_tiers.py`:

**Scoring System** (base score 1.0, deduct penalties):
- No findings at all: automatic Tier 1
- Null/missing antecedent: -0.20
- Vague antecedent patterns ("the environment", "the condition"): -0.20
- Non-canonical direction: -0.15
- Missing sample_size on empirical findings: -0.10
- Very short antecedent (<10 chars): -0.10
- No theory_links across all findings: -0.05

**Tier Thresholds**:
- Tier 1 (< 0.65): Full re-extraction needed
- Tier 2 (0.65-0.85): Surgical LLM fixes for targeted issues
- Tier 3 (> 0.85): Just add new fields, no major re-extraction

### Results

```
EXTRACTION SCORING REPORT
======================================================================
Total articles scored:         1061

Tier Distribution:
  Tier 1 (< 0.65, need re-extraction):      59 articles (  5.6%)
  Tier 2 (0.65-0.85, surgical fixes):        2 articles (  0.2%)
  Tier 3 (> 0.85, add new fields):        1000 articles ( 94.3%)

Score Statistics:
  Mean score:                  0.9421
  Median score:                1.0000
  Std dev:                     0.2292

Mean Score by Tier:
  Tier 1: 0.0000
  Tier 2: 0.7750
  Tier 3: 0.9980

Top Issues Across All Articles:
  No findings extracted:   59 articles
  No theory_links in any finding:   20 articles
  Very short antecedent:   10 articles
  Antecedent contains vague language:    2 articles
======================================================================
```

### Output Files

Three tier stratification files written to `data/field_discovery/`:

1. **tier1_reextract.json** (59 articles, 11 KB)
   - All have n_findings == 0
   - Pure re-extraction candidates
   - Example: 10.1007_s10339-021-01043-4.json

2. **tier2_surgical.json** (2 articles, 631 bytes)
   - Score 0.75-0.80 with specific fixable issues
   - Dichotomic_Reciprocity... (vague antecedent + missing theory_links)
   - 10.1093_oxfordhb_9780198735410.013.10 (vague antecedent)

3. **tier3_ok.json** (1,000 articles, 159 KB)
   - Score ≥ 0.85 (mean 0.9980)
   - Ready for field addition pass
   - Examples: 10.1016_j.respol.2007.09.006 (score 0.9, 41 findings), 10.1037_0033-295x.110.1.145 (score 0.9, 7 findings)

---

## Key Insights

### Extraction Quality is Strong

- **94.3% of articles** (1,000/1,061) have quality scores ≥ 0.85
- Mean score across corpus: 0.9421 (very high)
- No systemic issues with direction normalization or antecedent vagueness
- Only 59 articles need full re-extraction (all have zero findings)

### Tier 1 (Re-extraction) is Well-Defined

- 59 articles with n_findings == 0
- These are the only Tier 1 candidates
- Likely cases: articles that are methodological papers, reviews without specific claims, or LLM extraction failures
- Clear action: run extraction pipeline again with prompts tuned to these article types

### Tier 2 (Surgical) is Minimal

- Only 2 articles (0.2%)
- Both have vague antecedents but otherwise solid (20+ findings each)
- Easy fix: targeted LLM pass to rephrase antecedents
- One also missing theory_links — simple backfill operation

### Tier 3 (Add Fields) is Actionable

- 1,000 articles ready for next phase
- No major quality issues blocking field addition
- Current work (pass_a/b/c antecedent/sample_size/theory linking) is well-justified

---

## Files Generated

| File | Size | Purpose |
|------|------|---------|
| `scripts/apply_reflex_fixes.py` | 180 lines | Auto-fix local reflexes across corpus |
| `scripts/identify_reextraction_tiers.py` | 310 lines | Score extractions + stratify into tiers |
| `data/field_discovery/tier1_reextract.json` | 11 KB | 59 empty extractions |
| `data/field_discovery/tier2_surgical.json` | 631 B | 2 articles needing surgical fixes |
| `data/field_discovery/tier3_ok.json` | 159 KB | 1,000 ready articles |

---

## Next Steps

1. **Tier 1 (59 articles)**: Queue for full re-extraction with updated prompts
   - Focus on methodological papers, reviews, meta-analyses
   - Consider article type detection in extraction prompts

2. **Tier 2 (2 articles)**: Single-pass LLM fix
   - Rephrase vague antecedents (keep findings, refine language)
   - Backfill missing theory_links if possible

3. **Tier 3 (1,000 articles)**: Continue current field addition work
   - Pass A/B/C (antecedent, sample_size, theory_linking) can proceed
   - Use tier3_ok.json as reference set for sampling

---

## Quality Assurance

- **Code review**: Both scripts handle edge cases (non-dict files, JSON errors, missing fields)
- **Data validation**: All 1,065 files scanned, 4 non-extraction files skipped (batch logs)
- **Reproducibility**: Scoring algorithm fully documented with penalty system explicit
- **Tests run**: Manual verification of tier file structure and sample entries

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Total files scanned | 1,065 |
| Valid extraction files | 1,061 |
| Files with malformed JSON | 0 |
| Files with non-canonical directions | 0 |
| Files modified by reflexes | 0 |
| Tier 1 articles | 59 |
| Tier 2 articles | 2 |
| Tier 3 articles | 1,000 |
| Mean article score | 0.9421 |
| Median article score | 1.0000 |
| Max score | 1.0 |
| Min score (Tier 1) | 0.0 |

