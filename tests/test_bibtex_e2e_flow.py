from pathlib import Path
from unittest.mock import MagicMock, patch

from src.services.bibtex_ingestion import BibTeXIngestionService
from src.services.bibtex_utils import PDFBibTeXMatcher, parse_bibtex_string


def test_bibtex_to_ingestion_e2e(tmp_path):
    bibtex = """
    @article{smith2024daylight,
      title={Daylight and Sustained Attention in Classrooms},
      author={Smith, John and Doe, Jane},
      year={2024},
      doi={10.1234/daylight.2024.001},
      journal={Journal of Built Environment},
      abstract={Higher daylight exposure improved sustained attention.}
    }
    """
    entries = parse_bibtex_string(bibtex)
    assert len(entries) == 1

    pdf_path = tmp_path / "10.1234_daylight.2024.001.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nDummy PDF for e2e BibTeX ingestion test")

    matcher = PDFBibTeXMatcher(entries)
    matched, unmatched = matcher.match_all(
        [pdf_path],
        get_pdf_text=lambda _p: "doi:10.1234/daylight.2024.001",
    )
    assert len(matched) == 1
    assert len(unmatched) == 0
    assert matched[0].match_type == "doi"

    entry = matched[0].entry
    paper = {
        "title": entry.title,
        "authors": entry.authors,
        "year": entry.year,
        "abstract": entry.abstract,
        "doi": entry.doi,
        "venue": entry.journal,
        "pdf_path": str(pdf_path),
        "paper_id": "bibtex:e2e:test:001",
    }

    service = BibTeXIngestionService(output_base=tmp_path / "outputs")
    with patch.object(service, "_get_pipeline") as mock_get_pipeline:
        mock_pipeline = MagicMock(return_value={"status": "SUCCESS", "n_claims": 2, "n_rules": 1})
        mock_get_pipeline.return_value = mock_pipeline
        result = service.ingest_batch([paper])

    assert result.total == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert result.results[0].status == "success"
    assert result.results[0].n_claims == 2
    assert result.results[0].n_rules == 1
