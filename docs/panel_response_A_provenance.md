# Panel Response A: Knowledge as Situated Human Activity

## Can Statistical Patterns Substitute for Modeling Provenance?

**Date**: February 8, 2026  
**Convened by**: D. Kirsh, UCSD Cognitive Science  
**Panel Composition**: Social Epistemology, Testimony Epistemology, Philosophy of Language, Science Studies, Machine Learning/AI

---

## Preamble

The argument under review advances a thesis that is, at its core, both philosophically precise and practically urgent: that large language models, by virtue of their training regime, cannot perform the epistemic functions that rational belief management requires, because those functions are constitutively dependent on provenance information that the training process destroys. This is not an argument about what LLMs fail to do in practice—a point that might be remedied by engineering improvements—but about what they *cannot in principle* do given their representational commitments.

The panel has been asked to determine whether this limitation is fundamental or merely an engineering challenge. The answer, as will emerge, is that it is both—but in different respects, and the distinction matters enormously.

---

## I. Social Epistemology: Knowledge as Irreducibly Social

### Dr. Helen Longino (Stanford)

The argument's framing aligns closely with the program developed in *Science as Social Knowledge* (Longino, 1990) and extended in *The Fate of Knowledge* (Longino, 2002). The central claim of that program is that objectivity in science is not a property of individual epistemic agents or individual claims; it is a property of *social processes*—specifically, of critical discourse conducted under conditions of uptake, shared standards, qualified participation, and tempered equality. Knowledge claims achieve their epistemic status through surviving critical scrutiny within communities that enforce these norms.

The prompt's argument correctly identifies that LLM training collapses precisely this social structure. When gradient descent aggregates over a shuffled corpus, it destroys the discourse structure: the fact that claim *C* was challenged by researcher *R*, defended by *S*, replicated by *T*, and integrated into a consensus by community *K*. These are not ancillary facts about *C*; they are partially constitutive of *C*'s epistemic status. To know that a claim has survived critical scrutiny is to know something different from knowing the claim's propositional content. The LLM retains the latter while losing the former.

There is, however, a subtlety worth noting. Longino's framework distinguishes between the *content* of a knowledge claim and the *process* by which it was ratified. One might argue that the LLM, trained on the full textual record of a scientific community—the papers, the replies, the retractions, the meta-analyses—implicitly encodes the *outcome* of the social process even if it cannot represent the process itself. The model's parameter weights, on this view, reflect a kind of statistical equilibrium that corresponds, imperfectly, to community consensus.

This is partially correct but ultimately insufficient. The problem is that community consensus is not static. It is maintained by ongoing critical processes. When a new challenge arises, a rational agent must be able to revisit the evidential basis—who found what, how, and under what conditions—to reassess. The LLM's "consensus" is frozen at training time and, more problematically, is a weighted average that reflects *frequency of assertion* rather than *epistemic authority of asserters*. The two are, as the argument notes, often anti-correlated.

**Assessment**: The argument is sound on the social epistemology dimension. The destruction of provenance is not merely a loss of metadata; it is a loss of the social structure that confers epistemic status.

### Dr. Philip Kitcher (Columbia)

Kitcher's *Science, Truth, and Democracy* (2001) and earlier *The Advancement of Science* (1993) offer a framework of "well-ordered science" in which the division of cognitive labor and the social organization of inquiry play constitutive roles in the reliability of scientific knowledge. On Kitcher's account, the epistemic quality of a scientific community depends critically on the *distribution* of research strategies across investigators, which in turn depends on features like funding structures, career incentives, and institutional pressures.

The argument before us correctly identifies that an LLM cannot model this labor division. But Kitcher would push the point further: the argument underestimates the problem. It focuses primarily on the *weighting* and *interpretation* functions of provenance. But there is a third function that the prompt's analysis underplays: **the detection of systematic distortion**.

Consider the case of publication bias. A rational epistemic agent who knows that positive results are published at higher rates than null results will appropriately discount the frequency of positive claims in the literature. This requires modeling the *process* of publication—the incentive structures, the file-drawer problem, the editorial preferences—not just the *content* of published papers. An LLM trained on published text necessarily overweights published findings, with no capacity to correct for the known distortion introduced by the publication process itself.

Similarly, consider what Kitcher calls "cognitive pathologies"—situations where social organization systematically biases inquiry toward certain conclusions (e.g., industry-funded research on product safety). Detecting such pathologies requires modeling the *social organization of production*, not the textual residue it leaves behind. The distinction between "Industry study finds product safe" and "Independent study finds product safe" is not a stylistic distinction; it is a structural one concerning the relationship between the knowledge-producer and the object of knowledge.

**Assessment**: The argument is sound and, if anything, underestimates the scope of the problem by focusing on weighting and interpretation while giving less attention to the detection of systematic epistemic distortions.

### Dr. Miranda Fricker (CUNY)

The concept of *epistemic injustice* (Fricker, 2007) is directly relevant to the argument in a way the prompt's analysis does not fully develop. Epistemic injustice occurs when a speaker receives less credibility than they deserve due to prejudice—identity prejudice in testimonial injustice, or structural exclusion in hermeneutical injustice. The corrective for testimonial injustice is what Fricker calls the "virtuous hearer"—an agent who actively counteracts prejudicial credibility deflation.

An LLM trained on the historical textual record inherits the *distribution of credibility allocations* present in that record. If historically marginalized voices have been systematically cited less, published less, and referenced less, then the statistical patterns learned by the model will reproduce these patterns. The model does not merely *fail to correct* for epistemic injustice; it *encodes and perpetuates* it, because frequency of reference in the training corpus becomes a proxy for authority in the model's parameter space.

This is not merely a fairness problem (though it is that). It is an *epistemic reliability* problem. If good evidence from marginalized researchers is systematically downweighted because the training corpus underrepresents their work, then the model's "knowledge" is systematically distorted by the same prejudicial structures that social epistemology has identified as threats to objective inquiry.

Correcting this requires the kind of provenance modeling the argument advocates: knowing *who* produced a finding, being able to assess their competence *independent of* the frequency with which they are cited, and explicitly counteracting patterns of unjust credibility allocation. None of this is available to a system that collapses source identity into parameter averages.

