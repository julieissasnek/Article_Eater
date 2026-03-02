#!/usr/bin/env python3
"""
Semantic Scholar Metadata Enrichment — Sprint METADATA-1
=========================================================

Created: 2026-02-25
Purpose: Enrich paper extraction data with bibliographic metadata from
         Semantic Scholar API. Populates: year, authors, journal, citation_count,
         influential_citation_count, references (DOIs), cited_by (DOIs),
         and semantic_scholar_id.

Usage modes:
  1. REPAIR (standalone): Enrich all existing extraction JSON files
       python scripts/semantic_scholar_enrichment.py --repair
  2. SINGLE DOI: Enrich one paper
       python scripts/semantic_scholar_enrichment.py --doi 10.1073/pnas.1301227110
  3. BATCH DOIs: Enrich from a file of DOIs
       python scripts/semantic_scholar_enrichment.py --doi-file data/doi_list.txt
  4. LIBRARY (import): Use enrich_paper() or batch_enrich() in setup()

Requires:
  - SEMANTIC_SCHOLAR_API_KEY environment variable (optional but recommended;
    unauthenticated = 100 req/5min; authenticated = 1 req/sec)

API reference: https://api.semanticscholar.org/api-docs/graph

Panel rationale (Session 7, 2026-02-25):
  - Quine: Temporal ordering for reflective equilibrium insertion order
  - Cartwright: Co-authorship networks for epistemic community detection
  - DerSimonian: Recency weighting for meta-analytic accumulation
  - Pollock: Citation graph for defeater/support argumentation structure
  - Good: Citation count as proxy for community acceptance weight
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.services.pdf_extraction import PaperMetadata

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
S2_API = "https://api.semanticscholar.org/graph/v1"
S2_KEY_ENV = "SEMANTIC_SCHOLAR_API_KEY"

# Fields we request from S2 /paper endpoint
S2_PAPER_FIELDS = ",".join([
    "title",
    "authors",
    "year",
    "venue",
    "publicationVenue",
    "externalIds",
    "citationCount",
    "influentialCitationCount",
    "references.externalIds",
    "citations.externalIds",
])

# Rate limiting: S2 free tier = 100 requests per 5 minutes
RATE_LIMIT_DELAY_SEC = 1.0          # Authenticated: 1 req/sec
RATE_LIMIT_DELAY_FREE_SEC = 3.1     # Unauthenticated: ~100 per 5 min
MAX_RETRIES = 3
BATCH_SAVE_INTERVAL = 25            # Save progress every N papers

logger = logging.getLogger("semantic_scholar_enrichment")


# ===========================================================================
# S2 API Client
# ===========================================================================

class SemanticScholarClient:
    """Thin client around S2 /paper endpoint with rate limiting + retry."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get(S2_KEY_ENV)
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key
        self.delay = RATE_LIMIT_DELAY_SEC if self.api_key else RATE_LIMIT_DELAY_FREE_SEC
        self._last_request_time = 0.0

    def _rate_limit(self):
        """Enforce minimum delay between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    def get_paper_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Fetch paper metadata from S2 by DOI.

        Returns raw S2 response dict or None on failure.
        """
        url = f"{S2_API}/paper/DOI:{doi}"
        params = {"fields": S2_PAPER_FIELDS}

        for attempt in range(1, MAX_RETRIES + 1):
            self._rate_limit()
            try:
                r = self.session.get(url, params=params, timeout=30)
                if r.status_code == 200:
                    return r.json()
                elif r.status_code == 404:
                    logger.warning("DOI not found in S2: %s", doi)
                    return None
                elif r.status_code == 429:
                    wait = 2 ** attempt
                    logger.info("Rate limited by S2; waiting %ds (attempt %d/%d)", wait, attempt, MAX_RETRIES)
                    time.sleep(wait)
                    continue
                else:
                    logger.warning("S2 returned %d for DOI %s (attempt %d/%d)", r.status_code, doi, attempt, MAX_RETRIES)
                    if attempt < MAX_RETRIES:
                        time.sleep(2 ** attempt)
                        continue
                    return None
            except requests.RequestException as e:
                logger.warning("Request error for DOI %s: %s (attempt %d/%d)", doi, e, attempt, MAX_RETRIES)
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                return None
        return None


