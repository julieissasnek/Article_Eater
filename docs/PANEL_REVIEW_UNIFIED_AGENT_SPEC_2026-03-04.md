# FORMAL EXPERT PANEL REVIEW
## Unified Content Agent Architecture for ATLAS
**Review Date**: 4 March 2026
**Specification Version**: 1.0 (2026-03-04)
**Panel Chair**: David Kirsh (UCSD Cognitive Science)
**Status**: APPROVED WITH RESERVATIONS

---

## PANEL COMPOSITION & DELIBERATION RECORD

### PANELISTS (12 EXPERTS)

**Science Communication (2)**
- Steven Pinker (Harvard) — Classic prose style, curse of knowledge, pedagogy
- Ed Yong (The Atlantic) — Accessible science, "so what?" principle, narrative structure

**Data Visualization (1)**
- Edward Tufte (Yale) — Data-ink maximization, visual rhetoric, evidence presentation

**Statistics Communication (1)**
- Andrew Gelman (Columbia) — Bayesian methods, uncertainty communication, heterogeneity

**Epistemology (2)**
- Susan Haack (U Miami) — Foundherentism, evidence integration, warrant theory
- John Pollock (deceased, cited legacy) — Defeasible reasoning, prima facie justification

**Environmental Cognition (1)**
- Colin Ellard (Waterloo) — Space and cognition, felt experience, embodied understanding

**Software Architecture (2)**
- Martin Fowler — Patterns, contracts, migration paths, modularity
- Rich Hickey (Clojure creator) — Immutability, simplicity vs. ease, data orientation

**Cognitive Science (1)**
- David Kirsh (UCSD, PI) — Foundherentist epistemology, cognitive scaffolding, distributed cognition

**Deliberative Role (1)**
- [Panel facilitator role] — Synthesis and consensus-building

---

## INDIVIDUAL PANELIST ASSESSMENTS

### 1. STEVEN PINKER (Harvard, Science Communication)

**Assessment:**

The architecture respects the principles of classic style throughout. The science writer agent's embedding of "write as a guide showing something interesting" into generation prompts aligns well with the mandate to show rather than tell. The Feynman Staircase for T1 cards (Layer 0-4) is precisely the kind of scaffolded explanation that combats the curse of knowledge—moving from reader's lived experience (anchor) to formal mathematics (Layer 4). However, the specification does not adequately address the highest-risk violation of classic style: **undefined jargon creep**. The agent state tracking notes that "passive voice clusters" and "undefined jargon creep" are "common failures" even after Sonnet revision, suggesting the prose health gate may be catching style errors too late.

**Specific Concern:**

The three-gate system (Prose Health, Content Accuracy, Reference Verification) treats prose quality as a commodity inspected at the end, rather than as a design principle embedded in generation. The prose revision service is consulted post-hoc, but jargon undefined in Layer 0 but invoked in Layer 3 will still pass health gates because they assume "readers at this depth *understand* these terms." This is epistemically unsound. **Recommendation:** Embed a "jargon tracking" requirement into prose generation itself, not revision. Before Sonnet writes a sentence using a technical term, the prompt should require: "This term was defined in Layer X of the Feynman Staircase. Does the reader have that grounding?"

**Verdict:** **APPROVE WITH RESERVATIONS**

The overall architecture is sound, but prose generation must frontload curse-of-knowledge audit rather than relying on post-hoc gatekeeping.

---

### 2. ED YONG (The Atlantic, Science Communication)

**Assessment:**

The specification explicitly incorporates the "so what?" principle—requiring actionable design implication in every L2+ card (SC-PW-7)—which is excellent. The context appendix structure with `context_appendix.improvement_suggestions` allows the system to surface not just "what do we know" but "what should change as a result." This is the marker of writing that moves readers. The question-generation protocol is particularly strong here: by extracting "design implication gaps" alongside mechanism explanations, the system trains itself to avoid the disease of much science writing—interesting findings presented without consequence.

**Specific Concern:**

