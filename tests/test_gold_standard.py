"""
Tests for Sprint 9: Gold Standard Corpus and Validation.

This module tests:
1. Annotation loading from YAML
2. Corpus management
3. Extraction comparison
4. Aggregate validation metrics

Per expert panel consensus: Progressive validation as corpus grows.
"""

import pytest
import tempfile
from pathlib import Path

from src.services.gold_standard import (
    ExpectedBelief,
    ExpectedConstraint,
    NegativeTest,
    PaperAnnotation,
    CorpusManifest,
    GoldStandardCorpus,
    BeliefMatch,
    ComparisonResult,
    ExtractionComparator,
    validate_against_corpus,
)

from src.services.web_of_belief import (
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    CausalDirection,
    ScopeConditions,
)


class TestExpectedBelief:
    """Test Case 1: ExpectedBelief parsing."""

    def test_from_dict_basic(self):
        """Verify basic belief parsing."""
        data = {
            'id': 'test_b1',
            'content': 'Nature exposure improves mood',
            'expected_credence': [0.6, 0.8],
            'epistemic_level': 'empirical'
        }

        belief = ExpectedBelief.from_dict(data)

        assert belief.id == 'test_b1'
        assert belief.content == 'Nature exposure improves mood'
        assert belief.expected_credence_min == 0.6
        assert belief.expected_credence_max == 0.8
        assert belief.epistemic_level == EpistemicLevel.EMPIRICAL

    def test_from_dict_with_theory(self):
        """Verify belief with theory association."""
        data = {
            'id': 'test_b2',
            'content': 'Directed attention is fatigable',
            'expected_credence': [0.5, 0.7],
            'epistemic_level': 'theoretical',
            'theory': 'ART'
        }

        belief = ExpectedBelief.from_dict(data)

        assert belief.theory == 'ART'
        assert belief.epistemic_level == EpistemicLevel.THEORETICAL

    def test_from_dict_with_causal_direction(self):
        """Verify causal direction parsing."""
        data = {
            'id': 'test_b3',
            'content': 'Plants cause wellbeing improvement',
            'expected_credence': [0.6, 0.8],
            'epistemic_level': 'empirical',
            'causal_direction': 'forward'
        }

        belief = ExpectedBelief.from_dict(data)

        assert belief.causal_direction == CausalDirection.FORWARD

    def test_from_dict_with_scope(self):
        """Verify scope conditions parsing."""
        data = {
            'id': 'test_b4',
            'content': 'Effect found in adults',
            'expected_credence': [0.5, 0.7],
            'epistemic_level': 'empirical',
            'scope': {
                'population': 'adults',
                'setting': 'lab',
                'scope_specified': True
            }
        }

        belief = ExpectedBelief.from_dict(data)

        assert belief.scope is not None
        assert belief.scope.population == 'adults'
        assert belief.scope.setting == 'lab'
        assert belief.scope.scope_specified is True

    def test_from_dict_with_annotation_metadata(self):
        """Verify annotation metadata parsing."""
        data = {
            'id': 'test_b5',
            'content': 'Core theoretical claim',
            'expected_credence': [0.6, 0.8],
            'epistemic_level': 'theoretical',
            'annotation_metadata': {
                'confidence': 'high',
                'basis': 'Widely cited in literature'
            }
        }

        belief = ExpectedBelief.from_dict(data)

        assert belief.confidence == 'high'
        assert belief.basis == 'Widely cited in literature'


class TestExpectedConstraint:
    """Test Case 2: ExpectedConstraint parsing."""

    def test_from_dict_basic(self):
        """Verify basic constraint parsing."""
        data = {
            'source': 'b1',
            'target': 'b2',
            'type': 'supports',
            'expected_strength': [0.5, 0.7]
        }

        constraint = ExpectedConstraint.from_dict(data)

        assert constraint.source == 'b1'
        assert constraint.target == 'b2'
        assert constraint.constraint_type == 'supports'
        assert constraint.expected_strength_min == 0.5
        assert constraint.expected_strength_max == 0.7

    def test_from_dict_with_causal_direction(self):
        """Verify causal direction in constraints."""
        data = {
            'source': 'b1',
            'target': 'b2',
            'type': 'supports',
            'causal_direction': 'forward'
        }

        constraint = ExpectedConstraint.from_dict(data)

        assert constraint.causal_direction == CausalDirection.FORWARD


