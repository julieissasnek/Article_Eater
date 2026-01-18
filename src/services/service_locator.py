
"""Simple service locator for pluggable backends.

For now it only exposes get_graph_service(), but can be extended
later to return real Neo4j-backed implementations.
"""
from __future__ import annotations
from typing import Optional
from .graph_service_fallback import JSONLGraphStore

_graph_service: Optional[JSONLGraphStore] = None

def get_graph_service() -> JSONLGraphStore:
    global _graph_service
    if _graph_service is None:
        _graph_service = JSONLGraphStore()
    return _graph_service
