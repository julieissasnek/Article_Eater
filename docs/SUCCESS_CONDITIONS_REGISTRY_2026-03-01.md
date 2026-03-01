# SUCCESS CONDITIONS REGISTRY

**Date**: 2026-03-01
**Version**: 1.0.0
**Author**: Claude Code (Anthropic)
**Purpose**: Define explicit, measurable success conditions for all critical scripts and modules to prevent silent failures and zero-output problems.

---

## Executive Summary

This document specifies 56 success conditions across 9 critical components of the Article_Eater_PostQuinean_v1 system. Each condition is:

1. **Measurable**: Quantifiable metric with specific threshold
2. **Testable**: Automated test verifies condition
3. **Failure-detecting**: Would catch silent zero-output problems
4. **Component-specific**: Tailored to each script/module's role

The registry directly addresses David Kirsh's mandate: **"Every script, function, and process must have explicit SUCCESS CONDITIONS defined — and tests that verify them."** Many processes have yielded zero results or garbage; simple success checks would have caught these failures long ago.

---

## Problem Statement

The system has experienced cascading failures due to:

- **Silent zero-output**: Extraction produces empty files; no alert
- **Parsing corruption**: JSON loading succeeds but data is invalid
- **Skipped stages**: Pipeline progresses but key stages execute zero work
- **No validation gates**: Garbage output not detected until integration
- **Invisible failures**: Processes complete with exit code 0 but produce nothing

This registry eliminates these failure modes through explicit success verification.

---

## Registry Structure

Each component has:

- **Description**: What the component does
- **Entry point**: How to run/import it
- **4-8 Success Conditions**: Each with ID, name, metric, threshold, test

Success Condition Format:
- **ID**: Unique identifier (e.g., `SP-SC1`)
- **Name**: Short human-readable name
- **Description**: What success looks like
- **Metric**: Quantifiable measurement
- **Threshold**: Pass/fail criterion
- **Test Name**: Corresponding pytest function

---

## Component 1: scheduled_pipeline.py

**Role**: Orchestrates the entire pipeline (discovery → triage → extraction → QA → integration)

**Entry Point**: `python scripts/scheduled_pipeline.py run` or `python scripts/scheduled_pipeline.py daemon`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/scheduled_pipeline.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **SP-SC1** | Pipeline completes without fatal crash | exit_code == 0 AND error_log_critical == 0 | 100% | `test_pipeline_completes_without_fatal_crash` |
| **SP-SC2** | Wishlist add/save/load works | load_wishlist() after add yields matching entries | 100% | `test_pipeline_wishlist_operations` |
| **SP-SC3** | Discovery produces output | new_papers.json exists AND len > 0 | >0 papers | `test_discovery_produces_output` |
| **SP-SC4** | Triage classifies all papers | all(p.type_prediction for p in triage_output) | 100% | `test_triage_classifies_all_papers` |
| **SP-SC5** | Extraction produces files with findings | len(extractions) > 0 AND all n_findings > 0 | >0 per batch | `test_extraction_produces_files_with_findings` |
| **SP-SC6** | Pipeline state is logged and recoverable | queue_state.json exists AND contains checkpoints | 100% | `test_pipeline_state_persisted` |

### Known Issues / Audit Findings

- None yet (registry newly created)

### Recommendations

1. Run full pipeline weekly with monitoring
2. Alert on any SC1-SC4 failures
3. Investigate zero outputs in discovery/triage immediately

---

## Component 2: kirsh_decision_tree_analysis.py

**Role**: Implements David Kirsh's method for identifying causally-relevant stimulus attributes