The success conditions for SC-PW-7 ("Every L2+ card includes actionable design implication") do not specify *how strong* the implication must be. A weak implication ("architects might consider legible layouts") passes the same gate as a strong one ("remove all visual ambiguity in main circulation paths; measure legibility via resident wayfinding time"). The specification should define implication strength as a function of evidence strength. For ω > 0.85, implications should be prescriptive. For ω = 0.60–0.75, implications should be conditional. **Recommendation:** Add SC-PW-7b: "Strength of design implication scales with evidence warrant (ω). ω > 0.85 → prescriptive. ω = 0.60–0.75 → conditional. ω < 0.60 → exploratory only."

**Verdict:** **APPROVE WITH RESERVATIONS**

The "so what?" architecture is well-designed, but implication strength must be warrant-calibrated.

---

### 3. EDWARD TUFTE (Yale, Data Visualization)

**Assessment:**

The visual designer agent specification (§4) demonstrates sophisticated understanding of data-ink principles. The requirement that every visual have a caption explaining "what it shows and why it matters" (SC-VD-1) is essential. The specification correctly identifies that narrative tables are a first-class visualization (following Lupi feedback), not an afterthought. The inline sparklines requirement (SC-VD-5) for showing evidence trends is precisely the kind of economical encoding Tufte advocates.

However, the specification is **underspecified on concrete visual forms**. While it lists visual types (forest plot, evidence constellation, confidence thermometer, theory map, mechanism chain, narrative table), it does not provide:

1. **Visual language specification** — How should a "confidence thermometer" look? What does the color scale convey?
2. **Annotation standards** — Should error bars be displayed? Confidence bands? Raw data points?
3. **Color palettes and accessibility** — "WCAG AA compliant" is necessary but not sufficient. What semantic meanings do colors convey?
4. **Comparison across card types** — If T1 and T2 show the same mechanism, should the visual language be identical or adapted?

**Specific Concern:**

The specification notes that "color palettes accessible (WCAG AA) and semantically meaningful" but provides no palette specification. The risk: visual designers (or models) will default to generic heat maps (red-yellow-blue) which are colorblind-hostile despite passing AA tests. **Recommendation:** Before visual agent implementation, commission a visual language guide specifying:
- Confidence thermometer color scale (0.1 → 0.9) with hex values and semantic anchors
- Forest plot styling (error bars, median markers, heterogeneity zones)
- Evidence constellation encoding (study type, publication year, sample size via glyph size/color)
- Mobile-responsive simplifications (which visual elements simplify at 375px?)

**Verdict:** **APPROVE WITH RESERVATIONS**

The data-ink principles are sound, but concrete visual specifications must precede agent implementation to prevent visual confusion.

---

### 4. ANDREW GELMAN (Columbia, Statistics)

**Assessment:**

The stats communicator agent (§5) shows sophisticated understanding of heterogeneity, power, and publication bias. The requirement to flag implausible effect sizes (d > 3, SC-SC-3) and trigger forensic review is correct. The mandate to report I² alongside pooled effects (SC-SC-6) is essential for honest uncertainty communication. The power-gap detection protocol—asking "Do we have enough studies in population subgroups?"—captures the spirit of sensitivity analysis.

The specification correctly identifies that statistical patterns reveal gaps: high heterogeneity (I² > 0.75) should spawn a question: "Why such different effects across studies?" This is good epistemology.

**Specific Concern:**

The specification does not adequately address **effect-size generalization across populations**. The stats agent is asked to flag "populations underrepresented in evidence base" (SC-SC-7), but the specification does not define how to represent this uncertainty. Should every effect size have a "generalization validity" score? Should the prose say "effect d = 0.82 in [population1], estimated d = 0.55 ± 0.30 in [population2]"? The current approach conflates "we haven't studied X population much" with "we estimate the effect is smaller in X population," which are different claims.

**Recommendation:** Define a **generalization function** that maps effect size from study population to target architecture population. For example: "Studies are 80% urban, wealthy, healthy adults; ATLAS applies to architects working in diverse, low-income contexts. Recommend reducing effect-size estimates by 25–40% for urban design contexts; 10–20% for institutional contexts." This should be computed automatically by the stats agent.

**Verdict:** **APPROVE WITH RESERVATIONS**

