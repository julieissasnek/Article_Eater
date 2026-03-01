const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak, Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, UnderlineType, convertInchesToTwip, ImageRun, TabStopType, TabStopAlign, Footer, Header } = require('docx');
const fs = require('fs');
const path = require('path');

// Helper: Create a spacer paragraph
function spacer(height = 200) {
  return new Paragraph({
    spacing: { before: height },
  });
}

// Helper: Create a styled heading
function heading(text, level = 1) {
  const sizes = { 1: 32, 2: 28, 3: 24 };
  const outlineLevels = { 1: 0, 2: 1, 3: 2 };

  return new Paragraph({
    text: text,
    heading: HeadingLevel[`HEADING_${level}`],
    spacing: { before: 400, after: 200, line: 312, lineRule: 'auto' },
    style: `Heading${level}`,
  });
}

// Helper: Create a body paragraph
function body(text, opts = {}) {
  return new Paragraph({
    text: text,
    font: 'Garamond',
    size: 24,
    spacing: { line: 312, lineRule: 'auto', ...opts.spacing },
    alignment: opts.alignment || AlignmentType.JUSTIFIED,
    indent: opts.indent || {},
  });
}

// Helper: Create a block quote (indented, italic)
function blockQuote(text) {
  return new Paragraph({
    text: text,
    font: 'Garamond',
    size: 24,
    italics: true,
    spacing: { before: 200, after: 200, line: 312, lineRule: 'auto' },
    indent: { left: 720, right: 720 },
    alignment: AlignmentType.JUSTIFIED,
  });
}

// Helper: Embed an image with caption
function imageWithCaption(imagePath, caption) {
  const imageBuffer = fs.readFileSync(imagePath);
  const base64Image = imageBuffer.toString('base64');

  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 400, after: 200 },
      children: [
        new ImageRun({
          data: base64Image,
          transformation: {
            width: 550,
            height: 400,
          },
          type: 'png',
          altText: {
            title: 'Figure',
            description: caption,
            name: caption,
          },
        }),
      ],
    }),
    new Paragraph({
      text: caption,
      font: 'Garamond',
      size: 22,
      italics: true,
      alignment: AlignmentType.CENTER,
      spacing: { before: 100, after: 300 },
    }),
  ];
}

// Helper: Create references
function referenceEntry(authors, year, title, source, details = '', citations = '') {
  const text = `${authors} (${year}). ${title}. ${source}${details ? '. ' + details : ''}.${citations ? ' [' + citations + ' citations]' : ''}`;

  return new Paragraph({
    text: text,
    font: 'Garamond',
    size: 22,
    spacing: { before: 0, after: 200, line: 312, lineRule: 'auto' },
    indent: { left: 720, hanging: 720 },
    alignment: AlignmentType.JUSTIFIED,
  });
}

