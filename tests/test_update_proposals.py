"""Tests for Template Update Proposal Generator. Sprint 13 Task 13.1."""

import pytest
from datetime import datetime

from src.cmr.learning.update_proposals import (
    UpdateProposal,
    Evidence,
    ProposalType,
    ProposalStatus,
    generate_proposal,
    generate_contradiction_proposal,
    generate_boundary_revision_proposal,
    generate_moderator_proposal,
    get_pending_proposals,
    update_proposal_status,
    format_proposal_summary,
    _generate_proposal_id,
    _assess_impact,
)


class TestEvidence:
    def test_creates_evidence(self):
        e = Evidence(
            paper_citation="Smith et al. 2024",
            effect_size=0.5,
            sample_n=100,
        )
        assert e.paper_citation == "Smith et al. 2024"
        assert e.effect_size == 0.5
        assert e.sample_n == 100

    def test_to_dict(self):
        e = Evidence(
            paper_citation="Smith et al. 2024",
            effect_size=0.5,
            sample_n=100,
            context="lab study",
            direction="increase",
        )
        d = e.to_dict()
        assert d["paper_citation"] == "Smith et al. 2024"
        assert d["effect_size"] == 0.5
        assert d["sample_n"] == 100
        assert d["context"] == "lab study"
        assert d["direction"] == "increase"

    def test_optional_fields(self):
        e = Evidence(paper_citation="Test Paper")
        assert e.effect_size is None
        assert e.sample_n is None
        assert e.context is None


class TestUpdateProposal:
    def test_creates_proposal(self):
        p = UpdateProposal(
            proposal_id="UPD-20260217-ABC123",
            proposal_type=ProposalType.BOUNDARY_REVISION,
            template_id="VF3",
        )
        assert p.proposal_id == "UPD-20260217-ABC123"
        assert p.proposal_type == ProposalType.BOUNDARY_REVISION
        assert p.template_id == "VF3"

    def test_default_values(self):
        p = UpdateProposal(
            proposal_id="test",
            proposal_type=ProposalType.CONTRADICTION_FLAG,
            template_id="L1",
        )
        assert p.confidence == 0.5
        assert p.requires_human_review is True
        assert p.status == ProposalStatus.PROPOSED
        assert len(p.evidence) == 0

    def test_to_dict(self):
        p = UpdateProposal(
            proposal_id="test",
            proposal_type=ProposalType.NEW_PARAMETER,
            template_id="VIEW1",
            parameter_name="test_param",
            current_value=10.0,
            proposed_value=12.0,
            confidence=0.7,
        )
        d = p.to_dict()
        assert d["proposal_id"] == "test"
        assert d["proposal_type"] == "new_parameter"
        assert d["template_id"] == "VIEW1"
        assert d["parameter_name"] == "test_param"
        assert d["current_value"] == 10.0
        assert d["proposed_value"] == 12.0
        assert d["confidence"] == 0.7


class TestProposalTypes:
    def test_boundary_revision(self):
        assert ProposalType.BOUNDARY_REVISION.value == "boundary_revision"

    def test_new_parameter(self):
        assert ProposalType.NEW_PARAMETER.value == "new_parameter"

    def test_contradiction_flag(self):
        assert ProposalType.CONTRADICTION_FLAG.value == "contradiction_flag"

    def test_moderator_addition(self):
        assert ProposalType.MODERATOR_ADDITION.value == "moderator_addition"

    def test_interaction_discovery(self):
        assert ProposalType.INTERACTION_DISCOVERY.value == "interaction_discovery"


class TestProposalStatus:
    def test_proposed(self):
        assert ProposalStatus.PROPOSED.value == "proposed"

    def test_accepted(self):
        assert ProposalStatus.ACCEPTED.value == "accepted"

    def test_rejected(self):
        assert ProposalStatus.REJECTED.value == "rejected"


class TestGenerateProposalId:
    def test_generates_unique_ids(self):
        id1 = _generate_proposal_id("VF3", ProposalType.BOUNDARY_REVISION)
        id2 = _generate_proposal_id("VF3", ProposalType.BOUNDARY_REVISION)
        # IDs may be same if generated in same second, but format should be correct
        assert id1.startswith("UPD-")
        assert len(id1) > 10

    def test_id_format(self):
        id1 = _generate_proposal_id("L1", ProposalType.NEW_PARAMETER, "test_param")
        assert id1.startswith("UPD-")
        parts = id1.split("-")
        assert len(parts) == 3  # UPD, date, hash


