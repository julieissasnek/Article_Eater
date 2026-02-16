"""
BN Coherence Client (ARCH-4 Integration).

Provides Article_Eater with access to BN_graphical's coherence module for:
- Belief validation before integration
- Conflict detection with existing beliefs
- Rank calibration checking
- Format conversion (v1 ↔ v2)

This module acts as a client to BN_graphical's coherence services,
allowing AE to validate beliefs before adding them to the Web of Belief.

Usage:
    >>> from services.bn_coherence_client import BNCoherenceClient
    >>> client = BNCoherenceClient()
    >>> result = client.validate_beliefs(new_beliefs, existing_web_state)
    >>> if result.has_conflicts:
    ...     for conflict in result.conflicts:
    ...         handle_conflict(conflict)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Add BN_graphical to path for direct import
BN_GRAPHICAL_PATH = Path(__file__).parent.parent.parent.parent / "BN_graphical" / "src"
if BN_GRAPHICAL_PATH.exists():
    sys.path.insert(0, str(BN_GRAPHICAL_PATH))

try:
    from coherence import (
        # Sprint 4: Adapter
        EpistemicAdapter,
        DualEpistemicStatus,
        FormatVersion,
        WarrantStatus,
        get_adapter,
        # Sprint 5: Conflict Handler
        BeliefConflictHandler,
        BeliefConflict,
        ConflictResolution,
        ConflictType,
        ConflictSeverity,
        ResolutionStrategy,
        # Sprint 6: Calibrator
        RankCalibrator,
        CalibrationReport,
        InvariantViolation,
        InvariantType,
        ViolationSeverity,
        # Sprint 7: Workflow
        EpistemicWorkflow,
        WorkflowResult,
        WorkflowConfig,
        WorkflowStatus,
        ProcessingPhase,
        # Sprint 8: Validation
        BeliefValidationError,
        validate_belief,
        validate_belief_batch
    )
    BN_AVAILABLE = True
except ImportError as e:
    BN_AVAILABLE = False
    _import_error = str(e)

logger = logging.getLogger(__name__)


class CoherenceCheckStatus(str, Enum):
    """Status of coherence check."""
    PASSED = "passed"
    WARNING = "warning"
    CONFLICT = "conflict"
    CALIBRATION_ERROR = "calibration_error"
    FAILED = "failed"
    BN_UNAVAILABLE = "bn_unavailable"


@dataclass
class CoherenceCheckResult:
    """
    Result from BN coherence check.

    Attributes:
        status: Overall check status
        conflicts: List of detected conflicts
        resolutions: Suggested conflict resolutions
        calibration_issues: Rank calibration violations
        recommended_actions: Prioritized actions to take
        processed_beliefs: Beliefs with dual epistemic status
        errors: Any errors encountered
    """
    status: CoherenceCheckStatus
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    resolutions: List[Dict[str, Any]] = field(default_factory=list)
    calibration_issues: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    processed_beliefs: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def has_calibration_issues(self) -> bool:
        return len(self.calibration_issues) > 0

    @property
    def is_clean(self) -> bool:
        return self.status == CoherenceCheckStatus.PASSED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "conflicts": self.conflicts,
            "resolutions": self.resolutions,
            "calibration_issues": self.calibration_issues,
            "recommended_actions": self.recommended_actions,
            "processed_beliefs": self.processed_beliefs,
            "errors": self.errors
        }


class BNCoherenceClient:
    """
    Client for BN_graphical coherence services.

    Provides Article_Eater with access to belief validation,
    conflict detection, and rank calibration from BN_graphical.

    Usage:
        >>> client = BNCoherenceClient()
        >>> if client.is_available:
        ...     result = client.validate_beliefs(beliefs, existing)
        ...     if result.has_conflicts:
        ...         # Handle conflicts before integration
    """

    def __init__(
        self,
        output_format: str = "dual",
        run_calibration: bool = True,
        detect_conflicts: bool = True,
        resolve_conflicts: bool = True,
        incoherence_threshold: float = 0.3
    ):
        """
        Initialize the coherence client.

        Args:
            output_format: Output format ("v1", "v2", or "dual")
            run_calibration: Whether to run rank calibration
            detect_conflicts: Whether to detect conflicts
            resolve_conflicts: Whether to generate resolutions
            incoherence_threshold: Threshold for conflict detection
        """
        self._bn_available = BN_AVAILABLE
        self._workflow = None
        self._adapter = None

        if self._bn_available:
            # Map format string to enum
            format_map = {
                "v1": FormatVersion.V1,
                "v2": FormatVersion.V2,
                "dual": FormatVersion.DUAL
            }
            fmt = format_map.get(output_format, FormatVersion.DUAL)

            config = WorkflowConfig(
                output_format=fmt,
                run_calibration=run_calibration,
                detect_conflicts=detect_conflicts,
                resolve_conflicts=resolve_conflicts,
                incoherence_threshold=incoherence_threshold
            )
            self._workflow = EpistemicWorkflow(config)
            self._adapter = get_adapter()
            logger.info("BN coherence client initialized successfully")
        else:
            logger.warning(f"BN_graphical not available: {_import_error}")

    @property
    def is_available(self) -> bool:
        """Check if BN coherence services are available."""
        return self._bn_available

    def validate_beliefs(
        self,
        beliefs: List[Dict[str, Any]],
        existing_beliefs: Optional[Dict[str, Dict[str, Any]]] = None,
        support_relations: Optional[List[Tuple[str, str, int]]] = None,
        contradiction_pairs: Optional[List[Tuple[str, str]]] = None
    ) -> CoherenceCheckResult:
        """
        Validate beliefs through BN coherence pipeline.

        Args:
            beliefs: New beliefs to validate
            existing_beliefs: Existing beliefs to check against
            support_relations: Support relations for calibration
            contradiction_pairs: Known contradiction pairs

        Returns:
            CoherenceCheckResult with validation outcomes
        """
        if not self._bn_available:
            return CoherenceCheckResult(
                status=CoherenceCheckStatus.BN_UNAVAILABLE,
                errors=["BN_graphical coherence module not available"]
            )

        try:
            # Run through BN workflow
            result = self._workflow.process_beliefs(
                beliefs,
                existing_beliefs,
                support_relations,
                contradiction_pairs
            )

            # Map BN status to our status
            status_map = {
                WorkflowStatus.SUCCESS: CoherenceCheckStatus.PASSED,
                WorkflowStatus.WARNING: CoherenceCheckStatus.WARNING,
                WorkflowStatus.CONFLICT: CoherenceCheckStatus.CONFLICT,
                WorkflowStatus.CALIBRATION_ERROR: CoherenceCheckStatus.CALIBRATION_ERROR,
                WorkflowStatus.FAILED: CoherenceCheckStatus.FAILED
            }

            # Convert conflicts to dicts
            conflicts = [c.to_dict() for c in result.conflicts]
            resolutions = [r.to_dict() for r in result.resolutions]

            # Convert calibration issues
            calibration_issues = []
            if result.calibration_report:
                for v in result.calibration_report.violations:
                    calibration_issues.append({
                        "type": v.invariant.value if hasattr(v.invariant, 'value') else str(v.invariant),
                        "severity": v.severity.value if hasattr(v.severity, 'value') else str(v.severity),
                        "description": v.description,
                        "suggested_fix": v.suggested_fix,
                        "belief_ids": v.belief_ids
                    })

            return CoherenceCheckResult(
                status=status_map.get(result.overall_status, CoherenceCheckStatus.FAILED),
                conflicts=conflicts,
                resolutions=resolutions,
                calibration_issues=calibration_issues,
                recommended_actions=result.recommended_actions,
                processed_beliefs=result.processed_beliefs,
                errors=result.errors
            )

        except Exception as e:
            logger.exception(f"Coherence validation failed: {e}")
            return CoherenceCheckResult(
                status=CoherenceCheckStatus.FAILED,
                errors=[str(e)]
            )

    def convert_belief_format(
        self,
        belief: Dict[str, Any],
        target_format: str = "dual"
    ) -> Dict[str, Any]:
        """
        Convert belief to specified epistemic format.

        Args:
            belief: Belief dict in any format
            target_format: Target format ("v1", "v2", or "dual")

        Returns:
            Belief dict in target format
        """
        if not self._bn_available:
            return belief

        try:
            status = self._adapter.parse_ae_belief(belief)

            format_map = {
                "v1": FormatVersion.V1,
                "v2": FormatVersion.V2,
                "dual": FormatVersion.DUAL
            }
            fmt = format_map.get(target_format, FormatVersion.DUAL)

            exported = self._adapter.export_belief(status, fmt)
            return {**belief, **exported}

        except Exception as e:
            logger.warning(f"Format conversion failed for {belief.get('belief_id')}: {e}")
            return belief

    def check_single_belief(
        self,
        belief: Dict[str, Any],
        existing_beliefs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> CoherenceCheckResult:
        """
        Convenience method to check a single belief.

        Args:
            belief: Single belief to validate
            existing_beliefs: Existing beliefs to check against

        Returns:
            CoherenceCheckResult
        """
        return self.validate_beliefs([belief], existing_beliefs)

    def get_conflict_severity(self, conflict: Dict[str, Any]) -> str:
        """Get severity level of a conflict."""
        return conflict.get("severity", "unknown")

    def get_resolution_strategy(self, resolution: Dict[str, Any]) -> str:
        """Get recommended strategy for a resolution."""
        return resolution.get("strategy", "unknown")


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def check_beliefs_coherence(
    beliefs: List[Dict[str, Any]],
    existing_beliefs: Optional[Dict[str, Dict[str, Any]]] = None
) -> CoherenceCheckResult:
    """
    Convenience function to check beliefs through BN coherence.

    Args:
        beliefs: Beliefs to validate
        existing_beliefs: Existing beliefs to check against

    Returns:
        CoherenceCheckResult
    """
    client = BNCoherenceClient()
    return client.validate_beliefs(beliefs, existing_beliefs)


def convert_to_dual_format(belief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert belief to dual epistemic format.

    Args:
        belief: Belief in any format

    Returns:
        Belief with both v1 and v2 status
    """
    client = BNCoherenceClient()
    return client.convert_belief_format(belief, "dual")