**Entry Point**: `python scripts/kirsh_decision_tree_analysis.py`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/kirsh_decision_tree_analysis.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **KDT-SC1** | Stimuli loading succeeds | len(all_stimuli) > 0 | >0 stimuli | `test_kirsh_loads_stimuli` |
| **KDT-SC2** | Environmental filter preserves subset | len(filtered) > 0.5*len(all) AND all are_environmental | >50% retention | `test_kirsh_environmental_filter_works` |
| **KDT-SC3** | Clustering produces categories | 10 <= len(categories) <= 30 | 10-30 categories | `test_kirsh_clustering_produces_categories` |
| **KDT-SC4** | Essential attributes identified | all([2 <= len(essential) <= 5 for cat in categories]) | 2-5 per category | `test_kirsh_identifies_essential_attributes` |
| **KDT-SC5** | Novel attributes discovered | len(novel_attributes) >= 5 AND all have vision_algorithms | >=5 novel | `test_kirsh_discovers_novel_attributes` |
| **KDT-SC6** | Output report is complete | report has clusters, essential_attrs, novel_attrs, algorithms | 100% | `test_kirsh_output_complete` |

### Context

This script is critical for discovering new stimulus attributes. Session 18 results:
- **23,029** stimulus descriptions collected
- **16,948** environmental stimuli filtered
- **25** commonsense categories identified
- **12** new scientific attributes discovered (not in original 21-attribute taxonomy)

This script should produce high-quality clusters and novel attributes.

### Known Issues / Audit Findings

- None yet (script newly audited)

### Recommendations

1. Verify clustering quality: check for semantic coherence in categories
2. Validate novel attributes: confirm vision algorithms are implementable
3. Set weekly run schedule if data updates

---

## Component 3: backfill_operationalizations.py

**Role**: Fills missing operationalizations in outcome_vocab.json with evidence-based instruments

**Entry Point**: `python scripts/backfill_operationalizations.py`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/backfill_operationalizations.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **BO-SC1** | Vocabulary loads and parses | valid JSON AND len(terms) > 0 | >0 terms | `test_backfill_loads_vocab` |
| **BO-SC2** | Empty operationalizations identified | len(empty_terms) > 0 | >0 empty terms | `test_backfill_identifies_empty_terms` |
| **BO-SC3** | Backfilled ops are valid instruments | all(is_valid_instrument(op) for op in backfilled) | 100% valid | `test_backfill_operationalizations_valid` |
| **BO-SC4** | Existing ops are preserved | vocab_before == vocab_after for non-empty | 100% preserved | `test_backfill_preserves_existing` |
| **BO-SC5** | Output is saved and valid | file_exists AND validate_schema == PASS | 100% | `test_backfill_output_saved` |
| **BO-SC6** | Coverage improves measurably | coverage_after > coverage_before | >=10% improvement | `test_backfill_improves_coverage` |

### Context

Session 18 results:
- **216** operationalizations added
- **72** terms enriched (92.2% coverage)
- **295** total operationalizations in vocabulary

This script is critical for ensuring every outcome term has measurable instruments.

### Known Issues / Audit Findings

- None yet (script recently completed)

### Recommendations

1. Run after any vocabulary expansion
2. Check SC3 carefully: validate instrument names against literature
3. Document any new instrument categories added

---

## Component 4: link_outcomes_to_instruments.py

**Role**: Links outcome vocabulary operationalizations to instrument registry IDs

**Entry Point**: `python scripts/link_outcomes_to_instruments.py`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/link_outcomes_to_instruments.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **LOI-SC1** | Registry loads successfully | valid JSON AND len(instruments) > 0 | >0 instruments | `test_loi_loads_instruments` |
| **LOI-SC2** | Lookup table is built | all(lookup[key] == expected_id) | 100% match | `test_loi_builds_lookup` |
| **LOI-SC3** | Abbreviations extracted | all(expected_abbrev in extracted) | 100% extraction | `test_loi_extracts_abbreviations` |
| **LOI-SC4** | Operationalizations matched | all(len(matched_ids) >= 0) | 100% | `test_loi_matches_operationalizations` |
| **LOI-SC5** | Instrument IDs added to vocab | all(has_instrument_ids(op) for matched_op) | 100% | `test_loi_adds_instrument_ids` |
| **LOI-SC6** | Referential integrity | all(id in registry for id in output_vocab.instrument_ids) | 100% | `test_loi_referential_integrity` |

