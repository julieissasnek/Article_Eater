# QA Agent Implementation Plan

**Date**: February 16, 2026
**Status**: DRAFT — For review
**Source**: QA Agent Specification + Amendments 1-17 + Tier 2 Construct Map

---

## Executive Summary

The QA Agent specification revealed requirements at multiple system levels. This plan separates:
- **Web-level work** (knowledge representation)
- **Network structure work** (indices, graphs, registries)
- **Molecule-level work** (composite constructs)
- **QA-level work** (query routing and answer generation)
- **BN-level work** (quantitative parameters)

Key insights:
1. **Molecules**: Composite constructs (ART, SRT, Prospect-Refuge) are pre-defined, not computed at query time
2. **Network indices**: Templates have implicit structure (domains, frameworks, interactions) that needs explicit indexing
3. **Dual-layer**: Templates have theory, BN has parameters — QA must query both appropriately

**Total effort**: ~106 hours across 7 phases over ~16 calendar days (with parallelization)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        QA AGENT LAYER                           │
│  Query Classification → Routing → Answer Generation → Response  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ queries
┌─────────────────────────────────────────────────────────────────┐
│                      MOLECULE LAYER (NEW)                       │
│  Tier 2 Constructs: ART, SRT, Prospect-Refuge, Biophilia, ...  │
│  Each molecule = {templates[], interactions[], scope, evidence} │
└─────────────────────────────────────────────────────────────────┘
                              ↓ composed of
┌─────────────────────────────────────────────────────────────────┐
│                      TEMPLATE LAYER (Tier 1)                    │
│  Atomic elements: T1-T58, VF1-3, COL1-2, M1-17, SC1-4, etc.    │
│  ~150 templates organized by domain                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ parameters from
┌─────────────────────────────────────────────────────────────────┐
│                      BN MECHANISM LAYER                         │
│  Quantitative: effect sizes, goldilocks, confidence intervals  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Molecule Layer Formalization

**Owner**: Web/Template team (antigravity thread)
**Dependency**: Templates stable (✓ complete)
**Output**: `molecules/` directory with formalized construct definitions

### 1.1 Molecule Schema Definition

```python
@dataclass
class Molecule:
    """Tier 2 composite construct."""

    molecule_id: str  # e.g., "ART", "SRT", "PROSPECT_REFUGE"
    name: str
    short_description: str

    # Composition
    components: List[MoleculeComponent]  # Named sub-parts
    constituent_templates: List[str]  # All template IDs involved

    # Structure
    interaction_graph: Dict[str, Dict[str, InteractionType]]  # template → template → type
    component_hierarchy: Optional[Dict]  # e.g., ART has 4 sub-components

    # Metadata
    framework_ids: List[str]  # Tier 1 frameworks this instantiates
    domain: str  # e.g., "restoration", "safety", "aesthetics"
    scope_conditions: List[str]
    overall_maturity: str

    # Evidence
    key_references: List[Reference]
    empirical_support: str  # "established", "supported", "preliminary"

@dataclass
class MoleculeComponent:
    """Named sub-part of a molecule."""

    name: str  # e.g., "Soft Fascination", "Being Away"
    template_ids: List[str]
    interaction_type: InteractionType  # How templates combine
    description: str
```

### 1.2 Initial Molecule Definitions (from tier2_construct_map)

| Molecule | Components | Templates |
|----------|------------|-----------|
| **ART** | Soft Fascination, Being Away, Extent, Compatibility | T27, T31, T2, T23, T29, T3, T14(neg), T8, T1, T37 |
| **SRT** | Immediate Affect, Parasympathetic, Cortisol Reduction | T9, T22, T8, T12, T5 |
| **Prospect-Refuge** | Prospect, Refuge | T3, T5 (interaction) |
| **Biophilia** | Fractal Fluency, Complexity | T1, T2 |
| **Nature View Convergence** | 5 channels | T1, SC2, T25, L5, T5 (VIEW1 already defines this) |
| **Privacy Regulation** | 5 mechanisms | SOC2 (already a single template but complex) |
| **Circadian Health** | Light pathway | L2, T29 |
| **Architectural Promenade** | Threshold sequence | SC3, L1, MAT3, AX1, AX3, AX6 |

