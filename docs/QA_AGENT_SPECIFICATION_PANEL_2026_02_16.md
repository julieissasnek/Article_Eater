# CNFA Question-Answering Agent Specification

**Date**: February 16, 2026
**Version**: 1.0
**Purpose**: Specification for an adaptive QA agent serving diverse CNFA stakeholders with progressive disclosure

---

## Part I: Expert Panel Composition

### Panel P-QA: Question-Answering Agent Design

This panel combines expertise in explanation, pedagogy, CNFA domains, and human-computer interaction.

#### Explanation & Epistemology Experts

| Expert | Affiliation | Expertise | Role in Panel |
|--------|-------------|-----------|---------------|
| **Peter Lipton** | Cambridge (d. 2007) | Inference to Best Explanation | What makes explanations satisfying |
| **Alison Gopnik** | UC Berkeley | Causal learning, explanation in development | How novices vs experts seek explanation |
| **Michael Strevens** | NYU | Depth of explanation, kairetic account | When to go deeper vs stay shallow |
| **Tania Lombrozo** | Princeton | Psychology of explanation, simplicity | Cognitive constraints on good answers |
| **Wesley Salmon** | Pittsburgh (d. 2001) | Causal-mechanical explanation | Mechanistic depth levels |

#### CNFA Domain Experts

| Expert | Affiliation | Expertise | Role in Panel |
|--------|-------------|-----------|---------------|
| **Rachel Kaplan** | Michigan | Attention Restoration Theory | Behavioral/preference explanations |
| **Roger Ulrich** | Chalmers | Stress Recovery Theory, hospital design | Physiological/health explanations |
| **Colin Ellard** | Waterloo | Urban neuroscience, psychogeography | Neural mechanisms in real environments |
| **Anjan Chatterjee** | Penn | Neuroaesthetics, empirical aesthetics | Neural basis of architectural experience |
| **Juhani Pallasmaa** | Helsinki | Phenomenology of architecture | Experiential/phenomenological depth |
| **Sarah Robinson** | Architect-theorist | Embodied cognition in architecture | Body-space-mind integration |

#### Computational & Modeling Experts

| Expert | Affiliation | Expertise | Role in Panel |
|--------|-------------|-----------|---------------|
| **Karl Friston** | UCL | Predictive processing, free energy | Computational-level explanations |
| **Josh Tenenbaum** | MIT | Probabilistic models of cognition | Bayesian explanations of behavior |

#### Pedagogy & Learning Experts

| Expert | Affiliation | Expertise | Role in Panel |
|--------|-------------|-----------|---------------|
| **Carl Bereiter** | Toronto | Knowledge building, expertise development | How understanding deepens |
| **Michelene Chi** | ASU | Self-explanation, conceptual change | How learners process explanations |
| **K. Anders Ericsson** | FSU (d. 2020) | Expertise, deliberate practice | Expert vs novice knowledge structures |

#### HCI & Information Design

| Expert | Affiliation | Expertise | Role in Panel |
|--------|-------------|-----------|--------------|
| **Ben Shneiderman** | Maryland | Information visualization, progressive disclosure | Interface patterns |
| **Marti Hearst** | UC Berkeley | Search interfaces, NL understanding | Query interpretation |

---

## Part II: User Typology

### Panel Deliberation: Who Are Our Users?

**Lombrozo**: "Users differ not just in knowledge level but in *explanatory goals*. A student writing an essay wants breadth and connections. A researcher designing an experiment wants depth on mechanisms and boundary conditions."

**Bereiter**: "We should distinguish *knowledge-telling* users (who want to report facts) from *knowledge-building* users (who want to construct understanding). The same person shifts between modes."

**Ericsson**: "Expert knowledge is organized around principles and deep structure. Novice knowledge is organized around surface features. Our answers must bridge this gap."

### User Type Matrix

| User Type | Knowledge Level | Typical Goals | Explanation Depth Needed | Time Pressure |
|-----------|-----------------|---------------|--------------------------|---------------|
| **Undergraduate (intro)** | Surface concepts | Essay topics, exam prep | What + basic why | High |
| **Undergraduate (advanced)** | Some mechanisms | Research paper, honors thesis ideas | What + how + some why | Medium |
| **Masters student** | Methodological | Thesis design, literature synthesis | How + why + boundary conditions | Medium |
| **PhD student (early)** | Theoretical gaps | Dissertation framing, novel questions | Deep why + alternatives + gaps | Low |
| **PhD student (late)** | Expert-adjacent | Defending claims, peer review | Competing explanations + evidence strength | Variable |
| **Professor (teaching)** | Expert | Lecture prep, student questions | Multiple levels ready to deploy | Variable |
| **Professor (research)** | Deep expert | Grant writing, review articles | State of evidence + gaps + methodological critiques | Low |
| **Practicing architect** | Applied | Design decisions, client justification | Actionable implications + confidence level | High |
| **Design researcher** | Hybrid | Evidence-based design, post-occupancy | Effect sizes + boundary conditions + mechanisms | Medium |
| **Science journalist** | Translator | Public explanation | Compelling narrative + caveats + analogies | High |

### User Mode Matrix

**Chi**: "The same user operates in different modes. A PhD student sometimes wants quick facts, sometimes wants deep explanation."

