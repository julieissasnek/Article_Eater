# START HERE: Extraction Field Quality Framework

**Framework Version**: 1.0  
**Date**: 2026-02-28  
**Status**: Specification Complete, Ready for Implementation

---

## What Was Delivered

A comprehensive **Extraction Field Quality Framework** for the Article_Eater extraction pipeline.

**Problem**: Quality audit of 1,043 extraction files revealed systematic noise:
- Direction field has 169 unique values (should be 4)
- Direction ↔ effect_size mismatches in 2.3% of findings
- Vague antecedents in 32% of articles
- Mean article quality score: 0.722 (moderate problems across the board)

**Solution**: Five companion documents defining detection, scoring, cleanup, re-extraction, and ongoing maintenance.

---

## 5 Documents (123 KB Total)

### 1. EXTRACTION_QUALITY_BRIEFING_2026-02-28.md (11 KB) ⭐ Start here
**For**: David Kirsh, Project Stakeholders  
**Read Time**: 5-10 minutes  
**Contains**: Problem statement, solution overview, key design decisions, next steps, FAQ

**Action**: Read this first to understand what was built and why.

---

### 2. EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md (56 KB) ⭐ Technical reference
**For**: Engineers, Domain Experts, Panel Reviewers  
**Read Time**: 45-60 minutes  
**Contains**: Complete specification with 10 parts

**Parts**:
- Part 1: Success conditions for 11 fields (antecedent, consequent, direction, etc.)
- Part 2: Field-level quality scoring
- Part 3: Finding and article-level scores
- Part 4: Quality action logic (accept/flag/requeue/reject)
- Part 5: Re-extraction pipeline
- Part 6: Metrics dashboard
- Part 7: Overseer integration
- Part 8: Machine-readable rules
- Part 9: Decision log (3 key decisions for panel review)
- Part 10: Open questions (Q1-Q5)

**Action**: Read Part 9-10 before panel review. Reference Part 1-3 when implementing.

---

### 3. EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md (14 KB) ⭐ Implementation plan
**For**: Engineers, Project Managers  
**Read Time**: 20-30 minutes  
**Contains**: 7-phase implementation plan, 6-7 weeks

**Phases**:
1. QA validation module (Weeks 1-2)
2. Nightly QA scan / Overseer integration (Weeks 2-3)
3. Re-extraction pipeline (Weeks 3-4)
4. Metrics dashboard (Week 4)
5. Gold standard validation (Weeks 4-5)
6. Panel review (Weeks 5-6)
7. Ongoing operations (Week 6+)

Each phase has acceptance criteria, dependencies, and resource requirements.

**Action**: Follow this roadmap phase-by-phase after framework approval.

---

### 4. contracts/schemas/extraction_quality_rules.json (31 KB) ⭐ Machine-readable rules
**For**: Engineers (code consumption)  
**Format**: JSON  
**Contains**: 50+ validation rules in machine-readable format

**Includes**:
- Rule definitions (type, severity, error messages)
- Quality scoring weights
- Quality gates (system invariants)
- Panel review questions

**Action**: Load this in Python code. No rule hardcoding needed.

---

### 5. EXTRACTION_QUALITY_FRAMEWORK_INDEX_2026-02-28.md (11 KB) ⭐ Navigation guide
**For**: Anyone navigating the framework  
**Read Time**: 5-10 minutes  
**Contains**: Document descriptions, cross-references, use scenarios

**Use Scenarios**:
1. "I'm new to the project" → Read Briefing + Framework Part 1
2. "I'm implementing the validator" → Read Roadmap Phase 1 + Framework Parts 1-3
3. "I'm on the panel" → Read Briefing + Framework Parts 9-10
4. "I'm writing the dashboard" → Read Roadmap Phase 4 + Framework Part 6
5. "I need the scoring algorithm" → Read Briefing + Framework Parts 2-3

**Action**: Use this guide to find what you need quickly.

---

## Quick Facts

| Aspect | Details |
|--------|---------|
| **Fields Covered** | 11 (antecedent, consequent, direction, claim_type, measure_type, p_value, effect_size, effect_size_type, sample_size, confidence_interval, test_statistic) |
| **Validation Rules** | 50+ rules across all fields |
| **Quality Levels** | 4 (field, finding, article, system) |
| **Implementation Time** | 6-7 weeks (7 phases) |
| **Success Metrics** | Quality score: 0.72 → 0.80+; Vague antecedents: 32% → <10% |
| **Current Issues** | Direction chaos (169 values), vague antecedents (32%), effect_size mismatches (2.3%) |
| **Root Cause** | Extraction prompt under-constraining fields |
| **Panel Review** | Recommended mid-April, 90 minutes, 5 open questions |

---

## Three Key Decisions (For Panel)

