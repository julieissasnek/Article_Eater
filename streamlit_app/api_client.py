"""
Article Eater V23 — API Client
Sprint 3.0.1 — 2026-02-08

Client for connecting Streamlit interface to FastAPI backend.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests.exceptions import RequestException, Timeout

from config import API_BASE_URL, API_VERSION

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query types based on Pearl's ladder + Bates extensions."""
    WHAT = "what"
    WHY = "why"
    COMPARE = "compare"
    GAPS = "gaps"
    CONTRADICT = "contradict"
    CONTINGENT = "contingent"
    HOW_CONFIDENT = "how_confident"
    RELATED = "related"
    TRENDING = "trending"
    CANONICAL = "canonical"


class ResponseMode(Enum):
    """Response depth modes per Simon's progressive disclosure."""
    QUICK = "quick"        # Headline only
    STANDARD = "standard"  # Headline + summary
    DEEP = "deep"          # Full trace


@dataclass
class QueryRequest:
    """Request for a natural language query."""
    query: str
    mode: str = "standard"
    include_scope: bool = True
    include_practitioner_implications: bool = True
    max_evidence: int = 10
    user_type: Optional[str] = None


@dataclass
class BeliefSummary:
    """Summary of a belief for display."""
    id: str
    content: str
    credence: float
    status: str
    level: str
    theory: Optional[str] = None
    sources_count: int = 0
    constraints_count: int = 0


@dataclass
class QueryResult:
    """Result of a query with progressive disclosure structure."""
    query: str
    query_type: str
    headline: str
    summary: Optional[Dict[str, Any]] = None
    detail: Optional[Dict[str, Any]] = None
    practical_implications: Optional[List[str]] = None
    scope_conditions: Optional[Dict[str, str]] = None
    caveats: Optional[List[str]] = None
    key_sources: Optional[List[str]] = None
    related_beliefs: Optional[List[BeliefSummary]] = None


@dataclass
class SystemStats:
    """System-wide statistics."""
    total_beliefs: int
    total_constraints: int
    total_papers: int
    total_communities: int
    overall_coherence: float
    average_credence: float
    contested_beliefs: int
    stub_beliefs: int


