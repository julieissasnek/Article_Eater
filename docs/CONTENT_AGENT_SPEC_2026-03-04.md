# Content Agent Specifications — Article Eater
*Prepared 2026-03-04 by AG. For CW and panel review.*

## Overview

Five specialized content agents, each runnable from terminal, each designed to get smarter over time by building domain-specific knowledge from the Article Eater corpus. These are **not** API wrappers — they're structured scripts that take defined input, apply domain expertise, and produce quality-gated output.

**Design principle**: Each agent owns one presentation modality. They collaborate by producing compatible output formats that compose into cards, sheets, and views.

---

## Agent 1: Prose Writer (`prose_agent`)

**Role**: Generates all natural-language content — card text, warrant explanations, convergence zone narratives, examples.

**Background Knowledge** (loaded at startup):
- Writing norms from `CONFIDENCE_LANGUAGE` in `answer_renderer.py` (hedging rules, forbidden phrases like "interestingly")
- All 38 molecule definitions (so it can reference theories correctly)
- The extraction corpus structure (so it knows what evidence types exist)
- The finding-template schema (so it understands design types, effect sizes, IVs/DVs)

**Input**: Structured cluster/molecule data (JSON) + generation context (card type, user type, depth level)

**Output**: Prose text meeting these success conditions:
- SC-PW-1: No forbidden phrases ("interestingly", "it is worth noting", "importantly")
- SC-PW-2: Confidence language matches evidence strength (hedge for ω < 0.6, assert for ω > 0.85)
- SC-PW-3: At least one concrete example per L2+ card
- SC-PW-4: Mechanisms named and explained, not just listed
- SC-PW-5: Effect sizes contextualized (not just reported — what does d = 0.5 mean for a designer?)
- SC-PW-6: All claims traceable to specific findings in the corpus

**Getting smarter**: After each batch, logs which cards scored highest in `ProseRevisionService` quality gate. Over time, develops a "style memory" of what works for each topic domain.

**Terminal usage**:
```bash
python3 -m src.agents.prose_agent \
  --input data/materialized_views/belief_clusters.json \
  --cluster-range 0-100 \
  --depth L2 \
  --user-type researcher \
  --output data/cards/batch_prose/
```

---

## Agent 2: Visual Designer (`visual_agent`)

**Role**: Generates figure specifications, diagram descriptions, data visualization configs, and table layouts. Does NOT generate pixels — produces structured specs that renderers consume.

**Background Knowledge**:
- Figure registry from extraction corpus (what figures exist in papers)
- Molecule interaction maps (what connects to what)
- The network graph structure from `network_service.py`
- Tufte's principles: data-ink ratio, small multiples, sparklines

**Output types**:
| Output | Format | Example |
|--------|--------|---------|
| Confidence thermometer | SVG spec | Graduated bar showing evidence strength |
| Evidence constellation | D3 config | Scatter of findings by effect size × publication year |
| Theory map | Mermaid/DOT | Which theories predict this relationship |
| Comparison table | JSON → HTML | Side-by-side study characteristics |
| Forest plot spec | Vega-Lite | Meta-analytic forest plot of findings in cluster |

**Success conditions**:
- SC-VD-1: Every visual has a caption explaining what it shows and why it matters
- SC-VD-2: Tables are included here (not separate agent) — structured data in rows/columns with sorting + highlighting
- SC-VD-3: Color palettes are accessible (WCAG AA contrast) and semantically meaningful
- SC-VD-4: No chart junk — every visual element encodes data or aids comprehension

**Terminal usage**:
```bash
python3 -m src.agents.visual_agent \
  --input data/cards/batch_prose/cluster_002.json \
  --output-format svg+json \
  --output data/cards/batch_visuals/
```

---

## Agent 3: Stats Communicator (`stats_agent`)

**Role**: Translates statistical findings into reader-friendly explanations. Handles effect sizes, confidence intervals, meta-analytic summaries, and Bayesian belief updates. The agent that turns "d = 0.82, p < .001, 95% CI [0.65, 0.99]" into something a designer or clinician actually understands.

