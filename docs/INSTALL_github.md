# Install and Run – GitHub‑hosted repository

This guide is for users who will primarily work with Article Eater via a
GitHub repository (e.g., students pulling from a course repo, or
collaborators cloning from a lab repo).

## 1. Prepare the GitHub repository

1. On GitHub, create a new private or public repository:
   * Example name: `Article_Eater`.
2. On your machine, clone it:
   ```bash
   git clone <your-github-url> Article_Eater
   cd Article_Eater
   ```

3. Unzip `Article_Eater_v20_7_3_reconciled.zip` and copy its contents
   into this cloned directory, so that files like `MANIFEST.sha256`,
   `release.keep.yml`, `Project_Constitution.md`, and `src/` are at the
   repo root.

4. Commit and push:

   ```bash
   git add .
   git commit -m "Seed repo with Article Eater v20.7.3-reconciled"
   git push origin main
   ```

From this point on, students or collaborators can simply:

```bash
git clone <your-github-url> Article_Eater
```

to get a fresh copy.

## 2. Student / collaborator workflow

For students:

1. Clone the repository:
   ```bash
   git clone <your-github-url> Article_Eater
   cd Article_Eater
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run the basic sanity checks:
   ```bash
   python scripts/sanity_check.py
   python scripts/offline_pipeline_smoke.py
   python scripts/run_all_checks.py
   ```

4. Follow the relevant documentation:
   * `docs/STUDENT_QUICKSTART_Article_Eater_v20_7_3b.md`
   * `docs/STUDENT_HOWTO_RULE_GRAPH.md`
   * `docs/USAGE.md`
   * Any course‑specific handout from your instructor.

## 3. CI on GitHub

The file `.github/workflows/ci.yml` can be enabled as‑is or customised
for your environment. Typical steps in that workflow include:

* Installing dependencies.
* Running governance checks.
* Running unit and smoke tests.

After pushing to GitHub, you should see the CI pipeline run on each push /
pull request, enforcing a minimum level of quality and alignment with the
governance kit.

## 4. Updating a GitHub‑hosted repo from a new kit

If a future patch kit is distributed as a ZIP (e.g.,
`Article_Eater_v20_7_4_patch.zip`):

1. Clone or pull the latest state of your GitHub repo locally.
2. Unzip the patch kit alongside it.
3. From the patch kit directory, run:
   ```bash
   AE_TARGET_DIR=/path/to/local/Article_Eater python3 scripts/install_or_update.py
   ```
4. Review the changes (`git status`, `git diff`), then commit and push.

This keeps your GitHub repository in sync with the patch kit while
preserving archives of replaced files under the target repo’s `archive/`
directory.
