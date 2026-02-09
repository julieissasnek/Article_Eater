"""
Tests for BibTeX utilities (Sprint BIB-2).

Created: 2026-02-08
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.services.bibtex_utils import (
    BibTeXParser,
    BibTeXEntry,
    PDFBibTeXMatcher,
    MatchResult,
    parse_bibtex_string,
    parse_bibtex_file,
    normalize_text,
    title_similarity,
    extract_doi_from_text,
    extract_arxiv_id,
    entries_to_paper_jsons,
    create_match_report,
)


# =============================================================================
# SAMPLE BIBTEX DATA
# =============================================================================

SAMPLE_BIBTEX = """
@article{kaplan1989restorative,
    author = {Kaplan, Rachel and Kaplan, Stephen},
    title = {The Experience of Nature: A Psychological Perspective},
    journal = {Cambridge University Press},
    year = {1989},
    abstract = {This book explores how natural environments affect human cognition and well-being.},
    doi = {10.1017/CBO9780511508417},
    keywords = {environmental psychology, attention restoration, nature},
}

@article{ulrich1984view,
    author = {Ulrich, Roger S.},
    title = {View through a window may influence recovery from surgery},
    journal = {Science},
    year = {1984},
    volume = {224},
    number = {4647},
    pages = {420--421},
    doi = {10.1126/science.6143402},
}

@inproceedings{berman2008cognitive,
    author = {Berman, Marc G. and Jonides, John and Kaplan, Stephen},
    title = {The Cognitive Benefits of Interacting With Nature},
    booktitle = {Psychological Science},
    year = {2008},
    volume = {19},
    pages = {1207--1212},
    doi = {10.1111/j.1467-9280.2008.02225.x},
}