**Assessment**: The argument is sound and gains additional force when we recognize that the loss of provenance doesn't just prevent rational weighting—it perpetuates patterns of epistemic injustice embedded in the training corpus.

---

## II. Epistemology of Testimony: Speaker Assessment as Constitutive

### Dr. C.A.J. Coady (Melbourne)

The philosophical study of testimony—learning from the word of others—has, since at least Reid (1764/1997), recognized that testimony is a *fundamental* source of knowledge, not reducible to perception or inference. In *Testimony: A Philosophical Study* (Coady, 1992), the argument is made that our default entitlement to believe what we are told is a necessary condition for any linguistic community, since language acquisition itself depends on testimonial trust.

However—and this is the critical point for the present discussion—even the most generous account of testimonial entitlement includes conditions under which that default trust should be *withdrawn*. Coady identifies "negative" conditions: when a speaker is known to be unreliable on this topic, when they have apparent interests that conflict with truthful testimony, when the claim is implausible given background knowledge, and so on. These are sometimes called *defeaters* in the epistemological literature (Pollock, 1986).

The argument under review essentially contends that an LLM cannot process defeaters because defeater-detection requires knowing who the speaker is and what contextual factors might undermine their testimony. This is correct. An LLM processes text as text—as a string of tokens—without modeling the speaker as an agent with properties (expertise, interests, track record) that bear on testimonial reliability. When the model "learns" from a corpus that includes both trustworthy and untrustworthy testimony, it has no mechanism for applying differential defeaters to different sources.

There is a potential objection worth addressing. One might argue that the LLM learns to *detect unreliability markers* in text—e.g., the linguistic correlates of pseudoscience, the stylistic signatures of propaganda. To some degree this is true: the model likely encodes statistical associations between certain textual features and unreliability. But as the argument's "Problem 1" correctly notes, the mapping from style to authority is many-to-many. Reliable experts writing informally look stylistically similar to unreliable amateurs writing informally. Unreliable sources writing formally look stylistically similar to reliable sources writing formally. The predatory journal problem is precisely a case where surface markers of authority are deliberately mimicked in the absence of the underlying epistemic substance.

**Assessment**: The argument is sound from the perspective of testimony epistemology. Defeater-processing requires speaker models, and speaker models require provenance.

### Dr. Jennifer Lackey (Northwestern)

Lackey's *Learning from Words* (2008) develops a *dualist* account of testimonial knowledge that requires both speaker competence (the speaker must know what they assert) and hearer rationality (the hearer must not believe against their evidence). This dual requirement is directly relevant.

On Lackey's view, testimonial knowledge is not merely a matter of passively receiving reliable information. The hearer has an active epistemic responsibility to evaluate the speaker's competence and sincerity, at least to the degree that contextual information permits. This is what Lackey calls the "monitoring" component of testimonial knowledge.

The LLM fails on both sides of the dual requirement. On the speaker side: the model cannot assess speaker competence because competence is a property of *agents*, not of texts. The same agent can be competent on topic T₁ and incompetent on T₂, as the argument's "Dr. Smith" example illustrates. On the hearer side: the model cannot monitor for defeaters because monitoring requires tracking the relationship between the speaker's properties and the specific claim being made.

Lackey has also argued (Lackey, 2006) that *safe testimony*—testimony that is modally robust, i.e., would be true in nearby possible worlds—requires not just actual speaker reliability but a stable *basis* for that reliability (expertise, direct knowledge, institutional backing). An LLM that generates authoritative-sounding text may produce claims that are actually true, but if those claims lack a robust basis (because the model has no basis—it has statistical associations), then the "testimony" is not *safe* in Lackey's sense, even when it happens to be correct. This matters because unsafe testimony does not support knowledge even when true; it lacks the modal stability required.

**Assessment**: The argument is sound. Lackey's framework further reveals that even when LLMs produce true claims, the absence of grounded speaker competence means the outputs lack the modal robustness required for testimonial knowledge.

---

## III. Philosophy of Language and Pragmatics: Speaker-Relative Meaning

### Dr. Paul Grice (Represented Posthumously)

The Gricean framework (Grice, 1975, 1989) distinguishes between *what is said* (sentence meaning, roughly truth-conditional content) and *what is implicated* (speaker meaning, inferred from the cooperative principle and its maxims). This distinction is fundamental to the argument's Function 2 (Interpretation).

Conversational implicature depends essentially on *mutual knowledge of the speaker's intentions*. When a reviewer writes "that's an interesting approach," the hearer can infer "that's problematic" only by recognizing that the speaker, in this context, is observing the maxim of Quality (say what you believe to be true) while flouting the maxim of Quantity (be as informative as required), thereby implicating something beyond the literal content. This inference requires modeling the speaker as a *rational cooperative agent* with specific communicative intentions.

The argument correctly identifies that LLMs cannot perform this inference in a principled way. The model may learn a statistical association between "that's an interesting approach" in review contexts and negative evaluations—a kind of distributional regularity. But there is a deep difference between learning *that* this phrase is sometimes negative and understanding *why* it is negative in *this* context, which would require representing the speaker's intentions and the conversational maxims they are observing or flouting.

This matters for the scientific domain because scientific discourse is dense with implicature. Hedging language ("may suggest," "is consistent with") carries different implicatures depending on whether the speaker is being cautious (genuine uncertainty), diplomatic (avoiding direct contradiction of a senior colleague), or strategic (positioning for future claims of priority). These distinctions are invisible to distributional analysis.

**Assessment**: The argument is sound on pragmatic grounds. Gricean implicature requires speaker models that are constitutive of intended meaning, not merely statistically associated with it.

### Dr. John Searle (Berkeley)

Searle's speech act theory (Searle, 1969, 1979) provides another dimension of the argument's case for Function 2. The same sentence can constitute different speech acts depending on speaker, context, and institutional facts. "The defendant is guilty" is a *verdict* when uttered by a judge, a *report* when uttered by a journalist, an *opinion* when uttered at a dinner party, and a *prediction* when uttered by an attorney before trial. These are not mere connotative differences; they are differences in *illocutionary force* that determine what the utterance *does* in the world.

Crucially, institutional facts—the background of constitutive rules that give certain utterances their force—depend on *who* is speaking and *in what capacity*. An FDA document saying "the drug is effective" constitutes an institutional fact (regulatory approval) in a way that a blog post using the same words does not. The illocutionary force is different because the speaker occupies a different institutional position.

