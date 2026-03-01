"""
Overseer Self-Healing Engine (Phase 4)
=======================================

Autonomous self-healing loop that:
1. DETECT:  Overseer finds violations via check_integrity()
2. DIAGNOSE: Classifies root cause and selects playbook
3. REMEDIATE: Executes playbook with concrete handler implementations
4. VERIFY:  Re-checks invariants to confirm healing

Also supports PREDICTIVE healing: uses PredictiveHealthEngine to
act before violations actually occur.

References:
- Dijkstra (1968): "THE" Multiprogramming — layered invariant guards
- Pearl (1988): Bayesian Networks — probabilistic forecast of system health
- Winograd & Flores (1986): breakdown/repair — computers as contexts for action

Usage:
    from src.services.overseer_self_healing import SelfHealingOverseer
    healer = SelfHealingOverseer(overseer_service)
    report = healer.heal()  # Full detect→diagnose→remediate→verify cycle
"""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.services.overseer_playbooks import (
    RemediationAction,
    RemediationEngine,
    PlaybookResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Healing Report
# =============================================================================

@dataclass
class HealingReport:
    """Report from a self-healing cycle."""
    timestamp: str
    violations_detected: int
    violations_healed: int
    violations_deferred: int
    playbook_results: List[Dict]
    predictive_actions: List[Dict]
    post_healing_violations: int
    healing_success: bool
    duration_ms: float
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "violations_detected": self.violations_detected,
            "violations_healed": self.violations_healed,
            "violations_deferred": self.violations_deferred,
            "playbook_results": self.playbook_results,
            "predictive_actions": self.predictive_actions,
            "post_healing_violations": self.post_healing_violations,
            "healing_success": self.healing_success,
            "duration_ms": self.duration_ms,
            "notes": self.notes,
        }


# =============================================================================
# Concrete Action Handlers
# =============================================================================

