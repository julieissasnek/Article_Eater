# CLAUDE.md — ATLAS (Article Eater) Implementation Context
## Version 3.0 — February 26, 2026

> **Start here**: Read `ARCHITECTURE.md` for the system overview, `SCHEMA_REGISTRY.md` for data contracts. This file covers task tracking, governance rules, coding guidelines, and domain knowledge.

---

## Project Overview

Article Eater is a research system that extracts causal claims from scientific literature and assembles them into Bayesian networks using Quinean coherentist epistemology. The system processes papers from cognitive neuroscience of architecture (CNFA) — a field studying how built environments affect human cognition, emotion, physiology, and behavior.

**Epistemic Tier 2** extends the system with reflexive monitoring capabilities: the system reasons about its own epistemic health, detects structural vulnerabilities in the evidence network, and communicates confidence calibration to users.

## Architecture Summary

### Four Channels of Epistemic Confidence

Every claim in the web of belief is assessed on four channels:

1. **Network Coherence** — How well does this claim cohere with other claims in the web? (Quinean mutual support)
2. **Source Quality** — How methodologically sound is the evidence? (presentation_validity + measurement_validity + task_ecological_validity + design_validity)
3. **Bayesian Integration** — How does this claim update the posterior distribution? (Pearl's d-separation, explaining away, causal inference)
4. **Meta-Epistemic Monitoring** — What are the structural vulnerabilities? (concentration risk, unfalsifiability, circularity, temporal decay)

### Three Tiers

- **Tier 1**: Theoretical frameworks (10 canonical frameworks per Decision 3):
  1. PP — Predictive Processing
  2. SN — Spatial Navigation / Cognitive Mapping
  3. DP — Dual-Process Evaluation
  4. DT — DMN/TPN Dynamics
  5. NM — Neuromodulatory Systems
  6. IC — Interoceptive / Constructionist Affect
  7. MS — Memory Systems
  8. EC — Embodied Cognition
  9. CB — Chronobiological Regulation
  10. MSI — Multisensory Integration
- **Tier 1.5 Domain Theories**: ART (→ PP+SN), SRT (→ NM+IC), Biophilia (→ multiple T1) — formally reduced to T1 frameworks, not T1 themselves
- **Tier 2 Epistemic**: Epistemic infrastructure (quality assessment, coherence computation, reflexive monitoring)
- **Tier 2b**: Methodological validity framework (measurement instruments, presentation modalities, task-ecological validity)
- **Tier 3**: Extracted empirical claims (the actual nodes in the Bayesian network)

## Key Concepts

### Quinean Web of Belief
No foundational claims. Every claim supported by coherence with other claims. Revision propagates: changing one claim's status may require adjusting connected claims. The system maintains dynamic coherence scores rather than fixed truth values.

### Bridge Warrants
Explicit links between theoretical framework predictions and empirical findings. A bridge warrant says: "Framework F predicts finding E, with confidence C, via mechanism M." These are first-class nodes in the web, not mere annotations.

### Source Quality (EXPANDED IN V2.0)
Now computed from five sub-scores:
- `methodological_rigor` — general design quality (randomization, blinding, sample size, pre-registration)
- `presentation_validity` — how well the stimulus captures real architectural experience for this specific construct
- `measurement_validity` — how well the instrument captures the specific construct claimed
- `task_ecological_validity` — how well the experimental task recreates real building use (NEW)
- `independence_of_evidence` — are studies independent or from the same lab/paradigm?

### Claim Type Bifurcation (NEW IN V2.0)
Two distinct claim types:
- **Type A — Evaluative-response claims**: "People prefer environments with X." Well-supported by standard paradigm.
- **Type B — Functional-effect claims**: "X reduces occupant stress / improves performance." Requires ecological evidence.
Connected by GENERALIZABILITY_WARRANT links (default weight 0.5).

### Effect Pathways (NEW IN V2.0)
Per Canonical Decision 4 (`SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED`):
- **SUBPERSONAL**: Effect operates through non-conscious mechanisms (physiological regulation, implicit priming, automatic processing). Example: natural light regulates circadian rhythm without awareness.
- **PERSONAL_EPISTEMIC**: Effect requires conscious engagement or evaluation (person notices, judges, or reasons about the architecture). Example: aesthetic preference based on proportions.
- **MIXED**: Both pathways plausibly active. Example: wayfinding involves both automatic cognitive mapping and conscious decision-making.

### Method Registry (NEW IN V2.0)
A growing, queryable data structure profiling every measurement instrument and presentation modality encountered in the literature. Each entry contains temporal dynamics, confound structure, construct validity maps, and VR-specific threats. The registry is NOT static — it learns as new papers are processed. New/unknown methods are flagged as UNCHARACTERIZED for expert profiling.

### Five Types of Automatic Argumentative Challenges
When a claim is extracted, the system checks methods against registry profiles and generates latent challenges:
1. **Temporal misalignment** — instrument lag exceeds sampling protocol
2. **Presentation lacks critical channel** — construct depends on sensory channel the modality strips
3. **VR confounded measurement** — VR study without cybersickness control
4. **Single-modality measurement** — only one measurement type used
5. **Exposure duration inadequate** — too short for construct to manifest

### Task-Ecological Validity (NEW IN V2.0)
Five components, weighted:
- task_authenticity (0.30) — ecological task vs. artificial evaluation
- state_characterization (0.20) — incoming affective/cognitive/physical state measured?
- attentional_ecology (0.20) — attention directed to features or naturally distributed?
- temporal_ecology (0.15) — exposure duration representative of real use?
- social_ecology (0.15) — social context representative of real building use?

Task classification hierarchy:
- EXPLICIT_EVALUATION (0.2) — rate, judge, evaluate
- LAB_COGNITIVE_TASK (0.4) — Stroop, digit span in experimental room
- SIMULATED_ECOLOGICAL (0.6) — VR wayfinding, TSST
- REAL_TASK_CONTROLLED (0.8) — actual work/navigation observed
- NATURAL_BEHAVIOR (1.0) — POE, ESM, longitudinal data

## Sprint Structure

| Sprint | Focus | Duration | Depends On |
|--------|-------|----------|------------|
| 1 | Schema extensions, template scaffolds | 2 weeks | — |
| 2 | BN nodes, edges, 3-pathway model | 2 weeks | Sprint 1 |
| 3 | Reflexive monitoring algorithms | 2–3 weeks | Sprint 2 |
| 4 | Extraction pipeline extensions | 2 weeks | Sprint 1 |
| **4b** | **Method registry + task-ecological validity** | **2 weeks** | **Sprint 1** |
| 5 | Integration testing, CNFA validation | 2–3 weeks | Sprints 1–4b |

**Total: 12–14 weeks. Sprint 4b runs in parallel with Sprints 2–4.**

## File Structure

```
src/
  epistemic/
    schema.py          # Extended claim/link schemas (Sprint 1)
    templates.py       # BW, EEW, CONC, AC templates (Sprint 1)
    bn_nodes.py        # BN integration nodes (Sprint 2)
    bn_edges.py        # Causal edge types (Sprint 2)
    monitors/
      concentration.py   # Evidence concentration risk (Sprint 3)
      unfalsifiability.py # Unfalsifiable claim detection (Sprint 3)
      coherence.py       # Coherence anomaly detection (Sprint 3)
      temporal.py        # Temporal decay tracking (Sprint 3)
    extraction/
      tier2_extractor.py  # Extended extraction pipeline (Sprint 4)
      method_identifier.py # Method detection from papers (Sprint 4b)
  methods/
    registry.py          # MethodRegistry class and MethodEntry dataclass (Sprint 4b)
    seed_data.py         # Initial 15+ seed entries (Sprint 4b)
    task_ecology.py      # TaskClass, EffectPathway, ClaimType, scoring (Sprint 4b)
    validity_scorer.py   # Per-claim validity computation (Sprint 4b)
tests/
  test_sprint1.py
  test_sprint2.py
  test_sprint3.py
  test_sprint4.py
  test_sprint4b.py
  test_sprint5_integration.py
```

## Key Domain Knowledge

### The Immersion Hierarchy (7 levels)
Level 7: Real building, natural behavior — everything preserved
Level 6: Real building, controlled task — multisensory + embodied
Level 5: Room-scale VR with locomotion — visual + movement
Level 4: HMD VR stationary — visual immersion + head tracking
Level 3: 360° video — surround visual
Level 2: Photographs/renderings — central visual pattern only
Level 1: Verbal descriptions — conceptual only

### The Passive Observer Fallacy
Standard CNFA paradigm treats participants as spectators (rate images, stand in VR, walk prescribed paths). Real building users are task-active, goal-directed beings. The building is background resource for ecological tasks (wayfinding, working, healing, socializing). This fundamentally changes which features are processed, at what precision, through what pathways.

### Critical Instrument Facts
- Cortisol: 15-20 min onset lag. Sample taken during 15-min VR exposure measures PRE-exposure state.
- HRV: Cybersickness mimics stress physiological signature. Uninterpretable without cybersickness control.
- EEG: Movement artifacts make walking-through-building studies unusable without sophisticated rejection.
- Self-report + physiology consistently mismatch in VR studies (Albayrak-Kutlay et al. 2025).
- Photos: r = 0.86 with in-situ for PREFERENCE only. Not validated for stress, cognition, wayfinding, restoration.

### Gold Standard Study: Fich et al. (2014)
CAVE VR, N=93, TSST stressor (ecological task!), 7 cortisol time points (proper temporal resolution), fully orthogonal design. Found: enclosed room → 73% cortisol increase with slower recovery. Cortisol and HRV dissociated (different systems affected). Best methodological exemplar in CNFA.

## Coding Guidelines

- Python 3.10+, type hints everywhere
- Dataclasses for data structures, Pydantic where validation needed
- All enum values as string enums for JSON serialization
- Every function has docstring explaining epistemic rationale, not just code function
- Test names describe the epistemic property being verified
- Commit messages reference Sprint and Task number: `[Sprint 4b / Task 4b.3] Add task-ecological validity scoring`

## Reference Documents

- `Methodological_Validity_Framework_Tier2b_V1.0.docx` — Measurement and presentation validity (Part I)
- `Ecological_Validity_CNFA_Background_Notes_V1.0.docx` — Task-ecological validity, expert panel, method registry schema (Part II)
- `Missing_Fourth_Channel_Epistemic_Tier2_V1.0.docx` — Theoretical foundation
- `Epistemic_Tier2_Implementation_Plan_V1.0.docx` — Original sprint plan
- `IMPLEMENTATION_TASKS.md` — Original 30 atomic tasks
- `IMPLEMENTATION_TASKS_ADDENDUM.md` — Sprint 4b: 7 new tasks (method registry + task ecology)

---

## User Shortcuts

### "show progress"

When David says "show progress", display the PDF Extraction Live Monitor:

```bash
python3 scripts/monitor_queue.py
```

Or run inline Python to extract stats from `data/extraction_pipeline/extraction_queue.json` and display:
- Total In Queue, Currently Claimed, Actively Processing
- Successfully Accepted, Failed/Needs Review, Requeued
- Remaining Pending, Total API Cost, Mean Extraction Time
- Overall Progress percentage with progress bar

**Note**: Only meaningful when PDF extraction processes are actively running (Gemini API extraction pipeline).
