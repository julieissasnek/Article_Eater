# CMR PROJECT — COWORK SPRINT TASK BRIEF
## Authority document for autonomous panel execution
## Last updated: February 22, 2026
## Model: Opus 4.6
## Project folder: /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/

---

# ⚠️ COWORK OPERATING INSTRUCTIONS — READ BEFORE ANY SPRINT

## Crash-resilience protocol — MANDATORY, NO EXCEPTIONS

1. Before writing any panel content:
   - Create the output file immediately (header block only)
   - Copy that stub to outputs immediately
   - Confirm file exists before continuing

2. During panel production — after every ~250 lines of content:
   - Append the completed section using incremental writes
   - Confirm line count has grown before continuing
   - Never write the entire panel as a single block

3. Save cadence within each panel:
   - After panel header and charge: SAVE
   - After every 2 opening statements: SAVE
   - After each Crucible debate: SAVE
   - After each calibrated JSON block: SAVE
   - After each Output Block: SAVE

4. After completing each sprint:
   - Mark sprint status as COMPLETE in this file (SPRINT_TASK_BRIEF.md)
   - Update TRANSFER_Feb21_Session8_CORRECTED.md §5 gap count
   - Add sprint output to §8 session registry in transfer document
   - Run gap tracker commands listed in the sprint entry

5. Recovery after crash:
   - Read this file to find last COMPLETE sprint
   - Read the partial output file for the interrupted sprint
   - Identify last saved section
   - Resume from next section — do not re-run completed sections

## Review checkpoints — MANDATORY

Before running each sprint:
- Check this file for a field: `pre_panel_review_cleared: true/false`
- If false: STOP. Write a summary of proposed expert roster to
  PENDING_REVIEW_[PANEL_ID].md and wait for human to clear it.
- If true: proceed.

After completing each sprint:
- Write confidence score summary to REVIEW_[PANEL_ID]_post.md
  listing every bridge warrant assignment and confidence score > 0.55
- Set field `post_panel_review_cleared: false` in this sprint entry
- Wait for human to set it to true before running gap tracker commands

## Style rules for all panels
- Bertrand Russell style: clear, intelligent, accessible, no humor
- APA references with DOIs for every citation
- No emojis in prose
- Calibrated JSON is mandatory output for every template
- Residual gaps section is mandatory for every template
- IC2 and AX4 super-template interaction is mandatory for every template
- Full reference list at end of every panel output

## Review guide
- Read `OPUS_REVIEW_GUIDE.md` at the start of every review session for
  calibration discipline rules (bridge warrant hierarchy, THEORETICAL_DEFAULT
  threshold, Coburn R² ceiling, red flags). Do not skip.

---

# SPRINT STATUS OVERVIEW

| Sprint | Panel | Templates | Status | Pre-review | Post-review |
|--------|-------|-----------|--------|------------|-------------|
| S-01 | SOCIAL-I | 11 | COMPLETE | true | true |
| S-02 | MEMORY-I | 10 | PENDING | false | false |
| S-03 | MULTI-I | 9 | PENDING | false | false |
| S-04 | MUSIC-I | 13 | PENDING | false | false |
| S-05 | THERMAL-I | 3 | PENDING | false | false |
| S-06 | CREATIVE-I | 7 | PENDING | false | false |
| S-07 | NEUROMOD-I | 10 | PENDING | false | false |
| S-08 | CROSSCUT-I | 15 | PENDING | false | false |

---

# SPRINT S-01: SOCIAL-I

**status**: COMPLETE
**pre_panel_review_cleared**: true
**post_panel_review_cleared**: true
**sprint_id**: S-01
**panel_id**: SOCIAL-I
**master_plan_sprint**: 13.18
**priority**: 3
**output_filename**: SOCIAL_I_Panel_Output.md

## Input files — read ALL before writing anything