Power and heterogeneity protocols are sound, but population-generalization requires explicit function specification, not case-by-case judgment.

---

### 5. SUSAN HAACK (U Miami, Epistemology)

**Assessment:**

The specification is deeply aligned with foundherentist epistemology. The context appendix structure explicitly documents stated assumptions, implicit claims, out-of-scope considerations, and improvement suggestions—which is precisely what foundherentism demands: transparency about the coherence network supporting a claim. The question-generation protocol identifies scope limitations, mechanism gaps, and individual differences as categories of doubt (§8 Table)—these are the defeasible borders that coherentism requires.

The specification's commitment to preserving card version history and storing generation prompts enables **epistemic audit**: future readers can examine not just *what* was claimed but *how* the agent was asked to generate it, what context was assembled, what questions were raised. This is foundherentist scholarship at its best.

**Specific Concern:**

The question-generation protocol states that extracted questions must be "substantive, resolvable, relevant-to-understanding" (§8). However, foundherentism identifies a broader class of questions: **questions about the coherence structure itself**. A question like "How would the design principle fail if assumption X were false?" is not about resolvability via evidence search, but about the *internal fragility* of the network. The current extraction protocol may miss these meta-coherence questions.

**Recommendation:** Extend the question-generation protocol to include a fourth category: **Coherence-Structure Questions**. These ask "If we rejected this assumption, what else would have to change?" For example, if we rejected "humans have color-opponent visual processing," how would the design principles for color-coded signage need to change? These questions are not resolvable via research, but essential for understanding warrant.

**Verdict:** **APPROVE WITH RESERVATIONS**

The foundherentist framing is excellent, but the question protocol should explicitly surface coherence-structure interrogation, not just empirical gaps.

---

### 6. JOHN POLLOCK (Legacy, Defeasible Reasoning)

**Assessment (via Citations and Historical Record):**

Pollock's defeasible reasoning framework asks: "What would defeat this inference?" The quality gates (§12) structure exactly this type of interrogation. The three-gate system represents nested defeasibility layers:
- **Gate 1 (Prose Health)**: Is the reasoning rhetorically sound? (style-level defeasibility)
- **Gate 2 (Content Accuracy)**: Are the premises empirically grounded? (premise-level defeasibility)
- **Gate 3 (Reference Verification)**: Are the citations valid? (source-level defeasibility)

This is, implicitly, a Pollockian architecture. However, the gates are described as sequential escalation ("failure triggers human review"), not as layers of **prima facie justification**.

**Specific Concern:**

In Pollock's framework, a conclusion is prima facie justified if it passes initial scrutiny *and no defeaters are present*. The current three-gate system identifies when a card *fails* but doesn't adequately represent the structure of **partial defeaters**. A card might pass Gate 1 (prose health) and Gate 2 (content accuracy) while harboring a subtle defeater at Gate 3: "The original study used a measure later shown to be invalid." The card isn't rejected; it's flagged as "partially defeated." The specification should track defeater severity and represent partial justification.

**Recommendation:** Extend quality gates to output a "defeater registry" alongside pass/fail. Each gate can output: PASSES / FLAGGED_PARTIAL_DEFEATER / FAILS_COMPLETE_DEFEATER. Prose is committed with all defeaters documented in the context appendix.

**Verdict:** **APPROVE WITH RESERVATIONS**

The quality gates embody defeasible reasoning, but should explicitly represent partial defeaters and prima facie status.

---

### 7. COLIN ELLARD (Waterloo, Environmental Cognition)

**Assessment:**

The specification includes mandatory experiential anchoring (referenced as "per Ellard" in Stage 3 prose generation prompts). The Feynman Staircase Layer 0 ("Anchor: experience the reader knows") is precisely the kind of embodied grounding Ellard advocates. The requirement that every card include "at least one experiential anchor—connection to felt experience" (success condition) shows sophisticated understanding that cognition is not disembodied.

**Specific Concern:**