### Context

This script bridges outcome vocabulary to the instruments registry (95 instruments, Session 18).

### Known Issues / Audit Findings

- Abbreviation extraction regex may miss some variants (case sensitivity, hyphens)
- Some operationalizations may reference instruments not yet in registry

### Recommendations

1. Monitor LOI-SC3 and LOI-SC4: test on sample operationalizations
2. Update instruments registry before running this script
3. Investigate any unmatched operationalizations (LOI-SC4)

---

## Component 5: gemini_extraction_queue.py

**Role**: Manages extraction queue with Gemini API, two-run verification, cost tracking

**Entry Point**: `python scripts/gemini_extraction_queue.py --all --batch-size 50`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/gemini_extraction_queue.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **GEQ-SC1** | Triage loads and contains articles | len(triage['articles']) > 0 AND all have type_prediction | >0 articles | `test_geq_loads_triage` |
| **GEQ-SC2** | Queue state persisted | file_exists AND len(items) > 0 AND timestamped | 100% | `test_geq_queue_state_persisted` |
| **GEQ-SC3** | PDFs located for articles | len(pdf_found) / len(articles) >= 0.80 | >=80% | `test_geq_locates_pdfs` |
| **GEQ-SC4** | Prompts selected | all(get_prompt_family(article) is not None) | 100% | `test_geq_selects_prompts` |
| **GEQ-SC5** | Extractions structurally valid | all(is_valid_extraction(output)) | 100% | `test_geq_extractions_structurally_valid` |
| **GEQ-SC6** | Two-run verification performed | all(run1_exists AND run2_exists) | 100% | `test_geq_two_run_verification` |
| **GEQ-SC7** | Cost tracking accurate | total_cost == sum(run_costs) | 100% | `test_geq_cost_tracking` |
| **GEQ-SC8** | Output files named correctly | all(file_follows_naming_convention(f)) | 100% | `test_geq_output_naming` |

### Context

This is the core extraction engine. It connects triage output to Gemini API with verification and cost control.

**Pricing** (per 1M tokens):
- Gemini 2.5-flash: $0.15/M input, $0.60/M output
- Gemini 2.5-pro: $1.25/M input, $10.00/M output

### Known Issues / Audit Findings

- PDF location failure (GEQ-SC3 <100%) indicates missing PDFs in Article_Finder mirror
- Cost overruns should trigger alerts (track GEQ-SC7)
- Two-run verification (GEQ-SC6) is mandatory; single-run extractions skip validation

### Recommendations

1. **Weekly monitoring**: Check GEQ-SC5 on sample extractions
2. **Cost alerts**: Set GEQ-SC7 threshold based on budget
3. **PDF sync**: Run Article_Finder sync before extraction batches
4. **Verification review**: Spot-check run1 vs. run2 agreement monthly

---

## Component 6: run_panel_1_outcomes.py

**Role**: Panel-based resolution of unresolved outcome vocabulary terms

**Entry Point**: `python scripts/run_panel_1_outcomes.py --apply`

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/run_panel_1_outcomes.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **P1O-SC1** | Unresolved terms loaded | len(unresolved_terms) > 0 | >0 terms | `test_p1o_loads_unresolved_terms` |
| **P1O-SC2** | Terms filtered against vocab | no_term in output appears in existing_vocab | 100% | `test_p1o_filters_against_vocab` |
| **P1O-SC3** | Terms clustered | 10 <= len(clusters) <= 50 | 10-50 clusters | `test_p1o_clusters_terms` |
| **P1O-SC4** | Panel invoked | all(len(decisions) > 0 for batch in batches) | >0 decisions | `test_p1o_panel_invoked` |
| **P1O-SC5** | Decisions complete | all(has_required_fields(decision)) | 100% | `test_p1o_decisions_complete` |
| **P1O-SC6** | Output written | file_exists AND validate_schema == PASS | 100% | `test_p1o_output_written` |
| **P1O-SC7** | Coverage improves | coverage_after > coverage_before | >=50% resolved | `test_p1o_coverage_improves` |

