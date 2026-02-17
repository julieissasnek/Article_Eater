from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.cmr import models


def _create_memory_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_cmr_models_crud_cycle():
    session = _create_memory_session()

    template = models.TemplateRecord(
        template_id="CREA4_COLLAB",
        display_id="CREA4",
        name="Collaborative Creativity Architecture",
        series="CREA",
        generation=2,
        dedup_status="active",
        superseded_by=None,
        pe_contribution="organizational",
        maturity="supported",
        calibration_status="substantial",
        practical_accessibility="B",
        ecological_validation=True,
        json_path="data/templates/CREA4_collaborative_creativity_architecture.json",
        source_docs="58,65",
    )
    session.add(template)
    session.commit()

    evaluation = models.CMREvaluation(
        evaluation_type="building",
        target_description="Test lab",
        status="complete",
        building_context={"climate_zone": "3C", "building_type": "research"},
    )
    session.add(evaluation)
    session.commit()

    activation = models.CMRTemplateActivation(
        evaluation_id=evaluation.id,
        template_display_id=template.display_id,
        activation_reason="Test activation",
        inputs={"ceiling_height_m": 3.2},
        outputs={"r_h": 0.4},
        wis_score=72.5,
        wis_confidence=3.5,
        interaction_adjustments=[{"with_template": "CREA2", "factor": 1.1}],
    )
    session.add(activation)

    domain_score = models.CMRDomainScore(
        evaluation_id=evaluation.id,
        domain="A1",
        wis_score=72.5,
        wis_confidence=2.4,
        n_templates_activated=1,
        template_ids=template.display_id,
    )
    session.add(domain_score)

    overall_score = models.CMROverallScore(
        evaluation_id=evaluation.id,
        wis_geometric_mean=70.1,
        wis_confidence=4.0,
        n_domains_assessed=1,
        severe_deficit_domains="",
        data_gaps="",
    )
    session.add(overall_score)

    reduction = models.ReductionClaim(
        tier2_theory="ART",
        tier2_construct="Soft Fascination",
        reduction_type="full",
        template_mappings=[
            {"template_id": template.display_id, "mechanism": "divergent_walk", "coverage": 0.6}
        ],
        irreducible_residual="None",
        confidence="high",
        source_panel="T2-A",
        staging_links_reconciled=5,
        staging_links_total=8,
    )
    session.add(reduction)
    session.commit()

    loaded_evaluation = (
        session.query(models.CMREvaluation)
        .filter_by(target_description="Test lab")
        .one()
    )
    assert loaded_evaluation.status == "complete"
    assert len(loaded_evaluation.template_activations) == 1

    loaded_activation = loaded_evaluation.template_activations[0]
    assert loaded_activation.inputs["ceiling_height_m"] == 3.2
    assert loaded_activation.wis_score == 72.5

    loaded_domain = (
        session.query(models.CMRDomainScore)
        .filter_by(domain="A1")
        .one()
    )
    assert loaded_domain.wis_score == 72.5

    loaded_overall = (
        session.query(models.CMROverallScore)
        .filter_by(evaluation_id=loaded_evaluation.id)
        .one()
    )
    assert loaded_overall.wis_geometric_mean == 70.1

    loaded_claim = (
        session.query(models.ReductionClaim)
        .filter_by(tier2_theory="ART")
        .one()
    )
    assert loaded_claim.reduction_type == "full"
    assert isinstance(loaded_claim.template_mappings, list)
