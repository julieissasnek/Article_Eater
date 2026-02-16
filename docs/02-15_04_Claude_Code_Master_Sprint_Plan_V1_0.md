# Claude Code Master Sprint Plan
## Article Eater — Full Implementation Roadmap
## Version 1.0 — February 15, 2026

---

# HOW TO USE THIS DOCUMENT

This is the master task list for Claude Code (CC). It incorporates:

1. **Sprints 0–5** from the original `docs/IMPLEMENTATION_TASKS.md` (Epistemic Tier 2 integration) — **unchanged**, already well-specified
2. **Sprint 6**: Research Queue Prioritization — new
3. **Sprint 7**: Theory Tier Data Structures — new
4. **Sprint 8**: CMR Pipeline Scaffolding — new
5. **Sprint 9**: Pipeline Health & Expectation Tests — new

**For each new sprint, CC should read the referenced docs/ files before starting.** All relevant design documents should be placed in the project's `docs/` directory so CC can access them directly.

---

# REQUIRED DOCS IN `docs/` DIRECTORY

Copy these files into `docs/` before starting. CC will reference them by filename.

| File | Contents | Used By |
|------|----------|---------|
| `IMPLEMENTATION_TASKS.md` | Original Sprints 0–5 (epistemic Tier 2) | Sprints 0–5 |
| `Theory_Tier_Architecture_V1_0.md` | 8 Tier 1 frameworks, criteria, scope declarations | Sprints 6, 7, 8 |
| `CMR_Spec_V1_0.md` | CMR pipeline 6-step specification, prediction grammar | Sprint 8 |
| `CMR_Revised_Spec_Panel_Templates_V2_0.md` | Expert panel critique + Templates 1–20 | Sprint 7, 8 |
| `Neuroscience_Panel_Tier1_Frameworks_V1_0.md` | Panel I: template corrections/expansions, 9 panelists | Sprint 7 |
| `Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md` | Panel II: Templates 21–30, framework taxonomy | Sprint 7 |
| `Panel_III_Multimodal_Senses_HigherCognition_V1_0.md` | Panel III: multimodal templates, quantitative params | Sprint 7 |
| `Queue_Prioritization_Panel.md` | P-QUEUE-1: priority formula, satisficing rules | Sprint 6 |
| `Pipeline_Expectation_Tests.md` | Guardrail tests, data expectations, corpus health | Sprint 9 |
| `Ecological_Validity_Background_V1_0.md` | Tier 2b: task-ecological validity, method registry | Sprints 4b, 5 |

CC should also look for any files matching `docs/*.md` and `docs/*.py` that may have been added since this plan was written.

---

# SPRINT DEPENDENCY GRAPH

```
Sprint 0  (Discovery)
    │
    ▼
Sprint 1  (Schema Extensions)
    │
    ├──────────────────┐
    ▼                  ▼
Sprint 2            Sprint 4        Sprint 4b
(BN Integration)    (Extraction)    (Method Registry)
    │                  │                │
    ▼                  │                │
Sprint 3              │                │
(Reflexive Monitor)   │                │
    │                  │                │
    ├──────────────────┴────────────────┘
    ▼
Sprint 5  (Integration Testing)
    │
    ▼
Sprint 6  (Queue Prioritization)  ← can start after Sprint 2
    │
    ▼
Sprint 7  (Theory Tier Data Structures) ← can start after Sprint 1
    │
    ▼
Sprint 8  (CMR Pipeline Scaffolding) ← requires Sprint 7
    │
    ▼
Sprint 9  (Pipeline Health Tests) ← can start after Sprint 5
```

**Parallelization opportunities:**
- Sprint 6 can run in parallel with Sprints 3–5 (only needs BN subgraph from Sprint 2)
- Sprint 7 can run in parallel with Sprints 2–5 (only needs schema from Sprint 1)
- Sprint 9 can start any time after Sprint 5

---

# SPRINTS 0–5: EPISTEMIC TIER 2 (EXISTING)

**These are already fully specified in `docs/IMPLEMENTATION_TASKS.md`.** CC should read that file and execute Sprints 0–5 as written. No changes needed.

**Quick summary for orientation:**

| Sprint | Focus | Tasks | Key Deliverable |
|--------|-------|-------|-----------------|
| 0 | Discovery | 0.1–0.2 | Codebase map, baseline test state |
| 1 | Schema Extensions | 1.1–1.11 | EPISTEMIC domain, 7 link types, PathwayType, ReplicationStatus, PESubtype, bridge warrant subtypes, extended Node/Edge models |
| 2 | BN Integration | 2.1–2.6 | 10 epistemic BN nodes, environmental subgraph edges, source quality subgraph, pathway_type tagging, source_quality computation |
| 3 | Reflexive Monitoring | 3.1–3.5 | Coherence audit, entrenchment asymmetry monitor, structural bias detection, adversarial review cycle |
| 4 | Extraction Pipeline | 4.1–4.5 | Argumentative structure extraction, source quality metadata, pathway classifier, PE subtype classifier |
| 4b | Method Registry | 4b.1–4b.7 | Method registry data structure, 15+ seed entries, task-ecological validity scoring, claim type bifurcation, method identification in pipeline, per-claim validity with auto-challenges |
| 5 | Integration Testing | 5.1–5.8 | Ulrich test corpus, end-to-end pipeline test, three-pathway validation, bias detection validation, source quality ordering, claim type bifurcation validation, auto-challenge validation, uncharacterized method flagging |

**Reference docs for Sprints 0–5:**
- `docs/IMPLEMENTATION_TASKS.md` — the task specifications
- `CLAUDE.md` — project context and architecture summary
- `docs/Ecological_Validity_Background_V1_0.md` — for Sprint 4b context on method registry and task-ecological validity

---

# SPRINT 6: RESEARCH QUEUE PRIORITIZATION

## Context

**Read first:** `docs/Queue_Prioritization_Panel.md`

This sprint implements the unified priority scoring system designed by the P-QUEUE-1 expert panel (Simon, Howard, Thagard, Haack, Pearl, Cartwright, Marr, Friston). The Queue manages what the system searches for next — which gaps in the web of belief to try to fill, in what order, and when to stop.

## Task 6.1: Create ResearchTarget model

