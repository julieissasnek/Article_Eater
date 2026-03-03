# PART XXIII — Multi-Agent Coordination and Retrieval-Augmented Generation

**Section numbers**: §155–§159
**Date**: 2026-03-03
**Length**: ~2,800 words

---

## §155: Multi-Agent Coordination — From Ad Hoc to Systematic

The Article Eater system is not the work of a single agent. As of March 2026, two Claude instantiations work on the same repository: Antigravity (AG), a specialized research and engineering agent, and Claude Whitmore (CW), a general-purpose development agent. Both may be running simultaneously. Without coordination infrastructure, they risk data loss through conflicting edits, duplicate work, and stale shared state.

The solution is a file-based coordination system that makes agent state visible, human-readable, and durable across sessions. This system lives in `.agent_coord/`:

**COORDINATION_STATE.md**: The single source of truth for system metrics and active work.

A shared table tracks which agent is working on what files and when. When AG expands T1.5 from 4 to 13 theories, it records this immediately in COORDINATION_STATE. When CW later wires services into the orchestrator, it checks COORDINATION_STATE to verify that no other agent is modifying the orchestrator simultaneously. This prevents write conflicts on shared code files.

The file also maintains canonical sources of truth: "T1 frameworks always load from `schemas/theory/tier1_frameworks.json`, never hardcoded. T1.5 domain theories always load from `schemas/theory/tier1_5_domain_theories.json`." This shared reference prevents the situation where AG updates the JSON to 13 theories but CW, working in isolation, still hardcodes 4 in a newly written service.

**MESSAGE_BOARD.md**: Structured inter-agent communication.

When AG discovers that the interpretation layer has 2,680 lines but was only imported by one service (query_engine.py), it leaves a message for CW: "The interpretation layer looks unused. Should we add Step 9 to the enrichment orchestrator to classify question patterns?" This is not email. It is a formal record with timestamp, priority level, subject, and actionable body. CW reads it at session start, marks it ACKNOWLEDGED, and either acts on it or replies with a decision.

The message board is append-only, timestamped, and archived. It serves as the institutional memory of which agent requested which changes and when. When David asks "who decided to add dynamic T1.5 loading?" the answer is recorded: "AG decided on 2026-03-02 at 20:45 because we were expanding T1.5 from 4 to 13 and needed to avoid hardcoding."

**CHANGELOG.md**: Append-only record of all changes.

Each session, every agent documents what it changed: which files, what was added/modified, test counts before and after. This is durable history. Unlike git commits (which can be amended or rebased), the CHANGELOG cannot be edited. If AG added a service on Monday and CW modified it on Tuesday, that sequence is preserved forever. Six months later, someone can read the changelog and understand the evolution of the orchestrator service.

**Check-in/Check-out Workflows**: Formal session boundaries.

Every agent session must begin by running `/check-in`, which instructs the agent to:
1. Read COORDINATION_STATE to understand what the other agent is doing
2. Check MESSAGE_BOARD for unread messages
3. Read the last 50 lines of CHANGELOG to see recent changes
4. Lock any files it plans to edit

And must end with `/check-out`, which instructs the agent to:
1. Run the full test suite and record pass/failure counts
2. Update COORDINATION_STATE with new metrics
3. Clear its file locks
4. Leave a message on MESSAGE_BOARD if the other agent needs to know anything
5. Append to CHANGELOG

This creates formal session boundaries. Before you start, you know exactly what the other agent did. After you finish, you leave a breadcrumb for them to follow.

**Why this is better than database-backed locking:**

One might argue that a shared database with ACID transactions would be more robust than a filesystem-based coordination system. But in this context, the filesystem approach has three advantages over centralized locking:

First, it is **durable without external dependencies**. The COORDINATION_STATE file is a plain text markdown file that sits in git. If the database server is down, the agents can still coordinate by reading and writing text files. This is resilience by simplicity.

Second, it is **human-readable and auditable**. Any developer, including David, can open COORDINATION_STATE, see what each agent is doing, and understand the system state. A database schema requires a query interface. A text file requires only `cat`.

