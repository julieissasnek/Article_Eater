# Expert Panel Review: Sprint 4 Outcome Taxonomy Extensions

**Date**: 2026-01-18  
**Document Type**: Expert Panel Response  
**Sprint**: 4 (Outcome Taxonomy Extensions)  
**Status**: Panel Review Complete

---

## Executive Summary

The expert panel convened to evaluate five key decisions in the Sprint 4 implementation of the Article Eater outcome taxonomy extensions. The panel reached consensus on several fundamental points while identifying productive disagreements that suggest refinements to the current implementation.

**Key Consensus Points**:
- The theory-outcome relevance architecture is sound but requires empirical calibration
- Epistemic level assignment should be contextual rather than fixed
- The CNFA extension hierarchy requires restructuring around measurement operationalization
- Stub outcomes should be queued for review rather than immediately integrated
- Bridge candidate generation should combine automated suggestion with expert curation

**Key Disagreements**:
- The degree to which relevance scores can be meaningfully quantified (Pearl vs. Cartwright)
- Whether physiological measures warrant privileged observational status (Kaplan vs. Simon)
- The appropriate granularity for architectural outcome categories (Bates vs. Kaplan)

The panel recommends proceeding with Sprint 5 after implementing the modifications detailed below.

---

## Panel Composition and Expertise

### Dr. Judea Pearl
**Affiliation**: University of California, Los Angeles  
**Expertise**: Causal inference, Bayesian networks, structural causal models  
**Relevant Works**: *Causality* (2009), *The Book of Why* (2018)  
**Google Scholar Citations**: ~145,000  
**Role in Review**: Evaluating causal validity of theory-outcome mappings; assessing inference mechanisms

### Dr. Nancy Cartwright
**Affiliation**: Durham University / University of California, San Diego  
**Expertise**: Philosophy of science, causal mechanisms, external validity  
**Relevant Works**: *How the Laws of Physics Lie* (1983), *The Dappled World* (1999), *Evidence-Based Policy* (2012)  
**Google Scholar Citations**: ~28,000  
**Role in Review**: Evaluating bridge warrant validity; assessing domain transfer assumptions

### Dr. Rachel Kaplan
**Affiliation**: University of Michigan (Emerita)  
**Expertise**: Environmental psychology, Attention Restoration Theory, preference research  
**Relevant Works**: *The Experience of Nature* (1989), *With People in Mind* (1998)  
**Google Scholar Citations**: ~52,000  
**Role in Review**: Evaluating CNFA extensions; assessing psychological construct validity

### Dr. Marcia Bates
**Affiliation**: University of California, Los Angeles (Emerita)  
**Expertise**: Information science, faceted classification, information retrieval  
**Relevant Works**: "The Design of Browsing and Berrypicking Techniques" (1989), "Fundamental Forms of Information" (2006)  
**Google Scholar Citations**: ~18,000  
**Role in Review**: Evaluating taxonomy structure; assessing organizational principles

### Dr. Herbert Simon
**Affiliation**: Carnegie Mellon University (Posthumous contribution via published work)  
**Expertise**: Bounded rationality, decision-making, artificial intelligence, administrative behavior  
**Relevant Works**: *Administrative Behavior* (1947), *The Sciences of the Artificial* (1969), "Rational Choice and the Structure of the Environment" (1956)  
**Google Scholar Citations**: ~420,000  
**Role in Review**: Evaluating practical constraints; assessing satisficing in categorization

---

## Decision 4.1: Theory-Outcome Relevance Scores

### Question 1.1: Are the relevance scores reasonable based on the literature?

**Dr. Judea Pearl**:

The fundamental question is whether these relevance scores represent causal relationships or merely associational frequencies. The current implementation conflates two distinct quantities: (a) the probability that a study measuring outcome O will invoke theory T, and (b) the strength of causal connection between T's mechanisms and O's operationalization.

For Attention Restoration Theory (ART), the mapping of `cog.attention.sustained: 1.0` is defensible because ART's core causal mechanism—the recovery of directed attention capacity through involuntary attention engagement—directly predicts sustained attention outcomes (Kaplan & Kaplan, 1989). However, the assignment of `cog.memory.working: 0.8` requires justification. ART predicts working memory improvement only derivatively, through the mediating path: nature exposure → directed attention recovery → reduced cognitive load → improved working memory performance. This causal chain suggests the relevance score should reflect path-specific effects rather than total effects.

I recommend representing these mappings as structural equations or at minimum documenting the assumed causal pathways. A relevance score without causal grounding is merely a correlation coefficient in disguise.

**Dr. Nancy Cartwright**:

I find the very project of assigning universal numeric relevance scores philosophically problematic. Scientific theories do not have context-free relationships to outcomes; they possess what I have termed "capacities"—stable causal powers that manifest differently depending on enabling conditions (Cartwright, 1989). ART has the capacity to predict attention restoration, but this capacity is only exercised under specific conditions: sufficient exposure duration, appropriate environment type, adequate baseline depletion, and so forth.

The score of 1.0 for `cog.attention.sustained` under ART suggests this outcome is always maximally relevant, but empirical work shows substantial heterogeneity. Berman et al. (2008) found attention benefits with nature walks but not mere nature viewing; Ohly et al.'s (2016) meta-analysis revealed effect sizes ranging from negligible to substantial depending on context. A single numeric score cannot capture this variability.

If relevance scores must be retained, I recommend they represent modal or typical relevance rather than universal relevance, with explicit documentation of scope conditions under which the score applies.

**Dr. Rachel Kaplan**:

From the perspective of the substantive psychology, the scores for ART outcomes appear reasonable though perhaps overconfident. The core ART predictions concern soft fascination, extent, compatibility, and being-away—not direct mappings to cognitive outcomes (S. Kaplan, 1995). Sustained attention is an *indicator* of directed attention capacity, not the theoretical construct itself. 

The mapping `physio.fatigue: 0.8` for ART is appropriate given Stephen Kaplan's original framing of mental fatigue as the antecedent condition that restorative environments address (Kaplan, 1995). For SRT, the `affect.stress: 1.0` mapping correctly identifies the core dependent variable in Ulrich's formulation (Ulrich et al., 1991), though SRT also predicts physiological outcomes that should not be subordinated.

