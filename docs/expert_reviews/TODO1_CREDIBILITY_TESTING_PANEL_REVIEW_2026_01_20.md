# Expert Panel Review: TODO 1 — Credibility Testing

**Date:** January 20, 2026
**Sprint:** TODO 1, Phase A (Expert Consultation)
**Status:** Panel Deliberation

---

## Panel Composition

- **Dr. Judea Pearl** — Bayesian networks, causal inference
- **Dr. Nancy Cartwright** — Philosophy of science, capacities, external validity
- **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
- **Dr. Marcia Bates** — Information science, knowledge organization
- **Dr. Rachel Kaplan** — Environmental psychology (domain expert)
- **Dr. Deborah Mayo** — Philosophy of statistics, severe testing (invited for this TODO)

---

## Part I: Independent Reflection on the Problem

*Each panelist reflects on the credibility testing problem from their own perspective, before reviewing the proposed approach.*

---

### Dr. Judea Pearl

**On the Nature of the Credibility Testing Problem:**

The question being asked is: "When the system ingests new evidence and updates its beliefs, how do we know the update is correct?" This is fundamentally a question about **faithfulness**—does the computational process faithfully represent the epistemic process it claims to model?

From my perspective, there are two distinct credibility concerns:

**1. Structural Credibility:** When a new paper is processed, the system creates beliefs and constraints. Are these constraints *structurally appropriate*? Does the extracted causal structure match what the paper actually claims? If a paper reports a correlation, is the system correctly refraining from asserting causation? If the paper reports an experimental result with randomization, is the system correctly inferring a causal relationship?

The danger I see is **causal hallucination**—the system inferring causal relationships where only correlational evidence exists, or missing causal implications that experimental designs support.

**2. Parametric Credibility:** Given the structure, are the credence values appropriate? This is less concerning to me than structure. Numbers can be refined; wrong structure propagates errors throughout the network.

My first instinct: Before checking whether credence *magnitudes* are correct, verify that the *direction* and *type* of relationships are correct. A system that assigns 0.6 to a correlation when 0.7 was appropriate is making a small error. A system that treats a correlation as a causal edge is making a categorical error.

**Key question I would ask:** How does the system distinguish experimental evidence (which supports causal claims) from observational evidence (which supports only correlational claims)? This distinction must be preserved through extraction and updating.

---

### Dr. Nancy Cartwright

**On the Nature of the Credibility Testing Problem:**

I want to reframe the question slightly. The system isn't just asking "Is this update correct?" It's asking "Is this update *warranted* given the evidence?"

Warrant is a complex notion. A belief can be updated in ways that are:
- **Locally warranted but globally unwarranted:** The update makes sense given this one paper, but ignores everything else we know
- **Globally warranted but locally puzzling:** The update makes sense given the whole web, but seems to overweight or underweight this particular paper
- **Appropriately scoped vs. overgeneralized:** The update correctly applies to its domain of validity, or incorrectly generalizes beyond it

The most common failure mode I've observed in knowledge systems is **scope creep**—treating findings from a specific context as if they were universal laws. A study of college students in a laboratory becomes "humans respond to X with Y." This is not a computational error; it's an epistemological one.

For credibility testing, I would prioritize checking:
1. **Are scope conditions preserved?** Does the extracted belief carry its boundary conditions, or have they been lost?
2. **Are ceteris paribus clauses acknowledged?** Every scientific finding has implicit "other things being equal" conditions. Are these being tracked?
3. **Is the evidential weight appropriate to the study design?** A small-N qualitative study and a large-N RCT should not update beliefs equally.

**Key question I would ask:** When two papers report findings that *appear* to conflict, how does the system determine whether this is genuine contradiction vs. scope boundary vs. measurement divergence? The credibility of the system depends on getting this classification right.

---

### Dr. Herbert Simon

**On the Nature of the Credibility Testing Problem:**

From a design perspective, I see this as a **quality control problem** for a cognitive system. The system is processing information and making inferences. Quality control asks: Are those inferences within acceptable bounds?

In any quality control system, you face a fundamental tradeoff:
- **Type I errors (false alarms):** Flagging good updates as problematic
- **Type II errors (misses):** Accepting problematic updates

You cannot minimize both simultaneously. The question is: What error rate is acceptable for each type, and how do you calibrate the system to achieve it?

