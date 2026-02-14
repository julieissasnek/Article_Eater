"""
Synthesis Paper Ingester (Sprint 6c / Task 6c.3).

Ingests meta-analyses, systematic reviews, and narrative reviews
into the web of belief.

Per spec §5.2-5.4:
"Meta-analyses produce SYNTHESIS_CONCLUSIONs with pooled effects.
Systematic reviews produce SYNTHESIS_CONCLUSIONs per synthesized theme.
Narrative reviews produce EXPERT_SYNTHESIS nodes."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5.2, §5.3, §5.4
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

from src.epistemic.node_types import NodeType
from src.epistemic.edge_types import EdgeType
from src.epistemic.contracts.claim_v2 import ClaimV2
from src.epistemic.contracts.edge_v2 import EdgeV2
from src.epistemic.entrenchment.synthesis_rules import (
    compute_synthesis_entrenchment,
    compute_median_entrenchment,
)
from src.epistemic.entrenchment.expert_discount import (
    compute_expert_synthesis_entrenchment,
    EXPERT_SYNTHESIS_DISCOUNT,
)


class SynthesisType(str, Enum):
    """Type of synthesis paper."""
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    NARRATIVE_REVIEW = "narrative_review"


class EvidenceDirection(str, Enum):
    """Direction of evidence in a synthesis."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    INSUFFICIENT = "insufficient"
    NULL = "null"


# =============================================================================
# EXTRACTED DATA STRUCTURES
# =============================================================================

@dataclass
class PooledEffect:
    """A pooled effect from a meta-analysis."""
    effect_id: str
    effect_description: str
    effect_size: float
    effect_size_metric: str  # "d", "g", "r", "OR", etc.
    confidence_interval: tuple  # (lower, upper)
    n_studies: int
    n_participants: Optional[int] = None
    heterogeneity_i2: float = 0.0
    heterogeneity_q_pvalue: Optional[float] = None
    publication_bias: str = "none"  # "none" | "marginal" | "significant"
    grade_quality: str = "moderate"  # "high" | "moderate" | "low"


@dataclass
class ModeratorAnalysis:
    """A moderator analysis from a meta-analysis."""
    moderator_variable: str
    effect_by_level: Dict[str, float]  # level → effect size
    q_between: Optional[float] = None
    p_value: Optional[float] = None
    significant: bool = False


@dataclass
class SynthesisConclusion:
    """
    A synthesis conclusion extracted from a review.

    Per spec: "SYNTHESIS_CONCLUSIONs are aggregated findings across
    multiple studies. Higher-order evidence."
    """
    conclusion_id: str
    conclusion_text: str
    evidence_direction: EvidenceDirection
    n_included_studies: int
    included_study_ids: List[str] = field(default_factory=list)
    pooled_effect: Optional[PooledEffect] = None  # For meta-analyses
    quality_profile: Optional[str] = None
    scope_conditions: List[str] = field(default_factory=list)
    source_paper_id: str = ""

    def compute_entrenchment(
        self,
        included_study_entrenchments: Optional[List[float]] = None
    ) -> float:
        """Compute entrenchment for this synthesis conclusion."""
        return compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=included_study_entrenchments or [],
            heterogeneity_i2=self.pooled_effect.heterogeneity_i2 if self.pooled_effect else 0.0,
            publication_bias=self.pooled_effect.publication_bias if self.pooled_effect else "none",
            grade_quality=self.pooled_effect.grade_quality if self.pooled_effect else "moderate",
        )

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.conclusion_id,
            node_type=NodeType.SYNTHESIS_CONCLUSION.value,
            paper_id=self.source_paper_id,
            statement=self.conclusion_text,
            ae_confidence=self.compute_entrenchment(),
            provenance_tier="pdf_confirmed",
            evidence_level="synthesis",
            effect_size=self.pooled_effect.effect_size if self.pooled_effect else None,
            effect_size_type=self.pooled_effect.effect_size_metric if self.pooled_effect else None,
            confidence_interval=list(self.pooled_effect.confidence_interval) if self.pooled_effect else [],
            scope_conditions=self.scope_conditions,
            article_type_family="meta_analysis" if self.pooled_effect else "systematic_review",
        )


