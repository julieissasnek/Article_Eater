# Implementation Plan: TODO 1 — Credibility Testing

**Date:** January 20, 2026
**Phase:** B (Implementation Plan)
**Status:** Ready for critique
**Incorporates:** Expert Panel Review 2026-01-20

---

## 1. Executive Summary

This plan details the implementation of a credibility testing system that evaluates whether article additions to the Quinean web produce epistemically appropriate updates. The system implements tiered severity checks, maintains both Gold Standard and Failure Standard test corpora, and includes a feedback loop for continuous improvement.

**Core Design Principle (from Simon):** Optimize for high sensitivity (catching real problems) while accepting moderate false positive rates. Type II errors (missing problems) are more costly than Type I errors (false alarms).

---

## 2. Architecture Overview

```
                         ┌─────────────────────────┐
                         │   Article Extraction    │
                         │   (existing pipeline)   │
                         └───────────┬─────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │   Pre-Commit State      │
                         │   (extracted beliefs,   │
                         │    constraints, etc.)   │
                         └───────────┬─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
           │  Severity 1  │ │  Severity 2  │ │  Severity 3  │
           │   Checks     │ │   Checks     │ │   Checks     │
           │  (Critical)  │ │   (Major)    │ │   (Minor)    │
           └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                  │                │                │
                  └────────────────┼────────────────┘
                                   │
                                   ▼
                         ┌─────────────────────────┐
                         │   Credibility Report    │
                         │   - Severity level      │
                         │   - Specific flags      │
                         │   - Explanations        │
                         │   - Recommended action  │
                         └───────────┬─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │  AUTO-   │    │  FLAG    │    │  AUTO-   │
              │  ACCEPT  │    │  FOR     │    │  REJECT  │
              │          │    │  REVIEW  │    │          │
              └──────────┘    └────┬─────┘    └──────────┘
                                   │
                                   ▼
                         ┌─────────────────────────┐
                         │   Human Review Queue    │
                         │   (prioritized by       │
                         │    severity)            │
                         └───────────┬─────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │   Feedback Loop         │
                         │   (resolution tracking, │
                         │    threshold tuning)    │
                         └─────────────────────────┘
```

---

## 3. Data Structures

### 3.1 Credibility Report

```python
# Location: src/services/credibility_testing.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class Severity(Enum):
    """Flag severity levels (per Mayo)."""
    CRITICAL = 1    # Logical impossibilities, clear errors
    MAJOR = 2       # Strong anomalies likely indicating problems
    MINOR = 3       # Unusual patterns that might be fine

class FlagType(Enum):
    """Types of credibility flags."""
    # Severity 1 (Critical)
    INVALID_NUMERIC_VALUE = "invalid_numeric_value"
    SELF_CONTRADICTION = "self_contradiction"
    DUPLICATE_PAPER_ID = "duplicate_paper_id"
    PARSING_FAILURE = "parsing_failure"

    # Severity 2 (Major)
    CAUSAL_STATUS_MISMATCH = "causal_status_mismatch"
    EXCESSIVE_CREDENCE_CHANGE = "excessive_credence_change"
    SCOPE_OVERREACH = "scope_overreach"
    CAUSAL_CYCLE_CREATED = "causal_cycle_created"
    EFFECT_SIZE_IMPLAUSIBLE = "effect_size_implausible"

    # Severity 3 (Minor)
    SEMANTIC_MISMATCH = "semantic_mismatch"
    UNUSUAL_CONSTRAINT_PATTERN = "unusual_constraint_pattern"
    CREDENCE_CHANGE_ELEVATED = "credence_change_elevated"
    NEW_STUB_CREATED = "new_stub_created"

class RecommendedAction(Enum):
    """System recommendation for article."""
    AUTO_ACCEPT = "auto_accept"
    FLAG_FOR_REVIEW = "flag_for_review"
    AUTO_REJECT = "auto_reject"

@dataclass
class CredibilityFlag:
    """A single credibility concern."""
    flag_type: FlagType
    severity: Severity
    description: str
    details: Dict[str, Any]

    # For reviewer
    what_to_check: str
    expected_value: Optional[Any] = None
    observed_value: Optional[Any] = None

@dataclass
class CredibilityReport:
    """Complete credibility assessment for an article."""
    article_id: str
    timestamp: datetime

    # Flags by severity
    flags: List[CredibilityFlag] = field(default_factory=list)

    # Aggregate scores (0-1, higher = more credible)
    extraction_score: float = 1.0
    constraint_score: float = 1.0
    update_score: float = 1.0
    coherence_score: float = 1.0

    # Overall assessment
    overall_credibility: float = 1.0
    max_severity: Optional[Severity] = None
    recommended_action: RecommendedAction = RecommendedAction.AUTO_ACCEPT

    # For human review
    review_priority: int = 0  # Lower = higher priority
    estimated_review_time_minutes: int = 5

    def add_flag(self, flag: CredibilityFlag):
        self.flags.append(flag)
        if self.max_severity is None or flag.severity.value < self.max_severity.value:
            self.max_severity = flag.severity
        self._update_recommendation()

    def _update_recommendation(self):
        if self.max_severity == Severity.CRITICAL:
            self.recommended_action = RecommendedAction.AUTO_REJECT
            self.review_priority = 1
        elif self.max_severity == Severity.MAJOR:
            self.recommended_action = RecommendedAction.FLAG_FOR_REVIEW
            self.review_priority = 2
        elif self.max_severity == Severity.MINOR:
            self.recommended_action = RecommendedAction.FLAG_FOR_REVIEW
            self.review_priority = 3
        # No flags = auto-accept (default)
```

