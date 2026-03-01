# CMR Project — Final Sprint Plan (Session 12)
## February 25, 2026 | Based on Full Document Review
## Sources: MASTER_DOC_CMR (8,661 lines), SUPPLEMENT (967 lines), PAPER (522 lines), WEB_OF_BELIEF (2,083 lines), TRANSFER (100 lines)

---

# EXECUTIVE FINDINGS

After reading all five documents and cross-referencing them systematically, here is the precise state of the project and exactly what remains to be done.

## Key Discovery 1: The MASTER_DOC already contains §125–131 — but as raw paste

Sections §125–131 have been inserted into the MASTER_DOC as Parts IX-A and IX-B (lines 7474–8661). However, they were **pasted directly from the supplement** and still contain integration metadata like "**Insert after**: §88" and "**Source**: WEB_OF_BELIEF §14". These markers need to be stripped, and the sections need proper editorial integration (transitions, cross-references to existing MASTER_DOC content, removal of supplement formatting).

## Key Discovery 2: Six of seven Paper arguments already exist in the MASTER_DOC

The cross-reference analysis found that all seven intellectually substantive arguments from the paper are already present in the MASTER_DOC, most at equal or greater depth:

| Paper Argument | In MASTER_DOC? | Development Level |
|---------------|----------------|-------------------|
| 1. Olsson coherence-truth response | YES (lines 8480–8494) | Equal |
| 2. Mechanism-based vs. variable-based framing | YES (§85 + §126) | MORE developed |
| 3. Transportability / context-sensitive BN | YES (lines 152, 7553) | LESS developed |
| 4. Trajectory interactions gap | YES (line 8466) | Equal |
| 5. Phenomenological dimension / Pallasmaa | YES (lines 2961, 4704, 8466) | MORE developed |
| 6. O'Connor & Weatherall path dependence | YES (lines 8406–8407) | Equal |
| 7. Khalifa distributed understanding | YES (lines 8520–8522) | Equal |

**Only item 3 (transportability)** needs development — the MASTER_DOC mentions qualifiers in the projection function but does not explicitly connect to Bareinboim & Pearl's transportability framework or articulate the vision of context-sensitive BNs.

## Key Discovery 3: The WEB_OF_BELIEF is NOT stale, NOT superseded

The WEB_OF_BELIEF document contains ~20% unique material not in the supplement — primarily pedagogical scaffolding, algorithm implementation details, and the system architecture narrative. The supplement captures ~80% of the intellectual content in condensed form. **The WEB should be retained as the authoritative source document**, and specific uncaptured material should be extracted for MASTER_DOC integration.

## Key Discovery 4: Category B deepenings have NOT been applied

The supplement's Category B material (deepenings for §49, §56, §70, §71, §85) has NOT been integrated into the MASTER_DOC:
- **§49**: No web self-sufficiency argument, no Haack critique response
- **§56**: Template counts not updated from 103 to actual totals
- **§70**: No Opus review summary, no "best panel in the pipeline" assessment
- **§71**: No pre-panel clearance results
- **§85**: Still uses older symmetric framing; §126.4 explicitly flags this for asymmetric revision

## Key Discovery 5: The Paper is NOT yet an appendix

Appendix A exists (algorithm pseudocode summary), but the paper itself has not been added as an appendix.

## Key Discovery 6: Document is 8,661 lines, not 17,720

The header claims 17,720 lines but the file contains 8,661. This may be a partial export or the count was from a different version.

---

# REVISED SPRINT PLAN

## Sprint 0: Human Decisions Required (BLOCKING)
**Status**: Must be resolved before Sprints 1–4 can proceed

| # | Decision | Context | Urgency |
|---|----------|---------|---------|
| 0.1 | Approve supplement integration | §125–131 already pasted; Category B not yet applied. Approve proceeding with editorial cleanup + B integration? | **HIGH** — blocks Sprints 1–2 |
| 0.2 | CROSSCUT-I panel structure | Unified vs. split | HIGH — blocks panel execution |
| 0.3 | CROSSCUT-I awe templates | 2 of 3 vs. all 3 vs. defer | HIGH — blocks panel execution |
| 0.4 | Paper venue | *Phil Sci* vs. *Synthese* vs. *BJPS* vs. *AI* | MEDIUM |
| 0.5 | Paper title | Current vs. alternative | LOW |
| 0.6 | Confirm document line count | Is the 8,661-line file the complete MASTER_DOC, or is there a longer version? | **HIGH** — affects all integration work |

---

