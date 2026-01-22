"""
Query API Routes
================

API routes for natural language query processing.

Per expert panel:
- Show vocabulary expansion transparently (Bates)
- Exactly 3 follow-ups: deeper, broader, uncertainty (Simon)
- Abstract-only caution badges (Cartwright)

Date: January 21, 2026
Phase C Sprint C4
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

from src.services.query_parser import (
    QueryParser, parse_query, QueryType, QueryIntent, ParseResult
)
from src.services.query_response import (
    QueryResponseGenerator, QueryResponse, ResponseType, generate_response
)
from src.services.web_of_belief import WebOfBelief


router = APIRouter(prefix="/api/query", tags=["query"])


# =============================================================================
# Request/Response Models
# =============================================================================

class QueryRequest(BaseModel):
    """Request to process a natural language query."""
    query: str = Field(..., description="Natural language query", min_length=3)
    include_expansions: bool = Field(
        True, description="Include vocabulary expansions in response"
    )
    max_evidence: int = Field(
        10, ge=1, le=50, description="Maximum evidence items to return"
    )


class ParsedQueryResponse(BaseModel):
    """Response from parsing a query (without searching beliefs)."""
    query_type: str
    subject: Optional[str]
    object: Optional[str]
    confidence: float
    subject_expansions: List[str]
    object_expansions: List[str]
    needs_clarification: bool
    clarification_options: List[str]
    alternatives: List[Dict[str, Any]]


class EvidenceItemResponse(BaseModel):
    """Single piece of evidence in response."""
    belief_id: str
    content: str
    credence: float
    source_depth: str
    paper_ids: List[str]
    is_causal: bool
    needs_caution: bool


class FollowUpResponse(BaseModel):
    """A suggested follow-up question with executable query."""
    question: str
    type: str
    rationale: str
    query_url: Optional[str] = None
    query_params: Dict[str, Any] = Field(default_factory=dict)


class ContestedEvidenceResponse(BaseModel):
    """
    H5: Contested evidence section with opposing views grouped.

    Per Cartwright/Simon panel: Critical for epistemic transparency.
    """
    topic: str
    supporting: List[EvidenceItemResponse]
    contradicting: List[EvidenceItemResponse]
    summary: str
    reasons_for_disagreement: List[str]


class FullQueryResponse(BaseModel):
    """Complete response to a query."""
    # Query understanding
    query_type: str
    subject: Optional[str]
    object: Optional[str]
    confidence: float

    # Response content
    response_type: str
    summary: str
    confidence_level: str

    # Evidence
    evidence_items: List[EvidenceItemResponse]
    total_supporting: int
    total_contradicting: int
    is_contested: bool

    # Warnings
    abstract_only_warning: bool
    warnings: List[str] = Field(default_factory=list)

    # H5: Contested evidence section (per Cartwright/Simon panel)
    contested_evidence: Optional[ContestedEvidenceResponse] = None

    # Follow-ups (exactly 3)
    follow_ups: List[FollowUpResponse]

    # Vocabulary (per Bates: transparent)
    vocabulary_used: Dict[str, List[str]]

    # Scope
    scope_conditions: Optional[Dict[str, Any]]
    enabling_conditions: Optional[Dict[str, Any]]


class QuerySuggestion(BaseModel):
    """A suggested query for users."""
    query: str
    description: str
    category: str


# =============================================================================
# Shared Web Instance (F-Sprint Fix: centralized per Lamport)
# =============================================================================
# Import from web_of_belief.py to share single instance across all routes

from app.routes.web_of_belief import get_web, set_web


# =============================================================================
# API Routes
# =============================================================================

@router.post("/parse", response_model=ParsedQueryResponse)
async def parse_query_endpoint(request: QueryRequest):
    """
    Parse a query without searching for evidence.

    Use this to understand how the system interprets a query
    before running a full search.
    """
    result = parse_query(request.query)
    primary = result.primary

    alternatives = [
        {
            'query_type': alt.query_type.value,
            'subject': alt.subject,
            'object': alt.object,
            'confidence': alt.confidence
        }
        for alt in result.alternatives
    ]

    return ParsedQueryResponse(
        query_type=primary.query_type.value,
        subject=primary.subject,
        object=primary.object,
        confidence=primary.confidence,
        subject_expansions=primary.subject_expansions,
        object_expansions=primary.object_expansions,
        needs_clarification=result.needs_clarification,
        clarification_options=result.clarification_options,
        alternatives=alternatives
    )


@router.post("/search", response_model=FullQueryResponse)
async def search_query(request: QueryRequest):
    """
    Process a natural language query and return evidence.

    This is the main query endpoint that:
    1. Parses the query to understand intent
    2. Expands vocabulary for better matching
    3. Searches the web of belief for relevant evidence
    4. Returns structured response with follow-ups
    """
    web = get_web()

    # Parse query
    parse_result = parse_query(request.query)
    intent = parse_result.primary

    # Generate response
    generator = QueryResponseGenerator(web)
    response = generator.generate(parse_result)

    # Build warnings list
    warnings = []
    if response.abstract_only_warning:
        warnings.append(
            "Some evidence is from abstracts only. "
            "Causal claims from abstracts require verification (Cartwright)."
        )
    if response.is_contested:
        warnings.append(
            "This topic has contested evidence. "
            "Consider exploring alternative viewpoints."
        )

    # Build evidence items (limited to max_evidence)
    evidence_items = [
        EvidenceItemResponse(
            belief_id=e.belief_id,
            content=e.content,
            credence=e.credence,
            source_depth=e.source_depth,
            paper_ids=e.paper_ids,
            is_causal=e.is_causal,
            needs_caution=e.needs_caution
        )
        for e in response.evidence_items[:request.max_evidence]
    ]

    # Build follow-ups (exactly 3) with clickable query URLs (H4)
    follow_ups = [
        FollowUpResponse(
            question=f.question,
            type=f.type,
            rationale=f.rationale,
            query_url=f.query_url,
            query_params=f.query_params
        )
        for f in response.follow_ups
    ]

    # H5: Build contested evidence section if present
    contested_evidence_response = None
    if response.contested_evidence:
        ce = response.contested_evidence
        contested_evidence_response = ContestedEvidenceResponse(
            topic=ce.topic,
            supporting=[
                EvidenceItemResponse(
                    belief_id=e.belief_id,
                    content=e.content,
                    credence=e.credence,
                    source_depth=e.source_depth,
                    paper_ids=e.paper_ids,
                    is_causal=e.is_causal,
                    needs_caution=e.needs_caution
                ) for e in ce.supporting
            ],
            contradicting=[
                EvidenceItemResponse(
                    belief_id=e.belief_id,
                    content=e.content,
                    credence=e.credence,
                    source_depth=e.source_depth,
                    paper_ids=e.paper_ids,
                    is_causal=e.is_causal,
                    needs_caution=e.needs_caution
                ) for e in ce.contradicting
            ],
            summary=ce.summary,
            reasons_for_disagreement=ce.reasons_for_disagreement
        )

    return FullQueryResponse(
        # Query understanding
        query_type=intent.query_type.value,
        subject=intent.subject,
        object=intent.object,
        confidence=intent.confidence,

        # Response content
        response_type=response.response_type.value,
        summary=response.summary,
        confidence_level=response.confidence_level,

        # Evidence
        evidence_items=evidence_items,
        total_supporting=response.total_supporting,
        total_contradicting=response.total_contradicting,
        is_contested=response.is_contested,

        # Warnings
        abstract_only_warning=response.abstract_only_warning,
        warnings=warnings,

        # H5: Contested evidence
        contested_evidence=contested_evidence_response,

        # Follow-ups
        follow_ups=follow_ups,

        # Vocabulary
        vocabulary_used=response.vocabulary_used if request.include_expansions else {},

        # Scope
        scope_conditions=response.scope_conditions,
        enabling_conditions=response.enabling_conditions
    )


@router.get("/types", response_model=Dict[str, str])
async def get_query_types():
    """Get all supported query types with descriptions."""
    return {
        "what_is": "What is the effect of X on Y?",
        "does_affect": "Does X affect Y?",
        "how_much": "How much does X affect Y?",
        "what_do_we_know": "What do we know about X?",
        "what_evidence": "What evidence supports/contradicts X?",
        "compare": "Compare X and Y",
        "which_is_better": "Which is better, X or Y?",
        "how_confident": "How confident are we about X?",
        "why_believe": "Why do we believe X?",
        "what_contradicts": "What contradicts X?",
        "what_dont_know": "What don't we know about X?",
        "when_does": "When does X work?",
        "for_whom": "For whom does X work?",
    }


@router.get("/suggestions", response_model=List[QuerySuggestion])
async def get_query_suggestions():
    """Get suggested queries for exploring the evidence base."""
    return [
        # Effects queries
        QuerySuggestion(
            query="Does natural light affect productivity?",
            description="Explore the relationship between daylight and work output",
            category="effects"
        ),
        QuerySuggestion(
            query="What is the effect of plants on stress?",
            description="Investigate biophilic design and wellbeing",
            category="effects"
        ),
        QuerySuggestion(
            query="How much does temperature affect cognitive performance?",
            description="Quantify thermal comfort impacts",
            category="effects"
        ),

        # Knowledge queries
        QuerySuggestion(
            query="What do we know about open offices?",
            description="Survey evidence on open plan workspaces",
            category="knowledge"
        ),
        QuerySuggestion(
            query="What evidence supports biophilic design?",
            description="Review the evidence base for nature in buildings",
            category="knowledge"
        ),

        # Uncertainty queries
        QuerySuggestion(
            query="What don't we know about noise and focus?",
            description="Identify gaps in acoustic research",
            category="uncertainty"
        ),
        QuerySuggestion(
            query="How confident are we about natural light effects?",
            description="Assess confidence in daylight research",
            category="uncertainty"
        ),

        # Scope queries
        QuerySuggestion(
            query="For whom does thermal comfort matter most?",
            description="Explore population-specific effects",
            category="scope"
        ),
        QuerySuggestion(
            query="When does biophilic design work?",
            description="Understand boundary conditions",
            category="scope"
        ),

        # Comparison queries
        QuerySuggestion(
            query="Compare natural and artificial light",
            description="Contrast different lighting approaches",
            category="comparison"
        ),
    ]


@router.get("/vocabulary/{term}", response_model=Dict[str, Any])
async def expand_vocabulary(term: str):
    """
    Get vocabulary expansions for a term.

    Per Bates: vocabulary expansion should be transparent.
    """
    from src.services.query_parser import expand_term, VOCABULARY_BRIDGE

    expansions = expand_term(term)

    return {
        'term': term,
        'expansions': expansions,
        'note': 'These related terms are searched when you use the original term'
    }


@router.get("/history")
async def get_query_history():
    """
    Get recent query history (placeholder for session-based tracking).

    Note: In production, this would track per-session history.
    """
    return {
        'note': 'Query history tracking requires session management',
        'history': []
    }


# =============================================================================
# Stats and Health
# =============================================================================

@router.get("/stats")
async def get_query_stats():
    """Get statistics about query capabilities."""
    web = get_web()

    return {
        'beliefs_available': len(web.beliefs),
        'query_types_supported': len(QueryType) - 1,  # Exclude UNKNOWN
        'vocabulary_terms': 20,  # Approximate from VOCABULARY_BRIDGE
        'follow_ups_per_query': 3,  # Per Simon
    }