class ActionHandlers:
    """Concrete implementations of remediation actions.
    
    Each handler is a callable(params: Dict) that performs
    a specific corrective action on the system.
    """

    def __init__(self, overseer):
        self.overseer = overseer
        self.web = overseer.web
        self.web_db_path = overseer.web_db_path
        self.templates_dir = overseer.templates_dir
        self.extractions_dir = overseer.extractions_dir

    def quarantine_beliefs(self, params: Dict) -> None:
        """Quarantine recently added beliefs that may have caused violations."""
        lookback_hours = params.get("lookback_hours", 24)
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()
        
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Find recently added beliefs
                cursor.execute(
                    "SELECT belief_id FROM belief_versions "
                    "WHERE created_at > ? AND status != 'quarantined' "
                    "ORDER BY created_at DESC LIMIT 50",
                    (cutoff,)
                )
                recent = [row[0] for row in cursor.fetchall()]
                
                if recent:
                    for bid in recent:
                        self.overseer.quarantine_belief(
                            bid, f"Auto-quarantine: lookback {lookback_hours}h"
                        )
                    logger.info(f"Quarantined {len(recent)} recent beliefs")
                else:
                    logger.info("No recent beliefs to quarantine")
        except Exception as e:
            logger.warning(f"Quarantine failed: {e}")

    def recompute_coherence(self, params: Dict) -> None:
        """Recompute global and per-theory coherence scores."""
        try:
            if self.web and hasattr(self.web, 'recompute_coherence'):
                self.web.recompute_coherence()
                logger.info("Coherence recomputed")
            elif self.web and hasattr(self.web, 'coherence_score'):
                # Trigger read (some implementations cache on read)
                _ = self.web.coherence_score()
                logger.info("Coherence score refreshed")
            else:
                logger.info("No coherence recomputation method available (graceful skip)")
        except Exception as e:
            logger.warning(f"Coherence recomputation failed: {e}")

    def rebuild_constraints(self, params: Dict) -> None:
        """Rebuild constraint graph for orphan or damaged beliefs."""
        target = params.get("target", "all")
        try:
            if self.web and hasattr(self.web, 'rebuild_constraints'):
                if target == "orphans_only":
                    self.web.rebuild_constraints(orphans_only=True)
                else:
                    self.web.rebuild_constraints()
                logger.info(f"Constraints rebuilt (target={target})")
            else:
                logger.info("No constraint rebuild method available (graceful skip)")
        except Exception as e:
            logger.warning(f"Constraint rebuild failed: {e}")

    def rerun_pipeline(self, params: Dict) -> None:
        """Re-run a pipeline stage.
        
        In self-healing mode, this means re-registering stale/failed
        pipelines for re-execution rather than blocking on execution.
        """
        pipeline = params.get("pipeline", "integration")
        try:
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE pipeline_registry SET last_status = 'pending_rerun' "
                    "WHERE pipeline_id LIKE ? AND last_status IN ('failed', 'stale')",
                    (f"%{pipeline}%",)
                )
                updated = cursor.rowcount
                conn.commit()
                logger.info(f"Marked {updated} pipelines for rerun (target={pipeline})")
        except Exception as e:
            logger.warning(f"Pipeline rerun scheduling failed: {e}")

    def adjust_thresholds(self, params: Dict) -> None:
        """Adjust tolerance thresholds in overseer config.
        
        Records the adjustment in overseer.db for audit trail
        and automatic rollback after 48 hours.
        """
        threshold_key = params.get("threshold_key", "")
        delta = params.get("delta", 0)
        alpha_factor = params.get("alpha_factor")
        beta_factor = params.get("beta_factor")
        
        try:
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                # Ensure table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS threshold_adjustments (
                        threshold_key TEXT PRIMARY KEY,
                        delta REAL,
                        alpha_factor REAL,
                        beta_factor REAL,
                        adjusted_at TEXT,
                        rollback_at TEXT
                    )
                """)
                # Record threshold adjustment
                cursor.execute("""
                    INSERT OR REPLACE INTO threshold_adjustments 
                    (threshold_key, delta, alpha_factor, beta_factor,
                     adjusted_at, rollback_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    threshold_key, delta, alpha_factor, beta_factor,
                    datetime.now(timezone.utc).isoformat(),
                    (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat(),
                ))
                conn.commit()
                logger.info(
                    f"Threshold adjustment recorded: {threshold_key} "
                    f"delta={delta} alpha={alpha_factor} beta={beta_factor}"
                )
        except Exception as e:
            logger.warning(f"Threshold adjustment failed: {e}")

    def regenerate_templates(self, params: Dict) -> None:
        """Regenerate template-belief or template-theory mappings.
        
        This triggers re-scanning templates for theory links
        and re-mapping beliefs to templates.
        """
        try:
            # Count templates needing regeneration
            template_count = len(list(self.templates_dir.glob("*.json")))
            logger.info(f"Template regeneration requested for {template_count} templates")
            
            # Mark templates as needing refresh in overseer.db
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS maintenance_queue (
                        task_id TEXT PRIMARY KEY,
                        task_type TEXT,
                        status TEXT,
                        created_at TEXT
                    )
                """)
                cursor.execute("""
                    INSERT OR REPLACE INTO maintenance_queue 
                    (task_id, task_type, status, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    "regenerate_templates",
                    "template_refresh",
                    "pending",
                    datetime.now(timezone.utc).isoformat(),
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Template regeneration scheduling failed: {e}")

    def rollback_last_integration(self, params: Dict) -> None:
        """Rollback the most recent paper integration.
        
        Quarantines all beliefs created in the last integration event
        and logs the rollback for human review.
        """
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                # Find the most recent integration batch
                cursor.execute(
                    "SELECT belief_id, created_at FROM belief_versions "
                    "ORDER BY created_at DESC LIMIT 1"
                )
                latest = cursor.fetchone()
                if not latest:
                    logger.info("No beliefs to rollback")
                    return
                
                latest_time = latest[1]
                # Find all beliefs in the same integration window (±60s)
                cursor.execute(
                    "SELECT belief_id FROM belief_versions "
                    "WHERE created_at >= datetime(?, '-60 seconds') "
                    "AND created_at <= datetime(?, '+60 seconds')",
                    (latest_time, latest_time)
                )
                batch = [row[0] for row in cursor.fetchall()]
                
                for bid in batch:
                    self.overseer.quarantine_belief(
                        bid, "Auto-rollback: last integration"
                    )
                logger.info(f"Rolled back {len(batch)} beliefs from last integration")
        except Exception as e:
            logger.warning(f"Rollback failed: {e}")

    def notify_human(self, params: Dict) -> None:
        """Create a human notification record.
        
        In the real system this would send email/Slack.
        Here we log to overseer.db for dashboard display.
        """
        try:
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS human_notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT,
                        severity TEXT,
                        created_at TEXT,
                        acknowledged_at TEXT
                    )
                """)
                cursor.execute(
                    "INSERT INTO human_notifications (message, severity, created_at) "
                    "VALUES (?, ?, ?)",
                    (
                        params.get("message", "Self-healing action requires review"),
                        params.get("severity", "warning"),
                        datetime.now(timezone.utc).isoformat(),
                    )
                )
                conn.commit()
                logger.info("Human notification created")
        except Exception as e:
            logger.warning(f"Human notification failed: {e}")


# =============================================================================
# Self-Healing Overseer
# =============================================================================

class SelfHealingOverseer:
    """
    Autonomous self-healing loop for the Overseer system.
    
    Wires together:
    - OverseerService (detection)
    - RemediationEngine (playbook execution)
    - ActionHandlers (concrete implementations)
    - PredictiveHealthEngine (predictive pre-emption)
    
    Usage:
        from src.services.overseer import OverseerService
        overseer = OverseerService(...)
        healer = SelfHealingOverseer(overseer)
        report = healer.heal()
    """

    # Violations that can be auto-healed without human approval
    AUTO_HEAL_CODES = {"INV-1", "INV-2", "INV-4", "INV-6", "INV-7", "INV-8", "INV-9"}
    
    # Violations that require human approval first
    HUMAN_APPROVAL_CODES = {"INV-0", "INV-5"}
    
    # Maximum healing attempts per cycle
    MAX_ATTEMPTS = 3

    def __init__(self, overseer, enable_predictive: bool = True):
        self.overseer = overseer
        self.engine = RemediationEngine()
        self.handlers = ActionHandlers(overseer)
        self.enable_predictive = enable_predictive
        
        # Register all concrete handlers
        self._register_handlers()
        
        # History for learning loop
        self.healing_history: List[HealingReport] = []

    def _register_handlers(self) -> None:
        """Register concrete handler functions for each remediation action."""
        handler_map = {
            RemediationAction.QUARANTINE_BELIEFS: self.handlers.quarantine_beliefs,
            RemediationAction.RECOMPUTE_COHERENCE: self.handlers.recompute_coherence,
            RemediationAction.REBUILD_CONSTRAINTS: self.handlers.rebuild_constraints,
            RemediationAction.RERUN_PIPELINE: self.handlers.rerun_pipeline,
            RemediationAction.ADJUST_THRESHOLDS: self.handlers.adjust_thresholds,
            RemediationAction.REGENERATE_TEMPLATES: self.handlers.regenerate_templates,
            RemediationAction.ROLLBACK_LAST_INTEGRATION: self.handlers.rollback_last_integration,
            RemediationAction.NOTIFY_HUMAN: self.handlers.notify_human,
        }
        for action, handler in handler_map.items():
            self.engine.register_handler(action, handler)

    def heal(self) -> HealingReport:
        """
        Full self-healing cycle: detect → diagnose → remediate → verify.
        
        Returns HealingReport with complete audit trail.
        """
        start = time.time()
        notes = []
        playbook_results = []
        predictive_actions = []
        
        # ── PHASE 1: DETECT ──────────────────────────────────
        violations = self.overseer.check_integrity()
        n_detected = len(violations)
        notes.append(f"Detected {n_detected} violations")
        
        # ── PHASE 2: PREDICTIVE PRE-EMPTION ──────────────────
        if self.enable_predictive:
            try:
                from src.services.overseer_predictive import PredictiveHealthEngine
                predictor = PredictiveHealthEngine(overseer=self.overseer)
                
                # Get health history
                health_history = self._get_health_history()
                if len(health_history) >= 3:
                    prediction = predictor.predict_health(health_history)
                    
                    # Pre-emptive action if AESHI is declining
                    if (prediction.trend_direction == "declining" and 
                        prediction.predicted_aeshi < 0.6):
                        for action_name in prediction.recommended_actions:
                            predictive_actions.append({
                                "action": action_name,
                                "reason": f"Predictive: AESHI trending to {prediction.predicted_aeshi:.2f}",
                                "confidence": prediction.confidence,
                            })
                            notes.append(f"Predictive action: {action_name}")
                    
                    # Pattern detection
                    patterns = predictor.detect_patterns(health_history)
                    for pattern in patterns:
                        if pattern.severity in ("warning", "critical"):
                            notes.append(f"Pattern detected: {pattern.description}")
            except Exception as e:
                notes.append(f"Predictive engine unavailable: {e}")
        
        # ── PHASE 3: DIAGNOSE & REMEDIATE ────────────────────
        healed = 0
        deferred = 0
        
        for violation in violations:
            code = violation.code
            
            # Check if auto-healable
            if code in self.HUMAN_APPROVAL_CODES:
                # Defer to human
                self.handlers.notify_human({
                    "message": f"{code}: {violation.description}",
                    "severity": violation.severity,
                })
                deferred += 1
                notes.append(f"Deferred {code} to human review")
                continue
            
            # Execute playbook
            result = self.engine.execute_playbook(code)
            playbook_results.append({
                "violation_code": code,
                "playbook_name": result.playbook_name,
                "success": result.success,
                "steps_executed": result.steps_executed,
                "steps_total": result.steps_total,
                "duration_ms": result.duration_ms,
            })
            
            if result.success:
                healed += 1
                notes.append(f"Healed {code} via {result.playbook_name}")
            else:
                notes.append(f"Failed to heal {code}: {result.details}")
        
        # ── PHASE 4: VERIFY ──────────────────────────────────
        post_violations = self.overseer.check_integrity()
        n_post = len(post_violations)
        
        healing_success = n_post < n_detected
        notes.append(f"Post-healing: {n_post} violations (was {n_detected})")
        
        # Record
        duration_ms = (time.time() - start) * 1000
        report = HealingReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            violations_detected=n_detected,
            violations_healed=healed,
            violations_deferred=deferred,
            playbook_results=playbook_results,
            predictive_actions=predictive_actions,
            post_healing_violations=n_post,
            healing_success=healing_success,
            duration_ms=duration_ms,
            notes=notes,
        )
        
        self.healing_history.append(report)
        self._persist_report(report)
        
        return report

    def heal_specific(self, violation_code: str) -> PlaybookResult:
        """Heal a specific violation by code."""
        return self.engine.execute_playbook(violation_code)

    def rollback_adjustments(self) -> int:
        """Rollback any expired threshold adjustments."""
        rolled_back = 0
        try:
            now = datetime.now(timezone.utc).isoformat()
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT threshold_key FROM threshold_adjustments "
                    "WHERE rollback_at < ?",
                    (now,)
                )
                expired = [row[0] for row in cursor.fetchall()]
                if expired:
                    cursor.execute(
                        "DELETE FROM threshold_adjustments WHERE rollback_at < ?",
                        (now,)
                    )
                    conn.commit()
                    rolled_back = len(expired)
                    logger.info(f"Rolled back {rolled_back} expired adjustments")
        except Exception as e:
            logger.debug(f"Rollback check skipped: {e}")
        return rolled_back

    def get_success_rates(self) -> Dict[str, float]:
        """Get success rates for each playbook."""
        return self.engine.get_success_rates()

    def get_healing_summary(self) -> Dict[str, Any]:
        """Get summary of all healing cycles."""
        if not self.healing_history:
            return {"total_cycles": 0}
        
        total = len(self.healing_history)
        successes = sum(1 for r in self.healing_history if r.healing_success)
        total_healed = sum(r.violations_healed for r in self.healing_history)
        total_deferred = sum(r.violations_deferred for r in self.healing_history)
        
        return {
            "total_cycles": total,
            "success_rate": successes / total if total > 0 else 0.0,
            "total_violations_healed": total_healed,
            "total_violations_deferred": total_deferred,
            "playbook_success_rates": self.get_success_rates(),
            "last_cycle": self.healing_history[-1].to_dict(),
        }

    # ── Helpers ──────────────────────────────────────────────

    def _get_health_history(self) -> List[Dict]:
        """Load health metric history from overseer.db."""
        try:
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM overseer_health_metrics "
                    "ORDER BY timestamp DESC LIMIT 30"
                )
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in reversed(rows)]
        except Exception as e:
            logger.debug(f"Health history unavailable: {e}")
            return []

    def _persist_report(self, report: HealingReport) -> None:
        """Persist healing report to overseer.db."""
        try:
            with self.overseer._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS healing_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        violations_detected INTEGER,
                        violations_healed INTEGER,
                        violations_deferred INTEGER,
                        post_healing_violations INTEGER,
                        healing_success INTEGER,
                        duration_ms REAL,
                        report_json TEXT
                    )
                """)
                cursor.execute(
                    "INSERT INTO healing_reports "
                    "(timestamp, violations_detected, violations_healed, "
                    "violations_deferred, post_healing_violations, "
                    "healing_success, duration_ms, report_json) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        report.timestamp,
                        report.violations_detected,
                        report.violations_healed,
                        report.violations_deferred,
                        report.post_healing_violations,
                        1 if report.healing_success else 0,
                        report.duration_ms,
                        json.dumps(report.to_dict()),
                    )
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to persist healing report: {e}")


# =============================================================================
# CLI entry point
# =============================================================================

def run_self_healing(
    overseer_db: str = "data/overseer.db",
    web_db: str = "data/web.db",
) -> HealingReport:
    """Convenience function to run a self-healing cycle."""
    from src.services.overseer import OverseerService
    
    overseer = OverseerService(
        overseer_db_path=overseer_db,
        web=None,
        web_db_path=web_db,
    )
    healer = SelfHealingOverseer(overseer)
    return healer.heal()


if __name__ == "__main__":
    import sys
    report = run_self_healing()
    print(json.dumps(report.to_dict(), indent=2))
