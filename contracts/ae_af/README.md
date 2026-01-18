# Article Finder ↔ Article Eater Contract Pack (v1)

This pack defines the canonical file-bundle contract between **Article Finder (AF)** and **Article Eater (AE)**.

## Design goals
- **Stable interface**: AF depends on files + schemas, not AE internals.
- **Idempotent**: dedupe via `paper_id` + `pdf_sha256`.
- **HITL-capable**: AE can request review without breaking automation.
- **BN-ready**: AE emits normalized claims + Bayesian rule candidates.

## Invocation (normative)
AE MUST support a CLI that consumes an input bundle directory and writes an output bundle directory:

```bash
article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile deep --hitl auto
```

AF SHOULD treat AE as a black box, and only read `result.json` plus referenced artifacts.

## Bundle structure (normative)
### Input bundle (AF → AE)
Required:
- `paper.pdf`
- `paper.json` (schema: `schemas/ae.paper.v1.schema.json`)

Optional:
- `abstract.txt`
- `fulltext.txt`
- `citations.json`
- `figures/`
- `tables/`
- `overrides.json` (HITL overrides; schema TBD by project)

### Output bundle (AE → AF)
Required:
- `result.json` (schema: `schemas/ae.result.v1.schema.json`)
- `claims.jsonl` (records validate against `schemas/ae.claim.v1.schema.json`)
- `rules.jsonl`  (records validate against `schemas/ae.rule.v1.schema.json`)
- `provenance.json` (schema: `schemas/ae.provenance.v1.schema.json`)
- `audit.log.jsonl` (records validate against `schemas/ae.audit_event.v1.schema.json`)

Optional:
- `review_items.jsonl` (schema: `schemas/ae.review_item.v1.schema.json`)
- `fulltext.extracted.txt`
- `tables/`, `figures/`, `spans.jsonl`, `cost.json`

## Status mapping (recommended)
AE status (`result.json.status`) → AF corpus status
- `SUCCESS` → `processed_success`
- `PARTIAL_SUCCESS` → `processed_partial` (or `needs_human_review` if blocking issues)
- `FAIL` → `processed_fail`

## Versioning
Each schema has a `schema_id` (e.g., `ae.paper.v1`). Bump versions only with backwards-compatible care.
