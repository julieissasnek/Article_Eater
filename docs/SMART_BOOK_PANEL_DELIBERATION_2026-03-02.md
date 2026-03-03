# Panel Deliberation: Living Master Document Architecture

**Date**: 2026-03-02  
**Status**: DELIBERATION ONLY — not for implementation yet  
**Trigger**: User concern that the master book (~17K lines) goes stale as the system evolves rapidly, and that early sections become wrong when later innovations change the system  
**Next step**: Claude should also deliberate; then both agents discuss with user before implementing  

---

## The Problem Statement

The master document (`MASTER_DOC_CMR_2026-02-25.md`, ~17,785 lines, 124+ sections) serves simultaneously as:
1. **Authoritative specification** — what the system IS
2. **Design rationale** — WHY it's that way
3. **Historical record** — HOW it evolved
4. **Teaching document** — explaining the intellectual foundations

When the system changes rapidly (e.g., T1.5 going from 4→13 theories in a single session), early sections that mention "4 T1.5 theories" become *wrong* but nobody notices because:
- Two agents work concurrently, neither systematically updates the book
- No mechanism alerts you when a change in §78 invalidates claims in §50
- The book has no dependency graph between its own sections

---

## Panel Deliberation

### Panelist 1 — Donald Knuth (Literate Programming)

> "You've rediscovered the central problem of literate programming: code and documentation must be ONE artifact, or they diverge. Your master document is a *derived* artifact — it describes a system that changes independently. This will always rot.
>
> **My prescription**: The master document should contain *executable assertions*. When §50 says '4 T1.5 theories,' that should be a reference to a canonical value, not a hardcoded string. Think of it like LaTeX `\ref{}` — you don't write 'see Figure 3,' you write 'see Figure \ref{fig:architecture},' and the number updates automatically.
>
> For your system, this means sections should reference canonical sources:
> ```
> The system tracks {{T1_5_COUNT}} domain theories (see §78 for full roster).
> ```
> A pre-commit or nightly script resolves `{{T1_5_COUNT}}` from `schemas/theory/tier1_5_domain_theories.json` and flags any section where the resolved value has changed since last render."

### Panelist 2 — Leslie Lamport (Specification & TLA+)

> "The deeper issue is that your document conflates *specification* and *narrative*. A specification should be formally verifiable — you should be able to check whether the system satisfies the spec. A narrative explains and motivates.
>
> **Separate the concerns:**
> 1. **Spec sections** — assertions about the system that can be mechanically checked (counts, invariants, data flow descriptions). Mark these with a `[SPEC]` tag. These MUST match code.
> 2. **Rationale sections** — WHY decisions were made. These don't go stale in the same way; the rationale for choosing Haack's foundherentism is still valid even if the implementation details change.
> 3. **Historical sections** — WHAT changed and WHEN. These are append-only and never go stale by definition.
>
> When an agent changes the system, it should update ALL `[SPEC]` sections that reference the changed concept. This is checkable — you can grep for `[SPEC]` blocks and verify them against code."

### Panelist 3 — Ward Cunningham (Wiki Inventor, Technical Debt)

> "You've described *documentation debt*, which is a subset of technical debt. It accumulates silently and then causes confusion or errors when people trust stale text.
>
> **The wiki approach**: Every concept should have ONE canonical definition, and everything else should link to it. When you say 'T1.5 domain theories' in §50, that should be a hyperlink to the canonical definition in §78. If §78 changes, every section that links to it is flagged for review.
>
> But there's a deeper pattern: **concept dependency graphs**. Your master document mentions concepts (T1.5, Goldilocks Principle, AESHI, credence intervals, etc.) and these concepts have dependencies. If you change the definition of 'credence interval,' every section that discusses credence must be reviewed. This is exactly what your tier taxonomy propagation procedure does — but for the *document*, not just the *code*.
>
> **Practical suggestion**: Maintain a `concept_index.json` that maps concept names to the sections that define and reference them. When a concept changes, the index tells you which sections to update."

### Panelist 4 — Susan Haack (Foundherentism — already in your system!)

> "This is delightfully recursive. Your epistemic network maintains coherence among beliefs using crossword constraints and foundational anchors. Your master document IS an epistemic artifact — it contains beliefs about your system. Why not apply your own epistemic infrastructure to it?
>
> Specifically:
> 1. **Sections are beliefs** — each section asserts something about the system
> 2. **Dependencies are constraints** — §50 and §78 both discuss T1.5, creating a coherence constraint
> 3. **Code is the foundation** — the actual system is the experiential/observational ground truth
> 4. **Staleness is incoherence** — when §50 says '4' and the code says '13,' the document has an internal contradiction
>
> Your Overseer already detects inconsistencies in the belief network. Why not run a 'Document Overseer' that detects inconsistencies between document sections and between document and code?
>
> This IS the smart book. It's a document with its own epistemic health score."

### Panelist 5 — Fred Brooks (The Mythical Man-Month, Design Documents)

