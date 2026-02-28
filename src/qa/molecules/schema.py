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
    """Tier 2 composite construct built from Tier 1 Templates."""
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
    scope_conditions: List[str] = field(default_factory=list)
    overall_maturity: str = "TENTATIVE"
    
    # Evidence
    key_references: List[str] = field(default_factory=list) # DOIs
    empirical_support: str = "PRELIMINARY" # "ESTABLISHED", "SUPPORTED", "PRELIMINARY"

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
            "scope_conditions": self.scope_conditions,
            "overall_maturity": self.overall_maturity,
            "key_references": self.key_references,
            "empirical_support": self.empirical_support
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
            scope_conditions=data.get("scope_conditions", []),
            overall_maturity=data.get("overall_maturity", "TENTATIVE"),
            key_references=data.get("key_references", []),
            empirical_support=data.get("empirical_support", "PRELIMINARY")
        )
