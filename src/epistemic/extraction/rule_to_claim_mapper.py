"""
Rule to Claim Mapper (Sprint 6 Bridge).

Maps ae.rule.v2 rules from PDF extraction to Sprint 6 ClaimV2 objects
with proper NodeType assignment. This is the critical bridge connecting
the extraction pipeline to the epistemic web infrastructure.

The mapping logic:
    ae.rule.v2.rule_type → Sprint 6 NodeType
    - "edge" → EMPIRICAL_FINDING (causal relationship)
    - "presumption" → THEORETICAL_PROPOSITION (theoretical claim)
    - "association" → EMPIRICAL_FINDING with causal_level="association"
    - "constraint" → CONCEPTUAL_CONSTRAINT (methodological constraint)
    - "rebuttal" → METHODOLOGICAL_CRITIQUE (critique of theory/method)
    - "interaction" → EMPIRICAL_FINDING (interaction effect)
    - "contrast" → EMPIRICAL_FINDING (contrastive explanation)
    - "cpd_hint", "prior" → Not nodes (BN metadata only)

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §6.2
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import json

from src.epistemic.node_types import NodeType
from src.epistemic.edge_types import EdgeType
from src.epistemic.contracts.claim_v2 import ClaimV2
from src.epistemic.contracts.edge_v2 import EdgeV2


# =============================================================================
# RULE TYPE TO NODE TYPE MAPPING
# =============================================================================

RULE_TYPE_TO_NODE_TYPE: Dict[str, NodeType] = {
    # Empirical/evidence rules → EMPIRICAL_FINDING
    "edge": NodeType.EMPIRICAL_FINDING,
    "association": NodeType.EMPIRICAL_FINDING,
    "interaction": NodeType.EMPIRICAL_FINDING,
    "contrast": NodeType.EMPIRICAL_FINDING,

    # Theoretical rules → THEORETICAL_PROPOSITION
    "presumption": NodeType.THEORETICAL_PROPOSITION,

    # Methodological rules → appropriate types
    "constraint": NodeType.CONCEPTUAL_CONSTRAINT,
    "rebuttal": NodeType.METHODOLOGICAL_CRITIQUE,

    # BN-only metadata (not nodes)
    "cpd_hint": None,
    "prior": None,
}


# Evidence level mapping
RULE_TYPE_TO_EVIDENCE_LEVEL: Dict[str, str] = {
    "edge": "empirical",
    "association": "observational",
    "interaction": "empirical",
    "contrast": "contrastive",
    "presumption": "theoretical",
    "constraint": "methodological",
    "rebuttal": "critique",
    "cpd_hint": "bn_metadata",
    "prior": "bn_metadata",
}


# =============================================================================
# MAPPER FUNCTIONS
# =============================================================================

def map_rule_type_to_node_type(rule_type: str) -> Optional[NodeType]:
    """
    Map ae.rule.v2 rule_type to Sprint 6 NodeType.

    Args:
        rule_type: Value from ae.rule.v2.rule_type enum

    Returns:
        Corresponding NodeType, or None for BN-only metadata rules
    """
    return RULE_TYPE_TO_NODE_TYPE.get(rule_type.lower())


def map_causal_level(causal_level: Optional[str]) -> str:
    """Map ae.rule.v2 causal_level to ClaimV2 causal_level."""
    if not causal_level:
        return "association"
    return causal_level.lower()


def extract_statement_from_rule(rule: Dict[str, Any]) -> str:
    """
    Construct a human-readable statement from a rule's lhs/rhs structure.

    Example:
        lhs: [{"var": "env.lighting_colour", "state": "present"}]
        rhs: [{"var": "cog.thermal_comfort_perception", "state": "affected"}]
        polarity: "positive"

        → "Lighting colour positively affects thermal comfort perception"
    """
    # Extract variable names from lhs
    lhs_vars = []
    for item in rule.get("lhs", []):
        var = item.get("var", "")
        # Convert env.lighting_colour → lighting colour
        clean_var = var.split(".")[-1].replace("_", " ")
        lhs_vars.append(clean_var)

    # Extract variable names from rhs
    rhs_vars = []
    for item in rule.get("rhs", []):
        var = item.get("var", "")
        clean_var = var.split(".")[-1].replace("_", " ")
        rhs_vars.append(clean_var)

    # Build statement based on polarity
    polarity = rule.get("polarity", "unknown")
    polarity_word = {
        "positive": "positively affects",
        "negative": "negatively affects",
        "null": "has no effect on",
        "unknown": "affects",
        "u_shaped": "has a U-shaped effect on",
    }.get(polarity, "affects")

    lhs_str = " and ".join(lhs_vars) if lhs_vars else "Unknown factor"
    rhs_str = " and ".join(rhs_vars) if rhs_vars else "unknown outcome"

    return f"{lhs_str.capitalize()} {polarity_word} {rhs_str}"


def rule_to_claim_v2(rule: Dict[str, Any]) -> Optional[ClaimV2]:
    """
    Convert an ae.rule.v2 rule to a Sprint 6 ClaimV2.

    Args:
        rule: Dictionary in ae.rule.v2 format

    Returns:
        ClaimV2 object, or None if the rule type is BN-metadata only
    """
    rule_type = rule.get("rule_type", "edge")
    node_type = map_rule_type_to_node_type(rule_type)

    if node_type is None:
        # This is BN metadata, not a claim node
        return None

    # Extract IDs
    rule_id = rule.get("rule_id", "")
    paper_id = rule.get("paper_id", "")

    # Build statement
    statement = extract_statement_from_rule(rule)

    # Determine provenance tier
    provenance_tier = rule.get("provenance_tier", "abstract_provisional")
    if rule.get("evidence_level") == "abstract_finding_rule":
        provenance_tier = "abstract_provisional"
    elif "pdf" in str(rule.get("evidence_level", "")).lower():
        provenance_tier = "pdf_confirmed"

    # Build ClaimV2
    claim = ClaimV2(
        node_id=rule_id,
        node_type=node_type.value,
        paper_id=paper_id,
        statement=statement,
        ae_confidence=rule.get("ae_confidence", 0.5),
        provenance_tier=provenance_tier,
        evidence_level=RULE_TYPE_TO_EVIDENCE_LEVEL.get(rule_type, "unknown"),
        causal_level=map_causal_level(rule.get("causal_level")),

        # Argumentative metadata (Panel additions)
        argument_scheme=rule.get("argument_scheme"),
        critical_questions=rule.get("critical_questions", []),
        contrast_class=rule.get("contrast_class"),
        difference_maker=rule.get("difference_maker"),

        # Article type
        article_type_family=_infer_article_type(rule_type),
    )

    return claim


def _infer_article_type(rule_type: str) -> str:
    """Infer article type family from rule type."""
    type_map = {
        "edge": "empirical",
        "association": "empirical",
        "interaction": "empirical",
        "contrast": "empirical",
        "presumption": "theoretical",
        "constraint": "methodological",
        "rebuttal": "critique",
    }
    return type_map.get(rule_type, "unknown")


def rule_to_edge_v2(rule: Dict[str, Any]) -> Optional[EdgeV2]:
    """
    Extract causal edge from ae.rule.v2 if it represents a causal relationship.

    For "edge" and "association" rules, creates an edge connecting
    lhs variables to rhs variables in the BN.

    Args:
        rule: Dictionary in ae.rule.v2 format

    Returns:
        EdgeV2 if this is a causal rule, None otherwise
    """
    rule_type = rule.get("rule_type", "")

    # Only edge and association rules create BN edges
    if rule_type not in ("edge", "association", "interaction"):
        return None

    rule_id = rule.get("rule_id", "")
    paper_id = rule.get("paper_id", "")

    # Get BN node suggestions
    bn_mapping = rule.get("bn_mapping", {})
    node_suggestions = bn_mapping.get("node_suggestions", [])

    if len(node_suggestions) < 2:
        return None

    # Simple mapping: first node → second node
    # (In practice, lhs → rhs)
    lhs = rule.get("lhs", [])
    rhs = rule.get("rhs", [])

    if not lhs or not rhs:
        return None

    source_var = lhs[0].get("var", "")
    target_var = rhs[0].get("var", "")

    # Determine edge weight from strength and polarity
    strength = rule.get("strength", {})
    polarity = rule.get("polarity", "unknown")

    weight = 0.5  # Default
    if strength.get("kind") == "effect_size" and strength.get("value"):
        # Use effect size as weight (capped)
        weight = min(abs(strength["value"]), 1.0)
    elif polarity in ("positive", "negative"):
        weight = 0.6  # Known direction

    # Create edge
    return EdgeV2(
        edge_id=f"edge_{rule_id}",
        edge_type="causal",  # Legacy edge type for BN
        source_node_id=f"bn:{source_var}",
        target_node_id=f"bn:{target_var}",
        weight=weight,
        paper_id=paper_id,
        evidence_basis="explicit_statement",
        justification=f"From rule {rule_id}: {polarity} relationship",
        provenance_tier=rule.get("provenance_tier", "abstract_provisional"),
    )


# =============================================================================
# BATCH CONVERSION
# =============================================================================

@dataclass
class ConversionResult:
    """Result of converting rules to Sprint 6 structures."""
    claims: List[ClaimV2]
    edges: List[EdgeV2]
    skipped_bn_metadata: int
    errors: List[Dict[str, Any]]

    @property
    def total_claims(self) -> int:
        return len(self.claims)

    @property
    def total_edges(self) -> int:
        return len(self.edges)

    def summary(self) -> Dict[str, Any]:
        """Get conversion summary."""
        node_type_counts = {}
        for claim in self.claims:
            nt = claim.node_type
            node_type_counts[nt] = node_type_counts.get(nt, 0) + 1

        return {
            "total_claims": self.total_claims,
            "total_edges": self.total_edges,
            "skipped_bn_metadata": self.skipped_bn_metadata,
            "errors": len(self.errors),
            "node_type_distribution": node_type_counts,
        }


def convert_rules_to_sprint6(rules: List[Dict[str, Any]]) -> ConversionResult:
    """
    Convert a list of ae.rule.v2 rules to Sprint 6 ClaimV2 and EdgeV2 objects.

    Args:
        rules: List of dictionaries in ae.rule.v2 format

    Returns:
        ConversionResult with claims, edges, and diagnostics
    """
    claims = []
    edges = []
    skipped = 0
    errors = []

    for rule in rules:
        try:
            # Convert to claim
            claim = rule_to_claim_v2(rule)
            if claim:
                claims.append(claim)
            else:
                skipped += 1

            # Convert to edge (if applicable)
            edge = rule_to_edge_v2(rule)
            if edge:
                edges.append(edge)

        except Exception as e:
            errors.append({
                "rule_id": rule.get("rule_id", "unknown"),
                "error": str(e),
            })

    return ConversionResult(
        claims=claims,
        edges=edges,
        skipped_bn_metadata=skipped,
        errors=errors,
    )


def load_and_convert_rules_jsonl(filepath: str) -> ConversionResult:
    """
    Load rules from JSONL file and convert to Sprint 6 structures.

    Args:
        filepath: Path to JSONL file containing ae.rule.v2 rules

    Returns:
        ConversionResult
    """
    rules = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rules.append(json.loads(line))

    return convert_rules_to_sprint6(rules)


# =============================================================================
# THEORY BOOTSTRAP INTEGRATION
# =============================================================================

def connect_bootstrap_theory_to_claims(
    theory_predictions: List[Dict[str, Any]],
    extracted_claims: List[ClaimV2],
) -> List[EdgeV2]:
    """
    Create CONFIRMS_PREDICTION or DISCONFIRMS_PREDICTION edges
    linking bootstrap theory predictions to extracted claims.

    This connects Tier 1 (theories) to Tier 3 (extracted claims).

    Args:
        theory_predictions: Predictions from theory_bootstrap.py
        extracted_claims: ClaimV2 objects from PDF extraction

    Returns:
        List of EdgeV2 linking predictions to claims
    """
    edges = []

    for pred in theory_predictions:
        pred_id = pred.get("prediction_id", "")
        pred_outcome = pred.get("consequent_outcome", "").lower()
        pred_direction = pred.get("consequent_direction", "").lower()

        for claim in extracted_claims:
            # Check if claim relates to this prediction's outcome
            claim_statement = claim.statement.lower()

            if pred_outcome and pred_outcome in claim_statement:
                # Determine if confirms or disconfirms
                claim_direction = "positive" if "positively" in claim_statement else \
                                  "negative" if "negatively" in claim_statement else \
                                  "null" if "no effect" in claim_statement else "unknown"

                if claim_direction == pred_direction or pred_direction == "unknown":
                    edge_type = EdgeType.CONFIRMS_PREDICTION
                elif claim_direction == "null" and pred_direction in ("positive", "negative"):
                    edge_type = EdgeType.DISCONFIRMS_PREDICTION
                else:
                    edge_type = EdgeType.DISCONFIRMS_PREDICTION

                edges.append(EdgeV2(
                    edge_id=f"theory_link_{pred_id}_{claim.node_id}",
                    edge_type=edge_type.value,
                    source_node_id=claim.node_id,
                    target_node_id=pred_id,
                    weight=0.7 if edge_type == EdgeType.CONFIRMS_PREDICTION else 0.8,
                    paper_id=claim.paper_id,
                    evidence_basis="implicit_connection",
                    justification=f"Claim {'confirms' if edge_type == EdgeType.CONFIRMS_PREDICTION else 'disconfirms'} theory prediction",
                ))

    return edges