1. `TRANSFER_Feb21_Session8_CORRECTED.md` — project state (CORRECTED version; replaces TRANSFER_Feb21_Session8.md which contained the AWE-I sequencing error)
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 SOCIAL-I specification
3. `exemplar_panel_criteria.md` — style authority
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md` — panel prompt template
5. `STRESS_I_Panel_Output_Feb21.md` — T6 (NM_THREAT_HPA_001) and T7 (IC_ALLOSTATIC_ANTICIPATION_001): SOCIAL-I's isolation allostatic load template interacts with T7's body-budget framework
6. `VISUAL_I_Panel_Output_Feb21.md` — VIEW1 five-channel model: Channel 5 (T5 ecological safety via amygdala) is the closest visual analogue to SOCIAL-I's vagal regulation and social safety signaling templates
7. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet; read before calibrating

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| PROXEMIC_PE_ARCH_001 | Proxemic PE — Architecture Mediates Interpersonal Distance | 4 | IC, SN, NM |
| NM_SOCIAL_ISOLATION_ALLOSTATIC_001 | Social Isolation Allostatic Load | 4 | NM, IC |
| SPATIAL_SOCIAL_ENCOUNTER_001 | Spatial Configuration → Social Encounter Frequency and Quality | 4 | SN, NM, EC |
| TERRITORIAL_AFFORDANCE_SOCIAL_001 | Territorial Affordance and Social Prediction Gradient | 4 | IC, NM, SN |
| PRIVACY_GRADIENT_REGULATION_001 | Architectural Privacy Gradient | 4 | IC, NM, SN, EC |
| NM_VAGAL_REGULATION_001 | Vagal Regulation and Social Engagement System | 3 | NM, IC |
| NM_OXYTOCIN_SOCIAL_003 | Social environmental features → oxytocin release → prosocial behavior | 2 | NM |
| CROSS_SOCIAL_MIRROR_PRESENCE_001 | Social Mirror and Embodied Social Presence | 3 | IC, EC |
| XF_SOCIAL_AFFORDANCE_DENSITY_001 | Spatial layout → social affordances → social behavior | 3 | SN, NM |
| CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 | TPJ Spatial-Social Bridge | 2 | SN, IC |
| CROSS_SOCIAL_AFFORDANCE_READING_001 | Social Affordance Reading and Mentalizing | 2 | IC, SN |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Larry Young** | Emory University | Oxytocin-vasopressin systems; NM_OXYTOCIN_SOCIAL_003 calibration. World authority on molecular mechanisms of social bonding. |
| **Ralph Adolphs** | Caltech | Amygdala and personal space; PROXEMIC_PE_ARCH_001 primary anchor. SM patient studies on interpersonal distance neural mechanisms. |
| **Dan Kennedy** | Notre Dame | Amygdala lesion and personal space; second anchor for PROXEMIC_PE_ARCH_001. Extends Adolphs' work to architectural proxemic contexts. |
| **Stephen Porges** | Indiana University | Polyvagal theory; NM_VAGAL_REGULATION_001 primary anchor. Social engagement system and vagal regulation of physiological state. |
| **Kinda Al-Sayed** | UCL Bartlett | Space Syntax and social behavior; SPATIAL_SOCIAL_ENCOUNTER_001 and XF_SOCIAL_AFFORDANCE_DENSITY_001. Empirical studies of visibility graphs → social encounter patterns. |
| **Robin Dunbar** | Oxford University | Social brain hypothesis; CROSS_SOCIAL_MIRROR_PRESENCE_001 and social group size constraints. Provides evolutionary anchoring for social space requirements. |
| **John Cacioppo** (legacy) / **Stephanie Cacioppo** | University of Chicago | Social isolation neuroscience; NM_SOCIAL_ISOLATION_ALLOSTATIC_001 primary anchor. Pioneered neural and physiological measurement of loneliness and social isolation. |
| **Rebecca Saxe** | MIT | Theory of mind / TPJ; CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 primary anchor. rTPJ activation during mentalizing and its spatial determinants. |
| **Robert Gifford** | University of Victoria | Environmental psychology of privacy and crowding; PRIVACY_GRADIENT_REGULATION_001 anchor. Extends Altman's privacy regulation to architectural contexts. |
| **David Kirsh** | UCSD | Embodied social cognition; CROSS_SOCIAL_AFFORDANCE_READING_001 complement. Social affordance perception in designed environments. |

**Flag for review**: Stephen Porges' polyvagal theory is controversial in some neuroscience subfields (Grossman, 2023, critique). Ensure Porges' contributions are limited to the vagal regulation parameters that have direct empirical support (cardiac vagal tone measures) rather than the broader autonomic hierarchy claims.

## Key calibration constructs

1. **Interpersonal distance thresholds** (Hall proxemic zones: intimate <1.5ft, personal 1.5–4ft, social 4–12ft, public >12ft) — architectural mediation of these zones via spatial configuration
2. **Vagal tone and social engagement system** — cardiac vagal tone (RMSSD) as a function of social environmental safety signals; polyvagal regulation hierarchy
3. **Oxytocin release conditions** — architectural features that promote prosocial interaction (visual co-presence at appropriate density, shared activity spaces, prospect-and-refuge seating)
4. **Social isolation allostatic load** — cumulative cortisol, inflammatory markers, and cardiovascular risk from chronic social-spatial deprivation
5. **Privacy gradient regulation** — Altman's privacy regulation theory parametrized for architectural boundary conditions (edge sharpness, visual penetration, acoustic isolation)
6. **Social affordance density** — integration value × edge condition density → encounter frequency and valence

## Cross-template inputs from prior panels

- From STRESS-I: T7 (IC_ALLOSTATIC_ANTICIPATION_001) — social isolation allostatic load template must be calibrated relative to T7's body-budget framework
- From VISUAL-I: VIEW1 Channel 5 (T5 ecological safety) — vagal regulation template's amygdala-reduction mechanism is VIEW1's Channel 5 at the social level; must not double-count
- From SPATIAL-I: SC4 (SPATIAL_SOCIAL_ENCOUNTER_001) — already partially calibrated by SPATIAL-I; SOCIAL-I inherits SC4's spatial configuration parameters and adds the social neuroscience layer

## Gap tracker commands (run only after post_panel_review_cleared = true)

```bash
python3 scripts/gap_tracker.py --mark-calibrated PROXEMIC_PE_ARCH_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_SOCIAL_ISOLATION_ALLOSTATIC_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated SPATIAL_SOCIAL_ENCOUNTER_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated TERRITORIAL_AFFORDANCE_SOCIAL_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated PRIVACY_GRADIENT_REGULATION_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_VAGAL_REGULATION_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_OXYTOCIN_SOCIAL_003 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_SOCIAL_MIRROR_PRESENCE_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated XF_SOCIAL_AFFORDANCE_DENSITY_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_SOCIAL_AFFORDANCE_READING_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 11 target templates have calibrated JSON with confidence scores
- [ ] All 11 target templates have residual gaps section
- [ ] All templates have IC2 and AX4 interaction statement
- [ ] CMR integration note written
- [ ] Full APA reference list appended
- [ ] REVIEW_SOCIAL_I_post.md written with confidence score summary
- [ ] post_panel_review_cleared set to false (awaiting human review)
- [ ] Status updated to COMPLETE in sprint overview table

---

# SPRINT S-02: MEMORY-I

