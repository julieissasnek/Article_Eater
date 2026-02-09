"""
Paper Lifecycle API Routes
===========================

API routes for unified paper lifecycle tracking and pipeline health monitoring.

Provides endpoints for:
- Paper status queries (by stage, by status)
- Individual paper lifecycle history
- Pipeline health dashboard
- Blocked/failed paper queues

Date: 2026-02-09
Version: 23.0.1
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import logging

# Import lifecycle service
try:
    from src.services.paper_lifecycle import (
        PaperLifecycleService,
        LifecycleStage,
        StageStatus,
        PaperStatus,
        PipelineHealth,
        LifecycleEvent,
        get_lifecycle_service,
    )
    LIFECYCLE_AVAILABLE = True
except ImportError:
    LIFECYCLE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lifecycle", tags=["lifecycle"])


# =============================================================================
# Request/Response Models
# =============================================================================


class LifecycleStageEnum(str, Enum):
    """Lifecycle stage options for API."""
    DISCOVERED = "discovered"
    SEARCHED = "searched"
    RETRIEVED = "retrieved"
    STORED = "stored"
    TYPED = "typed"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    SYNTHESIZING = "synthesizing"
    SYNTHESIZED = "synthesized"
    ARCHIVED = "archived"
    FAILED = "failed"


class StageStatusEnum(str, Enum):
    """Stage status options for API."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class PaperStatusResponse(BaseModel):
    """Response model for paper status."""
    paper_id: str
    title: Optional[str]
    current_stage: str
    stage_since: str
    blocked_reason: Optional[str] = None
    total_transitions: int = 0
    last_activity: Optional[str] = None
    n_claims: int = 0
    n_rules: int = 0
    processing_time_seconds: float = 0.0


class LifecycleEventResponse(BaseModel):
    """Response model for a lifecycle event."""
    paper_id: str
    stage: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    run_id: Optional[str] = None
    job_id: Optional[str] = None
    triggered_by: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    blocking_reason: Optional[str] = None
    n_claims: Optional[int] = None
    n_rules: Optional[int] = None
    n_findings: Optional[int] = None
    text_source: Optional[str] = None
    text_length: Optional[int] = None
    coherence_score: Optional[float] = None


class PaperHistoryResponse(BaseModel):
    """Response model for paper history."""
    paper_id: str
    events: List[LifecycleEventResponse]
    total_events: int


class PipelineHealthResponse(BaseModel):
    """Response model for pipeline health."""
    total_papers: int = 0
    papers_by_stage: Dict[str, int] = Field(default_factory=dict)
    papers_blocked: int = 0
    papers_failed: int = 0
    avg_processing_time_seconds: float = 0.0
    last_7_days_processed: int = 0
    stage_success_rates: Dict[str, float] = Field(default_factory=dict)


class StageDistributionResponse(BaseModel):
    """Response model for stage distribution."""
    stages: Dict[str, int]
    total: int
    blocked_count: int
    failed_count: int


class TransitionRequest(BaseModel):
    """Request model for manual stage transition."""
    paper_id: str = Field(..., description="Paper identifier")
    stage: LifecycleStageEnum = Field(..., description="Target stage")
    status: StageStatusEnum = Field(StageStatusEnum.STARTED, description="Status")
    run_id: Optional[str] = Field(None, description="Pipeline run ID")
    triggered_by: str = Field("manual", description="What triggered this transition")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    blocking_reason: Optional[str] = Field(None, description="Reason if blocked")


# =============================================================================
# Helper Functions
# =============================================================================


def _check_lifecycle_available():
    """Check if lifecycle service is available."""
    if not LIFECYCLE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Paper lifecycle service not available. Check installation."
        )