**Do:** Create `src/queue/models.py` (or equivalent location).

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class GapType(str, Enum):
    CONTRADICTION = "contradiction"
    DIRECTION = "direction"
    MECHANISM = "mechanism"
    VALIDATION = "validation"
    MEDIATION = "mediation"
    BOUNDARY = "boundary"
    UNJUSTIFIED_EDGE = "unjustified_edge"

class MarrLevel(str, Enum):
    COMPUTATIONAL = "computational"     # WHY — framework link
    ALGORITHMIC = "algorithmic"         # HOW — mechanism/pathway
    IMPLEMENTATION = "implementation"   # WHERE — neural evidence

class PriorityBucket(str, Enum):
    HIGH = "high"       # >= 0.7: Act now — coherence actively damaged
    MEDIUM = "medium"   # >= 0.4: Should address — structural gap or theory prediction
    LOW = "low"         # < 0.4: Nice to have — boundary clarification

class CausalLevel(str, Enum):
    COUNTERFACTUAL = "counterfactual"
    INTERVENTIONAL = "interventional"
    ASSOCIATIONAL = "associational"

@dataclass
class ResearchTarget:
    target_id: str
    gap_type: GapType
    gap_description: str

    # VOI components (Howard)
    structural_voi: float = 0.0      # coherence gain if gap filled
    epistemic_voi: float = 0.0       # uncertainty reduction expected

    # Theory alignment (Friston) — NEW
    theory_drivers: List[str] = field(default_factory=list)  # framework IDs that predict this
    theory_voi: float = 0.0
    mechanism_predictions: List[str] = field(default_factory=list)

    # Coherence impact (Thagard)
    affected_beliefs: List[str] = field(default_factory=list)
    is_on_critical_path: bool = False

    # Grounding depth (Haack)
    grounding_depth: int = 0  # min hops to empirical finding

    # Causal level (Pearl)
    causal_level: CausalLevel = CausalLevel.ASSOCIATIONAL

    # Marr level (Marr) — NEW
    marr_level: Optional[MarrLevel] = None

    # Search state
    priority_score: float = 0.0
    priority_bucket: PriorityBucket = PriorityBucket.MEDIUM
    is_research_opportunity: bool = False  # requires experimental design, not lit search
    source: str = "gap_predictor"  # gap_predictor | theory_driven | voi_analysis | manual
    created_at: Optional[str] = None
    last_searched: Optional[str] = None
    status: str = "pending"  # pending | searching | satisfied | escalated | stale
```

**Test:** Create a ResearchTarget with all fields populated. Serialize/deserialize.

**Commit:** `[Sprint 6 / Task 6.1] Create ResearchTarget model`

## Task 6.2: Implement priority scoring function

**Do:** Create `src/queue/priority.py`.

Implement the panel consensus formula from `docs/Queue_Prioritization_Panel.md` § "Panel Consensus: Priority Formula":

```python
GAP_TYPE_WEIGHTS = {
    GapType.CONTRADICTION: 1.0,
    GapType.DIRECTION: 0.9,
    GapType.MECHANISM: 0.7,
    GapType.VALIDATION: 0.6,
    GapType.MEDIATION: 0.5,
    GapType.BOUNDARY: 0.4,
    GapType.UNJUSTIFIED_EDGE: 0.8,
}

CAUSAL_LEVEL_BOOST = {
    CausalLevel.COUNTERFACTUAL: 1.3,
    CausalLevel.INTERVENTIONAL: 1.2,
    CausalLevel.ASSOCIATIONAL: 1.0,
}

def compute_priority(target: ResearchTarget) -> float:
    """
    Unified priority score per P-QUEUE-1 panel consensus.
    Returns value in [0, 1] where higher = more urgent.
    """
    # Component 1: Gap Type Base (Thagard)
    gap_base = GAP_TYPE_WEIGHTS.get(target.gap_type, 0.5)

    # Component 2: Theory Alignment (Friston)
    n_frameworks = len(target.theory_drivers)
    theory_voi = min(n_frameworks / 3, 1.0)
    if target.mechanism_predictions:
        theory_voi *= 1.2
    theory_voi = min(theory_voi, 1.0)

    # Component 3: Coherence Impact (Thagard)
    coherence_impact = min(
        len(target.affected_beliefs) * 0.1 + (0.3 if target.is_on_critical_path else 0.0),
        1.0
    )

    # Component 4: Grounding Penalty (Haack)
    grounding_penalty = 0.2 if target.grounding_depth > 3 else 0.0

    # Component 5: Structural Gap Boost (Pearl)
    structural_boost = 0.2 if target.gap_type in [
        GapType.DIRECTION, GapType.UNJUSTIFIED_EDGE
    ] else 0.0

    # Component 6: Causal Level Boost (Pearl)
    causal_boost = CAUSAL_LEVEL_BOOST.get(target.causal_level, 1.0)

    # Weighted combination
    priority = (
        gap_base * 0.25 +
        target.structural_voi * 0.15 +
        target.epistemic_voi * 0.15 +
        theory_voi * 0.20 +
        coherence_impact * 0.15 +
        structural_boost +
        grounding_penalty
    ) * causal_boost

    return min(priority, 1.0)


def bucket_priority(score: float) -> PriorityBucket:
    """Per Simon: three buckets, not continuous scores."""
    if score >= 0.7:
        return PriorityBucket.HIGH
    elif score >= 0.4:
        return PriorityBucket.MEDIUM
    else:
        return PriorityBucket.LOW
```

**Test:**
```python
# HIGH priority: contradiction, predicted by 3 frameworks, on critical path
t_high = ResearchTarget(
    target_id="test_high", gap_type=GapType.CONTRADICTION,
    gap_description="test", structural_voi=0.8, epistemic_voi=0.7,
    theory_drivers=["pp", "dmn", "neuromod"],
    is_on_critical_path=True, affected_beliefs=["a", "b", "c", "d", "e"],
)
score = compute_priority(t_high)
assert score >= 0.7
assert bucket_priority(score) == PriorityBucket.HIGH

# LOW priority: boundary gap, no theory drivers, low VOI
t_low = ResearchTarget(
    target_id="test_low", gap_type=GapType.BOUNDARY,
    gap_description="test", structural_voi=0.1, epistemic_voi=0.1,
)
score = compute_priority(t_low)
assert score < 0.4
assert bucket_priority(score) == PriorityBucket.LOW
```

**Commit:** `[Sprint 6 / Task 6.2] Implement priority scoring function`

## Task 6.3: Implement satisficing rules

**Do:** Add to `src/queue/satisficing.py`:

```python
from dataclasses import dataclass

