# Effect Size Validator — Integration Guide

**Quick reference for using the effect size validator in ATLAS pipelines.**

---

## Installation & Setup

No additional dependencies required. The validator uses only Python standard library.

```python
from src.qa.effect_size_validator import EffectSizeValidator, ValidationResult, ProblemType

validator = EffectSizeValidator()
```

---

## Basic Usage

### Single Value Validation

```python
from src.qa.effect_size_validator import EffectSizeValidator

validator = EffectSizeValidator()

# Validate a single effect size
result = validator.validate_effect_size(0.45, "Cohen's d")

print(result.is_valid)          # True
print(result.problem_type)       # <ProblemType.VALID: 'valid'>
print(result.message)            # "Valid Cohen's d effect size"
print(result.suggested_correction) # None (already valid)
```

### Batch Validation

```python
# Validate multiple findings at once
findings = [
    {"effect_size": 0.5, "effect_size_type": "Cohen's d"},
    {"effect_size": 1.5, "effect_size_type": "Pearson's r"},
    {"effect_size": None, "effect_size_type": None},
]

report = validator.batch_validate(findings)

print(f"Valid: {report.valid_count}/{report.total_validated}")
print(f"Validity rate: {report.validity_rate:.1%}")
print(f"Problems by type: {report.problems_by_type}")
print(report.summary())
```

### File Validation

```python
from pathlib import Path

# Validate all effect sizes in an extraction file
filepath = Path("data/extractions/10.1234_example.json")
report = validator.validate_extraction_file(filepath)

print(f"File: {filepath.name}")
print(f"Problems: {report.problem_count}/{report.total_validated}")
for invalid in report.invalid_values[:5]:
    print(f"  - {invalid['problem_type']}: {invalid['effect_size']}")
```

---

## Problem Classification

The validator returns one of these problem types:

| Problem Type | Meaning | Action |
|---|---|---|
| `VALID` | Effect size is fine | Keep as-is |
| `NULL_VALUE` | Value is None/null | Acceptable (missing data) |
| `NON_NUMERIC` | Can't parse as number | Flag for manual review |
| `WRONG_FIELD` | Likely a p-value | Flag for manual review |
| `OUT_OF_RANGE` | Outside valid bounds | Flag for manual review |
| `NEGATIVE_INVALID` | Negative when must be positive | Flag for manual review |
| `OUTLIER` | Extreme but technically valid | Flag for manual review |

---

## Integration Examples

### 1. Extraction Quality Check (Post-Model)

```python
def validate_extraction(extraction_dict):
    """Validate quality of extracted findings."""
    validator = EffectSizeValidator()
    findings = extraction_dict.get("findings", [])
    report = validator.batch_validate(findings)

    # Fail if more than 5% invalid
    if report.problem_rate > 0.05:
        return False, f"Effect size problems: {report.problem_count} found"
    return True, "Effect sizes OK"

# Use in extraction pipeline
is_valid, message = validate_extraction(extraction)
if not is_valid:
    logger.warning(f"Extraction {doi}: {message}")
```

### 2. Data Loading Pipeline (Pre-Analysis)

```python
def load_findings_with_validation(filepath):
    """Load findings with automatic quarantine of invalid effect sizes."""
    validator = EffectSizeValidator()

    with open(filepath) as f:
        data = json.load(f)

    findings = data.get("findings", [])
    clean_findings = []
    quarantined = []

    for finding in findings:
        result = validator.validate_effect_size(
            finding.get("effect_size"),
            finding.get("effect_size_type")
        )

        if result.is_valid or result.problem_type == ProblemType.NULL_VALUE:
            clean_findings.append(finding)
        else:
            # Quarantine invalid
            finding["_original_effect_size"] = finding["effect_size"]
            finding["effect_size"] = None
            quarantined.append(finding)

    return clean_findings, quarantined
```

### 3. Automated Cleanup (Batch Processing)

```python
# See scripts/clean_effect_sizes.py for full implementation

from pathlib import Path

def batch_clean_extractions(extraction_dir, dry_run=True):
    """Clean all extractions in directory."""
    validator = EffectSizeValidator()
    cleaned_count = 0

    for filepath in Path(extraction_dir).glob("*.json"):
        with open(filepath) as f:
            data = json.load(f)

        findings = data.get("findings", [])
        had_problems = False

        for finding in findings:
            result = validator.validate_effect_size(
                finding.get("effect_size"),
                finding.get("effect_size_type")
            )

            if not result.is_valid:
                had_problems = True
                finding["_original_effect_size"] = finding["effect_size"]
                finding["_quarantine_reason"] = result.message
                finding["effect_size"] = None

        if had_problems and not dry_run:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            cleaned_count += 1

    return cleaned_count
```

### 4. Monitoring Dashboard

```python
def measure_quality_metrics(extraction_dir):
    """Compute quality metrics for dashboard."""
    validator = EffectSizeValidator()

    total_findings = 0
    total_problems = 0
    problems_by_type = {}

    for filepath in Path(extraction_dir).glob("*.json"):
        try:
            with open(filepath) as f:
                data = json.load(f)
            findings = data.get("findings", [])
            report = validator.batch_validate(findings)

            total_findings += report.total_validated
            total_problems += report.problem_count
            for ptype, count in report.problems_by_type.items():
                problems_by_type[ptype] = problems_by_type.get(ptype, 0) + count
        except:
            pass

    return {
        "total_findings": total_findings,
        "validity_rate": (total_findings - total_problems) / total_findings if total_findings else 1,
        "problem_count": total_problems,
        "problems_by_type": problems_by_type,
    }
```