My instinct is that **Type II errors are more costly** in this domain. A false alarm just means a human reviews something unnecessarily—inefficient but not damaging. A miss means a bad belief enters the web and potentially propagates its errors.

Therefore, I would design for **high sensitivity** (catch most real problems) and accept **moderate specificity** (some false alarms). Better to review 20% of articles and catch 95% of problems than to review 5% and catch only 60%.

But here's the bounded rationality question: **What resources are available for human review?** If human review is cheap (a graduate student can check flagged articles), set thresholds low and flag generously. If human review is expensive (requires faculty expertise for each flag), thresholds must be higher.

**Key question I would ask:** What is the actual cost structure? How many articles per week will the system process? How much human time is available for review? The optimal threshold depends entirely on these resource constraints.

---

### Dr. Marcia Bates

**On the Nature of the Credibility Testing Problem:**

I approach this as an **information quality** problem. The system is an information system; credibility testing is about ensuring the quality of information it contains and produces.

In information science, we distinguish several quality dimensions:
- **Accuracy:** Does the information correctly represent its source?
- **Completeness:** Is relevant information missing?
- **Consistency:** Do different parts of the system agree with each other?
- **Currency:** Is the information up to date?
- **Provenance:** Can we trace information back to its source?

For credibility testing, I would focus on **accuracy** and **consistency**:

**Accuracy:** Does the extracted belief accurately represent what the paper said? This is fundamentally a natural language understanding problem. Did the extraction correctly parse the paper's claims? Did it correctly identify the study's conclusions vs. speculations? Did it correctly identify statistical results?

**Consistency:** Do the beliefs extracted from a single paper cohere with each other? If a paper reports multiple findings, they should be internally consistent. If they're not, either the extraction is wrong or the paper is unusual.

I also want to flag **metadata quality**. A credibility check should verify:
- Is the paper ID correctly assigned?
- Are author names and years correct?
- Are statistical values (p, N, effect size) correctly parsed?
- Are scope conditions (population, setting, methodology) correctly extracted?

Metadata errors might seem minor, but they undermine the entire provenance chain. If you can't trust the paper ID, you can't trust anything.

**Key question I would ask:** What is the baseline error rate in extraction? Before designing credibility tests, we should know: what fraction of extractions have errors, and what kinds of errors are most common? This empirical knowledge should drive test design.

---

### Dr. Rachel Kaplan

**On the Nature of the Credibility Testing Problem:**

I bring the domain perspective—environmental psychology and the CNfA literature specifically. Let me reflect on what kinds of credibility failures are most likely and most damaging in this domain.

**Likely failure modes:**

1. **Effect size inflation:** Environmental psychology has a replication crisis. Published effect sizes are often inflated due to publication bias, small samples, and flexible analysis. The system should be skeptical of large effects from small studies.

2. **Mechanism overconfidence:** Papers often *invoke* theories (ART, SRT, Biophilia) without actually *testing* them. A paper might say "consistent with ART" when the study design doesn't actually test ART's mechanism. The system might incorrectly record this as evidence *for* ART.

3. **Context-specific findings generalized:** A finding about Japanese gardens in Kyoto might not apply to urban parks in Detroit. A finding about adults might not apply to children. The system must preserve these boundaries.

4. **Confound blindness:** Many environmental psychology studies have confounds. Natural views might co-occur with socioeconomic status. "Nature" might be confounded with "lack of urban stressors." The system should track these limitations.

**Most damaging failures:**

If the system develops high confidence in a claim that the research community would consider contested or uncertain, that's a serious credibility failure. The system should never be more confident than the expert consensus.

**Key question I would ask:** How does the system's confidence distribution compare to expert opinion? We should validate by asking domain experts: "The system believes X with credence 0.8. Does that match your assessment?" Systematic overconfidence or underconfidence would indicate calibration problems.

---

### Dr. Deborah Mayo

**On the Nature of the Credibility Testing Problem:**

I come at this from the perspective of **severe testing**—the idea that a hypothesis is only well-supported if it has passed tests that probably would have revealed errors if errors existed.

The question "Is this update credible?" can be reframed as: "Has the system's updating procedure been severely tested?"

A severely tested updating procedure would:
1. **Produce correct updates when given correct extractions** (verified against gold standard)
2. **Produce flagged/rejected updates when given erroneous extractions** (verified by injecting known errors)
3. **Produce appropriate confidence levels** (neither systematically overconfident nor underconfident)

