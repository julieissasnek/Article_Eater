#!/usr/bin/env python3
"""Compute AESHI (Article Eater System Health Index) for AE/AF/BN/Web stack."""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_web_bn_health import (  # noqa: E402
    collect_bn_metrics,
    collect_web_metrics,
    evaluate_checks,
)
from scripts.probe_web_of_belief_health import run_probe  # noqa: E402
from src.services.finding_template_relevance import (  # noqa: E402
    FindingRecord,
    _infer_finding_domains,
    load_template_profiles,
)
from src.services.db_locator import candidate_web_dbs, resolve_web_db as resolve_web_db_by_policy  # noqa: E402

MASTER_WEB_ID = "master:web:accumulated"
DEFAULT_BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"
DEFAULT_LINKS_JSON = PROJECT_ROOT / "data" / "production" / "finding_template_theory_links.json"
DEFAULT_TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
DEFAULT_THRESHOLDS = PROJECT_ROOT / "config" / "web_bn_health_thresholds.json"
DEFAULT_BASELINE_JSON = PROJECT_ROOT / "data" / "production" / "web_health_stress_baseline.json"
DEFAULT_JSON_OUT = PROJECT_ROOT / "data" / "production" / "system_health_report.json"
DEFAULT_MD_OUT = PROJECT_ROOT / "docs" / "system_health_report.md"


@dataclass
class GateResult:
    name: str
    ok: bool
    duration_seconds: float
    exit_code: int
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web-db", type=Path, default=None, help="Web DB path (auto-detect if omitted)")
    parser.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    parser.add_argument(
        "--finding-web-db",
        type=Path,
        default=None,
        help="DB path used for finding annotation/CCI checks (auto-select if omitted)",
    )
    parser.add_argument("--bn-json", type=Path, default=DEFAULT_BN_JSON, help="BN JSON path")
    parser.add_argument("--links-json", type=Path, default=DEFAULT_LINKS_JSON, help="Finding links artifact path")
    parser.add_argument("--templates-dir", type=Path, default=DEFAULT_TEMPLATES_DIR, help="Template directory path")
    parser.add_argument("--thresholds", type=Path, default=DEFAULT_THRESHOLDS, help="Web/BN threshold JSON")
    parser.add_argument(
        "--annotation-key",
        type=str,
        default="template_relevance_v1",
        help="epistemic_v2 annotation key to verify",
    )
    parser.add_argument(
        "--probe-iterations",
        type=int,
        default=500,
        help="Iterations for WebOfBelief invariant probe",
    )
    parser.add_argument("--probe-seed", type=int, default=1337, help="Seed for WebOfBelief invariant probe")
    parser.add_argument(
        "--min-unique-tier1",
        type=int,
        default=10,
        help="Minimum unique tier1 theories for finding contract gate",
    )
    parser.add_argument(
        "--min-tier2-coverage",
        type=float,
        default=0.90,
        help="Minimum tier2 coverage ratio for finding contract gate",
    )
    parser.add_argument(
        "--max-non-music-music-top",
        type=int,
        default=0,
        help="Max non-music findings with MUSIC_COGNITION top template",
    )
    parser.add_argument(
        "--min-persisted-ratio",
        type=float,
        default=1.0,
        help="Minimum annotation persistence ratio",
    )
    parser.add_argument("--stress-baseline-json", type=Path, default=DEFAULT_BASELINE_JSON)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT, help="JSON report output path")
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD_OUT, help="Markdown report output path")
    parser.add_argument("--skip-gates", action="store_true", help="Skip runtime gate scripts/probes")
    parser.add_argument("--print-json", action="store_true", help="Print JSON report to stdout")
    return parser.parse_args()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def linear_high(actual: float, floor: float, target: float) -> float:
    if target <= floor:
        return 1.0 if actual >= target else 0.0
    return clamp01((actual - floor) / (target - floor))


def linear_low(actual: float, best: float, worst: float) -> float:
    if worst <= best:
        return 1.0 if actual <= best else 0.0
    return clamp01((worst - actual) / (worst - best))


def resolve_web_db(explicit: Path | None, prefer: str) -> Path:
    return resolve_web_db_by_policy(explicit, prefer=prefer)


