# PANEL CONSULTATION IV — Outside Eyes
## "From Philosophical Metaphor to Computational Architecture"
## Convened: February 25, 2026 | Purpose: Genuinely different perspectives

---

## Panel Composition

1. **Elias Bareinboim** (Columbia) — Pearl's most prominent student; expert on causal transportability, data fusion, external validity. Would see problems in the web-to-BN projection that Pearl himself might not flag because Bareinboim has extended do-calculus in directions that intersect the paper's claims.

2. **Nancy Nersessian** (Georgia Tech) — Cognitive science of science; model-based reasoning. Studies how scientists *actually* construct and reason with models, as opposed to how philosophers say they should. Would confront the paper with the gap between the formal account and the messy reality.

3. **Melanie Mitchell** (Santa Fe Institute) — Complexity science, AI, analogy. Her book *Artificial Intelligence: A Guide for Thinking Humans* (2019) and her work on analogy in AI systems intersect the ANALOGICAL bridge warrant type directly. Would ask what the system knows about its own limitations.

4. **Michael Nielsen** (metascience, collective intelligence) — Physicist turned metascience researcher; *Reinventing Discovery* (2011) on how scientific communities generate knowledge through collective computation. Would see the panel process as a collective intelligence system and ask whether it has the right structural properties.

5. **Harry Francis Mallgrave** (Illinois Institute of Technology) — Architectural theorist and historian; *Architecture and Embodiment* (2013) is the most sophisticated existing treatment of neuroscience-architecture connections. This is someone from the paper's actual target domain. Would tell us whether the system captures anything that matters.

---

## Round Table: What Do You See That the Philosophers Missed?

---

### Elias Bareinboim — "Your projection function has a transportability problem."

The paper's Algorithm 6 projects the web into a Bayesian network. The BN then computes interventional predictions. But intervening *where*? The CMR's templates are calibrated from laboratory studies, field studies across various buildings, and expert judgment. The architect wants to know what will happen in *this specific building* with *these specific occupants*. That is a transportability problem.

In my work on causal transportability (Bareinboim & Pearl, 2016), I've shown that interventional predictions derived from one population (the study population) are valid for another population (the target population) only when specific graphical conditions hold — when the causal mechanisms that differ between populations are identifiable and controllable. The web's qualifier fields ("effect strongest for morning light in buildings with high spatial complexity") are informal transportability conditions: they specify where the mechanism chain applies. But the BN projection (Algorithm 6) does not formally encode these conditions. The resulting BN computes interventional predictions as if the study population and the target population are the same — which they never are.

This is not a minor issue. An architect in Oslo and an architect in Singapore will get the same BN predictions for daylight → mood, even though the populations differ in light exposure history, circadian adaptation, cultural relationship to indoor/outdoor space, and thermal expectations. The web *knows* about these differences (the qualifiers, the AX5 cultural modulation axiom, the AX3 individual differences parameters), but the BN projection *discards* most of this information.

**Recommendation**: The paper should acknowledge the transportability problem explicitly and suggest that Algorithm 6 be extended to produce a *family* of BNs — one for each target context — rather than a single BN. The qualifier fields in the web's Toulmin structures are the raw material for transportability conditions: they specify where the mechanism chain applies and where it breaks down. A context-sensitive projection function that generates context-specific BNs from the web's qualifier fields would be a significant extension. The paper doesn't need to implement this, but it should name the problem and sketch the solution, because any serious causal inference person who reads the paper will notice the gap.

**Suggested addition**: "A limitation of the current projection function is that it generates a single BN regardless of the target context. In practice, interventional predictions must be *transported* from the study populations in which the web's parameters were calibrated to the target population of interest (Bareinboim & Pearl, 2016). The web's qualifier fields — which specify the conditions under which each mechanism chain applies — contain the information needed for formal transportability analysis, but the current projection function does not exploit them. An extension that generates context-specific BNs, conditioned on the qualifier features of the target context, would address this limitation and connect the CMR architecture to the growing literature on causal transportability and external validity."

---

### Nancy Nersessian — "You've formalised the product of reasoning but not the process."

