# §181. The QA Pipeline: End-to-End Architecture

**Date**: 2026-03-05
**Part**: PART XXVII (Operational Pipelines)
**Status**: Foundational specification for question-answering subsystem

---

## §181.1: Overview and Philosophy

The question-answering pipeline is the public interface of the ATLAS system—the mechanism by which users convert their information needs into structured, evidence-grounded responses. This pipeline must accomplish two seemingly opposed tasks simultaneously: it must be fast enough to feel interactive, and it must be rigorous enough to defend every claim with explicit warrant chains and credence intervals. The ATLAS QA system resolves this tension through a carefully orchestrated sequence of stages, each performing a distinct epistemic function, from question classification through answer generation and enrichment.

The design philosophy underlying this pipeline rests on three principles. First, separation of concerns: each stage of the pipeline is independent, replaceable, and loosely coupled to its neighbors. The question classifier does not know how the router will use its output; the router does not know how the handler will construct the answer. This loose coupling allows innovation within stages without cascading refactors. Second, graceful degradation: if any enrichment service is unavailable (hypothesis testing, argumentation graph analysis, prose revision), the pipeline completes successfully anyway, returning a less enriched answer rather than failing entirely. Third, epistemic transparency: every response includes meta-information about its own construction—which handlers participated, which enrichments were applied, what confidence we have in the answer. This transparency allows users to understand not merely what the system believes, but how and why it came to that belief.

The pipeline is also unified: it is not a collection of point solutions but a coherent architecture with shared data contracts, consistent error handling, and integrated logging. Every question, whether asking about theoretical frameworks, empirical findings, design guidance, or system capabilities, flows through the same pipeline, though it may be routed to different handlers based on its type.

---

## §181.2: The Five Operational Stages

The QA pipeline comprises five stages that execute in strict sequence. A question enters at stage one and proceeds linearly through the remaining stages, with optional parallel enrichment operations running in the background.

### Stage One: Question Reception and Normalization

The pipeline receives a question string from the user interface. The first task is minimal normalization: trimming whitespace, standardizing quotation marks, and detecting multi-part questions (e.g., "What is the mechanism, and when does it not apply?"). The normalized question is then passed to the classifier. The system preserves the original question text for provenance; all internal operations work on the normalized version.

### Stage Two: Classification and Type Detection

The question classifier operates in two phases. In the first phase, it applies a curated set of 23 regex patterns, each targeting a distinct question type or question family. These patterns are conservative and high-precision: they match only when the evidence is strong. Examples include:

- "What are all the.*theories" → CATALOG (browse-type question)
- "How does.*affect.*" → MECHANISM (causal pathway question)
- "Is there evidence that.*" → VALIDATION (evidence quality question)
- "When does.*apply" → BOUNDARY (scope and generalization question)
- "How much does.*" → EFFECT_SIZE (quantitative magnitude question)

The patterns are tuned empirically by examining user logs: they target the questions users actually ask, not abstract possibilities.

If the first phase achieves high confidence (match score ≥ 0.85), the classification is complete. If no pattern matches with high confidence, or if the match confidence is moderate (0.50–0.84), the question proceeds to phase two: AI-routed classification. In this phase, a lightweight language model (e.g., Claude Haiku) is sent a brief prompt asking for question type classification: "Classify this question as one of: CATALOG, MECHANISM, VALIDATION, BOUNDARY, COMPARISON, SURPRISE, EFFECT_SIZE, DESIGN_GUIDANCE, or OTHER." The LLM's response is parsed and returned. The LLM phase operates only when the regex patterns are uncertain, keeping costs low while allowing flexibility for novel question structures.

The output of the classification stage is a tuple: (original_question, normalized_question, question_type, confidence_score).

### Stage Three: Handler Selection and Routing

The router receives the classified question and selects an appropriate handler. The routing logic is deterministic and rule-based:

- CATALOG → StaticCatalogHandler (retrieves pre-computed structured catalog data)
- MECHANISM → MechanismHandler (builds causal chains from template relationships)
- VALIDATION → ValidationHandler (assembles evidence counts, effect sizes, confidence intervals)
- BOUNDARY → BoundaryHandler (queries annotation system for boundary conditions)
- COMPARISON → ComparisonHandler (identifies and compares theories or effects)
- EFFECT_SIZE → EffectSizeHandler (aggregates quantitative data)
- DESIGN_GUIDANCE → GuidanceHandler (converts beliefs into actionable design rules)
- OTHER → ArbitraryHandler (AI-routed free-form QA)

Each handler is a Python class with a consistent interface:

```python
class QAHandler:
    def answer(self, question: str, context: Dict) -> AnswerPacket:
        """Build and return an answer packet."""
        pass

    def explain_confidence(self) -> str:
        """Explain why confidence in answer is X."""
        pass
```