### 1.3 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| M1.1 | Define molecule schema (dataclass) | 2h | — |
| M1.2 | Create `molecules/` directory structure | 1h | M1.1 |
| M1.3 | Formalize ART molecule | 3h | M1.2 |
| M1.4 | Formalize SRT molecule | 2h | M1.2 |
| M1.5 | Formalize Prospect-Refuge molecule | 2h | M1.2 |
| M1.6 | Formalize Biophilia molecule | 2h | M1.2 |
| M1.7 | Audit remaining constructs for molecule candidates | 4h | M1.3-M1.6 |
| M1.8 | Create molecule registry (index) | 2h | M1.7 |
| M1.9 | Define molecule↔template validation | 2h | M1.8 |

**Total Phase 1**: ~20 hours

---

## Phase 2: Template-to-Molecule Bridging

**Owner**: Web/Template team
**Dependency**: Phase 1 complete
**Output**: Bidirectional links between templates and molecules

### 2.1 Template Enhancement

Add to each template:
```json
{
  "template_id": "T27",
  "participates_in_molecules": [
    {
      "molecule_id": "ART",
      "component": "Soft Fascination",
      "role": "DMN re-engagement mechanism"
    }
  ]
}
```

### 2.2 Molecule Validation

Ensure all template references in molecules resolve:
```python
def validate_molecule(molecule: Molecule) -> List[ValidationError]:
    errors = []
    for template_id in molecule.constituent_templates:
        if not template_exists(template_id):
            errors.append(f"Template {template_id} not found")
        else:
            template = load_template(template_id)
            if molecule.molecule_id not in template.get("participates_in_molecules", []):
                errors.append(f"Template {template_id} missing back-reference to {molecule.molecule_id}")
    return errors
```

### 2.3 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| M2.1 | Add `participates_in_molecules` field to template schema | 1h | Phase 1 |
| M2.2 | Update templates with molecule back-references | 4h | M2.1 |
| M2.3 | Create validation script | 2h | M2.2 |
| M2.4 | Run validation, fix inconsistencies | 3h | M2.3 |

**Total Phase 2**: ~10 hours

---

## Phase 3: QA Query Routing

**Owner**: QA Agent team
**Dependency**: Phase 2 complete
**Output**: Query router that knows about molecules

### 3.1 Query Type → Target Mapping

| Query Pattern | Target | Example |
|---------------|--------|---------|
| "What is [construct]?" | Molecule lookup | "What is ART?" → ART molecule |
| "How does [component] work?" | Sub-molecule | "How does soft fascination work?" → ART.soft_fascination |
| "Why does [X] affect [Y]?" | Template causal chain | "Why do curves feel safe?" → VF1 causal links |
| "Does [X] reduce stress?" | Molecule match | Maps to SRT or ART depending on X |
| "What's the optimal [param]?" | BN mechanism | Goldilocks lookup |
| "Design [context] for [outcome]" | Multi-molecule synthesis | Relevant molecules for context |

### 3.2 Molecule-Aware Router

```python
class MoleculeAwareRouter:
    """Routes queries to appropriate knowledge layer."""

    def __init__(self):
        self.molecule_registry = load_molecule_registry()
        self.template_index = load_template_index()
        self.mechanism_registry = load_mechanism_registry()

    def route(self, question: ClassifiedQuestion) -> QueryPlan:

        # Check for molecule-level queries first
        if question.mentions_construct():
            construct = question.extract_construct()
            if construct in self.molecule_registry:
                return QueryPlan(
                    target="molecule",
                    molecule_id=construct,
                    depth=question.requested_depth
                )

        # Check for component-level queries
        if question.mentions_component():
            component = question.extract_component()
            molecule, comp = self.find_component(component)
            if molecule:
                return QueryPlan(
                    target="molecule_component",
                    molecule_id=molecule,
                    component=comp
                )

        # Fall back to template/mechanism routing (Amendment 11)
        if question.type in [WHY, MECHANISM, THEORY]:
            return QueryPlan(target="templates", ...)
        elif question.type in [EFFECT_SIZE, OPTIMAL]:
            return QueryPlan(target="mechanisms", ...)

        # Design questions → multi-molecule synthesis
        if question.type == DESIGN:
            relevant_molecules = self.find_molecules_for_context(question.context)
            return QueryPlan(
                target="molecule_synthesis",
                molecules=relevant_molecules
            )
```

