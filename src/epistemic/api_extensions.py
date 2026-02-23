"""
API Extensions for Non-Empirical Web Integration (Sprint 6d / Task 6d.3).

Provides FastAPI router extensions for the 12 node types and their
associated monitors and operations.

Endpoints cover:
1. Theory Health (/theories/health) - Track confirmation/disconfirmation ratios
2. Cross-Type Coherence (/coherence) - Query coherence between node types
3. Prediction Ledger (/predictions) - Access hypothesis tracking
4. Node Type Operations (/nodes) - CRUD for new node types

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §6.3
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.epistemic.node_types import NodeType, get_node_type_family
from src.epistemic.edge_types import EdgeType
from src.epistemic.monitors.theory_monitor import (
    TheoryMonitor,
)
from src.epistemic.monitors.cross_type_coherence import (
    CrossTypeCoherenceMonitor,
)
from src.epistemic.entrenchment.prediction_ledger import (
    PredictionLedger,
)


# =============================================================================
# Pydantic Models
# =============================================================================

class TheoryHealthResponse(BaseModel):
    """Response for theory health query."""
    theory_id: str
    theory_text: str
    current_entrenchment: float
    health_status: str
    n_hypotheses: int
    n_confirmations: int
    n_disconfirmations: int
    confirmation_rate: Optional[float]
    risks: List[str]
    recommendation: Optional[str]


class TheoryHealthSummaryResponse(BaseModel):
    """Summary of all monitored theories."""
    total_theories: int
    well_supported: int
    moderately_supported: int
    needs_revision: int
    problematic: int
    untested: int
    theories_with_risks: int
    highest_risk_theories: List[str]
    most_supported_theories: List[str]


class CoherenceScoreResponse(BaseModel):
    """Pairwise coherence score."""
    source_node_id: str
    source_node_type: str
    target_node_id: str
    target_node_type: str
    coherence_type: str
    score: float
    edge_count: int
    explanation: str


class CoherenceReportResponse(BaseModel):
    """Full coherence report."""
    total_nodes: int
    nodes_by_type: Dict[str, int]
    mean_theory_evidence_coherence: float
    mean_synthesis_primary_coherence: float
    ungrounded_theory_count: int
    uninterpreted_evidence_count: int
    anomaly_count: int


class AnomalyResponse(BaseModel):
    """Single coherence anomaly."""
    node_id: str
    node_type: str
    anomaly_type: str
    severity: float
    description: str
    suggested_action: str


class PredictionResponse(BaseModel):
    """Prediction from the ledger."""
    hypothesis_id: str
    hypothesis_text: str
    derived_from: str
    current_entrenchment: float
    n_confirmations: int
    n_disconfirmations: int
    status: str


class TheoryTrackRecordResponse(BaseModel):
    """Track record for a theory."""
    theory_id: str
    hypothesis_count: int
    total_confirmations: int
    total_disconfirmations: int
    success_rate: Optional[float]
    hypotheses: List[str]


class NodeCreateRequest(BaseModel):
    """Request to create a new node."""
    node_id: str
    node_type: str
    statement: str
    paper_id: str
    entrenchment: float = Field(default=0.35, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class NodeResponse(BaseModel):
    """Response for a node query."""
    node_id: str
    node_type: str
    family: str
    statement: str
    entrenchment: float
    paper_id: str
    bn_eligible: bool


class EdgeCreateRequest(BaseModel):
    """Request to create a new edge."""
    edge_id: str
    edge_type: str
    source_node_id: str
    target_node_id: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    paper_id: str


# =============================================================================
# In-Memory Storage (would be database in production)
# =============================================================================

_theory_monitor: Optional[TheoryMonitor] = None
_coherence_monitor: Optional[CrossTypeCoherenceMonitor] = None
_prediction_ledger: Optional[PredictionLedger] = None
_nodes: Dict[str, Dict[str, Any]] = {}
_edges: List[Dict[str, Any]] = []


def _get_theory_monitor() -> TheoryMonitor:
    global _theory_monitor, _prediction_ledger
    if _theory_monitor is None:
        _prediction_ledger = PredictionLedger()
        _theory_monitor = TheoryMonitor(_prediction_ledger)
    return _theory_monitor


def _get_coherence_monitor() -> CrossTypeCoherenceMonitor:
    global _coherence_monitor
    if _coherence_monitor is None:
        _coherence_monitor = CrossTypeCoherenceMonitor()
    return _coherence_monitor


def _get_prediction_ledger() -> PredictionLedger:
    global _prediction_ledger
    if _prediction_ledger is None:
        _prediction_ledger = PredictionLedger()
    return _prediction_ledger


# =============================================================================
# Routers
# =============================================================================

theory_health_router = APIRouter(prefix="/theories/health", tags=["theory_health"])
coherence_router = APIRouter(prefix="/coherence", tags=["coherence"])
predictions_router = APIRouter(prefix="/predictions", tags=["predictions"])
nodes_router = APIRouter(prefix="/nodes", tags=["nodes"])


# =============================================================================
# Theory Health Endpoints
# =============================================================================

@theory_health_router.get("/{theory_id}", response_model=TheoryHealthResponse)
async def get_theory_health(
    theory_id: str,
    entrenchment: float = Query(default=0.35, ge=0.0, le=1.0)
):
    """
    Get health status for a specific theory.

    Returns confirmation/disconfirmation ratios, risks, and recommendations.
    """
    monitor = _get_theory_monitor()

    # Find theory text from nodes
    theory_text = ""
    for node_id, node_data in _nodes.items():
        if node_data.get("node_type") == "theoretical_proposition" and node_id == theory_id:
            theory_text = node_data.get("statement", "")
            entrenchment = node_data.get("entrenchment", entrenchment)
            break

    report = monitor.assess_theory(
        theory_id=theory_id,
        theory_text=theory_text,
        current_entrenchment=entrenchment
    )

    return TheoryHealthResponse(
        theory_id=report.theory_id,
        theory_text=report.theory_text,
        current_entrenchment=report.current_entrenchment,
        health_status=report.health_status.value,
        n_hypotheses=report.n_hypotheses,
        n_confirmations=report.n_confirmations,
        n_disconfirmations=report.n_disconfirmations,
        confirmation_rate=report.confirmation_rate,
        risks=[r.value for r in report.risks],
        recommendation=report.recommendation
    )


@theory_health_router.get("/", response_model=TheoryHealthSummaryResponse)
async def get_theory_health_summary():
    """
    Get summary of health status for all monitored theories.
    """
    monitor = _get_theory_monitor()

    # Assess all theoretical propositions
    for node_id, node_data in _nodes.items():
        if node_data.get("node_type") == "theoretical_proposition":
            monitor.assess_theory(
                theory_id=node_id,
                theory_text=node_data.get("statement", ""),
                current_entrenchment=node_data.get("entrenchment", 0.35)
            )

    summary = monitor.get_summary()

    return TheoryHealthSummaryResponse(
        total_theories=summary.total_theories,
        well_supported=summary.well_supported,
        moderately_supported=summary.moderately_supported,
        needs_revision=summary.needs_revision,
        problematic=summary.problematic,
        untested=summary.untested,
        theories_with_risks=summary.theories_with_risks,
        highest_risk_theories=summary.highest_risk_theories,
        most_supported_theories=summary.most_supported_theories
    )


@theory_health_router.get("/alerts")
async def get_theory_alerts():
    """
    Get alerts for theories needing attention.

    Returns theories that are problematic, accumulating disconfirmations,
    or overentrenched without evidence.
    """
    monitor = _get_theory_monitor()

    # Refresh assessments
    for node_id, node_data in _nodes.items():
        if node_data.get("node_type") == "theoretical_proposition":
            monitor.assess_theory(
                theory_id=node_id,
                theory_text=node_data.get("statement", ""),
                current_entrenchment=node_data.get("entrenchment", 0.35)
            )

    alerts = monitor.check_theory_alerts()

    return {"alerts": alerts, "count": len(alerts)}


# =============================================================================
# Cross-Type Coherence Endpoints
# =============================================================================

@coherence_router.get("/pairwise", response_model=CoherenceScoreResponse)
async def get_pairwise_coherence(
    node_a: str = Query(..., description="First node ID"),
    node_b: str = Query(..., description="Second node ID")
):
    """
    Get coherence score between two nodes.

    Different node type pairs have different coherence semantics.
    """
    monitor = _get_coherence_monitor()

    # Register nodes if not already
    for node_id, node_data in _nodes.items():
        try:
            node_type = NodeType(node_data.get("node_type", "empirical_finding"))
            monitor.register_node(node_id, node_type)
        except ValueError:
            pass

    # Register edges
    for edge in _edges:
        monitor.register_edge(
            edge["source_node_id"],
            edge["target_node_id"],
            edge["edge_type"],
            edge.get("weight", 1.0)
        )

    score = monitor.compute_pairwise_coherence(node_a, node_b)

    if score is None:
        raise HTTPException(status_code=404, detail="One or both nodes not found")

    return CoherenceScoreResponse(
        source_node_id=score.source_node_id,
        source_node_type=score.source_node_type.value,
        target_node_id=score.target_node_id,
        target_node_type=score.target_node_type.value,
        coherence_type=score.coherence_type.value,
        score=score.score,
        edge_count=score.edge_count,
        explanation=score.explanation
    )


@coherence_router.get("/report", response_model=CoherenceReportResponse)
async def get_coherence_report():
    """
    Get comprehensive coherence report for the web.

    Includes cross-type coherence statistics and anomaly counts.
    """
    monitor = _get_coherence_monitor()

    # Register all nodes
    for node_id, node_data in _nodes.items():
        try:
            node_type = NodeType(node_data.get("node_type", "empirical_finding"))
            monitor.register_node(node_id, node_type)
        except ValueError:
            pass

    # Register all edges
    for edge in _edges:
        monitor.register_edge(
            edge["source_node_id"],
            edge["target_node_id"],
            edge["edge_type"],
            edge.get("weight", 1.0)
        )

    report = monitor.generate_report()

    return CoherenceReportResponse(
        total_nodes=report.total_nodes,
        nodes_by_type=report.nodes_by_type,
        mean_theory_evidence_coherence=report.mean_theory_evidence_coherence,
        mean_synthesis_primary_coherence=report.mean_synthesis_primary_coherence,
        ungrounded_theory_count=report.ungrounded_theory_count,
        uninterpreted_evidence_count=report.uninterpreted_evidence_count,
        anomaly_count=len(report.anomalies)
    )


@coherence_router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_coherence_anomalies():
    """
    Get structural anomalies in web coherence.

    Returns ungrounded theories, orphan syntheses, untested hypotheses, etc.
    """
    monitor = _get_coherence_monitor()

    # Register nodes and edges
    for node_id, node_data in _nodes.items():
        try:
            node_type = NodeType(node_data.get("node_type", "empirical_finding"))
            monitor.register_node(node_id, node_type)
        except ValueError:
            pass

    for edge in _edges:
        monitor.register_edge(
            edge["source_node_id"],
            edge["target_node_id"],
            edge["edge_type"],
            edge.get("weight", 1.0)
        )

    anomalies = monitor.detect_anomalies()

    return [
        AnomalyResponse(
            node_id=a.node_id,
            node_type=a.node_type.value,
            anomaly_type=a.anomaly_type.value,
            severity=a.severity,
            description=a.description,
            suggested_action=a.suggested_action
        )
        for a in anomalies
    ]


# =============================================================================
# Prediction Ledger Endpoints
# =============================================================================

@predictions_router.get("/", response_model=List[PredictionResponse])
async def list_predictions(
    status: Optional[str] = Query(default=None, pattern="^(untested|confirmed|disconfirmed|mixed)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """
    List all predictions in the ledger.

    Optionally filter by status (untested, confirmed, disconfirmed, mixed).
    """
    ledger = _get_prediction_ledger()
    entries = ledger.get_all_entries()

    # Filter by status if specified
    if status:
        entries = [e for e in entries if e.get_status() == status]

    # Paginate
    total = len(entries)
    entries = entries[offset:offset + limit]

    return [
        PredictionResponse(
            hypothesis_id=e.hypothesis_id,
            hypothesis_text=e.hypothesis_text,
            derived_from=e.derived_from,
            current_entrenchment=e.current_entrenchment,
            n_confirmations=len(e.confirmed_by),
            n_disconfirmations=len(e.disconfirmed_by),
            status=e.get_status()
        )
        for e in entries
    ]


@predictions_router.get("/{hypothesis_id}", response_model=PredictionResponse)
async def get_prediction(hypothesis_id: str):
    """Get details for a specific prediction."""
    ledger = _get_prediction_ledger()
    entry = ledger.get_entry(hypothesis_id)

    if entry is None:
        raise HTTPException(status_code=404, detail=f"Prediction {hypothesis_id} not found")

    return PredictionResponse(
        hypothesis_id=entry.hypothesis_id,
        hypothesis_text=entry.hypothesis_text,
        derived_from=entry.derived_from,
        current_entrenchment=entry.current_entrenchment,
        n_confirmations=len(entry.confirmed_by),
        n_disconfirmations=len(entry.disconfirmed_by),
        status=entry.get_status()
    )


@predictions_router.get("/theory/{theory_id}", response_model=TheoryTrackRecordResponse)
async def get_theory_track_record(theory_id: str):
    """
    Get track record for a theory.

    Shows all hypotheses derived from this theory and their confirmation status.
    """
    ledger = _get_prediction_ledger()
    record = ledger.compute_theory_track_record(theory_id)

    return TheoryTrackRecordResponse(
        theory_id=theory_id,
        hypothesis_count=record["hypothesis_count"],
        total_confirmations=record["total_confirmations"],
        total_disconfirmations=record["total_disconfirmations"],
        success_rate=record["success_rate"],
        hypotheses=record["hypotheses"]
    )


@predictions_router.post("/{hypothesis_id}/confirm")
async def confirm_prediction(
    hypothesis_id: str,
    study_id: str = Query(..., description="ID of confirming study"),
):
    """
    Record a confirmation of a prediction.
    """
    ledger = _get_prediction_ledger()
    entry = ledger.get_entry(hypothesis_id)

    if entry is None:
        raise HTTPException(status_code=404, detail=f"Prediction {hypothesis_id} not found")

    ledger.record_confirmation(hypothesis_id, study_id)

    return {"status": "confirmed", "hypothesis_id": hypothesis_id, "study_id": study_id}


@predictions_router.post("/{hypothesis_id}/disconfirm")
async def disconfirm_prediction(
    hypothesis_id: str,
    study_id: str = Query(..., description="ID of disconfirming study")
):
    """
    Record a disconfirmation of a prediction.
    """
    ledger = _get_prediction_ledger()
    entry = ledger.get_entry(hypothesis_id)

    if entry is None:
        raise HTTPException(status_code=404, detail=f"Prediction {hypothesis_id} not found")

    ledger.record_disconfirmation(hypothesis_id, study_id)

    return {"status": "disconfirmed", "hypothesis_id": hypothesis_id, "study_id": study_id}


# =============================================================================
# Node Type Endpoints
# =============================================================================

@nodes_router.get("/types")
async def list_node_types():
    """
    List all available node types with their properties.
    """
    from src.epistemic.node_types import NODE_TYPE_PROPERTIES

    types = []
    for node_type in NodeType:
        props = NODE_TYPE_PROPERTIES.get(node_type)
        types.append({
            "type": node_type.value,
            "family": props.family.value if props else "unknown",
            "has_effect_size": props.has_effect_size if props else False,
            "has_study_design": props.has_study_design if props else False,
            "bn_eligible": props.bn_eligible if props else False,
            "entrenchment_source": props.entrenchment_source if props else "coherence"
        })

    return {"types": types, "count": len(types)}


@nodes_router.get("/", response_model=List[NodeResponse])
async def list_nodes(
    node_type: Optional[str] = Query(default=None),
    family: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """
    List all nodes, optionally filtered by type or family.
    """
    from src.epistemic.node_types import NODE_TYPE_PROPERTIES

    filtered = []
    for node_id, node_data in _nodes.items():
        nt = node_data.get("node_type", "empirical_finding")

        # Filter by type
        if node_type and nt != node_type:
            continue

        # Filter by family
        try:
            node_type_enum = NodeType(nt)
            node_family = get_node_type_family(node_type_enum).value
            props = NODE_TYPE_PROPERTIES.get(node_type_enum)
            bn_eligible = props.bn_eligible if props else False
        except ValueError:
            node_family = "unknown"
            bn_eligible = False

        if family and node_family != family:
            continue

        filtered.append(NodeResponse(
            node_id=node_id,
            node_type=nt,
            family=node_family,
            statement=node_data.get("statement", ""),
            entrenchment=node_data.get("entrenchment", 0.35),
            paper_id=node_data.get("paper_id", ""),
            bn_eligible=bn_eligible
        ))

    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return paginated


@nodes_router.post("/", response_model=NodeResponse)
async def create_node(request: NodeCreateRequest):
    """
    Create a new node in the web.
    """
    from src.epistemic.node_types import NODE_TYPE_PROPERTIES

    # Validate node type
    try:
        node_type_enum = NodeType(request.node_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid node type: {request.node_type}")

    if request.node_id in _nodes:
        raise HTTPException(status_code=409, detail=f"Node {request.node_id} already exists")

    # Create node
    _nodes[request.node_id] = {
        "node_type": request.node_type,
        "statement": request.statement,
        "paper_id": request.paper_id,
        "entrenchment": request.entrenchment,
        "metadata": request.metadata or {},
        "created_at": datetime.now().isoformat()
    }

    # Register with coherence monitor
    monitor = _get_coherence_monitor()
    monitor.register_node(request.node_id, node_type_enum)

    # If hypothesis, register with ledger
    if request.node_type == "derived_hypothesis":
        ledger = _get_prediction_ledger()
        parent_theory = request.metadata.get("derived_from", "") if request.metadata else ""
        ledger.register_hypothesis(
            hypothesis_id=request.node_id,
            text=request.statement,
            parent_prop_id=parent_theory
        )

    props = NODE_TYPE_PROPERTIES.get(node_type_enum)

    return NodeResponse(
        node_id=request.node_id,
        node_type=request.node_type,
        family=get_node_type_family(node_type_enum).value,
        statement=request.statement,
        entrenchment=request.entrenchment,
        paper_id=request.paper_id,
        bn_eligible=props.bn_eligible if props else False
    )


@nodes_router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    """Get details for a specific node."""
    from src.epistemic.node_types import NODE_TYPE_PROPERTIES

    if node_id not in _nodes:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")

    node_data = _nodes[node_id]
    nt = node_data.get("node_type", "empirical_finding")

    try:
        node_type_enum = NodeType(nt)
        node_family = get_node_type_family(node_type_enum).value
        props = NODE_TYPE_PROPERTIES.get(node_type_enum)
        bn_eligible = props.bn_eligible if props else False
    except ValueError:
        node_family = "unknown"
        bn_eligible = False

    return NodeResponse(
        node_id=node_id,
        node_type=nt,
        family=node_family,
        statement=node_data.get("statement", ""),
        entrenchment=node_data.get("entrenchment", 0.35),
        paper_id=node_data.get("paper_id", ""),
        bn_eligible=bn_eligible
    )


@nodes_router.post("/edges")
async def create_edge(request: EdgeCreateRequest):
    """
    Create a new edge between nodes.
    """
    # Validate edge type
    try:
        edge_type_enum = EdgeType(request.edge_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid edge type: {request.edge_type}")

    # Check nodes exist
    if request.source_node_id not in _nodes:
        raise HTTPException(status_code=404, detail=f"Source node {request.source_node_id} not found")
    if request.target_node_id not in _nodes:
        raise HTTPException(status_code=404, detail=f"Target node {request.target_node_id} not found")

    # Create edge
    edge = {
        "edge_id": request.edge_id,
        "edge_type": request.edge_type,
        "source_node_id": request.source_node_id,
        "target_node_id": request.target_node_id,
        "weight": request.weight,
        "paper_id": request.paper_id,
        "created_at": datetime.now().isoformat()
    }
    _edges.append(edge)

    # Register with coherence monitor
    monitor = _get_coherence_monitor()
    monitor.register_edge(
        request.source_node_id,
        request.target_node_id,
        request.edge_type,
        request.weight
    )

    return {
        "status": "created",
        "edge_id": request.edge_id,
        "edge_type": request.edge_type
    }


# =============================================================================
# Router Aggregation
# =============================================================================

def get_sprint6_router() -> APIRouter:
    """Get the Sprint 6 API router with all sub-routers."""
    router = APIRouter(prefix="/api/v1/epistemic")

    router.include_router(theory_health_router)
    router.include_router(coherence_router)
    router.include_router(predictions_router)
    router.include_router(nodes_router)

    return router


# Convenience export
sprint6_router = get_sprint6_router()
