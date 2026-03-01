# The Molecule Layer: A Deep Reflection on Role, Design, and Expansion

**Date:** 2026-02-24  
**Author:** Antigravity (Agentic AI), in consultation with the Article Eater project  
**Status:** Living Document

---

## 1. What Is a Molecule?

In the Article Eater system, a **Molecule** is a Tier 2 composite construct that sits between the raw empirical claims extracted from individual papers (Tier 0) and the broad theoretical frameworks that organize the Web of Belief (Tier 3).

The metaphor is deliberate. Just as in chemistry, where atoms (individual empirical claims) combine into molecules (stable, functional compounds), here individual **Templates** (the "atoms" — e.g., T27: "DMN re-engagement → model maintenance") combine into **Molecules** (stable theoretical constructs — e.g., "Attention Restoration Theory"). The molecule is, therefore, the smallest *meaningful theoretical unit* that a non-specialist user would recognize and care about.

### The Three-Tier Hierarchy

| Tier | Name | Example | Granularity |
|------|------|---------|-------------|
| **0** | Extracted Claims | "Nature exposure reduced cortisol by d=0.43 (p<.01)" | Single data point from one paper |
| **1** | Templates | T27: "Low-demand → DMN re-engagement → restoration" | A single mechanistic pathway, grounded in multiple papers |
| **2** | **Molecules** | ART: "Attention Restoration Theory" | A named theory composed of multiple interacting templates |
| **3** | Frameworks | DT: "Dual-Task / Directed Attention" | A broad family of theories sharing assumptions |

### Why This Layer Exists

Without Molecules, the system faces a presentation problem. There are 51+ templates across 12+ frameworks. A website user asking "Why do parks make me feel better?" does not want to see a list of 10 templates about DMN subsystems, cortisol pathways, and theta oscillations. They want to see **"Attention Restoration Theory says..."** — a recognizable, coherent answer that synthesizes the template-level evidence into a narrative.

Molecules solve this by providing:
1. **A human-readable entry point** into the Web of Belief.
2. **A cache boundary** for pre-computed QA summaries (Level 1-3 Progressive Disclosure).
3. **An invalidation unit** for the QA Cache Manager: when a new PDF updates a template, the system knows which Molecules are affected.
4. **A navigation taxonomy** for the Streamlit app sidebar and future website.

---

## 2. How Molecules Currently Work in the System

### 2.1 Data Flow

```
PDF → Extraction Pipeline → Findings → Templates 
                                           ↓
                                      Molecules ← composed from Templates
                                           ↓
                                    QA Cache Manager ← hashes template state
                                           ↓
                                    Pre-Compute Pipeline ← generates L1/L2/L3 summaries
                                           ↓
                                    MoleculeAwareRouter ← serves to Streamlit frontend
```

### 2.2 Structural Properties

Each Molecule has:
- **Components**: Named sub-parts (e.g., ART has "Soft Fascination", "Being Away", "Extent", "Compatibility"). Each component maps to specific templates.
- **Constituent Templates**: The full list of templates that underpin the molecule.
- **Interaction Graph**: How templates relate to each other within the molecule (ADDITIVE, SYNERGISTIC, PREREQUISITE, MULTIPLICATIVE).
- **Empirical Support Level**: ESTABLISHED, SUPPORTED, PRELIMINARY, MIXED.
- **Framework IDs**: Which Tier 3 frameworks the molecule belongs to.
- **Scope Conditions**: Under what conditions the molecule's claims hold.

### 2.3 Operational Uses

| System Component | How It Uses Molecules |
|---|---|
| **QA Cache Manager** | Tracks which templates a Molecule depends on; flags cache as STALE when templates change |
| **Pre-Compute Pipeline** | Generates the L1 (summary), L2 (context), L3 (mechanistic) answers *per Molecule* |
| **MoleculeAwareRouter** | Routes user queries to the correct Molecule's cached answer |
| **Streamlit Frontend** | Displays Molecules in a sidebar taxonomy with progressive disclosure accordions |
| **Provenance System** | (Future) Aggregates Haack Foundherentist scores across a Molecule's constituent templates |

---

## 3. The Current Molecules: An Honest Assessment

We currently have 3 molecules: **ART**, **SRT**, and **Prospect-Refuge**. These are all "restoration and safety" constructs from environmental psychology. This is a narrow slice of the full template landscape.

### Coverage Analysis

