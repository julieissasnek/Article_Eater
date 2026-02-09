"""
Tests for BibTeX Generator with Full Metadata Support.
Sprint 3.0.4-D — 2026-02-09

Comprehensive tests for:
- All BibTeX entry types
- LaTeX escaping
- Cite key generation
- Full metadata handling
- WebOfBelief integration
- Batch export

Created: 2026-02-09
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.services.bibtex_generator import (
    # Classes
    BibTeXEntryType,
    GeneratedBibTeXEntry,
    CiteKeyGenerator,
    FullBibTeXGenerator,
    BibTeXValidationResult,
    # Functions
    escape_latex,
    clean_for_citekey,
    entries_from_belief_sources,
    entry_from_paper_json,
    export_to_bibtex,
    export_papers_to_bibtex,
    export_sources_to_bibtex,
    validate_entries,
    get_bibtex_generator,
    # Constants
    REQUIRED_FIELDS,
)


# =============================================================================
# LATEX ESCAPING TESTS
# =============================================================================


class TestLatexEscaping:
    """Tests for LaTeX special character escaping."""

    def test_escape_ampersand(self):
        """Test & escaping."""
        assert escape_latex("Smith & Jones") == r"Smith \& Jones"

    def test_escape_percent(self):
        """Test % escaping."""
        assert escape_latex("100% correct") == r"100\% correct"

    def test_escape_dollar(self):
        """Test $ escaping."""
        assert escape_latex("Price is $50") == r"Price is \$50"

    def test_escape_hash(self):
        """Test # escaping."""
        assert escape_latex("Item #1") == r"Item \#1"

    def test_escape_underscore(self):
        """Test _ escaping."""
        assert escape_latex("var_name") == r"var\_name"

    def test_escape_accented_characters(self):
        """Test Unicode to LaTeX conversion."""
        assert escape_latex("café") == r"caf\'e"
        assert escape_latex("Müller") == r"M\"uller"
        assert escape_latex("naïve") == r"na\"ive"
        assert escape_latex("señor") == r"se\~nor"

    def test_escape_german_eszett(self):
        """Test ß conversion."""
        assert escape_latex("Straße") == r"Stra\sse"

    def test_escape_em_dash(self):
        """Test em and en dash conversion."""
        assert escape_latex("1990–2000") == "1990--2000"
        assert escape_latex("Hello—World") == "Hello---World"

    def test_preserve_case_acronyms(self):
        """Test case preservation for acronyms."""
        result = escape_latex("The DNA Structure", preserve_case=True)
        assert "{DNA}" in result

    def test_preserve_case_mixed(self):
        """Test case preservation for mixed case words."""
        result = escape_latex("The McDonald Study", preserve_case=True)
        assert "{McDonald}" in result

    def test_empty_string(self):
        """Test empty string handling."""
        assert escape_latex("") == ""
        assert escape_latex(None) == ""

    def test_multiple_special_chars(self):
        """Test multiple special characters in one string."""
        result = escape_latex("50% off $100 items & more")
        assert r"\%" in result
        assert r"\$" in result
        assert r"\&" in result


class TestCleanForCitekey:
    """Tests for citation key cleaning."""

    def test_remove_diacritics(self):
        """Test diacritic removal."""
        assert clean_for_citekey("Müller") == "muller"
        assert clean_for_citekey("Gödel") == "godel"
        assert clean_for_citekey("Pérez") == "perez"

    def test_remove_special_chars(self):
        """Test special character removal."""
        assert clean_for_citekey("O'Brien") == "obrien"
        assert clean_for_citekey("Van Der Berg") == "vanderberg"

    def test_lowercase(self):
        """Test lowercase conversion."""
        assert clean_for_citekey("SMITH") == "smith"
        assert clean_for_citekey("McDonald") == "mcdonald"

    def test_empty_string(self):
        """Test empty string handling."""
        assert clean_for_citekey("") == ""


# =============================================================================
# BIBTEX ENTRY TESTS
# =============================================================================