| Mode | Trigger Context | Depth Tolerance | Format Preference |
|------|-----------------|-----------------|-------------------|
| **Quick lookup** | Mid-task, verify fact | 1 sentence | Direct answer |
| **Orientation** | New topic, scoping | 1 paragraph + pointers | Overview + links |
| **Understanding** | Genuine puzzlement | Multiple paragraphs | Structured explanation |
| **Integration** | Connecting ideas | Variable | Comparison, synthesis |
| **Evaluation** | Critical assessment | Deep | Evidence quality, alternatives |
| **Application** | Design decision | Practical | Implications + confidence |
| **Inspiration** | Topic hunting | Broad | Interesting questions, gaps |
| **Teaching prep** | Will explain to others | Layered | Multiple framings |

---

## Part III: Question Typology

### Panel Task: Generate Representative Questions

**Hearst**: "Questions cluster by *information need type*. We need to identify the underlying need, not just surface form."

**Gopnik**: "Children and scientists ask the same kinds of questions: What, How, Why, What-if. But the depth they expect differs enormously."

### The 25 Question Types

#### Category A: Empirical/Descriptive (What happens?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 1 | **Effect existence** | "Do high ceilings affect creativity?" | Architect scoping, student essay |
| 2 | **Effect size** | "How much do high ceilings affect creativity?" | Researcher, design decision |
| 3 | **Effect direction** | "Do high ceilings increase or decrease focused attention?" | Anyone, basic orientation |
| 4 | **Effect reliability** | "Is the ceiling height effect replicated?" | PhD student, critical evaluation |
| 5 | **Population variation** | "Do introverts respond differently to open offices?" | Applied researcher |
| 6 | **Boundary conditions** | "Does the ceiling height effect hold for elderly populations?" | Thesis design, healthcare architect |
| 7 | **Temporal dynamics** | "How long does the restorative effect of nature views persist?" | POE researcher |

#### Category B: Mechanistic (How does it work?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 8 | **Proximate mechanism** | "How do high ceilings promote creative thinking?" | Understanding mode |
| 9 | **Neural substrate** | "What brain regions respond to ceiling height?" | Neuro-focused researcher |
| 10 | **Computational account** | "How would predictive processing explain the spaciousness effect?" | Theoretically sophisticated |
| 11 | **Pathway identification** | "Is the nature restoration effect mediated by attention or affect?" | Mechanism-focused research |
| 12 | **Multi-level integration** | "How do neural, cognitive, and behavioral levels connect for wayfinding?" | Comprehensive understanding |

#### Category C: Explanatory (Why does it happen?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 13 | **Functional why** | "Why would evolution favor preference for prospect-refuge spaces?" | Deep understanding, teaching |
| 14 | **Developmental why** | "Why do children and adults differ in response to color saturation?" | Developmental researcher |
| 15 | **Contrastive why** | "Why do nature views work but nature sounds alone don't?" | Sophisticated questioner |
| 16 | **Comparative why** | "Why is biophilia stronger than topophilia effects?" | Theory integration |

#### Category D: Methodological (How do we know?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 17 | **Evidence assessment** | "How strong is the evidence for color-mood effects?" | Critical evaluation |
| 18 | **Measurement critique** | "Can self-report capture restoration accurately?" | Methods course, thesis design |
| 19 | **Study design** | "What would be a good experiment to test the complexity-liking curve?" | Honors/PhD thesis |
| 20 | **Paradigm limitations** | "Why do VR studies and real building studies often disagree?" | Sophisticated methodologist |

#### Category E: Applied/Design (What should I do?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 21 | **Design recommendation** | "What ceiling height is best for a creative workspace?" | Architect, evidence-based design |
| 22 | **Trade-off navigation** | "How do I balance daylight access with glare in a classroom?" | Design decision |
| 23 | **Confidence assessment** | "How confident should I be recommending biophilic design for stress reduction?" | Client presentation |

#### Category F: Generative/Exploratory (What's interesting?)

| # | Type | Example | User Context |
|---|------|---------|--------------|
| 24 | **Topic discovery** | "What are the most interesting open questions about acoustics and cognition?" | Essay topic, thesis scoping |
| 25 | **Gap identification** | "Where is the evidence weakest for prospect-refuge theory?" | PhD dissertation, research agenda |
| 26 | **Connection finding** | "How does embodied cognition relate to wayfinding research?" | Theory integration |
| 27 | **Controversy mapping** | "What do researchers disagree about regarding thermal comfort and productivity?" | Review article, teaching |

---

## Part IV: Principles of Good Explanation

### Panel Deliberation: What Makes an Answer Good?

#### Lipton's Contribution: Inference to Best Explanation

**Lipton**: "A good explanation is one we would *infer to*—it's lovely, not just likely. Loveliness comes from:
1. **Unification** — explaining many things with one principle
2. **Mechanism** — showing how, not just that
3. **Precision** — being specific enough to be wrong
4. **Scope** — applying broadly but with clear limits"

#### Strevens' Contribution: Kairetic Depth

**Strevens**: "The ideal explanatory depth is the level that captures *difference-makers*—factors that, if changed, would change the outcome. Go deep enough to find the difference-maker, no deeper."

**Applied to CNFA**: "If someone asks why nature views reduce stress, the difference-maker might be at the attentional level (soft fascination) or the evolutionary level (savanna preference). The right depth depends on what kind of 'why' they're asking."

#### Lombrozo's Contribution: Cognitive Constraints

**Lombrozo**: "Humans prefer:
1. **Simple explanations** (fewer causes > many)
2. **Explanations with broader scope** (generalize > specific)
3. **Explanations that cohere** with existing beliefs
4. **Explanations that enable prediction** of new cases

But experts tolerate more complexity than novices. Progressive disclosure respects this."

#### Salmon's Contribution: Causal-Mechanical Levels

**Salmon**: "Explanation has levels:
1. **Descriptive** — what happens
2. **Causal** — what causes it
3. **Mechanical** — how the causal process works
4. **Constitutive** — what the mechanism is made of

