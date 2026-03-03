# Mathematical Explanation Norms

*Created: 2026-03-02*
*Status: ACTIVE — applies to every formula, parameter, and constant in the master document*
*Authority: These norms are derived from the practices of great mathematical communicators and are mandatory for all ATLAS documentation.*

---

## Purpose

The ATLAS master document serves an audience of intelligent non-mathematicians — researchers and professionals who can follow mathematical reasoning but are not trained mathematicians. Every formula must therefore do more than state a relationship: it must make the reader *understand why* that relationship holds, *where it comes from*, and *what it means* when applied to real cases. A formula that is stated but not explained is a formula that cannot be critically evaluated, and a formula that cannot be critically evaluated has no place in an epistemic system built on coherence and transparency.

These norms codify how mathematical content should be presented throughout the master document. They draw on the accumulated wisdom of some of the most effective mathematical communicators of the past half century.

---

## Reference Group

The norms below are synthesized from the pedagogical practices of the following mathematical communicators, each of whom has demonstrated sustained success in making non-trivial mathematics accessible to intellectually engaged non-specialists:

**Steven Strogatz** (Cornell) — *The Joy of x*, *Infinite Powers*, and his New York Times "Elements of Math" series. Strogatz's signature contribution is the *narrative arc*: every formula emerges from a story, a puzzle, or a surprise. He treats the reader as a "nonmathematical friend" — someone who has never seen the result but is fully capable of understanding it when the path is lit properly (Strogatz, 2012, 2019). His principle: intuition and visualization first, then formalism, then the "aha" that connects them.

**Keith Devlin** (Stanford) — *The Math Gene*, *Mathematics: The New Golden Age*, and the popular "Math Guy" segments on NPR. Devlin distinguishes sharply between *understanding* and *procedure*: knowing how to perform a calculation is not the same as grasping what the calculation means. His central pedagogical commitment is that concrete instances must precede abstract generalizations — the reader should see the idea working in a specific case before encountering it in general form (Devlin, 2000, 2008).

**Jordan Ellenberg** (Wisconsin) — *How Not to Be Wrong: The Power of Mathematical Thinking*. Ellenberg's distinctive contribution is his framing of mathematics as "an atomic-powered prosthesis that you attach to your common sense, vastly multiplying its reach and strength." He shows that mathematical reasoning is not alien to everyday thinking but rather a disciplined extension of it. His technique: translate technical content into the vocabulary of intelligent amateurs, eliminating jargon without sacrificing precision (Ellenberg, 2014).

**Ian Stewart** (Warwick) — *Does God Play Dice?*, *Nature's Numbers*, and over 20 popular mathematics books. Stewart's guiding principle is that the reader has "zero knowledge but infinite intelligence" — a commitment to never condescending while always building from accessible foundations. He employs multiple entry points (historical narrative, physical intuition, visual demonstration) for the same concept, because different readers grasp different hooks (Stewart, 1995, 2011). His observation that "writing for a different audience makes you rethink everything" captures the epistemic virtue of clear explanation: if you cannot explain it plainly, you may not understand it as well as you think.

**Barry Mazur** (Harvard) — *Imagining Numbers* and his essays on mathematical narrative. Mazur's distinctive emphasis is on *imagination* over memorization. He traces the historical path by which concepts that once seemed impossible (imaginary numbers, infinite series, non-Euclidean geometry) became thinkable — and in doing so, he gives the reader permission to find the ideas strange at first. His technique: show the concept being born, with all the confusion and resistance of its original discoverers, so the reader understands that difficulty is part of the process, not a sign of failure (Mazur, 2003).

**Marcus du Sautoy** (Oxford, Simonyi Professor for the Public Understanding of Science) — *The Music of the Primes*, *Symmetry*. Du Sautoy's signature approach is *humanizing mathematics*: every theorem has a discoverer, every formula was born in a particular moment of intellectual struggle, and the story of that struggle makes the mathematics more memorable and more comprehensible. He combines biographical narrative with mathematical exposition so that the human and the formal illuminate each other (du Sautoy, 2003, 2008).

**John Tsitsiklis** (MIT) — *A Few Tips on Writing Papers with Mathematical Content*. Tsitsiklis provides the complementary perspective from technical writing rather than popularization: use minimal notation, maintain forward linear structure, provide signposts at the start of every section so the reader never loses orientation, and break content into chunks of manageable size (Tsitsiklis, 2019).