def _load_links_belief_ids(links_json: Path) -> set[str]:
    links = load_json(links_json)
    return {str(item.get("belief_id") or "") for item in links.get("resolutions", []) if item.get("belief_id")}


def resolve_finding_web_db(
    explicit: Path | None,
    primary_web_db: Path,
    links_json: Path,
    annotation_key: str,
) -> tuple[Path, dict[str, Any]]:
    if explicit is not None:
        if not explicit.exists():
            raise FileNotFoundError(f"Finding web DB not found: {explicit}")
        return explicit, {"mode": "explicit"}

    link_belief_ids = _load_links_belief_ids(links_json)
    candidates: list[Path] = []
    for path in (primary_web_db, *candidate_web_dbs()):
        if path.exists() and path not in candidates:
            candidates.append(path)

    scored: list[tuple[int, int, int, Path]] = []
    for candidate in candidates:
        belief_ids, annotated = belief_annotation_map(candidate, annotation_key)
        belief_match = len(link_belief_ids.intersection(belief_ids))
        anno_match = len(link_belief_ids.intersection(set(annotated.keys())))
        scored.append((anno_match, belief_match, len(belief_ids), candidate))

    if not scored:
        raise FileNotFoundError("No available candidate DB for finding contracts")

    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    best = scored[0]
    diag = {
        "mode": "auto",
        "selection_basis": "max(annotation_match, belief_match, belief_count)",
        "candidates": [
            {
                "path": str(path),
                "annotation_match": anno,
                "belief_match": bel,
                "belief_count": count,
            }
            for anno, bel, count, path in scored
        ],
    }
    return best[3], diag


def run_script_gate(name: str, script_relative: str) -> GateResult:
    start = time.perf_counter()
    cmd = [sys.executable, str(PROJECT_ROOT / script_relative)]
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    elapsed = time.perf_counter() - start
    detail = proc.stdout.strip()
    return GateResult(
        name=name,
        ok=(proc.returncode == 0),
        duration_seconds=elapsed,
        exit_code=int(proc.returncode),
        detail=detail,
    )


def run_web_probe_gate(iterations: int, seed: int) -> tuple[GateResult, dict[str, Any]]:
    start = time.perf_counter()
    try:
        counters = run_probe(iterations=iterations, seed=seed)
        elapsed = time.perf_counter() - start
        gate = GateResult(
            name="web_of_belief_invariants",
            ok=True,
            duration_seconds=elapsed,
            exit_code=0,
            detail=f"run_probe passed with counters={json.dumps(counters, sort_keys=True)}",
        )
        return gate, counters
    except Exception as exc:  # pragma: no cover - defensive
        elapsed = time.perf_counter() - start
        gate = GateResult(
            name="web_of_belief_invariants",
            ok=False,
            duration_seconds=elapsed,
            exit_code=1,
            detail=f"run_probe failed: {exc}",
        )
        return gate, {}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def belief_annotation_map(web_db: Path, annotation_key: str) -> tuple[set[str], dict[str, dict[str, Any]]]:
    conn = sqlite3.connect(str(web_db))
    try:
        cur = conn.cursor()
        # Works for v2 DBs (no web_id) and legacy DBs (with web_id).
        cols = {row[1] for row in cur.execute("PRAGMA table_info(beliefs)").fetchall()}
        if "web_id" in cols:
            rows = cur.execute(
                "SELECT belief_id, epistemic_v2 FROM beliefs WHERE web_id = ?",
                (MASTER_WEB_ID,),
            ).fetchall()
        else:
            rows = cur.execute("SELECT belief_id, epistemic_v2 FROM beliefs").fetchall()
    finally:
        conn.close()

    belief_ids: set[str] = set()
    annotated: dict[str, dict[str, Any]] = {}
    for belief_id, raw in rows:
        belief_id = str(belief_id)
        belief_ids.add(belief_id)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        annotation = payload.get(annotation_key)
        if isinstance(annotation, dict):
            annotated[belief_id] = annotation
    return belief_ids, annotated