SATISFICING_RULES = {
    "max_search_time_hours": 2,
    "min_articles_to_stop": 3,
    "max_databases": 5,
    "max_results_screened": 50,
    "stale_after_days": 30,
}

@dataclass
class SearchLog:
    target_id: str
    articles_found: list       # list of article IDs
    n_databases: int = 0
    n_screened: int = 0
    time_spent_hours: float = 0.0

def should_stop_searching(target, search_log: SearchLog) -> tuple:
    """
    Per Simon: Don't optimize, satisfice.
    Returns (should_stop: bool, reason: str)
    """
    if len(search_log.articles_found) >= SATISFICING_RULES["min_articles_to_stop"]:
        return True, "found_enough"

    if (search_log.n_databases >= SATISFICING_RULES["max_databases"]
            and search_log.n_screened >= SATISFICING_RULES["max_results_screened"]):
        return True, "searched_enough"

    if search_log.time_spent_hours >= SATISFICING_RULES["max_search_time_hours"]:
        return True, "time_limit_escalate_to_human"

    return False, "continue"
```

**Test:**
```python
log_enough = SearchLog("t1", articles_found=["a1", "a2", "a3"])
assert should_stop_searching(None, log_enough) == (True, "found_enough")

log_continue = SearchLog("t2", articles_found=["a1"], n_databases=2, n_screened=10)
assert should_stop_searching(None, log_continue) == (False, "continue")

log_timeout = SearchLog("t3", articles_found=[], time_spent_hours=2.5)
assert should_stop_searching(None, log_timeout) == (True, "time_limit_escalate_to_human")
```

**Commit:** `[Sprint 6 / Task 6.3] Implement satisficing rules`

## Task 6.4: Implement theory-driven target generation

**Do:** Add to `src/queue/theory_targets.py`:

```python
def refresh_theory_driven_targets(
    frameworks: list,
    existing_beliefs: dict,
    find_supporting_fn: callable
) -> list:
    """
    Generate ResearchTargets from Tier 1 framework predictions.
    Per Friston: minimize prediction error between what frameworks
    predict SHOULD exist and what we've found.

    Args:
        frameworks: list of framework objects with .predictions attribute
        existing_beliefs: dict mapping belief_id to credence
        find_supporting_fn: function(prediction) -> list of supporting beliefs
    """
    targets = []
    for framework in frameworks:
        if not hasattr(framework, 'predictions'):
            continue
        for prediction in framework.predictions:
            support = find_supporting_fn(prediction)
            support_credence = max((s.get('credence', 0) for s in support), default=0)

            if not support or support_credence < 0.5:
                target = ResearchTarget(
                    target_id=f"theory_{framework.framework_id}_{prediction.get('id', 'unknown')}",
                    gap_type=GapType.VALIDATION,
                    gap_description=f"{framework.name} predicts: {prediction.get('statement', '')}",
                    theory_drivers=[framework.framework_id],
                    mechanism_predictions=[prediction.get('statement', '')],
                    epistemic_voi=framework.confidence * (1.0 - support_credence),
                    source="theory_driven",
                )
                targets.append(target)
    return targets
```

**Test:** Create a mock framework with 3 predictions. One has support (credence 0.8), two don't. Should generate 2 targets.

**Commit:** `[Sprint 6 / Task 6.4] Implement theory-driven target generation`

## Task 6.5: Implement the Research Queue manager

**Do:** Create `src/queue/manager.py`:

```python
class ResearchQueue:
    def __init__(self):
        self._targets: dict = {}  # target_id -> ResearchTarget
        self._search_logs: dict = {}  # target_id -> SearchLog

    def add_target(self, target: ResearchTarget):
        target.priority_score = compute_priority(target)
        target.priority_bucket = bucket_priority(target.priority_score)
        self._targets[target.target_id] = target

    def get_next_target(self) -> Optional[ResearchTarget]:
        """Return highest priority pending target."""
        pending = [t for t in self._targets.values() if t.status == "pending"]
        if not pending:
            return None
        return max(pending, key=lambda t: t.priority_score)

    def mark_stale(self, stale_days: int = 30):
        """Mark targets not searched in stale_days as stale."""
        # implementation using created_at / last_searched
        pass

    def refresh_from_theories(self, frameworks, existing_beliefs, find_fn):
        """Add theory-driven targets, skip duplicates."""
        new_targets = refresh_theory_driven_targets(frameworks, existing_beliefs, find_fn)
        for t in new_targets:
            if t.target_id not in self._targets:
                self.add_target(t)

    def get_by_bucket(self, bucket: PriorityBucket) -> list:
        return [t for t in self._targets.values() if t.priority_bucket == bucket]

    def stats(self) -> dict:
        return {
            "total": len(self._targets),
            "high": len(self.get_by_bucket(PriorityBucket.HIGH)),
            "medium": len(self.get_by_bucket(PriorityBucket.MEDIUM)),
            "low": len(self.get_by_bucket(PriorityBucket.LOW)),
            "pending": len([t for t in self._targets.values() if t.status == "pending"]),
            "satisfied": len([t for t in self._targets.values() if t.status == "satisfied"]),
        }
```

**Test:** Add 5 targets with varying priority. `get_next_target()` returns highest. `stats()` counts are correct.

**Commit:** `[Sprint 6 / Task 6.5] Implement ResearchQueue manager`

## Task 6.6: Full test suite for Sprint 6

**Do:** `pytest tests/ -v`

**Test:** No regressions. All Sprint 6 tests pass.

**Commit:** `[Sprint 6 / Task 6.6] Sprint 6 complete — queue prioritization verified`

---

# SPRINT 7: THEORY TIER DATA STRUCTURES

## Context

**Read first:**
- `docs/Theory_Tier_Architecture_V1_0.md` — the 8 Tier 1 frameworks with criteria
- `docs/CMR_Revised_Spec_Panel_Templates_V2_0.md` — Templates 1–20 (fully specified)
- `docs/Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md` — Templates 21–30
- `docs/Panel_III_Multimodal_Senses_HigherCognition_V1_0.md` — Templates 31+ and quantitative parameters

This sprint turns the narrative template specifications into queryable data structures. The templates currently exist as rich markdown — causal chains with maturity tags, moderators, scope conditions, parameter ranges, and cross-framework links. CC needs to create Python models that capture this structure so the CMR engine (Sprint 8) can traverse them programmatically.

**Important:** CC does NOT need to encode all 30+ templates in this sprint. CC builds the *data model* and seeds it with 5–8 representative templates. The full encoding will be done incrementally as papers are processed.

## Task 7.1: Create Tier 1 Framework model

**Do:** Create `src/theory/frameworks.py`:

```python
@dataclass
class FrameworkScopeDeclaration:
    """What variables/processes this framework covers."""
    central_variables: List[str]       # variables this framework speaks to directly
    peripheral_variables: List[str]    # variables it touches indirectly
    processes_covered: List[str]       # mechanisms within scope
    does_not_apply_to: List[str]       # explicit exclusions
    neural_substrates: List[str]       # brain regions / systems