**Dimitri Bertsekas** (MIT) — *Ten Simple Rules for Mathematical Writing*. Bertsekas emphasizes notation consistency, the importance of treating formulas as sentences (with subjects, verbs, and objects), and the principle that every definition should be immediately followed by an example (Bertsekas, 2002).

---

## The Seven Norms

### Norm 1: The Four-Layer Explanation (MANDATORY for every formula)

Every formula in the master document must be accompanied by four layers of explanation, presented in this order:

**Layer 1 — Plain-English Statement.** State what the formula says in one or two sentences that contain no mathematical notation whatsoever. This sentence should be comprehensible to anyone familiar with the domain (architecture, environmental psychology, cognitive science) even if they have never seen a formula.

*Example*: "This formula says: the more reliable the study design and the closer the study population matches your building's users, the more you should trust that lab findings will hold in a real building."

**Layer 2 — Intuition and Motivation.** Explain *why* this particular mathematical form makes sense. What is the conceptual argument? Why multiplication and not addition? Why logarithms and not raw probabilities? The reader should be able to reconstruct the formula's general shape from the intuition alone, even if they could not derive the precise form.

*Example*: "We use the logit transform because probabilities near 0 and 1 are 'sticky' — a 0.95 probability is much harder to move to 0.99 than a 0.50 probability is to move to 0.54. The logit stretches the scale so that equal changes in the multiplicative factors produce equal changes in evidential impact, regardless of where you start on the probability scale."

**Layer 3 — Formal Statement with Defined Terms.** Present the formula with every variable, parameter, and constant explicitly defined. Each definition should include the variable's type (real number, integer, probability, etc.), its range, its units (if any), and a one-sentence description of what it represents.

**Layer 4 — Worked Examples Spanning the Diversity of Cases.** Provide at least two worked examples that illustrate how the formula behaves across meaningfully different inputs. The examples should span the range of typical use cases, showing the formula in action for both favorable and unfavorable scenarios. When a formula has boundary conditions or edge cases, at least one example should approach a boundary.

*Rationale*: This four-layer structure follows Strogatz's "narrative arc" (plain statement → intuition → formalism → application), Devlin's "concrete before formal" principle, and David's directive that "showing examples that span the diversity of cases" is essential.

**Success condition**: A reader who skips Layer 3 (the formal statement) and reads only Layers 1, 2, and 4 should still understand what the formula does, why it exists, and approximately what values it produces.

---

### Norm 2: Provenance and Intellectual History (MANDATORY for every formula)

Every formula must declare its intellectual origins. The reader should know: Did this formula come from an established literature? Was it adapted from a known framework? Was it proposed fresh for this system? And if so, on what basis?

**Three provenance categories:**

**ESTABLISHED** — The formula appears in the published literature essentially as stated. Cite the originating source and any major variants.

*Template*: "This formula follows [Author (Year)], who showed that [brief description]. Our notation adapts theirs by [specific changes]."

**ADAPTED** — The formula modifies an established result to fit the ATLAS context. Cite the original, explain what was changed and why, and justify each modification.

*Template*: "This adapts [Author (Year)]'s [formula name], originally developed for [original domain]. We modify it by [specific change] because [justification]. The original formula assumed [assumption]; in the ATLAS context, [that assumption does/does not hold] because [reason]."

**NOVEL** — The formula was developed specifically for this system. State the design principles that guided its construction, the alternatives that were considered, and why this particular form was chosen.

*Template*: "This formula is new to ATLAS, designed to capture [relationship]. The key design choices are: [Choice 1] because [reason], [Choice 2] because [reason]. Alternatives considered: [Alternative A], rejected because [reason]; [Alternative B], rejected because [reason]."

*Rationale*: Mazur's principle that showing how concepts are born — with all the intellectual struggle of their original developers — makes the mathematics both more comprehensible and more honestly situated. Du Sautoy's biographical approach: every formula has a discoverer, a moment, and a context.

---

### Norm 3: Every Constant Must Be Justified (MANDATORY)

No "magic numbers." Every numerical constant, threshold, weight, default value, floor, ceiling, or parameter in the master document must have an explicit justification. The justification must fall into one of four categories:

**EMPIRICAL** — The value is derived from data. Cite the data source, the method of derivation, and the uncertainty range.