def count_non_music_music_top(
    resolutions: list[dict[str, Any]],
    templates_dir: Path,
) -> int:
    templates = {t.display_id: t for t in load_template_profiles(templates_dir)}
    mismatches = 0
    for resolution in resolutions:
        top_templates = resolution.get("top_templates") or []
        if not top_templates:
            continue
        top = top_templates[0]
        display_id = str(top.get("display_id") or "")
        profile = templates.get(display_id)
        if profile is None:
            continue
        frameworks = {str(item).strip().upper() for item in profile.frameworks}
        if "MUSIC_COGNITION" not in frameworks:
            continue
        finding = FindingRecord(
            belief_id=str(resolution.get("belief_id") or ""),
            content="",
            environment_id=str(resolution.get("environment_id") or ""),
            outcome_id=str(resolution.get("outcome_id") or ""),
        )
        domains = _infer_finding_domains(finding)
        if "music" not in domains:
            mismatches += 1
    return mismatches


def bn_touch(node_set: set[str], environment_id: str, outcome_id: str, belief_id: str) -> bool:
    candidates = set()
    if belief_id:
        candidates.add(belief_id)
    if environment_id:
        candidates.add(f"env.{environment_id}")
        candidates.add(f"env.unresolved.{environment_id}")
    if outcome_id:
        candidates.add(f"out.{outcome_id}")
        candidates.add(f"out.unresolved.{outcome_id}")
    return any(candidate in node_set for candidate in candidates)


def compute_chain_completeness(
    resolutions: list[dict[str, Any]],
    belief_ids: set[str],
    annotations: dict[str, dict[str, Any]],
    bn_nodes: set[str],
) -> dict[str, Any]:
    totals = {
        "findings_total": len(resolutions),
        "has_belief_id": 0,
        "belief_exists": 0,
        "has_annotation": 0,
        "has_tier1": 0,
        "has_tier2": 0,
        "has_templates": 0,
        "bn_touched": 0,
        "complete_chain": 0,
    }
    for item in resolutions:
        belief_id = str(item.get("belief_id") or "")
        environment_id = str(item.get("environment_id") or "")
        outcome_id = str(item.get("outcome_id") or "")
        has_belief = bool(belief_id)
        exists = has_belief and belief_id in belief_ids
        has_annotation = exists and belief_id in annotations
        has_tier1 = bool(item.get("tier1_relevance"))
        has_tier2 = bool(item.get("tier2_relevance"))
        has_templates = bool(item.get("top_templates"))
        touched = bn_touch(bn_nodes, environment_id, outcome_id, belief_id)
        complete = all([has_belief, exists, has_annotation, has_tier1, has_tier2, has_templates, touched])

        if has_belief:
            totals["has_belief_id"] += 1
        if exists:
            totals["belief_exists"] += 1
        if has_annotation:
            totals["has_annotation"] += 1
        if has_tier1:
            totals["has_tier1"] += 1
        if has_tier2:
            totals["has_tier2"] += 1
        if has_templates:
            totals["has_templates"] += 1
        if touched:
            totals["bn_touched"] += 1
        if complete:
            totals["complete_chain"] += 1

    total = totals["findings_total"]
    ratios = {f"{k}_ratio": (v / total if total else 0.0) for k, v in totals.items() if k != "findings_total"}
    return {"counts": totals, "ratios": ratios}


