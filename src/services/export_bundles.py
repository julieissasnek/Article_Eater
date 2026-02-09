"""
Purpose-Driven Export Bundles (Munzner Framework).
Sprint 3.0.4-E — 2026-02-09

Comprehensive export bundle system following Tamara Munzner's nested model
for visualization design. Each bundle is optimized for:
1. Domain situation (who uses it, in what context)
2. Data/task abstraction (what they need to accomplish)
3. Visual encoding (how information is presented)
4. Algorithm (efficient generation)

Export Purposes:
- PRACTITIONER_BRIEFING: Quick design guidance for professionals
- LITERATURE_REVIEW: Academic synthesis for papers
- SYSTEMATIC_REVIEW: PRISMA-compatible meta-analysis
- PRESENTATION: Slides and visual summaries
- DATA_PIPELINE: Machine-readable for automation
- TEACHING_MATERIALS: Educational resources
- GRANT_WRITING: Research funding proposals
- POLICY_BRIEF: Evidence synthesis for policymakers

Created: 2026-02-09
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


# =============================================================================
# EXPORT PURPOSE DEFINITIONS
# =============================================================================


class ExportPurpose(Enum):
    """
    Purpose-driven export categories following Munzner's nested model.

    Each purpose defines:
    - Target audience (domain situation)
    - Primary tasks (task abstraction)
    - Required content types
    - Optimal formats
    """
    # Quick guidance for design practitioners
    PRACTITIONER_BRIEFING = "practitioner_briefing"

    # Academic synthesis for research papers
    LITERATURE_REVIEW = "literature_review"

    # PRISMA-compatible systematic review
    SYSTEMATIC_REVIEW = "systematic_review"

    # Presentation slides and visuals
    PRESENTATION = "presentation"

    # Machine-readable for data pipelines
    DATA_PIPELINE = "data_pipeline"

    # Educational resources for teaching
    TEACHING_MATERIALS = "teaching_materials"

    # Grant writing and funding proposals
    GRANT_WRITING = "grant_writing"

    # Policy briefs for decision-makers
    POLICY_BRIEF = "policy_brief"


@dataclass
class PurposeProfile:
    """
    Profile defining characteristics of an export purpose.
    Based on Munzner's domain situation analysis.
    """
    purpose: ExportPurpose
    name: str
    description: str

    # Target audience
    primary_audience: str
    expertise_level: str  # novice, intermediate, expert
    time_available: str  # minutes, hours, days

    # Primary tasks
    primary_tasks: List[str]

    # Content requirements
    required_content: List[str]
    optional_content: List[str]
    excluded_content: List[str]

    # Format preferences
    primary_formats: List[str]
    secondary_formats: List[str]

    # Detail level (1-5)
    detail_level: int

    # Include technical details
    include_statistics: bool
    include_methodology: bool
    include_limitations: bool
    include_citations: bool


# Define profiles for each purpose
PURPOSE_PROFILES: Dict[ExportPurpose, PurposeProfile] = {
    ExportPurpose.PRACTITIONER_BRIEFING: PurposeProfile(
        purpose=ExportPurpose.PRACTITIONER_BRIEFING,
        name="Practitioner Briefing",
        description="Quick evidence-based guidance for design professionals",
        primary_audience="Architects, designers, facility managers",
        expertise_level="intermediate",
        time_available="minutes",
        primary_tasks=[
            "Get design recommendations",
            "Understand evidence strength",
            "Identify applicable contexts"
        ],
        required_content=["key_findings", "recommendations", "confidence_levels"],
        optional_content=["scope_conditions", "examples"],
        excluded_content=["raw_statistics", "methodology_details", "full_citations"],
        primary_formats=["markdown", "html"],
        secondary_formats=["pdf"],
        detail_level=2,
        include_statistics=False,
        include_methodology=False,
        include_limitations=True,
        include_citations=False
    ),

    ExportPurpose.LITERATURE_REVIEW: PurposeProfile(
        purpose=ExportPurpose.LITERATURE_REVIEW,
        name="Literature Review",
        description="Comprehensive academic synthesis for research papers",
        primary_audience="Researchers, academics, graduate students",
        expertise_level="expert",
        time_available="hours",
        primary_tasks=[
            "Synthesize evidence",
            "Identify gaps",
            "Support claims with citations"
        ],
        required_content=[
            "evidence_synthesis", "citations", "methodology_summary",
            "scope_conditions", "gaps_identified"
        ],
        optional_content=["statistics", "visualizations"],
        excluded_content=[],
        primary_formats=["markdown", "bibtex"],
        secondary_formats=["json", "docx"],
        detail_level=5,
        include_statistics=True,
        include_methodology=True,
        include_limitations=True,
        include_citations=True
    ),

    ExportPurpose.SYSTEMATIC_REVIEW: PurposeProfile(
        purpose=ExportPurpose.SYSTEMATIC_REVIEW,
        name="Systematic Review",
        description="PRISMA-compatible meta-analysis documentation",
        primary_audience="Systematic reviewers, meta-analysts",
        expertise_level="expert",
        time_available="days",
        primary_tasks=[
            "Document search strategy",
            "Extract study data",
            "Assess quality",
            "Synthesize quantitatively"
        ],
        required_content=[
            "study_table", "quality_assessment", "effect_sizes",
            "forest_plot_data", "prisma_checklist", "full_citations"
        ],
        optional_content=["funnel_plot_data", "subgroup_analyses"],
        excluded_content=[],
        primary_formats=["json", "csv", "bibtex"],
        secondary_formats=["markdown", "html"],
        detail_level=5,
        include_statistics=True,
        include_methodology=True,
        include_limitations=True,
        include_citations=True
    ),

    ExportPurpose.PRESENTATION: PurposeProfile(
        purpose=ExportPurpose.PRESENTATION,
        name="Presentation",
        description="Visual summaries for talks and meetings",
        primary_audience="Speakers, meeting attendees",
        expertise_level="intermediate",
        time_available="minutes",
        primary_tasks=[
            "Communicate key findings",
            "Show evidence visually",
            "Engage audience"
        ],
        required_content=["key_findings", "visuals", "talking_points"],
        optional_content=["supporting_data", "citations"],
        excluded_content=["raw_data", "methodology_details"],
        primary_formats=["html", "markdown"],
        secondary_formats=["pdf"],
        detail_level=2,
        include_statistics=False,
        include_methodology=False,
        include_limitations=True,
        include_citations=False
    ),

    ExportPurpose.DATA_PIPELINE: PurposeProfile(
        purpose=ExportPurpose.DATA_PIPELINE,
        name="Data Pipeline",
        description="Machine-readable formats for automation and integration",
        primary_audience="Engineers, data scientists, systems",
        expertise_level="expert",
        time_available="automated",
        primary_tasks=[
            "Ingest data programmatically",
            "Process beliefs",
            "Integrate with other systems"
        ],
        required_content=["structured_data", "schema_info", "manifest"],
        optional_content=["validation_report"],
        excluded_content=["formatted_text", "visuals"],
        primary_formats=["jsonl", "json", "csv"],
        secondary_formats=["parquet"],
        detail_level=5,
        include_statistics=True,
        include_methodology=True,
        include_limitations=True,
        include_citations=True
    ),

    ExportPurpose.TEACHING_MATERIALS: PurposeProfile(
        purpose=ExportPurpose.TEACHING_MATERIALS,
        name="Teaching Materials",
        description="Educational resources for courses and workshops",
        primary_audience="Instructors, students",
        expertise_level="novice",
        time_available="hours",
        primary_tasks=[
            "Learn concepts",
            "Understand examples",
            "Apply knowledge"
        ],
        required_content=[
            "key_concepts", "examples", "exercises",
            "glossary", "discussion_questions"
        ],
        optional_content=["case_studies", "citations"],
        excluded_content=["raw_statistics"],
        primary_formats=["markdown", "html"],
        secondary_formats=["pdf", "docx"],
        detail_level=3,
        include_statistics=False,
        include_methodology=True,
        include_limitations=True,
        include_citations=False
    ),

    ExportPurpose.GRANT_WRITING: PurposeProfile(
        purpose=ExportPurpose.GRANT_WRITING,
        name="Grant Writing",
        description="Evidence summaries for research funding proposals",
        primary_audience="Grant applicants, reviewers",
        expertise_level="expert",
        time_available="hours",
        primary_tasks=[
            "Justify research need",
            "Demonstrate expertise",
            "Show evidence gaps"
        ],
        required_content=[
            "evidence_gaps", "research_significance",
            "preliminary_findings", "citations"
        ],
        optional_content=["statistics", "visualizations"],
        excluded_content=["raw_data"],
        primary_formats=["markdown", "docx"],
        secondary_formats=["bibtex"],
        detail_level=4,
        include_statistics=True,
        include_methodology=True,
        include_limitations=True,
        include_citations=True
    ),

    ExportPurpose.POLICY_BRIEF: PurposeProfile(
        purpose=ExportPurpose.POLICY_BRIEF,
        name="Policy Brief",
        description="Evidence synthesis for policymakers and stakeholders",
        primary_audience="Policymakers, government officials, NGOs",
        expertise_level="intermediate",
        time_available="minutes",
        primary_tasks=[
            "Understand evidence",
            "Make decisions",
            "Communicate to others"
        ],
        required_content=[
            "executive_summary", "key_recommendations",
            "evidence_strength", "implementation_considerations"
        ],
        optional_content=["cost_considerations", "stakeholder_impacts"],
        excluded_content=["technical_details", "raw_statistics"],
        primary_formats=["markdown", "pdf"],
        secondary_formats=["html"],
        detail_level=2,
        include_statistics=False,
        include_methodology=False,
        include_limitations=True,
        include_citations=False
    ),
}


# =============================================================================
# BUNDLE CONTENT GENERATORS
# =============================================================================


@dataclass
class BundleFile:
    """A single file in an export bundle."""
    filename: str
    content: str
    format: str
    description: str
    is_primary: bool = True


@dataclass
class ExportBundle:
    """A complete export bundle for a specific purpose."""
    purpose: ExportPurpose
    topic: str
    generated_at: str
    files: List[BundleFile]
    manifest: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "purpose": self.purpose.value,
            "topic": self.topic,
            "generated_at": self.generated_at,
            "file_count": len(self.files),
            "files": [
                {
                    "filename": f.filename,
                    "format": f.format,
                    "description": f.description,
                    "is_primary": f.is_primary,
                    "size_bytes": len(f.content.encode("utf-8"))
                }
                for f in self.files
            ],
            "manifest": self.manifest,
            "warnings": self.warnings
        }

    def write_to_directory(self, output_dir: Path) -> List[Path]:
        """Write all bundle files to a directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        written = []

        for file in self.files:
            path = output_dir / file.filename
            path.write_text(file.content, encoding="utf-8")
            written.append(path)

        # Write manifest
        manifest_path = output_dir / "MANIFEST.json"
        manifest_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        written.append(manifest_path)

        return written


