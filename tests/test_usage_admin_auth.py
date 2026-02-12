from fastapi.testclient import TestClient

from app.main import app


def test_usage_admin_summary_requires_admin_token(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")

    with TestClient(app) as client:
        r = client.get("/usage/admin/summary")
        assert r.status_code == 401


def test_usage_admin_summary_with_admin_token(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")

    with TestClient(app) as client:
        r = client.get("/usage/admin/summary", headers={"X-Admin-Token": "test-token"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
