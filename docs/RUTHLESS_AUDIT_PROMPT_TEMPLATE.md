# Ruthless System Audit Prompt — Reusable Template

*Version: V10 (2026-03-02)*
*Context: Post-Quinean Web of Belief / Epistemic Engineering System*
*Adaptable to any complex system audit*

---

## Instructions

Copy this prompt into a new AI session. Replace `[SYSTEM_NAME]`, `[SUBSYSTEM_LIST]`, and `[RECENT_CHANGES]` with your specifics. The 18-person panel, scoring dimensions, and expert decision framework are reusable as-is.

---

## Prompt

You are conducting a **ruthless, adversarial audit** of `[SYSTEM_NAME]`. Rules of engagement:
- Assume everything is wrong until proven otherwise
- No credit for intent — only working, tested implementations count
- References must be real, parameters must be justified
- Every claim must be verifiable via code or data

### 18-Person Expert Panel

Assign each audit task to 2-3 relevant panel members. Each panelist must:
1. **Assess** their domain from an adversarial perspective
2. **Score** their dimensions (1-10)
3. **Suggest improvements** from their individual expertise
4. **Flag decisions** that need focused deliberation

| # | Role | Expertise | Evaluates |
|---|------|-----------|-----------|
| 1 | Software Architect | Systems design, APIs, modularity | Architecture, contracts, DB design |
| 2 | Epistemologist | Foundherentism, defeasibility, warrant | Belief formation, credence, grounding |
| 3 | Test Engineer | Coverage, mutation testing, CI/CD | Test suite, success conditions |
| 4 | Data Engineer | Schema design, ETL, data quality | Pipelines, normalization, DB duality |
| 5 | Environmental Psychologist | IEQ, comfort, SBS | IV taxonomy, belief plausibility |
| 6 | Neuroscientist | EEG, fMRI, psychophysiology | Physiological DVs, neural measures |
| 7 | Lighting Researcher | CCT, illuminance, non-visual effects | Luminous taxonomy, parametric nodes |
| 8 | Acoustic Scientist | Soundscape, noise, speech privacy | Acoustic taxonomy, noise levels |
| 9 | Affect Researcher | PANAS, valence-arousal | DV classification, mood/affect |
| 10 | Well-being Specialist | Thermal comfort, IEQ satisfaction | Comfort DVs, thermal taxonomy |
| 11 | ML/Classification Expert | Taxonomy learning, hierarchical classification | Classifiers, generalization |
| 12 | NLP Specialist | Entity extraction, semantic similarity | Parsing, normalization |
| 13 | Bayesian Network Expert | DAG structure, causal inference | BN integration, constraints |
| 14 | Image/Vision Scientist | Computer vision, scene understanding | Image attributes, vision pipeline |
| 15 | Physiologist | Autonomic measures, HRV, cortisol | Physiological DV hierarchy |
| 16 | Expert System Designer | Knowledge representation, contracts | Integration layer, reflexes |
| 17 | HCI/UX Researcher | Progressive disclosure, explanation | UI, agent interaction |
| 18 | Research Methodologist | Meta-analysis, effect sizes, power | Effect size handling, bias |

### Audit Tasks

For each subsystem in `[SUBSYSTEM_LIST]`:
1. **End-to-end viability**: Can this pipeline execute from input → output without errors?
2. **Data integrity**: Are inputs validated? Are outputs conformant?
3. **Test coverage**: What % of the subsystem is tested? Are there integration tests?
4. **Success conditions**: Does the overseer monitor this subsystem?
5. **Expert plausibility**: Do domain experts agree the logic is correct?

### Specific Checks

1. **Pipeline Matrix**: For each pipeline, assess: Status (PASS/WARN/FAIL), tests exist, success conditions exist, rollback capability, error handling
2. **Classifier/Taxonomy Accuracy**: Sample N items, check classification accuracy, false positive/negative rates
3. **Belief Plausibility**: Sample top N beliefs, verify against domain literature
4. **Cross-system Integration**: Are all subsystem contracts satisfied? Schema mismatches?
5. **Self-monitoring**: Does the overseer detect all failure modes? Are reflexes adequate?
6. **Data Quality**: Field completeness rates, terminal error rates, normalization coverage

### Per-Panelist Improvement Suggestions

**CRITICAL**: Each of the 18 panelists MUST provide 3-4 specific improvement suggestions from their individual domain expertise. These should be:
- Concrete and actionable (not vague wishes)
- Prioritizable (tag as HIGH/MEDIUM/LOW)
- Connected to real system artifacts (cite files, functions, schemas)

### Scoring Dimensions (1-10 each)

| Dimension | What to assess |
|-----------|---------------|
| Philosophical coherence | Does the system implement its theoretical framework consistently? |
| Pipeline integrity | Do all pipelines execute end-to-end? |
| Success conditions | Are all subsystems monitored? |
| Architectural integrity | Clean separation? No structural debt? |
| Code quality | Tests, documentation, exception handling |
| Robustness | What happens when things break? |
| Interaction & workflow | Is the user experience coherent? |
| Content display | Is the system's knowledge accessible? |
| Credibility & rigor | Does the system produce trustworthy output? |
| Enterprise readiness | Could this deploy to production? |

### Expert Decisions Framework

For each decision requiring deliberation:
1. State the question clearly
2. Assign 2-3 relevant panelists
3. Document each panelist's position
4. Record the resolution or deferral reason
5. Track implementation status

### Output Format

Produce:
1. **Subsystem inventory table** (name, files, LOC, status, tests, panel lead)
2. **Per-dimension scores** with justification
3. **Per-panelist improvement suggestions** (3-4 each, tagged with priority)
4. **Expert decisions log** (questions requiring deliberation)
5. **Sprint backlog** ordered by severity × effort × impact
6. **Go/No-Go assessment** with conditions

### Recent Changes to Audit

`[RECENT_CHANGES]` — describe what was built since last audit, with file names and line counts.

---

## Example Usage

Replace the placeholders:

```
[SYSTEM_NAME] = "ATLAS Post-Quinean Web of Belief System"

[SUBSYSTEM_LIST] = 
1. QA & Query (9 files, 10K LOC)
2. Web of Belief (5 files, 7K LOC)
3. T3 Belief Engine (6 files, 3K LOC)
...

[RECENT_CHANGES] = 
- iv_dv_classifier.py: +60 semantic map entries
- t3_interp_bridge.py: NEW, 200 LOC
- generalization_tree.py: sample-size weighting
...
```
