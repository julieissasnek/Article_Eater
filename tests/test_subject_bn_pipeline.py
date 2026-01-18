import json
from pathlib import Path

from src.services import admin_service


FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str):
    path = FIXTURES / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_rulegraph_v2_bn_export_basic_subject_nodes_and_edges():
    events = _load("subject_bn_fixture_events.json")
    overrides = _load("subject_bn_fixture_overrides.json")
    export = admin_service.build_rulegraph_v2_bn_export(events, overrides, payload={})

    # We expect three rules in total (R1, R2, R3)
    assert export["meta"]["rules_count"] == 3

    nodes = {n["id"]: n for n in export["nodes"]}
    edges = export["edges"]
    rules = export["rules"]

    # Subject attribute nodes are present and correctly typed
    assert "age_band:26-40" in nodes
    assert nodes["age_band:26-40"]["type"] == "subject_age_band"

    assert "culture_region:India" in nodes
    assert nodes["culture_region:India"]["type"] == "subject_culture_region"

    # R2 should reflect the override fixture (clinical population and culture region)
    r2 = next(r for r in rules if r["rule_id"] == "R2")
    scope = r2["subject_scope"]
    assert scope["clinical_status"]["population"] == "anxiety"
    assert scope["culture"]["region"] == "India"
    trait_names = {t["name"] for t in scope.get("traits_measured") or []}
    assert "trait_anxiety" in trait_names

    # Edges use from/to/type and include a moderator edge from the override
    r2_node_id = r2["rule_node_id"]
    assert any(
        e["from"] == "culture_region:India"
        and e["to"] == r2_node_id
        and e["type"] == "subject_scope"
        for e in edges
    )
    assert any(
        e["from"] == "mod:noise|urban"
        and e["to"] == r2_node_id
        and e["type"] == "subject_moderator"
        for e in edges
    )


def test_build_rulegraph_v2_bn_export_filters_by_age_band():
    events = _load("subject_bn_fixture_events.json")
    overrides = _load("subject_bn_fixture_overrides.json")
    export = admin_service.build_rulegraph_v2_bn_export(
        events,
        overrides,
        payload={"age_band": "41-65"},
    )

    # Only P2/R3 should remain when we filter on 41-65
    assert export["meta"]["rules_count"] == 1
    rules = export["rules"]
    assert len(rules) == 1
    assert rules[0]["rule_id"] == "R3"
def test_build_rulegraph_v2_bn_export_filters_by_trait_and_text():
    events = _load("subject_bn_fixture_events.json")
    overrides = _load("subject_bn_fixture_overrides.json")
    export = admin_service.build_rulegraph_v2_bn_export(
        events,
        overrides,
        payload={
            "trait": "sensation_seeking",
            "text_filter": "bright light",
        },
    )

    # Only the R2 rule should match this combination
    assert export["meta"]["rules_count"] == 1
    rules = export["rules"]
    assert len(rules) == 1
    assert rules[0]["rule_id"] == "R2"
    # Ensure trait node and edge exist in the filtered export
    nodes = {n["id"]: n for n in export["nodes"]}
    edges = export["edges"]
    assert "trait:sensation_seeking" in nodes
    r2_node_id = rules[0]["rule_node_id"]
    assert any(
        e["from"] == "trait:sensation_seeking"
        and e["to"] == r2_node_id
        and e["type"] == "subject_scope"
        for e in edges
    )