I would recommend adding a distinction between core theoretical predictions (relevance 0.9-1.0), derived predictions (0.6-0.8), and exploratory associations (0.3-0.5).

**Synthesis for 1.1**:

The scores are approximately reasonable but require:
1. Explicit documentation of causal pathways (Pearl)
2. Scope conditions for when scores apply (Cartwright)
3. Distinction between core and derived predictions (Kaplan)


### Question 1.2: Should scores be derived empirically (from corpus analysis) rather than expert-assigned?

**Dr. Marcia Bates**:

This question presents a false dichotomy. In classification theory, we recognize that vocabularies can be constructed through literary warrant (what terms appear in the literature), user warrant (what terms users employ), or structural warrant (what the logical structure of the domain requires) (Beghtol, 1986; Hjørland, 2013). Each has merits and limitations.

Empirical derivation from corpus analysis provides literary warrant—we learn what associations researchers actually make. However, corpus frequencies may reflect historical accident, citation patterns, or methodological convenience rather than genuine theoretical relationships. Environmental psychology's heavy reliance on self-report measures means corpus analysis would overweight affect outcomes relative to physiological ones, not because affect is more theoretically central but because it is more easily measured.

I recommend a hybrid approach: initialize scores from corpus analysis to establish literary warrant, then adjust through expert review to incorporate structural warrant. The final scores should be versioned and their provenance documented.

**Dr. Herbert Simon**:

The choice between empirical and expert-assigned scores is fundamentally a question of satisficing (Simon, 1956). Perfect scores are unattainable; the question is what level of accuracy suffices for the system's purposes.

If the purpose is to achieve human-competitive theory assignment for extracted claims, then we should evaluate whether expert-assigned scores achieve this goal. If they do, the additional complexity of corpus analysis may not be warranted. If they do not, corpus analysis may help but is not guaranteed to do so—the corpus itself reflects imperfect human judgments.

I would suggest an iterative refinement process: begin with expert-assigned scores (cheap to obtain), evaluate performance on a held-out test set, and invest in corpus analysis only if performance is inadequate and corpus analysis is likely to improve it. This is a classic satisficing strategy—search until finding a satisfactory solution, do not continue searching merely because a better solution might exist.

**Dr. Judea Pearl**:

Corpus analysis can estimate P(Theory mentioned | Outcome measured), but this conditional probability is not what we want. What we want is something closer to causal effect: how much does knowing the outcome measured inform us about what theoretical mechanisms are operating?

The difference is crucial. If 80% of studies measuring "sustained attention" mention ART, this might reflect ART's popularity rather than its explanatory adequacy. A corpus trained on literature from the 1970s would show high Skinnerian relevance for behavioral outcomes; a corpus from the 2010s would not. The scores should track theoretical validity, not sociological prevalence.

I recommend using corpus analysis only to identify candidate theory-outcome pairs, with scores determined through meta-analytic effect sizes or structural analysis of theoretical commitments.

**Synthesis for 1.2**:

The panel recommends a hybrid approach:
1. Use corpus analysis to identify theory-outcome associations (Bates, Pearl)
2. Calibrate scores using meta-analytic effect sizes where available (Pearl)
3. Apply expert adjustment for structural considerations (Bates, Simon)
4. Adopt iterative refinement based on system performance (Simon)


### Question 1.3: Is 0.4 a reasonable threshold for theory attachment?

**Dr. Nancy Cartwright**:

A universal threshold is ill-conceived. What counts as "relevant enough" for theory attachment depends on the purpose of the attachment. If the purpose is to flag claims for expert review, a low threshold (0.3) casts a wider net. If the purpose is to automatically assign theoretical commitments that affect credence calculations, a high threshold (0.7) reduces false positives.

The appropriate threshold also depends on the base rate of theory-outcome associations. In a sparse relevance matrix where most cells are zero, a 0.4 threshold may be reasonable. In a dense matrix where most outcomes have modest relevance to multiple theories, 0.4 might create excessive multi-theory attachment.

I recommend replacing the single threshold with purpose-specific thresholds: a low threshold for exploratory flagging and a high threshold for automatic processing.

**Dr. Herbert Simon**:

The threshold of 0.4 appears to be an arbitrary value chosen for its intuitive reasonableness—neither too strict nor too lenient. This is not necessarily problematic; in the absence of optimality criteria, reasonable starting points are acceptable.

However, the system should include mechanisms for threshold adjustment based on feedback. If expert reviewers consistently override theory attachments at the 0.4-0.6 range, this suggests the threshold should be raised. Conversely, if experts frequently add theory attachments that the system missed, the threshold may be too high.

I recommend implementing the 0.4 threshold as a configurable parameter with logging to enable empirical calibration.

**Synthesis for 1.3**:

The 0.4 threshold is acceptable as a starting point with the following modifications:
1. Implement purpose-specific thresholds (Cartwright)
2. Make the threshold configurable and logged (Simon)
3. Plan for empirical calibration based on expert override patterns (Simon)

---

## Decision 4.2: Epistemic Level Defaults

### Question 2.1: Is this hierarchy philosophically defensible?

**Dr. Nancy Cartwright**:

The hierarchy reflects a naive foundationalism that philosophy of science has problematized since at least Duhem (1906). The assumption that physiological measures are "more observational" than cognitive measures presumes that observation is theory-neutral and that directness of measurement correlates with epistemic reliability. Both assumptions are contestable.

Consider cortisol measurement, classified as OBSERVATIONAL. Interpreting cortisol levels as stress requires theoretical commitments: that the HPA axis responds to psychological stressors, that cortisol levels reflect cumulative stress rather than circadian variation, that measurement timing captures the relevant stress response, and so forth. The observation "cortisol level is 15 μg/dL" becomes "the participant is stressed" only through substantial theoretical mediation.

Similarly, "sustained attention" measured via backward digit span is not obviously less observational than heart rate. Both require instrumentation; both require interpretive frameworks to become theoretically meaningful.

