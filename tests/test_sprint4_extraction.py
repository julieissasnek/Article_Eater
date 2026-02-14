"""
Tests for Sprint 4: Extraction Pipeline Extensions.

Verifies implementation of:
- Task 4.1: Argumentative structure extraction
- Task 4.2: Source quality metadata extraction
- Task 4.3: Epistemic mediation pathway classification
- Task 4.4: PE subtype classification
"""

import pytest


class TestTask41ArgumentativeExtraction:
    """Task 4.1: Extract argumentative structure from papers."""

    def test_can_import_argumentative_module(self):
        """Module imports successfully."""
        from src.epistemic.extraction.argumentative import (
            ArgumentativeMetadata,
            extract_argumentative_structure,
        )
        assert ArgumentativeMetadata is not None
        assert extract_argumentative_structure is not None

    def test_extract_theory_support(self):
        """Detects theory support language."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = """
        Our findings are consistent with Kaplan's attention restoration theory.
        The results support the prediction that natural environments reduce
        directed attention fatigue.
        """

        result = extract_argumentative_structure(text)
        assert result.argument_for is not None
        assert "attention restoration" in result.argument_for.lower()
        assert result.support_confidence > 0

    def test_extract_theory_challenge(self):
        """Detects theory challenge language."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = """
        These findings are inconsistent with Ulrich's stress recovery theory.
        The results challenge the view that nature views reduce stress through
        automatic physiological pathways.
        """

        result = extract_argumentative_structure(text)
        assert result.argument_against is not None
        assert "stress recovery" in result.argument_against.lower()
        assert result.challenge_confidence > 0

    def test_detect_direct_replication(self):
        """Detects direct replication studies."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = """
        This study is a direct replication of the original experiment by
        Smith et al. (2015). We followed the exact same protocol.
        """

        result = extract_argumentative_structure(text)
        assert result.replication_type == "direct_replication"

    def test_detect_meta_analysis(self):
        """Detects meta-analysis papers."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = """
        We conducted a meta-analysis of 47 studies examining the effect of
        biophilic design on workplace productivity.
        """

        result = extract_argumentative_structure(text)
        assert result.replication_type == "meta_analysis"

    def test_detect_adversarial_scrutiny(self):
        """Detects adversarial scrutiny indicators."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = """
        This multi-lab replication study involved independent research groups
        from different theoretical traditions testing competing hypotheses.
        """

        result = extract_argumentative_structure(text)
        assert result.adversarial_scrutiny_survived is True
        assert len(result.adversarial_indicators_found) > 0

    def test_original_study_default(self):
        """Default replication type is original."""
        from src.epistemic.extraction.argumentative import extract_argumentative_structure

        text = "We conducted an experiment examining how ceiling height affects creativity."

        result = extract_argumentative_structure(text)
        assert result.replication_type == "original"

    def test_metadata_serialization(self):
        """ArgumentativeMetadata can be serialized."""
        from src.epistemic.extraction.argumentative import ArgumentativeMetadata

        meta = ArgumentativeMetadata(
            argument_for="attention restoration theory",
            argument_against=None,
            adversarial_scrutiny_survived=True,
            replication_type="direct_replication",
        )

        result = meta.to_dict()
        assert result["argument_for"] == "attention restoration theory"
        assert result["adversarial_scrutiny_survived"] is True


class TestTask42SourceQualityExtraction:
    """Task 4.2: Extract source quality metadata."""

    def test_can_import_source_quality_module(self):
        """Module imports successfully."""
        from src.epistemic.extraction.source_quality_metadata import (
            SourceQualityMetadata,
            extract_source_quality_metadata,
            StudyDesign,
            PaperType,
        )
        assert SourceQualityMetadata is not None
        assert StudyDesign.RCT == "rct"

    def test_detect_rct_design(self):
        """Detects randomized controlled trial."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
            StudyDesign,
        )

        text = """
        Participants were randomly assigned to one of three conditions.
        This randomized controlled trial examined the effects of
        office layout on productivity.
        """

        result = extract_source_quality_metadata(text)
        assert result.study_design == StudyDesign.RCT

    def test_detect_correlational_design(self):
        """Detects correlational study design."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
            StudyDesign,
        )

        text = """
        This cross-sectional survey examined correlations between
        workplace design features and employee satisfaction.
        """

        result = extract_source_quality_metadata(text)
        assert result.study_design == StudyDesign.CORRELATIONAL

    def test_extract_sample_size(self):
        """Extracts sample size correctly."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
        )

        text = "A total of 200 participants completed the study (N = 200)."

        result = extract_source_quality_metadata(text)
        assert result.sample_size == 200

    def test_extract_multiple_sample_sizes(self):
        """Handles multiple sample sizes, takes largest."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
        )

        text = """
        Study 1 included 50 participants. Study 2 included 75 participants.
        In total, N = 125 across both studies.
        """

        result = extract_source_quality_metadata(text)
        assert result.sample_size == 125  # Largest
        assert 50 in result.sample_sizes_found
        assert 75 in result.sample_sizes_found

    def test_detect_preregistration(self):
        """Detects pre-registration indicators."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
        )

        text = """
        This study was pre-registered on the Open Science Framework
        (OSF) prior to data collection.
        """

        result = extract_source_quality_metadata(text)
        assert result.pre_registered is True

    def test_detect_meta_analysis_paper_type(self):
        """Detects meta-analysis paper type."""
        from src.epistemic.extraction.source_quality_metadata import (
            extract_source_quality_metadata,
            PaperType,
        )

        text = "Meta-analysis of biophilic design effects on wellbeing"

        result = extract_source_quality_metadata(text, title=text)
        assert result.paper_type == PaperType.META_ANALYSIS

    def test_metadata_serialization(self):
        """SourceQualityMetadata can be serialized."""
        from src.epistemic.extraction.source_quality_metadata import (
            SourceQualityMetadata,
            StudyDesign,
            PaperType,
        )

        meta = SourceQualityMetadata(
            study_design=StudyDesign.RCT,
            sample_size=200,
            pre_registered=True,
            paper_type=PaperType.PRIMARY,
        )

        result = meta.to_dict()
        assert result["study_design"] == "rct"
        assert result["sample_size"] == 200