@dataclass
class FrameworkPrediction:
    """A prediction this framework makes about environmental effects."""
    prediction_id: str
    statement: str                     # natural language prediction
    quantitative: bool = False         # does it predict specific values?
    ci_width: Optional[float] = None   # confidence interval width if quantitative
    maturity: str = "how_plausibly"    # how_possibly | how_plausibly | how_actually
    testable: bool = True

@dataclass
class Tier1Framework:
    framework_id: str                  # e.g., "predictive_processing"
    name: str
    core_claim: str
    tier: int = 1

    # Criteria (all must be met for Tier 1 status)
    mechanistic_specificity: bool = True
    cross_domain_generativity: bool = True
    convergent_multimethod_support: bool = True

    # Scope
    scope: Optional[FrameworkScopeDeclaration] = None

    # Predictions
    predictions: List[FrameworkPrediction] = field(default_factory=list)

    # Dependencies (for independence matrix)
    shares_theoretical_core_with: List[str] = field(default_factory=list)
    shares_neural_substrates_with: List[str] = field(default_factory=list)
    independence_scores: Dict[str, float] = field(default_factory=dict)
        # framework_id -> independence score [0,1]

    # Meta
    key_references: List[dict] = field(default_factory=list)
    overall_confidence: float = 0.8
```

**Test:** Instantiate the Predictive Processing framework with scope, 3 predictions, and independence scores for 2 other frameworks.

**Commit:** `[Sprint 7 / Task 7.1] Create Tier1Framework model`

## Task 7.2: Create Mechanistic Template model

**Do:** Create `src/theory/templates.py`:

```python
class MaturityLevel(str, Enum):
    HOW_POSSIBLY = "how_possibly"      # speculative
    HOW_PLAUSIBLY = "how_plausibly"    # supported conjecture
    HOW_ACTUALLY = "how_actually"      # confirmed mechanism

class BridgingQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CausalLink:
    """One step in a mechanistic template's causal chain."""
    link_id: str
    from_variable: str                 # entity/variable at start
    to_variable: str                   # entity/variable at end
    activity: str                      # what happens (natural language)
    from_level: str                    # ecological | computational | molecular | systems | psychological
    to_level: str
    bridging_quality: BridgingQuality = BridgingQuality.MEDIUM
    maturity: MaturityLevel = MaturityLevel.HOW_PLAUSIBLY
    evidence_summary: str = ""
    parameter_range: Optional[str] = None  # e.g., "15-30% cortisol reduction"
    temporal_dynamics: Optional[str] = None  # e.g., "onset 130ms, peak 300ms"

@dataclass
class ModerationEffect:
    """A variable that modulates the template's operation."""
    moderator_variable: str
    effect_description: str
    direction: str = "amplifies"       # amplifies | attenuates | reverses | shifts_peak
    evidence_strength: str = "moderate"

@dataclass
class ScopeCondition:
    """When this template does/doesn't apply."""
    condition: str                     # natural language description
    applies_when: bool = True          # True = required for template to work; False = template breaks
    evidence: str = ""

@dataclass
class MechanisticTemplate:
    template_id: str                   # e.g., "PP_SPECTRAL_MATCH_001"
    name: str                          # short descriptive name
    source_framework_ids: List[str]    # which Tier 1 framework(s) this derives from
    recommended_by: str = ""           # panelist who recommended it

    # Structure
    structural_pattern: str            # e.g., "environmental_feature → neural_process → outcome"
    higher_order_principle: str        # the transferable insight
    transferable_to: List[str] = field(default_factory=list)

    # Causal chain (the core mechanism)
    causal_chain: List[CausalLink] = field(default_factory=list)

    # Modifiers
    moderators: List[ModerationEffect] = field(default_factory=list)
    scope_conditions: List[ScopeCondition] = field(default_factory=list)
    known_interactions: List[str] = field(default_factory=list)  # template IDs this connects to

    # Assessment
    overall_maturity: MaturityLevel = MaturityLevel.HOW_PLAUSIBLY
    key_references: List[dict] = field(default_factory=list)

    # Variables index (auto-populated from causal chain)
    @property
    def all_variables(self) -> set:
        vars = set()
        for link in self.causal_chain:
            vars.add(link.from_variable)
            vars.add(link.to_variable)
        return vars
```

**Test:** Instantiate Template 21 (PP_ACTIVE_INFERENCE_003) with its full 4-link causal chain, 3 moderators, and 2 scope conditions from `docs/Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md`. Verify `all_variables` returns the correct set.

**Commit:** `[Sprint 7 / Task 7.2] Create MechanisticTemplate model`

## Task 7.3: Create the variable-to-framework index

**Do:** Create `src/theory/variable_index.py`:

```python
@dataclass
class VariableMatch:
    framework_id: str
    match_strength: str = "central"  # central | peripheral
    template_ids: List[str] = field(default_factory=list)