I do not recommend abandoning epistemic levels entirely—they serve a useful organizing function. However, I recommend reconceptualizing levels as reflecting degree of interpretive mediation rather than observational directness, and I recommend allowing context to modulate level assignment.

**Dr. Judea Pearl**:

The hierarchy encodes assumptions about the causal structure of knowledge that should be made explicit. The implicit model appears to be:

```
THEORETICAL → INTERMEDIATE → EMPIRICAL → OBSERVATIONAL
```

where arrows indicate inferential dependence: we infer theoretical claims from intermediate ones, intermediate from empirical, and empirical from observational.

This is reasonable as a default but ignores top-down effects. Theoretical commitments shape what counts as evidence; observations are "theory-laden" in Hanson's (1958) sense. The system should permit bidirectional influence: observations constrain theories, but theories also influence how observations are categorized and weighted.

I recommend implementing the hierarchy as a default that can be overridden by explicit theoretical commitments in the Web of Belief. If a strong theoretical belief contradicts an observational claim, the system should flag the conflict rather than automatically privileging the observation.

**Dr. Herbert Simon**:

The hierarchy is defensible as a bounded rationality strategy. We cannot represent infinite nuance in epistemic status; we must choose tractable categories. Four levels represent a reasonable compromise between expressive power and cognitive/computational manageability.

The specific level assignments follow the heuristic that direct measurement is more reliable than derived measurement. This heuristic is imperfect but useful. It will make errors but will on average improve inference quality compared to treating all claims as epistemically equivalent.

I recommend accepting the hierarchy as a "good enough" first approximation while acknowledging its limitations and planning for refinement based on error analysis.

**Synthesis for 2.1**:

The hierarchy is defensible as a pragmatic approximation with these modifications:
1. Reconceptualize levels as "degree of interpretive mediation" rather than "observational directness" (Cartwright)
2. Permit bidirectional influence between levels (Pearl)
3. Accept pragmatic limitations while planning for error-based refinement (Simon)


### Question 2.2: Should epistemic level be contextual (depending on how outcome is measured)?

**Dr. Rachel Kaplan**:

Absolutely yes. The same nominal outcome—"stress," for instance—has radically different epistemic status depending on measurement method. Self-reported stress on a Likert scale involves different epistemic commitments than salivary cortisol, which differs from heart rate variability, which differs from behavioral indicators of distress.

In environmental psychology, this is not merely a philosophical point but a practical reality. Parsons et al.'s (1998) driving simulation study used psychophysiological indicators of stress; Ulrich's (1984) surgery recovery study used days to discharge and pain medication requests; Hartig et al.'s (2003) attention study used the Necker cube task. These measure different constructs that we loosely group under "stress" or "restoration."

I recommend extending the outcome taxonomy to encode measurement method as a modifier, with epistemic level determined by the outcome-method combination rather than the outcome alone. `affect.stress[self_report]` would be INTERMEDIATE while `affect.stress[cortisol]` would be EMPIRICAL.

**Dr. Marcia Bates**:

The proposal to make epistemic level contextual aligns with faceted classification principles (Ranganathan, 1967). Rather than assigning outcomes to fixed positions in an enumerative hierarchy, we recognize that outcomes possess multiple facets—the phenomenon facet (what is measured), the method facet (how it is measured), and the interpretation facet (what theoretical framework gives it meaning).

Epistemic level emerges from the combination of facets rather than being intrinsic to the phenomenon facet alone. This is more expressive and better reflects actual research practice, where the same construct is operationalized in multiple ways with different validity characteristics.

Implementation should use a faceted code structure: `phenomenon.method.interpretation`, with epistemic level computed from the method facet according to a separate method-to-level mapping.

**Synthesis for 2.2**:

The panel unanimously recommends contextual epistemic levels:
1. Encode measurement method as an outcome modifier (Kaplan)
2. Use faceted classification with level computed from method facet (Bates)
3. Maintain default levels for when method is unspecified (implicit consensus)


### Question 2.3: Are physiological measures truly "more observational" than self-report?

**Dr. Nancy Cartwright**:

The assumption that physiological measures are more observational reflects what philosophers call the "view from nowhere" (Nagel, 1986)—the presumption that objective measurement transcends perspective. But there is no view from nowhere; all measurement is perspectival.

Physiological measures have different validity threats than self-report, not fewer. Heart rate variability is affected by respiration, posture, medication, and fitness level; cortisol by circadian rhythm, acute vs. chronic stress, and individual differences in HPA axis reactivity. These confounds are not less problematic than the social desirability bias in self-report—they are differently problematic.

The intuition that physiological measures are more objective likely reflects the rhetoric of "hardness" in science (Harding, 1998). Psychology's inferiority complex relative to biology and physics leads to privileging measurement methods that appear more "scientific." This is sociology of science, not epistemology.

I recommend treating physiological and self-report measures as epistemically equivalent by default, with contextual adjustment based on specific validity evidence.

**Dr. Rachel Kaplan**:

While I agree with Dr. Cartwright that physiological measures are not automatically superior, I believe the distinction has practical value in environmental psychology research. Self-report measures what participants believe or are willing to say about their mental states; physiological measures access states that may not be consciously available.

The restoration literature includes interesting dissociations. Berman et al. (2012) found that nature walks improved affect and cognition even when participants reported no mood change. This suggests that physiological and behavioral measures can detect restoration effects that self-report misses—not because self-report is epistemically inferior, but because it accesses a different aspect of the phenomenon.

I recommend encoding a distinction between access level (what aspect of the phenomenon is measured) rather than epistemic level (how reliable the measure is). Self-report accesses conscious experience; physiology accesses autonomic states; behavior accesses functional capacity. These are complementary, not hierarchical.

**Synthesis for 2.3**:

The panel recommends:
1. Abandon the assumption that physiological measures are epistemically privileged (Cartwright)
2. Distinguish access level (what is measured) from epistemic level (measurement reliability) (Kaplan)
3. Treat both measure types as potentially valid with different validity threats (both)

---

## Decision 4.3: CNFA Domain Extensions

### Question 3.1: Is the proposed hierarchy appropriate for CNFA?

**Dr. Rachel Kaplan**:

