"""
pdf_downloader.py -- Legal open-access PDF downloaders for Phase 5.

Provides two classes used exclusively by pdf_acquisition_engine.py.
Neither class is ever called during harvest or triage stages.

Classes
-------
UnpaywallDownloader
    Queries the Unpaywall REST API for the best open-access PDF URL,
    then downloads and validates the file.  Always tried FIRST in the
    Phase 5 cascade.

OpenAlexOADownloader
    Fetches the OpenAlex work record for a DOI and inspects:
      1. open_access.oa_url           (direct OA PDF link)
      2. primary_location.pdf_url     (publisher-deposited PDF)
      3. best_oa_location.pdf_url     (best available OA copy)
    Downloads and validates the first populated URL it finds.
    Tried SECOND in the Phase 5 cascade, only when Unpaywall fails.

Both classes
    - Enforce a per-instance rate limiter (token-bucket, thread-safe).
    - Validate downloaded files via magic-byte check (first 4 bytes == b'%PDF')
      AND minimum file size, not by Content-Type header alone.  This fixes
      the silent-discard defect in triage_engine._download_direct() which
      rejected valid PDFs served with Content-Type: binary/octet-stream.
    - Return the local file path on success, None on any failure.
    - Never raise; all exceptions are caught and logged to stderr.

IMPORTANT: scidownl is NOT here.  It is gated behind the Phase 5B
policy check in pdf_acquisition_engine.py and imported from
harvest_layer.acquire_pdf_scidownl() only when that gate passes.
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from typing import Optional

import requests

UA          = "KA-PDFAcquisition/5.0 (mailto:student@ucsd.edu)"
TIMEOUT     = 30          # seconds per HTTP call
MIN_PDF_BYTES = 1_024     # files smaller than this are rejected
MAX_RETRIES   = 2         # retry once on 429 / 5xx

UNPAYWALL_BASE  = "https://api.unpaywall.org/v2"
OPENALEX_WORKS  = "https://api.openalex.org/works"
UNPAYWALL_EMAIL = "student@ucsd.edu"


# ── Rate limiter (mirrors paper_fetcher._RateLimiter) ─────────────────────────

class _RateLimiter:
    def __init__(self, max_calls: int, period: float) -> None:
        self._max   = max_calls
        self._period = period
        self._lock  = threading.Lock()
        self._calls: list[float] = []

    def acquire(self) -> None:
        while True:
            with self._lock:
                now    = time.monotonic()
                cutoff = now - self._period
                self._calls = [t for t in self._calls if t > cutoff]
                if len(self._calls) < self._max:
                    self._calls.append(now)
                    return
                wait = self._calls[0] - cutoff
            time.sleep(max(wait, 0.01))


# ── PDF validation ─────────────────────────────────────────────────────────────

def _is_valid_pdf_bytes(data: bytes) -> bool:
    """
    Validate downloaded bytes as a PDF.

    Two checks — both must pass:
      1. Magic bytes: first 4 bytes must be b'%PDF'.
      2. Size: at least MIN_PDF_BYTES bytes.

    Deliberately does NOT check Content-Type so that papers served with
    Content-Type: binary/octet-stream are not silently rejected.
    """
    return len(data) > MIN_PDF_BYTES and data[:4] == b"%PDF"


def _save_pdf(data: bytes, out_path: str) -> bool:
    """Write validated PDF bytes to disk. Returns True on success."""
    try:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_bytes(data)
        return True
    except OSError as exc:
        print(f"  [pdf_downloader] Write error {out_path}: {exc}", file=sys.stderr)
        return False


# ── Shared HTTP fetch ─────────────────────────────────────────────────────────

def _fetch_bytes(
    url: str,
    *,
    rate_limiter: Optional[_RateLimiter] = None,
) -> Optional[bytes]:
    """
    GET a URL, returning raw bytes or None on failure.
    Retries once on 429 (respecting Retry-After) and once on 5xx.
    """
    headers = {"User-Agent": UA}
    for attempt in range(MAX_RETRIES + 1):
        if rate_limiter:
            rate_limiter.acquire()
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
            if resp.status_code == 200:
                return resp.content
            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", 2 ** attempt))
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            return None  # 4xx other than 429 — not retryable
        except requests.Timeout:
            time.sleep(2 ** attempt)
        except requests.RequestException:
            return None
    return None


# ── Client 1: Unpaywall ───────────────────────────────────────────────────────

class UnpaywallDownloader:
    """
    Step 1 in the Phase 5 acquisition cascade.

    Queries Unpaywall for the best open-access PDF URL for a DOI, then
    downloads and validates the PDF.

    Rate: 10 req/s (well within Unpaywall's limit for polite crawlers).
    Email is required by Unpaywall's acceptable-use policy.

    Usage:
        dl = UnpaywallDownloader()
        path = dl.try_download("10.1016/j.buildenv.2020.106960", "/pdfs/out.pdf")
        # path is the local file path on success, None on failure
    """

    SOURCE_NAME = "unpaywall"

    def __init__(self, email: str = UNPAYWALL_EMAIL) -> None:
        self._email   = email
        self._limiter = _RateLimiter(max_calls=10, period=1)

    def _get_oa_url(self, doi: str) -> Optional[str]:
        """Return the best OA PDF URL from Unpaywall, or None."""
        if rate_limiter := self._limiter:
            rate_limiter.acquire()
        try:
            resp = requests.get(
                f"{UNPAYWALL_BASE}/{doi}",
                params={"email": self._email},
                headers={"User-Agent": UA},
                timeout=15,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            best = data.get("best_oa_location") or {}
            url  = best.get("url_for_pdf") or best.get("url")
            # Reject HTML landing pages masquerading as PDF links
            if url and not any(x in url for x in [".pdf", "pdf", "download", "content"]):
                # If URL doesn't hint at a PDF, still try it — magic-byte check catches junk
                pass
            return url or None
        except Exception as exc:
            print(f"  [unpaywall] API error for {doi}: {exc}", file=sys.stderr)
            return None

    def try_download(self, doi: str, out_path: str) -> Optional[str]:
        """
        Try to download the open-access PDF for `doi`.

        Returns local path on success, None on any failure.
        Never raises.
        """
        if not doi:
            return None
        oa_url = self._get_oa_url(doi)
        if not oa_url:
            return None
        data = _fetch_bytes(oa_url, rate_limiter=self._limiter)
        if data is None:
            return None
        if not _is_valid_pdf_bytes(data):
            print(
                f"  [unpaywall] Downloaded content for {doi} failed PDF validation "
                f"(size={len(data)}, magic={data[:4]!r})",
                file=sys.stderr,
            )
            return None
        if _save_pdf(data, out_path):
            return out_path
        return None


# ── Client 2: OpenAlex OA URL ─────────────────────────────────────────────────

class OpenAlexOADownloader:
    """
    Step 2 in the Phase 5 acquisition cascade.

    Fetches the OpenAlex work record for a DOI and inspects three OA URL
    fields in priority order:
      1. open_access.oa_url
      2. primary_location.pdf_url
      3. best_oa_location.pdf_url  (inside open_access)

    Downloads the first non-null URL found and validates it as a PDF.

    This is the fix for triage_engine._download_direct() (Defect 4), which
    used the raw harvest-time `url` field and never called the OpenAlex API.

    Rate: 8 req/s (conservative; OpenAlex polite pool allows 10 req/s).
    """

    SOURCE_NAME = "openalex_oa"

    def __init__(self) -> None:
        self._limiter = _RateLimiter(max_calls=8, period=1)

    def _get_oa_url(self, doi: str) -> Optional[str]:
        """
        Call the OpenAlex works API and return the best available OA PDF URL.
        Checks three fields in priority order; returns the first non-null one.
        """
        if self._limiter:
            self._limiter.acquire()
        try:
            resp = requests.get(
                f"{OPENALEX_WORKS}/https://doi.org/{doi}",
                params={"select": "open_access,primary_location,best_oa_location"},
                headers={"User-Agent": UA},
                timeout=15,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()

            # Priority 1: open_access.oa_url
            oa = data.get("open_access") or {}
            url = oa.get("oa_url")
            if url:
                return url

            # Priority 2: primary_location.pdf_url
            primary = data.get("primary_location") or {}
            url = primary.get("pdf_url")
            if url:
                return url

            # Priority 3: best_oa_location inside open_access dict
            # (Some OA records store this as a nested object, not the top-level field)
            best = oa.get("best_oa_location") or {}
            url  = best.get("pdf_url") or best.get("url_for_pdf")
            return url or None

        except Exception as exc:
            print(f"  [openalex_oa] API error for {doi}: {exc}", file=sys.stderr)
            return None

    def try_download(self, doi: str, out_path: str) -> Optional[str]:
        """
        Try to download an OA PDF for `doi` via OpenAlex.

        Returns local path on success, None on any failure.
        Never raises.
        """
        if not doi:
            return None
        oa_url = self._get_oa_url(doi)
        if not oa_url:
            return None
        data = _fetch_bytes(oa_url, rate_limiter=self._limiter)
        if data is None:
            return None
        if not _is_valid_pdf_bytes(data):
            print(
                f"  [openalex_oa] Downloaded content for {doi} failed PDF validation "
                f"(size={len(data)}, magic={data[:4]!r})",
                file=sys.stderr,
            )
            return None
        if _save_pdf(data, out_path):
            return out_path
        return None
