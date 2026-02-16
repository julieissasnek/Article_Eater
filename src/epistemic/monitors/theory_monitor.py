"""
Theory Health Monitor (Sprint 6d / Task 6d.1).

Monitors the health of theoretical propositions in the web,
tracking confirmation/disconfirmation ratios and identifying
theories that may need revision or are gaining support.

Per spec §5.5:
"A theory with many confirmed predictions and few disconfirmations
is gaining entrenchment. A theory with accumulating disconfirmations
is losing it."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5.5
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

from src.epistemic.node_types import NodeType
from src.epistemic.entrenchment.prediction_ledger import PredictionLedger
from src.epistemic.entrenchment.theory_updating import assess_theory_health


class TheoryHealthStatus(str, Enum):
    """Health status of a theory."""
    WELL_SUPPORTED = "well_supported"      # High confirmation rate, stable
    MODERATELY_SUPPORTED = "moderately_supported"
    NEEDS_REVISION = "needs_revision"      # Mixed results, may need refinement
    PROBLEMATIC = "problematic"            # High disconfirmation rate
    UNTESTED = "untested"                  # No empirical tests yet
    SUSPECT = "suspect"                    # High entrenchment but no tests


class TheoryRisk(str, Enum):
    """Risk flags for theories."""
    UNFALSIFIABLE = "unfalsifiable"        # No testable predictions
    OVERENTRENCHED = "overentrenched"      # High entrenchment without evidence
    ACCUMULATING_DISCONFIRMATIONS = "accumulating_disconfirmations"
    SINGLE_LAB_SUPPORT = "single_lab_support"  # All confirmations from one source
    STALE = "stale"                        # No new tests in long time


@dataclass
class TheoryHealthReport:
    """Health report for a single theory."""
    theory_id: str
    theory_text: str
    current_entrenchment: float
    health_status: TheoryHealthStatus
    n_hypotheses: int
    n_confirmations: int
    n_disconfirmations: int
    confirmation_rate: Optional[float]
    risks: List[TheoryRisk] = field(default_factory=list)
    recent_changes: List[str] = field(default_factory=list)
    last_test_date: Optional[datetime] = None
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "theory_id": self.theory_id,
            "theory_text": self.theory_text,
            "current_entrenchment": self.current_entrenchment,
            "health_status": self.health_status.value,
            "n_hypotheses": self.n_hypotheses,
            "n_confirmations": self.n_confirmations,
            "n_disconfirmations": self.n_disconfirmations,
            "confirmation_rate": self.confirmation_rate,
            "risks": [r.value for r in self.risks],
            "recent_changes": self.recent_changes,
            "last_test_date": self.last_test_date.isoformat() if self.last_test_date else None,
            "recommendation": self.recommendation,
        }


@dataclass
class TheoryMonitorSummary:
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
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_theories": self.total_theories,
            "well_supported": self.well_supported,
            "moderately_supported": self.moderately_supported,
            "needs_revision": self.needs_revision,
            "problematic": self.problematic,
            "untested": self.untested,
            "theories_with_risks": self.theories_with_risks,
            "highest_risk_theories": self.highest_risk_theories,
            "most_supported_theories": self.most_supported_theories,
            "generated_at": self.generated_at.isoformat(),
        }


class TheoryMonitor:
    """
    Monitors the health of theoretical propositions.

    Integrates with the prediction ledger to track how well
    theories' predictions are being confirmed or disconfirmed.
    """

    def __init__(self, ledger: Optional[PredictionLedger] = None):
        self._ledger = ledger or PredictionLedger()
        self._theory_cache: Dict[str, TheoryHealthReport] = {}

    def set_ledger(self, ledger: PredictionLedger) -> None:
        """Set the prediction ledger to monitor."""
        self._ledger = ledger
        self._theory_cache.clear()

    def assess_theory(
        self,
        theory_id: str,
        theory_text: str = "",
        current_entrenchment: float = 0.35,
    ) -> TheoryHealthReport:
        """
        Assess the health of a single theory.

        Args:
            theory_id: ID of the theoretical proposition
            theory_text: Text of the theory
            current_entrenchment: Current entrenchment value

        Returns:
            TheoryHealthReport with assessment
        """
        # Get track record from ledger
        track_record = self._ledger.compute_theory_track_record(theory_id)

        n_hypotheses = track_record["hypothesis_count"]
        n_confirmations = track_record["total_confirmations"]
        n_disconfirmations = track_record["total_disconfirmations"]
        confirmation_rate = track_record["success_rate"]

        # Determine health status
        status_str, explanation = assess_theory_health(
            current_entrenchment,
            n_confirmations,
            n_disconfirmations
        )
        health_status = TheoryHealthStatus(status_str)

        # Identify risks
        risks = self._identify_risks(
            theory_id,
            current_entrenchment,
            n_hypotheses,
            n_confirmations,
            n_disconfirmations,
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            health_status, risks, n_hypotheses, n_confirmations, n_disconfirmations
        )

        report = TheoryHealthReport(
            theory_id=theory_id,
            theory_text=theory_text,
            current_entrenchment=current_entrenchment,
            health_status=health_status,
            n_hypotheses=n_hypotheses,
            n_confirmations=n_confirmations,
            n_disconfirmations=n_disconfirmations,
            confirmation_rate=confirmation_rate,
            risks=risks,
            recommendation=recommendation,
        )

        self._theory_cache[theory_id] = report
        return report

    def _identify_risks(
        self,
        theory_id: str,
        entrenchment: float,
        n_hypotheses: int,
        n_confirmations: int,
        n_disconfirmations: int,
    ) -> List[TheoryRisk]:
        """Identify risks for a theory."""
        risks = []

        # Unfalsifiable: high entrenchment but no testable predictions
        if n_hypotheses == 0 and entrenchment > 0.4:
            risks.append(TheoryRisk.UNFALSIFIABLE)

        # Overentrenched: high entrenchment without empirical support
        if entrenchment > 0.6 and n_confirmations == 0:
            risks.append(TheoryRisk.OVERENTRENCHED)

        # Accumulating disconfirmations
        total_tests = n_confirmations + n_disconfirmations
        if total_tests >= 3 and n_disconfirmations >= 2:
            if n_disconfirmations / total_tests > 0.4:
                risks.append(TheoryRisk.ACCUMULATING_DISCONFIRMATIONS)

        # Check for single-source support (would need web access)
        # This is a placeholder - real implementation would check study sources

        return risks

    def _generate_recommendation(
        self,
        status: TheoryHealthStatus,
        risks: List[TheoryRisk],
        n_hypotheses: int,
        n_confirmations: int,
        n_disconfirmations: int,
    ) -> str:
        """Generate a recommendation based on health and risks."""
        if TheoryRisk.UNFALSIFIABLE in risks:
            return "Theory lacks testable predictions. Derive specific hypotheses."

        if TheoryRisk.OVERENTRENCHED in risks:
            return "Theory has high entrenchment without empirical support. Seek confirming studies."

        if TheoryRisk.ACCUMULATING_DISCONFIRMATIONS in risks:
            return "Theory is accumulating disconfirmations. Consider revision or scope restriction."

        if status == TheoryHealthStatus.WELL_SUPPORTED:
            return "Theory is well supported. Continue monitoring for new evidence."

        if status == TheoryHealthStatus.UNTESTED:
            if n_hypotheses > 0:
                return f"Theory has {n_hypotheses} untested hypotheses. Seek empirical tests."
            return "Theory needs testable predictions derived."

        if status == TheoryHealthStatus.NEEDS_REVISION:
            return "Mixed evidence suggests theory may need refinement or scope conditions."

        if status == TheoryHealthStatus.PROBLEMATIC:
            return "Theory has poor track record. Major revision or replacement may be needed."

        return "Monitor for additional evidence."

    def get_summary(self, theory_ids: Optional[List[str]] = None) -> TheoryMonitorSummary:
        """
        Get summary of all monitored theories.

        Args:
            theory_ids: Optional list of theory IDs to include (all if None)

        Returns:
            TheoryMonitorSummary
        """
        if theory_ids is None:
            reports = list(self._theory_cache.values())
        else:
            reports = [self._theory_cache[tid] for tid in theory_ids if tid in self._theory_cache]

        # Count by status
        status_counts = {s: 0 for s in TheoryHealthStatus}
        for r in reports:
            status_counts[r.health_status] += 1

        # Find theories with risks
        with_risks = [r for r in reports if r.risks]

        # Sort by support and risk
        by_support = sorted(
            [r for r in reports if r.confirmation_rate is not None],
            key=lambda r: r.confirmation_rate,
            reverse=True
        )
        by_risk = sorted(
            with_risks,
            key=lambda r: len(r.risks),
            reverse=True
        )

        return TheoryMonitorSummary(
            total_theories=len(reports),
            well_supported=status_counts[TheoryHealthStatus.WELL_SUPPORTED],
            moderately_supported=status_counts[TheoryHealthStatus.MODERATELY_SUPPORTED],
            needs_revision=status_counts[TheoryHealthStatus.NEEDS_REVISION],
            problematic=status_counts[TheoryHealthStatus.PROBLEMATIC],
            untested=status_counts[TheoryHealthStatus.UNTESTED],
            theories_with_risks=len(with_risks),
            highest_risk_theories=[r.theory_id for r in by_risk[:5]],
            most_supported_theories=[r.theory_id for r in by_support[:5]],
        )

    def check_theory_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for theories that need attention.

        Returns:
            List of alert dictionaries
        """
        alerts = []

        for theory_id, report in self._theory_cache.items():
            if report.health_status == TheoryHealthStatus.PROBLEMATIC:
                alerts.append({
                    "type": "problematic_theory",
                    "severity": "high",
                    "theory_id": theory_id,
                    "message": f"Theory '{theory_id}' has problematic track record",
                    "recommendation": report.recommendation,
                })

            if TheoryRisk.ACCUMULATING_DISCONFIRMATIONS in report.risks:
                alerts.append({
                    "type": "accumulating_disconfirmations",
                    "severity": "medium",
                    "theory_id": theory_id,
                    "message": f"Theory '{theory_id}' is accumulating disconfirmations",
                    "disconfirmations": report.n_disconfirmations,
                })

            if TheoryRisk.OVERENTRENCHED in report.risks:
                alerts.append({
                    "type": "overentrenched",
                    "severity": "medium",
                    "theory_id": theory_id,
                    "message": f"Theory '{theory_id}' has high entrenchment without evidence",
                    "entrenchment": report.current_entrenchment,
                })

        return alerts


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_theory_monitor(ledger: Optional[PredictionLedger] = None) -> TheoryMonitor:
    """Create a theory monitor instance."""
    return TheoryMonitor(ledger)


def assess_all_theories(
    theory_data: List[Dict[str, Any]],
    ledger: PredictionLedger,
) -> List[TheoryHealthReport]:
    """
    Assess health of multiple theories.

    Args:
        theory_data: List of dicts with theory_id, theory_text, entrenchment
        ledger: The prediction ledger

    Returns:
        List of TheoryHealthReport
    """
    monitor = TheoryMonitor(ledger)
    reports = []

    for theory in theory_data:
        report = monitor.assess_theory(
            theory_id=theory["theory_id"],
            theory_text=theory.get("theory_text", ""),
            current_entrenchment=theory.get("entrenchment", 0.35),
        )
        reports.append(report)

    return reports
