#!/usr/bin/env python3
"""Minimal governance sanity checks for Article Eater.

This script is intentionally simple and must remain importable and runnable
under Python 3.11. It enforces the presence of core governance files,
checks that "kept" files are not deleted, and verifies that the subject
vocab is present and non-empty.
"""

import sys, os, subprocess, pathlib, yaml, json

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED = [
    "Project_Constitution.md",
    "release.keep.yml",
    "deprecations.yml",
    ".github/workflows/governance.yml",
    ".github/pull_request_template.md",
    "CODEOWNERS",
    "scripts/check_governance.py",
    "scripts/orphan_sweep.py",
    "scripts/public_surface_ledger.py",
    "scripts/manifest_sha256.py",
    "reconstructor_min.py",
    "deconcat.py",
    "RUTHLESS_v5.1.md",
    "public_surface_ledger.json",
]


def git_deleted_files() -> set[str]:
    """Return a set of files deleted in the last PR/commit range.

    For CI, we look at the diff between the base ref (if present) and HEAD.
    For local runs, we compare HEAD~1..HEAD.
    """
    try:
        base = os.environ.get("GITHUB_BASE_REF")
        diff_range = f"origin/{base}...HEAD" if base else "HEAD~1..HEAD"
        out = subprocess.check_output(
            ["git", "diff", "--name-status", diff_range],
            text=True,
        )
        return {
            line.split("\t", 1)[1].strip()
            for line in out.splitlines()
            if line.startswith("D\t")
        }
    except Exception:
        # If git is unavailable (e.g. in a tarball), fall back to no deletions.
        return set()


def main() -> None:
    # 1. All required governance files present
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        print("Missing governance files:", missing, file=sys.stderr)
        sys.exit(2)

    # 2. Kept files not deleted
    keep_path = ROOT / "release.keep.yml"
    kept = set()
    if keep_path.exists():
        keep_data = yaml.safe_load(keep_path.read_text(encoding="utf-8")) or {}
        kept = set(keep_data.get("kept") or [])
    deleted = git_deleted_files()
    violations = sorted(kept.intersection(deleted))
    if violations:
        print("Deletion violations for kept files:", violations, file=sys.stderr)
        sys.exit(3)


# 4. Streamlit control room and docs present
streamlit_script = ROOT / "scripts" / "ae_streamlit_control_room.py"
streamlit_doc = ROOT / "docs" / "STREAMLIT_CONTROL_ROOM.md"
missing_streamlit = []
if not streamlit_script.exists():
    missing_streamlit.append(str(streamlit_script))
if not streamlit_doc.exists():
    missing_streamlit.append(str(streamlit_doc))
if missing_streamlit:
    print("Missing Streamlit control room assets:", missing_streamlit, file=sys.stderr)
    sys.exit(7)

# 5. BN export metadata sanity check (code-level)
admin_service = ROOT / "src" / "services" / "admin_service.py"
if not admin_service.exists():
    print("admin_service.py missing; cannot verify BN export metadata.", file=sys.stderr)
    sys.exit(8)
admin_text = admin_service.read_text(encoding="utf-8")
if "BN_EXPORT_VERSION" not in admin_text or "'bn_version': BN_EXPORT_VERSION" not in admin_text:
    print("BN export version metadata not wired correctly in admin_service.py.", file=sys.stderr)
    sys.exit(9)
if "BN_EXPORT_GENERATOR" not in admin_text or "'generator': BN_EXPORT_GENERATOR" not in admin_text:
    print("BN export generator metadata not wired correctly in admin_service.py.", file=sys.stderr)
    sys.exit(10)
    # 3. Subject vocab is present and non-empty dict
    vocab_path = ROOT / "config" / "subject_vocab.json"
    if not vocab_path.exists():
        print("Missing subject vocab at", vocab_path, file=sys.stderr)
        sys.exit(4)
    try:
        data = json.loads(vocab_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        print("Failed to parse subject vocab:", exc, file=sys.stderr)
        sys.exit(5)
    if not isinstance(data, dict) or not data:
        print("Subject vocab is empty or not a dict.", file=sys.stderr)
        sys.exit(6)

    print("Governance check passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