### 3.2 Baseline Statistics

```python
@dataclass
class BaselineStatistics:
    """Statistics from Gold Standard for comparison."""

    # Credence change distributions by evidence type
    credence_change_mean: Dict[str, float]  # e.g., {"empirical": 0.08, "theoretical": 0.05}
    credence_change_std: Dict[str, float]

    # Constraint semantic similarity
    constraint_similarity_mean: float
    constraint_similarity_std: float
    constraint_similarity_threshold: float  # e.g., 2σ below mean

    # Effect size ranges by study type
    effect_size_ranges: Dict[str, Tuple[float, float]]  # e.g., {"lab_experiment": (0.1, 1.2)}

    # Coherence change per article
    coherence_change_mean: float
    coherence_change_std: float

    # Belief type distributions by paper type
    belief_type_distributions: Dict[str, Dict[str, float]]

    @classmethod
    def compute_from_corpus(cls, corpus: List[ProcessedArticle]) -> 'BaselineStatistics':
        """Compute baseline statistics from Gold Standard corpus."""
        ...
```

### 3.3 Feedback Record

```python
@dataclass
class FlagResolution:
    """Record of how a flag was resolved."""
    flag_type: FlagType
    severity: Severity
    article_id: str
    timestamp: datetime

    # Resolution
    resolution: str  # "true_positive", "false_positive", "deferred"
    reviewer_notes: Optional[str] = None

    # If true positive, what was wrong?
    error_category: Optional[str] = None  # "extraction_error", "paper_error", "system_error"

    # If false positive, why was it flagged incorrectly?
    false_positive_reason: Optional[str] = None
```

---

## 4. Credibility Checks Specification

### 4.1 Severity 1 (Critical) Checks

These detect logical impossibilities. Auto-reject if any fail.