class VariableFrameworkIndex:
    """
    Many-to-many mapping: which frameworks speak to which variables.
    This is what CMR Step 2 (Framework Matching) queries.
    """
    def __init__(self):
        self._index: Dict[str, List[VariableMatch]] = {}

    def register(self, variable: str, framework_id: str,
                 strength: str = "central", template_ids: list = None):
        if variable not in self._index:
            self._index[variable] = []
        self._index[variable].append(VariableMatch(
            framework_id=framework_id,
            match_strength=strength,
            template_ids=template_ids or []
        ))

    def match(self, variable: str) -> List[VariableMatch]:
        """Find all frameworks that speak to this variable."""
        return self._index.get(variable, [])

    def match_central(self, variable: str) -> List[VariableMatch]:
        """Only central matches."""
        return [m for m in self.match(variable) if m.match_strength == "central"]

    def build_from_templates(self, templates: List[MechanisticTemplate]):
        """Auto-populate index from template causal chains."""
        for template in templates:
            for var in template.all_variables:
                for fw_id in template.source_framework_ids:
                    self.register(var, fw_id, "central", [template.template_id])

    def frameworks_for_finding(self, variables: List[str]) -> Dict[str, List[VariableMatch]]:
        """
        Given a decomposed finding's variables, return all matching frameworks.
        This is the core query for CMR Step 2.
        """
        result = {}
        for var in variables:
            matches = self.match(var)
            if matches:
                result[var] = matches
        return result
```

**Test:**
```python
idx = VariableFrameworkIndex()
idx.register("cortisol", "neuromodulatory_systems", "central", ["NM_THREAT_HPA_001"])
idx.register("cortisol", "interoceptive_inference", "peripheral", ["IC_INTEROCEPTIVE_AFFECT_001"])
idx.register("cortisol", "dmn_tpn_dynamics", "peripheral", ["DMN_METABOLIC_001"])

matches = idx.match("cortisol")
assert len(matches) == 3

central = idx.match_central("cortisol")
assert len(central) == 1
assert central[0].framework_id == "neuromodulatory_systems"
```

**Commit:** `[Sprint 7 / Task 7.3] Create variable-to-framework index`

## Task 7.4: Create the framework independence matrix

**Do:** Create `src/theory/independence.py`:

```python
# Per CMR Spec V1.0, Step 5: Cross-Framework Convergence Assessment
#
# Independence scores determine whether convergent predictions from
# multiple frameworks are genuinely independent or pseudo-convergent.
#
# Read: docs/CMR_Spec_V1_0.md § Step 5

INDEPENDENCE_MATRIX = {
    # (framework_a, framework_b): independence_score
    # 1.0 = fully independent theories
    # 0.0 = same theory repackaged

    ("predictive_processing", "interoceptive_inference"): 0.2,  # II IS PP applied to body
    ("predictive_processing", "spatial_navigation"): 0.8,       # different substrates, origins
    ("predictive_processing", "dual_process"): 0.6,             # PP subsumes implicit/explicit
    ("predictive_processing", "dmn_tpn"): 0.5,                  # DMN interpretable via PP
    ("predictive_processing", "neuromodulatory"): 0.7,          # neuromod = precision mechanism
    ("predictive_processing", "embodied_cognition"): 0.5,       # active inference ≈ embodied
    ("predictive_processing", "circadian"): 0.9,                # largely independent
    ("spatial_navigation", "embodied_cognition"): 0.5,          # overlapping sensorimotor
    ("dmn_tpn", "neuromodulatory"): 0.4,                        # shared neural substrates
    ("neuromodulatory", "circadian"): 0.6,                      # melatonin/cortisol overlap
    ("interoceptive_inference", "neuromodulatory"): 0.4,        # interoception = body neuromod
    # ... extend as needed
}

def get_independence(fw_a: str, fw_b: str) -> float:
    """Symmetric lookup. Default 0.7 for unspecified pairs."""
    key = tuple(sorted([fw_a, fw_b]))
    return INDEPENDENCE_MATRIX.get(key,
           INDEPENDENCE_MATRIX.get((fw_a, fw_b),
           INDEPENDENCE_MATRIX.get((fw_b, fw_a), 0.7)))

def effective_independence(framework_ids: List[str]) -> float:
    """
    For a set of frameworks predicting the same thing,
    compute effective independence (not just count).
    """
    if len(framework_ids) <= 1:
        return 1.0
    pairs = [(a, b) for i, a in enumerate(framework_ids)
             for b in framework_ids[i+1:]]
    avg_independence = sum(get_independence(a, b) for a, b in pairs) / len(pairs)
    return avg_independence * len(framework_ids)  # effective independent lines
```

**Test:**
```python
# PP + interoception: low independence (they share theoretical core)
assert get_independence("predictive_processing", "interoceptive_inference") < 0.3

# PP + spatial nav: high independence
assert get_independence("predictive_processing", "spatial_navigation") > 0.7

