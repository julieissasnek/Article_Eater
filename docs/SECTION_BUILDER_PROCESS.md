# SECTION BUILDER PROCESS

**A Repeatable Editorial Pipeline for Compiling the Master Document**

*Created: February 24, 2026*
*Author: David Kirsh & Claude Opus 4.6*
*For: NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md*

---

## 1. Purpose

The master document is intended to grow to 500–750 pages by absorbing, vetting, and synthesizing the ~12 MB of substantive content scattered across 144+ files in the Article_Eater_PostQuinean_v1 repository. This document specifies the repeatable process by which any Claude session can pick up any `[SKELETON]` section and produce a `[WRITTEN]` or `[ABSORBED]` section of consistent quality.

The process is designed to be:
- **Resumable**: Any session can pick up any section without needing the full conversation history.
- **Auditable**: Every section records what sources it drew from, what was vetted, and what was changed.
- **Quality-controlled**: A structured review pass ensures recency, accuracy, informativeness, and completeness.
- **Non-destructive**: Source documents are never modified; the master document supersedes them.

---

## 2. The Five-Phase Pipeline

### Phase 1: GATHER

**Goal**: Identify and read all source documents for the target section.

**Steps**:
1. Read the `[SKELETON]` entry in the master document's TOC for the target section.
2. Note all `ABSORB FROM:` source files listed.
3. Read each source file completely. For files > 200 lines, read in chunks and take notes.
4. Identify any ADDITIONAL relevant sources not listed in the skeleton (use Grep/Glob to search for keywords from the section topic across the full docs/ and scripts/ directories).
5. **Consult the Example Catalog** (`docs/EXAMPLE_CATALOG_2026-02-24.md`). Check which worked examples, case studies, and walkthroughs are tagged for this section's domain. Read the Tier 1 examples first — these are well-written and should be absorbed with minimal rewriting. Tier 2 examples need editorial polish. Tier 3 examples contain useful data but need substantial rewriting.
6. Record findings in a working scratchpad (temporary file in /sessions/).

**Output**: A source inventory for the section:
```
## Source Inventory for §XX: [Section Title]
| Source File | Size | Last Modified | Relevance |
|-------------|------|---------------|-----------|
| [path]      | [KB] | [date]        | PRIMARY / SECONDARY / REFERENCE |
```

### Phase 2: VET

**Goal**: Assess each source for recency, accuracy, and currency. Flag stale or superseded content.

**Steps**:
1. **Recency check**: Compare dates across source files. If multiple versions exist (e.g., Calibration Registry V1.4 → V2.1), use ONLY the latest version. Note which earlier versions are superseded.
2. **Accuracy check**: Cross-reference claims against:
   - The actual template JSON files in `data/templates/` (ground truth for calibrated parameters)
   - The actual Python code in `scripts/` (ground truth for computational behavior)
   - The TASKS.md completed entries (ground truth for what was actually done vs. planned)
3. **Consistency check**: Look for contradictions between sources. Common issues:
   - Template counts may differ (earlier docs say 151, latest says 208 total / 103 calibrated)
   - Confidence ranges may have been recalibrated (ceiling adjudication changed some values)
   - T1.5 roster may differ (3 were rejected in the Feb 23 assessment)
   - Panel counts may differ (earlier docs may not include CROSSCUT-I or NEUROMOD-I)
4. **Currency check**: Has anything changed since the source was written? Check:
   - Did a later sprint modify the content described?
   - Did a Ruthless Review override any claims?
   - Did the ceiling adjudication algorithm change any parameters?

**Output**: A vet report:
```
## Vet Report for §XX
- Sources consulted: [N]
- Superseded sources: [list]
- Contradictions found: [list with resolution]
- Stale content flagged: [list]
- Ground-truth verified against: [templates/code/tasks checked]
```

### Phase 3: OUTLINE

**Goal**: Design the section structure before writing prose.

**Steps**:
1. Determine the section's **core argument** — what is the ONE thing the reader should understand after reading this section?
2. Determine **subsections** — typically 3–7, each advancing one component of the core argument.
3. For each subsection, note:
   - Key claims (with source file and line reference)
   - Key data (tables, numbers, parameters)
   - Key examples (worked examples, case studies)
   - Competing views or uncertainties
