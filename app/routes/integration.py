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
        service = EdgeJustificationService()
        web_available = service.web is not None

        return {
            "status": "healthy" if web_available else "degraded",
            "web_available": web_available,
            "services": {
                "edge_justification": True,
                "gap_predictor": False,  # INT-2
                "cross_layer_query": False  # INT-5
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
