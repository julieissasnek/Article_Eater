"""
Tests for Paper Fetcher Service
===============================

Tests for the unified paper ingestion client.

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone

from src.services.paper_fetcher import (
    PaperFetcher,
    PaperMetadata,
    Author,
    FetchResult,
    FetchStatus,
    IdentifierType,
    MockCrossRefClient,
    MockPubMedClient,
    MockSemanticScholarClient,
    MockArxivClient,
    estimate_study_type,
    generate_paper_id
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    return PaperMetadata(
        paper_id="doi:10.1234/test",
        doi="10.1234/test",
        pmid="12345678",
        title="Effects of Natural Light on Mood",
        abstract="This study examines the relationship between natural light exposure and mood.",
        authors=[
            Author(name="Smith, J.", affiliation="University"),
            Author(name="Jones, M.")
        ],
        year=2020,
        venue="Journal of Environmental Psychology",
        keywords=["natural light", "mood", "wellbeing"],
        citation_count=50,
        source="crossref"
    )


@pytest.fixture
def crossref_client(sample_paper):
    """Create a CrossRef client with cached paper."""
    client = MockCrossRefClient()
    client.cache["10.1234/test"] = sample_paper
    return client


@pytest.fixture
def pubmed_client():
    """Create a PubMed client with cached paper."""
    client = MockPubMedClient()
    client.cache["12345678"] = PaperMetadata(
        paper_id="pmid:12345678",
        pmid="12345678",
        title="PubMed Test Paper",
        abstract="A paper from PubMed.",
        authors=[Author(name="PubMed Author")],
        year=2019,
        mesh_terms=["Lighting", "Affect"],
        source="pubmed"
    )
    return client


@pytest.fixture
def paper_fetcher(crossref_client, pubmed_client):
    """Create a paper fetcher with mock clients."""
    return PaperFetcher(
        crossref_client=crossref_client,
        pubmed_client=pubmed_client
    )


# =============================================================================
# Identifier Detection Tests
# =============================================================================

class TestIdentifierDetection:
    """Tests for identifier type detection."""

    def test_detect_doi_standard(self):
        """Test detecting standard DOI format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("10.1234/test") == IdentifierType.DOI
        assert fetcher.detect_identifier_type("10.1000/xyz123") == IdentifierType.DOI
        assert fetcher.detect_identifier_type("10.12345/abcd.efgh") == IdentifierType.DOI

    def test_detect_doi_url(self):
        """Test detecting DOI URL format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("https://doi.org/10.1234/test") == IdentifierType.DOI
        assert fetcher.detect_identifier_type("http://dx.doi.org/10.1234/test") == IdentifierType.DOI

    def test_detect_pmid(self):
        """Test detecting PMID format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("12345678") == IdentifierType.PMID
        assert fetcher.detect_identifier_type("PMID:12345678") == IdentifierType.PMID
        assert fetcher.detect_identifier_type("pmid: 12345678") == IdentifierType.PMID

    def test_detect_arxiv_new_format(self):
        """Test detecting arXiv new format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("2301.12345") == IdentifierType.ARXIV
        assert fetcher.detect_identifier_type("arxiv:2301.12345") == IdentifierType.ARXIV
        assert fetcher.detect_identifier_type("arXiv:2301.12345v2") == IdentifierType.ARXIV

    def test_detect_arxiv_old_format(self):
        """Test detecting arXiv old format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("arxiv:cs.AI/0123456") == IdentifierType.ARXIV

    def test_detect_semantic_scholar_id(self):
        """Test detecting Semantic Scholar ID (40-char hex)."""
        fetcher = PaperFetcher()

        s2_id = "a" * 40
        assert fetcher.detect_identifier_type(s2_id) == IdentifierType.SEMANTIC_SCHOLAR

    def test_detect_unknown(self):
        """Test unknown identifier format."""
        fetcher = PaperFetcher()

        assert fetcher.detect_identifier_type("random text") == IdentifierType.UNKNOWN
        assert fetcher.detect_identifier_type("123") == IdentifierType.UNKNOWN
        assert fetcher.detect_identifier_type("") == IdentifierType.UNKNOWN


# =============================================================================
# Fetch Tests
# =============================================================================

