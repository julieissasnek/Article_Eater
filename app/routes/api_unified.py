"""
Article Eater V23 — Unified API Routes
Sprint 3.0.1 — 2026-02-08

Resource-based REST API following panel recommendations:
- Stonebraker/Fielding: Resource-based design (~25 endpoints)
- Simon: Layered API (Core 7 → Extended 25 → Full)
- Dean/Fowler: URL versioning, pagination, async

Core 7 Endpoints:
1. /api/v1/beliefs/      — Belief CRUD + search
2. /api/v1/queries/      — Natural language query execution
3. /api/v1/export/       — Evidence summaries, BibTeX, bundles
4. /api/v1/communities/  — Community-relative operations
5. /api/v1/constraints/  — Epistemic constraints
6. /api/v1/papers/       — Paper/source management
7. /api/v1/admin/        — System state, health, statistics
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import logging
import json
import io

logger = logging.getLogger(__name__)

# Create routers for each resource
beliefs_router = APIRouter(prefix="/beliefs", tags=["beliefs"])
queries_router = APIRouter(prefix="/queries", tags=["queries"])
export_router = APIRouter(prefix="/export", tags=["export"])
communities_router = APIRouter(prefix="/communities", tags=["communities"])
constraints_router = APIRouter(prefix="/constraints", tags=["constraints"])
papers_router = APIRouter(prefix="/papers", tags=["papers"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# Pydantic Models
# =============================================================================

class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BeliefStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CONTESTED = "CONTESTED"
    STUB = "STUB"


class EpistemicLevel(str, Enum):
    THEORETICAL = "THEORETICAL"
    INTERMEDIATE = "INTERMEDIATE"
    EMPIRICAL = "EMPIRICAL"
    OBSERVATIONAL = "OBSERVATIONAL"


class BeliefSummary(BaseModel):
    """Summary view of a belief."""
    id: str
    content: str
    credence: float
    uncertainty: float = 0.0
    status: BeliefStatus
    level: EpistemicLevel
    theory: Optional[str] = None
    sources_count: int = 0
    constraints_count: int = 0


class BeliefDetail(BeliefSummary):
    """Detailed view of a belief with all fields."""
    scope_conditions: Optional[Dict[str, str]] = None
    sources: List[str] = []
    supporting_constraints: List[str] = []
    opposing_constraints: List[str] = []
    communities: List[str] = []
    entrenchment: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BeliefCreate(BaseModel):
    """Request to create a new belief."""
    content: str
    credence: float = Field(ge=0.0, le=1.0)
    status: BeliefStatus = BeliefStatus.STUB
    level: EpistemicLevel = EpistemicLevel.EMPIRICAL
    theory: Optional[str] = None
    sources: List[str] = []


class BeliefUpdate(BaseModel):
    """Request to update a belief."""
    content: Optional[str] = None
    credence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    status: Optional[BeliefStatus] = None


class BeliefListResponse(BaseModel):
    """Paginated list of beliefs."""
    beliefs: List[BeliefSummary]
    total: int
    limit: int
    offset: int
    _links: Dict[str, str] = {}


class QueryRequest(BaseModel):
    """Natural language query request."""
    query: str
    mode: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    user_type: Optional[str] = None
    include_scope: bool = True
    include_practitioner_implications: bool = True
    max_evidence: int = Field(default=10, ge=1, le=50)


class QueryResponse(BaseModel):
    """Query result with progressive disclosure."""
    query_id: str
    status: str  # pending, complete, error
    query: str
    query_type: str
    causal_level: str
    headline: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    detail: Optional[Dict[str, Any]] = None
    practical_implications: Optional[List[str]] = None
    scope_conditions: Optional[Dict[str, str]] = None
    caveats: Optional[List[str]] = None
    key_sources: Optional[List[str]] = None
    processing_time_ms: int = 0
    cost_estimate: float = 0.0


class ExportRequest(BaseModel):
    """Export generation request."""
    topic: str
    purpose: str = Field(
        default="literature_review",
        pattern="^(practitioner_briefing|literature_review|systematic_review|data_pipeline|presentation)$"
    )
    format: str = Field(default="markdown", pattern="^(markdown|json|bibtex|jsonl)$")
    belief_ids: Optional[List[str]] = None
    min_credence: float = Field(default=0.0, ge=0.0, le=1.0)
    include_scope: bool = True
    include_checklist: bool = True


class ExportResponse(BaseModel):
    """Export result."""
    export_id: str
    topic: str
    purpose: str
    generated_at: str
    files: Dict[str, str]  # filename -> content or URL


class CommunityResponse(BaseModel):
    """Epistemic community."""
    id: str
    name: str
    description: Optional[str] = None
    beliefs_count: int
    average_credence: float
    key_researchers: List[str] = []


class ConstraintResponse(BaseModel):
    """Epistemic constraint between beliefs."""
    id: str
    from_belief: str
    to_belief: str
    polarity: str  # POSITIVE or NEGATIVE
    strength: float
    reason: Optional[str] = None


class PaperResponse(BaseModel):
    """Source paper."""
    id: str
    title: str
    authors: List[str]
    year: int
    journal: Optional[str] = None
    doi: Optional[str] = None
    beliefs_extracted: int = 0
    status: str = "pending"  # pending, processing, complete, error


class SystemStats(BaseModel):
    """System-wide statistics."""
    total_beliefs: int
    total_constraints: int
    total_papers: int
    total_communities: int
    overall_coherence: float
    average_credence: float
    contested_beliefs: int
    stub_beliefs: int
    last_updated: str


class HealthResponse(BaseModel):
    """System health status."""
    status: str  # healthy, degraded, unhealthy
    api_version: str
    uptime_seconds: int
    checks: Dict[str, Dict[str, Any]]


# =============================================================================
# Beliefs Endpoints
# =============================================================================

@beliefs_router.get("/", response_model=BeliefListResponse)
async def list_beliefs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[List[BeliefStatus]] = Query(default=None),
    level: Optional[List[EpistemicLevel]] = Query(default=None),
    theory: Optional[str] = Query(default=None),
    min_credence: float = Query(default=0.0, ge=0.0, le=1.0),
    search: Optional[str] = Query(default=None)
):
    """
    List beliefs with filtering and pagination.

    Filters:
    - status: Filter by belief status (ACCEPTED, REJECTED, CONTESTED, STUB)
    - level: Filter by epistemic level
    - theory: Filter by associated theory
    - min_credence: Minimum credence threshold
    - search: Full-text search in belief content
    """
    # TODO: Integrate with actual WebOfBelief
    # For now, return demo data
    demo_beliefs = [
        BeliefSummary(
            id="B001",
            content="Natural environments restore directed attention capacity",
            credence=0.85,
            uncertainty=0.08,
            status=BeliefStatus.ACCEPTED,
            level=EpistemicLevel.THEORETICAL,
            theory="ART",
            sources_count=12,
            constraints_count=8
        ),
        BeliefSummary(
            id="B002",
            content="Plants in offices reduce self-reported stress by 15-25%",
            credence=0.72,
            uncertainty=0.12,
            status=BeliefStatus.ACCEPTED,
            level=EpistemicLevel.EMPIRICAL,
            theory="Biophilia",
            sources_count=8,
            constraints_count=5
        ),
        BeliefSummary(
            id="B003",
            content="Window views to nature improve patient recovery",
            credence=0.65,
            uncertainty=0.15,
            status=BeliefStatus.CONTESTED,
            level=EpistemicLevel.EMPIRICAL,
            theory="SRT",
            sources_count=6,
            constraints_count=12
        ),
    ]

    return BeliefListResponse(
        beliefs=demo_beliefs,
        total=len(demo_beliefs),
        limit=limit,
        offset=offset,
        _links={
            "self": f"/api/v1/beliefs/?limit={limit}&offset={offset}",
            "next": f"/api/v1/beliefs/?limit={limit}&offset={offset + limit}" if offset + limit < len(demo_beliefs) else None
        }
    )


@beliefs_router.get("/{belief_id}", response_model=BeliefDetail)
async def get_belief(belief_id: str):
    """Get detailed information about a specific belief."""
    # TODO: Integrate with actual WebOfBelief
    if belief_id == "B001":
        return BeliefDetail(
            id="B001",
            content="Natural environments restore directed attention capacity",
            credence=0.85,
            uncertainty=0.08,
            status=BeliefStatus.ACCEPTED,
            level=EpistemicLevel.THEORETICAL,
            theory="ART",
            sources_count=12,
            constraints_count=8,
            scope_conditions={
                "population": "Adults, primarily Western",
                "setting": "Laboratory and field studies",
                "methodology": "Attention tests, self-report"
            },
            sources=["Kaplan & Kaplan 1989", "Berman et al. 2008", "Hartig et al. 2014"],
            supporting_constraints=["C001", "C002", "C003"],
            opposing_constraints=[],
            communities=["ART", "Environmental Psychology"],
            entrenchment=0.78
        )
    raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")


@beliefs_router.post("/", response_model=BeliefDetail, status_code=201)
async def create_belief(belief: BeliefCreate):
    """Create a new belief."""
    # TODO: Integrate with actual WebOfBelief
    new_id = f"B{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return BeliefDetail(
        id=new_id,
        content=belief.content,
        credence=belief.credence,
        status=belief.status,
        level=belief.level,
        theory=belief.theory,
        sources_count=len(belief.sources),
        constraints_count=0
    )


@beliefs_router.put("/{belief_id}", response_model=BeliefDetail)
async def update_belief(belief_id: str, update: BeliefUpdate):
    """Update an existing belief."""
    # TODO: Integrate with actual WebOfBelief
    raise HTTPException(status_code=501, detail="Update not yet implemented")


@beliefs_router.delete("/{belief_id}", status_code=204)
async def delete_belief(belief_id: str):
    """Delete a belief (move to quarantine)."""
    # TODO: Integrate with actual WebOfBelief
    raise HTTPException(status_code=501, detail="Delete not yet implemented")


@beliefs_router.get("/{belief_id}/constraints")
async def get_belief_constraints(belief_id: str):
    """Get all constraints involving this belief."""
    return {
        "belief_id": belief_id,
        "constraints": [
            {"id": "C001", "target": "B002", "polarity": "POSITIVE", "strength": 0.82},
            {"id": "C002", "target": "B003", "polarity": "POSITIVE", "strength": 0.65},
        ]
    }


@beliefs_router.get("/{belief_id}/evidence")
async def get_belief_evidence(belief_id: str):
    """Get evidence sources for this belief."""
    return {
        "belief_id": belief_id,
        "evidence": [
            {"source": "Kaplan & Kaplan 1989", "type": "book", "contribution": "Foundational theory"},
            {"source": "Berman et al. 2008", "type": "article", "contribution": "Empirical validation"},
        ]
    }


# =============================================================================
# Queries Endpoints
# =============================================================================

@queries_router.post("/", response_model=QueryResponse)
async def execute_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Execute a natural language query.

    Modes:
    - quick: Headline only (fastest, cheapest)
    - standard: Headline + summary + implications
    - deep: Full trace with detailed explanation

    The query is processed through:
    1. Intent detection (fast model)
    2. Evidence retrieval (no LLM)
    3. Response synthesis (capable model)
    """
    query_id = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # TODO: Integrate with LLM Query Bridge
    # For now, return demo response
    return QueryResponse(
        query_id=query_id,
        status="complete",
        query=request.query,
        query_type="WHAT",
        causal_level="associational",
        headline="Plants are associated with stress reduction in office settings (credence: 0.72 ± 0.12)",
        summary={
            "finding": "Multiple studies show 15-25% reduction in self-reported stress",
            "confidence": "moderate",
            "key_evidence": ["Lohr 1996", "Bringslimark 2007", "Fjeld 2000"]
        },
        practical_implications=[
            "Minimum 1 plant per 10m² workspace",
            "Visible greenery more effective than hidden",
            "Real plants preferred over artificial"
        ],
        scope_conditions={
            "population": "Office workers, primarily Western countries",
            "setting": "Indoor office environments",
            "methodology": "Self-report surveys, some cortisol measurements",
            "limitations": "Limited hospital data, no long-term studies"
        },
        caveats=[
            "Limited evidence for hospital settings",
            "Cultural variations understudied"
        ],
        key_sources=["Lohr et al. (1996)", "Bringslimark et al. (2007)"],
        processing_time_ms=150,
        cost_estimate=0.02
    )