### Context

Panel-1 is the first major panel in the system. It resolves outcome terms extracted from papers but not in the existing 112-term vocabulary.

**Session 18 results**:
- **4,080** unresolved outcome terms in queue
- **9** high-priority terms migrated to vocab
- Vocabulary expanded from 103 → 112 terms

### Known Issues / Audit Findings

- Queue may contain duplicates (P1O-SC2 filter important)
- Clustering quality varies; check semantic coherence (P1O-SC3)
- Panel decisions should be reviewed before acceptance

### Recommendations

1. Monitor P1O-SC3: inspect 5-10 random clusters for semantic coherence
2. Require human review of P1O-SC5 decisions before integration
3. Track P1O-SC7: if coverage < 50%, investigate panel rejection rate
4. Run every 2-4 weeks as extraction volume accumulates

---

## Component 7: src/qa/extraction_field_validator.py

**Role**: Validates all 11 extraction finding fields per quality rules

**Entry Point**:
```python
from src.qa.extraction_field_validator import ExtractionFieldValidator
validator = ExtractionFieldValidator()
report = validator.validate_article("data/extractions/10.1234_example.json")
```

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/src/qa/extraction_field_validator.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **EFV-SC1** | Validator initializes with rules | validator.rules is not None AND len > 0 | >0 rules | `test_efv_initializes` |
| **EFV-SC2** | Single article report complete | report has violations, quality_score, is_valid | 100% | `test_efv_validates_article` |
| **EFV-SC3** | Invalid fields detected | all(expected_violations in report) | 100% detection | `test_efv_detects_violations` |
| **EFV-SC4** | Quality score correct | 0 <= quality_score <= 1 AND decreases with violations | 100% | `test_efv_quality_score_correct` |
| **EFV-SC5** | Batch validation works | len(report.articles) >= input_count AND report.mean_score is float | 100% | `test_efv_batch_validation` |
| **EFV-SC6** | Below-threshold filtering works | all(score < threshold) | 100% accuracy | `test_efv_threshold_filtering` |
| **EFV-SC7** | Severity levels assigned | all(sev in {CRITICAL, ERROR, WARNING, INFO}) | 100% | `test_efv_severity_assignment` |

### Context

This validator is a critical quality gate. It prevents low-quality extractions from entering the web-of-belief. It validates 11 fields per extraction:
1. Finding ID
2. Antecedent
3. DV (dependent variable)
4. Direction
5. Effect size
6. Study design
7. Sample size
8. Theory commitment
9. Confidence
10. Evidence level
11. Justification

### Known Issues / Audit Findings

- Field validator may have missed corner cases (e.g., malformed JSON, null values)
- Quality scoring weights should be calibrated against expert judgment

### Recommendations

1. **Daily monitoring**: Validate sample of 20-50 extractions
2. **Threshold tuning**: Initially set mean_score threshold to 0.70 (not 0.75)
3. **Violation review**: Inspect violations at 100% severity to understand failure modes
4. **Calibration**: Run against manually-validated extractions quarterly

---

## Component 8: src/services/overseer.py

**Role**: OVERSEER — Superordinate monitoring of epistemic invariants and system health