class ArticleEaterClient:
    """Client for Article Eater API."""

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_version = API_VERSION
        self.timeout = timeout
        self.session = requests.Session()

    def _url(self, endpoint: str) -> str:
        """Construct full API URL."""
        return f"{self.base_url}/api/{self.api_version}/{endpoint.lstrip('/')}"

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request."""
        try:
            response = self.session.get(
                self._url(endpoint),
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Timeout:
            logger.error(f"Timeout calling {endpoint}")
            raise
        except RequestException as e:
            logger.error(f"Error calling {endpoint}: {e}")
            raise

    def _post(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request."""
        try:
            response = self.session.post(
                self._url(endpoint),
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Timeout:
            logger.error(f"Timeout calling {endpoint}")
            raise
        except RequestException as e:
            logger.error(f"Error calling {endpoint}: {e}")
            raise

    # =========================================================================
    # Query Operations
    # =========================================================================

    def execute_query(self, request: QueryRequest) -> QueryResult:
        """Execute a natural language query."""
        try:
            data = self._post("query/search", asdict(request))
            return QueryResult(
                query=request.query,
                query_type=data.get("query_type", "WHAT"),
                headline=data.get("headline", "No results found"),
                summary=data.get("summary"),
                detail=data.get("detail"),
                practical_implications=data.get("practical_implications"),
                scope_conditions=data.get("scope_conditions"),
                caveats=data.get("caveats"),
                key_sources=data.get("key_sources"),
            )
        except RequestException:
            # Return placeholder for offline/demo mode
            return self._demo_query_result(request.query)

    def parse_query(self, query: str) -> Dict:
        """Parse a natural language query into structured form."""
        try:
            return self._post("query/parse", {"query": query})
        except RequestException:
            return {"query_type": "WHAT", "entities": [], "confidence": 0.0}

    def get_query_suggestions(self, partial: str) -> List[str]:
        """Get query suggestions based on partial input."""
        try:
            data = self._get("query/suggestions", {"partial": partial})
            return data.get("suggestions", [])
        except RequestException:
            return []

    # =========================================================================
    # Belief Operations
    # =========================================================================

    def get_beliefs(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[List[str]] = None,
        level: Optional[List[str]] = None,
        min_credence: float = 0.0,
        search: Optional[str] = None
    ) -> List[BeliefSummary]:
        """Get beliefs with filtering and pagination."""
        params = {
            "limit": limit,
            "offset": offset,
            "min_credence": min_credence,
        }
        if status:
            params["status"] = ",".join(status)
        if level:
            params["level"] = ",".join(level)
        if search:
            params["search"] = search

        try:
            data = self._get("beliefs", params)
            return [BeliefSummary(**b) for b in data.get("beliefs", [])]
        except RequestException:
            return self._demo_beliefs()

    def get_belief(self, belief_id: str) -> Optional[Dict]:
        """Get detailed information about a specific belief."""
        try:
            return self._get(f"beliefs/{belief_id}")
        except RequestException:
            return None

    def get_belief_constraints(self, belief_id: str) -> List[Dict]:
        """Get constraints for a belief."""
        try:
            data = self._get(f"beliefs/{belief_id}/constraints")
            return data.get("constraints", [])
        except RequestException:
            return []

    def get_belief_evidence(self, belief_id: str) -> List[Dict]:
        """Get evidence sources for a belief."""
        try:
            data = self._get(f"beliefs/{belief_id}/evidence")
            return data.get("evidence", [])
        except RequestException:
            return []

    # =========================================================================
    # Community Operations
    # =========================================================================

    def get_communities(self) -> List[Dict]:
        """Get all epistemic communities."""
        try:
            data = self._get("communities")
            return data.get("communities", [])
        except RequestException:
            return self._demo_communities()

    def get_community(self, community_id: str) -> Optional[Dict]:
        """Get detailed information about a community."""
        try:
            return self._get(f"communities/{community_id}")
        except RequestException:
            return None

    def get_community_beliefs(self, community_id: str) -> List[BeliefSummary]:
        """Get beliefs associated with a community."""
        try:
            data = self._get(f"communities/{community_id}/beliefs")
            return [BeliefSummary(**b) for b in data.get("beliefs", [])]
        except RequestException:
            return []

    # =========================================================================
    # System Operations
    # =========================================================================

    def get_stats(self) -> SystemStats:
        """Get system-wide statistics."""
        try:
            data = self._get("admin/stats")
            return SystemStats(**data)
        except RequestException:
            return self._demo_stats()

    def get_health(self) -> Dict:
        """Get system health status."""
        try:
            return self._get("admin/health")
        except RequestException:
            return {"status": "offline", "message": "Cannot connect to API"}

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent system activity."""
        try:
            data = self._get("admin/activity", {"limit": limit})
            return data.get("activities", [])
        except RequestException:
            return []

    # =========================================================================
    # Export Operations
    # =========================================================================

    def export_bibtex(self, belief_ids: Optional[List[str]] = None) -> str:
        """Export BibTeX citations for beliefs."""
        try:
            data = self._post("export/bibtex", {"belief_ids": belief_ids})
            return data.get("bibtex", "")
        except RequestException:
            return ""

    def export_summary(
        self,
        query: str,
        format: str = "markdown"
    ) -> str:
        """Export evidence summary for a query."""
        try:
            data = self._post("export/summary", {"query": query, "format": format})
            return data.get("content", "")
        except RequestException:
            return ""

    # =========================================================================
    # Demo Data (for offline/development mode)
    # =========================================================================

    def _demo_query_result(self, query: str) -> QueryResult:
        """Return demo query result for development."""
        return QueryResult(
            query=query,
            query_type="WHAT",
            headline="Plants are associated with stress reduction in office settings (credence: 0.72 ± 0.12)",
            summary={
                "finding": "Multiple studies show 15-25% reduction in self-reported stress",
                "confidence": "moderate",
                "key_evidence": ["Lohr 1996", "Bringslimark 2007", "Fjeld 2000"]
            },
            practical_implications=[
                "Minimum 1 plant per 10m² workspace",
                "Visible greenery more effective than hidden",
                "Real plants preferred over artificial",
            ],
            scope_conditions={
                "population": "Office workers, primarily Western countries",
                "setting": "Indoor office environments",
                "methodology": "Self-report surveys, some cortisol measurements",
                "limitations": "Limited hospital data, no long-term studies"
            },
            caveats=[
                "Limited evidence for hospital settings",
                "No data on long-term effects",
                "Cultural variations not well studied"
            ],
            key_sources=[
                "Lohr et al. (1996) — n=96, cortisol + self-report",
                "Bringslimark et al. (2007) — Meta-analysis, k=21",
                "Fjeld (2000) — n=51, sick leave reduction"
            ]
        )

    def _demo_beliefs(self) -> List[BeliefSummary]:
        """Return demo beliefs for development."""
        return [
            BeliefSummary(
                id="B001",
                content="Natural environments restore directed attention capacity",
                credence=0.85,
                status="ACCEPTED",
                level="THEORETICAL",
                theory="ART",
                sources_count=12,
                constraints_count=8
            ),
            BeliefSummary(
                id="B002",
                content="Plants in offices reduce self-reported stress by 15-25%",
                credence=0.72,
                status="ACCEPTED",
                level="EMPIRICAL",
                theory="Biophilia",
                sources_count=8,
                constraints_count=5
            ),
            BeliefSummary(
                id="B003",
                content="Window views to nature improve patient recovery",
                credence=0.65,
                status="CONTESTED",
                level="EMPIRICAL",
                theory="SRT",
                sources_count=6,
                constraints_count=12
            ),
        ]

    def _demo_communities(self) -> List[Dict]:
        """Return demo communities for development."""
        return [
            {
                "id": "art",
                "name": "Attention Restoration Theory (ART)",
                "beliefs_count": 156,
                "average_credence": 0.78,
                "key_researchers": ["R. Kaplan", "S. Kaplan"]
            },
            {
                "id": "srt",
                "name": "Stress Recovery Theory (SRT)",
                "beliefs_count": 142,
                "average_credence": 0.72,
                "key_researchers": ["R. Ulrich"]
            },
            {
                "id": "biophilia",
                "name": "Biophilia Hypothesis",
                "beliefs_count": 234,
                "average_credence": 0.68,
                "key_researchers": ["E.O. Wilson", "S. Kellert"]
            },
        ]

    def _demo_stats(self) -> SystemStats:
        """Return demo stats for development."""
        return SystemStats(
            total_beliefs=1247,
            total_constraints=3891,
            total_papers=312,
            total_communities=4,
            overall_coherence=0.72,
            average_credence=0.68,
            contested_beliefs=231,
            stub_beliefs=142
        )


# Singleton client instance
_client: Optional[ArticleEaterClient] = None


def get_client() -> ArticleEaterClient:
    """Get or create API client singleton."""
    global _client
    if _client is None:
        _client = ArticleEaterClient()
    return _client