@queries_router.get("/{query_id}/results", response_model=QueryResponse)
async def get_query_results(query_id: str):
    """Get results for an async query."""
    # TODO: Implement async query storage
    raise HTTPException(status_code=404, detail=f"Query {query_id} not found")


@queries_router.get("/types")
async def get_query_types():
    """Get available query types and their descriptions."""
    return {
        "types": [
            {"type": "WHAT", "description": "What is X? What does Y show?", "causal_level": "associational"},
            {"type": "WHY", "description": "Why does X happen? What mechanism?", "causal_level": "associational"},
            {"type": "COMPARE", "description": "How does X compare to Y?", "causal_level": "associational"},
            {"type": "GAPS", "description": "What don't we know about X?", "causal_level": "associational"},
            {"type": "CONTRADICT", "description": "What contradicts X?", "causal_level": "associational"},
            {"type": "CONTINGENT", "description": "When does X apply?", "causal_level": "associational"},
            {"type": "HOW_CONFIDENT", "description": "How confident are we about X?", "causal_level": "associational"},
            {"type": "RELATED", "description": "What's related to X?", "causal_level": "associational"},
            {"type": "TRENDING", "description": "What's gaining/losing support?", "causal_level": "associational"},
            {"type": "CANONICAL", "description": "What's the seminal work on X?", "causal_level": "associational"},
        ]
    }