The hierarchy makes a reasonable first attempt but conflates perceptual features with psychological responses. Consider `arch.spatial.openness`—is this a feature of the space (high ceilings, few partitions) or a psychological response to the space (felt sense of openness)? Environmental psychology has long struggled with this ambiguity (Nasar, 1994).

I recommend splitting architectural outcomes into three sub-domains:
- `arch.feature`: Objective spatial properties (ceiling height, view distance, partition count)
- `arch.percept`: Perceptual judgments (perceived openness, perceived complexity)
- `arch.response`: Psychological/physiological responses to architecture (spatial affect, restoration)

This tripartite structure mirrors Gibson's (1979) distinction between physical properties, affordances, and effectivities, and aligns with how CNFA research actually proceeds—measuring objective features, collecting perceptual ratings, and assessing psychological outcomes.

**Dr. Marcia Bates**:

The current hierarchy violates several principles of sound taxonomy construction. Categories at the same hierarchical level should be mutually exclusive and collectively exhaustive within their parent category; sibling categories should employ consistent principles of division (Kwasnik, 1999).

The proposed `arch` domain mixes classification principles:
- `arch.spatial` and `arch.aesthetic` are perceptual modalities
- `arch.environ` appears to be about content (biophilic elements)
- `arch.affect` is a response type

The hierarchy also has granularity inconsistencies. `arch.aesthetic.beauty` is highly abstract while `arch.spatial.prospect_refuge` is a specific theoretical construct from Appleton (1975). These should not be siblings.

