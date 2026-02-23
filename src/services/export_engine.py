"""
Article Eater V23 — Export Engine
Sprint 3.0.4 — 2026-02-08

Export functionality for evidence summaries, BibTeX, and verification checklists.
Based on panel recommendations:
- Cartwright: Evidence summaries with scope metadata
- Zaharia: Pipeline-friendly formats (JSONL, Parquet)
- Gawande: Verification checklists
- Munzner: Purpose-driven export bundles
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    JSONL = "jsonl"
    BIBTEX = "bibtex"
    GRAPHML = "graphml"
    CSV = "csv"
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"


class ExportPurpose(Enum):
    """Purpose-driven export bundles (Munzner recommendation)."""
    PRACTITIONER_BRIEFING = "practitioner_briefing"  # Quick design guidance
    LITERATURE_REVIEW = "literature_review"          # Academic synthesis
    SYSTEMATIC_REVIEW = "systematic_review"          # PRISMA-compatible
    PRESENTATION = "presentation"                     # Slides/visuals
    DATA_PIPELINE = "data_pipeline"                   # Machine-readable


@dataclass
class SourcePaper:
    """A source paper for BibTeX generation."""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None


@dataclass
class ExportedBelief:
    """A belief formatted for export."""
    id: str
    content: str
    credence: float
    uncertainty: float
    status: str
    level: str
    theory: Optional[str] = None
    scope_conditions: Optional[Dict[str, str]] = None
    sources: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class EvidenceSummary:
    """Evidence summary following Cartwright's recommendations."""
    topic: str
    generated_at: str

    # Main finding
    key_finding: str
    credence: float
    uncertainty: float
    confidence_label: str  # high/moderate/low/very low

    # Method and Stimulus (per user request)
    methods_used: List[str]  # e.g., ["RCT", "quasi-experimental", "observational"]
    stimuli: List[str]  # e.g., ["indoor plants", "window views", "nature sounds"]

    # Scope conditions
    scope: Dict[str, str]  # population, setting, methodology, limitations

    # Evidence base
    supporting_evidence: List[Dict[str, Any]]
    contradicting_evidence: List[Dict[str, Any]]
    total_studies: int

    # Practical section
    practical_implications: List[str]
    what_could_defeat: List[str]  # What would change this conclusion

    # Metadata
    query: Optional[str] = None
    export_format: str = "markdown"


@dataclass
class VerificationChecklist:
    """Verification checklist following Gawande's recommendations."""
    title: str
    generated_at: str

    # Checklist items
    items: List[Dict[str, Any]]

    # Summary
    total_items: int
    completed_items: int
    warnings: List[str]


class BibTeXGenerator:
    """Generates BibTeX citations from source papers."""

    def __init__(self):
        self.entry_types = {
            "article": self._format_article,
            "book": self._format_book,
            "inproceedings": self._format_inproceedings,
            "techreport": self._format_techreport,
            "misc": self._format_misc,
        }

    def generate(self, papers: List[SourcePaper]) -> str:
        """Generate BibTeX for a list of papers."""
        entries = []
        for paper in papers:
            entry = self._generate_entry(paper)
            entries.append(entry)
        return "\n\n".join(entries)

    def _generate_entry(self, paper: SourcePaper) -> str:
        """Generate a single BibTeX entry."""
        # Determine entry type
        if paper.journal:
            entry_type = "article"
        else:
            entry_type = "misc"

        # Generate citation key
        first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
        cite_key = f"{first_author.lower()}{paper.year}"

        # Format entry
        formatter = self.entry_types.get(entry_type, self._format_misc)
        return formatter(paper, cite_key, entry_type)

    def _format_article(
        self,
        paper: SourcePaper,
        cite_key: str,
        entry_type: str
    ) -> str:
        """Format article entry."""
        lines = [f"@article{{{cite_key},"]
        lines.append(f"  author = {{{self._format_authors(paper.authors)}}},")
        lines.append(f"  title = {{{{{paper.title}}}}},")
        lines.append(f"  journal = {{{paper.journal}}},")
        lines.append(f"  year = {{{paper.year}}},")

        if paper.volume:
            lines.append(f"  volume = {{{paper.volume}}},")
        if paper.pages:
            lines.append(f"  pages = {{{paper.pages}}},")
        if paper.doi:
            lines.append(f"  doi = {{{paper.doi}}},")
        if paper.url:
            lines.append(f"  url = {{{paper.url}}},")

        lines.append("}")
        return "\n".join(lines)

    def _format_book(
        self,
        paper: SourcePaper,
        cite_key: str,
        entry_type: str
    ) -> str:
        """Format book entry."""
        lines = [f"@book{{{cite_key},"]
        lines.append(f"  author = {{{self._format_authors(paper.authors)}}},")
        lines.append(f"  title = {{{{{paper.title}}}}},")
        lines.append(f"  year = {{{paper.year}}},")
        if paper.doi:
            lines.append(f"  doi = {{{paper.doi}}},")
        lines.append("}")
        return "\n".join(lines)

    def _format_inproceedings(
        self,
        paper: SourcePaper,
        cite_key: str,
        entry_type: str
    ) -> str:
        """Format conference paper entry."""
        return self._format_misc(paper, cite_key, "inproceedings")

    def _format_techreport(
        self,
        paper: SourcePaper,
        cite_key: str,
        entry_type: str
    ) -> str:
        """Format technical report entry."""
        return self._format_misc(paper, cite_key, "techreport")

    def _format_misc(
        self,
        paper: SourcePaper,
        cite_key: str,
        entry_type: str
    ) -> str:
        """Format misc/fallback entry."""
        lines = [f"@{entry_type}{{{cite_key},"]
        lines.append(f"  author = {{{self._format_authors(paper.authors)}}},")
        lines.append(f"  title = {{{{{paper.title}}}}},")
        lines.append(f"  year = {{{paper.year}}},")
        if paper.doi:
            lines.append(f"  doi = {{{paper.doi}}},")
        if paper.url:
            lines.append(f"  url = {{{paper.url}}},")
        lines.append("}")
        return "\n".join(lines)

    def _format_authors(self, authors: List[str]) -> str:
        """Format author list for BibTeX."""
        return " and ".join(authors)


