"""
paper_fetcher.py -- Phase 4C HTTP clients for abstract collection.

Provides three validated API clients and one helper, each with:
  - Strict rate-limiting (token-bucket, thread-safe)
  - Automatic retry on HTTP 429 / 5xx with exponential backoff
  - Per-result title-similarity guard (SequenceMatcher >= 0.90) on
    all title-based lookups to prevent false-positive matches
  - Abstract validation enforced by the caller (abstract_collector_4c.py)

Clients
-------
  SemanticScholarClient  -- primary; rate-limited to 20 req/min (unauthenticated)
  CrossRefClient         -- DOI registry; 50 req/s polite pool
  PubMedClient           -- NCBI biomedical; 3 req/s without API key
  OpenAlexHelper         -- broad scholarly graph; 10 req/s

Thread-safety
-------------
  _RateLimiter uses threading.Lock.  All clients are safe to share
  across threads (one instance per process is sufficient).

Usage
-----
  from paper_fetcher import SemanticScholarClient, CrossRefClient
  from paper_fetcher import PubMedClient, OpenAlexHelper

  ss = SemanticScholarClient()
  result = ss.by_doi("10.1016/j.buildenv.2020.106960")
  # result: {"doi": ..., "title": ..., "abstract": ...,
  #          "year": ..., "source": "semantic_scholar"} or None
"""
from __future__ import annotations

import re
import threading
import time
from difflib import SequenceMatcher
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UA_STRING = "KA-AbstractCollector/4c (mailto:student@ucsd.edu)"

SS_PAPER_URL    = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
SS_SEARCH_URL   = "https://api.semanticscholar.org/graph/v1/paper/search"
CROSSREF_WORKS  = "https://api.crossref.org/works"
PUBMED_SEARCH   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH    = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENALEX_WORKS  = "https://api.openalex.org/works"

TITLE_SIM_THRESHOLD = 0.90   # SequenceMatcher ratio required for title lookups
DEFAULT_TIMEOUT     = 15     # seconds per HTTP call
MAX_RETRIES         = 3      # attempts on 429 / 5xx before giving up
BACKOFF_BASE        = 2.0    # exponential backoff: BACKOFF_BASE ** attempt seconds


# ---------------------------------------------------------------------------
# Rate-limiter — token bucket, thread-safe
# ---------------------------------------------------------------------------

class _RateLimiter:
    """
    Token-bucket rate limiter.

    Initialise with max_calls and period (seconds).  Each call to
    .acquire() blocks until a token is available, then consumes one.

    Example: _RateLimiter(max_calls=20, period=60) permits at most
    20 calls per 60-second window.
    """

    def __init__(self, max_calls: int, period: float) -> None:
        self._max_calls = max_calls
        self._period    = period
        self._lock      = threading.Lock()
        self._calls: list[float] = []   # timestamps of recent calls

    def acquire(self) -> None:
        """Block until a token is available, then consume one."""
        while True:
            with self._lock:
                now = time.monotonic()
                # Drop calls outside the rolling window
                cutoff = now - self._period
                self._calls = [t for t in self._calls if t > cutoff]
                if len(self._calls) < self._max_calls:
                    self._calls.append(now)
                    return
                # Calculate how long until the oldest call falls out
                wait = self._calls[0] - cutoff
            time.sleep(max(wait, 0.01))


# ---------------------------------------------------------------------------
# Shared HTTP helper
# ---------------------------------------------------------------------------

def _get(
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = DEFAULT_TIMEOUT,
    rate_limiter: Optional[_RateLimiter] = None,
) -> Optional[requests.Response]:
    """
    GET with retry on 429 / 5xx.  Returns Response or None on terminal failure.
    Respects Retry-After header on 429.
    """
    _headers = {"User-Agent": UA_STRING}
    if headers:
        _headers.update(headers)

    for attempt in range(MAX_RETRIES):
        if rate_limiter:
            rate_limiter.acquire()
        try:
            resp = requests.get(url, params=params, headers=_headers, timeout=timeout)
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", BACKOFF_BASE ** (attempt + 1)))
                time.sleep(retry_after)
                continue
            if resp.status_code >= 500:
                time.sleep(BACKOFF_BASE ** (attempt + 1))
                continue
            # 4xx other than 429 — not retryable
            return None
        except requests.Timeout:
            time.sleep(BACKOFF_BASE ** (attempt + 1))
        except requests.RequestException:
            return None

    return None


