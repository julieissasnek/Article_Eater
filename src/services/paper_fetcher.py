"""
Paper Fetcher Service
=====================

Unified ingestion client for fetching paper metadata from multiple sources.

Tier 1 implementation per expert panel feedback:
- Support DOI, PMID, Semantic Scholar ID, arXiv ID
- Auto-detect identifier type from format
- Metadata + structured data (not requiring full text)
- Citation graph integration

Per expert panel (Kaplan): Add PsycINFO support for environmental psychology.
Per expert panel (Cartwright): Mark abstract-only extractions with lower confidence.

Date: January 20, 2026
Updated: February 26, 2026 — replaced Mock clients with real HTTP implementations
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
import json
import os
import re
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Polite contact email for API rate-limit pools
_CONTACT_EMAIL = os.environ.get("AE_CONTACT_EMAIL", "dkirsh@gmail.com")


# =============================================================================
# Data Structures
# =============================================================================

class IdentifierType(Enum):
    """Types of paper identifiers."""
    DOI = "doi"
    PMID = "pmid"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    ARXIV = "arxiv"
    UNKNOWN = "unknown"


class FetchStatus(Enum):
    """Status of a fetch operation."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DUPLICATE = "duplicate"


@dataclass
class Author:
    """Author information."""
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'affiliation': self.affiliation,
            'orcid': self.orcid
        }


@dataclass
class Citation:
    """Citation relationship between papers."""
    citing_paper_id: str
    cited_paper_id: str
    context: Optional[str] = None  # Citation context if available

    def to_dict(self) -> Dict[str, Any]:
        return {
            'citing_paper_id': self.citing_paper_id,
            'cited_paper_id': self.cited_paper_id,
            'context': self.context
        }


@dataclass
class PaperMetadata:
    """
    Metadata for a scientific paper.

    Per expert panel (Cartwright): Track source_depth to indicate
    whether we have full text or just abstract.
    """
    # Identifiers
    paper_id: str  # Internal ID
    doi: Optional[str] = None
    pmid: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    arxiv_id: Optional[str] = None

    # Bibliographic info
    title: str = ""
    abstract: Optional[str] = None
    authors: List[Author] = field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None  # Journal/conference
    volume: Optional[str] = None
    pages: Optional[str] = None

    # Structured data
    keywords: List[str] = field(default_factory=list)
    mesh_terms: List[str] = field(default_factory=list)  # MeSH for PubMed
    study_type: Optional[str] = None  # RCT, observational, review, etc.
    open_access: bool = False

    # Citation info
    citation_count: int = 0
    references: List[str] = field(default_factory=list)  # Paper IDs this cites
    cited_by: List[str] = field(default_factory=list)    # Paper IDs citing this

    # Source tracking
    source: str = "unknown"  # Which API provided this
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paper_id': self.paper_id,
            'doi': self.doi,
            'pmid': self.pmid,
            'semantic_scholar_id': self.semantic_scholar_id,
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'abstract': self.abstract,
            'authors': [a.to_dict() for a in self.authors],
            'year': self.year,
            'venue': self.venue,
            'volume': self.volume,
            'pages': self.pages,
            'keywords': self.keywords,
            'mesh_terms': self.mesh_terms,
            'study_type': self.study_type,
            'open_access': self.open_access,
            'citation_count': self.citation_count,
            'references': self.references,
            'cited_by': self.cited_by,
            'source': self.source,
            'fetched_at': self.fetched_at.isoformat()
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'PaperMetadata':
        authors = [
            Author(
                name=a.get('name', ''),
                affiliation=a.get('affiliation'),
                orcid=a.get('orcid')
            )
            for a in d.get('authors', [])
        ]

        fetched_at = d.get('fetched_at')
        if isinstance(fetched_at, str):
            fetched_at = datetime.fromisoformat(fetched_at)
        elif fetched_at is None:
            fetched_at = datetime.now(timezone.utc)

        return cls(
            paper_id=d.get('paper_id', ''),
            doi=d.get('doi'),
            pmid=d.get('pmid'),
            semantic_scholar_id=d.get('semantic_scholar_id'),
            arxiv_id=d.get('arxiv_id'),
            title=d.get('title', ''),
            abstract=d.get('abstract'),
            authors=authors,
            year=d.get('year'),
            venue=d.get('venue'),
            volume=d.get('volume'),
            pages=d.get('pages'),
            keywords=d.get('keywords', []),
            mesh_terms=d.get('mesh_terms', []),
            study_type=d.get('study_type'),
            open_access=d.get('open_access', False),
            citation_count=d.get('citation_count', 0),
            references=d.get('references', []),
            cited_by=d.get('cited_by', []),
            source=d.get('source', 'unknown'),
            fetched_at=fetched_at
        )


