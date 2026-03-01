# Extraction Field Quality Framework — Implementation Roadmap

**Date**: 2026-02-28
**Framework Version**: 1.0
**Implementation Status**: Design Phase Complete. Ready for Development.

---

## Overview

Two companion documents define the Extraction Field Quality Framework:

1. **EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md** — Conceptual framework, validation rules (pseudocode), scoring logic, cleanup pipeline design, and decision log
2. **contracts/schemas/extraction_quality_rules.json** — Machine-readable validation rule set that can be loaded by Python QA modules

This roadmap breaks implementation into phases.

---

## Phase 1: QA Validation Module (Week 1-2)

**Goal**: Build Python module that validates extraction fields against rules.

### Deliverables

**File**: `src/qa/extraction_field_validator.py`

```python
# Pseudocode structure
class ExtractionFieldValidator:
    """Load extraction_quality_rules.json and validate findings."""

    def __init__(self, rules_path: str):
        self.rules = json.load(open(rules_path))
        self.field_validators = self._build_validators()

    def validate_finding(self, finding: dict) -> ValidationResult:
        """
        Returns:
        {
            'finding_id': ...,
            'field_scores': {'antecedent': 1.0, 'direction': 0.7, ...},
            'finding_quality_score': 0.82,
            'issues': [
                {'field': 'direction', 'rule': 'D3_DIRECTION_EFFECT_MISMATCH',
                 'severity': 'error', 'message': '...'}
            ]
        }
        """
        pass

    def validate_article(self, article: dict) -> ArticleValidationResult:
        """
        Returns:
        {
            'doi': ...,
            'n_findings': ...,
            'finding_scores': [...],
            'article_quality_score': 0.74,
            'recommended_action': 'requeue',
            'summary': {...}
        }
        """
        pass
```

**Tests**: `tests/test_extraction_field_validator.py`
- Test each validation rule with valid/invalid inputs
- Test edge cases (out-of-range values, null fields, type mismatches)
- Test article-level scoring

**Acceptance Criteria**:
- All 50+ validation rules implemented and tested
- Validation results match expected severity levels
- Performance: validate 1,000 articles in < 2 seconds

---

## Phase 2: Nightly QA Scan (Week 2-3)

**Goal**: Add QA scanning to Overseer nightly job.

### Deliverables

**File**: `src/overseer/qa_quality_gate.py`

```python
class QAQualityGate(OverseerStage):
    """Nightly QA scan of all extractions."""

    def run(self):
        # 1. Load all extraction files
        # 2. For each, validate with ExtractionFieldValidator
        # 3. Collect articles needing requeue
        # 4. Generate metrics report
        # 5. Log to quality_ledger.jsonl
        pass

    def generate_requeue_queue(self) -> list[RequeueCandidate]:
        """
        Returns list of articles flagged for re-extraction with:
        - doi
        - reason (vague_antecedent, direction_inconsistency, etc.)
        - quality_score
        - n_problematic_findings
        - priority (high, medium, low)
        """
        pass

    def generate_metrics_report(self) -> MetricsSnapshot:
        """
        Snapshot of system quality at given time:
        - article_quality distribution
        - field_issues breakdown
        - recommendations (% to requeue, % accept, etc.)
        """
        pass
```

**Integration with Overseer**:
Add to `config/overseer_stages.yaml`:
```yaml
stages:
  - name: "QA_QUALITY_GATE"
    enabled: true
    schedule: "0 2 * * *"  # 2 AM UTC
    description: "Scan extraction quality, flag articles for re-extraction"
    executor: "qa_quality_gate.QAQualityGate"
    config:
      rules_path: "contracts/schemas/extraction_quality_rules.json"
      output_dir: "data/qa_reports"
      alert_threshold: 0.75  # Alert if mean quality < 0.75
```

**Acceptance Criteria**:
- Scans 1,043 extractions in < 5 minutes
- Generates accurate requeue list
- Metrics report includes all required fields (distribution, field_issues, recommendations)
- Integrates cleanly with existing Overseer pipeline

---

## Phase 3: Re-extraction Pipeline (Week 3-4)

**Goal**: Schedule and execute re-extraction of flagged articles.

### Deliverables

**File**: `src/overseer/reextraction_scheduler.py`

