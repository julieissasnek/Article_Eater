# §183. Argumentation System: Graph Construction and Debate Detection

**Date**: 2026-03-05
**Part**: PART XXVII (Operational Pipelines)
**Status**: Foundational specification for scholarly argumentation modeling

---

## §183.1: From Citation Network to Structured Debate

The scholarly literature on built environment and human perception is not a collection of isolated papers. It is a network of citations, agreements, disagreements, and extensions. Papers cite predecessors, either to build on them or to challenge them. Authors position their work within families of related claims: some defend a theoretical framework, others critique it, still others extend it to new domains. A knowledge system that aspires to represent this literature faithfully must capture not merely what papers claim but how those claims relate to one another—who agrees with whom, where tensions exist, what questions remain contested.

The ATLAS argumentation system constructs and analyzes this scholarly debate structure. It operates in two modes. In the simpler mode, it uses publication metadata (years, citation counts, explicit co-citations) to infer argumentation structure. In the richer mode, it integrates data from the Semantic Scholar API (polarity detection via NLP of cited text snippets) to identify whether citations are supporting, challenging, or extending prior work. The system can then detect debate clusters—communities of papers that engage with the same questions—and flag regions of active disagreement.

This capability serves multiple purposes. For end users, the argumentation system allows the QA pipeline to surface disagreement: instead of presenting a single answer, it can say "Position A is supported by papers X and Y; Position B is supported by papers Z. Here is the evidence each side offers." For the knowledge base maintainers and the overseer system, argumentation detection allows identification of unresolved disputes that should be prioritized for integration and resolution.

---

## §183.2: The Argumentation Graph: Nodes, Edges, and Metadata

The argumentation graph is a directed, weighted graph where nodes represent papers and edges represent citation relationships with classified polarity.

**Nodes (ArgumentationNode)**

Each node represents a paper in the ATLAS knowledge base. The node stores:

- **DOI**: Unique identifier and stable reference
- **Title**: Full title for human readability
- **Year**: Publication year (for temporal ordering)
- **Authors**: List of author names (important for detecting author-based debates)
- **Theories**: List of theoretical frameworks the paper engages (e.g., "coherence theory," "foundationalism," "biophilia")
- **Claim Count**: Number of distinct claims extracted from the paper
- **Citation Count**: From Semantic Scholar if available; indicates influence and reach
- **Extraction Date**: When the paper was integrated into ATLAS

Nodes are hashable and equatable, allowing set operations (intersection, union, filtering) over collections of papers.

**Edges (ArgumentationEdge)**

Each edge represents a citation relationship between two papers. An edge from paper A to paper B means "A cites B." The edge carries:

- **Source DOI** and **Target DOI**: The citing and cited papers
- **Edge Type**: One of "cites" (generic), "supports" (A explicitly endorses B), "challenges" (A refutes or disagrees with B), "extends" (A builds on B with novel claims), "supersedes" (A replaces B with superior evidence or theory)
- **Polarity**: A float from -1.0 (contradicts) to +1.0 (supports), with 0.0 for neutral/unknown. This is the key quantity for debate detection.
- **Confidence**: How confident the system is in the polarity classification (0.0–1.0). High confidence (0.8+) indicates a clear citation polarity; lower confidence indicates ambiguity.
- **Evidence**: A brief string explaining the polarity assignment (e.g., "Target criticizes assumptions of source study"; "Target extends findings of source to new population").

---

## §183.3: Polarity Determination: Pattern Matching and NLP

The system determines edge polarity (whether a citation is supporting or challenging) through a two-stage process.

**Stage 1: Citation Context Pattern Matching** — The system examines the text surrounding the citation. Certain linguistic patterns strongly indicate polarity:

- "As [target] demonstrated..." → supports (+0.8)
- "[Target] found that..." → supports (+0.7)
- "In contrast to [target]..." → challenges (-0.6)
- "[Target]'s methodology has been criticized for..." → challenges (-0.7)
- "We extend the findings of [target] to..." → extends (+0.6, with edge type "extends")
- "Building on [target]'s framework..." → supports (+0.8, with edge type "extends")

The system maintains a curated list of ~50 such patterns, tuned empirically on a sample of annotated citations. For citations where the context is available (full text or abstract), pattern matching is fast and reliable.

**Stage 2: NLP-based Polarity Classification** — For citations where context patterns do not yield high confidence, or where the citing text is ambiguous, the system sends a brief prompt to Claude Haiku: "In this citation, does the citing paper support, challenge, extend, or neutrally acknowledge the cited paper? Provide your judgment and a brief reason." The LLM's response is parsed and used as the polarity.

This two-stage approach keeps costs low (pattern matching for most citations) while handling edge cases gracefully.

**Temporal Polarity** — Citation polarity can also vary temporally. An early paper might have been widely accepted (supporting citations), then later criticized as flawed methodology emerged. The system tracks citation polarity by decade or by clusters of time periods, allowing detection of temporal shifts in scientific opinion.

