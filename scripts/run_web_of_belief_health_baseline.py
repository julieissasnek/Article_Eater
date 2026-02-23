#!/usr/bin/env python3
"""Run and persist a deterministic WebOfBelief health baseline."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.probe_web_of_belief_health import run_probe


def parse_seeds(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def build_markdown(data: dict) -> str:
    lines = [
        "# WebOfBelief Stress Baseline",
        "",
        f"- Generated (UTC): {data['generated_at_utc']}",
        f"- Iterations per seed: {data['iterations']}",
        f"- Seeds: {', '.join(str(seed) for seed in data['seeds'])}",
        "",
        "## Runs",
        "",
        "| Seed | Elapsed (s) | Beliefs | Constraints | add_belief | add_constraint | add_evidence | seek_equilibrium |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for run in data["runs"]:
        lines.append(
            "| {seed} | {elapsed:.3f} | {beliefs} | {constraints} | {add_belief} | {add_constraint} | {add_evidence} | {seek_equilibrium} |".format(
                seed=run["seed"],
                elapsed=run["elapsed_seconds"],
                beliefs=run["counters"]["beliefs"],
                constraints=run["counters"]["constraints"],
                add_belief=run["counters"]["add_belief"],
                add_constraint=run["counters"]["add_constraint"],
                add_evidence=run["counters"]["add_evidence"],
                seek_equilibrium=run["counters"]["seek_equilibrium"],
            )
        )

    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- mean elapsed: {data['aggregate']['mean_elapsed_seconds']:.3f}s",
            f"- min elapsed: {data['aggregate']['min_elapsed_seconds']:.3f}s",
            f"- max elapsed: {data['aggregate']['max_elapsed_seconds']:.3f}s",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic WebOfBelief stress baseline.")
    parser.add_argument("--iterations", type=int, default=5000, help="Operations per seed.")
    parser.add_argument(
        "--seeds",
        type=str,
        default="1337,2026,4242",
        help="Comma-separated seeds.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=Path("docs/web_health_stress_baseline.md"),
        help="Markdown output path.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("data/production/web_health_stress_baseline.json"),
        help="JSON output path.",
    )
    args = parser.parse_args()

    seeds = parse_seeds(args.seeds)
    runs = []

    for seed in seeds:
        start = time.perf_counter()
        counters = run_probe(iterations=args.iterations, seed=seed)
        elapsed = time.perf_counter() - start
        runs.append(
            {
                "seed": seed,
                "elapsed_seconds": elapsed,
                "counters": counters,
            }
        )

    elapsed_values = [run["elapsed_seconds"] for run in runs]
    data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "iterations": args.iterations,
        "seeds": seeds,
        "runs": runs,
        "aggregate": {
            "mean_elapsed_seconds": sum(elapsed_values) / len(elapsed_values),
            "min_elapsed_seconds": min(elapsed_values),
            "max_elapsed_seconds": max(elapsed_values),
        },
    }

    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(build_markdown(data), encoding="utf-8")
    args.json_out.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Wrote markdown baseline: {args.markdown_out}")
    print(f"Wrote json baseline: {args.json_out}")
    print(
        "elapsed_seconds mean={:.3f} min={:.3f} max={:.3f}".format(
            data["aggregate"]["mean_elapsed_seconds"],
            data["aggregate"]["min_elapsed_seconds"],
            data["aggregate"]["max_elapsed_seconds"],
        )
    )


if __name__ == "__main__":
    main()
