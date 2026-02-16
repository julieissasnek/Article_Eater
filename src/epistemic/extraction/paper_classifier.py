"""
Paper Type Classifier (Sprint 6c / Task 6c.1).

Classifies academic papers into one of 15 template families and maps
to the node types each family can produce.

Per spec §1.1:
"The extraction pipeline was designed around an implicit model —
paper = empirical study — that captures only one of the 15 template families.
The other 14 families contain precisely the connective tissue that makes
the web of belief more than a glorified effect-size database."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5, Appendix A
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.epistemic.node_types import NodeType


class TemplateFamily(str, Enum):
    """
    The 15 template families for academic paper types.

    Each family has distinct extraction strategies and produces
    different combinations of node types.
    """
    # Family 1: Empirical Studies (primary evidence)
    EMPIRICAL_V2 = "empirical_v2"
    OBSERVATIONAL_FIELD = "observational_field"
    CASE_STUDY = "case_study"

    # Family 2: Synthesis Studies (aggregated evidence)
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    NARRATIVE_REVIEW = "narrative_review"

    # Family 3: Theoretical Papers (structural)
    THEORETICAL = "theoretical"
    CONCEPTUAL_FRAMEWORK = "conceptual_framework"

    # Family 4: Qualitative Studies
    INTERVIEW_STUDY = "interview_study"
    ETHNOGRAPHIC = "ethnographic"
    GROUNDED_THEORY = "grounded_theory"
    PHENOMENOLOGICAL = "phenomenological"

    # Family 5: Mixed/Other
    MIXED_METHODS = "mixed_methods"
    THOUGHT_PIECE = "thought_piece"

    # Family 6: Unknown/Unclassified
    UNKNOWN = "unknown"


# =============================================================================
# TEMPLATE FAMILY → NODE TYPES MAPPING (Appendix A)
# =============================================================================

TEMPLATE_NODE_TYPES: Dict[TemplateFamily, Set[NodeType]] = {
    TemplateFamily.EMPIRICAL_V2: {
        NodeType.EMPIRICAL_FINDING,
    },
    TemplateFamily.META_ANALYSIS: {
        NodeType.SYNTHESIS_CONCLUSION,
        NodeType.KNOWLEDGE_GAP,
    },
    TemplateFamily.SYSTEMATIC_REVIEW: {
        NodeType.SYNTHESIS_CONCLUSION,
        NodeType.METHODOLOGICAL_CRITIQUE,
        NodeType.KNOWLEDGE_GAP,
    },
    TemplateFamily.NARRATIVE_REVIEW: {
        NodeType.EXPERT_SYNTHESIS,
        NodeType.KNOWLEDGE_GAP,
        NodeType.BRIDGE_WARRANT,
    },
    TemplateFamily.THEORETICAL: {
        NodeType.THEORETICAL_PROPOSITION,
        NodeType.DERIVED_HYPOTHESIS,
        NodeType.CONCEPTUAL_DEFINITION,
        NodeType.BRIDGE_WARRANT,
    },
    TemplateFamily.CONCEPTUAL_FRAMEWORK: {
        NodeType.CONCEPTUAL_DEFINITION,
        NodeType.CONCEPTUAL_CONSTRAINT,
        NodeType.FRAMEWORK_STRUCTURE,
    },
    TemplateFamily.MIXED_METHODS: {
        NodeType.EMPIRICAL_FINDING,
        NodeType.QUALITATIVE_FINDING,
        NodeType.BRIDGE_WARRANT,
    },
    TemplateFamily.OBSERVATIONAL_FIELD: {
        NodeType.EMPIRICAL_FINDING,
    },
    TemplateFamily.CASE_STUDY: {
        NodeType.EMPIRICAL_FINDING,
        NodeType.DERIVED_HYPOTHESIS,
        NodeType.BRIDGE_WARRANT,
    },
    TemplateFamily.INTERVIEW_STUDY: {
        NodeType.QUALITATIVE_FINDING,
    },
    TemplateFamily.ETHNOGRAPHIC: {
        NodeType.QUALITATIVE_FINDING,
        NodeType.CONCEPTUAL_DEFINITION,
    },
    TemplateFamily.GROUNDED_THEORY: {
        NodeType.QUALITATIVE_FINDING,
        NodeType.DERIVED_HYPOTHESIS,
    },
    TemplateFamily.PHENOMENOLOGICAL: {
        NodeType.QUALITATIVE_FINDING,
    },
    TemplateFamily.THOUGHT_PIECE: {
        NodeType.EXPERT_SYNTHESIS,
        NodeType.METHODOLOGICAL_CRITIQUE,
        NodeType.KNOWLEDGE_GAP,
    },
    TemplateFamily.UNKNOWN: set(),  # Unknown papers produce nothing
}


# =============================================================================
# CLASSIFICATION SIGNALS
# =============================================================================

@dataclass
class ClassificationSignals:
    """
    Signals extracted from a paper for classification.

    These signals are used by the classifier to determine the template family.
    """
    title: str = ""
    abstract: str = ""
    venue: str = ""
    section_headings: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    has_methods_section: bool = False
    has_results_section: bool = False
    has_quantitative_results: bool = False
    has_effect_sizes: bool = False
    has_included_studies_table: bool = False
    has_forest_plot: bool = False
    has_prisma_diagram: bool = False
    n_references: int = 0
    n_figures: int = 0
    n_tables: int = 0


# =============================================================================
# KEYWORD PATTERNS FOR CLASSIFICATION
# =============================================================================

# Title/abstract patterns suggesting specific template families
TITLE_PATTERNS: Dict[TemplateFamily, List[str]] = {
    TemplateFamily.META_ANALYSIS: [
        r"meta[-\s]?analy",
        r"pooled\s+effect",
        r"quantitative\s+synthesis",
        r"systematic.*pooled",
    ],
    TemplateFamily.SYSTEMATIC_REVIEW: [
        r"systematic\s+review",
        r"scoping\s+review",
        r"evidence\s+synthesis",
        r"prisma",
    ],
    TemplateFamily.NARRATIVE_REVIEW: [
        r"(?<!systematic\s)review(?!\s+of\s+the\s+literature)",
        r"state\s+of\s+the\s+art",
        r"current\s+perspectives",
        r"integrative\s+review",
    ],
    TemplateFamily.THEORETICAL: [
        r"theor(y|etical)\s+(of|for|about)",
        r"toward\s+a\s+theory",
        r"conceptual\s+model",
        r"mechanistic\s+account",
        r"framework\s+for\s+understanding",
    ],
    TemplateFamily.CONCEPTUAL_FRAMEWORK: [
        r"conceptual\s+framework",
        r"taxonom(y|ic)",
        r"typolog(y|ical)",
        r"classification\s+of",
        r"defining\s+\w+\s*:",
    ],
    TemplateFamily.GROUNDED_THEORY: [
        r"grounded\s+theory",
        r"constant\s+comparative",
    ],
    TemplateFamily.PHENOMENOLOGICAL: [
        r"phenomenolog",
        r"lived\s+experience",
        r"hermeneutic",
    ],
    TemplateFamily.ETHNOGRAPHIC: [
        r"ethnograph",
        r"participant\s+observation",
        r"fieldwork",
    ],
    TemplateFamily.INTERVIEW_STUDY: [
        r"interview\s+study",
        r"qualitative\s+interview",
        r"semi[-\s]?structured\s+interview",
        r"in[-\s]?depth\s+interview",
        r"focus\s+group",
    ],
    TemplateFamily.CASE_STUDY: [
        r"case\s+study",
        r"single[-\s]?case",
        r"multiple[-\s]?case",
        r"instrumental\s+case",
    ],
    TemplateFamily.MIXED_METHODS: [
        r"mixed[-\s]?method",
        r"multi[-\s]?method",
        r"quantitative\s+and\s+qualitative",
        r"convergent\s+design",
        r"explanatory\s+sequential",
    ],
    TemplateFamily.OBSERVATIONAL_FIELD: [
        r"field\s+study",
        r"naturalistic\s+observation",
        r"post[-\s]?occupancy\s+evaluation",
        r"in[-\s]?situ",
    ],
    TemplateFamily.THOUGHT_PIECE: [
        r"commentary",
        r"perspective",
        r"opinion",
        r"editorial",
        r"viewpoint",
        r"position\s+paper",
    ],
}

# Section headings that suggest specific template families
SECTION_PATTERNS: Dict[TemplateFamily, List[str]] = {
    TemplateFamily.META_ANALYSIS: [
        r"forest\s+plot",
        r"pooled\s+effect",
        r"heterogeneity",
        r"publication\s+bias",
        r"funnel\s+plot",
        r"sensitivity\s+analysis",
    ],
    TemplateFamily.SYSTEMATIC_REVIEW: [
        r"inclusion\s+criteria",
        r"exclusion\s+criteria",
        r"search\s+strategy",
        r"quality\s+assessment",
        r"risk\s+of\s+bias",
        r"included\s+studies",
    ],
    TemplateFamily.EMPIRICAL_V2: [
        r"participants",
        r"procedure",
        r"measures",
        r"statistical\s+analysis",
        r"results",
        r"manipulation\s+check",
    ],
    TemplateFamily.GROUNDED_THEORY: [
        r"theoretical\s+sampling",
        r"open\s+coding",
        r"axial\s+coding",
        r"selective\s+coding",
        r"core\s+category",
    ],
    TemplateFamily.PHENOMENOLOGICAL: [
        r"epoché",
        r"bracketing",
        r"essence",
        r"meaning\s+units",
        r"textural\s+description",
        r"structural\s+description",
    ],
}


# =============================================================================
# CLASSIFIER
# =============================================================================

@dataclass
class ClassificationResult:
    """Result of paper classification."""
    template_family: TemplateFamily
    confidence: float  # [0, 1]
    producible_node_types: Set[NodeType]
    signals_matched: List[str]
    is_empirical: bool
    is_synthesis: bool
    is_theoretical: bool
    is_qualitative: bool
    runner_up_family: Optional[TemplateFamily] = None
    margin: float = 0.0
    needs_manual_review: bool = False
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    diagnostics: List[str] = field(default_factory=list)


class PaperClassifier:
    """
    Classifies papers into template families based on content signals.

    The classifier uses a combination of:
    - Title/abstract keyword matching
    - Section heading analysis
    - Structural features (presence of methods, results, etc.)
    - Content patterns (effect sizes, forest plots, etc.)
    """

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for efficiency."""
        self._title_patterns = {
            family: [re.compile(p, re.IGNORECASE) for p in patterns]
            for family, patterns in TITLE_PATTERNS.items()
        }
        self._section_patterns = {
            family: [re.compile(p, re.IGNORECASE) for p in patterns]
            for family, patterns in SECTION_PATTERNS.items()
        }

    def classify(self, signals: ClassificationSignals) -> ClassificationResult:
        """
        Classify a paper based on extracted signals.

        Args:
            signals: ClassificationSignals containing paper metadata

        Returns:
            ClassificationResult with template family and confidence
        """
        scores: Dict[TemplateFamily, float] = {f: 0.0 for f in TemplateFamily}
        matched_signals: Dict[TemplateFamily, List[str]] = {f: [] for f in TemplateFamily}
        diagnostics: List[str] = []

        text = " ".join([signals.title, signals.abstract, signals.venue, " ".join(signals.keywords)]).strip()
        text_lower = text.lower()
        title_lower = signals.title.lower()

        # 1. Score based on title/abstract patterns
        for family, patterns in self._title_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    scores[family] += 2.0
                    matched_signals[family].append(f"title_pattern:{pattern.pattern}")

        # 2. Score based on section headings
        section_text = " ".join(signals.section_headings)
        for family, patterns in self._section_patterns.items():
            for pattern in patterns:
                if pattern.search(section_text):
                    scores[family] += 1.5
                    matched_signals[family].append(f"section:{pattern.pattern}")

        # 3. Lexical indicators with phrase-boundary matching.
        empirical_method_hits, empirical_method_terms = self._count_phrase_hits(
            text_lower,
            [
                "participants",
                "methods",
                "procedure",
                "sample size",
                "intervention",
                "control group",
                "randomized",
                "randomised",
                "between-subject",
                "within-subject",
                "trial",
                "experiment",
                "experimental",
                "cross-sectional",
                "cohort",
            ],
        )
        quantitative_hits, quantitative_terms = self._count_phrase_hits(
            text_lower,
            [
                "p <",
                "p=",
                "95% ci",
                "confidence interval",
                "effect size",
                "cohen",
                "anova",
                "regression",
                "odds ratio",
                "beta",
            ],
        )
        review_hits, review_terms = self._count_phrase_hits(
            text_lower,
            [
                "systematic review",
                "scoping review",
                "narrative review",
                "literature review",
                "meta-analysis",
                "meta analysis",
                "review of",
                "evidence synthesis",
            ],
        )
        theoretical_hits, theoretical_terms = self._count_phrase_hits(
            text_lower,
            [
                "toward a theory",
                "theory of",
                "theory for",
                "theoretical framework",
                "conceptual model",
                "mechanistic account",
                "proposition",
                "taxonomy",
                "typology",
            ],
        )
        qualitative_hits, qualitative_terms = self._count_phrase_hits(
            text_lower,
            [
                "interview",
                "focus group",
                "ethnograph",
                "grounded theory",
                "phenomenolog",
                "participant observation",
            ],
        )

        if empirical_method_hits >= 2:
            scores[TemplateFamily.EMPIRICAL_V2] += 1.8
            matched_signals[TemplateFamily.EMPIRICAL_V2].append(
                f"empirical_method_hits:{','.join(empirical_method_terms[:4])}"
            )
        if empirical_method_hits >= 1 and quantitative_hits >= 1:
            scores[TemplateFamily.EMPIRICAL_V2] += 1.2
            matched_signals[TemplateFamily.EMPIRICAL_V2].append(
                f"empirical_quant_combo:{','.join(quantitative_terms[:3])}"
            )
        if quantitative_hits >= 1:
            scores[TemplateFamily.OBSERVATIONAL_FIELD] += 0.8

        if review_hits:
            scores[TemplateFamily.NARRATIVE_REVIEW] += 1.2
            matched_signals[TemplateFamily.NARRATIVE_REVIEW].append(
                f"review_hits:{','.join(review_terms[:3])}"
            )
        if review_hits and not empirical_method_hits:
            scores[TemplateFamily.SYSTEMATIC_REVIEW] += 0.8
        if qualitative_hits >= 2:
            scores[TemplateFamily.INTERVIEW_STUDY] += 1.0
            matched_signals[TemplateFamily.INTERVIEW_STUDY].append(
                f"qual_hits:{','.join(qualitative_terms[:3])}"
            )
        if theoretical_hits >= 1:
            scores[TemplateFamily.THEORETICAL] += 1.2
            matched_signals[TemplateFamily.THEORETICAL].append(
                f"theory_hits:{','.join(theoretical_terms[:3])}"
            )
        if "conceptual framework" in text_lower or "taxonomy" in text_lower:
            scores[TemplateFamily.CONCEPTUAL_FRAMEWORK] += 1.5

        # 4. Structural features from parsed signals
        if signals.has_forest_plot or signals.has_included_studies_table:
            scores[TemplateFamily.META_ANALYSIS] += 3.0
            matched_signals[TemplateFamily.META_ANALYSIS].append("has_forest_plot_or_studies_table")

        if signals.has_prisma_diagram:
            scores[TemplateFamily.SYSTEMATIC_REVIEW] += 2.5
            matched_signals[TemplateFamily.SYSTEMATIC_REVIEW].append("has_prisma_diagram")

        if signals.has_methods_section and signals.has_results_section:
            if signals.has_quantitative_results and signals.has_effect_sizes:
                scores[TemplateFamily.EMPIRICAL_V2] += 2.0
                matched_signals[TemplateFamily.EMPIRICAL_V2].append("has_methods_results_effects")
            elif signals.has_quantitative_results:
                scores[TemplateFamily.EMPIRICAL_V2] += 1.0
                scores[TemplateFamily.OBSERVATIONAL_FIELD] += 1.0

        if not signals.has_methods_section and not signals.has_results_section:
            scores[TemplateFamily.THEORETICAL] += 0.3
            scores[TemplateFamily.NARRATIVE_REVIEW] += 0.5
            scores[TemplateFamily.THOUGHT_PIECE] += 0.3

        # 5. Conflict resolution / penalties
        has_review_title = self._phrase_present(title_lower, "review")
        has_empirical_core = (
            signals.has_methods_section
            or signals.has_results_section
            or empirical_method_hits >= 2
            or (empirical_method_hits >= 1 and quantitative_hits >= 1)
        )
        if has_review_title and not has_empirical_core:
            scores[TemplateFamily.NARRATIVE_REVIEW] += 1.3
            scores[TemplateFamily.EMPIRICAL_V2] -= 1.0
            diagnostics.append("title_review_without_empirical_core")

        if "review of experiments" in text_lower or "review of experimental" in text_lower:
            scores[TemplateFamily.NARRATIVE_REVIEW] += 1.6
            scores[TemplateFamily.EMPIRICAL_V2] -= 1.2
            diagnostics.append("review_of_experiments_not_primary_empirical")

        if has_empirical_core and theoretical_hits:
            scores[TemplateFamily.THEORETICAL] -= 0.8
            diagnostics.append("theory_mentions_deweighted_due_to_empirical_core")

        # 6. Score based on reference count
        if signals.n_references > 100:
            scores[TemplateFamily.SYSTEMATIC_REVIEW] += 1.0
            scores[TemplateFamily.META_ANALYSIS] += 0.5
            matched_signals[TemplateFamily.SYSTEMATIC_REVIEW].append("high_ref_count")
        elif 0 < signals.n_references < 20:
            scores[TemplateFamily.THOUGHT_PIECE] += 0.5
            scores[TemplateFamily.CASE_STUDY] += 0.5

        # 7. Find winner and runner-up
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_family, best_score = ranked[0]
        runner_up_family, runner_up_score = ranked[1] if len(ranked) > 1 else (TemplateFamily.UNKNOWN, 0.0)
        margin = float(best_score - runner_up_score)

        if best_score < 0.8:
            if has_empirical_core:
                best_family = TemplateFamily.EMPIRICAL_V2
                best_score = 1.0
                matched_signals[best_family].append("default_empirical_from_structural_core")
                margin = max(margin, 0.2)
            else:
                best_family = TemplateFamily.UNKNOWN
                best_score = 0.0
                margin = 0.0

        confidence = min(1.0, max(0.0, (best_score + max(margin, 0.0)) / 5.5))
        needs_manual_review = bool(
            best_family == TemplateFamily.UNKNOWN
            or confidence < 0.55
            or margin < 0.35
        )

        node_types = TEMPLATE_NODE_TYPES.get(best_family, set())

        is_empirical = best_family in {
            TemplateFamily.EMPIRICAL_V2,
            TemplateFamily.OBSERVATIONAL_FIELD,
            TemplateFamily.CASE_STUDY,
            TemplateFamily.MIXED_METHODS,
        }
        is_synthesis = best_family in {
            TemplateFamily.META_ANALYSIS,
            TemplateFamily.SYSTEMATIC_REVIEW,
            TemplateFamily.NARRATIVE_REVIEW,
        }
        is_theoretical = best_family in {
            TemplateFamily.THEORETICAL,
            TemplateFamily.CONCEPTUAL_FRAMEWORK,
        }
        is_qualitative = best_family in {
            TemplateFamily.INTERVIEW_STUDY,
            TemplateFamily.ETHNOGRAPHIC,
            TemplateFamily.GROUNDED_THEORY,
            TemplateFamily.PHENOMENOLOGICAL,
        }

        return ClassificationResult(
            template_family=best_family,
            confidence=confidence,
            producible_node_types=node_types,
            signals_matched=matched_signals.get(best_family, []),
            is_empirical=is_empirical,
            is_synthesis=is_synthesis,
            is_theoretical=is_theoretical,
            is_qualitative=is_qualitative,
            runner_up_family=runner_up_family if runner_up_family != TemplateFamily.UNKNOWN else None,
            margin=margin,
            needs_manual_review=needs_manual_review,
            score_breakdown={k.value: float(v) for k, v in ranked},
            diagnostics=diagnostics,
        )

    def classify_from_text(
        self,
        title: str,
        abstract: str,
        venue: str = "",
        section_headings: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
    ) -> ClassificationResult:
        """
        Convenience method to classify from raw text.

        Args:
            title: Paper title
            abstract: Paper abstract
            section_headings: Optional list of section headings
            keywords: Optional list of keywords

        Returns:
            ClassificationResult
        """
        inferred = self._infer_structural_signals(title=title, abstract=abstract, venue=venue)
        signals = ClassificationSignals(
            title=title,
            abstract=abstract,
            venue=venue,
            section_headings=section_headings or inferred["section_headings"],
            keywords=keywords or [],
            has_methods_section=self._has_section(section_headings or [], ["method", "materials"]) or inferred["has_methods_section"],
            has_results_section=self._has_section(section_headings or [], ["result", "finding"]) or inferred["has_results_section"],
            has_quantitative_results=inferred["has_quantitative_results"],
            has_effect_sizes=inferred["has_effect_sizes"],
            has_included_studies_table=inferred["has_included_studies_table"],
            has_forest_plot=inferred["has_forest_plot"],
            has_prisma_diagram=inferred["has_prisma_diagram"],
        )
        return self.classify(signals)

    def _has_section(self, headings: List[str], patterns: List[str]) -> bool:
        """Check if any heading matches any pattern."""
        headings_lower = " ".join(h.lower() for h in headings)
        return any(p in headings_lower for p in patterns)

    def _phrase_present(self, text: str, phrase: str) -> bool:
        escaped = re.escape(phrase).replace(r"\ ", r"\s+")
        return re.search(rf"(?<!\w){escaped}(?!\w)", text, flags=re.IGNORECASE) is not None

    def _count_phrase_hits(self, text: str, phrases: List[str]) -> Tuple[int, List[str]]:
        hits: List[str] = []
        for phrase in phrases:
            if self._phrase_present(text, phrase):
                hits.append(phrase)
        return len(hits), hits

    def _infer_structural_signals(self, title: str, abstract: str, venue: str) -> Dict[str, Any]:
        combined = " ".join([title, abstract, venue]).lower()
        sections = []
        if re.search(r"\bmethods?\b", combined):
            sections.append("methods")
        if re.search(r"\bresults?\b|\bfindings?\b", combined):
            sections.append("results")
        if re.search(r"\bdiscussion\b", combined):
            sections.append("discussion")
        if re.search(r"\bconclusion(s)?\b", combined):
            sections.append("conclusion")

        has_methods = bool(
            re.search(
                r"\b(methods?|participants?|procedure|sample|randomi[sz]ed|intervention|control group)\b",
                combined,
            )
        )
        has_results = bool(
            re.search(
                r"\b(results?|findings?|observed|demonstrated|showed|significant)\b",
                combined,
            )
        )
        has_quant = bool(
            re.search(
                r"(\bp\s*[<=>]\s*0?\.\d+)|(\b95%\s*ci\b)|(\bci\b)|(\banova\b)|(\bregression\b)|(\bodds ratio\b)",
                combined,
            )
        )
        has_effect = bool(
            re.search(
                r"\b(effect size|cohen'?s?\s*d|hedges'\s*g|odds ratio|risk ratio|beta coefficient)\b",
                combined,
            )
        )

        return {
            "section_headings": sections,
            "has_methods_section": has_methods,
            "has_results_section": has_results,
            "has_quantitative_results": has_quant,
            "has_effect_sizes": has_effect,
            "has_included_studies_table": bool(re.search(r"\bincluded studies\b", combined)),
            "has_forest_plot": bool(re.search(r"\bforest plot\b", combined)),
            "has_prisma_diagram": bool(re.search(r"\bprisma\b", combined)),
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_node_types_for_template(family: TemplateFamily) -> Set[NodeType]:
    """
    Get the node types that a template family can produce.

    Args:
        family: The template family

    Returns:
        Set of NodeType values
    """
    return TEMPLATE_NODE_TYPES.get(family, set())


def can_produce_node_type(family: TemplateFamily, node_type: NodeType) -> bool:
    """
    Check if a template family can produce a specific node type.

    Args:
        family: The template family
        node_type: The node type to check

    Returns:
        True if the family can produce this node type
    """
    return node_type in TEMPLATE_NODE_TYPES.get(family, set())


def get_templates_producing_node_type(node_type: NodeType) -> List[TemplateFamily]:
    """
    Get all template families that can produce a specific node type.

    Args:
        node_type: The node type to look up

    Returns:
        List of template families
    """
    return [
        family for family, types in TEMPLATE_NODE_TYPES.items()
        if node_type in types
    ]


def is_empirical_template(family: TemplateFamily) -> bool:
    """Check if a template family produces empirical findings."""
    return family in {
        TemplateFamily.EMPIRICAL_V2,
        TemplateFamily.OBSERVATIONAL_FIELD,
        TemplateFamily.CASE_STUDY,
        TemplateFamily.MIXED_METHODS,
    }


def is_synthesis_template(family: TemplateFamily) -> bool:
    """Check if a template family produces synthesis conclusions."""
    return family in {
        TemplateFamily.META_ANALYSIS,
        TemplateFamily.SYSTEMATIC_REVIEW,
    }


def is_qualitative_template(family: TemplateFamily) -> bool:
    """Check if a template family produces qualitative findings."""
    return family in {
        TemplateFamily.INTERVIEW_STUDY,
        TemplateFamily.ETHNOGRAPHIC,
        TemplateFamily.GROUNDED_THEORY,
        TemplateFamily.PHENOMENOLOGICAL,
        TemplateFamily.MIXED_METHODS,
    }


# =============================================================================
# SINGLETON CLASSIFIER
# =============================================================================

_classifier: Optional[PaperClassifier] = None


def get_classifier() -> PaperClassifier:
    """Get the singleton paper classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = PaperClassifier()
    return _classifier


def classify_paper(
    title: str,
    abstract: str,
    venue: str = "",
    section_headings: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
) -> ClassificationResult:
    """
    Classify a paper using the singleton classifier.

    Args:
        title: Paper title
        abstract: Paper abstract
        section_headings: Optional list of section headings
        keywords: Optional list of keywords

    Returns:
        ClassificationResult
    """
    return get_classifier().classify_from_text(
        title=title,
        abstract=abstract,
        venue=venue,
        section_headings=section_headings,
        keywords=keywords,
    )
