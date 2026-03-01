# Success Conditions — Quick Start Guide

**Date**: 2026-03-01
**Audience**: Developers, testers, DevOps, David
**Purpose**: Quick reference for using the success conditions system

---

## TL;DR

Success conditions define what "success" looks like for each critical script/module. This system prevents silent failures (zero outputs, garbage data) through explicit validation at each stage.

**3 files created**:
1. `contracts/success_conditions.json` — Machine-readable registry (62 conditions)
2. `tests/test_success_conditions.py` — 92 pytest tests
3. `docs/SUCCESS_CONDITIONS_REGISTRY_2026-03-01.md` — Full documentation

**Run tests**: `pytest tests/test_success_conditions.py -v`

---

## Components Covered

| Script | Role | SCs | Key Metrics |
|--------|------|-----|------------|
| scheduled_pipeline.py | Orchestrator | 6 | Pipeline completes, stages produce output |
| kirsh_decision_tree_analysis.py | Stimulus analysis | 6 | Stimuli load, filter, cluster, novel attrs |
| backfill_operationalizations.py | Vocab enrichment | 6 | Ops valid, no data loss, coverage improves |
| link_outcomes_to_instruments.py | Instrument linking | 6 | Registry loads, IDs valid, refs intact |
| gemini_extraction_queue.py | Extraction engine | 8 | Triage loads, PDFs found, 2-run verify |
| run_panel_1_outcomes.py | Panel resolution | 7 | Terms load, cluster, panel invoked |
| extraction_field_validator.py | Quality QA | 7 | Fields validated, violations detected |
| overseer.py | System monitoring | 8 | Initializes, invariants checked |
| revised_prompts_v3.py | Extraction prompts | 8 | Directions defined, families exist |

---

## Success Condition ID Format

Each condition has a unique ID: `{COMPONENT}-SC{NUMBER}`

Examples:
- `SP-SC1`: scheduled_pipeline success condition 1
- `KDT-SC5`: kirsh_decision_tree success condition 5
- `GEQ-SC6`: gemini_extraction_queue success condition 6
- `OS-SC8`: overseer success condition 8

---

## Running Tests

### All tests
```bash
pytest tests/test_success_conditions.py -v
```

### Single component
```bash
pytest tests/test_success_conditions.py::TestScheduledPipeline -v
pytest tests/test_success_conditions.py::TestGeminiExtractionQueue -v
```

### Single test
```bash
pytest tests/test_success_conditions.py::TestScheduledPipeline::test_pipeline_completes_without_fatal_crash -v
```

### With coverage
```bash
pytest tests/test_success_conditions.py --cov=src --cov=scripts -v
```

### Quiet mode (pass/fail only)
```bash
pytest tests/test_success_conditions.py -q
```

---

## Monitoring Success Conditions

### Check if extraction produces output (GEQ-SC5)

**Metric**: `len(extractions) > 0 AND all(ext.n_findings > 0)`

**In Python**:
```python
import json
extractions = json.load(open('data/extractions/batch.json'))
assert len(extractions) > 0, "Zero extractions"
assert all(ext.get("n_findings", 0) > 0 for ext in extractions), \
    "Some extractions have zero findings"
print(f"✓ {len(extractions)} extractions with findings")
```

### Check if vocabulary loads and is valid (BO-SC1)

**Metric**: `valid_json AND len(terms) > 0`

**In Python**:
```python
import json
vocab = json.load(open('contracts/outcome_vocab/outcome_vocab.json'))
assert "terms" in vocab, "Missing 'terms' field"
assert len(vocab["terms"]) > 0, "No terms in vocabulary"
print(f"✓ Vocabulary has {len(vocab['terms'])} terms")
```

### Check if triage classifies all papers (SP-SC4)

**Metric**: `all(paper.type_prediction for paper in triage_output)`

**In Python**:
```python
import json
triage = json.load(open('data/triage/keyword_triage.json'))
unclassified = [p for p in triage.get("papers", []) if not p.get("type_prediction")]
assert len(unclassified) == 0, f"{len(unclassified)} papers unclassified"
print(f"✓ All {len(triage['papers'])} papers classified")
```

---

## Common Success Condition Patterns

### Pattern 1: Output Existence
**Metric**: File exists and contains data
**Condition ID**: SP-SC3, KDT-SC1, GEQ-SC1
**Check**: `file_exists AND len(data) > 0`

### Pattern 2: Data Integrity
**Metric**: Fields present, correct types, references valid
**Condition ID**: BO-SC4, LOI-SC6, EFV-SC3
**Check**: Schema validation, referential integrity checks

### Pattern 3: Process Coverage
**Metric**: All items processed, none skipped
**Condition ID**: SP-SC4, P1O-SC2, GEQ-SC3
**Check**: `all([item.processed for item in items])`

### Pattern 4: Quality Gates
**Metric**: Violations detected, thresholds applied
**Condition ID**: EFV-SC4, OS-SC5
**Check**: `quality_score >= threshold AND violations == expected`

### Pattern 5: Configuration
**Metric**: Required values/enums/mappings defined
**Condition ID**: REP-SC1, REP-SC2
**Check**: Enum members exist, mappings complete

---

## Failure Scenarios

### Scenario: Zero-Output Silent Failure

