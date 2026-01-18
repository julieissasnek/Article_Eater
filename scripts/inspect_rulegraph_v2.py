#!/usr/bin/env python3
"""Inspect RuleGraph v2 events in data/graph.jsonl.

This is a small CLI helper for humans (or downstream tools) to quickly
see which subject-aware rules exist, which papers they come from, and
a summary of subject_scope / subject_moderators.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict
from typing import Any, Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "graph.jsonl"


def load_events() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        print(f"[inspect_rulegraph_v2] No graph file at {DATA_PATH}")
        return []
    out: List[Dict[str, Any]] = []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # Ignore malformed lines; graph.jsonl is meant to be append-only and resilient.
                continue
    return out


def summarize_scope(scope: Dict[str, Any]) -> str:
    if not scope:
        return "no subject_scope"
    bits: List[str] = []
    demo = scope.get("demographics") or {}
    cult = scope.get("culture") or {}
    clin = scope.get("clinical_status") or {}
    traits = scope.get("traits_measured") or []

    if demo:
        band = demo.get("age_band") or "age_band=unknown"
        n = demo.get("sample_size")
        n_str = f"n={n}" if n is not None else "n=?"
        ed = demo.get("education_band") or "education_band=unknown"
        bits.append(f"{band}, {ed}, {n_str}")
    if cult:
        region = cult.get("region") or "region=unknown"
        countries = cult.get("countries") or []
        if countries:
            bits.append(f"{region}, {', '.join(countries)}")
        else:
            bits.append(region)
    if clin:
        pop = clin.get("population") or "population=unknown"
        bits.append(pop)
    if traits:
        names = [t.get("name") for t in traits if t.get("name")]
        if names:
            bits.append("traits: " + ", ".join(sorted(set(names))))
    return " | ".join(bits) if bits else "no subject_scope"


def summarize_moderators(moderators: List[Dict[str, Any]]) -> str:
    if not moderators:
        return "no moderators"
    dims = defaultdict(list)
    for m in moderators:
        dim = m.get("dimension") or "other"
        attr = m.get("attribute") or "<?>"
        dims[dim].append(attr)
    parts = []
    for dim, attrs in dims.items():
        uniq = sorted(set(attrs))
        parts.append(f"{dim}: {', '.join(uniq)}")
    return " | ".join(parts)


def main() -> None:
    events = load_events()
    if not events:
        return

    v2_events = [e for e in events if e.get("type") == "rulegraph_v2"]
    if not v2_events:
        print("[inspect_rulegraph_v2] No rulegraph_v2 events found.")
        return

    print(f"[inspect_rulegraph_v2] Found {len(v2_events)} rulegraph_v2 event(s).")
    for idx, ev in enumerate(v2_events, start=1):
        paper_id = ev.get("paper_id", "<unknown>")
        rules = ev.get("rules") or []
        print(f"Event {idx}: paper_id={paper_id}, rules={len(rules)}")

        # Show up to 3 sample rules.
        for r in rules[:3]:
            rid = r.get("rule_id", "<no-id>")
            text = (r.get("rule_text") or "")[:120].replace("\n", " ")
            scope = r.get("subject_scope") or {}
            moderators = r.get("subject_moderators") or []
            print(f"  - {rid}")
            print(f"    text: {text!r}")
            print(f"    scope: {summarize_scope(scope)}")
            print(f"    moderators: {summarize_moderators(moderators)}")
        print()

    print("[inspect_rulegraph_v2] Done.")


if __name__ == "__main__":
    main()
