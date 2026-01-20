# Understanding Bayesian Networks and Beyond: From Pearl to Quine

*An instructional essay for undergraduate students*

**Author:** David Kirsh, with Claude
**Date:** January 20, 2026
**Audience:** Second-year undergraduates with basic probability background

---

## 1. Introduction: What Problem Are We Solving?

Imagine you're a doctor. A patient comes in with a fever, a cough, and fatigue. What's wrong with them? It could be the flu, COVID, a bacterial infection, or dozens of other things. Each symptom gives you *evidence*, but no symptom definitively tells you the diagnosis. You need to *reason under uncertainty*—combine partial, probabilistic evidence to reach the best conclusion you can.

This is the problem that Bayesian Networks were invented to solve. And it turns out to be the same problem we face when trying to understand scientific knowledge: we have many studies, each providing partial evidence, and we need to combine them into coherent beliefs about how the world works.

This essay will explain:
1. What Bayesian Networks are and why Judea Pearl's work was revolutionary
2. How our Article Eater system originally used BN-like ideas
3. Why we moved to something different (a "Quinean Web of Belief")
4. What we gained and what we kept

---

## 2. Probability Basics: The Foundation

Before we can understand Bayesian Networks, we need to understand conditional probability.

### 2.1 Conditional Probability

**Unconditional probability** is what you probably learned first: "The probability of rain tomorrow is 30%." We write this as P(Rain) = 0.3.

**Conditional probability** asks: "Given that I know something, what's the probability of something else?" For example: "Given that there are dark clouds, what's the probability of rain?" We write this as P(Rain | Clouds) — read as "probability of Rain *given* Clouds."

The key insight is that knowing something changes the probabilities of other things. If I see dark clouds, P(Rain | Clouds) might be 0.7, much higher than the unconditional P(Rain) = 0.3.

### 2.2 Bayes' Theorem

Here's where it gets interesting. Sometimes we know P(A | B) but we want P(B | A). For example:
- We might know: P(Cough | Flu) = 0.9 — "If you have the flu, there's a 90% chance you'll cough"
- But we want: P(Flu | Cough) = ? — "If you're coughing, what's the chance you have the flu?"

These are NOT the same number! Most people with the flu cough, but most people who cough don't have the flu (they might have a cold, allergies, or just a dry throat).

**Bayes' Theorem** tells us how to flip conditional probabilities:

```
P(Flu | Cough) = P(Cough | Flu) × P(Flu) / P(Cough)
```

In words: the probability of flu given coughing depends on:
- How likely coughing is if you have flu (0.9)
- How common flu is in general (maybe 0.05 during flu season)
- How common coughing is in general (maybe 0.2)

Plugging in: P(Flu | Cough) = 0.9 × 0.05 / 0.2 = 0.225

So even though 90% of flu patients cough, only about 22.5% of coughing people have the flu. This is called the **base rate fallacy** when people get it wrong—they confuse P(A|B) with P(B|A).

### 2.3 The Curse of Dimensionality

Here's the problem. In the real world, we don't have just two variables (Flu and Cough). A doctor might consider:
- Fever (yes/no)
- Cough (yes/no)
- Fatigue (yes/no)
- Headache (yes/no)
- Nausea (yes/no)
- Recent travel (yes/no)
- Age (young/middle/old)
- Vaccination status (yes/no)
- ... and dozens more

If we have 20 binary variables, the full joint probability distribution has 2²⁰ = 1,048,576 entries. We'd need to specify over a million numbers! This is called the **curse of dimensionality**.

Worse, we'd need millions of data points to estimate all these numbers reliably. No medical dataset is that large.

---

## 3. Judea Pearl's Revolution: Bayesian Networks

### 3.1 The Key Insight: Structure Matters

Judea Pearl, a computer scientist at UCLA, had a crucial insight in the 1980s: **not all variables directly influence each other**.

Consider: Does your vaccination status directly affect whether you have a headache? No! The causal chain is:
```
Vaccination → reduces chance of Flu → Flu causes Headache
```