### 3.3 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| Q3.1 | Implement MoleculeAwareRouter | 4h | Phase 2 |
| Q3.2 | Add construct/component detection to question classifier | 3h | Q3.1 |
| Q3.3 | Implement molecule lookup response generator | 3h | Q3.2 |
| Q3.4 | Implement component lookup response generator | 2h | Q3.3 |
| Q3.5 | Implement multi-molecule synthesis | 4h | Q3.4 |
| Q3.6 | Integration tests | 4h | Q3.5 |

**Total Phase 3**: ~20 hours

---

## Phase 4: Amendment Revision

**Owner**: QA Agent team
**Dependency**: Phase 3 complete
**Output**: Revised amendments that leverage molecule layer

### 4.1 Amendments That Change

| Amendment | Original | Revised |
|-----------|----------|---------|
| **12: Multi-Template Synthesis** | On-the-fly synthesis | Molecule retrieval + gap synthesis |
| **13: Hierarchy Extraction** | Extract from templates | Also extract from molecules |
| **14: Context → Parameter** | Direct mapping | Context → relevant molecules → parameters |
| **16: Interaction Classification** | Compute at query time | Pre-defined in molecule schema |

### 4.2 Amendments That Stay

| Amendment | Why Unchanged |
|-----------|---------------|
| 10: Taxonomic Expansion | Still needed for domain siblings |
| 11: Dual-Layer Architecture | Still applies (templates vs mechanisms) |
| 15: Population Adjustment | Still needed at parameter level |
| 17: Confidence Chain | Still needed for causal explanations |

### 4.3 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| Q4.1 | Revise Amendment 12 for molecule layer | 2h | Phase 3 |
| Q4.2 | Revise Amendment 13 for molecule hierarchies | 1h | Phase 3 |
| Q4.3 | Revise Amendment 14 for molecule routing | 1h | Phase 3 |
| Q4.4 | Revise Amendment 16 with molecule interactions | 2h | Phase 3 |
| Q4.5 | Update amendments document | 2h | Q4.1-Q4.4 |

**Total Phase 4**: ~8 hours

---

## Phase 5: BN Integration

**Owner**: BN team
**Dependency**: Phase 1 complete (can run in parallel with 2-4)
**Output**: Molecule-level parameters in BN

### 5.1 Molecule → BN Mapping

Currently BN has attribute→mediator→outcome edges. Need to add:
- Molecule-level aggregate parameters
- Which mechanisms contribute to which molecules

```python
@dataclass
class MoleculeBNMapping:
    """Links molecule to BN parameters."""

    molecule_id: str
    relevant_edges: List[str]  # BN edge IDs
    aggregate_effect_size: Optional[float]  # Combined effect
    aggregate_confidence: float  # Based on constituent template maturities
```

### 5.2 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| B5.1 | Define MoleculeBNMapping schema | 2h | Phase 1 |
| B5.2 | Map ART to BN edges | 2h | B5.1 |
| B5.3 | Map SRT to BN edges | 2h | B5.2 |
| B5.4 | Map remaining molecules | 4h | B5.3 |
| B5.5 | Implement aggregate parameter computation | 3h | B5.4 |

**Total Phase 5**: ~13 hours

---

## Dependency Graph

```
Phase 1: Molecule Formalization
    │
    ├──────────────────┬────────────────────┐
    ↓                  ↓                    ↓
Phase 2: Bridging   Phase 5: BN Integration
    │                  │
    ↓                  │
Phase 3: QA Routing ←──┘
    │
    ↓
Phase 4: Amendment Revision
    │
    ↓
  DONE
```

**Critical path**: Phase 1 → Phase 2 → Phase 3 → Phase 4

**Parallel track**: Phase 5 can run alongside Phases 2-4

---

## Timeline Estimate

| Phase | Hours | Calendar (assuming 4h/day) |
|-------|-------|---------------------------|
| Phase 1: Molecules | 20h | 5 days |
| Phase 2: Bridging | 10h | 2.5 days |
| Phase 3: QA Routing | 20h | 5 days |
| Phase 4: Amendments | 8h | 2 days |
| Phase 5: BN (parallel) | 13h | 3 days |

**Total**: ~58 hours over ~14.5 calendar days (with Phase 5 parallel)

---

## Phase 6: Network Design Features

**Owner**: Web/Architecture team
**Dependency**: Can start in parallel with Phase 1
**Output**: Structural enhancements to the template network

These features were revealed by QA testing but aren't about molecules — they're about the template network itself.

