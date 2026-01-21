# Ruthless System Review: Article Eater Post-Quinean V21

**Date**: January 22, 2026
**Review Type**: Comprehensive Architecture & Governance Audit
**Status**: Pre-production validation

---

## Expert Panel (Expanded)

### Core Methodological Panel
1. **Dr. Judea Pearl** — Causality, Bayesian networks, do-calculus
2. **Dr. Nancy Cartwright** — Philosophy of science, evidence portability, bridge warrants
3. **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
4. **Dr. Marcia Bates** — Information science, search behavior, knowledge organization
5. **Dr. Rachel Kaplan** — Environmental psychology (domain expert for neuroarchitecture)

### Added Technical & Governance Experts
6. **Dr. Leslie Lamport** — Distributed systems, formal methods, specification
7. **Dr. Barbara Liskov** — Software design, abstraction, type systems
8. **Dr. Fred Brooks** — System architecture, software engineering management
9. **Dr. David Parnas** — Module design, information hiding, documentation
10. **Dr. Peter Naur** — Programming as theory building, tacit knowledge

---

## System Overview

Article Eater V21.0.0 (Post-Quinean) is a knowledge extraction and coherentist epistemology system for neuroarchitecture research. It extracts evidence from scientific articles and maintains a Quinean "Web of Belief" where:

- All beliefs are revisable (no foundations)
- Justification comes from coherence, not accumulation
- Conflicts trigger web-wide revision, not simple override
- The Bayesian Network is derivative of the web, not primary

### Architecture Layers

```
EXTRACTION LAYER (Track A)
├── Pipeline: app/tasks/pipeline.py
├── CLI: app/cli/article_eater_contract_cli.py
└── Schemas: contracts/ae_af/schemas/

EPISTEMIC LAYER (Track B - Quinean Engine)
├── Core: src/services/web_of_belief.py (1500+ lines)
├── Mapper: src/services/extraction_to_web.py
├── Bridges: src/services/bridge_warrants.py
├── Taxonomy: src/services/outcome_taxonomy.py
├── Persistence: src/services/web_persistence.py
└── Causal: src/services/causal_classifier.py

QUERY LAYER (Tier 1)
├── Parser: src/services/query_parser.py
├── Response: src/services/query_response.py
├── Reporting: src/services/reporting.py
├── Stability: src/services/stability_engine.py
└── Stopping: src/services/stopping_rules.py

API LAYER
├── app/routes/query.py
├── app/routes/reports.py
├── app/routes/ingestion.py
└── app/routes/web_of_belief.py

FRONTEND
├── frontend/evidence-explorer.html
└── frontend/ingestion.html
```

---

## Review Questions by Expert

### For Pearl (Causality & Inference)

1. **Causal Classification Tier Logic**: The three-tier system (CAUSAL/SUGGESTIVE/ASSOCIATIONAL) now uses design-first logic where experimental design takes precedence. Causal language alone without mechanism or confounder control yields SUGGESTIVE. Is this epistemically correct?

2. **Quasi-Experimental Handling**: Natural experiments, diff-in-diff, propensity score matching are treated as "between experimental and observational." Should they ever yield CAUSAL tier?

3. **Confounder Gap Detection**: We flag causal claims without confounder acknowledgment with severity levels (CRITICAL for abstract-only, WARNING for full-text). Is this appropriate?

4. **Directional Opposition**: Contested evidence now uses directional opposition (X increases Y vs X decreases Y) rather than credence threshold. Is this the right model for scientific disagreement?

### For Cartwright (Evidence Portability)

1. **Bridge Warrants**: Four types implemented (mechanism, functional, analogical, constitutive) with default P(bridge) values. Are these types sufficient for neuroarchitecture evidence transfer?

2. **Scope Conditions**: Follow-up queries now ask "Under what conditions does X affect Y?" Is this adequate for evidence portability assessment?

3. **Measurement Method Differences**: Disagreement detection now identifies self-report vs physiological measure differences. What other measurement distinctions matter for this domain?

4. **Evidence Quality Asymmetry**: We distinguish "genuine scientific disagreement" from "evidence quality asymmetry." Is this distinction maintainable in practice?

### For Simon (Bounded Rationality)

1. **Three-Tier vs Four-Tier**: Pearl suggested CAUSAL-INSUFFICIENT as a fourth tier. We kept three tiers per your advice but added warnings. Is this satisficing appropriately?

2. **Follow-Up Structure**: Exactly 3 follow-ups (deeper, scope, uncertainty). Is this cognitively appropriate for researcher decision-making?

3. **Confidence Levels**: High/Medium/Low/Unknown. Should there be more granularity or is this sufficient?

4. **Stopping Rules**: The stopping rules engine uses multiple criteria. Are these satisficing-compatible?

### For Bates (Information Science)

1. **Vocabulary Bridge**: Search terms are expanded via vocabulary lookup. Is this transparent enough to users?

2. **Evidence Item Display**: Top 10 evidence items shown with credence, source depth, causal flags. Is this appropriate information scent?

3. **Contested Evidence Section**: Shows supporting vs contradicting grouped with reasons for disagreement. Does this support effective browsing?

4. **Follow-Up Query URLs**: Follow-ups are now clickable with pre-filled parameters. Is this good search behavior support?