Vaccination affects headache only *through* its effect on flu. If we know whether you have the flu, knowing your vaccination status tells us nothing more about your headache.

This is called **conditional independence**: Vaccination and Headache are independent *given* Flu.

### 3.2 Graphical Representation

Pearl proposed representing these relationships as a **directed graph**:

```
    Vaccination
         ↓
        Flu  ←  Exposure
         ↓
      Cough    Fever    Fatigue
```

Each arrow means "directly influences." The absence of an arrow means "no direct influence."

This graph encodes conditional independence: Vaccination and Cough are independent given Flu. Fever and Fatigue are independent given Flu. And so on.

### 3.3 Why This Solves the Dimensionality Problem

Instead of specifying 2²⁰ numbers, we only need to specify:
- P(Vaccination) — one number
- P(Exposure) — one number
- P(Flu | Vaccination, Exposure) — four numbers (2×2 combinations)
- P(Cough | Flu) — two numbers
- P(Fever | Flu) — two numbers
- P(Fatigue | Flu) — two numbers

That's about 12 numbers instead of a million!

The graph structure tells us which conditional probabilities we need. Variables only need conditioning on their **parents** (the nodes with arrows pointing to them), not on every other variable.

### 3.4 Inference: Answering Questions

Once we have the network structure and the conditional probabilities (called **Conditional Probability Tables** or CPTs), we can answer questions:

- "Given that the patient has a cough and fever but no fatigue, what's the probability they have the flu?"
- "If we observe that someone was vaccinated and has no fever, what's the probability they were exposed?"

Pearl and others developed efficient algorithms for computing these answers by passing "messages" through the network—much faster than brute-force calculation.

### 3.5 Pearl's Deeper Contribution: Causality

Pearl didn't stop at probability. In his later work (especially his 2000 book *Causality*), he showed how to distinguish **causation** from **correlation**.

The key tool is the **do-operator**. There's a difference between:
- P(Flu | Vaccination = yes) — the probability of flu for people who *happen to be* vaccinated
- P(Flu | do(Vaccination = yes)) — the probability of flu if we *force* everyone to be vaccinated

The first might be confounded: maybe health-conscious people both get vaccinated AND avoid sick people. The second is the true causal effect.

Pearl showed when and how we can compute causal effects from observational data—a huge contribution to statistics, epidemiology, economics, and AI.

---

## 4. What Bayesian Networks Are Good At

### 4.1 Strengths

**1. Principled uncertainty handling.** Every probability is grounded in probability theory. There's no ad-hoc confidence scores—everything follows from Bayes' theorem.

**2. Efficient inference.** For sparse networks (few connections), inference is tractable. We can answer complex queries quickly.

**3. Transparent structure.** The graph shows exactly what influences what. You can look at the network and understand the model.

**4. Combines prior knowledge with data.** We can encode expert knowledge in the structure and priors, then update with data.

**5. Causal reasoning.** With Pearl's extensions, we can reason about interventions ("What if we do X?") and counterfactuals ("What would have happened if we had done X?").

### 4.2 Weaknesses

**1. Fixed ontology.** The variables must be defined upfront. If you built a network with variables {Flu, Cold, Allergies}, you can't easily add "COVID" later without restructuring.

**2. Requires known structure.** Someone must specify which arrows exist. For well-understood domains (like medical diagnosis), experts can do this. For emerging fields, the structure is unknown.

**3. Precise probabilities required.** Each CPT entry needs a number. Where do these come from? Often, experts must guess—"What's P(Fever | Flu)? Um... 0.8?" These guesses can be wrong.

**4. No representation of theoretical disagreement.** If two experts disagree about the structure (Should there be an arrow from X to Y?), the network can't represent this—you have to pick one structure.

**5. Observations are foundational.** Standard BNs assume observed evidence is certain. You observe "Cough = yes" and that's bedrock—no uncertainty about the observation itself.

**6. No "stubs."** Every observation must fit somewhere in the network. If a patient has a symptom you didn't include in your variables, the network can't represent it.

---

## 5. Article Eater Version 1: BN-Inspired Rules

