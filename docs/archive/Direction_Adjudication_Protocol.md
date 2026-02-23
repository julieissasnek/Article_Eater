# Direction Adjudication Protocol (HITL + LLM + RAG)

## Goal

Resolve uncertain or theory-tension direction claims using external evidence, not model priors alone.

## Inputs

- Claim queue: `data/review/theory_direction_tension_queue.json`
- Question packet: `docs/HITL_LLM_RAG_direction_questions.md`
- Override template: `data/review/direction_overrides.template.json`

## Evidence Standard

Direction may be set to `increase`, `decrease`, or `no_effect` only if at least one is present:

- Direct statistical sign evidence (`beta`, `r`, signed `t/d`) from paper text/table.
- Explicit author language in abstract/results/discussion/conclusion.
- High-quality secondary summary (meta-analysis/review) with clear directional statement.

If evidence is ambiguous, set direction to `unknown`.

## Required Fields for Override

Each override entry should include:

- `claim_id`
- `direction` (`increase|decrease|no_effect|unknown`)
- `status` (`approved` to apply)
- `reviewer`
- `rationale`
- `evidence_url`
- `evidence_quote`
- `updated_at` (UTC ISO timestamp)

## RAG/LLM Prompt Pattern

Use this pattern for each claim:

1. Retrieve paper abstract + results + discussion snippets for the exact IV→DV pair.
2. Ask for direction classification with citation-backed justification.
3. Reject answers without quote evidence and source URL.

## Re-run

Place approved entries in `data/review/direction_overrides.json`, then rerun:

```bash
python3 -m src.extraction.batch_extract --method enhanced --direction-mode default
```

Overrides are ingested automatically.