### D1: Quality Score Weighting
**Critical fields** (antecedent, consequent, direction) = weight 3  
**Empirical fields** (p_value, effect_size, sample_size) = weight 2  
**Supporting fields** (measure_type, CI, test_stat) = weight 1

**Rationale**: Semantic core (antecedent/consequent/direction) must be perfect. Statistics are important but secondary.

---

### D2: Direction Normalization
**Current**: 169 unique values (increase, enhance, facilitate, modulate, etc.)  
**Proposed**: 4 canonical values (increase, decrease, no_effect, mixed)

**Rationale**: The 169 values are linguistic variation, not semantic difference. Constraining Gemini to 4 values eliminates noise without losing information.

---

### D3: Mixed Direction + Numeric Effect Size = Error
**Finding**: 31 cases where direction="mixed" AND effect_size is numeric (e.g., d=0.45)  
**Problem**: Contradiction (mixed = effect varies by condition; can't report single ES)

**Decision**: Flag as error, not warning. Forces explicit choice (separate findings, or mixed with null ES, or one direction with caveats).

---

## Next Steps

### For David Kirsh (Decision Maker)

1. **Read** EXTRACTION_QUALITY_BRIEFING_2026-02-28.md (5 min)
2. **Decide**: Approve framework or request changes?
3. **If approved**: Assign engineer for Phase 1 implementation
4. **Schedule**: Panel review for mid-April (90 min)

### For Engineers (Implementation)

1. **Read** EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md (20 min)
2. **Phase 1**: Build `src/qa/extraction_field_validator.py`
   - Load `extraction_quality_rules.json`
   - Implement 50+ validation rules
   - Write tests
3. **Phase 2-7**: Follow roadmap sequentially
4. **Sync** with David weekly

### For Panel Reviewers (mid-April)

1. **Read** EXTRACTION_QUALITY_BRIEFING (5 min, context)
2. **Read** EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 9 (15 min, decisions)
3. **Read** EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 10 (5 min, open questions)
4. **Attend** 90-min panel session
5. **Discuss** Q1-Q5, provide feedback

---

## Document Map

```
START_HERE (this file)
  ├─ EXTRACTION_QUALITY_BRIEFING (executive summary)
  ├─ EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP (phases 1-7)
  ├─ EXTRACTION_FIELD_QUALITY_FRAMEWORK (full specification)
  ├─ extraction_quality_rules.json (machine-readable rules)
  └─ EXTRACTION_QUALITY_FRAMEWORK_INDEX (navigation guide)
```

**Recommended Reading Order**:
1. This file (context)
2. EXTRACTION_QUALITY_BRIEFING (problem & solution)
3. EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 9-10 (decisions & questions)
4. EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP (if implementing)
5. EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 1-8 (for details)

---

## Key Deliverables Summary

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| EXTRACTION_QUALITY_BRIEFING | 11 KB | 291 | Executive summary |
| EXTRACTION_FIELD_QUALITY_FRAMEWORK | 56 KB | 1,434 | Complete specification |
| EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP | 14 KB | 429 | Implementation plan |
| extraction_quality_rules.json | 31 KB | 909 | Machine-readable rules |
| EXTRACTION_QUALITY_FRAMEWORK_INDEX | 11 KB | 290 | Navigation guide |
| **TOTAL** | **123 KB** | **3,353** | **All deliverables** |

---

## Framework Status

**Specification Phase**: ✓ COMPLETE

✓ Problem analysis  
✓ Solution design  
✓ Success conditions defined  
✓ 50+ validation rules  
✓ Scoring system  
✓ Cleanup pipeline  
✓ Dashboard specification  
✓ Overseer integration plan  
✓ Implementation roadmap  
✓ Decision log  
✓ Open questions for panel  

**Ready For**: Implementation or Expert Panel Review

**Not Yet Done**: Code implementation (Phase 1-7 per roadmap)

---

## Contact

**Framework Design**: Claude Opus (Anthropic)  
**Review/Approval**: David Kirsh (Professor, UCSD)  
**Panel Review**: Expert panel (P-TC) — pending  
**Implementation Lead**: [Engineer TBD]  

---

## Questions?

**Q: Where do I start?**  
A: Read EXTRACTION_QUALITY_BRIEFING (this is the shortest, most accessible intro).

**Q: I need implementation details.**  
A: Read EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP.

**Q: I'm a panel reviewer.**  
A: Read Framework Part 9-10 (decisions & open questions).

**Q: I'm implementing the validator.**  
A: Read Framework Parts 1-3 and load extraction_quality_rules.json in your code.

**Q: What exactly is being built?**  
A: A system to detect extraction quality issues, automatically re-extract with targeted prompts, and maintain quality over time. All automated (nightly QA, weekly re-extraction, monthly reviews).

---

**Last Updated**: 2026-02-28  
**Version**: 1.0  
**Status**: Ready for Implementation