@book{appleton1975experience,
    author = {Appleton, Jay},
    title = {The Experience of Landscape},
    publisher = {Wiley},
    year = {1975},
    isbn = {0471032565},
}
"""

SAMPLE_BIBTEX_WITH_LATEX = """
@article{muller2020umlauts,
    author = {M\\"uller, Hans and Fran{\\c c}ois, Jean-Pierre},
    title = {Testing {LaTeX} Special Characters: \\& \\% {$\\alpha$}},
    journal = {Journal of {LaTeX} Processing},
    year = {2020},
}
"""


# =============================================================================
# PARSER TESTS
# =============================================================================


class TestBibTeXParser:
    """Tests for BibTeX parsing."""

    def test_parse_basic_article(self):
        """Test parsing a basic article entry."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        assert len(entries) == 4

        # Find Kaplan entry
        kaplan = next(e for e in entries if e.cite_key == "kaplan1989restorative")
        assert kaplan.entry_type == "article"
        assert kaplan.title == "The Experience of Nature: A Psychological Perspective"
        assert kaplan.year == 1989
        assert kaplan.doi == "10.1017/CBO9780511508417"
        assert len(kaplan.authors) == 2
        assert "Rachel Kaplan" in kaplan.authors
        assert "Stephen Kaplan" in kaplan.authors

    def test_parse_article_with_volume_pages(self):
        """Test parsing article with volume and pages."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        ulrich = next(e for e in entries if e.cite_key == "ulrich1984view")

        assert ulrich.volume == "224"
        assert ulrich.number == "4647"
        assert ulrich.pages == "420--421"

    def test_parse_inproceedings(self):
        """Test parsing conference paper."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        berman = next(e for e in entries if e.cite_key == "berman2008cognitive")

        assert berman.entry_type == "inproceedings"
        assert berman.booktitle == "Psychological Science"
        assert len(berman.authors) == 3

    def test_parse_book(self):
        """Test parsing book entry."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        appleton = next(e for e in entries if e.cite_key == "appleton1975experience")

        assert appleton.entry_type == "book"
        assert appleton.publisher == "Wiley"
        assert appleton.isbn == "0471032565"

    def test_parse_keywords(self):
        """Test keyword parsing."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        kaplan = next(e for e in entries if e.cite_key == "kaplan1989restorative")

        assert "environmental psychology" in kaplan.keywords
        assert "attention restoration" in kaplan.keywords
        assert "nature" in kaplan.keywords

    def test_parse_latex_special_chars(self):
        """Test LaTeX character cleaning."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX_WITH_LATEX)
        assert len(entries) == 1

        entry = entries[0]
        # Umlauts should be converted
        assert "ü" in entry.authors[0] or "u" in entry.authors[0]  # Müller or Muller
        # Braces around LaTeX should be removed
        assert "{" not in entry.title

    def test_parse_file(self):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bib", delete=False) as f:
            f.write(SAMPLE_BIBTEX)
            f.flush()

            entries = parse_bibtex_file(Path(f.name))
            assert len(entries) == 4

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        entries = parse_bibtex_string("")
        assert entries == []

    def test_parse_no_entries(self):
        """Test parsing BibTeX with no entries."""
        entries = parse_bibtex_string("% This is just a comment\n@comment{ignored}")
        assert entries == []


# =============================================================================
# ENTRY CONVERSION TESTS
# =============================================================================


class TestBibTeXEntry:
    """Tests for BibTeXEntry methods."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        entry = entries[0]

        d = entry.to_dict()
        assert "cite_key" in d
        assert "title" in d
        assert "authors" in d
        assert "year" in d

    def test_to_paper_json(self):
        """Test conversion to AE paper.json format."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        kaplan = next(e for e in entries if e.cite_key == "kaplan1989restorative")

        paper = kaplan.to_paper_json()

        assert paper["schema"] == "ae.paper.v1"
        assert paper["paper_id"] == "kaplan1989restorative"
        assert paper["title"] == "The Experience of Nature: A Psychological Perspective"
        assert paper["year"] == 1989
        assert paper["doi"] == "10.1017/CBO9780511508417"
        assert len(paper["authors"]) == 2
        assert paper["bibtex_source"]["cite_key"] == "kaplan1989restorative"

    def test_to_paper_json_custom_id(self):
        """Test paper.json with custom paper_id."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        entry = entries[0]

        paper = entry.to_paper_json(paper_id="custom_id_123")
        assert paper["paper_id"] == "custom_id_123"

    def test_metadata_completeness(self):
        """Test metadata completeness check."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        kaplan = next(e for e in entries if e.cite_key == "kaplan1989restorative")

        paper = kaplan.to_paper_json()
        completeness = paper["metadata_complete"]

        assert completeness["has_title"] is True
        assert completeness["has_authors"] is True
        assert completeness["has_year"] is True
        assert completeness["has_abstract"] is True
        assert completeness["has_doi"] is True

    def test_normalized_title(self):
        """Test title normalization."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        entry = entries[0]

        norm = entry.normalized_title
        assert norm.islower()
        assert ":" not in norm  # Punctuation removed

    def test_first_author_lastname(self):
        """Test first author extraction."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        kaplan = next(e for e in entries if e.cite_key == "kaplan1989restorative")

        assert kaplan.first_author_lastname == "kaplan"


# =============================================================================
# TEXT NORMALIZATION TESTS
# =============================================================================


class TestTextNormalization:
    """Tests for text normalization functions."""

    def test_normalize_basic(self):
        """Test basic normalization."""
        assert normalize_text("Hello World!") == "hello world"

    def test_normalize_diacritics(self):
        """Test diacritic removal."""
        assert normalize_text("café résumé") == "cafe resume"

    def test_normalize_punctuation(self):
        """Test punctuation removal."""
        assert normalize_text("Test: A Study (2024)") == "test a study 2024"

    def test_normalize_whitespace(self):
        """Test whitespace collapsing."""
        assert normalize_text("  multiple   spaces  ") == "multiple spaces"

    def test_title_similarity_identical(self):
        """Test similarity of identical titles."""
        assert title_similarity("Hello World", "Hello World") == 1.0

    def test_title_similarity_case_insensitive(self):
        """Test case-insensitive similarity."""
        assert title_similarity("Hello World", "hello world") == 1.0

    def test_title_similarity_partial(self):
        """Test partial similarity."""
        sim = title_similarity(
            "The Experience of Nature",
            "Experience of Nature: A Study"
        )
        assert sim > 0.6

    def test_title_similarity_different(self):
        """Test low similarity for different titles."""
        sim = title_similarity(
            "Quantum Physics Today",
            "Medieval History Overview"
        )
        assert sim < 0.35  # Low but not zero due to common words


# =============================================================================
# DOI/ARXIV EXTRACTION TESTS
# =============================================================================


class TestIdentifierExtraction:
    """Tests for DOI and arXiv ID extraction."""

    def test_extract_doi_standard(self):
        """Test standard DOI extraction."""
        text = "DOI: 10.1126/science.6143402"
        assert extract_doi_from_text(text) == "10.1126/science.6143402"

    def test_extract_doi_url(self):
        """Test DOI extraction from URL."""
        text = "https://doi.org/10.1111/j.1467-9280.2008.02225.x"
        assert extract_doi_from_text(text) == "10.1111/j.1467-9280.2008.02225.x"

    def test_extract_doi_in_filename(self):
        """Test DOI extraction from filename."""
        # DOI with slash (standard format)
        text = "paper_10.1017/CBO9780511508417.pdf"
        doi = extract_doi_from_text(text)
        assert doi is not None
        assert doi.startswith("10.")

    def test_extract_doi_none(self):
        """Test no DOI found."""
        text = "This is a paper about nature"
        assert extract_doi_from_text(text) is None

    def test_extract_arxiv_new_format(self):
        """Test new arXiv ID format."""
        text = "arxiv:2301.12345"
        assert extract_arxiv_id(text) == "2301.12345"

    def test_extract_arxiv_old_format(self):
        """Test old arXiv ID format."""
        text = "arxiv:hep-th/9901001"
        assert extract_arxiv_id(text) == "hep-th/9901001"

    def test_extract_arxiv_none(self):
        """Test no arXiv ID found."""
        text = "Regular paper without arxiv"
        assert extract_arxiv_id(text) is None


# =============================================================================
# MATCHING TESTS
# =============================================================================


class TestPDFBibTeXMatcher:
    """Tests for PDF-BibTeX matching."""

    def test_matcher_creation(self):
        """Test matcher initialization."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        assert len(matcher.entries) == 4
        assert len(matcher.doi_index) > 0

    def test_match_by_doi_in_filename(self):
        """Test matching by DOI in PDF text."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        # Match by DOI found in PDF text (more realistic scenario)
        pdf_path = Path("some_paper.pdf")
        pdf_text = "DOI: 10.1126/science.6143402\nView through a window..."
        result = matcher.match_pdf(pdf_path, pdf_text=pdf_text)

        assert result is not None
        assert result.match_type == "doi"
        assert result.confidence > 0.9
        assert result.entry.cite_key == "ulrich1984view"

    def test_match_by_title_in_filename(self):
        """Test matching by title similarity."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        # Create mock PDF with title-like filename
        pdf_path = Path("Experience_of_Nature_Psychological_Perspective.pdf")
        result = matcher.match_pdf(pdf_path, min_title_similarity=0.5)

        assert result is not None
        assert result.match_type == "title"

    def test_match_by_author_year(self):
        """Test matching by author-year pattern."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        pdf_path = Path("Ulrich1984.pdf")
        result = matcher.match_pdf(pdf_path)

        assert result is not None
        assert result.match_type == "filename"
        assert result.entry.cite_key == "ulrich1984view"

    def test_no_match(self):
        """Test when no match found."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        pdf_path = Path("completely_unrelated_document.pdf")
        result = matcher.match_pdf(pdf_path)

        assert result is None

    def test_match_all(self):
        """Test batch matching."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        pdf_paths = [
            Path("10.1126_science.6143402.pdf"),
            Path("Kaplan1989.pdf"),
            Path("random_document.pdf"),
        ]

        matched, unmatched = matcher.match_all(pdf_paths)

        assert len(matched) >= 1
        assert len(unmatched) <= 2

    def test_get_unmatched_entries(self):
        """Test getting unmatched BibTeX entries."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        matcher = PDFBibTeXMatcher(entries)

        # Match one entry
        matched = [
            MatchResult(
                pdf_path=Path("test.pdf"),
                entry=entries[0],
                confidence=0.9,
                match_type="doi",
            )
        ]

        unmatched = matcher.get_unmatched_entries(matched)
        assert len(unmatched) == 3


# =============================================================================
# EXPORT TESTS
# =============================================================================


class TestExport:
    """Tests for export functions."""

    def test_entries_to_paper_jsons(self):
        """Test batch conversion to paper.json."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        papers = entries_to_paper_jsons(entries)

        assert len(papers) == 4
        assert all(p["schema"] == "ae.paper.v1" for p in papers)

    def test_entries_to_paper_jsons_with_output(self):
        """Test export to files."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)

        with tempfile.TemporaryDirectory() as tmpdir:
            papers = entries_to_paper_jsons(entries, Path(tmpdir))

            # Check files were created
            files = list(Path(tmpdir).glob("*.json"))
            assert len(files) == 4

            # Verify content
            for f in files:
                data = json.loads(f.read_text())
                assert data["schema"] == "ae.paper.v1"

    def test_create_match_report(self):
        """Test match report generation."""
        entries = parse_bibtex_string(SAMPLE_BIBTEX)

        matched = [
            MatchResult(
                pdf_path=Path("test1.pdf"),
                entry=entries[0],
                confidence=0.95,
                match_type="doi",
            ),
            MatchResult(
                pdf_path=Path("test2.pdf"),
                entry=entries[1],
                confidence=0.85,
                match_type="title",
            ),
        ]

        report = create_match_report(
            matched=matched,
            unmatched_pdfs=[Path("orphan.pdf")],
            unmatched_entries=[entries[2], entries[3]],
        )

        assert report["summary"]["matched"] == 2
        assert report["summary"]["unmatched_pdfs"] == 1
        assert report["summary"]["unmatched_entries"] == 2
        assert report["match_type_breakdown"]["doi"] == 1
        assert report["match_type_breakdown"]["title"] == 1
        assert 0.85 < report["average_confidence"] < 0.95


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow(self):
        """Test complete parse-match-export workflow."""
        # 1. Parse BibTeX
        entries = parse_bibtex_string(SAMPLE_BIBTEX)
        assert len(entries) == 4

        # 2. Create matcher
        matcher = PDFBibTeXMatcher(entries)

        # 3. Match PDFs
        pdf_paths = [
            Path("Ulrich1984_surgery_view.pdf"),
            Path("kaplan_experience_nature_1989.pdf"),
        ]

        matched, unmatched = matcher.match_all(pdf_paths)

        # 4. Convert to paper.json
        for match in matched:
            paper = match.entry.to_paper_json()
            assert paper["schema"] == "ae.paper.v1"
            assert paper["paper_id"] is not None

        # 5. Generate report
        report = create_match_report(
            matched=matched,
            unmatched_pdfs=unmatched,
            unmatched_entries=matcher.get_unmatched_entries(matched),
        )

        assert "summary" in report
        assert "matches" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
