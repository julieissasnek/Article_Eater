# Mandate: Adopt Claim/Update/Complete Protocol Now

Effective immediately for all AI terminals (Claude Code, Codex, Antigravity).

## Required behavior

1. Before starting or continuing any active task, write a claim file:
   - `signals/{TASK_ID}_CLAIMED.json`
2. While working, write heartbeat updates at least every 10 minutes:
   - `signals/{TASK_ID}_UPDATE.json`
3. On completion, write completion file:
   - `signals/{TASK_ID}_COMPLETE.json`
4. Respect active claims from other AIs. Only steal an expired claim using explicit steal metadata.

## Tool to use

Use:
- `scripts/task_signal.py`

Examples:

```bash
python3 scripts/task_signal.py claim --task CC6 --by claude_code --intent "Implement extraction mapper" --output-file src/theory/extraction_mapper.ts
python3 scripts/task_signal.py update --task CC6 --by claude_code --progress 40 --note "Mapper + tests in progress" --file src/theory/extraction_mapper.ts
python3 scripts/task_signal.py complete --task CC6 --by claude_code --notes "Mapper complete and validated" --output-file src/theory/extraction_mapper.ts
```

Check status:

```bash
python3 scripts/task_signal.py status --task CC6
```

## Lease rules

- Default lease: 30 minutes
- Heartbeat cadence: <= 10 minutes
- Lease grace before steal: 5 minutes past expiry
- Steal must include reason and prior owner