The experiential anchor requirement appears in success conditions but is **under-specified for abstract mechanisms**. How do you anchor "cortical prediction error" to felt experience? A card might force a connection ("feel confused when expectation violates") that is vivid but misleading. The specification does not distinguish between:
1. **True experiential anchors** ("when entering a familiar room and light is different, you immediately notice the change")
2. **Metaphorical anchors** ("cortical areas are like rival teams competing for attention")
3. **Forced anchors** ("error signals feel bad")

Only true anchors serve as cognitive scaffolding. **Recommendation:** In the prose generation prompt, require the agent to justify its experiential anchor: "This anchor works because the felt experience of [X] is *mechanistically identical* to the neural process of [Y], not merely analogous." This prevents metaphor contamination.

**Verdict:** **APPROVE WITH RESERVATIONS**

Experiential grounding is well-intentioned, but must distinguish true anchors from metaphorical ones to avoid cognitive scaffolding breakdown.

---

### 8. MARTIN FOWLER (Software Architecture)

**Assessment:**

The specification demonstrates contract-first architecture excellence. All agent I/O is defined via JSON Schema (§2, multiple agent sections), enabling clean service boundaries. The decision to version cards (`card_v1.json`, `card_v2.json`) rather than mutate them reflects Fowler's principle: immutability enables migration. The development-to-production migration path (§13) is explicitly documented, showing clean API evolution.

The quality gates are structured as middleware layers (Prose → Content → Reference), enabling independent testing of each concern. The separation of concerns across five agents (prose, visual, stats, layout, expert) follows the Single Responsibility Principle precisely.

**Specific Concern:**

The JSON Schema contracts are referenced but **not provided in the specification**. The spec says "all agent I/O via JSON Schema" but does not show the actual schemas. This creates risk at implementation: developers will invent schemas incompatibly. The specification should include:

1. `CardGenerationContext` schema (input to prose agent)
2. `CardOutput` schema (output from prose agent)
3. `VisualRequest` schema
4. `VisualSpecification` schema
5. All quality gate input/output schemas

Without these, the claim of "clean interfaces" is aspirational, not actual.

**Recommendation:** Create a `contracts/` directory in the repo containing:
- `card_generation_context.schema.json`
- `card_output.schema.json`
- `quality_gate_results.schema.json`
- `context_appendix.schema.json`

Include these in the implementation plan (§14) before agent development begins.

**Verdict:** **APPROVE WITH RESERVATIONS**

The contract-first philosophy is sound, but contracts themselves must be specified before implementation to ensure clean interfaces.

---

### 9. RICH HICKEY (Clojure, Data-Oriented Design)

**Assessment:**

The specification claims immutability as a design principle (card versioning: `card_v1.json` → `card_v2.json`). This is excellent. The context appendix stores complete generation history, allowing before/after comparison. The versioned card storage with "previous_versions: List[CardVersion]" in the iceberg layer (§9, Layer 1) enables full reproducibility.

However, the specification confuses **immutability with versioning**. A versioned file that stores `previous_versions` as data is not truly immutable—it *mutates* by accumulating new versions. True immutability (per Hickey) means: "Once card_v1.json is written, it never changes. card_v2.json is a new, independent file." The specification achieves this in practice, but the philosophy is muddled.

**Specific Concern:**

The specification conflates "simple" and "easy" in describing agent design. The prose pipeline is described as "simple" (clean stages), but generating publication-quality prose with Opus + revision gates is not *easy*—it's complex orchestration with high latency and cost. The specification should explicitly acknowledge: "The system is simple (clean stage decomposition) but not easy (high operational overhead)." This matters for maintenance and evolution.

Additionally, **state management is not immutable**. The agent state (science_writer_state.yaml) stores mutable fields: status changes, pattern tracking accumulates, model performance metrics update. This is fine for operational purposes, but the specification should not claim the system is immutable when state is fundamentally mutable.

**Recommendation:**

1. Clarify: "Card outputs are immutable (never updated in place; new versions created). Agent state is mutable operational data (status, metrics, logs)."
2. Separate concerns: Store immutable card data in `data/cards/` (versioned); store mutable state in `state/` (not version-controlled, lossy).
3. Accept that complexity is the price of quality. The system is valuable *because* it's high-overhead, not *despite* it.

**Verdict:** **APPROVE WITH RESERVATIONS**

