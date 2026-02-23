"""
Article Eater — Cross-Layer Query Service
Sprint INT-5 — 2026-02-11

Enables querying across epistemic layers in the Web of Belief.
Supports queries like:
- Find all empirical beliefs supporting a theory
- Get the theory chain for an empirical finding
- Find beliefs connecting environment to outcome
- Identify cross-layer conflicts

Per panel recommendations (P-LAYER):
- Quine: Epistemic holism—all beliefs interconnected
- Haack: Foundherentism—layers matter but aren't rigid
- Thagard: Coherence contribution varies by layer
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of cross-layer queries."""
    THEORY_SUPPORT = "theory_support"       # Find empirical support for theory
    EMPIRICAL_GROUNDING = "empirical_grounding"  # Find theory grounding for empirical
    ENVIRONMENT_OUTCOME = "environment_outcome"  # Beliefs linking env to outcome
    LAYER_CONFLICTS = "layer_conflicts"     # Find conflicts across layers
    BELIEF_CHAIN = "belief_chain"           # Full chain from theory to observation


@dataclass
class BeliefSummary:
    """Summary of a belief for query results."""
    belief_id: str
    content: str
    level: str
    credence: float
    uncertainty: float
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ConstraintSummary:
    """Summary of a constraint for query results."""
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: str
    strength: float


@dataclass
class LayerConnection:
    """A connection between beliefs across layers."""
    source_belief: BeliefSummary
    target_belief: BeliefSummary
    constraint: ConstraintSummary
    layer_distance: int  # How many levels apart


@dataclass
class CrossLayerQueryResult:
    """Result of a cross-layer query."""
    query_type: str
    query_params: Dict[str, Any]
    beliefs: List[BeliefSummary]
    connections: List[LayerConnection]
    layer_summary: Dict[str, int]  # Count per level
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_type": self.query_type,
            "query_params": self.query_params,
            "n_beliefs": len(self.beliefs),
            "n_connections": len(self.connections),
            "beliefs": [
                {
                    "belief_id": b.belief_id,
                    "content": b.content[:200],
                    "level": b.level,
                    "credence": b.credence,
                    "uncertainty": b.uncertainty,
                    "environment_id": b.environment_id,
                    "outcome_id": b.outcome_id,
                    "tags": b.tags
                }
                for b in self.beliefs
            ],
            "connections": [
                {
                    "source": c.source_belief.belief_id,
                    "target": c.target_belief.belief_id,
                    "constraint_type": c.constraint.constraint_type,
                    "strength": c.constraint.strength,
                    "layer_distance": c.layer_distance
                }
                for c in self.connections
            ],
            "layer_summary": self.layer_summary,
            "generated_at": self.generated_at
        }


@dataclass
class TheorySupportResult:
    """Result of theory support query."""
    theory_belief: BeliefSummary
    supporting_beliefs: List[BeliefSummary]
    support_strength: float
    coverage_score: float  # How much of the theory is empirically grounded
    gaps: List[str]  # Aspects of theory without empirical support
    # Panel D6: Evidence quality weighting
    quality_weighted_support: float = 0.0
    evidence_quality_breakdown: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory": {
                "belief_id": self.theory_belief.belief_id,
                "content": self.theory_belief.content[:300],
                "credence": self.theory_belief.credence
            },
            "n_supporting": len(self.supporting_beliefs),
            "support_strength": self.support_strength,
            "quality_weighted_support": self.quality_weighted_support,
            "coverage_score": self.coverage_score,
            "evidence_quality_breakdown": self.evidence_quality_breakdown,
            "supporting_beliefs": [
                {
                    "belief_id": b.belief_id,
                    "content": b.content[:200],
                    "level": b.level,
                    "credence": b.credence
                }
                for b in self.supporting_beliefs
            ],
            "gaps": self.gaps
        }


