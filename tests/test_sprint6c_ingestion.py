"""
Tests for Sprint 6c: Ingestion Pipeline.

Tests the three ingestion modules:
- Task 6c.1: paper_classifier.py
- Task 6c.2: theoretical_extractor.py
- Task 6c.3: synthesis_ingester.py
"""

import pytest

# Task 6c.1: Paper Classifier
from src.epistemic.extraction.paper_classifier import (
    TemplateFamily,
    ClassificationSignals,
    PaperClassifier,
    classify_paper,
    get_node_types_for_template,
    can_produce_node_type,
    is_empirical_template,
    is_synthesis_template,
    TEMPLATE_NODE_TYPES,
)

# Task 6c.2: Theoretical Extractor
from src.epistemic.extraction.theoretical_extractor import (
    TheoreticalExtractor,
    ExtractedProposition,
    ExtractedHypothesis,
    ExtractedDefinition,
    extract_theoretical_paper,
    compute_proposition_entrenchment,
)

# Task 6c.3: Synthesis Ingester
from src.epistemic.extraction.synthesis_ingester import (
    SynthesisIngester,
    SynthesisType,
    EvidenceDirection,
    SynthesisConclusion,
    ExpertSynthesis,
    KnowledgeGap,
    PooledEffect,
    ingest_synthesis_paper,
    compute_synthesis_vs_primary_weight,
)

from src.epistemic.node_types import NodeType


# =============================================================================
# Task 6c.1: Paper Classifier Tests
# =============================================================================

class TestPaperClassifier:
    """Test paper classification."""

    def test_classify_meta_analysis_by_title(self):
        """Meta-analysis detected from title."""
        result = classify_paper(
            title="A meta-analysis of biophilic design effects on stress",
            abstract="This quantitative synthesis pooled 45 studies..."
        )
        assert result.template_family == TemplateFamily.META_ANALYSIS
        assert result.is_synthesis

    def test_classify_systematic_review_by_title(self):
        """Systematic review detected from title."""
        result = classify_paper(
            title="Effects of natural light on productivity: A systematic review",
            abstract="Following PRISMA guidelines, we systematically searched..."
        )
        assert result.template_family == TemplateFamily.SYSTEMATIC_REVIEW
        assert result.is_synthesis

    def test_classify_theoretical_paper(self):
        """Theoretical paper detected from title."""
        result = classify_paper(
            title="Toward a theory of restorative environments",
            abstract="We propose a mechanistic account of how natural settings..."
        )
        assert result.template_family == TemplateFamily.THEORETICAL
        assert result.is_theoretical

    def test_classify_empirical_from_sections(self):
        """Empirical paper detected from section structure."""
        result = classify_paper(
            title="Effects of ceiling height on creativity",
            abstract="We conducted an experiment...",
            section_headings=["Introduction", "Methods", "Participants", "Procedure", "Results", "Discussion"]
        )
        assert result.template_family == TemplateFamily.EMPIRICAL_V2
        assert result.is_empirical

    def test_review_of_experiments_not_forced_to_empirical(self):
        """A review paper mentioning experiments should stay review-family."""
        result = classify_paper(
            title="A review of experiments on biophilic design in workplaces",
            abstract="This review synthesizes experiments and applications across offices."
        )
        assert result.template_family in {
            TemplateFamily.NARRATIVE_REVIEW,
            TemplateFamily.SYSTEMATIC_REVIEW,
        }

    def test_trial_substring_in_industrial_not_empirical(self):
        """Substring hits like 'industrial' must not trigger trial-based empirical classification."""
        result = classify_paper(
            title="Sources and effects of low-frequency noise",
            abstract="We review road traffic, aircraft, and industrial machinery noise.",
        )
        assert result.template_family != TemplateFamily.EMPIRICAL_V2

    def test_empirical_with_theory_mentions_not_misclassified(self):
        """Empirical abstract mentioning theory should remain empirical when methods/results are present."""
        result = classify_paper(
            title="Effects of virtual environments on cognition",
            abstract=(
                "We conducted a randomized experiment with 120 participants. "
                "Methods and results are reported with p < 0.05 and effect sizes. "
                "Findings are interpreted using cognitive load theory."
            ),
        )
        assert result.template_family == TemplateFamily.EMPIRICAL_V2

    def test_template_node_types_mapping(self):
        """Each template family has defined node types."""
        for family in TemplateFamily:
            if family != TemplateFamily.UNKNOWN:
                node_types = get_node_types_for_template(family)
                assert len(node_types) > 0, f"{family} should produce at least one node type"

    def test_meta_analysis_produces_synthesis_conclusion(self):
        """Meta-analysis can produce SYNTHESIS_CONCLUSION."""
        assert can_produce_node_type(TemplateFamily.META_ANALYSIS, NodeType.SYNTHESIS_CONCLUSION)
        assert can_produce_node_type(TemplateFamily.META_ANALYSIS, NodeType.KNOWLEDGE_GAP)

    def test_theoretical_produces_propositions(self):
        """Theoretical papers can produce propositions and hypotheses."""
        assert can_produce_node_type(TemplateFamily.THEORETICAL, NodeType.THEORETICAL_PROPOSITION)
        assert can_produce_node_type(TemplateFamily.THEORETICAL, NodeType.DERIVED_HYPOTHESIS)

    def test_is_empirical_template(self):
        """is_empirical_template correctly identifies empirical templates."""
        assert is_empirical_template(TemplateFamily.EMPIRICAL_V2)
        assert is_empirical_template(TemplateFamily.CASE_STUDY)
        assert not is_empirical_template(TemplateFamily.META_ANALYSIS)

    def test_is_synthesis_template(self):
        """is_synthesis_template correctly identifies synthesis templates."""
        assert is_synthesis_template(TemplateFamily.META_ANALYSIS)
        assert is_synthesis_template(TemplateFamily.SYSTEMATIC_REVIEW)
        assert not is_synthesis_template(TemplateFamily.THEORETICAL)


