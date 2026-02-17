#!/usr/bin/env python3
"""Generate Sprint 12 task 12.23 dashboard JSON summary."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UTC = timezone.utc
DONE_PATTERN = re.compile(r"^(\d+\.\d+)\s+DONE\s+\[([A-Z0-9_-]+)\]\s+(.+)$")


def _now_iso() -> str:
    return datetime.now(tz=UTC).replace(microsecond=0).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _list_db_candidates(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for pattern in ("*.db", "data/*.db", "db/*.db"):
        candidates.extend(repo_root.glob(pattern))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return sorted(unique)


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return bool(row)


def _count_templates_from_db(db_path: Path) -> dict[str, Any] | None:
    if not db_path.exists():
        return None
    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "templates"):
            return None
        total = conn.execute("SELECT COUNT(*) FROM templates").fetchone()[0]
        by_status = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT COALESCE(dedup_status, 'unknown'), COUNT(*) FROM templates GROUP BY dedup_status"
            ).fetchall()
        }
        by_series = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT COALESCE(series, 'unknown'), COUNT(*) FROM templates GROUP BY series"
            ).fetchall()
        }
        by_generation = {
            str(row[0]): row[1]
            for row in conn.execute(
                "SELECT COALESCE(generation, -1), COUNT(*) FROM templates GROUP BY generation"
            ).fetchall()
        }
        return {
            "source": str(db_path),
            "total_templates": total,
            "by_status": by_status,
            "by_series": by_series,
            "by_generation": by_generation,
        }
    finally:
        conn.close()


def _extract_series(display_id: str) -> str:
    m = re.match(r"^([A-Z]+)", display_id or "")
    return m.group(1) if m else "unknown"


def _count_templates_from_files(repo_root: Path) -> dict[str, Any]:
    templates_dir = repo_root / "data/templates"
    by_status: Counter[str] = Counter()
    by_series: Counter[str] = Counter()
    by_generation: Counter[str] = Counter()
    total = 0
    if not templates_dir.exists():
        return {
            "source": str(templates_dir),
            "total_templates": 0,
            "by_status": {},
            "by_series": {},
            "by_generation": {},
        }

    for path in sorted(templates_dir.glob("*.json")):
        payload = _safe_json(path) or {}
        total += 1
        by_status[str(payload.get("dedup_status", "unknown"))] += 1
        display_id = str(payload.get("display_id", ""))
        by_series[_extract_series(display_id)] += 1
        if display_id.startswith(("L", "MAT", "TP", "SOC", "CREA", "VIEW", "SC", "COL", "VF", "OLF")):
            by_generation["2"] += 1
        else:
            by_generation["1"] += 1
    return {
        "source": str(templates_dir),
        "total_templates": total,
        "by_status": dict(by_status),
        "by_series": dict(by_series),
        "by_generation": dict(by_generation),
    }


def summarize_templates(repo_root: Path, preferred_db: Path | None) -> dict[str, Any]:
    if preferred_db:
        db_summary = _count_templates_from_db(preferred_db)
        if db_summary:
            return db_summary
    for db_path in _list_db_candidates(repo_root):
        db_summary = _count_templates_from_db(db_path)
        if db_summary and db_summary["total_templates"] > 0:
            return db_summary
    return _count_templates_from_files(repo_root)


def _select_web_db(repo_root: Path, preferred_db: Path | None) -> Path | None:
    candidates: list[Path] = []
    if preferred_db:
        candidates.append(preferred_db)
    candidates.extend(_list_db_candidates(repo_root))

    best: tuple[int, Path] | None = None
    seen: set[Path] = set()
    for path in candidates:
        path = path.resolve()
        if path in seen or not path.exists():
            continue
        seen.add(path)
        try:
            conn = sqlite3.connect(path)
            if not _table_exists(conn, "web_metadata"):
                conn.close()
                continue
            count = conn.execute("SELECT COUNT(*) FROM web_metadata").fetchone()[0]
            conn.close()
            if best is None or count > best[0]:
                best = (count, path)
        except Exception:
            continue
    return best[1] if best else None


def summarize_web_of_belief(repo_root: Path, preferred_db: Path | None) -> dict[str, Any]:
    db_path = _select_web_db(repo_root, preferred_db)
    if not db_path:
        return {"available": False, "reason": "no_web_database_found"}

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "web_metadata"):
            return {"available": False, "db_path": str(db_path), "reason": "web_metadata_missing"}

        row = conn.execute(
            """
            SELECT web_id, name, n_beliefs, n_constraints, coherence_score, updated_at
            FROM web_metadata
            WHERE is_master = 1
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            row = conn.execute(
                """
                SELECT web_id, name, n_beliefs, n_constraints, coherence_score, updated_at
                FROM web_metadata
                ORDER BY updated_at DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            return {"available": False, "db_path": str(db_path), "reason": "web_metadata_empty"}

        web_id, name, n_beliefs, n_constraints, coherence, updated_at = row
        n_papers = 0
        n_conflicts = 0
        n_requiring_review = 0
        n_alerts = 0
        if _table_exists(conn, "paper_integrations"):
            n_papers = conn.execute(
                "SELECT COUNT(DISTINCT paper_id) FROM paper_integrations WHERE web_id = ?",
                (web_id,),
            ).fetchone()[0]
        if _table_exists(conn, "belief_merge_log"):
            n_conflicts = conn.execute(
                "SELECT COUNT(*) FROM belief_merge_log WHERE web_id = ? AND merge_type = 'conflict'",
                (web_id,),
            ).fetchone()[0]
            n_requiring_review = conn.execute(
                "SELECT COUNT(*) FROM belief_merge_log WHERE web_id = ? AND requires_review = 1",
                (web_id,),
            ).fetchone()[0]
        if _table_exists(conn, "coherence_alerts"):
            n_alerts = conn.execute(
                "SELECT COUNT(*) FROM coherence_alerts WHERE web_id = ? AND acknowledged = 0",
                (web_id,),
            ).fetchone()[0]

        density = 0.0
        if n_beliefs and n_beliefs > 1:
            density = float(n_constraints or 0) / float(n_beliefs * (n_beliefs - 1))

        return {
            "available": True,
            "db_path": str(db_path),
            "web_id": web_id,
            "name": name,
            "n_beliefs": int(n_beliefs or 0),
            "n_constraints": int(n_constraints or 0),
            "coherence_score": float(coherence or 0.0),
            "constraint_density": density,
            "n_papers_integrated": int(n_papers),
            "n_conflicts": int(n_conflicts),
            "n_requiring_review": int(n_requiring_review),
            "n_unacknowledged_alerts": int(n_alerts),
            "updated_at": updated_at,
        }
    finally:
        conn.close()


def summarize_reconciliation(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "data/reconciliation/staging_theory_links.json"
    payload = _safe_json(path)
    if not payload:
        return {
            "available": False,
            "path": str(path),
            "reason": "missing_or_invalid_json",
        }
    summary = payload.get("summary", {})
    total = int(summary.get("total", 0))
    reconciled = int(summary.get("reconciled", 0))
    unreconciled = int(summary.get("unreconciled", 0))
    rate = (reconciled / total) if total else 0.0
    return {
        "available": True,
        "path": str(path),
        "total_links": total,
        "reconciled_links": reconciled,
        "unreconciled_links": unreconciled,
        "reconciled_rate": rate,
        "theory_counts": summary.get("theory_counts", {}),
    }


def summarize_tier2_reductions(repo_root: Path) -> dict[str, Any]:
    files = sorted((repo_root / "data/reductions").glob("*_reduction.json"))
    theory_summary: dict[str, Any] = {}
    total_constructs = 0
    all_coverages: list[float] = []
    for path in files:
        payload = _safe_json(path) or {}
        theory = str(payload.get("theory", path.stem.replace("_reduction", "")).upper())
        constructs = payload.get("constructs", {}) or {}
        coverages: list[float] = []
        mapping_count = 0
        for construct_data in constructs.values():
            coverage = float(construct_data.get("total_coverage", 0.0) or 0.0)
            coverages.append(coverage)
            mapping_count += len(construct_data.get("template_mappings", []) or [])
        total_constructs += len(constructs)
        all_coverages.extend(coverages)
        theory_summary[theory] = {
            "construct_count": len(constructs),
            "mapping_count": mapping_count,
            "mean_coverage": (sum(coverages) / len(coverages)) if coverages else 0.0,
            "min_coverage": min(coverages) if coverages else 0.0,
            "max_coverage": max(coverages) if coverages else 0.0,
            "source_file": str(path),
        }
    return {
        "source": "data/reductions/*_reduction.json",
        "theories": theory_summary,
        "overall": {
            "total_theories": len(theory_summary),
            "total_constructs": total_constructs,
            "mean_coverage": (sum(all_coverages) / len(all_coverages)) if all_coverages else 0.0,
        },
    }


def _star_to_numeric(text: str) -> float:
    cleaned = text.replace("*", "").strip()
    if not cleaned:
        return 0.0
    return float(cleaned.count("★")) + (0.5 if "½" in cleaned else 0.0)


def summarize_coverage_stars(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "docs/52_Registry_Addendum_V2_2.md"
    if not path.exists():
        return {"available": False, "reason": "registry_addendum_missing", "path": str(path)}

    domains: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| A"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 5:
            continue
        domain_label = parts[1]
        revised_stars = parts[3]
        domain_id = domain_label.split()[0]
        domains[domain_id] = {
            "domain": domain_label,
            "rating_text": revised_stars,
            "rating_numeric": _star_to_numeric(revised_stars),
        }
    numeric_values = [row["rating_numeric"] for row in domains.values()]
    return {
        "available": True,
        "path": str(path),
        "domains": domains,
        "domain_count": len(domains),
        "average_stars_numeric": (sum(numeric_values) / len(numeric_values)) if numeric_values else 0.0,
    }


def summarize_tests(repo_root: Path) -> dict[str, Any]:
    tests_dir = repo_root / "tests"
    py_files = sorted(tests_dir.rglob("test_*.py")) if tests_dir.exists() else []
    ts_files = sorted(tests_dir.rglob("test_*.ts")) if tests_dir.exists() else []
    py_cases = 0
    parse_errors = 0
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            parse_errors += 1
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                py_cases += 1
    return {
        "source": "static_ast_scan",
        "python_test_files": len(py_files),
        "typescript_test_files": len(ts_files),
        "python_test_cases": py_cases,
        "parse_errors": parse_errors,
    }


def parse_done_tasks(repo_root: Path) -> dict[str, Any]:
    done_path = repo_root / "docs/DONE.md"
    task_rows: dict[str, dict[str, str]] = {}
    if not done_path.exists():
        return {"path": str(done_path), "tasks": task_rows}
    for line in done_path.read_text(encoding="utf-8").splitlines():
        m = DONE_PATTERN.match(line.strip())
        if not m:
            continue
        task_id, agent, timestamp = m.groups()
        task_rows[task_id] = {"agent": agent, "timestamp": timestamp}
    return {"path": str(done_path), "tasks": task_rows}


def summarize_pipeline(repo_root: Path, done_tasks: dict[str, Any]) -> dict[str, Any]:
    tasks = done_tasks.get("tasks", {})
    required_task_ids = [
        "12.6",   # quick-assess
        "12.20",  # sensitivity
        "12.22",  # API wrapper
        "13.1",   # update proposals
        "13.3",   # evidence accumulation
        "13.4",   # paper history
        "13.6",   # uncertainty WIS
        "13.8",   # monte carlo sensitivity
        "13.13",  # process-paper pipeline
    ]
    task_completion = {task_id: (task_id in tasks) for task_id in required_task_ids}
    modules = {
        "building_eval": (repo_root / "src/cmr/building_eval.py").exists(),
        "paper_eval": (repo_root / "src/cmr/paper_eval.py").exists(),
        "quick_assess": (repo_root / "src/cmr/quick_assess.py").exists(),
        "compare": (repo_root / "src/cmr/compare.py").exists(),
        "sensitivity": (repo_root / "src/cmr/sensitivity.py").exists(),
        "api_wrapper": (repo_root / "src/cmr/api.py").exists(),
        "process_paper": (repo_root / "src/cmr/process_paper.py").exists(),
        "tier2_reductions_art": (repo_root / "data/reductions/art_reduction.json").exists(),
        "tier2_reductions_srt": (repo_root / "data/reductions/srt_reduction.json").exists(),
        "tier2_reductions_biophilia": (repo_root / "data/reductions/biophilia_reduction.json").exists(),
        "staging_reconciliation_output": (repo_root / "data/reconciliation/staging_theory_links.json").exists(),
    }
    pipeline_ready = all(modules.values()) and all(task_completion.values())
    return {
        "required_task_completion": task_completion,
        "module_checks": modules,
        "pipeline_ready": pipeline_ready,
    }


def generate_dashboard(repo_root: Path, output_path: Path, db_path: Path | None) -> dict[str, Any]:
    done_tasks = parse_done_tasks(repo_root)
    payload = {
        "generated_at": _now_iso(),
        "repo_root": str(repo_root),
        "template_counts_by_status": summarize_templates(repo_root, db_path),
        "web_of_belief_stats": summarize_web_of_belief(repo_root, db_path),
        "theory_link_reconciliation": summarize_reconciliation(repo_root),
        "tier2_reduction_coverage": summarize_tier2_reductions(repo_root),
        "coverage_stars": summarize_coverage_stars(repo_root),
        "test_counts": summarize_tests(repo_root),
        "pipeline_status": summarize_pipeline(repo_root, done_tasks),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate project dashboard summary JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/review/project_dashboard.json"),
        help="Output path for dashboard JSON.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("ae.db"),
        help="Preferred SQLite database path for template/web stats.",
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    output_path = args.output if args.output.is_absolute() else repo_root / args.output
    db_path = args.db_path if args.db_path.is_absolute() else repo_root / args.db_path
    payload = generate_dashboard(repo_root, output_path, db_path)
    print(f"Dashboard JSON written: {output_path}")
    print(
        "Snapshot:",
        json.dumps(
            {
                "generated_at": payload["generated_at"],
                "templates_total": payload["template_counts_by_status"].get("total_templates"),
                "reconciliation_rate": payload["theory_link_reconciliation"].get("reconciled_rate"),
                "pipeline_ready": payload["pipeline_status"].get("pipeline_ready"),
            },
            indent=2,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