Searle's framework of *Background* capacities (Searle, 1983) is also relevant: understanding an utterance requires a Background of embodied, situated capacities that enable interpretation. An LLM has no Background in Searle's sense—no embodied experience, no institutional position, no social location from which to interpret utterances. It has statistical patterns over strings, which is a different kind of thing entirely.

**Assessment**: The argument is sound. Speech act theory demonstrates that the illocutionary force of utterances depends constitutively on speaker identity and institutional context, neither of which is represented in LLM parameters.

### Dr. Robert Brandom (Pittsburgh)

Brandom's inferentialist semantics (Brandom, 1994, 2000) offers perhaps the deepest philosophical challenge to the idea that LLMs can approximate epistemic reasoning. For Brandom, the meaning of a claim is not determined by its truth conditions or its reference but by its *inferential role*—the commitments it undertakes and the entitlements it confers within a *social practice of giving and asking for reasons*.

On this view, understanding a claim requires knowing what else a speaker is *committed to* by making the claim, what *entitlements* the claim confers on both speaker and hearer, and what *incompatibilities* it introduces with other commitments. These are properties of *scorekeeping* in the space of reasons—a fundamentally social practice that tracks who is committed to what and who is entitled to what.

The argument under review maps neatly onto Brandom's framework. The LLM cannot engage in deontic scorekeeping because: (a) it does not represent speakers as agents with commitment sets, (b) it does not track the inferential consequences of assertions as they propagate through a discourse, and (c) it does not distinguish between entitled and unentitled assertions. When the model generates a claim, it is not *undertaking a commitment* (since it has no commitment set); it is producing a string that is statistically likely given its training distribution. This is, from Brandom's perspective, a fundamentally different activity from assertion.

The relevant implication for the provenance argument is this: on an inferentialist account, even the *content* of a claim is partially determined by the web of inferential commitments surrounding it, which is in turn determined by who is making the claim and what else they are committed to. This means that provenance is not merely relevant to *weighting* a claim whose content is independently determined. Provenance is partially constitutive of *what the claim means*. When different researchers use the term "learning" in different theoretical frameworks, they are not making the same claim with different authority; they are making *different claims* with different inferential roles.

This is a stronger conclusion than the prompt's own "Refined Claim," which treats weighting and interpretation as two separate functions. Brandom's framework suggests they are deeply intertwined: you cannot properly weight a claim without knowing what it means, and you cannot know what it means without knowing who is asserting it and what inferential commitments they bring.

**Assessment**: The argument is sound and, from an inferentialist perspective, actually understates the problem. Provenance is constitutive not merely of epistemic weight but of semantic content itself.

---

## IV. Science Studies: The Situatedness of Knowledge Production

### Dr. Bruno Latour (Sciences Po)

Latour's body of work—from *Laboratory Life* (Latour & Woolgar, 1979) through *Science in Action* (Latour, 1987) to the recent *Facing Gaia* (Latour, 2017)—has consistently argued that scientific facts are not discovered but *constructed* through networks of human and non-human actors (instruments, institutions, funding bodies, publication systems). On this view, a scientific claim is never "just" a proposition; it is a *node in a network* of associations that stabilize it.

The argument's characterization of LLMs as processing "outputs" while losing the "activity" that produced them is, in Latourian terms, the loss of the *network*. A claim that has been stabilized by replication, institutional endorsement, and integration into textbooks has passed through what Latour calls *trials of strength*—processes that test whether the claim can withstand challenge. A claim that has not been so tested, or that has been challenged and defended, or that has been retracted and reinstated, occupies a very different position in the network.

The LLM collapses all of this into parameter weights. The well-tested claim and the untested claim, if they produce similar token distributions, become indistinguishable in the model's representation. This is precisely the loss that the argument identifies: the destruction of the *actant network* that confers factual status.

Latour would add a point the argument does not fully develop: the *materiality* of knowledge production matters. It matters which instruments were used, what material conditions obtained, what calibration procedures were followed. These material practices leave textual traces (methods sections, supplementary materials), but the traces are highly compressed summaries of embodied, material activities. The LLM reads the summary without access to the activity summarized.

**Assessment**: The argument is sound. From a science studies perspective, it correctly identifies that LLMs process the products of inscription while losing the networks of production that confer factual status.

### Dr. Steven Shapin (Harvard)

Shapin's *A Social History of Truth* (1994) argues that the epistemological practices of modern science are rooted in historically specific social conventions about trust, credibility, and testimony. The "gentleman" of early modern natural philosophy was credible precisely because of his social position—independent means, no need to lie—and modern science inherits (in transformed fashion) this dependence on *social identity* as a credibility marker.

This historical perspective reinforces the argument in a specific way: the social practices that determine credibility are not *natural kinds* discoverable by statistical analysis. They are historically contingent conventions that vary across periods and communities. What counts as a credible source in 1950s behaviorist psychology is different from what counts as credible in 2020s computational neuroscience—not because the statistical patterns of the text are different (though they may be), but because the *community's standards for credibility allocation* have changed.

An LLM trained on the entire historical record averages across these shifting standards, producing a kind of temporal smearing of credibility norms. This is not merely imprecise; it is systematically misleading, because it treats historically superseded standards as equally current. The model cannot represent the *temporal structure* of credibility conventions because temporal order was destroyed in training.

Shapin would also emphasize that trust in science is fundamentally *interpersonal*—it depends on face-to-face interaction, reputation, institutional affiliation, and a thick context of social relationships. The idea that statistical patterns over text could substitute for this interpersonal trust structure would strike him as a category error, confusing the *record* of trust practices with the practices themselves.

**Assessment**: The argument is sound. Shapin's work adds the historical dimension: credibility norms are not only social but *historically situated*, and temporal averaging in training further distorts the representation.

---

## V. Machine Learning and AI: What Current Architectures Can and Cannot Represent

### Dr. Yoshua Bengio (Mila)

The argument makes several technical claims about LLM architecture that deserve careful evaluation from within the ML research community. The core technical claims are: (1) gradient descent with shuffled batches destroys temporal and source ordering; (2) the resulting parameter weights represent a blended average over sources; (3) attention mechanisms operate over context windows, not training data; (4) these mechanisms were optimized for prediction, not epistemic weighting.

