# Expert Panel Deliberation: QA System Personalization

**Date**: March 2, 2026
**Convened by**: David Kirsh, UCSD Cognitive Science
**Panel Members**: 8 expert researchers across cognitive science, HCI, science communication, and epistemology

---

## Panel Composition

1. **Personalization Researcher** (Brusilovsky tradition)
   - **Expertise**: User modeling, adaptive hypermedia, recommender systems
   - **Key contribution**: Dimensional framework for personalization; how to avoid oversimplification

2. **Science Communication Specialist** (Schiefele/Hidi tradition)
   - **Expertise**: Interest, engagement, explanatory styles; science for diverse audiences
   - **Key contribution**: Vocabulary register; what makes explanations compelling per audience

3. **HCI Expert - Explanatory Interfaces** (Shneiderman tradition)
   - **Expertise**: Progressive disclosure, overview+detail, visual information seeking
   - **Key contribution**: Answer structure; how to layer information; interaction design

4. **Cognitive Load Theorist** (Sweller/Paas tradition)
   - **Expertise**: Managing information complexity; cognitive load measurement
   - **Key contribution**: When to simplify, when to elaborate; load vs learning trade-offs

5. **Expert-Novice Differences Researcher** (Chi/Ericsson tradition)
   - **Expertise**: How domain experts vs novices process information differently
   - **Key contribution**: What experts want (deep, contrastive); what novices need (scaffolding)

6. **Architectural Practice Expert**
   - **Expertise**: Real-world design constraints, decision-making under uncertainty
   - **Key contribution**: What practitioners actually need; actionability requirements

7. **Evidence-Based Design Researcher**
   - **Expertise**: Design research, effect sizes, mechanisms, scope conditions
   - **Key contribution**: How to communicate evidence quality; what counts as actionable

8. **Computational Epistemologist**
   - **Expertise**: Credence, Bayesian reasoning, epistemic integrity, representation of uncertainty
   - **Key contribution**: How to ensure personalization doesn't distort truth; guardrails

---

## Q1: What Should ACTUALLY Differ Between User Types?

### Opening: The Personalization Researcher's Case

**Brusilovsky specialist**: "Personalization isn't just depth. True personalization changes the **content structure**, not just the presentation. What differs across users:

1. **Presupposition frame** — what background knowledge is assumed
2. **Information architecture** — what gets foregrounded vs backgrounded
3. **Vocabulary and terminology** — which words mean what
4. **Epistemological stance** — how certain/uncertain we sound
5. **Actionability** — is the answer a decision tool or intellectual resource?

The mistake most systems make: generate one canonical answer, then simplify it for novices. That's cosmetic. Real personalization changes the question itself."

### Architect's Perspective (Spatial Thinking)

**Architectural practice expert**: "An architect asks a fundamentally different question than a researcher.

- **Architect**: 'What should I build? What parameters should I specify in my design document?'
- **Researcher**: 'What do we know? What's contested? What would change if X were false?'
- **Student**: 'How do I understand this field and find my place in it?'

The architect doesn't want a literature review. They want: threshold values, trade-offs, costs, measurement strategy. They need to justify their choices to clients and contractors.

A researcher wants the opposite: they want to know the heterogeneity, confounds, mechanism debates. They want to design the next study."

### The Student's Case (Learning Trajectory)

**Cognitive load theorist**: "Novices face a different cognitive challenge. They're building a mental model from scratch. They need:

1. **Scaffolding**: Build from simpler to complex ideas
2. **Conceptual connection**: Link to what they already know
3. **Exemplars and non-exemplars**: 'Here's what ART is (exemplar); here's what it's NOT (non-exemplar)'
4. **Open questions**: Show where learning can continue
5. **Cognitive apprenticeship**: Expose expert problem-solving, not just conclusions

An expert doesn't need scaffolding; they're building on existing structures. They want nuance, competing interpretations, mechanism challenges."

### The Systematic Reviewer's Demand (Reproducibility)

**EBD researcher**: "Reviewers have a completely different contract with the system. They need:

- **Structured, machine-readable data** (not narrative)
- **Reproducibility**: exactly which studies, inclusion/exclusion criteria applied
- **Completeness**: all studies, all effect sizes, not a curated summary
- **Standardized format**: exportable to RevMan, Covidence, or statistical software
- **Zero interpretation**: just the facts; they'll interpret

This user doesn't want beautiful prose. They want a CSV they can import into R."

### The Quick-Lookup User (Decisiveness)

**Science communication specialist**: "Some users don't have time for nuance. They need a **fast signal** about a factual claim. The communication principle is **trust-first**: give them enough confidence to decide quickly.

