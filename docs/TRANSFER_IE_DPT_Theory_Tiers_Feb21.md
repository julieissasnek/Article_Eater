# ⚠️ SUPERSEDED — See TRANSFER_Feb21_Session8_CORRECTED.md for current version

# TRANSFER DOCUMENT: IE-DPT & Theory Tier Architecture
## Session Continuity Brief — February 21, 2026
## Status: ACTIVE WORKING DOCUMENT — update as work progresses
## Supersedes: TRANSFER_IE_DPT_Theory_Tiers_Feb20.md

---

# INSTRUCTIONS FOR NEXT CHAT

Read §1–§8 before doing anything. This document captures the complete state of a multi-session research project. Do not begin work until you understand the architecture (§2), the IE-DPT framework (§3), and the pending work queue (§7). Key source files to request from the user if not already uploaded:

- **THEORY_HIERARCHY_AND_MECHANISMS.md** — authoritative template registry (~150 templates)
- **T1_5_Expansion_Three_Reductions.md** — three T1.5 reductions from Feb 20 (Privacy Regulation, Kaplan Matrix, Adaptive Thermal Comfort) + cross-cutting analysis
- **IE_DPT_Full_T1_Specification.md** — full IE-DPT specification (NEEDS REVISION per §4)
- **T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md** — three T1.5 reductions from Feb 21 (this session's primary output)
- **02-14_07_Theory_Tier_Architecture_V1_0.md** — foundational tier structure document
- **02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1_0.md** — CB/MSI addition, allostasis

The user is a professor of Cognitive Science at UCSD (~35 years), former MIT AI Lab research faculty (1980s), colleague of David Kirsh. Write in Bertrand Russell style: clear, intelligent, accessible, no humor, no bullet-point overuse. Always provide APA references with DOIs. Distinguish scientific consensus from disagreement. Longer answers are preferred when every sentence carries content.

---

# §1. IDENTITY & PROJECT

**User**: Professor of Cognitive Science, UCSD. Prefers (a) APA references with Google Scholar citation counts, (b) clear consensus/disagreement marking, (c) longer substantive answers, (d) full reference lists.

**Project**: "Article Eater" / "Goldilocks" / "CMR" (Compositional Mechanistic Reasoning) — a computational system for evaluating cognitive neuroscience of architecture (CNFA) research claims. Uses a tiered theoretical architecture to evaluate whether and how environmental features affect human cognition, affect, and behavior via specified neural mechanisms. The system implements a Web of Belief with Bayesian causal network properties.

**Core credence formula**:
`P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

When a T1.5 theory gains credence from many supporting papers, any single low-N claim tagged to it inherits a structural confidence boost via the bridge mechanism.

---

# §2. THE THEORETICAL ARCHITECTURE (AUTHORITATIVE STATE AS OF FEB 21)

## 2.1 Tier 1: 10 Neurally Grounded Framework Theories

Each satisfies: (1) mechanistic specificity connecting to neural implementation, (2) cross-domain generativity, (3) convergent multi-method support.

| # | Code | Framework | Core Reference |
|---|------|-----------|---------------|
| 1 | **PP** | Predictive Processing / Active Inference | Friston (2010, ~8,000 GS) |
| 2 | **SN** | Spatial Navigation / Cognitive Mapping | O'Keefe & Nadel (1978, ~10,000 GS) |
| 3 | **DP** | Dual-Process Evaluation | Evans & Stanovich (2013, ~4,000 GS); Kahneman (2011, ~75,000 GS) |
| 4 | **DT** | DMN/TPN Dynamics | Raichle et al. (2001, ~15,000 GS) |
| 5 | **NM** | Neuromodulatory Systems | Schultz, Dayan & Montague (1997, ~12,000 GS) |
| 6 | **IC** | Interoceptive / Constructionist Affect | Barrett (2017, ~4,000 GS); Seth (2013, ~2,500 GS) |
| 7 | **MS** | Memory Systems | McClelland, McNaughton & O'Reilly (1995, ~5,000 GS) |
| 8 | **EC** | Embodied Cognition | Gibson (1979, ~35,000 GS); Varela, Thompson & Rosch (1991, ~15,000 GS) |
| 9 | **CB** | Chronobiological Regulation | Added by neuroscience panel Feb 15 |
| 10 | **MSI** | Multisensory Integration | Added by neuroscience panel Feb 15 |

**Meta-principle**: Allostasis (Sterling & Eyer, 1988) — not a T1 framework but the ultimate explanandum all frameworks serve.

**CRITICAL ERRORS TO AVOID**:
- ART and SRT are NOT T1 theories. They were demoted Feb 14 and reduced to T1.5 with T2 templates.
- IE-DPT is NOT T1 #11. DP was already T1 #3. IE-DPT is an elevation/expansion of DP to superordinate status. The T1 count remains 10.
- The Feb 20 panel briefing (02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md) contains incorrect T1 roster — treat with caution.

## 2.2 Tier 1.5: Domain Theories

Phenomenological organizing schemas — useful labels, not fundamental mechanisms. Reduced to T2 templates with explicit coverage fractions and irreducible residuals. **As of Feb 21, ten theories are formally reduced.**

### Formally Reduced (10)

| # | Theory | Domain | Primary T1 Frameworks | Reduced In |
|---|--------|--------|-----------------------|------------|
| 1 | **ART** (Kaplan, 1995) | Nature/Attention Restoration | PP, DT, SN | THEORY_HIERARCHY |
| 2 | **SRT** (Ulrich, 1983) | Nature/Stress Reduction | NM, IC, PP | THEORY_HIERARCHY |
| 3 | **Biophilia** (Wilson, 1984) | Innate Nature Affiliation | PP, EC, NM, MSI | THEORY_HIERARCHY |
| 4 | **Prospect-Refuge** (Appleton, 1975) | View + Shelter Preference | SN, NM | THEORY_HIERARCHY |
| 5 | **Privacy Regulation** (Altman, 1975) | Boundary Regulation for Social Contact | IC, NM, SN, EC, PP, MS, IE-DPT | T1_5_Expansion (Feb 20) |
| 6 | **Kaplan Preference Matrix** (Kaplan & Kaplan, 1989) | Coherence/Complexity/Legibility/Mystery | PP, SN, NM, EC, DT, IE-DPT | T1_5_Expansion (Feb 20) |
| 7 | **Adaptive Thermal Comfort** (de Dear & Brager, 1998) | Context-Dependent Thermal Tolerance | IC, PP, NM, EC, MS, IE-DPT | T1_5_Expansion (Feb 20) |
| 8 | **Space Syntax** (Hillier & Hanson, 1984) | Spatial Configuration & Movement | SN, PP, EC, IE-DPT | **Feb 21 (this session)** |
| 9 | **Soundscape Theory** (ISO 12913-1; Kang et al., 2016) | Acoustic Environment & Perception | PP, IC, NM, MSI, IE-DPT | **Feb 21 (this session)** |
| 10 | **Place Attachment** (Scannell & Gifford, 2010) | Temporal/Biographical Place Experience | MS, SN, IC, EC, IE-DPT | **Feb 21 (this session)** |

### Candidates Identified, Not Yet Reduced (8 remaining)

| Theory | Domain | Priority | Notes |
|--------|--------|----------|-------|
| Proxemics (Hall, 1966; ~15,000 GS) | Social-Spatial | HIGH | Best neural evidence of any candidate (Kennedy et al., 2009: amygdala lesion → no personal space). May partly collapse into Privacy Regulation. Third-priority candidate. |
| Place Attachment — sub-mechanisms | Temporal/Biographical | HIGH | Reduction revealed it is a cluster of 4–5 distinct mechanisms, not a unified theory. Sub-mechanism tags PA1–PA3 need formal registration. |
| Berlyne Complexity-Preference (1971; ~4,000 GS) | Visual Preference | Standard | May collapse into Kaplan Matrix upon reduction |
| Defensible Space / CPTED (Newman, 1972; ~4,000 GS) | Spatial Configuration | Standard | Partly covered by Space Syntax + Privacy Regulation |
| Crowding Theory (Stokols, 1972; ~2,500 GS) | Social-Spatial | Standard | May collapse into Privacy Regulation |
| Mehrabian-Russell PAD (1974; ~6,000 GS) | Affective Response | Standard | Broad phenomenology, may reduce well |
| Conceptual Metaphor (Lakoff & Johnson, 1980; ~50,000 GS) | Embodied Meaning | Standard | Connects to EC; very broad |
| Savanna Hypothesis (Orians, 1986) | Nature/Restoration | Low | Likely collapses into Biophilia |
| Fractal Fluency (Taylor, 2006) | Visual Preference | Low | Likely collapses into Berlyne/Kaplan |

## 2.3 Tier 2: Mechanistic Templates

Specific causal pathways: Architectural Feature → Neural Mechanism → Outcome. Each has maturity classification (how-actually / how-plausibly / how-possibly). ~150+ templates in the registry (THEORY_HIERARCHY_AND_MECHANISMS.md).

### Templates Proposed But Not Yet Registered (14 total)

**From T1_5_Expansion (Feb 20) — 5 proposed:**

| ID | Name | Frameworks | Source Theory |
|----|------|------------|---------------|
| PR1 | Social Boundary Detection | IC + NM | Privacy Regulation |
| PR2 | Territorial Familiarity | MS + SN | Privacy Regulation |
| KP1 | Scene Coherence Processing | PP | Kaplan Preference Matrix |
| KP2 | Spatial Mystery / Anticipated PE | PP + NM | Kaplan Preference Matrix |
| TC1 | Thermal Expectation Update | IC + PP | Adaptive Thermal Comfort |

**From Feb 21 reductions — 9 new proposed:**

| ID | Name | Frameworks | Source Theory | Maturity |
|----|------|------------|---------------|---------|
| SS1 | Syntactic Integration and Cognitive Map Efficiency | SN + PP | Space Syntax | How-plausibly |
| SS2 | Intelligibility and Predictive Spatial Inference | PP + SN | Space Syntax | How-plausibly |
| SS3 | Isovist Affordance and Perceived Spatial Control | EC + IC + NM | Space Syntax | How-plausibly |
| SOC1 | Acoustic Expectation Violation and Soundscape Appraisal | PP + IC + NM | Soundscape | How-plausibly |
| SOC2 | Acoustic Body-Budget Threat and Cardiovascular Risk | IC + NM | Soundscape | How-actually (cortisol path); How-plausibly (amygdala initiation) |
| SOC3 | Restorative Soundscape and ANS Recovery | PP + NM + IC | Soundscape | How-plausibly |
| PA1 | Biographical Episodic Binding and Place Attachment | MS + SN | Place Attachment | How-plausibly |
| PA2 | Allostatic Calibration and Embodied Security | IC + EC | Place Attachment | How-possibly (full path); How-plausibly (behavioral) |
| PA3 | Displacement Grief and Interoceptive Disruption | IC + MS | Place Attachment | How-plausibly |

**Status**: All 14 proposed templates require formal registration in THEORY_HIERARCHY_AND_MECHANISMS.md using the cross-repo contract format (cross_repo_contract_v2.md).

## 2.4 Tier 3: Empirical Claims

Extracted from scientific literature. Linked to T2 templates via Bridge Warrants (Cartwright typology):

| Bridge Type | Prior Probability | When to Use |
|-------------|------------------|-------------|
| CONSTITUTIVE | P = 0.75 | The architectural feature IS the mechanism (e.g., isovist IS the visual field input) |
| MECHANISM | P = 0.60 | The mechanism causally produces the outcome |
| EMPIRICAL_COVARIANCE | P = 0.60 | Strong observed correlation, mechanism inferred |
| FUNCTIONAL | P = 0.50 | Same functional role, mechanism not specified |
| CAPACITY | P = 0.45 | System has capacity to produce this effect |
| ANALOGICAL | P = 0.35 | Structurally analogous to established mechanism |

## 2.5 The Cascade (How Tiers Relate)

```
  IE-DPT (DP elevated to superordinate configuring role)
              │
    configures boundary conditions for
              │
              ▼
  PP · SN · DT · NM · IC · MS · EC · CB · MSI
              │
    provide neural mechanisms for
              │
              ▼
       ~150+ T2 MECHANISTIC TEMPLATES
       (+ 14 proposed: PR1, PR2, KP1, KP2, TC1,
                       SS1–3, SOC1–3, PA1–3)
              │
    aggregate into / reduce
              │
              ▼
    REDUCED (10): ART · SRT · Biophilia · Prospect-Refuge
                  Privacy Reg · Kaplan Matrix · Adaptive Thermal
                  Space Syntax · Soundscape · Place Attachment
    PENDING (8): Proxemics + 7 others (see §2.2)
              │
    predict/explain
              │
              ▼
       T3 EMPIRICAL CLAIMS
       (12,628 in data/web_persistence.db as of Feb 20)
```

## 2.6 Article Eater Software Architecture (Brief)

- **Extraction pipeline**: LLM + rule-engine tags empirical claims with `theory_id`
- **Mapping dictionaries**: `/src/services/extraction_to_web.py` contains `OUTCOME_DOMAIN_TO_THEORY` and `THEORY_KEYWORDS`
- **Backfill script**: `python3 scripts/patch_web_theories_and_levels.py` — retroactively applies new theory registrations to existing claims without re-running PDF extraction
- **Effect**: When Privacy Regulation, Kaplan Matrix, and Adaptive Thermal Comfort were added Feb 20, running the patch immediately connected 37 dormant claims to the new theories

---

# §3. IE-DPT: CURRENT STATUS

## 3.1 What IE-DPT Is

IE-DPT (Implicit-Explicit Dual Process Theory of architectural experience) is an elevation and expansion of the existing T1 framework DP (Dual-Process Evaluation). It is the system's superordinate modulating framework — not a parallel theory alongside PP, SN, etc., but a configuring layer that sets the boundary conditions for all T1 frameworks.

**Core claim**: The explicit channel (activity frame, semantic context, deliberate attention, goal state, expertise, cultural meaning, biographical history) systematically modulates implicit-channel environmental effects. This modulation is not noise but structured, predictable, and architecturally consequential.

**Two channels**:
- *Implicit channel*: Fast, automatic, below deliberate awareness. Primary substrate: PP prediction errors, IC body-budget signals, NM valence, SN cognitive maps, EC affordances. These are what the other 9 T1 frameworks describe.
- *Explicit channel*: Slow, deliberate, context-sensitive. Mediated by prefrontal systems (DLPFC, vmPFC), semantic memory, and working memory. Sets precision weights, configures category expectations, regulates implicit outputs.

**Kirsh distinction**: Explicit here ≠ Kahneman Type 2 (slow deliberate reasoning). It is Kirsh's sense of explicit: information that has been externalized or made available to deliberate manipulation, whether processing is fast or slow. A professional architect's immediate aesthetic judgment is Kahneman Type 1 but Kirsh-explicit — the result of deeply internalized explicit knowledge.

## 3.2 The Kirsh × Kahneman Matrix

|  | Kahneman Type 1 (automatic) | Kahneman Type 2 (deliberate) |
|--|--|--|
| **Kirsh-Explicit** (cheap extraction) | **Cell A: DESIGN IDEAL** — Organized space, skilled automatic performance | **Cell B: EVALUATIVE** — Organized space under deliberate analysis |
| **Kirsh-Implicit** (costly extraction) | **Cell C: HABITUATION-MASKED** — Automatic processing in poor space | **Cell D: COGNITIVE OVERLOAD** — Effortful processing in challenging space |

Good design moves D → A. Poor design traps occupants in C or D.

## 3.3 IE-DPT Specification Elements

**8 Core Claims (C1–C8)**: From implicit primacy through channel separability to architectural consequences.

**8 Mechanistic Claims (M1–M8)**: Neural substrate of the implicit channel, explicit modulation mechanisms, precision weighting, etc.

**12 Templates (T_IE_001–012)**:
- 001 Activity-Frame Complexity Retuning
- 002 Expertise-Modulated Aesthetic Divergence
- 003 Semantic Override
- 004 Real-Time Activity Frame Shift
- 005 Cost-Gated Threshold
- 006 Placebo Architecture
- 007 Café Paradox
- 008 Trauma-Space Interaction
- 009 McMansion Effect
- 010 Wayfinding × Goal State
- 011 Sacred Space
- 012 Habituation Breakage

**10 Interaction Effects (IX1–10)**: Activity × Complexity, Expertise × Aesthetic, Stress × Override, Dopamine × Memory, Frame × PE, Conflict × Decision Time, Social × Frame, Circadian × Explicit Capacity, Trauma × Environment, Culture × Perception.

**5 Architectural Consequences (DAP1–5)**: Same Room Different Optima, Expertise Invalidates Universal Rules, Habituation-Reengagement Cycle, Semantic Override, Persistence Paradox.

**10 Derived Principles (DAP1–10)**: Alignment, Activity-Tuning, Expertise-Relativity, Implicit Foundation, Sedimentation, Reengagement, Channel Separation Measurement, Cost-of-Control, Semantic Investment, Temporal Asymmetry.

**Source document**: IE_DPT_Full_T1_Specification.md (10,600 words) — NEEDS REVISION per §4.

## 3.4 IE-DPT Superordinate Status: Convergent Evidence

The following table summarizes the six independent domains in which the explicit channel explains the most practically consequential phenomenon — evidence that IE-DPT is not a special-case addition but a structural requirement of the architecture:

| Theory | The Explicit-Channel Indispensable Finding |
|--------|-------------------------------------------|
| Privacy Regulation | density ≠ crowding — density is physical; crowding is an explicit-frame evaluation |
| Adaptive Thermal Comfort | NV building occupants tolerate wider temperature ranges — adaptive frame shifts the acceptable band |
| Kaplan Preference Matrix | individual complexity optima vary — expertise and activity frame shift the preference point |
| Space Syntax | natural movement thesis is a population aggregate — individual goal-states regularly override syntactic pull |
| Soundscape Theory | 55 dBA traffic ≠ 55 dBA birdsong — same level, opposite evaluation; frame-dependent appraisal |
| Place Attachment | rootedness vs. sense of place — unreflective rootedness vs. explicitly constructed meaning operate differently |

Six independent replication instances across thermal, acoustic, social, spatial, visual preference, and biographical domains.

## 3.5 New Theoretical Requirement Identified This Session

**Place Attachment revealed a gap**: IE-DPT's current 12 templates all describe frame-switching at the timescale of minutes to hours. Place Attachment requires extension to biographical timescale — years of deliberate choice, personalization, social investment, and meaning-making sediment into implicit rootedness that is qualitatively distinct from short-term familiarity.

**Proposed extension**: "Biographical Explicit Integration" (BEI) meta-template — the process by which repeated, meaning-laden explicit encounters with a specific place consolidate over months and years into implicit familiarity → territorial security → identity integration. This would be a new structural element in the IE-DPT specification, not merely another T_IE template.

**Why it matters architecturally**: BEI explains (a) why physically identical rebuilt homes after disaster fail to restore pre-disaster wellbeing, (b) why elderly residents resist moving from objectively inferior environments, (c) why owned homes show stronger attachment than equivalent rented homes — in all three cases, BEI history is non-transferable by physical replication alone.

---

# §4. KNOWN ERRORS REQUIRING CORRECTION

**Error 1 — T1 Roster in IE-DPT Specification**: IE_DPT_Full_T1_Specification.md Part V (Integration Matrix) uses the incorrect pre-Feb 14 T1 roster (PP, Berlyne, ART, SRT, Biophilia, Fractal Fluency, Prospect-Refuge, Multisensory, Embodied Cognition, Activity Space). Correct roster: PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI. Fix: revise all cross-references in the integration matrix.

**Error 2 — ART/SRT Status in IE-DPT Specification**: The specification treats ART and SRT as T1 theories that IE-DPT is superordinate over. Correct: they are T1.5. The integration matrix should map against the 9 substantive T1 frameworks (not DP, since DP = IE-DPT itself) and separately show how IE-DPT captures ART/SRT irreducible residuals (Compatibility ~30%, Being Away ~15%).

**Error 3 — DP Framing**: The specification implies IE-DPT is T1 #11. Correct: DP was already T1 #3. IE-DPT is an elevation and expansion of #3 to superordinate/configuring status. T1 count remains 10.

**Error 4 — Panel Briefing**: 02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md contains incorrect T1 roster. Do not use it as an authority for the T1 list.

---

# §5. EMERGENT STRUCTURAL FINDINGS (CUMULATIVE)

These cross-cutting observations have emerged from 10 T1.5 reductions and should inform all future development:

**Finding 1 — IE-DPT superordinate status confirmed across six independent domains** (updated from Feb 20: was three). Every T1.5 reduction independently requires the explicit channel to explain its most practically consequential phenomenon. The convergence across unrelated domains (thermal, acoustic, social, spatial, visual, biographical) is the strongest available evidence for IE-DPT's structural role. See §3.4.

**Finding 2 — Two super-templates are strongly indicated.** IC2 (Body Budget Prediction) appears in 5 of 6 Feb 20–21 reductions. AX4 (Perceived Control) appears in 5 of 6. Both span thermal, acoustic, social, spatial, and biographical domains. These warrant formal elevation to a "super-template" category with privileged cross-reference status in the template registry, or at minimum a dedicated cross-reference index.

**Finding 3 — Irreducible residuals cluster in five categories** (updated from four):
  (a) Explicit-channel effects → IE-DPT captures these
  (b) Cultural/social norms → not yet specified in system
  (c) Individual physiological variation → below cognitive level, not CMR scope
  (d) Temporal dynamics → IE-DPT BEI extension needed (finding from Place Attachment)
  (e) Social/community relational structure → partially within scope but not yet formalized

**Finding 4 — Template re-use reveals hidden structure.** SC2 (Isovist), ENCLOSURE, T8 (Affordances), T66 (Learned Safety), AX4 (Control), IC2 (Body Budget) recur across phenomenologically unrelated domains. The template library is smaller than the theory library. Many T1.5 theories invoke the same mechanisms — which is why reduction is theoretically productive.

**Finding 5 — Place Attachment is not a unified theory.** Unlike ART (unified directed-attention mechanism) or Privacy Regulation (unified boundary-regulation dialectic), Place Attachment is a cluster of four to five mechanistically distinct phenomena (habitat familiarity, episodic binding, identity integration, territorial familiarity, rootedness/sense of place distinction) that happen to co-occur under long-term occupancy. Recommend registering it as a parent tag with five distinct sub-mechanism templates (PA1–PA5, with PA4–PA5 still to be specified) rather than as a unified theory entry.

**Finding 6 — Nature/restoration domain bias corrected.** Original T1.5 roster: 4/4 theories were nature/restoration. Now: 10 reduced theories span nature, social-spatial, visual preference, thermal, spatial configuration, acoustic, and biographical domains. The coverage is now meaningfully pluralistic, though gaps remain (see §6).

---

# §6. DOMAIN COVERAGE MAP (AS OF FEB 21)

| Domain | Covered By | Gap Level |
|--------|-----------|-----------|
| Nature / Restoration | ART, SRT, Biophilia | Well covered |
| Evolutionary spatial preference | Prospect-Refuge | Covered |
| Social-spatial / Boundary regulation | Privacy Regulation | Covered |
| Visual environmental preference | Kaplan Preference Matrix | Covered |
| Thermal / IEQ | Adaptive Thermal Comfort | Covered |
| Spatial configuration / Navigation | Space Syntax | Now covered (Feb 21) |
| Acoustic / IEQ | Soundscape Theory | Now covered (Feb 21) |
| Temporal/Biographical place experience | Place Attachment | Now covered (Feb 21) |
| Interpersonal distance regulation | Proxemics | **Gap — HIGH PRIORITY** |
| Visual complexity (non-Kaplan) | Berlyne | **Gap** |
| Affective valence / arousal / dominance | Mehrabian-Russell PAD | **Gap** |
| Embodied semantic meaning | Conceptual Metaphor | **Gap** |
| Security/surveillance spatial design | CPTED / Defensible Space | **Gap** |

---

# §7. PENDING WORK (PRIORITIZED)

## Immediate — Template Registration

1. Register 14 proposed templates (PR1, PR2, KP1, KP2, TC1, SS1–3, SOC1–3, PA1–3) in THEORY_HIERARCHY_AND_MECHANISMS.md using the cross-repo contract format (cross_repo_contract_v2.md). This is the most time-sensitive technical task — until done, the web of belief cannot connect the new reductions to incoming evidence.

2. Run `python3 scripts/patch_web_theories_and_levels.py` after registering the three new theories (Space_Syntax, Soundscape_Theory, Place_Attachment) and their outcome domains / keywords in `/src/services/extraction_to_web.py`. See §7.1 for the full extraction pipeline entries.

3. Register Place Attachment as a parent theory with sub-mechanism routing — individual claims should be tagged to PA1, PA2, or PA3 (and eventually PA4–PA5) rather than to the parent. Decide on the parent entry format.

## Next Priority — IE-DPT Specification Revision

4. Revise IE_DPT_Full_T1_Specification.md: correct T1 roster throughout, correct ART/SRT status, correct DP framing (see §4).

5. Revise integration matrix: map IE-DPT against the 9 substantive T1 frameworks (PP, SN, DT, NM, IC, MS, EC, CB, MSI) and separately show how it captures ART/SRT irreducible residuals.

6. Connect IE templates (T_IE_001–012) to existing ~150 T2 templates — which templates are directly modulated by which IE templates? This mapping is needed for the Bayesian network's conditional probability tables.

7. Add bridge warrants for each of the 12 IE templates.

8. **New**: Formalize the "Biographical Explicit Integration" (BEI) meta-template as a structural addition to the IE-DPT specification — not just another template but a temporal extension of the sedimentation principle (DAP6) to the biographical scale. This was identified from the Place Attachment reduction (§3.5).

## Next Priority — Super-Template Decision

9. Decide formally on IC2 and AX4 super-template status. Options:
   - **Option A**: Create a designated "Super-Template" tier between T1 and T2 for templates appearing in 4+ unrelated reductions
   - **Option B**: Keep as T2 templates but add a cross-reference index (a "prominence list")
   - **Option C**: Elevate to T1 — but this seems wrong since they are still specific mechanistic pathways, not framework-level theories
   The recommendation is Option B as the least architecturally disruptive move that still grants the empirical prominence its appropriate visibility.

## Next Priority — Next T1.5 Reductions

10. **Proxemics** (Hall, 1966; ~15,000 GS) — HIGH. Best neural evidence of any remaining candidate (Kennedy et al., 2009: amygdala lesion removes personal space). Key question: does it collapse into Privacy Regulation upon reduction, or does it reveal a genuine distinction (Proxemics = immediate, pre-reflective, amygdala-mediated distance regulation; Privacy Regulation = higher-level, dialectical, multi-mechanism boundary management)? Either outcome is architecturally informative.

11. **Berlyne Complexity-Preference** (1971) — STANDARD. Likely reduces well; likely overlaps significantly with Kaplan. The key question is whether the Berlyne reduction adds anything not captured by KP1 (scene coherence) and KP2 (mystery/anticipated PE), or whether Berlyne collapses into the Kaplan Matrix and can be archived.

12. **Crowding Theory** (Stokols, 1972) — STANDARD. May largely collapse into Privacy Regulation. The question is whether "crowding" as a psychological phenomenon has residuals not captured by the density ≠ crowding finding already in PR reduction.

## Medium-term

13. Revise ART and SRT reductions to capture IE-DPT residuals: Compatibility (~30%) and Being Away (~15%) are the two ART constructs with the strongest explicit-channel loading. These should be connected to the revised IE-DPT specification.

14. Read Making_Basic_Research_Relevant.docx (Kirsh paper) — relevant to the Kirsh-explicit distinction.

15. Verify the 4-cell Kirsh × Kahneman matrix against Kirsh's actual published positions.

16. Specify cultural-context module for cultural/social norm residuals (these appear in every reduction as part of the irreducible remainder but there is no CMR mechanism to handle them).

17. Decide on theory collapses before reducing next candidates: Fractal Fluency → Berlyne? Savanna → Biophilia? Crowding → Privacy Regulation? Each collapse decision removes a candidate from the reduction queue.

## Open Theoretical Questions

- Does IE-DPT's superordinate claim apply equally to CB and MSI? Circadian entrainment seems less activity-frame-dependent than complexity preference. Place Attachment reduction suggests CB does involve a biographical-timescale calibration analog — but the mechanism is allostatic rather than frame-based.
- Is Place Attachment's parent theory entry justified given it is a cluster rather than a unified theory? Recommend registering it with an explicit note that claims should be routed to sub-templates.
- Gap studies for IE-DPT templates 8–12 (Trauma-Space, McMansion Effect, Wayfinding × Goal State, Sacred Space, Habituation Breakage) — these templates were proposed but lack direct empirical support. Which has the most tractable research pathway?
- Organize T1.5 roster by domain (natural for practice) or by T1 framework (reveals shared mechanisms)? Current organization is by reduction order. Suggest reorganizing by domain in the next version of THEORY_HIERARCHY_AND_MECHANISMS.md.

---

# §7.1 EXTRACTION PIPELINE ENTRIES FOR NEW THEORIES

The following should be added to `/src/services/extraction_to_web.py`:

```python
# OUTCOME_DOMAIN_TO_THEORY additions (Space Syntax)
"spatial.configuration": ["Space_Syntax"],
"spatial.navigation.wayfinding": ["Space_Syntax", "SN"],
"spatial.movement": ["Space_Syntax"],
"spatial.integration": ["Space_Syntax"],
"spatial.intelligibility": ["Space_Syntax"],
"behav.pedestrian": ["Space_Syntax"],
"affect.spatial.disorientation": ["Space_Syntax"],
"affect.perceived.safety.spatial": ["Space_Syntax", "Prospect_Refuge"],

# THEORY_KEYWORDS additions (Space Syntax)
"Space_Syntax": [
    "space syntax", "hillier", "hanson", "axial analysis", "segment analysis",
    "integration value", "mean depth", "connectivity", "intelligibility",
    "natural movement", "isovist", "syntactic", "spatial network",
    "pedestrian flow", "topological depth", "angular analysis", "depthmap"
],

# OUTCOME_DOMAIN_TO_THEORY additions (Soundscape)
"acoustic.perception": ["Soundscape_Theory"],
"acoustic.annoyance": ["Soundscape_Theory"],
"acoustic.comfort": ["Soundscape_Theory"],
"acoustic.restoration": ["Soundscape_Theory", "ART"],
"health.noise": ["Soundscape_Theory"],
"physio.cortisol.noise": ["Soundscape_Theory", "SRT"],
"affect.soundscape": ["Soundscape_Theory"],

# THEORY_KEYWORDS additions (Soundscape)
"Soundscape_Theory": [
    "soundscape", "acoustic environment", "noise annoyance", "sound perception",
    "ISO 12913", "axelsson", "kang", "schafer", "soundscape evaluation",
    "pleasantness", "eventfulness", "acoustic comfort", "noise sensitivity",
    "sound masking", "speech intelligibility", "biophilic sound", "noise exposure",
    "environmental noise", "perceived noise", "acoustic restoration",
    "circumplex", "soundscape design"
],

# OUTCOME_DOMAIN_TO_THEORY additions (Place Attachment)
"place.attachment": ["Place_Attachment"],
"place.identity": ["Place_Attachment"],
"place.familiarity": ["Place_Attachment", "SN"],
"behav.relocation": ["Place_Attachment"],
"affect.displacement": ["Place_Attachment"],
"affect.rootedness": ["Place_Attachment"],
"health.aging.place": ["Place_Attachment"],
"affect.grief.relocation": ["Place_Attachment"],

# THEORY_KEYWORDS additions (Place Attachment)
"Place_Attachment": [
    "place attachment", "sense of place", "place identity", "rootedness",
    "topophilia", "place bonding", "scannell", "gifford", "lewicka",
    "tuan", "altman", "relocation", "displacement", "aging in place",
    "territorial familiarity", "biographical memory place",
    "place meaning", "home attachment", "place disruption",
    "post-disaster recovery place", "personalization attachment"
],
```

---

# §8. DOCUMENTS PRODUCED (COMPLETE REGISTRY)

## Session Outputs — Feb 21 (This Session)

| File | Contents | Status |
|------|----------|--------|
| **T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md** | Full reductions of Space Syntax, Soundscape Theory, Place Attachment. 9 new T2 templates. Extraction pipeline entries. Full reference list. | **Current — primary output** |
| **TRANSFER_IE_DPT_Theory_Tiers_Feb21.md** | This document | **Living document — update as work progresses** |

## Session Outputs — Feb 20

| File | Contents | Status |
|------|----------|--------|
| **IE_DPT_Full_T1_Specification.md** | Primary IE-DPT specification: 10,600 words. C1–C8, M1–M8, T_IE_001–012, IX1–10, DAP1–10 | **NEEDS REVISION** (§4 errors) |
| **T1_5_Expansion_Three_Reductions.md** | Reductions of Privacy Regulation, Kaplan Matrix, Adaptive Thermal Comfort. 5 proposed templates (PR1, PR2, KP1, KP2, TC1). Cross-cutting analysis. 18-theory roster. | Current |
| **Theory_Tier_Cascade_Narrative.md** | How T1→T2→T1.5 works; corrected roster; ART reduction walkthrough | Current |
| **TRANSFER_IE_DPT_Theory_Tiers_Feb20.md** | Superseded by this document | Archive |

## Historical Documents (User-Uploaded, Still Authoritative)

| File | Date | Authority For |
|------|------|---------------|
| **THEORY_HIERARCHY_AND_MECHANISMS.md** | Feb 20 | T1 roster, template registry, first 7 T1.5 reductions |
| **02-14_07_Theory_Tier_Architecture_V1_0.md** | Feb 14 | Tier structure, T1 criteria, ART/SRT demotion |
| **02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md** | Feb 14 | Template format, causal chains, maturity levels |
| **02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1_0.md** | Feb 15 | CB/MSI addition, allostasis, hospital worked example |
| **02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md** | Feb 15 | Templates 21–30 |
| **cross_repo_contract_v2.md** | Feb 16 | Software implementation protocol for new templates |
| **Adding_T1_5_Theories_Operationalization.md** | Feb 20 | Extraction pipeline SOP; OUTCOME_DOMAIN_TO_THEORY; THEORY_KEYWORDS; backfill script |
| **02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md** | Feb 20 | **CAUTION**: Contains incorrect T1 roster — do not use for T1 list |
| **Making_Basic_Research_Relevant.docx** | — | Kirsh paper — unread, relevant to Kirsh-explicit distinction |

---

# §9. HOW TO BEGIN THE NEXT SESSION

Tell the new chat:

> "Read TRANSFER_IE_DPT_Theory_Tiers_Feb21.md first. It contains the complete state of the CMR / Article Eater / IE-DPT project as of February 21, 2026. We have 10 formally reduced T1.5 theories (the most recent three — Space Syntax, Soundscape Theory, Place Attachment — were completed in the session that produced this transfer document), 14 proposed T2 templates awaiting registration, an IE-DPT specification needing revision (errors documented in §4), and a new theoretical gap identified in §3.5 (the Biographical Explicit Integration extension). The full pending work queue is in §7. The extraction pipeline entries for the three new theories are ready in §7.1. The most time-sensitive task is registering the 14 proposed templates per cross_repo_contract_v2.md."

Then upload the following files:
1. This transfer document (TRANSFER_IE_DPT_Theory_Tiers_Feb21.md)
2. THEORY_HIERARCHY_AND_MECHANISMS.md
3. T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md
4. IE_DPT_Full_T1_Specification.md
5. T1_5_Expansion_Three_Reductions.md
6. cross_repo_contract_v2.md (for template registration format)

---

*Last updated: February 21, 2026, Session 5*
*Next session should begin with §7, items 1–3 (template registration), then items 4–8 (IE-DPT revision)*
