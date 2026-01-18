# Claude handoff: implement against this contract

You are Claude working on **Article Finder** (AF) and/or **Article Eater** (AE).
Your job is to implement and validate the **file-bundle interface** described in this pack.

## Non-negotiables
1) AF MUST generate an **input bundle** containing:
   - `paper.pdf`
   - `paper.json` that validates against `schemas/ae.paper.v1.schema.json`

2) AE MUST produce an **output bundle** containing:
   - `result.json` validating `schemas/ae.result.v1.schema.json`
   - `claims.jsonl` (each line validates `schemas/ae.claim.v1.schema.json`)
   - `rules.jsonl`  (each line validates `schemas/ae.rule.v1.schema.json`)
   - `provenance.json` validating `schemas/ae.provenance.v1.schema.json`
   - `audit.log.jsonl` (each line validates `schemas/ae.audit_event.v1.schema.json`)

3) AE MUST support the canonical CLI:
   `article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile <fast|standard|deep> --hitl <off|auto|required>`

4) AF MUST NOT parse AE logs for success. AF MUST use `result.json.status` as truth.

## Deliverables expected from you
### If you are working on AE
- Provide a `article_eater` CLI that writes the required artifacts exactly.
- Validate outputs against provided JSON Schemas.
- Ensure deterministic filenames in `result.json.artifacts`.

### If you are working on AF
- Implement creation of input bundles from your corpus database.
- Implement ingestion of AE output bundles, including status mapping and indexing.
- Validate `paper.json` and AE outputs against schemas; surface errors clearly.

## Tests
- Add a small test that:
  - copies `examples/input_bundle_minimal/` into a temp dir,
  - runs AE (or a stubbed AE if you’re on AF side),
  - validates output bundle against schemas,
  - ensures `paper_id` and `pdf_sha256` are preserved.

## Examples
See `examples/` for a minimal input bundle and a sample output bundle.
