# PRE-PANEL REVIEW CLEARANCE — MEMORY-I (S-02)
## Reviewed by: Sonnet in claude.ai, February 22, 2026
## Decision: CLEARED WITH ROSTER MODIFICATIONS

---

## Roster changes (mandatory — apply before proceeding)

### Change 1: Replace Nikolai Bhatt with Michael Yassa on ED_PATTERN_SEP_COMP_001

Bhatt is a computational modeler. The template requires empirical calibration of
DG-CA3 pattern separation thresholds as a function of environmental input
similarity. Michael Yassa (UCI) has the most directly relevant human high-
resolution fMRI data distinguishing pattern separation from pattern completion
in hippocampal subfields, and his work on how environmental distinctiveness
modulates the separation/completion balance is the empirical foundation this
template needs.

**Replace**: Nikolai Bhatt → **Michael Yassa** (University of California, Irvine)
as primary anchor for ED_PATTERN_SEP_COMP_001.

### Change 2: Replace Annabelle Deza with Gabriel Radvansky on THRESHOLD_EPISODIC_BOUNDARY_001

"Annabelle Deza — NYU" does not appear to be a researcher associated with the
doorway effect literature. The doorway effect was established by Gabriel
Radvansky: Radvansky & Copeland (2006) and Radvansky, Krawietz, & Tamplin
(2011) are the canonical studies. Radvansky is at Notre Dame.

**Replace**: Annabelle Deza → **Gabriel Radvansky** (University of Notre Dame)
as primary anchor for THRESHOLD_EPISODIC_BOUNDARY_001.

### Change 3: Replace Koen Lamberts with Margaret Schlichting on MS_CONSOLIDATION_RESTORATION_001

Lamberts' expertise is perceptual decision-making and categorization, not memory
consolidation during rest. The template calibrates how restorative environments
promote DMN-mediated offline consolidation — this is waking rest, not sleep.
Margaret Schlichting's work on offline memory integration and hippocampal-
cortical consolidation during rest periods is directly relevant.

Erin Wamsley (Furman) was also considered but her focus is sleep-dependent
consolidation. The template concerns waking restorative environments (ART-
derived, DMN re-engagement), making Schlichting the better match.

**Replace**: Koen Lamberts → **Margaret Schlichting** (University of Toronto)
as primary anchor for MS_CONSOLIDATION_RESTORATION_001.

### Change 4: Name the practitioner — Colin Ellard

The brief specified "spatial cognition architect (from practice)" without
naming an individual. For calibration credibility, name a specific person.

**Replace**: unnamed practitioner → **Colin Ellard** (University of Waterloo).
Ellard is a neuroscientist by training who runs empirical studies of
physiological and emotional responses to urban and architectural environments.
His work on facade complexity and street-level design bridges computational
parameters to built-environment effects. He is a researcher-practitioner, not
a practitioner reading neuroscience — an important distinction for calibration
quality.

### Change 5: Assign Davachi as primary on ED_PE_ENCODING_PRINCIPLE_001

The PE encoding principle template currently has Howard as complement but no
named primary anchor. Davachi's work on prediction violation and hippocampal
encoding strength (including her work with Shohamy on reward prediction errors
modulating hippocampal encoding, and Davachi & DuBrow, 2015 on temporal
boundaries) makes her the natural primary. The PE encoding principle is
mechanistically continuous with relational binding — prediction errors at
encoding are what make some bindings stronger than others. This is a natural
double assignment, not a stretch.

**Add**: Lila Davachi as primary anchor on ED_PE_ENCODING_PRINCIPLE_001
(in addition to her existing primary on ED_HIPPOCAMPAL_ENCODING_001).
Marc Howard remains complement.

### Change 6: Assign Buzsaki and Morris to ED_SYSTEMS_CONSOLIDATION_001

This template had no named primary anchor. Sharp-wave ripple replay IS the
mechanism of systems consolidation at the neural level; Buzsaki is the
authority on both. Morris's schema-dependent encoding work describes what
happens when consolidation has already created neocortical schemas —
accelerated systems consolidation. Both contribute.

**Add**: György Buzsáki as primary anchor on ED_SYSTEMS_CONSOLIDATION_001
(in addition to MS_RIPPLE_REPLAY_002). Richard Morris as complement on
ED_SYSTEMS_CONSOLIDATION_001 (in addition to his primary on
ED_SCHEMA_ENCODING_001).

---

## Revised roster — 10 experts, 10 templates

