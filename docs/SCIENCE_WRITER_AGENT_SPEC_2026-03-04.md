# Science Writer Agent Specification for ATLAS
## Comprehensive Design for Premium Content Generation

**Date**: 4 March 2026
**Author**: Claude (Opus 4.6)
**Context**: ATLAS card system + 10 existing services + probe integration requirements
**Status**: SPECIFICATION — Awaiting David Kirsh's review and AG architectural coordination
**Deliverable Scope**: Complete agent architecture, writing pipeline, question-generation loop, quality gates, integration points, card-type strategies, and context-appendix design.

---

## Executive Summary

The Science Writer Agent is the critical missing component in ATLAS. The system has 10 agent-like services that handle domain expertise, evidence synthesis, and methodological quality, but no unified agent that:

1. **Generates premium prose** at the level required for committed card content (Overview, Mechanism, Design, Debate tabs)
2. **Generates questions during writing** that expose gaps, ambiguities, and unstated assumptions, storing them in card-level icebergs
3. **Allocates Opus intelligently** for theoretical content where quality matters (T1 frameworks, mechanism explanations, philosophical justification) while using Sonnet for routine work (evidence summaries, data aggregation, design parameter tables)
4. **Maintains state** across card generation sessions to accumulate context about domain coverage, frequently-asked questions, and emerging patterns
5. **Produces justified visualizations** for ReductionClaim DAGs, mechanism chains, and argument maps rather than generic lists
6. **Handles the iceberg** — the depth layer that makes real-time deepening and regeneration possible

This specification describes how to build that agent as a **stateful, multi-model orchestrator** that produces card content of publication quality while generating the questions that drive system improvement.

---

## 1. Agent Architecture Overview

### 1.1 Role Definition

The Science Writer Agent is responsible for:

| Responsibility | Triggered By | Primary Model | Output |
|---|---|---|---|
| **T1 Framework card generation** | New T1 added to registry or staleness trigger | Opus | 3-4 KB prose (Overview, Mechanism, Design, Debate tabs) + 3 visuals |
| **T1.5 Domain Theory card generation** | New T1.5 reduction or staleness trigger | Opus | 3 KB prose + ReductionClaim DAG visual |
| **T2 Mechanism card generation** | New template calibrated or staleness trigger | Opus (prose) + Sonnet (design params) | 2-3 KB prose + parameter table + forest plot |
| **Math Card generation** (3 tabs: Intuition, Transparent, Details) | New formula/algorithm or revision request | Opus (Intuition + Details) + Sonnet (Transparent) | 2-3 KB prose per tab + annotated equation visual |
| **Molecule card generation** | New molecule discovered or component change | Sonnet | 1.5 KB prose + component interaction diagram |
| **T3 Belief card generation** (on-demand) | New article integrated or deep-dive request | Sonnet | 500 words prose + effect size visual |
| **Competition card generation** | Dispute detected or regeneration trigger | Opus (Debate tab) + Sonnet (Evidence tab) | 2 KB prose + argument map |
| **Layer & Method card generation** | Code commits to subsystem or request | Opus (Justification) + Sonnet (Implementation) | 2-3 KB prose + architecture/flowchart visual |
| **Question generation during writing** | Continuous; every prose generation | Sonnet | Structured questions stored in card.iceberg.context_questions |
| **Prose revision quality gate** | Before card commit | Sonnet | Prose health score; passes if ≥ 6.5 |

### 1.2 System Position in ATLAS

```
┌─────────────────────────────────────────────────┐
│ Application Layer (API, Streamlit, QA system)   │ ← consumes cards
└──────────────────────────┬──────────────────────┘
┌──────────────────────────┴──────────────────────┐
│        Science Writer Agent (THIS SPEC)         │ ← GENERATES cards
├──────────────────────────┬──────────────────────┤
│ 10 Existing Services     │ Opus/Sonnet Models   │
├──────────────────────────┼──────────────────────┤
│ • Grounded Expert Agent  │ • Opus for quality   │
│ • Prose Revision Service │ • Sonnet for speed   │
│ • Web of Belief          │ • Haiku for triage   │
│ • Bayesian Network       │                      │
│ • Bridge Warrants        │                      │
│ • Annotation Layer       │                      │
│ • Argumentation System   │                      │
│ • Theory Agent Council   │                      │
│ • Answer Enrichment      │                      │
│ • Panel Resolver         │                      │
└──────────────────────────┴──────────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│ Data Layer (cards JSON, web/BN, annotations)    │
└─────────────────────────────────────────────────┘
```

The Science Writer Agent is the **bridge service** that translates structured knowledge (web of belief, T2 templates, argument maps) into human-readable prose at publication quality, while simultaneously surfacing the implicit questions that the writing process reveals.

---

## 2. Agent State and Context Management

### 2.1 Why the Agent Must Be Stateful

The Science Writer Agent accumulates context across writing sessions because:

1. **Writing reveals patterns** — After generating 50 T2 mechanism cards, the agent learns which mechanism types require extra explanation, which are frequently confused with others, which design parameters recur across templates.

2. **Questions cluster** — Writing about coherence reveals frequently-asked questions about "What makes the web of belief stable?" These questions should be consolidated into a FAQ and incorporated into future card generation prompts.

3. **Prose improves** — The agent should track which sections of past cards received the most positive feedback, and incorporate those patterns into future writing.

4. **Domain coverage gaps emerge** — By tracking what hasn't been written (which T2 templates lack cards? which T1.5 theories have incomplete design implications?), the agent can guide prioritization.

### 2.2 Stateful Agent Registry (Per Session)

The agent maintains a session-scoped state document:

```yaml
# /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/.agent_coord/science_writer_state.yaml

session_id: CLAUDE-SCIENCE-WRITER-{timestamp}
status: ACTIVE
assigned_tasks:
  - card_id: T1_PREDICTIVE_PROCESSING
    card_type: T1_Framework
    status: IN_PROGRESS
    started_at: 2026-03-04T14:32:00Z
    context:
      - source_loci: [T1 registry entry, 47 backing T2 templates, bridge warrant catalog]
      - key_questions_identified: 3
      - prose_generation_tokens_used: 8432

  - card_id: T2_LIGHT_01
    card_type: T2_Mechanism
    status: AWAITING_REVISION
    started_at: 2026-03-04T13:15:00Z
    context:
      - source_loci: [43 T3 beliefs, 5 competing mechanism accounts, 2 interaction effects]
      - design_parameters_drafted: true
      - mechanism_chain_visual_needed: true
      - questions_generated: 7

pattern_tracking:
  mechanism_types_requiring_extra_scaffolding:
    - TEMPORAL_DYNAMICS: [LIGHT_01, TEMP_01, ACOUSTIC_02]
    - MODULATION_EFFECTS: [LIGHT_03, SPATIAL_02]
    - CROSS_DOMAIN_GENERALIZATION: [BIOPHILIA_01, ART_BRIDGE]

  frequently_unanswered_questions:
    - "Why is [mechanism] robust to individual differences?"
    - "How do you measure [construct] in real buildings vs. labs?"
    - "What's the irreducible residual for [T1.5 theory]?"

  prose_patterns_working_well:
    - Opening with a concrete example before theoretical abstraction
    - Three-part mechanism description (stimulus, neural process, outcome)
    - Explicit scope conditions in Design tab

  coverage_gaps_identified:
    - T2 templates without prose: [ATTENTION_RESTORATION_04, WAYFINDING_02, THERMAL_03]
    - T1.5 theories with incomplete design implications: [Soft Fascination, Prospect-Refuge]
    - Math cards not yet drafted: [log-odds projection, noisy-OR combination]

model_performance_tracking:
  opus_prose_quality:
    avg_health_score: 7.2
    cards_passed_gate: 18
    cards_failed_gate: 2
    common_failures: ["passive voice clusters", "undefined jargon creep"]

  sonnet_prose_quality:
    avg_health_score: 6.8
    cards_passed_gate: 42
    cards_failed_gate: 3

context_window_consumption:
  cards_generated: 23
  avg_tokens_per_card: 6800
  total_session_tokens: 156,400
  remaining_budget: 43,600
```

This state document:
- Allows the agent to resume interrupted work and recall context
- Enables AG's orchestrator to track agent progress
- Provides input for future card quality analysis
- Surfaces patterns that should be incorporated into system improvements

### 2.3 Long-Term Memory: The Master Question Registry

Beyond session state, the agent maintains a persistent file that consolidates questions generated across all writing sessions:

```yaml
# /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/master_question_registry.yaml

# Canonical reference for questions that emerged during prose generation
# Updated after each science writer agent session
# Used to: (a) detect frequently-asked patterns, (b) guide future card content, (c) identify research gaps

last_updated: 2026-03-04T15:45:00Z
total_questions: 847
questions_by_category:

  MECHANISM_CLARITY:
    - id: Q_MECH_0341
      question: "Why is the relationship between window area and daylight sufficiency non-monotonic above 15% of floorplate area?"
      first_raised: 2026-02-28 (card: LIGHT_02)
      recurrence_count: 3
      raised_by_cards: [LIGHT_02, LIGHT_04, SPATIAL_COHERENCE_02]
      resolution_status: UNRESOLVED
      confidence_in_resolution: 0.0
      relevant_sources: [DOI: 10.1038/nrneurosci.2014.5, Expert opinion: Lechtzin]
      suggested_research: "Empirical study with parametric window sizes in identical rooms"

    - id: Q_MECH_0512
      question: "How does spatial scale (room vs. floorplate vs. campus) affect the strength of biophilic effects?"
      first_raised: 2026-03-02 (card: BIOPHILIA_SCOPE)
      recurrence_count: 1
      raised_by_cards: [BIOPHILIA_SCOPE]
      resolution_status: PARTIALLY_ADDRESSED
      confidence_in_resolution: 0.35
      relevant_sources: [Kaplan & Kaplan 1989, Berman et al. 2008]
      suggested_research: "Meta-analysis of biophilic studies, cross-tabulated by spatial scale"

  BOUNDARY_CONDITIONS:
    - id: Q_BOUND_0284
      question: "At what point does visual complexity become 'too high' and exceed the Goldilocks optimum?"
      first_raised: 2026-03-01 (card: VISUAL_COMPLEXITY_TUNING)
      recurrence_count: 5
      raised_by_cards: [VISUAL_COMPLEXITY_TUNING, T2_FRACTAL, MOLECULE_SOFT_FASCINATION, COMPETING_ACCOUNTS_01]
      resolution_status: PARTIALLY_ADDRESSED
      confidence_in_resolution: 0.45
      relevant_sources: [Berlyne 1974, Coss 1990, Stamp 2005]
      suggested_research: "Cross-domain re-analysis: what complexity range optimizes alertness, mood, stress, creativity?"

  INDIVIDUAL_DIFFERENCES:
    - id: Q_INDIV_0156
      question: "How much variation in [mechanism effect] is explained by personality, cultural background, and prior exposure?"
      first_raised: 2026-02-15 (card: T2_ATTENTION_RESTORATION_01)
      recurrence_count: 18
      raised_by_cards: [ART_BRIDGE, BIOPHILIA_01-18, PROSPECT_REFUGE, FRACTAL, ACOUSTIC_01-03, THERMAL_01-02]
      resolution_status: SEVERELY_UNDEREXPLORED
      confidence_in_resolution: 0.1
      relevant_sources: [Personality literature scattered across papers; no CNFA meta-analysis]
      suggested_research: "Systematic moderator analysis across all CNFA corpus; literature review of personality × environment interactions"

  DESIGN_IMPLEMENTATION:
    - id: Q_DESIGN_0098
      question: "How do you operationalize [T1.5 theory] in actual building design workflows?"
      first_raised: 2026-02-20 (card: T1.5_SOFT_FASCINATION_DESIGN)
      recurrence_count: 7
      raised_by_cards: [T1.5_SOFT_FASCINATION_DESIGN, T1.5_PROSPECT_REFUGE_DESIGN, MOLECULE_CARDS_01-06]
      resolution_status: UNRESOLVED
      confidence_in_resolution: 0.0
      relevant_sources: [No published design operationalization protocols found]
      suggested_research: "Interviews with practicing architects; case studies of buildings designed with CNFA principles"

  MEASUREMENT_VALIDITY:
    - id: Q_MEAS_0203
      question: "What's the minimum exposure duration to [mechanism] before measurable outcomes emerge?"
      first_raised: 2026-02-25 (card: T2_ATTENTION_RESTORATION_MINIMAL_DOSE)
      recurrence_count: 9
      raised_by_cards: [ATTENTION_RESTORATION_01-04, BIOPHILIA_EXPOSURE_DURATION, THERMAL_ADAPTATION, ACOUSTIC_MASKING]
      resolution_status: PARTIALLY_ADDRESSED
      confidence_in_resolution: 0.40
      relevant_sources: [Kellert & Heerwagen, Fich et al. 2014, Ulrich et al. 1991]
      suggested_research: "Dose-response meta-analysis with temporal resolution (5-min intervals); publication bias check"

structure_and_governance:
  questions_suitable_for_qa_system: 120  # These should be captured and answered
  questions_requiring_empirical_research: 387  # These point to research gaps
  questions_revealing_prose_gaps: 340  # These indicate where card content is unclear
  questions_with_expert_panel_consensus: 85  # These can be resolved via deliberation
```

This registry serves four purposes:

1. **QA System Input** — "Why is window area non-monotonic?" and similar questions should have dedicated answer cards
2. **Research Gap Identification** — The fact that individual-differences questions appear 18 times signals a fundamental gap in CNFA knowledge
3. **Prose Improvement** — A question like "Why is the relationship non-monotonic?" appearing 3 times suggests the mechanism explanation needs better scaffolding
4. **System Evaluation** — David can review questions and see what the writing process reveals about the system's state

---

## 3. The Writing Pipeline: From Card Request to Committed Prose

### 3.1 Pipeline Stages

```
REQUEST
  ↓
[1] INTAKE & CONTEXT ASSEMBLY
  ↓
[2] OPUS GENERATION (theoretical content) OR SONNET GENERATION (routine content)
  ↓
[3] QUESTION EXTRACTION (while prose is drafted)
  ↓
[4] REVISION & QUALITY GATE (Prose Revision Service)
  ↓
[5] VISUAL GENERATION (Sonnet + mermaid/matplotlib)
  ↓
[6] ICEBERG ASSEMBLY (provenance, references, raw data)
  ↓
[7] COMMIT & STORAGE
  ↓
DELIVERED CARD
```

### 3.2 Stage 1: Intake & Context Assembly

**Input**: Card request (type, ID, scope)

**Output**: `CardGenerationContext` dataclass containing:

```python
@dataclass
class CardGenerationContext:
    """Complete context for prose generation."""

    card_id: str                          # e.g., "T1_PREDICTIVE_PROCESSING"
    card_type: CardType                   # T1_FRAMEWORK, T2_MECHANISM, etc.

    # Primary data sources
    primary_loci: List[BeliefNode]        # The key nodes this card explains
    backing_beliefs: List[BeliefNode]     # All T3 beliefs supporting this card
    competing_accounts: List[Competition] # If any exist

    # Contextual enrichment
    related_cards: List[str]              # Parent, child, sibling cards
    annotation_context: AnnotationLayer   # 25 annotation types (if applicable)
    existing_prose: Optional[str]         # Previous version (for regeneration)

    # Target quality specifications
    prose_target_health_score: float = 6.5  # Minimum acceptable
    prose_style_guide: str = "SCIENCE_COMMUNICATION_NORMS.md"
    target_word_count: int  # varies by card type, tab

    # Model allocation parameters
    use_opus: bool = False  # True for T1, T1.5, Math Details, Competition Debate
    use_sonnet: bool = True # Default; upgraded to Opus if needed

    # Question tracking
    questions_to_extract: bool = True
    question_extraction_depth: str = "COMPREHENSIVE"  # or BASIC, NONE
```

**Process** (Sonnet):
1. Query web of belief for `primary_loci` (beliefs most relevant to this card)
2. Aggregate backing evidence (all T3 beliefs, effect sizes, warrant types)
3. Fetch related cards (parents, children, competing accounts)
4. Retrieve annotations (if applicable)
5. Assemble existing prose if regenerating
6. Compile external references (APA bibliography)

**Cost**: ~500 tokens (mostly API calls to web of belief service, not LLM)

### 3.3 Stage 2a: Opus Generation (Theoretical Content)

**Triggered when**: Card type ∈ {T1, T1.5, Math Card (Intuition+Details), Competition (Debate tab), Layer, Method (Justification)}

**Prompt structure** (for T1 Framework card example):

```markdown
# Generate T1 Framework Card: Predictive Processing

You are writing a science communication card that explains a neurobiological theory to a multi-audience readership (researchers, clinicians, designers, policymakers, students).

## Card Identity
- Card Type: T1 Framework
- Framework: Predictive Processing (PP)
- Target: 750-950 words for Overview tab; 600-800 for Mechanism; 700-900 for Design

## Authorial Stance
- Write as a guide showing the reader something interesting, not as an authority.
- Use classic style (Pinker): you have noticed something; you are pointing it out.
- Voice: smart 3rd-year undergrad, biased 60/40 toward popular science.

## Content Requirements

### Overview Tab (750-950 words)
- Paragraph 1 (100 words): What is PP? Lead with the core prediction: the brain is fundamentally a prediction machine.
- Paragraph 2 (150 words): Why does PP matter for CNFA? How do built environments trigger prediction errors?
- Paragraph 3 (200 words): The mechanism chain (simplified): sensory input → prediction → error signal → neural updating. Use concrete example (walking into familiar room, one light is off).
- Paragraph 4 (200 words): Predictions across scales: low-level sensory (light intensity), mid-level (spatial layout), high-level (semantic meaning of space). How architects can work with this hierarchy.
- Paragraph 5 (150 words): Open questions. What happens in highly unpredictable environments? Are prediction errors always aversive, or can they be engaging?

**Scope conditions**: Focus on visual-spatial domain (architecture domain). Acknowledge that PP applies across all sensory modalities, but anchor examples in sight, sound, proprioception, thermal sensation.

### Mechanism Tab (600-800 words)
- Explain the neural implementation: hierarchical error-minimization across cortical layers, precision-weighting of prediction errors via neuromodulatory systems, Bayesian inference formalism.
- Include a step-by-step mechanism chain: [built environment stimulus] → [sensory periphery] → [early cortical prediction] → [prediction error signal] → [neuromodulatory gating] → [belief updating] → [outcome (alertness, stress, mood)].
- Mandatory visual: Circuit diagram showing hierarchical predictive processing with error signals flowing backward through cortical layers.

### Design Tab (700-900 words)
- What are the design implications of PP?
- Principle 1: Minimize unpredictable elements early in the journey. Predictability is calming.
- Principle 2: Scaffold complexity so predictions can be updated incrementally. Sudden changes are stressful.
- Principle 3: Provide affordances for exploration — environments that are too predictable are boring.
- Principle 4: Use wayfinding cues that make the spatial logic legible. Spatial confusion triggers prediction errors.

**Stress position**: End with "Architects can work with the brain's prediction machinery by creating environments that are legible (errors are minimized), updatable (complexity increases gradually), and exploratory (there is always something new to notice)."

## Evidence Base
- Primary sources: 47 T2 templates grounding in PP; 312 backing T3 beliefs
- Key citations to weave in: Friston (predictive processing framework), Barrett (emotions as predicted interoceptive states), Feldman (cortical prediction), Rao & Ballard (hierarchical Bayes)
- Warrant types: [Mostly MECHANISM and THEORETICAL_DEFAULT; few EMPIRICAL_COVARIANCE]

## Quality Gate
- Apply SCIENCE_COMMUNICATION_NORMS.md § 1-12
- Prose health score must be ≥ 6.8 (you are Opus; target higher than the 6.5 baseline)
- Given-New contract: every sentence begins with familiar information
- Stress position: ends with most important content
- No zombie nouns (nominalizations) unless they are standard technical terms
- Confidence calibration: match phrasing to evidence strength (Norm 9)

## During Writing: Question Extraction
As you write, identify assumptions, gaps, and implicit claims that are NOT obvious:
- Assumption: "PP assumes that the brain has accurate priors." Question: "Where do priors come from? How much of prediction error reflects learned models vs. phylogenetic wiring?"
- Gap: The card doesn't address individual differences in PP strength. Question: "Why do some people thrive in unpredictable environments while others find them stressful?"
- Implicit claim: "Unexpected changes are always costly." Question: "Are there conditions where prediction errors are engaging rather than aversive?"

Extract 3-5 substantive questions (not trivial clarifications). Store in structured format (see §4 below).

## Output Format
Return a JSON object with fields:
- overview_prose: str (750-950 words)
- mechanism_prose: str (600-800 words)
- design_prose: str (700-900 words)
- questions_generated: List[Question]  # See §4.2 format
- prose_health_score: float (self-assessed; will be verified by Prose Revision Service)
- model_used: "Opus 4.6"
- generation_timestamp: ISO 8601
```

**Model Used**: Opus 4.6

