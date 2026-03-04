# §177. The Argumentation System — Walton Schemes, Citation Structure, and Debate Resolution

**Date**: 2026-03-04

---

## §177.1 Why Epistemic Flat Maps Must Become Structured Debates

A knowledge system that stores beliefs and their credences but does not model the arguments for and against them is epistemically impoverished. It resembles a map that marks terrain elevations but ignores the routes by which one might travel between peaks and valleys. ATLAS must do more than accumulate beliefs; it must represent the structure of scientific disagreement itself.

Science advances through debate, not through passive data accumulation. Kuhn's (1962) account of paradigm shifts makes this clear: scientific progress is not a smooth accumulation of facts but a punctuated series of crises in which competing frameworks clash. During a normal phase, scientists work within an established paradigm, solving puzzles within its conceptual structure. But when anomalies accumulate — when the paradigm cannot accommodate observations that matter — a crisis emerges. In the crisis phase, competing paradigms are explicitly pitted against each other. Scientists argue about which framework better explains the phenomena, which assumptions are defensible, which lines of evidence are trustworthy. The resolution of this debate is not a vote or a show of hands; it is a cognitive and social process in which the logical structure of the arguments determines which paradigm survives.

Lakatos (1978) refined Kuhn's account by arguing that scientific progress is the competition of research programmes, each with a hard core of foundational commitments and a protective belt of auxiliary hypotheses. Research programmes advance by generating novel predictions and explaining anomalies through modifications of the protective belt while preserving the core. But crucially, research programmes are compared by their argumentative strength: Which programme makes better use of its hard core? Which generates the most novel predictions? Which adapts most gracefully to anomalies? These are argumentative questions, not merely empirical ones.

ATLAS must model this argumentative structure because it is the mechanism by which credences should be updated. When a new finding challenges a belief in the system, the relevant question is not merely "Is this finding true?" but "Does this finding undermine the arguments that support the belief?" Does it attack a critical premise? Does it expose a gap in the warrant chain? Does it show that a critical question — a question that the argumentation scheme requires to be answered — has been left unaddressed?

Without an argumentation model, ATLAS would treat every belief as an isolated unit: credence ± evidence. With such a model, ATLAS can see that beliefs are embedded in networks of mutual support and attack. A finding that challenges belief A may also indirectly support belief B if B's arguments depend on assumptions that the finding calls into question. More importantly, ATLAS can identify where scientific consensus fails and where productive disagreement persists. These are precisely the points where future investigation is most valuable.

---

## §177.2 The ArgumentationGraph: Citation Relationships as Typed Edges

The ArgumentationGraph service represents the scholarly argumentation structure as a directed multigraph in which nodes are papers and edges are citation relationships enriched with polarity information.

**Nodes** represent individual papers in the extraction corpus. Each node carries:
- **Bibliographic metadata**: DOI, title, publication year, authors
- **Theoretical scaffolding**: List of theories referenced (e.g., "coherence", "foundationalism", "predictive processing")
- **Quantitative markers**: Number of claims extracted, citation count (if available from S2)
- **Temporal position**: Publication year and extraction date

The ArgumentationGraph operates in two modes. In base mode, without S2 enrichment, it uses publication years and shared theory references to infer temporal ordering and build the initial graph. In enriched mode, it overlays data from the Semantic Scholar citation API, gaining access to the full citation network and enabling more precise polarity detection.

**Edges** represent directed citation relationships between papers. Each edge is typed and scored:
- **Edge types**: cites | supports | challenges | extends | supersedes
- **Polarity**: A continuous value from −1.0 (directly contradicts) through 0.0 (neutral or unknown) to +1.0 (strongly supports)
- **Confidence**: A reliability score (0.0–1.0) indicating how certain the system is in the polarity assignment
- **Evidence**: A brief textual explanation of the polarity (e.g., "Strong theory alignment: coherence, foundationalism" or "Temporal ordering: 5 years apart")

Polarity is inferred through multiple channels. When two papers reference the same theoretical framework, the system assumes they are in dialogue about that framework. If paper A proposes an hypothesis about framework X and paper B (published later) also addresses framework X, the system infers that B's work either builds upon or responds to A's. The direction of the response — whether B supports, challenges, or extends A — is estimated through theory alignment and temporal proximity. Papers with high theory overlap and small publication gaps are likely to be in supporting or extending relationships; papers with low overlap or conflicting theoretical stances are candidates for challenge relationships.

With S2 enrichment, polarity becomes higher-confidence. The system can examine the actual citation context: does B cite A approvingly (citing it as a foundation or motivation) or critically (citing it as work to be corrected or transcended)? It can also apply sophisticated heuristics: a newer paper with substantially more citations than an older paper in the same domain likely represents a more influential or comprehensive treatment, suggesting a supersession relationship.

