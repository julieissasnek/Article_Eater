"""
Three Hierarchy Relations: Explanatory, Evidential, Compositional
=================================================================
Created: 2026-03-03
Implements: Panel Recommendation #4 (Unanimous)

The ATLAS taxonomy conflates three fundamentally different relations under
a single "hierarchy." As Woodward, Bechtel, Pearl, Smith, and Craver
unanimously agreed, these relations have different logical properties and
must be kept distinct:

  1. Explanatory:  T1 → T1.5 → T2 (top-down; X explains Y if X provides
                   causal principles that account for Y)
  2. Evidential:   T3 → T2 → T1.5 → T1 (bottom-up; empirical data supports/
                   validates templates, which exemplify theories)
  3. Compositional: bidirectional (X is composed of Y, where Y are parts/
                    constituents; T1 frameworks composed of atoms, molecules
                    composed of templates, functional circuits composed of
                    atoms in archetype patterns)

Each relation is independently indexed and queryable. They share entities
(the same T2 template appears in all three) but the *edges* carry different
semantics.

References:
- Woodward, J. (2003). Making Things Happen. Oxford University Press.
- Craver, C. F. (2007). Explaining the Brain. Oxford University Press.
- Pearl, J. (2009). Causality (2nd ed.). Cambridge University Press.
- Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative.
  Studies in History and Philosophy of Biological and Biomedical Sciences, 36, 421-441.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from src.qa.molecules.registry import MoleculeRegistry
from src.qa.molecules.t1_5_registry import T1_5Registry


class RelationType(Enum):
    """The three fundamental hierarchy relations in ATLAS."""
    EXPLANATORY = "explanatory"       # T1 → T1.5 → T2 (top-down causal account)
    EVIDENTIAL = "evidential"         # T3 → T2 → T1.5 → T1 (bottom-up empirical support)
    COMPOSITIONAL = "compositional"   # bidirectional (parts-whole)


class EntityTier(Enum):
    """Tiers of knowledge entities in the ATLAS hierarchy."""
    T1_FRAMEWORK = "T1"
    T1_ATOM = "T1_ATOM"
    T1_5_THEORY = "T1.5"
    MOLECULE = "MOLECULE"
    T2_TEMPLATE = "T2"
    T2_ARCHETYPE = "T2_ARCHETYPE"
    FUNCTIONAL_CIRCUIT = "FC"
    T3_BELIEF = "T3"


@dataclass
class HierarchyEdge:
    """A directed edge in one of the three hierarchy structures.

    Each edge connects two entities and carries semantics specific to
    the relation type. The same pair of entities may appear in multiple
    relations with different edge semantics.
    """
    source_id: str
    source_tier: EntityTier
    target_id: str
    target_tier: EntityTier
    relation: RelationType
    edge_label: str                       # e.g. "explains", "is_evidenced_by", "composed_of"
    confidence: float = 1.0               # 0-1 strength of the relation
    provenance: str = "system_derived"    # how this edge was established

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_tier": self.source_tier.value,
            "target_id": self.target_id,
            "target_tier": self.target_tier.value,
            "relation": self.relation.value,
            "edge_label": self.edge_label,
            "confidence": self.confidence,
            "provenance": self.provenance,
        }


class ExplanatoryHierarchy:
    """Structure 1: Top-down causal explanation.

    Edges: "explains"
    Direction: T1 → T1.5 → T2 (top-down)
    Semantics: X explains Y if X provides causal principles that account for Y.

    Traversal answers: "How does T1 explain this T2 template?"
    """

    def __init__(self, t1_5_registry: T1_5Registry, molecule_registry: MoleculeRegistry):
        self._t1_5 = t1_5_registry
        self._mol = molecule_registry
        self._edges: List[HierarchyEdge] = []
        self._build_index()

    def _build_index(self):
        """Build explanatory edges from T1 → T1.5 → T2.

        T1 explains T1.5: each T1.5 theory lists parent_t1_frameworks with
        percentage contributions. A T1 framework "explains" a T1.5 theory
        proportional to its contribution.

        T1.5 explains T2: each T1.5 theory lists constituent_templates.
        The T1.5 theory "explains" each of those T2 templates.
        """
        for theory in self._t1_5.get_all():
            # T1 → T1.5 edges
            for fw_id, pct in theory.parent_t1_frameworks.items():
                self._edges.append(HierarchyEdge(
                    source_id=fw_id,
                    source_tier=EntityTier.T1_FRAMEWORK,
                    target_id=theory.theory_id,
                    target_tier=EntityTier.T1_5_THEORY,
                    relation=RelationType.EXPLANATORY,
                    edge_label="explains",
                    confidence=pct / 100.0 if pct > 0 else 0.0,
                    provenance="t1_5_parent_framework"
                ))

            # T1.5 → T2 edges
            for tid in theory.constituent_templates:
                self._edges.append(HierarchyEdge(
                    source_id=theory.theory_id,
                    source_tier=EntityTier.T1_5_THEORY,
                    target_id=tid,
                    target_tier=EntityTier.T2_TEMPLATE,
                    relation=RelationType.EXPLANATORY,
                    edge_label="explains",
                    confidence=1.0,
                    provenance="t1_5_constituent"
                ))

    def explained_by(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all entities that explain the given entity (upstream causes)."""
        return [e for e in self._edges if e.target_id == entity_id]

    def explains(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all entities that the given entity explains (downstream effects)."""
        return [e for e in self._edges if e.source_id == entity_id]

    def trace_explanation(self, template_id: str) -> Dict:
        """Trace the full explanatory chain for a T2 template.

        Returns: {template_id, t1_5_explanations: [...], t1_explanations: [...]}
        """
        t1_5_edges = [e for e in self._edges
                      if e.target_id == template_id
                      and e.target_tier == EntityTier.T2_TEMPLATE]

        t1_explanations = []
        for t1_5_edge in t1_5_edges:
            t1_edges = [e for e in self._edges
                        if e.target_id == t1_5_edge.source_id
                        and e.target_tier == EntityTier.T1_5_THEORY]
            t1_explanations.extend(t1_edges)

        return {
            "template_id": template_id,
            "t1_5_explanations": [e.to_dict() for e in t1_5_edges],
            "t1_explanations": [e.to_dict() for e in t1_explanations],
        }

    @property
    def edges(self) -> List[HierarchyEdge]:
        return list(self._edges)

    @property
    def edge_count(self) -> int:
        return len(self._edges)


class EvidentialHierarchy:
    """Structure 2: Bottom-up empirical support.

    Edges: "is_evidenced_by"
    Direction: T3 → T2 → T1.5 → T1 (bottom-up)
    Semantics: T3 data supports/validates T2 templates, which exemplify T1.5 theories.

    Traversal answers: "What evidence supports this T1.5 theory?"
    """

    def __init__(self, t1_5_registry: T1_5Registry, molecule_registry: MoleculeRegistry):
        self._t1_5 = t1_5_registry
        self._mol = molecule_registry
        self._edges: List[HierarchyEdge] = []
        self._build_index()

    def _build_index(self):
        """Build evidential edges from T2 → T1.5 → T1.

        Evidence flows bottom-up: T2 templates are "evidenced_by" T3 beliefs
        (this part requires web-of-belief data, so we build the structural
        edges from T2→T1.5 and T1.5→T1 based on the theory definitions).

        T2 → T1.5: a template "provides evidence for" the T1.5 theories
        that include it as a constituent.

        T1.5 → T1: a T1.5 theory "provides evidence for" each of its
        parent T1 frameworks.
        """
        for theory in self._t1_5.get_all():
            # T2 → T1.5 edges (templates evidence theories)
            for tid in theory.constituent_templates:
                self._edges.append(HierarchyEdge(
                    source_id=tid,
                    source_tier=EntityTier.T2_TEMPLATE,
                    target_id=theory.theory_id,
                    target_tier=EntityTier.T1_5_THEORY,
                    relation=RelationType.EVIDENTIAL,
                    edge_label="provides_evidence_for",
                    confidence=1.0,
                    provenance="t1_5_constituent_reverse"
                ))

            # T1.5 → T1 edges (theories evidence frameworks)
            for fw_id, pct in theory.parent_t1_frameworks.items():
                self._edges.append(HierarchyEdge(
                    source_id=theory.theory_id,
                    source_tier=EntityTier.T1_5_THEORY,
                    target_id=fw_id,
                    target_tier=EntityTier.T1_FRAMEWORK,
                    relation=RelationType.EVIDENTIAL,
                    edge_label="provides_evidence_for",
                    confidence=pct / 100.0 if pct > 0 else 0.0,
                    provenance="t1_5_parent_framework_reverse"
                ))

    def evidenced_by(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all entities that provide evidence for the given entity."""
        return [e for e in self._edges if e.target_id == entity_id]

    def provides_evidence_for(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all entities that the given entity provides evidence for."""
        return [e for e in self._edges if e.source_id == entity_id]

    def trace_evidence(self, framework_id: str) -> Dict:
        """Trace the full evidential chain for a T1 framework.

        Returns: {framework_id, t1_5_evidence: [...], t2_evidence: [...]}
        """
        t1_5_edges = [e for e in self._edges
                      if e.target_id == framework_id
                      and e.source_tier == EntityTier.T1_5_THEORY]

        t2_evidence = []
        for t1_5_edge in t1_5_edges:
            t2_edges = [e for e in self._edges
                        if e.target_id == t1_5_edge.source_id
                        and e.source_tier == EntityTier.T2_TEMPLATE]
            t2_evidence.extend(t2_edges)

        return {
            "framework_id": framework_id,
            "t1_5_evidence": [e.to_dict() for e in t1_5_edges],
            "t2_evidence": [e.to_dict() for e in t2_evidence],
        }

    @property
    def edges(self) -> List[HierarchyEdge]:
        return list(self._edges)

    @property
    def edge_count(self) -> int:
        return len(self._edges)


class CompositionHierarchy:
    """Structure 3: Parts-whole composition.

    Edges: "composed_of"
    Direction: bidirectional
    Semantics: X is composed of Y, where Y are parts/constituents.

    Three distinct composition types (per Craver 2007):
    - Functional composition: molecules composed of templates by function
    - Spatial composition: (future) spatial containment relations
    - Type composition: T1 frameworks composed of T1 atoms

    Traversal answers: "What are molecules made of?"
    """

    def __init__(self, molecule_registry: MoleculeRegistry):
        self._mol = molecule_registry
        self._edges: List[HierarchyEdge] = []
        self._build_index()

    def _build_index(self):
        """Build compositional edges.

        Molecule → T2 template: a molecule is "composed_of" its
        constituent_templates.

        Functional circuit → T2 archetype: a functional circuit
        instantiates an archetype pattern.
        """
        for mol in self._mol.get_all():
            # Molecule → T2 templates (functional composition)
            for tid in mol.constituent_templates:
                self._edges.append(HierarchyEdge(
                    source_id=mol.molecule_id,
                    source_tier=(EntityTier.FUNCTIONAL_CIRCUIT
                                 if mol.molecule_type == "FUNCTIONAL_CIRCUIT"
                                 else EntityTier.MOLECULE),
                    target_id=tid,
                    target_tier=EntityTier.T2_TEMPLATE,
                    relation=RelationType.COMPOSITIONAL,
                    edge_label="composed_of",
                    confidence=1.0,
                    provenance="molecule_constituent"
                ))

            # Functional circuit → T2 archetype (type composition)
            for arch in getattr(mol, 'linked_archetypes', []):
                self._edges.append(HierarchyEdge(
                    source_id=mol.molecule_id,
                    source_tier=EntityTier.FUNCTIONAL_CIRCUIT,
                    target_id=arch,
                    target_tier=EntityTier.T2_ARCHETYPE,
                    relation=RelationType.COMPOSITIONAL,
                    edge_label="instantiates",
                    confidence=1.0,
                    provenance="fc_archetype_link"
                ))

    def composed_of(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all parts that compose the given entity."""
        return [e for e in self._edges if e.source_id == entity_id]

    def part_of(self, entity_id: str) -> List[HierarchyEdge]:
        """Find all entities that contain the given entity as a part."""
        return [e for e in self._edges if e.target_id == entity_id]

    def trace_composition(self, molecule_id: str) -> Dict:
        """Trace the full compositional structure of a molecule.

        Returns: {molecule_id, templates: [...], archetypes: [...]}
        """
        template_edges = [e for e in self._edges
                          if e.source_id == molecule_id
                          and e.target_tier == EntityTier.T2_TEMPLATE]
        archetype_edges = [e for e in self._edges
                           if e.source_id == molecule_id
                           and e.target_tier == EntityTier.T2_ARCHETYPE]

        return {
            "molecule_id": molecule_id,
            "templates": [e.to_dict() for e in template_edges],
            "archetypes": [e.to_dict() for e in archetype_edges],
        }

    @property
    def edges(self) -> List[HierarchyEdge]:
        return list(self._edges)

    @property
    def edge_count(self) -> int:
        return len(self._edges)


class ThreeRelationIndex:
    """Unified index over all three hierarchy relations.

    This is the primary interface for querying the ATLAS hierarchy.
    It composes the three separate structures (explanatory, evidential,
    compositional) and provides cross-relation queries.

    The key insight from the panel (Woodward, Craver, Pearl) is that
    asking "how does T1 explain T3?" requires traversing BOTH the
    explanatory AND compositional hierarchies. Different questions
    traverse different subsets of the three structures.

    SUCCESS CONDITIONS:
    SC-TRI-1: All three sub-hierarchies are independently queryable
    SC-TRI-2: Cross-relation queries compose correctly
    SC-TRI-3: Entity appears in consistent tier across all relations
    SC-TRI-4: Edge counts are non-zero for non-empty registries
    """

    def __init__(self, t1_5_registry: T1_5Registry = None,
                 molecule_registry: MoleculeRegistry = None):
        self._t1_5 = t1_5_registry or T1_5Registry()
        self._mol = molecule_registry or MoleculeRegistry()

        self.explanatory = ExplanatoryHierarchy(self._t1_5, self._mol)
        self.evidential = EvidentialHierarchy(self._t1_5, self._mol)
        self.compositional = CompositionHierarchy(self._mol)

    def get_all_edges(self, relation: RelationType = None) -> List[HierarchyEdge]:
        """Get all edges, optionally filtered by relation type."""
        if relation == RelationType.EXPLANATORY:
            return self.explanatory.edges
        elif relation == RelationType.EVIDENTIAL:
            return self.evidential.edges
        elif relation == RelationType.COMPOSITIONAL:
            return self.compositional.edges
        else:
            return (self.explanatory.edges +
                    self.evidential.edges +
                    self.compositional.edges)

    def get_entity_relations(self, entity_id: str) -> Dict[str, List[HierarchyEdge]]:
        """Get all relations involving an entity, organized by relation type.

        This is the key cross-relation query: for a given entity, what
        roles does it play in each of the three structures?
        """
        return {
            "explanatory_upstream": self.explanatory.explained_by(entity_id),
            "explanatory_downstream": self.explanatory.explains(entity_id),
            "evidential_supporting": self.evidential.evidenced_by(entity_id),
            "evidential_supported_by": self.evidential.provides_evidence_for(entity_id),
            "compositional_parts": self.compositional.composed_of(entity_id),
            "compositional_wholes": self.compositional.part_of(entity_id),
        }

    def full_trace(self, entity_id: str) -> Dict:
        """Complete trace of an entity across all three relations.

        For a T2 template, this answers:
        - What explains it? (explanatory trace upward)
        - What does it provide evidence for? (evidential trace upward)
        - What molecules is it part of? (compositional trace upward)
        """
        relations = self.get_entity_relations(entity_id)
        return {
            "entity_id": entity_id,
            "explanatory": {
                "explained_by": [e.to_dict() for e in relations["explanatory_upstream"]],
                "explains": [e.to_dict() for e in relations["explanatory_downstream"]],
            },
            "evidential": {
                "evidenced_by": [e.to_dict() for e in relations["evidential_supporting"]],
                "provides_evidence_for": [e.to_dict() for e in relations["evidential_supported_by"]],
            },
            "compositional": {
                "composed_of": [e.to_dict() for e in relations["compositional_parts"]],
                "part_of": [e.to_dict() for e in relations["compositional_wholes"]],
            },
        }

    def summary(self) -> str:
        """Human-readable summary of the three hierarchy structures."""
        lines = [
            "Three-Relation Hierarchy Index",
            "=" * 40,
            "",
            f"  Explanatory edges:   {self.explanatory.edge_count}",
            f"  Evidential edges:    {self.evidential.edge_count}",
            f"  Compositional edges: {self.compositional.edge_count}",
            f"  Total edges:         {self.explanatory.edge_count + self.evidential.edge_count + self.compositional.edge_count}",
            "",
            "Relation semantics:",
            "  Explanatory:   T1 --explains--> T1.5 --explains--> T2",
            "  Evidential:    T2 --evidences--> T1.5 --evidences--> T1",
            "  Compositional: Molecule --composed_of--> T2; FC --instantiates--> Archetype",
        ]
        return "\n".join(lines)
