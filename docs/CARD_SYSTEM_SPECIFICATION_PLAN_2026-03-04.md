# ATLAS Card System: Specification Plan

**Date**: 4 March 2026
**Author**: Claude (Opus), with David Kirsh
**Status**: PLAN — awaiting David's review before execution
**Scope**: Full specification of all card types, the iceberg architecture, visual requirements, user-type adaptation, and integration with the agent-based service architecture

---

## 1. The Problem

ATLAS generates knowledge artifacts at every level of its hierarchy — from individual article extractions to synthesized positions on broad scientific questions — but these artifacts have no unified specification. The codebase contains an `AnswerCard` dataclass, a `RenderedAnswer` with confidence thermometer, and a `MoleculeCardGenerator` with three disclosure levels, but these were built bottom-up as engineering conveniences rather than designed top-down as a coherent knowledge presentation system. The master document, meanwhile, documents the theoretical architecture comprehensively (T1 frameworks, T1.5 reductions, T2 templates, credence propagation, web of belief) but says almost nothing about how that knowledge is *presented* to different user types, what the surface and depth layers of a knowledge artifact look like, or how the system's own architecture should be explained to users.

The result is a system that knows a great deal but has no principled way of showing what it knows. This plan specifies what needs to be built.

---

## 2. Card Taxonomy: What Kinds of Knowledge Artifacts Does ATLAS Produce?

The audit identified **eight distinct card types**, organized into three tiers by the level of synthesis they represent.

### Tier A: Entity Cards (Wikipedia-style explanatory entries)

These are the "epistemic loci" from §173 — synthesized, multi-source entries that explain a concept in depth.

| Card Type | What It Explains | Example | Approximate Count |
|-----------|-----------------|---------|-------------------|
| **T1 Framework Card** | One of 10 neurally grounded framework theories | "Predictive Processing: How hierarchical prediction-error minimization shapes perception, action, and affect" | 10 |
| **T1.5 Domain Theory Card** | One of 13 formally reduced domain theories | "Attention Restoration Theory: How nature exposure reduces directed-attention fatigue via DMN release" | 13 |
| **T2 Mechanism Card** | One of 166 mechanistic templates | "LIGHT-01: How morning daylight (≥2,500 lux) entrains the circadian system via melanopsin-ipRGC activation" | 166 (103 calibrated, 63 scaffold) |
| **Molecule Card** | One of 18 latent variable bundles | "Soft Fascination: The co-occurrence of low-threat salience, moderate visual complexity, and DMN-permissive sensory input" | 18 |

### Tier B: Evidence Cards (Article-anchored findings)

These are source cards — atomic units tied to specific studies.

| Card Type | What It Captures | Example | Approximate Count |
|-----------|-----------------|---------|-------------------|
| **T3 Belief Card** | An individual empirical claim with provenance | "Bratman et al. (2015): 90-min nature walk reduced subgenual PFC activity (d = 0.48, N = 38)" | 12,000+ |
| **Competition Card** | A contested claim with competing accounts | "Barrett vs. Craig on affect construction: two-stage debate with three resolution scenarios" | ~120 |

### Tier C: System Cards (How ATLAS itself works)

These explain the system's own architecture, methods, and epistemic commitments.

| Card Type | What It Explains | Example | Approximate Count |
|-----------|-----------------|---------|-------------------|
| **Layer Card** | One architectural layer of the system | "The Annotation Layer: 20 annotation types, their schema, and how they enrich the evidence base" | ~12 layers |
| **Method Card** | A specific algorithm, process, or decision | "Typed Credence Propagation: How evidence flows through the web of belief via message-passing with differential attenuation" | ~20 methods |

### Total: ~12,350+ cards across 8 types

Not all will be precomputed. T3 belief cards and competition cards can be generated on demand from the database. Entity cards (Tier A) and system cards (Tier C) should be precomputed, reviewed, and maintained.

---

## 3. The Universal Card Schema: Surface, Body, and Iceberg

Every card, regardless of type, has three layers — what the user sees immediately, what they read in detail, and what lies beneath for deepening, regeneration, and audit.

### 3.1 Surface (The Card Face)

What the user sees before clicking in. Must communicate the essential identity and epistemic status at a glance.