```python
class Severity1Checks:
    """Critical checks - logical impossibilities."""

    def check_numeric_validity(self, extracted: ExtractedData) -> List[CredibilityFlag]:
        """Verify all numeric values are in valid ranges."""
        flags = []

        # Sample size must be positive
        if extracted.sample_size is not None and extracted.sample_size <= 0:
            flags.append(CredibilityFlag(
                flag_type=FlagType.INVALID_NUMERIC_VALUE,
                severity=Severity.CRITICAL,
                description=f"Sample size is non-positive: {extracted.sample_size}",
                details={"field": "sample_size", "value": extracted.sample_size},
                what_to_check="Verify sample size in original paper",
                expected_value="> 0",
                observed_value=extracted.sample_size
            ))

        # P-value must be in [0, 1]
        if extracted.p_value is not None:
            if not (0 <= extracted.p_value <= 1):
                flags.append(CredibilityFlag(
                    flag_type=FlagType.INVALID_NUMERIC_VALUE,
                    severity=Severity.CRITICAL,
                    description=f"P-value outside [0,1]: {extracted.p_value}",
                    details={"field": "p_value", "value": extracted.p_value},
                    what_to_check="Verify p-value in original paper",
                    expected_value="[0, 1]",
                    observed_value=extracted.p_value
                ))

        # Credence must be in (0, 1)
        for belief in extracted.beliefs:
            if not (0 < belief.credence.value < 1):
                flags.append(CredibilityFlag(
                    flag_type=FlagType.INVALID_NUMERIC_VALUE,
                    severity=Severity.CRITICAL,
                    description=f"Credence outside (0,1): {belief.credence.value}",
                    details={"belief_id": belief.id, "value": belief.credence.value},
                    what_to_check="Review credence assignment logic",
                    expected_value="(0, 1)",
                    observed_value=belief.credence.value
                ))

        return flags

    def check_self_contradiction(self, extracted: ExtractedData) -> List[CredibilityFlag]:
        """Check for contradictions within the same paper."""
        flags = []

        # Check if paper contains beliefs that directly contradict each other
        for i, belief1 in enumerate(extracted.beliefs):
            for belief2 in extracted.beliefs[i+1:]:
                if self._beliefs_contradict(belief1, belief2):
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.SELF_CONTRADICTION,
                        severity=Severity.CRITICAL,
                        description=f"Paper contains contradictory beliefs",
                        details={
                            "belief1": belief1.content,
                            "belief2": belief2.content
                        },
                        what_to_check="Review paper for actual contradiction vs. extraction error"
                    ))

        return flags

    def check_duplicate_paper(self, article_id: str, existing_ids: Set[str]) -> List[CredibilityFlag]:
        """Check if paper ID already exists."""
        flags = []
        if article_id in existing_ids:
            flags.append(CredibilityFlag(
                flag_type=FlagType.DUPLICATE_PAPER_ID,
                severity=Severity.CRITICAL,
                description=f"Paper ID already exists: {article_id}",
                details={"article_id": article_id},
                what_to_check="Verify this isn't a duplicate submission"
            ))
        return flags
```

### 4.2 Severity 2 (Major) Checks

These detect likely problems. Flag for review.