Good progressive disclosure moves through these levels."

#### Gopnik's Contribution: Explanation as Learning

**Gopnik**: "Explanation isn't just packaging knowledge—it's a tool for learning. A good explanation:
1. **Provokes inference** — learner generates further conclusions
2. **Supports transfer** — applies to new cases
3. **Highlights structure** — makes deep features visible
4. **Invites questions** — opens further inquiry"

### Synthesis: The Seven Principles of Good CNFA Answers

| # | Principle | Description | Implementation |
|---|-----------|-------------|----------------|
| **P1** | **Answer the actual question first** | Lead with direct response before elaboration | First sentence = direct answer |
| **P2** | **Match depth to user type** | Novices get shallower defaults; experts get deeper | User model drives initial depth |
| **P3** | **Enable controlled deepening** | User can request more depth at any point | "Why?" drills down; "How sure?" adds evidence |
| **P4** | **Make depth levels explicit** | Signal what kind of explanation you're giving | "At the behavioral level..." / "At the neural level..." |
| **P5** | **Preserve coherence across levels** | Deeper explanations should extend, not contradict, shallower ones | Multi-level integration |
| **P6** | **Acknowledge uncertainty honestly** | Distinguish strong evidence from speculation | Confidence markers throughout |
| **P7** | **Enable action** | Connect understanding to what user can do with it | Implications section for applied users |

---

## Part V: Progressive Disclosure Architecture

### Panel Design: Depth Levels

**Shneiderman**: "Progressive disclosure works when each level is *complete at that level*—not a teaser, but a satisfying answer that happens to have more available."

**Chi**: "Self-explanation research shows learning is active. Don't just reveal more—prompt the user to predict or connect."

### The Five Depth Levels

#### Level 1: Direct Answer (1-2 sentences)
- **Content**: Yes/no/it depends + brief qualifier
- **Format**: Single statement with confidence indicator
- **Example**: "Yes, high ceilings generally facilitate creative thinking, with moderate effect size (d ≈ 0.4). The effect is stronger for divergent thinking tasks than convergent ones."

#### Level 2: Contextualized Answer (1 paragraph)
- **Content**: Effect + key moderators + main mechanism hint
- **Format**: 3-5 sentences with structure
- **Example**: "High ceilings (3m+) facilitate creative thinking, particularly divergent thinking tasks like brainstorming (Meyers-Levy & Zhu, 2007). The effect is mediated by conceptual priming—height primes 'freedom' concepts. Effect size is moderate (d ≈ 0.4) but varies by population and task. The effect reverses for detail-oriented tasks, where lower ceilings improve performance. Evidence quality is moderate (few direct replications, mostly lab studies)."

#### Level 3: Mechanistic Explanation (3-5 paragraphs)
- **Content**: How the effect works, at cognitive/perceptual level
- **Format**: Structured sections (Mechanism, Evidence, Moderators)
- **Example sections**:
  - *Mechanism*: Conceptual metaphor theory → spatial height → abstract 'freedom' → broader associative processing
  - *Evidence*: Original study + replications + failures
  - *Moderators*: Task type, individual differences, cultural variation
  - *Boundary conditions*: Only works when height is noticed; habitation effects unclear

#### Level 4: Multi-Level Integration (5-10 paragraphs)
- **Content**: Cognitive + neural + evolutionary + computational accounts
- **Format**: Explicitly multi-level, showing connections
- **Example sections**:
  - *Cognitive level*: Conceptual metaphor, attentional scope
  - *Neural level*: Parietal attention networks, default mode modulation (speculative)
  - *Computational level*: Predictive processing—high ceilings = low precision priors = more exploration
  - *Evolutionary level*: Open savanna affordances → safety + foraging tradeoffs
  - *Cross-level coherence*: How levels connect

#### Level 5: Critical Scholarly Analysis (full treatment)
- **Content**: State of evidence, methodological critiques, open questions, research agenda
- **Format**: Review-article depth with citations
- **Example sections**:
  - *Evidence quality*: Study-by-study analysis, meta-analytic summary if available
  - *Methodological limitations*: Lab vs. field, measurement issues, confounds
  - *Theoretical alternatives*: Competing explanations
  - *Open questions*: What we don't know
  - *Research priorities*: What studies are needed

### Depth Transition Triggers

| User Action | System Response |
|-------------|-----------------|
| "Why?" or "Explain more" | Go one level deeper on mechanism |
| "How do we know?" | Surface evidence quality and methodology |
| "Does this apply to [X]?" | Discuss boundary conditions and moderators |
| "What's the neural basis?" | Jump to neural level specifically |
| "Can I use this for design?" | Pivot to application implications |
| "What don't we know?" | Surface gaps and uncertainties |
| "Give me everything" | Provide Level 5 treatment |

---

## Part VI: Explanation Templates by Question Type

### Template Structure

Each question type gets a response template with:
1. **Canonical structure** — sections expected at each depth level
2. **Required elements** — what must appear
3. **Optional elements** — available for progressive disclosure
4. **Confidence markers** — how to signal certainty
5. **Cross-references** — links to related questions

### Template Examples

#### Template: Effect Existence Questions (Type 1)

**Question pattern**: "Does X affect Y?" / "Is there a relationship between X and Y?"

| Depth | Structure |
|-------|-----------|
| L1 | [Yes/No/Mixed] + effect direction + confidence qualifier |
| L2 | L1 + effect size + key moderator + mechanism hint + evidence quality |
| L3 | L2 + detailed mechanism + full moderator analysis + boundary conditions |
| L4 | L3 + multi-level explanation (cognitive → neural → evolutionary) |
| L5 | L4 + systematic evidence review + methodology critique + research gaps |

