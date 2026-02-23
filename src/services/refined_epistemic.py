"""
Article Eater - Refined Epistemic Architecture
Phase 1: Foundational Refinements

Based on Expert Panel recommendations:
- Glymour: Constitutive vs. evidential dependencies
- Boghossian: Semantic status for criterial rules
- Hartmann: Bovens-Hartmann coherence measure

This module refines the web of belief architecture with more principled
philosophical foundations.

References:
- Bovens, L. & Hartmann, S. (2003). Bayesian Epistemology. Oxford. [Citations: 800+]
- Glymour, C. (2001). The Mind's Arrows: Bayes Nets and Graphical Causal Models. MIT.
- Boghossian, P. (1996). Analyticity Reconsidered. Noûs, 30(3). [Citations: 400+]
- Olsson, E. (2002). What is the Problem of Coherence and Truth? Journal of Philosophy.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple, FrozenSet
from enum import Enum
from datetime import datetime, timezone
import math
import logging
from collections import defaultdict
from itertools import combinations

logger = logging.getLogger(__name__)


# =============================================================================
# REFINED DEPENDENCY TYPES (Glymour)
# =============================================================================

class DependencyType(Enum):
    """
    Types of dependencies between beliefs/theories.
    
    Following Glymour's distinction between different kinds of
    inferential relationships in scientific reasoning.
    """
    # Constitutive: B partially defines what A means
    # Revising B changes the meaning of A
    CONSTITUTIVE = "constitutive"
    
    # Presuppositional: A presupposes B
    # A cannot be true unless B is true
    PRESUPPOSITIONAL = "presuppositional"
    
    # Evidential: A provides evidence for/against B
    # A's truth raises/lowers probability of B
    EVIDENTIAL = "evidential"
    
    # Explanatory: A explains B (or vice versa)
    # Related to inference to best explanation
    EXPLANATORY = "explanatory"
    
    # Analogical: A and B share structural similarity
    # Evidence for one weakly supports the other
    ANALOGICAL = "analogical"


@dataclass
class RefinedDependency:
    """
    A dependency with distinguished type and properties.
    """
    dependency_id: str
    source: str  # belief/theory ID
    target: str
    dep_type: DependencyType
    
    # Strength (meaning depends on type)
    # For EVIDENTIAL: likelihood ratio
    # For CONSTITUTIVE: degree of meaning dependence
    # For PRESUPPOSITIONAL: typically 1.0 (binary)
    strength: float = 0.5
    
    # Direction matters differently for different types
    # CONSTITUTIVE: asymmetric (B constitutes A, not vice versa)
    # EVIDENTIAL: can be symmetric
    symmetric: bool = False
    
    # What specific aspect is involved?
    aspect: str = ""  # e.g., "measurement validity", "mechanism"
    
    def propagation_factor(self) -> float:
        """
        How much does a change in source propagate to target?
        
        Constitutive and presuppositional dependencies propagate strongly.
        Evidential dependencies propagate more weakly.
        """
        factors = {
            DependencyType.CONSTITUTIVE: 0.9,
            DependencyType.PRESUPPOSITIONAL: 0.95,
            DependencyType.EVIDENTIAL: 0.5,
            DependencyType.EXPLANATORY: 0.6,
            DependencyType.ANALOGICAL: 0.3
        }
        return factors.get(self.dep_type, 0.5) * self.strength
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'target': self.target,
            'type': self.dep_type.value,
            'strength': self.strength,
            'symmetric': self.symmetric,
            'propagation_factor': self.propagation_factor()
        }


# =============================================================================
# SEMANTIC STATUS FOR CRITERIAL RULES (Boghossian)
# =============================================================================

class SemanticStatus(Enum):
    """
    Semantic status of a belief, following Boghossian's gradations.
    
    Not a sharp analytic/synthetic distinction, but a continuum
    of how much a belief's truth is tied to meaning vs. fact.
    """
    # Purely definitional: "Bachelors are unmarried"
    ANALYTIC = "analytic"
    
    # Criterial: partially defines measurement/observation
    # "Cortisol level reflects HPA axis activation"
    CRITERIAL = "criterial"
    
    # Framework: constitutes a way of thinking about domain
    # "Directed attention is a limited resource"
    FRAMEWORK = "framework"
    
    # Synthetic but central: well-confirmed, many dependencies
    # "Nature exposure reduces cortisol"
    CENTRAL_SYNTHETIC = "central_synthetic"
    
    # Ordinary synthetic: typical empirical claim
    SYNTHETIC = "synthetic"
    
    # Peripheral: easily revisable, few dependencies
    PERIPHERAL = "peripheral"


@dataclass
class SemanticBelief:
    """
    A belief with explicit semantic status.
    
    The semantic status affects:
    - How revisable the belief is
    - What happens when it's revised (meaning change vs. belief change)
    - How evidence bears on it
    """
    belief_id: str
    content: str
    semantic_status: SemanticStatus
    
    # Credence (for synthetic beliefs)
    # For analytic/criterial, this is less meaningful
    credence: float = 0.5
    
    # What would change if this belief were revised?
    revision_consequences: List[str] = field(default_factory=list)
    
    # For criterial beliefs: what measurements depend on this?
    constituted_measurements: List[str] = field(default_factory=list)
    
    # Entrenchment (emergent from dependencies, not intrinsic)
    entrenchment: float = 0.5
    
    def revisability(self) -> float:
        """
        How revisable is this belief?
        
        Analytic and criterial beliefs are very hard to revise
        (revision changes meaning, not just belief).
        """
        revisability_map = {
            SemanticStatus.ANALYTIC: 0.01,
            SemanticStatus.CRITERIAL: 0.05,
            SemanticStatus.FRAMEWORK: 0.15,
            SemanticStatus.CENTRAL_SYNTHETIC: 0.4,
            SemanticStatus.SYNTHETIC: 0.7,
            SemanticStatus.PERIPHERAL: 0.95
        }
        return revisability_map.get(self.semantic_status, 0.5)
    
    def revision_type(self) -> str:
        """What kind of revision would changing this belief constitute?"""
        if self.semantic_status in [SemanticStatus.ANALYTIC, SemanticStatus.CRITERIAL]:
            return "meaning_change"
        elif self.semantic_status == SemanticStatus.FRAMEWORK:
            return "paradigm_shift"
        else:
            return "belief_change"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'content': self.content,
            'semantic_status': self.semantic_status.value,
            'credence': self.credence,
            'revisability': self.revisability(),
            'revision_type': self.revision_type(),
            'entrenchment': self.entrenchment
        }


# =============================================================================
# BOVENS-HARTMANN COHERENCE (Hartmann)
# =============================================================================

class BovensHartmannCoherence:
    """
    Principled coherence measure based on Bovens & Hartmann (2003).
    
    Key ideas:
    1. Coherence is about how beliefs "hang together"
    2. Measured by comparing joint probability to independence
    3. Accounts for both agreement and mutual support
    
    The measure compares:
    - P(all beliefs true jointly)
    - P(all beliefs true if independent)
    
    If joint > independent, beliefs cohere (mutual support).
    If joint < independent, beliefs are in tension.
    """
    
    def __init__(self):
        pass
    
    def pairwise_coherence(
        self,
        p_a: float,
        p_b: float,
        p_a_and_b: float
    ) -> float:
        """
        Compute coherence between two beliefs.
        
        Uses the deviation from independence:
        C(A,B) = P(A,B) / (P(A) * P(B))
        
        C > 1: beliefs cohere (positively associated)
        C = 1: beliefs independent
        C < 1: beliefs in tension (negatively associated)
        
        Normalized to [-1, 1] range for interpretability.
        """
        if p_a == 0 or p_b == 0:
            return 0.0
        
        independence = p_a * p_b
        if independence == 0:
            return 0.0
        
        ratio = p_a_and_b / independence
        
        # Normalize: log scale, then sigmoid-like mapping
        if ratio == 0:
            return -1.0
        
        log_ratio = math.log(ratio)
        # Map to [-1, 1] using tanh
        return math.tanh(log_ratio)
    
    def set_coherence(
        self,
        beliefs: List[str],
        marginals: Dict[str, float],
        joint_probability: float
    ) -> float:
        """
        Compute coherence of a set of beliefs.
        
        Generalizes pairwise coherence to sets:
        C(S) = P(all in S true) / ∏P(b) for b in S
        
        Args:
            beliefs: List of belief IDs
            marginals: P(belief) for each belief
            joint_probability: P(all beliefs true jointly)
        """
        if not beliefs:
            return 0.0
        
        independence = 1.0
        for b in beliefs:
            independence *= marginals.get(b, 0.5)
        
        if independence == 0:
            return 0.0
        
        ratio = joint_probability / independence
        
        if ratio == 0:
            return -1.0
        
        log_ratio = math.log(ratio)
        return math.tanh(log_ratio)
    
    def agreement_coherence(
        self,
        reports: List[Tuple[str, bool]]  # (source, claim_true)
    ) -> float:
        """
        Coherence based on agreement among independent sources.
        
        If multiple independent sources agree, that's coherent.
        If they disagree, that's incoherent.
        
        This is the "witness agreement" model from Bovens & Hartmann.
        """
        if len(reports) < 2:
            return 0.0
        
        true_count = sum(1 for _, v in reports if v)
        false_count = len(reports) - true_count
        
        # Perfect agreement = 1, perfect disagreement = -1
        # 50/50 = 0
        agreement = abs(true_count - false_count) / len(reports)
        
        # Sign: positive if majority agrees on True, negative if on False
        if true_count >= false_count:
            return agreement
        else:
            return -agreement
    
    def explanatory_coherence(
        self,
        hypothesis: str,
        explained: List[str],
        explanation_strengths: Dict[str, float],
        competing_explanations: Dict[str, List[str]]
    ) -> float:
        """
        Coherence based on explanatory relationships.
        
        Following Thagard's Explanatory Coherence theory (which influenced
        Bovens & Hartmann):
        
        - Beliefs cohere if one explains others
        - Coherence increases with number of explained beliefs
        - Decreases with competing explanations
        """
        if not explained:
            return 0.0
        
        # Base coherence from explanation strength
        total_strength = sum(explanation_strengths.get(e, 0.5) for e in explained)
        avg_strength = total_strength / len(explained)
        
        # Penalty for competing explanations
        competition_penalty = 0.0
        for e in explained:
            competitors = competing_explanations.get(e, [])
            if competitors:
                competition_penalty += len(competitors) * 0.1
        
        coherence = avg_strength - min(0.5, competition_penalty)
        return max(-1.0, min(1.0, coherence))


# =============================================================================
# REFINED EPISTEMIC STATE
# =============================================================================

class RefinedEpistemicState:
    """
    Epistemic state with refined philosophical foundations.
    
    Improvements over base WebOfBelief:
    1. Typed dependencies (constitutive vs. evidential)
    2. Semantic status for beliefs
    3. Principled coherence measure
    4. Proper propagation based on dependency type
    """
    
    def __init__(self, domain: str = "neuroarchitecture"):
        self.domain = domain
        
        # Beliefs with semantic status
        self.beliefs: Dict[str, SemanticBelief] = {}
        
        # Refined dependencies
        self.dependencies: Dict[str, RefinedDependency] = {}
        
        # Coherence calculator
        self.coherence_calc = BovensHartmannCoherence()
        
        # Indices
        self._deps_by_source: Dict[str, List[str]] = defaultdict(list)
        self._deps_by_target: Dict[str, List[str]] = defaultdict(list)
        self._deps_by_type: Dict[DependencyType, List[str]] = defaultdict(list)
        
        # Cached coherence (recomputed on changes)
        self._coherence_cache: Dict[FrozenSet[str], float] = {}
        self._global_coherence: float = 0.5
        
        # History
        self.version: int = 0
        self.created_at = datetime.now(timezone.utc)
    
    # =========================================================================
    # BELIEF MANAGEMENT
    # =========================================================================
    
    def add_belief(self, belief: SemanticBelief) -> None:
        """Add a belief to the state."""
        self.beliefs[belief.belief_id] = belief
        self._invalidate_coherence_cache()
        self.version += 1
    
    def add_criterial_belief(
        self,
        belief_id: str,
        content: str,
        constitutes: List[str]
    ) -> SemanticBelief:
        """
        Add a criterial belief (measurement constitution).
        
        These beliefs define what counts as measuring something.
        Revising them changes meaning, not just belief.
        """
        belief = SemanticBelief(
            belief_id=belief_id,
            content=content,
            semantic_status=SemanticStatus.CRITERIAL,
            credence=0.99,  # Very high but not 1.0
            constituted_measurements=constitutes,
            entrenchment=0.95
        )
        self.add_belief(belief)
        return belief
    
    def add_framework_belief(
        self,
        belief_id: str,
        content: str,
        initial_credence: float = 0.7
    ) -> SemanticBelief:
        """
        Add a framework belief (paradigm-level).
        
        These structure how we think about the domain.
        """
        belief = SemanticBelief(
            belief_id=belief_id,
            content=content,
            semantic_status=SemanticStatus.FRAMEWORK,
            credence=initial_credence,
            entrenchment=0.7
        )
        self.add_belief(belief)
        return belief
    
    def add_synthetic_belief(
        self,
        belief_id: str,
        content: str,
        credence: float = 0.5,
        peripheral: bool = False
    ) -> SemanticBelief:
        """Add an ordinary empirical belief."""
        belief = SemanticBelief(
            belief_id=belief_id,
            content=content,
            semantic_status=SemanticStatus.PERIPHERAL if peripheral else SemanticStatus.SYNTHETIC,
            credence=credence,
            entrenchment=0.2 if peripheral else 0.4
        )
        self.add_belief(belief)
        return belief
    
    # =========================================================================
    # DEPENDENCY MANAGEMENT
    # =========================================================================
    
    def add_dependency(self, dep: RefinedDependency) -> None:
        """Add a dependency between beliefs."""
        if dep.source not in self.beliefs or dep.target not in self.beliefs:
            raise ValueError(f"Source or target belief not found")
        
        self.dependencies[dep.dependency_id] = dep
        self._deps_by_source[dep.source].append(dep.dependency_id)
        self._deps_by_target[dep.target].append(dep.dependency_id)
        self._deps_by_type[dep.dep_type].append(dep.dependency_id)
        
        # Update entrenchment based on dependencies
        self._update_entrenchment()
        self._invalidate_coherence_cache()
        self.version += 1
    
    def add_constitutive_dependency(
        self,
        source: str,
        target: str,
        aspect: str = "",
        strength: float = 0.9
    ) -> RefinedDependency:
        """
        Add a constitutive dependency.
        
        Source partially constitutes the meaning of target.
        Example: "Cortisol measurement" constitutes what we mean by "stress level."
        """
        dep = RefinedDependency(
            dependency_id=f"const:{source}:{target}",
            source=source,
            target=target,
            dep_type=DependencyType.CONSTITUTIVE,
            strength=strength,
            symmetric=False,
            aspect=aspect
        )
        self.add_dependency(dep)
        return dep
    
    def add_evidential_dependency(
        self,
        source: str,
        target: str,
        strength: float = 0.5,
        symmetric: bool = False
    ) -> RefinedDependency:
        """
        Add an evidential dependency.
        
        Source provides evidence for target.
        """
        dep = RefinedDependency(
            dependency_id=f"evid:{source}:{target}",
            source=source,
            target=target,
            dep_type=DependencyType.EVIDENTIAL,
            strength=strength,
            symmetric=symmetric
        )
        self.add_dependency(dep)
        return dep
    
    def add_presuppositional_dependency(
        self,
        source: str,
        target: str
    ) -> RefinedDependency:
        """
        Add a presuppositional dependency.
        
        Target presupposes source — target cannot be true if source is false.
        """
        dep = RefinedDependency(
            dependency_id=f"presup:{source}:{target}",
            source=source,
            target=target,
            dep_type=DependencyType.PRESUPPOSITIONAL,
            strength=1.0,
            symmetric=False
        )
        self.add_dependency(dep)
        return dep
    
    # =========================================================================
    # ENTRENCHMENT
    # =========================================================================
    
    def _update_entrenchment(self) -> None:
        """
        Update entrenchment scores based on dependency structure.
        
        Entrenchment emerges from how many other beliefs depend on this one.
        """
        # Count dependencies where each belief is the source
        dependency_counts: Dict[str, int] = defaultdict(int)
        weighted_counts: Dict[str, float] = defaultdict(float)
        
        for dep in self.dependencies.values():
            dependency_counts[dep.source] += 1
            weighted_counts[dep.source] += dep.propagation_factor()
        
        # Normalize and set entrenchment
        max_count = max(dependency_counts.values()) if dependency_counts else 1
        
        for belief_id, belief in self.beliefs.items():
            # Base entrenchment from semantic status
            base = 1.0 - belief.revisability()
            
            # Additional entrenchment from being depended upon
            dep_factor = weighted_counts[belief_id] / (max_count + 1)
            
            # Combine (semantic status dominates)
            belief.entrenchment = 0.7 * base + 0.3 * dep_factor
    
    # =========================================================================
    # COHERENCE
    # =========================================================================
    
    def _invalidate_coherence_cache(self) -> None:
        """Invalidate cached coherence values."""
        self._coherence_cache = {}
        self._global_coherence = None
    
    def compute_coherence(self, belief_ids: Optional[Set[str]] = None) -> float:
        """
        Compute Bovens-Hartmann coherence for a set of beliefs.
        
        If no belief_ids provided, computes global coherence.
        """
        if belief_ids is None:
            belief_ids = set(self.beliefs.keys())
        
        frozen_ids = frozenset(belief_ids)
        if frozen_ids in self._coherence_cache:
            return self._coherence_cache[frozen_ids]
        
        if len(belief_ids) < 2:
            return 0.5
        
        # Get marginals
        marginals = {bid: self.beliefs[bid].credence for bid in belief_ids}
        
        # Estimate joint probability
        # For proper calculation, we'd need the full joint distribution
        # Approximate using dependency structure
        joint = self._estimate_joint_probability(belief_ids)
        
        coherence = self.coherence_calc.set_coherence(
            list(belief_ids),
            marginals,
            joint
        )
        
        self._coherence_cache[frozen_ids] = coherence
        return coherence
    
    def _estimate_joint_probability(self, belief_ids: Set[str]) -> float:
        """
        Estimate P(all beliefs true) accounting for dependencies.
        
        This is approximate — full calculation would require
        the complete joint distribution.
        """
        if not belief_ids:
            return 1.0
        
        # Start with independence assumption
        joint = 1.0
        for bid in belief_ids:
            joint *= self.beliefs[bid].credence
        
        # Adjust for dependencies
        for dep in self.dependencies.values():
            if dep.source in belief_ids and dep.target in belief_ids:
                # Positive dependency increases joint probability
                if dep.dep_type in [DependencyType.CONSTITUTIVE, 
                                    DependencyType.PRESUPPOSITIONAL,
                                    DependencyType.EXPLANATORY]:
                    # These create positive association
                    joint *= (1 + 0.2 * dep.strength)
                elif dep.dep_type == DependencyType.EVIDENTIAL:
                    # Evidential can go either way, assume positive
                    joint *= (1 + 0.1 * dep.strength)
        
        return min(1.0, joint)
    
    def global_coherence(self) -> float:
        """Get global coherence score."""
        if self._global_coherence is None:
            self._global_coherence = self.compute_coherence()
        return self._global_coherence
    
    def find_tensions(self) -> List[Dict[str, Any]]:
        """
        Find belief pairs with negative coherence.
        """
        tensions = []
        
        for b1, b2 in combinations(self.beliefs.keys(), 2):
            pairwise = self.compute_coherence({b1, b2})
            if pairwise < -0.1:  # Threshold for tension
                tensions.append({
                    'beliefs': [b1, b2],
                    'coherence': pairwise,
                    'credences': [self.beliefs[b1].credence, self.beliefs[b2].credence]
                })
        
        tensions.sort(key=lambda x: x['coherence'])
        return tensions
    
    # =========================================================================
    # UPDATING
    # =========================================================================
    
    def update_belief(
        self,
        belief_id: str,
        new_credence: float,
        propagate: bool = True
    ) -> Dict[str, Any]:
        """
        Update a belief's credence and propagate through dependencies.
        
        Propagation depends on dependency type:
        - Constitutive/Presuppositional: strong propagation
        - Evidential: moderate propagation
        - Analogical: weak propagation
        """
        if belief_id not in self.beliefs:
            raise ValueError(f"Belief not found: {belief_id}")
        
        belief = self.beliefs[belief_id]
        updates = {
            'belief_id': belief_id,
            'old_credence': belief.credence,
            'new_credence': new_credence,
            'propagated': []
        }
        
        # Check revisability
        if abs(new_credence - belief.credence) > belief.revisability():
            logger.warning(
                f"Update to {belief_id} exceeds revisability "
                f"({belief.semantic_status.value})"
            )
        
        # Apply update
        belief.credence = new_credence
        
        # Propagate
        if propagate:
            delta = new_credence - updates['old_credence']
            propagated = self._propagate_update(belief_id, delta)
            updates['propagated'] = propagated
        
        self._invalidate_coherence_cache()
        self.version += 1
        
        return updates
    
    def _propagate_update(
        self,
        source_id: str,
        delta: float
    ) -> List[Dict[str, Any]]:
        """
        Propagate a credence change through dependencies.
        """
        propagated = []
        
        for dep_id in self._deps_by_source.get(source_id, []):
            dep = self.dependencies[dep_id]
            target = self.beliefs[dep.target]
            
            # Compute propagated delta
            prop_factor = dep.propagation_factor()
            prop_delta = delta * prop_factor * target.revisability()
            
            if abs(prop_delta) > 0.01:  # Threshold
                old_cred = target.credence
                target.credence = max(0.01, min(0.99, target.credence + prop_delta))
                
                propagated.append({
                    'target': dep.target,
                    'dependency_type': dep.dep_type.value,
                    'old_credence': old_cred,
                    'new_credence': target.credence,
                    'propagated_delta': prop_delta
                })
        
        return propagated
    
    def add_evidence(
        self,
        evidence_id: str,
        content: str,
        supports: Dict[str, float] = None,
        contradicts: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Add new evidence and update beliefs.
        """
        supports = supports or {}
        contradicts = contradicts or {}
        
        updates = {
            'evidence_id': evidence_id,
            'belief_updates': []
        }
        
        # Add evidence as peripheral belief
        self.add_synthetic_belief(evidence_id, content, 0.7, peripheral=True)
        
        # Update supported beliefs
        for belief_id, strength in supports.items():
            if belief_id in self.beliefs:
                belief = self.beliefs[belief_id]
                # Bayesian-ish update
                old_cred = belief.credence
                lr = (0.6 + 0.4 * strength) / 0.4  # Likelihood ratio
                odds = belief.credence / (1 - belief.credence + 1e-10)
                new_odds = odds * lr
                new_cred = new_odds / (1 + new_odds)
                new_cred = max(0.01, min(0.99, new_cred))
                
                result = self.update_belief(belief_id, new_cred)
                updates['belief_updates'].append(result)
                
                # Add evidential dependency
                self.add_evidential_dependency(evidence_id, belief_id, strength)
        
        # Update contradicted beliefs
        for belief_id, strength in contradicts.items():
            if belief_id in self.beliefs:
                belief = self.beliefs[belief_id]
                old_cred = belief.credence
                lr = 0.4 / (0.6 + 0.4 * strength)  # Inverse likelihood ratio
                odds = belief.credence / (1 - belief.credence + 1e-10)
                new_odds = odds * lr
                new_cred = new_odds / (1 + new_odds)
                new_cred = max(0.01, min(0.99, new_cred))
                
                result = self.update_belief(belief_id, new_cred)
                updates['belief_updates'].append(result)
        
        updates['coherence'] = self.global_coherence()
        return updates
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def summary(self) -> str:
        """Generate summary of epistemic state."""
        lines = [
            "# Refined Epistemic State",
            f"Domain: {self.domain}",
            f"Version: {self.version}",
            f"Global Coherence: {self.global_coherence():.3f}",
            "",
            "## Beliefs by Semantic Status"
        ]
        
        by_status: Dict[SemanticStatus, List[SemanticBelief]] = defaultdict(list)
        for belief in self.beliefs.values():
            by_status[belief.semantic_status].append(belief)
        
        for status in SemanticStatus:
            beliefs = by_status.get(status, [])
            if beliefs:
                lines.append(f"\n### {status.value.replace('_', ' ').title()} ({len(beliefs)})")
                for b in sorted(beliefs, key=lambda x: x.credence, reverse=True)[:5]:
                    lines.append(f"  - [{b.credence:.2f}] {b.content[:50]}...")
        
        # Dependencies by type
        lines.append("\n## Dependencies")
        for dep_type in DependencyType:
            deps = self._deps_by_type.get(dep_type, [])
            if deps:
                lines.append(f"  {dep_type.value}: {len(deps)}")
        
        # Tensions
        tensions = self.find_tensions()
        if tensions:
            lines.append(f"\n## Tensions ({len(tensions)})")
            for t in tensions[:3]:
                lines.append(f"  - {t['beliefs'][0]} vs {t['beliefs'][1]}: {t['coherence']:.3f}")
        
        return "\n".join(lines)


