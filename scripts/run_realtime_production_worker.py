#!/usr/bin/env python3
"""
Continuous realtime production worker.

Each cycle:
1. Intake new AF papers into provisional abstract table/rule artifacts.
2. Integrate provisional abstract beliefs into Web + BN.
3. Drain PDF completion queue in batch for PDF-confirmed extraction.
4. Integrate PDF-confirmed beliefs into Web + BN.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_article_finder_db, resolve_web_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run realtime table/rule production worker continuously.")
    parser.add_argument("--af-db", default=None, help="Path to article_finder.db (auto-resolved if omitted)")
    parser.add_argument("--web-db", default=None, help="Path to web DB (auto-resolved if omitted)")
    parser.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    parser.add_argument("--poll-seconds", type=int, default=45, help="Seconds between cycles")
    parser.add_argument("--intake-limit", type=int, default=250, help="Max new papers per intake cycle")
    parser.add_argument("--pdf-batch-size", type=int, default=40, help="Max queued PDFs to process per cycle")
    parser.add_argument("--pdf-workers", type=int, default=4, help="Parallel workers for PDF extraction")
    parser.add_argument(
        "--pdf-timeout-seconds",
        type=int,
        default=900,
        help="Hard timeout for PDF completion subprocess per cycle",
    )
    parser.add_argument(
        "--preprocess-pdfs",
        action="store_true",
        help="Run parallel PDF preprocess stage before PDF extraction",
    )
    parser.add_argument(
        "--preprocess-batch-size",
        type=int,
        default=200,
        help="Max queued PDFs to preprocess per cycle",
    )
    parser.add_argument(
        "--preprocess-workers",
        type=int,
        default=8,
        help="Parallel workers for PDF preprocess",
    )
    parser.add_argument(
        "--skip-preprocess-quarantine",
        action="store_true",
        help="Skip queued rows marked preprocess_status=quarantine/error during extraction",
    )
    parser.add_argument(
        "--quality-gate",
        action="store_true",
        help="Run extraction quality gate each cycle",
    )
    parser.add_argument(
        "--bn-state-path",
        default="data/production/realtime_incremental_bn.json",
        help="Shared incremental BN persistence path",
    )
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    return parser.parse_args()


def run_cmd(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return int(proc.returncode)


def run_cmd_with_timeout(cmd: list[str], timeout_seconds: int | None = None) -> int:
    try:
        proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), timeout=timeout_seconds)
        return int(proc.returncode)
    except subprocess.TimeoutExpired:
        print(f"[worker] timeout after {timeout_seconds}s: {' '.join(cmd)}")
        return 124


def collect_metrics(bn_state_path: Path) -> dict:
    metrics = {
        "web_beliefs": None,
        "web_constraints": None,
        "bn_nodes": None,
        "bn_edges": None,
    }

    try:
        web_db = resolve_web_db(prefer="integrated")
    except Exception:
        web_db = PROJECT_ROOT / "data" / "web_persistence.db"
    if web_db.exists():
        try:
            conn = sqlite3.connect(str(web_db))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM beliefs")
            metrics["web_beliefs"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM constraints")
            metrics["web_constraints"] = cur.fetchone()[0]
            conn.close()
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    if bn_state_path.exists():
        try:
            data = json.loads(bn_state_path.read_text(encoding="utf-8"))
            metrics["bn_nodes"] = len(data.get("nodes", []))
            metrics["bn_edges"] = len(data.get("edges", {}))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    return metrics


def run_cycle(args: argparse.Namespace) -> int:
    py = sys.executable
    af_db = resolve_article_finder_db(args.af_db)
    web_db = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    print(f"[worker] using af_db={af_db} web_db={web_db}")

    preprocess_cmd = [
        py,
        "scripts/preprocess_pdf_queue.py",
        "--queued-only",
        "--batch-size",
        str(args.preprocess_batch_size),
        "--max-workers",
        str(args.preprocess_workers),
    ]
    intake_cmd = [
        py,
        "scripts/run_realtime_table_rule_intake.py",
        "--db",
        str(af_db),
        "--web-db",
        str(web_db),
        "--web-db-prefer",
        args.web_db_prefer,
        "--limit",
        str(args.intake_limit),
        "--integrate-web",
        "--update-bn",
        "--bn-state-path",
        str(args.bn_state_path),
    ]
    pdf_cmd = [
        py,
        "scripts/process_realtime_pdf_completion_queue.py",
        "--af-db",
        str(af_db),
        "--web-db",
        str(web_db),
        "--web-db-prefer",
        args.web_db_prefer,
        "--batch-size",
        str(args.pdf_batch_size),
        "--max-workers",
        str(args.pdf_workers),
        "--prioritize-preprocessed",
        "--integrate-web",
        "--update-bn",
        "--bn-state-path",
        str(args.bn_state_path),
    ]
    if args.skip_preprocess_quarantine:
        pdf_cmd.append("--skip-preprocess-quarantine")
    quality_cmd = [
        py,
        "scripts/check_table_extraction_quality.py",
    ]

    print(f"[worker] intake start (limit={args.intake_limit})")
    rc1 = run_cmd(intake_cmd)
    print(f"[worker] intake rc={rc1}")

    rc0 = 0
    if args.preprocess_pdfs:
        print(
            "[worker] pdf preprocess start "
            f"(batch={args.preprocess_batch_size}, workers={args.preprocess_workers})"
        )
        rc0 = run_cmd(preprocess_cmd)
        print(f"[worker] pdf preprocess rc={rc0}")

    print(
        f"[worker] pdf completion start "
        f"(batch={args.pdf_batch_size}, workers={args.pdf_workers})"
    )
    rc2 = run_cmd_with_timeout(pdf_cmd, timeout_seconds=int(args.pdf_timeout_seconds))
    print(f"[worker] pdf completion rc={rc2}")

    rc3 = 0
    if args.quality_gate:
        print("[worker] quality gate start")
        rc3 = run_cmd(quality_cmd)
        print(f"[worker] quality gate rc={rc3}")

    metrics = collect_metrics(Path(args.bn_state_path))
    print(
        "[worker] metrics "
        f"web_beliefs={metrics['web_beliefs']} "
        f"web_constraints={metrics['web_constraints']} "
        f"bn_nodes={metrics['bn_nodes']} "
        f"bn_edges={metrics['bn_edges']}"
    )

    if args.quality_gate:
        return 0 if rc0 == 0 and rc1 == 0 and rc2 == 0 and rc3 == 0 else 1
    return 0 if rc0 == 0 and rc1 == 0 and rc2 == 0 else 1


def main() -> int:
    args = parse_args()
    cycle = 0

    while True:
        cycle += 1
        print(f"[worker] cycle={cycle} begin")
        rc = run_cycle(args)
        print(f"[worker] cycle={cycle} end rc={rc}")

        if args.once:
            return rc

        time.sleep(max(1, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
