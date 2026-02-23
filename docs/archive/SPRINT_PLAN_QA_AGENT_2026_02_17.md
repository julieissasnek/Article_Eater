# QA Agent Sprint Plan

**Date**: February 17, 2026
**Status**: APPROVED FOR EXECUTION
**Total Effort**: ~155 hours over ~6 weeks (4 parallel terminals)
**Integration**: Merges with existing Sprint 2.0 completion + Sprint 3.0 planning

---

## Executive Summary

This plan converts the QA Agent Implementation Plan (Phases 1-8) into sprints that integrate with Article Eater's existing sprint structure, prioritize based on dependencies, and distribute work across 4 AI terminals for efficient parallel execution.

### Sprint Overview

| Sprint | Name | Hours | Terminals | Dependencies |
|--------|------|-------|-----------|--------------|
| **2.0.R** | Pipeline Completion | 8h | T1 | — |
| **7.0** | Web Structure | 43h | T1+T2 (parallel) | 2.0.R |
| **7.5** | QA Agent Core | 28h | T3 | 7.0 |
| **8.0** | Argument & Aggregation | 34h | T4 | 7.0 |
| **8.5** | Query Optimization | 12h | T1 | 7.5, 8.0 |
| **9.0** | Integration & Testing | 16h | All | 8.5 |
| **KB** | Knowledge Base Enhancement | 14h | T2 (background) | — |

---

## Terminal Assignments

| Terminal | Primary Focus | Sprints |
|----------|---------------|---------|
| **T1** | Molecules + Query Indices | 2.0.R → 7.0A → 8.5 → 9.0 |
| **T2** | Network Features + KB | 7.0B → KB (background) → 9.0 |
| **T3** | QA Agent Core | 7.5 → 9.0 |
| **T4** | Argument Structure | 8.0 → 9.0 |

### Parallel Execution Timeline

```
Week 1:  T1: 2.0.R ─────────────────────────────────────
         T2: ─────────────────────────────────────────
         T3: ─────────────────────────────────────────
         T4: ─────────────────────────────────────────

Week 2:  T1: 7.0A (Molecules) ─────────────────────────
         T2: 7.0B (Network Features) ──────────────────
         T3: ─────────────────────────────────────────
         T4: 8.0 (Argument) ──────────────────────────

Week 3:  T1: 7.0A cont'd ──────────────────────────────
         T2: 7.0B cont'd ─────────────────────────────
         T3: 7.5 (QA Core) ────────────────────────────
         T4: 8.0 cont'd ──────────────────────────────

Week 4:  T1: 8.5 (Query Indices) ──────────────────────
         T2: KB (background) ──────────────────────────
         T3: 7.5 cont'd ──────────────────────────────
         T4: 8.0 cont'd ──────────────────────────────

Week 5:  T1: 9.0 ─────────────────────────────────────
         T2: 9.0 ─────────────────────────────────────
         T3: 9.0 ─────────────────────────────────────
         T4: 9.0 ─────────────────────────────────────
```

---

## Sprint 2.0.R: Pipeline Completion (PREREQUISITE)

**Terminal**: T1
**Hours**: 8h
**Status**: Completes existing Sprint 2.0

### Tasks

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 2.0.3 | CLI flags for web outputs | 2h | Add `--web-output`, `--tensions`, `--bridges` flags |
| 2.0.4 | Test with sample papers | 4h | End-to-end test with 5+ papers |
| 2.0.5 | Error handling and logging | 2h | Graceful failures, structured logging |

### Acceptance Criteria

- [ ] `./bin/article_eater eat --web-output` produces complete web state
- [ ] Pipeline handles missing fields gracefully
- [ ] Structured logs with timestamps

---

## Sprint 7.0: Web Structure (PARALLEL TRACKS)

**Terminals**: T1 (Track A), T2 (Track B)
**Hours**: 43h total (20h T1 + 23h T2)
**Dependencies**: Sprint 2.0.R complete