class TestFetch:
    """Tests for paper fetching."""

    def test_fetch_by_doi(self, paper_fetcher):
        """Test fetching by DOI."""
        result = paper_fetcher.fetch("10.1234/test")

        assert result.status == FetchStatus.SUCCESS
        assert result.metadata is not None
        assert result.metadata.title == "Effects of Natural Light on Mood"

    def test_fetch_by_doi_url(self, paper_fetcher):
        """Test fetching by DOI URL."""
        result = paper_fetcher.fetch("https://doi.org/10.1234/test")

        assert result.status == FetchStatus.SUCCESS

    def test_fetch_by_pmid(self, paper_fetcher):
        """Test fetching by PMID."""
        result = paper_fetcher.fetch("12345678")

        assert result.status == FetchStatus.SUCCESS
        assert result.metadata.title == "PubMed Test Paper"

    def test_fetch_by_pmid_with_prefix(self, paper_fetcher):
        """Test fetching by PMID with prefix."""
        result = paper_fetcher.fetch("PMID:12345678")

        assert result.status == FetchStatus.SUCCESS

    def test_fetch_not_found(self, paper_fetcher):
        """Test fetching non-existent paper."""
        result = paper_fetcher.fetch("10.9999/notfound")

        assert result.status == FetchStatus.NOT_FOUND
        assert result.error_message is not None

    def test_fetch_unknown_identifier(self, paper_fetcher):
        """Test fetching with unknown identifier type."""
        result = paper_fetcher.fetch("not a real identifier")

        assert result.status == FetchStatus.ERROR
        assert "Could not detect identifier type" in result.error_message


# =============================================================================
# Duplicate Detection Tests
# =============================================================================

class TestDuplicateDetection:
    """Tests for duplicate paper detection."""

    def test_detect_duplicate_by_doi(self, sample_paper):
        """Test detecting duplicate by DOI."""
        existing = {"paper_1": sample_paper}
        fetcher = PaperFetcher(existing_papers=existing)

        result = fetcher.fetch("10.1234/test")

        assert result.status == FetchStatus.DUPLICATE
        assert result.duplicate_of == "paper_1"

    def test_detect_duplicate_by_pmid(self, sample_paper):
        """Test detecting duplicate by PMID."""
        existing = {"paper_1": sample_paper}
        fetcher = PaperFetcher(existing_papers=existing)

        result = fetcher.fetch("12345678")

        assert result.status == FetchStatus.DUPLICATE

    def test_no_duplicate_for_new_paper(self, sample_paper):
        """Test that new papers are not flagged as duplicates."""
        existing = {"paper_1": sample_paper}
        fetcher = PaperFetcher(existing_papers=existing)

        # Different DOI should not be duplicate
        result = fetcher.fetch("10.9999/different")
        assert result.status != FetchStatus.DUPLICATE


# =============================================================================
# Paper Metadata Tests
# =============================================================================

class TestPaperMetadata:
    """Tests for PaperMetadata dataclass."""

    def test_to_dict(self, sample_paper):
        """Test serialization to dict."""
        d = sample_paper.to_dict()

        assert d['paper_id'] == "doi:10.1234/test"
        assert d['doi'] == "10.1234/test"
        assert d['title'] == "Effects of Natural Light on Mood"
        assert len(d['authors']) == 2
        assert d['year'] == 2020

    def test_from_dict(self, sample_paper):
        """Test deserialization from dict."""
        d = sample_paper.to_dict()
        restored = PaperMetadata.from_dict(d)

        assert restored.paper_id == sample_paper.paper_id
        assert restored.doi == sample_paper.doi
        assert restored.title == sample_paper.title
        assert len(restored.authors) == len(sample_paper.authors)
        assert restored.year == sample_paper.year

    def test_roundtrip(self, sample_paper):
        """Test full serialization roundtrip."""
        d = sample_paper.to_dict()
        restored = PaperMetadata.from_dict(d)

        assert restored.paper_id == sample_paper.paper_id
        assert restored.abstract == sample_paper.abstract
        assert restored.keywords == sample_paper.keywords


# =============================================================================
# Citation Suggestions Tests
# =============================================================================

class TestCitationSuggestions:
    """Tests for citation-based paper suggestions."""

    def test_get_citation_suggestions(self):
        """Test getting citation suggestions."""
        paper = PaperMetadata(
            paper_id="paper_1",
            title="Test",
            references=["paper_2", "paper_3", "paper_4"],
            cited_by=["paper_5", "paper_6"]
        )
        existing = {"paper_1": paper, "paper_2": PaperMetadata(paper_id="paper_2", title="Ref 1")}

        fetcher = PaperFetcher(existing_papers=existing)
        suggestions = fetcher.get_citation_suggestions("paper_1", list(existing.keys()))

        assert "paper_2" in suggestions['cites_in_web']
        assert "paper_3" in suggestions['cites_suggestions']
        assert "paper_5" in suggestions['citing_suggestions']

    def test_citation_suggestions_missing_paper(self):
        """Test suggestions for non-existent paper."""
        fetcher = PaperFetcher()
        suggestions = fetcher.get_citation_suggestions("nonexistent", [])

        assert suggestions['citing'] == []
        assert suggestions['cited_by'] == []


# =============================================================================
# Study Type Estimation Tests
# =============================================================================