# ============================================================
# WEB OF BELIEF INTEGRATION HOOKS
# ============================================================

def pre_integration_check(
    new_beliefs: List[Dict[str, Any]],
    web_state: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], CoherenceCheckResult]:
    """
    Pre-integration hook for WebOfBelief.add_belief().

    Call this before integrating beliefs into the web to:
    1. Detect conflicts with existing beliefs
    2. Check rank calibration
    3. Convert to dual format

    Args:
        new_beliefs: Beliefs about to be integrated
        web_state: Current web state (from web.to_dict() or similar)

    Returns:
        Tuple of (processed_beliefs, check_result)
    """
    # Extract existing beliefs from web state
    existing_beliefs = {}
    if "beliefs" in web_state:
        for belief in web_state["beliefs"]:
            bid = belief.get("belief_id")
            if bid:
                existing_beliefs[bid] = belief

    # Extract support relations from constraints
    support_relations = []
    contradiction_pairs = []

    if "constraints" in web_state:
        for constraint in web_state["constraints"]:
            ctype = constraint.get("constraint_type", "")
            source = constraint.get("source_id")
            target = constraint.get("target_id")

            if source and target:
                if ctype == "SUPPORTS":
                    # Default penalty of 1 for support
                    support_relations.append((source, target, 1))
                elif ctype == "CONTRADICTS":
                    contradiction_pairs.append((source, target))

    # Run coherence check
    client = BNCoherenceClient()
    result = client.validate_beliefs(
        new_beliefs,
        existing_beliefs,
        support_relations,
        contradiction_pairs
    )

    # Return processed beliefs with dual format
    processed = result.processed_beliefs if result.processed_beliefs else new_beliefs

    return processed, result