# =============================================================================
# Export Endpoints
# =============================================================================

@export_router.post("/", response_model=ExportResponse)
async def generate_export(request: ExportRequest):
    """
    Generate an export bundle.

    Purposes:
    - practitioner_briefing: Quick design guidance
    - literature_review: Academic synthesis with citations
    - systematic_review: PRISMA-compatible
    - data_pipeline: Machine-readable JSONL
    - presentation: Visual summaries
    """
    export_id = f"E{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # TODO: Integrate with ExportEngine
    return ExportResponse(
        export_id=export_id,
        topic=request.topic,
        purpose=request.purpose,
        generated_at=datetime.now().isoformat(),
        files={
            "summary.md": f"/api/v1/export/{export_id}/files/summary.md",
            "references.bib": f"/api/v1/export/{export_id}/files/references.bib"
        }
    )


@export_router.post("/bibtex")
async def export_bibtex(belief_ids: Optional[List[str]] = None):
    """Export BibTeX citations for specified beliefs or all."""
    # TODO: Integrate with ExportEngine
    bibtex = """@article{kaplan1989,
  author = {Kaplan, Rachel and Kaplan, Stephen},
  title = {{The Experience of Nature}},
  year = {1989},
}
"""
    return {"bibtex": bibtex}


@export_router.post("/summary")
async def export_summary(query: str, format: str = "markdown"):
    """Export evidence summary for a query."""
    # TODO: Integrate with ExportEngine
    return {"content": f"# Evidence Summary: {query}\n\n..."}