Claims (1) through (3) are technically accurate. Standard training procedures do indeed shuffle data, aggregate gradients, and produce parameter configurations that cannot be decomposed into source-specific contributions. Claim (4) is also correct as a description of current training objectives, though it deserves nuance.

The question of whether *alternative training regimes* could address these limitations is more interesting. Several directions are worth considering:

**Conditional training with provenance tokens.** One could augment training data with metadata tokens—author identifiers, journal identifiers, date stamps, institutional affiliations—and train the model to condition its generation on these features. This has been explored in limited forms (e.g., domain-adaptive pretraining; Gururangan et al., 2020). In principle, this could allow the model to generate text *as if* from a specific source type. But this is generation conditioned on source type, not *epistemic reasoning* about source authority. The model would learn to produce FDA-style text when prompted with an FDA token, not to reason about why FDA assertions deserve different epistemic weight than blog assertions.

**Retrieval-augmented generation with authority metadata.** RAG systems (Lewis et al., 2020) could be extended to include authority scores in the retrieval step, biasing retrieval toward more authoritative sources. This is technically feasible and represents a genuine improvement. But, as the argument correctly notes, this requires *adding explicit structure*—an authority scoring system external to the model—which concedes the central point.

**Multi-agent architectures.** Systems in which different model instances represent different expert perspectives, with an aggregation mechanism that explicitly weights by source authority, could approximate some of the provenance functions described. This is a form of hybrid architecture that again adds explicit epistemic structure.

The deeper question is whether provenance-sensitive representations could *emerge* from scale alone, without architectural modifications. The relevant theoretical framework here is the *manifold hypothesis* in representation learning (Bengio et al., 2013): high-dimensional data lies on lower-dimensional manifolds, and sufficiently powerful models discover these manifolds. Could the manifold of "authoritative scientific text" separate cleanly from the manifold of "non-authoritative text"?

The answer is: partially, but not sufficiently. Style-based separation (formal vs. informal, hedged vs. confident) does emerge. But *topic-relative authority*—the fact that the same author is authoritative on cardiology and non-authoritative on economics—requires relational representations that distributional learning does not naturally produce. Authority is a relation between speakers, topics, and contexts; it is not a distributional feature of text.

**Assessment**: The argument's technical claims are accurate. The limitation is not *absolute*—architectural modifications could add provenance-sensitivity—but such modifications require *adding explicit epistemic structure*, which concedes the argument's central point. Pure scaling of current architectures will not solve the problem.

### Dr. Percy Liang (Stanford)

Liang's work on foundation models (Bommasani et al., 2021) and the HELM benchmark (Liang et al., 2023) provides a framework for evaluating LLM capabilities systematically. The foundation model paradigm is premised on the idea that general-purpose models trained on broad data can be adapted to specific tasks through fine-tuning or prompting. The question here is whether "epistemic authority assessment" is the kind of task that admits of such adaptation.

The argument identifies a critical distinction that the foundation model literature has not adequately addressed: the difference between *generation capabilities* and *reasoning capabilities* with respect to provenance. Foundation models clearly learn to *generate* text that mimics authoritative discourse. The question is whether they can *reason about* authority—i.e., given two conflicting claims from different sources, determine which should be weighted more heavily and why.

Empirical evidence is somewhat informative here. Several studies have examined LLM performance on tasks that require source evaluation:

1. **Factual accuracy benchmarks** show that LLMs frequently assert false claims with high confidence (Lin et al., 2022), suggesting that their internal representations do not reliably track the reliability of underlying sources.

2. **Calibration studies** show that LLM confidence scores do not correlate well with correctness (Kadavath et al., 2022), which is what we would expect if the model lacks a principled mechanism for weighting by source quality.

3. **Prompt-based authority cueing** can shift model outputs—e.g., prefacing a question with "According to peer-reviewed research..." vs. "According to online forums..." elicits different responses (Petroni et al., 2019, and subsequent work). But this demonstrates *sensitivity to authority cues in the prompt*, not *internal reasoning about authority*. The model adjusts its generation to match the register suggested by the prompt, not to track epistemic status.

A useful framing from the HELM perspective: if we were to design a benchmark for "provenance-sensitive epistemic reasoning," what would it look like? It would need to test whether a model can (a) differentially weight conflicting claims based on source attributes, (b) adjust interpretations based on speaker community, (c) detect when a source's interests conflict with its testimony, and (d) update these assessments as new provenance information is provided. Current LLMs would perform poorly on such a benchmark—not because they have not been specifically trained for it, but because the required information is not available in their representations.

**Assessment**: The argument is sound. The foundation model paradigm's strengths (broad coverage, generalization) are precisely mismatched to the requirements of provenance-sensitive reasoning, which demands specific, structured information about sources rather than general distributional patterns.

### Dr. Melanie Mitchell (Santa Fe Institute)

Mitchell's work on analogy and conceptual abstraction (Mitchell, 1993; Mitchell, 2019) provides an important perspective on the argument's claim that LLMs perform "pattern matching over surface features" rather than genuine reasoning about authority.

Mitchell has argued (Mitchell, 2021) that current AI systems, including LLMs, achieve *narrow* competence through statistical pattern matching while lacking the *conceptual understanding* that would support robust generalization. This distinction maps directly onto the argument's core claim: the LLM can match the pattern "FDA text looks like this, blog text looks like that" without understanding the *concept* of epistemic authority that explains *why* these patterns differ and *how* they should be used.

The conceptual understanding of authority involves at minimum: (a) understanding that speakers have *mental states* (beliefs, intentions, interests) that influence their testimony, (b) understanding that *expertise* is domain-specific and varies across individuals, (c) understanding that *institutional structures* create systematic incentives and constraints on testimony, and (d) understanding that *discourse history* determines what is at stake in a given assertion. These are *conceptual* competencies that require representing abstract relations, not just statistical regularities.

Mitchell's analysis of analogy is also relevant. Scientific reasoning frequently involves analogical transfer—applying reasoning from one domain to another. Determining when such transfer is legitimate requires understanding the *structural relationships* in each domain, not just surface similarities. Similarly, determining when a source's authority in one domain transfers to another requires structural understanding of domain relationships—understanding that cardiology expertise partially transfers to vascular biology but not to economics, for instance.

