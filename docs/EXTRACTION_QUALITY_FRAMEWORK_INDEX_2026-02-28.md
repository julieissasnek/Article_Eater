# Extraction Field Quality Framework — Document Index

**Framework Version**: 1.0
**Generated**: 2026-02-28
**Status**: Specification Complete, Ready for Implementation

---

## Quick Links

**Start Here**:
→ **EXTRACTION_QUALITY_BRIEFING_2026-02-28.md** (5 min read)

**For Implementation**:
→ **EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md** (15 min read)

**For Technical Review**:
→ **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** (45 min read)

**Machine-Readable Rules**:
→ **contracts/schemas/extraction_quality_rules.json** (30 KB)

---

## Document Descriptions

### 1. EXTRACTION_QUALITY_BRIEFING_2026-02-28.md

**Audience**: David Kirsh, Project Stakeholders
**Length**: ~291 lines (5-10 min read)
**Purpose**: Executive summary and decision brief

**Contains**:
- Problem statement (audit findings, root causes)
- Solution overview (3 companion documents)
- Key design decisions (D1-D3) with rationale and risks
- Current quality metrics
- Immediate next steps
- FAQ

**Why Read This First**: Sets context and clarifies what was delivered.

---

### 2. EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md

**Audience**: Engineers, Domain Experts, Panel Reviewers
**Length**: ~1,434 lines (45-60 min read)
**Purpose**: Complete specification of validation rules, scoring system, and cleanup pipeline

**Contains (10 Parts)**:

**Part 1: Success Conditions for Each Field** (11 fields)
- Antecedent (stimulus/IV description)
- Consequent (outcome/DV description)
- Direction (effect direction)
- Claim type (classification)
- Measure type (how measured)
- P-value (statistical significance)
- Effect size (magnitude)
- Effect size type (name of statistic)
- Sample size (N)
- Confidence interval (CI)
- Test statistic (name and value)

Each field section includes:
- What "good" looks like (clear criteria)
- What "bad" looks like (failure modes from audit)
- Validation rules (pseudocode)
- Severity level (critical/error/warning/info)
- APA relevance (reporting standards)

**Part 2: Field-Level Quality Scoring System**
- Per-field score computation
- Score ranges (1.0, 0.7, 0.3, 0.0)
- Error vs. warning distinction

**Part 3: Finding & Article-Level Scores**
- Finding-level: weighted mean of field scores
- Article-level: median of finding scores

**Part 4: Quality Action Logic**
- Thresholds: accept (0.9+), flag (0.75-0.89), requeue (0.5-0.74), reject (<0.5)
- Recommendation system

**Part 5: Re-extraction Pipeline**
- Detection phase (nightly QA scan)
- Flagging phase (requeue queue)
- Scheduling phase (batch processing)
- Field-specific prompts (targeted re-extraction)
- Verification phase (improvement assessment)

**Part 6: Quality Metrics Dashboard**
- System-level metrics (distribution, trends)
- Field-level issues (breakdown by field)
- Action recommendations

**Part 7: Overseer Integration**
- New QA_QUALITY_GATE stage
- New invariants (quality gates)

**Part 8: Machine-Readable Validation Rules**
- References extraction_quality_rules.json

**Part 9: Decision Log for Panel Review**
- 3 key decisions with alternatives, rationale, risk, panelist concerns
- Focus on: weighting, direction normalization, mixed direction handling

**Part 10: Open Questions for Panel**
- Q1: Antecedent specificity (relative vs. absolute?)
- Q2: Mixed direction findings (separate or flag?)
- Q3: Effect size / direction tolerance (rounding considerations)
- Q4: P-value mandatoriness (APA compliance vs. pragmatism)
- Q5: Claim atomicity (multi-outcome claims)

**Why Read This**: This is the authoritative technical specification. Read if implementing the framework or participating in panel review.

---

### 3. EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md

**Audience**: Engineers, Project Managers
**Length**: ~429 lines (20-30 min read)
**Purpose**: Step-by-step implementation plan with phases, deliverables, acceptance criteria

**Contains (7 Phases + Appendix)**:

**Phase 1: QA Validation Module** (Week 1-2)
- File: `src/qa/extraction_field_validator.py`
- Load rules from JSON, validate findings
- Acceptance: 50+ rules tested, <2s for 1K articles

**Phase 2: Nightly QA Scan** (Week 2-3)
- File: `src/overseer/qa_quality_gate.py`
- Integrate with Overseer scheduling
- Acceptance: Scan 1K articles in <5 min, accurate requeue list

**Phase 3: Re-extraction Pipeline** (Week 3-4)
- File: `src/overseer/reextraction_scheduler.py`
- Batch processing, field-specific prompts
- Acceptance: Re-extract 100+ articles, 80%+ improve

**Phase 4: Metrics Dashboard** (Week 4)
- Streamlit-based quality visualization
- Distribution, trends, field breakdown, alerts
- Acceptance: <2s load, all metrics correct

**Phase 5: Gold Standard Validation** (Week 4-5)
- Test framework against manually verified papers
- Acceptance: Gold std score ≥0.85, audit articles <0.75

**Phase 6: Panel Review** (Week 5-6)
- 90-min session with experts
- Feedback, decisions, refinements

**Phase 7: Ongoing Operations** (Week 6+)
- Nightly QA runs, weekly re-extractions, monthly reviews
- Operational manual documentation

**Implementation Checklist**:
Table summarizing all 7 phases with week, deliverable, and acceptance criteria.

**Resource Requirements**:
- 1 engineer (6-7 weeks)
- 1 domain expert (panel, 1 week)
- Gemini API (~$15-30/month)
- Storage (~100 GB/year)