**Problem**: Extraction produces empty file; pipeline continues.

**Detection**:
- `GEQ-SC5` (zero extractions)
- `GEQ-SC6` (two-run verification fails)

**Fix**:
```python
# Before write, validate
extractions = run_extraction()
if not extractions or not any(ext.get("findings") for ext in extractions):
    raise ValueError("Extraction produced zero findings")
```

### Scenario: Parsing Corruption

**Problem**: JSON loads but structure is wrong.

**Detection**:
- `BO-SC1` (invalid JSON)
- `EFV-SC2` (missing fields)

**Fix**:
```python
# After load, validate schema
data = json.load(f)
required_fields = ["id", "terms", "version"]
for field in required_fields:
    assert field in data, f"Missing required field: {field}"
```

### Scenario: Cascading Failure

**Problem**: Component A fails silently; Component B processes garbage.

**Detection**:
- Component A's SC-X conditions fail
- Component B receives invalid input

**Fix**:
```python
# Check upstream success before processing
upstream_valid = check_success_conditions(component_a)
if not upstream_valid:
    raise RuntimeError("Upstream component failed; aborting")
```

---

## Adding Success Conditions

### When to Add

- New script/module added
- New failure mode discovered
- Existing component gains functionality
- User reports silent failure

### How to Add

1. **Identify component**: e.g., `scripts/new_script.py`

2. **Define success criterion**: e.g., "Output file contains >0 records"

3. **Create metric**: e.g., `len(records) > 0`

4. **Set threshold**: e.g., `>0 records per run`

5. **Write test**:
```python
def test_new_script_produces_output(self, project_root):
    """NEW-SC1: New script produces output."""
    script_file = project_root / "scripts" / "new_script.py"
    content = script_file.read_text()
    assert "output" in content.lower(), "Output logic not found"
```

6. **Add to JSON**:
```json
"scripts/new_script.py": {
  "description": "What new script does",
  "conditions": [
    {
      "id": "NEW-SC1",
      "name": "Script produces output",
      "description": "Output contains >0 records",
      "metric": "len(records) > 0",
      "threshold": ">0 records",
      "test_name": "test_new_script_produces_output"
    }
  ]
}
```

7. **Update documentation**: Add section to `docs/SUCCESS_CONDITIONS_REGISTRY_*.md`

8. **Commit**: `git commit -m "feat: Add NEW-SC1-3 success conditions for new_script.py"`

---

## Integrating with CI/CD

### GitHub Actions Example

```yaml
name: Success Conditions Check
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run success conditions tests
        run: pytest tests/test_success_conditions.py -v --tb=short
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results.xml
```

### GitLab CI Example

```yaml
success_conditions:
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pytest tests/test_success_conditions.py -v --tb=short
  artifacts:
    reports:
      junit: test-results.xml
```

---

## Debugging Failed Tests

### Test fails: "File not found"

**Problem**: Script file doesn't exist at expected path

**Solution**: Check file location
```bash
ls /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/scheduled_pipeline.py
```

### Test fails: "Syntax error"

**Problem**: Python file has syntax errors

**Solution**: Check syntax
```bash
python -m py_compile scripts/scheduled_pipeline.py
```

### Test fails: "Missing required field"

**Problem**: Component definition is incomplete

**Solution**: Inspect component source
```bash
grep -n "def load_" scripts/backfill_operationalizations.py
```

### Test fails: "Assertion error"

**Problem**: Success condition not met

**Solution**: Review assertion and actual data
```bash
pytest tests/test_success_conditions.py::TestScheduledPipeline::test_pipeline_defines_stages -vv
```

---

## Key Metrics & Thresholds

| Metric | Type | Threshold | Component |
|--------|------|-----------|-----------|
| Files exist | Boolean | 100% | All |
| Output size | Integer | >100 bytes | All |
| JSON valid | Boolean | 100% | All |
| Items processed | Integer | >0 | SP, KDT, BO |
| Coverage | Percentage | >=80% | BO, P1O |
| Quality score | Float | 0.0-1.0 | EFV, OS |
| Coherence delta | Float | <=5% | OS |
| Error count | Integer | 0 | All |

---

## FAQ

**Q: What if a success condition fails?**
A: It indicates a problem with that component. Debug using the test output and component logs.

**Q: Can I modify thresholds?**
A: Yes, update `contracts/success_conditions.json` and document the change in TASKS.md.

**Q: What if multiple tests fail?**
A: Start with the upstream-most component (e.g., pipeline before extraction).

**Q: How often should I run tests?**
A: Before each deployment; daily in production; continuously in CI/CD.

**Q: Can I add custom success conditions?**
A: Yes, follow the "Adding Success Conditions" section above.

---

## References

- **Full Documentation**: `docs/SUCCESS_CONDITIONS_REGISTRY_2026-03-01.md`
- **Completion Report**: `docs/AUDIT_SUCCESS_CONDITIONS_COMPLETION_2026-03-01.md`
- **Registry JSON**: `contracts/success_conditions.json`
- **Test Suite**: `tests/test_success_conditions.py`
- **This Guide**: `SUCCESS_CONDITIONS_QUICK_START.md`

---

**Document Version**: 1.0
**Last Updated**: 2026-03-01
**Status**: ACTIVE
**Questions?**: Review full documentation or check test source code
