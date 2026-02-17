"""
Tests for Sprint 8.0 argument structure and aggregation layer.
"""

import json

from src.argument.critique_aggregator import CritiqueAggregator
from src.argument.hierarchy_evidence import HierarchyAggregator, PairwiseEvidence
from src.argument.meta_analytic import MetaAnalyticAggregator, MetaAnalyticLink
from src.argument.paper_relations import (
    PaperRelation,
    PaperRelationType,
    extract_paper_relations_from_citation_analysis,
)
from src.argument.qa_handlers import ArgumentQueryHandler
from src.argument.template_hierarchy_registry import build_hierarchy_registry_from_dir
from src.services.query_engine import QueryEngine
from src.services.web_of_belief import WebOfBelief


def test_extract_paper_relations_from_citation_analysis():
    citations = [
        {
            "target_paper_id": "ulrich_1984",
            "citation_text": "We failed to replicate Ulrich's effect due to protocol differences.",
        },
        {
            "target_paper_id": "ulrich_1984",
            "citation_text": "This study identifies a methodological flaw in HRV measurement.",
        },
        {
            "target_paper_id": "kaplan_1989",
            "citation_text": (
                "Our meta-analysis pools effects across attention restoration studies."
            ),
        },
    ]
    relations = extract_paper_relations_from_citation_analysis("smith_2024", citations)

    assert len(relations) == 3
    assert relations[0].relation_type == PaperRelationType.FAILS_TO_REPLICATE
    assert relations[1].relation_type == PaperRelationType.CRITIQUES_METHOD
    assert relations[2].relation_type == PaperRelationType.META_ANALYZES


def test_critique_aggregator_collection_and_report():
    relations = [
        PaperRelation(
            relation_id="r1",
            source_paper_id="a",
            target_paper_id="ulrich_1984",
            relation_type=PaperRelationType.CRITIQUES_METHOD,
            target_aspect="method",
            critique_summary="Method validity critique",
            critique_strength=0.8,
        ),
        PaperRelation(
            relation_id="r2",
            source_paper_id="b",
            target_paper_id="ulrich_1984",
            relation_type=PaperRelationType.CRITIQUES_POPULATION,
            target_aspect="population",
            critique_summary="Population mismatch",
            critique_strength=0.6,
            resolved=True,
        ),
    ]
    aggregator = CritiqueAggregator(relations)
    collection = aggregator.collect_critiques("ulrich_1984")
    report = aggregator.vulnerability_report("ulrich_1984")

    assert collection.total_critique_count == 2
    assert collection.unresolved_count == 1
    assert collection.vulnerability_profile["method"] == 0.8
    assert report["high_risk_aspects"][0] == "method"


def test_meta_analytic_summary_computation():
    links = [
        MetaAnalyticLink("meta_1", "s1", 0.40, (0.20, 0.60), 1.2, 120, {"setting": "office"}),
        MetaAnalyticLink("meta_1", "s2", 0.25, (0.05, 0.45), 1.0, 95, {"setting": "office"}),
        MetaAnalyticLink("meta_1", "s3", 0.10, (-0.10, 0.30), 0.8, 80, {"setting": "school"}),
    ]
    summary = MetaAnalyticAggregator().summarize(
        meta_paper_id="meta_1",
        outcome_construct="stress_recovery",
        included_studies=links,
    )

    assert summary.k == 3
    assert summary.total_n == 295
    assert 0.0 <= summary.i_squared <= 100.0
    assert summary.pooled_ci[0] < summary.pooled_effect < summary.pooled_ci[1]
    assert "setting" in summary.moderator_effects


def test_hierarchy_aggregation_and_validation():
    registry = {
        "color_hierarchy": {
            "source_template": "COL2",
            "ordered_levels": ["saturation", "brightness", "hue"],
        }
    }
    aggregator = HierarchyAggregator(hierarchy_registry=registry)
    aggregator.add_pairwise_evidence(
        "color_hierarchy",
        PairwiseEvidence(
            higher_level="saturation",
            lower_level="brightness",
            studies_comparing=["p1", "p2", "p3"],
            pooled_difference=0.42,
            confidence_interval=(0.28, 0.56),
        ),
    )
    aggregator.add_pairwise_evidence(
        "color_hierarchy",
        PairwiseEvidence(
            higher_level="brightness",
            lower_level="hue",
            studies_comparing=["p4", "p5"],
            pooled_difference=0.21,
            confidence_interval=(0.08, 0.34),
        ),
    )

    evidence = aggregator.aggregate_hierarchy_evidence("color_hierarchy")
    validation = aggregator.validate_hierarchy("color_hierarchy")

    assert evidence.source_template == "COL2"
    assert evidence.n_studies == 5
    assert ("saturation", "hue") in evidence.pairwise_comparisons
    assert evidence.pairwise_comparisons[("saturation", "hue")].indirect_chain == [
        "saturation",
        "brightness",
        "hue",
    ]
    assert validation["verdict"] == "partially_supported"


