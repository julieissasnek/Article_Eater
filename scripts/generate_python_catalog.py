#!/usr/bin/env python3
"""
generate_python_catalog.py
--------------------------
Scans the repo for all .py files and writes an up-to-date catalog to
docs/python_source_catalog.md.

Usage:
    python scripts/generate_python_catalog.py          # writes docs/python_source_catalog.md
    python scripts/generate_python_catalog.py --check  # exits 1 if catalog is stale (CI-friendly)
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "docs" / "python_source_catalog.md"

# Directories to skip entirely (relative to repo root, no leading ./)
SKIP_DIRS = {
    ".venv", ".venv_pptx", ".venv_pptx2", ".panel_venv", "venv",
    "node_modules", "__pycache__", ".pptx_lib", ".git",
    ".ruff_cache", ".pytest_cache",
}

# Canonical directory buckets – order matters for display
CANONICAL_BUCKETS: list[tuple[str, str]] = [
    ("src/services/ecb_modules",    "ECB Sub-modules"),
    ("src/services/paper_integration", "Paper Integration"),
    ("src/services/web_of_belief_components", "WoB Components"),
    ("src/services/web_of_belief_modules",    "WoB Modules"),
    ("src/services",                "Core Services"),
    ("src/extraction",              "Extraction Pipeline"),
    ("src/theory",                  "Theory Tier"),
    ("src/models",                  "Data Models"),
    ("src/agents",                  "Agents"),
    ("src",                         "Other src/"),
    ("scripts",                     "Scripts"),
    ("tests",                       "Tests"),
    ("app/routes",                  "API Routes"),
    ("app",                         "App Core"),
    ("streamlit_app",               "Streamlit Dashboard"),
    ("apps",                        "Mini-apps"),
    ("db",                          "Database"),
    ("modules",                     "Modules"),
    ("bin",                         "CLI Entry-points"),
    ("lib",                         "Library Helpers"),
    ("governance_kit",              "Governance Kit"),
    ("migration_artifacts",         "Migration Artifacts"),
    ("qa_browse",                   "QA Browser"),
    ("gold_standard",               "Gold Standard"),
    ("examples",                    "Examples"),
]

# These directories contain frozen snapshots / archives, not live code
NON_CANONICAL_DIRS = [
    "ruthless_bundle_2026-02-08",
    "_review_package_2026_01_23",
    "Post_Quinean Setup",
    "quarantine",
    "archive",
    "_archive",
    "claude_code_v2_final",
    "_v18_package",
    "docs",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def should_skip(dirpath: str) -> bool:
    """Return True if this directory should be entirely skipped."""
    parts = Path(dirpath).parts
    return any(p in SKIP_DIRS for p in parts)


def collect_py_files() -> list[Path]:
    """Walk the repo and return all .py files (excluding skip dirs)."""
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = Path(dirpath).relative_to(REPO_ROOT)
        # Prune skip dirs in-place so os.walk doesn't descend
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
            or d in (".github",)  # keep .github if needed
        ]
        # But still skip hidden dirs we don't want
        if should_skip(str(rel_dir)):
            continue
        for fname in sorted(filenames):
            if fname.endswith(".py") and not fname.endswith(".pyc"):
                results.append(rel_dir / fname)
    return results


def bucket_files(files: list[Path]) -> tuple[
    dict[str, list[Path]], list[Path], list[Path]
]:
    """
    Sort files into canonical buckets, non-canonical, and root-level.
    Returns (canonical_dict, non_canonical_list, root_list).
    """
    canonical: dict[str, list[Path]] = defaultdict(list)
    non_canonical: list[Path] = []
    root_level: list[Path] = []

    for fpath in files:
        rel = str(fpath)
        # Check non-canonical first
        if any(rel.startswith(nd + "/") or rel.startswith(nd + os.sep) for nd in NON_CANONICAL_DIRS):
            non_canonical.append(fpath)
            continue
        # Check canonical buckets (first match wins – order matters)
        matched = False
        for prefix, label in CANONICAL_BUCKETS:
            if rel.startswith(prefix + "/") or rel.startswith(prefix + os.sep):
                canonical[label].append(fpath)
                matched = True
                break
        if not matched:
            if "/" not in rel and os.sep not in rel:
                root_level.append(fpath)
            else:
                # Anything else goes under its top-level dir name
                top = str(fpath).split("/")[0].split(os.sep)[0]
                canonical[f"Other ({top}/)"].append(fpath)

    return canonical, non_canonical, root_level


def render_table(files: list[Path]) -> str:
    """Render a markdown table of files."""
    lines = ["| File | Path |", "|------|------|"]
    for f in sorted(files):
        lines.append(f"| `{f.name}` | `{f}` |")
    return "\n".join(lines)


def render_catalog(
    canonical: dict[str, list[Path]],
    non_canonical: list[Path],
    root_level: list[Path],
) -> str:
    """Render the full markdown catalog."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts: list[str] = []

    parts.append("# Python Source File Catalog")
    parts.append("")
    parts.append(f"> Auto-generated by `scripts/generate_python_catalog.py` on **{now}**.")
    parts.append("> Re-run that script to refresh this file.")
    parts.append("")

    # Summary table
    total = sum(len(v) for v in canonical.values()) + len(root_level)
    parts.append(f"**{total}** canonical Python files across the repo "
                 f"(plus **{len(non_canonical)}** non-canonical copies in archives/snapshots).")
    parts.append("")

    # Canonical sections
    parts.append("---")
    parts.append("")
    for _prefix, label in CANONICAL_BUCKETS:
        bucket_files_list = canonical.get(label)
        if not bucket_files_list:
            continue
        parts.append(f"## {label}  ({len(bucket_files_list)} files)")
        parts.append("")
        parts.append(render_table(bucket_files_list))
        parts.append("")

    # Catch-all canonical buckets (Other (...))
    for label in sorted(canonical):
        if label.startswith("Other ("):
            bucket_files_list = canonical[label]
            parts.append(f"## {label}  ({len(bucket_files_list)} files)")
            parts.append("")
            parts.append(render_table(bucket_files_list))
            parts.append("")

    # Root-level
    if root_level:
        parts.append("---")
        parts.append("")
        parts.append(f"## Root-Level Scripts  ({len(root_level)} files)")
        parts.append("")
        parts.append("> [!TIP]")
        parts.append("> Consider moving these into `scripts/` or `tests/` for cleaner organization.")
        parts.append("")
        parts.append(render_table(root_level))
        parts.append("")

    # Non-canonical
    if non_canonical:
        parts.append("---")
        parts.append("")
        parts.append(f"## Non-Canonical Copies  ({len(non_canonical)} files)")
        parts.append("")
        parts.append("> [!WARNING]")
        parts.append("> These are **frozen snapshots** in archive/review/quarantine directories.")
        parts.append("> They are NOT the live code. Do not edit them.")
        parts.append("")
        # Group by top-level dir
        by_dir: dict[str, list[Path]] = defaultdict(list)
        for f in non_canonical:
            top = str(f).split("/")[0]
            by_dir[top].append(f)
        for dirname in sorted(by_dir):
            parts.append(f"### `{dirname}/`  ({len(by_dir[dirname])} files)")
            parts.append("")
            parts.append(render_table(by_dir[dirname]))
            parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="Check if the catalog is up-to-date; exit 1 if stale."
    )
    args = parser.parse_args()

    files = collect_py_files()
    canonical, non_canonical, root_level = bucket_files(files)
    new_content = render_catalog(canonical, non_canonical, root_level)

    if args.check:
        if OUTPUT_PATH.exists():
            existing = OUTPUT_PATH.read_text()
            # Compare ignoring the timestamp line
            def strip_timestamp(s: str) -> str:
                return "\n".join(
                    line for line in s.splitlines()
                    if not line.startswith("> Auto-generated by")
                )
            if strip_timestamp(existing) == strip_timestamp(new_content):
                print(f"✅  {OUTPUT_PATH.relative_to(REPO_ROOT)} is up-to-date.")
                return 0
            else:
                print(
                    f"❌  {OUTPUT_PATH.relative_to(REPO_ROOT)} is STALE. "
                    f"Run: python scripts/generate_python_catalog.py"
                )
                return 1
        else:
            print(f"❌  {OUTPUT_PATH.relative_to(REPO_ROOT)} does not exist.")
            return 1

    # Write the catalog
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(new_content)
    print(f"✅  Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}  "
          f"({sum(len(v) for v in canonical.values()) + len(root_level)} canonical, "
          f"{len(non_canonical)} non-canonical)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
