# Antigravity Installer (Single-File Desktop Install)

This document explains how to build and use the **Antigravity Installer** for Article Eater.

The goal is to give non-technical students a *single* Python file they can run on their laptop that will:

- Reconstruct a specific, governed Article Eater release from its concatenated TXT dump.
- Create a local virtual environment.
- Install all Python dependencies from `requirements.txt`.
- Create simple launchers for:
  - the worker (the “brain”), and
  - the Streamlit Control Room (the “eyes”).

The installer is **only a packaging wrapper**. It does **not** change Article Eater’s runtime logic, schema, or governance model.

---

## 1. Inputs and Outputs

### Inputs (Technical Lead / TA)

To build the installer for a given release you need:

1. The **canonical concatenated dump** for that version, e.g.:

   ```text
   Article_Eater_v20_7_43_usability_antigravity_full_concatenated.txt
   ```

2. The builder script from this repo:

   ```text
   scripts/build_antigravity_installer.py
   ```

### Output (Technical Lead / TA)

Running the builder once will produce:

```text
install_article_eater.py
```

This is the **only file** you give to students for the antigravity path.

---

## 2. How the Antigravity Installer Works

When a student runs `install_article_eater.py` on their machine, it will:

1. **Reconstruct the repo**

   - Decompress and parse the embedded concatenated TXT payload.
   - Recreate the Article Eater directory tree under:

     ```text
     ~/ArticleEater_v20
     ```

   - Write all files with the same paths and contents as in the governed release.

2. **Create a virtual environment**

   - Create `~/ArticleEater_v20/venv` (or reuse it if it already exists).
   - Use `python -m venv` (Python 3.10+ required).

3. **Install dependencies**

   - Install packages using:

     ```bash
     pip install -r requirements.txt
     ```

   - All installs happen inside the local `venv`.

4. **Create launchers**

   In `~/ArticleEater_v20`, the installer writes:

   - On **Windows**:
     - `START_BRAIN.bat` — runs the worker (`python -m app.worker`)
     - `START_EYES.bat` — runs the Streamlit Control Room (`streamlit run scripts/ae_streamlit_control_room.py`)

   - On **macOS / Linux**:
     - `start_brain.sh` — runs the worker
     - `start_eyes.sh` — runs the Streamlit Control Room

   These scripts are meant to be double-clicked (Windows) or run from a terminal (macOS/Linux) to give students an easy, repeatable workflow.

> **Important:** API keys and secrets are **not** embedded in the installer. Students must still configure them via `.env` or environment variables as described in `SECRETS_AND_KEYS.md` and `config/.env.example`.

---

## 3. Technical Lead Instructions – Building the Installer

These steps are for the Technical Lead or maintainers, not for students.

1. **Prepare a clean folder**

   Create a temporary directory on your machine and copy into it:

   ```text
   Article_Eater_v20_7_43_usability_antigravity_full_concatenated.txt
   scripts/build_antigravity_installer.py
   ```

   (You can copy the builder out of the repo’s `scripts/` folder.)

2. **Run the builder**

   From that folder, run:

   ```bash
   python build_antigravity_installer.py
   ```

   You should see logs such as:

   - `--- ANTIGRAVITY INSTALLER FACTORY ---`
   - `Reading Article_Eater_v20_7_43_usability_antigravity_full_concatenated.txt...`
   - `Compressing payload (gzip)...`
   - `Encoding payload (base64)...`
   - `Writing install_article_eater.py...`

3. **Verify the artifact**

   Confirm:

   - `install_article_eater.py` exists.
   - Its size is on the order of a couple of MB (not a few kilobytes).
   - Optionally, open it to verify it contains:
     - A `PAYLOAD_B64 = "..."` block.
     - Launcher creation logic for START_BRAIN / START_EYES.

4. **Sanity-check on a fresh machine**

   On a machine *without* an existing Article Eater install:

   - Ensure Python ≥ 3.10 is available.
   - Run:

     ```bash
     python install_article_eater.py
     ```

   - Confirm that:
     - `~/ArticleEater_v20` is created.
     - A `venv` directory exists inside it.
     - `requirements.txt` is installed with no fatal errors.
     - Launchers (`START_BRAIN` / `start_brain.sh` and `START_EYES` / `start_eyes.sh`) exist.

5. **Distribute to students**

   Once you are satisfied that the installer works on at least one “typical student” machine:

   - Share **only** `install_article_eater.py` (e.g., via Canvas, shared drive, or email).
   - Do **not** ask students to run the builder or handle the concatenated TXT.

---

## 4. Student Instructions – Using the Installer

These are the instructions students should see (you can reuse or adapt this text in course materials):

1. **Prerequisites**

   - Python 3.10 or newer installed.
   - A stable internet connection (for `pip install` and for the Article Eater APIs).

2. **Run the installer**

   - Download `install_article_eater.py` to a folder on your machine.
   - Run it with Python:
     - On **Windows**: double-click it or run

       ```bash
       python install_article_eater.py
       ```

     - On **macOS / Linux**: run

       ```bash
       python3 install_article_eater.py
       ```

   - Follow the prompts:
     - The installer will propose an install location like:

       ```text
       /Users/you/ArticleEater_v20
       ```

     - If that folder already exists, you can choose to overwrite or abort.

3. **Start the worker (“brain”)**

   - On **Windows**:
     - Go to the `ArticleEater_v20` folder.
     - Double-click `START_BRAIN.bat`.

   - On **macOS / Linux**:
     - Open a terminal in `~/ArticleEater_v20`.
     - Run:

       ```bash
       ./start_brain.sh
       ```

   - Leave this window open; it is now processing jobs in the background.

4. **Start the dashboard (“eyes”)**

   - On **Windows**:
     - Double-click `START_EYES.bat`.

   - On **macOS / Linux**:
     - In a second terminal, run:

       ```bash
       ./start_eyes.sh
       ```

   - This will open the **Streamlit Control Room** in your browser, showing:
     - Queue metrics (pending, running, failed).
     - Counts of papers and findings.
     - Recent jobs and recent findings.

5. **Configure API keys**

   - Follow the instructions in:

     - `SECRETS_AND_KEYS.md`
     - `config/.env.example`

   - Without valid keys, the system may start, but calls to external APIs (e.g., LLMs, Semantic Scholar) will fail or run in mock mode, depending on policy settings.

---

## 5. Versioning and Governance Notes

- The **source of truth** for each release remains:
  - The **ZIP** and
  - The **concatenated TXT** with embedded `deconcat.py` and file markers.

- The antigravity installer is a **derived artifact** built from a specific concatenated TXT dump:
  - It does **not** modify runtime behavior.
  - It does **not** bypass the governance kit (ACTIVE_SURFACE, MANIFEST, etc.).
  - It simply compresses and transports that already-governed build into a single, easy-to-run installer.

- For each new GO release, the Technical Lead should:
  1. Verify the release via the usual Ruthless / governance checks.
  2. Build a fresh `install_article_eater.py` from the corresponding concatenated TXT.
  3. Clearly label that installer with the matching version in course materials (e.g., “Article Eater v20.7.41 Antigravity Installer”).

This keeps the **teaching experience** as close to “one click” as practicable, without compromising the versioning discipline and scientific governance that Article Eater depends on.