# ===========================================================================
# S2 Response → PaperMetadata
# ===========================================================================

def _extract_doi(external_ids: Optional[Dict]) -> str:
    """Pull DOI from S2 externalIds dict."""
    if not external_ids:
        return ""
    return external_ids.get("DOI", "") or ""


def _extract_reference_dois(references: Optional[List[Dict]]) -> List[str]:
    """Extract DOIs from S2 references list."""
    if not references:
        return []
    dois = []
    for ref in references:
        ext = ref.get("externalIds") or {}
        doi = ext.get("DOI")
        if doi:
            dois.append(doi)
    return dois


def _extract_citation_dois(citations: Optional[List[Dict]]) -> List[str]:
    """Extract DOIs from S2 citations list."""
    if not citations:
        return []
    dois = []
    for cit in citations:
        ext = cit.get("externalIds") or {}
        doi = ext.get("DOI")
        if doi:
            dois.append(doi)
    return dois


def s2_to_paper_metadata(s2_data: Dict[str, Any], original_doi: str = "") -> PaperMetadata:
    """
    Convert raw Semantic Scholar API response to PaperMetadata dataclass.
    """
    # Authors: S2 returns list of {"authorId": ..., "name": "..."}
    authors_raw = s2_data.get("authors") or []
    authors = [a.get("name", "") for a in authors_raw if a.get("name")]

    # Journal: prefer publicationVenue.name, fall back to venue string
    pub_venue = s2_data.get("publicationVenue") or {}
    journal = pub_venue.get("name") or s2_data.get("venue") or ""

    # External IDs
    ext_ids = s2_data.get("externalIds") or {}
    doi = _extract_doi(ext_ids) or original_doi

    return PaperMetadata(
        doi=doi,
        title=s2_data.get("title") or "",
        authors=authors,
        year=s2_data.get("year"),
        journal=journal,
        citation_count=s2_data.get("citationCount"),
        influential_citation_count=s2_data.get("influentialCitationCount"),
        references=_extract_reference_dois(s2_data.get("references")),
        cited_by=_extract_citation_dois(s2_data.get("citations")),
        semantic_scholar_id=s2_data.get("paperId"),
        enriched=True,
        enriched_at=datetime.now(timezone.utc).isoformat(),
        enrichment_source="semantic_scholar",
    )


# ===========================================================================
# Public API (for import by setup() and orchestrator)
# ===========================================================================

def enrich_paper(doi: str, client: Optional[SemanticScholarClient] = None) -> Optional[PaperMetadata]:
    """
    Enrich a single paper by DOI.

    Returns PaperMetadata or None if DOI not found.
    """
    if client is None:
        client = SemanticScholarClient()
    s2_data = client.get_paper_by_doi(doi)
    if s2_data is None:
        return None
    return s2_to_paper_metadata(s2_data, original_doi=doi)


def batch_enrich(
    dois: List[str],
    client: Optional[SemanticScholarClient] = None,
    progress_callback=None,
) -> Dict[str, PaperMetadata]:
    """
    Enrich a batch of DOIs. Returns dict mapping DOI → PaperMetadata.

    Papers not found in S2 are omitted from the result dict.
    progress_callback(i, total, doi, success) is called after each paper.
    """
    if client is None:
        client = SemanticScholarClient()

    results: Dict[str, PaperMetadata] = {}
    total = len(dois)

    for i, doi in enumerate(dois, 1):
        doi_clean = doi.strip()
        if not doi_clean:
            continue
        metadata = enrich_paper(doi_clean, client)
        success = metadata is not None
        if success:
            results[doi_clean] = metadata
        if progress_callback:
            progress_callback(i, total, doi_clean, success)
        else:
            status = "OK" if success else "NOT FOUND"
            logger.info("[%d/%d] %s — %s", i, total, doi_clean, status)

    return results


# ===========================================================================
# Repair Mode: Enrich existing extraction JSON files
# ===========================================================================

