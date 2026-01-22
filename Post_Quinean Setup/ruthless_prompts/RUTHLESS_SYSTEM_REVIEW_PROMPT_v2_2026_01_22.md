# Ruthless System Review v2: Article Eater Post-Quinean V21

**Date**: January 22, 2026
**Review Type**: Comprehensive Architecture, ML/AI Scalability & Governance Audit
**Status**: Post-panel-validation review
**Version**: 2.0 (Expanded with AI/CS perspectives)

---

## Expert Panel (Expanded with Modern AI/CS Leaders)

### Core Methodological Panel (Original)
1. **Dr. Judea Pearl** — Causality, Bayesian networks, do-calculus
2. **Dr. Nancy Cartwright** — Philosophy of science, evidence portability, bridge warrants
3. **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
4. **Dr. Marcia Bates** — Information science, search behavior, knowledge organization
5. **Dr. Rachel Kaplan** — Environmental psychology (domain expert for neuroarchitecture)

### Technical & Governance Experts (Added Sprint E)
6. **Dr. Leslie Lamport** — Distributed systems, formal methods, specification
7. **Dr. Barbara Liskov** — Software design, abstraction, type systems
8. **Dr. Fred Brooks** — System architecture, software engineering management
9. **Dr. David Parnas** — Module design, information hiding, documentation
10. **Dr. Peter Naur** — Programming as theory building, tacit knowledge

### Modern AI/CS Leaders (New for v2)
11. **Dr. Andrew Ng** — ML systems, MLOps, deployment at scale, data-centric AI
12. **Dr. Andrej Karpathy** — Deep learning systems, practical ML engineering, LLM applications
13. **Dr. Ilya Sutskever** — Neural network scaling, emergent capabilities, AI safety
14. **Dr. Yann LeCun** — Self-supervised learning, world models, AI architecture
15. **Dr. Peter Norvig** — AI systems at scale, probabilistic programming, search
16. **Dr. Jeff Dean** — Large-scale systems, infrastructure, ML tooling

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

1. **Causal Classification Tier Logic**: Design-first logic where experimental design takes precedence. Is this epistemically correct?

2. **Directional Opposition**: Contested evidence uses directional opposition (X increases Y vs X decreases Y) rather than credence threshold. Validated in panel review. Any remaining concerns?

3. **Confounder Gap Detection**: Severity levels (CRITICAL for abstract-only, WARNING for full-text) with expanded keywords (IPW, doubly robust, g-computation). Adequate?

### For Cartwright (Evidence Portability)

1. **Bridge Warrants**: Five types now (mechanism, functional, analogical, constitutive, CAPACITY). CAPACITY reduced to P(bridge)=0.45 per your recommendation. Keywords tightened. Adequate?

2. **Measurement Modalities**: Expanded to 6 categories (self-report, behavioral, physiological, environmental, observational, archival). Missing anything?

3. **Evidence Quality Asymmetry**: Detection of measurement method disagreement reasons. Sufficient coverage?

### For Simon (Bounded Rationality)

1. **Three-Tier + Warnings**: Maintained per your advice. Still appropriate?

2. **Credence Presets**: Added High (>70%), Medium (40-70%), Low (<40%) quick filters. Good satisficing design?

3. **Cognitive Load**: 7+ filter facets now. Too many options?

### For Bates (Information Science)

1. **Vocabulary Tooltips**: Expanded terms now show "why expanded" on hover. Sufficient transparency?

2. **Faceted Filtering**: Added year range, study type, theoretical framework filters. Good facet selection?

3. **Credence Presets**: One-click High/Medium/Low buttons. Useful for searchers?

### For Kaplan (Domain Expert)

1. **Theoretical Frameworks**: Added Place Attachment, Restorative Environments, Environmental Preference detection. Removed generic terms (extent, compatibility). Complete?

2. **Pattern Refinements**: Moved thermal comfort to SUGGESTIVE, tightened LEED pattern. Correct domain modeling?

3. **Outcome Categories**: Added social, privacy, wayfinding, control. Complete for CNFA?