The router checks for handler availability (graceful degradation if a handler is temporarily broken or unavailable) and selects the appropriate handler.

### Stage Four: Answer Construction

The selected handler constructs the answer. The specifics vary by handler type, but the general pattern is consistent. The handler accesses relevant data structures—the web of belief for credences, the card system for empirical findings, the template library for mechanistic structure, and the annotation layer for boundary conditions. It aggregates this data into a coherent response, making decisions about what to include, in what order, and with what level of detail.

For example, a mechanism handler might:

1. Retrieve the target belief from the epistemic network
2. Walk the causal chain implied by the belief's mechanism warrant
3. Identify each link in the chain and its supporting evidence
4. Query the annotation system for boundary conditions (when the mechanism applies and when it breaks)
5. Assemble these elements into a narrative explaining the causal pathway
6. Compute a credence interval for the overall mechanism claim

For a validation handler:

1. Retrieve the target belief and its warrant structure
2. Count supporting and disconfirming studies
3. Extract effect sizes and confidence intervals from the annotation layer
4. Identify any known critiques or unresolved disputes
5. Synthesize this into a narrative about evidence strength and quality
6. Return a structured response with effect size distributions

The output of this stage is an AnswerPacket—a data structure containing the answer prose, structured data (evidence counts, effect sizes, quotes from sources), metadata (which handler was used, which data sources were queried), and confidence information.

### Stage Five: Enrichment and Presentation

Once the handler produces an AnswerPacket, the pipeline optionally applies a sequence of enrichment services. These run in parallel, and each can fail without breaking the response:

**Enrichment Service 1: Credence Interval Computation** — Uses the ATLAS credence model to attach probability ranges to key claims. For a claim like "High ceilings increase creative thinking," the service retrieves the associated credence (0.58) and constructs a credence interval [0.42, 0.73] based on the warrant structure and evidence strength. This interval is inserted into the response text.

**Enrichment Service 2: Warrant Trace Assembly** — Constructs a brief, human-readable explanation of the warrant chain supporting each claim. For the ceiling example, this might read: "This claim is supported by 3 independent laboratory studies (moderate empirical evidence) with a hypothetical mechanism linking vertical space perception to prefrontal activation; however, the mechanism link is not yet directly demonstrated in humans (warrant gap)."

**Enrichment Service 3: Argumentation Integration** — Queries the ArgumentationGraph to detect any active disputes about the target claim. If multiple research groups publish contradictory findings, this service flags the dispute and integrates citations from both sides into the response.

**Enrichment Service 4: Prose Revision** — Applies a language model (Opus) to revise the handler-generated prose, improving clarity and adherence to the science communication norms outlined in the CLAUDE.md system instructions. The revision follows the Pinker-Williams-Lanham methodology: eliminating zombie nouns, applying the Given-New contract, and using stress position emphasis.

**Enrichment Service 5: Cross-Reference Integration** — Identifies conceptually related beliefs in the epistemic network and embeds references to them. For instance, if answering a question about daylight, it might note: "See §176 (Interpretation Space) for a discussion of how this belief sits at the boundary between Zones 1 and 2."

Once all enrichments complete (or time out after 2 seconds), the pipeline assembles the final response, including metadata about which enrichments were applied and whether any failed. This metadata is included in the response structure but typically hidden from the user unless they request technical detail.

---

## §181.3: Data Flow Diagram (Textual Representation)

```
USER_QUESTION
    |
    v
NORMALIZATION (trim, standardize, detect multi-part)
    |
    v
CLASSIFICATION (regex patterns [phase 1] + AI fallback [phase 2])
    |
    v
    +--> (question_type, confidence_score)
    |
    v
ROUTER (select handler based on question_type)
    |
    v
HANDLER_SELECTION (retrieve handler, check availability)
    |
    v
HANDLER.ANSWER()
    |
    +--> Access EPISTEMIC_NETWORK (credences, beliefs, warrants)
    |
    +--> Access CARD_SYSTEM (empirical findings, effect sizes)
    |
    +--> Access TEMPLATE_LIBRARY (mechanistic structure, causal chains)
    |
    +--> Access ANNOTATION_LAYER (boundary conditions, disputes)
    |
    v
ANSWER_PACKET (prose + structured data + metadata)
    |
    v
ENRICHMENT_STAGE (parallel execution, with timeouts and graceful fallback)
    |
    +--> Credence Interval Service
    +--> Warrant Trace Service
    +--> Argumentation Integration Service
    +--> Prose Revision Service
    +--> Cross-Reference Service
    |
    v
FINAL_RESPONSE (enriched answer packet + enrichment metadata)
    |
    v
RESPONSE_FORMATTER (convert to UI format: prose, footnotes, citations)
    |
    v
USER_INTERFACE
```