---

## §183.4: Debate Clusters and Contestation Detection

Once the argumentation graph is constructed, the system identifies debate clusters—communities of papers that engage with overlapping questions and express disagreement.

**Cluster Detection Algorithm**: The system uses a variant of modularity-based community detection (similar to the Louvain algorithm) applied to the citation graph, with the twist that edges with opposite polarities create stronger cluster boundaries than edges with the same polarity.

Specifically:
1. Initialize each node as its own cluster.
2. For each node, consider merging its cluster with neighboring clusters (adjacent via citation edges).
3. Compute the modularity gain from merging: papers that cite each other with similar polarity (both supporting or both challenging a common paper) have high merge gain; papers that cite with opposite polarity have low or negative gain.
4. Perform merges greedily until modularity cannot be improved further.

The result is a partition of the papers into clusters, where papers within a cluster tend to cite each other with consistent polarity (supporting the same side of a debate) and papers across clusters cite with opposite polarity.

**Debate Properties**: For each cluster, the system computes:

- **Cluster ID**: Unique identifier
- **Topic**: Inferred from the paper titles and shared theoretical keywords (e.g., "fractal-preference," "daylight-effects," "biophilia-mechanisms")
- **Papers**: List of DOIs in the cluster
- **Theories Involved**: Theoretical frameworks referenced across cluster papers
- **Dominant Position**: The main claim or position that unifies the cluster (e.g., "fractal patterns in architecture are preferred across cultures")
- **Contestation Level**: A float from 0.0 (consensus, all edges have polarity ≈ +1.0) to 1.0 (highly contested, edges are balanced between +1.0 and -1.0)
- **Internal Edges and Average Polarity**: Statistics on within-cluster citation structure

**Contestation Computation**: The contestation level is computed as:

$$\text{contestation} = \frac{\text{sum of } |p| \text{ for all edges with } p < 0}{n_{\text{edges}}}$$

A cluster where all edges have polarity +0.8 has contestation near 0.0 (consensus). A cluster where edges are split between +0.7 (supporting) and -0.7 (challenging) has contestation near 0.7 (high disagreement).

---

## §183.5: Debate Integration into the QA System

When the QA pipeline constructs an answer, it consults the argumentation graph to enrich the response with debate information.

**Example**: A user asks "Does daylight in buildings improve occupant alertness?" The handler retrieves supporting papers and credence information. The enrichment service queries the argumentation graph, detecting that there exists a debate cluster on this topic with contestation level 0.65. The enrichment service retrieves the cluster information:

- 12 papers in the cluster
- Dominant position: "Daylight improves alertness" (8 papers supporting)
- Opposing position: "Daylight effects are confounded with workspace design" (4 papers challenging)
- Key unresolved question: "Does the effect persist in all-glass buildings with dynamic shading, or is it modulated by daylight variability?"

The answer is then enriched to include this debate information: "This claim is supported by 8 studies with credence 0.78. However, there is active debate about whether the effect depends on daylight variability or whether it holds even in buildings with dynamic control. See the related dispute section below for the opposing position."

---

## §183.6: Walton's Argumentation Schemes: Grammar of Scientific Reasoning

Walton's argumentation schemes (Walton, Reed, & Macagno, 2008) provide a vocabulary for understanding the structure of arguments. Rather than treating all scientific claims as simple assertions with evidence, the scheme framework recognizes that arguments have structure: they appeal to different grounds (empirical evidence, expert authority, analogy, etc.) and can be attacked in different ways.

The ATLAS system maps its warrant types (§182) to Walton schemes:

- **Empirical Evidence scheme**: "The studies show that X; therefore, X is true." (Vulnerable to: confounding, measurement error, generalization failures)
- **Expert Opinion scheme**: "Researcher R (with expertise E) asserts X; therefore, X is likely true." (Vulnerable to: appeals to unqualified authority, disagreement among experts)
- **Cause-to-Effect scheme**: "Cause C produces effect E; C is present; therefore, E occurs." (Vulnerable to: mechanism unknown, effect size overestimated, interaction effects)
- **Analogical scheme**: "Case A and case B are similar in respects R1, R2, R3; case A has property P; therefore, case B likely has property P." (Vulnerable to: disanalogy on properties that matter, boundary effects)
- **Practical Reasoning scheme**: "Goal G is desirable; action A achieves G; therefore, A should be done." (Vulnerable to: alternative means exist, unintended consequences, values conflict)

Each scheme has a set of critical questions—the standard lines of attack that undermine the argument. For the Empirical Evidence scheme, critical questions include: "How many studies?" (strength of evidence base), "What are the effect sizes?" (magnitude), "How reliable are the measurements?" (validity), "How representative is the sample?" (generalizability).

When the argumentation system identifies a debate cluster, it implicitly identifies which schemes are in use and which critical questions are being raised. If papers in one cluster use the Empirical Evidence scheme heavily but papers in another cluster question the critical question "How representative is the sample?", then the debate is about generalizability. The system can make this structure explicit in answers and in guidance to researchers.

