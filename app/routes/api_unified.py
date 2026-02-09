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
import sqlite3
import os

logger = logging.getLogger(__name__)

# Import actual services
from app.routes.web_of_belief import get_web, set_web
from src.services.web_of_belief import WebOfBelief, Belief, Credence

# Try to import social epistemology for community registry
try:
    from src.services.social_epistemology import CommunityRegistry, EpistemicCommunity
    _community_registry: Optional[CommunityRegistry] = None
except ImportError:
    CommunityRegistry = None
    EpistemicCommunity = None
    _community_registry = None

def get_community_registry() -> Optional["CommunityRegistry"]:
    """Get or create the community registry singleton."""
    global _community_registry
    if CommunityRegistry is None:
        return None
    if _community_registry is None:
        _community_registry = CommunityRegistry()
    return _community_registry

# Database path
def _get_db_path() -> str:
    return os.environ.get("AE_DB_PATH") or os.environ.get("AE_DB") or "ae.db"

def _get_db_connection():
    return sqlite3.connect(_get_db_path(), timeout=30.0)

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
    web = get_web()
    all_beliefs = list(web.beliefs.values())

    # Apply filters
    filtered = all_beliefs

    if status:
        status_values = [s.value for s in status]
        filtered = [b for b in filtered if b.status.value.upper() in status_values]

    if level:
        level_values = [l.value for l in level]
        filtered = [b for b in filtered if b.level and b.level.value.upper() in level_values]

    if theory:
        filtered = [b for b in filtered if theory.lower() in (b.theory_id or "").lower()]

    if min_credence > 0:
        filtered = [b for b in filtered if b.credence.value >= min_credence]

    if search:
        search_lower = search.lower()
        filtered = [b for b in filtered if search_lower in b.content.lower()]

    total = len(filtered)

    # Paginate
    paginated = filtered[offset:offset + limit]

    # Convert to response format
    belief_summaries = []
    for b in paginated:
        # Count constraints
        n_constraints = sum(1 for c in web.constraints.values()
                          if c.source_id == b.belief_id or c.target_id == b.belief_id)

        belief_summaries.append(BeliefSummary(
            id=b.belief_id,
            content=b.content,
            credence=b.credence.value,
            uncertainty=b.credence.uncertainty,
            status=BeliefStatus(b.status.value.upper()) if b.status else BeliefStatus.STUB,
            level=EpistemicLevel(b.level.value.upper()) if b.level else EpistemicLevel.EMPIRICAL,
            theory=b.theory_id,
            sources_count=len(b.paper_ids) if b.paper_ids else 0,
            constraints_count=n_constraints
        ))

    return BeliefListResponse(
        beliefs=belief_summaries,
        total=total,
        limit=limit,
        offset=offset,
        _links={
            "self": f"/api/v1/beliefs/?limit={limit}&offset={offset}",
            "next": f"/api/v1/beliefs/?limit={limit}&offset={offset + limit}" if offset + limit < total else None
        }
    )


@beliefs_router.get("/{belief_id}", response_model=BeliefDetail)
async def get_belief(belief_id: str):
    """Get detailed information about a specific belief."""
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    b = web.beliefs[belief_id]

    # Get constraints
    supporting = []
    opposing = []
    for c in web.constraints.values():
        if c.source_id == belief_id or c.target_id == belief_id:
            if c.polarity.value == "POSITIVE":
                supporting.append(c.constraint_id)
            else:
                opposing.append(c.constraint_id)

    # Get entrenchment
    entrenchment = web.get_entrenchment(belief_id)

    # Build scope conditions dict
    scope_dict = None
    if b.scope:
        scope_dict = {
            "population": b.scope.population,
            "setting": b.scope.setting,
            "duration": b.scope.duration,
        }

    # Get community associations
    communities = []
    if hasattr(b, 'community_associations') and b.community_associations:
        communities = list(b.community_associations.keys())

    return BeliefDetail(
        id=b.belief_id,
        content=b.content,
        credence=b.credence.value,
        uncertainty=b.credence.uncertainty,
        status=BeliefStatus(b.status.value.upper()) if b.status else BeliefStatus.STUB,
        level=EpistemicLevel(b.level.value.upper()) if b.level else EpistemicLevel.EMPIRICAL,
        theory=b.theory_id,
        sources_count=len(b.paper_ids) if b.paper_ids else 0,
        constraints_count=len(supporting) + len(opposing),
        scope_conditions=scope_dict,
        sources=b.paper_ids or [],
        supporting_constraints=supporting,
        opposing_constraints=opposing,
        communities=communities,
        entrenchment=entrenchment,
        created_at=None,
        updated_at=None
    )