### 5.1 What We Were Trying To Do

Our system, Article Eater, processes scientific papers about how built environments affect people. We wanted to answer questions like:
- "Does having plants in an office reduce stress?"
- "Do curved walls make people more creative?"
- "What's the effect of natural light on mood?"

The literature contains hundreds of studies, each providing partial evidence. We needed to synthesize this into a coherent knowledge structure.

### 5.2 The Rule-Based Approach

Our early system (versions 15-18) extracted **rules** from papers:

```yaml
# A "micro-rule" from a single study
rule_id: "ulrich_1984_r1"
type: "edge"
source: "nature_views"
target: "stress_recovery"
direction: "increases"
confidence: 0.75
evidence:
  paper: "Ulrich (1984)"
  sample_size: 46
  effect_size: 0.52
  p_value: 0.03
```

This is BN-like: we're saying there's a probabilistic relationship between "nature views" and "stress recovery." The confidence score is like a probability.

We also had **meso-rules** that aggregated micro-rules:

```yaml
# A "meso-rule" synthesizing multiple studies
rule_id: "nature_stress_meta"
type: "edge"
source: "natural_environment"
target: "stress_reduction"
direction: "increases"
confidence: 0.82
aggregated_from: ["ulrich_1984_r1", "kaplan_1989_r1", "berto_2005_r1"]
triangulation_score: 0.30  # Multiple measures agree
```

### 5.3 How This Resembled BNs

Like Bayesian Networks, our system:
- Had **nodes** (environmental features, psychological outcomes)
- Had **edges** with strengths (rules connecting nodes)
- Could be exported to actual BN software for inference
- Tracked provenance (which papers supported which edges)

### 5.4 How This Differed from Pearl's Vision

But several things were different:

**1. No true probabilities.** Our "confidence" scores weren't derived from Bayes' theorem. They were weighted composites of factors like sample size, effect size, and methodological quality. Pearl would object: these aren't real probabilities!

**2. Structure extracted from text, not specified by experts.** We didn't have domain experts draw the network. We extracted relationships from papers using natural language processing. This meant we could miss relationships that papers assumed but didn't state.

**3. Multiple theories, no way to represent disagreement.** Different theories (Attention Restoration Theory, Stress Recovery Theory) made different structural claims. Our system couldn't represent this uncertainty—we had to pick a structure.

**4. Evidence was uncertain.** We knew that studies could be wrong, have methodological flaws, or fail to replicate. But the rule structure treated extracted evidence as fixed.

---

## 6. The Problems We Encountered

### 6.1 The Commensurability Problem

Different papers used different concepts. One paper might measure "stress" via cortisol levels. Another might use heart rate variability. A third might use self-report questionnaires.

Are these the same variable? Our BN-like structure needed a fixed ontology, so we had to decide: is "cortisol" the same node as "self-reported stress"? If we said yes, we lost important distinctions. If we said no, we had a fragmented network.

### 6.2 The Directionality Problem

In BNs, causation flows in one direction: parents influence children. Evidence flows backward via Bayes' theorem: observing children updates beliefs about parents.

But in science, the relationship between theory and evidence is more complex:
- Empirical findings can support or challenge theories
- But theories also shape how we interpret findings
- A strong theory can make us skeptical of anomalous data
- While strong data can eventually overturn theories

Our rule-based system had a fixed direction: evidence → confidence in rules. But scientific reasoning is more circular than this.

### 6.3 The Stub Problem

Sometimes we'd extract a finding that didn't fit our ontology:
- "Fractal patterns in architecture reduce mental fatigue"

We didn't have "fractal patterns" in our environment taxonomy or "mental fatigue" (as distinct from "attention fatigue") in our outcome taxonomy.

In a BN, you can't have nodes that don't connect to anything. We either had to force-fit the finding into existing categories (losing information) or ignore it (losing the finding entirely).

### 6.4 The Contradiction Problem

Two studies might report opposite results:
- Study A: "Open offices increase collaboration"
- Study B: "Open offices decrease collaboration"

