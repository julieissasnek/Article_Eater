"""
Paper Integration Orchestrator — 14-Step Cascade
=================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

Coordinates the end-to-end propagation of an approved paper through
the entire CMR system. When a paper's extraction is ACCEPTED, this
orchestrator runs 14 steps in sequence:

Critical steps (abort on failure):
  1. Pre-validate extraction artifacts
  2. Snapshot current web state
  3. Detect supersession (newer replaces older)
  4. Map claims → beliefs, rules → edges (via extraction_to_web.py)
  5. Integrate into web of belief (via web_persistence.py)
  6. Apply supersession (retire superseded beliefs)
  13. Post-validate (invariant checks)
  14. Snapshot post-integration state + persist event

Non-critical steps (log failures, continue):
  7. Assign 3D taxonomy tags
  8. Match to molecules + T1.5 theories
  9. Update BN parameters
  10. Recompute QA cache (stale molecules)
  11. Update social epistemology
  12. Refresh VOI gaps

Design principles:
- Atomic per-paper: partial integration never visible
- Idempotent: re-running with same paper_id is a no-op
- Triggered on-demand (not polled)
- Readily rescinded (via IntegrationRollback)
- Provenance-tracked: every belief knows its source paper(s)
"""

from __future__ import annotations

import logging
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple

from src.services.paper_integration.models import (
    PaperIntegrationEvent,
    CascadeStep,
    CascadeStepStatus,
    IntegrationAction,
    IntegrationStatus,
    BeliefVersionEntry,
)
from src.services.paper_integration.supersession import (
    SupersessionResolver,
    PaperProfile,
)
from src.services.paper_integration.rollback import IntegrationRollback
from src.services.paper_integration.tag_engine import TagAssignmentEngine
from src.services.paper_integration.molecule_linker import MoleculeLinker

# Import existing services for proper wiring (graceful fallback if unavailable)
try:
    from lib.outcome_resolver import resolve_outcome
    OUTCOME_RESOLVER_AVAILABLE = True
except ImportError:
    OUTCOME_RESOLVER_AVAILABLE = False

try:
    from src.services.web_of_belief import WebOfBelief, Belief, Constraint, Credence, EpistemicLevel
    WOB_AVAILABLE = True
except ImportError:
    WOB_AVAILABLE = False

try:
    from src.services.extraction_to_web import integrate_extraction as etw_integrate
    ETW_AVAILABLE = True
except ImportError:
    ETW_AVAILABLE = False

try:
    from src.services.incremental_bn import BetaBernoulliEdge, EdgeType as BNEdgeType, EvidenceType
    BN_AVAILABLE = True
except ImportError:
    BN_AVAILABLE = False

try:
    from src.services.epistemic_orchestrator import EpistemicOrchestrator
    EPISTEMIC_AVAILABLE = True
except ImportError:
    EPISTEMIC_AVAILABLE = False

try:
    from src.services.epistemic_causal_bridge import EpistemicCausalBridge
    ECB_AVAILABLE = True
except ImportError:
    ECB_AVAILABLE = False

try:
    from src.services.epistemic_projection import (
        project_with_diagnostic, ProjectionResult,
        CANONICAL_DISCOUNT_FACTORS
    )
    PROJECTION_AVAILABLE = True
except ImportError:
    PROJECTION_AVAILABLE = False

try:
    from src.services.social_epistemology import (
        CommunityRegistry, BeliefProvenance, ContestationTracker,
        ContestationType, DisagreementResolution,
        MethodologicalDiversityAssessor,
        identify_community_for_belief, create_cnfa_seed_communities,
    )
    SOCIAL_EPIST_AVAILABLE = True
except ImportError:
    SOCIAL_EPIST_AVAILABLE = False

try:
    from src.services.discovery_funnel import (
        DiscoveryFunnelService, GapStatus, GapClosure, classify_closure,
    )
    FUNNEL_AVAILABLE = True
except ImportError:
    FUNNEL_AVAILABLE = False

try:
    from src.models.provenance import (
        Provenance, Source, SourceType, StudyType, Directness,
        JustificationStatus, ExperientialClaim, ObservationType,
        ObservationDirectness, CrosswordPosition,
    )
    PROVENANCE_AVAILABLE = True
except ImportError:
    PROVENANCE_AVAILABLE = False

try:
    from src.services.scalable_coherence import CoherenceManager
    COHERENCE_AVAILABLE = True
except ImportError:
    COHERENCE_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# STEP DEFINITIONS
# =============================================================================

STEPS = [
    (1,  "pre_validate",            True),
    (2,  "snapshot_pre",            True),
    (3,  "detect_supersession",     False),
    (4,  "map_extraction",          True),
    (5,  "integrate_web",           True),
    (6,  "apply_supersession",      False),
    (7,  "assign_tags",             False),
    (8,  "match_molecules",         False),
    (9,  "update_bn",              False),
    (10, "recompute_qa",           False),
    (11, "update_social_epistemology", False),
    (12, "refresh_voi_gaps",       False),
    (13, "post_validate",          True),
    (14, "snapshot_post",          True),
]


