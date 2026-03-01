# CMR Project — Comprehensive Sprint Plan
## Compiled February 25, 2026 | Session 12 (Cowork)
## Based on: TRANSFER_Feb25_Session11.md, MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md, PAPER_WoB_Computational_Model.md

---

# STATUS OVERVIEW

## What Has Been Completed (Sessions 9–11)

1. **MASTER_DOC Supplement fully expanded** — 967-line, ~100K document covering §125–131 (new Parts XIV–XV), Category B deepenings for §49/§56/§70/§71/§85, and the Cowork New-Files Alert Specification. (Source: SUPPLEMENT, lines 1–8)
2. **Philosophical paper drafted** — "From Philosophical Metaphor to Computational Architecture" (~11,800 words main text + appendix), framed for *Philosophy of Science*, revised per 5-person adversarial referee panel. (Source: PAPER, full document)
3. **Panel consultation completed** — Both a framing panel (Haack, Thagard, Pearl, Hartmann, Kelly) and adversarial referee panel (Woodward, Olsson, Bovens, Muller, Andersen) produced. (Source: TRANSFER, §1)
4. **Partial node/edge inventory produced** — 40 nodes, 52 edges in JSON (CMR_WEB_INVENTORY_SKELETON_v0.1.json). Covers T1, T1.5, WM, AX, and reduction edges. (Source: TRANSFER, §1)
5. **Four sealed CROSSCUT-I predictions recorded** — Informal Level 3 predictions. (Source: TRANSFER, §6)
6. **Implementation assessment produced** — Priority ordering, CC assignments, what can be done now vs. what requires CC. (Source: TRANSFER, §1)
7. **11 of 12 panels completed** — 96 calibrated templates. CROSSCUT-I remaining. (Source: TRANSFER, §7)

## What Has NOT Been Completed

### From Session 11 Transfer Doc (§8: Next Session Priorities)
- [ ] David reviews paper draft — decisions on venue, title, structural changes
- [ ] David reviews supplement — approves integration into MASTER_DOC
- [ ] David approves CROSSCUT-I structural decisions (Decisions 1–2 from Session 10)
- [ ] CC begins typed diff script and Algorithm 1–3 implementation
- [ ] Begin T2 template extraction into JSON inventory
- [ ] Seal formal algorithm-derived CROSSCUT-I predictions (once algorithms running)

### From Transfer Doc (§4: Decisions Awaiting Human Approval)
- [ ] **Decision 1**: CROSSCUT-I panel structure — unified vs. split
- [ ] **Decision 2**: CROSSCUT-I awe templates — 2 of 3 vs. all 3 vs. defer
- [ ] **Decision 3**: Paper venue — *Philosophy of Science* recommended; alternatives: *Synthese*, *BJPS*, *Artificial Intelligence*
- [ ] **Decision 4**: Paper title — "From Philosophical Metaphor to Computational Architecture" — David may prefer alternative

### From Transfer Doc (§5: CC Assignments)
- [ ] **CC-1 (HIGH)**: Typed diff script — Python: two JSON web states → structured diff
- [ ] **CC-2 (HIGH)**: Algorithm implementation (Alg 1–3) — Python: Credence Propagation, Coherence Metric, Competition Resolution. Test on 30-node skeleton.
- [ ] **CC-3 (MEDIUM)**: Interval-valued extension (Alg 1) — Extend for [c_lo, c_hi] intervals.

### From Supplement (Category C.6: Current Integration Backlog)
- [ ] REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md → §69 (Classification B, MEDIUM priority, **Pending**)
- [ ] REVIEW_NEUROMOD_I_CLEARANCE.md → §70 (Classification B, MEDIUM priority, **Partially addressed**)
- [ ] FOUNDATIONS_I_PANEL_OUTPUT.md → §128, Appendix (Classification A/C, MEDIUM priority, **Pending**)

---

# WHAT I IDENTIFIED BY CROSS-REFERENCING THE THREE DOCUMENTS

## A. Ideas in the Paper Not Yet Reflected in the Supplement or MASTER_DOC

The PAPER_WoB_Computational_Model.md contains several intellectually developed arguments that go beyond what the supplement covers. These need to be assessed against the MASTER_DOC to determine what's new:

### A.1 The Coherence-Truth Problem (Paper §7.1.1)
The paper contains a fully developed response to Olsson's (2005) impossibility result — the argument that coherence among reports is not truth-conducive. The three-component response (web + BN + testing protocol as a reconciliation of coherentism and empiricism) is articulated more carefully in the paper than anywhere in the supplement. **Action**: Check whether MASTER_DOC §49 or the supplement's §125–127 already contain this argument at this level of development. If not, extract the Olsson response for integration.