class TestTask43PathwayClassification:
    """Task 4.3: Classify epistemic mediation pathway."""

    def test_can_import_pathway_module(self):
        """Module imports successfully."""
        from src.epistemic.extraction.pathway_classifier import (
            classify_pathway,
            PathwayClassification,
            EPISTEMIC_KEYWORDS,
            SUBPERSONAL_KEYWORDS,
        )
        assert classify_pathway is not None
        assert len(EPISTEMIC_KEYWORDS) > 0
        assert len(SUBPERSONAL_KEYWORDS) > 0

    def test_classify_subpersonal(self):
        """Correctly classifies subpersonal pathway."""
        from src.epistemic.extraction.pathway_classifier import classify_pathway

        result = classify_pathway("Temperature affects circadian rhythm")
        assert result == "subpersonal"

    def test_classify_personal_epistemic(self):
        """Correctly classifies personal epistemic pathway."""
        from src.epistemic.extraction.pathway_classifier import classify_pathway

        result = classify_pathway("Spatial legibility affects wayfinding comprehension")
        assert result == "personal_epistemic"

    def test_classify_mixed(self):
        """Correctly classifies mixed pathway."""
        from src.epistemic.extraction.pathway_classifier import classify_pathway

        result = classify_pathway("Lighting color temperature affects mood interpretation")
        assert result == "mixed"

    def test_return_details_option(self):
        """Can return detailed classification."""
        from src.epistemic.extraction.pathway_classifier import (
            classify_pathway,
            PathwayClassification,
        )

        result = classify_pathway(
            "Spatial legibility affects wayfinding comprehension",
            return_details=True
        )

        assert isinstance(result, PathwayClassification)
        assert result.pathway == "personal_epistemic"
        assert result.epistemic_score > 0
        assert result.confidence > 0

    def test_default_to_mixed_when_uncertain(self):
        """Defaults to mixed when no clear indicators."""
        from src.epistemic.extraction.pathway_classifier import classify_pathway

        result = classify_pathway("Some generic claim about buildings")
        assert result == "mixed"


