"""Argument structure and aggregation utilities for QA sprint phase 8."""

from src.argument.critique_aggregator import CritiqueAggregator, CritiqueCollection
from src.argument.hierarchy_evidence import (
    HierarchyAggregator,
    HierarchyEvidence,
    PairwiseEvidence,
)
from src.argument.meta_analytic import MetaAnalyticAggregator, MetaAnalyticLink, MetaAnalyticSummary
from src.argument.paper_relations import (
    CRITIQUE_RELATION_TYPES,
    PaperRelation,
    PaperRelationType,
    extract_paper_relations_from_citation_analysis,
)
from src.argument.template_hierarchy_registry import (
    build_hierarchy_registry_from_dir,
    load_template_hierarchy_registry,
)

__all__ = [
    "CRITIQUE_RELATION_TYPES",
    "CritiqueAggregator",
    "CritiqueCollection",
    "HierarchyAggregator",
    "HierarchyEvidence",
    "MetaAnalyticAggregator",
    "MetaAnalyticLink",
    "MetaAnalyticSummary",
    "PairwiseEvidence",
    "PaperRelation",
    "PaperRelationType",
    "build_hierarchy_registry_from_dir",
    "extract_paper_relations_from_citation_analysis",
    "load_template_hierarchy_registry",
]
