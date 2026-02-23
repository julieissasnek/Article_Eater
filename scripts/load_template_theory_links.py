#!/usr/bin/env python3
"""Load template theory-links from template causal_links into CMR staging table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cmr.staging_theory_loader import load_staging_theory_links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates-dir", type=Path, default=Path("data/templates"))
    parser.add_argument("--db-path", type=str, default="ae.db")
    parser.add_argument("--no-clear", action="store_true", help="Append instead of replacing table rows.")
    args = parser.parse_args()

    summary = load_staging_theory_links(
        templates_dir=args.templates_dir,
        db_path=args.db_path,
        clear_existing=not args.no_clear,
    )
    print(f"Templates scanned:    {summary['templates_scanned']}")
    print(f"Templates with links: {summary['templates_with_links']}")
    print(f"Rows inserted:        {summary['rows_inserted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