*Template*: "d(MECHANISM) = 0.80, derived from [data source]: of [N] mechanism-type claims in [corpus], [X%] were successfully replicated (95% CI: [lower, upper]). See [citation]."

**THEORETICAL** — The value follows from a formal argument. State the premises and the derivation.

*Template*: "The floor ω = 0.05 implements [Principle Name]: even the weakest evidence contributes non-zero information because [argument]. Formally, if [premise], then [derivation], yielding ω ≥ 0.05."

**CALIBRATED** — The value was set by expert judgment, panel consensus, or iterative adjustment against known cases. Identify the decision-makers, the method, and any recorded disagreement.

*Template*: "TEA weights (0.30, 0.25, 0.15, 0.20, 0.10) were established by [Panel Name] on [Date] using [method — e.g., analytic hierarchy process, Delphi method, direct elicitation]. See Decision D-X.Y. Panelist [Name] dissented on [specific weight], arguing for [alternative] because [reason]."

**STIPULATED** — The value is a design choice with no strong empirical or theoretical basis. This is acceptable but must be accompanied by a sensitivity analysis.

*Template*: "δ_default = 0.90 is stipulated as a reasonable starting point. Sensitivity: if δ varies ± 0.10, predictions shift by [± X%]. See sensitivity table below."

**Success condition**: A skeptical reader can look at any number in the document and immediately determine (a) what kind of justification it has, (b) where that justification can be found, and (c) how much the system's outputs would change if the value were different.

*Rationale*: Ellenberg's principle that mathematics extends common sense — if a number is asserted without reason, common sense is precisely what should rebel. Tsitsiklis's emphasis on making every claim auditable.

---

### Norm 4: State Assumptions and Scope Explicitly (MANDATORY)

Every formula operates within a domain of valid application. The reader must know where the formula works, where it breaks down, and what happens at the boundaries.

**Required elements:**

1. **Assumptions** — What must be true for the formula to be valid? List every assumption, including ones that seem obvious. (What seems obvious to the author is often opaque to the reader.)

2. **Domain of validity** — For what ranges of input values does the formula produce meaningful results? What happens outside those ranges?

3. **Failure modes** — Under what conditions does the formula give misleading results? When should the reader *not* use it?

4. **Relationship to alternatives** — If other formulas could do the same job, why was this one chosen? What does it capture that the alternatives miss?

*Example*:
> "The projection formula assumes that (a) evidence from the source study is transferable in principle to the target population, (b) the four factors d, ω, δ operate multiplicatively rather than additively, and (c) the logit transform is an appropriate scale for evidence combination. Assumption (b) is the strongest: it implies that study design quality and population match contribute independently to transfer reliability. If these factors interact — for example, if population mismatch is worse for poorly designed studies — the formula will overestimate confidence in transferred evidence. This interaction has not been tested empirically and represents a known limitation."

*Rationale*: Stewart's principle of "zero knowledge, infinite intelligence" — the reader is smart enough to evaluate the formula critically, but only if the assumptions are laid bare. Devlin's insistence on understanding over procedure: knowing the limits of a formula is part of understanding it.

---

### Norm 5: Use Common-Sense Labels, Then Technical Terms (MANDATORY)

All mathematical notation must be accompanied by plain-English names. The plain-English name comes first; the technical symbol appears in parentheses afterward.

**The rule**: If a formula contains a symbol, the reader must encounter a plain-English name for that symbol within the same paragraph or within the preceding paragraph. Technical abbreviations (EN, BN, VOI, CCI, TEA, AESHI) must be introduced with their full common-sense meaning on each first use within a section.

**Good**: "How confident should we be in a real building, given what a lab study found? The answer depends on four factors: study design reliability (*d*), evidence quality (*ω*), population match (*δ*), and what the lab actually found (*p_lab*)."

**Bad**: "logit(p_target) = d(τ) · ω · δ · logit(p_lab), where d, ω, δ are defined in §48.1–48.3."

**For compound expressions**: Break them down term by term, explaining what each piece contributes to the whole. Treat the formula as a sentence — identify the subject, verb, and object.

*Example*: "The formula multiplies four things together. Think of it as a chain of filters: *d* asks 'How good was the study design?' (best designs let 95% of the evidence through; worst let only 25% through). Then *ω* asks 'How strong is this particular piece of evidence?' And *δ* asks 'How similar is the study population to the people who will actually use the building?' Each filter lets some fraction of the original lab result through. What comes out the other end is your best estimate for the real building."