**status**: COMPLETE
**pre_panel_review_cleared**: true
**post_panel_review_cleared**: true
**sprint_id**: S-02
**panel_id**: MEMORY-I
**master_plan_sprint**: 13.19
**priority**: 4
**output_filename**: MEMORY_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 MEMORY-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `SOCIAL_I_Panel_Output.md` — MEMORY-I depends on SOCIAL-I (context encoding and social memory interactions)
6. `02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md` — Templates 23 (SN_CONTEXT_MEMORY_002) and 25 (MS_RIPPLE_REPLAY_002) are MEMORY-I targets; read their structural specifications
7. `SPATIAL_I_Panel_Output_Feb21.md` (Doc 63) — SN_CONTEXT_MEMORY_002 interacts with spatial navigation templates
8. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| ED_HIPPOCAMPAL_ENCODING_001 | Hippocampal Relational Binding and Encoding | 5 | MS, SN |
| ED_RECONSOLIDATION_001 | Reconsolidation and Retrieval-Mediated Learning | 4 | MS |
| ED_SCHEMA_ENCODING_001 | Schema-Dependent Encoding Pathways | 4 | MS, PP |
| ED_SYSTEMS_CONSOLIDATION_001 | Systems Consolidation and Offline Replay | 4 | MS |
| ED_PATTERN_SEP_COMP_001 | Hippocampal Pattern Separation and Completion | 3 | MS, SN |
| ED_PE_ENCODING_PRINCIPLE_001 | The Prediction Error Encoding Principle | 3 | MS, PP |
| SN_CONTEXT_MEMORY_002 | Environmental context stability → context-dependent encoding | 3 | MS, SN |
| MS_RIPPLE_REPLAY_002 | Environmental rest → sharp-wave ripple replay → spatial consolidation | 4 | MS, SN |
| MS_CONSOLIDATION_RESTORATION_001 | Restorative environment → DMN → memory consolidation | 2 | MS, DT |
| THRESHOLD_EPISODIC_BOUNDARY_001 | Architectural Threshold as Episodic Boundary — Doorway Effect | 1 (medium) | MS, EC |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Lila Davachi** | Columbia University | Episodic memory binding; ED_HIPPOCAMPAL_ENCODING_001 primary anchor. |
| **Charan Ranganath** | UC Davis | Context-dependent encoding; SN_CONTEXT_MEMORY_002 primary anchor. |
| **Karim Nader** | McGill University | Reconsolidation; ED_RECONSOLIDATION_001 primary anchor. |
| **György Buzsáki** | NYU | Sharp-wave ripples and theta rhythms; MS_RIPPLE_REPLAY_002 primary anchor. |
| **Richard Morris** | University of Edinburgh | Schema-dependent learning; ED_SCHEMA_ENCODING_001 primary anchor. |
| **Nikolai Bhatt** | UC San Diego | Pattern separation computational models; ED_PATTERN_SEP_COMP_001 anchor. |
| **Marc Howard** | Boston University | Temporal context model; ED_PE_ENCODING_PRINCIPLE_001 complement. |
| **Gabriel Radvansky** | Notre Dame | Doorway effect / event boundary; THRESHOLD_EPISODIC_BOUNDARY_001 primary anchor. |
| **Environmental cognitive psychologist** | (from learning-space research) | Bridges lab memory findings to real-world educational and eldercare environments. |
| **Computational memory modeler** | (complementary learning systems) | Formal models of hippocampal-neocortical consolidation dynamics. |

## Key calibration constructs

1. **Hippocampal relational binding thresholds** — minimal environmental complexity for pattern separation vs. completion
2. **Reconsolidation temporal windows** — destabilization conditions, reconsolidation blockade timing
3. **Schema-dependent encoding rate** — neocortical schema availability → accelerated hippocampal encoding
4. **Sharp-wave ripple replay conditions** — environmental rest requirements for offline spatial memory consolidation
5. **Doorway effect boundary encoding** — architectural threshold properties → episodic segmentation strength

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated ED_HIPPOCAMPAL_ENCODING_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated ED_RECONSOLIDATION_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated ED_SCHEMA_ENCODING_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated ED_SYSTEMS_CONSOLIDATION_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated ED_PATTERN_SEP_COMP_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated ED_PE_ENCODING_PRINCIPLE_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated SN_CONTEXT_MEMORY_002 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated MS_RIPPLE_REPLAY_002 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated MS_CONSOLIDATION_RESTORATION_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --mark-calibrated THRESHOLD_EPISODIC_BOUNDARY_001 --panel MEMORY-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 10 target templates have calibrated JSON
- [ ] Residual gaps section per template
- [ ] IC2 and AX4 interaction per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_MEMORY_I_post.md written
- [ ] post_panel_review_cleared set to false
- [ ] Status updated to COMPLETE

---

# SPRINT S-03: MULTI-I

