"""
Output Serialization for Article Eater Pipeline

Sprint 2.0.2: Comprehensive output serialization for all pipeline outputs.

This module provides:
1. Manifest generation - tracks all outputs with schemas and checksums
2. Enhanced belief serialization with TD module data
3. Cluster statistics export (TD-C)
4. BN edge serialization with uncertainty (TD-E)
5. Theory inference audit trails (TD-A)
6. Scope condition exports (TD-B)
7. Temporal expression exports (TD-D)

All outputs follow a consistent structure:
{
    "schema": "ae.<type>.v1",
    "run_id": "...",
    "paper_id": "...",
    "created_at": "ISO timestamp",
    ...content...
}
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SCHEMA VERSIONS
# =============================================================================

SCHEMA_VERSIONS = {
    "manifest": "ae.manifest.v1",
    "web_state": "ae.web_state.v1",
    "coherence_summary": "ae.coherence_summary.v1",
    "theory_inference": "ae.theory_inference.v1",
    "scope_export": "ae.scope_export.v1",
    "temporal_export": "ae.temporal_export.v1",
    "cluster_stats": "ae.cluster_stats.v1",
    "bn_edges": "ae.bn_edges.v1",
    "claim": "ae.claim.v1",
    "rule": "ae.rule.v1",
    "stub": "ae.stub.v1",
    "tension": "ae.tension.v1",
    "bridge": "ae.bridge.v1",
    "anomaly": "ae.anomaly.v1",
}


# =============================================================================
# MANIFEST GENERATION
# =============================================================================

@dataclass
class OutputFile:
    """Metadata about an output file."""
    filename: str
    schema: str
    description: str
    record_count: int = 0
    sha256: Optional[str] = None
    size_bytes: int = 0


def _sha256_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def generate_manifest(
    out_dir: Path,
    run_id: str,
    paper_id: str,
    outputs: Dict[str, OutputFile]
) -> Dict[str, Any]:
    """
    Generate a manifest file listing all outputs.

    The manifest provides:
    - List of all output files with their schemas
    - Record counts for JSONL files
    - SHA256 checksums for verification
    - Run metadata for reproducibility
    """
    files = []
    for name, output in outputs.items():
        file_path = out_dir / output.filename
        if file_path.exists():
            output.sha256 = _sha256_file(file_path)
            output.size_bytes = file_path.stat().st_size

        files.append({
            "filename": output.filename,
            "schema": output.schema,
            "description": output.description,
            "record_count": output.record_count,
            "sha256": output.sha256,
            "size_bytes": output.size_bytes,
            "exists": file_path.exists() if file_path else False,
        })

    manifest = {
        "schema": SCHEMA_VERSIONS["manifest"],
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "generator": "article_eater.output_serializer",
        "generator_version": "2.0.2",
        "files": files,
        "file_count": len([f for f in files if f["exists"]]),
        "total_size_bytes": sum(f["size_bytes"] for f in files),
    }

    return manifest


# =============================================================================
# THEORY INFERENCE EXPORT (TD-A)
# =============================================================================

def serialize_theory_inference(
    mapping_results: List[Dict[str, Any]],
    run_id: str,
    paper_id: str
) -> Dict[str, Any]:
    """
    Serialize theory inference results with full audit trail.

    Exports:
    - Theory scores for each claim
    - Inference method used (legacy/embedding/hybrid)
    - Disambiguation actions taken
    - Review flags for human follow-up
    """
    inferences = []
    for result in mapping_results:
        inferences.append({
            "entity_id": result.get("entity_id"),
            "theory_inferences": result.get("theory_inferences", {}),
            "primary_theory_id": result.get("primary_theory_id"),
            "theory_ids": result.get("theory_ids", {}),
            "inference_method": result.get("theory_inference_method", "legacy"),
            "confidence": result.get("theory_confidence", 0.0),
            "needs_review": result.get("needs_theory_review", False),
            "review_reason": result.get("theory_review_reason"),
            "disambiguation_applied": result.get("disambiguation_applied", False),
            "inference_trace": result.get("inference_trace", []),
            "is_stub": result.get("is_stub", False),
            "stub_reason": result.get("stub_reason"),
        })

    # Aggregate statistics
    methods_used = {}
    for inf in inferences:
        method = inf["inference_method"]
        methods_used[method] = methods_used.get(method, 0) + 1

    needs_review = [i for i in inferences if i["needs_review"]]
    disambiguated = [i for i in inferences if i["disambiguation_applied"]]

    return {
        "schema": SCHEMA_VERSIONS["theory_inference"],
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "n_inferences": len(inferences),
        "n_needs_review": len(needs_review),
        "n_disambiguated": len(disambiguated),
        "methods_used": methods_used,
        "inferences": inferences,
        "review_queue": [i["entity_id"] for i in needs_review],
    }


# =============================================================================
# SCOPE EXPORT (TD-B)
# =============================================================================

def serialize_scope_conditions(
    beliefs_with_scope: List[Dict[str, Any]],
    run_id: str,
    paper_id: str
) -> Dict[str, Any]:
    """
    Serialize scope condition extractions.

    Exports:
    - Extracted population, setting, geography, measurement
    - Whether scope was explicitly stated or inferred
    - Generalization risk scores
    """
    scopes = []
    for belief in beliefs_with_scope:
        scope = belief.get("scope", {})
        if isinstance(scope, dict):
            scopes.append({
                "belief_id": belief.get("belief_id"),
                "population": scope.get("population"),
                "setting": scope.get("setting"),
                "geography": scope.get("geography"),
                "measurement": scope.get("measurement"),
                "scope_specified": scope.get("scope_specified", False),
                "explicit_fields": scope.get("explicit_fields", []),
                "generalization_risk": scope.get("generalization_risk"),
            })

    # Aggregate statistics
    n_specified = sum(1 for s in scopes if s.get("scope_specified"))
    n_with_population = sum(1 for s in scopes if s.get("population"))
    n_with_setting = sum(1 for s in scopes if s.get("setting"))

    return {
        "schema": SCHEMA_VERSIONS["scope_export"],
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "n_beliefs": len(scopes),
        "n_scope_specified": n_specified,
        "n_with_population": n_with_population,
        "n_with_setting": n_with_setting,
        "scope_coverage": n_specified / len(scopes) if scopes else 0.0,
        "scopes": scopes,
    }


# =============================================================================
# TEMPORAL EXPORT (TD-D)
# =============================================================================

def serialize_temporal_expressions(
    claims_with_temporal: List[Dict[str, Any]],
    run_id: str,
    paper_id: str
) -> Dict[str, Any]:
    """
    Serialize temporal expression extractions.

    Exports:
    - Duration mentions (normalized to minutes)
    - Frequency patterns
    - Exposure type classifications (acute/subacute/chronic/residential)
    - Temporal relations (before/after/during)
    """
    temporal_data = []
    for claim in claims_with_temporal:
        temporal = claim.get("temporal", {})
        if temporal:
            temporal_data.append({
                "claim_id": claim.get("claim_id"),
                "duration_minutes": temporal.get("duration_minutes"),
                "duration_text": temporal.get("duration_text"),
                "duration_confidence": temporal.get("duration_confidence"),
                "frequency": temporal.get("frequency"),
                "frequency_per_week": temporal.get("frequency_per_week"),
                "exposure_type": temporal.get("exposure_type"),
                "temporal_relations": temporal.get("relations", []),
                "study_duration_minutes": temporal.get("study_duration_minutes"),
            })

    # Aggregate by exposure type
    exposure_types = {}
    for t in temporal_data:
        exp_type = t.get("exposure_type", "unknown")
        exposure_types[exp_type] = exposure_types.get(exp_type, 0) + 1

    return {
        "schema": SCHEMA_VERSIONS["temporal_export"],
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "n_claims": len(temporal_data),
        "n_with_duration": sum(1 for t in temporal_data if t.get("duration_minutes")),
        "n_with_frequency": sum(1 for t in temporal_data if t.get("frequency")),
        "exposure_type_distribution": exposure_types,
        "temporal_data": temporal_data,
    }


# =============================================================================
# CLUSTER STATS EXPORT (TD-C)
# =============================================================================

def serialize_cluster_stats(
    coherence_manager: Any,
    run_id: str,
    paper_id: str
) -> Dict[str, Any]:
    """
    Serialize coherence cluster statistics.

    Exports:
    - Cluster sizes and types
    - Cache performance metrics
    - Computation timing
    - Cross-cluster constraint patterns
    """
    if coherence_manager is None:
        return {
            "schema": SCHEMA_VERSIONS["cluster_stats"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": False,
            "reason": "CoherenceManager not initialized",
        }

    try:
        stats = coherence_manager.stats()

        # Extract cluster details
        cluster_details = []
        if hasattr(coherence_manager, 'clusters') and hasattr(coherence_manager.clusters, 'clusters'):
            for cid, cluster in coherence_manager.clusters.clusters.items():
                cluster_details.append({
                    "cluster_id": cid,
                    "cluster_type": cluster.cluster_type.value if hasattr(cluster.cluster_type, 'value') else str(cluster.cluster_type),
                    "n_beliefs": len(cluster.belief_ids),
                    "n_boundary": len(cluster.boundary_beliefs),
                    "n_connected_clusters": len(cluster.connected_clusters),
                    "intra_coherence": cluster.intra_coherence,
                    "intra_coherence_valid": cluster.intra_coherence_valid,
                })

        return {
            "schema": SCHEMA_VERSIONS["cluster_stats"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": True,
            "network": stats.get("network", {}),
            "clusters_summary": stats.get("clusters", {}),
            "cache": stats.get("cache", {}),
            "performance": stats.get("performance", {}),
            "cluster_details": cluster_details,
        }
    except Exception as e:
        logger.warning(f"Failed to serialize cluster stats: {e}")
        return {
            "schema": SCHEMA_VERSIONS["cluster_stats"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": False,
            "reason": str(e),
        }


# =============================================================================
# BN EDGE EXPORT (TD-E)
# =============================================================================

def serialize_bn_edges(
    bn_builder: Any,
    run_id: str,
    paper_id: str
) -> Dict[str, Any]:
    """
    Serialize BN edge parameters with uncertainty bounds.

    Exports:
    - Edge strength estimates (posterior mean)
    - 95% credible intervals
    - Number of supporting/contradicting papers
    - Uncertainty classification (high/medium/low)
    """
    if bn_builder is None:
        return {
            "schema": SCHEMA_VERSIONS["bn_edges"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": False,
            "reason": "IncrementalBNBuilder not initialized",
        }

    try:
        edges = []
        uncertain_edges = []
        reliable_edges = []

        for key, edge in bn_builder.edges.items():
            ci_lower, ci_upper = edge.credible_interval(0.95)
            uncertainty = ci_upper - ci_lower

            edge_data = {
                "source": edge.source,
                "target": edge.target,
                "edge_type": edge.edge_type.value if hasattr(edge.edge_type, 'value') else str(edge.edge_type),
                "mean": edge.mean,
                "variance": edge.variance,
                "ci_95_lower": ci_lower,
                "ci_95_upper": ci_upper,
                "uncertainty": uncertainty,
                "n_papers": edge.n_papers,
                "paper_ids": list(edge.paper_ids),
                "is_reliable": edge.is_reliable,
                "effective_sample_size": edge.effective_sample_size,
            }
            edges.append(edge_data)

            if not edge.is_reliable:
                uncertain_edges.append(edge_data)
            else:
                reliable_edges.append(edge_data)

        # Identify gaps (hypothesized edges with no evidence)
        gaps = bn_builder.identify_gaps() if hasattr(bn_builder, 'identify_gaps') else []
        gap_data = [
            {
                "source": g.source,
                "target": g.target,
                "priority": g.priority,
                "uncertainty": g.uncertainty,
                "relevance": g.relevance,
                "search_queries": g.search_queries if hasattr(g, 'search_queries') else [],
            }
            for g in gaps
        ]

        return {
            "schema": SCHEMA_VERSIONS["bn_edges"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": True,
            "n_edges": len(edges),
            "n_reliable": len(reliable_edges),
            "n_uncertain": len(uncertain_edges),
            "n_gaps": len(gap_data),
            "edges": edges,
            "uncertain_edges": [e["source"] + "→" + e["target"] for e in uncertain_edges],
            "gaps": gap_data,
        }
    except Exception as e:
        logger.warning(f"Failed to serialize BN edges: {e}")
        return {
            "schema": SCHEMA_VERSIONS["bn_edges"],
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "available": False,
            "reason": str(e),
        }


# =============================================================================
# ENHANCED BELIEF SERIALIZATION
# =============================================================================

def serialize_belief_enhanced(
    belief: Any,
    mapping_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Serialize a belief with all TD module enhancements.

    Includes:
    - Standard belief fields
    - Theory inference details (TD-A)
    - Scope conditions (TD-B)
    - Temporal data (TD-D)
    - Task context (Sprint 2.6)
    """
    # Base serialization
    credence_dict = {}
    if hasattr(belief.credence, 'to_dict'):
        credence_dict = belief.credence.to_dict()
    elif hasattr(belief.credence, 'value'):
        credence_dict = {
            "value": belief.credence.value,
            "uncertainty": getattr(belief.credence, 'uncertainty', None),
            "n_supporting": getattr(belief.credence, 'n_supporting', 0),
            "n_contradicting": getattr(belief.credence, 'n_contradicting', 0),
            "n_observations": getattr(belief.credence, 'n_observations', 0)
        }
    else:
        credence_dict = {"value": float(belief.credence)}

    result = {
        "belief_id": belief.belief_id,
        "content": belief.content,
        "level": belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
        "status": belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
        "credence": credence_dict,
        "theory_id": belief.theory_id,
        "entrenchment": belief.entrenchment,
        "paper_ids": getattr(belief, 'paper_ids', []),
        "domain": getattr(belief, 'domain', None),
        "tags": getattr(belief, 'tags', []),
        "created_at": belief.created_at.isoformat() if hasattr(belief, 'created_at') and belief.created_at else None,
    }

    # Add scope conditions if available
    if hasattr(belief, 'scope') and belief.scope:
        scope = belief.scope
        result["scope"] = {
            "population": getattr(scope, 'population', None),
            "setting": getattr(scope, 'setting', None),
            "geography": getattr(scope, 'geography', None),
            "measurement": getattr(scope, 'measurement', None),
            "scope_specified": getattr(scope, 'scope_specified', False),
        }

    # Add environment/outcome IDs if available
    if hasattr(belief, 'environment_id'):
        result["environment_id"] = belief.environment_id
    if hasattr(belief, 'outcome_id'):
        result["outcome_id"] = belief.outcome_id

    # Add mapping result details if provided
    if mapping_result:
        result["theory_inference"] = {
            "method": mapping_result.get("theory_inference_method", "legacy"),
            "confidence": mapping_result.get("theory_confidence", 0.0),
            "all_theories": mapping_result.get("theory_ids", {}),
            "needs_review": mapping_result.get("needs_theory_review", False),
            "disambiguation_applied": mapping_result.get("disambiguation_applied", False),
        }

        # Task context (Sprint 2.6)
        result["task_context"] = {
            "inference_basis": mapping_result.get("inference_basis", "unknown"),
            "review_recommended": mapping_result.get("review_recommended", False),
            "presumed_lab": mapping_result.get("presumed_lab", False),
            "effective_demand": mapping_result.get("effective_demand"),
            "mechanism_only": mapping_result.get("mechanism_only", False),
        }

    return result


