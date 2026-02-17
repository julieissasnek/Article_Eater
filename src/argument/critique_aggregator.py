"""
Critique collection and vulnerability aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from src.argument.paper_relations import PaperRelation, PaperRelationType


@dataclass
class CritiqueCollection:
    """All critiques targeting a specific paper/method/claim."""

    target_id: str
    target_type: str
    method_critiques: List[PaperRelation] = field(default_factory=list)
    stimulus_critiques: List[PaperRelation] = field(default_factory=list)
    population_critiques: List[PaperRelation] = field(default_factory=list)
    assumption_critiques: List[PaperRelation] = field(default_factory=list)
    interpretation_critiques: List[PaperRelation] = field(default_factory=list)
    statistical_critiques: List[PaperRelation] = field(default_factory=list)
    total_critique_count: int = 0
    weighted_critique_severity: float = 0.0
    unresolved_count: int = 0
    vulnerability_profile: Dict[str, float] = field(default_factory=dict)


class CritiqueAggregator:
    """Collects and summarizes critiques for a target artifact."""

    _RELATION_BUCKET = {
        PaperRelationType.CRITIQUES_METHOD: "method_critiques",
        PaperRelationType.CRITIQUES_STIMULUS: "stimulus_critiques",
        PaperRelationType.CRITIQUES_POPULATION: "population_critiques",
        PaperRelationType.CRITIQUES_ASSUMPTION: "assumption_critiques",
        PaperRelationType.CRITIQUES_INTERPRETATION: "interpretation_critiques",
        PaperRelationType.CRITIQUES_STATISTICS: "statistical_critiques",
    }

    def __init__(self, relations: Iterable[PaperRelation] | None = None):
        self._relations: List[PaperRelation] = list(relations or [])

    def add_relation(self, relation: PaperRelation) -> None:
        self._relations.append(relation)

    def add_relations(self, relations: Iterable[PaperRelation]) -> None:
        self._relations.extend(relations)

    def collect_critiques(self, target_id: str, target_type: str = "paper") -> CritiqueCollection:
        critiques = [
            relation
            for relation in self._relations
            if relation.target_paper_id == target_id
            and relation.relation_type in self._RELATION_BUCKET
        ]

        collection = CritiqueCollection(target_id=target_id, target_type=target_type)
        vulnerability: Dict[str, float] = {}

        for relation in critiques:
            bucket = self._RELATION_BUCKET[relation.relation_type]
            getattr(collection, bucket).append(relation)

            aspect_key = relation.target_aspect or relation.relation_type.value
            vulnerability[aspect_key] = (
                vulnerability.get(aspect_key, 0.0) + relation.critique_strength
            )

            collection.weighted_critique_severity += relation.critique_strength
            if not relation.resolved:
                collection.unresolved_count += 1

        collection.total_critique_count = len(critiques)
        collection.weighted_critique_severity = round(collection.weighted_critique_severity, 3)
        collection.vulnerability_profile = {
            key: round(value, 3)
            for key, value in sorted(vulnerability.items(), key=lambda item: -item[1])
        }

        return collection

    def vulnerability_report(self, target_id: str, target_type: str = "paper") -> Dict[str, Any]:
        collection = self.collect_critiques(target_id=target_id, target_type=target_type)
        avg_severity = (
            collection.weighted_critique_severity / collection.total_critique_count
            if collection.total_critique_count
            else 0.0
        )

        return {
            "target_id": target_id,
            "target_type": target_type,
            "total_critiques": collection.total_critique_count,
            "unresolved_critiques": collection.unresolved_count,
            "weighted_severity": collection.weighted_critique_severity,
            "avg_severity": round(avg_severity, 3),
            "high_risk_aspects": list(collection.vulnerability_profile.keys())[:3],
            "vulnerability_profile": collection.vulnerability_profile,
            "critique_breakdown": {
                "method": len(collection.method_critiques),
                "stimulus": len(collection.stimulus_critiques),
                "population": len(collection.population_critiques),
                "assumption": len(collection.assumption_critiques),
                "interpretation": len(collection.interpretation_critiques),
                "statistics": len(collection.statistical_critiques),
            },
        }
