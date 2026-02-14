"""
Theoretical Paper Extractor (Sprint 6c / Task 6c.2).

Extracts propositions, hypotheses, and conceptual definitions from
theoretical papers for integration into the web of belief.

Per spec §5.5:
"Theoretical papers produce THEORETICAL_PROPOSITIONs, DERIVED_HYPOTHESEs,
BRIDGE_WARRANTs, and CONCEPTUAL_DEFINITIONs."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5.5, §5.6
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.epistemic.node_types import NodeType
from src.epistemic.edge_types import EdgeType
from src.epistemic.contracts.claim_v2 import ClaimV2
from src.epistemic.contracts.edge_v2 import EdgeV2


# =============================================================================
# EXTRACTED DATA STRUCTURES
# =============================================================================

@dataclass
class ExtractedProposition:
    """
    A theoretical proposition extracted from a paper.

    Per spec: "THEORETICAL_PROPOSITIONs propose causal relationships
    or mechanisms, derived from a theoretical framework."
    """
    proposition_id: str
    proposition_text: str
    is_central: bool = False  # Is this the paper's main thesis?
    derivation_chain: Optional[str] = None  # How it's derived from premises
    scope_conditions: List[str] = field(default_factory=list)
    mechanism_specification: Optional[str] = None
    prior_theories: List[str] = field(default_factory=list)  # Theories it builds on
    source_paper_id: str = ""
    source_section: Optional[str] = None

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.proposition_id,
            node_type=NodeType.THEORETICAL_PROPOSITION.value,
            paper_id=self.source_paper_id,
            statement=self.proposition_text,
            ae_confidence=0.35,  # Base for theoretical propositions
            provenance_tier="pdf_confirmed",
            evidence_level="theoretical",
            derivation_chain=[self.derivation_chain] if self.derivation_chain else [],
            scope_conditions=self.scope_conditions,
            source_section=self.source_section,
            article_type_family="theoretical",
        )


@dataclass
class ExtractedHypothesis:
    """
    A derived hypothesis extracted from a theoretical paper.

    Per spec: "DERIVED_HYPOTHESEs are testable predictions derived
    from a proposition. Links to confirming/disconfirming evidence."
    """
    hypothesis_id: str
    hypothesis_text: str
    derived_from_proposition_id: str
    testable_via: Optional[str] = None  # How can this be tested?
    expected_effect_direction: Optional[str] = None  # positive/negative/null
    predicted_effect_size: Optional[str] = None  # qualitative prediction
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.hypothesis_id,
            node_type=NodeType.DERIVED_HYPOTHESIS.value,
            paper_id=self.source_paper_id,
            statement=self.hypothesis_text,
            ae_confidence=0.35,  # Base for derived hypotheses
            provenance_tier="pdf_confirmed",
            evidence_level="derived",
            testable=True if self.testable_via else None,
            article_type_family="theoretical",
        )


@dataclass
class ExtractedDefinition:
    """
    A conceptual definition extracted from a paper.

    Per spec: "CONCEPTUAL_DEFINITIONs define constructs, terms, or
    distinctions. Feeds taxonomy/harmonization."
    """
    definition_id: str
    term_name: str
    definition_text: str
    is_new_term: bool = True  # Is this introducing a new term?
    supersedes_definition: Optional[str] = None  # If redefining existing
    distinguished_from: List[str] = field(default_factory=list)
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.definition_id,
            node_type=NodeType.CONCEPTUAL_DEFINITION.value,
            paper_id=self.source_paper_id,
            statement=f"{self.term_name}: {self.definition_text}",
            ae_confidence=0.80,  # High for definitions
            provenance_tier="pdf_confirmed",
            evidence_level="definitional",
            article_type_family="conceptual_framework",
        )


@dataclass
class ExtractedConstraint:
    """
    A conceptual constraint extracted from a paper.

    Per spec: "CONCEPTUAL_CONSTRAINTs are 'must-not-conflate' rules."
    """
    constraint_id: str
    constraint_name: str
    concept_a: str
    concept_b: str
    why_distinct: str
    conflation_consequences: Optional[str] = None
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.constraint_id,
            node_type=NodeType.CONCEPTUAL_CONSTRAINT.value,
            paper_id=self.source_paper_id,
            statement=f"Must distinguish {self.concept_a} from {self.concept_b}: {self.why_distinct}",
            ae_confidence=0.70,
            provenance_tier="pdf_confirmed",
            evidence_level="constraint",
            article_type_family="conceptual_framework",
        )


@dataclass
class ExtractedBridgeWarrant:
    """
    A bridge warrant extracted from a paper.

    Per spec: "BRIDGE_WARRANTs are explicit links licensing transfer
    from one domain/level to another."
    """
    warrant_id: str
    warrant_text: str
    source_domain: str
    target_domain: str
    justification: str
    strength: float = 0.5  # [0, 1]
    source_paper_id: str = ""

    def to_claim_v2(self) -> ClaimV2:
        """Convert to ClaimV2 for web ingestion."""
        return ClaimV2(
            node_id=self.warrant_id,
            node_type=NodeType.BRIDGE_WARRANT.value,
            paper_id=self.source_paper_id,
            statement=self.warrant_text,
            ae_confidence=self.strength,
            provenance_tier="pdf_confirmed",
            evidence_level="warrant",
            article_type_family="theoretical",
        )


@dataclass
class TheoryRelation:
    """
    A relationship between theories.

    Per spec: "SUBSUMES_THEORY and THEORY_TENSION edges connect
    theoretical propositions."
    """
    from_theory_id: str
    to_theory_id: str
    relation_type: str  # "subsumes" | "tension" | "extends" | "contradicts"
    description: str
    what_changed: Optional[str] = None

    def to_edge_v2(self, paper_id: str = "") -> EdgeV2:
        """Convert to EdgeV2 for web ingestion."""
        edge_type_map = {
            "subsumes": EdgeType.SUBSUMES_THEORY,
            "tension": EdgeType.THEORY_TENSION,
            "extends": EdgeType.SUBSUMES_THEORY,  # Extension is a form of subsumption
            "contradicts": EdgeType.THEORY_TENSION,
        }
        return EdgeV2(
            edge_id=f"theory_rel_{self.from_theory_id}_{self.to_theory_id}",
            edge_type=edge_type_map.get(self.relation_type, EdgeType.THEORY_TENSION).value,
            source_node_id=self.from_theory_id,
            target_node_id=self.to_theory_id,
            weight=0.7 if self.relation_type == "subsumes" else 0.5,
            paper_id=paper_id,
            justification=f"{self.relation_type}: {self.description}",
        )


# =============================================================================
# EXTRACTION RESULT
# =============================================================================

@dataclass
class TheoreticalExtractionResult:
    """
    Complete extraction result from a theoretical paper.

    Contains all extracted nodes and edges ready for web ingestion.
    """
    source_paper_id: str
    source_paper_title: str
    propositions: List[ExtractedProposition] = field(default_factory=list)
    hypotheses: List[ExtractedHypothesis] = field(default_factory=list)
    definitions: List[ExtractedDefinition] = field(default_factory=list)
    constraints: List[ExtractedConstraint] = field(default_factory=list)
    bridge_warrants: List[ExtractedBridgeWarrant] = field(default_factory=list)
    theory_relations: List[TheoryRelation] = field(default_factory=list)
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    extraction_confidence: float = 0.5

    @property
    def total_nodes(self) -> int:
        """Total number of extracted nodes."""
        return (
            len(self.propositions) +
            len(self.hypotheses) +
            len(self.definitions) +
            len(self.constraints) +
            len(self.bridge_warrants)
        )

    @property
    def total_edges(self) -> int:
        """Total number of extracted edges."""
        # Theory relations + THEORETICALLY_PREDICTS edges (one per hypothesis)
        return len(self.theory_relations) + len(self.hypotheses)

    def to_claims(self) -> List[ClaimV2]:
        """Convert all extracted items to ClaimV2 objects."""
        claims = []
        for prop in self.propositions:
            claims.append(prop.to_claim_v2())
        for hyp in self.hypotheses:
            claims.append(hyp.to_claim_v2())
        for defn in self.definitions:
            claims.append(defn.to_claim_v2())
        for constr in self.constraints:
            claims.append(constr.to_claim_v2())
        for warrant in self.bridge_warrants:
            claims.append(warrant.to_claim_v2())
        return claims

    def to_edges(self) -> List[EdgeV2]:
        """Convert all relations to EdgeV2 objects."""
        edges = []

        # Theory relations
        for rel in self.theory_relations:
            edges.append(rel.to_edge_v2(paper_id=self.source_paper_id))

        # THEORETICALLY_PREDICTS edges (proposition → hypothesis)
        for hyp in self.hypotheses:
            edges.append(EdgeV2(
                edge_id=f"predicts_{hyp.derived_from_proposition_id}_{hyp.hypothesis_id}",
                edge_type=EdgeType.THEORETICALLY_PREDICTS.value,
                source_node_id=hyp.derived_from_proposition_id,
                target_node_id=hyp.hypothesis_id,
                weight=0.8,
                paper_id=self.source_paper_id,
                justification=f"Testable via: {hyp.testable_via}" if hyp.testable_via else None,
            ))

        # DEFINES_CONSTRUCT edges (definition → construct)
        for defn in self.definitions:
            edges.append(EdgeV2(
                edge_id=f"defines_{defn.definition_id}",
                edge_type=EdgeType.DEFINES_CONSTRUCT.value,
                source_node_id=defn.definition_id,
                target_node_id=f"construct:{defn.term_name.lower().replace(' ', '_')}",
                weight=0.9,
                paper_id=self.source_paper_id,
                justification=f"Defines term: {defn.term_name}",
            ))

        return edges

    def summary(self) -> Dict[str, Any]:
        """Get a summary of the extraction result."""
        return {
            "source_paper_id": self.source_paper_id,
            "source_paper_title": self.source_paper_title,
            "n_propositions": len(self.propositions),
            "n_hypotheses": len(self.hypotheses),
            "n_definitions": len(self.definitions),
            "n_constraints": len(self.constraints),
            "n_bridge_warrants": len(self.bridge_warrants),
            "n_theory_relations": len(self.theory_relations),
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "extraction_confidence": self.extraction_confidence,
        }


# =============================================================================
# EXTRACTOR
# =============================================================================

class TheoreticalExtractor:
    """
    Extracts theoretical content from papers.

    This is a framework for extraction - actual extraction logic
    would typically use an LLM with structured prompts.
    """

    def __init__(self):
        pass

    def extract_from_template_output(
        self,
        paper_id: str,
        paper_title: str,
        template_output: Dict[str, Any]
    ) -> TheoreticalExtractionResult:
        """
        Extract from a theoretical template output.

        Args:
            paper_id: Unique paper identifier
            paper_title: Paper title
            template_output: Output from the theoretical template extraction

        Returns:
            TheoreticalExtractionResult with all extracted items
        """
        result = TheoreticalExtractionResult(
            source_paper_id=paper_id,
            source_paper_title=paper_title,
        )

        # Extract main thesis as central proposition
        if "thesis" in template_output:
            thesis = template_output["thesis"]
            if "main_claim" in thesis:
                result.propositions.append(ExtractedProposition(
                    proposition_id=f"{paper_id}_prop_central",
                    proposition_text=thesis["main_claim"],
                    is_central=True,
                    source_paper_id=paper_id,
                ))

        # Extract arguments as additional propositions
        if "arguments" in template_output:
            for i, arg in enumerate(template_output["arguments"].get("premise_conclusion", [])):
                result.propositions.append(ExtractedProposition(
                    proposition_id=f"{paper_id}_prop_{i}",
                    proposition_text=arg.get("conclusion", arg) if isinstance(arg, dict) else str(arg),
                    derivation_chain=arg.get("premises") if isinstance(arg, dict) else None,
                    source_paper_id=paper_id,
                ))

        # Extract framework relationships and mechanisms
        if "framework" in template_output:
            framework = template_output["framework"]

            # Extract derived hypotheses
            for i, hyp in enumerate(framework.get("derived_hypotheses", [])):
                parent_prop_id = f"{paper_id}_prop_central"
                result.hypotheses.append(ExtractedHypothesis(
                    hypothesis_id=f"{paper_id}_hyp_{i}",
                    hypothesis_text=hyp.get("hypothesis_text", hyp) if isinstance(hyp, dict) else str(hyp),
                    derived_from_proposition_id=parent_prop_id,
                    testable_via=hyp.get("testable_via") if isinstance(hyp, dict) else None,
                    source_paper_id=paper_id,
                ))

            # Extract scope conditions
            if "scope_conditions" in framework and result.propositions:
                result.propositions[0].scope_conditions = framework["scope_conditions"]

        # Extract foundation (prior theories)
        if "foundation" in template_output:
            foundation = template_output["foundation"]

            # Extract theory relations
            for prior in foundation.get("prior_theories", []):
                if isinstance(prior, dict):
                    result.theory_relations.append(TheoryRelation(
                        from_theory_id=f"{paper_id}_prop_central",
                        to_theory_id=prior.get("theory_id", prior.get("name", "unknown")),
                        relation_type=prior.get("relation_type", "extends"),
                        description=prior.get("description", ""),
                        what_changed=prior.get("what_changed"),
                    ))

            # Extract new concepts as definitions
            for concept in foundation.get("key_concepts", []):
                if isinstance(concept, dict) and concept.get("source") == "new":
                    result.definitions.append(ExtractedDefinition(
                        definition_id=f"{paper_id}_def_{concept.get('term', 'unknown')}",
                        term_name=concept.get("term", "unknown"),
                        definition_text=concept.get("definition", ""),
                        is_new_term=True,
                        source_paper_id=paper_id,
                    ))

        # Set extraction confidence based on completeness
        completeness = 0.0
        if result.propositions:
            completeness += 0.4
        if result.hypotheses:
            completeness += 0.3
        if result.definitions or result.constraints:
            completeness += 0.2
        if result.theory_relations:
            completeness += 0.1
        result.extraction_confidence = min(1.0, completeness)

        return result

    def create_proposition(
        self,
        paper_id: str,
        text: str,
        is_central: bool = False,
        mechanism: Optional[str] = None,
        scope_conditions: Optional[List[str]] = None,
    ) -> ExtractedProposition:
        """
        Create a proposition manually.

        Useful when building extraction programmatically.
        """
        prop_id = f"{paper_id}_prop_{uuid.uuid4().hex[:8]}"
        return ExtractedProposition(
            proposition_id=prop_id,
            proposition_text=text,
            is_central=is_central,
            mechanism_specification=mechanism,
            scope_conditions=scope_conditions or [],
            source_paper_id=paper_id,
        )

    def create_hypothesis(
        self,
        paper_id: str,
        text: str,
        derived_from: str,
        testable_via: Optional[str] = None,
    ) -> ExtractedHypothesis:
        """
        Create a hypothesis manually.

        Args:
            paper_id: Paper identifier
            text: Hypothesis text
            derived_from: ID of parent proposition
            testable_via: How the hypothesis can be tested
        """
        hyp_id = f"{paper_id}_hyp_{uuid.uuid4().hex[:8]}"
        return ExtractedHypothesis(
            hypothesis_id=hyp_id,
            hypothesis_text=text,
            derived_from_proposition_id=derived_from,
            testable_via=testable_via,
            source_paper_id=paper_id,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_theoretical_paper(
    paper_id: str,
    paper_title: str,
    template_output: Dict[str, Any]
) -> TheoreticalExtractionResult:
    """
    Extract theoretical content from a paper.

    Args:
        paper_id: Unique paper identifier
        paper_title: Paper title
        template_output: Output from theoretical template extraction

    Returns:
        TheoreticalExtractionResult
    """
    extractor = TheoreticalExtractor()
    return extractor.extract_from_template_output(paper_id, paper_title, template_output)


def compute_proposition_entrenchment(
    argument_quality: str,
    evidential_grounding: str,
    testability: str,
) -> float:
    """
    Compute entrenchment for a theoretical proposition.

    Per spec §5.5 entrenchment computation.

    Args:
        argument_quality: "valid_supported" | "valid_questionable" | "gaps"
        evidential_grounding: "strong" | "some" | "weak"
        testability: "clear" | "difficult"

    Returns:
        Entrenchment value [0, 1]
    """
    base = 0.35

    # Argument quality bonus
    if argument_quality == "valid_supported":
        base += 0.15
    elif argument_quality == "valid_questionable":
        base += 0.05
    elif argument_quality == "gaps":
        base -= 0.10

    # Evidential grounding bonus
    if evidential_grounding == "strong":
        base += 0.10
    elif evidential_grounding == "some":
        base += 0.05

    # Testability bonus
    if testability == "clear":
        base += 0.05
    elif testability == "difficult":
        base -= 0.05

    return max(0.0, min(1.0, base))
