# Bayesian Network Success Conditions for Judea Pearl's Causal Algorithms

Judea Pearl's causal inference framework (including Do-Calculus, D-Separation, and Backdoor/Frontdoor adjustments) places strict requirements on the structure and semantics of a Bayesian Network (BN). For the Article Eater project to fully leverage these algorithms to answer "What if?" (interventional) and "Why?" (counterfactual) queries, the BN must satisfy the following theoretical and structural conditions.

## 1. Structural DAG Requirement (No Cycles)
- **Constraint**: The network must be a **Directed Acyclic Graph (DAG)**. 
- **Reasoning**: Standard do-calculus relies on acyclicity to establish a clear topological ordering of cause and effect. Feedback loops (cycles) make the joint distribution unidentifiable under standard structural equation modeling unless they are unrolled dynamically across time (Dynamic Bayesian Networks).
- **Article Eater Context**: Our BN occasionally forms cycles when resolving highly interconnected theories. To support Pearl's algorithms, we must apply rigorous `break_bn_cycles.py` logic to prune recurrent edges, enforcing a DAG representation.

## 2. Causal Markov Condition
- **Constraint**: Every node is conditionally independent of its non-descendants, given its immediate parents in the DAG.
- **Reasoning**: This provides the foundational basis for **d-separation**, allowing the graph's structure to correspond exactly to conditional probabilities in the data.
- **Article Eater Context**: When bridging nodes across different T1.5 theories, we must avoid introducing naive "associational" edges. Every edge should delineate a clear mechanistic pathway.

## 3. Pearl's SCM (Structural Causal Model) Semantics
- **Constraint**: Edges represent asymmetric causal relationships, not just statistical correlations.
- **Reasoning**: The `do(X = x)` operator simulates a physical intervention by mutilating the graph—deleting all arrows pointing into $X$ while leaving the rest of the graph intact. If arrows merely represent correlation (e.g., $A \leftrightarrow B$), deleting inbound edges to $X$ yields mathematically invalid post-intervention distributions.

## 4. Unconfoundedness / Strict Backdoor Criterion
- **Constraint**: All common causes (confounders) of the treatment $X$ and the outcome $Y$ must be measured and included in the graph, or a valid instrumental variable / front-door mechanism must be present.
- **Reasoning**: The **Backdoor Criterion** identifies a set of variables $Z$ that blocks all spurious (non-causal) paths between $X$ and $Y$. If an unobserved confounder $U$ exists, it must be explicitly represented as a latent node ($U \rightarrow X, U \rightarrow Y$).
- **Article Eater Context**: The mapping from environmental factors (e.g., `env.noise`) to outcomes (e.g., `out.cognition`) often has confounding mediators (like `mediator.stress`). These must be correctly connected to evaluate the direct vs. indirect effects accurately.

## 5. Positivity (Overlap)
- **Constraint**: $0 < P(X = x | Z = z) < 1$ for all values of confounding variables $Z$.
- **Reasoning**: When adjusting for confounders, it must be theoretically possible for the intervention or non-intervention to occur under every condition in the adjustment set. Deterministic confounders block the calculation.

## 6. SUTVA (Stable Unit Treatment Value Assumption)
- **Constraint**: The potential outcome of one node/unit is unaffected by the treatment assignment of other units.
- **Reasoning**: Social/spatial spillover effects (e.g., if one person's noise level affects another's outcome) violate standard DAG assumptions unless the network is explicitly formulated as an interference graph.

## Conclusion
For Article Eater's `EpistemicCausalBridge` to return valid `QuineanCounterfactualResult` objects, the ingested BN must be a properly moralized DAG representing strict asymmetric causality, with latent unobserved variables adequately mapped in the JSON schema.
