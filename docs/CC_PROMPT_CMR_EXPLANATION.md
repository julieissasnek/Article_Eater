# CC TASK PROMPT: BUILD CMR ARCHITECTURE EXPLANATION
## Hand this file to Claude Code. It is the standing order for building the document.
## Last updated: February 22, 2026

---

## WHAT YOU ARE BUILDING

A single living document — `CMR_ARCHITECTURE_EXPLANATION.md` — that explains the
entire CMR (Compositional Mechanistic Reasoning) system to an audience of cognitive
scientists, architects, and computational modelers. The document must be accurate,
comprehensive, and grounded in the actual project files. It is a long-form technical
explanation, not a summary.

## CRITICAL INSTRUCTION: READ BEFORE YOU WRITE

**Do NOT write from memory or general knowledge.** Every substantive claim in this
document must be traceable to a specific passage in a specific project file. Your
memory of these files is unreliable. You MUST read each source file before writing
or revising any section that depends on it.

If a source file is not available in the project folder, mark the dependent content
with `[SOURCE UNAVAILABLE: filename]` and state what you would need to verify.

## STEP 1: LOCATE AND READ ALL SOURCE DOCUMENTS

The project folder should contain the files listed below. Read them ALL before
writing anything. If some are missing, note which ones and proceed with what you have.

### Primary authority documents (read these first, in this order):

1. `TRANSFER_Feb21_Session8_CORRECTED.md` — THE CURRENT PROJECT STATE. Contains:
   the core credence formula, the T1 roster, the T1.5 roster, the bridge warrant
   table, the gap registry, known errors, panel sequence, and pending work. This
   is the single most important file. Read it completely.

2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — THE AUTHORITATIVE panel sequence, template
   targets, required disciplines, and key calibration constructs for every panel.
   This takes precedence over all other documents on questions of panel scope and
   template assignment.

3. `OPUS_REVIEW_GUIDE.md` — Calibration discipline rules: bridge warrant hierarchy
   with priors, confidence score ranges, Coburn R² ceiling, mandatory per-template
   outputs, red flag scan, core credence formula.

4. `exemplar_panel_criteria.md` — Style authority for panel outputs. Read this to
   understand what a well-formed panel output looks like.

### Completed panel outputs (read these for concrete examples of calibrated templates):

5. `VISUAL_I_Panel_Output_Feb21.md` — Document 65. 8 templates calibrated. This is
   the most detailed panel output and the best source for: expert panel composition
   rationale, Crucible debate examples, calibrated JSON structure, residual gaps
   format, cross-template interaction flags, CMR integration notes. READ THIS
   THOROUGHLY — most of the worked examples in the explanation document should be
   drawn from this panel.

6. `STRESS_I_Panel_Output_Feb21.md` — T6, T7, T14 calibrated. Source for: allostatic
   anticipation mechanism, threat-HPA pathway, multimodal PE integration.

7. `LIGHT_I_Panel_Output_Feb21.md` — 8 circadian/light templates. Source for:
   CONSTITUTIVE warrant examples (window area IS daylight exposure), circadian
   mechanism chains, chronobiological regulation.

8. `SPATIAL_I_Panel_Output_Feb21.md` (Doc 63) — SC1-SC4. Source for: isovist-based
   prediction error, spatial integration, promenade temporal PE, Space Syntax bridge.

### Specification documents (read for template format and theoretical architecture):

9. `02-14_09_CMR_Revised_Spec_Panel_Templates_V2_0.md` — CMR V2.0 template spec.
   Templates 1-18. Source for: the original template format definition.

10. `02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md` — Templates 21-30.
    Source for: T22 (rapid gist), T29 (ALLOSTATIC_MASTER_001), T30.

11. `02-14_07_Theory_Tier_Architecture_V1_0.md` — Tier structure document. Source for:
    the rationale behind the tier system, ART/SRT demotion to T1.5.

12. `02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md` — Original CMR spec.
    Source for: the founding design rationale, the Web of Belief concept, the
    relationship between CMR and Bayesian reasoning.

### IE-DPT and theory documents:

13. `IE_DPT_Full_T1_Specification.md` — IE-DPT specification. CAUTION: contains
    Errors 1-3 (incorrect T1 roster, ART/SRT as T1, IE-DPT as T1 #11). Read but
    cross-check against Transfer doc §3 and §4.

14. `T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md` — Source
    for: Space Syntax, Soundscape Theory, Place Attachment formal reductions.

15. `Theory_Tier_Cascade_Narrative.md` — Narrative account of the tier cascade.

### Sprint and execution documents:

16. `AG_PROMPT_CMR_Sprint_Planning.md` — Sprint structure and Cowork protocol. Source
    for: crash-resilience protocol, pre/post-panel review, Cowork-Sonnet handoff.

17. `SPRINT_TASK_BRIEF.md` — Machine-readable task brief for Cowork.

### Historical documents (consult if available):

18. `THEORY_HIERARCHY_AND_MECHANISMS.md` — Feb 20. T1 roster, ~150 templates.
19. `cross_repo_contract_v2.md` — Software implementation protocol.
20. `Adding_T1_5_Theories_Operationalization.md` — Extraction pipeline SOP.

**If any document is missing, note it and proceed with what you have.**

---

## STEP 2: READ THE EXISTING DRAFT

After reading all source files, read the existing `CMR_ARCHITECTURE_EXPLANATION.md`.
This draft was written partially from memory and partially from source documents.
Treat it as a STARTING POINT, not as authoritative. Specific instructions:

- **Verify every factual claim** against the source documents. If the draft says
  something that contradicts a source file, the source file wins. Correct the draft.
- **Verify every reference**. If a citation appears in the draft but not in any
  source file, mark it `[VERIFY — not found in project files]`.
- **Verify all numbers** — confidence scores, bridge priors, R² values, effect sizes,
  template counts. These must match the source files exactly.
- **Flag any content that was clearly written from memory** rather than from sources.
  The most likely errors: misattributed quotes, wrong confidence scores, invented
  panel debate details, incorrect template IDs or names.

---

## STEP 3: CORRECT, ELABORATE, AND EXTEND

After verifying the draft, do the following:

### A. Correct errors
Fix anything that contradicts the source files. Preserve the prose style but make
the facts match the documents.

### B. Elaborate [TODO] sections
Each `[TODO]` marker in the draft identifies content that needs to be written. For
each TODO:
1. Identify which source file(s) contain the relevant information.
2. Read those files (or re-read the relevant sections).
3. Write the content based on what the files actually say.
4. Cite the source file in a comment if the information is project-internal
   (e.g., "per Transfer doc §2.1" or "per VISUAL-I Output Block 1").
5. For claims about external neuroscience, cite the APA reference from the
   relevant panel output's reference list — do not invent references.

### C. Expand the [DRAFT] sections
Sections marked `[DRAFT]` have initial content. Expand them by:
1. Adding detail from the source files.
2. Adding concrete examples from calibrated panels.
3. Adding nuance about scientific disagreement where the source files note it.

### D. Build the new Section 2.5: Quinean Webs and Bayesian Networks

This is a NEW section that the existing draft does not contain. It belongs after
Section 2.4 (The Multiplicative Structure) and before the worked examples. The
section should address:

**Why the CMR's "Web of Belief" structure is distinct from standard Bayesian
Network reasoning, and what is gained by the Quinean framing.**

The key argument (develop this from the source files and from the relevant
philosophy of science):

1. **Standard Bayesian Networks (BNs)** represent causal or probabilistic
   dependencies as directed acyclic graphs. Each node has a conditional probability
   table. Inference propagates through the graph via Bayes' rule. BNs are powerful
   but they assume: (a) a fixed graph structure, (b) conditional independence
   relations specified in advance, (c) all relevant variables are represented as
   nodes. In a BN, the structure of the network is given BEFORE inference begins.

2. **Quinean Webs of Belief** (Quine, 1951; Quine & Ullian, 1970) represent
   epistemic commitments as a web in which beliefs are connected by inferential
   relations of varying strength. The web has no fixed directionality — revisions
   at any point propagate through the web in all directions. Crucially, the STRUCTURE
   of the web is itself revisable: adding new evidence can change not just the
   credences assigned to nodes but which nodes exist, how they are connected, and
   what counts as evidence for what. Beliefs closer to the center of the web
   (more connected, more entrenched) are harder to revise; beliefs at the periphery
   are easier to revise.

3. **The CMR occupies a novel position between these two frameworks.** It has
   BN-like features: the credence formula is a product of conditional probabilities,
   the template system specifies directed causal chains, and the tier structure
   imposes a hierarchical dependency graph. But it also has Quinean features that
   standard BNs lack:

   a. **Revisable structure**: The T1 roster, the T1.5 roster, and the template
      inventory are not fixed. New T1.5 candidates can be surfaced (Aesthetic
      Anchoring from VISUAL-I). Templates can be added, split, or merged. The
      graph structure changes as the project progresses.

   b. **Entrenchment gradients**: T1 frameworks are more entrenched (harder to
      revise) than T1.5 theories, which are more entrenched than individual
      templates. This is a Quinean property — centrality in the web corresponds
      to resistance to revision. A BN has no native concept of entrenchment.

   c. **Holistic revision**: When a cross-template interaction is discovered
      (e.g., the D × SCI interaction in VISUAL-I), it can force revision not
      just of the two interacting templates but of the theoretical framework
      that treats them as independent. The 12 cross-template flags from VISUAL-I
      propagate through the web, potentially requiring revision in LIGHT-I,
      SPATIAL-I, NEUROMOD-I, and CROSSCUT-I. This is web-like holistic revision,
      not local BN updating.

   d. **Underdetermination and theory choice**: The CMR explicitly acknowledges
      that the same data can be compatible with different theoretical structures
      (e.g., the Olshausen vs. Salingaros debate about whether T1 and VF2 are
      independent channels or aspects of a single system). A BN must commit to
      one structure; the Quinean web can maintain multiple possible structures
      with different credences. The CMR does this via the CROSS_TEMPLATE_INTERACTION
      flags and the "joint computation" notes.

   e. **The bridge warrant as a web-structural element**: In a standard BN, the
      connection between a lab finding and an architectural application would be
      a single conditional probability. In the CMR, it is a TYPED connection
      (CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, etc.) with a qualitative
      character that affects how it responds to evidence. An ANALOGICAL bridge
      responds to new architectural data by potentially jumping to a completely
      different warrant type (EMPIRICAL_COVARIANCE), not just by updating a
      probability. This type-change is a structural revision — the edge in the
      graph changes character, not just weight.

4. **What is gained**: The Quinean framing gives the CMR three capabilities that
   a pure BN approach would lack:
   - The ability to represent and track STRUCTURAL UNCERTAINTY (uncertainty about
     the graph itself, not just about the values at nodes)
   - The ability to handle THEORY CHANGE (the addition of Aesthetic Anchoring as
     a T1.5 candidate changes the structure, not just the values)
   - The ability to represent ENTRENCHMENT (the principled asymmetry between
     revising a T1 framework and revising a single template's confidence score)

5. **The cost**: The Quinean approach is less formally rigorous than a pure BN.
   The CMR's multiplicative formula is a simplification — it treats the three
   factors as independent when they are not (as acknowledged in Section 2.4).
   A full Bayesian treatment would require specifying all conditional dependencies,
   which the CMR cannot currently do for 151 templates with 12 panels of
   cross-template interactions. The Quinean web is a PRACTICAL EPISTEMOLOGY for
   a system too complex for full Bayesian specification.

**Sources to consult for this section**:
- `02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md` — should contain
  the original Web of Belief framing
- `TRANSFER_Feb21_Session8_CORRECTED.md` §1 — mentions "Web of Belief with
  Bayesian causal network properties"
- `VISUAL_I_Panel_Output_Feb21.md` — cross-template flags as examples of
  holistic revision
- Quine, W. V. O. (1951). Two dogmas of empiricism. *Philosophical Review*,
  *60*(1), 20-43. (~15,000 citations)
- Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House.
  (~1,500 citations)
- Pearl, J. (2009). *Causality* (2nd ed.). Cambridge University Press.
  (~30,000 citations) — for the BN comparison
- Levi, I. (1991). *The fixation of belief and its undoing*. Cambridge University
  Press. — for the relationship between Quinean webs and Bayesian updating

**External philosophy of science references to include**:
- Duhem, P. (1906/1954). *The aim and structure of physical theory*. Princeton
  University Press. — Duhem-Quine thesis on holistic theory testing
- Friedman, M. (2001). *Dynamics of reason*. CSLI Publications. — relativized
  a priori and framework revision
- If you know of other relevant references from reading the project files, include
  them. If you are not confident a reference is real, flag it with [VERIFY].

---

## STYLE RULES

- **Bertrand Russell**: clear, intelligent, accessible, no humor.
- **Academic prose**: Paragraphs, not bullet points, for substantive content. Tables
  acceptable for structured data (rosters, hierarchies, panel status).
- **APA references with DOIs** and Google Scholar citation counts where available.
- **Longer substantive treatments preferred** over compressed summaries.
- **Distinguish scientific consensus from genuine disagreement** — name positions
  and proponents.
- **No emojis** in prose.
- **Markdown only**. No .docx.
- **Author context**: Professor of Cognitive Science, UCSD (~35 years). Former MIT
  AI Lab research faculty (1980s). Colleague of David Kirsh. Write at the level
  appropriate for this author.

---

## SAVE PROTOCOL

This document may be long. Use incremental saves:
1. After verifying and correcting the existing draft: SAVE.
2. After writing each new [TODO] section: SAVE.
3. After writing Section 2.5 (Quinean Webs): SAVE.
4. After updating the References section: SAVE.
5. After updating the Session Log: SAVE.

---

## SECTION STRUCTURE (update as needed)

1. Introduction: The Problem CMR Solves
2. The Core Credence Formula
   2.1 P(parent theory)
   2.2 P(bridge)
   2.3 P(CNFA-specific)
   2.4 The Multiplicative Structure and Its Justification
   **2.5 Quinean Webs and Bayesian Networks: Why the CMR Is Neither and Both** ← NEW
   2.6 Worked Example: VF2 (Visual Rhythm)
   2.7 Worked Example: VIEW1 (Nature View Convergence)
3. The Tiered Theoretical Architecture
   3.1 Tier 1: Neurally Grounded Framework Theories
   3.2 Tier 1.5: Domain Theories Formally Reduced to T1
   3.3 Tier 2 and Below
4. Bridge Warrants: Quantifying the Transfer Problem
   4.1 The Warrant Hierarchy in Detail
   4.2 The Constitutive/Mechanism Boundary
   4.3 The Analogical Warrant and Its Limits
5. The Template System
   5.1 Template Structure
   5.2 The 151-Template Landscape
6. Calibration: The Expert Panel Method
   6.1 Panel Composition Principles
   6.2 The Crucible Debate Method
   6.3 From Debate to Calibrated JSON
   6.4 The Review Protocol
7. Confidence Discipline and the Review Protocol
   7.1 Confidence Score Ranges
   7.2 The Coburn R² Ceiling (Generalized)
   7.3 The Red Flag Scan
8. The Panel Sequence and Its Rationale
9. Cross-Template Interactions and the Integration Problem
10. The Allostatic Meta-Principle
    10.1 Sterling's Allostasis and Its Architectural Implications
    10.2 ALLOSTATIC_MASTER_001 (T29): The Master Template
11. IE-DPT: The Implicit-Explicit Dual-Process Elevation
    11.1 What IE-DPT Claims
    11.2 The Kirsh Connection
    11.3 Known Errors in the IE-DPT Specification
12. Computational Implementation: The Article Eater
    12.1 System Architecture
    12.2 The Gap Tracker
    12.3 The Cowork Autonomous Execution Pipeline
13. What the System Cannot Do: Limitations and Residual Gaps
    13.1 The Independence Assumption
    13.2 The Expert Judgment Bottleneck
    13.3 Cultural and Individual Variation
    13.4 The Design-Actionability Gap
14. References
15. Session Log

---

## COMPLETION CRITERIA

The document is considered DRAFT-COMPLETE when:
- [ ] All [TODO] sections have initial content derived from source files
- [ ] All [DRAFT] sections have been verified against source files and expanded
- [ ] Section 2.5 (Quinean Webs) has been written
- [ ] All confidence scores, bridge priors, and template counts match source files
- [ ] All references have been verified against panel output reference lists
- [ ] The Session Log has been updated
- [ ] No `[SOURCE UNAVAILABLE]` markers remain for files that are actually present

The document is considered PUBLISHABLE when:
- [ ] All sections are marked [COMPLETE]
- [ ] An external reader unfamiliar with the project could understand the CMR system
  from this document alone
- [ ] All [VERIFY] markers have been resolved

---

*CC_PROMPT_CMR_EXPLANATION.md — Standing orders for Claude Code*
*Generated: February 22, 2026*
*To be read by CC before any work on CMR_ARCHITECTURE_EXPLANATION.md*