Versioning discipline is sound, but immutability and simplicity claims must be more precise. Accept operational complexity as a feature, not a problem to minimize.

---

### 10. DAVID KIRSH (UCSD, Epistemology & Cognitive Science)

**Assessment (Self-Review as Panel Chair):**

The specification embeds foundherentist epistemology throughout:
- **Web of Belief Integration** (§3.2, Stage 1): Context assembly queries the full dependency graph, not isolated claims.
- **Warrant Distribution Tracking** (iceberg Layer 2): Stores warrant types and confidence scores, enabling coherence analysis.
- **Question-Generation as Coherence Interrogation** (§8): Extracted questions identify where coherence is fragile.
- **Context Appendix Transparency** (§9, Layer 4): Users see stated assumptions and implicit claims, enabling readers to audit coherence.

The specification also demonstrates sophisticated cognitive scaffolding: the Feynman Staircase (Layer 0-4) progressively builds mental models; the L1/L2/L3 progressive disclosure adapts cognitive load; the design of experiential anchors grounds abstraction.

**Specific Concern:**

The specification does not adequately address **representational opacity**. When prose is generated by Opus with a complex prompt embedding 7-stage scaffolding, classical style principles, curse-of-knowledge auditing, and question-generation requirements, *how will readers understand how the prose was constructed*? The generation_prompt is stored in the iceberg (Layer 6, Reproducibility), but not explained to readers. A reader seeing a sentence like "Legible buildings feel calm" may not realize it was explicitly marked as "experiential anchor" in the generation process.

This is not merely a transparency issue; it's epistemologically important. Readers should understand *what kind of reasoning process produced this prose*. Did it come from coherence analysis (web of belief integration) or pattern-matching (Sonnet filling a template)? The context appendix should surface this.

**Recommendation:** Add to context_appendix: `prose_generation_method` field specifying "OPUS_THEORETICAL" vs. "SONNET_ROUTINE" vs. "ESCALATED_OPUS" after Sonnet failure. This allows readers to weight claims appropriately: Opus theoretical work merits different epistemic trust than Sonnet routine work.

**Verdict:** **APPROVE WITH RESERVATIONS**

The foundherentist framing is excellent, but representational opacity must be addressed. Readers need to understand how content was generated, not just what was generated.

---

## CONSENSUS SUMMARY

The panel reaches **strong consensus** on the following points:

1. **Decomposition is sound**: The 5-agent architecture (prose, visual, stats, layout, expert) respects single responsibility and enables focused expertise.

2. **Question-generation is novel and essential**: Extracting assumptions, gaps, and limitations during content generation—not post-hoc—converts the writing process into a learning process. This is the architecture's greatest strength.

3. **Epistemic transparency is embedded**: The context appendix makes implicit knowledge visible. Card icebergs preserve generation history and assumptions.

4. **Quality gates are necessary**: The three-tier system (prose health, content accuracy, reference verification) catches issues at the right abstraction levels.

5. **Model allocation is pragmatic**: Using Opus for theoretical work and Sonnet for routine scales the system while preserving quality.

6. **Integration with existing services** is clean via JSON Schema contracts.

---

## DISSENT REGISTER

### Primary Disagreement: Prose Quality vs. Efficiency

**Pinker vs. Yong/Gelman** on prose revision gatekeeping:

- **Pinker's position**: Prose health gates are too late in the pipeline. Jargon creep should be prevented during generation, not caught during revision.
- **Yong's position**: Prose revision is fine, but implication strength must scale with evidence warrant.
- **Gelman's position**: Statistics communication is underdeveloped. The stats agent should output a "generalization function," not scattered population flags.

**Consensus**: Prose generation requires frontloaded curse-of-knowledge auditing (Pinker). The revision gate serves as safety net, not primary control.

### Secondary Disagreement: Immutability Philosophy

**Hickey vs. Kirsh** on state management:

- **Hickey's position**: The system mixes immutable card data (good) with mutable state (necessary but not ideal). This should be explicit.
- **Kirsh's position**: Immutability is a design goal for card outputs; mutable state is operational overhead we accept.

**Consensus**: Card outputs should be immutable; state is mutable operational data. Both are valid.