# =============================================================================
# MAIN EXPORT FUNCTION
# =============================================================================

@dataclass
class PipelineOutputs:
    """Container for all pipeline outputs."""
    run_id: str
    paper_id: str
    out_dir: Path

    # Core outputs
    claims: List[Dict[str, Any]] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    beliefs: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

    # Integration reports
    web_state: Optional[Dict[str, Any]] = None
    coherence_summary: Optional[Dict[str, Any]] = None

    # TD module outputs
    mapping_results: List[Dict[str, Any]] = field(default_factory=list)
    coherence_manager: Any = None
    bn_builder: Any = None

    # Stubs and tensions
    stubs: List[Dict[str, Any]] = field(default_factory=list)
    tensions: List[Dict[str, Any]] = field(default_factory=list)

    # Bridges and anomalies
    bridges: List[Dict[str, Any]] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)


def export_all_outputs(outputs: PipelineOutputs) -> Dict[str, OutputFile]:
    """
    Export all pipeline outputs with consistent schemas.

    Returns a dict of OutputFile metadata for manifest generation.
    """
    output_files = {}
    out_dir = outputs.out_dir
    run_id = outputs.run_id
    paper_id = outputs.paper_id

    def _write_json(path: Path, data: Dict[str, Any]) -> int:
        """Write JSON and return size."""
        text = json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n"
        path.write_text(text, encoding="utf-8")
        return len(text)

    def _write_jsonl(path: Path, records: List[Dict[str, Any]]) -> int:
        """Write JSONL and return record count."""
        with path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        return len(records)

    # 1. Theory inference export (TD-A)
    if outputs.mapping_results:
        theory_export = serialize_theory_inference(
            outputs.mapping_results, run_id, paper_id
        )
        _write_json(out_dir / "theory_inference.json", theory_export)
        output_files["theory_inference"] = OutputFile(
            filename="theory_inference.json",
            schema=SCHEMA_VERSIONS["theory_inference"],
            description="Theory inference audit trail with confidence scores",
            record_count=len(outputs.mapping_results),
        )

    # 2. Scope export (TD-B)
    beliefs_with_scope = [
        b for b in outputs.beliefs.values()
        if isinstance(b, dict) and b.get("scope")
    ]
    if beliefs_with_scope:
        scope_export = serialize_scope_conditions(
            beliefs_with_scope, run_id, paper_id
        )
        _write_json(out_dir / "scope_export.json", scope_export)
        output_files["scope_export"] = OutputFile(
            filename="scope_export.json",
            schema=SCHEMA_VERSIONS["scope_export"],
            description="Scope condition extractions",
            record_count=len(beliefs_with_scope),
        )

    # 3. Cluster stats export (TD-C)
    cluster_stats = serialize_cluster_stats(
        outputs.coherence_manager, run_id, paper_id
    )
    _write_json(out_dir / "cluster_stats.json", cluster_stats)
    output_files["cluster_stats"] = OutputFile(
        filename="cluster_stats.json",
        schema=SCHEMA_VERSIONS["cluster_stats"],
        description="Coherence cluster statistics and cache performance",
        record_count=len(cluster_stats.get("cluster_details", [])),
    )

    # 4. BN edges export (TD-E)
    bn_edges = serialize_bn_edges(outputs.bn_builder, run_id, paper_id)
    _write_json(out_dir / "bn_edges.json", bn_edges)
    output_files["bn_edges"] = OutputFile(
        filename="bn_edges.json",
        schema=SCHEMA_VERSIONS["bn_edges"],
        description="BN edge parameters with uncertainty bounds",
        record_count=bn_edges.get("n_edges", 0),
    )

    # 5. Generate manifest
    manifest = generate_manifest(out_dir, run_id, paper_id, output_files)
    _write_json(out_dir / "manifest.json", manifest)

    return output_files


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def write_json(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON with consistent formatting."""
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n"
    path.write_text(text, encoding="utf-8")


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> int:
    """Write JSONL and return record count."""
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return len(records)


def read_manifest(out_dir: Path) -> Optional[Dict[str, Any]]:
    """Read a manifest file if it exists."""
    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return None


def verify_outputs(out_dir: Path) -> Dict[str, bool]:
    """Verify all outputs against their manifest checksums."""
    manifest = read_manifest(out_dir)
    if not manifest:
        return {"manifest_exists": False}

    results = {"manifest_exists": True}
    for file_info in manifest.get("files", []):
        filename = file_info["filename"]
        expected_sha = file_info.get("sha256")
        file_path = out_dir / filename

        if not file_path.exists():
            results[filename] = False
        elif expected_sha:
            actual_sha = _sha256_file(file_path)
            results[filename] = (actual_sha == expected_sha)
        else:
            results[filename] = True

    return results
