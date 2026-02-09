"""
Tests for BIB-7: BibTeX Ingestion Service.

Created: 2026-02-09
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.bibtex_ingestion import (
    BibTeXIngestionService,
    IngestionResult,
    BatchIngestionResult,
    ingest_single_paper,
)


class TestIngestionResult:
    """Tests for IngestionResult dataclass."""

    def test_create_success_result(self):
        result = IngestionResult(
            paper_id="test:001",
            status="success",
            pdf_path="/path/to/paper.pdf",
            output_dir="/path/to/output",
            n_claims=5,
            n_rules=3,
        )
        assert result.paper_id == "test:001"
        assert result.status == "success"
        assert result.n_claims == 5
        assert result.n_rules == 3
        assert result.error is None

    def test_create_failed_result(self):
        result = IngestionResult(
            paper_id="test:002",
            status="failed",
            pdf_path="/path/to/paper.pdf",
            error="PDF not found",
        )
        assert result.status == "failed"
        assert result.error == "PDF not found"
        assert result.n_claims == 0

    def test_to_dict(self):
        result = IngestionResult(
            paper_id="test:003",
            status="success",
            pdf_path="/path/to/paper.pdf",
            n_claims=10,
        )
        d = result.to_dict()
        assert d["paper_id"] == "test:003"
        assert d["status"] == "success"
        assert d["n_claims"] == 10


class TestBatchIngestionResult:
    """Tests for BatchIngestionResult dataclass."""

    def test_create_batch_result(self):
        results = [
            IngestionResult("p1", "success", "/p1.pdf", n_claims=5),
            IngestionResult("p2", "failed", "/p2.pdf", error="Not found"),
            IngestionResult("p3", "skipped", "/p3.pdf"),
        ]
        batch = BatchIngestionResult(
            total=3,
            succeeded=1,
            failed=1,
            skipped=1,
            results=results,
        )
        assert batch.total == 3
        assert batch.succeeded == 1
        assert batch.failed == 1
        assert batch.skipped == 1
        assert len(batch.results) == 3

    def test_to_dict(self):
        batch = BatchIngestionResult(total=2, succeeded=2, failed=0, skipped=0)
        d = batch.to_dict()
        assert d["total"] == 2
        assert d["succeeded"] == 2
        assert "results" in d


class TestBibTeXIngestionService:
    """Tests for BibTeXIngestionService."""

    def test_init_default(self):
        service = BibTeXIngestionService()
        assert service.output_base.exists() or service.output_base.parent.exists()
        assert service.profile == "standard"
        assert service.hitl == "auto"
        assert service.cleanup_bundles is True

    def test_init_custom(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = BibTeXIngestionService(
                output_base=Path(tmpdir) / "outputs",
                profile="thorough",
                hitl="confirm",
                cleanup_bundles=False,
            )
            assert service.profile == "thorough"
            assert service.hitl == "confirm"
            assert service.cleanup_bundles is False

    def test_ingest_paper_no_pdf_path(self):
        service = BibTeXIngestionService()
        result = service.ingest_paper({"title": "Test", "authors": ["Smith"]})
        assert result.status == "skipped"
        assert "No pdf_path" in result.error

    def test_ingest_paper_pdf_not_found(self):
        service = BibTeXIngestionService()
        result = service.ingest_paper({
            "title": "Test",
            "authors": ["Smith"],
            "pdf_path": "/nonexistent/paper.pdf",
        })
        assert result.status == "skipped"
        assert "PDF not found" in result.error

    def test_create_input_bundle(self):
        """Test that input bundle is created correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy PDF
            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nDummy PDF content for testing")

            service = BibTeXIngestionService(output_base=Path(tmpdir) / "outputs")

            paper = {
                "title": "Test Paper",
                "authors": ["John Smith", "Jane Doe"],
                "year": 2024,
                "abstract": "This is a test abstract.",
                "doi": "10.1234/test.2024",
            }

            bundle_dir = service._create_input_bundle(paper, pdf_path, "test:001")

            # Check bundle contents
            assert bundle_dir.exists()
            assert (bundle_dir / "paper.pdf").exists()
            assert (bundle_dir / "paper.json").exists()
            assert (bundle_dir / "abstract.txt").exists()

            # Check paper.json content
            with open(bundle_dir / "paper.json") as f:
                paper_json = json.load(f)

            assert paper_json["schema"] == "ae.paper.v1"
            assert paper_json["paper_id"] == "test:001"
            assert paper_json["title"] == "Test Paper"
            assert paper_json["abstract"] == "This is a test abstract."
            assert paper_json["doi"] == "10.1234/test.2024"
            assert len(paper_json["authors"]) == 2

            # Check abstract.txt content
            assert (bundle_dir / "abstract.txt").read_text() == "This is a test abstract."

            # Cleanup
            import shutil
            shutil.rmtree(bundle_dir)

    @patch("src.services.bibtex_ingestion.BibTeXIngestionService._get_pipeline")
    def test_ingest_paper_success(self, mock_get_pipeline):
        """Test successful paper ingestion."""
        # Mock pipeline
        mock_pipeline = MagicMock(return_value={
            "status": "SUCCESS",
            "n_claims": 5,
            "n_rules": 3,
        })
        mock_get_pipeline.return_value = mock_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy PDF
            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nDummy PDF")

            service = BibTeXIngestionService(
                output_base=Path(tmpdir) / "outputs",
                cleanup_bundles=True,
            )

            result = service.ingest_paper({
                "title": "Test Paper",
                "authors": ["Smith"],
                "year": 2024,
                "abstract": "Test abstract",
                "pdf_path": str(pdf_path),
            })

            assert result.status == "success"
            assert result.n_claims == 5
            assert result.n_rules == 3
            assert mock_pipeline.called

    @patch("src.services.bibtex_ingestion.BibTeXIngestionService._get_pipeline")
    def test_ingest_batch(self, mock_get_pipeline):
        """Test batch ingestion."""
        mock_pipeline = MagicMock(return_value={
            "status": "SUCCESS",
            "n_claims": 3,
            "n_rules": 1,
        })
        mock_get_pipeline.return_value = mock_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy PDFs
            pdf1 = Path(tmpdir) / "paper1.pdf"
            pdf2 = Path(tmpdir) / "paper2.pdf"
            pdf1.write_bytes(b"%PDF-1.4\nPDF 1")
            pdf2.write_bytes(b"%PDF-1.4\nPDF 2")

            service = BibTeXIngestionService(output_base=Path(tmpdir) / "outputs")

            papers = [
                {"title": "Paper 1", "authors": ["A"], "year": 2024, "pdf_path": str(pdf1)},
                {"title": "Paper 2", "authors": ["B"], "year": 2024, "pdf_path": str(pdf2)},
            ]

            result = service.ingest_batch(papers)

            assert result.total == 2
            assert result.succeeded == 2
            assert result.failed == 0
            assert len(result.results) == 2

    def test_ingest_from_json(self):
        """Test ingestion from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy PDF
            pdf_path = Path(tmpdir) / "paper.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nDummy")

            # Create papers JSON
            papers = [{
                "title": "Test",
                "authors": ["Author"],
                "year": 2024,
                "pdf_path": str(pdf_path),
            }]
            json_path = Path(tmpdir) / "papers.json"
            with open(json_path, 'w') as f:
                json.dump(papers, f)

            service = BibTeXIngestionService(output_base=Path(tmpdir) / "outputs")

            # Mock pipeline to avoid actual execution
            with patch.object(service, "_get_pipeline") as mock:
                mock.return_value = MagicMock(return_value={"status": "SUCCESS", "n_claims": 1, "n_rules": 0})
                result = service.ingest_from_json(json_path)

            assert result.total == 1


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch("src.services.bibtex_ingestion.BibTeXIngestionService.ingest_paper")
    def test_ingest_single_paper(self, mock_ingest):
        mock_ingest.return_value = IngestionResult(
            paper_id="test:001",
            status="success",
            pdf_path="/test.pdf",
            n_claims=5,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF")

            result = ingest_single_paper(
                pdf_path=pdf_path,
                title="Test Paper",
                authors=["Smith"],
                year=2024,
                abstract="Abstract text",
            )

            assert result.status == "success"
            mock_ingest.assert_called_once()
