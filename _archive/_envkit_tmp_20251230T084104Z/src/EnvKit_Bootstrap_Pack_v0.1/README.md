# EnvKit Bootstrap Pack v0.1

Unzip this pack at the *root* of any repository to add a portable “dev+governance” environment.

Core entrypoints:
- `./envkit_bootstrap.sh` — install/refresh (archives replacements under `_archive/envkit/<timestamp>/`)
- `./bin/prod_smoke.sh` — one truth command (fingerprint → rebuild decision → up → basic checks)
- `./bin/release_and_smoke.sh` — optional release gate then smoke

Quick start:

```bash
unzip -o EnvKit_Bootstrap_Pack_v0.1.zip
./envkit_bootstrap.sh
./bin/prod_smoke.sh
```