# ---------------------------------------------------------------------------
# Title-similarity guard
# ---------------------------------------------------------------------------

def _title_sim(a: str, b: str) -> float:
    """
    Return SequenceMatcher ratio after lowercasing and stripping punctuation.
    Used to reject false-positive title-based lookups.
    """
    def _clean(s: str) -> str:
        return re.sub(r"[^\w\s]", " ", s.lower()).strip()
    return SequenceMatcher(None, _clean(a), _clean(b)).ratio()


def _title_ok(query: str, found: str) -> bool:
    """Return True iff title similarity >= TITLE_SIM_THRESHOLD."""
    if not query or not found:
        return False
    return _title_sim(query, found) >= TITLE_SIM_THRESHOLD


# ---------------------------------------------------------------------------
# JATS / XML helpers
# ---------------------------------------------------------------------------

def _strip_jats(text: str) -> str:
    """Strip JATS XML tags from CrossRef abstracts."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _decode_inverted_index(inverted: Optional[dict]) -> str:
    """Reconstruct abstract text from OpenAlex inverted-index format."""
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, pos_list in inverted.items():
        for pos in pos_list:
            positions.append((pos, word))
    positions.sort()
    return " ".join(w for _, w in positions)


# ---------------------------------------------------------------------------
# Client 1: SemanticScholarClient
# ---------------------------------------------------------------------------

class SemanticScholarClient:
    """
    Semantic Scholar Graph API client.

    Rate limit: 20 requests/minute unauthenticated (enforced by token bucket).
    If an API key is provided, this limit is relaxed to 100 req/s, but the
    client is conservative by default.

    Methods
    -------
    by_doi(doi)          -- fetch by DOI, no title check needed
    by_title(title)      -- fetch top-1 search result; title similarity enforced
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        # Unauthenticated: 20 req/min.  Authenticated: much higher, but keep
        # conservative regardless to avoid accidental bans.
        self._limiter = _RateLimiter(max_calls=20, period=60)
        self._headers: dict[str, str] = {}
        if api_key:
            self._headers["x-api-key"] = api_key

    def by_doi(self, doi: str) -> Optional[dict]:
        """
        Fetch paper by DOI.  Returns normalised result dict or None.
        No title-similarity check (DOI is authoritative).
        """
        if not doi:
            return None
        url = SS_PAPER_URL.format(paper_id=f"DOI:{doi}")
        resp = _get(
            url,
            params={"fields": "title,abstract,externalIds,year,authors"},
            headers=self._headers,
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        data = resp.json()
        abstract = (data.get("abstract") or "").strip()
        return {
            "doi":      doi,
            "title":    (data.get("title") or "").strip(),
            "abstract": abstract,
            "year":     data.get("year"),
            "source":   "semantic_scholar",
        }

    def by_title(self, title: str) -> Optional[dict]:
        """
        Search by title; apply TITLE_SIM_THRESHOLD guard.
        Returns None if the top result does not match the query title.
        """
        if not title:
            return None
        resp = _get(
            SS_SEARCH_URL,
            params={
                "query":  title,
                "fields": "title,abstract,externalIds,year",
                "limit":  1,
            },
            headers=self._headers,
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        items = resp.json().get("data", [])
        if not items:
            return None
        item = items[0]
        found_title = (item.get("title") or "").strip()
        if not _title_ok(title, found_title):
            return None
        doi = (item.get("externalIds") or {}).get("DOI", "")
        return {
            "doi":      doi,
            "title":    found_title,
            "abstract": (item.get("abstract") or "").strip(),
            "year":     item.get("year"),
            "source":   "semantic_scholar",
        }


# ---------------------------------------------------------------------------
# Client 2: CrossRefClient
# ---------------------------------------------------------------------------

class CrossRefClient:
    """
    CrossRef Works API client.

    Polite pool: include mailto in User-Agent (done via UA_STRING).
    No hard rate limit enforced client-side; CrossRef allows ~50 req/s
    in the polite pool.  Uses a conservative 5 req/s limiter to avoid
    competing with other pipeline processes.

    Methods
    -------
    by_doi(doi)          -- fetch by DOI; authoritative, no title check
    by_title(title)      -- fuzzy title query, top-1; similarity enforced
    """

    def __init__(self) -> None:
        self._limiter = _RateLimiter(max_calls=5, period=1)

    def by_doi(self, doi: str) -> Optional[dict]:
        """Fetch CrossRef work record by DOI."""
        if not doi:
            return None
        resp = _get(
            f"{CROSSREF_WORKS}/{doi}",
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        item = resp.json().get("message", {})
        abstract = _strip_jats(item.get("abstract", ""))
        return {
            "doi":      doi,
            "title":    " ".join(item.get("title", [])).strip(),
            "abstract": abstract,
            "year":     (item.get("issued") or {}).get("date-parts", [[None]])[0][0],
            "source":   "crossref",
        }

    def by_title(self, title: str) -> Optional[dict]:
        """Query CrossRef by title; enforce title-similarity threshold."""
        if not title:
            return None
        resp = _get(
            CROSSREF_WORKS,
            params={
                "query.title": title,
                "rows":        1,
                "select":      "DOI,title,abstract,issued",
            },
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        items = resp.json().get("message", {}).get("items", [])
        if not items:
            return None
        item = items[0]
        found_title = " ".join(item.get("title", [])).strip()
        if not _title_ok(title, found_title):
            return None
        abstract = _strip_jats(item.get("abstract", ""))
        return {
            "doi":      item.get("DOI", ""),
            "title":    found_title,
            "abstract": abstract,
            "year":     (item.get("issued") or {}).get("date-parts", [[None]])[0][0],
            "source":   "crossref",
        }


# ---------------------------------------------------------------------------
# Client 3: PubMedClient
# ---------------------------------------------------------------------------

class PubMedClient:
    """
    NCBI PubMed E-utilities client.

    Without an API key: 3 req/s.  Uses a conservative 2 req/s limiter.
    PubMed does not support DOI direct-lookup via eutils; both lookups
    use title-search then fetch by PMID.

    Methods
    -------
    by_doi(doi)          -- searches PubMed for the DOI string in [aid] field
    by_title(title)      -- free-text title search; similarity enforced
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._limiter = _RateLimiter(max_calls=2, period=1)
        self._api_key = api_key

    def _search(self, term: str) -> Optional[str]:
        """Run esearch and return first PMID, or None."""
        params: dict = {
            "db":      "pubmed",
            "term":    term,
            "retmax":  1,
            "retmode": "json",
        }
        if self._api_key:
            params["api_key"] = self._api_key
        resp = _get(PUBMED_SEARCH, params=params, rate_limiter=self._limiter)
        if resp is None:
            return None
        ids = resp.json().get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None

    def _fetch(self, pmid: str) -> Optional[dict]:
        """Run efetch for PMID and parse abstract XML."""
        params: dict = {
            "db":      "pubmed",
            "id":      pmid,
            "retmode": "xml",
            "rettype": "abstract",
        }
        if self._api_key:
            params["api_key"] = self._api_key
        resp = _get(PUBMED_FETCH, params=params, rate_limiter=self._limiter)
        if resp is None:
            return None
        xml = resp.text

        # Abstract: may have multiple <AbstractText> sections
        abs_parts = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", xml, re.DOTALL)
        abstract = " ".join(
            re.sub(r"<[^>]+>", "", p).strip() for p in abs_parts
        ).strip()

        doi_m = re.search(r'ArticleId IdType="doi">(.*?)</ArticleId>', xml)
        doi = doi_m.group(1).strip() if doi_m else ""

        title_m = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml, re.DOTALL)
        found_title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""

        year_m = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", xml, re.DOTALL)
        year = int(year_m.group(1)) if year_m else None

        return {
            "doi":      doi,
            "title":    found_title,
            "abstract": abstract,
            "year":     year,
            "source":   "pubmed",
        }

    def by_doi(self, doi: str) -> Optional[dict]:
        """Search PubMed using DOI as query term ([aid] field)."""
        if not doi:
            return None
        pmid = self._search(f"{doi}[aid]")
        if pmid is None:
            return None
        return self._fetch(pmid)

    def by_title(self, title: str) -> Optional[dict]:
        """Search PubMed by title; enforce title-similarity threshold."""
        if not title:
            return None
        pmid = self._search(title)
        if pmid is None:
            return None
        result = self._fetch(pmid)
        if result is None:
            return None
        if not _title_ok(title, result.get("title", "")):
            return None
        return result


# ---------------------------------------------------------------------------
# Client 4: OpenAlexHelper
# ---------------------------------------------------------------------------

class OpenAlexHelper:
    """
    OpenAlex Works API helper.

    No authentication required.  Polite pool: include mailto in User-Agent.
    Rate limit: 10 req/s polite; enforced conservatively at 8 req/s.

    Methods
    -------
    by_doi(doi)          -- direct DOI URL lookup; authoritative
    by_title(title)      -- free-text search; similarity enforced
    """

    def __init__(self) -> None:
        self._limiter = _RateLimiter(max_calls=8, period=1)

    def by_doi(self, doi: str) -> Optional[dict]:
        """Fetch OpenAlex work by DOI URL."""
        if not doi:
            return None
        url = f"{OPENALEX_WORKS}/https://doi.org/{doi}"
        resp = _get(
            url,
            params={"select": "title,abstract_inverted_index,doi,publication_year"},
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        data = resp.json()
        abstract = _decode_inverted_index(data.get("abstract_inverted_index"))
        doi_raw = data.get("doi", "")
        norm_doi = doi_raw.replace("https://doi.org/", "").strip() if doi_raw else doi
        return {
            "doi":      norm_doi,
            "title":    (data.get("title") or "").strip(),
            "abstract": abstract,
            "year":     data.get("publication_year"),
            "source":   "openalex",
        }

    def by_title(self, title: str) -> Optional[dict]:
        """Search OpenAlex by title; enforce title-similarity threshold."""
        if not title:
            return None
        resp = _get(
            OPENALEX_WORKS,
            params={
                "search":   title,
                "per-page": 1,
                "select":   "title,abstract_inverted_index,doi,publication_year",
            },
            rate_limiter=self._limiter,
        )
        if resp is None:
            return None
        results = resp.json().get("results", [])
        if not results:
            return None
        data = results[0]
        found_title = (data.get("title") or "").strip()
        if not _title_ok(title, found_title):
            return None
        abstract = _decode_inverted_index(data.get("abstract_inverted_index"))
        doi_raw = data.get("doi", "")
        doi = doi_raw.replace("https://doi.org/", "").strip() if doi_raw else ""
        return {
            "doi":      doi,
            "title":    found_title,
            "abstract": abstract,
            "year":     data.get("publication_year"),
            "source":   "openalex",
        }


# ---------------------------------------------------------------------------
# UnpaywallClient alias
# ---------------------------------------------------------------------------
# The ingest layer names this UnpaywallDownloader; expose UnpaywallClient
# here so discovery_funnel.py and other consumers have a single import point.
try:
    import sys as _sys, pathlib as _pathlib
    _ingest = _pathlib.Path(__file__).resolve().parent.parent / "ingest"
    if str(_ingest.parent) not in _sys.path:
        _sys.path.insert(0, str(_ingest.parent))
    from ingest.pdf_downloader import UnpaywallDownloader as UnpaywallClient  # type: ignore
except ImportError:
    UnpaywallClient = None  # type: ignore


# ---------------------------------------------------------------------------
# estimate_study_type()
# ---------------------------------------------------------------------------

_EMPIRICAL_MARKERS = (
    "randomized", "randomised", "controlled trial", "rct", "experiment",
    "quasi-experiment", "field study", "laboratory study",
    "within-subject", "between-subject", "participants were",
)
_META_MARKERS = (
    "meta-analysis", "meta analysis", "systematic review",
    "scoping review", "pooled estimate", "effect size",
)
_REVIEW_MARKERS = (
    "literature review", "narrative review", "integrative review",
    "we reviewed", "review of studies",
)
_CASE_MARKERS = (
    "case study", "case report", "single case", "descriptive study",
)
_SURVEY_MARKERS = (
    "survey", "questionnaire", "cross-sectional", "self-report",
    "respondents", "participants completed",
)


def estimate_study_type(abstract: str) -> str:
    """
    Classify the methodological study type from an abstract string.

    Returns one of:
      'meta_analysis'     -- pooled quantitative synthesis
      'systematic_review' -- structured literature synthesis
      'empirical_rct'     -- randomized / controlled experiment
      'empirical_other'   -- other primary empirical study
      'survey'            -- questionnaire / cross-sectional
      'case_study'        -- single-case or descriptive
      'review'            -- narrative or integrative review
      'unknown'           -- insufficient signal

    Deterministic keyword classifier — zero network calls.
    Called by abstract_collector_4c.py after a validated abstract is
    stored, to populate study_type in article_references.
    """
    if not abstract:
        return "unknown"
    text = abstract.lower()
    if any(m in text for m in _META_MARKERS):
        return "meta_analysis" if ("meta-analysis" in text or "meta analysis" in text) else "systematic_review"
    if any(m in text for m in _EMPIRICAL_MARKERS):
        return "empirical_rct" if any(m in text for m in ("randomized","randomised","controlled trial","rct")) else "empirical_other"
    if any(m in text for m in _SURVEY_MARKERS):
        return "survey"
    if any(m in text for m in _CASE_MARKERS):
        return "case_study"
    if any(m in text for m in _REVIEW_MARKERS):
        return "review"
    return "unknown"


# ---------------------------------------------------------------------------
# PaperFetcher  -- unified multi-source search facade
# ---------------------------------------------------------------------------

class PaperFetcher:
    """
    Unified facade over SemanticScholarClient, CrossRefClient,
    PubMedClient, and OpenAlexHelper.

    Provides a single .search(doi, title) entry-point that walks the
    four-source chain and returns the first validated result.

    This is the canonical import point for abstract-collection code.
    Consumers should use PaperFetcher rather than instantiating the
    individual clients directly.

    Usage:
        fetcher = PaperFetcher()
        result  = fetcher.search(doi="10.1016/j.buildenv.2020.106960")
        stype   = fetcher.estimate_study_type(result["abstract"])
    """

    def __init__(self) -> None:
        self._ss = SemanticScholarClient()
        self._cr = CrossRefClient()
        self._pm = PubMedClient()
        self._oa = OpenAlexHelper()

    def search(self, doi: str = "", title: str = "") -> Optional[dict]:
        """
        Walk SS -> CrossRef -> PubMed -> OpenAlex.
        Return first result with a non-empty abstract, or None.

        Result dict keys: doi, title, abstract, year, source.
        """
        sources: list = []
        if doi:
            sources += [
                (self._ss.by_doi,  doi),
                (self._cr.by_doi,  doi),
                (self._pm.by_doi,  doi),
                (self._oa.by_doi,  doi),
            ]
        if title:
            sources += [
                (self._ss.by_title, title),
                (self._cr.by_title, title),
                (self._pm.by_title, title),
                (self._oa.by_title, title),
            ]
        for fn, arg in sources:
            try:
                result = fn(arg)
                if result and (result.get("abstract") or "").strip():
                    return result
            except Exception:
                continue
        return None

    @staticmethod
    def estimate_study_type(abstract: str) -> str:
        """Delegate to module-level estimate_study_type()."""
        return estimate_study_type(abstract)
