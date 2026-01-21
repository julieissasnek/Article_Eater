"""
Web of Belief API Routes
========================

FastAPI routes for Evidence Explorer visualization.
Connects frontend to graph_api.py and stability_engine.py services.

Date: January 21, 2026
Phase B Sprint B1
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# Import services
from src.services.web_of_belief import WebOfBelief, Belief
from src.services.graph_api import GraphAPIService, GraphExport, NodeDetail, SearchResults
from src.services.stability_engine import StabilityEngine, StabilityReport


# =============================================================================
# Router Configuration
# =============================================================================

router = APIRouter(prefix="/web", tags=["web-of-belief"])


# =============================================================================
# Response Models
# =============================================================================

class GraphResponse(BaseModel):
    """Graph export response for Cytoscape.js visualization."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class NodeDetailResponse(BaseModel):
    """Node detail response for detail panel."""
    belief_id: str
    content: str
    credence: Dict[str, Any]
    status: str
    outcome_category: Optional[str]
    source_depth: str
    scope: Optional[Dict[str, Any]]
    enabling_conditions: Optional[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    outgoing_constraints: List[Dict[str, Any]]
    incoming_constraints: List[Dict[str, Any]]
    credence_history_length: int
    stability_info: Dict[str, Any]
    # Three-level views per Simon
    headline: str
    summary: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search results response."""
    query: str
    total_results: int
    beliefs: List[Dict[str, Any]]
    papers: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]


class StabilityResponse(BaseModel):
    """Stability report response."""
    stability_level: str
    total_beliefs: int
    stable_beliefs: int
    unstable_beliefs: int
    contested_beliefs: int
    papers_processed: int
    publication_bias: Dict[str, Any]
    recommendation: str
    convergence_achieved: bool
    gaps: List[Dict[str, Any]]


# =============================================================================
# Web State Management (Singleton for now)
# =============================================================================

# In-memory web instance for demonstration
# Production would load from persistence layer
_web_instance: Optional[WebOfBelief] = None


def get_web() -> WebOfBelief:
    """Get or create the web of belief instance."""
    global _web_instance
    if _web_instance is None:
        _web_instance = WebOfBelief()
    return _web_instance


def set_web(web: WebOfBelief) -> None:
    """Set the web of belief instance (for testing or loading)."""
    global _web_instance
    _web_instance = web


# =============================================================================
# Graph Endpoints
# =============================================================================

@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    max_nodes: int = Query(30, ge=1, le=500, description="Maximum nodes to return"),
    min_credence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum credence threshold"),
    outcome_category: Optional[str] = Query(None, description="Filter by outcome category"),
    include_contested: bool = Query(True, description="Include contested beliefs")
) -> GraphResponse:
    """
    Get graph export for Cytoscape.js visualization.

    Returns nodes and edges in format ready for Cytoscape rendering.
    Default returns top 30 beliefs by credence (per Simon's recommendation).
    """
    web = get_web()
    service = GraphAPIService(web)

    # Use export_graph with its native parameters
    export = service.export_graph(
        max_nodes=max_nodes,
        min_credence=min_credence,
        outcome_filter=outcome_category,
        include_stubs=True
    )

    # Apply additional filter for contested if needed
    if not include_contested:
        nodes = [n for n in export.nodes if not n.contested]
        node_ids = {n.id for n in nodes}
        edges = [e for e in export.edges if e.source in node_ids and e.target in node_ids]
    else:
        nodes = export.nodes
        edges = export.edges

    return GraphResponse(
        nodes=[n.to_dict() for n in nodes],
        edges=[e.to_dict() for e in edges],
        metadata=export.metadata.to_dict()
    )


@router.get("/node/{belief_id}", response_model=NodeDetailResponse)
async def get_node_detail(belief_id: str) -> NodeDetailResponse:
    """
    Get detailed information for a single belief node.

    Returns three-level progressive disclosure:
    - headline: Single sentence summary
    - summary: Traffic-light view with key stats
    - full: Complete detail (all fields)
    """
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    service = GraphAPIService(web)
    detail = service.get_node_detail(belief_id)

    # Get stability info
    stability_engine = StabilityEngine(web)
    belief = web.beliefs[belief_id]
    stability_info = stability_engine.get_belief_stability_info(belief)

    # Build three-level views per Simon/Panel
    # Headline: Single sentence
    confidence_word = "High" if detail.credence > 0.7 else "Medium" if detail.credence > 0.4 else "Low"
    contested_flag = " (Contested)" if detail.contested else ""
    headline = f"{detail.content[:100]}{'...' if len(detail.content) > 100 else ''} — {confidence_word} confidence{contested_flag}"

    # Summary: Traffic light + key stats
    traffic_light = "green" if detail.credence > 0.7 else "yellow" if detail.credence > 0.4 else "red"
    summary = {
        "traffic_light": traffic_light,
        "credence_value": round(detail.credence, 2),
        "source_count": len(detail.sources),
        "disagreement_flag": detail.contested,
        "stability_status": "stable" if detail.is_stable else "evolving"
    }

    return NodeDetailResponse(
        belief_id=detail.belief_id,
        content=detail.content,
        credence={
            "value": detail.credence,
            "uncertainty": detail.credence_uncertainty,
            "range": list(detail.credence_range) if detail.credence_range else None
        },
        status=detail.status,
        outcome_category=detail.outcome_category,
        source_depth=detail.source_depth,
        scope=detail.scope.to_dict() if detail.scope else None,
        enabling_conditions=detail.enabling_conditions,
        sources=[s.to_dict() for s in detail.sources],
        outgoing_constraints=[c.to_dict() for c in detail.outgoing_constraints],
        incoming_constraints=[c.to_dict() for c in detail.incoming_constraints],
        credence_history_length=detail.credence_history_length,
        stability_info=stability_info.to_dict(),
        headline=headline,
        summary=summary
    )


@router.get("/search", response_model=SearchResponse)
async def search_web(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per category")
) -> SearchResponse:
    """
    Search beliefs, papers, and categories.

    Returns categorized results for search box dropdown.
    """
    web = get_web()
    service = GraphAPIService(web)

    results = service.search(q, max_results=limit)

    return SearchResponse(
        query=q,
        total_results=results.total_count,
        beliefs=[b.to_dict() for b in results.beliefs],
        papers=[p.to_dict() for p in results.papers],
        categories=[]  # No categories in SearchResults, could add if needed
    )


# =============================================================================
# Stability Endpoints
# =============================================================================

@router.get("/stability", response_model=StabilityResponse)
async def get_stability_report() -> StabilityResponse:
    """
    Get current stability report for the web.

    Includes:
    - Overall stability level
    - Publication bias assessment
    - Stopping recommendation
    - Identified gaps
    """
    web = get_web()
    engine = StabilityEngine(web)

    report = engine.generate_report()
    all_gaps, high_voi_gaps = engine.identify_gaps()

    return StabilityResponse(
        stability_level=report.stability_level.value,
        total_beliefs=report.total_beliefs,
        stable_beliefs=report.stable_beliefs,
        unstable_beliefs=report.unstable_beliefs,
        contested_beliefs=report.contested_beliefs,
        papers_processed=report.papers_processed,
        publication_bias=report.publication_bias.to_dict() if report.publication_bias else {},
        recommendation=report.recommendation,
        convergence_achieved=report.convergence_achieved,
        gaps=[g.to_dict() for g in high_voi_gaps]
    )


@router.get("/stability/should-stop")
async def should_stop_searching() -> Dict[str, Any]:
    """
    Check if search should stop based on stability.

    Returns decision and explanation (framed as "given current evidence").
    """
    web = get_web()
    engine = StabilityEngine(web)

    should_stop, reason = engine.should_stop_searching()

    return {
        "should_stop": should_stop,
        "reason": reason,
        "papers_processed": engine.papers_processed,
        "current_stability": engine.check_stability().value
    }


# =============================================================================
# Top Beliefs Endpoint (for default view)
# =============================================================================

@router.get("/top-beliefs")
async def get_top_beliefs(
    limit: int = Query(30, ge=1, le=100, description="Number of beliefs to return")
) -> Dict[str, Any]:
    """
    Get top beliefs by credence for default view.

    Per Simon's recommendation: show top 20-30 beliefs by default,
    not the entire web.
    """
    web = get_web()
    service = GraphAPIService(web)

    top = service.get_top_beliefs(n=limit)

    return {
        "count": len(top),
        "beliefs": top
    }


# =============================================================================
# Categories Endpoint (for filtering)
# =============================================================================

@router.get("/categories")
async def get_categories() -> Dict[str, Any]:
    """
    Get list of outcome categories with counts.

    Used for category filter dropdown in Evidence Explorer.
    """
    web = get_web()

    categories = {}
    for belief in web.beliefs.values():
        cat = belief.outcome_id or "uncategorized"
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in sorted(categories.items(), key=lambda x: -x[1])
        ]
    }


# =============================================================================
# Admin Endpoints (for testing/development)
# =============================================================================

@router.post("/admin/load-demo")
async def load_demo_data() -> Dict[str, Any]:
    """
    Load demonstration data for Evidence Explorer.
    Creates sample beliefs with various states for testing.
    """
    from src.services.web_of_belief import Credence, EpistemicLevel, BeliefStatus, SourceDepth
    from src.services.web_of_belief import EnablingConditions

    web = WebOfBelief()

    # Sample beliefs for demonstration
    demo_beliefs = [
        {
            "belief_id": "demo_1",
            "content": "Natural daylight in office environments improves worker productivity by 15-20%",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.78, 0.12),
            "outcome_id": "productivity",
            "source_depth": SourceDepth.FULL_TEXT,
        },
        {
            "belief_id": "demo_2",
            "content": "Biophilic design elements reduce perceived stress in healthcare settings",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.72, 0.15),
            "outcome_id": "stress_reduction",
            "source_depth": SourceDepth.FULL_TEXT,
        },
        {
            "belief_id": "demo_3",
            "content": "Indoor plants improve air quality through phytoremediation",
            "level": EpistemicLevel.THEORETICAL,
            "credence": Credence(0.65, 0.20),
            "outcome_id": "air_quality",
            "source_depth": SourceDepth.ABSTRACT,
        },
        {
            "belief_id": "demo_4",
            "content": "Access to nature views from windows correlates with faster patient recovery",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.68, 0.18),
            "outcome_id": "health_outcomes",
            "source_depth": SourceDepth.FULL_TEXT,
        },
        {
            "belief_id": "demo_5",
            "content": "Open-plan offices increase collaboration but decrease individual focus",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.55, 0.25),
            "outcome_id": "productivity",
            "contested": True,  # Conflicting evidence
            "source_depth": SourceDepth.FULL_TEXT,
        },
        {
            "belief_id": "demo_6",
            "content": "Noise levels above 65dB significantly impair cognitive performance",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.82, 0.08),
            "outcome_id": "cognitive_performance",
            "source_depth": SourceDepth.FULL_TEXT,
        },
        {
            "belief_id": "demo_7",
            "content": "Thermal comfort (20-24C) optimizes cognitive task performance",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.75, 0.10),
            "outcome_id": "cognitive_performance",
            "source_depth": SourceDepth.FULL_TEXT,
            "enabling_conditions": EnablingConditions(
                threshold=">20C and <24C",
                temporal_order="continuous exposure during task"
            )
        },
        {
            "belief_id": "demo_8",
            "content": "Green spaces near schools improve children's cognitive development",
            "level": EpistemicLevel.EMPIRICAL,
            "credence": Credence(0.58, 0.22),
            "outcome_id": "cognitive_development",
            "source_depth": SourceDepth.ABSTRACT,
        },
    ]

    for b in demo_beliefs:
        belief = Belief(**{k: v for k, v in b.items() if k != 'contested'})
        if b.get('contested'):
            belief.contested = True
        web.beliefs[belief.belief_id] = belief

        # Add some credence history for stability demonstration
        for i in range(5):
            delta = (i - 2) * 0.02  # Small fluctuations
            belief.record_credence_change(
                belief.credence.value + delta,
                f"paper_{i}"
            )

    # Add some connections (constraints)
    from src.services.web_of_belief import Constraint, ConstraintType
    connections = [
        ("demo_1", "demo_2", ConstraintType.SUPPORTS, 0.6),
        ("demo_2", "demo_4", ConstraintType.SUPPORTS, 0.5),
        ("demo_6", "demo_7", ConstraintType.SUPPORTS, 0.7),
        ("demo_3", "demo_2", ConstraintType.SUPPORTS, 0.4),
        ("demo_5", "demo_1", ConstraintType.CONTRADICTS, 0.3),
        ("demo_8", "demo_7", ConstraintType.SUPPORTS, 0.5),  # Using SUPPORTS for correlational
    ]
    for src, tgt, ctype, strength in connections:
        web.add_constraint(Constraint(
            constraint_id=f"c:{src}:{tgt}",
            source_id=src,
            target_id=tgt,
            constraint_type=ctype,
            strength=strength
        ))

    set_web(web)

    return {
        "status": "success",
        "beliefs_loaded": len(web.beliefs),
        "connections_added": 6
    }


@router.delete("/admin/clear")
async def clear_web() -> Dict[str, Any]:
    """Clear the web of belief (for testing)."""
    global _web_instance
    _web_instance = WebOfBelief()
    return {"status": "cleared"}