def compute_finding_contract(
    links_json: Path,
    templates_dir: Path,
    web_db: Path,
    annotation_key: str,
    min_unique_tier1: int,
    min_tier2_coverage: float,
    max_non_music_music_top: int,
    min_persisted_ratio: float,
) -> tuple[dict[str, Any], GateResult]:
    links = load_json(links_json)
    resolutions = links.get("resolutions", [])
    findings_total = len(resolutions)
    findings_with_tier2 = sum(1 for r in resolutions if r.get("tier2_relevance"))
    tier2_coverage = (findings_with_tier2 / findings_total) if findings_total else 0.0
    unique_tier1 = {
        key
        for resolution in resolutions
        for key in (resolution.get("tier1_relevance") or {}).keys()
    }
    non_music_music_top = count_non_music_music_top(resolutions, templates_dir)
    belief_ids, annotated = belief_annotation_map(web_db, annotation_key)
    persisted = len(annotated)
    total_beliefs = len(belief_ids)
    persisted_ratio = (persisted / total_beliefs) if total_beliefs else 0.0

    failures: list[str] = []
    if len(unique_tier1) < min_unique_tier1:
        failures.append(f"unique_tier1 {len(unique_tier1)} < {min_unique_tier1}")
    if tier2_coverage < min_tier2_coverage:
        failures.append(f"tier2_coverage {tier2_coverage:.3f} < {min_tier2_coverage:.3f}")
    if non_music_music_top > max_non_music_music_top:
        failures.append(f"non_music_music_top {non_music_music_top} > {max_non_music_music_top}")
    if persisted_ratio < min_persisted_ratio:
        failures.append(f"persisted_ratio {persisted_ratio:.3f} < {min_persisted_ratio:.3f}")

    metrics = {
        "findings_total": findings_total,
        "findings_with_tier2": findings_with_tier2,
        "tier2_coverage": tier2_coverage,
        "unique_tier1_count": len(unique_tier1),
        "non_music_music_top_count": non_music_music_top,
        "beliefs_total": total_beliefs,
        "beliefs_with_annotation": persisted,
        "persisted_ratio": persisted_ratio,
        "unique_tier1_values": sorted(unique_tier1),
    }

    gate = GateResult(
        name="finding_template_contracts",
        ok=(len(failures) == 0),
        duration_seconds=0.0,
        exit_code=0 if not failures else 1,
        detail="; ".join(failures) if failures else "all finding-template contracts passed",
    )
    return metrics, gate


