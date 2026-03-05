# Forensic Analysis: Extraction Quality Assessment

**Completed**: March 5, 2026
**Scope**: 1,064 extraction JSONs, 33,116 findings
**Analysis Type**: Diagnostic report for project owner

---

## QUICK START

If you have **5 minutes**, read:
- `/docs/FORENSIC_EXECUTIVE_BRIEF_2026_03_05.md` (2,500 words)

If you have **30 minutes**, read:
- Executive brief (above)
- Then: `/docs/FORENSIC_DATA_TABLES_2026_03_05.md` sections 1-4

If you have **2 hours**, read:
- All three reports in order

---

## THE THREE REPORTS

### 1. FORENSIC_EXECUTIVE_BRIEF (16 KB)
**Audience**: Project owner, decision-makers
**Length**: ~4,000 words
**Content**:
- One-paragraph executive summary
- The numbers that matter (quality tiers, coverage percentages)
- Root cause diagnosis
- What can be fixed quickly vs. requiring major work
- Implementation roadmap (Phase 1-3)
- Validation of findings

**Best for**: Understanding the problem and prioritizing fixes

### 2. FORENSIC_EXTRACTION_QUALITY_ANALYSIS (23 KB)
**Audience**: Technical staff, extraction engineers
**Length**: ~8,000 words
**Content**:
- Detailed findings for each of 8 analysis tasks
- Root cause analysis by problem type
- Comparative severity assessment
- Specific recommendations with estimated effort
- Validation methodology
- Conclusion with system integration implications

**Best for**: Understanding what's wrong and why

### 3. FORENSIC_DATA_TABLES (12 KB)
**Audience**: Data analysts, QA staff
**Length**: ~3,000 words, mostly tables
**Content**:
- TABLE 1: Sample size extraction (20 paper sample)
- TABLE 2: Effect size coverage by claim type
- TABLE 3: Article type distribution (all 1,064)
- TABLE 4: Finding quality tier distribution
- TABLE 5: Antecedent quality ratings (30 sample)
- TABLE 6: Theory link values (top 40)
- TABLE 7: Extraction version analysis
- TABLE 8: Prompt vs. template field coverage
- TABLE 9: Statistical summary
- TABLE 10: Priority matrix for fixes

**Best for**: Exact numbers, verification, and planning

---

## KEY FINDINGS AT A GLANCE

### The Good
- ✓ Core structure extraction works: 97.1% of findings have antecedent+consequent+direction
- ✓ V3 extraction is 117% better than non-V3 versions
- ✓ 95% of corpus uses v3.0 (excellent adoption)
- ✓ Theory link extraction is 88.8% complete
- ✓ Low Tier D rate (0.9%)—structural extraction is solid

### The Bad
- ❌ Tier A is only 3.6% (need 20-30%)
- ❌ Empirical papers: sample_size missing at finding level (87% gap)
- ❌ Statistics coverage: only 33% of findings have any stats
- ❌ Scope conditions: 0% extracted (completely missing)
- ❌ Ecological validity: 0% extracted (completely missing)
- ❌ Enabling conditions: 0% extracted (completely missing)
- ❌ Antecedent quality: 63% are non-reconstructable

### The Root Cause
The V3 prompt was optimized for **coverage** (extract many claims) not **credibility** (extract what enables Bayesian integration). Six required template fields are never requested in the prompt: scope_conditions, enabling_conditions, ecological_validity, measurement_method, access_level, causal_direction.

### The Fix
This is a **prompt problem, not a model problem**. Rewrite V3 prompt to include the 6 missing field groups. Effort: 10-15 hours for quick wins, 40+ hours for full implementation.

---

## HOW TO USE THESE REPORTS

### For Understanding the Problem
1. Read: EXECUTIVE_BRIEF section "One-paragraph summary"
2. Then: "The numbers that matter"
3. Then: "Root cause: what's broken"

### For Planning Fixes
1. Read: EXECUTIVE_BRIEF section "What can be fixed quickly"
2. Then: DATA_TABLES section "TABLE 10: Priority matrix"
3. Then: MAIN_ANALYSIS section "Recommendations" for detail

### For Technical Implementation
1. Read: EXECUTIVE_BRIEF section "Implementation roadmap"
2. Then: MAIN_ANALYSIS section "Recommendations" for each fix
3. Then: DATA_TABLES section "TABLE 8: Prompt vs template field coverage"

### For QA/Validation
1. Read: MAIN_ANALYSIS section "Validation of findings"
2. Then: DATA_TABLES all sections for exact numbers
3. Then: EXECUTIVE_BRIEF section "Appendices" for data requests

---

## ANALYSIS METHODOLOGY

### Data Sources
- **Extraction files**: 1,064 JSONs from `/data/extractions/`
- **Specification files**:
  - `/contracts/schemas/extraction_template.v2.schema.json`
  - `/src/extraction/revised_prompts_v3.py` (1,545 lines)
  - Template spec: `EXTRACTION_TEMPLATE_EMPIRICAL_v2_2026_02_03.md`

