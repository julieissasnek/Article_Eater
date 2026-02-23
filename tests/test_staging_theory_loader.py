from __future__ import annotations

import json
from pathlib import Path

from src.cmr.models import CMRStagingTheoryLink, get_session
from src.cmr.staging_theory_loader import load_staging_theory_links


def _write_template(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_load_staging_theory_links_from_template_causal_links(tmp_path: Path) -> None:
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_path / "ae_test.db"

    _write_template(
        templates_dir / "VF3.json",
        {
            "template_id": "SPATIAL_PROPORTIONS_001",
            "display_id": "VF3",
            "name": "Ceiling Height and Processing Style",
            "framework_ids": ["attention_restoration_theory"],
            "causal_links": [
                {
                    "from_variable": "ceiling_height_m",
                    "to_variable": "processing_mode",
                    "from_level": "environmental",
                    "to_level": "cognitive",
                    "maturity": "supported",
                }
            ],
        },
    )

    summary = load_staging_theory_links(
        templates_dir=templates_dir,
        db_path=str(db_path),
        clear_existing=True,
    )

    assert summary["rows_inserted"] == 1
    assert summary["theory_counts"]["ART"] == 1

    session = get_session(str(db_path))
    try:
        rows = session.query(CMRStagingTheoryLink).all()
        assert len(rows) == 1
        assert rows[0].template_display_id == "VF3"
        assert rows[0].from_variable == "ceiling_height_m"
        assert rows[0].to_variable == "processing_mode"
    finally:
        session.close()
