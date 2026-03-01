# QA Browse System — Maintenance Guide

> **For the Overseer and Repository Maintainers**

## What This Is

The QA Browse System is a **Streamlit-based interactive knowledge base** for the CMR (Correlation-to-Mechanism Research) project. It provides:

- **Full-text search** across 186 templates, 13 molecules, 94 MASTER_DOC sections, and 812 papers
- **Domain browse** across 12 architectural-neuroscience domains (Visual, Auditory, Thermal, Spatial, Circadian, Haptic, Stress, Creative, Social, Memory, Multisensory, Olfactory)
- **Wikipedia-style topic pages** with sidebar infobox, mechanism chains, parameters, hot references, argumentation content, and related topics
- **Hot references** — clicking any DOI expands to show the paper's abstract, extracted evidence, and template links from our enriched extraction data
- **Argumentation integration** — bridge warrant analysis, ceiling violation detection, critique summaries

## File Manifest

### Package: `qa_browse/`
| File | Purpose |
|------|---------|
| `__init__.py` | Package exports (lazy), comprehensive docstring |
| `config.py` | All constants: domain colors, bridge warrants, paths, template→domain map |
| `topic_index.py` | Data layer: loads templates/molecules/MASTER_DOC/papers into searchable index |

### Streamlit Pages: `streamlit_app/pages/`
| File | Purpose |
|------|---------|
| `9_knowledge_base.py` | Home page: search bar, domain grid, molecule browse, featured topics |
| `10_topic.py` | Topic page: template/molecule/section article view |

### Compatibility: `streamlit_app/`
| File | Purpose |
|------|---------|
| `topic_index.py` | Thin shim re-exporting from `qa_browse` package |

## Data Sources (Read-Only)

The system reads from these directories — **it never writes to them**:

| Directory | Content | Count |
|-----------|---------|-------|
| `data/templates/*.json` | Mechanistic template definitions | 186 |
| `data/molecules/*.json` | Molecule groupings | 13 |
| `data/qa_cache/*_QA.json` | Progressive disclosure L1/L2/L3 caches | 3 |
| `data/attributes/AD_*.json` | Domain attribute definitions | 5 |
| `data/extractions/10.*.json` | Per-paper extraction + CrossRef metadata | 812 |
| `data/extractions/citation_graph.json` | Citation network | 1,735 edges |
| `MASTER_DOC_CMR_2026-02-25.md` | Authoritative prose (in REPOS/ or docs/) | 8,662 lines |

## How to Keep It Current

### When templates or molecules change
**Nothing to do.** The `TopicIndex` reloads from disk on each Streamlit restart. Just restart the app.

### When a new domain is added
1. Add entry to `DOMAIN_CONFIG` in `qa_browse/config.py`
2. Add template ID prefixes to `TEMPLATE_DOMAIN_MAP` in `qa_browse/config.py`
3. Add description to `DOMAIN_DESCRIPTIONS` in `qa_browse/config.py`

### When the MASTER_DOC is updated
Ensure the file is at one of:
- `<repo>/docs/MASTER_DOC_CMR_2026-02-25.md`
- `<repo>/../MASTER_DOC_CMR_2026-02-25.md`

If the filename changes, update `MASTER_DOC_CANDIDATES` in `config.py`.

### When new QA caches are generated
Place them in `data/qa_cache/` with naming convention `{MOLECULE_ID}_QA.json`. They'll be automatically discovered.

## How to Run

```bash
# From project root
cd Article_Eater_PostQuinean_v1
streamlit run streamlit_app/main.py

# Or directly:
streamlit run streamlit_app/pages/9_knowledge_base.py
```

## Integration Checklist (for Coworker)

- [ ] Verify `qa_browse/` package imports correctly from project root
- [ ] Verify Streamlit pages load: navigate to Knowledge Base page
- [ ] Test search: try "biophilia", "prediction error", "thermal"
- [ ] Test topic page: click any template → verify infobox, mechanism chain, references
- [ ] Wire Knowledge Base link into existing main navigation (`streamlit_app/main.py`)
- [ ] Add `qa_browse` to any package registry or dependency list if needed
- [ ] Run existing test suite to confirm no regressions

## Domain Distribution (as of Feb 25, 2026)

| Domain | Templates | Avg Confidence |
|--------|-----------|----------------|
| 🫁 Stress & Allostasis | 50 | — |
| 👂 Auditory | 32 | — |
| 🔗 Multisensory | 17 | — |
| 🏗️ Spatial | 14 | — |
| 🧠 Memory & Learning | 11 | — |
| 🌡️ Thermal | 9 | — |
| 👁️ Visual | 9 | — |
| 💡 Creativity | 8 | — |
| 🤲 Haptic & Material | 6 | — |
| 👥 Social | 5 | — |
| 🌙 Circadian | 3 | — |
| 👃 Olfactory | 2 | — |
| **Total classified** | **166 / 186** (89%) | — |
| **Average per domain** | **13.8** | — |