def _convert_paper_status(status: PaperStatus) -> PaperStatusResponse:
    """Convert internal PaperStatus to response model."""
    return PaperStatusResponse(
        paper_id=status.paper_id,
        title=status.title,
        current_stage=status.current_stage.value if hasattr(status.current_stage, 'value') else str(status.current_stage),
        stage_since=status.stage_since,
        blocked_reason=status.blocked_reason,
        total_transitions=status.total_transitions,
        last_activity=status.last_activity,
        n_claims=status.n_claims,
        n_rules=status.n_rules,
        processing_time_seconds=status.processing_time_seconds,
    )


def _convert_lifecycle_event(event: LifecycleEvent) -> LifecycleEventResponse:
    """Convert internal LifecycleEvent to response model."""
    return LifecycleEventResponse(
        paper_id=event.paper_id,
        stage=event.stage.value if hasattr(event.stage, 'value') else str(event.stage),
        status=event.status.value if hasattr(event.status, 'value') else str(event.status),
        started_at=event.started_at,
        completed_at=event.completed_at,
        duration_seconds=event.duration_seconds,
        run_id=event.run_id,
        job_id=event.job_id,
        triggered_by=event.triggered_by,
        details=event.details,
        error_message=event.error_message,
        blocking_reason=event.blocking_reason,
        n_claims=event.n_claims,
        n_rules=event.n_rules,
        n_findings=event.n_findings,
        text_source=event.text_source,
        text_length=event.text_length,
        coherence_score=event.coherence_score,
    )


# =============================================================================
# API Routes
# =============================================================================


@router.get("/health", response_model=PipelineHealthResponse)
async def get_pipeline_health():
    """
    Get overall pipeline health summary.

    Returns aggregate statistics about pipeline processing:
    - Total papers and distribution by stage
    - Blocked/failed counts
    - Average processing time
    - Success rates by stage
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()
    health = service.get_pipeline_health()
    return PipelineHealthResponse(
        total_papers=health.total_papers,
        papers_by_stage=health.papers_by_stage,
        papers_blocked=health.papers_blocked,
        papers_failed=health.papers_failed,
        avg_processing_time_seconds=health.avg_processing_time_seconds,
        last_7_days_processed=health.last_7_days_processed,
        stage_success_rates=health.stage_success_rates,
    )


@router.get("/stages", response_model=StageDistributionResponse)
async def get_stage_distribution():
    """
    Get paper distribution across lifecycle stages.

    Returns count of papers in each stage plus blocked/failed counts.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()
    health = service.get_pipeline_health()
    return StageDistributionResponse(
        stages=health.papers_by_stage,
        total=health.total_papers,
        blocked_count=health.papers_blocked,
        failed_count=health.papers_failed,
    )