**status**: COMPLETE
**pre_panel_review_cleared**: true
**post_panel_review_cleared**: false
**sprint_id**: S-03
**panel_id**: MULTI-I
**master_plan_sprint**: 13.20
**priority**: 5
**output_filename**: MULTI_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 MULTI-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `VISUAL_I_Panel_Output_Feb21.md` — T1 (fractal/texture statistics) is the visual channel of MULTI-I's natural material convergence template; must not double-count
6. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| MATERIAL_IDENTITY_INTEGRATION_001 | Multi-Modal Material Identity Integration | 5 | MSI, PP, EC |
| CT_AFFECTIVE_TOUCH_001 | C-Tactile Affective Touch Pathway | 5 | EC, IC |
| NATURAL_MATERIAL_CONVERGENCE_001 | Natural Material Stress Reduction via Multi-Modal Convergence | 5 | MSI, IC, NM |
| HAP_SURFACE_MATERIAL_001 | Surface material → haptic exploration → affective response | 3 | EC, IC |
| MSI_INVERSE_EFFECTIVENESS_002 | Degraded unisensory channel → enhanced multisensory compensation | 3 | MSI |
| MSI_CONGRUENCY_PRINCIPLE_001 | Crossmodal congruency check → fluency and affect | 3 | MSI, PP |
| CROSSMODAL_CONGRUENCE_001 | Spatial navigation and social cognitive integration | 3 | MSI, SN |
| MATERIAL_CULTURAL_CONDITIONING_001 | Material-Cultural Conditioning and Evaluative Association | 3 | MSI, PP, IC |
| MATERIAL_AGING_TEMPORAL_DEPTH_001 | Material Aging and Temporal Depth — Patina as Perceptual Enrichment | 1 (medium) | EC, MS |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Charles Spence** | Oxford University | Crossmodal congruency and attention; MSI_CONGRUENCY_PRINCIPLE_001 primary anchor. |
| **India Morrison** | Linköping University | C-tactile afferents; CT_AFFECTIVE_TOUCH_001 primary anchor. |
| **Francis McGlone** | Liverpool John Moores | Affective touch neuroscience; CT_AFFECTIVE_TOUCH_001 complement. |
| **Barry Stein** (legacy) | Wake Forest University | Inverse effectiveness; MSI_INVERSE_EFFECTIVENESS_002 primary anchor. |
| **Marc Ernst** | Universität Ulm | Bayesian causal inference in MSI; MATERIAL_IDENTITY_INTEGRATION_001 computational anchor. |
| **Haptics engineer** | (selected for expertise) | HAP_SURFACE_MATERIAL_001 complement. Material surface → haptic perception. |
| **Byron Mikellides** | Oxford Brookes (emeritus) | Materials psychology in architecture; MATERIAL_CULTURAL_CONDITIONING_001 anchor. |
| **Juhani Pallasmaa** | Helsinki (emeritus) | Phenomenology of materiality; MATERIAL_AGING_TEMPORAL_DEPTH_001 theoretical anchor. |
| **Environmental psychologist** | (from materials/biophilic research) | Natural materials stress reduction empirical studies. |

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated MATERIAL_IDENTITY_INTEGRATION_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated CT_AFFECTIVE_TOUCH_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated NATURAL_MATERIAL_CONVERGENCE_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated HAP_SURFACE_MATERIAL_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated MSI_INVERSE_EFFECTIVENESS_002 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated MSI_CONGRUENCY_PRINCIPLE_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated CROSSMODAL_CONGRUENCE_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated MATERIAL_CULTURAL_CONDITIONING_001 --panel MULTI-I
python3 scripts/gap_tracker.py --mark-calibrated MATERIAL_AGING_TEMPORAL_DEPTH_001 --panel MULTI-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 9 target templates calibrated
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_MULTI_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE

---

# SPRINT S-04: MUSIC-I

**status**: PENDING
**pre_panel_review_cleared**: false
**post_panel_review_cleared**: false
**sprint_id**: S-04
**panel_id**: MUSIC-I
**master_plan_sprint**: 13.21
**priority**: 6
**output_filename**: MUSIC_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 MUSIC-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `MULTI_I_Panel_Output.md` — MSI interactions (master plan notes MUSIC-I depends on MULTI-I)
6. `VISUAL_I_Panel_Output_Feb21.md` — VF2 visual rhythm template (BRECVEMA rhythmic entrainment and VF2 are parallel temporal prediction mechanisms; must coordinate bridge warrants)
7. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| BRECVEMA_MULTI_MECHANISM_001 | BRECVEMA multi-mechanism musical emotion | 2 | PP, EC, NM, IC |
| BRECVEMA_BRAINSTEM_001 | Acoustic features → brainstem reflex → startle/attention | 1 (medium) | PP, NM |
| BRECVEMA_RHYTHMIC_ENTRAINMENT_002 | Musical pulse → motor entrainment → rhythmic coordination | 2 | EC, PP |
| BRECVEMA_CONTAGION_003 | Musical expression → emotional contagion → mirrored affect | 2 | IC, EC |
| BRECVEMA_EXPECTANCY_004 | Musical structure → expectancy violation → aesthetic emotion | 2 | PP, NM |
| BRECVEMA_MEMORY_005 | Musical cue → episodic memory retrieval → emotion reactivation | 2 | MS, IC |
| NEURAL_MUSIC_EMOTION_ARCH_001 | Neural Architecture of Music-Evoked Emotion | 3 | PP, NM, IC |
| PLEASURABLE_SADNESS_001 | The Paradox of Pleasurable Negative Emotions in Music | 3 | IC, PP |
| ACOUSTIC_EMOTION_MAPPING_001 | Acoustic Feature → Emotion Mapping (Bottom-Up Pathway) | 2 | PP, IC |
| MS_ACOUSTIC_ECOLOGY_001 | Acoustic Ecology and Soundscape Processing | 4 | MS, PP |
| AUD_SCENE_ANALYSIS_001 | Acoustic complexity → auditory scene analysis → cognitive load | 3 | MSI, PP |
| AUD_REVERBERATION_SPACE_003 | Room acoustics → auditory spatial perception → enclosure/safety | 3 | MSI, IC |
| AUDITORY_FRACTAL_SCALING_001 | Auditory 1/f Scaling — Biophilic Soundscape Statistics | 1 (medium) | PP |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Patrik Juslin** | Uppsala University | BRECVEMA originator; BRECVEMA_MULTI_MECHANISM_001 primary anchor. |
| **Stefan Koelsch** | University of Bergen | Neural architecture of music emotion; NEURAL_MUSIC_EMOTION_ARCH_001 primary anchor. |
| **Nina Kraus** | Northwestern University | Subcortical auditory plasticity; BRECVEMA_BRAINSTEM_001 primary anchor. |
| **Peter Vuust** | Aarhus University | Predictive coding and music; BRECVEMA_EXPECTANCY_004 primary anchor. |
| **Jian Kang** | UCL | Acoustic ecology and soundscape; MS_ACOUSTIC_ECOLOGY_001 primary anchor. ISO 12913 co-author. |
| **David Huron** | Ohio State University | Musical expectation; BRECVEMA_EXPECTANCY_004 complement. ITPRA theory. |
| **Tuomas Eerola** | Durham University | Pleasurable sadness and emotional contagion; PLEASURABLE_SADNESS_001 anchor. |
| **Trevor Cox** | University of Salford | Room acoustics perception; AUD_REVERBERATION_SPACE_003 anchor. |
| **Shinichi Sato** | (acoustics researcher) | Auditory scene analysis; AUD_SCENE_ANALYSIS_001 complement. |
| **Richard Taylor** | University of Oregon | Fractal scaling; AUDITORY_FRACTAL_SCALING_001 complement. 1/f statistics. |

