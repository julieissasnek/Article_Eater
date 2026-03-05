#!/usr/bin/env python3
"""
Backfill Effect Sizes — Compute Cohen's d from Available Statistics
====================================================================

Many older papers report F-statistics, t-values, r-values, or p-values
but not Cohen's d directly. This script:

  1. Scans all extraction JSONs for findings missing effect_size
  2. Parses test_statistic strings to extract F(df1,df2)=x, t(df)=x, etc.
  3. Uses effect_size_converter.to_cohens_d() to compute d
  4. Falls back to p-value + N conversion when test stat unavailable
  5. Writes computed d back to the extraction JSON (non-destructive)

NO API calls — pure math. Runs in ~30 seconds for full corpus.

Usage:
  python3 scripts/backfill_effect_sizes.py --dry-run     # Preview only
  python3 scripts/backfill_effect_sizes.py               # Write changes
  python3 scripts/backfill_effect_sizes.py --limit 50    # First 50 articles

Author: AG
Date: 2026-03-04
"""

import json
import re
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.effect_size_converter import to_cohens_d

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXT_DIR = PROJECT_ROOT / "data" / "extractions"


# ═══════════════════════════════════════════════════════════════
# Test statistic parsers
# ═══════════════════════════════════════════════════════════════

def parse_f_stat(ts: str) -> Optional[Dict[str, Any]]:
    """Parse F(df1, df2) = value from test_statistic string."""
    # Patterns: F(2,45)=3.21, F(1, 98) = 4.56, F(2,120)=7.8
    m = re.search(r'F\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*=\s*([\d.]+)', ts)
    if m:
        return {
            "stat_type": "f_value",
            "value": float(m.group(3)),
            "df1": int(m.group(1)),
            "df2": int(m.group(2)),
        }
    return None


def parse_t_stat(ts: str) -> Optional[Dict[str, Any]]:
    """Parse t(df) = value from test_statistic string."""
    # Patterns: t(98)=2.45, t(45) = -1.23
    m = re.search(r't\s*\(\s*(\d+)\s*\)\s*=\s*(-?[\d.]+)', ts)
    if m:
        return {
            "stat_type": "t_value",
            "value": float(m.group(2)),
            "df2": int(m.group(1)),
        }
    return None


def parse_chi_sq(ts: str) -> Optional[Dict[str, Any]]:
    """Parse χ²(df) = value. Can't directly convert to d without phi/V."""
    return None  # Chi-squared needs Cramer's V → r → d, too lossy


def parse_r_value(ts: str) -> Optional[Dict[str, Any]]:
    """Parse r = value from test_statistic string."""
    # Patterns: r=0.45, r = -0.32, r(45)=0.28
    m = re.search(r'r\s*(?:\(\d+\))?\s*=\s*(-?[\d.]+)', ts)
    if m:
        val = float(m.group(1))
        if -1 < val < 1:
            return {"stat_type": "r", "value": val}
    return None