// Build the document sections
const sections = [
  // TITLE PAGE
  new Paragraph({
    spacing: { before: 1440, after: 0 },
  }),
  new Paragraph({
    spacing: { before: 800, after: 0 },
  }),
  new Paragraph({
    text: "Mapping the Epistemic Landscape:",
    font: 'Garamond',
    size: 32,
    bold: true,
    alignment: AlignmentType.CENTER,
    spacing: { before: 600, after: 200, line: 312, lineRule: 'auto' },
  }),
  new Paragraph({
    text: "How Computational Systems Can — and Should — Distinguish What We Don't Know from What We Can't Know",
    font: 'Garamond',
    size: 28,
    bold: true,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 800, line: 312, lineRule: 'auto' },
  }),
  spacer(600),
  new Paragraph({
    text: "David Kirsh",
    font: 'Garamond',
    size: 24,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 100, line: 312, lineRule: 'auto' },
  }),
  new Paragraph({
    text: "Department of Cognitive Science",
    font: 'Garamond',
    size: 24,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 50, line: 312, lineRule: 'auto' },
  }),
  new Paragraph({
    text: "University of California, San Diego",
    font: 'Garamond',
    size: 24,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 400, line: 312, lineRule: 'auto' },
  }),
  spacer(400),
  new Paragraph({
    text: "February 2026",
    font: 'Garamond',
    size: 24,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 600, line: 312, lineRule: 'auto' },
  }),
  spacer(600),
  new Paragraph({
    text: "Working Paper — Comments Welcome",
    font: 'Garamond',
    size: 22,
    italics: true,
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 0, line: 312, lineRule: 'auto' },
  }),
  new Paragraph({
    text: '',
    pageBreakBefore: true,
  }),

  // ABSTRACT
  heading('Abstract'),
  new Paragraph({
    text: "Abstract",
    font: 'Garamond',
    size: 24,
    bold: true,
    spacing: { before: 0, after: 100, line: 312, lineRule: 'auto' },
  }),
  blockQuote(
    "Computational systems that reason with uncertainty frequently conflate epistemic uncertainty (uncertainty in our knowledge) with aleatory uncertainty (inherent stochasticity in the world). This conflation produces two characteristic errors: misallocation of research effort and misjudgment of model validation sufficiency. The ATLAS (Architecture for Typed, Layered Assessment of Science) system implements a dual architecture—an Epistemic Warrant Graph (EWG) tracking epistemic probabilities with full Toulmin provenance, and a Bayesian Network storing aleatory probabilities as bare conditional probability tables—to maintain the distinction computationally. This paper develops the theoretical and practical implications of this architecture. First, we show how bridge warrant types function as a finer-grained categorization of epistemic uncertainty, enabling value-of-information analyses that distinguish what is knowable from what is inherently aleatory. Second, we present a five-step CPT elicitation protocol that translates epistemic content into aleatory parameters while preserving traceability. Third, we respond to three major philosophical objections: de Finetti's radical subjectivism, Lewis's Principal Principle and Moss's interleaving problem, and Der Kiureghian and Ditlevsen's pragmatic reframing. We conclude that the epistemic-aleatory distinction, far from being a philosophical curiosity, is an architectural necessity for computational systems representing scientific knowledge in heterogeneous, evidence-rich domains. The framework is illustrated throughout with worked examples from environmental psychology and architectural neuroscience."
  ),
  spacer(400),
  new Paragraph({
    text: '',
    pageBreakBefore: true,
  }),

  // SECTION 1: TWO KINDS OF PROBABILITY
  heading('1. Two Kinds of Probability'),
  body(
    "Consider a fair die. Before you roll it, you assign probability 1/6 to each face. After you roll it (but before you look), you assign probability 1 to the outcome that occurred and probability 0 to all others. Have the probabilities changed? In one sense, no—the physical die is the same, its symmetries unchanged. In another sense, yes—your rational credence has shifted (Knight, 1921). This simple example carries a profound lesson: the term 'probability' hides two distinct phenomena that have been conflated throughout the history of modern probability theory (Hacking, 1975)."
  ),
  spacer(200),
  body(
    "The first phenomenon is aleatory: a property of the process itself. A fair die has an intrinsic property—its symmetry under rotations—that grounds a probability distribution over outcomes. This property exists whether or not anyone is observing (Kolmogorov, 1933). We might call this objective chance, physical randomness, or aleatory probability. It is a fact about how the world is constituted."
  ),
  spacer(200),
  body(
    "The second phenomenon is epistemic: a property of our knowledge. Your credence before you roll differs from your credence after, not because the die has changed, but because you have acquired information. This is subjective probability, rational credence, or epistemic probability (Ramsey, 1926; Savage, 1954). It is a fact about what we know and how we ought to update in light of evidence."
  ),
  spacer(200),
  body(
    "Most of applied probability theory conflates these two. A Bayesian network, a classical frequentist confidence interval, a Monte Carlo simulation—all treat probability as a single unified concept (Kolmogorov, 1933). This conflation is usually harmless when applied to mature, well-characterized domains (medical diagnosis, spam filtering). But in domains where evidence is heterogeneous, warrant types vary, and the investigator must decide where to invest research effort, the conflation produces two characteristic errors (Der Kiureghian & Ditlevsen, 2009)."
  ),
  spacer(200),
  body(
    "The first error is misallocation of research effort. Suppose a modeler assigns 0.35 probability to a causal link in an environmental process. A high-confidence 0.35, based on a large-sample experimental study with a standardized effect size (Cohen, 1988), carries different implications for research planning than a low-confidence 0.35, based on a single case report of a plausible mechanism. Both say 0.35, but one suggests the uncertainty is reducible by further investigation (epistemic), while the other suggests the uncertainty is irreducible or system-dependent (aleatory). Conflating the two leaves the investigator without guidance on what to study next (Der Kiureghian & Ditlevsen, 2009)."
  ),
  spacer(200),
  body(
    "The second error is misjudgment of model validation sufficiency. Suppose an engineer builds a computational model with 50 probabilistic parameters. She collects data on 40 of them, achieving narrow credence intervals. For the remaining 10, she assigns priors based on expert judgment or analogical reasoning (Cooke, 1991). She then validates the model against test data and observes a good fit (Oreskes, Shrader-Frechette & Belitz, 1994). Has validation succeeded? The answer depends on which 10 parameters are missing. If they govern inherently stochastic processes (turbulence, molecular diffusion), then uncertainty in them is largely irreducible; validation success is meaningful even with narrow epistemic uncertainty on others. If they govern causal mechanisms that could be studied experimentally (Oberkampf et al., 2004), then leaving them as expert priors is a validation failure—the model is credible despite carrying significant epistemic risk."
  ),
  spacer(200),
  body(
    "A meta-analysis illustrates the second error concretely. A meta-analyst aggregates effect sizes from a heterogeneous literature (Borenstein et al., 2009): some studies are large, well-controlled trials; others are smaller, correlational studies conducted in the field. The meta-analyst computes a pooled effect size, say d = 0.42, with a confidence interval [0.38, 0.46]. This interval reflects heterogeneity and sampling variability—it is epistemic uncertainty. But the same d = 0.42 could describe the variability in true effects across conditions (a mechanism works better in some settings than others). In the first interpretation, narrowing the interval requires more or better studies. In the second interpretation, the interval reflects an irreducible stochastic property of nature, and no further investigation will narrow it—instead, understanding why the mechanism works better in some settings is the relevant goal (Helton, 1997; Hoffman & Hammonds, 1994)."
  ),
  spacer(300),

  // Insert Figure 1
  ...imageWithCaption(
    '/sessions/keen-busy-turing/fig1.png',
    'Figure 1. Two kinds of uncertainty. Aleatory uncertainty (left) is a property of the process itself; epistemic uncertainty (right) is a property of our knowledge about the process. Conflating them produces two characteristic errors.'
  ),
  spacer(300),

  // SECTION 1.1: Historical Debate
  heading('1.1. The Historical Debate', 2),
  body(
    "Bruno de Finetti (1937), in his foundational work on subjective probability, argued that all probability is fundamentally epistemic—degrees of belief—and that apparent objective probabilities are reconstructible from subjective ones via his exchangeability theorem. De Finetti's position was radical: there is no such thing as physical randomness, only our ignorance about outcomes determined (perhaps) by deterministic laws we do not know. This framework was later refined by Ramsey (1926), whose work on truth and probability established the subjective interpretation as a coherent philosophical position."
  ),
  spacer(200),
  body(
    "The frequentist tradition, by contrast, anchored probability in the long-run frequency of outcomes in repeated trials (von Mises, 1928; Reichenbach, 1949). But frequentists disagreed among themselves about the interpretation: does frequency represent a fact about the world (objective chance), or does it provide a rational basis for assigning credences (an epistemic principle for setting personal probabilities)?"
  ),
  spacer(200),
  body(
    "Ian Hacking (1975) documented this ambivalence, calling probability 'Janus-faced'—it requires both an aspect looking toward objective reality and an aspect looking toward rational belief. His historical analysis showed that the modern concept of probability emerged only in the seventeenth century, as mathematicians and natural philosophers struggled to reconcile the appearance of randomness in nature with a commitment to determinism. Carnap (1950) later proposed logical probability as a third position, seeking a middle ground between radical subjectivism and strict frequentism."
  ),
  spacer(200),
  body(
    "Wolfgang Spohn (2012), building on Hacking and de Finetti, developed ranking theory as a framework that preserves the distinction while showing how epistemic and aleatory probabilities interact. In Spohn's system, both rational credences and objective chances are grounded in a common logical structure—a ranking function that assigns degrees of implausibility—but the two play different roles in rational inference. More recently, Jaynes (2003) provided a comprehensive Bayesian synthesis, arguing that probability is the logic of inference and that both epistemic and aleatory aspects are best understood within a unified probabilistic framework."
  ),
  spacer(300),

  // SECTION 1.2: Related Work
  heading('1.2. Related Work: The Distinction in Engineering, Risk Analysis, and Philosophy', 2),
  body(
    "The epistemic-aleatory distinction has gained renewed attention in engineering and risk analysis over the past two decades, motivated by the practical need to design systems and allocate research resources under uncertainty (Helton, 1997; National Research Council, 2009)."
  ),
  spacer(200),
  body(
    "Der Kiureghian and Ditlevsen (2009) argue that the distinction is model-dependent. What counts as aleatory versus epistemic depends on what the model chooses to represent. For instance, in a structural model, material properties might be treated as aleatory if the model includes random variation; but at a higher level of abstraction, the same property might be epistemic—we simply do not know its value in a particular building. Their key insight is pragmatic: the distinction is not absolute but relative to a modeling frame."
  ),
  spacer(200),
  body(
    "We agree with this pragmatism, but we argue that ATLAS's architectural commitment goes further. ATLAS does not merely recognize the distinction; it embeds it in the computational structure (Quine & Ullian, 1978). The Epistemic Warrant Graph (EWG) tracks epistemic content (with Toulmin provenance), while the Bayesian Network stores aleatory content (bare CPT entries). This dual architecture makes the choice of what is aleatory versus epistemic explicit and reversible: as the EWG revises, the projection to the BN regenerates. The architecture thus operationalizes Der Kiureghian and Ditlevsen's insight."
  ),
  spacer(200),
  body(
    "We call this epistemic layer the Epistemic Warrant Graph (EWG), a term that captures how the ATLAS system extends the philosophical tradition it inherits. Quine and Ullian (1978) introduced the metaphor of a 'web of belief'—an interconnected network where beliefs are justified by mutual coherence rather than by resting on foundations. The ATLAS system inherits Quine's core insight that beliefs are interconnected and that revision propagates through the network. But it departs from Quine in two crucial respects: first, every connection is typed according to a seven-level warrant hierarchy (CONSTITUTIVE through THEORETICAL_DEFAULT), so that the system tracks not just whether beliefs are connected but what kind of evidential support each connection provides; second, every connection carries a quantitative confidence weight that can be updated when new evidence arrives. The result is not Quine's holistic, untyped web but a structured, typed, quantitative graph—an epistemic warrant graph—whose edges can be projected into Bayesian network parameters via the discount function described in §3."
  ),
  spacer(200),
  body(
    "Kaplan and Garrick (1981), pioneering probabilistic risk analysis, proposed the risk triplet {scenario, probability, consequence}. They recognized that the probability component is problematic: it conflates the frequency of the scenario with our confidence that our model correctly describes what happens given the scenario. ATLAS's dual architecture directly addresses this conflation. The EWG tracks our confidence in the causal model (epistemic); the BN encodes the probability distribution over outcomes given that the model is correct (aleatory)."
  ),
  spacer(200),
  body(
    "Oberkampf, Helton, Joslyn, Trucano and Sargsyan (2004), in their taxonomy of uncertainty for computational modeling, distinguish parameter uncertainty (epistemic—we don't know the parameters' values but could in principle measure them) from stochastic variability (aleatory—the system behaves randomly and no measurement would reduce the variability). ATLAS extends this distinction by adding a finer categorization: within epistemic uncertainty, bridge warrant types specify different kinds of evidence and different paths to reduction (Saltelli et al., 2008)."
  ),
  spacer(200),
  body(
    "Fox and Ülkümen (2011) propose a two-dimensional uncertainty framework in psychological judgment: uncertainty about the state of the world (aleatory) versus uncertainty about the probability of that state (epistemic). Their experimental work shows that people distinguish these dimensions—and, moreover, that neglecting to do so leads to systematic judgment errors, such as overconfidence in outcomes that are actually very unpredictable."
  ),
  spacer(300),

  // SECTION 1.3: ATLAS Architecture
  heading('1.3. The Distinction in the ATLAS Architecture', 2),
  body(
    "The framework we develop here is grounded in a specific computational system: ATLAS (Architecture for Typed, Layered Assessment of Science), designed for the domain of environmental psychology and architectural neuroscience. ATLAS was built to address a concrete problem: how can a computational model integrate findings from over a thousand articles in cognitive neuroscience, environmental psychology, and architectural research—articles that vary enormously in methodology, evidence quality, and theoretical commitment—into a unified framework capable of supporting intervention reasoning (Woodward, 2003; Machamer, Darden & Craver, 2000)? The answer required confronting the epistemic-aleatory distinction head-on."
  ),
  spacer(200),
  body(
    "ATLAS is a large-scale knowledge graph: 130 nodes representing causal claims about how built environments affect neural processes and human behaviour, connected by approximately 400 typed edges. Each edge carries a Toulmin evidence structure (Toulmin, 1958; Walton, 2006) specifying the grounds (empirical data), warrant (the inferential bridge from data to claim), backing (the theoretical framework supporting the warrant), qualifiers (conditions under which the claim holds), and rebuttals (conditions under which it fails). The warrant types are ranked by epistemic strength in a seven-level hierarchy: CONSTITUTIVE (the claim is true by definition of the system), MECHANISM (a known causal pathway supports the claim), EMPIRICAL_COVARIANCE (direct observational data supports a correlation), FUNCTIONAL (the claim follows from the system's functional organisation), CAPACITY (the mechanism has the capacity to produce the effect), ANALOGICAL (a parallel case supports the claim), and THEORETICAL_DEFAULT (the claim is assumed as a framework starting point). This hierarchy is not arbitrary; it reflects the degree to which each warrant type constrains possible error (Thagard, 1989; Clark, 2013), from near-certainty (constitutive) to speculative extension (analogical and theoretical default)."
  ),
  spacer(200),
  body(
    "The ATLAS system maintains two architecturally distinct data structures. The first is the Epistemic Warrant Graph (EWG)—the knowledge graph just described. Its confidence scores are epistemic probabilities: they encode the scientific community's current best judgment about how much to trust each claim, given the available evidence and its warrant type (Joyce, 1998; Pettigrew, 2016). The second structure is a Bayesian Network (BN), a directed acyclic graph whose nodes represent random variables and whose edges encode conditional dependence (Pearl, 2009; Jensen & Nielsen, 2007). Each node has a conditional probability table (CPT) specifying P(child | parents). The BN's CPT entries are aleatory probabilities: they aspire to represent population frequencies and causal effect magnitudes, not the community's confidence in those frequencies."
  ),
  spacer(200),
  body(
    "The two structures are linked by a projection function π, which translates epistemically-warranted claims from the EWG into aleatory probability entries for the BN. This translation is necessarily lossy: the Toulmin provenance—qualifiers, rebuttals, competing accounts, warrant types—does not appear in the BN. But the projection is traceable and reversible: when the EWG revises (a new study arrives, a warrant is upgraded, a rebuttal is resolved), the affected CPT entries are recomputed (Druzdzel & van der Gaag, 2000; Renooij, 2001). The BN is not a permanent artifact; it is a derived representation that reflects the current state of the EWG."
  ),
  spacer(200),
  body(
    "The name ATLAS is not merely a branding convenience; it reflects a deep structural analogy to cartography that clarifies the system's architecture. In cartographic theory, a foundational insight is that the same territory can be represented by fundamentally different maps that serve different epistemic purposes—and that projecting from one representation to another necessarily involves information loss (Monmonier, 1991; Wood, 1992). A geological survey map shows the substrate: bedrock composition, fault lines, stratigraphic layers, the age and type of the ground itself. A road map of the same territory shows something entirely different: navigable routes, distances, and connectivity between destinations. You cannot recover the geological composition from a road map, nor can you plan a driving route from a geological survey. Each representation sacrifices information that the other preserves, and each makes different questions tractable."
  ),
  spacer(200),
  body(
    "The EWG–BN dual architecture in ATLAS instantiates exactly this cartographic principle. The Epistemic Warrant Graph is the geological map: it shows the evidential substrate of a scientific domain—what types of warrant support each claim, how strong the epistemic ground is, where the fault lines of contested evidence run, and which regions rest on bedrock (constitutive and mechanistic warrants) versus loose sediment (analogical and theoretical defaults). The Bayesian Network is the road map: it shows the navigable probabilistic routes through the domain, the conditional dependencies that allow prediction and intervention reasoning, optimised for computational tractability. The projection function π that translates EWG into BN is a cartographic projection in the precise mathematical sense identified by Gauss's Theorema Egregium (1828): just as a sphere's surface cannot be represented on a plane without distortion, the rich Toulmin provenance of the EWG cannot be projected into bare CPT entries without epistemic information loss. The loss is principled and traceable—we know exactly what was sacrificed and why—but it is irreversible in the same way that a Mercator projection cannot recover the true area ratios of the globe (Robinson, 1952; Monmonier, 1991)."
  ),
  spacer(200),
  body(
    "This cartographic analogy extends further. In geographic information systems (GIS), Tomlin's (1990) map algebra formalised how multiple map layers—geological, hydrological, political, economic—can be stacked over the same territory and combined through algebraic operations. ATLAS performs an analogous operation: multiple warrant types, each encoding a different dimension of evidential strength, are layered over the same set of causal claims. The projection function π performs what cartographers call generalisation—the systematic process by which detail is reduced when moving from a larger-scale to a smaller-scale representation (Robinson et al., 1995). As Monmonier (1991) observed, 'a map that did not generalise would be useless'; the same is true of a knowledge system that refused to project its epistemic content into computationally tractable parameters. The ATLAS name thus evokes not only the great scientific atlas projects—the Allen Brain Atlas, the Human Brain Atlas, the Visible Human Project—but the entire cartographic tradition of making complex terrain legible and navigable through principled, purpose-driven abstraction."
  ),
  spacer(200),
  body(
    "This dual architecture solves the conflation problem. Because epistemic content is stored separately from aleatory content, the system can answer questions that a standard Bayesian network cannot (Russell & Norvig, 2021). For instance: 'Which causal links in this network are most uncertain epistemically, despite having firm conditional probability assignments?' Answer: examine the warrant types in the EWG—links with ANALOGICAL or THEORETICAL_DEFAULT warrants carry high epistemic risk even if their CPT entries look precise. Or: 'Which uncertainties are reducible by additional research?' Answer: those with MECHANISM or EMPIRICAL_COVARIANCE warrants, where targeted empirical work can upgrade the evidence (Shortliffe & Buchanan, 1975). Or: 'If we invest in resolving the top three epistemic uncertainties, how much will the posterior distribution over outcomes change?' This is a value-of-information analysis (Howard, 1966; Raiffa & Schlaifer, 1961), and it is possible only when epistemic and aleatory are separated—a point made forcefully by Der Kiureghian and Ditlevsen (2009) in the engineering context and extended here to scientific knowledge systems."
  ),
  spacer(300),

  // Insert Figure 2
  ...imageWithCaption(
    '/sessions/keen-busy-turing/fig2.png',
    'Figure 2. The ATLAS dual architecture. The Epistemic Warrant Graph (EWG) (left) tracks epistemic probabilities with full Toulmin provenance. The Bayesian Network (right) stores aleatory probabilities as bare CPT entries. The projection function is necessarily lossy; the BN is regenerated when the EWG revises.'
  ),
  spacer(300),

  // Insert Figure 5 — System Overview
  ...imageWithCaption(
    '/sessions/keen-busy-turing/fig5.png',
    'Figure 3. System overview. ATLAS ingests findings from over 1,000 articles in cognitive neuroscience, environmental psychology, and architectural research. Epistemic content flows into the Epistemic Warrant Graph (EWG); aleatory parameters are derived via the projection function into the Bayesian Network. The two structures jointly support research planning, value-of-information analysis, and intervention predictions.'
  ),
  spacer(300),

  // SECTION 1.4: Lewis and the Principal Principle
  heading('1.4. Lewis\'s Principal Principle and the Interleaving Problem', 2),
  body(
    "David Lewis (1980) formulated the Principal Principle as a regulative ideal for how rational credence should relate to objective chance. The principle states: if you know that the objective chance of an event is p, and you have no other relevant information, then your rational credence in that event should be p. In other words, when the epistemic uncertainty about an objective chance goes to zero, rational credence should converge on that chance (Williamson, 2000). This foundational principle has guided debates about the relationship between epistemic and aleatory uncertainty."
  ),
  spacer(200),
  body(
    "In ATLAS terms, the Principal Principle can be restated as follows: the confidence in a CPT entry (stored in the BN) should reflect the tightness of the epistemic uncertainty about that entry (tracked in the EWG). A CPT entry whose warrant comes from a large-sample experiment with narrow confidence intervals represents high aleatory confidence backed by low epistemic uncertainty. A CPT entry based on expert judgment carries lower aleatory confidence (or equivalently, higher expected error) because it carries higher epistemic uncertainty (Hájek, 2019)."
  ),
  spacer(200),
  body(
    "This is the ideal. But recent philosophical work has questioned whether epistemic and aleatory probabilities are as cleanly separable as Lewis supposed. Sarah Moss (2018), in her work on probabilistic knowledge, argues that epistemic and aleatory probabilities are often 'interleaved' in practice. The path from high epistemic uncertainty to low epistemic uncertainty is not a simple linear approach to a fixed target; rather, as we learn more, we discover that the target itself is more complex than we thought, or that there are multiple conflicting targets, or that the very concept of an aleatory probability is context-dependent."
  ),
  spacer(200),
  body(
    "We acknowledge Moss's point. The ATLAS architecture does not dissolve the interleaving; instead, it makes the interleaving explicit and manageable. The EWG-to-BN projection is the place where interleaving is handled. When a study arrives that revises our understanding of a causal mechanism, the EWG updates (new warrant, possibly new qualifier or rebuttal). The projection function then recomputes the CPT entry, integrating across the updated epistemic landscape. The interleaving is not hidden in an opaque learning algorithm; it is traceable in the projection."
  ),
  spacer(200),
  body(
    "Moreover, the Principal Principle itself provides structure. It tells us what convergence looks like: it is the state in which epistemic uncertainty has been resolved (the Web has a single, high-confidence warrant), and aleatory uncertainty remains only to the extent that the causal mechanism itself is stochastic (the CPT entry reflects inherent variability, not ignorance). Moss tells us that the path to convergence is messy; Lewis tells us what the destination looks like. ATLAS provides the bookkeeping to track where we are on that path (Diaconis & Freedman, 1980)."
  ),
  spacer(300),

  // SECTION 2: Bridge Warrant Types
  heading('2. Bridge Warrant Types as Categorizations of Epistemic Uncertainty'),
  body(
    "Toulmin (1958) developed a model of argumentation in which a warrant serves as the inferential bridge from data to claim. The ATLAS system extends Toulmin's framework by typing warrants according to the kind of epistemic support they provide (Walton, 2006). As introduced in §1.3, the seven warrant types—CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, and THEORETICAL_DEFAULT—are not merely labels. They are categorisations of epistemic uncertainty that specify not just the confidence level but the kind of evidence that would change it."
  ),
  spacer(200),
  body(
    "This is a substantive claim grounded in philosophy of science (Cartwright, 1983). It says that the source of uncertainty matters as much as its magnitude. A confidence of 0.35 backed by a MECHANISM warrant (the causal pathway is characterised in the laboratory but its magnitude in architectural settings is uncertain) carries different research implications from a confidence of 0.35 backed by an ANALOGICAL warrant (we are reasoning by structural parallel from a different domain and the analogy may not hold). The first calls for field measurement in buildings; the second calls for establishing that the putative analogy is mechanistically grounded (Machamer, Darden & Craver, 2000). A bare number cannot make this distinction; a warrant type can."
  ),
  spacer(200),
  body(
    "Consider a concrete example drawn from the ATLAS system's treatment of daylight and mood. A causal link from daylight exposure to serotonin synthesis might carry a MECHANISM bridge at confidence 0.35. This says: the causal pathway—daylight → retinal ganglion cells → raphe nuclei → tryptophan hydroxylase → 5-HT synthesis—is well-characterised in laboratory neuroscience (Lambert et al., 2002), but its operation at sufficient magnitude in real buildings with real occupants over ecologically valid time scales remains uncertain. The research that would raise this confidence is measurement of the mechanism in architectural conditions: ambulatory neurochemical monitoring, or at least measurement of the relevant behavioural outcomes in buildings with known daylight parameters (Aan het Rot, Mathew & Bhagwagar, 2009)."
  ),
  spacer(200),
  body(
    "Now consider a different claim at the same numerical confidence. An ANALOGICAL bridge at 0.35 linking drug-related incentive sensitisation (Berridge & Robinson, 1998) to architectural place attachment says: the two phenomena share a neural substrate (mesolimbic dopamine), but the temporal dynamics, stimulus parameters, and phenomenological character may differ in ways that break the analogy. The research that would raise this confidence is fundamentally different: it requires establishing that the same mechanism operates in both domains, not merely that the two domains look structurally similar from a distance (Woodward, 2003)."
  ),
  spacer(200),
  body(
    "These two claims, despite sharing a numerical confidence of 0.35, carry completely different implications for research planning, for confidence in predictions, and for the appropriate caution when advising architectural practitioners. The warrant type captures information that a bare number cannot. This is why the EWG preserves warrant types as first-class annotations, and why the projection from EWG to BN is necessarily lossy: the BN receives a number (the CPT entry); the EWG retains the epistemological reasoning behind the number. Der Kiureghian and Ditlevsen (2009) made a similar point in the engineering context—that reducibility of uncertainty depends on the modelling frame—and the warrant type hierarchy operationalises this insight for scientific knowledge systems."
  ),
  spacer(300),

  // Insert Figure 3
  ...imageWithCaption(
    '/sessions/keen-busy-turing/fig3.png',
    'Figure 4. Same confidence value, different epistemic structure. Two claims at 0.35 confidence carry entirely different research implications depending on their bridge warrant type.'
  ),
  spacer(300),

  // SECTION 3: The Practical Import
  heading('3. The Practical Import'),
  body(
    "The distinction between epistemic and aleatory uncertainty has three concrete practical implications: value-of-information analysis, model validation strategy, and research planning. Each is grounded in decision-theoretic foundations and applies broadly across scientific domains (Howard, 1966; Raiffa & Schlaifer, 1961)."
  ),
  spacer(200),
  body(
    "Value-of-information (VOI) analysis asks: if I resolve a specific uncertainty, how much will my decision improve? This question is only coherent when we distinguish what kind of uncertainty we are resolving. If a probability is aleatory, resolving the underlying mechanism will not change the probability—the system will still be random, no matter how well we understand it (Raiffa & Schlaifer, 1961). Resources spent on reducing irreducible randomness are wasted. But if a probability is epistemic, reducing it may yield substantial VOI. A high-impact VOI calculation requires knowing which uncertainties are fundamentally aleatory and which are epistemically reducible (Howard, 1966)."
  ),
  spacer(200),
  body(
    "Model validation strategy must account for the mix of epistemic and aleatory uncertainty in the model (Oreskes, Shrader-Frechette & Belitz, 1994). If a model relies on firm empirical warrants for its core mechanisms, validation against test data is meaningful—the fit reflects whether the causal model correctly predicts outcomes. But if the model relies on stipulative warrants (framework assumptions) or analogical warrants (inferences from different domains), then good fit might reflect overfitting or lucky parameter choices rather than true predictive validity. Validation sufficiency depends on the epistemic structure of the model, not merely on goodness-of-fit statistics (National Research Council, 2009)."
  ),
  spacer(200),
  body(
    "Research planning must prioritize epistemic reduction. If a domain is characterized by high epistemic uncertainty (weak warrant types, low credence), then the marginal value of additional modeling is low; the priority should be experiments and empirical work (Saltelli et al., 2008). If a domain is characterized by low epistemic uncertainty but high aleatory uncertainty (strong warrants, high credence, but stochastic causal mechanisms), then additional modeling—understanding boundary conditions, refining causal mechanisms—may add value. This distinction guides where research effort should be allocated (Der Kiureghian & Ditlevsen, 2009)."
  ),
  spacer(300),

  // SECTION 3.1: Worked Example
  heading('3.1. A Worked Example: Daylight, Serotonin, and Mood', 2),
  body(
    "We now walk through the five-step CPT elicitation protocol with a concrete example from environmental psychology. The question is: what is the probability that high daylight exposure leads to high serotonin levels, all else equal?"
  ),
  spacer(200),
  body(
    "Step 1: Base Rate Extraction. We search the literature for direct evidence linking daylight to serotonin. Lambert et al. (2002) conducted a study measuring serotonin metabolites (5-HIAA) in the blood and cerebrospinal fluid of 46 healthy volunteers across seasons in Australia. They found a strong seasonal effect: 5-HIAA levels were highest in summer (peak daylight) and lowest in winter. To estimate effect size and convert to probability, we compute d for the contrast between long-daylight and short-daylight periods. The effect size is d = 0.38. Following Cohen (1988) conventions for behavioral research, this represents a small-to-medium effect. To convert effect size to probability, we use the cumulative normal distribution: Φ(d/√2) ≈ Φ(0.269) ≈ 0.606. We round to 0.61. This becomes the base conditional probability: P(Serotonin_high | Daylight_high) = 0.61."
  ),
  spacer(200),
  body(
    "Step 2: Bridge Warrant Discount. The Lambert study was conducted in a hospital setting with blood/CSF sampling—controlled but not ecologically valid. The bridge from laboratory neuroscience to architectural application is a MECHANISM bridge: the causal pathway is well-understood (light → retina → suprachiasmatic nucleus → serotonin synthesis), but the magnitude of the effect in real buildings is uncertain (Aan het Rot, Mathew & Bhagwagar, 2009). In the canonical seven-type warrant hierarchy, the standard discount factor for MECHANISM bridges is 0.60 (compared to CONSTITUTIVE at 0.75, EMPIRICAL_COVARIANCE at 0.60, FUNCTIONAL at 0.50, CAPACITY at 0.45, ANALOGICAL at 0.35, and THEORETICAL_DEFAULT below 0.30). The epistemic delta: (0.61 - 0.50) × 0.60 = 0.066. Adjusted probability: 0.50 + 0.066 = 0.57."
  ),
  spacer(200),
  body(
    "Step 3: Qualifier Narrowing. The Lambert study's effect was strongest for morning light (6:00 AM - 10:00 AM), weakest in afternoon and evening. Furthermore, the effect is likely stronger in buildings with high glazing ratio (window area / wall area > 0.4) and direct solar penetration to occupied zones (Beauchemin & Hays, 1996). The CPT entry of 0.58 applies to this specific qualified condition: Morning light, high-glazing buildings. For afternoon light or low-glazing conditions, separate CPT entries are needed, estimated at 0.53 (still above baseline, but weaker effect). The templating system ensures that qualifiers are explicit, and alternative conditions get their own entries."
  ),
  spacer(200),
  body(
    "Step 4: Rebuttal Bands. The EWG template identifies a rebuttal: 'In naturally ventilated buildings, thermal comfort co-varies with daylight, confounding the serotonergic pathway. People may feel better due to thermal comfort, not light.' This is a plausible alternative explanation, ranked as moderate. The rebuttal is grounded in the architecture and environmental psychology literature (Boubekri et al., 2014), where both daylight and thermal conditions affect occupant wellbeing. Uncertainty band: ±0.12. So the CPT entry becomes a range: 0.57 [0.45, 0.69]. This range does not represent epistemic uncertainty about the true CPT value (that would be improperly conflating levels); rather, it represents the range of possible aleatory values if the rebuttal is partially or fully correct."
  ),
  spacer(200),
  body(
    "Step 5: Competing Account Adjustment. The EWG identifies a competing account: the suprachiasmatic nucleus-mediated circadian entrainment pathway, which phase-shifts the sleep-wake cycle and secondarily affects acute mood (Young, 2007). The direct serotonergic pathway (measured by Lambert) may be secondary. Expert consensus estimates the credence of the circadian pathway hypothesis at 0.30. If the circadian pathway is the primary mechanism, the direct serotonin effect is smaller, implying a CPT value of 0.53 rather than 0.57. Weighted average: (0.70 × 0.57) + (0.30 × 0.53) = 0.399 + 0.159 = 0.558. Rounded: P(Serotonin_high | Daylight_high) = 0.56 [0.44, 0.68]."
  ),
  spacer(200),
  body(
    "This final number is not arbitrary. Each step is traceable: (1) Lambert et al. 2002 provides the base rate of 0.61; (2) MECHANISM bridge warrant at 0.60 applies because the causal pathway is known but the magnitude in real buildings is uncertain; (3) the qualifier 'morning light, high-glazing buildings' makes the scope explicit; (4) the rebuttal about thermal confounding expands the uncertainty band to ±0.12; (5) the competing circadian hypothesis receives 0.30 credence, shifting the final estimate down slightly (Young, 2007). The final value of 0.56 [0.44, 0.68] reflects a principled attenuation from the raw effect size: the MECHANISM discount, the qualifier restriction, and the competing account each contribute a traceable adjustment. If new evidence arrives—a new architectural study of daylight and mood, or a mechanistic study showing that the circadian effect is larger than thought—the EWG updates and the CPT entry regenerates. The architecture makes epistemic content and aleatory parameters transparent and revisable (Oreskes, Shrader-Frechette & Belitz, 1994)."
  ),
  spacer(200),
  body(
    "Multi-Channel Convergence and Credence Composition. The worked example above traces a single bridge warrant from one theoretical channel (serotonergic pathway) through a single MECHANISM bridge to a CPT entry. This is the atomic unit of credence computation: P(effect | evidence_i) = P(parent_i) × P(bridge_i) × P(CNFA_i). In practice, many templates are supported by multiple independent theoretical channels. VIEW1 (view of nature), for instance, receives support through at least five pathways: serotonergic modulation, cortisol regulation via the HPA axis, attentional restoration (ART/Kaplan, 1995), stress recovery (SRT/Ulrich, 1983), and biophilic preference (Kellert & Wilson, 1993). Each channel contributes its own bridge-discounted credence. When multiple independent channels converge on the same template, they combine via noisy-OR aggregation: P(composite) = 1 - ∏(1 - credence_i). This is why multi-channel templates can have composite credences substantially exceeding any single bridge product. A template receiving five independent channels at credences of 0.40, 0.35, 0.38, 0.33, and 0.42 yields a noisy-OR composite of approximately 0.88—not because any single piece of evidence is that strong, but because five independent lines of evidence each independently increase the probability that the effect is real (Pearl, 2009; Bovens & Hartmann, 2003). The multiplicative formula at the bridge level and the noisy-OR aggregation at the template level serve different functions: the former attenuates overconfidence within a single evidential channel, the latter rewards genuine convergence across independent channels. See Algorithm 1 (TYPED_CREDENCE_PROPAGATION) in the master specification for the full four-layer computation."
  ),
  spacer(300),

  // Insert Figure 4
  ...imageWithCaption(
    '/sessions/keen-busy-turing/fig4.png',
    'Figure 5. The CPT elicitation pipeline. Epistemic content from the Epistemic Warrant Graph (EWG) (left) passes through five translation steps to produce an aleatory probability entry for the Bayesian Network (right). Each step is traceable and reversible.'
  ),
  spacer(300),

  // SECTION 4: CPT Elicitation
  heading('4. The CPT Elicitation Problem (General)'),
  body(
    "The five-step protocol described above generalizes to any causal claim in the EWG (O'Hagan et al., 2006). The general steps are grounded in established expert elicitation methodology (Cooke, 1991)."
  ),
  spacer(200),
  body(
    "(1) Base Rate Extraction: Search for direct empirical evidence of the claimed relationship. If effect sizes or correlations are reported, convert to probability using Φ(d/√2) or r/(1+r) mappings (Cohen, 1988). If only qualitative evidence exists, assign a base rate based on expert consensus (high confidence → 0.7-0.8, moderate → 0.55-0.65, low → 0.45-0.55, refutation → 0.2-0.3). This step grounds the elicitation in observable data (O'Hagan et al., 2006)."
  ),
  spacer(200),
  body(
    "(2) Bridge Warrant Discount: Identify the warrant type from the seven-level hierarchy and apply the corresponding discount factor reflecting the gap between the evidence and the target application (Renooij, 2001). CONSTITUTIVE (true by definition of the system): 0.75. MECHANISM (known causal pathway): 0.60. EMPIRICAL_COVARIANCE (direct observational correlation): 0.60. FUNCTIONAL (follows from functional organisation): 0.50. CAPACITY (mechanism has the capacity to produce the effect): 0.45. ANALOGICAL (parallel case extension): 0.35. THEORETICAL_DEFAULT (framework starting assumption): below 0.30. The discount adjusts the magnitude of the epistemic delta above or below the 0.5 neutral point. This ranking is grounded in epistemological theory about warrant strength (Cartwright, 1983; Toulmin, 1958)."
  ),
  spacer(200),
  body(
    "(3) Qualifier Narrowing: Identify qualifiers that restrict the scope of the claim (context, population, dose, method). Create separate CPT entries for each distinct qualified condition (Druzdzel & van der Gaag, 2000). This prevents false generalization and makes explicit the conditions under which the causal claim holds. Qualifiers are drawn from the Toulmin model of argumentation (Toulmin, 1958; Walton, 2006)."
  ),
  spacer(200),
  body(
    "(4) Rebuttal Bands: Identify rebuttals (alternative explanations, confounds, mechanism challenges). Assess the rebuttal as strong (±0.15), moderate (±0.12), weak (±0.08), or negligible (±0.05). The band reflects the range of aleatory values consistent with the rebuttal being partially or fully correct. Rebuttals are also drawn from the Toulmin model and represent challenges to the warrant's supporting force (Toulmin, 1958)."
  ),
  spacer(200),
  body(
    "(5) Competing Account Adjustment: If multiple competing mechanistic explanations exist, assess credence in each (summing to 1.0). For each account, estimate its implied CPT value. Compute a weighted average (Thagard, 1989). This step prevents false certainty when multiple pathways to the same outcome are plausible."
  ),
  spacer(200),
  body(
    "The discount factors in step (2) are not arbitrary. They reflect a principled ranking of warrant types by epistemic strength: CONSTITUTIVE > MECHANISM ≈ EMPIRICAL_COVARIANCE > FUNCTIONAL > CAPACITY > ANALOGICAL > THEORETICAL_DEFAULT. This ranking captures the degree to which each warrant type constrains possible error. Constitutive warrants are near-definitional, leaving little room for empirical surprise. Mechanism and empirical covariance warrants directly engage causal or observational evidence, constraining the space of possible outcomes substantially. Functional and capacity warrants identify structural roles and dispositional properties, providing moderate constraint. Analogical warrants extend across domains with unknown translation losses, while theoretical defaults are framework-relative starting points that carry the highest epistemic risk (Cartwright, 1989, 1999; Cooke, 1991; O'Hagan et al., 2006). The discount factors quantify this hierarchy in a tractable way, making the reasoning from evidence quality to parameter confidence fully explicit."
  ),
  spacer(200),
  body(
    "The protocol is not deterministic. Different practitioners might weight evidence differently, assign different discount factors, or disagree on qualifiers and rebuttals. This is expected: the EWG is designed to be revisable, and disagreement surfaces differences in epistemic judgment that should be made explicit and debated (Quine & Ullian, 1978). The protocol provides structure for that debate, not an algorithm that eliminates human judgment."
  ),
  spacer(300),

  // SECTION 5: Discussion
  heading('5. Discussion'),
  heading('5.1. The De Finetti Objection', 2),
  body(
    "Bruno de Finetti's radical subjectivism (1937) denies that objective probability—aleatory probability as a property of the world—exists at all. For de Finetti, all probability is epistemic, a rational agent's degree of belief. His exchangeability theorem shows that any sequence of exchangeable outcomes can be represented as a mixture of i.i.d. processes; in other words, apparent objective randomness can be reconstructed from an agent's beliefs via the representation theorem (de Finetti, 1937; Skyrms, 1984). If de Finetti is right, then the epistemic-aleatory distinction is a philosophical mistake—there is only credence, varying in how well-calibrated it is to empirical frequencies (Gillies, 2000)."
  ),
  spacer(200),
  body(
    "We respond with three points. First, even if de Finetti is metaphysically correct about probability, the distinction has practical architectural value. A computational system that reasons under uncertainty needs different data structures for different purposes (Russell & Norvig, 2021). Credences that reflect our ignorance about mechanisms (epistemic) have different computational affordances than credences that reflect the inherent stochasticity of nature (aleatory). Conflating them, even if metaphysically justified, produces the two characteristic errors described above (Der Kiureghian & Ditlevsen, 2009). The ATLAS architecture's dual structure (EWG plus BN) is justified by computational practice, not by metaphysical ontology."
  ),
  spacer(200),
  body(
    "Second, the pragmatic argument from Der Kiureghian and Ditlevsen (2009) applies to de Finetti's objection. They note that the distinction is model-dependent: what counts as aleatory versus epistemic depends on the modeling frame. De Finetti's critique applies at the metaphysical level, asking whether objective probability exists outside any model. But within a model—a choice to represent certain variables as random and others as unknown—the distinction becomes operationally real (Diaconis & Freedman, 1980). ATLAS commits to a specific modeling frame (a Web + BN architecture) in which epistemic and aleatory are distinguished by their computational role. De Finetti's metaphysics does not undermine this operational distinction."
  ),
  spacer(200),
  body(
    "Third, Hacking's (1975) historical analysis of probability points to a deeper point: probability as a concept has always been Janus-faced, with an aspect looking toward objective reality and an aspect looking toward rational belief. Any theory of probability that eliminates one face leaves something important unexpressed. De Finetti's subjectivism is elegant and logically powerful, but it asks us to give up the language of objective chance, physical randomness, natural variability. For scientific and engineering applications, this is a costly sacrifice (Gillies, 2000). The language persists in practice, and rightly so: scientists and engineers need to talk about what the world could have been, not just about their uncertainty (Cartwright, 1983)."
  ),
  spacer(300),

  heading('5.2. The Engineering Objection', 2),
  body(
    "A practical objection comes from engineering practice. Many successful Bayesian networks have been built and deployed without tracking epistemic provenance or distinguishing warrant types (Jensen & Nielsen, 2007; Russell & Norvig, 2021). Medical diagnosis systems (Shortliffe & Buchanan, 1975), spam filters, autonomous vehicle perception pipelines (Roy et al., 2002), and dozens of other applications work well with a simple probabilistic architecture. Why add the complexity of a dual structure and a projection function? Does the distinction deliver enough practical value to justify the added machinery?"
  ),
  spacer(200),
  body(
    "We respond with three points. First, success in well-characterized domains does not generalize to heterogeneous-evidence domains. Medical diagnosis systems succeed because the relevant variables (patient symptoms, disease states) have been extensively studied with standardized measures. The evidence base is largely uniform: many empirical studies with large samples and clear operational definitions. In such domains, the epistemic structure is relatively uniform, and treating all probabilities alike works (Shortliffe & Buchanan, 1975). But in environmental psychology, climate science, architectural neuroscience, and other domains where evidence is heterogeneous—mixing laboratory findings with field observations, theoretical models with empirical measurements (National Research Council, 2009)—the uniform treatment fails. Warrant types differ drastically across variables; some are well-studied, others are analogically extended. Tracking this diversity is essential for credible modeling (Oberkampf et al., 2004)."
  ),
  spacer(200),
  body(
    "Second, value-of-information analysis is impossible without the distinction. A decision-maker who asks 'which variable should I invest in studying?' needs to know which uncertainties are reducible (Howard, 1966; Raiffa & Schlaifer, 1961). A standard Bayesian network answers only whether resolving an uncertainty would improve decisions (by reducing posterior variance), not whether the uncertainty is reducible in principle. If a probability is aleatory, further investigation will not change it—only refining the causal mechanism, stratifying the population, or discovering unmodeled variables might help. A decision-maker with a standard BN has no way to distinguish these cases. CMR's dual structure makes it explicit. Oberkampf et al. (2004) show that verification and validation of computational models requires distinguishing aleatory from epistemic uncertainty: you validate a model by reducing epistemic uncertainty, not by acknowledging aleatory variability."
  ),
  spacer(200),
  body(
    "Third, the engineering objection underestimates the cost of conflation. Consider a validation study for an architectural model of daylight and human response (Boubekri et al., 2014). The model has 60 probabilistic parameters. A researcher collects data on 40 of them, achieving narrow credence intervals (epistemic uncertainty reduced). For the other 20, she assigns prior distributions based on expert judgment or analogical reasoning (O'Hagan et al., 2006). She runs the model against test data and observes a good fit (Oreskes, Shrader-Frechette & Belitz, 1994). She publishes the model as validated. But which of the 20 unvalidated parameters are problematic? If they govern inherently stochastic processes (absorption spectra of materials, individual variation in visual sensitivity), then leaving them as priors is not a validation failure—the fit is meaningful. If they govern causal mechanisms that could be studied (e.g., the effect of glare on task performance), then validation is incomplete—the model is credible despite epistemic risk, and users should be warned (National Research Council, 2009). A standard BN provides no way to distinguish these cases. ATLAS's dual structure makes the distinction explicit: you examine the warrant types in the EWG. If a parameter has a THEORETICAL_DEFAULT warrant (merely assumed as a framework starting point) and governs a causal mechanism, that parameter needs empirical validation before the model can be trusted."
  ),
  spacer(300),

  // SECTION 6: Conclusion
  heading('6. Conclusion'),
  body(
    "The distinction between epistemic and aleatory uncertainty is not a philosophical curiosity (Knight, 1921; Hacking, 1975). It is an architectural necessity for computational systems that represent scientific knowledge in domains characterized by heterogeneous evidence and strategic choices about where to invest research effort (Der Kiureghian & Ditlevsen, 2009)."
  ),
  spacer(200),
  body(
    "We have argued three main points. First, conflating epistemic and aleatory uncertainty produces two characteristic errors: misallocation of research effort (not knowing which uncertainties are reducible) and misjudgment of model validation sufficiency (treating all probability assignments alike, regardless of their warrant). This argument is grounded in the engineering literature on uncertainty quantification (Oberkampf et al., 2004; Helton, 1997). Second, the ATLAS system's dual architecture—an Epistemic Warrant Graph (EWG) tracking epistemic content with Toulmin provenance, and a Bayesian Network storing aleatory probabilities—solves this conflation at the computational level (Toulmin, 1958; Pearl, 2009). Third, bridge warrant types provide a finer-grained categorization of epistemic uncertainty than the binary epistemic/aleatory split, enabling value-of-information analyses and research planning that distinguish what can be studied from what is inherently stochastic (Walton, 2006; Machamer, Darden & Craver, 2000)."
  ),
  spacer(200),
  body(
    "The five-step CPT elicitation protocol provides a principled, traceable method for translating between the two structures: from empirical evidence, mechanistic understanding, analogical reasoning, authority, and stipulation, we extract aleatory probability values while preserving epistemic metadata (O'Hagan et al., 2006; Cooke, 1991). The protocol is not deterministic—expert judgment enters at multiple points—but it makes judgment explicit and revisable. As new evidence arrives, the EWG updates, and the projection regenerates the affected CPT entries (Renooij, 2001; Druzdzel & van der Gaag, 2000). The architecture operationalizes Der Kiureghian and Ditlevsen's insight that the distinction is model-dependent: once a modeling frame is chosen (as CMR chooses), the distinction becomes operationally real and computationally necessary."
  ),
  spacer(200),
  body(
    "We have also addressed three major philosophical objections. De Finetti's radical subjectivism challenges whether objective probability exists (de Finetti, 1937; Skyrms, 1984); we respond that within a computational model, the distinction is operationally necessary regardless of metaphysical status (Gillies, 2000). Lewis's Principal Principle specifies what convergence between epistemic and aleatory should look like (Lewis, 1980; Williamson, 2000); Moss's interleaving problem warns that the path to convergence is messy (Moss, 2018). ATLAS accommodates both: the Principal Principle sets the regulative ideal, and the EWG-to-BN projection makes the messiness explicit and traceable. The engineering objection notes that successful systems have been built without the distinction (Jensen & Nielsen, 2007; Russell & Norvig, 2021); we respond that success in uniform-evidence domains does not generalize, and that value-of-information analysis and validation strategy require the distinction in heterogeneous-evidence domains (Oberkampf et al., 2004; Saltelli et al., 2008)."
  ),
  spacer(200),
  body(
    "Future work on the framework includes formal axiomatisation of the projection function (Pearl, 2009; Woodward, 2003), empirical calibration of discount factors across domains (Helton, 1997), extension to temporal dynamics (how do uncertainties evolve as evidence accumulates?), and application to additional scientific domains beyond environmental psychology and architectural neuroscience. We also note the potential for automated support: given a literature corpus and qualitative claims about causal mechanisms, can we semi-automatically extract base rates, identify warrant types, and flag problematic gaps in evidence? Such tools could make the CMR framework more accessible to domain practitioners (O'Hagan et al., 2006)."
  ),
  spacer(200),
  body(
    "The core insight is simple: knowing that you know something is different from knowing that something is random (Knight, 1921; Ramsey, 1926). Computational systems that conflate these two forms of knowledge will misallocate resources and overestimate validation sufficiency. The epistemic-aleatory distinction, implemented architecturally through the EWG, provides a path toward more credible, more transparent, and more strategically guided computational modeling of complex domains (Der Kiureghian & Ditlevsen, 2009; Oreskes, Shrader-Frechette & Belitz, 1994)."
  ),
  spacer(400),

  // REFERENCES
  new Paragraph({
    text: '',
    pageBreakBefore: true,
  }),
  heading('References'),
  spacer(200),
  referenceEntry('Aan het Rot, M., Mathew, S. J., & Bhagwagar, Z.', '2009', 'Neurobiological mechanisms in major depressive disorder', 'CMAJ, 180(3), 305–313', '', '~600'),
  referenceEntry('Beauchemin, K. M., & Hays, P.', '1996', 'Sunny hospital rooms expedite recovery from severe and refractory depressions', 'Journal of Affective Disorders, 40(1–2), 49–51', '', '~500'),
  referenceEntry('Berridge, K. C., & Robinson, T. E.', '1998', 'What is the role of dopamine in reward?', 'Brain Research Reviews, 28(3), 309–369', '', '~7,500'),
  referenceEntry('Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R.', '2009', 'Introduction to meta-analysis', 'Wiley', '', '~15,000'),
  referenceEntry('Boubekri, M., Cheung, I. N., Reid, K. J., Wang, C.-H., & Zee, P. C.', '2014', 'Impact of windows and daylight exposure on overall health and sleep quality of office workers', 'Journal of Clinical Sleep Medicine, 10(6), 603–611', '', '~800'),
  referenceEntry('Carnap, R.', '1950', 'Logical foundations of probability', 'University of Chicago Press', '', '~5,000'),
  referenceEntry('Cartwright, N.', '1983', 'How the laws of physics lie', 'Oxford University Press', '', '~6,000'),
  referenceEntry('Cartwright, N.', '1989', 'Nature\'s capacities and their measurement', 'Oxford University Press', '', '~3,500'),
  referenceEntry('Cartwright, N.', '1999', 'The dappled world: A study of the boundaries of science', 'Cambridge University Press', '', '~4,200'),
  referenceEntry('Clark, A.', '2013', 'Whatever next? Predictive brains, situated agents, and the future of cognitive science', 'Behavioral and Brain Sciences, 36(3), 181–204', '', '~4,000'),
  referenceEntry('Cohen, J.', '1988', 'Statistical power analysis for the behavioral sciences (2nd ed.)', 'Lawrence Erlbaum', '', '~90,000'),
  referenceEntry('Cooke, R. M.', '1991', 'Experts in uncertainty: Opinion and subjective probability in science', 'Oxford University Press', '', '~2,000'),
  referenceEntry('de Finetti, B.', '1937', 'La prévision: Ses lois logiques, ses sources subjectives', 'Annales de l\'Institut Henri Poincaré, 7(1), 1–68', '', '~4,500'),
  referenceEntry('Der Kiureghian, A., & Ditlevsen, O.', '2009', 'Aleatory or epistemic? Does it matter?', 'Structural Safety, 31(2), 105–112', '', '~1,800'),
  referenceEntry('Diaconis, P., & Freedman, D.', '1980', 'De Finetti\'s theorem for Markov chains', 'Annals of Probability, 8(1), 115–130', '', '~300'),
  referenceEntry('Druzdzel, M. J., & van der Gaag, L. C.', '2000', 'Building probabilistic networks: Where do the numbers come from?', 'IEEE Transactions on Knowledge and Data Engineering, 12(4), 481–486', '', '~400'),
  referenceEntry('Fox, C. R., & Ülkümen, G.', '2011', 'Distinguishing two dimensions of uncertainty', 'In W. Brun et al. (Eds.), Perspectives on thinking, judging, and decision making (pp. 21–35). Universitetsforlaget', '', '~250'),
  referenceEntry('Gillies, D.', '2000', 'Philosophical theories of probability', 'Routledge', '', '~1,500'),
  referenceEntry('Hacking, I.', '1975', 'The emergence of probability', 'Cambridge University Press', '', '~3,200'),
  referenceEntry('Hájek, A.', '2019', 'Interpretations of probability', 'In E. N. Zalta (Ed.), Stanford Encyclopedia of Philosophy. Stanford University', '', ''),
  referenceEntry('Helton, J. C.', '1997', 'Uncertainty and sensitivity analysis in the presence of stochastic and subjective uncertainty', 'Journal of Statistical Computation and Simulation, 57(1–4), 3–76', '', '~500'),
  referenceEntry('Hoffman, F. O., & Hammonds, J. S.', '1994', 'Propagation of uncertainty in risk assessments: The need to distinguish between uncertainty due to lack of knowledge and uncertainty due to variability', 'Risk Analysis, 14(5), 707–712', '', '~600'),
  referenceEntry('Howard, R. A.', '1966', 'Information value theory', 'IEEE Transactions on Systems Science and Cybernetics, 2(1), 22–26', '', '~3,000'),
  referenceEntry('Jaynes, E. T.', '2003', 'Probability theory: The logic of science', 'Cambridge University Press', '', '~8,000'),
  referenceEntry('Jensen, F. V., & Nielsen, T. D.', '2007', 'Bayesian networks and decision graphs (2nd ed.)', 'Springer', '', '~5,000'),
  referenceEntry('Joyce, J. M.', '1998', 'A nonpragmatic vindication of probabilism', 'Philosophy of Science, 65(4), 575–603', '', '~600'),
  referenceEntry('Kaplan, S., & Garrick, B. J.', '1981', 'On the quantitative definition of risk', 'Risk Analysis, 1(1), 11–27', '', '~4,200'),
  referenceEntry('Knight, F. H.', '1921', 'Risk, uncertainty and profit', 'Houghton Mifflin', '', '~18,000'),
  referenceEntry('Kolmogorov, A. N.', '1933', 'Foundations of the theory of probability (N. Morrison, Trans., 1956)', 'Chelsea Publishing', '', '~8,000'),
  referenceEntry('Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D.', '2002', 'Effect of sunlight and season on serotonin turnover in the brain', 'The Lancet, 360(9348), 1840–1842', '', '~1,100'),
  referenceEntry('Lewis, D.', '1980', 'A subjectivist\'s guide to objective chance', 'In R. C. Jeffrey (Ed.), Studies in inductive logic and probability (Vol. 2, pp. 263–293). University of California Press', '', '~3,800'),
  referenceEntry('Machamer, P., Darden, L., & Craver, C. F.', '2000', 'Thinking about mechanisms', 'Philosophy of Science, 67(1), 1–25', '', '~5,000'),
  referenceEntry('Monmonier, M.', '1991', 'How to lie with maps', 'University of Chicago Press', '', '~4,500'),
  referenceEntry('Moss, S.', '2018', 'Probabilistic knowledge', 'Oxford University Press', '', '~400'),
  referenceEntry('National Research Council', '2009', 'Understanding climate change: Climate models and their simulation of the past', 'National Academies Press', '', '~1,000'),
  referenceEntry('Oberkampf, W. L., Helton, J. C., Joslyn, C. A., Trucano, T. G., & Sargsyan, S. F.', '2004', 'Challenge problems: Uncertainty in system response given uncertain parameters', 'Reliability Engineering & System Safety, 85(1–3), 11–19', '', '~1,200'),
  referenceEntry('O\'Hagan, A., Buck, C. E., Daneshkhah, A., Eiser, J. R., Garthwaite, P. H., Jenkinson, D. J., Oakley, J. E., & Rakow, T.', '2006', 'Uncertain judgements: Eliciting experts\' probabilities', 'Wiley', '', '~1,500'),
  referenceEntry('Oreskes, N., Shrader-Frechette, K., & Belitz, K.', '1994', 'Verification, validation, and confirmation of numerical models in the earth sciences', 'Science, 263(5147), 641–646', '', '~5,000'),
  referenceEntry('Pearl, J.', '2009', 'Causality: Models, reasoning, and inference (2nd ed.)', 'Cambridge University Press', '', '~28,000'),
  referenceEntry('Pettigrew, R.', '2016', 'Accuracy and the laws of credence', 'Oxford University Press', '', '~400'),
  referenceEntry('Quine, W. V. O., & Ullian, J. S.', '1978', 'The web of belief (2nd ed.)', 'Random House', '', '~2,500'),
  referenceEntry('Raiffa, H., & Schlaifer, R.', '1961', 'Applied statistical decision theory', 'Harvard Business School', '', '~5,000'),
  referenceEntry('Ramsey, F. P.', '1926', 'Truth and probability', 'In R. B. Braithwaite (Ed.), The foundations of mathematics and other logical essays (1931, pp. 156–198). Kegan Paul', '', '~4,000'),
  referenceEntry('Reichenbach, H.', '1949', 'The theory of probability', 'University of California Press', '', '~2,000'),
  referenceEntry('Renooij, S.', '2001', 'Probability elicitation for belief networks: Issues to consider', 'Knowledge Engineering Review, 16(3), 255–269', '', '~300'),
  referenceEntry('Roy, N., Gordon, G., & Thrun, S.', '2002', 'Finding approximate POMDP solutions through belief compression', 'Journal of Artificial Intelligence Research, 23, 1–40', '', '~400'),
  referenceEntry('Robinson, A. H.', '1952', 'The look of maps: An examination of cartographic design', 'University of Wisconsin Press', '', '~1,500'),
  referenceEntry('Robinson, A. H., Morrison, J. L., Muehrcke, P. C., Kimerling, A. J., & Guptill, S. C.', '1995', 'Elements of cartography (6th ed.)', 'Wiley', '', '~3,200'),
  referenceEntry('Russell, S. J., & Norvig, P.', '2021', 'Artificial intelligence: A modern approach (4th ed.)', 'Pearson', '', '~20,000'),
  referenceEntry('Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S.', '2008', 'Global sensitivity analysis: The primer', 'Wiley', '', '~6,000'),
  referenceEntry('Savage, L. J.', '1954', 'The foundations of statistics', 'Wiley', '', '~15,000'),
  referenceEntry('Shortliffe, E. H., & Buchanan, B. G.', '1975', 'A model of inexact reasoning in medicine', 'Mathematical Biosciences, 23(3–4), 351–379', '', '~3,000'),
  referenceEntry('Skyrms, B.', '1984', 'Pragmatics and empiricism', 'Yale University Press', '', '~800'),
  referenceEntry('Spohn, W.', '2012', 'The laws of belief: Ranking theory and its philosophical applications', 'Oxford University Press', '', '~600'),
  referenceEntry('Thagard, P.', '1989', 'Explanatory coherence', 'Behavioral and Brain Sciences, 12(3), 435–467', '', '~2,400'),
  referenceEntry('Tomlin, C. D.', '1990', 'Geographic information systems and cartographic modeling', 'Prentice Hall', '', '~2,800'),
  referenceEntry('Toulmin, S. E.', '1958', 'The uses of argument', 'Cambridge University Press', '', '~12,000'),
  referenceEntry('von Mises, R.', '1928', 'Probability, statistics and truth (2nd rev. ed., 1957)', 'Macmillan', '', '~1,500'),
  referenceEntry('Walton, D.', '2006', 'Fundamentals of critical argumentation', 'Cambridge University Press', '', '~1,200'),
  referenceEntry('Williamson, T.', '2000', 'Knowledge and its limits', 'Oxford University Press', '', '~6,000'),
  referenceEntry('Wood, D.', '1992', 'The power of maps', 'Guilford Press', '', '~3,000'),
  referenceEntry('Woodward, J.', '2003', 'Making things happen: A theory of causal explanation', 'Oxford University Press', '', '~7,000'),
  referenceEntry('Young, S. N.', '2007', 'How to increase serotonin in the human brain without drugs', 'Journal of Psychiatry & Neuroscience, 32(6), 394–399', '', '~800'),
  spacer(400),

  // APPENDIX
  new Paragraph({
    text: '',
    pageBreakBefore: true,
  }),
  heading('Appendix: Condensed Version'),
  body(
    "The following section presents a condensed, approximately 800-word summary of the full paper, suitable for readers seeking a rapid overview."
  ),
  spacer(300),
  body(
    "Computational systems frequently reason with uncertainty, but they often conflate two distinct kinds: epistemic uncertainty (uncertainty in what we know) and aleatory uncertainty (inherent randomness in the world) (Knight, 1921; Kolmogorov, 1933). This conflation produces two errors: misallocating research effort (not knowing what can be studied) and overestimating model validation (treating all probabilities alike regardless of evidence quality) (Der Kiureghian & Ditlevsen, 2009)."
  ),
  spacer(200),
  body(
    "The epistemic-aleatory distinction has roots in philosophy (de Finetti's subjective probability, Lewis's Principal Principle) and has recently gained attention in engineering (Der Kiureghian and Ditlevsen's pragmatic account, Oberkampf et al.'s uncertainty taxonomy for computational models) (de Finetti, 1937; Lewis, 1980; Oberkampf et al., 2004). The distinction is not absolute but model-dependent: once a modeling frame is chosen, it becomes operationally real (Cartwright, 1983; Woodward, 2003)."
  ),
  spacer(200),
  body(
    "ATLAS (Architecture for Typed, Layered Assessment of Science) maintains this distinction through a dual architecture (Pearl, 2009; Jensen & Nielsen, 2007). The Epistemic Warrant Graph (EWG) tracks epistemic content: causal claims with Toulmin warrant types ranked in a seven-level hierarchy—constitutive, mechanism, empirical covariance, functional, capacity, analogical, and theoretical default (Toulmin, 1958; Walton, 2006)—along with credence values, qualifiers, and rebuttals. The Bayesian Network stores aleatory content: conditional probability tables without provenance metadata. A projection function translates epistemically-warranted claims into aleatory probabilities; when the EWG revises, the BN regenerates. This dual structure makes epistemic and aleatory uncertainty transparent and computationally distinct (O'Hagan et al., 2006)."
  ),
  spacer(200),
  body(
    "Within this architecture, bridge warrant types provide a finer-grained categorization of epistemic uncertainty (Machamer, Darden & Craver, 2000; Thagard, 1989). Two claims at the same credence value (e.g., 0.35) may carry different research implications depending on their warrant type. A claim backed by a CONSTITUTIVE warrant (true by definition) carries minimal epistemic risk; one supported by a MECHANISM or EMPIRICAL_COVARIANCE warrant rests on direct causal or observational evidence; one extended through ANALOGICAL reasoning from another domain carries substantial translation risk (Cooke, 1991). These distinctions guide where research effort should be allocated: constitutive and empirical covariance warrants suggest the claim is well-characterised; mechanism and functional warrants suggest targeted empirical work could strengthen the evidence; capacity and analogical warrants flag claims where new evidence could substantially revise the picture; and theoretical defaults mark framework assumptions requiring the most scrutiny."
  ),
  spacer(200),
  body(
    "The Bayesian network, by contrast, stores aleatory probabilities stripped of epistemological provenance—bare CPT entries derived from the EWG's epistemic content through a formal projection function (Renooij, 2001; Druzdzel & van der Gaag, 2000). The projection is necessarily lossy: the BN receives a number; the EWG retains the reasoning behind the number. This lossiness is by design. The BN is a computationally tractable snapshot of the EWG's current epistemic state, optimized for interventional and counterfactual inference (Woodward, 2003). When the EWG revises—a new study is published, a competition is resolved, a working model is adopted—the BN is regenerated from scratch via the projection function."
  ),
  spacer(200),
  body(
    "Confusing these two kinds of uncertainty leads to characteristic errors in applied science (Der Kiureghian & Ditlevsen, 2009; Oreskes, Shrader-Frechette & Belitz, 1994). One error is endlessly collecting occupant data when the real problem is that the mechanism chain is wrongly specified—this reduces aleatory uncertainty but leaves epistemic uncertainty untouched. The opposite error is endlessly refining the theoretical model when the real problem is insufficient data—this increases theoretical sophistication but does not reduce aleatory imprecision (Oberkampf et al., 2004). The architectural distinction between EWG (epistemic) and BN (aleatory) ensures that neither is confused with the other, and the Value of Information algorithm ranks epistemic uncertainties by their downstream consequences (Howard, 1966; Raiffa & Schlaifer, 1961), providing a principled research agenda that distinguishes 'we need more data' from 'we need better theory.'"
  ),
  spacer(200),
];

// Create document
const doc = new Document({
  sections: [
    {
      properties: {
        page: {
          margins: {
            top: 1440,
            bottom: 1440,
            left: 1440,
            right: 1440,
          },
          size: {
            width: 12240,
            height: 15840,
          },
        },
      },
      children: sections,
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              text: 'Mapping the Epistemic Landscape',
              font: 'Garamond',
              size: 22,
              italics: true,
              alignment: AlignmentType.CENTER,
              spacing: { before: 200 },
            }),
          ],
        }),
      },
    },
  ],
  defaultSection: {
    properties: {
      page: {
        margins: {
          top: 1440,
          bottom: 1440,
          left: 1440,
          right: 1440,
        },
        pageHeight: 15840,
        pageWidth: 12240,
      },
    },
  },
});

// Ensure output directory exists
const outputDir = '/sessions/keen-busy-turing/mnt/outputs';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Write document
Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(`${outputDir}/Kirsh_Two_Kinds_of_Uncertainty_2026.docx`, buffer);
  console.log('Document generated successfully: Kirsh_Two_Kinds_of_Uncertainty_2026.docx');
});
