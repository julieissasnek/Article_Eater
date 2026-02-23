# WebOfBelief Stabilization Contract

Date: 2026-02-19

## Scope
This contract governs changes to `src/services/web_of_belief.py` and extracted modules in `src/services/web_of_belief_modules/`.

## Freeze Policy
1. No net-new product features are added to `WebOfBelief` until invariants and baseline probes remain green for two consecutive baseline runs.
2. Allowed changes during freeze:
   - refactor-only structural moves,
   - bug fixes,
   - test and probe hardening,
   - performance instrumentation.
3. Every mutating-path change must include:
   - module/wrapper parity coverage where applicable,
   - invariant checks,
   - targeted regression tests.

## Runtime Safeguards
1. `WebOfBelief.assert_invariants()` is the canonical integrity checker.
2. Set `WEB_OF_BELIEF_ASSERT_INVARIANTS=1` to enforce invariants at runtime after mutating operations.
3. Health probe:
   - quick probe: `python3 scripts/probe_web_of_belief_health.py --iterations 400 --seed 1337`
   - baseline runner: `python3 scripts/run_web_of_belief_health_baseline.py --iterations 5000 --seeds 1337,2026,4242`

## Exit Criteria
1. Invariant suite passes.
2. Stress baseline passes for configured seeds/iterations.
3. Focused WebOfBelief regression suites pass.
4. Enum drift check remains `0`.
5. No known invariant violations in logs for debug-invariant-enabled runs.