I have spent thirty years studying how scientists actually build models — in laboratories, in research groups, over months and years of iterative work (*Creating Scientific Concepts*, 2008; *Interpreting Scientific and Engineering Practices*, 2022). The paper presents a beautiful formal structure: typed nodes, typed edges, algorithms, metrics. What it does not present — and what matters enormously — is how the web was actually *constructed*.

The paper says the web was built through "expert panel deliberation" (§5.2) involving "reduction, calibration, adjudication, inheritance, and constraint enforcement." These are the epistemological operations. But how were they performed? By a human researcher (David Kirsh) interacting with an AI system (Claude) simulating expert voices. This is a radically novel form of scientific model construction, and the paper does not reflect on what it means.

Here is what I would want to know as a cognitive scientist of science:

**First**: When a simulated expert "debates" in a Crucible, what is actually happening cognitively? In a real panel, experts bring embodied knowledge — tacit skills, laboratory intuitions, memories of specific experiments gone wrong, awareness of unpublished results. The simulated experts bring the LLM's compressed representation of the published literature. These are not the same thing. The CMR web, however well-constructed, encodes the published epistemic surface of the fields it draws on, not the deeper tacit knowledge that practicing neuroscientists carry. This matters because many of the most important scientific judgments — "this finding smells wrong," "this effect size is too large for this paradigm," "this group's work is technically excellent but conceptually confused" — rest on tacit knowledge that is not in the published literature.

**Second**: The iterative nature of the construction matters. The web was not built in one pass. It was built panel by panel, with each panel seeing the results of previous panels. This is *constructive* reasoning — each step builds on the products of previous steps. My research shows that constructive reasoning is sensitive to representational format: the way you represent intermediate results affects what you can derive from them. The template format (Toulmin structure, mechanism chain, bridge warrant type) is a specific representational choice, and it both enables and constrains what the panels can produce. A different representational format — say, causal diagrams without Toulmin provenance, or narrative case descriptions without numerical parameters — would produce a different web, not merely a differently formatted version of the same knowledge.

**Third**: The paper treats the web as representing the scientific community's beliefs. But whose beliefs, exactly? The literature that the panels draw on is predominantly Western, English-language, laboratory-based cognitive neuroscience. The architectural applications are predominantly Western building types. The expert voices are simulated from a corpus that overrepresents certain research traditions and underrepresents others. The web represents a *particular community's* beliefs, not THE scientific community's beliefs. This is not a criticism — all knowledge systems have a standpoint — but it should be acknowledged.

**Recommendation**: Add a paragraph in §5.2 or §6.6 acknowledging that the web encodes the published epistemic surface of its source fields, not the tacit knowledge of practicing researchers; that the representational format (Toulmin templates) both enables and constrains the knowledge that can be encoded; and that the web represents the beliefs of a specific (predominantly Western, laboratory-based) research tradition. These are not fatal limitations — they are the starting conditions for any formal knowledge system — but naming them is important for intellectual honesty.

---

### Melanie Mitchell — "What does the system know about what it doesn't know?"

I work on how AI systems handle analogy, abstraction, and the boundaries of their own competence (*Artificial Intelligence: A Guide for Thinking Humans*, 2019). The paper's Algorithm 5 (Value of Information) ranks the web's *known* uncertainties. But the most dangerous uncertainties are the *unknown* ones — the things the web does not know that it does not know.

The web has a mechanism chain for how ceiling height affects creativity through affect broadening. It has a competing account (spatial prediction error → explore-mode shift). What it may not have is the *correct* mechanism — the one that no current theory has articulated. The known unknowns (THEORETICAL_DEFAULTs, unresolved competitions) are tractable. The unknown unknowns (mechanisms not yet conceived, environmental features not yet studied, occupant responses not yet measured) are the real frontier.

The ANALOGICAL bridge warrant type is the web's most honest admission of limited understanding. When the web says "place attachment is analogous to drug-related incentive sensitisation" (NM4, 0.40 confidence, ANALOGICAL), it is saying: we don't have direct evidence; we are reasoning from a parallel case that might not apply. This is the right epistemic attitude. But the web does not have a mechanism for flagging *missing* templates — domains of the built environment that should have templates but don't. 

