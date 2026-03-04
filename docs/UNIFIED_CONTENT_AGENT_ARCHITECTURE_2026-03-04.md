# Unified Content Agent Architecture for ATLAS

**Version**: 1.0
**Date**: 4 March 2026
**Authors**: AG (5-agent decomposition) and CW (prose/science writer deepening)
**Reviewed by**: David Kirsh
**Status**: SPECIFICATION — Ready for implementation

---

## Executive Summary

This document reconciles two complementary specifications for the ATLAS knowledge system into a single unified architecture. The result preserves AG's clean modality-based agent decomposition (prose, visual, stats, layout, expert) while incorporating CW's deep epistemic and question-generation insights into every agent. The system produces publication-quality content while systematically surfacing the implicit questions that writing reveals—converting hidden gaps into actionable intelligence for ATLAS improvement.

**Key integration points**:
- AG's 5-agent pipeline remains the structural backbone
- CW's 7-stage prose pipeline becomes the template for all agents
- Question-generation extends from prose to visuals, stats, and layouts
- The context appendix (card iceberg) stores all questions, assumptions, and uncertainties
- Model allocation (Opus for theoretical, Sonnet for routine) applies across all agents
- Master question registry accumulates patterns for system-level analysis

This is not two separate systems; it is one architecture where every agent asks the same epistemic questions that CW identified in prose writing, and every agent maintains the same commitment to transparency and improvement.

---

## Table of Contents

1. The 5-Agent Architecture: Overview and Roles
2. Agent Collaboration Pipeline
3. The Science Writer Agent (Prose): Full Specification
4. The Visual Designer Agent: Question-Generation Extended
5. The Stats Communicator Agent: Power and Gap Detection
6. The Layout Composer Agent: Progressive Disclosure with Questions
7. The System Expert Agent: Persistent Knowledge with Interrogation
8. The Question-Generation Protocol: Universal Across All Agents
9. The Context Appendix: Iceberg Design for Every Card
10. Model Allocation Strategy: Opus vs. Sonnet Across All Agents
11. Card-Type-Specific Generation Strategies
12. Quality Gates: Three-Tier System with Escalation
13. Development Mode vs. Production Mode
14. Staleness Detection and Regeneration
15. Integration with Existing ATLAS Services
16. Success Conditions: Comprehensive List
17. Open Questions for David
18. Panel Review Record and Incorporated Feedback

---

## § 1. The 5-Agent Architecture: Overview and Roles

The system decomposes content generation into five specialized agents, each owning one presentation modality. This decomposition enables parallel development, focused expertise, and clean interfaces.

### Agent Roles (from AG with CW depth)

| Agent | Role | Primary Modality | Question-Generation? | Model Allocation |
|-------|------|------------------|----------------------|-------------------|
| **Prose Writer** | Generates all natural language content (card text, warrant explanations, mechanism narratives) | Text | **Yes** (extensive) | Opus for theory; Sonnet for routine |
| **Visual Designer** | Generates figure specs, diagram descriptions, visualization configs (SVG, mermaid, D3) | Graphics | **Yes** (new) | Opus for complex DAGs; Sonnet for specs |
| **Stats Communicator** | Translates statistical findings into narrative; flags power gaps, heterogeneity, and boundary conditions | Data narrative | **Yes** (new) | Sonnet (statistical reasoning straightforward) |
| **Layout Composer** | Assembles final card/sheet layouts from prose, visuals, stats; manages progressive disclosure | UX/interaction | **Yes** (new) | Sonnet (layout is deterministic given content) |
| **System Expert** | Persistent knowledge agent; answers queries from other agents; detects conflicts between documents | Knowledge retrieval | **Yes** (via queries) | Opus for synthesis; Sonnet for retrieval |

### Why This Decomposition Works