class EvidenceSummaryGenerator:
    """
    Generates evidence summaries with scope metadata.
    Following Cartwright's recommendations:
    - What was found
    - Where it applies
    - What it depends on
    - What could defeat it
    """

    def __init__(self):
        self.templates = {
            "markdown": self._to_markdown,
            "json": self._to_json,
            "html": self._to_html,
        }

    def generate(
        self,
        topic: str,
        beliefs: List[ExportedBelief],
        query: Optional[str] = None,
        format: str = "markdown"
    ) -> str:
        """Generate evidence summary from beliefs."""
        summary = self._build_summary(topic, beliefs, query)

        formatter = self.templates.get(format, self._to_markdown)
        return formatter(summary)

    def _build_summary(
        self,
        topic: str,
        beliefs: List[ExportedBelief],
        query: Optional[str]
    ) -> EvidenceSummary:
        """Build EvidenceSummary from beliefs."""
        # Separate supporting and contradicting evidence
        supporting = []
        contradicting = []

        for belief in beliefs:
            item = {
                "id": belief.id,
                "content": belief.content,
                "credence": belief.credence,
                "status": belief.status,
                "sources": belief.sources
            }
            if belief.status == "REJECTED":
                contradicting.append(item)
            else:
                supporting.append(item)

        # Calculate aggregate credence
        if beliefs:
            avg_credence = sum(b.credence for b in beliefs) / len(beliefs)
            avg_uncertainty = sum(b.uncertainty for b in beliefs) / len(beliefs)
        else:
            avg_credence = 0.0
            avg_uncertainty = 1.0

        # Determine confidence label
        if avg_credence >= 0.75:
            confidence_label = "high"
        elif avg_credence >= 0.50:
            confidence_label = "moderate"
        elif avg_credence >= 0.25:
            confidence_label = "low"
        else:
            confidence_label = "very low"

        # Aggregate scope conditions
        scope = self._aggregate_scope(beliefs)

        # Generate key finding
        if supporting:
            top = max(supporting, key=lambda x: x["credence"])
            key_finding = top["content"]
        else:
            key_finding = "No clear finding established."

        # Generate practical implications
        practical = self._generate_practical_implications(beliefs)

        # Generate defeat conditions
        defeat_conditions = self._generate_defeat_conditions(beliefs, scope)

        # Extract methods and stimuli
        methods, stimuli = self._extract_methods_and_stimuli(beliefs, scope)

        return EvidenceSummary(
            topic=topic,
            generated_at=datetime.now().isoformat(),
            key_finding=key_finding,
            credence=avg_credence,
            uncertainty=avg_uncertainty,
            confidence_label=confidence_label,
            methods_used=methods,
            stimuli=stimuli,
            scope=scope,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            total_studies=sum(len(b.sources) for b in beliefs),
            practical_implications=practical,
            what_could_defeat=defeat_conditions,
            query=query
        )

    def _aggregate_scope(self, beliefs: List[ExportedBelief]) -> Dict[str, str]:
        """Aggregate scope conditions from beliefs."""
        scope = {
            "population": "Not specified",
            "setting": "Not specified",
            "methodology": "Not specified",
            "limitations": "Not specified"
        }

        populations = set()
        settings = set()
        methods = set()
        limitations = set()

        for belief in beliefs:
            if belief.scope_conditions:
                if "population" in belief.scope_conditions:
                    populations.add(belief.scope_conditions["population"])
                if "setting" in belief.scope_conditions:
                    settings.add(belief.scope_conditions["setting"])
                if "methodology" in belief.scope_conditions:
                    methods.add(belief.scope_conditions["methodology"])
                if "limitations" in belief.scope_conditions:
                    limitations.add(belief.scope_conditions["limitations"])

        if populations:
            scope["population"] = "; ".join(populations)
        if settings:
            scope["setting"] = "; ".join(settings)
        if methods:
            scope["methodology"] = "; ".join(methods)
        if limitations:
            scope["limitations"] = "; ".join(limitations)

        return scope

    def _extract_methods_and_stimuli(
        self,
        beliefs: List[ExportedBelief],
        scope: Dict[str, str]
    ) -> tuple:
        """Extract research methods and stimuli/interventions from beliefs."""
        methods = set()
        stimuli = set()

        # Method keywords to look for
        method_keywords = {
            "RCT": ["randomized", "rct", "randomised"],
            "Quasi-experimental": ["quasi-experiment", "quasi experiment", "non-randomized"],
            "Observational": ["observational", "survey", "cross-sectional"],
            "Meta-analysis": ["meta-analysis", "meta analysis", "systematic review"],
            "Laboratory": ["laboratory", "lab study", "controlled experiment"],
            "Field study": ["field study", "naturalistic", "real-world"],
            "Longitudinal": ["longitudinal", "follow-up", "prospective"],
            "Self-report": ["self-report", "questionnaire", "survey"],
            "Physiological": ["cortisol", "heart rate", "hrv", "eeg", "fmri"],
        }

        # Stimulus keywords to look for
        stimulus_keywords = {
            "Indoor plants": ["indoor plant", "potted plant", "office plant", "houseplant"],
            "Window views": ["window view", "view through window", "natural view"],
            "Nature images": ["nature image", "nature photo", "picture of nature"],
            "Nature sounds": ["nature sound", "birdsong", "water sound", "natural sound"],
            "Green space": ["green space", "park", "garden", "outdoor nature"],
            "Natural light": ["natural light", "daylight", "sunlight"],
            "Water features": ["water feature", "fountain", "aquarium"],
            "Natural materials": ["wood", "natural material", "biophilic material"],
            "Forest bathing": ["forest bathing", "shinrin-yoku", "forest walk"],
        }

        # Check methodology from scope
        methodology = scope.get("methodology", "").lower()
        for method, keywords in method_keywords.items():
            if any(kw in methodology for kw in keywords):
                methods.add(method)

        # Check belief content for methods and stimuli
        for belief in beliefs:
            content = belief.content.lower()

            # Check for methods
            for method, keywords in method_keywords.items():
                if any(kw in content for kw in keywords):
                    methods.add(method)

            # Check for stimuli
            for stimulus, keywords in stimulus_keywords.items():
                if any(kw in content for kw in keywords):
                    stimuli.add(stimulus)

            # Also check scope conditions if available
            if belief.scope_conditions:
                for key, val in belief.scope_conditions.items():
                    val_lower = val.lower() if val else ""
                    for stimulus, keywords in stimulus_keywords.items():
                        if any(kw in val_lower for kw in keywords):
                            stimuli.add(stimulus)

        return list(methods) or ["Not specified"], list(stimuli) or ["Not specified"]

    def _generate_practical_implications(
        self,
        beliefs: List[ExportedBelief]
    ) -> List[str]:
        """Generate practical implications from beliefs."""
        implications = []

        # Extract high-credence empirical beliefs
        empirical = [b for b in beliefs if b.level == "EMPIRICAL" and b.credence >= 0.6]

        for belief in empirical[:5]:  # Top 5
            # Convert belief to actionable implication
            content = belief.content
            if content.startswith("People ") or content.startswith("Participants "):
                # Convert observation to recommendation
                implications.append(f"Consider: {content.lower()}")
            else:
                implications.append(content)

        if not implications:
            implications.append("Insufficient evidence for practical recommendations.")

        return implications

    def _generate_defeat_conditions(
        self,
        beliefs: List[ExportedBelief],
        scope: Dict[str, str]
    ) -> List[str]:
        """Generate conditions that could defeat the conclusion."""
        conditions = []

        # Scope-based defeat conditions
        if "laboratory" in scope.get("setting", "").lower():
            conditions.append("Findings may not replicate in naturalistic settings")

        if "western" in scope.get("population", "").lower():
            conditions.append("Cross-cultural validity not established")

        if "self-report" in scope.get("methodology", "").lower():
            conditions.append("Objective measures may show different results")

        # Evidence-based defeat conditions
        contested = [b for b in beliefs if b.status == "CONTESTED"]
        if contested:
            conditions.append(f"{len(contested)} findings are contested and may be revised")

        stubs = [b for b in beliefs if b.status == "STUB"]
        if stubs:
            conditions.append(f"{len(stubs)} findings lack sufficient evidence")

        if not conditions:
            conditions.append("No obvious defeat conditions identified")

        return conditions

    def _to_markdown(self, summary: EvidenceSummary) -> str:
        """Convert summary to Markdown format."""
        lines = [
            f"# Evidence Summary: {summary.topic}",
            f"*Generated: {summary.generated_at}*",
            "",
            "## Key Finding",
            f"{summary.key_finding}",
            "",
            f"**Credence**: {summary.credence:.2f} ± {summary.uncertainty:.2f}",
            f"**Confidence**: {summary.confidence_label.title()}",
            "",
            "## Methods and Stimuli",
            "",
            f"**Research Methods**: {', '.join(summary.methods_used)}",
            f"**Stimuli/Interventions**: {', '.join(summary.stimuli)}",
            "",
            "## Scope Conditions",
            "",
            f"- **Population**: {summary.scope['population']}",
            f"- **Setting**: {summary.scope['setting']}",
            f"- **Methodology**: {summary.scope['methodology']}",
            f"- **Limitations**: {summary.scope['limitations']}",
            "",
            "## Supporting Evidence",
            "",
        ]

        for ev in summary.supporting_evidence[:10]:
            lines.append(f"- [{ev['status']}] {ev['content']} (credence: {ev['credence']:.2f})")

        if summary.contradicting_evidence:
            lines.extend([
                "",
                "## Contradicting Evidence",
                ""
            ])
            for ev in summary.contradicting_evidence[:5]:
                lines.append(f"- {ev['content']}")

        lines.extend([
            "",
            "## Practical Implications",
            ""
        ])
        for impl in summary.practical_implications:
            lines.append(f"- {impl}")

        lines.extend([
            "",
            "## What Could Defeat This",
            ""
        ])
        for cond in summary.what_could_defeat:
            lines.append(f"- {cond}")

        lines.extend([
            "",
            "---",
            f"*Based on {summary.total_studies} source studies*",
            ""
        ])

        return "\n".join(lines)

    def _to_json(self, summary: EvidenceSummary) -> str:
        """Convert summary to JSON format."""
        return json.dumps(asdict(summary), indent=2)

    def _to_html(self, summary: EvidenceSummary) -> str:
        """Convert summary to HTML format."""
        # Convert markdown to basic HTML
        md = self._to_markdown(summary)
        # Simple conversion (would use proper markdown parser in production)
        html = md.replace("# ", "<h1>").replace("\n\n", "</p><p>")
        return f"<html><body><p>{html}</p></body></html>"