*Rationale*: Ellenberg's "atomic-powered prosthesis" metaphor — mathematics amplifies common sense, so the common-sense meaning must be visible at all times. The Common-Sense Labeling Rule already established in CLAUDE.md.

---

### Norm 6: Figures for Every Non-Trivial Formula (STRONGLY RECOMMENDED)

Every formula that involves more than two variables should have an accompanying figure showing how the output changes as inputs vary. The figure should:

1. **Show the shape** — Is the relationship linear, exponential, logarithmic, U-shaped, threshold? The reader should see the function's character at a glance.

2. **Mark the typical operating range** — Where do most real inputs fall? Shade or highlight this region.

3. **Show sensitivity** — If one parameter changes while others are held constant, how much does the output move? Overlay curves for different parameter values.

4. **Label in plain English** — Following Norm 5, axes and legends use common-sense terms with technical notation in parentheses.

5. **State the finding in the title** — Following the ATLAS visualization norms (Tufte data-ink ratio, in-figure finding statements), the figure title should say what the reader should learn from the figure, not merely name the topic.

*Example figure title*: "Study Design Quality (d) Has the Largest Effect on Transferred Confidence — Moving from 'Theory-Only' to 'Randomized Trial' Nearly Quadruples the Evidence That Survives Transfer"

*Rationale*: Strogatz's emphasis on visualization as a primary mode of mathematical understanding, not merely an illustration. Stewart's use of multiple entry points — for many readers, the figure *is* the explanation, and the formula is a compact summary of what the figure shows.

---

### Norm 7: Span the Diversity of Cases in Examples (MANDATORY)

When providing worked examples for a formula, the examples must span the range of situations the reader is likely to encounter. Specifically:

**Required diversity dimensions:**

1. **Best case / worst case** — Show the formula when everything goes right (high-quality study, perfect population match) and when everything goes poorly (weak study, distant population). The reader needs to see the full range.

2. **Typical case** — Show a realistic, middle-of-the-road scenario that represents everyday use.

3. **Edge case** — Show what happens near the boundaries: when a parameter approaches its floor or ceiling, when inputs are extreme, when the formula produces a surprising result.

4. **Cross-domain** — If the formula applies across domains (visual, acoustic, thermal, etc.), show at least one example from each of two different domains, so the reader sees that the formula's structure transcends any single application area.

**Format for each example:**

```
EXAMPLE [N]: [Brief scenario description]
  Context: [Why this case is interesting or typical]
  Inputs: [Each variable = value, with brief justification for each]
  Computation: [Step-by-step, showing intermediate values]
  Result: [Final answer]
  Interpretation: [What this means in practical terms — what should a designer do?]
```

*Rationale*: David's explicit directive: "showing examples that span the diversity of cases is good idea." Devlin's principle that understanding is demonstrated by application across varied contexts. Ellenberg's technique of translating abstract relationships into specific, tangible scenarios.

---

## Applying the Norms: A Checklist

For every formula in the master document, verify:

| # | Check | Norm | Status |
|---|-------|------|--------|
| 1 | Has a plain-English statement (no notation)? | Norm 1, Layer 1 | |
| 2 | Has an intuitive explanation of *why* this form? | Norm 1, Layer 2 | |
| 3 | Has a formal statement with all terms defined? | Norm 1, Layer 3 | |
| 4 | Has ≥ 2 worked examples spanning diverse cases? | Norms 1 & 7 | |
| 5 | States provenance (ESTABLISHED / ADAPTED / NOVEL)? | Norm 2 | |
| 6 | Every constant is justified (EMPIRICAL / THEORETICAL / CALIBRATED / STIPULATED)? | Norm 3 | |
| 7 | Assumptions listed explicitly? | Norm 4 | |
| 8 | Domain of validity and failure modes stated? | Norm 4 | |
| 9 | All labels use common-sense terms first, then technical? | Norm 5 | |
| 10 | Has an accompanying figure (if > 2 variables)? | Norm 6 | |
| 11 | Examples span best/worst/typical/edge cases? | Norm 7 | |

**Minimum passing score**: Items 1–6 and 9 are MANDATORY (must all pass). Items 7, 8, 10, 11 are STRONGLY RECOMMENDED (at least 3 of 4 should pass for any formula with more than two variables).

