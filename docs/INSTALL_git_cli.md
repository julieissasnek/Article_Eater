# Install and Run – git + Terminal (local developer workflow)

This guide is for developers who are comfortable with **git** and the
command line and want to keep Article Eater under version control on a
local machine.

## 1. Create or choose a Git repository

You have two main options:

1. Initialise a new repo locally and commit the reconciled tree.
2. Clone an existing remote (e.g. GitHub) and then drop the reconciled
   files into it.

### Option A – new local repo

```bash
mkdir Article_Eater
cd Article_Eater
git init
```

Unzip `Article_Eater_v20_7_3_reconciled.zip` **into this directory** so that
files like `MANIFEST.sha256`, `release.keep.yml`, and `src/` sit at the repo
root.

Then commit:

```bash
git add .
git commit -m "Add Article Eater v20.7.3-reconciled"
```

### Option B – existing remote

If you already have a remote (e.g., GitHub):

```bash
git clone <your-remote-url> Article_Eater
cd Article_Eater
```

Then copy the contents of the reconciled tree on top of your working copy,
respecting any local governance rules (e.g., do not delete existing
governance files).

Commit after reviewing the changes:

```bash
git status
git add .
git commit -m "Merge in v20.7.3-reconciled base"
```

## 2. Python environment

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

You can of course adapt this to your usual tooling (conda, poetry, uv, etc.),
but the repository is structured to work out of the box with a plain `venv`
and `pip`.

## 3. Governance and CI

This repo includes:

* `release.keep.yml` and `deprecations.yml` – for drift / deprecation control.
* `.github/workflows/ci.yml` – a CI workflow that can be used in GitHub
  Actions or adapted for other CI systems.
* `scripts/check_governance.py` – a script to run governance checks locally.

Typical pattern for local checks:

```bash
python scripts/check_governance.py
python scripts/run_all_checks.py
```

You may wish to add a pre‑commit hook that calls these scripts or invokes
a richer test command.

## 4. Running tests

With the virtual environment active:

```bash
pytest
```

The suite includes:

* API smoke tests
* Governance sanity tests
* Engine / relational analysis tests

## 5. Running the application

The exact entrypoint may vary by lab, but a standard pattern is:

```bash
# Example; adjust to your app.main definition.
scripts/run_api.sh --reload
```

Refer to:

* `docs/ARCHITECTURE_OVERVIEW.md`
* `docs/CONFIGURATION_GUIDE.md`
* `docs/USAGE.md`
* Any lab‑specific `README` or handoff notes.

## 6. Working with branches

A reasonable branch strategy is:

* `main` – tracking reconciled / stable releases (including v20.7.3).
* `feature/*` – experimental work (e.g., Neo4j backend, new agents).
* `calibration/*` – branches dedicated to BBN / confidence calibration.

Governance kit v3 can be used to document conversations and intent behind
larger changes; see `docs/AI_HANDOFF_PROMPT_FOR_GOVERNANCE_KIT.md`.

## 7. Using this tree as an overlay

The script `scripts/install_or_update.py` is designed to apply the current
tree as a non‑destructive overlay onto another target directory:

```bash
AE_TARGET_DIR=/path/to/target python3 scripts/install_or_update.py
```

This copies files from the current repo into the target, archiving any
replaced files under `archive/_replaced_<timestamp>/` in the target tree.