### 6.1 Domain Index (Amendment 10, 11)

Templates are implicitly organized by domain (prefix conventions), but no formal index exists.

```python
@dataclass
class DomainIndex:
    """First-class index of templates by domain."""

    domains: Dict[str, DomainEntry]

@dataclass
class DomainEntry:
    domain_id: str  # e.g., "acoustic", "color", "spatial"
    display_name: str
    template_prefixes: List[str]  # e.g., ["T58", "AUD_", "T19", "T31"]
    template_ids: List[str]  # All templates in domain
    sibling_domains: List[str]  # Related domains for expansion
    parent_domain: Optional[str]  # Hierarchy (sensory > acoustic)
```

**Why needed**: Amendment 10 (Taxonomic Expansion) requires finding domain siblings. Currently requires pattern matching on prefixes.

### 6.2 Framework Index (Shared Theory Detection)

Templates declare `framework_ids` but no index maps frameworks to templates.

```python
@dataclass
class FrameworkIndex:
    """Maps Tier 1 frameworks to templates that instantiate them."""

    frameworks: Dict[str, FrameworkEntry]

@dataclass
class FrameworkEntry:
    framework_id: str  # e.g., "PP", "ART", "BRECVEMA"
    full_name: str
    instantiating_templates: List[str]
    core_templates: List[str]  # Primary vs peripheral
    key_constructs: List[str]  # Main theoretical constructs
```

**Why needed**: Amendment 6 (Shared Theory Detection) requires knowing which templates share frameworks. "Do wood and plants work the same way?" → check shared framework_ids.

### 6.3 Interaction Graph (Cross-Template)

Templates have `interactions` fields but no unified graph.

```python
@dataclass
class InteractionGraph:
    """Explicit edges between templates."""

    edges: List[InteractionEdge]

@dataclass
class InteractionEdge:
    from_template: str
    to_template: str
    interaction_type: str  # "ELABORATION", "CRITICAL_INPUT", "CONFLICT", etc.
    description: str
    bidirectional: bool
```

**Why needed**: Amendment 16 (Cross-Template Interaction) requires knowing how templates interact. Currently scattered in individual template `interactions` fields.

### 6.4 Moderator Registry (Population/Context)

Templates have `moderators` and `scope_conditions` but no unified registry.

```python
@dataclass
class ModeratorRegistry:
    """Population and context moderators across templates."""

    moderators: Dict[str, ModeratorEntry]

@dataclass
class ModeratorEntry:
    moderator_id: str  # e.g., "age", "introversion", "task_type"
    type: str  # "population", "context", "individual_difference"
    affects_templates: List[str]
    direction: str  # How it modifies effect
    has_quantitative_formula: bool
    formula: Optional[str]  # e.g., L2's age correction
```

**Why needed**: Amendment 15 (Population Adjustment) requires knowing which templates have population-specific parameters. Currently must scan all templates.

### 6.5 Hierarchy Registry (Explicit Orderings)

Templates contain hierarchies (COL2.arousal_dimensions, VIEW1.synthetic_hierarchy) but no index.

```python
@dataclass
class HierarchyRegistry:
    """Explicit orderings found in templates."""

    hierarchies: Dict[str, HierarchyEntry]

@dataclass
class HierarchyEntry:
    hierarchy_id: str
    source_template: str
    field_path: str
    items: List[str]  # Ordered
    ordering_criterion: str  # What the order represents
    direction: str  # "high_to_low", "best_to_worst", etc.
```

**Why needed**: Amendment 13 (Hierarchy Extraction) requires finding and presenting these. Currently must parse template content at query time.

### 6.6 Maturity Propagation Rules

Templates have `overall_maturity` but no rules for aggregating across:
- Causal chains (multiple links)
- Molecules (multiple templates)
- Domains (multiple templates)

```python
class MaturityPropagation:
    """Rules for aggregating maturity."""

    @staticmethod
    def chain_maturity(links: List[CausalLink]) -> str:
        """Weakest link rule for causal chains."""
        return min(links, key=lambda l: MATURITY_ORDER[l.bridging_quality])

    @staticmethod
    def molecule_maturity(templates: List[Template]) -> str:
        """Aggregate maturity for molecule."""
        # Option A: Weakest link
        # Option B: Weighted average
        # Option C: Mode (most common)
        pass

    @staticmethod
    def domain_maturity(templates: List[Template]) -> Dict[str, float]:
        """Maturity distribution for domain."""
        return Counter([t.overall_maturity for t in templates])
```

