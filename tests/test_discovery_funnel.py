"""
Tests for Discovery Funnel Service — DISC-1
Article Eater v23.1.0
2026-02-09
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.services.discovery_funnel import (
    DiscoveryFunnelService,
    VOIGap,
    GapSearch,
    PDFRetrievalAttempt,
    GapClosure,
    FunnelMetrics,
    GapType,
    GapStatus,
    RetrievalMethod,
    RetrievalStatus,
    ClosureType,
    create_gap_from_voi_result,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def service(temp_db):
    """Create a DiscoveryFunnelService with temp database."""
    return DiscoveryFunnelService(db_path=temp_db)


# =============================================================================
# VOI GAP TESTS
# =============================================================================

class TestVOIGap:
    """Tests for VOIGap data class."""

    def test_gap_creation_defaults(self):
        """Test gap creation with defaults."""
        gap = VOIGap(
            gap_id="gap-1",
            topic="Effect of plants on stress",
            gap_type=GapType.MISSING_EVIDENCE,
            predicted_voi=0.75
        )
        assert gap.gap_id == "gap-1"
        assert gap.status == GapStatus.OPEN
        assert gap.priority == 0.5
        assert gap.identified_at is not None

    def test_gap_to_dict(self):
        """Test gap serialization."""
        gap = VOIGap(
            gap_id="gap-2",
            topic="Window size and attention",
            gap_type=GapType.WEAK_SUPPORT,
            predicted_voi=0.65,
            search_terms=["window", "attention", "office"]
        )
        d = gap.to_dict()
        assert d["gap_id"] == "gap-2"
        assert d["gap_type"] == "weak_support"
        assert d["search_terms"] == ["window", "attention", "office"]

    def test_gap_type_from_string(self):
        """Test gap type conversion from string."""
        gap = VOIGap(
            gap_id="gap-3",
            topic="Test",
            gap_type="contradiction",
            predicted_voi=0.5
        )
        assert gap.gap_type == GapType.CONTRADICTION


class TestVOIGapService:
    """Tests for gap CRUD operations."""

    def test_create_and_get_gap(self, service):
        """Test creating and retrieving a gap."""
        gap = VOIGap(
            gap_id="test-gap-1",
            topic="Biophilia and productivity",
            gap_type=GapType.MISSING_EVIDENCE,
            predicted_voi=0.8,
            theory_id="biophilia"
        )
        created = service.create_gap(gap)
        assert created.gap_id == "test-gap-1"

        retrieved = service.get_gap("test-gap-1")
        assert retrieved is not None
        assert retrieved.topic == "Biophilia and productivity"
        assert retrieved.predicted_voi == 0.8

    def test_list_gaps_by_status(self, service):
        """Test listing gaps filtered by status."""
        # Create gaps with different statuses
        service.create_gap(VOIGap(
            gap_id="g1", topic="Open gap 1",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.7
        ))
        service.create_gap(VOIGap(
            gap_id="g2", topic="Open gap 2",
            gap_type=GapType.WEAK_SUPPORT, predicted_voi=0.6
        ))

        open_gaps = service.list_gaps(status=GapStatus.OPEN)
        assert len(open_gaps) == 2

        closed_gaps = service.list_gaps(status=GapStatus.CLOSED)
        assert len(closed_gaps) == 0

    def test_list_gaps_by_voi(self, service):
        """Test listing gaps filtered by minimum VOI."""
        service.create_gap(VOIGap(
            gap_id="high-voi", topic="High value gap",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.9
        ))
        service.create_gap(VOIGap(
            gap_id="low-voi", topic="Low value gap",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.3
        ))

        high_value = service.list_gaps(min_voi=0.5)
        assert len(high_value) == 1
        assert high_value[0].gap_id == "high-voi"

    def test_update_gap_status(self, service):
        """Test updating gap status."""
        service.create_gap(VOIGap(
            gap_id="status-test", topic="Status test gap",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.5
        ))

        success = service.update_gap_status("status-test", GapStatus.CLOSED)
        assert success

        gap = service.get_gap("status-test")
        assert gap.status == GapStatus.CLOSED
        assert gap.closed_at is not None


# =============================================================================
# SEARCH TESTS
# =============================================================================

class TestGapSearch:
    """Tests for GapSearch data class."""

    def test_search_creation(self):
        """Test search creation."""
        search = GapSearch(
            search_id="search-1",
            gap_id="gap-1",
            query="biophilic design office productivity",
            source="semantic_scholar",
            n_results=25,
            n_relevant=8
        )
        assert search.search_id == "search-1"
        assert search.relevance_rate == 8 / 25

    def test_search_to_dict(self):
        """Test search serialization."""
        search = GapSearch(
            search_id="search-2",
            gap_id="gap-2",
            query="plant stress reduction",
            source="pubmed",
            filters={"year_min": 2020, "type": "rct"}
        )
        d = search.to_dict()
        assert d["source"] == "pubmed"
        assert d["filters"]["year_min"] == 2020


class TestGapSearchService:
    """Tests for search recording."""

    def test_record_search(self, service):
        """Test recording a search."""
        # First create a gap
        service.create_gap(VOIGap(
            gap_id="search-gap", topic="Test gap",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.5
        ))

        search = GapSearch(
            search_id="s1",
            gap_id="search-gap",
            query="test query",
            source="semantic_scholar",
            n_results=10,
            n_relevant=3
        )
        recorded = service.record_search(search)
        assert recorded.search_id == "s1"

        # Verify gap status updated
        gap = service.get_gap("search-gap")
        assert gap.status == GapStatus.SEARCHING
        assert gap.last_searched_at is not None

    def test_get_searches_for_gap(self, service):
        """Test retrieving searches for a gap."""
        service.create_gap(VOIGap(
            gap_id="multi-search-gap", topic="Test",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.5
        ))

        for i in range(3):
            service.record_search(GapSearch(
                search_id=f"ms-{i}",
                gap_id="multi-search-gap",
                query=f"query {i}",
                source="pubmed",
                n_results=i * 5
            ))

        searches = service.get_searches_for_gap("multi-search-gap")
        assert len(searches) == 3


# =============================================================================
# PDF RETRIEVAL TESTS
# =============================================================================

class TestPDFRetrievalAttempt:
    """Tests for PDFRetrievalAttempt data class."""

    def test_successful_retrieval(self):
        """Test successful retrieval."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/test",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.SUCCESS,
            pdf_path="/path/to/file.pdf"
        )
        assert attempt.succeeded
        assert not attempt.is_retryable

    def test_paywall_failure(self):
        """Test paywall failure."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/paywall",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.PAYWALL
        )
        assert not attempt.succeeded
        assert not attempt.is_retryable

    def test_retryable_failure(self):
        """Test retryable failure."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/timeout",
            method=RetrievalMethod.UNPAYWALL,
            status=RetrievalStatus.TIMEOUT,
            attempt_number=1,
            max_retries=3
        )
        assert not attempt.succeeded
        assert attempt.is_retryable

    def test_max_retries_exceeded(self):
        """Test max retries exceeded."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/timeout",
            method=RetrievalMethod.UNPAYWALL,
            status=RetrievalStatus.TIMEOUT,
            attempt_number=3,
            max_retries=3
        )
        assert not attempt.is_retryable


class TestPDFRetrievalService:
    """Tests for retrieval recording."""

    def test_record_success(self, service):
        """Test recording successful retrieval."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/success",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.SUCCESS,
            pdf_path="/tmp/paper.pdf",
            pdf_size_bytes=1024000
        )
        recorded = service.record_retrieval_attempt(attempt)
        assert recorded.attempt_id is not None

    def test_record_failure(self, service):
        """Test recording failed retrieval."""
        attempt = PDFRetrievalAttempt(
            doi="10.1234/paywall",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.PAYWALL,
            http_status_code=403,
            error_message="Access denied"
        )
        recorded = service.record_retrieval_attempt(attempt)
        assert recorded.attempt_id is not None

    def test_get_retrieval_attempts_by_status(self, service):
        """Test filtering retrieval attempts by status."""
        # Record various attempts
        for status in [RetrievalStatus.SUCCESS, RetrievalStatus.PAYWALL, RetrievalStatus.SUCCESS]:
            service.record_retrieval_attempt(PDFRetrievalAttempt(
                doi=f"10.1234/{status.value}",
                method=RetrievalMethod.DIRECT_LINK,
                status=status
            ))

        successes = service.get_retrieval_attempts(status=RetrievalStatus.SUCCESS)
        assert len(successes) == 2

        paywalls = service.get_retrieval_attempts(status=RetrievalStatus.PAYWALL)
        assert len(paywalls) == 1

    def test_retrieval_stats(self, service):
        """Test retrieval statistics."""
        # Record various attempts with different methods/statuses
        attempts = [
            (RetrievalMethod.DIRECT_LINK, RetrievalStatus.SUCCESS),
            (RetrievalMethod.DIRECT_LINK, RetrievalStatus.PAYWALL),
            (RetrievalMethod.UNPAYWALL, RetrievalStatus.SUCCESS),
            (RetrievalMethod.UNPAYWALL, RetrievalStatus.NOT_FOUND),
        ]
        for i, (method, status) in enumerate(attempts):
            service.record_retrieval_attempt(PDFRetrievalAttempt(
                doi=f"10.1234/stat-{i}",
                method=method,
                status=status
            ))

        stats = service.get_retrieval_stats()
        assert "direct_link" in stats
        assert stats["direct_link"]["success"] == 1
        assert "paywall" in stats["direct_link"]["failures"]