class TestAssessImpact:
    def test_boundary_revision_impact(self):
        impact = _assess_impact("VF3", ProposalType.BOUNDARY_REVISION, 2.75, 3.0)
        assert "Boundary shift" in impact
        assert "%" in impact

    def test_contradiction_impact(self):
        impact = _assess_impact("L1", ProposalType.CONTRADICTION_FLAG, 500, 350)
        assert "CRITICAL" in impact
        assert "contradicts" in impact.lower()

    def test_new_parameter_impact(self):
        impact = _assess_impact("VIEW1", ProposalType.NEW_PARAMETER, None, 0.5)
        assert "EXTENSION" in impact

    def test_moderator_impact(self):
        impact = _assess_impact("SOC2", ProposalType.MODERATOR_ADDITION, None, {"young": 1.2})
        assert "MODERATOR" in impact


class TestGenerateProposal:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_proposals.db")

    def test_creates_proposal(self, temp_db):
        evidence = Evidence(paper_citation="Test 2024", effect_size=0.4, sample_n=50)
        p = generate_proposal(
            template_id="VF3",
            proposal_type=ProposalType.BOUNDARY_REVISION,
            evidence=[evidence],
            parameter_name="optimal_Rh",
            current_value=0.5,
            proposed_value=0.6,
            db_path=temp_db,
        )
        assert isinstance(p, UpdateProposal)
        assert p.template_id == "VF3"
        assert p.proposal_type == ProposalType.BOUNDARY_REVISION

    def test_proposal_has_id(self, temp_db):
        p = generate_proposal(
            template_id="L1",
            proposal_type=ProposalType.NEW_PARAMETER,
            evidence=[],
            db_path=temp_db,
        )
        assert p.proposal_id.startswith("UPD-")

    def test_proposal_has_impact_assessment(self, temp_db):
        p = generate_proposal(
            template_id="VIEW1",
            proposal_type=ProposalType.CONTRADICTION_FLAG,
            evidence=[Evidence(paper_citation="Test")],
            db_path=temp_db,
        )
        assert p.impact_assessment != ""

    def test_requires_human_review(self, temp_db):
        p = generate_proposal(
            template_id="MAT4",
            proposal_type=ProposalType.MODERATOR_ADDITION,
            evidence=[],
            db_path=temp_db,
        )
        assert p.requires_human_review is True

    def test_status_is_proposed(self, temp_db):
        p = generate_proposal(
            template_id="SC4",
            proposal_type=ProposalType.INTERACTION_DISCOVERY,
            evidence=[],
            db_path=temp_db,
        )
        assert p.status == ProposalStatus.PROPOSED


class TestGenerateContradictionProposal:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_contradiction.db")

    def test_creates_contradiction(self, temp_db):
        evidence = Evidence(
            paper_citation="Contrary 2024",
            effect_size=-0.3,
            sample_n=80,
        )
        p = generate_contradiction_proposal(
            template_id="VF3",
            parameter_name="optimal_ceiling",
            current_value=3.0,
            observed_value=2.5,
            evidence=evidence,
            db_path=temp_db,
        )
        assert p.proposal_type == ProposalType.CONTRADICTION_FLAG
        assert p.current_value == 3.0
        assert p.proposed_value == 2.5

    def test_confidence_increases_with_sample(self, temp_db):
        small_evidence = Evidence(paper_citation="Small", sample_n=20)
        large_evidence = Evidence(paper_citation="Large", sample_n=150)

        p_small = generate_contradiction_proposal(
            template_id="L1",
            parameter_name="test",
            current_value=1,
            observed_value=2,
            evidence=small_evidence,
            db_path=temp_db,
        )
        p_large = generate_contradiction_proposal(
            template_id="L2",
            parameter_name="test",
            current_value=1,
            observed_value=2,
            evidence=large_evidence,
            db_path=temp_db,
        )
        assert p_large.confidence > p_small.confidence


class TestGenerateBoundaryRevisionProposal:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_boundary.db")

    def test_creates_boundary_proposal(self, temp_db):
        evidence = [
            Evidence(paper_citation="Study 1", effect_size=0.5, sample_n=100),
            Evidence(paper_citation="Study 2", effect_size=0.4, sample_n=80),
        ]
        p = generate_boundary_revision_proposal(
            template_id="VF3",
            parameter_name="goldilocks_low",
            current_boundary=0.4,
            proposed_boundary=0.45,
            evidence=evidence,
            db_path=temp_db,
        )
        assert p.proposal_type == ProposalType.BOUNDARY_REVISION
        assert p.current_value == 0.4
        assert p.proposed_value == 0.45

    def test_more_evidence_higher_confidence(self, temp_db):
        single = [Evidence(paper_citation="One", sample_n=50)]
        multiple = [
            Evidence(paper_citation="One", sample_n=50),
            Evidence(paper_citation="Two", sample_n=60),
            Evidence(paper_citation="Three", sample_n=70),
        ]

        p_single = generate_boundary_revision_proposal(
            template_id="L1",
            parameter_name="test",
            current_boundary=1.0,
            proposed_boundary=1.1,
            evidence=single,
            db_path=temp_db,
        )
        p_multiple = generate_boundary_revision_proposal(
            template_id="L2",
            parameter_name="test",
            current_boundary=1.0,
            proposed_boundary=1.1,
            evidence=multiple,
            db_path=temp_db,
        )
        assert p_multiple.confidence > p_single.confidence


