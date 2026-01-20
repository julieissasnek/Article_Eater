# Expert Panel Review: TODO 2 — Interpretive Intelligence

**Date:** January 20, 2026
**Sprint:** TODO 2, Phase A (Expert Consultation)
**Status:** Panel Deliberation

---

## Panel Composition

- **Dr. Judea Pearl** — Bayesian networks, causal inference
- **Dr. Nancy Cartwright** — Philosophy of science, explanation, external validity
- **Dr. Herbert Simon** — Bounded rationality, human-computer interaction
- **Dr. Marcia Bates** — Information science, information seeking behavior
- **Dr. Rachel Kaplan** — Environmental psychology (domain expert)
- **Dr. Deirdre Wilson** — Pragmatics, Relevance Theory (invited for this TODO)

---

## Part I: Independent Reflection on the Problem

*Each panelist reflects on the interpretive intelligence problem from their own perspective, before reviewing the proposed approach.*

---

### Dr. Judea Pearl

**On the Nature of the Interpretive Intelligence Problem:**

The system contains a causal-epistemic structure—beliefs connected by constraints that represent support, contradiction, and explanation relationships. The interpretive intelligence problem is: How do we make this structure *legible* to humans who want to understand what the system knows?

From my perspective, the central challenge is **causal explanation**. When a user asks "Why does the system believe plants reduce stress?", they're asking for a causal story. Not just "Papers A, B, and C say so" but "The mechanism is X, which operates through pathway Y, supported by evidence Z."

A good explanation traces causal chains. It identifies:
- **Direct causes:** What immediately produces the effect?
- **Mediators:** What intermediate variables carry the causal influence?
- **Moderators:** What conditions strengthen or weaken the effect?
- **Confounders:** What alternative explanations haven't been ruled out?

The interpretive system should be able to construct these causal narratives from the web's structure. If it can't, the web is storing information it can't explain, which limits its utility.

**Key concern:** Users often confuse correlation with causation. The interpretive system must be careful to distinguish "A is associated with B" from "A causes B." Overstepping this distinction would mislead users.

---

### Dr. Nancy Cartwright

**On the Nature of the Interpretive Intelligence Problem:**

I see this as fundamentally a problem of **communicating warranted assertibility**. The system has beliefs with credences. But what does it mean to tell a user "credence 0.75"? The user needs to understand:

1. **What kind of claim this is:** Theoretical, empirical, observational?
2. **How well-supported it is:** By how much evidence? Of what quality?
3. **What it depends on:** What auxiliary assumptions must hold?
4. **Where it applies:** Under what scope conditions?
5. **What could defeat it:** What would make us revise this belief?

A bare credence number conveys almost none of this. The interpretive system's job is to *unpack* the credence into these richer epistemic dimensions.

I'm particularly concerned about **communicating contingency**. Scientific claims are always contingent—they depend on background conditions, auxiliary hypotheses, and scope limitations. Users often don't appreciate this. They hear "Plants reduce stress" and think it's a universal law.

The interpretive system should proactively surface contingencies. Not just when asked, but as part of every explanation. "Plants reduce stress *in laboratory settings with healthy adults and short exposure durations*. The effect in chronic settings is less certain."

**Key concern:** Over-simplification. The temptation will be to give users clean, simple answers. But reality is messy. The interpretive system must find a way to communicate appropriate complexity without overwhelming users.

---

### Dr. Herbert Simon

**On the Nature of the Interpretive Intelligence Problem:**

This is an **interface design** problem. The system has complex internal structure. Users need to understand and use that structure. The interpretive layer is the interface between system complexity and user cognition.

I approach this through the lens of **bounded rationality**. Users have limited time, attention, and cognitive resources. They can't absorb a complete description of the web's structure. They need *appropriately simplified* representations that support their actual tasks.

What tasks do users have?
1. **Quick lookup:** "Does the system say anything about X?"
2. **Evidence review:** "What supports/contradicts claim Y?"
3. **Confidence assessment:** "How much should I trust Z?"
4. **Gap identification:** "What don't we know about W?"
5. **Decision support:** "Given uncertainty, what should I do?"