### Track A: Molecule Formalization (T1)

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 7.0.1 | Define Molecule schema | 2h | `molecules/schema.py` with Molecule, MoleculeComponent dataclasses |
| 7.0.2 | Create molecules/ directory | 1h | Structure: `molecules/{schema.py, registry.json, constructs/}` |
| 7.0.3 | Formalize ART molecule | 3h | `molecules/constructs/art.json` with 4 components |
| 7.0.4 | Formalize SRT molecule | 2h | `molecules/constructs/srt.json` |
| 7.0.5 | Formalize Prospect-Refuge | 2h | `molecules/constructs/prospect_refuge.json` |
| 7.0.6 | Formalize Biophilia | 2h | `molecules/constructs/biophilia.json` |
| 7.0.7 | Audit remaining constructs | 4h | Review tier2_construct_map, formalize candidates |
| 7.0.8 | Create molecule registry | 2h | `molecules/registry.json` index |
| 7.0.9 | Template bridging | 2h | Add `participates_in_molecules` to template schema |

**Files Created**:
- `molecules/schema.py`
- `molecules/registry.json`
- `molecules/constructs/*.json`

### Track B: Network Features (T2)

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 7.0.10 | DomainIndex | 3h | Index templates by domain (acoustic, color, spatial) |
| 7.0.11 | FrameworkIndex | 2h | Map frameworks (PP, ART, BRECVEMA) to templates |
| 7.0.12 | InteractionGraph | 4h | Extract template interactions as explicit graph |
| 7.0.13 | ModeratorRegistry | 3h | Unified registry of population/context moderators |
| 7.0.14 | HierarchyRegistry | 3h | Extract explicit orderings from templates |
| 7.0.15 | MaturityPropagation | 2h | Rules for aggregating maturity across chains/molecules |
| 7.0.16 | Unified network index | 4h | Combine all indices with validation |
| 7.0.17 | Validation tests | 2h | All templates indexed, no orphans |

**Files Created**:
- `src/indices/domain_index.py`
- `src/indices/framework_index.py`
- `src/indices/interaction_graph.py`
- `src/indices/moderator_registry.py`
- `src/indices/hierarchy_registry.py`
- `src/indices/maturity.py`
- `src/indices/__init__.py`

---

## Sprint 7.5: QA Agent Core (T3)

**Terminal**: T3
**Hours**: 28h
**Dependencies**: Sprint 7.0 complete (both tracks)

### Tasks

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 7.5.1 | Question classifier | 4h | Classify into 10 categories (A-J from spec) |
| 7.5.2 | MoleculeAwareRouter | 4h | Route queries to molecules/templates/mechanisms |
| 7.5.3 | Molecule lookup responder | 3h | "What is ART?" → structured response |
| 7.5.4 | Component lookup responder | 2h | "How does soft fascination work?" |
| 7.5.5 | Multi-molecule synthesis | 4h | "Design hospital room" → relevant molecules |
| 7.5.6 | Taxonomic expansion | 3h | Auto-distinguish sound types, color types |
| 7.5.7 | Amendment implementation | 4h | Amendments 12-17 response behaviors |
| 7.5.8 | Integration tests | 4h | 80 questions from spec as test cases |

**Files Created**:
- `src/qa/question_classifier.py`
- `src/qa/router.py`
- `src/qa/molecule_responder.py`
- `src/qa/synthesis.py`
- `src/qa/taxonomic_expansion.py`
- `tests/test_qa_agent.py`

---

## Sprint 8.0: Argument Structure & Aggregation (T4)

**Terminal**: T4
**Hours**: 34h
**Dependencies**: Sprint 7.0B (HierarchyRegistry) complete

### Tasks

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 8.0.1 | PaperRelation schema | 2h | Paper-to-paper argument relations |
| 8.0.2 | PaperRelationType enum | 1h | REPLICATES, CRITIQUES_METHOD, META_ANALYZES, etc. |
| 8.0.3 | CritiqueAggregator | 4h | Collect all critiques of a target |
| 8.0.4 | Paper relation extraction | 6h | Extract from citation analysis |
| 8.0.5 | MetaAnalyticLink schema | 2h | Link meta-analysis to constituent studies |
| 8.0.6 | MetaAnalyticSummary | 4h | Aggregate: pooled effect, I², Q, bias |
| 8.0.7 | HierarchyEvidence schema | 2h | Cross-paper evidence for hierarchies |
| 8.0.8 | HierarchyAggregator | 4h | Validate hierarchies against evidence |
| 8.0.9 | Hierarchy-template bridge | 3h | Connect evidence to HierarchyRegistry |
| 8.0.10 | QA: critique queries | 3h | "What critiques exist for X?" |
| 8.0.11 | QA: hierarchy evidence | 3h | "How strong is evidence for Y?" |