**Debate clusters** are detected through community analysis. In enriched mode, co-citation networks reveal groups of papers that mutually cite each other, indicating they are in active conversation. In base mode, papers sharing two or more theoretical frameworks are clustered together as likely communities of research. Each cluster is annotated with a contestation level (0.0 for consensus, 1.0 for highly contested) computed from the variance in polarities within the cluster. A cluster where all papers are positive about each other represents settled research; a cluster with high polarity variance represents an active debate.

---

## §177.3 Walton's Argumentation Schemes: The Grammar of Scientific Reasoning

Douglas Walton (1996) identified a set of argumentation schemes—stereotypical patterns of reasoning that underlie defeasible inference. A scheme is a template: it says "If you have premises of this form and these critical questions are satisfied, then you are licensed to draw this conclusion." The license is defeasible: new information can undermine it. But until that happens, the scheme provides a legitimate basis for belief.

ATLAS implements five operationally central schemes: argument from expert opinion, argument from sign, argument from cause to effect, argument from analogy, and argument from correlation to cause. Each scheme structures how evidence transfers its evidential force to a conclusion.

**Argument from expert opinion**: The inference is "Expert E says P; therefore P is true (or probable)." This scheme licenses reliance on authority when direct investigation is infeasible. Its critical questions are: (1) Is E a genuine expert in the domain? (2) Is E's opinion consistent with the expert consensus? (3) Has E been selected in an unbiased way, or was E cherry-picked? (4) Does E have a conflict of interest? An unaddressed critical question marks a vulnerability. If question (2) is not addressed — if we do not know whether E agrees with other experts — then the argument from expert opinion rests on a gap.

**Argument from sign**: The inference is "P is a sign of Q; we observe P; therefore Q is true." Disease symptoms illustrate this scheme: fever is a sign of infection, so observing fever licenses inferring infection. The critical questions are: (1) Is P actually a reliable sign of Q? (2) Are there alternative explanations for P that do not involve Q? (3) Is the sign unambiguous, or could it point to multiple conclusions? Failure to address these leaves the argument vulnerable. A fever could be caused by many conditions; if the argument from sign ignores this, it rests on unexamined ground.

**Argument from cause to effect**: The inference is "C causes E; C is true; therefore E will occur." This scheme licenses causal prediction. Its critical questions are: (1) Does C actually cause E, or is the relationship merely correlational? (2) Are there countervailing causes that might prevent E despite C? (3) What is the strength and frequency of the causal relationship? (4) Are there necessary conditions for C to produce E that might not be satisfied? A climate model might argue "Increased CO₂ causes warming; CO₂ is increasing; therefore warming will continue." But if the argument does not address whether cooling feedback mechanisms might offset the effect, it leaves a critical question unaddressed.

**Argument from analogy**: The inference is "A and B share features X, Y, Z; A has property P; therefore B probably has property P." This scheme is powerful in early-stage science when mechanisms are unknown. Its critical questions are: (1) Are X, Y, Z genuinely relevant to P? (2) Are there dissimilarities between A and B that defeat the analogy? (3) How many similar cases support the conclusion, and how many disconfirm it? (4) Is there a more specific, mechanistic understanding available that would replace the analogy? When a researcher argues "Attention restoration works in physical nature because it does in urban parks, by analogy to other restoration phenomena," an unaddressed critical question about what makes nature relevantly similar to parks is a gap.

**Argument from correlation to cause**: The inference is "X and Y are correlated; therefore X causes Y." This is one of the most treacherous schemes in empirical reasoning. Its critical questions are: (1) Could Y cause X instead (reverse causation)? (2) Could a third variable Z cause both X and Y (common cause)? (3) Is the correlation spurious? (4) If X and Y are genuinely related, does the relationship involve causation at all, or just association? Every observational study that finds a correlation leaves these critical questions in play until a mechanistic argument or experimental intervention addresses them.

When ATLAS extracts a claim from a paper, it identifies the argumentation scheme used to support that claim. It also identifies which critical questions the paper addresses and which remain open. An unaddressed critical question becomes a research gap: a place where future investigation would most efficiently resolve scientific uncertainty.

---

## §177.4 Toulmin Structure: The Microarchitecture of Warrants

Alongside Walton's schemes, ATLAS uses Toulmin's (1958) model of argument structure. Where Walton describes how inferences are licensed, Toulmin describes the components that must be present for a license to be legitimate.

Toulmin's classical structure has six parts:

- **Data (D)**: The factual ground on which the argument rests. "This paper reports a correlation between biophilia exposure and cortisol reduction."
- **Warrant (W)**: The bridge from data to claim. "Cortisol reduction is a valid marker of physiological stress reduction."
- **Backing (B)**: The evidence for the warrant. "Decades of neuroendocrinology research link cortisol levels to stress response (e.g., Sapolsky 2004)."
- **Claim (C)**: The conclusion the argument seeks to establish. "Biophilia exposure reduces stress."
- **Qualifier (Q)**: A modal operator expressing the strength of the claim. "Probably." "In most cases." "Provisional evidence suggests."
- **Rebuttal (R)**: Conditions under which the claim would fail. "Unless the biophilia exposure is very brief, or the subject is in acute distress."

ATLAS stores each claim with its Toulmin structure. This is not mere annotation; it is the foundation of the system's competition resolution algorithm (§129.3). When two papers make competing claims, the system can compare them structurally: Which claim has stronger backing? Which warrant is more fundamental or better-established? Which qualifier is more defensible?

Moreover, unaddressed components constitute research gaps. If a claim lacks explicit backing for its warrant, the system marks that as a gap: "Find experimental evidence for the link between cortisol reduction and stress recovery." If a claim's rebuttal conditions are not specified, that is a gap: "Under what environmental or physiological conditions does biophilia exposure fail to reduce stress?"

The combination of Walton and Toulmin creates a two-level architecture. Walton identifies the type of reasoning (expert opinion, cause to effect, etc.). Toulmin specifies what components must be present for that reasoning to be sound. Walton's critical questions are often questions about Toulmin components: "Is the warrant actually true?" "Is the backing adequate?" "Are the rebuttal conditions properly identified?"

---

## §177.5 From Unaddressed Questions to Research Gaps

The epistemic value of the argumentation system is realized through the gap discovery pipeline. When ATLAS processes a claim:

1. It identifies the argumentation scheme used.
2. It extracts the critical questions associated with that scheme.
3. It checks whether the source paper addresses each critical question.
4. For unaddressed critical questions, it generates research gaps.

Consider the argument from expert opinion scheme applied to a claim like "Attention restoration is a real phenomenon according to Kaplan & Kaplan (1989)." The scheme's critical questions include: "Is Kaplan an expert?" (yes, clearly, given citation counts and domain prominence) and "Is Kaplan's view consistent with expert consensus?" (this requires investigation).

If the source paper does not cite other experts or compare Kaplan's views to competing positions, then critical question (2) is unaddressed. ATLAS generates a gap: **Type: CRITICAL_QUESTION. Origin: argument from expert opinion. Gap: "Is Kaplan's view of attention restoration consistent with other leading researchers in environmental psychology?"**

This gap then feeds into the Interpretation Space (§176). The system computes how many beliefs depend on the consistency of Kaplan's view with expert consensus. If many downstream beliefs rest on this foundation, the gap becomes high-priority. The VOI system assigns research value accordingly: gathering evidence about expert disagreement (or consensus) would efficiently resolve uncertainty about multiple dependent beliefs.

Unaddressed critical questions are not mere absences. They are structural vulnerabilities. If argument A uses the "argument from expert opinion" scheme but leaves the "expert consensus" critical question unaddressed, then any finding about expert disagreement would undermine A. The argumentation system flags this relationship explicitly, enabling both the system and human users to see where attack is most likely to succeed.

This becomes especially powerful when debates involve multiple schemes. Paper X argues "Biophilia reduces stress by analogy to other restoration phenomena" (argument from analogy). Paper Y argues "The mechanism involves fractals, as shown by information theory" (argument from cause to effect). Paper Z argues "No mechanism is needed; the correlation is enough" (implicit argument from sign or correlation to cause). Each paper uses a different scheme, and each scheme leaves different critical questions in play. The argumentation graph surfaces these differences. It shows not just that the papers disagree, but *how* they disagree: which critical questions each is answering and which each is leaving open.

---

## §177.6 Formal Argumentation versus Informal Debate Tracking

An alternative design would be to store scientific debates as informal narrative summaries: "Kaplan argues that attention restoration is a distinct mechanism. Response 1 (Ulrich) argues that the mechanism is evolutionary preference. Response 2 (Joye & van den Berg) argue for ecological perspective including aesthetic values." This approach has merit for human readability. It preserves nuance and allows for detailed historiography.

But ATLAS uses formal argumentation for three reasons.

**First, computational tractability**: Formal schemes are decidable. Given a paper and an argument from expert opinion scheme, the system can ask: "Is expert status documented?" (computable via citation analysis), "Are competing expert views cited?" (computable via content extraction). With informal narratives, these questions require human judgment each time. Formal structure allows the system to apply the same analysis consistently across thousands of claims.