But—and this is critical—quick doesn't mean wrong. We can't say 'Plants definitely reduce stress' just because it's faster. We need to be **concise yet honest**: 'Yes, moderate confidence, 65%. Main caveat: only 5 rigorous studies.'"

### Consensus: Five Genuinely Different Cognitive Modes

The panel converges: **The five user types represent fundamentally different cognitive modes**, not just different reading levels.

| User Type | Cognitive Mode | Information Need | Decision Context |
|-----------|---|---|---|
| **Architect** | **Goal-directed pragmatism** | Actionable specifications | Real-world constraint satisfaction |
| **Researcher** | **Epistemic critique** | Evidence quality & heterogeneity | Advancing the field; designing next study |
| **Student** | **Schema construction** | Conceptual frameworks & examples | Building expertise; finding research direction |
| **Reviewer** | **Systematic reproducibility** | Structured, complete data | Synthesis and meta-analysis |
| **Quick Lookup** | **Rapid signal extraction** | Headline + credence + caveat | Fast decision-making under time pressure |

---

## Q2: What is Completeness for Each User Type?

### The Architect's Complete Answer

**Architectural practice expert**: "A complete answer for an architect has these layers:

1. **Design parameter(s)**: Specific, measurable values
   - *Bad*: 'Biophilic elements are good'
   - *Good*: 'Ceiling height >10 ft correlates with creative cognition; evidence threshold at 9.8 ft'

2. **Scope of applicability**: For whom, where, when
   - *Example*: 'Applies to knowledge work in offices with daylighting; weaker in manual labor'

3. **Evidence strength**: EBD level, number of studies, effect size range
   - *Example*: 'EBD Level B (5 RCTs, 12 observational); median d = 0.48'

4. **Practical implications**: What to do, what to avoid, trade-offs
   - *Example*: 'Use living plants (artificial doesn't work); proximity <3m matters; requires maintenance'

5. **Measurement strategy**: How to know it worked
   - *Example*: 'KPIs: employee stress (survey), sick days, productivity. Proxy: satisfaction with workspace'

6. **Contraindications**: When it doesn't apply or backfires
   - *Example*: 'May increase stress for agoraphobic workers; avoid in sealed buildings with poor ventilation'

7. **Cost-effectiveness**: ROI or priority ranking
   - *Example*: 'Low cost (~$100 per 20m²), high ROI if stress-related sick days > 1 per year per worker'

Everything else is optional or subordinate."

### The Researcher's Complete Answer

**Expert-novice researcher**: "A complete answer for a researcher is nearly the opposite:

1. **Effect sizes** with confidence intervals or full distribution
2. **Mechanism(s)** with supporting evidence at each causal step
3. **Scope conditions** with **evidence for each** (not speculation)
4. **Methodology summary**: Common designs, sample sizes, measurement
5. **Quality issues**: Publication bias, replication rate, contested interpretations
6. **Heterogeneity**: Effect size varies by what? Which moderators?
7. **Competing explanations**: Alternative theories that fit some data
8. **Research gaps**: What would advance the field
9. **Uncertainty quantified**: Credence intervals, not point estimates
10. **Conflicts**: Where does the community disagree and why

Practical thresholds are **not relevant**. If I'm a researcher, I design my own thresholds."

### The Student's Complete Answer

**Cognitive load theorist**: "A complete answer for a student includes:

1. **Theoretical framework** explained from first principles
2. **Key papers** with context about why they matter
3. **Evidence hierarchy**: Established, contested, speculative
4. **Theory map**: How this theory connects to others
5. **Historical context**: How did we get here? What changed?
6. **Practitioner applications** (if any): Does this matter outside academia?
7. **Methods commonly used** and their strengths/limitations
8. **Open questions**: Interesting research directions
9. **Field politics** (gently): Who disagrees about what
10. **Learning path**: 'If you want to master this, here's the sequence'

The goal is **schema construction**, not decision-making."

### The Reviewer's Complete Answer

**EBD researcher**: "A complete answer for a systematic reviewer is:

1. **Study-level data** (exportable table):
   - Study ID, authors, year, design, N, population, outcome, effect size, 95% CI, quality score

2. **GRADE assessment** for each outcome

3. **Inclusion/exclusion criteria** documented (reproducibility)

4. **Heterogeneity metrics**: I², Q test, explanation of variance sources

5. **Publication bias assessment**: Funnel plot, Egger test, trim-fill

6. **Sensitivity analyses**: Remove low-quality studies, show effect change

7. **Subgroup analyses**: Effects by population, setting, intervention type

8. **Forest plot data**: Ready for meta-analysis software import

