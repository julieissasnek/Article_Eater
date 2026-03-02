#!/usr/bin/env python3
"""
backfill_sample_n.py — Extract sample sizes from existing extraction data
=========================================================================

Scans extraction JSONs for sample size information stored at article level
(in 'participants', 'sample_size', etc.) and propagates it to individual
findings. Also attempts to parse sample size from finding text.

Usage:
    python3 scripts/backfill_sample_n.py              # Dry-run report
    python3 scripts/backfill_sample_n.py --fix        # Fix in-place
"""

import argparse
import json
import glob
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "extractions"


def extract_sample_n_from_participants(participants_text: str) -> Optional[int]:
    """
    Parse sample size from a 'participants' field string.
    
    Examples:
        "48 university students" → 48
        "N=120 (60 per group)" → 120
        "200 office workers, 100 male 100 female" → 200
        "24 participants aged 18-35" → 24
    """
    if not participants_text or not isinstance(participants_text, str):
        return None
    
    text = participants_text.strip()
    
    # Pattern: N=X or n=X
    m = re.search(r'[Nn]\s*=\s*(\d+)', text)
    if m:
        return int(m.group(1))
    
    # Pattern: starts with a number
    m = re.match(r'^(\d+)\s+', text)
    if m:
        n = int(m.group(1))
        if 2 <= n <= 100000:  # Plausible sample size range
            return n
    
    # Pattern: "total of X" or "a total of X"
    m = re.search(r'total\s+of\s+(\d+)', text, re.I)
    if m:
        return int(m.group(1))
    
    # Pattern: "X participants" anywhere
    m = re.search(r'(\d+)\s+participant', text, re.I)
    if m:
        return int(m.group(1))
    
    # Pattern: "X subjects" anywhere
    m = re.search(r'(\d+)\s+subject', text, re.I)
    if m:
        return int(m.group(1))
    
    # Pattern: "X students" anywhere
    m = re.search(r'(\d+)\s+student', text, re.I)
    if m:
        return int(m.group(1))
    
    # Pattern: "X respondents" anywhere
    m = re.search(r'(\d+)\s+respondent', text, re.I)
    if m:
        return int(m.group(1))
    
    # Pattern: "X adults/workers/employees/volunteers"
    m = re.search(r'(\d+)\s+(?:adult|worker|employee|volunteer|occupant|resident|person|people|individual)', text, re.I)
    if m:
        return int(m.group(1))
    
    return None


def extract_sample_n_from_finding(finding: dict) -> Optional[int]:
    """
    Try to extract sample_n from a finding dict.
    
    Checks multiple field names and falls back to text parsing.
    """
    # Direct fields
    for field in ['sample_n', 'sample_size', 'n', 'N', 'participants_n']:
        v = finding.get(field)
        if v is not None:
            try:
                n = int(float(str(v).strip()))
                if 2 <= n <= 100000:
                    return n
            except (ValueError, TypeError):
                pass
    
    # Parse from 'participants' text in finding
    p = finding.get('participants', '')
    if p:
        n = extract_sample_n_from_participants(str(p))
        if n:
            return n
    
    return None


def backfill_file(fpath: str, fix: bool = False) -> Tuple[int, int, int]:
    """
    Backfill sample_n for a single extraction file.
    
    Returns (total_findings, already_have, newly_backfilled)
    """
    try:
        with open(fpath) as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return (0, 0, 0)
    
    if not isinstance(data, dict):
        return (0, 0, 0)
    
    # Get article-level sample size
    article_n = None
    for field in ['participants', 'sample_size', 'sample_n', 'n_participants']:
        v = data.get(field)
        if v is not None:
            if isinstance(v, (int, float)) and 2 <= v <= 100000:
                article_n = int(v)
                break
            elif isinstance(v, str):
                n = extract_sample_n_from_participants(v)
                if n:
                    article_n = n
                    break
    
    findings = data.get('findings', [])
    total = len(findings)
    already_have = 0
    newly_backfilled = 0
    modified = False
    
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        
        # Check if already has sample_n
        existing_n = extract_sample_n_from_finding(finding)
        if existing_n:
            already_have += 1
            # Normalize to 'sample_n' field
            if 'sample_n' not in finding and fix:
                finding['sample_n'] = existing_n
                modified = True
            continue
        
        # Try to backfill from article level
        if article_n:
            newly_backfilled += 1
            if fix:
                finding['sample_n'] = article_n
                finding['sample_n_source'] = 'article_level_backfill'
                modified = True
    
    if fix and modified:
        with open(fpath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return (total, already_have, newly_backfilled)


def main():
    parser = argparse.ArgumentParser(description="Backfill sample_n in extraction JSONs")
    parser.add_argument("--fix", action="store_true", help="Fix in-place")
    args = parser.parse_args()
    
    files = sorted(glob.glob(str(DATA_DIR / "*.json")))
    
    total_findings = 0
    total_already = 0
    total_backfilled = 0
    files_modified = 0
    
    for fpath in files:
        t, a, b = backfill_file(fpath, fix=args.fix)
        total_findings += t
        total_already += a
        total_backfilled += b
        if b > 0:
            files_modified += 1
    
    coverage_before = total_already / max(total_findings, 1) * 100
    coverage_after = (total_already + total_backfilled) / max(total_findings, 1) * 100
    
    print("═" * 60)
    print("  SAMPLE_N BACKFILL RESULTS")
    print("═" * 60)
    print(f"  Files scanned: {len(files)}")
    print(f"  Total findings: {total_findings}")
    print(f"  Already have sample_n: {total_already} ({coverage_before:.1f}%)")
    print(f"  Newly backfilled: {total_backfilled}")
    print(f"  Coverage after: {coverage_after:.1f}%")
    print(f"  Files that would be modified: {files_modified}")
    if not args.fix:
        print(f"\n  (Dry run — use --fix to apply)")
    else:
        print(f"\n  ✅ {files_modified} files modified")


if __name__ == "__main__":
    main()