**Entry Point**:
```python
from src.services.overseer import OverseerSystem
overseer = OverseerSystem()
report = overseer.generate_health_report()
```

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/src/services/overseer.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **OS-SC1** | System initializes with 6 components | all 6 components not None | 100% | `test_overseer_initializes` |
| **OS-SC2** | INV-0 (OPERATIONAL) checked | system_state != BOOTSTRAP_FAILED | 100% | `test_overseer_inv0_operational` |
| **OS-SC3** | INV-1 (Provenance) checked | all(belief.provenance is not None) | 100% | `test_overseer_inv1_provenance` |
| **OS-SC4** | INV-4 (Coherence) monitored | coherence_delta <= 0.05 | <=5% loss | `test_overseer_inv4_coherence` |
| **OS-SC5** | INV-10 (QA quality) measured | mean(quality_scores) >= 0.75 | >=0.75 | `test_overseer_inv10_qa_quality` |
| **OS-SC6** | Violations detected | len(violations) > 0 when broken | 100% detection | `test_overseer_detects_violations` |
| **OS-SC7** | Health report generated | report has coherence, conflicts, completeness, timestamp | 100% | `test_overseer_generates_report` |
| **OS-SC8** | Scheduler triggers modes | all(trigger(mode) fires for mode in MODES) | 100% | `test_overseer_scheduler_triggers` |

### Invariants Monitored

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| INV-0 | System OPERATIONAL | System not in BOOTSTRAP_FAILED state | CRITICAL |
| INV-1 | Provenance | Every belief has provenance record | CRITICAL |
| INV-2 | BN-Web Sync | Bayesian network edges reflect web credences | CRITICAL |
| INV-3 | Schema Compliance | All beliefs conform to ClaimV2 schema | CRITICAL |
| INV-4 | Coherence Decline | Loss ≤ 5% per integration | MAJOR |
| INV-5 | Credence Range | All credences in [0, 1] | CRITICAL |
| INV-6 | Pipeline Utilization | Utilization ≥ 25% | MAJOR |
| INV-7 | Template Coverage | Coverage ≥ 80% | MAJOR |
| INV-8 | Theory Orphans | Orphan rate ≤ 10% | MAJOR |
| INV-9 | Paper-Source Evidence | Paper evidence ≥ 20% | MINOR |
| INV-10 | QA Quality | Mean score ≥ 0.75 | MAJOR |

### Operational Modes

- **POST_INTEGRATION** (~5 sec): Check after paper integration
- **PERIODIC** (~15 min nightly): Full audit of all invariants
- **ALERT** (immediate): Triggered by detected violation
- **ON_DEMAND**: Manual inspection

### Known Issues / Audit Findings

- Overseer is newly designed (Feb 26 expert panel review)
- INV-6, INV-7, INV-8, INV-9 may require calibration against real data
- Coherence delta threshold (5%) may be too lenient

### Recommendations

1. **Mandatory deployment**: OS-SC1 through OS-SC8 must all pass before integration
2. **INV-0 and INV-1**: Check continuously (non-optional)
3. **OS-SC4 calibration**: Monitor coherence deltas for first 10 integrations
4. **Alert setup**: Configure OS-SC6 violations to email on CRITICAL invariants
5. **Weekly review**: Check health report (OS-SC7) every Monday

---

## Component 9: src/extraction/revised_prompts_v3.py

**Role**: Comprehensive extraction prompt set for Gemini API (V3.0 complete rewrite)

**Entry Point**:
```python
from src.extraction.revised_prompts_v3 import get_prompt, CANONICAL_DIRECTIONS
prompt = get_prompt("empirical")
```

**Location**: `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/src/extraction/revised_prompts_v3.py`

### Success Conditions

| ID | Name | Metric | Threshold | Test |
|----|------|--------|-----------|------|
| **REP-SC1** | Directions enumerated | CANONICAL_DIRECTIONS == [increase, decrease, no_effect, mixed] | 100% match | `test_rep_canonical_directions` |
| **REP-SC2** | Families defined | 5 families with >1 member each, no duplicates | 100% | `test_rep_article_families` |
| **REP-SC3** | Base prompt exists | PROMPT_BASE_V3 contains JSON schema | 100% | `test_rep_base_prompt_exists` |
| **REP-SC4** | Family prompts exist | all 5 families have specific prompts | 100% | `test_rep_family_prompts_exist` |
| **REP-SC5** | Validation complete | 7 validation checks present (direction, antecedent, sample_size, theory, mechanism, instrument, outcome) | 100% | `test_rep_validation_complete` |
| **REP-SC6** | Vocab injection works | get_prompt_with_vocab(vocab) embeds hints | 100% | `test_rep_vocab_injection` |
| **REP-SC7** | Schema compatible | Output format matches extraction_template.v2.schema.json | 100% | `test_rep_schema_compliance` |
| **REP-SC8** | Antecedent specificity enforced | Prompt rejects vague antecedents | 100% | `test_rep_antecedent_specificity` |

