# Codex Model Switch Playbook

Date: 2026-02-18  
Owner: David + Codex  
Purpose: Keep default model stable, but allow per-session model/cost switching for specific tasks.

## 1) Keep Default As-Is

Your default remains in `~/.codex/config.toml`:

```toml
model = "gpt-5.3-codex"
model_reasoning_effort = "high"
```

Do not change this unless we explicitly decide to update global defaults.

## 2) One-Command Session Switching

Use these from terminal when launching a new Codex session.

### Max quality (upper-bound experiments)

```bash
codex -m gpt-5.3-codex -c model_reasoning_effort="xhigh"
```

### Balanced

```bash
codex -m gpt-5.2-codex -c model_reasoning_effort="medium"
```

### Low cost

```bash
codex -m gpt-5.1-codex-mini -c model_reasoning_effort="low"
```

### Preferred helper (this repo)

Use the wrapper script:

```bash
scripts/codex_mode.sh low --task "Run extraction pilot"
scripts/codex_mode.sh balanced --task "Patch and validate"
scripts/codex_mode.sh max --task "Discuss results and decide next step"
```

Preserve prior state while switching model tier:

```bash
# branch from the previous session context
scripts/codex_mode.sh low --fork-last --task "Run pilot"
scripts/codex_mode.sh balanced --fork-last --task "Repair issues"
scripts/codex_mode.sh max --fork-last --task "Interpret results"
```

Resume (continue) instead of fork:

```bash
scripts/codex_mode.sh balanced --resume-last --task "Continue same thread"
```

Dry run:

```bash
scripts/codex_mode.sh low --dry-run --task "Pilot"
```

## 3) Copy-Paste Startup Prompt (Per Session)

Paste this as the first user message in the session:

```text
Session mode: <MAX|BALANCED|LOW_COST>.
Task focus: <task name>.
If current model does not match this mode, stop and tell me the exact `codex -m ...` restart command.
Then proceed with the run plan and keep a metrics log in docs/CODEX_MODEL_SWITCH_PLAYBOOK.md.
```

Notes:
- Codex cannot reliably self-restart into another model inside the same active session.
- The operator (you) runs the restart command, then resumes.
- `scripts/codex_mode.sh` supports `new`, `resume-last`, and `fork-last` strategies.
- Default strategy is `resume-last` to preserve state by default.
- Use `fork-last` when you want to preserve state but try a different model in a branched run.

## 4) Pilot Commands (5 PDFs)

Upper bound first:

```bash
python3 scripts/run_llm_table_pilot.py \
  --n-pdfs 5 \
  --variants strict_gate,no_gate \
  --profiles config/llm_table_pilot_profiles.json
```

Degradation curve:

```bash
python3 scripts/run_llm_table_pilot.py \
  --n-pdfs 5 \
  --variants strict_gate \
  --profiles config/llm_table_pilot_profiles.json
```

Suggested workflow:

```bash
# 1) Low-cost run
scripts/codex_mode.sh low --fork-last --task "Run 5-PDF pilot extraction and save outputs"

# 2) Balanced repair/QA pass
scripts/codex_mode.sh balanced --fork-last --task "Review pilot outputs and patch issues"

# 3) Max-quality discussion/strategy
scripts/codex_mode.sh max --fork-last --task "Interpret results and choose scale-up plan"
```

## 4b) Detached Ladder Agent (Recommended)

Run upper -> balanced -> low as parallel background jobs:

```bash
python3 scripts/run_llm_table_ladder_agent.py start \
  --profiles config/llm_table_pilot_profiles.codex.json \
  --n-pdfs 5 \
  --variants strict_gate \
  --mode parallel \
  --detach \
  --tag pilot5
```

Then:

```bash
python3 scripts/run_llm_table_ladder_agent.py status --manifest data/production/llm_pilot/<RUN_ID>/ladder_manifest.json
python3 scripts/run_llm_table_ladder_agent.py summarize --manifest data/production/llm_pilot/<RUN_ID>/ladder_manifest.json
```

Protocol details are in `docs/LLM_LADDER_AGENT_PROTOCOL.md`.

## 5) Iteration Log

Append one row per run:

| Date (UTC) | Session Mode | Model | Reasoning | Task | Dataset | Key Metrics | Decision |
|---|---|---|---|---|---|---|---|
| 2026-02-18 | MAX | gpt-5.3-codex | xhigh | setup | n/a | playbook created | baseline process |

## 6) Model Ladder (Editable)

Edit this table as we refine cost/quality tradeoffs:

| Tier | Model | Reasoning | Intended Use |
|---|---|---|---|
| MAX | gpt-5.3-codex | xhigh | method upper-bound / hard failures |
| BALANCED | gpt-5.2-codex | medium | routine extraction + QA |
| LOW_COST | gpt-5.1-codex-mini | low | batch throughput / triage |
