"""
ae.claim.v2 Contract (Sprint 6a / Task 6a.3).

Universal node ingestion contract for all node types.
Every node entering the web — regardless of source template family —
must conform to this contract.

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §6.2
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class ProvenanceTier(str, Enum):
    """Source provenance tier."""
    ABSTRACT_PROVISIONAL = "abstract_provisional"
    PDF_CONFIRMED = "pdf_confirmed"


class CausalLevel(str, Enum):
    """Causal certainty level."""
    ASSOCIATION = "association"
    INTERVENTION = "intervention"
    COUNTERFACTUAL = "counterfactual"


class EvidenceBasis(str, Enum):
    """Basis for interpretive claims."""
    CITED_EVIDENCE = "cited_evidence"
    EXPERT_OPINION = "expert_opinion"
    CONSENSUS = "consensus"


class ExtractionDifficulty(str, Enum):
    """Difficulty of extraction."""
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


@dataclass
class ClaimV2:
    """
    Universal ingestion contract for all node types (ae.claim.v2).

    Fixes C1/C2 from gap audit: claim_text→statement, confidence→ae_confidence.

    Required fields for ALL node types:
        node_id, node_type, paper_id, statement, ae_confidence,
        provenance_tier, evidence_level

    Optional fields vary by node type family (see spec §6.2).
    """
    # === REQUIRED FOR ALL NODE TYPES ===
    node_id: str
    node_type: str  # One of the 12 NodeType values
    paper_id: str
    statement: str
    ae_confidence: float  # [0, 1]
    provenance_tier: str  # abstract_provisional | pdf_confirmed
    evidence_level: str

    # === SOURCE LOCATION (optional but recommended) ===
    source_section: Optional[str] = None
    source_page_start: Optional[int] = None
    source_page_end: Optional[int] = None
    source_quote: Optional[str] = None
    source_quote_hash: Optional[str] = None

    # === EVIDENCE NODE FIELDS (Family A) ===
    study_design: Optional[str] = None
    sample_size: Optional[int] = None
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None
    confidence_interval: List[float] = field(default_factory=list)
    p_value: Optional[float] = None
    causal_level: Optional[str] = None  # association | intervention | counterfactual

    # === STRUCTURAL NODE FIELDS (Family B) ===
    derivation_chain: List[str] = field(default_factory=list)
    scope_conditions: List[str] = field(default_factory=list)
    testable: Optional[bool] = None
    falsifiable: Optional[bool] = None

    # === INTERPRETIVE NODE FIELDS (Family C) ===
    author_expertise: Optional[str] = None
    evidence_basis: Optional[str] = None  # cited_evidence | expert_opinion | consensus
    n_studies_cited: Optional[int] = None
    declared_bias: Optional[str] = None

    # === ARGUMENTATIVE METADATA (Panel Additions) ===
    argument_scheme: Optional[str] = None
    critical_questions: List[str] = field(default_factory=list)
    critical_questions_addressed: List[str] = field(default_factory=list)
    critical_questions_unaddressed: List[str] = field(default_factory=list)
    contrast_class: Optional[str] = None
    difference_maker: Optional[str] = None

    # === BIBLIOGRAPHIC METADATA (Sprint METADATA-1) ===
    # Populated from Semantic Scholar / CrossRef enrichment or PDF extraction.
    # Enables temporal ordering (Quine), citation graph (argumentation structure),
    # community detection (Cartwright), and recency weighting (DerSimonian).
    publication_year: Optional[int] = None
    publication_authors: List[str] = field(default_factory=list)
    publication_journal: Optional[str] = None
    citation_count: Optional[int] = None
    influential_citation_count: Optional[int] = None
    references_dois: List[str] = field(default_factory=list)   # DOIs this paper cites
    cited_by_dois: List[str] = field(default_factory=list)      # DOIs citing this paper
    semantic_scholar_id: Optional[str] = None

    # === WEB INTEGRATION METADATA ===
    extraction_difficulty: Optional[str] = None
    source_zone: Optional[str] = None
    article_type_family: Optional[str] = None
    template_version: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "paper_id": self.paper_id,
            "statement": self.statement,
            "ae_confidence": self.ae_confidence,
            "provenance_tier": self.provenance_tier,
            "evidence_level": self.evidence_level,
            "source_section": self.source_section,
            "source_page_start": self.source_page_start,
            "source_page_end": self.source_page_end,
            "source_quote": self.source_quote,
            "source_quote_hash": self.source_quote_hash,
            "study_design": self.study_design,
            "sample_size": self.sample_size,
            "effect_size": self.effect_size,
            "effect_size_type": self.effect_size_type,
            "confidence_interval": self.confidence_interval,
            "p_value": self.p_value,
            "causal_level": self.causal_level,
            "derivation_chain": self.derivation_chain,
            "scope_conditions": self.scope_conditions,
            "testable": self.testable,
            "falsifiable": self.falsifiable,
            "author_expertise": self.author_expertise,
            "evidence_basis": self.evidence_basis,
            "n_studies_cited": self.n_studies_cited,
            "declared_bias": self.declared_bias,
            "argument_scheme": self.argument_scheme,
            "critical_questions": self.critical_questions,
            "critical_questions_addressed": self.critical_questions_addressed,
            "critical_questions_unaddressed": self.critical_questions_unaddressed,
            "contrast_class": self.contrast_class,
            "difference_maker": self.difference_maker,
            "publication_year": self.publication_year,
            "publication_authors": self.publication_authors,
            "publication_journal": self.publication_journal,
            "citation_count": self.citation_count,
            "influential_citation_count": self.influential_citation_count,
            "references_dois": self.references_dois,
            "cited_by_dois": self.cited_by_dois,
            "semantic_scholar_id": self.semantic_scholar_id,
            "extraction_difficulty": self.extraction_difficulty,
            "source_zone": self.source_zone,
            "article_type_family": self.article_type_family,
            "template_version": self.template_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClaimV2":
        """Create from dictionary."""
        return cls(
            node_id=data.get("node_id", ""),
            node_type=data.get("node_type", "empirical_finding"),
            paper_id=data.get("paper_id", ""),
            statement=data.get("statement", ""),
            ae_confidence=data.get("ae_confidence", 0.5),
            provenance_tier=data.get("provenance_tier", "abstract_provisional"),
            evidence_level=data.get("evidence_level", "unknown"),
            source_section=data.get("source_section"),
            source_page_start=data.get("source_page_start"),
            source_page_end=data.get("source_page_end"),
            source_quote=data.get("source_quote"),
            source_quote_hash=data.get("source_quote_hash"),
            study_design=data.get("study_design"),
            sample_size=data.get("sample_size"),
            effect_size=data.get("effect_size"),
            effect_size_type=data.get("effect_size_type"),
            confidence_interval=data.get("confidence_interval", []),
            p_value=data.get("p_value"),
            causal_level=data.get("causal_level"),
            derivation_chain=data.get("derivation_chain", []),
            scope_conditions=data.get("scope_conditions", []),
            testable=data.get("testable"),
            falsifiable=data.get("falsifiable"),
            author_expertise=data.get("author_expertise"),
            evidence_basis=data.get("evidence_basis"),
            n_studies_cited=data.get("n_studies_cited"),
            declared_bias=data.get("declared_bias"),
            argument_scheme=data.get("argument_scheme"),
            critical_questions=data.get("critical_questions", []),
            critical_questions_addressed=data.get("critical_questions_addressed", []),
            critical_questions_unaddressed=data.get("critical_questions_unaddressed", []),
            contrast_class=data.get("contrast_class"),
            difference_maker=data.get("difference_maker"),
            publication_year=data.get("publication_year"),
            publication_authors=data.get("publication_authors", []),
            publication_journal=data.get("publication_journal"),
            citation_count=data.get("citation_count"),
            influential_citation_count=data.get("influential_citation_count"),
            references_dois=data.get("references_dois", []),
            cited_by_dois=data.get("cited_by_dois", []),
            semantic_scholar_id=data.get("semantic_scholar_id"),
            extraction_difficulty=data.get("extraction_difficulty"),
            source_zone=data.get("source_zone"),
            article_type_family=data.get("article_type_family"),
            template_version=data.get("template_version"),
        )

    @classmethod
    def from_legacy(cls, legacy: dict) -> "ClaimV2":
        """
        Create from legacy format (claim_text, confidence).

        Fixes C1/C2 from gap audit.
        """
        return cls(
            node_id=legacy.get("node_id") or legacy.get("claim_id") or legacy.get("id", ""),
            node_type=legacy.get("node_type", "empirical_finding"),
            paper_id=legacy.get("paper_id", ""),
            statement=legacy.get("statement") or legacy.get("claim_text") or legacy.get("text", ""),
            ae_confidence=legacy.get("ae_confidence") or legacy.get("confidence", 0.5),
            provenance_tier=legacy.get("provenance_tier", "abstract_provisional"),
            evidence_level=legacy.get("evidence_level", "unknown"),
            study_design=legacy.get("study_design"),
            sample_size=legacy.get("sample_size"),
        )