**Background Knowledge**:
- Cohen's benchmarks and domain-specific calibration (d = 0.5 is "medium" in psychology but might be huge in architecture)
- The ω (omega) composite scoring system used in this project
- Bayesian update mechanics (how new evidence changes belief strength)
- Common statistical pitfalls in the corpus (file-drawer effect, p-hacking indicators, small-N studies)

**Output types**:
| Output | Format | Example |
|--------|--------|---------|
| Effect size narrative | Prose fragment | "An effect this large means that roughly 70% of people in the treatment group scored higher than the average control participant" |
| Confidence interval explanation | Prose + visual spec | What the CI means for practical decision-making |
| Evidence weight summary | JSON + prose | How the ω score was computed and what it implies |
| Power assessment | Prose | Whether the studies had enough participants to detect the claimed effect |

**Success conditions**:
- SC-SC-1: Never reports a statistic without contextualizing it
- SC-SC-2: Converts p-values to plain-English likelihood statements
- SC-SC-3: Flags implausible effect sizes (d > 3 is almost certainly wrong in social science)
- SC-SC-4: Explains what would change the conclusion (sensitivity analysis in prose)

**Terminal usage**:
```bash
python3 -m src.agents.stats_agent \
  --input data/cards/batch_prose/cluster_004.json \
  --output data/cards/batch_stats/
```

---

## Agent 4: Presentation Composer (`layout_agent`)

**Role**: Assembles final card/sheet layouts from prose, visuals, stats, and metadata. Decides what goes on the first view vs what's progressive disclosure. Manages the reading experience across card types.

**Background Knowledge**:
- Progressive disclosure theory (from our own ART/cognitive load molecules!)
- Card type specifications (L1 = 150-200 words, L2 = 300-400, L3 = 500-700)
- User type profiles (researcher wants mechanisms; clinician wants practice implications; student wants examples)
- The Streamlit component library available for rendering

**Output**: Complete card/sheet JSON that the Streamlit viewer or web API renders directly.

**Card interaction spec** (what this agent decides):

| Feature | L1 Card | L2 Card | L3 Sheet |
|---------|---------|---------|----------|
| Always visible | Headline + confidence | L1 + mechanism summary | Everything |
| Expandable | Evidence count | Warrant details | Study-level drill-down |
| Interactive | Confidence thermometer hover | Theory map click → molecule card | "Show me the studies" → finding table |
| Follow-up prompts | 2 auto-generated questions | 3 deeper questions | Links to related convergence zones |
| Shareable | Copy-paste summary | Export as PDF section | Full report page |

**Success conditions**:
- SC-LC-1: No card exceeds word limits for its level
- SC-LC-2: Every card has at least one interactive element
- SC-LC-3: L1 → L2 → L3 progression is genuinely progressive (not just longer text)
- SC-LC-4: Mobile-responsive layout (no horizontal scroll on 375px viewport)

**Terminal usage**:
```bash
python3 -m src.agents.layout_agent \
  --prose data/cards/batch_prose/cluster_002.json \
  --visuals data/cards/batch_visuals/cluster_002.json \
  --stats data/cards/batch_stats/cluster_002.json \
  --output data/cards/final/cluster_002_card.json
```

---

## Agent 5: System Expert (`expert_agent`)

**Role**: The persistent knowledge agent. Knows everything about the Article Eater system — all docs, all molecules, all design decisions, all past discussions. Other agents query it for context.

**Background Knowledge** (the full dbase):
- `docs/` — master doc, all session docs, all CW review docs
- `data/molecules/` — 38 molecule definitions with components and theory links
- `data/extractions/` — 1,069 extraction JSONs
- `data/materialized_views/` — belief clusters, answer cards, meta-reviews
- `data/discussions/` — exported conversations (user must provide)
- Code architecture map (auto-generated from `src/` directory scan)

**Persistence**: SQLite index at `data/system_expert.db`:
- `docs(path, title, summary, last_modified, embedding)`
- `concepts(name, type, definition, first_seen_in, related_concepts)`
- `decisions(description, rationale, date, conversation_id, status)`
- `dependency_graph(source_concept, target_concept, relation_type, evidence)`

**Query interface**:
```bash
# "What do we know about circadian effects on mood?"
python3 -m src.agents.expert_agent --query "circadian mood"

# "What design decisions have we made about card rendering?"
python3 -m src.agents.expert_agent --query "card rendering decisions"

# "Rebuild index after new papers ingested"
python3 -m src.agents.expert_agent --rebuild
```