In a BN, you'd need to pick a single number for P(Collaboration | Open Office). But maybe both studies are correct for different contexts—one studied creative teams, the other studied accountants.

Our BN-like structure couldn't represent "this relationship varies by context" as a first-class object. Context had to be encoded as additional parent nodes, which made the network complex and the conditional probability tables huge.

---

## 7. The Quinean Turn: A Different Philosophy

### 7.1 Who Was Quine?

W.V.O. Quine was a philosopher at Harvard in the mid-20th century. His 1951 paper "Two Dogmas of Empiricism" challenged the standard view of how knowledge works.

**The standard view (foundationalism):**
- Some beliefs are foundational (observations, sense data)
- Other beliefs are derived from foundational ones
- If a derived belief conflicts with observation, revise the derived belief
- Observations themselves are bedrock—never revised

**Quine's view (coherentism):**
- No beliefs are truly foundational
- All beliefs—including "observations"—are revisable
- What matters is **coherence**: how well beliefs fit together
- When we encounter conflict, we can revise *any* belief, including observations
- We tend to revise peripheral beliefs before central ones, but nothing is sacred

Quine used the metaphor of a **web of belief**: knowledge is like a spider's web, with beliefs connected to each other. Pull on one strand and the whole web adjusts. The center of the web is more stable, but even central beliefs can be revised if enough peripheral strands pull hard enough.

### 7.2 What This Means for Our System

Applying Quine's philosophy to Article Eater meant rethinking several assumptions:

**Old assumption:** Extracted evidence is bedrock.
**New assumption:** Extracted evidence is uncertain and revisable. Maybe the extraction was wrong. Maybe the study was flawed. Maybe the study was right but we misinterpreted it.

**Old assumption:** Theories derive support from evidence.
**New assumption:** Theories and evidence mutually constrain each other. A well-supported theory can make us skeptical of anomalous evidence. Accumulated anomalous evidence can eventually overturn a theory.

**Old assumption:** Beliefs must fit in the ontology.
**New assumption:** Beliefs can be "stubs"—present in the web but not yet connected to theory. Stubs are valuable: they indicate potential gaps in our theoretical frameworks.

**Old assumption:** Confidence flows upward (evidence → theory).
**New assumption:** Constraint flows in all directions. Beliefs constrain each other through a network of support and tension relationships.

### 7.3 The Web of Belief Architecture

Our current system implements this philosophy:

**Beliefs** replace rules:
```python
belief = Belief(
    content="Natural views support stress recovery",
    credence=Credence(value=0.75, uncertainty=0.15),
    level=EpistemicLevel.INTERMEDIATE,  # Not bedrock!
    status=BeliefStatus.ESTABLISHED,
    theory="SRT",
    scope=ScopeConditions(population="adults", setting="hospital")
)
```

**Constraints** replace edges:
```python
constraint = Constraint(
    source_id="nature_views_reduce_stress",
    target_id="SRT_core_claim",
    constraint_type=ConstraintType.INSTANTIATES,  # This finding instantiates the theory
    strength=0.7,
    symmetric=False  # Theory supports finding, finding supports theory
)
```

**Equilibrium-seeking** replaces inference:
Instead of computing conditional probabilities, the system seeks **reflective equilibrium**—a state where all beliefs cohere with each other given the constraints. When new evidence arrives, the whole web adjusts, not just the directly affected beliefs.

---

## 8. What We Gained and What We Kept

### 8.1 What We Kept from BNs

**1. Explicit structure.** Like BNs, our web has explicit nodes (beliefs) and edges (constraints). You can inspect the structure and understand what's connected to what.

**2. Probabilistic representation.** We still use numbers (credences) to represent confidence. We didn't abandon quantitative reasoning.

**3. Provenance tracking.** We still know which papers support which beliefs. This is essential for scientific credibility.

**4. Graphical organization.** The web can be visualized as a graph, making it comprehensible.

### 8.2 What We Added

**1. Revisability at every level.** No belief is bedrock. Observations, findings, mechanisms, and theories are all beliefs with credences that can change.

