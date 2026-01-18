"""Centralised configuration for Article Eater.

This module provides a single `get_settings()` function that reads from
environment variables (and optionally a `config/.env` file) and exposes a
strongly-typed Settings object.

All other modules should import configuration from here rather than
calling `os.getenv` directly.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import pathlib
from functools import lru_cache
from typing import Literal


ROOT = pathlib.Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / "config" / ".env"


def _load_env_file_if_present() -> None:
    """Load simple KEY=VALUE lines from config/.env into os.environ.

    This is a tiny replacement for python-dotenv so that we do not add
    another runtime dependency. Lines starting with `#` are ignored.
    """
    if not ENV_FILE.exists():
        return
    try:
        for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Fail silently; misconfigured .env should not prevent startup.
        return


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


@dataclass(frozen=True)
class Settings:
    env: Literal["dev", "staging", "prod"]
    llm_provider: str
    graph_backend: Literal["jsonl", "neo4j"]
    secret_key: str
    session_cookie_secure: bool
    log_level: str

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.env == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings object.

    Precedence:
    1. Environment variables (possibly from `config/.env`)
    2. Sensible defaults for local development
    """
    _load_env_file_if_present()

    env = os.getenv("AE_ENV", "dev").lower()
    if env not in {"dev", "staging", "prod"}:
        env = "dev"

    graph_backend = os.getenv("AE_GRAPH_BACKEND", "jsonl").lower()
    if graph_backend not in {"jsonl", "neo4j"}:
        graph_backend = "jsonl"

    secret_key = os.getenv("AE_SECRET_KEY", "DEV-ONLY-SECRET-KEY-CHANGE-ME")
    llm_provider = os.getenv("AE_LLM_PROVIDER", "fake")
    session_cookie_secure = _get_bool("AE_SESSION_COOKIE_SECURE", default=(env == "prod"))
    log_level = os.getenv("AE_LOG_LEVEL", "INFO").upper()

    return Settings(
        env=env,  # type: ignore[arg-type]
        llm_provider=llm_provider,
        graph_backend=graph_backend,  # type: ignore[arg-type]
        secret_key=secret_key,
        session_cookie_secure=session_cookie_secure,
        log_level=log_level,
    )
