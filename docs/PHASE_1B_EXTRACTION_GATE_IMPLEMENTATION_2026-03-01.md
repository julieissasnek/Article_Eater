# Phase 1B: Extraction Field Validator Blocking Gate

**Date**: 2026-03-01
**Version**: V23.0.2+
**Status**: Complete — All code written and tested

## Summary

Implemented a blocking quality gate for the extraction pipeline that routes articles below a quality score threshold (0.75) to a repair queue instead of proceeding to integration. This prevents low-quality extractions from contaminating the web of beliefs system.

## Components Implemented

### 1. Core Gating Functions

**File**: `/src/qa/extraction_field_validator.py`

#### `ExtractionFieldValidator.validate_and_gate(extraction_path, threshold=0.75)`
- Entry point for pipeline-level quality gating
- Returns: `(passed: bool, score: float, violations: list[dict])`
- Validates extraction file against all 11 extraction field rules
- Returns serializable violation dicts for logging and repair queues
- Signature allows custom thresholds for different validation contexts

#### Module-level `gate_extraction(extraction_path, threshold=0.75)`
- Complete gating workflow in one function
- Validates extraction using `validate_and_gate`
- **If PASSED**: Returns success dict, file stays in place
- **If FAILED**:
  - Moves file to `data/extractions/needs_repair/` directory
  - Creates companion `.violations.json` file with violation manifest
  - Returns result dict with full audit trail
- Result dict structure:
  ```python
  {
    "passed": bool,
    "score": float,
    "original_path": str,
    "new_path": str | None,
    "n_violations": int,
    "message": str
  }
  ```

### 2. Pipeline Integration

**File**: `/scripts/scheduled_pipeline.py`