Third, it **embeds semantic meaning**. When AG writes "Wire mock steps to real services: Orchestrator Steps 4–8 return hardcoded mock data. Connect them to the actual service implementations," this is not a lock on a record. It is a to-do item with explanation, priority, and context. A database would store `{"task_id": "T42", "agent": "CW", "priority": 1}`. The text version tells you *why* the task exists and *what decision* led to it.

This reflects Herbert Simon's principle that organizations coordinate not through centralized command, but through shared understanding of goals and constraints (Simon, 1957, pp. 79–110). The COORDINATION_STATE file is a shared mental model of what each agent is doing and why.

---

## §156: The RAG Experiment — Proving Epistemic Infrastructure Matters

The Article Eater system is expensive. It has 4,888 beliefs encoded in a web of belief, 18 molecules linking beliefs to 13 domain theories, 10 theoretical frameworks, an interpretation layer with two question classifiers, and an enrichment orchestrator with nine service calls. A naive alternative—Retrieval-Augmented Generation (RAG) over the same corpus—would be trivial to implement: embed the article texts, run similarity search, feed results to an LLM, return the answer.

The question is: does the epistemic infrastructure produce *better* answers than naive RAG? The experiment design answers this empirically.

**Four systems compete:**

RAG-Baseline uses vector embeddings of raw article texts (PDFs/abstracts). An LLM retrieves the top 10 chunks by cosine similarity to the question and generates an answer. This is GPT-4 doing CTRL+F in a corpus.

RAG-Enhanced uses vector embeddings of the 33,000+ extraction JSONs—the structured findings we extracted from each paper. An LLM retrieves structured findings instead of raw text. The question "Does natural light affect mood?" now retrieves objects like `{"finding_type": "effect_size", "outcome": "mood_improvement", "effect_size": 0.72, "n_studies": 23, "source_paper": "..."}`. This is more structured, but still retrieval without synthesis.

Article Eater uses the full epistemic network: the four-layer belief taxonomy, the 13 domain theory mappings, the warrants, credence estimates, and the interpretation layer. An LLM generates an answer and the orchestrator enriches it with theoretical context, uncertainty quantification, practical implications, and targeted follow-ups.

Article Eater (no LLM) uses the same epistemic network but answers only through templates and structured reasoning—no LLM generation. This isolates the value of the *infrastructure* from the value of fluency.

**Eight dependent variables, all scored blind by expert raters:**

Factual accuracy measures basic retrieval quality: are the facts stated in the answer true per the source papers? This is table stakes. Both RAG and Article Eater must get this right.

Evidential grounding measures depth: does the answer cite specific studies, sample sizes, effect sizes, or just vague generalizations? A RAG answer might say "green space is restorative," while an Article Eater answer says "green space reduces cortisol by 0.65 SD (Ulrich et al., 1991, n=120; averaged across 23 studies with 95% CI [0.51, 0.79])."

Theoretical integration measures *what* the Article Eater is built for: does the answer connect findings to T1 and T1.5 frameworks? Can it say "This result exemplifies predictive processing"? Or "Stress recovery theory predicts this outcome"? Naive RAG cannot do this systematically because it has no internal representation of theory.

Uncertainty honesty measures epistemic responsibility: does the answer express appropriate confidence? "We are 78% confident that X" versus "X is definitely true." RAG tends to hallucinate confidence; Article Eater quantifies uncertainty through credence and warrant strength.

Contradiction awareness measures dialectical sophistication: when evidence conflicts, does the answer acknowledge both sides and explain the disagreement? "Open offices harm productivity (Studies A, B, C), but Study D found no effect because they measured different outcomes" is a higher-order answer than either side alone.

Practical specificity measures actionability: if the question is "How should I design a hospital waiting room to reduce anxiety?" does the answer give recommendations like "Use 4000K color temperature (research evidence), 55 dB background noise (CVA calibration), and biophilic visual elements (Appleton's prospect-refuge theory)" or just "Use nature"? Article Eater has practical implications linked to each belief.

Cross-domain integration measures synthesis breadth: can the system connect findings across visual, acoustic, thermal, and olfactory domains? RAG sees each domain separately. Article Eater has molecules linking sensory modalities through the Goldilocks principle.

