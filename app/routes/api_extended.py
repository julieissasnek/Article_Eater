"""
Article Eater V23 — Extended API Routes
Sprint 3.0.1-D — 2026-02-09

Extension of the unified API with 20 additional endpoints covering:
1. Theory Management (4 endpoints)
2. Entrenchment Analytics (4 endpoints)
3. Causal Graph Operations (4 endpoints)
4. Export Bundles (4 endpoints)
5. Historical & Versioning (4 endpoints)

Together with api_unified.py Core 7, this provides ~25+ endpoints.

Per panel recommendations:
- Simon: Layered complexity (simple → advanced endpoints)
- Stonebraker: Resource-oriented design
- Fielding: REST constraints (stateless, cacheable, uniform interface)
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Response
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import hashlib
import os
import sqlite3

logger = logging.getLogger(__name__)

# Import actual services
from app.routes.web_of_belief import get_web, set_web

# Try to import theory registry
try:
    from src.services.theory_registry import TheoryRegistry
    _theory_registry: Optional[TheoryRegistry] = None
except ImportError:
    TheoryRegistry = None
    _theory_registry = None

# Try to import export bundles
try:
    from src.services.export_bundles import (
        generate_bundle,
        list_purposes,
        ExportPurpose,
        ExportBundle as ServiceExportBundle
    )
    _export_bundles_available = True
except ImportError:
    _export_bundles_available = False

# Try to import bibtex generator
try:
    from src.services.bibtex_generator import (
        export_papers_to_bibtex,
        GeneratedBibTeXEntry,
        BibTeXEntryType
    )
    _bibtex_available = True
except ImportError:
    _bibtex_available = False


# Database helper
def _get_db_path() -> str:
    return os.environ.get("AE_DB_PATH") or os.environ.get("AE_DB") or "ae.db"


def _get_db_connection():
    return sqlite3.connect(_get_db_path(), timeout=30.0)


# Create routers for extended endpoints
theories_router = APIRouter(prefix="/theories", tags=["theories"])
entrenchment_router = APIRouter(prefix="/entrenchment", tags=["entrenchment"])
graph_router = APIRouter(prefix="/graph", tags=["graph"])
bundles_router = APIRouter(prefix="/bundles", tags=["bundles"])
history_router = APIRouter(prefix="/history", tags=["history"])


# =============================================================================
# Pydantic Models for Extended API
# =============================================================================


class TheoryResponse(BaseModel):
    """Theory in the web of belief."""
    id: str
    name: str
    description: Optional[str] = None
    level: str  # meta-theory, theory, sub-theory
    belief_count: int = 0
    constraint_count: int = 0
    average_credence: float = 0.0
    entrenchment: float = 0.0
    key_beliefs: List[str] = []


class TheoryCreate(BaseModel):
    """Request to create a new theory."""
    name: str
    description: Optional[str] = None
    level: str = Field(default="theory", pattern="^(meta-theory|theory|sub-theory)$")
    key_beliefs: List[str] = []


class EntrenchmentScore(BaseModel):
    """Entrenchment score for a belief."""
    belief_id: str
    entrenchment: float
    components: Dict[str, float]  # connectivity, level_weight, coherence_contrib
    rank: Optional[int] = None


class EntrenchmentComparison(BaseModel):
    """Comparison of entrenchment between beliefs."""
    belief_a: str
    belief_b: str
    entrenchment_a: float
    entrenchment_b: float
    difference: float
    more_entrenched: str


class GraphNode(BaseModel):
    """Node in the belief graph."""
    id: str
    label: str
    type: str  # belief, theory
    credence: Optional[float] = None
    entrenchment: Optional[float] = None
    level: Optional[str] = None


class GraphEdge(BaseModel):
    """Edge in the belief graph."""
    source: str
    target: str
    polarity: str
    strength: float


class GraphStructure(BaseModel):
    """Complete graph structure."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any]


class PathInfo(BaseModel):
    """Path between two beliefs."""
    source: str
    target: str
    path_exists: bool
    path: List[str]
    length: int
    total_strength: float


class ExportBundleRequest(BaseModel):
    """Request to generate an export bundle."""
    topic: str
    purpose: str = Field(
        default="literature_review",
        description="One of: practitioner_briefing, literature_review, systematic_review, data_pipeline, presentation, teaching_materials, grant_writing, policy_brief"
    )
    belief_ids: Optional[List[str]] = None
    min_credence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExportBundleResponse(BaseModel):
    """Export bundle response."""
    bundle_id: str
    topic: str
    purpose: str
    generated_at: str
    file_count: int
    files: List[Dict[str, Any]]
    warnings: List[str] = []


