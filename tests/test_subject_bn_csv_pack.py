
import json
from pathlib import Path

from src.services.admin_service import build_rulegraph_v2_bn_export
from src.tools import bn_export_to_csv


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_subject_bn_export_roundtrip_to_csv(tmp_path):
    events_path = FIXTURES_DIR / "subject_bn_fixture_events.json"
    overrides_path = FIXTURES_DIR / "subject_bn_fixture_overrides.json"

    events = json.loads(events_path.read_text(encoding="utf-8"))
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    export = build_rulegraph_v2_bn_export(events, overrides, payload={})

    # Write export JSON to a temp file
    export_json = tmp_path / "export.json"
    export_json.write_text(json.dumps(export), encoding="utf-8")

    # Run the CSV writer
    out_dir = tmp_path / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    bn_export_to_csv.write_nodes_csv(export, out_dir)
    bn_export_to_csv.write_edges_csv(export, out_dir)
    bn_export_to_csv.write_rules_csv(export, out_dir)

    # Ensure CSVs were created and include expected headers
    nodes_csv = (out_dir / "nodes.csv").read_text(encoding="utf-8")
    edges_csv = (out_dir / "edges.csv").read_text(encoding="utf-8")
    rules_csv = (out_dir / "rules.csv").read_text(encoding="utf-8")

    assert "id,type,label,paper_id" in nodes_csv.splitlines()[0]
    assert "from,to,type" in edges_csv.splitlines()[0]
    assert "rule_id,paper_id,age_bands,traits,rule_text" in rules_csv.splitlines()[0]