4. **Plan example placement**. Every section should contain at least one concrete, worked example that makes the abstract machinery tangible. Prioritize:
   - Tier 1 examples from the Example Catalog (absorb with minimal rewriting)
   - Panel debate excerpts where experts disagree on mechanism (these are the most intellectually alive passages)
   - Quantitative walkthroughs where a specific number gets computed (e.g., melanopic dose at 2× ceiling depth, credence calculation for VIEW1)
   - Before/after comparisons where a design change maps to specific template re-ratings
   - Cross-modal examples where two sensory domains interact unexpectedly
5. Determine **what to include and what to omit**. The guiding principle:
   - INCLUDE: anything that advances understanding of the system's epistemic structure
   - INCLUDE: anything David has explicitly flagged as important
   - INCLUDE: scientific references with citations
   - INCLUDE: worked examples that make abstract principles concrete — these are the document's lifeblood
   - OMIT: implementation details that don't illuminate conceptual structure
   - OMIT: sprint logistics, session coordination, debugging narratives
   - OMIT: content that duplicates another section (cross-reference instead)
6. Estimate target length (pages).

**Output**: A structured outline with source annotations.

### Phase 4: WRITE

**Goal**: Produce the section prose.

**Writing Standards**:
- **Style**: Clean academic writing in the Bertrand Russell tradition — precise, unpretentious, occasionally wry, but without exaggerated Britishisms. Longer rather than shorter. Thorough explanations over brevity.
- **Voice**: First-person plural ("we") for system descriptions; impersonal for theoretical claims. The system has a point of view and is not afraid to state it, but always distinguishes certainty from uncertainty.
- **Citations**: APA format in-text, with full references at section end. Include Google Scholar citation count where known. When there is scientific disagreement, say so explicitly and name the positions.
- **Structure**: Prose paragraphs, not bullet points. Tables for data, not for argument. Equations only where they earn their keep (i.e., the formula actually gets computed somewhere in the system).
- **Accessibility**: NEVER use dark blue text on dark backgrounds. Follow WCAG 2.1 AA standards for any visual elements.
- **Cross-references**: Use `§XX` notation to reference other sections in the master document.

**Content Standards**:
- Every factual claim about the system should be verifiable against the codebase or template library.
- Every theoretical claim should have at least one academic reference.
- Every parameter value should cite its source (panel output, meta-analysis, standards document).
- Competing accounts and open questions should be explicitly flagged, not buried.
- Design decisions should be recorded with rationale (link to DECISIONS.md where applicable).

**Process**:
1. Write the section in the master document, replacing the `[SKELETON]` tag with content.
2. Mark the section `[ABSORBED — from: {source files}, vetted: {date}]`.
3. Add new references to the appropriate references section.
4. If the section is long (>15 pages), write it in multiple Edit calls, building subsection by subsection.

### Phase 5: VERIFY

**Goal**: Confirm the written section is accurate, complete, and well-integrated.

**Steps**:
1. **Spot-check**: Pick 3–5 specific factual claims in the section and verify them against the source of truth (template JSON, Python code, or cited paper).
2. **Completeness check**: Compare the section outline against the written prose — was anything planned but not written?
3. **Cross-reference check**: Ensure any `§XX` references point to sections that exist (or are at least in the skeleton).
4. **Redundancy check**: Search the master document for passages that overlap substantially with the new section. If found, consolidate — keep the better version, cross-reference from the other.
5. **Integration check**: Does the section's terminology match the rest of the document? (e.g., "template" vs. "mechanism template", "informativeness" vs. "VOI" — use consistent terms).

**Output**: Update section status tag:
```
[ABSORBED — from: {source files}, vetted: {date}, verified: {date}]
```

---

## 3. Section Priority Ordering

The following priority ordering reflects both intellectual dependency (later sections depend on earlier ones being right) and risk of content loss (content that exists only in scattered files is more at risk than content already consolidated).

### Priority 1: High Risk of Loss / High Dependency
These sections contain content that is currently scattered across many files and would be hardest to reconstruct:

| Section | Part | Source Size | Why Priority |
|---------|------|-------------|-------------|
| §60–71 (12 Domain Panels) | VI | ~1.8 MB | Largest body of substantive content; panel outputs are the empirical backbone |
| §72–78 (T1.5 Reductions) | VII | ~450K | Formal reductions are intellectually critical and spread across 6+ files |
| §84–89 (Web of Belief) | IX | ~260K | Core epistemological architecture, complex multi-file content |