class TestPaperAnnotation:
    """Test Case 3: Paper annotation loading."""

    def test_from_yaml_basic(self, tmp_path):
        """Verify basic YAML loading."""
        yaml_content = """
paper_id: test_paper_2026
citation: "Test Author (2026). Test Paper."
version: "1.0"

metadata:
  annotator: "test_annotator"
  annotation_date: "2026-01-19"
  review_status: "approved"

paper_characteristics:
  type: "empirical"
  theories: ["ART"]
  is_multi_theory: false
  ecological_validity: "field_natural"

expected_beliefs:
  - id: "test_b1"
    content: "Nature improves mood"
    expected_credence: [0.6, 0.8]
    epistemic_level: "empirical"

expected_constraints: []
should_NOT_extract: []
red_flags: []
"""
        yaml_path = tmp_path / "test_paper.yaml"
        yaml_path.write_text(yaml_content)

        annotation = PaperAnnotation.from_yaml(yaml_path)

        assert annotation.paper_id == "test_paper_2026"
        assert annotation.annotator == "test_annotator"
        assert annotation.review_status == "approved"
        assert annotation.paper_type == "empirical"
        assert "ART" in annotation.theories
        assert len(annotation.expected_beliefs) == 1
        assert annotation.expected_beliefs[0].content == "Nature improves mood"

    def test_from_yaml_with_negative_tests(self, tmp_path):
        """Verify negative test loading."""
        yaml_content = """
paper_id: test_paper_2026
citation: "Test (2026)"
version: "1.0"

metadata:
  annotator: "test"
  annotation_date: "2026-01-19"
  review_status: "draft"

paper_characteristics:
  type: "theory"
  theories: ["ART"]

expected_beliefs:
  - id: "b1"
    content: "Test belief"
    expected_credence: [0.5, 0.7]
    epistemic_level: "theoretical"

should_NOT_extract:
  - pattern: "proves ART"
    reason: "Overstates certainty"
  - pattern: "credence > 0.85"
    reason: "Too confident for theoretical claims"

red_flags:
  - "Effect sizes in theoretical paper"
  - "Claims about specific populations"
"""
        yaml_path = tmp_path / "test_negative.yaml"
        yaml_path.write_text(yaml_content)

        annotation = PaperAnnotation.from_yaml(yaml_path)

        assert len(annotation.should_not_extract) == 2
        assert annotation.should_not_extract[0].pattern == "proves ART"
        assert annotation.should_not_extract[0].reason == "Overstates certainty"
        assert len(annotation.red_flags) == 2


class TestGoldStandardCorpus:
    """Test Case 4: Corpus management."""

    def test_load_corpus(self, tmp_path):
        """Verify corpus loading from directory."""
        # Create manifest
        manifest_content = """
version: "1.0"
release_date: "2026-01-19"
status: "in_development"
annotators: ["test_annotator"]
papers:
  - id: "paper1"
    status: "annotated"
statistics:
  total_papers: 1
  annotated: 1
theory_coverage:
  ART: 1
"""
        (tmp_path / "manifest.yaml").write_text(manifest_content)

        # Create annotations directory
        annotations_dir = tmp_path / "annotations"
        annotations_dir.mkdir()

        # Create annotation
        annotation_content = """
paper_id: paper1
citation: "Author (2026)"
version: "1.0"

metadata:
  annotator: "test"
  annotation_date: "2026-01-19"
  review_status: "approved"

paper_characteristics:
  type: "empirical"
  theories: ["ART"]

expected_beliefs:
  - id: "b1"
    content: "Test belief"
    expected_credence: [0.5, 0.7]
    epistemic_level: "empirical"
"""
        (annotations_dir / "paper1.yaml").write_text(annotation_content)

        # Load corpus
        corpus = GoldStandardCorpus.load(str(tmp_path))

        assert corpus.manifest.version == "1.0"
        assert corpus.n_papers == 1
        assert "paper1" in corpus.annotations
        assert corpus.n_expected_beliefs == 1

    def test_get_papers_by_theory(self, tmp_path):
        """Verify filtering by theory."""
        (tmp_path / "manifest.yaml").write_text("version: '1.0'\npapers: []\nstatistics: {}\ntheory_coverage: {}")
        annotations_dir = tmp_path / "annotations"
        annotations_dir.mkdir()

        # ART paper
        (annotations_dir / "art_paper.yaml").write_text("""
paper_id: art_paper
citation: "ART (2026)"
version: "1.0"
metadata:
  annotator: test
  annotation_date: "2026-01-19"
  review_status: approved
paper_characteristics:
  type: empirical
  theories: ["ART"]
expected_beliefs:
  - id: b1
    content: Test
    expected_credence: [0.5, 0.7]
    epistemic_level: empirical
""")

        # SRT paper
        (annotations_dir / "srt_paper.yaml").write_text("""
paper_id: srt_paper
citation: "SRT (2026)"
version: "1.0"
metadata:
  annotator: test
  annotation_date: "2026-01-19"
  review_status: approved
paper_characteristics:
  type: empirical
  theories: ["SRT"]
expected_beliefs:
  - id: b1
    content: Test
    expected_credence: [0.5, 0.7]
    epistemic_level: empirical
""")

        corpus = GoldStandardCorpus.load(str(tmp_path))

        art_papers = corpus.get_papers_by_theory("ART")
        assert "art_paper" in art_papers
        assert "srt_paper" not in art_papers

        srt_papers = corpus.get_papers_by_theory("SRT")
        assert "srt_paper" in srt_papers