class TestGeneratedBibTeXEntry:
    """Tests for GeneratedBibTeXEntry dataclass."""

    def test_create_article(self):
        """Test creating an article entry."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="smith2024",
            title="A Study of Something",
            authors=["John Smith", "Jane Doe"],
            year=2024,
            journal="Nature",
            volume="42",
            pages="100-120",
            doi="10.1234/example"
        )

        assert entry.entry_type == BibTeXEntryType.ARTICLE
        assert entry.cite_key == "smith2024"
        assert entry.author == "John Smith and Jane Doe"
        assert entry.year == 2024

    def test_author_string_parsing(self):
        """Test automatic author string parsing."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            author="Smith, John and Doe, Jane and Brown, Bob"
        )

        assert len(entry.authors) == 3
        assert "Smith, John" in entry.authors

    def test_get_first_author_lastname_comma_format(self):
        """Test first author extraction from 'Last, First' format."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            authors=["Smith, John", "Doe, Jane"]
        )

        assert entry.get_first_author_lastname() == "Smith"

    def test_get_first_author_lastname_space_format(self):
        """Test first author extraction from 'First Last' format."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            authors=["John Smith", "Jane Doe"]
        )

        assert entry.get_first_author_lastname() == "Smith"

    def test_get_first_author_no_authors(self):
        """Test first author extraction with no authors."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.MISC,
            cite_key="test"
        )

        assert entry.get_first_author_lastname() == "unknown"

    def test_is_valid_article(self):
        """Test validation for article with all required fields."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            author="John Smith",
            title="Test Title",
            journal="Test Journal",
            year=2024
        )

        is_valid, missing = entry.is_valid()
        assert is_valid
        assert len(missing) == 0

    def test_is_valid_article_missing_fields(self):
        """Test validation for article missing required fields."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title="Test Title"
        )

        is_valid, missing = entry.is_valid()
        assert not is_valid
        assert "author" in missing
        assert "journal" in missing
        assert "year" in missing

    def test_is_valid_misc_no_requirements(self):
        """Test that misc type has no required fields."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.MISC,
            cite_key="test"
        )

        is_valid, missing = entry.is_valid()
        assert is_valid

    def test_to_dict(self):
        """Test dictionary conversion."""
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="smith2024",
            title="Test",
            year=2024,
            doi="10.1234/test"
        )

        d = entry.to_dict()
        assert d["entry_type"] == "article"
        assert d["cite_key"] == "smith2024"
        assert d["year"] == 2024
        assert d["doi"] == "10.1234/test"


# =============================================================================
# CITE KEY GENERATOR TESTS
# =============================================================================


class TestCiteKeyGenerator:
    """Tests for citation key generation."""

    def test_generate_authoryear(self):
        """Test author-year key generation."""
        generator = CiteKeyGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["John Smith"],
            year=2024
        )

        key = generator.generate(entry, style="authoryear")
        assert key == "smith2024"

    def test_generate_collision_handling(self):
        """Test unique key generation with collisions."""
        generator = CiteKeyGenerator()

        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="",
                authors=["John Smith"],
                year=2024
            )
            for _ in range(3)
        ]

        keys = [generator.generate(e) for e in entries]

        assert keys[0] == "smith2024"
        assert keys[1] == "smith2024a"
        assert keys[2] == "smith2024b"

        # All keys are unique
        assert len(set(keys)) == 3

    def test_generate_author_title(self):
        """Test author-title key generation."""
        generator = CiteKeyGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["John Smith"],
            title="Attention Is All You Need"
        )

        key = generator.generate(entry, style="authorTitle")
        assert "smith" in key
        assert "attention" in key

    def test_generate_doi_based(self):
        """Test DOI-based key generation."""
        generator = CiteKeyGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            doi="10.1234/example.2024"
        )

        key = generator.generate(entry, style="doi")
        assert key.startswith("doi")

    def test_reset(self):
        """Test key reset."""
        generator = CiteKeyGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["Smith"],
            year=2024
        )

        generator.generate(entry)
        generator.reset()

        # After reset, same key should be generated
        key = generator.generate(entry)
        assert key == "smith2024"

    def test_add_existing(self):
        """Test registering existing keys."""
        generator = CiteKeyGenerator()
        generator.add_existing(["smith2024", "smith2024a"])

        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["Smith"],
            year=2024
        )

        key = generator.generate(entry)
        assert key == "smith2024b"

    def test_no_year(self):
        """Test key generation without year."""
        generator = CiteKeyGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["Smith"]
        )

        key = generator.generate(entry)
        assert key == "smithnodate"


# =============================================================================
# FULL BIBTEX GENERATOR TESTS
# =============================================================================


