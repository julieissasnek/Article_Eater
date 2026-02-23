"""
Health Check API Routes

Provides system health and readiness endpoints for monitoring.

Endpoints:
    GET /health         - Basic health check (fast)
    GET /health/ready   - Readiness check (validates subsystems)
    GET /health/live    - Liveness check (is the process running)

Author: Claude Code (Feb 23, 2026)
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

# Project paths
ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT / "data" / "templates"


router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    """Basic health status response."""

    status: str = Field(..., description="Overall status: ok, degraded, or unhealthy")
    timestamp: str = Field(..., description="ISO timestamp of health check")
    version: str = Field(default="1.0.0", description="API version")


class SubsystemStatus(BaseModel):
    """Status of a single subsystem."""

    name: str
    status: str  # ok, degraded, unhealthy
    latency_ms: float | None = None
    details: dict[str, Any] | None = None


class ReadinessResponse(BaseModel):
    """Detailed readiness check response."""

    status: str = Field(..., description="Overall status")
    timestamp: str
    subsystems: list[SubsystemStatus]
    checks_passed: int
    checks_failed: int


def _check_database() -> SubsystemStatus:
    """Check database connectivity."""
    import os

    db_path_env = os.getenv("AE_DB_PATH")
    db_path = Path(db_path_env) if db_path_env else ROOT / "ae.db"

    start = time.perf_counter()
    try:
        if not db_path.exists():
            return SubsystemStatus(
                name="database",
                status="unhealthy",
                details={"error": f"Database not found: {db_path}"},
            )

        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.execute("SELECT 1")
        conn.close()
        latency = (time.perf_counter() - start) * 1000

        return SubsystemStatus(
            name="database",
            status="ok",
            latency_ms=round(latency, 2),
            details={"path": str(db_path)},
        )
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return SubsystemStatus(
            name="database",
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)},
        )


def _check_templates() -> SubsystemStatus:
    """Check templates directory."""
    start = time.perf_counter()
    try:
        if not TEMPLATES_DIR.exists():
            return SubsystemStatus(
                name="templates",
                status="unhealthy",
                details={"error": "Templates directory not found"},
            )

        template_count = len(list(TEMPLATES_DIR.glob("*.json")))
        latency = (time.perf_counter() - start) * 1000

        if template_count == 0:
            return SubsystemStatus(
                name="templates",
                status="unhealthy",
                latency_ms=round(latency, 2),
                details={"error": "No templates found"},
            )

        # Count calibrated templates
        calibrated = 0
        for f in TEMPLATES_DIR.glob("*.json"):
            try:
                import json

                data = json.loads(f.read_text())
                status = data.get("calibration_status") or data.get("status")
                if status == "calibrated" or data.get("calibrated"):
                    calibrated += 1
            except Exception:
                pass

        return SubsystemStatus(
            name="templates",
            status="ok",
            latency_ms=round(latency, 2),
            details={
                "total": template_count,
                "calibrated": calibrated,
                "path": str(TEMPLATES_DIR),
            },
        )
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return SubsystemStatus(
            name="templates",
            status="unhealthy",
            latency_ms=round(latency, 2),
            details={"error": str(e)},
        )


def _check_schemas() -> SubsystemStatus:
    """Check schemas directory."""
    schemas_dir = ROOT / "schemas"
    start = time.perf_counter()

    if not schemas_dir.exists():
        return SubsystemStatus(
            name="schemas",
            status="degraded",
            details={"error": "Schemas directory not found"},
        )

    schema_count = len(list(schemas_dir.glob("*.json")))
    latency = (time.perf_counter() - start) * 1000

    return SubsystemStatus(
        name="schemas",
        status="ok",
        latency_ms=round(latency, 2),
        details={"count": schema_count},
    )


@router.get("", response_model=HealthStatus)
@router.get("/", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """
    Basic health check.

    Returns immediately with basic status. Use /health/ready for
    detailed subsystem checks.
    """
    return HealthStatus(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/live", response_model=HealthStatus)
async def liveness_check() -> HealthStatus:
    """
    Liveness probe.

    Returns 200 if the process is running. Used by orchestrators
    (k8s, docker) to detect hung processes.
    """
    return HealthStatus(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness probe with subsystem checks.

    Validates all subsystems and returns detailed status.
    Returns 200 even if some subsystems are degraded (check response body).
    """
    subsystems = [
        _check_database(),
        _check_templates(),
        _check_schemas(),
    ]

    passed = sum(1 for s in subsystems if s.status == "ok")
    failed = sum(1 for s in subsystems if s.status == "unhealthy")

    # Determine overall status
    if failed > 0:
        overall = "unhealthy"
    elif any(s.status == "degraded" for s in subsystems):
        overall = "degraded"
    else:
        overall = "ok"

    return ReadinessResponse(
        status=overall,
        timestamp=datetime.now(timezone.utc).isoformat(),
        subsystems=subsystems,
        checks_passed=passed,
        checks_failed=failed,
    )