@dataclass
class ExpertSynthesis:
    """
    An expert synthesis from a narrative review.

    Per spec: "EXPERT_SYNTHESIS nodes carry expert interpretation
    of evidence. Lower confidence than SYNTHESIS_CONCLUSION because
    selection is non-systematic."
    """
    synthesis_id: str
    synthesis_text: str
    author_expertise: str = "unknown"  # "established" | "emerging" | "unknown"
    consistent_with_systematic: bool = False
    n_studies_cited: int = 0
    declared_perspective: Optional[str] = None
    attributed_findings: List[str] = field(default_factory=list)  # Study IDs
    source_paper_id: str = ""

    def compute_entrenchment(self) -> float:
        """Compute entrenchment for this expert synthesis."""
        return compute_expert_synthesis_entrenchment(
            author_expertise=self.author_expertise,
            consistent_with_systematic=self.consistent_with_systematic,
            n_studies_cited=self.n_studies_cited,
            theoretical_commitment_declared=self.declared_perspective is not None,
        )

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.synthesis_id,
            node_type=NodeType.EXPERT_SYNTHESIS.value,
            paper_id=self.source_paper_id,
            statement=self.synthesis_text,
            ae_confidence=self.compute_entrenchment(),
            provenance_tier="pdf_confirmed",
            evidence_level="expert_synthesis",
            author_expertise=self.author_expertise,
            evidence_basis="cited_evidence" if self.n_studies_cited > 0 else "expert_opinion",
            n_studies_cited=self.n_studies_cited,
            declared_bias=self.declared_perspective,
            article_type_family="narrative_review",
        )


@dataclass
class KnowledgeGap:
    """
    A knowledge gap identified in a review.

    Per spec: "KNOWLEDGE_GAP nodes mark missing knowledge.
    High VOI signal for future search/research."
    """
    gap_id: str
    gap_description: str
    voi_relevance: str = "medium"  # "high" | "medium" | "low"
    suggested_research: Optional[str] = None
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.gap_id,
            node_type=NodeType.KNOWLEDGE_GAP.value,
            paper_id=self.source_paper_id,
            statement=self.gap_description,
            ae_confidence=0.0,  # Gaps don't have confidence
            provenance_tier="pdf_confirmed",
            evidence_level="gap",
            article_type_family="systematic_review",
        )


@dataclass
class MethodologicalCritique:
    """
    A methodological critique from a review.

    Per spec: "METHODOLOGICAL_CRITIQUE nodes argue that a method,
    paradigm, or finding is flawed. Propagates validity penalties."
    """
    critique_id: str
    critique_content: str
    target_method: Optional[str] = None
    target_paradigm: Optional[str] = None
    severity: float = 0.5  # [0, 1]
    proposed_alternative: Optional[str] = None
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.critique_id,
            node_type=NodeType.METHODOLOGICAL_CRITIQUE.value,
            paper_id=self.source_paper_id,
            statement=self.critique_content,
            ae_confidence=0.55,  # Midpoint for critiques
            provenance_tier="pdf_confirmed",
            evidence_level="critique",
            article_type_family="systematic_review",
        )


# =============================================================================
# EXTRACTION RESULT
# =============================================================================