class ContentGenerator:
    """
    Generates content components for export bundles.
    Each method produces a specific type of content.
    """

    def __init__(self):
        self._cache = {}

    def generate_executive_summary(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        max_findings: int = 5
    ) -> str:
        """Generate a brief executive summary."""
        # Sort by credence
        sorted_beliefs = sorted(
            beliefs,
            key=lambda b: b.get("credence", 0),
            reverse=True
        )

        lines = [
            f"# Executive Summary: {topic}",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*",
            "",
            "## Key Findings",
            ""
        ]

        for i, belief in enumerate(sorted_beliefs[:max_findings], 1):
            credence = belief.get("credence", 0)
            content = belief.get("content", "")
            confidence = self._credence_to_label(credence)
            lines.append(f"{i}. {content} *({confidence} confidence)*")

        lines.extend([
            "",
            "## Evidence Strength",
            "",
            f"Based on {len(beliefs)} evidence items from {self._count_sources(beliefs)} sources.",
            ""
        ])

        # Add overall assessment
        avg_credence = sum(b.get("credence", 0) for b in beliefs) / len(beliefs) if beliefs else 0
        lines.append(f"Overall evidence quality: **{self._credence_to_label(avg_credence)}**")

        return "\n".join(lines)

    def generate_key_recommendations(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate actionable recommendations."""
        lines = [
            f"# Key Recommendations: {topic}",
            "",
        ]

        # Filter for high-credence empirical beliefs
        actionable = [
            b for b in beliefs
            if b.get("credence", 0) >= 0.6 and b.get("level") == "EMPIRICAL"
        ]

        if not actionable:
            lines.append("*Insufficient high-confidence evidence for specific recommendations.*")
            return "\n".join(lines)

        for i, belief in enumerate(actionable[:7], 1):
            content = belief.get("content", "")
            # Convert to recommendation format
            recommendation = self._to_recommendation(content)
            lines.append(f"{i}. {recommendation}")

        return "\n".join(lines)

    def generate_evidence_synthesis(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        include_citations: bool = True
    ) -> str:
        """Generate narrative evidence synthesis."""
        lines = [
            f"# Evidence Synthesis: {topic}",
            "",
        ]

        # Group by theory/theme
        by_theory = self._group_by_theory(beliefs)

        for theory, theory_beliefs in by_theory.items():
            lines.append(f"## {theory or 'General Findings'}")
            lines.append("")

            # Sort by credence
            sorted_beliefs = sorted(
                theory_beliefs,
                key=lambda b: b.get("credence", 0),
                reverse=True
            )

            for belief in sorted_beliefs:
                content = belief.get("content", "")
                credence = belief.get("credence", 0)
                sources = belief.get("sources", [])

                if include_citations and sources:
                    citation = f" ({', '.join(sources[:3])})"
                else:
                    citation = ""

                lines.append(f"- {content}{citation} *[{credence:.2f}]*")

            lines.append("")

        return "\n".join(lines)

    def generate_study_table(
        self,
        sources: List[Dict[str, Any]],
        format: str = "markdown"
    ) -> str:
        """Generate structured study characteristics table."""
        if format == "csv":
            return self._study_table_csv(sources)
        else:
            return self._study_table_markdown(sources)

    def _study_table_markdown(self, sources: List[Dict[str, Any]]) -> str:
        """Generate Markdown study table."""
        lines = [
            "# Study Characteristics",
            "",
            "| Citation | Year | Type | N | Key Finding |",
            "|----------|------|------|---|-------------|"
        ]

        for source in sources:
            citation = self._format_citation(source)
            year = source.get("year", "—")
            study_type = source.get("study_type", "—")
            n = source.get("sample_size", "—")
            finding = source.get("key_finding", "—")[:50]
            lines.append(f"| {citation} | {year} | {study_type} | {n} | {finding}... |")

        return "\n".join(lines)

    def _study_table_csv(self, sources: List[Dict[str, Any]]) -> str:
        """Generate CSV study table."""
        lines = ["citation,year,study_type,sample_size,key_finding"]

        for source in sources:
            citation = self._format_citation(source).replace('"', '""')
            year = source.get("year", "")
            study_type = source.get("study_type", "")
            n = source.get("sample_size", "")
            finding = source.get("key_finding", "").replace('"', '""')
            lines.append(f'"{citation}",{year},"{study_type}",{n},"{finding}"')

        return "\n".join(lines)

    def generate_prisma_checklist(
        self,
        beliefs: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> str:
        """Generate PRISMA checklist for systematic reviews."""
        lines = [
            "# PRISMA Checklist",
            "",
            "## Identification",
            f"- [ ] Total records identified: {len(sources)}",
            "",
            "## Screening",
            f"- [ ] Records screened: {len(sources)}",
            f"- [ ] Records excluded: 0",
            "",
            "## Eligibility",
            f"- [ ] Full-text articles assessed: {len(sources)}",
            "",
            "## Inclusion",
            f"- [ ] Studies included in synthesis: {len(sources)}",
            f"- [ ] Beliefs extracted: {len(beliefs)}",
            "",
            "## Quality Assessment",
            "- [ ] Risk of bias assessment completed",
            "- [ ] GRADE assessment completed",
            "",
            "## Synthesis",
            "- [ ] Narrative synthesis completed",
            "- [ ] Quantitative synthesis (if applicable)",
            "",
        ]

        return "\n".join(lines)

    def generate_teaching_content(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate educational content."""
        lines = [
            f"# Teaching Module: {topic}",
            "",
            "## Learning Objectives",
            "",
            "After this module, students will be able to:",
            "",
            "1. Explain the key findings in this domain",
            "2. Evaluate the strength of evidence",
            "3. Apply findings to practical scenarios",
            "",
            "## Key Concepts",
            "",
        ]

        # Extract concepts from high-credence beliefs
        concepts = self._extract_concepts(beliefs)
        for concept in concepts[:5]:
            lines.append(f"### {concept['name']}")
            lines.append("")
            lines.append(concept["description"])
            lines.append("")

        lines.extend([
            "## Discussion Questions",
            "",
            f"1. What factors might influence the applicability of {topic} findings?",
            "2. How would you design a study to test these findings?",
            "3. What are the practical implications for your field?",
            "",
            "## Exercise",
            "",
            f"Design a brief intervention based on the {topic} evidence presented.",
            "Consider scope conditions and implementation challenges.",
            "",
        ])

        return "\n".join(lines)

    def generate_grant_justification(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate content for grant writing."""
        lines = [
            f"# Research Justification: {topic}",
            "",
            "## Significance",
            "",
            f"Research on {topic} is significant because:",
            "",
        ]

        # Add significance points from high-credence beliefs
        significant = [b for b in beliefs if b.get("credence", 0) >= 0.7]
        for belief in significant[:3]:
            lines.append(f"- {belief.get('content', '')}")

        lines.extend([
            "",
            "## Evidence Gaps",
            "",
            "Current literature reveals the following gaps:",
            "",
        ])

        # Identify gaps from low-credence or stub beliefs
        gaps = [b for b in beliefs if b.get("status") in ["STUB", "CONTESTED"]]
        for gap in gaps[:3]:
            lines.append(f"- {gap.get('content', '')} (limited evidence)")

        lines.extend([
            "",
            "## Research Need",
            "",
            f"Further research on {topic} is needed to:",
            "",
            "1. Replicate findings in diverse populations",
            "2. Identify moderating factors",
            "3. Develop practical interventions",
            "",
        ])

        return "\n".join(lines)

    def generate_policy_implications(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate policy brief content."""
        lines = [
            f"# Policy Brief: {topic}",
            "",
            "## The Issue",
            "",
            f"Evidence synthesis regarding {topic} reveals important considerations for policy.",
            "",
            "## What the Evidence Shows",
            "",
        ]

        # High-confidence findings
        high_conf = [b for b in beliefs if b.get("credence", 0) >= 0.75]
        for belief in high_conf[:3]:
            lines.append(f"**Strong evidence**: {belief.get('content', '')}")
            lines.append("")

        lines.extend([
            "## Policy Recommendations",
            "",
        ])

        # Convert findings to recommendations
        for i, belief in enumerate(high_conf[:5], 1):
            rec = self._to_policy_recommendation(belief.get("content", ""))
            lines.append(f"{i}. {rec}")

        lines.extend([
            "",
            "## Implementation Considerations",
            "",
            "- Context-specific adaptation may be required",
            "- Stakeholder engagement is essential",
            "- Monitoring and evaluation should be planned",
            "",
            "## Confidence Assessment",
            "",
        ])

        avg_credence = sum(b.get("credence", 0) for b in beliefs) / len(beliefs) if beliefs else 0
        lines.append(f"Overall evidence confidence: **{self._credence_to_label(avg_credence)}**")

        return "\n".join(lines)

    # Helper methods

    def _credence_to_label(self, credence: float) -> str:
        """Convert credence score to human-readable label."""
        if credence >= 0.85:
            return "Very High"
        elif credence >= 0.70:
            return "High"
        elif credence >= 0.50:
            return "Moderate"
        elif credence >= 0.30:
            return "Low"
        else:
            return "Very Low"

    def _count_sources(self, beliefs: List[Dict[str, Any]]) -> int:
        """Count unique sources across beliefs."""
        sources = set()
        for belief in beliefs:
            for source in belief.get("sources", []):
                sources.add(source)
        return len(sources)

    def _to_recommendation(self, content: str) -> str:
        """Convert finding to recommendation format."""
        # Simple conversion - could be more sophisticated
        content = content.strip()
        if content.lower().startswith("people "):
            return "Consider that " + content.lower()
        elif content.lower().startswith("exposure to"):
            return "Consider implementing " + content.lower()
        else:
            return f"Consider: {content}"

    def _to_policy_recommendation(self, content: str) -> str:
        """Convert finding to policy recommendation."""
        content = content.strip()
        return f"Policies should consider that {content.lower()}"

    def _group_by_theory(
        self,
        beliefs: List[Dict[str, Any]]
    ) -> Dict[Optional[str], List[Dict[str, Any]]]:
        """Group beliefs by theory."""
        by_theory: Dict[Optional[str], List[Dict[str, Any]]] = {}
        for belief in beliefs:
            theory = belief.get("theory")
            if theory not in by_theory:
                by_theory[theory] = []
            by_theory[theory].append(belief)
        return by_theory

    def _format_citation(self, source: Dict[str, Any]) -> str:
        """Format a source as a brief citation."""
        authors = source.get("authors", [])
        year = source.get("year", "n.d.")

        if not authors:
            return f"({year})"

        first_author = authors[0].split()[-1] if authors else "Unknown"
        if len(authors) > 2:
            return f"{first_author} et al. ({year})"
        elif len(authors) == 2:
            second_author = authors[1].split()[-1]
            return f"{first_author} & {second_author} ({year})"
        else:
            return f"{first_author} ({year})"

    def _extract_concepts(
        self,
        beliefs: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract key concepts from beliefs for teaching."""
        concepts = []
        seen = set()

        for belief in sorted(beliefs, key=lambda b: b.get("credence", 0), reverse=True):
            content = belief.get("content", "")
            # Simple concept extraction - first few words
            words = content.split()[:3]
            concept_name = " ".join(words).title()

            if concept_name not in seen:
                seen.add(concept_name)
                concepts.append({
                    "name": concept_name,
                    "description": content
                })

        return concepts


# =============================================================================
# BUNDLE GENERATOR
# =============================================================================


class PurposeDrivenBundleGenerator:
    """
    Main generator for purpose-driven export bundles.

    Following Munzner's nested model:
    1. Domain situation → Purpose profiles
    2. Task abstraction → Content requirements
    3. Visual encoding → Format selection
    4. Algorithm → Efficient generation
    """

    def __init__(self):
        self.content_gen = ContentGenerator()
        self.profiles = PURPOSE_PROFILES

    def generate(
        self,
        purpose: ExportPurpose,
        topic: str,
        beliefs: List[Dict[str, Any]],
        sources: Optional[List[Dict[str, Any]]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ExportBundle:
        """
        Generate a complete export bundle for the given purpose.

        Args:
            purpose: The export purpose
            topic: Topic/query string
            beliefs: List of belief dictionaries
            sources: Optional list of source paper dictionaries
            additional_data: Optional additional data for specific purposes

        Returns:
            ExportBundle with all generated files
        """
        profile = self.profiles[purpose]
        sources = sources or []
        additional_data = additional_data or {}

        generated_at = datetime.now(timezone.utc).isoformat()
        files: List[BundleFile] = []
        warnings: List[str] = []

        # Generate content based on purpose
        if purpose == ExportPurpose.PRACTITIONER_BRIEFING:
            files.extend(self._generate_practitioner_bundle(topic, beliefs, profile))

        elif purpose == ExportPurpose.LITERATURE_REVIEW:
            files.extend(self._generate_literature_bundle(topic, beliefs, sources, profile))

        elif purpose == ExportPurpose.SYSTEMATIC_REVIEW:
            files.extend(self._generate_systematic_bundle(topic, beliefs, sources, profile))

        elif purpose == ExportPurpose.PRESENTATION:
            files.extend(self._generate_presentation_bundle(topic, beliefs, profile))

        elif purpose == ExportPurpose.DATA_PIPELINE:
            files.extend(self._generate_pipeline_bundle(topic, beliefs, sources, profile))

        elif purpose == ExportPurpose.TEACHING_MATERIALS:
            files.extend(self._generate_teaching_bundle(topic, beliefs, profile))

        elif purpose == ExportPurpose.GRANT_WRITING:
            files.extend(self._generate_grant_bundle(topic, beliefs, sources, profile))

        elif purpose == ExportPurpose.POLICY_BRIEF:
            files.extend(self._generate_policy_bundle(topic, beliefs, profile))

        else:
            warnings.append(f"Unknown purpose: {purpose}, using default bundle")
            files.append(BundleFile(
                filename="summary.md",
                content=self.content_gen.generate_evidence_synthesis(topic, beliefs),
                format="markdown",
                description="Evidence synthesis"
            ))

        # Validate bundle
        validation_warnings = self._validate_bundle(files, profile)
        warnings.extend(validation_warnings)

        # Build manifest
        manifest = {
            "purpose": purpose.value,
            "profile": profile.name,
            "topic": topic,
            "belief_count": len(beliefs),
            "source_count": len(sources),
            "file_count": len(files),
            "primary_files": [f.filename for f in files if f.is_primary],
            "generated_at": generated_at,
            "schema_version": "1.0"
        }

        return ExportBundle(
            purpose=purpose,
            topic=topic,
            generated_at=generated_at,
            files=files,
            manifest=manifest,
            warnings=warnings
        )

    def _generate_practitioner_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate practitioner briefing bundle."""
        files = []

        # Executive summary (primary)
        files.append(BundleFile(
            filename="summary.md",
            content=self.content_gen.generate_executive_summary(topic, beliefs),
            format="markdown",
            description="Executive summary with key findings",
            is_primary=True
        ))

        # Recommendations
        files.append(BundleFile(
            filename="recommendations.md",
            content=self.content_gen.generate_key_recommendations(topic, beliefs),
            format="markdown",
            description="Actionable recommendations",
            is_primary=True
        ))

        # Quick reference (optional)
        quick_ref = self._generate_quick_reference(topic, beliefs)
        files.append(BundleFile(
            filename="quick_reference.md",
            content=quick_ref,
            format="markdown",
            description="One-page quick reference",
            is_primary=False
        ))

        return files

    def _generate_literature_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate literature review bundle."""
        files = []

        # Evidence synthesis (primary)
        files.append(BundleFile(
            filename="synthesis.md",
            content=self.content_gen.generate_evidence_synthesis(topic, beliefs, include_citations=True),
            format="markdown",
            description="Narrative evidence synthesis",
            is_primary=True
        ))

        # BibTeX references
        bibtex = self._generate_bibtex(sources)
        files.append(BundleFile(
            filename="references.bib",
            content=bibtex,
            format="bibtex",
            description="BibTeX citations",
            is_primary=True
        ))

        # Beliefs JSON
        files.append(BundleFile(
            filename="beliefs.json",
            content=json.dumps(beliefs, indent=2, ensure_ascii=False),
            format="json",
            description="All extracted beliefs",
            is_primary=False
        ))

        # Study table
        files.append(BundleFile(
            filename="study_table.md",
            content=self.content_gen.generate_study_table(sources, "markdown"),
            format="markdown",
            description="Study characteristics table",
            is_primary=False
        ))

        return files

    def _generate_systematic_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate systematic review bundle."""
        files = []

        # Evidence summary JSON
        summary = {
            "topic": topic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "belief_count": len(beliefs),
            "source_count": len(sources),
            "beliefs": beliefs,
            "sources": sources
        }
        files.append(BundleFile(
            filename="evidence_summary.json",
            content=json.dumps(summary, indent=2, ensure_ascii=False),
            format="json",
            description="Complete evidence summary",
            is_primary=True
        ))

        # BibTeX
        files.append(BundleFile(
            filename="references.bib",
            content=self._generate_bibtex(sources),
            format="bibtex",
            description="BibTeX citations",
            is_primary=True
        ))

        # JSONL formats
        files.append(BundleFile(
            filename="beliefs.jsonl",
            content="\n".join(json.dumps(b) for b in beliefs),
            format="jsonl",
            description="Beliefs in JSONL format",
            is_primary=True
        ))

        files.append(BundleFile(
            filename="sources.jsonl",
            content="\n".join(json.dumps(s) for s in sources),
            format="jsonl",
            description="Sources in JSONL format",
            is_primary=True
        ))

        # CSV study table
        files.append(BundleFile(
            filename="study_table.csv",
            content=self.content_gen.generate_study_table(sources, "csv"),
            format="csv",
            description="Study characteristics (CSV)",
            is_primary=False
        ))

        # PRISMA checklist
        files.append(BundleFile(
            filename="prisma_checklist.md",
            content=self.content_gen.generate_prisma_checklist(beliefs, sources),
            format="markdown",
            description="PRISMA checklist",
            is_primary=False
        ))

        return files

    def _generate_presentation_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate presentation bundle."""
        files = []

        # Talking points
        files.append(BundleFile(
            filename="talking_points.md",
            content=self.content_gen.generate_executive_summary(topic, beliefs, max_findings=7),
            format="markdown",
            description="Key talking points",
            is_primary=True
        ))

        # Visual summary HTML
        visual = self._generate_visual_summary(topic, beliefs)
        files.append(BundleFile(
            filename="visual_summary.html",
            content=visual,
            format="html",
            description="Visual summary for slides",
            is_primary=True
        ))

        # Speaker notes
        notes = self._generate_speaker_notes(topic, beliefs)
        files.append(BundleFile(
            filename="speaker_notes.md",
            content=notes,
            format="markdown",
            description="Detailed speaker notes",
            is_primary=False
        ))

        return files

    def _generate_pipeline_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate data pipeline bundle."""
        files = []

        # Beliefs JSONL
        files.append(BundleFile(
            filename="beliefs.jsonl",
            content="\n".join(json.dumps(b) for b in beliefs),
            format="jsonl",
            description="Beliefs in JSONL format",
            is_primary=True
        ))

        # Sources JSONL
        files.append(BundleFile(
            filename="sources.jsonl",
            content="\n".join(json.dumps(s) for s in sources),
            format="jsonl",
            description="Sources in JSONL format",
            is_primary=True
        ))

        # Schema info
        schema = {
            "schema_version": "1.0",
            "belief_schema": {
                "id": "string",
                "content": "string",
                "credence": "float",
                "uncertainty": "float",
                "status": "string",
                "level": "string",
                "theory": "string|null",
                "sources": "array<string>",
                "constraints": "array<string>"
            },
            "source_schema": {
                "paper_id": "string",
                "title": "string",
                "authors": "array<string>",
                "year": "int",
                "doi": "string|null"
            }
        }
        files.append(BundleFile(
            filename="schema.json",
            content=json.dumps(schema, indent=2),
            format="json",
            description="Data schema definitions",
            is_primary=True
        ))

        # Manifest
        manifest = {
            "topic": topic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "belief_count": len(beliefs),
            "source_count": len(sources),
            "format_version": "1.0",
            "files": ["beliefs.jsonl", "sources.jsonl", "schema.json"]
        }
        files.append(BundleFile(
            filename="pipeline_manifest.json",
            content=json.dumps(manifest, indent=2),
            format="json",
            description="Pipeline manifest",
            is_primary=True
        ))

        return files

    def _generate_teaching_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate teaching materials bundle."""
        files = []

        # Module content
        files.append(BundleFile(
            filename="module.md",
            content=self.content_gen.generate_teaching_content(topic, beliefs),
            format="markdown",
            description="Teaching module content",
            is_primary=True
        ))

        # Summary handout
        files.append(BundleFile(
            filename="handout.md",
            content=self.content_gen.generate_executive_summary(topic, beliefs),
            format="markdown",
            description="Student handout",
            is_primary=True
        ))

        # Discussion guide
        discussion = self._generate_discussion_guide(topic, beliefs)
        files.append(BundleFile(
            filename="discussion_guide.md",
            content=discussion,
            format="markdown",
            description="Discussion guide for instructors",
            is_primary=False
        ))

        return files

    def _generate_grant_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        sources: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate grant writing bundle."""
        files = []

        # Research justification
        files.append(BundleFile(
            filename="justification.md",
            content=self.content_gen.generate_grant_justification(topic, beliefs),
            format="markdown",
            description="Research justification",
            is_primary=True
        ))

        # Evidence synthesis
        files.append(BundleFile(
            filename="evidence_review.md",
            content=self.content_gen.generate_evidence_synthesis(topic, beliefs, include_citations=True),
            format="markdown",
            description="Literature review for grant",
            is_primary=True
        ))

        # BibTeX
        files.append(BundleFile(
            filename="references.bib",
            content=self._generate_bibtex(sources),
            format="bibtex",
            description="BibTeX citations",
            is_primary=False
        ))

        return files

    def _generate_policy_bundle(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]],
        profile: PurposeProfile
    ) -> List[BundleFile]:
        """Generate policy brief bundle."""
        files = []

        # Policy brief
        files.append(BundleFile(
            filename="policy_brief.md",
            content=self.content_gen.generate_policy_implications(topic, beliefs),
            format="markdown",
            description="Policy brief",
            is_primary=True
        ))

        # Executive summary
        files.append(BundleFile(
            filename="executive_summary.md",
            content=self.content_gen.generate_executive_summary(topic, beliefs, max_findings=3),
            format="markdown",
            description="One-page executive summary",
            is_primary=True
        ))

        # Recommendations
        files.append(BundleFile(
            filename="recommendations.md",
            content=self.content_gen.generate_key_recommendations(topic, beliefs),
            format="markdown",
            description="Policy recommendations",
            is_primary=False
        ))

        return files

    # Helper methods

    def _generate_bibtex(self, sources: List[Dict[str, Any]]) -> str:
        """Generate BibTeX from sources."""
        # Import the bibtex_generator we just created
        try:
            from src.services.bibtex_generator import export_papers_to_bibtex
            return export_papers_to_bibtex(sources)
        except ImportError:
            # Fallback simple generation
            entries = []
            for source in sources:
                authors = source.get("authors", [])
                year = source.get("year", "")
                first_author = authors[0].split()[-1].lower() if authors else "unknown"
                cite_key = f"{first_author}{year}"

                entry = [f"@article{{{cite_key},"]
                if authors:
                    entry.append(f"  author = {{{' and '.join(authors)}}},")
                entry.append(f"  title = {{{source.get('title', '')}}},")
                if year:
                    entry.append(f"  year = {{{year}}},")
                if source.get("doi"):
                    entry.append(f"  doi = {{{source.get('doi')}}},")
                entry.append("}")
                entries.append("\n".join(entry))

            return "\n\n".join(entries)

    def _generate_quick_reference(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate one-page quick reference."""
        lines = [
            f"# Quick Reference: {topic}",
            "",
            "## At a Glance",
            "",
        ]

        top_beliefs = sorted(beliefs, key=lambda b: b.get("credence", 0), reverse=True)[:5]
        for belief in top_beliefs:
            credence = belief.get("credence", 0)
            icon = "✓" if credence >= 0.7 else "○" if credence >= 0.5 else "?"
            lines.append(f"{icon} {belief.get('content', '')}")

        lines.extend([
            "",
            "## Legend",
            "✓ High confidence | ○ Moderate | ? Limited evidence",
            "",
            f"*Based on {len(beliefs)} evidence items*",
        ])

        return "\n".join(lines)

    def _generate_visual_summary(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate HTML visual summary."""
        top_beliefs = sorted(beliefs, key=lambda b: b.get("credence", 0), reverse=True)[:5]

        findings_html = ""
        for belief in top_beliefs:
            credence = belief.get("credence", 0)
            width = int(credence * 100)
            color = "#85D2A3" if credence >= 0.7 else "#F5D491" if credence >= 0.5 else "#E8A87C"
            findings_html += f"""
            <div class="finding">
                <p>{belief.get('content', '')}</p>
                <div class="bar" style="width: {width}%; background: {color};">{credence:.0%}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Georgia, serif; background: #FFF9F0; color: #4A5568; padding: 40px; }}
                h1 {{ color: #5B8FB9; }}
                .finding {{ margin: 20px 0; }}
                .finding p {{ margin: 5px 0; }}
                .bar {{ height: 24px; border-radius: 4px; color: white; text-align: right; padding-right: 8px; line-height: 24px; }}
            </style>
        </head>
        <body>
            <h1>{topic}</h1>
            <h2>Key Findings</h2>
            {findings_html}
            <p><em>Based on {len(beliefs)} evidence items</em></p>
        </body>
        </html>
        """

    def _generate_speaker_notes(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate speaker notes."""
        lines = [
            f"# Speaker Notes: {topic}",
            "",
            "## Opening (1-2 min)",
            "",
            f"Introduce the topic of {topic} and its relevance.",
            "",
            "## Key Findings (5-7 min)",
            "",
        ]

        top_beliefs = sorted(beliefs, key=lambda b: b.get("credence", 0), reverse=True)[:5]
        for i, belief in enumerate(top_beliefs, 1):
            lines.append(f"### Slide {i+1}")
            lines.append(f"**Finding**: {belief.get('content', '')}")
            lines.append(f"**Confidence**: {belief.get('credence', 0):.0%}")
            lines.append("**Talking points**:")
            lines.append("- Explain the finding")
            lines.append("- Note the evidence strength")
            lines.append("- Connect to practical implications")
            lines.append("")

        lines.extend([
            "## Q&A Preparation",
            "",
            "- Be prepared to discuss methodology",
            "- Know the limitations of the evidence",
            "- Have examples ready",
        ])

        return "\n".join(lines)

    def _generate_discussion_guide(
        self,
        topic: str,
        beliefs: List[Dict[str, Any]]
    ) -> str:
        """Generate discussion guide for teaching."""
        lines = [
            f"# Discussion Guide: {topic}",
            "",
            "## Warm-up Questions",
            "",
            f"1. What do you already know about {topic}?",
            "2. Where have you encountered this in practice?",
            "",
            "## Core Discussion",
            "",
        ]

        for belief in beliefs[:3]:
            content = belief.get("content", "")
            lines.append(f"### Topic: {content[:50]}...")
            lines.append("")
            lines.append("**Questions to raise:**")
            lines.append("- Do you agree with this finding?")
            lines.append("- What evidence would change your mind?")
            lines.append("- How would you apply this?")
            lines.append("")

        lines.extend([
            "## Synthesis Questions",
            "",
            "- What patterns do you see across the findings?",
            "- What questions remain unanswered?",
            "- How would you design follow-up research?",
        ])

        return "\n".join(lines)

    def _validate_bundle(
        self,
        files: List[BundleFile],
        profile: PurposeProfile
    ) -> List[str]:
        """Validate bundle against profile requirements."""
        warnings = []

        # Check for required content
        filenames = {f.filename for f in files}
        file_descriptions = {f.description.lower() for f in files}

        for required in profile.required_content:
            # Check if any file matches the required content type
            if not any(required.lower() in desc for desc in file_descriptions):
                warnings.append(f"Missing required content: {required}")

        # Check primary format coverage
        formats = {f.format for f in files}
        if not any(fmt in profile.primary_formats for fmt in formats):
            warnings.append(f"No files in primary formats: {profile.primary_formats}")

        return warnings


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


_generator: Optional[PurposeDrivenBundleGenerator] = None


def get_bundle_generator() -> PurposeDrivenBundleGenerator:
    """Get or create bundle generator singleton."""
    global _generator
    if _generator is None:
        _generator = PurposeDrivenBundleGenerator()
    return _generator


def generate_bundle(
    purpose: Union[ExportPurpose, str],
    topic: str,
    beliefs: List[Dict[str, Any]],
    sources: Optional[List[Dict[str, Any]]] = None,
    output_dir: Optional[Path] = None
) -> ExportBundle:
    """
    Generate an export bundle for a specific purpose.

    Args:
        purpose: Export purpose (enum or string)
        topic: Topic string
        beliefs: List of belief dictionaries
        sources: Optional list of source dictionaries
        output_dir: Optional directory to write files

    Returns:
        ExportBundle with generated content
    """
    if isinstance(purpose, str):
        purpose = ExportPurpose(purpose)

    generator = get_bundle_generator()
    bundle = generator.generate(purpose, topic, beliefs, sources)

    if output_dir:
        bundle.write_to_directory(output_dir)

    return bundle


def list_purposes() -> List[Dict[str, Any]]:
    """List available export purposes with descriptions."""
    return [
        {
            "purpose": p.value,
            "name": PURPOSE_PROFILES[p].name,
            "description": PURPOSE_PROFILES[p].description,
            "audience": PURPOSE_PROFILES[p].primary_audience,
            "primary_formats": PURPOSE_PROFILES[p].primary_formats
        }
        for p in ExportPurpose
    ]