# =============================================================================
# Task 6c.2: Theoretical Extractor Tests
# =============================================================================

class TestTheoreticalExtractor:
    """Test theoretical paper extraction."""

    def test_extract_central_proposition(self):
        """Central thesis is extracted as proposition."""
        template = {
            "thesis": {"main_claim": "Attention restoration occurs via soft fascination"}
        }
        result = extract_theoretical_paper("kaplan_1995", "ART Paper", template)
        assert len(result.propositions) == 1
        assert result.propositions[0].is_central
        assert "Attention restoration" in result.propositions[0].proposition_text

    def test_extract_derived_hypotheses(self):
        """Derived hypotheses are linked to parent proposition."""
        template = {
            "thesis": {"main_claim": "Soft fascination restores directed attention"},
            "framework": {
                "derived_hypotheses": [
                    {"hypothesis_text": "Natural environments should improve ANT scores", "testable_via": "ANT task"},
                    {"hypothesis_text": "Restoration effect increases with exposure duration"}
                ]
            }
        }
        result = extract_theoretical_paper("test_001", "Test Paper", template)
        assert len(result.hypotheses) == 2
        assert result.hypotheses[0].derived_from_proposition_id.endswith("_prop_central")
        assert result.hypotheses[0].testable_via == "ANT task"

    def test_extract_new_definitions(self):
        """New term definitions are extracted."""
        template = {
            "thesis": {"main_claim": "Test proposition"},
            "foundation": {
                "key_concepts": [
                    {"term": "soft fascination", "definition": "Effortless attention to natural stimuli", "source": "new"},
                    {"term": "directed attention", "definition": "Voluntary, effortful focus", "source": "existing"}
                ]
            }
        }
        result = extract_theoretical_paper("test_001", "Test Paper", template)
        # Only new terms should be extracted as definitions
        assert len(result.definitions) == 1
        assert result.definitions[0].term_name == "soft fascination"

    def test_extraction_to_claims(self):
        """Extraction result converts to ClaimV2 objects."""
        template = {
            "thesis": {"main_claim": "Test proposition"},
            "framework": {
                "derived_hypotheses": [{"hypothesis_text": "Test hypothesis"}]
            }
        }
        result = extract_theoretical_paper("test_001", "Test Paper", template)
        claims = result.to_claims()
        assert len(claims) == 2  # 1 proposition + 1 hypothesis
        assert all(c.paper_id == "test_001" for c in claims)

    def test_extraction_to_edges(self):
        """Extraction result generates appropriate edges."""
        template = {
            "thesis": {"main_claim": "Test proposition"},
            "framework": {
                "derived_hypotheses": [{"hypothesis_text": "Test hypothesis"}]
            }
        }
        result = extract_theoretical_paper("test_001", "Test Paper", template)
        edges = result.to_edges()
        # Should have THEORETICALLY_PREDICTS edge (edge_type is now a string)
        assert any(e.edge_type == "theoretically_predicts" for e in edges)

    def test_compute_proposition_entrenchment_best_case(self):
        """Best case entrenchment computation."""
        ent = compute_proposition_entrenchment("valid_supported", "strong", "clear")
        assert ent == pytest.approx(0.65)  # 0.35 + 0.15 + 0.10 + 0.05

    def test_compute_proposition_entrenchment_worst_case(self):
        """Worst case entrenchment computation."""
        ent = compute_proposition_entrenchment("gaps", "weak", "difficult")
        assert ent == pytest.approx(0.20)  # 0.35 - 0.10 - 0.05