# =============================================================================
# FACTORY
# =============================================================================

def create_refined_neuroarchitecture() -> RefinedEpistemicState:
    """Create a refined epistemic state for neuroarchitecture."""
    state = RefinedEpistemicState(domain="neuroarchitecture")
    
    # === CRITERIAL BELIEFS ===
    
    state.add_criterial_belief(
        "crit_cortisol",
        "Salivary cortisol concentration reflects HPA axis activation",
        constitutes=["stress_measurement"]
    )
    
    state.add_criterial_belief(
        "crit_attention",
        "Sustained Attention to Response Task measures directed attention capacity",
        constitutes=["attention_measurement"]
    )
    
    # === FRAMEWORK BELIEFS ===
    
    state.add_framework_belief(
        "framework_attention_limited",
        "Directed attention is a limited cognitive resource that can be depleted",
        initial_credence=0.8
    )
    
    state.add_framework_belief(
        "framework_stress_physiology",
        "Psychological stress has measurable physiological correlates",
        initial_credence=0.9
    )
    
    # === THEORETICAL BELIEFS ===
    
    art_core = state.add_synthetic_belief(
        "ART_core",
        "Natural environments restore directed attention through soft fascination",
        credence=0.72
    )
    
    srt_core = state.add_synthetic_belief(
        "SRT_core",
        "Natural environments trigger rapid autonomic stress recovery",
        credence=0.75
    )
    
    # === EMPIRICAL BELIEFS ===
    
    state.add_synthetic_belief(
        "nature_attention",
        "Nature exposure improves performance on attention tasks",
        credence=0.68
    )
    
    state.add_synthetic_belief(
        "nature_cortisol",
        "Nature exposure reduces salivary cortisol levels",
        credence=0.71
    )
    
    # === DEPENDENCIES ===
    
    # Criterial rules constitute what measurements mean
    state.add_constitutive_dependency("crit_cortisol", "nature_cortisol", "measurement_validity")
    state.add_constitutive_dependency("crit_attention", "nature_attention", "measurement_validity")
    
    # Framework beliefs are presupposed by theories
    state.add_presuppositional_dependency("framework_attention_limited", "ART_core")
    state.add_presuppositional_dependency("framework_stress_physiology", "SRT_core")
    
    # Empirical beliefs provide evidence for theories
    state.add_evidential_dependency("nature_attention", "ART_core", strength=0.7)
    state.add_evidential_dependency("nature_cortisol", "SRT_core", strength=0.7)
    
    return state


if __name__ == "__main__":
    state = create_refined_neuroarchitecture()
    print(state.summary())
    
    print("\n" + "="*60 + "\n")
    
    # Add some evidence
    print("Adding evidence that nature reduces cortisol...")
    updates = state.add_evidence(
        "ev_park_study",
        "20-min park walk reduced cortisol by 15% (d=0.45)",
        supports={"nature_cortisol": 0.65, "SRT_core": 0.5}
    )
    
    print(f"\nUpdates: {len(updates['belief_updates'])} beliefs changed")
    for u in updates['belief_updates']:
        print(f"  {u['belief_id']}: {u['old_credence']:.3f} -> {u['new_credence']:.3f}")
        for p in u.get('propagated', []):
            print(f"    -> {p['target']}: {p['old_credence']:.3f} -> {p['new_credence']:.3f}")
    
    print(f"\nNew coherence: {updates['coherence']:.3f}")