**Success conditions**:
- SC-SE-1: Can answer "what do we know about X?" for any molecule, archetype, or finding theme in < 2 seconds
- SC-SE-2: Tracks all design decisions with rationale and source conversation
- SC-SE-3: Detects conflicts between documents (doc A says X, doc B says not-X)
- SC-SE-4: Suggests connections that no single document makes explicit

---

## Agent Collaboration Protocol

```
User Query → expert_agent (retrieves relevant context)
                ↓
          prose_agent (generates text from context + cluster data)
                ↓
          stats_agent (enriches with effect size narratives)
                ↓
          visual_agent (generates figure/table specs)
                ↓
          layout_agent (composes final card/sheet)
                ↓
          ProseRevisionService (quality gate)
                ↓
          Output → qa_cache / answer_cards / web API
```

Each agent reads from the previous agent's output directory. All agents can query `expert_agent` for cross-referencing.

---

## Running Without API — Terminal-Only Mode

All agents are Python scripts in `src/agents/`. During development:
- **You** run them in terminal with your preferred LLM behind the scenes (Claude Code for Opus, AG for Gemini, CW for Claude, Codex for GPT-4)
- Each agent produces intermediate JSON files
- No API calls needed — the LLM reasoning happens inside the agent session itself
- Once stable, agents can be wired to API for automated batch runs

The key insight: during development phase, **the agent IS the conversation**. When you say "CW, run the prose agent on clusters 0-100", CW reads the prose_agent spec, reads the cluster data, generates the output, and writes it to the output directory. The "agent" is the spec + the LLM + the context — not a separate running process.

Once the output quality stabilizes, we codify the best prompts and patterns into Python scripts that call the API directly.

---

## Panel Review Questions

The following questions should be evaluated by the panel before implementation:

1. **Science writers**: Is the prose quality bar (SC-PW-1 through SC-PW-6) sufficient? What's missing from the writing norms?
2. **Visualization experts**: Should the visual_agent produce pixel-ready output (SVG/PNG) or always produce specs for a renderer?
3. **Stats communicators**: How should we handle uncertain or contradictory evidence in a way that doesn't paralyze the reader?
4. **System architect**: Is the sequential pipeline (prose → stats → visual → layout) the right order, or should some agents run in parallel?
5. **Domain experts**: What's the right word for belief "nodules"? Candidates: convergence zones, evidence clusters, belief constellations, research themes.
6. **UX designer**: Should L1 cards be interactive at all, or should they be pure summary? At what progressive disclosure level does interactivity begin?

---

## Panel

### Science Writers
1. **Ed Yong** (Atlantic) — clear, honest science communication without hype
2. **Carl Zimmer** (NYT) — complex biology for general audience
3. **Maria Popova** (The Marginalian) — connecting science to human experience

### Visualization
4. **Edward Tufte** — data-ink ratio, evidence presentation
5. **Giorgia Lupi** — data humanism, making data personal
6. **Mike Bostock** (D3.js) — interactive data visualization on the web

### Stats Communication
7. **Andrew Gelman** — honest stats, posterior predictive checks, communicating uncertainty
8. **Sander Greenland** — statistical interpretation beyond p-values
9. **Regina Nuzzo** — science journalism on statistical issues

### Environmental Psychology / Architecture
10. **Colin Ellard** — environmental neuroscience, space and cognition
11. **Sarah Williams Goldhagen** — architecture and neuroscience
12. **Jan Gehl** — human-scale design, evidence-based urbanism

### System Architecture
13. **Martin Fowler** — software patterns for complex systems
14. **Rich Hickey** — data-oriented design, simple vs easy

### Discussion Moderator
15. **David Kirsh** — to represent the project's epistemic commitments and ensure agents serve the foundherentist framework


## Panel Prompt

