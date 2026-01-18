# ARTICLE EATER: SYSTEM VISION & STATE
## Living Document - Updated Each Version

**Current Version**: v15.8.1 → v16.0 (in progress)  
**Last Updated**: 2025-11-08  
**Author**: David (Professor, UCSD Cognitive Science)  
**Document Purpose**: Human-readable summary of what the system IS, WHERE it's going, and WHY it matters

---

## WHAT IS ARTICLE EATER?

### The Vision (Why This Exists)

Article Eater is an **Epistemological Engine** for evidence synthesis in **Cognitive Neuroscience for Architecture (CNfA)** - the study of how built environments affect human cognition, affect, and behavior.

**The Problem It Solves**:

Traditional literature reviews are **narrative summaries** - a researcher reads 50 papers and writes "Plants reduce stress." But this loses critical detail:

- **WHAT reduced stress?** (Cortisol? Heart rate? Self-report?)
- **HOW MUCH?** (Effect size? Statistical significance?)
- **WHY?** (What's the mechanism? Biophilia? Attention restoration?)
- **EVIDENCE QUALITY?** (N=10 or N=1000? Controlled experiment or survey?)

Article Eater transforms narrative reviews into **structured, queryable knowledge graphs** where every claim is backed by:
- Operational measures (cortisol ↓, heart rate ↓, STAI score ↓)
- Statistical evidence (p-values, effect sizes, sample sizes)
- Proposed mechanisms (Predictive Processing, Embodied Cognition, Allostasis)
- Full provenance (which papers, which experiments, which conditions)

**The Ultimate Goal**:

Enable architects and designers to answer questions like:
- "Show me ALL evidence that curved walls reduce anxiety"
- "What mechanisms explain biophilic design effects?"
- "Which architectural features have the strongest evidence for improving focus?"
- "Where are the gaps in the literature?"

And to export this knowledge as:
- Hierarchical rule sets (micro → meso → macro)
- Bayesian networks (for probabilistic reasoning)
- Meta-review publications (with full statistical rigor)

---

## HOW IT WORKS (High-Level Architecture)

### The 7-Panel Review (Core Artifact)

Article Eater processes academic papers through a structured **7-Panel Analysis**:

1. **Citation Information**: APA format, DOI, citation count, seminal status
2. **Research Focus**: Question, hypothesis, study type
3. **Study Context**: Setting, building type, stimulus details (for replication)
4. **Methodology**: Conditions, procedure, N, demographics, devices used
5. **Findings**: **CRITICAL** - Extracts EVERY operational measure separately with full statistics
6. **Discussion & Mechanisms**: Theoretical frameworks, proposed "why", evidence strength
7. **Key References**: Top 3-5 foundational citations from paper

**Example**:

```
Paper: "Curved Walls Reduce Anxiety in Office Environments"

Panel 5 (Findings) extracts:
├─ Operational Finding 1: salivary_cortisol ↓ (p=0.03, d=0.52, N=68)
├─ Operational Finding 2: state_anxiety_inventory ↓ (p=0.01, d=0.64, N=68)
└─ Operational Finding 3: heart_rate ↓ (p=0.08, d=0.31, N=68)

Panel 6 (Mechanisms) extracts:
├─ Mechanism: Predictive Processing Fluency
│   Framework: Free Energy Principle (Friston, 2010)
│   Evidence: Moderate (fMRI shows reduced FFA activation)
└─ Mechanism: Evolutionary Preference for Natural Forms
    Framework: Biophilia Hypothesis (Wilson, 1984)
    Evidence: Speculative (amygdala response to angular shapes)
```

### The Hierarchical Rule Structure (v16.0 Innovation)

**Three Levels of Abstraction**:

**MICRO-RULES**: Individual operational measures from single studies
```
"Curved walls → cortisol ↓" (p<.05, d=0.52, N=68, Paper A)
"Curved walls → STAI ↓" (p<.01, d=0.64, N=68, Paper A)
"Curved walls → HR ↓" (p<.08, d=0.31, N=68, Paper A)
```

**MESO-RULES**: Aggregated constructs from multiple micro-rules
```
"Curved walls → stress reduction"
├─ Triangulation: 3 operational measures (cortisol, STAI, HR)
├─ Sample: N=68 total
├─ Confidence: 0.82 (triangulation=0.30, effect=0.28, sample=0.14, consistency=0.10)
└─ Mechanism: Predictive Processing Fluency
```

**MACRO-RULES**: Theoretical principles (future - not yet implemented)
```
"Biophilic design → improved wellbeing"
├─ Multiple pathways: stress ↓, attention ↑, mood ↑
├─ Framework: Biophilia Hypothesis + Attention Restoration Theory
└─ Evidence: 15 meso-rules, 60+ micro-rules, N=2000+ aggregate
```

### The Two-Mode Interface (Planned)

**Librarian Mode**: Paper inventory and scouting
- View all papers ingested
- Search/filter by topic, year, author
- Scout for new papers (HITL enrichment)
- Triage: Keep, discard, or deep-review

**Synthesizer Mode**: Knowledge graph building
- Review 7-panel extractions
- Approve/edit micro-rules
- Trigger meta-aggregation (micro → meso)
- Link to external corpus (foundational science)
- Export rules, networks, reports

---

## WHERE WE ARE NOW (v15.8.1 → v16.0)

### v15.8.1 State (Current Production)

**What Works**:
- ✅ Paper ingestion (DOI, PDF upload, arXiv)
- ✅ 7-Panel extraction (via Anthropic Claude API)
- ✅ Evidence collection (passages with context)
- ✅ Flat rule synthesis (consequent → antecedents, confidence)
- ✅ JSON-based storage (findings/job_id/rules.json)
- ✅ Basic web UI (jobs list, shortlist, rules view, evidence view)
- ✅ RAG integration (vector search for evidence retrieval)

**What's Missing** (Critical Gaps):
- ❌ No hierarchical rules (everything is flat, duplicate micro-rules)
- ❌ No operational measure tracking (cortisol + HR treated as "stress")
- ❌ No mechanism extraction (only correlations, no "why")
- ❌ No meta-aggregation (can't synthesize across studies)
- ❌ No paper-to-rules reverse lookup (can't validate provenance)
- ❌ No tree visualization (can't see hierarchy)
- ❌ Poor UI navigation (fragmented, unclear workflow)

**The Result**: 
System works for **single-paper analysis** but fails for **multi-paper synthesis**. Can't answer "Show me ALL evidence for X" or "What's the triangulation across measures?"

### v16.0 Target (In Progress)

**Phase 1 Goals** (Current Work):

1. **Database Enhancement** ✅ (Code ready, not deployed)
   - Add rule_level (micro/meso/macro)
   - Add parent_rule_id (foreign key for hierarchy)
   - Add operational_measure, measure_type, measure_direction
   - Add mechanism, mechanism_description, theoretical_framework
   - Add statistical fields (p_value, effect_size, sample_size, CI)
   - Add confidence decomposition (triangulation, effect, sample, consistency)

2. **Enhanced Extraction** ✅ (Prompt written, not deployed)
   - 7-Panel prompt v16 extracts EVERY operational measure separately
   - Panel 5 returns array of operational_findings (not aggregated)
   - Panel 6 extracts mechanisms with theoretical frameworks
   - Full statistical details required (p, d, N, CI, descriptives)

3. **Meta-Review Aggregation** ✅ (Code ready, not deployed)
   - meta_review.py module aggregates micro → meso
   - Infers construct from operational measures (STRESS_MEASURES, ATTENTION_MEASURES)
   - Calculates decomposed confidence
   - Creates parent-child relationships

4. **Hierarchical UI** ✅ (Templates ready, not deployed)
   - Tree view (expand/collapse nodes)
   - Flat list (search/sort/filter)
   - Network view (placeholder for v17.0)
   - Paper-to-rules analysis (reverse lookup)
   - Toggle between views

**Phase 1 Deliverables** (Completed, Not Deployed):
- ✅ SQL migrations (2 files)
- ✅ Enhanced 7-panel prompt
- ✅ meta_review.py (600 lines)
- ✅ routes_papers.py (300 lines)
- ✅ routes_rules.py enhanced (200 lines)
- ✅ 5 HTML templates (1,100 lines)
- ✅ hierarchy.css (800 lines)
- ✅ hierarchy.js (300 lines)
- ✅ Complete deployment guide
- ✅ 150,000 words of documentation

**Deployment Status**: 
Code is **production-ready** but **not yet deployed**. Waiting for:
- Final review of database schema
- Test with 5+ papers on similar topic
- User acceptance of UI design
- 20-24 hours for full implementation

### Future Roadmap (Post-v16.0)

**v16.1** (Month 2):
- Macro-rule synthesis (meso → macro aggregation)
- Mechanism validation (check citations exist)
- Improved construct taxonomy
- Bayesian network export (basic)

**v17.0** (Month 3-4):
- D3.js network visualization (mechanism links)
- Cross-job meta-analysis (aggregate across jobs)
- Contradiction detection (conflicting rules)
- Temporal analysis (how evidence evolved 2010→2025)

**v18.0** (Month 5-6):
- Collaborative rule refinement (multi-user)
- AI-assisted mechanism discovery
- Zotero/Mendeley integration
- Publication-ready export formats

---

## WHY THIS MATTERS (Academic Context)

### The CNfA Research Gap

Cognitive Neuroscience for Architecture is a young field (~15 years old) with a fragmentation problem:

**Current State**:
- Papers scattered across: Architecture, Psychology, Neuroscience, HCI, Environmental Psychology
- Same effects studied with different operational measures (can't compare)
- Mechanisms proposed but rarely validated
- Meta-reviews are rare and narrative (not structured)
- Designers can't access findings (too technical, too scattered)

**What Article Eater Enables**:
- **Triangulation**: See if cortisol ↓, HR ↓, and subjective stress ↓ ALL agree
- **Mechanism Discovery**: Identify which theories (Biophilia vs. Attention Restoration) have better evidence
- **Gap Analysis**: Find understudied areas (e.g., "No studies on curved walls in schools")
- **Designer Translation**: Export simple rules ("Use curves in high-stress spaces")
- **Meta-Review Publication**: Generate rigorous, structured literature reviews

### The Theoretical Foundations

Article Eater is grounded in three academic traditions:

**1. Evidence-Based Design (EBD)**
- Hamilton & Watkins (2009): Systematic approach to incorporating research into design
- Article Eater makes EBD queryable and updatable

**2. Knowledge Synthesis Methods**
- Cooper et al. (2019): "Research Synthesis and Meta-Analysis" - structured extraction
- Article Eater implements systematic extraction at scale

**3. Computational Cognitive Science**
- Anderson & Lebiere (1998): ACT-R cognitive architecture
- Article Eater models architectural effects as cognitive mechanisms

### The Unique Contribution

**Existing Tools**:
- **Zotero/Mendeley**: Manage papers, but no extraction
- **Covidence/DistillerSR**: Systematic reviews, but no hierarchy
- **Neo4j/GraphDB**: Knowledge graphs, but no CNfA-specific structure

**Article Eater**:
- **Domain-Specific**: Built for CNfA (operational measures, mechanisms, set-of-support)
- **Hierarchical**: Micro/meso/macro abstraction levels
- **HITL**: Human-in-the-loop for quality control
- **Exportable**: Rules, networks, reports

---

## KEY DESIGN PRINCIPLES

### 1. Theoretical Parsimony with Empirical Rigor

**Principle**: Higher-level frameworks (Predictive Processing, Embodied Cognition) unify explanations, but system must still track specific, operational constructs with empirical evidence.

**Implementation**: 
- Micro-rules: Specific operational measures (cortisol, HR, STAI)
- Meso-rules: Aggregated constructs (stress, anxiety, attention)
- Macro-rules: Theoretical principles (Biophilia → wellbeing)

### 2. Provenance Tracking

**Principle**: Every claim must be traceable to original papers, experiments, and statistical tests.

**Implementation**:
- Rules link to Evidence items
- Evidence items link to Papers
- Papers link to DOIs
- Statistical support required (p, d, N, method)

### 3. Triangulation-Based Confidence

**Principle**: Confidence in a construct increases with diversity of operational measures showing consistent effects.

**Implementation**:
- More measures (cortisol + HR + BP + HRV) = higher triangulation score
- Larger effect sizes = higher effect strength score
- Larger sample sizes = higher sample score
- Consistent directions = higher consistency score
- Total confidence = weighted sum

### 4. Human-in-the-Loop Quality

**Principle**: AI assists extraction, but humans verify quality, approve rules, and make decisions.

**Implementation**:
- AI extracts 7-panel reviews
- Human reviews and edits
- AI proposes aggregations
- Human approves or rejects
- Final rules are human-approved

### 5. Graceful Degradation

**Principle**: System should work even when some information is missing or incomplete.

**Implementation**:
- Rules without mechanisms still valid (just lower confidence)
- Single operational measure = valid micro-rule (just no triangulation)
- Missing statistical details = warnings, not errors
- Flat rules coexist with hierarchical rules

---

## TECHNICAL STACK

### Current (v15.8.1)

**Backend**:
- Python 3.11
- Flask (web framework)
- SQLAlchemy (ORM, but minimal use - mostly JSON)
- Celery (async task processing)
- PyPDF2 (PDF parsing)
- Anthropic API (Claude Sonnet 4 for extraction)

**Frontend**:
- HTML/Jinja2 templates
- Vanilla CSS (no frameworks)
- Vanilla JavaScript (no frameworks)
- Some jQuery (legacy, being removed)

**Data Storage**:
- SQLite (database for papers, jobs, users)
- JSON files (findings/job_id/*.json for rules, evidence)
- Local filesystem (uploaded PDFs)

**Infrastructure**:
- Development: Local (no deployment yet)
- Git: Not yet committed (vibe coding with AI)
- CI/CD: Not yet configured

### Target (v16.0)

**Backend Changes**:
- ✅ Enhanced SQLAlchemy models (hierarchical rules)
- ✅ New module: meta_review.py (aggregation logic)
- ✅ New routes: routes_papers.py (paper analysis)
- ✅ Enhanced routes: routes_rules.py (hierarchy support)

**Frontend Changes**:
- ✅ New templates: rules_view_hierarchical.html, rules_tree.html
- ✅ New CSS: hierarchy.css (800 lines)
- ✅ New JS: hierarchy.js (interactive tree)

**Data Storage Changes**:
- ✅ Enhanced SQLite schema (15+ new columns)
- ✅ Hybrid: JSON for flat rules, DB for hierarchical rules
- ✅ Migration path: Flat JSON → Hierarchical DB

**Infrastructure**:
- Still local development
- Governance: v2.0 with Conversation Ledger
- Git: Planning to commit after v16.0 stable

---

## GOVERNANCE APPROACH

### Pre-Git Phase (Current)

**Challenge**: Vibe coding with AI creates "Intent Rot" - lose track of why code exists

**Solution**: Conversation Ledger (governance/CONVERSATION_LEDGER.yml)
- Tracks sessions (what you asked, what AI did)
- Tracks decisions (what you chose, why)
- Tracks context (user profile, project facts)
- Tracks artifacts (what got created, provenance)

**Maintenance**: Update ledger after each work session with AI

### Post-Git Phase (Future)

**Upgrade Path**:
- Conversation Ledger → Architecture Decision Records (ADRs)
- Sessions → Git commit messages with session IDs
- Decisions → docs/adr/*.md files
- Artifacts → Git history

**CI/CD**:
- Drift Shield workflow (from governance kit v1.5)
- 13 guards (manifest, deprecations, contracts, etc.)
- + 1 new guard (conversation_guard.py)

---

## KNOWN LIMITATIONS & FUTURE WORK

### Current Limitations (v15.8.1)

1. **Flat Rules Only**: Can't represent hierarchies
2. **Operational Measures Lost**: Aggregated too early
3. **No Mechanisms**: Only "what" not "why"
4. **No Meta-Analysis**: Can't synthesize across papers
5. **Poor Provenance**: Can't trace rules back to papers easily
6. **UI Fragmentation**: Navigation unclear, workflow hidden

### Limitations After v16.0

1. **No Macro-Rules**: Meso → macro aggregation not implemented
2. **No Cross-Job Analysis**: Rules isolated per job
3. **No Network Viz**: Tree view only, not full graph
4. **Manual Aggregation**: User must trigger meta-review
5. **No Bayesian Export**: Placeholder only
6. **Single-User**: No collaboration features

### Known Issues (To Fix)

1. **7-Panel Prompt**: Sometimes misses operational measures in complex tables
2. **Construct Inference**: CONSTRUCT_MAP incomplete (missing some measures)
3. **Confidence Tuning**: Weights may need adjustment based on real data
4. **UI Performance**: Tree view slow with 100+ rules
5. **Mobile**: Not yet responsive (desktop only)

### Future Research Questions

1. **Optimal Aggregation**: When should micro-rules aggregate? (Always? Threshold?)
2. **Mechanism Validation**: How to programmatically check if mechanism citations valid?
3. **Contradiction Detection**: How to handle conflicting findings? (Paper A: effect, Paper B: no effect)
4. **Temporal Weighting**: Should older studies have lower confidence?
5. **Quality Assessment**: How to incorporate study quality (blinding, randomization, etc.)?

---

## REFERENCES (Key Papers That Shaped This System)

**Cognitive Neuroscience for Architecture**:
- Eberhard, J. P. (2009). *Brain Landscape: The Coexistence of Neuroscience and Architecture*. Oxford.
- Mallgrave, H. F. (2013). *Architecture and Embodiment*. Routledge.
- Robinson, S., & Pallasmaa, J. (2015). *Mind in Architecture*. MIT Press.

**Evidence-Based Design**:
- Hamilton, D. K., & Watkins, D. H. (2009). *Evidence-Based Design for Multiple Building Types*. Wiley.
- Ulrich, R. S., et al. (2008). A review of the research literature on evidence-based healthcare design. *HERD*, 1(3), 61-125.

**Meta-Analysis & Synthesis**:
- Cooper, H., Hedges, L. V., & Valentine, J. C. (2019). *The Handbook of Research Synthesis and Meta-Analysis*. Russell Sage.
- Borenstein, M., et al. (2009). *Introduction to Meta-Analysis*. Wiley.

**Theoretical Frameworks**:
- Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.
- Barsalou, L. W. (2008). Grounded cognition. *Annual Review of Psychology*, 59, 617-645.
- Wilson, E. O. (1984). *Biophilia*. Harvard University Press.
- Kaplan, S. (1995). The restorative benefits of nature. *Journal of Environmental Psychology*, 15(3), 169-182.

**Knowledge Graphs & Provenance**:
- Freire, J., et al. (2008). Provenance for computational tasks: A survey. *Computing in Science & Engineering*, 10(3), 11-21.
- Hogan, A., et al. (2021). Knowledge graphs. *ACM Computing Surveys*, 54(4), 1-37.

---

## VERSION HISTORY

### v15.8.1 (Current Production)
**Date**: 2025-11-08 (pre-governance, no Git)  
**Status**: Working but incomplete  
**Key Features**: 7-panel extraction, flat rules, JSON storage, basic UI  
**Major Gaps**: No hierarchy, no mechanisms, no meta-aggregation

### v16.0 (In Progress)
**Target Date**: 2025-11-15  
**Status**: Code ready, not deployed  
**Key Features**: Hierarchical rules, operational measures, mechanisms, meta-aggregation, tree UI  
**Implementation Time**: 20-24 hours estimated

### v16.1 (Planned)
**Target Date**: 2025-12-15  
**Key Features**: Macro-rules, mechanism validation, Bayesian export (basic)

### v17.0 (Planned)
**Target Date**: 2026-01-31  
**Key Features**: Network visualization, cross-job analysis, contradiction detection

### v18.0 (Vision)
**Target Date**: 2026-03-31  
**Key Features**: Multi-user, collaborative refinement, publication export

---

## MAINTAINER NOTES

**Primary Developer**: David (Human) + Claude/AI (Code Generation)  
**Development Model**: "Vibe Coding" - human steers, AI implements  
**Memory Strategy**: Conversation Ledger (no persistent AI memory)  
**Deployment**: Local only (not production yet)  
**Repository**: Not yet in Git (planning to commit after v16.0)

**For Future Maintainers**:

1. **Read This First**: This document is the "truth" about what the system IS and WHY
2. **Then Read**: CONVERSATION_LEDGER.yml for detailed session history
3. **Then Read**: Phase 1 implementation docs for v16.0 technical details
4. **Context**: User is professor at UCSD, 35 years experience, building research tool
5. **Domain**: CNfA = Cognitive Neuroscience for Architecture (not mainstream CS)
6. **Standards**: Academic rigor required (APA citations, statistical reporting, provenance)

**When Updating This Document**:
- Keep version history complete (don't delete old entries)
- Update "Current Version" and "Last Updated" at top
- Add new sections as system evolves
- Preserve "Why This Matters" - future devs need context
- Link to CONVERSATION_LEDGER.yml for detailed provenance

---

**Document Version**: 1.0  
**Created**: 2025-11-08  
**Purpose**: Living summary of Article Eater system state  
**Audience**: Future developers, collaborators, and 6-months-from-now David  
**Companion Docs**: CONVERSATION_LEDGER.yml (detailed), Phase 1 packages (code)