**2. Meta-uncertainty.** We don't just say "credence = 0.75." We say "credence = 0.75 ± 0.15"—we're uncertain about our uncertainty. This is more honest about our epistemic state.

**3. Stubs.** Findings can exist without theoretical homes. The system tracks them and flags them as potential research opportunities.

**4. Bidirectional constraint.** In a BN, causation flows from parents to children. In our web, constraints flow in multiple directions. A well-supported theory constrains what findings we expect; unexpected findings constrain how much we trust the theory.

**5. Scope conditions.** Every belief has explicit scope: what population, setting, duration, methodology does it apply to? This lets us represent "X reduces stress *for adults in hospital settings*" rather than overgeneralizing.

**6. Conflict categorization.** When beliefs conflict, we don't just average them. We categorize the conflict:
   - Genuine contradiction (one must be wrong)
   - Scope boundary (both are right, in different contexts)
   - Methodological divergence (different methods, different results)
   - Precision boundary (both are right within their confidence intervals)

**7. Bridge warrants.** We can represent connections across theories. If Stress Recovery Theory and Attention Restoration Theory both predict that nature reduces stress, we can represent a "bridge" between them, tracking how evidence for one provides partial support for the other.

### 8.3 What We Lost (And Why It's Okay)

**1. True Bayesian probabilities.** Our credences aren't derived from Bayes' theorem. Pearl would object that they're not "real" probabilities.

*Why it's okay:* We're not doing inference in the BN sense. We're tracking scientific beliefs, which have a different character than medical diagnosis or fault detection. Scientists don't actually update beliefs via Bayes' theorem—they use judgment, weighing evidence quality, replication, and theoretical fit.

**2. Efficient exact inference.** BN inference algorithms can compute P(X|Y) exactly (for tractable networks). Our equilibrium-seeking is approximate and iterative.

*Why it's okay:* We're not trying to compute precise conditional probabilities. We're trying to maintain a coherent representation of scientific knowledge. Approximate coherence is more useful than precise probabilities over a dubious structure.

**3. Guaranteed convergence.** BN message-passing provably converges for certain network types. Our equilibrium-seeking might not converge, or might have multiple equilibria.

*Why it's okay:* Science itself doesn't always converge! Sometimes there are genuinely competing frameworks. Our system should represent this, not force artificial convergence.

---

## 9. A Concrete Example

Let's trace how the two systems would handle the same evidence.

### The Evidence

A new paper reports: "In a study of 50 hospital patients, those with window views of trees had 15% shorter hospital stays than those with views of a brick wall (p < 0.05)."

### BN-Style Processing (Old System)

1. Extract rule: "nature_views → shorter_hospital_stay, strength=0.65"
2. Add to network as edge
3. Propagate: this increases confidence in connected rules
4. Done

Problems:
- What if "shorter_hospital_stay" isn't in our ontology? Force-fit or ignore.
- What if another study found no effect? Average the confidences.
- We can't represent that this is a single study with N=50 (modest evidence).

### Quinean Processing (New System)

1. Extract belief:
   ```
   content: "Nature window views associated with shorter hospital stays"
   credence: 0.65 ± 0.20  (modest confidence, high uncertainty due to small N)
   level: EMPIRICAL
   scope: {population: "surgical patients", setting: "hospital", geography: "Pennsylvania"}
   source: "Ulrich 1984"
   ```

2. Create constraints:
   ```
   This belief INSTANTIATES "SRT predicts nature reduces stress" (strength: 0.6)
   This belief SUPPORTS "Nature has beneficial health effects" (strength: 0.5)
   ```

3. Check for conflicts:
   - Found: Another belief says "Window views show no health benefit (Smith 2020)"
   - Analyze: Different populations (surgical vs. general patients)
   - Categorize: SCOPE_BOUNDARY, not genuine contradiction
   - Both beliefs remain with their credences

4. Seek equilibrium:
   - SRT theory credence slightly increases (it predicted this)
   - ART theory credence slightly increases (via bridge warrant to SRT)
   - The "no benefit" finding is recognized as non-contradictory (different scope)