# 3 frameworks: PP, spatial_nav, neuromod → should have decent effective independence
eff = effective_independence(["predictive_processing", "spatial_navigation", "neuromodulatory"])
assert eff > 1.5  # more than 1 effective independent line
```

**Commit:** `[Sprint 7 / Task 7.4] Create framework independence matrix`

## Task 7.5: Seed 5–8 representative templates

**Do:** Create `src/theory/seed_templates.py`.

Encode these templates from the docs as MechanisticTemplate instances:

1. **PP_SPECTRAL_MATCH_001** (Template 1, from CMR V2.0 Part III)
2. **PP_COMPLEXITY_GOLDILOCKS_002** (Template 2, from CMR V2.0 Part III)
3. **PP_ACTIVE_INFERENCE_003** (Template 21, from Panel II)
4. **PP_RAPID_GIST_004** (Template 22, from Panel II)
5. **SN_LAYOUT_COGNITIVE_MAP_001** (Template 3, from CMR V2.0 Part III)
6. **NM_THREAT_HPA_001** (Template 5, from CMR V2.0 Part III)
7. **IC_INTEROCEPTIVE_AFFECT_001** (Template 12, from CMR V2.0 Part III)
8. **ALLOSTATIC_EFFICIENCY_MASTER_001** (Template 27, from Panel II — Sterling)

For each, read the full specification from the relevant docs file and encode:
- All causal chain links with maturity tags and bridging quality
- At least 2 moderators
- At least 1 scope condition
- Key references
- `known_interactions` (which other templates it connects to)

**Test:** Load all 8 templates. For each, verify:
- `len(causal_chain) >= 3`
- `all_variables` returns a non-empty set
- `overall_maturity` is set
- `source_framework_ids` is non-empty

**Commit:** `[Sprint 7 / Task 7.5] Seed 8 representative mechanistic templates`

## Task 7.6: Seed the 8 Tier 1 Frameworks

**Do:** Create `src/theory/seed_frameworks.py`.

Encode all 8 Tier 1 frameworks from `docs/Theory_Tier_Architecture_V1_0.md`:

1. Predictive Processing / Active Inference / Free Energy
2. Spatial Navigation and Cognitive Mapping
3. Dual-Process Theory
4. Default Mode Network vs. Task-Positive Network
5. Neuromodulatory Systems
6. Interoceptive Inference and Affect Construction
7. Circadian and Chronobiological Regulation
8. Embodied Cognition and Affordances

For each, encode:
- `scope`: central_variables, peripheral_variables, processes_covered, does_not_apply_to, neural_substrates
- `predictions`: at least 3 architectural predictions per framework (from the docs)
- `independence_scores`: populate from the matrix in Task 7.4
- `key_references`: at least 3 per framework

**Test:** Load all 8. Verify each has scope, ≥3 predictions, ≥2 independence scores.

**Commit:** `[Sprint 7 / Task 7.6] Seed 8 Tier 1 frameworks`

## Task 7.7: Build variable index from seeded templates

**Do:** Write a script that:
1. Loads all seeded templates
2. Calls `VariableFrameworkIndex.build_from_templates()`
3. Saves the index (JSON or pickle)
4. Prints a summary: how many variables, how many have multiple framework matches

**Test:** The index contains ≥20 variables. At least 5 variables have matches from ≥2 frameworks (e.g., "cortisol", "prediction_error", "cognitive_map").

**Commit:** `[Sprint 7 / Task 7.7] Build variable-to-framework index from seed data`

## Task 7.8: Full test suite for Sprint 7

**Do:** `pytest tests/ -v`

**Test:** No regressions. All Sprint 7 tests pass.

**Commit:** `[Sprint 7 / Task 7.8] Sprint 7 complete — theory tier data structures verified`

---

# SPRINT 8: CMR PIPELINE SCAFFOLDING

## Context

**Read first:**
- `docs/CMR_Spec_V1_0.md` — the full 6-step pipeline specification
- `docs/CMR_Revised_Spec_Panel_Templates_V2_0.md` — the expert panel's 15 corrections

This sprint builds the skeleton of the Compositional Mechanistic Reasoning engine. The CMR engine is what transforms Article Eater from a knowledge organizer into a hypothesis generator. It takes a finding, decomposes it, matches it to Tier 1 frameworks, traces mechanisms through templates, and generates novel predictions.

**Important:** This sprint builds the pipeline *structure* and tests it with the seeded templates from Sprint 7. Full production use requires encoding many more templates (an ongoing process). The pipeline should be designed to work with whatever templates are available, gracefully degrading when coverage is incomplete.

## Task 8.1: Implement Step 1 — Causal Decomposition

**Do:** Create `src/cmr/decomposition.py`:

```python
@dataclass
class DecomposedFinding:
    original_text: str
    environmental_stimulus: str
    outcome_variables: List[str]
    candidate_mediators: List[str]
    population: str = ""
    context: str = ""
    observed_variables: List[str] = field(default_factory=list)
    inferred_variables: List[str] = field(default_factory=list)

# Decomposition templates for common finding types
DECOMPOSITION_TEMPLATES = {
    "env_affects_outcome": {
        # "Environmental feature X affects outcome Y"
        "decompose_outcome_into": [
            "physiological_component",
            "cognitive_component",
            "affective_component",
            "behavioral_component",
        ]
    },
    "env_preference": {
        # "People prefer environment X over Y"
        "decompose_outcome_into": [
            "explicit_evaluation",
            "implicit_affect",
            "approach_behavior",
            "physiological_response",
        ]
    },
    # Add more templates as patterns emerge
}

def decompose_finding(finding_text: str, finding_type: str = "env_affects_outcome") -> DecomposedFinding:
    """
    Step 1 of CMR: Break finding into component causal variables.

    Per Bechtel & Richardson (1993/2010) decomposition strategy.

    Note: In production, this will be LLM-assisted with structured output.
    For now, implement keyword extraction + template application.
    """
    # Implementation: extract key variables from text
    # Apply decomposition template to expand outcome
    # Classify variables as observed vs. inferred
    pass  # CC implements extraction logic
```

**Test:** Decompose "Nature views speed hospital recovery" → should produce environmental_stimulus = "nature_view", outcome_variables should include "recovery_time" and decomposed components.

**Commit:** `[Sprint 8 / Task 8.1] Implement CMR Step 1 — Causal Decomposition`

## Task 8.2: Implement Step 2 — Framework Matching

**Do:** Create `src/cmr/matching.py`:

```python
@dataclass
class FrameworkMatchResult:
    variable: str
    framework_id: str
    match_strength: str  # central | peripheral
    template_ids: List[str]
    relevance_score: float = 0.0

def match_frameworks(
    decomposed: DecomposedFinding,
    index: VariableFrameworkIndex,
    frameworks: Dict[str, Tier1Framework]
) -> List[FrameworkMatchResult]:
    """
    Step 2 of CMR: For each variable in the decomposed finding,
    find frameworks that have something to say about it.

    Per Darden (2002) schema instantiation.

    Returns matches sorted by relevance.
    """
    all_variables = (
        [decomposed.environmental_stimulus] +
        decomposed.outcome_variables +
        decomposed.candidate_mediators
    )

    results = []
    for var in all_variables:
        matches = index.frameworks_for_finding([var])
        for matched_var, match_list in matches.items():
            for m in match_list:
                results.append(FrameworkMatchResult(
                    variable=matched_var,
                    framework_id=m.framework_id,
                    match_strength=m.match_strength,
                    template_ids=m.template_ids,
                ))

    # Deduplicate and rank
    # Central matches score higher than peripheral
    for r in results:
        r.relevance_score = 1.0 if r.match_strength == "central" else 0.5

    return sorted(results, key=lambda r: r.relevance_score, reverse=True)
```

**Test:** Decompose "Nature views speed hospital recovery", match against the seeded index. Should match at least: predictive_processing (via prediction_error), neuromodulatory (via cortisol), dmn_tpn (via attentional demand).

**Commit:** `[Sprint 8 / Task 8.2] Implement CMR Step 2 — Framework Matching`

## Task 8.3: Implement Step 3 — Mechanism Tracing

**Do:** Create `src/cmr/tracing.py`:

```python
@dataclass
class MechanismTrace:
    """A traced causal path through one or more templates."""
    trace_id: str
    finding: str
    framework_ids: List[str]
    template_ids: List[str]
    links: List[CausalLink]          # ordered chain from stimulus to outcome
    weakest_maturity: MaturityLevel   # bottleneck maturity
    cross_framework_bridges: List[str]  # where trace crosses framework boundaries
    overall_confidence: float = 0.0