| Field | Description | Visual Treatment |
|-------|-------------|-----------------|
| **Title** | Assertion-evidence headline (not a topic label) | Bold, 16pt, sentence case |
| **Type Badge** | T1 / T1.5 / T2 / T3 / Molecule / System | Color-coded chip |
| **Confidence Thermometer** | 4-level (HIGH / MOD-HIGH / MODERATE / LOW) with ω score | Colored bar with numeric score |
| **Direction** | ↑ increase / ↓ decrease / ↔ mixed / ∅ no effect | Arrow icon |
| **Evidence Count** | N findings from M papers | Small text below thermometer |
| **Staleness Indicator** | Fresh / Aging / Stale (based on §173.4 staleness score) | Dot: green / amber / red |
| **Key Visual** | One chart, diagram, or figure that captures the core content | Thumbnail (expandable) |

### 3.2 Body (The Readable Entry)

The main content — what a user reads when they open the card. Organized as **tabs** to serve different user types without overwhelming any single type.

#### Tab Architecture

| Tab | Content | Primary User | Always Present? |
|-----|---------|-------------|----------------|
| **Overview** | 2-3 paragraph prose summary (Zone 1 committed prose). Written at prose health ≥ 6.5. Cites key references inline. Addresses the "what and why" question. | All users | Yes |
| **Mechanism** | The causal pathway. For T2 cards: the full mechanism chain (environmental feature → neural process → outcome). For T1/T1.5 cards: the theoretical architecture and its neural implementation. Includes a mechanism diagram (visual). | Researchers, Designers | Yes (T1, T1.5, T2, Molecule) |
| **Evidence** | Quantitative evidence summary. Effect sizes with CIs. Study count, replication status, population scope. Meta-analytic forest plot or evidence weight chart (visual). Confidence decomposition (d, ω, δ breakdown). | Researchers | Yes |
| **Design** | Actionable implications. For T2 cards: specific design parameters with ranges. For T1/T1.5: broad design principles. For T3: what this finding means for practice. Includes design parameter table (visual). | Designers, Clinicians | Yes (T1.5, T2, T3) |
| **Connections** | How this card relates to others. Parent/child in the tier hierarchy. Cross-template interactions. Competition relationships. Molecule membership. Network neighborhood diagram (visual). | Researchers, System users | Yes |
| **Debate** | Competing accounts, unresolved tensions, active frontiers. Who disagrees and why. What evidence would resolve the debate. Argument map (visual). | Researchers | Only if competition exists |
| **History** | Version history of this card. When it was created, when last regenerated, what changed. Diff view showing previous vs. current committed prose. | All users (collapsed by default) | Yes |

#### User-Type Rendering

The tab order and default-open state varies by user type:

| User Type | Default Tab | Tab Order | Hidden Tabs |
|-----------|------------|-----------|-------------|
| **Researcher** | Overview | Overview → Evidence → Mechanism → Connections → Debate → Design → History | None |
| **Designer** | Design | Design → Overview → Mechanism → Evidence → Connections → History | Debate (unless competition exists) |
| **Clinician** | Overview | Overview → Design → Evidence → Mechanism → Connections → History | Debate |
| **Policymaker** | Overview | Overview → Design → Evidence → History | Mechanism, Connections, Debate |

### 3.3 Iceberg (The Depth Layer)

What lies beneath — not visible by default but essential for regeneration, audit, deepening, and provenance.

| Component | Content | Purpose |
|-----------|---------|---------|
| **Source Map** (Zone 3) | Dependency graph: which source cards, T2 templates, T1 frameworks, and molecules back this card | Provenance audit; regeneration trigger |
| **Internal References** | Pointers to master doc sections, specification documents, panel outputs, sprint reports | Context for deepening; "read more" links |
| **External References** | Full APA bibliography with DOIs and Google Scholar citation counts | Academic credibility; citation generation |
| **Raw Data** | The actual database records — T3 beliefs, effect sizes, confidence intervals, scope conditions — that this card synthesizes | Regeneration input; fact-checking |
| **Staleness Ledger** | Dated log of all changes to backing evidence since last regeneration | Determines when to regenerate |
| **Agent Context** | The prompt, model, and parameters used to generate this card's committed prose | Reproducibility; quality improvement |
| **Quality Scores** | Prose health score (§170), confidence calibration, coverage completeness | Quality gate compliance |
| **Diff Archive** | Previous versions of committed prose with annotated diffs | Version comparison; editorial review |