class CrossLayerQueryService:
    """
    Service for querying across epistemic layers.

    Enables:
    - Finding empirical support for theoretical beliefs
    - Tracing belief chains from theory to observation
    - Finding environment-outcome connections
    - Identifying cross-layer conflicts
    """

    # Level ordering (from most theoretical to most observational)
    LEVEL_ORDER = ['theoretical', 'intermediate', 'empirical', 'observational']

    def __init__(self, web=None, accumulator=None):
        """Initialize with Web of Belief or accumulator."""
        self._web = web
        self._accumulator = accumulator

    @property
    def web(self):
        """Lazy-load web from accumulator if needed."""
        if self._web is None:
            if self._accumulator is not None:
                # get_master_web() returns (WebOfBelief, BridgeRegistry) tuple
                self._web, _ = self._accumulator.get_master_web()
            else:
                try:
                    from src.services.web_accumulator import get_accumulator
                    acc = get_accumulator()
                    self._web, _ = acc.get_master_web()
                except Exception as e:
                    logger.error(f"Could not load web: {e}")
                    return None
        return self._web

    def _belief_to_summary(self, belief) -> BeliefSummary:
        """Convert a Belief object to BeliefSummary."""
        cred = belief.credence.value if hasattr(belief.credence, 'value') else belief.credence
        unc = belief.credence.uncertainty if hasattr(belief.credence, 'uncertainty') else 0.3
        level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)

        return BeliefSummary(
            belief_id=belief.belief_id,
            content=belief.content,
            level=level,
            credence=cred,
            uncertainty=unc,
            environment_id=belief.environment_id,
            outcome_id=belief.outcome_id,
            tags=getattr(belief, 'tags', [])
        )

    def _constraint_to_summary(self, constraint) -> ConstraintSummary:
        """Convert a Constraint object to ConstraintSummary."""
        ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)

        return ConstraintSummary(
            constraint_id=constraint.constraint_id,
            source_id=constraint.source_id,
            target_id=constraint.target_id,
            constraint_type=ctype,
            strength=constraint.strength
        )

    def _get_level_distance(self, level1: str, level2: str) -> int:
        """Calculate distance between two epistemic levels."""
        try:
            idx1 = self.LEVEL_ORDER.index(level1)
            idx2 = self.LEVEL_ORDER.index(level2)
            return abs(idx1 - idx2)
        except ValueError:
            return 0

    # Panel D6: Evidence quality weights per Cartwright's recommendation
    # Experimental evidence > Observational > Correlational
    EVIDENCE_QUALITY_WEIGHTS: Dict[str, float] = {
        'experimental': 3.0,      # Direct experimental test
        'observational': 2.0,     # Systematic observation
        'empirical': 1.5,         # General empirical finding
        'correlational': 1.0,     # Correlational evidence
        'intermediate': 1.0,      # Intermediate level
        'theoretical': 0.5,       # Theory-derived (not direct evidence)
    }

    def _get_evidence_quality(self, belief) -> str:
        """
        Determine evidence quality from belief tags or level.
        Panel D6: Cartwright - weight by evidence quality, not just count.
        """
        tags = getattr(belief, 'tags', [])

        # Check tags for evidence type
        for tag in tags:
            tag_lower = tag.lower()
            if 'experiment' in tag_lower or 'rct' in tag_lower:
                return 'experimental'
            if 'observat' in tag_lower:
                return 'observational'
            if 'correlat' in tag_lower:
                return 'correlational'

        # Fall back to level
        level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)
        return level

    def find_theory_support(self, theory_id: str) -> Optional[TheorySupportResult]:
        """
        Find empirical beliefs that support a theoretical belief.
        Panel D6: Weights evidence by quality per Cartwright's recommendation.

        Args:
            theory_id: ID of the theoretical belief

        Returns:
            TheorySupportResult with supporting beliefs and metrics
        """
        if not self.web:
            return None

        # Get the theory belief
        theory = self.web.beliefs.get(theory_id)
        if not theory:
            return None

        theory_summary = self._belief_to_summary(theory)

        # Find all beliefs connected to this theory
        supporting_beliefs = []
        evidence_qualities = []
        constraints_index = getattr(self.web, '_constraints_by_belief', {})

        related_constraints = constraints_index.get(theory_id, [])

        for constraint_id in related_constraints:
            constraint = self.web.constraints.get(constraint_id)
            if not constraint:
                continue

            # Get the other belief in this constraint
            other_id = constraint.target_id if constraint.source_id == theory_id else constraint.source_id
            other_belief = self.web.beliefs.get(other_id)

            if not other_belief:
                continue

            # Check if this is a supporting constraint from empirical/observational level
            other_level = other_belief.level.value if hasattr(other_belief.level, 'value') else str(other_belief.level)
            ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)

            if other_level in ['empirical', 'observational', 'intermediate']:
                if ctype in ['supports', 'instantiates', 'explains']:
                    supporting_beliefs.append(self._belief_to_summary(other_belief))
                    evidence_qualities.append(self._get_evidence_quality(other_belief))

        # Panel D6: Calculate quality-weighted support strength
        quality_weighted_support = 0.0
        evidence_quality_breakdown = {}
        total_weight = 0.0

        for belief, quality in zip(supporting_beliefs, evidence_qualities):
            weight = self.EVIDENCE_QUALITY_WEIGHTS.get(quality, 1.0)
            quality_weighted_support += belief.credence * weight
            total_weight += weight
            evidence_quality_breakdown[quality] = evidence_quality_breakdown.get(quality, 0) + 1

        if total_weight > 0:
            quality_weighted_support /= total_weight

        # Simple support strength (unweighted average)
        if supporting_beliefs:
            total_cred = sum(b.credence for b in supporting_beliefs)
            support_strength = total_cred / len(supporting_beliefs)
        else:
            support_strength = 0.0

        # Panel D6: Coverage score weights experimental evidence more heavily
        # One experimental test is worth more than five correlational findings
        weighted_count = sum(
            self.EVIDENCE_QUALITY_WEIGHTS.get(q, 1.0)
            for q in evidence_qualities
        )
        coverage_score = min(1.0, weighted_count / 6.0)  # 6.0 = two experimental tests

        # Identify gaps
        gaps = []
        if coverage_score < 0.4:
            gaps.append("Limited empirical support")
        if not any(b.level == 'observational' for b in supporting_beliefs):
            gaps.append("No direct observational evidence")
        if 'experimental' not in evidence_quality_breakdown:
            gaps.append("No experimental validation")

        return TheorySupportResult(
            theory_belief=theory_summary,
            supporting_beliefs=supporting_beliefs,
            support_strength=support_strength,
            coverage_score=coverage_score,
            gaps=gaps,
            quality_weighted_support=quality_weighted_support,
            evidence_quality_breakdown=evidence_quality_breakdown,
        )

    def find_empirical_grounding(self, empirical_id: str) -> Optional[CrossLayerQueryResult]:
        """
        Find theoretical beliefs that ground an empirical finding.

        Args:
            empirical_id: ID of the empirical belief

        Returns:
            CrossLayerQueryResult with theoretical grounding
        """
        if not self.web:
            return None

        empirical = self.web.beliefs.get(empirical_id)
        if not empirical:
            return None

        beliefs = [self._belief_to_summary(empirical)]
        connections = []
        layer_summary = {'theoretical': 0, 'intermediate': 0, 'empirical': 1, 'observational': 0}

        # Find theoretical beliefs connected to this empirical belief
        constraints_index = getattr(self.web, '_constraints_by_belief', {})
        related_constraints = constraints_index.get(empirical_id, [])

        for constraint_id in related_constraints:
            constraint = self.web.constraints.get(constraint_id)
            if not constraint:
                continue

            other_id = constraint.target_id if constraint.source_id == empirical_id else constraint.source_id
            other_belief = self.web.beliefs.get(other_id)

            if not other_belief:
                continue

            other_level = other_belief.level.value if hasattr(other_belief.level, 'value') else str(other_belief.level)

            if other_level in ['theoretical', 'intermediate']:
                other_summary = self._belief_to_summary(other_belief)
                beliefs.append(other_summary)
                layer_summary[other_level] = layer_summary.get(other_level, 0) + 1

                emp_level = empirical.level.value if hasattr(empirical.level, 'value') else str(empirical.level)
                connections.append(LayerConnection(
                    source_belief=self._belief_to_summary(empirical),
                    target_belief=other_summary,
                    constraint=self._constraint_to_summary(constraint),
                    layer_distance=self._get_level_distance(emp_level, other_level)
                ))

        return CrossLayerQueryResult(
            query_type=QueryType.EMPIRICAL_GROUNDING.value,
            query_params={"empirical_id": empirical_id},
            beliefs=beliefs,
            connections=connections,
            layer_summary=layer_summary,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

    def find_environment_outcome_beliefs(
        self,
        environment_id: Optional[str] = None,
        outcome_id: Optional[str] = None
    ) -> CrossLayerQueryResult:
        """
        Find beliefs connecting a specific environment to outcome.

        Args:
            environment_id: Filter by environment (e.g., 'daylight')
            outcome_id: Filter by outcome (e.g., 'stress')

        Returns:
            CrossLayerQueryResult with matching beliefs
        """
        if not self.web:
            return CrossLayerQueryResult(
                query_type=QueryType.ENVIRONMENT_OUTCOME.value,
                query_params={"environment_id": environment_id, "outcome_id": outcome_id},
                beliefs=[],
                connections=[],
                layer_summary={},
                generated_at=datetime.now(timezone.utc).isoformat()
            )

        beliefs = []
        layer_summary = {'theoretical': 0, 'intermediate': 0, 'empirical': 0, 'observational': 0}

        for belief in self.web.beliefs.values():
            # Filter by environment if specified
            if environment_id and belief.environment_id != environment_id:
                continue
            # Filter by outcome if specified
            if outcome_id and belief.outcome_id != outcome_id:
                continue

            summary = self._belief_to_summary(belief)
            beliefs.append(summary)

            level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)
            if level in layer_summary:
                layer_summary[level] += 1

        # Find connections between matching beliefs
        connections = []
        belief_ids = {b.belief_id for b in beliefs}

        for constraint in self.web.constraints.values():
            if constraint.source_id in belief_ids and constraint.target_id in belief_ids:
                source = self.web.beliefs.get(constraint.source_id)
                target = self.web.beliefs.get(constraint.target_id)
                if source and target:
                    source_level = source.level.value if hasattr(source.level, 'value') else str(source.level)
                    target_level = target.level.value if hasattr(target.level, 'value') else str(target.level)

                    connections.append(LayerConnection(
                        source_belief=self._belief_to_summary(source),
                        target_belief=self._belief_to_summary(target),
                        constraint=self._constraint_to_summary(constraint),
                        layer_distance=self._get_level_distance(source_level, target_level)
                    ))

        return CrossLayerQueryResult(
            query_type=QueryType.ENVIRONMENT_OUTCOME.value,
            query_params={"environment_id": environment_id, "outcome_id": outcome_id},
            beliefs=beliefs,
            connections=connections,
            layer_summary=layer_summary,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

    def find_cross_layer_conflicts(self) -> CrossLayerQueryResult:
        """
        Find conflicts between beliefs at different epistemic layers.

        Returns:
            CrossLayerQueryResult with conflicting beliefs
        """
        if not self.web:
            return CrossLayerQueryResult(
                query_type=QueryType.LAYER_CONFLICTS.value,
                query_params={},
                beliefs=[],
                connections=[],
                layer_summary={},
                generated_at=datetime.now(timezone.utc).isoformat()
            )

        conflicting_beliefs = set()
        connections = []
        layer_summary = {'theoretical': 0, 'intermediate': 0, 'empirical': 0, 'observational': 0}

        for constraint in self.web.constraints.values():
            ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)

            if ctype == 'contradicts':
                source = self.web.beliefs.get(constraint.source_id)
                target = self.web.beliefs.get(constraint.target_id)

                if source and target:
                    source_level = source.level.value if hasattr(source.level, 'value') else str(source.level)
                    target_level = target.level.value if hasattr(target.level, 'value') else str(target.level)

                    # Only include if beliefs are at different levels
                    if source_level != target_level:
                        conflicting_beliefs.add(constraint.source_id)
                        conflicting_beliefs.add(constraint.target_id)

                        connections.append(LayerConnection(
                            source_belief=self._belief_to_summary(source),
                            target_belief=self._belief_to_summary(target),
                            constraint=self._constraint_to_summary(constraint),
                            layer_distance=self._get_level_distance(source_level, target_level)
                        ))

        # Collect belief summaries
        beliefs = []
        for belief_id in conflicting_beliefs:
            belief = self.web.beliefs.get(belief_id)
            if belief:
                beliefs.append(self._belief_to_summary(belief))
                level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)
                if level in layer_summary:
                    layer_summary[level] += 1

        return CrossLayerQueryResult(
            query_type=QueryType.LAYER_CONFLICTS.value,
            query_params={},
            beliefs=beliefs,
            connections=connections,
            layer_summary=layer_summary,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

    def get_belief_chain(self, belief_id: str, max_depth: int = 5) -> CrossLayerQueryResult:
        """
        Get the full chain of beliefs connected to a given belief.
        Traces both up (towards theory) and down (towards observation).

        Args:
            belief_id: Starting belief ID
            max_depth: Maximum traversal depth

        Returns:
            CrossLayerQueryResult with the belief chain
        """
        if not self.web:
            return CrossLayerQueryResult(
                query_type=QueryType.BELIEF_CHAIN.value,
                query_params={"belief_id": belief_id, "max_depth": max_depth},
                beliefs=[],
                connections=[],
                layer_summary={},
                generated_at=datetime.now(timezone.utc).isoformat()
            )

        start_belief = self.web.beliefs.get(belief_id)
        if not start_belief:
            return CrossLayerQueryResult(
                query_type=QueryType.BELIEF_CHAIN.value,
                query_params={"belief_id": belief_id, "max_depth": max_depth},
                beliefs=[],
                connections=[],
                layer_summary={},
                generated_at=datetime.now(timezone.utc).isoformat()
            )

        # BFS to find all connected beliefs up to max_depth
        visited = {belief_id}
        queue = [(belief_id, 0)]
        beliefs = [self._belief_to_summary(start_belief)]
        connections = []
        layer_summary = {'theoretical': 0, 'intermediate': 0, 'empirical': 0, 'observational': 0}

        start_level = start_belief.level.value if hasattr(start_belief.level, 'value') else str(start_belief.level)
        if start_level in layer_summary:
            layer_summary[start_level] += 1

        constraints_index = getattr(self.web, '_constraints_by_belief', {})

        while queue:
            current_id, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            related_constraints = constraints_index.get(current_id, [])

            for constraint_id in related_constraints:
                constraint = self.web.constraints.get(constraint_id)
                if not constraint:
                    continue

                other_id = constraint.target_id if constraint.source_id == current_id else constraint.source_id

                if other_id in visited:
                    continue

                other_belief = self.web.beliefs.get(other_id)
                if not other_belief:
                    continue

                visited.add(other_id)
                queue.append((other_id, depth + 1))

                other_summary = self._belief_to_summary(other_belief)
                beliefs.append(other_summary)

                other_level = other_belief.level.value if hasattr(other_belief.level, 'value') else str(other_belief.level)
                if other_level in layer_summary:
                    layer_summary[other_level] += 1

                current_belief = self.web.beliefs.get(current_id)
                if current_belief:
                    current_level = current_belief.level.value if hasattr(current_belief.level, 'value') else str(current_belief.level)
                    connections.append(LayerConnection(
                        source_belief=self._belief_to_summary(current_belief),
                        target_belief=other_summary,
                        constraint=self._constraint_to_summary(constraint),
                        layer_distance=self._get_level_distance(current_level, other_level)
                    ))

        return CrossLayerQueryResult(
            query_type=QueryType.BELIEF_CHAIN.value,
            query_params={"belief_id": belief_id, "max_depth": max_depth},
            beliefs=beliefs,
            connections=connections,
            layer_summary=layer_summary,
            generated_at=datetime.now(timezone.utc).isoformat()
        )

    def get_layer_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about beliefs across layers.

        Returns:
            Dictionary with layer statistics
        """
        if not self.web:
            return {"error": "Web not available"}

        stats = {
            "total_beliefs": len(self.web.beliefs),
            "total_constraints": len(self.web.constraints),
            "by_level": {},
            "cross_layer_connections": 0,
            "within_layer_connections": 0,
            "constraint_types": {}
        }

        # Count beliefs by level
        for belief in self.web.beliefs.values():
            level = belief.level.value if hasattr(belief.level, 'value') else str(belief.level)
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

        # Analyze constraints
        for constraint in self.web.constraints.values():
            source = self.web.beliefs.get(constraint.source_id)
            target = self.web.beliefs.get(constraint.target_id)

            if source and target:
                source_level = source.level.value if hasattr(source.level, 'value') else str(source.level)
                target_level = target.level.value if hasattr(target.level, 'value') else str(target.level)

                if source_level == target_level:
                    stats["within_layer_connections"] += 1
                else:
                    stats["cross_layer_connections"] += 1

            ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)
            stats["constraint_types"][ctype] = stats["constraint_types"].get(ctype, 0) + 1

        return stats


# Singleton accessor
_query_service = None

def get_cross_layer_service() -> CrossLayerQueryService:
    """Get or create the cross-layer query service."""
    global _query_service
    if _query_service is None:
        _query_service = CrossLayerQueryService()
    return _query_service
