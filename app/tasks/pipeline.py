
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from app.services.semantic_scholar import search as s2_search
from app.services.embeddings import embed_text, cosine
from app.services.extract_article_essence import extract_findings_from_text
from app.pdf_ingest import extract_pdf_text
from lib.outcome_resolver import resolve_or_queue

# Sprint 2.0.5: Structured error handling and logging
try:
    from src.services.pipeline_logging import (
        configure_logging,
        get_logger,
        PipelineError,
        ExtractionError,
        LLMError,
        ConfigurationError,
        WebIntegrationError,
        SerializationError,
        DatabaseError,
        ValidationError,
        RetryableError,
        ErrorSeverity,
        ErrorCollector,
        pipeline_stage,
        with_retry,
    )
    PIPELINE_LOGGING_AVAILABLE = True
except ImportError:
    PIPELINE_LOGGING_AVAILABLE = False
    # Fallback stubs if logging module not available
    import logging
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(f"ae.{name}")
    class ErrorCollector:
        def __init__(self, run_id, paper_id=None):
            self.errors = []
        def record(self, *args, **kwargs):
            pass
        def to_jsonl(self, path):
            return 0
        def get_summary(self):
            return {"total_errors": 0}

# Initialize main pipeline logger
_pipeline_logger = get_logger("pipeline")

# Paper Lifecycle Tracking (unified pipeline health monitoring)
try:
    from src.services.paper_lifecycle import (
        PaperLifecycleService,
        LifecycleStage,
        StageStatus,
        get_lifecycle_service,
    )
    LIFECYCLE_TRACKING_AVAILABLE = True
except ImportError:
    LIFECYCLE_TRACKING_AVAILABLE = False
    _pipeline_logger.debug("Paper lifecycle tracking not available")

# Sprint 2: Web of Belief integration (Post-Quinean)
# These imports enable coherentist analysis of extracted findings
try:
    from src.services.web_of_belief import WebOfBelief, create_neuroarchitecture_web
    from src.services.extraction_to_web import (
        integrate_extraction,
        export_stubs_jsonl,
        export_tensions_jsonl,
        get_stub_report,
        get_tensions,
        load_outcome_lookup
    )
    WEB_OF_BELIEF_AVAILABLE = True
except ImportError:
    WEB_OF_BELIEF_AVAILABLE = False

# Sprint 3: Bridge Warrants integration
try:
    from src.services.bridge_warrants import (
        BridgeWarrant,
        BridgeRegistry,
        BridgeType,
        BridgeStatus,
        create_bridge,
        detect_bridge_from_claim,
        export_bridges_jsonl,
        create_anomaly_from_bridge_failure,
        export_anomalies_jsonl,
        Anomaly
    )
    BRIDGE_WARRANTS_AVAILABLE = True
except ImportError:
    BRIDGE_WARRANTS_AVAILABLE = False

# Sprint B: Credibility Testing integration (TODO 1)
try:
    from src.services.credibility_testing import (
        CredibilityTester,
        CredibilityReport,
        Decision,
        create_tester,
    )
    CREDIBILITY_TESTING_AVAILABLE = True
except ImportError:
    CREDIBILITY_TESTING_AVAILABLE = False

# Feedback tracking for credibility testing threshold calibration
try:
    from src.services.credibility_feedback import (
        FeedbackTracker,
        create_tracker as create_feedback_tracker,
        get_default_tracker,
    )
    CREDIBILITY_FEEDBACK_AVAILABLE = True
except ImportError:
    CREDIBILITY_FEEDBACK_AVAILABLE = False

# Sprint TD-C: Scalable Coherence (O(n log n) coherence computation)
try:
    from src.services.scalable_coherence import (
        CoherenceManager,
        ClusterManager,
        ConstraintNetwork,
        ClusterType,
    )
    SCALABLE_COHERENCE_AVAILABLE = True
except ImportError:
    SCALABLE_COHERENCE_AVAILABLE = False

# Sprint TD-E: Incremental BN Learning (conjugate prior updates)
try:
    from src.services.incremental_bn import (
        IncrementalBNBuilder,
        BetaBernoulliEdge,
        ActiveLearningScheduler,
        EdgeType,
    )
    INCREMENTAL_BN_AVAILABLE = True
except ImportError:
    INCREMENTAL_BN_AVAILABLE = False

# Sprint ECB: Epistemic-Causal Bridge (Quinean→Pearlian integration)
# ECB-F14 (Parnas): Lazy import to isolate failures - module imported inside function
# The CAUSAL_BRIDGE_AVAILABLE flag is set dynamically when first needed
CAUSAL_BRIDGE_AVAILABLE = None  # Will be set on first use

# Sprint 2.0.2: Output Serialization
try:
    from src.services.output_serializer import (
        PipelineOutputs,
        export_all_outputs,
        serialize_theory_inference,
        serialize_scope_conditions,
        serialize_temporal_expressions,
        serialize_cluster_stats,
        serialize_bn_edges,
        generate_manifest,
        OutputFile,
        SCHEMA_VERSIONS,
    )
    OUTPUT_SERIALIZER_AVAILABLE = True
except ImportError:
    OUTPUT_SERIALIZER_AVAILABLE = False

# TBL-4: Table Extraction integration (Sprint 3.0)
try:
    from src.services.table_to_claims import (
        PipelineTableIntegrator,
        TableExtractionResult,
        TableClaim,
        extract_tables_for_pipeline,
        export_tables_jsonl,
        export_table_claims_jsonl,
    )
    from src.services.table_extractor import (
        ExtractedTable,
        ExtractionMethod,
    )
    TABLE_EXTRACTION_AVAILABLE = True
except ImportError:
    TABLE_EXTRACTION_AVAILABLE = False

DB = os.environ.get("AE_DB", "ae.db")
BN_EXPORT_VERSION = "0.2"
BN_EXPORT_GENERATOR = "article_eater_rulegraph_v2"

def _conn():
    return sqlite3.connect(DB)


def _resolve_db_path() -> Path:
    db = os.environ.get("AE_DB_PATH") or os.environ.get("AE_DB") or os.environ.get("DB_PATH")
    if not db:
        db_url = os.environ.get("DB_URL")
        if db_url and db_url.startswith("sqlite:///"):
            db = db_url.replace("sqlite:///", "", 1)
    return Path(db or "ae.db").expanduser().resolve()


def _db_has_table(con: sqlite3.Connection, name: str) -> bool:
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None


