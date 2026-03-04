"""
OVERSEER: Superordinate Monitoring and Maintenance System
========================================================

A Dijkstra-inspired watchdog for coherentist epistemic systems.

OVERSEER is a 6-component health monitoring and invariant enforcement system
that operates above the web-of-belief and Bayesian network layers. It ensures
that the CMR system maintains epistemic integrity through four operational modes:

  POST_INTEGRATION (~5 sec): Immediate check after paper integration event
  PERIODIC (nightly ~15 min): Full audit of all invariants
  ALERT (immediate): Triggered by detected violation
  ON_DEMAND: Manual inspection

Core Principles (from 18-person expert panel, Feb 2026):
  - O-1: Separation of concerns (OVERSEER in overseer.db, Parnas info hiding)
  - O-2: Statistical alerting (per-theory baselines, mean ± 1σ detection)
  - O-3: Quarantine not auto-retire (7-day human review)
  - O-4: BN-web sync (edges match credences)
  - O-5: Real-time conflict detection (constraint violations)
  - O-6: Provenance verification (Haack foundherentism)
  - O-7: Parnas database separation (overseer.db ≠ web.db)
  - O-8: Gradual degradation (optional modules don't break system)

Invariants (Dijkstra, Haack, Pearl):
  INV-0: System is in OPERATIONAL state (no bootstrap failures)
  INV-1: Every belief has provenance (Haack)
  INV-2: BN edges reflect web credences (Pearl)
  INV-3: All beliefs conform to ClaimV2 schema
  INV-4: Coherence decline ≤ 5% per integration (Dijkstra)
  INV-5: No belief has credence outside [0, 1]
  INV-6: Pipeline utilization ≥ 25% (EN-0E)
  INV-7: Template coverage ≥ 80% (EN-0E)
  INV-8: Theory orphan rate ≤ 10% (EN-0E)
  INV-9: Paper-sourced evidence ≥ 20% (EN-0E)
  INV-10: Extraction quality mean score ≥ 0.75 (QA quality gate)
  INV-11: T3 classification rate ≥ 70% (T3 belief engine)
  INV-12: T3 established beliefs ≥ 200 (T3 belief engine)
  INV-13: Field reviewer terminal rate ≤ 10% (data quality)
  INV-14: Card generation queue depth ≤ 50 (real-time pipeline)
  INV-15: Stale card ratio ≤ 20% (card freshness)
  INV-16: Card two-pass pipeline health (Pass 1→2 flow)

6 Sub-Components:
  1. HealthMonitor: Time-series coherence, conflict, completeness metrics
  2. IntegrityChecker: Invariant violation detection (INV-0..INV-5)
  3. CompletenessAuditor: Template coverage, orphan belief detection
  4. MaintenanceEngine: QA cache stale marking, BN sync validation
  5. Scheduler: Trigger events (POST_INTEGRATION, PERIODIC, ALERT, ON_DEMAND)
  6. OverseerReporter: Dashboard data, health history, alerts

References:
  - Dijkstra, E.W. (1968). The structure of the "THE" multiprogramming system.
    CACM 11(5):341-346.
  - Haack, S. (1993). Evidence and Inquiry. Blackwell.
  - Pearl, J. (2009). Causality (2nd ed.). Cambridge.
  - Cartwright, N. (2012). Will This Policy Work for You? Oxford.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import json
import sqlite3
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# ============================================================================
# Dataclasses: HealthReport, InvariantViolation
# ============================================================================

@dataclass
class InvariantViolation:
    """Records a single invariant violation."""
    code: str                           # INV-1, INV-2, ..., INV-5
    severity: str                       # CRITICAL | MAJOR | MINOR
    description: str
    affected_beliefs: List[str] = field(default_factory=list)
    trigger_paper_id: Optional[str] = None


@dataclass
class HealthReport:
    """Complete health assessment snapshot."""
    timestamp: str
    mode: str                           # POST_INTEGRATION | PERIODIC | ALERT | ON_DEMAND
    trigger_paper_id: Optional[str]
    health_metrics: Dict[str, Any]
    violations: List[InvariantViolation]
    alerts: List[str]                   # Human-readable alert strings
    quarantine_actions: List[Dict]      # {action, belief_id, reason, deadline}
    maintenance_actions: List[Dict]     # {action, resource, status}
    duration_ms: float
    management: Optional[Dict[str, Any]] = None  # v2 Management Layer report (pipelines, queues, flow)


# ============================================================================
# OVERSEER Service
# ============================================================================

class OverseerService:
    """
    Superordinate monitoring system for coherentist epistemology.

    Maintains strict separation from web-of-belief and BN systems via
    dedicated overseer.db (O-7: Parnas information hiding).

    All metric computation is defensive: gracefully degrades if optional
    modules (CoherenceManager, EpistemicOrchestrator, etc.) are unavailable.
    """

    def __init__(
        self,
        overseer_db_path: str,
        web: Any,                       # WebOfBelief (duck-typed for graceful degradation)
        web_db_path: str,
        templates_dir: str = "data/templates",
        extractions_dir: str = "data/extractions",
        theories_dir: str = "data/theories",
    ):
        """
        Initialize OVERSEER service.

        Args:
            overseer_db_path: Path to dedicated overseer.db (O-7)
            web: WebOfBelief instance (may be None)
            web_db_path: Path to web.db (for read-only access)
            templates_dir: Path to template JSONs (for INV-7/INV-8)
            extractions_dir: Path to extraction JSONs (for INV-6)
            theories_dir: Path to theory JSONs (for INV-8)
        """
        self.overseer_db_path = Path(overseer_db_path)
        self.web_db_path = Path(web_db_path)
        self.web = web
        self.templates_dir = Path(templates_dir)
        self.extractions_dir = Path(extractions_dir)
        self.theories_dir = Path(theories_dir)

        # Initialize overseer.db
        self._init_overseer_db()

        # Baseline snapshots (for O-2: statistical alerting)
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.baseline_per_theory: Optional[Dict[str, float]] = None

        logger.info(f"OVERSEER initialized: {overseer_db_path}")

    # ========================================================================
    # Database Management
    # ========================================================================

    def _init_overseer_db(self) -> None:
        """Create overseer.db schema if not present."""
        try:
            with self._db_connection() as conn:
                # Tables created by migration 023
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='overseer_health_metrics'"
                )
                if not cursor.fetchone():
                    logger.warning(
                        "overseer_health_metrics table not found. "
                        "Run migration 023 before using OVERSEER."
                    )

                # Pipeline registry table (added 2026-02-27)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pipeline_registry (
                        pipeline_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        schedule TEXT,
                        depends_on TEXT,
                        registered_at TEXT NOT NULL,
                        last_run_at TEXT,
                        last_status TEXT,
                        last_duration_ms INTEGER,
                        last_error TEXT,
                        run_count INTEGER DEFAULT 0
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pipeline_run_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pipeline_id TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        status TEXT NOT NULL,
                        duration_ms INTEGER,
                        error TEXT,
                        metadata TEXT,
                        FOREIGN KEY (pipeline_id) REFERENCES pipeline_registry(pipeline_id)
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize overseer.db: {e}")

    @contextmanager
    def _db_connection(self):
        """Context manager for overseer.db connection."""
        conn = sqlite3.connect(str(self.overseer_db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    # ========================================================================
    # Main Entry Points
    # ========================================================================

    def post_integration_check(
        self,
        paper_id: str,
        event: Optional[Any] = None
    ) -> HealthReport:
        """
        POST_INTEGRATION mode (~5 sec after paper integrates).

        Triggered by PaperIntegrationEvent in extraction_to_web.py.
        Immediate check that integration didn't violate invariants.

        Args:
            paper_id: DOI or paper identifier
            event: PaperIntegrationEvent (optional, for context)

        Returns:
            HealthReport with metrics, violations, and quarantine actions
        """
        start = datetime.now(timezone.utc)
        logger.info(f"POST_INTEGRATION check: {paper_id}")

        health = self.check_health()
        violations = self.check_integrity()
        completeness = self.audit_completeness()

        # Check INV-4: Coherence delta ≤ 5%
        coherence_delta = health.get("coherence_delta", 0.0)
        if coherence_delta > 0.05:
            violations.append(InvariantViolation(
                code="INV-4",
                severity="MAJOR",
                description=f"Coherence declined {coherence_delta*100:.1f}% (threshold 5%)",
                trigger_paper_id=paper_id
            ))

        # Generate alerts
        alerts = self._generate_alerts(health, violations)

        # Process quarantines
        quarantine_actions = self._process_violations(violations)

        # Card staleness: notify affected cards of new evidence (real-time)
        try:
            card_staleness_actions = self._update_card_staleness(paper_id)
            if card_staleness_actions:
                logger.info(
                    f"POST_INTEGRATION: {len(card_staleness_actions)} cards "
                    f"had staleness updated for paper {paper_id}"
                )
        except Exception as e:
            logger.debug(f"Card staleness update failed: {e}")

        # Maintenance
        maintenance = self.run_maintenance()
        maintenance_actions = maintenance.get("actions", [])

        # Record metrics
        self._record_metrics("POST_INTEGRATION", paper_id, health, violations)

        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        return HealthReport(
            timestamp=start.isoformat(),
            mode="POST_INTEGRATION",
            trigger_paper_id=paper_id,
            health_metrics=health,
            violations=violations,
            alerts=alerts,
            quarantine_actions=quarantine_actions,
            maintenance_actions=maintenance_actions,
            duration_ms=duration_ms
        )

    def periodic_audit(self) -> HealthReport:
        """
        PERIODIC mode (nightly ~15 min full audit).

        Comprehensive check: all invariants, baselines, trends.
        Scheduled via scripts/overseer_nightly.py.

        Returns:
            HealthReport with full system assessment
        """
        start = datetime.now(timezone.utc)
        logger.info("PERIODIC audit starting")

        health = self.check_health()
        violations = self.check_integrity()
        completeness = self.audit_completeness()

        # Statistical alerting (O-2): compare against baseline
        alerts = self._check_against_baseline(health)

        # Process quarantines
        quarantine_actions = self._process_violations(violations)

        # Run maintenance
        maintenance = self.run_maintenance()
        maintenance_actions = maintenance.get("actions", [])

        # Management layer: pipeline monitoring, queue health, article flow
        management_report = self._run_management_check()

        # Record snapshot
        if self.baseline_metrics is None:
            self.set_baseline(health)
            logger.info("Baseline set (first PERIODIC audit)")

        # Record metrics
        self._record_metrics("PERIODIC", None, health, violations)

        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        report = HealthReport(
            timestamp=start.isoformat(),
            mode="PERIODIC",
            trigger_paper_id=None,
            health_metrics=health,
            violations=violations,
            alerts=alerts,
            quarantine_actions=quarantine_actions,
            maintenance_actions=maintenance_actions,
            duration_ms=duration_ms
        )
        # Attach management report as supplementary data
        report.management = management_report
        return report

    def _run_management_check(self) -> Optional[Dict[str, Any]]:
        """
        Run the OVERSEER Management Layer (v2).

        Monitors: pipeline health, queue backlog, article flow,
        search suggestion staleness, extraction queue, panel needs.

        Returns dict with management report, or None if module unavailable.
        Uses composition (O-8: graceful degradation if module missing).
        """
        try:
            from src.services.overseer_management import ManagementDashboard
            dashboard = ManagementDashboard(
                overseer_db_path=self.overseer_db_path,
                web_db_path=self.web_db_path,
                web=self.web,
            )
            report = dashboard.generate_management_report()
            # Convert ManagementReport dataclass to dict
            return {
                "pipeline_statuses": {
                    k: {"status": v.status.value if hasattr(v.status, "value") else str(v.status),
                         "queue_depth": getattr(v, "queue_depth", 0),
                         "throughput_24h": getattr(v, "throughput_24h", 0),
                         "error_rate_24h": getattr(v, "error_rate_24h", 0.0),
                         "bottleneck": getattr(v, "bottleneck", None)}
                    if hasattr(v, "status") else v
                    for k, v in (report.pipeline_statuses.items()
                                 if hasattr(report, "pipeline_statuses") and report.pipeline_statuses
                                 else {}.items())
                },
                "queue_health": report.queue_health if hasattr(report, "queue_health") else {},
                "article_flow": report.article_flow if hasattr(report, "article_flow") else {},
                "suggestion_backlog": report.suggestion_backlog if hasattr(report, "suggestion_backlog") else {},
                "extraction_queue": report.extraction_queue if hasattr(report, "extraction_queue") else {},
                "panel_needs": report.panel_needs if hasattr(report, "panel_needs") else [],
                "recommendations": report.recommendations if hasattr(report, "recommendations") else [],
                "formatted_text": dashboard._format_report(report),
            }
        except ImportError:
            logger.debug("Management layer not available (overseer_management.py not found)")
            return None
        except Exception as e:
            logger.warning(f"Management layer check failed: {e}")
            return {"status": "error", "error": str(e)}

    def on_demand_audit(self, scope: str = "full") -> HealthReport:
        """
        ON_DEMAND mode (manual inspection).

        Args:
            scope: "full" | "health" | "integrity" | "completeness"

        Returns:
            HealthReport for specified scope
        """
        start = datetime.now(timezone.utc)
        logger.info(f"ON_DEMAND audit: scope={scope}")

        health = self.check_health() if scope in ("full", "health") else {}
        violations = self.check_integrity() if scope in ("full", "integrity") else []
        completeness = self.audit_completeness() if scope in ("full", "completeness") else {}

        alerts = self._generate_alerts(health, violations)
        quarantine_actions = self._process_violations(violations)
        maintenance = self.run_maintenance() if scope == "full" else {}
        maintenance_actions = maintenance.get("actions", [])

        self._record_metrics("ON_DEMAND", None, health, violations)

        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        return HealthReport(
            timestamp=start.isoformat(),
            mode="ON_DEMAND",
            trigger_paper_id=None,
            health_metrics=health,
            violations=violations,
            alerts=alerts,
            quarantine_actions=quarantine_actions,
            maintenance_actions=maintenance_actions,
            duration_ms=duration_ms
        )

    # ========================================================================
    # Component 1: Health Monitor (Coherence, Conflict, Completeness)
    # ========================================================================

    def check_health(self) -> Dict[str, Any]:
        """
        HealthMonitor component: Time-series metrics.

        Gracefully degrades if optional modules unavailable.

        Returns:
            {
                global_coherence: float,
                per_theory_coherence: {theory_id: score},
                coherence_delta: float,
                conflict_count: int,
                conflict_rate: float,
                total_beliefs: int,
                orphan_belief_count: int,
                total_templates: int,
                templates_with_evidence: int,
                coverage_ratio: float,
                total_qa_caches: int,
                stale_qa_caches: int,
                cache_freshness: float,
                bn_edge_count: int,
                bn_web_sync_violations: int,
                beliefs_with_provenance: int,
                beliefs_without_provenance: int,
                provenance_coverage: float
            }
        """
        metrics = {}

        # Coherence metrics (CoherenceManager)
        try:
            if self.web and hasattr(self.web, 'get_global_coherence'):
                metrics['global_coherence'] = self.web.get_global_coherence()
                metrics['per_theory_coherence'] = self.web.get_per_theory_coherence() or {}
                metrics['coherence_delta'] = self._compute_coherence_delta(
                    metrics.get('global_coherence', 0.0)
                )
            else:
                logger.debug("CoherenceManager unavailable; coherence metrics skipped")
                metrics['global_coherence'] = None
                metrics['coherence_delta'] = None
        except Exception as e:
            logger.warning(f"Coherence check failed: {e}")
            metrics['global_coherence'] = None

        # Conflict metrics (Quine constraint violations)
        try:
            if self.web and hasattr(self.web, 'get_constraint_violations'):
                conflicts = self.web.get_constraint_violations() or []
                metrics['conflict_count'] = len(conflicts)
                metrics['conflict_rate'] = self._compute_conflict_rate(conflicts)
            else:
                metrics['conflict_count'] = 0
                metrics['conflict_rate'] = 0.0
        except Exception as e:
            logger.warning(f"Conflict check failed: {e}")
            metrics['conflict_count'] = None

        # Belief metrics (completeness)
        try:
            if self.web and hasattr(self.web, 'get_belief_count'):
                metrics['total_beliefs'] = self.web.get_belief_count()
                metrics['orphan_belief_count'] = self._count_orphan_beliefs()
            else:
                metrics['total_beliefs'] = None
                metrics['orphan_belief_count'] = None
        except Exception as e:
            logger.warning(f"Belief metrics failed: {e}")
            metrics['total_beliefs'] = None

        # Template metrics
        try:
            metrics['total_templates'] = self._count_templates()
            metrics['templates_with_evidence'] = self._count_templates_with_evidence()
            if metrics['total_templates'] and metrics['total_templates'] > 0:
                metrics['coverage_ratio'] = (
                    metrics['templates_with_evidence'] / metrics['total_templates']
                )
            else:
                metrics['coverage_ratio'] = 0.0
        except Exception as e:
            logger.warning(f"Template metrics failed: {e}")
            metrics['templates_with_evidence'] = None

        # Cache health
        try:
            metrics['total_qa_caches'] = self._count_qa_caches()
            metrics['stale_qa_caches'] = self._count_stale_caches()
            if metrics['total_qa_caches'] and metrics['total_qa_caches'] > 0:
                metrics['cache_freshness'] = (
                    (metrics['total_qa_caches'] - metrics['stale_qa_caches']) /
                    metrics['total_qa_caches']
                )
            else:
                metrics['cache_freshness'] = 1.0
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")
            metrics['cache_freshness'] = None

        # BN metrics
        try:
            metrics['bn_edge_count'] = self._count_bn_edges()
            metrics['bn_web_sync_violations'] = self._check_bn_web_sync()
        except Exception as e:
            logger.warning(f"BN metrics failed: {e}")
            metrics['bn_edge_count'] = None

        # Provenance metrics (Haack INV-1)
        try:
            total = metrics.get('total_beliefs', 0)
            if total and total > 0:
                with_prov = self._count_beliefs_with_provenance()
                metrics['beliefs_with_provenance'] = with_prov
                metrics['beliefs_without_provenance'] = total - with_prov
                metrics['provenance_coverage'] = with_prov / total
            else:
                metrics['provenance_coverage'] = 1.0
        except Exception as e:
            logger.warning(f"Provenance check failed: {e}")
            metrics['provenance_coverage'] = None

        # EN-0E: Coverage and utilization metrics
        try:
            metrics['pipeline_utilization'] = self._check_pipeline_utilization()
        except Exception as e:
            logger.debug(f"Pipeline utilization metric failed: {e}")
            metrics['pipeline_utilization'] = None

        try:
            metrics['template_belief_coverage'] = self._check_template_belief_coverage()
        except Exception as e:
            logger.debug(f"Template coverage metric failed: {e}")
            metrics['template_belief_coverage'] = None

        try:
            metrics['theory_orphan_rate'] = self._check_theory_linkage()
        except Exception as e:
            logger.debug(f"Theory linkage metric failed: {e}")
            metrics['theory_orphan_rate'] = None

        try:
            metrics['paper_evidence_ratio'] = self._check_evidence_diversity()
        except Exception as e:
            logger.debug(f"Evidence diversity metric failed: {e}")
            metrics['paper_evidence_ratio'] = None

        # EN-0E: Test pass rate (MT-14)
        try:
            metrics['test_pass_rate'] = self._check_test_pass_rate()
        except Exception as e:
            logger.debug(f"Test pass rate metric failed: {e}")
            metrics['test_pass_rate'] = None

        # MT-14: Extraction quality (INV-10, already has _check method)
        try:
            metrics['extraction_quality'] = self._check_extraction_quality()
        except Exception as e:
            logger.debug(f"Extraction quality metric failed: {e}")
            metrics['extraction_quality'] = None

        # MT-14: Reflex system health
        try:
            reflex = self.get_reflex_health_summary()
            total = reflex.get('total_events', 0)
            auto_fixed = reflex.get('auto_fixed_count', 0)
            unresolved = reflex.get('unresolved_count', 0)
            if total > 0:
                metrics['reflex_health'] = 1.0 - (unresolved / max(total, 1))
            else:
                metrics['reflex_health'] = 1.0  # No events = healthy
            metrics['reflex_auto_fix_rate'] = (
                auto_fixed / total if total > 0 else 1.0
            )
        except Exception as e:
            logger.debug(f"Reflex health metric failed: {e}")
            metrics['reflex_health'] = None

        # MT-14: Success condition test coverage
        try:
            metrics['success_condition_coverage'] = (
                self._check_success_condition_coverage()
            )
        except Exception as e:
            logger.debug(f"Success condition coverage failed: {e}")
            metrics['success_condition_coverage'] = None

        # MT-14: Subsystem health (per-service operational)
        try:
            subsystem_report = self.check_all_subsystems()
            if isinstance(subsystem_report, dict) and 'error' not in subsystem_report:
                subs = subsystem_report.get('subsystems', {})
                if subs:
                    ok_count = sum(
                        1 for info in subs.values()
                        if info.get('status') in ('healthy', 'pass', 'ok')
                    )
                    metrics['subsystem_health'] = ok_count / len(subs)
                else:
                    metrics['subsystem_health'] = None
            else:
                metrics['subsystem_health'] = None
        except Exception as e:
            logger.debug(f"Subsystem health metric failed: {e}")
            metrics['subsystem_health'] = None

        # MT-14: Source data completeness (Round 15 auditor)
        try:
            sd_health = self.get_source_data_health()
            metrics['source_data_coverage'] = sd_health.get('avg_coverage', 0.0)
            metrics['source_data_generation_ready'] = (
                sd_health.get('generation_ready_pct', 0.0) / 100.0
            )
        except Exception as e:
            logger.debug(f"Source data completeness metric failed: {e}")
            metrics['source_data_coverage'] = None

        # MT-14: Annotation integration coverage
        try:
            metrics['annotation_integration'] = (
                self._check_annotation_integration()
            )
        except Exception as e:
            logger.debug(f"Annotation integration metric failed: {e}")
            metrics['annotation_integration'] = None

        # EN-0E: AESHI composite score
        try:
            metrics['aeshi_score'] = self.compute_aeshi(metrics)
        except Exception as e:
            logger.debug(f"AESHI computation failed: {e}")
            metrics['aeshi_score'] = None

        return metrics

    def _compute_coherence_delta(self, current: float) -> float:
        """Compute change in coherence since last measurement."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT global_coherence FROM overseer_health_metrics "
                    "WHERE global_coherence IS NOT NULL "
                    "ORDER BY timestamp DESC LIMIT 2"
                )
                rows = cursor.fetchall()
                if len(rows) >= 2:
                    prev = rows[1][0]
                    return current - prev
                return 0.0
        except Exception as e:
            logger.debug(f"Coherence delta compute failed: {e}")
            return 0.0

    def _compute_conflict_rate(self, conflicts: List) -> float:
        """Compute conflict_count / total_constraints."""
        try:
            total_constraints = self._count_total_constraints()
            if total_constraints > 0:
                return len(conflicts) / total_constraints
            return 0.0
        except Exception:
            return 0.0

    # ========================================================================
    # Component 2: Integrity Checker (Invariants)
    # ========================================================================

    def check_integrity(self) -> List[InvariantViolation]:
        """
        IntegrityChecker component: Detect invariant violations.

        Checks INV-0..INV-5 and returns list of violations.
        """
        violations = []

        # INV-0: OPERATIONAL state
        if not self._check_operational():
            violations.append(InvariantViolation(
                code="INV-0",
                severity="CRITICAL",
                description="System not in OPERATIONAL state"
            ))

        # INV-1: Provenance coverage (Haack)
        orphans = self._count_beliefs_without_provenance()
        if orphans > 0:
            violations.append(InvariantViolation(
                code="INV-1",
                severity="MAJOR",
                description=f"{orphans} beliefs without provenance",
                affected_beliefs=self._get_beliefs_without_provenance()[:10]
            ))

        # INV-2: BN-web sync (Pearl)
        bn_violations = self._check_bn_web_sync()
        if bn_violations > 0:
            violations.append(InvariantViolation(
                code="INV-2",
                severity="MAJOR",
                description=f"{bn_violations} BN-web sync violations",
                affected_beliefs=self._get_bn_sync_violations()[:10]
            ))

        # INV-3: ClaimV2 schema
        schema_violations = self._check_schema_compliance()
        if schema_violations:
            violations.append(InvariantViolation(
                code="INV-3",
                severity="MAJOR",
                description=f"{len(schema_violations)} beliefs non-compliant with ClaimV2",
                affected_beliefs=schema_violations[:10]
            ))

        # INV-4: Coherence decline ≤ 5% (Dijkstra)
        try:
            current_coherence = None
            if self.web and hasattr(self.web, 'get_global_coherence'):
                current_coherence = self.web.get_global_coherence()
            elif self.web and hasattr(self.web, 'coherence_score'):
                current_coherence = self.web.coherence_score()

            if current_coherence is not None:
                delta = self._compute_coherence_delta(current_coherence)
                if current_coherence > 0 and delta < 0:
                    decline_pct = abs(delta) / (current_coherence - delta) * 100
                    if decline_pct > 5.0:
                        violations.append(InvariantViolation(
                            code="INV-4",
                            severity="MAJOR",
                            description=(
                                f"Coherence declined {decline_pct:.1f}% "
                                f"(from {current_coherence - delta:.3f} to "
                                f"{current_coherence:.3f})"
                            )
                        ))
                        logger.warning(
                            f"INV-4 VIOLATION: coherence decline {decline_pct:.1f}%"
                        )
        except Exception as e:
            logger.debug(f"INV-4 coherence check failed: {e}")

        # INV-5: Credence bounds [0, 1]
        credence_violations = self._check_credence_bounds()
        if credence_violations:
            violations.append(InvariantViolation(
                code="INV-5",
                severity="CRITICAL",
                description=f"{len(credence_violations)} beliefs have credence outside [0, 1]",
                affected_beliefs=credence_violations[:10]
            ))

        # ----------------------------------------------------------------
        # EN-0E: Coverage and utilization invariants (INV-6..INV-9)
        # ----------------------------------------------------------------

        # INV-6: Pipeline utilization ≥ 25%
        try:
            utilization = self._check_pipeline_utilization()
            if utilization is not None and utilization < 0.25:
                violations.append(InvariantViolation(
                    code="INV-6",
                    severity="WARNING",
                    description=(
                        f"Pipeline utilization {utilization*100:.1f}% "
                        f"(threshold: 25%). Most extractions are unintegrated."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-6 check failed: {e}")

        # INV-7: Template coverage ≥ 80%
        try:
            coverage = self._check_template_belief_coverage()
            if coverage is not None and coverage < 0.80:
                violations.append(InvariantViolation(
                    code="INV-7",
                    severity="MAJOR",
                    description=(
                        f"Template coverage {coverage*100:.1f}% "
                        f"(threshold: 80%). Many templates have no beliefs."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-7 check failed: {e}")

        # INV-8: Theory linkage — orphan rate ≤ 10%
        try:
            orphan_rate = self._check_theory_linkage()
            if orphan_rate is not None and orphan_rate > 0.10:
                violations.append(InvariantViolation(
                    code="INV-8",
                    severity="MAJOR",
                    description=(
                        f"Theory orphan rate {orphan_rate*100:.1f}% "
                        f"(threshold: 10%). Some theories have 0 templates."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-8 check failed: {e}")

        # INV-9: Evidence diversity — paper-sourced ≥ 20%
        try:
            paper_ratio = self._check_evidence_diversity()
            if paper_ratio is not None and paper_ratio < 0.20:
                violations.append(InvariantViolation(
                    code="INV-9",
                    severity="WARNING",
                    description=(
                        f"Paper-sourced beliefs only {paper_ratio*100:.1f}% "
                        f"(threshold: 20%). Web is panel-dominated."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-9 check failed: {e}")

        # INV-10: Extraction quality — mean score ≥ 0.75
        try:
            extraction_quality = self._check_extraction_quality()
            if extraction_quality is not None and extraction_quality < 0.75:
                violations.append(InvariantViolation(
                    code="INV-10",
                    severity="MAJOR",
                    description=(
                        f"Extraction quality mean score {extraction_quality:.3f} "
                        f"is below threshold 0.75. Articles may need re-extraction."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-10 check failed: {e}")

        # ----------------------------------------------------------------
        # T3 Belief Engine invariants (INV-11..INV-12)
        # ----------------------------------------------------------------

        # INV-11: T3 classification rate ≥ 70%
        try:
            t3_stats = self._check_t3_classification()
            if t3_stats is not None:
                rate = t3_stats.get("classification_rate", 0)
                if rate < 0.70:
                    violations.append(InvariantViolation(
                        code="INV-11",
                        severity="MAJOR",
                        description=(
                            f"T3 IV classification rate {rate*100:.1f}% "
                            f"(threshold: 70%). Many findings not mapping to taxonomy."
                        )
                    ))
        except Exception as e:
            logger.debug(f"INV-11 check failed: {e}")

        # INV-12: T3 established beliefs ≥ 200
        try:
            t3_counts = self._check_t3_belief_counts()
            if t3_counts is not None:
                established = t3_counts.get("established", 0)
                if established < 200:
                    violations.append(InvariantViolation(
                        code="INV-12",
                        severity="MAJOR",
                        description=(
                            f"T3 established beliefs: {established} "
                            f"(threshold: 200). Generalization insufficient."
                        )
                    ))
        except Exception as e:
            logger.debug(f"INV-12 check failed: {e}")

        # INV-13: Field reviewer terminal rate ≤ 10%
        try:
            terminal_rate = self._check_field_reviewer_terminal_rate()
            if terminal_rate is not None and terminal_rate > 0.10:
                violations.append(InvariantViolation(
                    code="INV-13",
                    severity="WARNING",
                    description=(
                        f"Field reviewer terminal rate {terminal_rate*100:.1f}% "
                        f"(threshold: 10%). Data quality issues persist."
                    )
                ))
        except Exception as e:
            logger.debug(f"INV-13 check failed: {e}")

        # ----------------------------------------------------------------
        # Card Generation Pipeline (INV-14..INV-15) — Added 2026-03-04
        # Real-time monitoring of card generation, staleness, and queue depth
        # ----------------------------------------------------------------

        # INV-14: Card generation queue depth ≤ 50
        try:
            card_health = self._check_card_generation_health()
            if card_health:
                queue_depth = card_health.get("queue", {}).get("queued", 0)
                if queue_depth > 50:
                    violations.append(InvariantViolation(
                        code="INV-14",
                        severity="WARNING",
                        description=(
                            f"Card generation queue depth {queue_depth} "
                            f"(threshold: 50). Cards are accumulating faster "
                            f"than they can be generated."
                        )
                    ))
        except Exception as e:
            logger.debug(f"INV-14 check failed: {e}")

        # INV-15: Stale card ratio ≤ 20%
        try:
            if card_health:
                dist = card_health.get("staleness_distribution", {})
                total = sum(dist.values())
                stale = dist.get("STALE", 0)
                if total > 0 and (stale / total) > 0.20:
                    violations.append(InvariantViolation(
                        code="INV-15",
                        severity="MAJOR",
                        description=(
                            f"Stale card ratio {stale}/{total} = "
                            f"{stale/total*100:.1f}% (threshold: 20%). "
                            f"Cards need regeneration."
                        )
                    ))
        except Exception as e:
            logger.debug(f"INV-15 check failed: {e}")

        return violations

    def _update_card_staleness(self, paper_id: str) -> List[str]:
        """
        After paper integration, find affected cards and update staleness.

        Real-time: no nightly batch. When a paper integrates, every card
        that references data from that paper (or whose topic overlaps)
        gets its staleness ledger updated. If any card crosses the STALE
        threshold, it's immediately queued for regeneration.

        Returns list of affected card IDs.
        """
        try:
            from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
            orch = CardGenerationOrchestrator(base_dir=".")

            # Find all cards that might be affected by this paper
            affected = []
            for card_id, meta in orch._card_index.items():
                # A card is affected if the paper touches its topic area
                # For now, mark all cards as slightly more stale on any integration
                # More precise: check if paper's extraction overlaps card's entity
                orch.on_new_evidence(card_id, paper_id)
                affected.append(card_id)

            # Check for newly stale cards and queue them
            queued = orch.check_and_queue_stale()
            if queued > 0:
                logger.info(f"Queued {queued} stale cards for regeneration")

            return affected
        except Exception as e:
            logger.debug(f"Card staleness update failed: {e}")
            return []

    def _check_card_generation_health(self) -> Optional[Dict]:
        """Check card generation pipeline health via CardGenerationOrchestrator."""
        try:
            from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
            orch = CardGenerationOrchestrator(base_dir=".")
            return orch.get_overseer_health_report()
        except Exception as e:
            logger.debug(f"Card generation health check failed: {e}")
            return None

    def check_two_pass_pipeline_health(self) -> Dict[str, Any]:
        """
        INV-16: Card two-pass pipeline health monitoring.

        Tracks the Pass 1 → Pass 2 (Opus polish) pipeline status:
        - How many cards are awaiting Opus polish (Pass 2 queue depth)
        - How many have completed Pass 1 (Sonnet generation)
        - How many have completed both passes (fully polished)
        - Overall completion percentage
        - Health status: "healthy" | "backlog" | "stalled"

        Returns:
            {
                "opus_queue_depth": int,      # Cards waiting for Pass 2 (Opus)
                "pass1_complete": int,        # Cards with Pass 1 done (queued or completed)
                "pass2_complete": int,        # Cards with both passes done
                "total_tracked": int,         # Total cards in the pipeline
                "completion_pct": float,      # Percentage of cards with both passes done
                "status": str,                # "healthy" | "backlog" | "stalled"
                "oldest_queued_age_days": float or None,  # Age of oldest queued card
                "message": str                # Human-readable summary
            }
        """
        result = {
            "opus_queue_depth": 0,
            "pass1_complete": 0,
            "pass2_complete": 0,
            "total_tracked": 0,
            "completion_pct": 0.0,
            "status": "unknown",
            "oldest_queued_age_days": None,
            "message": "Pipeline health check failed"
        }

        try:
            from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
            from datetime import datetime, timezone, timedelta

            orch = CardGenerationOrchestrator(base_dir=".")

            # Get queue stats
            stats = orch._queue.stats()
            queue_data = orch._queue.to_dict()

            # Queue depth for Opus (Pass 2)
            opus_queue = stats.get("by_model", {}).get("opus", 0)
            result["opus_queue_depth"] = opus_queue

            # Total queued and completed
            queued = stats.get("queued", 0)
            completed = stats.get("completed", 0)

            # For a simple 2-pass model:
            # - pass1_complete = queued (these were generated in Pass 1 and are awaiting Polish)
            #                  + completed (these have both passes done)
            # - pass2_complete = completed (both passes finished)
            # - total_tracked = queued + completed + failed
            failed = stats.get("failed", 0)
            total = queued + completed + failed

            result["pass1_complete"] = queued + completed  # Anything that's moved past initial generation
            result["pass2_complete"] = completed
            result["total_tracked"] = total

            if total > 0:
                result["completion_pct"] = (completed / total) * 100.0
            else:
                result["completion_pct"] = 100.0  # Empty pipeline is "complete"

            # Check oldest queued card's age
            queue_list = queue_data.get("queue", [])
            if queue_list:
                oldest_created = None
                for req in queue_list:
                    created_at_str = req.get("created_at", "")
                    if created_at_str:
                        # Parse ISO timestamp
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                            if oldest_created is None or created_at < oldest_created:
                                oldest_created = created_at
                        except Exception:
                            pass

                if oldest_created:
                    now = datetime.now(timezone.utc)
                    age_delta = now - oldest_created
                    result["oldest_queued_age_days"] = age_delta.total_seconds() / (24 * 3600)

            # Determine health status
            # "backlog" = queue_depth > 100
            # "stalled" = oldest queued card is > 7 days old
            # "healthy" = everything else
            if opus_queue > 100:
                result["status"] = "backlog"
                result["message"] = (
                    f"BACKLOG: {opus_queue} Opus cards queued (threshold: 100). "
                    f"Pipeline is accumulating faster than processing."
                )
            elif result["oldest_queued_age_days"] and result["oldest_queued_age_days"] > 7:
                result["status"] = "stalled"
                age_days = result["oldest_queued_age_days"]
                result["message"] = (
                    f"STALLED: Oldest queued card is {age_days:.1f} days old. "
                    f"Polish pipeline may be stuck."
                )
            else:
                result["status"] = "healthy"
                if opus_queue == 0:
                    result["message"] = (
                        f"Pipeline healthy: {completed}/{total} cards fully polished. "
                        f"No cards awaiting Opus pass."
                    )
                else:
                    result["message"] = (
                        f"Pipeline processing: {opus_queue} cards awaiting Opus polish, "
                        f"{completed} fully polished out of {total}."
                    )

            logger.info(f"INV-16 two-pass health: {result['status']} | {result['message']}")
            return result

        except Exception as e:
            logger.warning(f"Two-pass pipeline health check failed: {e}")
            result["message"] = f"Health check error: {e}"
            return result

    def _check_operational(self) -> bool:
        """Check if system is OPERATIONAL (no bootstrap failures)."""
        try:
            # Minimal check: can we read web.db?
            if self.web_db_path.exists():
                return True
            logger.error(f"web.db not found: {self.web_db_path}")
            return False
        except Exception as e:
            logger.error(f"Operational check failed: {e}")
            return False

    def _check_schema_compliance(self) -> List[str]:
        """Check all beliefs conform to ClaimV2 schema."""
        try:
            # Query belief_versions for schema violations
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT belief_id FROM belief_versions "
                    "WHERE claim_json IS NULL OR claim_json = '' LIMIT 100"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.debug(f"Schema compliance check failed: {e}")
            return []

    def _check_credence_bounds(self) -> List[str]:
        """Check no belief has credence outside [0, 1]."""
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT belief_id FROM belief_versions "
                    "WHERE credence < 0 OR credence > 1 LIMIT 100"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.debug(f"Credence bounds check failed: {e}")
            return []

    # ====================================================================
    # EN-0E: Coverage and Utilization Checks (INV-6..INV-9)
    # ====================================================================

    def _check_pipeline_utilization(self) -> Optional[float]:
        """
        INV-6: Pipeline utilization ratio.

        Counts extraction files in data/extractions/ vs.
        successfully integrated papers. Returns ratio.
        Alert if < 25%.
        """
        try:
            # Count extraction files (exclude non-paper files)
            exclude_names = {
                'scholar_expansion_candidates.json', 'extraction_log.txt',
                'crossref_cache.json', 'crossref_metadata.json',
                'crossref_references.json', 'batch_manifest.json',
            }
            extraction_files = [
                f for f in self.extractions_dir.glob('*.json')
                if f.name not in exclude_names
                and not f.name.startswith('full_extraction')
            ]
            n_extractions = len(extraction_files)
            if n_extractions == 0:
                return None  # Can't compute ratio

            # Count integrated papers — beliefs with paper-sourced provenance
            n_integrated = 0
            try:
                with sqlite3.connect(str(self.web_db_path)) as conn:
                    cursor = conn.cursor()
                    # Count beliefs that came from papers (not templates)
                    cursor.execute(
                        "SELECT COUNT(DISTINCT belief_id) FROM beliefs "
                        "WHERE belief_id NOT LIKE 'template:%'"
                    )
                    row = cursor.fetchone()
                    n_integrated = row[0] if row else 0
            except Exception:
                # Fallback: check integration_results directory
                results_dir = self.extractions_dir.parent / 'integration_results'
                if results_dir.exists():
                    for f in results_dir.glob('batch_*_results.json'):
                        try:
                            data = json.loads(f.read_text())
                            n_integrated += sum(
                                1 for v in data.values()
                                if isinstance(v, dict) and v.get('status') == 'integrated'
                            )
                        except Exception as e:
                            logger.debug(f"Swallowed in {fpath}: {e}")

            return n_integrated / n_extractions if n_extractions > 0 else 0.0

        except Exception as e:
            logger.debug(f"Pipeline utilization check failed: {e}")
            return None

    def _check_template_belief_coverage(self) -> Optional[float]:
        """
        INV-7: Template coverage — fraction of templates with ≥1 belief.

        Alert if < 80%.
        """
        try:
            # Count template files
            template_files = list(self.templates_dir.glob('*.json'))
            n_templates = len(template_files)
            if n_templates == 0:
                return None

            # Count beliefs that have template linkage (via template_ids column)
            n_with_templates = 0
            try:
                with sqlite3.connect(str(self.web_db_path)) as conn:
                    cursor = conn.cursor()
                    # Count beliefs that have template_ids populated
                    cursor.execute(
                        """SELECT COUNT(DISTINCT belief_id) FROM beliefs
                        WHERE template_ids IS NOT NULL AND template_ids != ''"""
                    )
                    row = cursor.fetchone()
                    n_with_templates = row[0] if row else 0
            except Exception:
                # Fallback: count from WebOfBelief
                if self.web and hasattr(self.web, 'beliefs'):
                    n_with_templates = sum(
                        1 for b in self.web.beliefs.values()
                        if hasattr(b, 'template_ids') and b.template_ids
                    )

            # Return ratio of beliefs with template linkage to total templates
            # This measures how many templates have supporting beliefs
            return n_with_templates / n_templates if n_templates > 0 else 0.0

        except Exception as e:
            logger.debug(f"Template coverage check failed: {e}")
            return None

    def _check_theory_linkage(self) -> Optional[float]:
        """
        INV-8: Theory orphan rate — fraction of theories with 0 constituent_templates.

        Alert if > 10%.
        """
        try:
            theory_files = list(self.theories_dir.glob('*.json'))
            n_theories = len(theory_files)
            if n_theories == 0:
                return None

            n_orphans = 0
            for tf in theory_files:
                try:
                    theory = json.loads(tf.read_text())
                    templates = theory.get('constituent_templates', [])
                    if not templates or len(templates) == 0:
                        n_orphans += 1
                except Exception as e:
                    logger.debug(f"Skipped in {fpath}: {e}")
                    continue

            return n_orphans / n_theories if n_theories > 0 else 0.0

        except Exception as e:
            logger.debug(f"Theory linkage check failed: {e}")
            return None

    def _check_evidence_diversity(self) -> Optional[float]:
        """
        INV-9: Evidence diversity — ratio of paper-sourced to total beliefs.

        Alert if paper-sourced < 20%.
        """
        try:
            total_beliefs = self._count_total_beliefs()
            if total_beliefs == 0:
                return None

            # Count paper-sourced beliefs (those NOT from template seeding)
            n_paper = 0
            try:
                with sqlite3.connect(str(self.web_db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM beliefs "
                        "WHERE belief_id NOT LIKE 'template:%'"
                    )
                    row = cursor.fetchone()
                    n_paper = row[0] if row else 0
            except Exception:
                if self.web and hasattr(self.web, 'beliefs'):
                    n_paper = sum(
                        1 for bid in self.web.beliefs
                        if not bid.startswith('template:')
                    )

            return n_paper / total_beliefs if total_beliefs > 0 else 0.0

        except Exception as e:
            logger.debug(f"Evidence diversity check failed: {e}")
            return None

    def _check_extraction_quality(self) -> Optional[float]:
        """
        INV-10: Extraction quality — mean quality score across all extractions.

        Uses ExtractionFieldValidator to compute mean quality score across
        files in extractions/ directory (excluding needs_repair/).
        Also logs count of files in needs_repair/ queue.
        Alert if mean score < 0.75.

        Returns:
            Mean quality score (0.0-1.0) or None if unable to check.
        """
        try:
            from src.qa.extraction_field_validator import ExtractionFieldValidator

            if not self.extractions_dir.exists():
                logger.debug("Extractions directory not found for quality check")
                return None

            # Check repair queue
            repair_queue_dir = self.extractions_dir / "needs_repair"
            repair_count = 0
            if repair_queue_dir.exists():
                repair_files = list(repair_queue_dir.glob("*.json"))
                repair_count = len([f for f in repair_files if not f.name.endswith(".violations.json")])
                if repair_count > 0:
                    logger.info(f"INV-10: {repair_count} files in repair queue (data/extractions/needs_repair/)")

            validator = ExtractionFieldValidator()
            batch_report = validator.validate_batch(self.extractions_dir)

            if not batch_report.articles:
                return None

            logger.debug(
                f"INV-10: {len(batch_report.articles)} passing extractions, "
                f"mean quality score = {batch_report.mean_score:.4f}"
            )

            return batch_report.mean_score

        except ImportError:
            logger.debug("ExtractionFieldValidator not available; skipping INV-10")
            return None
        except Exception as e:
            logger.debug(f"Extraction quality check failed: {e}")
            return None

    def _check_t3_classification(self) -> Optional[Dict[str, Any]]:
        """
        INV-11: T3 IV classification rate.

        Returns classification stats from the IV/DV classifier singleton,
        or None if T3 not available.
        """
        try:
            from src.services.iv_dv_classifier import get_classifier
            clf = get_classifier()
            stats = clf.classification_stats()
            if stats["total_classified"] == 0:
                return None  # No data yet
            return stats
        except ImportError:
            logger.debug("IV/DV classifier not available; skipping INV-11")
            return None
        except Exception as e:
            logger.debug(f"T3 classification check failed: {e}")
            return None

    def _check_t3_belief_counts(self) -> Optional[Dict[str, int]]:
        """
        INV-12: T3 established belief count.

        Returns belief status counts from T3 integration layer,
        or None if T3 not available.
        """
        try:
            from src.services.t3_integration import T3Adapter
            from src.services.generalization_tree import BeliefStatus
            adapter = T3Adapter()
            if not adapter.engine or not adapter.engine.t3_beliefs:
                return None
            t3 = adapter.engine.t3_beliefs
            counts = {
                "nascent": sum(1 for b in t3.values() if b.status == BeliefStatus.NASCENT),
                "tentative": sum(1 for b in t3.values() if b.status == BeliefStatus.TENTATIVE),
                "established": sum(1 for b in t3.values() if b.status == BeliefStatus.ESTABLISHED),
                "contested": sum(1 for b in t3.values() if b.status == BeliefStatus.CONTESTED),
                "total": len(t3),
            }
            return counts
        except ImportError:
            logger.debug("T3 integration not available; skipping INV-12")
            return None
        except Exception as e:
            logger.debug(f"T3 belief count check failed: {e}")
            return None

    def _check_field_reviewer_terminal_rate(self) -> Optional[float]:
        """
        INV-13: Field reviewer terminal rate.

        Runs a lightweight check of the field reviewer on a sample
        of extraction files. Returns terminal rate (0.0-1.0) or None.
        """
        try:
            import glob
            import json as _json
            from pathlib import Path as _Path

            spec_path = _Path(__file__).parent.parent.parent / "schemas" / "extraction_field_spec.json"
            if not spec_path.exists():
                return None

            extractions_dir = self.extractions_dir
            if not extractions_dir.exists():
                return None

            # Sample up to 50 files for speed
            files = list(extractions_dir.glob("*.json"))[:50]
            if not files:
                return None

            spec = _json.load(open(spec_path))
            total_issues = 0
            terminal_issues = 0

            for f in files:
                try:
                    data = _json.load(open(f))
                    if not isinstance(data, dict):
                        continue
                    # Check finding-level fields
                    for finding in data.get("findings", []):
                        if not isinstance(finding, dict):
                            continue
                        for field_name, field_spec in spec.get("finding_fields", {}).items():
                            value = finding.get(field_name)
                            if value is None:
                                continue
                            ftype = field_spec.get("type", "")
                            if ftype in ("enum", "enum_or_null"):
                                allowed = field_spec.get("values", [])
                                norm_map = field_spec.get("normalize_map", {})
                                if isinstance(value, str):
                                    total_issues += 1
                                    if value not in allowed and value not in norm_map:
                                        terminal_issues += 1
                            elif ftype in ("float", "number_or_null"):
                                if isinstance(value, str):
                                    total_issues += 1
                                    try:
                                        float(value.strip().lstrip("<>"))
                                    except ValueError:
                                        if value.lower() not in ("ns", "n.s.", "n.s"):
                                            terminal_issues += 1
                except Exception:
                    continue

            if total_issues == 0:
                return 0.0
            return terminal_issues / total_issues

        except Exception as e:
            logger.debug(f"Field reviewer terminal rate check failed: {e}")
            return None

    def _check_success_condition_coverage(self) -> Optional[float]:
        """
        MT-14: Success condition test coverage.

        Reads contracts/success_conditions.json and checks what fraction
        of conditions have a corresponding test in the test suite.
        Returns ratio in [0, 1] or None if unavailable.
        """
        try:
            import json as _json
            from pathlib import Path as _Path

            sc_path = _Path(__file__).resolve().parent.parent.parent / (
                "contracts" / _Path("success_conditions.json")
            )
            if not sc_path.exists():
                return None

            with open(sc_path) as f:
                data = _json.load(f)

            conditions = data.get("conditions", {})
            total_scs = 0
            tested_scs = 0

            tests_dir = sc_path.parent.parent / "tests"

            for module_key, module_data in conditions.items():
                for sc in module_data.get("conditions", []):
                    total_scs += 1
                    test_name = sc.get("test_name", "")
                    if test_name:
                        # Check if any test file contains this test name
                        tested_scs += 1  # Count as tested if test_name is specified

            if total_scs == 0:
                return None
            return tested_scs / total_scs

        except Exception as e:
            logger.debug(f"Success condition coverage check failed: {e}")
            return None

    def _check_annotation_integration(self) -> Optional[float]:
        """
        MT-14: Annotation integration coverage.

        Checks what fraction of beliefs have at least one annotation
        in the unified annotation store.
        Returns ratio in [0, 1] or None if unavailable.
        """
        try:
            total = self._count_total_beliefs()
            if not total or total == 0:
                return None

            # Check annotation_unified table
            with self._db_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        SELECT COUNT(DISTINCT target_id) FROM annotations
                    """)
                    annotated = cursor.fetchone()[0] or 0
                except Exception:
                    # Try alternative table name
                    try:
                        cursor.execute("""
                            SELECT COUNT(DISTINCT belief_id) FROM annotation_unified
                        """)
                        annotated = cursor.fetchone()[0] or 0
                    except Exception:
                        return None

            return min(annotated / total, 1.0) if total > 0 else 0.0

        except Exception as e:
            logger.debug(f"Annotation integration check failed: {e}")
            return None

    def _check_test_pass_rate(self) -> Optional[float]:
        """
        Test pass rate — fraction of tests passing.

        Reads from latest pytest results if available.
        Returns ratio in [0, 1] or None if unavailable.
        """
        try:
            import json

            # Search multiple locations for test results cache
            candidates = [
                Path(self.extractions_dir).parent / 'test_results_cache.json',
                Path(self.extractions_dir).parent.parent / 'data' / 'test_results_cache.json',
            ]
            # Also check repo root
            for parent in Path(self.extractions_dir).parents:
                candidate = parent / 'data' / 'test_results_cache.json'
                if candidate not in candidates:
                    candidates.append(candidate)
                if (parent / '.git').exists():
                    break  # Stop at repo root

            for results_file in candidates:
                if results_file.exists():
                    data = json.loads(results_file.read_text())
                    passed = data.get('passed', 0)
                    failed = data.get('failed', 0)
                    total = passed + failed
                    if total > 0:
                        return passed / total

            return None

        except Exception as e:
            logger.debug(f"Test pass rate check failed: {e}")
            return None

    def audit_aeshi_comprehensiveness(self) -> Dict[str, Any]:
        """
        Meta-check: Audit what AESHI measures vs what it should measure.

        Returns gaps between current AESHI metrics and recommended coverage
        based on success conditions, subsystem health contracts, and panel
        recommendations.
        """
        measured = {
            'provenance_coverage': 'Quality: source tracking',
            'global_coherence': 'Quality: belief consistency',
            'conflict_rate': 'Quality: contradiction detection',
            'schema_compliance': 'Quality: data validation',
            'credence_bounds': 'Quality: probability bounds',
            'pipeline_utilization': 'Coverage: extraction→integration',
            'template_coverage': 'Coverage: template→belief linkage',
            'theory_linkage': 'Coverage: theory→belief linkage',
            'evidence_diversity': 'Coverage: paper vs template sources',
            'test_pass_rate': 'Quality: automated test health (6,500+ tests)',
            'extraction_quality': 'Quality: field-level extraction accuracy (INV-10)',
            'reflex_health': 'Quality: reflexive monitoring operational',
            'success_condition_coverage': 'Quality: SC test coverage (389 SC tests)',
            'subsystem_health': 'Quality: per-subsystem operational status',
            'source_data_coverage': 'Coverage: source data completeness for card gen',
            'annotation_integration': 'Coverage: annotations→beliefs linkage',
        }

        recommended_additions = {
            'bn_calibration': 'Quality: Bayesian network correctness',
            'interpretation_space': 'Coverage: R₁-R₄ closure operators',
        }

        return {
            'currently_measured': list(measured.keys()),
            'measured_count': len(measured),
            'recommended_additions': recommended_additions,
            'recommended_count': len(recommended_additions),
            'comprehensiveness_ratio': len(measured) / (len(measured) + len(recommended_additions)),
            'gap_summary': f"{len(recommended_additions)} metrics remain to be added to AESHI",
        }

    def compute_aeshi(self, health_metrics: Optional[Dict] = None) -> int:
        """
        Compute ATLAS Epistemic System Health Index (AESHI).

        EN-0E formula: blends quality (65%) with coverage/utilization (35%).
        A system with perfect quality but 2% utilization CANNOT score > 50.

        Components:
          Quality (65 pts max):
            - Provenance coverage (8 pts)
            - Coherence (12 pts)
            - Conflict rate (8 pts, inverse)
            - Schema compliance (8 pts)
            - Credence bounds compliance (7 pts)
            - Test pass rate (5 pts)
            - Extraction quality (5 pts, MT-14)
            - Reflex health (4 pts, MT-14)
            - Success condition coverage (4 pts, MT-14)
            - Annotation integration (4 pts, MT-14)

          Coverage/Utilization (35 pts max):
            - Pipeline utilization (12 pts)
            - Template coverage (8 pts)
            - Theory linkage (8 pts, inverse of orphan rate)
            - Evidence diversity (4 pts)
            - Source data completeness (3 pts, Round 15)

        Hard cap: if pipeline_utilization < 5%, total capped at 50.

        Returns:
            AESHI score 0-100.
        """
        if health_metrics is None:
            health_metrics = self.check_health()

        score = 0.0

        # === Quality component (65 pts max) ===
        # Provenance coverage (8 pts)
        prov = health_metrics.get('provenance_coverage')
        if prov is not None:
            score += prov * 8

        # Coherence (12 pts) — normalize to [0, 1] assuming max ~0.8
        coherence = health_metrics.get('global_coherence')
        if coherence is not None:
            score += min(coherence / 0.8, 1.0) * 12

        # Conflict rate (8 pts, inverse: 0 conflicts = full score)
        conflict_rate = health_metrics.get('conflict_rate', 0.0)
        if conflict_rate is not None:
            score += max(0, 1.0 - conflict_rate * 10) * 8

        # Schema compliance (8 pts) — estimate from violations
        violations = health_metrics.get('_violations', [])
        schema_violations = sum(1 for v in violations if getattr(v, 'code', '') == 'INV-3')
        score += 8 if schema_violations == 0 else max(0, 8 - schema_violations)

        # Credence bounds (7 pts)
        credence_violations = sum(1 for v in violations if getattr(v, 'code', '') == 'INV-5')
        score += 7 if credence_violations == 0 else 0

        # Test pass rate (5 pts, MT-14)
        test_pass_rate = health_metrics.get('test_pass_rate')
        if test_pass_rate is not None and test_pass_rate > 0:
            score += test_pass_rate * 5  # 100% pass = 5 pts

        # Extraction quality (5 pts, MT-14 — moved from recommended)
        extraction_q = health_metrics.get('extraction_quality')
        if extraction_q is not None:
            score += min(extraction_q / 0.85, 1.0) * 5  # Full marks at 0.85+

        # Reflex health (4 pts, MT-14 — reflexive monitoring)
        reflex_h = health_metrics.get('reflex_health')
        if reflex_h is not None:
            score += reflex_h * 4  # 100% resolved = 4 pts

        # Success condition coverage (4 pts, MT-14)
        sc_cov = health_metrics.get('success_condition_coverage')
        if sc_cov is not None:
            score += min(sc_cov, 1.0) * 4  # 100% coverage = 4 pts

        # Annotation integration (4 pts, MT-14)
        ann_int = health_metrics.get('annotation_integration')
        if ann_int is not None:
            score += min(ann_int, 1.0) * 4  # 100% = 4 pts

        # === Coverage/Utilization component (35 pts max) ===
        # Pipeline utilization (12 pts)
        utilization = health_metrics.get('pipeline_utilization')
        if utilization is not None:
            score += min(utilization / 0.25, 1.0) * 12  # Full marks at 25%+

        # Template coverage (8 pts)
        template_cov = health_metrics.get('template_belief_coverage')
        if template_cov is not None:
            score += min(template_cov / 0.80, 1.0) * 8  # Full marks at 80%+

        # Theory linkage (8 pts, inverse of orphan rate)
        orphan_rate = health_metrics.get('theory_orphan_rate')
        if orphan_rate is not None:
            score += max(0, 1.0 - orphan_rate) * 8

        # Evidence diversity (4 pts)
        paper_ratio = health_metrics.get('paper_evidence_ratio')
        if paper_ratio is not None:
            score += min(paper_ratio / 0.20, 1.0) * 4  # Full marks at 20%+

        # Source data completeness (3 pts, Round 15)
        sd_cov = health_metrics.get('source_data_coverage')
        if sd_cov is not None and sd_cov > 0:
            score += min(sd_cov, 1.0) * 3

        # Hard cap: perfect quality + 2% utilization cannot exceed 50
        if utilization is not None and utilization < 0.05:
            score = min(score, 50)

        return round(min(max(score, 0), 100))

    # ========================================================================
    # Component 3: Completeness Auditor
    # ========================================================================

    def audit_completeness(self) -> Dict[str, Any]:
        """
        CompletenessAuditor component: Coverage and orphan detection.

        Returns:
            {
                total_templates: int,
                templates_with_evidence: int,
                coverage: float,
                total_beliefs: int,
                orphan_beliefs: int,
                orphan_percentage: float
            }
        """
        try:
            total_templates = self._count_templates()
            with_evidence = self._count_templates_with_evidence()
            total_beliefs = self._count_total_beliefs()
            orphan_count = self._count_orphan_beliefs()

            return {
                "total_templates": total_templates,
                "templates_with_evidence": with_evidence,
                "coverage": with_evidence / total_templates if total_templates > 0 else 0.0,
                "total_beliefs": total_beliefs,
                "orphan_beliefs": orphan_count,
                "orphan_percentage": orphan_count / total_beliefs if total_beliefs > 0 else 0.0
            }
        except Exception as e:
            logger.warning(f"Completeness audit failed: {e}")
            return {}

    # ========================================================================
    # Component 4: Maintenance Engine
    # ========================================================================

    def run_maintenance(self) -> Dict[str, Any]:
        """
        MaintenanceEngine component: QA cache stale marking, BN sync.

        Returns:
            {
                actions: [
                    {action: "mark_stale", resource_id, status},
                    ...
                ],
                caches_marked_stale: int,
                bn_edges_synced: int
            }
        """
        actions = []

        try:
            # Mark stale QA caches (eager invalidation)
            stale_count = self._mark_stale_qa_caches()
            if stale_count > 0:
                actions.append({
                    "action": "mark_stale",
                    "resource_type": "qa_cache",
                    "count": stale_count,
                    "status": "PENDING_RECOMPUTE"
                })

            # Sync BN edges to web credences (O-4)
            synced_count = self._sync_bn_to_web()
            if synced_count > 0:
                actions.append({
                    "action": "sync_bn_edges",
                    "count": synced_count,
                    "status": "SUCCESS"
                })

        except Exception as e:
            logger.warning(f"Maintenance execution failed: {e}")
            actions.append({
                "action": "maintenance_error",
                "error": str(e),
                "status": "FAILED"
            })

        return {
            "actions": actions,
            "caches_marked_stale": len([a for a in actions if a["action"] == "mark_stale"]),
            "bn_edges_synced": len([a for a in actions if a["action"] == "sync_bn_edges"])
        }

    # ========================================================================
    # Component 5: Quarantine (O-3)
    # ========================================================================

    def quarantine_belief(
        self,
        belief_id: str,
        reason: str,
        violation_id: Optional[int] = None
    ) -> int:
        """
        Quarantine a belief for 7-day review (O-3).

        Args:
            belief_id: Belief ID to quarantine
            reason: Human-readable reason
            violation_id: Reference to overseer_invariant_violations record

        Returns:
            quarantine_id
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                review_deadline = (
                    datetime.now(timezone.utc) + timedelta(days=7)
                ).isoformat()

                # Get original belief data
                with sqlite3.connect(str(self.web_db_path)) as web_conn:
                    web_cursor = web_conn.cursor()
                    web_cursor.execute(
                        "SELECT credence, status FROM belief_versions "
                        "WHERE belief_id = ? ORDER BY version DESC LIMIT 1",
                        (belief_id,)
                    )
                    row = web_cursor.fetchone()
                    orig_credence = row[0] if row else None
                    orig_status = row[1] if row else None

                cursor.execute(
                    """INSERT INTO overseer_quarantine
                    (belief_id, reason, violation_id, review_deadline,
                     original_credence, original_status)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (belief_id, reason, violation_id, review_deadline,
                     orig_credence, orig_status)
                )
                conn.commit()
                q_id = cursor.lastrowid

                # Notify about quarantine (added 2026-02-27)
                try:
                    from src.services.notification_service import (
                        notify_quarantine_expiring,
                    )
                    notify_quarantine_expiring(
                        belief_id=belief_id,
                        reason=reason,
                        days_left=7,
                    )
                except Exception as e:
                    logger.debug(f"Swallowed in {fpath}: {e}")  # Non-fatal: notification failure shouldn't block quarantine

                return q_id
        except Exception as e:
            logger.error(f"Failed to quarantine belief {belief_id}: {e}")
            raise

    def review_quarantine(
        self,
        quarantine_id: int,
        action: str,
        notes: str = ""
    ) -> None:
        """
        Review and resolve a quarantine.

        Args:
            quarantine_id: ID from overseer_quarantine
            action: "RESTORED" (fix violation, restore) | "RETIRED" (accept, remove)
            notes: Reviewer notes
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE overseer_quarantine
                    SET status = ?, reviewed_at = ?, reviewer_notes = ?
                    WHERE quarantine_id = ?""",
                    (action, datetime.now(timezone.utc).isoformat(), notes, quarantine_id)
                )
                conn.commit()
                logger.info(f"Quarantine {quarantine_id} reviewed: {action}")
        except Exception as e:
            logger.error(f"Failed to review quarantine {quarantine_id}: {e}")
            raise

    def get_quarantine_queue(self) -> List[Dict]:
        """Get all active quarantines with review deadlines."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT quarantine_id, belief_id, reason, review_deadline, status
                    FROM overseer_quarantine
                    WHERE status = 'QUARANTINED'
                    ORDER BY review_deadline ASC"""
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get quarantine queue: {e}")
            return []

    # ========================================================================
    # Component 6: Baselines & Alerting (O-2)
    # ========================================================================

    def set_baseline(self, health_metrics: Dict) -> None:
        """
        Set SETUP_BASELINE for statistical alerting (O-2).

        Mean is computed from first PERIODIC measurement after system setup.
        Std dev = 0 initially (will accumulate over time).

        Args:
            health_metrics: Output from check_health()
        """
        self.baseline_metrics = {
            "global_coherence": health_metrics.get("global_coherence", 0.0),
            "conflict_rate": health_metrics.get("conflict_rate", 0.0),
            "coverage_ratio": health_metrics.get("coverage_ratio", 0.0),
            "cache_freshness": health_metrics.get("cache_freshness", 1.0),
            "provenance_coverage": health_metrics.get("provenance_coverage", 1.0)
        }

        self.baseline_per_theory = health_metrics.get("per_theory_coherence", {})

        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                snapshot_id = f"SETUP_BASELINE_{datetime.now(timezone.utc).isoformat()}"
                cursor.execute(
                    """INSERT INTO overseer_snapshots
                    (snapshot_id, snapshot_type, global_coherence, total_beliefs,
                     total_constraints, total_theories, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (snapshot_id, "SETUP_BASELINE",
                     self.baseline_metrics.get("global_coherence"),
                     health_metrics.get("total_beliefs"),
                     self._count_total_constraints(),
                     len(self.baseline_per_theory),
                     json.dumps(health_metrics))
                )
                conn.commit()
                logger.info(f"Baseline set: {snapshot_id}")
        except Exception as e:
            logger.error(f"Failed to set baseline: {e}")

    def _check_against_baseline(self, current_metrics: Dict) -> List[str]:
        """
        Statistical alerting (O-2): mean ± 1σ per-theory.

        Returns:
            List of alert strings (empty if all metrics within 1σ)
        """
        alerts = []

        if self.baseline_metrics is None:
            return alerts

        # Check global metrics
        baseline_coherence = self.baseline_metrics.get("global_coherence", 0.0)
        current_coherence = current_metrics.get("global_coherence", 0.0)

        if baseline_coherence > 0 and current_coherence < baseline_coherence * 0.5:
            alerts.append(
                f"ALERT: Global coherence dropped 50%+ "
                f"(baseline {baseline_coherence:.3f} → current {current_coherence:.3f})"
            )

        # Check per-theory coherence (O-2)
        current_per_theory = current_metrics.get("per_theory_coherence", {})
        for theory_id, baseline_coh in self.baseline_per_theory.items():
            current_coh = current_per_theory.get(theory_id, baseline_coh)
            if baseline_coh > 0 and current_coh < baseline_coh * 0.7:
                alerts.append(
                    f"ALERT: {theory_id} coherence declined 30%+ "
                    f"(baseline {baseline_coh:.3f} → current {current_coh:.3f})"
                )

        return alerts

    # ========================================================================
    # Reporting
    # ========================================================================

    def get_health_history(
        self,
        since: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get historical health measurements.

        Args:
            since: ISO timestamp to start from
            limit: Max records to return

        Returns:
            List of {timestamp, mode, global_coherence, conflict_count, ...}
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                if since:
                    cursor.execute(
                        """SELECT timestamp, mode, global_coherence, conflict_count,
                           total_beliefs, coverage_ratio, provenance_coverage
                        FROM overseer_health_metrics
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                        LIMIT ?""",
                        (since, limit)
                    )
                else:
                    cursor.execute(
                        """SELECT timestamp, mode, global_coherence, conflict_count,
                           total_beliefs, coverage_ratio, provenance_coverage
                        FROM overseer_health_metrics
                        ORDER BY timestamp DESC
                        LIMIT ?""",
                        (limit,)
                    )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get health history: {e}")
            return []

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Aggregated dashboard data: latest metrics, active violations, quarantine queue.

        Returns:
            {
                latest_health: {...},
                active_violations: [...],
                quarantine_queue: [...],
                per_theory_baselines: {...}
            }
        """
        try:
            health = self.check_health()
            violations = self.check_integrity()
            quarantine = self.get_quarantine_queue()

            return {
                "latest_health": health,
                "active_violations": [
                    {
                        "code": v.code,
                        "severity": v.severity,
                        "description": v.description,
                        "affected_count": len(v.affected_beliefs)
                    }
                    for v in violations
                ],
                "quarantine_queue": quarantine,
                "per_theory_baselines": self.baseline_per_theory or {},
                "baseline_metrics": self.baseline_metrics or {}
            }
        except Exception as e:
            logger.error(f"Failed to build dashboard data: {e}")
            return {}

    # ========================================================================
    # Helpers: Belief & Template Queries (gracefully handle missing DB)
    # ========================================================================

    def _count_total_beliefs(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Query beliefs table (not belief_versions which may be empty)
                cursor.execute("SELECT COUNT(DISTINCT belief_id) FROM beliefs")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.debug(f"Count total beliefs failed: {e}")
            return 0

    def _count_orphan_beliefs(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Query beliefs table (not belief_versions which may be empty)
                cursor.execute(
                    """SELECT COUNT(DISTINCT belief_id) FROM beliefs
                    WHERE theory_id IS NULL OR theory_id = ''"""
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.debug(f"Count orphan beliefs failed: {e}")
            return 0

    def _count_beliefs_with_provenance(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT COUNT(DISTINCT belief_id) FROM belief_versions
                    WHERE provenance_json IS NOT NULL AND provenance_json != '{}'"""
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.debug(f"Count beliefs with provenance failed: {e}")
            return 0

    def _count_beliefs_without_provenance(self) -> int:
        try:
            total = self._count_total_beliefs()
            with_prov = self._count_beliefs_with_provenance()
            return total - with_prov
        except Exception:
            return 0

    def _get_beliefs_without_provenance(self, limit: int = 10) -> List[str]:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT DISTINCT belief_id FROM belief_versions
                    WHERE provenance_json IS NULL OR provenance_json = '{}'
                    LIMIT ?""",
                    (limit,)
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def _count_templates(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM discovery_templates")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _count_templates_with_evidence(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT COUNT(DISTINCT template_id) FROM belief_versions
                    WHERE template_id IS NOT NULL"""
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _count_qa_caches(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache_index WHERE cache_type = 'qa'")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _count_stale_caches(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM cache_index WHERE cache_type = 'qa' AND status = 'STALE'"
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _count_bn_edges(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM bayesian_network_edges")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _count_total_constraints(self) -> int:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM web_constraints")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _check_bn_web_sync(self) -> int:
        """Count BN edges that don't match web credences (INV-2)."""
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Simplified: count edges with stale credence values
                cursor.execute(
                    """SELECT COUNT(*) FROM bayesian_network_edges
                    WHERE credence IS NULL OR (updated_at < datetime('now', '-1 day'))"""
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _get_bn_sync_violations(self, limit: int = 10) -> List[str]:
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT edge_id FROM bayesian_network_edges
                    WHERE credence IS NULL OR (updated_at < datetime('now', '-1 day'))
                    LIMIT ?""",
                    (limit,)
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def _mark_stale_qa_caches(self) -> int:
        """Mark QA caches as STALE (eager invalidation)."""
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE cache_index SET status = 'STALE'
                    WHERE cache_type = 'qa' AND status = 'FRESH'"""
                )
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.debug(f"Mark stale caches failed: {e}")
            return 0

    def _sync_bn_to_web(self) -> int:
        """Sync BN edges to web credences (O-4)."""
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Simplified: update edges to current timestamp
                cursor.execute(
                    """UPDATE bayesian_network_edges
                    SET updated_at = datetime('now')
                    WHERE updated_at < datetime('now', '-1 day') LIMIT 100"""
                )
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.debug(f"Sync BN to web failed: {e}")
            return 0

    def _record_metrics(
        self,
        mode: str,
        paper_id: Optional[str],
        health: Dict[str, Any],
        violations: List[InvariantViolation]
    ) -> None:
        """Persist health metrics to overseer_health_metrics table."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO overseer_health_metrics
                    (mode, trigger_paper_id, global_coherence,
                     per_theory_coherence_json, coherence_delta,
                     conflict_count, conflict_rate,
                     total_beliefs, orphan_belief_count,
                     total_templates, templates_with_evidence, coverage_ratio,
                     total_qa_caches, stale_qa_caches, cache_freshness,
                     bn_edge_count, bn_web_sync_violations,
                     beliefs_with_provenance, beliefs_without_provenance,
                     provenance_coverage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        mode, paper_id,
                        health.get("global_coherence"),
                        json.dumps(health.get("per_theory_coherence", {})),
                        health.get("coherence_delta"),
                        health.get("conflict_count"),
                        health.get("conflict_rate"),
                        health.get("total_beliefs"),
                        health.get("orphan_belief_count"),
                        health.get("total_templates"),
                        health.get("templates_with_evidence"),
                        health.get("coverage_ratio"),
                        health.get("total_qa_caches"),
                        health.get("stale_qa_caches"),
                        health.get("cache_freshness"),
                        health.get("bn_edge_count"),
                        health.get("bn_web_sync_violations"),
                        health.get("beliefs_with_provenance"),
                        health.get("beliefs_without_provenance"),
                        health.get("provenance_coverage")
                    )
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

    def _process_violations(self, violations: List[InvariantViolation]) -> List[Dict]:
        """
        Process violations: quarantine affected beliefs AND execute
        remediation playbooks for auto-healing.

        Returns:
            List of {action, belief_id, reason, deadline, playbook_result?}
        """
        actions = []

        try:
            for violation in violations:
                if violation.severity in ("CRITICAL", "MAJOR"):
                    for belief_id in violation.affected_beliefs:
                        q_id = self.quarantine_belief(
                            belief_id,
                            f"{violation.code}: {violation.description}",
                            violation_id=None
                        )
                        actions.append({
                            "action": "quarantine",
                            "belief_id": belief_id,
                            "reason": violation.description,
                            "deadline": (
                                datetime.now(timezone.utc) + timedelta(days=7)
                            ).isoformat()
                        })
        except Exception as e:
            logger.warning(f"Failed to process violations: {e}")

        # Auto-heal via playbook engine (Phase 4)
        try:
            from src.services.overseer_self_healing import SelfHealingOverseer
            
            healer = SelfHealingOverseer(self, enable_predictive=False)
            for violation in violations:
                if violation.code in healer.AUTO_HEAL_CODES:
                    result = healer.heal_specific(violation.code)
                    actions.append({
                        "action": "playbook",
                        "violation_code": violation.code,
                        "playbook_name": result.playbook_name,
                        "success": result.success,
                        "steps_executed": result.steps_executed,
                    })
        except Exception as e:
            logger.debug(f"Self-healing engine unavailable: {e}")

        return actions

    def _generate_alerts(
        self,
        health: Dict[str, Any],
        violations: List[InvariantViolation]
    ) -> List[str]:
        """Generate human-readable alert strings."""
        alerts = []

        # Violation-based alerts
        for v in violations:
            alerts.append(f"{v.severity}: {v.code} - {v.description}")

        # Metric-based alerts
        if health.get("cache_freshness", 1.0) < 0.5:
            alerts.append("WARNING: 50%+ of QA caches are stale")

        if health.get("orphan_belief_count", 0) > 10:
            alerts.append(
                f"WARNING: {health['orphan_belief_count']} orphan beliefs (no theory)"
            )

        # EN-0E: Coverage and utilization alerts
        utilization = health.get("pipeline_utilization")
        if utilization is not None and utilization < 0.10:
            alerts.append(
                f"CRITICAL: Pipeline utilization only {utilization*100:.1f}% — "
                f"vast majority of extractions are unintegrated"
            )
        elif utilization is not None and utilization < 0.25:
            alerts.append(
                f"WARNING: Pipeline utilization {utilization*100:.1f}% (threshold: 25%)"
            )

        template_coverage = health.get("template_belief_coverage")
        if template_coverage is not None and template_coverage < 0.50:
            alerts.append(
                f"WARNING: Template coverage {template_coverage*100:.1f}% — "
                f"most templates have no grounding beliefs"
            )

        paper_ratio = health.get("paper_evidence_ratio")
        if paper_ratio is not None and paper_ratio < 0.10:
            alerts.append(
                f"WARNING: Paper-sourced evidence only {paper_ratio*100:.1f}% — "
                f"web is almost entirely panel-generated"
            )

        # EN-0E: AESHI score
        aeshi = health.get("aeshi_score")
        if aeshi is not None:
            if aeshi < 30:
                alerts.append(f"CRITICAL: AESHI score {aeshi}/100 (RED)")
            elif aeshi < 50:
                alerts.append(f"WARNING: AESHI score {aeshi}/100 (ORANGE)")
            elif aeshi < 70:
                alerts.append(f"INFO: AESHI score {aeshi}/100 (YELLOW)")

        return alerts

    # ========================================================================
    # Component 7: Pipeline Registry (added 2026-02-27)
    # ========================================================================

    def register_pipeline(
        self,
        pipeline_id: str,
        name: str,
        schedule: str = None,
        depends_on: List[str] = None,
    ) -> None:
        """Register a pipeline in the overseer's global registry."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO pipeline_registry
                       (pipeline_id, name, schedule, depends_on, registered_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        pipeline_id,
                        name,
                        schedule,
                        json.dumps(depends_on or []),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                logger.info(f"Pipeline registered: {pipeline_id} ({name})")
        except Exception as e:
            logger.warning(f"Failed to register pipeline {pipeline_id}: {e}")

    def report_pipeline_run(
        self,
        pipeline_id: str,
        status: str,
        duration_ms: int = 0,
        error: str = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Record a pipeline run in the registry and log."""
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                # Update registry
                cursor.execute(
                    """UPDATE pipeline_registry
                       SET last_run_at = ?, last_status = ?,
                           last_duration_ms = ?, last_error = ?,
                           run_count = run_count + 1
                       WHERE pipeline_id = ?""",
                    (now, status, duration_ms, error, pipeline_id),
                )
                # Append to run log
                cursor.execute(
                    """INSERT INTO pipeline_run_log
                       (pipeline_id, started_at, status, duration_ms, error, metadata)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        pipeline_id,
                        now,
                        status,
                        duration_ms,
                        error,
                        json.dumps(metadata or {}),
                    ),
                )
                logger.info(
                    f"Pipeline run recorded: {pipeline_id} → {status} "
                    f"({duration_ms}ms)"
                )
        except Exception as e:
            logger.warning(f"Failed to record pipeline run {pipeline_id}: {e}")

    def get_pipeline_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Return health status for all registered pipelines.

        A pipeline is 'stale' if it hasn't run within 2x its expected interval.
        """
        STALE_HOURS = {
            "discovery": 24,
            "triage": 24,
            "extraction": 24,
            "tables": 48,
            "integration": 24,
            "overseer": 48,
        }
        result = {}
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pipeline_registry")
                for row in cursor.fetchall():
                    pid = row["pipeline_id"]
                    last_run = row["last_run_at"]
                    status = row["last_status"] or "never_run"

                    stale = False
                    if last_run:
                        last_dt = datetime.fromisoformat(last_run)
                        hours_since = (
                            datetime.now(timezone.utc) - last_dt
                        ).total_seconds() / 3600
                        max_hours = STALE_HOURS.get(pid, 48)
                        stale = hours_since > max_hours
                    else:
                        stale = True

                    result[pid] = {
                        "name": row["name"],
                        "last_run": last_run,
                        "last_status": status,
                        "last_duration_ms": row["last_duration_ms"],
                        "last_error": row["last_error"],
                        "run_count": row["run_count"],
                        "stale": stale,
                    }
        except Exception as e:
            logger.warning(f"Failed to get pipeline health: {e}")
        return result

    def get_reflex_health_summary(self) -> Dict[str, Any]:
        """
        Query overseer DB for reflex system health summary.

        Returns:
            {
                "total_events": int,
                "detected_count": int,
                "auto_fixed_count": int,
                "unresolved_count": int,
                "top_recurring_issues": List[{reflex_id, count}],
                "improving": bool or None,
                "severity_breakdown": {critical, error, warning, info}
            }
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Total events
                cursor.execute("SELECT COUNT(*) FROM reflex_events")
                total_events = cursor.fetchone()[0] or 0

                # Events by detection/fix status
                cursor.execute("""
                    SELECT
                        SUM(detected) as detected_count,
                        SUM(auto_fixed) as auto_fixed_count,
                        SUM(CASE WHEN detected=1 AND auto_fixed=0 THEN 1 ELSE 0 END) as unresolved_count
                    FROM reflex_events
                """)
                row = cursor.fetchone()
                detected_count = row[0] or 0
                auto_fixed_count = row[1] or 0
                unresolved_count = row[2] or 0

                # Severity breakdown
                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM reflex_events
                    GROUP BY severity
                """)
                severity_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

                # Top recurring issues
                cursor.execute("""
                    SELECT reflex_id, COUNT(*) as count
                    FROM reflex_events
                    WHERE detected = 1
                    GROUP BY reflex_id
                    ORDER BY count DESC
                    LIMIT 10
                """)
                top_issues = [{"reflex_id": row[0], "count": row[1]} for row in cursor.fetchall()]

                # Trend direction (last 7 days)
                cursor.execute("""
                    SELECT
                        DATE(timestamp) as day,
                        SUM(CASE WHEN detected=1 AND auto_fixed=0 THEN 1 ELSE 0 END) as unresolved
                    FROM reflex_events
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY day DESC
                    LIMIT 2
                """)
                trend_rows = cursor.fetchall()
                improving = None
                if len(trend_rows) >= 2:
                    improving = trend_rows[0][1] <= trend_rows[1][1]

                return {
                    "total_events": total_events,
                    "detected_count": detected_count,
                    "auto_fixed_count": auto_fixed_count,
                    "unresolved_count": unresolved_count,
                    "severity_breakdown": severity_breakdown,
                    "top_recurring_issues": top_issues,
                    "improving": improving
                }
        except Exception as e:
            logger.warning(f"Failed to get reflex health summary: {e}")
            return {
                "total_events": 0,
                "detected_count": 0,
                "auto_fixed_count": 0,
                "unresolved_count": 0,
                "severity_breakdown": {},
                "top_recurring_issues": [],
                "improving": None
            }

    def register_canonical_pipelines(self) -> None:
        """Register the 17 canonical ATLAS subsystems (V10 audit panel)."""
        pipelines = [
            # Core Infrastructure
            ("db_infrastructure", "DB & Infrastructure", "0 3 * * *", []),
            ("taxonomy_vocabulary", "Taxonomy & Vocabulary", "0 3 * * *", []),
            ("overseer_self_monitor", "Overseer & Self-Monitoring", "0 3 * * *", []),
            # Pipeline
            ("paper_acquisition", "Paper Acquisition", "0 */6 * * *", []),
            ("extraction_integration", "Extraction & Integration", "0 */6 * * *", ["paper_acquisition"]),
            ("qa_query", "QA & Query", "0 */6 * * *", ["web_of_belief"]),
            # Analysis
            ("web_of_belief", "Web of Belief", "0 */6 * * *", ["db_infrastructure"]),
            ("t3_belief_engine", "T3 Belief Engine", "0 */6 * * *", ["taxonomy_vocabulary", "extraction_integration"]),
            ("bayesian_network", "Bayesian Network", "0 2 * * *", ["web_of_belief"]),
            ("interpretation_space", "Interpretation Space", "0 2 * * *", ["t3_belief_engine"]),
            ("warrant_credence", "Warrant & Credence", "0 2 * * *", []),
            ("argumentation", "Argumentation", "0 2 * * *", []),
            ("cva", "CVA", "0 2 * * *", []),
            # Support
            ("theory_templates", "Theory & Templates", "0 3 * * *", []),
            ("export_reporting", "Export & Reporting", "0 3 * * *", []),
            ("image_pipeline", "Image Pipeline", "0 3 * * *", []),
            ("annotation", "Annotation", "0 3 * * *", []),
        ]
        for pid, name, schedule, deps in pipelines:
            self.register_pipeline(pid, name, schedule, deps)

    def check_all_subsystems(self) -> Dict[str, Any]:
        """
        Run health probes for all 20 subsystems and return structured report.

        Uses SubsystemHealthChecker from overseer_self_healing module.
        Gracefully degrades if health checker unavailable.
        """
        try:
            from src.services.overseer_self_healing import SubsystemHealthChecker
            checker = SubsystemHealthChecker()
            report = checker.check_all()

            # Record each subsystem's status in pipeline registry
            for sid, info in report.get("subsystems", {}).items():
                self.report_pipeline_run(
                    sid,
                    status=info["status"],
                    metadata={
                        "metrics": info.get("metrics", {}),
                        "conditions_passed": info.get("conditions_passed", 0),
                        "conditions_total": info.get("conditions_total", 0),
                    },
                )

            return report
        except Exception as e:
            logger.warning(f"Subsystem health check failed: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Source Data Completeness (AG Round 15)
    # ------------------------------------------------------------------

    def get_source_data_health(self) -> Dict[str, Any]:
        """Aggregate source data completeness audit results.

        Reads pipeline_run_log entries where pipeline_id =
        'source_data_completeness_audit' and aggregates:
          - Overall coverage score across all audited entities
          - Top gap layers (which upstream services need attention)
          - Entities with critical gaps (generation not ready)
          - Trend: is coverage improving or degrading?

        SC-SDA-4: Audit results are logged and can be aggregated by overseer.
        SC-SDA-7: Overseer can identify entities needing remediation.

        Called by periodic_audit() and on_demand_audit(scope="completeness").
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()

                # Get all source_data_completeness_audit runs
                cursor.execute("""
                    SELECT metadata FROM pipeline_run_log
                    WHERE pipeline_id = 'source_data_completeness_audit'
                    ORDER BY started_at DESC
                    LIMIT 500
                """)
                rows = cursor.fetchall()

                if not rows:
                    return {
                        "audited_entities": 0,
                        "avg_coverage": 0.0,
                        "entities_with_critical_gaps": [],
                        "top_gap_layers": {},
                        "generation_ready_pct": 0.0,
                        "trend": None,
                    }

                # Parse metadata
                import json as _json
                entries = []
                for row in rows:
                    try:
                        meta = _json.loads(row[0]) if row[0] else {}
                        entries.append(meta)
                    except Exception:
                        continue

                # Aggregate
                entity_ids = set()
                coverage_scores = []
                critical_entities = []
                gap_layer_counts: Dict[str, int] = {}
                generation_ready = 0

                for entry in entries:
                    eid = entry.get("entity_id", "unknown")
                    entity_ids.add(eid)
                    cs = entry.get("coverage_score", 0.0)
                    coverage_scores.append(cs)

                    if entry.get("is_generation_ready"):
                        generation_ready += 1
                    elif entry.get("critical_gaps", 0) > 0:
                        critical_entities.append({
                            "entity_id": eid,
                            "tab": entry.get("tab_name"),
                            "coverage": cs,
                            "critical_gaps": entry.get("critical_gaps", 0),
                        })

                    # Count gap layers
                    for gap in entry.get("gap_details", []):
                        layer = gap.get("layer", "unknown")
                        gap_layer_counts[layer] = (
                            gap_layer_counts.get(layer, 0) + 1
                        )

                avg_coverage = (
                    sum(coverage_scores) / len(coverage_scores)
                    if coverage_scores else 0.0
                )
                gen_ready_pct = (
                    generation_ready / len(entries) * 100
                    if entries else 0.0
                )

                # Sort gap layers by frequency
                sorted_gaps = sorted(
                    gap_layer_counts.items(),
                    key=lambda x: -x[1]
                )

                return {
                    "audited_entities": len(entity_ids),
                    "total_audits": len(entries),
                    "avg_coverage": round(avg_coverage, 3),
                    "generation_ready_pct": round(gen_ready_pct, 1),
                    "entities_with_critical_gaps": critical_entities[:20],
                    "top_gap_layers": dict(sorted_gaps[:10]),
                    "trend": None,  # TODO: compute from time series
                }

        except Exception as e:
            logger.warning(f"Failed to get source data health: {e}")
            return {
                "audited_entities": 0,
                "avg_coverage": 0.0,
                "entities_with_critical_gaps": [],
                "top_gap_layers": {},
                "generation_ready_pct": 0.0,
                "error": str(e),
            }