def repair_extractions(
    extractions_dir: Path,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Scan extraction JSON files, enrich each with S2 metadata, write back.

    If output_dir is specified, writes enriched copies there (non-destructive).
    Otherwise, updates files in place.

    Returns summary dict with counts.
    """
    client = SemanticScholarClient()
    if output_dir is None:
        output_dir = extractions_dir

    # Find all per-paper extraction files (DOI-named, not batch files)
    extraction_files = sorted(extractions_dir.glob("10.*.json"))
    logger.info("Found %d per-paper extraction files in %s", len(extraction_files), extractions_dir)

    stats = {"total": len(extraction_files), "enriched": 0, "skipped": 0, "not_found": 0, "errors": 0}

    for i, fpath in enumerate(extraction_files, 1):
        try:
            with open(fpath) as f:
                data = json.load(f)

            # Skip if already enriched
            if data.get("paper_metadata", {}).get("enriched"):
                stats["skipped"] += 1
                logger.debug("[%d/%d] Already enriched: %s", i, stats["total"], fpath.name)
                continue

            # Extract DOI from filename or data
            doi = data.get("doi", "")
            if not doi:
                # Filename is DOI with _ replacing /
                doi = fpath.stem.replace("_", "/", 1)

            if dry_run:
                logger.info("[%d/%d] DRY RUN: would enrich %s", i, stats["total"], doi)
                continue

            metadata = enrich_paper(doi, client)
            if metadata is None:
                stats["not_found"] += 1
                logger.warning("[%d/%d] Not found in S2: %s", i, stats["total"], doi)
                continue

            # Merge metadata into extraction data
            data["paper_metadata"] = metadata.to_dict()

            # Also backfill top-level fields if missing
            if not data.get("year") and metadata.year:
                data["year"] = metadata.year
            if not data.get("journal") and metadata.journal:
                data["journal"] = metadata.journal
            if isinstance(data.get("authors"), str) and metadata.authors:
                data["authors_structured"] = metadata.authors

            # Write back
            out_path = output_dir / fpath.name
            with open(out_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            stats["enriched"] += 1
            logger.info("[%d/%d] Enriched: %s (year=%s, citations=%s, refs=%d, cited_by=%d)",
                        i, stats["total"], doi, metadata.year,
                        metadata.citation_count, len(metadata.references), len(metadata.cited_by))

            # Periodic save of progress summary
            if i % BATCH_SAVE_INTERVAL == 0:
                _save_progress(output_dir, stats, i)

        except Exception as e:
            stats["errors"] += 1
            logger.error("[%d/%d] Error processing %s: %s", i, stats["total"], fpath.name, e)

    # Final summary
    _save_progress(output_dir, stats, stats["total"])
    return stats


def repair_batch_extractions(
    extractions_dir: Path,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Scan batch extraction JSON files (full_extraction_*.json, classified_extraction_*.json),
    enrich each paper entry within them.
    """
    client = SemanticScholarClient()
    if output_dir is None:
        output_dir = extractions_dir

    batch_files = sorted(
        list(extractions_dir.glob("full_extraction_*.json"))
        + list(extractions_dir.glob("classified_extraction_*.json"))
        + list(extractions_dir.glob("two_pass_extraction_*.json"))
    )
    logger.info("Found %d batch extraction files", len(batch_files))

    stats = {"total_papers": 0, "enriched": 0, "not_found": 0, "skipped": 0, "errors": 0}

    for bf in batch_files:
        try:
            with open(bf) as f:
                batch_data = json.load(f)

            papers = batch_data if isinstance(batch_data, list) else batch_data.get("papers", [])
            logger.info("Processing batch file %s (%d papers)", bf.name, len(papers))

            for paper in papers:
                stats["total_papers"] += 1
                doi = paper.get("doi", "")
                if not doi:
                    continue

                if paper.get("paper_metadata", {}).get("enriched"):
                    stats["skipped"] += 1
                    continue

                if dry_run:
                    continue

                metadata = enrich_paper(doi, client)
                if metadata is None:
                    stats["not_found"] += 1
                    continue

                paper["paper_metadata"] = metadata.to_dict()
                if not paper.get("year") and metadata.year:
                    paper["year"] = metadata.year
                stats["enriched"] += 1

            # Write back
            if not dry_run:
                out_path = output_dir / bf.name
                with open(out_path, "w") as f:
                    json.dump(batch_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            stats["errors"] += 1
            logger.error("Error processing batch file %s: %s", bf.name, e)

    return stats


def _save_progress(output_dir: Path, stats: Dict, processed: int):
    """Write enrichment progress to a sidecar file."""
    progress_path = output_dir / "_enrichment_progress.json"
    progress = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "processed": processed,
        **stats,
    }
    with open(progress_path, "w") as f:
        json.dump(progress, f, indent=2)


# ===========================================================================
# Citation Graph Export (for argumentation structure)
# ===========================================================================

def build_citation_graph(extractions_dir: Path) -> Dict[str, Any]:
    """
    Build a citation graph from enriched extraction files.

    Returns {
      "nodes": [{"doi": ..., "year": ..., "title": ..., "citation_count": ...}],
      "edges": [{"source": doi_A, "target": doi_B, "type": "cites"}],
      "stats": {...}
    }

    An edge (A → B) means paper A cites paper B.
    This is the argumentation structure: if A cites B, A may support, extend,
    or challenge B's claims.
    """
    extraction_files = sorted(extractions_dir.glob("10.*.json"))
    corpus_dois = set()
    nodes = []
    edges = []

    # First pass: collect all DOIs in our corpus
    for fpath in extraction_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
            doi = data.get("doi", fpath.stem.replace("_", "/", 1))
            corpus_dois.add(doi)
        except Exception as e:
            logger.debug(f"Skipped: {e}")
            continue

    # Second pass: build graph
    for fpath in extraction_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
            doi = data.get("doi", fpath.stem.replace("_", "/", 1))
            pm = data.get("paper_metadata", {})

            nodes.append({
                "doi": doi,
                "year": pm.get("year") or data.get("year"),
                "title": pm.get("title") or data.get("title", ""),
                "citation_count": pm.get("citation_count"),
                "authors": pm.get("authors", []),
            })

            # Edges: this paper cites other papers in our corpus
            for ref_doi in pm.get("references", []):
                if ref_doi in corpus_dois:
                    edges.append({"source": doi, "target": ref_doi, "type": "cites"})

            # Reverse edges: papers in our corpus cite this paper
            for citer_doi in pm.get("cited_by", []):
                if citer_doi in corpus_dois:
                    edges.append({"source": citer_doi, "target": doi, "type": "cites"})

        except Exception as e:
            logger.debug(f"Skipped: {e}")
            continue

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {
        "nodes": nodes,
        "edges": unique_edges,
        "stats": {
            "n_papers": len(nodes),
            "n_intra_corpus_citations": len(unique_edges),
            "corpus_dois": len(corpus_dois),
            "year_range": (
                min((n["year"] for n in nodes if n["year"]), default=None),
                max((n["year"] for n in nodes if n["year"]), default=None),
            ),
        },
    }


# ===========================================================================
# CrossRef Ingestion (for comparison and gap-filling)
# ===========================================================================

def crossref_to_paper_metadata(cr_data: Dict[str, Any]) -> PaperMetadata:
    """
    Convert a CrossRef API record to PaperMetadata.

    CrossRef provides complementary metadata: reliable publication dates,
    publisher info, volume/issue/pages, ISSN. S2 provides citation counts
    and reference/cited_by DOI lists. We merge both sources.
    """
    # Authors: CrossRef returns [{"given": "...", "family": "..."}, ...]
    authors_raw = cr_data.get("author", [])
    authors = []
    for a in authors_raw:
        given = a.get("given", "")
        family = a.get("family", "")
        name = f"{given} {family}".strip() if given or family else ""
        if name:
            authors.append(name)

    # Year: CrossRef stores dates as {"date-parts": [[2020, 3, 15]]}
    year = None
    for date_field in ["published-print", "published-online", "issued", "created"]:
        date_obj = cr_data.get(date_field, {})
        date_parts = date_obj.get("date-parts", [[]])
        if date_parts and date_parts[0] and date_parts[0][0]:
            year = date_parts[0][0]
            break

    # Journal: container-title is a list
    container = cr_data.get("container-title", [])
    journal = container[0] if container else ""

    # Title: also a list
    title_list = cr_data.get("title", [])
    title = title_list[0] if title_list else ""

    # References: CrossRef provides reference DOIs
    refs = []
    for ref in cr_data.get("reference", []):
        ref_doi = ref.get("DOI", "")
        if ref_doi:
            refs.append(ref_doi)

    return PaperMetadata(
        doi=cr_data.get("DOI", ""),
        title=title,
        authors=authors,
        year=year,
        journal=journal,
        volume=cr_data.get("volume"),
        issue=cr_data.get("issue"),
        pages=cr_data.get("page"),
        publisher=cr_data.get("publisher", ""),
        citation_count=cr_data.get("is-referenced-by-count"),
        references=refs,
        enriched=True,
        enriched_at=datetime.now(timezone.utc).isoformat(),
        enrichment_source="crossref",
    )


def merge_metadata(s2_meta: Optional[PaperMetadata], cr_meta: Optional[PaperMetadata]) -> PaperMetadata:
    """
    Merge S2 and CrossRef metadata, preferring S2 for citation graph data
    and CrossRef for publication details (volume, issue, pages, publisher).
    """
    if s2_meta is None and cr_meta is None:
        return PaperMetadata()
    if s2_meta is None:
        return cr_meta
    if cr_meta is None:
        return s2_meta

    # Start with S2 as base (has citation counts, references, cited_by)
    merged = PaperMetadata(
        doi=s2_meta.doi or cr_meta.doi,
        title=s2_meta.title or cr_meta.title,
        authors=s2_meta.authors if s2_meta.authors else cr_meta.authors,
        year=s2_meta.year or cr_meta.year,
        journal=s2_meta.journal or cr_meta.journal,
        # CrossRef has better volume/issue/pages data
        volume=cr_meta.volume or s2_meta.volume,
        issue=cr_meta.issue or s2_meta.issue,
        pages=cr_meta.pages or s2_meta.pages,
        publisher=cr_meta.publisher or s2_meta.publisher,
        # S2 has better citation data
        citation_count=s2_meta.citation_count if s2_meta.citation_count is not None else cr_meta.citation_count,
        influential_citation_count=s2_meta.influential_citation_count,
        # S2 references are DOI-resolved; CrossRef may have more
        references=s2_meta.references if s2_meta.references else cr_meta.references,
        cited_by=s2_meta.cited_by,  # CrossRef doesn't provide cited_by DOIs
        semantic_scholar_id=s2_meta.semantic_scholar_id,
        enriched=True,
        enriched_at=datetime.now(timezone.utc).isoformat(),
        enrichment_source="semantic_scholar+crossref",
    )
    return merged


def ingest_crossref_file(
    crossref_path: Path,
    extractions_dir: Path,
    merge_with_s2: bool = True,
) -> Dict[str, Any]:
    """
    Ingest a CrossRef data file and merge with existing extraction metadata.

    The CrossRef file can be:
    - A JSON array of CrossRef records (from CrossRef API bulk download)
    - A JSON object with "items" or "message" containing records
    - A JSONL file (one JSON record per line)

    Args:
        crossref_path: Path to CrossRef data file
        extractions_dir: Directory with extraction JSON files
        merge_with_s2: If True, merge CrossRef with existing S2 metadata

    Returns:
        Stats dict with counts of papers processed
    """
    stats = {"total": 0, "merged": 0, "new": 0, "skipped": 0, "errors": 0}

    # Load CrossRef data
    logger.info("Loading CrossRef data from %s", crossref_path)
    cr_records = {}

    suffix = crossref_path.suffix.lower()
    if suffix == ".jsonl":
        with open(crossref_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    doi = record.get("DOI", "")
                    if doi:
                        cr_records[doi.lower()] = record
                except json.JSONDecodeError:
                    stats["errors"] += 1
    else:
        with open(crossref_path) as f:
            data = json.load(f)

        # Handle different CrossRef formats
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("items", data.get("message", {}).get("items", [data]))
        else:
            records = []

        for record in records:
            doi = record.get("DOI", "")
            if doi:
                cr_records[doi.lower()] = record

    logger.info("Loaded %d CrossRef records", len(cr_records))
    stats["total"] = len(cr_records)

    # Match to extraction files and merge
    extraction_files = sorted(extractions_dir.glob("10.*.json"))
    for fpath in extraction_files:
        try:
            with open(fpath) as f:
                ext_data = json.load(f)

            doi = ext_data.get("doi", fpath.stem.replace("_", "/", 1))
            doi_lower = doi.lower()

            if doi_lower not in cr_records:
                continue

            cr_meta = crossref_to_paper_metadata(cr_records[doi_lower])

            if merge_with_s2 and ext_data.get("paper_metadata", {}).get("enriched"):
                # Merge with existing S2 metadata
                existing = PaperMetadata(**ext_data["paper_metadata"]) if ext_data.get("paper_metadata") else None
                merged = merge_metadata(existing, cr_meta)
                ext_data["paper_metadata"] = merged.to_dict()
                stats["merged"] += 1
            else:
                ext_data["paper_metadata"] = cr_meta.to_dict()
                stats["new"] += 1

            # Backfill top-level fields
            if not ext_data.get("year") and cr_meta.year:
                ext_data["year"] = cr_meta.year
            if not ext_data.get("journal") and cr_meta.journal:
                ext_data["journal"] = cr_meta.journal

            with open(fpath, "w") as f:
                json.dump(ext_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            stats["errors"] += 1
            logger.error("Error processing %s with CrossRef: %s", fpath.name, e)

    logger.info("CrossRef ingestion complete: %s", stats)
    return stats


# ===========================================================================
# CLI
# ===========================================================================

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Semantic Scholar Metadata Enrichment for Article Eater",
    )
    parser.add_argument("--repair", action="store_true",
                        help="Enrich all existing per-paper extraction files")
    parser.add_argument("--repair-batches", action="store_true",
                        help="Enrich all batch extraction files")
    parser.add_argument("--doi", type=str,
                        help="Enrich a single DOI and print result")
    parser.add_argument("--doi-file", type=str,
                        help="Enrich DOIs listed in a text file (one per line)")
    parser.add_argument("--build-graph", action="store_true",
                        help="Build citation graph from enriched extractions")
    parser.add_argument("--crossref-file", type=str,
                        help="Ingest CrossRef data file (JSON or JSONL) and merge with S2 metadata")
    parser.add_argument("--no-merge", action="store_true",
                        help="With --crossref-file: don't merge with existing S2 metadata, overwrite instead")
    parser.add_argument("--extractions-dir", type=str,
                        default=str(REPO_ROOT / "data" / "extractions"),
                        help="Directory containing extraction JSON files")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory (defaults to extractions-dir, in-place)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be enriched without making changes")
    args = parser.parse_args()

    extractions_dir = Path(args.extractions_dir)
    output_dir = Path(args.output_dir) if args.output_dir else None

    if args.doi:
        metadata = enrich_paper(args.doi)
        if metadata:
            print(json.dumps(metadata.to_dict(), indent=2))
        else:
            print(f"Not found in Semantic Scholar: {args.doi}", file=sys.stderr)
            sys.exit(1)

    elif args.doi_file:
        with open(args.doi_file) as f:
            dois = [line.strip() for line in f if line.strip()]
        results = batch_enrich(dois)
        print(f"\nEnriched {len(results)}/{len(dois)} papers")
        # Write results
        out_path = extractions_dir / "enrichment_results.json"
        with open(out_path, "w") as f:
            json.dump({doi: m.to_dict() for doi, m in results.items()}, f, indent=2)
        print(f"Results written to {out_path}")

    elif args.repair:
        stats = repair_extractions(extractions_dir, output_dir, dry_run=args.dry_run)
        print(f"\nRepair complete: {json.dumps(stats, indent=2)}")

    elif args.repair_batches:
        stats = repair_batch_extractions(extractions_dir, output_dir, dry_run=args.dry_run)
        print(f"\nBatch repair complete: {json.dumps(stats, indent=2)}")

    elif args.crossref_file:
        cr_path = Path(args.crossref_file)
        stats = ingest_crossref_file(
            cr_path, extractions_dir,
            merge_with_s2=not args.no_merge,
        )
        print(f"\nCrossRef ingestion complete: {json.dumps(stats, indent=2)}")

    elif args.build_graph:
        graph = build_citation_graph(extractions_dir)
        out_path = extractions_dir / "citation_graph.json"
        with open(out_path, "w") as f:
            json.dump(graph, f, indent=2)
        print(f"Citation graph: {graph['stats']}")
        print(f"Written to {out_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
