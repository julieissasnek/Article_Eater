"""
Reporting Service
=================

Generates reports and summaries from the web of belief.

Per expert panel:
- Clear epistemic summary (Pearl)
- Highlight gaps and uncertainties (Simon)
- Source depth transparency (Cartwright)

Date: January 21, 2026
Phase D Sprint D2
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from datetime import datetime

from src.services.web_of_belief import WebOfBelief, Belief, SourceDepth

# H2: Import taxonomy for dynamic outcome categories (per Kaplan panel recommendation)
try:
    from src.services.outcome_taxonomy import ExtendedOutcomeTaxonomy
    TAXONOMY_AVAILABLE = True
except ImportError:
    TAXONOMY_AVAILABLE = False


# =============================================================================
# Report Types
# =============================================================================

class ReportType(Enum):
    """Types of reports available."""
    EXECUTIVE_SUMMARY = "executive"      # High-level overview
    EVIDENCE_INVENTORY = "inventory"     # Complete evidence listing
    CONFIDENCE_ANALYSIS = "confidence"   # Confidence assessment
    GAP_ANALYSIS = "gaps"                # What we don't know
    QUALITY_ASSESSMENT = "quality"       # Evidence quality report
    TOPIC_DEEP_DIVE = "topic"           # Deep dive on specific topic
    CONTRADICTION_REPORT = "contradictions"  # Areas of disagreement


@dataclass
class ReportSection:
    """A section within a report."""
    title: str
    content: str
    data: Optional[Dict[str, Any]] = None
    subsections: List['ReportSection'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'content': self.content,
            'data': self.data,
            'subsections': [s.to_dict() for s in self.subsections]
        }


@dataclass
class Report:
    """A complete report."""
    report_type: ReportType
    title: str
    generated_at: str
    summary: str
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_type': self.report_type.value,
            'title': self.title,
            'generated_at': self.generated_at,
            'summary': self.summary,
            'sections': [s.to_dict() for s in self.sections],
            'metadata': self.metadata
        }


# =============================================================================
# Report Generator
# =============================================================================

class ReportGenerator:
    """
    Generates various reports from the web of belief.

    Provides multiple report types for different audiences
    and purposes.
    """

    # H2: Fallback outcome categories (used only if taxonomy unavailable)
    # E1.D3 (per Kaplan): Added physio.stress (distinct from affect.stress)
    # F1.3: Expanded per Kaplan (ruthless review 2026-01-22)
    # Panel validation (2026-01-22): Added missing outcomes per Kaplan (M3)
    _FALLBACK_OUTCOME_CATEGORIES = {
        # Original categories
        'behav.productivity', 'cog.performance', 'affect.stress', 'health.wellbeing',
        'health', 'cog.attention', 'affect.mood', 'physio.stress',
        # F1.3: Expanded outcomes per Kaplan
        'cog.creativity',       # Creative thinking
        'behav.collaboration',  # Teamwork, communication
        'physio.circadian',     # Circadian rhythm measures
        'affect.satisfaction',  # Job/space satisfaction
        'cog.focus',           # Concentration, focus
        'physio.cortisol',     # Stress hormone
        'behav.absenteeism',   # Attendance patterns
        # Panel validation (2026-01-22): M3 additions per Kaplan
        'behav.social',        # Social interaction, communication frequency
        'affect.privacy',      # Perceived privacy satisfaction
        'cog.wayfinding',      # Navigation, spatial orientation
        'affect.control',      # Perceived environmental control
    }

    def __init__(self, web: WebOfBelief):
        """Initialize with a web of belief."""
        self.web = web
        self._taxonomy: Optional[ExtendedOutcomeTaxonomy] = None
        if TAXONOMY_AVAILABLE:
            try:
                self._taxonomy = ExtendedOutcomeTaxonomy()
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")  # Fall back to hardcoded

    def _get_expected_outcomes(self) -> Set[str]:
        """
        Get expected outcome categories from taxonomy.

        H2 (per Kaplan panel): Derive outcomes dynamically from taxonomy
        rather than hardcoding them.

        Returns:
            Set of outcome IDs to check for coverage
        """
        if self._taxonomy:
            # Get top-level domains from taxonomy
            outcomes = set()
            for outcome in self._taxonomy.get_all_outcomes():
                # Include domain-level and one level below
                parts = outcome.outcome_id.split('.')
                if len(parts) <= 2:  # Top-level domains and immediate children
                    outcomes.add(outcome.outcome_id)
            return outcomes if outcomes else self._FALLBACK_OUTCOME_CATEGORIES
        return self._FALLBACK_OUTCOME_CATEGORIES

    def generate(
        self,
        report_type: ReportType,
        topic: Optional[str] = None
    ) -> Report:
        """
        Generate a report of the specified type.

        Args:
            report_type: Type of report to generate
            topic: Optional topic to focus on

        Returns:
            Complete Report object
        """
        generators = {
            ReportType.EXECUTIVE_SUMMARY: self._generate_executive_summary,
            ReportType.EVIDENCE_INVENTORY: self._generate_evidence_inventory,
            ReportType.CONFIDENCE_ANALYSIS: self._generate_confidence_analysis,
            ReportType.GAP_ANALYSIS: self._generate_gap_analysis,
            ReportType.QUALITY_ASSESSMENT: self._generate_quality_assessment,
            ReportType.TOPIC_DEEP_DIVE: self._generate_topic_deep_dive,
            ReportType.CONTRADICTION_REPORT: self._generate_contradiction_report,
        }

        generator = generators.get(report_type, self._generate_executive_summary)
        return generator(topic)

    def _generate_executive_summary(self, topic: Optional[str] = None) -> Report:
        """Generate executive summary report."""
        beliefs = self._get_beliefs(topic)

        # Calculate key metrics
        total = len(beliefs)
        avg_credence = sum(b.credence.value for b in beliefs) / total if total else 0
        high_confidence = sum(1 for b in beliefs if b.credence.value >= 0.7)
        contested = sum(1 for b in beliefs if b.contested)

        # Count by source depth
        by_depth = {}
        for b in beliefs:
            depth = b.source_depth.value if b.source_depth else "unknown"
            by_depth[depth] = by_depth.get(depth, 0) + 1

        # Top findings (highest credence)
        top_beliefs = sorted(beliefs, key=lambda b: -b.credence.value)[:5]
        top_findings = [
            f"- {b.content} (credence: {b.credence.value:.0%})"
            for b in top_beliefs
        ]

        summary = (
            f"Evidence base contains {total} beliefs "
            f"with average credence of {avg_credence:.0%}. "
            f"{high_confidence} beliefs have high confidence (≥70%). "
            f"{contested} beliefs are contested."
        )

        sections = [
            ReportSection(
                title="Key Metrics",
                content=f"Total beliefs: {total}\n"
                        f"Average credence: {avg_credence:.1%}\n"
                        f"High confidence beliefs: {high_confidence}\n"
                        f"Contested beliefs: {contested}",
                data={
                    'total_beliefs': total,
                    'average_credence': avg_credence,
                    'high_confidence': high_confidence,
                    'contested': contested
                }
            ),
            ReportSection(
                title="Source Quality",
                content="\n".join(f"- {depth}: {count}" for depth, count in by_depth.items()),
                data={'by_depth': by_depth}
            ),
            ReportSection(
                title="Top Findings",
                content="\n".join(top_findings) if top_findings else "No findings yet.",
                data={'top_beliefs': [b.belief_id for b in top_beliefs]}
            )
        ]

        return Report(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            title="Executive Summary" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={'topic': topic, 'belief_count': total}
        )

    def _generate_evidence_inventory(self, topic: Optional[str] = None) -> Report:
        """Generate complete evidence inventory."""
        beliefs = self._get_beliefs(topic)

        # Group by outcome
        by_outcome: Dict[str, List[Belief]] = {}
        for b in beliefs:
            outcome = b.outcome_id or "unclassified"
            if outcome not in by_outcome:
                by_outcome[outcome] = []
            by_outcome[outcome].append(b)

        sections = []
        for outcome, outcome_beliefs in sorted(by_outcome.items()):
            items = []
            for b in sorted(outcome_beliefs, key=lambda x: -x.credence.value):
                depth = b.source_depth.value if b.source_depth else "unknown"
                items.append(
                    f"• [{b.credence.value:.0%}] {b.content}\n"
                    f"  Source: {depth} | Papers: {len(b.paper_ids)}"
                )

            sections.append(ReportSection(
                title=f"{outcome.title()} ({len(outcome_beliefs)} beliefs)",
                content="\n\n".join(items),
                data={
                    'outcome': outcome,
                    'count': len(outcome_beliefs),
                    'belief_ids': [b.belief_id for b in outcome_beliefs]
                }
            ))

        summary = (
            f"Complete inventory of {len(beliefs)} beliefs "
            f"across {len(by_outcome)} outcome categories."
        )

        return Report(
            report_type=ReportType.EVIDENCE_INVENTORY,
            title="Evidence Inventory" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={'topic': topic, 'categories': list(by_outcome.keys())}
        )

    def _generate_confidence_analysis(self, topic: Optional[str] = None) -> Report:
        """Generate confidence analysis report."""
        beliefs = self._get_beliefs(topic)

        if not beliefs:
            return Report(
                report_type=ReportType.CONFIDENCE_ANALYSIS,
                title="Confidence Analysis",
                generated_at=datetime.now().isoformat(),
                summary="No beliefs to analyze.",
                sections=[]
            )

        # Categorize by confidence
        high = [b for b in beliefs if b.credence.value >= 0.7]
        medium = [b for b in beliefs if 0.4 <= b.credence.value < 0.7]
        low = [b for b in beliefs if b.credence.value < 0.4]

        # Uncertainty analysis
        avg_uncertainty = sum(b.credence.uncertainty for b in beliefs) / len(beliefs)
        high_uncertainty = [b for b in beliefs if b.credence.uncertainty >= 0.2]

        sections = [
            ReportSection(
                title="High Confidence (≥70%)",
                content="\n".join(f"• {b.content} ({b.credence.value:.0%})" for b in high[:10]),
                data={'count': len(high), 'beliefs': [b.belief_id for b in high]}
            ),
            ReportSection(
                title="Medium Confidence (40-70%)",
                content="\n".join(f"• {b.content} ({b.credence.value:.0%})" for b in medium[:10]),
                data={'count': len(medium), 'beliefs': [b.belief_id for b in medium]}
            ),
            ReportSection(
                title="Low Confidence (<40%)",
                content="\n".join(f"• {b.content} ({b.credence.value:.0%})" for b in low[:10]),
                data={'count': len(low), 'beliefs': [b.belief_id for b in low]}
            ),
            ReportSection(
                title="Uncertainty Analysis",
                content=f"Average uncertainty: {avg_uncertainty:.1%}\n"
                        f"High uncertainty beliefs: {len(high_uncertainty)}\n\n"
                        "These beliefs may benefit from additional evidence.",
                data={
                    'avg_uncertainty': avg_uncertainty,
                    'high_uncertainty_count': len(high_uncertainty)
                }
            )
        ]

        summary = (
            f"Of {len(beliefs)} beliefs: {len(high)} high confidence, "
            f"{len(medium)} medium, {len(low)} low. "
            f"Average uncertainty: {avg_uncertainty:.1%}."
        )

        return Report(
            report_type=ReportType.CONFIDENCE_ANALYSIS,
            title="Confidence Analysis" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={
                'high_count': len(high),
                'medium_count': len(medium),
                'low_count': len(low)
            }
        )

    def _generate_gap_analysis(self, topic: Optional[str] = None) -> Report:
        """Generate gap analysis report (what we don't know)."""
        beliefs = self._get_beliefs(topic)

        # Identify gaps
        gaps = []

        # 1. Low coverage outcomes (H2: from taxonomy, not hardcoded)
        outcomes = set(b.outcome_id for b in beliefs if b.outcome_id)
        expected_outcomes = self._get_expected_outcomes()  # H2: Dynamic from taxonomy
        missing_outcomes = expected_outcomes - outcomes
        if missing_outcomes:
            gaps.append(ReportSection(
                title="Missing Outcome Categories",
                content="No evidence found for:\n" +
                        "\n".join(f"• {o}" for o in sorted(missing_outcomes)),
                data={
                    'missing': list(missing_outcomes),
                    'source': 'taxonomy' if self._taxonomy else 'fallback'
                }
            ))

        # 2. Abstract-only causal claims (per Cartwright)
        abstract_causal = [
            b for b in beliefs
            if b.source_depth == SourceDepth.ABSTRACT
            and self._is_causal_claim(b)
        ]
        if abstract_causal:
            gaps.append(ReportSection(
                title="Unverified Causal Claims (Abstract-Only)",
                content="These causal claims need full-text verification:\n" +
                        "\n".join(f"• {b.content}" for b in abstract_causal[:10]),
                data={'count': len(abstract_causal), 'beliefs': [b.belief_id for b in abstract_causal]}
            ))

        # 3. High uncertainty beliefs
        high_uncertainty = [b for b in beliefs if b.credence.uncertainty >= 0.25]
        if high_uncertainty:
            gaps.append(ReportSection(
                title="High Uncertainty Beliefs",
                content="These beliefs have high uncertainty and may need more evidence:\n" +
                        "\n".join(f"• {b.content} (±{b.credence.uncertainty:.0%})"
                                  for b in high_uncertainty[:10]),
                data={'count': len(high_uncertainty)}
            ))

        # 4. Single-source beliefs
        single_source = [b for b in beliefs if len(b.paper_ids) <= 1]
        if single_source:
            gaps.append(ReportSection(
                title="Single-Source Beliefs",
                content=f"{len(single_source)} beliefs are supported by only one paper. "
                        "Consider seeking corroborating evidence.",
                data={'count': len(single_source)}
            ))

        # 5. Missing scope conditions
        unscoped = [
            b for b in beliefs
            if self._is_causal_claim(b) and not b.scope
        ]
        if unscoped:
            gaps.append(ReportSection(
                title="Missing Scope Conditions",
                content="Causal claims without specified scope (population/setting):\n" +
                        "\n".join(f"• {b.content}" for b in unscoped[:10]),
                data={'count': len(unscoped)}
            ))

        # 6. H3: Missing confounder coverage with severity weighting (E1.D4 panel)
        # Per Pearl/Cartwright: severity based on source depth
        confounder_gaps = self._find_causal_without_confounders_with_severity(beliefs)

        # CRITICAL: Abstract-only causal claims without confounder mention
        if confounder_gaps['critical']:
            gaps.append(ReportSection(
                title="CRITICAL: Abstract-Only Causal Claims Without Confounder Control",
                content="These abstract-only causal claims lack confounder acknowledgment "
                        "and require immediate full-text verification (Pearl/Cartwright):\n" +
                        "\n".join(f"• {b.content}" for b in confounder_gaps['critical'][:10]),
                data={
                    'count': len(confounder_gaps['critical']),
                    'belief_ids': [b.belief_id for b in confounder_gaps['critical']],
                    'severity': 'CRITICAL'
                }
            ))

        # WARNING: Full-text causal claims without confounder mention
        if confounder_gaps['warning']:
            gaps.append(ReportSection(
                title="WARNING: Causal Claims Without Confounder Control",
                content="These causal claims lack explicit confounder acknowledgment (Pearl):\n" +
                        "\n".join(f"• {b.content}" for b in confounder_gaps['warning'][:10]),
                data={
                    'count': len(confounder_gaps['warning']),
                    'belief_ids': [b.belief_id for b in confounder_gaps['warning']],
                    'severity': 'WARNING'
                }
            ))

        summary = f"Identified {len(gaps)} categories of knowledge gaps."

        return Report(
            report_type=ReportType.GAP_ANALYSIS,
            title="Gap Analysis" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=gaps,
            metadata={'gap_count': len(gaps)}
        )

    def _generate_quality_assessment(self, topic: Optional[str] = None) -> Report:
        """Generate evidence quality assessment."""
        beliefs = self._get_beliefs(topic)

        if not beliefs:
            return Report(
                report_type=ReportType.QUALITY_ASSESSMENT,
                title="Quality Assessment",
                generated_at=datetime.now().isoformat(),
                summary="No beliefs to assess.",
                sections=[]
            )

        # Quality metrics
        full_text = sum(1 for b in beliefs if b.source_depth == SourceDepth.FULL_TEXT)
        abstract_only = sum(1 for b in beliefs if b.source_depth == SourceDepth.ABSTRACT)
        metadata_only = sum(1 for b in beliefs if b.source_depth == SourceDepth.METADATA)

        full_text_pct = full_text / len(beliefs) if beliefs else 0

        # Epistemic level distribution
        by_level: Dict[str, int] = {}
        for b in beliefs:
            level = b.level.value if b.level else "unknown"
            by_level[level] = by_level.get(level, 0) + 1

        # Multi-source support
        multi_source = sum(1 for b in beliefs if len(b.paper_ids) > 1)
        avg_sources = sum(len(b.paper_ids) for b in beliefs) / len(beliefs) if beliefs else 0

        # Quality score (simple weighted calculation)
        quality_score = (
            (full_text_pct * 0.4) +  # Full text is best
            (multi_source / len(beliefs) * 0.3 if beliefs else 0) +  # Multi-source is good
            (sum(b.credence.value for b in beliefs) / len(beliefs) * 0.3 if beliefs else 0)  # High credence
        )

        sections = [
            ReportSection(
                title="Source Depth Quality",
                content=f"Full text: {full_text} ({full_text/len(beliefs):.0%})\n"
                        f"Abstract only: {abstract_only} ({abstract_only/len(beliefs):.0%})\n"
                        f"Metadata only: {metadata_only} ({metadata_only/len(beliefs):.0%})",
                data={
                    'full_text': full_text,
                    'abstract': abstract_only,
                    'metadata': metadata_only
                }
            ),
            ReportSection(
                title="Epistemic Level Distribution",
                content="\n".join(f"• {level}: {count}" for level, count in by_level.items()),
                data=by_level
            ),
            ReportSection(
                title="Source Corroboration",
                content=f"Multi-source beliefs: {multi_source} ({multi_source/len(beliefs):.0%})\n"
                        f"Average sources per belief: {avg_sources:.1f}",
                data={
                    'multi_source': multi_source,
                    'avg_sources': avg_sources
                }
            ),
            ReportSection(
                title="Overall Quality Score",
                content=f"Quality score: {quality_score:.0%}\n\n"
                        "Score based on: source depth (40%), corroboration (30%), credence (30%)",
                data={'quality_score': quality_score}
            )
        ]

        summary = (
            f"Quality assessment of {len(beliefs)} beliefs. "
            f"Overall quality score: {quality_score:.0%}. "
            f"{full_text_pct:.0%} from full text sources."
        )

        return Report(
            report_type=ReportType.QUALITY_ASSESSMENT,
            title="Quality Assessment" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={'quality_score': quality_score}
        )

    def _generate_topic_deep_dive(self, topic: Optional[str] = None) -> Report:
        """Generate deep dive on specific topic."""
        if not topic:
            return Report(
                report_type=ReportType.TOPIC_DEEP_DIVE,
                title="Topic Deep Dive",
                generated_at=datetime.now().isoformat(),
                summary="No topic specified for deep dive.",
                sections=[]
            )

        beliefs = self._get_beliefs(topic)

        if not beliefs:
            return Report(
                report_type=ReportType.TOPIC_DEEP_DIVE,
                title=f"Topic Deep Dive: {topic}",
                generated_at=datetime.now().isoformat(),
                summary=f"No beliefs found for topic: {topic}",
                sections=[]
            )

        # Organize findings
        supporting = [b for b in beliefs if b.credence.value >= 0.5]
        contrary = [b for b in beliefs if b.credence.value < 0.5]
        contested = [b for b in beliefs if b.contested]

        # Extract mechanisms (beliefs with "because", "mechanism", etc.)
        mechanisms = [
            b for b in beliefs
            if any(kw in b.content.lower() for kw in ['because', 'mechanism', 'pathway', 'through'])
        ]

        # Scope conditions
        scoped = [b for b in beliefs if b.scope and b.scope.scope_specified]

        sections = [
            ReportSection(
                title="Summary",
                content=f"Found {len(beliefs)} beliefs about {topic}.\n"
                        f"Supporting: {len(supporting)} | Contrary: {len(contrary)} | Contested: {len(contested)}",
                data={'total': len(beliefs), 'supporting': len(supporting), 'contrary': len(contrary)}
            ),
            ReportSection(
                title="Key Findings",
                content="\n".join(f"• {b.content} ({b.credence.value:.0%})"
                                  for b in sorted(beliefs, key=lambda x: -x.credence.value)[:10]),
                data={'top_beliefs': [b.belief_id for b in beliefs[:10]]}
            ),
        ]

        if mechanisms:
            sections.append(ReportSection(
                title="Mechanisms",
                content="\n".join(f"• {b.content}" for b in mechanisms[:5]),
                data={'count': len(mechanisms)}
            ))

        if scoped:
            conditions = []
            for b in scoped:
                if b.scope.population:
                    conditions.append(f"Population: {b.scope.population}")
                if b.scope.setting:
                    conditions.append(f"Setting: {b.scope.setting}")
            sections.append(ReportSection(
                title="Scope Conditions",
                content="\n".join(f"• {c}" for c in set(conditions)),
                data={'conditions': list(set(conditions))}
            ))

        if contested:
            sections.append(ReportSection(
                title="Contested Areas",
                content="These findings are disputed:\n" +
                        "\n".join(f"• {b.content}" for b in contested),
                data={'contested_count': len(contested)}
            ))

        summary = (
            f"Deep dive on '{topic}': {len(beliefs)} beliefs, "
            f"{len(supporting)} supporting, {len(contested)} contested."
        )

        return Report(
            report_type=ReportType.TOPIC_DEEP_DIVE,
            title=f"Topic Deep Dive: {topic}",
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={'topic': topic}
        )

    def _generate_contradiction_report(self, topic: Optional[str] = None) -> Report:
        """Generate report on contradictions and disputes."""
        beliefs = self._get_beliefs(topic)
        contested = [b for b in beliefs if b.contested]

        # Group contradictions by outcome
        by_outcome: Dict[str, List[Belief]] = {}
        for b in contested:
            outcome = b.outcome_id or "general"
            if outcome not in by_outcome:
                by_outcome[outcome] = []
            by_outcome[outcome].append(b)

        sections = []
        for outcome, outcome_beliefs in by_outcome.items():
            sections.append(ReportSection(
                title=f"Contested: {outcome.title()}",
                content="\n".join(f"• {b.content} ({b.credence.value:.0%})"
                                  for b in outcome_beliefs),
                data={
                    'outcome': outcome,
                    'count': len(outcome_beliefs),
                    'beliefs': [b.belief_id for b in outcome_beliefs]
                }
            ))

        # Add summary of contradiction sources
        if contested:
            sections.append(ReportSection(
                title="Recommendations",
                content="To resolve contradictions, consider:\n"
                        "• Seeking full-text sources for abstract-only claims\n"
                        "• Checking scope conditions (population, setting differences)\n"
                        "• Examining methodological differences across studies\n"
                        "• Looking for mediating or moderating variables",
                data={}
            ))

        summary = (
            f"Found {len(contested)} contested beliefs"
            + (f" about {topic}" if topic else "")
            + f" across {len(by_outcome)} outcome categories."
        )

        return Report(
            report_type=ReportType.CONTRADICTION_REPORT,
            title="Contradiction Report" + (f": {topic}" if topic else ""),
            generated_at=datetime.now().isoformat(),
            summary=summary,
            sections=sections,
            metadata={'total_contested': len(contested)}
        )

    def _get_beliefs(self, topic: Optional[str] = None) -> List[Belief]:
        """Get beliefs, optionally filtered by topic."""
        if topic:
            topic_lower = topic.lower()
            return [
                b for b in self.web.beliefs.values()
                if topic_lower in b.content.lower()
            ]
        return list(self.web.beliefs.values())

    def _is_causal_claim(self, belief: Belief) -> bool:
        """Check if belief is a causal claim."""
        causal_keywords = [
            'cause', 'effect', 'affect', 'impact', 'influence',
            'improve', 'reduce', 'increase', 'decrease', 'lead to'
        ]
        content_lower = belief.content.lower()
        return any(kw in content_lower for kw in causal_keywords)

    def _find_causal_without_confounders(self, beliefs: List[Belief]) -> List[Belief]:
        """
        H3: Find causal claims that don't mention confounders.

        Per Pearl panel recommendation: Causal claims should acknowledge
        potential confounders for validity assessment.

        Returns:
            List of causal beliefs without confounder acknowledgment
        """
        results = []
        for belief in beliefs:
            if self._is_causal_claim(belief):
                content_lower = belief.content.lower()
                has_confounder_mention = any(
                    kw in content_lower for kw in self._get_confounder_keywords()
                )
                if not has_confounder_mention:
                    results.append(belief)

        return results

    def _get_confounder_keywords(self) -> List[str]:
        """
        Get comprehensive confounder keywords per panel review.

        Expanded per Pearl, Cartwright, Kaplan panel recommendations (E1.D4).
        """
        # Standard statistical control terms
        statistical = [
            'confounder', 'confounding', 'controlled for', 'controlling for',
            'adjusted for', 'adjusting for', 'covariate', 'covariates',
            'held constant', 'accounted for', 'independent of',
            'after adjusting', 'after controlling', 'net of',
            'spurious', 'third variable', 'alternative explanation'
        ]

        # Pearl additions: causal identification strategies
        # L1: Panel validation (2026-01-22) - added IPW, doubly robust, g-computation
        causal_identification = [
            'propensity score', 'instrumental variable', 'instrument',
            'difference-in-differences', 'diff-in-diff', 'DiD',
            'regression discontinuity', 'RDD',
            'matching', 'matched sample', 'matched pairs',
            'stratified', 'stratification', 'blocked',
            'within-subjects', 'within-subject', 'repeated measures',
            # L1: Strong causal method indicators per Pearl panel validation
            'inverse probability weighting', 'IPW', 'IPTW',
            'doubly robust', 'doubly-robust',
            'g-computation', 'g computation', 'G-formula',
            'marginal structural model', 'MSM',
            'targeted learning', 'TMLE'
        ]

        # Cartwright additions: domain-specific confounders
        domain_specific = [
            'socioeconomic', 'SES', 'income', 'education level',
            'self-selection', 'selection bias', 'selection effect',
            'building age', 'building type', 'building characteristics',
            'climate', 'latitude', 'seasonal', 'seasonality', 'weather'
        ]

        # Kaplan additions: environmental psychology terms
        environmental_psych = [
            'baseline', 'baseline measurement', 'baseline condition',
            'pre-post', 'pre-test', 'pretest', 'post-test', 'posttest',
            'time of day', 'circadian', 'diurnal'
        ]

        # F1.4: Kaplan domain confounders (ruthless review 2026-01-22)
        kaplan_domain = [
            'occupant density', 'crowding',
            'personal control', 'autonomy',
            'work type', 'knowledge work', 'routine work',
            'habituation', 'prior exposure', 'adaptation',
            'workstation', 'workspace configuration',
            'job demands', 'job control', 'job type'
        ]

        # Panel validation (2026-01-22): M4 additions per Kaplan
        # Demographic confounders
        demographic = [
            'age', 'gender', 'sex', 'education', 'education level',
            'cultural background', 'culture', 'nationality', 'ethnicity'
        ]

        # Individual differences (sensitivity)
        individual_differences = [
            'noise sensitivity', 'thermal sensitivity', 'light sensitivity',
            'personality', 'introvert', 'extravert', 'neuroticism',
            'environmental sensitivity'
        ]

        # Environmental confounders
        environmental_confounders = [
            'window access', 'view content', 'daylight access',
            'air quality', 'ventilation rate', 'temperature'
        ]

        # Organizational confounders
        organizational = [
            'organizational culture', 'management style',
            'team size', 'tenure', 'job satisfaction', 'workload'
        ]

        # F2.3: Pearl implicit confounder control patterns (ruthless review)
        implicit_control = [
            'adjusted model', 'full model', 'final model',
            'multivariate', 'multiple regression', 'multilevel',
            'after including covariates', 'Model 2', 'Model 3',
            'Model II', 'Model III', 'hierarchical model'
        ]

        # Mediator/moderator terms
        mechanism_terms = [
            'mediator', 'mediating', 'mediation',
            'moderator', 'moderating', 'moderation',
            'interaction effect', 'interaction term'
        ]

        return (statistical + causal_identification + domain_specific +
                environmental_psych + kaplan_domain + implicit_control +
                mechanism_terms + demographic + individual_differences +
                environmental_confounders + organizational)

    def _get_confounder_gap_severity(
        self,
        belief: Belief,
        has_confounder_mention: bool
    ) -> str:
        """
        Determine severity of confounder gap per panel recommendation.

        Per Cartwright (E1.D4):
        - CRITICAL: Abstract-only causal claim, no confounder mention
        - WARNING: Full-text causal claim, no confounder mention
        - INFO: Associational claim or has confounder mention

        Returns:
            Severity level as string
        """
        if has_confounder_mention:
            return "INFO"

        is_causal = self._is_causal_claim(belief)
        is_abstract_only = belief.source_depth == SourceDepth.ABSTRACT

        if is_causal and is_abstract_only:
            return "CRITICAL"
        elif is_causal:
            return "WARNING"
        else:
            return "INFO"

    def _find_causal_without_confounders_with_severity(
        self,
        beliefs: List[Belief]
    ) -> Dict[str, List[Belief]]:
        """
        Find causal claims without confounders, grouped by severity.

        Per panel (E1.D4): Severity weighting based on source depth.

        Returns:
            Dict with 'critical', 'warning' keys containing belief lists
        """
        confounder_keywords = self._get_confounder_keywords()
        results = {'critical': [], 'warning': []}

        for belief in beliefs:
            if self._is_causal_claim(belief):
                content_lower = belief.content.lower()
                has_confounder_mention = any(
                    kw in content_lower for kw in confounder_keywords
                )

                if not has_confounder_mention:
                    severity = self._get_confounder_gap_severity(
                        belief, has_confounder_mention
                    )
                    if severity == "CRITICAL":
                        results['critical'].append(belief)
                    elif severity == "WARNING":
                        results['warning'].append(belief)

        return results


# =============================================================================
# Convenience Functions
# =============================================================================

def generate_report(
    web: WebOfBelief,
    report_type: ReportType = ReportType.EXECUTIVE_SUMMARY,
    topic: Optional[str] = None
) -> Report:
    """
    Convenience function to generate a report.

    Args:
        web: The web of belief
        report_type: Type of report to generate
        topic: Optional topic to focus on

    Returns:
        Generated Report
    """
    generator = ReportGenerator(web)
    return generator.generate(report_type, topic)
