# IMPLEMENTATION_TASKS_ADDENDUM_SPRINT6.md — Non-Empirical Web Integration

**Created**: February 14, 2026
**Depends On**: Sprint 1 (Schema Extensions), Sprint 4b (Method Registry)
**Reference**: `docs/Non_Empirical_Web_Integration_Spec_V1.0.md`

This addendum extends the Epistemic Tier 2 implementation with support for non-empirical paper types (theoretical, review, meta-analysis, conceptual framework, thought piece, qualitative). Currently ~50% of processed PDFs produce no usable claims because the extraction-to-web pipeline only handles empirical findings. Sprint 6 fixes that.

Work through these tasks **in order**. Each task has:
- **Do**: exactly what to implement
- **Test**: how to verify it works
- **Commit**: message format

Do NOT skip ahead. Do NOT proceed if a test fails.

---

## Sprint 6a: Schema Extensions (1 week)

### Task 6a.1: Add NodeType enum with 12 types

**Do**: Create `src/epistemic/node_types.py` with the expanded NodeType enum:

```python
from enum import Enum

class NodeType(str, Enum):
    """
    Node types for web of belief (12 types in 5 families).

    Per Non_Empirical_Web_Integration_Spec_V1.0.md §2.2.
    """
    # Family A: Evidence Nodes (carry data)
    EMPIRICAL_FINDING = "empirical_finding"
    SYNTHESIS_CONCLUSION = "synthesis_conclusion"
    QUALITATIVE_FINDING = "qualitative_finding"

    # Family B: Structural Nodes (organize the web)
    THEORETICAL_PROPOSITION = "theoretical_proposition"
    DERIVED_HYPOTHESIS = "derived_hypothesis"
    CONCEPTUAL_DEFINITION = "conceptual_definition"
    CONCEPTUAL_CONSTRAINT = "conceptual_constraint"

    # Family C: Interpretive Nodes (carry expert judgment)
    EXPERT_SYNTHESIS = "expert_synthesis"
    METHODOLOGICAL_CRITIQUE = "methodological_critique"

    # Family D: Gap Nodes (mark what's missing)
    KNOWLEDGE_GAP = "knowledge_gap"

    # Family E: Meta-Nodes (organize other nodes)
    FRAMEWORK_STRUCTURE = "framework_structure"
    BRIDGE_WARRANT = "bridge_warrant"
```

**Test**:
```python
from src.epistemic.node_types import NodeType
assert len(NodeType) == 12
assert NodeType.THEORETICAL_PROPOSITION.value == "theoretical_proposition"
assert NodeType.SYNTHESIS_CONCLUSION.value == "synthesis_conclusion"
```

**Commit**: `[Sprint 6a / Task 6a.1] Add NodeType enum with 12 types`

---

### Task 6a.2: Add new EdgeType enum values

**Do**: Extend the existing edge type enum (in `src/services/web_of_belief.py` or create `src/epistemic/edge_types.py`) with the new edge types from spec §3.2:

```python
# === Review/Synthesis Edges ===
INCLUDES_IN_SYNTHESIS = "includes_in_synthesis"
SYNTHESIZES_AS = "synthesizes_as"
IDENTIFIES_MODERATOR = "identifies_moderator"
CONTRADICTS_SYNTHESIS = "contradicts_synthesis"

# === Theoretical Edges ===
THEORETICALLY_PREDICTS = "theoretically_predicts"
CONFIRMS_PREDICTION = "confirms_prediction"
DISCONFIRMS_PREDICTION = "disconfirms_prediction"
PROPOSES_MECHANISM = "proposes_mechanism"
SUBSUMES_THEORY = "subsumes_theory"
THEORY_TENSION = "theory_tension"

# === Conceptual Edges ===
DEFINES_CONSTRUCT = "defines_construct"
MUST_DISTINGUISH = "must_distinguish"
REDEFINES = "redefines"
ORGANIZES = "organizes"

# === Critique Edges ===
CHALLENGES_METHOD = "challenges_method"
CHALLENGES_PARADIGM = "challenges_paradigm"
PROPOSES_BETTER_METHOD = "proposes_better_method"

# === Attribution Edges ===
ATTRIBUTES_FINDING = "attributes_finding"
INTERPRETS_AS = "interprets_as"
```

**Test**:
```python
from src.epistemic.edge_types import EdgeType  # or wherever defined
assert EdgeType.THEORETICALLY_PREDICTS.value == "theoretically_predicts"
assert EdgeType.CONFIRMS_PREDICTION.value == "confirms_prediction"
assert EdgeType.CHALLENGES_METHOD.value == "challenges_method"
```

**Commit**: `[Sprint 6a / Task 6a.2] Add 19 new edge types for non-empirical integration`

---

### Task 6a.3: Create ae.claim.v2 schema