5. Track metadata:
   - This is one study (n=1 for replication count)
   - Small sample (N=50)
   - High ecological validity (real hospital, real patients)
   - Scope is narrow (one hospital in Pennsylvania, 1984)

What we gained:
- Uncertainty is explicit (±0.20)
- Scope conditions are preserved
- Apparent contradiction is diagnosed as scope boundary
- Multiple theories updated through bridge warrants
- Metadata tracked for future analysis

---

## 10. Summary: Two Ways of Thinking About Knowledge

| Aspect | Bayesian Network | Quinean Web |
|--------|------------------|-------------|
| **Foundation** | Observations are bedrock | Nothing is bedrock |
| **Structure** | Fixed ontology, specified edges | Emergent structure, revisable |
| **Numbers** | True probabilities from Bayes | Credences with meta-uncertainty |
| **Flow** | Causation: parents→children. Evidence: children→parents | Mutual constraint in all directions |
| **Conflict** | Must resolve (one number per edge) | Can coexist (scope boundaries, etc.) |
| **Misfits** | Must fit ontology or be discarded | Can be stubs awaiting integration |
| **Inference** | Compute P(Query \| Evidence) | Seek reflective equilibrium |
| **Philosophy** | Foundationalist | Coherentist |

Pearl's Bayesian Networks are brilliant tools for domains with:
- Known structure (experts can draw the graph)
- Stable ontology (variables don't change)
- Real probabilities (derived from data or well-calibrated expertise)
- Clear separation between evidence and hypothesis

Our Quinean Web is designed for scientific knowledge synthesis, where:
- Structure is contested and evolving
- New concepts emerge from the literature
- "Probabilities" are credences based on judgment
- Theory and evidence mutually constrain each other

We haven't abandoned Pearl—we've built on his insights while adapting them to a different problem. The explicit structure, the quantitative representation, the graphical organization—these all come from the BN tradition. But the philosophy of knowledge that governs how the system behaves is Quinean: coherentist, holistic, and humble about what counts as bedrock.

---

## 11. Conclusion: Standing on Shoulders

Judea Pearl revolutionized how we reason under uncertainty. His Bayesian Networks showed that we can represent complex probabilistic relationships compactly and reason about them efficiently. His work on causality showed how to distinguish correlation from causation—arguably the most important inferential distinction in science.

Our Article Eater system owes much to Pearl. The idea that knowledge has structure, that this structure can be represented graphically, that we can compute with it—all of this comes from the BN tradition.

But science is messier than medical diagnosis. The ontology shifts. Theories compete. Evidence is uncertain and revisable. Findings don't always fit. For this domain, we needed a different philosophical foundation: Quine's web of belief, where coherence replaces derivation and nothing is immune from revision.

The result is a system that retains Pearl's strengths—explicit structure, quantitative reasoning, graphical representation—while adding capabilities for handling the genuine complexity of scientific knowledge: uncertainty at every level, scope conditions, stub findings, bidirectional constraint, and honest representation of what we know and what we don't.

Pearl gave us tools for reasoning under uncertainty. Quine gave us a philosophy for reasoning about knowledge itself. Our system tries to combine both.

---

## Further Reading

**On Bayesian Networks:**
- Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann. [The foundational text]
- Murphy, K. (2012). *Machine Learning: A Probabilistic Perspective*. MIT Press. [Chapter 10 for a modern treatment]

**On Causality:**
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge. [The definitive work]
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why*. Basic Books. [Accessible popular science version]

**On Quine and Coherentism:**
- Quine, W.V.O. (1951). "Two Dogmas of Empiricism." *Philosophical Review*. [The original manifesto]
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard. [Systematic coherentism]

**On Scientific Knowledge:**
- Kuhn, T. (1962). *The Structure of Scientific Revolutions*. Chicago. [How science actually changes]
- Lakatos, I. (1978). *The Methodology of Scientific Research Programmes*. Cambridge. [Research programs and their evolution]

---

*Essay prepared for COGS 101 students, January 2026*