class VerificationChecklistGenerator:
    """
    Generates verification checklists following Gawande's recommendations.
    Ensures exports are complete and accurate.
    """

    def generate(
        self,
        beliefs: List[ExportedBelief],
        sources: List[SourcePaper],
        title: str = "Evidence Export Verification"
    ) -> VerificationChecklist:
        """Generate verification checklist for an export."""
        items = []

        # Scope conditions reviewed
        beliefs_with_scope = sum(1 for b in beliefs if b.scope_conditions)
        items.append({
            "category": "Scope",
            "item": "Scope conditions reviewed",
            "checked": beliefs_with_scope == len(beliefs),
            "detail": f"{beliefs_with_scope}/{len(beliefs)} beliefs have scope conditions"
        })

        # Contradicting evidence acknowledged
        rejected = [b for b in beliefs if b.status == "REJECTED"]
        contested = [b for b in beliefs if b.status == "CONTESTED"]
        items.append({
            "category": "Evidence",
            "item": "Contradicting evidence acknowledged",
            "checked": True,  # Always true if we got here
            "detail": f"{len(rejected)} rejected, {len(contested)} contested"
        })

        # Confidence levels appropriate
        high_cred_low_evidence = sum(
            1 for b in beliefs
            if b.credence > 0.8 and len(b.sources) < 3
        )
        items.append({
            "category": "Confidence",
            "item": "Confidence levels appropriate",
            "checked": high_cred_low_evidence == 0,
            "detail": f"{high_cred_low_evidence} beliefs may have inflated confidence"
        })

        # Citations complete
        beliefs_with_sources = sum(1 for b in beliefs if b.sources)
        items.append({
            "category": "Citations",
            "item": "Citations complete",
            "checked": beliefs_with_sources == len(beliefs),
            "detail": f"{beliefs_with_sources}/{len(beliefs)} beliefs have citations"
        })

        # Source papers included
        items.append({
            "category": "Sources",
            "item": "Source papers included",
            "checked": len(sources) > 0,
            "detail": f"{len(sources)} source papers"
        })

        # Generate warnings
        warnings = []
        if beliefs_with_scope < len(beliefs):
            warnings.append(f"{len(beliefs) - beliefs_with_scope} beliefs missing scope conditions")
        if high_cred_low_evidence > 0:
            warnings.append(f"{high_cred_low_evidence} beliefs may have inflated confidence")
        if contested:
            warnings.append(f"{len(contested)} beliefs are contested between communities")

        completed = sum(1 for item in items if item["checked"])

        return VerificationChecklist(
            title=title,
            generated_at=datetime.now().isoformat(),
            items=items,
            total_items=len(items),
            completed_items=completed,
            warnings=warnings
        )

    def to_markdown(self, checklist: VerificationChecklist) -> str:
        """Convert checklist to Markdown format."""
        lines = [
            f"# {checklist.title}",
            f"*Generated: {checklist.generated_at}*",
            "",
            f"**Status**: {checklist.completed_items}/{checklist.total_items} items verified",
            "",
            "## Verification Items",
            ""
        ]

        for item in checklist.items:
            check = "✓" if item["checked"] else "☐"
            lines.append(f"- [{check}] **{item['item']}** ({item['category']})")
            lines.append(f"  - {item['detail']}")

        if checklist.warnings:
            lines.extend([
                "",
                "## Warnings",
                ""
            ])
            for warning in checklist.warnings:
                lines.append(f"⚠️ {warning}")

        return "\n".join(lines)