> "The fundamental tension is between *completeness* and *currency*. A 17,000-line document cannot stay current when two agents make changes daily. My experience says:
>
> 1. **The document should be layered**, not monolithic:
>    - Layer 0: **Invariants** — things that NEVER change (philosophical commitments, architectural principles)
>    - Layer 1: **Architecture** — changes rarely (tier taxonomy structure, pipeline topology)
>    - Layer 2: **Implementation** — changes frequently (counts, algorithms, service wiring)
>    - Layer 3: **Status** — changes constantly (test counts, AESHI, feature flags)
>
> 2. **Only Layers 0-1 belong in a 'master book.'** Layers 2-3 should be in living documents that are generated from code (like your COORDINATION_STATE.md).
>
> 3. **History is invaluable** but should be in an appendix or changelog, not inline. 'We used to have 4 T1.5 theories; we now have 13' is interesting history but should not appear in the main text — the main text should just say '13' with a footnote to the changelog."

### Panelist 6 — Version Control Expert (Git Philosophy)

> "You already have the technology for this. Git tracks changes to files. The problem is that your master document is ONE file, so `git blame` shows you line-level changes but not concept-level changes.
>
> **Proposal**: Split the master document into section files:
> ```
> docs/master_doc/
>   00_introduction.md
>   34_tier_architecture.md
>   50_t15_theories.md
>   78_theory_roster.md
>   ...
> ```
> Each section file has YAML frontmatter:
> ```yaml
> ---
> section: 50
> title: T1.5 Domain Theories
> depends_on: [78, 34]
> defines_concepts: [t1_5_count, t1_5_roster]
> references_concepts: [t1_frameworks, tier_taxonomy]
> last_verified: 2026-03-02
> verified_by: AG
> ---
> ```
> A CI script checks: for every concept defined in one section, are all referencing sections up-to-date? This is your 'smart book' — it's just dependency tracking with section-level granularity."

---

## Panel Consensus: The Smart Book Architecture

The panelists converge on these principles:

### 1. Concept Registry (Cunningham + Knuth)
A machine-readable registry of key concepts with their canonical values and source files. Sections reference concepts, not hardcoded values.

### 2. Section Dependency Graph (Lamport + Haack)
Each section declares what it defines and what it references. A change to a defining section flags all referencing sections for review.

### 3. Layer Separation (Brooks)
Invariants and architecture in the master book. Implementation details and status in generated/living documents. History in changelogs.

### 4. Document Overseer (Haack — recursive application of our own system)
A lightweight checker that validates concept consistency across sections, analogous to the Overseer's invariant checks on the belief network.

### 5. Section-Level Versioning (Git Expert)
Split into trackable units OR add YAML frontmatter with dependency declarations. Either way, enable per-section audit trails.

---

## Precedents in Practice

| System | How It Solves This | Applicable Here? |
|--------|-------------------|-----------------|
| LaTeX `\ref{}` / `\cite{}` | Cross-references auto-update | Yes — concept references |
| Jupyter Book / MyST | Executable documentation with cross-refs | Yes — could render from source |
| Sphinx `.. include::` | Pull content from canonical sources | Yes — for counts/specs |
| AsciiDoc `include::[]` | Include fragments from other files | Yes — same pattern |
| RFC series | Each RFC obsoletes/updates earlier ones | Yes — change tracking |
| W3C specs | "At Risk" markers for unstable features | Yes — for Layer 2-3 content |
| Software BOMs | Dependency graphs for components | Yes — concept dependency graph |
| Design docs (Google) | "Invariants" section + status enum | Yes — Layer 0 separation |

---

## What AG Has Done That's Not in the Master Book

Based on this session and prior work, the following AG contributions are likely **not documented** in the master book:

1. **Tier Taxonomy Propagation Procedure** — 6-layer audit, 5 success conditions
2. **T1.5 expansion to 13** — including Goldilocks Principle provenance
3. **Tag engine kebab-case normalization** — T1_KEYWORDS cleanup
4. **Tier taxonomy verification test** — automated checking
5. **Interpretation layer as service** — Step 9 in enrichment orchestrator
6. **Multi-agent coordination system** — check-in/out, message board
7. **Service architecture extensions** — 5 new lazy-load services
8. **RAG vs Article Eater experiment design** — 40-question comparison
9. **V11 ruthless audit** — service architecture panel review
10. **Foundational paper audit** — 46/50 refs found but as citations not extracted papers

These represent design decisions and justifications that SHOULD be in the master book.

---

## Open Questions for User + Claude Discussion

1. **Monolith vs. split?** Keep one big file or split into section files with dependency frontmatter?
2. **How aggressive on automation?** Concept registry + nightly checker vs. manual discipline?
3. **Who maintains?** Should Claude own the book and AG contribute via MESSAGE_BOARD, or should both have write access?
4. **Scope**: Should the book include test/verification architecture (success conditions, Overseer, reflexes) as first-class sections? (AG's position: YES — these embody design principles)
5. **History format**: Inline "was X, now Y" annotations vs. separate changelog appendix?
