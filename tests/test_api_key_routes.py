"""Tests for API key routes security and behavior."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.db import connect
from app.main import app


def _clear_user_keys(user_id: str) -> None:
    with connect() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM user_api_keys WHERE user_id=?", (user_id,))
        con.commit()


def test_profile_api_keys_requires_admin_token(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
    user_id = "test_keys_auth"
    _clear_user_keys(user_id)

    with TestClient(app) as client:
        r = client.get("/profile/api-keys", params={"user_id": user_id})
        assert r.status_code == 401


def test_profile_api_keys_set_get_list_delete(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
    headers = {"X-Admin-Token": "test-token"}
    user_id = "test_keys_crud"
    _clear_user_keys(user_id)

    with TestClient(app) as client:
        r = client.post(
            "/profile/api-keys",
            headers=headers,
            json={"user_id": user_id, "provider": "openai", "key": "sk-test-12345678"},
        )
        assert r.status_code == 200

        r = client.post(
            "/profile/api-keys",
            headers=headers,
            json={"user_id": user_id, "provider": "gemini", "key": "gm-test-87654321"},
        )
        assert r.status_code == 200

        r = client.get(
            "/profile/api-keys",
            headers=headers,
            params={"user_id": user_id, "provider": "openai"},
        )
        assert r.status_code == 200
        assert r.json()["provider"] == "openai"
        assert "*" in r.json()["key_masked"]

        r = client.get(
            "/profile/api-keys",
            headers=headers,
            params={"user_id": user_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["user_id"] == user_id
        providers = {k["provider"] for k in data["keys"]}
        assert {"openai", "gemini"}.issubset(providers)

        r = client.delete(
            "/profile/api-keys/openai",
            headers=headers,
            params={"user_id": user_id},
        )
        assert r.status_code == 200
        assert r.json()["deleted"] is True

        r = client.get(
            "/profile/api-keys",
            headers=headers,
            params={"user_id": user_id, "provider": "openai"},
        )
        assert r.status_code == 200
        assert r.json()["key_masked"] == ""

    _clear_user_keys(user_id)


def test_legacy_profile_keys_uses_encrypted_storage(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
    headers = {"X-Admin-Token": "test-token"}
    user_id = 42
    _clear_user_keys(str(user_id))

    with TestClient(app) as client:
        # Legacy endpoint also requires admin token.
        r = client.get("/profile/keys", params={"user_id": user_id})
        assert r.status_code == 401

        r = client.post(
            "/profile/keys",
            headers=headers,
            params={"user_id": user_id, "openai_api_key": "sk-legacy-11223344"},
        )
        assert r.status_code == 200

        r = client.get(
            "/profile/keys",
            headers=headers,
            params={"user_id": user_id},
        )
        assert r.status_code == 200
        body = r.json()
        assert "*" in body["openai_api_key"]
        assert body["openai_api_key"] != "sk-legacy-11223344"

    _clear_user_keys(str(user_id))


def test_profile_stub_routes_require_admin_token(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
    headers = {"X-Admin-Token": "test-token"}

    with TestClient(app) as client:
        r = client.get("/profile")
        assert r.status_code == 401

        r = client.get("/profile", headers=headers)
        assert r.status_code == 200

        r = client.patch("/profile", json={"name": "Updated Name"})
        assert r.status_code == 401

        r = client.patch("/profile", headers=headers, json={"name": "Updated Name"})
        assert r.status_code == 200


def test_admin_page_requires_admin_token(monkeypatch):
    monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
    headers = {"X-Admin-Token": "test-token"}

    with TestClient(app) as client:
        r = client.get("/admin")
        assert r.status_code == 401

        r = client.get("/admin", headers=headers)
        assert r.status_code == 200
