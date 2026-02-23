# ⚠️ SUPERSEDED — See TRANSFER_Feb21_Session8_CORRECTED.md for current version

# TRANSFER DOCUMENT: CMR / Article Eater / IE-DPT Project
## Session Continuity Brief — February 21, 2026, Session 6
## Status: ACTIVE — update frequently; compact risk is REAL in this session
## Supersedes: TRANSFER_IE_DPT_Theory_Tiers_Feb21.md (Session 5)

---

# ⚠️ COMPACT RISK NOTICE

This session loaded three large files at start (THEORY_HIERARCHY ~600 lines, TRANSFER ~488 lines, OPUS_PROMPT ~174 lines) plus generated a full STRESS-I panel output (~450 lines of dense JSON and prose) in the assistant turn, then loaded THEORY_HIERARCHY again. Estimated tokens consumed at document creation: **~60,000–80,000 of ~200,000 context limit** (~35–40%). The session is already in the second half of safe working range. Every substantive work block should trigger an update to this document. If the user's messages stop receiving responses or responses truncate, context has been exceeded.

**Estimated remaining working tokens at time of this draft: ~120,000–140,000.**
**Estimated remaining meaningful work blocks: 4–6 substantial exchanges.**

---

# INSTRUCTIONS FOR NEXT CHAT

Read §1–§9 before doing anything. This document supersedes all prior transfer documents. The most critical new content in this session (Session 6) is:

1. **STRESS-I panel is complete** — T6, T7, T14 calibrated JSON produced and saved as artifacts (see §8)
2. **Gap analysis is in progress** — the 39 gap templates have been partially reconstructed but NOT yet fully enumerated (see §6)
3. **The generalized panel meta-prompt has NOT yet been produced** — this is the primary pending task (see §7)
4. **The gap panel assignment table has NOT yet been produced** — second pending task

Upload list for next session:
- TRANSFER_Feb21_Session6.md (this document — most recent)
- THEORY_HIERARCHY_AND_MECHANISMS.md (authoritative template registry)
- STRESS_I_Panel_Output_Feb21.md (completed panel output — reference)
- T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md (if available)
- IE_DPT_Full_T1_Specification.md (for revision tasks)
- cross_repo_contract_v2.md (for template registration)

---

# §1. IDENTITY & PROJECT

**User**: Professor of Cognitive Science, UCSD (~35 years). Former MIT AI Lab research faculty (1980s). Colleague of David Kirsh. Write in Bertrand Russell style: clear, intelligent, accessible, no humor. APA references with DOIs. Longer substantive answers preferred. Distinguish scientific consensus from disagreement.

**Output format preference (set Session 6)**: Markdown only. Do NOT produce .docx versions of .md files unless explicitly requested. This saves significant tokens per session.

**Project**: "Article Eater" / "Goldilocks" / "CMR" (Compositional Mechanistic Reasoning) — computational system for evaluating CNFA (Cognitive Neuroscience for Architecture) research claims. Tiered theoretical architecture. Web of Belief with Bayesian causal network properties.