```python
class Severity2Checks:
    """Major checks - likely problems."""

    def __init__(self, baseline: BaselineStatistics, web: WebOfBelief):
        self.baseline = baseline
        self.web = web

    def check_causal_status_mismatch(self, extracted: ExtractedData) -> List[CredibilityFlag]:
        """
        Verify causal claims match study design.
        Per Pearl: Correlational studies shouldn't yield causal constraints.
        """
        flags = []

        study_design = extracted.methodology.get("design")
        is_experimental = study_design in ["rct", "experiment", "quasi_experiment", "natural_experiment"]

        for constraint in extracted.constraints:
            if constraint.causal_direction in [CausalDirection.FORWARD, CausalDirection.REVERSE]:
                if not is_experimental:
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.CAUSAL_STATUS_MISMATCH,
                        severity=Severity.MAJOR,
                        description=f"Causal claim from non-experimental study",
                        details={
                            "constraint": str(constraint),
                            "study_design": study_design,
                            "causal_direction": constraint.causal_direction.value
                        },
                        what_to_check="Verify study design supports causal inference. "
                                     "If correlational, change to CORRELATIONAL direction.",
                        expected_value="CORRELATIONAL for observational studies",
                        observed_value=constraint.causal_direction.value
                    ))

        return flags

    def check_credence_change_magnitude(
        self,
        pre_state: WebState,
        post_state: WebState,
        extracted: ExtractedData
    ) -> List[CredibilityFlag]:
        """
        Check if credence changes are proportionate to evidence strength.
        Per panel: Flag changes > 2σ given prior uncertainty and evidence strength.
        """
        flags = []

        for belief_id in post_state.beliefs:
            if belief_id in pre_state.beliefs:
                pre_credence = pre_state.beliefs[belief_id].credence
                post_credence = post_state.beliefs[belief_id].credence

                change = abs(post_credence.value - pre_credence.value)

                # Compute expected change based on evidence strength
                evidence_strength = self._compute_evidence_strength(extracted)
                expected_change_std = self.baseline.credence_change_std.get(
                    extracted.paper_type, 0.1
                )

                # Threshold: 2σ, scaled by evidence strength
                threshold = 2 * expected_change_std * (1 + evidence_strength)

                if change > threshold:
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.EXCESSIVE_CREDENCE_CHANGE,
                        severity=Severity.MAJOR,
                        description=f"Credence change exceeds expected range",
                        details={
                            "belief_id": belief_id,
                            "pre_credence": pre_credence.value,
                            "post_credence": post_credence.value,
                            "change": change,
                            "threshold": threshold
                        },
                        what_to_check="Verify evidence strength justifies this change. "
                                     "Check for extraction errors or unusual paper.",
                        expected_value=f"< {threshold:.3f}",
                        observed_value=f"{change:.3f}"
                    ))

        return flags

    def check_scope_overreach(self, extracted: ExtractedData) -> List[CredibilityFlag]:
        """
        Check if scope conditions match paper's actual sample.
        Per Cartwright: Most common failure is treating specific findings as universal.
        """
        flags = []

        paper_sample = extracted.methodology.get("sample_description", "")

        for belief in extracted.beliefs:
            # Check for missing scope when sample is specific
            if belief.scope.scope_specified == False:
                # Check if paper mentions specific population
                specific_indicators = ["students", "undergraduates", "patients", "elderly",
                                       "children", "Western", "American", "Japanese"]
                if any(ind.lower() in paper_sample.lower() for ind in specific_indicators):
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.SCOPE_OVERREACH,
                        severity=Severity.MAJOR,
                        description=f"Scope not specified despite specific sample",
                        details={
                            "belief": belief.content,
                            "sample_description": paper_sample
                        },
                        what_to_check="Extract appropriate scope conditions from paper. "
                                     "Do not assume universal applicability.",
                        expected_value="scope_specified=True with appropriate conditions",
                        observed_value="scope_specified=False"
                    ))

            # Check for universal scope from limited sample
            if belief.scope.population is None and extracted.sample_size:
                if extracted.sample_size < 200:  # Small sample
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.SCOPE_OVERREACH,
                        severity=Severity.MAJOR,
                        description=f"No population scope from small sample (N={extracted.sample_size})",
                        details={
                            "belief": belief.content,
                            "sample_size": extracted.sample_size
                        },
                        what_to_check="Small samples rarely justify universal claims. "
                                     "Add appropriate population scope."
                    ))

        return flags

    def check_causal_cycles(
        self,
        pre_state: WebState,
        new_constraints: List[Constraint]
    ) -> List[CredibilityFlag]:
        """
        Check if new constraints create causal cycles.
        Per Pearl: Cycles aren't always wrong but should be reviewed.
        """
        flags = []

        # Build graph including new constraints
        graph = self._build_causal_graph(pre_state, new_constraints)
        cycles = self._find_cycles(graph)

        for cycle in cycles:
            flags.append(CredibilityFlag(
                flag_type=FlagType.CAUSAL_CYCLE_CREATED,
                severity=Severity.MAJOR,
                description=f"Causal cycle detected",
                details={"cycle": cycle},
                what_to_check="Verify if this represents bidirectional causation, "
                             "different timescales, or extraction error."
            ))

        return flags

    def check_effect_size_plausibility(self, extracted: ExtractedData) -> List[CredibilityFlag]:
        """
        Check if effect sizes are within plausible ranges.
        Per Kaplan: d > 1.5 for environmental manipulation is highly suspicious.
        """
        flags = []

        study_type = extracted.methodology.get("design", "unknown")
        expected_range = self.baseline.effect_size_ranges.get(study_type, (0, 2.0))

        for finding in extracted.findings:
            if finding.effect_size is not None:
                d = abs(finding.effect_size)
                if d > expected_range[1]:
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.EFFECT_SIZE_IMPLAUSIBLE,
                        severity=Severity.MAJOR,
                        description=f"Effect size unusually large: d={d:.2f}",
                        details={
                            "finding": finding.description,
                            "effect_size": d,
                            "study_type": study_type,
                            "expected_max": expected_range[1]
                        },
                        what_to_check="Verify effect size in original paper. "
                                     "Large effects in environmental psychology are rare."
                    ))

        return flags
```

