"""
T1.5 Theory Schema — Domain-Level Bridge Theories

T1.5 theories are domain-level theories from environmental psychology that
occupy the intermediate position between T1 neural frameworks (PP, NM, IC...)
and T2 templates. They organize families of phenomena, are *explained by*
T1 frameworks, and retain meaningful irreducible residuals.

Schema grounded in Panel D-1 ReductionClaim architecture (master paper §72)
and the canonical T1.5 roster (§78.3).

Constraints honored:
  [C1] irreducible_residual is REQUIRED (three-part structure)
  [C3] status includes REJECTED/DEFERRED with rejection_rationale
  [HC] parent_t1_frameworks references T1 (not owned by T1)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class IrreducibleResidual:
    """Three-part irreducible residual per Panel D-1 (§72.5).
    
    Part 1: Schema gaps — resolvable by adding/refining templates.
    Part 2: Compositional adequacy — whether the DAG is sufficient.
    Part 3: Narrative — free-text scientific judgment.
    """
    schema_gaps: List[str] = field(default_factory=list)
    compositional_adequacy: str = "INTERACTION_DEPENDENT"  # FULLY_DECOMPOSABLE | INTERACTION_DEPENDENT | EMERGENT_RESIDUAL
    narrative: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_gaps": self.schema_gaps,
            "compositional_adequacy": self.compositional_adequacy,
            "narrative": self.narrative
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IrreducibleResidual':
        return cls(
            schema_gaps=data.get("schema_gaps", []),
            compositional_adequacy=data.get("compositional_adequacy", "INTERACTION_DEPENDENT"),
            narrative=data.get("narrative", "")
        )


@dataclass
class ConstructReduction:
    """A single construct within a T1.5 theory and its template decomposition."""
    construct_name: str
    description: str
    template_ids: List[str]
    reduction_confidence: str = "MEDIUM"  # LOW | LOW-MEDIUM | MEDIUM | HIGH
    maturity: str = "how-plausibly"       # how-possibly | how-plausibly | how-actually

    def to_dict(self) -> Dict[str, Any]:
        return {
            "construct_name": self.construct_name,
            "description": self.description,
            "template_ids": self.template_ids,
            "reduction_confidence": self.reduction_confidence,
            "maturity": self.maturity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConstructReduction':
        return cls(
            construct_name=data["construct_name"],
            description=data.get("description", ""),
            template_ids=data.get("template_ids", []),
            reduction_confidence=data.get("reduction_confidence", "MEDIUM"),
            maturity=data.get("maturity", "how-plausibly")
        )


@dataclass
class T1_5Theory:
    """A formally reduced (or rejected/deferred) T1.5 domain theory.
    
    T1.5 theories sit between T1 frameworks and T2 templates.
    They organize domain-level phenomena, are explained by T1 frameworks,
    and retain meaningful irreducible residuals.
    
    Hierarchy (§34.5):
        T1 Frameworks ← referenced by T1.5 via parent_t1_frameworks
        T1.5 Theories ← own their templates; referenced by Molecules
        Molecules     ← QA-facing packaging of T1.5 content
    """
    theory_id: str
    name: str
    originator: str
    year: int
    citation: str
    
    # Status
    status: str  # REDUCED | CANDIDATE | REJECTED | DEFERRED
    
    # T1 framework linkage — maps framework_id -> percentage contribution
    # e.g. {"PP": 40, "SN": 20, "NM": 20, "EC": 10, "IE-DPT": 10}
    parent_t1_frameworks: Dict[str, int] = field(default_factory=dict)
    
    # Construct-level reductions (from §73-77)
    constructs: List[ConstructReduction] = field(default_factory=list)
    
    # All templates this theory covers
    constituent_templates: List[str] = field(default_factory=list)
    
    # Coverage and maturity
    template_coverage_pct: float = 0.0
    maturity: str = "how-plausibly"  # how-possibly | how-plausibly | how-actually
    
    # REQUIRED — three-part irreducible residual [C1]
    irreducible_residual: Optional[IrreducibleResidual] = None
    
    # Required for REJECTED/DEFERRED status [C3]
    rejection_rationale: str = ""
    
    # Child molecules that package this theory
    child_molecules: List[str] = field(default_factory=list)
    
    # Scholarly metadata
    google_scholar_count: int = 0
    key_references: List[str] = field(default_factory=list)
    reduced_in: str = ""  # Source document reference

    # --- Structural Boundary Criteria (2026-03-03) ---
    # Panel Recommendation #3 (Unanimous): Replace sociological boundary
    # ("published author") with structural criteria. Three independent tests:
    #
    # (a) Irreducible residual: Does the theory have genuine emergent content
    #     that cannot be decomposed into T1 frameworks? Threshold: residual
    #     must have ≥1 schema gap OR compositional_adequacy != FULLY_DECOMPOSABLE.
    #
    # (b) Constitutive relevance (Craver 2007): Does the theory name a
    #     mechanism that is constitutively relevant to the phenomenon it
    #     explains? I.e., intervening on the mechanism changes the phenomenon.
    #
    # (c) Design-guidance utility: Does the theory generate specific,
    #     actionable design guidance that is NOT derivable from its constituent
    #     T1 frameworks alone?
    #
    # A theory qualifies as T1.5 if it passes ≥2 of 3 structural tests.
    # This replaces the prior sociological criterion (Craver, Cartwright,
    # Smith, Mitchell, Potochnik — unanimous).
    boundary_criteria: Optional[Dict[str, Any]] = field(default_factory=lambda: None)
    # Expected structure:
    # {
    #   "has_irreducible_residual": bool,    # test (a)
    #   "constitutive_relevance": bool,      # test (b)
    #   "design_guidance_utility": bool,     # test (c)
    #   "structural_score": int,             # count of True (0-3)
    #   "boundary_justification": str        # narrative explaining why
    # }

    def validate(self) -> List[str]:
        """Return list of validation errors, empty if valid."""
        errors = []
        if self.status == "REDUCED" and self.irreducible_residual is None:
            errors.append(f"{self.theory_id}: REDUCED theory must have irreducible_residual [C1]")
        if self.status == "REDUCED" and self.irreducible_residual and not self.irreducible_residual.narrative:
            errors.append(f"{self.theory_id}: irreducible_residual.narrative must not be empty [C1]")
        if self.status in ("REJECTED", "DEFERRED") and not self.rejection_rationale:
            errors.append(f"{self.theory_id}: {self.status} theory must have rejection_rationale [C3]")
        if self.status == "REDUCED" and not self.parent_t1_frameworks:
            errors.append(f"{self.theory_id}: REDUCED theory must have parent_t1_frameworks")
        # Structural boundary check: REDUCED theories should pass ≥2/3 structural tests
        if self.status == "REDUCED" and self.boundary_criteria:
            score = self.boundary_criteria.get("structural_score", 0)
            if score < 2:
                errors.append(
                    f"{self.theory_id}: REDUCED theory passes only {score}/3 structural "
                    f"boundary tests (need ≥2). Consider CANDIDATE status."
                )
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory_id": self.theory_id,
            "name": self.name,
            "originator": self.originator,
            "year": self.year,
            "citation": self.citation,
            "status": self.status,
            "parent_t1_frameworks": self.parent_t1_frameworks,
            "constructs": [c.to_dict() for c in self.constructs],
            "constituent_templates": self.constituent_templates,
            "template_coverage_pct": self.template_coverage_pct,
            "maturity": self.maturity,
            "irreducible_residual": self.irreducible_residual.to_dict() if self.irreducible_residual else None,
            "rejection_rationale": self.rejection_rationale,
            "child_molecules": self.child_molecules,
            "google_scholar_count": self.google_scholar_count,
            "key_references": self.key_references,
            "reduced_in": self.reduced_in,
            "boundary_criteria": self.boundary_criteria
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'T1_5Theory':
        ir_data = data.get("irreducible_residual")
        ir = IrreducibleResidual.from_dict(ir_data) if ir_data else None
        
        return cls(
            theory_id=data["theory_id"],
            name=data["name"],
            originator=data.get("originator", ""),
            year=data.get("year", 0),
            citation=data.get("citation", ""),
            status=data["status"],
            parent_t1_frameworks=data.get("parent_t1_frameworks", {}),
            constructs=[ConstructReduction.from_dict(c) for c in data.get("constructs", [])],
            constituent_templates=data.get("constituent_templates", []),
            template_coverage_pct=data.get("template_coverage_pct", 0.0),
            maturity=data.get("maturity", "how-plausibly"),
            irreducible_residual=ir,
            rejection_rationale=data.get("rejection_rationale", ""),
            child_molecules=data.get("child_molecules", []),
            google_scholar_count=data.get("google_scholar_count", 0),
            key_references=data.get("key_references", []),
            reduced_in=data.get("reduced_in", ""),
            boundary_criteria=data.get("boundary_criteria")
        )