The key insight from severe testing: **you must probe for errors, not just check for consistency**. A system that confirms its own outputs is not testing itself severely. You need to actively seek ways the system could fail and verify it doesn't fail in those ways.

Concretely, I would recommend:
1. **Adversarial testing:** Create deliberately problematic inputs (papers with wrong statistics, contradictory claims, scope-inappropriate generalizations) and verify the system flags them
2. **Calibration testing:** For beliefs where we have expert assessments, compare system credences to expert credences
3. **Stability testing:** Process the same paper multiple times (with slight variations in extraction). The results should be stable.

**Key question I would ask:** What specific errors are we probing for? A test that doesn't specify what it's looking for is not a severe test. We need a taxonomy of failure modes, and a test for each.

---

## Part II: Panel Review of Proposed Approach

*The panel has now read the implementation team's proposed approach from `STRATEGIC_TODOS_PROBLEM_ANALYSIS_2026_01_20.md`.*

---

### Panel Discussion

**Dr. Pearl:** I appreciate that the proposal distinguishes extraction credibility from update credibility. This maps to my distinction between structural and parametric credibility. However, I don't see explicit attention to the *causal status* of extracted relationships. The proposal should include a specific check: Is this relationship marked as causal, correlational, or uncertain? And does that marking match the study design?

**Dr. Cartwright:** The proposal mentions "scope overreach" as a failure mode, which I endorse. But the operationalization—checking whether extracted scope matches the paper—assumes extraction got the scope right in the first place. What if the paper itself overgeneralizes? Some papers claim "humans do X" when they studied only WEIRD undergraduates. The credibility test should check for *paper-level* scope inflation, not just extraction-level errors.

**Dr. Simon:** The proposal sensibly discusses false positive vs. true positive rates. But it doesn't quantify the cost structure. I would push for explicit numbers: How many articles per month? What's the human review capacity? What's the cost of a false alarm vs. a miss? Without these, we can't set rational thresholds.

**Dr. Bates:** The proposal mentions checking "semantic similarity" for constraints. This is good, but I want more detail. What embedding model? What similarity threshold? Have we validated that this measure correlates with human judgments of semantic relatedness in this domain? CNfA terminology might not be well-represented in general-purpose embeddings.

**Dr. Kaplan:** I like the domain-specific sanity checks mentioned in the proposal. But I'd add: we should have a list of "known effects" in environmental psychology with expected effect size ranges. If the system extracts an effect size far outside the expected range, that's a red flag. For example, d > 1.5 for any environmental manipulation is highly suspicious.

**Dr. Mayo:** The proposal mentions "baseline calibration" against the Gold Standard corpus. This is good but insufficient. The Gold Standard represents *correct* processing. We also need a "Failure Standard"—deliberately flawed inputs where we know what the system *should* flag. Testing only against correct cases doesn't severely test the detection mechanisms.

---

## Part III: Responses to Specific Questions

*The implementation team posed specific questions. Here are the panel's responses.*

---

### Q1: What counts as "excessive" credence change?

**Dr. Pearl:** There's no universal answer because it depends on the prior uncertainty. A credence moving from 0.5±0.3 to 0.7±0.2 is reasonable. A credence moving from 0.8±0.1 to 0.4±0.1 is suspicious—you're moving 4 standard deviations on low uncertainty. I'd flag changes that exceed 2× the prior uncertainty.

**Dr. Cartwright:** I'd add: it depends on whether the new evidence *should* be powerful. A large meta-analysis should move credences more than a single small study. The flag shouldn't be "large change" but "large change inconsistent with evidence strength."

**Dr. Simon:** Operationally: compute the distribution of credence changes in your Gold Standard corpus. Flag anything beyond the 95th percentile. This is atheoretical but practical.

**Dr. Mayo:** An excessive change is one that would *rarely occur* if the system were working correctly. This is the severe testing perspective—flag things that would be surprising under the "system is correct" hypothesis.

---

### Q2: How do we measure "semantic appropriateness" of constraints without using LLMs?