The argument's "Dr. Smith" example illustrates this perfectly. An LLM might learn that "Dr. Smith" is associated with medical terminology and therefore generates medical text when prompted with that name. But it cannot reason about *why* Dr. Smith's authority transfers to epidemiology (shared methodological foundations) but not to economics (no shared foundations). This kind of structural analogy between domains of expertise is precisely the kind of conceptual reasoning that, on Mitchell's account, lies beyond current distributional methods.

**Assessment**: The argument is sound. The distinction between pattern matching over authority-correlated features and conceptual understanding of authority is real and consequential. Current architectures achieve the former but not the latter.

---

## VI. Responses to Panel Questions

### Question 1: Is the refined argument sound?

**Panel consensus: Yes, with qualifications.** The six-part refined claim (traces exist, are noisy, non-relational, non-queryable, blended, and therefore insufficient for explicit epistemic computation) is accurate. The primary qualification is that the argument is actually *stronger* than its own refined claim suggests, particularly from inferentialist (Brandom) and social epistemology (Longino, Fricker) perspectives, where provenance is constitutive of meaning and epistemic status, not merely useful for weighting.

### Question 2: Could implicit traces be made explicit?

The panel's assessment is that this is possible in limited respects but faces principled barriers. Probing techniques (Li et al., 2023; Burns et al., 2023) can extract some latent structure from model representations—for instance, identifying whether a representation encodes "scientific register" vs. "informal register." But the kind of information needed—topic-specific authority, speaker interests, discourse position—is *relational* in character, and there is strong theoretical reason (drawn from both the philosophy side and the ML side) to doubt that relational information can be reliably recovered from distributional representations that were not trained to preserve it.

The analogy to lossy compression is apt: some information is recoverable from compressed representations, but information that was *not salient to the compression objective* (next-token prediction) is likely to be irretrievably lost. Provenance information that leaves distributional traces (stylistic markers) is partially recoverable; provenance information that does not (topic-specific authority, speaker interests) is probably not.

### Question 3: Can attention mechanisms be leveraged for epistemic weighting?

**No, not as currently implemented.** As the argument correctly states, attention in transformer architectures was learned for prediction-relevance, not epistemic weighting. The attention pattern that maximizes next-token prediction is the one that attends to tokens most informative for predicting the next token—which correlates with topical relevance and syntactic structure, not with source authority.

Could attention be *repurposed* for authority weighting? In principle, yes—through fine-tuning with authority-labeled data or through architectural modifications that add authority-based attention heads. But this constitutes adding explicit structure, not leveraging existing implicit capabilities.

There is one important nuance: in-context learning (Brown et al., 2020) allows LLMs to approximate new functions when given examples in the prompt. If the prompt includes explicit authority labels ("Source: NEJM Phase III trial" vs. "Source: wellness blog"), the model may attend differentially to these in a way that approximates authority weighting. But this requires the *user* to supply the provenance structure—exactly the external augmentation the argument predicts is necessary.

### Question 4: Can scale overcome these limitations?

**The panel's consensus is: no, not through scale alone.** The argument against scale-based solutions is straightforward and, in the panel's view, compelling. The training objective (next-token prediction) does not include an authority-tracking loss term. Scaling model parameters, data volume, or training compute improves performance on the training objective without creating new objectives. Authority-sensitive reasoning would require either (a) a modified training objective that rewards authority-appropriate weighting, (b) training data augmented with provenance labels, or (c) architectural components that explicitly represent source structure.

This is not to say that scale provides *nothing*. Larger models likely learn finer-grained stylistic distinctions and may be better at detecting surface-level unreliability markers (e.g., the presence of citations, hedging language, specific quantification). But these improvements are improvements in the quality of the *noisy, non-relational traces* the argument identifies—not progress toward the *explicit, relational, queryable* provenance representations that epistemic reasoning requires.

There is a useful analogy from the history of AI: the symbolic AI community's "frames problem" (McCarthy & Hayes, 1969). The frames problem showed that representing *change* requires explicit mechanisms that do not emerge from static representations, no matter how detailed. The provenance problem has a similar structure: representing *epistemic authority* requires explicit mechanisms that do not emerge from distributional representations, no matter how large.

### Question 5: Fundamental limitation or engineering challenge?

**Both, but in distinct respects.** The panel distinguishes two claims:

**(a) The representation claim:** Current LLM architectures, trained on text without provenance labels using next-token prediction, cannot represent provenance in the way required for epistemic reasoning. This is a *fundamental limitation of the representation* given the architecture and training regime.

**(b) The architectural claim:** No neural architecture could ever represent provenance sufficiently for epistemic reasoning. This is much stronger and the panel does *not* endorse it.

Hybrid architectures—neurosymbolic systems, memory-augmented networks, graph neural networks with explicit entity representations, multi-agent systems with role-differentiated components—could in principle represent the required provenance structure. These would be *engineering solutions*, but solutions that require *explicitly adding the kind of structure the argument identifies as missing*.

The fundamental insight is: **provenance information must be explicitly represented to be explicitly reasoned about.** This is a constraint on any system, not just neural networks. The question is whether the explicit representation is embedded in the architecture (symbolic), in the training data (labeled), in external augmentation (RAG with authority scoring), or in the inference procedure (multi-agent deliberation). What cannot work is hoping that the representation emerges implicitly from scale.

This maps onto what Fodor and Pylyshyn (1988) called the *systematicity* of thought: certain cognitive capacities are constitutively linked, such that having one requires having others. If a system can reason about epistemic authority, it must be able to represent sources, track their properties, and compute over those representations. These capacities are systematic in Fodor and Pylyshyn's sense: you cannot have authority reasoning without source representation.

### Question 6: What would count as a counterexample?

The panel proposes the following test, refined from the prompt's suggestion:

**The Provenance Reasoning Test (PRT):** Present the model with a set of conflicting claims on a topic, each attributed to a source described only by name and institutional affiliation (no stylistic cues in the claim text itself). Assess whether the model can:

1. Correctly rank the claims by epistemic authority on *this* specific topic
2. Explain *why* the ranking is appropriate (topic-specific expertise, potential conflicts of interest, institutional credibility)
3. Adjust the ranking when new information is provided about a source (e.g., "Source X has published 30 papers on this topic" or "Source Y was funded by the manufacturer")
4. Transfer the reasoning to a novel domain (e.g., if the model correctly ranks medical sources, can it correctly rank legal sources using analogous principles?)

A model that passes all four components would constitute a genuine counterexample, as it would demonstrate *reasoning about authority as a relational property* rather than pattern-matching over stylistic features.

The panel's prediction: current LLMs will fail components 2-4 reliably, with partial success on component 1 only when source identity correlates with patterns in the training data (e.g., the model "knows" that NEJM is a prestigious medical journal because this is frequently stated in its training corpus, but cannot reason about *why* this matters for a specific claim).

### Question 7: Does the testimony literature support the argument?

**Yes, strongly.** The testimony literature (Coady, 1992; Lackey, 2008; Fricker, 2007) establishes that speaker assessment is *necessary for rational belief from testimony*, not merely *useful as a heuristic*. The distinction is clear:

A heuristic for evaluating testimony would be: "generally prefer formal sources over informal ones." This could be implemented as a statistical pattern without genuine speaker modeling.

The requirement established by the testimony literature is stronger: "evaluate the specific speaker's competence on the specific topic, given the specific context, including potential defeaters." This cannot be reduced to a heuristic because the relevant factors are open-ended, domain-specific, and context-sensitive.

Lackey's (2008) argument is especially clear: testimonial knowledge requires that the speaker *knows* the proposition asserted (not just that they happen to state something true). Assessing whether a speaker knows requires modeling their epistemic position—their access to evidence, their competence to evaluate it, their freedom from distorting interests. This is not reducible to a statistical pattern over text.

There are philosophers who take a more "reductionist" view of testimony—roughly, that testimonial knowledge reduces to inductive evidence about speaker reliability (Hume, 1748/2000, is sometimes read this way; Fricker, 1994, gives a more sophisticated reductionist account). Even on these reductionist views, the *evidence about speaker reliability* must be tracked, which requires provenance information. So even the weakest position in the testimony literature supports the core argument.

### Question 8: Relationship to other debates

The argument connects to several major debates in philosophy of mind and AI:

**Symbol grounding problem** (Harnad, 1990): Just as symbols require grounding in sensory experience to have meaning, authority claims require grounding in social reality—institutional positions, expertise relations, interest structures—to have epistemic force. The LLM's "authority representations" are ungrounded in the same way its symbol representations are: they are statistical associations between tokens, not grounded assessments of social reality.

**Frame problem** (McCarthy & Hayes, 1969; Shanahan, 1997): The frame problem concerns which aspects of a situation change (and which remain stable) when an action is taken. Analogously, the provenance problem concerns which aspects of a claim's epistemic status change when contextual information changes (e.g., when we learn that a study's funder had a financial interest). Both problems require explicit tracking of relevant factors and cannot be solved by default reasoning over distributions.

**Contextual embeddings and polysemy**: Modern transformer architectures produce context-dependent word embeddings (Devlin et al., 2019), which partially addresses polysemy at the *linguistic* level (the same word means different things in different textual contexts). But the argument's "learning" example (behaviorist vs. cognitivist vs. connectionist) shows that the relevant context is not *textual* but *theoretical*—which community the speaker belongs to. Contextual embeddings capture textual context but not theoretical-community context.

**Compositionality**: The argument relates to debates about whether neural networks achieve compositionality (Hupkes et al., 2020; Lake & Baroni, 2018). Authority reasoning is compositional: the authority of a source on a topic is a function of the source's properties and the topic's properties, composed according to rules (expertise matching, conflict of interest detection, etc.). If neural networks struggle with compositionality generally, they will struggle with this specific compositional task.

**Social dimensions of AI alignment**: The argument has direct implications for the AI alignment literature. If LLMs cannot reason about epistemic authority, they cannot reliably distinguish trustworthy from untrustworthy information. This makes them vulnerable to data poisoning (the "10,000 wellness blogs vs. 100 oncology papers" scenario), which is a specific form of the alignment problem: aligning the model's outputs with human epistemic values requires the kind of provenance-sensitive reasoning that the model cannot perform.

### Question 9: If the argument is correct, what follows?

**(a) Explicit provenance modeling is necessary for trustworthy AI.** Any AI system intended to support rational decision-making—in medicine, law, policy, science—must incorporate explicit representations of who produced what information, under what conditions, with what authority, and with what potential biases. This is not optional; it is a requirement of rational belief management.

**(b) Training data should be labeled with source metadata.** The current practice of training on undifferentiated text corpora, with provenance stripped or ignored, is epistemically irresponsible. Even minimal metadata—source type (peer-reviewed journal, newspaper, blog, corporate communication), publication date, institutional affiliation—would substantially improve the model's capacity for provenance-sensitive processing.

**(c) Hybrid architectures are the most promising path.** The combination of neural language models (for language understanding and generation) with explicit knowledge structures (for provenance tracking, authority assessment, and epistemic reasoning) is not merely one option among many; it is the architecture that the epistemological analysis points toward. The Article Eater project's architecture—with its explicit web of belief, theory registry, and extraction-to-web mapper—is an example of this hybrid approach, and the argument provides philosophical justification for its design.

**(d) "Next-generation RAG" requires social epistemology.** The argument's vision of RAG augmented with authority scoring, speaker modeling, and community-relative interpretation is not merely an engineering improvement. It is a different paradigm: retrieval guided not by semantic similarity but by epistemic authority, with generation constrained not by distributional likelihood but by the rational norms of testimony assessment. This is the computational operationalization of social epistemology.

### Question 10: From Latour/Shapin—What epistemic status does LLM "knowledge" have?

This is perhaps the most philosophically interesting question. The panel proposes the following answer:

LLM outputs have the epistemic status of **aggregate hearsay with unknown provenance**—a kind of unattributed statistical digest of the training corpus. This is a legitimate but severely limited form of information that is useful for certain purposes (generating plausible text, suggesting starting points for inquiry, identifying relevant vocabulary and concepts) but inappropriate for purposes that require rational belief management (clinical decision support, legal reasoning, policy analysis, scientific synthesis).