class TestStudyTypeEstimation:
    """Tests for study type estimation from abstract."""

    def test_detect_meta_analysis(self):
        """Test detecting meta-analysis."""
        abstract = "This meta-analysis combines results from 50 studies..."
        assert estimate_study_type(abstract, "Meta-Analysis of Light Effects") == "meta_analysis"

    def test_detect_systematic_review(self):
        """Test detecting systematic review."""
        abstract = "A systematic review of the literature on..."
        assert estimate_study_type(abstract, "Test") == "systematic_review"

    def test_detect_rct(self):
        """Test detecting randomized controlled trial."""
        abstract = "Participants were randomized to treatment or control..."
        assert estimate_study_type(abstract, "Test") == "rct"

    def test_detect_longitudinal(self):
        """Test detecting longitudinal study."""
        abstract = "This longitudinal study followed participants for 5 years..."
        assert estimate_study_type(abstract, "Test") == "longitudinal"

    def test_detect_cross_sectional(self):
        """Test detecting cross-sectional study."""
        abstract = "A cross-sectional survey of 500 participants..."
        assert estimate_study_type(abstract, "Test") == "cross_sectional"

    def test_detect_from_title(self):
        """Test detecting study type from title when abstract is empty."""
        assert estimate_study_type(None, "A Meta-Analysis of Effects") == "meta_analysis"

    def test_unknown_study_type(self):
        """Test handling of unknown study type."""
        assert estimate_study_type("Some generic text", "Generic Title") is None


# =============================================================================
# Paper ID Generation Tests
# =============================================================================

class TestPaperIdGeneration:
    """Tests for paper ID generation."""

    def test_generate_id_from_doi(self):
        """Test generating ID from DOI."""
        paper = PaperMetadata(paper_id="", doi="10.1234/test", title="Test")
        paper_id = generate_paper_id(paper)

        assert paper_id == "doi:10.1234/test"

    def test_generate_id_from_pmid(self):
        """Test generating ID from PMID when no DOI."""
        paper = PaperMetadata(paper_id="", pmid="12345678", title="Test")
        paper_id = generate_paper_id(paper)

        assert paper_id == "pmid:12345678"

    def test_generate_id_from_metadata(self):
        """Test generating ID from author/year/title."""
        paper = PaperMetadata(
            paper_id="",
            title="Effects of Light on Mood",
            authors=[Author(name="Smith, John")],
            year=2020
        )
        paper_id = generate_paper_id(paper)

        assert "smith" in paper_id.lower()
        assert "2020" in paper_id
        assert "effects" in paper_id.lower()


# =============================================================================
# Search Tests
# =============================================================================

class TestSearch:
    """Tests for paper search."""

    def test_search_returns_dict(self):
        """Test that search returns dict of source -> results."""
        fetcher = PaperFetcher()
        results = fetcher.search("natural light mood")

        assert isinstance(results, dict)
        assert 'pubmed' in results or 'semantic_scholar' in results

    def test_search_specific_sources(self):
        """Test searching specific sources only."""
        fetcher = PaperFetcher()
        results = fetcher.search("test", sources=['arxiv'])

        assert 'arxiv' in results
        assert 'pubmed' not in results


# =============================================================================
# Author Tests
# =============================================================================

class TestAuthor:
    """Tests for Author dataclass."""

    def test_author_to_dict(self):
        """Test author serialization."""
        author = Author(
            name="Smith, John",
            affiliation="MIT",
            orcid="0000-0001-2345-6789"
        )
        d = author.to_dict()

        assert d['name'] == "Smith, John"
        assert d['affiliation'] == "MIT"
        assert d['orcid'] == "0000-0001-2345-6789"

    def test_author_minimal(self):
        """Test author with just name."""
        author = Author(name="Jones, Mary")
        d = author.to_dict()

        assert d['name'] == "Jones, Mary"
        assert d['affiliation'] is None


# =============================================================================
# FetchResult Tests
# =============================================================================

class TestFetchResult:
    """Tests for FetchResult dataclass."""

    def test_success_result(self, sample_paper):
        """Test successful fetch result."""
        result = FetchResult(
            status=FetchStatus.SUCCESS,
            metadata=sample_paper
        )
        d = result.to_dict()

        assert d['status'] == 'success'
        assert d['metadata'] is not None

    def test_error_result(self):
        """Test error fetch result."""
        result = FetchResult(
            status=FetchStatus.ERROR,
            error_message="Something went wrong"
        )
        d = result.to_dict()

        assert d['status'] == 'error'
        assert d['error_message'] == "Something went wrong"
        assert d['metadata'] is None

    def test_duplicate_result(self):
        """Test duplicate fetch result."""
        result = FetchResult(
            status=FetchStatus.DUPLICATE,
            duplicate_of="existing_paper_123"
        )
        d = result.to_dict()

        assert d['status'] == 'duplicate'
        assert d['duplicate_of'] == "existing_paper_123"