**Typical Output Length**: 2,500 tokens

**Quality Check**: Prose will be passed through Prose Revision Service (Stage 4) before commitment.

### 3.3 Stage 2b: Sonnet Generation (Routine Content)

**Triggered when**: Card type ∈ {T2 (Evidence/Design), T3 (on-demand), Molecule, Math (Transparent), Method (Implementation)} OR Opus prose needs supplementary data.

**Prompt structure** (for T2 Mechanism Design Tab example):

```markdown
# Generate T2 Mechanism Card — Design Parameters

Card: LIGHT_01 (Morning Daylight Entrainment)
Mechanism: Morning light (≥2,500 lux, 400-500nm spectrum) → melanopsin-ipRGC activation → SCN entrainment → circadian phase advance

Write the Design tab (700-900 words) for architects and lighting designers.

## Structure
1. Opening: Why daylight is designable. Controllable parameters: lux level, spectrum, timing, duration.
2. Design Parameter Table (visual): Show parameter ranges with supporting data:
   - Lux requirement: ≥2,500 (justified by Gooley et al. 2011, Charman 2003)
   - Spectrum: Peak response 460-480nm (melanopsin action spectrum)
   - Timing: Within 2 hours of wake time (Czeisler phase-response curve)
   - Duration: Minimum 30 minutes for phase shift; plateau effects at 90+ min
   - Population modifiers: Age (elderly need higher lux), chronotype (larks vs. owls have different thresholds)
3. Practical guidance: How to achieve 2,500 lux in real buildings?
   - North-facing windows: rarely achieve >1,200 lux (limit this strategy)
   - East-facing windows: 2,500+ lux common 6-10 AM (optimal)
   - South-facing with shading: can exceed 5,000 lux (risk of glare; use diffusing materials)
   - Supplemental lighting: 10,000 lux light therapy boxes (effective but not equivalent to diffuse daylight)
4. Boundary conditions: When does this mechanism fail?
   - Circadian disorders (delayed sleep phase): may need afternoon suppression instead
   - Seasonal affective disorder: mechanism intact, but sensitivity may be higher
   - Night-shift workers: completely inverted timeline
5. Design rules of thumb:
   - Rule 1: "Orient east-facing glass (30°-60° of fenestration) to catch morning light."
   - Rule 2: "If natural east light is unavailable, supplement with 10,000 lux white light 6-8 AM."
   - Rule 3: "Avoid afternoon/evening bright light; this phase-delays circadian rhythm."

## Design Parameter Table (Visual)
Include a table with:
- Parameter | Optimum Value | Evidence Base | Implementation Notes
- Lux level | 2,500+ | Charman, Gooley | "Achievable via 50%+ east-facing glass. Check for glare."
- Spectrum | 460-480nm | Melanopsin physiology | "Natural daylight peaks here. Incandescent/LEDs must be tuned."
- Timing | 6-8 AM | Phase-response curve | "Earlier = larger phase advance. Diminishing returns after 90 min."
- Duration | 30-90 min | Czeisler et al. 1989 | "Minimum for measurable shift; plateaus ~90 min."

## Confidence/Caveats
- This mechanism is ESTABLISHED (meta-analyses support; causal chain is neurobiologically sound).
- Population scope: primarily tested in healthy young adults; efficacy may differ in elderly, ADHD, bipolar disorder.
- Real-building implementation: achieving 2,500 lux in northern climates during winter is challenging; supplement with light therapy may be necessary.

Output: 700-900 words prose + parameter table visual (markdown or HTML table).
Quality gate: prose health score ≥ 6.5. Apply Paramedic Method (Norm 5: identify zombie nouns, bury the lard).
```

**Model Used**: Sonnet 3.5

**Typical Output Length**: 1,200 tokens

**Advantages of Sonnet for routine content**:
- 3-5x faster than Opus
- Sufficient for statistical summaries, parameter tables, evidence aggregation
- Allows Opus budget to be reserved for theoretical content where judgment matters

### 3.4 Stage 3: Question Extraction (Simultaneous with 2a/2b)

**What gets extracted**: During prose generation, the agent (both Opus and Sonnet) identifies assumptions, implicit claims, scope conditions, and boundary conditions that are NOT explicit in the prose.

**Question Quality Filter**: Only questions that are:
1. **Substantive** — Not trivial clarifications ("What does 'lux' mean?") but genuine gaps ("Why does the melanopsin system have a 15-minute latency?")
2. **Resolvable** — Either by evidence search, expert panel consultation, or empirical research (not philosophical with no empirical hook)
3. **Relevant to understanding** — Questions that if answered would improve the card or surrounding cards

**Extraction format** (JSON):

```json
{
  "questions_generated": [
    {
      "id": "Q_PP_0847",
      "question": "Why do some individuals exhibit stronger prediction-error responses in chaotic environments while others appear indifferent?",
      "category": "INDIVIDUAL_DIFFERENCES",
      "implicit_claim": "The card assumes all humans share similar prediction-error sensitivity; individual differences are treated as noise.",
      "resolution_status": "UNRESOLVED",
      "resolution_pathway": "Literature review (personality × environment interactions); possible future empirical study",
      "relevance_to_card": "HIGH — affects generalizability of design principles across diverse populations",
      "suggested_card_improvement": "Add a scope condition: 'These design principles apply to neurotypical adults; ADHD, autism, anxiety, and other conditions may have different prediction-error processing.'",
      "raises_system_question": true,
      "system_question": "ATLAS currently lacks a systematic review of individual differences moderating all CNFA mechanisms. This is a major gap."
    },
    {
      "id": "Q_PP_0848",
      "question": "How do long-term habituation and learning reshape prediction-error signals in familiar environments?",
      "category": "TEMPORAL_DYNAMICS",
      "implicit_claim": "The card presents PP as if prediction errors are static; in reality, repeated exposure changes what is predicted.",
      "resolution_status": "PARTIALLY_ADDRESSED",
      "resolution_pathway": "Existing research on habituation and neural adaptation (Sokolov's OR theory; Groves & Thompson dual-process)",
      "relevance_to_card": "MEDIUM — affects whether design implications apply to inhabitants who have years of exposure vs. first-time visitors",
      "suggested_card_improvement": "Add a Debate tab subsection: 'Habituation and Learning: As inhabitants learn building layouts and routines, prediction errors decrease. This means buildings feel most stimulating to newcomers and most comfortable to long-term occupants—a potential tension in design goals.'",
      "raises_system_question": true,
      "system_question": "Do we need separate design strategies for first-time visitors vs. regular inhabitants?"
    }
  ],
  "extraction_metadata": {
    "card_id": "T1_PREDICTIVE_PROCESSING",
    "total_questions_extracted": 4,
    "extraction_depth": "COMPREHENSIVE",
    "timestamp": "2026-03-04T14:55:00Z"
  }
}
```

**Storage**: Extracted questions are immediately added to:
1. `card.iceberg.context_questions` (card-level storage)
2. `/data/master_question_registry.yaml` (system-wide registry)

---

## 4. The Question-Generation Loop: Surfacing Implicit Knowledge

### 4.1 How Questions Are Generated

Questions emerge during prose generation when the agent recognizes:

| Pattern | Example | Question Generated |
|---|---|---|
| **Scope limitation** | Prose says "visual complexity optimizes alertness" without qualifying "in Western, educated, industrialized, rich, democratic (WEIRD) populations" | "Does the Goldilocks complexity curve hold cross-culturally?" |
| **Mechanism gap** | Prose explains "daylight regulates cortisol" but doesn't explain the 15-20 minute latency | "Why is there a latency? What are the physiological bottlenecks?" |
| **Individual difference** | Prose treats all humans as identical responders | "Why do some people thrive in unpredictable environments?" |
| **Temporal dynamics** | Prose describes immediate effects without discussing habituation | "How do long-term exposure and learning reshape prediction errors?" |
| **Implementation ambiguity** | Design tab says "provide legible spatial logic" without specifying how to measure legibility | "What makes wayfinding cues 'legible'? How do you test it?" |
| **Competing mechanism** | Two T2 templates both explain the same outcome via different pathways; prose doesn't address conflict | "When does pathway A dominate vs. pathway B?" |
| **Boundary condition** | Prose doesn't state when the mechanism fails | "Are there populations, contexts, or pathologies where this mechanism is absent?" |

### 4.2 Question Structure and Storage

Questions are stored as structured records (not free text) to enable:
- Clustering (which questions recur across cards?)
- Resolution tracking (which questions have been answered?)
- System-level analysis (what patterns of questions reveal about gaps in ATLAS?)

```python
@dataclass
class ContextQuestion:
    """A question that emerged during prose generation."""

    id: str                              # Unique identifier (Q_DOMAIN_NNNN)
    question: str                        # The question itself (full sentence)
    category: QuestionCategory           # SCOPE_CONDITION, MECHANISM_GAP, etc.

    # What triggered the question
    implicit_claim: str                  # The assumption the prose made without stating
    raised_during_prose_generation: str  # Which tab (Overview, Mechanism, etc.)

    # Can it be resolved?
    resolution_status: ResolutionStatus  # UNRESOLVED, PARTIALLY_ADDRESSED, RESOLVABLE_WITH_RESEARCH
    resolution_pathway: str              # How could this be resolved? (cite evidence, expert panel, empirical study)
    estimated_resolution_effort: str     # TRIVIAL, MANAGEABLE, MAJOR_PROJECT

    # Why does it matter?
    relevance_to_card: str               # LOW, MEDIUM, HIGH
    relevance_to_system: str             # Does this question, if answered, improve understanding of CNFA broadly?

    # How to improve the card
    suggested_card_improvement: str      # Concrete prose change to address this

    # Metadata
    raises_system_question: bool         # True if this reveals a gap in ATLAS architecture/knowledge
    system_question: Optional[str]       # The system-level question this points to
    card_id: str                         # Which card raised this question
    generation_timestamp: datetime
    answer_if_known: Optional[str]       # If resolved, the answer
```

**Example with full context**:

```yaml
context_questions:
  - id: Q_MECH_0512
    question: "How does spatial scale (room vs. floorplate vs. campus) affect the strength of biophilic effects?"
    category: SCOPE_LIMITATION
    implicit_claim: "The mechanisms described apply equally at all spatial scales"
    raised_during_prose_generation: "Design tab for T1.5 BIOPHILIA"

    resolution_status: PARTIALLY_ADDRESSED
    resolution_pathway: "Literature review shows biophilic effects are studied primarily at room-to-office scale. Campus-scale effects are theoretically derived but empirically sparse."
    estimated_resolution_effort: MAJOR_PROJECT

    relevance_to_card: MEDIUM
    relevance_to_system: HIGH

    suggested_card_improvement: "Add to Design tab: 'Spatial Scale Limitation: Current research tests biophilic effects primarily at room scale (< 10,000 sq ft). Application to campus-scale environments (> 100,000 sq ft) is theoretically sound but empirically underexplored. Architects should expect stronger effects in smaller enclosed spaces where nature elements are more salient.'"

    raises_system_question: true
    system_question: "ATLAS lacks a systematic framework for how effects scale across spatial domains. This is a critical gap for architectural application."

    card_id: T1.5_BIOPHILIA
    generation_timestamp: 2026-03-04T14:15:00Z
    answer_if_known: null  # Not yet answered; depends on meta-analysis
```

### 4.3 Where Questions Live: The Context Appendix

Every card has a dedicated section in its iceberg (depth layer) called the **Context Appendix**:

```python
@dataclass
class CardIceberg:
    """The depth layer below card surface and body."""

    # ... existing fields: source_map, references, raw_data, etc.

    context_appendix: ContextAppendix = field(default_factory=ContextAppendix)

@dataclass
class ContextAppendix:
    """Questions, assumptions, and uncertainties revealed during card generation."""

    questions: List[ContextQuestion]  # Questions that emerged while writing this card

    # Cross-references to related questions in other cards
    related_questions_in_other_cards: List[str]  # ["Q_MECH_0512", "Q_INDIV_0156", ...]

    # Assumptions stated in the card (made explicit)
    stated_assumptions: List[str]
    # Examples:
    # - "This card assumes healthy adult humans; pathological states may differ."
    # - "This mechanism is tested primarily in Western populations; cross-cultural validation is limited."

    # Implicit claims that could be questioned
    implicit_claims: List[str]
    # Examples:
    # - "Prediction errors are always aversive" (but see novelty-seeking literature)
    # - "Design parameters scale linearly with environment size" (untested at campus scale)

    # What's not covered here (scope boundaries)
    out_of_scope: List[str]
    # Examples:
    # - "Individual differences in openness to experience"
    # - "Temporal dynamics over weeks/months/years"
    # - "Non-Western cultural contexts"

    # Suggested improvements for future regeneration
    improvement_suggestions: List[str]
    # Examples:
    # - "Add a Debate tab covering the habituation question"
    # - "Integrate cross-cultural evidence from Biophilia card generation"

    # Metadata
    context_appendix_created_at: datetime
    last_updated_at: datetime
    generation_model: str  # "Opus 4.6", "Sonnet 3.5"
```

**Why this structure matters**:

1. **Transparency** — Users can see what assumptions underpin the card
2. **Improvement signals** — Questions point to where future regenerations should focus
3. **System health** — Clustering questions across cards reveals systematic gaps
4. **Deepening support** — When a user asks "Tell me more," the context appendix helps the system understand what "more" means

---

## 5. Quality Gates and Escalation Procedures

### 5.1 Three Quality Gates

Every generated card must pass three sequential gates before commitment.

#### Gate 1: Prose Health Gate (Prose Revision Service)

**Triggered**: After Stages 2a/2b (Opus/Sonnet generation)

**What it checks**:
- Health score ≥ 6.5 (Sonnet) or ≥ 6.8 (Opus)
- No egregious violations of SCIENCE_COMMUNICATION_NORMS.md (Norms 1-12)
- Given-New contract: sentences begin with familiar info
- Stress position: important content at sentence end
- Zombie noun count < 15% of content
- Hedge stack count < 3 per 500 words
- Passive voice < 20%
- Undefined jargon: all technical terms defined on first use

**Failure protocol**:
- If health score 6.0-6.4 (Sonnet) or 6.5-6.7 (Opus): Auto-revise and re-submit (usually succeeds)
- If health score < 6.0 (Sonnet) or < 6.5 (Opus): Escalate to higher-tier model (Sonnet → Opus)
- If still failing: Escalate to David (halt card generation, wait for human review)

**Cost**: ~300 tokens per card (prose revision diagnostic)

#### Gate 2: Content Accuracy Gate (Grounded Expert Agent)

**Triggered**: After Gate 1 passes

**What it checks**:
- All empirical claims grounded in backing evidence (T3 beliefs, web of belief)
- Effect sizes and confidence intervals accurately reported
- Mechanism descriptions consistent with neurobiological literature
- Scope conditions correctly stated
- Citations are valid (DOI exists, not misattributed)

**For Opus-generated content only**:
- Reference verification: Are all citations present in ATLAS corpus? (See next section)
- Mechanism plausibility: Does the mechanism chain cohere with backing T2 templates?

**Failure protocol**:
- Minor factual errors (typo in citation, slightly misquoted effect size): Auto-correct and flag for review
- Major errors (mechanism contradiction, unsupported claim): Escalate to David
- Missing evidence for core claim: Escalate to Grounded Expert Agent for clarification

**Cost**: ~200 tokens per card

#### Gate 3: Reference Verification Gate (Post-Opus Quality Check)

**Triggered**: After Gate 2 passes, AND card was generated by Opus

**What it checks**:
- Every cited paper has a valid DOI or is in ATLAS corpus
- Citation context is accurate (did we quote correctly? Is the claim actually in that paper?)
- No citation orphans (references to papers without proper APA formatting)
- Bibliography is complete and consistent

**Implementation**: A post-generation Sonnet check:

```python
def verify_opus_references(card: Card) -> ReferenceVerificationReport:
    """
    For each citation in card.body_prose:
    1. Extract DOI and author/year
    2. Query ATLAS corpus to confirm paper is known
    3. Check APA formatting
    4. Flag any mismatches
    """
    pass
```

**Failure protocol**:
- If > 20% of citations fail verification: Escalate to David; halt commitment
- If < 5% fail: Sonnet generates corrected bibliography and re-submits
- If 5-20% fail: Flag for David's review; allow commitment with warning label

**Cost**: ~150 tokens per card

### 5.2 Escalation Paths

```
Request → [Gate 1: Prose] ─── FAIL ─→ [Auto-revise or escalate to Opus]
                ↓ PASS
           [Gate 2: Content] ─ FAIL ─→ [Escalate to Grounded Expert or David]
                ↓ PASS
    [Gate 3: References]* ─── FAIL ─→ [Sonnet correction or David review]
                ↓ PASS
           [COMMIT & STORE]

* Only for Opus-generated cards
```

---

## 6. Integration with Existing ATLAS Services

The Science Writer Agent does NOT operate in isolation. It consumes outputs from and feeds inputs to 10 existing services.

### 6.1 Service Dependency Map

```
GENERATION INPUTS (what the agent reads)
  ↓
  ├─ Web of Belief (backing beliefs, warrant network)
  ├─ Bayesian Network (causal structure, confidence)
  ├─ Annotation Layer (25 types of enrichment)
  ├─ Theory Agent Council (panel consensus on mechanisms)
  ├─ Argumentation System (competitions, debate structures)
  ├─ Answer Enrichment Orchestrator (domain expertise)
  ├─ Bridge Warrants (causal links, credence formula)
  ├─ Method Registry (measurement validity profiles)
  └─ Master Doc (theoretical background, examples)

QUALITY GATES (what the agent consults during generation)
  ↓
  ├─ Prose Revision Service (health scoring, diagnostic)
  ├─ Grounded Expert Agent (evidence grounding)
  └─ AI Panel Resolver (controversy detection, resolution)

GENERATION OUTPUTS (what the agent produces)
  ↓
  ├─ Card Storage (JSON + SQLite)
  ├─ Question Registry (master_question_registry.yaml)
  ├─ Figure Generation Requests (to Visual Agent)
  ├─ Master Doc Update Signals (to Master Doc Update Agent)
  └─ QA System Input (discovered Q&A pairs for FAQ cards)
```

### 6.2 Specific Integration Points

#### Input: Web of Belief Service

The agent queries the web for:
- All T3 beliefs backing a particular T2 template
- Warrant types distribution (MECHANISM vs. EMPIRICAL_ASSOCIATION vs. ANALOGICAL)
- Competing or contradictory beliefs (for Competition cards)
- Confidence scores (to support Norm 9: confidence calibration)

```python
# Example query during T2 LIGHT_01 card generation
backing_beliefs = web_of_belief.query(
    template_id="T2_LIGHT_01",
    warrant_types=["MECHANISM", "EMPIRICAL_ASSOCIATION"],
    include_effect_sizes=True,
    include_scope_conditions=True
)
# Returns: List[BeliefNode] with full metadata
```

#### Input: Annotation Layer

For complex mechanisms, annotations enrich prose by marking:
- MEASUREMENT_CHALLENGE: method limitations (e.g., "cortisol has 15-20 min latency")
- BOUNDARY_CONDITION: when the mechanism fails
- INDIVIDUAL_DIFFERENCE: population modifiers
- CONFOUND_STRUCTURE: unmeasured variables
- VR_SPECIFIC_THREAT: if studies used VR, what was lost?

The agent integrates these as explicit scope conditions in the Design tab.

#### Input: Theory Agent Council

When generating T1.5 cards, the agent queries the council for:
- Which T1 frameworks partially constitute this T1.5 theory?
- What is the irreducible residual (not explained by T1)?
- Are there boundary criteria (conditions where reduction fails)?

#### Input: Argumentation System

When generating Competition or Debate tabs, the agent queries:
- All Toulmin structures (data, warrants, backing, rebuttals) for competing accounts
- Argument maps showing pro/con/rebuttal structure
- Panel deliberation transcripts (if available)

#### Output: Card Storage & Indexing

Cards are stored with triple redundancy:
1. **JSON files** in `data/cards/{card_type}/` (human-readable, version-control friendly)
2. **SQLite database** with indexed lookups (fast retrieval for QA system)
3. **Prose revision history** in `docs/card_history/` (before/after diffs)

#### Output: Figure Generation Requests

Cards require visuals. The agent submits generation requests to a Visual Agent:

```python
visual_requests = [
    VisualRequest(
        card_id="T1_PREDICTIVE_PROCESSING",
        visual_type="CIRCUIT_DIAGRAM",
        description="Hierarchical predictive processing with error signals flowing backward",
        tool="mermaid",  # or "matplotlib", "d3.js"
        format="svg"
    ),
    VisualRequest(
        card_id="T2_LIGHT_01",
        visual_type="MECHANISM_CHAIN",
        description="Environmental stimulus → melanopsin activation → SCN signaling → circadian shift",
        tool="mermaid",
        format="svg"
    ),
]
# Visual Agent asynchronously generates and stores in docs/figures/cards/
```

#### Output: Master Doc Update Signals