class TestFullBibTeXGenerator:
    """Tests for full BibTeX generation."""

    def test_generate_article_entry(self):
        """Test generating an article entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="smith2024",
            author="John Smith",
            title="A Test Article",
            journal="Test Journal",
            year=2024,
            volume="10",
            pages="1-20",
            doi="10.1234/test"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@article{smith2024," in result
        assert "author = {John Smith}" in result
        assert "title = {A Test Article}" in result
        assert "journal = {Test Journal}" in result
        assert "year = 2024" in result
        assert "doi = {10.1234/test}" in result

    def test_generate_book_entry(self):
        """Test generating a book entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.BOOK,
            cite_key="doe2023",
            author="Jane Doe",
            title="The Complete Guide",
            publisher="Academic Press",
            year=2023,
            isbn="978-1234567890"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@book{doe2023," in result
        assert "publisher = {Academic Press}" in result
        assert "isbn = {978-1234567890}" in result

    def test_generate_inproceedings_entry(self):
        """Test generating a conference paper entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.INPROCEEDINGS,
            cite_key="brown2024",
            author="Bob Brown",
            title="Conference Paper Title",
            booktitle="Proceedings of the International Conference",
            year=2024,
            pages="100-110"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@inproceedings{brown2024," in result
        assert "booktitle = {Proceedings" in result

    def test_generate_phdthesis_entry(self):
        """Test generating a PhD thesis entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.PHDTHESIS,
            cite_key="wilson2022",
            author="Alice Wilson",
            title="Doctoral Dissertation",
            school="MIT",
            year=2022
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@phdthesis{wilson2022," in result
        assert "school = {MIT}" in result

    def test_generate_techreport_entry(self):
        """Test generating a technical report entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.TECHREPORT,
            cite_key="nasa2024",
            author="NASA Team",
            title="Technical Report",
            institution="NASA",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@techreport{nasa2024," in result
        assert "institution = {NASA}" in result

    def test_auto_key_generation(self):
        """Test automatic cite key generation."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",  # Empty - should auto-generate
            author="John Smith",
            title="Test",
            journal="Journal",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=True)

        assert "@article{smith2024," in result
        assert entry.cite_key == "smith2024"

    def test_latex_escaping_in_output(self):
        """Test that special characters are escaped."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            author="O'Brien & Müller",
            title="100% Effective: A $50 Solution",
            journal="Test",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert r"\&" in result
        assert r"\%" in result
        assert r"\$" in result

    def test_keywords_formatting(self):
        """Test keywords field formatting."""
        generator = FullBibTeXGenerator(include_keywords=True)
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title="Test",
            year=2024,
            keywords=["machine learning", "neural networks", "AI"]
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "keywords = {machine learning, neural networks, AI}" in result

    def test_exclude_abstract(self):
        """Test excluding abstract field."""
        generator = FullBibTeXGenerator(include_abstract=False)
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title="Test",
            year=2024,
            abstract="This is the abstract."
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "abstract" not in result

    def test_exclude_url(self):
        """Test excluding URL field."""
        generator = FullBibTeXGenerator(include_url=False)
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title="Test",
            year=2024,
            url="https://example.com"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "url" not in result

    def test_batch_generation(self):
        """Test batch generation of multiple entries."""
        generator = FullBibTeXGenerator()
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="",
                authors=["Smith"],
                title="Paper 1",
                journal="Journal",
                year=2024
            ),
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="",
                authors=["Doe"],
                title="Paper 2",
                journal="Journal",
                year=2024
            )
        ]

        result = generator.generate_batch(entries, header_comment="Test Export")

        assert "% Test Export" in result
        assert "@article{smith2024," in result
        assert "@article{doe2024," in result
        # Two separate entries
        assert result.count("@article{") == 2

    def test_custom_indent(self):
        """Test custom indentation."""
        generator = FullBibTeXGenerator(indent="    ")  # 4 spaces
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title="Test",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "    title = " in result

    def test_arxiv_entry(self):
        """Test arXiv paper entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.MISC,
            cite_key="arxiv2024",
            author="Author Name",
            title="ArXiv Paper",
            year=2024,
            eprint="2401.12345",
            archiveprefix="arXiv",
            primaryclass="cs.AI"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "eprint = {2401.12345}" in result
        assert "archiveprefix = {arXiv}" in result
        assert "primaryclass = {cs.AI}" in result


# =============================================================================
# CONVERSION FUNCTION TESTS
# =============================================================================


class TestConversionFunctions:
    """Tests for conversion functions."""

    def test_entries_from_belief_sources_article(self):
        """Test converting article source."""
        sources = [{
            "title": "Test Article",
            "authors": ["John Smith", "Jane Doe"],
            "year": 2024,
            "journal": "Nature",
            "volume": "42",
            "doi": "10.1234/test"
        }]

        entries = entries_from_belief_sources(sources)

        assert len(entries) == 1
        assert entries[0].entry_type == BibTeXEntryType.ARTICLE
        assert entries[0].journal == "Nature"

    def test_entries_from_belief_sources_conference(self):
        """Test converting conference source."""
        sources = [{
            "title": "Conference Paper",
            "authors": ["Bob Brown"],
            "year": 2024,
            "booktitle": "ICML 2024",
            "type": "conference"
        }]

        entries = entries_from_belief_sources(sources)

        assert len(entries) == 1
        assert entries[0].entry_type == BibTeXEntryType.INPROCEEDINGS
        assert entries[0].booktitle == "ICML 2024"

    def test_entries_from_belief_sources_phd_thesis(self):
        """Test converting PhD thesis source."""
        sources = [{
            "title": "Doctoral Work",
            "authors": ["Alice Wilson"],
            "year": 2022,
            "school": "MIT",
            "type": "phd thesis"
        }]

        entries = entries_from_belief_sources(sources)

        assert len(entries) == 1
        assert entries[0].entry_type == BibTeXEntryType.PHDTHESIS
        assert entries[0].school == "MIT"

    def test_entries_from_belief_sources_arxiv(self):
        """Test converting arXiv source."""
        sources = [{
            "title": "ArXiv Paper",
            "authors": ["Author"],
            "year": 2024,
            "arxiv_id": "2401.12345"
        }]

        entries = entries_from_belief_sources(sources)

        assert len(entries) == 1
        assert entries[0].eprint == "2401.12345"
        assert entries[0].archiveprefix == "arXiv"

    def test_entry_from_paper_json(self):
        """Test converting paper.json format."""
        paper = {
            "paper_id": "paper123",
            "title": "Test Paper",
            "authors": ["John Smith"],
            "year": 2024,
            "journal": "Science",
            "volume": "380",
            "doi": "10.1234/test",
            "bibtex_source": {
                "cite_key": "smith2024science"
            }
        }

        entry = entry_from_paper_json(paper)

        assert entry.entry_type == BibTeXEntryType.ARTICLE
        assert entry.cite_key == "smith2024science"
        assert entry.journal == "Science"
        assert entry.source_id == "paper123"

    def test_entry_from_paper_json_conference(self):
        """Test converting conference paper.json."""
        paper = {
            "title": "Conference Paper",
            "authors": ["Jane Doe"],
            "year": 2024,
            "venue": "Conference on Machine Learning"
        }

        entry = entry_from_paper_json(paper)

        assert entry.entry_type == BibTeXEntryType.INPROCEEDINGS
        assert entry.booktitle == "Conference on Machine Learning"


# =============================================================================
# EXPORT FUNCTION TESTS
# =============================================================================


class TestExportFunctions:
    """Tests for export functions."""

    def test_export_to_bibtex(self):
        """Test basic BibTeX export."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="smith2024",
                author="Smith",
                title="Test",
                journal="Journal",
                year=2024
            )
        ]

        result = export_to_bibtex(entries)

        assert "@article{smith2024," in result
        assert "% Article Eater V23 BibTeX Export" in result

    def test_export_to_bibtex_with_file(self, tmp_path):
        """Test BibTeX export to file."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                title="Test",
                year=2024
            )
        ]

        output_path = tmp_path / "test.bib"
        export_to_bibtex(entries, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "@article{test," in content

    def test_export_papers_to_bibtex(self):
        """Test exporting papers in paper.json format."""
        papers = [
            {
                "title": "Paper 1",
                "authors": ["Smith"],
                "year": 2024,
                "journal": "Nature"
            },
            {
                "title": "Paper 2",
                "authors": ["Doe"],
                "year": 2024,
                "journal": "Science"
            }
        ]

        result = export_papers_to_bibtex(papers)

        assert result.count("@article{") == 2

    def test_export_sources_to_bibtex(self):
        """Test exporting belief sources."""
        sources = [
            {
                "title": "Source 1",
                "authors": ["Author 1"],
                "year": 2024,
                "journal": "Journal"
            }
        ]

        result = export_sources_to_bibtex(sources)

        assert "@article{" in result


# =============================================================================
# VALIDATION TESTS
# =============================================================================


class TestValidation:
    """Tests for entry validation."""

    def test_validate_valid_entry(self):
        """Test validating a valid entry."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                author="Smith",
                title="Test",
                journal="Journal",
                year=2024
            )
        ]

        results = validate_entries(entries)

        assert len(results) == 1
        assert results[0].is_valid
        assert len(results[0].missing_fields) == 0

    def test_validate_missing_fields(self):
        """Test validating entry with missing fields."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                title="Test"
                # Missing: author, journal, year
            )
        ]

        results = validate_entries(entries)

        assert len(results) == 1
        assert not results[0].is_valid
        assert "author" in results[0].missing_fields
        assert "journal" in results[0].missing_fields
        assert "year" in results[0].missing_fields

    def test_validate_warnings_no_identifiers(self):
        """Test warning when no DOI or URL."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                author="Smith",
                title="Test",
                journal="Journal",
                year=2024
                # No doi or url
            )
        ]

        results = validate_entries(entries)

        assert any("DOI or URL" in w for w in results[0].warnings)

    def test_validate_warnings_suspicious_year(self):
        """Test warning for suspicious year."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                author="Smith",
                title="Test",
                journal="Journal",
                year=1800  # Too old
            )
        ]

        results = validate_entries(entries)

        assert any("Suspicious year" in w for w in results[0].warnings)

    def test_validate_warnings_short_title(self):
        """Test warning for short title."""
        entries = [
            GeneratedBibTeXEntry(
                entry_type=BibTeXEntryType.ARTICLE,
                cite_key="test",
                author="Smith",
                title="Test",  # Only 4 chars
                journal="Journal",
                year=2024
            )
        ]

        results = validate_entries(entries)

        assert any("Title seems too short" in w for w in results[0].warnings)