**Why needed**: Amendment 17 (Confidence Chain) and molecule-level queries require maturity aggregation.

### 6.7 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| N6.1 | Create DomainIndex from template prefixes | 3h | — |
| N6.2 | Create FrameworkIndex from framework_ids | 2h | — |
| N6.3 | Extract InteractionGraph from template interactions | 4h | — |
| N6.4 | Create ModeratorRegistry from template moderators | 3h | — |
| N6.5 | Create HierarchyRegistry from template content | 3h | — |
| N6.6 | Define MaturityPropagation rules | 2h | — |
| N6.7 | Create unified network index | 4h | N6.1-N6.6 |
| N6.8 | Validation: all templates indexed | 2h | N6.7 |

**Total Phase 6**: ~23 hours

---

## Phase 7: Query Optimization Indices

**Owner**: QA Agent team
**Dependency**: Phase 6 complete
**Output**: Optimized lookup structures for common query patterns

### 7.1 Outcome → Template Index

"What affects stress?" → Find all templates with stress-related outcomes.

```python
outcome_index: Dict[str, List[str]]  # outcome → template_ids
# e.g., {"stress": ["T5", "T29", "SOC2", "T58", ...]}
```

### 7.2 Attribute → Template Index

"What does ceiling height affect?" → Find all templates mentioning ceiling height.

```python
attribute_index: Dict[str, List[str]]  # attribute → template_ids
# e.g., {"ceiling_height": ["T3", "AX3", ...]}
```

### 7.3 Causal Path Index

Pre-computed paths between common attribute-outcome pairs.

```python
@dataclass
class CausalPathIndex:
    paths: Dict[Tuple[str, str], List[CausalPath]]  # (attribute, outcome) → paths
```

### 7.4 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| Q7.1 | Build outcome index | 3h | Phase 6 |
| Q7.2 | Build attribute index | 3h | Phase 6 |
| Q7.3 | Build causal path index (common pairs) | 4h | Q7.1, Q7.2 |
| Q7.4 | Query performance benchmarks | 2h | Q7.3 |

**Total Phase 7**: ~12 hours

---

## Revised Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        QA AGENT LAYER                           │
│  Query Classification → Routing → Answer Generation → Response  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ queries
┌─────────────────────────────────────────────────────────────────┐
│                       INDEX LAYER (Phase 7)                     │
│  DomainIndex, FrameworkIndex, OutcomeIndex, AttributeIndex     │
│  CausalPathIndex, HierarchyRegistry, ModeratorRegistry         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ lookups
┌─────────────────────────────────────────────────────────────────┐
│                      MOLECULE LAYER (Phase 1)                   │
│  Tier 2 Constructs: ART, SRT, Prospect-Refuge, Biophilia, ...  │
│  InteractionGraph between molecules                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ composed of
┌─────────────────────────────────────────────────────────────────┐
│                      TEMPLATE LAYER (Tier 1)                    │
│  Atomic elements: T1-T58, VF1-3, COL1-2, M1-17, SC1-4, etc.    │
│  InteractionGraph between templates                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ parameters from
┌─────────────────────────────────────────────────────────────────┐
│                      BN MECHANISM LAYER                         │
│  Quantitative: effect sizes, goldilocks, confidence intervals  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Revised Dependency Graph

```
Phase 1: Molecule Formalization ←──────┐
    │                                  │
    ├──────────────┐                   │
    ↓              ↓                   │
Phase 2        Phase 5                 │
Bridging       BN Integration          │
    │              │                   │
    ↓              │        Phase 6: Network Features
Phase 3: QA Routing ←──────────────────┤
    │                                  │
    ↓                                  ↓
Phase 4                    Phase 7: Query Indices
Amendment Revision                     │
    │                                  │
    └──────────────────────────────────┘
                    ↓
                  DONE
```

**Parallel tracks**:
- Phase 1 + Phase 6 (both can start immediately)
- Phase 5 + Phase 2 (once Phase 1 done)
- Phase 7 follows Phase 6

---

## Revised Timeline