**Files Created**:
- `src/argument/paper_relations.py`
- `src/argument/critique_aggregator.py`
- `src/argument/meta_analytic.py`
- `src/argument/hierarchy_evidence.py`
- `tests/test_argument_structure.py`

---

## Sprint 8.5: Query Optimization Indices (T1)

**Terminal**: T1
**Hours**: 12h
**Dependencies**: Sprints 7.5, 8.0 complete

### Tasks

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| 8.5.1 | Outcome index | 3h | outcome → template_ids lookup |
| 8.5.2 | Attribute index | 3h | attribute → template_ids lookup |
| 8.5.3 | Causal path index | 4h | Pre-computed common paths |
| 8.5.4 | Performance benchmarks | 2h | Query latency targets |

**Files Created**:
- `src/indices/outcome_index.py`
- `src/indices/attribute_index.py`
- `src/indices/causal_path_index.py`

---

## Sprint 9.0: Integration & Testing (ALL)

**Terminals**: T1, T2, T3, T4
**Hours**: 16h (4h each)
**Dependencies**: All previous sprints

### Tasks

| ID | Terminal | Task | Hours |
|----|----------|------|-------|
| 9.0.1 | T1 | End-to-end QA tests (80 questions) | 4h |
| 9.0.2 | T2 | Index consistency validation | 4h |
| 9.0.3 | T3 | Amendment compliance tests | 4h |
| 9.0.4 | T4 | Argument structure integration | 4h |

---

## Sprint KB: Knowledge Base Enhancement (BACKGROUND)

**Terminal**: T2 (runs in background when blocked)
**Hours**: 14h
**Dependencies**: None (independent track)

### Tasks

| ID | Task | Hours | Description |
|----|------|-------|-------------|
| KB.1 | Curvature mechanism entry | 3h | Add to BN registry from VF1 |
| KB.2 | Color arousal mechanism entry | 3h | Add from COL1/COL2 |
| KB.3 | Effect size extraction | 4h | From Valdez & Mehrabian, Bar & Neta |
| KB.4 | Template-mechanism bridge | 4h | Utility to sync templates → registry |

---

## AI Terminal Prompts

### Terminal T1 Prompt

```markdown
# TERMINAL T1: Molecule Formalization + Query Indices

## Your Mission
You are Terminal T1, responsible for formalizing Tier 2 molecules and building query optimization indices.

## Context
- **Repo**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`
- **Sprint Sequence**: 2.0.R → 7.0A → 8.5 → 9.0
- **Key Docs**:
  - `docs/QA_AGENT_IMPLEMENTATION_PLAN_2026_02_16.md` (Phases 1, 7)
  - `docs/tier2_construct_map_preliminary.md` (molecule definitions)
  - `docs/SPRINT_PLAN_QA_AGENT_2026_02_17.md` (this plan)

## Sprint 2.0.R Tasks (Do First)
1. Add CLI flags to `app/cli/article_eater_contract_cli.py`:
   - `--web-output`: Enable web state JSON output
   - `--tensions`: Output tensions.jsonl
   - `--bridges`: Output bridges.jsonl
2. Test with 5+ sample papers from `contracts/ae_af/examples/`
3. Add error handling to `app/tasks/pipeline.py`

## Sprint 7.0A Tasks (Molecule Formalization)
1. Create `molecules/schema.py` with:
   ```python
   @dataclass
   class MoleculeComponent:
       name: str
       template_ids: List[str]
       interaction_type: str
       description: str

   @dataclass
   class Molecule:
       molecule_id: str
       name: str
       components: List[MoleculeComponent]
       constituent_templates: List[str]
       framework_ids: List[str]
       domain: str
       overall_maturity: str
       key_references: List[str]
   ```

2. Formalize these molecules (create JSON files in `molecules/constructs/`):
   - **ART**: T27 (soft fascination), T31 (being away), T2 (extent), T23 (compatibility), T29, T3, T14(neg), T8, T1, T37
   - **SRT**: T9, T22, T8, T12, T5
   - **Prospect-Refuge**: T3, T5 (interaction)
   - **Biophilia**: T1, T2