@export_router.get("/{export_id}/files/{filename}")
async def download_export_file(export_id: str, filename: str):
    """Download a specific file from an export bundle."""
    # TODO: Implement file storage and retrieval
    raise HTTPException(status_code=404, detail="Export file not found")


# =============================================================================
# Communities Endpoints
# =============================================================================

@communities_router.get("/", response_model=List[CommunityResponse])
async def list_communities():
    """List all epistemic communities."""
    return [
        CommunityResponse(
            id="art",
            name="Attention Restoration Theory (ART)",
            description="Theory that nature restores directed attention capacity",
            beliefs_count=156,
            average_credence=0.78,
            key_researchers=["R. Kaplan", "S. Kaplan", "M. Berman"]
        ),
        CommunityResponse(
            id="srt",
            name="Stress Recovery Theory (SRT)",
            description="Theory that nature triggers physiological stress recovery",
            beliefs_count=142,
            average_credence=0.72,
            key_researchers=["R. Ulrich"]
        ),
        CommunityResponse(
            id="biophilia",
            name="Biophilia Hypothesis",
            description="Innate human affiliation with nature",
            beliefs_count=234,
            average_credence=0.68,
            key_researchers=["E.O. Wilson", "S. Kellert"]
        ),
        CommunityResponse(
            id="env_psych",
            name="Environmental Psychology",
            description="Study of person-environment transactions",
            beliefs_count=312,
            average_credence=0.65,
            key_researchers=["D. Stokols", "I. Altman"]
        ),
    ]


