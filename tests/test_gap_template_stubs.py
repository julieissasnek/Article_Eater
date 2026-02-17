import json

from scripts.ensure_gap_template_stubs import GAP_TEMPLATE_IDS, ensure_gap_template_stubs
from src.cmr.models import TemplateRecord, get_session


def test_ensure_gap_template_stubs_creates_missing_and_upserts_db(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Seed one existing file to verify update path.
    (templates_dir / "T4.json").write_text(
        json.dumps(
            {
                "template_id": "T4_EXISTING_001",
                "display_id": "T4",
                "name": "Existing T4",
            }
        ),
        encoding="utf-8",
    )

    db_path = str(tmp_path / "gap_templates.db")
    result = ensure_gap_template_stubs(templates_dir, db_path)
    assert result["gap_templates_processed"] == 10
    assert result["db_inserts"] + result["db_updates"] == 10

    for display_id in GAP_TEMPLATE_IDS:
        path = templates_dir / f"{display_id}.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["display_id"] == display_id
        assert data["dedup_status"] == "gap"
        assert "gap_stub_note" in data
        for required in (
            "pe_contribution",
            "practical_accessibility",
            "dedup_status",
            "generation",
            "ecological_validation",
        ):
            assert required in data

    session = get_session(db_path)
    try:
        count = (
            session.query(TemplateRecord)
            .filter(TemplateRecord.display_id.in_(GAP_TEMPLATE_IDS))
            .count()
        )
        assert count == 10
    finally:
        session.close()