**Second, rational reconstruction of strength**: Which arguments are strongest? This is not a question that informal debate summaries can easily answer. But in a formal argumentation framework (Dung, 1995), strength is defined: an argument is acceptable if all attacks against it are themselves acceptable attacks. Recursive application of this definition yields a grounded extension: the set of arguments that are collectively acceptable. ATLAS does not use Dung's framework directly (Dung is designed for abstract arguments with binary attack relations; ATLAS needs richer structure), but it borrows the core insight: formal argumentation enables computational strength analysis.

**Third, gap discovery as feedback**: The research gaps discovered through unaddressed critical questions are only possible because the system understands the formal structure. An informal debate summary might note that "some researchers question expert consensus" but would never generate the specific gap "Find whether Kaplan's attention restoration theory is consistent with evolutionary psychology accounts of restoration." The formal argumentation system generates this gap automatically, with high precision, because it understands the critical questions inherent in the expert opinion scheme.

The cost of formalization is loss of nuance. Some debates cannot be cleanly classified into Walton schemes. Some expert disagreement is substantive and productive, not a "critical question to be resolved" but rather a genuine plurality of legitimate positions. ATLAS addresses this through explicit representation of competing complete arguments: if three schools of thought exist, each is modeled as a separate argument (perhaps using different schemes), and the system represents their competition without forcing one to "win." The argumentation graph can show multiple polarities pointing in different directions, representing genuine scholarly disagreement.

But the gain in tractability and gap discovery justifies the cost. Science progresses not by eliminating disagreement but by making disagreement precise, testable, and resolvable. Formal argumentation is the mechanism by which ATLAS enables that precision.

---

## §177.7 Connection to Web of Belief and Interpretation Space

The ArgumentationGraph is not an isolated component. It integrates with three other systems:

**Web of Belief (§140)**: Every belief in the epistemic network carries not only a credence and warrant type but also a location in the argumentation graph. When updating a belief's credence in light of new evidence, the system consults the argumentation graph. A finding that addresses an unaddressed critical question in an argument supporting the belief has greater impact than a finding that merely adds to a large literature. A finding that undermines a premise of an argument attacking the belief strengthens rather than weakens credence.

**Interpretation Space (§176)**: The research gaps discovered through critical question analysis populate the Interpretation Space's gap inventory. Gaps of type CRITICAL_QUESTION appear in the Res(W, R₁) residual (argumentation closure residual). The Coherence_Tension metric explicitly computes unresolved argumentation attacks: papers with mutually contradictory claims and unaddressed counter-arguments sit at high tension points. These tension points become interpretation space peaks—places where new evidence would have maximal epistemic value.

**QA System (§189)**: When users ask questions about contested claims, the system draws on the ArgumentationGraph to provide balanced responses. Rather than reporting "The literature says P with credence 0.65," the system can say "There are two main arguments for P: Argument A (from expert opinion, based on Kaplan's work) and Argument B (from mechanism, based on information-theoretic fractal analysis). Argument A leaves the expert consensus critical question unaddressed. Argument B's mechanism requires validation in controlled settings. Here are the key disagreements..."

---

## §177.8 Design Implications: Moving from Static Belief Maps to Dynamic Argumentation

The ArgumentationGraph reflects a philosophical commitment: that knowledge is not a set of independently verified facts but a web of interdependent arguments. Accepting one argument commits you to answering its critical questions. Accepting multiple arguments with different schemes commits you to explaining their potential conflicts. This is the Quinean picture (§130): beliefs are held in a web, and the web's stability is the relevant epistemological unit.

The argumentation system makes this web visible and computable. ATLAS moves from a static belief map—beliefs with credences—to a dynamic argumentation landscape where the system can see:

- Which debates are actively contested (high-polarity variance within clusters)
- Which arguments are strongest (defended against attacks, critical questions answered)
- Where future investigation would have highest impact (unaddressed critical questions)
- How new evidence changes not just one belief but the web of arguments on which it rests

This is the foundation for intelligent, evidence-responsive, transparent science. A system that models debate structure can advise researchers not just "What is the best current belief?" but "What evidence would most efficiently resolve the current disagreement?" and "Where does the scientific consensus most genuinely apply, and where is productive disagreement still occurring?"

---

## References

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, *77*(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X

Kuhn, T. S. (1962). *The structure of scientific revolutions*. University of Chicago Press.

Lakatos, I. (1978). *The methodology of scientific research programmes*. Cambridge University Press.

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

Walton, D. N. (1996). *Argumentation schemes for presumptive reasoning*. Lawrence Erlbaum Associates.