@communities_router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(community_id: str):
    """Get details for a specific community."""
    communities = await list_communities()
    for c in communities:
        if c.id == community_id:
            return c
    raise HTTPException(status_code=404, detail=f"Community {community_id} not found")


@communities_router.get("/{community_id}/beliefs")
async def get_community_beliefs(
    community_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Get beliefs associated with a community."""
    # TODO: Integrate with actual data
    return {
        "community_id": community_id,
        "beliefs": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


# =============================================================================
# Constraints Endpoints
# =============================================================================

@constraints_router.get("/")
async def list_constraints(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    polarity: Optional[str] = Query(default=None, pattern="^(POSITIVE|NEGATIVE)$")
):
    """List epistemic constraints."""
    return {
        "constraints": [
            ConstraintResponse(
                id="C001",
                from_belief="B001",
                to_belief="B002",
                polarity="POSITIVE",
                strength=0.82,
                reason="ART supports plant stress reduction"
            ),
            ConstraintResponse(
                id="C002",
                from_belief="B002",
                to_belief="B005",
                polarity="NEGATIVE",
                strength=0.89,
                reason="Real vs artificial plants conflict"
            ),
        ],
        "total": 2,
        "limit": limit,
        "offset": offset
    }


@constraints_router.get("/{constraint_id}", response_model=ConstraintResponse)
async def get_constraint(constraint_id: str):
    """Get details for a specific constraint."""
    # TODO: Integrate with actual data
    raise HTTPException(status_code=404, detail=f"Constraint {constraint_id} not found")


# =============================================================================
# Papers Endpoints
# =============================================================================

@papers_router.get("/", response_model=List[PaperResponse])
async def list_papers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None)
):
    """List source papers."""
    return [
        PaperResponse(
            id="P001",
            title="The Experience of Nature: A Psychological Perspective",
            authors=["Kaplan, R.", "Kaplan, S."],
            year=1989,
            beliefs_extracted=23,
            status="complete"
        ),
        PaperResponse(
            id="P002",
            title="View Through a Window May Influence Recovery from Surgery",
            authors=["Ulrich, R.S."],
            year=1984,
            journal="Science",
            doi="10.1126/science.6143402",
            beliefs_extracted=8,
            status="complete"
        ),
    ]


@papers_router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str):
    """Get details for a specific paper."""
    papers = await list_papers()
    for p in papers:
        if p.id == paper_id:
            return p
    raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")


# =============================================================================
# Admin Endpoints
# =============================================================================

@admin_router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system-wide statistics."""
    return SystemStats(
        total_beliefs=1247,
        total_constraints=3891,
        total_papers=312,
        total_communities=4,
        overall_coherence=0.72,
        average_credence=0.68,
        contested_beliefs=231,
        stub_beliefs=142,
        last_updated=datetime.now().isoformat()
    )


@admin_router.get("/health", response_model=HealthResponse)
async def get_health():
    """Get system health status."""
    return HealthResponse(
        status="healthy",
        api_version="v1",
        uptime_seconds=3600,
        checks={
            "database": {"status": "ok", "latency_ms": 5},
            "llm_service": {"status": "ok", "provider": "anthropic"},
            "cache": {"status": "ok", "hit_rate": 0.85},
        }
    )


@admin_router.get("/activity")
async def get_recent_activity(limit: int = Query(default=10, ge=1, le=50)):
    """Get recent system activity."""
    return {
        "activities": [
            {"type": "belief_added", "description": "Plants reduce cognitive load", "timestamp": datetime.now().isoformat()},
            {"type": "constraint_added", "description": "ART → attention restoration", "timestamp": datetime.now().isoformat()},
        ]
    }


# =============================================================================
# Router Aggregation
# =============================================================================

def get_unified_router() -> APIRouter:
    """Get the unified API router with all sub-routers."""
    router = APIRouter(prefix="/api/v1")

    router.include_router(beliefs_router)
    router.include_router(queries_router)
    router.include_router(export_router)
    router.include_router(communities_router)
    router.include_router(constraints_router)
    router.include_router(papers_router)
    router.include_router(admin_router)

    return router


# Convenience export
unified_router = get_unified_router()