Each task requires different information at different granularities. The interpretive system must recognize the task (implicitly or explicitly) and tailor its response.

I would design for **progressive disclosure**: Start with a summary. Let users drill down if they want detail. This respects bounded rationality—users who want depth can get it, but users who want a quick answer aren't overwhelmed.

**Key concern:** The system should never claim more than it knows. If asked about something outside its domain or with high uncertainty, it should say so clearly. False confidence is worse than acknowledged ignorance.

---

### Dr. Marcia Bates

**On the Nature of the Interpretive Intelligence Problem:**

From information science, I see this as **knowledge access** problem. The web contains structured knowledge. The interpretive system must make that knowledge *findable* and *usable*.

There are multiple access modes:
- **Query-driven:** User asks a specific question, system provides answer
- **Browsing:** User explores the structure, system reveals relevant connections
- **Alerting:** System proactively notifies user of relevant information

Most proposals focus only on query-driven access. But research shows that browsing and alerting are equally important for knowledge work. Users don't always know what question to ask. Sometimes they need to explore, and the system should support that.

I would also emphasize **information architecture**. How are explanations organized? What's the hierarchy of concepts? How do users navigate from one piece of knowledge to another? Good information architecture makes the system self-explanatory.

**Key concern:** Vocabulary mismatch. Users may ask questions using different terms than the system uses internally. "Does natural light help focus?" might need to map to "natural_lighting → attention_restoration" even though the words don't match. The interpretive system needs semantic flexibility.

---

### Dr. Rachel Kaplan

**On the Nature of the Interpretive Intelligence Problem:**

As the domain expert, I think about what CNfA practitioners actually need to know and how they'd use this system.

**Typical user questions in CNfA:**
- "I'm designing a hospital waiting room. What environmental features reduce patient anxiety?"
- "A client wants to add plants to their office. What evidence supports this?"
- "We're choosing between large windows and skylights. Which is better for occupant wellbeing?"
- "What don't we know about biophilic design that we should research?"

Notice these are practical questions tied to design decisions. Users don't want epistemology lectures—they want actionable guidance with appropriate caveats.

The interpretive system should:
1. **Translate between academic concepts and design features:** "Natural views" in research becomes "windows overlooking gardens" in design
2. **Acknowledge the lab-to-field gap:** Most evidence is from controlled settings. Real buildings are messier.
3. **Flag contested claims:** Where researchers disagree, say so
4. **Suggest design implications:** Not just "evidence supports X" but "therefore, consider Y"

**Key concern:** The system must be honest about the limitations of the CNfA literature. Much of it is correlational, small-sample, and Western-centric. Users should understand they're working with suggestive evidence, not engineering specifications.

---

### Dr. Deirdre Wilson

**On the Nature of the Interpretive Intelligence Problem:**

From Relevance Theory, I see explanation as a **communication** problem. The system has information. The user wants understanding. Explanation is the process of making information cognitively accessible.

Relevance Theory says: Good communication achieves cognitive effects with minimal processing effort. An explanation is good if:
1. It tells the user something they didn't already know (achieves effect)
2. It does so in a way that's easy to understand (minimizes effort)

This has practical implications:

**Tailor to user knowledge:** An explanation for an expert differs from one for a novice. The system should model what the user already knows and fill in gaps, not repeat what they know.

**Use implicature judiciously:** Natural language conveys meaning through what's said AND what's implied. "The evidence is moderate" implies "don't bet your life on it." The system should be aware of what it's implying, not just what it's stating.

**Order information by relevance:** Present the most relevant information first. For a question about plants and stress, lead with the direct evidence, then supporting context, then caveats. Don't bury the answer.

**Avoid garden paths:** Don't structure explanations in ways that lead users to wrong intermediate conclusions. If the final message is "it's complicated," don't start with confident claims that you'll later qualify.

**Key concern:** Miscommunication. The system might produce text that's technically accurate but pragmatically misleading. Testing should include not just "Is this correct?" but "Did users understand what we meant?"

---