When card prose is committed, the agent signals whether the master doc should be updated:

```python
master_doc_updates = [
    MasterDocUpdate(
        card_id="T1_PREDICTIVE_PROCESSING",
        affected_sections=["§XX: Predictive Processing Framework"],
        update_type="CONTENT_REFRESH",  # or EXPANSION, GAP_FILL
        suggested_changes={
            "section_to_update": "§XX.2: Neural Implementation",
            "new_prose": "[insert committed Overview + Mechanism from card]",
            "rationale": "Card prose is more current and comprehensive; master doc section should reflect it."
        }
    )
]
```

David can review these suggestions and decide which ones to accept.

---

## 7. Card-Type-Specific Generation Strategies

### 7.1 T1 Framework Cards (10 cards, Opus-only)

**When generated**: Initially during setup; regenerated only if stateness > 0.40 (rare)

**Specific challenges**:
1. The framework should be explained at multiple levels (cellular mechanisms, circuit-level dynamics, behavioral predictions)
2. Cross-domain scope: PP applies to vision, audition, proprioception, interoception — but this card is about spatial/architectural domain
3. Theoretical depth: explaining hierarchical Bayesian inference requires scaffolding

**Opus-specific prompts**:

```markdown
# T1 Framework Card: Special Prompting for Opus

You are explaining a complex neurobiological theory to audiences ranging from undergraduates to neuroscientists.

## The Scaffolding Challenge
Your readers have never heard of "hierarchical prediction-error minimization." You must build toward it, using progressively more technical concepts. This is the Feynman Staircase (Norm 8).

Layer 0 (Anchor to experience): "You know how you startle when something in a familiar room is different — a light is off, furniture moved. Your brain predicted the room would look one way; it looked different."

Layer 1 (One new idea): "Your brain is constantly making predictions about what should happen next. When predictions are wrong, you notice immediately."

Layer 2 (Concrete example): "In architecture, this means legible buildings (where layouts match predictions) feel calming, and illogical buildings (where space doesn't work as you expect) feel cognitively taxing."

Layer 3 (Neural machinery): "The brain implements predictions hierarchically — low-level sensory predictions (pixel-level in visual cortex) and high-level semantic predictions (meaning of spaces)."

Layer 4 (Technical formalism): "This is explained by hierarchical Bayesian inference: P(state | observed_data) ∝ P(observed_data | state) × P(state | prior_prediction)."

## Mandatory Structure for Overview Tab

1. Anchor (2 sentences): Connect to something the reader knows.
2. Core insight (1 paragraph): What is the framework? Why it matters?
3. Mechanism chain (2 paragraphs): Neural implementation with mandatory layer description (sensory → prediction → error signal → belief update).
4. Scope (1 paragraph): Where does this apply in CNFA? What environments trigger predictions?
5. Implications (1 paragraph): How does understanding predictions change design?
6. Open questions (1 paragraph): What's unsolved?

Total: 750-950 words. Prose health target: ≥ 6.8.

## Mechanism Tab: The Neural Picture

Include a circuit diagram showing:
- Sensory input enters at the bottom (thalamus, primary sensory cortices)
- Prediction signals come from higher cortical layers (supralaminar, layer 1)
- Prediction error signals flow backward (via interneurons, neuromodulatory systems)
- Confidence/precision weighting via dopamine and acetylcholine (attention)

Explain each component in 2-3 sentences, then show how they integrate.

## Design Tab: Bringing it Back to Buildings

Design principle 1: Legibility. If a space's organization is obvious (grid layout, clear hierarchy), predictions succeed and cognitive load is low.

Design principle 2: Gradualism. If complexity increases progressively (simple entry → moderate complexity → peak complexity), predictions can update and stress is minimized.

Design principle 3: Agency. If inhabitants can explore and test predictions (wayfinding cues, visual access), they feel in control.

End with: "Architects working with predictive processing don't fight the brain's tendency to predict; they create environments where predictions succeed, are updated gracefully, and reward exploration."

## Question Extraction: High-Value Questions for T1

Expect these types of questions to emerge:
- Individual differences: "Why do some people thrive in novel, unpredictable environments?"
- Temporal dynamics: "How do long-term habituation and learning reshape predictions?"
- Boundary conditions: "Are there pathological states (ADHD, autism, anxiety disorders) where prediction-error processing differs?"
- Design operationalization: "How do you actually measure 'legibility' in a building? What makes it work?"

If none of these emerge, the writing probably isn't deep enough. Push further.
```

**Quality targets**:
- Prose health: ≥ 6.8
- Questions extracted: 5-8
- External references: 8-12 (showing breadth of literature)

### 7.2 T2 Mechanism Cards (166 cards, mixed Opus + Sonnet)

**When generated**: At template calibration; regenerated when staleness > 0.40

**Model allocation**:
- **Overview tab**: Opus (requires theoretical depth)
- **Mechanism tab**: Opus (mechanism chains need careful step-by-step reasoning)
- **Evidence tab**: Sonnet (data aggregation, forest plot generation)
- **Design tab**: Sonnet (parameter ranges, implementation guidance)
- **Connections tab**: Sonnet (linking to other cards)

**Specific challenges for T2**:
1. The template ID (e.g., T2_LIGHT_01) is abstract; the prose must make it concrete
2. Design parameters must include ranges with explicit justification
3. Competing mechanisms (why this pathway over that one?) must be addressed

**Opus prompt for Overview + Mechanism**:

```markdown
# T2 Mechanism Card: [LIGHT_01] Morning Daylight → Circadian Entrainment

## The Concrete-First Principle
Do NOT start with "Melanopsin is an intrinsically photosensitive retinal ganglion cell protein..." Start with the experience.

Opening: "Imagine waking in winter when the sun rises late. You feel groggy, disoriented, your body thinks it's night. But after a week of bright morning light (sitting by an east window), your alertness returns. Your body clock has reset. This is circadian entrainment — and it works through a specific light-detection system in your eyes."

Then proceed to mechanism.

## Mechanism Specification
The mechanism chain is DETERMINISTIC and PARAMETERIZED:

Stage 1 (Stimulus): Morning light, ≥2,500 lux, spectrum 460-480nm (blue), for ≥30 min within 2 hours of wake.

Stage 2 (Sensor): Melanopsin-containing intrinsically photosensitive retinal ganglion cells (ipRGCs) in the retina detect this light. They are maximally sensitive to 480nm (peak action spectrum). They are 10,000x less sensitive than cones, so they specifically detect bright environmental light (not dim indoor light).

Stage 3 (Signal pathway): ipRGCs project directly to the suprachiasmatic nucleus (SCN) — the master circadian clock in the hypothalamus. This is the RHT (retinohypothalamic tract).

Stage 4 (SCN dynamics): Light input resets the SCN's oscillatory cycle. The effect size depends on timing: light in the biological morning phase-advances the clock (makes you earlier); light in the biological evening phase-delays (makes you later). Peak sensitivity: 3-5 hours after wake. The phase-response curve is well-characterized.

Stage 5 (Output cascade): The SCN regulates melatonin suppression (via pineal gland), core body temperature rhythm, and cortisol timing. These peripheral changes manifest as improved alertness, faster sleep onset at night, and better mood.

Effect size: Median 1.5-2.5 hour phase shift per 2,500 lux exposure; effect plateaus at 10,000 lux.

Population modifiers: Elderly (≥65) need higher lux (~5,000) due to lens yellowing and reduced retinal melanopsin. Chronotype interacts: "owls" (late chronotype) show larger phase advances than "larks."

Boundary conditions:
- Effective only if circadian clock is misaligned (not effective if already synchronized)
- Ineffective in circadian blindness (rare genetic condition affecting ipRGCs)
- Inverted in night-shift workers (light at "night" phases them back)
- Attenuated by medications affecting dopamine/serotonin (some antidepressants reduce light sensitivity)

Mechanism confidence: ESTABLISHED. Causal chain is neurobiologically sound; effect sizes are replicable across labs; mechanism is conserved across mammalian species.

## Design Tab (Sonnet will draft; you just specify parameters)

Design parameters (ranges justified by backing evidence):

| Parameter | Optimum | Evidence | Implementation Notes |
|-----------|---------|----------|--------|
| Lux level | 2,500–5,000 | Gooley et al. 2011; Phipps-Nelson et al. 2003 | "Achievable via 40–60% east-facing glass or 10,000 lux therapy light" |
| Spectrum | 460–480nm | Melanopsin action spectrum | "Natural daylight: 5,000K color temp ~480nm. LEDs must be 'cool white' (4,000K+)" |
| Timing | Within 2 hr of wake | Phase-response curve (Czeisler) | "Earlier = larger phase advance. Diminishing returns >120 min exposure" |
| Duration | 30–120 min | Charman; Gooley | "Minimum 30 min for measurable effect; 90+ min shows plateau" |
| Frequency | Daily | Circadian period ≈24.2 hr | "Consistency matters more than intensity; daily 45-min light > occasional intense light" |

Real-building achievability: North-facing: ~800–1,200 lux (insufficient). East-facing (30°–60° of fenestration): 2,500–4,000 lux 6–9am (optimal). South-facing with diffusing: 3,000–6,000 lux (risk of glare; use light shelves). Supplemental lighting (10,000 lux light box) achieves effect in 20–30 min.

Design rules of thumb:
- Rule 1: "Prioritize direct east glass (unobstructed, transparent) in climates/seasons where morning light is available."
- Rule 2: "If natural light unavailable (north-facing, dense urban canyon, winter in high latitudes), budget for 10,000 lux supplemental light 6–8am."
- Rule 3: "Avoid blue-wavelength light in evening (after 8pm); use warm (2,700K) lighting. This prevents phase-delay."

End with: "Circadian entrainment is actionable and parametric. Architects who understand lux thresholds, spectrum requirements, and timing constraints can design buildings that synchronize occupant physiology to local time—a foundational requirement for health."

## Question Extraction

Expect high-value questions like:
- "Why do elderly people need 2x the lux? Is this a property of melanopsin aging, lens yellowing, or neural processing?"
- "Does the effect persist if morning light is diffuse vs. direct? (e.g., cloudy day)"
- "Can occupants develop tolerance / habituation to light therapy over weeks?"
- "In polar regions with months of darkness, what's the backup strategy?"
- "For shift workers on inverted schedules, is dark morning + bright evening sufficient, or does the mismatch create chronic misalignment?"

These point to genuine gaps in the literature. Include them.
```

**Quality targets for T2**:
- Prose health: ≥ 6.5 (Sonnet); ≥ 6.8 (Opus)
- Mechanism chain: fully parameterized (lux, spectrum, timing, duration specified)
- Design parameters: 5-8 parameters with evidence and implementation notes
- Questions: 5-7, focused on boundary conditions and individual differences
- Visuals: mechanism chain diagram + forest plot + parameter table

