"""
Paper triage classifier for Article Eater extraction pipeline (Sprint D Task D.2).

Classifies papers by type to determine which contain extractable empirical findings.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


# Domain keywords for relevance classification
DOMAIN_KEYWORDS = {
    "A1_Materials": [
        "material", "wood", "concrete", "stone", "texture", "surface",
        "finish", "natural materials", "biophilic materials"
    ],
    "A2_Spatial_Scale": [
        "ceiling", "height", "volume", "proportion", "scale", "spacious",
        "room size", "floor area", "spatial"
    ],
    "A3_Spatial_Config": [
        "layout", "wayfinding", "navigation", "circulation", "configuration",
        "space syntax", "integration", "connectivity", "depth"
    ],
    "A4_Light": [
        "light", "daylight", "illuminance", "lux", "lighting", "circadian",
        "window", "glare", "luminance", "natural light"
    ],
    "A5_Acoustic": [
        "noise", "acoustic", "sound", "reverberation", "speech", "auditory",
        "soundscape", "dB", "decibel"
    ],
    "A6_Visual_Form": [
        "color", "colour", "visual", "pattern", "fractal", "curvature",
        "view", "aesthetic", "complexity", "form"
    ],
    "A7_Haptic_Thermal": [
        "thermal", "temperature", "comfort", "haptic", "touch", "tactile",
        "HVAC", "ventilation", "climate"
    ],
    "A8_Social": [
        "social", "privacy", "collaboration", "interaction", "open plan",
        "workspace", "office", "density", "crowding"
    ],
    "A9_Task_Cognition": [
        "cognitive", "attention", "memory", "creativity", "performance",
        "productivity", "concentration", "focus", "task"
    ],
    "A10_Temporal": [
        "temporal", "time", "duration", "exposure", "circadian", "seasonal",
        "dynamic", "variation"
    ],
}

# Article type mappings from CSV to triage categories
ARTICLE_TYPE_MAPPING = {
    # Maps to 'empirical'
    "empirical_v2": "empirical",
    "empirical": "empirical",
    "experiment": "empirical",
    "experimental": "empirical",
    "field_study": "empirical",
    "survey_study": "empirical",
    "interview_study": "empirical",  # May contain qualitative findings
    "phenomenological": "empirical",  # Has qualitative data

    # Maps to 'review'
    "narrative_review": "review",
    "literature_review": "review",
    "systematic_review": "review",
    "scoping_review": "review",

    # Maps to 'meta_analysis'
    "meta_analysis": "meta_analysis",
    "meta-analysis": "meta_analysis",

    # Maps to 'theoretical'
    "theoretical": "theoretical",
    "conceptual_framework": "theoretical",
    "conceptual": "theoretical",
    "thought_piece": "theoretical",
    "perspective": "theoretical",
    "commentary": "theoretical",
    "editorial": "theoretical",

    # Maps to 'methods'
    "methods": "methods",
    "methodological": "methods",
    "protocol": "methods",
    "guidelines": "methods",

    # Maps to 'off_topic'
    "off_topic": "off_topic",

    # Unknown - will classify based on content
    "unknown": "unknown",
    "case_study": "empirical",  # Often has specific findings
}

# Keywords suggesting empirical content
EMPIRICAL_KEYWORDS = [
    r"\bn\s*=\s*\d+",  # Sample size
    r"\bp\s*[<>=]\s*0?\.\d+",  # P-value
    r"participants?",
    r"subjects?",
    r"respondents?",
    r"experiment\d?",
    r"measured",
    r"significant(ly)?",
    r"correlation",
    r"regression",
    r"anova",
    r"t-test",
    r"effect size",
    r"findings? show",
    r"results indicate",
]


@dataclass
class PaperTriage:
    """Triage result for a single paper."""

    paper_id: str
    triage_type: str  # empirical, review, meta_analysis, theoretical, methods, off_topic
    confidence: float
    n_rows: int
    has_tables: bool
    relevant_domains: list[str]
    article_type_family: str
    title: str | None = None
    abstract: str | None = None
    n_table_rows: int = 0
    n_discourse_rows: int = 0
    extractable: bool = False
    priority: int = 0  # Higher = more important to process

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "triage_type": self.triage_type,
            "confidence": self.confidence,
            "n_rows": self.n_rows,
            "has_tables": self.has_tables,
            "relevant_domains": self.relevant_domains,
            "article_type_family": self.article_type_family,
            "title": self.title,
            "abstract": self.abstract,
            "n_table_rows": self.n_table_rows,
            "n_discourse_rows": self.n_discourse_rows,
            "extractable": self.extractable,
            "priority": self.priority,
        }


@dataclass
class TriageResult:
    """Result of triaging all papers."""

    papers: list[PaperTriage]
    triage_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_papers: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    extractable_count: int = 0
    method: str = "rule_based"

    def to_dict(self) -> dict:
        return {
            "triage_date": self.triage_date,
            "method": self.method,
            "total_papers": self.total_papers,
            "by_type": self.by_type,
            "extractable_count": self.extractable_count,
            "papers": [p.to_dict() for p in self.papers],
        }


def _detect_domains(text: str) -> list[str]:
    """Identify relevant architectural domains from text."""
    if not text:
        return []

    text_lower = text.lower()
    domains = []

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                domains.append(domain)
                break

    return domains


def _has_empirical_signals(text: str) -> float:
    """Check if text contains empirical research signals. Returns confidence 0-1."""
    if not text:
        return 0.0

    text_lower = text.lower()
    matches = 0

    for pattern in EMPIRICAL_KEYWORDS:
        if re.search(pattern, text_lower):
            matches += 1

    # Normalize: 3+ matches = high confidence
    return min(1.0, matches / 3.0)


def _classify_paper(
    paper_id: str,
    rows: pd.DataFrame,
    title: str | None = None,
    abstract: str | None = None,
) -> PaperTriage:
    """Classify a single paper based on its data."""

    n_rows = int(len(rows))

    # Get article type from first row
    article_type_family = "unknown"
    if "article_type_family" in rows.columns:
        type_vals = rows["article_type_family"].dropna().unique()
        if len(type_vals) > 0:
            article_type_family = str(type_vals[0]).lower().strip()

    # Count table vs discourse rows
    n_table_rows = 0
    n_discourse_rows = 0
    if "claim_type" in rows.columns:
        claim_types = rows["claim_type"].value_counts()
        # Table rows typically have environment/outcome variables
        has_env = int(rows["environment_variable"].notna().sum())
        has_out = int(rows["outcome_variable"].notna().sum())
        n_table_rows = max(has_env, has_out)
        n_discourse_rows = n_rows - n_table_rows

    has_tables = bool(n_table_rows > 0)

    # Map article type to triage category
    triage_type = ARTICLE_TYPE_MAPPING.get(article_type_family, "unknown")

    # If unknown, try to infer from content
    confidence = 0.7  # Base confidence for mapped types

    if triage_type == "unknown":
        # Check statements for empirical signals
        statements = " ".join(rows["statement"].dropna().astype(str).tolist()[:20])
        combined_text = f"{title or ''} {abstract or ''} {statements}"

        empirical_score = _has_empirical_signals(combined_text)

        if empirical_score > 0.5:
            triage_type = "empirical"
            confidence = 0.5 + empirical_score * 0.3
        elif has_tables and n_table_rows > 5:
            triage_type = "empirical"
            confidence = 0.5
        else:
            triage_type = "theoretical"
            confidence = 0.4

    # Identify relevant domains
    combined_text = f"{title or ''} {abstract or ''}"
    if len(combined_text) < 50:
        # Use first few statements
        statements = " ".join(rows["statement"].dropna().astype(str).tolist()[:5])
        combined_text += " " + statements

    relevant_domains = _detect_domains(combined_text)

    # Determine if extractable
    extractable = bool(triage_type in ("empirical", "review", "meta_analysis") and has_tables)

    # Priority scoring
    priority = 0
    if triage_type == "meta_analysis":
        priority = 100
    elif triage_type == "empirical":
        priority = 80 + min(20, n_table_rows // 5)
    elif triage_type == "review":
        priority = 60 + min(20, n_table_rows // 5)

    if len(relevant_domains) > 0:
        priority += 10 * len(relevant_domains)

    return PaperTriage(
        paper_id=paper_id,
        triage_type=triage_type,
        confidence=round(confidence, 2),
        n_rows=n_rows,
        has_tables=has_tables,
        relevant_domains=relevant_domains,
        article_type_family=article_type_family,
        title=title,
        abstract=abstract,
        n_table_rows=n_table_rows,
        n_discourse_rows=n_discourse_rows,
        extractable=extractable,
        priority=priority,
    )


def triage_papers(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    articles_db_path: str = "ae.db",
    output_path: str | None = "data/production/paper_triage.json",
) -> TriageResult:
    """
    Classify each paper by type using its content.

    Args:
        csv_path: Path to the CSV with extracted data
        articles_db_path: Path to articles database for titles/abstracts
        output_path: Where to save results (None to skip saving)

    Returns:
        TriageResult with classification for each paper
    """
    import sqlite3

    # Load CSV
    df = pd.read_csv(csv_path, low_memory=False)

    # Load articles metadata if available
    articles = {}
    if Path(articles_db_path).exists():
        try:
            conn = sqlite3.connect(articles_db_path)
            articles_df = pd.read_sql("SELECT doi, title, abstract FROM articles", conn)
            conn.close()
            for _, row in articles_df.iterrows():
                doi = row.get("doi")
                if doi:
                    articles[f"doi:{doi}"] = {
                        "title": row.get("title"),
                        "abstract": row.get("abstract"),
                    }
        except Exception:
            pass  # No articles table or other error

    # Group by paper_id and classify each
    paper_triages = []
    paper_ids = df["paper_id"].dropna().unique()

    for paper_id in paper_ids:
        paper_rows = df[df["paper_id"] == paper_id]
        article_info = articles.get(paper_id, {})

        triage = _classify_paper(
            paper_id=paper_id,
            rows=paper_rows,
            title=article_info.get("title"),
            abstract=article_info.get("abstract"),
        )
        paper_triages.append(triage)

    # Sort by priority (highest first)
    paper_triages.sort(key=lambda x: x.priority, reverse=True)

    # Compute summary stats
    by_type = Counter(p.triage_type for p in paper_triages)
    extractable_count = sum(1 for p in paper_triages if p.extractable)

    result = TriageResult(
        papers=paper_triages,
        total_papers=len(paper_triages),
        by_type=dict(by_type),
        extractable_count=extractable_count,
        method="rule_based",
    )

    # Save if path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)

    return result


def get_extractable_papers(triage_path: str = "data/production/paper_triage.json") -> list[str]:
    """Return list of paper_ids that are extractable."""
    with open(triage_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [p["paper_id"] for p in data["papers"] if p.get("extractable")]


def print_triage_report(result: TriageResult) -> str:
    """Generate a human-readable triage report."""
    lines = [
        "PAPER TRIAGE REPORT",
        "=" * 60,
        f"Total papers: {result.total_papers}",
        f"Method: {result.method}",
        "",
        "BY TYPE:",
    ]

    for type_name, count in sorted(result.by_type.items(), key=lambda x: -x[1]):
        extractable = "✓" if type_name in ("empirical", "review", "meta_analysis") else " "
        lines.append(f"  {extractable} {type_name}: {count}")

    lines.extend([
        "",
        f"Extractable papers: {result.extractable_count}",
        "",
        "TOP 20 BY PRIORITY:",
    ])

    for p in result.papers[:20]:
        domains = ", ".join(p.relevant_domains[:3]) if p.relevant_domains else "no domains"
        lines.append(
            f"  [{p.triage_type}] {p.paper_id[:50]} "
            f"(tables:{p.n_table_rows}, {domains})"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Run triage when executed directly
    print("Running paper triage...")
    result = triage_papers()
    print(print_triage_report(result))
