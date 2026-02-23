"""
Article Eater - Model Abstraction Levels
=========================================

Handles the continuum of model complexity from simple to full.

The full Quinean web is too complex to always compute. We need the ability
to operate at different levels of abstraction:

LEVEL 0 (Flat): Just findings, no theory structure
LEVEL 1 (Domain): CNFA findings + CNFA theories (ART, SRT, etc.)
LEVEL 2 (Grounded): Level 1 + supporting theories from other domains
LEVEL 3 (Full): Complete web including criterial rules

At each level, we treat "lower" levels as fixed background and only
compute updates within the current level.

Key Concepts:

1. BACKGROUND FIXING
   - Some beliefs are held fixed during a computation
   - They provide evidential support but aren't updated
   - This is a pragmatic choice, not a metaphysical one

2. MODEL ZOOM
   - Start at a coarse level
   - If anomalies accumulate, zoom in to finer level
   - If coherence is high, zoom out to coarser level

3. CRITERIAL RULES
   - Constitutive claims that define measurement
   - "This device measures heart rate"
   - Almost semantic, very weakly empirical
   - Extremely high entrenchment
   - Revision invalidates large amounts of evidence

4. THEORY NESTING
   - CNFA theories are supported by deeper theories
   - SRT depends on stress physiology
   - ART depends on attention mechanisms
   - Evidence for deeper theory propagates to nested theories

Philosophical Background:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism.
- Wittgenstein, L. (1969). On Certainty. — "hinge propositions"
- Kuhn, T. (1962). Structure of Scientific Revolutions. — paradigms as background
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ABSTRACTION LEVELS
# =============================================================================

class AbstractionLevel(Enum):
    """Levels of model abstraction."""
    FLAT = 0       # Just findings, no theory structure
    DOMAIN = 1     # Domain theories (ART, SRT, etc.)
    GROUNDED = 2   # + supporting theories from other domains
    FULL = 3       # Complete web including criterial rules


class BeliefRole(Enum):
    """Role of a belief at a given abstraction level."""
    ACTIVE = "active"           # Subject to update
    BACKGROUND = "background"   # Fixed, provides support
    CRITERIAL = "criterial"     # Constitutive, almost semantic
    EXCLUDED = "excluded"       # Not relevant at this level


# =============================================================================
# CRITERIAL RULES
# =============================================================================

@dataclass
class CriterialRule:
    """
    A constitutive rule that defines what counts as measurement/observation.
    
    These are "hinge propositions" (Wittgenstein) — they're not ordinary
    empirical claims but preconditions for empirical inquiry.
    
    Examples:
    - "EEG measures cortical electrical activity"
    - "Salivary cortisol reflects HPA axis activation"
    - "Self-report scales measure subjective experience"
    
    Revising a criterial rule invalidates all evidence that depends on it.
    """
    rule_id: str
    content: str
    
    # What measurement/observation does this constitute?
    constitutes: str  # e.g., "cortisol_measurement"
    
    # What evidence depends on this rule?
    dependent_evidence: List[str] = field(default_factory=list)
    
    # Domain of application
    domain: str = ""
    
    # Even criterial rules have some (very small) revisability
    # This is not credence but resistance to revision
    entrenchment: float = 0.99
    
    def invalidation_cost(self) -> int:
        """How much would be invalidated if we revised this?"""
        return len(self.dependent_evidence)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'content': self.content,
            'constitutes': self.constitutes,
            'n_dependent': len(self.dependent_evidence),
            'entrenchment': self.entrenchment
        }


# =============================================================================
# THEORY NESTING
# =============================================================================

@dataclass
class TheoryDependency:
    """
    A dependency relationship between theories.
    
    When theory A depends on theory B, evidence for B provides
    indirect support for A. Conversely, if B is refuted, A loses
    its grounding.
    
    Example: SRT depends on stress_physiology
    - Evidence that cortisol reflects stress supports SRT's mechanism
    - If stress physiology were refuted, SRT would lose its foundation
    """
    dependency_id: str
    dependent_theory: str      # The theory that depends (e.g., SRT)
    supporting_theory: str     # The theory it depends on (e.g., stress_physiology)
    
    # How much does dependent rely on supporting?
    strength: float = 0.5
    
    # What aspect of the supporting theory is relied upon?
    relied_claims: List[str] = field(default_factory=list)
    
    # Is this dependency essential or auxiliary?
    essential: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dependent': self.dependent_theory,
            'supporting': self.supporting_theory,
            'strength': self.strength,
            'essential': self.essential
        }


@dataclass
class NestedTheory:
    """
    A theory with explicit dependencies on other theories.
    
    This captures the hierarchical structure where domain-specific
    theories (ART, SRT) rest on more fundamental theories from
    basic science (attention mechanisms, stress physiology).
    """
    theory_id: str
    name: str
    domain: str
    
    # What theories does this depend on?
    dependencies: List[TheoryDependency] = field(default_factory=list)
    
    # What theories depend on this?
    dependents: List[str] = field(default_factory=list)
    
    # Depth in the nesting hierarchy (0 = most fundamental)
    depth: int = 0
    
    # Local credence (within this theory's domain)
    local_credence: float = 0.5
    
    # Grounded credence (accounting for dependencies)
    grounded_credence: float = 0.5
    
    def compute_grounded_credence(
        self,
        supporting_credences: Dict[str, float]
    ) -> float:
        """
        Compute credence accounting for dependencies.
        
        If a supporting theory has low credence, this theory's
        grounded credence is reduced.
        """
        if not self.dependencies:
            self.grounded_credence = self.local_credence
            return self.grounded_credence
        
        # Product of essential dependencies
        essential_product = 1.0
        auxiliary_sum = 0.0
        n_auxiliary = 0
        
        for dep in self.dependencies:
            supporting_cred = supporting_credences.get(dep.supporting_theory, 0.5)
            weighted_cred = dep.strength * supporting_cred + (1 - dep.strength) * 0.5
            
            if dep.essential:
                essential_product *= weighted_cred
            else:
                auxiliary_sum += weighted_cred
                n_auxiliary += 1
        
        # Combine essential (multiplicative) and auxiliary (average)
        auxiliary_factor = auxiliary_sum / n_auxiliary if n_auxiliary > 0 else 1.0
        
        self.grounded_credence = self.local_credence * essential_product * (0.5 + 0.5 * auxiliary_factor)
        return self.grounded_credence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'theory_id': self.theory_id,
            'name': self.name,
            'domain': self.domain,
            'depth': self.depth,
            'local_credence': self.local_credence,
            'grounded_credence': self.grounded_credence,
            'n_dependencies': len(self.dependencies),
            'n_dependents': len(self.dependents)
        }


# =============================================================================
# ABSTRACTION CONTROLLER
# =============================================================================

class AbstractionController:
    """
    Controls what level of abstraction the model operates at.
    
    Key responsibilities:
    1. Determine which beliefs are active vs. background at each level
    2. Propagate evidence through nested theories
    3. Decide when to zoom in/out
    4. Handle criterial rules specially
    """
    
    def __init__(self, web: 'WebOfBelief' = None):
        self.web = web
        self.current_level = AbstractionLevel.DOMAIN
        
        # Nested theories from various domains
        self.nested_theories: Dict[str, NestedTheory] = {}
        
        # Criterial rules
        self.criterial_rules: Dict[str, CriterialRule] = {}
        
        # Theory dependencies
        self.dependencies: Dict[str, TheoryDependency] = {}
        
        # Level-specific configuration
        self.level_configs: Dict[AbstractionLevel, Dict[str, Any]] = {
            AbstractionLevel.FLAT: {
                'include_theories': False,
                'max_depth': 0,
                'background_domains': set()
            },
            AbstractionLevel.DOMAIN: {
                'include_theories': True,
                'max_depth': 1,
                'background_domains': {'basic_science', 'methodology'}
            },
            AbstractionLevel.GROUNDED: {
                'include_theories': True,
                'max_depth': 2,
                'background_domains': {'methodology'}
            },
            AbstractionLevel.FULL: {
                'include_theories': True,
                'max_depth': float('inf'),
                'background_domains': set()
            }
        }
        
        # Zoom history
        self._zoom_history: List[Dict[str, Any]] = []
    
    def set_level(self, level: AbstractionLevel) -> None:
        """Set the current abstraction level."""
        self._zoom_history.append({
            'from': self.current_level.value,
            'to': level.value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        self.current_level = level
        logger.info(f"Abstraction level set to {level.value}")
    
    def get_belief_role(self, belief_id: str) -> BeliefRole:
        """Determine the role of a belief at current abstraction level."""
        if belief_id not in self.web.beliefs:
            return BeliefRole.EXCLUDED
        
        belief = self.web.beliefs[belief_id]
        config = self.level_configs[self.current_level]
        
        # Criterial rules are always background (unless FULL level)
        if belief_id in self.criterial_rules:
            if self.current_level == AbstractionLevel.FULL:
                return BeliefRole.CRITERIAL
            return BeliefRole.BACKGROUND
        
        # Check theory depth
        if belief.theory_id:
            if belief.theory_id in self.nested_theories:
                theory = self.nested_theories[belief.theory_id]
                if theory.depth > config['max_depth']:
                    return BeliefRole.BACKGROUND
                if theory.domain in config['background_domains']:
                    return BeliefRole.BACKGROUND
        
        # FLAT level excludes all theory-attached beliefs
        if self.current_level == AbstractionLevel.FLAT:
            if belief.theory_id:
                return BeliefRole.EXCLUDED
        
        return BeliefRole.ACTIVE
    
    def get_active_beliefs(self) -> List[str]:
        """Get beliefs that are active at current level."""
        return [
            bid for bid in self.web.beliefs
            if self.get_belief_role(bid) == BeliefRole.ACTIVE
        ]
    
    def get_background_beliefs(self) -> List[str]:
        """Get beliefs that are fixed background at current level."""
        return [
            bid for bid in self.web.beliefs
            if self.get_belief_role(bid) == BeliefRole.BACKGROUND
        ]
    
    # =========================================================================
    # NESTED THEORY MANAGEMENT
    # =========================================================================
    
    def add_nested_theory(self, theory: NestedTheory) -> None:
        """Add a nested theory to the controller."""
        self.nested_theories[theory.theory_id] = theory
        
        # Update dependents
        for dep in theory.dependencies:
            if dep.supporting_theory in self.nested_theories:
                self.nested_theories[dep.supporting_theory].dependents.append(theory.theory_id)
    
    def add_dependency(self, dependency: TheoryDependency) -> None:
        """Add a dependency between theories."""
        self.dependencies[dependency.dependency_id] = dependency
        
        # Update theory objects
        if dependency.dependent_theory in self.nested_theories:
            self.nested_theories[dependency.dependent_theory].dependencies.append(dependency)
        if dependency.supporting_theory in self.nested_theories:
            self.nested_theories[dependency.supporting_theory].dependents.append(
                dependency.dependent_theory
            )
    
    def propagate_to_nested(
        self,
        supporting_theory: str,
        credence_delta: float
    ) -> Dict[str, float]:
        """
        Propagate credence change to nested theories.
        
        When a supporting theory's credence changes, dependent theories'
        grounded credences need recalculation.
        """
        updates = {}
        
        theory = self.nested_theories.get(supporting_theory)
        if not theory:
            return updates
        
        # Update all dependents
        for dependent_id in theory.dependents:
            if dependent_id in self.nested_theories:
                dependent = self.nested_theories[dependent_id]
                old_grounded = dependent.grounded_credence
                
                # Get all supporting credences
                supporting_creds = {
                    dep.supporting_theory: self.nested_theories[dep.supporting_theory].local_credence
                    for dep in dependent.dependencies
                    if dep.supporting_theory in self.nested_theories
                }
                
                dependent.compute_grounded_credence(supporting_creds)
                updates[dependent_id] = dependent.grounded_credence - old_grounded
        
        return updates
    
    # =========================================================================
    # CRITERIAL RULES
    # =========================================================================
    
    def add_criterial_rule(self, rule: CriterialRule) -> None:
        """Add a criterial rule."""
        self.criterial_rules[rule.rule_id] = rule
    
    def link_evidence_to_criterial(
        self,
        evidence_id: str,
        rule_id: str
    ) -> None:
        """Link evidence to a criterial rule it depends on."""
        if rule_id in self.criterial_rules:
            self.criterial_rules[rule_id].dependent_evidence.append(evidence_id)
    
    def check_criterial_integrity(self) -> List[Dict[str, Any]]:
        """
        Check for evidence that might challenge criterial rules.
        
        This is rare but important — if evidence consistently contradicts
        what a criterial rule constitutes, we may need to revise the rule
        (which would invalidate dependent evidence).
        """
        warnings = []
        
        for rule_id, rule in self.criterial_rules.items():
            # Check if there's contradictory evidence
            # This would require sophisticated analysis...
            # For now, just flag rules with high invalidation cost
            if rule.invalidation_cost() > 10:
                warnings.append({
                    'rule_id': rule_id,
                    'type': 'high_invalidation_cost',
                    'n_dependent': rule.invalidation_cost(),
                    'message': f"Revising '{rule.content}' would invalidate {rule.invalidation_cost()} pieces of evidence"
                })
        
        return warnings
    
    # =========================================================================
    # ZOOM CONTROL
    # =========================================================================
    
    def should_zoom_in(
        self,
        anomaly_count: int,
        coherence: float
    ) -> bool:
        """
        Determine if we should zoom to finer abstraction level.
        
        Zoom in when:
        - Anomalies are accumulating
        - Coherence is dropping
        - We're not already at FULL
        """
        if self.current_level == AbstractionLevel.FULL:
            return False
        
        # Heuristic thresholds
        if anomaly_count > 3 and coherence < 0.4:
            return True
        if anomaly_count > 5:
            return True
        
        return False
    
    def should_zoom_out(
        self,
        coherence: float,
        time_since_anomaly: float  # seconds
    ) -> bool:
        """
        Determine if we should zoom to coarser abstraction level.
        
        Zoom out when:
        - Coherence is high
        - No recent anomalies
        - We're not already at FLAT
        """
        if self.current_level == AbstractionLevel.FLAT:
            return False
        
        if coherence > 0.7 and time_since_anomaly > 3600:
            return True
        
        return False
    
    def auto_adjust_level(
        self,
        anomaly_count: int,
        coherence: float,
        time_since_anomaly: float
    ) -> Optional[AbstractionLevel]:
        """
        Automatically adjust abstraction level if needed.
        
        Returns new level if changed, None otherwise.
        """
        if self.should_zoom_in(anomaly_count, coherence):
            new_level = AbstractionLevel(min(
                self.current_level.value + 1,
                AbstractionLevel.FULL.value
            ))
            self.set_level(new_level)
            return new_level
        
        if self.should_zoom_out(coherence, time_since_anomaly):
            new_level = AbstractionLevel(max(
                self.current_level.value - 1,
                AbstractionLevel.FLAT.value
            ))
            self.set_level(new_level)
            return new_level
        
        return None
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def summary(self) -> str:
        """Generate summary of abstraction state."""
        lines = [
            "# Abstraction Controller Summary",
            f"Current level: {self.current_level.name}",
            "",
            "## Nested Theories"
        ]
        
        # Group by depth
        by_depth: Dict[int, List[NestedTheory]] = {}
        for theory in self.nested_theories.values():
            by_depth.setdefault(theory.depth, []).append(theory)
        
        for depth in sorted(by_depth.keys()):
            lines.append(f"\n### Depth {depth}")
            for theory in by_depth[depth]:
                lines.append(
                    f"  - {theory.name}: local={theory.local_credence:.2f}, "
                    f"grounded={theory.grounded_credence:.2f}"
                )
        
        if self.criterial_rules:
            lines.append("\n## Criterial Rules")
            for rule in self.criterial_rules.values():
                lines.append(f"  - {rule.content[:50]}... ({rule.invalidation_cost()} dependent)")
        
        active = self.get_active_beliefs() if self.web else []
        background = self.get_background_beliefs() if self.web else []
        
        lines.append(f"\n## Current Level Stats")
        lines.append(f"  Active beliefs: {len(active)}")
        lines.append(f"  Background beliefs: {len(background)}")
        
        return "\n".join(lines)


# =============================================================================
# FACTORY FOR GROUNDED MODEL
# =============================================================================

def create_grounded_neuroarchitecture() -> AbstractionController:
    """
    Create an abstraction controller with neuroarchitecture theories
    grounded in basic science.
    """
    controller = AbstractionController()
    
    # === DEEP THEORIES (basic science) ===
    
    controller.add_nested_theory(NestedTheory(
        theory_id="stress_physiology",
        name="Stress Physiology",
        domain="basic_science",
        depth=0,
        local_credence=0.9  # Well-established
    ))
    
    controller.add_nested_theory(NestedTheory(
        theory_id="attention_mechanisms",
        name="Attention Mechanisms",
        domain="basic_science",
        depth=0,
        local_credence=0.85
    ))
    
    controller.add_nested_theory(NestedTheory(
        theory_id="evolutionary_psychology",
        name="Evolutionary Psychology",
        domain="basic_science",
        depth=0,
        local_credence=0.65  # More contested
    ))
    
    # === MID-LEVEL THEORIES (environmental psychology) ===
    
    controller.add_nested_theory(NestedTheory(
        theory_id="SRT",
        name="Stress Recovery Theory",
        domain="environmental_psychology",
        depth=1,
        local_credence=0.72
    ))
    
    controller.add_dependency(TheoryDependency(
        dependency_id="SRT_stress",
        dependent_theory="SRT",
        supporting_theory="stress_physiology",
        strength=0.8,
        essential=True,
        relied_claims=["cortisol reflects HPA axis activation", "autonomic response to threat"]
    ))
    
    controller.add_dependency(TheoryDependency(
        dependency_id="SRT_evopsych",
        dependent_theory="SRT",
        supporting_theory="evolutionary_psychology",
        strength=0.5,
        essential=False,
        relied_claims=["evolved responses to natural stimuli"]
    ))
    
    controller.add_nested_theory(NestedTheory(
        theory_id="ART",
        name="Attention Restoration Theory",
        domain="environmental_psychology",
        depth=1,
        local_credence=0.75
    ))
    
    controller.add_dependency(TheoryDependency(
        dependency_id="ART_attention",
        dependent_theory="ART",
        supporting_theory="attention_mechanisms",
        strength=0.85,
        essential=True,
        relied_claims=["directed attention is limited resource", "involuntary attention is distinct"]
    ))
    
    controller.add_nested_theory(NestedTheory(
        theory_id="BIOPHILIA",
        name="Biophilia Hypothesis",
        domain="environmental_psychology",
        depth=1,
        local_credence=0.68
    ))
    
    controller.add_dependency(TheoryDependency(
        dependency_id="BIO_evopsych",
        dependent_theory="BIOPHILIA",
        supporting_theory="evolutionary_psychology",
        strength=0.75,
        essential=True,
        relied_claims=["innate affiliative responses", "habitat selection pressures"]
    ))
    
    # === CRITERIAL RULES ===
    
    controller.add_criterial_rule(CriterialRule(
        rule_id="cortisol_measurement",
        content="Salivary cortisol concentration reflects HPA axis activation",
        constitutes="stress_measurement",
        domain="methodology"
    ))
    
    controller.add_criterial_rule(CriterialRule(
        rule_id="attention_measurement",
        content="Sustained Attention to Response Task measures directed attention",
        constitutes="attention_measurement",
        domain="methodology"
    ))
    
    controller.add_criterial_rule(CriterialRule(
        rule_id="self_report",
        content="Self-report scales measure subjective psychological states",
        constitutes="subjective_measurement",
        domain="methodology"
    ))
    
    # Compute grounded credences
    for theory in controller.nested_theories.values():
        if theory.dependencies:
            supporting_creds = {
                dep.supporting_theory: controller.nested_theories[dep.supporting_theory].local_credence
                for dep in theory.dependencies
                if dep.supporting_theory in controller.nested_theories
            }
            theory.compute_grounded_credence(supporting_creds)
    
    return controller


if __name__ == "__main__":
    controller = create_grounded_neuroarchitecture()
    print(controller.summary())
    
    print("\n" + "="*60)
    print("\nGrounded credences (accounting for dependencies):\n")
    
    for tid, theory in sorted(controller.nested_theories.items(), key=lambda x: x[1].depth):
        print(f"{theory.name}:")
        print(f"  Depth: {theory.depth}")
        print(f"  Local credence: {theory.local_credence:.3f}")
        print(f"  Grounded credence: {theory.grounded_credence:.3f}")
        if theory.dependencies:
            print(f"  Depends on: {[d.supporting_theory for d in theory.dependencies]}")
        print()
