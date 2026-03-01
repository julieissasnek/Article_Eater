# PANEL SPECIFICATION — FOUNDATIONS-I: A Formal Inference Calculus for Typed Belief Webs

## Panel ID: FOUNDATIONS-I
## Sprint: F-01 (Meta-epistemological, outside the domain pipeline)
## Date: February 23, 2026
## Character: This is not a domain panel. It does not calibrate templates about
##   buildings and brains. It builds the formal machinery that tells the CMR
##   how to REASON OVER its calibrated templates. It is a panel about the
##   system's own epistemology.

---

# PART I: PANEL CHARGE

## 1.1 The Problem

The CMR system has built a Web of Belief containing approximately 93
calibrated templates, 10 Tier 1 framework theories, 10 Tier 1.5 domain
theories, 8 cross-cutting axioms, 2 working models, and a rich structure of
typed edges connecting them. The system can answer lookup queries ("what is the
confidence for daylight's effect on mood?") and can propagate effects
compositionally along mechanism chains.

What the system cannot do is reason *formally* over its own structure. When the
system says "Barrett-Craig should be adopted as a working model," or "AX4
should be elevated to a cross-cutting moderator," or "the competition between
wanting-driven and goal-directed approach should be resolved in favour of a
dual-parameter model," these decisions are made by expert judgment in the
panel process. They are reasonable, well-argued decisions. But they are not
derived from a formal calculus. There are no explicit inference rules that take
the web's current state as input and produce these decisions as output.

This matters for three reasons:

1. **Reproducibility.** Different reasoners examining the same web should reach
   the same conclusions. Without formal rules, two people (or two AI systems)
   may evaluate the same web differently because they apply different implicit
   standards for what counts as "sufficient evidence for adoption" or
   "adequate grounds for demotion."

2. **Automation.** As the web grows (new templates, new evidence, revised
   parameters), the reasoning operations — coherence checking, competition
   resolution, structural revision — must be performed at scale. Informal
   expert judgment does not scale. Formal rules do.

3. **Justification.** When the system recommends a design intervention to an
   architect, the architect should be able to ask "why do you believe this?"
   and receive an answer that traces through the web's inference rules, not
   just through its data. The formal calculus provides the justificatory
   backbone.

## 1.2 The Deliverable

A **formal inference calculus for typed belief webs** — a set of rules,
formally specified, that governs:

- How credence propagates through each type of edge
- How competition between hypotheses is resolved
- How global coherence is evaluated
- How the web revises its own structure
- What convergence properties the revision strategy has

The calculus must be:
- **Sound**: it should not derive conclusions that are epistemologically
  unjustified
- **Complete enough**: it should handle every edge type and every reasoning
  operation the CMR actually performs
- **Computationally tractable**: it should be implementable as software
  operating over the CMR's graph structure
- **Empirically adequate**: when applied to the CMR's actual history of
  decisions (Barrett-Craig adoption, AX4 elevation, ART/SRT demotion), it
  should reproduce those decisions as correct inferences — or, if it cannot,
  it should identify which decisions were suboptimal and why

## 1.3 What Success Looks Like

The panel succeeds if and only if all seven of the following conditions are
met:

**S-1 (Formal Semantics for Every Edge Type).** Every edge type in the CMR
web (reduction, bridge warrant [7 subtypes], competition, cross-template
interaction, inheritance, working-model, and AX-axiom) has a formal semantics:
a mathematical specification of what the edge means, what inference rules
operate over it, and how it interacts with other edge types.

**S-2 (Credence Propagation Rules).** There exist explicit, implementable
rules for computing the credence of any node in the web given the credences of
its neighbours and the types of the connecting edges. The rules must handle
multi-parent nodes (a T1.5 theory with 2-3 T1 parents), typed attenuation
(credence propagates differently through MECHANISM edges than ANALOGICAL
edges), and the hierarchical entrenchment ordering (T1 nodes are more resistant
to revision than T2 nodes).

**S-3 (Competition Resolution Protocol).** There exists a formal protocol for
resolving competition edges: given two (or more) hypotheses that compete to
explain the same evidence, the protocol determines whether one defeats the
other, whether they are in equilibrium, or whether a compromise (domain
partition, weighted integration) is warranted. The protocol must handle
graded defeat (partial undermining), domain-restricted competition (one
account wins in one context, another wins in a different context), and the
generation of compromise models.

**S-4 (Global Coherence Metric).** There exists a computable metric that
evaluates the coherence of the total web — not just pairwise consistency, but
the degree to which the web's beliefs mutually support each other through
explanation, analogy, and inheritance. The metric must be sensitive to
structural features: adding a new explanation link should increase coherence;
adding a contradiction should decrease it; independent convergence from
different theoretical traditions should increase it more than convergent
evidence from the same tradition.

**S-5 (Structural Revision Rules).** There exist explicit rules for modifying
the web's structure (adding nodes, removing nodes, adding edges, changing
edge types, promoting/demoting theories between tiers) in response to new
evidence or theoretical considerations. The rules must satisfy the AGM
rationality postulates (or a justified extension of them) and must specify the
entrenchment ordering that determines which beliefs give way first when
revision is required.