# =============================================================================
# GAP CLOSURE TESTS
# =============================================================================

class TestGapClosure:
    """Tests for GapClosure data class."""

    def test_closure_voi_reduction(self):
        """Test VOI reduction calculation."""
        closure = GapClosure(
            gap_id="g1",
            paper_id="p1",
            voi_before=0.8,
            voi_after=0.3,
            closure_type=ClosureType.PARTIAL
        )
        assert closure.voi_reduction == 0.5

    def test_closure_to_dict(self):
        """Test closure serialization."""
        closure = GapClosure(
            gap_id="g2",
            paper_id="p2",
            voi_before=0.9,
            voi_after=0.1,
            closure_type=ClosureType.FULL,
            n_beliefs_added=5
        )
        d = closure.to_dict()
        assert d["closure_type"] == "full"
        assert d["voi_reduction"] == 0.8


class TestGapClosureService:
    """Tests for closure recording."""

    def test_record_full_closure(self, service):
        """Test recording full closure updates gap status."""
        service.create_gap(VOIGap(
            gap_id="close-me", topic="Gap to close",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.8
        ))

        closure = GapClosure(
            gap_id="close-me",
            paper_id="paper-1",
            voi_before=0.8,
            voi_after=0.05,
            closure_type=ClosureType.FULL,
            n_beliefs_added=3
        )
        recorded = service.record_closure(closure)
        assert recorded.closure_id is not None

        # Verify gap is now closed
        gap = service.get_gap("close-me")
        assert gap.status == GapStatus.CLOSED

    def test_record_partial_closure(self, service):
        """Test recording partial closure doesn't close gap."""
        service.create_gap(VOIGap(
            gap_id="partial-gap", topic="Gap with partial closure",
            gap_type=GapType.WEAK_SUPPORT, predicted_voi=0.7
        ))

        closure = GapClosure(
            gap_id="partial-gap",
            paper_id="paper-2",
            voi_before=0.7,
            voi_after=0.4,
            closure_type=ClosureType.PARTIAL
        )
        service.record_closure(closure)

        # Gap should still be open
        gap = service.get_gap("partial-gap")
        assert gap.status != GapStatus.CLOSED

    def test_get_closures_for_gap(self, service):
        """Test retrieving closures for a gap."""
        service.create_gap(VOIGap(
            gap_id="multi-close", topic="Gap with multiple closures",
            gap_type=GapType.MISSING_EVIDENCE, predicted_voi=0.9
        ))

        for i, ct in enumerate([ClosureType.PARTIAL, ClosureType.PARTIAL, ClosureType.FULL]):
            service.record_closure(GapClosure(
                gap_id="multi-close",
                paper_id=f"paper-{i}",
                voi_before=0.9 - i * 0.3,
                voi_after=0.9 - (i + 1) * 0.3,
                closure_type=ct
            ))

        closures = service.get_closures_for_gap("multi-close")
        assert len(closures) == 3


