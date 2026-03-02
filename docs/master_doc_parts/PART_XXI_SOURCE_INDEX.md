# PART XXI: SOURCE DOCUMENT INDEX (§147)

*This Part catalogues the primary source documents produced during ATLAS system development. It provides researchers, panel members, and practitioners with a reference map to the underlying research, design decisions, and evidence synthesis that inform the system.*

---

## §147: Document Provenance and Cross-References {#147}

The ATLAS system documentation consists of multiple interconnected source documents, each serving a specific epistemic function. This section lists the key sources in chronological order of production, with brief descriptions and indicative content.

### 147.1 Foundational Warrant Analysis

**02-26_01_EN_Warrant_Analysis_V1.0.docx**

*February 26, 2026 | ~30 pages*

A formal analysis of the seven warrant types that structure epistemic claims in the ATLAS system. This document provides the theoretical justification for each warrant type's transfer reliability (d value), including case studies demonstrating how warrant type selection affects downstream credence calculations. Key sections: (a) Constitutive warrants and definitional boundaries; (b) Mechanism warrants and causal pathway specificity; (c) Empirical association warrants and replication across populations; (d) Functional warrants and known behavioral roles; (e) Capacity warrants and possibility versus actuality; (f) Analogical warrants and cross-domain transfer; (g) Theory-derived warrants and untested predictions. This document is the primary reference for understanding the epistemic principles underlying the entire system.

### 147.2 Response to External Critique

**02-26_02_Addressing_Pearl_Typed_Edges_V2.0.docx**

*February 26, 2026 | ~40 pages*

A detailed response to anticipated objections from Judea Pearl and other causal inference theorists regarding the ATLAS system's use of typed edges (edges annotated with warrant type τ and strength ω) in an epistemic network. This document addresses: (a) Why a coherentist epistemic network (Quine/Haack) can coexist with a Bayesian operational network (Pearl); (b) How warrant types map to structural properties of transferred causal claims (Woodward's invariance ranges); (c) Why cycles and parallel edges are epistemically legitimate in the EN but not the BN; (d) How the projection function π resolves the apparent paradox of using both coherentist and Bayesian reasoning; (e) Concrete examples where standard Pearl do-calculus would fail but the ATLAS system succeeds by distinguishing epistemic assessment from operational prediction. Essential reading for theorists and critics of the system.

### 147.3 First Terminology Consolidation

**02-27_03_ATLAS_Terminology_Cheat_Sheet_V1.0.docx**

*February 27, 2026 | Version 1.0*

The first consolidated terminology document, produced early in Session 2. This version introduced the basic three-layer architecture (EN, π, BN) and the four core numbers (ω, d, δ, CPT) but contained terminology that was refined in later revisions. Key distinctions: Epistemic Network vs. Bayesian Network; warrant strength vs. transfer reliability; population transfer factor. This document shows the evolution of naming conventions and served as the basis for the revised v2.0 cheat sheet (see 02-27_06 below).

### 147.4 Session 2 Decision Record

**02-27_04_Exchange_Summary_Session2.md**

*February 27, 2026 | Session 2 continuation*

A comprehensive record of 17 major conceptual decisions and naming conventions established during the continuation of Session 2. This document captures: (a) DECISION 1: Rename "Epistemic Warrant Graph" → "Epistemic Network"; (b) DECISION 2: Rename "confidence weight" → "warrant strength" (ω); (c) DECISION 3: Define "transfer reliability" (d) as discount factor; (d) DECISION 4: Define CPT (Conditional Probability Table); (e) DECISION 5: Rename EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION; (f) DECISION 6: Rename THEORETICAL_DEFAULT → THEORY_DERIVED [theory name]; (g) DECISION 7: Finalize the seven-warrant-type set with canonical d values; (h) Further naming and notational conventions. Each decision includes rationale and cross-references to affected sections of the system. This is the reference document for understanding which terminology decisions are final.