4. **Confounders**: Added demographic, individual sensitivity, organizational factors. What's missing?

### For Lamport (Formal Methods)

1. **INV-W8**: Added credence propagation invariant. Formulation correct?

2. **Snapshot Semantics**: Added explicit snapshot() method with WebOfBeliefSnapshot class. Consistency model adequately specified?

3. **Runtime Enforcement**: Which invariants should be runtime vs test-time?

### For Liskov (Software Design)

1. **Snapshot Class**: WebOfBeliefSnapshot provides immutable query-time copy. Good abstraction?

2. **Type Safety**: Snapshot maintains typed access to beliefs. Sufficient?

### For Brooks (Architecture)

1. **Feature Creep**: 7 filter facets, 6 measurement modalities, 7 theoretical frameworks. Over-engineering?

2. **Conceptual Integrity**: Does adding all these dimensions fragment the system's conceptual model?

### For Parnas (Module Design)

1. **Confounder Keywords**: Now spread across reporting.py in multiple lists. Should this be consolidated?

2. **Pattern Definitions**: Patterns in causal_classifier.py vs constants in query_response.py. Duplication?

### For Naur (Theory Building)

1. **Worked Examples**: Added to DESIGN_RATIONALE.md. Sufficient for theory reconstruction?

2. **Negative Examples**: Added "What we don't do" section. Adequate tacit knowledge capture?

---

## NEW: Questions for Modern AI/CS Leaders

### For Andrew Ng (ML Systems & MLOps)

1. **Data Pipeline**: The extraction pipeline uses pattern matching, not ML. Given the domain (scientific articles), is this the right choice? Would a fine-tuned model improve extraction accuracy?

2. **Labeling & Validation**: How should we validate the causal classifications? What's the gold standard annotation strategy for neuroarchitecture claims?

3. **MLOps Readiness**: If we add ML components later, is the architecture ready? What's missing for experiment tracking, model versioning, A/B testing?

4. **Data-Centric AI**: The system currently uses expert-defined patterns. Should we be collecting user feedback to improve patterns? What's the data flywheel strategy?

### For Andrej Karpathy (Practical ML Engineering)

1. **LLM Integration Points**: Where would an LLM add value? Claim extraction? Query understanding? Evidence summarization? All three?

2. **Prompt Engineering**: If using LLMs, what prompt patterns work best for scientific claim extraction? Chain-of-thought? Few-shot?

3. **Hybrid Systems**: Pattern matching for structure + LLM for understanding - is this the right architecture? Or should it be end-to-end?

4. **Error Analysis**: What's the failure mode analysis strategy? How do we catch systematic errors in classification?

### For Ilya Sutskever (Neural Network Scaling & Safety)

1. **Epistemic Uncertainty**: The system tracks credence and uncertainty. How does this relate to model uncertainty in neural networks? Should we be using ensemble methods?

2. **Emergent Capabilities**: At what scale would the web of belief exhibit emergent properties? Is coherentist epistemology compatible with neural scaling?

3. **Safety Alignment**: The system makes claims about causation in architectural design. What safety measures should exist to prevent misuse or overconfidence?

4. **Hallucination Risk**: If LLMs are integrated, how do we ground outputs in the evidence base? What's the retrieval-augmented generation strategy?

### For Yann LeCun (Self-Supervised Learning & Architecture)

1. **World Models**: The web of belief is essentially a world model for neuroarchitecture. How does this compare to learned world models? What are the trade-offs?

2. **Self-Supervised Signals**: Could the constraint satisfaction in equilibrium-seeking be formulated as a self-supervised learning objective?

3. **Energy-Based View**: The coherence score is like an energy function. Should we use gradient-based optimization for belief revision?

4. **Representation Learning**: The belief embeddings are implicit (text content). Should beliefs have learned vector representations?

### For Peter Norvig (AI Systems at Scale)

1. **Probabilistic Programming**: The web of belief is essentially a probabilistic knowledge base. Should we use PPL (Pyro, Stan) for coherence calculations?