**Do**: Create `contracts/schemas/ae_claim_v2.schema.json` with the universal ingestion contract from spec §6.2:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ae.claim.v2",
  "title": "Article Eater Claim V2",
  "description": "Universal node ingestion contract for all node types",
  "type": "object",
  "required": ["node_id", "node_type", "paper_id", "statement", "ae_confidence", "provenance_tier", "evidence_level"],
  "properties": {
    "node_id": { "type": "string" },
    "node_type": { "type": "string", "enum": ["empirical_finding", "synthesis_conclusion", "qualitative_finding", "theoretical_proposition", "derived_hypothesis", "conceptual_definition", "conceptual_constraint", "expert_synthesis", "methodological_critique", "knowledge_gap", "framework_structure", "bridge_warrant"] },
    "paper_id": { "type": "string" },
    "statement": { "type": "string" },
    "ae_confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "provenance_tier": { "type": "string", "enum": ["abstract_provisional", "pdf_confirmed"] },
    "evidence_level": { "type": "string" },
    "source_section": { "type": "string" },
    "source_page_start": { "type": ["integer", "null"] },
    "source_page_end": { "type": ["integer", "null"] },
    "source_quote": { "type": "string" },
    "source_quote_hash": { "type": "string" },

    "study_design": { "type": "string" },
    "sample_size": { "type": ["integer", "null"] },
    "effect_size": { "type": ["number", "null"] },
    "effect_size_type": { "type": "string" },
    "confidence_interval": { "type": "array" },
    "p_value": { "type": ["number", "null"] },
    "causal_level": { "type": "string", "enum": ["association", "intervention", "counterfactual"] },

    "derivation_chain": { "type": "array" },
    "scope_conditions": { "type": "array" },
    "testable": { "type": "boolean" },
    "falsifiable": { "type": "boolean" },

    "author_expertise": { "type": "string" },
    "evidence_basis": { "type": "string", "enum": ["cited_evidence", "expert_opinion", "consensus"] },
    "n_studies_cited": { "type": ["integer", "null"] },
    "declared_bias": { "type": "string" },

    "argument_scheme": { "type": "string" },
    "critical_questions": { "type": "array" },
    "critical_questions_addressed": { "type": "array" },
    "critical_questions_unaddressed": { "type": "array" },
    "contrast_class": { "type": "string" },
    "difference_maker": { "type": "string" },

    "extraction_difficulty": { "type": "string", "enum": ["easy", "moderate", "hard"] },
    "source_zone": { "type": "string" },
    "article_type_family": { "type": "string" },
    "template_version": { "type": "string" }
  }
}
```

Also create the Python dataclass `src/epistemic/contracts/claim_v2.py`.

**Test**:
```python
from src.epistemic.contracts.claim_v2 import ClaimV2
claim = ClaimV2(
    node_id="test_001",
    node_type="theoretical_proposition",
    paper_id="paper_001",
    statement="Test proposition",
    ae_confidence=0.5,
    provenance_tier="abstract_provisional",
    evidence_level="abstract_finding_rule"
)
assert claim.node_type == "theoretical_proposition"
```

**Commit**: `[Sprint 6a / Task 6a.3] Create ae.claim.v2 schema and dataclass`

---

### Task 6a.4: Create ae.edge.v2 schema

**Do**: Create `contracts/schemas/ae_edge_v2.schema.json` with the edge ingestion contract from spec §6.3:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ae.edge.v2",
  "title": "Article Eater Edge V2",
  "description": "Universal edge ingestion contract",
  "type": "object",
  "required": ["edge_id", "edge_type", "source_node_id", "target_node_id", "weight", "paper_id"],
  "properties": {
    "edge_id": { "type": "string" },
    "edge_type": { "type": "string" },
    "source_node_id": { "type": "string" },
    "target_node_id": { "type": "string" },
    "weight": { "type": "number", "minimum": 0, "maximum": 1 },
    "paper_id": { "type": "string" },
    "evidence_basis": { "type": "string", "enum": ["explicit_statement", "implicit_connection", "reviewer_interpretation"] },
    "justification": { "type": "string" },
    "provenance_tier": { "type": "string" },
    "needs_verification": { "type": "boolean", "default": false }
  }
}
```

Also create the Python dataclass `src/epistemic/contracts/edge_v2.py`.

**Test**:
```python
from src.epistemic.contracts.edge_v2 import EdgeV2
edge = EdgeV2(
    edge_id="edge_001",
    edge_type="theoretically_predicts",
    source_node_id="prop_001",
    target_node_id="hyp_001",
    weight=0.8,
    paper_id="paper_001"
)
assert edge.edge_type == "theoretically_predicts"
```

**Commit**: `[Sprint 6a / Task 6a.4] Create ae.edge.v2 schema and dataclass`

---

### Task 6a.5: Add node type → template family mapping validation

**Do**: Create `src/epistemic/validation/node_template_mapping.py` implementing the compatibility matrix from spec Appendix A:

```python
NODE_TYPE_TEMPLATE_MAP = {
    "empirical_v2": ["empirical_finding"],
    "meta_analysis": ["synthesis_conclusion", "knowledge_gap"],
    "systematic_review": ["synthesis_conclusion", "methodological_critique", "knowledge_gap"],
    "narrative_review": ["expert_synthesis", "knowledge_gap", "bridge_warrant"],
    "theoretical": ["theoretical_proposition", "derived_hypothesis", "conceptual_definition", "bridge_warrant"],
    "conceptual_framework": ["conceptual_definition", "conceptual_constraint", "framework_structure"],
    "mixed_methods": ["empirical_finding", "qualitative_finding", "bridge_warrant"],
    "observational_field": ["empirical_finding"],
    "case_study": ["empirical_finding", "derived_hypothesis", "bridge_warrant"],
    "interview_study": ["qualitative_finding"],
    "ethnographic": ["qualitative_finding", "conceptual_definition"],
    "grounded_theory": ["qualitative_finding", "derived_hypothesis"],
    "phenomenological": ["qualitative_finding"],
    "thought_piece": ["expert_synthesis", "methodological_critique", "knowledge_gap"],
}

def validate_node_for_template(node_type: str, template_family: str) -> bool:
    """Check if node_type is valid for the given template_family."""
    valid_types = NODE_TYPE_TEMPLATE_MAP.get(template_family, [])
    return node_type in valid_types
```

**Test**:
```python
from src.epistemic.validation.node_template_mapping import validate_node_for_template
assert validate_node_for_template("theoretical_proposition", "theoretical") == True
assert validate_node_for_template("empirical_finding", "theoretical") == False
assert validate_node_for_template("synthesis_conclusion", "meta_analysis") == True
```

**Commit**: `[Sprint 6a / Task 6a.5] Add node type → template family mapping validation`

---

## Sprint 6b: Entrenchment Dynamics (2 weeks)

### Task 6b.1: Create entrenchment computation module

**Do**: Create `src/epistemic/entrenchment/node_type_entrenchment.py` with base entrenchment computation per node type (spec §4.2):

```python
from dataclasses import dataclass
from typing import Optional
from src.epistemic.node_types import NodeType

@dataclass
class EntrenchmentParams:
    """Parameters affecting entrenchment computation."""
    heterogeneity_i2: Optional[float] = None  # For SYNTHESIS_CONCLUSION
    publication_bias: Optional[str] = None     # For SYNTHESIS_CONCLUSION
    grade_quality: Optional[str] = None        # For SYNTHESIS_CONCLUSION
    argument_quality: Optional[str] = None     # For THEORETICAL_PROPOSITION
    evidential_grounding: Optional[str] = None
    testability: Optional[str] = None
    convergence_level: Optional[float] = None  # For QUALITATIVE_FINDING
    author_expertise: Optional[str] = None     # For EXPERT_SYNTHESIS

BASE_ENTRENCHMENT = {
    NodeType.EMPIRICAL_FINDING: 0.50,       # From source_quality
    NodeType.SYNTHESIS_CONCLUSION: 0.75,     # High base, modifiers apply
    NodeType.QUALITATIVE_FINDING: 0.50,      # Midpoint of 0.40-0.60
    NodeType.THEORETICAL_PROPOSITION: 0.35,  # Low base, gains from predictions
    NodeType.DERIVED_HYPOTHESIS: 0.35,       # Inherits from parent
    NodeType.CONCEPTUAL_DEFINITION: 0.80,    # High (definitions are confident)
    NodeType.CONCEPTUAL_CONSTRAINT: 0.70,    # Midpoint of 0.60-0.85
    NodeType.EXPERT_SYNTHESIS: 0.45,         # Low (non-systematic)
    NodeType.METHODOLOGICAL_CRITIQUE: 0.55,  # Midpoint of 0.40-0.70
    NodeType.KNOWLEDGE_GAP: None,            # N/A - gaps don't have entrenchment
    NodeType.FRAMEWORK_STRUCTURE: 0.75,      # Midpoint of 0.65-0.85
    NodeType.BRIDGE_WARRANT: 0.45,           # Midpoint of 0.30-0.60
}

def compute_base_entrenchment(node_type: NodeType, params: EntrenchmentParams = None) -> Optional[float]:
    """Compute base entrenchment for a node type."""
    if node_type == NodeType.KNOWLEDGE_GAP:
        return None

    base = BASE_ENTRENCHMENT.get(node_type, 0.50)

    if params is None:
        return base

    # Apply modifiers based on node type
    # ... (implement per-type modifiers from spec §4.2)

    return max(0.0, min(1.0, base))
```

**Test**:
```python
from src.epistemic.entrenchment.node_type_entrenchment import compute_base_entrenchment, NodeType
assert compute_base_entrenchment(NodeType.SYNTHESIS_CONCLUSION) == 0.75
assert compute_base_entrenchment(NodeType.THEORETICAL_PROPOSITION) == 0.35
assert compute_base_entrenchment(NodeType.KNOWLEDGE_GAP) is None
```

