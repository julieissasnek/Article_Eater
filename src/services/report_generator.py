"""
Report Generator Service — Sprint 3.0.4-F
2026-02-10

Generates professional reports from evidence queries in PDF and Markdown formats.

Report Types:
- Evidence Summary: Concise summary for practitioners
- Research Brief: Detailed brief for researchers
- Technical Report: Full technical documentation
- Literature Map: Visual overview of the evidence landscape

Expert Panel Guidance:
- Cartwright: Scope conditions must be explicit
- Kaplan: Practitioner implications must be actionable
- Simon: Progressive disclosure (headline → summary → detail)
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime, timezone
from io import BytesIO

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class ReportFormat(Enum):
    """Supported export formats."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class ReportType(Enum):
    """Types of reports that can be generated."""
    EVIDENCE_SUMMARY = "evidence_summary"
    RESEARCH_BRIEF = "research_brief"
    TECHNICAL_REPORT = "technical_report"
    LITERATURE_MAP = "literature_map"
    VERIFICATION_CHECKLIST = "verification_checklist"


class ConfidenceLevel(Enum):
    """Confidence levels for findings."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class EvidenceSource:
    """A source of evidence."""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    doi: Optional[str] = None
    journal: Optional[str] = None
    credence_contribution: float = 0.0
    methodology: Optional[str] = None


@dataclass
class Finding:
    """A research finding to include in the report."""
    belief_id: str
    content: str
    credence: float
    confidence: ConfidenceLevel
    status: str
    level: str
    sources: List[EvidenceSource] = field(default_factory=list)
    scope_population: Optional[str] = None
    scope_setting: Optional[str] = None
    scope_methodology: Optional[str] = None
    scope_limitations: Optional[str] = None
    supporting_theories: List[str] = field(default_factory=list)
    contradicting_findings: List[str] = field(default_factory=list)


@dataclass
class ScopeSection:
    """Scope conditions section."""
    populations: List[str] = field(default_factory=list)
    settings: List[str] = field(default_factory=list)
    methodologies: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    generalization_warnings: List[str] = field(default_factory=list)


@dataclass
class PracticalImplication:
    """A practical implication for practitioners."""
    recommendation: str
    confidence: ConfidenceLevel
    evidence_strength: str
    applicable_when: List[str] = field(default_factory=list)
    not_applicable_when: List[str] = field(default_factory=list)


@dataclass
class ReportSection:
    """A section of the report."""
    title: str
    content: str
    subsections: List['ReportSection'] = field(default_factory=list)
    level: int = 1


@dataclass
class ReportMetadata:
    """Metadata for the report."""
    title: str
    subtitle: Optional[str] = None
    query: Optional[str] = None
    report_type: ReportType = ReportType.EVIDENCE_SUMMARY
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0"
    author: str = "Article Eater V23"
    total_beliefs: int = 0
    total_sources: int = 0
    average_credence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MODERATE


@dataclass
class Report:
    """A complete report."""
    metadata: ReportMetadata
    executive_summary: str
    findings: List[Finding] = field(default_factory=list)
    scope: Optional[ScopeSection] = None
    implications: List[PracticalImplication] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    methodology_notes: Optional[str] = None
    sections: List[ReportSection] = field(default_factory=list)
    references: List[EvidenceSource] = field(default_factory=list)


# =============================================================================
# Report Generator
# =============================================================================

class ReportGenerator:
    """
    Generates professional reports from evidence data.

    Supports multiple report types and output formats.
    """

    def __init__(self):
        self.current_report: Optional[Report] = None

    # =========================================================================
    # Report Building
    # =========================================================================

    def create_report(
        self,
        title: str,
        query: Optional[str] = None,
        report_type: ReportType = ReportType.EVIDENCE_SUMMARY,
        subtitle: Optional[str] = None
    ) -> Report:
        """Create a new report with metadata."""
        metadata = ReportMetadata(
            title=title,
            subtitle=subtitle,
            query=query,
            report_type=report_type
        )

        self.current_report = Report(
            metadata=metadata,
            executive_summary=""
        )

        return self.current_report

    def add_findings(
        self,
        findings: List[Dict[str, Any]],
        report: Optional[Report] = None
    ) -> None:
        """Add findings to the report from belief data."""
        report = report or self.current_report
        if not report:
            raise ValueError("No report to add findings to")

        for finding_data in findings:
            finding = self._parse_finding(finding_data)
            report.findings.append(finding)

        # Update metadata
        report.metadata.total_beliefs = len(report.findings)
        if report.findings:
            credences = [f.credence for f in report.findings]
            report.metadata.average_credence = sum(credences) / len(credences)

            # Determine overall confidence
            avg = report.metadata.average_credence
            if avg >= 0.75:
                report.metadata.confidence_level = ConfidenceLevel.HIGH
            elif avg >= 0.5:
                report.metadata.confidence_level = ConfidenceLevel.MODERATE
            else:
                report.metadata.confidence_level = ConfidenceLevel.LOW

    def _parse_finding(self, data: Dict[str, Any]) -> Finding:
        """Parse finding data into Finding object."""
        credence = data.get("credence", 0.5)
        if isinstance(credence, dict):
            credence = credence.get("point", 0.5)

        # Determine confidence from credence
        if credence >= 0.75:
            confidence = ConfidenceLevel.HIGH
        elif credence >= 0.5:
            confidence = ConfidenceLevel.MODERATE
        else:
            confidence = ConfidenceLevel.LOW

        # Parse sources
        sources = []
        for source_data in data.get("sources", data.get("paper_ids", [])):
            if isinstance(source_data, str):
                sources.append(EvidenceSource(
                    paper_id=source_data,
                    title="",
                    authors=[],
                    year=0
                ))
            elif isinstance(source_data, dict):
                sources.append(EvidenceSource(
                    paper_id=source_data.get("id", ""),
                    title=source_data.get("title", ""),
                    authors=source_data.get("authors", []),
                    year=source_data.get("year", 0),
                    doi=source_data.get("doi"),
                    journal=source_data.get("journal")
                ))

        # Extract scope
        scope = data.get("scope", data.get("scope_conditions", {}))
        if isinstance(scope, dict):
            scope_pop = scope.get("population")
            scope_setting = scope.get("setting")
            scope_method = scope.get("methodology")
            scope_limits = scope.get("limitations")
        else:
            scope_pop = scope_setting = scope_method = scope_limits = None

        return Finding(
            belief_id=data.get("id", data.get("belief_id", "unknown")),
            content=data.get("content", ""),
            credence=credence,
            confidence=confidence,
            status=str(data.get("status", "unknown")).upper(),
            level=str(data.get("level", "empirical")).upper(),
            sources=sources,
            scope_population=scope_pop,
            scope_setting=scope_setting,
            scope_methodology=scope_method,
            scope_limitations=scope_limits,
            supporting_theories=data.get("theory_ids", data.get("theories", [])),
        )

    def add_scope_conditions(
        self,
        scope: Dict[str, Any],
        report: Optional[Report] = None
    ) -> None:
        """Add scope conditions section."""
        report = report or self.current_report
        if not report:
            raise ValueError("No report to add scope to")

        report.scope = ScopeSection(
            populations=scope.get("populations", []),
            settings=scope.get("settings", []),
            methodologies=scope.get("methodologies", []),
            limitations=scope.get("limitations", []),
            generalization_warnings=scope.get("warnings", [])
        )

    def add_implications(
        self,
        implications: List[Dict[str, Any]],
        report: Optional[Report] = None
    ) -> None:
        """Add practical implications."""
        report = report or self.current_report
        if not report:
            raise ValueError("No report to add implications to")

        for impl_data in implications:
            impl = PracticalImplication(
                recommendation=impl_data.get("recommendation", ""),
                confidence=ConfidenceLevel(impl_data.get("confidence", "moderate")),
                evidence_strength=impl_data.get("evidence_strength", "moderate"),
                applicable_when=impl_data.get("applicable_when", []),
                not_applicable_when=impl_data.get("not_applicable_when", [])
            )
            report.implications.append(impl)

    def add_caveats(
        self,
        caveats: List[str],
        report: Optional[Report] = None
    ) -> None:
        """Add caveats and limitations."""
        report = report or self.current_report
        if not report:
            raise ValueError("No report to add caveats to")

        report.caveats.extend(caveats)

    def set_executive_summary(
        self,
        summary: str,
        report: Optional[Report] = None
    ) -> None:
        """Set the executive summary."""
        report = report or self.current_report
        if not report:
            raise ValueError("No report to set summary for")

        report.executive_summary = summary

    def generate_executive_summary(
        self,
        report: Optional[Report] = None
    ) -> str:
        """Auto-generate executive summary from findings."""
        report = report or self.current_report
        if not report:
            return ""

        lines = []

        # Opening
        if report.metadata.query:
            lines.append(f"This report summarizes evidence for the query: *{report.metadata.query}*")
        lines.append("")

        # Key finding
        if report.findings:
            top = max(report.findings, key=lambda f: f.credence)
            lines.append(f"**Key Finding**: {top.content} (credence: {top.credence:.2f})")
            lines.append("")

        # Evidence overview
        lines.append(f"**Evidence Base**: {report.metadata.total_beliefs} beliefs from "
                    f"{report.metadata.total_sources} sources")
        lines.append(f"**Overall Confidence**: {report.metadata.confidence_level.value}")
        lines.append("")

        # Scope warning
        if report.scope and report.scope.generalization_warnings:
            lines.append("**Generalization Warning**: " + report.scope.generalization_warnings[0])

        summary = "\n".join(lines)
        report.executive_summary = summary
        return summary

    # =========================================================================
    # Format Conversion - Markdown
    # =========================================================================

    def to_markdown(
        self,
        report: Optional[Report] = None,
        include_toc: bool = True
    ) -> str:
        """Convert report to Markdown format."""
        report = report or self.current_report
        if not report:
            return "# No Report Data"

        lines = []

        # Title
        lines.append(f"# {report.metadata.title}")
        if report.metadata.subtitle:
            lines.append(f"*{report.metadata.subtitle}*")
        lines.append("")
        lines.append(f"Generated: {report.metadata.generated_at}")
        lines.append(f"Report Type: {report.metadata.report_type.value}")
        lines.append("")

        # Table of Contents
        if include_toc:
            lines.append("## Table of Contents")
            lines.append("1. [Executive Summary](#executive-summary)")
            lines.append("2. [Key Findings](#key-findings)")
            if report.scope:
                lines.append("3. [Scope Conditions](#scope-conditions)")
            if report.implications:
                lines.append("4. [Practical Implications](#practical-implications)")
            if report.caveats:
                lines.append("5. [Caveats and Limitations](#caveats-and-limitations)")
            lines.append("6. [References](#references)")
            lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.executive_summary or "*No summary provided*")
        lines.append("")

        # Key Findings
        lines.append("## Key Findings")
        lines.append("")

        if not report.findings:
            lines.append("*No findings available*")
        else:
            # Sort by credence
            sorted_findings = sorted(report.findings, key=lambda f: f.credence, reverse=True)

            for i, finding in enumerate(sorted_findings, 1):
                lines.append(f"### Finding {i}")
                lines.append("")
                lines.append(f"**{finding.content}**")
                lines.append("")
                lines.append(f"- **Credence**: {finding.credence:.2f}")
                lines.append(f"- **Confidence**: {finding.confidence.value}")
                lines.append(f"- **Status**: {finding.status}")
                lines.append(f"- **Level**: {finding.level}")

                if finding.supporting_theories:
                    lines.append(f"- **Theories**: {', '.join(finding.supporting_theories)}")

                if finding.scope_population:
                    lines.append(f"- **Population**: {finding.scope_population}")
                if finding.scope_setting:
                    lines.append(f"- **Setting**: {finding.scope_setting}")

                if finding.sources:
                    source_refs = [s.paper_id for s in finding.sources[:5]]
                    lines.append(f"- **Sources**: {', '.join(source_refs)}")

                lines.append("")

        # Scope Conditions
        if report.scope:
            lines.append("## Scope Conditions")
            lines.append("")
            lines.append("### Populations Studied")
            for pop in report.scope.populations:
                lines.append(f"- {pop}")
            lines.append("")

            lines.append("### Settings")
            for setting in report.scope.settings:
                lines.append(f"- {setting}")
            lines.append("")

            lines.append("### Methodologies Used")
            for method in report.scope.methodologies:
                lines.append(f"- {method}")
            lines.append("")

            if report.scope.limitations:
                lines.append("### Limitations")
                for limit in report.scope.limitations:
                    lines.append(f"- {limit}")
                lines.append("")

            if report.scope.generalization_warnings:
                lines.append("### Generalization Warnings")
                for warning in report.scope.generalization_warnings:
                    lines.append(f"⚠️ {warning}")
                lines.append("")

        # Practical Implications
        if report.implications:
            lines.append("## Practical Implications")
            lines.append("")

            for impl in report.implications:
                lines.append(f"### {impl.recommendation}")
                lines.append("")
                lines.append(f"**Confidence**: {impl.confidence.value}")
                lines.append(f"**Evidence Strength**: {impl.evidence_strength}")
                lines.append("")

                if impl.applicable_when:
                    lines.append("**Applicable when**:")
                    for cond in impl.applicable_when:
                        lines.append(f"- {cond}")
                    lines.append("")

                if impl.not_applicable_when:
                    lines.append("**Not applicable when**:")
                    for cond in impl.not_applicable_when:
                        lines.append(f"- {cond}")
                    lines.append("")

        # Caveats
        if report.caveats:
            lines.append("## Caveats and Limitations")
            lines.append("")
            for caveat in report.caveats:
                lines.append(f"- {caveat}")
            lines.append("")

        # References
        lines.append("## References")
        lines.append("")

        # Collect all unique sources
        all_sources = []
        seen_ids = set()
        for finding in report.findings:
            for source in finding.sources:
                if source.paper_id not in seen_ids:
                    all_sources.append(source)
                    seen_ids.add(source.paper_id)

        if all_sources:
            for source in sorted(all_sources, key=lambda s: (s.year or 0, s.paper_id)):
                if source.title:
                    ref = f"- {', '.join(source.authors[:3]) if source.authors else 'Unknown'} "
                    ref += f"({source.year}). {source.title}."
                    if source.journal:
                        ref += f" *{source.journal}*."
                    if source.doi:
                        ref += f" https://doi.org/{source.doi}"
                    lines.append(ref)
                else:
                    lines.append(f"- {source.paper_id}")
        else:
            lines.append("*No references available*")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Generated by {report.metadata.author}*")

        return "\n".join(lines)

    # =========================================================================
    # Format Conversion - HTML
    # =========================================================================

    def to_html(
        self,
        report: Optional[Report] = None,
        standalone: bool = True
    ) -> str:
        """Convert report to HTML format."""
        report = report or self.current_report
        if not report:
            return "<html><body><p>No report data</p></body></html>"

        # Use markdown as intermediate and convert
        # For production, would use proper HTML templating
        md_content = self.to_markdown(report, include_toc=False)

        # Simple markdown to HTML conversion
        html_content = self._markdown_to_html(md_content)

        if standalone:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{report.metadata.title}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 10px; }}
        h2 {{ color: #1976D2; margin-top: 30px; }}
        h3 {{ color: #455A64; }}
        .finding {{ background: #F5F5F5; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .credence-high {{ border-left: 4px solid #2E7D32; }}
        .credence-moderate {{ border-left: 4px solid #F57C00; }}
        .credence-low {{ border-left: 4px solid #9E9E9E; }}
        .warning {{ background: #FFF3E0; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .implication {{ background: #E3F2FD; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        ul {{ padding-left: 20px; }}
        code {{ background: #F5F5F5; padding: 2px 6px; border-radius: 4px; }}
        hr {{ border: none; border-top: 1px solid #E0E0E0; margin: 30px 0; }}
        .footer {{ color: #9E9E9E; font-size: 0.9em; text-align: center; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            return html
        else:
            return html_content

    def _markdown_to_html(self, md: str) -> str:
        """Simple markdown to HTML conversion."""
        import re

        html = md

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Wrap consecutive li elements in ul
        html = re.sub(r'(<li>.*?</li>\n)+', lambda m: f'<ul>{m.group(0)}</ul>', html, flags=re.DOTALL)

        # Paragraphs (simple)
        lines = html.split('\n\n')
        processed = []
        for line in lines:
            if not line.strip().startswith('<'):
                processed.append(f'<p>{line}</p>')
            else:
                processed.append(line)
        html = '\n'.join(processed)

        # Horizontal rules
        html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

        return html

    # =========================================================================
    # Format Conversion - PDF
    # =========================================================================

    def to_pdf(
        self,
        report: Optional[Report] = None
    ) -> bytes:
        """
        Convert report to PDF format.
        Requires reportlab library.
        """
        report = report or self.current_report
        if not report:
            return b""

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, ListFlowable, ListItem
            )
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
        except ImportError:
            logger.warning("reportlab not installed. Install with: pip install reportlab")
            return b""

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )

        styles = getSampleStyleSheet()

        # Helper to add or update style
        def add_or_update_style(style):
            if style.name in styles.byName:
                styles.byName[style.name] = style
            else:
                styles.add(style)

        # Custom styles
        add_or_update_style(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Title'],
            textColor=colors.HexColor('#2E7D32'),
            fontSize=24,
            spaceAfter=20
        ))
        add_or_update_style(ParagraphStyle(
            name='ReportSubtitle',
            parent=styles['Normal'],
            textColor=colors.HexColor('#666666'),
            fontSize=12,
            spaceAfter=30
        ))
        add_or_update_style(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading1'],
            textColor=colors.HexColor('#1976D2'),
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10
        ))
        add_or_update_style(ParagraphStyle(
            name='SubsectionHeading',
            parent=styles['Heading2'],
            textColor=colors.HexColor('#455A64'),
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8
        ))
        add_or_update_style(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=8
        ))
        add_or_update_style(ParagraphStyle(
            name='FindingText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=10,
            spaceAfter=4
        ))

        story = []

        # Title
        story.append(Paragraph(report.metadata.title, styles['ReportTitle']))
        if report.metadata.subtitle:
            story.append(Paragraph(report.metadata.subtitle, styles['ReportSubtitle']))

        # Metadata
        meta_text = f"Generated: {report.metadata.generated_at}<br/>"
        meta_text += f"Report Type: {report.metadata.report_type.value}<br/>"
        meta_text += f"Confidence: {report.metadata.confidence_level.value}"
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['SectionHeading']))
        if report.executive_summary:
            # Clean markdown formatting for PDF
            summary = report.executive_summary.replace('**', '').replace('*', '')
            story.append(Paragraph(summary, styles['BodyText']))
        else:
            story.append(Paragraph("No summary provided.", styles['BodyText']))
        story.append(Spacer(1, 15))

        # Key Findings
        story.append(Paragraph("Key Findings", styles['SectionHeading']))

        if report.findings:
            sorted_findings = sorted(report.findings, key=lambda f: f.credence, reverse=True)

            for i, finding in enumerate(sorted_findings[:10], 1):  # Limit to top 10
                story.append(Paragraph(f"Finding {i}", styles['SubsectionHeading']))

                # Finding content
                story.append(Paragraph(finding.content, styles['FindingText']))

                # Metrics table
                metrics_data = [
                    ['Credence', f'{finding.credence:.2f}'],
                    ['Confidence', finding.confidence.value],
                    ['Status', finding.status],
                    ['Level', finding.level],
                ]

                if finding.scope_population:
                    metrics_data.append(['Population', finding.scope_population])
                if finding.scope_setting:
                    metrics_data.append(['Setting', finding.scope_setting])

                table = Table(metrics_data, colWidths=[1.5*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No findings available.", styles['BodyText']))

        # Scope Conditions
        if report.scope:
            story.append(PageBreak())
            story.append(Paragraph("Scope Conditions", styles['SectionHeading']))

            if report.scope.populations:
                story.append(Paragraph("Populations Studied:", styles['SubsectionHeading']))
                for pop in report.scope.populations:
                    story.append(Paragraph(f"• {pop}", styles['FindingText']))

            if report.scope.settings:
                story.append(Paragraph("Settings:", styles['SubsectionHeading']))
                for setting in report.scope.settings:
                    story.append(Paragraph(f"• {setting}", styles['FindingText']))

            if report.scope.generalization_warnings:
                story.append(Paragraph("Generalization Warnings:", styles['SubsectionHeading']))
                for warning in report.scope.generalization_warnings:
                    story.append(Paragraph(f"⚠ {warning}", styles['FindingText']))

        # Practical Implications
        if report.implications:
            story.append(Paragraph("Practical Implications", styles['SectionHeading']))
            for impl in report.implications:
                story.append(Paragraph(impl.recommendation, styles['SubsectionHeading']))
                story.append(Paragraph(
                    f"Confidence: {impl.confidence.value} | Evidence: {impl.evidence_strength}",
                    styles['FindingText']
                ))

        # Caveats
        if report.caveats:
            story.append(Paragraph("Caveats and Limitations", styles['SectionHeading']))
            for caveat in report.caveats:
                story.append(Paragraph(f"• {caveat}", styles['FindingText']))

        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Generated by {report.metadata.author}",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
        ))

        doc.build(story)
        return buffer.getvalue()

    # =========================================================================
    # Format Conversion - JSON
    # =========================================================================

    def to_json(
        self,
        report: Optional[Report] = None,
        indent: int = 2
    ) -> str:
        """Convert report to JSON format."""
        report = report or self.current_report
        if not report:
            return "{}"

        def serialize(obj):
            if hasattr(obj, '__dict__'):
                d = {}
                for k, v in obj.__dict__.items():
                    if isinstance(v, Enum):
                        d[k] = v.value
                    elif isinstance(v, list):
                        d[k] = [serialize(item) for item in v]
                    elif hasattr(v, '__dict__'):
                        d[k] = serialize(v)
                    else:
                        d[k] = v
                return d
            return obj

        data = serialize(report)
        return json.dumps(data, indent=indent, default=str)

    # =========================================================================
    # Export Convenience
    # =========================================================================

    def export(
        self,
        format: ReportFormat,
        report: Optional[Report] = None
    ) -> Union[str, bytes]:
        """Export report in the specified format."""
        if format == ReportFormat.MARKDOWN:
            return self.to_markdown(report)
        elif format == ReportFormat.HTML:
            return self.to_html(report)
        elif format == ReportFormat.PDF:
            return self.to_pdf(report)
        elif format == ReportFormat.JSON:
            return self.to_json(report)
        else:
            raise ValueError(f"Unsupported format: {format}")


# =============================================================================
# Singleton and Convenience Functions
# =============================================================================

_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get or create singleton report generator."""
    global _generator
    if _generator is None:
        _generator = ReportGenerator()
    return _generator


def generate_evidence_report(
    title: str,
    findings: List[Dict[str, Any]],
    query: Optional[str] = None,
    format: ReportFormat = ReportFormat.MARKDOWN,
    scope: Optional[Dict[str, Any]] = None,
    implications: Optional[List[Dict[str, Any]]] = None,
    caveats: Optional[List[str]] = None
) -> Union[str, bytes]:
    """
    Convenience function to generate a complete evidence report.

    Args:
        title: Report title
        findings: List of finding dictionaries
        query: Optional original query
        format: Output format (markdown, html, pdf, json)
        scope: Optional scope conditions
        implications: Optional practical implications
        caveats: Optional caveats list

    Returns:
        Report content in specified format
    """
    generator = ReportGenerator()

    report = generator.create_report(
        title=title,
        query=query,
        report_type=ReportType.EVIDENCE_SUMMARY
    )

    generator.add_findings(findings, report)

    if scope:
        generator.add_scope_conditions(scope, report)

    if implications:
        generator.add_implications(implications, report)

    if caveats:
        generator.add_caveats(caveats, report)

    generator.generate_executive_summary(report)

    return generator.export(format, report)