### For Kaplan (Domain Expert)

1. **Neuroarchitecture Patterns**: Added domain-specific patterns (design intervention, restorative effect, biophilic response, preference for). Are these the right terms?

2. **Outcome Taxonomy**: Fallback includes affect.stress, physio.stress, cog.attention, etc. What's missing?

3. **Domain Confounders**: Added socioeconomic, self-selection, climate, building age. What else matters for this field?

4. **ART/Prospect-Refuge**: Should the system explicitly detect Attention Restoration Theory or Prospect-Refuge Theory terminology?

### For Lamport (Formal Methods)

1. **State Consistency**: The web of belief can be mutated during queries. Is there a consistency model?

2. **Specification**: Are the schemas in `contracts/ae_af/schemas/` sufficiently precise?

3. **Invariants**: What invariants should the web of belief maintain? Are they documented and enforced?

### For Liskov (Software Design)

1. **Abstraction Boundaries**: Are the service boundaries (query_parser → query_response → web_of_belief) clean?

2. **Substitutability**: Can components be replaced without affecting others?

3. **Type Safety**: Type hints are used throughout. Is the type discipline sufficient?

### For Brooks (Architecture)

1. **Conceptual Integrity**: Does the system have a coherent conceptual model?

2. **Essential vs Accidental Complexity**: Where is complexity warranted vs accidental?

3. **Second System Effect**: Is there over-engineering anywhere?

### For Parnas (Module Design)

1. **Information Hiding**: Do modules expose only what's necessary?

2. **Secret Ownership**: Is each design decision localized to one module?

3. **Documentation**: Is the CLAUDE.md adequate for onboarding?

### For Naur (Theory Building)

1. **Tacit Knowledge**: What knowledge is embedded in the code but not documented?

2. **Theory Preservation**: If the original developers leave, can the theory be reconstructed from artifacts?

---

## User Types & Use Cases

### User Type 1: CNFA Researcher
**Primary Use Cases**:
- Query the evidence base about environmental effects on cognition
- Understand confidence levels and sources of uncertainty
- Identify gaps in current knowledge
- Export evidence for BN construction

**Questions**:
- Can they trust the causal classifications?
- Are the follow-up suggestions useful for research planning?
- Is the contested evidence display helpful for literature review?

### User Type 2: Graduate Student
**Primary Use Cases**:
- Learn about neuroarchitecture evidence
- Understand which claims are well-supported
- Find primary sources for coursework

**Questions**:
- Is the interface learnable?
- Are confidence explanations understandable?
- Can they distinguish strong from weak evidence?

### User Type 3: System Administrator
**Primary Use Cases**:
- Ingest new papers into the system
- Monitor web of belief health
- Generate reports for faculty

**Questions**:
- Is the ingestion workflow clear?
- Are error messages actionable?
- Can they diagnose issues from logs?

### User Type 4: Domain Expert (External Reviewer)
**Primary Use Cases**:
- Validate evidence classifications
- Review for domain accuracy
- Suggest taxonomy improvements

**Questions**:
- Can they audit classifications?
- Is provenance traceable?
- Can they suggest corrections?

---

## Critical Questions

1. **Is the Quinean commitment actually implemented?** Or are we just doing Bayesian updating with extra steps?

2. **Are stubs (findings that don't fit current ontology) handled correctly?** They should be held, not forced or dropped.

3. **What happens when the web becomes inconsistent?** Is there a recovery mechanism?

4. **Is the test coverage adequate?** 238+ tests pass, but what's not tested?

5. **What security concerns exist?** Input validation, injection risks, etc.

6. **What's the disaster recovery plan?** Web snapshots exist, but is restoration tested?

7. **Is the governance model enforceable?** CLAUDE.md documents rules, but are they checkable?

---

## Deliverables Requested

For each expert, provide:
1. **Assessment** (APPROVE / MODIFY / REJECT)
2. **Priority** (CRITICAL / HIGH / MEDIUM / LOW)
3. **Specific concerns** (with file:line references if applicable)
4. **Recommended actions**

---

## Current Test Status

```
Tests: 238+ passing
Files:
- test_causal_classifier.py: 49 tests
- test_reporting.py: 44 tests
- test_query_response.py: 33 tests
- test_query_routes.py: 25 tests
- test_query_parser.py: 30+ tests
- test_stability_engine.py: 30+ tests
- test_stopping_rules.py: 20+ tests
```

---

## Files for Review

### Priority 1 - Core Engine
- `src/services/web_of_belief.py` (1500+ lines - THE key file)
- `src/services/causal_classifier.py` (580 lines - E1.D5 restructured)
- `src/services/query_response.py` (755 lines - E1.D2 directional opposition)

### Priority 2 - Supporting Services
- `src/services/reporting.py` (862 lines - E1.D4 confounder gap)
- `src/services/query_parser.py` (503 lines)
- `src/services/bridge_warrants.py` (1000+ lines)

### Priority 3 - API & Integration
- `app/routes/query.py`
- `app/routes/reports.py`
- `app/tasks/pipeline.py`

### Priority 4 - Schemas & Governance
- `contracts/ae_af/schemas/*.json`
- `CLAUDE.md`
- `Project_Constitution.md`
