# Project Constitution (EnvKit)

1. No deletions by default. Archive prior copies under `_archive/envkit/<timestamp>/`.
2. One truth command: `./bin/prod_smoke.sh`.
3. Bootstrap must be idempotent.
4. Rebuild only when runtime inputs change (fingerprint).
5. AI-safe operation via repo-local `AGENTS.md` and optional exec policy templates.