### 4.3 Severity 3 (Minor) Checks

These detect unusual patterns. Flag for batched review.

```python
class Severity3Checks:
    """Minor checks - unusual patterns."""

    def __init__(self, baseline: BaselineStatistics, web: WebOfBelief):
        self.baseline = baseline
        self.web = web

    def check_semantic_coherence(self, new_constraints: List[Constraint]) -> List[CredibilityFlag]:
        """
        Check if constraints connect semantically related beliefs.
        Per Bates: Use taxonomy distance, co-citation, or embeddings.
        """
        flags = []

        for constraint in new_constraints:
            source_belief = self.web.beliefs.get(constraint.source_id)
            target_belief = self.web.beliefs.get(constraint.target_id)

            if source_belief and target_belief:
                similarity = self._compute_semantic_similarity(source_belief, target_belief)

                if similarity < self.baseline.constraint_similarity_threshold:
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.SEMANTIC_MISMATCH,
                        severity=Severity.MINOR,
                        description=f"Constraint connects semantically distant beliefs",
                        details={
                            "source": source_belief.content[:50],
                            "target": target_belief.content[:50],
                            "similarity": similarity,
                            "threshold": self.baseline.constraint_similarity_threshold
                        },
                        what_to_check="Verify these beliefs should be connected. "
                                     "May indicate extraction error or genuine novel connection."
                    ))

        return flags

    def _compute_semantic_similarity(self, belief1: Belief, belief2: Belief) -> float:
        """
        Compute semantic similarity using multiple methods.

        Methods (per Bates):
        1. Taxonomy distance (if both have environment_id or outcome_id)
        2. Keyword overlap
        3. Embedding similarity (if available)
        """
        scores = []

        # Taxonomy distance
        if belief1.environment_id and belief2.environment_id:
            tax_dist = taxonomy_distance(belief1.environment_id, belief2.environment_id)
            scores.append(1.0 / (1.0 + tax_dist))

        if belief1.outcome_id and belief2.outcome_id:
            tax_dist = taxonomy_distance(belief1.outcome_id, belief2.outcome_id)
            scores.append(1.0 / (1.0 + tax_dist))

        # Keyword overlap
        keywords1 = set(belief1.content.lower().split())
        keywords2 = set(belief2.content.lower().split())
        if keywords1 and keywords2:
            jaccard = len(keywords1 & keywords2) / len(keywords1 | keywords2)
            scores.append(jaccard)

        return sum(scores) / len(scores) if scores else 0.0

    def check_credence_change_elevated(
        self,
        pre_state: WebState,
        post_state: WebState
    ) -> List[CredibilityFlag]:
        """
        Check for elevated but not excessive credence changes.
        Softer version of Severity 2 check.
        """
        flags = []

        for belief_id in post_state.beliefs:
            if belief_id in pre_state.beliefs:
                pre = pre_state.beliefs[belief_id].credence.value
                post = post_state.beliefs[belief_id].credence.value
                change = abs(post - pre)

                # 1σ threshold (vs 2σ for Severity 2)
                threshold = self.baseline.credence_change_std.get("empirical", 0.1)

                if change > threshold and change <= 2 * threshold:
                    flags.append(CredibilityFlag(
                        flag_type=FlagType.CREDENCE_CHANGE_ELEVATED,
                        severity=Severity.MINOR,
                        description=f"Credence change elevated (within 1-2σ)",
                        details={
                            "belief_id": belief_id,
                            "change": change,
                            "threshold_1sigma": threshold
                        },
                        what_to_check="Review if change is appropriate. May be fine."
                    ))

        return flags

    def check_new_stubs(self, new_beliefs: List[Belief]) -> List[CredibilityFlag]:
        """
        Note when stubs are created (findings without theoretical home).
        """
        flags = []

        for belief in new_beliefs:
            if belief.status == BeliefStatus.STUB:
                flags.append(CredibilityFlag(
                    flag_type=FlagType.NEW_STUB_CREATED,
                    severity=Severity.MINOR,
                    description=f"New stub created (finding without theoretical home)",
                    details={"belief": belief.content},
                    what_to_check="Stub may indicate gap in taxonomy or novel finding. "
                                 "Not necessarily an error."
                ))

        return flags
```

