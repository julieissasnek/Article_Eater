"""
Gold Standard Corpus Loader and Validator.

Sprint 9: Validation infrastructure for Article Eater Post-Quinean.
Per expert panel consensus: Progressive validation as corpus grows.

This module provides:
1. GoldStandardCorpus - Load and manage the Gold Standard corpus
2. AnnotationLoader - Parse YAML annotation files
3. ExtractionComparator - Compare extractions against Gold Standard
4. ValidationMetrics - Compute recall, precision, F1, credence calibration
"""

import yaml
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from src.services.web_of_belief import (
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ScopeConditions,
    CausalDirection,
)

from src.services.validation import (
    ValidationReport,
    ValidationPhase,
    PASS_THRESHOLDS,
    EcologicalValidity,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ANNOTATION DATA STRUCTURES
# =============================================================================

@dataclass
class ExpectedBelief:
    """A belief expected to be extracted from a paper."""
    id: str
    content: str
    expected_credence_min: float
    expected_credence_max: float
    epistemic_level: EpistemicLevel
    theory: Optional[str] = None
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    scope: Optional[ScopeConditions] = None
    confidence: str = "medium"  # annotator confidence
    basis: str = ""  # why we expect this

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExpectedBelief':
        credence_range = d.get('expected_credence', [0.4, 0.6])
        level_str = d.get('epistemic_level', 'empirical')

        # Map level string to enum
        level_map = {
            'theoretical': EpistemicLevel.THEORETICAL,
            'intermediate': EpistemicLevel.INTERMEDIATE,
            'empirical': EpistemicLevel.EMPIRICAL,
            'observational': EpistemicLevel.OBSERVATIONAL,
        }
        level = level_map.get(level_str, EpistemicLevel.EMPIRICAL)

        # Parse causal direction
        causal_str = d.get('causal_direction', 'unknown')
        try:
            causal_direction = CausalDirection(causal_str)
        except ValueError:
            causal_direction = CausalDirection.UNKNOWN

        # Parse scope
        scope = None
        if 'scope' in d and d['scope']:
            scope_data = d['scope']
            scope = ScopeConditions(
                population=scope_data.get('population'),
                setting=scope_data.get('setting'),
                duration=scope_data.get('duration'),
                measurement=scope_data.get('measurement'),
                geography=scope_data.get('geography'),
                scope_specified=scope_data.get('scope_specified', False)
            )

        # Parse annotation metadata
        meta = d.get('annotation_metadata', {})

        return cls(
            id=d['id'],
            content=d['content'],
            expected_credence_min=credence_range[0],
            expected_credence_max=credence_range[1],
            epistemic_level=level,
            theory=d.get('theory'),
            environment_id=d.get('environment_id'),
            outcome_id=d.get('outcome_id'),
            causal_direction=causal_direction,
            scope=scope,
            confidence=meta.get('confidence', 'medium'),
            basis=meta.get('basis', '')
        )


@dataclass
class ExpectedConstraint:
    """A constraint expected between beliefs."""
    source: str
    target: str
    constraint_type: str
    expected_strength_min: float = 0.3
    expected_strength_max: float = 0.7
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    confidence: str = "medium"
    basis: str = ""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExpectedConstraint':
        strength_range = d.get('expected_strength', [0.3, 0.7])

        causal_str = d.get('causal_direction', 'unknown')
        try:
            causal_direction = CausalDirection(causal_str)
        except ValueError:
            causal_direction = CausalDirection.UNKNOWN

        meta = d.get('annotation_metadata', {})

        return cls(
            source=d['source'],
            target=d['target'],
            constraint_type=d['type'],
            expected_strength_min=strength_range[0],
            expected_strength_max=strength_range[1],
            causal_direction=causal_direction,
            confidence=meta.get('confidence', 'medium'),
            basis=meta.get('basis', '')
        )


@dataclass
class NegativeTest:
    """A pattern that should NOT be extracted."""
    pattern: str
    reason: str


@dataclass
class PaperAnnotation:
    """Complete annotation for a single paper."""
    paper_id: str
    citation: str
    version: str
    annotator: str
    annotation_date: str
    review_status: str

    # Paper characteristics
    paper_type: str
    theories: List[str]
    is_multi_theory: bool
    ecological_validity: Optional[str]
    methodology_score: Optional[Tuple[float, float]]

    # Expected extractions
    expected_beliefs: List[ExpectedBelief]
    expected_constraints: List[ExpectedConstraint]

    # Negative tests
    should_not_extract: List[NegativeTest]
    red_flags: List[str]

    # Notes
    validation_notes: str = ""

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'PaperAnnotation':
        """Load annotation from YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        meta = data.get('metadata', {})
        chars = data.get('paper_characteristics', {})

        # Parse expected beliefs
        beliefs = [
            ExpectedBelief.from_dict(b)
            for b in data.get('expected_beliefs', [])
        ]

        # Parse expected constraints
        constraints = [
            ExpectedConstraint.from_dict(c)
            for c in data.get('expected_constraints', [])
        ]

        # Parse negative tests
        negative = [
            NegativeTest(pattern=n['pattern'], reason=n['reason'])
            for n in data.get('should_NOT_extract', [])
        ]

        # Parse methodology score
        meth_score = chars.get('methodology_score')
        if meth_score and len(meth_score) == 2:
            meth_score = (meth_score[0], meth_score[1])
        else:
            meth_score = None

        return cls(
            paper_id=data['paper_id'],
            citation=data['citation'],
            version=data['version'],
            annotator=meta.get('annotator', 'unknown'),
            annotation_date=meta.get('annotation_date', ''),
            review_status=meta.get('review_status', 'draft'),
            paper_type=chars.get('type', 'empirical'),
            theories=chars.get('theories', []),
            is_multi_theory=chars.get('is_multi_theory', False),
            ecological_validity=chars.get('ecological_validity'),
            methodology_score=meth_score,
            expected_beliefs=beliefs,
            expected_constraints=constraints,
            should_not_extract=negative,
            red_flags=data.get('red_flags', []),
            validation_notes=data.get('validation_notes', '')
        )


# =============================================================================
# CORPUS MANAGEMENT
# =============================================================================

@dataclass
class CorpusManifest:
    """Manifest for the Gold Standard corpus."""
    version: str
    release_date: str
    status: str
    annotators: List[str]
    papers: List[Dict[str, Any]]
    statistics: Dict[str, int]
    theory_coverage: Dict[str, int]
    notes: str = ""

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'CorpusManifest':
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            version=data.get('version', '0.0'),
            release_date=data.get('release_date', ''),
            status=data.get('status', 'unknown'),
            annotators=data.get('annotators', []),
            papers=data.get('papers', []),
            statistics=data.get('statistics', {}),
            theory_coverage=data.get('theory_coverage', {}),
            notes=data.get('notes', '')
        )


class GoldStandardCorpus:
    """
    Load and manage the Gold Standard corpus.

    Usage:
        corpus = GoldStandardCorpus.load("gold_standard/v1.0")
        annotation = corpus.get_annotation("kaplan_1989")
    """

    def __init__(self, corpus_path: Path):
        self.corpus_path = corpus_path
        self.manifest: Optional[CorpusManifest] = None
        self.annotations: Dict[str, PaperAnnotation] = {}
        self._loaded = False

    @classmethod
    def load(cls, path: str) -> 'GoldStandardCorpus':
        """Load corpus from directory."""
        corpus = cls(Path(path))
        corpus._load()
        return corpus

    def _load(self) -> None:
        """Load manifest and all annotations."""
        # Load manifest
        manifest_path = self.corpus_path / "manifest.yaml"
        if manifest_path.exists():
            self.manifest = CorpusManifest.from_yaml(manifest_path)
        else:
            logger.warning(f"No manifest found at {manifest_path}")
            self.manifest = CorpusManifest(
                version="0.0",
                release_date="",
                status="unknown",
                annotators=[],
                papers=[],
                statistics={},
                theory_coverage={}
            )

        # Load annotations
        annotations_dir = self.corpus_path / "annotations"
        if annotations_dir.exists():
            for yaml_file in annotations_dir.glob("*.yaml"):
                try:
                    annotation = PaperAnnotation.from_yaml(yaml_file)
                    self.annotations[annotation.paper_id] = annotation
                    logger.debug(f"Loaded annotation: {annotation.paper_id}")
                except Exception as e:
                    logger.error(f"Failed to load {yaml_file}: {e}")

        self._loaded = True
        logger.info(f"Loaded corpus v{self.manifest.version} with {len(self.annotations)} annotations")

    def get_annotation(self, paper_id: str) -> Optional[PaperAnnotation]:
        """Get annotation for a specific paper."""
        return self.annotations.get(paper_id)

    def get_annotated_paper_ids(self) -> List[str]:
        """Get list of papers with annotations."""
        return list(self.annotations.keys())

    def get_papers_by_theory(self, theory: str) -> List[str]:
        """Get papers that discuss a specific theory."""
        return [
            paper_id for paper_id, ann in self.annotations.items()
            if theory in ann.theories
        ]

    def get_papers_by_type(self, paper_type: str) -> List[str]:
        """Get papers of a specific type."""
        return [
            paper_id for paper_id, ann in self.annotations.items()
            if ann.paper_type == paper_type
        ]

    @property
    def n_papers(self) -> int:
        return len(self.annotations)

    @property
    def n_expected_beliefs(self) -> int:
        return sum(len(a.expected_beliefs) for a in self.annotations.values())

    @property
    def n_expected_constraints(self) -> int:
        return sum(len(a.expected_constraints) for a in self.annotations.values())


# =============================================================================
# EXTRACTION COMPARISON
# =============================================================================

@dataclass
class BeliefMatch:
    """Result of matching an extracted belief to Gold Standard."""
    extracted_belief: Belief
    expected_belief: Optional[ExpectedBelief]
    match_type: str  # "exact", "partial", "no_match"
    content_similarity: float
    credence_in_range: bool
    level_match: bool
    notes: List[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """Result of comparing extractions to Gold Standard."""
    paper_id: str

    # Belief metrics
    n_expected: int
    n_extracted: int
    n_matched: int
    n_missed: int  # Expected but not extracted
    n_spurious: int  # Extracted but not expected

    # Credence calibration
    credences_in_range: int
    credence_errors: List[Tuple[str, float, float, float]]  # (id, expected_min, expected_max, actual)

    # Level accuracy
    levels_correct: int
    level_errors: List[Tuple[str, str, str]]  # (id, expected, actual)

    # Negative test results
    negative_violations: List[Tuple[str, str]]  # (pattern, extracted_content)

    # Detailed matches
    matches: List[BeliefMatch] = field(default_factory=list)

    @property
    def belief_recall(self) -> float:
        return self.n_matched / self.n_expected if self.n_expected > 0 else 0.0

    @property
    def belief_precision(self) -> float:
        return self.n_matched / self.n_extracted if self.n_extracted > 0 else 0.0

    @property
    def belief_f1(self) -> float:
        if self.belief_recall + self.belief_precision == 0:
            return 0.0
        return 2 * (self.belief_recall * self.belief_precision) / (self.belief_recall + self.belief_precision)

    @property
    def credence_accuracy(self) -> float:
        return self.credences_in_range / self.n_matched if self.n_matched > 0 else 0.0

    @property
    def level_accuracy(self) -> float:
        return self.levels_correct / self.n_matched if self.n_matched > 0 else 0.0


class ExtractionComparator:
    """
    Compare extracted beliefs against Gold Standard annotations.

    Per expert panel: Use fuzzy matching for content, range checking for credence.
    """

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def compare(
        self,
        annotation: PaperAnnotation,
        extracted_beliefs: List[Belief]
    ) -> ComparisonResult:
        """
        Compare extracted beliefs against expected beliefs.

        Args:
            annotation: Gold Standard annotation for the paper
            extracted_beliefs: Beliefs extracted by the system

        Returns:
            ComparisonResult with detailed metrics
        """
        matches = []
        matched_expected: Set[str] = set()
        matched_extracted: Set[str] = set()

        credences_in_range = 0
        credence_errors = []
        levels_correct = 0
        level_errors = []

        # Match each extracted belief to expected beliefs
        for extracted in extracted_beliefs:
            best_match = None
            best_similarity = 0.0

            for expected in annotation.expected_beliefs:
                if expected.id in matched_expected:
                    continue

                similarity = self._content_similarity(extracted.content, expected.content)

                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = expected

            if best_match:
                # Found a match
                matched_expected.add(best_match.id)
                matched_extracted.add(extracted.belief_id)

                # Check credence
                credence_ok = (
                    best_match.expected_credence_min <= extracted.credence.value <= best_match.expected_credence_max
                )
                if credence_ok:
                    credences_in_range += 1
                else:
                    credence_errors.append((
                        best_match.id,
                        best_match.expected_credence_min,
                        best_match.expected_credence_max,
                        extracted.credence.value
                    ))

                # Check level
                level_ok = extracted.level == best_match.epistemic_level
                if level_ok:
                    levels_correct += 1
                else:
                    level_errors.append((
                        best_match.id,
                        best_match.epistemic_level.value,
                        extracted.level.value
                    ))

                match = BeliefMatch(
                    extracted_belief=extracted,
                    expected_belief=best_match,
                    match_type="exact" if best_similarity > 0.9 else "partial",
                    content_similarity=best_similarity,
                    credence_in_range=credence_ok,
                    level_match=level_ok
                )
            else:
                # No match - spurious extraction
                match = BeliefMatch(
                    extracted_belief=extracted,
                    expected_belief=None,
                    match_type="no_match",
                    content_similarity=0.0,
                    credence_in_range=False,
                    level_match=False,
                    notes=["Spurious extraction - not in Gold Standard"]
                )

            matches.append(match)

        # Check negative tests
        negative_violations = []
        for negative in annotation.should_not_extract:
            for extracted in extracted_beliefs:
                if self._matches_pattern(extracted.content, negative.pattern):
                    negative_violations.append((negative.pattern, extracted.content))

        return ComparisonResult(
            paper_id=annotation.paper_id,
            n_expected=len(annotation.expected_beliefs),
            n_extracted=len(extracted_beliefs),
            n_matched=len(matched_expected),
            n_missed=len(annotation.expected_beliefs) - len(matched_expected),
            n_spurious=len(extracted_beliefs) - len(matched_extracted),
            credences_in_range=credences_in_range,
            credence_errors=credence_errors,
            levels_correct=levels_correct,
            level_errors=level_errors,
            negative_violations=negative_violations,
            matches=matches
        )

    def _content_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two text strings.

        Uses simple word overlap for now. Could be enhanced with
        sentence embeddings or other NLP techniques.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        # Jaccard similarity
        jaccard = len(intersection) / len(union)

        # Bonus for key term matches
        key_terms = {"increase", "decrease", "improve", "reduce", "affect", "cause", "restore"}
        key_matches = sum(1 for t in key_terms if t in words1 and t in words2)
        key_bonus = key_matches * 0.1

        return min(1.0, jaccard + key_bonus)

    def _matches_pattern(self, content: str, pattern: str) -> bool:
        """Check if content matches a negative test pattern."""
        content_lower = content.lower()
        pattern_lower = pattern.lower()

        # Direct substring match
        if pattern_lower in content_lower:
            return True

        # Check for credence threshold pattern (e.g., "credence > 0.85")
        if "credence" in pattern_lower and ">" in pattern_lower:
            # This would need actual credence checking in real implementation
            pass

        return False


# =============================================================================
# AGGREGATE VALIDATION
# =============================================================================

def validate_against_corpus(
    corpus: GoldStandardCorpus,
    extractions: Dict[str, List[Belief]],
    comparator: Optional[ExtractionComparator] = None
) -> ValidationReport:
    """
    Validate extractions against the entire Gold Standard corpus.

    Args:
        corpus: The Gold Standard corpus
        extractions: Dict mapping paper_id to extracted beliefs
        comparator: Optional custom comparator

    Returns:
        ValidationReport with aggregate metrics
    """
    if comparator is None:
        comparator = ExtractionComparator()

    all_results = []
    f1_by_level = {"empirical": [], "intermediate": [], "theoretical": []}
    credence_by_level = {"empirical": [], "intermediate": [], "theoretical": []}

    total_expected = 0
    total_extracted = 0
    total_matched = 0
    total_credence_ok = 0
    total_violations = 0

    for paper_id, annotation in corpus.annotations.items():
        if paper_id not in extractions:
            logger.warning(f"No extractions for paper: {paper_id}")
            continue

        result = comparator.compare(annotation, extractions[paper_id])
        all_results.append(result)

        total_expected += result.n_expected
        total_extracted += result.n_extracted
        total_matched += result.n_matched
        total_credence_ok += result.credences_in_range
        total_violations += len(result.negative_violations)

        # Track by level
        for match in result.matches:
            if match.expected_belief:
                level = match.expected_belief.epistemic_level.value
                if level in f1_by_level:
                    f1_by_level[level].append(1.0 if match.match_type != "no_match" else 0.0)
                    if match.credence_in_range:
                        credence_by_level[level].append(1.0)
                    else:
                        credence_by_level[level].append(0.0)

    # Compute aggregate metrics
    recall = total_matched / total_expected if total_expected > 0 else 0.0
    precision = total_matched / total_extracted if total_extracted > 0 else 0.0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) > 0 else 0.0

    credence_in_range = total_credence_ok / total_matched if total_matched > 0 else 0.0

    # Compute per-level F1
    level_f1 = {}
    level_credence = {}
    for level, scores in f1_by_level.items():
        level_f1[level] = sum(scores) / len(scores) if scores else 0.0
    for level, scores in credence_by_level.items():
        level_credence[level] = sum(scores) / len(scores) if scores else 0.0

    return ValidationReport(
        belief_recall=recall,
        belief_precision=precision,
        belief_f1=f1,
        f1_by_level=level_f1,
        credence_mae=0.0,  # Would need detailed computation
        credence_in_range=credence_in_range,
        credence_by_level=level_credence,
        should_not_extract_violations=total_violations,
        corpus_version=corpus.manifest.version,
        statistical_power="sufficient" if corpus.n_papers >= 30 else "preliminary"
    )


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Data structures
    "ExpectedBelief",
    "ExpectedConstraint",
    "NegativeTest",
    "PaperAnnotation",
    "CorpusManifest",

    # Corpus management
    "GoldStandardCorpus",

    # Comparison
    "BeliefMatch",
    "ComparisonResult",
    "ExtractionComparator",

    # Validation
    "validate_against_corpus",
]
