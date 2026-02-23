# RAG + LLM Direction Consensus (No HITL)

Script: `scripts/run_direction_rag_ladder.py`

## What It Does
- Retrieves local evidence chunks per tension claim (PDF preprocess cache + structured/abstract claim quotes).
- Runs multi-model direction adjudication from profile config.
- Verifies grounding (chunk IDs + exact quote presence + lexical/stat sign consistency).
- Applies consensus (`2-of-3` by default) and emits override JSON.

## Hard Gates (Built-In)
- Preflight fails the run if any are true:
  - tension queue is empty,
  - required provider credentials are missing,
  - provider connectivity check fails.
- Post-run fails the run if any are true:
  - overrides list is empty,
  - all model votes failed,
  - no direction changes (unless `--allow-noop`).
- Failed runs write:
  - `*_failed.json` report artifact,
  - `*_failed.json` overrides artifact.

## Inputs
- Queue: `data/review/theory_direction_tension_queue.json`
- Claims: `data/production/structured_claims.json`
- Abstract claims: `data/production/abstract_claims.json`
- Preprocess cache: `data/production/pdf_preprocess_cache`
- Profiles: `config/direction_rag_profiles.openai.example.json` (or your own)

## Required For External Models
- Set provider credentials in shell env (example):
  - `OPENAI_API_KEY` for `provider=openai`
  - `GOOGLE_API_KEY`/`GEMINI_API_KEY` for `provider=gemini`
  - local Ollama server for `provider=ollama`

## Pilot Run
```bash
python3 scripts/run_direction_rag_ladder.py \
  --profiles config/direction_rag_profiles.openai.example.json \
  --limit 10 \
  --top-k-chunks 8 \
  --model-timeout-s 90 \
  --output-overrides data/review/direction_overrides.rag_llm_consensus.limit10.json \
  --output-report data/review/direction_rag_llm_consensus_report.limit10.json
```

If you intentionally need to bypass connectivity preflight:
```bash
python3 scripts/run_direction_rag_ladder.py \
  --profiles config/direction_rag_profiles.openai.example.json \
  --skip-preflight-connectivity \
  --allow-noop
```

## Full Queue Run
```bash
python3 scripts/run_direction_rag_ladder.py \
  --profiles config/direction_rag_profiles.openai.example.json \
  --top-k-chunks 10 \
  --model-timeout-s 120 \
  --output-overrides data/review/direction_overrides.rag_llm_consensus.json \
  --output-report data/review/direction_rag_llm_consensus_report.json
```

## Apply Overrides
```bash
python3 -m src.extraction.batch_extract \
  --method enhanced \
  --direction-overrides-path data/review/direction_overrides.rag_llm_consensus.json \
  --output-path data/production/structured_claims.rag_llm_consensus.json
```

## Optional Extraction Success Gate
You can ask the script to validate extraction output against a baseline:
```bash
python3 scripts/run_direction_rag_ladder.py \
  --profiles config/direction_rag_profiles.openai.example.json \
  --check-extraction-output data/production/structured_claims.rag_llm_consensus.json \
  --baseline-extraction-path data/production/structured_claims.json
```
Validation requires:
- `direction_overrides_applied > 0`
- and either tension decreases or direction counts change vs baseline.

## Notes
- In restricted sandboxes with no network, external-provider calls fail; run from a terminal session with outbound network.
- `provider=codex_exec` depends on local Codex CLI behavior and may be blocked in nested sandboxes.
