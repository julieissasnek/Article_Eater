"""
Article Eater V23 — Causal Operations API
Sprint 3.0.1-F

Per Judea Pearl's recommendations, separating causal inference endpoints.
Endpoints:
- GET /causal/paths/{from_id}/{to_id}: Find causal pathways
- GET /causal/interventions/{target}: Project causal intervention impact
- POST /causal/counterfactual: Counterfactual "What if" querying
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

logger = __import__("logging").getLogger(__name__)

from app.routes.web_of_belief import get_web

causal_router = APIRouter(prefix="/causal", tags=["causal"])

# =============================================================================
# Models
# =============================================================================

class CausalPathInfo(BaseModel):
    source: str
    target: str
    path_exists: bool
    paths: List[List[str]]
    causal_strength_estimate: float

class CausalInterventionResponse(BaseModel):
    target: str
    downstream_impacts: List[Dict[str, Any]]
    upstream_causes: List[Dict[str, Any]]

class CounterfactualQuery(BaseModel):
    assumption: Dict[str, Any]
    target_variable: str

class CounterfactualResponse(BaseModel):
    original_state: float
    counterfactual_state: float
    difference: float
    explanation: str

# =============================================================================
# Endpoints
# =============================================================================

@causal_router.get("/paths/{from_id}/{to_id}", response_model=CausalPathInfo)
async def get_causal_paths(from_id: str, to_id: str):
    """
    Find causal pathways between constructs.
    """
    web = get_web()
    
    if from_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Source belief {from_id} not found")
        
    if to_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Target belief {to_id} not found")

    # Breadth-first search for paths (simplified scaffolding)
    paths = []
    
    # Check direct constraints
    for c in web.constraints.values():
        if c.source_id == from_id and c.target_id == to_id:
            paths.append([from_id, to_id])
            
    return CausalPathInfo(
        source=from_id,
        target=to_id,
        path_exists=len(paths) > 0,
        paths=paths,
        causal_strength_estimate=0.85 if paths else 0.0
    )


@causal_router.get("/interventions/{target}", response_model=CausalInterventionResponse)
async def analyze_intervention(target: str, magnitude: float = Query(1.0, ge=-1.0, le=1.0)):
    """
    Project causal impact if an intervention shifts the target construct.
    """
    web = get_web()
    
    if target not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Target belief {target} not found")
        
    downstream = []
    upstream = []
    
    for c in web.constraints.values():
        if c.source_id == target:
            # We are the cause, this is downstream impact
            impact = magnitude * c.strength * (1.0 if c.polarity.value.upper() == "POSITIVE" else -1.0)
            downstream.append({
                "affected_belief": c.target_id,
                "projected_change": round(impact, 3),
                "mechanism_strength": c.strength
            })
        elif c.target_id == target:
            # We are the effect, these are upstream causes
            upstream.append({
                "causing_belief": c.source_id,
                "required_shift_to_achieve": round(magnitude / c.strength if c.strength > 0 else 0, 3),
                "mechanism_strength": c.strength
            })
            
    return CausalInterventionResponse(
        target=target,
        downstream_impacts=downstream,
        upstream_causes=upstream
    )

@causal_router.post("/counterfactual", response_model=CounterfactualResponse)
async def query_counterfactual(query: CounterfactualQuery):
    """
    Simulate "What if" counterfactual query by shifting a specific assumption.
    """
    web = get_web()
    target = query.target_variable
    
    if target not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Target belief {target} not found")
        
    original = web.beliefs[target].credence.value
    
    # Scaffolding: simulate a drop/rise based on the assumption logic
    assumption_shift = query.assumption.get("strength_shift", -0.5) 
    counterfactual = max(0.0, min(1.0, original + assumption_shift))
    
    return CounterfactualResponse(
        original_state=original,
        counterfactual_state=counterfactual,
        difference=round(counterfactual - original, 3),
        explanation=f"If assumption holds, target drops by {abs(assumption_shift)}."
    )