There is no template for how *smell* affects cognition in buildings (olfactory processing is a major sensory system with known effects on memory, emotion, and alertness, but the CMR has no OLFACTORY-I panel). There is no template for how *proprioceptive feedback from floor surfaces* affects gait, cognitive load, and fall risk in elderly populations (a major architectural concern with clear neural mechanisms). The web's coherence metric would not detect these absences because coherence is defined over *existing* edges, not missing ones.

**Recommendation**: The paper should acknowledge the unknown-unknowns problem and suggest a method for detecting template gaps. One approach: compare the web's environmental feature inventory against a comprehensive taxonomy of building features (e.g., the Building Research Establishment's taxonomy of indoor environmental quality parameters). Any building feature with known neural mechanisms but no CMR template is a gap. Another approach: look for orphaned T1 mechanisms — T1 framework theories that have no downstream T2 templates in certain domains. If the Neuromodulation framework (T1_NM) connects to templates in every sensory domain except olfaction, the olfaction gap is detectable from the web's own structure.

This connects to something deeper about the paper's philosophical framing. The paper says the web represents "what the community believes." But a community's beliefs include not only what they assert but what they *attend to* — what questions they consider worth asking. The web represents the community's *explicit* beliefs (the templates and their parameters) but not its *attentional structure* (which questions are being asked and which are being ignored). A truly self-aware epistemic system would track both.

---

### Michael Nielsen — "The panel process is a collective intelligence system. Does it have the right structure?"

I study how scientific communities generate knowledge through collective computation (*Reinventing Discovery*, 2011). The CMR panel process is a collective intelligence system: it takes distributed knowledge (from the published literature, mediated through simulated expert voices) and aggregates it into a structured representation (the web). The question I want to ask is whether this system has the structural properties that collective intelligence research has identified as important.

**Diversity**: Collective intelligence systems work best when they aggregate diverse, independent perspectives (Surowiecki, 2004; Hong & Page, 2004). The CMR panels simulate experts from different theoretical traditions, which provides some diversity. But the diversity is constrained by the LLM's training corpus and by the panel structure: each panel has a pre-specified roster of experts from pre-specified traditions. There is no mechanism for an unexpected voice to emerge — no equivalent of the outsider who wanders into a seminar and asks the question nobody thought to ask. Real scientific breakthroughs often come from precisely this kind of unstructured diversity.

**Independence**: The simulated experts are not independent — they share a common generative source. O'Connor raised this point and it is correct. But I want to add a different dimension: even if the experts *were* independent, the panel structure creates dependencies through the sequential process. Each panel sees the results of previous panels, which means later panels are anchored by earlier ones. This is not necessarily bad — it can prevent redundant work and ensure consistency — but it means the panels are not independently estimating the same quantities. They are *sequentially constructing* a shared representation. The accuracy of the final product depends on the order of construction, which is O'Connor's path-dependence point, but it also depends on *how much* each panel defers to previous panels versus challenging them. The Crucible structure (where experts contest each other's claims) is the mechanism for challenge, but challenge happens *within* panels, not *between* them. There is no systematic mechanism for a later panel to challenge the conclusions of an earlier panel. This is an asymmetry worth flagging.

**Aggregation mechanism**: The panel process aggregates expert knowledge through structured deliberation (Round Table → Crucible → Calibration). This is a specific aggregation mechanism, and it has known properties. Deliberative aggregation tends to produce consensus — even false consensus — more reliably than, say, prediction markets or Delphi methods (which preserve disagreement more explicitly). The CMR partially addresses this through the EQUILIBRIUM resolution status (Algorithm 2), which records unresolved disagreements. But the system does not have an equivalent of a prediction market — a mechanism that elicits and aggregates independent quantitative estimates before deliberation can produce premature convergence.

