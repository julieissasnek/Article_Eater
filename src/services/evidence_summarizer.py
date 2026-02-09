"""
Evidence Summary Generator — Sprint 3.0.4-A
2026-02-09

Generates evidence summaries with scope metadata per Cartwright's philosophy.
Includes transferability assessments, confidence intervals, and caveats.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class EvidenceStrength(Enum):
    """Overall strength of evidence for a claim."""
    STRONG = "strong"           # High credence, multiple sources, consistent
    MODERATE = "moderate"       # Good credence, some variation
    WEAK = "weak"               # Low credence or limited sources
    MIXED = "mixed"             # Conflicting evidence
    INSUFFICIENT = "insufficient"  # Not enough data


class TransferabilityLevel(Enum):
    """How transferable findings are to new contexts."""
    HIGH = "high"               # Broad scope, replicated across contexts
    MODERATE = "moderate"       # Some scope limits, moderate replication
    LOW = "low"                 # Narrow scope, context-dependent
    UNKNOWN = "unknown"         # Insufficient scope metadata


class CaveatType(Enum):
    """Types of caveats for evidence interpretation."""
    SCOPE_LIMITATION = "scope_limitation"
    METHODOLOGICAL = "methodological"
    SAMPLE_SIZE = "sample_size"
    REPLICATION = "replication"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    ECOLOGICAL_VALIDITY = "ecological_validity"
    TEMPORAL = "temporal"
    CULTURAL = "cultural"
    MEASUREMENT = "measurement"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ScopeMetadata:
    """Scope information per Cartwright's capacities framework."""
    population: Optional[str] = None
    setting: Optional[str] = None
    duration: Optional[str] = None
    intervention_type: Optional[str] = None
    outcome_measure: Optional[str] = None

    # Cartwright-specific
    enabling_conditions: List[str] = field(default_factory=list)
    boundary_conditions: List[str] = field(default_factory=list)
    known_moderators: List[str] = field(default_factory=list)

    # Transferability assessment
    generalization_risk: Optional[float] = None  # 0-1, higher = riskier
    context_sensitivity: Optional[str] = None    # low/medium/high

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None and v != []}


@dataclass
class EvidenceCaveat:
    """A caveat or limitation on evidence interpretation."""
    caveat_type: CaveatType
    description: str
    severity: str = "medium"  # low, medium, high
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.caveat_type.value,
            "description": self.description,
            "severity": self.severity,
            "recommendation": self.recommendation
        }