def _load_rules_from_db(db_path: Path, paper_id: str) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    con = sqlite3.connect(str(db_path))
    try:
        if not _db_has_table(con, "rules"):
            return []
        cur = con.cursor()
        cur.execute(
            """
            SELECT rule_id, rule, confidence, triangulation_score, contradiction_count, job_id, created_at
            FROM rules
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        if not rows:
            return []
        rules: List[Dict[str, Any]] = []
        for row in rows:
            rule_id, rule_text, confidence, _, _, _, _ = row
            lhs = []
            rhs = []
            if rule_text and "->" in rule_text:
                parts = [p.strip() for p in rule_text.split("->", 1)]
                lhs_raw = [p.strip() for p in parts[0].split(",")] if parts[0] else []
                lhs = [{"var": v, "state": "present"} for v in lhs_raw if v]
                rhs = [{"var": parts[1], "state": "present"}] if parts[1] else []
            rules.append(
                {
                    "schema": "ae.rule.v1",
                    "rule_id": str(rule_id),
                    "paper_id": paper_id,
                    "rule_type": "edge",
                    "statement": rule_text or "",
                    "lhs": lhs,
                    "rhs": rhs,
                    "polarity": "unknown",
                    "strength": {
                        "kind": "confidence" if confidence is not None else "unknown",
                        "type": None,
                        "value": float(confidence) if confidence is not None else None,
                    },
                    "applicability": {"population": [], "setting": [], "boundary_conditions": []},
                    "evidence_links": [],
                    "bn_mapping": {"node_suggestions": [], "discretization_hint": "unknown"},
                    "ae_confidence": float(confidence) if confidence is not None else 0.0,
                }
            )
        return rules
    finally:
        con.close()

def _bn_export_from_rules(rules: List[Dict[str, Any]], paper_id: str) -> Dict[str, Any]:
    nodes = []
    edges = []
    export_rules = []
    for rule in rules:
        rule_id = str(rule.get("rule_id") or "")
        rule_text = rule.get("statement") or rule.get("rule") or rule.get("rule_text") or ""
        node_id = f"rule:{paper_id}:{rule_id}" if rule_id else f"rule:{paper_id}"
        nodes.append({"id": node_id, "type": "rule", "label": rule_text or node_id})
        export_rules.append(
            {
                "rule_id": rule_id,
                "paper_id": paper_id,
                "rule_text": rule_text,
                "subject_scope": {},
                "subject_moderators": [],
                "subject_scope_summary": "",
                "moderators_summary": "",
                "evidence": {"links": rule.get("evidence_links") or []},
                "provenance": {"source": "ae.rules"},
                "graph_version": "2.0",
                "status": "accepted",
            }
        )
    return {
        "bn_version": BN_EXPORT_VERSION,
        "generator": BN_EXPORT_GENERATOR,
        "filters": {"paper_id": paper_id, "text_filter": None, "age_band": None, "trait": None},
        "meta": {"rules_count": len(export_rules), "papers": [paper_id]},
        "nodes": nodes,
        "edges": edges,
        "rules": export_rules,
    }


# =============================================================================
# SPRINT 2: WEB OF BELIEF INTEGRATION (Expert Panel Revised 2026-01-18)
# =============================================================================

# Logging for web integration (Decision 2.2: WARNING-level on failure)
import logging
_web_logger = logging.getLogger("ae.web_integration")

# Equilibrium configuration (Decision 2.5: Make configurable)
WEB_SEEK_EQUILIBRIUM = os.environ.get("AE_WEB_SEEK_EQUILIBRIUM", "true").lower() == "true"
WEB_EQUILIBRIUM_MAX_ITERATIONS = int(os.environ.get("AE_WEB_EQUILIBRIUM_MAX_ITERATIONS", "10"))
WEB_EQUILIBRIUM_CONVERGENCE_THRESHOLD = float(os.environ.get("AE_WEB_CONVERGENCE_THRESHOLD", "0.001"))


def _serialize_belief_full(belief) -> Dict[str, Any]:
    """Serialize a belief with FULL content for Sprint 5 merge support (Decision 2.4)."""
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

    return {
        "belief_id": belief.belief_id,
        "content": belief.content,  # FULL content, not truncated (Decision 2.4)
        "level": belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
        "status": belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
        "credence": credence_dict,
        "theory_id": belief.theory_id,
        "entrenchment": belief.entrenchment,
        "paper_ids": getattr(belief, 'paper_ids', []),
        "domain": getattr(belief, 'domain', None),
        "tags": getattr(belief, 'tags', []),
        "created_at": belief.created_at.isoformat() if hasattr(belief, 'created_at') and belief.created_at else None
    }


def _serialize_constraint_full(constraint) -> Dict[str, Any]:
    """Serialize a constraint for full web reconstruction (Decision 2.4)."""
    return {
        "constraint_id": constraint.constraint_id,
        "source_id": constraint.source_id,
        "target_id": constraint.target_id,
        "constraint_type": constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type),
        "strength": constraint.strength,
        "bidirectional": getattr(constraint, 'bidirectional', False),
        "evidence_ids": getattr(constraint, 'evidence_ids', []),
        "warrant_type": getattr(constraint, 'warrant_type', None),
        "provenance": getattr(constraint, 'provenance', None)
    }


def _write_error_state_files(
    out_dir: Path,
    run_id: str,
    paper_id: str,
    failure_stage: str,
    error_type: str,
    error_message: str,
    recoverable: bool = False
) -> None:
    """Write error-state files on integration failure (Decision 2.6)."""
    error_info = {
        "failure_stage": failure_stage,
        "error_type": error_type,
        "error_message": error_message,
        "recoverable": recoverable
    }

    # Write coherence_summary.json with error state
    coherence_summary = {
        "schema": "ae.coherence_summary.v1",
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "status": "failed",
        "extraction_succeeded": True,
        "web_integration_succeeded": False,
        "error": error_info,
        "coherence_before": None,
        "coherence_after": None,
        "n_beliefs": 0,
        "n_stubs": 0,
        "n_anomalies": 0
    }
    _write_json(out_dir / "coherence_summary.json", coherence_summary)

    # Write web_state.json with error state
    web_state = {
        "schema": "ae.web_state.v1",
        "run_id": run_id,
        "paper_id": paper_id,
        "created_at": _utc_now(),
        "status": "failed",
        "error": error_info,
        "beliefs": {},
        "constraints": {}
    }
    _write_json(out_dir / "web_state.json", web_state)


def _integrate_into_web_of_belief(
    claims: List[Dict[str, Any]],
    rules: List[Dict[str, Any]],
    out_dir: Path,
    run_id: str,
    paper_id: str,
    web_options: Optional[Dict[str, Any]] = None,
    export_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Integrate extracted claims and rules into a Quinean Web of Belief.

    Sprint 2 integration point: This function bridges Track A (extraction)
    with Track B (epistemic analysis).

    Expert Panel Revisions (2026-01-18):
    - Decision 2.2: Structured error capture, WARNING-level logging
    - Decision 2.4: Full belief content and constraint serialization
    - Decision 2.5: Configurable equilibrium parameters, convergence logging
    - Decision 2.6: Write error-state files on failure

    Sprint 2.0.3: Added web_options and export_options from CLI flags.

    Outputs written to out_dir:
    - web_state.json: Serialized web of belief state (full, for Sprint 5 merge)
    - stubs.jsonl: Beliefs without theory connections
    - tensions.jsonl: Beliefs in tension with the web
    - coherence_summary.json: Web coherence metrics and equilibrium log
    - manifest.json: Output manifest with checksums (if export_options.manifest)
    - cluster_stats.json: Coherence cluster statistics (if export_options.cluster_stats)
    - bn_edges.json: BN edge parameters with uncertainty (if export_options.bn_edges)

    Returns:
        Dict with integration summary for inclusion in result.json
    """
    # Sprint 2.0.3: Default options
    web_options = web_options or {}
    export_options = export_options or {
        "manifest": True,
        "bn_state": True,
        "cluster_stats": True,
        "bn_edges": True,
    }
    # Decision 2.2: Structured error capture
    def make_error_result(failure_stage: str, error_type: str, error_message: str, recoverable: bool = False):
        return {
            "web_integration": "failed",
            "failure_stage": failure_stage,
            "error_type": error_type,
            "error_message": error_message,
            "recoverable": recoverable,
            "n_beliefs": 0,
            "n_stubs": 0,
            "n_tensions": 0,
            "coherence": None
        }

    # Sprint 2.0.3: Check if web integration is disabled via CLI flag
    if not web_options.get("enabled", True):
        _web_logger.info(f"[{paper_id}] Web integration skipped: disabled via --no-web flag")
        return {
            "web_integration": "skipped",
            "reason": "disabled_via_cli",
            "n_beliefs": 0,
            "n_constraints": 0,
            "n_stubs": 0,
            "n_tensions": 0,
        }

    # Check if web of belief is available
    if not WEB_OF_BELIEF_AVAILABLE:
        _web_logger.warning(f"[{paper_id}] Web integration skipped: web_of_belief module not available")
        # Decision 2.6: Write error-state files
        _write_error_state_files(
            out_dir, run_id, paper_id,
            failure_stage="import",
            error_type="ImportError",
            error_message="web_of_belief module not available",
            recoverable=True
        )
        return make_error_result("import", "ImportError", "web_of_belief module not available", recoverable=True)

    # Stage 1: Import and initialization
    try:
        web = create_neuroarchitecture_web()
        outcome_lookup = load_outcome_lookup()
    except Exception as e:
        _web_logger.warning(f"[{paper_id}] Web integration failed at initialization: {e}")
        _write_error_state_files(out_dir, run_id, paper_id, "initialization", type(e).__name__, str(e), recoverable=True)
        return make_error_result("initialization", type(e).__name__, str(e), recoverable=True)

    # Stage 1.1: Initialize scalable coherence manager (TD-C)
    coherence_manager = None
    if SCALABLE_COHERENCE_AVAILABLE:
        try:
            coherence_manager = CoherenceManager()
            _web_logger.debug(f"[{paper_id}] Using scalable coherence (O(n log n))")
        except Exception as e:
            _web_logger.warning(f"[{paper_id}] Scalable coherence init failed, using default: {e}")

    # Stage 1.2: Initialize incremental BN builder (TD-E)
    bn_builder = None
    if INCREMENTAL_BN_AVAILABLE:
        try:
            bn_builder = IncrementalBNBuilder()
            _web_logger.debug(f"[{paper_id}] Using incremental BN learning")
        except Exception as e:
            _web_logger.warning(f"[{paper_id}] Incremental BN init failed: {e}")

    # Stage 1.5: Credibility Testing (Sprint B - TODO 1)
    credibility_report = None
    if CREDIBILITY_TESTING_AVAILABLE:
        try:
            tester = create_tester(web)

            # Extract metadata for credibility checks
            credibility_metadata = {
                'sample_size': None,
                'study_design': None,
                'sample_description': '',
                'effect_size': None,
                'p_value': None,
            }

            # Try to extract metadata from claims
            for claim in claims:
                if isinstance(claim, dict):
                    if 'sample_size' in claim and credibility_metadata['sample_size'] is None:
                        credibility_metadata['sample_size'] = claim.get('sample_size')
                    if 'study_design' in claim and credibility_metadata['study_design'] is None:
                        credibility_metadata['study_design'] = claim.get('study_design')
                    if 'effect_size' in claim and credibility_metadata['effect_size'] is None:
                        credibility_metadata['effect_size'] = claim.get('effect_size')

            # Convert claims to beliefs for credibility evaluation
            # (CredibilityTester works with Belief objects, but we don't have them yet)
            # For now, we perform basic metadata checks
            from src.services.web_of_belief import Belief, Credence, EpistemicLevel

            temp_beliefs = []
            for claim in claims:
                if isinstance(claim, dict):
                    temp_beliefs.append(Belief(
                        belief_id=claim.get('claim_id', 'temp'),
                        content=claim.get('claim', ''),
                        level=EpistemicLevel.EMPIRICAL,
                        credence=Credence(value=0.5, uncertainty=0.3),
                    ))

            credibility_report = tester.evaluate(
                article_id=paper_id,
                beliefs=temp_beliefs,
                constraints=[],
                metadata=credibility_metadata
            )

            # Log credibility assessment
            if credibility_report.is_clean:
                _web_logger.info(f"[{paper_id}] Credibility check: PASS (no flags)")
            else:
                _web_logger.warning(
                    f"[{paper_id}] Credibility check: {credibility_report.overall_decision.value.upper()} "
                    f"({len(credibility_report.flags)} flags)"
                )

            # Write credibility report
            cred_report_path = out_dir / "credibility_report.json"
            with open(cred_report_path, 'w') as f:
                json.dump(credibility_report.to_dict(), f, indent=2, default=str)

            # If BLOCK, halt integration
            if credibility_report.overall_decision == Decision.BLOCK:
                _web_logger.error(f"[{paper_id}] Credibility BLOCK - halting integration")
                return make_error_result(
                    "credibility",
                    "CredibilityBlock",
                    f"Credibility check failed: {[f.reason for f in credibility_report.flags]}",
                    recoverable=True
                )

            # If REVIEW, add to review queue for human follow-up
            if credibility_report.overall_decision == Decision.REVIEW:
                review_queue_path = out_dir.parent / "review_queue.jsonl"
                review_entry = {
                    'article_id': paper_id,
                    'timestamp': credibility_report.timestamp.isoformat() if hasattr(credibility_report.timestamp, 'isoformat') else str(credibility_report.timestamp),
                    'n_flags': len(credibility_report.flags),
                    'flags_summary': [f.reason[:80] for f in credibility_report.flags],
                    'report_path': str(cred_report_path),
                    'status': 'pending_review',
                }
                with open(review_queue_path, 'a') as f:
                    f.write(json.dumps(review_entry) + '\n')
                _web_logger.info(f"[{paper_id}] Added to review queue ({len(credibility_report.flags)} flags)")

        except Exception as e:
            _web_logger.warning(f"[{paper_id}] Credibility testing failed: {e}")
            # Non-fatal - continue with integration

    # Stage 2: Mapping claims and rules to beliefs
    try:
        # Decision 2.5: Configurable equilibrium, with convergence logging
        equilibrium_log = []

        # Custom integration with convergence tracking
        report = integrate_extraction(
            claims=claims,
            rules=rules,
            web=web,
            outcome_lookup=outcome_lookup,
            seek_equilibrium=False,  # We'll do it manually for logging
            equilibrium_iterations=0
        )

        # TD-C: Sync beliefs and constraints to scalable coherence manager
        if coherence_manager:
            try:
                for belief_id, belief in web.beliefs.items():
                    coherence_manager.on_belief_added(
                        belief_id=belief_id,
                        theory_id=belief.theory_id,
                        level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                        domain=getattr(belief, 'domain', None)
                    )
                for constraint_id, constraint in web.constraints.items():
                    coherence_manager.on_constraint_added(
                        constraint_id=constraint_id,
                        source_id=constraint.source_id,
                        target_id=constraint.target_id,
                        constraint_type=constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type),
                        strength=constraint.strength
                    )
                _web_logger.debug(f"[{paper_id}] Synced {len(web.beliefs)} beliefs to coherence manager")
            except Exception as e:
                _web_logger.warning(f"[{paper_id}] Coherence manager sync failed: {e}")
                coherence_manager = None  # Fall back to default

        # Helper to compute coherence using scalable manager if available
        def _compute_coherence() -> float:
            if coherence_manager:
                try:
                    return coherence_manager.compute_coherence()
                except Exception:
                    pass
            return web.coherence_score() if hasattr(web, 'coherence_score') else 0.0

        # Record initial coherence
        initial_coherence = _compute_coherence()
        equilibrium_log.append({"iteration": 0, "coherence": initial_coherence})

        # Decision 2.5: Manual equilibrium with convergence detection
        if WEB_SEEK_EQUILIBRIUM and hasattr(web, 'seek_equilibrium'):
            prev_coherence = initial_coherence
            converged = False
            converged_at = None

            for i in range(1, WEB_EQUILIBRIUM_MAX_ITERATIONS + 1):
                web.seek_equilibrium(max_iterations=1)
                current_coherence = _compute_coherence()
                equilibrium_log.append({"iteration": i, "coherence": current_coherence})

                delta = abs(current_coherence - prev_coherence)
                if delta < WEB_EQUILIBRIUM_CONVERGENCE_THRESHOLD:
                    converged = True
                    converged_at = i
                    break
                prev_coherence = current_coherence

            final_coherence = current_coherence
        else:
            converged = True
            converged_at = 0
            final_coherence = initial_coherence

    except Exception as e:
        _web_logger.warning(f"[{paper_id}] Web integration failed at mapping: {e}")
        _write_error_state_files(out_dir, run_id, paper_id, "mapping", type(e).__name__, str(e), recoverable=False)
        return make_error_result("mapping", type(e).__name__, str(e), recoverable=False)

    # Stage 2.5: Sprint 3 Bridge Detection and Integration
    bridge_registry = None
    anomalies = []
    n_bridges = 0

    if BRIDGE_WARRANTS_AVAILABLE:
        try:
            bridge_registry = BridgeRegistry()

            # Detect bridges from claims
            for claim in claims:
                detected_bridge = detect_bridge_from_claim(claim, target_domain="architectural_perception")
                if detected_bridge:
                    bridge_registry.add(detected_bridge)
                    # Integrate bridge into web
                    if hasattr(web, 'integrate_bridge'):
                        web.integrate_bridge(detected_bridge, create_constraints=True)

            n_bridges = len(bridge_registry.all())

            # Create anomaly records for any failed bridges
            for failed_bridge in bridge_registry.get_failed():
                anomaly = create_anomaly_from_bridge_failure(failed_bridge)
                anomalies.append(anomaly)

            _web_logger.info(f"[{paper_id}] Bridge detection: {n_bridges} bridges detected, {len(anomalies)} anomalies")

        except Exception as e:
            _web_logger.warning(f"[{paper_id}] Bridge detection failed (non-fatal): {e}")
            # Bridge detection failure is non-fatal; continue with web integration

    # Stage 2.7: Incremental BN Parameter Updates (TD-E)
    bn_updates = 0
    if bn_builder and rules:
        try:
            for rule in rules:
                # Extract rule components for BN edge
                lhs = rule.get("lhs", [])
                rhs = rule.get("rhs", [])
                polarity = rule.get("polarity", "unknown")
                strength = rule.get("strength", {})
                ae_confidence = rule.get("ae_confidence", 0.5)

                # Create edges from lhs to rhs
                for lhs_item in lhs:
                    for rhs_item in rhs:
                        source = lhs_item.get("var", "") if isinstance(lhs_item, dict) else str(lhs_item)
                        target = rhs_item.get("var", "") if isinstance(rhs_item, dict) else str(rhs_item)

                        if source and target:
                            # Determine if evidence supports or contradicts the edge
                            supports = polarity not in ("negative", "null")

                            # Use ae_confidence as evidence weight
                            weight = ae_confidence if ae_confidence else 0.5

                            # Update edge parameters
                            bn_builder.observe_evidence(
                                source=source,
                                target=target,
                                supports=supports,
                                weight=weight,
                                paper_id=paper_id
                            )
                            bn_updates += 1

            _web_logger.info(f"[{paper_id}] BN parameters: {bn_updates} edge updates")

        except Exception as e:
            _web_logger.warning(f"[{paper_id}] Incremental BN update failed (non-fatal): {e}")

    # Stage 2.8: Epistemic-Causal Bridge (Sprint ECB)
    # Build causal layer from epistemic web if enabled
    # ECB-F14 (Parnas): Lazy import to isolate module failures
    # ECB-F7 (Pearl): Prominent warning when causal layer fails
    causal_bridge = None
    causal_models_built = False
    causal_model_summary = {}
    causal_layer_warning = None  # ECB-F7: Track failure for prominent warning

    # Check if causal bridge is disabled via CLI
    causal_enabled = web_options.get("causal_enabled", True)

    # ECB-F14: Lazy import - only import when actually needed
    global CAUSAL_BRIDGE_AVAILABLE
    if CAUSAL_BRIDGE_AVAILABLE is None:
        try:
            from src.services.epistemic_causal_bridge import (
                EpistemicCausalBridge,
                ContrastClass,
                PopulationContext,
                QuineanCounterfactualResult,
            )
            CAUSAL_BRIDGE_AVAILABLE = True
        except ImportError as import_err:
            _web_logger.warning(f"Causal bridge module import failed: {import_err}")
            CAUSAL_BRIDGE_AVAILABLE = False

    if CAUSAL_BRIDGE_AVAILABLE and causal_enabled and len(web.beliefs) > 0:
        try:
            # Import again in local scope (already cached by Python)
            from src.services.epistemic_causal_bridge import EpistemicCausalBridge

            # Create bridge from the web of belief
            causal_bridge = EpistemicCausalBridge(web)

            # Build causal models from high-credence beliefs
            credence_threshold = web_options.get("causal_credence_threshold", 0.5)
            model = causal_bridge.build_causal_models(credence_threshold=credence_threshold)

            if model and model.theory_models:
                causal_models_built = True
                causal_model_summary = {
                    "n_theories": len(model.theory_models),
                    "theories": list(model.theory_models.keys()),
                    "n_variables": len(model.get_all_variables()) if hasattr(model, 'get_all_variables') else 0,
                    "credence_threshold": credence_threshold,
                }
                _web_logger.info(
                    f"[{paper_id}] Causal bridge built: {causal_model_summary['n_theories']} theories, "
                    f"{causal_model_summary['n_variables']} variables"
                )
            else:
                _web_logger.debug(f"[{paper_id}] Causal bridge: no models built (insufficient beliefs)")

        except Exception as e:
            # ECB-F7 (Pearl): Prominent warning - don't silently degrade
            causal_layer_warning = f"CAUSAL LAYER FAILED: {e}"
            _web_logger.warning(f"[{paper_id}] {causal_layer_warning}")
            causal_model_summary = {
                "enabled": False,
                "error": str(e),
                "WARNING": "CAUSAL LAYER UNAVAILABLE - Results lack causal annotations"
            }

    elif not causal_enabled:
        _web_logger.debug(f"[{paper_id}] Causal bridge skipped: disabled via --no-causal flag")
    elif not CAUSAL_BRIDGE_AVAILABLE:
        causal_layer_warning = "CAUSAL LAYER UNAVAILABLE: Module import failed"
        _web_logger.warning(f"[{paper_id}] {causal_layer_warning}")

    # Stage 3: Serialization
    try:
        # Decision 2.4: Full belief and constraint serialization
        beliefs_serialized = {
            bid: _serialize_belief_full(b)
            for bid, b in web.beliefs.items()
        }

        constraints_serialized = {
            cid: _serialize_constraint_full(c)
            for cid, c in web.constraints.items()
        }

        # Export web state with FULL content (Decision 2.4)
        web_state = {
            "schema": "ae.web_state.v1",
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "status": "success",
            "n_beliefs": len(web.beliefs),
            "n_constraints": len(web.constraints),
            "coherence_score": final_coherence,
            "beliefs": beliefs_serialized,
            "constraints": constraints_serialized,  # Decision 2.4: Include constraints
            "integration_report": report.to_dict(),
            # Decision 2.5: Equilibrium metadata for reproducibility
            "equilibrium_config": {
                "seek_equilibrium": WEB_SEEK_EQUILIBRIUM,
                "max_iterations": WEB_EQUILIBRIUM_MAX_ITERATIONS,
                "convergence_threshold": WEB_EQUILIBRIUM_CONVERGENCE_THRESHOLD
            },
            # Sprint ECB: Causal bridge metadata
            "causal_bridge": {
                "built": causal_models_built,
                "enabled": causal_enabled,
                "summary": causal_model_summary if causal_models_built else None,
                # ECB-F7 (Pearl): Prominent warning when causal layer fails
                "warning": causal_layer_warning,
            },
            # ECB-F7: Top-level warnings for visibility
            "warnings": [causal_layer_warning] if causal_layer_warning else [],
        }
        _write_json(out_dir / "web_state.json", web_state)

        # Export stubs
        n_stubs = export_stubs_jsonl(web, out_dir / "stubs.jsonl")

        # Export tensions
        n_tensions = export_tensions_jsonl(web, out_dir / "tensions.jsonl")

        # Sprint 3: Export bridges and anomalies
        if bridge_registry and BRIDGE_WARRANTS_AVAILABLE:
            export_bridges_jsonl(bridge_registry, out_dir / "bridges.jsonl")
            if anomalies:
                export_anomalies_jsonl(anomalies, out_dir / "anomalies.jsonl")

        # TD-E: Export incremental BN state (controlled by --export-bn)
        n_bn_edges = 0
        if bn_builder:
            try:
                bn_state = bn_builder.to_dict()
                n_bn_edges = len(bn_state.get("edges", {}))
                if export_options.get("bn_state", True):
                    _write_json(out_dir / "bn_incremental_state.json", bn_state)
                    _web_logger.debug(f"[{paper_id}] Exported BN state: {n_bn_edges} edges")
            except Exception as e:
                _web_logger.warning(f"[{paper_id}] BN state export failed: {e}")

        # Write coherence summary with equilibrium log (Decision 2.5)
        coherence_summary = {
            "schema": "ae.coherence_summary.v1",
            "run_id": run_id,
            "paper_id": paper_id,
            "created_at": _utc_now(),
            "status": "success",
            "extraction_succeeded": True,
            "web_integration_succeeded": True,
            "coherence_before": initial_coherence,
            "coherence_after": final_coherence,
            "coherence_delta": final_coherence - initial_coherence if initial_coherence is not None else None,
            "n_beliefs": len(web.beliefs),
            "n_stubs": n_stubs,
            "n_anomalies": report.n_anomalies + len(anomalies),  # Include bridge anomalies
            "theory_distribution": report.theory_distribution,
            "level_distribution": report.level_distribution,
            "stub_reasons": report.stub_reasons,
            # Decision 2.5: Convergence log
            "equilibrium_log": equilibrium_log,
            "converged": converged,
            "converged_at_iteration": converged_at,
            # Sprint 3: Bridge statistics
            "n_bridges": n_bridges,
            "n_bridge_anomalies": len(anomalies),
            # TD-C/TD-E: Scalability statistics
            "scalable_coherence_used": coherence_manager is not None,
            "incremental_bn_used": bn_builder is not None,
            "n_bn_updates": bn_updates,
            "n_bn_edges": n_bn_edges
        }
        _write_json(out_dir / "coherence_summary.json", coherence_summary)

        # Sprint 2.0.2/2.0.3: Enhanced output serialization with TD module exports
        # Controlled by export_options from CLI flags
        output_files = {}
        if OUTPUT_SERIALIZER_AVAILABLE:
            try:
                # Export cluster statistics (TD-C) - controlled by --export-cluster-stats
                if export_options.get("cluster_stats", True):
                    cluster_stats = serialize_cluster_stats(coherence_manager, run_id, paper_id)
                    _write_json(out_dir / "cluster_stats.json", cluster_stats)
                    output_files["cluster_stats"] = OutputFile(
                        filename="cluster_stats.json",
                        schema=SCHEMA_VERSIONS["cluster_stats"],
                        description="Coherence cluster statistics and cache performance",
                        record_count=len(cluster_stats.get("cluster_details", [])),
                    )

                # Export BN edges with uncertainty (TD-E) - controlled by --export-bn-edges
                if export_options.get("bn_edges", True):
                    bn_edges = serialize_bn_edges(bn_builder, run_id, paper_id)
                    _write_json(out_dir / "bn_edges.json", bn_edges)
                    output_files["bn_edges"] = OutputFile(
                        filename="bn_edges.json",
                        schema=SCHEMA_VERSIONS["bn_edges"],
                        description="BN edge parameters with uncertainty bounds",
                        record_count=bn_edges.get("n_edges", 0),
                    )

                # Register existing outputs in manifest
                output_files["web_state"] = OutputFile(
                    filename="web_state.json",
                    schema=SCHEMA_VERSIONS.get("web_state", "ae.web_state.v1"),
                    description="Full web of belief state",
                    record_count=len(web.beliefs),
                )
                output_files["coherence_summary"] = OutputFile(
                    filename="coherence_summary.json",
                    schema=SCHEMA_VERSIONS.get("coherence_summary", "ae.coherence_summary.v1"),
                    description="Coherence computation summary with equilibrium log",
                    record_count=1,
                )
                output_files["stubs"] = OutputFile(
                    filename="stubs.jsonl",
                    schema=SCHEMA_VERSIONS.get("stub", "ae.stub.v1"),
                    description="Findings that couldn't be mapped to beliefs",
                    record_count=n_stubs,
                )
                output_files["tensions"] = OutputFile(
                    filename="tensions.jsonl",
                    schema=SCHEMA_VERSIONS.get("tension", "ae.tension.v1"),
                    description="Detected coherence tensions",
                    record_count=n_tensions,
                )
                if bridge_registry and BRIDGE_WARRANTS_AVAILABLE:
                    output_files["bridges"] = OutputFile(
                        filename="bridges.jsonl",
                        schema=SCHEMA_VERSIONS.get("bridge", "ae.bridge.v1"),
                        description="Bridge warrants between domains",
                        record_count=n_bridges,
                    )
                    if anomalies:
                        output_files["anomalies"] = OutputFile(
                            filename="anomalies.jsonl",
                            schema=SCHEMA_VERSIONS.get("anomaly", "ae.anomaly.v1"),
                            description="Anomalies from failed bridge integration",
                            record_count=len(anomalies),
                        )
                # BN incremental state - controlled by --export-bn
                if bn_builder and export_options.get("bn_state", True):
                    output_files["bn_incremental_state"] = OutputFile(
                        filename="bn_incremental_state.json",
                        schema="ae.bn_incremental_state.v1",
                        description="Incremental BN parameter state",
                        record_count=n_bn_edges,
                    )

                # Generate manifest - controlled by --export-manifest
                if export_options.get("manifest", True):
                    manifest = generate_manifest(out_dir, run_id, paper_id, output_files)
                    _write_json(out_dir / "manifest.json", manifest)
                    _web_logger.debug(f"[{paper_id}] Manifest written: {len(output_files)} files")

            except Exception as e:
                _web_logger.warning(f"[{paper_id}] Enhanced output serialization failed (non-fatal): {e}")

        return {
            "web_integration": "success",
            "n_beliefs": len(web.beliefs),
            "n_constraints": len(web.constraints),
            "n_stubs": n_stubs,
            "n_tensions": n_tensions,
            "coherence_before": initial_coherence,
            "coherence_after": final_coherence,
            "theory_distribution": report.theory_distribution,
            "converged": converged,
            "converged_at_iteration": converged_at,
            # Sprint 3: Bridge statistics
            "n_bridges": n_bridges,
            "n_bridge_anomalies": len(anomalies),
            # TD-C/TD-E: Scalability statistics
            "scalable_coherence_used": coherence_manager is not None,
            "incremental_bn_used": bn_builder is not None,
            "n_bn_updates": bn_updates,
            "n_bn_edges": n_bn_edges,
            # Sprint 2.0.2: Output manifest
            "manifest_generated": OUTPUT_SERIALIZER_AVAILABLE and len(output_files) > 0,
            "n_output_files": len(output_files) if OUTPUT_SERIALIZER_AVAILABLE else 0,
        }

    except Exception as e:
        _web_logger.warning(f"[{paper_id}] Web integration failed at serialization: {e}")
        _write_error_state_files(out_dir, run_id, paper_id, "serialization", type(e).__name__, str(e), recoverable=False)
        return make_error_result("serialization", type(e).__name__, str(e), recoverable=False)