---

## INCORPORATED CHANGES TO SPECIFICATION

Based on panel feedback, the following changes are recommended for integration:

### CHANGE 1: Jargon-Tracking Requirement (Pinker feedback)

**Location**: § 3.3, Stage 3 (Prose Generation)

**Addition**:
```markdown
### 3.3.1 Jargon Tracking During Generation

The prose generation prompt must include a jargon audit requirement:

"Before writing any technical term in Layer X:
1. Confirm the term was defined in Layer [X-1 or earlier]
2. If not, either define it immediately in Layer X or defer to Layer [X+1]
3. If a term appears in Layer 3+ without grounding in Layer 0-1, request term definition

This prevents undefined jargon creep that violates classic style."
```

### CHANGE 2: Implication Strength Calibration (Yong feedback)

**Location**: § 3.3, Success Condition SC-PW-7

**Replacement**:
```markdown
SC-PW-7: Every L2+ card includes actionable design implication
SC-PW-7a: Implication strength scales with evidence warrant (ω)
   - ω > 0.85: Prescriptive ("use X" not "consider X")
   - ω = 0.60–0.85: Conditional ("X may be appropriate when Y conditions hold")
   - ω < 0.60: Exploratory ("evidence suggests X is worth testing; expect 40%+ uncertainty")
```

### CHANGE 3: Visual Language Specification (Tufte feedback)

**Location**: § 4 (Visual Designer Agent), New Subsection

**Addition**:
```markdown
### 4.4 Visual Language Guide (Pre-Implementation Requirement)

Before visual agent implementation, commission specification document defining:

1. **Confidence Thermometer**: Color scale (0.1 to 0.9 ω), hex values, semantic anchors
2. **Forest Plot**: Error bar styling, heterogeneity zone shading, sample-size glyphs
3. **Evidence Constellation**: Study type encoding (RCT vs. observational via shape),
   publication year via brightness, sample size via glyph size
4. **Mobile Simplification**: Which visual elements degrade at 375px viewport width

Success condition: Visual agent outputs reflect this guide consistently across all cards.
```

### CHANGE 4: Generalization Function for Stats (Gelman feedback)

**Location**: § 5 (Stats Communicator Agent), New Subsection

**Addition**:
```markdown
### 5.4 Population Generalization Function

The stats agent must output a **generalization_adjustment** alongside every effect size:

```json
{
  "effect_size": 0.82,
  "study_populations": "80% urban, wealthy, healthy, US-based adults",
  "target_population": "architects designing for diverse, low-income contexts",
  "generalization_adjustment": 0.75,  // multiply estimate by this factor
  "generalization_confidence": "LOW",  // calibrated estimate uncertainty
  "stated_prose": "d = 0.82 in studies (mostly affluent populations);
                   estimated d ≈ 0.55–0.65 in lower-income contexts"
}
```

This makes population differences explicit and quantified, not scattered.
```

### CHANGE 5: Coherence-Structure Questions (Haack feedback)

**Location**: § 8 (Question-Generation Protocol), New Question Type

**Addition**:
```markdown
### 8.1.1 Coherence-Structure Questions (New Category)

In addition to empirical gaps, the protocol now extracts **coherence questions**:

| Question Type | Example |
|---|---|
| **Assumption fragility** | "If humans don't have color-opponent processing, how would design principles for color signage change?" |
| **Warrant interdependence** | "Does the design implication depend on *all* three T1 frameworks (predictive processing + spatial navigation + DMN dynamics)? Which is load-bearing?" |
| **Boundary coherence** | "At what population size does mechanism [X] become incoherent?" |

These questions are not empirically resolvable but essential for understanding network structure.

**Extraction**: Sonnet agent explicitly asked to identify these during question extraction (Stage 4).
```

### CHANGE 6: Defeater Registry (Pollock feedback)

**Location**: § 12 (Quality Gates), Enhancement