9. **Search strategy** documented: databases, search terms, selection process, inter-rater agreement

10. **Excluded studies**: High-quality studies that didn't meet inclusion criteria

Everything else is the reviewer's job. Don't interpret; just structure."

### The Quick Lookup's Complete Answer

**Science communication specialist**: "A complete quick answer is:

1. **Headline**: Yes/No/Probably with credence
2. **Credence level**: High/Moderate/Low (and why in one sentence)
3. **One-sentence mechanism**: Why does it work
4. **One-sentence scope**: For whom/when does it apply
5. **One-sentence caveat**: Main limitation

Total: <100 words. Perfect is <50 words."

### Completeness Summary Table

| User Type | # of Required Elements | Total Length | Depth | Time to Read |
|-----------|---|---|---|---|
| **Architect** | 7 | 400–600 words | Moderate (mechanism brief) | 5–10 min |
| **Researcher** | 10 | 1000–1500 words | Deep (all epistemology) | 20–30 min |
| **Student** | 10 | 600–900 words | Moderate–Deep (conceptual) | 15–20 min |
| **Reviewer** | 10 | Structured data + metadata | Complete (all studies) | 30+ min (for analysis) |
| **Quick** | 5 | 50–100 words | Minimal (headlines only) | 1–2 min |

---

## Q3: How Do We Avoid Epistemic Compromise?

### The Computational Epistemologist's Opening

**Epistemologist**: "Personalization is an epistemological risk. When we simplify for architects, we might:

1. Imply false precision ('Ceiling height 10.0 feet' vs. 'threshold somewhere around 9.8–10.2 ft')
2. Omit crucial qualifications ('Plants reduce stress' vs. 'Plants reduce stress, probably, with moderate heterogeneity and publication bias')
3. Hide competing mechanisms ('It works because of visual beauty' vs. 'Three mechanisms are proposed; hard to distinguish empirically')
4. Overstate generalizability ('Works in all offices' vs. 'Works in Western offices with natural light')

The guardrails must ensure that **simplification never becomes falsehood**."

### Rule 1: Required Caveats Per Credence Level

**Panel consensus**:
- **Credence ≥ 0.85**: Can state as fact; optional caveat
  - *Example*: "Water is necessary for plant growth."
- **Credence 0.70–0.85**: State finding + brief qualifier
  - *Example*: "We're 75% confident that plants reduce self-reported stress (based on 17 studies; some heterogeneity)."
- **Credence 0.50–0.70**: State finding + reason for uncertainty + scope variance
  - *Example*: "65% confident. Effect stronger in offices (70%) than hospitals (55%). Publication bias likely inflates estimate 10–15%."
- **Credence < 0.50**: Label as speculative; name the competing hypotheses
  - *Example*: "Speculative (40% credence). Mechanism could be visual preference (SRT), attention restoration (ART), or evolutionary signaling. Evidence supports all three."

### Rule 2: Evidence Quality Disclosure (Always)

**EBD researcher**: "Every answer, regardless of depth, must disclose:

- What type of evidence: 'X RCTs, Y observational studies'
- Study quality: 'Publication bias likely', 'Limited to small samples', 'Blinding unclear'
- Effect stability: 'Consistent across populations' vs. 'Heterogeneous (I² = 65%)'
- Methodological concerns: 'Demand characteristics possible in experimental design'

For architects, this can be concise:
- **Short**: 'EBD Level B evidence (5 RCTs, some heterogeneity)'
- **Not short but still OK**: 'Based on 17 studies, mostly observational, with small effect sizes (r = 0.35). Publication bias likely inflates true effect by 10–15%. Evidence weaker for non-Western populations.'"

### Rule 3: No Threshold Inflation

**Expert-novice researcher**: "If researchers report:
> 'Effect size d = 0.48 (95% CI: 0.32–0.64); N = 1,247; range across populations: d = 0.25 (hospitals) to d = 0.68 (offices)'

Then architects should NOT report:
> 'Ceiling height: 10.0 feet (false precision)'

Instead:
> 'Ceiling height: 10+ feet. Evidence threshold is around 9.8 ft; below that, effect weakens but isn't eliminated; above 10 ft, effect plateaus.'"

### Rule 4: Mechanism Honesty (Even in Simplified Answers)

**Cognitive load theorist**: "If the field debates the mechanism, the student MUST know this. If the architect can't know it, then say so transparently:

- **Researcher** (full): 'ART vs SRT debate; predictive processing provides third alternative; all three fit the data'
- **Architect** (simplified but honest): 'Mechanism is still being studied. Plants seem to work via visual or psychological processes (exact pathway unclear). Design implications are the same either way.'
- **Student** (learning): 'The field debates whether plants work because they restore attention (ART), induce positive affect (SRT), or signal status (evolutionary). You should be able to articulate this debate.'
- **Quick** (minimal but honest): 'Why is debated among experts.'"