---

## §183.7: Toulmin Structure: Microarchitecture of Warrants

Within each argument, Toulmin's structure (Toulmin, 1958) distinguishes claim, data, warrant, backing, qualifier, and rebuttal.

- **Claim**: What the argument asserts (e.g., "Daylight improves alertness")
- **Data**: The evidence offered (e.g., "Study X found a 0.4 standard deviation improvement")
- **Warrant**: The license connecting data to claim (e.g., "Studies are valid evidence for real-world effects")
- **Backing**: The justification for the warrant (e.g., "Randomized trials eliminate confounding")
- **Qualifier**: The strength of the claim (e.g., "probably," "definitely," "in most cases")
- **Rebuttal**: Exceptions and conditions (e.g., "unless the building has dynamic shading that varies daylight unpredictably")

The ATLAS system models this structure in its warrants and annotations. When extracting a claim from a paper, the extraction process identifies not only the claim but, where possible, the data, warrant, and rebuttal. Annotations then capture backing (which theoretical frameworks justify the warrant?) and qualify the claim with credence intervals.

The argumentation system uses Toulmin structure to identify debates: if papers A and B assert the same claim but on different data and warrants, the debate is about which data or warrant is more reliable. If they assert different claims, the debate is conceptual.

---

## §183.8: Gap Discovery and Research Agenda Generation

The argumentation system, combined with the interpretation space (§176), identifies gaps in the scholarly literature. A gap is a question that remains unresolved across all papers in a debate cluster.

**Example**: The debate cluster on daylight effects includes papers A and B that support the effect, and papers C and D that challenge it due to generalization concerns. None of the papers directly tests the effect in buildings with dynamic shading systems. The system identifies this as a gap: "Generalizability of daylight effects to dynamically-shaded buildings: Unresolved."

These gaps are ranked by endogenous value (§176.4): a gap with high structural impact (resolving it would strengthen many related beliefs), high tractability (the answer is likely findable in literature or through research), and high coherence tension (the gap sits at a dispute point) moves to the top of the research agenda.

The gaps are exposed to the interpretation space, becoming part of the Epistemic Network's explicit research priorities.

---

## §183.9: Bridge Relationships and Debate Propagation

Debates are not isolated. If a debate exists in one domain (e.g., "Does daylight affect alertness in offices?") and a bridge warrant connects to another domain (e.g., "Does daylight affect alertness in residential buildings?"), then the debate propagates across the bridge. The system recognizes this and flags the target domain as contested, even if no papers directly studying the target domain exist.

This is crucial for understanding epistemic coherence. A belief that is well-supported by mechanism warrants but sits in a contested region of the debate graph is less secure than one that rests on consensus.

---

## §183.10: Integration with the Card System

Cards represent empirical findings extracted from papers. The argumentation system links cards to debate clusters, allowing the card system to flag which empirical findings are in dispute.

For instance, if a card records "Daylight exposure increases alertness by 0.40 standard deviations (N=45, p=0.02)" and this finding comes from a paper in a debate cluster where other papers question the generalizability, the card is marked with a dispute flag. When the QA system retrieves this card, it can note the dispute and encourage the user to examine the debate.

---

## §183.11: Design Rationale: Why Formal Argumentation?

Why model argumentation formally, using schemes and Toulmin structure, rather than treating it informally? Formal models allow systematic analysis. If a system understands the structure of an argument (claim, data, warrant, critical questions), it can:

1. Detect when two arguments are in real disagreement vs. merely using different terminology.
2. Identify the specific point of dispute (is the disagreement about data? mechanism? generalizability? values?).
3. Explain disputes to users at the appropriate level of detail.
4. Generate research priorities that would resolve disputes.

Informal treatment of argumentation (simply noting "papers A and B disagree") provides much less information.

The system also benefits from the psychological work on argument understanding: humans reason more reliably when argument structure is made explicit (Macagno & Walton, 2018). By surfacing the schemes and critical questions in answers, the system helps users reason more carefully about claims.

---

## §183.12: Cross-References and Related Sections

The argumentation system operates in concert with:

- **§177** (The Argumentation System, earlier part): Walton schemes in abstract.
- **§176** (The Interpretation Space): Gap discovery and research agenda generation.
- **§182** (Bridge Warrant Lifecycle): How debates propagate across domain bridges.
- **§181** (QA Pipeline): How the enrichment service integrates argumentation data into answers.
- **§175** (The Annotation Layer): Where dispute flags and debate cluster membership are stored.

---

**References**

Macagno, F., & Walton, D. (2018). Interpreting stasis theory as a method of argumentation analysis. *Argumentation*, 32(1), 1–42.

Toulmin, S. E. (1958). *The Uses of Argument*. Cambridge University Press.

Walton, D. N., Reed, C. A., & Macagno, F. (2008). *Argumentation Schemes*. Cambridge University Press.