### 147.5 Revised Terminology Cheat Sheet

**02-27_06_ATLAS_Cheat_Sheet_V2.0.docx**

*February 27, 2026 | Final terminology version*

The canonical terminology reference document. This version incorporates all decisions from 02-27_04_Exchange_Summary_Session2.md and presents: (a) The Three-Layer Architecture table (EN, π, BN); (b) The Four Numbers table (ω, d, δ, CPT); (c) The Seven Warrant Types table with d values and working examples; (d) How Evidence Combines rules (serial, parallel, explanatory boost); (e) The Dual-BN Diagnostic; (f) Population Transfer Factors; (g) What the EN has that the BN doesn't; (h) Key Structural Principles; (i) Quick Reference All Symbols table. This document is the primary reference for all terminology questions and should be consulted before any other ATLAS documentation. It is included in the master doc as Part XIX, §140.

### 147.6 Formulas and Worked Examples

**02-27_07_ATLAS_Technical_Appendix_V1.0.docx**

*February 27, 2026 | Technical reference*

The technical specification for the projection mechanism. This document provides: (a) Core Formulas: log-odds transform, single-edge projection, serial combination, parallel combination, empirical floor, theory dependence diagnostic; (b) Worked Example 1: Daylight → Mood, showing how three serial mechanism links combine to produce p_target ≈ 0.61, with parallel evidence boost to 0.69; (c) Worked Example 2: Fractal → Wellbeing, showing how theory-derived links create a near-zero signal despite plausible mechanisms; (d) Worked Example 3: Population Transfer Effects, showing how δ varies across three target populations; (e) Worked Example 4: Dual-BN Comparison, showing how architects use full projection vs. empirical floor to make design decisions; (f) Complete Formula Reference. Every numerical value in these examples is exact and has been hand-calculated for verification. This document is included in the master doc as Part XX, §141–§146.

### 147.7 Cross-Audit Synthesis

**CROSS_AUDIT_SYNTHESIS_AND_SPRINT_PLAN_2026-02-27.md**

*February 27, 2026 | 0430 hours*

A synthesis document produced after cross-auditing all major system components (EN, BN, projection mechanism, expert panel inputs, and decision logs). This document: (a) Summarizes the current state of the epistemic network (813 papers loaded, 747 integrated, 23,766 beliefs in web_persistence.db); (b) Documents the Article Eater pipeline (integrated in 1973.9s, approximately 33 minutes); (c) Lists all major decisions from Sessions 1–2; (d) Identifies inconsistencies or gaps in terminology; (e) Proposes refined sprint planning for the following weeks. Key insight: The system is operationally sound but requires continued documentation work (this Master Doc) and expert panel review before release.

### 147.8 Revised Sprint Plan

**NEW_DOCUMENT_SYNTHESIS_AND_REVISED_SPRINT_PLAN_2026-02-27.md**

*February 27, 2026 | Sprint 8 planning*

A revised sprint plan incorporating decisions from all prior sessions and the cross-audit synthesis. This document: (a) Breaks down Sprint 8 into four phases (Computational Infrastructure, Epistemic Framework, Decision Tracking, Master Doc Assembly); (b) Identifies Phase 4 tasks: Add Cheat Sheet, Technical Appendix, enhance Part XVIII, and create Source Document Index; (c) Specifies dependencies and success criteria; (d) Outlines Sprint 9 priorities. This is the planning document for the current work session (Sprint 8 Phase 4).

### 147.9 Run Report

**RUN_REPORT_2026-02-27_0430.md**

*February 27, 2026 | 0430 hours*

A technical report documenting the latest full run of the Article Eater system and codex integration pipeline. This report includes: (a) Start time, end time, and total runtime (1973.9 seconds, ~33 minutes); (b) Papers loaded and integrated counts; (c) Database statistics (813 papers, 747 integrated into web, 23,766 beliefs in web_persistence.db); (d) Error logs (any papers that failed integration and reasons); (e) Performance metrics (average extraction time per paper, database query times, BN computation times); (f) Recommendations for optimization. This is the operational baseline for system health monitoring.

