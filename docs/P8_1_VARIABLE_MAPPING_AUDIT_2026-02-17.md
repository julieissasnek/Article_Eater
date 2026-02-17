# P8.1 Variable Mapping Coverage Audit

**Date**: 2026-02-17
**Task**: P8.1 (Sprint 8 — Pipeline Reliability Hardening)
**Author**: Codex

## Scope

Audit mapping coverage in production artifacts:
- `data/production/realtime_tables.jsonl`
- `data/production/realtime_rules.jsonl`

Focus:
- env/out node coverage
- unresolved rates
- table→rule mapping consistency
- resolution method quality signals

## Dataset Snapshot

- Rows in `realtime_tables.jsonl`: `12,596`
- Rows in `realtime_rules.jsonl`: `12,596`
- Parse errors: `0`

## Core Findings

### 1. Node coverage is complete, but unresolved IDs remain high

From production tables/rules (identical rowwise values):

- `environment_node_id` unresolved: `3,473 / 12,596` (`27.6%`)
- `outcome_node_id` unresolved: `1,972 / 12,596` (`15.7%`)

Interpretation:
- Mapping coverage is not failing at field presence. It is failing at canonical resolution quality.

### 2. Rule layer faithfully mirrors table layer

- Per-paper count alignment (`paper_id`) between tables and rules: `4,172/4,172` papers matched exactly
- Row-index alignment between table node IDs and rule LHS/RHS vars:
  - Environment: `12,596/12,596` (`100%`)
  - Outcome: `12,596/12,596` (`100%`)

Interpretation:
- Table→rule translation is structurally consistent.
- Current unresolved burden is upstream (canonical mapping and corpus relevance), not a table→rule handoff bug.

### 3. Resolution mode mix indicates heavy fallback usage

`environment_resolution_match_type`:
- `lookup_exact`: `4,823`
- `generic_keyword`: `3,335`
- `unresolved`: `3,473`
- `exact`: `728`
- `fuzzy`: `237`

`outcome_resolution_match_type`:
- `lookup_exact`: `7,589`
- `generic_keyword`: `1,770`
- `unresolved`: `1,972`
- `exact`: `1,240`
- `fuzzy`: `25`

Interpretation:
- Environment mapping is weaker than outcome mapping.
- Large `generic_keyword` share implies coarse normalization pathways are still doing heavy lifting.

### 4. Domain contamination contributes materially

Heuristic architecture-related subset (title/venue/snippet keyword filter):
- Architecture-like rows: `6,988`
- Non-architecture rows: `5,608`

Unresolved rates by subset:
- Architecture-like:
  - env unresolved: `1,464/6,988` (`21.0%`)
  - out unresolved: `985/6,988` (`14.1%`)
- Non-architecture:
  - env unresolved: `2,009/5,608` (`35.8%`)
  - out unresolved: `987/5,608` (`17.6%`)

Interpretation:
- Off-domain corpus mix is a major source of unresolved environment IDs.
- Even in architecture-like rows, unresolved rates remain high enough to justify ontology expansion and mapper improvements.

## Root-Cause Summary

1. **Canonical ontology coverage gap** (especially environment side).
2. **Mapper strategy over-reliance on generic keyword fallback**.
3. **Corpus relevance drift** (non-architecture papers entering production path).

## Recommended Next Actions (P8 follow-on)

1. **P8.2**: Build canonical env/out registry expansion pass using unresolved clusters from this audit (start with highest-frequency unresolved IDs and architecture-like subset first).
2. **P8.3**: Add staged resolver policy:
   - strict dictionary
   - ontology synonym expansion
   - constrained LLM candidate generation
   - unresolved fallback with explicit confidence
3. **P8.6**: Add hard metrics in pipeline output:
   - unresolved env/out rates
   - resolution-match-type distribution
   - architecture-likeness gate pass/fail
4. Add domain gate before ingestion into production dataset to reduce off-domain unresolved noise.

## Reproducibility

Audit run from repo root:
- `python3 scripts/check_enum_drift.py` (separate blocker check; result: 0 drift issues)
- ad-hoc JSONL audits over `data/production/realtime_tables.jsonl` and `data/production/realtime_rules.jsonl` with row-count, unresolved-rate, and alignment checks.