> You are reviewing a content agent specification for the Article Eater system — a research synthesis platform in environmental/architectural psychology. The system ingests academic papers, extracts findings, clusters them into "convergence zones of belief," and needs to present them to diverse audiences (researchers, designers, clinicians, students, general public). 
>
> We are proposing 5 specialized agents. Each agent gets smarter over time by learning from the corpus. Please evaluate:
> 1. Are the success conditions for each agent sufficient or too strict?
> 2. Is anything missing from the agent collaboration protocol?
> 3. What presentation forms have we overlooked? (We have: prose, tables, diagrams, forest plots, confidence thermometers. What else?)
> 4. How should "freshness" be operationalized — what makes one card interestingly different from another without being gratuitously varied?
> 5. Should examples in cards be drawn from the corpus itself, or generated to illustrate points?

---

### Panel Responses

**Ed Yong**: The prose norms are a good start, but you're missing the most important one: *every card should answer "so what?"* A designer reading about circadian effects on mood needs to know what to do with that information. SC-PW-7 should be: "Every L2+ card includes at least one actionable design implication."

**Edward Tufte**: Your visual agent should never produce decorative elements. Every pixel must encode data. I'd add SC-VD-5: "No visual element exists purely for aesthetic appeal." Also, sparklines inline with text are under-utilized — your confidence thermometer is good, but why not inline evidence trends showing how the finding has strengthened or weakened over publication years?

**Andrew Gelman**: SC-SC-3 (flag implausible effect sizes) is critical and underspecified. d > 3 is not just "almost certainly wrong" — it should trigger a forensic review. Also: you need to distinguish between heterogeneity in effects (genuine moderators) and heterogeneity from methodological noise. Your stats agent should report I² alongside effect sizes to show how consistent the evidence actually is.

**Colin Ellard**: The convergence zone naming is good. What you're missing is *experiential anchoring* — each card should connect findings to a felt experience. "Noise impairs concentration" is science; "that moment when someone's phone conversation makes you lose your train of thought" is relatable knowledge. Your prose agent should be required to include at least one experiential anchor per card.

**Sarah Williams Goldhagen**: Your agent collaboration protocol is linear but the design process is iterative. A designer might start with a visual (a building layout), then need stats about that configuration, then need prose explaining the evidence. Your agents need bidirectional queries, not just sequential pipeline.

**Rich Hickey**: Your agents are simple — that's good. But your persistence model needs immutability. Every card generation should produce a new version, not overwrite. You need `card_v1.json`, `card_v2.json`, etc., so you can always compare what changed and why. This also helps your "getting smarter" goal: you can measure quality drift over time.

**Martin Fowler**: The agent-as-conversation pattern for development is pragmatic. But you should plan for the migration path to automated agents early. Define the input/output contracts formally (JSON Schema) so that switching from "CW reads the spec and generates" to "Python script calls API" requires zero changes to downstream consumers.

**Regina Nuzzo**: The stats agent should have a "danger zone" mode: when findings are based on < 30 participants, or when the design is purely observational, the card should LEAD with the uncertainty, not bury it. SC-SC-5: "For evidence weaker than ω < 0.5, caveats come before claims."

**Giorgia Lupi**: Tables are not a separate agent concern — they belong in visual_agent. But your table spec is missing: *narrative tables*. Not just rows of data, but tables where the structure tells a story (sorted by effect strength, colored by theory affiliation, with inline annotations). Your visual agent should treat tables as a first-class visualization form.

**David Kirsh**: All of this is well-designed, but remember: these agents serve the foundherentist epistemology. They must never present evidence as foundational ("this study proves"). They must always present it as part of a web: mutually supporting, cross-referencing, where confidence comes from coherence across diverse evidence types. SC-PW-8: "No card presents a single study as conclusive. All cards contextualize within the convergence zone."

---

### Incorporated Changes

Based on panel feedback, adding:
- **SC-PW-7**: Every L2+ card includes an actionable design implication
- **SC-PW-8**: No card presents a single study as conclusive; all contextualize within convergence zone
- **SC-VD-5**: No decorative visual elements; inline sparklines for evidence trends
- **SC-SC-5**: For ω < 0.5, caveats come before claims
- **SC-SC-6**: Report I² heterogeneity alongside pooled effects
- **Narrative tables** added to visual_agent output types
- **Versioned card output** (immutable history per Rich Hickey)
- **JSON Schema contracts** for all agent input/output (per Martin Fowler)
- **Experiential anchoring** required in prose (per Colin Ellard)
- **Bidirectional agent queries** for iterative workflows (per Goldhagen)