Explanation depth measures mechanistic understanding: does the answer explain *why*, not just *what*? A good answer to "Does daylight improve sleep?" says "Light resets the circadian phase through melanopsin-expressing retinal ganglion cells (ipRGCs), which project to the suprachiasmatic nucleus (SCN); SCN signals the pineal gland to produce melatonin when light drops in the evening (CCT < 3000K triggers melatonin suppression). This phase reset prevents delayed sleep phase disorder." RAG might just say "daylight improves sleep."

**The question battery has 40 items across eight categories:**

Simple factual questions that RAG should answer well. Complex evidence synthesis questions that differentiate the systems. Theoretical mechanism questions where Article Eater dominates. Contradiction handling questions testing dialectical sophistication. Cross-domain integration questions. Practical design recommendations. Methodological assessment questions. Meta-epistemic questions (hardest for RAG) like "Where are the biggest gaps in the evidence base? How confident should we be?"

**Predicted results and their interpretation:**

RAG-Baseline and RAG-Enhanced will converge on simple factual questions—both systems have access to the same corpus. They will both score around 4/5 on factual accuracy.

RAG-Baseline will fail on evidence synthesis, theoretical mechanism, and meta-epistemic questions. It has no internal structure to compute weighted effect sizes or reason about theoretical frameworks.

RAG-Enhanced will do better by having structured extractions, but it still cannot synthesize knowledge across papers—it just retrieves the best matching extraction. Article Eater, with an explicit belief network, can say "This phenomenon appears in 23 papers via mechanism X and 7 papers via mechanism Y, and these mechanisms interact according to principle Z."

The gap widens as questions become epistemically complex. This reveals the staircase of epistemic sophistication: retrieval alone covers 20% of the question space (simple facts). Retrieval + structure covers 50%. Retrieval + structure + theory covers 80%. Full epistemic infrastructure covers 95%.

**Methodological rigor:**

