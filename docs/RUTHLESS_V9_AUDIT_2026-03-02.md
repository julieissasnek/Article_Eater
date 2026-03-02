# RUTHLESS V9 — Full-System Audit with 18-Expert Panel

*Created: 2026-03-02 by DK request*
*Status: ACTIVE — Execute immediately*
*Previous: V8 scored 6.1/10, AESHI 88.29 GREEN*

---

## Purpose

Post-sprint audit of everything built by AG and CW since V8. The system has grown substantially with new subsystems (T3 belief engine, IV/DV classifier, image attribute sync, field reviewer, interpretation space, credence-warrant, theory agents, missing templates). This audit uses an **18-person expert panel** with deeper domain expertise than prior audits.

**Rules of engagement**: Adversarial. Assume everything is wrong until proven otherwise. No credit for intent. References must be real. Parameters must be justified.

---

## 18-Person Expert Panel

### Core Architecture (4 experts)
| # | Role | Expertise | Evaluates |
|---|------|-----------|-----------|
| 1 | **Software Architect** | Distributed systems, API design, modularity | Integration layer, contracts, DB architecture |
| 2 | **Epistemologist** | Foundherentism, defeasibility, warrant theory | Belief formation, credence, grounding |
| 3 | **Test Engineer** | Coverage, mutation testing, CI/CD | Test suite (4,994 tests), success conditions |
| 4 | **Data Engineer** | Schema design, ETL, data quality | Extraction pipeline, field normalization, DB duality |

### Domain Science (6 experts)
| # | Role | Expertise | Evaluates |
|---|------|-----------|-----------|
| 5 | **Environmental Psychologist** | IEQ, comfort, SBS | IV taxonomy, belief plausibility |
| 6 | **Neuroscientist** | EEG, fMRI, psychophysiology | Physiological DVs, access levels, neural measures |
| 7 | **Lighting Researcher** | CCT, illuminance, non-visual effects | Luminous taxonomy, CCT parametric nodes |
| 8 | **Acoustic Scientist** | Soundscape, noise effects, speech privacy | Acoustic taxonomy, noise parametric levels |
| 9 | **Affect Researcher** | Emotion measurement, PANAS, valence-arousal | DV classification, mood/affect measures |
| 10 | **Well-being/Comfort Specialist** | Thermal comfort, IEQ satisfaction | Comfort DVs, thermal taxonomy |

### Computational (4 experts)
| # | Role | Expertise | Evaluates |
|---|------|-----------|-----------|
| 11 | **ML/Classification Expert** | Taxonomy learning, hierarchical classification | IV/DV classifier, generalization tree |
| 12 | **NLP Specialist** | Entity extraction, semantic similarity | Antecedent/consequent parsing, field normalization |
| 13 | **Bayesian Network Expert** | DAG structure, causal inference | BN↔EN integration, constraint propagation |
| 14 | **Image/Vision Scientist** | Computer vision, scene understanding | Image attributes (36), vision pipeline |

### Integration & Design (4 experts)
| # | Role | Expertise | Evaluates |
|---|------|-----------|-----------|
| 15 | **Physiologist** | Autonomic measures, HRV, cortisol | Physiological DV hierarchy, access level rules |
| 16 | **Expert System Designer** | Knowledge representation, contract-first design | T3 integration layer, overseer reflexes |
| 17 | **HCI/UX Researcher** | Progressive disclosure, explanation depth | Streamlit UI, grounded expert agent |
| 18 | **Research Methodologist** | Meta-analysis, effect sizes, power analysis | Effect size handling, p-value normalization, field reviewer |

---

## What's New Since V8

### AG-Built (This Session)
| Component | LOC | Tests | Status |
|-----------|-----|-------|--------|
| `iv_dv_classifier.py` | ~550 | 30/30 | ✅ Live, integrated |
| `image_attribute_sync.py` | ~300 | Needs tests | ✅ Live, 28 nodes |
| `field_reviewer.py` | ~350 | Needs tests | ✅ Dry-run verified |
| `extraction_field_spec.json` | ~140 | Used by reviewer | ✅ Data-validated |
| `test_iv_dv_classifier.py` | ~220 | 30 tests | ✅ All pass |
| `stimulus_taxonomy.py` expansion | +60 nodes | Covered by T3 tests | ✅ 133 total nodes |
| `t3_belief_engine.py` wiring | Classifier integration | 108/108 T3 tests | ✅ 519 established beliefs |