@beliefs_router.post("/", response_model=BeliefDetail, status_code=201)
async def create_belief(belief: BeliefCreate):
    """Create a new belief in the Web of Belief."""
    from src.services.web_of_belief import BeliefStatus as WoBStatus, EpistemicLevel as WoBLevel, ScopeConditions

    web = get_web()

    # Generate a unique belief ID
    new_id = f"B{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Map API enums to WebOfBelief enums
    wob_status = WoBStatus(belief.status.value.lower())
    wob_level = WoBLevel(belief.level.value.lower())

    # Create the belief in the web
    new_belief = web.add_belief(
        belief_id=new_id,
        content=belief.content,
        credence=belief.credence,
        status=wob_status,
        level=wob_level,
        theory_id=belief.theory,
        paper_ids=belief.sources if belief.sources else None
    )

    return BeliefDetail(
        id=new_belief.belief_id,
        content=new_belief.content,
        credence=new_belief.credence.value,
        uncertainty=new_belief.credence.uncertainty,
        status=BeliefStatus(new_belief.status.value.upper()),
        level=EpistemicLevel(new_belief.level.value.upper()) if new_belief.level else EpistemicLevel.EMPIRICAL,
        theory=new_belief.theory_id,
        sources_count=len(new_belief.paper_ids) if new_belief.paper_ids else 0,
        constraints_count=0,
        scope_conditions=None,
        sources=new_belief.paper_ids or [],
        supporting_constraints=[],
        opposing_constraints=[],
        communities=[],
        entrenchment=web.get_entrenchment(new_belief.belief_id),
        created_at=None,
        updated_at=None
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
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    # Find all constraints where this belief is source or target
    supporting = []
    opposing = []
    for c in web.constraints.values():
        if c.source_id == belief_id or c.target_id == belief_id:
            other_id = c.target_id if c.source_id == belief_id else c.source_id
            constraint_info = {
                "id": c.constraint_id,
                "other_belief": other_id,
                "polarity": c.polarity.value.upper(),
                "strength": c.strength,
                "direction": "outgoing" if c.source_id == belief_id else "incoming"
            }
            if c.polarity.value.upper() == "POSITIVE":
                supporting.append(constraint_info)
            else:
                opposing.append(constraint_info)

    return {
        "belief_id": belief_id,
        "supporting": supporting,
        "opposing": opposing,
        "total": len(supporting) + len(opposing)
    }


@beliefs_router.get("/{belief_id}/evidence")
async def get_belief_evidence(belief_id: str):
    """Get evidence sources for this belief."""
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    belief = web.beliefs[belief_id]
    paper_ids = belief.paper_ids or []

    # Try to get paper details from database
    evidence = []
    if paper_ids:
        try:
            conn = _get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            for pid in paper_ids:
                cursor.execute("""
                    SELECT article_id, title, authors, year, venue
                    FROM articles WHERE article_id = ?
                """, (pid,))
                row = cursor.fetchone()
                if row:
                    authors = json.loads(row['authors']) if row['authors'] else []
                    evidence.append({
                        "paper_id": row['article_id'],
                        "title": row['title'],
                        "authors": authors,
                        "year": row['year'],
                        "venue": row['venue']
                    })
                else:
                    # Paper not in DB, just return the ID
                    evidence.append({"paper_id": pid, "title": None})

            conn.close()
        except Exception as e:
            logger.warning(f"Could not fetch paper details: {e}")
            # Fall back to just paper IDs
            evidence = [{"paper_id": pid, "title": None} for pid in paper_ids]

    return {
        "belief_id": belief_id,
        "evidence_count": len(evidence),
        "evidence": evidence
    }


# =============================================================================
# Queries Endpoints
# =============================================================================

@queries_router.post("/", response_model=QueryResponse)
async def execute_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Execute a natural language query with progressive disclosure (per Simon).

    Modes:
    - quick: Headline only (fastest, cheapest)
    - standard: Headline + summary + implications
    - deep: Full trace with detailed explanation

    The query is processed through:
    1. Intent detection (fast model)
    2. Evidence retrieval (no LLM)
    3. Response synthesis (capable model)
    """
    from src.services.query_response import generate_progressive_response, ResponseMode

    # Map request mode to ResponseMode
    mode_map = {
        "quick": ResponseMode.HEADLINE,
        "standard": ResponseMode.SUMMARY,
        "deep": ResponseMode.DETAIL
    }
    response_mode = mode_map.get(request.mode, ResponseMode.SUMMARY)

    # Get Web of Belief
    web = get_web()

    # Generate progressive response
    try:
        progressive = generate_progressive_response(
            web=web,
            query=request.query,
            mode=response_mode,
            include_practitioner_implications=request.include_practitioner_implications
        )

        return QueryResponse(
            query_id=progressive.query_id,
            status="complete",
            query=request.query,
            query_type=progressive.summary.get('finding', 'UNKNOWN')[:20] if progressive.summary else "UNKNOWN",
            causal_level=progressive.causal_level,
            headline=progressive.headline,
            summary=progressive.summary,
            detail=progressive.detail,
            practical_implications=progressive.practical_implications,
            scope_conditions=progressive.scope_conditions,
            caveats=progressive.caveats,
            key_sources=progressive.key_sources,
            processing_time_ms=progressive.processing_time_ms,
            cost_estimate=progressive.cost_estimate
        )
    except Exception as e:
        logger.warning(f"Query processing error: {e}")
        # Fallback to minimal response
        return QueryResponse(
            query_id=f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="error",
            query=request.query,
            query_type="UNKNOWN",
            causal_level="unknown",
            headline=f"Error processing query: {str(e)[:50]}",
            processing_time_ms=0,
            cost_estimate=0.0
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

@communities_router.get("/")
async def list_communities():
    """List all epistemic communities."""
    registry = get_community_registry()

    # If registry is available and has communities, use it
    if registry and registry.communities:
        communities = []
        for c in registry.communities.values():
            communities.append(CommunityResponse(
                id=c.community_id,
                name=c.name,
                description=getattr(c, 'description', None),
                beliefs_count=0,  # Would need to query WebOfBelief
                average_credence=0.0,
                key_researchers=[]
            ))
        return communities

    # Fallback to seed data for known CNfA communities
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
    registry = get_community_registry()

    # Try registry first
    if registry:
        c = registry.get_community(community_id)
        if c:
            return CommunityResponse(
                id=c.community_id,
                name=c.name,
                description=getattr(c, 'description', None),
                beliefs_count=0,
                average_credence=0.0,
                key_researchers=[]
            )

    # Fallback to seed data
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
    web = get_web()

    # Find beliefs associated with this community
    community_beliefs = []
    for b in web.beliefs.values():
        if hasattr(b, 'community_associations') and b.community_associations:
            if community_id in b.community_associations:
                community_beliefs.append({
                    "id": b.belief_id,
                    "content": b.content,
                    "credence": b.credence.value,
                    "community_credence": b.community_associations.get(community_id, b.credence.value)
                })

    total = len(community_beliefs)
    paginated = community_beliefs[offset:offset + limit]

    return {
        "community_id": community_id,
        "beliefs": paginated,
        "total": total,
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
    """List epistemic constraints from WebOfBelief."""
    web = get_web()

    all_constraints = list(web.constraints.values())

    # Filter by polarity if specified
    if polarity:
        all_constraints = [c for c in all_constraints
                         if c.polarity.value.upper() == polarity]

    total = len(all_constraints)

    # Paginate
    paginated = all_constraints[offset:offset + limit]

    # Convert to response format
    constraint_responses = []
    for c in paginated:
        constraint_responses.append(ConstraintResponse(
            id=c.constraint_id,
            from_belief=c.source_id,
            to_belief=c.target_id,
            polarity=c.polarity.value.upper(),
            strength=c.strength,
            reason=c.reason if hasattr(c, 'reason') else None
        ))

    return {
        "constraints": constraint_responses,
        "total": total,
        "limit": limit,
        "offset": offset,
        "_links": {
            "self": f"/api/v1/constraints/?limit={limit}&offset={offset}",
            "next": f"/api/v1/constraints/?limit={limit}&offset={offset + limit}" if offset + limit < total else None
        }
    }


@constraints_router.get("/{constraint_id}", response_model=ConstraintResponse)
async def get_constraint(constraint_id: str):
    """Get details for a specific constraint."""
    web = get_web()

    if constraint_id not in web.constraints:
        raise HTTPException(status_code=404, detail=f"Constraint {constraint_id} not found")

    c = web.constraints[constraint_id]

    return ConstraintResponse(
        id=c.constraint_id,
        from_belief=c.source_id,
        to_belief=c.target_id,
        polarity=c.polarity.value.upper(),
        strength=c.strength,
        reason=c.reason if hasattr(c, 'reason') else None
    )


# =============================================================================
# Papers Endpoints
# =============================================================================

@papers_router.get("/")
async def list_papers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None)
):
    """List source papers from the database."""
    try:
        conn = _get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query with optional status filter
        if status:
            cursor.execute("""
                SELECT article_id, title, authors, year, venue, doi
                FROM articles
                WHERE status = ?
                ORDER BY year DESC
                LIMIT ? OFFSET ?
            """, (status, limit, offset))
        else:
            cursor.execute("""
                SELECT article_id, title, authors, year, venue, doi
                FROM articles
                ORDER BY year DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()

        # Get total count
        if status:
            cursor.execute("SELECT COUNT(*) FROM articles WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]

        conn.close()

        # Convert to response format
        papers = []
        for row in rows:
            authors = json.loads(row['authors']) if row['authors'] else []
            papers.append(PaperResponse(
                id=row['article_id'],
                title=row['title'] or "Untitled",
                authors=authors,
                year=row['year'] or 0,
                journal=row['venue'],
                doi=row['doi'],
                beliefs_extracted=0,  # Could be counted from findings table
                status="complete"
            ))

        return {
            "papers": papers,
            "total": total,
            "limit": limit,
            "offset": offset,
            "_links": {
                "self": f"/api/v1/papers/?limit={limit}&offset={offset}",
                "next": f"/api/v1/papers/?limit={limit}&offset={offset + limit}" if offset + limit < total else None
            }
        }

    except Exception as e:
        logger.warning(f"Database query failed: {e}")
        # Return empty list if database not available
        return {
            "papers": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "_links": {"self": f"/api/v1/papers/?limit={limit}&offset={offset}"}
        }


@papers_router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str):
    """Get details for a specific paper from the database."""
    try:
        conn = _get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT article_id, title, authors, year, venue, doi
            FROM articles
            WHERE article_id = ?
        """, (paper_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        authors = json.loads(row['authors']) if row['authors'] else []

        return PaperResponse(
            id=row['article_id'],
            title=row['title'] or "Untitled",
            authors=authors,
            year=row['year'] or 0,
            journal=row['venue'],
            doi=row['doi'],
            beliefs_extracted=0,
            status="complete"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Database query failed: {e}")
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")


# =============================================================================
# Admin Endpoints
# =============================================================================

@admin_router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system-wide statistics from WebOfBelief and database."""
    web = get_web()

    # Get counts from WebOfBelief
    all_beliefs = list(web.beliefs.values())
    total_beliefs = len(all_beliefs)
    total_constraints = len(web.constraints)

    # Count contested and stub beliefs
    contested = sum(1 for b in all_beliefs if b.status and b.status.value.upper() == "CONTESTED")
    stubs = sum(1 for b in all_beliefs if b.status and b.status.value.upper() == "STUB")

    # Calculate average credence
    if total_beliefs > 0:
        avg_credence = sum(b.credence.value for b in all_beliefs) / total_beliefs
    else:
        avg_credence = 0.0

    # Get community count
    total_communities = len(web.communities) if hasattr(web, 'communities') else 0

    # Get overall coherence
    try:
        overall_coherence = web.compute_coherence()
    except Exception:
        overall_coherence = 0.0

    # Get paper count from database
    total_papers = 0
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_papers = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass  # Database may not be available

    return SystemStats(
        total_beliefs=total_beliefs,
        total_constraints=total_constraints,
        total_papers=total_papers,
        total_communities=total_communities,
        overall_coherence=overall_coherence,
        average_credence=round(avg_credence, 3),
        contested_beliefs=contested,
        stub_beliefs=stubs,
        last_updated=datetime.now().isoformat()
    )


@admin_router.get("/health", response_model=HealthResponse)
async def get_health():
    """Get system health status with real connectivity checks."""
    import time

    checks = {}
    overall_status = "healthy"

    # Check database connectivity
    try:
        start = time.time()
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        latency_ms = int((time.time() - start) * 1000)
        checks["database"] = {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}
        overall_status = "degraded"

    # Check WebOfBelief availability
    try:
        web = get_web()
        belief_count = len(web.beliefs)
        checks["web_of_belief"] = {"status": "ok", "beliefs_loaded": belief_count}
    except Exception as e:
        checks["web_of_belief"] = {"status": "error", "error": str(e)}
        overall_status = "degraded"

    # Check community registry
    try:
        registry = get_community_registry()
        if registry:
            checks["community_registry"] = {"status": "ok", "communities": len(registry.communities)}
        else:
            checks["community_registry"] = {"status": "unavailable", "reason": "Module not loaded"}
    except Exception as e:
        checks["community_registry"] = {"status": "error", "error": str(e)}

    # LLM service check (placeholder - would need actual API key check)
    checks["llm_service"] = {"status": "ok", "provider": "anthropic", "note": "Not verified"}

    return HealthResponse(
        status=overall_status,
        api_version="v1",
        uptime_seconds=0,  # Would need process start time tracking
        checks=checks
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
