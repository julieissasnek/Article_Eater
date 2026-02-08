"""
Tests for App Main Router Wiring
================================

Ensures that critical routers are actually mounted in app.main,
preventing the "green tests with broken deployment" anti-pattern.

Per ChatGPT ruthless review (2026-01-22):
- Route tests that create their own FastAPI app can pass
  even when app.main doesn't mount those routes
- This single integration test prevents that regression

Date: January 22, 2026
"""

import pytest


def test_critical_routes_mounted():
    """
    Verify query/reports/ingestion routes are accessible from app.main.

    This is the single "wiring test" recommended by the panel review.
    If this test fails, the API is not exposing required endpoints.
    """
    from app.main import app

    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    # Query routes must be mounted
    query_paths = [p for p in paths if "/query" in p]
    assert len(query_paths) > 0, (
        "Query routes not mounted in app.main! "
        "Expected paths containing '/query' but found none. "
        "Check that query_router is included with include_router()."
    )

    # Reports routes must be mounted
    reports_paths = [p for p in paths if "/reports" in p]
    assert len(reports_paths) > 0, (
        "Reports routes not mounted in app.main! "
        "Expected paths containing '/reports' but found none. "
        "Check that reports_router is included with include_router()."
    )

    # Ingestion routes must be mounted
    ingestion_paths = [p for p in paths if "/ingestion" in p]
    assert len(ingestion_paths) > 0, (
        "Ingestion routes not mounted in app.main! "
        "Expected paths containing '/ingestion' but found none. "
        "Check that ingestion_router is included with include_router()."
    )

    # Web of belief routes must be mounted
    web_paths = [p for p in paths if "/web" in p]
    assert len(web_paths) > 0, (
        "Web of belief routes not mounted in app.main! "
        "Expected paths containing '/web' but found none. "
        "Check that web_of_belief_router is included with include_router()."
    )


def test_openapi_tags_present():
    """
    Verify OpenAPI documentation includes expected tags.

    Tags help organize the API documentation and their presence
    confirms the routers were mounted with proper metadata.
    """
    from app.main import app

    openapi_schema = app.openapi()
    tags = openapi_schema.get("tags", [])
    tag_names = [t.get("name") for t in tags]

    # Check for key tags (some may be in openapi_tags, others added by routers)
    expected_in_schema = ["health", "jobs", "library"]
    for tag in expected_in_schema:
        assert tag in tag_names, f"Expected tag '{tag}' not found in OpenAPI schema"


def test_health_endpoint_accessible():
    """
    Verify /healthz endpoint is accessible.

    This is a basic smoke test that the app can be instantiated
    and responds to requests.
    """
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"


def test_cors_no_wildcard_with_credentials():
    """
    Verify CORS is not misconfigured with wildcard + credentials.

    Per security review: allow_origins="*" with allow_credentials=True
    is insecure and causes inconsistent browser behavior.
    """
    from app.main import app

    # Find CORS middleware
    cors_middleware = None
    for middleware in app.user_middleware:
        if "CORSMiddleware" in str(middleware):
            cors_middleware = middleware
            break

    if cors_middleware is not None:
        # Check kwargs for the problematic pattern
        kwargs = cors_middleware.kwargs if hasattr(middleware, 'kwargs') else {}
        allow_origins = kwargs.get("allow_origins", [])
        allow_credentials = kwargs.get("allow_credentials", False)

        if allow_credentials:
            assert "*" not in allow_origins, (
                "CORS misconfiguration: allow_origins contains '*' "
                "while allow_credentials=True. This is insecure and "
                "causes inconsistent browser behavior. Remove '*' from "
                "allow_origins or set allow_credentials=False."
            )