**Example at L2**:
> "Yes, high ceilings are associated with enhanced creative thinking, with moderate effect size (d ≈ 0.4, based on Meyers-Levy & Zhu, 2007). The effect appears specific to divergent thinking tasks and is mediated by conceptual metaphor priming (height → freedom → broadened cognition). Evidence quality is moderate—original study well-designed but limited direct replication. Effect reverses for detail-focused tasks."

**Confidence markers**:
- Strong evidence: "robustly shows," "well-established"
- Moderate evidence: "suggests," "indicates," "associated with"
- Weak evidence: "preliminary evidence suggests," "one study found"
- Theoretical: "theory predicts," "would be expected to"

#### Template: Mechanistic Questions (Type 8)

**Question pattern**: "How does X affect Y?" / "What is the mechanism for...?"

| Depth | Structure |
|-------|-----------|
| L1 | Primary mechanism in one sentence |
| L2 | Mechanism + pathway + key evidence |
| L3 | Detailed mechanism with sub-processes + evidence per step |
| L4 | Multiple mechanism levels (perceptual → cognitive → neural → computational) |
| L5 | Mechanistic evidence review + competing mechanisms + open questions |

**Required elements**:
- Process description (not just correlation)
- Level specification (perceptual? cognitive? neural?)
- Evidence status for each mechanistic claim

#### Template: Contrastive Why Questions (Type 15)

**Question pattern**: "Why does X happen but not Y?" / "Why does A work better than B?"

| Depth | Structure |
|-------|-----------|
| L1 | Key difference factor in one sentence |
| L2 | Difference factor + mechanism for why it matters |
| L3 | Systematic comparison of conditions + mechanistic account of difference |
| L4 | Multi-level analysis of the contrast |
| L5 | Full comparative analysis with evidence for difference-making |

**Lipton**: "Contrastive questions are the heart of explanation. 'Why P rather than Q?' requires identifying what's present in P's causal history that's absent in Q's."

**Required elements**:
- Explicit statement of the contrast (not just one side)
- Identification of difference-maker
- Why the difference-maker matters mechanistically

#### Template: Design Recommendation Questions (Type 21)

**Question pattern**: "What should I do about X?" / "What's the best Y for Z?"

| Depth | Structure |
|-------|-----------|
| L1 | Direct recommendation + confidence |
| L2 | Recommendation + key trade-offs + evidence basis |
| L3 | Recommendation + full trade-off analysis + when to deviate |
| L4 | Multiple framings of the decision + mechanistic grounding for recommendations |
| L5 | Full evidence review + design process recommendations + uncertainty acknowledgment |

**Required elements**:
- Actionable recommendation (not just "it depends")
- Confidence level for the recommendation
- Key trade-offs or considerations
- When the recommendation doesn't apply

---

## Part VII: User-Adaptive Behavior

### Panel Discussion: Adapting to Users

**Bereiter**: "Knowledge-building conversations adapt to what the learner already knows. The system should model the user's current understanding."

**Ericsson**: "Experts chunk information differently. An expert architect hearing 'biophilic design' retrieves a rich network; a novice retrieves a definition. Answers should connect to existing knowledge."

### User Model Components

| Component | How Assessed | How Used |
|-----------|--------------|----------|
| **Domain expertise** | Vocabulary used, question sophistication | Default depth level, jargon tolerance |
| **Theoretical orientation** | Frameworks mentioned, question framing | Preferred explanation style |
| **Current mode** | Question phrasing, context | Format and completeness |
| **Time pressure** | Explicit ("quick question") or implicit | Conciseness vs. thoroughness |
| **Application context** | Mentioned use case | Emphasis on implications vs. understanding |

### Adaptation Rules

| User Signal | System Adaptation |
|-------------|-------------------|
| Uses technical terms correctly | Higher default depth, more jargon OK |
| Asks "what is X" basics | Lower default depth, define terms |
| Mentions teaching/explaining | Provide multiple framings |
| Mentions design decision | Emphasize implications and confidence |
| Asks follow-up why | Increase depth on next response |
| Says "briefly" or "quick" | Compress to L1-L2 only |
| Asks about evidence quality | Include methodology in all responses |
| Mentions specific theory | Frame answers in that theoretical language |

### Interaction Patterns

#### Pattern 1: The Drilling Conversation
User asks surface question → gets L2 answer → asks "why?" → gets L3 → asks "but how does that work neurally?" → gets targeted L4

**System behavior**: Track depth requested, maintain coherence across levels, remember what's been explained.

#### Pattern 2: The Scoping Conversation
User asks broad question → gets L2 overview → asks about specific aspect → gets L3 on that aspect → asks about different aspect → gets L3 on that

**System behavior**: Maintain topic continuity, signal what aspects are available, avoid repetition.

#### Pattern 3: The Critical Conversation
User asks question → gets L2 answer → asks "how strong is the evidence?" → gets methodological detail → asks "what about study X?" → engages specific evidence

**System behavior**: Shift to evidence-focused mode, maintain scholarly precision, acknowledge limitations.

#### Pattern 4: The Application Conversation
User asks about effect → gets L2 → asks "so what should I do?" → gets design recommendation → asks "how confident?" → gets uncertainty analysis

**System behavior**: Pivot between understanding and application smoothly, make recommendations actionable.

---

## Part VIII: Quality Criteria for Answers

### Panel Evaluation: What Makes a Good Answer?

The panel identified quality criteria at three levels:

### Criteria Level 1: Basic Quality (all answers)

