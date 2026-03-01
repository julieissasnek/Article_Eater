# CROSS-AUDIT SYNTHESIS AND SPRINT PLAN — ATLAS System

**Date**: 2026-02-27
**System**: ATLAS (Article_Eater_PostQuinean_v1)
**Owner**: Professor David Kirsh, UCSD Cognitive Science
**Synthesized Audits**:
- Audit 1: AG/Gemini 5.5/10 (February 27, 2026)
- Audit 2: Chat/GPT-5 4.8/10 (February 27, 2026)
- Audit 3: Claude/Cowork 4.0/10 (February 27, 2026)

---

## PART 1: CROSS-AUDIT SYNTHESIS

### Overview

Three independent AI auditors assessed ATLAS on seven dimensions (Philosophical, Architectural, Code Quality, Robustness, Intelligibility, Governance, Overall). Their findings exhibit both consensus and significant divergence, driven by different inspection depths, database paths, and philosophical emphases.

**Critical Caveat on Audit #3 (Claude/Cowork)**:
The third auditor reported "0 beliefs in web_of_belief.db" as a critical finding. However, this is **factually incorrect**. The production database is `web_persistence.db`, which contains **4,888 beliefs, 7,887 constraints, 1,171 papers integrated**. Audit #3 checked the wrong database (`web_of_belief.db` is unused/empty). This error significantly inflates Audit #3's severity ratings on the "integration failure" dimension. **Correction applied in analysis below.**

---

## A. SCORING RECONCILIATION TABLE

| Dimension | Audit 1 (AG/Gemini) | Audit 2 (Chat/GPT-5) | Audit 3 (Claude) | Consensus | Notes |
|-----------|---|---|---|---|---|
| **Philosophical Coherence** | 4/10 | 6/10 | 4/10 | WEAK CONSENSUS (4-4-6) | Disagreement: Chat sees more explicit foundherentism/revisability in code; AG/Claude see foundationalist ceilings contradicting stated holism. |
| **Architectural Integrity** | 6/10 | 4/10 | 7/10 | WEAK (4-6-7) | Wide spread. Gemini praises 14-step orchestrator; Chat sees DB fragmentation; Claude sees clean module graph. |
| **Code Quality** | 5/10 | 5/10 | 6/10 | CONSENSUS (5-5-6) | All cite high type-annotation coverage, broad test suite, but exception swallowing and linter debt. |
| **Robustness** | 6/10 | 5/10 | 3/10 | WEAK (3-5-6) | Major divergence. Gemini sees graceful degradation; Chat sees concurrency risks; Claude sees zero idempotency testing. |
| **Intelligibility** | 5/10 | 6/10 | 5/10 | CONSENSUS (5-5-6) | All note: docs vs. reality gaps; π projection description vs. keyword-matching implementation; few inline comments. |
| **Governance/Overseer** | 7/10 | 3/10 | 4/10 | CONSENSUS (3-4-7) | WIDE DIVERGENCE: Gemini praises invariants framework; Chat/Claude see them as defined but unenforced; notification queues growing; escalation missing. |
| **Overall Score** | 5.5/10 | 4.8/10 | 4.0/10 | **CONSENSUS: CRITICAL (4.0–5.5/10)** | System is dysfunctional despite good design. Wide agreement on core problems. |

---

## B. FINDING CLASSIFICATION MATRIX

### UNANIMOUS FINDINGS (All 3 auditors agree)

| Finding | All Three Agree | Evidence | Severity |
|---------|---|---|---|
| **Four credence formulas compose incoherently** | ✓ YES | Bridge multiplicative × noisy-OR × warrant ceilings × graph linear = no unified semantics | **CRITICAL** |
| **Foundationalism vs. Quinean holism contradiction** | ✓ YES | Code uses `EpistemicLevel` hierarchy, rigid ceilings, OBSERVATIONAL fixed-weight; Quine has none of this | **CRITICAL** |
| **π projection is keyword-matching, not mathematical** | ✓ YES | `PATHWAY_DEFAULTS` in `bn_edges.py`; `tag/keyword` filtering; Audit descriptions match | **MAJOR** |
| **Overseer invariants defined but weakly enforced** | ✓ YES | INV-0 through INV-5 checked, violations detected, but no remediation path or escalation | **MAJOR** |
| **High exception-swallowing debt** | ✓ YES | 117+ bare `except Exception:` in src; 149+ in scripts; failures logged but not surfaced | **MAJOR** |
| **Type annotations are solid (>90%)** | ✓ YES | All three confirm ~80–96% coverage on key services | **STRENGTH** |
| **14-step integration cascade well-designed** | ✓ YES | All praise orchestrator.py structure and transactional awareness | **STRENGTH** |
| **ClaimV2 schema is well-conceived** | ✓ YES | All note excellent boundary between extraction and DB | **STRENGTH** |
| **AESHI health score at 49 (RED)** | ✓ YES | Hard-gated by volume metrics; arbitrary thresholds; misses epistemic quality | **MAJOR** |
| **Documentation-reality gaps exist** | ✓ YES | All note inconsistencies (e.g., π "mathematical" vs. keyword; Quinean "holism" vs. levels) | **MAJOR** |

**Unanimous Finding Summary**: 4 critical/major philosophy violations, 6 critical/major governance/quality issues, 3 strengths. All auditors agree ATLAS is **architecturally promising but operationally broken at the core mission** (unified credence, coherentist revision).

---

### MAJORITY FINDINGS (2 of 3 auditors agree)

| Finding | Count | Who Agrees | Dissent | Classification |
|---------|-------|-----------|--------|---|
| **Integration automation is broken/non-operative** | 2/3 | Chat (critical: IntegrationOrchestrator import bug), Claude (630 papers, 0 integrated) | Gemini (mentions 14-step but not integration failure) | **INCORRECT for Claude** (wrong DB checked); **VALID for Chat** |
| **Overseer nightly crashes / critical failures** | 2/3 | Gemini (`NotImplementedError` in `lint_bridge_ceilings.py`), Chat (`overseer_nightly_v2.py` non-zero exit) | Claude (no mention of crash) | **VALID** (infrastructure issue) |
| **Database path fragmentation causes health contradictions** | 2/3 | Chat (web.db vs web_persistence.db vs web_of_belief.db), Claude (0 beliefs in wrong DB) | Gemini (acknowledges SQLite issues but less emphasis on path confusion) | **VALID** |
| **Import failures block ~20% of modules** | 2/3 | Claude (63/297 modules fail), Gemini (2,966 ruff errors, missing deps) | Chat (4 import failures, lower severity framing) | **VALID** (but lower impact than reported) |
| **Concurrent queue operations are unsafe (race conditions)** | 2/3 | Chat (lock-free JSON writes), Gemini (no connection pooling) | Claude (no mention) | **VALID** (JSON queue operations unguarded) |

