"""
Methodological Critique Propagation (Sprint 6b / Task 6b.3).

Implements validity penalty propagation from METHODOLOGICAL_CRITIQUEs
to the method registry.

Per spec §4.2:
"METHODOLOGICAL_CRITIQUEs have a PROPAGATION effect. When a critique targets
a method in the method registry, it should reduce the measurement_validity
or presentation_validity score for EVERY claim extracted from studies using
that method."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §4.2, §7.2
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class CritiquePropagationResult:
    """Result of propagating a critique to the method registry."""
    method_id: str
    affected_constructs: List[str]
    original_validity: Dict[str, float]
    new_validity: Dict[str, float]
    penalty_applied: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def constructs_affected_count(self) -> int:
        return len(self.affected_constructs)


def propagate_critique_to_registry(
    critique_target_method_id: str,
    critique_severity: float,
    affected_constructs: List[str],
    registry,  # MethodRegistry - avoiding circular import
    penalty_scale: float = 0.2
) -> Optional[CritiquePropagationResult]:
    """
    Propagate methodological critique to method registry.

    Reduces construct_validity for all affected constructs.
    This is how a single Heft-style ecological validity critique
    can cascade through the web.

    Args:
        critique_target_method_id: ID of the method being critiqued
        critique_severity: Severity of critique [0, 1] where 1 = devastating
        affected_constructs: List of constructs whose validity is affected
        registry: The MethodRegistry to update
        penalty_scale: How much critique_severity maps to validity penalty

    Returns:
        CritiquePropagationResult if method found, None otherwise
    """
    method = registry.get(critique_target_method_id)
    if method is None:
        return None

    # Calculate penalty
    penalty = critique_severity * penalty_scale

    # Record original validity
    original_validity = {}
    new_validity = {}

    for construct in affected_constructs:
        current = method.get_construct_validity(construct)
        original_validity[construct] = current

        # Apply penalty, ensuring validity stays >= 0
        updated = max(0.0, current - penalty)
        new_validity[construct] = updated

        # Update the method's construct validity map
        if hasattr(method, 'construct_validity_map') and method.construct_validity_map is not None:
            method.construct_validity_map[construct] = updated

    return CritiquePropagationResult(
        method_id=critique_target_method_id,
        affected_constructs=affected_constructs,
        original_validity=original_validity,
        new_validity=new_validity,
        penalty_applied=penalty
    )


def compute_cascade_impact(
    critique_target_method_id: str,
    registry,
    web=None  # WebOfBelief - optional
) -> Dict[str, int]:
    """
    Compute how many claims would be affected by a critique.

    Useful for understanding the impact of a methodological critique
    before applying it.

    Args:
        critique_target_method_id: Method being critiqued
        registry: The MethodRegistry
        web: Optional WebOfBelief to count affected claims

    Returns:
        Dict with impact statistics
    """
    method = registry.get(critique_target_method_id)
    if method is None:
        return {"method_found": False, "affected_claims": 0}

    result = {
        "method_found": True,
        "method_id": critique_target_method_id,
        "constructs_in_map": len(method.construct_validity_map) if method.construct_validity_map else 0,
    }

    # If we have a web, count affected claims
    if web is not None:
        # This would require iterating claims and checking their methods
        # Placeholder for now
        result["affected_claims"] = 0
        result["note"] = "Claim counting not implemented"

    return result


def record_critique_in_registry(
    critique_target_method_id: str,
    critique_description: str,
    registry,
    severity: float = 0.5
) -> bool:
    """
    Record a critique in the method's confounds list.

    Per spec §7.2:
    "When a critique targets a specific method, the method's
    confounds list should be updated."

    Args:
        critique_target_method_id: Method being critiqued
        critique_description: Description of the methodological problem
        registry: The MethodRegistry
        severity: Severity of the critique [0, 1]

    Returns:
        True if recorded, False if method not found
    """
    method = registry.get(critique_target_method_id)
    if method is None:
        return False

    # Add to confounds if the field exists
    if hasattr(method, 'confounds') and method.confounds is not None:
        # Format: "CRITIQUE: description (severity: X.X)"
        critique_entry = f"CRITIQUE: {critique_description} (severity: {severity:.2f})"
        if critique_entry not in method.confounds:
            method.confounds.append(critique_entry)

    return True


def suggest_alternative_method(
    critique_target_method_id: str,
    proposed_alternative_id: str,
    registry
) -> bool:
    """
    Record a proposed better method in response to critique.

    Per spec §7.2:
    "When a critique proposes a better method, the registry
    should note the recommended alternative."

    Args:
        critique_target_method_id: Method being critiqued
        proposed_alternative_id: ID of proposed better method
        registry: The MethodRegistry

    Returns:
        True if recorded, False if either method not found
    """
    critiqued = registry.get(critique_target_method_id)
    alternative = registry.get(proposed_alternative_id)

    if critiqued is None or alternative is None:
        return False

    # Record the alternative (implementation depends on registry structure)
    # For now, add as a confound note
    if hasattr(critiqued, 'confounds') and critiqued.confounds is not None:
        note = f"ALTERNATIVE: Consider using {proposed_alternative_id} instead"
        if note not in critiqued.confounds:
            critiqued.confounds.append(note)

    return True