class TestExtractionComparator:
    """Test Case 5: Extraction comparison."""

    def test_content_similarity_exact(self):
        """Verify similarity for identical content."""
        comparator = ExtractionComparator()

        similarity = comparator._content_similarity(
            "Nature exposure improves mood",
            "Nature exposure improves mood"
        )

        assert similarity == 1.0

    def test_content_similarity_partial(self):
        """Verify similarity for partially matching content."""
        comparator = ExtractionComparator()

        similarity = comparator._content_similarity(
            "Nature exposure improves mood significantly",
            "Nature exposure improves wellbeing"
        )

        # Should have moderate similarity (shared: nature, exposure, improves)
        assert 0.4 < similarity < 0.9

    def test_content_similarity_no_match(self):
        """Verify low similarity for unrelated content."""
        comparator = ExtractionComparator()

        similarity = comparator._content_similarity(
            "Plants reduce stress",
            "Temperature affects productivity"
        )

        assert similarity < 0.3

    def test_compare_perfect_match(self, tmp_path):
        """Verify comparison with perfect extraction."""
        # Create annotation
        annotation = PaperAnnotation(
            paper_id="test",
            citation="Test",
            version="1.0",
            annotator="test",
            annotation_date="2026-01-19",
            review_status="approved",
            paper_type="empirical",
            theories=["ART"],
            is_multi_theory=False,
            ecological_validity="field_natural",
            methodology_score=None,
            expected_beliefs=[
                ExpectedBelief(
                    id="b1",
                    content="Nature exposure improves mood",
                    expected_credence_min=0.6,
                    expected_credence_max=0.8,
                    epistemic_level=EpistemicLevel.EMPIRICAL
                )
            ],
            expected_constraints=[],
            should_not_extract=[],
            red_flags=[]
        )

        # Create matching extraction
        extracted = [
            Belief(
                belief_id="ext_b1",
                content="Nature exposure improves mood",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.7, 0.15)
            )
        ]

        comparator = ExtractionComparator()
        result = comparator.compare(annotation, extracted)

        assert result.n_expected == 1
        assert result.n_extracted == 1
        assert result.n_matched == 1
        assert result.n_missed == 0
        assert result.n_spurious == 0
        assert result.credences_in_range == 1
        assert result.belief_recall == 1.0
        assert result.belief_precision == 1.0
        assert result.belief_f1 == 1.0

    def test_compare_credence_out_of_range(self, tmp_path):
        """Verify detection of credence outside expected range."""
        annotation = PaperAnnotation(
            paper_id="test",
            citation="Test",
            version="1.0",
            annotator="test",
            annotation_date="2026-01-19",
            review_status="approved",
            paper_type="empirical",
            theories=["ART"],
            is_multi_theory=False,
            ecological_validity="field_natural",
            methodology_score=None,
            expected_beliefs=[
                ExpectedBelief(
                    id="b1",
                    content="Nature improves mood",
                    expected_credence_min=0.6,
                    expected_credence_max=0.8,
                    epistemic_level=EpistemicLevel.EMPIRICAL
                )
            ],
            expected_constraints=[],
            should_not_extract=[],
            red_flags=[]
        )

        # Extraction with credence too high
        extracted = [
            Belief(
                belief_id="ext_b1",
                content="Nature improves mood",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.95, 0.05)  # Too high!
            )
        ]

        comparator = ExtractionComparator()
        result = comparator.compare(annotation, extracted)

        assert result.n_matched == 1
        assert result.credences_in_range == 0
        assert len(result.credence_errors) == 1
        assert result.credence_errors[0][3] == 0.95  # actual credence

    def test_compare_level_mismatch(self):
        """Verify detection of epistemic level mismatch."""
        annotation = PaperAnnotation(
            paper_id="test",
            citation="Test",
            version="1.0",
            annotator="test",
            annotation_date="2026-01-19",
            review_status="approved",
            paper_type="theory",
            theories=["ART"],
            is_multi_theory=False,
            ecological_validity=None,
            methodology_score=None,
            expected_beliefs=[
                ExpectedBelief(
                    id="b1",
                    content="Attention is fatigable",
                    expected_credence_min=0.5,
                    expected_credence_max=0.7,
                    epistemic_level=EpistemicLevel.THEORETICAL
                )
            ],
            expected_constraints=[],
            should_not_extract=[],
            red_flags=[]
        )

        # Extraction with wrong level
        extracted = [
            Belief(
                belief_id="ext_b1",
                content="Attention is fatigable",
                level=EpistemicLevel.EMPIRICAL,  # Wrong!
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.6, 0.2)
            )
        ]

        comparator = ExtractionComparator()
        result = comparator.compare(annotation, extracted)

        assert result.n_matched == 1
        assert result.levels_correct == 0
        assert len(result.level_errors) == 1

    def test_compare_negative_test_violation(self):
        """Verify detection of negative test violations."""
        annotation = PaperAnnotation(
            paper_id="test",
            citation="Test",
            version="1.0",
            annotator="test",
            annotation_date="2026-01-19",
            review_status="approved",
            paper_type="theory",
            theories=["ART"],
            is_multi_theory=False,
            ecological_validity=None,
            methodology_score=None,
            expected_beliefs=[],
            expected_constraints=[],
            should_not_extract=[
                NegativeTest(pattern="ART is proven", reason="Overstates certainty")
            ],
            red_flags=[]
        )

        # Extraction that violates negative test
        extracted = [
            Belief(
                belief_id="bad_b1",
                content="This study shows ART is proven correct",
                level=EpistemicLevel.THEORETICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.9, 0.1)
            )
        ]

        comparator = ExtractionComparator()
        result = comparator.compare(annotation, extracted)

        assert len(result.negative_violations) == 1
        assert "ART is proven" in result.negative_violations[0][0]


