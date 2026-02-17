"""
Argument-specific query handlers for Sprint 8.0 QA integration.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from src.argument.critique_aggregator import CritiqueAggregator
from src.argument.hierarchy_evidence import HierarchyAggregator
from src.argument.template_hierarchy_registry import load_template_hierarchy_registry


class ArgumentQueryHandler:
    """
    Handles argument-structure queries before generic web-of-belief search.
    """

    CRITIQUE_PATTERN = re.compile(r"what\s+critiques?\s+exist\s+for\s+(.+?)(?:\?|$)", re.IGNORECASE)
    HIERARCHY_PATTERN = re.compile(
        r"how\s+strong\s+is\s+(?:the\s+)?evidence\s+for\s+(.+?)(?:\?|$)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        critique_aggregator: Optional[CritiqueAggregator] = None,
        hierarchy_aggregator: Optional[HierarchyAggregator] = None,
        target_aliases: Optional[Dict[str, str]] = None,
    ):
        template_registry, template_aliases = load_template_hierarchy_registry()
        self.critique_aggregator = critique_aggregator or CritiqueAggregator()
        self.hierarchy_aggregator = hierarchy_aggregator or HierarchyAggregator(
            hierarchy_registry=template_registry
        )

        merged_aliases: Dict[str, str] = dict(template_aliases)
        merged_aliases.update(target_aliases or {})
        self.target_aliases = {self._normalize_alias(k): v for k, v in merged_aliases.items()}

    def handle_query(
        self,
        query_id: str,
        query_text: str,
        processing_time_ms: int,
    ) -> Optional[Dict[str, Any]]:
        critique_match = self.CRITIQUE_PATTERN.search(query_text)
        if critique_match:
            raw = critique_match.group(1).strip()
            target_id = self._resolve_target(raw)
            return self._build_critique_response(
                query_id,
                query_text,
                raw,
                target_id,
                processing_time_ms,
            )

        hierarchy_match = self.HIERARCHY_PATTERN.search(query_text)
        if hierarchy_match:
            raw = hierarchy_match.group(1).strip()
            hierarchy_id = self._resolve_target(raw)
            return self._build_hierarchy_response(
                query_id,
                query_text,
                raw,
                hierarchy_id,
                processing_time_ms,
            )

        return None

    def _resolve_target(self, raw_target: str) -> str:
        key = self._normalize_alias(raw_target)
        return self.target_aliases.get(key, key.replace(" ", "_"))

    def _normalize_alias(self, value: str) -> str:
        value = value.lower().strip().replace("_", " ")
        value = re.sub(r"\s+", " ", value)
        return value

    def _build_critique_response(
        self,
        query_id: str,
        query_text: str,
        raw_target: str,
        target_id: str,
        processing_time_ms: int,
    ) -> Dict[str, Any]:
        collection = self.critique_aggregator.collect_critiques(
            target_id=target_id,
            target_type="paper",
        )
        report = self.critique_aggregator.vulnerability_report(
            target_id=target_id,
            target_type="paper",
        )

        headline = (
            f"Found {collection.total_critique_count} critiques for {raw_target}."
            if collection.total_critique_count
            else f"No critiques found for {raw_target}."
        )

        response = {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": "success" if collection.total_critique_count else "no_results",
            "response_mode": "summary",
            "headline": headline,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "query_type": "paper_critiques",
                "target_id": target_id,
                "original_query": query_text,
            },
            "summary": {
                "target": raw_target,
                "total_critique_count": collection.total_critique_count,
                "weighted_critique_severity": collection.weighted_critique_severity,
                "unresolved_count": collection.unresolved_count,
                "vulnerability_profile": collection.vulnerability_profile,
            },
            "detail": {
                "method_critiques": [item.to_dict() for item in collection.method_critiques],
                "stimulus_critiques": [item.to_dict() for item in collection.stimulus_critiques],
                "population_critiques": [
                    item.to_dict() for item in collection.population_critiques
                ],
                "assumption_critiques": [
                    item.to_dict() for item in collection.assumption_critiques
                ],
                "interpretation_critiques": [
                    item.to_dict() for item in collection.interpretation_critiques
                ],
                "statistical_critiques": [
                    item.to_dict() for item in collection.statistical_critiques
                ],
            },
            "report": report,
            "follow_ups": [
                {
                    "question": f"What methodological critiques dominate for {raw_target}?",
                    "type": "deeper",
                    "executable_query": f"what critiques exist for {raw_target}",
                }
            ],
        }
        return response

    def _build_hierarchy_response(
        self,
        query_id: str,
        query_text: str,
        raw_target: str,
        hierarchy_id: str,
        processing_time_ms: int,
    ) -> Dict[str, Any]:
        evidence = self.hierarchy_aggregator.aggregate_hierarchy_evidence(hierarchy_id)
        validation = self.hierarchy_aggregator.validate_hierarchy(hierarchy_id)
        bridge = self.hierarchy_aggregator.build_hierarchy_template_bridge(hierarchy_id)

        pairwise = []
        for (higher, lower), item in evidence.pairwise_comparisons.items():
            pairwise.append(
                {
                    "higher_level": higher,
                    "lower_level": lower,
                    "studies_comparing": item.studies_comparing,
                    "pooled_difference": item.pooled_difference,
                    "confidence_interval": item.confidence_interval,
                    "indirect_chain": item.indirect_chain,
                    "indirect_confidence": item.indirect_confidence,
                }
            )

        headline = (
            f"Hierarchy evidence for {raw_target}: {validation['verdict']} "
            f"({evidence.n_studies} studies)."
        )

        return {
            "schema": "ae.query_response.v1",
            "query_id": query_id,
            "status": (
                "success"
                if (evidence.n_studies or evidence.ordered_levels)
                else "no_results"
            ),
            "response_mode": "summary",
            "headline": headline,
            "metadata": {
                "processing_time_ms": processing_time_ms,
                "query_type": "hierarchy_evidence",
                "target_id": hierarchy_id,
                "original_query": query_text,
            },
            "summary": {
                "hierarchy_id": hierarchy_id,
                "ordered_levels": evidence.ordered_levels,
                "evidence_strength": evidence.evidence_strength,
                "n_studies": evidence.n_studies,
                "verdict": validation["verdict"],
            },
            "detail": {
                "pairwise_comparisons": pairwise,
                "validation": validation,
                "bridge": bridge,
            },
            "follow_ups": [
                {
                    "question": f"What pairwise evidence is missing for {raw_target}?",
                    "type": "uncertainty",
                    "executable_query": f"how strong is evidence for {raw_target}",
                }
            ],
        }