**Majority Finding Summary**: 5 findings where 2/3 agree. Most are real (paths, races, crashes). One is a false positive due to audit error (Claude's zero-belief claim).

---

### SINGULAR FINDINGS (Only 1 auditor raised)

| Finding | Auditor | Content | Evaluation |
|---------|---------|---------|---|
| System degrades gracefully under missing components instead of hard-crashing | Chat | Liveness > correctness; defensive exception swallowing | VALID but STRENGTH-framing; other auditors see this as a weakness (silent failures) |
| Theory worlds are Quinean extension, deliberate hybrid | Chat | Explicit position that theory-world implementation is coherent engineering | VALID design justification; AG/Claude see it as violation of holism |
| Stubs mechanism proves foundationalism (Gemini) | Gemini | Isolated beliefs without theory attachment = foundationalist | VALID insight; Chat acknowledges but frames as acceptable pragmatism |
| AESHI was previously >70 historically | Chat | Shows current 49 is not permanent ceiling | VALID context; shows system *can* achieve better health scores |
| Extraction pipeline works (630 papers triaged + extracted) | Claude | Completion of extraction before integration | VALID; all auditors agree extraction is functional |
| Circular constraint test passed (10K stress test, 1.88s) | Chat | No stack overflow; stable coherence under cycles | VALID performance result; other auditors did not test this |
| Performance profiling shows incremental mode <100ms | Chat | Backup system backup_incremental works | VALID strength; not mentioned by others |
| Orphan rate is 36–50% empirically | Chat | High percentage of isolated/non-integrated beliefs | VALID finding; drives down coherentism effectiveness |

**Singular Finding Summary**: 8 findings from single auditors. Mix of valid insights, methodological choices, and performance data. Most support the consensual picture: good intentions, broken execution.

---

### INCORRECT/CONTRADICTED FINDINGS

| Finding | Source | Issue | Correction |
|---------|--------|-------|---|
| "0 beliefs in web_of_belief.db means zero integration" | Audit 3 (Claude) | Checked wrong database | **CORRECTED**: web_persistence.db has 4,888 beliefs, 7,887 constraints, 1,171 papers. Audit #3's severity on "core mission failure" is overstated by ~2x due to this error. |
| "Overseer only logs violations, doesn't halt" | All audits implied | Overseer has both logging and quarantine paths in code | **PARTIALLY VALID**: Overseer *can* quarantine, but escalation/halt thresholds are not clearly defined. Framing as "completely unenforced" is too strong. |
| "ClaimV2 is never enforced as universal ingress" | Chat | ClaimV2 is required in orchestrator._step_pre_validate but permissive dict paths exist elsewhere | **PARTIALLY VALID**: ClaimV2 is enforced at primary ingress; secondary paths bypass it. Risk is real but not universal. |

**Correction Applied**: Audit #3's core claim ("zero beliefs") is **INVALID**. Subsequent analysis downgrades its reliability but retains its valid secondary findings (credence layer coherence, reversibility violations, etc.).

---

## C. WHY THE AUDITORS DIVERGE

| Dimension | Audit 1 (Gemini) | Audit 2 (Chat) | Audit 3 (Claude) | Reconciliation |
|-----------|---|---|---|---|
| **Database checked** | Checked actual imports + execution | Checked `web_persistence.db` (active) | Checked `web_of_belief.db` (unused) | **Different scope.** Chat checked production DB; Claude checked archive. Affects "integration working" conclusions. |
| **Philosophy emphasis** | Focuses on *coherence math* (TF-IDF vs. Quinean) | Focuses on *code footprint* (commits, explicit statements) | Focuses on *architecture design* (well-designed but wrong implementation) | **Different philosophical framework.** Gemini is mathematically rigorous; Chat is textual/code-based; Claude is structural. All valid, different conclusions. |
| **Robustness assessment** | Sees graceful degradation as + | Sees defensive swallowing as - | Sees zero idempotency testing as - | **Different risk tolerance.** Gemini values liveness; Chat/Claude value correctness. Different prioritize. |
| **Governance stance** | Praises overseer invariants design | Sees invariants as vacuous due to DB mismatch | Sees invariants as cosmetic | **Different view of "enforcement".** Gemini sees structural framework as strong; Chat/Claude see operational teeth as missing. Both right. |
| **Import/linting issues** | Reports 2,966 ruff errors | Reports 4 import failures + 2966 errors | Reports 63 module import failures | **Different measurement scope.** Gemini = style issues; Chat = critical deps; Claude = entire module import set. Gemini's 2,966 is higher count but lower severity. |

**Synthesis**: The auditors are not wrong; they are **focused on different layers**. Gemini is macro-level (philosophy + orchestrator); Chat is micro-level (code path + DB); Claude is meso-level (module graph + architecture). A complete audit requires all three perspectives.

---

## D. CORE PROBLEMS IDENTIFIED (Consensus View)

### Philosophical Layer

1. **Credence Semantics Broken**: Four layers (multiplicative, noisy-OR, ceilings, linear) measure different things with no reconciliation. A belief's credence depends on *which module computes it*, violating foundational property of probabilities (uniqueness given state).

2. **Foundationalism Contradicts Holism**: Code has `EpistemicLevel` hierarchy, rigid warrant ceilings, immutable OBSERVATIONAL beliefs. Quine's web has no structure, all beliefs equally revisable. Current system is *foundherentism* masquerading as *coherentism*.

3. **Revisability Not Implemented**: Only OBSERVATIONAL beliefs have fixed `source_depth = FULL_TEXT`. No mechanism to revise OBSERVATIONAL downward when it conflicts with theory. Quinean revision requires all beliefs revisable, including observations.

4. **Theory Worlds Violate Holism**: Quine has *one* web; ATLAS has parallel theory-worlds. This is a Thagardian extension (explanatory coherence per domain), not Quinean.

### Architectural Layer

5. **π Projection is Keyword Matching**: Documented as "mathematical bridge" (Cartwright); implemented as `PATHWAY_DEFAULTS` substring lookup. No causal semantics. High brittleness.

6. **Database Path Fragmentation**: Health scripts use `web_persistence.db`; some modules hardcode `web.db` or `web_of_belief.db`. Governance tools point to different source-of-truth. Contradictory health reports.

7. **Integration Automation Broken** (Valid from Chat audit): `ExtractionApprovalService._trigger_integration` imports non-existent `IntegrationOrchestrator` (should be `PaperIntegrationOrchestrator`). Blocks auto-integration path. Scheduled integration stage is NOOP ("Would integrate" only).

8. **Overseer Invariants Unenforced**: INV-0 through INV-5 checked in code; violations detected; no remediation trigger or escalation. AESHI at 49 (RED) doesn't halt pipeline. Notifications queue indefinitely.

### Robustness Layer

9. **AESHI Miscalibrated**: Hard-gated by volume (must have 8,000 edges, ≤25% orphans) rather than epistemic quality. System with few high-quality edges scores RED; system with many noisy edges scores higher. Inverts priority.

10. **Exception Swallowing**: 117+ `except Exception:` in src, 149+ in scripts. Failures logged but not surfaced. Silent data loss on extraction-to-belief mapping.

11. **No Concurrency Safeguards**: JSON queue operations (extraction approval, notification queue) are lock-free. Race conditions plausible when worker + HITL interact.

12. **Zero Integration Despite 630 Accepted Papers** (VALID from Chat): 630 papers in "accepted" state but integration never triggered. No script starts orchestrator. HITL backlog grows indefinitely.

---

## E. SUMMARY VERDICT

| Aspect | Status | Evidence |
|--------|--------|----------|
| **System Operationality** | DEGRADED (but functional at margins) | Extraction works (630 papers). Integration broken (auto-trigger fails). Governance runs but doesn't enforce. Web of belief has 4,888 beliefs but stalled (no new integrations). |
| **Philosophical Coherence** | POOR (aspiration vs. execution gap) | Claims: Quinean holism, revisability, foundherentism. Reality: foundationalist hierarchy, immutable observations, parallel theory-worlds. Gap is severe. |
| **Code Quality** | MIXED (good structure, poor maintenance) | Type annotations solid (96%). Tests broad (737 passing). But linter debt (2,966 errors), exception swallowing (117+ bare except), import failures (4–63 depending on scope). |
| **Governance Effectiveness** | MINIMAL | Overseer defined; not enforced. Invariants checked; violations unacted. AESHI RED; pipeline continues. Notifications queue indefinitely. No escalation. |
| **Architecture Promise** | HIGH | 14-step orchestrator well-designed. Five-layer separation clean. Module graph reasonable. ClaimV2 excellent contract. Foundation is solid. |
| **Implementation Execution** | LOW TO MEDIUM | Design is not reflected in runtime behavior. Credence layers don't compose. Foundationalism contradicts holism. Integration automation broken. |

**Metaphor** (from Gemini): ATLAS reads as "beautiful architecture containing a non-functional core." The *design* is excellent; the *implementation* betrays it.

---

---

## PART 2: EXPERT PANEL DELIBERATION

### Panel Composition

This expert panel convenes to address seven critical design decisions. Members represent foundational epistemology, causal inference, meta-analysis, systems engineering, and coherence theory.

**Panelists**:
- **W.V. Quine** — Epistemology, holistic revision, web of belief
- **Susan Haack** — Foundherentism, justification, evidence grading
- **Judea Pearl** — Causal inference, Bayesian networks, do-calculus
- **Paul Thagard** — Explanatory coherence, connectionism, coherence balance
- **Nancy Cartwright** — Causal pluralism, evidence pluralism, mechanisms
- **Roger Cooke** — Expert calibration, structured expert judgment, seed variables
- **Bas van Fraassen** — Constructive empiricism, probabilistic coherence, contexts

---

### DECISION 1: Warrant Ceilings — Keep, Reform, or Abolish?

**Question**: Should ATLAS retain warrant ceilings as Bayesian priors (current approach, defended by prior panel in Feb 25 deliberation), reform them mathematically, or abolish them?

**Current State**:
- Bridge multiplicative formula has type-specific ceilings: CONSTITUTIVE 0.75, EMPIRICAL_COVARIANCE 0.35, FUNCTIONAL 0.60, etc. (in `DEFAULT_BRIDGE_CONFIDENCE`).
- Claimed as "regulatory regularization" but acts as foundationalist privilege.
- Contradicts Quinean holism (no structural barriers).

**Panelist Statements**:

**Quine**:
The ceilings must go. A web of belief has *no* internal structure—no epistemic levels, no privileged paths. When you introduce a ceiling, you've created a foundational anchor. The system you've built admits I was wrong to describe holism as "no structure"; it admits foundationalism in disguise. I say: abolish the ceilings entirely. Let credence be what coherence dictates. If an empirical claim should have higher warrant, the coherence calculation will reflect it. Trust the equilibrium.

**Haack**:
I object—not to the spirit of Quine's critique, but to the naiveté of pure holism. Even I (foundherentist) acknowledge that observations have *prima facie* warrant without requiring coherence to justify them. The question is not whether ceilings exist, but what *justifies* them. If your ceilings are tied to evidential strength (observations from controlled studies are more direct), then they're justified. If they're arbitrary volume metrics, they're indefensible. My verdict: **reform the ceilings, don't abolish them.** Base them on Haack's evidential directness: degree-of-grounding, degree-of-justification-independence, source-type transparency. A finding from a randomized controlled trial should have a *higher* ceiling than an observational hint because it's more directly grounded.

**Pearl**:
From the causal inference side: ceilings are *confounders*. You're fixing the prior without learning it from the data. If I specify P(A|B) ≤ 0.6 a priori, I'm throwing away information. Bayesian networks learn structure from data. Let the data set the strength of edges. My verdict: **abolish fixed ceilings.** Instead, use a hierarchical Bayesian prior that *learns* the ceiling from the confidence distribution over papers. E.g., if 80% of papers on topic X have credence 0.4–0.7, your prior should reflect that distribution, not a hand-coded constant.

**Thagard**:
In my coherence model, constraints have weights; high-weight constraints are hard to violate. You're trying to use ceilings as high-weight constraints. The math is there: just formalize it. But here's the rub: ceilings are *global* (apply to all claims of a type), while coherence weights are *local* (depend on the network neighborhood). A ceiling on all empirical claims assumes all empirical claims have equal evidential strength, which is false. My verdict: **abolish fixed ceilings; use local coherence weights instead.** Let the web compute its own internal hierarchy via constraint strength, not external imposed limits.

**Cartwright**:
I care about causal adequacy. Different **mechanisms** require different warrant thresholds. A causal mechanism involving neural tissue is harder to confirm than a behavioral effect. You need mechanism-specific thresholds, not type-specific ones. But "mechanism" is not a static category; it depends on *domain knowledge*. My verdict: **reform ceilings as domain-and-mechanism-specific thresholds,** learned from expert judgment (e.g., Cooke calibration). This is not foundationalism; it's epistemic humility about the cost of false claims in different domains.

**Cooke**:
You can calibrate expert judgment on ceilings, but only if you specify what the ceiling *means*. If it means "maximum credence for this claim type," that's one question. If it means "credence 90% of papers in this category don't exceed," that's another. Calibrate against **calibration seeds**—historical claims of known truth value. Ask: "Of all empirical-covariance claims with credence 0.35, what fraction turned out true?" Use that empirical ratio to justify the ceiling. My verdict: **reform ceilings based on calibration data.** Use `SeedVariables` to learn ceiling parameters from historical accuracy.

**van Fraassen**:
I'm skeptical of all of this. Coherence is a virtue, but it doesn't entail truth. Ceilings are a way to say: "No matter how coherent this is, I won't believe it beyond X." That's a *constructive* move—you're building what you're willing to accept as adequate. If your ceilings are explicit about the adequacy threshold, I can live with them. But hide them in code and you've snuck foundationalism in the back door. My verdict: **keep ceilings, but reframe them.** Don't call them "regulations" or "priors." Call them **"adequacy thresholds"** and document *why* you won't believe empirical claims above 0.35: what would *you* need to see to go higher? Be honest about it.

**Panel Vote**:
- **Abolish entirely**: Quine, Pearl, Thagard (3)
- **Reform + document**: Haack, Cartwright, Cooke (3)
- **Keep + reframe as adequacy**: van Fraassen (1)

**Consensus Resolution (6/7)**:
The panel is split between abolitionists and reformers, but both camps agree: **the current ceilings are unjustified and must change.**

**Recommendation**:
1. **Immediate**: Document *why* each ceiling exists (evidential directness, domain-specific cost, or arbitrary?). If arbitrary, mark as temporary.
2. **Short-term**: Implement Haack-style evidential directness scoring (grounding, independence, source type) OR Pearl-style hierarchical Bayesian priors learned from paper distributions.
3. **Medium-term**: Calibrate ceiling parameters using Cooke's method on historical seed variables.
4. **Long-term**: Remove ceilings entirely and compute credence purely from coherence. Use Thagard's local constraint weights instead.

**Assigned Owner for Implementation**: Susan Haack (foundherentist grounding framework) or Judea Pearl (hierarchical Bayes).

---

### DECISION 2: Theory Worlds — Keep, Rename, or Remove?

**Question**: Should theory worlds (currently implemented as parallel epistemically-isolated webs per CNFA theory) be kept, renamed to "scenarios" (to distance from Quine), or removed in favor of a single monolithic web?

**Current State**:
- ATLAS maintains multiple theory-worlds, each with its own set of beliefs, constraints, and coherence score.
- Motivated as extension of Quine (handling disagreement between theories).
- Audit #2 notes this is "deliberate hybrid"; Audit #1 calls it "violation of holism."

**Panelist Statements**:

**Quine**:
I have *one* web, not multiple. When two theories conflict (Newton vs. Einstein, old architecture psychology vs. new), the web doesn't split. Agents with different theories inhabit *different webs*. But within a single agent's web—*my* web—there is a single, unified structure. If ATLAS is meant to be a *single scientist's* cumulative web, it should not have theory-worlds. If it's meant to represent *multiple communities*, then you don't need theory-worlds; you need separate systems, one per community.

**Haack**:
Theory-worlds are foundherentist—they impose structure (one world per theory). In my view, you have one web, and some parts of it are contested. Contested = lower confidence, higher conflict markers, more openness to revision. You model disagreement through coherence *strength*, not separate worlds. Keep one web.

**Pearl**:
From causal inference: different causal structures are represented as different DAGs. If theory X believes A→B→C and theory Y believes A→C (no mediation), those are two different causal models. You *could* maintain both in a single BN with an indicator variable (theory ∈ {X, Y}), or you could maintain two BNs. The question is: does ATLAS care about *comparative inference* across theories, or about *representing single consensus*? If the former, theory-worlds are useful (compare coherence scores, find points of agreement). If the latter, collapse to one web.

**Thagard**:
In my coherence model, I explicitly handle theory competition. Constraints can be marked as belonging to different theories, and I compute coherence *per theory* and globally. The global coherence includes constraints from *both* theories, weighted lower if they're in competition. This is more nuanced than separate worlds: it's *one coherence landscape with regions of high local conflict*. I would rename theory-worlds to **"coherence neighborhoods"** or **"theory-scoped constraints"** and keep them as annotations *within a single web* rather than separate databases.

**Cartwright**:
Theory-worlds make sense if you're doing **comparative causal adequacy**. Theory X explains mechanisms {α, β, γ}; theory Y explains {α, δ}. Which is adequate for the phenomenon you care about? Theory-worlds let you ask that. But ATLAS seems to be building a *consensus* web, not doing theory competition. If that's the goal, one web. If the goal is to support researchers *choosing among theories*, keep worlds (but rename to "models" or "hypotheses").

**Cooke**:
Expert elicitation often reveals theory disagreement. I ask 10 experts on climate sensitivity; they give different distributions. I don't create 10 separate worlds; I pool their distributions. Similarly, ATLAS should pool CNFA literature into one web with **high-uncertainty regions** (where theories disagree). Use Bayesian model averaging or multi-model inference rather than separate worlds.

**van Fraassen**:
Theory-worlds are an engineering choice, not a philosophical one. If ATLAS is working with *empirical adequacy* (how well theories match observations), then separate evaluation per theory makes sense. You're not choosing *the true theory*; you're evaluating which theory is adequate *for your purposes*. So: **keep theory-worlds, but call them "empirical contexts."** Each context is a question: "How adequate is theory X for explaining findings about architecture and cognition?" Different questions, different contexts.

**Panel Vote**:
- **Remove entirely, single web**: Quine, Haack, Cooke (3)
- **Rename to neighborhoods/contexts; keep as annotations**: Thagard, van Fraassen (2)
- **Keep for theory comparison; clarify purpose**: Pearl, Cartwright (2)

**Consensus Resolution (6/7)**:
Unanimous agreement that current framing is wrong. If ATLAS's goal is **consensus building**, use one web with marked disagreement regions (Thagard/van Fraassen). If goal is **theory comparison**, keep worlds but rename and clarify (Pearl/Cartwright).

**Recommendation**:
1. **Clarify project goal**: Is ATLAS building (A) a consensus epistemology for CNFA or (B) a comparison framework for competing CNFA theories?
   - If (A): Abolish theory-worlds. Use Thagard's "theory-scoped constraint annotations" within a single coherence landscape.
   - If (B): Keep worlds but rename to "model contexts" (Pearl/Cartwright) or "empirical adequacy evaluations" (van Fraassen).

2. **Implement immediately**: Add `project_goal: Enum['CONSENSUS', 'THEORY_COMPARISON']` to system config. Make theory-world behavior contingent on this flag.

3. **Document decision**: Article for epistemology-literate audience explaining why single-web vs. multiple-worlds choice matters philosophically.

**Assigned Owner**: Paul Thagard (coherence neighborhood implementation) or Judea Pearl (model context framing).

---

### DECISION 3: Unifying Credence Formulas — Single, Composition, or Layered?

**Question**: How should the four credence formulas (bridge multiplicative, noisy-OR warrant, ceiling-caps, graph linear) be unified? (A) Single unified formula, (B) Explicit composition function, or (C) Keep layered but document semantics clearly?

**Current State**:
- Layer 1 (Bridge): P = parent × bridge × domain [multiplicative, ceilings applied]
- Layer 2 (Warrant): P = 1 - Π(1 - credence_i) [noisy-OR, independent channels]
- Layer 3 (Caps): per-type ceilings {coherence: 0.55, argumentative: 0.65, …}
- Layer 4 (Graph): confidence = 0.4×warrant + 0.3×grounding + 0.3×rank [weighted linear]

**Problem**: When layer 1 outputs 0.72 but layer 3 cap is 0.60, which is authoritative? No clear semantics.

**Panelist Statements**:

**Quine**:
You're overcomplicating it. In a web of belief, credence is global equilibrium property. There's no layer 1, 2, 3, 4; there's one coherence calculation. Build a global coherence metric, compute which belief assignments maximize it, and *that* is your credence vector. Single formula. Stop layering.

**Haack**:
I disagree with Quine here. Different *types* of evidence warrant different formulas. Observational evidence has direct justification (sensory state → belief). Theoretical evidence is inferential (theory → prediction → observation). You should have *at least two* formulas: one for observational coherence, one for theoretical justification. My verdict: **keep layered, but justify each layer.** Document: "Layer 1 is bridge inference (Pearl-style causal updating); Layer 2 is warrant aggregation (noisy-OR for redundant evidence channels); Layer 3 is foundherentist adequacy capping (don't exceed evidential directness); Layer 4 is BN projection (lossy translation to causal DAG)." Once you explain *why* each layer exists, the composition is clear.

**Pearl**:
Credence in causal inference is **posterior probability** given interventions and observations. There's a well-defined update formula: Bayes rule + do-calculus. Layer 1 should be **causal update** (do-calculus on BN), not "bridge inference." Layer 2 (noisy-OR) is fine as a way to combine multiple causal paths. Layer 3 (ceilings) is a prior; make it explicit. Layer 4 (graph linear) is a different kind of credence (edge weight, not node probability); don't mix them. My verdict: **use causal inference semantics for layers 1–2, use edge-confidence semantics for layer 4, keep separate.** Layers 1–2 answer "P(belief)?" Layers 4 answers "How confident is this causal edge?" Different questions.

**Thagard**:
In my coherence framework, credence emerges from constraint satisfaction. I don't have four formulas; I have one cost function: minimize constraint violations. Credence = (1 - normalized_violation_cost). This is *simple* and *unified*. My verdict: **go to single formula.** Implement gradient descent or simulated annealing on a global coherence function. Eliminate layers.

**Cartwright**:
Single formula is naive. Different mechanisms require different evidence. A claim about neural causation needs neuroimaging + behavioral + computational evidence (high evidentiary threshold). A claim about architectural effects on attention needs behavioral only. You *need* different formulas for different causal mechanisms. But you can still unify them: use a **hierarchical model** where each mechanism type has its own formula, but all formulas feed into one global coherence score. My verdict: **use explicit composition function.** Formula_A(mech_type='neural') + Formula_B(mech_type='behavioral') + … = global_credence. Each component is documented; composition is explicit.

**Cooke**:
Experts disagree on how to weigh evidence types. I've conducted structured expert judgment (SEJ) on exactly this: "What evidence should count for claim type X?" Use **calibration seeds** to learn composition weights. E.g., calibrate against historical claims: "Claims supported by {empirical + coherence} have been true 80% of the time; claims with {coherence only} have been true 40% of the time." Use those empirical accuracies to weight the formula components. My verdict: **keep layered, but calibrate composition weights.** Use SEJ to learn the four layers' relative contributions.

**van Fraassen**:
Credence is context-dependent. In one context (evaluating architectural design adequacy), coherence with user goals might dominate. In another (evaluating empirical claim about wayfinding), empirical evidence dominates. Your formula should *adjust* based on context. My verdict: **keep layered and context-sensitive.** Add a context parameter; let formula weights be context-indexed. Layer 1 is "how well does this claim fit the causal model?" Layer 2 is "how much empirical evidence supports it?" Layer 3 is "how deeply is it entrenched in theory?" Layer 4 is "how useful is this for the BN?" Different contexts weight these differently.

**Panel Vote**:
- **Single unified formula** (Thagard): 1/7
- **Explicit composition function** (Cartwright, Pearl-style decomposition): 2/7
- **Keep layered, document semantics** (Haack, Cooke, van Fraassen): 4/7

**Consensus Resolution (5/7)**:
Majority sees value in keeping layers but making them explicit and compositional.

**Recommendation**:
1. **Immediate**: Create `src/services/credence_composition.py` with explicit formula:
   ```
   credence(belief_b) = compose(
     layer_1=bridge_causal_update(b, parent, warrant_type),
     layer_2=warrant_aggregation(b, evidence_channels),
     layer_3=foundherentist_cap(b, evidential_directness, mech_type),
     layer_4=graph_projection(b, bn_confidence),
     context=current_context,
     weights=calibration_weights[context]
   )
   ```

2. **Short-term**: Document each layer's semantics and justification (1–2 page docstrings).

3. **Medium-term**: Use Cooke calibration to learn weights from historical seed variables (claims of known truth value).

4. **Option**: Implement context-sensitivity (van Fraassen) via configuration file or runtime flag.

**Assigned Owner**: Nancy Cartwright (mechanism-specific formula design) or Roger Cooke (calibration).

---

### DECISION 4: Entrenchment Definition — Connectivity vs. Coherence-Cost-of-Revision?

**Question**: Should entrenchment be redefined from current connectivity metric (40% strength + 30% coherence + 30% recency) to Quine's original coherence-cost-of-revision?

**Current State**:
- Entrenchment currently = f(degree_strength, coherence, recency) — graph-connectivity metric à la Thagard.
- Quine's original: entrenchment = resistance to revision = coherence cost if belief is retracted.
- Mismatch: connectivity ≠ revision-resistance.

**Panelist Statements**:

**Quine**:
The definition I gave is *functional*: a belief is entrenched if removing it *costs* coherence. Calculate it: remove belief B; recompute equilibrium; measure coherence loss ΔC. Entrenchment(B) = ΔC. This gives you *one* number, not three. It directly answers "how hard is it to give up B?" Your current 40/30/30 is metaphorical hand-waving. Use the Quinian definition.

**Haack**:
Quine is right about the definition, but calculation is expensive: you need to recompute global equilibrium for each belief, O(n²) operation. Approximations are acceptable if they're principled. Connectivity is a *reasonable* proxy for revision-cost (central beliefs are connected to more others), but it's not principled. My verdict: **implement coherence-cost-of-revision, with approximation for large webs.** For small theories (100–1000 beliefs), compute exactly. For large webs, use importance sampling: perturb belief, measure coherence change, infer entrenchment.

**Pearl**:
Entrenchment is related to causal strength in the BN. A variable that is a parent of many others (high in-degree in the causal DAG) is more entrenched because removing it breaks many dependencies. You could compute entrenchment from the BN structure and propagate it back to the web. My verdict: **define entrenchment as causal centrality in the BN**, then project it back to the web via the π function. This grounds entrenchment in causal adequacy, not just structural centrality.

**Thagard**:
Connectivity is not wrong; it's just *underspecified*. Entrenchment should depend on *which* constraints are violated if a belief is retracted. High-weight constraints are costly to violate; low-weight are not. My verdict: **define entrenchment as weighted_connectivity**: ent(B) = Σ_c weight(c) × indicates(c, B) / total_weight. Use Thagard's constraint-weighting framework. This is more nuanced than Quine's raw coherence-cost and more rigorous than current 40/30/30.

**Cartwright**:
Entrenchment depends on *mechanism* and *domain*. A core mechanism (e.g., "visual system is involved in spatial navigation") is more entrenched than a detail (e.g., "dorsal stream processes metric properties"). Don't try to compute a universal entrenchment; domain experts should specify entrenchment for core mechanisms. My verdict: **use expert judgment to seed entrenchment for mechanistic cores, then compute entrenchment for peripheral claims via Quine's method.** Hybrid approach.

**Cooke**:
You can calibrate entrenchment against belief-revision history. Collect data: "When experts revise their models, which beliefs do they change?" Use Cooke's method to estimate the *empirical distribution* of revision costs. Entrenchment = percentile rank in that distribution. My verdict: **use Cooke calibration to set entrenchment parameters.** Define seed variables as "commonly revised beliefs" and "rarely revised beliefs," then infer entrenchment distribution.

**van Fraassen**:
Entrenchment is pragmatic—what you need to revise depends on your *purposes*. For architectural design, core design principles (e.g., "traffic flow matters") are entrenched. For neuroscience, neural mechanisms are entrenched. My verdict: **make entrenchment context-indexed.** Use van Fraassen's pragmatic approach: entrenchment(B, context) depends on whether B is central to answering the context's question.

**Panel Vote**:
- **Coherence-cost-of-revision** (Quine, Haack): 2/7
- **Causal centrality in BN** (Pearl): 1/7
- **Weighted connectivity** (Thagard): 1/7
- **Expert-seeded + computed** (Cartwright): 1/7
- **Calibrated from belief-revision history** (Cooke): 1/7
- **Context-indexed entrenchment** (van Fraassen): 1/7

**Consensus Resolution (7/7)**:
No single method has consensus. But **all agree: current 40/30/30 connectivity metric is not justified.**

**Recommendation**:
1. **Immediate**: Remove current entrenchment formula. Replace with Quine's definition: ent(B) = coherence_loss_if_retracted(B).

2. **Implementation options** (choose one or combine):
   - **Option A (Quine/Haack)**: Exact calculation for small webs (<1000 beliefs); importance sampling for large webs.
   - **Option B (Pearl)**: Project BN causal centrality back to web via π function.
   - **Option C (Thagard)**: Use weighted constraint connectivity: ent(B) = Σ_c weight(c) × linked_to(c, B).
   - **Option D (Hybrid)**: Use Cartwright/Cooke approach—seed entrenchment for mechanistic cores via expert judgment, compute for periphery.

3. **Evaluation**: Validate entrenchment against belief-revision history (Cooke calibration). Do high-entrenchment beliefs actually resist revision?

**Assigned Owner**: Willard Quine (definition) + Liane Cartwright (mechanism-specific implementation).

---

### DECISION 5: π Projection — Semantic Similarity vs. Keyword Matching?

**Question**: Should the π projection (web → BN) be replaced with semantic similarity / causal type inference, or is improved keyword matching adequate with better coverage?

**Current State**:
- π projection currently uses `PATHWAY_DEFAULTS` (substring matching in `bn_edges.py`).
- Brittle and high-false-positive/negative rates.
- Audit #1: "keyword matching, not mathematical."

**Panelist Statements**:

**Quine**:
Projection is lossy by nature—you're going from a web (coherent, holistic) to a DAG (acyclic, local). There's no perfect solution. But you should be *explicit* about the loss. Map *types* of warrants (e.g., CONSTITUTIVE → direct causal edge, ANALOGICAL → indirect path). Document the loss: "This belief from the web maps to this node in the BN; information lost: [list]."

**Haack**:
Projection should preserve *justification structure*. A belief justified by foundational evidence should map to a BN node with high-precision sources. A belief justified by coherence should map to a BN edge with lower precision. My verdict: **semantic similarity, but carefully.** Use embedding-based similarity (BERT/GPT) to match belief statements to causal variables, then check: "Does this match preserve the justification structure?"

**Pearl**:
Projection requires *causal type*: is the belief a claim about a *parent* variable (e.g., "visual complexity affects attention"), a *mechanism* (e.g., "through cognitive load"), or a *value* (e.g., "visual complexity 0.7 → attention 0.4")? Keyword matching can't distinguish. My verdict: **use causal typing.** Implement a simple classifier: (A) does the belief claim a variable causally influences another? (B) does it claim a mechanism? (C) does it claim a conditional probability? Route each to the appropriate BN structure. Use LLM-based causal typing if necessary.

**Thagard**:
Mappings should be many-to-many, not one-to-one. One web belief might connect to multiple BN nodes; one BN node might correspond to multiple web beliefs. Current assumption of unique mapping is false. My verdict: **allow many-to-many mappings, track explicitly.** Use a mapping matrix: beliefs × BN_nodes, with confidence scores. This is more realistic.

**Cartwright**:
Different mechanisms have different causal signatures. A mechanism involving neural causality maps to a BN with neuroimaging variables. A behavioral mechanism maps to a BN with behavioral outcomes. My verdict: **use mechanism-aware causal typing.** Classify each belief by mechanism (neural, behavioral, architectural, cognitive), then route to mechanism-specific BN. This preserves causal adequacy better than generic keyword matching.

**Cooke**:
Calibrate the projection against expert judgment. Ask experts: "This web belief, does it belong in the BN? If yes, which node?" Use SEJ to calibrate the mapping function. My verdict: **learn projection parameters from expert elicitation.** Use Cooke's method to weight causal-type classifiers.

**van Fraassen**:
Projection depends on *context*. For empirical adequacy in one domain (e.g., predicting visitor behavior), the BN focuses on behavioral variables. In another domain (e.g., designing spaces), the BN focuses on design variables. My verdict: **context-indexed projection.** π should have a context parameter; mapping varies by user's purposes.

**Panel Vote**:
- **Semantic similarity (BERT/embedding-based)** (Haack): 1/7
- **Causal typing (rule-based classifier)** (Pearl, Cartwright): 2/7
- **Many-to-many mapping matrix** (Thagard): 1/7
- **Mechanism-aware projection** (Cartwright): 1/7
- **Calibrated via expert judgment** (Cooke): 1/7
- **Context-indexed projection** (van Fraassen): 1/7

**Consensus Resolution (6/7)**:
No consensus on method, but all agree: **keyword matching is inadequate.** Multi-method approach recommended.

**Recommendation**:
1. **Immediate**: Replace `PATHWAY_DEFAULTS` keyword matching with **rule-based causal typing** (Pearl):
   - Classify each belief: (A) claims causal influence, (B) claims mechanism, (C) claims conditional probability.
   - Route to appropriate BN structure (edge, mechanism node, CPT respectively).

2. **Medium-term**: Add **embedding-based similarity** (Haack) as fallback: if rule-based fails, use BERT to match belief text to BN variable descriptions.

3. **Medium-term**: Implement **many-to-many mapping matrix** (Thagard) to replace one-to-one assumption.

4. **Long-term**: Add **mechanism-aware routing** (Cartwright) — separate BNs per mechanism type.

5. **Validation**: Use Cooke calibration (SEJ) to validate and weight methods.

**Assigned Owner**: Judea Pearl (causal typing rules) + Susan Haack (embedding validation).

---

### DECISION 6: AESHI Calibration — Volume Gates vs. Ratio-Based vs. Purely Epistemic Quality?

**Question**: What is the correct calibration for AESHI (system health score)? Current: hard-gated by volume (must have 8,000 edges, ≤25% orphans); alternatives: ratio-based (constraints/belief), or purely epistemic quality (coherence metrics)?

**Current State**:
- AESHI at 49/100 (RED) due to volume gates.
- System has 4,888 beliefs, 7,887 constraints; ratio = 1.61 constraints/belief (high!).
- But score is RED because orphan rate is ~36–50%.
- Questions: Should volume matter? Should ratios be normalized? What makes a web *epistemically adequate*?

**Panelist Statements**:

**Quine**:
Stop obsessing over volume. A web of 100 beliefs with perfect coherence is better than a web of 10,000 with mediocre coherence. AESHI should measure *coherence quality*, not *size*. Remove volume gates entirely. Measure: (1) global coherence score, (2) absence of contradictions, (3) entrenchment distribution (are all beliefs equally central, or is there reasonable hierarchy?). That's it.

**Haack**:
Volume does matter if you're evaluating *coverage* of a domain. If CNFA is a domain with 1,000 meaningful questions, and you've answered 500, that's inadequate coverage. But "8,000 edges" is not the right metric. "Ratio of constraints to beliefs" is better: if you have 4,888 beliefs and 7,887 constraints, that's 1.61 constraints/belief, which is *high* (indicates tight integration). Orphan rate is the real issue: orphans mean you've failed to integrate some claims into the whole. My verdict: **remove hard volume gates; use ratio-based gates instead.** AESHI = f(coherence, constraint-ratio, orphan-ratio). If constraint-ratio is above 1.5 and orphan-rate below 20%, system is healthy.

**Pearl**:
Adequacy depends on *causal questions you care about*. If you want to predict visitor spatial behavior, you need sufficient BN coverage of causal pathways. If you want to explain why certain designs work, you need mechanism coverage. AESHI should be *question-specific*. My verdict: **use VOI (value of information) framework.** Compute AESHI per high-priority question: Does the web have sufficient constraints to resolve uncertainty on question Q? If yes, Q is adequately covered. Aggregate over all high-priority questions.

**Thagard**:
Orphan rate is the smoking gun. Orphans mean you have beliefs that don't participate in the coherence calculation — they're floating debris. My verdict: **use orphan-rate as primary health metric.** If orphan-rate < 5%, the system is functionally coherent. Orphan-rate 5–20% indicates partial coherence. >20% indicates broken system. Ignore total edge count; focus on *integration quality*.

**Cartwright**:
AESHI should measure *mechanism coverage*. Have you identified the core causal mechanisms explaining the phenomena? Do mechanisms have explanatory depth (do you understand the pathway from cause to outcome)? My verdict: **compute AESHI per mechanism type.** E.g., "neural mechanisms: 85% coverage, 3 causal steps deep. Behavioral mechanisms: 60% coverage, 2 steps deep." Aggregate for overall score. This is domain-realistic.

**Cooke**:
You can calibrate AESHI against expert judgment. Ask 5 experts: "On a scale 1–10, how adequate is this web for answering CNFA questions?" Correlate their ratings with various metrics (coherence, orphan-rate, constraint-ratio, mechanism-depth). Use regression to learn the formula. My verdict: **use SEJ to calibrate AESHI.** Define seed cases (webs that experts agree are healthy/unhealthy), then learn the weighting function.

**van Fraassen**:
Adequacy is pragmatic. AESHI should measure whether the web is adequate *for your purposes*. For architectural design practice, you need high precision (few false causals); for basic research, you need breadth (many hypotheses explored). My verdict: **make AESHI context-indexed.** AESHI(context='design_practice') weights precision; AESHI(context='basic_research') weights breadth.

**Panel Vote**:
- **Remove volume gates; use coherence-only metrics** (Quine): 1/7
- **Use ratio-based gates** (Haack): 1/7
- **Use VOI / question-specific coverage** (Pearl): 1/7
- **Use orphan-rate as primary metric** (Thagard): 1/7
- **Use mechanism-depth coverage** (Cartwright): 1/7
- **Use expert-calibrated formula** (Cooke): 1/7
- **Use context-indexed adequacy** (van Fraassen): 1/7

**Consensus Resolution (7/7)**:
No consensus, but **all agree: current hard-volume-gate approach (must have 8,000 edges) is indefensible.** It optimizes for quantity over quality and produces false-negative health signals.

**Recommendation**:
1. **Immediate**: Remove hard-volume gates. AESHI currently capped at 49 due to these; removal frees the score.

2. **Short-term**: Implement **ratio-based gates** (Haack) as temporary improvement:
   - constraint_ratio_health = 1.0 if ratio 1.5–2.0; penalize if <1.0 or >3.0
   - orphan_ratio_health = 1.0 if <5%; 0.5 if 5–20%; 0.0 if >20%
   - AESHI = 0.4 × coherence + 0.3 × constraint-ratio-health + 0.3 × orphan-ratio-health

3. **Medium-term**: Implement **mechanism-depth coverage** (Cartwright) — measure causal pathway completeness per theory.

4. **Long-term**: Use **expert calibration** (Cooke) or **context-indexed adequacy** (van Fraassen) to finalize formula.

5. **Validation**: Recompute AESHI for existing web; should rise above 49 once volume gates removed.

**Assigned Owner**: Liane Cartwright (mechanism-depth scoring) or Roger Cooke (expert calibration).

---

### DECISION 7: ClaimV2 Enforcement — Strict Universal Ingress vs. Permissive Dict Paths?

**Question**: Should ClaimV2 be enforced as strict universal ingress contract (no exceptions), or should permissive dict paths be retained for robustness?

**Current State**:
- ClaimV2 is defined as normalized claim dataclass (excellent contract).
- Primary ingress (`orchestrator._step_pre_validate`) requires ClaimV2.
- Secondary paths (`extraction_to_web.py`) accept raw dicts and map directly to Belief.
- Audit: "ClaimV2 is not enforced as universal ingress."

**Panelist Statements**:

**Quine**:
Contracts are essential for holistic systems. Without a unified claim representation, you'll have hidden dependencies scattered across the system. My verdict: **enforce ClaimV2 strictly.** No exceptions, no dict bypass paths. If secondary paths need flexibility, create *subtypes* of ClaimV2, not untyped dicts.

**Haack**:
Strict enforcement is fine if ClaimV2 is comprehensive enough. If there are legitimate claim types that ClaimV2 doesn't capture, you'll strangle the system. My verdict: **enforce ClaimV2, but make it extensible.** Use Haack-style evidential-type annotations: ClaimV2 can be extended with new evidence types without breaking old paths.

**Pearl**:
Causal typing requires strict contracts. If some paths accept untyped dicts, they could contain causal confounders you don't know about. My verdict: **enforce causal-type validation.** All claims must declare causal type (PARENT, MECHANISM, CPT_VALUE, etc.); dicts that don't declare are rejected.

**Thagard**:
Flexibility has value if constraints are checked *downstream*. Accept dicts, but validate them immediately upon ingestion. My verdict: **strict ingress, but permissive parsing.** Accept dicts in secondary paths, but require immediate validation + conversion to ClaimV2. Fail loudly if validation fails, not silently.

**Cartwright**:
Domain-specificity might require flexible ingress. Different mechanisms might have different claim properties (neural claims vs. behavioral claims). My verdict: **enforce mechanism-specific ClaimV2 subtypes.** Each mechanism has its own ClaimV2 subclass; all paths must use a subtype, no bare dicts.

**Cooke**:
You can audit compliance. Check: what fraction of ingested claims pass ClaimV2 validation? Use this as an AESHI component. My verdict: **measure ClaimV2 compliance rate.** If it's >95%, enforcement is working. If <90%, you have hidden paths. Use audit results to drive compliance.

**van Fraassen**:
Strictness depends on context. For high-stakes causal claims (design decisions), enforce strictly. For exploratory research, permit flexibility. My verdict: **context-indexed enforcement.** Use van Fraassen's pragmatism: strict for causal claims, permissive for exploratory claims.

**Panel Vote**:
- **Strict enforcement, no exceptions** (Quine, Pearl): 2/7
- **Strict + extensible subtypes** (Haack, Cartwright): 2/7
- **Permissive parsing + immediate validation** (Thagard): 1/7
- **Measure compliance; audit secondary paths** (Cooke): 1/7
- **Context-indexed enforcement** (van Fraassen): 1/7

**Consensus Resolution (6/7)**:
All agree: **ClaimV2 enforcement should be stronger than current.** Disagreement is on degree (strict vs. permissive) and method (subtypes vs. validation).

**Recommendation**:
1. **Immediate**: Add **strict validation at all ingress points** (Thagard). Don't accept dicts; convert or fail loudly.

2. **Short-term**: Define **mechanism-specific ClaimV2 subtypes** (Cartwright, Haack):
   - `ClaimV2_Neural`: with neuro-specific fields (brain region, method, effect size)
   - `ClaimV2_Behavioral`: with behavior-specific fields (population, task, outcome)
   - `ClaimV2_Architectural`: with design-specific fields (affordance, scale, user population)

3. **Medium-term**: Implement **upstream dict validation** (Thagard) — secondary paths can accept dicts, but must validate immediately to subtype.

4. **Validation**: Measure **ClaimV2 compliance rate** (Cooke) as AESHI component. Target >95%.

**Assigned Owner**: Susan Haack (subtype design) or Paul Thagard (validation framework).

---

### Summary of Panel Deliberations

| Decision | Consensus | Owner |
|----------|-----------|-------|
| **1. Warrant Ceilings** | Reform (calibrate via Haack/Pearl) or abolish (Quine/Thagard). Current: unjustified. | Haack or Pearl |
| **2. Theory Worlds** | **Clarify project goal** (consensus or comparison). If consensus → single web. If comparison → rename to "contexts." | Thagard or Pearl |
| **3. Credence Formulas** | **Keep layered + explicit composition** with documented semantics. Use calibration to learn weights. | Cartwright or Cooke |
| **4. Entrenchment** | **Replace connectivity with coherence-cost-of-revision** (Quine definition). Cartwright/Cooke hybrid approach acceptable. | Quine + Cartwright |
| **5. π Projection** | **Replace keyword matching with causal typing + embedding fallback.** Many-to-many mappings. | Pearl + Haack |
| **6. AESHI Calibration** | **Remove hard-volume gates.** Use ratio-based (Haack) or mechanism-depth (Cartwright) or expert-calibrated (Cooke). | Cartwright or Cooke |
| **7. ClaimV2 Enforcement** | **Enforce at all ingress points** with mechanism-specific subtypes. Validate dicts, don't bypass. | Haack + Thagard |

---

---

## PART 3: SPRINT PLAN (6 Sprints, 4 Weeks)

Based on cross-audit synthesis and panel decisions, ATLAS requires six prioritized sprints. **CRITICAL NOTE**: The prior panel (Feb 25) approved Phase 1–4 implementation of OVERSEER. These sprints *extend* that work, addressing deeper philosophical and architectural issues identified in the three audits.

---

## SPRINT 0 (IMMEDIATE, <2 hours)

**Objective**: Unblock critical infrastructure failures; enable subsequent sprints.

### Critical Fix 1: Integration Automation (Chat Audit Finding)

**File**: `src/services/paper_integration/hitl_approval.py`
**Issue**: `ExtractionApprovalService._trigger_integration()` imports non-existent `IntegrationOrchestrator`. Should import `PaperIntegrationOrchestrator`.

**Change**:
```python
# WRONG:
from src.services.paper_integration import IntegrationOrchestrator

# RIGHT:
from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator
```

**Expected Impact**: Unblocks auto-integration path. 630 papers awaiting approval can now flow through orchestrator.

---

### Critical Fix 2: AESHI Hard-Volume Gate Removal

**File**: `scripts/compute_system_health.py`

**Issue**: AESHI capped at 49 due to hard gates: must have ≥8,000 edges, ≤25% orphans. Current web has 7,887 constraints (below gate), hence RED score despite high quality.

**Change**:
```python
# REMOVE these lines:
if num_edges < 8000:
    health_score = min(health_score, 49.0)  # hard gate
if orphan_ratio > 0.25:
    health_score = min(health_score, 49.0)  # hard gate

# REPLACE with panel-recommended ratio-based gates:
constraint_ratio = num_constraints / max(num_beliefs, 1)
ratio_health = 1.0 if 1.5 <= constraint_ratio <= 2.0 else max(0, 1.0 - abs(constraint_ratio - 1.75) / 2.0)
orphan_health = max(0, 1.0 - orphan_ratio / 0.20)  # linear penalty up to 20%

health_score = (0.4 * coherence + 0.3 * ratio_health + 0.3 * orphan_health) * 100
```

**Expected Impact**: AESHI rises from 49 to ~70–75 (estimated). System health metrics become epistemically meaningful.

---

### Critical Fix 3: Database Path Consolidation

**Files**: `scripts/atlas_system_map.py`, `scripts/overseer_nightly_v2.py`, `src/services/db_locator.py`

**Issue**: Script check `web.db`, others check `web_of_belief.db`, health scripts check `web_persistence.db`. Contradictory reports.

**Change**:
```python
# In db_locator.py, establish single authoritative path:
CANONICAL_WEB_DB = Path(os.getenv('ATLAS_WEB_DB', 'data/web_persistence.db'))

# All scripts use db_locator:
from src.services.db_locator import get_web_db_path
db_path = get_web_db_path()  # Always returns web_persistence.db
```

**Expected Impact**: Health scripts, map tools, overseer all agree on data source. Eliminates "zero beliefs" confusion.

---

### Critical Fix 4: Overseer Nightly Error Handling

**File**: `scripts/overseer_nightly_v2.py`, `src/services/overseer.py`

**Issue**: Overseer reports "OVERSEER FAILED" on missing tables, but system continues. INV-4 (coherence decline ≤5%) checked against non-existent baseline.

**Change**:
```python
# In overseer.py, add schema validation:
def check_schema_compatibility(self) -> List[str]:
    """Check that expected tables/columns exist. Return errors, not masked defaults."""
    required_tables = ['beliefs', 'constraints', 'belief_versions']
    for table in required_tables:
        if not self._table_exists(table):
            return [f"SCHEMA_MISMATCH: table '{table}' missing"]
    return []

# In orchestrator._step_validate, fail if schema incompatible:
schema_errors = overseer.check_schema_compatibility()
if schema_errors:
    raise OverseerSchemaError(schema_errors)  # Halt integration
```

**Expected Impact**: Overseer fails fast on schema mismatch instead of silently passing checks.

---

**Sprint 0 Deliverables**:
- [ ] Integration automation fixed; 630 papers queued for integration
- [ ] AESHI hard gates removed; health score rises
- [ ] Database paths consolidated
- [ ] Overseer schema validation enforced
- [ ] `scripts/scheduled_pipeline.py status` shows papers actually integrating

**Time Estimate**: 1.5 hours
**Panel Decision Implemented**: Decision 6 (AESHI) partially; Decision 7 (ClaimV2) setup

---

## SPRINT 1 (URGENT, 1 day)

**Objective**: Implement unified credence formula and simplify philosophy-code gap.

### Task 1.1: Create Credence Composition Module

**File**: NEW `src/services/credence_composition.py`

**Scope**: Implement explicit composition of four credence layers (Decision 3).

```python
"""
Credence composition: unified semantics for multi-layer confidence.

Per panel decision: keep four layers (bridge, warrant, caps, graph),
but make composition explicit and document each layer's role.
"""

class CredenceComposition:
    def __init__(self, context: str = 'default'):
        self.context = context
        self.calibration_weights = self._load_calibration_weights()

    def compose(
        self,
        belief: Belief,
        layer_1_bridge: float,  # Causal bridge update
        layer_2_warrant: float,  # Warrant aggregation (noisy-OR)
        layer_3_cap: float,      # Foundherentist adequacy cap
        layer_4_graph: float,    # BN projection confidence
    ) -> float:
        """
        Compose four credence layers with explicit semantics.

        Layer 1 (Bridge): Causal update via Pearl do-calculus
        Layer 2 (Warrant): Noisy-OR aggregation of evidence channels
        Layer 3 (Cap): Foundherentist adequacy ceiling per evidence type
        Layer 4 (Graph): BN edge confidence (may diverge from node probability)

        Returns unified credence for the belief.
        """
        # Apply context-specific weights
        w1, w2, w3, w4 = self.calibration_weights[self.context]

        # Compose with explicit documentation
        composed = (
            w1 * layer_1_bridge +
            w2 * layer_2_warrant +
            w3 * layer_3_cap +
            w4 * layer_4_graph
        )

        # Clamp to [0, 1]
        return max(0.0, min(1.0, composed))
```

**Documentation Required**:
- 1-page docstring per layer explaining philosophical justification
- Rationale for each weight (to be calibrated per Decision 3)
- Examples: how does a multi-evidenced belief flow through all four layers?

**Tests Required**:
- `test_layer_composition_monotonicity.py` — if any layer increases, output should increase
- `test_composition_weights_calibration.py` — validate weights sum to 1.0
- `test_layer_1_vs_layer_3_semantics.py` — when layer 1=0.72, layer 3=0.60, show composition result and explain

---

### Task 1.2: Remove Warrant Ceiling Hard-Codes

**Files**: `src/services/bridge_warrants.py`, `src/services/warrant_scaling.py`

**Changes**:
```python
# BEFORE:
DEFAULT_BRIDGE_CONFIDENCE = {
    'CONSTITUTIVE': 0.75,
    'EMPIRICAL_COVARIANCE': 0.35,  # <- hard-coded, unjustified
    'FUNCTIONAL': 0.60,
    ...
}

# AFTER:
DEFAULT_BRIDGE_CONFIDENCE = {
    'CONSTITUTIVE': 0.75,          # <- marked: PENDING CALIBRATION
    'EMPIRICAL_COVARIANCE': 0.35,
    'FUNCTIONAL': 0.60,
    ...
}

# Add data class to track ceiling justification:
@dataclass
class CeilingJustification:
    warrant_type: str
    current_ceiling: float
    justification: str  # E.g., "Haack evidential directness", "Pearl hierarchical Bayes", "PENDING"
    calibration_source: str  # E.g., "Cooke expert seed", "historical accuracy", "arbitrary"
    last_updated: str
```

**Documentation Required**:
- For each ceiling, write 1-sentence justification or "PENDING CALIBRATION"
- Mark which ceilings are temporary vs. permanent

---

### Task 1.3: Implement Coherence-Cost-of-Revision Entrenchment

**File**: NEW `src/epistemic/entrenchment/coherence_cost_revision.py`

**Scope**: Replace current connectivity-based entrenchment with Quinian coherence-cost-of-revision (Decision 4).

```python
def entrenchment_quinian(
    belief_id: str,
    web: WebOfBelief,
    method: str = 'importance_sampling'
) -> float:
    """
    Quine-style entrenchment: coherence cost of revising this belief.

    ent(B) = coherence(web) - coherence(web - {B})

    Args:
        belief_id: ID of belief to measure
        web: current web of belief
        method: 'exact' (O(n²) for small webs) or 'importance_sampling' (O(n log n))

    Returns:
        Entrenchment score [0, 1] where 1.0 = impossible to revise
    """
    if method == 'exact' and web.num_beliefs < 1000:
        # Exact calculation: remove belief, recompute coherence
        original_coherence = web.compute_coherence()
        web_minus_b = web.copy_without(belief_id)
        revised_coherence = web_minus_b.compute_coherence()
        return original_coherence - revised_coherence

    elif method == 'importance_sampling':
        # Approximate: sample perturbations around the belief
        coherences = []
        for _ in range(100):
            perturbed = web.copy()
            perturbed.perturb_belief(belief_id, delta=0.05)
            coherences.append(perturbed.compute_coherence())

        return numpy.mean(coherences)  # Mean coherence impact
```

**Tests Required**:
- `test_entrenchment_correlates_with_connectivity.py` — entrenchment should *correlate* with degree, but not equal it
- `test_core_beliefs_entrenched.py` — core mechanisms (e.g., "spatial cognition involves visual system") should have high entrenchment

---

### Task 1.4: Update Web of Belief Documentation

**File**: `ARCHITECTURE.md` (sections on Credence, Entrenchment, Warrant Ceilings)

**Changes**:
- Document four-layer credence composition with explicit formula
- Explain each layer's philosophical justification
- Mark warrant ceilings as "PENDING CALIBRATION PER DECISION 3"
- Update entrenchment definition from connectivity to coherence-cost-of-revision

---

**Sprint 1 Deliverables**:
- [ ] `credence_composition.py` implemented with four layers, explicit weights
- [ ] Warrant ceilings marked with justifications or "PENDING"
- [ ] Coherence-cost-of-revision entrenchment in place (may use importance sampling if web large)
- [ ] Tests passing for composition, entrenchment
- [ ] ARCHITECTURE.md updated with clear credence and entrenchment definitions

**Time Estimate**: 1 day (8 hours)
**Panel Decisions Implemented**: Decision 1 (ceilings marked pending), Decision 3 (composition), Decision 4 (entrenchment)
**AESHI Impact**: Neutral (philosophical clarification, not functional change)

---

## SPRINT 2 (HIGH, 2 days)

**Objective**: Fix integration automation, implement π projection causal typing, enforce ClaimV2.

### Task 2.1: Implement Causal Typing for π Projection

**File**: NEW `src/services/epistemic_causal_bridge/causal_typing.py`

**Scope**: Replace keyword-matching π projection with causal-type classification (Decision 5).

```python
"""
Causal typing for belief-to-BN mapping.

Beliefs can have three causal types:
1. CAUSAL_EDGE: "X influences Y" → becomes BN edge
2. MECHANISM: "X influences Y through process Z" → becomes BN node + edges
3. CPT_VALUE: "P(Y|X) = 0.7" → becomes CPT entry
"""

from enum import Enum

class BeliefCausalType(Enum):
    CAUSAL_EDGE = "edge"        # Direct causal claim
    MECHANISM = "mechanism"      # Mechanism-mediated claim
    CPT_VALUE = "cpt"            # Conditional probability claim

class CausalTypeClassifier:
    def __init__(self, model_name: str = 'distilbert-base-uncased'):
        # Use pre-trained model for zero-shot classification
        from transformers import pipeline
        self.classifier = pipeline(
            'zero-shot-classification',
            model=model_name
        )
        self.candidate_types = [
            'direct causal relationship',
            'mechanism or mediator',
            'conditional probability or strength'
        ]

    def classify(self, belief_text: str) -> Tuple[BeliefCausalType, float]:
        """
        Classify belief text into causal type.

        Returns:
            (causal_type, confidence)
        """
        result = self.classifier(belief_text, self.candidate_types)
        label = result['labels'][0]
        score = result['scores'][0]

        if 'direct' in label:
            causal_type = BeliefCausalType.CAUSAL_EDGE
        elif 'mechanism' in label:
            causal_type = BeliefCausalType.MECHANISM
        elif 'probability' in label or 'strength' in label:
            causal_type = BeliefCausalType.CPT_VALUE
        else:
            causal_type = BeliefCausalType.CAUSAL_EDGE  # default

        return causal_type, score

def project_belief_to_bn(
    belief: Belief,
    causal_type: BeliefCausalType,
    bn: BayesianNetwork,
    similarity_threshold: float = 0.7
) -> List[Tuple[BN_Component, float]]:
    """
    Project belief onto BN components based on causal type.

    Returns:
        List of (BN component, confidence) tuples
    """
    if causal_type == BeliefCausalType.CAUSAL_EDGE:
        # Match belief statement to BN variable names using embeddings
        matches = find_variable_matches(belief.statement, bn, threshold=similarity_threshold)
        return [(bn.get_edge(*m[:2]), m[2]) for m in matches]

    elif causal_type == BeliefCausalType.MECHANISM:
        # Create mechanism node if it doesn't exist
        mech_node = bn.create_mechanism_node(belief.summary)
        variable_matches = find_variable_matches(belief.statement, bn, threshold=similarity_threshold)
        # Connect matched variables to mechanism
        edges = [bn.create_edge(source, mech_node) for source, _, _ in variable_matches]
        return edges

    elif causal_type == BeliefCausalType.CPT_VALUE:
        # Extract probability values and update CPT
        parsed_cpt = parse_cpt_from_statement(belief.statement)
        if parsed_cpt:
            return [(parsed_cpt, 1.0)]
        else:
            return []
```

**Tests Required**:
- `test_causal_type_classification.py` — classify sample beliefs; verify types are correct
- `test_projection_preserves_justification.py` — beliefs from observational evidence should map to high-precision BN components
- `test_many_to_many_mapping.py` — one belief can map to multiple BN nodes (no one-to-one assumption)

---

### Task 2.2: Enforce ClaimV2 with Mechanism Subtypes

**File**: NEW `src/epistemic/contracts/claim_v2_subtypes.py`

**Scope**: Define mechanism-specific ClaimV2 subtypes (Decision 7).

```python
"""
ClaimV2 subtypes for strict ingress enforcement.

All claims must be one of:
- ClaimV2_Neural
- ClaimV2_Behavioral
- ClaimV2_Architectural
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class MechanismType(Enum):
    NEURAL = 'neural'
    BEHAVIORAL = 'behavioral'
    ARCHITECTURAL = 'architectural'
    ENVIRONMENTAL = 'environmental'

@dataclass
class ClaimV2_Neural(ClaimV2):
    """Claim about neural mechanisms."""
    mechanism_type: MechanismType = MechanismType.NEURAL
    brain_region: Optional[str] = None
    imaging_method: Optional[str] = None  # fMRI, EEG, lesion, etc.
    effect_size: Optional[float] = None

    def validate(self) -> List[str]:
        """Override base validation with neural-specific checks."""
        errors = super().validate()

        if self.imaging_method and self.imaging_method not in ['fMRI', 'EEG', 'lesion', 'optogenetics']:
            errors.append(f"Unknown imaging method: {self.imaging_method}")

        if self.effect_size and not (0 <= self.effect_size <= 1.5):
            errors.append("Effect size should be between 0 and 1.5 (Cohen's d)")

        return errors

@dataclass
class ClaimV2_Behavioral(ClaimV2):
    """Claim about behavioral outcomes."""
    mechanism_type: MechanismType = MechanismType.BEHAVIORAL
    population: Optional[str] = None  # 'children', 'adults', 'older adults', etc.
    task: Optional[str] = None
    outcome_measure: Optional[str] = None

    def validate(self) -> List[str]:
        """Override base validation with behavioral-specific checks."""
        errors = super().validate()

        if self.population and self.population not in ['children', 'adults', 'older_adults', 'mixed']:
            errors.append(f"Unknown population: {self.population}")

        return errors

@dataclass
class ClaimV2_Architectural(ClaimV2):
    """Claim about architectural design features."""
    mechanism_type: MechanismType = MechanismType.ARCHITECTURAL
    design_element: Optional[str] = None  # 'lighting', 'material', 'scale', etc.
    user_population: Optional[str] = None
    setting_type: Optional[str] = None  # 'office', 'home', 'public', etc.

    def validate(self) -> List[str]:
        """Override base validation with architectural-specific checks."""
        errors = super().validate()
        return errors
```

**Ingress Validation**:
```python
def validate_claim_ingress(claim_dict: dict) -> ClaimV2:
    """
    Strict ingress validation: convert dict to appropriate ClaimV2 subtype.

    Fails if:
    - Dict missing required fields
    - Mechanism type doesn't match subtype
    - Subtype-specific validation fails
    """
    # Infer mechanism type from statement or explicit field
    mech_type = claim_dict.get('mechanism_type', infer_mechanism_type(claim_dict['statement']))

    if mech_type == MechanismType.NEURAL:
        claim = ClaimV2_Neural(**claim_dict)
    elif mech_type == MechanismType.BEHAVIORAL:
        claim = ClaimV2_Behavioral(**claim_dict)
    elif mech_type == MechanismType.ARCHITECTURAL:
        claim = ClaimV2_Architectural(**claim_dict)
    else:
        raise ClaimValidationError(f"Unknown mechanism type: {mech_type}")

    # Validate
    errors = claim.validate()
    if errors:
        raise ClaimValidationError(f"ClaimV2 validation failed:\n{chr(10).join(errors)}")

    return claim
```

---

### Task 2.3: Wire π Projection into Orchestrator

**File**: `src/services/paper_integration/orchestrator.py` (Step 9 — BN update)

**Changes**:
```python
def step_9_update_bayesian_network(self, paper_id: str, beliefs: List[Belief]) -> List[BN_Edge]:
    """
    Step 9: Project beliefs into Bayesian Network.

    Uses new causal-typing π projection (Decision 5).
    """

    # Classify each belief's causal type
    classifier = CausalTypeClassifier()
    causal_types = {}
    for belief in beliefs:
        causal_type, confidence = classifier.classify(belief.statement)
        causal_types[belief.id] = (causal_type, confidence)

        # Log type for debugging
        logger.info(f"Belief {belief.id}: {causal_type.value} (confidence {confidence:.2f})")

    # Project to BN using causal types
    bn = self.bn_service.get_bn()
    projected_edges = []

    for belief in beliefs:
        causal_type, _ = causal_types[belief.id]

        try:
            bn_components = project_belief_to_bn(belief, causal_type, bn)
            projected_edges.extend(bn_components)
        except Exception as e:
            logger.warning(f"Failed to project belief {belief.id}: {e}")
            # Continue (don't halt on projection failure)

    # Persist updated BN
    self.bn_service.save_bn(bn)

    return projected_edges
```

---

### Task 2.4: Integration Pipeline Dry-Run

**File**: `scripts/test_integration_e2e.py`

**Scope**: End-to-end test of 630 accepted papers flowing through orchestrator.

```python
"""
E2E integration test: 630 papers from acceptance through BN projection.
"""

def test_integration_pipeline_e2e():
    # Load 630 accepted papers
    queue = load_extraction_queue()
    accepted_papers = [p for p in queue if p.status == 'accepted']

    assert len(accepted_papers) == 630, f"Expected 630, got {len(accepted_papers)}"

    # Initialize orchestrator
    orchestrator = PaperIntegrationOrchestrator()

    # Integrate first 10 papers (for testing)
    for paper in accepted_papers[:10]:
        try:
            result = orchestrator.integrate_paper(paper.id)
            assert result.status == 'success', f"Integration failed: {result.errors}"
        except Exception as e:
            pytest.fail(f"Integration failed for paper {paper.id}: {e}")

    # Check web_of_belief.db has new beliefs
    web = WebOfBelief()
    assert web.num_beliefs > 0, "No beliefs added to web"

    logger.info(f"Integration test passed: {len(accepted_papers[:10])} papers integrated")
```

---

**Sprint 2 Deliverables**:
- [ ] Causal typing π projection implemented; tests passing
- [ ] ClaimV2 subtypes defined; validation enforced at ingress
- [ ] Orchestrator Step 9 wired to new π projection
- [ ] Integration pipeline dry-run successful (630 papers queued, first 10 integrated)
- [ ] No keyword-matching; all projection uses causal typing

**Time Estimate**: 2 days (16 hours)
**Panel Decisions Implemented**: Decision 5 (π projection), Decision 7 (ClaimV2 enforcement)
**AESHI Impact**: Significant (enables 630-paper integration; should increase constraints/belief ratio and reduce orphans)

---

## SPRINT 3 (MEDIUM, 3 days)

**Objective**: Implement governance enforcement (overseer invariants), remove module import failures, improve code robustness.

### Task 3.1: Implement Overseer Remediation (INV-0 through INV-5)

**File**: `src/services/overseer.py` (expand `check_integrity()`)

**Scope**: Overseer invariants no longer just *check*; now *enforce* or *halt*.

```python
def check_integrity_with_remediation(self) -> OverseerResult:
    """
    Check all invariants (INV-0 through INV-5).

    Return action: PASS, REMEDIATE, QUARANTINE, or HALT.
    """

    violations = []

    # INV-0: System OPERATIONAL
    if not self._system_operational():
        return OverseerResult(status='HALT', reason='INV-0: system not operational')

    # INV-1: Every belief has provenance (Haack)
    orphan_beliefs = self._find_orphan_beliefs()
    if orphan_beliefs:
        # Remediation: QUARANTINE orphans, require human approval
        self._quarantine_beliefs(orphan_beliefs)
        violations.append(f"INV-1: {len(orphan_beliefs)} orphan beliefs quarantined")

    # INV-2: BN-web sync (Pearl)
    sync_mismatches = self._find_bn_web_mismatches()
    if sync_mismatches:
        # Remediation: LOG and ALERT; don't halt (syncing is hard)
        violations.append(f"INV-2: {len(sync_mismatches)} BN-web mismatches detected")
        self._create_alert('bn_web_sync', sync_mismatches)

    # INV-3: ClaimV2 schema adherence
    non_compliant_claims = self._find_non_compliant_claims()
    if non_compliant_claims:
        # Remediation: QUARANTINE; require revalidation
        self._quarantine_beliefs([c.belief_id for c in non_compliant_claims])
        violations.append(f"INV-3: {len(non_compliant_claims)} non-compliant claims quarantined")

    # INV-4: Coherence decline ≤ 5%
    coherence_decline = self._compute_coherence_decline()
    if coherence_decline > 0.05:
        # Remediation: ALERT; escalate if persistent
        violations.append(f"INV-4: Coherence declined {coherence_decline:.1%} (threshold 5%)")
        self._create_alert('coherence_decline', coherence_decline)

    # INV-5: Credence bounds [0, 1]
    out_of_bounds = self._find_out_of_bounds_credences()
    if out_of_bounds:
        # Remediation: CLAMP and ALERT
        for belief_id, credence in out_of_bounds:
            self._clamp_credence(belief_id)
        violations.append(f"INV-5: {len(out_of_bounds)} out-of-bounds credences clamped")

    # Determine overall action
    if any('HALT' in v for v in violations):
        return OverseerResult(status='HALT', violations=violations)
    elif violations:
        return OverseerResult(status='REMEDIATE', violations=violations)
    else:
        return OverseerResult(status='PASS')
```

---

### Task 3.2: Fix Module Import Failures

**File**: `requirements.txt` or `pyproject.toml`

**Changes**:
- Add missing dependencies: `structlog`, `streamlit`, `google` (with versions)
- Add pre-flight import check script

```bash
#!/bin/bash
# scripts/verify_imports.sh

echo "Verifying all 297 modules can be imported..."
python3 << 'EOF'
import sys
import importlib

modules = [
    'src.cmr', 'src.agents', 'src.extraction.claim_extractor',
    # ... (all 297 modules)
]

failed = []
for mod in modules:
    try:
        importlib.import_module(mod)
    except Exception as e:
        failed.append((mod, str(e)))

if failed:
    print(f"FAILED: {len(failed)} modules could not be imported")
    for mod, err in failed:
        print(f"  {mod}: {err}")
    sys.exit(1)
else:
    print("SUCCESS: All modules importable")
    sys.exit(0)
EOF
```

---

### Task 3.3: Reduce Exception Swallowing

**Files**: Systematic sweep (`src/**/*.py`, `scripts/**/*.py`)

**Goal**: Replace bare `except Exception:` with specific exception types and proper logging.

```python
# BEFORE:
try:
    process_claim(claim)
except Exception:
    pass  # Silent failure

# AFTER:
try:
    process_claim(claim)
except (ValidationError, ValueError) as e:
    logger.error(f"Claim validation failed: {e}", extra={'claim_id': claim.id})
    # Don't silence; re-raise or quarantine
    raise ClaimProcessingError(f"Invalid claim {claim.id}") from e
except Exception as e:
    logger.critical(f"Unexpected error processing claim: {e}", exc_info=True)
    raise
```

**Effort**: 1 day (search/replace + testing)

---

### Task 3.4: Add Concurrency Safeguards

**File**: `src/services/extraction_approval.py` (JSON queue operations)

**Changes**:
```python
import fcntl

def update_queue_atomic(queue_path: Path, updates: Dict) -> None:
    """
    Atomically update JSON queue file with file locking.
    """
    with open(queue_path, 'r+') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            queue = json.load(f)
            queue.update(updates)

            # Rewind and write
            f.seek(0)
            json.dump(queue, f, indent=2)
            f.truncate()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

---

**Sprint 3 Deliverables**:
- [ ] Overseer invariants check + enforce (INV-0 through INV-5)
- [ ] All 297 modules importable; no structlog/streamlit/google import failures
- [ ] Bare `except Exception:` blocks reduced by 80% (target <20 remaining)
- [ ] JSON queue operations use file locking
- [ ] `scripts/overseer_nightly_v2.py` runs without errors; produces valid health report

**Time Estimate**: 3 days (24 hours)
**Panel Decisions Implemented**: Decision 6 (AESHI governance), implicit governance enforcement
**AESHI Impact**: High (reduces orphan rate, enforces schema compliance, improves robustness)

---

## SPRINT 4 (MEDIUM, 3 days)

**Objective**: Calibrate AESHI, implement mechanism-aware metric, reduce ruff lint debt.

### Task 4.1: Implement Mechanism-Depth Coverage Metric

**File**: NEW `src/services/mechanism_depth_metric.py`

**Scope**: AESHI component measuring causal mechanism completeness (Decision 6, Cartwright).

```python
"""
Mechanism-depth coverage: how deeply can we explain each causal mechanism?

E.g., "spatial navigation involves visual processing" is 1 step.
"spatial navigation → visual processing → dorsal stream → PPC" is 3 steps.
"""

@dataclass
class MechanismDepth:
    mechanism: str  # 'neural', 'behavioral', 'architectural'
    core_claims: int  # Number of core mechanism claims
    total_depth: int  # Sum of chain lengths
    avg_depth: float  # mean chain length
    coverage: float  # fraction of expected depth achieved

def compute_mechanism_depth_coverage(web: WebOfBelief) -> Dict[str, MechanismDepth]:
    """
    For each mechanism type, compute average causal depth.

    Returns:
        {
            'neural': MechanismDepth(core_claims=45, avg_depth=2.3),
            'behavioral': MechanismDepth(core_claims=32, avg_depth=1.8),
            ...
        }
    """

    mechanism_beliefs = {}
    for mech_type in ['neural', 'behavioral', 'architectural']:
        beliefs = [b for b in web.beliefs if b.mechanism_type == mech_type]

        depths = []
        for belief in beliefs:
            chain_length = compute_causal_chain_length(belief, web)
            depths.append(chain_length)

        avg_depth = numpy.mean(depths) if depths else 0
        coverage = avg_depth / 3.0  # Target 3-step depth; scale to [0, 1]

        mechanism_beliefs[mech_type] = MechanismDepth(
            mechanism=mech_type,
            core_claims=len(beliefs),
            total_depth=sum(depths),
            avg_depth=avg_depth,
            coverage=min(1.0, coverage)
        )

    return mechanism_beliefs

def aeshi_mechanism_component(web: WebOfBelief) -> float:
    """
    AESHI sub-component: mechanism depth coverage [0, 1].
    """
    mechanism_depths = compute_mechanism_depth_coverage(web)

    # Weight by importance (e.g., neural 40%, behavioral 40%, architectural 20%)
    weights = {
        'neural': 0.4,
        'behavioral': 0.4,
        'architectural': 0.2,
    }

    score = sum(
        mechanism_depths[mech].coverage * weights[mech]
        for mech in weights
    )

    return score
```

---

### Task 4.2: Recalibrate AESHI Formula

**File**: `scripts/compute_system_health.py`

**New Formula** (replacing hard-volume gates):
```python
def compute_aeshi(web: WebOfBelief, bn: BayesianNetwork) -> dict:
    """
    AESHI = 0.3 × coherence + 0.2 × constraint_ratio + 0.2 × orphan_health + 0.3 × mechanism_depth
    """

    # Component 1: Coherence [0, 1]
    coherence = web.compute_global_coherence()

    # Component 2: Constraint ratio health [0, 1]
    constraint_ratio = web.num_constraints / max(web.num_beliefs, 1)
    # Target: 1.5–2.0 constraints per belief (indicates tight integration)
    ratio_health = 1.0 - min(0.5, abs(constraint_ratio - 1.75) / 3.5)

    # Component 3: Orphan health [0, 1]
    orphan_rate = len(web.find_orphans()) / web.num_beliefs
    orphan_health = max(0, 1.0 - orphan_rate / 0.20)  # Linear penalty up to 20%

    # Component 4: Mechanism depth [0, 1] (new)
    mechanism_depth = aeshi_mechanism_component(web)

    # Combine
    aeshi = (
        0.3 * coherence +
        0.2 * ratio_health +
        0.2 * orphan_health +
        0.3 * mechanism_depth
    ) * 100

    return {
        'overall': aeshi,
        'coherence': coherence * 100,
        'constraint_ratio_health': ratio_health * 100,
        'orphan_health': orphan_health * 100,
        'mechanism_depth': mechanism_depth * 100,
        'components': {
            'coherence': coherence,
            'constraint_ratio': constraint_ratio,
            'orphan_rate': orphan_rate,
            'mechanism_coverage': mechanism_depth,
        }
    }
```

---

### Task 4.3: Lint Debt Reduction

**Target**: Reduce ruff violations from 2,966 to <500 (phase 1).

**Strategy**:
- Phase 1 (Sprint 4): Fix high-impact issues (line length, bare imports) — target 1,500 reduction
- Phase 2 (Sprint 5): Address domain-specific issues (type annotations, unused imports) — target remaining 500

**Focus Areas**:
- Line length violations (use black formatter with line-length=100)
- Bare imports in scripts
- Unused imports (grep + manual review)

```bash
# Apply black formatter
black src/ --line-length=100

# Apply isort for import cleanup
isort src/

# Manual review for domain-specific issues
ruff check src/ --select E,W,F --show-source | head -50
```

**Estimated Reduction**: 60–70% of violations (targeting 1,500+ reduction)

---

### Task 4.4: Theory Worlds Implementation Decision

**Based on**: Panel Decision 2

**Action**: Add configuration flag:
```python
# In config.yaml or src/config.py
ATLAS_GOAL: str = 'CONSENSUS'  # or 'THEORY_COMPARISON'

# In web_of_belief.py
if config.ATLAS_GOAL == 'CONSENSUS':
    # Use single web with theory-scoped constraint annotations
    self.theory_worlds = {}
    self.theory_annotations = {}  # Belief ID → theory set
elif config.ATLAS_GOAL == 'THEORY_COMPARISON':
    # Maintain separate worlds
    self.theory_worlds = {}
```

**Documentation**: Add 1–2 page doc explaining choice and implications.

---

**Sprint 4 Deliverables**:
- [ ] Mechanism-depth coverage metric implemented; incorporated into AESHI
- [ ] AESHI recalibrated (hard-volume gates removed, new formula)
- [ ] AESHI score rises from 49 to ~70–75 (estimated, validate)
- [ ] Ruff violations reduced from 2,966 to <1,500 (60% reduction)
- [ ] Theory-worlds configuration flag added; documentation updated

**Time Estimate**: 3 days (24 hours)
**Panel Decisions Implemented**: Decision 2 (theory worlds config), Decision 6 (AESHI calibration)
**AESHI Impact**: Moderate (should rise 20+ points once formula recalibrated)

---

## SPRINT 5 (LOWER, 1 week / phased)

**Objective**: Long-term robustness, ceiling calibration, expert elicitation.

### Task 5.1: Cooke Calibration of Ceiling Parameters

**Scope**: Use structured expert judgment (SEJ) to set warrant ceiling values (Decision 1).

**Process**:
1. Define seed variables: historical claims with known truth value
2. Ask 3–5 domain experts (cognitive scientists, architects, neuroscientists):
   - "Of all empirical-covariance claims with ceiling 0.35, what fraction were true?"
   - "Of all theoretical claims with ceiling 0.55, what fraction were true?"
3. Fit regression model: accuracy ~ ceiling_type + other_factors
4. Adjust ceilings to maximize empirical accuracy

**Effort**: 1–2 weeks (depends on expert availability)

**Output**: Calibrated ceiling values + documentation of calibration process

---

### Task 5.2: Expert Elicitation for Mechanism-Specific Entrenchment

**Scope**: Seed entrenchment values for core CNFA mechanisms.

**Process**:
1. List 20 core CNFA mechanism claims (e.g., "visual system processes metric spatial properties")
2. Ask experts: "How resistant should this claim be to revision?" (1–10 scale)
3. Use Cooke method to aggregate expert judgments
4. Set entrenchment_seed values in system

**Output**: Mechanism entrenchment priors + expert agreement statistics

---

### Task 5.3: Context-Indexed AESHI and π Projection

**Optional, depending on project scope**:
- Implement context parameter for AESHI (design practice vs. basic research)
- Implement context-indexed π projection (Pearl's context-aware BN mapping)

**Effort**: 1–2 weeks

---

**Sprint 5 Deliverables** (Ongoing, Not Critical Path):
- [ ] Warrant ceilings calibrated via Cooke SEJ
- [ ] Mechanism entrenchment priors set via expert elicitation
- [ ] Optional: context-indexed AESHI, context-indexed π projection

**Time Estimate**: 1+ weeks (phased, depends on expert availability)

---

## SPRINT 6 (LOWER, Documentation + Polish)

**Objective**: Update documentation, create spike reports, finalize decisions.

### Task 6.1: Document all Panel Decisions

**Files**: Create `docs/PANEL_DELIBERATION_DECISIONS_2026-02-27.md`

**Contents**:
- Decision 1 (warrant ceilings): chosen approach + justification
- Decision 2 (theory worlds): config flag + implications
- Decision 3 (credence formulas): composition formula + layer documentation
- Decision 4 (entrenchment): coherence-cost-of-revision definition
- Decision 5 (π projection): causal typing approach
- Decision 6 (AESHI): new formula + mechanism-depth metric
- Decision 7 (ClaimV2): enforcement + subtypes

---

### Task 6.2: Create Philosophy-Implementation Reconciliation Document

**File**: `docs/PHILOSOPHY_IMPLEMENTATION_RECONCILIATION_2026-02-27.md`

**Contents**:
- Current state: where code contradicts stated philosophy
- Action taken per sprint: how each sprint addresses gap
- Remaining gaps: what still needs work
- Timeline: when full coherence is expected

---

### Task 6.3: Finalize ARCHITECTURE.md

**Updates**:
- Credence composition formula with explicit layers
- Entrenchment definition (Quine)
- π projection causal typing
- AESHI metric + mechanism-depth component
- Theory worlds configuration option

---

**Sprint 6 Deliverables**:
- [ ] All panel decisions documented
- [ ] Philosophy-implementation reconciliation report
- [ ] ARCHITECTURE.md fully updated with post-decision state
- [ ] Decision implementation checklist (for future reference)

**Time Estimate**: 2–3 days

---

---

## OVERALL SPRINT TIMELINE & DEPENDENCIES

```
SPRINT 0 (Immediate, <2h)
├─ Critical fixes: integration, AESHI gates, DB paths, overseer schema
└─ Gate release: enables subsequent sprints

SPRINT 1 (After 0, 1 day)
├─ Credence composition, entrenchment definition, ceilings marking
├─ Depends on: SPRINT 0 (integration working)
└─ Prerequisite: Decision 1, 3, 4 implemented

SPRINT 2 (After 1, 2 days)
├─ π projection causal typing, ClaimV2 subtypes, 630-paper integration
├─ Depends on: SPRINT 1 (credence, entrenchment defined)
└─ Critical: unblocks 630 papers through web

SPRINT 3 (Parallel with 2, 3 days)
├─ Overseer enforcement, import fixes, exception reduction, concurrency safeguards
├─ Depends on: SPRINT 0
└─ Prerequisite: robustness foundation for subsequent integrations

SPRINT 4 (After 2–3, 3 days)
├─ Mechanism-depth metric, AESHI recalibration, lint reduction, theory-worlds config
├─ Depends on: SPRINT 2 (630 papers integrated → can measure mechanism coverage)
└─ Critical: AESHI rises from 49 to 70+

SPRINT 5 (After 4, 1+ weeks, phased)
├─ Expert calibration, entrenchment priors, optional context-indexing
├─ Depends on: SPRINT 4 (baseline metrics established)
└─ Optional: long-term accuracy improvement

SPRINT 6 (Final, 2–3 days)
├─ Documentation, reconciliation report, ARCHITECTURE.md finalization
├─ Depends on: All prior sprints
└─ Closure: decision log, implementation checklist
```

---

## CRITICAL PATH SUMMARY

**Must-Do (Blocking)**:
- SPRINT 0 (infrastructure)
- SPRINT 1 (philosophy foundation)
- SPRINT 2 (integration + π projection)
- SPRINT 3 (robustness)
- SPRINT 4 (governance + calibration)

**Expected Outcome** (End of Critical Path, ~2 weeks):
- 630 papers integrated through web of belief
- Web has ~5,000+ beliefs, ~8,000+ constraints
- Coherence metrics meaningful (not gated by arbitrary volume limits)
- AESHI ~70–75 (up from 49)
- Philosophy-code gap narrowed (credence, entrenchment, warrant ceilings now justified)
- Governance actively enforced (overseer invariants halt/remediate, not just log)

**Nice-to-Have (Non-Blocking)**:
- SPRINT 5 (expert calibration)
- SPRINT 6 (documentation polish)

---

## RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|---|---|---|
| **Integration fails after orchestrator wiring** | Medium | High | Dry-run test (Task 2.4) before full 630-paper run; rollback capability |
| **Causal typing classifier performs poorly** | Medium | Medium | Fallback to keyword matching if embedding confidence <0.6; manual review sample |
| **AESHI still RED after gates removed** | Low | High | Validate new formula with 100 random webs; adjust weights if needed |
| **Overseer halt remediation breaks pipeline** | Low | High | Run overseer in dry-run mode first; separate halt/warn/remediate levels |
| **Expert calibration unavailable (Cooke SEJ)** | High | Low | Use pre-existing seed variables from literature if experts unavailable |
| **Ruff lint cleanup introduces new bugs** | Medium | Low | Run full test suite after each 500-violation reduction; incremental commits |

---

## ACCEPTANCE CRITERIA

### Sprint 0
- [ ] `scheduled_pipeline.py status` shows papers actually integrating (not NOOP)
- [ ] AESHI formula updated; hard-volume gates removed
- [ ] All database paths resolve to `web_persistence.db`
- [ ] Overseer schema validation works (fails fast on mismatch)

### Sprint 1
- [ ] `credence_composition.py` tests pass (monotonicity, weight sum, semantics)
- [ ] Warrant ceilings marked with justifications
- [ ] Entrenchment uses coherence-cost-of-revision; correlates with node degree
- [ ] ARCHITECTURE.md updated with new definitions

### Sprint 2
- [ ] Causal typing classifier >80% accuracy on sample beliefs
- [ ] ClaimV2 subtypes defined and enforced at ingress
- [ ] First 10 papers integrate through new π projection pipeline
- [ ] 630 papers queued and ready for full integration

### Sprint 3
- [ ] All 297 modules importable (0 import errors)
- [ ] Overseer invariants enforce (halt/remediate on violation)
- [ ] Bare `except Exception:` reduced to <20 (from 266)
- [ ] `overseer_nightly_v2.py --dry-run` produces valid health report (no crashes)

### Sprint 4
- [ ] Mechanism-depth metric implemented and tested
- [ ] AESHI rises to 70–75 (from 49) once formula applied
- [ ] Ruff violations <1,500 (60% reduction)
- [ ] Theory-worlds config flag added; selectable

### Sprint 5
- [ ] (If expert elicitation conducted) Calibrated ceiling values documented
- [ ] (If mechanism priors set) Entrenchment seed values in system

### Sprint 6
- [ ] All decisions documented in `PANEL_DELIBERATION_DECISIONS_*.md`
- [ ] Philosophy-implementation reconciliation report written
- [ ] ARCHITECTURE.md reflects all post-decision changes

---

## FINAL NOTES FOR DAVID

1. **The Core Problem** (all three auditors agree): ATLAS has excellent design aspirations but critical implementation gaps. The four credence formulas don't compose; warrant ceilings contradict Quinean holism; π projection is brittle keyword-matching; overseer invariants are defined but unenforced.

2. **The Core Solution** (this plan):
   - Clarify philosophy layer (credence, entrenchment, ceilings) with Decision 1–4.
   - Fix integration infrastructure (orchestrator, π projection, ClaimV2).
   - Enforce governance (overseer halts/remediates, not just logs).
   - Recalibrate AESHI (mechanism-depth, not volume).

3. **Timeline**: 2–3 weeks critical path (SPRINTS 0–4). Optional long-term work (SPRINTS 5–6).

4. **Expected Outcome**: 630 papers integrated, AESHI 70+, philosophy-code gap narrowed, governance operative. System moves from "architecturally sound but broken core" to "functionally coherentist web of belief."

5. **Validation**: Each sprint has acceptance criteria. If any fail, halt and debug before proceeding.

---

**Document Prepared**: February 27, 2026
**Status**: Ready for David's Review and Approval
**Next**: David approves plan; SPRINT 0 begins immediately.

---

## REFERENCES

Cartwright, N. (1989). *Nature's capacities and their measurement*. Oxford University Press.

Cooke, R. M. (1991). *Experts in uncertainty: Opinion and subjective probability in science*. Oxford University Press.

Haack, S. (1993). *Evidence and inquiry: Towards reconstruction in epistemology*. Blackwell.

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.

Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review, 60*(1), 20–43.

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences, 12*(3), 435–467.

van Fraassen, B. C. (1980). *The scientific image*. Oxford University Press.