### Rule 5: Scope Conditions Are Non-Negotiable

**Architectural practice expert**: "EVERY answer must answer: 'For whom does this work? In what contexts? With what side effects?'

- Researcher finds: r = 0.35 overall; r = 0.50 introverts, r = 0.22 extroverts
- This MUST appear in every answer:
  - **Architect**: 'Stronger benefit for introverted workers; placement near focus areas recommended'
  - **Researcher**: Full interaction table
  - **Student**: 'Individual differences: introverts respond more strongly (debate why)'
  - **Reviewer**: Subgroup analysis metadata
  - **Quick**: 'Works especially well for introverted workers'"

### Rule 6: Competing Explanations Are Part of Honesty

**Panel consensus**: If finding X can be explained by theories A, B, and C, then:

- Omitting the alternatives is **not simplification; it's distortion**
- Naming them at appropriate depth is **intellectual honesty**
- Saying 'mechanism unclear' in architecture answer is **correct**
- Omitting competing theories in researcher answer is **malpractice**

Example:
- Finding: People near windows recover faster after surgery (Ulrich 1984)
- Explanation A: Natural views trigger parasympathetic activation (SRT)
- Explanation B: Distraction from pain / attention restoration (ART)
- Explanation C: Confound — window rooms are better rooms (causality unclear)

All answers should acknowledge at least C; A and B should be in researcher/student answers.

### Rule 7: The Caveat Requirement

**Epistemologist** (proposing a formal rule):

> **All personalized answers must include at least one explicit caveat, stated per user type:**
> - **Architect**: 'Main caveat: ...'
> - **Researcher**: 'Limitations: (1) ... (2) ... (3) ...'
> - **Student**: 'Why we're unsure: ...'
> - **Reviewer**: Published in GRADE column or methodological notes
> - **Quick**: 'Main limitation: ...'

**Penalty for violation**: If answer includes no caveat, add one immediately.

---

## Q4: What's the Minimum Viable Personalization?

### The Pragmatist's Challenge

**Science communication specialist**: "We can't personalize everything. That's unmaintainable. What's the **smallest set of distinctions** that gives real differentiation?

Let's say we have N questions and M user types. Currently, we generate N answers (one generic per question). Real personalization would be N × M answers. That's expensive.

What if we identify 3–4 **dimensions of variation** that cover 80% of the difference?"

### Proposed Dimensions

#### Dimension 1: Answer Structure (What Comes First)

| User Type | Lead Element |
|---|---|
| **Architect** | Design parameter or specification |
| **Researcher** | Effect size with CI |
| **Student** | Theory explanation |
| **Reviewer** | Study-level data table |
| **Quick** | Headline (yes/no/maybe) |

**Implementation cost**: Medium. Requires question-type specific handlers (MECHANISM, EVIDENCE_FOR, SCOPE, etc.), but only 4–5 handlers needed to cover 80% of queries.

#### Dimension 2: Evidence Presentation Depth

| User Type | Depth | Metrics Included |
|---|---|---|
| **Architect** | Moderate | EBD level, effect size range, sample size |
| **Researcher** | Deep | d/r with 95% CI, I², p(bias), subgroup effects |
| **Student** | Moderate | Study count, quality, what's contested |
| **Reviewer** | Complete | Full GRADE, all study data, heterogeneity decomposed |
| **Quick** | Minimal | Study count only |

**Implementation cost**: Low. Mostly conditional rendering based on user type; reuse existing effect-size calculations.

#### Dimension 3: Vocabulary Register

| User Type | Style | Example Transform |
|---|---|---|
| **Architect** | Plain + design terms | Attention Restoration Theory → 'your directed attention system recovery' |
| **Researcher** | Technical | Leave as "Attention Restoration Theory (ART; Kaplan & Kaplan 1989)" |
| **Student** | Accessible + conceptual | "Think of it this way: directed attention is like a mental muscle..." |
| **Reviewer** | Standardized (PRISMA) | "RCT, quasi-experimental design, observational cohort" |
| **Quick** | Conversational | "Yeah, pretty solid evidence" |

**Implementation cost**: Medium. Requires vocabulary mapping + templated explanations, but mostly NLP substitution.

#### Dimension 4: Uncertainty Communication