The iceberg is what makes real-time deepening possible. When a user asks "tell me more about this" or "what's the evidence behind this claim," the system doesn't need to search from scratch — it has the full provenance chain, the raw data, and the references already compiled. An Opus-class agent can use the iceberg to regenerate the card's body with greater depth, additional examples, or updated evidence in seconds rather than minutes.

---

## 4. Card-Type-Specific Specifications

### 4.1 T1 Framework Cards (10 cards)

**Surface**: Framework name + core claim as assertion headline. Neural implementation summary. Cross-domain count (how many T1.5 theories and T2 templates this framework grounds).

**Body tabs**:
- **Overview**: The framework's core mechanism in 2-3 paragraphs. What it predicts, why it matters, where it came from.
- **Mechanism**: Neural implementation diagram. Key brain regions, neurotransmitter systems, circuit motifs. Mandatory visual: circuit diagram or anatomical schematic.
- **Evidence**: Multi-method convergence table. Single-cell, fMRI, lesion, computational model, behavioral — check marks for which methods support the framework. Citation count and replication landscape.
- **Design**: Broad architectural implications. What environments should do to work with (not against) this framework. 3-5 design principles with examples.
- **Connections**: Downward links (which T1.5 theories does this framework partially constitute? Which T2 templates does it ground?). Lateral links (which other T1 frameworks interact with this one?). Mandatory visual: network neighborhood diagram showing this T1's position in the web.
- **Debate**: Where the framework is challenged. Known limitations, competing interpretations, boundary conditions.

**Iceberg**: Full list of T1.5 theories with coverage fractions. Full list of T2 templates with bridge warrant types. Panel deliberation records where this framework was discussed.