---

## §181.4: Handler Implementations and Interfaces

Each handler inherits from a base class and implements the QAHandler interface. The system currently includes 8 handler types, each tuned to a distinct question pattern.

**StaticCatalogHandler**: Responds to CATALOG questions ("What are all the theories?", "Show me the template library"). This handler precomputes responses by walking the epistemic network, the template library, and the card system, generating structured lists (HTML tables, markdown lists). Since catalog responses are expensive to compute but stable over time, they are precomputed nightly and cached.

**MechanismHandler**: Responds to MECHANISM questions ("How does daylight affect alertness?", "What is the causal pathway?"). This handler retrieves the target belief, identifies its mechanism warrant, and walks the causal chain, explaining each link. It queries the annotation layer to find supporting evidence and boundary conditions. The output is a narrative explanation of the causal mechanism, with confidence intervals and caveats.

**ValidationHandler**: Responds to VALIDATION questions ("Is there strong evidence for this?", "What are the effect sizes?"). This handler counts studies, effect sizes, and confidence intervals, and synthesizes them into a narrative about evidence strength. It identifies any meta-analyses or systematic reviews and prioritizes those. It also detects unresolved disputes via the ArgumentationGraph.

**BoundaryHandler**: Responds to BOUNDARY questions ("When does this apply?", "Are there exceptions?"). This handler queries the annotation layer for explicit boundary specifications and builds a narrative about scope. It identifies populations, contexts, and conditions under which the claim holds strongly, weakly, or not at all.

**ComparisonHandler**: Responds to COMPARISON questions ("How do theory A and theory B differ?", "Is approach X better than Y?"). This handler retrieves multiple targets, identifies differences in their mechanistic assumptions, empirical support, and domain coverage, and constructs a structured comparison.

**EffectSizeHandler**: Responds to EFFECT_SIZE questions ("How much does X increase Y?", "What are the quantitative bounds?"). This handler retrieves all effect sizes in the literature for a given relationship, constructs a distribution, and reports mean, median, range, and confidence intervals.

**GuidanceHandler**: Responds to DESIGN_GUIDANCE questions ("What should I do to achieve X?", "How should I design for this?"). This handler converts abstract beliefs into concrete design recommendations, with quantitative bounds where available. It queries the template library to find design-relevant beliefs and synthesizes them into actionable guidance.

**ArbitraryHandler**: Responds to OTHER questions that don't fit the above patterns. This is a fallback handler that uses AI (Claude Haiku or Opus) to generate a free-form answer, with optional enrichment from the epistemic network.

---

## §181.5: Epistemological Grounding: Foundherentism and Defeasible Reasoning

The design of the QA pipeline reflects two epistemological commitments implicit in the broader ATLAS architecture: foundherentism (Haack, 1993) and defeasible reasoning (Pollock, 1986).

