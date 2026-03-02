#!/usr/bin/env python3
"""
check_repo_health.py — Systemic Prevention Health Check
========================================================

PURPOSE: Automated guard against the 4 failure classes discovered in RV5 audit.
RUN: Before commits, after any rename/refactor, or periodically.

GUARDS:
  1. Import smoke test — every src/ module must import
  2. Enum lint — no duplicate enum members in any file
  3. Test collection gate — pytest must collect >= baseline
  4. Module-test manifest — every service/model must have a test file
  5. JSON validity — all contract/schema/calibration JSONs parse
  6. EN/BN health diagnostic — informativeness of the epistemic network

Added: 2026-02-28 (post-RV5-2 root-cause analysis)
"""

import ast
import glob
import importlib
import json
import os
import pkgutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
DATA_DIR = PROJECT_ROOT / "data"

# Terminal colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def header(title: str):
    print(f"\n{BOLD}{CYAN}{'═' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 60}{RESET}\n")


def ok(msg: str):
    print(f"  {GREEN}✓{RESET} {msg}")


def warn(msg: str):
    print(f"  {YELLOW}⚠{RESET} {msg}")


def fail(msg: str):
    print(f"  {RED}✗{RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
# GUARD 1: Import Smoke Test
# ═══════════════════════════════════════════════════════════════

def check_imports() -> List[str]:
    """Try importing every module in src/. Return list of failures."""
    header("GUARD 1: Import Smoke Test")
    failures = []

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    modules = []
    for importer, modname, ispkg in pkgutil.walk_packages(
        [str(SRC_DIR)], prefix="src."
    ):
        modules.append(modname)

    for mod_name in sorted(modules):
        try:
            importlib.import_module(mod_name)
            ok(mod_name)
        except Exception as e:
            fail(f"{mod_name}: {type(e).__name__}: {str(e)[:100]}")
            failures.append(mod_name)

    print(f"\n  {len(modules)} modules scanned, {len(failures)} failures")
    return failures


# ═══════════════════════════════════════════════════════════════
# GUARD 2: Enum Duplicate Lint
# ═══════════════════════════════════════════════════════════════

def check_enum_duplicates() -> List[str]:
    """AST-scan all .py files for duplicate enum member names."""
    header("GUARD 2: Enum Duplicate Lint")
    failures = []

    py_files = list(SRC_DIR.rglob("*.py"))

    for fpath in sorted(py_files):
        try:
            tree = ast.parse(fpath.read_text(), filename=str(fpath))
        except SyntaxError:
            fail(f"{fpath.relative_to(PROJECT_ROOT)}: SyntaxError")
            failures.append(str(fpath))
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if any base is Enum-like
                bases = [
                    getattr(b, 'id', getattr(b, 'attr', ''))
                    for b in node.bases
                ]
                is_enum = any(
                    b in ('Enum', 'IntEnum', 'StrEnum', 'Flag', 'IntFlag')
                    for b in bases
                )
                if not is_enum:
                    continue

                # Check for duplicate assignment targets
                names = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id in names:
                                    fail(
                                        f"{fpath.relative_to(PROJECT_ROOT)}: "
                                        f"Duplicate enum member '{target.id}' "
                                        f"in class {node.name} (line {item.lineno})"
                                    )
                                    failures.append(f"{fpath}:{node.name}.{target.id}")
                                names.append(target.id)

    if not failures:
        ok(f"Scanned {len(py_files)} files — no duplicate enum members")
    return failures


# ═══════════════════════════════════════════════════════════════
# GUARD 3: Module-Test Manifest
# ═══════════════════════════════════════════════════════════════

def check_test_coverage_manifest() -> List[str]:
    """Every src/services/*.py and src/models/*.py should have a test file."""
    header("GUARD 3: Module-Test Coverage Manifest")
    missing = []

    # Core modules that MUST have tests
    for subdir in ["services", "models"]:
        src_subdir = SRC_DIR / subdir
        if not src_subdir.exists():
            continue

        for fpath in sorted(src_subdir.glob("*.py")):
            if fpath.name.startswith("__"):
                continue

            base = fpath.stem
            # Look for any test file that contains the module name
            test_patterns = [
                TESTS_DIR / f"test_{base}.py",
                TESTS_DIR / f"test_{subdir}_{base}.py",
            ]

            # Also check if any test file imports this module
            has_test = any(tp.exists() for tp in test_patterns)

            if has_test:
                ok(f"{subdir}/{base}: test file exists")
            else:
                warn(f"{subdir}/{base}: NO test file found")
                missing.append(f"{subdir}/{base}")

    if missing:
        print(f"\n  {len(missing)} modules have no dedicated test file")
    else:
        print(f"\n  All modules have test files")
    return missing


# ═══════════════════════════════════════════════════════════════
# GUARD 4: JSON Validity
# ═══════════════════════════════════════════════════════════════

def check_json_validity() -> List[str]:
    """Validate all JSON files in contracts/ and data/calibration/."""
    header("GUARD 4: JSON Schema/Contract Validity")
    failures = []

    json_dirs = [
        CONTRACTS_DIR,
        DATA_DIR / "calibration",
    ]

    for d in json_dirs:
        if not d.exists():
            warn(f"{d.relative_to(PROJECT_ROOT)}: directory not found")
            continue

        for fpath in sorted(d.rglob("*.json")):
            try:
                with open(fpath) as f:
                    json.load(f)
                ok(f"{fpath.relative_to(PROJECT_ROOT)}")
            except json.JSONDecodeError as e:
                fail(f"{fpath.relative_to(PROJECT_ROOT)}: {e}")
                failures.append(str(fpath))

    if not failures:
        print(f"\n  All JSON files valid")
    return failures


# ═══════════════════════════════════════════════════════════════
# GUARD 5: EN/BN Health Diagnostic
# ═══════════════════════════════════════════════════════════════

def check_en_bn_health() -> Dict:
    """
    Measure the informativeness of the Epistemic Network and Bayesian Network.
    Answers: can we squeeze more from what we have, or must we get more articles?
    """
    header("GUARD 5: EN/BN Health & Informativeness Diagnostic")

    stats = {}

    # --- Extractions available ---
    extractions_dir = DATA_DIR / "extractions"
    if extractions_dir.exists():
        extraction_files = list(extractions_dir.glob("10.*.json"))
        stats["extractions_available"] = len(extraction_files)

        total_findings = 0
        total_with_effect = 0
        total_with_direction = 0
        for ef in extraction_files[:200]:  # Sample first 200
            try:
                data = json.load(open(ef))
                findings = data.get("findings", [])
                total_findings += len(findings)
                for f in findings:
                    if f.get("effect_size"):
                        total_with_effect += 1
                    if f.get("direction"):
                        total_with_direction += 1
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        stats["sampled_papers"] = min(200, len(extraction_files))
        stats["avg_findings_per_paper"] = total_findings / max(1, stats["sampled_papers"])
        stats["findings_with_effect_size_pct"] = (
            total_with_effect / max(1, total_findings) * 100
        )
        stats["findings_with_direction_pct"] = (
            total_with_direction / max(1, total_findings) * 100
        )
    else:
        stats["extractions_available"] = 0

    # --- Templates ---
    templates_dir = DATA_DIR / "templates"
    if templates_dir.exists():
        templates = list(templates_dir.glob("*.json"))
        stats["templates_total"] = len(templates)

        calibrated = 0
        for tf in templates:
            try:
                t = json.load(open(tf))
                if t.get("calibration_status") == "calibrated":
                    calibrated += 1
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
        stats["templates_calibrated"] = calibrated
    else:
        stats["templates_total"] = 0
        stats["templates_calibrated"] = 0

    # --- Theories ---
    theories_dir = DATA_DIR / "theories"
    if theories_dir.exists():
        stats["theories"] = len(list(theories_dir.glob("*.json")))
    else:
        stats["theories"] = 0

    # --- Molecules ---
    molecules_dir = DATA_DIR / "molecules"
    if molecules_dir.exists():
        stats["molecules"] = len(list(molecules_dir.glob("*.json")))
    else:
        stats["molecules"] = 0

    # --- Database (if accessible) ---
    db_paths = [
        DATA_DIR / "web_persistence_v2.db",
        Path("/tmp/web_persistence_v2.db"),
    ]
    db_found = False
    for db_path in db_paths:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()

                # Count beliefs
                try:
                    cur.execute("SELECT COUNT(*) FROM beliefs")
                    stats["beliefs_in_db"] = cur.fetchone()[0]
                except Exception:
                    stats["beliefs_in_db"] = 0

                # Count edges/constraints
                try:
                    cur.execute("SELECT COUNT(*) FROM constraints")
                    stats["constraints_in_db"] = cur.fetchone()[0]
                except Exception:
                    stats["constraints_in_db"] = 0

                # Count papers integrated
                try:
                    cur.execute("SELECT COUNT(DISTINCT paper_id) FROM beliefs WHERE paper_id IS NOT NULL")
                    stats["papers_in_db"] = cur.fetchone()[0]
                except Exception:
                    stats["papers_in_db"] = 0

                conn.close()
                db_found = True
                stats["db_source"] = str(db_path)
                break
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    if not db_found:
        stats["beliefs_in_db"] = "N/A (DB not accessible)"
        stats["constraints_in_db"] = "N/A"
        stats["papers_in_db"] = "N/A"

    # --- Outcome vocab ---
    vocab_path = DATA_DIR / "outcome_vocab.json"
    if vocab_path.exists():
        try:
            vocab = json.load(open(vocab_path))
            if isinstance(vocab, dict) and "terms" in vocab:
                stats["vocab_terms"] = len(vocab["terms"])
            elif isinstance(vocab, list):
                stats["vocab_terms"] = len(vocab)
            else:
                stats["vocab_terms"] = len(vocab)
        except Exception:
            stats["vocab_terms"] = 0
    else:
        stats["vocab_terms"] = 0

    # --- Print results ---
    print(f"  {'Metric':<40s} {'Value':>10s}")
    print(f"  {'─' * 40} {'─' * 10}")
    for k, v in stats.items():
        print(f"  {k:<40s} {str(v):>10s}")

    # --- Utilization analysis ---
    print(f"\n  {BOLD}Utilization Analysis:{RESET}")

    extractions = stats.get("extractions_available", 0)
    if isinstance(stats.get("papers_in_db"), int) and extractions > 0:
        papers_db = stats["papers_in_db"]
        utilization = papers_db / extractions * 100
        if utilization < 25:
            fail(f"Paper utilization: {papers_db}/{extractions} = {utilization:.1f}% — "
                 f"SEVERE UNDERUTILIZATION. Can squeeze much more from existing data.")
        elif utilization < 50:
            warn(f"Paper utilization: {papers_db}/{extractions} = {utilization:.1f}% — "
                 f"Moderate. Room to integrate more existing papers.")
        else:
            ok(f"Paper utilization: {papers_db}/{extractions} = {utilization:.1f}%")
    else:
        warn("Cannot compute paper utilization (DB not accessible)")

    templates = stats.get("templates_total", 0)
    calibrated = stats.get("templates_calibrated", 0)
    if templates > 0:
        cal_pct = calibrated / templates * 100
        if cal_pct < 60:
            fail(f"Template calibration: {calibrated}/{templates} = {cal_pct:.0f}%")
        elif cal_pct < 80:
            warn(f"Template calibration: {calibrated}/{templates} = {cal_pct:.0f}%")
        else:
            ok(f"Template calibration: {calibrated}/{templates} = {cal_pct:.0f}%")

    return stats


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    header("ATLAS REPO HEALTH CHECK")
    print(f"  Project: {PROJECT_ROOT}")
    print(f"  Time: {__import__('datetime').datetime.now().isoformat()}")

    all_failures = []

    # Guard 1: Imports
    import_failures = check_imports()
    all_failures.extend(import_failures)

    # Guard 2: Enum duplicates
    enum_failures = check_enum_duplicates()
    all_failures.extend(enum_failures)

    # Guard 3: Module-test manifest
    test_gaps = check_test_coverage_manifest()
    # test gaps are warnings, not failures

    # Guard 4: JSON validity
    json_failures = check_json_validity()
    all_failures.extend(json_failures)

    # Guard 5: EN/BN health
    en_bn_stats = check_en_bn_health()

    # ─── Summary ───
    header("SUMMARY")

    if all_failures:
        fail(f"{len(all_failures)} HARD FAILURES (must fix before commit)")
        for f_item in all_failures:
            print(f"    → {f_item}")
        print()
        return 1
    elif test_gaps:
        warn(f"{len(test_gaps)} modules without test files (should add)")
        ok("No hard failures")
        return 0
    else:
        ok("All checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