---

## Application to Current ATLAS Gaps

The math audit (2026-03-02) identified the following formulas needing remediation under these norms:

### Critical (Missing Formulas)

| Formula | Current Status | Norms Violated | Remediation |
|---------|---------------|----------------|-------------|
| Coherence (C*) | Not formalized | All 7 norms | Write from scratch per Norm 1–7 |
| VOI (Value of Information) | Conceptual only | Norms 1 (Layers 2–4), 2, 3, 6, 7 | Formalize and add all layers |

### High Priority (Formulas Exist but Lack Explanation)

| Formula | Current Status | Norms Violated | Remediation |
|---------|---------------|----------------|-------------|
| d values (transfer reliability) | Constants stated, no justification | Norm 3 | Add CALIBRATED or STIPULATED justification + sensitivity |
| Projection formula | Good, but intuition layer thin | Norm 1 (Layer 2), Norm 7 | Expand intuition; add cross-domain examples |
| AESHI | Formula stated, weights unjustified | Norms 3, 4, 7 | Justify weights; add sensitivity analysis |
| TEA | Formula stated, weights unjustified | Norms 3, 7 | Justify weights; show what changes if weights shift |

### Medium Priority (~20 Constants)

| Constant | Location | Norm 3 Category Needed |
|----------|----------|----------------------|
| δ default = 0.90 | §48.3A | CALIBRATED or STIPULATED |
| δ minimum = 0.30 | §48.3A | THEORETICAL |
| ω floor = 0.05 | §48.3B | THEORETICAL |
| ω ceiling = 0.98 | §48.3B | THEORETICAL |
| Convergence ε (unspecified) | PART_XVII | STIPULATED |
| λ (coherence weighting) | PART_IX | Depends on C* formalization |
| ... (~14 more) | Various | Various |

---

## Integration with Other Contracts

- **FIGURE_CONSISTENCY_CONTRACT.md**: Norm 6 (figures for formulas) generates new figures that must be registered in FIGURE_DEPENDENCIES.json and tracked for staleness.
- **VISUALIZATION_NORMS.md**: Norm 6 figures follow the ATLAS visual palette and design standards.
- **Common-Sense Labeling Rule (CLAUDE.md)**: Norm 5 extends and formalizes this rule for mathematical content specifically.
- **Decision Tracking Protocol (CLAUDE.md)**: Norm 2 (provenance) and Norm 3 (constant justification) create entries in the decision log when new formulas or constants are introduced.

---

## References

Bertsekas, D. P. (2002). *Ten simple rules for mathematical writing*. MIT. Available at: https://www.robots.ox.ac.uk/~phst/Style/Ten_Rules.pdf

Devlin, K. (2000). *The math gene: How mathematical thinking evolved and why numbers are like gossip*. Basic Books.

Devlin, K. (2008). *The unfinished game: Pascal, Fermat, and the seventeenth-century letter that made the modern world*. Basic Books.

du Sautoy, M. (2003). *The music of the primes: Why an unsolved problem in mathematics matters*. Fourth Estate/HarperCollins.

du Sautoy, M. (2008). *Symmetry: A journey into the patterns of nature*. HarperCollins.

Ellenberg, J. (2014). *How not to be wrong: The power of mathematical thinking*. Penguin Press.

Mazur, B. (2003). *Imagining numbers (particularly the square root of minus fifteen)*. Farrar, Straus and Giroux.

Stewart, I. (1995). *Nature's numbers: The unreal reality of mathematics*. Basic Books.

Stewart, I. (2011). *The mathematics of life*. Basic Books.

Strogatz, S. (2012). *The joy of x: A guided tour of math, from one to infinity*. Houghton Mifflin Harcourt.

Strogatz, S. (2019). *Infinite powers: How calculus reveals the secrets of the universe*. Houghton Mifflin Harcourt.

Tsitsiklis, J. N. (2019). *A few tips on writing papers with mathematical content*. MIT. Available at: https://www.mit.edu/~jnt/Papers/R-20-write-v5.pdf

---

## Revision History

| Date | Change | Reason |
|------|--------|--------|
| 2026-03-02 | Created | David requested norms derived from great math popularizers; math audit revealed 3 critical gaps + ~20 unjustified constants |