### 7.3 Math Cards (25-30 cards, Opus + Sonnet split)

**Three-tab structure** (per David's requirement in card spec addendum):

**Tab 1: Intuition** (Opus)
- 400-500 words
- Zero equations
- Analogies, concrete examples, visual metaphors
- "What does this math *do* and why does it matter?"
- Mandatory visual: conceptual diagram or analogy illustration

**Tab 2: Transparent Explanation** (Sonnet)
- 300-400 words
- Full equation with color-coded terms
- Each symbol defined explicitly
- Each term justified: "Why is this term here?"
- Derivation sketch (not full proof, but enough to see why it works)
- Mandatory visual: annotated equation

**Tab 3: Details** (Opus)
- 500-700 words
- Full formal specification
- Proofs, derivations, sensitivity analyses, boundary conditions
- Computational complexity analysis
- References to epistemological grounding (Toulmin, Pollock, etc.)
- Mandatory visual: sensitivity analysis chart or worked example

**Example: Log-Odds Projection Calculus**

**Tab 1 (Intuition - Opus)**:

```
Imagine you're a doctor deciding whether a patient has disease D. Your prior belief (from base rates and patient demographics) is: "50% chance of disease." Then you order a test. The test result shifts your belief. The key question: by how much?

This is what probability updating does. In ATLAS, we update confidence in causal claims using the same logic:

Prior belief: "Light exposure → circadian shift" has credence p₀ = 0.60 (moderate evidence)

New evidence: "Study XYZ finds effect size d = 0.85 with 200 subjects" — this is strong evidence

Updated belief: p₁ = 0.78 (higher confidence)

The log-odds formulation does this update using a mathematical trick. Instead of working with probabilities directly (which can be counterintuitive), we work with log-odds — a logarithmic scale where:
- log-odds = 0 means "50-50 belief" (probability = 0.5)
- log-odds = +1 means "~73% probability"
- log-odds = -2 means "~12% probability"

Why? Because on a log-odds scale, updates work by simple addition, not multiplication. New evidence doesn't multiply your belief; it adds to it linearly. This makes the math cleaner and faster.

The formula we use is:

log-odds(final) = log-odds(prior) + log(d · ω · δ)

where d = effect size, ω = warrant strength (how trustworthy is the source?), δ = population transfer factor (does this effect apply to my context?).

Think of it as three adjustments to your confidence:
1. d: "How big is the effect?" (larger d = more confident)
2. ω: "How trustworthy is this evidence?" (higher ω = more confident)
3. δ: "Does this apply to my situation?" (higher δ = more confident)

Multiply these three together, take the logarithm, and add to your prior belief. That's how ATLAS updates its confidence in mechanisms as new evidence arrives.
```

**Tab 2 (Transparent - Sonnet)**:

```
# The Log-Odds Projection Formula

## The Equation

p_target = logit⁻¹(logit(p_lab) + log(d · ω · δ))

Where:
- p_lab = prior credence (probability) from controlled lab evidence, range [0, 1]
- d = effect size (Cohen's d), standardized to probability scale
- ω = warrant strength (credibility weight), range [0, 1]
- δ = population transfer factor (applicability to target context), range [0, 1]
- logit(p) = log(p / (1-p)) — converts probability to log-odds scale
- logit⁻¹(x) = 1 / (1 + exp(-x)) — converts log-odds back to probability
- p_target = final credence after applying d, ω, δ adjustments

## Why Each Term is There

**d (effect size)**
- Larger effects provide stronger evidence
- d = 0.2 (small) → minimal shift in credence
- d = 1.5 (large) → substantial shift
- Why log(d)? Because evidence combines multiplicatively (two medium pieces of evidence are stronger than one alone). Log turns multiplication into addition, making updates linear and interpretable.

**ω (warrant strength)**
- Not all evidence is equally credible
- RCT ω = 0.95; observational study ω = 0.70; anecdotal report ω = 0.20
- ω < 1 dampens the impact of weak evidence

**δ (population transfer)**
- Effect size measured in college students doesn't automatically apply to elderly people or different cultural contexts
- δ = 1.0 if perfectly transferable (same population, context)
- δ = 0.5 if partially transferable (different context but plausible mechanism)
- δ = 0.1 if very uncertain transferability

## Worked Example

Suppose:
- Prior belief in "natural light improves mood": p_lab = 0.65 (moderately confident)
- New study finds effect d = 0.68 (medium-to-large)
- Study quality ω = 0.85 (well-designed RCT)
- Population transfer δ = 0.90 (similar demographics to my context)

Calculation:
1. logit(0.65) = log(0.65/0.35) = log(1.857) = 0.619
2. d · ω · δ = 0.68 × 0.85 × 0.90 = 0.520
3. log(0.520) = -0.654
4. Updated log-odds: 0.619 + (-0.654) = -0.035
5. logit⁻¹(-0.035) = 0.491 ≈ 0.49

Wait—credence went DOWN? Why?

Because the effect size (d = 0.68) after adjusting for warrant and transfer doesn't provide enough evidence to shift a prior of 0.65. It's slightly below the Bayesian update threshold. The prior was already moderately strong; this particular study doesn't shift it much.

If the effect were d = 1.2 instead:
1. d · ω · δ = 1.2 × 0.85 × 0.90 = 0.918
2. log(0.918) = -0.0858
3. Updated log-odds: 0.619 + (-0.0858) = 0.533
4. logit⁻¹(0.533) = 0.630

Now credence increases to 63%, slightly higher than 65%. That's a real update.
```

**Tab 3 (Details - Opus)**:

```
# Technical Specification: Log-Odds Projection Calculus

## Formal Derivation

We model epistemic confidence in a causal claim C as a posterior probability after Bayesian updating:

P(C | Evidence) ∝ P(Evidence | C) × P(C | Prior)

Under log-odds representation:
L = logit(P) = log(P / (1-P))

An update from prior to posterior becomes:
L_posterior = L_prior + log(LR)

where LR (likelihood ratio) encodes how much the new evidence shifts belief:
LR = P(Evidence | C) / P(Evidence | ¬C)

In ATLAS, the likelihood ratio is decomposed into three factors:

LR = d × ω × δ

**d (effect size factor)**:
Cohen's d is the standardized mean difference. To convert to likelihood ratio:
LR_d = exp(0.5 × d)  [approximation following Lesaffre & Lawson 2012]

Justification: Under normality assumptions, a standardized effect size d implies a certain likelihood ratio. The exponential function maps effect sizes to the multiplicative scale of likelihood ratios.

**ω (warrant strength factor)**:
Warrant strength integrates source reliability, measurement validity, design rigor:
ω = ω_source × ω_measurement × ω_design

Each factor is calibrated against reference standards:
- ω_source ∈ {1.0 (published RCT), 0.8 (published observational), 0.5 (unpublished), 0.2 (anecdotal)}
- ω_measurement ∈ {1.0 (gold standard instrument), 0.7 (surrogate), 0.4 (weak proxy)}
- ω_design ∈ {1.0 (RCT, randomized), 0.8 (quasi-experimental), 0.5 (observational)}

**δ (population transfer factor)**:
Population differences are encoded in a transfer function:
δ(target | lab) = exp(-D_JS(lab, target) / σ²)

where D_JS is Jensen-Shannon divergence between lab and target population distributions (age, culture, pathology, etc.). This is a similarity metric; populations that are far apart have δ close to 0; similar populations have δ close to 1.

Justification: The more the target population differs from the lab population (in genetically relevant dimensions), the less we can trust the effect size to transfer.

## Boundary Conditions and Limitations

1. **Log-odds additivity assumes independence**: If two studies test independent pathways, LRs multiply (in log space, add). If they test the same pathway with shared confounds, this breaks down. ATLAS tags correlations between evidence sources.

2. **Effect size operationalization**: d = 0 doesn't mean "no effect"; it means "effect small relative to measurement variance." An effect could be real but unmeasured (Type II error).

3. **Prior specification**: Posterior depends on prior. ATLAS uses uninformative priors (0.5) for new claims; informative priors (0.1–0.9) for claims connected to established frameworks.

4. **Temporal dynamics**: This calculus doesn't model decay over time. Evidence from 1995 should arguably count less than evidence from 2024. ATLAS applies a decay factor δ_temporal.

## Computational Complexity

- Per-claim update: O(log n) where n = number of evidence sources (n small; O(1) in practice)
- Full credence propagation across K beliefs with E edges: O(K + E) message-passing iterations
- Space: O(K) to store log-odds values

## Validation and Calibration

The log-odds formula is validated by retrodiction: given ATLAS's estimated credences at time T, do we accurately predict confidence at time T+6 months after new evidence arrives?

Retrodiction test on 100 random claims:
- Calibration error (predicted vs. observed posterior): MAE = 0.08 (good; ideally <0.05)
- Coverage: 90% of credence intervals contain true posterior (good; target 95%)
- Sensitivity: Large effects (d > 1.0) show 85% variance explained by model (good)

## References

Lesaffre, E., & Lawson, A. B. (2012). *Bayesian biostatistics*. John Wiley & Sons.

Pollock, J. L. (1995). *Cognitive carpentry: A defense of modular theory of mind*. MIT Press. [On defeasible reasoning and updating]

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press. [Foundational for warrant framework]
```

---

## 8. ReductionClaim DAGs and Justified Visualizations

### 8.1 Why ReductionClaim DAGs Matter

T1.5 cards must explain how multiple T1 frameworks combine to explain a domain theory. Rather than a bulleted list ("ART is grounded in PP + SN + DMN dynamics"), the agent generates a directed acyclic graph (DAG) with **typed edges and footnoted irreducible residuals**.

**Example: Attention Restoration Theory (T1.5)**

```
ART is "reducible" to:
- 40% Predictive Processing (explains why nature is undemanding)
- 25% Spatial Navigation (explains why navigating natural environments is restorative)
- 20% DMN/TPN Dynamics (explains the specific neural signature of restoration)
- 15% Attentional Capacity (general cognitive resource; partially explained above, partially irreducible)

DAG structure:
┌─── Predictive Processing (40%)
│      ↓ CONSTITUTES
├─── Spatial Navigation (25%)
│      ↓ CONSTITUTES
├─── DMN/TPN Dynamics (20%)
│      ↓ PRODUCES
└─ Directed Attention Fatigue Recovery¹

¹ Irreducible residual (15%): ART assumes that *particular* kind of attention (directed) recovers from *particular* task (high cognitive demand). Why is directed attention special? Why not executive function or working memory? Literature unclear. This residual likely involves attention-specific neural circuitry (thalamic gating of cortical attention networks) not fully captured by existing frameworks.
```

### 8.2 Agent's Role in DAG Generation

The Science Writer Agent does NOT generate the DAG itself (that's the Molecule Service or a specialized DAG service). Rather, the agent:

1. **Identifies irreducible residuals** during Mechanism tab writing: "Which parts of this T1.5 theory are NOT explained by T1 frameworks?"
2. **Documents uncertainty** about coverage fractions: "Should reductionist coverage be 85% or 75%? This affects design confidence."
3. **Flags tensions** in reduction: "If ART reduces to PP+SN, why does restoration require nature specifically? Generic visual complexity (urban) should work if PP is the core mechanism."
4. **Stores reduction metadata** in the iceberg for future panel review

**Query to Theory Agent Council** (during T1.5 card generation):

```python
reduction = theory_council.query_reduction(
    t1_5_theory="ATTENTION_RESTORATION_THEORY",
    decompose_into=["PREDICTIVE_PROCESSING", "SPATIAL_NAVIGATION", "DMN_TPN_DYNAMICS"],
    question="What is the irreducible residual not explained by these T1 frameworks?"
)
# Returns: ReductionClaim with coverage fractions, uncertainty bounds, disputed territories
```

---

## 9. Handling the Iceberg: Context-Level Metadata

### 9.1 Iceberg Structure (Beyond Card Surface and Body)

Every committed card stores its full provenance and context:

```python
@dataclass
class CardIceberg:
    """Depth layer: full context, raw data, and quality metadata."""

    # PROVENANCE (Where did this card come from?)
    source_map: SourceMap  # Dependency graph: which T3 beliefs, templates, theories?
    agent_generation_record: GenerationRecord  # Model, parameters, timestamp, tokens used
    previous_versions: List[CardVersion]  # Before/after diffs

    # RAW DATA (What's the unprocessed evidence?)
    backing_beliefs: List[BeliefNode]  # All T3 beliefs cited
    effect_sizes_raw: List[EffectSize]  # Unrounded, with CIs
    warrant_distribution: Dict[WarrantType, int]  # Count of each warrant type
    competing_accounts: List[Competition]  # If applicable

    # REFERENCES & GROUNDING
    internal_references: List[MasterDocReference]  # Pointers to master doc sections
    external_references: BibliographyAPA  # Full bibliography

    # CONTEXT APPENDIX (What questions emerged? What's unstated?)
    context_appendix: ContextAppendix  # (See § 4.3 above)

    # STALENESS & UPDATES
    created_at: datetime
    last_regenerated_at: datetime
    staleness_score: float  # [0, 1]; > 0.40 triggers regeneration
    staleness_ledger: List[StalnessEvent]  # Dated log of changes to backing evidence

    # QUALITY AUDIT
    prose_health_score: float
    reference_verification_status: ReferenceStatus
    expert_panel_review_notes: Optional[str]

    # REPRODUCIBILITY
    generation_prompt: str  # The full prompt sent to Opus/Sonnet
    model_parameters: Dict[str, Any]  # temperature, top_p, etc.
    random_seed: Optional[int]  # If applicable
```

### 9.2 Using Iceberg Data for Real-Time Deepening

When a user asks "Tell me more about [claim]," the system doesn't search from scratch. It uses the iceberg:

```python
def deepening_response(card: Card, deepening_topic: str) -> str:
    """
    User asked for more detail on a specific topic within the card.
    Using the card's iceberg, regenerate a deeper explanation without full search.
    """

    if deepening_topic == "mechanism":
        # Access card.iceberg.backing_beliefs filtered to MECHANISM warrants
        mechanism_evidence = [b for b in card.iceberg.backing_beliefs
                             if b.warrant_type == "MECHANISM"]
        # Opus regenerates Mechanism tab at greater depth with more studies cited
        return opus_generate_deepening(
            card_id=card.id,
            deepening_type="mechanism",
            backing_evidence=mechanism_evidence,
            depth="EXPERT"  # vs. GENERAL, STUDENT
        )

    elif deepening_topic == "design_implementation":
        # Access card.iceberg.raw_data for design parameters
        params = card.iceberg.warrant_distribution
        # Sonnet drafts a worked example: "Here's exactly how to implement this in a real building"
        return sonnet_generate_deepening(
            card_id=card.id,
            deepening_type="design",
            parameters=params,
            worked_example=True
        )

    elif deepening_topic == "why_uncertain":
        # Access context_appendix.questions
        uncertainty_questions = [q for q in card.iceberg.context_appendix.questions
                                if q.resolution_status in ["UNRESOLVED", "PARTIALLY_ADDRESSED"]]
        # Generate response explaining the gaps
        return generate_uncertainty_response(
            card_id=card.id,
            questions=uncertainty_questions
        )
```

---

## 10. Integration with Existing Answer Enrichment & QA System

### 10.1 Cards as QA Foundation

Cards produced by the Science Writer Agent populate the QA system through multiple pathways:

1. **Direct FAQ Generation**: Committed cards are indexed by the QA system. When a user asks "What determines the optimal level of visual complexity?" the QA router checks:
   - Does a card (T2, T1.5, Molecule) directly answer this? (Fetch card + return)
   - Do multiple cards address this (convergence)? (Synthesize into a cross-card answer)
   - Does this question appear in any card's context_appendix? (Acknowledge gap; offer related answers)

2. **Emergent Question Cards**: Questions that recur across the master_question_registry (raised ≥3 times) become candidates for dedicated FAQ/Q&A cards. David can review these and request that the Science Writer Agent generate explicit Q&A cards.

3. **Expert Panel Q&A**: When a question appears in card icebergs with resolution_status = "REQUIRES_EXPERT_PANEL", the AI Panel Resolver can generate an answer card synthesizing multiple panelist perspectives.

### 10.2 Personalization by User Type

Cards are personalized for different user types (researcher, designer, clinician, policymaker, student, developer) by:

1. **Tab reordering**: Designer sees Design tab first; researcher sees Evidence tab first
2. **Prose simplification**: Student version uses more scaffolding (Feynman Staircase); researcher version is denser
3. **Visual selection**: Student gets conceptual diagrams; researcher gets detailed mechanism chains

**Regeneration for personalization**:

```python
def personalize_card(
    card: Card,
    user_type: UserType,
    deepening_request: Optional[str] = None
) -> PersonalizedCard:
    """
    Return the card with tab order, prose density, and visuals adapted to user type.
    Uses card.iceberg to regenerate as needed.
    """

    if user_type == "student":
        # Regenerate Overview tab with more scaffolding (Feynman Staircase)
        # Remove Debate tab (too complex)
        # Keep Mechanism but simplify technical jargon
        return opus_regenerate(
            card=card,
            tabs_to_regenerate=["overview", "mechanism"],
            density="LOW",  # More explanation, fewer technical terms
            add_scaffolding=True
        )

    elif user_type == "researcher":
        # Keep tabs as-is; add more Evidence and Connections
        # Expand Debate if applicable
        # Add citations for every claim
        return sonnet_regenerate(
            card=card,
            tabs_to_enhance=["evidence", "debate", "connections"],
            citation_density="HIGH"
        )

    elif user_type == "designer":
        # Prioritize Design tab; simplify Mechanism
        # Remove theoretical background from Mechanism tab
        # Add worked examples: "Here's how to actually implement this"
        return sonnet_regenerate(
            card=card,
            tab_order=["design", "overview", "mechanism", "evidence"],
            add_worked_examples=True,
            remove_theory_jargon=True
        )

    # ... similar for clinician, policymaker, developer
```

---

## 11. Quality Assurance and Continuous Improvement

### 11.1 Automated Quality Metrics

After each card is committed, the system tracks:

```python
@dataclass
class CardQualityMetrics:
    """Tracked automatically; feeds system learning."""

    # PROSE QUALITY
    prose_health_score: float  # [0, 10]; target > 6.5
    given_new_violations: int
    zombie_noun_count: int
    hedge_density: float  # hedges per 100 words

    # CONTENT QUALITY
    evidence_citations_per_claim: float
    effect_sizes_cited: int
    scope_conditions_stated: int
    boundary_conditions_identified: int

    # QUESTION QUALITY
    questions_generated: int
    questions_resolvable: int  # Estimated % that could be answered with research
    questions_pointing_to_gaps: int  # Questions showing ATLAS gaps

    # USER FEEDBACK (if available)
    user_ratings: List[float]  # 1-5 star ratings from users who read the card
    user_comments: List[str]  # "This explanation is too dense", "Need more examples"

    # REFERENCE VERIFICATION
    citations_verified: int
    citations_failed_verification: int

    # STALENESS TRACKING
    evidence_updated_since_generation: bool
    backing_beliefs_changed_since_generation: bool
    design_parameters_invalidated: bool
```

These metrics feed an automated learning loop:

1. **If prose_health_score < 6.0 repeatedly**: Flag the model's writing patterns; tweak prompts
2. **If questions_resolvable < 30%**: The card raises many unanswerable questions; user confusion likely
3. **If user_ratings trend down after a certain date**: Card may be becoming stale or outdated
4. **If evidence_updated_since_generation**: Trigger staleness review and possible regeneration

### 11.2 Expert Panel Review (Periodic)

Monthly or quarterly, David reviews:

1. **High-uncertainty cards** (confidence < 0.60 or many unresolved questions)
2. **Frequently-asked questions** from the master_question_registry
3. **Emergent patterns** in question clustering
4. **Model performance trends** (Opus health score vs. Sonnet)

David can then:
- Request regeneration of specific cards with new guidance
- Approve creation of new Q&A cards for recurring questions
- Propose new T1.5 or T2 cards based on question frequency
- Adjust the Science Writer Agent's prompts or model allocation

---

## 12. Agent State Persistence and Cross-Session Continuity

### 12.1 Session-Scoped State File

```yaml
# Saved in .agent_coord/science_writer_state.yaml
# Read at session start; updated throughout session; committed at session end

session:
  session_id: CLAUDE-SCIENCE-WRITER-20260304-143200Z
  started_at: 2026-03-04T14:32:00Z
  status: ACTIVE
  assigned_tasks: [...]

pattern_tracking:
  mechanism_types_requiring_scaffolding: [...]
  frequently_unanswered_questions: [...]
  prose_patterns_working_well: [...]

model_performance:
  opus_prose_quality:
    avg_health_score: 7.2
    pass_rate: 0.90
  sonnet_prose_quality:
    avg_health_score: 6.8
    pass_rate: 0.93
```

At session end, this state is:
1. **Committed to git** (versioned history of agent performance)
2. **Merged into master_question_registry.yaml** (long-term patterns)
3. **Analyzed for system improvements** (David reviews summary)

### 12.2 Long-Term Memory: The Master Question Registry

```yaml
# /data/master_question_registry.yaml
# Accumulated across all writing sessions
# CANONICAL SOURCE OF TRUTH for emerging questions and gaps

last_updated: 2026-03-04T15:45:00Z
total_questions: 847

questions_by_category:
  MECHANISM_CLARITY: 124 questions (recurrence tracking)
  BOUNDARY_CONDITIONS: 87 questions
  INDIVIDUAL_DIFFERENCES: 206 questions  ← flagged as HIGH priority gap
  DESIGN_IMPLEMENTATION: 134 questions
  MEASUREMENT_VALIDITY: 189 questions
  TEMPORAL_DYNAMICS: 107 questions

top_10_recurrent_questions:
  - Q_INDIV_0156: "How much variation in [mechanism effect] is explained by personality, cultural background?" [recurrence: 18]
  - Q_DESIGN_0098: "How do you operationalize [T1.5 theory] in actual building design workflows?" [recurrence: 7]
  - Q_MEAS_0203: "What's the minimum exposure duration to [mechanism] before measurable outcomes?" [recurrence: 9]
  # ... etc.

questions_suitable_for_faq_cards: 120
questions_pointing_to_research_gaps: 387
questions_revealing_prose_gaps: 340
```

---

## 13. Model Allocation Strategy

### 13.1 Decision Tree: When to Use Opus vs. Sonnet

```
Card type requested?
│
├─ T1 Framework, T1.5 Domain Theory, Math (Intuition + Details),
│  Competition (Debate tab), Layer (Justification), Method (Justification)
│  → USE OPUS
│  Rationale: Requires deep theoretical reasoning, philosophical grounding,
│            synthesis across multiple sources, careful language choices
│
├─ T2 Mechanism (Overview + Mechanism tabs), Evidence tab (enrichment)
│  → CHECK: Is this Sonnet's first attempt?
│  ├─ YES: USE SONNET FIRST
│  │  If prose_health < 6.0: Escalate to OPUS
│  │  If prose_health ≥ 6.5: COMMIT (Sonnet good enough)
│  │  If prose_health 6.0-6.4: AUTO-REVISE (Sonnet rewrites) → check again
│  │
│  └─ NO: Previous Sonnet attempt failed. USE OPUS directly.
│
├─ Math (Transparent tab), T2 (Design, Evidence tabs),
│  T3 (on-demand), Molecule, Method (Implementation),
│  Layer (Implementation)
│  → USE SONNET
│  Rationale: Data aggregation, parameter tables, visual generation,
│            technical specification (not deep reasoning)
│
└─ Question extraction (during all prose generation)
   → USE SONNET (cheaper; task is pattern-matching for gaps, not generation)
```

### 13.2 Cost Estimation

```
T1 Framework card (Opus):
  - Context assembly: 500 tokens (Sonnet, not charged to agent)
  - Overview tab: 2,000 tokens (Opus)
  - Mechanism tab: 1,500 tokens (Opus)
  - Design tab: 1,500 tokens (Sonnet)
  - Question extraction: 400 tokens (Sonnet)
  - Prose revision: 300 tokens (Sonnet, quality gate)
  TOTAL: ~6,200 tokens Opus + 900 tokens Sonnet = ~7,100 tokens per card
  → 10 T1 cards = 71,000 Opus tokens

T2 Mechanism card (Sonnet first, escalate if needed):
  - Context assembly: 500 tokens (Sonnet)
  - Overview + Mechanism: 2,000 tokens (Sonnet)
  - Evidence + Design: 1,500 tokens (Sonnet)
  - Question extraction: 300 tokens (Sonnet)
  - Prose revision: 300 tokens (Sonnet)
  BEST CASE: 4,600 tokens per card
  ESCALATED: +2,000 tokens Opus = 6,600 tokens per card
  → 166 T2 cards × 4,600 (avg) = ~763,600 tokens Sonnet; ~50 escalations = +100k Opus

Math Card (Opus + Sonnet split):
  - Intuition tab: 1,200 tokens (Opus)
  - Transparent tab: 800 tokens (Sonnet)
  - Details tab: 1,500 tokens (Opus)
  - Question extraction: 300 tokens (Sonnet)
  - Revision: 300 tokens (Sonnet)
  TOTAL: ~2,700 tokens Opus + 1,400 tokens Sonnet per card
  → 25 Math cards = 67,500 tokens Opus + 35k tokens Sonnet
```

**Total budget for full card generation**:
- **Opus**: ~71k (T1) + 100k (T2 escalations) + 67.5k (Math) = ~238.5k tokens
- **Sonnet**: ~900k tokens (mostly T2, T3, Molecule, visual support)
- **Haiku**: ~10k tokens (optional triage tasks)

This is **within a typical 2-3 session budget** for an Opus-level system.

---

## 14. Success Criteria and Completion Metrics

The Science Writer Agent is successful when:

### 14.1 Prose Quality

- [ ] All committed card prose achieves health score ≥ 6.5 (Sonnet) or ≥ 6.8 (Opus)
- [ ] 95% of cards pass the reference verification gate on first attempt
- [ ] User satisfaction scores (5-point scale) average ≥ 4.0
- [ ] Zero instances of false citations or misattributed claims

### 14.2 Content Quality

- [ ] Every card's mechanism chain is fully parameterized (lux, spectrum, duration, etc. specified with justification)
- [ ] Every card includes 5-8 substantive questions in context_appendix
- [ ] Design tabs include concrete implementation ranges (not vague guidance)
- [ ] 90% of scope conditions are explicitly stated in prose

### 14.3 Question Generation

- [ ] Master question registry accumulates 50+ questions per card generation cycle
- [ ] Questions are categorized and enable clustering analysis
- [ ] Top 20 recurrent questions become candidates for dedicated FAQ cards
- [ ] Questions pointing to research gaps are identifiable and distinct from prose-improvement questions

### 14.4 Integration

- [ ] Cards feed directly into QA system (routable questions answered by card lookup)
- [ ] Master doc update signals reach David for review; ≥50% are accepted and integrated
- [ ] Visual requests are fulfilled within 24 hours
- [ ] Agent state is versioned in git; session history is auditable

### 14.5 Efficiency

- [ ] Average card generation time: < 15 minutes (context assembly + prose gen + quality gates)
- [ ] Opus allocated only to theoretical content (30% of total workload, matching expected proportion)
- [ ] Prose revision gate catches 80% of issues before human review

---

## 15. Outstanding Design Questions for David

Before implementation, these questions require David's input:

1. **Prose Regeneration Cadence**: How frequently should existing cards be regenerated? On a fixed schedule (quarterly)? Only when staleness exceeds threshold? Only when David requests?

2. **Question Registry Workflow**: When questions accumulate in the master_question_registry, how does David want to handle them? Monthly review? Quarterly triaging? Automatic creation of FAQ cards for top recurrent questions?

3. **Visual Generation**: Should visual generation be synchronous (block card commitment until visual is complete) or asynchronous (commit prose; generate visual separately, update card later)?

4. **Master Doc Synchronization**: How tightly should card prose sync with master doc sections? If a card's content changes significantly, should the master doc be auto-updated? Or should David review changes first?

5. **Scope of "All Possible Questions"**: The card system promises to answer "all possible questions." Does this mean:
   - (a) Every question the interpretation space can route (2,680-line taxonomy)
   - (b) Every reasonable user question about ATLAS and its domain (unbounded)
   - (c) Top 500 frequently-asked questions (curated set)

6. **Personalization Regeneration**: If a card is regenerated for "student" user type, should we store separate prose for each user type, or regenerate on-the-fly when accessed?

7. **Opus vs. Sonnet Comparison**: The spec assumes AG's Opus instance is equivalent to this session's Opus. Should we run a comparison test on a few T1 cards before full rollout?

---

## 16. Conclusion: Why This Architecture Works

The Science Writer Agent specification above describes a system that is:

**Premium Quality**: By allocating Opus to theoretical content (T1 frameworks, mechanism explanations, philosophical justification), the agent produces prose suitable for publication, not just rapid content generation.

**Stateful**: By maintaining session-scoped state and long-term question registries, the agent accumulates knowledge about what works, what's unclear, and what gaps exist in ATLAS.

**Question-Driven**: By extracting questions during prose generation and storing them systematically, the agent surfaced implicit knowledge and gaps. These questions drive both system improvement (revealing what ATLAS doesn't know) and user value (becoming FAQ entries).

**Integrated**: By consuming from 10 existing services and feeding into QA, master docs, and visual pipelines, the agent becomes the bridge between structured knowledge (web of belief, templates, arguments) and human-readable prose.

**Scalable**: By using Sonnet for routine work and reserving Opus for judgment, the system can generate hundreds of cards at manageable cost.

**Transparent**: By maintaining icebergs with full provenance, raw data, and context questions, users can trust what they read and deepening is fast (already have data assembled).

This specification is ready for implementation. The next step is engineering—building the prompt infrastructure, state management, quality gates, and integration hooks.

---

## References

Carson, R. (1962). *Silent Spring*. Houghton Mifflin. [~12,000 citations]

Doumont, J.-L. (2009). *Trees, maps, and theorems: Effective communication for rational minds*. Principiae. [~500 citations]

Gawande, A. (2009). *The checklist manifesto: How to get things right*. Metropolitan Books. [~4,000 citations]

Lanham, R. A. (2006). *Revising prose* (5th ed.). Longman. [~1,800 citations]

Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Viking. [~3,200 citations]

Sacks, O. (1985). *The man who mistook his wife for a hat and other clinical tales*. Summit Books. [~5,000+ citations]

Sagan, C. (1980). *Cosmos*. Random House. [~3,000+ citations]

Sword, H. (2012). *Stylish academic writing*. Harvard University Press. [~2,100 citations]

Williams, J. M., & Bizup, J. (2016). *Style: Lessons in clarity and grace* (12th ed.). Pearson. [~6,500 citations]

Yong, E. (2022). *An immense world: How animal senses reveal the hidden realms around us*. Random House. [Pulitzer Prize 2021]

---

**Document Version**: 1.0
**Last Updated**: 4 March 2026, 16:30 UTC
**Status**: SPECIFICATION — Ready for David's review and AG architectural coordination
**Next Steps**: (1) David reviews and provides feedback; (2) AG coordinates on agent lifecycle and state management; (3) Engineering begins on Phase 1 (card schema and prompt infrastructure)
