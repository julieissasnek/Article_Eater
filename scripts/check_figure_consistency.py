#!/usr/bin/env python3
"""
ATLAS Figure-Document Consistency Checker

Validates that all figures declared in FIGURE_DEPENDENCIES.json match current source text.
Reads dependency patterns from the contract and greps source Part files to verify consistency.

Usage:
    python check_figure_consistency.py --quick              # Fast: critical deps only
    python check_figure_consistency.py --full               # All deps, all figures
    python check_figure_consistency.py --figure m1          # Just M-1
    python check_figure_consistency.py --full --add-tasks   # Full + append stale items to TASKS.md
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from dataclasses import dataclass


# WCAG accessible colors (no dark blue on dark background)
class Colors:
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass
class DependencyStatus:
    figure_id: str
    figure_title: str
    dependency_type: str
    claim: str
    pattern: str
    severity: str
    found: bool
    matched_text: Optional[str] = None
    source_file: Optional[str] = None


def load_dependencies_contract(contract_path: Path) -> Dict:
    """Load FIGURE_DEPENDENCIES.json contract."""
    with open(contract_path, "r") as f:
        return json.load(f)


def search_files(pattern: str, file_paths: List[Path], case_insensitive: bool = True) -> Tuple[bool, Optional[str], Optional[Path]]:
    """
    Search for regex pattern across files.
    Returns (found: bool, matched_text: str, source_file: Path)
    """
    flags = re.IGNORECASE if case_insensitive else 0

    for file_path in file_paths:
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            match = re.search(pattern, content, flags)
            if match:
                # Extract surrounding context (50 chars before/after)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                return True, context, file_path

        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not read {file_path}: {e}{Colors.RESET}", file=sys.stderr)
            continue

    return False, None, None


def check_figure(
    figure_id: str,
    figure_data: Dict,
    parts_base_dir: Path,
    critical_only: bool = False
) -> List[DependencyStatus]:
    """Check all dependencies for a single figure."""
    results = []

    # Build list of source files to search
    source_files = []
    for part_name in figure_data.get("source_parts", []):
        part_path = parts_base_dir / part_name
        source_files.append(part_path)

    # Check each dependency
    for dep in figure_data.get("dependencies", []):
        # Skip non-critical if critical_only
        if critical_only and dep.get("severity") != "CRITICAL":
            continue

        pattern = dep.get("grep_pattern", "")
        found, matched_text, source_file = search_files(pattern, source_files)

        status = DependencyStatus(
            figure_id=figure_id,
            figure_title=figure_data.get("title", ""),
            dependency_type=dep.get("type", ""),
            claim=dep.get("claim", ""),
            pattern=pattern,
            severity=dep.get("severity", "MINOR"),
            found=found,
            matched_text=matched_text,
            source_file=source_file.name if source_file else None
        )
        results.append(status)

    return results


def determine_status(results: List[DependencyStatus]) -> Tuple[str, int]:
    """
    Determine overall status from results.
    Returns (status_label, exit_code)
    - CURRENT: all found (exit 0)
    - STALE-MINOR: found but some MINOR deps missing (exit 1)
    - STALE-CRITICAL: any CRITICAL dep missing (exit 2)
    """
    missing_critical = any(not r.found and r.severity == "CRITICAL" for r in results)
    missing_minor = any(not r.found and r.severity == "MINOR" for r in results)

    if missing_critical:
        return "STALE-CRITICAL", 2
    elif missing_minor:
        return "STALE-MINOR", 1
    else:
        return "CURRENT", 0


def print_results(
    results: List[DependencyStatus],
    verbose: bool = False
) -> None:
    """Print formatted results table."""
    print(f"\n{Colors.BOLD}{Colors.WHITE}FIGURE CONSISTENCY CHECK{Colors.RESET}\n")

    # Group by figure
    by_figure = {}
    for r in results:
        if r.figure_id not in by_figure:
            by_figure[r.figure_id] = {"title": r.figure_title, "deps": []}
        by_figure[r.figure_id]["deps"].append(r)

    # Summary table
    print(f"{Colors.BOLD}Summary by Figure:{Colors.RESET}\n")
    print(f"{'Figure':<10} {'Title':<50} {'Status':<15} {'Critical Missing':<5}")
    print("-" * 85)

    exit_codes = []

    for figure_id in sorted(by_figure.keys()):
        fig_data = by_figure[figure_id]
        fig_results = fig_data["deps"]

        status, exit_code = determine_status(fig_results)
        critical_missing = sum(1 for r in fig_results if not r.found and r.severity == "CRITICAL")
        exit_codes.append(exit_code)

        # Color code status
        if status == "CURRENT":
            status_colored = f"{Colors.GREEN}{status}{Colors.RESET}"
        elif status == "STALE-MINOR":
            status_colored = f"{Colors.YELLOW}{status}{Colors.RESET}"
        else:  # STALE-CRITICAL
            status_colored = f"{Colors.RED}{status}{Colors.RESET}"

        title_truncated = fig_data["title"][:45] + "..." if len(fig_data["title"]) > 45 else fig_data["title"]
        print(f"{figure_id:<10} {title_truncated:<50} {status_colored:<15} {critical_missing:<5}")

        # Detailed deps if verbose
        if verbose:
            print(f"\n  {Colors.BOLD}Dependencies:{Colors.RESET}")
            for dep in fig_results:
                icon = Colors.GREEN + "✓" + Colors.RESET if dep.found else Colors.RED + "✗" + Colors.RESET
                print(
                    f"    {icon} [{dep.severity:8}] {dep.dependency_type:12} | {dep.claim[:60]}"
                )
                if not dep.found:
                    print(f"        Pattern: {dep.pattern[:70]}")
                else:
                    print(f"        Found in: {dep.source_file}")
                    if dep.matched_text:
                        preview = dep.matched_text.replace("\n", " ")[:80]
                        print(f"        Context: ...{preview}...")

    # Overall summary
    print("\n" + "=" * 85)
    max_exit = max(exit_codes) if exit_codes else 0

    if max_exit == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All figures CURRENT{Colors.RESET}")
    elif max_exit == 1:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some figures STALE-MINOR (non-critical deps missing){Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some figures STALE-CRITICAL (critical deps missing){Colors.RESET}")

    print(f"\nExit code: {max_exit}\n")
    return max_exit


def main():
    parser = argparse.ArgumentParser(
        description="Check ATLAS figure-document consistency"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Only check CRITICAL dependencies (faster)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=True,
        help="Check all dependencies (default)"
    )
    parser.add_argument(
        "--figure",
        type=str,
        help="Check only one figure (e.g., m1, m4, m24)"
    )
    parser.add_argument(
        "--add-tasks",
        action="store_true",
        help="Append stale findings to TASKS.md"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed dependency info"
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent
    contract_path = repo_root / "contracts" / "FIGURE_DEPENDENCIES.json"
    parts_dir = repo_root / "docs" / "master_doc_parts"
    tasks_path = repo_root / "TASKS.md"

    if not contract_path.exists():
        print(f"{Colors.RED}Error: {contract_path} not found{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

    if not parts_dir.exists():
        print(f"{Colors.RED}Error: {parts_dir} not found{Colors.RESET}", file=sys.stderr)
        sys.exit(1)

    # Load contract
    contract = load_dependencies_contract(contract_path)
    figures = contract.get("figures", {})

    # Filter if --figure specified
    if args.figure:
        fig_id = args.figure.lower()
        if fig_id not in figures:
            # Try with m_ prefix
            fig_id = f"m{fig_id}" if not fig_id.startswith("m") else fig_id
        if fig_id not in figures:
            print(f"{Colors.RED}Figure {args.figure} not found in contract{Colors.RESET}", file=sys.stderr)
            sys.exit(1)
        figures = {fig_id: figures[fig_id]}

    # Check all specified figures
    all_results = []
    for figure_id, figure_data in sorted(figures.items()):
        results = check_figure(
            figure_id,
            figure_data,
            parts_dir,
            critical_only=args.quick
        )
        all_results.extend(results)

    # Print results
    exit_code = print_results(all_results, verbose=args.verbose)

    # Add to TASKS.md if requested
    if args.add_tasks and exit_code > 0:
        stale_findings = [r for r in all_results if not r.found]
        if stale_findings:
            print(f"\n{Colors.CYAN}Adding stale findings to {tasks_path}...{Colors.RESET}")
            try:
                with open(tasks_path, "a") as f:
                    f.write("\n## Figure Consistency Check - Stale Dependencies\n\n")
                    f.write(f"*Last updated: 2026-03-02*\n\n")
                    f.write("| Figure | Type | Claim | Pattern | Severity |\n")
                    f.write("|--------|------|-------|---------|----------|\n")
                    for finding in stale_findings:
                        claim_short = finding.claim[:50] + "..." if len(finding.claim) > 50 else finding.claim
                        f.write(
                            f"| {finding.figure_id} | {finding.dependency_type} | {claim_short} | "
                            f"`{finding.pattern[:30]}...` | {finding.severity} |\n"
                        )
                print(f"{Colors.GREEN}✓ Added {len(stale_findings)} stale items to TASKS.md{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error writing to TASKS.md: {e}{Colors.RESET}", file=sys.stderr)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