**Note**: This panel has the most templates (13). 10 experts at the upper limit of the 8–10 range is recommended.

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_MULTI_MECHANISM_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_BRAINSTEM_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_RHYTHMIC_ENTRAINMENT_002 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_CONTAGION_003 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_EXPECTANCY_004 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated BRECVEMA_MEMORY_005 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated NEURAL_MUSIC_EMOTION_ARCH_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated PLEASURABLE_SADNESS_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated ACOUSTIC_EMOTION_MAPPING_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated MS_ACOUSTIC_ECOLOGY_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated AUD_SCENE_ANALYSIS_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated AUD_REVERBERATION_SPACE_003 --panel MUSIC-I
python3 scripts/gap_tracker.py --mark-calibrated AUDITORY_FRACTAL_SCALING_001 --panel MUSIC-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 13 target templates calibrated
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_MUSIC_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE

---

# SPRINT S-05: THERMAL-I

**status**: PENDING
**pre_panel_review_cleared**: false
**post_panel_review_cleared**: false
**sprint_id**: S-05
**panel_id**: THERMAL-I
**master_plan_sprint**: 13.22
**priority**: 7
**output_filename**: THERMAL_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 THERMAL-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `STRESS_I_Panel_Output_Feb21.md` — T7 (allostatic anticipation) directly feeds into thermal comfort as a form of metabolic prediction
6. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| THERMAL_ADAPTIVE_PE_001 | Thermal Comfort as Adaptive Prediction Error and Metabolic Regulation | 5 | IC, PP |
| IC_THERMAL_COMFORT_001 | Thermal Comfort and Thermoregulatory Interoceptive Processing | 4 | IC, NM |
| THERMAL_COMFORT_ADAPTIVE_PE_001 | Adaptive Thermal Comfort and Allesthesia | 1 (medium) | IC, PP |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Richard de Dear** | University of Sydney | Adaptive thermal comfort; originator; ASHRAE 55 contributor. |
| **Lisa Feldman Barrett** | Northeastern University | Interoceptive prediction; IC_THERMAL_COMFORT_001 primary anchor. |
| **Bud Craig** | Barrow Neurological Institute | Insular cortex thermoception; THERMAL_ADAPTIVE_PE_001 primary anchor. |
| **Wim van Marken Lichtenbelt** | Maastricht University | Brown adipose tissue and metabolic thermoregulation. |
| **Pawel Wargocki** | Technical University of Denmark | IEQ and thermal satisfaction; empirical anchor. |
| **Computational thermoregulation modeler** | (selected) | Skin-core temperature dynamics, allesthesia thresholds. |
| **Environmental psychologist** | (IEQ/occupant research) | Thermal satisfaction measurement in buildings. |
| **Architect** | (clinical building experience) | Thermal zoning for healthcare and eldercare. |

**Note**: Only 3 templates — 8 experts is appropriate; do not over-staff.

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated THERMAL_ADAPTIVE_PE_001 --panel THERMAL-I
python3 scripts/gap_tracker.py --mark-calibrated IC_THERMAL_COMFORT_001 --panel THERMAL-I
python3 scripts/gap_tracker.py --mark-calibrated THERMAL_COMFORT_ADAPTIVE_PE_001 --panel THERMAL-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 3 templates calibrated
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_THERMAL_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE

---

# SPRINT S-06: CREATIVE-I

