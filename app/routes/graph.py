from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional

from src.services.service_locator import get_graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/events")
def list_events(
    type: Optional[str] = Query(None, description="Filter by event type, e.g. 'finding', 'seven_panel', 'aggregation', 'links'"),
    paper_id: Optional[str] = Query(None, description="Optional paper_id filter"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of events to return"),
) -> Dict[str, Any]:
    """Read-only view over the JSONL graph events."""
    store = get_graph_service()
    events: List[Dict[str, Any]] = store.get_all_events()

    if type:
        events = [e for e in events if e.get("type") == type]
    if paper_id:
        events = [e for e in events if e.get("paper_id") == paper_id]

    truncated = False
    if len(events) > limit:
        events = events[:limit]
        truncated = True

    return {
        "count": len(events),
        "truncated": truncated,
        "events": events,
    }


@router.get("/topic/{topic}")
def graph_by_topic(topic: str) -> Dict[str, Any]:
    """Navigate findings and links for a given topic (substring matching)."""
    store = get_graph_service()
    findings = store.get_findings_by_topic(topic)
    links = store.get_links_for_topic(topic)
    return {
        "topic": topic,
        "findings": findings,
        "links": links,
    }