def parse_eta_sq(ts: str) -> Optional[Dict[str, Any]]:
    """Parse η² = value or eta² = value."""
    m = re.search(r'(?:η[²p]?|eta[²_]?(?:squared|sq|p)?)\s*=\s*([\d.]+)', ts, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        if 0 <= val < 1:
            return {"stat_type": "eta_squared", "value": val}
    return None


def parse_beta(ts: str) -> Optional[Dict[str, Any]]:
    """Parse β = value or beta = value."""
    m = re.search(r'(?:β|[Bb]eta)\s*=\s*(-?[\d.]+)', ts)
    if m:
        val = float(m.group(1))
        if -1 < val < 1:
            return {"stat_type": "beta", "value": val}
    return None


def parse_test_statistic(ts: str) -> Optional[Dict[str, Any]]:
    """Try all parsers in priority order."""
    for parser in [parse_f_stat, parse_t_stat, parse_r_value, parse_eta_sq, parse_beta]:
        result = parser(ts)
        if result:
            return result
    return None


def parse_p_value(pv: Any) -> Optional[float]:
    """Parse p-value from various formats to numeric."""
    if pv is None or pv == "" or pv == "null":
        return None
    if isinstance(pv, (int, float)):
        return float(pv) if 0 < float(pv) < 1 else None
    s = str(pv).strip().lower()
    if s in ("significant", "ns", "not significant"):
        return None
    # Handle "<0.001", "<.05", "< 0.01"
    m = re.match(r'<\s*([\d.]+)', s)
    if m:
        return float(m.group(1))
    # Handle "p = 0.003" or just "0.003"
    m = re.match(r'(?:p\s*[=<>])?\s*([\d.]+)', s)
    if m:
        val = float(m.group(1))
        if 0 < val < 1:
            return val
    return None


# ═══════════════════════════════════════════════════════════════
# Main backfill logic
# ═══════════════════════════════════════════════════════════════

def backfill_article(filepath: Path, dry_run: bool = True) -> Dict[str, int]:
    """Compute Cohen's d for findings missing effect_size in one article."""
    stats = {"computed_from_test_stat": 0, "computed_from_p": 0,
             "already_has": 0, "no_data": 0, "error": 0}

    try:
        data = json.loads(filepath.read_text(errors="replace"))
    except (json.JSONDecodeError, Exception):
        return stats

    if not isinstance(data, dict):
        return stats

    findings = data.get("findings", [])
    if not findings:
        return stats

    modified = False

    for finding in findings:
        es = finding.get("effect_size")
        if es is not None and es != "" and es != "null":
            stats["already_has"] += 1
            continue

        ts = str(finding.get("test_statistic", "") or "")
        pv = finding.get("p_value")
        sn = finding.get("sample_size") or finding.get("sample_n")

        # Strategy 1: Parse test_statistic → compute d
        if ts:
            parsed = parse_test_statistic(ts)
            if parsed:
                try:
                    result = to_cohens_d(**parsed)
                    d = result["d"]
                    finding["effect_size"] = round(abs(d), 4)
                    finding["effect_size_type"] = "Cohen's d"
                    finding["effect_size_computed"] = True
                    finding["effect_size_method"] = result["method"]
                    if result.get("assumptions"):
                        finding["effect_size_assumptions"] = result["assumptions"]
                    # Preserve direction sign
                    direction = finding.get("direction", "")
                    if direction == "decrease" and d > 0:
                        finding["effect_size"] = round(-abs(d), 4)
                    elif direction == "increase" and d < 0:
                        finding["effect_size"] = round(abs(d), 4)
                    stats["computed_from_test_stat"] += 1
                    modified = True
                    continue
                except (ValueError, ZeroDivisionError):
                    stats["error"] += 1

        # Strategy 2: p-value + sample_size → approximate d
        p_num = parse_p_value(pv)
        if p_num and sn and int(sn) > 2:
            try:
                result = to_cohens_d(
                    value=p_num, stat_type="p_value_only", n=int(sn)
                )
                d = result["d"]
                finding["effect_size"] = round(abs(d), 4)
                finding["effect_size_type"] = "Cohen's d"
                finding["effect_size_computed"] = True
                finding["effect_size_method"] = "p_to_z_to_d"
                finding["effect_size_assumptions"] = result.get("assumptions", [])
                direction = finding.get("direction", "")
                if direction == "decrease":
                    finding["effect_size"] = round(-abs(d), 4)
                stats["computed_from_p"] += 1
                modified = True
                continue
            except (ValueError, ZeroDivisionError):
                stats["error"] += 1

        stats["no_data"] += 1

    if modified and not dry_run:
        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Backfill Cohen's d from test statistics")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't write")
    parser.add_argument("--limit", type=int, help="Limit number of articles")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not EXT_DIR.exists():
        logger.error(f"No extractions directory: {EXT_DIR}")
        sys.exit(1)

    files = sorted(EXT_DIR.glob("*.json"))
    if args.limit:
        files = files[:args.limit]

    totals = {"computed_from_test_stat": 0, "computed_from_p": 0,
              "already_has": 0, "no_data": 0, "error": 0}
    articles_modified = 0

    for i, f in enumerate(files):
        stats = backfill_article(f, dry_run=args.dry_run)
        for k, v in stats.items():
            totals[k] += v
        if stats["computed_from_test_stat"] + stats["computed_from_p"] > 0:
            articles_modified += 1
            if args.verbose:
                logger.info(f"  [{i+1}] {f.name}: +{stats['computed_from_test_stat']} test_stat, +{stats['computed_from_p']} p-value")

    total_computed = totals["computed_from_test_stat"] + totals["computed_from_p"]
    total_findings = sum(totals.values())

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Effect Size Backfill Results")
    print(f"{'=' * 50}")
    print(f"  Articles scanned:    {len(files)}")
    print(f"  Articles modified:   {articles_modified}")
    print(f"  Total findings:      {total_findings:,}")
    print(f"  Already had effect:  {totals['already_has']:,} ({totals['already_has']/max(total_findings,1)*100:.1f}%)")
    print(f"  Computed from test:  {totals['computed_from_test_stat']:,}")
    print(f"  Computed from p+N:   {totals['computed_from_p']:,}")
    print(f"  Total computed:      {total_computed:,}")
    print(f"  No computable data:  {totals['no_data']:,}")
    print(f"  Errors:              {totals['error']}")
    if total_computed:
        new_coverage = (totals['already_has'] + total_computed) / max(total_findings, 1) * 100
        print(f"\n  Coverage: {totals['already_has']/max(total_findings,1)*100:.1f}% → {new_coverage:.1f}%")


if __name__ == "__main__":
    main()