**status**: PENDING
**pre_panel_review_cleared**: false
**post_panel_review_cleared**: false
**sprint_id**: S-06
**panel_id**: CREATIVE-I
**master_plan_sprint**: 13.23
**priority**: 8
**output_filename**: CREATIVE_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 CREATIVE-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `MEMORY_I_Panel_Output.md` — master plan notes CREATIVE-I depends on MEMORY-I via the DMN-restoration link
6. `VISUAL_I_Panel_Output_Feb21.md` — VF3 (R_h and affect broadening → CREA2B) is already partially calibrated; CREATIVE-I must read VF3's CREA2B coefficient and build on it rather than re-derive it
7. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| INCUBATION_ARCHITECTURE_001 | Incubation Architecture — Movement, Transition, Soft Fascination | 5 | EC, DT, PP |
| CREATIVE_NETWORK_DYNAMICS_001 | Creative Network Dynamics — DMN–Executive Coupling | 3 | DT, PP |
| COLLABORATIVE_CREATIVITY_ARCHITECTURE_001 | Collaborative Creativity Architecture | 3 | DT, SN, NM |
| HC_CREATIVE_DIVERGENCE_001 | Restoration-Enabled Creative Divergence | 3 | DT, NM |
| CROSS_CREATIVE_NETWORK_DYNAMICS_001 | Creative Network Dynamics — DMN-ECN-SN Coupling | 1 (medium) | DT, PP |
| PROCESSING_STYLE_MODULATION_001 | Multi-Channel Processing Style Modulation — Divergent/Convergent | 4 | DT, PP, NM |
| CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001 | Multi-Channel Processing Style — Creativity Goldilocks | 2 | DT, PP |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Roger Beaty** | Penn State | DMN-ECN coupling in creativity; primary anchor. |
| **Rex Jung** | University of New Mexico | Neuroscience of creativity; HC_CREATIVE_DIVERGENCE_001 anchor. |
| **Jonathan Schooler** | UCSB | Mind-wandering and incubation; INCUBATION_ARCHITECTURE_001 anchor. |
| **Kalina Christoff** | UBC | DMN dynamics and spontaneous thought; complement. |
| **Marily Oppezzo** | Stanford University | Walking and creative output; walking boosts divergent thinking ~60%. |
| **Keith Sawyer** | University of North Carolina | Collaborative creativity; primary anchor. |
| **Computational network modeler** | (DMN-TPN-SN) | Formal network switching and mode selection models. |
| **Architect** | (innovation-space design practice) | Translates cognitive mode switching to spatial design. |

## Critical cross-template note for Cowork

VF3 (VF3_SPATIAL_PROPORTIONS_001) already assigned d_divergent = 0.40 (range 0.25–0.55, confidence 0.55) to the CREA2B creativity bonus. CREATIVE-I must use this as an inherited parameter, not re-derive it. The CREATIVE-I panel should focus on the DMN-execution network coupling, incubation, and collaborative creativity templates — not repeat the ceiling height work already done in VISUAL-I.

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated INCUBATION_ARCHITECTURE_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated CREATIVE_NETWORK_DYNAMICS_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated COLLABORATIVE_CREATIVITY_ARCHITECTURE_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated HC_CREATIVE_DIVERGENCE_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_CREATIVE_NETWORK_DYNAMICS_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated PROCESSING_STYLE_MODULATION_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_ENVIRONMENTAL_PROCESSING_STYLE_001 --panel CREATIVE-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 7 templates calibrated
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_CREATIVE_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE

---

# SPRINT S-07: NEUROMOD-I

**status**: PENDING
**pre_panel_review_cleared**: false
**post_panel_review_cleared**: false
**sprint_id**: S-07
**panel_id**: NEUROMOD-I
**master_plan_sprint**: 13.25
**priority**: 10
**output_filename**: NEUROMOD_I_Panel_Output.md

## Input files

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 NEUROMOD-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. `STRESS_I_Panel_Output_Feb21.md` — NM_THREAT_HPA_001 (T5/T6) already partially calibrated; NEUROMOD-I inherits these values
6. `SOCIAL_I_Panel_Output.md` — master plan notes NEUROMOD-I depends on SOCIAL-I (allostatic load accumulation from social isolation)
7. `VISUAL_I_Panel_Output_Feb21.md` — cross-template flags assigned to NEUROMOD-I: VIEW1_T29_allostatic_restoration and VF1_IC2_cognitive_load_CCI_interaction must be resolved here
8. `LIGHT_I_Panel_Output_Feb21.md` — cross-template flags: ALLOSTATIC_MASTER_001 and NM_NORADRENERGIC_EXPLORE_006 from LIGHT-I assigned to NEUROMOD-I
9. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Missing Params | T1 Frameworks |
|----|------|---------------|---------------|
| ALLOSTATIC_MASTER_001 | Cumulative environmental demands → total allostatic cost | 3 | IC, NM |
| NM_REWARD_PREDICTION_ERROR_001 | Environmental Reward Prediction Error | 3 | NM, PP |
| NM_WANTING_LIKING_DISSOCIATION_001 | Architectural Wanting-Liking Dissociation | 4 | NM |
| NM_NORADRENERGIC_EXPLORE_006 | Environmental novelty/uncertainty → LC-NE → explore-exploit shift | 3 | NM, PP |
| NM_CHOLINERGIC_GATING_007 | Environmental salience → basal forebrain ACh → cortical precision | 3 | NM, PP |
| NM_DOPAMINE_NOVELTY_002 | Environmental novelty → dopaminergic response → exploration | 2 | NM |
| NM_DOPAMINERGIC_NOVELTY_REWARD_001 | Architectural novelty → dopaminergic response → wanting/approach | 3 | NM, PP |
| NM_THREAT_HPA_001 | Environmental threat cues → amygdala → HPA → cortisol | 2 | NM, IC |
| MULTIMODAL_PE_INTEGRATION_001 | Prediction Error Signals Feed Mesolimbic Dopamine | 3 | NM, PP |
| NM_SAFETY_SIGNALING_001 | Learned Safety and Active Threat Inhibition | 3 | NM, IC |

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Wolfram Schultz** | University of Cambridge | Reward prediction error; discoverer of dopaminergic RPE. **Do not substitute without flagging.** |
| **Kent Berridge** | University of Michigan | Wanting/liking dissociation; incentive salience vs. hedonic impact. **Do not substitute without flagging.** |
| **Gary Aston-Jones** | Rutgers University | LC-NE explore-exploit; NM_NORADRENERGIC_EXPLORE_006 anchor. |
| **Trevor Robbins** | University of Cambridge | Cholinergic/attentional gating; NM_CHOLINERGIC_GATING_007 anchor. |
| **Bruce McEwen** (legacy) / **Teresa Seeman** | Rockefeller / UCLA | Allostatic load; ALLOSTATIC_MASTER_001 primary anchor. |
| **Joseph LeDoux** | NYU | Amygdala threat detection; NM_THREAT_HPA_001 complement. |
| **Gregory Quirk / Mohammed Milad** | Puerto Rico / NYU | Safety signaling; NM_SAFETY_SIGNALING_001 anchor. vmPFC inhibition of amygdala. |
| **Computational neuromodulation modeler** | (selected) | Formal models of DA, NE, ACh interactions. |