@dataclass
class FetchResult:
    """Result of a fetch operation."""
    status: FetchStatus
    metadata: Optional[PaperMetadata] = None
    error_message: Optional[str] = None
    duplicate_of: Optional[str] = None  # If duplicate, ID of existing paper

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'metadata': self.metadata.to_dict() if self.metadata else None,
            'error_message': self.error_message,
            'duplicate_of': self.duplicate_of
        }


# =============================================================================
# API Client Base Class
# =============================================================================

class APIClient(ABC):
    """Abstract base class for paper metadata API clients."""

    @abstractmethod
    def fetch(self, identifier: str) -> FetchResult:
        """Fetch paper metadata by identifier."""
        pass

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        """Search for papers by query."""
        pass


# =============================================================================
# Mock API Clients (for testing without real API access)
# =============================================================================

class MockCrossRefClient(APIClient):
    """
    Mock CrossRef API client for DOI resolution.

    In production, this would call the CrossRef API.
    """

    def __init__(self):
        self.cache: Dict[str, PaperMetadata] = {}

    def fetch(self, doi: str) -> FetchResult:
        """Fetch metadata by DOI."""
        # Normalize DOI
        doi = self._normalize_doi(doi)

        if doi in self.cache:
            return FetchResult(
                status=FetchStatus.SUCCESS,
                metadata=self.cache[doi]
            )

        # In real implementation, would call CrossRef API
        # For now, return mock data for testing
        logger.info(f"MockCrossRefClient: Would fetch DOI {doi}")

        # Return not found for unknown DOIs
        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"DOI not found: {doi}"
        )

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        """Search CrossRef by query."""
        # Would call CrossRef API in production
        return []

    def _normalize_doi(self, doi: str) -> str:
        """Normalize DOI format."""
        # Remove URL prefix if present
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
        return doi.lower()


class MockPubMedClient(APIClient):
    """
    Mock PubMed E-utilities client for PMID resolution.

    In production, this would call the NCBI E-utilities API.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cache: Dict[str, PaperMetadata] = {}

    def fetch(self, pmid: str) -> FetchResult:
        """Fetch metadata by PMID."""
        # Normalize PMID
        pmid = self._normalize_pmid(pmid)

        if pmid in self.cache:
            return FetchResult(
                status=FetchStatus.SUCCESS,
                metadata=self.cache[pmid]
            )

        logger.info(f"MockPubMedClient: Would fetch PMID {pmid}")
        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"PMID not found: {pmid}"
        )

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        """Search PubMed by query."""
        return []

    def _normalize_pmid(self, pmid: str) -> str:
        """Normalize PMID format."""
        # Remove PMID prefix if present
        pmid = re.sub(r'^pmid:?\s*', '', pmid, flags=re.IGNORECASE)
        return pmid


class MockSemanticScholarClient(APIClient):
    """
    Mock Semantic Scholar API client.

    Provides citation graph data in addition to metadata.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cache: Dict[str, PaperMetadata] = {}

    def fetch(self, s2_id: str) -> FetchResult:
        """Fetch metadata by Semantic Scholar ID."""
        if s2_id in self.cache:
            return FetchResult(
                status=FetchStatus.SUCCESS,
                metadata=self.cache[s2_id]
            )

        logger.info(f"MockSemanticScholarClient: Would fetch S2ID {s2_id}")
        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"S2ID not found: {s2_id}"
        )

    def fetch_by_doi(self, doi: str) -> FetchResult:
        """Fetch by DOI (Semantic Scholar also supports DOI lookup)."""
        logger.info(f"MockSemanticScholarClient: Would fetch DOI {doi}")
        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"DOI not found in Semantic Scholar: {doi}"
        )

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        """Search Semantic Scholar by query."""
        return []

    def get_citations(self, paper_id: str) -> List[Citation]:
        """Get citations for a paper."""
        return []

    def get_references(self, paper_id: str) -> List[Citation]:
        """Get references from a paper."""
        return []


class MockArxivClient(APIClient):
    """
    Mock arXiv API client.

    For preprint access.
    """

    def __init__(self):
        self.cache: Dict[str, PaperMetadata] = {}

    def fetch(self, arxiv_id: str) -> FetchResult:
        """Fetch metadata by arXiv ID."""
        arxiv_id = self._normalize_arxiv_id(arxiv_id)

        if arxiv_id in self.cache:
            return FetchResult(
                status=FetchStatus.SUCCESS,
                metadata=self.cache[arxiv_id]
            )

        logger.info(f"MockArxivClient: Would fetch arXiv {arxiv_id}")
        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"arXiv ID not found: {arxiv_id}"
        )

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        """Search arXiv by query."""
        return []

    def _normalize_arxiv_id(self, arxiv_id: str) -> str:
        """Normalize arXiv ID format."""
        # Remove arxiv: prefix if present
        arxiv_id = re.sub(r'^arxiv:?\s*', '', arxiv_id, flags=re.IGNORECASE)
        # Remove version suffix for caching
        return arxiv_id