```python
class ReextractionScheduler(OverseerStage):
    """Schedule and execute re-extraction batches."""

    def run(self):
        # 1. Read requeue_candidates from QA_QUALITY_GATE
        # 2. Prioritize by: high > medium > low, then by quality_score
        # 3. Create batches (10-20 articles per batch)
        # 4. For each batch:
        #    - Select field-specific re-extraction prompt
        #    - Call Gemini with targeted prompt
        #    - Save new extraction
        #    - Compare old vs. new quality
        #    - Log improvement
        pass

    def select_prompt_variant(self, article: dict, issues: list[str]) -> str:
        """
        Choose re-extraction prompt based on detected issues.
        Examples:
        - if 'vague_antecedent' in issues: use EXTRACTION_ANTECEDENT_CLARIFICATION
        - if 'direction_inconsistency' in issues: use EXTRACTION_DIRECTION_VALIDATION
        - else: use standard EXTRACTION_PROMPT_V2
        """
        pass

    def verify_improvement(self, old_article: dict, new_article: dict) -> ImprovementReport:
        """
        Compare quality scores and field-level improvements.
        """
        pass
```

**Re-extraction Prompts**:
Update `src/extraction/revised_prompts_v2.py` with new variants:
- `EXTRACTION_ANTECEDENT_CLARIFICATION` — Target vague antecedents
- `EXTRACTION_DIRECTION_VALIDATION` — Target direction inconsistencies
- `EXTRACTION_EFFECT_SIZE_VALIDATION` — Target effect_size issues
- `EXTRACTION_FIELD_REPAIR_{field}` — Generic field repair for any field

Each variant includes:
```python
"""
Instruction: [specific guidance for problematic field]
Context: [what Gemini extracted before, why it was wrong]
Example: [corrected extraction]
"""
```

**Storage**:
- Original extraction: `data/extractions/{doi}.json`
- Re-extracted: `data/extractions/{doi}_reext_v{N}.json` (keep history)
- Improvement report: `data/qa_reports/reextraction_improvements_2026-02-28.jsonl`

**Acceptance Criteria**:
- Re-extract 100+ articles in first batch
- Average improvement (new_score - old_score) > 0.05
- At least 80% of re-extractions improve quality or stay the same
- Track all re-extractions in improvement_report

---

## Phase 4: Quality Metrics Dashboard (Week 4)

**Goal**: Create dashboard to track extraction quality over time.

### Deliverables

**File**: `src/dashboards/extraction_quality_dashboard.py` (Streamlit or similar)

**Metrics Displayed**:
1. **System Quality Overview**
   - Distribution of article quality scores (histogram)
   - Mean/median/stdev quality over time (line chart)
   - Percentage in each quality band (0-50%, 50-75%, 75-90%, 90-100%)

2. **Field Quality Breakdown**
   - Which fields have most issues? (bar chart)
   - Failure rate per field (antecedent, direction, effect_size, etc.)
   - Evolution of field quality over time

3. **Action Recommendations**
   - Articles to accept (n, %)
   - Articles flagged for review (n, %)
   - Articles to requeue (n, %)

4. **Re-extraction History**
   - Number of articles re-extracted
   - Average improvement (before/after quality score)
   - Which issues were successfully fixed?

5. **Invariant Violations**
   - Alert if any gate threshold exceeded
   - Timestamp and severity of violation

**Data Source**:
- `data/qa_reports/metrics_{date}.json` (daily snapshots)
- `data/qa_reports/reextraction_improvements_*.jsonl`

**Acceptance Criteria**:
- Dashboard loads in < 2 seconds
- All metrics computed correctly
- Responsive to new data (updates within 1 hour of new QA scan)

---

## Phase 5: Gold Standard Validation (Week 4-5)

**Goal**: Validate quality framework against manually verified gold standard papers.

### Deliverables

**Process**:
1. Select 10-20 gold standard papers (already manually verified)
2. For each gold standard finding, compute quality score
3. Compare to human judgment (should be high quality)
4. Refine thresholds/weights if needed

**File**: `tests/test_extraction_quality_gold_standard.py`

```python
def test_gold_standard_articles_score_high():
    """
    Gold standard papers should have mean article_quality_score >= 0.85
    """
    gold_standard_articles = load_gold_standard_papers()
    scores = [compute_article_quality_score(a) for a in gold_standard_articles]
    mean_score = statistics.mean(scores)
    assert mean_score >= 0.85, f"Gold standard mean score {mean_score} too low"

def test_problematic_articles_identified():
    """
    Articles flagged during Phase 1 audit should score < 0.75
    """
    problematic_dois = [
        '10.1016_s0272-4944(02)00079-8',  # From quality audit
        '10.3758_s13414-010-0073-7',
        # ... more
    ]
    for doi in problematic_dois:
        article = load_extraction(doi)
        score = compute_article_quality_score(article)
        assert score < 0.75, f"{doi} should be flagged but scored {score}"
```

**Acceptance Criteria**:
- Gold standard articles score >= 0.85
- Audited problematic articles score < 0.75
- No false positives (good articles flagged as bad)
- No false negatives (bad articles accepted)

---

## Phase 6: Panel Review & Refinement (Week 5-6)

**Goal**: Present framework and initial results to expert panel for feedback.

### Deliverables