## Critical note for Cowork

ALLOSTATIC_MASTER_001 (T29) is the **master template** that all other templates feed into. Calibrate it **LAST** within this panel, after all input templates are calibrated. T29's parameters depend on the cumulative outputs of dopaminergic, noradrenergic, cholinergic, and HPA templates.

## CALIBRATION CONSTRAINT (from MEMORY-I Flag 4)

PE encoding pathway (VTA → hippocampus) is shared between MEMORY-I templates (ED_PE_ENCODING_PRINCIPLE_001) and NEUROMOD-I dopaminergic templates. Apply partial-out rule: **NEUROMOD-I owns the dopaminergic mechanism; MEMORY-I owns the encoding consequence**. Do not double-count the PE signal as both a neuromodulatory input and an encoding driver. Cross-reference: PRE_PANEL_REVIEW_CLEARANCE_MEMORY_I.md Flag 4.

## MATHEMATICAL INTEGRATION NOTE — ALLOSTATIC_MASTER_001 (A-06, from Audit)

> [!CAUTION]
> **Audit Finding (A-03)**: The Sprint Brief previously specified that ALLOSTATIC_MASTER_001 must be calibrated LAST but provided NO functional constraints on HOW to mathematically integrate dopaminergic, noradrenergic, cholinergic, and HPA outputs into a single allostatic load metric. Without this guidance, the LLM agent will be forced to invent ungrounded theoretical math.

**Required integration approach for T29 (ALLOSTATIC_MASTER_001):**

1. **Additive weighted-sum model** (not multiplicative). Allostatic load is a cumulative cost, not a cascading product:
   ```
   AL_total = w_HPA × HPA_chronic_activation
            + w_NE  × NE_tonic_elevation
            + w_DA  × DA_reward_deficit
            + w_ACh × ACh_precision_failure
            + w_inflammation × inflammatory_load
   ```

2. **Weights (w_i) must be sourced from McEwen & Stellar (1993) or Seeman et al. (2001)**. If no direct weight is available, use equal weights (1.0) and flag as `THEORETICAL_DEFAULT`.

3. **Each sub-system contributes via its CHRONIC deviation from homeostasis**, not its acute phasic response. Specifically:
   - HPA: chronic cortisol slope flattening (not acute cortisol spikes)
   - NE: sustained tonic elevation (not phasic alerting bursts)
   - DA: chronic reward prediction error deficit (not single novelty responses)
   - ACh: sustained precision weighting failure (not momentary attention shifts)

4. **The allostatic load output is dimensionless (0-10 scale)** normalized to population reference ranges from Seeman et al.

5. **Social isolation load** (from SOCIAL-I, NM_SOCIAL_ISOLATION_ALLOSTATIC_001) enters as an additive term, NOT as a multiplicative moderator.