1. **Clean interfaces**: Each agent reads from previous agent's output directory; all read/write via JSON Schema contracts (Fowler's principle)
2. **Parallel execution**: Prose and visual agents can run in parallel; stats waits for prose; layout composes final result
3. **Modality mastery**: Each agent owns domain expertise in its modality — prose norms, visualization principles, statistical communication, UX patterns
4. **Question-generation convergence**: All agents ask "What's implicit here? What's missing? What would the reader wonder?" — questions cluster in context appendix for system learning
5. **Immutable versioning** (Hickey's principle): Every card version produces new file (`card_v1.json`, `card_v2.json`), preserving history for comparison and learning

---

## § 2. Agent Collaboration Protocol

```
User Query → expert_agent (retrieves relevant context)
                ↓
          prose_agent (generates text from context + cluster data)
                ↓    [questions generated during writing]
          stats_agent (enriches with effect size narratives, power assessment)
                ↓    [questions generated during stats explanation]
          visual_agent (generates figure/table specs)
                ↓    [questions generated during visual planning]
          layout_agent (composes final card/sheet)
                ↓    [questions generated during IA design]
          quality_gate_1: Prose Health (Prose Revision Service)
                ↓
          quality_gate_2: Content Accuracy (Grounded Expert Agent)
                ↓
          quality_gate_3: Reference Verification (post-Opus check)
                ↓
          Output → context_appendix assembled
                ↓
          card_storage + master_question_registry updated
                ↓
          qa_cache / answer_cards / web API
```

**Bidirectional queries** (per Goldhagen feedback): Any agent can query any other during development. A designer might start with a visual concept, then query stats for parameters, then query prose for explanation. The pipeline linearizes for production, but development supports iteration.

---

## § 3. The Science Writer Agent (Prose): Full Specification

The prose writer is the deepest and most fully specified agent, responsible for generating all natural-language content. This section integrates CW's 7-stage pipeline with AG's success conditions.

### 3.1 Role Definition

The Science Writer Agent is responsible for:
- **T1 Framework cards** (Opus): Overview, Mechanism, Design, Debate tabs explaining foundational theories
- **T1.5 Domain Theory cards** (Opus): ReductionClaim DAGs with irreducible residuals
- **T2 Mechanism cards** (Opus prose + Sonnet routine): Concrete mechanism chains with parameterized design space
- **Math cards** (Opus + Sonnet split): Three-tab structure (Intuition/Transparent/Details)
- **Molecule cards** (Sonnet): Component relationships and theory linkages
- **T3 Belief cards** (Sonnet): Evidence summaries and effect size narratives
- **Competition cards** (Opus Debate + Sonnet Evidence): Rival mechanisms and decision-making
- **Question generation** (all cards, Sonnet): Continuous extraction during prose generation

### 3.2 Agent State Management

The agent is stateful and accumulates context across writing sessions.

**Session-scoped state** (`science_writer_state.yaml`):
```yaml
session_id: CLAUDE-SCIENCE-WRITER-{timestamp}
status: ACTIVE | PAUSED | COMPLETED
assigned_tasks:
  - card_id: T1_PREDICTIVE_PROCESSING
    card_type: T1_Framework
    status: IN_PROGRESS | AWAITING_REVISION | COMPLETED
    context:
      source_loci: [T1 registry, backing T2 templates, bridge warrants]
      key_questions_identified: 3
      prose_generation_tokens_used: 8432

pattern_tracking:
  mechanism_types_requiring_extra_scaffolding: [TEMPORAL_DYNAMICS, MODULATION_EFFECTS]
  frequently_unanswered_questions: ["Why is [mechanism] robust to individual differences?", ...]
  prose_patterns_working_well: ["Opening with concrete example", "Three-part mechanism description", ...]
  coverage_gaps_identified: [T2 templates without prose, T1.5 theories incomplete, ...]

model_performance_tracking:
  opus_prose_quality:
    avg_health_score: 7.2
    cards_passed_gate: 18
    common_failures: ["passive voice clusters", "undefined jargon creep"]
  sonnet_prose_quality:
    avg_health_score: 6.8
    cards_passed_gate: 42
    common_failures: ["over-simplification of nuanced mechanisms"]

context_window_consumption:
  cards_generated: 23
  avg_tokens_per_card: 6800
  total_session_tokens: 156,400
```

**Long-term memory** (`master_question_registry.yaml`):

Consolidated across all writing sessions, tracking:
- Questions by category (MECHANISM_CLARITY, BOUNDARY_CONDITIONS, INDIVIDUAL_DIFFERENCES, DESIGN_IMPLEMENTATION, MEASUREMENT_VALIDITY, TEMPORAL_DYNAMICS)
- Recurrence counts (questions raised ≥3 times are flagged)
- Resolution status (UNRESOLVED, PARTIALLY_ADDRESSED, RESOLVABLE_WITH_RESEARCH)
- Suggested research directions

Example entry:
```yaml
Q_INDIV_0156:
  question: "How much variation in [mechanism effect] is explained by personality, cultural background, and prior exposure?"
  first_raised: 2026-02-15 (card: T2_ATTENTION_RESTORATION_01)
  recurrence_count: 18
  raised_by_cards: [ART, BIOPHILIA_01-18, PROSPECT_REFUGE, FRACTAL, ACOUSTIC_01-03, ...]
  resolution_status: SEVERELY_UNDEREXPLORED
  confidence_in_resolution: 0.1
  suggested_research: "Systematic moderator analysis across all CNFA corpus"
```

### 3.3 The Writing Pipeline: 7 Stages

```
REQUEST → [1] INTAKE & CONTEXT ASSEMBLY
          ↓
        [2] MODEL ALLOCATION (Opus or Sonnet)
          ↓
        [3] PROSE GENERATION (theoretical content)
          ↓
        [4] QUESTION EXTRACTION (during writing)
          ↓
        [5] REVISION & QUALITY GATE (Prose Revision Service)
          ↓
        [6] VISUAL GENERATION REQUEST (to Visual Agent)
          ↓
        [7] ICEBERG ASSEMBLY & COMMIT
          ↓
        DELIVERED CARD
```

#### Stage 1: Intake & Context Assembly

**Input**: Card request (type, ID, scope, user types)

**Process** (Sonnet):
1. Query web of belief for primary loci (beliefs most relevant to card)
2. Aggregate backing evidence (T3 beliefs, effect sizes, warrant types)
3. Fetch related cards (parents, siblings, competing accounts)
4. Retrieve annotations (25 types if applicable)
5. Assemble existing prose if regenerating
6. Compile external references (APA bibliography)

**Output**: `CardGenerationContext` dataclass with all source material assembled

**Cost**: ~500 tokens

#### Stage 2: Model Allocation

**Decision tree**:
- T1, T1.5, Math (Intuition+Details), Competition Debate, Layer Justification → **Opus**
- T2 (Overview+Mechanism), Evidence enrichment, Theory synthesis → **Opus first; escalate if health < 6.5**
- T2 (Design+Evidence), T3, Molecule, Math Transparent, Method Implementation → **Sonnet**
- Question extraction, revision gatekeeping → **Sonnet**

#### Stage 3: Prose Generation

**For Opus content**, the prompt embeds:
- Authorial stance: "Write as a guide showing something interesting" (classic style per Pinker)
- Scaffolding requirement: Feynman Staircase (Layer 0 to 4, anchoring each new concept)
- Success conditions (SC-PW-1 through SC-PW-8 from panel feedback)
- Card-type-specific structure (T1 = anchor+core+mechanism+scope+implications+open questions)
- Mandatory visual specifications and mechanism parameterization

**For Sonnet content**, similar structure with lower prose health target (6.5 vs. 6.8).

**Example prompt fragment** (T1 Framework):
```markdown
You are explaining Predictive Processing (a complex neuroscience framework) to
audiences ranging from undergraduates to architects.

## Required Structure
1. Anchor (2 sentences): Connect to reader's experience
2. Core insight (1 para): What is PP? Why matters?
3. Mechanism chain (2 paras): Sensory → prediction → error signal → belief update
4. Scope (1 para): Where in architecture does PP apply?
5. Implications (1 para): How does this change design?
6. Open questions (1 para): What's unsolved?

Target: 750-950 words. Prose health ≥ 6.8.

## During Writing: Extract Questions
As you write, identify assumptions that are NOT explicit:
- Assumption: "PP assumes accurate priors."
  Question: "Where do priors come from? Learned vs. phylogenetic?"
- Gap: Card doesn't address individual differences.
  Question: "Why do some thrive in unpredictable environments while others find them stressful?"

Extract 3-5 substantive questions (not trivial clarifications).
```

**Output**: Prose text (750-2,500 tokens depending on card type) + health score + questions list

#### Stage 4: Question Extraction

**Triggered**: Simultaneously with prose generation

**What gets extracted**: Assumptions, implicit claims, scope conditions, boundary conditions not explicit in prose

**Question quality filter**: Only substantive, resolvable, relevant-to-understanding questions

**Extraction format** (JSON):
```json
{
  "questions_generated": [
    {
      "id": "Q_PP_0847",
      "question": "Why do some individuals exhibit stronger prediction-error responses in chaotic environments while others appear indifferent?",
      "category": "INDIVIDUAL_DIFFERENCES",
      "implicit_claim": "Card assumes all humans share similar prediction-error sensitivity",
      "resolution_status": "UNRESOLVED",
      "resolution_pathway": "Literature review + empirical study",
      "relevance_to_card": "HIGH",
      "relevance_to_system": "HIGH — affects generalizability of design principles",
      "suggested_card_improvement": "Add scope condition: 'These principles apply to neurotypical adults; ADHD, autism, anxiety may differ.'",
      "raises_system_question": true,
      "system_question": "ATLAS lacks systematic review of individual differences moderating all mechanisms"
    }
  ],
  "extraction_metadata": {
    "card_id": "T1_PREDICTIVE_PROCESSING",
    "total_questions_extracted": 4,
    "extraction_depth": "COMPREHENSIVE"
  }
}
```

**Storage**: Immediately added to:
1. `card.iceberg.context_questions` (card-level storage)
2. `/data/master_question_registry.yaml` (system-wide registry)

**Cost**: ~400 tokens (Sonnet, pattern-matching for gaps)

#### Stage 5: Revision & Quality Gate

Three sequential gates (detailed in § 12):

1. **Prose Health Gate** (Prose Revision Service): Health score ≥ 6.5 (Sonnet) or ≥ 6.8 (Opus); no SCIENCE_COMMUNICATION_NORMS violations
2. **Content Accuracy Gate** (Grounded Expert Agent): All empirical claims grounded; effect sizes accurate; mechanisms consistent with literature
3. **Reference Verification Gate** (post-Opus): All citations valid; DOIs exist; context accurate

Failure protocols escalate to higher tier model or human review.

**Cost**: ~600 tokens total (diagnostic + revision)

#### Stage 6: Visual Generation Request

Agent submits requests to Visual Agent:
```python
visual_requests = [
    VisualRequest(
        card_id="T1_PREDICTIVE_PROCESSING",
        visual_type="CIRCUIT_DIAGRAM",
        description="Hierarchical predictive processing with error signals backward",
        tool="mermaid",
        format="svg"
    ),
    # ... more as needed
]
```

Visuals are generated asynchronously; cards can commit with placeholder and update when visual is ready.

#### Stage 7: Iceberg Assembly & Commit

The card's "depth layer" (context appendix) is fully assembled:

```python
@dataclass
class CardIceberg:
    # Provenance
    source_map: SourceMap  # Dependency graph of T3 beliefs, templates, theories
    agent_generation_record: GenerationRecord  # Model, params, timestamp, tokens
    previous_versions: List[CardVersion]  # Before/after diffs

    # Raw data
    backing_beliefs: List[BeliefNode]  # All T3 beliefs cited
    effect_sizes_raw: List[EffectSize]  # Unrounded, with CIs
    warrant_distribution: Dict[WarrantType, int]
    competing_accounts: List[Competition]

    # Context appendix (THE QUESTIONS LAYER)
    context_appendix: ContextAppendix
      - questions: List[ContextQuestion]  # Questions extracted during writing
      - related_questions_in_other_cards: List[str]
      - stated_assumptions: List[str]
      - implicit_claims: List[str]
      - out_of_scope: List[str]
      - improvement_suggestions: List[str]

    # Staleness & updates
    created_at: datetime
    last_regenerated_at: datetime
    staleness_score: float  # [0, 1]; > 0.40 triggers regeneration
    staleness_ledger: List[StalenessEvent]

    # Quality audit
    prose_health_score: float
    reference_verification_status: ReferenceStatus
    expert_panel_review_notes: Optional[str]

    # Reproducibility
    generation_prompt: str  # Full prompt sent to model
    model_parameters: Dict
    random_seed: Optional[int]
```

Card is stored with **triple redundancy**:
1. JSON files in `data/cards/{card_type}/` (version-controlled)
2. SQLite database with indexed lookups (fast retrieval)
3. Prose revision history in `docs/card_history/` (diffs)

---

## § 4. The Visual Designer Agent: Question-Generation Extended

The Visual Designer generates figure specifications, diagram descriptions, visualization configs. New in this unified architecture: **the visual agent also asks questions**.

### Role Definition

- Generates SVG specs (confidence thermometers, evidence constellations, theory maps)
- Generates D3/Vega configs (forest plots, interactive networks)
- Generates Mermaid/DOT specs (mechanism chains, theory maps, DAGs)
- Generates table layouts (narrative tables with data-driven storytelling)
- **NEW**: Extracts design-level questions (visualizations reveal what data is missing)

### Design-Level Question Generation

As the visual agent plans visualizations, it asks:

| Visualization Type | Hidden Questions |
|---|---|
| **Forest plot for effect size** | "Do we have enough studies to show heterogeneity meaningfully? If I = 0.92, is the variation methodological noise or genuine moderators?" |
| **Evidence constellation** (scatter of findings) | "Are there obvious clusters (e.g., all large effects from RCTs, all small from observational)? Does this suggest publication bias?" |
| **Confidence thermometer** | "Is the confidence band so wide that visual representation is misleading? Should we qualify it as 'uncertain' above 0.70?" |
| **Theory map** | "Are we forcing all mechanisms into the same graph when they operate at different scales? Should we separate levels?" |
| **Mechanism chain diagram** | "Do we have evidence for each arrow, or are some inferred? Where's the biggest gap?" |
| **Narrative table** (sorted by effect strength) | "Why is this effect 5x larger than that one? Same mechanism? Different population? Different measurement?" |

**Extraction format** (VISUAL_QUESTIONS):
```json
{
  "visual_questions_generated": [
    {
      "id": "VQ_LIGHT_0234",
      "visual_element": "Forest plot for circadian studies",
      "question": "Do we have enough studies (N>3) in each population subgroup (age, chronotype) to detect moderators, or is sample-size heterogeneity drowning signal?",
      "category": "DATA_SUFFICIENCY",
      "severity": "MEDIUM — affects interpretation confidence",
      "suggested_visual_enhancement": "Add a subgroup analysis table below the forest plot showing N per subgroup",
      "implicit_data_gap": "We lack studies with explicit age × chronotype × dose interactions"
    }
  ]
}
```

These visual questions are stored separately in the context appendix as `context_appendix.visual_design_questions`.

### Success Conditions (from AG panel feedback + visual epistemology)

- **SC-VD-1**: Every visual has a caption explaining what it shows and why it matters
- **SC-VD-2**: Data-ink ratio high; no decorative elements (Tufte principle)
- **SC-VD-3**: Color palettes accessible (WCAG AA) and semantically meaningful
- **SC-VD-4**: Inline sparklines show evidence trends (strengthening/weakening over time)
- **SC-VD-5**: Tables are narrative (structure tells story); not just data grids
- **SC-VD-6**: All visuals are reproducible (mermaid code checked into git, data source documented)

### Terminal Usage

```bash
python3 -m src.agents.visual_agent \
  --input data/cards/batch_prose/cluster_002.json \
  --output-format svg+json \
  --extract-questions true \
  --output data/cards/batch_visuals/
```

---

## § 5. The Stats Communicator Agent: Power and Gap Detection

The Stats Communicator translates statistical findings into reader-friendly narratives while flagging gaps.

### Role Definition

- Translates effect sizes into plain English (d = 0.82 → "70% of treatment group scored above control average")
- Contextualizes confidence intervals with practical decision-making implications
- Explains warrant strength via evidence summaries
- Flags implausible effect sizes (d > 3 suggests measurement/methodological errors)
- **NEW**: Detects power gaps, sample-size heterogeneity, and heterogeneity in mechanisms

### Power Gap Detection

As the stats agent enriches prose with effect size narratives, it asks:

| Statistical Pattern | Question Generated |
|---|---|
| **Small N < 30 across studies** | "Studies are underpowered. How confident are we in effect size estimates? Confidence intervals likely wide." |
| **High heterogeneity (I² > 0.75)** | "Why such different effects across studies? Same mechanism? Different contexts? Methodological differences masking signal?" |
| **Publication bias signals** | "Funnel plot asymmetry suggests positive results over-represented. True effect may be 30-50% smaller than reported." |
| **Subgroup sample sizes unbalanced** | "Only 5 studies test elderly population; 50 test young adults. Generalization to elderly uncertain." |
| **Minimum exposure duration unclear** | "Studies vary from 5-minute interventions to 8-week programs. What's the minimum dose? We don't know." |

**Extraction format** (STATS_QUESTIONS):
```json
{
  "stats_questions_generated": [
    {
      "id": "SQ_LIGHT_0045",
      "statistical_pattern": "Only 2 studies with N > 200; 12 studies with N < 50",
      "question": "Are small-N studies showing inflated effect sizes (regression to mean, selective reporting)? Should we weight by N?",
      "category": "POWER_ASSESSMENT",
      "severity": "HIGH — undermines confidence in mechanism",
      "suggested_improvement": "Perform sensitivity analysis: how does pooled effect change if we exclude N<50 studies?",
      "implicit_evidence_gap": "We need RCT-scale studies (N > 200) in populations of interest"
    }
  ]
}
```

### Success Conditions (from AG + Gelman/Nuzzo panel feedback)

- **SC-SC-1**: Never reports a statistic without contextualizing it
- **SC-SC-2**: Converts p-values to plain-English likelihood statements
- **SC-SC-3**: Flags implausible effect sizes; triggers forensic review if d > 3
- **SC-SC-4**: Explains what would change the conclusion (sensitivity analysis in prose)
- **SC-SC-5**: For ω < 0.5 (weak evidence), caveats come before claims
- **SC-SC-6**: Reports I² heterogeneity alongside pooled effects; explains what it means
- **SC-SC-7**: Identifies populations underrepresented in evidence base (age, culture, pathology)

### Terminal Usage

```bash
python3 -m src.agents.stats_agent \
  --input data/cards/batch_prose/cluster_004.json \
  --output data/cards/batch_stats/ \
  --extract-questions true \
  --power-threshold 0.80
```

---

## § 6. The Layout Composer Agent: Progressive Disclosure with Questions

The Layout Composer assembles final card/sheet layouts from prose, visuals, and stats, while managing progressive disclosure and extracting UX-level questions.

### Role Definition

- Composes card JSON from prose, visuals, stats, metadata
- Decides what goes on first view vs. expandable sections
- Manages L1/L2/L3 progression (150-200 words → 300-400 → 500-700)
- Adapts for user types (researcher, designer, clinician, policymaker, student, developer)
- **NEW**: Extracts layout/IA questions about progressive disclosure effectiveness

### Progressive Disclosure Structure

```
L1 Card (150-200 words)
├─ Always visible: Headline + confidence thermometer
├─ Expandable: Evidence count, mechanism summary (expandable arrow)
└─ Interactive: Hover thermometer; click "show more"

L2 Card (300-400 words)
├─ Always visible: L1 content + mechanism explanation
├─ Expandable: Warrant details, theory map
├─ Interactive: Click theory → card; click effect size → forest plot
└─ Follow-ups: 3 auto-generated deeper questions

L3 Sheet (500-700+ words)
├─ Everything visible (vertical scrolling)
├─ Interactive: Study-level drill-down; related cards
├─ Shareable: Export as PDF section
└─ Cited: Full bibliography, all sources linked
```

### Layout-Level Question Generation

As the layout agent composes information architecture, it asks:

| IA Decision | Hidden Questions |
|---|---|
| **Progressive disclosure levels** | "At what depth does the reader have enough context to make decisions? Is L2 sufficient, or does design require L3?" |
| **User type adaptation** | "Should designer and researcher see the same evidence, or different visualizations? Do they need separate prose?" |
| **Interactivity placement** | "Is the confidence thermometer the most salient element, or should design parameters be first for architects?" |
| **Question placement** | "Should follow-up questions appear at end of card (close reader), or in sidebar (encourage exploration)?" |
| **Expandable sections** | "Which details are 'nice to know' vs. 'essential'? Am I hiding important caveats in expandable sections?" |

**Extraction format** (LAYOUT_QUESTIONS):
```json
{
  "layout_questions_generated": [
    {
      "id": "LQ_LIGHT_0012",
      "layout_decision": "Design parameters in expandable 'Implementation Details' section",
      "question": "Are architects scrolling past implementation details because they're hidden? Should parameters be L2 visible?",
      "category": "DISCOVERABILITY",
      "severity": "MEDIUM — may cause tool non-adoption",
      "suggested_improvement": "A/B test: Card with design parameters L2 visible vs. hidden. Measure engagement.",
      "ux_implication": "If designers don't find what they need on first screen, they leave"
    }
  ]
}
```

### Success Conditions (from AG panel + UX research)

- **SC-LC-1**: No card exceeds word limits for its level
- **SC-LC-2**: Every card has at least one interactive element (even L1)
- **SC-LC-3**: L1 → L2 → L3 progression is genuinely progressive (not just longer text)
- **SC-LC-4**: Mobile-responsive (no horizontal scroll on 375px viewport)
- **SC-LC-5**: For user type adaptations, key content is never hidden (at worst, reordered)
- **SC-LC-6**: Follow-up questions are specific to card content (not generic)

### Terminal Usage

```bash
python3 -m src.agents.layout_agent \
  --prose data/cards/batch_prose/cluster_002.json \
  --visuals data/cards/batch_visuals/cluster_002.json \
  --stats data/cards/batch_stats/cluster_002.json \
  --user-types researcher,designer,student \
  --extract-questions true \
  --output data/cards/final/cluster_002_card.json
```

---

## § 7. The System Expert Agent: Persistent Knowledge with Interrogation

The System Expert is the persistent knowledge agent. Other agents query it; it maintains the system's institutional memory.

### Role Definition

- Knows everything about ATLAS: all docs, molecules, design decisions, past discussions
- Indexes 1,069+ extraction JSONs
- Maintains concept dependency graph (what relates to what)
- Detects conflicts between documents and surfaces them for resolution
- **NEW**: Answers agent queries about context, precedent, and related knowledge

### Background Knowledge (the full dbase)

- `docs/` — master doc, all session docs, all CW review docs
- `data/molecules/` — 38 molecule definitions with components and theory links
- `data/extractions/` — 1,069 extraction JSONs from ingested papers
- `data/materialized_views/` — belief clusters, answer cards, meta-reviews
- `data/discussions/` — exported conversations (user-provided)
- Code architecture map (auto-generated from `src/` scan)

### Persistence: SQLite Index

```sql
CREATE TABLE docs (
    path TEXT PRIMARY KEY,
    title TEXT,
    summary TEXT,
    last_modified TIMESTAMP,
    embedding VECTOR(1536)
);

CREATE TABLE concepts (
    name TEXT PRIMARY KEY,
    type TEXT,  -- "THEORY", "MECHANISM", "DESIGN_PATTERN"
    definition TEXT,
    first_seen_in TEXT,
    related_concepts TEXT[]
);

CREATE TABLE decisions (
    id TEXT PRIMARY KEY,
    description TEXT,
    rationale TEXT,
    date DATE,
    conversation_id TEXT,
    status TEXT  -- "ACTIVE", "SUPERSEDED", "OPEN_FOR_REVIEW"
);

CREATE TABLE dependency_graph (
    source_concept TEXT,
    target_concept TEXT,
    relation_type TEXT,  -- "DEPENDS_ON", "EXPLAINS", "CONTRADICTS"
    evidence TEXT
);
```

### Query Interface (for other agents)

```python
# Prose agent asks: "What do we know about circadian effects on mood?"
context = expert_agent.query("circadian mood", depth="COMPREHENSIVE")

# Visual agent asks: "Show me all competing mechanisms for attention restoration"
competitions = expert_agent.query_competing_accounts("ATTENTION_RESTORATION")

# Stats agent asks: "What population subgroups have we studied in light-response studies?"
subgroups = expert_agent.query("light exposure population subgroups", type="POPULATION_COVERAGE")

# System-level query: "What design decisions have we made about card rendering?"
decisions = expert_agent.query("card rendering decisions", type="DECISIONS")

# Detect conflicts: "Document A says X, Document B says not-X. Resolve."
conflicts = expert_agent.detect_conflicts()
```

### Question-Generation at System Level

As queries are processed, the expert agent asks:

| Query Pattern | System-Level Question |
|---|---|
| **Repeated queries for same topic** | "If 4 agents have queried 'how do we measure legibility', this should be a standard definition, not scattered across docs" |
| **Conflicting information across docs** | "Document A: 'dark patterns reduce stress'; Document B: 'mystery/uncertainty increases curiosity'. When does each apply?" |
| **Concept appears in N docs but no definition** | "What is 'wayfinding'? It's mentioned in 17 cards but defined in only 1. Should we have a canonical Molecule card?" |
| **Decision with unclear rationale** | "We decided 'always use Opus for T1', but is this still valid given new Sonnet capabilities?" |

These system questions go into `master_question_registry.yaml` as `SYSTEM_ARCHITECTURE` category.

### Success Conditions (from AG + architecture expertise)

- **SC-SE-1**: Can answer "what do we know about X?" for any molecule, archetype, or finding theme in < 2 seconds
- **SC-SE-2**: Tracks all design decisions with rationale and source conversation
- **SC-SE-3**: Detects conflicts between documents; surfaces for resolution
- **SC-SE-4**: Suggests connections that no single document makes explicit
- **SC-SE-5**: Maintains semantic consistency (same concept, same name across codebase)

### Terminal Usage

```bash
# "What do we know about circadian effects on mood?"
python3 -m src.agents.expert_agent --query "circadian mood"

# "What design decisions have we made about card rendering?"
python3 -m src.agents.expert_agent --query "card rendering decisions"

# Rebuild index after new papers ingested
python3 -m src.agents.expert_agent --rebuild

# Detect conflicts across docs
python3 -m src.agents.expert_agent --detect-conflicts
```

---

## § 8. The Question-Generation Protocol: Universal Across All Agents

All five agents extract questions during content generation. This unified protocol ensures consistency.

### What Constitutes a Question?

A question is a **gap, assumption, or limitation** that the agent recognizes while working but is NOT resolved in the content being produced.

| Question Type | Example |
|---|---|
| **Scope limitation** | Prose assumes "Western, educated populations." Question: "Does this hold cross-culturally?" |
| **Mechanism gap** | Design says "provide legible layout" but doesn't specify how to measure legibility |
| **Individual difference** | Content treats all humans identically. Question: "Why do some thrive in chaos while others don't?" |
| **Temporal dynamics** | Card describes immediate effects but doesn't address habituation over weeks |
| **Implementation ambiguity** | Design principle stated abstractly. Question: "What does this look like in a real building?" |
| **Competing mechanism** | Two T2 templates explain the same outcome differently. Question: "When does pathway A dominate?" |
| **Data gap** | Statistical analysis shows heterogeneity. Question: "Why are effect sizes 5x different?" |
| **Boundary condition** | Content doesn't state when the mechanism fails |
| **Visual information gap** | Graph shows variation but no explanation. Question: "What's causing this heterogeneity?" |
| **IA gap** | Design parameters not discoverable. Question: "Are users missing critical info?" |

### Question Quality Filter

Only questions that are:
1. **Substantive** — Not trivial ("What does 'lux' mean?") but genuine gaps
2. **Resolvable** — Via evidence search, expert panel, or empirical research
3. **Relevant** — If answered, would improve understanding or usability

**Questions that are NOT extracted**:
- Rhetorical questions (author's attempt to engage reader, not genuine gap)
- Questions answered elsewhere in the same card
- Purely philosophical questions with no empirical hook

### Extraction Depth (Configurable)

```yaml
# Question extraction depth: COMPREHENSIVE, MODERATE, BASIC
COMPREHENSIVE:  # Extract all gaps
  - All scope limitations
  - All mechanism ambiguities
  - All boundary conditions
  - All individual differences
  - All temporal dynamics
  - All measurement challenges

MODERATE:  # Extract major gaps only
  - Scope limitations affecting design
  - Mechanism ambiguities about causality
  - Boundary conditions that matter (not edge cases)

BASIC:  # Extract only critical gaps
  - Scope conditions that invalidate design implications
  - Mechanism contradictions with existing cards
```

### Question Storage and Lifecycle

Every extracted question flows through this lifecycle:

1. **Generated** during content production (Stage 4 in prose pipeline, simultaneous in visual/stats/layout agents)
2. **Stored** in `card.iceberg.context_questions` (card-level storage)
3. **Aggregated** into `master_question_registry.yaml` (system-level tracking)
4. **Analyzed** for patterns (clustering, recurrence, resolution status)
5. **Actioned** as:
   - FAQ card generation (if recurs ≥3 times)
   - Research direction (if points to literature gap)
   - System improvement (if reveals architectural gap)
   - Prose improvement (if suggests card needs better explanation)

### Question Metadata

Every question is tagged with:

```python
@dataclass
class ContextQuestion:
    id: str                            # Q_DOMAIN_NNNN
    question: str                      # Full sentence
    category: QuestionCategory         # SCOPE, MECHANISM, BOUNDARY, etc.

    implicit_claim: str                # What assumption is this questioning?
    raised_during_prose_generation: str  # Which agent, which tab

    resolution_status: ResolutionStatus  # UNRESOLVED, PARTIALLY_ADDRESSED, RESOLVABLE
    resolution_pathway: str            # How to resolve: literature, expert, research
    estimated_resolution_effort: str   # TRIVIAL, MANAGEABLE, MAJOR_PROJECT

    relevance_to_card: str             # LOW, MEDIUM, HIGH
    relevance_to_system: str           # Does this reveal ATLAS gaps?

    suggested_card_improvement: str    # Concrete prose/visual change

    raises_system_question: bool       # True if reveals architectural gap
    system_question: Optional[str]     # The system-level question

    card_id: str                       # Which card raised this
    generation_timestamp: datetime
    answer_if_known: Optional[str]     # If resolved, store answer
```

---

## § 9. The Context Appendix: Iceberg Design for Every Card

Every card has a depth layer that stores implicit knowledge, raw data, and questions.

### Iceberg Structure

The "surface" is prose; the "body" is mechanism explanation; the "iceberg" is everything below:

```
SURFACE: Headline + confidence thermometer
         ↓
BODY: Overview/Mechanism/Design/Evidence prose + visuals
         ↓
ICEBERG: Provenance, raw data, assumptions, questions, improvements
```

### Iceberg Contents

#### Layer 1: Provenance
- Source map: Which T3 beliefs, T2 templates, T1 frameworks contributed?
- Generation record: Opus or Sonnet? When? How many tokens?
- Version history: Previous generations with diffs

#### Layer 2: Raw Data
- All backing beliefs with warrant types and confidence scores
- Effect sizes unrounded with confidence intervals
- Competing accounts and their relative strength
- Design parameters with justification

#### Layer 3: References
- Internal references (which master doc sections)?
- External bibliography (APA, all DOIs verified)

#### Layer 4: Context Appendix (THE QUESTIONS LAYER)
```python
@dataclass
class ContextAppendix:
    # Questions extracted during generation
    questions: List[ContextQuestion]
    related_questions_in_other_cards: List[str]

    # Stated assumptions
    stated_assumptions: List[str]
    # "This card assumes healthy adult humans"
    # "Mechanism tested primarily in Western populations"

    # Implicit claims
    implicit_claims: List[str]
    # "Prediction errors are always aversive" (but see novelty literature)
    # "Design parameters scale linearly" (untested at campus scale)

    # Out of scope
    out_of_scope: List[str]
    # "Individual differences in openness to experience"
    # "Temporal dynamics over months/years"
    # "Non-Western cultural contexts"

    # Improvement suggestions
    improvement_suggestions: List[str]
    # "Add Debate tab covering habituation"
    # "Integrate cross-cultural evidence"

    # Metadata
    created_at: datetime
    last_updated_at: datetime
    generation_model: str  # Opus 4.6, Sonnet 3.5
```

#### Layer 5: Staleness & Metadata
- Created/regenerated timestamps
- Staleness score (0-1); > 0.40 triggers regeneration
- Dated log of backing evidence changes
- Prose health score
- Reference verification status

#### Layer 6: Reproducibility
- Full prompt sent to model
- Model parameters (temperature, top_p, etc.)
- Random seed (if applicable)
- Allows reproduction or variation

### Why This Structure Matters

1. **Transparency**: Users see what assumptions underpin claims
2. **Deepening**: When user asks "Tell me more," system accesses iceberg without re-searching
3. **Improvement**: Questions point to where regeneration should focus
4. **System health**: Clustering questions across cards reveals systematic gaps
5. **Regeneration efficiency**: Iceberg data pre-assembled for next generation

---

## § 10. Model Allocation Strategy: Opus vs. Sonnet Across All Agents

Intelligent model allocation reserves Opus for content requiring judgment and Sonnet for routine work.

### Decision Tree

```
Agent request received.

Prose Writer Agent?
├─ T1 Framework, T1.5 Domain Theory, Math (Intuition+Details) → OPUS (theoretical depth)
├─ T2 Mechanism (Overview+Mechanism), Competition Debate → OPUS first; escalate if prose_health < 6.5
├─ T2 (Design+Evidence), T3, Molecule, Math Transparent, Method Implementation → SONNET
└─ Question extraction, revision gatekeeping → SONNET

Visual Designer Agent?
├─ Complex DAG/ReductionClaim (→ Theory Agent Council queries) → OPUS (synthesis)
├─ Specification generation, table layout → SONNET

Stats Communicator Agent?
├─ Power assessment, heterogeneity explanation → SONNET (statistical reasoning straightforward)

Layout Composer Agent?
├─ Progressive disclosure decisions → SONNET (deterministic given content)

System Expert Agent?
├─ Synthesis queries (conflicting docs, concept connections) → OPUS
└─ Simple retrieval queries → SONNET
```

### Cost Estimation for Full System

**T1 Framework cards (10 cards, Opus-heavy)**:
- Context assembly: 500 tokens (Sonnet)
- Overview + Mechanism + Design prose: 5,000 tokens (Opus, 2k+1.5k+1.5k)
- Question extraction: 400 tokens (Sonnet)
- Prose revision: 300 tokens (Sonnet)
- **Per card**: ~5,000 Opus + 1,200 Sonnet = 6,200 tokens
- **Total**: 50,000 Opus + 12,000 Sonnet

**T2 Mechanism cards (166 cards, Sonnet-heavy)**:
- Context + prose (Sonnet first): 2,000 tokens
- If escalation (health < 6.5): +2,000 Opus (assume 20% escalation = 33 cards)
- Question extraction: 300 tokens (Sonnet)
- Revision: 300 tokens (Sonnet)
- **Per card (best case)**: 2,600 Sonnet
- **Per card (escalated)**: 2,300 Sonnet + 2,000 Opus
- **Total**: ~764,000 Sonnet + 66,000 Opus

**Math Cards (30 cards, mixed)**:
- Intuition + Details: 2,700 tokens (Opus)
- Transparent tab: 800 tokens (Sonnet)
- Extraction + revision: 600 tokens (Sonnet)
- **Per card**: 2,700 Opus + 1,400 Sonnet
- **Total**: 81,000 Opus + 42,000 Sonnet

**Competition Cards (estimated 5-10)**:
- Debate tab: 1,500 Opus
- Evidence tab: 800 Sonnet
- **Total**: 15,000 Opus + 8,000 Sonnet

**Overall Budget**:
- **Opus**: 50k + 66k + 81k + 15k = ~**212,000 tokens**
- **Sonnet**: 12k + 764k + 42k + 8k = ~**826,000 tokens**
- **Total**: ~1,038,000 tokens

This is achievable in **2-3 intensive sessions** at standard Claude API usage.

---

## § 11. Card-Type-Specific Generation Strategies

Each of the 9 card types has distinct generation strategies reflecting its epistemic role.

### 11.1 T1 Framework Cards (10 cards, Opus-only)

**Generation challenge**: Explain complex neurobiology to audiences from undergraduates to neuroscientists without losing rigor.

**Key strategy**: Feynman Staircase (Layer 0-4)
- **Layer 0 (Anchor)**: Experience the reader knows ("You startle when light in familiar room is different")
- **Layer 1 (Core)**: One new idea ("Your brain constantly predicts; wrong predictions get noticed")
- **Layer 2 (Example)**: Concrete instance ("Legible buildings feel calm; illogical buildings feel taxing")
- **Layer 3 (Neural)**: How the brain implements this ("Predictions stored in cortical layers; errors signal mismatch")
- **Layer 4 (Formalism)**: Mathematical description ("Hierarchical Bayesian inference: P(state | data) ∝ P(data | state) × P(state)")

**Success targets**:
- Prose health: ≥ 6.8
- Questions extracted: 5-8 (deep questions about individual differences, temporal dynamics, boundary conditions)
- External references: 8-12
- Mechanism chain: fully explained (not just listed)

### 11.2 T2 Mechanism Cards (166 cards, mixed Opus+Sonnet)

**Generation challenge**: Make abstract template concrete while preserving mechanism precision.

**Key strategy**: Parameterization
- Every mechanism chain includes: stimulus (lux, duration, spectrum), sensor, signal pathway, integration, output
- Every design tab includes: 5-8 design parameters with ranges, evidence justification, real-building achievability

**Model allocation**:
- **Overview + Mechanism**: Opus first (health ≥ 6.5 required); if lower, auto-revise or escalate
- **Evidence + Design**: Sonnet (data aggregation, tables, parameter ranges)

**Success targets**:
- Mechanism chain: Fully parameterized (d values, lux thresholds, timing windows all specified)
- Design tab: 5-8 parameters with practical implementation guidance
- Questions: 5-7, focused on boundary conditions and individual differences
- Visuals: Mechanism chain diagram + forest plot + parameter table

### 11.3 T1.5 Domain Theory Cards (5-10 cards, Opus)

**Generation challenge**: Reduce domain theory to constituent T1 frameworks while honoring irreducible residuals.

**Key strategy**: ReductionClaim DAG with footnoted gaps
- Query Theory Agent Council: "What T1 frameworks constitute this T1.5?"
- Document coverage fractions (e.g., "ART is 40% PP + 25% Spatial Nav + 20% DMN + 15% irreducible")
- Footnote irreducible residual (what's not explained by reduction?)

**Success targets**:
- DAG shows all dependencies with coverage percentages
- Mechanism tab explains what's irreducible and why
- Questions: 6-10 (focused on reduction validity and missing pieces)

### 11.4 Math Cards (25-30 cards, Opus+Sonnet split)

**Three-tab structure** (per David's spec addendum):

**Tab 1: Intuition** (Opus, 400-500 words, ZERO equations)
- Analogies, concrete examples, visual metaphors
- "What does this math do and why does it matter?"
- Mandatory visual: conceptual diagram

**Tab 2: Transparent Explanation** (Sonnet, 300-400 words)
- Full equation with color-coded terms
- Each symbol defined explicitly
- Each term justified ("Why is this term here?")
- Derivation sketch
- Mandatory visual: annotated equation

**Tab 3: Details** (Opus, 500-700 words)
- Full formal specification, proofs, sensitivity analyses, boundary conditions
- Computational complexity analysis
- Epistemological grounding (Toulmin, Pollock, etc.)
- Mandatory visual: sensitivity chart or worked example

**Success targets**:
- Intuition: Comprehensible to intelligent non-specialist
- Transparent: All symbols defined; no undefined variables
- Details: Sufficient for reimplementation; computational properties clear

### 11.5 Molecule Cards (38 cards, Sonnet)

**Generation challenge**: Concisely define abstract concept while showing relationships.

**Key strategy**: Component interaction
- Structure: Definition → Key components → Interaction with other molecules → Design implications
- Visual: Component interaction diagram (what molecules feed into this? what does it feed?)

**Success targets**:
- Health score ≥ 6.5
- Definition is short but precise (1-2 sentences)
- Design implications are actionable (not abstract)

### 11.6 T3 Belief Cards (on-demand, Sonnet)

**Generation challenge**: Summarize single empirical finding in context of broader convergence.

**Key strategy**: Contextualization
- Lead with effect size and what it means
- Explain warrant type (why trust this study?)
- Show where it fits in larger picture

**Success targets**:
- Health score ≥ 6.5
- Effect size contextualized (d = 0.5 means __)
- Caveats stated (sample size, population, measurement)

### 11.7 Competition Cards (5-10 cards, Opus Debate + Sonnet Evidence)

**Generation challenge**: Present rival mechanisms fairly while being honest about relative evidence.

**Key strategy**: Toulmin argumentation
- Data: The empirical finding
- Warrants: Why this evidence supports mechanism A vs. B
- Backing: Citations and mechanism coherence
- Rebuttals: When does each mechanism fail?
- Qualifier: How confident are we in the comparison?

**Success targets**:
- No straw-manning of rival accounts
- Relative evidence is quantified (A has 60% backing, B has 40%)
- Boundary conditions clearly stated (when does A dominate?)

### 11.8 Layer & Method Cards (estimated 3-5 cards, Opus Justification + Sonnet Implementation)

**Generation challenge**: Explain architectural layer or methodological choice with both philosophy and practice.

**Key strategy**: Dual pathway
- Justification tab (Opus): Why does this layer/method matter? Epistemological grounding
- Implementation tab (Sonnet): How is it actually done? Code, workflows, tools

**Success targets**:
- Justification: Clear philosophical/epistemic motivation
- Implementation: Step-by-step reproducibility

---

## § 12. Quality Gates: Three-Tier System with Escalation

Every card must pass three sequential gates before commitment.

### Gate 1: Prose Health (Prose Revision Service)

**Triggered**: After prose generation (Stages 2a/2b)

**Checks**:
- Health score ≥ 6.5 (Sonnet) or ≥ 6.8 (Opus)
- No violations of SCIENCE_COMMUNICATION_NORMS (Norms 1-12: Given-New, stress position, zombie nouns, jargon clarity, confidence calibration, etc.)
- Given-New contract: sentences begin with familiar info
- Stress position: important content at sentence end
- Zombie noun count < 15%
- Hedge stack < 3 per 500 words
- Passive voice < 20%
- Undefined jargon: all technical terms defined on first use

**Failure protocol**:
```
Health score 6.0–6.4 (Sonnet) or 6.5–6.7 (Opus)?
  → Auto-revise (Sonnet regenerates with feedback) → re-check
  → If health now ≥ 6.5, PASS

Health score < 6.0 (Sonnet) or < 6.5 (Opus)?
  → Escalate to higher-tier model (Sonnet → Opus)
  → Opus regenerates → re-check
  → If still failing → Escalate to David (halt, wait for human review)
```

**Cost**: ~300 tokens

### Gate 2: Content Accuracy (Grounded Expert Agent)

**Triggered**: After Gate 1 passes

**Checks**:
- All empirical claims grounded in backing evidence (T3 beliefs, web of belief)
- Effect sizes and confidence intervals accurately reported (not misquoted)
- Mechanism descriptions consistent with neurobiological literature
- Scope conditions correctly stated
- Citations are valid (DOI exists, claim is actually in that paper)
- No contradictions with existing cards or master doc

**For Opus-generated content only**:
- Reference verification (next gate)
- Mechanism plausibility (does mechanism chain cohere with T2 backing?)

**Failure protocol**:
```
Minor errors (typo in citation, slight effect size rounding)?
  → Auto-correct + flag for review

Major errors (mechanism contradiction, unsupported claim)?
  → Escalate to David (halt card; need manual review)

Missing evidence for core claim?
  → Escalate to Grounded Expert Agent for clarification
```

**Cost**: ~200 tokens

### Gate 3: Reference Verification (Post-Opus Quality Check)

**Triggered**: After Gate 2 passes, AND card was generated by Opus

**Checks**:
- Every cited paper has valid DOI or is in ATLAS corpus
- Citation context is accurate (did we quote correctly? Is the claim actually in that paper?)
- No citation orphans (references without APA formatting)
- Bibliography complete and consistent

**Implementation** (Sonnet):
```python
def verify_opus_references(card: Card) -> ReferenceVerificationReport:
    """For each citation in card.body_prose:
    1. Extract DOI and author/year
    2. Query ATLAS corpus to confirm paper is known
    3. Check APA formatting
    4. Flag mismatches
    """
```

**Failure protocol**:
```
> 20% of citations fail verification?
  → Escalate to David; halt commitment

< 5% fail?
  → Sonnet generates corrected bibliography → re-submit

5–20% fail?
  → Flag for David's review; allow commitment with warning label
```

**Cost**: ~150 tokens

### Escalation Summary

```
Request → [Gate 1: Prose Health]
             ↓ FAIL → [Auto-revise] → re-check → [Still fail] → [Escalate to Opus] → re-check
             ↓ PASS
          [Gate 2: Content Accuracy]
             ↓ FAIL → [Minor: auto-correct] OR [Major: escalate to David]
             ↓ PASS
          [Gate 3: Reference Verification]*
             ↓ FAIL → [<5%: Sonnet fixes] OR [5-20%: flag for David] OR [>20%: halt]
             ↓ PASS
          [COMMIT & STORE]

* Only for Opus-generated cards
```

---

## § 13. Development Mode vs. Production Mode

During development, "the agent IS the conversation." Once stable, agents codify into API scripts.

### Development Mode

**How it works**:
- You (human) read the agent spec (e.g., prose_agent spec, visual_agent spec)
- You read cluster data and context
- You generate content (as the agent)
- You write output to JSON files
- Other agents read those outputs

**Advantage**: Full control, can iterate, understand implicit decisions

**Example**:
```bash
# CW reads prose_agent spec + cluster data
# CW generates prose for T1_PREDICTIVE_PROCESSING
# CW writes to data/cards/batch_prose/T1_PREDICTIVE_PROCESSING.json
# Visual agent reads that file and generates visuals

# Stats agent reads prose + cluster data and adds statistical narratives
# Layout agent reads all three and composes final card
```

### Production Mode

**How it works**:
- Prompts are codified into Python scripts
- Scripts call Claude API directly
- Input/output contracts (JSON Schema) are frozen
- Cards are generated automatically on schedule or trigger

**Migration path** (Fowler's principle):
1. **Freeze the interface** — Define final JSON Schema for agent inputs/outputs
2. **Codify the prompts** — Extract best prompts from development sessions into Python
3. **Add orchestration** — Script that calls agents in sequence
4. **Test compatibility** — Verify API-driven agents produce equivalent output to human agents
5. **Deploy** — Run on schedule; alert on failures

**Zero changes required downstream** because interfaces are identical.

---

## § 14. Staleness Detection and Regeneration

Cards become stale when backing evidence changes, and stale cards trigger automatic regeneration.

### Staleness Score Calculation

```
staleness_score = (
    0.3 * evidence_freshness_decay +
    0.3 * design_parameter_validity +
    0.2 * mechanism_confidence_drift +
    0.1 * question_resolution_rate +
    0.1 * user_feedback_signal
)

Where:
- evidence_freshness_decay: # of months old / max_age_before_clearly_stale (24 months)
- design_parameter_validity: "Has backing evidence for design params changed?"
- mechanism_confidence_drift: "Has credence in mechanism shifted?"
- question_resolution_rate: "How many context questions were resolved?"
- user_feedback_signal: "Are users rating this card lower over time?"

Triggers regeneration if > 0.40
```

### Regeneration Workflow

**When triggered** (manually by David, or automatically on schedule):
1. Fetch card + iceberg
2. Check which parts are stale (evidence, design params, confidence)
3. Regenerate stale sections (not full card rewrite)
4. Run through all three quality gates
5. If improvements detected, commit new version (`card_v2.json`)
6. Store before/after diff in `docs/card_history/`
7. Update `master_question_registry` with resolved questions

**Efficiency**: Iceberg pre-assembled; regeneration is 30-50% faster than initial generation

---

## § 15. Integration with Existing ATLAS Services

The 5-agent system consumes outputs from and feeds inputs to 10 existing services.

### Service Dependency Map

**GENERATION INPUTS** (what agents read):
- Web of Belief (backing beliefs, warrant network)
- Bayesian Network (causal structure, confidence scores)
- Annotation Layer (25 enrichment types)
- Theory Agent Council (panel consensus on mechanisms)
- Argumentation System (competitions, Toulmin structures)
- Answer Enrichment Orchestrator (domain expertise)
- Bridge Warrants (causal links, credence formula)
- Method Registry (measurement validity profiles)
- Master Doc (theoretical background, examples)

**QUALITY GATES** (what agents consult):
- Prose Revision Service (health scoring, diagnostic)
- Grounded Expert Agent (evidence grounding)
- AI Panel Resolver (controversy detection, resolution)

**GENERATION OUTPUTS** (what agents produce):
- Card Storage (JSON + SQLite)
- Question Registry (master_question_registry.yaml)
- Figure Generation Requests (to Visual Agent)
- Master Doc Update Signals (to Master Doc Update Agent)
- QA System Input (discovered Q&A pairs for FAQ cards)

### Specific Integration Points

#### Web of Belief Queries

```python
# Prose agent: "What's the evidence for T2_LIGHT_01?"
backing_beliefs = web_of_belief.query(
    template_id="T2_LIGHT_01",
    warrant_types=["MECHANISM", "EMPIRICAL_ASSOCIATION"],
    include_effect_sizes=True,
    include_scope_conditions=True
)
# Returns: List[BeliefNode] with full metadata
```

#### Annotation Layer Integration

For complex mechanisms, annotations enrich prose:
- MEASUREMENT_CHALLENGE: method limitations (cortisol 15-20 min latency)
- BOUNDARY_CONDITION: when mechanism fails
- INDIVIDUAL_DIFFERENCE: population modifiers
- CONFOUND_STRUCTURE: unmeasured variables
- VR_SPECIFIC_THREAT: what was lost in VR studies

Agent integrates these as explicit scope conditions in Design tab.

#### Theory Agent Council Queries

When generating T1.5 cards:
```python
reduction = theory_council.query_reduction(
    t1_5_theory="ATTENTION_RESTORATION_THEORY",
    decompose_into=["PREDICTIVE_PROCESSING", "SPATIAL_NAVIGATION", "DMN_TPN_DYNAMICS"],
    question="What is the irreducible residual not explained by these T1?"
)
# Returns: ReductionClaim with coverage fractions, uncertainty bounds, disputed territories
```

#### Argumentation System Queries

When generating Competition or Debate tabs:
```python
competitions = argumentation_system.query_competing_accounts(
    claim="Natural daylight improves mood",
    include_toulmin_structures=True,
    include_argument_maps=True,
    include_panel_deliberations=True
)
# Returns: List[Competition] with pro/con/rebuttal structure
```

#### Card Storage & Indexing

Cards stored with **triple redundancy**:
1. **JSON files** in `data/cards/{card_type}/` (version-controlled, human-readable)
2. **SQLite database** with indexed lookups (fast retrieval for QA system)
3. **Prose revision history** in `docs/card_history/` (before/after diffs)

#### Visual Generation Requests

```python
visual_requests = [
    VisualRequest(
        card_id="T1_PREDICTIVE_PROCESSING",
        visual_type="CIRCUIT_DIAGRAM",
        description="Hierarchical predictive processing with error signals backward",
        tool="mermaid",
        format="svg"
    ),
]
# Visual Agent asynchronously generates; stores in docs/figures/cards/
```

#### Master Doc Update Signals

```python
master_doc_updates = [
    MasterDocUpdate(
        card_id="T1_PREDICTIVE_PROCESSING",
        affected_sections=["§XX: Predictive Processing Framework"],
        update_type="CONTENT_REFRESH",  # or EXPANSION, GAP_FILL
        suggested_changes={
            "section_to_update": "§XX.2: Neural Implementation",
            "new_prose": "[insert committed Overview + Mechanism from card]",
            "rationale": "Card prose more current and comprehensive"
        }
    )
]
# David reviews suggestions; decides which to accept
```

#### QA System Integration

Cards populate QA system through multiple pathways:
1. **Direct FAQ**: Question matches card topic exactly → return card
2. **Cross-card synthesis**: Multiple cards address question → synthesize answer
3. **Context appendix lookup**: Question in context_appendix.questions → acknowledge gap, offer related answers

---

## § 16. Success Conditions: Comprehensive List

### Prose Quality (Prose Writer Agent)

- [ ] All committed card prose achieves health score ≥ 6.5 (Sonnet) or ≥ 6.8 (Opus)
- [ ] 95% of Opus-generated cards pass reference verification gate on first attempt
- [ ] User satisfaction scores (5-point scale) average ≥ 4.0
- [ ] Zero instances of false citations or misattributed claims
- [ ] Every L2+ card includes actionable design implication (SC-PW-7)
- [ ] No card presents single study as conclusive; all contextualize within convergence zone (SC-PW-8)
- [ ] Every card includes at least one experiential anchor — connection to felt experience (per Ellard)

### Content Quality (All Agents)

- [ ] Every card's mechanism chain fully parameterized (lux, spectrum, duration, timing specified with justification)
- [ ] Every card includes 5-8 substantive questions in context_appendix
- [ ] Design tabs include concrete implementation ranges (not vague guidance)
- [ ] 90% of scope conditions explicitly stated in prose
- [ ] Confidence language matches evidence strength (hedge for ω < 0.6, assert for ω > 0.85)
- [ ] All claims traceable to specific findings in corpus

### Visual Quality (Visual Designer Agent)

- [ ] Every visual has caption explaining what it shows and why it matters (SC-VD-1)
- [ ] No decorative visual elements; every element encodes data (SC-VD-5)
- [ ] Color palettes accessible (WCAG AA) and semantically meaningful (SC-VD-3)
- [ ] Inline sparklines show evidence trends (SC-VD-5, Tufte feedback)
- [ ] Narrative tables tell story (not just data grids; SC-VD-2, Lupi feedback)

### Stats Communication Quality (Stats Communicator Agent)

- [ ] Never reports statistic without contextualizing it (SC-SC-1)
- [ ] p-values converted to plain-English likelihood statements (SC-SC-2)
- [ ] Implausible effect sizes flagged and trigger forensic review (d > 3) (SC-SC-3)
- [ ] For ω < 0.5, caveats come before claims (SC-SC-5)
- [ ] I² heterogeneity reported alongside pooled effects (SC-SC-6)
- [ ] Power gaps and population underrepresentation identified

### Layout Quality (Layout Composer Agent)

- [ ] No card exceeds word limits for its level (SC-LC-1)
- [ ] Every card has at least one interactive element (SC-LC-2)
- [ ] L1 → L2 → L3 progression genuinely progressive (SC-LC-3)
- [ ] Mobile-responsive (no horizontal scroll on 375px viewport) (SC-LC-4)
- [ ] For user type adaptations, key content never hidden (at worst, reordered) (SC-LC-5)
- [ ] Follow-up questions specific to card content (not generic) (SC-LC-6)

### Question Generation (All Agents)

- [ ] Master question registry accumulates 50+ questions per card generation cycle
- [ ] Questions categorized and enable clustering analysis
- [ ] Top 20 recurrent questions become candidates for FAQ cards
- [ ] Questions pointing to research gaps distinct from prose-improvement questions
- [ ] Prose questions, visual questions, stats questions, layout questions stored separately in context_appendix

### System Expert Agent

- [ ] Can answer "what do we know about X?" for any molecule/archetype in < 2 seconds (SC-SE-1)
- [ ] Tracks all design decisions with rationale and source (SC-SE-2)
- [ ] Detects conflicts between documents and surfaces for resolution (SC-SE-3)
- [ ] Suggests connections not explicit in single documents (SC-SE-4)
- [ ] Maintains semantic consistency across codebase (SC-SE-5)

### Integration

- [ ] Cards feed directly into QA system (routable questions answered by card lookup)
- [ ] Master doc update signals reach David; ≥50% accepted and integrated
- [ ] Visual requests fulfilled within 24 hours
- [ ] Agent state versioned in git; session history auditable
- [ ] Three-gate quality system catches 80% of issues before human review

### Efficiency

- [ ] Average card generation time: < 15 minutes (context + prose + gates)
- [ ] Opus allocated to ~30% of workload (matching theory/routine split)
- [ ] Prose revision gate catches 80% of issues before human review
- [ ] Staleness detection triggers regeneration without manual intervention

---

## § 17. Open Questions for David

Before full implementation, these require decision:

1. **Prose Regeneration Cadence**: Fixed schedule (quarterly)? Threshold-based (staleness > 0.40)? Manual request only?

2. **Question Registry Workflow**: When questions accumulate, how should David handle them? Monthly review? Auto-create FAQ cards for top recurrent questions?

3. **Visual Generation Sync**: Synchronous (block card commitment until visual ready) or asynchronous (commit prose, update with visual later)?

4. **Master Doc Synchronization**: When card prose changes significantly, auto-update master doc or David reviews changes first?

5. **Scope of "All Possible Questions"**: Does ATLAS promise to answer (a) all routable questions in interpretation space? (b) all reasonable user questions (unbounded)? (c) top 500 FAQ questions (curated)?

6. **Personalization Storage**: For user type adaptations (researcher vs. designer prose), store separate versions or regenerate on-the-fly?

7. **Opus vs. Sonnet Comparison**: Should we run test on 3-5 T1 cards with AG's Opus before full rollout to confirm equivalence?

8. **Individual Differences Priority**: The master question registry shows individual-differences questions as severely underexplored. Should we commission a systematic meta-analysis?

9. **Design Operationalization**: Multiple questions point to "How do you actually implement [theory] in real buildings?" Should we create a linked methodology guide or case studies?

10. **Question Registry Transparency**: Should the master question registry be exposed to users (showing what ATLAS doesn't yet know) or kept internal?

---

## § 18. Panel Review Record and Incorporated Feedback

This section documents the expert panel's feedback and how it was incorporated.

### Panel (15 experts from two specs)

**Science Writers**: Ed Yong (Atlantic), Carl Zimmer (NYT), Maria Popova (Marginalian)
**Visualization**: Edward Tufte, Giorgia Lupi, Mike Bostock (D3.js)
**Stats**: Andrew Gelman, Sander Greenland, Regina Nuzzo
**Domain**: Colin Ellard (environmental neuroscience), Sarah Williams Goldhagen (architecture-neuroscience), Jan Gehl (human-scale design)
**Architecture**: Martin Fowler (software patterns), Rich Hickey (data-oriented design)
**Moderator**: David Kirsh (foundherentist epistemology)

### Feedback Incorporated (from AG spec §16-20)

**Ed Yong** ("Answer 'so what?'"):
- **Feedback**: Prose must include actionable design implication, not just evidence summary
- **Incorporated**: SC-PW-7 added — Every L2+ card includes actionable design implication

**Edward Tufte** ("Every pixel encodes data"):
- **Feedback**: No decorative elements; inline sparklines for evidence trends
- **Incorporated**: SC-VD-5 added; visual agent required to show trend lines

**Andrew Gelman** ("Flag heterogeneity"):
- **Feedback**: Implausible effect sizes need forensic review; I² must accompany pooled effects
- **Incorporated**: SC-SC-3 and SC-SC-6 added; stats agent flags power gaps

**Colin Ellard** ("Experiential anchoring"):
- **Feedback**: Connect findings to felt experience ("that moment when...")
- **Incorporated**: Prose prompts include mandatory experiential anchor

**Sarah Williams Goldhagen** ("Iterative design process"):
- **Feedback**: Agents need bidirectional queries, not just sequential pipeline
- **Incorporated**: Bidirectional queries enabled in development mode; production pipeline remains sequential

**Rich Hickey** ("Immutability"):
- **Feedback**: Every card generation produces new versioned file
- **Incorporated**: card_v1.json, card_v2.json system with diffs stored

**Martin Fowler** ("Contract-first"):
- **Feedback**: Define JSON Schema contracts so API migration requires zero downstream changes
- **Incorporated**: All agent I/O via JSON Schema; development → production migration path documented

**Regina Nuzzo** ("Lead with uncertainty"):
- **Feedback**: For weak evidence (ω < 0.5), caveats come before claims
- **Incorporated**: SC-SC-5 added; stats agent prioritizes caveats

**Giorgia Lupi** ("Tables as visualization"):
- **Feedback**: Tables are a first-class visualization, not afterthought
- **Incorporated**: Visual agent treats narrative tables as core output type

**David Kirsh** ("Foundherentist framing"):
- **Feedback**: No single study presented as conclusive; always contextualize within web
- **Incorporated**: SC-PW-8 added; all cards show convergence zone context

### Feedback from CW Spec (Integration)

The CW specification itself represents deep feedback on prose quality, question-generation, and model allocation. Key insights incorporated:

- **Question-generation loop** (CW core): Extended from prose to all agents
- **Stateful agent** (CW emphasis): Agent maintains session state + master question registry
- **Model allocation strategy** (CW): Opus for theory; Sonnet for routine
- **Context appendix** (CW design): Full iceberg layer capturing assumptions, questions, improvements
- **Three quality gates** (CW): Prose health, content accuracy, reference verification
- **Card-type-specific strategies** (CW): T1 Feynman Staircase, T2 parameterization, Math three-tab structure
- **Integration with 10 ATLAS services** (CW): Detailed service dependency map

---

## Conclusion

The unified CONTENT_AGENT_ARCHITECTURE synthesizes AG's clean 5-agent decomposition with CW's deep epistemic and question-generation insights. The result is a system that:

**Produces publication-quality content** through selective Opus allocation to theoretical work and systematic quality gates.

**Systematically surfaces implicit knowledge** via question extraction in every agent, question clustering in master registry, and transparency via context appendices.

**Maintains institutional memory** through stateful agents, long-term question registries, versioned card history, and design decision tracking.

**Integrates with existing ATLAS services** cleanly via JSON Schema contracts, enabling development-mode human orchestration and production-mode API automation.

**Adapts across user types** (researcher, designer, clinician, policymaker, student, developer) without losing content integrity.

**Enables continuous improvement** through staleness detection, regeneration workflows, user feedback integration, and question-driven research gap identification.

This specification is complete and ready for implementation. The next phase is engineering: building prompt infrastructure, state management, quality gate implementations, service integrations, and automated orchestration scripts.

---

## References

Carson, R. (1962). *Silent Spring*. Houghton Mifflin.

Doumont, J.-L. (2009). *Trees, maps, and theorems: Effective communication for rational minds*. Principiae.

Fowler, M. (2002). *Patterns of enterprise application architecture*. Addison-Wesley.

Gelman, A. (2013). *Bayesian data analysis* (3rd ed.). Chapman & Hall/CRC.

Hickey, R. (2013). "The value of values." JVM Language Summit keynote.

Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Penguin Press.

Pollock, J. L. (1995). *Cognitive carpentry: A defense of modular theory of mind*. MIT Press.

Quine, W. V. O. (1960). *Word and object*. MIT Press.

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

Tufte, E. R. (1983). *The visual display of quantitative information*. Graphics Press.

Yong, E. (2016). *I contain multitudes: The microbes within us and a grander view of life*. Ecco.