---

## 5. Test Corpora

### 5.1 Gold Standard Corpus

Use existing `gold_standard/v1.0/` corpus for baseline calibration.

```python
# Location: src/services/credibility_testing.py

def calibrate_from_gold_standard(gold_standard_path: str) -> BaselineStatistics:
    """
    Process Gold Standard corpus to establish baseline statistics.

    Gold Standard contains papers with known-good extractions.
    Statistics from these become the reference distribution.
    """
    corpus = GoldStandardCorpus(gold_standard_path)

    credence_changes = defaultdict(list)
    constraint_similarities = []
    effect_sizes = defaultdict(list)
    coherence_changes = []

    for annotation in corpus.annotations:
        # Process each paper
        # Collect statistics on credence changes, similarities, etc.
        ...

    return BaselineStatistics(
        credence_change_mean={k: np.mean(v) for k, v in credence_changes.items()},
        credence_change_std={k: np.std(v) for k, v in credence_changes.items()},
        constraint_similarity_mean=np.mean(constraint_similarities),
        constraint_similarity_std=np.std(constraint_similarities),
        constraint_similarity_threshold=np.mean(constraint_similarities) - 2*np.std(constraint_similarities),
        effect_size_ranges={k: (np.percentile(v, 5), np.percentile(v, 95)) for k, v in effect_sizes.items()},
        coherence_change_mean=np.mean(coherence_changes),
        coherence_change_std=np.std(coherence_changes)
    )
```

### 5.2 Failure Standard Corpus (Per Mayo)

Create deliberately flawed inputs to test detection.

```yaml
# Location: gold_standard/failure_standard/manifest.yaml

version: "1.0"
purpose: "Adversarial test cases for credibility detection"

failure_cases:
  # Severity 1: Logical impossibilities
  - id: "fail_s1_negative_n"
    description: "Paper with negative sample size"
    expected_flag: "INVALID_NUMERIC_VALUE"
    expected_severity: 1

  - id: "fail_s1_p_over_1"
    description: "Paper with p-value > 1"
    expected_flag: "INVALID_NUMERIC_VALUE"
    expected_severity: 1

  - id: "fail_s1_contradiction"
    description: "Paper with contradictory claims"
    expected_flag: "SELF_CONTRADICTION"
    expected_severity: 1

  # Severity 2: Likely problems
  - id: "fail_s2_causal_from_correlational"
    description: "Causal claim extracted from survey study"
    expected_flag: "CAUSAL_STATUS_MISMATCH"
    expected_severity: 2

  - id: "fail_s2_huge_effect"
    description: "Effect size d=3.5 from field study"
    expected_flag: "EFFECT_SIZE_IMPLAUSIBLE"
    expected_severity: 2

  - id: "fail_s2_scope_overreach"
    description: "Universal claim from N=25 undergraduate sample"
    expected_flag: "SCOPE_OVERREACH"
    expected_severity: 2

  # Severity 3: Unusual patterns
  - id: "fail_s3_semantic_mismatch"
    description: "Constraint connecting unrelated concepts"
    expected_flag: "SEMANTIC_MISMATCH"
    expected_severity: 3
```