# =============================================================================
# Task 6c.3: Synthesis Ingester Tests
# =============================================================================

class TestSynthesisIngester:
    """Test synthesis paper ingestion."""

    def test_ingest_meta_analysis(self):
        """Meta-analysis is properly ingested."""
        template = {
            "overall_effect": {
                "effect_size": 0.45,
                "metric": "d",
                "CI": [0.25, 0.65],
                "N_studies": 15,
                "heterogeneity_I2": 35.0,
                "publication_bias": "none",
                "conclusion": "Biophilic design reduces stress (d=0.45)"
            },
            "included_studies": ["study_1", "study_2", "study_3"],
            "gaps": ["No long-term studies"]
        }
        result = ingest_synthesis_paper("meta_001", "Meta Test", SynthesisType.META_ANALYSIS, template)

        assert result.synthesis_type == SynthesisType.META_ANALYSIS
        assert len(result.conclusions) == 1
        assert result.conclusions[0].pooled_effect is not None
        assert result.conclusions[0].pooled_effect.effect_size == pytest.approx(0.45)
        assert len(result.knowledge_gaps) == 1

    def test_ingest_systematic_review(self):
        """Systematic review is properly ingested."""
        template = {
            "themes": [
                {"synthesis": "Natural light improves mood", "evidence_direction": "positive", "n_studies": 8},
                {"synthesis": "Effects on productivity are mixed", "evidence_direction": "mixed", "n_studies": 5}
            ],
            "gaps": [{"gap": "Need more field studies"}],
            "quality_issues": [{"problem": "Many studies lack control groups", "method": "pre-post design"}]
        }
        result = ingest_synthesis_paper("sr_001", "SR Test", SynthesisType.SYSTEMATIC_REVIEW, template)

        assert result.synthesis_type == SynthesisType.SYSTEMATIC_REVIEW
        assert len(result.conclusions) == 2
        assert result.conclusions[0].evidence_direction == EvidenceDirection.POSITIVE
        assert result.conclusions[1].evidence_direction == EvidenceDirection.MIXED
        assert len(result.knowledge_gaps) == 1
        assert len(result.critiques) == 1

    def test_ingest_narrative_review(self):
        """Narrative review is properly ingested."""
        template = {
            "author": {
                "expertise_domain": "established",
                "stated_perspective": "biophilia perspective"
            },
            "themes": [
                {
                    "author_synthesis": "Nature reduces stress through multiple pathways",
                    "key_studies": [{"citation": "ulrich_1984"}, {"citation": "kaplan_1995"}]
                }
            ],
            "conclusions": {
                "summary_statements": ["Biophilic design should be standard practice"],
                "gaps": [{"gap": "Mechanism studies needed"}]
            }
        }
        result = ingest_synthesis_paper("nr_001", "NR Test", SynthesisType.NARRATIVE_REVIEW, template)

        assert result.synthesis_type == SynthesisType.NARRATIVE_REVIEW
        assert len(result.expert_syntheses) == 2  # 1 theme + 1 conclusion
        assert result.expert_syntheses[0].author_expertise == "established"
        assert len(result.expert_syntheses[0].attributed_findings) == 2
        assert len(result.knowledge_gaps) == 1

    def test_synthesis_conclusion_entrenchment(self):
        """Synthesis conclusion computes entrenchment correctly."""
        pooled = PooledEffect(
            effect_id="test",
            effect_description="Test effect",
            effect_size=0.5,
            effect_size_metric="d",
            confidence_interval=(0.3, 0.7),
            n_studies=10,
            heterogeneity_i2=30.0,
            publication_bias="none",
            grade_quality="high"
        )
        conclusion = SynthesisConclusion(
            conclusion_id="test_conc",
            conclusion_text="Test conclusion",
            evidence_direction=EvidenceDirection.POSITIVE,
            n_included_studies=10,
            pooled_effect=pooled,
        )
        ent = conclusion.compute_entrenchment()
        # Base 0.75 + quality_bonus 0.05 = 0.80
        assert ent == pytest.approx(0.80)

    def test_synthesis_to_edges(self):
        """Synthesis result generates INCLUDES_IN_SYNTHESIS edges."""
        template = {
            "overall_effect": {
                "effect_size": 0.4,
                "N_studies": 3,
                "conclusion": "Effect exists"
            },
            "included_studies": ["s1", "s2", "s3"]
        }
        result = ingest_synthesis_paper("meta_001", "Test", SynthesisType.META_ANALYSIS, template)
        edges = result.to_edges()

        # Should have 3 INCLUDES_IN_SYNTHESIS edges (edge_type is now a string)
        include_edges = [e for e in edges if e.edge_type == "includes_in_synthesis"]
        assert len(include_edges) == 3

    def test_compute_synthesis_vs_primary_weight(self):
        """Synthesis vs primary weight computation."""
        # Large, homogeneous meta-analysis should beat primary study
        weight = compute_synthesis_vs_primary_weight(
            synthesis_n_studies=20,
            synthesis_heterogeneity=30.0,
            primary_study_quality=0.6
        )
        assert weight > 1.0  # Trust synthesis

        # Small, heterogeneous meta-analysis vs high-quality primary
        weight = compute_synthesis_vs_primary_weight(
            synthesis_n_studies=3,
            synthesis_heterogeneity=80.0,
            primary_study_quality=0.9
        )
        assert weight < 1.0  # Trust primary


class TestEvidenceDirection:
    """Test evidence direction classification."""

    def test_positive_from_effect_size(self):
        """Positive effect size classifies as positive."""
        ingester = SynthesisIngester()
        direction = ingester._classify_direction(0.5)
        assert direction == EvidenceDirection.POSITIVE

    def test_negative_from_effect_size(self):
        """Negative effect size classifies as negative."""
        ingester = SynthesisIngester()
        direction = ingester._classify_direction(-0.5)
        assert direction == EvidenceDirection.NEGATIVE

    def test_null_from_small_effect_size(self):
        """Near-zero effect size classifies as null."""
        ingester = SynthesisIngester()
        direction = ingester._classify_direction(0.1)
        assert direction == EvidenceDirection.NULL