**Commit**: `[Sprint 6b / Task 6b.1] Create entrenchment computation module with base values`

---

### Task 6b.2: Implement asymmetric Popperian updating for THEORETICAL_PROPOSITION

**Do**: In `src/epistemic/entrenchment/theory_updating.py`, implement asymmetric confirmation/disconfirmation:

```python
CONFIRMATION_BONUS = 0.05    # Per confirmed prediction
DISCONFIRMATION_PENALTY = 0.10  # Per disconfirmed prediction (asymmetric!)

def update_theory_entrenchment(
    current_entrenchment: float,
    confirmations: int,
    disconfirmations: int
) -> float:
    """
    Update theoretical proposition entrenchment based on prediction outcomes.

    Implements Popperian asymmetry: disconfirmation hurts more than
    confirmation helps. Per spec §4.2.
    """
    adjustment = (confirmations * CONFIRMATION_BONUS) - (disconfirmations * DISCONFIRMATION_PENALTY)
    new_entrenchment = current_entrenchment + adjustment
    return max(0.0, min(1.0, new_entrenchment))
```

**Test**:
```python
from src.epistemic.entrenchment.theory_updating import update_theory_entrenchment

# Confirmation raises entrenchment
assert update_theory_entrenchment(0.35, confirmations=1, disconfirmations=0) == 0.40

# Disconfirmation lowers more (asymmetric)
assert update_theory_entrenchment(0.35, confirmations=0, disconfirmations=1) == 0.25

# Net effect: 1 confirm + 1 disconfirm = net loss (Popperian)
assert update_theory_entrenchment(0.35, confirmations=1, disconfirmations=1) == 0.30
```

**Commit**: `[Sprint 6b / Task 6b.2] Implement asymmetric Popperian updating for theories`

---

### Task 6b.3: Implement METHODOLOGICAL_CRITIQUE propagation

**Do**: In `src/epistemic/entrenchment/critique_propagation.py`, implement validity penalty propagation to method registry:

```python
from src.methods.registry import MethodRegistry
from typing import List

def propagate_critique_to_registry(
    critique_target_method_id: str,
    critique_severity: float,
    affected_constructs: List[str],
    registry: MethodRegistry
) -> int:
    """
    Propagate methodological critique to method registry.

    Reduces construct_validity for all affected constructs.
    Returns count of affected methods.

    Per spec §4.2: "METHODOLOGICAL_CRITIQUEs have a PROPAGATION effect."
    """
    method = registry.get(critique_target_method_id)
    if method is None:
        return 0

    penalty = critique_severity * 0.2  # Scale critique to validity penalty

    for construct in affected_constructs:
        current = method.get_construct_validity(construct)
        method.set_construct_validity(construct, max(0.0, current - penalty))

    return 1
```

**Test**:
```python
from src.epistemic.entrenchment.critique_propagation import propagate_critique_to_registry
from src.methods.registry import MethodRegistry
from src.methods.seed_data import load_seed_entries

registry = MethodRegistry()
load_seed_entries(registry)

# Get initial validity
hrv = registry.get("hrv_time_domain")
initial_stress = hrv.get_construct_validity("stress")

# Apply critique
propagate_critique_to_registry(
    "hrv_time_domain",
    critique_severity=0.5,
    affected_constructs=["stress"],
    registry=registry
)

# Validity should be reduced
new_stress = hrv.get_construct_validity("stress")
assert new_stress < initial_stress
```

**Commit**: `[Sprint 6b / Task 6b.3] Implement methodological critique propagation to method registry`

---

### Task 6b.4: Implement prediction tracking ledger for DERIVED_HYPOTHESIS

**Do**: Create `src/epistemic/prediction_ledger.py`:

```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class PredictionLedgerEntry:
    """Tracks confirmation/disconfirmation of a derived hypothesis."""
    hypothesis_id: str
    hypothesis_text: str
    derived_from: str  # parent THEORETICAL_PROPOSITION id
    confirmed_by: List[str] = field(default_factory=list)
    disconfirmed_by: List[str] = field(default_factory=list)
    current_entrenchment: float = 0.35
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def confirmation_count(self) -> int:
        return len(self.confirmed_by)

    @property
    def disconfirmation_count(self) -> int:
        return len(self.disconfirmed_by)

    def add_confirmation(self, study_id: str) -> None:
        if study_id not in self.confirmed_by:
            self.confirmed_by.append(study_id)

    def add_disconfirmation(self, study_id: str) -> None:
        if study_id not in self.disconfirmed_by:
            self.disconfirmed_by.append(study_id)

class PredictionLedger:
    """Maintains prediction tracking for all derived hypotheses."""

    def __init__(self):
        self._entries: dict[str, PredictionLedgerEntry] = {}

    def register_hypothesis(self, hypothesis_id: str, text: str, parent_prop_id: str) -> None:
        self._entries[hypothesis_id] = PredictionLedgerEntry(
            hypothesis_id=hypothesis_id,
            hypothesis_text=text,
            derived_from=parent_prop_id
        )

    def record_confirmation(self, hypothesis_id: str, study_id: str) -> None:
        if hypothesis_id in self._entries:
            self._entries[hypothesis_id].add_confirmation(study_id)

    def record_disconfirmation(self, hypothesis_id: str, study_id: str) -> None:
        if hypothesis_id in self._entries:
            self._entries[hypothesis_id].add_disconfirmation(study_id)

    def get_entry(self, hypothesis_id: str) -> Optional[PredictionLedgerEntry]:
        return self._entries.get(hypothesis_id)
```