| # | Expert | Institution | Primary assignment | Additional |
|---|--------|------------|-------------------|------------|
| 1 | Lila Davachi | Columbia | ED_HIPPOCAMPAL_ENCODING_001 | ED_PE_ENCODING_PRINCIPLE_001 (primary) |
| 2 | Charan Ranganath | UC Davis | SN_CONTEXT_MEMORY_002 | |
| 3 | Karim Nader | McGill | ED_RECONSOLIDATION_001 | Bridge ≤ CAPACITY for architectural params |
| 4 | György Buzsáki | NYU | MS_RIPPLE_REPLAY_002 | ED_SYSTEMS_CONSOLIDATION_001 (primary) |
| 5 | Richard Morris | Edinburgh | ED_SCHEMA_ENCODING_001 | ED_SYSTEMS_CONSOLIDATION_001 (complement) |
| 6 | Michael Yassa | UCI | ED_PATTERN_SEP_COMP_001 | REPLACES Bhatt |
| 7 | Marc Howard | Boston University | ED_PE_ENCODING_PRINCIPLE_001 (complement) | |
| 8 | Gabriel Radvansky | Notre Dame | THRESHOLD_EPISODIC_BOUNDARY_001 | REPLACES Deza |
| 9 | Margaret Schlichting | U Toronto | MS_CONSOLIDATION_RESTORATION_001 | REPLACES Lamberts |
| 10 | Colin Ellard | Waterloo | Environmental design translation | Named; REPLACES unnamed |

---

## Template-expert coverage check

| Template | Primary | Complement | Coverage |
|----------|---------|-----------|----------|
| ED_HIPPOCAMPAL_ENCODING_001 | Davachi | | Complete |
| ED_RECONSOLIDATION_001 | Nader | | Complete |
| ED_SCHEMA_ENCODING_001 | Morris | | Complete |
| ED_SYSTEMS_CONSOLIDATION_001 | Buzsáki | Morris | Complete |
| ED_PATTERN_SEP_COMP_001 | Yassa | | Complete |
| ED_PE_ENCODING_PRINCIPLE_001 | Davachi | Howard | Complete |
| SN_CONTEXT_MEMORY_002 | Ranganath | | Complete |
| MS_RIPPLE_REPLAY_002 | Buzsáki | | Complete |
| MS_CONSOLIDATION_RESTORATION_001 | Schlichting | | Complete |
| THRESHOLD_EPISODIC_BOUNDARY_001 | Radvansky | | Complete |

All 10 templates have named primary anchors. Three double assignments
(Davachi ×2, Buzsáki ×2, Morris ×2), all mechanistically justified.

---

## Constraints to enforce during calibration and post-panel review

1. **Nader reconsolidation bridge ceiling**: Reconsolidation is established in
   animal fear conditioning. Translation to architectural contexts (how spatial
   environment changes interact with reconsolidation of spatial memories) is
   speculative. Bridge warrants for architectural parameters on
   ED_RECONSOLIDATION_001 must not exceed CAPACITY (0.45). ANALOGICAL (0.35)
   is more defensible for any specific architectural manipulation claim.

2. **Ripple replay environmental conditions**: Buzsáki's SWR data are from
   rodent hippocampus during quiet rest. The translation to "architectural
   rest spaces promote SWR-mediated consolidation in humans" requires
   specifying what "quiet rest" means architecturally (low visual complexity,
   acoustic shielding, postural support). These parameters should carry
   THEORETICAL_DEFAULT until a human neuroimaging study measures SWR analogues
   during rest in varied architectural conditions.

3. **Doorway effect magnitude**: Radvansky's doorway effect is well-replicated
   but small (typically d ≈ 0.30-0.50 for recall decrement after boundary
   crossing). The architectural translation — that threshold design properties
   (contrast magnitude, spatial compression ratio) modulate episodic
   segmentation strength — has not been parametrically tested in real
   buildings. Bridge warrant: EMPIRICAL_COVARIANCE at best (the effect is
   demonstrated in VR and physical rooms, but specific architectural threshold
   properties have not been varied parametrically). Confidence on dose-response
   parameters should carry THEORETICAL_DEFAULT.

4. **Systems consolidation timescale**: ED_SYSTEMS_CONSOLIDATION_001 operates
   on timescales of weeks to years (gradual hippocampal-to-neocortical
   transfer). Any architectural claim about single-session or single-day
   effects on systems consolidation is inconsistent with the mechanism's
   timescale. The panel must distinguish between: (a) acute environmental
   effects on consolidation-supporting neural activity (ripple replay, DMN
   re-engagement), which are session-scale, and (b) systems consolidation
   itself, which is not. Confidence scores for acute effects can be moderate;
   confidence scores for claims about architectural effects on systems
   consolidation as such should be very low (< 0.40).

5. **SPATIAL-I interaction**: SN_CONTEXT_MEMORY_002 interacts with SPATIAL-I
   templates (particularly SC1 spatial integration). Ranganath's calibration
   must reference SPATIAL-I SC1 parameters and avoid double-counting the
   spatial navigation contribution to context-dependent encoding.

---

## Action

Set `pre_panel_review_cleared: true` in S-02 of SPRINT_TASK_BRIEF_for_Cowork.md.

Proceed with MEMORY-I panel execution using the revised 10-expert roster above.

---

*PRE_PANEL_REVIEW_CLEARANCE_MEMORY_I.md — CMR Project*
*Reviewed: February 22, 2026*