@dataclass
class SourceEvidence:
    """Evidence from a single source/paper."""
    paper_id: str
    paper_title: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None

    finding: Optional[str] = None
    effect_size: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    sample_size: Optional[int] = None
    methodology: Optional[str] = None

    credence: Optional[float] = None
    credence_uncertainty: Optional[float] = None

    scope: Optional[ScopeMetadata] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "paper_id": self.paper_id,
            "paper_title": self.paper_title,
            "authors": self.authors,
            "year": self.year,
            "finding": self.finding,
            "effect_size": self.effect_size,
            "sample_size": self.sample_size,
            "methodology": self.methodology,
            "credence": self.credence,
            "credence_uncertainty": self.credence_uncertainty
        }
        if self.confidence_interval:
            d["confidence_interval"] = list(self.confidence_interval)
        if self.scope:
            d["scope"] = self.scope.to_dict()
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class EvidenceSynthesis:
    """Synthesized view across multiple sources."""
    pooled_credence: float
    pooled_uncertainty: float
    n_sources: int

    heterogeneity: Optional[float] = None  # I-squared or similar
    consistency: Optional[str] = None      # consistent/mixed/conflicting

    pooled_effect_size: Optional[float] = None
    pooled_ci: Optional[Tuple[float, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "pooled_credence": self.pooled_credence,
            "pooled_uncertainty": self.pooled_uncertainty,
            "n_sources": self.n_sources,
            "heterogeneity": self.heterogeneity,
            "consistency": self.consistency,
            "pooled_effect_size": self.pooled_effect_size
        }
        if self.pooled_ci:
            d["pooled_confidence_interval"] = list(self.pooled_ci)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class EvidenceSummary:
    """Complete evidence summary for a claim or topic."""
    claim_id: Optional[str] = None
    claim_content: Optional[str] = None
    topic: Optional[str] = None

    # Overall assessment
    strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT
    transferability: TransferabilityLevel = TransferabilityLevel.UNKNOWN

    # Synthesis
    synthesis: Optional[EvidenceSynthesis] = None

    # Sources
    sources: List[SourceEvidence] = field(default_factory=list)

    # Scope
    combined_scope: Optional[ScopeMetadata] = None
    scope_gaps: List[str] = field(default_factory=list)

    # Caveats
    caveats: List[EvidenceCaveat] = field(default_factory=list)

    # Practical implications
    implications: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_content": self.claim_content,
            "topic": self.topic,
            "strength": self.strength.value,
            "transferability": self.transferability.value,
            "synthesis": self.synthesis.to_dict() if self.synthesis else None,
            "sources": [s.to_dict() for s in self.sources],
            "combined_scope": self.combined_scope.to_dict() if self.combined_scope else None,
            "scope_gaps": self.scope_gaps,
            "caveats": [c.to_dict() for c in self.caveats],
            "implications": self.implications,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at,
            "version": self.version
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Generate markdown summary."""
        lines = []

        # Header
        if self.claim_content:
            lines.append(f"# Evidence Summary: {self.claim_content[:80]}...")
        elif self.topic:
            lines.append(f"# Evidence Summary: {self.topic}")
        else:
            lines.append("# Evidence Summary")

        lines.append("")
        lines.append(f"**Generated**: {self.generated_at[:10]}")
        lines.append(f"**Strength**: {self.strength.value.title()}")
        lines.append(f"**Transferability**: {self.transferability.value.title()}")
        lines.append("")

        # Synthesis
        if self.synthesis:
            lines.append("## Synthesis")
            lines.append("")
            lines.append(f"- **Pooled Credence**: {self.synthesis.pooled_credence:.2f} "
                        f"(+/- {self.synthesis.pooled_uncertainty:.2f})")
            lines.append(f"- **Sources**: {self.synthesis.n_sources}")
            if self.synthesis.consistency:
                lines.append(f"- **Consistency**: {self.synthesis.consistency}")
            if self.synthesis.pooled_effect_size is not None:
                lines.append(f"- **Effect Size**: {self.synthesis.pooled_effect_size:.3f}")
            lines.append("")

        # Sources
        if self.sources:
            lines.append("## Sources")
            lines.append("")
            for i, src in enumerate(self.sources, 1):
                author_year = f"{src.authors}, {src.year}" if src.authors and src.year else src.paper_id
                lines.append(f"### {i}. {author_year}")
                if src.finding:
                    lines.append(f"- **Finding**: {src.finding}")
                if src.credence is not None:
                    lines.append(f"- **Credence**: {src.credence:.2f}")
                if src.sample_size:
                    lines.append(f"- **Sample**: n={src.sample_size}")
                if src.methodology:
                    lines.append(f"- **Method**: {src.methodology}")
                lines.append("")

        # Scope
        if self.combined_scope:
            lines.append("## Scope Conditions")
            lines.append("")
            scope = self.combined_scope
            if scope.population:
                lines.append(f"- **Population**: {scope.population}")
            if scope.setting:
                lines.append(f"- **Setting**: {scope.setting}")
            if scope.duration:
                lines.append(f"- **Duration**: {scope.duration}")
            if scope.enabling_conditions:
                lines.append(f"- **Enabling Conditions**: {', '.join(scope.enabling_conditions)}")
            if scope.boundary_conditions:
                lines.append(f"- **Boundary Conditions**: {', '.join(scope.boundary_conditions)}")
            if scope.known_moderators:
                lines.append(f"- **Known Moderators**: {', '.join(scope.known_moderators)}")
            lines.append("")

        # Scope gaps
        if self.scope_gaps:
            lines.append("## Scope Gaps")
            lines.append("")
            for gap in self.scope_gaps:
                lines.append(f"- {gap}")
            lines.append("")

        # Caveats
        if self.caveats:
            lines.append("## Caveats")
            lines.append("")
            for caveat in self.caveats:
                severity_marker = {"low": "", "medium": "!", "high": "!!"}
                marker = severity_marker.get(caveat.severity, "")
                lines.append(f"- **{caveat.caveat_type.value.replace('_', ' ').title()}**{marker}: "
                           f"{caveat.description}")
                if caveat.recommendation:
                    lines.append(f"  - *Recommendation*: {caveat.recommendation}")
            lines.append("")

        # Implications
        if self.implications:
            lines.append("## Practical Implications")
            lines.append("")
            for impl in self.implications:
                lines.append(f"- {impl}")
            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Evidence Summarizer Service
# =============================================================================

class EvidenceSummarizer:
    """
    Generates evidence summaries with Cartwright-style scope analysis.

    Key principles:
    1. Scope matters - findings don't automatically transfer
    2. Enabling conditions must be checked
    3. Heterogeneity indicates context sensitivity
    4. Caveats are first-class citizens
    """

    # Per P-S3-C Panel (Cartwright): Level-dependent credence thresholds
    # Theoretical claims require stricter standards; empirical data is more lenient
    LEVEL_CREDENCE_THRESHOLDS = {
        "theoretical": {"low": 0.5, "high": 0.8},
        "intermediate": {"low": 0.4, "high": 0.7},
        "empirical": {"low": 0.3, "high": 0.6},
        "observational": {"low": 0.2, "high": 0.5},
    }

    def __init__(
        self,
        min_sources_for_synthesis: int = 2,
        high_heterogeneity_threshold: float = 0.5,
        high_credence_threshold: float = 0.7,
        low_credence_threshold: float = 0.4,
        use_level_dependent_thresholds: bool = True
    ):
        """
        Initialize evidence summarizer.

        Per P-S3-C Panel (Cartwright, Higgins):
        - use_level_dependent_thresholds: If True, credence thresholds vary by
          epistemic level (theoretical vs empirical)
        """
        self.min_sources_for_synthesis = min_sources_for_synthesis
        self.high_heterogeneity_threshold = high_heterogeneity_threshold
        self.high_credence_threshold = high_credence_threshold
        self.low_credence_threshold = low_credence_threshold
        self.use_level_dependent_thresholds = use_level_dependent_thresholds

    def _get_thresholds_for_level(self, level: Optional[str] = None) -> Dict[str, float]:
        """
        Get credence thresholds appropriate for epistemic level.

        Per P-S3-C Panel (Cartwright): Different standards for different levels.
        """
        if not self.use_level_dependent_thresholds or level is None:
            return {"low": self.low_credence_threshold, "high": self.high_credence_threshold}

        level_str = level.value if hasattr(level, 'value') else str(level).lower()
        return self.LEVEL_CREDENCE_THRESHOLDS.get(
            level_str,
            {"low": self.low_credence_threshold, "high": self.high_credence_threshold}
        )

    def summarize_belief(
        self,
        belief: Any,
        web: Optional[Any] = None,
        include_sources: bool = True
    ) -> EvidenceSummary:
        """
        Create evidence summary from a Belief object.

        Args:
            belief: Belief object from web_of_belief
            web: Optional WebOfBelief for additional context
            include_sources: Whether to include detailed source info

        Returns:
            EvidenceSummary with scope metadata and caveats
        """
        summary = EvidenceSummary(
            claim_id=getattr(belief, 'belief_id', None),
            claim_content=getattr(belief, 'content', None)
        )

        # Extract credence
        credence_obj = getattr(belief, 'credence', None)
        if credence_obj:
            credence_val = getattr(credence_obj, 'value', None)
            credence_unc = getattr(credence_obj, 'uncertainty', None)

            if credence_val is not None:
                summary.synthesis = EvidenceSynthesis(
                    pooled_credence=credence_val,
                    pooled_uncertainty=credence_unc or 0.2,
                    n_sources=len(getattr(belief, 'paper_ids', []) or [])
                )

        # Build sources from paper_ids
        if include_sources:
            paper_ids = getattr(belief, 'paper_ids', []) or []
            for paper_id in paper_ids:
                source = SourceEvidence(
                    paper_id=paper_id,
                    credence=credence_obj.value if credence_obj else None,
                    credence_uncertainty=credence_obj.uncertainty if credence_obj else None
                )
                summary.sources.append(source)

        # Extract scope from belief
        scope_cond = getattr(belief, 'scope_conditions', None)
        if scope_cond:
            summary.combined_scope = ScopeMetadata(
                population=getattr(scope_cond, 'population', None),
                setting=getattr(scope_cond, 'setting', None),
                duration=getattr(scope_cond, 'duration', None),
                enabling_conditions=getattr(scope_cond, 'enabling_conditions', []) or [],
                boundary_conditions=getattr(scope_cond, 'boundary_conditions', []) or [],
                known_moderators=getattr(scope_cond, 'moderators', []) or []
            )

        # Assess strength
        summary.strength = self._assess_strength(summary)

        # Assess transferability
        summary.transferability = self._assess_transferability(summary)

        # Generate caveats
        summary.caveats = self._generate_caveats(belief, summary)

        # Generate implications
        summary.implications = self._generate_implications(belief, summary)

        return summary

    def summarize_beliefs(
        self,
        beliefs: List[Any],
        topic: Optional[str] = None,
        web: Optional[Any] = None
    ) -> EvidenceSummary:
        """
        Create synthesized evidence summary from multiple beliefs.

        Args:
            beliefs: List of Belief objects
            topic: Topic label for the summary
            web: Optional WebOfBelief for context

        Returns:
            Synthesized EvidenceSummary
        """
        if not beliefs:
            return EvidenceSummary(
                topic=topic,
                strength=EvidenceStrength.INSUFFICIENT
            )

        summary = EvidenceSummary(topic=topic)

        # Collect all sources
        all_sources: List[SourceEvidence] = []
        credences: List[float] = []
        uncertainties: List[float] = []

        for belief in beliefs:
            credence_obj = getattr(belief, 'credence', None)
            if credence_obj and hasattr(credence_obj, 'value'):
                credences.append(credence_obj.value)
                uncertainties.append(getattr(credence_obj, 'uncertainty', 0.2))

            paper_ids = getattr(belief, 'paper_ids', []) or []
            for paper_id in paper_ids:
                source = SourceEvidence(
                    paper_id=paper_id,
                    finding=getattr(belief, 'content', None),
                    credence=credence_obj.value if credence_obj else None
                )
                all_sources.append(source)

        summary.sources = all_sources

        # Compute synthesis
        if credences:
            # Inverse-variance weighted mean
            weights = [1.0 / (u ** 2) if u > 0 else 1.0 for u in uncertainties]
            total_weight = sum(weights)

            pooled = sum(c * w for c, w in zip(credences, weights)) / total_weight
            pooled_var = 1.0 / total_weight
            pooled_unc = pooled_var ** 0.5

            # Assess heterogeneity (simplified)
            if len(credences) > 1:
                mean_c = sum(credences) / len(credences)
                variance = sum((c - mean_c) ** 2 for c in credences) / len(credences)
                heterogeneity = min(1.0, variance / 0.1)  # Normalize to 0-1
            else:
                heterogeneity = 0.0

            # Assess consistency
            if heterogeneity < 0.2:
                consistency = "consistent"
            elif heterogeneity < 0.5:
                consistency = "mixed"
            else:
                consistency = "conflicting"

            summary.synthesis = EvidenceSynthesis(
                pooled_credence=pooled,
                pooled_uncertainty=pooled_unc,
                n_sources=len(all_sources),
                heterogeneity=heterogeneity,
                consistency=consistency
            )

        # Combine scope from all beliefs
        summary.combined_scope = self._combine_scopes(beliefs)

        # Identify scope gaps
        summary.scope_gaps = self._identify_scope_gaps(beliefs)

        # Assess overall strength
        summary.strength = self._assess_strength(summary)

        # Assess transferability
        summary.transferability = self._assess_transferability(summary)

        # Generate caveats
        summary.caveats = self._generate_multi_caveats(beliefs, summary)

        return summary

    def summarize_query_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> EvidenceSummary:
        """
        Create evidence summary from query results.

        Args:
            results: List of result dicts with belief_id, content, credence, etc.
            query: The original query string

        Returns:
            EvidenceSummary for the query
        """
        summary = EvidenceSummary(topic=query)

        credences = []
        for result in results:
            credence = result.get('credence')
            if isinstance(credence, dict):
                credences.append(credence.get('value', 0.5))
            elif isinstance(credence, (int, float)):
                credences.append(float(credence))

            source = SourceEvidence(
                paper_id=result.get('paper_id', result.get('belief_id', 'unknown')),
                finding=result.get('content'),
                credence=credences[-1] if credences else None
            )
            summary.sources.append(source)

        if credences:
            summary.synthesis = EvidenceSynthesis(
                pooled_credence=sum(credences) / len(credences),
                pooled_uncertainty=0.15,
                n_sources=len(results)
            )

        summary.strength = self._assess_strength(summary)
        summary.transferability = self._assess_transferability(summary)

        return summary

    def _assess_strength(
        self,
        summary: EvidenceSummary,
        epistemic_level: Optional[str] = None
    ) -> EvidenceStrength:
        """
        Assess overall evidence strength.

        Per P-S3-C Panel (Cartwright, Mayo):
        - Use level-dependent thresholds (theoretical requires stricter standards)
        - Account for uncertainty in credence (effective credence = mean - 0.5*uncertainty)
        """
        if not summary.synthesis:
            return EvidenceStrength.INSUFFICIENT

        synth = summary.synthesis

        # Check for conflicts
        if synth.consistency == "conflicting":
            return EvidenceStrength.MIXED

        # Per P-S3-C Panel (Mayo): Use effective credence accounting for uncertainty
        uncertainty = synth.pooled_uncertainty or 0.0
        effective_credence = synth.pooled_credence - (uncertainty * 0.5)

        # Per P-S3-C Panel (Cartwright): Get level-appropriate thresholds
        thresholds = self._get_thresholds_for_level(epistemic_level)
        high_threshold = thresholds["high"]
        low_threshold = thresholds["low"]

        # Assess strength using effective credence and level-dependent thresholds
        if effective_credence >= high_threshold:
            if synth.n_sources >= 3:
                return EvidenceStrength.STRONG
            return EvidenceStrength.MODERATE
        elif effective_credence >= low_threshold:
            return EvidenceStrength.MODERATE
        else:
            return EvidenceStrength.WEAK

    def _assess_transferability(self, summary: EvidenceSummary) -> TransferabilityLevel:
        """Assess how transferable findings are (Cartwright capacities)."""
        if not summary.combined_scope:
            return TransferabilityLevel.UNKNOWN

        scope = summary.combined_scope

        # Check for explicit scope limitations
        has_narrow_population = scope.population and any(
            term in scope.population.lower()
            for term in ['students', 'elderly', 'children', 'patients', 'workers']
        )

        has_specific_setting = scope.setting and any(
            term in scope.setting.lower()
            for term in ['laboratory', 'hospital', 'school', 'specific']
        )

        has_enabling_conditions = bool(scope.enabling_conditions)
        has_boundary_conditions = bool(scope.boundary_conditions)

        # Count limiting factors
        limiting_factors = sum([
            1 if has_narrow_population else 0,
            1 if has_specific_setting else 0,
            1 if has_enabling_conditions else 0,
            1 if has_boundary_conditions else 0,
            1 if (scope.generalization_risk or 0) > 0.5 else 0,
            1 if scope.context_sensitivity == "high" else 0
        ])

        if limiting_factors == 0:
            return TransferabilityLevel.HIGH
        elif limiting_factors <= 2:
            return TransferabilityLevel.MODERATE
        else:
            return TransferabilityLevel.LOW

    def _combine_scopes(self, beliefs: List[Any]) -> Optional[ScopeMetadata]:
        """Combine scope conditions from multiple beliefs."""
        populations = set()
        settings = set()
        enabling = set()
        boundary = set()
        moderators = set()

        for belief in beliefs:
            scope = getattr(belief, 'scope_conditions', None)
            if not scope:
                continue

            if hasattr(scope, 'population') and scope.population:
                populations.add(scope.population)
            if hasattr(scope, 'setting') and scope.setting:
                settings.add(scope.setting)
            if hasattr(scope, 'enabling_conditions'):
                enabling.update(scope.enabling_conditions or [])
            if hasattr(scope, 'boundary_conditions'):
                boundary.update(scope.boundary_conditions or [])
            if hasattr(scope, 'moderators'):
                moderators.update(scope.moderators or [])

        if not (populations or settings or enabling or boundary):
            return None

        return ScopeMetadata(
            population="; ".join(populations) if populations else None,
            setting="; ".join(settings) if settings else None,
            enabling_conditions=list(enabling),
            boundary_conditions=list(boundary),
            known_moderators=list(moderators)
        )

    def _identify_scope_gaps(self, beliefs: List[Any]) -> List[str]:
        """Identify gaps in scope coverage."""
        gaps = []

        has_population = False
        has_setting = False
        has_duration = False

        for belief in beliefs:
            scope = getattr(belief, 'scope_conditions', None)
            if scope:
                if hasattr(scope, 'population') and scope.population:
                    has_population = True
                if hasattr(scope, 'setting') and scope.setting:
                    has_setting = True
                if hasattr(scope, 'duration') and scope.duration:
                    has_duration = True

        if not has_population:
            gaps.append("Population characteristics not specified")
        if not has_setting:
            gaps.append("Setting/context not specified")
        if not has_duration:
            gaps.append("Duration/temporal scope not specified")

        return gaps

    def _generate_caveats(
        self,
        belief: Any,
        summary: EvidenceSummary
    ) -> List[EvidenceCaveat]:
        """Generate caveats for a single belief summary."""
        caveats = []

        # Check source count
        if summary.synthesis and summary.synthesis.n_sources < 3:
            caveats.append(EvidenceCaveat(
                caveat_type=CaveatType.REPLICATION,
                description=f"Based on only {summary.synthesis.n_sources} source(s)",
                severity="medium",
                recommendation="Seek additional replication studies"
            ))

        # Check scope
        if summary.transferability == TransferabilityLevel.LOW:
            caveats.append(EvidenceCaveat(
                caveat_type=CaveatType.SCOPE_LIMITATION,
                description="Findings have narrow scope conditions",
                severity="high",
                recommendation="Verify enabling conditions before applying"
            ))

        # Check credence
        if summary.synthesis and summary.synthesis.pooled_credence < 0.5:
            caveats.append(EvidenceCaveat(
                caveat_type=CaveatType.CONFLICTING_EVIDENCE,
                description="Low overall credence suggests uncertainty",
                severity="medium"
            ))

        return caveats

    def _generate_multi_caveats(
        self,
        beliefs: List[Any],
        summary: EvidenceSummary
    ) -> List[EvidenceCaveat]:
        """Generate caveats for multi-belief summary."""
        caveats = []

        # Check heterogeneity
        if summary.synthesis and summary.synthesis.heterogeneity:
            if summary.synthesis.heterogeneity > self.high_heterogeneity_threshold:
                caveats.append(EvidenceCaveat(
                    caveat_type=CaveatType.CONFLICTING_EVIDENCE,
                    description="High heterogeneity across sources suggests context-dependent effects",
                    severity="high",
                    recommendation="Investigate moderating factors"
                ))

        # Check scope gaps
        if summary.scope_gaps:
            caveats.append(EvidenceCaveat(
                caveat_type=CaveatType.SCOPE_LIMITATION,
                description=f"Scope metadata incomplete: {', '.join(summary.scope_gaps)}",
                severity="medium",
                recommendation="Obtain missing scope information before generalizing"
            ))

        # Check replication
        if summary.synthesis and summary.synthesis.n_sources < self.min_sources_for_synthesis:
            caveats.append(EvidenceCaveat(
                caveat_type=CaveatType.REPLICATION,
                description="Insufficient sources for robust synthesis",
                severity="high"
            ))

        return caveats

    def _generate_implications(
        self,
        belief: Any,
        summary: EvidenceSummary
    ) -> List[str]:
        """Generate practical implications."""
        implications = []

        if summary.strength in [EvidenceStrength.STRONG, EvidenceStrength.MODERATE]:
            content = getattr(belief, 'content', '')
            if content:
                # Simple implication generation
                implications.append(f"Evidence supports: {content[:100]}...")

        if summary.transferability == TransferabilityLevel.HIGH:
            implications.append("Findings likely applicable across contexts")
        elif summary.transferability == TransferabilityLevel.LOW:
            implications.append("Apply with caution; verify local conditions")

        return implications


# =============================================================================
# Convenience Functions
# =============================================================================

def create_evidence_summary(
    belief: Any,
    web: Optional[Any] = None
) -> EvidenceSummary:
    """Create evidence summary from a belief."""
    summarizer = EvidenceSummarizer()
    return summarizer.summarize_belief(belief, web)


def create_topic_summary(
    beliefs: List[Any],
    topic: str,
    web: Optional[Any] = None
) -> EvidenceSummary:
    """Create synthesized summary for a topic."""
    summarizer = EvidenceSummarizer()
    return summarizer.summarize_beliefs(beliefs, topic, web)


def format_evidence_markdown(summary: EvidenceSummary) -> str:
    """Format evidence summary as markdown."""
    return summary.to_markdown()


def format_evidence_json(summary: EvidenceSummary) -> str:
    """Format evidence summary as JSON."""
    return summary.to_json()
