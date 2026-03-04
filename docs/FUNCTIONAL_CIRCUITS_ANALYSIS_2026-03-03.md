# Functional Circuits: Analysis & Architectural Mapping

## TL;DR

**The system already has most of the infrastructure.** The 6 T2 computational archetypes from your Claude Chrome transcript are already coded as `T2ArchetypeType` in [mechanism_templates.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/mechanism_templates.py). Processing fluency is already a registered T1.5 theory with inputs/outputs/linked archetypes. What's missing: the other 21 functional circuits as data entries, and the T1-level atoms as an explicit registry.

---

## What Already Exists

### T2 Archetypes (all 6 from the transcript ✅)

The [T2ArchetypeType](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/models/mechanism_templates.py#L32-L39) enum already has:

| Archetype | Enum Value | Dataclass |
|:----------|:-----------|:----------|
| Predictive Coding | `predictive_coding` | `PredictiveCodingArchetype` |
| Homeostatic Regulation | `homeostatic_regulation` | `HomeostaticRegulationArchetype` |
| Accumulation to Bound | `accumulation_to_bound` | `AccumulationToBoundArchetype` |
| Competitive Selection | `competitive_selection` | `CompetitiveSelectionArchetype` |
| Gated Propagation | `gated_propagation` | `GatedPropagationArchetype` |
| Convergent State Monitoring | `convergent_state_monitoring` | *(class exists)* |

Each has `input_variables`, `output_variables`, `parameters: Dict[str, ParameterSpec]`, `domain_examples`, and `t1_framework_links`.

### Processing Fluency (the Claude Chrome example ✅)

Already registered at [data/theories/processing_fluency.json](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/theories/processing_fluency.json) with:

- **Inputs**: `prediction_error_magnitude`, `perceptual_organization_cost`, `metabolic_cost_rate`
- **Outputs**: `fluency_signal`, `approach_probability`, `aesthetic_judgment_bias`, `truth_judgment_bias`
- **Linked archetypes**: `PREDICTIVE_CODING`, `HOMEOSTATIC_REGULATION`, `GATED_PROPAGATION`
- **3 constructs** each mapped to template IDs with reduction confidence

### Infrastructure (already built ✅)

| Layer | Registry | Data Dir | Count |
|:------|:---------|:---------|:------|
| T1.5 Theories | `T1_5Registry` | `data/theories/` | **25** |
| Molecules | `MoleculeRegistry` | `data/molecules/` | **18** |
| T2 Archetypes | `T2ArchetypeType` enum | code-level | **6** |
| QA Router | `MoleculeAwareRouter` | `data/qa_cache/` | wired |
| Molecule QA | `MoleculeAwareRouter._classify_question()` | — | routes to cache |

---

## What the Claude Chrome Discussion Adds

### The Key Conceptual Distinction

The transcript correctly identifies that functional circuits are **T1.5 molecules whose internal organization follows T2 templates**. In our system's terms:

- **Molecule** (`molecule_type: "MECHANISM"`) = the functional circuit itself
- **T2 Archetype** (`linked_archetypes`) = which computational template it instantiates  
- **Components** (`MoleculeComponent`) = the T1-level atoms it wires together
- **T1.5 Theory** (`parent_t1_5_theory`) = the domain theory it supports

This maps cleanly. Processing fluency already demonstrates the pattern.

### 22 Functional Circuits to Register

Here are the circuits from the transcript, grouped by T2 template:

#### T2-1: Convergent State Monitoring (5)

| Circuit | Inputs | Output | Exists? |
|:--------|:-------|:-------|:--------|
| Fluency monitoring | PE, perceptual org, metabolic cost | ease signal → hedonic marking | ✅ `PROCESSING_FLUENCY` |
| Coherence monitoring | cross-modal PEs, temporal consistency | conflict signal → behavioral adjust | ❌ NEW |
| Environmental threat monitoring | enclosure, illumination, sharpness, occlusion | avoidance signal | ❌ NEW |
| Vitality/energy monitoring | interoceptive signals, fatigure, sleep pressure | resource signal | ❌ NEW |
| Social safety monitoring | facial expression, vocal prosody, familiarity | social threat/safety signal | ❌ NEW |

#### T2-2: Predictive Matching (4)

| Circuit | Exists? |
|:--------|:--------|
| Sensory prediction error (low-level) | ❌ NEW |
| Social prediction error | ❌ NEW |
| Reward prediction error | ❌ NEW |
| Aesthetic expectation violation | ❌ NEW |

#### T2-3: Homeostatic Regulation (4)

| Circuit | Exists? |
|:--------|:--------|
| Arousal regulation | Partial — `berlyne_arousal.json` covers domain |
| Cognitive load regulation | Partial — `cognitive_load_architecture.json` covers domain |
| Thermoregulatory-style affect regulation | ❌ NEW |
| Interpersonal distance regulation | Partial — `proxemics.json` covers domain |

#### T2-4: Accumulation to Bound (3)

| Circuit | Exists? |
|:--------|:--------|
| Familiarity detection | ❌ NEW |
| Dread/anxiety accumulation | ❌ NEW |
| Interest/curiosity accumulation | ❌ NEW |

#### T2-5: Competitive Selection (3)

| Circuit | Exists? |
|:--------|:--------|
| Attentional selection | ❌ NEW |
| Action selection | ❌ NEW |
| Interpretive selection (bistability) | ❌ NEW |

#### T2-6: Gated Propagation (3)

| Circuit | Exists? |
|:--------|:--------|
| Affective gating of memory | ❌ NEW |
| Context-gated threat response | ❌ NEW |
| Expertise-gated aesthetic processing | ❌ NEW |

**Score: 1 existing, ~3 partial, 18 fully new.**

### T1 Atoms: A Missing Layer

The transcript enumerates ~30 T1-level computational primitives (lateral inhibition, gain control, Bayesian updating, binding, Hebbian association, etc.). The system has no explicit T1 atom registry. T1 frameworks (PP, NM, IC, etc.) exist, but the individual computational primitives are not indexed as searchable entities.

---

## Answering Your Questions

### "Are there more of these?"

Yes — at least 4 beyond what Claude Chrome lists:
- **Habit circuit** (T2: gated_propagation — repetition removes the gate)
- **Empathic resonance** (T2: convergent_state_monitoring over mirrored states)
- **Temporal prediction** (T2: predictive_matching over rhythmic structure — connects to `brecvema.json`)
- **Disgust/contamination monitoring** (T2: convergent_state_monitoring over pathogen cues)

### "Do we have some other entity to characterize?"

**No, we don't need a new entity type.** The functional circuits map perfectly onto existing infrastructure:

```
Functional Circuit = Molecule(molecule_type="MECHANISM")
                     linked to T2Archetype via linked_archetypes
                     composed of MoleculeComponents (the T1 atoms)
                     parented to T1_5Theory via parent_t1_5_theory
```

What we need is a **new molecule_type value**: `"FUNCTIONAL_CIRCUIT"` alongside the existing `THEORY`, `MECHANISM`, `PHENOMENON`, `DESIGN_PATTERN`.

### "What should we surface in QA?"

| Entity Layer | QA Surface? | How |
|:-------------|:-----------|:----|
| T1 frameworks (PP, NM, IC...) | ✅ Already via framework_voices | Enrichment step 7 |
| T1-level atoms (PE, gain control...) | ⚠️ NOT YET — need atom registry | New data layer |
| T1.5 theories (25 registered) | ✅ Via T1_5Registry + linked molecules | QA cache |
| Molecules (18 registered) | ✅ Via MoleculeAwareRouter fast path | QA cache |
| Functional circuits (22 identified) | ❌ NOT YET — need molecule entries | Same as molecules |
| T2 archetypes (6 coded) | ⚠️ NOT DIRECTLY — only via molecules | Could add direct route |
| T3 metabeliefs (~519 clusters) | ✅ Via cluster answer cards | Card retriever |

---

## What Needs To Be Done

### Priority 1: Register the 18 new circuits as molecules

Create JSON files in `data/molecules/` following the `processing_fluency.json` pattern. Each needs:
- `molecule_type: "FUNCTIONAL_CIRCUIT"`
- `linked_archetypes: [which T2]`
- `inputs/outputs`
- Components with template_ids

### Priority 2: Add `FUNCTIONAL_CIRCUIT` to molecule_type enum

One-line change in [schema.py](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/molecules/schema.py#L61): add to the comment documenting valid values.

### Priority 3: Wire T2 archetype → molecule index in MoleculeRegistry

Add `find_by_archetype(archetype_type)` method so QA can say "show me all convergent state monitors."

### Priority 4: T1 Atom Registry (later)

Create `data/atoms/` with JSON definitions of the ~30 computational primitives. This is lower priority because the atoms are implicit in the template IDs already.

---

## For CW / Master Doc

This analysis should be added to the master doc as part of the subsystem inventory. The key addition is that functional circuits are **not a new tier** — they are molecules whose internal structure follows T2 templates. The existing T1 → T1.5 → Molecule hierarchy absorbs them cleanly.

The Claude Chrome references list (60+ papers with citation counts) should be added to the master doc's bibliography or at minimum to a reference appendix.

---

## CW Handoff

**CW should:**
1. Review this analysis and flag any disagreements with the mapping
2. Populate the 18 new functional circuit molecule JSONs in `data/molecules/` (or split this work with AG)
3. Add `find_by_archetype()` to `MoleculeRegistry` if CW owns that file
4. Contribute to the panel prompt at `docs/PANEL_PROMPT_T_LEVELS_FUNCTIONAL_CIRCUITS_2026-03-03.md`
5. Consider whether the existing T1.5 theories in `data/theories/` need `linked_archetypes`, `inputs`, `outputs` fields added (processing_fluency.json already has them; the other 24 do not)

**Key finding**: The `processing_fluency.json` already demonstrates the full pattern — `linked_archetypes`, `inputs`, `outputs`, constructs mapped to template IDs. The other 24 T1.5 theories should be updated to match this richer schema.