**Core credence formula**: `P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

---

# §2. THEORETICAL ARCHITECTURE (AUTHORITATIVE STATE AS OF FEB 21, SESSION 6)

## 2.1 Tier 1: 10 Neurally Grounded Framework Theories

| # | Code | Framework | Core Reference |
|---|------|-----------|----------------|
| 1 | PP | Predictive Processing / Active Inference | Friston (2010) |
| 2 | SN | Spatial Navigation / Cognitive Mapping | O'Keefe & Nadel (1978) |
| 3 | DP | Dual-Process Evaluation | Evans & Stanovich (2013); Kahneman (2011) |
| 4 | DT | DMN/TPN Dynamics | Raichle et al. (2001) |
| 5 | NM | Neuromodulatory Systems | Schultz, Dayan & Montague (1997) |
| 6 | IC | Interoceptive / Constructionist Affect | Barrett (2017); Seth (2013) |
| 7 | MS | Memory Systems | McClelland, McNaughton & O'Reilly (1995) |
| 8 | EC | Embodied Cognition | Gibson (1979); Varela, Thompson & Rosch (1991) |
| 9 | CB | Chronobiological Regulation | Added Feb 15 neuroscience panel |
| 10 | MSI | Multisensory Integration | Added Feb 15 neuroscience panel |

**Meta-principle**: Allostasis (Sterling & Eyer, 1988) — ultimate explanandum all frameworks serve.

**CRITICAL ERRORS TO AVOID**:
- ART and SRT are NOT T1 theories — demoted Feb 14 to T1.5
- IE-DPT is NOT T1 #11 — it is an elevation/expansion of DP (#3) to superordinate status; T1 count remains 10
- The Feb 20 panel briefing (02-20_10) contains incorrect T1 roster — do not use

## 2.2 Tier 1.5: Domain Theories — 10 Formally Reduced

| # | Theory | Primary T1 Frameworks | Reduced In |
|---|--------|-----------------------|-----------|
| 1 | ART (Kaplan, 1995) | PP, DT, SN | THEORY_HIERARCHY |
| 2 | SRT (Ulrich, 1983) | NM, IC, PP | THEORY_HIERARCHY |
| 3 | Biophilia (Wilson, 1984) | PP, EC, NM, MSI | THEORY_HIERARCHY |
| 4 | Prospect-Refuge (Appleton, 1975) | SN, NM | THEORY_HIERARCHY |
| 5 | Privacy Regulation (Altman, 1975) | IC, NM, SN, EC, PP, MS, IE-DPT | T1_5_Expansion Feb 20 |
| 6 | Kaplan Preference Matrix (1989) | PP, SN, NM, EC, DT, IE-DPT | T1_5_Expansion Feb 20 |
| 7 | Adaptive Thermal Comfort (de Dear & Brager, 1998) | IC, PP, NM, EC, MS, IE-DPT | T1_5_Expansion Feb 20 |
| 8 | Space Syntax (Hillier & Hanson, 1984) | SN, PP, EC, IE-DPT | Feb 21 Session 5 |
| 9 | Soundscape Theory (ISO 12913-1; Kang, 2016) | PP, IC, NM, MSI, IE-DPT | Feb 21 Session 5 |
| 10 | Place Attachment (Scannell & Gifford, 2010) | MS, SN, IC, EC, IE-DPT | Feb 21 Session 5 |

### 8 Remaining Candidates (Not Yet Reduced)

Proxemics (Hall, 1966) — HIGH priority; best neural evidence (Kennedy et al. 2009: amygdala lesion removes personal space)
Berlyne Complexity-Preference (1971) — may collapse into Kaplan
Defensible Space / CPTED (Newman, 1972) — partly covered by Space Syntax
Crowding Theory (Stokols, 1972) — may collapse into Privacy Regulation
Mehrabian-Russell PAD (1974) — broad phenomenology
Conceptual Metaphor (Lakoff & Johnson, 1980) — connects to EC
Savanna Hypothesis (Orians, 1986) — likely collapses into Biophilia
Fractal Fluency (Taylor, 2006) — likely collapses into Berlyne/Kaplan

## 2.3 Tier 2: Mechanistic Templates

~150 registered templates in THEORY_HIERARCHY_AND_MECHANISMS.md across these series:
T1-T74 (~60 core), L1-L5 (lighting), MAT1-MAT5 (materials), SC1-SC4 (spatial cognition), SOC1-SOC3 (social), VF1-VF3 (visual form), CREA1-CREA4 (creativity), E1-E6 (memory/emotion), M1-M17 (music/acoustics), AX1-AX12 (cross-cutting), COL1-COL2 (color), TP1-TP4 (temporal), CROSS_* (cross-framework), VIEW1 (nature view), OLF1 (olfactory)

**39 gap templates** exist in the production system (`data/templates/*.json`). Three calibrated by STRESS-I panel (T6, T7, T14). 36 remain.

### 14 Proposed Templates Awaiting Registration

From Feb 20: PR1 (Social Boundary Detection), PR2 (Territorial Familiarity), KP1 (Scene Coherence Processing), KP2 (Spatial Mystery/PE), TC1 (Thermal Expectation Update)

From Feb 21 Session 5: SS1 (Syntactic Integration/Map Efficiency), SS2 (Intelligibility/Predictive Spatial Inference), SS3 (Isovist Affordance/Perceived Control), SOC1 (Acoustic Expectation Violation), SOC2 (Acoustic Body-Budget Threat), SOC3 (Restorative Soundscape/ANS Recovery), PA1 (Biographical Episodic Binding), PA2 (Allostatic Calibration/Embodied Security), PA3 (Displacement Grief/Interoceptive Disruption)

**Status**: All 14 require formal registration in THEORY_HIERARCHY_AND_MECHANISMS.md using cross_repo_contract_v2.md format.

## 2.4 Bridge Warrant Types (Cartwright Typology)

| Type | Prior P | When to Use |
|------|---------|-------------|
| CONSTITUTIVE | 0.75 | The feature IS the mechanism |
| MECHANISM | 0.60 | Causal pathway transferred |
| EMPIRICAL_COVARIANCE | 0.60 | Strong correlation, mechanism inferred |
| FUNCTIONAL | 0.50 | Same function, different mechanism |
| CAPACITY | 0.45 | System has capacity, mechanism unspecified |
| ANALOGICAL | 0.35 | Structural analogy |

---

# §3. IE-DPT: CURRENT STATUS

**What it is**: Elevation and expansion of DP (T1 #3) to superordinate configuring status. Not T1 #11. T1 count remains 10.

**Two channels**:
- Implicit: fast, automatic — what PP, SN, DT, NM, IC, MS, EC, CB, MSI describe
- Explicit (Kirsh sense, not Kahneman Type 2): information available to deliberate manipulation; sets precision weights, configures category expectations, regulates implicit outputs

**Kirsh × Kahneman matrix**:
- Cell A (Kirsh-explicit × Kahneman Type 1): DESIGN IDEAL — organized space, skilled automatic performance
- Cell B (Kirsh-explicit × Type 2): EVALUATIVE — organized space under deliberate analysis
- Cell C (Kirsh-implicit × Type 1): HABITUATION-MASKED — automatic processing in poor space
- Cell D (Kirsh-implicit × Type 2): COGNITIVE OVERLOAD — effortful in challenging space
- Good design moves D → A

**12 Templates (T_IE_001–012)**: Activity-Frame Complexity Retuning, Expertise-Modulated Aesthetic Divergence, Semantic Override, Real-Time Activity Frame Shift, Cost-Gated Threshold, Placebo Architecture, Café Paradox, Trauma-Space Interaction, McMansion Effect, Wayfinding × Goal State, Sacred Space, Habituation Breakage

**Source document**: IE_DPT_Full_T1_Specification.md (10,600 words) — **NEEDS REVISION** (see §4)

**Superordinate status confirmed across 6 independent domains**: Privacy Regulation (density ≠ crowding), Adaptive Thermal Comfort (NV occupant tolerance), Kaplan Matrix (complexity optima), Space Syntax (goal-state override of syntactic pull), Soundscape (55 dBA traffic ≠ 55 dBA birdsong), Place Attachment (rootedness vs. constructed meaning)

**Biographical Explicit Integration (BEI)**: New structural element needed in IE-DPT specification — repeated meaning-laden explicit encounters consolidate over years into implicit rootedness. Not a T_IE template but a temporal extension of the sedimentation principle.

---

# §4. KNOWN ERRORS REQUIRING CORRECTION

**Error 1**: IE_DPT_Full_T1_Specification.md Part V uses incorrect pre-Feb 14 T1 roster. Fix: revise all cross-references in integration matrix.

**Error 2**: Specification treats ART and SRT as T1 theories. Correct: they are T1.5.

**Error 3**: Specification implies IE-DPT is T1 #11. Correct: it is elevation of #3; T1 count remains 10.

**Error 4**: 02-20_10_Panel_Launch_Briefing contains incorrect T1 roster — do not use as authority.

---

# §5. EMERGENT STRUCTURAL FINDINGS (CUMULATIVE)

**Finding 1**: IE-DPT superordinate status confirmed across 6 independent domains (updated from 3 in Feb 20).

**Finding 2**: Two super-templates strongly indicated — IC2 (Body Budget Prediction) appears in 5/6 Feb 20–21 reductions AND in all 3 STRESS-I templates. AX4 (Perceived Control) appears in 5/6 reductions AND in all 3 STRESS-I templates. Both now have 9 convergent instances across unrelated domains. This is among the strongest structural findings of the entire project.

**Finding 3**: Irreducible residuals cluster in 5 categories: (a) Explicit-channel effects → IE-DPT captures; (b) Cultural/social norms → not yet in system; (c) Individual physiological variation → below CMR scope; (d) Temporal dynamics → IE-DPT BEI extension needed; (e) Social/community relational structure → partially in scope, not formalized.

**Finding 4**: Template re-use reveals hidden structure — SC2, ENCLOSURE, T8, T66, AX4, IC2 recur across phenomenologically unrelated domains. Template library smaller than theory library.

**Finding 5**: Place Attachment is not a unified theory — cluster of 4–5 mechanistically distinct phenomena. Register as parent tag with PA1–PA5 sub-mechanism templates.

**Finding 6**: Nature/restoration domain bias corrected — 10 reduced theories now span nature, social-spatial, visual preference, thermal, spatial configuration, acoustic, and biographical domains.

**Finding 7 (NEW, Session 6)**: IC2 and AX4 super-template candidacy further strengthened by independent appearance in all 3 STRESS-I templates. Now 9 independent validation instances each. Option B elevation (cross-reference prominence list) is the recommendation; this should be formally decided before the next batch of gap panels, since these super-templates should be referenced in every subsequent panel prompt.

---

# §6. THE GAP TEMPLATE LANDSCAPE — CONFIRMED STATE (Session 6)

## Critical Correction: Scale is Much Larger Than Originally Stated
The OPUS_PROMPT claimed 39 gaps. The gap_registry_report.md from the production JSON scan reveals the actual situation:
- **Total templates tracked**: 151
- **High severity gaps (5-6 pts — full work required)**: 133
- **Medium severity gaps (3-4 pts — modeling/evidence required)**: 15
- **Calibrated / Completed**: 3 (T6, T7, T14 — done by STRESS-I panel)
- **Total remaining gaps**: 148

This is not 39 gaps in an otherwise calibrated system. It is essentially the full template registry awaiting empirical parameterization. The "39 gaps" figure in the OPUS_PROMPT may have referred to a different or earlier state, or to a subset with `status: "gap"` explicitly set. The severity scoring in gap_registry_report.md uses: missing parameter_range (+3), empty evidence_base (+2), not_calibrated (+1).

## Panel Cluster Assignments (Produced in Session 6 — See §7 and Panel Plan Document)

The 148 gaps have been organized into 12 thematic panels. See the Panel Master Plan document produced in Session 6 for the full cluster table with panel IDs, target templates, discipline requirements, and sequencing.

## Severity tiers
**High (133 templates)**: All have missing_parameter_range + empty_evidence_base + not_calibrated. Full empirical calibration work required.
**Medium (15 templates)**: Have parameter_range or evidence_base partially present; need modeling/evidence work, not full calibration from scratch.

## Confirmed gap_registry.json is now at data/gap_registry.json
Script at scripts/gap_tracker.py supports: --report, --mark-calibrated, --assign, --export-for-panel

---

# §7. PENDING WORK (PRIORITIZED)

## IMMEDIATE — This session or next

**1. Complete gap template enumeration** — Using THEORY_HIERARCHY_AND_MECHANISMS.md, reconstruct the most likely 39 gaps by identifying templates with thin or missing calibration in the registry. Produce a table: Gap ID | Template Name | T1 Frameworks | Panel Discipline Requirements | Priority.

**2. Produce the generalized panel meta-prompt** — Abstract the OPUS_PROMPT_STRESS_I_GAP_PANEL.md structure into a parameterized template with injection points for: target template IDs, mechanism chains, discipline requirements, key papers, constructs to calibrate, and expected JSON format. This is the primary deliverable of Session 6.

**3. Assign gaps to panel clusters** — Group the 36 remaining gaps into thematically coherent panel clusters (analogous to STRESS-I). Each cluster should address 2–5 mechanistically related templates. Produce panel cluster table with panel ID, target templates, and panel discipline requirements.

**4. Produce adapted panel prompts for each cluster** — Fill the meta-prompt template for each cluster. This may take multiple sessions.

## NEXT PRIORITY — Template Registration
**5.** Register 14 proposed templates (PR1, PR2, KP1, KP2, TC1, SS1–3, SOC1–3, PA1–3) in THEORY_HIERARCHY_AND_MECHANISMS.md using cross_repo_contract_v2.md format.

**6.** Run `python3 scripts/patch_web_theories_and_levels.py` after registering Space_Syntax, Soundscape_Theory, Place_Attachment and their keywords/outcome domains in `/src/services/extraction_to_web.py` (full entries in TRANSFER Session 5, §7.1).

**7.** Register Place Attachment as parent theory with sub-mechanism routing (PA1–PA5).

## NEXT PRIORITY — IE-DPT Revision
**8.** Revise IE_DPT_Full_T1_Specification.md: correct T1 roster (Errors 1–3 in §4).

**9.** Revise integration matrix: map IE-DPT against 9 substantive T1 frameworks (PP, SN, DT, NM, IC, MS, EC, CB, MSI).

**10.** Connect T_IE_001–012 to existing ~150 T2 templates — mapping for Bayesian network CPTs.

**11.** Add bridge warrants for each of the 12 IE templates.

**12.** Formalize BEI meta-template as structural addition to IE-DPT specification.

## MEDIUM-TERM
**13.** Formally decide IC2 and AX4 super-template status (recommendation: Option B — cross-reference prominence list).

**14.** Reduce Proxemics — HIGH priority, best neural evidence of remaining candidates.

**15.** Decide on theory collapses before reducing remaining candidates: Fractal Fluency → Berlyne? Savanna → Biophilia? Crowding → Privacy Regulation?

**16.** Read Making_Basic_Research_Relevant.docx (Kirsh paper) — Kirsh-explicit distinction.

**17.** Verify Kirsh × Kahneman 4-cell matrix against Kirsh's actual published positions.

**18.** Specify cultural-context module for cultural/social norm residuals.

---

# §8. SESSION 6 OUTPUTS (COMPLETE REGISTRY AS OF DOCUMENT CREATION)

| File | Contents | Status | Location |
|------|----------|--------|----------|
| STRESS_I_Panel_Output_Feb21.docx | Full STRESS-I expert panel — 10 experts, debate, calibrated T6/T7/T14 JSON, CMR integration note, 16 APA references | COMPLETE | /mnt/user-data/outputs/ |
| STRESS_I_Panel_Output_Feb21.md | Same content, markdown format | COMPLETE | /mnt/user-data/outputs/ |
| TRANSFER_Feb21_Session6.md | This document | ACTIVE — update frequently | /home/claude/ and outputs/ |

---

# §9. DOCUMENTS PRODUCED (COMPLETE REGISTRY, ALL SESSIONS)

## Session 6 (Feb 21, this session)
See §8 above.

## Session 5 (Feb 21)
- T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md — full reductions, 9 new T2 templates
- TRANSFER_IE_DPT_Theory_Tiers_Feb21.md — superseded by this document

## Session 4 (Feb 20)
- IE_DPT_Full_T1_Specification.md — 10,600 words; **NEEDS REVISION** (§4 errors)
- T1_5_Expansion_Three_Reductions.md — Privacy Regulation, Kaplan Matrix, Adaptive Thermal Comfort
- Theory_Tier_Cascade_Narrative.md — corrected roster, ART reduction walkthrough
- TRANSFER_IE_DPT_Theory_Tiers_Feb20.md — superseded

## Historical (User-Uploaded, Still Authoritative)
- THEORY_HIERARCHY_AND_MECHANISMS.md — Feb 20; T1 roster, ~150 templates
- 02-14_07_Theory_Tier_Architecture_V1_0.md — Feb 14; tier structure, ART/SRT demotion
- 02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md — Feb 14; template format
- 02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1_0.md — Feb 15; CB/MSI addition
- 02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md — Feb 15; templates 21–30
- cross_repo_contract_v2.md — Feb 16; software implementation protocol
- Adding_T1_5_Theories_Operationalization.md — Feb 20; extraction pipeline SOP
- Making_Basic_Research_Relevant.docx — Kirsh paper; unread

---

# §10. TOKEN/CONTEXT ESTIMATES FOR SESSION 6

## Estimation methodology
Context window: ~200,000 tokens (Claude Sonnet 4.6 standard)
Input tokens consumed (approximate):
- System prompt: ~8,000
- OPUS_PROMPT file: ~3,000
- TRANSFER_Feb21 file: ~9,000
- THEORY_HIERARCHY file (loaded twice): ~14,000
- First user message: ~100
- STRESS-I panel output (assistant turn): ~12,000
- Second user message: ~50
- File read tools (theory hierarchy second load): ~7,000
- Third user message ("what are the other 35 gaps"): ~50
- Assistant response (planning, honest assessment): ~800
- Fourth user message (upload + current instructions): ~100
- This transfer doc (being written): ~4,000
**Total estimated input: ~58,000–65,000 tokens consumed**

## Remaining capacity
**Estimated remaining: ~135,000–142,000 tokens**
**Estimated remaining substantial exchanges: 5–8**

## Daily/weekly usage estimate
Claude Pro plan: approximately 30–40 messages per day on complex projects with large files; heavier sessions (like this one with large multi-file loads) consume roughly 2–3× the per-message average. This session has consumed approximately 4–5 messages worth of a standard session budget.

**Estimated daily budget used (this session so far): ~25–35%**
**Estimated weekly budget used**: Cannot be calculated without knowing how many sessions occurred this week — please advise if you want this tracked.

---

# §11. HOW TO BEGIN NEXT SESSION

Tell the new chat:

> "Read TRANSFER_Feb21_Session6.md first. It is the complete state of the CMR / Article Eater / IE-DPT project as of February 21, 2026, Session 6. The STRESS-I gap panel is complete (T6, T7, T14 calibrated — artifacts produced). The immediate tasks are: (1) reconstruct the full list of 36 remaining gap templates from THEORY_HIERARCHY_AND_MECHANISMS.md, (2) produce a generalized panel meta-prompt by abstracting the OPUS_PROMPT_STRESS_I_GAP_PANEL.md, (3) cluster the 36 gaps into thematic panel groups and assign discipline requirements to each. The full pending work queue is in §7."

Upload:
1. TRANSFER_Feb21_Session6.md (this document)
2. THEORY_HIERARCHY_AND_MECHANISMS.md
3. STRESS_I_Panel_Output_Feb21.md (as reference for the panel format)
4. OPUS_PROMPT_STRESS_I_GAP_PANEL.md (as reference for the prompt format to generalize)

---

*Created: February 21, 2026, Session 6*
*Next update: after gap enumeration and meta-prompt work*
