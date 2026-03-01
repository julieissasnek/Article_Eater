# TRANSFER DOCUMENT — Session 11 (Continued), Feb 25, 2026

**Project**: CMR (Cognitive Neuroscience for Architecture) / "Article Eater" / "Goldilocks"
**Author**: David Kirsh, Dept of Cognitive Science, UCSD
**Session**: 11 (continued after context compaction)

---

## WHAT WAS ACCOMPLISHED THIS SESSION

### TASK 1: MASTER_DOC SUPPLEMENT (Session 11 Part 1 — COMPLETED)
- Expanded pre-crash 465-line skeleton to 947-line, 100K fully developed document
- MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md — all §125-131 written at full density
- File in /mnt/user-data/outputs/

### TASK 2: PHILOSOPHICAL PAPER (Session 11 Parts 1-2 — SUBSTANTIALLY REVISED)

**Paper**: "From Philosophical Metaphor to Computational Architecture: How a Web of Belief Becomes a Working Knowledge System"
**Current version**: PAPER_WoB_Computational_Model_v2.md (905 lines, ~18,000 words + appendices, 7 figures)
**Companion code**: cmr_demo.py (1,211 lines, working Python implementation)

#### Revisions completed this session (Part 2):

**Round 1 — Six craft improvements:**
1. Abstract compressed from ~350 to ~272 words (Philosophy of Science range)
2. Two SVG figures created (architecture diagram + projection loss diagram)
3. Related Work section §1.1 added (ECHO, probabilistic programming, knowledge graphs, AGM)
4. Epistemic-aleatory distinction strengthened in §2.4 with two-claims-at-0.35 worked example
5. Algorithm 1 numerical walkthrough on 5-node subgraph added to §3.2
6. Barrett-Craig worked example expanded to full 5-step lifecycle in §5.4

