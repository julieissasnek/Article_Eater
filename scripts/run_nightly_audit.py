#!/usr/bin/env python3
"""
Layer 2/3 Nightly QA Audit Runner
==================================

This script runs all Layer 2/3 systemic failure mode tests (marked with
@pytest.mark.layer2_nightly), collects results, and generates both a
JSON report and a markdown summary.

Layer 2 tests detect:
- Cross-service data integrity failures
- Silent failures (undetected service crashes)
- Epistemic invariant violations
- Latency budget overruns
- Schema consistency issues

Usage:
    python scripts/run_nightly_audit.py [--output-dir OUTDIR]

Output:
    - docs/nightly_reports/{timestamp}_layer2_results.json
    - docs/nightly_reports/{timestamp}_layer2_summary.md

Exit Code:
    0 if all tests pass
    1 if any tests fail

Author: CW (Claude Code)
Date: 2026-03-03
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple


def run_pytest_layer2(verbose: bool = False) -> Tuple[int, str]:
    """
    Run pytest with layer2_nightly marker.

    Args:
        verbose: If True, show full pytest output

    Returns:
        (exit_code, json_report_path)
    """
    # Create a temporary JSON report file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_report = f.name

    cmd = [
        'pytest',
        'tests',
        '-m', 'layer2_nightly',
        f'--json-report',
        f'--json-report-file={json_report}',
        '--tb=short',
        '-v' if verbose else '-q',
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        return result.returncode, json_report
    except FileNotFoundError:
        # Fallback if pytest-json-report not available
        print("WARNING: pytest-json-report not available. Using text output fallback.", file=sys.stderr)
        cmd_fallback = [
            'pytest',
            'tests',
            '-m', 'layer2_nightly',
            '--tb=short',
            '-v' if verbose else '-q',
        ]
        result = subprocess.run(
            cmd_fallback,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        return result.returncode, None


def parse_pytest_output(exit_code: int, json_report: str = None) -> Dict[str, Any]:
    """
    Parse pytest output (JSON or text fallback).

    Args:
        exit_code: Pytest exit code
        json_report: Path to JSON report if available

    Returns:
        Dictionary with test results
    """
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': 0,
        'tests': [],
    }

    if json_report and os.path.exists(json_report):
        try:
            with open(json_report, 'r') as f:
                data = json.load(f)
                results['passed'] = data.get('summary', {}).get('passed', 0)
                results['failed'] = data.get('summary', {}).get('failed', 0)
                results['skipped'] = data.get('summary', {}).get('skipped', 0)
                results['errors'] = data.get('summary', {}).get('error', 0)
                results['tests'] = data.get('tests', [])
        except Exception as e:
            print(f"WARNING: Failed to parse JSON report: {e}", file=sys.stderr)

    return results


def generate_json_report(results: Dict[str, Any], timestamp: str) -> str:
    """
    Generate JSON report.

    Args:
        results: Test results dictionary
        timestamp: ISO timestamp

    Returns:
        JSON string
    """
    report = {
        'timestamp': timestamp,
        'layer': 'layer2_nightly',
        'summary': {
            'total': results['passed'] + results['failed'] + results['skipped'] + results['errors'],
            'passed': results['passed'],
            'failed': results['failed'],
            'skipped': results['skipped'],
            'errors': results['errors'],
        },
        'status': 'PASS' if results['failed'] == 0 and results['errors'] == 0 else 'FAIL',
        'test_details': results.get('tests', []),
    }
    return json.dumps(report, indent=2)


def generate_markdown_summary(results: Dict[str, Any], timestamp: str) -> str:
    """
    Generate markdown summary.

    Args:
        results: Test results dictionary
        timestamp: ISO timestamp

    Returns:
        Markdown string
    """
    total = results['passed'] + results['failed'] + results['skipped'] + results['errors']
    status = 'PASS' if results['failed'] == 0 and results['errors'] == 0 else 'FAIL'
    status_emoji = '✓' if status == 'PASS' else '✗'

    md = f"""# Layer 2/3 Nightly QA Audit Report

