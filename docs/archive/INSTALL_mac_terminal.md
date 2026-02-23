# Install and Run – macOS (no git, Terminal only)

This guide is for users on macOS who have downloaded the
`Article_Eater_v20_7_3_reconciled.zip` file and are comfortable using
the Terminal, but do **not** plan to use git.

## 1. Unzip the archive

1. Locate `Article_Eater_v20_7_3_reconciled.zip` in Finder.
2. Double‑click to unzip. You should see a folder such as:
   * `Article_Eater_v20_7_3_reconciled/`

Move this folder somewhere convenient (e.g. `Documents/Article_Eater/`).

## 2. Open Terminal in the repo directory

1. Open **Terminal**.
2. Change into the extracted folder, for example:
   ```bash
   cd ~/Documents/Article_Eater/Article_Eater_v20_7_3_reconciled
   ```

All commands below assume you are in this directory.

## 3. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If `python3` is not found, install Python 3 (e.g., via python.org or Homebrew)
and then retry.

To deactivate later:
```bash
deactivate
```

## 4. Install Python dependencies

With the virtual environment active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs the core dependencies needed for the backend, agents, and
governance checks.

## 5. Run basic sanity checks

From the repo root:

```bash
python scripts/sanity_check.py
python scripts/offline_pipeline_smoke.py
python scripts/run_all_checks.py
```

These scripts are designed to fail fast if the environment or wiring is
obviously broken.

* If all three complete without errors, your local install is healthy.
* If something fails, check the error message and consult:
  * `docs/CONFIGURATION_GUIDE.md`
  * `docs/ARCHITECTURE_OVERVIEW.md`
  * `docs/THREAT_MODEL_v1.md`

## 6. Running the main application (example pattern)

Different labs may run Article Eater slightly differently. A typical pattern is:

1. Start the backend API (for example, using uvicorn on the FastAPI app):
   ```bash
   # Example pattern – adjust if your lab uses a different command.
   scripts/run_api.sh --reload
   ```

2. Navigate in your browser to the URL printed in the terminal
   (often `http://127.0.0.1:8000` or similar).

For the exact entrypoint your lab uses, see:

* `README.md` (if present)
* `docs/ARCHITECTURE_OVERVIEW.md`
* Any lab‑specific handoff notes under `docs/` or `HANDOFF_INSTRUCTIONS_FINAL.md`.

## 7. Optional: explore the graph and rules

Once the backend is running:

* Graph navigation (read‑only):
  * `GET /graph/events`
  * `GET /graph/topic/{topic}`

* Rule GUI (read‑only for most users; editable for admins with a password):
  * See `docs/STUDENT_HOWTO_RULE_GRAPH.md` for the URLs and expected flows.

## 8. Updating later

If a future patch kit is provided with its own `install_or_update.py`,
you can:

1. Unzip the patch kit.
2. Set the environment variable `AE_TARGET_DIR` to point at this install.
3. Run the installer from the patch directory, for example:
   ```bash
   cd /path/to/patch_kit
   AE_TARGET_DIR=/path/to/Article_Eater_v20_7_3_reconciled python3 scripts/install_or_update.py
   ```

This will copy new files into your existing install and archive any
replaced files under `archive/_replaced_<timestamp>/`.