Looking at the 51+ templates and 12+ frameworks in `template_id_aliases.json`, the current molecules cover:

| Framework | Templates in Registry | Covered by Existing Molecules? |
|---|---|---|
| **DT** (Dual-Task / Directed Attention) | T4, T10, T16, T27, T48 | Partially (ART uses T27) |
| **NM** (Neuromodulation) | T5, T6, T11, T17, T26, T41, T42 | Partially (SRT uses T5, T8) |
| **PP** (Predictive Processing) | T1, T2, T15, T21, T22, T31 | Partially (ART uses T1, T2, T31) |
| **SN** (Spatial Navigation) | T3, T23, T24, T33 | Partially (ART uses T23; PR uses T3) |
| **EC** (Embodied Cognition) | T8, T18, T19, T28, T34 | Partially (ART/SRT use T8) |
| **IC** (Interoception) | T7, T12, T29, T35 | Partially (SRT uses T12; ART uses T29) |
| **MS** (Memory Systems) | T10, T25, T47 | ❌ Not covered |
| **HC** (Heuristics & Cognitive Control) | T36, T37, T38 | ❌ Not covered |
| **MSI** (Multisensory Integration) | T31, T33, T34, T39, T40, T46 | ❌ Not covered |
| **CB** (Chronobiology) | T30, T32 | ❌ Not covered |
| **XF** (Cross-Framework) | T13, T14, T19, T20 | ❌ Not covered |
| **DP** (Dual Process) | T9, T19, T43 | ❌ Not covered |
| **CREA** (Creativity) | CREA1-4, T51 | ❌ Not covered |
| **AX** (Awe) | AX1-AX12 | ❌ Not covered |
| **BRECVEMA** (Musical Emotion) | BRECVEMA 1-6 | ❌ Not covered |

**Conclusion:** Only ~15 of 51+ core templates are currently organized into Molecules. The Neuromodulation, Multisensory, Chronobiology, Creativity, Awe, and Cognitive Control frameworks are entirely unrepresented. This is a major gap.

---

## 4. Proposed New Molecules

Based on the template registry and the natural theoretical clusters that emerge from the frameworks, I propose the following new Molecules, organized by the type of value they add:

### 4.1 High-Priority: Core Environmental Psychology Theories

These are "household name" theories that users will search for directly.

#### **BIOPHILIA** — The Biophilia Hypothesis
- **Why:** One of the most commonly searched terms in environmental design. Currently has no molecule despite being tagged extensively in the extraction pipeline.
- **Components:** Nature Affinity (T9: DP_IMPLICIT_EVALUATION), Material Preference (HAP_SURFACE_MATERIAL_001), Fractal Response (AUDITORY_FRACTAL_SCALING_001, visual fractal templates)
- **Constituent Templates:** T9, T13, T34, plus NATURAL_MATERIAL_CONVERGENCE_001, BIOPHILIC_DOSE_RESPONSE_001
- **Framework:** EC, DP
- **Empirical Support:** ESTABLISHED

#### **WAYFINDING** — Spatial Navigation & Cognitive Mapping
- **Why:** Huge practical relevance for architects. The SN framework has 4+ templates but no molecule.
- **Components:** Cognitive Map Formation (T3: SN_LAYOUT), Path Integration (T24: Theta Sequences), Context-Dependent Memory (T23: SN_CONTEXT_MEMORY), Navigation Stress (T14: XF_NAVIGATION_STRESS)
- **Constituent Templates:** T3, T23, T24, T14, CROSS_MB_MF_ARBITRATION_001
- **Framework:** SN, XF
- **Empirical Support:** SUPPORTED

#### **CIRCADIAN_ARCHITECTURE** — Light, Time, and the Built Environment
- **Why:** The CB framework is entirely uncovered. Circadian lighting is a growing field with increasing regulatory attention.
- **Components:** Photoentrainment (T30: CHRONO_LIGHT_ENTRAINMENT), Subcortical Encoding (T32: AUD_SUBCORTICAL_ENCODING), Temporal Processing (ARCH_PROMENADE_TEMPORAL_PE_001)
- **Constituent Templates:** T30, T32, ARCH_PROMENADE_TEMPORAL_PE_001
- **Framework:** CB
- **Empirical Support:** SUPPORTED

### 4.2 Medium-Priority: Emerging and Cross-Framework Constructs

These are less commonly searched but represent important theoretical advances.