6. **Constraint**: The sum must be monotonically non-decreasing over exposure duration. Allostatic load accumulates; it does not spontaneously decrease without recovery intervention.

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated ALLOSTATIC_MASTER_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_REWARD_PREDICTION_ERROR_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_WANTING_LIKING_DISSOCIATION_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_NORADRENERGIC_EXPLORE_006 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_CHOLINERGIC_GATING_007 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_DOPAMINE_NOVELTY_002 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_DOPAMINERGIC_NOVELTY_REWARD_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_THREAT_HPA_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated MULTIMODAL_PE_INTEGRATION_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --mark-calibrated NM_SAFETY_SIGNALING_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --report
```

## Completion checklist

- [ ] All 10 templates calibrated
- [ ] ALLOSTATIC_MASTER_001 calibrated last, incorporating all prior panels
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_NEUROMOD_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE

---

# SPRINT S-08: CROSSCUT-I

**status**: PENDING
**pre_panel_review_cleared**: false
**post_panel_review_cleared**: false
**sprint_id**: S-08
**panel_id**: CROSSCUT-I
**master_plan_sprint**: 13.26
**priority**: 11
**output_filename**: CROSSCUT_I_Panel_Output.md

## Input files — ALL prior panel outputs required

1. `TRANSFER_Feb21_Session8_CORRECTED.md`
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 CROSSCUT-I specification
3. `exemplar_panel_criteria.md`
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
5. ALL completed panel output files — CROSSCUT-I is the integrating panel that derives cross-cutting parameters from the aggregate of all prior work
6. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

## Target templates

| ID | Name | Category | T1 Frameworks |
|----|------|----------|---------------|
| AX_DOSE_RESPONSE_007 | Dose-Response Cross-Cutting Axiom | AX-series | Various |
| AX_CULTURAL_MODULATION_009 | Cultural Modulation Cross-Cutting Axiom | AX-series | Various |
| AX_INDIVIDUAL_DIFFERENCES_008 | Individual Differences Cross-Cutting Axiom | AX-series | Various |
| AX_CONTROL_STRESS_004 | Control-Stress Interaction Axiom | AX-series | IC, NM |
| AX_HABITUATION_002 | Habituation Cross-Cutting Axiom | AX-series | PP |
| AX_CHRONIC_ACUTE_011 | Chronic-Acute Temporal Distinction | AX-series | NM, IC |
| AX_ATTENTION_MEDIATION_010 | Attention Mediation Axiom | AX-series | PP, DT |
| AX_VR_LIMITATION_012 | VR Ecological Validity Limitation | AX-series | EC |
| CROSS_WM_GAMMA_BETA_DYNAMICS_001 | Working Memory Gamma-Beta Dynamics | CROSS | MS, PP |
| CROSS_PROACTIVE_REACTIVE_CONTROL_001 | Proactive/Reactive Cognitive Control | CROSS | DT, PP |
| CROSS_HIERARCHICAL_CONTROL_001 | Hierarchical Cognitive Control | CROSS | DT, PP |
| CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001 | Thalamic Environmental Filter | CROSS | PP, NM |
| TEMPORAL_HIERARCHY_ARCH_PE_001 | Temporal Hierarchy of Architectural PE | CROSS | PP |
| ER_ECOLOGICAL_RATIONALITY_001 | Ecological Rationality | CROSS | PP, EC |
| SALIENCE_NETWORK_SWITCH_001 | Salience Network Switching | CROSS | DT, NM |

**Note**: The AX3 awe templates flagged by VISUAL-I belong here, not in a standalone AWE-I panel. If AX3_AWE_HIGH_PE_001, AX3_SMALL_SELF_001, and AX3_NEED_FOR_ACCOMMODATION_001 are in the gap registry, add them to this sprint's target list.

## Expert roster (proposed — subject to pre-panel review)

| Expert | Institution | Primary Contribution |
|--------|------------|---------------------|
| **Meta-analyst (dose-response)** | (selected) | Dose-response modeling across environmental psychology; AX_DOSE_RESPONSE_007. |
| **Computational neuroscientist (cross-domain)** | (selected) | Parameter estimation across all T1 frameworks. Internal consistency. |
| **Individual differences / psychometrics specialist** | (selected) | AX_INDIVIDUAL_DIFFERENCES_008. Population stratification moderators. |
| **Cultural neuroscience researcher** | (selected) | AX_CULTURAL_MODULATION_009. Cross-cultural validation. |
| **Gerd Gigerenzer** (legacy) / **Lael Schooler** | (ecological rationality) | ER_ECOLOGICAL_RATIONALITY_001. Adaptive heuristics. |
| **Dacher Keltner** | UC Berkeley | AX3 awe templates (if in scope). Awe phenomenology and small-self. |
| **Network neuroscientist (DMN-TPN-SN)** | (selected) | SALIENCE_NETWORK_SWITCH_001 and CROSS_HIERARCHICAL_CONTROL_001. |
| **Thalamic gating researcher** | (selected) | CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001. Reticular nucleus gating. |

## Critical note for Cowork

This is the final panel. Before beginning, read ALL prior panel output files and extract:
(a) all THEORETICAL_DEFAULT flags that appeared in more than 3 panels
(b) all cross-template interaction flags that were assigned to CROSSCUT-I
(c) all AX-series template stubs
The panel's primary task is to derive canonical AX parameter ranges from the aggregate of domain-panel outputs.

## Gap tracker commands

```bash
python3 scripts/gap_tracker.py --mark-calibrated AX_DOSE_RESPONSE_007 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_CULTURAL_MODULATION_009 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_INDIVIDUAL_DIFFERENCES_008 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_CONTROL_STRESS_004 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_HABITUATION_002 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_CHRONIC_ACUTE_011 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_ATTENTION_MEDIATION_010 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated AX_VR_LIMITATION_012 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_WM_GAMMA_BETA_DYNAMICS_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_PROACTIVE_REACTIVE_CONTROL_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_HIERARCHICAL_CONTROL_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated TEMPORAL_HIERARCHY_ARCH_PE_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated ER_ECOLOGICAL_RATIONALITY_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --mark-calibrated SALIENCE_NETWORK_SWITCH_001 --panel CROSSCUT-I
python3 scripts/gap_tracker.py --report
# Final report — should show close to 0 remaining high-severity gaps
```

## Completion checklist

- [ ] All 15 templates calibrated
- [ ] All cross-panel AX parameter ranges derived and documented
- [ ] All prior THEORETICAL_DEFAULT flags reviewed and upgraded where possible
- [ ] Residual gaps per template
- [ ] IC2 and AX4 per template
- [ ] CMR integration note
- [ ] Full APA reference list
- [ ] REVIEW_CROSSCUT_I_post.md written
- [ ] post_panel_review_cleared false
- [ ] Status COMPLETE
- [ ] FINAL gap tracker report run and appended to this file

---

# APPENDIX: STANDING REVIEW PROTOCOL

## Pre-panel review (handled by Sonnet in claude.ai)

When Cowork writes `PENDING_REVIEW_[PANEL_ID].md`, share it in claude.ai
and ask: "Review this proposed expert roster for [PANEL_ID]. Flag any
expert whose primary expertise does not match the specific calibration
constructs they are being asked to anchor."

When cleared, return to Cowork and set:
`pre_panel_review_cleared: true` in the relevant sprint entry.

## Post-panel review (handled by Sonnet in claude.ai)

When Cowork writes `REVIEW_[PANEL_ID]_post.md`, share it in claude.ai
and ask: "Review these bridge warrant assignments and confidence scores.
Flag: (a) any confidence score above 0.65 for an architectural outcome
measure that lacks direct architectural empirical data, (b) any MECHANISM
warrant assigned to a parameter where only EMPIRICAL_COVARIANCE is
warranted, (c) any parameter above 0.50 that should carry THEORETICAL_DEFAULT."

When cleared, return to Cowork and set:
`post_panel_review_cleared: true` in the relevant sprint entry.
Cowork then runs the gap tracker commands for that sprint.

---

*SPRINT_TASK_BRIEF.md — CMR Project*
*Generated by Antigravity, February 22, 2026*
*To be read by Cowork as standing orders*
*Update sprint status fields in place as work completes*