```python
# Location: tests/test_credibility_failure_standard.py

def test_failure_standard_detection():
    """Verify all Failure Standard cases are detected."""
    failure_corpus = load_failure_standard()
    tester = CredibilityTester(web, config)

    for case in failure_corpus.cases:
        report = tester.evaluate(case.extracted_data)

        # Must detect expected flag
        flag_types = [f.flag_type.value for f in report.flags]
        assert case.expected_flag in flag_types, \
            f"Failed to detect {case.expected_flag} in {case.id}"

        # Must assign correct severity
        relevant_flags = [f for f in report.flags if f.flag_type.value == case.expected_flag]
        assert any(f.severity.value == case.expected_severity for f in relevant_flags), \
            f"Wrong severity for {case.id}"
```

---

## 6. Feedback Loop

### 6.1 Resolution Tracking

```python
# Location: src/services/credibility_feedback.py

class FeedbackTracker:
    """Track flag resolutions to improve thresholds."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def record_resolution(self, resolution: FlagResolution):
        """Record how a flag was resolved."""
        ...

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Compute performance metrics from resolution history."""
        resolutions = self._get_all_resolutions()

        metrics = {}
        for flag_type in FlagType:
            type_resolutions = [r for r in resolutions if r.flag_type == flag_type]
            if type_resolutions:
                true_positives = sum(1 for r in type_resolutions if r.resolution == "true_positive")
                false_positives = sum(1 for r in type_resolutions if r.resolution == "false_positive")
                total = len(type_resolutions)

                metrics[flag_type.value] = {
                    "total_flags": total,
                    "true_positive_rate": true_positives / total if total > 0 else 0,
                    "false_positive_rate": false_positives / total if total > 0 else 0,
                }

        return metrics

    def suggest_threshold_adjustments(self) -> List[ThresholdAdjustment]:
        """
        Suggest threshold adjustments based on performance.
        Per Simon: Adjust based on actual false positive rates.
        """
        metrics = self.get_performance_metrics()
        adjustments = []

        for flag_type, data in metrics.items():
            if data["false_positive_rate"] > 0.4:  # Too many false alarms
                adjustments.append(ThresholdAdjustment(
                    flag_type=flag_type,
                    direction="raise",
                    reason=f"False positive rate {data['false_positive_rate']:.0%} exceeds 40%"
                ))
            elif data["false_positive_rate"] < 0.1 and data["total_flags"] > 10:
                # Very few false alarms - maybe threshold is too conservative
                adjustments.append(ThresholdAdjustment(
                    flag_type=flag_type,
                    direction="lower",
                    reason=f"False positive rate only {data['false_positive_rate']:.0%}, may be missing issues"
                ))

        return adjustments
```

---

## 7. Integration with Pipeline

```python
# Location: app/tasks/pipeline.py (modification)

def process_article(article_id: str, pdf_path: str) -> ProcessingResult:
    """Process article with credibility checking."""

    # Extract (existing)
    extracted = extract_from_pdf(pdf_path)

    # Get pre-state
    pre_state = web.get_state_snapshot()

    # Apply to web (tentatively)
    web.begin_transaction()
    try:
        beliefs, constraints = web.integrate_extraction(extracted)
        post_state = web.get_state_snapshot()

        # Credibility check
        credibility_report = credibility_tester.evaluate(
            article_id=article_id,
            pre_state=pre_state,
            post_state=post_state,
            extracted_beliefs=beliefs,
            extracted_constraints=constraints
        )

        # Decision
        if credibility_report.recommended_action == RecommendedAction.AUTO_ACCEPT:
            web.commit_transaction()
            return ProcessingResult(status="accepted", report=credibility_report)

        elif credibility_report.recommended_action == RecommendedAction.AUTO_REJECT:
            web.rollback_transaction()
            return ProcessingResult(status="rejected", report=credibility_report)

        else:  # FLAG_FOR_REVIEW
            web.rollback_transaction()
            review_queue.add(article_id, credibility_report)
            return ProcessingResult(status="flagged", report=credibility_report)

    except Exception as e:
        web.rollback_transaction()
        raise
```

