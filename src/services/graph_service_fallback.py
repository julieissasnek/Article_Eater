
"""JSONL-based fallback graph service for Article Eater.

This is deliberately simple and file-backed so the system has a
persistence layer even if no external graph DB (e.g. Neo4j) is configured.

It stores append-only events to data/graph.jsonl. Each line is a JSON object.

The API is intentionally narrow and can be replaced by a real graph backend
by implementing the same methods on a different class.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Iterable, List
import json, uuid

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_PATH = DATA_DIR / "graph.jsonl"

def _write(event: Dict[str, Any]) -> None:
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    with GRAPH_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def _iter() -> Iterable[Dict[str, Any]]:
    if not GRAPH_PATH.exists():
        return []
    with GRAPH_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                # Ignore corrupt lines rather than breaking the whole store
                continue

class JSONLGraphStore:
    """Very small event-sourced JSONL store.

    This is *not* a general-purpose graph DB; it is just enough
    for the Article Eater demo flows and can be swapped out later.
    """

    def create_finding(self, paper_id: str, finding: Dict[str, Any]) -> str:
        rec_id = str(uuid.uuid4())
        _write({
            "type": "finding",
            "id": rec_id,
            "paper_id": paper_id,
            "finding": finding,
        })
        return rec_id

    def attach_seven_panel(self, paper_id: str, panel: Dict[str, Any], raw_abstract=None) -> None:
        _write({
            "type": "seven_panel",
            "paper_id": paper_id,
            "panel": panel,
            "raw_abstract": raw_abstract,
        })

    def get_findings_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Very simple substring-based topic search on finding_text."""
        topic = (topic or "").lower().strip()
        if not topic:
            return [e["finding"] for e in _iter() if e.get("type") == "finding"]
        out: List[Dict[str, Any]] = []
        for e in _iter():
            if e.get("type") != "finding":
                continue
            txt = (e.get("finding", {}).get("finding_text", "") or "").lower()
            if topic in txt:
                out.append(e["finding"])
        return out

    def apply_aggregation(self, topic: str, payload: Dict[str, Any]) -> None:
        _write({
            "type": "aggregation",
            "topic": topic,
            "payload": payload,
        })

    def get_constructs_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Return simple 'construct' summaries from prior aggregations."""
        items: List[Dict[str, Any]] = []
        for e in _iter():
            if e.get("type") == "aggregation" and e.get("topic") == topic:
                groups = (e.get("payload", {}) or {}).get("groups") or []
                for g in groups:
                    items.append({"summary": g.get("summary", "")})
        return items

    def apply_links(self, topic: str, payload: Dict[str, Any]) -> None:
        _write({
            "type": "links",
            "topic": topic,
            "payload": payload,
        })



    def apply_rulegraph_v2(self, paper_id: str, rules: List[Dict[str, Any]]) -> None:
        """Append a RuleGraph v2 event to the JSONL store.

        This keeps v2 rule payloads segregated from legacy events while
        remaining inspectable with a simple `cat data/graph.jsonl`.
        """
        _write({
            "type": "rulegraph_v2",
            "paper_id": paper_id,
            "rules": rules,
        })
    def get_links_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for e in _iter():
            if e.get("type") == "links" and e.get("topic") == topic:
                out.append(e.get("payload") or {})
        return out

    def get_all_events(self) -> List[Dict[str, Any]]:
        return list(_iter())
