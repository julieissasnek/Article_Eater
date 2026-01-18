#!/usr/bin/env python3
"""Build a single-file 'Antigravity Installer' for Article Eater.

This is an internal packaging helper. It takes a concatenated TXT dump
for a given release and emits a self-contained installer script that:

- Reconstructs the repo into ~/ArticleEater_v20
- Creates a virtualenv
- Installs requirements.txt
- Writes simple launchers for the worker and the Streamlit Control Room
"""

import base64
import gzip
from pathlib import Path

INPUT_DUMP = "Article_Eater_v20_7_43_usability_antigravity_full_concatenated.txt"
OUTPUT_INSTALLER = "install_article_eater.py"
APP_NAME = "ArticleEater_v20"

INSTALLER_TEMPLATE = '''#!/usr/bin/env python3
# Article Eater v20 - Antigravity Installer
# ZERO FRICTION. ZERO CONFUSION.
import sys
import os
import base64
import gzip
import subprocess
import shutil
import platform
from pathlib import Path

PAYLOAD_B64 = "{PAYLOAD}"
APP_DIR_NAME = "{APP_DIR_NAME}"

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
X = '\033[0m'

def log(msg, color=G):
    print(f"{color}[installer] {msg}{X}")

def fail(msg):
    print(f"\n{R}ERROR: {msg}{X}")
    input("Press Enter to exit...")
    sys.exit(1)

def check_python():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        fail(f"Python 3.10+ required. You have {v.major}.{v.minor}")
    log(f"Python {v.major}.{v.minor} detected. Good.")

def extract_payload(dest_dir):
    log("Extracting payload...")
    try:
        compressed = base64.b64decode(PAYLOAD_B64)
        raw_text = gzip.decompress(compressed).decode("utf-8")

        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        marker_path = "----- FILE PATH:"
        marker_start = "----- CONTENT START -----"
        marker_end = "----- CONTENT END -----"

        current_file = None
        buffer = []
        collecting = False

        for line in raw_text.splitlines(keepends=True):
            clean = line.strip()
            if clean.startswith(marker_path):
                if current_file and buffer:
                    p = dest_path / current_file
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("".join(buffer), encoding="utf-8")
                current_file = clean.split(":", 1)[1].strip()
                buffer = []
                collecting = False
            elif clean == marker_start:
                collecting = True
            elif clean == marker_end:
                collecting = False
            elif collecting:
                buffer.append(line)

        if current_file and buffer:
            p = dest_path / current_file
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("".join(buffer), encoding="utf-8")

        log("Extraction complete.")
    except Exception as e:
        fail(f"Extraction failed: {e}")

def setup_venv(dest_dir):
    venv_path = Path(dest_dir) / "venv"
    if venv_path.exists():
        log("Virtual environment exists. Skipping creation.")
    else:
        log("Creating virtual environment (this may take a moment)...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        except subprocess.CalledProcessError:
            fail("Could not create venv.")
    return venv_path

def install_deps(dest_dir, venv_path):
    log("Installing dependencies from requirements.txt...")

    if platform.system() == "Windows":
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"

    req_file = Path(dest_dir) / "requirements.txt"
    if not req_file.exists():
        fail("requirements.txt not found in payload.")

    try:
        subprocess.check_call(
            [str(pip_exe), "install", "-r", str(req_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        log("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        fail("Pip install failed. Check internet connection and try again.")

def create_launchers(dest_dir, venv_path):
    log("Creating easy launcher scripts...")
    dest = Path(dest_dir)

    if platform.system() == "Windows":
        py_exe = venv_path / "Scripts" / "python.exe"
        streamlit_exe = venv_path / "Scripts" / "streamlit.exe"

        with open(dest / "START_BRAIN.bat", "w", encoding="utf-8") as f:
            f.write(f'@echo off\n"{py_exe}" -m app.worker\npause')

        with open(dest / "START_EYES.bat", "w", encoding="utf-8") as f:
            f.write(
                f'@echo off\n"{streamlit_exe}" run scripts/ae_streamlit_control_room.py\npause'
            )
    else:
        py_exe = venv_path / "bin" / "python"
        streamlit_exe = venv_path / "bin" / "streamlit"

        p1 = dest / "start_brain.sh"
        p1.write_text(f'#!/bin/bash\n"{py_exe}" -m app.worker', encoding="utf-8")
        p1.chmod(0o755)

        p2 = dest / "start_eyes.sh"
        p2.write_text(
            f'#!/bin/bash\n"{streamlit_exe}" run scripts/ae_streamlit_control_room.py',
            encoding="utf-8",
        )
        p2.chmod(0o755)

def main():
    print(f"\n{Y}🦁 Article Eater v20 - Antigravity Installer{X}")
    print(f"{Y}=========================================={X}\n")

    check_python()

    home = Path.home()
    install_dir = home / APP_DIR_NAME

    if install_dir.exists():
        log(f"Found existing installation at {install_dir}")
        ans = input(f"{Y}Overwrite? [y/N]: {X}")
        if ans.lower() != "y":
            log("Aborting.")
            sys.exit(0)
        shutil.rmtree(install_dir)

    log(f"Installing to: {install_dir}")

    extract_payload(install_dir)
    venv = setup_venv(install_dir)
    install_deps(install_dir, venv)
    create_launchers(install_dir, venv)

    print(f"\n{G}SUCCESS! Installation complete.{X}")
    print(f"Go to: {install_dir}")
    print("1. Run 'START_BRAIN' / 'start_brain.sh' to run the worker.")
    print("2. Run 'START_EYES' / 'start_eyes.sh' to open the dashboard (Streamlit).")
    print("\nRemember to configure your API keys as described in SECRETS_AND_KEYS.md")

    input("\nPress Enter to exit installer...")

if __name__ == "__main__":
    main()
'''

def build():
    print("--- ANTIGRAVITY INSTALLER FACTORY ---")
    dump_path = Path(INPUT_DUMP)
    if not dump_path.exists():
        print(f"Error: Input file '{dump_path}' not found.")
        print("Make sure you have the concatenated dump in this directory.")
        return

    print(f"Reading {dump_path}...")
    raw_data = dump_path.read_bytes()

    print("Compressing payload (gzip)...")
    compressed = gzip.compress(raw_data)

    print("Encoding payload (base64)...")
    b64_data = base64.b64encode(compressed).decode("utf-8")

    print("Injecting into installer template...")
    script_text = INSTALLER_TEMPLATE.format(PAYLOAD=b64_data, APP_DIR_NAME=APP_NAME)

    out_path = Path(OUTPUT_INSTALLER)
    out_path.write_text(script_text, encoding="utf-8")

    print(f"Done. Wrote {out_path}")
    print(f"Original size: {len(raw_data)/1024/1024:.2f} MB")
    print(f"Installer size: {len(script_text)/1024/1024:.2f} MB")

if __name__ == "__main__":
    build()
