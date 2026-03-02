# Documentation Visualization Plan: From Text Walls to Cognitive Scaffolding

**Date**: March 2, 2026
**Author**: David Kirsh & Claude (Cowork Session 21)
**Status**: PLAN — awaiting David's review

---

## 1. The Problem

The ATLAS master document is 23,445 lines (~750 printed pages) of pure text. It contains zero embedded figures. It describes complex architectures (Bayesian networks, three-layer projection calculus, 10-framework tier hierarchy, 12 domain panels), inherently visual phenomena (fractal dimension, luminance contrast, spatial rhythm, acoustic spectra), and multi-step procedures (extraction pipeline, credence computation, panel convening) — all in prose alone.

The cognitive load this imposes on any reader — including David, Claude, and future collaborators — is severe. Research on multimedia learning (Mayer, 2009; cited >15,000 times) demonstrates that spatial-verbal integration produces deeper understanding than either modality alone, with effect sizes of d ≈ 0.70–1.00 for well-designed diagrams vs. text-only presentation. The same prediction-error optimization principle we describe in the Goldilocks paper applies here: readers build better mental models when information arrives through multiple complementary channels.

Meanwhile, the Goldilocks paper demonstrates what the documentation *could* look like: 10 figures with rich captions, every one following the Scientific American standard where a reader could understand the argument from captions and figures alone. The question is how to scale this quality across the entire documentation system.

## 2. Current State

