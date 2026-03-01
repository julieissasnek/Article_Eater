const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, 
        PageBreak, Footer, PageNumber, BorderStyle, Table, TableRow, 
        TableCell, WidthType, ShadingType, PageOrientation } = require('docx');

// ===== HELPERS =====
const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 },
  children: [new TextRun({ text, bold: true, font: "Georgia", size: 32 })]
});
const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2, spacing: { before: 320, after: 160 },
  children: [new TextRun({ text, bold: true, font: "Georgia", size: 28 })]
});
const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3, spacing: { before: 260, after: 120 },
  children: [new TextRun({ text, bold: true, font: "Georgia", size: 26 })]
});
const p = (text, opts = {}) => new Paragraph({
  spacing: { before: 120, after: 120, line: 276 },
  indent: opts.noIndent ? undefined : { firstLine: 360 },
  alignment: opts.center ? AlignmentType.CENTER : undefined,
  children: [new TextRun({ text, font: "Georgia", size: 24, italics: opts.i || false, bold: opts.b || false })]
});
const pr = (runs, opts = {}) => new Paragraph({
  spacing: { before: opts.sb || 120, after: opts.sa || 120, line: 276 },
  indent: opts.noIndent ? undefined : { firstLine: 360 },
  children: runs.map(r => new TextRun({ font: "Georgia", size: 24, ...r }))
});
const bq = (text) => new Paragraph({
  spacing: { before: 200, after: 200, line: 276 },
  indent: { left: 720, right: 720 },
  children: [new TextRun({ text, font: "Georgia", size: 22, italics: true })]
});
const PB = () => new Paragraph({ children: [new PageBreak()] });
const SP = (n=400) => new Paragraph({ spacing: { before: n }, children: [] });