---

## Correction Workflow

```python
# Detect and suggest corrections
finding = {"effect_size": 2.0, "effect_size_type": "Pearson's r"}

result = validator.validate_effect_size(
    finding["effect_size"],
    finding["effect_size_type"]
)

if not result.is_valid:
    correction = validator.suggest_correction(
        finding["effect_size"],
        finding["effect_size_type"]
    )

    if correction is not None:
        print(f"Suggested fix: {finding['effect_size']} → {correction}")
        # finding["effect_size"] = correction  # Apply if confident
    else:
        print(f"Manual review needed: {result.message}")
```

---

## Measure Type Aliases

The validator automatically normalizes these aliases:

```python
# All equivalent to "Cohen's d"
"cohen's d", "cohens d", "d", "Cohen's d"

# All equivalent to "Pearson's r"
"pearson's r", "pearsons r", "r", "correlation"

# All equivalent to "R²"
"r2", "r squared", "r-squared", "R²"

# All equivalent to "Odds ratio"
"odds ratio", "or"

# All equivalent to "Eta squared"
"eta squared", "eta2", "η2"
```

---

## Common Issues & Solutions

### Issue: All small values flagged as p-values
**Solution**: This shouldn't happen with current validator. The validator only flags specific p-values (0.01, 0.05, 0.001) and scientific notation (< 0.001).

### Issue: Correlations in [0.3, 0.7] marked as valid but seem wrong
**Solution**: These ARE valid for correlations. If you suspect data quality issue, check `effect_size_type` field.

### Issue: Need to exclude certain measure types
**Solution**: Add custom filtering before validation:
```python
if finding.get("effect_size_type") in ["Beta", "regression_coefficient"]:
    # Skip validation for unstandardized coefficients
    continue
result = validator.validate_effect_size(...)
```

### Issue: Want stricter outlier detection
**Solution**: Subclass validator and override `_validate_typed()`:
```python
class StrictEffectSizeValidator(EffectSizeValidator):
    def _validate_typed(self, value, measure_type):
        result = super()._validate_typed(value, measure_type)
        # Add stricter checks here
        return result
```

---

## Performance Notes

- **Single validation**: < 1ms
- **Batch of 100 findings**: < 5ms
- **File with 1,000 findings**: < 10ms
- **Dataset of 1,069 files (33K findings)**: < 5 seconds

No optimization needed for typical use cases.

---

## Logging Integration

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("effect_size_validator")

# Validator logs errors for malformed files
validator = EffectSizeValidator()
report = validator.validate_extraction_file(Path("bad_file.json"))
# Will log: "Failed to read bad_file.json: ..."
```

---

## Type Hints & IDE Support

Full type hints for IDE autocomplete:

```python
from src.qa.effect_size_validator import (
    EffectSizeValidator,
    ValidationResult,
    BatchValidationReport,
    ProblemType,
    MeasureType,
)

validator: EffectSizeValidator = EffectSizeValidator()
result: ValidationResult = validator.validate_effect_size(0.5, "Cohen's d")
report: BatchValidationReport = validator.batch_validate(findings)
problem: ProblemType = result.problem_type
```

---

## Testing Your Integration

```python
# Quick smoke test
validator = EffectSizeValidator()

# Should all be valid
assert validator.validate_effect_size(0.8, "Cohen's d").is_valid
assert validator.validate_effect_size(0.5, "Pearson's r").is_valid
assert validator.validate_effect_size(0.1, "Eta squared").is_valid

# Should all be invalid
assert not validator.validate_effect_size(2.0, "Pearson's r").is_valid
assert not validator.validate_effect_size(0.05, "Cohen's d").is_valid
assert not validator.validate_effect_size("text", "Cohen's d").is_valid

print("✓ All smoke tests passed")
```

---

## Extending the Validator

To add support for new measure types:

```python
# In EffectSizeValidator.VALID_RANGES
"Cohen's f": (-2, 2),  # New measure type
"Glass's delta": (-4, 4),

# In EffectSizeValidator.OUTLIER_THRESHOLDS
"Cohen's f": (-3, 3),

# In MeasureType enum (optional)
COHENS_F = "Cohen's f"

# In MeasureType.normalize() (optional)
"cohens f": "Cohen's f",
```

Then add tests in `tests/test_effect_size_validator.py`:

```python
def test_cohens_f_valid(self, validator):
    """Cohen's f values in range should be valid."""
    result = validator.validate_effect_size(0.5, "Cohen's f")
    assert result.is_valid
```

---

## See Also

- `src/qa/effect_size_validator.py` — Full validator implementation
- `tests/test_effect_size_validator.py` — Test suite (65 tests)
- `scripts/clean_effect_sizes.py` — Batch cleanup script
- `docs/EFFECT_SIZE_CLEANUP_REPORT_2026-03-02.md` — Implementation report

