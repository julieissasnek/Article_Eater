#!/usr/bin/env python3
"""Health probes for finding-template relevance output and persistence contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.services.finding_template_relevance import (  # noqa: E402
    FindingRecord,
    _infer_finding_domains,
    load_template_profiles,
)
from src.services.db_locator import get_web_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--links-json",
        type=Path,
        default=Path("data/production/finding_template_theory_links.json"),
        help="Path to relevance resolution JSON artifact",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path("data/templates"),
        help="Template JSON directory",
    )
    parser.add_argument(
        "--web-db",
        type=Path,
        default=get_web_db(),
        help="Web DB path for persistence checks",
    )
    parser.add_argument(
        "--annotation-key",
        type=str,
        default="template_relevance_v1",
        help="epistemic_v2 key expected for persisted relevance payload",
    )
    parser.add_argument(
        "--max-non-music-music-top",
        type=int,
        default=0,
        help="Maximum allowed non-music findings whose top template uses MUSIC_COGNITION",
    )
    parser.add_argument(
        "--min-unique-tier1",
        type=int,
        default=10,
        help="Minimum required number of unique tier1 theories linked",
    )
    parser.add_argument(
        "--min-tier2-coverage",
        type=float,
        default=0.9,
        help="Minimum required ratio of findings with non-empty tier2 relevance",
    )
    parser.add_argument(
        "--min-persisted-ratio",
        type=float,
        default=1.0,
        help="Minimum required ratio of beliefs with persisted annotation",
    )
    return parser.parse_args()


def _persistence_ratio(db_path: Path, annotation_key: str) -> tuple[int, int, float]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        rows = cur.execute("SELECT epistemic_v2 FROM beliefs").fetchall()
    finally:
        conn.close()

    total = len(rows)
    with_key = 0
    for (raw,) in rows:
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue
        if annotation_key in payload:
            with_key += 1

    ratio = (with_key / total) if total else 0.0
    return with_key, total, ratio


def main() -> int:
    args = parse_args()

    links = json.loads(args.links_json.read_text(encoding="utf-8"))
    resolutions = links.get("resolutions", [])
    templates = {t.display_id: t for t in load_template_profiles(args.templates_dir)}

    findings_total = len(resolutions)
    findings_with_tier2 = sum(1 for r in resolutions if r.get("tier2_relevance"))
    tier2_coverage = (findings_with_tier2 / findings_total) if findings_total else 0.0

    unique_tier1 = {
        key
        for resolution in resolutions
        for key in (resolution.get("tier1_relevance") or {}).keys()
    }

    non_music_music_top = 0
    for resolution in resolutions:
        top_templates = resolution.get("top_templates") or []
        if not top_templates:
            continue
        top = top_templates[0]
        profile = templates.get(str(top.get("display_id") or ""))
        if not profile:
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
        finding_domains = _infer_finding_domains(finding)
        if "music" not in finding_domains:
            non_music_music_top += 1

    persisted_with_key, beliefs_total, persisted_ratio = _persistence_ratio(args.web_db, args.annotation_key)

    print(f"findings_total: {findings_total}")
    print(f"findings_with_tier2: {findings_with_tier2} ({tier2_coverage:.3f})")
    print(f"unique_tier1: {len(unique_tier1)}")
    print(f"non_music_findings_with_music_top_template: {non_music_music_top}")
    print(
        f"beliefs_with_{args.annotation_key}: {persisted_with_key}/{beliefs_total} "
        f"({persisted_ratio:.3f})"
    )

    failures: list[str] = []
    if len(unique_tier1) < args.min_unique_tier1:
        failures.append(
            f"unique_tier1={len(unique_tier1)} below threshold {args.min_unique_tier1}"
        )
    if tier2_coverage < args.min_tier2_coverage:
        failures.append(
            f"tier2_coverage={tier2_coverage:.3f} below threshold {args.min_tier2_coverage:.3f}"
        )
    if non_music_music_top > args.max_non_music_music_top:
        failures.append(
            f"non_music_music_top={non_music_music_top} exceeds max {args.max_non_music_music_top}"
        )
    if persisted_ratio < args.min_persisted_ratio:
        failures.append(
            f"persisted_ratio={persisted_ratio:.3f} below threshold {args.min_persisted_ratio:.3f}"
        )

    if failures:
        print("health_probe: FAIL")
        for item in failures:
            print(f"  - {item}")
        return 2

    print("health_probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