def trace_mechanism(
    stimulus_variable: str,
    outcome_variable: str,
    matched_templates: List[MechanisticTemplate],
) -> List[MechanismTrace]:
    """
    Step 3 of CMR: Trace causal chains from stimulus through templates to outcome.

    Per Darden & Craver (2002) forward chaining.

    This is a graph traversal: find paths from stimulus to outcome
    through the causal links in the template library.
    """
    # Build a graph from all causal links across matched templates
    # Find paths from stimulus_variable to outcome_variable
    # Track which templates and frameworks each path traverses
    # Identify cross-framework bridges (where a trace exits one framework)
    # Compute weakest maturity along each path
    pass  # CC implements graph traversal
```

**Test:** With the 8 seeded templates, trace from "nature_view" to "cortisol_reduction". Should find at least one path through predictive processing templates.

**Commit:** `[Sprint 8 / Task 8.3] Implement CMR Step 3 — Mechanism Tracing`

## Task 8.4: Implement Step 4 — Prediction Generation (stub)

**Do:** Create `src/cmr/prediction.py`:

```python
class InterventionistOperation(str, Enum):
    SUBSTITUTE_CAUSE = "substitute_cause"
    VARY_MODERATOR = "vary_moderator"
    BLOCK_PATHWAY = "block_pathway"
    CHANGE_TEMPORAL_CONTEXT = "change_temporal_context"
    VARY_INDIVIDUAL = "vary_individual"
    CROSS_CULTURAL = "cross_cultural"
    ADD_CONCURRENT_MECHANISM = "add_concurrent"
    CHANGE_DOSE = "change_dose"

@dataclass
class GeneratedPrediction:
    prediction_id: str
    statement: str
    derivation_chain: List[str]       # framework and template IDs used
    interventionist_operation: InterventionistOperation
    confidence: float                  # inherits weakest link
    testability: str = "testable"     # testable | difficult | infeasible
    novelty: str = "unknown"          # novel | known | partially_known
    convergence_score: float = 0.0    # how many independent traces support this
    effective_independence: float = 0.0

def generate_predictions(trace: MechanismTrace) -> List[GeneratedPrediction]:
    """
    Step 4 of CMR: Apply interventionist operations to generate predictions.

    Per Woodward (2003) — "If we intervene on variable X, what happens to Y?"

    NOTE: In production, this will be LLM-assisted. For now, implement
    template-based generation for SUBSTITUTE_CAUSE and VARY_MODERATOR only.
    """
    predictions = []
    # For each link in the trace, apply applicable operations
    # SUBSTITUTE_CAUSE: if mechanism is X → Y, any stimulus with property X should → Y
    # VARY_MODERATOR: for each moderator, predict how variation changes outcome
    return predictions
```

**Test:** Given a trace through PP_SPECTRAL_MATCH_001, generate at least one SUBSTITUTE_CAUSE prediction (e.g., "artificial fractal scenes should produce similar effects").

**Commit:** `[Sprint 8 / Task 8.4] Implement CMR Step 4 — Prediction Generation stub`

## Task 8.5: Implement Step 5 — Cross-Framework Convergence

**Do:** Create `src/cmr/convergence.py`:

```python
def assess_convergence(
    predictions: List[GeneratedPrediction],
    independence_fn: callable = get_independence
) -> List[GeneratedPrediction]:
    """
    Step 5 of CMR: Check for convergent predictions from independent frameworks.

    Per Thagard (1989) explanatory coherence at prediction level.

    Groups predictions by semantic similarity of statement,
    computes effective independence for each group.
    """
    # Group predictions by similar outcome
    # For each group, compute effective independence score
    # Update convergence_score and effective_independence on each prediction
    # Flag contradictions (same variable, opposite predicted direction)
    return predictions
```

**Test:** Create 3 predictions from 3 different frameworks all predicting "cortisol reduction." Convergence score should be high. Independence should reflect actual independence matrix values.

**Commit:** `[Sprint 8 / Task 8.5] Implement CMR Step 5 — Cross-Framework Convergence`

## Task 8.6: Implement the CMR orchestrator

**Do:** Create `src/cmr/engine.py`:

```python
class CMREngine:
    def __init__(self, frameworks, templates, variable_index, independence_fn):
        self.frameworks = frameworks
        self.templates = templates
        self.variable_index = variable_index
        self.independence_fn = independence_fn

    def process_finding(self, finding_text: str) -> dict:
        """
        Run the full CMR pipeline on a finding.

        Returns:
        {
            "decomposition": DecomposedFinding,
            "framework_matches": List[FrameworkMatchResult],
            "mechanism_traces": List[MechanismTrace],
            "predictions": List[GeneratedPrediction],
            "convergence_summary": dict,
        }
        """
        # Step 1: Decompose
        decomposed = decompose_finding(finding_text)

        # Step 2: Match
        matches = match_frameworks(decomposed, self.variable_index, self.frameworks)

        # Step 3: Trace
        matched_template_ids = set()
        for m in matches:
            matched_template_ids.update(m.template_ids)
        matched_templates = [self.templates[tid] for tid in matched_template_ids
                           if tid in self.templates]

        traces = []
        for outcome in decomposed.outcome_variables:
            traces.extend(trace_mechanism(
                decomposed.environmental_stimulus, outcome, matched_templates
            ))

        # Step 4: Predict
        all_predictions = []
        for trace in traces:
            all_predictions.extend(generate_predictions(trace))

        # Step 5: Convergence
        all_predictions = assess_convergence(all_predictions, self.independence_fn)

        return {
            "decomposition": decomposed,
            "framework_matches": matches,
            "mechanism_traces": traces,
            "predictions": all_predictions,
            "convergence_summary": {
                "total_predictions": len(all_predictions),
                "convergent_groups": len(set(p.statement for p in all_predictions)),
                "max_convergence": max((p.convergence_score for p in all_predictions), default=0),
            }
        }