### CW-Built (Recent Sessions)
| Component | LOC | Status |
|-----------|-----|--------|
| Interpretation Space (Phase 3) | ~1000 | ✅ Complete |
| Theory Agent Profiles (Sprint T7) | ~800 | ✅ Complete |
| Credence-Warrant Integration | ~600 | ✅ Complete |
| Missing Templates + Ceiling Decisions | ~500 | ✅ Complete |
| Phase 1A/1B Completion | ~400 | ✅ Complete |
| IMG2 Phase 3 (Image Attributes v1.4) | ~300 | ✅ Complete |
| Backfill Outcome IDs | ~200 | ✅ Complete |

---

## Audit Tasks

### RV9-1: T3 Belief Engine End-to-End Verification
**Panel leads**: Epistemologist (#2), ML Expert (#11), Env Psychologist (#5)

**What**: Verify the complete T3 pipeline: raw extraction → classifier → generalization tree → belief formation → aggregation → established/contested/nascent status.

**Specific checks**:
1. Are the 519 established beliefs **scientifically plausible**? Sample 25 and verify against source papers.
2. Are the 19 contested beliefs **genuinely contested** in the literature? Or are they classifier artifacts?
3. Is the "Light & Color → Happiness (41 studies, 90%)" belief too broad? Should it decompose?
4. Does "Fractal dimension → Aesthetic preference (22 studies, 82%)" correctly aggregate studies that measured different DVs?
5. Do the access level rules (conscious/autonomic/behavioral/neural) correctly prevent cross-level generalization?
6. Is the 28.2% unclassified rate acceptable? What are the top unclassified patterns?

**Expert questions to store**:
- Should "acoustic environment → accuracy" (68 studies) be decomposed by noise type?
- Is it valid to merge across AR/VR/real settings?
- How should the classifier handle multi-factor IVs ("CCT × illuminance interaction")?

---

### RV9-2: IV/DV Classifier Accuracy Audit
**Panel leads**: NLP Specialist (#12), ML Expert (#11), Research Methodologist (#18)

**What**: Evaluate the 3-stage classifier quality. Test edge cases, adversarial inputs, taxonomy coverage gaps.

**Specific checks**:
1. **False positive rate**: Sample 50 "pattern-matched" IVs — are they correctly classified?
2. **False negative rate**: Sample 50 "unclassified" IVs — could they have been classified?
3. **Semantic map completeness**: Run all unique antecedents through classifier, report coverage by domain
4. **DV measure type accuracy**: Are access levels (conscious/autonomic/neural) correctly inferred?
5. **Abstract attribute extraction**: Does "5700K" → CCT_K=5700 work reliably across formats?
6. **Cross-cutting conflicts**: What happens when an IV maps to multiple taxonomy nodes?

**Test commands**:
```bash
python3 -m pytest tests/test_iv_dv_classifier.py -v
python3 -c "from src.services.iv_dv_classifier import get_classifier; clf = get_classifier(); print(clf.classification_stats())"
```

---

### RV9-3: Image Attribute ↔ Taxonomy Sync Verification
**Panel leads**: Image Scientist (#14), Lighting Researcher (#7), Vision Scientist (#14)

**What**: Verify the auto-sync path from `causal_theoretic_image_attributes.json` → taxonomy nodes → classifier.

**Specific checks**:
1. Do all 36 image attributes have taxonomy mappings? (Currently 31/36 mapped)
2. Are the 5 unmapped attributes correctly excluded (retired/deprecated)?
3. Do keywords in the attribute mappings match the actual attribute computations?
4. Is the addition of 28 new taxonomy nodes from image sync creating duplicate/overlapping nodes?
5. Does the classifier correctly classify IVs that correspond to computed image attributes?

---

### RV9-4: Field Reviewer Accuracy & Coverage
**Panel leads**: Data Engineer (#4), NLP Specialist (#12), Research Methodologist (#18)

**What**: Validate the field spec and reviewer against actual data quality issues.

**Specific checks**:
1. Review the 1,121 terminal issues (6.4%) — are they truly unfixable?
2. Is the `p_value` handling correct? (`<0.001`→0.001, `ns`→1.0)
3. Is the `direction` normalization correct? (`no_effect`→`null`, `positive`→`increase`)
4. Are there field types the spec doesn't cover? (52 finding fields, spec covers ~15)
5. What about multi-valued fields? (`self_report|behavioral`, `self_report, performance`)
6. Does `--fix` mode produce correct output? Test on 10 files manually.

**Test commands**:
```bash
python3 scripts/field_reviewer.py --report /tmp/field_review_report.md
```

---

### RV9-5: Taxonomy Coherence & Domain Coverage
**Panel leads**: Env Psychologist (#5), Lighting (#7), Acoustic (#8), Comfort (#10), Affect (#9)

**What**: Domain experts review taxonomy node definitions, keywords, and hierarchy for accuracy.

**Specific checks by domain**:
1. **Luminous** (19 nodes, 5 experts): Are CCT parametric levels (2700K warm, 4000K neutral, 6500K cool, 17000K enriched) correct? Are illuminance levels (≤200 low, 200–500 standard, ≥500 high) aligned with standards?
2. **Acoustic** (10 nodes, 2 experts): Is "noise.moderate (45-65 dB)" the right range? Is soundscape quality correctly defined?
3. **Thermal** (8 nodes, 1 expert): Are temperature parametric levels (≤20°C cool, 20-26°C comfortable, ≥26°C warm) aligned with ASHRAE?
4. **Natural/Biomorphic** (10+5 nodes): Are fractal dimension keywords accurate? Is spectral slope (1/f) correctly placed under biomorphic?
5. **Affect DVs**: Is the affect hierarchy (positive/negative → specific emotions) complete? Missing: awe, boredom, fascination.

**Expert questions to store**:
- Should we add a "multisensory" node for studies manipulating >1 modality?
- How to handle "perceived control" (person_state? or social_spatial?)?
- Need a "biophilia" abstract node separate from specific biophilic elements?

---

### RV9-6: Interpretation Space & Phase 3 Verification
**Panel leads**: Epistemologist (#2), Research Methodologist (#18), Expert System Designer (#16)

**What**: Verify Phase 3 interpretation space results and boundary closure gap.

**Specific checks**:
1. Is 62% validation closure an honest number? Spot-check 10 of the 31 "well replicated" beliefs
2. Is the 0% boundary closure a measurement failure or genuine gap?
3. Are the frontier questions actionable? Could they drive real evidence acquisition?
4. Does the Phase 3 integration with T3 nascent beliefs create a coherent search pipeline?

---

### RV9-7: Cross-System Integration Audit
**Panel leads**: Software Architect (#1), Expert System Designer (#16), Data Engineer (#4)

**What**: Verify that AG's new systems (T3, classifier, field reviewer, image sync) integrate correctly with CW's systems (interpretation space, theory agents, credence-warrant).

**Specific checks**:
1. Can T3 beliefs feed into interpretation space analysis?
2. Does the classifier share a taxonomy with `outcome_taxonomy.py`?
3. Do the theory agent profiles use T3 belief data?
4. Is the credence-warrant formula applied to T3 beliefs?
5. Do image attribute computes feed back into the classifier pipeline?
6. Are there schema conflicts between AG and CW JSON outputs?

---

### RV9-8: Pipeline Integrity Re-Assessment
**Panel leads**: Software Architect (#1), Test Engineer (#3)

**What**: Re-evaluate the V8 pipeline matrix. Which of the 3 FAIL / 3 WARN pipelines are now passing?

**Updated matrix to verify**:
- Paper Acquisition → Still FAIL? (API keys issue)
- Extraction (Gemini) → Now has field reviewer
- Integration Cascade (14-step) → Transaction semantics?
- T3 Pipeline → NEW — needs assessment (PASS expected)
- AESHI → Previously WARN, check if updated with new metrics

---

### RV9-9: V8 Critical Issues Re-Assessment
**Panel leads**: All 18

**What**: For each of the 15 V8 critical issues, assess current status:

| V8 Issue | Current Status | Action |
|----------|----------------|--------|
| 1. Test suite blocked (cv2) | Fixed (pytest.importorskip) | ✅ Verify |
| 2. 4 pipelines lack SCs | Partially addressed | Check |
| 3. BN→EN feedback | Not implemented | Design decision needed |
| 4. Two active databases | Unknown | Check |
| 5. No deployment procedure | Unknown | Check |
| 6. 151 silent exception swallows | Unknown | Check |
| 7. No adversarial testing | Not done | Design phase |
| 8. 14-step cascade no rollback | Unknown | Check |
| 9. SC registry underpopulated | 89 SCs now | Verify |
| 10. 72 scripts bypass get_web_db() | Partially fixed | Check |
| 11. No user personas | Not done | Design needed |
| 12. No replication tracking | Not done | T3 partially addresses |
| 13. Pydantic V1 deprecation | Unknown | Check |
| 14. 33 stubs/TODOs | Unknown | Count |
| 15. No API key audit | Unknown | Check |

---

### RV9-10: Synthesis — AESHI Re-score + Sprint Plan
**Panel leads**: All 18

**What**: Compute updated AESHI. Generate sprint backlog ordered by severity × effort × impact.

**Output**:
1. Updated 10-dimension scoring (target: ≥ 7.0/10 average)
2. Sprint backlog (S1: 1-day fixes, S2: 3-day sprints, S3: 1-week sprints)
3. Expert decisions log (items needing panel deliberation)
4. Go/No-Go assessment for production readiness

---

## Expert Decisions to Store

These are design decisions that would benefit from focused expert deliberation:

1. **Generalization Granularity** (#5, #11): When should T3 merge "CCT 2700K vs 5700K" with "CCT 3000K vs 6500K"? Parametric range or mechanism identity?
2. **Cross-modal Merging** (#6, #9): Can a study using "VR forest" generalize with "real forest walk"? What about "forest image" vs "forest sound"?
3. **Contested Belief Adjudication** (#2, #18): When studies disagree (wood→attention: 15/15 split), is this a moderator effect, measurement artifact, or genuine inconsistency?
4. **Access Level Boundaries** (#6, #15): Should we merge across heart rate (autonomic) and self-reported arousal (conscious) when both measure "stress response"?
5. **Publication Bias in T3** (#18): Should T3 weight sample size? Address file drawer problem? Apply trim-and-fill?
6. **Taxonomy Depth vs Breadth** (#11, #12): 133 nodes with 28 from image sync — is this over-specified? Are there nodes with no data?
7. **Field Reviewer Normalization Decisions** (#4, #18): Is normalizing `<0.001` → 0.001 losing critical information? Should we store both original + normalized?

---

## Execution Plan

### Phase 1: Automated Checks (30 min)
```bash
# Run all tests
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -30

# T3 pipeline numbers
python3 -c "..." # (use script from classifier verification)

# Field reviewer
python3 scripts/field_reviewer.py --report /tmp/rv9_field_review.md

# Image sync
python3 -c "from src.services.image_attribute_sync import sync_image_attributes; print(sync_image_attributes())"

# Count stubs/TODOs
grep -rn "TODO\|STUB\|FIXME\|HACK\|XXX" src/ --include="*.py" | wc -l
```

### Phase 2: Expert Panel Reviews (1-2 hours)
- Each audit task assigned to panel leads
- Experts review code, data, and outputs
- Store decisions needing deliberation in `docs/EXPERT_DECISIONS_LOG.md`

### Phase 3: Sprint Planning (30 min)
- Rank all findings by severity × impact
- Group into sprints (S1 immediate, S2 this week, S3 next week)
- Assign to AG or CW based on expertise

### Phase 4: Execute & Verify (variable)
- Fix highest-priority items
- Re-run automated checks
- Expert re-review of contested decisions