@dataclass
class SynthesisExtractionResult:
    """
    Complete extraction result from a synthesis paper.
    """
    source_paper_id: str
    source_paper_title: str
    synthesis_type: SynthesisType
    conclusions: List[SynthesisConclusion] = field(default_factory=list)
    expert_syntheses: List[ExpertSynthesis] = field(default_factory=list)
    knowledge_gaps: List[KnowledgeGap] = field(default_factory=list)
    critiques: List[MethodologicalCritique] = field(default_factory=list)
    moderator_analyses: List[ModeratorAnalysis] = field(default_factory=list)
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    extraction_confidence: float = 0.5

    @property
    def total_nodes(self) -> int:
        """Total number of extracted nodes."""
        return (
            len(self.conclusions) +
            len(self.expert_syntheses) +
            len(self.knowledge_gaps) +
            len(self.critiques)
        )

    def to_claims(self) -> List[ClaimV2]:
        """Convert all extracted items to ClaimV2 objects."""
        claims = []
        for conc in self.conclusions:
            claims.append(conc.to_claim_v2())
        for exp in self.expert_syntheses:
            claims.append(exp.to_claim_v2())
        for gap in self.knowledge_gaps:
            claims.append(gap.to_claim_v2())
        for crit in self.critiques:
            claims.append(crit.to_claim_v2())
        return claims

    def to_edges(self) -> List[EdgeV2]:
        """Generate edges for the extraction."""
        edges = []

        # INCLUDES_IN_SYNTHESIS edges
        for conc in self.conclusions:
            for study_id in conc.included_study_ids:
                edges.append(EdgeV2(
                    edge_id=f"includes_{conc.conclusion_id}_{study_id}",
                    edge_type=EdgeType.INCLUDES_IN_SYNTHESIS.value,
                    source_node_id=conc.conclusion_id,
                    target_node_id=study_id,
                    weight=0.8,
                    paper_id=self.source_paper_id,
                ))

        # IDENTIFIES_MODERATOR edges
        for mod in self.moderator_analyses:
            for conc in self.conclusions:
                edges.append(EdgeV2(
                    edge_id=f"moderator_{conc.conclusion_id}_{mod.moderator_variable}",
                    edge_type=EdgeType.IDENTIFIES_MODERATOR.value,
                    source_node_id=conc.conclusion_id,
                    target_node_id=f"moderator:{mod.moderator_variable}",
                    weight=0.7 if mod.significant else 0.4,
                    paper_id=self.source_paper_id,
                    justification=f"Moderator: {mod.moderator_variable}, significant={mod.significant}",
                ))

        # ATTRIBUTES_FINDING edges for expert syntheses
        for exp in self.expert_syntheses:
            for study_id in exp.attributed_findings:
                edges.append(EdgeV2(
                    edge_id=f"attributes_{exp.synthesis_id}_{study_id}",
                    edge_type=EdgeType.ATTRIBUTES_FINDING.value,
                    source_node_id=exp.synthesis_id,
                    target_node_id=study_id,
                    weight=0.6,
                    paper_id=self.source_paper_id,
                    needs_verification=True,
                ))

        # CRITIQUES_METHOD edges
        for crit in self.critiques:
            if crit.target_method:
                edges.append(EdgeV2(
                    edge_id=f"critiques_{crit.critique_id}",
                    edge_type=EdgeType.CRITIQUES_METHOD.value,
                    source_node_id=crit.critique_id,
                    target_node_id=f"method:{crit.target_method}",
                    weight=crit.severity,
                    paper_id=self.source_paper_id,
                    justification=f"Severity: {crit.severity}, alternative: {crit.proposed_alternative}",
                ))

        return edges

    def summary(self) -> Dict[str, Any]:
        """Get a summary of the extraction result."""
        return {
            "source_paper_id": self.source_paper_id,
            "source_paper_title": self.source_paper_title,
            "synthesis_type": self.synthesis_type.value,
            "n_conclusions": len(self.conclusions),
            "n_expert_syntheses": len(self.expert_syntheses),
            "n_knowledge_gaps": len(self.knowledge_gaps),
            "n_critiques": len(self.critiques),
            "n_moderators": len(self.moderator_analyses),
            "total_nodes": self.total_nodes,
            "extraction_confidence": self.extraction_confidence,
        }


# =============================================================================
# INGESTERS
# =============================================================================

