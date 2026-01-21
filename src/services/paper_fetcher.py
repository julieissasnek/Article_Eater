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
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import re
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


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
# Unified Paper Fetcher
# =============================================================================

class PaperFetcher:
    """
    Unified paper fetcher that auto-detects identifier type.

    Per expert panel (Systems Architect): Users should just paste
    any identifier and the system handles the rest.
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
            crossref_client: Client for DOI resolution
            pubmed_client: Client for PMID resolution
            semantic_scholar_client: Client for S2 ID and citations
            arxiv_client: Client for arXiv preprints
            existing_papers: Dict of existing papers for duplicate detection
        """
        self.crossref = crossref_client or MockCrossRefClient()
        self.pubmed = pubmed_client or MockPubMedClient()
        self.semantic_scholar = semantic_scholar_client or MockSemanticScholarClient()
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