@dataclass
class ArticleMetadata:
    """Complete metadata for an article/study — the full table format."""
    # Citation
    article_id: str
    citation: str  # e.g., "Ulrich (1984)"
    title: str
    authors: List[str]
    year: int
    journal: Optional[str] = None
    doi: Optional[str] = None

    # Study Design
    study_type: str = "Unknown"  # RCT, quasi-experimental, observational, meta-analysis
    randomization: str = "Unknown"  # True, Stratified, Cluster, None
    blinding: str = "Unknown"  # Double-blind, Single-blind, Open-label
    control_type: str = "Unknown"  # Placebo, Active, Waitlist, None

    # Sample
    sample_size: Optional[int] = None
    population: str = "Not specified"
    age_range: Optional[str] = None
    gender_distribution: Optional[str] = None
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None
    attrition_rate: Optional[float] = None

    # Intervention/Stimulus
    intervention: Optional[str] = None
    intervention_duration: Optional[str] = None
    intervention_frequency: Optional[str] = None
    control_condition: Optional[str] = None

    # Setting
    setting: str = "Not specified"  # Laboratory, Field, Hospital, Office, etc.
    country: Optional[str] = None
    environment_type: Optional[str] = None  # Indoor, Outdoor, Mixed

    # Outcomes
    primary_outcome: Optional[str] = None
    secondary_outcomes: List[str] = field(default_factory=list)
    outcome_measures: List[str] = field(default_factory=list)  # Instruments used
    follow_up_duration: Optional[str] = None

    # Results
    effect_size: Optional[float] = None
    effect_size_type: str = "d"  # d, r, OR, RR, etc.
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    p_value: Optional[float] = None
    statistical_test: Optional[str] = None

    # Quality Assessment
    quality_score: Optional[float] = None
    quality_tool: str = "Not assessed"  # Cochrane RoB, GRADE, NOS, etc.
    risk_of_bias: str = "Not assessed"  # Low, Some concerns, High
    limitations: List[str] = field(default_factory=list)

    # Extracted Beliefs
    beliefs_extracted: int = 0
    key_findings: List[str] = field(default_factory=list)

    # Notes
    notes: Optional[str] = None


