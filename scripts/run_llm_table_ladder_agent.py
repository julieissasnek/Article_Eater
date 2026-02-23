#!/usr/bin/env python3
"""Run high->balanced->low table extraction pilots as a managed benchmark ladder.

Key goals:
- Launch model tiers in separate background jobs (detached optional).
- Keep run artifacts isolated under one ladder run directory.
- Produce a merged summary for direct cross-tier comparison.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_CSV = "data/production/realtime_pdf_completion_queue.csv"
DEFAULT_OUTPUT_DIR = "data/production/llm_pilot"
DEFAULT_PROFILES_PATH = "config/llm_table_pilot_profiles.codex.json"
PILOT_SCRIPT = "scripts/run_llm_table_pilot.py"


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: str
    model: str


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_tag(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-_.") or "run"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_profiles(path: Path) -> list[ModelProfile]:
    payload = _load_json(path)
    out: list[ModelProfile] = []
    for item in payload.get("profiles", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        provider = str(item.get("provider") or "").strip()
        model = str(item.get("model") or "").strip()
        if not name or not provider or not model:
            continue
        out.append(ModelProfile(name=name, provider=provider, model=model))
    if not out:
        raise SystemExit(f"No usable profiles in {path}")
    return out


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_rc(path: Path) -> int | None:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    try:
        return int(raw)
    except Exception:
        return 1


def _job_state(job: dict[str, Any]) -> dict[str, Any]:
    pid = int(job["pid"])
    rc_path = Path(job["rc_path"])
    rc = _read_rc(rc_path)
    if rc is not None:
        return {"name": job["name"], "status": "success" if rc == 0 else "failed", "rc": rc}
    if _pid_alive(pid):
        return {"name": job["name"], "status": "running", "rc": None}
    return {"name": job["name"], "status": "dead_no_rc", "rc": None}


def _build_job_command(
    profile_cfg: Path,
    queue_csv: str,
    output_dir: Path,
    n_pdfs: int,
    max_pages: int,
    variants: str,
    vocab_path: str,
) -> list[str]:
    return [
        "python3",
        PILOT_SCRIPT,
        "--queue-csv",
        queue_csv,
        "--profiles",
        str(profile_cfg),
        "--n-pdfs",
        str(n_pdfs),
        "--max-pages",
        str(max_pages),
        "--variants",
        variants,
        "--output-dir",
        str(output_dir),
        "--vocab-path",
        vocab_path,
    ]


def _spawn_job(cmd: list[str], log_path: Path, rc_path: Path) -> subprocess.Popen[bytes]:
    quoted = " ".join(shlex.quote(part) for part in cmd)
    shell_cmd = (
        f"cd {shlex.quote(str(PROJECT_ROOT))} && "
        f"{quoted} > {shlex.quote(str(log_path))} 2>&1; "
        f"rc=$?; echo $rc > {shlex.quote(str(rc_path))}; exit $rc"
    )
    return subprocess.Popen(
        ["/bin/zsh", "-lc", shell_cmd],
        start_new_session=True,
    )


def _counts(states: list[dict[str, Any]]) -> dict[str, int]:
    out = {"running": 0, "success": 0, "failed": 0, "dead_no_rc": 0}
    for item in states:
        status = item.get("status")
        if status in out:
            out[status] += 1
    return out


def _parse_summary_path(log_path: Path) -> Path | None:
    if not log_path.exists():
        return None
    raw = log_path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"Summary written:\s+(.+)", raw)
    if not matches:
        return None
    last = matches[-1].strip()
    p = Path(last)
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()
    return p


def _collect_runs(summary_paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in summary_paths:
        payload = _load_json(path)
        for run in payload.get("runs", []):
            metrics = run.get("metrics") or {}
            mapped = float(metrics.get("mapped_both_pct") or 0.0)
            suspect = float(metrics.get("suspect_claims_pct") or 0.0)
            unknown = float(metrics.get("unknown_direction_pct") or 0.0)
            rows.append(
                {
                    "profile": run.get("profile"),
                    "provider": run.get("provider"),
                    "model": run.get("model"),
                    "variant": run.get("variant"),
                    "output": run.get("output"),
                    "claims": int(metrics.get("claims") or 0),
                    "mapped_both_pct": mapped,
                    "suspect_claims_pct": suspect,
                    "unknown_direction_pct": unknown,
                    "precision_proxy": round(mapped - suspect - unknown, 2),
                }
            )
    return rows


def _render_summary_md(payload: dict[str, Any]) -> str:
    lines = [
        "# LLM Ladder Summary",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Generated: `{payload['generated_at']}`",
        f"- Total runs: `{payload['total_runs']}`",
        "",
        "| profile | variant | model | claims | mapped% | suspect% | unknown_dir% | precision_proxy |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload.get("runs", []):
        lines.append(
            f"| {row.get('profile')} | {row.get('variant')} | {row.get('model')} | "
            f"{row.get('claims')} | {row.get('mapped_both_pct')} | {row.get('suspect_claims_pct')} | "
            f"{row.get('unknown_direction_pct')} | {row.get('precision_proxy')} |"
        )
    lines.extend(
        [
            "",
            "## Best Precision Proxy",
        ]
    )
    best = payload.get("best_by_precision_proxy")
    if best:
        lines.append(
            f"- `{best['profile']}` / `{best['variant']}` / `{best['model']}` "
            f"with precision_proxy `{best['precision_proxy']}`"
        )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _run_status(manifest_path: Path, as_json: bool = False) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    states = [_job_state(job) for job in manifest.get("jobs", [])]
    counts = _counts(states)
    payload = {
        "manifest": str(manifest_path),
        "run_id": manifest.get("run_id"),
        "run_dir": manifest.get("run_dir"),
        "states": states,
        "counts": counts,
        "all_done": counts["running"] == 0 and counts["dead_no_rc"] == 0,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"manifest={manifest_path}")
        print(f"run_id={manifest.get('run_id')}")
        for state in states:
            suffix = f" rc={state['rc']}" if state.get("rc") is not None else ""
            print(f"- {state['name']}: {state['status']}{suffix}")
        print(f"counts={counts}")
    return payload


def _run_summarize(manifest_path: Path) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    run_dir = Path(manifest["run_dir"])

    summary_paths: list[Path] = []
    for job in manifest.get("jobs", []):
        p = _parse_summary_path(Path(job["log_path"]))
        if p and p.exists():
            summary_paths.append(p)

    summary_paths = sorted({p.resolve() for p in summary_paths})
    runs = _collect_runs(summary_paths)
    runs_sorted = sorted(runs, key=lambda r: r["precision_proxy"], reverse=True)

    payload = {
        "run_id": manifest.get("run_id"),
        "generated_at": _utc_ts(),
        "manifest_path": str(manifest_path),
        "summary_files": [str(p) for p in summary_paths],
        "total_runs": len(runs_sorted),
        "runs": runs_sorted,
        "best_by_precision_proxy": runs_sorted[0] if runs_sorted else None,
    }

    out_json = run_dir / "ladder_summary.json"
    out_md = run_dir / "ladder_summary.md"
    _write_json(out_json, payload)
    out_md.write_text(_render_summary_md(payload), encoding="utf-8")

    manifest["ladder_summary_json"] = str(out_json)
    manifest["ladder_summary_md"] = str(out_md)
    manifest["updated_at"] = _utc_ts()
    _write_json(manifest_path, manifest)

    print(json.dumps(payload, indent=2))
    print(f"ladder_summary_json={out_json}")
    print(f"ladder_summary_md={out_md}")
    return payload


def _cmd_start(args: argparse.Namespace) -> None:
    if args.detach and args.mode != "parallel":
        raise SystemExit("--detach requires --mode parallel")

    profiles = _load_profiles(Path(args.profiles))
    run_id = f"ladder_{_utc_ts()}_{_safe_tag(args.tag or 'default')}"
    run_dir = (PROJECT_ROOT / args.output_dir / run_id).resolve()
    logs_dir = run_dir / "logs"
    state_dir = run_dir / "state"
    profile_dir = run_dir / "profiles"
    for p in (logs_dir, state_dir, profile_dir):
        p.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    for profile in profiles:
        per_profile_cfg = profile_dir / f"{profile.name}.json"
        _write_json(
            per_profile_cfg,
            {
                "profiles": [
                    {
                        "name": profile.name,
                        "provider": profile.provider,
                        "model": profile.model,
                    }
                ]
            },
        )
        log_path = logs_dir / f"{profile.name}.log"
        rc_path = state_dir / f"{profile.name}.rc"
        cmd = _build_job_command(
            profile_cfg=per_profile_cfg,
            queue_csv=args.queue_csv,
            output_dir=run_dir,
            n_pdfs=args.n_pdfs,
            max_pages=args.max_pages,
            variants=args.variants,
            vocab_path=args.vocab_path,
        )
        proc = _spawn_job(cmd, log_path=log_path, rc_path=rc_path)
        jobs.append(
            {
                "name": profile.name,
                "provider": profile.provider,
                "model": profile.model,
                "pid": proc.pid,
                "log_path": str(log_path),
                "rc_path": str(rc_path),
                "profile_config_path": str(per_profile_cfg),
                "command": cmd,
            }
        )
        if args.mode == "sequential":
            proc.wait()

    manifest = {
        "run_id": run_id,
        "created_at": _utc_ts(),
        "run_dir": str(run_dir),
        "output_dir": args.output_dir,
        "queue_csv": args.queue_csv,
        "n_pdfs": args.n_pdfs,
        "max_pages": args.max_pages,
        "variants": args.variants,
        "mode": args.mode,
        "detached": bool(args.detach),
        "jobs": jobs,
    }
    manifest_path = run_dir / "ladder_manifest.json"
    _write_json(manifest_path, manifest)
    print(f"manifest={manifest_path}")

    if args.detach:
        print("detached=true")
        print(
            f"status_cmd=python3 scripts/run_llm_table_ladder_agent.py status --manifest {shlex.quote(str(manifest_path))}"
        )
        print(
            f"summarize_cmd=python3 scripts/run_llm_table_ladder_agent.py summarize --manifest {shlex.quote(str(manifest_path))}"
        )
        return

    while True:
        payload = _run_status(manifest_path, as_json=True)
        if payload["all_done"]:
            break
        time.sleep(max(1, int(args.poll_seconds)))
    _run_summarize(manifest_path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Managed high->balanced->low extraction ladder runner.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Start ladder jobs (detached optional).")
    p_start.add_argument("--profiles", default=DEFAULT_PROFILES_PATH)
    p_start.add_argument("--queue-csv", default=DEFAULT_QUEUE_CSV)
    p_start.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    p_start.add_argument("--vocab-path", default="data/vocabulary/variable_vocabulary.json")
    p_start.add_argument("--n-pdfs", type=int, default=5)
    p_start.add_argument("--max-pages", type=int, default=10)
    p_start.add_argument("--variants", default="strict_gate")
    p_start.add_argument("--mode", choices=["parallel", "sequential"], default="parallel")
    p_start.add_argument("--detach", action="store_true")
    p_start.add_argument("--poll-seconds", type=int, default=8)
    p_start.add_argument("--tag", default="")

    p_status = sub.add_parser("status", help="Check ladder job status from manifest.")
    p_status.add_argument("--manifest", required=True)
    p_status.add_argument("--json", action="store_true")

    p_sum = sub.add_parser("summarize", help="Build merged ladder summary from manifest.")
    p_sum.add_argument("--manifest", required=True)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.cmd == "start":
        _cmd_start(args)
        return
    if args.cmd == "status":
        _run_status(Path(args.manifest), as_json=bool(args.json))
        return
    if args.cmd == "summarize":
        _run_summarize(Path(args.manifest))
        return
    raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