3. Create `molecules/registry.json` as index

4. Add `participates_in_molecules` field to template schema

## Sprint 8.5 Tasks (Query Indices)
After T2, T3, T4 complete their work:
1. Build outcome → template index
2. Build attribute → template index
3. Build pre-computed causal path index for common pairs
4. Benchmark query latency (<100ms target)

## Coordination
- Check `ACTIVE_TASKS.md` before claiming tasks
- Update progress in `TASKS.md` session log
- Notify when Sprint 2.0.R complete (unblocks T2 for 7.0B)
- Notify when Sprint 7.0A complete (unblocks T3 for 7.5)

## Testing
- Run `pytest tests/` after each task group
- Create tests in `tests/test_molecules.py`, `tests/test_query_indices.py`
```

---

### Terminal T2 Prompt

```markdown
# TERMINAL T2: Network Features + Knowledge Base

## Your Mission
You are Terminal T2, responsible for building network structure indices and knowledge base enhancements.

## Context
- **Repo**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`
- **Sprint Sequence**: 7.0B → KB (background) → 9.0
- **Key Docs**:
  - `docs/QA_AGENT_IMPLEMENTATION_PLAN_2026_02_16.md` (Phase 6)
  - `docs/KBASE_ENHANCEMENT_FLAGS_2026_02_16.md` (KB tasks)
  - `docs/SPRINT_PLAN_QA_AGENT_2026_02_17.md` (this plan)

## Wait Condition
Wait for T1 to complete Sprint 2.0.R before starting Sprint 7.0B.

## Sprint 7.0B Tasks (Network Features)
Create `src/indices/` directory with these modules:

### 1. DomainIndex (`domain_index.py`)
```python
@dataclass
class DomainEntry:
    domain_id: str  # "acoustic", "color", "spatial"
    display_name: str
    template_prefixes: List[str]  # ["T58", "AUD_", "T19"]
    template_ids: List[str]
    sibling_domains: List[str]
    parent_domain: Optional[str]

class DomainIndex:
    def __init__(self, templates_dir: str): ...
    def get_domain(self, domain_id: str) -> DomainEntry: ...
    def get_templates_for_domain(self, domain_id: str) -> List[str]: ...
    def get_siblings(self, domain_id: str) -> List[str]: ...
```

### 2. FrameworkIndex (`framework_index.py`)
Map Tier 1 frameworks (PP, ART, BRECVEMA) to templates that instantiate them.

### 3. InteractionGraph (`interaction_graph.py`)
Extract `interactions` field from templates into unified graph:
```python
@dataclass
class InteractionEdge:
    from_template: str
    to_template: str
    interaction_type: str  # "ELABORATION", "CRITICAL_INPUT", "CONFLICT"
    bidirectional: bool
```

### 4. ModeratorRegistry (`moderator_registry.py`)
Unified registry of moderators (age, introversion, task_type) across templates.

### 5. HierarchyRegistry (`hierarchy_registry.py`)
Extract explicit orderings:
- COL2.arousal_dimensions: saturation > brightness > hue
- VIEW1.synthetic_hierarchy: real > video > photo > none
- L2.age_correction formulas

### 6. MaturityPropagation (`maturity.py`)
Rules for aggregating maturity:
- Chain: weakest link
- Molecule: min(template maturities) or weighted average
- Domain: distribution

### 7. Unified Index (`__init__.py`)
Combine all indices with validation that all templates are indexed.

## Sprint KB Tasks (Background)
When blocked waiting for others, work on KB:
1. Add curvature_preference mechanism to `BN_graphical/src/mechanisms/mechanism_registry.json`
2. Add color_saturation_arousal, color_warmth_arousal mechanisms
3. Extract effect sizes from literature (Valdez & Mehrabian 1994, Bar & Neta 2006)
4. Create utility to bridge templates → mechanisms

## Coordination
- Check `ACTIVE_TASKS.md` before claiming tasks
- Notify when HierarchyRegistry complete (unblocks T4 for 8.0.7-8.0.9)
- Notify when 7.0B complete (unblocks T3 for 7.5)

## Testing
- Create `tests/test_indices.py`
- Validate: every template appears in at least one index
```

---

### Terminal T3 Prompt

