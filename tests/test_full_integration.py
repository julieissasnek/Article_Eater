"""
Full integration tests for Article_Eater integration surfaces.

Covers:
1. API health and endpoint contract checks
2. Gap -> evidence -> belief closure cycle
3. Ingestion route + integration route interoperability
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.ingestion import _papers, set_web
from src.services.cross_layer_query import CrossLayerQueryService
from src.services.edge_justification import EdgeJustificationService
from src.services.gap_predictor import GapPredictor
from src.services.web_of_belief import Belief, Credence, EpistemicLevel, SourceDepth, WebOfBelief


@dataclass
class _StubAccumulator:
    web: WebOfBelief

    def get_master_web(self):
        return self.web, None


@pytest.fixture
def integration_context(monkeypatch):
    """Create a shared in-memory web and patch singleton accessors."""
    import src.services.cross_layer_query as cross_module
    import src.services.edge_justification as edge_module
    import src.services.gap_predictor as gap_module
    import src.services.web_accumulator as accumulator_module

    web = WebOfBelief()
    web.add_belief(
        Belief(
            belief_id="b_empirical_noise_stress",
            content="Office noise increases stress in open-plan workplaces.",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.72, uncertainty=0.18),
            environment_id="sensory.noise",
            outcome_id="stress",
            paper_ids=["paper_seed_001"],
            source_depth=SourceDepth.ABSTRACT,
        )
    )

    set_web(web)
    _papers.clear()

    edge_service = EdgeJustificationService(web=web)
    gap_predictor = GapPredictor(web=web, edge_justification_service=edge_service)
    cross_service = CrossLayerQueryService(web=web)

    monkeypatch.setattr(edge_module, "get_edge_justification_service", lambda: edge_service)
    monkeypatch.setattr(gap_module, "get_gap_predictor", lambda: gap_predictor)
    monkeypatch.setattr(cross_module, "get_cross_layer_service", lambda: cross_service)
    monkeypatch.setattr(accumulator_module, "WebAccumulator", lambda: _StubAccumulator(web))

    with TestClient(app) as client:
        yield client, web

    _papers.clear()
    set_web(WebOfBelief())


def test_integration_endpoints_respond(integration_context):
    client, _ = integration_context

    health = client.get("/api/v1/integration/health")
    assert health.status_code == 200
    health_data = health.json()
    assert "status" in health_data
    assert "services" in health_data

    gaps = client.get("/api/v1/integration/gaps", params={"max_gaps": 10, "pretty": False})
    assert gaps.status_code == 200
    gaps_data = gaps.json()
    assert "n_gaps" in gaps_data
    assert "gaps" in gaps_data

    stats = client.get("/api/v1/integration/query/statistics")
    assert stats.status_code == 200
    stats_data = stats.json()
    assert "total_beliefs" in stats_data

    web_state = client.get("/api/v1/integration/web/state")
    assert web_state.status_code == 200
    web_state_data = web_state.json()
    assert web_state_data["n_beliefs"] >= 1


def test_gap_to_evidence_to_belief_cycle(integration_context):
    client, web = integration_context

    before = client.get("/api/v1/integration/gaps/mechanism")
    assert before.status_code == 200
    before_data = before.json()
    assert before_data["n_gaps"] >= 1

    # Add theoretical explanation for the same environment->outcome pair.
    web.add_belief(
        Belief(
            belief_id="b_theory_noise_stress",
            content="Attention restoration theory explains why noise elevates stress.",
            level=EpistemicLevel.THEORETICAL,
            credence=Credence(value=0.66, uncertainty=0.22),
            environment_id="sensory.noise",
            outcome_id="stress",
            theory_id="theory.ART",
            paper_ids=["paper_seed_002"],
            source_depth=SourceDepth.ABSTRACT,
        )
    )

    after = client.get("/api/v1/integration/gaps/mechanism")
    assert after.status_code == 200
    after_data = after.json()
    assert after_data["n_gaps"] == 0


def test_ingestion_and_stats_work_with_integration_state(integration_context):
    client, _ = integration_context

    ingest = client.post(
        "/api/v1/ingestion/paper",
        json={
            "paper": {
                "paper_id": "paper_ingest_001",
                "title": "Daylight and workplace wellbeing",
                "source_depth": "abstract",
            },
            "beliefs": [
                {
                    "content": "Observed daylight variation across open-plan offices.",
                    "level": "observation",
                    "outcome_id": "wellbeing",
                    "source_depth": "abstract",
                }
            ],
        },
    )
    assert ingest.status_code == 200

    stats = client.get("/api/v1/ingestion/stats")
    assert stats.status_code == 200
    data = stats.json()
    assert data["total_papers"] >= 1
    assert data["total_beliefs"] >= 1
