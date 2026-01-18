#!/usr/bin/env python3
"""Article Eater v20.7.3 – CLI home page and setup guide.

This script is meant as a gentle "home page" for users who have the
repository on disk and want quick, context‑appropriate setup hints.

It does **not** modify your system or install dependencies by itself;
instead it prints curated instructions for three common starting points:

1. macOS users with a ZIP and Terminal (no git).
2. Developers using git on the command line.
3. Users working from a GitHub‑hosted repository.

Usage
-----
From the repo root:

    python scripts/ae_home.py

Then follow the on‑screen prompts.
"""

import textwrap


def section_mac() -> str:
    return textwrap.dedent("""            === macOS + ZIP + Terminal (no git) ===

        1) Open Terminal and cd into the repo directory, e.g.:

           cd /path/to/Article_Eater_v20_7_3_reconciled

        2) Create and activate a virtual environment:

           python3 -m venv .venv
           source .venv/bin/activate

        3) Install dependencies:

           pip install --upgrade pip
           pip install -r requirements.txt

        4) Run basic sanity checks:

           python scripts/sanity_check.py
           python scripts/offline_pipeline_smoke.py
           python scripts/run_all_checks.py

        5) For more detail, open:

           docs/INSTALL_mac_terminal.md
           docs/STUDENT_QUICKSTART_Article_Eater_v20_7_3b.md
           docs/STUDENT_HOWTO_RULE_GRAPH.md
        """)


def section_git() -> str:
    return textwrap.dedent("""            === git + Terminal (local developer workflow) ===

        1) Initialise or clone a git repo, then place this tree at the root.

           # new local repo
           mkdir Article_Eater
           cd Article_Eater
           git init
           # copy the reconciled tree here, then:
           git add .
           git commit -m "Add Article Eater v20.7.3-reconciled"

        2) Create and activate a virtual environment:

           python3 -m venv .venv
           source .venv/bin/activate
           pip install --upgrade pip
           pip install -r requirements.txt

        3) Run governance and tests:

           python scripts/check_governance.py
           python scripts/run_all_checks.py
           pytest

        4) For more detail, open:

           docs/INSTALL_git_cli.md
           docs/ARCHITECTURE_OVERVIEW.md
           docs/CONFIGURATION_GUIDE.md
        """)


def section_github() -> str:
    return textwrap.dedent("""            === GitHub‑hosted repository ===

        1) On GitHub: create a new repository and push this reconciled tree
           as the initial commit.

        2) Students / collaborators then:

           git clone <your-github-url> Article_Eater
           cd Article_Eater
           python3 -m venv .venv
           source .venv/bin/activate
           pip install --upgrade pip
           pip install -r requirements.txt

        3) Run the basic checks:

           python scripts/sanity_check.py
           python scripts/offline_pipeline_smoke.py
           python scripts/run_all_checks.py

        4) For more detail, open:

           docs/INSTALL_github.md
           docs/STUDENT_QUICKSTART_Article_Eater_v20_7_3b.md
           docs/STUDENT_HOWTO_RULE_GRAPH.md
        """)


def main() -> None:
    print("Article Eater v20.7.3 – Home")
    print("-------------------------------------------")
    print("Select your starting point:")
    print("  1) macOS + ZIP + Terminal (no git)")
    print("  2) git + Terminal (local developer)")
    print("  3) GitHub‑hosted repository")
    print("  q) Quit")
    choice = input("Enter choice [1/2/3/q]: ").strip().lower()
    print()

    if choice == "1":
        print(section_mac())
    elif choice == "2":
        print(section_git())
    elif choice == "3":
        print(section_github())
    else:
        print("Exiting. No changes were made.")

if __name__ == "__main__":
    main()