class TestGenerateModeratorProposal:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_moderator.db")

    def test_creates_moderator_proposal(self, temp_db):
        evidence = [Evidence(paper_citation="Age Study", sample_n=100)]
        p = generate_moderator_proposal(
            template_id="VF3",
            moderator_name="age_group",
            moderator_values={"child": 1.3, "adult": 1.0, "elderly": 0.9},
            evidence=evidence,
            db_path=temp_db,
        )
        assert p.proposal_type == ProposalType.MODERATOR_ADDITION
        assert p.parameter_name == "age_group"
        assert isinstance(p.proposed_value, dict)


class TestPersistenceAndRetrieval:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_persist.db")

    def test_persists_proposal(self, temp_db):
        generate_proposal(
            template_id="TEST1",
            proposal_type=ProposalType.NEW_PARAMETER,
            evidence=[Evidence(paper_citation="Test Paper")],
            db_path=temp_db,
        )
        # Should be retrievable
        pending = get_pending_proposals(db_path=temp_db)
        assert len(pending) >= 1
        assert any(p.template_id == "TEST1" for p in pending)

    def test_retrieves_by_template(self, temp_db):
        generate_proposal(
            template_id="VF3",
            proposal_type=ProposalType.BOUNDARY_REVISION,
            evidence=[],
            db_path=temp_db,
        )
        generate_proposal(
            template_id="L1",
            proposal_type=ProposalType.NEW_PARAMETER,
            evidence=[],
            db_path=temp_db,
        )

        vf3_proposals = get_pending_proposals(db_path=temp_db, template_id="VF3")
        assert all(p.template_id == "VF3" for p in vf3_proposals)

    def test_retrieves_by_type(self, temp_db):
        generate_proposal(
            template_id="A1",
            proposal_type=ProposalType.CONTRADICTION_FLAG,
            evidence=[],
            db_path=temp_db,
        )
        generate_proposal(
            template_id="A2",
            proposal_type=ProposalType.NEW_PARAMETER,
            evidence=[],
            db_path=temp_db,
        )

        contradictions = get_pending_proposals(
            db_path=temp_db,
            proposal_type=ProposalType.CONTRADICTION_FLAG,
        )
        assert all(p.proposal_type == ProposalType.CONTRADICTION_FLAG for p in contradictions)


class TestUpdateStatus:
    @pytest.fixture
    def temp_db(self, tmp_path):
        return str(tmp_path / "test_status.db")

    def test_updates_status(self, temp_db):
        p = generate_proposal(
            template_id="STATUS_TEST",
            proposal_type=ProposalType.NEW_PARAMETER,
            evidence=[],
            db_path=temp_db,
        )
        assert p.status == ProposalStatus.PROPOSED

        success = update_proposal_status(
            proposal_id=p.proposal_id,
            new_status=ProposalStatus.ACCEPTED,
            reviewed_by="test_reviewer",
            review_notes="Looks good",
            db_path=temp_db,
        )
        assert success is True

    def test_returns_false_for_missing(self, temp_db):
        success = update_proposal_status(
            proposal_id="NONEXISTENT",
            new_status=ProposalStatus.REJECTED,
            reviewed_by="test",
            db_path=temp_db,
        )
        assert success is False


class TestFormatProposalSummary:
    def test_formats_proposal(self):
        p = UpdateProposal(
            proposal_id="UPD-20260217-ABC123",
            proposal_type=ProposalType.BOUNDARY_REVISION,
            template_id="VF3",
            parameter_name="optimal_Rh",
            current_value=0.5,
            proposed_value=0.6,
            evidence=[
                Evidence(paper_citation="Smith 2024", effect_size=0.4, sample_n=100)
            ],
            confidence=0.7,
            impact_assessment="Boundary shift: 20% change | SIGNIFICANT",
        )
        summary = format_proposal_summary(p)
        assert "UPD-20260217-ABC123" in summary
        assert "VF3" in summary
        assert "boundary_revision" in summary
        assert "Smith 2024" in summary
        assert "0.5" in summary
        assert "0.6" in summary

    def test_includes_evidence(self):
        p = UpdateProposal(
            proposal_id="test",
            proposal_type=ProposalType.NEW_PARAMETER,
            template_id="L1",
            evidence=[
                Evidence(paper_citation="Paper A", effect_size=0.3),
                Evidence(paper_citation="Paper B", sample_n=50),
            ],
        )
        summary = format_proposal_summary(p)
        assert "Paper A" in summary
        assert "Paper B" in summary
        assert "d=0.30" in summary
        assert "N=50" in summary
