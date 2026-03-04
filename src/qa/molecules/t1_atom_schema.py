"""
T1 Atom Schema
==============
Dataclass and validation for Tier 1 Atoms.

T1 atoms are ~30 computational primitives that underlie T1 frameworks.
Examples: lateral inhibition, gain control, Bayesian updating, binding,
Hebbian association, prediction error, divisive normalization, error
monitoring, precision weighting.

This schema implements the panel's Recommendation #1: "Separate canonical
from hypothetical T1 atoms" by stratifying atoms into three maturity categories:

- CANONICAL: Neurally grounded, mechanistically understood, cross-domain confirmed
- ESTABLISHED: Good evidence but domain-limited or mechanism partially understood
- HYPOTHETICAL: Theoretically motivated but limited direct evidence

Usage:
    atom = T1Atom.from_dict(json_data)
    atom.validate()
    data = atom.to_dict()
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class T1Atom:
    """A single Tier 1 computational primitive.

    T1 atoms are the building blocks of T1 frameworks. They represent
    well-characterized neural computations that appear across multiple
    sensory and cognitive domains.

    Fields:
    -------
    atom_id: str
        Unique identifier (e.g., "lateral_inhibition").

    name: str
        Human-readable name (e.g., "Lateral Inhibition").

    description: str
        2-3 sentence explanation of what this atom computes.

    maturity: str
        One of: CANONICAL, ESTABLISHED, HYPOTHETICAL

    neural_substrate: List[str]
        Brain regions or circuits that implement this atom.
        Examples: ["retina", "V1", "auditory_cortex"]

    computational_signature: str
        Mathematical characterization of the computation.
        Examples: "y_i = x_i - w * sum(x_j) for j in neighborhood"

    t1_frameworks: List[str]
        Which T1 frameworks use this atom.
        Examples: ["predictive-processing", "multisensory-integration"]

    key_references: List[str]
        APA-format citations providing evidence for this atom.

    empirical_evidence: str
        Brief summary of the evidence base supporting this atom.

    cross_domain_confirmed: bool
        True if this atom is used across >1 sensory/cognitive domain.
        All CANONICAL atoms must have this=True.

    parameters: Dict[str, Any]
        Optional: atom-specific parameters.
        Examples: {"inhibition_radius": "varies by layer",
                   "weight_profile": "Mexican hat"}
    """

    atom_id: str
    name: str
    description: str
    maturity: str  # CANONICAL | ESTABLISHED | HYPOTHETICAL
    neural_substrate: List[str]
    computational_signature: str
    t1_frameworks: List[str]
    key_references: List[str]
    empirical_evidence: str
    cross_domain_confirmed: bool
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "atom_id": self.atom_id,
            "name": self.name,
            "description": self.description,
            "maturity": self.maturity,
            "neural_substrate": self.neural_substrate,
            "computational_signature": self.computational_signature,
            "t1_frameworks": self.t1_frameworks,
            "key_references": self.key_references,
            "empirical_evidence": self.empirical_evidence,
            "cross_domain_confirmed": self.cross_domain_confirmed,
            "parameters": self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'T1Atom':
        """Construct from JSON-like dict."""
        return cls(
            atom_id=data["atom_id"],
            name=data["name"],
            description=data["description"],
            maturity=data["maturity"],
            neural_substrate=data.get("neural_substrate", []),
            computational_signature=data.get("computational_signature", ""),
            t1_frameworks=data.get("t1_frameworks", []),
            key_references=data.get("key_references", []),
            empirical_evidence=data.get("empirical_evidence", ""),
            cross_domain_confirmed=data.get("cross_domain_confirmed", False),
            parameters=data.get("parameters", {})
        )

    def validate(self) -> List[str]:
        """Validate this atom's integrity.

        Returns a list of validation errors (empty if valid).

        Validation rules:
        - atom_id: non-empty, lowercase+underscores
        - name: non-empty, <100 chars
        - description: non-empty, 2-3 sentences expected
        - maturity: one of CANONICAL, ESTABLISHED, HYPOTHETICAL
        - neural_substrate: non-empty list
        - computational_signature: non-empty
        - t1_frameworks: non-empty list
        - key_references: non-empty list
        - empirical_evidence: non-empty
        - cross_domain_confirmed: True for all CANONICAL atoms
        """
        errors = []

        if not self.atom_id or not self.atom_id.strip():
            errors.append("atom_id: must be non-empty")
        elif not all(c.islower() or c == '_' for c in self.atom_id):
            errors.append("atom_id: must be lowercase with underscores only")

        if not self.name or not self.name.strip():
            errors.append("name: must be non-empty")
        elif len(self.name) > 100:
            errors.append("name: must be <100 characters")

        if not self.description or not self.description.strip():
            errors.append("description: must be non-empty")

        if self.maturity not in ("CANONICAL", "ESTABLISHED", "HYPOTHETICAL"):
            errors.append(f"maturity: must be CANONICAL/ESTABLISHED/HYPOTHETICAL, got '{self.maturity}'")

        if not self.neural_substrate:
            errors.append("neural_substrate: must be non-empty list")

        if not self.computational_signature or not self.computational_signature.strip():
            errors.append("computational_signature: must be non-empty")

        if not self.t1_frameworks:
            errors.append("t1_frameworks: must be non-empty list")

        if not self.key_references:
            errors.append("key_references: must be non-empty list")

        if not self.empirical_evidence or not self.empirical_evidence.strip():
            errors.append("empirical_evidence: must be non-empty")

        # CANONICAL atoms must be cross_domain_confirmed
        if self.maturity == "CANONICAL" and not self.cross_domain_confirmed:
            errors.append("CANONICAL atoms must have cross_domain_confirmed=True")

        return errors