**Test**:
```python
from src.epistemic.prediction_ledger import PredictionLedger

ledger = PredictionLedger()
ledger.register_hypothesis("h1", "ART predicts nature restores attention", "art_prop_1")
ledger.record_confirmation("h1", "berman_2008")
ledger.record_confirmation("h1", "berto_2005")

entry = ledger.get_entry("h1")
assert entry.confirmation_count == 2
assert entry.disconfirmation_count == 0
```

**Commit**: `[Sprint 6b / Task 6b.4] Implement prediction tracking ledger`

---

### Task 6b.5: Implement SYNTHESIS_CONCLUSION floor rule

**Do**: In `src/epistemic/entrenchment/synthesis_rules.py`:

```python
from typing import List

def compute_synthesis_entrenchment(
    base_entrenchment: float,
    included_study_entrenchments: List[float],
    heterogeneity_i2: float = 0.0,
    publication_bias: str = "none"
) -> float:
    """
    Compute entrenchment for SYNTHESIS_CONCLUSION.

    Per spec §4.2: "A SYNTHESIS_CONCLUSION's entrenchment should ALWAYS be
    >= the median entrenchment of its included studies."
    """
    # Apply modifiers
    if heterogeneity_i2 > 75:
        base_entrenchment -= 0.15
    elif heterogeneity_i2 > 50:
        base_entrenchment -= 0.05

    if publication_bias == "significant":
        base_entrenchment -= 0.10
    elif publication_bias == "marginal":
        base_entrenchment -= 0.05

    # Floor rule: must be >= median of included studies
    if included_study_entrenchments:
        sorted_entrenchments = sorted(included_study_entrenchments)
        n = len(sorted_entrenchments)
        median = sorted_entrenchments[n // 2] if n % 2 == 1 else \
                 (sorted_entrenchments[n // 2 - 1] + sorted_entrenchments[n // 2]) / 2
        base_entrenchment = max(base_entrenchment, median)

    return max(0.0, min(1.0, base_entrenchment))
```

**Test**:
```python
from src.epistemic.entrenchment.synthesis_rules import compute_synthesis_entrenchment

# Floor rule: synthesis >= median of included studies
included = [0.3, 0.4, 0.5, 0.6, 0.7]  # median = 0.5
result = compute_synthesis_entrenchment(
    base_entrenchment=0.40,  # Lower than median
    included_study_entrenchments=included
)
assert result >= 0.5  # Floor kicks in
```

**Commit**: `[Sprint 6b / Task 6b.5] Implement SYNTHESIS_CONCLUSION floor rule`

---

### Task 6b.6: Implement EXPERT_SYNTHESIS discount factor

**Do**: In `src/epistemic/entrenchment/expert_discount.py`:

```python
EXPERT_SYNTHESIS_DISCOUNT = 0.7  # Configurable default

def apply_expert_synthesis_discount(
    equivalent_synthesis_entrenchment: float,
    discount_factor: float = EXPERT_SYNTHESIS_DISCOUNT
) -> float:
    """
    Apply discount to EXPERT_SYNTHESIS relative to equivalent SYNTHESIS_CONCLUSION.

    Per spec §4.2: "EXPERT_SYNTHESIS nodes are DISCOUNTED relative to
    SYNTHESIS_CONCLUSION nodes... default: 0.7 × equivalent systematic finding"
    """
    return equivalent_synthesis_entrenchment * discount_factor
```

**Test**:
```python
from src.epistemic.entrenchment.expert_discount import apply_expert_synthesis_discount

synthesis_entrenchment = 0.70
expert_entrenchment = apply_expert_synthesis_discount(synthesis_entrenchment)
assert expert_entrenchment == 0.49  # 0.70 * 0.7
assert expert_entrenchment < synthesis_entrenchment
```

**Commit**: `[Sprint 6b / Task 6b.6] Implement EXPERT_SYNTHESIS discount factor`

---

## Sprint 6c: Ingestion Pipeline (1 week)

### Task 6c.1: Update extraction_to_web.py for ae.claim.v2

**Do**: Update `src/services/extraction_to_web.py` to accept the ae.claim.v2 contract. Add field mapping from legacy fields:

```python
def normalize_claim_to_v2(claim: dict) -> dict:
    """
    Normalize claim from any source to ae.claim.v2 format.

    Fixes C1/C2 from gap audit: claim_text→statement, confidence→ae_confidence
    """
    return {
        "node_id": claim.get("node_id") or claim.get("claim_id") or claim.get("id"),
        "node_type": claim.get("node_type", "empirical_finding"),
        "paper_id": claim.get("paper_id"),
        "statement": claim.get("statement") or claim.get("claim_text") or claim.get("text"),
        "ae_confidence": claim.get("ae_confidence") or claim.get("confidence", 0.5),
        "provenance_tier": claim.get("provenance_tier", "abstract_provisional"),
        "evidence_level": claim.get("evidence_level", "unknown"),
        # ... map remaining fields
    }
```

**Test**:
```python
from src.services.extraction_to_web import normalize_claim_to_v2

# Legacy format
legacy = {"claim_id": "c1", "claim_text": "Nature reduces stress", "confidence": 0.7}
v2 = normalize_claim_to_v2(legacy)

assert v2["node_id"] == "c1"
assert v2["statement"] == "Nature reduces stress"
assert v2["ae_confidence"] == 0.7
```

**Commit**: `[Sprint 6c / Task 6c.1] Update extraction_to_web.py for ae.claim.v2 contract`

---

### Task 6c.2: Add node_type routing in ingestion

**Do**: Add routing logic that processes different node types differently:

```python
def route_node_by_type(claim: dict) -> str:
    """
    Determine processing path based on node_type.

    Returns handler name for this node type.
    """
    node_type = claim.get("node_type", "empirical_finding")

    routing = {
        "empirical_finding": "handle_evidence_node",
        "synthesis_conclusion": "handle_evidence_node",
        "qualitative_finding": "handle_evidence_node",
        "theoretical_proposition": "handle_structural_node",
        "derived_hypothesis": "handle_structural_node",
        "conceptual_definition": "handle_conceptual_node",
        "conceptual_constraint": "handle_conceptual_node",
        "expert_synthesis": "handle_interpretive_node",
        "methodological_critique": "handle_critique_node",
        "knowledge_gap": "handle_gap_node",
        "framework_structure": "handle_meta_node",
        "bridge_warrant": "handle_structural_node",
    }

    return routing.get(node_type, "handle_evidence_node")
```

**Test**:
```python
from src.services.extraction_to_web import route_node_by_type

assert route_node_by_type({"node_type": "theoretical_proposition"}) == "handle_structural_node"
assert route_node_by_type({"node_type": "methodological_critique"}) == "handle_critique_node"
assert route_node_by_type({"node_type": "synthesis_conclusion"}) == "handle_evidence_node"
```

**Commit**: `[Sprint 6c / Task 6c.2] Add node_type routing in ingestion pipeline`

---

### Task 6c.3: Add edge_type validation with compatibility matrix

**Do**: Create edge validation using the compatibility matrix from spec §3.3:

```python
from src.epistemic.node_types import NodeType

EDGE_COMPATIBILITY = {
    "includes_in_synthesis": {
        "valid_sources": ["synthesis_conclusion"],
        "valid_targets": ["empirical_finding"]
    },
    "theoretically_predicts": {
        "valid_sources": ["theoretical_proposition"],
        "valid_targets": ["derived_hypothesis"]
    },
    "confirms_prediction": {
        "valid_sources": ["empirical_finding", "synthesis_conclusion"],
        "valid_targets": ["derived_hypothesis"]
    },
    "disconfirms_prediction": {
        "valid_sources": ["empirical_finding", "synthesis_conclusion"],
        "valid_targets": ["derived_hypothesis"]
    },
    "challenges_method": {
        "valid_sources": ["methodological_critique"],
        "valid_targets": []  # Targets method_registry entries, not nodes
    },
    "must_distinguish": {
        "valid_sources": ["conceptual_constraint"],
        "valid_targets": []  # Targets construct pairs
    },
    # ... add remaining edge types
}

def validate_edge(edge_type: str, source_node_type: str, target_node_type: str) -> tuple[bool, str]:
    """Validate edge against compatibility matrix."""
    if edge_type not in EDGE_COMPATIBILITY:
        return True, "unknown_edge_type"  # Allow unknown types with warning

    compat = EDGE_COMPATIBILITY[edge_type]

    if source_node_type not in compat["valid_sources"]:
        return False, f"Invalid source type {source_node_type} for edge {edge_type}"

    if compat["valid_targets"] and target_node_type not in compat["valid_targets"]:
        return False, f"Invalid target type {target_node_type} for edge {edge_type}"

    return True, "valid"
```

**Test**:
```python
from src.epistemic.validation.edge_validation import validate_edge

valid, msg = validate_edge("theoretically_predicts", "theoretical_proposition", "derived_hypothesis")
assert valid == True

invalid, msg = validate_edge("theoretically_predicts", "empirical_finding", "derived_hypothesis")
assert invalid == False
```

