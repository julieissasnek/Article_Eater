"""
Hierarchy-evidence bridge for cross-paper aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PairwiseEvidence:
    """Evidence supporting an ordered pair in a hierarchy."""

    higher_level: str
    lower_level: str
    studies_comparing: List[str] = field(default_factory=list)
    pooled_difference: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    indirect_chain: Optional[List[str]] = None
    indirect_confidence: float = 0.0


@dataclass
class HierarchyEvidence:
    """Cross-paper evidence for a within-template hierarchy."""

    hierarchy_id: str
    source_template: str
    ordered_levels: List[str]
    pairwise_comparisons: Dict[Tuple[str, str], PairwiseEvidence]
    evidence_strength: str
    n_studies: int
    n_papers: int


class HierarchyAggregator:
    """Aggregates direct and indirect evidence for hierarchy claims."""

    def __init__(self, hierarchy_registry: Any = None):
        self.hierarchy_registry = hierarchy_registry
        self._evidence: Dict[str, Dict[Tuple[str, str], List[PairwiseEvidence]]] = {}

    def add_pairwise_evidence(self, hierarchy_id: str, evidence: PairwiseEvidence) -> None:
        key = (evidence.higher_level, evidence.lower_level)
        self._evidence.setdefault(hierarchy_id, {}).setdefault(key, []).append(evidence)

    def aggregate_hierarchy_evidence(
        self,
        hierarchy_id: str,
        source_template: Optional[str] = None,
        ordered_levels: Optional[List[str]] = None,
    ) -> HierarchyEvidence:
        registry_item = self._lookup_registry_hierarchy(hierarchy_id)
        levels = (
            ordered_levels
            or (registry_item.get("ordered_levels") if registry_item else None)
            or self._levels_from_observed_edges(hierarchy_id)
        )
        levels = list(levels or [])

        template = (
            source_template
            or (registry_item.get("source_template") if registry_item else None)
            or "unknown"
        )

        pairwise_map: Dict[Tuple[str, str], PairwiseEvidence] = {}
        unique_studies = set()
        observed = self._evidence.get(hierarchy_id, {})

        for i in range(len(levels)):
            for j in range(i + 1, len(levels)):
                higher = levels[i]
                lower = levels[j]
                key = (higher, lower)
                entries = observed.get(key, [])
                merged = self._merge_entries(higher, lower, entries, levels)
                pairwise_map[key] = merged
                unique_studies.update(merged.studies_comparing)

        evidence_strength = self._classify_strength(len(unique_studies), pairwise_map)

        return HierarchyEvidence(
            hierarchy_id=hierarchy_id,
            source_template=template,
            ordered_levels=levels,
            pairwise_comparisons=pairwise_map,
            evidence_strength=evidence_strength,
            n_studies=len(unique_studies),
            n_papers=len(unique_studies),
        )

    def validate_hierarchy(self, hierarchy_id: str) -> Dict[str, Any]:
        evidence = self.aggregate_hierarchy_evidence(hierarchy_id)

        supported: List[Tuple[str, str]] = []
        challenged: List[Tuple[str, str]] = []
        missing: List[Tuple[str, str]] = []

        for pair, item in evidence.pairwise_comparisons.items():
            if item.pooled_difference is None:
                missing.append(pair)
                continue
            if item.confidence_interval and item.confidence_interval[0] <= 0:
                challenged.append(pair)
                continue
            if item.pooled_difference > 0:
                supported.append(pair)
            else:
                challenged.append(pair)

        if challenged:
            verdict = "contested"
        elif missing and supported:
            verdict = "partially_supported"
        elif supported:
            verdict = "supported"
        else:
            verdict = "insufficient_evidence"

        total_pairs = len(evidence.pairwise_comparisons)
        coverage = (len(supported) / total_pairs) if total_pairs else 0.0

        return {
            "hierarchy_id": hierarchy_id,
            "evidence_strength": evidence.evidence_strength,
            "verdict": verdict,
            "n_studies": evidence.n_studies,
            "coverage": round(coverage, 3),
            "supported_pairs": [f"{hi}>{lo}" for hi, lo in supported],
            "challenged_pairs": [f"{hi}>{lo}" for hi, lo in challenged],
            "missing_pairs": [f"{hi}>{lo}" for hi, lo in missing],
        }

    def build_hierarchy_template_bridge(self, hierarchy_id: str) -> Dict[str, Any]:
        """Bridge hierarchy registry structure with aggregated evidence."""

        registry_item = self._lookup_registry_hierarchy(hierarchy_id)
        validation = self.validate_hierarchy(hierarchy_id)
        return {
            "hierarchy_id": hierarchy_id,
            "registry_hierarchy": registry_item,
            "validation": validation,
        }

    def _lookup_registry_hierarchy(self, hierarchy_id: str) -> Optional[Dict[str, Any]]:
        registry = self.hierarchy_registry
        if registry is None:
            return None

        if hasattr(registry, "get_hierarchy"):
            item = registry.get_hierarchy(hierarchy_id)
            return item if isinstance(item, dict) else None

        if isinstance(registry, dict):
            return registry.get(hierarchy_id)

        if hasattr(registry, "hierarchies"):
            maybe = getattr(registry, "hierarchies")
            if isinstance(maybe, dict):
                return maybe.get(hierarchy_id)

        return None

    def _levels_from_observed_edges(self, hierarchy_id: str) -> List[str]:
        edges = self._evidence.get(hierarchy_id, {})
        if not edges:
            return []
        nodes = []
        for higher, lower in edges.keys():
            if higher not in nodes:
                nodes.append(higher)
            if lower not in nodes:
                nodes.append(lower)
        return nodes

    def _merge_entries(
        self,
        higher: str,
        lower: str,
        entries: List[PairwiseEvidence],
        ordered_levels: List[str],
    ) -> PairwiseEvidence:
        if not entries:
            indirect_chain = self._indirect_chain(higher, lower, ordered_levels)
            return PairwiseEvidence(
                higher_level=higher,
                lower_level=lower,
                studies_comparing=[],
                pooled_difference=None,
                confidence_interval=None,
                indirect_chain=indirect_chain,
                indirect_confidence=0.25 if indirect_chain else 0.0,
            )

        unique_studies = sorted({study for entry in entries for study in entry.studies_comparing})
        pooled_values = [
            entry.pooled_difference for entry in entries if entry.pooled_difference is not None
        ]
        pooled_difference = None if not pooled_values else sum(pooled_values) / len(pooled_values)

        ci_values = [
            entry.confidence_interval for entry in entries if entry.confidence_interval is not None
        ]
        confidence_interval = None
        if ci_values:
            lows = [ci[0] for ci in ci_values]
            highs = [ci[1] for ci in ci_values]
            confidence_interval = (sum(lows) / len(lows), sum(highs) / len(highs))

        return PairwiseEvidence(
            higher_level=higher,
            lower_level=lower,
            studies_comparing=unique_studies,
            pooled_difference=(
                round(pooled_difference, 4) if pooled_difference is not None else None
            ),
            confidence_interval=(
                (round(confidence_interval[0], 4), round(confidence_interval[1], 4))
                if confidence_interval
                else None
            ),
            indirect_chain=None,
            indirect_confidence=0.0,
        )

    def _indirect_chain(
        self,
        higher: str,
        lower: str,
        ordered_levels: List[str],
    ) -> Optional[List[str]]:
        if higher not in ordered_levels or lower not in ordered_levels:
            return None
        i = ordered_levels.index(higher)
        j = ordered_levels.index(lower)
        if i >= j or j - i <= 1:
            return None
        return ordered_levels[i : j + 1]

    def _classify_strength(
        self,
        n_studies: int,
        pairwise_map: Dict[Tuple[str, str], PairwiseEvidence],
    ) -> str:
        has_direct_effect = any(
            item.pooled_difference is not None for item in pairwise_map.values()
        )
        if n_studies >= 8 and has_direct_effect:
            return "meta-analytic"
        if n_studies >= 3:
            return "multi-study"
        if n_studies >= 1:
            return "single-study"
        return "theoretical"