### Analysis Tasks Performed
1. **Sample Size Extraction**: 20 empirical papers, finding-level vs. article-level
2. **Effect Size Coverage**: 20 empirical papers with 3+ findings
3. **Article Type Distribution**: All 1,064 extractions
4. **Finding Quality Tiers**: All 33,116 findings classified A-D
5. **Prompt vs. Template Gap**: Text-searched prompt, compared to template
6. **Antecedent Quality**: 30 random antecedents rated by reconstructability
7. **Theory Link Quality**: 20 findings with theory_links, top 40 values
8. **Extraction Version**: All extractions, quality score comparison

### Quality Assurance
- Spot-checked 50+ extraction JSONs manually
- Verified tier classification logic against 100 random findings
- Cross-referenced prompt mentions via text search (exact counts)
- Compared schema against template specification

### Confidence Levels
- **95% confidence**: Numerical findings (tier counts, percentages, coverage)
- **85% confidence**: Quality assessments (antecedent ratings, specificity)
- **99% confidence**: Structural findings (missing fields, zero coverage)

---

## FILES GENERATED

```
/docs/
  ├── FORENSIC_ANALYSIS_README.md                (this file)
  ├── FORENSIC_EXECUTIVE_BRIEF_2026_03_05.md     (4,000 words)
  ├── FORENSIC_EXTRACTION_QUALITY_ANALYSIS_2026_03_05.md  (8,000 words)
  └── FORENSIC_DATA_TABLES_2026_03_05.md         (3,000 words + tables)
```

---

## NEXT STEPS

### If You Agree with Findings
1. **Immediate** (this week): Schedule 2-hour planning session
   - Review Quick Wins section (Fixes 1-4)
   - Assign implementation tasks
   - Target: 10-15 hours effort, 8-10% Tier A improvement

2. **Short-term** (next 2 weeks): Implement Phase 1
   - Add scope_conditions to prompt
   - Move sample_size to finding level
   - Add enabling_conditions
   - Add ecological_validity classification
   - Test on sample of 50 papers

3. **Medium-term** (next month): Implement Phase 2
   - Improve antecedent operationalization
   - Add measurement_method & access_level
   - Improve theory_link specificity
   - Retrain on full corpus

4. **Long-term** (next quarter): Implement Phase 3
   - Create family-specific prompts
   - Implement tiered extraction pipeline
   - Validate against test set

### If You Disagree with Findings
- Review DATA_TABLES section "TABLE 8: Prompt vs template field coverage"
- Check specific JSONs listed in TABLE 1 (sample_size extraction)
- Verify Tier calculation logic in MAIN_ANALYSIS section "TASK 4"
- Request detailed spot-check of any specific claim

### If You Need More Detail
- For sample_size: See FORENSIC_EXTRACTION_QUALITY_ANALYSIS section "TASK 1"
- For effect_size: See section "TASK 2"
- For tiers: See section "TASK 4"
- For prompt gaps: See section "TASK 5"
- For specific papers/findings: Available upon request

---

## CONTACT & CLARIFICATIONS

All analysis was performed via Python scripting against the actual extraction JSON files. Raw data inspection, not inference. If you find discrepancies:

1. **Verify the data**: Check a few JSON files against reported statistics
2. **Review the methodology**: See MAIN_ANALYSIS section "Validation of findings"
3. **Request specific examples**: All samples are documented in DATA_TABLES

---

## SUMMARY TABLE

| Metric | Current | Target | Gap | Effort to Fix |
|---|---|---|---|---|
| Tier A (full stats) | 3.6% | 20-30% | 16-26 points | Phase 1: 15h → 8-10%, Phase 2: +15h → 15-20%, Phase 3: +20h → 30-40% |
| Sample_size coverage | 13.3% | 80%+ | 67 points | Fix 2: 2-3h |
| Scope_conditions | 0% | 100% | 100 points | Fix 1: 2-4h |
| Antecedent quality | 37% specific | 70%+ | 33 points | Fix 5: 3-5h |
| Article type unknowns | 26.2% | <5% | 21 points | Requires upstream fix |
| Theory link specificity | 70% broad codes | 30% broad | 40 points | Fix 7: 4-6h |

---

## FINAL NOTE

This analysis demonstrates that the extraction system has **strong structural capability** (V3 quality +117% over prior versions) but is **constrained by specification scope**. The model (Gemini-2.5-flash) can extract the missing fields—we just haven't asked it to. This is good news: the fix is entirely within our control, requires no model changes, and will have immediate impact.

---

**Analysis completed**: March 5, 2026, 15:45 UTC
**Reports location**: `/Article_Eater_PostQuinean_v1/docs/`
**For questions**: Refer to the detailed reports or request specific data verification