**Recommendation**: A brief paragraph noting that the panel process is a collective intelligence system with specific structural properties (sequential construction, deliberative aggregation, limited inter-panel challenge), and that these properties have implications for the reliability of the web's contents. The web reflects not only what the scientific community knows but how the *specific aggregation mechanism* (the panel process) transforms that knowledge into a structured representation. Different aggregation mechanisms — prediction markets, Delphi methods, adversarial collaboration protocols — might produce different webs from the same underlying knowledge. This is worth stating because it means the web is not uniquely determined by the science; it is co-determined by the science and the methodology used to extract and represent it.

---

### Harry Francis Mallgrave — "Does this system capture anything that actually matters for architecture?"

I have spent forty years thinking about the relationship between neuroscience and architectural theory (*Architecture and Embodiment*, 2013; *From Object to Experience*, 2018). I am the person this system is ultimately for. Let me tell you what I see.

**What the paper gets right**: The insight that architectural knowledge requires both mechanistic understanding (why does this feature affect occupants this way?) and interventional reasoning (what will happen if I change the design?) is exactly correct. Architects intuitively operate with both — they have mental models of how spaces work (mechanisms) and they simulate design alternatives (interventions) — but they do so informally, guided by experience and intuition. A system that makes both formal is genuinely valuable.

**What concerns me — the experiential dimension is missing**: The CMR web encodes mechanisms: daylight → 5-HT synthesis → mood modulation. What it does not encode is *what the experience of being in a daylit space is like*. The phenomenological dimension — the felt quality of light moving across a wall during the course of a day, the sense of enclosure and release as one moves from a low corridor into a high atrium, the emotional resonance of a well-proportioned room — is absent from the mechanism chains. This is not a minor omission. It is the omission of what architecture *is*, as experienced by the people who inhabit it.

