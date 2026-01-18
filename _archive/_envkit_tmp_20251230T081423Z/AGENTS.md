# Repo Agent Contract

Applies to ALL AI assistants (Claude, Codex, ChatGPT).

## Golden Command
```
./bin/prod_smoke.sh
```

## Safety Rules
1. No deletions — archive first
2. Minimal changes
3. Test before commit
4. Bump version on code changes
5. No bypass of release gates

## For Claude
- Run `./bin/claude_start.sh` at session start
- Read `.aidev/context.md`
- Use `./bin/claude_diagnose.sh` on errors
- Update `.aidev/claude_memory.md` at session end

## For Codex
- Follow `templates/codex_config.toml`
- Follow `templates/codex_default.rules`

## Forbidden
```
rm -rf, sudo, git reset --hard, git clean, curl | bash
```

## Key Commands
| Command | Purpose |
|---------|---------|
| `./bin/prod_smoke.sh` | ONE TRUTH — verify all |
| `./bin/test.sh` | Run tests |
| `./bin/version.sh bump` | Increment version |
| `./bin/claude_diagnose.sh` | Diagnose errors |