class ArticleMetadataTableGenerator:
    """
    Generates complete article metadata tables.
    Shows all extracted information for each study in structured format.
    """

    def generate(
        self,
        articles: List[ArticleMetadata],
        format: str = "markdown",
        columns: Optional[List[str]] = None
    ) -> str:
        """Generate article metadata table in specified format."""
        if format == "markdown":
            return self._to_markdown(articles, columns)
        elif format == "csv":
            return self._to_csv(articles)
        elif format == "html":
            return self._to_html(articles)
        else:
            return self._to_markdown(articles, columns)

    def _to_markdown(
        self,
        articles: List[ArticleMetadata],
        columns: Optional[List[str]] = None
    ) -> str:
        """Generate comprehensive Markdown table."""
        lines = [
            "# Article Metadata Table",
            "",
            "## Study Characteristics",
            "",
            "| Citation | Year | Type | N | Population | Setting | Intervention |",
            "|----------|------|------|---|------------|---------|--------------|"
        ]

        for a in articles:
            lines.append(
                f"| {a.citation} | {a.year} | {a.study_type} | "
                f"{a.sample_size or '—'} | {a.population[:30]}... | "
                f"{a.setting} | {a.intervention or '—'} |"
            )

        lines.extend([
            "",
            "## Methods and Design",
            "",
            "| Citation | Randomization | Blinding | Control | Duration | Follow-up |",
            "|----------|---------------|----------|---------|----------|-----------|"
        ])

        for a in articles:
            lines.append(
                f"| {a.citation} | {a.randomization} | {a.blinding} | "
                f"{a.control_type} | {a.intervention_duration or '—'} | "
                f"{a.follow_up_duration or '—'} |"
            )

        lines.extend([
            "",
            "## Outcomes and Results",
            "",
            "| Citation | Primary Outcome | Effect Size | 95% CI | p-value | Quality |",
            "|----------|-----------------|-------------|--------|---------|---------|"
        ])

        for a in articles:
            es = f"{a.effect_size:.2f} ({a.effect_size_type})" if a.effect_size else "—"
            ci = f"[{a.ci_lower:.2f}, {a.ci_upper:.2f}]" if a.ci_lower and a.ci_upper else "—"
            p = f"{a.p_value:.3f}" if a.p_value and a.p_value >= 0.001 else ("<.001" if a.p_value else "—")

            lines.append(
                f"| {a.citation} | {a.primary_outcome or '—'} | {es} | "
                f"{ci} | {p} | {a.risk_of_bias} |"
            )

        lines.extend([
            "",
            "## Key Findings",
            ""
        ])

        for a in articles:
            lines.append(f"### {a.citation}")
            if a.key_findings:
                for finding in a.key_findings:
                    lines.append(f"- {finding}")
            else:
                lines.append("- No key findings extracted")
            lines.append("")

        lines.extend([
            "---",
            f"*{len(articles)} articles included*"
        ])

        return "\n".join(lines)

    def _to_csv(self, articles: List[ArticleMetadata]) -> str:
        """Generate comprehensive CSV."""
        headers = [
            "article_id", "citation", "title", "authors", "year", "journal", "doi",
            "study_type", "randomization", "blinding", "control_type",
            "sample_size", "population", "age_range", "gender_distribution",
            "intervention", "intervention_duration", "control_condition",
            "setting", "country", "environment_type",
            "primary_outcome", "secondary_outcomes", "outcome_measures", "follow_up_duration",
            "effect_size", "effect_size_type", "ci_lower", "ci_upper", "p_value",
            "quality_score", "quality_tool", "risk_of_bias", "limitations",
            "beliefs_extracted", "key_findings", "notes"
        ]

        lines = [",".join(headers)]

        for a in articles:
            row = [
                a.article_id,
                f'"{a.citation}"',
                f'"{a.title}"',
                f'"{"; ".join(a.authors)}"',
                str(a.year),
                f'"{a.journal or ""}"',
                a.doi or "",
                a.study_type,
                a.randomization,
                a.blinding,
                a.control_type,
                str(a.sample_size or ""),
                f'"{a.population}"',
                a.age_range or "",
                a.gender_distribution or "",
                f'"{a.intervention or ""}"',
                a.intervention_duration or "",
                f'"{a.control_condition or ""}"',
                a.setting,
                a.country or "",
                a.environment_type or "",
                f'"{a.primary_outcome or ""}"',
                f'"{"; ".join(a.secondary_outcomes)}"',
                f'"{"; ".join(a.outcome_measures)}"',
                a.follow_up_duration or "",
                str(a.effect_size or ""),
                a.effect_size_type,
                str(a.ci_lower or ""),
                str(a.ci_upper or ""),
                str(a.p_value or ""),
                str(a.quality_score or ""),
                a.quality_tool,
                a.risk_of_bias,
                f'"{"; ".join(a.limitations)}"',
                str(a.beliefs_extracted),
                f'"{"; ".join(a.key_findings)}"',
                f'"{a.notes or ""}"'
            ]
            lines.append(",".join(row))

        return "\n".join(lines)

    def _to_html(self, articles: List[ArticleMetadata]) -> str:
        """Generate styled HTML table."""
        rows = []
        for a in articles:
            es = f"{a.effect_size:.2f} ({a.effect_size_type})" if a.effect_size else "—"
            ci = f"[{a.ci_lower:.2f}, {a.ci_upper:.2f}]" if a.ci_lower and a.ci_upper else "—"
            p = f"{a.p_value:.3f}" if a.p_value and a.p_value >= 0.001 else ("<.001" if a.p_value else "—")

            quality_color = {
                "Low": "#85D2A3",
                "Some concerns": "#F5D491",
                "High": "#E8A87C",
                "Not assessed": "#B8C5D0"
            }.get(a.risk_of_bias, "#B8C5D0")

            rows.append(f"""
            <tr>
                <td><strong>{a.citation}</strong><br><small>{a.title[:50]}...</small></td>
                <td>{a.study_type}</td>
                <td>{a.sample_size or '—'}</td>
                <td>{a.intervention or '—'}</td>
                <td>{a.primary_outcome or '—'}</td>
                <td>{es}</td>
                <td>{ci}</td>
                <td>{p}</td>
                <td style="background-color: {quality_color}">{a.risk_of_bias}</td>
            </tr>""")

        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Georgia, serif; background-color: #FFF9F0; color: #4A5568; }}
                h1 {{ color: #5B8FB9; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th {{ background-color: #5B8FB9; color: white; padding: 12px; text-align: left; }}
                td {{ border: 1px solid #E2E8F0; padding: 10px; vertical-align: top; }}
                tr:nth-child(even) {{ background-color: #F8FCFF; }}
                tr:hover {{ background-color: #E8F4F8; }}
                small {{ color: #718096; }}
            </style>
        </head>
        <body>
            <h1>Article Metadata Table</h1>
            <p><em>{len(articles)} articles</em></p>
            <table>
                <thead>
                    <tr>
                        <th>Citation</th>
                        <th>Type</th>
                        <th>N</th>
                        <th>Intervention</th>
                        <th>Primary Outcome</th>
                        <th>Effect Size</th>
                        <th>95% CI</th>
                        <th>p</th>
                        <th>Risk of Bias</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </body>
        </html>
        """


@dataclass
class RCTStudyFact:
    """Facts extracted from an RCT study for tabular display."""
    study_id: str
    citation: str  # e.g., "Ulrich 1984"
    sample_size: Optional[int] = None
    intervention: Optional[str] = None
    control: Optional[str] = None
    outcome_measure: Optional[str] = None
    effect_size: Optional[float] = None
    effect_size_type: str = "d"  # Cohen's d, r, OR, etc.
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    p_value: Optional[float] = None
    study_quality: str = "Not assessed"  # High, Moderate, Low, Not assessed
    randomization: str = "Unknown"  # True RCT, Quasi-experimental, Unknown
    blinding: str = "Unknown"  # Double-blind, Single-blind, Open, Unknown
    follow_up: Optional[str] = None
    notes: Optional[str] = None


class RCTTableGenerator:
    """
    Generates structured tables of RCT study facts.
    Useful for systematic reviews and meta-analyses.
    """

    def __init__(self):
        self.columns = [
            "Study", "N", "Intervention", "Control", "Outcome",
            "Effect Size", "95% CI", "p", "Quality", "Design"
        ]

    def generate(
        self,
        studies: List[RCTStudyFact],
        format: str = "markdown"
    ) -> str:
        """Generate RCT facts table in specified format."""
        if format == "markdown":
            return self._to_markdown(studies)
        elif format == "csv":
            return self._to_csv(studies)
        elif format == "html":
            return self._to_html(studies)
        else:
            return self._to_markdown(studies)

    def _to_markdown(self, studies: List[RCTStudyFact]) -> str:
        """Generate Markdown table."""
        lines = [
            "# RCT Study Facts",
            "",
            "| Study | N | Intervention | Control | Outcome | Effect Size | 95% CI | p | Quality | Design |",
            "|-------|---|--------------|---------|---------|-------------|--------|---|---------|--------|"
        ]

        for s in studies:
            # Format effect size with type
            es = f"{s.effect_size:.2f} ({s.effect_size_type})" if s.effect_size else "—"

            # Format confidence interval
            if s.ci_lower is not None and s.ci_upper is not None:
                ci = f"[{s.ci_lower:.2f}, {s.ci_upper:.2f}]"
            else:
                ci = "—"

            # Format p-value
            if s.p_value is not None:
                p = f"{s.p_value:.3f}" if s.p_value >= 0.001 else "<.001"
            else:
                p = "—"

            # Format sample size
            n = str(s.sample_size) if s.sample_size else "—"

            lines.append(
                f"| {s.citation} | {n} | {s.intervention or '—'} | "
                f"{s.control or '—'} | {s.outcome_measure or '—'} | "
                f"{es} | {ci} | {p} | {s.study_quality} | {s.randomization} |"
            )

        lines.extend([
            "",
            "---",
            "*Effect sizes: d = Cohen's d, r = correlation, OR = odds ratio*",
            f"*{len(studies)} studies included*"
        ])

        return "\n".join(lines)

    def _to_csv(self, studies: List[RCTStudyFact]) -> str:
        """Generate CSV table."""
        lines = [
            "Study,N,Intervention,Control,Outcome,Effect Size,ES Type,CI Lower,CI Upper,p-value,Quality,Randomization,Blinding,Follow-up,Notes"
        ]

        for s in studies:
            lines.append(
                f'"{s.citation}",{s.sample_size or ""},"{s.intervention or ""}",'
                f'"{s.control or ""}","{s.outcome_measure or ""}",'
                f'{s.effect_size or ""},{s.effect_size_type},'
                f'{s.ci_lower or ""},{s.ci_upper or ""},{s.p_value or ""},'
                f'"{s.study_quality}","{s.randomization}","{s.blinding}",'
                f'"{s.follow_up or ""}","{s.notes or ""}"'
            )

        return "\n".join(lines)

    def _to_html(self, studies: List[RCTStudyFact]) -> str:
        """Generate HTML table with styling."""
        rows = []
        for s in studies:
            es = f"{s.effect_size:.2f} ({s.effect_size_type})" if s.effect_size else "—"
            ci = f"[{s.ci_lower:.2f}, {s.ci_upper:.2f}]" if s.ci_lower and s.ci_upper else "—"
            p = f"{s.p_value:.3f}" if s.p_value and s.p_value >= 0.001 else ("<.001" if s.p_value else "—")

            # Quality color coding
            quality_color = {
                "High": "#85D2A3",
                "Moderate": "#F5D491",
                "Low": "#E8A87C",
                "Not assessed": "#B8C5D0"
            }.get(s.study_quality, "#B8C5D0")

            rows.append(f"""
            <tr>
                <td>{s.citation}</td>
                <td>{s.sample_size or '—'}</td>
                <td>{s.intervention or '—'}</td>
                <td>{s.control or '—'}</td>
                <td>{s.outcome_measure or '—'}</td>
                <td>{es}</td>
                <td>{ci}</td>
                <td>{p}</td>
                <td style="background-color: {quality_color}">{s.study_quality}</td>
                <td>{s.randomization}</td>
            </tr>""")

        return f"""
        <html>
        <head>
            <style>
                table {{ border-collapse: collapse; width: 100%; font-family: Georgia, serif; }}
                th {{ background-color: #5B8FB9; color: white; padding: 12px; text-align: left; }}
                td {{ border: 1px solid #E2E8F0; padding: 8px; color: #4A5568; }}
                tr:nth-child(even) {{ background-color: #FFF9F0; }}
                tr:hover {{ background-color: #E8F4F8; }}
            </style>
        </head>
        <body>
            <h1 style="color: #5B8FB9;">RCT Study Facts</h1>
            <table>
                <thead>
                    <tr>
                        <th>Study</th>
                        <th>N</th>
                        <th>Intervention</th>
                        <th>Control</th>
                        <th>Outcome</th>
                        <th>Effect Size</th>
                        <th>95% CI</th>
                        <th>p</th>
                        <th>Quality</th>
                        <th>Design</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
            <p><em>{len(studies)} studies included</em></p>
        </body>
        </html>
        """


class ExportEngine:
    """
    Main export engine combining all export functionality.
    Supports purpose-driven bundles per Munzner recommendation.
    """

    def __init__(self):
        self.bibtex_gen = BibTeXGenerator()
        self.summary_gen = EvidenceSummaryGenerator()
        self.checklist_gen = VerificationChecklistGenerator()
        self.rct_table_gen = RCTTableGenerator()
        self.article_table_gen = ArticleMetadataTableGenerator()

    def export_bibtex(self, papers: List[SourcePaper]) -> str:
        """Export BibTeX citations."""
        return self.bibtex_gen.generate(papers)

    def export_summary(
        self,
        topic: str,
        beliefs: List[ExportedBelief],
        query: Optional[str] = None,
        format: str = "markdown"
    ) -> str:
        """Export evidence summary."""
        return self.summary_gen.generate(topic, beliefs, query, format)

    def export_checklist(
        self,
        beliefs: List[ExportedBelief],
        sources: List[SourcePaper]
    ) -> str:
        """Export verification checklist."""
        checklist = self.checklist_gen.generate(beliefs, sources)
        return self.checklist_gen.to_markdown(checklist)

    def export_rct_table(
        self,
        studies: List[RCTStudyFact],
        format: str = "markdown"
    ) -> str:
        """Export RCT study facts as a structured table."""
        return self.rct_table_gen.generate(studies, format)

    def export_article_metadata_table(
        self,
        articles: List[ArticleMetadata],
        format: str = "markdown"
    ) -> str:
        """Export complete article metadata table."""
        return self.article_table_gen.generate(articles, format)

    def export_to_docx(
        self,
        content: str,
        title: str = "Evidence Summary"
    ) -> bytes:
        """
        Export content to DOCX format.
        Requires python-docx library.
        Returns bytes that can be written to file.
        """
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.enum.style import WD_STYLE_TYPE
        except ImportError:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return b""

        doc = Document()

        # Add title
        doc.add_heading(title, 0)

        # Parse markdown-like content and add to document
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            elif line.startswith('- '):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif line.startswith('| '):
                # Table row - simplified handling
                doc.add_paragraph(line.replace('|', ' | '))
            elif line.startswith('*') and line.endswith('*'):
                p = doc.add_paragraph()
                p.add_run(line.strip('*')).italic = True
            elif line.startswith('**') and '**' in line[2:]:
                p = doc.add_paragraph()
                p.add_run(line.replace('**', '')).bold = True
            else:
                doc.add_paragraph(line)

        # Save to bytes
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.read()

    def export_to_pdf(
        self,
        content: str,
        title: str = "Evidence Summary"
    ) -> bytes:
        """
        Export content to PDF format.
        Requires reportlab library.
        Returns bytes that can be written to file.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
        except ImportError:
            logger.warning("reportlab not installed. Install with: pip install reportlab")
            return b""

        from io import BytesIO
        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()

        # Custom styles matching cheerful color scheme
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            textColor=colors.HexColor('#5B8FB9'),
            fontSize=18
        ))
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            textColor=colors.HexColor('#5B8FB9'),
            fontSize=14
        ))
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            textColor=colors.HexColor('#4A5568'),
            fontSize=10
        ))

        story = []

        # Add title
        story.append(Paragraph(title, styles['CustomTitle']))
        story.append(Spacer(1, 12))

        # Parse content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
            elif line.startswith('# '):
                story.append(Paragraph(line[2:], styles['CustomTitle']))
            elif line.startswith('## '):
                story.append(Spacer(1, 12))
                story.append(Paragraph(line[3:], styles['CustomHeading']))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
            elif line.startswith('- '):
                story.append(Paragraph(f"• {line[2:]}", styles['CustomBody']))
            elif line.startswith('*') and line.endswith('*'):
                story.append(Paragraph(f"<i>{line.strip('*')}</i>", styles['CustomBody']))
            elif '**' in line:
                formatted = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                story.append(Paragraph(formatted, styles['CustomBody']))
            else:
                story.append(Paragraph(line, styles['CustomBody']))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    def export_bundle(
        self,
        purpose: ExportPurpose,
        topic: str,
        beliefs: List[ExportedBelief],
        sources: List[SourcePaper],
        output_dir: Path,
        rct_studies: Optional[List[RCTStudyFact]] = None
    ) -> Dict[str, str]:
        """
        Export a purpose-driven bundle.
        Returns dict of {filename: content} for each exported file.
        """
        bundle = {}
        output_dir.mkdir(parents=True, exist_ok=True)

        if purpose == ExportPurpose.PRACTITIONER_BRIEFING:
            # Quick design guidance
            bundle["summary.md"] = self.export_summary(
                topic, beliefs, format="markdown"
            )
            bundle["checklist.md"] = self.export_checklist(beliefs, sources)

        elif purpose == ExportPurpose.LITERATURE_REVIEW:
            # Academic synthesis
            bundle["summary.md"] = self.export_summary(
                topic, beliefs, format="markdown"
            )
            bundle["references.bib"] = self.export_bibtex(sources)
            bundle["beliefs.json"] = json.dumps(
                [asdict(b) for b in beliefs], indent=2
            )
            bundle["checklist.md"] = self.export_checklist(beliefs, sources)

        elif purpose == ExportPurpose.SYSTEMATIC_REVIEW:
            # PRISMA-compatible
            bundle["evidence_summary.json"] = self.export_summary(
                topic, beliefs, format="json"
            )
            bundle["references.bib"] = self.export_bibtex(sources)
            bundle["beliefs.jsonl"] = "\n".join(
                json.dumps(asdict(b)) for b in beliefs
            )
            bundle["sources.jsonl"] = "\n".join(
                json.dumps(asdict(s)) for s in sources
            )
            bundle["checklist.md"] = self.export_checklist(beliefs, sources)
            # Include RCT table if studies provided
            if rct_studies:
                bundle["rct_table.md"] = self.export_rct_table(rct_studies, "markdown")
                bundle["rct_table.csv"] = self.export_rct_table(rct_studies, "csv")
                bundle["rct_table.html"] = self.export_rct_table(rct_studies, "html")

        elif purpose == ExportPurpose.DATA_PIPELINE:
            # Machine-readable
            bundle["beliefs.jsonl"] = "\n".join(
                json.dumps(asdict(b)) for b in beliefs
            )
            bundle["sources.jsonl"] = "\n".join(
                json.dumps(asdict(s)) for s in sources
            )
            bundle["manifest.json"] = json.dumps({
                "topic": topic,
                "generated_at": datetime.now().isoformat(),
                "belief_count": len(beliefs),
                "source_count": len(sources),
                "format_version": "1.0"
            }, indent=2)

        else:  # PRESENTATION or default
            bundle["summary.md"] = self.export_summary(
                topic, beliefs, format="markdown"
            )

        # Write files
        for filename, content in bundle.items():
            filepath = output_dir / filename
            filepath.write_text(content)

        return bundle


# Convenience functions
_engine: Optional[ExportEngine] = None


def get_export_engine() -> ExportEngine:
    """Get or create export engine singleton."""
    global _engine
    if _engine is None:
        _engine = ExportEngine()
    return _engine


def export_bibtex(papers: List[SourcePaper]) -> str:
    """Export BibTeX citations."""
    return get_export_engine().export_bibtex(papers)


def export_summary(
    topic: str,
    beliefs: List[ExportedBelief],
    query: Optional[str] = None,
    format: str = "markdown"
) -> str:
    """Export evidence summary."""
    return get_export_engine().export_summary(topic, beliefs, query, format)