2. **Search at Scale**: If the belief graph grows to millions of nodes, what search strategies apply? How do we maintain query latency?

3. **Knowledge Graphs**: How does this compare to enterprise knowledge graphs? What can we learn from Google's Knowledge Graph architecture?

4. **Evaluation Metrics**: Beyond test coverage, what system-level metrics matter? Precision@k? NDCG? User satisfaction proxies?

### For Jeff Dean (Large-Scale Systems & ML Infrastructure)

1. **Scaling Bottlenecks**: The current in-memory web is limited. What's the path to distributed web of belief? Sharding strategy?

2. **Serving Infrastructure**: For production, what's missing? Caching? Load balancing? Request routing by belief subgraph?

3. **Training Infrastructure**: If we add learned components, what's the training pipeline? TPU/GPU requirements?

4. **Monitoring & Observability**: What telemetry is needed? Belief drift detection? Query latency percentiles? Classification confidence distribution?

---

## Current Implementation Status

### Recently Completed (Sprint F Panel Validation)

**Critical**:
- INV-W8: Credence propagation invariant added

**High Priority**:
- CAPACITY bridge: P(bridge) = 0.45, tightened keywords
- Theoretical frameworks: Place Attachment, Restorative Environments, Environmental Preference
- Removed generic terms: extent, compatibility from ART patterns
- Snapshot semantics: WebOfBeliefSnapshot class added
- Measurement modalities: Expanded to 6 categories

**Medium Priority**:
- Thermal comfort moved to SUGGESTIVE
- LEED pattern tightened
- Outcome categories: social, privacy, wayfinding, control added
- Confounders: demographic, sensitivity, environmental, organizational added
- Frontend facets: year range, study type, framework
- Worked examples in DESIGN_RATIONALE.md

**Low Priority**:
- Causal method indicators: IPW, doubly robust, g-computation
- Vocabulary tooltips with "why expanded"
- Credence presets (High/Medium/Low)

### Test Status

```
Tests: 241 passing
Core modules:
- test_bridge_warrants.py: 27 tests
- test_web_persistence.py: 31 tests
- test_outcome_taxonomy.py: 26 tests
- test_reporting.py: 44 tests
- test_causal_classifier.py: 49 tests
- test_query_response.py: 33 tests
```

---

## Critical Questions for All Experts

1. **Is the system production-ready?** What's missing for deployment?

2. **What's the biggest architectural risk?** Single point of failure? Scalability limit?

3. **What would you prioritize for the next sprint?** ML integration? Scale testing? User studies?

4. **What's the validation strategy?** How do we know the system is correct?

5. **What's the maintenance burden?** Will pattern definitions drift? Who owns updates?

---

## Deliverables Requested

For each expert, provide:
1. **Assessment** (APPROVE / MODIFY / REJECT)
2. **Priority** (CRITICAL / HIGH / MEDIUM / LOW)
3. **Specific concerns** (with file:line references if applicable)
4. **Recommended actions**

For AI/CS leaders specifically:
- **Integration opportunity** (where ML/AI could add value)
- **Risk assessment** (what could go wrong)
- **Scaling consideration** (what breaks at 10x, 100x, 1000x)

---

## Files for Review

### Priority 1 - Core Engine
- `src/services/web_of_belief.py` (1600+ lines - THE key file)
- `src/services/causal_classifier.py` (650+ lines)
- `src/services/query_response.py` (800+ lines)

### Priority 2 - Supporting Services
- `src/services/reporting.py` (920+ lines)
- `src/services/bridge_warrants.py` (1000+ lines)
- `src/services/query_parser.py` (500+ lines)

### Priority 3 - API & Integration
- `app/routes/query.py`
- `app/routes/reports.py`
- `app/routes/web_of_belief.py`

### Priority 4 - Documentation & Governance
- `docs/DESIGN_RATIONALE.md` (now with worked examples)
- `docs/INVARIANTS.md` (with INV-W8 and snapshot semantics)
- `CLAUDE.md`
