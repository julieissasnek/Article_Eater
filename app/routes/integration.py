"""
Article Eater — Integration API Routes
Sprint INT-1 — 2026-02-11

Endpoints for Web-BN integration:
- Edge justification (beliefs supporting BN edges)
- Gap prediction (INT-2)
- Cross-layer queries (INT-5)

Per panel recommendations (P-VIS, P-LAYER):
- Pearl: BN edges should have epistemic justification
- Simon: Progressive disclosure for complex data
- Shneiderman: Overview first, details on demand
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integration", tags=["Integration"])


# =============================================================================
# Pydantic Models
# =============================================================================

class BeliefSummaryResponse(BaseModel):
    """Summary of a belief supporting/conflicting with an edge."""
    belief_id: str
    credence: float
    uncertainty: float
    content_summary: str
    paper_id: Optional[str] = None
    paper_citation: Optional[str] = None
    epistemic_level: Optional[str] = None
    theory_tags: List[str] = []


class ConflictSummaryResponse(BaseModel):
    """Summary of a conflicting belief."""
    belief_id: str
    credence: float
    conflict_type: str
    content_summary: str
    conflict_detail: Optional[str] = None


class ProvenanceSummaryResponse(BaseModel):
    """Provenance information for edge justification."""
    n_papers: int = 0
    primary_papers: List[str] = []
    date_range: Optional[Dict[str, int]] = None
    study_types: List[str] = []


class EdgeJustificationResponse(BaseModel):
    """Full edge justification response."""
    schema_: str = Field(alias="schema", default="integration.edge_justification.v1")
    edge_id: str
    source_node: str
    target_node: str
    aggregate_credence: float
    aggregate_uncertainty: float
    justification_status: str
    supporting_beliefs: List[BeliefSummaryResponse] = []
    conflicting_beliefs: List[ConflictSummaryResponse] = []
    net_support: float
    key_theories: List[str] = []
    causal_direction_confidence: float
    provenance: Optional[ProvenanceSummaryResponse] = None
    generated_at: str

    class Config:
        populate_by_name = True


class AllEdgesJustificationResponse(BaseModel):
    """Response for all edge justifications."""
    n_edges: int
    n_justified: int
    n_unjustified: int
    n_contested: int
    edges: List[EdgeJustificationResponse]


class UnjustifiedEdgesResponse(BaseModel):
    """Response for edges lacking justification."""
    n_unjustified: int
    edge_ids: List[str]
    recommendation: str


# =============================================================================
# Edge Justification Endpoints (INT-1)
# =============================================================================

@router.get(
    "/edge/{source}/{target}/justification",
    response_model=EdgeJustificationResponse,
    summary="Get epistemic justification for a BN edge",
    description="""
    Returns the epistemic justification for a Bayesian Network edge.

    This endpoint bridges the BN causal structure with the Web of Belief by:
    1. Finding beliefs that relate source to target variables
    2. Aggregating their credences (inverse-variance weighted)
    3. Identifying conflicting beliefs
    4. Computing justification status (STRONG, MODERATE, WEAK, UNJUSTIFIED, CONTESTED)

    Example: /api/v1/integration/edge/daylight/stress/justification
    """
)
async def get_edge_justification(source: str, target: str):
    """Get justification for a specific BN edge."""
    try:
        from src.services.edge_justification import get_edge_justification_service

        service = get_edge_justification_service()
        justification = service.get_justification(source, target)

        return justification.to_dict()

    except ImportError as e:
        logger.error(f"Edge justification service not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="Edge justification service not available"
        )
    except Exception as e:
        logger.error(f"Error getting edge justification: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error computing justification: {str(e)}"
        )


@router.get(
    "/edges/justifications",
    response_model=AllEdgesJustificationResponse,
    summary="Get justifications for all BN edges",
    description="""
    Returns justifications for all edges in the default BN structure.

    Optionally provide a custom list of edges as query parameter.
    """
)
async def get_all_edge_justifications(
    edges: Optional[str] = Query(
        None,
        description="Comma-separated edge list (e.g., 'daylight_stress,plants_mood')"
    )
):
    """Get justifications for all BN edges."""
    try:
        from src.services.edge_justification import get_edge_justification_service

        service = get_edge_justification_service()

        # Parse custom edges if provided
        bn_edges = None
        if edges:
            bn_edges = []
            for edge_str in edges.split(','):
                parts = edge_str.strip().split('_')
                if len(parts) >= 2:
                    bn_edges.append((parts[0], '_'.join(parts[1:])))

        justifications = service.get_all_justifications(bn_edges)

        # Compute summary stats
        n_justified = sum(1 for j in justifications if j.justification_status.value != 'unjustified')
        n_unjustified = sum(1 for j in justifications if j.justification_status.value == 'unjustified')
        n_contested = sum(1 for j in justifications if j.justification_status.value == 'contested')

        return {
            "n_edges": len(justifications),
            "n_justified": n_justified,
            "n_unjustified": n_unjustified,
            "n_contested": n_contested,
            "edges": [j.to_dict() for j in justifications]
        }

    except ImportError as e:
        logger.error(f"Edge justification service not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="Edge justification service not available"
        )
    except Exception as e:
        logger.error(f"Error getting all justifications: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error computing justifications: {str(e)}"
        )


@router.get(
    "/edges/unjustified",
    response_model=UnjustifiedEdgesResponse,
    summary="Find BN edges lacking epistemic justification",
    description="""
    Returns a list of BN edges that have no supporting beliefs in the Web of Belief.

    These represent potential gaps where:
    - The BN structure assumes a relationship
    - But no extracted evidence supports it
    """
)
async def get_unjustified_edges():
    """Find edges without epistemic support."""
    try:
        from src.services.edge_justification import get_edge_justification_service

        service = get_edge_justification_service()
        justifications = service.get_all_justifications()

        unjustified = [
            j.edge_id for j in justifications
            if j.justification_status.value == 'unjustified'
        ]

        return {
            "n_unjustified": len(unjustified),
            "edge_ids": unjustified,
            "recommendation": (
                "These edges lack epistemic support. Consider: "
                "1) Searching for papers that address these relationships, "
                "2) Removing unsupported edges from the BN, or "
                "3) Marking them as hypothetical."
            ) if unjustified else "All edges have epistemic support."
        }

    except Exception as e:
        logger.error(f"Error finding unjustified edges: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error finding unjustified edges: {str(e)}"
        )


# =============================================================================
# Gap Prediction Endpoints (INT-2)
# =============================================================================

class GapResponse(BaseModel):
    """A predicted knowledge gap."""
    gap_id: str
    gap_type: str
    description: str
    priority: str
    voi_score: float
    affected_edge: Optional[str] = None
    affected_beliefs: List[str] = []
    implied_by: List[str] = []
    suggested_search: str
    resolution_approach: str


class GapReportResponse(BaseModel):
    """Full gap analysis report."""
    schema_: str = Field(alias="schema", default="integration.gap_report.v1")
    report_id: str
    generated_at: str
    n_gaps: int
    n_high_priority: int
    summary: Dict[str, Any]
    gaps: List[GapResponse]

    class Config:
        populate_by_name = True


@router.get(
    "/gaps",
    response_model=GapReportResponse,
    summary="Find all knowledge gaps",
    description="""
    Analyzes the epistemic web to predict knowledge gaps.

    Gap types:
    - MEDIATION: A→X→Y exists but direct A→Y is missing
    - MECHANISM: Empirical beliefs without theoretical explanation
    - BOUNDARY: Narrow scope conditions (limited settings/populations)
    - DIRECTION: Conflicting causal directions
    - VALIDATION: Theoretical beliefs without empirical support
    - UNJUSTIFIED_EDGE: BN edges without belief support
    """
)
async def find_gaps(
    max_gaps: int = Query(50, description="Maximum number of gaps to return"),
    gap_type: Optional[str] = Query(None, description="Filter by gap type")
):
    """Find knowledge gaps in the epistemic web."""
    try:
        from src.services.gap_predictor import get_gap_predictor

        predictor = get_gap_predictor()
        report = predictor.find_all_gaps(max_gaps=max_gaps)

        # Filter by type if specified
        if gap_type:
            report.gaps = [g for g in report.gaps if g.gap_type.value == gap_type]
            report.n_gaps = len(report.gaps)
            report.n_high_priority = sum(1 for g in report.gaps if g.priority.value == 'high')

        return report.to_dict()

    except Exception as e:
        logger.error(f"Error finding gaps: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing gaps: {str(e)}"
        )


@router.get(
    "/gaps/{gap_type}",
    summary="Find gaps of a specific type"
)
async def find_gaps_by_type(gap_type: str):
    """Find gaps of a specific type."""
    valid_types = ['mediation', 'mechanism', 'boundary', 'direction', 'validation', 'unjustified_edge']
    if gap_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid gap type. Must be one of: {valid_types}"
        )

    try:
        from src.services.gap_predictor import get_gap_predictor

        predictor = get_gap_predictor()

        # Call specific detector
        if gap_type == 'mediation':
            gaps = predictor.find_mediation_gaps()
        elif gap_type == 'mechanism':
            gaps = predictor.find_mechanism_gaps()
        elif gap_type == 'boundary':
            gaps = predictor.find_boundary_gaps()
        elif gap_type == 'direction':
            gaps = predictor.find_direction_gaps()
        elif gap_type == 'validation':
            gaps = predictor.find_validation_gaps()
        elif gap_type == 'unjustified_edge':
            gaps = predictor.find_unjustified_edge_gaps()
        else:
            gaps = []

        return {
            "gap_type": gap_type,
            "n_gaps": len(gaps),
            "gaps": [g.to_dict() for g in gaps]
        }

    except Exception as e:
        logger.error(f"Error finding {gap_type} gaps: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# =============================================================================
# Web of Belief State Endpoint (INT-4)
# =============================================================================

class WebBeliefResponse(BaseModel):
    """A belief in the web."""
    belief_id: str
    content: str
    level: str
    status: str
    credence: float
    uncertainty: float
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    theory_id: Optional[str] = None
    tags: List[str] = []


class WebConstraintResponse(BaseModel):
    """A constraint in the web."""
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: str
    strength: float


class WebStateResponse(BaseModel):
    """Full web of belief state for visualization."""
    beliefs: List[WebBeliefResponse]
    constraints: List[WebConstraintResponse]
    n_beliefs: int
    n_constraints: int
    n_theoretical: int
    n_empirical: int


@router.get(
    "/web/state",
    response_model=WebStateResponse,
    summary="Get Web of Belief state for visualization",
    description="""
    Returns the current state of the Web of Belief for frontend visualization.
    Includes all beliefs and constraints with their properties.
    """
)
async def get_web_state():
    """Get the web of belief state."""
    try:
        from src.services.web_accumulator import WebAccumulator

        accumulator = WebAccumulator()
        web, _ = accumulator.get_master_web()

        beliefs = []
        n_theoretical = 0
        n_empirical = 0

        for belief in web.beliefs.values():
            cred = belief.credence.value if hasattr(belief.credence, 'value') else belief.credence
            unc = belief.credence.uncertainty if hasattr(belief.credence, 'uncertainty') else 0.3

            beliefs.append(WebBeliefResponse(
                belief_id=belief.belief_id,
                content=belief.content[:500],  # Truncate long content
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                credence=cred,
                uncertainty=unc,
                environment_id=belief.environment_id,
                outcome_id=belief.outcome_id,
                theory_id=getattr(belief, 'theory_id', None),
                tags=getattr(belief, 'tags', [])
            ))

            if belief.level.value == 'theoretical':
                n_theoretical += 1
            elif belief.level.value == 'empirical':
                n_empirical += 1

        constraints = []
        for constraint in web.constraints.values():
            constraints.append(WebConstraintResponse(
                constraint_id=constraint.constraint_id,
                source_id=constraint.source_id,
                target_id=constraint.target_id,
                constraint_type=constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type),
                strength=constraint.strength
            ))

        return WebStateResponse(
            beliefs=beliefs,
            constraints=constraints,
            n_beliefs=len(beliefs),
            n_constraints=len(constraints),
            n_theoretical=n_theoretical,
            n_empirical=n_empirical
        )

    except Exception as e:
        logger.error(f"Error getting web state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving web state: {str(e)}"
        )


# =============================================================================
# Cross-Layer Query Endpoints (INT-5)
# =============================================================================

class CrossLayerQueryResponse(BaseModel):
    """Response for cross-layer queries."""
    query_type: str
    query_params: Dict[str, Any]
    n_beliefs: int
    n_connections: int
    beliefs: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    layer_summary: Dict[str, int]
    generated_at: str


class TheorySupportResponse(BaseModel):
    """Response for theory support query."""
    theory: Dict[str, Any]
    n_supporting: int
    support_strength: float
    coverage_score: float
    supporting_beliefs: List[Dict[str, Any]]
    gaps: List[str]


class LayerStatisticsResponse(BaseModel):
    """Response for layer statistics."""
    total_beliefs: int
    total_constraints: int
    by_level: Dict[str, int]
    cross_layer_connections: int
    within_layer_connections: int
    constraint_types: Dict[str, int]


@router.get(
    "/query/theory/{theory_id}/support",
    response_model=TheorySupportResponse,
    summary="Find empirical support for a theory",
    description="""
    Returns empirical beliefs that support a given theoretical belief.
    Includes support strength, coverage score, and identified gaps.
    """
)
async def get_theory_support(theory_id: str):
    """Find empirical support for a theoretical belief."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        result = service.find_theory_support(theory_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Theory belief '{theory_id}' not found"
            )

        return result.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding theory support: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "/query/empirical/{empirical_id}/grounding",
    response_model=CrossLayerQueryResponse,
    summary="Find theoretical grounding for empirical belief",
    description="""
    Returns theoretical beliefs that provide grounding for an empirical finding.
    """
)
async def get_empirical_grounding(empirical_id: str):
    """Find theoretical grounding for an empirical belief."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        result = service.find_empirical_grounding(empirical_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Empirical belief '{empirical_id}' not found"
            )

        return result.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding empirical grounding: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "/query/environment-outcome",
    response_model=CrossLayerQueryResponse,
    summary="Find beliefs connecting environment to outcome",
    description="""
    Returns beliefs that link a specific environment feature to a psychological outcome.
    Filter by environment_id (e.g., 'daylight') and/or outcome_id (e.g., 'stress').
    """
)
async def get_environment_outcome_beliefs(
    environment_id: Optional[str] = Query(None, description="Environment ID to filter by"),
    outcome_id: Optional[str] = Query(None, description="Outcome ID to filter by")
):
    """Find beliefs connecting environment to outcome."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        result = service.find_environment_outcome_beliefs(
            environment_id=environment_id,
            outcome_id=outcome_id
        )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Error finding environment-outcome beliefs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "/query/conflicts",
    response_model=CrossLayerQueryResponse,
    summary="Find cross-layer conflicts",
    description="""
    Returns beliefs that have contradictions across different epistemic layers.
    These represent areas where theory and evidence may be in tension.
    """
)
async def get_cross_layer_conflicts():
    """Find conflicts between beliefs at different epistemic layers."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        result = service.find_cross_layer_conflicts()

        return result.to_dict()

    except Exception as e:
        logger.error(f"Error finding cross-layer conflicts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "/query/belief/{belief_id}/chain",
    response_model=CrossLayerQueryResponse,
    summary="Get belief chain",
    description="""
    Returns the full chain of beliefs connected to a given belief.
    Traces connections both up (towards theory) and down (towards observation).
    """
)
async def get_belief_chain(
    belief_id: str,
    max_depth: int = Query(5, description="Maximum traversal depth", ge=1, le=10)
):
    """Get the full chain of beliefs connected to a given belief."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        result = service.get_belief_chain(belief_id, max_depth=max_depth)

        if not result.beliefs:
            raise HTTPException(
                status_code=404,
                detail=f"Belief '{belief_id}' not found"
            )

        return result.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting belief chain: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "/query/statistics",
    response_model=LayerStatisticsResponse,
    summary="Get layer statistics",
    description="""
    Returns statistics about beliefs across epistemic layers.
    Includes counts by level, constraint types, and cross-layer vs within-layer connections.
    """
)
async def get_layer_statistics():
    """Get statistics about beliefs across layers."""
    try:
        from src.services.cross_layer_query import get_cross_layer_service

        service = get_cross_layer_service()
        stats = service.get_layer_statistics()

        if "error" in stats:
            raise HTTPException(
                status_code=503,
                detail=stats["error"]
            )

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting layer statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# =============================================================================
# Health Check
# =============================================================================

@router.get(
    "/health",
    summary="Integration API health check"
)
async def integration_health():
    """Check integration service health."""
    try:
        from src.services.edge_justification import EdgeJustificationService
        from src.services.cross_layer_query import CrossLayerQueryService

        edge_service = EdgeJustificationService()
        query_service = CrossLayerQueryService()

        web_available = edge_service.web is not None
        query_available = query_service.web is not None

        return {
            "status": "healthy" if web_available else "degraded",
            "web_available": web_available,
            "services": {
                "edge_justification": True,
                "gap_predictor": True,  # INT-2
                "cross_layer_query": query_available  # INT-5
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