def should_integrate_belief(
    belief: Dict[str, Any],
    check_result: CoherenceCheckResult,
    allow_conflicts: bool = False,
    allow_calibration_errors: bool = True
) -> Tuple[bool, str]:
    """
    Determine if a belief should be integrated based on coherence check.

    Args:
        belief: The belief being considered
        check_result: Result from coherence check
        allow_conflicts: Whether to allow beliefs with conflicts
        allow_calibration_errors: Whether to allow calibration errors

    Returns:
        Tuple of (should_integrate, reason)
    """
    belief_id = belief.get("belief_id", "unknown")

    if check_result.status == CoherenceCheckStatus.BN_UNAVAILABLE:
        # BN not available - integrate anyway with warning
        return True, "BN coherence unavailable, proceeding with integration"

    if check_result.status == CoherenceCheckStatus.FAILED:
        return False, f"Coherence check failed: {check_result.errors}"

    # Check for conflicts involving this belief
    if not allow_conflicts:
        for conflict in check_result.conflicts:
            if belief_id in [conflict.get("prediction_id"), conflict.get("ae_belief_id")]:
                severity = conflict.get("severity", "unknown")
                if severity in ["critical", "major"]:
                    return False, f"Critical/major conflict detected: {conflict.get('conflict_id')}"

    # Check for calibration errors involving this belief
    if not allow_calibration_errors:
        for issue in check_result.calibration_issues:
            if belief_id in issue.get("belief_ids", []):
                if issue.get("severity") == "error":
                    return False, f"Calibration error: {issue.get('description')}"

    return True, "Passed coherence checks"
