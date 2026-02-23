# Web of Belief: Edges, Mechanisms, and Neural Representations

The Article Eater "Web of Belief" operates as a Quinean epistemic network (based on W.V.O. Quine and Paul Thagard's work) rather than a strict physical causal graph. As a result, its edges encode relationships of logical constraint, explanatory coherence, and argumentative support. 

This document defines the edge taxonomy and how the system explicitly represents abstract mechanisms (like neural pathways or cognitive states) as computable nodes.

## 1. The 9 Families of Edges

The Edge Types are categorized into 9 distinct theoretical families (defined in `src/epistemic/edge_types.py`):

1. **`CONSTRAINT` (Basic Epistemic)**
   * **Edges**: `supports`, `contradicts`, `explains`, `instantiates`, `analogous`, `independent`
   * **Purpose**: Basic relationships pulled directly from reading a paper before any complex theory generation happens. E.g., Observation A `supports` Hypothesis B. Observation C `contradicts` Hypothesis D. Theory E `explains` Finding F.

2. **`COHERENCE` (Quinean Holistic Integration)**
   * **Edges**: `coherence_support`, `coherence_tension`
   * **Purpose**: Bidirectional, defeasible edges used by Loopy Belief Propagation to update the entire probability distribution of the web. They encode whether two beliefs conceptually "go together" or "cause tension" globally.

3. **`EPISTEMIC` (Theory Tier / CMR Pipeline)**
   * **Edges**: `epistemic_derivation`, `epistemic_cross_template`, `epistemic_mediation`
   * **Purpose**: Directional inferential edges tracking the exact provenance chain from an abstract Tier 1 Theory (like Attention Restoration Theory) down to a specific testable Tier 2 Hypothesis.

4. **`ARGUMENTATIVE`**
   * **Edges**: `argumentative_support`, `argumentative_challenge`
   * **Purpose**: Captures when a finding supports or attacks a proposition via a multi-step logical argument, rather than direct evidentiary proof.

5. **`REVIEW_SYNTHESIS` (Meta-Analysis)**
   * **Edges**: `includes_in_synthesis`, `synthesizes_as`, `identifies_moderator`, `contradicts_synthesis`
   * **Purpose**: Tracks how primary empirical findings are "rolled up" into systematic reviews and meta-analyses. 

6. **`THEORETICAL` (Theory-Prediction Framework)**
   * **Edges**: `theoretically_predicts`, `confirms_prediction`, `disconfirms_prediction`, `proposes_mechanism`, `subsumes_theory`, `theory_tension`
   * **Purpose**: The core architecture of the post-CMR pipeline. Encodes when a theory makes a successful prediction, or when one theory generalizes/subsumes another. High `confirms_prediction` edge density leads to high entrenchment for the parent theory.

7. **`CONCEPTUAL` (Definitional)**
   * **Edges**: `defines_construct`, `must_distinguish`, `redefines`, `organizes`
   * **Purpose**: Tracks ontology and taxonomy. Ensures the system doesn't conflate two distinct terms that sound similar but are explicitly distinct in the literature.

8. **`CRITIQUE` (Validity Challenge)**
   * **Edges**: `challenges_method`, `challenges_paradigm`, `proposes_better_method`
   * **Purpose**: Represents papers that don't contradict an outcome, but contradict the *method* used to achieve the outcome.

9. **`ATTRIBUTION` (Citation)**
   * **Edges**: `attributes_finding`, `interprets_as`
   * **Purpose**: Simple bibliographic linking.

---

## 2. Bridging

In the Web of Belief, **Bridging** is defined by the `BRIDGE_WARRANT` node type and the `bridges` edge type. 

### What does it mean?
Because Article Eater operates across wildly different domains—such as spatial architecture and neurobiology—it faces an **epistemic gap** when linking findings. 
An architectural study might show that "Open plan offices increase stress." A biological study might show that "Elevated cortisol impairs working memory." 

A `BRIDGE_WARRANT` is an explicit logical node that licenses the transfer of knowledge across these domains (e.g., claiming "Stress responses in open plan offices are driven by chronic cortisol elevation"). The `bridges` edge connects the architectural phenomenon to the biological mechanism. Without this explicit bridge, the system treats the two domains as independent, preventing naive or hallucinatory correlations.

---

## 3. Representation of Neural Elements and Mechanisms

A key question in modeling psychology and cognitive science is: *How are biological neural elements (like the Vagal Pathway, Default Mode Network, or HPA axis) represented in the graph?*

They are **explicitly represented as nodes**, rather than just text labels on an edge.

### Implementation Specifics:
1. **Node Type**: Neural subsystems and biological mechanisms are ingested as nodes of type `THEORETICAL_PROPOSITION` (Family B: Structural Nodes). 
2. **Belief Kind**: Inside the `Belief` data object, they carry the `BeliefKind.MECHANISTIC` flag, indicating they describe "how" something happens.
3. **Connecting Edges (`proposes_mechanism`)**: These mechanistic nodes are connected to Tier 1 Theories (like "Stress Recovery Theory") via `epistemic_derivation` or `subsumes_theory` edges. They connect downwards to empirical Tier 3 outcomes via the **`proposes_mechanism`** edge. 

### Why Represent Them As Nodes?
By explicitly representing the "Vagal Pathway" as its own `THEORETICAL_PROPOSITION` node, the system can:
* **Falsify the Mechanism**: A new paper can attack the vagal pathway directly (creating a `contradicts` edge) without necessarily attacking the parent Stress Recovery Theory as a whole.
* **Determine Probability of Necessity/Sufficiency (PN/PS)**: If multiple theories (e.g., SRT and ART) both point to the "Default Mode Network" as the shared mechanism, the system can use graph traversal (`_trace_path()`) to determine that the DMN is a *Necessary* (PN) bottleneck for cognitive restoration across all paradigms. 
* **Support Compositional Mechanistic Reasoning (CMR)**: (Pending Sprint 7): Finding multiple mechanisms allows the system to compose complex predictions, such as deducing what happens if a drug blocks the vagal pathway while a subject is exposed to nature.