**Risks & Mitigations**:
- Rules too strict → Gold standard test + panel review
- Re-extraction doesn't improve → Field-specific prompts, monitor
- Nightly scan overhead → Parallel processing, caching
- Data loss → Versioned copies
- Scope creep → Strict agenda

**Success Metrics**:
- Quality score: 0.72 → 0.80+
- Vague antecedents: 32% → <10%
- Direction canonicalization: 86% → >99%
- System automation: fully nightly

**Why Read This**: If you're implementing the framework, follow this roadmap phase by phase.

---

### 4. contracts/schemas/extraction_quality_rules.json

**Audience**: Engineers (consuming via code)
**Format**: JSON
**Size**: ~939 lines
**Purpose**: Machine-readable validation rule set

**Structure**:

```
{
  "version": "1.0",
  "fields": {
    "antecedent": { rules: [...] },
    "consequent": { rules: [...] },
    "direction": { rules: [...] },
    ... (11 fields total)
  },
  "quality_scoring": { weights, thresholds },
  "quality_gates": { gates, thresholds },
  "panel_review_questions": [ Q1-Q5 ]
}
```

Each field contains:
- Description, criticality, allowed_values
- Rules array with rule_id, severity, check_type, error_message

Each rule specifies:
- What to check (enum_value, regex, type, range, etc.)
- Expected values or patterns
- Error/warning message

**Why Read This**: Load it in Python code to validate extractions without hardcoding rules. Enables rule versioning and evolution.

---

## How to Use These Documents

### Scenario 1: "I'm new to this project and want to understand the problem."

1. Read **EXTRACTION_QUALITY_BRIEFING_2026-02-28.md** (5 min)
2. Scan **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Part 1 (10 min)
3. Ask questions

### Scenario 2: "I need to implement the validation module."

1. Read **EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md** Phase 1 (5 min)
2. Read **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Parts 1-3 (30 min)
3. Load **contracts/schemas/extraction_quality_rules.json** and write validator (code)

### Scenario 3: "I'm on the panel and need to review the framework."

1. Read **EXTRACTION_QUALITY_BRIEFING_2026-02-28.md** (5 min)
2. Read **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Part 9 (decisions) (15 min)
3. Read **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Part 10 (open questions) (5 min)
4. Skim **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Part 1 (your field of expertise) (15 min)
5. Attend panel session

### Scenario 4: "I need to understand the scoring algorithm."

1. Read **EXTRACTION_QUALITY_BRIEFING_2026-02-28.md** (background) (5 min)
2. Read **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Parts 2-3 (scoring) (15 min)
3. Reference **contracts/schemas/extraction_quality_rules.json** "quality_scoring" section

### Scenario 5: "I'm writing the metrics dashboard."

1. Read **EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP_2026-02-28.md** Phase 4 (5 min)
2. Read **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** Part 6 (metrics) (10 min)
3. Reference **contracts/schemas/extraction_quality_rules.json** "quality_scoring" section

---

## Key Concepts (Cross-Document)

| Concept | Definition | Key Docs |
|---------|-----------|----------|
| **Field Quality Score** | Per-field score in [0, 1] (1.0=perfect, 0.7=warnings, 0.3=errors, 0.0=critical) | Briefing, Framework Part 2 |
| **Finding Quality Score** | Weighted mean of field scores for a single finding | Framework Part 3 |
| **Article Quality Score** | Median of finding scores for the entire article | Framework Part 3 |
| **Quality Action** | Recommendation (accept, flag, requeue, reject) based on score | Framework Part 4 |
| **Re-extraction** | Process of re-running Gemini extraction on flagged articles with improved prompts | Framework Part 5, Roadmap Phase 3 |
| **Field-Specific Prompt** | Targeted re-extraction prompt that addresses specific issues detected in QA scan | Framework Part 5 |
| **Validation Rule** | Programmatic check for a single field (enum, range, regex, etc.) | Framework Part 1, Rules JSON |
| **Quality Gate** | Invariant threshold (e.g., max 10% broken articles) that triggers alerts if violated | Framework Part 7, Roadmap |

---

## Timestamps & Versioning

| Document | Version | Date | Status |
|----------|---------|------|--------|
| EXTRACTION_QUALITY_BRIEFING | 1.0 | 2026-02-28 | Specification Complete |
| EXTRACTION_FIELD_QUALITY_FRAMEWORK | 1.0 | 2026-02-28 | Specification Complete |
| EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP | 1.0 | 2026-02-28 | Specification Complete |
| extraction_quality_rules.json | 1.0 | 2026-02-28 | Specification Complete |
| EXTRACTION_QUALITY_FRAMEWORK_INDEX | 1.0 | 2026-02-28 | This document |

---

## Next Steps

**For David Kirsh**:
1. Review EXTRACTION_QUALITY_BRIEFING
2. Decide: Approve framework or request changes?
3. If approved: Assign engineer for Phase 1

**For Engineers** (post-approval):
1. Follow EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP
2. Phase 1: Implement src/qa/extraction_field_validator.py
3. Sync with David weekly

**For Panel Reviewers** (mid-April):
1. Read Briefing + Framework Parts 9-10
2. Attend 90-min review session
3. Provide feedback on open questions Q1-Q5

---

## Questions / Feedback

If you have questions or suggestions about the framework:

**Technical Questions**: Refer to EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 1 (your field)
**Implementation Questions**: Refer to EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP
**Design Decisions**: Refer to EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 9
**Open Questions**: Refer to EXTRACTION_FIELD_QUALITY_FRAMEWORK Part 10

Contact: David Kirsh (decision maker), Engineer (implementation lead)

---

**Framework by**: Claude Opus (Anthropic)
**Reviewed by**: Framework specification only (panel review pending)
**Status**: Ready for implementation or expert panel review