```

**Test:** Process "Nature views speed hospital recovery" through the full pipeline with seeded data. Should produce at least 1 mechanism trace and at least 1 prediction without errors.

**Commit:** `[Sprint 8 / Task 8.6] Implement CMR orchestrator`

## Task 8.7: Full test suite for Sprint 8

**Do:** `pytest tests/ -v`

**Test:** No regressions. All Sprint 8 tests pass.

**Commit:** `[Sprint 8 / Task 8.7] Sprint 8 complete — CMR pipeline scaffolding verified`

---

# SPRINT 9: PIPELINE HEALTH & EXPECTATION TESTS

## Context

**Read first:** `docs/Pipeline_Expectation_Tests.md`

This sprint creates systematic health checks for the full pipeline. These run as CI gates to catch regressions, ensure extraction quality, and verify that the epistemic machinery is working as intended.

## Task 9.1: Policy guardrail unit tests

**Do:** Create `tests/test_realtime_pipeline_guardrails.py`:

Per `docs/Pipeline_Expectation_Tests.md` § 1:
- Abstract rule gate allows confident empirical families
- Abstract rule gate defers non-empirical/uncertain families
- PDF claim rows from uncertain article types marked `needs_verification=true`
- `quality_flag` includes `needs_article_type_verification` where appropriate

**Test:** `pytest -q tests/test_realtime_pipeline_guardrails.py`

**Commit:** `[Sprint 9 / Task 9.1] Add policy guardrail unit tests`

## Task 9.2: Data-level expectation gate

**Do:** Create `scripts/verify_pipeline_expectations.py`:

Per `docs/Pipeline_Expectation_Tests.md` § 2:
- No queue row regresses from `completed_pdf_extracted` to timeout/error/no-claims
- In confirmed tranche rows, `needs_verification=true` rate ≥ 0.95 threshold
- `quality_flag` marker rate ≥ 0.95 threshold
- Script outputs `expectation_gate: PASS` or `expectation_gate: FAIL` with details

**Test:** `python3 scripts/verify_pipeline_expectations.py` → `expectation_gate: PASS`

**Commit:** `[Sprint 9 / Task 9.2] Add data-level expectation gate`

## Task 9.3: Corpus health gate

**Do:** Create `scripts/check_table_extraction_quality.py`:

Per `docs/Pipeline_Expectation_Tests.md` § 3:
- Global extraction health and coverage tracking
- Reports completeness rate, error rate, claim yield per paper
- Outputs `quality_gate: PASS` or `quality_gate: FAIL`

**Test:** `python3 scripts/check_table_extraction_quality.py` → `quality_gate: PASS`

**Commit:** `[Sprint 9 / Task 9.3] Add corpus health gate`

## Task 9.4: Epistemic health dashboard data

**Do:** Create `scripts/epistemic_health_report.py`:

Generate a summary report covering all epistemic systems:
- Web of belief stats: total nodes, edges, coherence distribution
- Source quality distribution across claims
- Asymmetry monitor summary (how many claims are over-entrenched?)
- Structural bias summary (how many single-lab clusters?)
- Queue stats (HIGH/MEDIUM/LOW distribution, stale count)
- Theory coverage: how many Tier 1 predictions have supporting evidence?
- CMR capacity: how many templates seeded, how many variables indexed?

Output as JSON for potential dashboard consumption.

**Test:** Script runs without error and produces valid JSON with all fields.

**Commit:** `[Sprint 9 / Task 9.4] Add epistemic health report script`

## Task 9.5: Full regression suite

**Do:** `pytest tests/ -v && python3 scripts/verify_pipeline_expectations.py && python3 scripts/check_table_extraction_quality.py`

**Test:** All pass.

**Commit:** `[Sprint 9 / Task 9.5] Sprint 9 complete — pipeline health verified`

---

# UPDATED SPRINT SUMMARY

| Sprint | Focus | Tasks | Depends On | Est. Duration | Key Deliverable |
|--------|-------|-------|------------|---------------|-----------------|
| 0 | Discovery | 0.1–0.2 | — | 1 day | Codebase map |
| 1 | Schema Extensions | 1.1–1.11 | Sprint 0 | 1–2 weeks | Extended schema |
| 2 | BN Integration | 2.1–2.6 | Sprint 1 | 1–2 weeks | Epistemic BN subgraph |
| 3 | Reflexive Monitoring | 3.1–3.5 | Sprint 2 | 2 weeks | 4 monitoring tools |
| 4 | Extraction Extensions | 4.1–4.5 | Sprint 1 | 1–2 weeks | Extended extractor |
| 4b | Method Registry | 4b.1–4b.7 | Sprint 1 | 2 weeks | Method registry + validity scoring |
| 5 | Integration Testing | 5.1–5.8 | Sprints 1–4b | 2 weeks | Validated epistemic system |
| **6** | **Queue Prioritization** | **6.1–6.6** | **Sprint 2** | **1–2 weeks** | **Priority scoring + satisficing** |
| **7** | **Theory Tier Data** | **7.1–7.8** | **Sprint 1** | **2–3 weeks** | **Framework + template models, variable index** |
| **8** | **CMR Scaffolding** | **8.1–8.7** | **Sprint 7** | **2–3 weeks** | **6-step CMR pipeline** |
| **9** | **Pipeline Health** | **9.1–9.5** | **Sprint 5** | **1 week** | **CI gates + health report** |

**Total estimated: 16–22 weeks** (with parallelization: 12–16 weeks)

**Critical path:** 0 → 1 → 2 → 3 → 5 → 9 (epistemic core)
**Parallel track A:** 1 → 7 → 8 (theory + CMR)
**Parallel track B:** 1 → 4/4b → 5 (extraction + validation)
**Parallel track C:** 2 → 6 (queue)

---

# NOTES FOR CC

1. **Always read the referenced doc files before starting a sprint.** The docs contain design decisions, edge cases, and rationale that aren't repeated in the task specs.

2. **The theory tier data (Sprint 7) is the most judgment-heavy.** If unsure how to encode a template's causal chain or scope conditions, look at the worked example in `docs/CMR_Revised_Spec_Panel_Templates_V2_0.md` Part III — every template there has the full format.

3. **Sprint 8 (CMR) will be LLM-assisted in production.** Steps 1 (decomposition) and 4 (prediction generation) will eventually use Claude API calls. For now, implement keyword-based approximations that demonstrate the pipeline structure. The important thing is the *data flow*, not the NLP quality.

4. **Don't gold-plate.** Per Simon (and the Queue panel): satisfice. Get the pipeline working with 8 templates first. More templates will be added incrementally.

5. **Check `git log --oneline -20` at the start of each session** to see where you left off. Read CLAUDE.md and this file to re-orient.