class SynthesisIngester:
    """
    Ingests synthesis papers into the web of belief.
    """

    def ingest_meta_analysis(
        self,
        paper_id: str,
        paper_title: str,
        template_output: Dict[str, Any]
    ) -> SynthesisExtractionResult:
        """
        Ingest a meta-analysis paper.

        Args:
            paper_id: Unique paper identifier
            paper_title: Paper title
            template_output: Output from meta_analysis template extraction

        Returns:
            SynthesisExtractionResult
        """
        result = SynthesisExtractionResult(
            source_paper_id=paper_id,
            source_paper_title=paper_title,
            synthesis_type=SynthesisType.META_ANALYSIS,
        )

        # Extract overall effect as SYNTHESIS_CONCLUSION
        if "overall_effect" in template_output:
            oe = template_output["overall_effect"]
            pooled = PooledEffect(
                effect_id=f"{paper_id}_effect_overall",
                effect_description=oe.get("description", "Pooled effect"),
                effect_size=oe.get("effect_size", 0.0),
                effect_size_metric=oe.get("metric", "d"),
                confidence_interval=tuple(oe.get("CI", [0, 0])),
                n_studies=oe.get("N_studies", 0),
                n_participants=oe.get("N_participants"),
                heterogeneity_i2=oe.get("heterogeneity_I2", 0.0),
                publication_bias=oe.get("publication_bias", "none"),
                grade_quality=oe.get("grade_quality", "moderate"),
            )

            result.conclusions.append(SynthesisConclusion(
                conclusion_id=f"{paper_id}_conclusion_overall",
                conclusion_text=oe.get("conclusion", f"Pooled effect: {pooled.effect_size}"),
                evidence_direction=self._classify_direction(pooled.effect_size),
                n_included_studies=pooled.n_studies,
                included_study_ids=template_output.get("included_studies", []),
                pooled_effect=pooled,
                source_paper_id=paper_id,
            ))

        # Extract moderator analyses
        for i, mod in enumerate(template_output.get("moderator_analyses", [])):
            result.moderator_analyses.append(ModeratorAnalysis(
                moderator_variable=mod.get("moderator", f"moderator_{i}"),
                effect_by_level=mod.get("effect_per_level", {}),
                q_between=mod.get("Q_between"),
                p_value=mod.get("p_value"),
                significant=mod.get("significant", False),
            ))

        # Extract knowledge gaps
        for i, gap in enumerate(template_output.get("gaps", [])):
            gap_text = gap.get("gap", gap) if isinstance(gap, dict) else str(gap)
            result.knowledge_gaps.append(KnowledgeGap(
                gap_id=f"{paper_id}_gap_{i}",
                gap_description=gap_text,
                voi_relevance=gap.get("voi_relevance", "medium") if isinstance(gap, dict) else "medium",
                source_paper_id=paper_id,
            ))

        result.extraction_confidence = 0.8 if result.conclusions else 0.4
        return result

    def ingest_systematic_review(
        self,
        paper_id: str,
        paper_title: str,
        template_output: Dict[str, Any]
    ) -> SynthesisExtractionResult:
        """
        Ingest a systematic review paper.

        Args:
            paper_id: Unique paper identifier
            paper_title: Paper title
            template_output: Output from systematic_review template extraction

        Returns:
            SynthesisExtractionResult
        """
        result = SynthesisExtractionResult(
            source_paper_id=paper_id,
            source_paper_title=paper_title,
            synthesis_type=SynthesisType.SYSTEMATIC_REVIEW,
        )

        # Extract themes as SYNTHESIS_CONCLUSIONs
        for i, theme in enumerate(template_output.get("themes", [])):
            direction_str = theme.get("evidence_direction", "mixed")
            try:
                direction = EvidenceDirection(direction_str)
            except ValueError:
                direction = EvidenceDirection.MIXED

            result.conclusions.append(SynthesisConclusion(
                conclusion_id=f"{paper_id}_theme_{i}",
                conclusion_text=theme.get("synthesis", theme.get("name", f"Theme {i}")),
                evidence_direction=direction,
                n_included_studies=theme.get("n_studies", 0),
                included_study_ids=theme.get("study_ids", []),
                quality_profile=theme.get("quality_summary"),
                source_paper_id=paper_id,
            ))

        # Extract knowledge gaps
        for i, gap in enumerate(template_output.get("gaps", [])):
            gap_text = gap.get("gap", gap) if isinstance(gap, dict) else str(gap)
            result.knowledge_gaps.append(KnowledgeGap(
                gap_id=f"{paper_id}_gap_{i}",
                gap_description=gap_text,
                source_paper_id=paper_id,
            ))

        # Extract methodological critiques
        for i, issue in enumerate(template_output.get("quality_issues", [])):
            issue_text = issue.get("problem", issue) if isinstance(issue, dict) else str(issue)
            result.critiques.append(MethodologicalCritique(
                critique_id=f"{paper_id}_critique_{i}",
                critique_content=issue_text,
                target_method=issue.get("method") if isinstance(issue, dict) else None,
                severity=issue.get("severity", 0.5) if isinstance(issue, dict) else 0.5,
                source_paper_id=paper_id,
            ))

        result.extraction_confidence = 0.7 if result.conclusions else 0.4
        return result

    def ingest_narrative_review(
        self,
        paper_id: str,
        paper_title: str,
        template_output: Dict[str, Any]
    ) -> SynthesisExtractionResult:
        """
        Ingest a narrative review paper.

        Args:
            paper_id: Unique paper identifier
            paper_title: Paper title
            template_output: Output from narrative_review template extraction

        Returns:
            SynthesisExtractionResult
        """
        result = SynthesisExtractionResult(
            source_paper_id=paper_id,
            source_paper_title=paper_title,
            synthesis_type=SynthesisType.NARRATIVE_REVIEW,
        )

        # Get author info
        author_info = template_output.get("author", {})
        author_expertise = author_info.get("expertise_domain", "unknown")
        declared_perspective = author_info.get("stated_perspective")

        # Map expertise to standard values
        if author_expertise in ["established", "recognized", "prominent"]:
            author_expertise = "established"
        elif author_expertise in ["emerging", "junior"]:
            author_expertise = "emerging"
        else:
            author_expertise = "unknown"

        # Extract themes as EXPERT_SYNTHESIS nodes
        for i, theme in enumerate(template_output.get("themes", [])):
            synthesis_text = theme.get("author_synthesis", theme.get("summary", ""))
            key_studies = theme.get("key_studies", [])
            study_ids = [s.get("citation", s) if isinstance(s, dict) else str(s)
                        for s in key_studies]

            result.expert_syntheses.append(ExpertSynthesis(
                synthesis_id=f"{paper_id}_synthesis_{i}",
                synthesis_text=synthesis_text,
                author_expertise=author_expertise,
                n_studies_cited=len(study_ids),
                declared_perspective=declared_perspective,
                attributed_findings=study_ids,
                source_paper_id=paper_id,
            ))

        # Extract conclusions as additional EXPERT_SYNTHESIS nodes
        conclusions = template_output.get("conclusions", {})
        for i, stmt in enumerate(conclusions.get("summary_statements", [])):
            result.expert_syntheses.append(ExpertSynthesis(
                synthesis_id=f"{paper_id}_conclusion_{i}",
                synthesis_text=stmt if isinstance(stmt, str) else stmt.get("statement", ""),
                author_expertise=author_expertise,
                declared_perspective=declared_perspective,
                source_paper_id=paper_id,
            ))

        # Extract knowledge gaps
        for i, gap in enumerate(conclusions.get("gaps", [])):
            gap_text = gap.get("gap", gap) if isinstance(gap, dict) else str(gap)
            result.knowledge_gaps.append(KnowledgeGap(
                gap_id=f"{paper_id}_gap_{i}",
                gap_description=gap_text,
                source_paper_id=paper_id,
            ))

        result.extraction_confidence = 0.6 if result.expert_syntheses else 0.3
        return result

    def _classify_direction(self, effect_size: float) -> EvidenceDirection:
        """Classify effect direction from effect size."""
        if effect_size > 0.2:
            return EvidenceDirection.POSITIVE
        elif effect_size < -0.2:
            return EvidenceDirection.NEGATIVE
        else:
            return EvidenceDirection.NULL


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ingest_synthesis_paper(
    paper_id: str,
    paper_title: str,
    synthesis_type: SynthesisType,
    template_output: Dict[str, Any]
) -> SynthesisExtractionResult:
    """
    Ingest a synthesis paper based on its type.

    Args:
        paper_id: Unique paper identifier
        paper_title: Paper title
        synthesis_type: Type of synthesis (meta, systematic, narrative)
        template_output: Template extraction output

    Returns:
        SynthesisExtractionResult
    """
    ingester = SynthesisIngester()

    if synthesis_type == SynthesisType.META_ANALYSIS:
        return ingester.ingest_meta_analysis(paper_id, paper_title, template_output)
    elif synthesis_type == SynthesisType.SYSTEMATIC_REVIEW:
        return ingester.ingest_systematic_review(paper_id, paper_title, template_output)
    elif synthesis_type == SynthesisType.NARRATIVE_REVIEW:
        return ingester.ingest_narrative_review(paper_id, paper_title, template_output)
    else:
        raise ValueError(f"Unknown synthesis type: {synthesis_type}")


def compute_synthesis_vs_primary_weight(
    synthesis_n_studies: int,
    synthesis_heterogeneity: float,
    primary_study_quality: float,
) -> float:
    """
    Compute relative weight of synthesis vs. conflicting primary study.

    Per spec: Syntheses with many studies and low heterogeneity should
    generally be trusted over individual studies.

    Args:
        synthesis_n_studies: Number of studies in synthesis
        synthesis_heterogeneity: I² statistic
        primary_study_quality: Quality score of the primary study

    Returns:
        Weight ratio (>1 means trust synthesis, <1 means trust primary)
    """
    # Base weight from number of studies (sqrt for diminishing returns)
    n_weight = min(3.0, (synthesis_n_studies / 5) ** 0.5)

    # Heterogeneity penalty
    if synthesis_heterogeneity > 75:
        het_factor = 0.5
    elif synthesis_heterogeneity > 50:
        het_factor = 0.75
    else:
        het_factor = 1.0

    synthesis_weight = n_weight * het_factor

    # If primary study is very high quality, reduce synthesis advantage
    if primary_study_quality > 0.8:
        synthesis_weight *= 0.8

    return synthesis_weight
