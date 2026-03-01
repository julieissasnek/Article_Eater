# MASTER_DOC SUPPLEMENT — February 25, 2026 Session

## Integration Instructions for Cowork

This supplement contains new intellectual content from the February 25, 2026
Opus/Chat session that should be integrated into MASTER_DOC_CMR. The material
falls into three categories:

**Category A — New sections to add.** These contain original analysis not
present in the master doc. They should be inserted at the specified locations.

**Category B — Deepening of existing sections.** These refine or extend
material already in §36–39, §49, §85–88. They should be merged into those
sections rather than duplicated.

**Category C — Technical appendices.** These contain pseudocode, formal
specifications, and testing protocols that should be placed in appendix
sections for reference without disrupting the narrative flow.

---

# CATEGORY A: NEW SECTIONS

---

## §125: The Epistemic-Aleatory Distinction and Its Architectural Consequences

**Insert after**: §88 (Mechanism Chain Traversal) or as new Part XIV opener

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md §14

### Core Argument

The CMR system tracks two fundamentally different kinds of probability, and
confusing them produces bad science.

**Aleatory probability** describes the inherent randomness of the world. When
we say "the probability that this occupant will report positive mood given high
daylight is 0.70," we describe a frequency in the population. This is what
the BN computes.

**Epistemic probability** describes our uncertainty about the world. When we
say "our confidence that the daylight → 5-HT → mood pathway is correctly
specified is 0.45," we describe our state of knowledge. This is what the web
tracks.

The bridge warrant types are *categorisations of epistemic uncertainty* — they
tell you WHY your confidence is at its current level (because you have a
complete mechanism, or a statistical correlation, or are reasoning from
analogy). The distinction matters practically because the two kinds of
probability respond to different interventions: aleatory uncertainty is reduced
by collecting more data from the same process; epistemic uncertainty is reduced
by improving the theoretical model.

The BN's CPTs should contain aleatory probabilities. The web's confidence
scores contain epistemic probabilities. The projection from web to BN
involves a translation from epistemic to aleatory — a lossy conversion that
discards the warrant type, the Toulmin justification, the competing accounts,
and the qualifier/rebuttal structure. This is why the BN must be a derived
projection, not the primary representation.

### The CPT Elicitation Problem

The conditional probabilities between mechanism steps are never made explicit
in the panel outputs. The Toulmin justifications contain effect sizes (which
are not conditional probabilities), confidence scores (which are epistemic,
not aleatory), warrant types (which constrain ceilings, not CPTs), and
qualifiers/rebuttals (which define domain restrictions, not numerical values).

A CPT elicitation protocol is needed — a structured method that converts
Toulmin evidence into explicit CPT entries:

1. Start with the effect size from the strongest study; convert to base rate
2. Apply bridge warrant discount: CONSTITUTIVE = 0.90, MECHANISM = 0.75,
   EMPIRICAL_COVARIANCE = 0.70, FUNCTIONAL = 0.60, CAPACITY = 0.55,
   ANALOGICAL = 0.45, THEORETICAL_DEFAULT = 0.50
3. Apply qualifier narrowing (domain-specific conditions)
4. Assign uncertainty bands from the rebuttal
5. Adjust for competing accounts

This protocol should be formalised and applied retroactively to the calibrated
corpus after CROSSCUT-I completes.

---

## §126: The BN's Irreducible Contribution — Do-Calculus and Counterfactuals

**Insert after**: §125, or merge into §85

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md §9 (revised)

### Narrowing the BN's Role

The web can compute quantitative consequences through its own mechanism chains
by compositional reasoning. When the web says "daylight increases 5-HT
synthesis (d = 0.38) AND 5-HT moderates wanting-liking balance (d = 0.45)
AND wanting drives approach (d = 0.55)," the web can propagate these values
compositionally.

The BN's unique, irreducible contribution is twofold:

1. **Interventional reasoning (do-calculus).** The web cannot formally
   distinguish observing that daylight is high from intervening to make it
   high. The BN severs incoming causal edges on intervention (Pearl, 2009)
   and handles confounding, selection bias, and the see/do distinction.

2. **Counterfactual reasoning.** "Given that we observed low mood, WOULD mood
   have been positive if daylight had been high?" requires structural
   equations and do-calculus machinery the web's qualitative mechanism
   reasoning cannot replicate.

This narrowing is important: it means the web is more self-sufficient than
previously assumed. The BN provides causal logic, not quantitative
computation. The web provides everything else.

---

## §127: Reflective Equilibrium as a Formal Operation

**Insert after**: §126, or merge into §49.4

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md §13

The concept from Goodman (1955) and Rawls (1971) describes mutual adjustment
between principles and particular judgments. The CMR panel process IS a
structured method for achieving reflective equilibrium:

- Round Table: presents general principles (each expert's T1 framework)
- Crucible: tests principles against particular findings and competing accounts
- Calibration: adjusts both principles (working models, T1.5 reductions) and
  particular findings (template parameters, confidence scores) until coherence

The Barrett-Craig two-stage model is a reflective equilibrium outcome: neither
Barrett's pure constructionism nor Craig's pure labelled-line theory survived
intact; both were adjusted until they cohered with the full evidence.

A BN cannot achieve reflective equilibrium because it has no principles — only
parameters. BN parameters are revised by Bayes' rule in response to evidence.
Reflective equilibrium adjusts beliefs in response to coherence with OTHER
beliefs. These are different epistemic operations.

---

## §128: FOUNDATIONS-I — Toward a Formal Inference Calculus for the Web

**Insert as**: New Part (Part XV: META-EPISTEMOLOGICAL FOUNDATIONS)

**Source**: PANEL_SPECIFICATION_FOUNDATIONS_I.md

### 128.1 The Problem

The CMR web has ~130 nodes, ~400 edges, 8 edge types. It can answer lookup
and compositional queries. What it cannot do is reason formally over its own
structure. When the system adopts Barrett-Craig, elevates AX4, or defers
Aesthetic Anchoring, these are informal expert judgments. A formal inference
calculus would make these derivable from explicit rules.

### 128.2 The Eight Edge Types (Exhaustive Inventory)

1. **REDUCTION** (T1 → T1.5 → T2): higher-tier belief explained by lower-tier
   mechanism. Open: multi-parent conjunction vs. disjunction.
2. **BRIDGE WARRANT** (7 subtypes: CONSTITUTIVE through THEORETICAL_DEFAULT):
   connects theoretical claim to evidence with typed inferential bridge.
3. **COMPETITION**: rival hypotheses for same evidence. Three outcomes: victory,
   compromise (domain partition), equilibrium.
4. **CROSS-TEMPLATE INTERACTION**: shared mechanism or environmental input.
5. **INHERITANCE**: parameter sharing across templates.
6. **WORKING MODEL**: theoretical commitment constraining multiple templates.
7. **AX-AXIOM**: meta-parameter modifying all templates.
8. **PARTIAL-OUT**: scope partition preventing double-counting.

### 128.3 The FOUNDATIONS-I Expert Panel

Nine experts: Thagard (coherence), Glymour (theory-evidence bridge),
Hartmann (Bayesian coherentism), Gärdenfors (belief revision), Prakken
(argumentation), Kelly (formal learning theory), Pearl (causal inference),
Olsson (collective belief), D'Agostino (computational tractability).

### 128.4 Five Crucible Debates

1. Credence propagation through reduction: conjunctive vs. disjunctive vs.
   compositional
2. Competition resolution: argumentation defeat vs. Bayesian updating vs.
   reflective equilibrium
3. Coherence metric: constraint satisfaction vs. probabilistic measure vs.
   hybrid
4. Structural revision: threshold vs. continuous vs. problem-solving
5. Bridge warrant hierarchy: discovered vs. stipulated

### 128.5 Seven Success Conditions

S-1: Formal semantics for every edge type
S-2: Credence propagation rules (implementable)
S-3: Competition resolution protocol
S-4: Global coherence metric (computable)
S-5: Structural revision rules (AGM-compliant)
S-6: Convergence guarantee
S-7: Empirical adequacy (reproduce 4/5 historical CMR decisions)

---

## §129: Six Algorithms for Web Inference

**Insert as**: Technical Appendix to §128

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md Part IX

### 129.1 Algorithm 1 — Typed Credence Propagation

Iterative message-passing with typed attenuation factors. Each edge type has
a different α (reduction 0.90, MECHANISM bridge 0.75, ANALOGICAL 0.45, etc.).
Multi-parent nodes use noisy-OR for complementary T1 parents, max for
overlapping. Entrenchment constrains revision speed: T1 nodes lose at most
0.01 credence per iteration; T2 nodes revise freely. Complexity: O(iter × |E|).
For CMR (~400 edges, 1000 iterations max): milliseconds.

### 129.2 Algorithm 2 — Graded Competition Resolution

Computes attack strength between competing hypotheses using Toulmin structure
comparison. Produces VICTORY (>0.30 net advantage), COMPROMISE (domain
partition detected), or EQUILIBRIUM (interval-valued credences).
Complexity: O(k² × |T|). Trivial for CMR's typical 2–3 way competitions.

### 129.3 Algorithm 3 — Typed Coherence Metric

Weighted constraint satisfaction over all edges. Positive constraints
(reduction, inheritance, etc.) contribute positively when both connected
nodes have high credence. Competition edges contribute positively when
resolved, negatively when in equilibrium. Produces global score C ∈ [-1, 1]
plus diagnostic decomposition by edge type and by node. Complexity: O(|E|).

### 129.4 Algorithm 4 — Structural Revision

AGM-style with entrenchment ordering. New evidence triggers: (1) impact
assessment (which nodes change?), (2) revision type classification (parametric
vs. structural), (3) greedy minimal revision in entrenchment order (least
entrenched first), (4) coherence verification. Defers to human review when
greedy revision fails. Complexity: O(|affected| × |E|).

### 129.5 Algorithm 5 — Value of Information

Perturbation-based sensitivity analysis. For each uncertain parameter:
simulate optimistic resolution, simulate pessimistic resolution, compute
average absolute coherence change, multiply by downstream reach (BFS).
Produces ranked research agenda. Complexity: O(|uncertainties| × (|E| + |N|)).

### 129.6 Algorithm 6 — BN Projection

Compresses mechanism chains into BN edges between observable/manipulable
variables. CPTs derived from product of step probabilities with typed
attenuation. Checks DAG property and conditional independence. Lossy by
design — epistemic structure discarded. Complexity: O(|chains| × |length| + |V|³).

### 129.7 Complexity Summary

All algorithms polynomial. All complete in milliseconds for the CMR's actual
graph (~130 nodes, ~400 edges). The calculus is implementable as real-time
interactive software.

---

## §130: Testing the Calculus — Five Levels

**Insert after**: §129

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md Part VIII

Level 1: **Internal consistency** — sanity checks (credences in [0,1],
termination, no scope overlaps). Software task.

Level 2: **Retrodiction** — reproduce 5 major decisions + 50–100 micro-
decisions from panel history. Score: >80% = strong, 60–80% = moderate, <60%
= calculus needs revision.

Level 3: **Prediction** — before CROSSCUT-I execution, predict which AX
parameters are most contested, whether ecological rationality achieves
EMPIRICAL_COVARIANCE, and how Aesthetic Anchoring evaluation resolves. Seal
predictions. Compare after.

Level 4: **Cross-domain transfer** — apply calculus to air-pollution-cognition
or psychedelic-therapy domains. If domain experts find outputs reasonable, the
calculus is domain-general.

Level 5: **Adversarial stress testing** — pathological webs (credence cycles,
contradictory inheritance, total competition equilibrium, 1000-node scale).

**Ultimate test**: Can the calculus discover something the human experts
missed? A non-obvious consequence of the web's structure that follows from
formal rules but was invisible to informal reasoning.

---

## §131: Three Frontiers

**Insert after**: §130

**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md Part VII

### 131.1 Temporal Dynamics

The web has a history. Coherence trajectory across panels. Path dependence
question: would different panel ordering produce a different web? Markov chain
ergodicity analogy.

### 131.2 Imprecise Credences

Irresolvable competitions → interval-valued credences (Levi, 1980;
Walley, 1991). Propagate through both web and BN. Produces honestly wide
predictions where science is genuinely unsettled.

### 131.3 Meta-Uncertainty

The calculus is itself a theory. Meta-credences on inference rules.
Pragmatic resolution: one level of meta-uncertainty, sensitivity analysis
over algorithmic parameters (α values, thresholds).

---

# CATEGORY B: DEEPENING OF EXISTING SECTIONS

---

## For §49 (Quinean Webs and Bayesian Networks)

**Add to §49.5**: The web can do its own compositional quantitative reasoning
along mechanism chains. The BN's unique contribution is narrowed to
do-calculus (interventional reasoning separating causation from association
in presence of confounders) and counterfactual reasoning. This is a stronger
claim than the current §49.5 makes — it means the web is nearly
self-sufficient for everything except formal causal inference.

**Add to §49.7**: Haack's critique (coherence underspecified) now has a
proposed answer: the FOUNDATIONS-I panel specification (§128) addresses this
directly by specifying a formal coherence metric (Algorithm 3) with typed
constraint satisfaction.

## For §70 (NEUROMOD-I)

**Add**: The Opus review (OPUS_REVIEW_NEUROMOD_I_FINAL.md) cleared NEUROMOD-I
as "best panel in the pipeline." Key results: T29 verification confirmed
(12/12 constraints, 1 mild double-count accepted); differential-mode model
formally adopted as third CMR working model (alongside Barrett-Craig and,
pending CROSSCUT-I, potentially Aesthetic Anchoring); NM4 incentive
sensitisation retained despite 0.40 ANALOGICAL confidence; Lambert et al.
(2002) 5-HT pathway flagged for literature review.

## For §85 (BN-Web Relationship)

**Add**: The current §85 treats the BN-Web as bidirectionally constraining
with roughly symmetric contributions. The Feb 25 analysis sharpens this: the
web is epistemically primary and can compute quantitative consequences on its
own. The BN's unique contribution is interventional reasoning (do-calculus)
and counterfactuals — not quantitative prediction, which the web can do by
compositional chain propagation. The flow diagram should be updated to reflect
the asymmetric relationship (see §126).

## For §56.2 (12-Panel Roster)

**Update**: Template counts now reflect actual panel outputs: CREATIVE-I = 7
(not 7), NEUROMOD-I = 11 (expanded from 7), CROSSCUT-I = 17 (expanded from
15). Total calibrated: 93 (pipeline) + pre-pipeline. Update panel roster
accordingly.

## For §56.4 (What Each Panel Contributes)

**Add**: NEUROMOD-I contributed the T29 allostatic load master template (the
most cross-connected template in the corpus), the Dayan computational
taxonomy (DA = reward PE, NE = unexpected uncertainty, ACh = expected
uncertainty, 5-HT = aversive prediction), and convergence with CREATIVE-I
on the differential-mode model. CROSSCUT-I contributed AX3 awe templates
(resolving orphaned VISUAL-I cross-template flags), the three-tier individual
differences model including neurodiversity, and the era-dependent VR
limitation discount.

---

# CATEGORY C: COWORK NEW-FILES ALERT SPECIFICATION

---

## New-Files Integration Monitor

### Purpose

Automated detection of new or modified files in the CMR project that may
contain material warranting integration into MASTER_DOC_CMR.

### Monitored Locations

```
/mnt/user-data/outputs/          — Opus/Chat session outputs
/mnt/user-data/uploads/          — User-uploaded documents
```

### File Patterns That Trigger Alerts

```
REVIEW_*                         — Panel reviews (pre-panel or post-panel)
OPUS_REVIEW_*                    — Opus clearance reviews
*_Panel_Output.md                — Panel execution outputs
TRANSFER_*.md                    — Session transfer documents
WEB_OF_BELIEF_*                  — Architectural philosophy documents
PANEL_SPECIFICATION_*            — New panel specifications
CMR_ARCHITECTURE_*               — Architecture explanation updates
```

### Alert Format

When Cowork encounters a new file matching the patterns above, it should:

1. Read the file
2. Compare its content against the MASTER_DOC table of contents
3. Classify new material as:
   - **A (New Section)**: content not covered by any existing section
   - **B (Deepening)**: content that extends an existing section
   - **C (Technical Appendix)**: pseudocode, formal specs, testing protocols
4. Generate an integration brief:
   ```
   INTEGRATION ALERT
   File: [filename]
   Date: [date]
   Classification: A/B/C
   Target section(s): §[number]
   Summary: [2-3 sentences on what's new]
   Priority: HIGH/MEDIUM/LOW
   ```

### Current Backlog (Feb 25, 2026)

Files produced this session needing integration:

| File | Classification | Target | Priority |
|------|---------------|--------|----------|
| WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md | A (§125–131) | New Part XV | HIGH |
| PANEL_SPECIFICATION_FOUNDATIONS_I.md | A (§128) | New Part XV | HIGH |
| OPUS_REVIEW_NEUROMOD_I_FINAL.md | B | §70 | MEDIUM |
| REVIEW_CROSSCUT_I_CLEARANCE.md | B | §71 | MEDIUM |
| REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md | B | §69 | MEDIUM |
| REVIEW_NEUROMOD_I_CLEARANCE.md | B | §70 | MEDIUM |

### Implementation Note

This alert system should be implemented as a check at the START of every
Cowork session: "Are there new files in outputs/ or uploads/ that match
the monitored patterns and have not yet been integrated into MASTER_DOC?"
If yes, generate integration alerts before proceeding with other work.

---

# INTEGRATION PRIORITY ORDER

1. **§125–126** (epistemic-aleatory distinction + narrowed BN role) — these
   sharpen the existing §49 and §85 significantly
2. **§128** (FOUNDATIONS-I specification) — entirely new intellectual content
3. **§129** (six algorithms) — makes §128 operational
4. **§130** (testing protocol) — makes §129 testable
5. **§127** (reflective equilibrium) — philosophical deepening of §49
6. **§131** (three frontiers) — research directions
7. **Category B updates** to §49, §70, §85, §56 — corrections and additions

---

*MASTER_DOC_SUPPLEMENT_Feb25.md — CMR Project*
*Generated by Opus/Chat, February 25, 2026*
*For integration by Cowork into MASTER_DOC_CMR*