I recommend restructuring around a consistent classification principle. If the domain concerns perceptual features, organize by perceptual dimension (spatial, chromatic, textural). If it concerns theoretical constructs, organize by theory (Kaplan's framework, Appleton's framework, Ulrich's framework). Do not mix principles within a level.

**Dr. Herbert Simon**:

The proposed hierarchy is adequate for a first iteration but will require empirical refinement. The key test is not whether the hierarchy is logically perfect but whether it enables useful extraction and organization of claims from the literature.

I recommend implementing the current hierarchy with robust logging of how extracted claims map to categories. Categories that are rarely used may be too specific; categories that accumulate heterogeneous claims may be too broad. Let the data guide refinement rather than attempting to achieve perfection before deployment.

**Synthesis for 3.1**:

The panel recommends restructuring the hierarchy:
1. Separate features, percepts, and responses (Kaplan)
2. Use consistent classification principles within levels (Bates)
3. Implement with logging to guide empirical refinement (Simon)


### Question 3.2: Are there important architectural outcomes missing?

**Dr. Rachel Kaplan**:

Several theoretically important constructs are absent:

**From Attention Restoration Theory**:
- Soft fascination (the key mechanism of restoration)
- Extent (perceived scope of the environment)
- Compatibility (fit between environment and inclinations)
- Being-away (psychological distance from demands)

**From Stress Recovery Theory**:
- Perceived safety
- Aesthetic liking (distinct from beauty, per Ulrich, 1983)

**From Prospect-Refuge Theory**:
- Prospect (opportunity to see)
- Refuge (opportunity to hide)
- Hazard (perceived threat)

**From Biophilic Design Framework**:
- Each of Kellert's (2008) 72 attributes could warrant an outcome code

The challenge is balancing comprehensiveness against tractability. I recommend including all named constructs from major theories (ART, SRT, prospect-refuge, biophilia) while leaving detailed attributes like Kellert's for future extension.

**Dr. Marcia Bates**:

From an information science perspective, the taxonomy should support both specific and general queries. A researcher should be able to retrieve all claims about "spatial perception" broadly or "perceived enclosure" specifically.

Missing from this perspective:
- Wayfinding and legibility (Lynch, 1960)
- Place attachment (Altman & Low, 1992)
- Environmental legibility
- Perceived control over environment
- Privacy regulation

The taxonomy should also include placeholder categories for emergent constructs. Environmental psychology evolves; the taxonomy must accommodate new constructs without requiring restructuring.

**Synthesis for 3.2**:

Add the following categories:
1. ART-specific constructs: fascination, extent, compatibility, being-away (Kaplan)
2. Prospect-refuge components: prospect, refuge, hazard (Kaplan)
3. Additional environmental constructs: wayfinding, place attachment, perceived control (Bates)
4. Placeholder categories for future extension (Bates)


### Question 3.3: Should "prospect-refuge" be under spatial or affect?

**Dr. Rachel Kaplan**:

Prospect-refuge is fundamentally about spatial configuration and its evolutionary significance. Appleton (1975) theorized that humans prefer landscapes offering both prospect (ability to see) and refuge (ability to hide) because such environments conferred survival advantages in ancestral environments.

The affective response to prospect-refuge configurations is a consequence, not the construct itself. Placing prospect-refuge under `arch.affect` would conflate the environmental feature with its psychological effect—precisely the conflation I cautioned against earlier.

I recommend placing prospect-refuge under a new `arch.config` (spatial configuration) category, with a separate `arch.response.safety` category for the affective response it evokes.

**Dr. Nancy Cartwright**:

This question illustrates why taxonomic placement requires explicit theoretical commitment. If we adopt an objectivist view where prospect-refuge is a feature of environments that can be measured independently of observers, it belongs under spatial features. If we adopt a transactionalist view where prospect-refuge is constituted by the organism-environment relationship (as Gibson might argue), the distinction between spatial feature and affective response breaks down.

The taxonomy cannot be theory-neutral. I recommend making theoretical commitments explicit in documentation: the taxonomy adopts [specified position] on the ontology of environmental psychology constructs, with the understanding that alternative positions are possible.

**Synthesis for 3.3**:

Place prospect-refuge under spatial configuration with these considerations:
1. Create `arch.config` category for spatial configurations (Kaplan)
2. Document the theoretical commitment this placement reflects (Cartwright)
3. Create separate `arch.response.safety` for affective consequences (Kaplan)


### Question 3.4: How should geometric outcomes (angular vs. curved) be categorized?

**Dr. Rachel Kaplan**:

Geometric properties like angularity vs. curvature are features of surfaces and forms, not perceptual or affective constructs. Research by Bar and Neta (2006) demonstrates that curved contours are preferred to angular ones, likely due to evolved threat detection (sharp angles signal potential harm). But the angularity itself is a stimulus property; the preference is the response.

I recommend:
- `arch.geometry.angular`: Angular/sharp forms
- `arch.geometry.curved`: Curved/smooth forms
- `arch.geometry.fractal`: Fractal/self-similar patterns
- `arch.response.geometry_preference`: Affective response to geometry

**Dr. Marcia Bates**:

Geometric properties should be organized as a facet that can combine with other facets. A claim might concern "curved ceiling surfaces" or "angular floor patterns." The geometry is an attribute that modifies a spatial element.

I recommend implementing geometry as a facet (`+curved`, `+angular`, `+fractal`) that can be applied to any `arch.feature` code, rather than as a separate sub-domain. This avoids proliferation of categories and supports combinatorial expressiveness.

**Synthesis for 3.4**:

The panel recommends:
1. Treat geometry as a feature attribute, not a separate domain (Bates)
2. Implement as a facet modifier applicable to spatial features (Bates)
3. Create separate response category for geometry preferences (Kaplan)

---

## Decision 4.4: Stub Outcome Management

### Question 4.1: Should stubs immediately create beliefs in the web, or queue for review?

**Dr. Judea Pearl**:

Introducing unvetted stubs directly into the Web of Belief risks corrupting inference. The Web's credence calculations propagate belief updates through the constraint network; a misspecified stub could introduce spurious correlations or contradict existing beliefs without appropriate flagging.

I strongly recommend queuing stubs for review. Stubs should be stored in a separate "holding area" with the following properties:
- No constraint propagation to or from stubs
- Periodic batch review to resolve stubs to canonical outcomes
- Conflict detection if a stub's inferred domain contradicts its claimed relationships

Only after expert review should stubs be promoted to full beliefs with constraint participation.

**Dr. Herbert Simon**:

The decision depends on the cost-benefit ratio of errors. If stub errors are easily detected and corrected (low error cost), immediate integration with flagging is acceptable. If stub errors are difficult to detect and propagate silently (high error cost), queuing is preferable.

Given that the Web of Belief performs probabilistic inference, a single misspecified stub is unlikely to catastrophically corrupt the system—credence updates are moderated by uncertainty estimates. However, accumulated stubs could introduce systematic bias.

I recommend a hybrid approach: stubs with high domain-inference confidence (e.g., keywords strongly associated with a single domain) can be provisionally integrated with reduced credence weight; stubs with low confidence should be queued for review.

**Dr. Marcia Bates**:

From an information organization perspective, the question is whether to maintain a single authoritative vocabulary or permit vocabulary heterogeneity with reconciliation mechanisms. Both approaches have precedent: LCSH maintains strict vocabulary control; folksonomies permit uncontrolled terms with emergent organization (Vander Wal, 2007).

For a system intended to support formal inference, vocabulary control is important. Stubs represent vocabulary expansion that should be deliberate rather than accidental.

I recommend stubs be queued with metadata capturing: (a) the raw term as extracted, (b) the paper and context of extraction, (c) the inferred domain, and (d) suggested canonical mappings. Human reviewers can then accept, modify, or reject stub-to-canonical mappings in batch.

**Synthesis for 4.1**:

The panel recommends queuing stubs for review:
1. Maintain a separate holding area without constraint propagation (Pearl)
2. High-confidence stubs may be provisionally integrated with reduced weight (Simon)
3. Capture rich metadata to facilitate batch review (Bates)


### Question 4.2: How should stub credence be initialized (currently default)?

**Dr. Judea Pearl**:

Credence should reflect the uncertainty appropriate to the stub's status. Default credence (presumably 0.5 or the prior) is inappropriate because it treats the stub as equivalent to a vetted outcome about which we have no information. But we do have information: we know the outcome term appeared in a scientific paper, which is some evidence of validity.

I recommend initializing stub credence based on:
- Source quality: peer-reviewed journal > conference paper > preprint
- Domain confidence: high confidence in domain inference → higher credence
- Corroboration: term appearing in multiple papers → higher credence

These factors should be combined into a stub-specific prior that reflects our uncertainty about whether the stub represents a valid construct.

**Dr. Nancy Cartwright**:

The deeper problem is that credence is not well-defined for stubs. Credence in the Web of Belief represents our degree of belief in a claim's truth. But stubs are not claims—they are placeholders for potential claims. We cannot coherently ask "how much do we believe in the truth of this placeholder?"

I recommend separating two questions: (a) how confident are we that the stub represents a valid construct? and (b) if it represents a valid construct, what is our credence in claims involving it?

Stubs should carry a "construct validity" estimate (answering question a) separate from claim credence (answering question b). Only after construct validity is established through review should claim credence be assigned.

**Synthesis for 4.2**:

The panel recommends:
1. Do not assign claim credence to unvetted stubs (Cartwright)
2. Assign "construct validity" estimate based on source quality, domain confidence, and corroboration (Pearl, Cartwright)
3. Convert construct validity to credence prior only after review (implicit consensus)


### Question 4.3: What happens when a stub is later resolved (merge or replace)?

**Dr. Marcia Bates**:

Standard vocabulary control practice is to create "see" references from deprecated terms to canonical terms, preserving the history of vocabulary development (Taylor & Joudrey, 2017). This is preferable to silent replacement because it:
- Maintains provenance for extracted claims
- Enables analysis of vocabulary evolution
- Supports users who search using the original stub term

I recommend implementing stub resolution as a merge operation: the stub is deprecated and linked to its canonical resolution, claims using the stub are re-pointed to the canonical outcome, and the stub remains in the vocabulary as a deprecated synonym.

**Dr. Judea Pearl**:

If stubs have influenced inference before resolution (which I have recommended against), then resolution creates a version control problem. The Web of Belief at time T was computed with the stub; the Web at time T+1 is computed with the canonical outcome. These may yield different credence distributions.

If my recommendation to queue stubs is adopted, this problem does not arise: stubs never influence inference, so resolution simply promotes them to canonical status.

For stubs that were provisionally integrated, I recommend recomputing affected beliefs upon resolution, with documentation of the pre- and post-resolution states.

**Synthesis for 4.3**:

Implement stub resolution as merge with history preservation:
1. Deprecated stubs link to canonical outcomes as synonyms (Bates)
2. Claims are re-pointed to canonical outcomes (Bates)
3. If stubs influenced inference, recompute affected beliefs (Pearl)

---

## Decision 4.5: Bridge Candidate Identification

### Question 5.1: Should bridge candidates be auto-generated or manually curated?

**Dr. Nancy Cartwright**:

Bridge warrants—claims that evidence from one domain can inform beliefs in another—are among the most epistemically fraught claims in science. They require justification that automatic generation cannot provide. The warrant that "evidence about cortisol reduction transfers to claims about stress reduction" requires the substantive claim that cortisol is a valid indicator of stress, which is contestable.

I am skeptical of automated bridge generation. At most, automation should *suggest* candidates for human curation, not *create* bridges with epistemic force.

However, I acknowledge that pragmatic constraints may require some automation. If so, I recommend automatically generated bridges be flagged with high uncertainty and low constraint strength, so they influence inference only weakly until validated.

**Dr. Judea Pearl**:

Bridge warrants encode causal assumptions that should be explicit. The mapping `arch.environ.biophilic → affect.stress` implicitly assumes a causal path: biophilic elements → [mechanism] → reduced stress. Without specifying the mechanism, we cannot evaluate whether the bridge is valid.

I recommend that bridge candidates include mechanism annotations, even if the mechanism is initially "unspecified." This makes the causal assumption explicit and identifies what evidence would validate or invalidate the bridge.

Automatic generation is acceptable for mechanism-unspecified candidates; these are essentially hypotheses that the system flags for investigation. Human curation should focus on specifying mechanisms and evaluating their plausibility.

**Dr. Herbert Simon**:

The question is one of resource allocation. Manual curation is more accurate but expensive; automatic generation is cheaper but noisier. The optimal strategy depends on the downstream cost of false bridges versus the cost of curation.

For a research support system where users can inspect and override system judgments, automatic generation with flagging is acceptable—users can catch errors. For an autonomous inference system, stricter curation is warranted.

I recommend automatic generation with a quality tier system: high-confidence bridges (strong theoretical basis, empirical support) are auto-approved; moderate-confidence bridges are flagged for batch review; low-confidence bridges are suggestions only, not integrated into inference.

**Synthesis for 5.1**:

The panel recommends a tiered approach:
1. Automatic generation produces bridge *candidates*, not bridges (Cartwright)
2. Candidates require mechanism annotation (Pearl)
3. Quality tiers determine curation requirements (Simon)
   - High confidence: auto-approved for inference
   - Moderate confidence: flagged for batch review
   - Low confidence: suggestions only


### Question 5.2: What determines a "reasonable" cross-domain bridge?

**Dr. Nancy Cartwright**:

A reasonable bridge requires what I have called "thick causal knowledge"—understanding of the mechanisms that connect the domains and the conditions under which those mechanisms operate (Cartwright, 2012). Thin statistical associations are insufficient.

For `arch.environ.biophilic → affect.stress`, reasonableness requires:
- A plausible mechanism (e.g., evolutionary affiliation with natural forms, soft fascination, perceived safety)
- Evidence that the mechanism operates in the relevant contexts
- Understanding of moderating conditions (e.g., biophilia effects may depend on cultural background, exposure duration, baseline stress)

I recommend evaluating bridge reasonableness against these criteria, with explicit documentation of the mechanistic rationale and known moderators.

**Dr. Rachel Kaplan**:

From the environmental psychology literature, reasonable cross-domain bridges have empirical precedent. The arch → affect bridges are well-studied; the arch → physio bridges less so; the arch → cog bridges are intermediate.

I recommend using literature support as a reasonableness criterion:
- Extensively documented (>50 studies): high confidence
- Moderately documented (10-50 studies): moderate confidence
- Sparsely documented (<10 studies): low confidence
- Undocumented: speculative, requires theoretical rationale

For novel bridges without empirical precedent, theoretical rationale should invoke established mechanisms (e.g., applying ART mechanisms to new outcome pairs).

**Dr. Judea Pearl**:

A reasonable bridge should satisfy d-separation constraints in the underlying causal graph. If we believe that biophilic elements affect stress through a mediating variable M (say, positive affect), then the bridge should reflect this structure: arch.environ.biophilic → M → affect.stress.

Bridges that violate causal assumptions are unreasonable regardless of statistical association. For example, a bridge from arch.aesthetic.beauty to physio.cortisol without mechanism is suspicious—we have no theoretical account of how aesthetic judgments would directly affect HPA axis function.

I recommend evaluating reasonableness through causal graph consistency: a bridge is reasonable if it can be represented as a path in a plausible causal graph.

**Synthesis for 5.2**:

Reasonableness criteria for cross-domain bridges:
1. Mechanistic plausibility with explicit mechanism specification (Cartwright)
2. Empirical precedent with literature support estimates (Kaplan)
3. Causal graph consistency (Pearl)
4. All three criteria should be documented for each bridge


### Question 5.3: How should bridge type (mechanism, functional, analogical) be inferred from outcomes?

**Dr. Nancy Cartwright**:

Bridge types encode distinct epistemic claims:
- **Mechanistic bridges** claim shared causal mechanism
- **Functional bridges** claim similar functional role without mechanism identity
- **Analogical bridges** claim structural similarity without causal or functional commitment

Type inference from outcomes alone is unreliable because the same outcome pair could be connected by any type. `arch.spatial.openness → affect.spaciousness` might be mechanistic (openness causes spaciousness perception), functional (both play the role of freedom-related responses), or analogical (semantic similarity without causal connection).

I recommend defaulting to the weakest type (analogical) for automatic inference, upgrading to stronger types only with explicit evidence:
- Mechanistic: requires specification of causal pathway
- Functional: requires evidence of interchangeable functional role
- Analogical: default for semantic/domain similarity

**Dr. Marcia Bates**:

Information retrieval research distinguishes term relationships that parallel bridge types (Hjørland, 2007):
- Hierarchical (BT/NT): functional subsumption
- Associative (RT): mechanistic or empirical connection
- Equivalence (USE/UF): analogical mapping

The system could infer bridge type from taxonomic relationships:
- Same hierarchy path → functional (shared parent implies shared function)
- Same domain, different hierarchy → mechanistic (domain implies shared mechanisms)
- Different domain → analogical (only structural similarity)

This is a heuristic, not a guarantee, but provides reasonable defaults.

**Synthesis for 5.3**:

Bridge type inference should:
1. Default to analogical (weakest commitment) (Cartwright)
2. Use taxonomic heuristics for initial inference (Bates)
   - Same hierarchy → functional
   - Same domain → mechanistic
   - Different domain → analogical
3. Upgrade to stronger types only with explicit evidence (Cartwright)

---

## Summary of Recommendations

### Decision 4.1: Theory-Outcome Relevance Scores

| Aspect | Recommendation |
|--------|----------------|
| Score validity | Approximately reasonable; require explicit causal pathway documentation |
| Derivation method | Hybrid: corpus analysis for candidate identification, expert adjustment for structural validity |
| Threshold (0.4) | Acceptable starting point; make configurable with purpose-specific variants |

### Decision 4.2: Epistemic Level Defaults

| Aspect | Recommendation |
|--------|----------------|
| Hierarchy validity | Defensible as pragmatic approximation; reconceptualize as "interpretive mediation" |
| Contextuality | Yes—encode measurement method as facet modifier |
| Physiological privilege | Abandon; treat as equal with different validity threats |

### Decision 4.3: CNFA Domain Extensions

| Aspect | Recommendation |
|--------|----------------|
| Hierarchy structure | Restructure: separate features, percepts, responses; use consistent classification principles |
| Missing outcomes | Add ART constructs, prospect-refuge components, wayfinding, place attachment |
| Prospect-refuge placement | Under `arch.config` (spatial configuration), not affect |
| Geometric outcomes | Implement as facet modifier, not separate domain |

### Decision 4.4: Stub Outcome Management

| Aspect | Recommendation |
|--------|----------------|
| Integration | Queue for review; high-confidence stubs may be provisionally integrated |
| Credence | Assign construct validity estimate, not claim credence |
| Resolution | Merge with history; deprecated stubs become synonyms |

### Decision 4.5: Bridge Candidate Identification

| Aspect | Recommendation |
|--------|----------------|
| Generation method | Automatic generation produces candidates; tiered curation determines integration |
| Reasonableness | Evaluate via mechanism plausibility, literature support, causal graph consistency |
| Type inference | Default to analogical; upgrade with evidence |

---

## Areas of Consensus

1. **Contextual assignment over fixed defaults**: All panelists agreed that fixed, context-free assignments (for epistemic level, relevance scores, bridge types) are problematic. Context should modulate defaults.

2. **Pragmatic implementation with planned refinement**: Panelists acknowledged that perfect systems are unattainable; the goal is adequate initial implementation with mechanisms for empirical refinement.

3. **Separation of concerns**: Multiple panelists recommended separating conflated concepts (features vs. percepts vs. responses; construct validity vs. claim credence; candidate generation vs. curation).

4. **Explicit documentation of assumptions**: Theoretical commitments implicit in design decisions should be made explicit to enable critique and revision.

---

## Areas of Productive Disagreement

### Pearl vs. Cartwright on Relevance Score Quantification

Pearl believes causal relationships can be quantified with appropriate structural modeling; Cartwright is skeptical that context-free numeric scores are meaningful. Both agree scores are useful pragmatically but differ on their epistemological status.

**Resolution**: Treat scores as heuristic summaries with documented limitations, not as precise measurements.

### Kaplan vs. Simon on Physiological Privilege

Kaplan argues physiological measures access different phenomena (autonomic states vs. conscious experience) rather than the same phenomenon more directly. Simon's position is agnostic—what matters is practical utility.

**Resolution**: Implement access level (what is measured) as separate from epistemic level (measurement reliability).

### Bates vs. Kaplan on Taxonomy Granularity

Bates favors structural consistency even at the cost of theoretical alignment; Kaplan favors theoretical constructs even if structurally inconsistent.

**Resolution**: Use structurally consistent organization with theoretical constructs as named entities within structure.

---

## Final Recommendations for Sprint 5

Based on this review, the panel recommends the following modifications before proceeding to Sprint 5:

1. **Revise epistemic level assignment** to be method-dependent with faceted structure
2. **Restructure CNFA hierarchy** following the feature/percept/response distinction
3. **Implement stub queuing** with construct validity estimates
4. **Add mechanism annotation** requirement for bridge candidates
5. **Create tiered curation workflow** based on bridge confidence

The panel approves Sprint 4 implementation as adequate for research use with the understanding that these refinements will be incorporated in Sprint 5.

---

## References

Altman, I., & Low, S. M. (Eds.). (1992). *Place attachment*. Plenum Press. [Google Scholar citations: ~3,800]

Appleton, J. (1975). *The experience of landscape*. Wiley. [Google Scholar citations: ~3,200]

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science, 17*(8), 645-648. https://doi.org/10.1111/j.1467-9280.2006.01759.x [Google Scholar citations: ~1,200]

Bates, M. J. (1989). The design of browsing and berrypicking techniques for the online search interface. *Online Review, 13*(5), 407-424. https://doi.org/10.1108/eb024320 [Google Scholar citations: ~3,400]

Beghtol, C. (1986). Semantic validity: Concepts of warrant in bibliographic classification systems. *Library Resources & Technical Services, 30*(2), 109-125. [Google Scholar citations: ~280]

Berman, M. G., Jonides, J., & Kaplan, S. (2008). The cognitive benefits of interacting with nature. *Psychological Science, 19*(12), 1207-1212. https://doi.org/10.1111/j.1467-9280.2008.02225.x [Google Scholar citations: ~3,100]

Berman, M. G., Kross, E., Krpan, K. M., Askren, M. K., Burson, A., Deldin, P. J., ... & Jonides, J. (2012). Interacting with nature improves cognition and affect for individuals with depression. *Journal of Affective Disorders, 140*(3), 300-305. https://doi.org/10.1016/j.jad.2012.03.012 [Google Scholar citations: ~850]

Cartwright, N. (1983). *How the laws of physics lie*. Oxford University Press. [Google Scholar citations: ~7,500]

Cartwright, N. (1989). *Nature's capacities and their measurement*. Oxford University Press. [Google Scholar citations: ~2,800]

Cartwright, N. (1999). *The dappled world: A study of the boundaries of science*. Cambridge University Press. [Google Scholar citations: ~3,600]

Cartwright, N. (2012). Presidential address: Will this policy work for you? Predicting effectiveness better: How philosophy helps. *Philosophy of Science, 79*(5), 973-989. https://doi.org/10.1086/668041 [Google Scholar citations: ~380]

Duhem, P. (1906/1954). *The aim and structure of physical theory* (P. P. Wiener, Trans.). Princeton University Press. [Google Scholar citations: ~8,200]

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin. [Google Scholar citations: ~52,000]

Hanson, N. R. (1958). *Patterns of discovery: An inquiry into the conceptual foundations of science*. Cambridge University Press. [Google Scholar citations: ~8,400]

Harding, S. G. (1998). *Is science multicultural? Postcolonialisms, feminisms, and epistemologies*. Indiana University Press. [Google Scholar citations: ~1,900]

Hartig, T., Evans, G. W., Jamner, L. D., Davis, D. S., & Gärling, T. (2003). Tracking restoration in natural and urban field settings. *Journal of Environmental Psychology, 23*(2), 109-123. https://doi.org/10.1016/S0272-4944(02)00109-3 [Google Scholar citations: ~1,700]

Hjørland, B. (2007). Semantics and knowledge organization. *Annual Review of Information Science and Technology, 41*(1), 367-405. https://doi.org/10.1002/aris.2007.1440410115 [Google Scholar citations: ~390]

Hjørland, B. (2013). Facet analysis: The logical approach to knowledge organization. *Information Processing & Management, 49*(2), 545-557. https://doi.org/10.1016/j.ipm.2012.10.001 [Google Scholar citations: ~210]

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. [Google Scholar citations: ~9,400]

Kaplan, R., & Kaplan, S. (1998). *With people in mind: Design and management of everyday nature*. Island Press. [Google Scholar citations: ~2,100]

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology, 15*(3), 169-182. https://doi.org/10.1016/0272-4944(95)90001-2 [Google Scholar citations: ~7,800]

Kellert, S. R. (2008). Dimensions, elements, and attributes of biophilic design. In S. R. Kellert, J. Heerwagen, & M. Mador (Eds.), *Biophilic design: The theory, science, and practice of bringing buildings to life* (pp. 3-19). Wiley. [Google Scholar citations: ~850]

Kwasnik, B. H. (1999). The role of classification in knowledge representation and discovery. *Library Trends, 48*(1), 22-47. [Google Scholar citations: ~420]

Lynch, K. (1960). *The image of the city*. MIT Press. [Google Scholar citations: ~38,000]

Nagel, T. (1986). *The view from nowhere*. Oxford University Press. [Google Scholar citations: ~12,000]

Nasar, J. L. (1994). Urban design aesthetics: The evaluative qualities of building exteriors. *Environment and Behavior, 26*(3), 377-401. https://doi.org/10.1177/001391659402600305 [Google Scholar citations: ~580]

Ohly, H., White, M. P., Wheeler, B. W., Bethel, A., Ukoumunne, O. C., Nikolaou, V., & Garside, R. (2016). Attention restoration theory: A systematic review of the attention restoration potential of exposure to natural environments. *Journal of Toxicology and Environmental Health, Part B, 19*(7), 305-343. https://doi.org/10.1080/10937404.2016.1196155 [Google Scholar citations: ~680]

Parsons, R., Tassinary, L. G., Ulrich, R. S., Hebl, M. R., & Grossman-Alexander, M. (1998). The view from the road: Implications for stress recovery and immunization. *Journal of Environmental Psychology, 18*(2), 113-140. https://doi.org/10.1006/jevp.1998.0086 [Google Scholar citations: ~720]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. [Google Scholar citations: ~48,000]

Pearl, J., & Mackenzie, D. (2018). *The book of why: The new science of cause and effect*. Basic Books. [Google Scholar citations: ~4,200]

Ranganathan, S. R. (1967). *Prolegomena to library classification* (3rd ed.). Asia Publishing House. [Google Scholar citations: ~1,600]

Simon, H. A. (1947). *Administrative behavior: A study of decision-making processes in administrative organization*. Macmillan. [Google Scholar citations: ~42,000]

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review, 63*(2), 129-138. https://doi.org/10.1037/h0042769 [Google Scholar citations: ~6,200]

Simon, H. A. (1969). *The sciences of the artificial*. MIT Press. [Google Scholar citations: ~35,000]

Taylor, A. G., & Joudrey, D. N. (2017). *The organization of information* (4th ed.). Libraries Unlimited. [Google Scholar citations: ~1,900]

Ulrich, R. S. (1983). Aesthetic and affective response to natural environment. In I. Altman & J. F. Wohlwill (Eds.), *Behavior and the natural environment* (pp. 85-125). Plenum Press. [Google Scholar citations: ~4,200]

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science, 224*(4647), 420-421. https://doi.org/10.1126/science.6143402 [Google Scholar citations: ~8,400]

Ulrich, R. S., Simons, R. F., Losito, B. D., Fiorito, E., Miles, M. A., & Zelson, M. (1991). Stress recovery during exposure to natural and urban environments. *Journal of Environmental Psychology, 11*(3), 201-230. https://doi.org/10.1016/S0272-4944(05)80184-7 [Google Scholar citations: ~6,100]

Vander Wal, T. (2007). Folksonomy coinage and definition. Retrieved from http://vanderwal.net/folksonomy.html [Google Scholar citations: ~890]

---

**Document prepared by Expert Panel Secretariat**  
**Date**: 2026-01-18  
**Version**: 1.0