**Commit**: `[Sprint 6c / Task 6c.3] Add edge_type validation with compatibility matrix`

---

## Sprint 6d: Monitor Updates (1 week)

### Task 6d.1: Update coherence audit for legitimate propagation

**Do**: Update `src/epistemic/monitors/coherence.py` to distinguish legitimate propagation from unexplained drift:

```python
def is_legitimate_propagation(
    node_id: str,
    entrenchment_change: float,
    prediction_ledger: PredictionLedger
) -> bool:
    """
    Check if entrenchment change is due to legitimate propagation.

    For THEORETICAL_PROPOSITIONs, entrenchment changes are legitimate
    if they flow through DERIVED_HYPOTHESIS confirmation/disconfirmation.
    """
    # Check if this node has hypotheses in the prediction ledger
    # that have recent confirmations/disconfirmations
    # ... implementation
    return True
```

**Test**: Existing coherence audit tests still pass, plus new tests for legitimate propagation.

**Commit**: `[Sprint 6d / Task 6d.1] Update coherence audit for legitimate propagation detection`

---

### Task 6d.2: Add review_dominance check to structural bias detection

**Do**: Update `src/epistemic/monitors/concentration.py`:

```python
def check_review_dominance(web: WebOfBelief, threshold: float = 0.3) -> dict:
    """
    Check if web structure is dominated by small number of review papers.

    Per spec §7.1: "Over-reliance on one influential review means the web
    inherits that reviewer's selection bias and interpretive framework."

    Returns dict with dominance score and dominant reviews if any.
    """
    # Count edges attributable to each review paper
    # Flag if any single review accounts for > threshold of edges
    pass
```

**Test**:
```python
# Web where one review contributes 40% of edges should be flagged
result = check_review_dominance(web)
if result["dominance_score"] > 0.3:
    assert len(result["dominant_reviews"]) > 0
```

**Commit**: `[Sprint 6d / Task 6d.2] Add review_dominance check to structural bias detection`

---

### Task 6d.3: Add theory-without-predictions check

**Do**: Update `src/epistemic/monitors/entrenchment.py`:

```python
def check_theory_without_predictions(web: WebOfBelief, prediction_ledger: PredictionLedger) -> list:
    """
    Flag THEORETICAL_PROPOSITIONs with high entrenchment but few confirmed predictions.

    Per spec §7.1: "a theory that's entrenched purely by coherence with other
    theories, without empirical grounding, is epistemically suspect."
    """
    flagged = []
    for node in web.get_nodes_by_type("theoretical_proposition"):
        if node.entrenchment > 0.5:
            # Check for derived hypotheses with confirmations
            hypotheses = web.get_children_by_edge_type(node.id, "theoretically_predicts")
            total_confirmations = sum(
                prediction_ledger.get_entry(h.id).confirmation_count
                for h in hypotheses if prediction_ledger.get_entry(h.id)
            )
            if total_confirmations == 0:
                flagged.append(node.id)
    return flagged
```

**Test**:
```python
# Theory with 0.6 entrenchment but 0 confirmed predictions should be flagged
flagged = check_theory_without_predictions(web, ledger)
assert "ungrounded_theory_001" in flagged
```

**Commit**: `[Sprint 6d / Task 6d.3] Add theory-without-predictions check`

---

### Task 6d.4: Update adversarial review for single-review-removal fragility

**Do**: Update `src/epistemic/monitors/adversarial.py`:

```python
def test_single_review_removal(web: WebOfBelief, review_paper_id: str) -> dict:
    """
    Test what happens if a single influential review is removed.

    Returns dict with fragility metrics.
    """
    # Remove all nodes and edges attributed to this review
    # Compute: % of edges lost, % of nodes orphaned, coherence change
    pass
```

**Test**:
```python
result = test_single_review_removal(web, "influential_review_001")
assert "edges_lost_pct" in result
assert "orphaned_nodes" in result
```

**Commit**: `[Sprint 6d / Task 6d.4] Add single-review-removal fragility test`

---

## Sprint 6e: Integration Tests (1 week)

### Task 6e.1: Test Joye & Dewitte produces expected nodes/edges

**Do**: Create `tests/test_sprint6_integration.py` with test fixture:

```python
def test_joye_dewitte_produces_expected_structure():
    """
    Per spec Appendix B: Joye & Dewitte (2018) should produce ~8 nodes and ~15 edges.
    """
    # Load or simulate Joye & Dewitte extraction
    nodes, edges = extract_paper("joye_dewitte_2018")

    assert len(nodes) >= 6  # Allow some variance
    assert len(edges) >= 10

    # Check expected node types are present
    node_types = {n.node_type for n in nodes}
    assert "theoretical_proposition" in node_types
    assert "derived_hypothesis" in node_types
    assert "expert_synthesis" in node_types
```

**Test**: Test passes when run against Joye & Dewitte extraction.