```markdown
# TERMINAL T3: QA Agent Core

## Your Mission
You are Terminal T3, responsible for building the QA Agent query system.

## Context
- **Repo**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`
- **Sprint Sequence**: 7.5 → 9.0
- **Key Docs**:
  - `docs/QA_AGENT_SPECIFICATION_PANEL_2026_02_16.md` (full spec)
  - `docs/QA_AGENT_SPECIFICATION_AMENDMENTS_2026_02_16.md` (17 amendments)
  - `docs/QA_AGENT_GENERATED_QUESTIONS_2026_02_16.md` (80 test questions)
  - `docs/QA_AGENT_IMPLEMENTATION_PLAN_2026_02_16.md` (Phase 3)

## Wait Condition
Wait for T1 (7.0A) and T2 (7.0B) to complete before starting Sprint 7.5.

## Sprint 7.5 Tasks (QA Agent Core)
Create `src/qa/` directory with these modules:

### 1. Question Classifier (`question_classifier.py`)
Classify into 10 categories from spec:
- A: Effect Existence ("Does X affect Y?")
- B: Mechanism/Why ("Why does X affect Y?")
- C: Comparative ("Is X better than Y?")
- D: Dosage/Optimization ("How much X?")
- E: Scope/Boundary ("Does X apply to population Z?")
- F: Interaction ("How do X and Y interact?")
- G: Design/Application ("How to design for outcome Z?")
- H: Theory/Framework ("What is theory X?")
- I: Evidence/Confidence ("How strong is evidence for X?")
- J: Gap/Research ("What's unknown about X?")

### 2. MoleculeAwareRouter (`router.py`)
```python
class MoleculeAwareRouter:
    def __init__(self, molecule_registry, template_index, mechanism_registry): ...

    def route(self, question: ClassifiedQuestion) -> QueryPlan:
        """
        Routes to:
        - molecule: "What is ART?"
        - molecule_component: "How does soft fascination work?"
        - templates: WHY/MECHANISM questions
        - mechanisms: EFFECT_SIZE/OPTIMAL questions
        - molecule_synthesis: DESIGN questions
        """
```

### 3. Molecule Responder (`molecule_responder.py`)
Structured responses for molecule-level queries:
- Enumerate components
- List constituent templates
- Report overall maturity
- Cite key references

### 4. Multi-Molecule Synthesis (`synthesis.py`)
For design questions ("design hospital room"):
1. Identify context (hospital = healthcare, patient)
2. Retrieve relevant molecules (ART, circadian, privacy)
3. Check for interactions between molecules
4. Synthesize recommendations

### 5. Taxonomic Expansion (`taxonomic_expansion.py`)
Amendment 10: Auto-distinguish domain siblings:
- Sound types: speech (depleting), mechanical (depleting), natural (restorative), music (complex)
- Color types: hue, saturation, brightness
- Nature types: real, video, photo, plants

### 6. Amendment Implementation
Implement amendments 12-17:
- 12: Multi-template synthesis for design questions
- 13: Hierarchy extraction in responses
- 14: Context → parameter mapping
- 15: Population adjustment detection
- 16: Cross-template interaction classification
- 17: Confidence chain (weakest link) reporting

### 7. Integration Tests (`tests/test_qa_agent.py`)
Use 80 questions from `QA_AGENT_GENERATED_QUESTIONS_2026_02_16.md` as test cases:
- Category A: 6 questions
- Category B: 8 questions
- ...etc.

## Coordination
- Depends on molecules registry from T1
- Depends on network indices from T2
- Update progress in `TASKS.md` session log
```

---

### Terminal T4 Prompt

```markdown
# TERMINAL T4: Argument Structure & Aggregation

## Your Mission
You are Terminal T4, responsible for building paper-level argument relations and meta-analytic aggregation.