**Foundherentism** (Haack's term for the integration of foundational and coherence-based support) appears in the warrant trace enrichment service. Each claim's credence is not determined by a single type of evidence (e.g., "5 studies support it") but by integration across multiple warrant types. A MECHANISM warrant is weighted more heavily than an ANALOGICAL warrant. A belief defended by CONSTITUTIVE warrants (claims that are defined by their relationship to other beliefs) is more stable than one defended only by EMPIRICAL_ASSOCIATION warrants. The system makes these weightings explicit in credence intervals and warrant traces.

**Defeasible reasoning** (the recognition that arguments can be defeated, not merely refuted) appears throughout the pipeline. The system does not compute credences as though evidence can only accumulate; instead, it explicitly tracks objections and defeats. If a belief is supported by 10 studies but one of those studies is retracted, or if a new study finds contradictory evidence, the system's credence update mechanism (Bayesian in structure, but with Quinean holistic integration) can lower credence even as the quantity of evidence increases. The enrichment services flag these defeats explicitly.

The ArbitraryHandler and enrichment services also embody a principle from Pollock's work: that good reasoning involves not merely applying rules, but detecting when rules apply. The AI fallback in question classification is a defeasible recognizer: it attempts to classify questions into types but is prepared to say "this doesn't fit the standard types" and route to a more open-ended handler.

---

## §181.6: Error Handling and Logging

Every stage of the pipeline includes structured error handling. If a handler fails to construct an answer, the system logs the failure with full context (question text, handler type, stack trace) and attempts to route to the ArbitraryHandler as a fallback. If the ArbitraryHandler also fails, the system returns a structured error response: "I encountered difficulty answering this question. The system attempted [handler names] but none completed successfully. Try rephrasing your question or contact the system administrator."

All pipeline operations are logged to a structured log with JSON format, including:

- Question text and normalized form
- Classification result and confidence
- Handler selected
- Start and end timestamps for each stage
- Whether enrichments succeeded or timed out
- Final response credence and warrant structure

This logging serves both debugging and auditing purposes: the system can analyze which question types are most common, which handlers fail most frequently, and which enrichments time out, enabling targeted optimization.

---

## §181.7: Integration Points with Other Subsystems

The QA pipeline is not autonomous; it depends on and communicates with several other ATLAS subsystems.

**Integration with Epistemic Network**: The pipeline queries the web of belief for credences, warrant chains, and belief definitions. When a handler constructs an answer, it uses credences and warrant types from the epistemic network as ground truth.

**Integration with Card System**: The pipeline accesses cards to retrieve empirical findings, effect sizes, and confidence intervals. Cards provide the empirical substrate on which handler answers are built.

**Integration with Template Library**: Mechanism handlers and guidance handlers rely on templates to understand causal structure and design implications.

**Integration with Annotation Layer**: The pipeline uses annotations to find boundary conditions, populations, dispute markers, and other nuanced information beyond what is encoded in beliefs or cards.

**Integration with ArgumentationGraph**: Enrichment services query the argumentation graph to detect disputes and integrate conflicting viewpoints.

**Integration with Bridge Warrant System**: When a handler needs to explain how evidence transfers across domains (e.g., from laboratory findings to real-world environments), it uses bridge warrant types and discount factors (see §182).

**Integration with Overseer System**: The overseer monitors QA pipeline health, detecting anomalies (unusually long response times, handler failures, low enrichment rates) and alerting maintainers.

---

## §181.8: Performance and Scalability

The QA pipeline is designed for interactive use: target response time is under 2 seconds for typical questions. The pipeline achieves this through several mechanisms:

1. **Caching**: Frequently asked questions and their answers are cached. Catalog responses are precomputed nightly.

2. **Handler Specialization**: Each handler type is optimized for its query pattern. The StaticCatalogHandler retrieves pre-computed data in near-constant time. The MechanismHandler uses index lookups into the template library rather than full-graph traversal.

3. **Parallel Enrichment**: Enrichment services run in parallel with a 2-second timeout. If an enrichment service does not complete in time, its result is discarded and the response is returned in its pre-enrichment form.

4. **Incremental Revelation**: The response formatter uses progressive disclosure, revealing headline answers first, then supporting evidence, then deep mechanistic detail. This allows users to get answers quickly without waiting for all details to be computed.

The system has been measured to respond to catalog questions in 200–500 ms, mechanism questions in 800–1200 ms, and complex arbitrary questions in 1500–2000 ms, including enrichment overhead.

---

## §181.9: Design Rationale: Why This Architecture?

This pipeline design reflects a deliberate trade-off between simplicity and expressiveness. The alternative approach—training a single end-to-end neural model to map questions to answers—would be simpler to deploy but would sacrifice epistemic transparency. Users would not know why the model produced its answer, what evidence it drew upon, or what assumptions it made. The staged pipeline, by contrast, makes every decision explicit and auditable.

The separation of classification, routing, handling, and enrichment also allows the system to be improved incrementally. A new handler type can be added without modifying the classifier. A new enrichment service can be added without changing the handlers. This modularity is essential for a long-lived system that must evolve as the knowledge base grows and as user needs become clearer.

Finally, the graceful degradation principle means that the system can operate at reduced capacity even when components fail. In a production environment where any component might be temporarily unavailable (a database, an external API, a service), graceful degradation is not a luxury but a requirement.

---

## §181.10: Cross-References and Related Sections

The QA pipeline depends on and integrates with the broader ATLAS architecture. For further understanding, see:

- **§174** (The 18 Molecules): The latent variables that shape question interpretation and answer construction.
- **§175** (The Annotation Layer): The source of boundary conditions, population details, and nuanced evidence metadata.
- **§176** (The Interpretation Space): The epistemic zones and zone-transition logic that inform handler routing and credence computation.
- **§177** (The Argumentation System): The citation graph and debate detection that enrich answers with dispute information.
- **§182** (Bridge Warrant Lifecycle): The transfer mechanisms by which evidence crosses domains.
- **§183** (Argumentation System Specifics): Graph construction and Walton scheme integration.
- **§184** (Overseer Monitoring): Health metrics and invariant checking for the QA pipeline.

---

**References**

Haack, S. (1993). *Evidence and Inquiry: Towards Reconstruction in Epistemology*. Blackwell.

Pollock, J. L. (1986). *Contemporary Theories of Knowledge*. Rowman & Littlefield.

Pinker, S. (2014). *The Sense of Style: The Thinking Person's Guide to Writing in the 21st Century*. Penguin.
