# P8.4 pgmpy BN Inference Wiring

**Date**: 2026-02-17  
**Task**: P8.4 (Sprint 8 — Pipeline Reliability Hardening)  
**Author**: Codex

## Summary

Integrated optional `pgmpy` inference hooks into incremental BN service with safe degradation when dependency is absent.

Updated files:
- `src/services/incremental_bn.py`
- `tests/test_incremental_bn.py`

## New Capabilities

### In `IncrementalBNBuilder`

- `build_pgmpy_model()`
  - Converts current edge set into a pgmpy Bayesian network
  - Builds binary CPDs from learned edge means
  - Validates model via `check_model()`

- `query_posterior(target, evidence)`
  - Runs `VariableElimination` query and returns `P(target=1 | evidence)`

- `is_d_separated(x, y, observed)`
  - Returns d-separation status via pgmpy connectivity checks

- `get_markov_blanket(node)`
  - Returns Markov blanket for a node

### New module convenience wrappers

- `query_posterior(...)`
- `check_d_separation(...)`
- `get_markov_blanket(...)`

### `get_edge_estimate(...)` upgrade

- Added optional `use_pgmpy_fallback` flag.
- Behavior:
  - If direct edge exists -> return learned edge mean (unchanged)
  - If missing and fallback enabled -> attempt pgmpy posterior `P(target=1 | source=1)`

## Dependency Handling

- `pgmpy` import is optional and version-tolerant:
  - `DiscreteBayesianNetwork` (newer)
  - `BayesianNetwork` (older fallback)
- When unavailable, inference APIs return `None` without raising.

## Verification

Commands:
```bash
python3 -m py_compile src/services/incremental_bn.py
./venv/bin/pytest -q tests/test_incremental_bn.py tests/test_grounded_expert_agent.py
```

Result:
- `47 passed`

Environment note:
- `pgmpy` not installed in current runtime, so tests verify graceful fallback behavior.

