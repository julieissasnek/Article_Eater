import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.cmr.models import (
    Base,
    CMRDomainScore,
    CMREvaluation,
    CMROverallScore,
    CMRTemplateActivation,
    ReductionClaim,
    TemplateRecord,
)


def _session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_cmr_evaluation_crud():
    session = _session()
    record = CMREvaluation(
        evaluation_type="building",
        target_description="Salk Institute pilot",
        status="in_progress",
        building_context={"building_type": "lab", "climate": "temperate"},
    )
    session.add(record)
    session.commit()

    loaded = session.query(CMREvaluation).filter_by(evaluation_type="building").one()
    assert loaded.target_description == "Salk Institute pilot"
    assert loaded.building_context["building_type"] == "lab"


def test_cmr_template_activation_crud():
    session = _session()
    template = TemplateRecord(
        template_id="VISUAL_FORM_CEILING_HEIGHT_001",
        display_id="VF3",
        name="Ceiling Height and Cognitive Mode",
        series="VF",
        generation=2,
        dedup_status="active",
        superseded_by=None,
        pe_contribution="predictive",
        maturity="supported",
        calibration_status="partial",
        practical_accessibility="B",
        ecological_validation=True,
        json_path="data/templates/VF3.json",
        source_docs="39,64",
    )
    evaluation = CMREvaluation(
        evaluation_type="building",
        target_description="Pilot",
        status="complete",
        building_context={"building_type": "office"},
    )
    session.add_all([template, evaluation])
    session.commit()

    activation = CMRTemplateActivation(
        evaluation_id=evaluation.id,
        template_display_id="VF3",
        activation_reason="Ceiling and area provided",
        inputs={"ceiling_height_m": 3.2, "floor_area_m2": 40.0},
        outputs={"zone": "liberating", "r_h": 0.506},
        wis_score=82.0,
        wis_confidence=10.0,
        interaction_adjustments=[{"with_template": "CREA2", "factor": 0.84}],
    )
    session.add(activation)
    session.commit()

    loaded = session.query(CMRTemplateActivation).filter_by(template_display_id="VF3").one()
    assert loaded.inputs["ceiling_height_m"] == 3.2
    assert loaded.outputs["zone"] == "liberating"
    assert loaded.wis_score == 82.0


def test_cmr_domain_score_crud():
    session = _session()
    evaluation = CMREvaluation(
        evaluation_type="building",
        target_description="Domain aggregation run",
        status="complete",
        building_context={},
    )
    session.add(evaluation)
    session.commit()

    domain = CMRDomainScore(
        evaluation_id=evaluation.id,
        domain="A4",
        wis_score=71.5,
        wis_confidence=9.0,
        n_templates_activated=3,
        template_ids="VF1,VF2,VF3",
    )
    session.add(domain)
    session.commit()

    loaded = session.query(CMRDomainScore).filter_by(domain="A4").one()
    assert loaded.aggregation_method == "weighted_average"
    assert loaded.weight_basis == "calibration_confidence"
    assert loaded.n_templates_activated == 3


def test_cmr_overall_score_crud_and_severe_deficits():
    session = _session()
    evaluation = CMREvaluation(
        evaluation_type="building",
        target_description="Overall run",
        status="complete",
        building_context={},
    )
    session.add(evaluation)
    session.commit()

    overall = CMROverallScore(
        evaluation_id=evaluation.id,
        wis_geometric_mean=36.7,
        wis_confidence=12.0,
        n_domains_assessed=2,
        severe_deficit_domains="A3",
        data_gaps="A9",
    )
    session.add(overall)
    session.commit()

    loaded = session.query(CMROverallScore).filter_by(evaluation_id=evaluation.id).one()
    assert loaded.wis_geometric_mean == 36.7
    assert loaded.severe_deficit_domains == "A3"
    assert loaded.data_gaps == "A9"


def test_reduction_claim_crud():
    session = _session()
    claim = ReductionClaim(
        tier2_theory="ART",
        tier2_construct="Soft Fascination",
        reduction_type="partial",
        template_mappings=[
            {
                "template_id": "VIEW1",
                "mechanism": "restoration",
                "coverage": 0.72,
            }
        ],
        irreducible_residual="Aesthetic appraisal component",
        confidence="moderate",
        source_panel="T2-A",
        staging_links_reconciled=1251,
        staging_links_total=1251,
    )
    session.add(claim)
    session.commit()

    loaded = session.query(ReductionClaim).filter_by(tier2_theory="ART").one()
    assert loaded.tier2_construct == "Soft Fascination"
    assert loaded.template_mappings[0]["coverage"] == 0.72
    assert loaded.staging_links_total == 1251


def test_migration_021_creates_expected_tables(tmp_path: Path):
    db_path = tmp_path / "cmr.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript("CREATE TABLE IF NOT EXISTS templates (display_id TEXT PRIMARY KEY);")

    migration_sql = Path("migrations/021_add_cmr_models.sql").read_text(encoding="utf-8")
    conn.executescript(migration_sql)
    conn.commit()

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    assert "cmr_evaluations" in tables
    assert "cmr_template_activations" in tables
    assert "cmr_domain_scores" in tables
    assert "cmr_overall_scores" in tables
    assert "reduction_claims" in tables