def _compute_af_decision(
    claims: List[Dict[str, Any]],
    rules: List[Dict[str, Any]],
    blocking_issues: List[str],
) -> Dict[str, Any]:
    min_rules = int(os.environ.get("AE_ACCEPT_MIN_RULES", "1"))
    min_conf = float(os.environ.get("AE_ACCEPT_MIN_CONF", "0.2"))
    claim_conf = max([c.get("ae_confidence", 0.0) for c in claims], default=0.0)
    rule_conf = max([r.get("ae_confidence", 0.0) for r in rules], default=0.0)
    best_conf = max(claim_conf, rule_conf)
    if not claims and not rules:
        return {"decision": "reject", "reason": "no_extracts", "confidence": best_conf}
    if blocking_issues:
        return {"decision": "accept_with_caveats", "reason": "blocking_issues", "confidence": best_conf}
    if len(rules) < min_rules:
        return {"decision": "accept_with_caveats", "reason": "insufficient_rules", "confidence": best_conf}
    if best_conf < min_conf:
        return {"decision": "accept_with_caveats", "reason": "low_confidence", "confidence": best_conf}
    return {"decision": "accept", "reason": "meets_thresholds", "confidence": best_conf}

def run_l0_harvest(job_id: int, query: str, limit: int=20):
    hits = s2_search(query, limit=limit)
    with _conn() as con:
        for h in hits:
            con.execute("INSERT OR IGNORE INTO articles (s2_id,title,abstract,year,url,citation_count) VALUES (?,?,?,?,?,?)",
                        (h.get('paperId'), h.get('title'), h.get('abstract'), h.get('year'), h.get('url'), h.get('citationCount',0)))
        con.execute("UPDATE processing_queue SET status='done', result='l0_harvested' WHERE id=?", (job_id,))
    return len(hits)