## Context
- **Repo**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`
- **Sprint Sequence**: 8.0 → 9.0
- **Key Docs**:
  - `docs/QA_AGENT_IMPLEMENTATION_PLAN_2026_02_16.md` (Phase 8)
  - `src/services/argument_attack.py` (existing belief-level attacks)
  - `src/epistemic/extraction/argumentative.py` (existing extraction)

## Start Condition
Can start Sprint 8.0 in parallel with T1/T2 working on Sprint 7.0.
Tasks 8.0.7-8.0.9 (hierarchy evidence) depend on T2's HierarchyRegistry.

## Sprint 8.0 Tasks (Argument Structure)
Create `src/argument/` directory:

### 1. Paper Relations (`paper_relations.py`)
```python
class PaperRelationType(Enum):
    REPLICATES = "replicates"
    FAILS_TO_REPLICATE = "fails_to_replicate"
    EXTENDS = "extends"
    CRITIQUES_METHOD = "critiques_method"
    CRITIQUES_STIMULUS = "critiques_stimulus"
    CRITIQUES_POPULATION = "critiques_population"
    CRITIQUES_ASSUMPTION = "critiques_assumption"
    CRITIQUES_INTERPRETATION = "critiques_interpretation"
    CRITIQUES_STATISTICS = "critiques_statistics"
    META_ANALYZES = "meta_analyzes"
    REVIEWS = "reviews"
    CONFIRMS = "confirms"

@dataclass
class PaperRelation:
    relation_id: str
    source_paper_id: str
    target_paper_id: str
    relation_type: PaperRelationType
    target_aspect: str  # "method", "assumption", "interpretation"
    specific_target: str  # "HRV measurement", "student sample"
    critique_summary: str
    critique_strength: float  # 0-1
    resolved: bool
    resolution: Optional[str]
```

### 2. Critique Aggregator (`critique_aggregator.py`)
```python
@dataclass
class CritiqueCollection:
    target_id: str
    target_type: str  # "paper", "method", "claim"
    method_critiques: List[PaperRelation]
    stimulus_critiques: List[PaperRelation]
    population_critiques: List[PaperRelation]
    assumption_critiques: List[PaperRelation]
    total_critique_count: int
    weighted_critique_severity: float
    vulnerability_profile: Dict[str, float]

class CritiqueAggregator:
    def collect_critiques(self, target_id: str) -> CritiqueCollection: ...
    def vulnerability_report(self, target_id: str) -> Dict[str, Any]: ...
```

### 3. Meta-Analytic Structure (`meta_analytic.py`)
```python
@dataclass
class MetaAnalyticLink:
    meta_paper_id: str
    included_paper_id: str
    effect_size: float  # Cohen's d
    effect_size_ci: Tuple[float, float]
    weight: float
    sample_size: int
    moderators: Dict[str, Any]

@dataclass
class MetaAnalyticSummary:
    meta_paper_id: str
    outcome_construct: str
    included_studies: List[MetaAnalyticLink]
    k: int  # study count
    total_n: int
    pooled_effect: float
    pooled_ci: Tuple[float, float]
    i_squared: float  # heterogeneity
    q_statistic: float
    publication_bias_detected: bool
```

### 4. Hierarchy Evidence (`hierarchy_evidence.py`)
Wait for T2's HierarchyRegistry, then:
```python
@dataclass
class PairwiseEvidence:
    higher_level: str
    lower_level: str
    studies_comparing: List[str]
    pooled_difference: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    indirect_chain: Optional[List[str]]

@dataclass
class HierarchyEvidence:
    hierarchy_id: str
    source_template: str
    ordered_levels: List[str]
    pairwise_comparisons: Dict[Tuple[str, str], PairwiseEvidence]
    evidence_strength: str  # "meta-analytic", "multi-study", "single-study"
    n_studies: int

class HierarchyAggregator:
    def aggregate_hierarchy_evidence(self, hierarchy_id: str) -> HierarchyEvidence: ...
    def validate_hierarchy(self, hierarchy_id: str) -> Dict[str, Any]: ...
```

### 5. QA Integration
Add query handlers:
- "What critiques exist for Ulrich 1984?" → CritiqueCollection response
- "How strong is the evidence for saturation > brightness?" → HierarchyEvidence response

## Coordination
- Check `ACTIVE_TASKS.md` before claiming tasks
- Tasks 8.0.1-8.0.6 can run in parallel with 7.0
- Tasks 8.0.7-8.0.9 wait for T2's HierarchyRegistry
- Update progress in `TASKS.md` session log

## Existing Code to Understand
- `src/services/argument_attack.py`: Belief-level attacks (use as reference, don't duplicate)
- `src/epistemic/extraction/argumentative.py`: Theory support/challenge extraction
- `src/epistemic/entrenchment/critique_propagation.py`: Method critique propagation
```

---

## TASKS.md Updates