### A.2 Mechanism-Based vs. Variable-Based Causal Reasoning Distinction (Paper §4.1)
The paper draws the web-BN boundary not as "qualitative vs. quantitative" or "non-causal vs. causal" but as **mechanism-based vs. variable-based** causal reasoning — citing Illari & Russo (2014). This framing is sharper than the supplement's §126 treatment. **Action**: Verify whether the MASTER_DOC already uses this framing. If the existing §85 still uses the older "qualitative vs. quantitative" framing, this revision is important.

### A.3 Context-Sensitive BN Projection / Transportability (Paper §4.3)
The paper identifies a limitation of the projection function: it generates a context-free BN. It connects this to Bareinboim & Pearl's (2016) causal transportability framework and suggests that the web's Toulmin qualifiers are the raw material for formal transportability conditions. **Action**: This is a concrete extension proposal not present in the supplement. Should be added to §131 (Three Frontiers) or as a new frontier.

### A.4 Trajectory Interactions Gap (Paper §6.6)
The paper identifies that the template format encodes *point* interactions but not *trajectory* interactions — the temporal unfolding of experience as occupants move through spatial sequences. It notes this is an "orphaned prediction" from T1 frameworks (PP, DMN/Place Cells) without T2 instantiation. **Action**: This is a concrete gap the MASTER_DOC should document. Could be flagged for Algorithm 5 (VOI) extension.

### A.5 Phenomenological Dimension (Paper §6.6)
The paper notes the web does not encode the phenomenological dimension of architectural experience — citing Pallasmaa (2005). Whether this is reducible to neural mechanisms or an independent explanatory level is flagged as an open question. **Action**: Check whether the MASTER_DOC addresses this. If not, a brief note in §131 or a new frontier is warranted.

### A.6 Social-Epistemic Limitations (Paper §5.2)
The paper contains a more developed treatment of O'Connor & Weatherall's (2019) social epistemology concerns — specifically distinguishing convergent vs. divergent path dependence and connecting it to the CMR's panel ordering. **Action**: Check whether this analysis exists in the MASTER_DOC. It strengthens the supplement's §127.4 treatment of path dependence.

### A.7 Understanding as Distributed (Paper §7.4)
The paper develops Khalifa's (2017) argument that understanding requires counterfactual reasoning capacity, and argues that scientific understanding in the CMR is *distributed across both structures*. This is a philosophically substantive claim about the structure of understanding itself. **Action**: This may warrant a new subsection in the MASTER_DOC, perhaps in §125 or §126.

## B. Paper as Appendix

The paper should be added as an appendix to the MASTER_DOC. Specifically:
- The full paper text (~11,800 words + appendix tables) should become a new Part or Appendix.
- Suggested location: **Appendix B** (or whatever follows the current appendix structure), with a brief introduction noting it was drafted February 2026 for journal submission and represents the CMR's philosophical self-understanding.
- Cross-references from §125–131 to the paper appendix should be added.

## C. WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md — Staleness Assessment

**Cannot fully assess without the file**, but based on references across all three documents:

- The WEB_OF_BELIEF doc (108K, 2,084 lines) is the *primary source* from which the supplement was derived (SUPPLEMENT, line 10).
- The supplement explicitly states it addresses the WEB_OF_BELIEF doc's content via §125–131 (SUPPLEMENT, C.6 backlog table, line 860: "Addressed by this supplement").
- The paper was also derived from the WEB_OF_BELIEF doc's analysis (PAPER, Appendix A references it).

**Preliminary assessment**: The WEB_OF_BELIEF doc is likely the *source*, not a separate document needing integration — the supplement and paper are its derivatives. However, it may contain material that neither the supplement nor the paper fully captured (the supplement covers §125–131 and Category B, but the WEB_OF_BELIEF doc is 2,084 lines while the supplement is 967 lines). **Action when file is available**: Diff the WEB_OF_BELIEF doc against the supplement to identify any uncaptured material, especially in Parts not covered by §125–131 (e.g., the JSON inventory schema, the detailed flow diagrams, any worked examples).

---

# SPRINT PLAN

## Sprint 0: File Access and Orientation (THIS SESSION)
**Goal**: Get all files, verify completeness, finalize sprint plan