### 147.10 Synthesis of Source Documents

The relationship among these source documents is as follows:

- **Epistemic Foundation**: 02-26_01 (Warrant Analysis) + 02-26_02 (Pearl Response) establish the theoretical underpinnings.
- **Terminology Evolution**: 02-27_03 (v1.0) → 02-27_04 (Decisions) → 02-27_06 (v2.0) shows the refinement process.
- **Technical Specification**: 02-27_07 (Technical Appendix) provides the formulas and calculations.
- **System State**: CROSS_AUDIT_SYNTHESIS (full picture) + RUN_REPORT (operational metrics) document the current state.
- **Future Planning**: NEW_DOCUMENT_SYNTHESIS (revised sprint plan) guides next steps.

All of these documents are reflected in or referenced by the Master Document, which serves as the unified repository for all ATLAS knowledge. Cross-references between this index and specific sections of the master doc (e.g., "see §140 for the cheat sheet, which is adapted from 02-27_06") enable readers to navigate both the original source documents and their integrated presence in the master doc.

### 147.11 References for §147

Kirsh, D. (2026). *ATLAS Master Document*. Working archive. University of California, San Diego. [This document]

---

## References

Acking, C.-A., & Küller, R. (1972). The perception of an interior as a function of its colour. *Ergonomics*, 15(6), 645-654.

Appleton, J. (1975). *The Experience of Landscape*. Wiley.

Aston-Jones, G., & Cohen, J. D. (2005). An integrative theory of locus coeruleus-norepinephrine function: Adaptive gain and optimal performance. *Annual Review of Neuroscience*, 28, 403-450.

Augustin, S. (2009). *Place Advantage: Applied Psychology for Interior Architecture*. Wiley.

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science*, 17(8), 645-648.

Bechtel, R. B. (1997). *Environment and Behavior: An Introduction*. Sage.

Billock, V. A., & Tsou, B. H. (2001). Seeing forbidden colors. *Scientific American*, 302(2), 72-77.

Boubekri, M., Cheung, I. N., Reid, K. J., Wang, C. H., & Zee, P. C. (2014). Impact of windows and daylight exposure on overall health and sleep quality of office workers. *Journal of Clinical Sleep Medicine*, 10(6), 603-611.

Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge theory: A meta-analysis of the findings of environmental preference research. *City, Territory and Architecture*, 3(1), 4.

Gladwell, V. F., Brown, D. K., Barton, J. L., Tarvainen, M. P., Kuoppa, P., Pretty, J., ... & Sandercock, G. R. H. (2012). The effects of views of nature on autonomic control. *European Journal of Applied Physiology*, 112(9), 3379-3386.

Haapakangas, A., Hongisto, V., Hyönä, J., Kokko, J., & Keränen, J. (2011). Effects of irrelevant speech on performance and subjective disturbance: The role of acoustic design in open-plan offices. *Applied Acoustics*, 77, 98-109.

Hasson, U., Hendler, T., Bashat, D. B., & Malach, R. (2003). Vase or face? A neural correlate of shape-selective grouping processes in the human brain. *Journal of Cognitive Neuroscience*, 15(3), 335-351.

Jones, D. M., Miles, C., & Page, J. (1999). Disruption of reading by irrelevant speech: Effects of attention, arousal or memory? *Applied Cognitive Psychology*, 13(6), 541-558.

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology*, 15(3), 169-182.

Kardan, O., Demiralp, E., Hout, M. C., Hunter, M. R., Karimi, H., Hanayik, T., ... & Berman, M. G. (2015). Is the preference of natural versus man-made scenes driven by bottom-up processing of the visual features of nature? *Frontiers in Psychology*, 6, 471.