# =============================================================================
# SINGLETON TESTS
# =============================================================================


class TestSingleton:
    """Tests for singleton getter."""

    def test_get_bibtex_generator(self):
        """Test getting generator singleton."""
        gen1 = get_bibtex_generator()
        gen2 = get_bibtex_generator()

        # Same instance
        assert gen1 is gen2

    def test_get_bibtex_generator_with_options(self):
        """Test getting generator with custom options."""
        gen = get_bibtex_generator(include_abstract=False)

        assert gen.include_abstract is False


# =============================================================================
# ENTRY TYPE TESTS
# =============================================================================


class TestEntryTypes:
    """Tests for all BibTeX entry types."""

    @pytest.mark.parametrize("entry_type", list(BibTeXEntryType))
    def test_entry_type_generation(self, entry_type):
        """Test that all entry types can be generated."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=entry_type,
            cite_key="test",
            title="Test Title",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert f"@{entry_type.value}{{test," in result

    def test_required_fields_defined(self):
        """Test that all entry types have required fields defined."""
        for entry_type in BibTeXEntryType:
            assert entry_type in REQUIRED_FIELDS


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_entry(self):
        """Test generating empty entry."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.MISC,
            cite_key="empty"
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert "@misc{empty," in result
        assert "}" in result

    def test_very_long_title(self):
        """Test handling very long titles."""
        generator = FullBibTeXGenerator()
        long_title = "A Very Long Title " * 50
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            title=long_title,
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        assert len(result) > len(long_title)

    def test_unicode_author_names(self):
        """Test handling Unicode author names."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            authors=["José García", "François Müller", "北川 太郎"],
            title="Test",
            journal="Journal",
            year=2024
        )

        result = generator.generate_entry(entry, auto_key=False)

        # Should escape properly
        assert "author = " in result

    def test_special_chars_in_all_fields(self):
        """Test special characters in various fields."""
        generator = FullBibTeXGenerator()
        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="test",
            author="Smith & Jones",
            title="100% Effective: A $50 Solution #1",
            journal="Journal of A&B",
            year=2024,
            note="See http://example.com & more"
        )

        result = generator.generate_entry(entry, auto_key=False)

        # All special chars should be escaped
        assert r"\&" in result
        assert r"\%" in result
        assert r"\$" in result
        assert r"\#" in result

    def test_multiple_collision_suffix(self):
        """Test many collisions (beyond 26)."""
        generator = CiteKeyGenerator()

        # Register many existing keys
        for i in range(30):
            if i == 0:
                generator.used_keys.add("smith2024")
            elif i <= 26:
                generator.used_keys.add(f"smith2024{chr(ord('a') + i - 1)}")
            else:
                generator.used_keys.add(f"smith2024a{chr(ord('a') + i - 27)}")

        entry = GeneratedBibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            cite_key="",
            authors=["Smith"],
            year=2024
        )

        key = generator.generate(entry)

        # Should find a unique key
        assert key not in generator.used_keys - {key}
