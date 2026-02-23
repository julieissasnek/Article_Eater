# ⚠️ SUPERSEDED — See TRANSFER_Feb21_Session8_CORRECTED.md for current version

# Opus Transfer Context V10.0
## February 18, 2026 — Session: Sprint D Diagnosis, Adversarial Review, Philosopher Presentation

---

## SESSION SUMMARY

This session covered five major work streams:

### 1. Sprint D Agent Deployment
Created agent prompts for three-way parallel execution of Sprint D (data remediation):
- **CC**: D.1 (vocabulary), D.2 (triage), D.5 (gold standard), D.6 (extraction engine), D.12 (CMR integration)
- **Codex**: D.8 (effect size converter), D.3 (table classification), D.10 (batch pipeline)
- **Antigravity**: D.4 (garbage audit), D.7 (gold standard validation), D.9 (web health), D.11 (web rebuild), D.13 (validation)

Files: `SprintD_Agent_Prompts.md`, `SprintD_Addendum_Abstract_Extraction.md`

### 2. Sprint D Results Diagnosis
User uploaded four reports from Sprint D in progress:
- `extraction_validation_report.md`: Precision 0.00, Recall 0.00, F1 0.00. Zero papers with extractions. D.10 batch pipeline hadn't run yet. Gold standard has 15 papers with 139 claims.
- `full_csv_audit_report.md`: 171,840 rows, 92.8% discourse fragments, 7.2% table extractions. Top "high confidence" pairs are garbage: `social→social` (53), `cognitive→cognitive` (29), `wood→wood` (11). Only ~50-80 of 682 "high confidence" pairs contain real signal (~10%).
- `web_of_belief_health_report.md`: 2,068 disconnected components, OCR-corrupted node IDs, 1,609 edges with default credence 0.5. Unsalvageable.
- `FINAL_SYSTEM_ASSESSMENT.md`: Pipeline engineering IS complete (3,654 tests pass, WIS scores differentiate, API works). But claims "Web of Belief Integration ✔" with the 12,628 garbage beliefs. Honest about some limitations but misleading about data quality.

**Key conclusion**: Left half (pipeline engineering) is genuinely complete and working on clean synthetic inputs. Right half (data: extraction, variable resolution, web population) is broken. Sprint D bridges the gap.

### 3. Mapping Precision Analysis (Doc 71)
Diagnosed FIVE specific failure modes in PDF→claim extraction:

1. **Table Structure Blindness**: pdfplumber extracts cells but system doesn't know column roles (IV column vs statistic columns). Fix: table-type-aware extraction templates (regression, ANOVA, correlation, descriptive).

2. **DV Is In The Caption, Not The Table**: In most results tables, the dependent variable appears ONLY in the table caption ("Table 3: Regression predicting **creative performance**"). The system looks only at cell content. Fix: caption-first DV extraction — always check caption for "predicting X", "effects on X", "X by condition" BEFORE looking at cells. **THIS IS THE SINGLE HIGHEST-IMPACT FIX.**

3. **Synonym Coverage Too Thin**: Only 9 synonym mappings and 5 synonym groups. Needs 200+ covering measurement instruments (RAT, PANAS, STAI), abbreviations (CCT, SPL, RT60), physiological markers (cortisol→stress), theoretical terms (prospect→spatial_openness).

4. **Forced Matching Produces Confident Wrong Answers**: "instruction" matched to "hazard_indicators" at 87% confidence. Fix: matching threshold with rejection class — return None if best match < 0.65. Blacklist common non-variable terms.

5. **OCR Corruption Not Detected**: Character doubling, concatenated words, garbled encoding. Fix: OCR quality gate as pre-filter before table classification.

### 4. Abstract + Caption Extraction (NEW Tasks D.14, D.15)

**Critical gap identified**: Sprint D focused entirely on tables but neglected abstracts, which are arguably the BEST source. Abstracts are clean text, author-curated, multi-claim (2-4 per paper), and available for nearly all 386 papers.

Created two new tasks:
- **D.14** (CC): `src/extraction/abstract_extractor.py` — extract claims from abstracts AND figure/table captions. Also produces `caption_dv_lookup.json` mapping table IDs to their caption-derived DVs (this fixes table extraction too).
- **D.15** (Codex): Merge abstract claims + caption claims + table claims in batch pipeline. Wire caption DV lookup into table extraction.