Kourtzi, Z., & Kanwisher, N. (2000). Cortical regions involved in perceiving object shape. *Journal of Neuroscience*, 20(9), 3310-3318.

Mehta, R., Zhu, R. J., & Cheema, A. (2012). Is noise always bad? Exploring the effects of ambient noise on creative cognition. *Journal of Consumer Research*, 39(4), 784-799.

Meyers-Levy, J., & Zhu, R. J. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research*, 34(2), 174-186.

Nicoll, G., & Zimring, C. (2009). Effect of innovative building design on physical activity. *Journal of Public Health Policy*, 30(S1), S111-S123.

Nieuwenhuis, M., Knight, C., Postmes, T., & Haslam, S. A. (2014). The relative benefits of green versus lean office space: Three field experiments. *Journal of Experimental Psychology: Applied*, 20(3), 199-214.

Öhman, A., Flykt, A., & Esteves, F. (2001). Emotion drives attention: Detecting the snake in the grass. *Journal of Experimental Psychology: General*, 130(3), 466-478.

Pasupathy, A., & Connor, C. E. (2002). Population coding of shape in area V4. *Nature Neuroscience*, 5(12), 1332-1338.

Salamé, P., & Baddeley, A. (1982). Disruption of short-term memory by unattended speech: Implications for the structure of working memory. *Journal of Verbal Learning and Verbal Behavior*, 21(2), 150-164.

Sommer, R. (1969). *Personal Space: The Behavioral Basis of Design*. Prentice-Hall.

Stamps, A. E. (2005). Enclosure and safety in urbanscapes. *Environment and Behavior*, 37(1), 102-133.

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science*, 224(4647), 420-421.

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Gonzalez-Mora, J. L., Leder, H., ... & Skov, M. (2015). Architectural design and the brain: Effects of ceiling height and perceived enclosure on beauty judgments and approach-avoidance decisions. *Journal of Environmental Psychology*, 41, 10-18.

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., ... & Skov, M. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. *Proceedings of the National Academy of Sciences*, 110(Supplement 2), 10446-10453.

Viola, A. U., James, L. M., Schlangen, L. J., & Dijk, D. J. (2008). Blue-enriched white light in the workplace improves self-reported alertness, performance and sleep quality. *Scandinavian Journal of Work, Environment & Health*, 34(4), 297-306.

Wastiels, L., Schifferstein, H. N., Heylighen, A., & Wouters, I. (2012). Relating material experience to technical parameters: A case study on visual and tactile warmth perception of indoor wall materials. *Building and Environment*, 49, 359-367.

Williams, L. E., & Bargh, J. A. (2008). Experiencing physical warmth promotes interpersonal warmth. *Science*, 322(5901), 606-607.

Zimring, C., Joseph, A., Nicoll, G. L., & Tsepas, S. (2005). Influences of building design and site design on physical activity: Research and intervention opportunities. *American Journal of Preventive Medicine*, 28(2), 186-193.

---

## Additional References for Expanded Sections

Aggleton, J. P., & Waskett, L. (1999). The ability of odours to serve as state-dependent cues for real-world memories. *British Journal of Psychology*, 90(1), 1-7.

Anderson, M. L. (2010). Neural reuse: A fundamental organizational principle of the brain. *Behavioral and Brain Sciences*, 33(4), 245-266.

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181-204.

Diener, E., & Wallbom, M. (1976). Effects of self-awareness on antinormative behavior. *Journal of Research in Personality*, 10(1), 107-111.

Fenko, A., Schifferstein, H. N., & Hekkert, P. (2010). Shifts in sensory dominance between various stages of user–product interactions. *Applied Ergonomics*, 41(1), 34-40.

Flynn, J. E., Hendrick, C., Spencer, T., & Martyniuk, O. (1979). A guide to methodology procedures for measuring subjective impressions in lighting. *Journal of the Illuminating Engineering Society*, 8(2), 95-110.

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.