| Asset Category | Count | Quality | Integration |
|---------------|-------|---------|-------------|
| Master doc (text) | 23,445 lines | Dense but well-organized | 0 figures embedded |
| Architecture figures (Figure1–7.svg) | 7 | Hand-coded, professional | Not embedded anywhere |
| Goldilocks figures (figure_1–10.svg) | 10 | Matplotlib, good captions | Embedded in one paper only |
| System diagrams (diagrams/*.svg) | 5 | Mermaid, minimal styling | Not embedded anywhere |
| Smaller docs (docs/*.md) | 493 | Varies | 2 have embedded images (0.4%) |

**Figure-to-page ratio**: Master doc = 1:∞ (zero figures). Goldilocks paper = 1:4 (excellent). Academic standard = 1:3–5 pages.

## 3. Design Principles for ATLAS Documentation Figures

These principles extend the paper-writing norms (now in CLAUDE.md) to the specific challenges of technical system documentation.

### 3.1 The "Caption-First" Principle

Before creating any figure, write the caption. If you can't write a 4–6 sentence caption that tells the reader what to look at, what pattern to notice, and why it matters — you don't yet know what the figure should show. The caption is the design specification.

### 3.2 The "Three Audiences" Principle

Every major figure should work for three audiences simultaneously:

1. **David** (system architect): Needs to see how components connect, where decisions were made, and what the current state is. Cares about theoretical fidelity and epistemic honesty.
2. **Claude/AG** (implementation agents): Needs to see data flow, module boundaries, and schema relationships. Cares about where code lives and what calls what.
3. **Future collaborators** (grad students, reviewers): Needs to understand the system without reading 750 pages. Cares about the big picture first, details on demand.

### 3.3 The "Progressive Disclosure" Principle

Borrow from the theory guides: three levels of detail.

- **Level 1 (Overview)**: One figure that shows the entire system. Anyone can grasp the architecture in 60 seconds.
- **Level 2 (Subsystem)**: One figure per major subsystem (projection calculus, tier hierarchy, each domain panel). A researcher studying one domain can understand it in 5 minutes.
- **Level 3 (Detail)**: Specific parameter charts, calibration curves, decision trees. An implementer can get exact values.

### 3.4 The "Grounded in Data" Principle

Where possible, figures should be generated from actual system data — not hand-drawn approximations. Query the database for real belief counts, real confidence distributions, real warrant type ratios. This keeps figures honest and makes them automatically updateable.

### 3.5 The "Master Figure Index" Principle

Create and maintain a `docs/FIGURE_INDEX.md` that maps every figure to the section(s) it belongs in, its generation script (if any), and its last-updated date. This prevents orphaned figures and ensures regeneration after major changes.

## 4. The Figure Inventory: What the Master Doc Needs

### Phase 1: Architecture Overview (3 figures)

These are the "Level 1" figures. They should be the first things a new reader sees.

| Fig # | Title | Section | Content | Type |
|-------|-------|---------|---------|------|
| M-1 | "The ATLAS Three-Layer Architecture" | §1, §48A | EN (epistemic network) → π (projection) → BN (Bayesian network). Show data flow, key transformations, feedback loops. | Boxology |
| M-2 | "The Tier Hierarchy: From Foundational Frameworks to Empirical Claims" | §50 | 10 T1 frameworks → 14 T1.5 domain theories → ~93 T2 templates → 3,420+ T3 beliefs. Show edge types between tiers. | DAG / hierarchy |
| M-3 | "The ATLAS Pipeline: From PDF to Belief" | §43–§47 | End-to-end: PDF intake → Gemini extraction → quality gate → credence computation → BN integration → coherence check → QA. | Flowchart |

**Note**: Figure1_Architecture.svg already exists in docs/ and covers M-1 partially. It should be updated and embedded. Figure3_Tier_Hierarchy.svg covers M-2 partially.

### Phase 2: The Credence Calculus (3 figures)

These are the "Level 2" figures for Part IV — the mathematical heart of the system.

| Fig # | Title | Section | Content | Type |
|-------|-------|---------|---------|------|
| M-4 | "Four Factors in the Projection Formula" | §48 | Visual decomposition of logit(p_target) = d·ω·δ·logit(p_lab). Each factor labeled with meaning, typical range, and what shifts it. | Annotated equation |
| M-5 | "How Warrant Strength (ω) Is Computed" | §48.3B | The warrant_strength.py pipeline: base ω → confidence multiplier → replication multiplier → meta-analytic multiplier. Show typical values. | Flow + value chart |
| M-6 | "Population Transfer: From Lab to Building" | §48.3A | Decision tree for δ assignment. Immersion hierarchy levels × claim types → δ values. | Decision tree |

**Note**: Figure2_Projection_Loss.svg and Figure4_Epistemic_vs_Aleatory.svg partially cover these. They should be updated, captioned, and embedded.

### Phase 3: Domain Panel Diagrams (12 figures, one per panel)

Each of the 12 domain panels in Parts V–VI should have one "panel overview" figure showing:
- Which T1 frameworks feed the panel
- How many templates the panel contains
- Warrant type distribution (pie chart or bar)
- Key parameters with their Goldilocks ranges
- One exemplar finding with full credence trace

| Fig # | Panel | Section | Special Content |
|-------|-------|---------|-----------------|
| M-7 | VISUAL-I | §60 | Fractal dimension D ≈ 1.3 curve + 3 visual dimensions |
| M-8 | LIGHT-I | §61 | Dual-pathway architecture (image-forming vs. non-visual) |
| M-9 | THERMAL-I | §62 | Adaptive comfort model curve + cultural calibration |
| M-10 | ACOUSTIC-I | §63 | Soundscape preference curve + quality modulation |
| M-11 | MUSIC-I | §64 | BRECVEMA 8-mechanism taxonomy with latencies |
| M-12 | STRESS-I | §65 | Cortisol temporal dynamics + allostatic regulation |
| M-13 | SOCIAL-I | §66 | Proxemics zones + density optimum |
| M-14 | MEMORY-I | §67 | Hippocampal spatial mapping → architectural wayfinding |
| M-15 | MULTI-I | §68 | Cross-modal interaction matrix |
| M-16 | CREATIVE-I | §69 | Flow state parameters + environmental conditions |
| M-17 | NEUROMOD-I | §70 | Triple convergence (dopamine/serotonin/opioids) at optimum |
| M-18 | CROSSCUT-I | §71 | Cross-panel interaction network |

### Phase 4: System Operations (3 figures)

| Fig # | Title | Section | Content | Type |
|-------|-------|---------|---------|------|
| M-19 | "The Nightly Pipeline: 13 Stages of Evidence Maintenance" | Overseer sections | Flowchart showing nightly integration pipeline stages, with health checks and failure modes. | Flowchart |
| M-20 | "The Recommendation Loop: From Gap to Article to Belief" | §47A–E | Circular flow: gap detection → VOI scoring → search dispatch → extraction → integration → new gap detection. | Circular flow |
| M-21 | "AESHI Score Computation: Six Subscores → One Number" | §53.8 | AESHI formula visualization: 6 colored bars feeding weighted sum. Show current scores. | Stacked bar + formula |

### Phase 5: Data-Driven Dashboards (3 figures, generated from DB)

These should be auto-generated from actual database queries so they stay current.

| Fig # | Title | Content | Data Source |
|-------|-------|---------|-------------|
| M-22 | "Evidence Landscape: 3,420 Beliefs by Tier, Framework, and Confidence" | Treemap or heatmap of belief distribution | `ae.db` → beliefs table |
| M-23 | "Warrant Type Distribution Across the Web of Belief" | Stacked bar showing EMPIRICAL_ASSOCIATION vs. MECHANISM vs. ANALOGICAL vs. CAPACITY | `ae.db` → warrant types |
| M-24 | "Schema Gaps: Where ATLAS Knows It Doesn't Know" | Heat map of gap density by domain panel × theory framework | `interpretation_space_suggestions` table |

**Total new figures**: 24
**Existing figures to update and embed**: 7 (Figure1–7.svg)
**Goldilocks figures**: 10 (already done, in paper only)
**Grand total when complete**: ~41 figures across the documentation system

## 5. Implementation Strategy

### 5.1 Scriptable Generation

Every figure should be generated by a Python script stored in `scripts/generate_*_figures.py`, following the pattern established by `scripts/generate_goldilocks_figures.py`. Benefits:

- Reproducible: anyone can regenerate figures after changes
- Updatable: data-driven figures reflect current DB state
- Consistent: all figures use the ATLAS palette and style from `contracts/VISUALIZATION_NORMS.md`
- Versionable: figure scripts are committed alongside the docs

### 5.2 The Master Figure Index

Create `docs/FIGURE_INDEX.md`:

```markdown
# ATLAS Figure Index

| Fig ID | Title | Section(s) | File | Generator Script | Last Updated |
|--------|-------|------------|------|------------------|--------------|
| M-1 | The ATLAS Three-Layer Architecture | §1, §48A | docs/figures/m1_three_layer.svg | scripts/generate_master_figures.py | 2026-03-XX |
| ... | ... | ... | ... | ... | ... |
```

### 5.3 Embedding Protocol

For the master doc (which is split into 21 parts in `docs/master_doc_parts/`):

1. Add figure references to the appropriate Part files
2. Use relative paths: `![M-1 caption...](figures/m1_three_layer.svg)`
3. Add a bold caption line below each figure (the "Title: Subtitle" format from the Goldilocks paper)
4. Run the assembly script to verify figures integrate correctly into the full document

### 5.4 Caption Generation Workflow

For each figure:

1. Write the caption FIRST (caption-first principle)
2. The caption specifies what the figure must show
3. Generate the figure to match the caption
4. Review figure + caption together
5. Apply the "could a reader understand the paper from captions alone?" test

### 5.5 Phasing

| Phase | Scope | Figures | Effort | Priority |
|-------|-------|---------|--------|----------|
| 1 | Architecture Overview | M-1, M-2, M-3 | ~4 hrs | **P0 — do first** |
| 2 | Credence Calculus | M-4, M-5, M-6 | ~4 hrs | P1 |
| 3 | Domain Panels | M-7 through M-18 | ~12 hrs | P1 |
| 4 | System Operations | M-19, M-20, M-21 | ~4 hrs | P2 |
| 5 | Data Dashboards | M-22, M-23, M-24 | ~4 hrs | P2 |
| **Total** | | **24 new figures** | **~28 hrs** | |

## 6. Documentation Style Extension

The paper-writing norms (now in CLAUDE.md) apply directly to the master document with these adaptations:

### What Changes for Internal Documentation

| Norm | Paper Version | Documentation Version |
|------|--------------|----------------------|
| Section orientation | 3–5 sentences, states punchline | Same — every section needs this |
| Figure density | 1 per 3–5 pages | 1 per 5–10 pages (less dense but still required) |
| Caption standard | Full Sci Am (5–8 sentences) | Moderate (3–5 sentences — direct the eye, state pattern, give implication) |
| In-figure titles | State the finding | State the architectural point |
| Confidence spectrum | Match phrasing to d-values | Match phrasing to ATLAS confidence levels |
| Evidence grounding | Check EN/BN | Same — query the web of belief |
| Equation scaffolding | Explain before, during, after | Same |

### What Stays the Same

- Lead with the point (every paragraph)
- Informative headings (state findings, not topics)
- Active voice default
- SCQA paragraph structure for expository sections
- Direct labeling on figures
- Colorblind-safe palette
- Tufte data-ink ratio

### What the Master Doc Specifically Needs (Beyond Figures)

1. **Section orientations**: Many of the 80+ sections currently jump straight into content. Each needs a 3–5 sentence orientation paragraph.

2. **Informative headings**: Replace generic headings ("Panel Results", "Discussion") with finding-stating headings ("Fractal Dimension Peaks at D ≈ 1.3 Because Natural Scenes Cluster There").

3. **Cross-references**: Currently sparse. Every section that introduces a concept should link to where that concept is formally defined.

4. **Summary tables**: Each domain panel should end with a summary table (the "design dashboard" pattern from the Goldilocks paper) showing key parameters and their Goldilocks ranges.

5. **Running example**: Consider threading one exemplar finding (e.g., "fractal facade complexity → aesthetic preference") through multiple sections to show how it flows through the entire pipeline.

## 7. Success Criteria

After implementing this plan, the documentation should pass these tests:

1. **The 60-Second Test**: A new reader can understand the ATLAS architecture by looking at M-1, M-2, M-3 and reading their captions. (~60 seconds)

2. **The Caption-Only Test**: A reader can understand any domain panel by reading only the figure captions, without reading body text.

3. **The Figure Index Test**: Every figure can be found via `docs/FIGURE_INDEX.md` and regenerated via its listed script.

4. **The Currency Test**: Data-driven figures (M-22, M-23, M-24) reflect the current state of `ae.db`, not a snapshot from weeks ago.

5. **The Goldilocks Test**: The figure density is neither too sparse (current state: zero in master doc) nor too dense (not every paragraph needs a figure). Target: 1 figure per 5–10 pages of master doc content.

---

## 8. Relationship to Paper Writing

Every figure created for the master doc is a *candidate* for future papers. The pipeline flows in one direction:

```
Master Doc Figures → Paper Figure Selection → Caption Enhancement → Publication
```

This means master doc figures should be created at "80% publication quality" — clean enough to drop into a paper with only caption polishing. The Goldilocks paper figures already demonstrate this: they were created for the paper but could serve the master doc equally well.

The reverse is also true: every paper we write should audit its claims against the master doc and its figures. The `paper_evidence_auditor.py` tool automates part of this — checking whether empirical claims in papers have ATLAS evidence backing.

---

## References

Mayer, R. E. (2009). *Multimedia learning* (2nd ed.). Cambridge University Press. [~15,200 citations]

Tufte, E. R. (2001). *The visual display of quantitative information* (2nd ed.). Graphics Press. [~9,800 citations]

Cleveland, W. S., & McGill, R. (1984). Graphical perception: Theory, experimentation, and application to the development of graphical methods. *Journal of the American Statistical Association*, 79(387), 531–554. [~3,400 citations]

---

*This plan was created as part of the ATLAS documentation improvement initiative. The paper-writing norms have been saved to CLAUDE.md for automatic enforcement in all future sessions.*