## Sprint 1: Editorial Cleanup of §125–131
**Goal**: Strip supplement metadata, add editorial transitions, verify cross-references
**Depends on**: Decision 0.1
**Effort**: MODERATE (mechanical but careful)

| # | Task | Location | Priority |
|---|------|----------|----------|
| 1.1 | Remove all "**Insert after**:" metadata lines from §125–131 | Lines 7474–8661 | HIGH |
| 1.2 | Remove all "**Source**:" metadata lines | Lines 7474–8661 | HIGH |
| 1.3 | Remove all "[Supplement Category X]" markers | Lines 7474–8661 | HIGH |
| 1.4 | Add editorial transition paragraph at Part IX-A opener | Before §125 | MEDIUM |
| 1.5 | Add editorial transition paragraph at Part IX-B opener | Before §128 | MEDIUM |
| 1.6 | Verify all internal §-references resolve correctly | Throughout §125–131 | MEDIUM |
| 1.7 | Verify reference list at end of §131 is complete | End of §131 | MEDIUM |
| 1.8 | Rename Part IX-A/IX-B to Part XIV/XV (or confirm current naming) | Headers | MEDIUM |

---

## Sprint 2: Category B Deepenings
**Goal**: Integrate the five Category B updates from the supplement into their target sections
**Depends on**: Decision 0.1
**Effort**: SUBSTANTIAL (requires careful merging with existing prose)

| # | Task | Source (SUPPLEMENT) | Target (MASTER_DOC) | What's Missing | Priority |
|---|------|---------------------|----------------------|----------------|----------|
| 2.1 | Add web self-sufficiency argument | B.1 (§49.5) | §49 | Compositional quantitative reasoning argument — web can generate quantitative predictions without BN for many use cases | HIGH |
| 2.2 | Add Haack critique response | B.1 (§49.7) | §49 | Response to "why not just use a BN?" objection | MEDIUM |
| 2.3 | **Revise §85 for asymmetric architecture** | B.4 (§85 revision) | §85 (lines 6513–6624) | §85 currently treats web and BN as roughly equal partners; §126.4 explicitly says this needs revision to reflect asymmetric relationship (web is primary, BN is derivative) | **HIGH** |
| 2.4 | Add Opus review summary to §70 | B.2 (§70 deepening) | §70 (after line 3697) | NEUROMOD-I was assessed as "best panel in pipeline"; Opus review results not mentioned | MEDIUM |
| 2.5 | Add pre-panel clearance to §71 | B.3 (§71 deepening) | §71 (after line 3734) | Seven clearance issues and their resolutions | MEDIUM |
| 2.6 | Update template counts in §56 | B.5 (§56 update) | §56 (lines 894–948) | Verify 103 count matches current state; update §56.2 and §56.4 if needed | MEDIUM |

**Special note on 2.3**: This is the most intellectually consequential Category B task. §85 currently says "Two Structures, One System" and treats the BN and web as co-equal. The supplement's §126 demonstrates that the web can do compositional quantitative reasoning without the BN, making the BN a specialised derivative for interventional/counterfactual queries only. This reframes the entire architecture.

---

## Sprint 3: Paper-Derived Enhancement (Transportability)
**Goal**: Strengthen the one paper argument that is underdeveloped in the MASTER_DOC
**Effort**: LIGHT (single addition)

| # | Task | Source | Target | Priority |
|---|------|--------|--------|----------|
| 3.1 | Expand transportability discussion | PAPER §4.3, Bareinboim & Pearl (2016) | §131 (Three Frontiers) or new frontier | MEDIUM |
| 3.2 | Connect Toulmin qualifiers to formal transportability conditions | PAPER §4.3 | §129.7 (BN Projection) | MEDIUM |

*All other paper arguments are already present at equal or greater depth.*

---

## Sprint 4: Paper as Appendix
**Goal**: Add the full paper to the MASTER_DOC
**Effort**: MODERATE (formatting + cross-references)

| # | Task | Priority |
|---|------|----------|
| 4.1 | Add paper as Appendix B (after existing Appendix A) | HIGH |
| 4.2 | Add introductory note: "Drafted February 2026 for journal submission; represents the CMR's philosophical self-understanding" | MEDIUM |
| 4.3 | Add cross-references from §125–131 to paper appendix | MEDIUM |
| 4.4 | Verify no reference conflicts between paper and MASTER_DOC reference lists | LOW |

---

