# AE Install Kit (EnvKit + Contract Smoke Test)
Ports: Source-of-truth in contracts/ports.json.

This is a **drop-in install kit** for:

`/Users/davidusa/REPOS/Article_Eater_v20_7_43`

Files:
- `install_ae_envkit.sh` — one-command installer
- `doctor.sh` — diagnostics
- `README_INSTALL_AE_ENVKIT.md` — this file

## Put these files here
Copy all three into your **repo root**:

`/Users/davidusa/REPOS/Article_Eater_v20_7_43/`

## EnvKit input (required for EnvKit bootstrap)
Place your EnvKit zip here:

`/Users/davidusa/REPOS/Article_Eater_v20_7_43/Envkit.zip`

Or run with:

```bash
ENVKIT_ZIP_PATH=/path/to/Envkit.zip bash install_ae_envkit.sh
```

## Run installer
From repo root:

```bash
bash install_ae_envkit.sh
```

This will:
1) Bootstrap EnvKit (if `.envkit/` isn’t already present)  
2) Create/reuse `.venv/`  
3) Install `requirements.txt` (plus `jsonschema`)  
4) Create `./bin/article_eater` wrapper **if** the contract CLI exists  
5) Run a contract smoke test **if** the contract example bundle exists  

## If something fails
Run:

```bash
bash doctor.sh
```

It prints exactly what is missing and what to do next.
