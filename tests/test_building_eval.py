import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.cmr import models
from src.cmr.building_eval import evaluate_building


def _create_memory_session():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def _insert_template(session):
    template = models.TemplateRecord(
        template_id="L1_LIGHT",
        display_id="L1",
        name="Luminance Balance",
        series="L",
        generation=2,
        dedup_status="active",
        superseded_by=None,
        pe_contribution="organizational",
        maturity="supported",
        calibration_status="substantial",
        practical_accessibility="B",
        ecological_validation=False,
        json_path="data/templates/L1_luminance_balance.json",
        source_docs="49",
    )
    session.add(template)
    session.commit()
    return template


def test_evaluate_building_returns_overall_wis():
    session = _create_memory_session()
    template = _insert_template(session)

    report = evaluate_building(
        building_context={"building_name": "Test Lab", "climate_zone": "3C"},
        measured_features={"ceiling_height_m": 3.2, "floor_area_m2": 25.0},
        occupant_profile={"age": 35},
        session=session,
    )

    assert report["overall_wis"] == pytest.approx(50.0, abs=30.0)
    assert any(score["domain"] == template.series for score in report["domain_scores"])
    assert "data_gaps" in report
