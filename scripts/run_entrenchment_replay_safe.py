#!/usr/bin/env python3
"""
Run scholarly entrenchment replay safely against a copied DB by default.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

# Ensure script execution works from repository checkout without PYTHONPATH setup.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

PaperWebLoader = Callable[[str], Optional["WebOfBelief"]]


def _load_loader(spec: str) -> PaperWebLoader:
    """
    Resolve loader from module:function string.
    """
    if ":" not in spec:
        raise ValueError("loader spec must be in module:function format")
    module_name, fn_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    fn = getattr(module, fn_name, None)
    if fn is None or not callable(fn):
        raise ValueError(f"loader callable not found: {spec}")
    return fn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safe scholarly replay runner using DB copy strategy."
    )
    parser.add_argument("--source-db", default="ae.db", help="Path to live/source DB.")
    parser.add_argument(
        "--replay-db",
        default=None,
        help="Path for replay DB copy. If omitted, creates timestamped copy in --copy-dir.",
    )
    parser.add_argument(
        "--copy-dir",
        default="data/replay",
        help="Directory for timestamped replay DB copies.",
    )
    parser.add_argument(
        "--overwrite-replay-db",
        action="store_true",
        help="Overwrite existing --replay-db target.",
    )
    parser.add_argument(
        "--allow-mutating-master",
        action="store_true",
        help="Disable safe-copy mode and run replay directly on source DB.",
    )
    parser.add_argument(
        "--paper-id",
        action="append",
        default=None,
        help="Optional paper_id to replay (repeatable).",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max papers to replay.")
    parser.add_argument(
        "--loader",
        default=None,
        help="Custom paper web loader in module:function format.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to write JSON summary.",
    )
    return parser.parse_args()


def main() -> int:
    from src.services.entrenchment_replay import ScholarlyReplayService

    args = parse_args()

    if args.allow_mutating_master:
        service = ScholarlyReplayService(
            source_db_path=args.source_db,
            replay_db_path=args.replay_db or args.source_db,
        )
    else:
        service = ScholarlyReplayService.with_safe_replay_copy(
            source_db_path=args.source_db,
            replay_db_path=args.replay_db,
            copy_dir=args.copy_dir,
            overwrite=args.overwrite_replay_db,
        )

    loader = _load_loader(args.loader) if args.loader else service.make_master_filtered_loader()
    reports = service.replay(
        paper_web_loader=loader,
        paper_ids=args.paper_id,
        limit=args.limit,
        allow_mutating_master=args.allow_mutating_master,
    )

    summary: dict[str, Any] = {
        "source_db": service.source_db_path,
        "replay_db": service.replay_db_path,
        "safe_mode": not args.allow_mutating_master,
        "paper_ids_filter": args.paper_id or [],
        "limit": args.limit,
        "reports_count": len(reports),
        "totals": {
            "beliefs_added": sum(r.get("n_beliefs_added", 0) for r in reports),
            "beliefs_updated": sum(r.get("n_beliefs_updated", 0) for r in reports),
            "constraints_added": sum(r.get("n_constraints_added", 0) for r in reports),
        },
    }

    output = {"summary": summary, "reports": reports}
    text = json.dumps(output, indent=2)
    print(text)

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