## Part II: Panel Review of Proposed Approach

*The panel has now read the implementation team's proposed approach from `STRATEGIC_TODOS_PROBLEM_ANALYSIS_2026_01_20.md`.*

---

### Panel Discussion

**Dr. Pearl:** The proposed explanation patterns (evidence trace, theory trace, credibility assessment, contingency map) are sensible. But I notice there's no explicit "causal explanation" pattern. When users ask "why," they often want causal mechanisms, not just evidential support. I'd add a "mechanism trace" pattern: What causal pathway connects environment to outcome?

**Dr. Cartwright:** The proposal mentions "contingency mapping" and "fragility analysis," which I strongly endorse. However, I'd distinguish between:
- **Local contingencies:** This specific belief depends on assumptions A, B, C
- **Structural contingencies:** The entire framework depends on assumptions X, Y, Z

Users should be able to ask about both. What does *this belief* depend on? What does *the whole system* depend on?

**Dr. Simon:** The proposal discusses "depth" parameters (summary/standard/deep) and "audience" parameters (researcher/practitioner/student). Good. But how does the system know which to use? I'd recommend:
1. Default to "standard" depth and "practitioner" audience
2. Let users explicitly request other modes
3. Track user behavior to learn preferences over time

**Dr. Bates:** The proposal's template-based approach is pragmatic. But I'm concerned about template rigidity. Real questions don't always fit templates. The system needs graceful fallback when questions don't match. Perhaps: attempt template matching, and if confidence is low, fall back to a generic "here's what I found" response rather than forcing into an ill-fitting template.

**Dr. Kaplan:** I appreciate the example outputs in the proposal. They're readable and informative. I'd add: every explanation should end with a "practical implications" or "so what" section. Researchers might want the epistemology, but practitioners want to know what to do.

**Dr. Wilson:** The proposal mentions "natural language generation" but doesn't specify how. This is crucial. Bad phrasing can undermine even correct content. I'd recommend:
1. Write templates with careful attention to pragmatic implications
2. Have actual CNfA practitioners review the output for clarity
3. Avoid hedge words that create false impressions ("perhaps," "might," "could" everywhere suggests the system knows nothing)

---

## Part III: Responses to Specific Questions

---

### Q1: How do we decide when contingencies are "worth mentioning"?

**Dr. Cartwright:** A contingency is worth mentioning if:
1. **It's plausibly violated:** "This assumes population is healthy adults"—mention if user's context might differ
2. **It's commonly misunderstood:** "This doesn't mean plants cure disease"—mention if users often over-interpret
3. **It's close to being undermined:** "This assumption is contested by recent studies"—mention if fragile

Don't mention contingencies that are universally assumed and uncontested. "This assumes physics works" is not helpful.

**Dr. Wilson:** Apply the relevance criterion: A contingency is worth mentioning if it changes what the user should believe or do. If knowing the contingency wouldn't affect their decisions, omit it.

**Dr. Kaplan:** In CNfA, I'd always mention:
- Lab vs. field distinction
- Duration of exposure (acute vs. chronic)
- Population specificity (WEIRD samples)
- Mechanism uncertainty

These are the contingencies that most often trip up practitioners.

---

### Q2: How do we communicate uncertainty without paralysis?

**Dr. Simon:** Frame uncertainty in terms of decisions. Not "credence is 0.6" but "The evidence supports this, but there's a reasonable chance it doesn't apply to your context. Consider a pilot test before full implementation."

Decision-relevant uncertainty empowers action; abstract uncertainty paralyzes.

**Dr. Pearl:** Distinguish **reducible** from **irreducible** uncertainty. If uncertainty is high because we lack studies, say "We need more research; expect refinement as evidence accumulates." If uncertainty is high because the phenomenon is inherently variable, say "Effects vary by context; expect variation even with more research."

**Dr. Wilson:** Use concrete language. Not "The effect might not generalize" but "The effect was tested in offices; we don't know if it works in hospitals." Specific uncertainty is less paralyzing than vague uncertainty.

---

### Q3: Should explanations differ by user expertise?

