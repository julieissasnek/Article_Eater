"""
Paper-level argument relations and citation-context extraction.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


class PaperRelationType(Enum):
    """Types of inter-paper argument relations."""

    REPLICATES = "replicates"
    FAILS_TO_REPLICATE = "fails_to_replicate"
    EXTENDS = "extends"

    CRITIQUES_METHOD = "critiques_method"
    CRITIQUES_STIMULUS = "critiques_stimulus"
    CRITIQUES_POPULATION = "critiques_population"
    CRITIQUES_ASSUMPTION = "critiques_assumption"
    CRITIQUES_INTERPRETATION = "critiques_interpretation"
    CRITIQUES_STATISTICS = "critiques_statistics"

    META_ANALYZES = "meta_analyzes"
    REVIEWS = "reviews"

    CONFIRMS = "confirms"
    CITES_SUPPORTING = "cites_supporting"


CRITIQUE_RELATION_TYPES = {
    PaperRelationType.CRITIQUES_METHOD,
    PaperRelationType.CRITIQUES_STIMULUS,
    PaperRelationType.CRITIQUES_POPULATION,
    PaperRelationType.CRITIQUES_ASSUMPTION,
    PaperRelationType.CRITIQUES_INTERPRETATION,
    PaperRelationType.CRITIQUES_STATISTICS,
}


@dataclass
class PaperRelation:
    """Argumentative relation between two papers."""

    relation_id: str
    source_paper_id: str
    target_paper_id: str
    relation_type: PaperRelationType
    target_aspect: str = "unknown"
    specific_target: str = ""
    critique_summary: str = ""
    evidence_for_critique: List[str] = field(default_factory=list)
    critique_strength: float = 0.5
    resolved: bool = False
    resolution: Optional[str] = None

    def is_critique(self) -> bool:
        return self.relation_type in CRITIQUE_RELATION_TYPES

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_paper_id": self.source_paper_id,
            "target_paper_id": self.target_paper_id,
            "relation_type": self.relation_type.value,
            "target_aspect": self.target_aspect,
            "specific_target": self.specific_target,
            "critique_summary": self.critique_summary,
            "evidence_for_critique": self.evidence_for_critique,
            "critique_strength": self.critique_strength,
            "resolved": self.resolved,
            "resolution": self.resolution,
        }


_RELATION_HINTS: List[Tuple[PaperRelationType, List[str]]] = [
    (
        PaperRelationType.FAILS_TO_REPLICATE,
        [
            r"fail(?:ed|s)?\s+to\s+replicat",
            r"did\s+not\s+replicat",
            r"non[-\s]?replication",
        ],
    ),
    (
        PaperRelationType.REPLICATES,
        [
            r"direct\s+replicat",
            r"success(?:ful)?\s+replicat",
            r"replicat(?:ed|es)\s+the\s+findings?",
        ],
    ),
    (
        PaperRelationType.META_ANALYZES,
        [
            r"meta[-\s]?analysis",
            r"pooled\s+effect",
            r"quantitative\s+synthesis",
        ],
    ),
    (PaperRelationType.REVIEWS, [r"systematic\s+review", r"narrative\s+review"]),
    (PaperRelationType.EXTENDS, [r"extend(?:s|ed)", r"generaliz(?:e|es|ed)\s+to"]),
    (
        PaperRelationType.CRITIQUES_METHOD,
        [r"methodolog(?:y|ical)\s+flaw", r"measurement\s+bias", r"protocol\s+issue"],
    ),
    (
        PaperRelationType.CRITIQUES_STIMULUS,
        [r"stimulus\s+validity", r"artifact\s+of\s+the\s+stimulus"],
    ),
    (
        PaperRelationType.CRITIQUES_POPULATION,
        [r"population\s+bias", r"sample\s+bias", r"limited\s+generalizability"],
    ),
    (
        PaperRelationType.CRITIQUES_ASSUMPTION,
        [r"assum(?:es|ption)\s+that", r"unjustified\s+assumption"],
    ),
    (
        PaperRelationType.CRITIQUES_INTERPRETATION,
        [r"alternative\s+interpretation", r"misinterpret(?:ed|ation)"],
    ),
    (
        PaperRelationType.CRITIQUES_STATISTICS,
        [r"underpowered", r"p[-\s]?hacking", r"incorrect\s+model", r"statistical\s+issue"],
    ),
    (
        PaperRelationType.CONFIRMS,
        [r"independent(?:ly)?\s+confirm", r"consistent\s+with\s+prior"],
    ),
]

_ASPECT_HINTS: List[Tuple[str, List[str]]] = [
    ("method", [r"method", r"protocol", r"measurement", r"instrument"]),
    ("stimulus", [r"stimulus", r"exposure", r"manipulation"]),
    ("population", [r"population", r"sample", r"cohort", r"participants"]),
    ("assumption", [r"assumption", r"premise"]),
    ("interpretation", [r"interpretation", r"inference"]),
    ("statistics", [r"statistical", r"model", r"power"]),
]

_STRONG_CRITIQUE_HINTS = (
    "fatally flawed",
    "invalid",
    "cannot support",
    "failed to replicate",
    "systematic bias",
    "serious flaw",
)
_WEAK_CRITIQUE_HINTS = (
    "may",
    "might",
    "possibly",
    "suggests caution",
    "limited evidence",
)


def infer_relation_type(citation_context: str) -> PaperRelationType:
    """Infer relation type from citation context text."""

    text = citation_context.lower()
    for relation_type, patterns in _RELATION_HINTS:
        if any(re.search(pattern, text) for pattern in patterns):
            return relation_type
    return PaperRelationType.CITES_SUPPORTING


def infer_target_aspect(citation_context: str) -> Tuple[str, str]:
    """Infer broad target aspect and a narrow target string."""

    text = citation_context.lower()
    aspect = "unknown"

    for candidate, patterns in _ASPECT_HINTS:
        if any(re.search(pattern, text) for pattern in patterns):
            aspect = candidate
            break

    specific_target = ""
    quoted = re.search(r"['\"]([^'\"]{3,80})['\"]", citation_context)
    if quoted:
        specific_target = quoted.group(1).strip()
    else:
        targeted = re.search(r"(?:about|on|of)\s+([a-z0-9\-\s]{4,80})", text)
        if targeted:
            specific_target = targeted.group(1).strip(" .,;:")

    return aspect, specific_target


def estimate_critique_strength(citation_context: str) -> float:
    """Estimate critique severity in [0, 1] from lexical cues."""

    text = citation_context.lower()
    score = 0.5

    for hint in _STRONG_CRITIQUE_HINTS:
        if hint in text:
            score += 0.2

    for hint in _WEAK_CRITIQUE_HINTS:
        if hint in text:
            score -= 0.08

    return max(0.0, min(1.0, round(score, 2)))


def _stable_relation_id(
    source_paper_id: str,
    target_paper_id: str,
    context: str,
    index: int,
) -> str:
    payload = f"{source_paper_id}|{target_paper_id}|{index}|{context[:160]}".encode("utf-8")
    digest = hashlib.md5(payload).hexdigest()[:12]
    return f"rel_{digest}"


def _coerce_relation_type(value: Any, fallback_context: str) -> PaperRelationType:
    if isinstance(value, PaperRelationType):
        return value
    if isinstance(value, str):
        for item in PaperRelationType:
            if value == item.value or value == item.name:
                return item
    return infer_relation_type(fallback_context)


def extract_paper_relations_from_citation_analysis(
    source_paper_id: str,
    citation_records: Iterable[Dict[str, Any]],
) -> List[PaperRelation]:
    """
    Build paper relations from citation-analysis records.

    Expected record fields:
    - target_paper_id (required)
    - citation_text or citation_context (required)
    - relation_type (optional)
    - target_aspect (optional)
    - specific_target (optional)
    - critique_strength (optional)
    - critique_summary (optional)
    - evidence_for_critique (optional list[str])
    - resolved (optional bool)
    - resolution (optional str)
    """

    relations: List[PaperRelation] = []
    for idx, record in enumerate(citation_records):
        target_paper_id = str(record.get("target_paper_id", "")).strip()
        context = str(record.get("citation_text") or record.get("citation_context") or "").strip()
        if not target_paper_id or not context:
            continue

        relation_type = _coerce_relation_type(record.get("relation_type"), context)
        inferred_aspect, inferred_specific = infer_target_aspect(context)
        target_aspect = str(record.get("target_aspect") or inferred_aspect or "unknown")
        specific_target = str(record.get("specific_target") or inferred_specific or "")
        critique_strength = float(
            record.get("critique_strength") or estimate_critique_strength(context)
        )
        critique_summary = str(record.get("critique_summary") or context[:220])
        evidence_for_critique = list(record.get("evidence_for_critique") or [])
        resolved = bool(record.get("resolved", False))
        resolution = record.get("resolution")

        relations.append(
            PaperRelation(
                relation_id=_stable_relation_id(source_paper_id, target_paper_id, context, idx),
                source_paper_id=source_paper_id,
                target_paper_id=target_paper_id,
                relation_type=relation_type,
                target_aspect=target_aspect,
                specific_target=specific_target,
                critique_summary=critique_summary,
                evidence_for_critique=evidence_for_critique,
                critique_strength=max(0.0, min(1.0, critique_strength)),
                resolved=resolved,
                resolution=resolution,
            )
        )

    return relations