**Round 2 — Pseudocode, demonstrations, BN-vs-WoB comparison:**
7. Appendix A: Full pseudocode for Algorithms 1, 3, and 6 with design-decision commentary
8. Appendix B: Computational demonstration from working 15-node implementation
   - Table B1: Credence propagation (convergence in 21 iterations)
   - Table B2: Coherence decomposition by edge type (competition only negative contributor)
   - Table B3: VOI rankings (5-HT template #1 priority, ceiling-creativity last)
   - Table B4: BN projection with information loss accounting
   - Table B5-B6: Side-by-side WoB vs BN for daylight-mood and ceiling-creativity queries
   - Four principle demonstrations with computed numbers
9. §6.6 updated — paper no longer claims algorithms unimplemented; subgraph results exist
10. cmr_demo.py — 1,211-line working Python implementation of all six algorithms

**Round 3 — David's latest requests (this round):**
11. Added §1 paragraph on project scope: 1000+ articles codified, supplementation with deep theories from outside the field, mechanism chains as applied causal models from architectural properties to psychological/behavioural outcomes, BN scale (~25 env variables, ~15 outcomes, ~80 edges)
12. Sharpened ECHO critique in §1.1 with two concrete examples (undifferentiated evidence types, binary partition losing the middle range)
13. Sharpened probabilistic programming critique with concrete Pyro example (identical posteriors for epistemologically different claims)
14. Sharpened knowledge graph critique with concrete `(Daylight, increases, Serotonin)` example showing what the KG entry cannot express
15. Sharpened AGM critique with concrete example of structured vs. unstructured revision
16. Expanded sick building syndrome example in §5.3 with what's wrong (critical daylight→5-HT link unsupported in buildings) and what we'd now think (circadian disruption or interoceptive prediction error more likely; VOI flags this for research)

**Round 4 — Five new illustrations for undergraduate accessibility:**
17. Figure 3: Tier hierarchy with all 8 edge types on a concrete 12-node subgraph (§2.2)
18. Figure 4: Epistemic vs. Aleatory — the two-claims-at-0.35 visual comparison (§2.4)
19. Figure 5: Competition resolution — three outcomes from same starting state (§3.3)
20. Figure 6: Bridge warrant ceiling enforcement — strong theory cannot inflate weak evidence (§3.2)
21. Figure 7: Barrett-Craig before/after graph transformation showing reflective equilibrium (§5.4)
All figures referenced inline at their corresponding sections.

### TASK 3: PUSH ANALYSIS FORWARD (Session 11 Part 1 — PARTIALLY COMPLETED)
- TASK3_IMPLEMENTATION_ASSESSMENT.md — priority ordering
- CMR_WEB_INVENTORY_SKELETON_v0.1.json — 40 nodes, 52 edges (partial)
- Four sealed CROSSCUT-I predictions
- Three CC assignments defined

---

## FILES IN /mnt/user-data/outputs/

| File | Size | Status |
|------|------|--------|
| PAPER_WoB_Computational_Model_v2.md | ~119K | **CURRENT VERSION** — 894 lines, 55 sections |
| PAPER_WoB_Computational_Model.md | ~86K | Superseded by v2 |
| cmr_demo.py | ~53K | Working implementation, 15-node subgraph |
| CMR_DEMO_OUTPUT.txt | ~18K | Full output from cmr_demo.py |
| Figure1_Architecture.svg | ~9K | Three-component architecture diagram |
| Figure2_Projection_Loss.svg | ~8K | Mechanism chain → BN edge compression |
| Figure3_Tier_Hierarchy.svg | ~10K | Tier hierarchy with all 8 edge types |
| Figure4_Epistemic_vs_Aleatory.svg | ~8K | Two-claims-at-0.35 visual comparison |
| Figure5_Competition_Resolution.svg | ~10K | Three competition outcomes |
| Figure6_Ceiling_Enforcement.svg | ~8K | Ceiling enforcement: with/without |
| Figure7_Barrett_Craig.svg | ~10K | Barrett-Craig before/after transformation |
| MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md | ~100K | §125-131 at full prose density |
| PANEL_CONSULTATION_PAPER_SHARPENING.md | ~12K | Panel 1 (Framing) |
| REFEREE_SIMULATION_PANEL.md | ~26K | Panel 2 (Adversarial) |
| PANEL_CONSULTATION_III_CONSTRUCTIVE.md | ~15K | Panel 3 (Next-Gen) |
| PANEL_CONSULTATION_IV_OUTSIDE_EYES.md | ~26K | Panel 4 (Outside) |
| TASK3_IMPLEMENTATION_ASSESSMENT.md | ~9K | CC assignments + predictions |
| TRANSFER_Feb25_Session11.md | ~6K | Previous transfer doc (superseded by this) |

---

## PAPER STRUCTURE (v2, current)

1. The Gap — coherentism + causal inference never integrated; 1000+ articles codified
   1.1 Related Work — ECHO, probabilistic programming, knowledge graphs, AGM (all with concrete critiques)
2. The Typed Web of Belief
   2.1 Beyond Quine — mechanist structure with coherentist properties
   2.2 The Formal Object — G = (N, E, τ_N, τ_E, θ)
   2.3 The Eight Edge Types — exhaustive taxonomy with discovered/stipulated distinction
   2.4 Two Kinds of Probability — **STRONG**: two-claims-at-0.35 worked example, different research programmes, different interventions
3. The Algorithms: Making Coherentism Computable
   3.1-3.7 Six algorithms with typed attenuation, numerical walkthrough
   3.8 Complexity summary, pointer to Appendix B
4. The Bayesian Network Interface
   4.1 What BN provides (do-calculus, counterfactuals)
   4.2 What BN cannot provide (explanation, warrants, coherence, structural revision)
   4.3 Projection function (lossy, transportability limitation)
   4.4 Feedback loop
   4.5 Asymmetric relationship (mechanism-based vs. variable-based causal reasoning)
5. The Case Study
   5.1 CMR system (130 nodes, 400 edges, 8 edge types)
   5.2 Panel process as epistemology engineering (social-epistemic limitations acknowledged)
   5.3 What web represents that database cannot (propagation example + **expanded SBS**)
   5.4 Barrett-Craig compromise (**FULL 5-STEP LIFECYCLE**)
6. Testing and Limits
   6.1-6.5 Five levels
   6.6 What tested/not tested (**updated**: subgraph implementation exists)
   6.6b Three candid limitations (tacit knowledge, template format constraints, temporal-sequential gap)
7. Philosophy of Science Implications
   7.1 Coherentism is computable
   7.1.1 Coherence-truth problem (Olsson's challenge, three-component response)
   7.2 Reflective equilibrium partially formalisable
   7.3 Web-BN boundary precise
   7.4 Understanding distributed (Khalifa)
8. Conclusion
References (39 entries, 1921-2021)
Appendix A: Pseudocode for Algorithms 1, 3, 6
Appendix B: Computational demonstration (Tables B1-B6, principle demonstrations)
Figures 1-2

---

## KEY INTELLECTUAL OUTCOMES FROM PAPER PANELS (Session 11 Part 1)

1. Web-BN boundary = mechanism-based vs. variable-based causal reasoning (not non-causal vs. causal)
2. Three-component architecture reconciles coherentism + empiricism
3. Understanding distributed across both structures (Khalifa) — philosophically necessary
4. Transportability problem in projection function (Bareinboim)
5. Temporal-sequential experience = major detectable gap (orphaned T1 predictions)
6. Epistemic-aleatory distinction must be crystal clear — different uncertainties require different research

---

## DECISIONS STILL AWAITING DAVID'S APPROVAL

1. CROSSCUT-I panel structure — keep unified vs. split
2. CROSSCUT-I awe templates — 2 of 3 vs. all 3
3. Paper venue — Philosophy of Science recommended by Panel 1
4. Paper title — current: "From Philosophical Metaphor to Computational Architecture"

---

## CC ASSIGNMENTS (from Session 11 Part 1)

1. Typed diff script (Python: two JSON web states → structured diff)
2. Algorithm 1-3 implementation (Credence Propagation, Coherence Metric, Competition Resolution) — **NOTE: cmr_demo.py now provides reference implementation for these on 15-node subgraph**
3. Interval-valued extension (Algorithm 1 for [c_lo, c_hi])

---

## NEXT SESSION PRIORITIES

1. David reviews paper v2 — venue decision, title decision, structural changes
2. David reviews supplement — approves MASTER_DOC integration
3. David approves CROSSCUT-I structural decisions
4. CC begins typed diff script + full-scale Algorithm 1-3 (using cmr_demo.py as reference)
5. Begin T2 template extraction into JSON (populate CMR_WEB_INVENTORY_SKELETON)
6. Seal formal algorithm-derived CROSSCUT-I predictions (once algorithms running on full web)
7. Consider: paper could benefit from one more pass on the Related Work section (e.g., comparing to Dung's argumentation frameworks, which are cited but not fully critiqued)

---

## SEALED CROSSCUT-I PREDICTIONS (from Session 11 Part 1)

1. AX4 (perceived control) least contested; AX_DOSE_RESPONSE most contested
2. ER_ECOLOGICAL_RATIONALITY_001 won't reach EMPIRICAL_COVARIANCE
3. Aesthetic Anchoring deferred again
4. Awe templates generate most cross-template interaction flags

---

*Transfer document created: Feb 25, 2026*
*Paper version: v2 (905 lines, ~18,000 words + appendices, 39 references, 7 figures, working code)*