The analogy to a specific social institution is illuminating: the LLM is like a **very well-read but unreliable narrator**—someone who has consumed an enormous amount of text, can reproduce its patterns and conventions fluently, but cannot tell you where any particular claim came from, cannot assess the reliability of their sources, and cannot distinguish between what they "know" from Nature and what they "know" from a wellness blog. We would not trust such a narrator for serious epistemic purposes, however impressive their fluency.

Shapin's historical analysis adds a further dimension. In the early modern period, knowledge from testimony was calibrated by *social identity*—the gentleman's word was trusted because his social position made lying costly. Modern science replaced this with institutional mechanisms—peer review, replication, conflict of interest disclosure—that perform the same calibration function through different means. The LLM strips away *both* calibration systems: it has neither the social identity information nor the institutional metadata. What remains is *text without calibration*—a form of information that is, in Shapin's terms, pre-epistemic: it has not yet been subjected to the social processes that convert information into knowledge.

---

## VII. Panel Consensus and Synthesis

### Consensus Statement

The panel reaches the following consensus, with no dissenting members:

**1. The limitation is fundamental with respect to current architectures and training regimes.** Standard LLMs trained on text without provenance labels cannot, in principle, perform the epistemic functions of provenance-sensitive reasoning (differential weighting by source authority, speaker-relative interpretation, defeater detection, systematic distortion correction). This is not a matter of insufficient scale or compute; it is a consequence of the training regime's destruction of the information required for these functions.

**2. The limitation is surmountable through architectural augmentation, but not through scaling.** Hybrid systems that explicitly represent provenance information—through labeled training data, authority-aware retrieval, multi-agent architectures, or external knowledge structures—can in principle address the limitation. But these solutions all involve *adding explicit epistemic structure*, which concedes the argument's central claim: explicit epistemic computation requires explicit epistemic structure.

**3. The argument is actually stronger than its own "refined claim" suggests.** The refined claim treats weighting and interpretation as two separate functions that both require provenance. The panel (drawing on Brandom, Longino, and Fricker) holds that provenance is constitutive of *meaning* (not just weight), *epistemic status* (not just credibility assessment), and *epistemic justice* (not just calibration). The scope of the problem is wider than the argument itself acknowledges.

### Formal and Empirical Results That Would Settle the Question

1. **Information-theoretic analysis.** A formal proof that the mutual information between source identity and model parameters approaches zero as training data is shuffled and aggregated would provide rigorous support for the argument. Conversely, a proof that this mutual information remains bounded above zero in specific parameter regions would partially challenge the argument.

2. **Provenance Reasoning Test (PRT) benchmark.** An empirical benchmark (as described under Question 6) that systematically tests LLMs' capacity for topic-specific authority assessment, interest-based bias detection, and community-relative interpretation would provide definitive empirical evidence. The panel predicts that current LLMs will fail this benchmark on the dimensions requiring relational reasoning about authority.

3. **Probing studies.** Detailed probing of LLM hidden representations to determine whether source-type information is linearly extractable from intermediate layers would clarify the extent of implicit provenance encoding. Existing work (e.g., Belinkov, 2022) provides methodological templates.

4. **Controlled provenance corruption studies.** Training models on corpora where provenance labels are systematically corrupted (e.g., attaching prestigious journal names to pseudoscientific text) and measuring the impact on model outputs would directly test whether the model encodes *substantive* authority or merely *surface markers* of authority.

### Practical Implications for AI System Design

1. **Provenance-labeled training corpora** should become standard practice for AI systems intended to support epistemic reasoning. At minimum, metadata should include source type, institutional affiliation, publication date, and known conflicts of interest.

2. **Authority-aware retrieval** should replace or augment semantic similarity-based retrieval in RAG systems. This requires explicit authority scoring models that are *separate from* and *prior to* the language model's generation step.

3. **Epistemic metadata layers** should be added to language model outputs: every generated claim should be accompanied by structured information about its provenance (source types, confidence calibration, known limitations), not merely a fluency score.

4. **The Article Eater architecture**—with its explicit web of belief, theory registry, and extraction-to-web mapper—represents a promising template for how these capabilities can be implemented in practice. Its design reflects the epistemological requirements identified in this analysis.

5. **Regulatory frameworks** for AI in high-stakes domains (medicine, law, policy) should require explicit provenance tracking as a condition of deployment. The argument establishes that systems without such tracking cannot be trusted for rational belief management, regardless of their fluency or apparent accuracy.

---

## References

Belinkov, Y. (2022). Probing classifiers: Promises, shortcomings, and advances. *Computational Linguistics*, 48(1), 207–219. https://doi.org/10.1162/coli_a_00422 [Google Scholar: ~400 citations]

Bengio, Y., Courville, A., & Vincent, P. (2013). Representation learning: A review and new perspectives. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 35(8), 1798–1828. https://doi.org/10.1109/TPAMI.2013.50 [Google Scholar: ~20,000 citations]

Bommasani, R., Hudson, D. A., Adeli, E., Altman, R., Arber, S., von Arx, S., ... & Liang, P. (2021). On the opportunities and risks of foundation models. *arXiv preprint arXiv:2108.07258*. [Google Scholar: ~3,500 citations]

Brandom, R. (1994). *Making it explicit: Reasoning, representing, and discursive commitment*. Harvard University Press. [Google Scholar: ~5,500 citations]

Brandom, R. (2000). *Articulating reasons: An introduction to inferentialism*. Harvard University Press. [Google Scholar: ~2,500 citations]

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems*, 33, 1877–1901. [Google Scholar: ~30,000 citations]

Burns, C., Ye, H., Klein, D., & Steinhardt, J. (2023). Discovering latent knowledge in language models without supervision. *International Conference on Learning Representations (ICLR 2023)*. [Google Scholar: ~200 citations]

Coady, C. A. J. (1992). *Testimony: A philosophical study*. Oxford University Press. [Google Scholar: ~2,200 citations]

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *Proceedings of NAACL-HLT 2019*, 4171–4186. [Google Scholar: ~90,000 citations]

Fodor, J. A., & Pylyshyn, Z. W. (1988). Connectionism and cognitive architecture: A critical analysis. *Cognition*, 28(1–2), 3–71. https://doi.org/10.1016/0010-0277(88)90031-5 [Google Scholar: ~7,500 citations]