#### **MULTISENSORY_DESIGN** — How Senses Combine in Architecture
- **Why:** The MSI framework has 5+ templates but no molecule. Multisensory design is increasingly important in healthcare and hospitality.
- **Components:** Congruency Effects (T39: MSI_CONGRUENCY), Inverse Effectiveness (T40: MSI_INVERSE), Haptic-Material (T34: HAP_SURFACE_MATERIAL), Crossmodal Binding (CROSSMODAL_CONGRUENCE_001), Thalamic Filtering (T46: CROSS_THALAMIC)
- **Constituent Templates:** T39, T40, T34, T46, CROSSMODAL_CONGRUENCE_001
- **Framework:** MSI, PP
- **Empirical Support:** PRELIMINARY

#### **COGNITIVE_LOAD_ARCHITECTURE** — Environmental Demands on Working Memory
- **Why:** The HC framework is entirely uncovered. This is one of the most practically actionable constructs for designers (reduce cognitive load → better performance).
- **Components:** Working Memory Capacity (T36: HC_WORKING_MEMORY_LOAD), Ecological Rationality (T37: ER_ECOLOGICAL_RATIONALITY), Hierarchical Control (T38: HC_HIERARCHICAL_CONTROL), Cognitive Offloading (T28: EC_COGNITIVE_OFFLOADING)
- **Constituent Templates:** T36, T37, T38, T28
- **Framework:** HC, EC
- **Empirical Support:** SUPPORTED

#### **AWE_ARCHITECTURE** — The Experience of Awe in Built Environments
- **Why:** The AX (Awe) framework has 12+ templates and represents a rich, emerging field. The experience of awe in cathedrals, museums, and monumental spaces is highly relevant for visitors and designers.
- **Components:** Vastness Perception (AX1), Small Self Effect (AX3_SMALL_SELF_001), Attention Mediation (AX_ATTENTION_MEDIATION_010), Dose-Response (AX_DOSE_RESPONSE_007)
- **Constituent Templates:** AX1, AX2, AX3, AX3_AWE_MECHANISM_001, AX3_SMALL_SELF_001, AX4, AX_ATTENTION_MEDIATION_010, AX_DOSE_RESPONSE_007
- **Framework:** AX (new framework)
- **Empirical Support:** PRELIMINARY

#### **CREATIVE_ENVIRONMENTS** — How Spaces Foster Creativity
- **Why:** The CREA framework has 4+ templates but no molecule. This is directly relevant for workplace design.
- **Components:** Creative Network Dynamics (CREA1), Processing Style Modulation (CREA2), Incubation Architecture (CREA3), Collaborative Creativity (CREA4/T51)
- **Constituent Templates:** CREA1, CREA2, CREA3, CREA4, T51, CROSS_CREATIVE_NETWORK_DYNAMICS_001, CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001
- **Framework:** CREA (new framework)
- **Empirical Support:** PRELIMINARY

### 4.3 Low-Priority but Valuable: Specialized Constructs

#### **SOCIAL_ARCHITECTURE** — How Spaces Shape Social Behavior
- **Why:** Templates T19, T48, T49, T50 form a clear cluster around social cognition in architecture.
- **Components:** Social Affordances (T19: XF_SOCIAL_AFFORDANCE), DMN Social Cognition (T48: DT_SOCIAL_COGNITION_DMN), Architectural Loneliness (T49: CROSS_ARCHITECTURAL_LONELINESS), Social Enrichment (T50: CROSS_SOCIAL_ENRICHMENT)
- **Framework:** DT, EC
- **Empirical Support:** PRELIMINARY

#### **ALLOSTATIC_REGULATION** — The Body's Budget in Architecture
- **Why:** The IC (Interoception) framework's core concept is allostatic load, which integrates many other constructs.
- **Components:** Allostatic Anticipation (T7: IC_ALLOSTATIC_ANTICIPATION), Interoceptive Affect (T12: IC_INTEROCEPTIVE_AFFECT), Master Allostatic Cost (T29: ALLOSTATIC_MASTER)
- **Framework:** IC
- **Empirical Support:** SUPPORTED

#### **ACOUSTIC_WELLBEING** — Sound, Music, and Spatial Experience
- **Why:** The AUD and BRECVEMA templates form a rich acoustic cluster.
- **Components:** Auditory Scene Analysis (T31: AUD_SCENE_ANALYSIS), Reverberation-Space (T33: AUD_REVERBERATION), Acoustic Emotion (ACOUSTIC_EMOTION_MAPPING_001), BRECVEMA mechanisms
- **Framework:** MSI, PP, NM
- **Empirical Support:** PRELIMINARY

