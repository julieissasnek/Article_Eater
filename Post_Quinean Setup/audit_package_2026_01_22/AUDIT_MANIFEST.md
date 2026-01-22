# Audit Package Manifest

**Date**: January 22, 2026
**Version**: V21.0.0 (Post-Quinean)
**Purpose**: Governance and infrastructure audit closure

---

## Files Included

### 1. Backend Dependency Definition
| File | Status | Notes |
|------|--------|-------|
| `requirements.txt` | INCLUDED | Full Python dependencies (FastAPI, SQLAlchemy, etc.) |
| `pyproject.toml` | INCLUDED | Minimal - contains only ruff linting config |

### 2. CI/Workflows
| File | Status | Notes |
|------|--------|-------|
| `.github/workflows/*` | **NOT PRESENT** | No CI workflows exist in the repository |

**Gap Note**: The Project_Constitution.md references CI gates ("CI gates (governance, orphan sweep, ledger delta) must pass"), but `.github/workflows/` directory does not exist. This is a governance gap that should be addressed.

### 3. Governance Documents
| File | Status | Notes |
|------|--------|-------|
| `CLAUDE.md` | INCLUDED | Full governance file (12KB) - AI agent instructions |
| `Project_Constitution.md` | INCLUDED | Core project rules (1.1KB) |

### 4. Run Entrypoint Instructions
| File | Status | Notes |
|------|--------|-------|
| `bin/article_eater` | INCLUDED | Main CLI entrypoint script |
| `bin/prod_smoke.sh` | INCLUDED | Production smoke test script |
| `bin/release_and_smoke.sh` | INCLUDED | Release verification script |
| `scripts/article_eater_wrapper.sh` | INCLUDED | Actual Python runner |
| `RUN_INSTRUCTIONS.md` | INCLUDED | New - comprehensive run documentation |

### 5. Additional Documentation (Sprint F3)
| File | Status | Notes |
|------|--------|-------|
| `DESIGN_RATIONALE.md` | INCLUDED | Theory of the System (Naur item) |
| `INVARIANTS.md` | INCLUDED | System invariants (Lamport item) |
| `ARCHITECTURE_DIAGRAM.md` | INCLUDED | Visual documentation (Parnas item) |

---

## Audit Findings Summary

### Present and Compliant
1. **Dependencies**: `requirements.txt` is comprehensive and up-to-date
2. **Governance**: `CLAUDE.md` and `Project_Constitution.md` exist at repo root
3. **Entrypoints**: Clear CLI scripts in `bin/` with wrapper in `scripts/`
4. **Documentation**: Design rationale, invariants, and architecture now documented

### Gaps Identified
1. **No CI/CD Workflows**: `.github/workflows/` is missing
   - Constitution references CI gates that don't exist
   - Recommendation: Create workflows for governance checks, tests, and ledger validation

2. **No README.md**: Root-level README is absent
   - Recommendation: Create from RUN_INSTRUCTIONS.md or CLAUDE.md summary

3. **pyproject.toml is incomplete**: Only has ruff config
   - Dependencies are in requirements.txt (acceptable but not modern)
   - Recommendation: Consider migrating to full pyproject.toml with dependencies

---

## Verification Commands

```bash
# Verify dependencies can be installed
pip install -r requirements.txt

# Run core tests
pytest tests/test_causal_classifier.py tests/test_reporting.py \
       tests/test_bridge_warrants.py tests/test_query_response.py -v

# Run smoke test
./bin/prod_smoke.sh

# Check governance
python scripts/check_governance.py
```

---

## Sign-Off

This audit package contains all requested files that exist in the repository. The CI/CD gap should be addressed in a future sprint before production deployment.