**Dr. Simon:** Absolutely. Three levels:

**Novice (student):** Define terms, provide background, emphasize main points, skip caveats that would confuse
**Practitioner:** Assume domain knowledge, emphasize practical implications, include key caveats
**Researcher:** Full detail, complete caveats, statistical nuances, methodological discussions

Default to practitioner. Let users request other levels.

**Dr. Bates:** Also consider: expertise in the *system* vs. expertise in the *domain*. A CNfA expert might be a novice at understanding our web structure. Explanations should accommodate both dimensions.

---

### Q4: How do we explain cross-theory bridges without confusing users?

**Dr. Pearl:** Use causal language. Not "SRT and ART have a functional bridge" but "Both theories predict that nature reduces stress, though they propose different mechanisms. Evidence for one partially supports the other because the predicted effects overlap."

**Dr. Cartwright:** I'd avoid the term "bridge" entirely in user-facing explanations. Instead: "Multiple theories converge on this prediction" or "This finding is consistent with several theoretical frameworks." The concept of bridging theories is valuable internally; users don't need the jargon.

**Dr. Kaplan:** For CNfA practitioners, frame it as: "Researchers have different theories about *why* nature helps, but they agree *that* it helps. The mechanism debate is ongoing, but the practical recommendation stands."

---

## Part IV: Additional Thoughts and Requirements

---

### Dr. Pearl — On Mechanism Explanation

I want to add a requirement: the system should be able to explain **mechanisms**, not just evidence.

When a user asks "Why do plants reduce stress?", answers come at different levels:
1. **Evidential:** "Studies show plants reduce cortisol levels"
2. **Theoretical:** "Stress Recovery Theory predicts biophilic elements trigger restoration"
3. **Mechanistic:** "Natural elements engage soft fascination, allowing directed attention to recover, reducing cognitive load and physiological stress markers"

Level 3 is what users often really want. It explains *how* the effect works, not just *that* it exists.

The system should be able to construct mechanistic explanations by chaining intermediate beliefs. If we have:
- Plants → soft fascination
- Soft fascination → attention recovery
- Attention recovery → reduced cognitive load
- Reduced cognitive load → lower stress markers

Then we can explain: "Plants provide soft fascination, which allows attention to recover, reducing cognitive load and ultimately lowering stress markers."

This requires tracking mechanistic constraints separately from evidential ones. The web already has constraint types; we should use them for explanation construction.

---

### Dr. Cartwright — On Explaining Disagreement

Scientific knowledge includes disagreement. The interpretive system should explain disagreements, not hide them.

When experts disagree, users should understand:
1. **What the disagreement is about:** Mechanism? Effect existence? Generalizability?
2. **Who disagrees:** Is this fringe vs. mainstream, or genuine scientific controversy?
3. **Why they disagree:** Different data? Different interpretations? Different auxiliary assumptions?
4. **What would resolve it:** What evidence would settle the debate?

An interpretive system that only gives the "consensus view" misleads users about the state of knowledge. Real science is messier than textbook summaries.

I'd add a specific capability: "Explain the controversy about X" should produce a balanced summary of competing views with their respective evidence bases.

---

### Dr. Simon — On Interactive Explanation

Explanation shouldn't be one-way. Users should be able to:
1. **Ask follow-up questions:** "You mentioned assumption X. Tell me more."
2. **Challenge claims:** "I don't believe Y. What's your evidence?"
3. **Explore alternatives:** "What if Z weren't true?"

This requires the system to maintain context across interactions. Not just answer one query, but engage in a dialogue about a topic.

For initial implementation, this might be too ambitious. But design with extensibility in mind—don't lock into a pure question-answer pattern.

---

### Dr. Bates — On Visualization

Not everything needs to be text. Some explanations are better as visualizations:
- **Evidence networks:** Show which papers support which beliefs
- **Theory maps:** Show relationships between theoretical constructs
- **Confidence distributions:** Show uncertainty visually, not just as numbers
- **Scope diagrams:** Show what populations/settings a finding applies to