**Key visual requirements**:
1. Neural circuit diagram (anatomical)
2. Cross-domain evidence convergence chart (methods × domains matrix)
3. Network neighborhood graph (this T1's connections)

### 4.2 T1.5 Domain Theory Cards (13 cards)

**Surface**: Theory name + originator. Core claim as assertion headline. Coverage fraction (what % is explained by T1 frameworks vs. irreducible residual).

**Body tabs**:
- **Overview**: The theory's contribution — what it adds beyond the T1 frameworks that partially explain it. 2-3 paragraphs.
- **Mechanism**: ReductionClaim DAG showing how T1 frameworks combine to produce this theory's predictions. Mandatory visual: DAG with PRODUCES / INHIBITS / CONSTITUTES / MODULATES edges.
- **Evidence**: Empirical support from the backing literature. Key studies, effect sizes, population scope. Meta-analytic summary if available.
- **Design**: Specific design implications that flow from this theory but not from its constituent T1 frameworks alone. The irreducible residual's design consequences.
- **Connections**: Upward (which T1 frameworks constitute it). Downward (which T2 templates operationalize it). Lateral (which other T1.5 theories share constituents). Mandatory visual: tier-cascade diagram.
- **Debate**: Boundary criteria assessment (3 structural tests from T-Levels panel). Score and justification.

**Iceberg**: Full ReductionClaim specification with mutual manipulability evidence. Panel D-1 records. Coverage fractions per T1 framework.

**Key visual requirements**:
1. ReductionClaim DAG
2. Coverage fraction pie chart (T1 contributions + irreducible residual)
3. Tier-cascade diagram

### 4.3 T2 Mechanism Cards (166 cards)

**Surface**: Template ID + assertion headline (the mechanism claim). Calibration status (CALIBRATED / SCAFFOLD). Confidence thermometer. Effect size range.

**Body tabs**:
- **Overview**: The mechanism chain in prose: "When [environmental feature] is present, [neural process] occurs, leading to [psychological outcome] with [effect size range]."
- **Mechanism**: Full mechanism chain with every step parameterized. Mandatory visual: mechanism chain diagram with quantified steps.
- **Evidence**: Source belief summary. N findings from M papers. Forest plot of effect sizes. Warrant type distribution (how many MECHANISM vs. EMPIRICAL_ASSOCIATION vs. ANALOGICAL bridges?). Mandatory visual: forest plot or evidence weight chart.
- **Design**: Specific design parameters. Ranges, optima, boundary conditions, population modifiers. Mandatory visual: parameter table with recommended ranges.
- **Connections**: Parent T1/T1.5 theories. Molecule membership. Cross-template interactions (SYNERGISTIC / ANTAGONISTIC / CONDITIONAL). Competition relationships.
- **Debate**: Competing mechanism accounts. Unresolved questions about boundary conditions or effect moderators.

**Iceberg**: All backing T3 beliefs with full provenance. Credence decomposition (d · ω · δ). Panel calibration records. Sensitivity analysis data.

**Key visual requirements**:
1. Mechanism chain diagram (quantified)
2. Forest plot or evidence weight chart
3. Design parameter table with ranges

### 4.4 Molecule Cards (18 cards)

**Surface**: Molecule name + short description. Type badge (THEORY / MECHANISM / PHENOMENON / DESIGN_PATTERN). Maturity (TENTATIVE → ESTABLISHED). Component count.

**Body tabs**:
- **Overview**: What this molecule is — the co-occurrence pattern, why it matters, what it predicts.
- **Mechanism**: Component architecture. How the constituent templates interact (ADDITIVE / MULTIPLICATIVE / SYNERGISTIC / PREREQUISITE). Mandatory visual: component interaction graph.
- **Evidence**: Empirical support for the co-occurrence pattern. Which studies show these templates co-activating? Study design diversity.
- **Design**: What designing for this molecule means in practice. How to create environments that engage all components simultaneously.
- **Connections**: Constituent T2 templates (with interaction types). Parent T1/T1.5 theories. Functional circuit membership. Mandatory visual: molecule composition diagram.

**Iceberg**: Full molecule JSON from `data/molecules/`. Template interaction matrix. Rasa assignment.

**Key visual requirements**:
1. Component interaction graph
2. Molecule composition diagram (templates as nodes, interaction types as edges)

### 4.5 T3 Belief Cards (12,000+ cards — generated on demand)

**Surface**: Finding assertion as headline. Source article (author, year). Effect size + CI. Warrant type badge. Confidence thermometer.

**Body tabs**:
- **Overview**: One-paragraph summary of what this study found and what it means.
- **Evidence**: Full statistical details. Sample size, design, population, effect size, confidence interval, p-value, replication status. Mandatory visual: effect size with CI (lollipop plot or similar).
- **Design**: If applicable — what this finding implies for practice.
- **Connections**: Which T2 templates this belief supports. Which T1/T1.5 theories it connects to (via bridge warrants). Scope conditions. Mandatory visual: belief's position in the web (local neighborhood).

**Iceberg**: Full extraction record. DOI. Article family. Quality action status. Reflex check results. Annotation history.

**Key visual requirements**:
1. Effect size with CI visualization
2. Web neighborhood diagram

### 4.6 Competition Cards (~120 cards — generated on demand)

**Surface**: Competition title. Competing accounts listed. Resolution status (VICTORY / COMPROMISE / EQUILIBRIUM / UNRESOLVED).

**Body tabs**:
- **Overview**: What's being debated and why it matters.
- **Evidence**: Evidence for each side. Comparative strength assessment. Mandatory visual: argument map (pro/con structure).
- **Debate**: Full Toulmin analysis for each account. Data, warrants, backing, qualifiers, rebuttals. Resolution threshold analysis.
- **Connections**: Which templates/theories are affected by the outcome. Downstream credence implications.

**Iceberg**: Full argumentation graph records. Panel deliberation transcripts. Critical questions addressed/unaddressed.

**Key visual requirements**:
1. Argument map (pro/con/rebuttal structure)
2. Evidence comparison chart

### 4.7 Layer Cards (~12 cards)

These explain ATLAS's own architecture. Each major system layer gets a card.

**Layers requiring cards**:
1. Extraction Module (article → structured data)
2. Web of Belief (coherence engine)
3. Bayesian Network (causal inference)
4. Credence Propagation (algorithms 1-6)
5. Interpretation Space (question taxonomy, routing)
6. Annotation Layer (20 annotation types)
7. Argumentation System (Toulmin, competitions)
8. Expert Panels (simulated deliberation)
9. QA Pipeline (question → answer)
10. Prose Revision Service (writing quality)
11. Card Architecture (this very system)
12. Agent Coordination (multi-agent orchestration)

**Body tabs**:
- **Overview**: What this layer does in 2-3 paragraphs. Its role in the overall system.
- **Mechanism**: How it works. Architecture diagram. Key data flows. Mandatory visual: system architecture diagram.
- **Justification**: Why this layer exists. The theoretical/engineering decision that led to it. References to epistemological literature that grounds it.
- **Connections**: What feeds into it, what it produces, which other layers it depends on.
- **Implementation**: Current code status. Key files, line counts, test counts.

**Iceberg**: Master doc section references. Design decision log entries. Sprint completion reports.

### 4.8 Method Cards (~20 cards)

These explain specific algorithms, processes, or decisions within the system.

**Methods requiring cards** (non-exhaustive):
1. Typed Credence Propagation (Algorithm 1)
2. Graded Competition Resolution (Algorithm 2)
3. Typed Global Coherence Metric (Algorithm 3)
4. AGM-Style Structural Revision (Algorithm 4)
5. Value of Information (Algorithm 5)
6. BN Projection (Algorithm 6)
7. Log-Odds Projection Calculus (credence formula)
8. Quinean Entrenchment (rate limits)
9. Noisy-OR vs. Max Combination
10. ReductionClaim DAG (T1.5 decomposition)
11. Reflex System (13 extraction hygiene checks)
12. Staleness Scoring (card regeneration trigger)
13. Bridge Warrant Assignment
14. Molecule Discovery (co-occurrence clustering)
15. Question Routing (interpretation layer)

**Body tabs**:
- **Overview**: What this method does and why.
- **Mechanism**: The algorithm itself — pseudocode, step-by-step explanation, complexity analysis. Mandatory visual: flowchart or decision diagram.
- **Justification**: Philosophical and engineering rationale. Why this approach over alternatives. (This is exactly what the §129.2 fattening insert covers.)
- **Examples**: 2-3 worked examples showing the method in action. Mandatory visual: annotated example.
- **Sensitivity**: How sensitive is the output to parameter choices? Which parameters are high-leverage?

**Iceberg**: Full algorithm specification. Retrodiction test results. Panel review records. Parameter sensitivity analysis data.

---

## 5. Visual Requirements Summary

Every card type specifies mandatory visuals. The full visual catalog:

| Visual Type | Used In | Rendering Method | Count |
|-------------|---------|-----------------|-------|
| **Mechanism chain diagram** | T2, T1 | Mermaid / SVG | ~170 |
| **ReductionClaim DAG** | T1.5 | Mermaid / SVG | 13 |
| **Network neighborhood graph** | T1, T3, Competition | D3 / networkx → SVG | ~150+ |
| **Forest plot / evidence chart** | T2, T3 | matplotlib / plotly | ~170 |
| **Coverage fraction pie chart** | T1.5 | matplotlib | 13 |
| **Component interaction graph** | Molecule | D3 / networkx → SVG | 18 |
| **Argument map** | Competition | Mermaid / custom | ~120 |
| **System architecture diagram** | Layer | Mermaid / SVG | 12 |
| **Design parameter table** | T2 | HTML table / SVG | ~170 |
| **Effect size with CI** | T3 | matplotlib / plotly | On-demand |
| **Flowchart / decision diagram** | Method | Mermaid / SVG | ~20 |
| **Annotated worked example** | Method | Custom / LaTeX → SVG | ~40 |

**Priority**: Mechanism chain diagrams (T2) and ReductionClaim DAGs (T1.5) are the highest-value visuals — they communicate the system's core theoretical content more efficiently than prose alone.

---

## 6. The Science Agent and Card Regeneration

David has asked AG to build agents that can replace fixed services. The card system is a prime candidate for agent-based architecture because:

1. **Card generation requires judgment** — synthesizing evidence, weighing competing accounts, choosing what to emphasize — not just template filling.
2. **Different card types need different expertise** — T1 cards need deep theoretical knowledge (Opus-class); T3 cards need statistical precision (Sonnet-class); system cards need engineering clarity (either).
3. **Regeneration is event-driven** — cards regenerate when staleness exceeds threshold, not on a fixed schedule.
4. **The iceberg makes agents efficient** — by providing the full provenance chain and raw data, the iceberg allows an agent to regenerate a card without re-searching the entire database.

### Proposed Agent Architecture

| Agent | Role | Model | Trigger |
|-------|------|-------|---------|
| **Theoretical Card Agent** | Generates/regenerates T1, T1.5, and theoretical method cards | Opus | Staleness > 0.40 on theoretical loci |
| **Evidence Card Agent** | Generates/regenerates T2, T3, and competition cards | Sonnet | Staleness > 0.40 on evidence loci; new paper integration |
| **System Card Agent** | Generates/regenerates layer and method cards | Sonnet | Code changes to relevant subsystems |
| **Visual Agent** | Generates/updates all card visuals | Sonnet | Card regeneration triggers visual refresh |
| **Reference Verification Agent** | Validates all citations in Opus-generated cards | Sonnet/Haiku | Post-generation quality gate |
| **Master Doc Update Agent** | Propagates card content changes back to master doc sections | Opus | Card regeneration that affects master doc coverage |

### Coordination with AG

AG should be the authority on agent lifecycle, state management, and orchestration. The card system needs to:
1. Register card types as agent-manageable artifacts
2. Define staleness triggers that AG's scheduler can monitor
3. Provide iceberg data in a format agents can consume
4. Accept regenerated cards through a validation gate before committing

**Question for David**: Is AG's Opus the same model as this session's Opus? If so, the theoretical card agent can produce prose at the same quality level as master doc fattening inserts. If not (e.g., AG uses a different Opus instance or version), we should run a comparison.

---

## 7. Master Doc Gaps to Fill

The audit identified five documentation gaps that should be addressed as Part of the card specification work. Each becomes a new master doc section:

| Gap | Proposed Section | Part | Priority |
|-----|-----------------|------|----------|
| **Molecules inventory** | §174: The 18 Molecules — Latent Variables in the ATLAS Web | XXVI (new) | HIGH |
| **Annotation layer** | §175: The Annotation Layer — 20 Types, Schema, and Enrichment Protocol | XXVI | HIGH |
| **Interpretation space taxonomy** | §176: The Interpretation Space — Question Types, Routing, and Gap Discovery | XXVI | HIGH |
| **Card system full specification** | §177: The Card System — Types, Schema, Tabs, Visuals, and Iceberg | XXVI | HIGH |
| **System architecture overview** | §178: ATLAS System Architecture — A Layer-by-Layer Guide | XXVI | MEDIUM |

These five sections would constitute **Part XXVI: System Presentation and Knowledge Artifacts** — the Part that explains how ATLAS presents what it knows.

---

## 8. Execution Plan

### Phase 1: Card Schema Specification (Code) — 1-2 sessions

**Deliverables**:
- `src/cards/card_schema.py` — Universal card schema (surface, body tabs, iceberg) as Python dataclasses
- `src/cards/card_types.py` — Type-specific schemas for all 8 card types
- `src/cards/tab_config.py` — User-type-specific tab ordering and visibility
- `src/cards/staleness.py` — Staleness scoring implementation (from §173.4 spec)
- `contracts/schemas/card_system.v1.schema.json` — JSON schema for card serialization
- Tests: ~80 tests covering schema validation, tab ordering, staleness scoring

### Phase 2: Master Doc Part XXVI — 1-2 sessions

**Deliverables**:
- §174: Molecules inventory (~2,000 words)
- §175: Annotation layer specification (~2,500 words)
- §176: Interpretation space taxonomy (~2,000 words)
- §177: Card system specification (~4,000 words, incorporating this plan's content)
- §178: System architecture overview (~3,000 words)
- Total: ~13,500 words in Part XXVI

### Phase 3: Precompute Tier A Cards — 2-3 sessions

**Deliverables**:
- 10 T1 Framework Cards (Opus-generated, reference-verified)
- 13 T1.5 Domain Theory Cards (Opus-generated, reference-verified)
- 18 Molecule Cards (Sonnet-generated)
- ~30 exemplar T2 Mechanism Cards (Sonnet-generated — representative sample across domains)
- 12 Layer Cards (Sonnet-generated)
- 15 Method Cards (Opus for theoretical justification, Sonnet for algorithm specification)
- Stored in `data/cards/` as JSON with full iceberg

### Phase 4: Visual Generation — 1-2 sessions (parallelizable with Phase 3)

**Deliverables**:
- 13 ReductionClaim DAGs (one per T1.5 theory)
- 10 T1 network neighborhood diagrams
- 30 T2 mechanism chain diagrams (exemplar set)
- 18 molecule composition diagrams
- 12 system architecture diagrams (one per layer)
- Stored in `docs/figures/cards/` as SVG

### Phase 5: Agent Integration — 1 session (requires AG coordination)

**Deliverables**:
- Card agent registration in AG's orchestrator
- Staleness monitoring integration
- Regeneration trigger wiring
- Quality gate for Opus outputs (reference verification)
- Master doc update propagation

---

## 9. Open Questions for David

1. **Tab architecture**: Is the 7-tab structure (Overview, Mechanism, Evidence, Design, Connections, Debate, History) right, or do you want different/additional tabs? In particular, should there be a "Teaching" tab aimed at students?

2. **User types**: The current 4 types (researcher, clinician, designer, policymaker) come from the existing `answer_renderer.py`. Should we add "student" (3rd-year undergrad) and "system developer" (someone extending ATLAS)?

3. **Visual priority**: Which visuals should we generate first? I'd recommend ReductionClaim DAGs (T1.5) and mechanism chain diagrams (T2) because they communicate the most unique content. But if you want system architecture diagrams first (for the "explain the system clearly" goal), those should come first.

4. **AG coordination timing**: Should I start Phase 1 (code specification) now and coordinate with AG later, or wait until the agent architecture is designed jointly?

5. **Card storage format**: JSON files in `data/cards/`? SQLite table? Both (JSON as source of truth, SQLite as indexed lookup)?

6. **Scope of "all possible questions"**: When you say cards should cover answers to "all possible questions," do you mean: (a) every question the interpretation space can route (the 2,680-line taxonomy), or (b) every question a reasonable user might ask about ATLAS and its domain, which is potentially unbounded? The former is tractable; the latter requires a discovery mechanism.

---

## 10. Addendum: David's Decisions + AG Gap Integration (4 March 2026, evening)

### 10.1 David's Answers to Open Questions

1. **User types**: Student YES, Developer YES (hidden, login-gated). Total: 6 user types (researcher, clinician, designer, policymaker, student, developer).
2. **Visuals**: ReductionClaim DAGs and system architecture diagrams both needed. System architecture needs blowups for specific areas.
3. **Phase 1 timing**: Proceed now, coordinate with AG on agent architecture in parallel.
4. **Math Cards**: NEW CARD TYPE added to taxonomy (see §10.3 below).

### 10.2 AG Gap Analysis Integration

AG's end-to-end wiring audit (March 2026) identified critical gaps that reshape our execution priorities:

**Working now**: Molecule cards → Streamlit (L1 visible, L2/L3 pending); Cluster cards → QA handler (<50ms). AG wired CardRetriever + fixed nightly pipeline.

**Not wired**:
- Archetype cards written to qa_cache but no router path reads them
- Meta-reviews: MetaReviewGenerator exists but zero reviews generated (empty dir)
- Convergence zone sheets: not designed, not built
- Warrant explanations: computed but no card/viewer renders them in plain English
- Interactive features: no drill-down from cluster card → individual findings

**Three systems NOT documented in master doc or AG's work**:
- **Annotation system** (25 types across 3 parallel unintegrated layers) — NOT consumed by QA pipeline. This is severe: annotations exist but nothing reads them.
- **Argumentation system** (900 LOC) — documented only as "R₁ rule set" inside Interpretation Space spec. No standalone spec or integration guide.
- **Interpretation space** (85KB conceptual spec + 300 LOC implementation) — gap between ambitious theory and modest code is the largest disconnect in the system.

### 10.3 Math Cards: New Card Type (David's Requirement)

**Card Type 9: Math Card** (~25-30 cards)

Every equation, algorithm, or formal method in ATLAS gets a card with a distinctive three-layer explanation structure:

**Tab 1 — Intuition** (all users): Science-writer explanation of what the math *does* and *why it matters*. No equations. Uses analogies, concrete examples, and visual metaphors. Written to Strogatz/Devlin standard (per MATH_EXPLANATION_NORMS.md). Mandatory visual: conceptual diagram or analogy illustration.

**Tab 2 — Transparent Explanation** (researchers, students): The equation itself, explained step by step. Each symbol defined. Each term justified. "Here is the equation; here is what each piece means; here is why each piece is there." Written so a graduate student in cognitive science can follow it. Mandatory visual: annotated equation with color-coded terms.

**Tab 3 — Details** (technical readers, developers): Full formal specification. Proofs, derivations, sensitivity analyses, boundary conditions, computational complexity. References to the epistemological literature that grounds each design choice (Toulmin on warrant strength, Pollock on defeasibility, etc.). This is what the §129.2 fattening inserts provide.

**Math Cards needed** (non-exhaustive):
1. Log-odds projection calculus (p_target = logit⁻¹(logit(p_lab) + log(d·ω·δ)))
2. Typed credence propagation (Algorithm 1)
3. Graded competition resolution (Algorithm 2)
4. Typed global coherence metric (Algorithm 3)
5. AGM-style structural revision (Algorithm 4)
6. Value of information (Algorithm 5)
7. BN projection (Algorithm 6)
8. Noisy-OR vs. max combination rules
9. Quinean entrenchment rate limits
10. Staleness scoring function
11. Bridge warrant hierarchy (α table)
12. CCI (Complete Chain Index) metric
13. AESHI scoring formula (6 subscores)
14. Effect size conversion (d → OR → RR)
15. Population transfer factor (δ computation)
16. Warrant strength (ω assessment)
17. Coherence-weighted confidence
18. Molecule discovery (co-occurrence clustering)
19. VOI scoring function
20. ReductionClaim coverage fraction computation

### 10.4 Revised Part XXVI Scope

Part XXVI now covers 7 sections (expanded from 5):

| Section | Title | Words (est.) | Priority |
|---------|-------|-------------|----------|
| §174 | The 18 Molecules — Latent Variables in the ATLAS Web | ~2,500 | HIGH |
| §175 | The Annotation Layer — 25 Types, Three Layers, and the Integration Problem | ~2,500 | HIGH |
| §176 | The Interpretation Space — Four Epistemic Zones, Question Taxonomy, and Gap Discovery | ~3,000 | HIGH |
| §177 | The Argumentation System — Walton Schemes, Citation Structure, and Debate Resolution | ~2,000 | HIGH |
| §178 | The Card System — 9 Types, Universal Schema, Tabs, Visuals, and Iceberg | ~4,000 | HIGH |
| §179 | Math Cards — The Three-Layer Explanation Architecture | ~2,000 | HIGH |
| §180 | ATLAS System Architecture — A Layer-by-Layer Guide with Blowup Diagrams | ~3,500 | MEDIUM |

Total: ~19,500 words in Part XXVI. This is a major documentation campaign.

### 10.5 Revised Execution Priority

Given AG's gap analysis and David's requirements, the execution order is:

1. **Write Part XXVI** (§174-§180) — fill the documentation gaps NOW
2. **Generate meta-reviews** (3,788 clusters, no LLM, ~15 min) — unblocks convergence zones
3. **Wire archetype cards to router** — quick win, code exists
4. **Code card schema** (Phase 1 from original plan) — in parallel with AG agent architecture
5. **Precompute cards** (Phase 3) — starts with 10 T1 + 13 T1.5 + 20 Math Cards
6. **Visual generation** (Phase 4) — ReductionClaim DAGs first, then system architecture
7. **Agent integration** (Phase 5) — coordinate with AG
8. **Test agent quality** — run science advisor comparison

---

## 11. What This Plan Does NOT Cover (Future Work)

- **Interactive card UI** — This plan specifies card content and schema but not the rendering frontend (web app, Streamlit, etc.)
- **Real-time card deepening** — The iceberg supports it architecturally, but the conversational interface for "tell me more" is an AG-level feature
- **Card-to-card navigation** — The Connections tab provides links, but a full hyperlinked knowledge graph browser is a separate project
- **Automated visual generation from data** — Phase 4 generates visuals manually; automated visual pipelines (e.g., auto-generating forest plots from T3 data) would be Phase 6

---

## References

Aristotle. (~350 BCE). *Topics*, Book I. [Translated by W. A. Pickard-Cambridge, in *The Complete Works of Aristotle*, ed. J. Barnes, Princeton University Press, 1984.]

Quine, W. V. O. (1951). Two dogmas of empiricism. *Philosophical Review*, 60(1), 20–43. [~15,000 GS]

Sword, H. (2012). *Stylish academic writing*. Harvard University Press. [~1,500 GS]

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press. [~15,000 GS]

Tufte, E. R. (2001). *The visual display of quantitative information* (2nd ed.). Graphics Press. [~15,000 GS]