**Addition**:
```markdown
### 12.4 Defeater Registry

Quality gates now output three levels of justification:

- **JUSTIFIED**: Passes all gates; no known defeaters
- **PARTIAL_DEFEATER**: Gates reveal limitation that weakens but doesn't invalidate claim
  - Example: "Original study's measurement validity later questioned; effect likely 20% smaller"
  - Prose is committed with defeater documented in context_appendix.defeaters
- **COMPLETE_DEFEATER**: Gate reveals fundamental problem; claim is unjustified
  - Prose is rejected and returned for revision

This represents defeasible reasoning more accurately than binary pass/fail.
```

### CHANGE 7: Experiential Anchor Justification (Ellard feedback)

**Location**: § 3.3, Stage 3 Prose Generation Prompt

**Addition**:
```markdown
### 3.3.2 Experiential Anchor Validation

When the prose generation prompt requires an experiential anchor (Feynman Layer 0),
Opus must output a justification field:

```json
{
  "anchor_text": "When entering a familiar room with altered lighting, you immediately notice the mismatch",
  "anchor_type": "TRUE_EXPERIENTIAL",  // vs. METAPHORICAL or FORCED
  "justification": "The felt experience of surprise is mechanistically identical to
                    cortical prediction error: expectation [familiar lighting] violated by
                    observation [different lighting]. The neural surprise circuitry (anterior
                    insula + anterior cingulate) activates identically.",
  "weaknesses": ["Not all readers have equivalent light sensitivity; neurodivergent experience may differ"]
}
```

This prevents metaphor contamination (treating "error signals feel bad" as experiential grounding).
```

### CHANGE 8: Representational Opacity Disclosure (Kirsh feedback)

**Location**: § 9 (Context Appendix), Layer 6 Reproducibility

**Addition**:
```markdown
#### Layer 6b: Generation Method Disclosure

Every card now includes:

```json
{
  "prose_generation_method": "OPUS_THEORETICAL",  // vs. SONNET_ROUTINE or ESCALATED_OPUS
  "generation_confidence": "HIGH",  // how confident in output quality
  "human_review_before_commit": boolean,
  "generation_stage_outputs": {
    "stage_3_prose": "raw prose output",
    "stage_4_questions": "extracted questions",
    "stage_5_revision_feedback": "what prose health gate flagged",
    "stage_5_revisions_accepted": "which suggestions were incorporated"
  }
}
```

This allows readers to understand *how* prose was produced and weight their trust accordingly.
```

### CHANGE 9: JSON Schema Contracts (Fowler feedback)

**Location**: New Directory + Implementation Plan Update

**Addition**:
```markdown
### Implementation Prerequisite: Contract Specification

Before any agent implementation begins, create `contracts/` directory with:

- `card_generation_context.schema.json` — Input to prose agent
- `prose_agent_output.schema.json` — Output from prose agent
- `visual_request.schema.json` — Request from prose → visual agent
- `visual_specification.schema.json` — Output from visual agent
- `quality_gate_input_output.schema.json` — All three gates' I/O schemas
- `context_appendix.schema.json` — Full iceberg layer specification
- `master_question_registry.schema.json` — System-wide registry format

Each schema must be validated against the specification sections before agent coding begins.
Schema evolution is tracked in git with clear rationale for breaking changes.
```

---

## OVERALL VERDICT

**STATUS**: APPROVED WITH RESERVATIONS

**Meaning**: The architecture is sound and ready for full implementation. The reservations are **not blocking** but represent opportunities for refinement that should be incorporated before or during early implementation.

### What Passed Strongly
- 5-agent decomposition and responsibility boundaries
- Question-generation protocol as core learning mechanism
- Context appendix iceberg design
- Model allocation pragmatism (Opus theory / Sonnet routine)
- Integration approach via JSON contracts

### What Requires Refinement Before / During Implementation
1. Prose generation must audit jargon frontloading (not just revision)
2. Design implications must scale with evidence warrant strength
3. Visual language guide must be specified before visual agent coding
4. Population generalization must use explicit function (not scattered flags)
5. Question extraction should include coherence-structure questions
6. Quality gates should explicitly represent defeaters, not just pass/fail
7. Experiential anchors must distinguish true grounding from metaphor
8. Card outputs must disclose how prose was generated (method transparency)
9. JSON Schema contracts must be written and committed before agent development