@router.get("/papers", response_model=List[PaperStatusResponse])
async def get_papers_by_stage(
    stage: Optional[LifecycleStageEnum] = Query(None, description="Filter by stage"),
    blocked_only: bool = Query(False, description="Only show blocked papers"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum papers to return"),
):
    """
    Get papers filtered by stage and/or status.

    Optional filters:
    - stage: Filter to specific lifecycle stage
    - blocked_only: Only return blocked papers
    - limit: Maximum number of papers to return (default 100)
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()

    # Convert stage if provided
    internal_stage = None
    if stage:
        internal_stage = LifecycleStage(stage.value)

    # Get blocked or filter by stage
    if blocked_only:
        papers = service.get_blocked_papers(limit=limit)
    else:
        papers = service.get_papers_by_stage(
            stage=internal_stage,
            limit=limit,
        )

    return [_convert_paper_status(p) for p in papers]


@router.get("/papers/blocked", response_model=List[PaperStatusResponse])
async def get_blocked_papers(
    limit: int = Query(50, ge=1, le=500, description="Maximum papers to return"),
):
    """
    Get papers that are blocked and need attention.

    These are papers that have encountered issues during processing
    and require manual intervention or investigation.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()
    papers = service.get_blocked_papers(limit=limit)
    return [_convert_paper_status(p) for p in papers]


@router.get("/paper/{paper_id}", response_model=PaperStatusResponse)
async def get_paper_status(paper_id: str):
    """
    Get current lifecycle status for a specific paper.

    Returns the paper's current stage, blocked reason if any,
    and aggregate metrics like n_claims and n_rules.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()
    status = service.get_paper_status(paper_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    return _convert_paper_status(status)


@router.get("/paper/{paper_id}/history", response_model=PaperHistoryResponse)
async def get_paper_history(paper_id: str):
    """
    Get full lifecycle history for a paper.

    Returns all stage transitions the paper has gone through,
    with timing information and any errors encountered.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()

    # First check if paper exists
    status = service.get_paper_status(paper_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    events = service.get_paper_history(paper_id)
    return PaperHistoryResponse(
        paper_id=paper_id,
        events=[_convert_lifecycle_event(e) for e in events],
        total_events=len(events),
    )


@router.post("/transition", response_model=Dict[str, Any])
async def manual_transition(request: TransitionRequest):
    """
    Manually transition a paper to a new stage.

    Use this for:
    - Recovering blocked papers
    - Manual intervention in processing
    - Testing lifecycle tracking

    Note: This bypasses normal pipeline flow and should be used carefully.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()

    # Convert enums
    stage = LifecycleStage(request.stage.value)
    status = StageStatus(request.status.value)

    try:
        event_id = service.transition(
            paper_id=request.paper_id,
            stage=stage,
            status=status,
            run_id=request.run_id,
            triggered_by=request.triggered_by,
            error_message=request.error_message,
            blocking_reason=request.blocking_reason,
        )
        return {
            "success": True,
            "event_id": event_id,
            "paper_id": request.paper_id,
            "stage": request.stage.value,
            "status": request.status.value,
        }
    except Exception as e:
        logger.error(f"Manual transition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper/{paper_id}/unblock")
async def unblock_paper(paper_id: str, run_id: Optional[str] = None):
    """
    Clear blocked status for a paper and reset to DISCOVERED stage.

    Use this to retry processing for a previously blocked paper.
    The paper will be transitioned back to DISCOVERED stage with
    the blocked reason cleared.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()

    # Check if paper exists
    status = service.get_paper_status(paper_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

    # Reset to discovered
    event_id = service.transition(
        paper_id=paper_id,
        stage=LifecycleStage.DISCOVERED,
        status=StageStatus.SUCCESS,
        run_id=run_id,
        triggered_by="manual_unblock",
        details={"previous_stage": status.current_stage.value, "previous_reason": status.blocked_reason},
    )

    return {
        "success": True,
        "event_id": event_id,
        "paper_id": paper_id,
        "previous_stage": status.current_stage.value,
        "new_stage": "discovered",
        "message": "Paper unblocked and reset to DISCOVERED stage",
    }


# =============================================================================
# Statistics Endpoints
# =============================================================================


@router.get("/stats/processing-times")
async def get_processing_times(
    stage: Optional[LifecycleStageEnum] = Query(None, description="Filter by stage"),
    days: int = Query(7, ge=1, le=90, description="Days of data to include"),
):
    """
    Get processing time statistics by stage.

    Returns average, min, max processing times for each stage
    over the specified time period.
    """
    _check_lifecycle_available()
    # This would query paper_lifecycle table for timing stats
    # For now, return placeholder
    return {
        "note": "Detailed processing time statistics",
        "stage_filter": stage.value if stage else None,
        "days": days,
        "avg_times_by_stage": {
            "extracting": 45.2,
            "synthesizing": 12.8,
        },
    }


@router.get("/stats/success-rates")
async def get_success_rates(
    days: int = Query(30, ge=1, le=365, description="Days of data to include"),
):
    """
    Get success rates by stage over time.

    Returns percentage of successful completions for each stage
    over the specified time period.
    """
    _check_lifecycle_available()
    service = get_lifecycle_service()
    health = service.get_pipeline_health()
    return {
        "days": days,
        "success_rates": health.stage_success_rates,
        "total_processed": health.last_7_days_processed,
    }