class TestTask44PEClassification:
    """Task 4.4: Classify PE subtype."""

    def test_can_import_pe_module(self):
        """Module imports successfully."""
        from src.epistemic.extraction.pe_classifier import (
            classify_pe_subtype,
            PEClassification,
            FUNCTIONAL_PE_KEYWORDS,
            NAVIGATIONAL_PE_KEYWORDS,
            SOCIAL_PE_KEYWORDS,
        )
        assert classify_pe_subtype is not None
        assert len(FUNCTIONAL_PE_KEYWORDS) > 0

    def test_classify_navigational_pe(self):
        """Correctly classifies navigational PE."""
        from src.epistemic.extraction.pe_classifier import classify_pe_subtype

        result = classify_pe_subtype("wayfinding mismatch causes disorientation")
        assert result == "navigational_pe"

    def test_classify_functional_pe(self):
        """Correctly classifies functional PE."""
        from src.epistemic.extraction.pe_classifier import classify_pe_subtype

        result = classify_pe_subtype("affordance prediction error in hospital design")
        assert result == "functional_pe"

    def test_classify_social_pe(self):
        """Correctly classifies social PE."""
        from src.epistemic.extraction.pe_classifier import classify_pe_subtype

        result = classify_pe_subtype(
            "expectation violation regarding social norms and appropriate behavior"
        )
        assert result == "social_pe"

    def test_non_pe_claim_returns_none(self):
        """Non-PE claims return None."""
        from src.epistemic.extraction.pe_classifier import classify_pe_subtype

        result = classify_pe_subtype("cortisol levels increased")
        assert result is None

    def test_return_details_option(self):
        """Can return detailed classification."""
        from src.epistemic.extraction.pe_classifier import (
            classify_pe_subtype,
            PEClassification,
        )

        result = classify_pe_subtype(
            "wayfinding mismatch causes disorientation",
            return_details=True
        )

        assert isinstance(result, PEClassification)
        assert result.pe_subtype == "navigational_pe"
        assert result.is_pe_claim is True
        assert result.navigational_score > 0

    def test_non_pe_with_details(self):
        """Non-PE claims return PEClassification with None subtype."""
        from src.epistemic.extraction.pe_classifier import (
            classify_pe_subtype,
            PEClassification,
        )

        result = classify_pe_subtype("cortisol levels increased", return_details=True)

        assert isinstance(result, PEClassification)
        assert result.pe_subtype is None
        assert result.is_pe_claim is False


class TestExtractionModuleIntegration:
    """Test all extraction modules work together."""

    def test_all_modules_importable_from_package(self):
        """All modules accessible from main package."""
        from src.epistemic.extraction import (
            ArgumentativeMetadata,
            extract_argumentative_structure,
            SourceQualityMetadata,
            extract_source_quality_metadata,
            classify_pathway,
            classify_pe_subtype,
        )

        assert ArgumentativeMetadata is not None
        assert extract_argumentative_structure is not None
        assert SourceQualityMetadata is not None
        assert extract_source_quality_metadata is not None
        assert classify_pathway is not None
        assert classify_pe_subtype is not None

    def test_full_extraction_workflow(self):
        """Test extracting all metadata from a sample paper excerpt."""
        from src.epistemic.extraction import (
            extract_argumentative_structure,
            extract_source_quality_metadata,
            classify_pathway,
            classify_pe_subtype,
        )

        # Sample paper excerpt with clear theory references
        paper_text = """
        This randomized controlled trial with N=150 participants examined
        how wayfinding legibility affects spatial navigation and stress.

        Our findings support kaplan's attention restoration theory,
        suggesting that legible environments reduce cognitive load during
        navigation tasks. These results challenge ulrich's stress recovery theory
        which suggests all stress reduction is mediated by autonomic pathways.

        This study was pre-registered on OSF prior to data collection.
        """

        claim = "wayfinding legibility mismatch increases navigational stress"

        # Extract argumentative structure
        arg_meta = extract_argumentative_structure(paper_text)
        assert arg_meta.argument_for is not None  # Supports ART
        assert "attention restoration" in arg_meta.argument_for.lower()

        # Extract source quality metadata
        sq_meta = extract_source_quality_metadata(paper_text)
        assert sq_meta.sample_size == 150
        assert sq_meta.pre_registered is True

        # Classify pathway
        pathway = classify_pathway(claim)
        assert pathway in ["personal_epistemic", "mixed"]

        # Classify PE subtype
        pe_subtype = classify_pe_subtype(claim)
        assert pe_subtype == "navigational_pe"