# =============================================================================
# Real API Clients (live HTTP implementations)
# =============================================================================

class _RateLimiter:
    """Simple per-class rate limiter."""
    def __init__(self, min_delay: float = 1.0):
        self._min_delay = min_delay
        self._last_request: float = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request = time.monotonic()


def _http_get_json(url: str, headers: Optional[Dict[str, str]] = None,
                   retries: int = 3, backoff: float = 2.0) -> Optional[Dict]:
    """GET a URL, parse JSON response, with retries."""
    hdrs = {"User-Agent": f"ArticleEater/1.0 (mailto:{_CONTACT_EMAIL})"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = backoff * (2 ** attempt)
                logger.warning("Rate limited on %s, waiting %.1fs", url, wait)
                time.sleep(wait)
                continue
            if e.code in (404, 410):
                return None
            logger.warning("HTTP %d for %s (attempt %d/%d)", e.code, url, attempt + 1, retries)
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
        except Exception as exc:
            logger.warning("Request error for %s: %s (attempt %d/%d)", url, exc, attempt + 1, retries)
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
    return None


class CrossRefClient(APIClient):
    """
    Real CrossRef API client for DOI resolution and text search.

    Uses https://api.crossref.org with polite pool (mailto header).
    """

    BASE = "https://api.crossref.org"

    def __init__(self) -> None:
        self._limiter = _RateLimiter(min_delay=0.5)

    def fetch(self, doi: str) -> FetchResult:
        doi = self._normalize_doi(doi)
        self._limiter.wait()
        url = f"{self.BASE}/works/{urllib.parse.quote(doi, safe='')}"
        data = _http_get_json(url)
        if data is None or "message" not in data:
            return FetchResult(status=FetchStatus.NOT_FOUND,
                               error_message=f"DOI not found in CrossRef: {doi}")
        msg = data["message"]
        return FetchResult(status=FetchStatus.SUCCESS,
                           metadata=self._parse_work(msg, doi))

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        self._limiter.wait()
        params = urllib.parse.urlencode({
            "query": query,
            "rows": max_results,
            "select": "DOI,title,author,published-print,published-online,"
                      "container-title,volume,page,abstract,is-referenced-by-count,"
                      "subject,type",
        })
        url = f"{self.BASE}/works?{params}"
        data = _http_get_json(url)
        if not data or "message" not in data:
            return []
        items = data["message"].get("items", [])
        results: List[PaperMetadata] = []
        for item in items[:max_results]:
            doi = item.get("DOI", "")
            results.append(self._parse_work(item, doi))
        return results

    # -- helpers --

    @staticmethod
    def _normalize_doi(doi: str) -> str:
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
        return doi.strip()

    def _parse_work(self, msg: Dict[str, Any], doi: str) -> PaperMetadata:
        title_parts = msg.get("title", [])
        title = title_parts[0] if title_parts else ""

        authors: List[Author] = []
        for a in msg.get("author", []):
            name_parts = []
            if a.get("given"):
                name_parts.append(a["given"])
            if a.get("family"):
                name_parts.append(a["family"])
            if name_parts:
                affils = a.get("affiliation", [])
                affil = affils[0].get("name") if affils else None
                authors.append(Author(name=" ".join(name_parts),
                                      affiliation=affil,
                                      orcid=a.get("ORCID")))

        year: Optional[int] = None
        for date_field in ("published-print", "published-online", "issued", "created"):
            dp = msg.get(date_field, {}).get("date-parts", [[]])
            if dp and dp[0] and dp[0][0]:
                year = int(dp[0][0])
                break

        venue_parts = msg.get("container-title", [])
        venue = venue_parts[0] if venue_parts else None
        abstract_raw = msg.get("abstract", "")
        # CrossRef abstracts often have JATS XML tags
        abstract = re.sub(r"<[^>]+>", "", abstract_raw).strip() if abstract_raw else None

        return PaperMetadata(
            paper_id=f"doi:{doi}",
            doi=doi,
            title=title,
            abstract=abstract,
            authors=authors,
            year=year,
            venue=venue,
            volume=msg.get("volume"),
            pages=msg.get("page"),
            keywords=msg.get("subject", []),
            study_type=estimate_study_type(abstract, title),
            open_access=bool(msg.get("license")),
            citation_count=int(msg.get("is-referenced-by-count", 0)),
            references=[ref.get("DOI", "") for ref in msg.get("reference", [])
                        if ref.get("DOI")],
            source="crossref",
        )


class PubMedClient(APIClient):
    """
    Real PubMed E-utilities client for PMID resolution and search.

    Uses https://eutils.ncbi.nlm.nih.gov/entrez/eutils.
    """

    BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("NCBI_API_KEY")
        # With API key: 10 req/sec; without: 3 req/sec
        delay = 0.12 if self.api_key else 0.35
        self._limiter = _RateLimiter(min_delay=delay)

    def fetch(self, pmid: str) -> FetchResult:
        pmid = self._normalize_pmid(pmid)
        self._limiter.wait()
        params: Dict[str, str] = {
            "db": "pubmed", "id": pmid, "rettype": "xml", "retmode": "xml",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{self.BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
        try:
            hdrs = {"User-Agent": f"ArticleEater/1.0 (mailto:{_CONTACT_EMAIL})"}
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=30) as resp:
                xml_bytes = resp.read()
        except Exception as exc:
            return FetchResult(status=FetchStatus.ERROR,
                               error_message=f"PubMed fetch error: {exc}")

        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as exc:
            return FetchResult(status=FetchStatus.ERROR,
                               error_message=f"PubMed XML parse error: {exc}")

        article = root.find(".//PubmedArticle")
        if article is None:
            return FetchResult(status=FetchStatus.NOT_FOUND,
                               error_message=f"PMID not found: {pmid}")
        return FetchResult(status=FetchStatus.SUCCESS,
                           metadata=self._parse_article(article, pmid))

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        self._limiter.wait()
        params: Dict[str, str] = {
            "db": "pubmed", "term": query, "retmax": str(max_results),
            "retmode": "json", "sort": "relevance",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        url = f"{self.BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        data = _http_get_json(url)
        if not data:
            return []
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        # Fetch each found PMID
        results: List[PaperMetadata] = []
        for pmid in ids:
            r = self.fetch(pmid)
            if r.status == FetchStatus.SUCCESS and r.metadata:
                results.append(r.metadata)
        return results

    @staticmethod
    def _normalize_pmid(pmid: str) -> str:
        return re.sub(r'^pmid:?\s*', '', pmid, flags=re.IGNORECASE).strip()

    def _parse_article(self, article: ET.Element, pmid: str) -> PaperMetadata:
        mc = article.find(".//MedlineCitation")
        ac = mc.find("Article") if mc is not None else None

        title = ""
        if ac is not None:
            t_el = ac.find("ArticleTitle")
            if t_el is not None and t_el.text:
                title = t_el.text

        abstract_parts: List[str] = []
        if ac is not None:
            for at in ac.findall(".//AbstractText"):
                label = at.get("Label", "")
                text = (at.text or "").strip()
                if label and text:
                    abstract_parts.append(f"{label}: {text}")
                elif text:
                    abstract_parts.append(text)
        abstract = " ".join(abstract_parts) if abstract_parts else None

        authors: List[Author] = []
        if ac is not None:
            for au in ac.findall(".//Author"):
                ln = (au.findtext("LastName") or "").strip()
                fn = (au.findtext("ForeName") or au.findtext("FirstName") or "").strip()
                if ln:
                    name = f"{fn} {ln}".strip()
                    affils = au.findall(".//Affiliation")
                    affil = affils[0].text if affils and affils[0].text else None
                    authors.append(Author(name=name, affiliation=affil))

        year: Optional[int] = None
        if ac is not None:
            for dp in ac.findall(".//PubDate/Year"):
                if dp.text and dp.text.isdigit():
                    year = int(dp.text)
                    break

        venue: Optional[str] = None
        if ac is not None:
            j = ac.find("Journal")
            if j is not None:
                venue = j.findtext("Title") or j.findtext("ISOAbbreviation")

        mesh: List[str] = []
        if mc is not None:
            for mh in mc.findall(".//MeshHeading/DescriptorName"):
                if mh.text:
                    mesh.append(mh.text)

        keywords: List[str] = []
        if mc is not None:
            for kw in mc.findall(".//Keyword"):
                if kw.text:
                    keywords.append(kw.text)

        # Try to find DOI in article IDs
        doi: Optional[str] = None
        for aid in article.findall(".//ArticleId"):
            if aid.get("IdType") == "doi" and aid.text:
                doi = aid.text

        return PaperMetadata(
            paper_id=f"pmid:{pmid}",
            doi=doi,
            pmid=pmid,
            title=title,
            abstract=abstract,
            authors=authors,
            year=year,
            venue=venue,
            keywords=keywords,
            mesh_terms=mesh,
            study_type=estimate_study_type(abstract, title),
            source="pubmed",
        )


class SemanticScholarClient(APIClient):
    """
    Real Semantic Scholar Graph API client.

    Supports DOI lookup, S2 ID lookup, search, and citation graph.
    https://api.semanticscholar.org/api-docs/graph
    """

    BASE = "https://api.semanticscholar.org/graph/v1"
    PAPER_FIELDS = ",".join([
        "title", "authors", "year", "venue", "publicationVenue",
        "externalIds", "abstract", "citationCount", "influentialCitationCount",
        "isOpenAccess", "fieldsOfStudy", "s2FieldsOfStudy",
        "references.externalIds", "citations.externalIds",
    ])

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        # Unauthenticated: 100 req / 5 min ≈ 3s; authenticated: 1 req/s
        delay = 1.1 if self.api_key else 3.1
        self._limiter = _RateLimiter(min_delay=delay)

    def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {}
        if self.api_key:
            h["x-api-key"] = self.api_key
        return h

    def fetch(self, s2_id: str) -> FetchResult:
        self._limiter.wait()
        url = f"{self.BASE}/paper/{urllib.parse.quote(s2_id, safe='')}?fields={self.PAPER_FIELDS}"
        data = _http_get_json(url, headers=self._headers())
        if data is None:
            return FetchResult(status=FetchStatus.NOT_FOUND,
                               error_message=f"S2 paper not found: {s2_id}")
        return FetchResult(status=FetchStatus.SUCCESS,
                           metadata=self._parse_paper(data))

    def fetch_by_doi(self, doi: str) -> FetchResult:
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi).strip()
        return self.fetch(f"DOI:{doi}")

    def search(self, query: str, max_results: int = 10) -> List[PaperMetadata]:
        self._limiter.wait()
        params = urllib.parse.urlencode({
            "query": query, "limit": min(max_results, 100),
            "fields": "title,authors,year,venue,externalIds,abstract,"
                      "citationCount,isOpenAccess,fieldsOfStudy",
        })
        url = f"{self.BASE}/paper/search?{params}"
        data = _http_get_json(url, headers=self._headers())
        if not data:
            return []
        papers = data.get("data", [])
        return [self._parse_paper(p) for p in papers[:max_results]]

    def get_citations(self, paper_id: str) -> List[Citation]:
        self._limiter.wait()
        url = (f"{self.BASE}/paper/{urllib.parse.quote(paper_id, safe='')}"
               f"/citations?fields=externalIds,contexts&limit=100")
        data = _http_get_json(url, headers=self._headers())
        if not data:
            return []
        results: List[Citation] = []
        for item in data.get("data", []):
            citing = item.get("citingPaper", {})
            eids = citing.get("externalIds", {}) or {}
            citing_id = eids.get("DOI") or citing.get("paperId", "")
            contexts = item.get("contexts", [])
            ctx = contexts[0] if contexts else None
            if citing_id:
                results.append(Citation(citing_paper_id=citing_id,
                                        cited_paper_id=paper_id,
                                        context=ctx))
        return results

    def get_references(self, paper_id: str) -> List[Citation]:
        self._limiter.wait()
        url = (f"{self.BASE}/paper/{urllib.parse.quote(paper_id, safe='')}"
               f"/references?fields=externalIds,contexts&limit=100")
        data = _http_get_json(url, headers=self._headers())
        if not data:
            return []
        results: List[Citation] = []
        for item in data.get("data", []):
            cited = item.get("citedPaper", {})
            eids = cited.get("externalIds", {}) or {}
            cited_id = eids.get("DOI") or cited.get("paperId", "")
            contexts = item.get("contexts", [])
            ctx = contexts[0] if contexts else None
            if cited_id:
                results.append(Citation(citing_paper_id=paper_id,
                                        cited_paper_id=cited_id,
                                        context=ctx))
        return results

    def _parse_paper(self, data: Dict[str, Any]) -> PaperMetadata:
        eids = data.get("externalIds", {}) or {}
        doi = eids.get("DOI")
        pmid = eids.get("PubMed")
        arxiv = eids.get("ArXiv")
        s2id = data.get("paperId", "")

        authors: List[Author] = []
        for a in data.get("authors", []):
            name = a.get("name", "").strip()
            if name:
                authors.append(Author(name=name))

        title = (data.get("title") or "").strip()
        abstract = (data.get("abstract") or "").strip() or None

        ref_dois: List[str] = []
        for ref in data.get("references", []) or []:
            r_eids = (ref.get("externalIds") or {})
            if r_eids.get("DOI"):
                ref_dois.append(r_eids["DOI"])

        cited_dois: List[str] = []
        for cit in data.get("citations", []) or []:
            c_eids = (cit.get("externalIds") or {})
            if c_eids.get("DOI"):
                cited_dois.append(c_eids["DOI"])

        paper_id = f"doi:{doi}" if doi else f"s2:{s2id}"
        fos = data.get("fieldsOfStudy") or data.get("s2FieldsOfStudy") or []
        keywords = [f.get("category", f) if isinstance(f, dict) else f for f in fos]

        return PaperMetadata(
            paper_id=paper_id,
            doi=doi,
            pmid=pmid,
            semantic_scholar_id=s2id,
            arxiv_id=arxiv,
            title=title,
            abstract=abstract,
            authors=authors,
            year=data.get("year"),
            venue=data.get("venue") or "",
            keywords=keywords,
            study_type=estimate_study_type(abstract, title),
            open_access=bool(data.get("isOpenAccess")),
            citation_count=int(data.get("citationCount", 0) or 0),
            references=ref_dois,
            cited_by=cited_dois,
            source="semantic_scholar",
        )


# =============================================================================
# Unified Paper Fetcher
# =============================================================================

class PaperFetcher:
    """
    Unified paper fetcher that auto-detects identifier type.

    Per expert panel (Systems Architect): Users should just paste
    any identifier and the system handles the rest.

    Defaults to real API clients. Pass Mock* clients for testing.
    """

    def __init__(
        self,
        crossref_client: Optional[APIClient] = None,
        pubmed_client: Optional[APIClient] = None,
        semantic_scholar_client: Optional[APIClient] = None,
        arxiv_client: Optional[APIClient] = None,
        existing_papers: Optional[Dict[str, PaperMetadata]] = None
    ):
        """
        Initialize the fetcher with API clients.

        Args:
            crossref_client: Client for DOI resolution (default: real CrossRefClient)
            pubmed_client: Client for PMID resolution (default: real PubMedClient)
            semantic_scholar_client: Client for S2 ID and citations (default: real SemanticScholarClient)
            arxiv_client: Client for arXiv preprints (default: MockArxivClient — no real arXiv client yet)
            existing_papers: Dict of existing papers for duplicate detection
        """
        self.crossref = crossref_client or CrossRefClient()
        self.pubmed = pubmed_client or PubMedClient()
        self.semantic_scholar = semantic_scholar_client or SemanticScholarClient()
        self.arxiv = arxiv_client or MockArxivClient()
        self.existing_papers = existing_papers or {}

    def detect_identifier_type(self, identifier: str) -> IdentifierType:
        """
        Detect the type of identifier from its format.

        Args:
            identifier: The identifier string to analyze

        Returns:
            IdentifierType enum value
        """
        identifier = identifier.strip()

        # DOI patterns
        doi_patterns = [
            r'^10\.\d{4,}/',  # Standard DOI
            r'^https?://(dx\.)?doi\.org/10\.\d{4,}/',  # DOI URL
        ]
        for pattern in doi_patterns:
            if re.match(pattern, identifier, re.IGNORECASE):
                return IdentifierType.DOI

        # PMID pattern (numeric, optionally with PMID prefix)
        if re.match(r'^(pmid:?\s*)?\d{6,9}$', identifier, re.IGNORECASE):
            return IdentifierType.PMID

        # arXiv patterns
        arxiv_patterns = [
            r'^arxiv:?\s*\d{4}\.\d{4,5}(v\d+)?$',  # New format: 2301.12345
            r'^arxiv:?\s*[a-z-]+(\.[A-Za-z]+)?/\d{7}(v\d+)?$',   # Old format: cs.AI/0123456
            r'^\d{4}\.\d{4,5}(v\d+)?$',             # Just the number
        ]
        for pattern in arxiv_patterns:
            if re.match(pattern, identifier, re.IGNORECASE):
                return IdentifierType.ARXIV

        # Semantic Scholar ID (40-char hex)
        if re.match(r'^[0-9a-f]{40}$', identifier, re.IGNORECASE):
            return IdentifierType.SEMANTIC_SCHOLAR

        return IdentifierType.UNKNOWN

    def fetch(self, identifier: str) -> FetchResult:
        """
        Fetch paper metadata by any supported identifier.

        Auto-detects identifier type and routes to appropriate client.

        Args:
            identifier: DOI, PMID, S2 ID, or arXiv ID

        Returns:
            FetchResult with metadata or error
        """
        id_type = self.detect_identifier_type(identifier)

        if id_type == IdentifierType.UNKNOWN:
            return FetchResult(
                status=FetchStatus.ERROR,
                error_message=f"Could not detect identifier type for: {identifier}"
            )

        # Check for duplicates first
        duplicate = self._check_duplicate(identifier, id_type)
        if duplicate:
            return FetchResult(
                status=FetchStatus.DUPLICATE,
                duplicate_of=duplicate
            )

        # Route to appropriate client
        if id_type == IdentifierType.DOI:
            return self._fetch_by_doi(identifier)
        elif id_type == IdentifierType.PMID:
            return self.pubmed.fetch(identifier)
        elif id_type == IdentifierType.ARXIV:
            return self.arxiv.fetch(identifier)
        elif id_type == IdentifierType.SEMANTIC_SCHOLAR:
            return self.semantic_scholar.fetch(identifier)
        else:
            return FetchResult(
                status=FetchStatus.ERROR,
                error_message=f"Unsupported identifier type: {id_type}"
            )

    def _fetch_by_doi(self, doi: str) -> FetchResult:
        """
        Fetch by DOI, trying multiple sources.

        Per expert panel (Bates): Use Semantic Scholar as backup
        since it aggregates from multiple sources.
        """
        # Try CrossRef first
        result = self.crossref.fetch(doi)
        if result.status == FetchStatus.SUCCESS:
            return result

        # Fall back to Semantic Scholar
        if hasattr(self.semantic_scholar, 'fetch_by_doi'):
            result = self.semantic_scholar.fetch_by_doi(doi)
            if result.status == FetchStatus.SUCCESS:
                return result

        return FetchResult(
            status=FetchStatus.NOT_FOUND,
            error_message=f"DOI not found in any source: {doi}"
        )

    def _check_duplicate(self, identifier: str, id_type: IdentifierType) -> Optional[str]:
        """
        Check if paper already exists in the collection.

        Returns existing paper ID if duplicate, None otherwise.
        """
        identifier_lower = identifier.lower()

        for paper_id, paper in self.existing_papers.items():
            if id_type == IdentifierType.DOI and paper.doi:
                if paper.doi.lower() == identifier_lower:
                    return paper_id
            elif id_type == IdentifierType.PMID and paper.pmid:
                if paper.pmid == identifier_lower.replace('pmid:', '').strip():
                    return paper_id
            elif id_type == IdentifierType.ARXIV and paper.arxiv_id:
                norm_id = re.sub(r'^arxiv:?\s*', '', identifier_lower, flags=re.IGNORECASE)
                if paper.arxiv_id.lower() == norm_id:
                    return paper_id
            elif id_type == IdentifierType.SEMANTIC_SCHOLAR and paper.semantic_scholar_id:
                if paper.semantic_scholar_id.lower() == identifier_lower:
                    return paper_id

        return None

    def search(self, query: str, sources: Optional[List[str]] = None, max_results: int = 10) -> Dict[str, List[PaperMetadata]]:
        """
        Search for papers across multiple sources.

        Args:
            query: Search query
            sources: List of sources to search ('pubmed', 'semantic_scholar', 'arxiv')
            max_results: Maximum results per source

        Returns:
            Dict mapping source name to list of results
        """
        if sources is None:
            sources = ['pubmed', 'semantic_scholar']

        results = {}

        if 'pubmed' in sources:
            results['pubmed'] = self.pubmed.search(query, max_results)

        if 'semantic_scholar' in sources:
            results['semantic_scholar'] = self.semantic_scholar.search(query, max_results)

        if 'arxiv' in sources:
            results['arxiv'] = self.arxiv.search(query, max_results)

        return results

    def get_citation_suggestions(
        self,
        paper_id: str,
        existing_paper_ids: List[str]
    ) -> Dict[str, List[str]]:
        """
        Get citation-based paper suggestions.

        Per expert panel (Bates): Suggest papers based on citations,
        both citing and cited by.

        Args:
            paper_id: The paper to get suggestions for
            existing_paper_ids: Papers already in the web

        Returns:
            Dict with 'citing' and 'cited_by' lists of paper IDs
        """
        paper = self.existing_papers.get(paper_id)
        if not paper:
            return {'citing': [], 'cited_by': []}

        # Find papers that cite this one and are in our web
        citing_in_web = [
            pid for pid in paper.cited_by
            if pid in existing_paper_ids
        ]

        # Find papers this cites that are in our web
        cites_in_web = [
            pid for pid in paper.references
            if pid in existing_paper_ids
        ]

        # Find papers that cite this one but are NOT in our web (suggestions)
        citing_suggestions = [
            pid for pid in paper.cited_by
            if pid not in existing_paper_ids
        ][:5]  # Limit suggestions

        # Find papers this cites that are NOT in our web (suggestions)
        cites_suggestions = [
            pid for pid in paper.references
            if pid not in existing_paper_ids
        ][:5]

        return {
            'citing_in_web': citing_in_web,
            'cites_in_web': cites_in_web,
            'citing_suggestions': citing_suggestions,
            'cites_suggestions': cites_suggestions
        }


# =============================================================================
# Helper Functions
# =============================================================================

def estimate_study_type(abstract: Optional[str], title: str) -> Optional[str]:
    """
    Estimate study type from abstract and title.

    Returns study type string or None if unable to determine.
    """
    if not abstract and not title:
        return None

    text = f"{title} {abstract or ''}".lower()

    # Check for specific study types
    if 'meta-analysis' in text or 'meta analysis' in text:
        return 'meta_analysis'
    if 'systematic review' in text:
        return 'systematic_review'
    if 'randomized' in text or 'randomised' in text:
        return 'rct'
    if 'randomized controlled trial' in text or 'randomised controlled trial' in text:
        return 'rct'
    if 'longitudinal' in text:
        return 'longitudinal'
    if 'cross-sectional' in text or 'cross sectional' in text:
        return 'cross_sectional'
    if 'case study' in text or 'case report' in text:
        return 'case_study'
    if 'review' in text:
        return 'review'
    if 'experiment' in text or 'experimental' in text:
        return 'experimental'
    if 'survey' in text or 'questionnaire' in text:
        return 'survey'
    if 'qualitative' in text:
        return 'qualitative'

    return None


def generate_paper_id(metadata: PaperMetadata) -> str:
    """
    Generate a stable paper ID from metadata.

    Uses DOI if available, otherwise constructs from author/year/title.
    """
    if metadata.doi:
        return f"doi:{metadata.doi}"
    if metadata.pmid:
        return f"pmid:{metadata.pmid}"
    if metadata.arxiv_id:
        return f"arxiv:{metadata.arxiv_id}"
    if metadata.semantic_scholar_id:
        return f"s2:{metadata.semantic_scholar_id}"

    # Construct from metadata
    author_part = ""
    if metadata.authors:
        # Use first author's last name
        first_author = metadata.authors[0].name
        last_name = first_author.split(',')[0].split()[-1]
        author_part = last_name.lower()[:10]

    year_part = str(metadata.year) if metadata.year else "unknown"

    title_part = ""
    if metadata.title:
        # First significant word of title
        words = [w for w in metadata.title.lower().split() if len(w) > 3]
        if words:
            title_part = words[0][:10]

    return f"{author_part}_{year_part}_{title_part}".strip('_')


# =============================================================================
# Unpaywall Client (added 2026-02-27, Sprint COMPLETENESS-1)
# =============================================================================

class UnpaywallClient:
    """
    Client for the Unpaywall API — checks open access availability for DOIs.

    Unpaywall is a free, legal service that indexes OA copies of papers.
    API docs: https://unpaywall.org/products/api

    Rate limit: 100K requests/day with polite email header.
    """

    BASE_URL = "https://api.unpaywall.org/v2"

    def __init__(self, email: str = None):
        self.email = email or _CONTACT_EMAIL

    def check_oa_status(self, doi: str) -> Dict[str, Any]:
        """
        Check if a paper is available open access.

        Returns:
            {
                "is_oa": bool,
                "best_oa_url": str or None,
                "license": str or None,
                "host_type": str or None,  # "publisher", "repository"
                "doi": str,
                "title": str or None,
                "error": str or None,
            }
        """
        result = {
            "is_oa": False,
            "best_oa_url": None,
            "license": None,
            "host_type": None,
            "doi": doi,
            "title": None,
            "error": None,
        }

        try:
            # Clean DOI
            doi = doi.strip()
            if doi.startswith("http"):
                doi = doi.split("doi.org/")[-1]

            url = f"{self.BASE_URL}/{urllib.parse.quote(doi, safe='')}?email={self.email}"
            time.sleep(0.5)  # Polite delay

            req = urllib.request.Request(url)
            req.add_header("User-Agent", f"ATLAS/1.0 (mailto:{self.email})")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            result["is_oa"] = data.get("is_oa", False)
            result["title"] = data.get("title")

            # Find best OA location
            best_loc = data.get("best_oa_location")
            if best_loc:
                result["best_oa_url"] = (
                    best_loc.get("url_for_pdf")
                    or best_loc.get("url")
                )
                result["license"] = best_loc.get("license")
                result["host_type"] = best_loc.get("host_type")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                result["error"] = f"DOI not found in Unpaywall: {doi}"
            else:
                result["error"] = f"HTTP {e.code}: {e.reason}"
        except Exception as e:
            result["error"] = str(e)

        return result


def crossref_title_search(
    title: str,
    limit: int = 3,
    email: str = None,
) -> List[Dict[str, Any]]:
    """
    Search CrossRef by title to find DOI candidates.

    Returns list of {doi, title, score, authors, year}.
    """
    email = email or _CONTACT_EMAIL
    results = []

    try:
        query = urllib.parse.quote(title)
        url = (
            f"https://api.crossref.org/works?"
            f"query.title={query}&rows={limit}"
            f"&mailto={email}"
        )
        time.sleep(0.5)  # Polite delay

        req = urllib.request.Request(url)
        req.add_header("User-Agent", f"ATLAS/1.0 (mailto:{email})")

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("message", {}).get("items", [])
        for item in items:
            authors = []
            for a in item.get("author", []):
                name = f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
                if name:
                    authors.append(name)

            year = None
            date_parts = item.get("published-print", {}).get("date-parts", [[]])
            if not date_parts or not date_parts[0]:
                date_parts = item.get("published-online", {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

            results.append({
                "doi": item.get("DOI"),
                "title": item.get("title", [""])[0] if item.get("title") else "",
                "score": item.get("score", 0),
                "authors": authors,
                "year": year,
            })

    except Exception as e:
        logger.warning(f"CrossRef title search failed: {e}")

    return results