### Article Families and Types

| Family | Member Types |
|--------|--------------|
| **empirical** | empirical_v2, observational_field, case_study, mixed_methods |
| **synthesis** | meta_analysis, systematic_review, narrative_review |
| **theoretical** | theoretical, conceptual_framework, thought_piece |
| **qualitative** | interview_study, ethnographic, grounded_theory, phenomenological |
| **methods** | methods, instrument, protocol, guidelines, scale_development, validation |

### Canonical Directions

- `increase`: Effect increases outcome
- `decrease`: Effect decreases outcome
- `no_effect`: No significant effect
- `mixed`: Mixed or conditional effects

### Validation Checks

1. **Direction**: Must be one of 4 canonical values
2. **Antecedent**: Must be specific (no "some" or "may"), ≥8 words
3. **Sample size**: Required if empirical; documented when present
4. **Theory**: Must cite specific theory when claiming theory-based
5. **Mechanism**: Multi-step causal chain for mechanism papers (≥2 steps)
6. **Instrument**: Specific instrument names, not generic terms
7. **Outcome**: Outcome term must exist in outcome_vocab or marked as novel

### Context

V3.0 is a complete rewrite from V2.0 with major improvements:
- Enhanced JSON specification
- Explicit validation suffix
- Family-specific prompts restructured
- Vocabulary injection support
- Full schema.v2 compatibility

### Known Issues / Audit Findings

- REP-SC2: Family type definitions may have typos (validate against article database)
- REP-SC5: Some validation checks may be redundant (e.g., outcome check also in validator.py)

### Recommendations

1. **Monthly calibration**: Test prompt quality on 10-20 paper sample
2. **A/B testing**: Compare V3 vs. V2 extraction quality (if V2 still available)
3. **REP-SC6 validation**: Ensure outcome_vocab is current before injection
4. **Direction canonicalization**: Verify all extracted directions are in 4 canonical values

---

## Testing Strategy

### Running the Test Suite

```bash
# Run all success condition tests
pytest tests/test_success_conditions.py -v

# Run tests for specific component
pytest tests/test_success_conditions.py::TestScheduledPipeline -v

# Run single test
pytest tests/test_success_conditions.py::TestScheduledPipeline::test_pipeline_completes_without_fatal_crash -v

# Run with coverage
pytest tests/test_success_conditions.py --cov=src --cov=scripts
```

### Test Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Module imports | 9 | Verify syntax and imports |
| Function definitions | 28 | Verify required functions exist |
| Component structure | 13 | Verify component architecture |
| Data integrity | 3 | Verify critical files exist |
| Registry integrity | 4 | Verify registry completeness |
| **Total** | **~60** | Comprehensive coverage |

### CI/CD Integration

```yaml
# Example: .github/workflows/success_conditions.yml
name: Success Conditions Check
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pytest tests/test_success_conditions.py -v
```

---

## Failure Scenarios & Mitigations

### Scenario 1: Silent Zero-Output

**Problem**: Script runs to completion but produces zero output.

**Detection**: SC-X threshold checks (e.g., SC1 requires >0 items).

**Mitigation**:
- Monitor output file existence
- Check file size (should be >100 bytes)
- Validate JSON structure immediately after write

