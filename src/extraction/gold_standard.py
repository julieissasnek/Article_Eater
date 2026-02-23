"""
Gold standard paper management for extraction validation (Sprint D Task D.5).

Provides utilities for loading, updating, and validating against gold standard papers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GOLD_STANDARD_PATH = Path(__file__).parent.parent.parent / "data" / "gold_standard" / "gold_standard_papers.json"


@dataclass
class VerifiedClaim:
    """A manually verified claim from a gold standard paper."""

    claim_id: str
    environment_variable: str  # Canonical IV from vocabulary
    outcome_variable: str  # Canonical DV from vocabulary
    effect_direction: str  # positive, negative, null, mixed
    statement: str
    source_page: int | None = None
    source_table: str | None = None
    verified_by: str | None = None
    verified_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "environment_variable": self.environment_variable,
            "outcome_variable": self.outcome_variable,
            "effect_direction": self.effect_direction,
            "statement": self.statement,
            "source_page": self.source_page,
            "source_table": self.source_table,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "VerifiedClaim":
        return cls(
            claim_id=d["claim_id"],
            environment_variable=d["environment_variable"],
            outcome_variable=d["outcome_variable"],
            effect_direction=d["effect_direction"],
            statement=d["statement"],
            source_page=d.get("source_page"),
            source_table=d.get("source_table"),
            verified_by=d.get("verified_by"),
            verified_at=d.get("verified_at"),
        )


@dataclass
class GoldStandardPaper:
    """A gold standard paper for extraction validation."""

    paper_id: str
    article_type_family: str
    n_structured_rows: int
    gold_standard_status: str  # candidate, selected, rejected
    selection_rationale: str | None = None
    domains: list[str] = field(default_factory=list)
    manual_review_notes: str | None = None
    verified_claims: list[VerifiedClaim] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "article_type_family": self.article_type_family,
            "n_structured_rows": self.n_structured_rows,
            "gold_standard_status": self.gold_standard_status,
            "selection_rationale": self.selection_rationale,
            "domains": self.domains,
            "manual_review_notes": self.manual_review_notes,
            "verified_claims": [c.to_dict() for c in self.verified_claims],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GoldStandardPaper":
        verified = [VerifiedClaim.from_dict(c) for c in d.get("verified_claims", [])]
        return cls(
            paper_id=d["paper_id"],
            article_type_family=d["article_type_family"],
            n_structured_rows=d["n_structured_rows"],
            gold_standard_status=d["gold_standard_status"],
            selection_rationale=d.get("selection_rationale"),
            domains=d.get("domains", []),
            manual_review_notes=d.get("manual_review_notes"),
            verified_claims=verified,
        )


def load_gold_standard(path: str | Path | None = None) -> list[GoldStandardPaper]:
    """Load gold standard papers from JSON file."""
    filepath = Path(path) if path else GOLD_STANDARD_PATH

    if not filepath.exists():
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [GoldStandardPaper.from_dict(p) for p in data.get("papers", [])]


def save_gold_standard(papers: list[GoldStandardPaper], path: str | Path | None = None) -> None:
    """Save gold standard papers to JSON file."""
    filepath = Path(path) if path else GOLD_STANDARD_PATH
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Compute summary
    selected = sum(1 for p in papers if p.gold_standard_status == "selected")
    rejected = sum(1 for p in papers if p.gold_standard_status == "rejected")
    pending = sum(1 for p in papers if p.gold_standard_status == "candidate")

    data = {
        "metadata": {
            "updated": datetime.now(timezone.utc).isoformat(),
            "sprint": "D",
            "task": "D.5",
            "description": "Gold standard papers for extraction validation",
        },
        "papers": [p.to_dict() for p in papers],
        "summary": {
            "total": len(papers),
            "selected": selected,
            "rejected": rejected,
            "pending_review": pending,
        },
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_selected_papers(path: str | Path | None = None) -> list[GoldStandardPaper]:
    """Return only selected gold standard papers."""
    papers = load_gold_standard(path)
    return [p for p in papers if p.gold_standard_status == "selected"]


def get_paper_by_id(paper_id: str, path: str | Path | None = None) -> GoldStandardPaper | None:
    """Get a specific gold standard paper by ID."""
    papers = load_gold_standard(path)
    for p in papers:
        if p.paper_id == paper_id:
            return p
    return None


def add_verified_claim(
    paper_id: str,
    claim: VerifiedClaim,
    path: str | Path | None = None,
) -> bool:
    """Add a verified claim to a gold standard paper."""
    papers = load_gold_standard(path)

    for paper in papers:
        if paper.paper_id == paper_id:
            paper.verified_claims.append(claim)
            save_gold_standard(papers, path)
            return True

    return False


def validate_extraction_against_gold(
    paper_id: str,
    extracted_claims: list[dict],
    path: str | Path | None = None,
) -> dict:
    """
    Validate extracted claims against gold standard verified claims.

    Returns dict with precision, recall, and detailed matches.
    """
    paper = get_paper_by_id(paper_id, path)
    if not paper or not paper.verified_claims:
        return {
            "paper_id": paper_id,
            "status": "no_gold_standard",
            "message": "No verified claims available for this paper",
        }

    gold_claims = paper.verified_claims

    # Match by IV-DV pair
    gold_pairs = {(c.environment_variable, c.outcome_variable) for c in gold_claims}
    extracted_pairs = {(c.get("environment_variable"), c.get("outcome_variable")) for c in extracted_claims}

    true_positives = gold_pairs & extracted_pairs
    false_positives = extracted_pairs - gold_pairs
    false_negatives = gold_pairs - extracted_pairs

    precision = len(true_positives) / len(extracted_pairs) if extracted_pairs else 0.0
    recall = len(true_positives) / len(gold_pairs) if gold_pairs else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "paper_id": paper_id,
        "status": "validated",
        "n_gold_claims": len(gold_claims),
        "n_extracted_claims": len(extracted_claims),
        "true_positives": len(true_positives),
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "matched_pairs": list(true_positives),
        "missed_pairs": list(false_negatives),
        "spurious_pairs": list(false_positives),
    }


def print_gold_standard_summary(path: str | Path | None = None) -> str:
    """Generate summary report of gold standard papers."""
    papers = load_gold_standard(path)

    if not papers:
        return "No gold standard papers loaded."

    selected = [p for p in papers if p.gold_standard_status == "selected"]
    total_verified = sum(len(p.verified_claims) for p in papers)

    domains = {}
    for p in selected:
        for d in p.domains:
            domains[d] = domains.get(d, 0) + 1

    lines = [
        "GOLD STANDARD PAPERS SUMMARY",
        "=" * 50,
        f"Total papers: {len(papers)}",
        f"Selected: {len(selected)}",
        f"Total verified claims: {total_verified}",
        "",
        "DOMAIN COVERAGE:",
    ]

    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        lines.append(f"  {domain}: {count}")

    lines.extend(["", "SELECTED PAPERS:"])

    for p in selected:
        n_claims = len(p.verified_claims)
        lines.append(
            f"  {p.paper_id[:50]} ({p.article_type_family}, {n_claims} verified)"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(print_gold_standard_summary())