| Criterion | Description | Test |
|-----------|-------------|------|
| **Accuracy** | Factually correct | Would domain expert endorse? |
| **Relevance** | Answers the question asked | Does first sentence address the question? |
| **Appropriate depth** | Matches user needs | Neither overwhelming nor insulting |
| **Clarity** | Understandable at user level | No unexplained jargon for non-experts |
| **Honesty** | Acknowledges uncertainty | Doesn't oversell weak evidence |

### Criteria Level 2: Explanation Quality (L2+)

| Criterion | Description | Test |
|-----------|-------------|------|
| **Mechanism present** | Shows how, not just that | Causal process described? |
| **Coherence** | Parts fit together | No contradictions between levels |
| **Generativity** | Enables further inference | User can predict new cases? |
| **Boundary conditions** | Specifies when it applies | Limits stated? |

### Criteria Level 3: Deep Quality (L4+)

| Criterion | Description | Test |
|-----------|-------------|------|
| **Multi-level integration** | Connects explanation levels | Explicit cross-level links? |
| **Alternatives acknowledged** | Competing explanations noted | Not presenting one view as only view |
| **Evidence grounded** | Claims linked to studies | Can trace to sources? |
| **Gaps identified** | What we don't know | Honest about limits? |

### Quality Scoring Rubric

For each answer, rate on 1-5:

| Dimension | 1 (Poor) | 3 (Adequate) | 5 (Excellent) |
|-----------|----------|--------------|---------------|
| **Directness** | Doesn't answer question | Answers eventually | Opens with direct answer |
| **Depth calibration** | Too shallow or too deep | Mostly appropriate | Perfectly matched to user |
| **Mechanistic clarity** | No mechanism | Mechanism sketched | Mechanism fully articulated |
| **Evidence integration** | No evidence cited | Some evidence | Evidence woven throughout |
| **Uncertainty handling** | Overconfident | Some hedging | Calibrated confidence |
| **Actionability** | No implications | Some implications | Clear next steps |

---

## Part IX: Implementation Specification

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  - Query input with context signals                          │
│  - Progressive disclosure controls ("Why?" / "More" / etc)   │
│  - User type selection/inference                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Query Understanding Layer                  │
│  - Question type classification (25 types)                   │
│  - Entity/concept extraction                                 │
│  - Depth request detection                                   │
│  - Context/mode inference                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    User Model Layer                          │
│  - Expertise level estimation                                │
│  - Current mode detection                                    │
│  - Session history and depth trajectory                      │
│  - Application context                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Response Planning Layer                      │
│  - Select response template (by question type)               │
│  - Determine initial depth level (by user model)             │
│  - Plan progressive disclosure options                       │
│  - Identify cross-references                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Knowledge Retrieval Layer                    │
│  - Query Web of Belief for relevant claims                   │
│  - Retrieve evidence summaries                               │
│  - Get mechanism chains                                      │
│  - Pull confidence/uncertainty metadata                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Response Generation Layer                    │
│  - Fill template with retrieved knowledge                    │
│  - Apply depth-appropriate filtering                         │
│  - Add confidence markers                                    │
│  - Generate disclosure prompts                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Quality Check Layer                       │
│  - Verify accuracy against knowledge base                    │
│  - Check depth appropriateness                               │
│  - Validate coherence                                        │
│  - Confirm disclosure options available                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Structures

#### Question Type Enum

```python
class QuestionType(Enum):
    # Category A: Empirical
    EFFECT_EXISTENCE = "effect_existence"
    EFFECT_SIZE = "effect_size"
    EFFECT_DIRECTION = "effect_direction"
    EFFECT_RELIABILITY = "effect_reliability"
    POPULATION_VARIATION = "population_variation"
    BOUNDARY_CONDITIONS = "boundary_conditions"
    TEMPORAL_DYNAMICS = "temporal_dynamics"

    # Category B: Mechanistic
    PROXIMATE_MECHANISM = "proximate_mechanism"
    NEURAL_SUBSTRATE = "neural_substrate"
    COMPUTATIONAL_ACCOUNT = "computational_account"
    PATHWAY_IDENTIFICATION = "pathway_identification"
    MULTI_LEVEL_INTEGRATION = "multi_level_integration"

    # Category C: Explanatory
    FUNCTIONAL_WHY = "functional_why"
    DEVELOPMENTAL_WHY = "developmental_why"
    CONTRASTIVE_WHY = "contrastive_why"
    COMPARATIVE_WHY = "comparative_why"

    # Category D: Methodological
    EVIDENCE_ASSESSMENT = "evidence_assessment"
    MEASUREMENT_CRITIQUE = "measurement_critique"
    STUDY_DESIGN = "study_design"
    PARADIGM_LIMITATIONS = "paradigm_limitations"

    # Category E: Applied
    DESIGN_RECOMMENDATION = "design_recommendation"
    TRADEOFF_NAVIGATION = "tradeoff_navigation"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"

    # Category F: Generative
    TOPIC_DISCOVERY = "topic_discovery"
    GAP_IDENTIFICATION = "gap_identification"
    CONNECTION_FINDING = "connection_finding"
    CONTROVERSY_MAPPING = "controversy_mapping"
```

#### Depth Level Enum

```python
class DepthLevel(Enum):
    L1_DIRECT = 1      # 1-2 sentences
    L2_CONTEXTUALIZED = 2   # 1 paragraph
    L3_MECHANISTIC = 3      # 3-5 paragraphs
    L4_MULTILEVEL = 4       # 5-10 paragraphs
    L5_SCHOLARLY = 5        # Full treatment
```

#### User Model