| Phase | Hours | Calendar | Parallel? |
|-------|-------|----------|-----------|
| Phase 1: Molecules | 20h | 5 days | Start Day 1 |
| Phase 6: Network Features | 23h | 6 days | Start Day 1 (parallel) |
| Phase 2: Bridging | 10h | 2.5 days | After Phase 1 |
| Phase 5: BN Integration | 13h | 3 days | After Phase 1 (parallel) |
| Phase 7: Query Indices | 12h | 3 days | After Phase 6 |
| Phase 3: QA Routing | 20h | 5 days | After Phases 2, 6 |
| Phase 4: Amendments | 8h | 2 days | After Phase 3 |

**Total**: ~106 hours over ~16 calendar days (with parallelization)

---

## Open Questions

1. **Molecule granularity**: Is "ART" one molecule with 4 components, or 4 separate molecules that compose? Current plan: one molecule with named components.

2. **Template overlap**: T5 (Threat/HPA) participates in multiple molecules (ART, SRT, Prospect-Refuge). How to handle queries that span molecules?

3. **Emergent molecules**: Some template combinations aren't named constructs yet. Should we auto-detect candidate molecules from template interaction patterns?

4. **VIEW1 status**: VIEW1 (Nature View Convergence) already defines a 5-channel composition. Is it a template or a molecule? Current answer: it's a template that IS a molecule (self-documenting composite).

5. **Molecule maturity**: How to compute molecule maturity from constituent template maturities? Proposal: min(template maturities) for "weakest link" or weighted average.

---

## Success Criteria

- [ ] All Tier 2 constructs from construct_map formalized as molecules
- [ ] Bidirectional template↔molecule links validated
- [ ] QA router correctly identifies molecule-level queries
- [ ] "What is ART?" returns structured molecule response
- [ ] "Design a restorative hospital room" synthesizes relevant molecules
- [ ] Amendments 12, 13, 14, 16 revised for molecule layer
- [ ] BN has molecule-level aggregate parameters

---

## Files Created/Modified

| File | Action | Phase |
|------|--------|-------|
| `molecules/schema.py` | NEW | 1 |
| `molecules/art.json` | NEW | 1 |
| `molecules/srt.json` | NEW | 1 |
| `molecules/prospect_refuge.json` | NEW | 1 |
| `molecules/registry.json` | NEW | 1 |
| `data/templates/*.json` | MODIFY (add participates_in) | 2 |
| `src/qa/router.py` | NEW | 3 |
| `src/qa/molecule_responder.py` | NEW | 3 |
| `docs/QA_AGENT_SPECIFICATION_AMENDMENTS_*.md` | MODIFY | 4 |
| `src/mechanisms/molecule_bn_mapping.json` | NEW | 5 |

---

## Phase 8: Argument Structure & Aggregation Layer

**Owner**: Web/Epistemic team
**Dependency**: Phase 1 (molecules), Phase 6 (network indices)
**Output**: Paper-level argument relations, meta-analytic aggregation, hierarchy→aggregation bridge

### 8.1 Gap Analysis: What EXISTS vs What's NEEDED

**Currently Implemented** (belief-level):
- `argument_attack.py`: Belief vs belief attacks with contrast class analysis
- `argumentative.py`: Theory support/challenge extraction from single paper
- `critique_propagation.py`: Method critique propagation to registry

**Missing** (paper-level and aggregation):
- Paper-to-paper argumentative relations
- Meta-analytic effect size aggregation
- Replication tracking across papers
- Systematic critique collection per target paper
- Hierarchy → aggregation → generalization pathway

### 8.2 Paper-Level Argument Relations

Papers don't just contain beliefs — papers **argue** with each other. Need:

```python
@dataclass
class PaperRelation:
    """Argumentative relation between two papers."""

    relation_id: str
    source_paper_id: str  # The paper making the argument
    target_paper_id: str  # The paper being argued about
    relation_type: PaperRelationType

    # What aspect is being targeted
    target_aspect: str  # "method", "assumption", "interpretation", "stimulus", "population"
    specific_target: str  # e.g., "HRV measurement", "student sample", "stress interpretation"

    # The argument content
    critique_summary: str
    evidence_for_critique: List[str]  # Claims supporting the critique

    # Strength and outcome
    critique_strength: float  # 0-1
    resolved: bool  # Has this been addressed?
    resolution: Optional[str]  # How it was resolved

class PaperRelationType(Enum):
    """Types of inter-paper argument relations."""

    # Replication relations
    REPLICATES = "replicates"               # Directly reproduces finding
    FAILS_TO_REPLICATE = "fails_to_replicate"  # Attempted but failed
    EXTENDS = "extends"                      # Extends to new population/context

    # Critique relations
    CRITIQUES_METHOD = "critiques_method"    # Attacks methodology
    CRITIQUES_STIMULUS = "critiques_stimulus"  # Attacks stimulus validity
    CRITIQUES_POPULATION = "critiques_population"  # Questions generalizability
    CRITIQUES_ASSUMPTION = "critiques_assumption"  # Challenges tacit assumption
    CRITIQUES_INTERPRETATION = "critiques_interpretation"  # Different interpretation of same data
    CRITIQUES_STATISTICS = "critiques_statistics"  # Statistical analysis problems

    # Aggregation relations
    META_ANALYZES = "meta_analyzes"          # Quantitative synthesis
    REVIEWS = "reviews"                       # Narrative synthesis

    # Support relations
    CONFIRMS = "confirms"                     # Independent confirmation
    CITES_SUPPORTING = "cites_supporting"     # Cites as evidence
```

### 8.3 Critique Aggregator

Collect all critiques targeting a paper/belief/method:

```python
@dataclass
class CritiqueCollection:
    """All critiques targeting a specific paper, method, or assumption."""

    target_id: str  # Paper ID, method ID, or assumption ID
    target_type: str  # "paper", "method", "assumption", "claim"

    # Organized by critique type
    method_critiques: List[PaperRelation]
    stimulus_critiques: List[PaperRelation]
    population_critiques: List[PaperRelation]
    assumption_critiques: List[PaperRelation]
    interpretation_critiques: List[PaperRelation]
    statistical_critiques: List[PaperRelation]

    # Aggregated impact
    total_critique_count: int
    weighted_critique_severity: float  # Sum of critique_strength
    unresolved_count: int

    # Which aspects are most attacked?
    vulnerability_profile: Dict[str, float]  # aspect → total severity

class CritiqueAggregator:
    """Collects and summarizes all critiques of a target."""

    def collect_critiques(self, target_id: str) -> CritiqueCollection:
        """Find all papers that critique this target."""
        pass

    def vulnerability_report(self, target_id: str) -> Dict[str, Any]:
        """Generate report of target's vulnerabilities."""
        pass
```

### 8.4 Meta-Analytic Structure

Connect meta-analyses to their constituent papers:

```python
@dataclass
class MetaAnalyticLink:
    """Link between meta-analysis and included study."""

    meta_paper_id: str
    included_paper_id: str
    effect_size: float  # Standardized effect (Cohen's d, etc.)
    effect_size_ci: Tuple[float, float]  # 95% CI
    weight: float  # Weight in meta-analysis
    sample_size: int
    moderators: Dict[str, Any]  # Subgroup moderator values

@dataclass
class MetaAnalyticSummary:
    """Aggregated effect from meta-analysis."""

    meta_paper_id: str
    outcome_construct: str

    # Included studies
    included_studies: List[MetaAnalyticLink]
    k: int  # Number of studies
    total_n: int  # Total sample size

    # Summary effect
    pooled_effect: float
    pooled_ci: Tuple[float, float]

    # Heterogeneity
    i_squared: float  # Percentage of variance due to heterogeneity
    q_statistic: float
    tau_squared: float  # Between-study variance

    # Moderator analysis
    moderator_effects: Dict[str, Dict[str, float]]  # moderator → {level → effect}

    # Quality indicators
    publication_bias_detected: bool
    egger_test_p: Optional[float]
    trim_and_fill_adjusted: Optional[float]
```

### 8.5 Hierarchy → Aggregation Bridge

The user's key question: How do within-template hierarchies connect to cross-paper aggregation?

**Current hierarchies** (within template):
- COL2.arousal_dimensions: saturation > brightness > hue
- VIEW1.synthetic_hierarchy: real > video > photo > none
- L2.age_correction: elderly = 2x melanopic EDI

**Gap**: These orderings don't connect to:
1. Effect size comparison across papers testing these levels
2. Meta-analytic evidence for the hierarchy
3. Generalization confidence based on evidence breadth

**Bridge needed**:

```python
@dataclass
class HierarchyEvidence:
    """Links a within-template hierarchy to cross-paper evidence."""

    hierarchy_id: str
    source_template: str
    ordered_levels: List[str]  # The hierarchy ordering

    # Evidence for each pairwise comparison
    pairwise_comparisons: Dict[Tuple[str, str], PairwiseEvidence]

    # Overall support
    evidence_strength: str  # "meta-analytic", "multi-study", "single-study", "theoretical"
    n_studies: int
    n_papers: int

@dataclass
class PairwiseEvidence:
    """Evidence for one level > another level."""

    higher_level: str
    lower_level: str

    # Direct comparisons
    studies_comparing: List[str]  # Paper IDs
    pooled_difference: Optional[float]  # Effect size
    confidence_interval: Optional[Tuple[float, float]]

    # Indirect evidence
    indirect_chain: Optional[List[str]]  # If no direct comparison, transitive inference
    indirect_confidence: float

class HierarchyAggregator:
    """Aggregates evidence for hierarchies across papers."""

    def aggregate_hierarchy_evidence(
        self,
        hierarchy_id: str
    ) -> HierarchyEvidence:
        """Gather all cross-paper evidence for a hierarchy."""
        pass

    def validate_hierarchy(
        self,
        hierarchy_id: str
    ) -> Dict[str, Any]:
        """Check if cross-paper evidence supports the claimed ordering."""
        pass
```

### 8.6 Generalization Pathway

Hierarchy → Aggregation → Generalization:

```
1. HIERARCHY (within template)
   └─ "saturation > brightness > hue for arousal"

2. AGGREGATION (across papers)
   └─ 5 papers test saturation vs brightness → pooled d = 0.42 [0.28, 0.56]
   └─ 3 papers test brightness vs hue → pooled d = 0.21 [0.08, 0.34]

3. GENERALIZATION
   └─ Saturation-brightness ordering: "Established" (k=5, I²=23%)
   └─ Brightness-hue ordering: "Supported" (k=3, I²=45%)
   └─ Full hierarchy: "Supported" (transitive inference required)
```

### 8.7 Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| A8.1 | Define PaperRelation schema | 2h | — |
| A8.2 | Define PaperRelationType enum (all critique types) | 1h | A8.1 |
| A8.3 | Implement CritiqueCollection aggregator | 4h | A8.2 |
| A8.4 | Extract paper relations from citation analysis | 6h | A8.3 |
| A8.5 | Define MetaAnalyticLink and MetaAnalyticSummary | 2h | — |
| A8.6 | Extract meta-analysis structure from meta-analysis papers | 4h | A8.5 |
| A8.7 | Implement HierarchyEvidence schema | 2h | — |
| A8.8 | Implement HierarchyAggregator | 4h | A8.7 |
| A8.9 | Connect hierarchy evidence to template hierarchies | 3h | A8.8, Phase 6 |
| A8.10 | QA integration: Answer "What critiques exist for X?" | 3h | A8.3 |
| A8.11 | QA integration: Answer "How strong is the evidence for hierarchy Y?" | 3h | A8.8 |

**Total Phase 8**: ~34 hours

---

## Revised Total Timeline

| Phase | Hours | Calendar |
|-------|-------|----------|
| Phase 1: Molecules | 20h | 5 days |
| Phase 2: Bridging | 10h | 2.5 days |
| Phase 3: QA Routing | 20h | 5 days |
| Phase 4: Amendments | 8h | 2 days |
| Phase 5: BN Integration | 13h | 3 days |
| Phase 6: Network Features | 23h | 6 days |
| Phase 7: Query Indices | 12h | 3 days |
| **Phase 8: Argument & Aggregation** | **34h** | **8.5 days** |

**New Total**: ~140 hours over ~22 calendar days (with parallelization)

---

## Phase 8 Parallelization

```
Phase 1 ←──────────────────┐
    │                      │
    ↓                      │
Phase 2                    │
    │                      │
    ↓                      │
Phase 3        Phase 6 ────┼──→ Phase 8 (A8.7-A8.11)
    │              │       │
    ↓              ↓       │
Phase 4       Phase 7      │
                           │
                           │
           Phase 8 (A8.1-A8.6) ←───── Can start in parallel
```

Phase 8 has two sub-tracks:
- **A8.1-A8.6** (Paper Relations & Meta-Analysis): Can start immediately
- **A8.7-A8.11** (Hierarchy Aggregation): Depends on Phase 6 (HierarchyRegistry)

---

*End of Implementation Plan*