| User Type | How We Say "We're Unsure" |
|---|---|
| **Architect** | "65% confident; stronger in offices (70%), weaker in homes (55%)" |
| **Researcher** | "60–70% credence; publication bias inflates by 10–15%" |
| **Student** | "Well-supported, though contested on mechanisms" |
| **Reviewer** | "GRADE: Moderate certainty of evidence" |
| **Quick** | "Moderate confidence" |

**Implementation cost**: Low. Template-based rendering based on effect_data.credence, publication_bias, heterogeneity, etc.

### The Minimal Viable Set

**Panel consensus**: If we implement these **4 dimensions** well, we get real personalization without massive cost:

1. **Answer structure** (what comes first) — 30% of the difference
2. **Evidence depth** (what details included) — 25% of the difference
3. **Vocabulary register** (what words mean) — 20% of the difference
4. **Uncertainty communication** (how confident) — 15% of the difference
5. **Leftovers** (scope, mechanisms, actionability, learning path) — 10% of the difference

**Implementation estimate**:
- Phase 1 (structures): 2 weeks
- Phase 2 (handlers): 3 weeks
- Phase 3 (depth + vocabulary + uncertainty): 2 weeks
- Phase 4 (integration + testing): 1 week
- **Total: ~8 weeks for 80% of the benefit**

---

## Q5: Generation vs Presentation: Where Should Personalization Happen?

### The False Economy of Reuse

**HCI expert**: "Some systems generate one canonical answer, then personalize only the presentation. This is tempting because:

- Write logic once ✓
- Reuse expensive computations ✓
- Easier to maintain ✓

But it **fails** for these user types:

- **Architect**: Wants a design document, not a literature review reformatted. Needs different content (parameters, trade-offs).
- **Reviewer**: Wants machine-readable data, not prose reformatted into tables.
- **Student**: Wants scaffolding and theory first, not summary→detail. Needs learning narrative.
- **Quick**: Wants a signal, not a summary shortened. Needs just headline + credence.

You can't get there with presentation-only personalization."

### The Case for Generation-Time Personalization

**Cognitive load theorist**: "Personalization must happen at **generation time** because:

1. Different user types ask different questions
   - Architect: 'What parameters?'
   - Researcher: 'What's the heterogeneity?'
   - These lead to different search queries, different template selection

2. Different user types need different information structures
   - Architect: design param → scope → evidence → measurement
   - Researcher: mechanism → effect sizes → heterogeneity → gaps
   - You can't reorder prose; you need different prose

3. Some user types need data the others don't
   - Reviewer: needs all studies, even weak ones
   - Architect: can use curated subset
   - Quick: needs just high-confidence findings

4. Generation cost is already high; presentation cost is cheap
   - If we're already calling LLMs to synthesize, routing to type-specific logic is free
   - Reformatting prose is cheap; generating different prose is already expensive anyway

### Recommendation

**Personalize at generation time. Structure by user type at the handler level.** (This is what the spec proposes.)

---

## Key Takeaways: Panel Summary

1. **Personalization is structural, not cosmetic.** Different user types represent different cognitive modes and information needs, not just different reading levels.

2. **Completeness means different things per type.** Architect wants parameters + trade-offs. Researcher wants heterogeneity + mechanisms. Student wants theory + learning path. Reviewer wants data. Quick wants a signal.

3. **Epistemic integrity is non-negotiable.** Simplification must not create false certainty. All answers must include: what we know, what we don't know, what's contested.

4. **Scope conditions are mandatory.** Every answer must say for whom and when this finding applies.

5. **Minimum viable personalization is 4 dimensions.** Answer structure, evidence depth, vocabulary register, uncertainty communication. These cover 80% of the difference with manageable implementation cost.

6. **Personalize at generation time.** Different user types need different content, not just reformatted presentations.

7. **User profiles should be explicit and testable.** Each profile includes: presupposition frame, question modes, completeness criteria, vocabulary register, actionability level, uncertainty communication strategy.

---

## Questions for Implementation Team

1. **Which question types should we personalize first?** (Recommend: MECHANISM, EVIDENCE_FOR, SCOPE — covers 60% of queries)

2. **How do we maintain consistency across handlers?** (Suggest: shared template library for guardrails, credence calculation, scope extraction)

3. **How do we A/B test personalization?** (Recommend: user satisfaction survey: "How well did this answer match your needs?" Personalized should score 15–25% higher)

4. **How do we evolve user profiles based on feedback?** (Suggest: log rejected/refined answers; analyze patterns; update profiles quarterly)

5. **Should personalization be visible to the user?** (Recommend: yes; show "This answer is customized for [Architect]" with option to switch types)

---

**Document prepared by**: Expert panel deliberation
**Distributed to**: Implementation team, David Kirsh
**Next step**: Specification review → code review of implementation