#### New Stage: `run_extraction_quality_gate()`
- Runs after extraction (`run_extraction`), before table extraction (`run_tables`)
- Discovers all `.json` files in `data/extractions/` directory
- Gates each file with threshold=0.75
- Logs pass/fail statistics
- Returns True for pipeline success (even if files fail — doesn't crash pipeline)

#### Stage Registration
Added to `STAGES` dictionary with proper ordering:
```
"extract" → "qa_gate" → "tables"
```

Pipeline now runs as:
1. discovery
2. triage
3. extract
4. **qa_gate** ← NEW
5. tables
6. integrate
7. overseer
8. cva

### 3. Overseer Integration

**File**: `/src/services/overseer.py`

#### Enhanced `_check_extraction_quality()` Method
Updated INV-10 (Extraction quality gate) to:
- Count files in `data/extractions/needs_repair/` directory
- Log count of files in repair queue
- Only validate files in main `extractions/` directory (excludes needs_repair)
- Provides visibility into queue status in system health reports

Example log output:
```
INV-10: 3 files in repair queue (data/extractions/needs_repair/)
INV-10: 47 passing extractions, mean quality score = 0.8234
```

### 4. Comprehensive Test Suite

**File**: `/tests/test_extraction_gate.py`

**Test Coverage** (12 tests, all passing):

1. `test_passing_extraction_returns_passed_true` — validate_and_gate returns passed=True for high-quality extractions
2. `test_failing_extraction_returns_passed_false` — validate_and_gate returns passed=False for low-quality extractions
3. `test_violations_are_serializable_dicts` — Violation objects are JSON-serializable
4. `test_custom_threshold` — Custom thresholds control gate decisions
5. `test_passing_extraction_not_moved` — Passing files stay in original location
6. `test_failing_extraction_moved_to_repair` — Failing files move to needs_repair directory
7. `test_violations_json_created` — Companion .violations.json created for failed files
8. `test_custom_threshold_gates_correctly` — Different thresholds produce different gating decisions
9. `test_missing_file_handled_gracefully` — Handles missing files without crashing
10. `test_repair_queue_dir_created_if_needed` — Creates needs_repair directory automatically
11. `test_gating_multiple_files` — Batch gating works correctly
12. `test_result_message_is_informative` — Result messages are clear and actionable

## Data Flow

```
data/extractions/
├── 10.1234_good_article.json      → PASSED → stays in place
├── 10.5678_poor_article.json      → FAILED → moves to needs_repair/
└── needs_repair/
    ├── 10.5678_poor_article.json
    └── 10.5678_poor_article.violations.json
```

## Repair Queue Structure

When an extraction fails, two files are created in `data/extractions/needs_repair/`:

**1. Extraction File** (moved, not copied)
```
data/extractions/needs_repair/10.5678_poor_article.json
```

**2. Violations Manifest** (new)
```
data/extractions/needs_repair/10.5678_poor_article.violations.json
```

Manifest structure:
```json
{
  "original_path": "data/extractions/10.5678_poor_article.json",
  "repair_queue_path": "data/extractions/needs_repair/10.5678_poor_article.json",
  "quality_score": 0.3542,
  "threshold": 0.75,
  "timestamp": "2026-03-01T15:42:33.123456",
  "violation_count": 23,
  "violations": [
    {
      "rule_id": "A1_NULL_ANTECEDENT",
      "field": "antecedent",
      "severity": "critical",
      "message": "Antecedent cannot be null or empty",
      "finding_index": 0
    },
    ...
  ]
}
```

## Quality Threshold Calibration

The default threshold is **0.75** (75% quality score) because:

- **Scoring formula**: Quality score = 1.0 − sum of violation penalties
  - CRITICAL: −0.25
  - ERROR: −0.15
  - WARNING: −0.05
  - INFO: −0.00 (no penalty)

- **Threshold interpretation**:
  - **≥ 0.75**: Acceptable for integration (≤1 critical or ≤5 errors)
  - **< 0.75**: Requires repair before integration

- **Rationale**: INV-10 in Overseer also checks mean score ≥ 0.75 across all extractions, so the pipeline gate aligns with system health requirements

## Error Handling

The gate_extraction function handles errors gracefully:

1. **File not found**: Logs error, returns failed result (no crash)
2. **JSON decode error**: Caught by validate_article, returns empty report
3. **Directory creation failure**: Creates repair_dir with mkdir(exist_ok=True, parents=True)
4. **File move failure**: Logs error, returns error message in result dict

Pipeline continues even if individual files fail — only crashes on catastrophic errors.

## Logging

The implementation provides detailed logging at INFO and WARNING levels:

**Passing extraction**:
```
PASS: 10.1234_article.json (score=0.9500, 5 violations)
```

**Failing extraction**:
```
FAIL: 10.5678_article.json moved to repair queue (score=0.3200, 28 violations).
See 10.5678_article.violations.json
```

**Batch summary**:
```
Quality gate complete: 47 passed, 3 failed, 0 errors
```

## Integration with Existing Components

### With ExtractionFieldValidator
- Uses existing `validate_article()` method
- Leverages all 11 field validators unchanged
- Returns serialized violation objects from existing Violation class

### With scheduled_pipeline.py
- Fits naturally after extraction, before table extraction
- Follows existing stage pattern (call function, return bool)
- Supports stage-specific runs: `python scripts/scheduled_pipeline.py run --stage qa_gate`
- Integrates with OverseerService for pipeline reporting

### With overseer.py
- INV-10 now reports both passing extractions and repair queue count
- Enables system health visibility into quality gate results
- No breaking changes to existing invariant checks

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `/src/qa/extraction_field_validator.py` | Added `validate_and_gate()` method to class, added `gate_extraction()` module function | +95 |
| `/scripts/scheduled_pipeline.py` | Added `run_extraction_quality_gate()` stage, registered in STAGES dict | +60 |
| `/src/services/overseer.py` | Enhanced `_check_extraction_quality()` to count repair queue files | +20 |
| `/tests/test_extraction_gate.py` | NEW — Comprehensive test suite with 12 tests | +370 |

## Testing Results

All tests pass with comprehensive coverage:
- Unit tests for validate_and_gate API
- Integration tests for gate_extraction workflow
- Edge case handling (missing files, custom thresholds)
- Batch processing verification
- Repair queue creation and manifest generation

Test execution:
```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
# Run all tests
python -m pytest tests/test_extraction_gate.py -v

# Or run individual test classes
python -m pytest tests/test_extraction_gate.py::TestValidateAndGate -v
python -m pytest tests/test_extraction_gate.py::TestGateExtraction -v
```

## Usage Examples

### In Pipeline
```bash
# Run full pipeline with new qa_gate stage
python scripts/scheduled_pipeline.py run

# Run only gating (after extractions exist)
python scripts/scheduled_pipeline.py run --stage qa_gate

# Run without gating (old behavior, not recommended)
python scripts/scheduled_pipeline.py run --stage discovery triage extract tables
```

### Programmatic API
```python
from src.qa.extraction_field_validator import gate_extraction

# Gate a single extraction
result = gate_extraction("data/extractions/paper_123.json", threshold=0.75)

if result["passed"]:
    print(f"✓ Passed: {result['score']:.4f}")
else:
    print(f"✗ Failed: {result['score']:.4f}, moved to repair")
    print(f"   Violations file: {result['new_path']}.violations.json")

# Check repair queue
import json
from pathlib import Path
violations_file = Path(result["new_path"]).parent / f"{Path(result['new_path']).stem}.violations.json"
manifest = json.loads(violations_file.read_text())
print(f"Violations: {manifest['violation_count']}")
```

### Checking Repair Queue
```bash
# List files in repair queue
ls -lah data/extractions/needs_repair/

# View violations for a file
cat data/extractions/needs_repair/paper_123.violations.json | jq '.violations[] | {field, rule_id, message}'

# Count files awaiting repair
ls data/extractions/needs_repair/*.json | grep -v violations.json | wc -l
```

## Next Steps (Future Work)

1. **Repair Automation**: Implement automated repair mechanisms for common violation patterns
2. **Quality Dashboard**: Web UI showing repair queue stats and violation patterns
3. **Threshold Tuning**: Analyze real extractions to optimize threshold for your corpus
4. **Escalation Workflows**: HITL (human-in-the-loop) review for high-value papers in repair queue
5. **Metrics Tracking**: Track pass/fail rates over time in system health reports
6. **Batch Repair**: Bulk operations for moving repaired files back to main extraction directory

## Backward Compatibility

- No breaking changes to existing APIs
- validate_article() and validate_batch() work unchanged
- ExtractionFieldValidator can be used without gating
- Pipeline can run without qa_gate stage if needed (though not recommended)
- Overseer INV-10 now provides more detailed information but still reports pass/fail on same criteria

## References

- Original spec: docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md
- Quality rules: contracts/schemas/extraction_quality_rules.json
- Overseer invariants: docs/OVERSEER_INVARIANTS.md (INV-10)
- Pipeline architecture: CLAUDE.md (Proactive Task Execution section)