Fricker, E. (1994). Against gullibility. In B. K. Matilal & A. Chakrabarti (Eds.), *Knowing from words* (pp. 125–161). Kluwer. [Google Scholar: ~800 citations]

Fricker, M. (2007). *Epistemic injustice: Power and the ethics of knowing*. Oxford University Press. [Google Scholar: ~6,500 citations]

Grice, H. P. (1975). Logic and conversation. In P. Cole & J. L. Morgan (Eds.), *Syntax and semantics: Vol. 3. Speech acts* (pp. 41–58). Academic Press. [Google Scholar: ~30,000 citations]

Grice, H. P. (1989). *Studies in the way of words*. Harvard University Press. [Google Scholar: ~12,000 citations]

Gururangan, S., Marasović, A., Swayamdipta, S., Lo, K., Beltagy, I., Downey, D., & Smith, N. A. (2020). Don't stop pretraining: Adapt language models to domains and tasks. *Proceedings of ACL 2020*, 8342–8360. [Google Scholar: ~2,500 citations]

Harnad, S. (1990). The symbol grounding problem. *Physica D*, 42(1–3), 335–346. https://doi.org/10.1016/0167-2789(90)90087-6 [Google Scholar: ~5,000 citations]

Hume, D. (2000). *An enquiry concerning human understanding* (T. L. Beauchamp, Ed.). Oxford University Press. (Original work published 1748) [Google Scholar: ~15,000 citations, various editions]

Hupkes, D., Dankers, V., Mul, M., & Bruni, E. (2020). Compositionality decomposed: How do neural networks generalise? *Journal of Artificial Intelligence Research*, 67, 757–795. [Google Scholar: ~400 citations]

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., ... & Kaplan, J. (2022). Language models (mostly) know what they know. *arXiv preprint arXiv:2207.05221*. [Google Scholar: ~500 citations]

Kitcher, P. (1993). *The advancement of science: Science without legend, objectivity without illusions*. Oxford University Press. [Google Scholar: ~2,000 citations]

Kitcher, P. (2001). *Science, truth, and democracy*. Oxford University Press. [Google Scholar: ~1,200 citations]

Lackey, J. (2006). Learning from words. *Philosophy and Phenomenological Research*, 73(1), 77–101. [Google Scholar: ~400 citations]

Lackey, J. (2008). *Learning from words: Testimony as a source of knowledge*. Oxford University Press. [Google Scholar: ~1,500 citations]

Lake, B. M., & Baroni, M. (2018). Generalization without systematicity: On the compositional skills of sequence-to-sequence recurrent networks. *Proceedings of ICML 2018*, 2873–2882. [Google Scholar: ~1,500 citations]

Latour, B. (1987). *Science in action: How to follow scientists and engineers through society*. Harvard University Press. [Google Scholar: ~15,000 citations]

Latour, B. (2017). *Facing Gaia: Eight lectures on the new climatic regime*. Polity Press. [Google Scholar: ~1,500 citations]

Latour, B., & Woolgar, S. (1979). *Laboratory life: The social construction of scientific facts*. Sage. [Google Scholar: ~12,000 citations]

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474. [Google Scholar: ~4,000 citations]

Li, K., Patel, O., Viégas, F., Pfister, H., & Wattenberg, M. (2023). Inference-time intervention: Eliciting truthful answers from a language model. *Advances in Neural Information Processing Systems*, 36. [Google Scholar: ~200 citations]

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., ... & Koreeda, Y. (2023). Holistic evaluation of language models. *Annals of the New York Academy of Sciences*, 1525(1), 140–146. [Google Scholar: ~1,200 citations]

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *Proceedings of ACL 2022*, 3214–3252. [Google Scholar: ~1,000 citations]

Longino, H. E. (1990). *Science as social knowledge: Values and objectivity in scientific inquiry*. Princeton University Press. [Google Scholar: ~5,000 citations]

Longino, H. E. (2002). *The fate of knowledge*. Princeton University Press. [Google Scholar: ~2,000 citations]

McCarthy, J., & Hayes, P. J. (1969). Some philosophical problems from the standpoint of artificial intelligence. In B. Meltzer & D. Michie (Eds.), *Machine intelligence 4* (pp. 463–502). Edinburgh University Press. [Google Scholar: ~5,500 citations]

Mitchell, M. (1993). *Analogy-making as perception: A computer model*. MIT Press. [Google Scholar: ~500 citations]

Mitchell, M. (2019). *Artificial intelligence: A guide for thinking humans*. Farrar, Straus and Giroux. [Google Scholar: ~800 citations]

Mitchell, M. (2021). Why AI is harder than we think. *Proceedings of the Genetic and Evolutionary Computation Conference (GECCO '21)*, 3–3. [Google Scholar: ~400 citations]

Petroni, F., Rocktäschel, T., Riedel, S., Lewis, P., Bakhtin, A., Wu, Y., & Miller, A. (2019). Language models as knowledge bases? *Proceedings of EMNLP 2019*, 2463–2473. [Google Scholar: ~2,500 citations]

Pollock, J. L. (1986). *Contemporary theories of knowledge*. Rowman & Littlefield. [Google Scholar: ~1,500 citations]

Reid, T. (1997). *An inquiry into the human mind on the principles of common sense* (D. R. Brookes, Ed.). Pennsylvania State University Press. (Original work published 1764) [Google Scholar: ~3,000 citations, various editions]

Searle, J. R. (1969). *Speech acts: An essay in the philosophy of language*. Cambridge University Press. [Google Scholar: ~18,000 citations]

Searle, J. R. (1979). *Expression and meaning: Studies in the theory of speech acts*. Cambridge University Press. [Google Scholar: ~5,000 citations]

Searle, J. R. (1983). *Intentionality: An essay in the philosophy of mind*. Cambridge University Press. [Google Scholar: ~7,000 citations]

Shanahan, M. (1997). *Solving the frame problem: A mathematical investigation of the common sense law of inertia*. MIT Press. [Google Scholar: ~800 citations]

Shapin, S. (1994). *A social history of truth: Civility and science in seventeenth-century England*. University of Chicago Press. [Google Scholar: ~3,500 citations]

---

*Panel Response completed February 8, 2026*