Herz, R. S., & Engen, T. (1996). Odor memory: Review and analysis. *Psychonomic Bulletin & Review*, 3(3), 300-313.

Heschong, L. (2003). *Windows and offices: A study of office worker performance and the indoor environment*. California Energy Commission.

Hildebrand, G. (1999). *Origins of Architectural Pleasure*. University of California Press.

Joye, Y. (2007). Architectural lessons from environmental psychology: The case of biophilic architecture. *Review of General Psychology*, 11(4), 305-328.

Kellert, S. R., & Calabrese, E. F. (2015). *The practice of biophilic design*. www.biophilic-design.com.

Lakoff, G., & Johnson, M. (1999). *Philosophy in the Flesh: The Embodied Mind and Its Challenge to Western Thought*. Basic Books.

Lam, W. M. (1977). *Perception and Lighting as Formgivers for Architecture*. McGraw-Hill.

Maki, B. E. (1997). Gait changes in older adults: Predictors of falls or indicators of fear? *Journal of the American Geriatrics Society*, 45(3), 313-320.

Marigold, D. S., & Patla, A. E. (2002). Strategies for dynamic stability during locomotion on a slippery surface: Effects of prior experience and knowledge. *Journal of Neurophysiology*, 88(1), 339-353.

McMains, S., & Kastner, S. (2011). Interactions of top-down and bottom-up mechanisms in human visual cortex. *Journal of Neuroscience*, 31(2), 587-597.

Oberfeld, D., Hecht, H., & Gamer, M. (2010). Surface lightness influences perceived room height. *Quarterly Journal of Experimental Psychology*, 63(10), 1999-2011.

O'Keefe, J., & Nadel, L. (1978). *The Hippocampus as a Cognitive Map*. Oxford University Press.

Pallasmaa, J. (2005). *The Eyes of the Skin: Architecture and the Senses*. Wiley.

Quine, W. V. O., & Ullian, J. S. (1978). *The Web of Belief*. Random House.

Rea, M. S., Figueiro, M. G., & Bullough, J. D. (2017). Circadian photobiology: An emerging framework for lighting practice and research. *Lighting Research & Technology*, 34(3), 177-187.

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure: Is beauty in the perceiver's processing experience? *Personality and Social Psychology Review*, 8(4), 364-382.

Saxbe, D. E., & Repetti, R. (2010). No place like home: Home tours correlate with daily patterns of mood and cortisol. *Personality and Social Psychology Bulletin*, 36(1), 71-81.

Smith, R. J., & Bugni, V. (2006). Symbolic interaction theory and architecture. *Symbolic Interaction*, 29(2), 123-155.

Vartanian, O., Navarrete, G., Palumbo, L., & Chatterjee, A. (2019). Individual differences in preference for architectural interiors. *Journal of Environmental Psychology*, 77, 101368.

Weber, C. O. (1931). The aesthetics of rectangles and theories of affection. *Journal of Applied Psychology*, 15(3), 310-318.

Werner, S., & Schindler, L. E. (2004). The role of spatial reference frames in architecture: Misalignment impairs wayfinding performance. *Environment and Behavior*, 36(4), 461-482.

Wilson, E. O. (1984). *Biophilia*. Harvard University Press.

Zahorik, P. (2002). Assessing auditory distance perception using virtual acoustics. *Journal of the Acoustical Society of America*, 111(4), 1832-1846.

## Additional References for Sections 45–47

Ades, A. E., Lu, G., & Claxton, K. (2004). Expected value of sample information calculations in medical decision modeling. *Medical Decision Making*, 24(2), 207–227.

ASHRAE. (2023). *ANSI/ASHRAE Standard 55-2023: Thermal environmental conditions for human occupancy*. American Society of Heating, Refrigerating and Air-Conditioning Engineers.

Berenbaum, M. C. (1989). What is synergy? *Pharmacological Reviews*, 41(2), 93–141.

Chaloner, K., & Verdinelli, I. (1995). Bayesian experimental design: A review. *Statistical Science*, 10(3), 273–304.