# =============================================================================
# METRICS TESTS
# =============================================================================

class TestFunnelMetrics:
    """Tests for FunnelMetrics data class."""

    def test_metrics_defaults(self):
        """Test metrics defaults."""
        metrics = FunnelMetrics()
        assert metrics.open_gaps == 0
        assert metrics.search_hit_rate is None
        assert metrics.end_to_end_rate is None

    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        metrics = FunnelMetrics(
            open_gaps=10,
            closed_gaps=5,
            searches_30d=20,
            results_found_30d=100
        )
        d = metrics.to_dict()
        assert d["open_gaps"] == 10
        assert d["closed_gaps"] == 5


class TestFunnelMetricsService:
    """Tests for funnel metrics calculation."""

    def test_get_empty_metrics(self, service):
        """Test metrics with no data."""
        metrics = service.get_funnel_metrics()
        assert metrics.open_gaps == 0
        assert metrics.searches_30d == 0

    def test_get_metrics_with_data(self, service):
        """Test metrics with sample data."""
        # Create gaps
        for i in range(5):
            service.create_gap(VOIGap(
                gap_id=f"metric-gap-{i}",
                topic=f"Metric gap {i}",
                gap_type=GapType.MISSING_EVIDENCE,
                predicted_voi=0.5 + i * 0.1
            ))

        # Record searches
        for i in range(3):
            service.record_search(GapSearch(
                search_id=f"metric-search-{i}",
                gap_id=f"metric-gap-{i}",
                query="test query",
                source="pubmed",
                n_results=10,
                n_relevant=3
            ))

        # Record retrievals
        service.record_retrieval_attempt(PDFRetrievalAttempt(
            doi="10.1234/metric-1",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.SUCCESS
        ))
        service.record_retrieval_attempt(PDFRetrievalAttempt(
            doi="10.1234/metric-2",
            method=RetrievalMethod.DIRECT_LINK,
            status=RetrievalStatus.PAYWALL
        ))

        metrics = service.get_funnel_metrics()
        assert metrics.searching_gaps == 3  # 3 gaps were searched
        assert metrics.searches_30d == 3
        assert metrics.retrieval_attempts_30d == 2
        assert metrics.retrieval_success_30d == 1
        assert metrics.paywall_failures_30d == 1

    def test_bottleneck_analysis(self, service):
        """Test bottleneck analysis."""
        # Create a scenario with poor PDF retrieval
        for i in range(10):
            status = RetrievalStatus.PAYWALL if i < 7 else RetrievalStatus.SUCCESS
            service.record_retrieval_attempt(PDFRetrievalAttempt(
                doi=f"10.1234/bottleneck-{i}",
                method=RetrievalMethod.DIRECT_LINK,
                status=status
            ))

        analysis = service.get_bottleneck_analysis()
        assert analysis["health"] in ["degraded", "poor"]
        assert len(analysis["bottlenecks"]) > 0
        assert any(b["stage"] == "retrieval" for b in analysis["bottlenecks"])


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Tests for convenience functions."""

    def test_create_gap_from_voi_result(self):
        """Test creating gap from VOI search result."""
        voi_result = {
            "topic": "Effect of natural light on circadian rhythm",
            "gap_type": "missing_evidence",
            "voi": 0.85,
            "theory_id": "chronobiology",
            "search_terms": ["natural light", "circadian", "office"],
            "uncertainty_reduction": 0.3,
        }

        gap = create_gap_from_voi_result(voi_result, web_id="web-123")

        assert gap.topic == "Effect of natural light on circadian rhythm"
        assert gap.gap_type == GapType.MISSING_EVIDENCE
        assert gap.predicted_voi == 0.85
        assert gap.theory_id == "chronobiology"
        assert gap.web_id == "web-123"
        assert gap.identified_by == "voi_search"
        assert "natural light" in gap.search_terms


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestFunnelIntegration:
    """Integration tests for full funnel flow."""

    def test_full_funnel_flow(self, service):
        """Test complete flow from gap to closure."""
        # 1. Identify gap
        gap = VOIGap(
            gap_id="full-flow-gap",
            topic="Effect of biophilic design on hospital recovery",
            gap_type=GapType.MISSING_EVIDENCE,
            predicted_voi=0.9,
            theory_id="biophilia",
            search_terms=["biophilic", "hospital", "recovery"]
        )
        service.create_gap(gap)
        assert service.get_gap("full-flow-gap").status == GapStatus.OPEN

        # 2. Execute search
        search = GapSearch(
            search_id="flow-search-1",
            gap_id="full-flow-gap",
            query="biophilic design hospital recovery RCT",
            source="pubmed",
            n_results=15,
            n_relevant=4,
            n_new=3,
            top_results=["doi-1", "doi-2", "doi-3"]
        )
        service.record_search(search)
        assert service.get_gap("full-flow-gap").status == GapStatus.SEARCHING

        # 3. Attempt PDF retrieval (mixed results)
        for i, doi in enumerate(search.top_results):
            status = RetrievalStatus.SUCCESS if i < 2 else RetrievalStatus.PAYWALL
            service.record_retrieval_attempt(PDFRetrievalAttempt(
                doi=doi,
                gap_id="full-flow-gap",
                search_id="flow-search-1",
                method=RetrievalMethod.UNPAYWALL,
                status=status
            ))

        attempts = service.get_retrieval_attempts(gap_id="full-flow-gap")
        assert len(attempts) == 3
        assert sum(1 for a in attempts if a.succeeded) == 2

        # 4. Record closure (partial - still one paper missing)
        closure = GapClosure(
            gap_id="full-flow-gap",
            paper_id="paper-from-doi-1",
            voi_before=0.9,
            voi_after=0.4,
            closure_type=ClosureType.PARTIAL,
            n_beliefs_added=5,
            relevance_to_gap=0.85
        )
        service.record_closure(closure)

        # 5. Verify final state
        gap = service.get_gap("full-flow-gap")
        assert gap.status == GapStatus.SEARCHING  # Not fully closed

        closures = service.get_closures_for_gap("full-flow-gap")
        assert len(closures) == 1
        assert closures[0].voi_reduction == 0.5

        # 6. Check metrics
        metrics = service.get_funnel_metrics()
        assert metrics.searching_gaps >= 1
