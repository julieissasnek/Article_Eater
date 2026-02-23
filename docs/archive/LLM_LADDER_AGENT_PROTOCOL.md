# LLM Ladder Agent Protocol

Date: 2026-02-18  
Purpose: Run the same extraction benchmark at high, balanced, and low model tiers and compare quality/cost proxies consistently across Codex, CC, and AG.

## Contract

- Input:
  - queue CSV (paper selection source)
  - model profiles JSON (`name`, `provider`, `model`)
  - fixed variants (`strict_gate` recommended baseline)
- Output:
  - per-profile pilot artifacts (JSON)
  - merged ladder summary:
    - `claims`
    - `mapped_both_pct`
    - `suspect_claims_pct`
    - `unknown_direction_pct`
    - `precision_proxy = mapped_both_pct - suspect_claims_pct - unknown_direction_pct`

## Standard Commands

Start detached (parallel jobs, terminal remains free):

```bash
python3 scripts/run_llm_table_ladder_agent.py start \
  --profiles config/llm_table_pilot_profiles.codex.json \
  --n-pdfs 5 \
  --variants strict_gate \
  --mode parallel \
  --detach \
  --tag pilot5
```

Check status:

```bash
python3 scripts/run_llm_table_ladder_agent.py status \
  --manifest data/production/llm_pilot/<RUN_ID>/ladder_manifest.json
```

Build merged comparison summary:

```bash
python3 scripts/run_llm_table_ladder_agent.py summarize \
  --manifest data/production/llm_pilot/<RUN_ID>/ladder_manifest.json
```

## Provider Profiles

- Codex no-key path: `provider = "codex_exec"` (uses `codex exec`).
- OpenAI/Gemini/Ollama paths are supported by `run_llm_table_pilot.py` via `provider` in profile config.
- Keep profile names stable (`upper_*`, `balanced_*`, `low_*`) for comparable reporting.

## Portability Notes for CC/AG

- Reuse the same script and output schema.
- Only swap the `--profiles` JSON for each environment.
- Keep:
  - same `--n-pdfs`
  - same `--variants`
  - same queue CSV snapshot
  to preserve fair comparisons.