| # | Task | Status | Depends On |
|---|------|--------|------------|
| 0.1 | Mount repo folder or upload MASTER_DOC_CMR | BLOCKED | David |
| 0.2 | Upload or locate WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md | BLOCKED | David |
| 0.3 | Verify MASTER_DOC table of contents and current section numbering | BLOCKED | 0.1 |
| 0.4 | Diff WEB_OF_BELIEF against supplement to find uncaptured material | BLOCKED | 0.2 |
| 0.5 | Finalize this sprint plan with any additional items from 0.3–0.4 | BLOCKED | 0.3, 0.4 |

## Sprint 1: MASTER_DOC Integration — New Sections (Category A)
**Goal**: Insert §125–131 as Parts XIV and XV
**Priority order** (from SUPPLEMENT, lines 20–28):

| # | Task | Source | Target | Priority |
|---|------|--------|--------|----------|
| 1.1 | Insert §125 (Epistemic-Aleatory Distinction) | SUPPLEMENT §125 | After §88 or as Part XIV opener | HIGH |
| 1.2 | Insert §126 (BN's Irreducible Contribution) | SUPPLEMENT §126 | After §125 | HIGH |
| 1.3 | Insert §128 (FOUNDATIONS-I Specification) | SUPPLEMENT §128 | Part XV opener | HIGH |
| 1.4 | Insert §129 (Six Algorithms with Pseudocode) | SUPPLEMENT §129 | After §128 | HIGH |
| 1.5 | Insert §130 (Five-Level Testing Protocol) | SUPPLEMENT §130 | After §129 | HIGH |
| 1.6 | Insert §127 (Reflective Equilibrium Formalized) | SUPPLEMENT §127 | After §126 | MEDIUM |
| 1.7 | Insert §131 (Three Frontiers) | SUPPLEMENT §131 | After §130 | MEDIUM |
| 1.8 | Add Part XIV header and introductory prose | — | Before §125 | MEDIUM |
| 1.9 | Add Part XV header and introductory prose | — | Before §128 | MEDIUM |

## Sprint 2: MASTER_DOC Integration — Deepening Existing Sections (Category B)
**Goal**: Merge Category B material into existing sections

| # | Task | Source | Target | Priority |
|---|------|--------|--------|----------|
| 2.1 | Update §49.5 with web self-sufficiency argument | SUPPLEMENT B.1 | §49.5 | HIGH |
| 2.2 | Update §49.7 with Haack critique response | SUPPLEMENT B.1 | §49.7 | MEDIUM |
| 2.3 | Update §70 with NEUROMOD-I Opus review results | SUPPLEMENT B.2 | §70 | MEDIUM |
| 2.4 | Update §71 with CROSSCUT-I pre-panel clearance | SUPPLEMENT B.3 | §71 | MEDIUM |
| 2.5 | Revise §85 for asymmetric architecture | SUPPLEMENT B.4 | §85 | HIGH |
| 2.6 | Update §56.2 and §56.4 with template counts | SUPPLEMENT B.5 | §56 | MEDIUM |

## Sprint 3: Paper-Derived Additions
**Goal**: Integrate intellectually developed material from the paper that goes beyond the supplement

| # | Task | Source | Target | Priority |
|---|------|--------|--------|----------|
| 3.1 | Integrate Olsson coherence-truth response | PAPER §7.1.1 | §127 or §130 | HIGH |
| 3.2 | Sharpen mechanism-based vs. variable-based framing | PAPER §4.1 | §85, §126 | HIGH |
| 3.3 | Add transportability/context-sensitive BN projection | PAPER §4.3 | §131 (new frontier) | MEDIUM |
| 3.4 | Document trajectory interactions gap | PAPER §6.6 | §131 or new subsection | MEDIUM |
| 3.5 | Add phenomenological dimension note | PAPER §6.6 | §131 | LOW |
| 3.6 | Strengthen path dependence analysis | PAPER §5.2 | §127.4 | MEDIUM |
| 3.7 | Add distributed understanding argument | PAPER §7.4 | §125 or §126 | MEDIUM |

## Sprint 4: Paper as Appendix
**Goal**: Add the full paper to the MASTER_DOC

| # | Task | Priority |
|---|------|----------|
| 4.1 | Add paper as new Appendix with introduction | HIGH |
| 4.2 | Add cross-references from §125–131 to paper appendix | MEDIUM |
| 4.3 | Verify reference consistency between paper and MASTER_DOC | MEDIUM |

## Sprint 5: WEB_OF_BELIEF Assessment
**Goal**: Determine if WEB_OF_BELIEF doc has uncaptured material

| # | Task | Priority |
|---|------|----------|
| 5.1 | Read WEB_OF_BELIEF doc in full | HIGH |
| 5.2 | Diff against supplement to find uncaptured material | HIGH |
| 5.3 | Assess staleness — is it superseded by supplement + paper? | HIGH |
| 5.4 | If stale: mark as historical, add note to MASTER_DOC | MEDIUM |
| 5.5 | If not stale: extract remaining material for integration | MEDIUM |

## Sprint 6: Remaining Integration Backlog
**Goal**: Address files flagged in SUPPLEMENT C.6 that remain pending

| # | Task | Source | Target | Priority |
|---|------|--------|--------|----------|
| 6.1 | Integrate REVIEW_CREATIVE_I_CLEARANCE | REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md | §69 | MEDIUM |
| 6.2 | Complete REVIEW_NEUROMOD_I_CLEARANCE integration | REVIEW_NEUROMOD_I_CLEARANCE.md | §70 | MEDIUM |
| 6.3 | Integrate FOUNDATIONS_I_PANEL_OUTPUT | FOUNDATIONS_I_PANEL_OUTPUT.md | §128, Appendix | MEDIUM |

## Sprint 7: CC Implementation Tasks
**Goal**: Algorithm implementation and tooling (may require Claude Code or dedicated coding session)

| # | Task | Priority | Specification |
|---|------|----------|---------------|
| 7.1 | Build typed diff script | HIGH | Python: two JSON web states → structured diff |
| 7.2 | Implement Algorithm 1 (Credence Propagation) | HIGH | Test on 30-node skeleton |
| 7.3 | Implement Algorithm 2 (Competition Resolution) | HIGH | Test on 30-node skeleton |
| 7.4 | Implement Algorithm 3 (Coherence Metric) | HIGH | Test on 30-node skeleton |
| 7.5 | Complete T2 template extraction into JSON | MEDIUM | Extend 40-node skeleton to full ~130 nodes |
| 7.6 | Implement interval-valued extension (Alg 1) | MEDIUM | Test whether outputs are informatively narrow |
| 7.7 | Generate formal algorithm-derived CROSSCUT-I predictions | MEDIUM | Requires 7.2–7.4 |

## Sprint 8: Human Decisions Required
**Goal**: David makes pending decisions that unblock downstream work

| # | Decision | Context | Urgency |
|---|----------|---------|---------|
| 8.1 | CROSSCUT-I panel structure | Unified vs. split | HIGH (blocks panel execution) |
| 8.2 | CROSSCUT-I awe templates | 2 of 3 vs. all 3 vs. defer | HIGH (blocks panel execution) |
| 8.3 | Paper venue | *Phil Sci* vs. *Synthese* vs. *BJPS* vs. *AI* | MEDIUM |
| 8.4 | Paper title | Current vs. alternative | LOW |
| 8.5 | Approve supplement integration into MASTER_DOC | Category A and B material | HIGH (blocks Sprints 1–2) |

---

# DEPENDENCY GRAPH

```
Sprint 0 (File Access) ──→ Sprint 1 (New Sections) ──→ Sprint 3 (Paper Additions)
                       ──→ Sprint 2 (Deepening)     ──→ Sprint 4 (Paper as Appendix)
                       ──→ Sprint 5 (WEB_OF_BELIEF Assessment)
                       ──→ Sprint 6 (Backlog)

Sprint 8 (Human Decisions)
  8.5 ──→ Sprints 1, 2
  8.1, 8.2 ──→ CROSSCUT-I execution
  8.3, 8.4 ──→ Paper finalization

Sprint 7 (CC Implementation) — largely independent, can proceed in parallel
  7.1 ──→ Sprint 5 (diff tool needed for WEB_OF_BELIEF assessment)
  7.2–7.4 ──→ 7.7 (formal predictions require running algorithms)
```

---

# VERIFICATION CHECKLIST

Before declaring any sprint complete:

- [ ] All inserted sections have correct §-numbering consistent with MASTER_DOC TOC
- [ ] All cross-references between sections are valid (no dangling §-references)
- [ ] All references cited in body text appear in consolidated reference list
- [ ] No duplicate material between supplement sections and existing MASTER_DOC content
- [ ] Bridge warrant hierarchy values are consistent across §125, §128, §129, and paper Appendix A
- [ ] Template counts in §56.2 match actual panel output tallies
- [ ] Paper appendix cross-references point to correct MASTER_DOC sections

---

*CMR_SPRINT_PLAN_Feb25.md — Session 12 (Cowork)*
*Compiled from: TRANSFER_Feb25_Session11.md, MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md, PAPER_WoB_Computational_Model.md*
*For: David Kirsh, Cognitive Science, UCSD*