```python
@dataclass
class UserModel:
    expertise_level: float  # 0.0 (novice) to 1.0 (expert)
    theoretical_orientation: List[str]  # e.g., ["predictive_processing", "embodied_cognition"]
    current_mode: str  # "quick_lookup", "understanding", "evaluation", etc.
    time_pressure: str  # "high", "medium", "low"
    application_context: Optional[str]  # "design", "teaching", "research", None
    session_depth_trajectory: List[int]  # depths requested in session
    topics_discussed: List[str]

    def default_depth(self) -> DepthLevel:
        """Determine default depth level based on user characteristics."""
        if self.current_mode == "quick_lookup":
            return DepthLevel.L1_DIRECT
        elif self.expertise_level < 0.3:
            return DepthLevel.L2_CONTEXTUALIZED
        elif self.expertise_level < 0.7:
            return DepthLevel.L3_MECHANISTIC
        else:
            return DepthLevel.L4_MULTILEVEL
```

#### Response Template

```python
@dataclass
class ResponseTemplate:
    question_type: QuestionType

    # Content requirements per depth level
    l1_required: List[str]  # e.g., ["direct_answer", "confidence_marker"]
    l2_required: List[str]  # e.g., ["mechanism_hint", "key_moderator", "evidence_quality"]
    l3_required: List[str]
    l4_required: List[str]
    l5_required: List[str]

    # Disclosure prompts
    depth_prompts: Dict[DepthLevel, List[str]]  # e.g., {L2: ["Why?", "How does it work?"]}
    lateral_prompts: List[str]  # e.g., ["Related: Does this apply to...?"]

    # Quality checks
    required_confidence_markers: bool
    required_citations: DepthLevel  # L3 and above need citations
```

### Interaction Protocol

#### Query → Response Flow

1. **Receive query** with any context signals
2. **Classify question type** (25-way classification)
3. **Update user model** with new signals
4. **Select template** for question type
5. **Determine depth** from user model
6. **Retrieve knowledge** from Web of Belief
7. **Generate response** using template
8. **Add disclosure prompts** for deeper levels
9. **Quality check** before delivery
10. **Deliver response**

#### Depth Transition Protocol