---

## 8. Sprint Plan

### Sprint B: Core Checks (2 weeks)

**Goals:**
- Implement Severity 1 checks (all)
- Implement Severity 2 checks (causal_status_mismatch, excessive_credence_change, effect_size_plausibility)
- Create Failure Standard corpus (Severity 1-2 cases)
- Integrate with pipeline (transaction support)

**Deliverables:**
- `src/services/credibility_testing.py` (core module)
- `gold_standard/failure_standard/` (adversarial test cases)
- Tests achieving 100% detection on Failure Standard
- Pipeline integration (tentative apply, check, commit/rollback)

**Decision Points to Track:**
- Threshold values for excessive_credence_change
- Effect size plausibility ranges by study type
- How to handle papers with missing statistical info

### Sprint C: Extended Checks (2 weeks)

**Goals:**
- Implement remaining Severity 2 checks (scope_overreach, causal_cycle)
- Implement all Severity 3 checks
- Calibrate from Gold Standard corpus
- Build feedback tracking infrastructure

**Deliverables:**
- Complete check suite
- `BaselineStatistics` computed from Gold Standard
- `src/services/credibility_feedback.py`
- Dashboard for viewing flags and metrics

**Decision Points to Track:**
- Semantic similarity computation method
- Stub creation: when is it a concern vs. expected?
- Threshold tuning based on initial runs

### Sprint D: Calibration and Testing (2 weeks)

**Goals:**
- Process test corpus (20+ papers)
- Collect initial flag resolutions
- Tune thresholds based on performance
- Achieve target metrics (90% sensitivity, <30% false positive among flags)

**Deliverables:**
- Performance report
- Tuned thresholds
- Documentation of threshold rationale
- Recommendation for production deployment

**Decision Points to Track:**
- Which flags needed threshold adjustment?
- Any flag types that should be promoted/demoted in severity?
- Resource requirements for human review

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Severity 1 detection rate | 100% | All Failure Standard S1 cases caught |
| Severity 2 detection rate | 95% | Failure Standard + randomly injected errors |
| Severity 3 detection rate | 80% | Failure Standard + expert review |
| False positive rate (among flags) | <30% | Resolutions from human review |
| Flag rate (% of articles flagged) | 10-20% | Processing logs |
| Processing time overhead | <5 sec/article | Benchmarks (no API calls) |
| Auto-reject rate | <2% | Processing logs (only logical impossibilities) |

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Baseline statistics unstable with small Gold Standard | Start conservative (flag more), tighten as corpus grows |
| Semantic similarity unreliable for CNfA terms | Validate against expert judgments; use multiple methods |
| Human review becomes bottleneck | Batch Severity 3 flags for weekly review; prioritize by severity |
| Threshold tuning requires many resolutions | Use simulated resolutions initially; refine with real data |
| Novel paper types not in baseline | Flag anything far from baseline; expand baseline iteratively |

---

## 11. Files to Create

```
src/services/credibility_testing.py      # Core module
src/services/credibility_feedback.py     # Feedback tracking
tests/test_credibility_testing.py        # Unit tests
tests/test_credibility_failure_standard.py  # Adversarial tests
gold_standard/failure_standard/manifest.yaml
gold_standard/failure_standard/cases/    # Failure case files
docs/CREDIBILITY_TESTING_USER_GUIDE.md   # Documentation
```

---

*Plan ready for critique*
*Next step: Review by team + world-class system designer*
