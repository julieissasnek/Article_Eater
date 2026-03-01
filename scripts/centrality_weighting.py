#!/usr/bin/env python3
"""Centrality Weighting for Findings and Article Adequacy.

Weights extracted findings by their relevance to central concepts in the BN/Web,
and computes article adequacy scores based on weighted findings.

Usage:
    python scripts/centrality_weighting.py --analyze-web
    python scripts/centrality_weighting.py --score-extraction batch_20260223_1657.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
WEB_FILE = PROJECT_ROOT / "data" / "accumulated_web.json"
TEMPLATE_DIR = PROJECT_ROOT / ".claude" / "worktrees" / "nice-hofstadter" / "data" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"


@dataclass
class CentralityConcept:
    """A concept in the web with its centrality metrics."""
    concept_id: str
    canonical_name: str
    degree_centrality: int
    in_degree: int
    out_degree: int
    constraint_types: dict[str, int] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)

    @property
    def normalized_centrality(self) -> float:
        """Normalized centrality score [0, 1]."""
        # Max observed degree ~868, use 1000 as ceiling
        return min(1.0, self.degree_centrality / 1000.0)


@dataclass
class FindingScore:
    """Centrality score for an extracted finding."""
    finding_id: int
    antecedent: str
    consequent: str
    direction: str
    matched_concepts: list[str]
    concept_scores: dict[str, float]
    total_score: float
    adequacy_category: str  # high, medium, low, unknown

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "direction": self.direction,
            "matched_concepts": self.matched_concepts,
            "total_score": round(self.total_score, 4),
            "adequacy_category": self.adequacy_category,
        }


@dataclass
class ArticleAdequacy:
    """Adequacy score for an article based on its findings."""
    doi: str
    article_type: str
    n_findings: int
    n_high_centrality: int
    n_medium_centrality: int
    n_low_centrality: int
    n_unknown: int
    total_weighted_score: float
    average_finding_score: float
    adequacy_grade: str  # A, B, C, D, F
    finding_scores: list[FindingScore] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "doi": self.doi,
            "article_type": self.article_type,
            "n_findings": self.n_findings,
            "breakdown": {
                "high_centrality": self.n_high_centrality,
                "medium_centrality": self.n_medium_centrality,
                "low_centrality": self.n_low_centrality,
                "unknown": self.n_unknown,
            },
            "total_weighted_score": round(self.total_weighted_score, 4),
            "average_finding_score": round(self.average_finding_score, 4),
            "adequacy_grade": self.adequacy_grade,
        }


class CentralityAnalyzer:
    """Analyzes centrality in the web of belief and scores findings."""

    # Key architectural/environmental concepts that map to BN nodes
    CONCEPT_KEYWORDS = {
        "central_hearth": ["hearth", "fireplace", "central", "gathering", "focal"],
        "spatial_entropy": ["complexity", "entropy", "spatial", "legibility", "wayfinding"],
        "visible_dirt_decay": ["dirt", "decay", "maintenance", "cleanliness", "degradation"],
        "wood_prominent": ["wood", "timber", "wooden", "natural material"],
        "glass_prominent": ["glass", "transparency", "daylight", "window", "glazing"],
        "metal_prominent": ["metal", "steel", "industrial", "metallic"],
        "glare": ["glare", "brightness", "visual comfort", "daylighting"],
        "ceiling_height": ["ceiling", "height", "volume", "spaciousness"],
        "enclosure": ["enclosure", "openness", "refuge", "prospect", "boundary"],
        "nature_view": ["nature", "biophilia", "green", "plants", "vegetation", "view"],
        "noise": ["noise", "acoustic", "sound", "quiet", "auditory"],
        "temperature": ["temperature", "thermal", "comfort", "HVAC", "climate"],
        "lighting": ["light", "illumination", "lux", "brightness", "circadian"],
        "color": ["color", "colour", "hue", "warm", "cool", "chromatic"],
        "texture": ["texture", "tactile", "material", "surface", "haptic"],
        "crowding": ["crowding", "density", "personal space", "proxemics"],
        "wayfinding": ["wayfinding", "navigation", "orientation", "legibility"],
        "stress": ["stress", "cortisol", "anxiety", "relaxation", "calm"],
        "attention": ["attention", "focus", "concentration", "distraction"],
        "affect": ["affect", "mood", "emotion", "valence", "arousal"],
        "preference": ["preference", "aesthetic", "beauty", "liking", "appeal"],
        "performance": ["performance", "productivity", "cognition", "task"],
        "restoration": ["restoration", "restorative", "recovery", "fatigue"],
    }

    def __init__(self):
        self.concepts: dict[str, CentralityConcept] = {}
        self.belief_centrality: dict[str, int] = {}
        self.web_loaded = False

    def load_web(self) -> bool:
        """Load web of belief and compute centrality metrics."""
        if not WEB_FILE.exists():
            print(f"Web file not found: {WEB_FILE}")
            return False

        with open(WEB_FILE) as f:
            web = json.load(f)

        beliefs = web.get("beliefs", {})
        constraints = web.get("constraints", {})

        # Compute degree centrality
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)
        constraint_types: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for cid, c in constraints.items():
            source = c.get("source_id", "")
            target = c.get("target_id", "")
            ctype = c.get("constraint_type", "unknown")

            out_degree[source] += 1
            in_degree[target] += 1
            constraint_types[source][ctype] += 1
            constraint_types[target][ctype] += 1

        # Store belief centrality
        for bid in beliefs:
            self.belief_centrality[bid] = in_degree.get(bid, 0) + out_degree.get(bid, 0)

        # Extract key concepts from high-centrality beliefs
        for bid, degree in sorted(self.belief_centrality.items(), key=lambda x: -x[1])[:100]:
            belief = beliefs.get(bid, {})
            content = belief.get("content", "")

            # Extract concept name from content
            concept_name = self._extract_concept_name(content)
            if concept_name and concept_name not in self.concepts:
                self.concepts[concept_name] = CentralityConcept(
                    concept_id=bid,
                    canonical_name=concept_name,
                    degree_centrality=degree,
                    in_degree=in_degree.get(bid, 0),
                    out_degree=out_degree.get(bid, 0),
                    constraint_types=dict(constraint_types[bid]),
                    keywords=self._get_keywords_for_concept(concept_name),
                )

        self.web_loaded = True
        print(f"Loaded web: {len(beliefs)} beliefs, {len(constraints)} constraints")
        print(f"Identified {len(self.concepts)} central concepts")
        return True

    def _extract_concept_name(self, content: str) -> str | None:
        """Extract concept name from belief content."""
        # Pattern: env.xxx.yyy -> yyy or out.xxx.yyy -> yyy
        patterns = [
            r"env\.[\w.]+\.(\w+)",
            r"out\.[\w.]+\.(\w+)",
            r"env\.(\w+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None

    def _get_keywords_for_concept(self, concept_name: str) -> list[str]:
        """Get keywords for a concept."""
        # Check predefined keywords
        for key, keywords in self.CONCEPT_KEYWORDS.items():
            if key in concept_name.lower() or concept_name.lower() in key:
                return keywords

        # Generate from concept name
        words = re.split(r"[_\s]+", concept_name.lower())
        return words

    def score_finding(self, finding: dict) -> FindingScore:
        """Score a single finding by its centrality relevance."""
        antecedent = (finding.get("antecedent") or "").lower()
        consequent = (finding.get("consequent") or "").lower()
        direction = finding.get("direction", "unknown")
        finding_id = finding.get("id", 0)

        # Find matching concepts
        matched_concepts = []
        concept_scores: dict[str, float] = {}

        combined_text = f"{antecedent} {consequent}"

        for concept_name, concept in self.concepts.items():
            score = 0.0
            for keyword in concept.keywords:
                if keyword.lower() in combined_text:
                    score += 0.3 * concept.normalized_centrality

            if score > 0:
                matched_concepts.append(concept_name)
                concept_scores[concept_name] = score

        # Also check predefined keywords
        for key, keywords in self.CONCEPT_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in combined_text and key not in matched_concepts:
                    matched_concepts.append(key)
                    concept_scores[key] = 0.2  # Base score for predefined

        total_score = sum(concept_scores.values())

        # Direction bonus: clear increase/decrease is more valuable
        if direction in ("increase", "decrease"):
            total_score *= 1.2
        elif direction == "no_effect":
            total_score *= 0.8  # Still useful (null results)

        # Categorize
        if total_score >= 0.5:
            category = "high"
        elif total_score >= 0.2:
            category = "medium"
        elif total_score > 0:
            category = "low"
        else:
            category = "unknown"

        return FindingScore(
            finding_id=finding_id,
            antecedent=antecedent[:100],
            consequent=consequent[:100],
            direction=direction,
            matched_concepts=matched_concepts[:5],
            concept_scores=concept_scores,
            total_score=total_score,
            adequacy_category=category,
        )

    def score_article(self, extraction: dict) -> ArticleAdequacy:
        """Score an article based on its extracted findings."""
        doi = extraction.get("doi", "unknown")
        article_type = extraction.get("article_type", "unknown")

        final_result = extraction.get("final_result") or extraction.get("extraction", {})

        # Handle different article types - each has different field names
        findings = (
            final_result.get("findings")  # empirical
            or final_result.get("pooled_effects")  # meta_analysis
            or final_result.get("themes")  # narrative_review
            or final_result.get("methodological_claims")  # methods
            or final_result.get("theoretical_propositions")  # theoretical
            or []
        )

        finding_scores = []
        n_high = n_medium = n_low = n_unknown = 0
        total_weighted = 0.0

        for finding in findings:
            score = self.score_finding(finding)
            finding_scores.append(score)
            total_weighted += score.total_score

            if score.adequacy_category == "high":
                n_high += 1
            elif score.adequacy_category == "medium":
                n_medium += 1
            elif score.adequacy_category == "low":
                n_low += 1
            else:
                n_unknown += 1

        n_findings = len(findings)
        avg_score = total_weighted / n_findings if n_findings > 0 else 0.0

        # Grade calculation
        # A: >=3 high centrality findings OR avg >= 0.4
        # B: >=1 high OR >=3 medium OR avg >= 0.25
        # C: >=2 medium OR avg >= 0.15
        # D: >=1 medium or low OR any findings
        # F: no findings

        if n_findings == 0:
            grade = "F"
        elif n_high >= 3 or avg_score >= 0.4:
            grade = "A"
        elif n_high >= 1 or n_medium >= 3 or avg_score >= 0.25:
            grade = "B"
        elif n_medium >= 2 or avg_score >= 0.15:
            grade = "C"
        else:
            grade = "D"

        return ArticleAdequacy(
            doi=doi,
            article_type=article_type,
            n_findings=n_findings,
            n_high_centrality=n_high,
            n_medium_centrality=n_medium,
            n_low_centrality=n_low,
            n_unknown=n_unknown,
            total_weighted_score=total_weighted,
            average_finding_score=avg_score,
            adequacy_grade=grade,
            finding_scores=finding_scores,
        )


def analyze_web():
    """Analyze the web of belief and show centrality statistics."""
    analyzer = CentralityAnalyzer()
    if not analyzer.load_web():
        return

    print("\n=== TOP CENTRAL CONCEPTS ===")
    for name, concept in sorted(
        analyzer.concepts.items(),
        key=lambda x: -x[1].degree_centrality
    )[:20]:
        print(f"  {name}: degree={concept.degree_centrality}, "
              f"normalized={concept.normalized_centrality:.3f}")
        print(f"    Keywords: {', '.join(concept.keywords[:5])}")


def score_extraction_file(filename: str):
    """Score an extraction file and show results."""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return

    analyzer = CentralityAnalyzer()
    if not analyzer.load_web():
        print("Warning: Web not loaded, using keyword-only scoring")

    with open(filepath) as f:
        data = json.load(f)

    extractions = data if isinstance(data, list) else data.get("results", [])

    print(f"\n=== ARTICLE ADEQUACY SCORES ({len(extractions)} articles) ===\n")

    results = []
    grade_counts = Counter()

    for ext in extractions:
        adequacy = analyzer.score_article(ext)
        results.append(adequacy)
        grade_counts[adequacy.adequacy_grade] += 1

        print(f"DOI: {adequacy.doi[:50]}")
        print(f"  Type: {adequacy.article_type}")
        print(f"  Findings: {adequacy.n_findings}")
        print(f"  High/Med/Low/Unk: {adequacy.n_high_centrality}/{adequacy.n_medium_centrality}/"
              f"{adequacy.n_low_centrality}/{adequacy.n_unknown}")
        print(f"  Avg Score: {adequacy.average_finding_score:.3f}")
        print(f"  Grade: {adequacy.adequacy_grade}")
        print()

    print("=== SUMMARY ===")
    print(f"Grade distribution: {dict(grade_counts)}")

    # Save scored results
    output_file = OUTPUT_DIR / f"scored_{filename}"
    with open(output_file, "w") as f:
        json.dump({
            "source_file": filename,
            "n_articles": len(results),
            "grade_distribution": dict(grade_counts),
            "articles": [r.to_dict() for r in results],
        }, f, indent=2)
    print(f"\nSaved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Centrality weighting for findings")
    parser.add_argument("--analyze-web", action="store_true", help="Analyze web centrality")
    parser.add_argument("--score-extraction", type=str, help="Score an extraction file")

    args = parser.parse_args()

    if args.analyze_web:
        analyze_web()
    elif args.score_extraction:
        score_extraction_file(args.score_extraction)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