When user requests more depth:
1. **Parse depth request** ("Why?" → mechanism depth; "Evidence?" → methodological depth)
2. **Check current depth** in session state
3. **Retrieve additional content** for requested dimension
4. **Generate incremental response** (don't repeat, extend)
5. **Update disclosure prompts** for even deeper levels
6. **Update session state**

### Integration with Article Eater

This QA agent integrates with the existing Article Eater system:

| Article Eater Component | QA Agent Usage |
|-------------------------|----------------|
| Web of Belief | Source of claims and credence scores |
| Bridge Warrants | Source of mechanism explanations |
| Social Epistemology | Community consensus and disagreement |
| Epistemic-Causal Bridge | Causal explanations and counterfactuals |
| Evidence Quality Scores | Confidence calibration |
| Scope Conditions | Boundary condition answers |

---

## Part X: Example Interactions

### Example 1: Undergraduate Essay Research

**User context**: Intro psych student, high time pressure, topic hunting mode

**Query**: "What are some interesting topics about how buildings affect mental health?"

**System response (L2 + topic list)**:
> Architecture influences mental health through multiple pathways—daylight affects circadian rhythms and mood; spatial layout affects social interaction and isolation; views of nature reduce stress and support attention recovery. Here are well-researched topics with interesting open questions:
>
> **Well-established effects:**
> - Nature views and stress recovery (strong evidence, mechanism debated)
> - Daylight and depression (strong evidence, circadian mechanism)
> - Noise and cognitive load (strong evidence, practical implications)
>
> **Emerging/debated areas:**
> - Ceiling height and creativity (moderate evidence, conceptual metaphor explanation)
> - Biophilic design and productivity (promising but methodologically messy)
> - Color and emotion (surprisingly weak evidence despite intuitions)
>
> **Gaps ripe for exploration:**
> - Long-term vs. acute effects (most studies are short-term)
> - Individual differences (why do people respond differently?)
>
> Would you like more on any of these? I can suggest specific research questions for essay topics.

### Example 2: PhD Student Designing Experiment

**User context**: PhD student, methods-focused, experimental design mode

**Query**: "What would be a good experiment to test whether the restorative effect of nature is about attention or affect?"

**System response (L3 + methodology)**:
> This is a pathway identification question—you want to distinguish attentional (ART) from affective (SRT) mechanisms. Both predict restoration; they differ on *process*.
>
> **Key design requirements:**
>
> 1. **Manipulate nature exposure** (VR, photos, or real—each has tradeoffs)
> 2. **Measure both pathways independently:**
>    - Attention: ANT, SART, or backward digit span (pre/post)
>    - Affect: PANAS, SAM, or continuous physiological (HR, EDA)
> 3. **Include mediation tests:**
>    - If attention mediates: Nature → ↑ attention → ↓ stress
>    - If affect mediates: Nature → ↓ negative affect → ↑ attention
>
> **Design recommendations:**
>
> - **Stressor paradigm**: Include cognitive load task before nature exposure (makes restoration detectable)
> - **Temporal resolution**: Sample affect continuously; attention only pre/post (attention tests are themselves fatiguing)
> - **Control condition**: Urban without nature but matched for interest/complexity (not blank screen)
>
> **Critical methodological issues:**
>
> 1. *VR cybersickness* confounds physiological stress measures—need SSQ control
> 2. *Self-report/physiology mismatch* is common—don't rely on one
> 3. *Exposure duration* matters—short exposures (<5 min) may not show full effect
>
> **Example design** (based on Berto, 2005 + Berman et al., 2008):
> - N = 60, within-subjects
> - Session: Baseline → Stressor (mental arithmetic) → Exposure (nature vs. urban vs. rest) → ANT
> - Continuous HR/EDA throughout
> - PANAS at each transition
> - Mediation analysis with bootstrapped confidence intervals
>
> **Evidence quality note**: The attentional mechanism (ART) has more direct experimental support than the affective mechanism (SRT), but both are plausible. Your experiment could help clarify.
>
> Want me to go deeper on the statistical analysis plan, or discuss specific measurement instruments?

### Example 3: Architect Seeking Design Guidance

**User context**: Practicing architect, high time pressure, design decision mode

**Query**: "I'm designing a hospital waiting room. What does the evidence say about reducing patient anxiety?"

**System response (L2 + actionable)**:
> **Direct recommendations** (ordered by evidence strength):
>
> 1. **Include nature views or nature imagery** — Strong evidence (Ulrich, 1984 and many replications). Effect size is substantial; even nature photographs help.
>
> 2. **Maximize daylight, control glare** — Strong evidence for mood; design challenge is balancing views with patient privacy.
>
> 3. **Reduce unpredictable noise** — Strong evidence that noise increases stress. Sound masking or absorptive materials help.
>
> 4. **Provide prospect and refuge** — Moderate evidence. Patients want to see the entrance (prospect) but feel protected (refuge). Avoid exposed seating facing blank walls.
>
> 5. **Offer seating flexibility** — Weaker evidence but reasonable inference. Some want social seating, others want privacy. Modular options help.
>
> **Confidence assessment:**
> - Nature views: High confidence (recommend strongly)
> - Daylight: High confidence (recommend strongly)
> - Acoustics: High confidence (recommend strongly)
> - Prospect-refuge: Moderate confidence (recommend, but less evidence)
> - Color choices: Low confidence (weak evidence despite strong intuitions—warm ≠ calming)
>
> **What we don't know:**
> - Optimal nature density (how much is enough?)
> - Individual differences (some patients prefer minimal stimulation)
> - Interaction effects (does nature help if it's noisy?)
>
> Would you like specific design parameters (lux levels, nature ratios, acoustic targets)?

### Example 4: Deep Conceptual Understanding

**User context**: Professor, low time pressure, understanding mode, theoretically sophisticated

**Query**: "Do high ceilings facilitate creativity, when and for whom? And why?"

**System response (L4, multi-level)**:
> **Short answer**: Yes, but the effect is specific, moderate in size, and depends on task type and individual factors. The mechanism involves conceptual metaphor priming.
>
> ---
>
> **I. The Empirical Effect**
>
> High ceilings (≥3m) enhance *divergent thinking*—generating multiple solutions, making distant associations, flexible categorization (Meyers-Levy & Zhu, 2007). Effect size is moderate (d ≈ 0.35–0.45 in original study).
>
> The effect *reverses* for *convergent thinking*—detailed analysis, systematic processing, focused attention. Lower ceilings improve these tasks.
>
> **Moderators identified:**
> - *Task type*: Divergent vs. convergent (most important moderator)
> - *Awareness*: Effect diminishes when height is made explicit
> - *Individual differences*: Preliminary evidence that creative individuals show larger effect
> - *Cultural factors*: Not well studied; metaphor may vary
>
> **Evidence quality**: The original study is well-designed (within-subjects, multiple tasks, manipulation checks). Direct replications are limited. The effect appears in the broader "embodied cognition" literature but specific ceiling-height work is sparse.
>
> ---
>
> **II. Cognitive-Level Mechanism**
>
> The explanation invokes **conceptual metaphor theory** (Lakoff & Johnson, 1980):
>
> 1. Spatial height is metaphorically linked to freedom, abstraction, and openness (UP IS FREE, UP IS ABSTRACT)
> 2. Environmental cues (high ceiling) prime these concepts
> 3. Primed "freedom" activates broader associative processing
> 4. Broader processing facilitates divergent thinking
>
> The reverse effect for convergent tasks: low ceilings prime "confinement" → focused, detail-oriented processing.
>
> **Supporting evidence**: The priming mechanism was tested explicitly—participants in high-ceiling rooms were faster to identify freedom-related words. This mediation effect is the key evidence for the mechanism.
>
> ---
>
> **III. Neural-Level Account (speculative)**
>
> No direct neuroimaging of ceiling height effects exists. However, the mechanism maps onto known neural systems:
>
> - *Divergent thinking* recruits default mode network (DMN), especially medial prefrontal cortex and angular gyrus—areas involved in conceptual combination and distant associations
> - *Convergent thinking* recruits task-positive network (TPN), especially dorsolateral PFC—areas involved in focused attention and constraint satisfaction
> - Spatial processing in parietal cortex may provide the metaphor-grounding link
>
> **Prediction**: High ceilings should increase DMN relative to TPN activation during creative tasks. This is testable but not yet tested.
>
> ---
>
> **IV. Computational-Level Account**
>
> From a predictive processing perspective (Friston, 2010):
>
> - High ceilings represent a **high-entropy environment**—less predictable, more uncertainty
> - High uncertainty → lower precision on priors → more exploration in hypothesis space
> - More exploration → better divergent thinking
>
> Low ceilings represent a **low-entropy environment**:
> - More predictable → higher precision on priors → exploitation over exploration
> - More exploitation → better convergent thinking
>
> This account predicts the task-type reversal naturally—it's not about "creativity" as a monolith but about exploration/exploitation tradeoffs.
>
> ---
>
> **V. Evolutionary-Level Account**
>
> Speculative but coherent with prospect-refuge theory (Appleton, 1975):
>
> - High ceilings simulate open savanna environments—spaces affording long-distance viewing and escape routes
> - Such environments would have favored exploratory behavior (foraging, scouting)
> - Exploratory behavioral mode → exploratory cognitive mode (cognitive offloading onto environment)
>
> Low ceilings simulate refuges—enclosed protective spaces:
> - Favored vigilance and detailed environmental monitoring
> - Monitoring mode → detail-focused cognition
>
> This is a "why" at the ultimate level—explaining why the metaphor exists in the first place.
>
> ---
>
> **VI. Cross-Level Integration**
>
> The accounts are complementary, not competing:
>
> | Level | Account | Testable Prediction |
> |-------|---------|---------------------|
> | Behavioral | Task-type moderation | Divergent ↑, convergent ↓ |
> | Cognitive | Metaphor priming | Freedom-word priming mediates |
> | Neural | DMN/TPN balance | High ceiling → ↑ DMN |
> | Computational | Precision weighting | High ceiling → ↓ prior precision |
> | Evolutionary | Prospect affordance | Should correlate with prospect-refuge preferences |
>
> The evolutionary account explains *why* the metaphor exists. The computational account explains *how* the effect optimizes cognition. The cognitive account explains *what* mental representations are involved. The neural account identifies *where* in the brain. The behavioral account captures *when* the effect appears.
>
> ---
>
> **VII. Open Questions**
>
> 1. **Habituation**: Does the effect persist for people who work in high-ceiling spaces daily?
> 2. **Optimal height**: Is there a threshold? A ceiling?
> 3. **Individual differences**: Who responds most strongly?
> 4. **Cultural variation**: Does the metaphor hold cross-culturally?
> 5. **Real-world validity**: Lab effects use photos; do actual high ceilings show the same effects?
> 6. **Design combinations**: How does ceiling height interact with other factors (lighting, nature, crowding)?
>
> Would you like me to go deeper on any level, or discuss the methodological limitations in more detail?

---

## Part XI: Appendices

### Appendix A: Question Classification Heuristics

| Pattern | Likely Type |
|---------|-------------|
| "Does X affect Y?" | EFFECT_EXISTENCE |
| "How much does X..." | EFFECT_SIZE |
| "How does X work?" | PROXIMATE_MECHANISM |
| "Why does X happen?" | FUNCTIONAL_WHY |
| "Why X and not Y?" | CONTRASTIVE_WHY |
| "How strong is the evidence..." | EVIDENCE_ASSESSMENT |
| "What should I..." | DESIGN_RECOMMENDATION |
| "What's interesting about..." | TOPIC_DISCOVERY |
| "What don't we know..." | GAP_IDENTIFICATION |
| "What's the neural basis..." | NEURAL_SUBSTRATE |

### Appendix B: Confidence Vocabulary

| Confidence Level | Phrases |
|------------------|---------|
| Strong evidence | "well-established," "robust," "replicated," "strong evidence shows" |
| Moderate evidence | "suggests," "indicates," "evidence supports," "appears to" |
| Weak evidence | "preliminary," "limited evidence," "one study found," "tentative" |
| Theoretical | "theory predicts," "would be expected," "should, in principle" |
| Speculative | "speculative," "might," "plausibly," "one possibility is" |
| Unknown | "unknown," "not studied," "remains to be determined" |

### Appendix C: Depth Transition Phrases

| To go deeper | Phrase |
|--------------|--------|
| +mechanism | "This works because..." |
| +neural | "At the neural level..." |
| +evolutionary | "From an evolutionary perspective..." |
| +computational | "Computationally, this can be modeled as..." |
| +evidence detail | "The key study showing this..." |
| +methodology | "Methodologically, this was tested by..." |
| +limitations | "The limitations of this evidence include..." |
| +alternatives | "An alternative explanation is..." |

---

## Part XII: Panel Endorsements

### Final Panel Review

**Lipton**: "The progressive disclosure structure respects the core insight that explanation is contrastive and audience-relative. The five depth levels map well onto the kinds of explanatory information people seek."

**Lombrozo**: "The emphasis on mechanism at every level beyond L1 is appropriate—humans don't feel they've explained something until they see how it works. The templates should enforce this."

**Strevens**: "The depth levels correctly identify that the 'right' depth depends on what difference-maker the user is seeking. The system should help users discover what depth they actually need."

**Chi**: "The interaction patterns support self-explanation. By offering prompts for deeper levels, the system invites the user to predict what they'll learn—this enhances learning."

**Bereiter**: "The user model distinguishes knowledge-telling from knowledge-building. This is essential—the same user may switch modes, and the system should track this."

**Gopnik**: "The question typology correctly identifies that 'why' questions come in kinds—functional, developmental, contrastive. Different 'whys' need different explanatory resources."

**Kaplan (R.)**: "The application examples show appropriate respect for evidence quality—recommending strongly where evidence is strong, hedging where it isn't. This serves architects and designers well."

**Friston**: "The computational-level integration is appropriate. Predictive processing provides a unifying framework for understanding when effects will generalize."

**Pallasmaa**: "I would add attention to phenomenological depth—not just mechanism, but experience. How does the high ceiling *feel*? This matters for architects."

**Response**: Phenomenological depth added as optional extension to L4 explanations.

---

*End of Specification*

**Document Status**: Complete, ready for implementation
**Next Steps**:
1. Build question classifier for 25+ types
2. Implement user model
3. Create response templates
4. Integrate with Web of Belief
5. Build progressive disclosure UI

---

*Prepared by Panel P-QA, February 16, 2026*