## Sprint 5: WEB_OF_BELIEF Material Extraction
**Goal**: Integrate the ~20% unique material from WEB_OF_BELIEF that the supplement missed
**Effort**: SUBSTANTIAL (selective extraction from 2,083-line source)

### Priority 1: Must Integrate

| # | Task | WEB Source | MASTER_DOC Target | Estimated Size |
|---|------|------------|-------------------|----------------|
| 5.1 | Panels as epistemology engineering | WEB §15 (~40 lines) | §56 (The Twelve Panels) | ~20 lines condensed |
| 5.2 | Web vs. meta-analyses/systematic reviews | WEB §16 (~55 lines) | §49 (Quinean Webs) | ~25 lines condensed |
| 5.3 | Algorithm implementation details: α factors, λ=0.3 damping, convergence guarantee | WEB §30 (lines 1259–1341) | §129 or Appendix A expansion | ~40 lines |
| 5.4 | Algorithm limitations (semantic, theory generation, causal discovery, ground truth) | WEB §37 (~70 lines) | §129 (new subsection) | ~30 lines |
| 5.5 | Feature-vector representation for domain partitions (Algorithm 2) | WEB §31 (lines 1420–1425) | §129.3 | ~10 lines |
| 5.6 | System architecture diagram | WEB §38 (~60 lines) | §85 or new figure | ~30 lines |
| 5.7 | Information cycle (six-step narrative) | WEB §39 (~40 lines) | New subsection in Part IV or VI | ~25 lines |
| 5.8 | Edge type weights for Algorithm 3 (coherence metric) | WEB §32 (lines 1468–1481) | §129.4 | ~15 lines |
| 5.9 | Entrenchment formula for Algorithm 4 | WEB §33 (lines 1551–1567) | §129.5 | ~15 lines |

### Priority 2: Should Integrate

| # | Task | WEB Source | Target | Notes |
|---|------|------------|--------|-------|
| 5.10 | Adapt WEB conclusion as Part XV finale | WEB lines 1932–1979 | End of §131 | "Knows that it knows, knows why, knows what it doesn't" |
| 5.11 | VOI practical output example | WEB §34 (lines 1678–1682) | §129.6 | Concrete research agenda output |
| 5.12 | BN projection bounds computation (CPT_lo, CPT_hi) | WEB §35 (lines 1726–1729) | §129.7 | For implementers |

### Decision: WEB_OF_BELIEF Document Status

The WEB_OF_BELIEF document should be:
1. **RETAINED** as the authoritative source document for §125–131 content
2. **REFERENCED** in MASTER_DOC Parts XIV–XV with citation
3. **NOT deleted** — it contains pedagogical scaffolding (~400 lines) and algorithm implementation detail (~200 lines) that the supplement and MASTER_DOC compress away
4. **NOT revised** for staleness — its philosophical foundations are timeless; the only outdated element is node counts (reflecting post-STRESS-I state rather than post-NEUROMOD-I), which is clearly marked as an earlier snapshot

---

## Sprint 6: Remaining Integration Backlog
**Goal**: Address files flagged in SUPPLEMENT C.6 still pending
**Depends on**: Access to these files (not currently uploaded)

| # | Task | Source File | Target | Priority | Status per SUPPLEMENT |
|---|------|------------|--------|----------|-----------------------|
| 6.1 | Integrate REVIEW_CREATIVE_I_CLEARANCE | REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md | §69 | MEDIUM | **Pending** |
| 6.2 | Complete NEUROMOD_I clearance | REVIEW_NEUROMOD_I_CLEARANCE.md | §70 | MEDIUM | **Partially addressed** |
| 6.3 | Integrate FOUNDATIONS_I panel output | FOUNDATIONS_I_PANEL_OUTPUT.md | §128, Appendix | MEDIUM | **Pending** |

---

## Sprint 7: CC Implementation Tasks
**Goal**: Algorithm implementation and tooling
**Effort**: SUBSTANTIAL (coding)

| # | Task | Priority | Specification | Depends On |
|---|------|----------|---------------|------------|
| 7.1 | Build typed diff script | HIGH | Python: two JSON web states → structured diff | — |
| 7.2 | Implement Algorithm 1 (Credence Propagation) | HIGH | Use WEB §30 for params: λ=0.3, α table, entrenchment values | Sprint 5.3 |
| 7.3 | Implement Algorithm 2 (Competition Resolution) | HIGH | Use WEB §31 for feature-vector approach | Sprint 5.5 |
| 7.4 | Implement Algorithm 3 (Coherence Metric) | HIGH | Use WEB §32 for edge weights table | Sprint 5.8 |
| 7.5 | Complete T2 template extraction into JSON | MEDIUM | Extend 40-node skeleton to ~130 nodes | — |
| 7.6 | Implement interval-valued extension (Alg 1) | MEDIUM | Walley (1991) imprecise probabilities | — |
| 7.7 | Generate formal CROSSCUT-I predictions | MEDIUM | Requires 7.2–7.4 running | 7.2, 7.3, 7.4 |