def run_l1_clustering(job_id: int, topic: str, sample: int=200):
    with _conn() as con:
        rows = con.execute("SELECT id, abstract FROM articles WHERE abstract IS NOT NULL LIMIT ?", (sample,)).fetchall()
    vecs = [(rid, embed_text(ab or "")) for rid, ab in rows]
    # naive single-pass threshold clustering
    clusters = []
    TH = 0.8
    for rid, v in vecs:
        placed=False
        for c in clusters:
            if cosine(v, c['centroid']) > TH:
                c['ids'].append(rid)
                placed=True; break
        if not placed:
            clusters.append({'ids':[rid], 'centroid': v})
    with _conn() as con:
        for i, c in enumerate(clusters):
            for rid in c['ids']:
                con.execute("UPDATE articles SET cluster=? WHERE id=?", (i, rid))
        con.execute("UPDATE processing_queue SET status='done', result='l1_clustered' WHERE id=?", (job_id,))
    return len(clusters)

def run_l2_extraction(job_id: int, article_id: int, topic: str):
    with _conn() as con:
        row = con.execute("SELECT id, title, abstract, pdf_text FROM articles WHERE id=?", (article_id,)).fetchone()
    if not row: return 0
    text = row[3] or row[2] or ""
    findings = extract_findings_from_text(text, topic=topic, is_admin=False)
    with _conn() as con:
        for f in findings:
            st = f.get("statistics",{}) if isinstance(f, dict) else {}
            con.execute("""INSERT INTO findings(article_id, finding_text, p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper, quote, page_span)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""", (article_id, 
                            f.get("finding_text") if isinstance(f, dict) else str(f),
                            st.get("p_value"), st.get("effect_size"), st.get("effect_size_type"), st.get("sample_size"),
                            st.get("ci_lower"), st.get("ci_upper"),
                            f.get("quote"), f.get("page_span")))
        con.execute("UPDATE processing_queue SET status='done', result='l2_extracted' WHERE id=?", (job_id,))
    return len(findings)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(p: Path, rows: List[Dict[str, Any]]) -> None:
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _audit_event(run_id: str, paper_id: str, stage: str, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.audit_event.v1",
        "ts": _utc_now(),
        "run_id": run_id,
        "paper_id": paper_id,
        "stage": stage,
        "event": event,
        "data": data,
    }