Add the following to `ruthless_bundle_2026-02-08/TASKS.md`:

### New Sprint Entries

```markdown
## Sprint 7.0: Web Structure

**Status**: PENDING
**Terminals**: T1 (Track A), T2 (Track B)
**Dependencies**: Sprint 2.0.R complete

### Track A: Molecule Formalization (T1)
| ID | Task | Hours | Status |
|----|------|-------|--------|
| 7.0.1 | Define Molecule schema | 2h | PENDING |
| 7.0.2 | Create molecules/ directory | 1h | PENDING |
| 7.0.3 | Formalize ART molecule | 3h | PENDING |
| 7.0.4 | Formalize SRT molecule | 2h | PENDING |
| 7.0.5 | Formalize Prospect-Refuge | 2h | PENDING |
| 7.0.6 | Formalize Biophilia | 2h | PENDING |
| 7.0.7 | Audit remaining constructs | 4h | PENDING |
| 7.0.8 | Create molecule registry | 2h | PENDING |
| 7.0.9 | Template bridging | 2h | PENDING |

### Track B: Network Features (T2)
| ID | Task | Hours | Status |
|----|------|-------|--------|
| 7.0.10 | DomainIndex | 3h | PENDING |
| 7.0.11 | FrameworkIndex | 2h | PENDING |
| 7.0.12 | InteractionGraph | 4h | PENDING |
| 7.0.13 | ModeratorRegistry | 3h | PENDING |
| 7.0.14 | HierarchyRegistry | 3h | PENDING |
| 7.0.15 | MaturityPropagation | 2h | PENDING |
| 7.0.16 | Unified network index | 4h | PENDING |
| 7.0.17 | Validation tests | 2h | PENDING |

---

## Sprint 7.5: QA Agent Core

**Status**: PENDING
**Terminal**: T3
**Dependencies**: Sprint 7.0 complete

| ID | Task | Hours | Status |
|----|------|-------|--------|
| 7.5.1 | Question classifier | 4h | PENDING |
| 7.5.2 | MoleculeAwareRouter | 4h | PENDING |
| 7.5.3 | Molecule lookup responder | 3h | PENDING |
| 7.5.4 | Component lookup responder | 2h | PENDING |
| 7.5.5 | Multi-molecule synthesis | 4h | PENDING |
| 7.5.6 | Taxonomic expansion | 3h | PENDING |
| 7.5.7 | Amendment implementation | 4h | PENDING |
| 7.5.8 | Integration tests | 4h | PENDING |

---

## Sprint 8.0: Argument Structure & Aggregation

**Status**: PENDING
**Terminal**: T4
**Dependencies**: Sprint 7.0B (partial)

| ID | Task | Hours | Status |
|----|------|-------|--------|
| 8.0.1 | PaperRelation schema | 2h | PENDING |
| 8.0.2 | PaperRelationType enum | 1h | PENDING |
| 8.0.3 | CritiqueAggregator | 4h | PENDING |
| 8.0.4 | Paper relation extraction | 6h | PENDING |
| 8.0.5 | MetaAnalyticLink schema | 2h | PENDING |
| 8.0.6 | MetaAnalyticSummary | 4h | PENDING |
| 8.0.7 | HierarchyEvidence schema | 2h | PENDING (wait for 7.0.14) |
| 8.0.8 | HierarchyAggregator | 4h | PENDING (wait for 7.0.14) |
| 8.0.9 | Hierarchy-template bridge | 3h | PENDING |
| 8.0.10 | QA: critique queries | 3h | PENDING |
| 8.0.11 | QA: hierarchy evidence | 3h | PENDING |
```

---

## Acceptance Criteria (Sprint 9.0)

Sprint 9.0 is complete when:

1. [ ] 80 test questions from spec pass
2. [ ] All templates indexed in at least one index
3. [ ] Molecule registry contains ART, SRT, Prospect-Refuge, Biophilia
4. [ ] "What is ART?" returns structured molecule response
5. [ ] "Design a restorative hospital room" synthesizes relevant molecules
6. [ ] "What critiques exist for Ulrich 1984?" returns aggregated critiques
7. [ ] "How strong is evidence for saturation > brightness?" returns hierarchy evidence
8. [ ] Query latency < 100ms for simple lookups

---

*End of Sprint Plan*
