# QA Agent Specification: Amendments from Query Testing

**Date**: February 16, 2026
**Source**: Testing query "Do wood walls reduce stress as much as plants in a room?"

---

## Amendment 1: Distinguish Confidence from Effect Size

### Problem Discovered
The spec conflates "confidence" and "effect size." The actual data structure has:
- **Edge confidence** (0.75) = how sure we are the pathway exists
- **Effect size** (Cohen's d, r) = how large the effect is

These are different. A pathway can have high confidence (we're sure it exists) but small effect size (it doesn't do much).

### Spec Change

Add to **Part VI: Response Templates**:

```markdown
### Confidence vs Effect Size Vocabulary

| Concept | Data Source | User-Facing Language |
|---------|-------------|---------------------|
| Pathway confidence | `mechanism.confidence` | "well-established," "strong evidence" |
| Effect magnitude | `claim.effect_size` | "large effect (d > 0.8)," "small effect" |
| Pathway reliability | confidence × replication_rate | "robust," "preliminary" |

**Rule**: Never say "strong effect" when you mean "strong evidence." Distinguish:
- "There is strong evidence that X reduces Y" (confidence)
- "X strongly reduces Y" (effect magnitude)
```

---

## Amendment 2: Add Comparative Question Subtypes

### Problem Discovered
"Do wood walls reduce stress *as much as* plants?" has three interpretations:
1. Do both work? (existence comparison)
2. Which works more? (magnitude comparison)
3. Do they work the same way? (mechanism comparison)

The spec's single "COMPARATIVE_WHY" type is too coarse.

### Spec Change

Replace `COMPARATIVE_WHY` with three subtypes:

```python
class QuestionType(Enum):
    # ... existing types ...

    # Category C: Explanatory - Comparative subtypes
    COMPARATIVE_EXISTENCE = "comparative_existence"  # "Do both X and Y affect Z?"
    COMPARATIVE_MAGNITUDE = "comparative_magnitude"  # "Does X affect Z more than Y?"
    COMPARATIVE_MECHANISM = "comparative_mechanism"  # "Do X and Y work the same way?"
```

**Detection heuristics:**
- "as much as," "more than," "stronger" → COMPARATIVE_MAGNITUDE
- "same way," "differently," "same mechanism" → COMPARATIVE_MECHANISM
- "both," "and/or" → COMPARATIVE_EXISTENCE

---

## Amendment 3: Add Pathway Comparison Logic

### Problem Discovered
Plants reduce stress via TWO pathways; wood via ONE. This matters for:
- Robustness (multiple pathways = more reliable effect)
- Mechanism understanding (different routes = different intervention points)
- Effect summation (do pathways add up?)

The spec doesn't address multi-pathway reasoning.

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
@dataclass
class PathwayAnalysis:
    """Analysis of all causal pathways between factor and outcome."""

    source: str  # e.g., "plant_density"
    target: str  # e.g., "stress"
    pathways: List[CausalPathway]

    @property
    def pathway_count(self) -> int:
        return len(self.pathways)

    @property
    def aggregate_confidence(self) -> float:
        """Combined confidence across all pathways."""
        # Don't just average—multiple pathways increase robustness
        if not self.pathways:
            return 0.0
        max_conf = max(p.confidence for p in self.pathways)
        # Bonus for redundancy: each additional pathway adds 10% to confidence
        redundancy_bonus = min(0.2, 0.1 * (len(self.pathways) - 1))
        return min(0.99, max_conf + redundancy_bonus)

    @property
    def robustness(self) -> str:
        """Qualitative robustness assessment."""
        if self.pathway_count >= 2:
            return "robust (multiple independent pathways)"
        elif self.pathway_count == 1:
            return "single pathway"
        return "no pathway found"

def compare_pathways(
    factor_a: str,
    factor_b: str,
    outcome: str
) -> PathwayComparison:
    """Compare causal pathways for two factors affecting same outcome."""
    pathways_a = analyze_pathways(factor_a, outcome)
    pathways_b = analyze_pathways(factor_b, outcome)

    return PathwayComparison(
        factor_a=factor_a,
        factor_b=factor_b,
        outcome=outcome,
        a_pathways=pathways_a,
        b_pathways=pathways_b,
        shared_mediators=find_shared_mediators(pathways_a, pathways_b),
        comparison_type=infer_comparison_type(pathways_a, pathways_b)
    )
```

---

## Amendment 4: Add Missing Data Handling Protocol

### Problem Discovered
No direct wood-vs-plants comparison study exists. The system must:
1. Acknowledge the gap
2. Reason from indirect evidence
3. Flag as research opportunity

### Spec Change

Add to **Part VIII: Quality Criteria**:

```markdown
### Missing Data Protocol

When direct evidence for a question doesn't exist:

**Level 1: Acknowledge**
> "No direct comparison studies were found."

**Level 2: Indirect Reasoning**
> "Based on separate pathways: [A has X pathways with aggregate confidence Y; B has...]"

**Level 3: Gap Flagging**
If user is researcher/PhD:
> "This represents a research gap. A direct comparison study would need to..."

**Required phrases by data availability:**

| Data State | Required Phrase |
|------------|----------------|
| Direct evidence exists | "Studies directly comparing X and Y show..." |
| Only indirect evidence | "No direct comparison found. Based on separate evidence..." |
| One factor well-studied, other not | "X is well-studied; Y has limited evidence..." |
| Neither well-studied | "Both factors have limited evidence..." |
```

---

## Amendment 5: Leverage Goldilocks Parameters

### Problem Discovered
The mechanism registry has rich Goldilocks data (optimal values, widths, asymmetry) that the spec ignores. This enables dosage-specific answers.

### Spec Change

Add question type:

```python
class QuestionType(Enum):
    # ... existing types ...
    DOSAGE_OPTIMIZATION = "dosage_optimization"  # "How much X is optimal?"
```

Add to **Part VI: Response Templates**:

```markdown
### Template: Dosage Optimization Questions

**Question pattern**: "How much X is best?" / "What's the optimal level of X?"

| Depth | Structure |
|-------|-----------|
| L1 | Optimal value + confidence |
| L2 | L1 + tolerance range + asymmetry warning |
| L3 | L2 + mechanism for low/high/optimal + individual differences |

**Example at L2**:
> "Optimal wood coverage is approximately 40% of visible surfaces (±15%).
> The effect is asymmetric—too much wood (>55%) is worse than too little,
> creating dark, enclosed feelings. Below 25%, insufficient biophilic signal."

**Data mapping**:
- `goldilocks.optimal_value` → "approximately X%"
- `goldilocks.optimal_width` → "±Y%"
- `goldilocks.asymmetry` → "too much is worse" / "too little is worse" / "symmetric"
- `goldilocks.mechanism_for_low` → L3 explanation
- `goldilocks.mechanism_for_high` → L3 explanation
```

---

## Amendment 6: Add Shared Theory Detection

### Problem Discovered
Both wood and plants share the same theoretical base (Biophilia, ART, SRT). This is important for:
- Understanding why both work
- Predicting interactions (might not add up if same mechanism)
- Suggesting that one might substitute for the other

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
def find_shared_theories(
    factor_a: str,
    factor_b: str
) -> SharedTheoryAnalysis:
    """Identify shared theoretical alignment between two factors."""
    theories_a = get_theories_for_factor(factor_a)  # e.g., {"Biophilia", "ART", "SRT"}
    theories_b = get_theories_for_factor(factor_b)  # e.g., {"Biophilia", "ART"}

    shared = theories_a & theories_b
    unique_a = theories_a - theories_b
    unique_b = theories_b - theories_a

    return SharedTheoryAnalysis(
        shared_theories=shared,
        unique_to_a=unique_a,
        unique_to_b=unique_b,
        substitutability=len(shared) / len(theories_a | theories_b),
        additivity_warning=len(shared) > 0  # Same mechanism = may not add up
    )
```

**Response integration**:
> "Both wood and plants work through the same theoretical mechanisms (Biophilia, SRT),
> suggesting they may be partially substitutable. Adding both may not double the effect—
> they're tapping the same psychological systems."

---

## Amendment 7: Add Quantitative Comparison Handling

### Problem Discovered
"As much as" demands quantitative comparison, but:
- Effect sizes may be in different units (d vs r vs β)
- Pathway confidence ≠ effect magnitude
- Need to convert or caveat

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
@dataclass
class QuantitativeComparison:
    """Result of comparing effect magnitudes."""

    factor_a: str
    factor_b: str
    outcome: str

    # If direct effect sizes available
    effect_size_a: Optional[float]
    effect_size_b: Optional[float]
    effect_type: Optional[str]  # "cohens_d", "correlation", "beta"

    # If only pathway confidence available
    pathway_confidence_a: float
    pathway_confidence_b: float

    comparison_basis: str  # "direct_effect_size" | "pathway_confidence" | "insufficient_data"

    def generate_comparison_statement(self) -> str:
        if self.comparison_basis == "direct_effect_size":
            if self.effect_size_a > self.effect_size_b * 1.2:
                return f"{self.factor_a} has a larger effect than {self.factor_b}"
            elif self.effect_size_b > self.effect_size_a * 1.2:
                return f"{self.factor_b} has a larger effect than {self.factor_a}"
            else:
                return f"{self.factor_a} and {self.factor_b} have similar effect sizes"
        elif self.comparison_basis == "pathway_confidence":
            return (
                f"Cannot directly compare magnitudes. "
                f"Both pathways are moderately supported "
                f"({self.factor_a}: {self.pathway_confidence_a:.0%}, "
                f"{self.factor_b}: {self.pathway_confidence_b:.0%})"
            )
        else:
            return "Insufficient data for quantitative comparison"
```

**Response template for magnitude comparison:**
> "Direct effect size comparison is not available in the knowledge base.
> Based on pathway analysis: wood→stress has 64% pathway confidence;
> plants→stress has ~70% via two independent routes.
> Plants may have a slight edge due to pathway redundancy, but
> a direct comparison study would be needed to quantify the difference."

---

## Amendment 8: Refine Question Classification Heuristics

### Problem Discovered
The query "Do wood walls reduce stress as much as plants" contains multiple signals:
- "Do" → existence question
- "as much as" → magnitude comparison
- Two factors → comparative

Need disambiguation logic.

### Spec Change

Add to **Appendix A: Question Classification Heuristics**:

```markdown
### Compound Question Handling

When multiple question types are detected:

1. **Primary type** = most specific detected type
2. **Secondary type(s)** = additional detected types
3. **Response structure** = answer primary, then address secondary

**Priority order** (most specific first):
1. COMPARATIVE_MAGNITUDE ("as much as", "more than")
2. COMPARATIVE_MECHANISM ("same way", "different mechanism")
3. COMPARATIVE_EXISTENCE ("both", "and")
4. EFFECT_SIZE ("how much")
5. EFFECT_EXISTENCE ("does X affect Y")

**Example classification:**
Query: "Do wood walls reduce stress as much as plants?"
- Detected: EFFECT_EXISTENCE + COMPARATIVE_MAGNITUDE
- Primary: COMPARATIVE_MAGNITUDE (more specific)
- Response: Lead with magnitude comparison, then confirm both effects exist
```

---

## Amendment 9: Add Research Gap Surfacing

### Problem Discovered
The query revealed a genuine research gap (no direct comparison studies). This is valuable information for researchers.

### Spec Change

Add question type:

```python
class QuestionType(Enum):
    # ... existing types ...

    # Category F: Generative - New type
    COMPARISON_GAP = "comparison_gap"  # Detected when comparative Q lacks direct evidence
```

Add to **Part V: Progressive Disclosure Architecture**:

```markdown
### Automatic Gap Detection

When answering comparative questions without direct evidence:

**For L3+ responses to researchers/PhDs:**
Append gap identification:
> "**Research Gap Identified**: No direct comparison of wood surfaces vs.
> indoor plants on stress outcomes was found. A study design could:
> - 2×2 factorial (wood present/absent × plants present/absent)
> - Outcome: salivary cortisol + self-reported stress (STAI)
> - Exposure: 30+ minutes (per enabling conditions for both pathways)
> - This would test additivity vs. substitutability of biophilic elements."

**For applied users (architects):**
> "In the absence of direct comparison data, consider using both elements—
> different pathways suggest they may complement each other."
```

---

## Amendment 10: Proactive Taxonomic Expansion

### Problem Discovered

Query "what effects does noise diminish?" was answered narrowly. Required three follow-up questions (natural sounds? music?) to surface the full acoustic taxonomy. A knowledgeable expert would proactively distinguish sound types without being asked.

### Spec Change

Add to **Part VII: Explanation Principles**:

```markdown
### Principle 8: Proactive Taxonomic Expansion

When answering about environmental factor X or outcome Y, proactively surface the relevant taxonomy rather than waiting for follow-up questions.

**For environmental factors (stimuli):**
1. Identify the domain of X (acoustic, visual, thermal, social, etc.)
2. Retrieve sibling concepts with meaningfully different effects
3. Lead with taxonomy before answering the specific question

**For outcomes:**
1. Identify related outcomes that may also be affected
2. Surface the outcome hierarchy (e.g., stress → cortisol, HRV, self-report)
3. Note when effects diverge across outcome measures

**Example transformation:**

| Question | Narrow Answer | Expanded Answer |
|----------|---------------|-----------------|
| "Does noise reduce focus?" | "Yes, noise reduces focus via..." | "Sound affects focus differently by type: speech (depleting), mechanical (depleting), natural (restorative), music (depends). For noise specifically..." |

**Implementation:**
- Detect domain of query entity
- Query mechanism registry for sibling entities in same domain
- Check for divergent effect directions among siblings
- If divergence exists, lead with taxonomy table
```

Add to **Part IX: Implementation Specification**:

```python
def expand_query_taxonomy(
    entity: str,
    entity_type: Literal["stimulus", "outcome"]
) -> TaxonomicContext:
    """Proactively expand query entity to its taxonomic context."""

    domain = get_domain(entity)  # e.g., "acoustic" for "noise"
    siblings = get_domain_siblings(entity, domain)

    # Check if siblings have divergent effects
    effects = {s: get_effect_direction(s) for s in siblings}
    has_divergence = len(set(effects.values())) > 1

    return TaxonomicContext(
        query_entity=entity,
        domain=domain,
        siblings=siblings,
        effect_directions=effects,
        requires_expansion=has_divergence,
        taxonomy_table=generate_taxonomy_table(siblings, effects) if has_divergence else None
    )
```

**Response template when expansion applies:**

```markdown
[Domain] affects [outcome] differently by type:

| Type | Effect | Mechanism |
|------|--------|-----------|
| [sibling_1] | [direction] | [brief mechanism] |
| [sibling_2] | [direction] | [brief mechanism] |
| ... | ... | ... |

For [query_entity] specifically: [detailed answer]
```

---

## Amendment 11: Query Templates for Theory, Mechanisms for Parameters

### Problem Discovered

The QA spec assumed queries go to the BN mechanism registry. But:
- Templates (web level) already contain rich Tier 1 theory, causal links, scope conditions, interactions
- Templates are already organized by domain (COL1/COL2 = color, VF1-3 = visual form, M1-17 = music, T58/AUD_* = acoustic)
- The taxonomic hierarchy exists in Article Eater — the mechanism registry is flat

The BN mechanism registry was designed for quantitative parameters, not theoretical explanation. Querying mechanisms for "why" questions is querying the wrong layer.

### Spec Change

Add to **Part III: System Architecture**:

```markdown
### Dual-Layer Query Architecture

The QA agent queries TWO knowledge sources for different purposes:

| Query Type | Source | Returns |
|------------|--------|---------|
| "Why does X affect Y?" | Templates (Web of Belief) | Theory, mechanism, scope conditions |
| "How much does X affect Y?" | Mechanisms (BN) | Effect size, goldilocks parameters |
| "What types of X exist?" | Template domain index | Taxonomic siblings |
| "What's the optimal level of X?" | Mechanisms (BN) | Goldilocks optimal_value, width |
| "What theory explains X?" | Templates (Web of Belief) | framework_ids, higher_order_principle |

**Template organization by domain:**

| Domain | Template Prefixes | Content |
|--------|-------------------|---------|
| Acoustic | T58, AUD_*, T19, T31 | Sound types, speech, music |
| Color | COL1, COL2, T24 | Chromatic PE, arousal |
| Visual Form | VF1, VF2, VF3 | Curvature, rhythm, proportion |
| Music | M1-M17 | BRECVEMA mechanisms |
| Light | L1-L5, CB_* | Circadian, luminance |
| Spatial | SC1-SC4, SN_* | Navigation, enclosure |
| Material | MAT1-MAT5 | Touch, thermal, identity |
| Social | SOC1-SOC3, T48-T52 | Privacy, presence |

**Query routing logic:**

```python
def route_query(question: Question) -> QueryPlan:
    """Route question to appropriate knowledge layer."""

    if question.type in [WHY, MECHANISM, THEORY_ALIGNMENT]:
        # Theory questions → templates
        return QueryPlan(
            primary_source="templates",
            secondary_source="mechanisms",  # for parameters
            index_by="domain"
        )

    elif question.type in [EFFECT_SIZE, DOSAGE_OPTIMIZATION, QUANTITATIVE]:
        # Parameter questions → mechanisms
        return QueryPlan(
            primary_source="mechanisms",
            secondary_source="templates",  # for context
            index_by="attribute"
        )

    elif question.type in [TAXONOMY, COMPARATIVE_EXISTENCE]:
        # Taxonomic questions → template domain index
        return QueryPlan(
            primary_source="template_index",
            group_by="domain",
            return_siblings=True
        )
```

**Implication**: The "missing mechanism registry entries" flagged in KBASE_ENHANCEMENT_FLAGS are less critical for theory questions — the templates already have the theory. The gap is in bridging templates to mechanisms for quantitative queries.
```

### Architectural Principle

The Web of Belief contains **theory**. The BN contains **parameters**. The QA agent should:
1. Query templates for explanatory content (why, how, what theory)
2. Query mechanisms for quantitative content (how much, optimal level)
3. Use template domain structure for taxonomic expansion
4. Bridge between layers only when both theory AND parameters are needed

---

## Amendment 12: Multi-Template Synthesis for Design Questions

### Problem Discovered

Design questions like "How should I design a restorative hospital room?" require combining multiple templates (VIEW1 + L2 + SOC2 + T20 + T58). Panel spec assumed single-template answers.

### Spec Change

Add to **Part VI: Response Templates**:

```markdown
### Template: Design Synthesis Questions

**Question pattern**: "How should I design X for Y?" / "What makes a good Z?"

**Response structure**:

1. **Identify relevant domains** for context (e.g., hospital room → view, light, privacy, thermal, acoustic)
2. **Retrieve templates** for each domain
3. **Extract design-relevant parameters** from each
4. **Synthesize** with priority ordering based on effect magnitude and evidence quality
5. **Flag conflicts** where templates have competing recommendations

**Example synthesis for "restorative hospital room"**:

| Domain | Template | Key Recommendation | Priority |
|--------|----------|-------------------|----------|
| View | VIEW1 | Nature view with water, vegetation | HIGH (established) |
| Light | L2 | High mEDI morning, dim evening; age-correct | HIGH (established) |
| Privacy | SOC2 | Visual + acoustic privacy mechanisms | HIGH (supported) |
| Acoustic | T58 | Low STI, natural sound masking | MEDIUM (supported) |
| Thermal | T20 | Individual control over temperature | MEDIUM (established) |
```

```python
def synthesize_design_answer(
    context: str,
    building_type: str,
    user_population: Optional[str] = None
) -> DesignSynthesis:
    """Combine multiple templates for design question."""

    relevant_domains = identify_domains_for_context(context, building_type)
    templates = [get_templates_for_domain(d) for d in relevant_domains]

    recommendations = []
    for template in flatten(templates):
        rec = extract_design_recommendation(template, context)
        rec.priority = compute_priority(template.maturity, template.effect_magnitude)
        if user_population:
            rec = apply_population_adjustment(rec, user_population)
        recommendations.append(rec)

    conflicts = detect_conflicts(recommendations)

    return DesignSynthesis(
        recommendations=sorted(recommendations, key=lambda r: r.priority, reverse=True),
        conflicts=conflicts,
        templates_used=[t.display_id for t in flatten(templates)]
    )
```

---

## Amendment 13: Hierarchy Extraction

### Problem Discovered

Templates contain explicit hierarchies (VIEW1.synthetic_nature_hierarchy, COL2.arousal_dimensions, SOC2.five_mechanisms). Panel didn't specify how to extract and present these.

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
@dataclass
class ExtractedHierarchy:
    """Ordered ranking from template content."""

    source_template: str
    field_path: str  # e.g., "arousal_dimensions" or "synthetic_nature_hierarchy"
    items: List[str]  # Ordered from highest to lowest
    ordering_criterion: str  # e.g., "effect magnitude", "channel count", "naturalness"

def extract_hierarchies(template: Dict) -> List[ExtractedHierarchy]:
    """Find and extract ordered rankings from template."""

    hierarchy_fields = [
        "synthetic_nature_hierarchy",
        "view_quality_gradient",
        "arousal_dimensions",
        "five_privacy_mechanisms",
        "compositional_techniques"
    ]

    hierarchies = []
    for field in hierarchy_fields:
        if field in template:
            hierarchies.append(parse_hierarchy(template, field))

    return hierarchies
```

**Response integration**: When answering comparative questions, check for explicit hierarchies before computing comparisons.

---

## Amendment 14: Context → Parameter Mapping

### Problem Discovered

Questions like "What color for a gym?" require: context (gym) → activity type (high arousal) → parameter (bright, saturated). Panel didn't specify this mapping.

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
# Context → Activity → Optimal Parameter mapping

CONTEXT_ACTIVITY_MAP = {
    "gym": "high_arousal",
    "bedroom": "low_arousal",
    "office": "moderate_arousal",
    "meditation_room": "low_arousal",
    "retail": "high_arousal",
    "hospital_room": "low_arousal",
    "classroom": "moderate_arousal",
    "restaurant": "moderate_to_high_arousal"
}

def map_context_to_parameter(
    context: str,
    attribute: str  # e.g., "color", "light", "sound"
) -> ParameterRecommendation:
    """Map building context to optimal attribute parameters."""

    activity = CONTEXT_ACTIVITY_MAP.get(context, "moderate")
    template = get_template_for_attribute(attribute)

    if hasattr(template, "context_arousal_matching"):
        return template.context_arousal_matching[activity]
    elif hasattr(template, "goldilocks"):
        return template.goldilocks.optimal_for_activity(activity)
    else:
        return ParameterRecommendation(value="unknown", confidence="low")
```

---

## Amendment 15: Population Adjustment Detection

### Problem Discovered

L2 has explicit age-correction formulas. Other templates may need similar population-specific adjustments. Panel didn't address this.

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
@dataclass
class PopulationAdjustment:
    """Population-specific parameter modification."""

    base_parameter: str
    population: str  # e.g., "elderly", "children", "shift_workers"
    adjustment_formula: Optional[str]  # e.g., "M-EDI(age) ≈ M-EDI(25) × (1 + 0.015 × (age − 25))"
    adjustment_factor: Optional[float]  # e.g., 2.0 for elderly
    source_template: str

POPULATION_ADJUSTMENTS = {
    "L2": {
        "elderly": PopulationAdjustment(
            base_parameter="melanopic_EDI",
            population="elderly",
            adjustment_formula="M-EDI(age) ≈ M-EDI(25) × (1 + 0.015 × (age − 25))",
            adjustment_factor=2.0,  # for age 90
            source_template="L2"
        )
    },
    "SOC2": {
        "introverts": PopulationAdjustment(
            base_parameter="optimal_social_exposure",
            population="introverts",
            adjustment_factor=0.7,  # lower optimal level
            source_template="SOC2"
        )
    }
}

def apply_population_adjustment(
    parameter: Any,
    population: str,
    template_id: str
) -> Any:
    """Apply population-specific adjustment if available."""

    if template_id in POPULATION_ADJUSTMENTS:
        if population in POPULATION_ADJUSTMENTS[template_id]:
            adj = POPULATION_ADJUSTMENTS[template_id][population]
            return parameter * adj.adjustment_factor
    return parameter
```

---

## Amendment 16: Cross-Template Interaction Classification

### Problem Discovered

Questions like "Does noise cancel out plant benefits?" require knowing whether effects add, interfere, or compensate. Panel didn't address interaction types.

### Spec Change

Add to **Part IX: Implementation Specification**:

```python
class InteractionType(Enum):
    ADDITIVE = "additive"  # Independent pathways, effects sum
    INTERFERING = "interfering"  # Compete for same resource
    COMPENSATORY = "compensatory"  # One can substitute for other
    AMPLIFYING = "amplifying"  # Combined effect > sum of parts
    GATING = "gating"  # One enables/disables the other

@dataclass
class CrossTemplateInteraction:
    """Interaction between two templates."""

    template_a: str
    template_b: str
    interaction_type: InteractionType
    shared_pathway: Optional[str]  # If interfering, what do they share?
    evidence: str

def classify_interaction(
    template_a: str,
    template_b: str
) -> CrossTemplateInteraction:
    """Determine how two templates interact."""

    # Check for shared mediators
    mediators_a = get_mediators(template_a)
    mediators_b = get_mediators(template_b)
    shared = mediators_a & mediators_b

    if shared:
        # Same pathway → may interfere or amplify
        if effects_same_direction(template_a, template_b):
            return CrossTemplateInteraction(
                template_a, template_b,
                InteractionType.AMPLIFYING,
                shared_pathway=list(shared)[0],
                evidence="Shared mediator, same direction"
            )
        else:
            return CrossTemplateInteraction(
                template_a, template_b,
                InteractionType.INTERFERING,
                shared_pathway=list(shared)[0],
                evidence="Shared mediator, opposite direction"
            )
    else:
        # Independent pathways → additive
        return CrossTemplateInteraction(
            template_a, template_b,
            InteractionType.ADDITIVE,
            shared_pathway=None,
            evidence="No shared mediators"
        )
```

---

## Amendment 17: Confidence Chain Reporting

### Problem Discovered

Templates have bridging_quality at each causal link (strong/moderate/weak). Users need to know which links in a causal chain are well-established vs speculative.

### Spec Change

Add to **Part VI: Response Templates**:

```markdown
### Confidence Chain Visualization

For mechanism answers spanning multiple causal links, report confidence at each step:

**Example**: "How does a nature view reduce stress?"

```
nature_view → fractal_processing → reduced_cognitive_load → lower_cortisol
   [strong]        [moderate]           [strong]              [established]
```

**Weakest link rule**: Overall pathway confidence = min(link confidences)

**Response template**:
> "Nature views reduce stress through fractal processing (strong evidence)
> which reduces cognitive load (moderate evidence), lowering cortisol
> (strong evidence). The weakest link is fractal→cognitive_load
> (moderate), so overall pathway confidence is MODERATE."
```

```python
@dataclass
class ConfidenceChain:
    """Confidence through a causal pathway."""

    links: List[Tuple[str, str, str]]  # (from, to, bridging_quality)
    overall_confidence: str  # min of all links
    weakest_link: Tuple[str, str]

def compute_confidence_chain(pathway: List[CausalLink]) -> ConfidenceChain:
    """Compute confidence through a causal chain."""

    links = [(l.from_entity, l.to_entity, l.bridging_quality) for l in pathway]
    qualities = [l.bridging_quality for l in pathway]

    quality_order = {"strong": 3, "moderate": 2, "weak": 1}
    min_quality = min(qualities, key=lambda q: quality_order.get(q, 0))
    weakest_idx = qualities.index(min_quality)

    return ConfidenceChain(
        links=links,
        overall_confidence=min_quality,
        weakest_link=(pathway[weakest_idx].from_entity, pathway[weakest_idx].to_entity)
    )
```

---

## Summary: Spec Improvements from Testing

| # | Amendment | Problem Discovered | Solution |
|---|-----------|-------------------|----------|
| 1 | Confidence vs Effect Size | Conflated in spec | Explicit vocabulary distinction |
| 2 | Comparative Subtypes | Single type too coarse | Three subtypes: existence, magnitude, mechanism |
| 3 | Pathway Comparison | Multi-pathway reasoning missing | PathwayAnalysis dataclass + robustness scoring |
| 4 | Missing Data Protocol | No guidance for gaps | Explicit acknowledge → reason → flag protocol |
| 5 | Goldilocks Parameters | Rich data ignored | DOSAGE_OPTIMIZATION question type |
| 6 | Shared Theory Detection | Substitutability not addressed | SharedTheoryAnalysis + additivity warnings |
| 7 | Quantitative Comparison | "As much as" unanswerable | QuantitativeComparison with fallback logic |
| 8 | Question Classification | Compound questions ambiguous | Priority ordering + primary/secondary structure |
| 9 | Research Gap Surfacing | Gaps not leveraged | Automatic gap detection for researchers |
| 10 | Proactive Taxonomic Expansion | Narrow answers required follow-ups | Lead with domain taxonomy when siblings diverge |
| 11 | Dual-Layer Query Architecture | Queried BN for theory questions | Templates for theory, mechanisms for parameters |
| 12 | Multi-Template Synthesis | Design questions need multiple templates | Synthesis protocol with priority ordering |
| 13 | Hierarchy Extraction | Templates have explicit orderings | Extract and present ranked lists |
| 14 | Context → Parameter Mapping | "Color for gym?" needs activity mapping | Context → activity → parameter chain |
| 15 | Population Adjustment | Age/trait corrections exist | Detect and apply population-specific formulas |
| 16 | Cross-Template Interaction | "Does X cancel Y?" unanswerable | Interaction type classification |
| 17 | Confidence Chain Reporting | Multi-link confidence unclear | Weakest-link reporting |

---

## Revised Data Requirements

Based on testing, the QA agent needs these fields to be reliably populated:

| Field | Current Status | Priority |
|-------|---------------|----------|
| `mechanism.confidence` | ✅ Available | — |
| `claim.effect_size` | ⚠️ Sparse | HIGH |
| `mechanism.theory_alignment` | ✅ Available | — |
| `goldilocks.*` | ✅ Available | — |
| `pathway.mediators` | ✅ Available | — |
| Direct comparison claims | ❌ Missing | MEDIUM |
| Effect size units/types | ⚠️ Inconsistent | HIGH |

**Recommendation**: Prioritize effect size extraction at claim level to enable magnitude comparisons.

---

*End of Amendments*
