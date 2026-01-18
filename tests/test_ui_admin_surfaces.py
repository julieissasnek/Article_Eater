from fastapi.testclient import TestClient
from app.main import app
from src.services import admin_service

class DummyProc:
    def __init__(self, returncode: int = 0, stdout: str = "ok\n", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

def test_ui_config_shape():
    """/ui/config should expose basic flags with the expected shape."""
    c = TestClient(app)
    r = c.get("/ui/config")
    assert r.status_code == 200
    data = r.json()
    assert "demo_mode" in data
    assert "engine_use_mocks" in data
    assert "eager" in data
    assert isinstance(data["demo_mode"], bool)
    assert isinstance(data["engine_use_mocks"], bool)
    assert isinstance(data["eager"], dict)

def test_run_v2_smoke_endpoint(monkeypatch):
    """/api/admin/run_v2_smoke should return a well-formed JSON payload.

    We monkeypatch subprocess.run so the test does not depend on the
    full offline v2 pipeline script, and we set AE_ADMIN_TOKEN so the
    admin guard will allow the request.
    """
    # Ensure admin guard can succeed
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")

    # Patch subprocess.run used inside admin_service.run_v2_smoke
    def fake_run(cmd, capture_output=True, text=True, check=False):
        return DummyProc(returncode=0, stdout="v2 smoke ok\n", stderr="")

    monkeypatch.setattr(admin_service.subprocess, "run", fake_run)

    c = TestClient(app)
    r = c.post("/api/admin/run_v2_smoke", headers={"X-Admin-Token": "test-token"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") in {"ok", "failed", "error"}
    assert "returncode" in data
    assert "stdout" in data
    assert "stderr" in data
