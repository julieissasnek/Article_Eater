"""
Ingestion API Routes
====================

API routes for paper and belief ingestion.

Per expert panel:
- Track source depth (full_text, abstract, metadata) (Cartwright)
- Capture scope conditions (Kaplan)
- Support incremental belief addition (Simon)

Date: January 21, 2026
Phase C Sprint C3
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

from src.services.web_of_belief import (
    WebOfBelief, Belief, Credence, EpistemicLevel, SourceDepth,
    ScopeConditions, EnablingConditions
)


router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SourceDepthEnum(str, Enum):
    """Source depth levels."""
    FULL_TEXT = "full_text"
    ABSTRACT = "abstract"
    METADATA = "metadata"


class EpistemicLevelEnum(str, Enum):
    """Epistemic level options."""
    OBSERVATION = "observation"
    EMPIRICAL = "empirical"
    THEORETICAL = "theoretical"
    META_THEORETICAL = "meta_theoretical"


class ScopeConditionsModel(BaseModel):
    """Scope conditions for a belief."""
    population: Optional[str] = None
    setting: Optional[str] = None
    duration: Optional[str] = None
    scope_specified: bool = False


class EnablingConditionsModel(BaseModel):
    """Enabling conditions for a belief."""
    minimum_exposure: Optional[str] = None
    threshold: Optional[str] = None
    temporal_order: Optional[str] = None
    dose_response: Optional[str] = None


class PaperMetadata(BaseModel):
    """Metadata for a paper."""
    paper_id: str = Field(..., description="Unique paper identifier")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="Author names")
    year: Optional[int] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="DOI if available")
    journal: Optional[str] = Field(None, description="Journal name")
    source_depth: SourceDepthEnum = Field(
        SourceDepthEnum.ABSTRACT,
        description="What level of text we have access to"
    )
    abstract: Optional[str] = Field(None, description="Paper abstract")
    keywords: List[str] = Field(default_factory=list, description="Keywords")


class BeliefInput(BaseModel):
    """Input for adding a belief."""
    content: str = Field(..., description="The belief statement", min_length=10)
    credence: float = Field(0.5, ge=0.0, le=1.0, description="Initial credence (0-1)")
    credence_uncertainty: float = Field(0.2, ge=0.0, le=0.5, description="Uncertainty in credence")
    level: EpistemicLevelEnum = Field(
        EpistemicLevelEnum.EMPIRICAL,
        description="Epistemic level"
    )
    outcome_id: Optional[str] = Field(None, description="Related outcome category")
    paper_ids: List[str] = Field(default_factory=list, description="Source paper IDs")
    source_depth: SourceDepthEnum = Field(
        SourceDepthEnum.ABSTRACT,
        description="Source depth for this belief"
    )
    scope: Optional[ScopeConditionsModel] = Field(None, description="Scope conditions")
    enabling_conditions: Optional[EnablingConditionsModel] = Field(
        None, description="Enabling conditions"
    )
    is_causal: bool = Field(False, description="Whether this is a causal claim")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class PaperWithBeliefs(BaseModel):
    """Paper with associated beliefs for batch ingestion."""
    paper: PaperMetadata
    beliefs: List[BeliefInput] = Field(default_factory=list)


class AddBeliefResponse(BaseModel):
    """Response after adding a belief."""
    belief_id: str
    content: str
    credence: float
    added_at: str
    warnings: List[str] = Field(default_factory=list)


class AddPaperResponse(BaseModel):
    """Response after adding a paper."""
    paper_id: str
    title: str
    beliefs_added: int
    belief_ids: List[str]
    warnings: List[str] = Field(default_factory=list)


class IngestionStats(BaseModel):
    """Statistics about ingestion status."""
    total_papers: int
    total_beliefs: int
    beliefs_by_level: Dict[str, int]
    beliefs_by_source_depth: Dict[str, int]
    causal_claims: int
    abstract_only_causal: int  # Cartwright warning


# =============================================================================
# In-Memory Storage (would be database in production)
# =============================================================================

# Simple in-memory storage for papers
_papers: Dict[str, PaperMetadata] = {}

# F-Sprint Fix: Use centralized web instance per Lamport
from app.routes.web_of_belief import get_web, set_web


# =============================================================================
# API Routes
# =============================================================================

@router.post("/paper", response_model=AddPaperResponse)
async def add_paper(request: PaperWithBeliefs):
    """
    Add a new paper with optional beliefs.

    This is the primary ingestion endpoint for adding new research
    to the web of belief.
    """
    web = get_web()
    warnings = []
    belief_ids = []

    # Store paper metadata
    _papers[request.paper.paper_id] = request.paper

    # Add each belief
    for belief_input in request.beliefs:
        result = _add_belief_to_web(web, belief_input, request.paper.paper_id)
        belief_ids.append(result.belief_id)
        warnings.extend(result.warnings)

    return AddPaperResponse(
        paper_id=request.paper.paper_id,
        title=request.paper.title,
        beliefs_added=len(belief_ids),
        belief_ids=belief_ids,
        warnings=warnings
    )


@router.post("/belief", response_model=AddBeliefResponse)
async def add_belief(belief: BeliefInput):
    """
    Add a single belief to the web.

    Use this for adding beliefs from papers already in the system.
    """
    web = get_web()
    return _add_belief_to_web(web, belief)


@router.get("/papers", response_model=List[PaperMetadata])
async def list_papers():
    """Get list of all ingested papers."""
    return list(_papers.values())


@router.get("/paper/{paper_id}", response_model=PaperMetadata)
async def get_paper(paper_id: str):
    """Get metadata for a specific paper."""
    if paper_id not in _papers:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    return _papers[paper_id]


@router.get("/paper/{paper_id}/beliefs")
async def get_paper_beliefs(paper_id: str):
    """Get all beliefs from a specific paper."""
    if paper_id not in _papers:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    web = get_web()
    beliefs = []
    for belief in web.beliefs.values():
        if paper_id in belief.paper_ids:
            beliefs.append({
                'belief_id': belief.belief_id,
                'content': belief.content,
                'credence': belief.credence.value,
                'level': belief.level.value if belief.level else None,
                'source_depth': belief.source_depth.value if belief.source_depth else None
            })

    return {'paper_id': paper_id, 'beliefs': beliefs, 'count': len(beliefs)}


@router.get("/stats", response_model=IngestionStats)
async def get_ingestion_stats():
    """Get ingestion statistics."""
    web = get_web()

    # Count by epistemic level
    beliefs_by_level: Dict[str, int] = {}
    for belief in web.beliefs.values():
        level = belief.level.value if belief.level else "unknown"
        beliefs_by_level[level] = beliefs_by_level.get(level, 0) + 1

    # Count by source depth
    beliefs_by_source_depth: Dict[str, int] = {}
    for belief in web.beliefs.values():
        depth = belief.source_depth.value if belief.source_depth else "unknown"
        beliefs_by_source_depth[depth] = beliefs_by_source_depth.get(depth, 0) + 1

    # Count causal claims
    causal_keywords = ['cause', 'effect', 'affect', 'impact', 'influence',
                       'improve', 'reduce', 'increase', 'decrease', 'lead to']
    causal_claims = 0
    abstract_only_causal = 0

    for belief in web.beliefs.values():
        content_lower = belief.content.lower()
        is_causal = any(kw in content_lower for kw in causal_keywords)
        if is_causal:
            causal_claims += 1
            if belief.source_depth == SourceDepth.ABSTRACT:
                abstract_only_causal += 1

    return IngestionStats(
        total_papers=len(_papers),
        total_beliefs=len(web.beliefs),
        beliefs_by_level=beliefs_by_level,
        beliefs_by_source_depth=beliefs_by_source_depth,
        causal_claims=causal_claims,
        abstract_only_causal=abstract_only_causal
    )


@router.delete("/paper/{paper_id}")
async def delete_paper(paper_id: str):
    """
    Remove a paper and optionally its beliefs.

    Note: This is a soft delete per governance rules.
    """
    if paper_id not in _papers:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Remove paper metadata
    paper = _papers.pop(paper_id)

    # Note: We don't delete beliefs - they remain in the web
    # (governance: no deletions, only revisions)

    return {
        'deleted': paper_id,
        'title': paper.title,
        'note': 'Paper metadata removed. Beliefs remain in web per governance rules.'
    }


# =============================================================================
# Outcome Categories
# =============================================================================

# Standard outcome categories from CNFA domain
OUTCOME_CATEGORIES = {
    'productivity': 'Worker productivity and task performance',
    'cognition': 'Cognitive function and mental performance',
    'stress': 'Stress levels and anxiety',
    'wellbeing': 'General wellbeing and satisfaction',
    'health': 'Physical health outcomes',
    'creativity': 'Creative thinking and problem solving',
    'attention': 'Attention and concentration',
    'mood': 'Mood and emotional state',
    'sleep': 'Sleep quality and circadian rhythm',
    'social': 'Social interaction and collaboration',
    'recovery': 'Recovery from illness or fatigue',
    'perception': 'Perceptual processing and preferences'
}


@router.get("/outcome-categories")
async def get_outcome_categories():
    """Get available outcome categories for belief classification."""
    return OUTCOME_CATEGORIES


# =============================================================================
# Helper Functions
# =============================================================================

def _add_belief_to_web(
    web: WebOfBelief,
    belief_input: BeliefInput,
    paper_id: Optional[str] = None
) -> AddBeliefResponse:
    """Add a belief to the web and return response with warnings."""
    warnings = []

    # Generate belief ID
    import hashlib
    content_hash = hashlib.md5(belief_input.content.encode()).hexdigest()[:8]
    belief_id = f"b_{content_hash}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Convert enums
    level = EpistemicLevel(belief_input.level.value)
    source_depth = SourceDepth(belief_input.source_depth.value)

    # Build paper_ids list
    paper_ids = list(belief_input.paper_ids)
    if paper_id and paper_id not in paper_ids:
        paper_ids.append(paper_id)

    # Convert scope conditions
    scope = None
    if belief_input.scope:
        scope = ScopeConditions(
            population=belief_input.scope.population,
            setting=belief_input.scope.setting,
            duration=belief_input.scope.duration,
            scope_specified=belief_input.scope.scope_specified
        )

    # Convert enabling conditions
    enabling = None
    if belief_input.enabling_conditions:
        enabling = EnablingConditions(
            minimum_exposure=belief_input.enabling_conditions.minimum_exposure,
            threshold=belief_input.enabling_conditions.threshold,
            temporal_order=belief_input.enabling_conditions.temporal_order,
            dose_response=belief_input.enabling_conditions.dose_response
        )

    # Create belief
    belief = Belief(
        belief_id=belief_id,
        content=belief_input.content,
        level=level,
        credence=Credence(belief_input.credence, belief_input.credence_uncertainty),
        outcome_id=belief_input.outcome_id,
        paper_ids=paper_ids,
        source_depth=source_depth,
        scope=scope,
        enabling_conditions=enabling
    )

    # Check for Cartwright warning (abstract-only causal claim)
    if belief_input.is_causal and source_depth == SourceDepth.ABSTRACT:
        warnings.append(
            "CAUTION: This causal claim is based only on abstract. "
            "Full-text verification recommended (per Cartwright)."
        )

    # Check for causal keywords even if not marked as causal
    causal_keywords = ['cause', 'effect', 'affect', 'impact', 'influence',
                       'improve', 'reduce', 'increase', 'decrease', 'lead to']
    content_lower = belief_input.content.lower()
    has_causal_language = any(kw in content_lower for kw in causal_keywords)

    if has_causal_language and not belief_input.is_causal:
        warnings.append(
            "NOTE: Content contains causal language but is_causal=False. "
            "Consider marking as causal claim for proper tracking."
        )

    if has_causal_language and source_depth == SourceDepth.ABSTRACT:
        if not belief_input.is_causal:  # Only add if not already warned
            warnings.append(
                "CAUTION: Causal language detected in abstract-only belief. "
                "Full-text verification recommended (per Cartwright)."
            )

    # Add to web
    web.beliefs[belief_id] = belief

    return AddBeliefResponse(
        belief_id=belief_id,
        content=belief_input.content,
        credence=belief_input.credence,
        added_at=datetime.now().isoformat(),
        warnings=warnings
    )