---

# DEPENDENCY GRAPH

```
Sprint 0 (Decisions) ─────────────────────────────────────────────────
  │                                                                    │
  0.1 (Approve integration) ──→ Sprint 1 (Cleanup §125–131)           │
  │                          ──→ Sprint 2 (Category B)                 │
  0.6 (Confirm line count)  ──→ All integration sprints                │
  0.2, 0.3 ──────────────────→ CROSSCUT-I execution                   │
  0.4, 0.5 ──────────────────→ Paper finalization                     │
                                                                       │
Sprint 1 (Cleanup) ──→ Sprint 3 (Transportability) ──→ Sprint 4 (Paper Appendix)
                   ──→ Sprint 5 (WEB_OF_BELIEF extraction)

Sprint 2 (Category B)
  2.3 (§85 revision) should precede Sprint 3 (needs correct framing)

Sprint 5 (WEB extraction)
  5.3–5.9 ──→ Sprint 7 (CC implementation needs parameter details)

Sprint 6 (Backlog) — independent; requires file access

Sprint 7 (CC Implementation) — largely parallel once params available
  7.2–7.4 ──→ 7.7 (predictions require running algorithms)
```

---

# RECOMMENDED EXECUTION ORDER

Given the dependencies and David's review cycle:

**Phase A — Can Start Immediately (no decisions needed)**
- Sprint 5 (WEB extraction) — purely additive, does not modify existing content
- Sprint 7.1 (typed diff script) — independent coding task

**Phase B — After Decision 0.1**
- Sprint 1 (Cleanup §125–131) — mechanical, fast
- Sprint 2 (Category B) — requires careful prose editing
- Sprint 3 (Transportability) — light, targeted
- Sprint 4 (Paper as Appendix) — formatting

**Phase C — After Sprints 1–2 complete**
- Sprint 7.2–7.7 (algorithm implementation)

**Phase D — After File Access**
- Sprint 6 (Backlog files)

---

# QUESTIONS THAT AROSE DURING REVIEW

1. **Document completeness**: Is the 8,661-line file the complete MASTER_DOC? The header says 17,720 lines. If sections are missing, the Category B integration targets may not exist in this version.

2. **Part numbering**: §125–131 are currently under "Part IX-A" and "Part IX-B." The supplement proposed "Part XIV" and "Part XV." Which numbering scheme should we use?

3. **§85 revision scope**: The revision from symmetric to asymmetric framing is philosophically significant. Should this be a tracked-changes edit (preserving the original) or a clean rewrite?

4. **WEB_OF_BELIEF disposition**: Should we add it as an additional appendix (Appendix C), or simply reference it? It's 2,083 lines — large for an appendix but valuable as an authoritative source.

5. **Integration backlog files**: Are REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md, REVIEW_NEUROMOD_I_CLEARANCE.md, and FOUNDATIONS_I_PANEL_OUTPUT.md available? They are flagged as pending integration.

---

# VERIFICATION CHECKLIST

Before declaring any sprint complete:

- [ ] All §-references in §125–131 resolve to actual sections in MASTER_DOC
- [ ] No supplement metadata markers remain in the document
- [ ] §85 asymmetric revision is consistent with §126 claims
- [ ] Template counts in §56 match actual panel tallies
- [ ] Paper appendix cross-references point to correct MASTER_DOC sections
- [ ] WEB_OF_BELIEF-derived parameter tables (α factors, edge weights, entrenchment) are consistent with §129 algorithm descriptions
- [ ] All references cited in body text appear in consolidated reference list
- [ ] No duplicate material between newly integrated WEB content and existing MASTER_DOC

---

*CMR_SPRINT_PLAN_FINAL_Feb25.md — Session 12 (Cowork)*
*Compiled from full review of: MASTER_DOC_CMR_2026-02-25.md (8,661 lines), MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md (967 lines), PAPER_WoB_Computational_Model.md (522 lines), WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md (2,083 lines), TRANSFER_Feb25_Session11.md (100 lines)*
*For: David Kirsh, Department of Cognitive Science, UCSD*