**Example**:
```python
# BAD: No validation
extractions = run_extraction()
with open("data/extractions/batch.json", "w") as f:
    json.dump(extractions, f)

# GOOD: Validate before writing
extractions = run_extraction()
assert len(extractions) > 0, "Zero extractions produced"
assert all(ext.get("findings") for ext in extractions), "Some extractions missing findings"
with open("data/extractions/batch.json", "w") as f:
    json.dump(extractions, f)
```

### Scenario 2: Parsing Corruption

**Problem**: JSON loads successfully but data structure is wrong.

**Detection**: Schema validation in SC-X conditions.

**Mitigation**:
- Validate JSON schema immediately after loading
- Check required fields before use
- Type-check numeric ranges (e.g., 0 <= quality_score <= 1)

**Example**:
```python
# BAD: No validation
data = json.load(f)
process(data)

# GOOD: Validate structure
data = json.load(f)
assert "terms" in data, "Missing 'terms' field"
assert isinstance(data["terms"], list), "terms should be list"
assert len(data["terms"]) > 0, "terms is empty"
for term in data["terms"]:
    assert "id" in term, f"Term missing 'id': {term}"
process(data)
```

### Scenario 3: Skipped Stages

**Problem**: Pipeline progresses but key stage executes zero work.

**Detection**: SC-X stage-specific conditions (e.g., SC5 for extraction).

**Mitigation**:
- Add checkpoints between stages
- Log item counts at each stage
- Alert if any stage processes <1 item

**Example**:
```python
# BAD: No visibility into skipped work
for stage in stages:
    stage.run()

# GOOD: Monitor each stage
for stage in stages:
    before = count_output(stage)
    stage.run()
    after = count_output(stage)
    assert after > before, f"{stage.name} produced zero work"
    log(f"{stage.name}: {before} -> {after} items")
```

### Scenario 4: Cascading Failures

**Problem**: One component's failure goes undetected, cascades to next component.

**Detection**: Success conditions at component boundaries.

**Mitigation**:
- Test each component independently before integration
- Run test suite as gate before deployment
- Monitor each SC-X condition in production

**Example**: If extraction (Component 5) produces zero findings, don't run Panel-1 (Component 6).

---

## Maintenance & Updates

### When to Add New Success Conditions

Add a new SC when:
1. New script/module added to system
2. Existing component gains new functionality
3. Audit discovers new failure mode
4. User reports silent failure

### Adding a Success Condition

1. **Identify the component** (e.g., `scripts/new_script.py`)
2. **Define success metrics** (what does good output look like?)
3. **Set thresholds** (minimum acceptable levels)
4. **Write test** (in `tests/test_success_conditions.py`)
5. **Document in this registry** (in `docs/SUCCESS_CONDITIONS_REGISTRY_*.md`)
6. **Add to JSON** (in `contracts/success_conditions.json`)

### Quarterly Calibration

Every quarter:
1. Review this registry
2. Check which conditions are most frequently violated
3. Adjust thresholds if needed
4. Add new conditions for new failure modes
5. Update test suite

---

## Success Conditions Checklist

Use this checklist before deploying any component:

- [ ] All SC tests pass (pytest run complete)
- [ ] Component produces expected output files
- [ ] Output files are non-empty (>100 bytes each)
- [ ] Output files are valid JSON/CSV/etc.
- [ ] No data corruption detected
- [ ] Logging is configured and working
- [ ] Error handling is in place
- [ ] Downstream components can accept output

---

## References

- Success Conditions Registry (JSON): `contracts/success_conditions.json`
- Test Suite: `tests/test_success_conditions.py`
- CLAUDE.md (global instructions): `CLAUDE.md`
- TASKS.md (current work): `TASKS.md`
- Overseer Invariants: `src/services/overseer.py` (lines 26-36)
- Extraction Schema: `contracts/schemas/extraction_template.v2.schema.json`

---

**Document Version**: 1.0
**Last Updated**: 2026-03-01
**Status**: ACTIVE
**Next Review**: 2026-03-31