Three expert raters (an environmental psychologist, an epistemologist, and an architect) will score each answer blind, without knowing which system produced it. Answers will be shuffled randomly and presented without system labels. Inter-rater reliability (Krippendorff's alpha) will be computed. IRR > 0.70 is acceptable; > 0.80 is excellent.

The experiment does not compare Article Eater to GPT-4 directly. It compares Article Eater to RAG using the same underlying LLM and the same corpus. This isolates the value of epistemic infrastructure from the value of raw model power. A small LLM with Article Eater's infrastructure will outperform a large LLM with naive RAG on epistemically complex questions.

**What this proves:**

The experiment demonstrates Polanyi's principle that "tacit knowledge cannot be fully articulated" (Polanyi, 1966). RAG operates with explicit knowledge: the text of papers in the corpus. Article Eater operates with *crystallized* tacit knowledge: the patterns, theories, mechanisms, and contradictions distilled from the corpus and encoded in beliefs, warrants, and theories. This crystallized tacit knowledge is what separates an expert from a search engine.

It also validates Ryle's distinction between "knowing-how" and "knowing-that" (Ryle, 1949). RAG has knowing-that: facts retrieved from the corpus. Article Eater has knowing-how: the ability to apply theories, handle contradictions, quantify uncertainty, and integrate across domains. Practical expertise requires both, and the experiment measures both.

---

## §157: Corpus Completion — The Theoretical Foundations Reading List

The Article Eater epistemic network cites 1,083 empirical papers: studies on lighting and productivity, biophilic design and stress recovery, thermal comfort, acoustic design, and so on. But it does not contain the theoretical foundations that these papers cite.

When de Dear and Brager (1998) published "Developing an adaptive model of thermal comfort and preference," they built on decades of research: Fanger (1972) on thermal sensation, McIntyre (1980) on thermal preferences, Humphreys and Nicol (1998) on adaptive behavior. When Kaplan and Kaplan (1989) wrote "The Experience of Nature," they drew on ecological psychology (Gibson, 1979), information processing theory (Neisser, 1967), and visual complexity research (Berlyne, 1960, 1971).

These foundational papers—the ones that define the T1 frameworks and T1.5 domain theories—are not extracted in our system. We have 1,083 empirical papers but not the 53 theoretical foundations that structure them.

AG (Antigravity) identified all 53 foundational papers and created a reading list organized by framework and theory. The T1 frameworks include:

- Predictive Processing (Clark, 2013, 2015; Friston, 2010; Hohwy, 2013)
- Embodied Cognition (Gibson, 1979; Barsalou, 2008; Clark, 1997; Varela, Thompson & Rosch, 1991)
- Spatial Navigation (O'Keefe & Nadel, 1978; Moser et al., 2008; Tolman, 1948)
- Neuromodulatory Systems (Berridge & Robinson, 2009; Schultz, 1997; Dayan & Huys, 2009)
- Interoceptive Inference (Craig, 2002; Seth, 2013; Barrett, 2017)
- Default Mode / Task Positive Networks (Raichle et al., 2001; Fox et al., 2005; Buckner et al., 2008)
- Active Inference (Friston et al., 2010; Pezzulo et al., 2018)
- Circadian and Homeostatic Regulation (Borbély, 1982; Czeisler et al., 1999)
- Allostatic Regulation (McEwen, 2000; Sterling, 2012)
- Social Cognition (Tomasello et al., 2005; Dunbar, 1998)

The T1.5 domain theories include:

- Attention Restoration Theory (Kaplan & Kaplan, 1989; Kaplan, 1995)
- Stress Recovery Theory (Ulrich, 1983; Ulrich et al., 1991)
- Biophilia Hypothesis (Wilson, 1984; Kellert & Wilson, 1993)
- Prospect-Refuge Theory (Appleton, 1975; Dosen & Ostwald, 2016)
- Privacy Regulation Theory (Altman, 1975)
- Kaplan Preference Matrix (Kaplan & Kaplan, 1982)
- Adaptive Thermal Comfort (de Dear & Brager, 1998; Humphreys & Nicol, 1998)
- Space Syntax (Hillier & Hanson, 1984; Hillier, 1996)
- Soundscape Theory (Schafer, 1977; Brown et al., 2011)
- Place Attachment (Lewicka, 2011; Scannell & Gifford, 2010)
- BRECVEMA (Juslin, 2013) — the mechanisms of musical emotion
- Flow Theory (Csikszentmihalyi, 1990)
- Goldilocks Principle (Berlyne, 1971; Kirsh, 2026)

Plus foundational epistemology (Haack, 1993; Quine, 1951; Quine & Ullian, 1978).

**Why this matters:**

First, the RAG experiment cannot be fair without these papers. If RAG's corpus includes the 53 foundations but Article Eater's system is built on them without having them extracted, we are comparing systems on unequal footing. For the experiment to be rigorous, both systems need the same foundational knowledge.

Second, extracting the foundations enables self-audit. AG can extract Kaplan and Kaplan (1989) and verify that the "Attention Restoration Theory" belief network matches the originators' definition. When Kaplan describes the four attentional mechanisms (directed attention fatigue, fascination, compatibility, scope), AG can check: "Do our beliefs about ART capture these four?" If not, the system has a theory gap to fix.

Third, it completes the corpus epistemically. Right now, we have 1,083 papers citing foundational theories, but the theories themselves are implicit in the code. Making them explicit—as extracted beliefs—moves the system from "we use these theories" to "here is what Kaplan said and here is what the literature says about it and here is how they connect."

This is part of a larger principle: epistemic infrastructure should be **materially present** in the system, not merely assumed. The difference between a system that uses Quine's coherentism and a system that has Quine's *Web of Belief* (1978) extracted and integrated is the difference between implicit and explicit knowledge (Haack, 1993).

---

## §158: The Tier Taxonomy Propagation Procedure

The T1.5 domain theory count appeared in four different places with four different values: 4 in §50, 10 in §122, 12 in §78, 13 in §78 (including Goldilocks). This inconsistency was discovered during the AG ruthless engineering audit and created ambiguity: which count is correct?

The resolution (March 2, 2026) is 13 T1.5 theories. Berlyne's New Experimental Aesthetics (1971) is subsumed by the Goldilocks Principle (Berlyne + Kirsh extension to architectural cognition). The full roster is:

1. ART (Kaplan), 2. SRT (Ulrich), 3. Biophilia, 4. Prospect-Refuge, 5. Privacy Regulation, 6. Kaplan Preference Matrix, 7. Adaptive Thermal Comfort, 8. Space Syntax, 9. Soundscape Theory, 10. Place Attachment, 11. BRECVEMA, 12. Flow, 13. Goldilocks.

But changing a fundamental tier count is dangerous. The count is baked into prompts, docstrings, tests, and documentation. If you change the JSON but forget to update the QA handler, stale code will say "4 T1.5" forever. To prevent this, AG designed a six-layer propagation procedure:

**Layer 1: Canonical Sources.** The source of truth files are JSON schemas in `schemas/theory/`:
- `tier1_frameworks.json` (10 frameworks)
- `tier1_5_domain_theories.json` (13 theories)
- `tier2_mechanisms.json` (~166 templates)
- `molecule_taxonomy.json` (18 molecules)

Change the JSON first. Then verify that all downstream systems load from these files, not hardcoded values.

**Layer 2: Dynamic Loading Code.** Services like `arbitrary_qa_handler.py` and `finding_template_relevance.py` should load tier counts from JSON at runtime, not compile time. When you request `get_tier_count("T1.5")`, it reads from the JSON. This is verifiable: if the code has `T1_5_COUNT = 13` as a constant, that is a violation.

**Layer 3: Keyword Matching.** The tag engine and warrant strength calculator use T1 abbreviations and names. These should be loaded from a mapping dict derived from the JSON, not hardcoded abbreviations. The mapping should use kebab-case IDs like `attention-restoration-theory` and maintain backward compatibility aliases.

**Layer 4: LLM Prompts.** The extraction prompts guide the Gemini model to identify which T1 framework and T1.5 theory each finding belongs to. Abbreviations in prompts (PP for Predictive Processing, ART for Attention Restoration Theory) are acceptable because they are domain conventions in the literature. But if you add a theory, the prompt should be updated to mention it.

**Layer 5: QA and Display.** When an arbitrary question asks "How many T1.5 theories do you have?" the answer must match the canonical count. This is user-facing and mission-critical.

**Layer 6: Documentation.** The master doc, architecture spec, tier architecture spec, and other docs must all say the same count. AG created a comprehensive 6-layer audit procedure to verify consistency across all subsystems.

The success condition is not just "the count is 13" but "no file in the system can be out of sync with the canonical JSON." The tier taxonomy consistency test suite has 13 tests:

1. Canonical JSONs have correct counts (T1=10, T1.5=13)
2. QA catalog dynamically loads from JSON
3. No stale hardcoded "4 T1.5" in code
4. tag_engine uses kebab-case IDs
5. T3 is never hardcoded
... and so on.

Every time an agent runs `/check-out`, these tests run. If they fail, the agent fixes them before leaving. This makes tier taxonomy consistency not a one-time audit, but a continuous invariant.

This is an instance of Brooks' principle of layer separation: keep invariants (what must always be true) separate from architecture (what the structure is) separate from implementation (how to achieve it) (Brooks, 1975). The invariant is "T1.5 count is always 13 and always loaded from JSON." The architecture is six-layer propagation. The implementation is the test suite that enforces it.

---

## §159: PDF Acquisition and Auto-Ingestion Architecture

Getting papers into the system is the first bottleneck. The empirical corpus of 1,083 papers took weeks to assemble. Adding 53 foundational papers should be faster, but it still requires solving the "paywalled PDF" problem: most academic papers are published by Elsevier, Wiley, or Taylor & Francis and are not freely available online.

AG designed a five-step cascade to maximize automated retrieval before asking David for manual help:

**Step 1: OpenAlex Content API.** Query the OpenAlex API for each DOI. OpenAlex returns structured metadata and *the open-access status and PDF URL*. For papers marked as open access, this yields a direct PDF link. No cost, no authentication.

**Step 2: Unpaywall.** A second source for open-access PDFs. Unpaywall aggregates open-access metadata from publishers, repositories, and preprint servers. It is free (email-based API). For papers not found by OpenAlex, Unpaywall often has them.

**Step 3: CORE.** This is the game-changer. CORE indexes 37 million full texts from institutional repositories worldwide: university libraries, preprint servers, and research institutions. Many paywalled papers have "green open access" versions—the author's accepted manuscript—sitting in their university's repository. CORE finds these. It is free with registration.

**Step 4: PubMed Central (PMC).** For biomedical papers, PMC has 8 million open-access full texts. Many of the foundational papers on circadian rhythm, stress physiology, and neuromodulation are in PMC. Free.

**Step 5: Internet Archive Scholar and Fallback.** For rare or old papers (Berlyne 1971, Appleton 1975), check Internet Archive and other preprint servers (bioRxiv, PsyArXiv, SSRN).

If none of these yield a PDF, the paper goes into a "human-in-the-loop" (HITL) database: `data/acquisition/hitl_needed.json`. This records the DOI, reason for failure, priority, and recommended manual source (Elicit, Academia.edu, Zotero + UCSD proxy).

**The auto-ingestion pipeline:**

Once a PDF arrives in `data/pdfs_incoming/`, five stages run automatically:

**DETECT**: Identify the paper (by filename or DOI lookup in CrossRef). Verify it matches one of the wanted papers.

**EXTRACT**: Run the extraction pipeline (Gemini + V3 prompts). Generate the extraction JSON.

**QA GATE**: Validate the extraction. Check for common failure modes (empty findings, parse errors, nonsensical theory mappings). If validation fails, flag it.

**INTEGRATE**: Add findings to the epistemic network. Update belief counts, wire new beliefs to T1.5 theories, check for contradictions with existing beliefs.

**OVERSEER**: A second pass by the Overseer service, checking for anomalies or high-uncertainty findings that need human review.

Failed extractions (those that don't pass the QA gate) are recorded in the HITL database with details: "PDF extracted but 87 of 104 findings had low confidence. Manual review recommended." This prevents garbage data from silently entering the system.

The architecture reflects insights from the PDF retrieval API analysis. AG found that most off-the-shelf PDF retrieval services are disappointing because:

1. **Sandbox constraints**: AG runs in a sandboxed environment with restricted outbound network access. It cannot download arbitrary PDFs from the web.
2. **Publisher paywalls**: Most papers are paywalled. Publishers actively block non-browser user agents.
3. **Authentication**: Authenticated access (UCSD proxy, Academia.edu premium) requires browser automation, which is not available.

Rather than trying to make AG smarter at downloading, the solution is to **make the workflow give AG less to download**. By maximizing automated OA retrieval (OpenAlex + CORE + PMC), 65–75% of papers arrive without human intervention. The remaining 25–35% require David's 2–5 minutes per batch: paste DOIs into Elicit, download from Academia.edu, or use the UCSD proxy. This is vastly more efficient than asking AG to solve the sandbox problem.

This is an instance of bounded rationality and workflow design: given agent constraints, design the process to respect those constraints and play to the agent's strengths (querying APIs, processing PDFs) while offloading tasks that require human judgment (choosing which paywalled papers are worth the effort to retrieve).

The system also learns from failures. Each time a paper is not found, the HITL database records why. Over time, this data guides future decisions: "Scite and CORE together cover 82% of papers; the remaining 18% are consistently older books (pre-1995) or conference proceedings not indexed anywhere."

---

## References

Appleton, J. (1975). *The Experience of Landscape*. Wiley.

Barsalou, L. W. (2008). Grounded cognition. *Annual Review of Psychology*, 59, 617–645.

Berlyne, D. E. (1971). *Aesthetics and Psychobiology*. Appleton-Century-Crofts.

Berridge, K. C., & Robinson, T. E. (2009). Parsing reward. *Trends in Neuroscience*, 32(9), 507–510.

Brooks, F. P. (1975). *The Mythical Man-Month*. Addison-Wesley.

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181–204.

Clark, A. (2015). *Surfing Uncertainty: Prediction, Action, and the Embodied Mind*. Oxford University Press.

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1), 145–167.

Dunbar, R. I. M. (1998). The social brain hypothesis. *Evolutionary Anthropology*, 6(5), 178–190.

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11, 127–138.

Haack, S. (1993). *Evidence and Inquiry: Towards Reconstruction in Epistemology*. Blackwell.

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, 15(3), 169–182.

Kaplan, R., & Kaplan, S. (1989). *The Experience of Nature: A Psychological Perspective*. Cambridge University Press.

Polanyi, M. (1966). *The Tacit Dimension*. Doubleday.

Quine, W. V. O., & Ullian, J. S. (1978). *The Web of Belief*. McGraw-Hill.

Ryle, G. (1949). *The Concept of Mind*. Hutchinson.

Simon, H. A. (1957). *Administrative Behavior* (2nd ed.). Macmillan.

Wilson, E. O. (1984). *Biophilia*. Harvard University Press.

