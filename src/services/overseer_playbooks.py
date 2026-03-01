"""
overseer_playbooks.py — Remediation Playbooks for Overseer (Phase 4)
=====================================================================

Auto-remediation engine: when overseer detects violations,
playbooks prescribe and execute corrective actions.

Reference: AG_ASSIGNMENT Phase 4, Tasks 4.1–4.3
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
import logging
import time

log = logging.getLogger(__name__)


class PlaybookSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RemediationAction(Enum):
    """Standard remediation actions."""
    RERUN_PIPELINE = "rerun_pipeline"
    QUARANTINE_BELIEFS = "quarantine_beliefs"
    ADJUST_THRESHOLDS = "adjust_thresholds"
    REGENERATE_TEMPLATES = "regenerate_templates"
    NOTIFY_HUMAN = "notify_human"
    RECOMPUTE_COHERENCE = "recompute_coherence"
    REBUILD_CONSTRAINTS = "rebuild_constraints"
    ROLLBACK_LAST_INTEGRATION = "rollback_last_integration"
    SKIP = "skip"


@dataclass
class PlaybookStep:
    """Single step in a remediation playbook."""
    action: RemediationAction
    description: str
    params: Dict = field(default_factory=dict)
    timeout_seconds: float = 300.0
    retry_count: int = 1


@dataclass
class PlaybookResult:
    """Result of executing a playbook."""
    playbook_name: str
    success: bool
    steps_executed: int
    steps_total: int
    duration_ms: float
    details: str = ""


@dataclass
class RemediationPlaybook:
    """
    A remediation playbook for a specific violation type.

    Maps invariant violations to sequences of corrective actions.
    """
    name: str
    violation_code: str  # e.g., "INV-4"
    severity: PlaybookSeverity
    steps: List[PlaybookStep]
    description: str = ""
    success_count: int = 0
    failure_count: int = 0
    last_run: Optional[str] = None

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


# ──────────────────────────────────────────────────────────────────
# Pre-defined Playbooks (from spec §4.1)
# ──────────────────────────────────────────────────────────────────

PLAYBOOKS: Dict[str, RemediationPlaybook] = {
    "INV-0": RemediationPlaybook(
        name="belief_count_recovery",
        violation_code="INV-0",
        severity=PlaybookSeverity.CRITICAL,
        description="Belief count dropped below threshold",
        steps=[
            PlaybookStep(RemediationAction.ROLLBACK_LAST_INTEGRATION,
                         "Rollback the last integration that may have deleted beliefs"),
            PlaybookStep(RemediationAction.RERUN_PIPELINE,
                         "Re-run integration pipeline to restore beliefs",
                         params={"pipeline": "integration"}),
            PlaybookStep(RemediationAction.NOTIFY_HUMAN,
                         "Alert human operator if beliefs still missing"),
        ],
    ),
    "INV-1": RemediationPlaybook(
        name="constraint_ratio_fix",
        violation_code="INV-1",
        severity=PlaybookSeverity.WARNING,
        description="Constraint-to-belief ratio out of range",
        steps=[
            PlaybookStep(RemediationAction.REBUILD_CONSTRAINTS,
                         "Rebuild constraint graph from belief pairs"),
            PlaybookStep(RemediationAction.RECOMPUTE_COHERENCE,
                         "Recompute coherence scores"),
        ],
    ),
    "INV-2": RemediationPlaybook(
        name="orphan_belief_cleanup",
        violation_code="INV-2",
        severity=PlaybookSeverity.WARNING,
        description="Too many orphan beliefs (>30%)",
        steps=[
            PlaybookStep(RemediationAction.REBUILD_CONSTRAINTS,
                         "Generate constraints for orphan beliefs",
                         params={"target": "orphans_only"}),
            PlaybookStep(RemediationAction.ADJUST_THRESHOLDS,
                         "Temporarily raise orphan threshold if structural",
                         params={"threshold_key": "max_orphan_ratio", "delta": 0.05}),
        ],
    ),
    "INV-4": RemediationPlaybook(
        name="coherence_decline_recovery",
        violation_code="INV-4",
        severity=PlaybookSeverity.CRITICAL,
        description="Coherence declined >5%",
        steps=[
            PlaybookStep(RemediationAction.QUARANTINE_BELIEFS,
                         "Quarantine recently added beliefs that reduced coherence",
                         params={"lookback_hours": 24}),
            PlaybookStep(RemediationAction.RECOMPUTE_COHERENCE,
                         "Recompute coherence without quarantined beliefs"),
            PlaybookStep(RemediationAction.NOTIFY_HUMAN,
                         "Alert human for review of quarantined beliefs"),
        ],
    ),
    "INV-6": RemediationPlaybook(
        name="pipeline_utilization_recovery",
        violation_code="INV-6",
        severity=PlaybookSeverity.WARNING,
        description="Pipeline utilization below threshold",
        steps=[
            PlaybookStep(RemediationAction.RERUN_PIPELINE,
                         "Re-run underutilized pipeline stages",
                         params={"pipeline": "all"}),
        ],
    ),
    "INV-7": RemediationPlaybook(
        name="template_coverage_fix",
        violation_code="INV-7",
        severity=PlaybookSeverity.WARNING,
        description="Template coverage below threshold",
        steps=[
            PlaybookStep(RemediationAction.REGENERATE_TEMPLATES,
                         "Regenerate template-belief mappings"),
            PlaybookStep(RemediationAction.ADJUST_THRESHOLDS,
                         "Lower coverage threshold if templates are sparse",
                         params={"threshold_key": "min_template_coverage", "delta": -0.05}),
        ],
    ),
    "INV-8": RemediationPlaybook(
        name="theory_orphan_fix",
        violation_code="INV-8",
        severity=PlaybookSeverity.WARNING,
        description="Theory orphan rate above threshold",
        steps=[
            PlaybookStep(RemediationAction.REGENERATE_TEMPLATES,
                         "Regenerate theory-template links for orphan theories"),
            PlaybookStep(RemediationAction.REBUILD_CONSTRAINTS,
                         "Rebuild constraints to connect orphan theories",
                         params={"target": "orphans_only"}),
        ],
    ),
    "INV-9": RemediationPlaybook(
        name="evidence_diversity_fix",
        violation_code="INV-9",
        severity=PlaybookSeverity.INFO,
        description="Panel-dominated evidence needs more paper signals",
        steps=[
            PlaybookStep(RemediationAction.RERUN_PIPELINE,
                         "Re-run integration pipeline for unprocessed papers",
                         params={"pipeline": "integration"}),
            PlaybookStep(RemediationAction.NOTIFY_HUMAN,
                         "Alert: system needs more paper integrations"),
        ],
    ),
}

# CVA-aware invariants (Phase 4, Task 4.5)
CVA_PLAYBOOKS: Dict[str, RemediationPlaybook] = {
    "INV-10": RemediationPlaybook(
        name="cva_constraint_drift",
        violation_code="INV-10",
        severity=PlaybookSeverity.WARNING,
        description="CVA constraint vector drifting outside expected range",
        steps=[
            PlaybookStep(RemediationAction.RECOMPUTE_COHERENCE,
                         "Recalibrate constraint θ(ψ) parameters"),
            PlaybookStep(RemediationAction.NOTIFY_HUMAN,
                         "Alert: constraint drift may indicate model misfit"),
        ],
    ),
    "INV-11": RemediationPlaybook(
        name="cva_valuation_instability",
        violation_code="INV-11",
        severity=PlaybookSeverity.CRITICAL,
        description="CVA valuation engine producing unstable outputs",
        steps=[
            PlaybookStep(RemediationAction.ADJUST_THRESHOLDS,
                         "Reduce dynamics alpha/beta to stabilize",
                         params={"alpha_factor": 0.8, "beta_factor": 0.8}),
            PlaybookStep(RemediationAction.RECOMPUTE_COHERENCE,
                         "Recompute valuations with reduced gain"),
        ],
    ),
    "INV-12": RemediationPlaybook(
        name="cva_attractor_collapse",
        violation_code="INV-12",
        severity=PlaybookSeverity.CRITICAL,
        description="All states converging to single attractor (basin collapse)",
        steps=[
            PlaybookStep(RemediationAction.ADJUST_THRESHOLDS,
                         "Widen basin radii for underrepresented attractors"),
            PlaybookStep(RemediationAction.NOTIFY_HUMAN,
                         "Alert: attractor collapse may require model revision"),
        ],
    ),
    "INV-13": RemediationPlaybook(
        name="cva_cultural_variant_missing",
        violation_code="INV-13",
        severity=PlaybookSeverity.INFO,
        description="Cultural variant data incomplete",
        steps=[
            PlaybookStep(RemediationAction.REGENERATE_TEMPLATES,
                         "Regenerate cultural variant configurations"),
        ],
    ),
}

# Merge all playbooks
ALL_PLAYBOOKS = {**PLAYBOOKS, **CVA_PLAYBOOKS}


class RemediationEngine:
    """
    Auto-remediation engine with learning loop.

    Executes playbooks for violations, tracks success rates,
    and adjusts strategy over time.
    """

    def __init__(self):
        self.playbooks = dict(ALL_PLAYBOOKS)
        self.execution_log: List[PlaybookResult] = []
        # Action handlers (can be registered)
        self._handlers: Dict[RemediationAction, Callable] = {}

    def register_handler(
        self, action: RemediationAction, handler: Callable
    ):
        """Register a handler function for a remediation action."""
        self._handlers[action] = handler

    def execute_playbook(self, violation_code: str) -> PlaybookResult:
        """Execute the playbook for a given violation."""
        playbook = self.playbooks.get(violation_code)
        if not playbook:
            return PlaybookResult(
                playbook_name="unknown",
                success=False, steps_executed=0, steps_total=0,
                duration_ms=0, details=f"No playbook for {violation_code}",
            )

        start = time.time()
        steps_done = 0

        for step in playbook.steps:
            handler = self._handlers.get(step.action)
            if handler:
                try:
                    handler(step.params)
                    steps_done += 1
                except Exception as e:
                    log.warning(f"Playbook {playbook.name} step failed: {e}")
                    break
            else:
                # No handler = log and skip
                log.info(f"Playbook {playbook.name}: {step.action.value} "
                         f"(no handler, skipping): {step.description}")
                steps_done += 1

        duration = (time.time() - start) * 1000
        success = steps_done == len(playbook.steps)

        # Update learning loop
        if success:
            playbook.success_count += 1
        else:
            playbook.failure_count += 1

        result = PlaybookResult(
            playbook_name=playbook.name,
            success=success,
            steps_executed=steps_done,
            steps_total=len(playbook.steps),
            duration_ms=duration,
        )
        self.execution_log.append(result)
        return result

    def get_success_rates(self) -> Dict[str, float]:
        """Return success rate for each playbook."""
        return {
            code: pb.success_rate
            for code, pb in self.playbooks.items()
        }