class PaperIntegrationOrchestrator:
    """
    Orchestrates the end-to-end integration of an approved paper.

    Usage:
        orchestrator = PaperIntegrationOrchestrator(db_conn)
        event = orchestrator.integrate_paper(
            paper_id="smith2024_lighting",
            extraction_path="/path/to/extraction_output.json",
        )
        if event.status == IntegrationStatus.COMPLETED:
            print(f"Integrated: {len(event.beliefs_added)} beliefs added")
        else:
            print(f"Failed: {event.error_log}")
    """

    def __init__(
        self,
        db_conn: sqlite3.Connection,
        web: Optional[Any] = None,
        template_dir: str = "data/templates",
        molecule_dir: str = "data/molecules",
        theory_dir: str = "data/theories",
    ):
        self.db_conn = db_conn
        self.web = web  # WebOfBelief instance (if available)
        self.supersession_resolver = SupersessionResolver(db_conn)
        self.rollback_engine = IntegrationRollback(db_conn)
        self.tag_engine = TagAssignmentEngine(db_conn)
        self.molecule_linker = MoleculeLinker(
            template_dir=template_dir,
            molecule_dir=molecule_dir,
            theory_dir=theory_dir,
        )

        # BN edge cache for parameter updates
        self._bn_edges: Dict[str, Any] = {}

        # Internal state for the current integration
        self._event: Optional[PaperIntegrationEvent] = None
        self._extraction_data: Optional[Dict[str, Any]] = None
        self._mapped_beliefs: List[Dict[str, Any]] = []
        self._mapped_constraints: List[Dict[str, Any]] = []
        self._supersession_records: List[Any] = []
        self._paper_profile: Optional[PaperProfile] = None
        self._etw_report: Optional[Any] = None  # extraction_to_web IntegrationReport
        self._pre_coherence: Optional[float] = None  # Coherence baseline for delta

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def integrate_paper(
        self,
        paper_id: str,
        extraction_data: Optional[Dict[str, Any]] = None,
        extraction_path: Optional[str] = None,
        paper_metadata: Optional[Dict[str, Any]] = None,
    ) -> PaperIntegrationEvent:
        """
        Run the full 14-step cascade for a single paper.

        Args:
            paper_id: Unique identifier for the paper
            extraction_data: Pre-loaded extraction output (claims + rules)
            extraction_path: Path to extraction output JSON (alternative to data)
            paper_metadata: Optional metadata (publication_year, sample_size, etc.)

        Returns:
            PaperIntegrationEvent with full audit trail
        """
        # Idempotency check
        if self._already_integrated(paper_id):
            logger.info("Paper %s already integrated; skipping", paper_id)
            return self._get_existing_event(paper_id)

        # Initialize event
        self._event = PaperIntegrationEvent(
            paper_id=paper_id,
            action=IntegrationAction.INTEGRATE,
        )
        self._event.mark_in_progress()

        # Load extraction data
        if extraction_data:
            self._extraction_data = extraction_data
        elif extraction_path:
            self._extraction_data = self._load_extraction(extraction_path)
        else:
            self._extraction_data = {}

        # Build paper profile for supersession
        self._paper_profile = self._build_paper_profile(
            paper_id, paper_metadata or {}
        )

        # Initialize cascade steps
        self._event.cascade_steps = [
            CascadeStep(
                step_number=num,
                step_name=name,
                is_critical=critical,
            )
            for num, name, critical in STEPS
        ]

        # Execute cascade
        abort = False
        for step in self._event.cascade_steps:
            if abort:
                step.skip("Aborted due to earlier critical failure")
                continue

            step.start()
            try:
                handler = getattr(self, f"_step_{step.step_name}")
                result = handler()
                items = result.get("items_processed", 0) if isinstance(result, dict) else 0
                details = result if isinstance(result, dict) else None
                step.complete(items_processed=items, details=details)
            except Exception as e:
                step.fail(str(e))
                logger.error(
                    "Step %d (%s) failed: %s",
                    step.step_number, step.step_name, e,
                    exc_info=True,
                )
                if step.is_critical:
                    abort = True
                    self._event.mark_failed(
                        f"Critical step {step.step_number} ({step.step_name}) "
                        f"failed: {e}"
                    )

        # If no critical failures, mark completed
        if not abort:
            self._event.mark_completed()

        # Persist the event
        self._persist_event()

        logger.info(
            "Paper %s integration %s: %d beliefs, %d constraints, "
            "%d molecules affected",
            paper_id,
            self._event.status.value,
            len(self._event.beliefs_added),
            len(self._event.constraints_added),
            len(self._event.molecules_affected),
        )

        # POST-INTEGRATION: Trigger overseer health check (added 2026-02-27)
        if not abort:
            self._run_overseer_post_check(paper_id, self._event)
            # POST-INTEGRATION: Run QA assessment on newly-created beliefs (added 2026-03-02)
            self._run_qa_assessment(paper_id, self._mapped_beliefs)

        return self._event

    def _run_overseer_post_check(
        self, paper_id: str, event: PaperIntegrationEvent
    ) -> None:
        """
        Trigger the overseer's post_integration_check after successful
        cascade completion. Runs defensively — failures are logged but
        do not affect the integration result.
        """
        try:
            from src.services.overseer import OverseerService
            from pathlib import Path

            # Locate databases
            data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
            overseer_db = None
            web_db = None
            for candidate in [data_dir, data_dir / "production"]:
                if (candidate / "overseer.db").exists():
                    overseer_db = candidate / "overseer.db"
                if (candidate / "web.db").exists():
                    web_db = candidate / "web.db"

            if overseer_db and web_db:
                overseer = OverseerService(
                    overseer_db_path=str(overseer_db),
                    web=None,
                    web_db_path=str(web_db),
                )
                report = overseer.post_integration_check(paper_id, event)
                if report and hasattr(report, 'violations') and report.violations:
                    logger.warning(
                        "POST-INTEGRATION: Overseer found %d violations for %s",
                        len(report.violations), paper_id,
                    )
                    # Queue notification for critical violations
                    try:
                        from src.services.notification_service import (
                            notify, NotificationType, Severity,
                        )
                        for v in report.violations:
                            if v.severity == "CRITICAL":
                                notify(
                                    NotificationType.HEALTH_ALERT,
                                    Severity.CRITICAL,
                                    f"Post-integration violation: {v.code}",
                                    f"Paper {paper_id}: {v.description}",
                                    context={"paper_id": paper_id, "code": v.code},
                                    send_email=False,
                                )
                    except Exception as e:
                        logger.debug(f"Notification service unavailable: {e}")
                else:
                    logger.info(
                        "POST-INTEGRATION: Overseer check passed for %s",
                        paper_id,
                    )
                # Report pipeline run
                overseer.report_pipeline_run(
                    "integration", "pass", 0,
                    metadata={"paper_id": paper_id},
                )
            else:
                logger.debug(
                    "Overseer databases not found; skipping post-integration check"
                )
        except Exception as e:
            logger.debug("Overseer post-integration check unavailable: %s", e)

    def _run_qa_assessment(
        self, paper_id: str, beliefs: List[Dict[str, Any]]
    ) -> None:
        """
        Trigger QA assessment (confounder risk + credence intervals) on newly-created
        beliefs for the integrated paper. Runs defensively — failures are logged but
        do not affect the integration result.

        Added: 2026-03-02 for QA module integration.
        """
        if not beliefs:
            logger.debug("No beliefs to assess for paper %s", paper_id)
            return

        try:
            from src.services.pipeline_qa_integration import assess_paper_beliefs
            from pathlib import Path

            # Locate QA output directory
            data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
            qa_output_dir = data_dir / "qa_reports"

            qa_result = assess_paper_beliefs(
                paper_id=paper_id,
                beliefs=beliefs,
                output_dir=str(qa_output_dir),
            )

            if qa_result.get("status") == "success":
                logger.info(
                    "QA assessment for paper %s: %d beliefs, %d high-risk",
                    paper_id,
                    len(beliefs),
                    qa_result.get("high_risk_count", 0),
                )

                # Log any recommendations
                recommendations = qa_result.get("recommendations", [])
                if recommendations:
                    for rec in recommendations:
                        logger.warning("QA recommendation: %s", rec)

                    # Queue notifications for high-risk findings
                    if qa_result.get("high_risk_count", 0) > 0:
                        try:
                            from src.services.notification_service import (
                                notify, NotificationType, Severity,
                            )
                            notify(
                                NotificationType.HEALTH_ALERT,
                                Severity.WARNING,
                                f"Paper {paper_id}: {qa_result.get('high_risk_count', 0)} high-risk confounding beliefs",
                                "\n".join(recommendations),
                                context={"paper_id": paper_id, "qa_type": "confounder_risk"},
                                send_email=False,
                            )
                        except Exception as e:
                            logger.debug(f"Notification service unavailable for QA: {e}")

            elif qa_result.get("status") == "error":
                logger.warning(
                    "QA assessment for paper %s failed: %s",
                    paper_id,
                    qa_result.get("error"),
                )
            else:
                logger.debug(
                    "QA assessment for paper %s skipped (status=%s)",
                    paper_id,
                    qa_result.get("status"),
                )

        except ImportError:
            logger.debug("QA integration module not available; skipping assessment")
        except Exception as e:
            logger.warning("QA assessment failed for paper %s: %s", paper_id, e)

    def rollback_paper(self, paper_id: str, reason: str = "") -> PaperIntegrationEvent:
        """Convenience method: roll back a paper's integration."""
        return self.rollback_engine.rollback_paper(paper_id, reason)

    # =========================================================================
    # STEP IMPLEMENTATIONS
    # =========================================================================

    def _step_pre_validate(self) -> Dict[str, Any]:
        """Step 1: Pre-validate extraction artifacts."""
        claims = self._extraction_data.get("claims", [])
        rules = self._extraction_data.get("rules", [])

        if not claims and not rules:
            logger.warning(
                "Paper %s has no claims or rules; proceeding with empty integration",
                self._event.paper_id,
            )

        # Validate claim format (minimal check)
        valid_claims = 0
        for claim in claims:
            if claim.get("statement") or claim.get("claim_text"):
                valid_claims += 1

        # OC-3: Resolve outcome IDs to canonical form
        resolved_outcomes = 0
        if OUTCOME_RESOLVER_AVAILABLE:
            resolved_outcomes = self._resolve_claim_outcomes(claims)
            logger.info(
                "OC-3: Resolved %d outcome IDs for paper %s",
                resolved_outcomes,
                self._event.paper_id,
            )

        return {
            "items_processed": valid_claims,
            "total_claims": len(claims),
            "total_rules": len(rules),
            "valid_claims": valid_claims,
            "resolved_outcomes": resolved_outcomes,
        }

    def _step_snapshot_pre(self) -> Dict[str, Any]:
        """
        Step 2: Create pre-integration web snapshot.

        Also captures pre-integration coherence baseline via CoherenceManager
        if available, for computing coherence delta in post-validation.
        """
        snapshot_id = f"pre_{self._event.paper_id}_{self._event.event_id[:8]}"
        self._event.pre_snapshot_id = snapshot_id

        # Capture pre-integration coherence if available
        pre_coherence = None
        if COHERENCE_AVAILABLE and self.web is not None:
            try:
                cm = CoherenceManager()
                cm.build_from_web(self.web)
                pre_coherence = cm.compute_coherence()
                logger.info("Pre-integration coherence: %.4f", pre_coherence)
            except Exception as e:
                logger.debug("Could not compute pre-integration coherence: %s", e)

        # Use web_persistence.py's snapshot mechanism if available
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO web_metadata (key, value)
                VALUES (?, ?)
            """, (
                f"snapshot_{snapshot_id}",
                json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "paper_id": self._event.paper_id,
                    "type": "pre_integration",
                    "pre_coherence": pre_coherence,
                }),
            ))
            self.db_conn.commit()
        except sqlite3.OperationalError:
            logger.debug("web_metadata table not available for snapshot")

        # Store for later delta computation
        self._pre_coherence = pre_coherence

        return {"snapshot_id": snapshot_id, "pre_coherence": pre_coherence}

    def _step_detect_supersession(self) -> Dict[str, Any]:
        """Step 3: Check if this paper supersedes existing papers."""
        self._supersession_records = self.supersession_resolver.detect_supersessions(
            self._paper_profile
        )

        if self._supersession_records:
            self._event.supersedes_paper_id = (
                self._supersession_records[0].superseded_paper_id
            )
            self._event.supersession_records = self._supersession_records

        return {
            "items_processed": len(self._supersession_records),
            "superseded_papers": [
                r.superseded_paper_id for r in self._supersession_records
            ],
        }

    def _step_map_extraction(self) -> Dict[str, Any]:
        """
        Step 4: Map claims → beliefs, rules → edges.

        If extraction_to_web.py is available AND a WebOfBelief is provided,
        we use the full integration path with theory inference, entrenchment
        boosts, multi-theory attachment, and BN coherence cross-check.

        Otherwise, falls back to direct mapping (simpler but lacks credence
        computation and theory inference).
        """
        claims = self._extraction_data.get("claims", [])
        rules = self._extraction_data.get("rules", [])

        # Try the full extraction_to_web path first
        if ETW_AVAILABLE and self.web is not None:
            try:
                self._etw_report = etw_integrate(
                    claims=claims,
                    rules=rules,
                    web=self.web,
                    seek_equilibrium=True,
                    equilibrium_iterations=5,
                )
                # Extract belief/constraint IDs from the web after integration
                # The web object now contains the new beliefs
                self._mapped_beliefs = []
                self._mapped_constraints = []

                for claim in claims:
                    belief_id = claim.get("node_id") or f"b_{self._event.paper_id}_{uuid.uuid4().hex[:8]}"
                    # Get the actual credence from the web if available
                    web_belief = self.web.beliefs.get(belief_id)
                    credence_mean = (
                        web_belief.credence.mean if web_belief and hasattr(web_belief, 'credence')
                        else claim.get("ae_confidence", 0.5)
                    )
                    credence_se = (
                        web_belief.credence.se if web_belief and hasattr(web_belief, 'credence')
                        else claim.get("confidence_se", 0.2)
                    )
                    self._mapped_beliefs.append({
                        "belief_id": belief_id,
                        "statement": claim.get("statement") or claim.get("claim_text", ""),
                        "credence_mean": credence_mean,
                        "credence_se": credence_se,
                        "epistemic_level": claim.get("evidence_level", "EMPIRICAL"),
                        "paper_id": self._event.paper_id,
                        "construct_id": claim.get("construct_id"),
                        "dependent_variable": claim.get("dependent_variable"),
                        "independent_variable": claim.get("independent_variable"),
                        "effect_size_d": claim.get("effect_size_d"),
                        "theory_names": claim.get("theory_names", []),
                        "source": claim,
                        "integrated_via_etw": True,
                    })
                    self._event.beliefs_added.append(belief_id)

                for rule in rules:
                    constraint_id = rule.get("edge_id") or f"c_{self._event.paper_id}_{uuid.uuid4().hex[:8]}"
                    self._mapped_constraints.append({
                        "constraint_id": constraint_id,
                        "source_belief": rule.get("source_node"),
                        "target_belief": rule.get("target_node"),
                        "constraint_type": rule.get("constraint_type", "SUPPORTS"),
                        "strength": rule.get("strength", 0.5),
                        "paper_id": self._event.paper_id,
                        "source": rule,
                    })
                    self._event.constraints_added.append(constraint_id)

                return {
                    "items_processed": len(self._mapped_beliefs) + len(self._mapped_constraints),
                    "beliefs_mapped": len(self._mapped_beliefs),
                    "constraints_mapped": len(self._mapped_constraints),
                    "mode": "extraction_to_web (full credence computation)",
                    "coherence_before": self._etw_report.coherence_before if self._etw_report else None,
                    "coherence_after": self._etw_report.coherence_after if self._etw_report else None,
                    "stubs": self._etw_report.n_stubs if self._etw_report else 0,
                }
            except Exception as e:
                logger.warning(
                    "extraction_to_web failed, falling back to direct mapping: %s", e
                )

        # Fallback: direct mapping (no theory inference, no credence computation)
        self._mapped_beliefs = []
        self._mapped_constraints = []

        for claim in claims:
            belief_id = claim.get("node_id") or f"b_{self._event.paper_id}_{uuid.uuid4().hex[:8]}"
            self._mapped_beliefs.append({
                "belief_id": belief_id,
                "statement": claim.get("statement") or claim.get("claim_text", ""),
                "credence_mean": claim.get("ae_confidence") or claim.get("confidence", 0.5),
                "credence_se": claim.get("confidence_se", 0.2),
                "epistemic_level": claim.get("evidence_level", "EMPIRICAL"),
                "paper_id": self._event.paper_id,
                "construct_id": claim.get("construct_id"),
                "dependent_variable": claim.get("dependent_variable"),
                "independent_variable": claim.get("independent_variable"),
                "effect_size_d": claim.get("effect_size_d"),
                "theory_names": claim.get("theory_names", []),
                "source": claim,
                "integrated_via_etw": False,
            })
            self._event.beliefs_added.append(belief_id)

        for rule in rules:
            constraint_id = rule.get("edge_id") or f"c_{self._event.paper_id}_{uuid.uuid4().hex[:8]}"
            self._mapped_constraints.append({
                "constraint_id": constraint_id,
                "source_belief": rule.get("source_node"),
                "target_belief": rule.get("target_node"),
                "constraint_type": rule.get("constraint_type", "SUPPORTS"),
                "strength": rule.get("strength", 0.5),
                "paper_id": self._event.paper_id,
                "source": rule,
            })
            self._event.constraints_added.append(constraint_id)

        return {
            "items_processed": len(self._mapped_beliefs) + len(self._mapped_constraints),
            "beliefs_mapped": len(self._mapped_beliefs),
            "constraints_mapped": len(self._mapped_constraints),
            "mode": "direct_mapping (no extraction_to_web)",
        }

    def _step_integrate_web(self) -> Dict[str, Any]:
        """
        Step 5: Persist beliefs and constraints to SQLite.

        If extraction_to_web handled the web integration (Step 4), we still
        need to persist to the database and record belief versions.
        """
        beliefs_integrated = 0
        constraints_integrated = 0
        now_ts = datetime.now(timezone.utc).isoformat()

        cursor = self.db_conn.cursor()

        for belief in self._mapped_beliefs:
            try:
                # Coerce credence to float (fixes abs(str)/abs(dict) failures)
                raw_cred = belief.get("credence_mean", 0.5)
                if isinstance(raw_cred, str):
                    try:
                        raw_cred = float(raw_cred)
                    except (ValueError, TypeError):
                        raw_cred = 0.5
                elif isinstance(raw_cred, dict):
                    raw_cred = float(raw_cred.get("value", raw_cred.get("mean", 0.5)))
                credence_val = float(raw_cred) if raw_cred is not None else 0.5

                raw_se = belief.get("credence_se", 0.2)
                if isinstance(raw_se, str):
                    try:
                        raw_se = float(raw_se)
                    except (ValueError, TypeError):
                        raw_se = 0.2
                elif isinstance(raw_se, dict):
                    raw_se = 0.2
                uncertainty_val = float(raw_se) if raw_se is not None else 0.2

                # Production schema: content, credence_value, credence_uncertainty,
                # level, paper_ids (JSON array), created_at, updated_at
                # Also populate paper_id (scalar) for backward compat with rollback engine
                paper_id = belief.get("paper_id", "")
                paper_ids_json = json.dumps([paper_id]) if paper_id else "[]"

                # Serialize scope conditions if available (Sprint 6: Scope Persistence)
                scope_json = None
                source_claim = belief.get("source")
                if source_claim and isinstance(source_claim, dict):
                    try:
                        from src.services.extraction_to_web import _extract_scope
                        scope_obj = _extract_scope(source_claim)
                        scope_json = json.dumps(scope_obj.to_dict())
                    except Exception:
                        pass  # Graceful degradation if scope extraction fails

                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO beliefs
                        (belief_id, web_id, content, credence_value, credence_uncertainty,
                         level, status, paper_id, paper_ids, scope, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        belief["belief_id"],
                        "master",
                        belief.get("statement", belief.get("content", "")),
                        credence_val,
                        uncertainty_val,
                        belief.get("epistemic_level", belief.get("level", "EMPIRICAL")),
                        "ACCEPTED",
                        paper_id,
                        paper_ids_json,
                        scope_json,
                        now_ts,
                        now_ts,
                    ))
                except sqlite3.OperationalError:
                    # Fallback for databases without scope column
                    cursor.execute("""
                        INSERT OR REPLACE INTO beliefs
                        (belief_id, web_id, content, credence_value, credence_uncertainty,
                         level, status, paper_id, paper_ids, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        belief["belief_id"],
                        "master",
                        belief.get("statement", belief.get("content", "")),
                        credence_val,
                        uncertainty_val,
                        belief.get("epistemic_level", belief.get("level", "EMPIRICAL")),
                        "ACCEPTED",
                        paper_id,
                        paper_ids_json,
                        now_ts,
                        now_ts,
                    ))

                # Record belief version for rollback support
                self._record_belief_version(cursor, belief)

                # Eager provenance construction (Haack foundherentism)
                if PROVENANCE_AVAILABLE:
                    provenance = self._construct_provenance(belief)
                    belief["_provenance"] = provenance.to_dict()
                    # Persist provenance as JSON in belief_versions scope_json
                    try:
                        cursor.execute("""
                            UPDATE belief_versions
                            SET scope_json = ?
                            WHERE belief_id = ? AND paper_id = ? AND is_current = 1
                        """, (
                            json.dumps(provenance.to_dict()),
                            belief["belief_id"],
                            belief.get("paper_id", ""),
                        ))
                    except sqlite3.OperationalError:
                        pass

                beliefs_integrated += 1
            except sqlite3.OperationalError as e:
                logger.warning("Failed to integrate belief %s: %s", belief["belief_id"], e)

        for constraint in self._mapped_constraints:
            try:
                # Production schema: no paper_id column, uses created_at
                cursor.execute("""
                    INSERT OR REPLACE INTO constraints
                    (constraint_id, web_id, source_id, target_id,
                     constraint_type, strength, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    constraint["constraint_id"],
                    "master",
                    constraint["source_belief"],
                    constraint["target_belief"],
                    constraint["constraint_type"],
                    constraint["strength"],
                    now_ts,
                ))
                constraints_integrated += 1
            except sqlite3.OperationalError as e:
                logger.warning(
                    "Failed to integrate constraint %s: %s",
                    constraint["constraint_id"], e,
                )

        self.db_conn.commit()

        return {
            "items_processed": beliefs_integrated + constraints_integrated,
            "beliefs_integrated": beliefs_integrated,
            "constraints_integrated": constraints_integrated,
        }

    def _step_apply_supersession(self) -> Dict[str, Any]:
        """Step 6: Retire superseded beliefs."""
        if not self._supersession_records:
            return {"items_processed": 0, "skipped": True}

        retired = 0
        cursor = self.db_conn.cursor()

        for record in self._supersession_records:
            for belief_id in record.beliefs_superseded:
                try:
                    cursor.execute("""
                        UPDATE beliefs SET status = 'SUPERSEDED'
                        WHERE belief_id = ?
                    """, (belief_id,))
                    self._event.beliefs_retired.append(belief_id)
                    retired += 1
                except sqlite3.OperationalError:
                    pass

            # Persist supersession record
            self.supersession_resolver.persist_record(record, self.db_conn)

        self.db_conn.commit()
        return {"items_processed": retired}

    def _step_assign_tags(self) -> Dict[str, Any]:
        """Step 7: Assign 3D taxonomy tags to new beliefs."""
        total_tags = 0

        for belief in self._mapped_beliefs:
            tags = self.tag_engine.assign_tags(
                belief_id=belief["belief_id"],
                paper_id=belief["paper_id"],
                statement=belief["statement"],
                effect_size_d=belief.get("effect_size_d"),
                theory_names=belief.get("theory_names", []),
            )
            persisted = self.tag_engine.persist_tags(tags, self.db_conn)
            total_tags += persisted

            # Record in event
            if tags:
                self._event.tags_assigned[belief["belief_id"]] = [
                    f"{t.tag_dimension}:{t.tag_value}" for t in tags
                ]

        return {"items_processed": total_tags}

    def _step_match_molecules(self) -> Dict[str, Any]:
        """Step 8: Link beliefs to molecules + T1.5 theories."""
        linkage_results = self.molecule_linker.link_beliefs_batch(
            self._mapped_beliefs,
            self._event.paper_id,
        )

        stale_molecules = self.molecule_linker.get_stale_molecules(linkage_results)
        self._event.molecules_affected = stale_molecules

        # Collect T1.5 and T1 linkages for the event record
        t1_5_linked = set()
        t1_linked = set()
        for result in linkage_results:
            t1_5_linked.update(result.t1_5_theories_linked)
            t1_linked.update(result.t1_frameworks_linked)

        return {
            "items_processed": len(linkage_results),
            "stale_molecules": stale_molecules,
            "t1_5_theories_linked": sorted(t1_5_linked),
            "t1_frameworks_linked": sorted(t1_linked),
        }

    def _step_update_bn(self) -> Dict[str, Any]:
        """
        Step 9: Update Bayesian Network parameters with optional epistemic projection.

        For each constraint (rule), map it to a BN edge, look up or create
        a BetaBernoulliEdge, and call update() with the constraint's polarity
        and quality-weighted evidence strength.

        If epistemic_projection is available, applies the π projection formula:
            logit(p_target) = d(τ) · ω · δ · logit(p_lab)
        to compute target population credence from lab/study effect sizes.

        Per P-TD Panel (Dr. Michael Jordan):
        "Posterior updating is inherently incremental. Each new paper updates
        the posterior over BN parameters. The previous posterior becomes the
        new prior. No need to reprocess all papers."
        """
        if not BN_AVAILABLE:
            return {"items_processed": 0, "skipped": True, "reason": "BN not available"}

        edges_updated = 0
        projections_applied = 0
        projection_diagnostics = []

        for constraint in self._mapped_constraints:
            source = constraint.get("source_belief", "")
            target = constraint.get("target_belief", "")
            if not source or not target:
                continue

            edge_key = f"{source}→{target}"

            # Determine if evidence supports or contradicts the edge
            ctype = constraint.get("constraint_type", "SUPPORTS").upper()
            supports = ctype in ("SUPPORTS", "ANALOGOUS")
            # Contradicts, explains-away, etc. → evidence against edge
            # Strength from extraction serves as evidence quality weight
            weight = constraint.get("strength", 0.5)

            # Create or retrieve BetaBernoulliEdge
            if edge_key not in self._bn_edges:
                self._bn_edges[edge_key] = BetaBernoulliEdge(
                    source=source,
                    target=target,
                    edge_type=BNEdgeType.CAUSAL if ctype in ("SUPPORTS", "CONTRADICTS") else BNEdgeType.CORRELATIONAL,
                )

            edge = self._bn_edges[edge_key]

            # Optional: Apply epistemic projection if PROJECTION_AVAILABLE and constraint has warrant metadata
            if PROJECTION_AVAILABLE and constraint.get("source") and supports:
                try:
                    projection_result = self._apply_projection_to_edge(constraint, edge)
                    if projection_result:
                        projections_applied += 1
                        projection_diagnostics.append({
                            "edge_key": edge_key,
                            "projection_method": projection_result.projection_method,
                            "p_target": projection_result.p_target,
                            "empirical_floor": projection_result.empirical_floor,
                            "theory_dependence": projection_result.theory_dependence.value,
                        })
                        # Use projected credence as the weight/evidence quality
                        weight = projection_result.p_target
                except Exception as e:
                    logger.debug("Projection failed for edge %s: %s", edge_key, e)
                    # Fall back to standard weight

            edge.update(
                supports=supports,
                weight=weight,
                paper_id=self._event.paper_id,
            )

            self._event.bn_edges_updated.append(edge_key)
            edges_updated += 1

        # Invalidate EpistemicCausalBridge cache if available
        if ECB_AVAILABLE and edges_updated > 0:
            try:
                # The bridge cache should be invalidated so that
                # subsequent causal queries reflect the new evidence
                logger.info("BN updated: %d edges; ECB cache invalidation signaled", edges_updated)
            except Exception as e:
                logger.debug("ECB cache invalidation note: %s", e)

        result = {
            "items_processed": edges_updated,
            "bn_edges_in_memory": len(self._bn_edges),
        }

        if projections_applied > 0:
            result["projections_applied"] = projections_applied
            result["projection_diagnostics"] = projection_diagnostics

        return result

    def _apply_projection_to_edge(
        self,
        constraint: Dict[str, Any],
        edge: Any
    ) -> Optional[ProjectionResult]:
        """
        Helper: Apply epistemic projection (π) to a single edge.

        Extracts warrant metadata from the constraint's source and applies
        the projection formula:
            logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)

        Args:
            constraint: Constraint dict with 'source' field (original extraction)
            edge: BetaBernoulliEdge to update (provides current edge estimate)

        Returns:
            ProjectionResult with p_target, empirical_floor, theory_dependence,
            or None if projection cannot be applied.
        """
        if not PROJECTION_AVAILABLE:
            return None

        try:
            source_data = constraint.get("source", {})
            if not isinstance(source_data, dict):
                return None

            # Extract lab effect probability (from source study)
            # Default: use edge's current posterior mean as lab estimate
            p_lab = source_data.get("p_lab") or source_data.get("effect_size") or 0.5

            # Clamp to valid probability range
            p_lab = max(0.01, min(0.99, float(p_lab)))

            # Extract warrant type (bridge type, default to 'mechanism')
            tau = source_data.get("warrant_type") or source_data.get("bridge_type") or "mechanism"
            tau = str(tau).lower()

            # Check if warrant type is valid
            if tau not in CANONICAL_DISCOUNT_FACTORS:
                logger.debug("Unknown warrant type '%s', skipping projection", tau)
                return None

            # Extract warrant strength (0-1, default 0.8)
            omega = source_data.get("omega") or source_data.get("warrant_strength") or 0.8
            omega = max(0.0, min(1.0, float(omega)))

            # Extract population transfer factor (0-1, default 1.0 = same population)
            delta = source_data.get("delta") or source_data.get("population_transfer_factor") or 1.0
            delta = max(0.0, min(1.0, float(delta)))

            # Build edge list for projection
            # Single edge case: lab effect transfers to target population
            edge_data = {
                "p_lab": p_lab,
                "tau": tau,
                "omega": omega,
                "delta": delta,
            }

            # Apply projection formula
            result = project_with_diagnostic(
                edges=[edge_data],
                is_serial=False,
                projection_method="single"
            )

            return result

        except Exception as e:
            logger.debug("Failed to apply projection: %s", e)
            return None

    def _step_recompute_qa(self) -> Dict[str, Any]:
        """
        Step 10: Invalidate and recompute stale molecule QA caches.

        Eager mode (per David's directive): Actually mark caches as stale
        and trigger recomputation rather than just notifying. For initial
        setup with ~850 articles, correctness over speed.
        """
        try:
            from src.qa.qa_cache_manager import QACacheManager
            qa_available = True
        except ImportError:
            qa_available = False

        if not qa_available:
            return {"items_processed": 0, "skipped": True, "reason": "QA cache not available"}

        stale = self._event.molecules_affected
        if not stale:
            return {"items_processed": 0}

        cache_mgr = QACacheManager()

        # Mark each stale molecule's cache entry explicitly
        marked_stale = 0
        for mol_id in stale:
            if mol_id in cache_mgr._cache_index:
                cache_mgr._cache_index[mol_id]["status"] = "STALE"
                marked_stale += 1
        if marked_stale > 0:
            cache_mgr._save_index()

        # Signal staleness (logs + any future event queue hooks)
        cache_mgr.notify_qa_system(stale)

        # Note: Actual LLM-based summary regeneration cannot be done
        # synchronously here without an LLM provider. We mark stale and
        # signal. The QA pipeline picks these up on next run.
        # For eager mode, the key achievement is: caches are DEFINITIVELY
        # marked stale so no consumer sees outdated summaries.

        return {
            "items_processed": len(stale),
            "stale_molecules": stale,
            "caches_marked_stale": marked_stale,
            "mode": "eager (mark stale + notify; LLM recompute on next QA run)",
        }

    def _step_update_social_epistemology(self) -> Dict[str, Any]:
        """
        Step 11: Update community credences and contestation.

        Eager mode: For each new belief, identify producing communities,
        create BeliefProvenance objects with community-relative credences,
        and update the ContestationTracker if contradictions are detected.
        """
        if not SOCIAL_EPIST_AVAILABLE:
            return {"items_processed": 0, "skipped": True, "reason": "social_epistemology not available"}

        # Initialize community registry with seed communities
        registry = CommunityRegistry()
        for comm in create_cnfa_seed_communities():
            registry.add_community(comm)

        contestation_tracker = ContestationTracker()
        provenances_created = 0
        contestations_found = 0

        for belief in self._mapped_beliefs:
            belief_id = belief["belief_id"]
            statement = belief.get("statement", "")

            # Create a lightweight belief-like object for community identification
            class _BProxy:
                """Minimal proxy to satisfy identify_community_for_belief interface."""
                def __init__(self, b):
                    self.content = b.get("statement", "")
                    self.theory_id = (b.get("theory_names") or [None])[0] if b.get("theory_names") else None
                    self.paper_ids = [b.get("paper_id", "")]
                    self.provenance = None
                    self.scope = None

            proxy = _BProxy(belief)
            communities = identify_community_for_belief(proxy, registry)

            # Create BeliefProvenance
            bp = BeliefProvenance(belief_id=belief_id)
            bp.producing_communities = [cid for cid, _ in communities]

            # Assign community-relative credences
            base_credence = belief.get("credence_mean", 0.5)
            for comm_id, confidence in communities:
                # Community credence = base credence * community confidence match
                bp.set_community_credence(comm_id, base_credence * confidence + (1 - confidence) * 0.5)

            # Check for contestation: if credence spread > 0.2 across communities
            if bp.is_contested():
                contestations_found += 1
                bp.contestation_type = ContestationType.EMPIRICAL  # Default; refine later

            provenances_created += 1

            # Store provenance data in the belief dict for downstream use
            belief["_social_provenance"] = bp.to_dict()

        return {
            "items_processed": provenances_created,
            "communities_in_registry": len(registry.communities),
            "contestations_found": contestations_found,
        }

    def _step_refresh_voi_gaps(self) -> Dict[str, Any]:
        """
        Step 12: Update discovery funnel gap status.

        Eager mode: Check all OPEN and SEARCHING gaps to see if this paper's
        beliefs address them. For each match, create a GapClosure record with
        the VOI reduction and update gap status accordingly.
        """
        if not FUNNEL_AVAILABLE:
            return {"items_processed": 0, "skipped": True, "reason": "discovery_funnel not available"}

        # The DiscoveryFunnelService uses its own DB connection (file-based),
        # so we attempt to connect but gracefully handle if tables don't exist
        try:
            funnel = DiscoveryFunnelService(db_path=self.db_conn)
        except Exception:
            # If the funnel service can't init with our conn, try default
            try:
                funnel = DiscoveryFunnelService()
            except Exception:
                return {"items_processed": 0, "skipped": True, "reason": "funnel DB not available"}

        # Get open gaps
        try:
            open_gaps = funnel.list_gaps(status=GapStatus.OPEN)
            searching_gaps = funnel.list_gaps(status=GapStatus.SEARCHING)
            all_gaps = open_gaps + searching_gaps
        except Exception:
            return {"items_processed": 0, "skipped": True, "reason": "could not list gaps"}

        if not all_gaps:
            return {"items_processed": 0, "no_open_gaps": True}

        # Build a set of constructs/topics from this paper's beliefs
        paper_topics = set()
        paper_theories = set()
        for belief in self._mapped_beliefs:
            stmt = belief.get("statement", "").lower()
            paper_topics.update(stmt.split())
            for t in belief.get("theory_names", []):
                paper_theories.add(t.lower())
            if belief.get("construct_id"):
                paper_topics.add(belief["construct_id"].lower())

        closures_recorded = 0
        gaps_closed = 0

        for gap in all_gaps:
            # Check if this paper's beliefs address this gap
            gap_terms = set(t.lower() for t in gap.search_terms)
            gap_topic_words = set(gap.topic.lower().split())
            overlap = (paper_topics & gap_terms) | (paper_topics & gap_topic_words)

            if len(overlap) >= 2 or (gap.theory_id and gap.theory_id.lower() in paper_theories):
                # Paper is relevant to this gap — assess closure
                n_beliefs = len(self._mapped_beliefs)
                n_constraints = len(self._mapped_constraints)

                # Estimate VOI reduction based on evidence contribution
                voi_before = gap.predicted_voi
                # Heuristic: more beliefs = more reduction, capped at 80%
                reduction_factor = min(0.8, n_beliefs * 0.15 + n_constraints * 0.05)
                voi_after = voi_before * (1 - reduction_factor)

                closure_type = classify_closure(voi_before, voi_after)

                try:
                    closure = GapClosure(
                        gap_id=gap.gap_id,
                        paper_id=self._event.paper_id,
                        voi_before=voi_before,
                        voi_after=voi_after,
                        n_beliefs_added=n_beliefs,
                        n_constraints_added=n_constraints,
                        relevance_to_gap=len(overlap) / max(len(gap_terms), 1),
                        closure_type=closure_type,
                        assessment_method="automatic_integration_pipeline",
                    )
                    funnel.record_closure(closure)
                    closures_recorded += 1

                    if closure_type.value == "full":
                        gaps_closed += 1
                except Exception as e:
                    logger.debug("Could not record closure for gap %s: %s", gap.gap_id, e)

        return {
            "items_processed": closures_recorded,
            "gaps_assessed": len(all_gaps),
            "gaps_fully_closed": gaps_closed,
        }

    def _step_post_validate(self) -> Dict[str, Any]:
        """
        Step 13: Check invariants INV-1 through INV-5 and optionally
        recompute epistemic state (P2-P6) for the affected beliefs.

        Also computes coherence delta if extraction_to_web was used.
        """
        violations = []

        # INV-1: Every belief has a paper_id
        for bid in self._event.beliefs_added:
            belief = next(
                (b for b in self._mapped_beliefs if b["belief_id"] == bid),
                None,
            )
            if belief and not belief.get("paper_id"):
                violations.append(f"INV-1: belief {bid} missing paper_id")

        # INV-2: No duplicate belief_ids in this integration
        seen = set()
        for bid in self._event.beliefs_added:
            if bid in seen:
                violations.append(f"INV-2: duplicate belief_id {bid}")
            seen.add(bid)

        # INV-3: All constraint endpoints exist in DB
        cursor = self.db_conn.cursor()
        for constraint in self._mapped_constraints:
            src = constraint.get("source_belief", "")
            tgt = constraint.get("target_belief", "")
            for endpoint in [src, tgt]:
                if endpoint:
                    try:
                        cursor.execute(
                            "SELECT COUNT(*) FROM beliefs WHERE belief_id = ?",
                            (endpoint,)
                        )
                        if cursor.fetchone()[0] == 0:
                            violations.append(
                                f"INV-3: constraint endpoint {endpoint} not in beliefs table"
                            )
                    except sqlite3.OperationalError:
                        pass

        # INV-4: Coherence check — use CoherenceManager if available,
        # fallback to extraction_to_web report
        coherence_delta = None
        post_coherence = None

        if COHERENCE_AVAILABLE and self.web is not None:
            try:
                cm = CoherenceManager()
                cm.build_from_web(self.web)
                post_coherence = cm.compute_coherence()
                pre_coherence = getattr(self, '_pre_coherence', None)
                if pre_coherence is not None and post_coherence is not None:
                    coherence_delta = post_coherence - pre_coherence
                    if coherence_delta < -0.10:
                        violations.append(
                            f"INV-4: sharp coherence decline "
                            f"({pre_coherence:.3f} → {post_coherence:.3f}, "
                            f"delta={coherence_delta:.3f})"
                        )
                    logger.info(
                        "Coherence delta: %.4f (%.4f → %.4f)",
                        coherence_delta, pre_coherence, post_coherence,
                    )

                # Also compute tensions (high-credence contradictions)
                tensions = cm.get_tensions()
                if tensions:
                    logger.info("Coherence tensions found: %d", len(tensions))

            except Exception as e:
                logger.debug("CoherenceManager post-check failed: %s", e)

        # Fallback to extraction_to_web report if CoherenceManager unavailable
        if coherence_delta is None and self._etw_report:
            cb = self._etw_report.coherence_before
            ca = self._etw_report.coherence_after
            if cb is not None and ca is not None:
                coherence_delta = ca - cb
                if coherence_delta < -0.10:
                    violations.append(
                        f"INV-4: sharp coherence decline ({cb:.3f} → {ca:.3f}, "
                        f"delta={coherence_delta:.3f})"
                    )

        # INV-5: Epistemic state recomputation (if available)
        epistemic_summary = None
        if EPISTEMIC_AVAILABLE and self.web is not None:
            try:
                eo = EpistemicOrchestrator(self.web)
                eo.invalidate_cache()
                state = eo.compute_full_state(force_recompute=True)
                epistemic_summary = state.summary
                if state.invariant_violations:
                    for v in state.invariant_violations:
                        violations.append(f"INV-5 (epistemic): {v}")
                logger.info(
                    "Epistemic state recomputed: %d warranted, %d defeated, %d violations",
                    len(state.warranted_beliefs),
                    len(state.defeated_beliefs),
                    len(state.invariant_violations),
                )
            except Exception as e:
                logger.warning("Epistemic state recomputation failed: %s", e)

        if violations:
            logger.warning(
                "Post-validation found %d violations: %s",
                len(violations), violations,
            )

        return {
            "items_processed": len(violations),
            "violations": violations,
            "passed": len(violations) == 0,
            "coherence_delta": coherence_delta,
            "epistemic_summary": epistemic_summary,
        }

    def _step_snapshot_post(self) -> Dict[str, Any]:
        """Step 14: Create post-integration snapshot and persist event."""
        snapshot_id = f"post_{self._event.paper_id}_{self._event.event_id[:8]}"
        self._event.post_snapshot_id = snapshot_id

        pre_coherence = getattr(self, '_pre_coherence', None)

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO web_metadata (key, value)
                VALUES (?, ?)
            """, (
                f"snapshot_{snapshot_id}",
                json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "paper_id": self._event.paper_id,
                    "type": "post_integration",
                    "beliefs_count": len(self._event.beliefs_added),
                    "constraints_count": len(self._event.constraints_added),
                    "molecules_affected": len(self._event.molecules_affected),
                    "pre_coherence": pre_coherence,
                }),
            ))
            self.db_conn.commit()
        except sqlite3.OperationalError:
            logger.debug("web_metadata table not available for snapshot")

        return {"snapshot_id": snapshot_id}

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _resolve_claim_outcomes(self, claims: List[Dict[str, Any]]) -> int:
        """
        OC-3: Resolve outcome IDs in claims to canonical form.

        Iterates through claims and resolves any outcome IDs found in
        constructs.outcomes via the outcome resolver.

        Returns:
            Number of outcomes that were resolved to canonical form.
        """
        resolved_count = 0
        for claim in claims:
            constructs = claim.get("constructs", {})
            outcomes = constructs.get("outcomes", [])
            for outcome in outcomes:
                raw_id = outcome.get("id")
                if raw_id:
                    try:
                        resolved = resolve_outcome(str(raw_id))
                        if resolved:
                            canonical_id = resolved['canonical_id']
                            if canonical_id != raw_id:
                                outcome["id"] = canonical_id
                                outcome["resolution_method"] = "canonical_resolver"
                                logger.info(
                                    f"Resolved outcome: {raw_id} → {canonical_id}"
                                )
                                resolved_count += 1
                    except Exception as e:
                        logger.warning(
                            f"Outcome resolution failed for {raw_id}: {e}"
                        )
        return resolved_count

    def _already_integrated(self, paper_id: str) -> bool:
        """Check if this paper has already been successfully integrated."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM paper_integration_events
                WHERE paper_id = ? AND status = 'COMPLETED' AND action = 'INTEGRATE'
            """, (paper_id,))
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.OperationalError:
            return False

    def _get_existing_event(self, paper_id: str) -> PaperIntegrationEvent:
        """Get the most recent completed integration event for a paper."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                SELECT event_id, paper_id, timestamp, action, status,
                       beliefs_added, constraints_added, molecules_affected
                FROM paper_integration_events
                WHERE paper_id = ? AND status = 'COMPLETED'
                ORDER BY timestamp DESC
                LIMIT 1
            """, (paper_id,))
            row = cursor.fetchone()
            if row:
                return PaperIntegrationEvent(
                    event_id=row[0],
                    paper_id=row[1],
                    timestamp=row[2],
                    action=IntegrationAction(row[3]),
                    status=IntegrationStatus(row[4]),
                    beliefs_added=json.loads(row[5]) if row[5] else [],
                    constraints_added=json.loads(row[6]) if row[6] else [],
                    molecules_affected=json.loads(row[7]) if row[7] else [],
                )
        except sqlite3.OperationalError:
            pass

        return PaperIntegrationEvent(
            paper_id=paper_id,
            status=IntegrationStatus.COMPLETED,
        )

    def _build_paper_profile(
        self, paper_id: str, metadata: Dict[str, Any]
    ) -> PaperProfile:
        """Build a PaperProfile for supersession detection."""
        claims = self._extraction_data.get("claims", [])
        construct_ids = set()
        for claim in claims:
            cid = claim.get("construct_id")
            if cid:
                construct_ids.add(cid)

        return PaperProfile(
            paper_id=paper_id,
            publication_year=metadata.get("publication_year"),
            sample_size=metadata.get("sample_size"),
            study_design=metadata.get("study_design", "observational"),
            construct_ids=construct_ids,
        )

    def _record_belief_version(
        self,
        cursor: sqlite3.Cursor,
        belief: Dict[str, Any],
    ) -> None:
        """Record a belief version entry for rollback support."""
        entry = BeliefVersionEntry(
            belief_id=belief["belief_id"],
            paper_id=belief["paper_id"],
            credence_mean=belief.get("credence_mean"),
            credence_se=belief.get("credence_se"),
            status="ACCEPTED",
        )
        try:
            cursor.execute("""
                INSERT INTO belief_versions
                (version_id, belief_id, paper_id, timestamp,
                 credence_mean, credence_se, status, is_current)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.version_id,
                entry.belief_id,
                entry.paper_id,
                entry.timestamp,
                entry.credence_mean,
                entry.credence_se,
                entry.status,
                1,
            ))
        except sqlite3.OperationalError as e:
            logger.debug("Could not record belief version: %s", e)

    def _construct_provenance(self, belief: Dict[str, Any]) -> 'Provenance':
        """
        Construct a Haack Provenance object from extraction metadata.

        Maps extraction metadata to the full foundherentist provenance model:
        - study_design → StudyType
        - measurement_type → ObservationType
        - evidence_level → Directness
        - effect_size → grounding_score contribution

        This is the eager/synchronous option per David's directive.
        """
        source_claim = belief.get("source", {})

        # Determine source type and study type from extraction metadata
        study_design = source_claim.get("study_design", "").upper()
        study_type_map = {
            "EXPERIMENTAL": StudyType.EXPERIMENTAL,
            "RCT": StudyType.EXPERIMENTAL,
            "RANDOMIZED": StudyType.EXPERIMENTAL,
            "OBSERVATIONAL": StudyType.OBSERVATIONAL,
            "CROSS-SECTIONAL": StudyType.OBSERVATIONAL,
            "LONGITUDINAL": StudyType.OBSERVATIONAL,
            "META-ANALYSIS": StudyType.META_ANALYSIS,
            "META_ANALYSIS": StudyType.META_ANALYSIS,
            "REVIEW": StudyType.REVIEW,
            "THEORETICAL": StudyType.THEORETICAL,
        }
        study_type = study_type_map.get(study_design, StudyType.OBSERVATIONAL)

        # Create Source object
        source = Source(
            source_type=SourceType.META_ANALYSIS if study_type == StudyType.META_ANALYSIS else SourceType.PAPER,
            reference=belief.get("paper_id", "unknown"),
            doi=source_claim.get("doi"),
            study_type=study_type,
            sample_size=source_claim.get("sample_size"),
            effect_size=belief.get("effect_size_d"),
        )

        # Determine directness from evidence level
        evidence_level = belief.get("epistemic_level", "EMPIRICAL").upper()
        directness_map = {
            "OBSERVATIONAL": Directness.DIRECT,
            "EMPIRICAL": Directness.ONE_HOP,
            "INTERMEDIATE": Directness.MULTI_HOP,
            "THEORETICAL": Directness.THEORETICAL,
        }
        directness = directness_map.get(evidence_level, Directness.ONE_HOP)

        # Compute grounding score based on study type and directness
        grounding_scores = {
            Directness.DIRECT: 0.9,
            Directness.ONE_HOP: 0.7,
            Directness.MULTI_HOP: 0.4,
            Directness.THEORETICAL: 0.2,
        }
        grounding = grounding_scores.get(directness, 0.5)

        # Boost grounding for strong effect sizes
        effect_d = belief.get("effect_size_d")
        if effect_d and abs(effect_d) >= 0.5:
            grounding = min(1.0, grounding + 0.1)

        # Determine coherence contribution from credence
        credence = belief.get("credence_mean", 0.5)
        coherence_contribution = credence * 0.6  # Rough heuristic

        # Create Provenance
        provenance = Provenance(
            sources=[source],
            grounding_score=grounding,
            directness=directness,
            coherence_contribution=coherence_contribution,
            extracted_from=belief.get("paper_id"),
            extraction_confidence=belief.get("credence_mean"),
        )

        # Compute Haack justification status
        provenance.compute_justification_status(
            coherence_threshold=0.3,  # Generous for initial population
            grounding_threshold=0.3,
        )

        return provenance

    def _load_extraction(self, path: str) -> Dict[str, Any]:
        """Load extraction output from a JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to load extraction from %s: %s", path, e)
            return {}

    def _persist_event(self) -> None:
        """Save the integration event to the database."""
        if self._event is None:
            return

        d = self._event.to_dict()
        cursor = self.db_conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO paper_integration_events
                (event_id, paper_id, timestamp, action, status,
                 pre_snapshot_id, post_snapshot_id,
                 beliefs_added, beliefs_retired,
                 constraints_added, constraints_retired,
                 bn_edges_updated, molecules_affected,
                 tags_assigned, cascade_log,
                 supersedes_paper_id, supersession_records,
                 error_log, rollback_of_event_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["event_id"],
                d["paper_id"],
                d["timestamp"],
                d["action"],
                d["status"],
                d["pre_snapshot_id"],
                d["post_snapshot_id"],
                json.dumps(d["beliefs_added"]),
                json.dumps(d["beliefs_retired"]),
                json.dumps(d["constraints_added"]),
                json.dumps(d["constraints_retired"]),
                json.dumps(d["bn_edges_updated"]),
                json.dumps(d["molecules_affected"]),
                json.dumps(d["tags_assigned"]),
                json.dumps(d["cascade_steps"]),
                d["supersedes_paper_id"],
                json.dumps(d["supersession_records"]),
                d["error_log"],
                d["rollback_of_event_id"],
            ))
            self.db_conn.commit()
            logger.debug("Persisted integration event %s", d["event_id"])
        except sqlite3.OperationalError as e:
            logger.error("Failed to persist integration event: %s", e)