**Dr. Bates:** Several options, in order of preference:
1. **Taxonomy distance:** If both beliefs reference concepts in your ontology, compute their distance in the taxonomy tree. Beliefs about "nature views" and "stress" are closer than "nature views" and "wayfinding."
2. **Co-citation:** Do the source papers cite each other or common ancestors? This suggests the research community sees them as related.
3. **Embedding similarity:** Use a domain-adapted embedding model. Fine-tune on CNfA literature if possible.
4. **Keyword overlap:** Simple but surprisingly effective. Beliefs that share technical terms are probably related.

**Dr. Pearl:** Add: check for *common causes* in the causal structure. If two beliefs both trace to the same theoretical construct, they should be allowed to connect. If they trace to unrelated constructs, a direct constraint between them is suspicious.

---

### Q3: Should the system ever reject an article outright, or always flag for human review?

**Dr. Simon:** Given bounded resources, you need a two-tier system:
- **Auto-accept:** Passes all checks, within normal parameters
- **Flag for review:** Anomalous on some dimension, but plausibly correct
- **Auto-reject:** So anomalous that no reasonable interpretation could be correct

Auto-rejection should be rare and narrow: duplicate paper IDs, impossible values (negative sample sizes, p > 1), clear parsing failures. Anything that requires interpretation should be flagged, not rejected.

**Dr. Mayo:** I'd be very cautious with auto-rejection. The history of science includes many cases where "impossible" results turned out to be discoveries. Auto-rejection should be reserved for *logical* impossibilities, not *improbable* findings.

**Dr. Kaplan:** In CNfA, I'd auto-reject: papers that aren't actually about environment-human relationships (misclassified papers), papers with clearly fabricated data (if detectable), papers that are duplicates of already-processed work. Beyond that, flag for human review.

---

### Q4: How do we handle the cold-start problem?

**Dr. Simon:** Bootstrap from the Gold Standard corpus. Process those papers first, compute baseline statistics, then use those baselines for new papers. The Gold Standard becomes your reference distribution.

**Dr. Bates:** Also: start with a small manually-verified set and expand incrementally. After processing 10 papers with human oversight, you have a baseline. After 100, it's more robust. The system gets more autonomous as it accumulates calibration data.

**Dr. Cartwright:** Be explicit about uncertainty during cold start. The first few articles should update beliefs *less* because we're uncertain about the baseline. As N grows, updates can be larger because we trust the system more. This is a hierarchical Bayesian approach—uncertain about the parameters of the process itself.

---

## Part IV: Additional Thoughts and Requirements

*Panel members offer additional insights not constrained by the proposal.*

---

### Dr. Pearl — On Causal Sanity Checks

I want to add a requirement not in the original proposal: **causal cycle detection**.

When new constraints are added, check for cycles in the causal structure. If paper A says "X causes Y" and paper B says "Y causes X," this could indicate:
- Bidirectional causation (legitimate)
- Measurement at different timescales
- Error in one paper
- Error in extraction

The system should flag causal cycles for review. They're not always errors, but they're always worth examining.

Also: **instrumental variable consistency**. If a paper uses an instrument to establish causality, verify that the instrument isn't used elsewhere in the web as a direct cause. This would indicate structural inconsistency.

---

### Dr. Cartwright — On Tracking Auxiliary Assumptions

Scientific claims don't stand alone—they depend on auxiliary assumptions. "Plants reduce stress" assumes:
- The stress measure is valid
- The plant manipulation was the only difference between conditions
- The population is representative

The system should track these auxiliary assumptions, at least at a coarse level. When testing credibility, check: are the auxiliary assumptions plausible? Are they consistent across papers that make similar claims?

This is more ambitious than simple credibility checking, but it's what real scientific evaluation requires.

---

### Dr. Simon — On Feedback Loops

The credibility testing system will generate flags. Those flags will go to human reviewers. Those reviewers will make decisions. Those decisions should feed back into the system.

I recommend tracking:
- **Flag resolution rate:** What fraction of flags turn out to be real problems?
- **Flag type distribution:** Which kinds of flags are most often true positives?
- **Reviewer agreement:** Do multiple reviewers agree on flag resolution?

This data lets you refine thresholds over time. If 90% of "excessive credence change" flags turn out to be false alarms, raise that threshold. If 90% of "semantic mismatch" flags are true problems, lower that threshold.

The system should get better at credibility testing as it accumulates feedback data.

---

### Dr. Bates — On Documentation and Explainability

Every flag should come with an explanation. Not just "this article was flagged" but:
- Which specific test(s) failed
- What the expected value was vs. the observed value
- What the human reviewer should check