def test_argument_query_handler_critique_and_hierarchy_queries():
    relations = [
        PaperRelation(
            relation_id="r1",
            source_paper_id="a",
            target_paper_id="ulrich_1984",
            relation_type=PaperRelationType.CRITIQUES_METHOD,
            target_aspect="method",
            critique_summary="Method issue",
            critique_strength=0.7,
        )
    ]
    critique_agg = CritiqueAggregator(relations)
    hierarchy_agg = HierarchyAggregator(
        hierarchy_registry={
            "saturation_brightness": {
                "source_template": "COL2",
                "ordered_levels": ["saturation", "brightness"],
            }
        }
    )
    hierarchy_agg.add_pairwise_evidence(
        "saturation_brightness",
        PairwiseEvidence(
            higher_level="saturation",
            lower_level="brightness",
            studies_comparing=["p1", "p2"],
            pooled_difference=0.31,
            confidence_interval=(0.12, 0.50),
        ),
    )

    handler = ArgumentQueryHandler(
        critique_aggregator=critique_agg,
        hierarchy_aggregator=hierarchy_agg,
        target_aliases={
            "ulrich 1984": "ulrich_1984",
            "saturation > brightness": "saturation_brightness",
        },
    )

    critique_response = handler.handle_query(
        query_id="q1",
        query_text="What critiques exist for Ulrich 1984?",
        processing_time_ms=4,
    )
    hierarchy_response = handler.handle_query(
        query_id="q2",
        query_text="How strong is the evidence for saturation > brightness?",
        processing_time_ms=5,
    )

    assert critique_response is not None
    assert critique_response["status"] == "success"
    assert critique_response["summary"]["total_critique_count"] == 1

    assert hierarchy_response is not None
    assert hierarchy_response["status"] == "success"
    assert hierarchy_response["summary"]["hierarchy_id"] == "saturation_brightness"


def test_query_engine_routes_argument_queries():
    critique_agg = CritiqueAggregator(
        [
            PaperRelation(
                relation_id="r1",
                source_paper_id="source",
                target_paper_id="ulrich_1984",
                relation_type=PaperRelationType.CRITIQUES_METHOD,
                target_aspect="method",
                critique_summary="Methodological concern",
                critique_strength=0.75,
            )
        ]
    )
    handler = ArgumentQueryHandler(
        critique_aggregator=critique_agg,
        hierarchy_aggregator=HierarchyAggregator(),
        target_aliases={"ulrich 1984": "ulrich_1984"},
    )

    engine = QueryEngine(
        web=WebOfBelief(domain="neuroarchitecture"),
        argument_query_handler=handler,
    )
    response = engine.query("What critiques exist for Ulrich 1984?")

    assert response["metadata"]["query_type"] == "paper_critiques"
    assert response["summary"]["total_critique_count"] == 1


def test_template_hierarchy_registry_builder_supports_common_patterns(tmp_path):
    col2 = {
        "display_id": "COL2",
        "arousal_dimensions": {
            "saturation": {"effect_magnitude": "Primary (strongest)"},
            "brightness": {"effect_magnitude": "Secondary"},
            "hue_warm_cool": {"effect_magnitude": "Tertiary (modest)"},
        },
    }
    view1 = {
        "display_id": "VIEW1",
        "synthetic_nature_hierarchy": {
            "hierarchy": [
                "Real view (all channels)",
                "Video view (partial)",
                "No view",
            ]
        },
    }

    (tmp_path / "col2.json").write_text(json.dumps(col2), encoding="utf-8")
    (tmp_path / "view1.json").write_text(json.dumps(view1), encoding="utf-8")

    registry, aliases = build_hierarchy_registry_from_dir(tmp_path)

    assert "col2_arousal_dimensions" in registry
    assert registry["col2_arousal_dimensions"]["ordered_levels"][:2] == [
        "saturation",
        "brightness",
    ]
    assert aliases["saturation > brightness"] == "col2_arousal_dimensions"
    assert "view1_synthetic_nature_hierarchy" in registry


def test_argument_query_handler_auto_loads_template_aliases(monkeypatch):
    fake_registry = {
        "col2_arousal_dimensions": {
            "source_template": "COL2",
            "ordered_levels": ["saturation", "brightness", "hue"],
        }
    }
    fake_aliases = {"saturation > brightness": "col2_arousal_dimensions"}

    monkeypatch.setattr(
        "src.argument.qa_handlers.load_template_hierarchy_registry",
        lambda: (fake_registry, fake_aliases),
    )

    handler = ArgumentQueryHandler()
    response = handler.handle_query(
        query_id="q_auto",
        query_text="How strong is the evidence for saturation > brightness?",
        processing_time_ms=3,
    )

    assert response is not None
    assert response["status"] == "success"
    assert response["summary"]["hierarchy_id"] == "col2_arousal_dimensions"
    assert response["summary"]["ordered_levels"] == ["saturation", "brightness", "hue"]
