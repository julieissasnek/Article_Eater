"""
BibTeX Ingestion Service for Article Eater.

BIB-7: Takes matched PDFs with BibTeX metadata and ingests them into the AE pipeline.

This service:
1. Reads matched papers (from BibTeX import wizard or direct API)
2. Creates proper input bundles (paper.json + PDF)
3. Runs the AE extraction pipeline
4. Returns structured results

Created: 2026-02-09
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of ingesting a single paper."""

    paper_id: str
    status: str  # "success", "partial", "failed", "skipped"
    pdf_path: str
    output_dir: Optional[str] = None
    n_claims: int = 0
    n_rules: int = 0
    error: Optional[str] = None
    pipeline_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "status": self.status,
            "pdf_path": self.pdf_path,
            "output_dir": self.output_dir,
            "n_claims": self.n_claims,
            "n_rules": self.n_rules,
            "error": self.error,
        }


@dataclass
class BatchIngestionResult:
    """Result of batch ingestion."""

    total: int
    succeeded: int
    failed: int
    skipped: int
    results: List[IngestionResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "results": [r.to_dict() for r in self.results],
        }


class BibTeXIngestionService:
    """
    Service for ingesting matched PDFs with BibTeX metadata into Article Eater.

    Usage:
        service = BibTeXIngestionService(output_base="/path/to/outputs")

        # From matched papers JSON (from BibTeX import wizard)
        result = service.ingest_from_json("/path/to/papers.json")

        # Or from individual paper dict
        result = service.ingest_paper(paper_dict)
    """

    def __init__(
        self,
        output_base: Optional[Path] = None,
        profile: str = "standard",
        hitl: str = "auto",
        cleanup_bundles: bool = True,
    ):
        """
        Initialize the ingestion service.

        Args:
            output_base: Base directory for pipeline outputs. Defaults to ~/ae_outputs.
            profile: Extraction profile (standard, thorough, quick).
            hitl: Human-in-the-loop mode (auto, confirm, skip).
            cleanup_bundles: Whether to clean up temporary input bundles after processing.
        """
        self.output_base = Path(output_base or Path.home() / "ae_outputs").expanduser()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.profile = profile
        self.hitl = hitl
        self.cleanup_bundles = cleanup_bundles

        # Import pipeline lazily to avoid circular imports
        self._pipeline = None

    def _get_pipeline(self):
        """Lazy import of pipeline to avoid circular imports."""
        if self._pipeline is None:
            from app.tasks.pipeline import process_paper_bundle
            self._pipeline = process_paper_bundle
        return self._pipeline

    def ingest_from_json(self, json_path: Path) -> BatchIngestionResult:
        """
        Ingest papers from a matched papers JSON file.

        Args:
            json_path: Path to JSON file containing list of matched papers.
                       Each paper should have: title, authors, year, abstract, pdf_path, etc.

        Returns:
            BatchIngestionResult with status of all ingestions.
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"Papers JSON not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)

        if not isinstance(papers, list):
            papers = [papers]

        return self.ingest_batch(papers)

    def ingest_batch(self, papers: List[Dict[str, Any]]) -> BatchIngestionResult:
        """
        Ingest a batch of papers.

        Args:
            papers: List of paper dicts with metadata and pdf_path.

        Returns:
            BatchIngestionResult with status of all ingestions.
        """
        results = []
        succeeded = 0
        failed = 0
        skipped = 0

        for i, paper in enumerate(papers):
            logger.info(f"Processing paper {i+1}/{len(papers)}: {paper.get('title', 'Unknown')[:50]}")

            try:
                result = self.ingest_paper(paper)
                results.append(result)

                if result.status == "success":
                    succeeded += 1
                elif result.status == "failed":
                    failed += 1
                elif result.status == "skipped":
                    skipped += 1
                else:  # partial
                    succeeded += 1

            except Exception as e:
                logger.error(f"Failed to ingest paper: {e}")
                results.append(IngestionResult(
                    paper_id=paper.get("paper_id", f"unknown_{i}"),
                    status="failed",
                    pdf_path=paper.get("pdf_path", "unknown"),
                    error=str(e),
                ))
                failed += 1

        return BatchIngestionResult(
            total=len(papers),
            succeeded=succeeded,
            failed=failed,
            skipped=skipped,
            results=results,
        )

    def ingest_paper(self, paper: Dict[str, Any]) -> IngestionResult:
        """
        Ingest a single paper into the AE pipeline.

        Args:
            paper: Paper dict with metadata and pdf_path.
                   Expected fields: title, authors, year, abstract, pdf_path
                   Optional: doi, venue, paper_id

        Returns:
            IngestionResult with status and extracted claims/rules count.
        """
        # Get PDF path
        pdf_path = paper.get("pdf_path")
        if not pdf_path:
            return IngestionResult(
                paper_id=paper.get("paper_id", "unknown"),
                status="skipped",
                pdf_path="",
                error="No pdf_path provided",
            )

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return IngestionResult(
                paper_id=paper.get("paper_id", "unknown"),
                status="skipped",
                pdf_path=str(pdf_path),
                error=f"PDF not found: {pdf_path}",
            )

        # Generate paper_id if not provided
        paper_id = paper.get("paper_id")
        if not paper_id:
            # Use SHA256 of PDF for consistent ID
            pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]
            paper_id = f"bibtex:{pdf_hash}"

        # Create input bundle
        try:
            bundle_dir = self._create_input_bundle(paper, pdf_path, paper_id)
        except Exception as e:
            return IngestionResult(
                paper_id=paper_id,
                status="failed",
                pdf_path=str(pdf_path),
                error=f"Failed to create input bundle: {e}",
            )

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_id = paper_id.replace(":", "_").replace("/", "_")
        output_dir = self.output_base / f"{safe_id}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run pipeline
        try:
            pipeline_fn = self._get_pipeline()
            result = pipeline_fn(
                in_dir=bundle_dir,
                out_dir=output_dir,
                profile=self.profile,
                hitl=self.hitl,
            )

            status = result.get("status", "unknown").lower()
            if status == "success":
                final_status = "success"
            elif status == "partial_success":
                final_status = "partial"
            else:
                final_status = "failed"

            return IngestionResult(
                paper_id=paper_id,
                status=final_status,
                pdf_path=str(pdf_path),
                output_dir=str(output_dir),
                n_claims=result.get("n_claims", 0),
                n_rules=result.get("n_rules", 0),
                pipeline_result=result,
            )

        except Exception as e:
            logger.error(f"Pipeline failed for {paper_id}: {e}")
            return IngestionResult(
                paper_id=paper_id,
                status="failed",
                pdf_path=str(pdf_path),
                output_dir=str(output_dir),
                error=f"Pipeline error: {e}",
            )
        finally:
            # Cleanup temporary bundle if requested
            if self.cleanup_bundles and bundle_dir.exists():
                try:
                    shutil.rmtree(bundle_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup bundle {bundle_dir}: {e}")

    def _create_input_bundle(
        self,
        paper: Dict[str, Any],
        pdf_path: Path,
        paper_id: str,
    ) -> Path:
        """
        Create an input bundle directory for the pipeline.

        Returns:
            Path to the created bundle directory.
        """
        # Create temporary bundle directory
        bundle_dir = Path(tempfile.mkdtemp(prefix="ae_bundle_"))

        # Copy PDF to bundle
        pdf_dest = bundle_dir / "paper.pdf"
        shutil.copy2(pdf_path, pdf_dest)

        # Compute PDF hash
        pdf_bytes = pdf_dest.read_bytes()
        pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()

        # Create paper.json
        # Convert authors list to schema format
        authors = paper.get("authors", [])
        if isinstance(authors, list):
            if authors and isinstance(authors[0], str):
                # Simple string list -> convert to schema format
                authors = [{"name": a} for a in authors]
            # else already in schema format or empty
        else:
            # Single author string
            authors = [{"name": str(authors)}] if authors else [{"name": "Unknown"}]

        paper_json = {
            "schema": "ae.paper.v1",
            "paper_id": paper_id,
            "title": paper.get("title", "Untitled"),
            "authors": authors,
            "year": paper.get("year", datetime.now().year),
            "doi": paper.get("doi"),
            "venue": paper.get("venue") or paper.get("journal"),
            "abstract": paper.get("abstract"),  # BIB-6: This enables abstract fallback
            "publisher": paper.get("publisher"),
            "url": paper.get("url"),
            "source": {
                "finder_run_id": f"bibtex_import_{datetime.now().strftime('%Y%m%d')}",
                "ingest_method": "bibtex_import",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            },
            "files": {
                "pdf_sha256": pdf_sha256,
                "pdf_bytes": len(pdf_bytes),
            },
            "notes": {
                "human_notes": None,
                "tags": paper.get("keywords", []),
            },
        }

        # Add BibTeX source info if available
        if "bibtex_source" in paper:
            paper_json["bibtex_source"] = paper["bibtex_source"]
        elif "cite_key" in paper:
            paper_json["bibtex_source"] = {
                "cite_key": paper["cite_key"],
                "entry_type": paper.get("entry_type", "article"),
            }

        paper_json_path = bundle_dir / "paper.json"
        with open(paper_json_path, 'w', encoding='utf-8') as f:
            json.dump(paper_json, f, indent=2, ensure_ascii=False)

        # If abstract is available, also write abstract.txt as additional fallback
        if paper.get("abstract"):
            abstract_path = bundle_dir / "abstract.txt"
            with open(abstract_path, 'w', encoding='utf-8') as f:
                f.write(paper["abstract"])

        logger.debug(f"Created input bundle at {bundle_dir}")
        return bundle_dir


def ingest_matched_papers(
    papers_json: Path,
    output_base: Optional[Path] = None,
    profile: str = "standard",
) -> BatchIngestionResult:
    """
    Convenience function for ingesting matched papers.

    Args:
        papers_json: Path to matched papers JSON file.
        output_base: Base directory for outputs.
        profile: Extraction profile.

    Returns:
        BatchIngestionResult with all ingestion results.
    """
    service = BibTeXIngestionService(output_base=output_base, profile=profile)
    return service.ingest_from_json(papers_json)


def ingest_single_paper(
    pdf_path: Path,
    title: str,
    authors: List[str],
    year: int,
    abstract: Optional[str] = None,
    doi: Optional[str] = None,
    output_base: Optional[Path] = None,
    profile: str = "standard",
) -> IngestionResult:
    """
    Convenience function for ingesting a single paper with metadata.

    Args:
        pdf_path: Path to PDF file.
        title: Paper title.
        authors: List of author names.
        year: Publication year.
        abstract: Paper abstract (optional but recommended).
        doi: DOI (optional).
        output_base: Base directory for outputs.
        profile: Extraction profile.

    Returns:
        IngestionResult with extraction status.
    """
    paper = {
        "pdf_path": str(pdf_path),
        "title": title,
        "authors": authors,
        "year": year,
        "abstract": abstract,
        "doi": doi,
    }

    service = BibTeXIngestionService(output_base=output_base, profile=profile)
    return service.ingest_paper(paper)