Ernst, M. O., & Banks, M. S. (2002). Humans integrate visual and haptic information in a statistically optimal fashion. *Nature*, 415(6870), 429–433.

Good, I. J. (1950). *Probability and the weighing of evidence*. Griffin.

Greco, W. R., Bravo, G., & Parsons, J. C. (1995). The search for synergy: A critical review from a response surface perspective. *Pharmacological Reviews*, 47(2), 331–385.

Hempel, C. G. (1965). *Aspects of scientific explanation*. Free Press.

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*, 2(1), 22–26.

International WELL Building Institute. (2020). *WELL Building Standard v2*. International WELL Building Institute.

Jacobs, R. A., Jordan, M. I., Nowlan, S. J., & Hinton, G. E. (1991). Adaptive mixtures of local experts. *Neural Computation*, 3(1), 79–87.

Kahneman, D. (1973). *Attention and effort*. Prentice-Hall.

Keeney, R. L., & Raiffa, H. (1976). *Decisions with multiple objectives: Preferences and value tradeoffs*. Wiley.

Kruithof, A. A. (1941). Tubular luminescence lamps for general illumination. *Philips Technical Review*, 6(3), 65–96.

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, 67(1), 1–25.

Mayo, D. G. (1996). *Error and the growth of experimental knowledge*. University of Chicago Press.

Mehrabian, A., & Russell, J. A. (1974). *An approach to environmental psychology*. MIT Press.

Neufert, E. (2019). *Architects' data* (5th ed.). Wiley-Blackwell.

Pearl, J. (2000). *Causality: Models, reasoning, and inference*. Cambridge University Press.

Pearl, J., & Bareinboim, E. (2014). External validity: From do-calculus to transportability across populations. *Statistical Science*, 29(4), 579–595.

Popper, K. R. (1959). *The logic of scientific discovery*. Hutchinson.

Raiffa, H., & Schlaifer, R. (1961). *Applied statistical decision theory*. Harvard Business School.

Rea, M. S., & Freyssinier, J. P. (2013). White lighting. *Color Research & Application*, 38(2), 82–92.

Reichenbach, H. (1938). *Experience and prediction: An analysis of the foundations and the structure of knowledge*. University of Chicago Press.

Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.

Spence, C. (2011). Crossmodal correspondences: A tutorial review. *Attention, Perception, & Psychophysics*, 73(4), 971–995.

Turvey, M. T. (1992). Affordances and prospective control: An outline of the ontology. *Ecological Psychology*, 4(3), 173–187.

Zhou, B., Lapedriza, A., Khosla, A., Oliva, A., & Torralba, A. (2018). Places: A 10 million image database for scene recognition. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 40(6), 1452–1464.

---

## Article Eater System Documentation

Kirsh, D., et al. (2026a). *IE-DPT Full T1 Specification: Implicit-Explicit Dual-Process Theory and the Canonical T1 Framework Roster*. Article Eater System Documentation, UCSD Cognitive Science. Available at: `docs/IE_DPT_Full_T1_Specification.md`

Kirsh, D., et al. (2026b). *Adding T1.5 Theories: Operationalization for the Web of Belief*. Article Eater System Documentation, UCSD Cognitive Science. Available at: `docs/archive/Adding_T1_5_Theories_Operationalization.md`

Kirsh, D., et al. (2026c). *T1.5 Three New Reductions: Space Syntax, Soundscape, and Place Attachment*. Article Eater System Documentation, UCSD Cognitive Science. Available at: `docs/archive/T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md`

---

*Draft completed: February 23, 2026; Sections 45–47 added February 24, 2026*
*Word count: ~28,000*
*For: Educational purposes—demonstrating neural explanations for environmental psychology*
*Structure: Part I (30 Examples) + Part II (Theoretical Foundations) + Part III (Prediction Pipeline, System Inventory, VOI)*