---

## 5. What Would More Molecules Add to the System?

### 5.1 For the Website / QA Engine
- **More entry points**: Instead of 3 topics in the sidebar, users could navigate 12+ meaningful constructs.
- **Better query routing**: The `MoleculeAwareRouter` would be able to match queries like "How does ceiling height affect creativity?" to the `CREATIVE_ENVIRONMENTS` molecule directly.
- **Richer pre-computed content**: More cached L1/L2/L3 summaries means more of the website's content is static and fast.

### 5.2 For the Extraction Pipeline
- **Smarter classification**: If we know which Molecules exist, the extraction pipeline could ask the LLM not just "Is this paper empirical?" but "Which of these 12 Molecules does this paper's evidence support?" This could dramatically improve both classification accuracy and extraction recall.
- **Targeted prompts**: Instead of a generic extraction prompt, we could generate Molecule-specific prompts that prime the LLM to look for the exact types of claims that matter for that Molecule.

### 5.3 For the Web of Belief / BN
- **Coherence checking**: Molecules define expected interaction patterns between templates. If a new paper's evidence contradicts the expected interaction (e.g., "Soft Fascination INHIBITS Being Away" rather than being ADDITIVE), the system could flag this as a potential coherence violation worthy of expert review.
- **Gap analysis**: The system could identify which Molecules have weak empirical support and which templates within those Molecules are most in need of new evidence.

### 5.4 For the Provenance System
- **Aggregate grounding scores**: Instead of reporting individual template provenance, the system could compute a Molecule-level "Foundherentist Score" that summarizes how well-grounded the entire theory is.
- **Crossword visualization**: This would enable a visual display showing how the templates within a Molecule support each other, and where the "weak links" in the justificatory chain are.

---

## 6. Design Considerations for New Molecules

### 6.1 When Should Something Be a Molecule vs. a Template?

A construct qualifies as a Molecule if:
1. **It has a recognized name** in the literature (e.g., "Biophilia", "Wayfinding").
2. **It requires multiple templates** to explain fully (a single-template construct is just a template).
3. **Its components interact** (they are not merely a list; there are SYNERGISTIC, PREREQUISITE, or MULTIPLICATIVE relationships).
4. **A user might search for it** on a website (if nobody would ask about it, it probably shouldn't be a navigation-level construct).

### 6.2 Avoiding Molecule Sprawl

There is a danger of over-molecularizing. Not every cluster of related templates needs its own Molecule. The test is: **Does this Molecule tell a story that a single template cannot?** If the answer is no, the templates are better left as standalone entries in the Web of Belief.

### 6.3 Molecule Versioning

As new papers are extracted and new templates are created, Molecules will need to evolve. The `overall_maturity` field (TENTATIVE → PRELIMINARY → SUPPORTED → ESTABLISHED) provides a natural versioning mechanism. Some Molecules may even need to be *split* as evidence accumulates (e.g., "Restoration" might eventually split into distinct ART and SRT molecules — which we have already done).

---

## 7. Recommendations

1. **Immediately create** the BIOPHILIA, WAYFINDING, and CIRCADIAN_ARCHITECTURE molecules. These are the highest-value additions because they represent well-known theories that users will search for directly.

2. **Create in the next sprint** the MULTISENSORY_DESIGN, COGNITIVE_LOAD_ARCHITECTURE, and AWE_ARCHITECTURE molecules. These represent emerging but important fields.

3. **Defer** the SOCIAL_ARCHITECTURE, ALLOSTATIC_REGULATION, and ACOUSTIC_WELLBEING molecules until their constituent templates have more empirical support in the extraction pipeline.

4. **Integrate Molecules into the extraction pipeline** by adding a "Molecule tagging" step that asks the LLM which Molecules a paper's findings support, before running the detailed extraction prompt. This would dramatically improve both classification and recall.

5. **Expand the `Molecule` schema** to include:
   - `competing_theories`: List of other Molecules that offer alternative explanations for the same phenomena.
   - `design_implications`: Concrete, actionable guidance for practitioners (e.g., "Include fractals at 1/f scaling in wall textures").
   - `confidence_intervals`: Numeric range reflecting the spread of effect sizes across the constituent templates.

---

*This is a living document. It should be updated as new Molecules are created and the extraction pipeline evolves.*
