# Mapping the Epistemic Landscape: How Computational Systems Can — and Should — Distinguish What We Don't Know from What We Can't Know

**ATLAS (Architecture for Typed, Layered Assessment of Science): A System for Deriving the Neural Chains Behind Architecture-Behavior Relationships**

*Draft Paper – February 23, 2026; Expanded February 24, 2026; T1.5 Implementation Documented February 25, 2026; ATLAS naming and web of belief terminology updated February 26, 2026; Terminology and naming sweep completed February 27, 2026*

*MASTER_DOC version saved February 27, 2026*

*Terminology updated per Session 2 decisions (2026-02-27). See docs/02-27_04_Exchange_Summary_Session2.md*

*David Kirsh, Department of Cognitive Science, UC San Diego*

---

# MASTER TABLE OF CONTENTS

*This document is a comprehensive working archive (~500–750 pages when complete) containing the full theoretical, empirical, computational, and methodological content of the ATLAS system. Sections marked `[WRITTEN]` contain finished prose. Sections marked `[SKELETON]` contain a structural outline with source-file annotations indicating which repository documents should be absorbed. Sections marked `[ABSORBED]` have been compiled from source documents through the Section Builder process (see SECTION_BUILDER_PROCESS.md).*

*The document is intentionally maximal — a repository of everything the system knows, how it works, and why. Publishable papers, grant proposals, course materials, and design manuals are extracted from this substrate, not written from scratch.*

---

## How to Navigate This Document

This Master Document contains four interlinked layers of material. The reading path depends on your role and familiarity with ATLAS:

**For first-time readers (begin here):**
1. Read Parts I–III (§1–§47) to understand the explanation gap, the system's design philosophy, and the prediction pipeline. These sections establish why ATLAS exists and what it does.
2. Read §49–§50 (Quinean foundations and tiered theories) to grasp the epistemic framework.
3. Skim the introduction to one expert panel (e.g., §60 VISUAL-I) to see how the system works in practice.
4. Read §140 (Cheat Sheet) or the external summary document for a quick reference.

**For theorists and epistemologists:**
- Part II (§33–§42): Theoretical foundations, Quinean webs, mechanisms, and bridge warrants.
- §49–§51: Credence calculus and the coherentist epistemology underlying ATLAS.
- §53: The independence assumption problem and open theoretical questions.

**For mathematicians and computational researchers:**
- §48–§48A: The projection calculus, log-odds formalism, warrant types with canonical transfer reliabilities, and the EN/π/BN three-layer architecture.
- §52: Confidence discipline and review protocols.
- Technical appendix (external): Detailed mathematical proofs and implementation guidance.

**For practitioners (architects, landscape designers, building scientists):**
- §1–§35: The explanation gap and mechanism walkthroughs; understand the "why" behind design recommendations.
- §45–§47: The prediction pipeline and value-of-information scoring.
- Parts V–XVII (§54–§78): Expert panel outputs organized by domain (visual properties, light, acoustics, social-environmental factors, thermal comfort). Each panel section contains template descriptions, mechanism chains, and worked examples. Use §140 (Cheat Sheet) to find templates relevant to your project.

**For system architects and reviewers:**
- §48–§48A: The operational projection calculus and three-layer architecture.
- §54: The interstitial section "From Formalism to Calibration" explaining how panels operationalize the projection formula.
- §60–§78: Expert panel sections, focusing on the "EN edges calibrated" and "warrant type assignments" noted in each panel's opening.
- Part XVIII (if present): Deployment frameworks, software interfaces, and system integration.

**For quality assurance and maintenance:**
- §52: Confidence discipline and review protocols.
- Exchange Summary document (external): Session 2 decisions, decision rationale, and current status.
- Terminology index (§2.5): Maps old terminology to new ω/d/δ framework.

**Quick lookups:**
- "Where do I find information about X?" → See the Thematic Index at Part XXI (if present).
- "What is the projection formula?" → §48.3 (single-edge) or §48.4–§48.5 (serial/parallel).
- "How do I estimate population transfer for my context?" → §48.3A (Population Transfer Factor Assignment).
- "What are the warrant types and their transfer reliabilities?" → §48.1 (table at end of section).

---

## CRITICAL: Formula Transition Note

**STATUS OF THE CREDENCE CALCULUS IN THIS DOCUMENT**

The ATLAS system is transitioning from a legacy three-factor credence formula to a new four-factor log-odds projection calculus. This note clarifies which formula is operationally authoritative and why the document contains both.

**The Canonical Formula (Operationally Deployed)**

The four-factor log-odds projection calculus, defined in §48 and §48A, is the **current and future standard**:

**logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)**

This formula is operationally deployed in the system. It contains four epistemically distinct components:
- **d(τ)**: Transfer reliability, determined by warrant type (fixed: CONSTITUTIVE 0.95, MECHANISM 0.80, EMPIRICAL_ASSOCIATION 0.80, FUNCTIONAL 0.65, CAPACITY 0.55, ANALOGICAL 0.40, THEORY_DERIVED 0.25)
- **ω**: Warrant strength, reflecting study quality and replication (0–1)
- **δ(pop, pop_target)**: Population transfer factor, accounting for demographic and cultural distance (0–1)
- **logit(p_lab)**: Log-odds of the empirically observed effect

This formula is used to compute template credence values and populate Bayesian Network Conditional Probability Tables (CPTs).

**The Legacy Three-Factor Formula (Pedagogical Reference)**

Throughout Parts V–XVII (§54–§78), the document discusses a three-factor credence formula:

**P(composite) = P(parent) × P(bridge) × P(CNFA-specific)**

This formula was the original ATLAS credence model and appears in panel sections because those sections predate the transition to the four-factor formalism. The three-factor formula is retained for three reasons:
1. **Historical record**: It documents how the system evolved.
2. **Pedagogical clarity**: In simple cases where population transfer is approximately uniform across contexts, the three-factor formula provides intuitive explanation.
3. **Legacy integration**: Some existing panel calibrations reference this framework.

**However**, the three-factor formula has known limitations (documented in §53: The Independence Assumption Problem). The four-factor formula addresses these limitations by disaggregating "confidence" into three separate epistemic dimensions (d, ω, δ) and using log-odds arithmetic to avoid epistemic incoherence.

**Mapping Between Formulas**

If you encounter the three-factor formula in older sections, understand it as follows:
- **P(parent)** ≈ contributes to overall warrant strength through the evidence supporting the parent theory; partially captured by ω
- **P(bridge)** ≈ corresponds to transfer reliability d; the likelihood that the bridge relationship (e.g., "proxy confidence") transfers across contexts
- **P(CNFA-specific)** ≈ corresponds to study-specific evidence quality and population transfer; captured by ω · δ

**Recommendation for New Work**

For any **new template calibration, new domain panels, or extended applications**, use §48's projection calculus exclusively. Assign:
1. Warrant type τ (determines d)
2. Warrant strength ω (evidence quality)
3. Population transfer factor δ (demographic distance)
4. Empirically observed probability p_lab (lab finding)

Then compute: **logit(p_target) = d · ω · δ · logit(p_lab)** and recover **p_target = σ(logit(p_target))**.

For implementation details, see §48–§48A. For population transfer factor canonical values, see §48.3A (Population Transfer Factor Assignment). For worked examples, see §48.7–§48.11.

---

