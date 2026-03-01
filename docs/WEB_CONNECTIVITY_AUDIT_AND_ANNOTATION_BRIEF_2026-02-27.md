# Web of Belief: Full Connectivity Audit & Annotation System Brief

**For: Cowork Discussion**
**Date: 2026-02-27**
**Author: System (Antigravity)**

---

## 1. Current State of the Web

### What Exists (Assets)

| Layer | Count | Status |
|---|---|---|
| **Templates** | 208 | 103 calibrated, 105 uncalibrated |
| **Panel Documents** | 84 | Expert panel outputs (MUSIC-I, CROSSCUT-I, etc.) |
| **Molecules** (T1.5 groupings) | 13 | Link to 85 templates total |
| **Theories** (T1.5) | 23 | Link to 32+ templates (many have 0) |
| **Extraction Files** (from papers) | 1,046 | Claim-level extractions from research papers |
| **Extracted Findings** | 18 | Only 18 findings from 9 papers made it through pipeline |
| **Key References** (in templates) | 578 | 326 author-year, 221 DOI, 0 PMID |
| **14-Step Integration Pipeline** | Built | `PaperIntegrationOrchestrator` — barely run |
| **Tag Engine** (3D taxonomy) | Built | Entity, theoretical, effect-size dimensions |
| **Molecule Linker** | Built | Belief → template → molecule → T1.5 hookup |

### The Three Connectivity Gaps

```
                    ┌─────────────────────────────────┐
                    │        84 PANEL DOCS             │
                    │   (expert knowledge, deep)       │
                    └──────────┬──────────────────────┘
                               │ (created via panel sprints)
                               ▼
         ┌─────────────────────────────────────────────┐
         │            208 TEMPLATES                     │
         │  ┌───────────┐     ┌────────────────────┐   │
         │  │Calibrated │     │   Uncalibrated      │   │
         │  │   103     │     │      105            │   │
         │  │mechanism  │ GAP │  causal_links       │   │
      ①  │  │params     │◄───►│  moderators         │   │
         │  │warrants   │     │  structural_pattern │   │
         │  └───────────┘     └────────────────────┘   │
         └────────┬────────────────────┬───────────────┘
                  │                    │
         ┌────────▼────────┐  ┌───────▼────────────┐
         │  13 MOLECULES   │  │   23 THEORIES      │
      ②  │  85 template    │  │  32+ template       │
         │  links          │  │  links (gaps!)      │
         └────────┬────────┘  └───────┬────────────┘
                  │                    │
         ┌────────▼────────────────────▼───────────────┐
         │            WEB OF BELIEF                     │
      ③  │  ~103 beliefs (from seed script)             │
         │  Constraints: unknown (DB sandboxed)         │
         │  Article-sourced beliefs: ~18 (barely any)   │
         └─────────────────────────────────────────────┘
                  ▲
                  │ (14-step pipeline exists, barely run)
         ┌───────┴────────────────────────────────────┐
         │   1,046 PAPER EXTRACTIONS                   │
         │   578 key references in templates           │
         │   Pipeline: built but only 18 findings done │
         └─────────────────────────────────────────────┘
```

> [!CAUTION]
> **Gap ①**: Calibrated and uncalibrated templates use completely different field schemas— effectively two parallel systems. Bridging underway.
>
> **Gap ②**: 5 of 23 theories (22%) link to 0 templates. Molecule→template links exist but aren't bidirectional in all cases.
>
> **Gap ③**: The automated article→belief pipeline has processed only 18/1,046 extractions. The vast majority of knowledge in the web comes from panel documents, not from individual paper integration.

### What Must Be Done (Beyond Annotations)

| Action | Impact | Effort |
|---|---|---|
| **Run the paper integration pipeline** on existing 1,046 extractions | Adds article-sourced beliefs to the web, dramatically increasing evidence density | High — needs testing, possibly extraction quality review |
| **Bridge template worlds** (Phase 1, script ready) | Makes all 208 templates queryable by QA features | Low — non-destructive, script built |
| **Backfill theory→template links** | 5 theories with 0 templates need constituent_templates populated | Medium |
| **Bidirectional molecule links** | Ensure templates point back to their molecules | Low |
| **Run belief seeder on all templates** (not just calibrated) | Adds ~105 more beliefs from uncalibrated templates | Low — script exists, needs flag change |
| **Reference resolution** | Match 326 author-year references to DOIs for paper linkage | Medium |
| **Quality review of 1,046 extractions** | Many extractions may be low-quality; need triage before bulk integration | High |

---

## 2. Annotation System: Current State & Proposal

### What Exists Today

| Component | What It Does | Coverage |
|---|---|---|
| `TagAssignmentEngine` | 3D taxonomy tags on beliefs: entity/topic + theoretical + effect-size | 7 entity domains, T1 framework matching |
| `MoleculeLinker` | Links beliefs → templates → molecules → T1.5 theories | 13 molecules, 23 theories |
| `key_references` in templates | Author-year and DOI citations | 578 references across 160 templates |
| `calibration_panel` / `panel_source` | Which expert panel created each template | 80% panel_source, 8% calibration_panel |
| `panel_docs` | Links back to source panel markdown files | 44% coverage |
| `bridge_warrant` | Epistemic type classification (CONSTITUTIVE, MECHANISM, etc.) | 50% (calibrated only) |
| `causal_links.edge_confidence` | Link maturity: strong/moderate/weak | 45% (uncalibrated with causal_links) |

### What's Missing: The Annotation Gap

The system currently has **no general-purpose annotation layer**. Each piece of metadata is hardcoded into specific fields. This means:

1. **No way to attach expert commentary** to a template parameter without editing the JSON
2. **No way to flag a threshold as uncertain** without changing the data
3. **No way to record that two templates interact** outside of predefined fields
4. **No way to track user feedback** on QA answers
5. **No versioning of annotations** — edits overwrite originals

### Proposed Annotation Types

We propose **10 annotation types** organized by what they attach to and what purpose they serve:

#### Layer 1: Evidence Annotations (attach to templates or beliefs)

| Type | Purpose | Example |
|---|---|---|
| `CALIBRATION_NOTE` | Expert commentary on calibration quality | "Panel felt this ceiling was too generous — see minutes 2026-02-15" |
| `SENSITIVITY_FLAG` | Marks parameters that are uncertain or vary widely | "This threshold varies 3× across studies (0.3–0.9)" |
| `EVIDENCE_OVERRIDE` | Manual upgrade/downgrade of maturity level | Reviewer upgraded from how-plausibly → how-actually after new RCT |
| `PROVENANCE_PATCH` | Backfills missing provenance (DOI, panel ref) | Added missing DOI from panel meeting transcript |

#### Layer 2: Relational Annotations (attach to pairs of entities)

| Type | Purpose | Example |
|---|---|---|
| `CROSS_REFERENCE` | Links templates that interact or share mechanisms | CLE1 and L4 have complementary but distinct mechanisms |
| `MOLECULE_LINK` | Connects template to a molecule/T1.5 pathway | Template AX1 touches pain-overlap pathway in allostatic molecule |
| `CLINICAL_CAUTION` | Safety-relevant annotation on a causal link | "Contraindicated in photosensitive epilepsy patients" |

#### Layer 3: QA/User-Facing Annotations (attach to answers or questions)

| Type | Purpose | Example |
|---|---|---|
| `OPEN_QUESTION` | Knowledge gap marker | "No studies on this effect in elderly populations" |
| `SEARCH_PROMPT` | Directed search suggestion for knowledge gap | "Search: 'circadian entrainment elderly hospital'" |
| `USER_FEEDBACK` | User-reported answer quality | Rating (1-5) + comment on specific preprocessed answer |

### Proposed Schema

```python
@dataclass
class Annotation:
    id: str                           # UUID
    type: AnnotationType              # One of the 10 types above
    target_type: str                  # 'template', 'belief', 'answer', 'causal_link', 'parameter'
    target_id: str                    # ID of the annotated entity
    content: str                      # The annotation text
    author: str                       # Human name, panel name, or 'system'
    created: datetime                 # When created
    provenance: Dict[str, Any]        # How this annotation was created
    confidence: float                 # 0.0–1.0 reliability of the annotation itself
    supersedes: Optional[str]         # ID of annotation this replaces (versioning)
    status: str                       # 'active', 'superseded', 'retracted'
    metadata: Dict[str, Any]          # Type-specific extra data
```

### How Annotations Connect to the Existing System

```
Template JSON
├── calibrated_parameters
│   └── [SENSITIVITY_FLAG annotation] → "varies 3×"
│   └── [CALIBRATION_NOTE annotation] → "panel comment"
├── causal_links
│   └── [EVIDENCE_OVERRIDE annotation] → "upgraded maturity"
│   └── [CLINICAL_CAUTION annotation] → "contraindication"
├── [CROSS_REFERENCE annotation] → links to related template
└── [MOLECULE_LINK annotation] → links to T1.5 pathway

QA Preprocessed Answer
├── response text
│   └── [OPEN_QUESTION annotation] → knowledge gap
│   └── [SEARCH_PROMPT annotation] → how to fill the gap
└── [USER_FEEDBACK annotation] → quality rating
```

### Key Design Questions for Cowork

1. **Storage**: Should annotations live in the template JSONs themselves (simpler but couples annotation to data) or in a separate annotation store (more flexible but requires joins)?

2. **Authorship**: Who can create annotations? Options:
   - System-only (automated during pipeline runs)
   - System + named human experts
   - System + experts + end users (full crowdsourcing)

3. **Lifecycle**: Should annotations be immutable (append-only with supersession) or mutable (edit-in-place)?

4. **Priority order**: Which annotation types should we implement first?
   - Our recommendation: `SENSITIVITY_FLAG` and `CALIBRATION_NOTE` first (highest information density), then `OPEN_QUESTION` and `SEARCH_PROMPT` (already partially implemented in QA-1).

5. **Molecules & T1.5s**: The `MOLECULE_LINK` annotation type could replace or supplement the current `MoleculeLinker` service. Should new molecule/T1.5 connections be:
   - Recorded as annotations (lightweight, versionable)
   - Or hardcoded into molecule JSONs (current approach, heavier but more structured)

6. **Annotation-driven preprocessing**: When we batch-preprocess answers, should annotations be baked into the cached answer (faster retrieval) or applied at query time (always fresh)?

---

## 3. Recommended Roadmap

| Priority | Action | What It Unlocks |
|---|---|---|
| 🔴 **Now** | Bridge template worlds (script ready) | All 208 templates queryable |
| 🔴 **Now** | Annotation schema (pending Cowork) | Foundation for all deepening |
| 🟠 **Next** | Run belief seeder on uncalibrated templates | ~105 more beliefs in web |
| 🟠 **Next** | Bulk paper integration (1,046 extractions) | Article-sourced evidence |
| 🟡 **Then** | Backfill theory/molecule links | Complete T1→T1.5→T2 chain |
| 🟡 **Then** | Batch preprocess answers (version-stamped) | Complete answer library |
| 🟢 **After** | Annotation-powered deepening + user feedback | Iterative quality improvement |

---

*This document should be shared with Cowork for annotation system design input.*