def _review_item(run_id: str, paper_id: str, item_id: str, severity: str, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.review_item.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "item_id": item_id,
        "severity": severity,
        "question": question,
        "context": context,
    }


def _run_from_contract_bundle_impl(
    *,
    in_dir: Path,
    out_dir: Path,
    profile: str,
    hitl: str,
    web_options: Optional[Dict[str, Any]] = None,
    export_options: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Read AF-style bundle in in_dir, run AE extraction, write AE outputs to out_dir,
    and return a summary dict (counts, warnings, etc).

    Sprint 2.0.3: Now accepts web_options and export_options from CLI flags.
    Sprint 2.0.5: Enhanced error handling and structured logging.

    web_options:
        enabled: bool - Enable/disable web of belief integration
        seek_equilibrium: bool - Whether to seek equilibrium
        max_iterations: int - Max iterations for equilibrium
        convergence_threshold: float - Convergence threshold

    export_options:
        manifest: bool - Generate manifest.json
        bn_state: bool - Export bn_incremental_state.json
        cluster_stats: bool - Export cluster_stats.json
        bn_edges: bool - Export bn_edges.json
    """
    in_dir = Path(in_dir).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sprint 2.0.3: Apply CLI options to environment variables
    web_options = web_options or {}
    export_options = export_options or {}

    # Sprint 2.0.5: Initialize run metadata early for error collection
    run_id = f"ae.run.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    paper_id = "unknown"  # Will be updated after reading paper.json

    # Sprint 2.0.5: Initialize error collector
    error_collector = ErrorCollector(run_id, paper_id)
    _pipeline_logger.info(f"Starting pipeline run: {run_id}", extra={"run_id": run_id})

    # Override environment variables with CLI options
    if "seek_equilibrium" in web_options:
        os.environ["AE_WEB_SEEK_EQUILIBRIUM"] = str(web_options["seek_equilibrium"]).lower()
    if "max_iterations" in web_options:
        os.environ["AE_WEB_EQUILIBRIUM_MAX_ITERATIONS"] = str(web_options["max_iterations"])
    if "convergence_threshold" in web_options:
        os.environ["AE_WEB_CONVERGENCE_THRESHOLD"] = str(web_options["convergence_threshold"])

    audits: List[Dict[str, Any]] = []
    review_items: List[Dict[str, Any]] = []

    # Sprint 2.0.5: Wrap input validation in try/except
    pdf_path = in_dir / "paper.pdf"
    paper_path = in_dir / "paper.json"

    try:
        if not paper_path.exists():
            error_msg = f"Missing required file: {paper_path}"
            _pipeline_logger.error(error_msg)
            if PIPELINE_LOGGING_AVAILABLE:
                error_collector.record(
                    ValidationError(error_msg, paper_id=paper_id, recoverable=False),
                    ErrorSeverity.FATAL,
                    "validation",
                )
            return {
                "run_id": run_id,
                "paper_id": paper_id,
                "status": "FAIL",
                "n_claims": 0,
                "n_rules": 0,
                "blocking_issues": ["missing_paper_json"],
                "error": error_msg,
            }
        paper = json.loads(paper_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in paper.json: {e}"
        _pipeline_logger.error(error_msg)
        if PIPELINE_LOGGING_AVAILABLE:
            error_collector.record(e, ErrorSeverity.FATAL, "validation", {"file": str(paper_path)})
        return {
            "run_id": run_id,
            "paper_id": paper_id,
            "status": "FAIL",
            "n_claims": 0,
            "n_rules": 0,
            "blocking_issues": ["invalid_paper_json"],
            "error": error_msg,
        }
    except Exception as e:
        error_msg = f"Failed to read paper.json: {e}"
        _pipeline_logger.error(error_msg, exc_info=True)
        if PIPELINE_LOGGING_AVAILABLE:
            error_collector.record(e, ErrorSeverity.FATAL, "validation", {"file": str(paper_path)})
        return {
            "run_id": run_id,
            "paper_id": paper_id,
            "status": "FAIL",
            "n_claims": 0,
            "n_rules": 0,
            "blocking_issues": ["read_error"],
            "error": error_msg,
        }

    paper_id = paper.get("paper_id", "unknown")
    error_collector.paper_id = paper_id  # Update collector with actual paper_id
    _pipeline_logger.info(f"Processing paper: {paper_id}", extra={"paper_id": paper_id, "run_id": run_id})

    # Record publication metadata for scholarly timeline replay (best effort)
    try:
        from src.services.web_persistence import WebPersistenceService
        pub_year = paper.get("year")
        pub_date = paper.get("publication_date") or paper.get("published_at")
        first_seen = paper.get("source", {}).get("retrieved_at")
        db_path = _resolve_db_path()
        WebPersistenceService(str(db_path)).upsert_paper_publication(
            paper_id=paper_id,
            publication_year=pub_year,
            publication_date=pub_date,
            first_seen_at=first_seen,
            source="paper_json"
        )
    except Exception as metadata_err:
        _pipeline_logger.debug(
            f"[{paper_id}] Publication metadata not recorded: {metadata_err}",
            extra={"paper_id": paper_id, "run_id": run_id}
        )

    # Paper Lifecycle Tracking: Start extraction stage
    lifecycle_service = None
    if LIFECYCLE_TRACKING_AVAILABLE:
        try:
            lifecycle_service = get_lifecycle_service()
            lifecycle_service.transition(
                paper_id=paper_id,
                stage=LifecycleStage.EXTRACTING,
                status=StageStatus.IN_PROGRESS,
                run_id=run_id,
                triggered_by="pipeline",
                details={"profile": profile, "hitl": hitl},
            )
            _pipeline_logger.debug(f"Lifecycle: {paper_id} -> EXTRACTING", extra={"paper_id": paper_id})
        except Exception as lifecycle_err:
            _pipeline_logger.warning(f"Lifecycle tracking init failed: {lifecycle_err}", extra={"paper_id": paper_id})

    try:
        pdf_sha256 = _sha256_file(pdf_path) if pdf_path.exists() else "0" * 64
        paper_json_sha256 = _sha256_file(paper_path)
    except Exception as e:
        _pipeline_logger.warning(f"Failed to compute file hash: {e}", extra={"paper_id": paper_id})
        pdf_sha256 = "0" * 64
        paper_json_sha256 = "0" * 64

    audits.append(_audit_event(run_id, paper_id, "ingest", "start", {"profile": profile, "hitl": hitl}))

    # Sprint 2.0.5: Text extraction with comprehensive error handling
    text = ""
    fulltext_path = in_dir / "fulltext.txt"
    abstract_path = in_dir / "abstract.txt"

    try:
        if fulltext_path.exists():
            _pipeline_logger.debug(f"Reading fulltext from {fulltext_path}", extra={"paper_id": paper_id})
            text = fulltext_path.read_text(encoding="utf-8", errors="ignore")
        elif abstract_path.exists():
            _pipeline_logger.debug(f"Reading abstract from {abstract_path}", extra={"paper_id": paper_id})
            text = abstract_path.read_text(encoding="utf-8", errors="ignore")
        elif pdf_path.exists():
            _pipeline_logger.debug(f"Extracting text from PDF: {pdf_path}", extra={"paper_id": paper_id})
            try:
                text = extract_pdf_text(pdf_path) or ""
            except Exception as pdf_err:
                _pipeline_logger.warning(
                    f"PDF extraction failed: {pdf_err}",
                    extra={"paper_id": paper_id},
                    exc_info=True
                )
                if PIPELINE_LOGGING_AVAILABLE:
                    error_collector.record(
                        ExtractionError(f"PDF extraction failed: {pdf_err}", paper_id=paper_id, recoverable=True),
                        ErrorSeverity.DEGRADED,
                        "extraction",
                        {"pdf_path": str(pdf_path)},
                    )
                text = ""
    except Exception as e:
        _pipeline_logger.error(f"Text extraction failed: {e}", extra={"paper_id": paper_id}, exc_info=True)
        if PIPELINE_LOGGING_AVAILABLE:
            error_collector.record(e, ErrorSeverity.BLOCKING, "extraction")
        text = ""

    # BIB-6: Fallback to paper.json abstract when fulltext extraction fails or yields minimal text
    MIN_TEXT_LENGTH = 100  # Minimum useful text length for extraction
    text_source = "fulltext" if fulltext_path.exists() else ("abstract_file" if abstract_path.exists() else "pdf")

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        paper_abstract = paper.get("abstract", "")
        if paper_abstract and len(paper_abstract.strip()) >= MIN_TEXT_LENGTH:
            _pipeline_logger.info(
                f"Using abstract from paper.json as fallback ({len(paper_abstract)} chars)",
                extra={"paper_id": paper_id, "text_length": len(paper_abstract)}
            )
            text = paper_abstract
            text_source = "paper_json_abstract"
            audits.append(_audit_event(
                run_id, paper_id, "extract", "fallback",
                {"source": "paper_json_abstract", "length": len(paper_abstract)}
            ))
        elif paper_abstract:
            _pipeline_logger.debug(
                f"paper.json abstract too short ({len(paper_abstract)} chars < {MIN_TEXT_LENGTH})",
                extra={"paper_id": paper_id}
            )

    if text:
        _pipeline_logger.info(
            f"Extracted {len(text)} characters of text",
            extra={"paper_id": paper_id, "text_length": len(text)}
        )
        # Lifecycle tracking: record text extraction details
        if lifecycle_service:
            try:
                lifecycle_service.update_paper_metrics(
                    paper_id=paper_id,
                    text_source=text_source,
                    text_length=len(text),
                )
            except Exception as lifecycle_err:
                _pipeline_logger.debug(f"Lifecycle metrics update failed: {lifecycle_err}")
    else:
        _pipeline_logger.warning(f"No text extracted from input bundle", extra={"paper_id": paper_id})
        audits.append(_audit_event(run_id, paper_id, "extract", "fail", {"reason": "no_text_extracted"}))
        review_items.append(
            _review_item(
                run_id,
                paper_id,
                "rev_missing_text",
                "blocking",
                "No text could be extracted from the input bundle.",
                {"pdf": str(pdf_path)},
            )
        )

    # Sprint 2.0.5: LLM extraction with enhanced error handling and logging
    topic = paper.get("title") or paper.get("doi") or "unknown"
    findings = []
    llm_blocked = False
    llm_error_details = None

    if text:
        # Check for LLM configuration
        has_llm_key = bool(
            os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("OLLAMA_MODEL")
            or os.environ.get("OLLAMA_BASE")
            or os.environ.get("AE_LLM_MODEL")
        )
        if not has_llm_key:
            llm_blocked = True
            _pipeline_logger.warning(
                "LLM extraction skipped: no API key configured",
                extra={"paper_id": paper_id}
            )
            if PIPELINE_LOGGING_AVAILABLE:
                error_collector.record(
                    ConfigurationError(
                        "LLM API key missing; configure GOOGLE_API_KEY or OPENAI_API_KEY",
                        paper_id=paper_id,
                        recoverable=True
                    ),
                    ErrorSeverity.BLOCKING,
                    "configuration",
                )
            audits.append(_audit_event(run_id, paper_id, "extract", "skip", {"reason": "llm_not_configured"}))
            review_items.append(
                _review_item(
                    run_id,
                    paper_id,
                    "rev_llm_key",
                    "blocking",
                    "LLM API key missing; configure GOOGLE_API_KEY or OPENAI_API_KEY.",
                    {},
                )
            )
        else:
            _pipeline_logger.info(
                f"Starting LLM extraction for topic: {topic[:50]}...",
                extra={"paper_id": paper_id, "topic": topic}
            )
            extraction_start = time.time()

            try:
                findings = extract_findings_from_text(text, topic=topic, is_admin=False)
                extraction_time = time.time() - extraction_start
                _pipeline_logger.info(
                    f"LLM extraction complete: {len(findings)} findings in {extraction_time:.2f}s",
                    extra={
                        "paper_id": paper_id,
                        "n_findings": len(findings),
                        "extraction_time_s": extraction_time
                    }
                )
            except Exception as exc:
                extraction_time = time.time() - extraction_start
                llm_blocked = True
                llm_error_details = {
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "extraction_time_s": extraction_time,
                }
                _pipeline_logger.error(
                    f"LLM extraction failed after {extraction_time:.2f}s: {exc}",
                    extra={"paper_id": paper_id, **llm_error_details},
                    exc_info=True
                )
                if PIPELINE_LOGGING_AVAILABLE:
                    error_collector.record(
                        LLMError(f"LLM extraction failed: {exc}", paper_id=paper_id, recoverable=True),
                        ErrorSeverity.BLOCKING,
                        "llm_extraction",
                        llm_error_details,
                    )
                audits.append(_audit_event(run_id, paper_id, "extract", "fail", {"reason": str(exc)}))
                review_items.append(
                    _review_item(
                        run_id,
                        paper_id,
                        "rev_llm_error",
                        "blocking",
                        "LLM extraction failed; check provider configuration.",
                        {"error": str(exc)},
                    )
                )

    claims: List[Dict[str, Any]] = []
    rules: List[Dict[str, Any]] = []
    for idx, finding in enumerate(findings, start=1):
        if isinstance(finding, dict):
            stats = finding.get("statistics", {}) or {}
            antecedents = finding.get("antecedents") or finding.get("antecedent") or []
            if isinstance(antecedents, str):
                antecedents = [antecedents]
            if not antecedents:
                constructs = finding.get("constructs") or {}
                env_factors = constructs.get("environment_factors") or []
                if isinstance(env_factors, str):
                    env_factors = [env_factors]
                antecedents = env_factors
            consequent = (
                finding.get("consequent")
                or finding.get("finding_text")
                or finding.get("statement")
                or "Unspecified finding"
            )
            statement = finding.get("finding_text") or finding.get("statement") or consequent
            confidence = float(finding.get("ae_confidence") or finding.get("confidence") or 0.0)
        else:
            stats = {}
            antecedents = []
            consequent = str(finding) or "Unspecified finding"
            statement = str(finding) or "Unspecified finding"
            confidence = 0.0

        claim_id = f"{paper_id}.claim.{idx}"
        claim = {
            "schema": "ae.claim.v1",
            "claim_id": claim_id,
            "paper_id": paper_id,
            "claim_type": "descriptive",
            "statement": statement,
            "constructs": {
                "environment_factors": [],
                "outcomes": [],
                "mediators": [],
                "moderators": [],
            },
            "study": {
                "design": "unknown",
                "sample": {
                    "n": stats.get("sample_size"),
                    "population": None,
                    "age_mean": None,
                    "country": None,
                },
                "task": [],
                "setting": [],
            },
            "statistics": {
                "effect_size": {
                    "type": stats.get("effect_size_type"),
                    "value": stats.get("effect_size"),
                },
                "p_value": stats.get("p_value"),
                "ci95": None,
            },
            "evidence": [],
            "constraints": [],
            "ae_confidence": confidence,
        }
        claims.append(claim)

        n_val = stats.get("sample_size")
        d_val = stats.get("effect_size")
        p_val = stats.get("p_value")
        rule_statement = (
            f"{statement} (n={n_val if n_val is not None else 'unknown'}, "
            f"d={d_val if d_val is not None else 'unknown'}, "
            f"p={p_val if p_val is not None else 'unknown'})"
        )

        rule_id = f"{paper_id}.rule.{idx}"
        measure_dir = finding.get("measure_direction") if isinstance(finding, dict) else None
        if measure_dir == "positive":
            polarity = "positive"
        elif measure_dir == "negative":
            polarity = "negative"
        elif stats.get("effect_size") is not None:
            polarity = "positive" if float(stats.get("effect_size")) >= 0 else "negative"
        else:
            polarity = "unknown"
        strength = {"kind": "unknown", "type": None, "value": None}
        if stats.get("effect_size") is not None:
            strength = {
                "kind": "effect_size",
                "type": stats.get("effect_size_type"),
                "value": stats.get("effect_size"),
            }
        elif stats.get("p_value") is not None:
            strength = {"kind": "p_value", "type": None, "value": stats.get("p_value")}

        rule = {
            "schema": "ae.rule.v1",
            "rule_id": rule_id,
            "paper_id": paper_id,
            "rule_type": "edge",
            "statement": rule_statement,
            "lhs": antecedents if isinstance(antecedents, list) else [],
            "rhs": [consequent] if consequent else [],
            "polarity": polarity,
            "strength": strength,
            "applicability": {"population": [], "setting": [], "boundary_conditions": []},
            "evidence_links": [{"claim_id": claim_id}],
            "bn_mapping": {"node_suggestions": [], "discretization_hint": "unknown"},
            "ae_confidence": confidence,
        }
        rules.append(rule)

    db_rules = _load_rules_from_db(_resolve_db_path(), paper_id)
    if db_rules:
        rules = db_rules
        audits.append(_audit_event(run_id, paper_id, "rules", "source", {"source": "db", "n_rules": len(rules)}))

    # Lifecycle tracking: record extraction counts
    if lifecycle_service:
        try:
            lifecycle_service.update_paper_metrics(
                paper_id=paper_id,
                n_claims=len(claims),
                n_rules=len(rules),
                n_findings=len(findings),
            )
        except Exception as lifecycle_err:
            _pipeline_logger.debug(f"Lifecycle metrics update failed: {lifecycle_err}")

    bn_export = None
    if rules:
        bn_export = _bn_export_from_rules(rules, paper_id)
        _write_json(out_dir / "bn_export.json", bn_export)
        audits.append(
            _audit_event(
                run_id,
                paper_id,
                "bn_export",
                "done",
                {"path": "bn_export.json", "n_rules": len(rules)},
            )
        )

    # TBL-4: Table extraction and claim generation
    table_extraction_result = None
    extracted_tables = []
    table_claims = []

    if TABLE_EXTRACTION_AVAILABLE and pdf_path.exists():
        _pipeline_logger.info(f"Starting table extraction from PDF", extra={"paper_id": paper_id})
        table_start = time.time()

        try:
            # Get API client if available for AI extraction
            api_client = None
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    api_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                pass

            # Determine extraction method
            extraction_method = ExtractionMethod.AI_API if api_client else ExtractionMethod.PDFPLUMBER

            # Extract tables and generate claims
            integrator = PipelineTableIntegrator(
                api_client=api_client,
                extraction_method=extraction_method
            )
            table_extraction_result = integrator.extract_and_convert(pdf_path, paper_id)
            extracted_tables = table_extraction_result.tables
            table_claims = table_extraction_result.claims

            table_time = time.time() - table_start
            _pipeline_logger.info(
                f"Table extraction complete: {len(extracted_tables)} tables, {len(table_claims)} claims in {table_time:.2f}s",
                extra={
                    "paper_id": paper_id,
                    "n_tables": len(extracted_tables),
                    "n_table_claims": len(table_claims),
                    "extraction_time_s": table_time,
                }
            )

            # Merge table claims with text claims
            if table_claims:
                original_claim_count = len(claims)
                claims = integrator.merge_with_text_claims(
                    table_claims,
                    claims
                )
                _pipeline_logger.info(
                    f"Merged {len(claims) - original_claim_count} table claims (deduped from {len(table_claims)})",
                    extra={"paper_id": paper_id}
                )

            # Export tables to JSONL
            if extracted_tables:
                tables_path = out_dir / "tables.jsonl"
                export_tables_jsonl(extracted_tables, tables_path)
                audits.append(
                    _audit_event(
                        run_id,
                        paper_id,
                        "table_extraction",
                        "done",
                        {
                            "path": "tables.jsonl",
                            "n_tables": len(extracted_tables),
                            "n_table_claims": len(table_claims),
                        },
                    )
                )

        except Exception as table_err:
            _pipeline_logger.warning(
                f"Table extraction failed: {table_err}",
                extra={"paper_id": paper_id},
                exc_info=True
            )
            if PIPELINE_LOGGING_AVAILABLE:
                error_collector.record(
                    ExtractionError(f"Table extraction failed: {table_err}", paper_id=paper_id, recoverable=True),
                    ErrorSeverity.WARNING,
                    "table_extraction",
                )
            audits.append(_audit_event(run_id, paper_id, "table_extraction", "fail", {"reason": str(table_err)}))

    # Lifecycle tracking: record table extraction counts
    if lifecycle_service and (extracted_tables or table_claims):
        try:
            lifecycle_service.update_paper_metrics(
                paper_id=paper_id,
                n_tables_extracted=len(extracted_tables),
                n_table_claims=len(table_claims),
            )
        except Exception as lifecycle_err:
            _pipeline_logger.debug(f"Lifecycle table metrics update failed: {lifecycle_err}")
    elif not TABLE_EXTRACTION_AVAILABLE:
        _pipeline_logger.debug("Table extraction skipped: module not available", extra={"paper_id": paper_id})
    elif not pdf_path.exists():
        _pipeline_logger.debug("Table extraction skipped: no PDF file", extra={"paper_id": paper_id})

    # Lifecycle tracking: Mark extraction complete, start synthesis
    if lifecycle_service:
        try:
            # Complete extraction stage
            lifecycle_service.complete_stage(
                paper_id=paper_id,
                stage=LifecycleStage.EXTRACTING,
                status=StageStatus.SUCCESS,
                n_claims=len(claims),
                n_rules=len(rules),
                text_source=text_source,
                text_length=len(text) if text else 0,
            )
            # Transition to EXTRACTED
            lifecycle_service.transition(
                paper_id=paper_id,
                stage=LifecycleStage.EXTRACTED,
                status=StageStatus.SUCCESS,
                run_id=run_id,
                triggered_by="pipeline",
            )
            # Start synthesis stage
            lifecycle_service.transition(
                paper_id=paper_id,
                stage=LifecycleStage.SYNTHESIZING,
                status=StageStatus.IN_PROGRESS,
                run_id=run_id,
                triggered_by="pipeline",
            )
            _pipeline_logger.debug(f"Lifecycle: {paper_id} -> SYNTHESIZING", extra={"paper_id": paper_id})
        except Exception as lifecycle_err:
            _pipeline_logger.warning(f"Lifecycle extraction->synthesis transition failed: {lifecycle_err}")

    # Sprint 2: Web of Belief integration
    # Sprint 2.0.3: Pass through web_options and export_options from CLI
    web_integration_result = _integrate_into_web_of_belief(
        claims=claims,
        rules=rules,
        out_dir=out_dir,
        run_id=run_id,
        paper_id=paper_id,
        web_options=web_options,
        export_options=export_options,
    )
    audits.append(
        _audit_event(
            run_id,
            paper_id,
            "web_integration",
            web_integration_result.get("web_integration", "unknown"),
            web_integration_result,
        )
    )

    # Lifecycle tracking: Complete synthesis stage
    if lifecycle_service:
        try:
            web_status = web_integration_result.get("web_integration", "unknown")
            if web_status == "success":
                lifecycle_service.complete_stage(
                    paper_id=paper_id,
                    stage=LifecycleStage.SYNTHESIZING,
                    status=StageStatus.SUCCESS,
                    coherence_score=web_integration_result.get("coherence_after"),
                )
                lifecycle_service.transition(
                    paper_id=paper_id,
                    stage=LifecycleStage.SYNTHESIZED,
                    status=StageStatus.SUCCESS,
                    run_id=run_id,
                    triggered_by="pipeline",
                    coherence_score=web_integration_result.get("coherence_after"),
                )
                # Update paper metrics with web integration results
                lifecycle_service.update_paper_metrics(
                    paper_id=paper_id,
                    coherence_score=web_integration_result.get("coherence_after"),
                    n_beliefs_added=web_integration_result.get("n_beliefs", 0),
                    n_stubs_created=web_integration_result.get("n_stubs", 0),
                    n_tensions_detected=web_integration_result.get("n_tensions", 0),
                )
                _pipeline_logger.debug(f"Lifecycle: {paper_id} -> SYNTHESIZED", extra={"paper_id": paper_id})
            elif web_status == "skipped":
                lifecycle_service.complete_stage(
                    paper_id=paper_id,
                    stage=LifecycleStage.SYNTHESIZING,
                    status=StageStatus.SKIPPED,
                )
            else:
                lifecycle_service.complete_stage(
                    paper_id=paper_id,
                    stage=LifecycleStage.SYNTHESIZING,
                    status=StageStatus.FAILED,
                    error_message=web_integration_result.get("error_message", "Web integration failed"),
                )
        except Exception as lifecycle_err:
            _pipeline_logger.warning(f"Lifecycle synthesis completion failed: {lifecycle_err}")

    status = "SUCCESS" if claims else ("FAIL" if not text else "PARTIAL_SUCCESS")
    blocking = []
    errors = []
    if not text:
        blocking.append("no_text_extracted")
        errors.append({"code": "no_text", "message": "No text could be extracted from bundle inputs."})
    elif llm_blocked:
        blocking.append("llm_not_configured")
        errors.append({"code": "llm_not_configured", "message": "Missing or misconfigured LLM API key."})
    elif not claims:
        blocking.append("no_findings")

    decision = _compute_af_decision(claims, rules, blocking)
    warnings = []
    if decision["decision"] != "accept":
        warnings.append(f"af_decision:{decision['decision']}:{decision['reason']}")
        review_items.append(
            _review_item(
                run_id,
                paper_id,
                "rev_accept_criteria",
                "info",
                "Review AE accept criteria; partially useful papers should not be rejected.",
                {"decision": decision, "blocking_issues": blocking},
            )
        )

    result = {
        "schema": "ae.result.v1",
        "paper_id": paper_id,
        "pdf_sha256": pdf_sha256,
        "run_id": run_id,
        "status": status,
        "profile": profile,
        "hitl": hitl,
        "summary": {
            "n_claims": len(claims),
            "n_rules": len(rules),
            "n_effect_sizes": len([c for c in claims if c["statistics"]["effect_size"]["value"] is not None]),
            "n_population_records": len([c for c in claims if c["study"]["sample"]["n"] is not None]),
            "n_environment_factors": sum(len(c["constructs"]["environment_factors"]) for c in claims),
            # TBL-4: Table extraction summary
            "n_tables": len(extracted_tables),
            "n_table_claims": len(table_claims),
        },
        "artifacts": {
            "claims_jsonl": "claims.jsonl",
            "rules_jsonl": "rules.jsonl",
            "provenance_json": "provenance.json",
            "audit_log_jsonl": "audit.log.jsonl",
            # Sprint 2: Web of Belief outputs
            "web_state_json": "web_state.json" if web_integration_result.get("web_integration") == "success" else None,
            "stubs_jsonl": "stubs.jsonl" if web_integration_result.get("web_integration") == "success" else None,
            "tensions_jsonl": "tensions.jsonl" if web_integration_result.get("web_integration") == "success" else None,
            "coherence_summary_json": "coherence_summary.json" if web_integration_result.get("web_integration") == "success" else None,
            # Sprint 3: Bridge warrant outputs
            "bridges_jsonl": "bridges.jsonl" if web_integration_result.get("n_bridges", 0) > 0 else None,
            "anomalies_jsonl": "anomalies.jsonl" if web_integration_result.get("n_bridge_anomalies", 0) > 0 else None,
            # TBL-4: Table extraction outputs
            "tables_jsonl": "tables.jsonl" if extracted_tables else None,
        },
        "quality": {
            "confidence": decision["confidence"],
            "blocking_issues": blocking,
            "warnings": warnings,
            "af_decision": decision,
        },
        # Sprint 2: Web of Belief integration summary
        "web_integration": web_integration_result,
        "errors": errors,
    }
    audits.append(_audit_event(run_id, paper_id, "decision", "af", decision))
    if decision["decision"] != "accept" and status == "SUCCESS":
        status = "PARTIAL_SUCCESS"
        result["status"] = status

    provenance = {
        "schema": "ae.provenance.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "inputs": {"pdf_sha256": pdf_sha256, "paper_json_sha256": paper_json_sha256},
        "environment": {"python": sys.version.split()[0], "platform": sys.platform},
        "models": [],
        "tools": [{"name": "ae.pipeline", "version": "v1"}],
    }

    audits.append(_audit_event(run_id, paper_id, "extract", "done", {"n_claims": len(claims), "n_rules": len(rules)}))
    audits.append(_audit_event(run_id, paper_id, "finalize", "done", {"status": status}))

    # Sprint 2.0.5: Serialize outputs with error handling
    try:
        _write_json(out_dir / "result.json", result)
        _write_jsonl(out_dir / "claims.jsonl", claims)
        _write_jsonl(out_dir / "rules.jsonl", rules)
        _write_json(out_dir / "provenance.json", provenance)
        _write_jsonl(out_dir / "audit.log.jsonl", audits)
        _write_jsonl(out_dir / "review_items.jsonl", review_items)

        # Sprint 2.0.5: Write error log if any errors were collected
        if PIPELINE_LOGGING_AVAILABLE and error_collector.errors:
            n_errors = error_collector.to_jsonl(out_dir / "errors.jsonl")
            error_summary = error_collector.get_summary()
            _pipeline_logger.info(
                f"Pipeline completed with {n_errors} errors",
                extra={"paper_id": paper_id, "error_summary": error_summary}
            )
            # Add error summary to result
            result["error_summary"] = error_summary
            # Re-write result.json with error summary
            _write_json(out_dir / "result.json", result)
        else:
            _pipeline_logger.info(
                f"Pipeline completed successfully: {len(claims)} claims, {len(rules)} rules",
                extra={"paper_id": paper_id}
            )

    except Exception as e:
        _pipeline_logger.error(
            f"Failed to write output files: {e}",
            extra={"paper_id": paper_id},
            exc_info=True
        )
        if PIPELINE_LOGGING_AVAILABLE:
            error_collector.record(
                SerializationError(f"Output serialization failed: {e}", paper_id=paper_id),
                ErrorSeverity.DEGRADED,
                "serialization",
            )
            # Try to write at least the error log
            try:
                error_collector.to_jsonl(out_dir / "errors.jsonl")
            except Exception:
                pass

    # Lifecycle tracking: Final status update
    if lifecycle_service:
        try:
            if status == "SUCCESS":
                # Archive successfully processed papers
                lifecycle_service.transition(
                    paper_id=paper_id,
                    stage=LifecycleStage.ARCHIVED,
                    status=StageStatus.SUCCESS,
                    run_id=run_id,
                    triggered_by="pipeline",
                    details={"profile": profile, "n_claims": len(claims), "n_rules": len(rules)},
                )
                lifecycle_service.update_paper_metrics(
                    paper_id=paper_id,
                    has_blocking_issues=0,
                )
                _pipeline_logger.debug(f"Lifecycle: {paper_id} -> ARCHIVED", extra={"paper_id": paper_id})
            elif status == "FAIL":
                lifecycle_service.transition(
                    paper_id=paper_id,
                    stage=LifecycleStage.FAILED,
                    status=StageStatus.FAILED,
                    run_id=run_id,
                    triggered_by="pipeline",
                    error_message="; ".join(blocking) if blocking else "Processing failed",
                    blocking_reason=blocking[0] if blocking else None,
                )
                lifecycle_service.update_paper_metrics(
                    paper_id=paper_id,
                    has_blocking_issues=1,
                    n_failures=1,  # Note: this should increment, but for simplicity set to 1
                )
                _pipeline_logger.debug(f"Lifecycle: {paper_id} -> FAILED", extra={"paper_id": paper_id})
            # PARTIAL_SUCCESS stays at current stage (SYNTHESIZED or EXTRACTED)
        except Exception as lifecycle_err:
            _pipeline_logger.warning(f"Lifecycle final status update failed: {lifecycle_err}")

    return {
        "run_id": run_id,
        "paper_id": paper_id,
        "status": status,
        "n_claims": len(claims),
        "n_rules": len(rules),
        "blocking_issues": blocking,
        # Sprint 2: Web of Belief integration summary
        "web_integration": web_integration_result.get("web_integration"),
        "n_beliefs": web_integration_result.get("n_beliefs", 0),
        "n_stubs": web_integration_result.get("n_stubs", 0),
        "coherence": web_integration_result.get("coherence_after"),
        # TBL-4: Table extraction summary
        "n_tables": len(extracted_tables),
        "n_table_claims": len(table_claims),
        # Sprint 2.0.5: Error summary
        "n_errors": len(error_collector.errors) if PIPELINE_LOGGING_AVAILABLE else 0,
        "has_blocking_errors": error_collector.has_blocking_errors() if PIPELINE_LOGGING_AVAILABLE else False,
    }

# --- CHATGPT_PATCH_AE_AF_WIRING_V1 BEGIN ---
"""
Contract wiring entrypoint for Article Finder to Article Eater.

This function is called by app/cli/article_eater_contract_cli.py when present.
It is intentionally defensive: it attempts to call the existing extraction pipeline
if available, but will degrade gracefully if the extractor signature differs.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import importlib
import hashlib

def _resolve_outcome_id(raw_id, paper_id=None):
    """Resolve outcome ID through Outcome_Contractor."""
    try:
        result = resolve_or_queue(str(raw_id), paper_id=paper_id)
        return result['canonical_id']
    except Exception:
        return str(raw_id)


def _read_text_if_exists(p: Path) -> Optional[str]:
    try:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return None

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def _try_call_extractor(fulltext: str, meta: Dict[str, Any], profile: str) -> Dict[str, Any]:
    mod = _safe_import("app.services.extract_article_essence")
    if mod is None:
        return {"_error": "extract_article_essence_import_failed"}
    candidates = ["extract_findings_from_text", "extract_article_essence", "extract", "run_extract", "run", "main_extract"]
    last = None
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            try:
                # Try a few common call patterns
                try:
                    return fn(fulltext=fulltext, meta=meta, profile=profile)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext, meta)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn({"fulltext": fulltext, "meta": meta, "profile": profile})  # type: ignore
                except TypeError:
                    pass
            except Exception as e:
                last = e
                continue
    if last is not None:
        return {"_error": "extractor_call_failed: %s: %s" % (last.__class__.__name__, str(last))}
    return {"_error": "no_extractor_entrypoint_found"}

def run_from_contract_bundle(
    *,
    in_dir: Path,
    out_dir: Path,
    profile: str,
    hitl: str,
    web_options: Optional[Dict[str, Any]] = None,
    export_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compat wrapper used by CLI; delegates to implementation with contract outputs."""
    return _run_from_contract_bundle_impl(
        in_dir=in_dir,
        out_dir=out_dir,
        profile=profile,
        hitl=hitl,
        web_options=web_options,
        export_options=export_options,
    )
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 END ---