class SnapshotResponse(BaseModel):
    """Web of belief snapshot."""
    snapshot_id: str
    created_at: str
    belief_count: int
    constraint_count: int
    description: Optional[str] = None
    hash: str


class DiffEntry(BaseModel):
    """Single change in a diff."""
    type: str  # added, removed, modified
    entity_type: str  # belief, constraint
    entity_id: str
    details: Optional[Dict[str, Any]] = None


class SnapshotDiff(BaseModel):
    """Difference between two snapshots."""
    from_snapshot: str
    to_snapshot: str
    changes: List[DiffEntry]
    summary: Dict[str, int]  # counts by type


# =============================================================================
# Theory Endpoints (4 endpoints)
# =============================================================================


@theories_router.get("/")
async def list_theories(
    level: Optional[str] = Query(default=None, pattern="^(meta-theory|theory|sub-theory)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all theories in the web of belief.

    Theories are higher-level constructs that organize beliefs.
    Examples: ART (Attention Restoration Theory), SRT (Stress Recovery Theory).
    """
    web = get_web()

    # Extract unique theory IDs from beliefs
    theory_ids = set()
    for b in web.beliefs.values():
        if b.theory_id:
            theory_ids.add(b.theory_id)

    theories = []
    for tid in sorted(theory_ids):
        # Get beliefs for this theory
        theory_beliefs = [b for b in web.beliefs.values() if b.theory_id == tid]

        # Calculate stats
        belief_count = len(theory_beliefs)
        avg_credence = sum(b.credence.value for b in theory_beliefs) / belief_count if belief_count > 0 else 0

        # Count constraints involving theory beliefs
        theory_belief_ids = {b.belief_id for b in theory_beliefs}
        constraint_count = sum(
            1 for c in web.constraints.values()
            if c.source_id in theory_belief_ids or c.target_id in theory_belief_ids
        )

        # Calculate average entrenchment
        entrenchments = [web.get_entrenchment(b.belief_id) for b in theory_beliefs]
        avg_entrenchment = sum(entrenchments) / len(entrenchments) if entrenchments else 0

        # Determine level (heuristic based on name patterns)
        theory_level = "theory"
        if "meta" in tid.lower():
            theory_level = "meta-theory"
        elif "sub" in tid.lower() or len(theory_beliefs) < 5:
            theory_level = "sub-theory"

        if level and theory_level != level:
            continue

        theories.append(TheoryResponse(
            id=tid,
            name=tid.replace("_", " ").title(),
            description=f"Theory with {belief_count} beliefs",
            level=theory_level,
            belief_count=belief_count,
            constraint_count=constraint_count,
            average_credence=round(avg_credence, 3),
            entrenchment=round(avg_entrenchment, 3),
            key_beliefs=[b.belief_id for b in sorted(theory_beliefs, key=lambda x: x.credence.value, reverse=True)[:3]]
        ))

    total = len(theories)
    paginated = theories[offset:offset + limit]

    return {
        "theories": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@theories_router.get("/{theory_id}", response_model=TheoryResponse)
async def get_theory(theory_id: str):
    """Get details for a specific theory."""
    web = get_web()

    # Find beliefs for this theory
    theory_beliefs = [b for b in web.beliefs.values() if b.theory_id == theory_id]

    if not theory_beliefs:
        raise HTTPException(status_code=404, detail=f"Theory {theory_id} not found")

    belief_count = len(theory_beliefs)
    avg_credence = sum(b.credence.value for b in theory_beliefs) / belief_count if belief_count > 0 else 0

    theory_belief_ids = {b.belief_id for b in theory_beliefs}
    constraint_count = sum(
        1 for c in web.constraints.values()
        if c.source_id in theory_belief_ids or c.target_id in theory_belief_ids
    )

    entrenchments = [web.get_entrenchment(b.belief_id) for b in theory_beliefs]
    avg_entrenchment = sum(entrenchments) / len(entrenchments) if entrenchments else 0

    return TheoryResponse(
        id=theory_id,
        name=theory_id.replace("_", " ").title(),
        description=f"Theory with {belief_count} beliefs",
        level="theory",
        belief_count=belief_count,
        constraint_count=constraint_count,
        average_credence=round(avg_credence, 3),
        entrenchment=round(avg_entrenchment, 3),
        key_beliefs=[b.belief_id for b in sorted(theory_beliefs, key=lambda x: x.credence.value, reverse=True)[:5]]
    )


@theories_router.get("/{theory_id}/beliefs")
async def get_theory_beliefs(
    theory_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_credence: float = Query(default=0.0, ge=0.0, le=1.0)
):
    """Get all beliefs associated with a theory."""
    web = get_web()

    # Find beliefs for this theory
    theory_beliefs = [
        b for b in web.beliefs.values()
        if b.theory_id == theory_id and b.credence.value >= min_credence
    ]

    if not theory_beliefs:
        raise HTTPException(status_code=404, detail=f"Theory {theory_id} not found or has no beliefs")

    # Sort by credence
    sorted_beliefs = sorted(theory_beliefs, key=lambda x: x.credence.value, reverse=True)

    total = len(sorted_beliefs)
    paginated = sorted_beliefs[offset:offset + limit]

    beliefs = []
    for b in paginated:
        beliefs.append({
            "id": b.belief_id,
            "content": b.content,
            "credence": b.credence.value,
            "level": b.level.value.upper() if b.level else "EMPIRICAL",
            "entrenchment": web.get_entrenchment(b.belief_id)
        })

    return {
        "theory_id": theory_id,
        "beliefs": beliefs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@theories_router.get("/{theory_id}/constraints")
async def get_theory_constraints(theory_id: str):
    """Get constraints within or involving a theory."""
    web = get_web()

    # Find beliefs for this theory
    theory_belief_ids = {b.belief_id for b in web.beliefs.values() if b.theory_id == theory_id}

    if not theory_belief_ids:
        raise HTTPException(status_code=404, detail=f"Theory {theory_id} not found")

    # Find constraints
    internal = []  # Both beliefs in theory
    bridging = []  # One belief in theory, one outside

    for c in web.constraints.values():
        source_in = c.source_id in theory_belief_ids
        target_in = c.target_id in theory_belief_ids

        if source_in and target_in:
            internal.append({
                "id": c.constraint_id,
                "from": c.source_id,
                "to": c.target_id,
                "polarity": c.polarity.value.upper(),
                "strength": c.strength
            })
        elif source_in or target_in:
            bridging.append({
                "id": c.constraint_id,
                "from": c.source_id,
                "to": c.target_id,
                "polarity": c.polarity.value.upper(),
                "strength": c.strength,
                "external_belief": c.target_id if source_in else c.source_id
            })

    return {
        "theory_id": theory_id,
        "internal_constraints": internal,
        "bridging_constraints": bridging,
        "internal_count": len(internal),
        "bridging_count": len(bridging)
    }


# =============================================================================
# Entrenchment Analytics Endpoints (4 endpoints)
# =============================================================================


@entrenchment_router.get("/scores")
async def get_entrenchment_scores(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_entrenchment: float = Query(default=0.0, ge=0.0, le=1.0)
):
    """
    Get entrenchment scores for all beliefs, ranked.

    Entrenchment in V23 is emergent, computed from:
    - 40% connectivity (constraint count)
    - 30% level weight (THEORETICAL=0.8, EMPIRICAL=0.3, etc.)
    - 30% coherence contribution
    """
    web = get_web()

    scores = []
    for b in web.beliefs.values():
        entrenchment = web.get_entrenchment(b.belief_id)

        if entrenchment < min_entrenchment:
            continue

        # Compute components (approximation)
        n_constraints = sum(
            1 for c in web.constraints.values()
            if c.source_id == b.belief_id or c.target_id == b.belief_id
        )
        max_constraints = max(len(web.beliefs), 1) * 2  # Normalization factor
        connectivity = min(n_constraints / max_constraints, 1.0)

        level_weights = {
            "THEORETICAL": 0.8,
            "INTERMEDIATE": 0.5,
            "EMPIRICAL": 0.3,
            "OBSERVATIONAL": 0.2
        }
        level_weight = level_weights.get(b.level.value.upper() if b.level else "EMPIRICAL", 0.3)

        # Coherence contribution (approximation)
        coherence_contrib = b.credence.value * (1.0 if b.status and b.status.value.upper() == "ACCEPTED" else 0.5)

        scores.append(EntrenchmentScore(
            belief_id=b.belief_id,
            entrenchment=round(entrenchment, 4),
            components={
                "connectivity": round(connectivity, 3),
                "level_weight": round(level_weight, 3),
                "coherence_contrib": round(coherence_contrib, 3)
            }
        ))

    # Sort by entrenchment descending
    scores.sort(key=lambda x: x.entrenchment, reverse=True)

    # Add ranks
    for i, s in enumerate(scores):
        s.rank = i + 1

    total = len(scores)
    paginated = scores[offset:offset + limit]

    return {
        "scores": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@entrenchment_router.get("/belief/{belief_id}", response_model=EntrenchmentScore)
async def get_belief_entrenchment(belief_id: str):
    """Get detailed entrenchment score for a specific belief."""
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    b = web.beliefs[belief_id]
    entrenchment = web.get_entrenchment(belief_id)

    # Compute components
    n_constraints = sum(
        1 for c in web.constraints.values()
        if c.source_id == belief_id or c.target_id == belief_id
    )
    max_constraints = max(len(web.beliefs), 1) * 2
    connectivity = min(n_constraints / max_constraints, 1.0)

    level_weights = {
        "THEORETICAL": 0.8,
        "INTERMEDIATE": 0.5,
        "EMPIRICAL": 0.3,
        "OBSERVATIONAL": 0.2
    }
    level_weight = level_weights.get(b.level.value.upper() if b.level else "EMPIRICAL", 0.3)

    coherence_contrib = b.credence.value * (1.0 if b.status and b.status.value.upper() == "ACCEPTED" else 0.5)

    # Calculate rank
    all_entrenchments = [(bid, web.get_entrenchment(bid)) for bid in web.beliefs]
    all_entrenchments.sort(key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (bid, _) in enumerate(all_entrenchments) if bid == belief_id), None)

    return EntrenchmentScore(
        belief_id=belief_id,
        entrenchment=round(entrenchment, 4),
        components={
            "connectivity": round(connectivity, 3),
            "level_weight": round(level_weight, 3),
            "coherence_contrib": round(coherence_contrib, 3)
        },
        rank=rank
    )


@entrenchment_router.get("/compare", response_model=EntrenchmentComparison)
async def compare_entrenchment(
    belief_a: str = Query(..., description="First belief ID"),
    belief_b: str = Query(..., description="Second belief ID")
):
    """Compare entrenchment between two beliefs."""
    web = get_web()

    if belief_a not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_a} not found")
    if belief_b not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_b} not found")

    ent_a = web.get_entrenchment(belief_a)
    ent_b = web.get_entrenchment(belief_b)

    return EntrenchmentComparison(
        belief_a=belief_a,
        belief_b=belief_b,
        entrenchment_a=round(ent_a, 4),
        entrenchment_b=round(ent_b, 4),
        difference=round(abs(ent_a - ent_b), 4),
        more_entrenched=belief_a if ent_a > ent_b else belief_b if ent_b > ent_a else "equal"
    )


@entrenchment_router.get("/distribution")
async def get_entrenchment_distribution():
    """Get distribution statistics for entrenchment scores."""
    web = get_web()

    entrenchments = [web.get_entrenchment(bid) for bid in web.beliefs]

    if not entrenchments:
        return {"error": "No beliefs in web"}

    # Calculate distribution stats
    sorted_ent = sorted(entrenchments)
    n = len(sorted_ent)

    distribution = {
        "count": n,
        "min": round(sorted_ent[0], 4),
        "max": round(sorted_ent[-1], 4),
        "mean": round(sum(sorted_ent) / n, 4),
        "median": round(sorted_ent[n // 2], 4),
        "percentiles": {
            "p10": round(sorted_ent[int(n * 0.1)], 4) if n > 10 else None,
            "p25": round(sorted_ent[int(n * 0.25)], 4) if n > 4 else None,
            "p75": round(sorted_ent[int(n * 0.75)], 4) if n > 4 else None,
            "p90": round(sorted_ent[int(n * 0.9)], 4) if n > 10 else None,
        },
        "histogram": _compute_histogram(entrenchments, bins=10)
    }

    return distribution


def _compute_histogram(values: List[float], bins: int = 10) -> List[Dict[str, Any]]:
    """Compute histogram of values."""
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / bins if max_val > min_val else 1

    histogram = []
    for i in range(bins):
        bin_start = min_val + i * bin_width
        bin_end = bin_start + bin_width
        count = sum(1 for v in values if bin_start <= v < bin_end)
        if i == bins - 1:  # Include max in last bin
            count += sum(1 for v in values if v == max_val)
        histogram.append({
            "bin": i,
            "start": round(bin_start, 3),
            "end": round(bin_end, 3),
            "count": count
        })

    return histogram


# =============================================================================
# Graph Endpoints (4 endpoints)
# =============================================================================


@graph_router.get("/structure", response_model=GraphStructure)
async def get_graph_structure(
    include_theories: bool = Query(default=True),
    min_credence: float = Query(default=0.0, ge=0.0, le=1.0),
    max_nodes: int = Query(default=100, ge=1, le=500)
):
    """
    Get the belief graph structure for visualization.

    Returns nodes (beliefs, optionally theories) and edges (constraints).
    """
    web = get_web()

    nodes = []
    edges = []

    # Add belief nodes
    beliefs = [
        b for b in web.beliefs.values()
        if b.credence.value >= min_credence
    ]

    # Sort by credence and limit
    beliefs = sorted(beliefs, key=lambda x: x.credence.value, reverse=True)[:max_nodes]
    belief_ids = {b.belief_id for b in beliefs}

    for b in beliefs:
        nodes.append(GraphNode(
            id=b.belief_id,
            label=b.content[:50] + "..." if len(b.content) > 50 else b.content,
            type="belief",
            credence=b.credence.value,
            entrenchment=web.get_entrenchment(b.belief_id),
            level=b.level.value.upper() if b.level else None
        ))

    # Add theory nodes if requested
    if include_theories:
        theory_ids = set()
        for b in beliefs:
            if b.theory_id:
                theory_ids.add(b.theory_id)

        for tid in theory_ids:
            nodes.append(GraphNode(
                id=f"theory:{tid}",
                label=tid.replace("_", " ").title(),
                type="theory",
                credence=None,
                entrenchment=None,
                level="theory"
            ))

    # Add edges for constraints
    for c in web.constraints.values():
        if c.source_id in belief_ids and c.target_id in belief_ids:
            edges.append(GraphEdge(
                source=c.source_id,
                target=c.target_id,
                polarity=c.polarity.value.upper(),
                strength=c.strength
            ))

    # Add theory membership edges
    if include_theories:
        for b in beliefs:
            if b.theory_id:
                edges.append(GraphEdge(
                    source=b.belief_id,
                    target=f"theory:{b.theory_id}",
                    polarity="MEMBER",
                    strength=1.0
                ))

    metadata = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "belief_count": len(belief_ids),
        "theory_count": len([n for n in nodes if n.type == "theory"]),
        "generated_at": datetime.now().isoformat()
    }

    return GraphStructure(nodes=nodes, edges=edges, metadata=metadata)


@graph_router.get("/neighbors/{belief_id}")
async def get_belief_neighbors(
    belief_id: str,
    depth: int = Query(default=1, ge=1, le=3)
):
    """Get neighboring beliefs up to specified depth."""
    web = get_web()

    if belief_id not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {belief_id} not found")

    visited = {belief_id}
    current_level = {belief_id}
    levels = []

    for d in range(depth):
        next_level = set()
        level_info = []

        for bid in current_level:
            # Find constraints involving this belief
            for c in web.constraints.values():
                neighbor = None
                direction = None

                if c.source_id == bid and c.target_id not in visited:
                    neighbor = c.target_id
                    direction = "outgoing"
                elif c.target_id == bid and c.source_id not in visited:
                    neighbor = c.source_id
                    direction = "incoming"

                if neighbor:
                    next_level.add(neighbor)
                    visited.add(neighbor)

                    if neighbor in web.beliefs:
                        b = web.beliefs[neighbor]
                        level_info.append({
                            "belief_id": neighbor,
                            "content": b.content[:100],
                            "credence": b.credence.value,
                            "direction": direction,
                            "from_belief": bid,
                            "polarity": c.polarity.value.upper(),
                            "strength": c.strength
                        })

        levels.append(level_info)
        current_level = next_level

        if not current_level:
            break

    return {
        "center": belief_id,
        "depth": depth,
        "levels": levels,
        "total_neighbors": len(visited) - 1
    }


@graph_router.get("/path", response_model=PathInfo)
async def find_path(
    source: str = Query(..., description="Source belief ID"),
    target: str = Query(..., description="Target belief ID")
):
    """Find shortest path between two beliefs."""
    web = get_web()

    if source not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {source} not found")
    if target not in web.beliefs:
        raise HTTPException(status_code=404, detail=f"Belief {target} not found")

    # BFS to find shortest path
    from collections import deque

    # Build adjacency list
    adj: Dict[str, List[tuple]] = {bid: [] for bid in web.beliefs}
    for c in web.constraints.values():
        if c.source_id in adj and c.target_id in adj:
            adj[c.source_id].append((c.target_id, c.strength))
            adj[c.target_id].append((c.source_id, c.strength))

    # BFS
    queue = deque([(source, [source], 0.0)])
    visited = {source}

    while queue:
        current, path, total_strength = queue.popleft()

        if current == target:
            return PathInfo(
                source=source,
                target=target,
                path_exists=True,
                path=path,
                length=len(path) - 1,
                total_strength=round(total_strength, 3)
            )

        for neighbor, strength in adj[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], total_strength + strength))

    return PathInfo(
        source=source,
        target=target,
        path_exists=False,
        path=[],
        length=-1,
        total_strength=0.0
    )


@graph_router.get("/clusters")
async def get_belief_clusters(
    algorithm: str = Query(default="connected", pattern="^(connected|theory)$")
):
    """Get belief clusters (connected components or by theory)."""
    web = get_web()

    if algorithm == "theory":
        # Cluster by theory
        clusters: Dict[str, List[str]] = {}
        no_theory = []

        for b in web.beliefs.values():
            if b.theory_id:
                if b.theory_id not in clusters:
                    clusters[b.theory_id] = []
                clusters[b.theory_id].append(b.belief_id)
            else:
                no_theory.append(b.belief_id)

        result = [
            {
                "cluster_id": tid,
                "name": tid.replace("_", " ").title(),
                "belief_ids": bids,
                "size": len(bids)
            }
            for tid, bids in clusters.items()
        ]

        if no_theory:
            result.append({
                "cluster_id": "no_theory",
                "name": "Unaffiliated",
                "belief_ids": no_theory,
                "size": len(no_theory)
            })

        return {"algorithm": "theory", "clusters": result, "cluster_count": len(result)}

    else:
        # Connected components
        adj: Dict[str, set] = {bid: set() for bid in web.beliefs}
        for c in web.constraints.values():
            if c.source_id in adj and c.target_id in adj:
                adj[c.source_id].add(c.target_id)
                adj[c.target_id].add(c.source_id)

        visited = set()
        clusters = []

        for bid in web.beliefs:
            if bid in visited:
                continue

            # BFS to find component
            component = []
            queue = [bid]
            while queue:
                current = queue.pop()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                for neighbor in adj[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

            clusters.append({
                "cluster_id": f"cluster_{len(clusters)}",
                "belief_ids": component,
                "size": len(component)
            })

        # Sort by size descending
        clusters.sort(key=lambda x: x["size"], reverse=True)

        return {"algorithm": "connected", "clusters": clusters, "cluster_count": len(clusters)}


# =============================================================================
# Export Bundle Endpoints (4 endpoints)
# =============================================================================


@bundles_router.get("/purposes")
async def list_bundle_purposes():
    """List available export bundle purposes."""
    if _export_bundles_available:
        purposes = list_purposes()
        return {"purposes": purposes}
    else:
        # Fallback
        return {
            "purposes": [
                {"purpose": "practitioner_briefing", "name": "Practitioner Briefing", "description": "Quick guidance for practitioners"},
                {"purpose": "literature_review", "name": "Literature Review", "description": "Academic synthesis"},
                {"purpose": "systematic_review", "name": "Systematic Review", "description": "PRISMA-compatible"},
                {"purpose": "data_pipeline", "name": "Data Pipeline", "description": "Machine-readable"},
                {"purpose": "presentation", "name": "Presentation", "description": "Visual summaries"},
                {"purpose": "teaching_materials", "name": "Teaching Materials", "description": "Educational resources"},
                {"purpose": "grant_writing", "name": "Grant Writing", "description": "Research proposals"},
                {"purpose": "policy_brief", "name": "Policy Brief", "description": "Policy summaries"},
            ]
        }


@bundles_router.post("/", response_model=ExportBundleResponse)
async def create_export_bundle(request: ExportBundleRequest):
    """
    Generate an export bundle for a specific purpose.

    Uses the Munzner-based export_bundles module for purpose-driven generation.
    """
    web = get_web()

    # Gather beliefs
    if request.belief_ids:
        beliefs = [
            web.beliefs[bid] for bid in request.belief_ids
            if bid in web.beliefs and web.beliefs[bid].credence.value >= request.min_credence
        ]
    else:
        beliefs = [
            b for b in web.beliefs.values()
            if b.credence.value >= request.min_credence
        ]

    # Convert beliefs to dicts
    belief_dicts = []
    for b in beliefs:
        belief_dicts.append({
            "id": b.belief_id,
            "content": b.content,
            "credence": b.credence.value,
            "uncertainty": b.credence.uncertainty,
            "status": b.status.value.upper() if b.status else "STUB",
            "level": b.level.value.upper() if b.level else "EMPIRICAL",
            "theory": b.theory_id,
            "sources": b.paper_ids or [],
            "constraints": []
        })

    # Gather sources
    source_dicts = []
    paper_ids = set()
    for b in beliefs:
        if b.paper_ids:
            paper_ids.update(b.paper_ids)

    # Try to get paper details from database
    if paper_ids:
        try:
            conn = _get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            for pid in paper_ids:
                cursor.execute("""
                    SELECT article_id, title, authors, year, venue, doi
                    FROM articles WHERE article_id = ?
                """, (pid,))
                row = cursor.fetchone()
                if row:
                    authors = json.loads(row['authors']) if row['authors'] else []
                    source_dicts.append({
                        "paper_id": row['article_id'],
                        "title": row['title'],
                        "authors": authors,
                        "year": row['year'],
                        "journal": row['venue'],
                        "doi": row['doi']
                    })

            conn.close()
        except Exception as e:
            logger.warning(f"Could not fetch paper details: {e}")

    # Generate bundle
    bundle_id = f"bundle_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if _export_bundles_available:
        try:
            bundle = generate_bundle(
                purpose=request.purpose,
                topic=request.topic,
                beliefs=belief_dicts,
                sources=source_dicts
            )

            return ExportBundleResponse(
                bundle_id=bundle_id,
                topic=request.topic,
                purpose=request.purpose,
                generated_at=bundle.generated_at,
                file_count=len(bundle.files),
                files=[
                    {
                        "filename": f.filename,
                        "format": f.format,
                        "description": f.description,
                        "size_bytes": len(f.content.encode("utf-8"))
                    }
                    for f in bundle.files
                ],
                warnings=bundle.warnings
            )
        except Exception as e:
            logger.error(f"Bundle generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Bundle generation failed: {str(e)}")
    else:
        # Fallback simple bundle
        return ExportBundleResponse(
            bundle_id=bundle_id,
            topic=request.topic,
            purpose=request.purpose,
            generated_at=datetime.now().isoformat(),
            file_count=1,
            files=[{"filename": "summary.md", "format": "markdown", "description": "Summary"}],
            warnings=["export_bundles module not available, using fallback"]
        )


@bundles_router.get("/{bundle_id}/download")
async def download_bundle(
    bundle_id: str,
    format: str = Query(default="zip", pattern="^(zip|tar)$")
):
    """Download a complete export bundle."""
    # This would integrate with actual file storage
    raise HTTPException(status_code=501, detail="Bundle download not yet implemented - use individual file endpoints")


@bundles_router.post("/bibtex")
async def generate_bibtex_export(
    belief_ids: Optional[List[str]] = None,
    min_credence: float = Query(default=0.0, ge=0.0, le=1.0)
):
    """Generate BibTeX export for belief sources."""
    web = get_web()

    # Gather paper IDs
    paper_ids = set()

    if belief_ids:
        for bid in belief_ids:
            if bid in web.beliefs and web.beliefs[bid].paper_ids:
                paper_ids.update(web.beliefs[bid].paper_ids)
    else:
        for b in web.beliefs.values():
            if b.credence.value >= min_credence and b.paper_ids:
                paper_ids.update(b.paper_ids)

    # Get paper details
    papers = []
    if paper_ids:
        try:
            conn = _get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            for pid in paper_ids:
                cursor.execute("""
                    SELECT article_id, title, authors, year, venue, doi
                    FROM articles WHERE article_id = ?
                """, (pid,))
                row = cursor.fetchone()
                if row:
                    authors = json.loads(row['authors']) if row['authors'] else []
                    papers.append({
                        "paper_id": row['article_id'],
                        "title": row['title'],
                        "authors": authors,
                        "year": row['year'],
                        "journal": row['venue'],
                        "doi": row['doi']
                    })

            conn.close()
        except Exception as e:
            logger.warning(f"Could not fetch paper details: {e}")

    # Generate BibTeX
    if _bibtex_available and papers:
        bibtex = export_papers_to_bibtex(papers)
    else:
        # Fallback simple generation
        entries = []
        for p in papers:
            authors = p.get("authors", [])
            year = p.get("year", "")
            first_author = authors[0].split()[-1].lower() if authors else "unknown"
            cite_key = f"{first_author}{year}"

            entry = [f"@article{{{cite_key},"]
            if authors:
                entry.append(f"  author = {{{' and '.join(authors)}}},")
            entry.append(f"  title = {{{p.get('title', '')}}},")
            if year:
                entry.append(f"  year = {{{year}}},")
            if p.get("doi"):
                entry.append(f"  doi = {{{p.get('doi')}}},")
            entry.append("}")
            entries.append("\n".join(entry))

        bibtex = "\n\n".join(entries)

    return Response(
        content=bibtex,
        media_type="application/x-bibtex",
        headers={"Content-Disposition": "attachment; filename=references.bib"}
    )


# =============================================================================
# History Endpoints (4 endpoints)
# =============================================================================

# In-memory snapshot storage (would be database in production)
_snapshots: Dict[str, Dict[str, Any]] = {}


@history_router.post("/snapshots", response_model=SnapshotResponse)
async def create_snapshot(description: Optional[str] = None):
    """Create a snapshot of the current web of belief state."""
    web = get_web()

    # Serialize current state
    state = {
        "beliefs": {
            bid: {
                "content": b.content,
                "credence": b.credence.value,
                "status": b.status.value if b.status else None,
                "level": b.level.value if b.level else None,
                "theory_id": b.theory_id
            }
            for bid, b in web.beliefs.items()
        },
        "constraints": {
            cid: {
                "source": c.source_id,
                "target": c.target_id,
                "polarity": c.polarity.value,
                "strength": c.strength
            }
            for cid, c in web.constraints.items()
        }
    }

    # Generate hash
    state_json = json.dumps(state, sort_keys=True)
    state_hash = hashlib.sha256(state_json.encode()).hexdigest()[:12]

    snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    snapshot = {
        "id": snapshot_id,
        "created_at": datetime.now().isoformat(),
        "belief_count": len(state["beliefs"]),
        "constraint_count": len(state["constraints"]),
        "description": description,
        "hash": state_hash,
        "state": state
    }

    _snapshots[snapshot_id] = snapshot

    return SnapshotResponse(
        snapshot_id=snapshot_id,
        created_at=snapshot["created_at"],
        belief_count=snapshot["belief_count"],
        constraint_count=snapshot["constraint_count"],
        description=description,
        hash=state_hash
    )


@history_router.get("/snapshots")
async def list_snapshots():
    """List all available snapshots."""
    snapshots = [
        SnapshotResponse(
            snapshot_id=s["id"],
            created_at=s["created_at"],
            belief_count=s["belief_count"],
            constraint_count=s["constraint_count"],
            description=s.get("description"),
            hash=s["hash"]
        )
        for s in sorted(_snapshots.values(), key=lambda x: x["created_at"], reverse=True)
    ]

    return {"snapshots": snapshots, "total": len(snapshots)}


@history_router.get("/snapshots/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(snapshot_id: str):
    """Get details for a specific snapshot."""
    if snapshot_id not in _snapshots:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")

    s = _snapshots[snapshot_id]

    return SnapshotResponse(
        snapshot_id=s["id"],
        created_at=s["created_at"],
        belief_count=s["belief_count"],
        constraint_count=s["constraint_count"],
        description=s.get("description"),
        hash=s["hash"]
    )


@history_router.get("/diff", response_model=SnapshotDiff)
async def diff_snapshots(
    from_snapshot: str = Query(..., description="Earlier snapshot ID"),
    to_snapshot: str = Query(..., description="Later snapshot ID")
):
    """Get the difference between two snapshots."""
    if from_snapshot not in _snapshots:
        raise HTTPException(status_code=404, detail=f"Snapshot {from_snapshot} not found")
    if to_snapshot not in _snapshots:
        raise HTTPException(status_code=404, detail=f"Snapshot {to_snapshot} not found")

    from_state = _snapshots[from_snapshot]["state"]
    to_state = _snapshots[to_snapshot]["state"]

    changes = []
    summary = {"added": 0, "removed": 0, "modified": 0}

    # Compare beliefs
    from_beliefs = set(from_state["beliefs"].keys())
    to_beliefs = set(to_state["beliefs"].keys())

    for bid in to_beliefs - from_beliefs:
        changes.append(DiffEntry(
            type="added",
            entity_type="belief",
            entity_id=bid,
            details=to_state["beliefs"][bid]
        ))
        summary["added"] += 1

    for bid in from_beliefs - to_beliefs:
        changes.append(DiffEntry(
            type="removed",
            entity_type="belief",
            entity_id=bid,
            details=from_state["beliefs"][bid]
        ))
        summary["removed"] += 1

    for bid in from_beliefs & to_beliefs:
        if from_state["beliefs"][bid] != to_state["beliefs"][bid]:
            changes.append(DiffEntry(
                type="modified",
                entity_type="belief",
                entity_id=bid,
                details={
                    "from": from_state["beliefs"][bid],
                    "to": to_state["beliefs"][bid]
                }
            ))
            summary["modified"] += 1

    # Compare constraints
    from_constraints = set(from_state["constraints"].keys())
    to_constraints = set(to_state["constraints"].keys())

    for cid in to_constraints - from_constraints:
        changes.append(DiffEntry(
            type="added",
            entity_type="constraint",
            entity_id=cid,
            details=to_state["constraints"][cid]
        ))
        summary["added"] += 1

    for cid in from_constraints - to_constraints:
        changes.append(DiffEntry(
            type="removed",
            entity_type="constraint",
            entity_id=cid,
            details=from_state["constraints"][cid]
        ))
        summary["removed"] += 1

    return SnapshotDiff(
        from_snapshot=from_snapshot,
        to_snapshot=to_snapshot,
        changes=changes,
        summary=summary
    )


# =============================================================================
# Router Aggregation
# =============================================================================


def get_extended_router() -> APIRouter:
    """Get the extended API router with all sub-routers."""
    router = APIRouter(prefix="/api/v1")

    router.include_router(theories_router)
    router.include_router(entrenchment_router)
    router.include_router(graph_router)
    router.include_router(bundles_router)
    router.include_router(history_router)

    return router


# Convenience export
extended_router = get_extended_router()