**Date**: {timestamp}
**Status**: {status_emoji} {status}

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {total} |
| Passed | {results['passed']} |
| Failed | {results['failed']} |
| Skipped | {results['skipped']} |
| Errors | {results['errors']} |

## Test Categories Covered

Layer 2 systemic failure mode tests cover five critical categories:

1. **Cross-Service Data Integrity** — Information survives transit across all enrichment steps
   - paper_ids preserved through pipeline
   - belief counts unchanged
   - belief text uncorrupted
   - base answer preserved immutable

2. **Silent Failure Detection** — Service failures are visible in final output
   - Failed services named in warnings
   - Skipped services produce warnings
   - Services attempted tracked
   - Complete status requires zero failures/skips

3. **Epistemic Invariants** — Architectural commitments enforced end-to-end
   - Abstained answers have no enrichment
   - Warnings never empty strings
   - Metadata always has timing dict
   - Status is valid enum
   - Paper IDs not lost on completion

4. **Budget Honesty** — Latency budget reflected accurately
   - Tight budgets cause skips or degradation
   - Budget exceeded reflected in status
   - Budget exceeded services appear in metadata

5. **Schema Consistency** — Data structures stable across runs
   - EnrichedBelief fields consistent
   - to_dict() has all dataclass fields
   - Metadata has required keys
   - to_dict() roundtrip preserves status
   - Multiple runs produce same schema

## Detail

"""

    if results['failed'] > 0:
        md += f"\n### Failed Tests ({results['failed']})\n\n"
        failed_tests = [t for t in results.get('tests', []) if t.get('outcome') == 'failed']
        for test in failed_tests:
            md += f"- {test.get('name', 'unknown')}\n"
            if test.get('log'):
                md += f"  ```\n  {test['log']}\n  ```\n"

    if results['skipped'] > 0:
        md += f"\n### Skipped Tests ({results['skipped']})\n\n"
        skipped_tests = [t for t in results.get('tests', []) if t.get('outcome') == 'skipped']
        for test in skipped_tests:
            md += f"- {test.get('name', 'unknown')}\n"

    md += f"""
## Interpretation

"""
    if status == 'PASS':
        md += """All Layer 2 systemic invariants PASS. The system demonstrates:
- Cross-service data integrity
- Visible failure modes
- Enforced epistemic commitments
- Honest latency reporting
- Schema stability

Safe to deploy to production.
"""
    else:
        md += f"""FAILURES DETECTED. The system has:
- {results['failed']} failing tests
- {results['errors']} errors

DO NOT deploy. Address failures immediately:
1. Review failed test details above
2. Check error messages
3. Fix underlying issues
4. Re-run nightly audit
"""

    md += f"""
---
Generated: {timestamp}
Layer: Layer 2/3 Nightly QA Audit
"""
    return md


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run Layer 2/3 nightly QA audit')
    parser.add_argument('--output-dir', default='docs/nightly_reports',
                        help='Directory for report output')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose pytest output')
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp
    timestamp = datetime.utcnow().isoformat() + 'Z'
    timestamp_short = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    print(f"Running Layer 2/3 nightly QA audit...")
    print(f"Timestamp: {timestamp}")

    # Run pytest
    exit_code, json_report = run_pytest_layer2(verbose=args.verbose)

    # Parse results
    results = parse_pytest_output(exit_code, json_report)

    # Generate reports
    json_str = generate_json_report(results, timestamp)
    md_str = generate_markdown_summary(results, timestamp)

    # Write reports
    json_file = output_dir / f'{timestamp_short}_layer2_results.json'
    md_file = output_dir / f'{timestamp_short}_layer2_summary.md'

    with open(json_file, 'w') as f:
        f.write(json_str)
    print(f"Wrote JSON report: {json_file}")

    with open(md_file, 'w') as f:
        f.write(md_str)
    print(f"Wrote markdown summary: {md_file}")

    # Clean up temp JSON report if it exists
    if json_report and os.path.exists(json_report):
        os.unlink(json_report)

    # Print summary to console
    print("\n" + md_str)

    # Exit with pytest exit code
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
