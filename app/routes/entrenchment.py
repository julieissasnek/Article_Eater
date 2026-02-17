"""
Entrenchment API Routes — ENT-4/ENT-5
2026-02-09

Provides API endpoints for entrenchment monitoring and health metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.services.web_persistence import WebPersistenceService

router = APIRouter(prefix="/entrenchment", tags=["entrenchment"])


# =============================================================================
# Response Models
# =============================================================================

class EntrenchmentSnapshot(BaseModel):
    """Single entrenchment snapshot."""
    belief_id: str
    as_of_date: str
    entrenchment: float
    timeline_type: str
    paper_id: Optional[str] = None


class TrajectoryResponse(BaseModel):
    """Entrenchment trajectory for a belief."""
    belief_id: str
    timeline_type: str
    data_points: List[Dict[str, Any]]
    volatility: Optional[float] = None
    trend: Optional[float] = None
    latest: Optional[float] = None
    n_snapshots: int = 0


class TimelineComparisonResponse(BaseModel):
    """Comparison between system and scholarly timelines."""
    belief_id: str
    system_entrenchment: Optional[float] = None
    scholarly_entrenchment: Optional[float] = None
    divergence: Optional[float] = None


class HealthMetricsResponse(BaseModel):
    """Web health metrics summary."""
    total_beliefs: int = 0
    avg_entrenchment: Optional[float] = None
    avg_volatility: Optional[float] = None
    timeline_divergence: Optional[float] = None
    stagnant_count: int = 0
    conflict_load: Optional[float] = None
    high_volatility_count: int = 0
    low_entrenchment_count: int = 0


class BeliefComparisonEntry(BaseModel):
    """Single entry in belief comparison table."""
    belief_id: str
    content: Optional[str] = None
    theory: Optional[str] = None
    system_entrenchment: Optional[float] = None
    scholarly_entrenchment: Optional[float] = None
    divergence: Optional[float] = None
    volatility: Optional[float] = None
    trend: Optional[str] = None


class BeliefComparisonResponse(BaseModel):
    """List of belief comparisons."""
    beliefs: List[BeliefComparisonEntry]


# =============================================================================
# Dependencies
# =============================================================================

def get_persistence() -> WebPersistenceService:
    """Get persistence service instance."""
    # In production, this would be injected properly
    return WebPersistenceService("ae.db")


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/trajectory/{belief_id}", response_model=TrajectoryResponse)
async def get_entrenchment_trajectory(
    belief_id: str,
    timeline: str = Query("system", pattern="^(system|scholarly)$"),
    limit: int = Query(50, ge=1, le=200),
    persistence: WebPersistenceService = Depends(get_persistence)
) -> TrajectoryResponse:
    """
    Get entrenchment trajectory for a specific belief.

    Returns time-series data showing how entrenchment changed over time.
    """
    trajectory = persistence.get_entrenchment_trajectory(
        belief_id=belief_id,
        timeline_type=timeline,
        limit=limit
    )

    return TrajectoryResponse(
        belief_id=trajectory["belief_id"],
        timeline_type=trajectory["timeline_type"],
        data_points=trajectory["data_points"],
        volatility=trajectory["volatility"],
        trend=trajectory["trend"],
        latest=trajectory["latest"],
        n_snapshots=trajectory["n_snapshots"]
    )


@router.get("/history/{belief_id}")
async def get_entrenchment_history(
    belief_id: str,
    timeline: Optional[str] = Query(None, pattern="^(system|scholarly)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    persistence: WebPersistenceService = Depends(get_persistence)
) -> Dict[str, Any]:
    """
    Get raw entrenchment history for a belief.
    """
    history = persistence.get_entrenchment_history(
        belief_id=belief_id,
        timeline_type=timeline,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    return {"belief_id": belief_id, "history": history}


@router.get("/compare/{belief_id}", response_model=TimelineComparisonResponse)
async def compare_timelines(
    belief_id: str,
    persistence: WebPersistenceService = Depends(get_persistence)
) -> TimelineComparisonResponse:
    """
    Compare entrenchment between system and scholarly timelines for a belief.
    """
    comparison = persistence.compare_timeline_entrenchment(belief_id)

    return TimelineComparisonResponse(
        belief_id=comparison["belief_id"],
        system_entrenchment=comparison["system_entrenchment"],
        scholarly_entrenchment=comparison["scholarly_entrenchment"],
        divergence=comparison["divergence"]
    )


@router.get("/health", response_model=HealthMetricsResponse)
async def get_health_metrics(
    persistence: WebPersistenceService = Depends(get_persistence)
) -> HealthMetricsResponse:
    """
    Get overall web health metrics.

    Metrics include:
    - Average entrenchment and volatility
    - Timeline divergence score
    - Stagnation detection (beliefs not updated recently)
    - Conflict load
    """
    try:
        web_id = persistence.get_master_web_id()
        if not web_id:
            return HealthMetricsResponse()

        web, _ = persistence.load_web(web_id)
        if not web:
            return HealthMetricsResponse()

        # Calculate metrics
        total_beliefs = len(web.beliefs)
        if total_beliefs == 0:
            return HealthMetricsResponse(total_beliefs=0)

        # Get entrenchment values
        entrenchments = []
        volatilities = []
        divergences = []
        stagnant_count = 0
        high_volatility_count = 0
        low_entrenchment_count = 0

        for belief_id in web.beliefs:
            # Get trajectory for volatility
            trajectory = persistence.get_entrenchment_trajectory(
                belief_id=belief_id,
                timeline_type="system",
                limit=20
            )

            if trajectory["latest"] is not None:
                entrenchments.append(trajectory["latest"])
                if trajectory["latest"] < 0.3:
                    low_entrenchment_count += 1

            if trajectory["volatility"] is not None:
                volatilities.append(trajectory["volatility"])
                if trajectory["volatility"] > 0.1:
                    high_volatility_count += 1

            # Check for stagnation (no change in recent history)
            if trajectory["n_snapshots"] >= 2:
                if trajectory["volatility"] is not None and trajectory["volatility"] < 0.001:
                    stagnant_count += 1
            elif trajectory["n_snapshots"] <= 1:
                # Only one or no snapshots could indicate stagnation
                stagnant_count += 1

            # Calculate divergence
            comparison = persistence.compare_timeline_entrenchment(belief_id)
            if comparison["divergence"] is not None:
                divergences.append(comparison["divergence"])

        avg_entrenchment = sum(entrenchments) / len(entrenchments) if entrenchments else None
        avg_volatility = sum(volatilities) / len(volatilities) if volatilities else None
        avg_divergence = sum(divergences) / len(divergences) if divergences else None

        # Calculate conflict load from web coherence
        conflict_load = 1.0 - web.global_coherence() if hasattr(web, 'global_coherence') else None

        return HealthMetricsResponse(
            total_beliefs=total_beliefs,
            avg_entrenchment=avg_entrenchment,
            avg_volatility=avg_volatility,
            timeline_divergence=avg_divergence,
            stagnant_count=stagnant_count,
            conflict_load=conflict_load,
            high_volatility_count=high_volatility_count,
            low_entrenchment_count=low_entrenchment_count
        )

    except Exception as e:
        # Return empty metrics on error
        return HealthMetricsResponse()


@router.get("/comparison", response_model=BeliefComparisonResponse)
async def get_belief_comparison(
    theory: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    persistence: WebPersistenceService = Depends(get_persistence)
) -> BeliefComparisonResponse:
    """
    Get comparison table of all beliefs with their entrenchment metrics.
    """
    try:
        web_id = persistence.get_master_web_id()
        if not web_id:
            return BeliefComparisonResponse(beliefs=[])

        web, _ = persistence.load_web(web_id)
        if not web:
            return BeliefComparisonResponse(beliefs=[])

        beliefs = []
        for belief_id, belief in list(web.beliefs.items())[:limit]:
            # Filter by theory if specified
            if theory and getattr(belief, 'theory_id', None) != theory:
                continue

            # Get trajectory for volatility and trend
            trajectory = persistence.get_entrenchment_trajectory(
                belief_id=belief_id,
                timeline_type="system",
                limit=20
            )

            # Get comparison for divergence
            comparison = persistence.compare_timeline_entrenchment(belief_id)

            # Determine trend direction
            trend = "stable"
            if trajectory["trend"] is not None:
                if trajectory["trend"] > 0.01:
                    trend = "up"
                elif trajectory["trend"] < -0.01:
                    trend = "down"

            beliefs.append(BeliefComparisonEntry(
                belief_id=belief_id,
                content=getattr(belief, 'content', None),
                theory=getattr(belief, 'theory_id', None),
                system_entrenchment=comparison["system_entrenchment"],
                scholarly_entrenchment=comparison["scholarly_entrenchment"],
                divergence=comparison["divergence"],
                volatility=trajectory["volatility"],
                trend=trend
            ))

        return BeliefComparisonResponse(beliefs=beliefs)

    except Exception as e:
        return BeliefComparisonResponse(beliefs=[])


@router.get("/events")
async def get_entrenchment_events(
    belief_id: Optional[str] = None,
    timeline: Optional[str] = Query(None, pattern="^(system|scholarly)$"),
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    persistence: WebPersistenceService = Depends(get_persistence)
) -> Dict[str, Any]:
    """
    Get entrenchment change events.
    """
    events = persistence.get_entrenchment_events(
        belief_id=belief_id,
        timeline_type=timeline,
        event_type=event_type,
        limit=limit
    )

    return {"events": events}