I'd recommend: implement text-based explanation first, but design data structures that support visualization. Add visual explanations later as the system matures.

---

### Dr. Kaplan — On Practical Recommendations

Every explanation should optionally include a "Practical Recommendations" section:

**For the belief "Natural views reduce stress in office settings":**

*Practical Recommendations:*
- *Design consideration:* Provide visual access to natural elements where possible
- *Minimum effective dose:* Even small plants or nature images may help (evidence: moderate)
- *Stronger effects:* Views of trees and water outperform single plants (evidence: preliminary)
- *Caveats for implementation:* Effects demonstrated in controlled settings; real offices have confounds (noise, social factors)

This translation from evidence to action is what practitioners need. Academic explanations are fine for researchers, but most users want guidance.

---

### Dr. Wilson — On Testing Explanations

Explanations should be tested with real users, not just verified for accuracy.

I recommend:
1. **Comprehension testing:** Can users correctly answer questions about what the system explained?
2. **Inference testing:** Do users draw correct conclusions from explanations?
3. **Action testing:** Do users make better decisions after receiving explanations?
4. **Miscommunication testing:** Do any explanations lead to systematically wrong interpretations?

This is empirical linguistics applied to system design. Don't just ask "Is the explanation accurate?" Ask "Did it communicate successfully?"

---

## Part V: Synthesis and Recommendations

---

### Recommended Explanation Patterns (Prioritized)

1. **Evidence Trace** — What papers/studies support this belief?
2. **Credibility Assessment** — How confident should we be, and why?
3. **Mechanism Explanation** — How does this effect work?
4. **Scope Specification** — Where does this apply, and where doesn't it?
5. **Contingency Map** — What assumptions does this rest on?
6. **Disagreement Summary** — Where do experts differ, and why?
7. **Practical Implications** — What does this mean for design decisions?

### Recommended User Modes

| Mode | Depth | Audience | Use Case |
|------|-------|----------|----------|
| Quick | Summary | Practitioner | "Does the system say anything about X?" |
| Standard | Medium | Practitioner | "Tell me about X" (default) |
| Deep | Full | Researcher | "Give me everything about X" |
| Novice | Expanded | Student | "Explain X like I'm new to this" |

### Recommended Implementation Approach

1. **Start with Evidence Trace and Credibility Assessment** — Most common queries

2. **Implement progressive disclosure** — Summary → Detail on demand

3. **Build template library with pragmatic review** — Have practitioners validate that templates communicate clearly

4. **Add Mechanism Explanation in phase 2** — Requires chaining intermediate beliefs

5. **Add Practical Implications section** — High value for practitioners

6. **Design for dialogue** — Even if v1 is single-query, structure supports follow-ups

7. **Test with real users** — Comprehension, inference, and action testing

### Vocabulary Bridge

Maintain a mapping between:
- **Internal terms:** "natural.views", "psych.stress.recovery"
- **Academic terms:** "natural views", "stress recovery"
- **Practitioner terms:** "windows with nature views", "anxiety reduction"
- **Common queries:** "Do plants help?", "Is natural light good?"

The system should accept queries in any vocabulary and respond in the appropriate one for the user mode.

### Avoid These Failure Modes

1. **Jargon overload:** Don't use "epistemic level" or "constraint strength" in user explanations
2. **False precision:** Don't say "credence 0.73" — say "moderate-high confidence"
3. **Hedge paralysis:** Don't qualify every sentence to the point of meaninglessness
4. **Implicature accidents:** Don't inadvertently suggest things you don't mean
5. **Confidence distortion:** Don't present contested claims as consensus

---

## Next Steps

1. **Implement Evidence Trace and Credibility Assessment** (Sprint B)
2. **Build initial template library** (Sprint B)
3. **Test with 5-10 practitioners** for comprehension (Sprint C)
4. **Add Mechanism Explanation and Practical Implications** (Sprint C)
5. **Refine based on user feedback** (Sprint D)
6. **Panel reconvenes** to review user test results (after Sprint D)

---

*Panel session concluded: January 20, 2026*
*Document prepared for implementation team*
