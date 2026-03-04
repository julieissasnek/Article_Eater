"""
Framework Voice Renderer — Norm-Compliant Voice Generation from Corpus Data
============================================================================

Takes pre-computed corpus-grounded framework voice data (from mv_builder)
and renders structured, evidence-backed perspective text per framework.

Each voice follows this structure:
  1. Framework identification + paper count
  2. Key finding(s) with effect sizes
  3. Mechanism chain (if available)
  4. Scope conditions / complications
  5. What we don't know (gap)

The renderer uses ConfidenceThermometer calibrated language and runs
through ProseRevisionService as a quality gate.

Usage:
    from src.qa.framework_voice_renderer import FrameworkVoiceRenderer
    renderer = FrameworkVoiceRenderer()
    rendered = renderer.render_voices(mv_data, topic="daylight", limit=4)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rendered Voice Data Structure
# ---------------------------------------------------------------------------

@dataclass
class RenderedVoice:
    """A single rendered framework voice with structured content."""
    framework_abbr: str
    framework_name: str
    perspective: str
    n_papers: int
    n_findings: int
    top_findings_summary: List[str]
    mechanism_chains: List[str]
    scope_conditions: List[str]
    confidence_label: str  # "high", "moderate", "low", "insufficient"
    source: str  # "corpus_grounded" or "framework_template"
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework_abbr,
            "name": self.framework_name,
            "voice": self.perspective,
            "n_papers": self.n_papers,
            "n_findings": self.n_findings,
            "top_findings": self.top_findings_summary,
            "mechanism_chains": self.mechanism_chains,
            "scope_conditions": self.scope_conditions,
            "confidence_level": self.confidence_label,
            "source": self.source,
            "relevance_score": self.relevance_score,
        }


# ---------------------------------------------------------------------------
# Confidence-calibrated language maps
# ---------------------------------------------------------------------------

CONFIDENCE_LANGUAGE = {
    "high": {
        "verb": "shows",
        "qualifier": "consistently",
        "intro": "Strong evidence from",
    },
    "moderate": {
        "verb": "suggests",
        "qualifier": "in several studies",
        "intro": "Moderate evidence from",
    },
    "low": {
        "verb": "indicates",
        "qualifier": "in limited studies",
        "intro": "Preliminary evidence from",
    },
    "insufficient": {
        "verb": "may involve",
        "qualifier": "",
        "intro": "The corpus does not yet address",
    },
}


def _confidence_from_counts(n_papers: int, n_findings: int) -> str:
    """Map paper/finding counts to confidence label."""
    if n_papers >= 10 and n_findings >= 20:
        return "high"
    elif n_papers >= 3 and n_findings >= 5:
        return "moderate"
    elif n_papers >= 1:
        return "low"
    return "insufficient"


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class FrameworkVoiceRenderer:
    """
    Renders norm-compliant framework voice perspectives from corpus data.

    Uses confidence-calibrated language and optional prose quality checking.
    """

    def __init__(self, use_prose_gate: bool = False):
        """
        Args:
            use_prose_gate: If True, run each voice through ProseRevisionService.
                           Disabled by default for performance.
        """
        self._use_prose_gate = use_prose_gate
        self._prose_service = None

    def render_voices(
        self,
        mv_data: Dict[str, Any],
        topic: str = "",
        limit: int = 4,
    ) -> List[RenderedVoice]:
        """
        Render structured voices from pre-computed MV data.

        Args:
            mv_data: Output of mv_builder.build_framework_voices()
            topic: Query topic for relevance scoring
            limit: Maximum number of voices to return

        Returns:
            List of RenderedVoice objects, sorted by relevance
        """
        if not mv_data or "error" in mv_data:
            return []

        # Score and sort by topic relevance
        topic_words = set(topic.lower().split()) if topic else set()
        scored = []

        for abbr, data in mv_data.items():
            if not isinstance(data, dict):
                continue

            relevance = self._score_relevance(data, topic_words)
            scored.append((abbr, data, relevance))

        scored.sort(key=lambda x: (-x[2], -x[1].get("n_papers", 0)))

        # Render top voices
        rendered = []
        for abbr, data, score in scored[:limit]:
            voice = self._render_single_voice(abbr, data, score)
            rendered.append(voice)

        return rendered

    def render_voices_as_dicts(
        self,
        mv_data: Dict[str, Any],
        topic: str = "",
        limit: int = 4,
    ) -> List[Dict[str, Any]]:
        """Convenience: render and immediately convert to dicts."""
        return [v.to_dict() for v in self.render_voices(mv_data, topic, limit)]

    def _score_relevance(
        self, data: Dict, topic_words: set
    ) -> float:
        """Score framework relevance to the query topic."""
        relevance = 0.0

        # Keyword overlap with top findings
        for finding in data.get("top_findings", []):
            text = (
                finding.get("antecedent", "") + " " +
                finding.get("consequent", "")
            ).lower()
            relevance += sum(1 for w in topic_words if w in text)

        # Evidence volume bonus (capped)
        relevance += min(data.get("n_papers", 0) / 10, 2.0)

        return relevance

    def _render_single_voice(
        self, abbr: str, data: Dict, relevance: float
    ) -> RenderedVoice:
        """Render a single framework voice."""
        name = data.get("name", abbr)
        n_papers = data.get("n_papers", 0)
        n_findings = data.get("n_findings", 0)
        confidence = _confidence_from_counts(n_papers, n_findings)
        lang = CONFIDENCE_LANGUAGE[confidence]

        # Build perspective prose
        perspective = self._build_perspective(
            name, n_papers, n_findings, confidence, lang, data
        )

        # Summarize top findings
        finding_summaries = []
        for f in data.get("top_findings", [])[:3]:
            summary = self._summarize_finding(f, lang)
            if summary:
                finding_summaries.append(summary)

        # Optionally run through prose quality gate
        if self._use_prose_gate:
            perspective = self._quality_check(perspective)

        return RenderedVoice(
            framework_abbr=abbr,
            framework_name=name,
            perspective=perspective,
            n_papers=n_papers,
            n_findings=n_findings,
            top_findings_summary=finding_summaries,
            mechanism_chains=data.get("mechanism_chains", [])[:5],
            scope_conditions=data.get("scope_conditions", [])[:5],
            confidence_label=confidence,
            source=data.get("source", "corpus_grounded"),
            relevance_score=round(relevance, 2),
        )

    def _build_perspective(
        self,
        name: str,
        n_papers: int,
        n_findings: int,
        confidence: str,
        lang: Dict,
        data: Dict,
    ) -> str:
        """Build the structured perspective text."""
        if n_papers == 0:
            core = data.get("core_mechanism", "")
            return (
                f"{name}: The corpus does not yet address this topic through "
                f"this framework. Core mechanism: {core}"
            )

        parts = [
            f"{lang['intro']} {n_papers} paper(s) ({n_findings} findings) "
            f"addresses this through {name}."
        ]

        # Key finding
        top = data.get("top_findings", [])
        if top:
            best = top[0]
            ant = best.get("antecedent", "?")
            cons = best.get("consequent", "?")
            direction = best.get("direction", "")
            effect = best.get("effect_size")

            finding_text = f"The evidence {lang['qualifier']} {lang['verb']} that {ant}"
            if direction:
                finding_text += f" {direction}s"
            finding_text += f" {cons}"
            if effect is not None:
                finding_text += f" (d = {effect:.2f})"
            finding_text += "."
            parts.append(finding_text)

        # Mechanisms
        mechanisms = data.get("mechanism_chains", [])
        if mechanisms:
            parts.append(f"Proposed mechanism: {mechanisms[0]}.")

        # Scope conditions
        conditions = data.get("scope_conditions", [])
        if conditions:
            parts.append(f"Important scope condition: {conditions[0]}.")

        # Key principle from framework
        principle = data.get("key_principle", "")
        if principle:
            parts.append(f"Framework principle: {principle}")

        return " ".join(parts)

    def _summarize_finding(self, finding: Dict, lang: Dict) -> str:
        """Create a one-line summary of a finding."""
        ant = finding.get("antecedent", "")
        cons = finding.get("consequent", "")
        if not ant and not cons:
            return ""

        direction = finding.get("direction", "")
        effect = finding.get("effect_size")
        p_val = finding.get("p_value")

        parts = [f"{ant} → {cons}"]
        if direction:
            parts[0] += f" ({direction})"
        stats = []
        if effect is not None:
            stats.append(f"d={effect:.2f}")
        if p_val is not None:
            stats.append(f"p={p_val}")
        if stats:
            parts.append(f"[{', '.join(stats)}]")

        return " ".join(parts)

    def _quality_check(self, prose: str) -> str:
        """Run prose through ProseRevisionService quality gate."""
        if self._prose_service is None:
            try:
                from src.services.prose_revision_service import ProseRevisionService
                self._prose_service = ProseRevisionService(context="qa_response")
            except ImportError:
                logger.debug("ProseRevisionService not available — skipping quality check")
                return prose

        try:
            report = self._prose_service.critique(prose)
            # If critical issues exist, log them but don't fail
            if report.critical_count > 0:
                logger.warning(
                    f"Framework voice has {report.critical_count} critical prose issues"
                )
        except Exception as e:
            logger.debug(f"Prose quality check failed: {e}")

        return prose
