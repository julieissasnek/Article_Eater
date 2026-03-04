from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MoleculeComponent:
    """Named sub-part of a molecule (e.g., Soft Fascination)."""
    name: str
    template_ids: List[str]
    interaction_type: str  # "ADDITIVE", "MULTIPLICATIVE", "SYNERGISTIC", "PREREQUISITE"
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "template_ids": self.template_ids,
            "interaction_type": self.interaction_type,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoleculeComponent':
        return cls(
            name=data["name"],
            template_ids=data["template_ids"],
            interaction_type=data["interaction_type"],
            description=data["description"]
        )

@dataclass
class Molecule:
    """Tier 2 composite construct built from Tier 1 Templates.
    
    Molecules sit between raw extracted claims (Tier 0/1) and broad 
    frameworks (Tier 3). They represent the smallest named, recognizable 
    theoretical unit a user would search for (e.g., "Attention Restoration 
    Theory"), composed of multiple interacting Templates.
    
    See: docs/MOLECULES_DEEP_REFLECTION_2026_02_24.md
    """
    molecule_id: str
    name: str
    short_description: str
    components: List[MoleculeComponent]
    constituent_templates: List[str]
    
    # Structure
    interaction_graph: Dict[str, Dict[str, str]]  # template -> template -> interaction_type
    
    # Metadata
    framework_ids: List[str]
    domain: str
    molecule_type: str = "THEORY"  # "THEORY", "MECHANISM", "PHENOMENON", "DESIGN_PATTERN"
    scope_conditions: List[str] = field(default_factory=list)
    overall_maturity: str = "TENTATIVE"  # "TENTATIVE", "PRELIMINARY", "SUPPORTED", "ESTABLISHED"
    
    # Evidence
    key_references: List[str] = field(default_factory=list)
    empirical_support: str = "PRELIMINARY"

    # --- New fields from Schema Expansion (2026-02-24) ---

    # Competing/alternative theories that explain the same phenomena
    competing_theories: List[str] = field(default_factory=list)

    # Actionable guidance for practitioners derived from this molecule
    design_implications: List[str] = field(default_factory=list)

    # Numeric spread of effect sizes across constituent templates
    # e.g. {"cohens_d_range": [0.2, 0.8], "typical_d": 0.45}
    confidence_intervals: Optional[Dict[str, Any]] = None

    # --- T1.5 Theory Layer (2026-02-24) ---
    # [C4] Molecule keeps its own constituent_templates (no auto-derivation from T1.5)
    # [HC] Links molecule to its canonical T1.5 parent theory
    parent_t1_5_theory: Optional[str] = None

    # --- Functional Circuit Fields (2026-03-03) ---
    # molecule_type values now include: THEORY, MECHANISM, PHENOMENON, DESIGN_PATTERN, FUNCTIONAL_CIRCUIT
    # Functional circuits are molecules whose internal structure follows T2 archetype patterns.
    # These fields connect the molecule to the T2 computational archetype grammar.
    linked_archetypes: List[str] = field(default_factory=list)  # e.g. ["PREDICTIVE_CODING", "HOMEOSTATIC_REGULATION"]
    inputs: List[str] = field(default_factory=list)   # named input variables from archetype
    outputs: List[str] = field(default_factory=list)  # named output variables

    def to_dict(self) -> Dict[str, Any]:
        return {
            "molecule_id": self.molecule_id,
            "name": self.name,
            "short_description": self.short_description,
            "components": [c.to_dict() for c in self.components],
            "constituent_templates": self.constituent_templates,
            "interaction_graph": self.interaction_graph,
            "framework_ids": self.framework_ids,
            "domain": self.domain,
            "molecule_type": self.molecule_type,
            "scope_conditions": self.scope_conditions,
            "overall_maturity": self.overall_maturity,
            "key_references": self.key_references,
            "empirical_support": self.empirical_support,
            "competing_theories": self.competing_theories,
            "design_implications": self.design_implications,
            "confidence_intervals": self.confidence_intervals,
            "parent_t1_5_theory": self.parent_t1_5_theory,
            "linked_archetypes": self.linked_archetypes,
            "inputs": self.inputs,
            "outputs": self.outputs
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Molecule':
        return cls(
            molecule_id=data["molecule_id"],
            name=data["name"],
            short_description=data["short_description"],
            components=[MoleculeComponent.from_dict(c) for c in data.get("components", [])],
            constituent_templates=data.get("constituent_templates", []),
            interaction_graph=data.get("interaction_graph", {}),
            framework_ids=data.get("framework_ids", []),
            domain=data.get("domain", ""),
            molecule_type=data.get("molecule_type", "THEORY"),
            scope_conditions=data.get("scope_conditions", []),
            overall_maturity=data.get("overall_maturity", "TENTATIVE"),
            key_references=data.get("key_references", []),
            empirical_support=data.get("empirical_support", "PRELIMINARY"),
            competing_theories=data.get("competing_theories", []),
            design_implications=data.get("design_implications", []),
            confidence_intervals=data.get("confidence_intervals"),
            parent_t1_5_theory=data.get("parent_t1_5_theory"),
            linked_archetypes=data.get("linked_archetypes", []),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", [])
        )