def compute_template_grounding(resolutions: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    findings_with_templates = 0
    for resolution in resolutions:
        top_templates = resolution.get("top_templates") or []
        if not top_templates:
            continue
        findings_with_templates += 1
        seen_this_finding: set[str] = set()
        for item in top_templates:
            key = str(item.get("display_id") or item.get("template_id") or "").strip()
            if not key or key in seen_this_finding:
                continue
            counts[key] += 1
            seen_this_finding.add(key)
    active_templates = len(counts)
    adequately_grounded = sum(1 for _, n in counts.items() if n >= 3)
    weakly_grounded = sum(1 for _, n in counts.items() if 1 <= n < 3)
    adequate_ratio = (adequately_grounded / active_templates) if active_templates else 0.0
    return {
        "active_templates": active_templates,
        "adequately_grounded_templates": adequately_grounded,
        "weakly_grounded_templates": weakly_grounded,
        "adequate_ratio": adequate_ratio,
        "findings_with_templates": findings_with_templates,
    }


def parse_calibration_count(smoke_output: str) -> int:
    for line in smoke_output.splitlines():
        marker = "calibration files:"
        if marker in line:
            value = line.split(marker, 1)[1].strip()
            try:
                return int(value)
            except ValueError:
                return 0
    return 0


def parse_baseline_runtime(baseline_json: Path) -> tuple[float | None, int | None]:
    if not baseline_json.exists():
        return None, None
    try:
        payload = load_json(baseline_json)
    except Exception:
        return None, None
    agg = payload.get("aggregate") or {}
    mean_elapsed = agg.get("mean_elapsed_seconds")
    iterations = payload.get("iterations")
    try:
        return float(mean_elapsed), int(iterations)
    except Exception:
        return None, None


def compute_scores(
    web_bn_report: dict[str, Any],
    finding_metrics: dict[str, Any],
    chain: dict[str, Any],
    template_grounding: dict[str, Any],
    gates: dict[str, GateResult],
    probe_runtime_seconds: float | None,
    probe_iterations: int,
    baseline_mean_seconds: float | None,
    baseline_iterations: int | None,
) -> dict[str, Any]:
    minimum = web_bn_report["minimum_viable"]
    target = web_bn_report["target"]
    web = web_bn_report["metrics"]["web"]
    bn = web_bn_report["metrics"]["bn"]
    cci = chain["ratios"]["complete_chain_ratio"]

    minimum_ratio = (minimum["passed"] / len(minimum["results"])) if minimum["results"] else 1.0
    target_ratio = (target["passed"] / len(target["results"])) if target["results"] else 1.0

    contract = 100.0 * (
        0.35 * minimum_ratio
        + 0.20 * target_ratio
        + 0.25 * finding_metrics["persisted_ratio"]
        + 0.10 * (1.0 if bn["dangling_edges"] == 0 else 0.0)
        + 0.10 * (1.0 if bn["has_cycle"] == 0 else 0.0)
    )

    v1_ok = 1.0 if gates["offline_pipeline_smoke"].ok else 0.0
    v2_ok = 1.0 if gates["offline_pipeline_v2_smoke"].ok else 0.0
    calibration_count = parse_calibration_count(gates["offline_pipeline_smoke"].detail)
    calibration_score = clamp01(float(calibration_count))
    pipeline = 100.0 * (
        0.20 * v1_ok
        + 0.20 * v2_ok
        + 0.45 * cci
        + 0.15 * calibration_score
    )

    web_bn = 100.0 * (
        0.18 * linear_low(float(web["isolated_pct"]), best=5.0, worst=25.0)
        + 0.12 * linear_high(float(web["bridge_with_source_pct"]), floor=80.0, target=95.0)
        + 0.10 * linear_high(float(web["contradicts_share_pct"]), floor=1.0, target=3.0)
        + 0.20 * linear_high(float(bn["largest_component_pct"]), floor=50.0, target=85.0)
        + 0.20 * linear_low(float(bn["unresolved_pct"]), best=20.0, worst=95.0)
        + 0.10 * linear_high(float(bn["edges"]), floor=1000.0, target=5000.0)
        + 0.10 * linear_high(float(web["constraints"]), floor=8000.0, target=20000.0)
    )

    theory = 100.0 * (
        0.32 * linear_high(float(finding_metrics["tier2_coverage"]), floor=0.90, target=0.98)
        + 0.28
        * linear_high(
            float(finding_metrics["unique_tier1_count"]),
            floor=10.0,
            target=25.0,
        )
        + 0.20
        * linear_low(
            float(finding_metrics["non_music_music_top_count"]),
            best=0.0,
            worst=5.0,
        )
        + 0.20 * linear_high(float(template_grounding["adequate_ratio"]), floor=0.60, target=0.85)
    )

    hard_gate_pass_rate = (
        sum(1 for gate in gates.values() if gate.ok) / len(gates) if gates else 0.0
    )
    sanity_ok = 1.0 if gates["sanity_check"].ok else 0.0
    probe_ok = 1.0 if gates["web_of_belief_invariants"].ok else 0.0

    runtime_score = 0.5
    runtime_ratio = None
    if (
        probe_runtime_seconds is not None
        and baseline_mean_seconds is not None
        and baseline_iterations is not None
        and baseline_iterations > 0
    ):
        expected = baseline_mean_seconds * (probe_iterations / float(baseline_iterations))
        if expected > 0:
            runtime_ratio = probe_runtime_seconds / expected
            runtime_score = linear_low(runtime_ratio, best=1.2, worst=2.0)

    stability = 100.0 * (
        0.35 * hard_gate_pass_rate
        + 0.25 * probe_ok
        + 0.20 * sanity_ok
        + 0.20 * runtime_score
    )

    weighted = (
        0.25 * contract
        + 0.20 * pipeline
        + 0.25 * web_bn
        + 0.20 * theory
        + 0.10 * stability
    )

    hard_gates_ok = all(gate.ok for gate in gates.values()) if gates else True
    if not hard_gates_ok:
        weighted = min(weighted, 49.0)
    score = round(weighted, 2)

    if hard_gates_ok and score >= 85.0:
        band = "GREEN"
    elif hard_gates_ok and score >= 70.0:
        band = "YELLOW"
    else:
        band = "RED"

    overall_ok = hard_gates_ok and score >= 70.0
    return {
        "overall_score": score,
        "band": band,
        "overall_ok": overall_ok,
        "hard_gates_ok": hard_gates_ok,
        "subscores": {
            "contract": round(contract, 2),
            "pipeline": round(pipeline, 2),
            "web_bn": round(web_bn, 2),
            "theory": round(theory, 2),
            "stability": round(stability, 2),
        },
        "inputs": {
            "minimum_ratio": round(minimum_ratio, 4),
            "target_ratio": round(target_ratio, 4),
            "cci_ratio": round(cci, 4),
            "hard_gate_pass_rate": round(hard_gate_pass_rate, 4),
            "runtime_ratio_to_baseline": None if runtime_ratio is None else round(runtime_ratio, 4),
        },
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AESHI System Health Report",
        "",
        f"- Generated (UTC): {report['generated_at_utc']}",
        f"- Overall score: **{report['score']['overall_score']}**",
        f"- Band: **{report['score']['band']}**",
        f"- Overall status: **{'PASS' if report['score']['overall_ok'] else 'FAIL'}**",
        "",
        "## Hard Gates",
        "",
        "| Gate | Status | Time (s) | Detail |",
        "|---|---|---:|---|",
    ]
    for gate in report["gates"].values():
        detail = gate["detail"].replace("\n", " ").strip()
        if len(detail) > 120:
            detail = detail[:117] + "..."
        lines.append(
            f"| {gate['name']} | {'PASS' if gate['ok'] else 'FAIL'} | {gate['duration_seconds']:.3f} | {detail} |"
        )

    lines.extend(
        [
            "",
            "## Subscores",
            "",
            "| Area | Score |",
            "|---|---:|",
        ]
    )
    for key, value in report["score"]["subscores"].items():
        lines.append(f"| {key} | {value:.2f} |")

    lines.extend(
        [
            "",
            "## Key Metrics",
            "",
            f"- findings_total: {report['finding_metrics']['findings_total']}",
            f"- tier2_coverage: {report['finding_metrics']['tier2_coverage']:.4f}",
            f"- unique_tier1_count: {report['finding_metrics']['unique_tier1_count']}",
            f"- CCI complete_chain_ratio: {report['chain_completeness']['ratios']['complete_chain_ratio']:.4f}",
            f"- web isolated_pct: {report['web_bn_report']['metrics']['web']['isolated_pct']:.3f}",
            f"- bn unresolved_pct: {report['web_bn_report']['metrics']['bn']['unresolved_pct']:.3f}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_web_bn_report(web_db: Path, bn_json: Path, thresholds_path: Path) -> tuple[dict[str, Any], GateResult]:
    web_metrics = collect_web_metrics(web_db)
    bn_metrics = collect_bn_metrics(bn_json)
    thresholds = load_json(thresholds_path)
    metrics = {"web": web_metrics, "bn": bn_metrics}
    minimum = evaluate_checks(metrics, thresholds.get("minimum_viable", []))
    target = evaluate_checks(metrics, thresholds.get("target", []))
    gate = GateResult(
        name="web_bn_minimum_viable",
        ok=bool(minimum.get("ok")),
        duration_seconds=0.0,
        exit_code=0 if minimum.get("ok") else 1,
        detail=f"minimum_viable passed={minimum.get('passed')} failed={minimum.get('failed')}",
    )
    report = {"metrics": metrics, "minimum_viable": minimum, "target": target}
    return report, gate


def main() -> int:
    args = parse_args()
    web_db = resolve_web_db(args.web_db, args.web_db_prefer)
    finding_web_db, finding_db_selection = resolve_finding_web_db(
        explicit=args.finding_web_db,
        primary_web_db=web_db,
        links_json=args.links_json,
        annotation_key=args.annotation_key,
    )
    if not args.bn_json.exists():
        raise FileNotFoundError(f"BN JSON not found: {args.bn_json}")
    if not args.links_json.exists():
        raise FileNotFoundError(f"Links JSON not found: {args.links_json}")
    if not args.templates_dir.exists():
        raise FileNotFoundError(f"Templates directory not found: {args.templates_dir}")
    if not args.thresholds.exists():
        raise FileNotFoundError(f"Threshold config not found: {args.thresholds}")

    gates: dict[str, GateResult] = {}
    probe_counters: dict[str, Any] = {}

    if args.skip_gates:
        gates["sanity_check"] = GateResult("sanity_check", True, 0.0, 0, "skipped")
        gates["offline_pipeline_smoke"] = GateResult("offline_pipeline_smoke", True, 0.0, 0, "skipped")
        gates["offline_pipeline_v2_smoke"] = GateResult(
            "offline_pipeline_v2_smoke",
            True,
            0.0,
            0,
            "skipped",
        )
        gates["web_of_belief_invariants"] = GateResult(
            "web_of_belief_invariants",
            True,
            0.0,
            0,
            "skipped",
        )
    else:
        gates["sanity_check"] = run_script_gate("sanity_check", "scripts/sanity_check.py")
        gates["offline_pipeline_smoke"] = run_script_gate(
            "offline_pipeline_smoke",
            "scripts/offline_pipeline_smoke.py",
        )
        gates["offline_pipeline_v2_smoke"] = run_script_gate(
            "offline_pipeline_v2_smoke",
            "scripts/offline_pipeline_v2_smoke.py",
        )
        probe_gate, probe_counters = run_web_probe_gate(args.probe_iterations, args.probe_seed)
        gates["web_of_belief_invariants"] = probe_gate

    web_bn_report, web_bn_gate = build_web_bn_report(web_db, args.bn_json, args.thresholds)
    gates[web_bn_gate.name] = web_bn_gate

    finding_metrics, finding_gate = compute_finding_contract(
        links_json=args.links_json,
        templates_dir=args.templates_dir,
        web_db=finding_web_db,
        annotation_key=args.annotation_key,
        min_unique_tier1=args.min_unique_tier1,
        min_tier2_coverage=args.min_tier2_coverage,
        max_non_music_music_top=args.max_non_music_music_top,
        min_persisted_ratio=args.min_persisted_ratio,
    )
    gates[finding_gate.name] = finding_gate

    links_payload = load_json(args.links_json)
    resolutions = links_payload.get("resolutions", [])
    bn_payload = load_json(args.bn_json)
    bn_nodes = {str(item) for item in bn_payload.get("nodes", []) if item is not None}
    belief_ids, annotations = belief_annotation_map(finding_web_db, args.annotation_key)
    chain = compute_chain_completeness(resolutions, belief_ids, annotations, bn_nodes)
    template_grounding = compute_template_grounding(resolutions)

    baseline_mean, baseline_iterations = parse_baseline_runtime(args.stress_baseline_json)
    probe_runtime = (
        gates["web_of_belief_invariants"].duration_seconds
        if not args.skip_gates
        else None
    )
    score = compute_scores(
        web_bn_report=web_bn_report,
        finding_metrics=finding_metrics,
        chain=chain,
        template_grounding=template_grounding,
        gates=gates,
        probe_runtime_seconds=probe_runtime,
        probe_iterations=args.probe_iterations,
        baseline_mean_seconds=baseline_mean,
        baseline_iterations=baseline_iterations,
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "paths": {
            "web_db": str(web_db),
            "finding_web_db": str(finding_web_db),
            "bn_json": str(args.bn_json),
            "links_json": str(args.links_json),
            "templates_dir": str(args.templates_dir),
            "thresholds": str(args.thresholds),
            "stress_baseline_json": str(args.stress_baseline_json),
        },
        "finding_db_selection": finding_db_selection,
        "gates": {name: asdict(result) for name, result in gates.items()},
        "score": score,
        "web_bn_report": web_bn_report,
        "finding_metrics": finding_metrics,
        "chain_completeness": chain,
        "template_grounding": template_grounding,
        "web_probe_counters": probe_counters,
    }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    args.markdown_out.write_text(build_markdown(report), encoding="utf-8")

    summary = (
        f"AESHI score={report['score']['overall_score']} band={report['score']['band']} "
        f"status={'PASS' if report['score']['overall_ok'] else 'FAIL'} "
        f"hard_gates={'PASS' if report['score']['hard_gates_ok'] else 'FAIL'}"
    )
    print(summary)
    print(f"JSON report: {args.json_out}")
    print(f"Markdown report: {args.markdown_out}")
    if args.print_json:
        print(json.dumps(report, indent=2))

    return 0 if report["score"]["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
