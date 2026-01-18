# EnvKit Bootstrap Pack v0.2.2

Unzip this pack at the *root* of any repository to add a portable “dev + governance” environment.

## Core entrypoints

- `./envkit_bootstrap.sh` — install/refresh (archives replacements under `_archive/envkit/<timestamp>/`)
- `./bin/prod_smoke.sh` — one truth command (fingerprint → rebuild decision → up → basic checks)
- `./bin/release_and_smoke.sh` — optional release gate then smoke

## Quick start

```bash
unzip -o EnvKit_Bootstrap_Pack_v0.2.2.zip
./envkit_bootstrap.sh
./bin/prod_smoke.sh
```

## v0.2.2 helper commands

```bash
./bin/version.sh check
./bin/context.sh
./bin/claude_start.sh
./bin/claude_diagnose.sh "paste an error message here"
```

Notes
- `./bin/test.sh` is a thin wrapper; configure `testing.command` in `envkit.yml` to enable a real test suite.
- Docker is required for `runtime.kind: docker_compose` workflows.


## New in v0.2.2

- Release pack now emitted under `Releases/EnvKit_Bootstrap_Pack_vX.Y.Z.zip`.
- `./bin/prod_smoke.sh` handles endpoints more robustly and skips compose when absent.
- Version propagation handles filenames with spaces.