**Panel Session (90 minutes)**:
1. Present framework overview (15 min)
2. Show audit results (vague antecedents, direction chaos, etc.) (10 min)
3. Discuss open questions Q1-Q5 (45 min)
4. Review re-extraction improvements (15 min)
5. Decide on next steps (5 min)

**Documentation**:
- `docs/PANEL_REVIEW_EXTRACTION_QUALITY_2026-{date}.md` — Minutes, decisions, action items

**Possible Refinements**:
- Adjust field weights based on panel input
- Refine threshold values
- Clarify rules for edge cases (e.g., Q2 on mixed directions)
- Update re-extraction prompts

---

## Phase 7: Ongoing Maintenance (Week 6+)

**Goal**: Integrate quality framework into standard Overseer operations.

### Deliverables

**Recurring Tasks**:
1. **Nightly QA_QUALITY_GATE stage** runs automatically
2. **Weekly reextraction batches** process flagged articles
3. **Monthly dashboard review** with David to assess trends
4. **Quarterly rule refinement** based on new failure patterns

**Documentation**:
- `docs/QA_OPERATION_MANUAL.md` — How to run, monitor, and update QA system
- `docs/QUALITY_LEDGER.md` — Cumulative log of all quality interventions

**Metrics Tracked**:
- Extraction quality trending (should improve as re-extractions happen)
- Re-extraction success rate (% of articles that improve)
- Field-level quality (which fields still need work?)
- Extraction pipeline performance (time, cost per article)

---

## Summary: Implementation Checklist

| Phase | Deliverable | Week | Acceptance Criteria |
|-------|------------|------|-------------------|
| 1 | `src/qa/extraction_field_validator.py` | 1-2 | 50+ rules, tests passing, <2s for 1K articles |
| 2 | `src/overseer/qa_quality_gate.py` + Overseer integration | 2-3 | Scans 1K articles in <5 min, accurate requeue list |
| 3 | `src/overseer/reextraction_scheduler.py` + prompts | 3-4 | Re-extract 100+ articles, 80%+ improve |
| 4 | Streamlit dashboard | 4 | <2s load time, all metrics correct |
| 5 | Gold standard validation tests | 4-5 | Gold std score ≥0.85, audit articles score <0.75 |
| 6 | Panel review session | 5-6 | Panel feedback documented, decisions made |
| 7 | Ongoing operations | 6+ | Nightly QA runs, weekly re-extractions, monthly reviews |

---

## Resource Requirements

**Development**:
- 1 engineer (6-7 weeks)
- 1 domain expert (panel review, 1 week)

**Infrastructure**:
- Gemini API calls for re-extraction (~2-3K articles/month estimate = ~$15-30/month)
- Storage for QA reports and re-extracted files (~100 GB/year)

**Dependencies**:
- `pydantic` (validation models)
- `streamlit` (dashboard)
- Existing `llm_extraction_service.py` (for re-extraction calls)
- Existing Overseer framework

---

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Validation rules too strict, reject good data | Gold standard test + panel review |
| Re-extraction doesn't improve quality | Use field-specific prompts, monitor improvement rate |
| Overhead of nightly QA scans | Parallel processing, cache results |
| Data loss if re-extraction overwrites original | Keep versioned copies (`_reext_v1`, `_reext_v2`, etc.) |
| Panel review causes scope creep | Set strict agenda, time-box Q&A |

---

## Success Metrics (End of Implementation)

1. **Extraction quality improves**: Mean article quality score rises from 0.72 to 0.80+
2. **Vague antecedents reduced**: <10% of articles contain vague antecedent language
3. **Direction field normalized**: <5% non-canonical direction values
4. **System is automated**: Nightly QA scans run without manual intervention
5. **Panel is satisfied**: Framework approved for use in evidence synthesis

---

## Appendix: Files to Create/Modify

**New Files**:
- `src/qa/extraction_field_validator.py` (300+ lines)
- `src/qa/__init__.py`
- `src/qa/metrics.py` (for dashboard)
- `src/overseer/qa_quality_gate.py` (200+ lines)
- `src/overseer/reextraction_scheduler.py` (300+ lines)
- `src/dashboards/extraction_quality_dashboard.py` (400+ lines)
- `tests/test_extraction_field_validator.py` (300+ lines)
- `tests/test_extraction_quality_gold_standard.py` (100+ lines)
- `docs/QA_OPERATION_MANUAL.md`
- `docs/QUALITY_LEDGER.md`

**Modified Files**:
- `src/extraction/revised_prompts_v2.py` (add prompt variants)
- `config/overseer_stages.yaml` (add QA_QUALITY_GATE stage)
- `config/overseer_invariants.json` (add quality gates)
- `TASKS.md` (record progress)

**Existing Files (Unchanged)**:
- `contracts/schemas/extraction_quality_rules.json` (reference only)
- `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md` (reference only)