I recognise that the paper is about the *epistemological architecture* of the knowledge system, not about the experience of buildings per se. But the philosophical framing in §7.4 claims the system provides "understanding" of how buildings affect people. If understanding requires grasping the correct explanation (Khalifa's criterion), and if the correct explanation of how buildings affect people necessarily includes an experiential dimension — what Pallasmaa (2005) calls "the eyes of the skin," what Merleau-Ponty (1945) called the "lived body" — then the system's understanding is systematically incomplete. It understands the *neural mechanisms* by which buildings affect people. It does not understand the *experience* by which buildings affect people. Whether the neural account is sufficient, or whether the experiential dimension is irreducible, is one of the deepest questions at the architecture-neuroscience boundary.

**What excites me — the bridge warrant hierarchy**: The bridge warrant types (CONSTITUTIVE through ANALOGICAL) capture something that architectural researchers desperately need: a formal vocabulary for talking about how confident we should be in claims that transfer from neuroscience laboratories to real buildings. Every architectural researcher I know struggles with this transfer problem — "yes, this works in the lab, but does it work in a building?" — and the bridge warrant hierarchy provides the first systematic framework for addressing it. If the system did nothing else, this hierarchy alone would be a contribution to the field.

**What I would add — the temporal dimension of experience**: Buildings are not experienced in snapshots. They are experienced as *journeys* — temporal sequences of spatial experiences. The experience of entering a cathedral is not the sum of its visual features; it is the *sequence* of compression (narthex), release (nave), and culmination (apse). The mechanism chains in the web are spatial but not temporal — they encode what happens at a given point in a building, not what happens as one moves through a building over time. The AX6 axiom (Acute vs. Chronic Effects) addresses temporal duration but not temporal *sequence*. A template that encoded the *sequential unfolding* of spatial experience — prediction error accumulation along a circulation path, affect trajectory through a sequence of rooms — would capture something that no current template addresses.

**Recommendation**: Add a sentence in the limitations (§6.6 or §7.4) acknowledging that the web encodes mechanism-based understanding of how environmental features affect neural processes, but does not encode the phenomenological dimension of architectural experience — the felt quality of inhabiting a space. Whether this dimension is reducible to the neural mechanisms or constitutes an independent explanatory level is an open question that the architecture-neuroscience boundary has not yet resolved. Also note the absence of temporal-sequential templates as a gap that the web's own structure could, in principle, detect (no T2 templates connect spatial sequence to prediction error accumulation, despite the existence of T1 mechanisms — predictive processing, spatial navigation — that clearly support such templates).

---

## Cross-Panelist Discussion

**Bareinboim**: Harry's point about temporal sequence connects to my transportability concern. The studies that calibrate the web's templates measure responses to *static* environments — a room at a fixed daylight level, a space with a given ceiling height. But architectural experience unfolds over time and involves movement through sequences of spaces. The transportability from static-exposure studies to dynamic-journey experiences is a specific and under-acknowledged bridge warrant problem. It is not captured by any of the current seven bridge warrant subtypes. You might need an eighth: TEMPORAL_EXTRAPOLATION or SEQUENTIAL_TRANSFER — reasoning from static to dynamic exposure.

**Nersessian**: That connects to my point about representational format constraining what can be known. The template format — mechanism chain from feature to mechanism to outcome — encodes *point* interactions (one feature, one mechanism, one outcome). It does not naturally encode *trajectory* interactions (a sequence of features encountered during movement, producing an evolving neural state). The representational format makes it easy to encode "high ceiling → affect broadening → creativity" and hard to encode "low corridor → high atrium transition → prediction error spike → dopaminergic phasic response → enhanced exploration → affect broadening." The temporal-sequential gap is partly a gap in the science and partly a gap imposed by the representational format.

**Mitchell**: And it connects to my point about unknown unknowns. The absence of temporal-sequential templates is detectable: the T1_PP (Predictive Processing) framework explicitly predicts that prediction error *trajectories* — not just levels — matter for cognition. The T1_DMN framework (hippocampal place cells, grid cells) explicitly encodes spatial sequences. Both T1 frameworks predict temporal-sequential effects, but no T2 templates instantiate them. This is an orphaned prediction — a case where the web's own high-level theories predict effects that the web's specific templates do not capture. Algorithm 5 (VOI) could, in principle, detect this if it were extended to look for T1 predictions without T2 instantiation.

**Nielsen**: This convergence — Bareinboim on transportability, Nancy on representational format, Melanie on orphaned predictions, Harry on the experiential dimension — is the kind of insight that emerges from genuine diversity. No single philosopher would have produced it. The temporal-sequential gap is a concrete, actionable finding: it identifies a specific kind of template that the web needs and does not have, and it can be detected from the web's own structure.

---

## Summary of Recommendations

| # | Recommendation | Source | Character | Impact |
|---|---------------|--------|-----------|--------|
| O1 | Acknowledge transportability problem in web-to-BN projection; sketch context-sensitive projection | Bareinboim | Technical gap in the architecture | HIGH — any causal inference reader will notice |
| O2 | Acknowledge the web encodes published epistemic surface, not tacit knowledge; representational format constrains content | Nersessian | Epistemological honesty | MEDIUM — important for framing |
| O3 | Note unknown-unknowns problem; suggest orphaned-T1-prediction method for gap detection | Mitchell | Extends VOI analysis | MEDIUM — sharpens Algorithm 5 |
| O4 | Note panel process is a collective intelligence system with specific structural properties; different aggregation mechanisms might produce different webs | Nielsen | Social epistemology deepening | LOW-MEDIUM — strengthens §5.2 |
| O5 | Acknowledge absence of phenomenological/experiential dimension and temporal-sequential templates | Mallgrave | Domain-specific gap | MEDIUM — matters for target audience |
| O6 | Consider an eighth bridge warrant subtype: TEMPORAL_EXTRAPOLATION for static-to-dynamic transfer | Bareinboim + Mallgrave | Novel contribution | LOW — future work, but worth flagging |

**Convergent finding (all five)**: The temporal-sequential dimension of architectural experience is a major gap detectable from the web's own structure. T1 frameworks (PP, DMN) predict temporal-sequential effects. No T2 templates instantiate them. This is an orphaned prediction and a high-priority template gap.

---

*PANEL_CONSULTATION_IV_OUTSIDE_EYES.md — CMR Project*
*February 25, 2026 (Session 11)*