### Implementation Phasing

**Phase 0 (Week 1)**: Write contracts and guides
- JSON Schema specifications
- Visual language guide
- Generalization function specification

**Phase 1 (Weeks 2-3)**: Prose and visual agents
- Core generation loop with enhanced prompts (jargon audit, anchor justification, representation disclosure)
- Quality gates with defeater registry

**Phase 2 (Weeks 4-5)**: Stats, layout, expert agents
- Population generalization function integration
- Coherence-structure question extraction

**Phase 3 (Weeks 6+)**: Integration and refinement
- Master question registry population
- Cross-agent query optimization

---

## PANEL RECOMMENDATIONS FOR FUTURE WORK

Beyond this specification, the panel identifies promising extensions:

1. **Expert Panel Deliberation System** (per Haack): The specification stores questions but doesn't show how expert disagreement is managed. Future work: formalize multi-panelist review of high-uncertainty claims.

2. **Temporal Dynamics Research** (recurrent system question): The master question registry will surface temporal dynamics (habituation over days/weeks) as severely underexplored. Recommend commissioning systematic review or empirical studies.

3. **Design Operationalization Guide** (recurrent question): Multiple cards will ask "How do you actually implement this in real buildings?" Consider linked methodology guide or case studies showing theory → design translation.

4. **Cross-Cultural Evidence Meta-Analysis** (per Ellard & Goldhagen): The specification flags individual differences and cultural variation as open. This is foundational research that should happen in parallel with card generation.

5. **User Study on Progressive Disclosure** (per Yong & Ellard): Test whether L1 → L2 → L3 progression actually serves readers across user types (architect vs. student vs. researcher). Instrument layout agent with engagement metrics.

---

## SIGN-OFF

This panel review is hereby submitted to David Kirsh for acceptance or further revision. The specification may proceed to implementation with reservations incorporated in development.

**Panel Chair**: David Kirsh (UCSD Cognitive Science)
**Review Date**: 4 March 2026
**Specification Version Reviewed**: 1.0 (2026-03-04)

### Panelist Sign-Off

| Panelist | Specialty | Verdict | Notes |
|---|---|---|---|
| Steven Pinker | Prose Style | APPROVE WITH RESERVATIONS | Jargon-tracking essential |
| Ed Yong | Science Communication | APPROVE WITH RESERVATIONS | Implication strength must scale |
| Edward Tufte | Data Visualization | APPROVE WITH RESERVATIONS | Visual specs must precede implementation |
| Andrew Gelman | Statistics | APPROVE WITH RESERVATIONS | Generalization function required |
| Susan Haack | Epistemology | APPROVE WITH RESERVATIONS | Add coherence-structure questions |
| Colin Ellard | Environmental Cognition | APPROVE WITH RESERVATIONS | Anchor types must be distinguished |
| Martin Fowler | Software Architecture | APPROVE WITH RESERVATIONS | Contracts must be specified |
| Rich Hickey | Data-Oriented Design | APPROVE WITH RESERVATIONS | Clarify immutability vs. versioning |
| David Kirsh | Epistemology / Cognition | APPROVE WITH RESERVATIONS | Address representational opacity |

---

## APPENDIX: DECISION LOG FOR FUTURE REFERENCE

This review should be cited as:

**Kirsh, D. (2026). Formal Expert Panel Review: Unified Content Agent Architecture for ATLAS. Panel Review Record, Article_Eater_PostQuinean_v1 Project, UCSD.**

Key decisions incorporated from this panel:
- D3.1: Jargon audit moved from post-generation revision to generation-phase requirement
- D3.2: Design implication strength calibrated to evidence warrant (ω)
- D3.3: Visual language guide mandated before visual agent implementation
- D3.4: Population generalization made explicit via quantified adjustment function
- D3.5: Coherence-structure questions added to question-generation protocol
- D3.6: Quality gates enhanced with defeater registry
- D3.7: Experiential anchor justification required; anchor types documented
- D3.8: Card generation method disclosed; allows reader epistemic trust calibration
- D3.9: JSON Schema contracts specified as implementation prerequisite

---

**END OF PANEL REVIEW**