// Table helpers
const bdr = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const bdrs = { top: bdr, bottom: bdr, left: bdr, right: bdr };
const cm = { top: 80, bottom: 80, left: 120, right: 120 };
const hcell = (text, w) => new TableCell({ borders: bdrs, width: { size: w, type: WidthType.DXA },
  shading: { fill: "2C3E50", type: ShadingType.CLEAR }, margins: cm,
  children: [new Paragraph({ spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Georgia", size: 20, bold: true, color: "FFFFFF" })] })] });
const tcell = (text, w, opts={}) => new TableCell({ borders: bdrs, width: { size: w, type: WidthType.DXA },
  shading: opts.sh ? { fill: opts.sh, type: ShadingType.CLEAR } : undefined, margins: cm,
  children: [new Paragraph({ spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Georgia", size: 20, bold: opts.b||false, italics: opts.i||false })] })] });

const C = []; // content array

// ===== TITLE =====
C.push(SP(1800));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
  children: [new TextRun({ text: "The ATLAS Epistemic Network", font: "Georgia", size: 44, bold: true })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
  children: [new TextRun({ text: "Architecture, Terminology, and Formal Properties", font: "Georgia", size: 32, bold: true })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
  children: [new TextRun({ text: "A Dual-Layer System for Evidence-Based Architectural Design", font: "Georgia", size: 26, italics: true })] }));
C.push(SP(300));
C.push(p("David Kirsh", { center: true, noIndent: true }));
C.push(p("Department of Cognitive Science, UC San Diego", { center: true, noIndent: true }));
C.push(SP(120));
C.push(p("February 2026 \u2014 Working Document v1.0", { center: true, noIndent: true }));
C.push(PB());

// ===== 1. INTRODUCTION =====
C.push(h1("1. Introduction: The Problem of Responsible Transfer"));

C.push(p("Environmental psychology produces findings in laboratories. Architects apply those findings in buildings. Between the laboratory and the building lies a transfer gap that no amount of statistical sophistication can close by itself. The laboratory used controlled lighting, a homogeneous population of undergraduates, and thirty-minute exposure periods. The building will have variable lighting, a diverse population of occupants, and years of continuous habitation. The question is not whether the laboratory finding is true \u2014 it may well be \u2014 but whether it will hold in this radically different context."));

C.push(p("The ATLAS system is designed to answer that question honestly. It does so through a dual-layer architecture that separates two fundamentally different concerns: what we know about environment-behavior relationships (the epistemic layer) and what we predict will happen in a specific building (the operational layer). The epistemic layer is the Epistemic Network (EN). The operational layer is a standard Bayesian Network (BN). They are connected by a projection function, \u03C0, that translates epistemic assessments into operational parameters."));

C.push(p("This paper describes the architecture, defines its terminology, explains the formal properties of its components, and works through detailed examples showing how the system produces different \u2014 and more informative \u2014 outputs than either layer could produce alone."));

C.push(h2("1.1 Why Two Layers?"));

C.push(p("The two layers exist because the world contains two fundamentally different kinds of uncertainty, and collapsing them into one representation loses information that architects need."));

C.push(pr([
  { text: "Aleatory uncertainty ", bold: true },
  { text: "concerns the inherent variability of outcomes. Even in a perfectly understood system, different people respond differently to daylight, noise, spatial complexity, and thermal conditions. This variability is irreducible \u2014 it is a feature of the world, not a feature of our ignorance. It is properly represented by probability distributions, and it is what Bayesian Networks handle beautifully. The BN\u2019s Conditional Probability Tables (CPTs) encode this variability: P(mood = positive | daylight = high) = 0.72 means that 72% of people in this context will report positive mood under high daylight. The remaining 28% will not, and no amount of additional research will change this." }
]));

C.push(pr([
  { text: "Epistemic uncertainty ", bold: true },
  { text: "concerns our ignorance about the causal structure itself. Is daylight really a cause of mood, or is the correlation confounded by some unmeasured factor? Does the relationship hold in Indian as well as Scandinavian populations? Is the effect mediated by serotonin or by some other pathway? Will the relationship transfer from a laboratory with controlled conditions to a hospital with variable conditions? This uncertainty is reducible \u2014 new evidence can resolve it \u2014 and its magnitude depends on the quality, character, and population scope of existing evidence. It is this uncertainty that the Epistemic Network encodes." }
]));

C.push(p("The standard approach in applied science is to collapse both kinds of uncertainty into a single representation: a probability distribution that reflects both our ignorance and the world\u2019s variability. This is what Bayesian model averaging does, and it is what Judea Pearl\u2019s Structural Causal Model (SCM) framework does when it represents uncertainty as error terms in structural equations. For many purposes, this collapse is harmless. But for the specific problem of cross-context transfer \u2014 taking a finding from one context and applying it in another \u2014 the collapse is actively harmful, because it prevents the system from distinguishing between claims that are uncertain because the world is noisy and claims that are uncertain because the evidence is weak. The architect needs to know: is this 0.72 probability a reliable estimate of a noisy phenomenon, or might it be wildly wrong in a new context? Only the two-layer architecture can answer this question (Der Kiureghian & Ditlevsen, 2009)."));

C.push(PB());

// ===== 2. THE EPISTEMIC NETWORK =====
C.push(h1("2. The Epistemic Network (EN)"));

C.push(h2("2.1 What It Is"));

C.push(p("The Epistemic Network is a labeled directed multigraph W = (N, E, \u03C4, \u03C9, pop) in which:"));

C.push(pr([
  { text: "Nodes (N) ", bold: true },
  { text: "are propositions about environment-behavior relationships. Each node is a claim that can be true or false, well-supported or poorly-supported. Examples: \u201CDaylight exposure elevates serotonin production,\u201D \u201CFractal complexity in facades reduces cortical prediction error,\u201D \u201COpen-plan offices decrease focused work performance.\u201D Unlike BN nodes, which are random variables taking values, EN nodes are statements about the world." }
]));

C.push(pr([
  { text: "Edges (E) ", bold: true },
  { text: "are directed connections representing evidential support. An edge from node A to node B means: \u201CThis specific piece of evidence bears on the claim at B.\u201D The EN permits multiple edges between the same pair of nodes (parallel edges representing different lines of evidence) and directed cycles (representing mutual epistemic support). Each edge carries three annotations: a warrant type \u03C4, a warrant strength \u03C9, and population metadata pop." }
]));

C.push(pr([
  { text: "Warrant type (\u03C4) ", bold: true },
  { text: "classifies the kind of evidential bridge the edge represents. There are seven canonical types (Section 3), ranging from CONSTITUTIVE (the evidence is a definitional identity) to THEORY_DERIVED (the evidence is a prediction from a named theoretical framework). The warrant type determines the transfer reliability (discount factor d) \u2014 how much of the evidence survives when transferred to a new context." }
]));

C.push(pr([
  { text: "Warrant strength (\u03C9) ", bold: true },
  { text: "is the degree of belief in the evidential bridge, expressed as a number in (0, 1). High \u03C9 (e.g., 0.90) means the evidence is strong, well-replicated, and methodologically sound. Low \u03C9 (e.g., 0.35) means the evidence is preliminary, contested, or methodologically weak. Warrant strength is NOT a probability of an outcome. It is a meta-level judgment about evidence quality." }
]));

C.push(pr([
  { text: "Population metadata (pop) ", bold: true },
  { text: "records who was studied: sample size, mean age and variance, culture/country, WEIRD index, neurodiversity inclusion, socioeconomic profile, and any other relevant demographics. This metadata is used by the projection function \u03C0 to compute the population transfer factor \u03B4 when projecting to a specific target context." }
]));

C.push(h2("2.2 What It Is Not"));

C.push(pr([
  { text: "The EN is not a Bayesian Network. ", bold: true },
  { text: "It permits cycles, parallel edges, and typed edges \u2014 none of which BNs allow. It does not satisfy the Markov condition (the conditional independence structure that defines a BN does not apply, because EN edges represent evidential support, not probabilistic dependence). The update rule for \u03C9 when new evidence arrives is not necessarily Bayesian conditionalization \u2014 it may involve qualitative judgments about evidence quality that do not reduce to likelihood ratios." }
]));

C.push(pr([
  { text: "The EN is better described as a coherentist epistemic structure, ", bold: true },
  { text: "following Quine\u2019s (1951) web of belief and its modern formalization in coherentist epistemology (BonJour, 1985; Thagard, 2000). Claims in the EN support each other in a network; there is no foundational layer of incorrigible evidence. A mechanistic claim supports and is supported by empirical observations, theoretical predictions, and analogical extensions. The overall coherence of the network determines the degree of belief in each claim." }
]));

C.push(p("The EN is Bayesian in one narrow sense: the warrant strength \u03C9 can be interpreted as a subjective probability (a degree of belief in the proposition that the evidential bridge holds), which is a concept from the Bayesian tradition of de Finetti (1937) and Ramsey (1926). But the structure that relates these degrees of belief is coherentist, not Bayesian."));

C.push(PB());

// ===== 3. THE SEVEN WARRANT TYPES =====
C.push(h1("3. The Seven Warrant Types"));

C.push(p("Each warrant type captures a distinct epistemic relationship between evidence and claim. They are ordered by expected transfer reliability \u2014 technically, by the expected invariance range of the evidential bridge under contextual perturbation (Woodward, 2003). The transfer reliability (discount factor d) is set by the type, not by any individual study. It represents a structural property of the kind of evidence, not a judgment about specific evidence quality (which is what \u03C9 captures)."));

// Type 1
C.push(h2("3.1 CONSTITUTIVE (d = 0.95)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "An identity or definitional relationship. The laboratory variable IS the architectural variable, by definition. This is not a causal claim but a conceptual truth grounded in mereology (the logic of parts and wholes) and Wittgenstein\u2019s criterial relations." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Maximally invariant. Transfers to any context where the definitions hold. Cannot be confounded (you cannot confound an identity)." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Window-to-wall ratio IS glazed area divided by wall area. Ceiling height IS room volume divided by floor area. These hold in every building, in every culture, under every intervention, by definition." }
]));
C.push(pr([
  { text: "Why d = 0.95, not 1.0: ", bold: true },
  { text: "Even definitional relationships can have edge cases (does \u201Cwindow\u201D include skylights? translucent panels?). The small discount accommodates definitional ambiguity." }
]));

// Type 2
C.push(h2("3.2 MECHANISM (d = 0.80)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "A known causal pathway with identified entities and activities (Machamer, Darden, & Craver, 2000). We know not just THAT A causes C but WHY and HOW: through a specific chain of intermediate processes that can be described, intervened on, and potentially disrupted." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "High invariance. Transfers to any context where the mechanistic chain is intact. Fails only when a specific link in the chain is disrupted. Provides precise guidance for Pearl\u2019s S-node placement in transportability analysis." }
]));
C.push(pr([
  { text: "The accordion principle: ", bold: true },
  { text: "Mechanisms can be described at multiple levels of granularity. Early research may establish a coarse mechanism (\u201Clight increases serotonin, somehow\u201D); later work elaborates intermediate steps (retinal ganglion cells \u2192 retinohypothalamic tract \u2192 raphe nuclei \u2192 tryptophan hydroxylase). The warrant type stays MECHANISM at every granularity level, but the warrant strength \u03C9 increases as the mechanism is elaborated. A coarsely described mechanism might get \u03C9 = 0.60; a finely described mechanism, \u03C9 = 0.90. The accordion changes \u03C9, not \u03C4." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Daylight exposure \u2192 retinal ganglion cells \u2192 retinohypothalamic tract \u2192 raphe nuclei \u2192 tryptophan hydroxylase \u2192 serotonin production (Lambert et al., 2002). Each entity and activity in the chain is identified." }
]));

// Type 3
C.push(h2("3.3 EMPIRICAL_ASSOCIATION (d = 0.80)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "A replicated statistical association without known mechanism. We know THAT A correlates with C \u2014 the association has been observed across multiple studies \u2014 but we do not know WHY. The mediating pathway is unidentified." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Moderate invariance with a specific vulnerability. The association is robust across observed contexts (that\u2019s what replication means), but because the mechanism is unknown, we cannot predict which background changes will disrupt it. Vulnerable to confounding: any unmeasured common cause could explain the association. S-node placement is uncertain because the mediating pathway is unknown." }
]));
C.push(pr([
  { text: "Note on naming: ", bold: true },
  { text: "Previously called EMPIRICAL_COVARIANCE. Renamed to EMPIRICAL_ASSOCIATION because \u201Cassociation\u201D is the epidemiological term of art for a replicated relationship where causation is not claimed, and it is more intuitive for non-statisticians than \u201Ccovariance.\u201D" }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Hospitals with more natural light show faster patient recovery (Beauchemin & Hays, 1996; Walch et al., 2005). The association replicates, but whether it is mediated by serotonin, vitamin D, circadian regulation, patient mood, or staff behavior is unclear." }
]));

// Type 4
C.push(h2("3.4 FUNCTIONAL (d = 0.65)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "Evidence that a system performs a specific functional role (Putnam, 1967; Block, 1980), without a known mechanism implementing that function. We know WHAT the system does but not HOW it does it." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Intermediate invariance. If the system reliably performs the function across observed contexts, there is reason to believe it will do so in new contexts. But without mechanistic understanding, we cannot predict when the function will fail." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Natural elements in offices \u201Cserve as stress reducers\u201D (Kaplan, 1995). The functional claim is supported empirically \u2014 nature exposure reliably reduces stress markers \u2014 but the underlying mechanism (attention restoration? autonomic regulation? evolutionary preference?) is debated." }
]));

// Type 5
C.push(h2("3.5 CAPACITY (d = 0.55)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "Evidence that a system CAN produce an effect, based on the system\u2019s known capacities (Cartwright, 1989), without evidence that it DOES produce the effect in the relevant context. Asserts possibility, not actuality." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Low-to-moderate invariance. The capacity is a real property of the system, but exercising a capacity requires triggering conditions that may or may not be present in the target context." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Human auditory cortex can discriminate reverberation times (demonstrated in controlled psychoacoustic experiments). Therefore room acoustics COULD affect perceived spaciousness. But nobody has shown this connection in an actual building \u2014 the capacity exists, but its exercise in situ is undemonstrated." }
]));

// Type 6
C.push(h2("3.6 ANALOGICAL (d = 0.40)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "Cross-domain transfer via structural similarity (Gentner, 1983; Holyoak & Thagard, 1995; Bartha, 2010). Evidence from domain X is applied to domain Y because the two domains share relevant structural features." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Low invariance. Analogical transfer is notoriously sensitive to surface features that mask deep structural differences. The invariance range is the set of contexts sharing the relevant structural features with the source domain \u2014 a set that is itself uncertain." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Fractal patterns reduce stress in natural landscapes (H\u00E4gerh\u00E4ll et al., 2004). By analogy, fractal patterns in building facades should reduce stress, since both involve visual processing of scale-invariant structure. The analogy is plausible but the structural similarity has not been verified." }
]));

// Type 7
C.push(h2("3.7 THEORY_DERIVED [theory name] (d = 0.25)"));
C.push(pr([
  { text: "Definition: ", bold: true },
  { text: "A prediction derived from a named theoretical framework, without direct empirical confirmation. The claim follows logically from the theory but has not been independently tested. Each THEORY_DERIVED edge carries an explicit theory tag identifying the framework from which it is derived." }
]));
C.push(pr([
  { text: "Transfer property: ", bold: true },
  { text: "Minimal invariance. The prediction holds only to the extent that the theory is correct in this domain. Since theories are underdetermined by evidence and may fail in new domains, the transfer reliability is low." }
]));
C.push(pr([
  { text: "Why the theory tag matters: ", bold: true },
  { text: "Three reasons. First, auditability: every claim traces to a named theory. Second, update propagation: if the theory is challenged, all edges presupposing it can be queried and updated as a class. Third, theory comparison: competing theories (e.g., predictive processing vs. attention restoration theory) generate parallel THEORY_DERIVED edges with different tags, and the EN can track which theory accumulates more empirical support over time." }
]));
C.push(pr([
  { text: "Note on naming: ", bold: true },
  { text: "Previously called THEORETICAL_DEFAULT. Renamed because \u201Cdefault\u201D implies a fallback or shrug, whereas these edges represent substantive theoretical commitments that do real intellectual work. \u201CTHEORY_DERIVED\u201D names the epistemic status: a prediction derived from a specific theory, awaiting empirical confirmation." }
]));
C.push(pr([
  { text: "Example: ", bold: true },
  { text: "Predictive processing theory (Friston, 2010; Clark, 2013) predicts that moderately complex facades should minimize cortical prediction error, yielding aesthetic preference. Warrant type: THEORY_DERIVED [Predictive Processing], \u03C9 = 0.40." }
]));

C.push(PB());

// ===== 4. THE THREE NUMBERS =====
C.push(h1("4. The Three Numbers: Warrant Strength, Transfer Reliability, and Conditional Probability"));

C.push(p("The single most important thing to understand about the ATLAS architecture is that there are three categorically different kinds of number. They answer different questions, encode different kinds of uncertainty, and live in different layers of the system. Confusing them produces nonsense."));

C.push(h2("4.1 Warrant Strength (\u03C9)"));
C.push(pr([
  { text: "Lives in: ", bold: true },
  { text: "the Epistemic Network, on each edge." }
]));
C.push(pr([
  { text: "Measures: ", bold: true },
  { text: "how well-supported this specific piece of evidence is. Is the study well-designed? Has it been replicated? Is the methodology sound? Is the sample adequate?" }
]));
C.push(pr([
  { text: "Kind of uncertainty: ", bold: true },
  { text: "EPISTEMIC. Reducible by gathering more or better evidence. A low \u03C9 means we need more studies." }
]));
C.push(pr([
  { text: "What \u03C9 = 0.80 means: ", bold: true },
  { text: "\u201CWe are quite confident this evidence is solid.\u201D (Strong studies, good replication, sound methodology.)" }
]));
C.push(pr([
  { text: "Prose term: ", bold: true },
  { text: "\u201CDegree of belief in the evidential bridge.\u201D" }
]));

C.push(h2("4.2 Transfer Reliability (d)"));
C.push(pr([
  { text: "Lives in: ", bold: true },
  { text: "the projection bridge, determined by the warrant type \u03C4." }
]));
C.push(pr([
  { text: "Measures: ", bold: true },
  { text: "how much of any evidence of this TYPE survives transfer to a new context. This is a structural property of the evidence type, not a judgment about specific evidence." }
]));
C.push(pr([
  { text: "Kind of uncertainty: ", bold: true },
  { text: "EPISTEMIC. Reflects the expected invariance range of the evidence type (Woodward, 2003)." }
]));
C.push(pr([
  { text: "What d = 0.80 means: ", bold: true },
  { text: "\u201CThis type of evidence retains 80% of its information when transferred to a new context.\u201D (E.g., MECHANISM \u2014 mechanistic knowledge is robust to contextual perturbation.)" }
]));
C.push(pr([
  { text: "Prose term: ", bold: true },
  { text: "\u201CTransfer reliability.\u201D" }
]));

C.push(h2("4.3 Conditional Probability (CPT)"));
C.push(pr([
  { text: "Lives in: ", bold: true },
  { text: "the Bayesian Network, on each edge." }
]));
C.push(pr([
  { text: "Full name: ", bold: true },
  { text: "Conditional Probability Table. Written P(X | Pa(X)). For each configuration of parent variable values, a probability distribution over X\u2019s values. Each column sums to 1.0." }
]));
C.push(pr([
  { text: "Measures: ", bold: true },
  { text: "what actually happens in the world. Given these inputs, what is the probability of each outcome?" }
]));
C.push(pr([
  { text: "Kind of uncertainty: ", bold: true },
  { text: "ALEATORY. Irreducible randomness in how people respond. Even a perfectly known mechanism produces variable outcomes across individuals." }
]));
C.push(pr([
  { text: "What CPT = 0.80 means: ", bold: true },
  { text: "\u201CThere is an 80% chance of this outcome given these inputs.\u201D (E.g., P(serotonin = elevated | daylight = high) = 0.80.)" }
]));
C.push(pr([
  { text: "Prose term: ", bold: true },
  { text: "\u201CProbability of outcome given inputs.\u201D" }
]));

C.push(h2("4.4 How They Work Together"));
C.push(p("The warrant strength \u03C9 tells you how good the evidence is. The transfer reliability d tells you how much of that type of evidence survives transfer. The CPT tells you what the evidence predicts will happen. The projection function \u03C0 uses \u03C9 and d to compute the CPT:"));
C.push(p("logit(p_target) = d(\u03C4) \u00B7 \u03C9 \u00B7 \u03B4(pop, pop_target) \u00B7 logit(p_lab)", { noIndent: true, b: true }));
C.push(p("where \u03B4 is the population transfer factor (Section 8). Three multiplicative attenuation factors, each doing different work, each encoding a different source of epistemic uncertainty. The result is converted back from log-odds to probability via the sigmoid function to produce the BN\u2019s CPT entry."));

C.push(PB());

// ===== 5. COMBINATION RULES =====
C.push(h1("5. How Evidence Combines: Serial and Parallel Paths"));

C.push(p("The EN frequently contains complex topologies: chains of evidence running through intermediate nodes, multiple lines of evidence converging on a single claim, and combinations of both. The way evidence combines depends on whether the paths are serial or parallel."));

C.push(h2("5.1 Serial Combination (Chains)"));
C.push(pr([
  { text: "Rule: Minimum-discount composition. ", bold: true },
  { text: "For a chain of edges e\u2081, e\u2082, ..., e\u2096, the effective transfer reliability is d_eff = min(d(\u03C4(e\u2081)), d(\u03C4(e\u2082)), ..., d(\u03C4(e\u2096))). The weakest link dominates." }
]));
C.push(p("This is the conservative choice. It prevents the system from claiming stronger evidence than the weakest step supports. If a four-link chain has three MECHANISM links (d = 0.80) and one THEORY_DERIVED link (d = 0.25), the effective transfer reliability is 0.25. The theoretical link is the bottleneck."));
C.push(pr([
  { text: "When it applies: ", bold: true },
  { text: "When inferring through intermediate states that are not independently established. The chain\u2019s reliability cannot exceed the reliability of its least reliable link." }
]));
C.push(pr([
  { text: "Graph-theoretic connection: ", bold: true },
  { text: "This is the classical widest-path (bottleneck shortest path) problem (Pollack, 1960), solvable in O(E log V) via a Dijkstra variant." }
]));

C.push(h2("5.2 Parallel Combination (Convergent Evidence)"));
C.push(pr([
  { text: "Rule: Additive in log-odds. ", bold: true },
  { text: "When multiple independent lines of evidence support the same claim, their contributions sum: Total = \u03A3 d_i \u00B7 \u03C9_i \u00B7 logit(p_i). More evidence = higher confidence." }
]));
C.push(p("This follows from the standard Bayesian result for combining independent evidence (Jaynes, 2003, Ch. 4). Each line of evidence contributes an independent log-odds increment. The total is converted back to probability via the sigmoid function. Parallel evidence always increases confidence; it can never decrease it."));
C.push(pr([
  { text: "When it applies: ", bold: true },
  { text: "When multiple independent sources converge on the same claim. A claim supported by both a MECHANISM edge and an EMPIRICAL_ASSOCIATION edge has two independent lines of evidence; they combine additively." }
]));

C.push(h2("5.3 The Explanatory Boost: Why Mechanism + Association > Association Alone"));
C.push(p("There is a natural question: if I have an empirical association and then I discover the mechanism behind it, does confidence go up or down? The answer is unambiguously up, and here is why."));
C.push(p("When a mechanism is discovered that explains an existing empirical association, three things happen in the EN:"));
C.push(pr([
  { text: "First, the original EMPIRICAL_ASSOCIATION edge stays. ", bold: true },
  { text: "The correlation has been observed and replicated. It stands as its own line of evidence." }
]));
C.push(pr([
  { text: "Second, a new MECHANISM path is added in parallel ", bold: true },
  { text: "\u2014 a parallel route through intermediate nodes explaining WHY the association exists. This path has its own warrant type and strength." }
]));
C.push(pr([
  { text: "Third, the original edge\u2019s warrant strength \u03C9 goes up. ", bold: true },
  { text: "When an empirical association receives a mechanistic explanation, the association itself becomes more trustworthy because we now have a reason to believe the correlation is not confounded. The mechanism explains the association, reducing the probability that it is spurious." }
]));
C.push(pr([
  { text: "Fourth, the two lines of evidence combine additively ", bold: true },
  { text: "through the projection. The BN edge now gets contributions from both the empirical association and the mechanistic path, producing a higher CPT value than either alone." }
]));
C.push(p("The car mechanic principle illustrates this concretely. A mechanic who has replaced twenty carburetors and fixed the stalling problem every time has strong EMPIRICAL_ASSOCIATION evidence (d = 0.80, \u03C9 = 0.70). A theorist who knows combustion chemistry but has never touched a car has THEORY_DERIVED evidence (d = 0.25, \u03C9 = 0.80). The mechanic is more confident than the theorist \u2014 empirical evidence outperforms theory without data. But the mechanic who also understands the theory outperforms both, because the theoretical understanding provides a second, parallel line of evidence AND increases \u03C9 on the empirical edge by explaining why the fix works (gas/oxygen ratio \u2192 combustion efficiency \u2192 engine performance). Explanation adds to empirical evidence; it never subtracts."));
C.push(p("This resolves a potential paradox: a chain that runs through THEORY_DERIVED links (d = 0.25) should not produce less confidence than an empirical association alone (d = 0.80). And it does not, if the topology is correct. Theory that serves as the ONLY bridge between disconnected empirical findings (serial chain) correctly gets the minimum discount. Theory that EXPLAINS an existing empirical finding (parallel support) correctly boosts the combined confidence."));

C.push(PB());

// ===== 6. DUAL BN DIAGNOSTIC =====
C.push(h1("6. The Dual-BN Diagnostic: Full Projection vs. Empirical Floor"));

C.push(p("For every BN edge that \u03C0 produces by collapsing an EN path, the system computes and stores three diagnostics:"));

C.push(h2("6.1 Full Projection"));
C.push(p("The standard computation using all links in the chain, including THEORY_DERIVED links. This is the system\u2019s best estimate, because theoretical evidence, even though weak, is better than no evidence. This is what goes into the BN\u2019s CPT and what the architect uses for decision-making."));

C.push(h2("6.2 Empirical Floor"));
C.push(p("The projection computed using ONLY empirically grounded links: CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, and FUNCTIONAL. CAPACITY, ANALOGICAL, and THEORY_DERIVED links are removed. Two things can happen:"));
C.push(pr([
  { text: "The chain survives: ", bold: true },
  { text: "There is still a continuous path from input to output. The empirical floor gives you the confidence based purely on empirical evidence, ignoring theoretical scaffolding." }
]));
C.push(pr([
  { text: "The chain breaks: ", bold: true },
  { text: "Removing the theoretical links disconnects the path. The empirical floor equals the ignorance prior of 0.50. This is enormously informative: it means the entire claim depends on theoretical scaffolding to bridge empirically disconnected findings." }
]));

C.push(h2("6.3 Theory Dependence Diagnostic"));
C.push(p("A categorical label summarizing the gap between full projection and empirical floor:"));
C.push(pr([
  { text: "Empirically grounded: ", bold: true },
  { text: "The empirical floor is close to the full projection (ratio > 0.80). Removing theoretical links barely changes the estimate. The claim stands on its own empirical legs." }
]));
C.push(pr([
  { text: "Theory-augmented: ", bold: true },
  { text: "The empirical floor exists but is substantially lower than the full projection (ratio 0.40\u20130.80). Theory adds meaningful confidence beyond what empirical evidence alone supports." }
]));
C.push(pr([
  { text: "Theory-scaffolded [theory name]: ", bold: true },
  { text: "The empirical floor is near the ignorance prior, or the chain breaks entirely without theoretical links. The claim DEPENDS on the named theory to connect empirically established findings." }
]));

C.push(h2("6.4 The Dual-BN Option"));
C.push(p("The system can run the BN twice: once with the full projection (the theory-inclusive model) and once with only empirically grounded projections (the empirical-only model). The empirical-only BN will have fewer edges \u2014 some paths will be missing entirely. Comparing the two outputs tells the architect what the theoretical scaffolding is buying and where the empirical evidence stops."));

C.push(PB());

// ===== 7. POPULATION TRANSFER =====
C.push(h1("7. Population Transfer Factors (\u03B4)"));

C.push(p("Most findings in environmental psychology come from specific populations that may not represent the populations architects are designing for. The population transfer factor \u03B4 formalizes this concern."));

C.push(h2("7.1 The Problem"));
C.push(p("Henrich, Heine, and Norenzayan (2010) demonstrated that the vast majority of psychology findings come from WEIRD populations \u2014 Western, Educated, Industrialized, Rich, Democratic \u2014 comprising roughly 12% of the world\u2019s population. This population is systematically unusual on many psychological dimensions, including visual perception, spatial reasoning, aesthetic preference, and social cognition. Designing a hospital in rural India using evidence derived exclusively from American undergraduates is, to put it directly, epistemically reckless."));

C.push(h2("7.2 The Architecture"));
C.push(p("Every EN edge carries population metadata (pop) recording who was studied. When the projection function \u03C0 projects an edge to a specific target context, it computes a population transfer factor \u03B4(pop_source, pop_target) \u2208 (0, 1) that attenuates the projection based on the population mismatch."));
C.push(p("The full projection formula is:"));
C.push(p("logit(p_target) = d(\u03C4) \u00B7 \u03C9 \u00B7 \u03B4(pop, pop_target) \u00B7 logit(p_lab)", { noIndent: true, b: true }));
C.push(p("Three multiplicative attenuation factors in log-odds space, each encoding a different source of epistemic uncertainty:"));
C.push(pr([{ text: "d: ", bold: true }, { text: "How well does this TYPE of evidence transfer in general?" }]));
C.push(pr([{ text: "\u03C9: ", bold: true }, { text: "How good is this SPECIFIC piece of evidence?" }]));
C.push(pr([{ text: "\u03B4: ", bold: true }, { text: "How well does evidence from THIS population transfer to THAT population?" }]));

C.push(h2("7.3 Population Distance Dimensions"));
C.push(pr([{ text: "Cultural distance: ", bold: true }, { text: "How different is the target culture from the study culture? Measurable via Hofstede\u2019s dimensions, Henrich\u2019s WEIRD index, or more recent cultural psychology metrics. High cultural distance \u2192 low \u03B4." }]));
C.push(pr([{ text: "Demographic distance: ", bold: true }, { text: "How different is the target population in age, socioeconomic status, and education? Large demographic mismatch \u2192 low \u03B4." }]));
C.push(pr([{ text: "Neurodiversity scope: ", bold: true }, { text: "Was the study sample neurotypical-only? If the target population includes neurodiverse individuals, and the study excluded them, \u03B4 drops \u2014 potentially dramatically for sensory-environment relationships." }]));
C.push(pr([{ text: "Ecological validity: ", bold: true }, { text: "Lab vs. field, short vs. chronic exposure, single stimulus vs. naturalistic environment." }]));

C.push(h2("7.4 The Neurodiversity Special Case"));
C.push(p("Neurodiversity is not merely another population dimension that attenuates effects. It can reverse them. Fluorescent lighting at 120Hz flicker: neurotypical individuals typically do not perceive it; many autistic individuals find it severely aversive (Wilkins et al., 2009). Open-plan offices: neurotypical extraverts may thrive; individuals with ADHD may find them impossible. This is not attenuation \u2014 it is sign reversal."));
C.push(p("The population factor \u03B4 handles attenuation (smaller effect) but not reversal (opposite effect). For neurodiversity, the EN needs explicit moderator nodes: edges from \u201Csensory processing profile\u201D to specific environment-behavior relationships, with their own warrant types reflecting how well the moderation is established."));

C.push(h2("7.5 Implications for Non-WEIRD Contexts"));
C.push(p("For most of environmental psychology, \u03B4 will be painfully low for non-WEIRD populations. This is not a flaw in the system \u2014 it is the system honestly reporting what the evidence actually supports. The result will be a BN with weak CPTs for non-WEIRD contexts, which correctly reflects our state of knowledge. The system produces a clear research prioritization signal: \u201CFor this hospital in Ahmedabad, the EN identifies 47 edges whose population transfer factor \u03B4 < 0.50. The highest-priority research need is direct empirical studies with Indian urban populations.\u201D"));

C.push(PB());

// ===== 8. WORKED EXAMPLES =====
C.push(h1("8. Worked Examples"));

C.push(h2("8.1 The Daylight \u2192 Mood Chain (Empirically Grounded)"));
C.push(p("Claim: \u201CIncreasing window-to-wall ratio improves patient mood.\u201D Target: a new hospital in a Western city with a demographically similar population to the study samples."));
C.push(pr([{ text: "Link 1: Window ratio \u2192 Daylight. ", bold: true }, { text: "\u03C4 = CONSTITUTIVE, \u03C9 = 0.95, d = 0.95. Larger windows admit more light by definition of fenestration. Holds in every building with transparent glazing." }], { sb: 160 }));
C.push(pr([{ text: "Link 2: Daylight \u2192 Serotonin. ", bold: true }, { text: "\u03C4 = MECHANISM, \u03C9 = 0.85, d = 0.80. Lambert et al. (2002) identified the specific neurochemical pathway: bright light stimulates retinal ganglion cells projecting via the retinohypothalamic tract to the raphe nuclei, increasing tryptophan hydroxylase activity and serotonin turnover." }], { sb: 160 }));
C.push(pr([{ text: "Link 3: Serotonin \u2192 Mood. ", bold: true }, { text: "\u03C4 = MECHANISM, \u03C9 = 0.80, d = 0.80. The serotonergic system\u2019s role in mood regulation is well-established through the pharmacological literature (Aan het Rot et al., 2009). SSRIs work by increasing serotonin availability." }], { sb: 160 }));
C.push(p("Serial combination: d_eff = min(0.95, 0.80, 0.80) = 0.80."));
C.push(p("Population factor: \u03B4 \u2248 0.90 (Western city, similar demographics)."));
C.push(p("Full projection: P(mood = positive | windows = large) \u2248 0.74."));
C.push(p("Empirical floor: All links empirically grounded. Floor = 0.74. Identical."));
C.push(p("Diagnostic: Empirically grounded.", { b: true }));

C.push(h2("8.2 The Fractal \u2192 Wellbeing Chain (Theory-Scaffolded)"));
C.push(p("Claim: \u201CFractal facades improve occupant wellbeing.\u201D Target: same hospital."));
C.push(pr([{ text: "Link 1: Fractal patterns \u2192 Cortical response. ", bold: true }, { text: "\u03C4 = MECHANISM, \u03C9 = 0.75, d = 0.80. H\u00E4gerh\u00E4ll et al. (2008) showed using EEG that viewing fractal patterns in the D = 1.3 range produces distinct alpha-band activity. Note: EEG is the measurement instrument, not part of the mechanism. The mechanism is: retinal processing of scale-invariant structure \u2192 specific cortical activation patterns." }], { sb: 160 }));
C.push(pr([{ text: "Link 2: Cortical response \u2192 Prediction error. ", bold: true }, { text: "\u03C4 = THEORY_DERIVED [Predictive Processing], \u03C9 = 0.45, d = 0.25. Predictive processing theory proposes that cortical hierarchies compute prediction error. Scale-invariant stimuli should produce low prediction error because their statistical structure is consistent across spatial scales. But this is an interpretation \u2014 nobody has directly measured \u2018prediction error\u2019 as a neural quantity in response to architectural fractals." }], { sb: 160 }));
C.push(pr([{ text: "Link 3: Prediction error \u2192 Stress reduction. ", bold: true }, { text: "\u03C4 = THEORY_DERIVED [Predictive Processing], \u03C9 = 0.40, d = 0.25. The theory proposes that high prediction error triggers arousal; low prediction error reduces stress. Some general evidence supports this framework (Barrett, 2017), but the specific link from visual prediction error to stress physiology in architectural contexts is largely theoretical." }], { sb: 160 }));
C.push(pr([{ text: "Link 4: Stress reduction \u2192 Wellbeing. ", bold: true }, { text: "\u03C4 = EMPIRICAL_ASSOCIATION, \u03C9 = 0.70, d = 0.80. The association between lower chronic stress markers and better self-reported wellbeing is well-established in health psychology (Cohen et al., 2007)." }], { sb: 160 }));
C.push(p("Serial combination: d_eff = min(0.80, 0.25, 0.25, 0.80) = 0.25."));
C.push(p("Full projection: P(wellbeing = high | fractal_D = 1.3) \u2248 0.58."));
C.push(p("Empirical floor: Remove Links 2 and 3 (THEORY_DERIVED). Chain BREAKS \u2014 no empirical path from cortical response to stress reduction. Floor = 0.50 (ignorance prior)."));
C.push(p("Diagnostic: Theory-scaffolded [Predictive Processing].", { b: true }));
C.push(p("Research recommendation: The highest-value investment is an experiment testing whether the cortical response to architectural fractals reflects prediction error (upgrading Link 2 from THEORY_DERIVED to MECHANISM or EMPIRICAL_ASSOCIATION) and whether that response predicts stress outcomes (upgrading Link 3)."));

C.push(h2("8.3 What the BN Loses"));
C.push(p("For the daylight chain, the BN says: \u201CLarger windows improve mood (P = 0.74).\u201D For the fractal chain, the BN says: \u201CFractal facades slightly improve wellbeing (P = 0.58).\u201D Both are single numbers. The BN cannot tell you:"));
C.push(p("\u2014 That the daylight claim is empirically grounded while the fractal claim is theory-scaffolded"));
C.push(p("\u2014 That the fractal chain\u2019s weakness is localized to two specific links in the middle"));
C.push(p("\u2014 That those links presuppose predictive processing theory specifically"));
C.push(p("\u2014 That a single targeted experiment could dramatically strengthen the fractal claim"));
C.push(p("\u2014 That the daylight claim would transfer well to non-WEIRD populations (\u03B4 = 0.75, mechanism is biological) while the fractal claim might not (\u03B4 = 0.50, aesthetic preferences are culturally variable)"));
C.push(p("The EN preserves all of this information. The BN collapses it into single numbers. The projection function \u03C0 is the responsible compression that produces the BN\u2019s numbers while the EN retains the full epistemic record for audit, explanation, research prioritization, and context-specific re-projection."));

C.push(PB());

// ===== REFERENCES =====
C.push(h1("9. References"));

const refs = [
  "Aan het Rot, M., Mathew, S. J., & Bhagwagar, Z. (2009). Neurobiological mechanisms in major depressive disorder. CMAJ, 180(3), 305\u2013313.",
  "Bareinboim, E., & Pearl, J. (2016). Causal inference and the data-fusion problem. Proceedings of the National Academy of Sciences, 113(27), 7345\u20137352.",
  "Barrett, L. F. (2017). How emotions are made: The secret life of the brain. Houghton Mifflin Harcourt.",
  "Bartha, P. (2010). By parallel reasoning: The construction and evaluation of analogical arguments. Oxford University Press.",
  "Beauchemin, K. M., & Hays, P. (1996). Sunny hospital rooms expedite recovery from severe and refractory depressions. Journal of Affective Disorders, 40(1\u20132), 49\u201351.",
  "Block, N. (1980). Troubles with functionalism. In N. Block (Ed.), Readings in philosophy of psychology (Vol. 1, pp. 268\u2013305). Harvard University Press.",
  "BonJour, L. (1985). The structure of empirical knowledge. Harvard University Press.",
  "Cartwright, N. (1989). Nature\u2019s capacities and their measurement. Oxford University Press.",
  "Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. Behavioral and Brain Sciences, 36(3), 181\u2013204.",
  "Cohen, S., Janicki-Deverts, D., & Miller, G. E. (2007). Psychological stress and disease. JAMA, 298(14), 1685\u20131687.",
  "de Finetti, B. (1937). La pr\u00E9vision: Ses lois logiques, ses sources subjectives. Annales de l\u2019Institut Henri Poincar\u00E9, 7(1), 1\u201368.",
  "Der Kiureghian, A., & Ditlevsen, O. (2009). Aleatory or epistemic? Does it matter? Structural Safety, 31(2), 105\u2013112.",
  "Friston, K. (2010). The free-energy principle: A unified brain theory? Nature Reviews Neuroscience, 11(2), 127\u2013138.",
  "Gentner, D. (1983). Structure-mapping: A theoretical framework for analogy. Cognitive Science, 7(2), 155\u2013170.",
  "H\u00E4gerh\u00E4ll, C. M., Laike, T., Taylor, R. P., K\u00FCller, M., K\u00FCller, R., & Martin, T. P. (2008). Investigations of human EEG response to viewing fractal patterns. Perception, 37(10), 1488\u20131494.",
  "Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The weirdest people in the world? Behavioral and Brain Sciences, 33(2\u20133), 61\u201383.",
  "Holyoak, K. J., & Thagard, P. (1995). Mental leaps: Analogy in creative thought. MIT Press.",
  "Jaynes, E. T. (2003). Probability theory: The logic of science. Cambridge University Press.",
  "Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. Journal of Environmental Psychology, 15(3), 169\u2013182.",
  "Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D. (2002). Effect of sunlight and season on serotonin turnover in the brain. The Lancet, 360(9348), 1840\u20131842.",
  "Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. Philosophy of Science, 67(1), 1\u201325.",
  "Marr, D. (1982). Vision: A computational investigation into the human representation and processing of visual information. W. H. Freeman.",
  "Pearl, J. (2009). Causality: Models, reasoning, and inference (2nd ed.). Cambridge University Press.",
  "Pearl, J., & Bareinboim, E. (2011). Transportability of causal and statistical relations: A formal approach. In Proceedings of the 25th AAAI Conference on Artificial Intelligence (pp. 247\u2013254).",
  "Pollack, M. (1960). The maximum capacity through a network. Operations Research, 8(5), 733\u2013736.",
  "Putnam, H. (1967). Psychological predicates. In W. H. Capitan & D. D. Merrill (Eds.), Art, mind, and religion (pp. 37\u201348). University of Pittsburgh Press.",
  "Quine, W. V. O. (1951). Two dogmas of empiricism. The Philosophical Review, 60(1), 20\u201343.",
  "Ramsey, F. P. (1926). Truth and probability. In R. B. Braithwaite (Ed.), The foundations of mathematics and other logical essays (1931, pp. 156\u2013198). Routledge.",
  "Thagard, P. (2000). Coherence in thought and action. MIT Press.",
  "Walch, J. M., Rabin, B. S., Day, R., Williams, J. N., Choi, K., & Kang, J. D. (2005). The effect of sunlight on postoperative analgesic medication use. Psychosomatic Medicine, 67(1), 156\u2013163.",
  "Wilkins, A. J., Veitch, J., & Lehman, B. (2009). LED lighting flicker and potential health concerns: IEEE standard PAR1789 update. In Proceedings of the IEEE Energy Conversion Congress and Exposition.",
  "Woodward, J. (2003). Making things happen: A theory of causal explanation. Oxford University Press."
];

refs.forEach(ref => {
  C.push(new Paragraph({
    spacing: { before: 50, after: 50, line: 260 },
    indent: { left: 720, hanging: 720 },
    children: [new TextRun({ text: ref, font: "Georgia", size: 21 })]
  }));
});

// ===== BUILD DOCUMENT =====
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Georgia", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Georgia" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Georgia" },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Georgia" },
        paragraph: { spacing: { before: 260, after: 120 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "ATLAS Epistemic Network \u2014 Architecture & Properties \u2014 p. ", font: "Georgia", size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Georgia", size: 18, color: "888888" })
          ]
        })]
      })
    },
    children: C
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = '/mnt/user-data/outputs/02-27_05_ATLAS_EN_Master_Report_V1.0.docx';
  fs.writeFileSync(outPath, buffer);
  console.log('Written:', outPath, '(' + Math.round(buffer.length/1024) + ' KB)');
});
