# System Improvements Recommendations

*Created: 2026-02-23*

This document captures recommended system improvements that were identified during a design review but deferred due to risk/effort considerations.

---

## Completed Improvements

| Improvement | Status | Files |
|-------------|--------|-------|
| Pre-commit validation hook | DONE | `.pre-commit-config.yaml`, `scripts/validate_all_templates.py` |
| Centralized template loader with schema validation | DONE | `src/data/template_loader.py` |
| TASKS.md archival | DONE | Reduced from 4059 to 110 lines |

---

## Recommended: Split Large Files

### Problem

Several files exceed 3000 lines, making them difficult to maintain:

| File | Lines | Recommendation |
|------|-------|----------------|
| `src/cmr/template_computations.py` | 3821 | Split by template category |
| `src/services/epistemic_causal_bridge.py` | 3618 | Split by responsibility |
| `src/services/web_persistence.py` | 3147 | Split into query/persistence layers |

### Proposed Split for `template_computations.py`

```
src/cmr/computations/
    __init__.py          # Re-export all compute functions
    base.py              # ComputeResult, OutputType, helpers
    visual.py            # VF1, VF2, VF3, COL1, COL2
    light.py             # L1, L2, L3, L4, L5
    material.py          # MAT1, MAT2, MAT3, MAT4, MAT5
    spatial.py           # SC1, SC2, SC3, SC4, TP1-TP4
    social.py            # SOC1, SOC2, SOC3
    creative.py          # CREA1, CREA2, CREA3, CREA4
    stress.py            # T4, T6, T7, T10, T14, T15
    memory.py            # T17, T18, T23, T28
    nature.py            # VIEW1, OLF1
```

### Risk Assessment

- **Risk**: Medium (could break imports, require test updates)
- **Mitigation**: Add `__init__.py` that re-exports all functions for backward compatibility
- **Effort**: 2-4 hours
- **Recommendation**: Do this during a dedicated refactoring sprint with full test coverage

---

## Recommended: Runtime Type Checking

### Problem

Type hints exist but aren't enforced at runtime, so type errors can slip through.

### Solution

Add `beartype` for runtime type checking on critical functions:

```python
# Add to requirements.txt
beartype>=0.18.0

# Usage in critical functions
from beartype import beartype

@beartype
def compute_confidence(mechanism_chain: list[dict]) -> float:
    ...
```

### Risk Assessment

- **Risk**: Low (decorators are additive, don't change logic)
- **Effort**: 1-2 hours to add to critical paths
- **Recommendation**: Add to new code first, then incrementally to existing critical functions

### Installation

```bash
pip install beartype
# Add to requirements.txt: beartype>=0.18.0
```

---

## Using Pre-commit Hooks

The pre-commit configuration has been created. To activate:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks in this repo
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

This will automatically:
1. Validate JSON syntax
2. Validate template schema compliance
3. Validate Toulmin justifications
4. Run ruff linting
5. Fix trailing whitespace

---

## Using the Template Loader

The new template loader provides schema validation:

```python
from src.data.template_loader import load_template, load_all_templates

# Load single template with validation (default)
template = load_template("ED_HIPPOCAMPAL_ENCODING_001")

# Load without validation (faster, for trusted contexts)
template = load_template("ED_HIPPOCAMPAL_ENCODING_001", validate=False)

# Load all templates
templates = load_all_templates()

# Load only calibrated templates
calibrated = get_calibrated_templates()
```

### Error Handling

```python
from src.data.template_loader import (
    load_template,
    TemplateNotFoundError,
    TemplateValidationError,
)

try:
    template = load_template("INVALID_TEMPLATE")
except TemplateNotFoundError:
    print("Template not found")
except TemplateValidationError as e:
    print(f"Validation errors: {e.errors}")
```

---

## Priority Order for Future Work

1. **Enable pre-commit hooks** (immediate, no risk)
2. **Use template loader in new code** (immediate, no risk)
3. **Add beartype to new functions** (low risk, incremental)
4. **Split large files** (medium risk, defer to refactoring sprint)

---

*Document maintained by: System Design Sprint (2026-02-23)*
