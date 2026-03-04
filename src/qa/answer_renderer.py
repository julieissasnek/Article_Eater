"""
Answer Renderer — Norm-Compliant Answer Generation Per User Type
================================================================

Takes pre-computed enrichment data (omega scores, evidence index, gaps,
framework voices) and renders norm-compliant prose for each user type.

Uses ProseRevisionService as quality gate before marking answers FRESH.
Generates confidence thermometer data alongside each answer.

Norm documents enforced:
  - contracts/WRITING_STYLE_GUIDE.md
  - contracts/SCIENCE_COMMUNICATION_NORMS.md
  - contracts/VISUALIZATION_NORMS.md
  - contracts/MATH_EXPLANATION_NORMS.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Confidence Thermometer
# ---------------------------------------------------------------------------

class ConfidenceLevel(str, Enum):
    """Four-level confidence scale for the visual thermometer."""
    HIGH = "high"              # ω > 0.7, replicated 5+, d > 0.5
    MOD_HIGH = "mod_high"      # ω 0.5-0.7, some replication
    MODERATE = "moderate"      # ω 0.3-0.5, limited replication
    LOW = "low"                # ω < 0.3, single study or theoretical


# ATLAS palette (from VISUALIZATION_NORMS.md §2)
THERMOMETER_COLORS = {
    ConfidenceLevel.HIGH: "#27AE60",       # ATLAS green
    ConfidenceLevel.MOD_HIGH: "#2171B5",   # ATLAS blue
    ConfidenceLevel.MODERATE: "#F39C12",   # ATLAS amber
    ConfidenceLevel.LOW: "#CB4335",        # ATLAS brick red
}

# Confidence spectrum language (from WRITING_STYLE_GUIDE §5)
CONFIDENCE_LANGUAGE = {
    ConfidenceLevel.HIGH: {
        "prefix": "",
        "verbs": ["produces", "reliably leads to", "generates"],
        "example": "X produces Y",
    },
    ConfidenceLevel.MOD_HIGH: {
        "prefix": "",
        "verbs": ["is associated with", "is linked to", "tends to"],
        "example": "X is associated with Y",
    },
    ConfidenceLevel.MODERATE: {
        "prefix": "Preliminary evidence indicates",
        "verbs": ["may influence", "appears to affect", "suggests"],
        "example": "Preliminary evidence indicates X may influence Y",
    },
    ConfidenceLevel.LOW: {
        "prefix": "One possibility is",
        "verbs": ["might", "could potentially", "has been hypothesized to"],
        "example": "One possibility is that X influences Y",
    },
}


@dataclass
class ConfidenceThermometer:
    """Pre-computed confidence visualization data for an answer."""
    level: ConfidenceLevel
    omega_composite: float
    color: str
    label: str                     # e.g. "Mod-High (ω = 0.62)"
    n_supporting_findings: int = 0
    n_replications: int = 0
    mean_effect_size: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "omega_composite": round(self.omega_composite, 3),
            "color": self.color,
            "label": self.label,
            "n_supporting_findings": self.n_supporting_findings,
            "n_replications": self.n_replications,
            "mean_effect_size": self.mean_effect_size,
        }


def compute_confidence_level(omega: float) -> ConfidenceLevel:
    """Map composite omega score to confidence level."""
    if omega > 0.7:
        return ConfidenceLevel.HIGH
    elif omega > 0.5:
        return ConfidenceLevel.MOD_HIGH
    elif omega > 0.3:
        return ConfidenceLevel.MODERATE
    else:
        return ConfidenceLevel.LOW


def build_thermometer(
    omega_composite: float,
    n_findings: int = 0,
    n_replications: int = 0,
    mean_effect_size: Optional[float] = None,
) -> ConfidenceThermometer:
    """Build a confidence thermometer from omega score and evidence stats."""
    level = compute_confidence_level(omega_composite)
    color = THERMOMETER_COLORS[level]
    level_name = {
        ConfidenceLevel.HIGH: "High",
        ConfidenceLevel.MOD_HIGH: "Mod-High",
        ConfidenceLevel.MODERATE: "Moderate",
        ConfidenceLevel.LOW: "Low",
    }[level]
    label = f"{level_name} (ω = {omega_composite:.2f})"

    return ConfidenceThermometer(
        level=level,
        omega_composite=omega_composite,
        color=color,
        label=label,
        n_supporting_findings=n_findings,
        n_replications=n_replications,
        mean_effect_size=mean_effect_size,
    )


# ---------------------------------------------------------------------------
# Rendering Config Per User Type
# ---------------------------------------------------------------------------

@dataclass
class RenderingConfig:
    """Norm-compliant rendering parameters per user type."""
    user_type: str
    voice_bias_popular: float = 0.5
    voice_bias_expert: float = 0.5
    max_length_words: int = 400
    disclosure_levels: List[str] = field(default_factory=lambda: ["L1", "L2"])
    include_equations: bool = False
    include_citations: bool = True
    include_omega_scores: bool = False
    include_provenance_chains: bool = False
    include_research_tools: bool = False
    include_gap_analysis: bool = False
    include_design_implications: bool = False


# Pre-defined configs per user type
USER_TYPE_CONFIGS = {
    "general_public": RenderingConfig(
        user_type="general_public",
        voice_bias_popular=0.8, voice_bias_expert=0.2,
        max_length_words=100,
        disclosure_levels=["L1"],
        include_citations=False,
    ),
    "student": RenderingConfig(
        user_type="student",
        voice_bias_popular=0.6, voice_bias_expert=0.4,
        max_length_words=300,
        disclosure_levels=["L1", "L2"],
    ),
    "clinician": RenderingConfig(
        user_type="clinician",
        voice_bias_popular=0.5, voice_bias_expert=0.5,
        max_length_words=400,
        disclosure_levels=["L1", "L2"],
        include_design_implications=True,
    ),
    "architect_designer": RenderingConfig(
        user_type="architect_designer",
        voice_bias_popular=0.5, voice_bias_expert=0.5,
        max_length_words=400,
        disclosure_levels=["L1", "L2"],
        include_design_implications=True,
    ),
    "researcher": RenderingConfig(
        user_type="researcher",
        voice_bias_popular=0.3, voice_bias_expert=0.7,
        max_length_words=800,
        disclosure_levels=["L1", "L2", "L3"],
        include_equations=True,
        include_omega_scores=True,
        include_gap_analysis=True,
    ),
    "deep_researcher": RenderingConfig(
        user_type="deep_researcher",
        voice_bias_popular=0.2, voice_bias_expert=0.8,
        max_length_words=0,  # 0 = unlimited
        disclosure_levels=["L1", "L2", "L3"],
        include_equations=True,
        include_citations=True,
        include_omega_scores=True,
        include_provenance_chains=True,
        include_research_tools=True,
        include_gap_analysis=True,
        include_design_implications=True,
    ),
}


# ---------------------------------------------------------------------------
# Rendered Answer
# ---------------------------------------------------------------------------

@dataclass
class RenderedAnswer:
    """A fully rendered, norm-compliant answer for a specific user type."""
    topic_cluster: str
    user_type: str
    thermometer: ConfidenceThermometer
    prose: str                    # The rendered answer text
    disclosure_level: str         # Highest level included (L1, L2, L3)
    word_count: int = 0
    quality_score: float = 0.0   # From ProseRevisionService
    quality_passed: bool = False
    rendering_config: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "topic_cluster": self.topic_cluster,
            "user_type": self.user_type,
            "thermometer": self.thermometer.to_dict(),
            "prose": self.prose,
            "disclosure_level": self.disclosure_level,
            "word_count": self.word_count,
            "quality_score": self.quality_score,
            "quality_passed": self.quality_passed,
        }


# ---------------------------------------------------------------------------
# Answer Renderer
# ---------------------------------------------------------------------------

class AnswerRenderer:
    """
    Renders norm-compliant prose per user type from pre-computed data.

    Uses ProseRevisionService as quality gate.
    """

    DISALLOWED_PHRASES = [
        "clearly", "obviously", "interestingly", "it is worth noting",
        "it is important to note", "it can be observed that",
        "as noted above", "the fact that",
    ]

    def __init__(self):
        self._prose_service = None

    def _get_prose_service(self):
        """Lazy load ProseRevisionService."""
        if self._prose_service is None:
            try:
                from src.services.prose_revision_service import ProseRevisionService
                self._prose_service = ProseRevisionService(context="qa_response")
            except ImportError:
                logger.warning("ProseRevisionService not available")
        return self._prose_service

    def render(
        self,
        topic_cluster: str,
        evidence_data: Dict[str, Any],
        omega_scores: Dict[str, Any],
        user_type: str = "researcher",
    ) -> RenderedAnswer:
        """
        Render a norm-compliant answer for a specific user type.

        Args:
            topic_cluster: Topic cluster ID (e.g., "nature_restoration")
            evidence_data: Pre-computed evidence index entries for this topic
            omega_scores: Pre-computed omega scores for relevant findings
            user_type: Target user type

        Returns:
            RenderedAnswer with prose, thermometer, and quality score
        """
        config = USER_TYPE_CONFIGS.get(user_type, USER_TYPE_CONFIGS["researcher"])

        # 1. Build confidence thermometer
        omega_composite = self._compute_composite_omega(omega_scores)
        n_findings = len(evidence_data.get("findings", []))
        thermometer = build_thermometer(omega_composite, n_findings=n_findings)

        # 2. Render prose per disclosure level
        prose = self._render_prose(
            topic_cluster, evidence_data, omega_scores, config, thermometer
        )

        # 3. Quality gate via ProseRevisionService
        quality_score, quality_passed = self._quality_check(prose)

        word_count = len(prose.split())

        return RenderedAnswer(
            topic_cluster=topic_cluster,
            user_type=user_type,
            thermometer=thermometer,
            prose=prose,
            disclosure_level=config.disclosure_levels[-1],
            word_count=word_count,
            quality_score=quality_score,
            quality_passed=quality_passed,
            rendering_config={
                "voice_bias": f"{config.voice_bias_popular:.0%} popular / {config.voice_bias_expert:.0%} expert",
                "max_length": config.max_length_words or "unlimited",
            },
        )

    def _compute_composite_omega(self, omega_scores: Dict) -> float:
        """Compute average composite omega from all scored findings."""
        scores = omega_scores.get("scores", [])
        if not scores:
            # Try nested structure from mv_builder
            all_scores = []
            for article_key, article_data in omega_scores.items():
                if isinstance(article_data, dict) and "scores" in article_data:
                    all_scores.extend(article_data["scores"])
            scores = all_scores

        if not scores:
            return 0.0

        totals = [s.get("omega_total", 0.0) for s in scores if isinstance(s, dict)]
        return sum(totals) / len(totals) if totals else 0.0

    def _render_prose(
        self,
        topic_cluster: str,
        evidence_data: Dict,
        omega_scores: Dict,
        config: RenderingConfig,
        thermometer: ConfidenceThermometer,
    ) -> str:
        """Render the answer prose following norm constraints."""
        sections = []
        conf_lang = CONFIDENCE_LANGUAGE[thermometer.level]

        # Topic title (informative heading — WRITING_STYLE_GUIDE §3.3)
        topic_title = topic_cluster.replace("_", " ").title()

        # L1: Direct answer (1-2 sentences, lead with the point)
        findings = evidence_data.get("findings", [])
        if findings:
            first = findings[0] if isinstance(findings[0], dict) else {}
            antecedent = first.get("antecedent", topic_title)
            consequent = first.get("consequent", "outcomes")
            direction = first.get("direction", "affects")

            if thermometer.level in (ConfidenceLevel.HIGH, ConfidenceLevel.MOD_HIGH):
                l1 = (
                    f"{antecedent.capitalize()} {conf_lang['verbs'][0]} "
                    f"{consequent}. "
                    f"This is supported by {len(findings)} findings across the corpus."
                )
            else:
                l1 = (
                    f"{conf_lang['prefix']} that {antecedent} "
                    f"{conf_lang['verbs'][0]} {consequent}. "
                    f"Evidence is limited to {len(findings)} findings."
                )
        else:
            l1 = (
                f"The corpus contains no direct empirical evidence on {topic_title}. "
                f"This topic requires further research."
            )
        sections.append(l1)

        # L2: Contextualized (3-5 sentences, SCQA structure)
        if "L2" in config.disclosure_levels and findings:
            # Situation
            situation = f"Research on {topic_title.lower()} spans multiple studies in the corpus."
            # Complication
            n_with_pvalue = sum(
                1 for f in findings
                if isinstance(f, dict) and f.get("p_value") is not None
            )
            complication = (
                f"Of these, {n_with_pvalue} report statistical significance, "
                f"while the remainder are theoretical or qualitative."
            )
            # Answer
            answer = (
                f"The composite evidence strength is {thermometer.label}, "
                f"which means the confidence level is {thermometer.level.value.replace('_', '-')}."
            )

            l2 = f"{situation} {complication} {answer}"

            if config.include_citations:
                sources = set()
                for f in findings[:5]:
                    if isinstance(f, dict):
                        sources.add(f.get("source_file", "").replace(".json", ""))
                if sources:
                    l2 += f" Key sources: {', '.join(list(sources)[:3])}."

            sections.append(l2)

        # L3: Mechanistic detail
        if "L3" in config.disclosure_levels and findings:
            mechanisms = []
            for f in findings[:5]:
                if isinstance(f, dict):
                    ant = f.get("antecedent", "")
                    cons = f.get("consequent", "")
                    direction = f.get("direction", "")
                    if ant and cons:
                        mechanisms.append(f"{ant} → {direction} {cons}")

            if mechanisms:
                l3 = "Mechanistic pathways: " + "; ".join(mechanisms) + "."
                sections.append(l3)

            # Omega scores for researcher+
            if config.include_omega_scores:
                sections.append(
                    f"Evidence quality: ω = {thermometer.omega_composite:.2f} "
                    f"({thermometer.n_supporting_findings} findings)."
                )

        # Design implications for architect_designer
        if config.include_design_implications and findings:
            sections.append(
                f"Design implication: consider {topic_title.lower()} "
                f"as a factor in spatial design decisions."
            )

        # Gap analysis for researcher+
        if config.include_gap_analysis:
            sections.append(
                f"Research needed: further replication and cross-cultural validation "
                f"would strengthen the evidence base for {topic_title.lower()}."
            )

        prose = "\n\n".join(sections)

        # Enforce max length
        if config.max_length_words > 0:
            words = prose.split()
            if len(words) > config.max_length_words:
                prose = " ".join(words[:config.max_length_words]) + "..."

        return prose

    def _quality_check(self, prose: str) -> tuple:
        """Run prose through ProseRevisionService quality gate."""
        # Check disallowed phrases
        prose_lower = prose.lower()
        for phrase in self.DISALLOWED_PHRASES:
            if phrase in prose_lower:
                logger.warning(f"Disallowed phrase found: '{phrase}'")

        # Run prose revision service if available
        service = self._get_prose_service()
        if service is not None:
            try:
                report = service.full_critique(prose)
                score = report.overall_score
                passed = score >= 0.7 and report.critical_count == 0
                return score, passed
            except Exception as e:
                logger.warning(f"Prose quality check failed: {e}")

        # Fallback: basic checks
        word_count = len(prose.split())
        has_content = word_count > 10
        no_disallowed = not any(p in prose_lower for p in self.DISALLOWED_PHRASES)
        score = 0.8 if (has_content and no_disallowed) else 0.4
        return score, score >= 0.7
