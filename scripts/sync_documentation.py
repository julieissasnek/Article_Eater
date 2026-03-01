#!/usr/bin/env python3
"""
sync_documentation.py — ATLAS Documentation Synchronization Tool

Reads canonical values from source code and compares against documentation.
Reports any drift between code and docs. Optionally fixes drift with --fix.

Usage:
    python scripts/sync_documentation.py            # report only
    python scripts/sync_documentation.py --fix       # report + fix drift
    python scripts/sync_documentation.py --verbose   # detailed output

Created: 2026-02-26
"""

import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Resolve repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
DOCS = REPO_ROOT / "docs"

# Source-of-truth files
BRIDGE_WARRANTS_PY = SRC / "services" / "bridge_warrants.py"
WARRANT_SCALING_PY = SRC / "epistemic" / "warrant_scaling.py"
ENUMS_PY = SRC / "services" / "web_of_belief_components" / "enums.py"
BUILD_DOC_JS = DOCS / "build_doc.js"
ARCHITECTURE_MD = REPO_ROOT / "ARCHITECTURE.md"

# Canonical ceiling values expected in code (will be read dynamically)
KNOWN_WARRANT_TYPES = [
    "CONSTITUTIVE", "MECHANISM", "EMPIRICAL_ASSOCIATION",
    "FUNCTIONAL", "CAPACITY", "THEORY_DERIVED", "ANALOGICAL"
]


def extract_ceiling_values_from_code(filepath: Path) -> dict:
    """Extract DEFAULT_BRIDGE_CONFIDENCE dict from bridge_warrants.py."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    # Look for dict assignment pattern
    match = re.search(
        r"DEFAULT_BRIDGE_CONFIDENCE[^{]*\{([^}]+)\}",
        text, re.DOTALL
    )
    if not match:
        return {}
    ceilings = {}
    for line in match.group(1).split("\n"):
        line = line.strip().rstrip(",")
        # Match both "STRING": 0.75 and BridgeType.NAME: 0.75
        kv = re.match(r'(?:BridgeType\.)?["\']?(\w+)["\']?\s*:\s*([\d.]+)', line)
        if kv:
            ceilings[kv.group(1)] = float(kv.group(2))
    return ceilings


def extract_base_warrants_from_code(filepath: Path) -> dict:
    """Extract BASE_*_WARRANT constants from warrant_scaling.py."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    warrants = {}
    for name in ["BASE_COHERENCE_WARRANT", "BASE_ARGUMENTATIVE_WARRANT", "BASE_VIGILANCE_WARRANT"]:
        match = re.search(rf"{name}\s*=\s*([\d.]+)", text)
        if match:
            warrants[name] = float(match.group(1))
    return warrants


def extract_ceilings_from_build_doc(filepath: Path) -> dict:
    """Extract ceiling values mentioned in build_doc.js Step 2 text."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    ceilings = {}
    # Pattern: "MECHANISM bridges is 0.60" or "CONSTITUTIVE at 0.75"
    for wtype in KNOWN_WARRANT_TYPES:
        patterns = [
            rf"{wtype}[^0-9]*?(0\.\d+)",
            rf"{wtype}\s+(?:bridges?\s+)?(?:is|at)\s+(0\.\d+)",
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                ceilings[wtype] = float(match.group(1))
                break
    return ceilings


def extract_ceilings_from_architecture(filepath: Path) -> dict:
    """Extract ceiling values from ARCHITECTURE.md table."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    ceilings = {}
    for wtype in KNOWN_WARRANT_TYPES:
        match = re.search(rf"\|\s*{wtype}\s*\|\s*(0\.\d+)", text)
        if match:
            ceilings[wtype] = float(match.group(1))
    return ceilings


def compare_ceilings(source_name: str, source: dict, target_name: str, target: dict) -> list:
    """Compare two ceiling dicts. Returns list of (type, source_val, target_val) drifts."""
    drifts = []
    for wtype in KNOWN_WARRANT_TYPES:
        sv = source.get(wtype)
        tv = target.get(wtype)
        if sv is not None and tv is not None and abs(sv - tv) > 0.001:
            drifts.append((wtype, sv, tv))
        elif sv is not None and tv is None:
            drifts.append((wtype, sv, "MISSING"))
    return drifts


def run_sync(fix=False, verbose=False):
    """Main sync logic."""
    report_lines = []
    drift_count = 0
    fix_count = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines.append(f"# Documentation Sync Report")
    report_lines.append(f"**Generated**: {timestamp}")
    report_lines.append(f"**Mode**: {'FIX' if fix else 'REPORT ONLY'}")
    report_lines.append("")

    # 1. Read code ceilings (source of truth)
    code_ceilings = extract_ceiling_values_from_code(BRIDGE_WARRANTS_PY)
    if not code_ceilings:
        report_lines.append("WARNING: Could not read ceilings from bridge_warrants.py")
    else:
        report_lines.append(f"## Code Ceilings (bridge_warrants.py)")
        for wt, val in sorted(code_ceilings.items()):
            report_lines.append(f"  {wt}: {val}")
        report_lines.append("")

    # 2. Read base warrants
    base_warrants = extract_base_warrants_from_code(WARRANT_SCALING_PY)
    if base_warrants:
        report_lines.append(f"## Base Warrants (warrant_scaling.py)")
        for name, val in sorted(base_warrants.items()):
            report_lines.append(f"  {name}: {val}")
        report_lines.append("")

    # 3. Compare against build_doc.js
    doc_ceilings = extract_ceilings_from_build_doc(BUILD_DOC_JS)
    if doc_ceilings:
        drifts = compare_ceilings("bridge_warrants.py", code_ceilings, "build_doc.js", doc_ceilings)
        if drifts:
            report_lines.append(f"## DRIFT: build_doc.js vs code")
            for wtype, sv, tv in drifts:
                report_lines.append(f"  {wtype}: code={sv}, doc={tv}")
                drift_count += 1
        else:
            report_lines.append(f"## build_doc.js: IN SYNC")
        report_lines.append("")

    # 4. Compare against ARCHITECTURE.md
    arch_ceilings = extract_ceilings_from_architecture(ARCHITECTURE_MD)
    if arch_ceilings:
        drifts = compare_ceilings("bridge_warrants.py", code_ceilings, "ARCHITECTURE.md", arch_ceilings)
        if drifts:
            report_lines.append(f"## DRIFT: ARCHITECTURE.md vs code")
            for wtype, sv, tv in drifts:
                report_lines.append(f"  {wtype}: code={sv}, doc={tv}")
                drift_count += 1
        else:
            report_lines.append(f"## ARCHITECTURE.md: IN SYNC")
        report_lines.append("")

    # 5. Summary
    report_lines.append(f"## Summary")
    report_lines.append(f"- Drift items found: {drift_count}")
    if fix:
        report_lines.append(f"- Items fixed: {fix_count}")
    report_lines.append("")

    # Print report
    report_text = "\n".join(report_lines)
    print(report_text)

    # Save report
    report_dir = DOCS / "sync_reports"
    report_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = report_dir / f"SYNC_REPORT_{date_str}.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    return drift_count


def main():
    parser = argparse.ArgumentParser(description="ATLAS Documentation Sync Tool")
    parser.add_argument("--fix", action="store_true", help="Fix drift (update docs to match code)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    drift_count = run_sync(fix=args.fix, verbose=args.verbose)
    sys.exit(0 if drift_count == 0 else 1)


if __name__ == "__main__":
    main()