This serves two purposes:
1. Helps reviewers make good decisions
2. Creates a record for analyzing the credibility system itself

Also: maintain a log of all credibility decisions. This becomes a dataset for improving the system and for understanding the characteristics of the literature.

---

### Dr. Kaplan — On Domain-Specific Calibration

Environmental psychology has certain regularities:
- Effect sizes for environmental manipulations are typically small to medium (d = 0.2 to 0.6)
- Laboratory studies tend to find larger effects than field studies
- Self-report measures tend to show larger effects than physiological measures
- Studies of natural environments tend to find beneficial effects; null results are underreported

The credibility system should encode these regularities. An article reporting d = 1.2 from a field study with physiological measures should be flagged—not because it's necessarily wrong, but because it's unusual enough to warrant review.

I'd also suggest building a list of "landmark papers" that are frequently cited and well-validated. New extractions can be compared against these landmarks. If a new paper contradicts a landmark paper, that's worth flagging.

---

### Dr. Mayo — On Severity Grading

Not all flags are equal. I recommend a **severity grading** system:

**Severity 1 (Critical):** Logical impossibilities, clear errors
- Examples: p < 0, N = -5, self-contradictory claims within paper

**Severity 2 (Major):** Strong anomalies that likely indicate problems
- Examples: Credence change > 3σ, causal claim from correlational study, effect size d > 1.5

**Severity 3 (Minor):** Unusual patterns that might be fine
- Examples: Credence change > 2σ, new constraint with low semantic similarity, effect in unexpected direction

Human review priority should follow severity. Severity 1 flags should be reviewed immediately. Severity 3 flags can be batched and reviewed weekly.

---

## Part V: Synthesis and Recommendations

*Consolidated recommendations from the panel.*

---

### Recommended Credibility Tests (Prioritized)

1. **Logical consistency checks** (Severity 1)
   - Valid ranges for all numeric values
   - No self-contradiction within paper
   - Paper ID uniqueness

2. **Causal status verification** (Severity 2)
   - Experimental design → causal claim permitted
   - Correlational design → correlational claim only
   - Flag mismatches

3. **Credence change magnitude** (Severity 2-3)
   - Flag changes > 2σ given prior uncertainty and evidence strength
   - Threshold adapts to evidence quality

4. **Scope preservation** (Severity 2)
   - Extracted scope must match paper's stated population/setting
   - Flag universal claims from limited samples

5. **Semantic coherence of constraints** (Severity 3)
   - Taxonomy distance, co-citation, or embedding similarity
   - Flag constraints between unrelated concepts

6. **Effect size plausibility** (Severity 3, domain-specific)
   - Expected ranges by study type and measure type
   - Flag outliers for review

7. **Causal structure consistency** (Severity 2)
   - Flag cycles
   - Flag instrument reuse as direct cause

### Recommended Implementation Approach

1. **Start with Gold Standard calibration**
   - Process known-good papers
   - Establish baseline distributions for all metrics

2. **Add adversarial test cases**
   - Create deliberately flawed inputs
   - Verify detection for each failure mode

3. **Implement tiered response**
   - Auto-accept / Flag / Auto-reject
   - Auto-reject only for logical impossibilities

4. **Build feedback loop**
   - Track flag resolution
   - Adjust thresholds based on performance

5. **Document everything**
   - Every flag has an explanation
   - Maintain decision log for meta-analysis

### Recommended Metrics

- True positive rate (sensitivity): Target > 90%
- Flag rate (fraction of articles flagged): Target 10-20%
- False positive rate among flags: Accept up to 30% (better to over-flag)
- Severity 1 detection rate: Target 100%

### Resource Requirements

Before implementation, determine:
- Articles per month (processing load)
- Human review hours per month (capacity)
- Cost of false alarm (reviewer time) vs. miss (bad belief in web)

---

## Next Steps

1. **Implementation team** incorporates panel recommendations into design
2. **Gold Standard corpus** is processed to establish baselines
3. **Adversarial test set** is created with known failure modes
4. **Sprint B** implements Severity 1-2 tests
5. **Sprint C** implements Severity 3 tests and feedback loop
6. **Panel reconvenes** after Sprint C to review results

---

*Panel session concluded: January 20, 2026*
*Document prepared for implementation team*