class TestValidateAgainstCorpus:
    """Test Case 6: Aggregate validation."""

    def test_validate_single_paper(self, tmp_path):
        """Verify validation of single paper extraction."""
        # Setup corpus
        (tmp_path / "manifest.yaml").write_text("version: '1.0'\npapers: []\nstatistics: {}\ntheory_coverage: {}")
        annotations_dir = tmp_path / "annotations"
        annotations_dir.mkdir()

        (annotations_dir / "test_paper.yaml").write_text("""
paper_id: test_paper
citation: "Test (2026)"
version: "1.0"
metadata:
  annotator: test
  annotation_date: "2026-01-19"
  review_status: approved
paper_characteristics:
  type: empirical
  theories: ["ART"]
expected_beliefs:
  - id: b1
    content: Nature improves mood
    expected_credence: [0.5, 0.8]
    epistemic_level: empirical
  - id: b2
    content: Plants reduce stress
    expected_credence: [0.5, 0.8]
    epistemic_level: empirical
""")

        corpus = GoldStandardCorpus.load(str(tmp_path))

        # Create extractions (matching one belief)
        extractions = {
            "test_paper": [
                Belief(
                    belief_id="ext_1",
                    content="Nature improves mood",
                    level=EpistemicLevel.EMPIRICAL,
                    status=BeliefStatus.TENTATIVE,
                    credence=Credence(0.65, 0.2)
                )
            ]
        }

        report = validate_against_corpus(corpus, extractions)

        assert report.belief_recall == 0.5  # 1 of 2 matched
        assert report.belief_precision == 1.0  # 1 of 1 correct
        assert report.corpus_version == "1.0"


class TestComparisonResultMetrics:
    """Test Case 7: ComparisonResult computed properties."""

    def test_recall_precision_f1(self):
        """Verify metric computations."""
        result = ComparisonResult(
            paper_id="test",
            n_expected=10,
            n_extracted=8,
            n_matched=6,
            n_missed=4,
            n_spurious=2,
            credences_in_range=5,
            credence_errors=[],
            levels_correct=6,
            level_errors=[],
            negative_violations=[]
        )

        assert result.belief_recall == 0.6  # 6/10
        assert result.belief_precision == 0.75  # 6/8
        assert abs(result.belief_f1 - 0.667) < 0.01  # 2*0.6*0.75/(0.6+0.75)

    def test_credence_accuracy(self):
        """Verify credence accuracy computation."""
        result = ComparisonResult(
            paper_id="test",
            n_expected=5,
            n_extracted=5,
            n_matched=5,
            n_missed=0,
            n_spurious=0,
            credences_in_range=4,
            credence_errors=[("b1", 0.6, 0.8, 0.5)],
            levels_correct=5,
            level_errors=[],
            negative_violations=[]
        )

        assert result.credence_accuracy == 0.8  # 4/5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