**Commit**: `[Sprint 6e / Task 6e.1] Test Joye & Dewitte paper produces expected web structure`

---

### Task 6e.2: Test METHODOLOGICAL_CRITIQUE propagation

**Do**:
```python
def test_critique_propagates_to_affected_studies():
    """METHODOLOGICAL_CRITIQUE should reduce validity for all studies using criticized method."""
    # Create critique node
    # Add studies using the criticized method
    # Verify validity is reduced for all affected studies
    pass
```

**Commit**: `[Sprint 6e / Task 6e.2] Test methodological critique propagation`

---

### Task 6e.3: Test THEORETICAL_PROPOSITION asymmetric updating

**Do**:
```python
def test_theory_asymmetric_updating():
    """Disconfirmation should hurt more than confirmation helps (Popperian)."""
    # Start with base entrenchment
    # Add 1 confirmation: +0.05
    # Add 1 disconfirmation: -0.10
    # Net: -0.05 (asymmetric)
    pass
```

**Commit**: `[Sprint 6e / Task 6e.3] Test asymmetric Popperian updating for theories`

---

### Task 6e.4: Test SYNTHESIS_CONCLUSION floor rule

**Do**:
```python
def test_synthesis_floor_rule():
    """SYNTHESIS_CONCLUSION entrenchment >= median of included studies."""
    included = [0.3, 0.4, 0.5, 0.6, 0.7]  # median = 0.5
    synthesis = create_synthesis(included_studies=included)

    assert synthesis.entrenchment >= 0.5
```

**Commit**: `[Sprint 6e / Task 6e.4] Test SYNTHESIS_CONCLUSION floor rule`

---

### Task 6e.5: Test EXPERT_SYNTHESIS discount

**Do**:
```python
def test_expert_synthesis_discount():
    """EXPERT_SYNTHESIS < equivalent SYNTHESIS_CONCLUSION."""
    systematic = create_synthesis_conclusion(entrenchment=0.70)
    narrative = create_expert_synthesis(equivalent_to=systematic)

    assert narrative.entrenchment < systematic.entrenchment
    assert narrative.entrenchment == pytest.approx(0.49, abs=0.01)  # 0.7 * 0.7
```

**Commit**: `[Sprint 6e / Task 6e.5] Test EXPERT_SYNTHESIS discount factor`

---

### Task 6e.6: Test CONCEPTUAL_CONSTRAINT validation warning

**Do**:
```python
def test_conceptual_constraint_fires_warning():
    """CONCEPTUAL_CONSTRAINT should fire warning when terms are conflated."""
    # Add constraint: must distinguish "restoration" from "relaxation"
    # Try to add claim conflating them
    # Verify warning is generated
    pass
```

**Commit**: `[Sprint 6e / Task 6e.6] Test CONCEPTUAL_CONSTRAINT validation warning`

---

### Task 6e.7: Integration test with mixed corpus

**Do**:
```python
def test_mixed_corpus_produces_coherent_web():
    """Mixed corpus (empirical + theoretical + review) should produce coherent web."""
    corpus = load_test_corpus("mixed_paper_types")  # ~10 papers of different types

    web = WebOfBelief()
    for paper in corpus:
        nodes, edges = extract_paper(paper)
        for node in nodes:
            web.add_node(node)
        for edge in edges:
            web.add_edge(edge)

    # Coherence should be computed without errors
    coherence = web.compute_coherence()
    assert coherence > 0

    # Should have multiple node types
    node_types = web.get_node_type_distribution()
    assert len(node_types) >= 4
```

**Commit**: `[Sprint 6e / Task 6e.7] Integration test with mixed paper type corpus`

---

## Sprint 6 Summary

| Sprint | Focus | Tasks | Duration |
|--------|-------|-------|----------|
| 6a | Schema Extensions | 6a.1–6a.5 | 1 week |
| 6b | Entrenchment Dynamics | 6b.1–6b.6 | 2 weeks |
| 6c | Ingestion Pipeline | 6c.1–6c.3 | 1 week |
| 6d | Monitor Updates | 6d.1–6d.4 | 1 week |
| 6e | Integration Tests | 6e.1–6e.7 | 1 week |

**Total**: 25 tasks across 5 sub-sprints (6 weeks)

---

## Dependencies

```
Sprint 1 (Schema Extensions) ───┐
                                 ├──► Sprint 6a ──► 6b ──► 6c ──► 6d ──► 6e
Sprint 4b (Method Registry) ────┘
```

**Note**: Sprint 6 can begin after Sprint 5 (Integration Testing) is complete.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| All Sprint 6 tests pass | 100% |
| Non-empirical papers produce nodes | >90% extraction rate |
| Node type coverage | All 12 types used |
| Edge type coverage | All 19 new types tested |
| No regression in existing tests | 100% pass |

---

*Sprint 6 plan ready for execution.*
*Depends on: Sprint 1, Sprint 4b*
*Reference: Non_Empirical_Web_Integration_Spec_V1.0.md*