**S-6 (Convergence Guarantee).** There exists a proof or well-supported
argument that the web's revision strategy, applied to an infinite stream of
evidence, converges to the truth (or to the closest approximation thereof
given the web's representational limitations). If convergence cannot be
guaranteed unconditionally, the conditions under which convergence holds and
fails must be explicitly characterised.

**S-7 (Empirical Adequacy Test).** The calculus, when applied to the CMR's
actual history of decisions (at least: Barrett-Craig adoption, differential-
mode model adoption, AX4 elevation, ART/SRT demotion to T1.5, Aesthetic
Anchoring deferral), reproduces at least 4 of 5 as correct inferences from
the evidence available at the time. If it disagrees with any historical
decision, the disagreement must be articulated as a specific argument showing
why the calculus recommends a different conclusion.

---

# PART II: PANEL COMPOSITION

| # | Expert | Institution | Role | Primary Assignment | Why This Person |
|---|--------|------------|------|-------------------|-----------------|
| 1 | Paul Thagard | U Waterloo (emeritus) | Coherence anchor | Global coherence metric (S-4), competition resolution (S-3) | Created ECHO, the closest existing formalism. Defines what coherence means computationally. |
| 2 | Clark Glymour | CMU (emeritus) | Theory-evidence bridge | Bridge warrant semantics, reduction edge formalism | Uniquely straddles philosophy of science and causal inference. His bootstrap testing (1980) addresses exactly how theoretical terms connect to evidence. |
| 3 | Stephan Hartmann | LMU Munich / MCMP | Bayesian coherentism | Credence propagation (S-2), coherence-probability interface | With Bovens, proved that coherence ≠ high joint probability. Brings formal tools for relating coherence to probabilistic inference. |
| 4 | Peter Gärdenfors | Lund | Belief revision | Structural revision rules (S-5), entrenchment ordering | Co-creator of AGM, the standard framework for belief revision. Conceptual spaces work provides geometric tools for graded belief. |
| 5 | Henry Prakken | Utrecht | Argumentation | Competition resolution (S-3), Toulmin formalisation | ASPIC+ framework handles structured argumentation with strict/defeasible rules. Maps directly onto CMR's Toulmin layer. |
| 6 | Kevin Kelly | CMU | Formal learning theory | Convergence (S-6), reliability of revision strategy | Topological methods for assessing whether belief-revision strategies converge. Provides meta-level guarantee of epistemic soundness. |
| 7 | Judea Pearl | UCLA (emeritus) | Causal inference | Do-calculus interface, BN-web bridge | Invented do-calculus. Defines the boundary between what the web can and cannot do. Essential for specifying what the BN contributes that the web cannot. |
| 8 | Erik Olsson | Lund | Coherentism / social epistemology | Collective belief dynamics (S-4, S-5) | Work on coherence in multi-agent systems directly relevant to CMR panels (multiple simulated experts forming collective judgment). |
| 9 | Marcello D'Agostino | U Milan | Logic / bounded rationality | Computational tractability, information-theoretic constraints | Work on depth-bounded reasoning and computationally tractable approximations to ideal inference. Ensures the calculus is implementable, not just theoretically elegant. |

**Textual Authority**: W.V.O. Quine & J.S. Ullian (web of belief metaphor),
Nelson Goodman & John Rawls (reflective equilibrium), Stephen Toulmin
(argumentation structure), Larry Laudan (problem-solving model of scientific
progress).

---

# PART III: THE EDGE TYPES — Exhaustive Inventory

Before the panel can reason about the edges, we must define exactly what
exists. The CMR web contains 8 distinct edge types, some with subtypes.

## Edge Type 1: REDUCTION

**Notation**: T1 ──reduces──→ T1.5, or T1.5 ──reduces──→ T2

**What it means**: A higher-tier belief is EXPLAINED BY a lower-tier
mechanism. Prospect-Refuge theory (T1.5) is reduced to Predictive Processing
(T1) + Default Mode / Place Cells (T1). This means: the claims of
Prospect-Refuge theory can be derived (at least approximately) from the
principles of PP and DP applied to the domain of spatial experience.

**Current informal semantics**: Reduction edges carry credence downward via
the credence formula P(CNFA) = P(T1) × P(bridge) × P(CNFA-specific). A T2
template inherits partial credence from its T1 parents.

**Open questions for the panel**:
- Multi-parent reduction: When a T1.5 theory has 2 T1 parents (e.g.,
  Prospect-Refuge = PP + DP), is the credence contribution conjunctive
  (P(PP) × P(DP)) or disjunctive (max(P(PP), P(DP))) or something else?
  Conjunctive means *both* must be true; disjunctive means *either* suffices.
  The answer probably depends on whether the T1 parents provide independent
  or complementary mechanisms.
- Depth of reduction: Is the credence attenuation per edge constant, or does
  it compound? If a T2 template is reduced to a T1.5 theory which is reduced
  to a T1 framework (two reduction edges), does credence attenuate twice?
- Symmetry: Does successful prediction by a T2 template increase credence in
  its T1 parent? (Bottom-up credence flow.) If the daylight → 5-HT → mood
  pathway is empirically confirmed, does PP gain credence because it
  predicted a prediction-error mechanism? This would make reduction edges
  bidirectional in some sense, even though the explanation flows downward.

## Edge Type 2: BRIDGE WARRANT (7 subtypes)

**Notation**: claim ──bridge(type)──→ evidence

**What it means**: A bridge warrant connects a theoretical claim to its
empirical evidence, specifying the *type and strength of the inferential
bridge*. The 7 subtypes form a hierarchy:

| Subtype | Ceiling | Meaning |
|---------|---------|---------|
| CONSTITUTIVE | 0.75 | The mechanism IS the phenomenon (e.g., DA firing IS the RPE) |
| MECHANISM | 0.60 | Complete causal pathway specified at neural/molecular level |
| EMPIRICAL_COVARIANCE | 0.60 | Replicated statistical association, incomplete mechanism |
| FUNCTIONAL | 0.50 | Same function in lab and building, possibly different mechanism |
| CAPACITY | 0.45 | Neural system has capacity to respond, but untested in architecture |
| ANALOGICAL | 0.35 | Reasoning from parallel case |
| THEORETICAL_DEFAULT | 0.40 | Expert-assigned placeholder awaiting empirical calibration |

**Current informal semantics**: The warrant type determines the maximum
confidence (ceiling) for the associated claim. The actual confidence may be
lower than the ceiling but never higher.

**Open questions for the panel**:
- Promotion and demotion: When does a bridge warrant change type? If a new
  study provides a mechanism for a previously EMPIRICAL_COVARIANCE claim, does
  the bridge automatically upgrade to MECHANISM? What is the formal trigger?
- Interaction with competing accounts: If a claim has a MECHANISM bridge but
  a competing account also has a MECHANISM bridge, how do the two bridges
  interact? Do they compete (the stronger mechanism wins) or coexist (the
  claim's credence is split)?
- Compound bridges: When a mechanism chain has multiple steps, each with its
  own bridge warrant, is the chain's overall warrant the weakest link
  (minimum), the product, or something else?
- THEORETICAL_DEFAULT → empirical: When a THEORETICAL_DEFAULT is replaced by
  empirical data, how does the revision propagate? Is it a simple parameter
  update or does it trigger structural revision if the empirical value
  differs substantially from the default?

## Edge Type 3: COMPETITION

**Notation**: hypothesis_A ──competes──→ hypothesis_B

**What it means**: Two (or more) hypotheses both attempt to explain the same
evidence or phenomenon, and they are mutually incompatible (in whole or in
part). Barrett's constructionism competed with Craig's labelled-line theory.
Goal-directed approach competes with DA-driven approach. Motor-afferent
walking-creativity competes with attentional-release walking-creativity.

**Current informal semantics**: Competition edges are resolved in Crucible
debates, which produce one of three outcomes: victory (one account wins),
compromise (both accounts are partially correct, usually via domain
partition), or recorded disagreement (the competition remains for future
resolution).

**Open questions for the panel**:
- Graded competition: Can competition be partial? If Barrett's model
  accounts for 70% of the evidence and Craig's for 30%, is this a 0.70/0.30
  credence split, or does Barrett win entirely because she explains more?
  What is the formal relationship between explanatory coverage and credence?
- Domain-restricted competition: Barrett wins for anterior insula, Craig wins
  for posterior insula. The compromise is a domain partition. How does the
  formal calculus represent domain partitions? As conditional credences
  (P(Barrett | anterior insula) = high, P(Craig | posterior insula) = high)?
  Or as a new, composite hypothesis that supersedes both?
- Multi-way competition: Most Crucible debates are binary, but some claims
  face 3+ competing accounts. How does the credence distribute? Is it
  proportional to explanatory coherence, or does the best account get a
  disproportionate share (winner-take-most)?
- Diachronic competition: A competition that is currently in equilibrium
  (0.50/0.50) may be resolved by future evidence. How does the web represent
  the *expected information gain* from a future experiment that would resolve
  the competition? This connects competition edges to VOI analysis.

## Edge Type 4: CROSS-TEMPLATE INTERACTION

**Notation**: template_A ──interacts──→ template_B

**What it means**: Two templates share a mechanism, an environmental input, or
a neural substrate, such that the output of one affects the output of the
other. NE alerting (NM5) interacts with ACh precision (NM6) through the
NE-ACh orthogonal uncertainty framework. 5-HT mood (NM7) moderates the
wanting-liking balance (NM2).

**Current informal semantics**: Cross-template interactions are flagged during
panel calibration and either resolved within-panel (the interaction is
modelled explicitly in one or both templates) or assigned to CROSSCUT-I for
cross-panel reconciliation. Resolved interactions become constraints on the
interacting templates' parameters.

**Open questions for the panel**:
- Directionality: Is the interaction symmetric (A affects B and B affects A)
  or asymmetric (A affects B but not vice versa)? In the CMR, most
  interactions are modelled as asymmetric (5-HT moderates wanting-liking, not
  the reverse), but the underlying neuroscience may be bidirectional. How
  does the formal calculus handle the simplification from bidirectional
  neuroscience to unidirectional model?
- Interaction strength: How strong is the interaction? The CMR currently
  specifies interaction effects as moderation parameters (e.g., AX4_mod
  range 0.6-1.4 on HPA and NE), but these are THEORETICAL_DEFAULTs. What
  formal constraints should govern interaction strength?
- Emergent interactions: Two templates may interact through a pathway that
  neither template explicitly models. Daylight affects both NE (alerting) and
  5-HT (mood), and NE and 5-HT interact in the raphe nuclei — but no
  template models the NE-5-HT interaction directly. How does the web detect
  and represent emergent interactions?
- Double-counting: The T29 verification identified a mild double-count
  (social isolation enters T29 both directly and through inflammation). What
  formal rule detects double-counting, and what is the formal remedy?

## Edge Type 5: INHERITANCE

**Notation**: template_A ──inherits(parameter)──→ template_B

**What it means**: Template B uses a parameter that was calibrated by
template A. NEUROMOD-I's NM8 (threat/HPA) inherits HPA parameters from
STRESS-I's T7 (body budget). CREATIVE-I's incubation template inherits DMN
re-engagement conditions from MEMORY-I.

**Current informal semantics**: Inheritance is enforced by constraints (C-01:
"Inherit STRESS-I HPA parameters. Do not re-derive."). The receiving template
uses the parameter value as given and does not independently calibrate it.

**Open questions for the panel**:
- Confidence inheritance: When template B inherits a parameter from template
  A, does it also inherit the confidence? If A calibrated the parameter at
  confidence 0.55, does B use it at 0.55? Or does the additional step (using
  the parameter in a new context) introduce additional uncertainty, reducing
  B's confidence below 0.55?
- Revision propagation: When template A revises its parameter (due to new
  evidence), does the revision automatically propagate to all inheriting
  templates? What is the formal mechanism? Is it instantaneous or staged?
- Conflict: What happens when template B has independent evidence suggesting
  a different parameter value than what it inherits from A? Which takes
  priority — the inherited value (maintaining consistency) or the
  independent evidence (respecting data priority)? This is a direct conflict
  between Thagard's Principle 3 (coherence favours consistency) and
  Principle 4 (data priority).
- Inheritance depth: If template C inherits from B, which inherits from A,
  does C indirectly inherit from A? Is there credence attenuation at each
  inheritance step?

## Edge Type 6: WORKING MODEL

**Notation**: working_model ──constrains──→ {set of templates}

**What it means**: A working model is a theoretical commitment that the web
has adopted as a default assumption, applicable to multiple templates, with an
explicit revision clause. Barrett-Craig two-stage interoception and the
differential-mode model are the CMR's two current working models.

**Current informal semantics**: Working models are adopted by human decision
(in the CREATIVE-I and NEUROMOD-I reviews). They constrain all templates
that involve their domain (Barrett-Craig constrains all templates with IC
components; differential-mode constrains all templates with stimulation-mode
interactions). They carry a "revision clause" — a statement of what evidence
would trigger revision.

**Open questions for the panel**:
- Formal status: Is a working model a belief (with a credence score), a
  constraint (a hard rule that templates must satisfy), or something in
  between (a soft constraint with a credence-dependent strength)? If it is a
  belief, what is its credence, and how does revision of that credence
  propagate to the constrained templates? If it is a constraint, what
  happens when a template has strong evidence against the constraint?
- Revision clause formalism: The revision clause is currently stated in
  natural language ("if future evidence shows the posterior-anterior insular
  gradient is not as clean as Kurth et al. (2010) suggested, revise").
  Can this be formalised? What counts as "sufficient evidence to trigger
  revision"? Is there a formal threshold, or is it a judgment call?
- Scope: A working model constrains "all templates that involve its domain."
  But how is the domain formally defined? Barrett-Craig applies to "IC
  components" — but what counts as an IC component? Is there a formal
  criterion, or is it a family resemblance?
- Interaction between working models: What happens when two working models
  make conflicting predictions for the same template? The CMR currently has
  only two working models that do not conflict, but as more are adopted,
  conflicts become likely.

## Edge Type 7: AX-AXIOM

**Notation**: AX_parameter ──modifies──→ {set of templates}

**What it means**: An AX axiom is a cross-cutting parameter (dose-response
function, habituation rate, individual-difference moderator, cultural
modifier, perceived control moderator, acute-chronic distinction, attention
mediation, VR limitation discount) that modifies the output of every template
in the web.

**Current informal semantics**: AX axioms are calibrated by CROSSCUT-I (the
final domain panel) and applied retroactively to the entire calibrated corpus.
They are meta-parameters: they do not add new mechanisms but modify existing
ones.

**Open questions for the panel**:
- Priority: When an AX axiom (e.g., AX_HABITUATION_002 specifying a general
  habituation rate) conflicts with a domain-specific calibration (e.g., NM1
  specifying RPE-specific habituation at a different rate), which takes
  priority? Is the AX axiom a default that domain-specific values override,
  or a constraint that domain-specific values must respect?
- Level-dependence: AX parameters may apply differently at different IE-DPT
  levels (habituation may be faster for Level 1 implicit processes than Level
  3 explicit processes). How does the formal calculus represent
  level-dependent axioms?
- Retroactive application: AX axioms from CROSSCUT-I are applied to
  templates calibrated by earlier panels. Does retroactive application change
  the confidence scores of earlier templates? If AX_VR_LIMITATION_012
  specifies a discount factor for VR evidence, and an earlier template relied
  heavily on VR studies, its confidence should decrease. Is this automatic?
- Composition: Multiple AX axioms may apply to the same template (dose-
  response AND habituation AND individual differences AND cultural
  modulation). How do they compose? Multiplicatively? Additively? In what
  order?

## Edge Type 8: PARTIAL-OUT

**Notation**: template_A ──partial_out(mechanism)──→ template_B

**What it means**: Two templates address related phenomena but are formally
partitioned so that each owns a specific mechanism or outcome. NEUROMOD-I owns
the DA mechanism; MEMORY-I owns the encoding consequence. The partial-out
prevents double-counting.

**Current informal semantics**: Partial-outs are enforced by constraints
(C-04: "PE encoding partial-out: NEUROMOD-I owns DA mechanism; MEMORY-I owns
encoding"). They are essentially scope boundaries.

**Open questions for the panel**:
- Completeness: How do we know the partial-out is exhaustive — that the
  partitioned scopes cover the full phenomenon with no gaps and no overlaps?
  The DA-mechanism / encoding-consequence partition seems clean, but more
  complex phenomena may not partition cleanly.
- Confidence interaction: When two partial-out templates together explain a
  full phenomenon (DA mechanism + encoding consequence = full PE → memory
  effect), is the combined confidence the product of the two template
  confidences, the minimum, or the maximum? What is the formal rule?
- Revision: If one template in a partial-out pair is revised (the DA
  mechanism is respecified), does the other template require revision too
  (even though it owns a different mechanism)? The partial-out edge says
  they are formally separate, but the underlying neuroscience is connected.

---

# PART IV: CRUCIBLE DEBATES (5)

## Crucible 1: Credence Propagation Through Reduction — Conjunctive, Disjunctive, or Compositional?

**Charge**: When a T1.5 theory has multiple T1 parents (e.g., Prospect-Refuge
= PP + DP), how does credence flow from parents to child?

**Position A — Conjunctive (Glymour)**:
Both parents must be approximately correct for the child to be correct.
Prospect-Refuge theory claims that the brain predicts threat from spatial
configuration (PP) AND that place cells encode refuge locations (DP). If
either parent theory is wrong, the child theory fails. Therefore:
P(T1.5) ≤ min(P(PP), P(DP)) — the child's credence cannot exceed its
weakest parent's.

**Position B — Disjunctive (Hartmann)**:
Multiple parents provide independent support. Even if PP is wrong, DP might
independently explain Prospect-Refuge (organisms prefer prospect-refuge
configurations because of hippocampal place cell encoding of safe locations,
regardless of whether this involves prediction error). Therefore:
P(T1.5) ≥ max(P(PP), P(DP)) — the child inherits at least as much credence
as its strongest parent provides.

**Position C — Compositional (Thagard)**:
Neither conjunction nor disjunction. The child's credence depends on how
the parents INTERACT in explaining the child. If the parents provide
complementary mechanisms (PP explains the threat-detection component, DP
explains the spatial-memory component), the child is more credible than
either parent alone because it has a richer explanatory base. If the parents
provide redundant mechanisms (both explain the same aspect), the child gets
little additional credence from the second parent. Therefore the rule must
be sensitive to the STRUCTURE of the reduction, not just the number of
parents.

**Success condition**: A formal rule that handles multi-parent reduction,
produces intuitively correct results for the CMR's actual T1.5 theories, and
specifies the conditions under which the conjunctive, disjunctive, and
compositional modes apply.

---

## Crucible 2: Competition Resolution — Argumentation Defeat or Bayesian Updating?

**Charge**: When two hypotheses compete (Barrett vs. Craig, wanting-driven vs.
goal-directed approach), how is the competition resolved?

**Position A — Argumentation Defeat (Prakken)**:
Model the competition as an argumentation framework. Each hypothesis is an
argument; each argument attacks the other. Resolve using Dung's preferred
semantics (or a graded extension): an argument is acceptable if it survives
all attacks from acceptable counter-arguments. The Barrett-Craig debate is
resolved by identifying which argument's data, backing, and warrant survive
the other's rebuttal.

This approach handles domain partitions naturally: Barrett and Craig both
survive in their respective domains (anterior and posterior insula) because
each attacks the other only outside its own domain. The compromise is a
labelling: Barrett is IN for anterior insula, Craig is IN for posterior
insula, and the competition edge becomes a domain-restricted defeat
relation.

**Position B — Bayesian Updating (Hartmann)**:
Model the competition as a Bayesian hypothesis comparison. Assign prior
probabilities to Barrett and Craig. Update on the evidence (Kurth et al.
2010 meta-analysis, individual fMRI studies, etc.) using Bayes' rule.
The posterior ratio P(Barrett | evidence) / P(Craig | evidence) determines
the resolution. If the ratio is > 3:1, Barrett wins; if < 1:3, Craig wins;
if between 1:3 and 3:1, the competition is unresolved.

This approach is quantitatively precise but loses the domain-partition
structure: Bayesian updating produces a single posterior ratio, not a
domain-specific credence map. Producing Barrett-wins-here and Craig-wins-there
requires a more complex model with domain-conditioned hypotheses.

**Position C — Reflective Equilibrium (Gärdenfors)**:
Neither defeat nor updating. Resolution comes from mutually adjusting the
hypotheses and the interpretation of the evidence until a coherent state is
reached. This is what the CMR actually did: it adjusted Barrett (dropping
her claim to explain early sensory interoception) and adjusted Craig
(dropping his claim to explain evaluative interoception) until the
two-stage model emerged. The formal mechanism is belief revision: contract
both hypotheses to their empirically supported cores, then expand with the
compromise.

**Success condition**: A formal protocol that handles graded competition,
domain partition, multi-way competition, and the generation of compromise
hypotheses. The protocol must reproduce the Barrett-Craig resolution and the
wanting-liking dual-parameter outcome as correct applications.

---

## Crucible 3: Coherence — Constraint Satisfaction or Probabilistic Measure?

**Charge**: What does it mean to say the web is "coherent," and how do we
measure it?

**Position A — Constraint Satisfaction (Thagard)**:
Coherence is a property of the web's constraint structure. Define positive
constraints (explanation links, inheritance links, analogy links) and negative
constraints (competition links, contradiction links). The web's coherence is
the degree to which the accepted beliefs satisfy positive constraints and
avoid negative constraints. This is computed by a connectionist settling
algorithm (ECHO) or a constraint optimisation algorithm.

The advantage: this captures the STRUCTURAL notion of coherence — beliefs
cohere because of how they are connected, not because of their individual
probabilities. The disadvantage: the output is a single number (global
coherence score) that does not decompose into contributions from individual
beliefs or edges.

**Position B — Probabilistic Measure (Hartmann, Olsson)**:
Coherence is a probabilistic property. The web is coherent to the degree
that its beliefs are more probable jointly than they would be independently.
Formally: C(B) = P(B₁ ∧ B₂ ∧ ... ∧ Bₙ) / [P(B₁) × P(B₂) × ... × P(Bₙ)].
If C > 1, the beliefs are positively coherent (they support each other); if
C < 1, they are incoherent.

The advantage: this is formally precise and decomposes naturally. The
disadvantage: Bovens and Hartmann (2003) proved that this measure can be
misleading — a set of independently likely beliefs can have C > 1 without
being explanatorily coherent. The measure does not distinguish coherence-by-
explanation from coherence-by-coincidence.

**Position C — Hybrid: Typed Constraints with Probabilistic Weights
(D'Agostino)**:
Use Thagard's constraint structure but assign weights to constraints based
on their type and the epistemic probabilities of the connected beliefs.
MECHANISM explanation links get higher weight than ANALOGICAL links.
Competition links between well-supported hypotheses get higher weight than
competition between speculative hypotheses. The coherence metric is the
weighted constraint satisfaction score.

The advantage: this combines structural sensitivity (constraint types) with
quantitative precision (probabilistic weights). The disadvantage: the
weighting scheme introduces free parameters that must themselves be
justified.

**Success condition**: A coherence metric that is (a) computable,
(b) sensitive to edge types, (c) distinguishes coherence-by-explanation from
coherence-by-coincidence, and (d) correctly identifies the CMR web as more
coherent after the Barrett-Craig adoption than before (because the compromise
resolves a competition edge and creates new explanation links).

---

## Crucible 4: Structural Revision — When Does Evidence Change the Web's Structure (Not Just Its Parameters)?

**Charge**: When new evidence arrives, when does the web update parameters
(a THEORETICAL_DEFAULT gets a new value) and when does it revise structure (a
mechanism step is added, removed, or reordered; a theory is promoted or
demoted; a working model is adopted or abandoned)?

**Position A — Threshold Model (Gärdenfors)**:
Structural revision is triggered when parametric updating alone would produce
incoherence. If a new empirical value is close to the THEORETICAL_DEFAULT, the
web updates the parameter and moves on. If the new value is dramatically
different (say, outside the 95% CI of the web's prior), parametric updating
is insufficient — the web must ask whether the mechanism chain itself is
wrong, whether the evidence reflects a new phenomenon, or whether a competing
account has become dominant. Structural revision kicks in when parametric
updating fails to restore coherence.

This approach is conservative: the web's structure is stable unless forced to
change. This protects against premature structural revision driven by noisy
data but risks sluggishness — the web might cling to a wrong structure longer
than it should because the evidence never quite reaches the threshold.

**Position B — Continuous Evaluation Model (Kelly)**:
There is no threshold. The web continuously evaluates whether alternative
structures (different mechanism chains, different theory-tier assignments)
would produce higher coherence than the current structure. Structural revision
happens whenever a better structure is found, regardless of whether the
current structure is "in crisis."

This approach is more responsive but potentially unstable: the web might
oscillate between structures as new evidence arrives. Kelly's formal learning
theory provides convergence guarantees that prevent this — the key is that the
revision strategy must satisfy certain topological constraints (avoiding what
Kelly calls "mind changes" that do not bring you closer to the truth).

**Position C — Problem-Solving Model (Olsson, drawing on Laudan)**:
Structural revision is driven by problem-solving effectiveness, not by
coherence alone. Larry Laudan (1977) argued that scientific theories are
evaluated by how many empirical problems they solve and how few conceptual
problems they generate. Applied to the CMR web: a structural revision is
warranted when the revised structure solves more problems (explains more
template outputs, resolves more competition edges) and generates fewer
problems (introduces fewer new THEORETICAL_DEFAULTs, fewer new competition
edges) than the current structure.

**Success condition**: A formal criterion for when structural revision is
triggered, expressed in terms that are computable from the web's current state.
The criterion must correctly identify the AX4 elevation as a warranted
structural revision (high evidence count, high downstream leverage, resolution
of recurring THEORETICAL_DEFAULTs) and the Aesthetic Anchoring deferral as a
correct non-revision (insufficient evidence, no reduction document, no
competing-account resolution).

---

## Crucible 5: The Bridge Warrant Hierarchy — Discovered or Stipulated?

**Charge**: The CMR's bridge warrant types (CONSTITUTIVE through
THEORETICAL_DEFAULT) form a hierarchy with ceiling values. Is this hierarchy
an empirical discovery about the reliability of different inference types, or
is it a stipulation — a design decision about how much trust to place in
different kinds of evidence?

**Position A — Discovered (Glymour)**:
The hierarchy reflects a genuine epistemological fact: mechanisms provide
stronger evidence than statistical associations, which provide stronger
evidence than analogies. This is not a convention; it is a consequence of the
different kinds of underdetermination that afflict each inference type.
MECHANISM bridges are stronger because a complete causal pathway constrains
the possible confounders more tightly than a statistical correlation.
ANALOGICAL bridges are weaker because the validity of an analogy is always
conditional on whether the relevant similarities outweigh the relevant
differences — and this is underdetermined in ways that mechanism claims are
not.

If the hierarchy is discovered, the ceiling values (0.75, 0.60, 0.50, etc.)
are *approximate measurements* of the reliability of each inference type, and
they can be calibrated empirically by examining historical cases where
mechanism-based inferences turned out to be correct or incorrect.

**Position B — Stipulated (D'Agostino)**:
The hierarchy is a useful convention — a design decision about how much trust
the CMR system should place in different evidence types. There is no
"true" ceiling for MECHANISM bridges. The value 0.60 was chosen because it
seemed reasonable. It could have been 0.55 or 0.65. The hierarchy is a
pragmatic tool for preventing confidence inflation, not a claim about the
world.

If the hierarchy is stipulated, the ceiling values are *tunable parameters*
of the system, and different settings produce different system behaviours.
The right settings are the ones that produce the most useful architectural
recommendations — a pragmatic, not epistemological, criterion.

**Position C — Partially Discovered, Partially Stipulated (Kelly)**:
The ordering of the hierarchy (CONSTITUTIVE > MECHANISM > EMPIRICAL_COVARIANCE
> ... > ANALOGICAL) is a discovered fact about inferential reliability. But
the specific ceiling values are stipulated — they are design choices that
operationalise the discovered ordering. The ordering is objective; the
specific numbers are conventional.

The analogy: temperature is objectively ordered (hot > warm > cold), but the
specific numbers on the Celsius scale are conventional. The hierarchy's
ordering is like temperature ordering; the ceiling values are like degree
markers.

**Success condition**: A principled account of the bridge warrant hierarchy
that specifies: (a) whether the ordering is revisable (can future evidence
show that ANALOGICAL bridges are sometimes MORE reliable than MECHANISM
bridges?), (b) whether the ceiling values are calibratable (is there a
procedure for measuring the actual reliability of each bridge type?), and
(c) how the hierarchy interacts with the formal inference rules (does a
higher-ceiling bridge produce a different inference rule, or does it just
produce a higher confidence bound?).

---

# PART V: CALIBRATION ORDER

```
Phase 1: Foundations (Sessions 1-2)
  1. Bridge warrant hierarchy (Crucible 5) — foundational; semantics
     of warrants govern everything downstream
  2. Reduction edge formalism (Crucible 1) — credence propagation
     through the tier structure
  3. Inheritance edge formalism — parameter sharing and revision
     propagation

Phase 2: Dynamics (Sessions 3-4)
  4. Competition resolution protocol (Crucible 2) — how rival
     hypotheses are evaluated
  5. Partial-out formalism — scope partitioning and double-counting
     prevention
  6. Cross-template interaction formalism — emergent interactions
     and moderator effects

Phase 3: Global Properties (Sessions 5-6)
  7. Coherence metric (Crucible 3) — typed constraint satisfaction
  8. Working model and AX-axiom formalism — meta-level constraints
  9. Structural revision rules (Crucible 4) — when and how the web
     changes shape

Phase 4: Meta-Properties (Sessions 7-8)
  10. Convergence analysis (Kelly) — does the revision strategy
      converge?
  11. Computational tractability analysis (D'Agostino) — is the
      calculus implementable?
  12. Empirical adequacy test (S-7) — does the calculus reproduce
      the CMR's historical decisions?
```

---

# PART VI: CONSTRAINTS

| # | Constraint | Rationale |
|---|-----------|-----------|
| F-01 | All inference rules must be formally specified (no natural-language-only rules) | Ensures implementability |
| F-02 | Every rule must be tested against at least 3 CMR examples (actual decisions or template calibrations) | Ensures empirical adequacy |
| F-03 | The calculus must handle graded belief (credence scores 0-1), not just binary (accept/reject) | The CMR web uses continuous credences |
| F-04 | The calculus must preserve the epistemic/aleatory distinction throughout | The web tracks epistemic probabilities; the BN uses aleatory probabilities; the calculus must not conflate them |
| F-05 | Computational complexity of each rule must be stated (polynomial, exponential, etc.) | Per D'Agostino's requirement: tractability is not optional |
| F-06 | The calculus must specify the interface with the BN: exactly which web outputs become BN inputs, and which BN outputs feed back to the web | Per the WoB-BN architecture document |
| F-07 | All panel members must state their philosophical commitments (realist/instrumentalist, foundationalist/coherentist) at the start, so that disagreements can be traced to their sources | Methodological transparency |

---

# PART VII: RISK ASSESSMENT

| Risk | Severity | Mitigation |
|------|----------|------------|
| Panel members disagree on foundational issues (realism vs. instrumentalism) and cannot converge | High | F-07 requires transparency; Crucible structure forces concrete deliverables even from disagreement |
| Calculus is formally elegant but computationally intractable | High | D'Agostino is specifically assigned to enforce tractability at every step |
| Calculus is tractable but too weak (handles toy examples but not the CMR's real 93-template web) | Medium | S-7 (empirical adequacy test) catches this; every rule tested on 3+ real examples |
| Calculus resolves all Crucible debates by deferring to "judgment" rather than formal rules | High | Success conditions S-1 through S-6 explicitly require formal specifications, not natural-language guidelines |
| Pearl's causal framework dominates and the coherentist/argumentation perspectives are marginalised | Medium | Panel structure gives 3 seats to coherentist/argumentation (Thagard, Prakken, Olsson) vs. 1 to Pearl |
| The calculus is complete but nobody can use it because the documentation is impenetrable | Medium | Deliverable must include a tutorial applying the full calculus to one worked example (the Barrett-Craig adoption decision) |

---

# PART VIII: RELATIONSHIP TO THE CMR DOMAIN PIPELINE

This panel operates outside the domain pipeline (STRESS-I through CROSSCUT-I).
Its deliverable is not a set of calibrated templates but a formal calculus that
operates OVER the calibrated templates. The relationship is:

```
FOUNDATIONS-I deliverable     operates on     CMR domain pipeline output
─────────────────────────     ───────────     ─────────────────────────
Inference rules               →               93 calibrated templates
Coherence metric              →               Web of Belief structure
Revision protocol             →               Future evidence and theory changes
Convergence guarantee         →               Long-term reliability of the system
BN interface specification    →               WoB ↔ BN projection function
```

The domain pipeline provides the CONTENT. FOUNDATIONS-I provides the LOGIC.
Without the content, the logic has nothing to operate on. Without the logic,
the content is a collection of well-argued beliefs with no formal method for
reasoning over them.

---

# PART IX: A NOTE ON AMBITION

This panel attempts something that has not been done before: a complete formal
inference calculus for a typed, hierarchical, multi-theory belief web with
graded credences, multiple edge types, structural revision, and a specified
interface to a causal inference engine.

Thagard's ECHO handles flat coherence networks with binary constraints.
Gärdenfors' AGM handles belief revision in classical logic. Prakken's ASPIC+
handles structured argumentation with defeat relations. Hartmann's Bayesian
coherentism handles probabilistic coherence measures. Kelly's formal learning
theory handles convergence of revision strategies. Pearl's do-calculus handles
causal inference from graphical models.

None of these, alone, is sufficient. The CMR web requires elements from all
of them, integrated into a single framework. This integration is the
intellectual contribution of FOUNDATIONS-I. It may not be fully achievable in
a single panel — but the panel should produce at least a well-specified
*architecture* for the calculus, with formal rules for the most important
edge types and a research programme for the remainder.

If the panel achieves S-1 through S-7, the CMR will have something that no
other knowledge system in environmental science — or, as far as I know, in any
applied science — currently has: a formal epistemological backbone that
specifies not just what is believed but how the beliefs relate to each other,
how they should be revised, and what it means for the system to be getting
closer to the truth.

---

*PANEL_SPECIFICATION_FOUNDATIONS_I.md — CMR Project*
*February 23, 2026*
*Panel: FOUNDATIONS-I (F-01, meta-epistemological)*
*Status: SPECIFICATION COMPLETE — Awaiting human review*
