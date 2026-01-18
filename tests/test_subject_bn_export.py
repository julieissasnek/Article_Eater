
import json
from pathlib import Path

from src.services.admin_service import build_rulegraph_v2_bn_export


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_subject_bn_export_structure_and_subject_nodes(tmp_path):
    events_path = FIXTURES_DIR / "subject_bn_fixture_events.json"
    overrides_path = FIXTURES_DIR / "subject_bn_fixture_overrides.json"

    events = json.loads(events_path.read_text(encoding="utf-8"))
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    payload = {
        "paper_id": "",
        "text_filter": "",
        "age_band": "",
        "trait": "",
    }

    export = build_rulegraph_v2_bn_export(events, overrides, payload)

    # Basic sanity: nodes/edges/rules exist
    assert export["nodes"], "Expected at least one node in BN export"
    assert export["edges"], "Expected at least one edge in BN export"
    assert export["rules"], "Expected at least one rule in BN export"

    node_ids = {n["id"] for n in export["nodes"]}
    edge_tuples = {(e["from"], e["to"], e["type"]) for e in export["edges"]}

    # Subject attribute nodes
    assert "age_band:26-40" in node_ids
    assert "age_band:18-25" in node_ids
    assert "culture_region:India" in node_ids
    assert "culture_region:North_America" in node_ids or "culture_region:Western_Europe" in node_ids

    # Moderator nodes
    assert any(n.startswith("mod:lighting|") or n.startswith("mod:complexity|") for n in node_ids)

    # Rule nodes
    assert any(n.startswith("rule:P1:") for n in node_ids)
    assert any(n.startswith("rule:P2:") for n in node_ids)

    # Edges use the expected (from, to, type) schema
    assert all(len(t) == 3 for t in edge_tuples)
    assert all(t[2] in {"subject_scope", "subject_moderator"} for t in edge_tuples)

    # Check that at least one subject-moderator edge exists
    assert any(t[2] == "subject_moderator" for t in edge_tuples)

def test_subject_bn_export_includes_metadata(tmp_path):
    events_path = FIXTURES_DIR / "subject_bn_fixture_events.json"
    overrides_path = FIXTURES_DIR / "subject_bn_fixture_overrides.json"

    events = json.loads(events_path.read_text(encoding="utf-8"))
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    payload = {
        "paper_id": "",
        "text_filter": "",
        "age_band": "",
        "trait": "",
    }

    export = build_rulegraph_v2_bn_export(events, overrides, payload)

    assert export.get("bn_version"), "Expected bn_version in BN export metadata"
    assert export.get("generator") == "article_eater_rulegraph_v2"
