"""
Reports API Routes
==================

API routes for stopping rules and report generation.

Date: January 21, 2026
Phase D Sprint D1-D2
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

from src.services.stopping_rules import (
    StoppingRulesEngine, StoppingDecision, StoppingReason, evaluate_stopping
)
from src.services.reporting import (
    ReportGenerator, Report, ReportType, generate_report
)
from src.services.web_of_belief import WebOfBelief


router = APIRouter(prefix="/api/reports", tags=["reports"])


# =============================================================================
# Shared Web Instance (F-Sprint Fix: centralized per Lamport)
# =============================================================================
# Import from web_of_belief.py to share single instance across all routes

from app.routes.web_of_belief import get_web, set_web


# =============================================================================
# Request/Response Models
# =============================================================================

class StoppingEvaluationRequest(BaseModel):
    """Request to evaluate stopping criteria."""
    topic: Optional[str] = Field(None, description="Topic to focus evaluation on")
    min_beliefs: int = Field(5, ge=1, description="Minimum beliefs before considering stop")
    confidence_threshold: float = Field(0.7, ge=0, le=1, description="Confidence threshold")


class StoppingCriterionResponse(BaseModel):
    """Single stopping criterion response."""
    name: str
    description: str
    threshold: float
    current_value: float
    is_met: bool
    reason: str


class StoppingEvaluationResponse(BaseModel):
    """Response from stopping evaluation."""
    should_stop: bool
    primary_reason: Optional[str]
    confidence: float
    criteria_met: List[StoppingCriterionResponse]
    criteria_not_met: List[StoppingCriterionResponse]
    recommendation: str


class ReportTypeEnum(str, Enum):
    """Available report types."""
    EXECUTIVE_SUMMARY = "executive"
    EVIDENCE_INVENTORY = "inventory"
    CONFIDENCE_ANALYSIS = "confidence"
    GAP_ANALYSIS = "gaps"
    QUALITY_ASSESSMENT = "quality"
    TOPIC_DEEP_DIVE = "topic"
    CONTRADICTION_REPORT = "contradictions"


class ReportRequest(BaseModel):
    """Request to generate a report."""
    report_type: ReportTypeEnum = Field(
        ReportTypeEnum.EXECUTIVE_SUMMARY,
        description="Type of report to generate"
    )
    topic: Optional[str] = Field(None, description="Topic to focus report on")


class ReportSectionResponse(BaseModel):
    """Section within a report."""
    title: str
    content: str
    data: Optional[Dict[str, Any]] = None
    subsections: List['ReportSectionResponse'] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """Complete report response."""
    report_type: str
    title: str
    generated_at: str
    summary: str
    sections: List[ReportSectionResponse]
    metadata: Dict[str, Any]


# =============================================================================
# Stopping Routes
# =============================================================================

@router.post("/stopping/evaluate", response_model=StoppingEvaluationResponse)
async def evaluate_stopping_criteria(request: StoppingEvaluationRequest):
    """
    Evaluate whether evidence gathering should stop.

    Uses multiple criteria including:
    - Information saturation
    - Confidence thresholds
    - Evidence count
    - Coverage across epistemic levels
    - Contradiction stability
    """
    web = get_web()

    decision = evaluate_stopping(
        web,
        topic=request.topic,
        min_beliefs=request.min_beliefs,
        confidence_threshold=request.confidence_threshold
    )

    return StoppingEvaluationResponse(
        should_stop=decision.should_stop,
        primary_reason=decision.primary_reason.value if decision.primary_reason else None,
        confidence=decision.confidence,
        criteria_met=[
            StoppingCriterionResponse(
                name=c.name,
                description=c.description,
                threshold=c.threshold,
                current_value=c.current_value,
                is_met=c.is_met,
                reason=c.reason.value
            )
            for c in decision.criteria_met
        ],
        criteria_not_met=[
            StoppingCriterionResponse(
                name=c.name,
                description=c.description,
                threshold=c.threshold,
                current_value=c.current_value,
                is_met=c.is_met,
                reason=c.reason.value
            )
            for c in decision.criteria_not_met
        ],
        recommendation=decision.recommendation
    )


@router.get("/stopping/reasons")
async def get_stopping_reasons():
    """Get all possible stopping reasons with descriptions."""
    return {
        "saturation": "No new unique information being found",
        "confidence": "Sufficient confidence level reached",
        "count": "Minimum evidence quantity gathered",
        "time": "Search time budget exceeded",
        "cost_benefit": "Marginal value of additional search too low",
        "manual": "User manually stopped the search",
        "coverage": "All relevant epistemic areas covered",
        "stable": "Contradictions have stabilized"
    }


# =============================================================================
# Report Routes
# =============================================================================

@router.post("/generate", response_model=ReportResponse)
async def generate_report_endpoint(request: ReportRequest):
    """
    Generate a report of the specified type.

    Available report types:
    - executive: High-level summary
    - inventory: Complete evidence listing
    - confidence: Confidence analysis
    - gaps: What we don't know
    - quality: Evidence quality assessment
    - topic: Deep dive on specific topic
    - contradictions: Areas of disagreement
    """
    web = get_web()

    report_type_map = {
        ReportTypeEnum.EXECUTIVE_SUMMARY: ReportType.EXECUTIVE_SUMMARY,
        ReportTypeEnum.EVIDENCE_INVENTORY: ReportType.EVIDENCE_INVENTORY,
        ReportTypeEnum.CONFIDENCE_ANALYSIS: ReportType.CONFIDENCE_ANALYSIS,
        ReportTypeEnum.GAP_ANALYSIS: ReportType.GAP_ANALYSIS,
        ReportTypeEnum.QUALITY_ASSESSMENT: ReportType.QUALITY_ASSESSMENT,
        ReportTypeEnum.TOPIC_DEEP_DIVE: ReportType.TOPIC_DEEP_DIVE,
        ReportTypeEnum.CONTRADICTION_REPORT: ReportType.CONTRADICTION_REPORT,
    }

    report = generate_report(
        web,
        report_type=report_type_map[request.report_type],
        topic=request.topic
    )

    return ReportResponse(
        report_type=report.report_type.value,
        title=report.title,
        generated_at=report.generated_at,
        summary=report.summary,
        sections=[
            ReportSectionResponse(
                title=s.title,
                content=s.content,
                data=s.data,
                subsections=[]
            )
            for s in report.sections
        ],
        metadata=report.metadata
    )


@router.get("/types")
async def get_report_types():
    """Get available report types with descriptions."""
    return {
        "executive": "High-level executive summary with key metrics",
        "inventory": "Complete inventory of all evidence",
        "confidence": "Analysis of confidence levels and uncertainty",
        "gaps": "Gap analysis showing what we don't know",
        "quality": "Evidence quality assessment",
        "topic": "Deep dive on a specific topic",
        "contradictions": "Report on contradictions and disputes"
    }


@router.get("/summary")
async def get_quick_summary():
    """Get a quick summary of the evidence base."""
    web = get_web()
    beliefs = list(web.beliefs.values())

    if not beliefs:
        return {
            'total_beliefs': 0,
            'status': 'empty',
            'message': 'No beliefs in the evidence base yet.'
        }

    avg_credence = sum(b.credence.value for b in beliefs) / len(beliefs)
    high_confidence = sum(1 for b in beliefs if b.credence.value >= 0.7)
    contested = sum(1 for b in beliefs if b.contested)

    # Determine status
    if len(beliefs) < 5:
        status = 'insufficient'
        message = 'Need more evidence to draw conclusions.'
    elif avg_credence < 0.5:
        status = 'uncertain'
        message = 'Evidence is inconclusive, more high-quality sources needed.'
    elif contested > len(beliefs) * 0.3:
        status = 'contested'
        message = 'Significant disagreement in the evidence base.'
    elif avg_credence >= 0.7:
        status = 'confident'
        message = 'Strong evidence base with high confidence.'
    else:
        status = 'moderate'
        message = 'Moderate evidence base, consider additional sources.'

    return {
        'total_beliefs': len(beliefs),
        'average_credence': avg_credence,
        'high_confidence_count': high_confidence,
        'contested_count': contested,
        'status': status,
        'message': message
    }


# =============================================================================
# Combined Analysis
# =============================================================================

@router.get("/dashboard")
async def get_dashboard_data():
    """
    Get all data needed for a reporting dashboard.

    Returns stopping status, key metrics, and quick summaries.
    """
    web = get_web()
    beliefs = list(web.beliefs.values())

    # Stopping evaluation
    stopping = evaluate_stopping(web)

    # Quick metrics
    total = len(beliefs)
    avg_credence = sum(b.credence.value for b in beliefs) / total if total else 0
    contested = sum(1 for b in beliefs if b.contested)

    # By source depth
    by_depth = {}
    for b in beliefs:
        depth = b.source_depth.value if b.source_depth else "unknown"
        by_depth[depth] = by_depth.get(depth, 0) + 1

    # By outcome
    by_outcome = {}
    for b in beliefs:
        outcome = b.outcome_id or "unclassified"
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1

    return {
        'stopping': {
            'should_stop': stopping.should_stop,
            'confidence': stopping.confidence,
            'recommendation': stopping.recommendation,
            'criteria_met': len(stopping.criteria_met),
            'criteria_total': len(stopping.criteria_met) + len(stopping.criteria_not_met)
        },
        'metrics': {
            'total_beliefs': total,
            'average_credence': avg_credence,
            'contested_beliefs': contested,
            'high_confidence': sum(1 for b in beliefs if b.credence.value >= 0.7)
        },
        'distribution': {
            'by_source_depth': by_depth,
            'by_outcome': by_outcome
        },
        'health': {
            'has_minimum_evidence': total >= 5,
            'has_diversity': len(by_outcome) >= 2,
            'low_uncertainty': sum(1 for b in beliefs if b.credence.uncertainty < 0.15) > total * 0.5 if total else False
        }
    }
