import json

from src.cmr.building_eval import evaluate_building
from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper
from src.services.web_of_belief import (
    Belief,
    BeliefStatus,
    Constraint,
    ConstraintType,
    Credence,
    EpistemicLevel,
    create_neuroarchitecture_web,
)
from src.services.web_persistence import WebPersistenceService


def _seed_template(session, display_id: str, series: str, json_path: str) -> None:
    session.add(
        TemplateRecord(
            template_id=f"{display_id}_TEMPLATE_001",
            display_id=display_id,
            name=f"{display_id} Template",
            series=series,
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="organizational",
            maturity="supported",
            calibration_status="partial",
            practical_accessibility="B",
            ecological_validation=False,
            json_path=json_path,
            source_docs="68",
        )
    )


def _seed_master_web(service: WebPersistenceService) -> str:
    web_id = "master:web:accumulated"
    web = create_neuroarchitecture_web()
    web.beliefs.clear()
    web.constraints.clear()

    web.add_belief(
        Belief(
            belief_id="belief:nature:001",
            content="Nature view reduces stress and improves restoration.",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.72, 0.2, n_observations=12),
            theory_id="ART",
            paper_ids=["paper:001"],
        )
    )
    web.add_belief(
        Belief(
            belief_id="belief:stress:001",
            content="Stress reduction increases with restorative cues.",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.66, 0.25, n_observations=9),
            theory_id="SRT",
            paper_ids=["paper:002"],
        )
    )

    link = Constraint(
        constraint_id="constraint:tier2:WX1:001",
        source_id="belief:nature:001",
        target_id="belief:stress:001",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.8,
        bidirectional=False,
        evidence_ids=["paper:001"],
    )
    link.warrant_type = "tier2_theory_link"  # type: ignore[attr-defined]
    link.provenance = json.dumps({"theory_id": "ART", "template_id": "WX1"})  # type: ignore[attr-defined]
    web.add_constraint(link)

    service.save_web(web, web_id, "Master Web", is_master=True)
    return web_id


def _build_env(tmp_path):
    db_path = str(tmp_path / "web_integration.db")
    create_tables(db_path)

    view1_json = tmp_path / "VIEW1.json"
    view1_json.write_text(
        json.dumps(
            {
                "display_id": "VIEW1",
                "causal_links": [
                    {
                        "from_level": "environmental",
                        "from_variable": "nature_view",
                        "to_level": "affective",
                        "to_variable": "stress_reduction",
                        "activity": "reduces stress",
                    }
                ],
                "structural_pattern": "nature view reduces stress",
            }
        ),
        encoding="utf-8",
    )

    wx1_json = tmp_path / "WX1.json"
    wx1_json.write_text(
        json.dumps(
            {
                "display_id": "WX1",
                "inputs_required": [],
                "domain": "W",
            }
        ),
        encoding="utf-8",
    )

    session = get_session(db_path)
    _seed_template(session, "VIEW1", "VIEW", str(view1_json))
    _seed_template(session, "WX1", "W", str(wx1_json))
    session.commit()
    session.close()

    service = WebPersistenceService(db_path)
    master_web_id = _seed_master_web(service)
    return db_path, service, master_web_id


def test_paper_eval_queries_web(tmp_path):
    db_path, service, _ = _build_env(tmp_path)

    result = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "c1",
                "description": "Nature view decreases stress.",
                "iv": "nature_view",
                "dv": "stress_reduction",
                "direction": "decrease",
            }
        ],
        db_path=db_path,
        web_service=service,
    )

    summary = result["web_query_summary"]
    assert summary["query_count"] > 0, "Paper eval made zero web of belief queries"
    serialized_queries = " ".join(item.get("query", "") for item in summary.get("queries", []))
    assert any(term in serialized_queries for term in ("nature", "view", "stress"))


def test_building_eval_queries_web(tmp_path):
    db_path, service, _ = _build_env(tmp_path)

    result = evaluate_building(
        building_context={"target_description": "Integration building"},
        measured_features={},
        occupant_profile={"age": 35},
        db_path=db_path,
        web_service=service,
    )

    summary = result["web_constraint_query_summary"]
    assert summary["query_count"] > 0
    assert any(item.get("template_id") == "WX1" for item in summary.get("queries", []))


def test_staging_links_reachable(tmp_path):
    _, service, master_web_id = _build_env(tmp_path)

    constraints = service.get_constraints_for_web(master_web_id)
    links = [c for c in constraints if getattr(c, "warrant_type", None) == "tier2_theory_link"]
    assert len(links) >= 1

    for link in links[:10]:
        theory_id = getattr(link, "theory_id", None)
        provenance = getattr(link, "provenance", None)
        if not theory_id and provenance:
            try:
                theory_id = json.loads(str(provenance)).get("theory_id")
            except Exception:
                theory_id = None
        assert theory_id, f"Theory link missing theory_id: {link}"


def test_beliefs_have_evidence(tmp_path):
    _, service, master_web_id = _build_env(tmp_path)

    beliefs = service.get_beliefs_for_web(master_web_id)
    empty_count = sum(
        1
        for belief in beliefs
        if not getattr(belief, "evidence", None)
        and not getattr(belief, "source", None)
        and not getattr(belief, "paper_ids", None)
    )
    assert empty_count / max(len(beliefs), 1) < 0.3


def test_constraints_reference_valid_templates(tmp_path):
    db_path, service, master_web_id = _build_env(tmp_path)

    session = get_session(db_path)
    template_ids = {t.display_id for t in session.query(TemplateRecord).all()}
    session.close()

    constraints = service.get_constraints_for_web(master_web_id)
    for constraint in constraints:
        template_id = getattr(constraint, "template_id", None)
        if not template_id:
            provenance = getattr(constraint, "provenance", None)
            if provenance:
                try:
                    template_id = json.loads(str(provenance)).get("template_id")
                except Exception:
                    template_id = None
        if template_id:
            assert template_id in template_ids