Expected yield: ~950 claims from abstracts + ~300 from captions, plus improved table extraction precision from caption DVs. Abstract extraction alone may yield MORE high-quality claims than table extraction.

**Told user to PAUSE Antigravity's D.11 (web rebuild)** until Codex finishes D.15, since the input data is about to change fundamentally. AG should prep/test the web_rebuilder.py against synthetic data while waiting.

### 5. Table Extraction Effectiveness Assessment
Assessed current end-to-end table extraction:
- Tables detected in PDFs: ~60-70% (pdfplumber misses tables without ruled lines)
- Correctly parsed cell structure: ~40-50% (column alignment failures)
- Correct IV/DV extraction from parsed cells: ~5-10%
- **Net yield: ~2-3% of claims in tables correctly extracted end-to-end**

**Image/illustration handling: completely absent.** Three tiers proposed:
- **Tier 1 (do now)**: Figure caption extraction — added to D.14. Almost free.
- **Tier 2 (post-Sprint D)**: Chart-to-data via vision model. 15-20 agent-hours.
- **Tier 3 (defer)**: Architectural stimulus classification from photos. Research frontier.

### 6. Adversarial Review Prompt
Created `adversarial_review_prompt.md` — a comprehensive adversarial review to run inside the repo after Sprint D completes. Features:
- **7 expert reviewers**: Computational Epistemologist, Software Architect, Research Methodologist, Cognitive Scientist/Neuroscientist, Practicing Architect, Data Engineer, Philosopher of Science
- **4 end-to-end tests**: New paper eval, 3 real buildings (Maggie's Centre vs windowless basement vs open-plan tech office), sensitivity check, Ulrich baseline
- **5 user types evaluated**: Practicing architect, researcher, policy maker, developer, student
- **Support matrix**: Which capability × which user type = works/broken/missing
- **Output**: Kill-or-keep verdict per subsystem, priority fix list, gap analysis to MVP per user type

### 7. Philosopher Presentation (INCOMPLETE — needs next session)
Started building a presentation for Andy Clark and philosophers. Created:
- `Presentation_Andy_Clark_Article_Eater.md` — good content on Goldilocks theory, use cases, prediction generation examples, Quinean web philosophy, system architecture. BUT:
- `article_eater_architecture.jsx` — interactive diagram with 5 components, click for details
- Word document generation script — CUT OFF mid-Section 3.4 (Bayesian Network). Incomplete.

**CRITICAL USER FEEDBACK FOR NEXT SESSION — the presentation needs:**

1. **EXPLAIN WHAT A TEMPLATE IS CONCRETELY.** The word "template" is used throughout as if self-explanatory. Show 2-3 complete template examples with all fields (input, output, mechanism chain, parameters, scope conditions, moderators, interactions). Walk through one template in detail so a philosopher who has never seen the system understands what a template IS.

2. **LIST ALL THE THEORIES AND SHOW HOW TEMPLATES DERIVE FROM THEM.** The doc mentions ART, SRT, Biophilia but doesn't enumerate the full theory inventory or show the reduction process. Need:
   - Full list of theories the system engages with (ART, SRT, Biophilia, Prospect-Refuge, PP/FEP, Berlyne's aesthetics, embodied cognition, thermal comfort models, circadian biology, etc.)
   - For each theory: what constructs does it contribute? Which templates capture them?
   - Show a concrete example: "ART says X. This decomposes into constructs A, B, C. Construct A maps to templates T14 and T15 because [specific mechanism]. Construct B maps to template T22 because [specific mechanism]. The irreducible residual is D — what ART claims that NO current template captures."

3. **THE THEORY-TO-TEMPLATE REDUCTION IS ITSELF A CONTRIBUTION.** David explicitly flagged this. The formal reduction of ART/SRT/Biophilia to mechanistic templates — showing which parts are captured, which compete, and which are irreducible — is novel philosophical/scientific work independent of the software. The presentation should highlight this as a contribution in its own right, not just a design decision.

4. **THE BAYESIAN NETWORK SECTION NEEDS COMPLETION.** The docx script was cut off mid-BN. Needs: relationship between BN and web (complementary: web = coherentist "what is believed", BN = foundationalist "what causes what"), how BN parameters derive from templates, worked inference example.

5. **SHOW A CLEAR WORKED EXAMPLE OF ANSWERING A QUESTION.** Not just "the system can do X" but: here is a specific question, here are the exact steps the system takes, here is the output at each stage, here is the answer with uncertainty and provenance. The prediction generation examples (morning light + creativity, wood + pain, curved hallways) are excellent but need the SYSTEM TRACE showing how each step produces them.

---

## FILES CREATED THIS SESSION

| File | Status | Description |
|------|--------|-------------|
| `SprintD_Agent_Prompts.md` | ✅ Complete | Prompts for CC, Codex, Antigravity |
| `SprintD_Addendum_Abstract_Extraction.md` | ✅ Complete | D.14 + D.15 addendum prompts |
| `Doc71_SprintD_Diagnostics_and_Precision_Fix.md` | ✅ Complete | 8 diagnostic queries + 5 failure modes + abstract extraction spec |
| `adversarial_review_prompt.md` | ✅ Complete | 7-expert adversarial review + end-to-end tests + user types |
| `Presentation_Andy_Clark_Article_Eater.md` | ✅ Complete | Presentation notes (good, but see feedback above for improvements) |
| `article_eater_architecture.jsx` | ✅ Complete | Interactive architecture diagram |
| Word document (.docx) | ❌ INCOMPLETE | Script cut off mid-Section 3.4. Needs restart. |

---

## CURRENT SPRINT STATUS

### Sprint D (Data Remediation) — IN PROGRESS
- D.1–D.13: Original tasks deployed to CC, Codex, AG
- D.14–D.15: New abstract/caption extraction tasks added (addendum sent)
- AG D.11 (web rebuild): PAUSED pending D.15 completion
- Extraction validation: still 0/0/0 as of last report (D.10 not yet run)

### Sprints 12-13 (Pipeline Engineering) — DECLARED COMPLETE
- 3,654 tests pass, API works, building eval differentiates
- Final System Assessment says "production-ready" (true for pipeline, false for data)

### Adversarial Review — READY TO DEPLOY
- Prompt complete at `adversarial_review_prompt.md`
- Run AFTER Sprint D completes (so reviewers see clean data, not garbage)
- Assign to CC, Codex, and Antigravity inside the repo

---

## IMMEDIATE PRIORITIES FOR NEXT SESSION

1. **Check Sprint D progress** — Run the 8 diagnostic queries from Doc 71 Part 1 to see what's landed
2. **Complete the philosopher presentation** — Incorporate all 5 feedback items above. Templates need concrete examples. Theories need enumeration. Reductions need to be highlighted as novel contribution. BN needs completion. Worked question-answering example needed.
3. **Generate the Word document** — The .docx was cut off mid-generation. Restart with the improved content.
4. **Monitor D.14/D.15 landing** — Once abstract extraction + merge is done, unblock AG for D.11 web rebuild
5. **Deploy adversarial review** — When Sprint D validates clean, run the review

---

## KEY ARCHITECTURAL INSIGHTS FROM THIS SESSION

**The system has two halves, and they're at very different maturity levels:**
- LEFT (pipeline): Complete, tested, working on clean input. Real computation, not placeholders.
- RIGHT (data): Broken. The 171k-row CSV is 93% discourse fragments + 7% garbage. Sprint D fixes this.

**Abstract extraction may be more valuable than table extraction.** Clean text, no OCR, author-curated, multi-claim. Expected ~950 high-quality claims vs table extraction's ~500-800 after quality filtering. And abstracts are available for nearly all 386 papers, not just the ~150 with extractable tables.

**The caption DV lookup is a bridge between extraction channels.** CC's D.14 produces caption_dv_lookup.json as a side output. Codex's D.10/D.15 wires it into table extraction. One artifact, two benefits: claims from results-figure captions + precision fix for table extraction.

**The Goldilocks theory is genuinely distinct from PP.** Three commitments PP cannot generate: normative (optimal PE level), multi-channel (profile across channels), contextual (depends on task). PP provides mechanism; Goldilocks provides the normative framework for design application.

---

## TRANSCRIPT LOCATION
Full conversation transcript: `/mnt/transcripts/` (check for latest dated file)
Previous transcripts catalogued in: `/mnt/transcripts/journal.txt`

---

*Transfer Context V10.0 — February 18, 2026*