### Priority 2: Conceptually Central
These sections define the system's intellectual identity:

| Section | Part | Source Size | Why Priority |
|---------|------|-------------|-------------|
| §48–53 (Credence Calculus) | IV | ~200K | The formula at the heart of CMR |
| §79–83 (IE-DPT) | VIII | ~320K | The superordinate framework; David's distinctive theoretical contribution |
| §90–95 (Template Library) | X | ~330K | The concrete deliverable; what the system actually produced |

### Priority 3: Methodologically Important
These sections document how the work was done:

| Section | Part | Source Size | Why Priority |
|---------|------|-------------|-------------|
| §54–59 (Expert Panel Method) | V | ~250K | Novel methodology; publishable on its own |
| §107–113 (Limitations) | XIII | ~300K | Intellectual honesty; pre-empts reviewers |
| §96–100 (Architectural Typology) | XI | ~100K | New content from this session |

### Priority 4: Application and Reference
These sections are important but can be built later:

| Section | Part | Source Size | Why Priority |
|---------|------|-------------|-------------|
| §114–118 (Goldilocks/Design) | XIV | ~5 MB | Applied content; depends on everything else |
| §119–124 (Variables/Implementation) | XV | ~600K | Reference material; less prose-dependent |
| Appendices A–E | — | ~400K | Supporting material |

---

## 4. Session Protocol

At the START of any session that will build sections:

1. Read this document (SECTION_BUILDER_PROCESS.md).
2. Read the master document's TOC to see which sections are `[SKELETON]` vs. `[ABSORBED]`.
3. Check TASKS.md for any pending section-building tasks.
4. Pick the highest-priority `[SKELETON]` section that is not currently claimed by another terminal.
5. Claim the section in ACTIVE_TASKS.md (if parallel work is active).
6. Run the five-phase pipeline (GATHER → VET → OUTLINE → WRITE → VERIFY).
7. Update TASKS.md with the completion.

At the END of any session:

1. If a section is partially complete, mark it `[IN PROGRESS — {date}, completed through §XX.Y]`.
2. Record what was done in TASKS.md session log.
3. Note any issues discovered that affect other sections.

---

## 5. Quality Metrics

A completed section should meet ALL of the following:

| Metric | Standard | How to Check |
|--------|----------|-------------|
| **Recency** | All content reflects the latest version of every source | Vet report confirms no superseded sources used |
| **Accuracy** | All factual claims verified against ground truth | Spot-check 3–5 claims against templates/code |
| **Informativeness** | Section adds understanding beyond what any single source provides | Does the synthesis reveal connections or tensions not visible in individual sources? |
| **Completeness** | No major topic in the source material is omitted without explanation | Compare outline against source file TOCs |
| **Integration** | Section is well-connected to the rest of the master document | Cross-references present; terminology consistent |
| **Citation quality** | All claims have APA citations where applicable | References section updated with new entries |
| **Readability** | Clean academic prose; no bullet-point dumping | Read the first and last paragraphs — do they flow? |

---

## 6. Handling Conflicts and Contradictions

When source documents contradict each other:

1. **Check dates** — the more recent document usually wins.
2. **Check ground truth** — if a template JSON disagrees with a panel output document, the JSON wins (it's the implemented version).
3. **Check TASKS.md** — if a task was completed that modifies the content, the post-task state wins.
4. **Check the Ruthless Review** — if the Review flagged something, the Review's finding wins.
5. **If genuinely unresolvable** — document both positions in the section with a `[OPEN QUESTION]` tag and add to the Decision Pending table in TASKS.md.

---

## 7. Version Control

The master document filename includes its creation date (2026-02-23). As the document grows:

- **Do NOT rename the file** — other documents and scripts may reference it.
- **DO update the header date** (the "Expanded: " date) each time significant content is added.
- **DO update the word count estimate** in the footer.
- **DO commit to git** after each completed section with message: `docs: absorb §XX [Section Title] into master paper`.

---

*This process document is itself subject to revision as we learn what works. The goal is not bureaucratic compliance but consistent quality across a multi-session, multi-hundred-page compilation effort.*
